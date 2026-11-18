// THE PLANT FIELD (2026-11-18): every tree and bush in the world, drawn from a few grown VARIANTS per kind, each
// at three LEVELS OF DETAIL, instanced -- a forest of a thousand trees in a few dozen draws.
//
//   field = createPlantField(scene)
//   const h = field.add("oak", x, y, z, { yaw, scale, seed })   // -> { kind, variant, sk, info }: info is the tree as
//                                                                //    the game knows it (plantInfo: trunk, boughs, crown)
//   field.build()                                                // after the adds (again after more adds)
//   field.update(camera)                                         // every frame: which trees at which LOD, culled
//   field.clear()
//
// A KIND is a species in species.js (TREES), or "bush" / "bush:<fruit>" (SHRUB, bare or bearing one of BUSH_FRUITS:
// one kind, the fruit an instance's own -- its berries painted in a marker colour and recoloured in the shader). Each
// kind grows VARIANTS skeletons (grow.js), meshes each at LOD 0/1/2 (mesh.js) and bakes its bark and its spray atlas
// once (bake.js). An instance is a variant placed: position, yaw, scale, a tint and a phase of its own -- so no two
// trees in a wood look or sway alike, though they share a few shapes.
//
// THE LEVELS (by distance, scaled by the tree's height; switched with a dithered cross-fade, never a pop):
//   0  all the wood, every twig spray as a see-through card (alpha-to-coverage edges) -- TRI_BUDGET (5000) a tree:
//      the wood gets what the leaves leave of it (mesh.js woodMesh coarsens until it fits)
//   1  the same tree, its details left out: trunk and limbs, the twigs gone, ~30% of the same cards in their own
//      places, bigger, painted with the filled spray (bake.js column 4: nearly solid) -- mesh.js FAR_CARDS; their
//      vertices pulled from a buffer (pullBuffer)
//   2  trunk and big limbs on a few sides, ~16% of the cards, bigger still
//   (until 2026-11-18 the far crowns were camera-facing clumps painted from the skeleton: cheaper in pixels, but a
//    different tree at every switch)
// THE DRAWS: the wood and the leaves apart (two shaders: one for both cost the GPU half again -- see THE COLOUR); at
// level 0 a draw per variant, at 1 and 2 ONE draw for all of a kind's variants, their meshes end to end, each
// vertex knowing its variant (aWind.z) and each instance its own (its phase: PHASE_SPAN), the rest sent out of view
// -- the far levels' few hundred triangles cost less than the draws they save.
//
// THE SHADERS (WGSL, the world's one sun: light.js; the clouds' shadows: cloudshadow.js; snow: foliage.js SNOW):
//   wood   bark albedo and normal map in the branch's own frame (the tangent runs along it), the crown's shade
//          (baked per vertex: aTone.x), the trunk's foot darker; snow on what faces up
//   leaves the card's own colour from the atlas; lit by a normal mixed of the CROWN's (out from its middle, so the
//          crown reads as one rounded mass) and the card's own; the sun through a leaf when it is behind it; the
//          crown's inner shade; autumn turns a share of the cards (each by its own random) to the species' autumn
//          colour, keeping the painted leaf's light and dark; bare (winter) drops them; spring's blossom (or a
//          species' flowers in their season) shows the atlas's flower cell on a share of the sprays, the summer's
//          fruit its fruit cell on another (each card by its own random: a tree can be in both)
//   wind   every vertex moves by its bend weight (mesh.js aWind: none at the foot, most at the limbs' ends) on its
//          limb's phase plus its tree's, with the world's wind (grass.js WIND, WIND_DIR) and its gusts
// Everything a leaf's shape cuts is a cut-out in the shader, so the meshes take the grass mask's cut path
// (userData.cut, NOGRASS_LAYER, black in MASK_MODE).
import * as THREE from "three";
import { wgslFn, uniform, texture, attribute, varying, float, vec2, vec3, vec4, uv, screenCoordinate,
         cameraPosition, renderGroup, normalize, storage, vertexIndex, uint } from "three/tsl";
import { MASK_MODE, NOGRASS_LAYER, WIND, WIND_DIR } from "../grass.js";
import { LIGHT, lightWGSL } from "../light.js";
import { cloudShade, CLOUD } from "../cloudshadow.js";
import { SNOW, FOLIAGE_T } from "../foliage.js";
import { TREES, SHRUB, BUSH_FRUITS } from "./species.js";
import { growPlant } from "./grow.js";
import { woodMesh, leafMesh, bodyMesh, crownShape, rootCards } from "./mesh.js";
import { bakeBark, bakeSprays, SPRAY_ASPECT, FRUIT_MARKER } from "./bake.js";

// THE SEASON, for every plant at once (index.html sets it): autumn 0..1 (the leaves turning), bare 0..1 (fallen),
// bloom 0..1 (spring blossom on the orchard trees), fruit 0..1 (summer into autumn); flowers: the ceiba's season
export const SEASON = { autumn: uniform(0), bare: uniform(0), bloom: uniform(0), fruit: uniform(0), flowers: uniform(1) };
// the distances the levels change at, for a tree 15 m high (a taller one later, a bush sooner), and the fade's width
export const PLANT_LOD = { near: 34, mid: 120, fade: .12, variants: 3, bushVariants: 3, force: -1 };

const D = (v) => v.toFixed(5);
const TRI_BUDGET = 5000;   // (a tree's triangles at its nearest, wood and leaves)
const PHASE_SPAN = 8;   // (an instance's phase, 0..2pi, plus PHASE_SPAN times its variant)
const SUN = `vec3<f32>(${LIGHT.dir.map(D).join(", ")})`;

