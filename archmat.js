// BUILDING MATERIALS: how the architecture engine's surfaces are SHADED -- kept apart from architecture.js, which
// makes their GEOMETRY. The startup cache (pregen.js SECTIONS.buildings) is filed under the geometry code's hash: a
// change to a shader here (moss on the roofs, the crops' gusts, the snow) no longer retires every building's cached
// geometry, so a look can be tuned without every start then building the town from scratch.
//
//   glassMat                       every window's glass (its colour in the vertices)
//   archMaterial(side, pat)        a part's pattern material (colour and accent in the vertices: paintGeometry)
//   placedMaterial(mat)            its twin for geometry with the building's translation baked in (merge.js)
//   finishTile(r), finishTilesOf   a finish rule's pattern tile (patterns.js draws it, pregen/ may have it)
//   finishMaterial(r, side, open, geo)  a finish rule's material: the tile at the vertex's `aUV` (geo: given its slot)
//   woodMaterial(), plainStone()   grained wood (doors, shutters); a light-free stone for the viewers
import * as THREE from "three";
import { wgslFn, uniform, attribute, varying, texture, float, positionGeometry, positionWorld,
         normalWorld, modelWorldMatrix, cameraPosition, vec3, renderGroup } from "three/tsl";
import { TEXTURES, TILES, tileTexture, PARALLAX } from "./textures.js";
import { patternTile } from "./textures_wgsl.js";
import { FOLIAGE_T, SNOW, HARVEST } from "./foliage.js";   // the one wind clock: leaves and grain sway together
import { landShade, valueNoise, WET, PUDDLE, puddleShade } from "./cloudshadow.js";
import { renderPattern, patternOf, sizeOf as patternSize } from "./patterns.js";
import { PREGEN, pregenOn, pregenMiss, tileKey, recordFor } from "./pregen.js";
import { ruleParams } from "./arch/finish.js";
import { lightWGSL } from "./light.js";

// GLASS: one material for every window in the world. Its colour used to be baked into a material of its own
// (sixty of them, one mesh each -- exactly the mistake the building materials just stopped making); now it
// rides in the vertices like every other part's, so a building's glass merges into one mesh and the whole
// world shares one shader.
export const glassMat = new THREE.MeshBasicNodeMaterial({ transparent: true, opacity: .38, depthWrite: false, side: THREE.DoubleSide });
glassMat.colorNode = varying(attribute("aC", "vec3"), "vGlassC");

// deterministic orientation shading: a face's brightness comes purely from
// which way it points (all six directions distinct), so same-colored walls
// meeting at a corner -- or a floor against a wall -- always read as
// separate planes, outdoors and indoors alike, independent of any lights
const PAT_IDS = { ashlar: 1, brick: 2, grooves: 3, stars: 4, marble: 5, tiles: 6, scroll: 7, gothic: 8, checker: 9, ornament: 10, parquet: 11, wood: 12,
                  rye: 13, barley: 14, beans: 15, garlic: 16, berries: 17, fruit: 18, cherries: 19 };   // 13-16 are cut-outs (transparent between the plants), 17-19 dots

// Patterns live in the OBJECT's own frame -- its geometry's position and
// normal (for an instanced copy, scaled by the instance's own scale, so a
// unit box stretched into a shutter keeps metre-sized grain) -- and move
// with it: a barge, a cart or a swinging door carries its texture instead
// of sliding through a world-fixed one. Only the orientation shading and
// the snow read the world (a face's brightness says which way it points
// NOW). Buildings are placed by translation alone, so their merged,
// root-local geometry patterns exactly as in world space.
// The relief the parallax walks down into, at q (metres in the pattern's plane): a tile's baked alpha, or
// wood's grain worked out here -- q = (across the grain, along it), raised latewood with the soft wood between
// worn down. Generated per material because the wood case has no texture to sample.
const reliefFn = (id) => wgslFn(id === 12 ? `
  fn reliefAt(q: vec2<f32>, gx: vec2<f32>, gy: vec2<f32>, period: vec2<f32>) -> f32 {
    let g = sin(q.x * 42.0 + sin(q.y * 1.9 + q.x * 3.0) * 2.4 + sin(q.x * 8.5) * 1.1);
    return 1.0 - 0.75 * smoothstep(0.25, 0.95, g) - 0.15 * smoothstep(0.6, 1.0, sin(q.y * 23.0 + q.x * 15.0));
  }
` : `
  fn reliefAt(tex: texture_2d<f32>, samp: sampler, q: vec2<f32>, gx: vec2<f32>, gy: vec2<f32>, period: vec2<f32>) -> f32 {
    return textureSampleGrad(tex, samp, q / period, gx, gy).a;
  }
`);

// THE BUILDING FRAGMENT. The GLSL twin was one shader with a wall of #if PAT == n; WGSL has no preprocessor,
// so the same selection happens here in JavaScript and each material carries only the branch it needs.
// Returns (rgb, keep) -- keep < 0 is the crops' discard, the material's alphaTest cutting the pixel away.
// HOW A FACE IS LIT, and where snow lies: one source for every building material (archFrag, the finish material) --
// brightness from which way the face points, snow on what faces up well above the ground
const SHADE_K = lightWGSL("n");   // (light.js: the world's one sun, the same term every engine shades by)
// (snow settling, 0 .. 1: it lies in patches first -- where a slow noise is low -- and covers all of it at 1)
// (`low`: an open-air site's surfaces -- the market's paving, a yard's, the stalls' awnings -- snow at any height; a
//  building's only well above the ground, so its floors indoors stay bare)
const SNOW_ON = (c, low = "0.0") => `mix(${c}, vec3<f32>(0.93, 0.94, 0.97), smoothstep(-0.25, 0.25, snow * 1.4 - 0.3 - 0.5 * valueNoise2(pW.xz * 2.3) - 0.25 * valueNoise2(pW.xz * 7.1 + vec2<f32>(3.0, 1.0))) * smoothstep(0.06, 0.45, n.y) * max(${low}, smoothstep(3.2, 5.5, pW.y)))`;
const archFragSource = ({ id, baked, pom, steps, shadow }) => {
  const texParams = (baked || (pom && id !== 12)) ? "tex: texture_2d<f32>, samp: sampler, " : "";
  const reliefCall = (q) => id === 12 ? `reliefAt(${q}, gx, gy, period)` : `reliefAt(tex, samp, ${q}, gx, gy, period)`;
  const floorPat = id === 9 || id === 11;
  return `
  fn archFrag(nW: vec3<f32>, pW: vec3<f32>, pL: vec3<f32>, nL: vec3<f32>, Tw: vec3<f32>, Bw: vec3<f32>,
              camPos: vec3<f32>, ${texParams}C: vec3<f32>, C2: vec3<f32>, snow: f32, t: f32, harvest: f32,
              period: vec2<f32>, depth: f32, pomFar: f32, texelUV: f32) -> vec4<f32> {
    let n = normalize(nW);
    var col = C;
    var k = ${SHADE_K};
    let nl = normalize(nL);                                  // the face's normal in its own frame: picks the pattern plane
    let u = select(pL.x, pL.z, abs(nl.x) > abs(nl.z));       // coordinate along the face
${pom ? `
    // PARALLAX: walk the view ray down into the relief -- steps layers to depth metres, along the pattern's own
    // axes (a wall's face: along it and up; a floor's top: x and z; wood: across the grain and along it) --
    // refine between the last two layers; there the relief's slope tilts the normal (lit by the world's
    // orientation shading, 1.8x) and the shadow reads toward that light give the relief short shadows; the
    // colour is read where the ray met the relief. Near only: it fades out toward pomFar metres.
    // The ray is followed in WORLD space against the world-space pattern axes, which is the same walk the GLSL
    // made in the object's frame (the two frames differ by a rotation, and nothing here is scaled).
    let upP = step(0.5, abs(nl.y));
${id === 12 ? `
    var q0 = vec2<f32>(u, pL.y);
    if (upP > 0.5) { q0 = pL.zx; }
    let onPlane = 1.0;
    let gx = vec2<f32>(0.0);
    let gy = vec2<f32>(0.0);
    let eq = vec2<f32>(0.002);
` : `
    var q0 = vec2<f32>(u, pL.y);
    ${floorPat ? "q0 = pL.xz;" : ""}
    let onPlane = ${floorPat ? "abs(nl.y)" : "1.0 - abs(nl.y)"};
    // every read at the UNSHIFTED gradients, so the mip level never jumps as the ray walks
    let gx = dpdx(q0 / period);
    let gy = dpdy(q0 / period);
    let eq = texelUV * period;
`}
    let Vw = camPos - pW;
    let pdist = length(Vw);
    let fade = 1.0 - smoothstep(0.65 * pomFar, pomFar, pdist);
    var relief = 1.0;
    var qP = q0;
    let vd = Vw / max(pdist, 1e-4);
    let dn = dot(vd, n);
    if (fade > 0.01 && onPlane > 0.7 && dn > 0.06) {
      let dq = -vec2<f32>(dot(vd, Tw), dot(vd, Bw)) / dn * depth * fade / ${steps}.0;   // metres across the pattern per layer
      var layer = 1.0;
      var h = ${reliefCall("qP")};
      var hPrev = h;
      for (var i: i32 = 0; i < ${steps}; i = i + 1) {
        if (h >= layer) { break; }
        hPrev = h;
        layer = layer - 1.0 / ${steps}.0;
        qP = qP + dq;
        h = ${reliefCall("qP")};
      }
      let after = h - layer;
      let before = hPrev - (layer + 1.0 / ${steps}.0);
      qP = qP - dq * clamp(after / max(after - before, 1e-5), 0.0, 1.0);       // between the last two layers
      let h0 = ${reliefCall("qP")};
      relief = mix(1.0, h0, fade);
      let slope = vec2<f32>(${reliefCall("qP + vec2<f32>(eq.x, 0.0)")} - h0,
                            ${reliefCall("qP + vec2<f32>(0.0, eq.y)")} - h0) / eq * depth;   // metres of relief per metre
      let np = normalize(n - (Tw * slope.x + Bw * slope.y) * fade);
      k = k + 1.8 * dot(np - n, vec3<f32>(0.1, 0.2, 0.06));
${shadow > 0 ? `
      let Lw = normalize(vec3<f32>(0.1, 0.2, 0.06));
      let lt = vec3<f32>(dot(Lw, Tw), dot(Lw, Bw), dot(Lw, n));
      if (lt.z > 0.05 && h0 < 0.98) {
        var occ = 0.0;
        for (var i: i32 = 1; i <= ${shadow}; i = i + 1) {
          let up = (1.0 - h0) * f32(i) / ${shadow}.0;
          occ = max(occ, ${reliefCall("qP + lt.xy / lt.z * depth * up")} - (h0 + up));
        }
        k = k * (1.0 - 0.45 * smoothstep(0.0, 0.12, occ) * fade);
      }` : ""}
    }
` : ""}
${id >= 1 && id <= 11 ? `
    // flat repeating patterns: (brightness k, accent share, dark-figure share) at this point of the pattern's
    // plane -- floors (checker, parquet) in x/z
    let q = ${floorPat ? "pL.xz" : "vec2<f32>(u, pL.y)"};
${baked ? `
    let T = ${pom ? "textureSampleGrad(tex, samp, qP / period, gx, gy)" : "textureSample(tex, samp, q / period)"}.rgb;
    var kab = vec3<f32>(T.r * 1.5, T.g, T.b);
${pom ? "    kab.x = kab.x * (1.0 - 0.2 * (1.0 - relief));   // the deep parts (mortar, channels) a shade darker still" : ""}
` : `
    let kab = patternTile(${id}.0, q, 0.0);
`}
    k = k * kab.x;
    col = mix(col, C2, kab.y);
    col = mix(col, vec3<f32>(0.05, 0.045, 0.04), kab.z);
${id === 5 ? "    k = k * (1.0 - 0.035 * (0.5 + 0.5 * sin(pL.x * 0.8 + pL.y * 2.3 + pL.z * 1.1)));   // marble veining: smooth, stays per pixel" : ""}
` : ""}
${id === 12 ? `
    // wood grain, slight: streaks along the board -- lengthwise on horizontal faces, vertical on upright ones,
    // wandering a little
    let upF = step(0.5, abs(nl.y));
    var along = mix(pL.y, pL.x, upF);
    var across = mix(u, pL.z, upF);
${pom ? `    along = qP.y; across = qP.x;      // the grain where the ray met it
    k = k * (1.0 - 0.2 * (1.0 - relief));` : ""}
    let g = sin(across * 42.0 + sin(along * 1.9 + across * 3.0) * 2.4 + sin(across * 8.5) * 1.1);
    k = k * (1.0 - 0.075 * smoothstep(0.25, 0.95, g) - 0.03 * smoothstep(0.6, 1.0, sin(along * 23.0 + across * 15.0)));
` : ""}
${id >= 13 && id <= 16 ? `
    // crops as cut-outs: a thin see-through slab carries a row of plants -- rye/barley stalks with ears, bean
    // poles with leaves, garlic leaf-fans -- and is discarded between them, so a field of thousands of plants
    // costs a few dozen boxes. Heights count from the soil top (the site stands 1cm up: .12 local is .13 world).
    let hgt = pL.y - 0.12;
${id === 13 || id === 14 ? `
    let H = ${id === 13 ? "1.15" : "0.85"};
    let cw = 0.07;
    let earL = ${id === 13 ? "0.16" : "0.12"};
    let earW = ${id === 13 ? "0.026" : "0.034"};
    if (harvest > 0.5) {
      // HARVESTED: stubble a hand high, and the sheaves stood up in STOOKS every 3 m across the field -- a cone each, drawn
      // where the crossing rows meet, so two silhouettes cross in it and it reads round from every side
      if (hgt < 0.0 || hgt > 0.95) { return vec4<f32>(0.0, 0.0, 0.0, -1.0); }
      let sd = (vec2<f32>(fract(pW.x / 3.0), fract(pW.z / 3.0)) - vec2<f32>(0.5)) * 3.0;
      if (length(sd) < (0.95 - hgt) * 0.36) {
        col = C2;
        k = k * (0.78 + 0.3 * fract(sin(dot(floor(pW.xz * 30.0) + vec2<f32>(floor(hgt * 25.0), 0.0), vec2<f32>(12.9, 78.2))) * 43758.5));
      } else if (hgt < 0.09 && fract(u / 0.06) < 0.35) {
        col = mix(C, C2, 0.5); k = k * 0.8;
      } else { return vec4<f32>(0.0, 0.0, 0.0, -1.0); }
    } else {
    // wind: the row bends as one -- the coordinate along the slab shifts by a smooth gust field that grows
    // toward the ears, so neighbouring stalks move together and waves run over the field
    // ...and GUSTS: broad bands running across the field down the wind (the grass's way, .31/.95), bending it further
    // and turning the ears pale as they bow -- the silver waves that run over ripe grain
    let gust = smoothstep(0.35, 1.0, 0.5 + 0.5 * sin(t * 0.9 - (pW.x * 0.31 + pW.z * 0.95) * 0.42) + 0.2 * sin(t * 0.37 + pW.x * 0.13 - pW.z * 0.07));
    let sw = pow(clamp(hgt / H, 0.0, 1.0), 1.5) * (0.06 * sin(t * 1.3 + u * 0.35 + pL.z * 0.2) + 0.022 * sin(t * 2.9 + u * 1.1) + 0.07 * gust);
    let uu = u - sw;
    let id2 = floor(uu / cw);
    let fu = fract(uu / cw) - 0.5;
    let hs = fract(sin(id2 * 127.1) * 43758.5);
    let top = H * (0.78 + 0.27 * hs);
    let dx = abs(fu * cw - (hs - 0.5) * 0.1 * hgt / H);      // a slight lean, each its own way
    if (hgt > top || hgt < 0.0) { return vec4<f32>(0.0, 0.0, 0.0, -1.0); }
    if (hgt > top - earL) {
      if (dx > earW) { return vec4<f32>(0.0, 0.0, 0.0, -1.0); }
      col = C2;
      k = k * (0.9 + 0.2 * hs) * (1.0 + 0.34 * gust);
    } else {
      if (dx > 0.011) { return vec4<f32>(0.0, 0.0, 0.0, -1.0); }
      k = k * (0.85 + 0.3 * hs) * (1.0 + 0.2 * gust * hgt / H);
    }
    }
` : id === 15 ? `
    let cw = 0.5;
    let id2 = floor(u / cw);
    let fu = fract(u / cw) - 0.5;
    let hs = fract(sin(id2 * 91.7) * 43758.5);
    let top = 1.7 * (0.85 + 0.2 * hs);
    if (hgt > top || hgt < 0.0) { return vec4<f32>(0.0, 0.0, 0.0, -1.0); }
    let dx = fu * cw;
    let row = floor(hgt / 0.17);
    let fr = fract(hgt / 0.17) - 0.5;
    let sd = ((row + floor(hs * 2.0)) - 2.0 * floor((row + floor(hs * 2.0)) / 2.0)) * 2.0 - 1.0;   // leaves alternate sides up the pole
    let lj = fract(sin(id2 * 31.3 + row * 17.1) * 43758.5);
    let lc = vec2<f32>(dx - sd * (0.07 + 0.05 * lj), fr * 0.17);
    let leaf = step(length(lc * vec2<f32>(1.0, 1.6)), 0.085);
    let pole = step(abs(dx), 0.014);
    if (leaf < 0.5 && pole < 0.5) { return vec4<f32>(0.0, 0.0, 0.0, -1.0); }
    col = select(C, C2, leaf > 0.5);
    k = k * (0.85 + 0.3 * lj);
` : `
    let cw = 0.3;
    let id2 = floor(u / cw);
    let fu = fract(u / cw) - 0.5;
    let hs = fract(sin(id2 * 57.3) * 43758.5);
    let top = 0.45 * (0.8 + 0.35 * hs);
    if (hgt > top || hgt < 0.0) { return vec4<f32>(0.0, 0.0, 0.0, -1.0); }
    let dx = fu * cw;
    var keep = 0.0;
    for (var i: i32 = -1; i <= 1; i = i + 1) {        // three leaves fanning out from the bulb
      let lx = f32(i) * (0.05 + 0.04 * hs) * hgt / 0.45 + (hs - 0.5) * 0.04;
      keep = max(keep, step(abs(dx - lx), 0.012 * (1.0 - 0.5 * hgt / top)));
    }
    if (keep < 0.5) { return vec4<f32>(0.0, 0.0, 0.0, -1.0); }
    k = k * (0.85 + 0.3 * hs);
`}` : ""}
${id >= 17 && id <= 19 ? `
    // currants (17, ~1cm), apples (18, ~8cm) and cherries (19, ~2.5cm): sharp dots of the accent colour
    // scattered over a crown
    let c = ${id === 17 ? "0.065" : id === 18 ? "0.25" : "0.08"};
    let rr = ${id === 17 ? "0.005" : id === 18 ? "0.04" : "0.0125"};
    let cell = floor(pL / c);
    let f = fract(pL / c);
    let jit = fract(sin(vec3<f32>(dot(cell, vec3<f32>(127.1, 311.7, 74.7)),
                                  dot(cell, vec3<f32>(269.5, 183.3, 246.1)),
                                  dot(cell, vec3<f32>(113.5, 271.9, 124.6)))) * 43758.5) * 0.5 + 0.25;
    let show = step(fract(sin(dot(cell, vec3<f32>(12.9, 78.2, 37.7))) * 4375.5), ${id === 17 ? "0.9" : id === 18 ? "0.75" : "0.85"});   // a heavy crop
    col = mix(col, C2, step(length((f - jit) * c), rr) * show);
` : ""}
    var shaded = col * k;
    // snow settles on upward-facing surfaces well above the ground (roofs, cornices, the stands) -- walls and
    // columns stay bare; the ramp starts near 0 so even steep spires collect snow
    shaded = ${SNOW_ON("shaded")};
    return vec4<f32>(shaded, 1.0);
  }
`;
};