// ---- the vertex: the variant's point, turned and scaled and swayed, into the world. The far levels draw a kind's
// variants as one mesh (wind.z the variant a vertex is of, the instance's in its phase i1.z: PHASE_SPAN a variant):
// the other variants' points are sent far below the world, out of every view
const plantPoint = wgslFn(`
  fn plantPoint(p: vec3<f32>, i0: vec4<f32>, i1: vec4<f32>, wind: vec3<f32>, t: f32, gust: f32, wdir: vec2<f32>) -> vec3<f32> {
    if (abs(floor(i1.z / ${PHASE_SPAN}.0) - wind.z) > 0.5) { return vec3<f32>(0.0, -1e6, 0.0); }
    let c = cos(i0.w);
    let s = sin(i0.w);
    var q = vec3<f32>(p.x * c + p.z * s, p.y, -p.x * s + p.z * c) * i1.x;
    let ph = wind.y + i1.z;
    let k = wind.x * i1.x * (0.16 + 0.38 * gust);   // (eased 2026-11-18: the branches swung too wildly)
    let along = k * (0.55 * sin(t * 0.9 + ph) + 0.3 * sin(t * 2.1 + ph * 1.7) + 0.6 * gust);
    let across = k * 0.45 * sin(t * 1.3 + ph * 2.3);
    q = q + vec3<f32>(wdir.x * along - wdir.y * across, -abs(along) * 0.08, wdir.y * along + wdir.x * across);
    return q + i0.xyz;
  }
`);
// a near leaf card's corner (mesh.js leafMesh: its vertices on its midline; tone.w its width in cm plus its grown
// facing -- the angle of its side round its axis, over pi, in the frame mesh.js cardFrame builds): spread from its
// (swayed) midline to its side, turned round its own axis toward the eye -- the old leaf banners faced the camera, and
// a spray seen edge-on is a streak -- but by at most CARD_TURN from as it grew, so close by it never swings round; and
// its tip fluttering on its own, more in a gust (its base stays on its branch). A frond (w 0) as grown
const CARD_TURN = .6;   // (radians, ~35 degrees)
const cardCorner = wgslFn(`
  fn cardCorner(c: vec3<f32>, ax: vec3<f32>, uv: vec2<f32>, pack: f32, scale: f32, rnd: f32, eye: vec3<f32>, t: f32, gust: f32) -> vec3<f32> {
    if (pack <= 0.0 || c.y < -1e5) { return c; }   // (a frond; or another variant's, sent out of view: plantPoint)
    let w = floor(pack) * 0.01 * scale;
    let th = fract(pack) * 3.14159265;
    var fr1 = cross(ax, vec3<f32>(0.0, 1.0, 0.0));
    if (length(fr1) < 1e-4) { fr1 = cross(ax, vec3<f32>(1.0, 0.0, 0.0)); }
    fr1 = normalize(fr1);
    let fr2 = cross(ax, fr1);
    // the side that would face the eye, as an angle in that frame; the turn to it the short way (a side is a side
    // either way round: modulo pi), held to CARD_TURN
    let want = cross(ax, eye - c);
    var a = th;
    if (length(want) > 1e-5) {
      let d = atan2(dot(want, fr2), dot(want, fr1)) - th;
      a = th + clamp(d - 3.14159265 * round(d / 3.14159265), -${CARD_TURN.toFixed(3)}, ${CARD_TURN.toFixed(3)});
    }
    let side = fr1 * cos(a) + fr2 * sin(a);
    let ph = rnd * 6.2832;
    let fl = uv.y * w * (0.08 + 0.12 * gust);
    let flutter = vec3<f32>(sin(t * 1.7 + ph * 5.1), 0.45 * sin(t * 2.6 + ph * 3.3), sin(t * 1.3 + ph * 4.7)) * fl;
    return c + side * ((uv.x - 0.5) * w) + flutter;
  }
`);
// a direction of the variant turned by the instance's yaw
const plantDir = wgslFn(`
  fn plantDir(d: vec3<f32>, yaw: f32) -> vec3<f32> {
    let c = cos(yaw);
    let s = sin(yaw);
    return normalize(vec3<f32>(d.x * c + d.z * s, d.y, -d.x * s + d.z * c));
  }
`);
// ---- dithered cross-fade between levels: keep the fragment if its screen hash is under the fade (or, for the
// level fading out, -fade: over it), so the two levels together cover every pixel once
const DITHER = `
    let hh = fract(sin(dot(floor(frag), vec2<f32>(12.9898, 78.233))) * 43758.5453);
    if (fade >= 0.0) { if (hh >= fade) { discard; } } else { if (hh < -fade) { discard; } }`;

// ---- THE COLOUR. The wood and the leaves are drawn apart (each variant and level two draws): one shader for both
// sampled the bark and the atlas for every pixel, and the leaves' discard cost the wood its early depth test --
// half the draws, but the plants' GPU time up by half again.

// the wood: the bark's albedo and normal map in the branch's frame (the tangent runs along it)
const woodFrag = wgslFn(`
  fn woodFrag(alb: vec3<f32>, nm: vec3<f32>, n: vec3<f32>, tg: vec3<f32>, tone: vec4<f32>, tint: f32, snow: f32,
              maskMode: f32, fade: f32, frag: vec2<f32>, eye: vec3<f32>, pw: vec3<f32>) -> vec4<f32> {
    ${DITHER}
    if (maskMode > 0.5) { return vec4<f32>(0.0, 0.0, 0.0, 1.0); }
    var N = normalize(n);
    if (dot(N, eye - pw) < 0.0) { N = -N; }
    let T = normalize(tg - N * dot(tg, N));
    let B = cross(N, T);
    let m = nm * 2.0 - 1.0;
    let nn = normalize(T * m.y + B * m.x + N * max(0.2, m.z));
    let k = ${lightWGSL("nn")};
    var c = alb * k * tone.x * (1.0 + 0.12 * tint);
    if (snow > 0.001) {
      let up = smoothstep(0.25, 0.8, nn.y);
      c = mix(c, vec3<f32>(0.9, 0.93, 0.98) * k, snow * up * 0.85);
    }
    return vec4<f32>(c, 1.0);
  }
`);