// the pattern's two axes in the world (along the face, up -- a floor's x, z), for the parallax to step along
const patAxes = wgslFn(`
  fn patAxes(nl0: vec3<f32>, model: mat4x4<f32>, which: f32, flat3: f32, wood: f32) -> vec3<f32> {
    let m3 = mat3x3<f32>(model[0].xyz, model[1].xyz, model[2].xyz);
    let woodTop = wood > 0.5 && abs(nl0.y) > 0.5;          // (wood on a level face: across z, along x)
    var v = vec3<f32>(1.0, 0.0, 0.0);
    if (which < 0.5) {                                     // T: along the face
      if (flat3 > 0.5) { v = vec3<f32>(1.0, 0.0, 0.0); }
      else if (woodTop || abs(nl0.x) > abs(nl0.z)) { v = vec3<f32>(0.0, 0.0, 1.0); }
    } else {                                               // B: up the face
      if (flat3 > 0.5) { v = vec3<f32>(0.0, 0.0, 1.0); }
      else if (woodTop) { v = vec3<f32>(1.0, 0.0, 0.0); }
      else { v = vec3<f32>(0.0, 1.0, 0.0); }
    }
    return normalize(m3 * v);
  }
`);

const cutOf = wgslFn(`fn cutOf(v: f32) -> f32 { if (v < 0.0) { return 0.0; } return 1.0; }`);