// the leaves (cards and fronds): tex the atlas sample (alpha sharpened to a one-pixel edge for alpha-to-coverage,
// lifted with the mip so a far crown keeps its leaves), crownN the crown's normal, bent toward the card's own
const leafFrag = wgslFn(`
  fn leafFrag(tex: vec4<f32>, auv: vec2<f32>, atlasSize: vec2<f32>, crownN: vec3<f32>, pw: vec3<f32>, eye: vec3<f32>,
              tone: vec4<f32>, tint: f32, seas: vec4<f32>, autumnCol: vec3<f32>, flags: vec4<f32>, snow: f32,
              maskMode: f32, fade: f32, frag: vec2<f32>, cloud: f32, fruit: vec3<f32>) -> vec4<f32> {
    ${DITHER}
    let rnd = tone.y;
    // winter: a deciduous tree's leaves gone (each card by its own random); and the card's clear texels at once --
    // most of a card's pixels (WGSL's discard only demotes the pixel, so the derivatives below still hold)
    if ((flags.x > 0.5 && fract(rnd * 3.71) < seas.y) || tex.a < 0.004) { discard; }
    let dx = dpdx(auv * atlasSize);
    let dy = dpdy(auv * atlasSize);
    let mip = max(0.0, 0.5 * log2(max(dot(dx, dx), dot(dy, dy))));
    var a = tex.a * (1.0 + mip * 0.3);
    a = (a - 0.5) / max(abs(dpdx(a)) + abs(dpdy(a)), 1e-4) + 0.5;
    if (a <= 0.0) { discard; }
    if (maskMode > 0.5) {
      if (a < 0.5) { discard; }
      return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    var f = normalize(cross(dpdx(pw), dpdy(pw)));
    if (dot(f, eye - pw) < 0.0) { f = -f; }
    let n = normalize(normalize(crownN) * 0.7 + f * 0.3 * flags.y);
    let k = ${lightWGSL("n")};
    var c = tex.rgb * (1.0 + 0.16 * tint);
    // a bush's berries are painted in the marker magenta (bake.js FRUIT_MARKER): recoloured to its own fruit,
    // keeping their light and dark (the value) and the highlight (the green the gradient mixed in)
    if (fruit.x >= 0.0) {
      let v = max(tex.r, tex.b);
      let berry = smoothstep(0.06, 0.2, min(tex.r, tex.b) - tex.g);
      c = mix(c, mix(fruit * v * 1.3, vec3<f32>(v), clamp(tex.g / max(v, 1e-3), 0.0, 1.0) * 0.8), berry);
    }
    // autumn: a share of the cards turned, keeping the painted leaf's light and dark
    if (flags.x > 0.5) {
      let turn = smoothstep(0.0, 0.25, seas.x * 1.25 - fract(rnd * 7.31));
      let lum = dot(tex.rgb, vec3<f32>(0.3, 0.55, 0.15));
      let ac = autumnCol * (0.65 + 0.7 * fract(rnd * 13.7)) * lum * 3.2;
      c = mix(c, mix(ac, autumnCol * lum * 1.6, step(0.8, fract(rnd * 5.3))), turn);
    }
    let through = max(0.0, dot(normalize(pw - eye), ${SUN}));
    var lit = c * k * tone.x * mix(vec3<f32>(0.92, 0.98, 0.96), vec3<f32>(1.1, 1.08, 0.9), smoothstep(0.62, 1.0, k));
    lit = lit + c * vec3<f32>(0.55, 0.6, 0.2) * through * through * through * tone.x;
    if (snow > 0.001) {   // (snow caught on the sprays that face up, in clots: where the painted leaf is light, the outer crown more)
      let up = smoothstep(-0.1, 0.7, n.y) * smoothstep(0.4, 0.9, tone.x);
      let clot = smoothstep(0.12, 0.38, dot(tex.rgb, vec3<f32>(0.4, 0.45, 0.15)) * 2.2 + fract(rnd * 17.3) * 0.3 - 0.15);
      lit = mix(lit, vec3<f32>(0.9, 0.93, 0.98) * k, snow * clamp(up * clot, 0.0, 0.8));
    }
    return vec4<f32>(lit * cloud, clamp(a, 0.0, 1.0));
  }
`);

// the atlas column a card shows (bake.js bakeSprays: five, and a sixth for bodies -- cells): 0/1 its leafy sprays (by its random) -- far (the far
// levels' cards) the filled one, 4 -- 2 when it is in flower (show.x: the share now), 3 when it bears fruit (show.y;
// by another random of its own -- flowers win)
const cardUv = wgslFn(`
  fn cardUv(uv: vec2<f32>, tone: vec4<f32>, show: vec2<f32>, far: f32, cells: f32) -> vec2<f32> {
    if (tone.w < -0.5) { return uv; }   // (a body -- a banana's bunch, a cacao's pod: its uv is the atlas's already, mesh.js)
    var cell = floor(fract(tone.y * 2.93) * 2.0);
    if (far > 0.5) { cell = 4.0; }
    if (fract(tone.z * 7.31 + tone.y * 3.17) < show.y) { cell = 3.0; }
    if (tone.z < show.x) { cell = 2.0; }
    return vec2<f32>((cell + clamp(uv.x, 0.004, 0.996)) / cells, clamp(uv.y, 0.004, 0.996));
  }
`);
// ---- the kinds -----------------------------------------------------------------------------------------------
// a kind's species and, for a bush, its fruit's slot (0 none, 1.. the BUSH_FRUITS by their order): the bushes of every
// fruit are ONE kind "bush" -- one set of draws -- each instance carrying its slot (in its tint: packTint)
function speciesOf(kind, own = {}) {
  if (own[kind] && kind !== "bush") return { key: kind, S: own[kind], slot: 0 };
  if (TREES[kind]) return { key: kind, S: TREES[kind], slot: 0 };
  const SHRUB_ = own.bush ?? SHRUB;
  if (kind === "bush") return { key: "bush", S: SHRUB_, slot: 0 };
  if (kind.startsWith("bush:")) {
    const i = BUSH_FRUITS.findIndex((b) => b.name === kind.slice(5));
    if (i < 0) throw new Error(`plants: no bush fruit "${kind.slice(5)}"`);
    return { key: "bush", S: SHRUB_, slot: i + 1 };
  }
  throw new Error(`plants: no kind "${kind}"`);
}
// an instance's tint (-1..1) and its fruit slot in one float, and the shader's way back
const packTint = (tint, slot) => tint + 4 * slot;
const unpackTint = (y) => { const slot = y.div(4).round(); return { slot, tint: y.sub(slot.mul(4)) }; };
// the bush fruits' colours, a texel each (slot 1 at texel 0), sampled by the slot
const fruitPalette = (() => {
  const d = new Uint8Array(8 * 4), c = new THREE.Color();
  BUSH_FRUITS.forEach((f, i) => { c.setHex(f.color); d.set([c.r * 255, c.g * 255, c.b * 255, 255].map(Math.round), i * 4); });
  const t = new THREE.DataTexture(d, 8, 1, THREE.RGBAFormat);
  t.colorSpace = THREE.SRGBColorSpace; t.magFilter = t.minFilter = THREE.NearestFilter; t.needsUpdate = true;
  return t;
})();
const KIND_SEED = (kind) => [...kind].reduce((a, ch) => (a * 31 + ch.charCodeAt(0)) | 0, 7);

// THE TREE AS THE GAME KNOWS IT (index.html treeCol; squirrels.js climbs `trunk`, perchers.js and nests.js sit on
// `boughs`; the shade and the leaf litter reach to `crown`), in the variant's own frame, unscaled:
//   trunkR    the trunk's radius at its foot             height  the top of the leaves
//   trunk     the trunk's centreline, foot to fork (and on up the leaders): segments { a, b, r0, r1 }
//   boughs    the limbs and branches a bird can sit on -- near level (rising or falling at most 1 in 2), a hand's breadth
//             thick: segments as the trunk's (none on a palm)
//   crown     its reach over the ground: metres from the trunk nine leaves in ten lie within
//   evergreen, autumnC (the colour its leaves turn: the litter's)
export function plantInfo(S, sk) {
  const seg = (b, i) => ({ a: b.pts[i], b: b.pts[i + 1], r0: b.rad[i], r1: b.rad[i + 1] });
  const trunk = [], boughs = [];
  for (const b of sk.branches) for (let i = 0; i < b.pts.length - 1; i++) {
    if (b.level === 0) trunk.push(seg(b, i));
    else if (b.level <= 2 && !b.dead && S.habit !== "palm") {
      const d = b.pts[i + 1].map((v, k) => v - b.pts[i][k]);
      if (Math.abs(d[1]) * 2 < Math.hypot(d[0], d[2]) && (b.rad[i] + b.rad[i + 1]) / 2 > .03) boughs.push(seg(b, i));
    }
  }
  const pts = sk.cards.length ? sk.cards.map((c) => c.p) : sk.fronds.map((f) => f.p.map((v, k) => v + f.d[k] * f.len * .6));
  const reach = pts.map((p) => Math.hypot(p[0], p[2])).sort((a, b) => a - b);
  return { trunkR: sk.branches[0]?.rad[0] ?? .1, height: sk.H, trunk, boughs, crown: reach.length ? reach[Math.floor(reach.length * .9)] : sk.H * .25,
           evergreen: !!S.evergreen, autumnC: S.evergreen ? undefined : S.colors.autumn };
}
// the same, scaled by k about the foot
function scaledInfo(I, k) {
  if (k === 1) return I;
  const sc = (g) => ({ a: g.a.map((v) => v * k), b: g.b.map((v) => v * k), r0: g.r0 * k, r1: g.r1 * k });
  return { ...I, trunkR: I.trunkR * k, height: I.height * k, crown: I.crown * k, trunk: I.trunk.map(sc), boughs: I.boughs.map(sc) };
}