// THE COLOUR RIDES IN THE VERTICES, NOT IN THE MATERIAL.
// Every part of a building used to ask for a material of its own colour, and since buildBuilding merges parts
// by MATERIAL, a house with thirty-nine colours ended up as thirty-nine meshes -- thirty-nine objects for
// three to walk, five times a frame, and thirty-nine draws when it is in view. The shader is the same for all
// of them: what differs is two vec3 uniforms. So the colour and the accent are written per vertex instead
// (paintGeometry, below) and a material is keyed by what actually changes the SHADER -- its pattern and which
// side it shows. A farmhouse then merges into a handful of meshes, and the picture is identical: the value
// that reached the shader as a uniform now reaches it as an attribute, unchanged.
const archCache = new Map();
export function archMaterial(side, pat, placed = false) {
  // pat: mathematically-defined surface patterns in the object's space --
  //  ashlar: large stone courses, staggered joints   brick: tight running bond
  //  marble: hairline joints + soft veining (Greek precision masonry)
  //  grooves: vertical channels in an accent color (triglyphs)
  //  stars: a dot grid in an accent color (painted tympana, rosette bands)
  //  (1-11 are flat repeating patterns: read from a baked, mipmapped tile --
  //  textures.js -- or, with TEXTURES.on false, evaluated per pixel from the same maths)
  // `placed`: the twin for geometry that has had its building's translation BAKED IN (merge.js mergeAcross joins
  // whole streets into one mesh). The pattern must still be read in the building's own frame, so the vertices
  // carry their original local position in `aLocal` and the pattern reads that -- bit for bit what it read before.
  const key = `${side ?? ""}|${pat ?? ""}${placed ? "|placed" : ""}`;
  if (archCache.has(key)) return archCache.get(key);
  const id = PAT_IDS[pat] ?? 0, tile = TEXTURES.on && id >= 1 && id <= 11 ? TILES[pat] : null;
  const pom = PARALLAX.on && ((tile && tile.depth > 0) || id === 12);   // parallax: a tile's baked relief, or wood's grain
  const baked = !!tile;
  const texNode = tile ? texture(tileTexture(pat)) : null;

  const rawPos = placed ? attribute("aLocal", "vec3") : positionGeometry, rawNormal = attribute("normal", "vec3");
  const flat3 = id === 9 || id === 11 ? 1 : 0, wood = id === 12 ? 1 : 0;
  const args = {
    nW: normalWorld, pW: positionWorld, pL: rawPos, nL: rawNormal,
    Tw: varying(patAxes({ nl0: rawNormal.normalize(), model: modelWorldMatrix, which: float(0), flat3: float(flat3), wood: float(wood) }), "vTw"),
    Bw: varying(patAxes({ nl0: rawNormal.normalize(), model: modelWorldMatrix, which: float(1), flat3: float(flat3), wood: float(wood) }), "vBw"),
    camPos: cameraPosition,
    C: varying(attribute("aC", "vec3"), "vArchC"), C2: varying(attribute("aC2", "vec3"), "vArchC2"),
    snow: uniform(0).setGroup(renderGroup).onRenderUpdate(() => SNOW.value),
    t: uniform(0).setGroup(renderGroup).onRenderUpdate(() => FOLIAGE_T.value),      // the one wind clock (foliage.js): the crops sway with the leaves
    harvest: uniform(0).setGroup(renderGroup).onRenderUpdate(() => HARVEST.value),  // (late autumn: the grain cut, stooks in the fields)
    period: uniform(new THREE.Vector2(...(tile ? tile.period : [1, 1]))),
    depth: uniform(id === 12 ? .004 : tile?.depth ?? 0),
    pomFar: uniform(PARALLAX.far), texelUV: uniform(tile ? 1 / tile.size : 0),
  };
  if (texNode) { args.tex = texNode; args.samp = texNode; }

  const includes = [valueNoise];   // (SNOW_ON's patches)
  if (pom) includes.push(reliefFn(id));
  if (id >= 1 && id <= 11 && !baked) includes.push(patternTile);
  const frag = wgslFn(archFragSource({ id, baked, pom, steps: PARALLAX.steps, shadow: PARALLAX.shadowSteps }), includes)(args);

  const mat = new THREE.MeshBasicNodeMaterial({ side: side === "double" ? THREE.DoubleSide : THREE.FrontSide });
  mat.colorNode = frag.xyz.mul(landShade());   // (the clouds' shadows passing over, as on the ground: cloudshadow.js)
  if (id >= 13 && id <= 16) {          // the crops are cut-outs: a node material discards through alphaTest
    mat.opacityNode = cutOf({ v: frag.w });
    mat.alphaTest = .5;
  }
  mat.userData.archArgs = { side, pat };
  mat.userData.arch = { side, pat, placed };
  archCache.set(key, mat);
  return mat;
}
// the `placed` twin of a building material (null for any other material: nothing else reads the local frame)
export const placedMaterial = (mat) => mat?.userData?.arch ? (mat.userData.arch.placed ? mat : archMaterial(mat.userData.arch.side, mat.userData.arch.pat, true)) : null;