// (species: definitions of its own by kind -- "oak", "bush" -- over species.js's: the asset manager's, being edited)
export function createPlantField(scene, { species = {} } = {}) {
  const kinds = new Map();    // kind ("bush" for every bush) -> { kind, S, variants: [{ sk, info, r, geo }], mats, draws, cap, instances: [] }
  const all = [];             // every instance: { K, v, name (the kind as added: "bush:currant"), x, y, z, yaw, scale, tint (packed), phase }
  const group = new THREE.Group();
  group.name = "plants";
  scene.add(group);
  const uT = uniform(0).setGroup(renderGroup).onRenderUpdate(() => FOLIAGE_T.value);
  const uMask = uniform(0).setGroup(renderGroup).onRenderUpdate(() => MASK_MODE.value);
  const uSnow = uniform(0).setGroup(renderGroup).onRenderUpdate(() => SNOW.value);
  const uWdir = uniform(new THREE.Vector2(WIND_DIR.x, WIND_DIR.y));
  // (snow lying turns and drops the broadleaves' last leaves with it: a winter world is a bare one)
  const seas = vec4(SEASON.autumn.max(uSnow), SEASON.bare.max(uSnow), SEASON.bloom, SEASON.fruit);

  function materials(K) {
    const { S } = K, seed = KIND_SEED(K.kind), bush = K.kind === "bush";
    const bark = bakeBark(S, seed);
    const atlas = K.atlas;
    const { flower, fruit } = atlas.userData;
    const deciduous = !S.evergreen;
    const flags = uniform(new THREE.Vector4(deciduous ? 1 : 0, S.habit === "palm" ? .3 : 1, 0, 0));
    const autumnCol = uniform(new THREE.Color(S.colors.autumn ?? S.colors.leaf[0]));
    // which share of the sprays is in flower now, and which in fruit
    const showF = flower ? (S.season?.flowers ? SEASON.flowers.mul(S.season.flowers) : SEASON.bloom.mul(S.season?.blossom ?? .8)) : float(0);
    const showR = fruit ? SEASON.fruit.mul(S.season?.fruit ?? .5) : float(0);
    const A = { i0: attribute("aI0", "vec4"), i1: attribute("aI1", "vec4"), wind: attribute("aWind", "vec3"), tone: attribute("aTone", "vec4") };
    const { slot, tint } = unpackTint(A.i1.y);
    // a bush shows berries only if it bears (slot > 0), in its fruit's colour; the trees' fruit is painted in its own
    const showNow = vec2(showF, bush ? showR.mul(slot.greaterThan(.5).select(float(1), float(0))) : showR);
    const fruitCol = bush ? texture(fruitPalette, vec2(varying(slot, "vPlantSlot").sub(.5).div(8), .5)).rgb : vec3(-1);
    const fade = A.i1.w;
    const pt = (p, wind = A.wind) => plantPoint({ p, i0: A.i0, i1: A.i1, wind, t: uT, gust: WIND.strength, wdir: uWdir });
    const cloudAt = (p) => uMask.greaterThan(.5).select(float(1), varying(cloudShade({ p: p.xz, t: CLOUD.t, amount: CLOUD.amount, cover: CLOUD.cover }), "vPlantCloud"));
    const crownN = varying(plantDir({ d: attribute("normal", "vec3"), yaw: A.i0.w }), "vPlantN");
    // the wood
    const wood = new THREE.MeshBasicNodeMaterial();
    const pw = pt(attribute("position", "vec3"));
    wood.positionNode = pw;
    const tile = uv();
    const wout = woodFrag({ alb: texture(bark.map, tile).rgb, nm: texture(bark.normalMap, tile).rgb, n: crownN,
                            tg: varying(plantDir({ d: attribute("tangent", "vec3"), yaw: A.i0.w }), "vPlantT"),
                            tone: A.tone, tint, snow: uSnow, maskMode: uMask, fade, frag: screenCoordinate, eye: cameraPosition, pw: varying(pw, "vPlantPw") });
    wood.colorNode = wout.xyz.mul(cloudAt(pw));
    // the leaves: cards (and a palm's fronds) -- opaque, both sides: their edges are coverage, not blending (blended,
    // they showed whatever had been drawn before them); far: the far levels' cards, on the filled spray
    // (src: the vertex's data -- its attributes, or a far level's pulled from its buffer: pulledVertex)
    const own = { pos: attribute("position", "vec3"), uv: uv(), normal: attribute("normal", "vec3"), tangent: attribute("tangent", "vec3"), wind: A.wind, tone: A.tone };
    const leafMat = (far, src = own) => {
      const m = new THREE.MeshBasicNodeMaterial({ alphaToCoverage: true, side: THREE.DoubleSide });
      const c = pt(src.pos, src.wind);
      const p = cardCorner({ c, ax: plantDir({ d: src.tangent, yaw: A.i0.w }), uv: src.uv, pack: src.tone.w, scale: A.i1.x,
                             rnd: src.tone.y, eye: cameraPosition, t: uT, gust: WIND.strength });
      m.positionNode = p;
      const auv = varying(cardUv({ uv: src.uv, tone: src.tone, show: showNow, far: float(far ? 1 : 0), cells: float(atlas.userData.cells) }), "vPlantUv");
      const tone = src === own ? A.tone : varying(src.tone, "vPlantTone");
      const out = leafFrag({ tex: texture(atlas, auv), auv, atlasSize: uniform(new THREE.Vector2(atlas.image.width, atlas.image.height)),
                             crownN: src === own ? crownN : varying(plantDir({ d: src.normal, yaw: A.i0.w }), "vPlantN"),
                             pw: varying(p, "vPlantPw"), eye: cameraPosition, tone, tint, seas, autumnCol, flags,
                             snow: uSnow, maskMode: uMask, fade, frag: screenCoordinate, cloud: cloudAt(p), fruit: fruitCol });
      m.colorNode = out.xyz;
      m.opacityNode = out.w;
      return m;
    };
    // the far levels' cards: each level its own material, its vertices pulled from its buffer
    const mats = { wood, leaf: leafMat(false), bark, atlas, pullN: {} };
    mats.body = mats.leaf;   // (a banana's bunch, a cacao's pods: drawn as the leaves are, on their own vertices at every level)
    if (S.habit !== "palm") for (let L = 1; L < K.variants[0].geo.length; L++) {
      const part = "far" + L, P = pullBuffer(K.variants.map((V) => V.geo[L].find(([k]) => k === part)[1]));
      mats[part] = leafMat(true, pulledVertex(P, A.i1));
      mats.pullN[part] = P.N;
    }
    return mats;
  }

  // the near level: the leaves, and the wood in what they leave of the budget (TRI_BUDGET a tree)
  // (and where the wood cannot come down that far -- a big oak's limbs alone -- the leaves give up cards to it, each
  //  card two triangles; leafMesh grows the rest a little so the crown keeps its cover). The far levels: the same
  //  tree, its details left out -- their cards a share of these very ones (the same maxCards: the same thinning)
  const MIN_CARDS = Math.round(TRI_BUDGET * .15 / 2);
  function levels(S, sk, box, cells) {
    let maxCards, leaf = leafMesh(S, sk, { aspect: SPRAY_ASPECT, box });
    const body = sk.bodies.length ? (lod) => [["body", bodyMesh(sk, lod, cells)]] : () => [], near = body(0), bt = near[0]?.[1].tris ?? 0;
    const wood = woodMesh(S, sk, 0, { budget: Math.max(1200, TRI_BUDGET - leaf.tris - bt) });
    // (twigs pruned to fit: their cards moved onto the wood still drawn, and meshed again -- the same count, so the same
    //  budget; every level's cards are these)
    if (wood.minR) { rootCards(sk, wood.minR); leaf = leafMesh(S, sk, { aspect: SPRAY_ASPECT, box }); }
    if (wood.tris + leaf.tris + bt > TRI_BUDGET && !sk.fronds.length)
      // (never none: a wood that ate the budget -- a bamboo's hundreds of side shoots -- still leaves the leaves a share)
      leaf = leafMesh(S, sk, { aspect: SPRAY_ASPECT, box, maxCards: maxCards = Math.max(MIN_CARDS, Math.floor((TRI_BUDGET - wood.tris - bt) / 2)) });
    const palm = !!sk.fronds.length;
    const far = (lod) => [["wood", woodMesh(S, sk, lod)], [palm ? "leaf" : "far" + lod, leafMesh(S, sk, { aspect: SPRAY_ASPECT, box, maxCards, lod })], ...body(lod)];
    return [[["wood", wood], ["leaf", leaf], ...near], far(1), far(2)];
  }
  // a kind's variants grown, its sprays painted, and every variant meshed at its levels -- the cards cut to where the
  // paintings are (bake.js trims)
  function grow(K) {
    const { S } = K, n = K.kind === "bush" ? PLANT_LOD.bushVariants : PLANT_LOD.variants, seed = KIND_SEED(K.kind);
    const sks = Array.from({ length: n }, (_, v) => growPlant(S, seed + v * 101));
    const t0 = performance.now();
    K.atlas = bakeSprays(S, seed, K.kind === "bush" ? FRUIT_MARKER : null);
    timing.bake += performance.now() - t0;
    const box = K.atlas.userData.sprayBox;
    // (each level its wood and its leaves: cards, or a palm's fronds)
    K.variants = sks.map((sk) => ({ sk, info: plantInfo(S, sk), r: Math.max(sk.H * .55, crownShape(sk).R * 1.2), geo: levels(S, sk, box, K.atlas.userData.cells) }));
  }

  const timing = { grow: 0, bake: 0 };   // (ms spent growing and meshing the variants, and baking the textures)
  function kindOf(key, S) {
    if (!kinds.has(key)) {
      const K = { kind: key, S, instances: [], mats: null }, t0 = performance.now(), b0 = timing.bake;
      grow(K);
      timing.grow += performance.now() - t0 - (timing.bake - b0);
      kinds.set(key, K);
    }
    return kinds.get(key);
  }

  // a draw: one part of one variant at one level, with the instance buffers of its kind's capacity
  function makeDraw(K, arrays, mat, cap, lod) {
    const g = new THREE.InstancedBufferGeometry();
    for (const [name, size] of ATTRS) if (arrays[name]) g.setAttribute(name, new THREE.BufferAttribute(arrays[name], size));
    g.setIndex(new THREE.BufferAttribute(arrays.index, 1));
    const i0 = new THREE.InstancedBufferAttribute(new Float32Array(cap * 4), 4), i1 = new THREE.InstancedBufferAttribute(new Float32Array(cap * 4), 4);
    i0.setUsage(THREE.DynamicDrawUsage); i1.setUsage(THREE.DynamicDrawUsage);
    g.setAttribute("aI0", i0); g.setAttribute("aI1", i1);
    g.instanceCount = 0;
    const mesh = new THREE.Mesh(g, mat);
    mesh.frustumCulled = false;
    mesh.userData.cut = true;               // (its shape is the shader's: never an occluder through an override material)
    if (lod === 0) mesh.layers.enable(NOGRASS_LAYER);   // ...it writes the grass mask itself (MASK_MODE) -- the near level
                                                        // only: the grass fringe is gone (grass.js FRINGE.fade) before the next
    mesh.visible = false;
    group.add(mesh);
    return { mesh, i0, i1, n: 0, tris: arrays.tris };
  }

  let draws = [], cells = [], tris = 0;   // (every draw of every kind; the cells of plants; this frame's triangles)
  // an instance into its level's draws (fade: its share of the pixels, negative for the level fading out)
  function put(it, L, fade) {
    for (const { d, tris: t } of it.K.draws[it.v][L]) {
      const o = d.n * 4, a = d.i0.array, b = d.i1.array;
      a[o] = it.x; a[o + 1] = it.y; a[o + 2] = it.z; a[o + 3] = it.yaw;
      b[o] = it.scale; b[o + 1] = it.tint; b[o + 2] = it.phase; b[o + 3] = fade;
      d.n++; tris += t;
    }
  }
  const field = {
    group, SEASON,
    // a plant: its kind, where it stands (y: the ground), turned by yaw; as grown, or scaled (scale), or to a height in metres
    add(kind, x, y, z, { yaw = 0, scale = 1, height = 0, seed = all.length } = {}) {
      const { key, S, slot } = speciesOf(kind, species), K = kindOf(key, S), h = Math.imul(seed + 1, 2654435761) >>> 0;
      const v = h % K.variants.length, V = K.variants[v];
      if (height > 0) scale = height / V.sk.H;
      const it = { K, v, name: kind, x, y, z, yaw, scale, tint: packTint(((h >>> 8) % 1000) / 500 - 1, slot), phase: ((h >>> 4) % 628) / 100 + v * PHASE_SPAN };
      K.instances.push(it); all.push(it);
      return { kind, variant: v, info: scaledInfo(V.info, scale), position: { x, y, z }, rotY: yaw };
    },
    // the meshes, sized for the instances added so far; the instances' bounds and level distances, and the CELLS
    // they are culled by (CELL metres square: a whole cell out of view is skipped without looking at its plants)
    build() {
      for (const K of kinds.values()) {
        if (!K.mats) { const t0 = performance.now(); K.mats = materials(K); timing.bake += performance.now() - t0; }
        const cap = Math.max(1, K.instances.length) * 2;   // (x2: an instance fading between two levels is in both)
        if (K.cap >= cap) continue;
        if (K.flat) for (const d of K.flat) { group.remove(d.mesh); d.mesh.geometry.dispose(); }
        K.cap = cap;
        // K.draws[variant][level]: its parts' draws ({ d, tris: the variant's own }) -- the near level a draw for each
        // variant (they are heavy), the others one for all of them, the variants' meshes end to end (plantPoint)
        const geo = K.variants.map((V, v) => V.geo.map((parts) => parts.map(([part, a]) => [part, ofVariant(a, v)])));
        K.draws = geo.map((levels) => [levels[0].map(([part, a]) => ({ d: makeDraw(K, a, K.mats[part], cap, 0), tris: a.tris }))]);
        for (let L = 1; L < geo[0].length; L++) {
          const shared = geo[0][L].map(([part], j) => makeDraw(K, K.mats.pullN[part] ? pullShape(K.mats.pullN[part]) : joined(geo.map((levels) => levels[L][j][1])),
                                                               K.mats[part], cap, L));
          geo.forEach((levels, v) => K.draws[v][L] = levels[L].map(([, a], j) => ({ d: shared[j], tris: a.tris })));
        }
        K.flat = [...new Set(K.draws.flat(2).map((e) => e.d))];
      }
      draws = [...kinds.values()].flatMap((K) => K.flat ?? []);
      const byCell = new Map();
      for (const it of all) {
        const V = it.K.variants[it.v], H = V.sk.H * it.scale, k = Math.pow(Math.max(2, H) / 15, .6);
        Object.assign(it, { sy: it.y + H * .5, R: V.r * it.scale, ey: it.y + H * .4, near: PLANT_LOD.near * k, mid: PLANT_LOD.mid * k });
        const key = Math.floor(it.x / CELL) + "," + Math.floor(it.z / CELL);
        if (!byCell.has(key)) byCell.set(key, []);
        byCell.get(key).push(it);
      }
      cells = [...byCell.values()].map((items) => {   // (each cell's sphere: round its plants' middle, reaching all of theirs)
        const n = items.length, c = new THREE.Vector3(items.reduce((a, it) => a + it.x, 0) / n, items.reduce((a, it) => a + it.sy, 0) / n, items.reduce((a, it) => a + it.z, 0) / n);
        return { sphere: new THREE.Sphere(c, Math.max(...items.map((it) => Math.hypot(it.x - c.x, it.sy - c.y, it.z - c.z) + it.R))), items };
      });
    },
    // every plant gone (the meshes stay, for the next build's plants: a season's rebuild plants the same again)
    clear() {
      for (const K of kinds.values()) K.instances = [];
      all.length = 0; cells = [];
    },
    // every frame: each tree's level by its distance (a tree's height scales it), culled to the view, the fades
    update(camera) {
      _m.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
      _f.setFromProjectionMatrix(_m);
      const cx = camera.position.x, cy = camera.position.y, cz = camera.position.z, w = PLANT_LOD.fade, force = PLANT_LOD.force;
      for (const d of draws) d.n = 0;
      tris = 0;
      let shown = 0;
      for (const cell of cells) {
        if (!_f.intersectsSphere(cell.sphere)) continue;
        for (const it of cell.items) {
          _s.center.set(it.x, it.sy, it.z); _s.radius = it.R;
          if (!_f.intersectsSphere(_s)) continue;
          shown++;
          const dist = Math.hypot(it.x - cx, it.ey - cy, it.z - cz), near = it.near, mid = it.mid;
          let lod, f = 1;   // f: how far into its level (1: fully), 0..1 over the fade band before the next level
          if (force >= 0) lod = force;
          else if (dist < near) { lod = 0; f = clamp01((near - dist) / (near * w)); }
          else if (dist < mid) { lod = 1; f = clamp01((mid - dist) / (mid * w)); }
          else lod = 2;
          if (f < 1 && lod < 2) { put(it, lod, f); put(it, lod + 1, -f); }   // (the two levels share the pixels: the near one's share is f)
          else put(it, lod, 1);
        }
      }
      for (const d of draws) {
        d.mesh.geometry.instanceCount = d.n;
        d.mesh.visible = d.n > 0;
        if (d.n) {
          d.i0.clearUpdateRanges(); d.i0.addUpdateRange(0, d.n * 4); d.i0.needsUpdate = true;
          d.i1.clearUpdateRanges(); d.i1.addUpdateRange(0, d.n * 4); d.i1.needsUpdate = true;
        }
      }
      field.stats = { trees: all.length, shown, tris };
    },
    // everything let go: the meshes, the materials, the bakes (a field made for a while: the asset manager's)
    dispose() {
      scene.remove(group);
      for (const K of kinds.values()) {
        for (const d of K.flat ?? []) d.mesh.geometry.dispose();
        if (!K.mats) continue;
        for (const m of [K.mats.wood, K.mats.leaf, K.mats.far1, K.mats.far2]) m?.dispose();
        for (const t of [K.mats.bark.map, K.mats.bark.normalMap, K.mats.atlas]) t?.dispose();
      }
      kinds.clear(); all.length = 0; cells = []; draws = [];
    },
    // the first plant added as `kind` (the lab's camera: "bush:currant" finds a currant bush)
    first: (kind) => all.find((it) => it.name === kind),
    kinds, timing,
  };
  return field;
}
// a mesh's vertex attributes -- with the instances' two, WebGPU's limit of eight. aWind (mesh.js: a point's sway and
// phase) gains a third number here, the variant the point is of (plantPoint)
const ATTRS = [["position", 3], ["normal", 3], ["uv", 2], ["tangent", 3], ["aWind", 3], ["aTone", 4]];
// a variant's mesh (mesh.js Geo output) with its variant number in aWind
function ofVariant(a, v) {
  const n = a.position.length / 3, w = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { w[i * 3] = a.aWind[i * 2]; w[i * 3 + 1] = a.aWind[i * 2 + 1]; w[i * 3 + 2] = v; }
  return { ...a, aWind: w };
}
// THE FAR CARDS' VERTICES, PULLED: a far level draws all of a kind's variants at once. Merged end to end (as its
// wood is: joined), every instance would run all the variants' vertices, two thirds of them only to be sent out of
// view -- the far cards were most of the plants' vertex time (2026-11-18: ~2 ms of a dense wood's frame). So their
// vertices are in a storage buffer, PULL_VEC4 vec4s each, a variant's after another's, each padded to the longest
// (out of view: no triangle); the draw runs the longest's count, every vertex reading its instance's own variant.
// All far cards are quads, so one index serves every variant.
//   [pos.xyz, uv.x] [normal.xyz, uv.y] [tangent.xyz, bend] [tone] [phase, -, -, -]
const PULL_VEC4 = 5;
function pullBuffer(list) {   // (each variant's arrays, mesh.js leafMesh -- aWind as grown: bend, phase)
  const N = Math.max(4, ...list.map((a) => a.position.length / 3)), data = new Float32Array(list.length * N * PULL_VEC4 * 4);
  list.forEach((a, v) => {
    const n = a.position.length / 3;
    for (let i = 0; i < N; i++) {
      const o = (v * N + i) * PULL_VEC4 * 4;
      if (i >= n) { data[o + 1] = -1e6; continue; }
      data.set([a.position[i * 3], a.position[i * 3 + 1], a.position[i * 3 + 2], a.uv[i * 2],
                a.normal[i * 3], a.normal[i * 3 + 1], a.normal[i * 3 + 2], a.uv[i * 2 + 1],
                a.tangent[i * 3], a.tangent[i * 3 + 1], a.tangent[i * 3 + 2], a.aWind[i * 2],
                a.aTone[i * 4], a.aTone[i * 4 + 1], a.aTone[i * 4 + 2], a.aTone[i * 4 + 3], a.aWind[i * 2 + 1], 0, 0, 0], o);
    }
  });
  return { N, buf: new THREE.StorageBufferAttribute(data, 4) };
}
// a pulled vertex's data, as the leaf material reads it (i1.z: the instance's phase, its variant in it)
function pulledVertex({ N, buf }, i1) {
  const s = storage(buf, "vec4", buf.count).toReadOnly(), v = i1.z.div(PHASE_SPAN).floor();
  const base = v.toUint().mul(uint(N)).add(vertexIndex).mul(uint(PULL_VEC4));
  const e = [0, 1, 2, 3, 4].map((k) => s.element(base.add(uint(k))));
  return { pos: e[0].xyz, uv: vec2(e[0].w, e[1].w), normal: e[1].xyz, tangent: e[2].xyz, wind: vec3(e[2].w, e[4].x, v), tone: e[3] };
}
// its draw's shape: N vertices (a position only to count them by: the material reads its own) in quads
function pullShape(N) {
  const index = new Uint32Array(N / 4 * 6);
  for (let q = 0; q < N / 4; q++) index.set([q * 4, q * 4 + 2, q * 4 + 1, q * 4 + 1, q * 4 + 2, q * 4 + 3], q * 6);
  return { position: new Float32Array(N * 3), index, tris: N / 2 };
}
// meshes end to end, as one
function joined(list) {
  const out = { tris: 0 }, nv = list.map((a) => a.position.length / 3);
  for (const [name, size] of ATTRS) {
    out[name] = new Float32Array(nv.reduce((x, y) => x + y, 0) * size);
    let o = 0;
    list.forEach((a, k) => { out[name].set(a[name], o * size); o += nv[k]; });
  }
  out.index = new Uint32Array(list.reduce((x, a) => x + a.index.length, 0));
  let o = 0, base = 0;
  list.forEach((a, k) => { for (let i = 0; i < a.index.length; i++) out.index[o + i] = a.index[i] + base; o += a.index.length; base += nv[k]; out.tris += a.tris; });
  return out;
}
const clamp01 = (x) => Math.max(0, Math.min(1, x));
const CELL = 48;   // (metres: the culling cells' size)
const _m = new THREE.Matrix4(), _f = new THREE.Frustum(), _s = new THREE.Sphere();