// a rule's tile: the pattern drawn once (patterns.js renderPattern) into a mipmapped, anisotropic texture -- shared by
// every rule and every building that asks for the same pattern in the same colours
const finishTiles = new Map();
const finishKey = (r) => `${r.pattern}|${JSON.stringify(r.palette ?? null)}|${JSON.stringify(ruleParams(r))}|${r.res ?? ""}`;
export function finishTile(r) {
  const key = finishKey(r);
  let t = finishTiles.get(key);
  // (pregenerated, if pregen/ has it: the same tile, drawn once by build/pregen.py -- else drawn here, as always)
  const pk = pregenOn() ? tileKey(r.pattern, r.palette, ruleParams(r), r.res) : null;
  if (pk && t) recordFor("tiles", pk, t.canvas);   // (the generator notes which buildings use a tile made for another)
  if (!t) {
    const cached = pk && PREGEN.tiles.get(pk), def = patternOf(r.pattern);
    const tile = cached ? { canvas: cached, size: patternSize(def, ruleParams(r)), repeat: def.repeat !== false }
                        : renderPattern(r.pattern, { palette: r.palette, params: ruleParams(r), res: r.res });
    if (pk) recordFor("tiles", pk, tile.canvas);
    if (pk && !cached) pregenMiss("tile", r.pattern, pk);
    finishTiles.set(key, t = { size: tile.size, canvas: tile.canvas, repeat: tile.repeat });
  }
  return t;
}
// (the tile as a texture of its own: ?tilearray=0 only)
function tileTex(t) {
  if (t.tex) return t.tex;
  const tex = t.tex = new THREE.CanvasTexture(t.canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = tex.wrapT = t.repeat ? THREE.RepeatWrapping : THREE.ClampToEdgeWrapping;
  tex.minFilter = THREE.LinearMipmapLinearFilter; tex.anisotropy = 8; tex.generateMipmaps = true;
  return tex;
}

// THE TILE ARRAY. Every finish tile is one layer of ONE texture (TILE_RES square, mipmapped and repeating layer by layer,
// as fabric.js keeps the cloths), and each finish -- which tile, how many metres it spans at its scale -- one texel of
// a little table, its SLOT. A finished surface carries its slot per vertex (`aSlot`), so every pattern in the world
// shares a few materials (front or both sides x weathered or dry x open air) and the world's merge joins a building's
// walls, roofs, timbers and furniture into one draw, not one per pattern: in the market's view 81 finish materials
// were 131 of the frame's 255 draws, and three pays every draw on the CPU. A tile's own proportions are stretched to
// the square layer and back by its slot (the table says its metres); its canvas is let go once it is in the array.
// ?tilearray=0: a texture and a material per finish, as before.
export const TILE_ARRAY = typeof location === "undefined" || new URLSearchParams(location.search).get("tilearray") !== "0";
const TILE_RES = 512;
const TA = { n: 0, cap: 0, data: null, node: null, slots: new Map(), info: null, infoData: null, infoNode: null, scratch: null };
function tileArray(cap) {   // (grown: a new texture, the same node -- a material built once keeps working)
  const old = TA.data;
  TA.cap = cap; TA.data = new Uint8Array(TILE_RES * TILE_RES * 4 * cap);
  if (old) TA.data.set(old);
  const t = new THREE.DataArrayTexture(TA.data, TILE_RES, TILE_RES, cap);
  t.format = THREE.RGBAFormat; t.type = THREE.UnsignedByteType; t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.magFilter = THREE.LinearFilter; t.minFilter = THREE.LinearMipmapLinearFilter; t.generateMipmaps = true; t.anisotropy = 8;
  t.needsUpdate = true;
  TA.up = false; t.onUpdate = () => { TA.up = true; };   // (until its first upload the whole array goes up, layers and all)
  if (TA.node) { TA.node.value.dispose(); TA.node.value = t; } else TA.node = texture(t);
}
function tileLayer(t) {   // the tile's layer, drawn into the array the first time a finish asks for it
  if (t.layer !== undefined) return t.layer;
  if (TA.n === TA.cap) tileArray(TA.cap ? TA.cap + 16 : 64);   // (16 layers more at a time: a spare layer is a megabyte and a third)
  const R = TILE_RES, cv = TA.scratch ??= new OffscreenCanvas(R, R), cx = cv.getContext("2d", { willReadFrequently: true });
  cx.clearRect(0, 0, R, R); cx.drawImage(t.canvas, 0, 0, R, R);
  const px = cx.getImageData(0, 0, R, R).data, row = R * 4, L = t.layer = TA.n++, base = L * R * row;
  for (let y = 0; y < R; y++) TA.data.set(px.subarray(y * row, (y + 1) * row), base + (R - 1 - y) * row);   // (bottom row first: as a canvas texture reads)
  const tex = TA.node.value;
  if (TA.up) tex.addLayerUpdate(L);   // (once it is up, only the new layer goes up)
  tex.needsUpdate = true;
  if (!PREGEN.record) t.canvas = null;   // (in the array now; the generator still writes the tiles out)
  return L;
}
function finishSlot(r) {
  const k = r.scale ?? 1, key = finishKey(r) + "|" + k;
  let s = TA.slots.get(key);
  if (s !== undefined) return s;
  s = TA.slots.size;
  if (!TA.info || s * 4 >= TA.infoData.length) {   // (the table, grown by doubling)
    const old = TA.infoData, n = Math.max(256, (old?.length ?? 0) / 2);
    TA.infoData = new Float32Array(n * 4); if (old) TA.infoData.set(old);
    const it = new THREE.DataTexture(TA.infoData, n, 1, THREE.RGBAFormat, THREE.FloatType);
    it.needsUpdate = true;
    if (TA.infoNode) { TA.infoNode.value.dispose(); TA.infoNode.value = it; } else TA.infoNode = texture(it);
    TA.info = it;
  }
  const t = finishTile(r);
  TA.infoData.set([tileLayer(t), 1 / (t.size[0] * k), 1 / (t.size[1] * k), 0], s * 4);
  TA.info.needsUpdate = true;
  TA.slots.set(key, s);
  return s;
}
const finishTexel = wgslFn(`
  fn finishTexel(tiles: texture_2d_array<f32>, samp: sampler, info: texture_2d<f32>, slot: f32, uv: vec2<f32>) -> vec3<f32> {
    let f = textureLoad(info, vec2<i32>(i32(slot + 0.5), 0), 0);
    return textureSample(tiles, samp, uv * f.yz + vec2<f32>(0.5), i32(f.x + 0.5)).rgb;
  }
`);

export const finishTileList = () => [...finishTiles.values()];   // (every tile drawn so far)
// every tile a finish draws with, drawn now (build/pregen.py: a town's style bakes its whole range this way)
export function finishTilesOf(finish) { for (const r of finish.rules) if (r.pattern) finishTile(r); }

// THE FINISH MATERIAL: the tile read at the vertex's own pattern coordinates (`aUV`, metres; the tile is `period`
// metres), lit and snowed on exactly as every other building material is (SHADE_K, SNOW_ON)
// MOSS on the roofs: in small patches on any sloped face that looks up (a roof: never a ceiling, never a floor), more
// on the north side where the sun is short -- a dull green over the tiles, the thatch or the slates; only on the older
// roofs (a slow noise over the town: one quarter mossy, another clean)
const finishShade = wgslFn(`
  fn finishShade(c: vec3<f32>, nW: vec3<f32>, pW: vec3<f32>, snow: f32, wet: f32, low: f32, pud: f32, sky: vec3<f32>, t: f32, rain: f32, cam: vec3<f32>) -> vec3<f32> {
    let n = normalize(nW);
    let k = ${SHADE_K};
    var cm = c;
    if (n.y > 0.25 && n.y < 0.95) {
      let m = valueNoise2(pW.xz * 2.2) * 0.55 + valueNoise2(pW.xz * 7.0 + vec2<f32>(5.0, 2.0)) * 0.45 + 0.14 * n.z;
      let old = smoothstep(0.45, 0.75, valueNoise2(pW.xz * 0.04 + vec2<f32>(3.0, 7.0)));   // (some roofs old and mossy, some clean)
      cm = mix(c, mix(c, vec3<f32>(0.32, 0.4, 0.18), 0.65), smoothstep(0.68, 0.82, m) * 0.38 * old);
    }
    // WET after rain (an outside face only: the material says): darker, the roofs most -- they take the rain full on
    cm = cm * (1.0 - wet * mix(0.1, 0.3, smoothstep(0.2, 0.7, n.y)));
    // ...and PUDDLES on its level faces where the rule says (a square's paving: cloudshadow.js)
    if (pud > 0.5 && n.y > 0.97) { cm = puddleShade(cm, pW, 0.0, 1.0, wet, sky, t, rain, cam); }
    return ${SNOW_ON("cm * k", "low")};
  }
`, [valueNoise, puddleShade]);
const finishMats = new Map();
// a finish rule's material, for the geometry `geo` (its `aUV`, metres) -- which, with the tile array, is given its slot
export function finishMaterial(r, side, open = false, geo = null) {   // open: an open-air site's (snow at any height)
  const pud = !!r.puddles;   // (a rule's `puddles`: open ground under the sky -- a square's paving -- rained on, puddles in its hollows)
  const outside = pud || (r.side !== "in" && r.surface !== "ceiling" && r.surface !== "floor");   // (rained on: not a room's inside, a ceiling or a floor)
  if (TILE_ARRAY) {
    if (!geo) throw new Error("finishMaterial: the geometry is needed (its slot)");
    const slot = finishSlot(r);
    geo.setAttribute("aSlot", new THREE.BufferAttribute(new Float32Array(geo.attributes.position.count).fill(slot), 1));
  }
  const key = TILE_ARRAY ? `array|${side ?? ""}${outside ? "" : "|dry"}${open ? "|open" : ""}${pud ? "|pud" : ""}`
                         : finishKey(r) + "|" + (r.scale ?? 1) + "|" + (side ?? "") + (outside ? "" : "|dry") + (open ? "|open" : "") + (pud ? "|pud" : "");
  let mat = finishMats.get(key);
  if (!mat) {
    let c;
    if (TILE_ARRAY) c = finishTexel({ tiles: TA.node, samp: TA.node, info: TA.infoNode, slot: attribute("aSlot", "float"), uv: attribute("aUV", "vec2") });
    else {
      const t = finishTile(r), k = r.scale ?? 1;
      c = texture(tileTex(t), attribute("aUV", "vec2").div(uniform(new THREE.Vector2(t.size[0] * k, t.size[1] * k))).add(.5)).rgb;
    }
    mat = new THREE.MeshBasicNodeMaterial({ side: side === "double" ? THREE.DoubleSide : THREE.FrontSide });
    mat.colorNode = finishShade({ c, nW: normalWorld, pW: positionWorld, snow: uniform(0).setGroup(renderGroup).onRenderUpdate(() => SNOW.value),
                                  wet: uniform(0).setGroup(renderGroup).onRenderUpdate(() => outside ? WET.value : 0), low: float(open ? 1 : 0),
                                  pud: float(pud ? 1 : 0), sky: PUDDLE.sky, t: PUDDLE.t, rain: PUDDLE.rain, cam: cameraPosition }).mul(landShade());
    mat.userData.finish = key;
    finishMats.set(key, mat);
  }
  return mat;
}

// wood with grain: door panels and shutters the demo hinges (patterns ride with the object anyway)
// wood with grain: the material is shared, the colour comes from the geometry (paintGeometry)
export const woodMaterial = () => archMaterial(undefined, "wood");

// A PLAIN STONE, for looking at a definition on its own: the world's own light-free shading (how bright a
// face is says which way it points) with no pattern and nothing baked behind it. FLAT SHADING WITHOUT VERTEX
// NORMALS -- architecture wants every face flat and every corner sharp, and the engine wants its vertices
// WELDED, which pull against each other -- so the normal is taken per pixel from the derivatives of the world
// position. The face is then exactly as flat as it is. (arch_lab.html and assets.html draw with it.)
let plainCache = null;
export function plainStone(base = [.80, .76, .66]) {
  const fn = plainCache ?? (plainCache = wgslFn(`
    fn plainStone(pw: vec3<f32>, eye: vec3<f32>, base: vec3<f32>) -> vec3<f32> {
      var n = normalize(cross(dpdx(pw), dpdy(pw)));
      if (dot(n, eye - pw) < 0.0) { n = -n; }
      let k = ${lightWGSL("n")};
      return base * k;
    }
  `));
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 });
  mat.colorNode = fn({ pw: positionWorld, eye: cameraPosition, base: vec3(...base) }).mul(landShade());
  return mat;
}
