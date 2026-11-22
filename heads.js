// THE HEADS (2026-09-30): people's faces as low-poly MESHES (face.js through items.js: assets/items/faces/*), not
// SDF parts -- a head on the anatomy, with its brow, sockets, cheekbones, nose, lips, chin, jaw, ears. Like the tools
// in hands (tools.js): built once per kind, every kind in one batched pool (batchpool.js: one draw for all the faces
// in view, not one per kind), every copy placed each frame at a
// person's head part, read back from the posed composite (herd.ends): the head's axis from the head capsule (now a
// pin), and where it looks from the pin of a nose people.js keeps as the GAZE.
//
// A person's def carries `face` { kind (man | woman | child | elder | beast-man), seed, skin, hair (colours), hr (the
// cranium radius), style (its hairstyle: assets/items/hair), fringe, head, gaze (part indices) }; composite.js keeps it on the animal. A kind here is that plus the
// colours, so a village of a hundred shares a few dozen meshes; each mesh is one geometry with its colours in the
// vertices (every face material is plain paint), shaded HALF-LAMBERT under the world's one sun (faceMaterial,
// light.js) -- in the world, so a head turned toward the sun lights up and one turned away falls into shade.
import * as THREE from "three";
import { batchPool } from "./batchpool.js";
import { ASSETS } from "./catalogue.js";
import { buildItem } from "./items.js";
import { flatten } from "./defs.js";
import { FACE_ATTRS, FACE_PARAMS } from "./face.js";   // (the canon's values: what a face variety's deltas add to)
import { paintedGeometry } from "./tools.js";
import { smoothArrays, cavityArrays } from "./facecavity.js";   // (their sums, three-free: the far heads' worker runs them too)
import { wgslFn, normalWorld, positionWorld, cameraPosition, attribute, uv, texture, vec3, vec4, positionLocal, positionGeometry, time, sin } from "three/tsl";
import { WIND, WIND_DIR, grassWind } from "./grass.js";   // (the hair stirs in the grass's wind)
import { LIGHT } from "./light.js";   // the world's one static sun
import { stoneMaterial, PAINTED } from "./shell.js";   // a statue's head: the stone its body is (statues.js)
import { PREGEN, pregenOn, pregenMiss, recordFor, hasher, fetchFace, packFace, unpackFace } from "./pregen.js";   // (heads built once by build/pregen.py)

const CANON_R = .090;   // the canon face's cranium radius (face.js LEVELS): scaled to each person's hr (a little under it: the SDF hair cap covers the skull)
const HAIRLINE = .042;  // the mesh's own hairline, under the cap's: whatever skull shows through the cap shows as hair
const SEEDS = 16;       // how many of a kind and colouring are told apart (their ranges drawn by the seed: faceVariety) -- 5 made a village of a few faces

// A BUILT FACE AS ONE GEOMETRY: tools.js paintedGeometry, shaded by faceMaterial in the WORLD's light (light.js) -- the
// lips too: face.js gives every vertex the smooth surface's own normal, so their rolls take the light as the skin does
// WET: the eyes (all but the catchlight, which is the highlight already) and, less, the lips take a sharp specular
export const WET = { eye: 1, iris: 1, pupil: 1, limbus: 1, lip: .3 };
const cavities = new WeakMap();   // built face -> its vertices' darkness (cavityOf: the shape's, kept for every colouring of it)
// (a living face's normals SMOOTHED a little too -- LIVING_SMOOTH, smoothNormals below: the field's creases along its
//  guide lines read as hard planes down the cheeks and the jaw, a faceted mask; worked out once a shape, as the hollows)
export const LIVING_SMOOTH = { r: .013, cos: .5 };
const smoothed = new WeakMap(), carved = new WeakMap();   // (built face -> its smoothed normals: a living face's, a carved one's)
export const faceGeometry = (built, recolor = null) => {
  const geo = paintedGeometry(built, { strands: ["hair"], wet: WET, recolor });
  let dark = cavities.get(built);
  if (!dark) cavities.set(built, dark = cavityOf(geo));
  const sm = smoothed.get(built);
  if (sm && sm.length === geo.attributes.normal.array.length) geo.setAttribute("normal", new THREE.Float32BufferAttribute(sm, 3));
  else smoothed.set(built, smoothNormals(geo, LIVING_SMOOTH).attributes.normal.array);
  return cavityShade(geo, CAVITY, dark);
};
// A CARVED HEAD's geometry (a statue's: shell.js stoneMaterial `head`): no paint -- its hollows as an attribute of their own
// (`cavity`, the same darkness the paint takes), for the stone to cut them in; the hair's mask and uv for its locks
// -- its normals SMOOTHED (CARVED_SMOOTH): the face's field is creased along its guide lines, the cheekbone's, the mouth's
// corner to the jaw -- under paint unseen, in hard-lit stone a low-poly mask of planes. Its CURLS (`curl`: shell.js
// CURLS): a beard's, always; the hair's where its hairstyle is carved so (`carve: "curls"`, the ushnisha's snail curls)
// (`recolor`: a PAINTED one's colours -- shell.js PAINTED: its skin, hair, brows and lips, as a living face's)
export const stoneFaceGeometry = (built, { curls = false, recolor = null } = {}) => {
  const geo = paintedGeometry(built, { strands: ["hair"], wet: WET, recolor });
  let dark = cavities.get(built);
  if (!dark) cavities.set(built, dark = cavityOf(geo));
  geo.setAttribute("cavity", new THREE.Float32BufferAttribute(dark, 1));
  const curl = [];   // (per vertex, in paintedGeometry's order: each group's indices)
  for (const g of built.groups) { const v = g.roles?.has("beard") || (curls && g.roles?.has("hair")) ? 1 : 0; for (let i = 0; i < g.idx.length; i++) curl.push(v); }
  geo.setAttribute("curl", new THREE.Float32BufferAttribute(curl, 1));
  const sm = carved.get(built);   // (a shape's smoothing, once: a temple's statues share their heads)
  if (sm && sm.length === geo.attributes.normal.array.length) { geo.setAttribute("normal", new THREE.Float32BufferAttribute(sm, 3)); return geo; }
  carved.set(built, smoothNormals(geo).attributes.normal.array);
  return geo;
};
// SMOOTHED NORMALS: each vertex's normal the mean of those within `r` (falling off with the distance), only of points
// facing within `cos` of its own -- not across a lip to the other lip, a lid to the eye -- and of its own kind (skin,
// the wet eye); not the hair's (its locks are lit by their own relief)
export const CARVED_SMOOTH = { r: .022, cos: .3 };
export function smoothNormals(geo, C = CARVED_SMOOTH) {
  const out = smoothArrays(geo.attributes.position.array, geo.attributes.normal.array, geo.attributes.hairMask?.array, geo.attributes.wetMask?.array, C);
  geo.setAttribute("normal", new THREE.Float32BufferAttribute(out, 3));
  return geo;
}
// THE FACE'S HOLLOWS (2026-10-24): the sun's half-Lambert gives a head its round, not its form -- the eye sockets, the
// creases beside the nose and under the lower lip, the ear's bowl, the hairline under the hair read as flat paint. So
// every vertex is darkened by how CONCAVE the surface is round it: the mean of the points within `r` (two radii: the
// creases and the sockets) lies in front of a hollow and behind a bump -- its height over the vertex along the normal,
// over r, is the cavity (a bump's is below 0: no change). The darkening is `k` at a cavity of 1, warmer in the skin
// (`warm`: light through the skin is red in its folds), less on the wet eyes (`wet` its share) -- and none on the hair
// (its strands are dense and costly to measure, and its own sheen shades them: `hair` would be its share)
export const CAVITY = { r: [.007, .018], k: [2.6, 1.9], max: .42, warm: [1, .9, .86], hair: 0, wet: .4 };
export function cavityShade(geo, C = CAVITY, dark = cavityOf(geo, C)) {
  const col = geo.attributes.color.array, hm = geo.attributes.hairMask?.array, wm = geo.attributes.wetMask?.array;
  for (let i = 0; i < dark.length; i++) {
    const skin = !hm?.[i] && !wm?.[i], d = dark[i] * (hm?.[i] ? C.hair : wm?.[i] ? C.wet : 1);
    for (let q = 0; q < 3; q++) col[i * 3 + q] *= 1 - d * (skin ? 2 - C.warm[q] : 1);
  }
  return geo;
}
// how dark each vertex of a face's geometry is by its hollow (its shape's alone: kept per built face, whatever colours
// it is painted in -- createHeads)
export function cavityOf(geo, C = CAVITY) {
  return cavityArrays(geo.attributes.position.array, geo.attributes.normal.array, geo.attributes.hairMask?.array, C);
}
// HALF-LAMBERT for faces: f = (n . l + 1) / 2 under the world's sun (light.js; `dir` here overrides it -- the viewer's
// sliders), through a RAMP that is the face's own fall-off: `dark` how dark the far side gets (0 none .. 1 black),
// `gamma` its shape (1 straight; higher keeps the lit side bright longer), or `curve` points [f, light] joined by a
// Catmull-Rom spline (overrides dark and gamma). The ramp is a 256-texel strip: any shape costs one lookup.
export const SHADE = { dark: .8, gamma: 1.6, curve: null, skin: null, hair: null };
// THE HAIR'S SHEEN (Kajiya-Kay): hair lit as fibres, not as a surface -- a highlight where the half vector is square to
// the hair's direction, a band round the head across the strands. Two of them, as hair has (Marschner's R and TRT):
// the first white and tight, shifted toward the tip (`shift1`, along the normal), the second broader and the hair's own
// colour, shifted toward the root; `jitter` breaks the shift strand by strand. `exp` their tightness, `s` their strength.
// THE FIBRES: the hair's texture, drawn in the shader along it -- streaks across u (which runs ACROSS the hair: a
// strand's width, round the cap and a sheet) at `freq` a unit and 2.7 times that, wavering a little down the hair,
// `fibre` how strong (0 plain paint); they fade where they would be finer than a pixel, so it never shimmers
export const HAIR_SHEEN = { shift1: -.08, shift2: .12, exp1: 90, exp2: 24, s1: .17, s2: .15, jitter: .25, fibre: .35, freq: 140 };   // (s1, s2 halved: at .35 / .3 it read oily)
export function shadeAt(SH, f) {
  const C = SH.curve;
  if (Array.isArray(C) && C.length >= 2) {
    const P = C.slice().sort((a, b) => a[0] - b[0]);
    if (f <= P[0][0]) return P[0][1];
    if (f >= P[P.length - 1][0]) return P[P.length - 1][1];
    let i = 0; while (i + 1 < P.length - 1 && P[i + 1][0] <= f) i++;
    const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(P.length - 1, i + 2)], t = (f - p1[0]) / Math.max(1e-6, p2[0] - p1[0]);
    // (Catmull-Rom in the light, clamped to the segment's own range so it never overshoots into negative or over 1)
    const v = .5 * (2 * p1[1] + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t * t + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t * t * t);
    return Math.max(Math.min(p1[1], p2[1]), Math.min(Math.max(p1[1], p2[1]), v));
  }
  return 1 - (SH.dark ?? .8) * Math.pow(1 - f, SH.gamma ?? 1.6);
}
const halfLambert = wgslFn(`
  fn halfLambert(n: vec3<f32>, l: vec3<f32>, ramp: texture_2d<f32>, samp: sampler) -> vec3<f32> {
    let f = clamp(dot(normalize(n), l) * 0.5 + 0.5, 0.0, 1.0);
    return vec3<f32>(textureSampleLevel(ramp, samp, vec2<f32>(f, 0.5), 0.0).r);
  }
`);
// the hair's direction is read from the screen: the surface's gradient of v (which runs along the hair: hair.js) out of
// the derivatives of the world position and of v -- so it needs no tangent attribute, and holds under any instance turn
const hairSheen = wgslFn(`
  fn hairSheen(n: vec3<f32>, p: vec3<f32>, tv: vec2<f32>, l: vec3<f32>, cam: vec3<f32>, mask: f32, base0: vec3<f32>, lam: vec3<f32>, k: vec4<f32>, e: vec4<f32>, fb: vec4<f32>) -> vec3<f32> {
    let N = normalize(n);
    // the fibres: value noise across u at two frequencies, wavering down v
    let x = tv.x * fb.y + sin(tv.y * 37.0) * 0.6;
    let fx = fwidth(x);
    let i1 = floor(x); let f1 = fract(x);
    let n1 = mix(fract(sin(i1 * 127.1) * 43758.5453), fract(sin((i1 + 1.0) * 127.1) * 43758.5453), smoothstep(0.0, 1.0, f1));
    let x2 = x * 2.7 + 13.0; let i2 = floor(x2); let f2 = fract(x2);
    let n2 = mix(fract(sin(i2 * 311.7) * 43758.5453), fract(sin((i2 + 1.0) * 311.7) * 43758.5453), smoothstep(0.0, 1.0, f2));
    let fib = 1.0 + fb.x * 2.0 * ((n1 * 0.65 + n2 * 0.35) - 0.5) * clamp(1.5 - fx * 2.0, 0.0, 1.0) * mask;
    let base = base0 * fib;
    let dp1 = dpdx(p); let dp2 = dpdy(p); let dv1 = dpdx(tv.y); let dv2 = dpdy(tv.y);
    var T = cross(dp2, N) * dv1 + cross(N, dp1) * dv2;
    if (dot(T, T) < 1e-20) { T = vec3<f32>(0.0, 1.0, 0.0); }
    T = normalize(T - N * dot(N, T) + vec3<f32>(0.0, 1e-6, 0.0));
    let V = normalize(cam - p); let H = normalize(l + V);
    let j = (fract(sin(tv.x * 1271.1) * 43758.5453) - 0.5) * e.z;
    let T1 = normalize(T + N * (k.x + j)); let T2 = normalize(T + N * (k.y + j));
    let d1 = dot(T1, H); let d2 = dot(T2, H);
    let s1 = pow(sqrt(max(0.0, 1.0 - d1 * d1)), e.x);
    let s2 = pow(sqrt(max(0.0, 1.0 - d2 * d2)), e.y);
    let lit = smoothstep(-0.1, 0.35, dot(N, l));
    return base * lam + (vec3<f32>(s1 * k.z) + base * (s2 * k.w)) * (lit * mask);
  }
`);
// THE WET SHINE: Blinn-Phong under the world's sun, very sharp (a cornea, a tear film), and a rim of the sky's light
// where the surface turns from the eye (the wet edge catching it) -- weighted by the vertex's wetness
const wetShine = wgslFn(`
  fn wetShine(c: vec3<f32>, n: vec3<f32>, p: vec3<f32>, l: vec3<f32>, cam: vec3<f32>, wet: f32) -> vec3<f32> {
    if (wet <= 0.0) { return c; }
    let v = normalize(cam - p);
    let nn = normalize(n);
    let h = normalize(l + v);
    let sp = pow(max(dot(nn, h), 0.0), 160.0) * 1.4 + pow(max(dot(nn, h), 0.0), 24.0) * 0.12;
    let rim = pow(1.0 - max(dot(nn, v), 0.0), 4.0) * 0.18;
    return c + vec3<f32>(1.0, 0.98, 0.95) * (sp + rim) * wet;
  }
`);
export function faceMaterial(shade = SHADE) {
  const SH = { ...SHADE, ...shade }, W = 256, data = new Uint8Array(W * 4);
  for (let i = 0; i < W; i++) { const v = Math.round(255 * Math.max(0, Math.min(1, shadeAt(SH, i / (W - 1))))); data.set([v, v, v, 255], i * 4); }
  const ramp = new THREE.DataTexture(data, W, 1, THREE.RGBAFormat); ramp.magFilter = ramp.minFilter = THREE.LinearFilter; ramp.needsUpdate = true;
  const d = SH.dir ?? LIGHT.dir, dl = Math.hypot(...d) || 1;
  const m = new THREE.MeshBasicNodeMaterial();
  const L = vec3(d[0] / dl, d[1] / dl, d[2] / dl), K = { ...HAIR_SHEEN, ...(SH.hair ?? {}) };
  const lam = halfLambert({ n: normalWorld, l: L, ramp: texture(ramp), samp: texture(ramp) });
  // (the paint is the vertex colour; on the hair -- its mask -- the sheen goes on over it)
  // (SH.base: the paint as a node instead -- bodies.js paints its creatures' patterns over the vertex colour)
  const sheen = hairSheen({ n: normalWorld, p: positionWorld, tv: uv(), l: L, cam: cameraPosition, mask: attribute("hairMask", "float"), base0: SH.base ?? attribute("color", "vec3"), lam,
                            k: vec4(K.shift1, K.shift2, K.s1, K.s2), e: vec4(K.exp1, K.exp2, K.jitter, 0), fb: vec4(K.fibre, K.freq, 0, 0) });
  m.colorNode = wetShine({ c: sheen, n: normalWorld, p: positionWorld, l: L, cam: cameraPosition, wet: attribute("wetMask", "float") });
  m.userData.ramp = ramp;
  m.positionNode = hairSway();
  return m;
}
// HAIR IN THE WIND (2026-10-24): what hangs below the head (a long fall, a plait, two locks) is blown the wind's way
// and flutters back -- by how far below the head's middle it hangs (the geometry's own y: the head's frame), so the
// crown stays put and the tips move most; the flutter runs down the hair and each head has its own (by where it is:
// the batch has already placed the vertex -- positionLocal is the world's here). HAIR_SWAY.amp metres a metre of hang
// in a full wind; with the grass's gusts (grass.js WIND, grassWind)
export const HAIR_SWAY = { amp: .1, from: .02, speed: 2.1, per: 9 };
function hairSway() {
  const H = HAIR_SWAY, hang = positionGeometry.y.negate().sub(H.from).max(0);
  const ph = time.mul(H.speed).add(positionLocal.x.mul(.9)).add(positionLocal.z.mul(.7)).add(positionGeometry.y.mul(H.per));
  const gust = grassWind({ p: positionLocal.xz, t: time }).mul(.25).add(.6).mul(WIND.strength);
  const blow = sin(ph).mul(.45).add(sin(ph.mul(2.3).add(1.7)).mul(.25)).add(.55).mul(gust);
  return positionLocal.add(vec3(WIND_DIR.x, 0, WIND_DIR.y).mul(blow.mul(hang).mul(H.amp).mul(attribute("hairMask", "float"))));
}
// WHAT A HAIRSTYLE ASKS OF THE FACE under it: a tonsure's shaven crown is skin (face.js `bare`: the cap's `top`) --
// the face paints its scalp in the hair's colour above the hairline, so without it the bare crown would read as hair
// ...and what is worn over the hair lies on its cap (jewelry.js headFit: a diadem, a wreath): `hairCap`
export function hairFaceParams(bank, style) {
  const cap = bank.get(style?.startsWith?.("items/") ? style : "items/hair/" + style)?.parts?.find((q) => q.type === "hair")?.cap ?? null;
  return { ...(cap?.top !== undefined ? { bare: cap.top } : {}), hairCap: cap };
}
// shade: the faces' half-Lambert (config.json people.faceShade: dark, gamma or curve, skin) -- one material for all of them
// how finely the game's heads are subdivided (face.js: 0 the guide lattice itself, 1 once -- config.json people.faceDetail)
// (a STATUE's carved head -- `stone` -- its own: seen close and lit hard by the stone's light, once was faceted planes
//  over the cheeks and the jaw)
export const DETAIL = { face: 1, stone: 1.5, far: .7, farStone: 1 };
const detailOf = (s) => (s.far ? (s.stone ? DETAIL.farStone : DETAIL.far) : s.stone ? DETAIL.stone : DETAIL.face);
// FAR HEADS (2026-11-22): a head past FAR.out metres from the eye is drawn from a FAR SHAPE -- the same face, hair and
// jewels at DETAIL.far (face.js: below .75 the guide lattice itself, no subdivision; a woman's 4250 triangles 2012, a
// man's 4014 1776; a statue's carved head at 1 for its 1.5) -- and near again inside FAR.in (the gap: a person standing
// about the line never flickers between the two). Only where the caller says where the eye is (index.html; the viewers
// draw every head near). A far shape is built OFF THE MAIN THREAD (faceworker.js: 25-50 ms a face, which on the main
// thread would be a dropped frame each), or taken from pregen/ like a near one (recordFace records both); until it has
// come the head stays near. Its colourings are made at most FAR.perFrame a frame (paint and index, ~4 ms: the hollows
// and smoothed normals come from the worker). A near shape is exactly what it was: built at startup as before, its key unchanged.
export const FAR = { out: 10, in: 8, perFrame: 1, seeds: SEEDS };
// (what was built and drawn: the far heads' counts and their worker's time, for checks -- index.html's walk scripts)
export const HEAD_STATS = { near: 0, nearMs: 0, far: 0, farMs: 0, farMain: 0, farMainMs: 0, farKinds: 0, farKindMs: 0, drawnNear: 0, drawnFar: 0 };
// A FACE'S SHAPE: everything about it but its size (the copy's scale: hr over the canon's) and its skin's and hair's
// colours (painted on: built in placeholders) -- so pregen/ can keep it, and a village's heads share few builds.
// Its FAMILY: the kind, the hair, what is worn -- another seed of one family stands in for a face pregen/ has not got
// (heads.js is told the generator's faces were drawn at random: which seed of a family a person gets is no matter)
const SKIN0 = "#fe01fd", HAIR0 = "#fd02fe", BROW0 = "#fc03fc", STUB0 = "#fb04fb", LIP0 = "#fa05fa";
// THE LIPS from the skin (2026-10-24): the skin's own colour, darker and ruddier -- a pink picked at random sat on dark
// skin like paint. `tint` how far toward red-brown, `dark` how much darker; the pale skin a little rosier
export const LIPS = { tint: [.62, .3, .3], mix: [.32, .55], dark: .8 };   // (mix: toward the tint on the darkest skin .. the palest)
// (worked in sRGB, as the colours are written: three's Color mixes in linear light, which washed the lips out)
const lipOf = (skin) => {
  const c = new THREE.Color(skin); c.getHSL(_hsl, THREE.SRGBColorSpace);
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(skin.slice(i, i + 2), 16) / 255), tm = .6 + .8 * _hsl.l;
  const k = LIPS.mix[0] + (LIPS.mix[1] - LIPS.mix[0]) * Math.min(1, Math.max(0, (_hsl.l - .25) / .55));
  const out = [r, g, b].map((v, q) => Math.round(Math.max(0, Math.min(1, (v + (LIPS.tint[q] * tm - v) * k) * LIPS.dark)) * 255));
  return "#" + out.map((v) => v.toString(16).padStart(2, "0")).join("");
};
// THE BROWS a shade darker than the hair (a fair head's are, and a face is read by its brows and eyes from metres away:
// fair brows on dark skin, or on pale, all but vanished) -- the hair's colour times this
export const BROW_TONE = .55;
// (grey and white hair keeps its brows grey: an elder's are light, often bushier, not dark)
const _hsl = {};
// (toward a dark warm brown, not darker by a factor: a blond's brows and beard went olive that way)
const BROW_DARK = new THREE.Color("#2b1d14");
const browOf = (hair) => { const c = new THREE.Color(hair); c.getHSL(_hsl, THREE.SRGBColorSpace);   // (as the eye sees it: in linear light a mid grey is .32)
  return "#" + (_hsl.s < .15 && _hsl.l > .4 ? c.multiplyScalar(.88) : c.lerp(BROW_DARK, 1 - BROW_TONE)).getHexString(); };
// STUBBLE: the skin, a third of the way to the brows' colour (face.js BEARDS stubble)
export const STUBBLE = .35;
const stubbleOf = (skin, hair) => "#" + new THREE.Color(skin).lerp(new THREE.Color(browOf(hair)), STUBBLE).getHexString();
// (FAR HEADS: the same face at DETAIL.far -- FAR.seeds of a family: 16, every seed, its own face; fewer would share
//  (a town's 190 shapes are 90 families: half the worker's time) but a face at ten metres, twenty pixels tall, then
//  changed its eyes and jaw as it crossed the line)
export const farShape = (f) => { const s = faceShape(f); return { ...s, seed: s.seed % FAR.seeds, far: 1 }; };
// (no far shape where it would be no lighter: config.json people.faceDetail at or under DETAIL.far)
const hasFar = (s) => detailOf({ ...s, far: 1 }) < detailOf({ ...s, far: 0 });
export const faceShape = (f) => ({ kind: f.kind, seed: f.seed % SEEDS, style: f.style ?? "", fringe: f.fringe ?? 0, stone: f.stone ?? 0, headwear: f.headwear ?? "", ears: f.ears ?? "", ...(f.beard ? { beard: f.beard } : {}), ...(f.full ? { full: f.full } : {}) });
// (its FULLNESS -- `full`, the body's fat in steps: people.js -- is of the family: a fat man's face never stands in for a thin one's)
export const faceFamily = (s) => `${s.kind}|${s.style}|${s.fringe}|${s.stone ? (PAINTED.has(s.stone) ? "p@" : "1@") + DETAIL.stone : 0}|${s.headwear}|${s.ears}${s.beard ? "|" + s.beard : ""}${s.full ? "|f" + s.full : ""}${s.far ? "|far@" + detailOf(s) : ""}`;   // (a carved one at its detail: no other stands in)
// HOW THIS FACE DIFFERS from the others of its kind (assets/items/faces/face.json `variety`, docs/face.md): its seed's place
// on a few AXES that move several attributes together within the kind's own ranges -- a woman's finer or stronger jaw, brow
// and nose at once, never a man's -- then a chin and a nose SHAPE picked by the kind's weights, and the FULLNESS of a stout
// or a lean body's face (s.full) -> the params handed to the face over its definition's own draws
const vrng = (seed) => { let a = (seed >>> 0) || 1; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
export function faceVariety(s, bank) {
  const def = bank.get("items/faces/" + s.kind);
  if (!def || s.stone) return {};   // (a carved head: the sculptor's ideal, as its definition has it)
  const flat = flatten(def, bank), V = flat.variety, P = flat.params ?? {};
  if (!V) return {};
  const k = V.kinds?.[s.kind] ?? 1;
  if (k <= 0) return {};
  const r = vrng((1 + s.seed) * 7907 + [...s.kind].reduce((h, c) => h * 31 + c.charCodeAt(0), 7));
  const bell = () => (r() + r() + r() - 1.5) / 1.5;   // (-1..1, most near 0)
  const z = Object.fromEntries(Object.keys(V.axes ?? {}).map((a) => [a, bell()]));
  const out = {}, base = {};
  // the attributes the kind gives as RANGES: placed in them by the axes (their weights, normalised) and their own share
  for (const [name, v] of Object.entries(P)) {
    if (!(Array.isArray(v) && v.length === 2 && v.every((x) => typeof x === "number"))) continue;
    let s2 = 0, w2 = 0;
    for (const [a, ws] of Object.entries(V.axes ?? {})) if (ws[name] !== undefined) { s2 += ws[name] * z[a]; w2 += ws[name] * ws[name]; }
    const own = bell(), x = w2 > 0 ? (1 - V.own) * s2 / Math.sqrt(w2) + V.own * own : own;
    out[name] = v[0] + (v[1] - v[0]) * Math.max(-.15, Math.min(1.15, .5 + .75 * x));
  }
  for (const [name, v] of Object.entries(P)) if (typeof v === "number") base[name] = v;
  const val = (name) => out[name] ?? base[name] ?? FACE_ATTRS[name] ?? FACE_PARAMS[name] ?? 0;
  const pickOf = (table, weights) => {
    const ks = Object.keys(weights ?? {}).filter((n) => table?.[n]), tot = ks.reduce((t, n) => t + weights[n], 0);
    let x = r() * tot;
    for (const n of ks) if ((x -= weights[n]) < 0) return n;
    return ks[ks.length - 1] ?? null;
  };
  const W = V.weights?.[s.kind] ?? {}, chin = pickOf(V.chins, W.chins), nose = pickOf(V.noses, W.noses);
  const add = (deltas, f = k) => { for (const [n, d] of Object.entries(deltas ?? {})) if (!n.startsWith("_")) out[n] = val(n) + d * f; };
  add(V.chins?.[chin]); add(V.noses?.[nose]); add(V.full?.[s.full ?? 0]);
  return out;
}
// (the definitions a face is made of: its key carries them, so an edited face, hairstyle or jewel is not found)
const contentOf = new WeakMap();
function faceContent(bank) {
  let c = contentOf.get(bank);
  if (!c) {
    const h = hasher().str("face-content");
    for (const [p, d] of [...bank].filter(([p]) => /^items\/(faces|hair|jewelry|flowers\/blooms)\//.test(p) || p === "items/materials").sort((a, b) => (a[0] < b[0] ? -1 : 1))) h.str(p).json(d);
    contentOf.set(bank, c = h.hex());
  }
  return c;
}
export const faceKey = (s, bank, SH) => hasher().str("face").str(faceContent(bank)).json({ ...s, detail: detailOf(s), skin: SH.skin ?? null }).hex();
export function buildFace(s, bank, lib, SH) { const [path, opts] = faceBuild(s, bank, SH); return buildItem(path, bank, lib, opts); }
// (buildItem's arguments for a face, but the bank and the materials: the far heads' worker is handed these)
export const faceBuild = (s, bank, SH) => ["items/faces/" + s.kind, { seed: 1 + s.seed, materials: { skin: SH.skin ?? SKIN0, hairColour: HAIR0, brow: BROW0, stubble: STUB0, lip: LIP0 },
    params: { ...faceVariety(s, bank), detail: detailOf(s), scale: 1, hairline: s.style === "none" ? .2 : HAIRLINE, seed: 1 + s.seed, ...(s.style ? { hairstyle: "items/hair/" + s.style, fringe: s.fringe, ...hairFaceParams(bank, s.style) } : {}), ...(s.stone ? { carved: 1, painted: PAINTED.has(s.stone) ? 1 : 0 } : {}),
              ...(s.headwear ? { headwear: s.headwear } : {}), ...(s.ears ? { earrings: s.ears } : {}), ...(s.beard ? { beard: s.beard } : {}) } }];   // (a beard the person is given -- an outfit's: face.js BEARDS -- over the face's own draw)   // (the person's own hairstyle, else the face's pick; what is worn on the head and the ears: jewelry.js)
// the generator (pregen.html): a person's face built and kept, unless it already is
export function recordFace(f, { bank = ASSETS, lib = bank.get("items/materials")?.materials ?? {}, shade = {} } = {}) {
  const SH = { ...SHADE, ...shade }, s = faceShape(f), key = faceKey(s, bank, SH);
  if (!bank.has("items/faces/" + s.kind)) return false;
  // (and its FAR shape, for the heads past FAR.out: a world without it in pregen/ builds it in the worker)
  const fs = farShape(f), fk = faceKey(fs, bank, SH);
  if (hasFar(s) && !PREGEN.record?.faces.has(fk)) recordFor("faces", fk, { buf: packFace(buildFace(fs, bank, lib, SH)), family: faceFamily(fs), seed: fs.seed });
  if (PREGEN.record?.faces.has(key)) return false;
  recordFor("faces", key, { buf: packFace(buildFace(s, bank, lib, SH)), family: faceFamily(s), seed: s.seed });
  return true;
}
// WHERE A HEAD SITS: on the head part (its two ends: a the cranium's centre, b the jaw end), looking along the gaze
// part (g0 -> g1), at the person's size (hr over the canon's) -- the matrix the head is drawn with (and clipcheck.js
// puts the hair where it is drawn)
const _X = new THREE.Vector3(), _Y = new THREE.Vector3(), _Z = new THREE.Vector3();
export function headMatrix(a, b, g0, g1, rotY, hr, M = new THREE.Matrix4()) {
  _Y.set(a[0] - b[0], a[1] - b[1], a[2] - b[2]).normalize();                              // up the head: from the jaw end to the cranium's centre
  _X.set(g1[0] - g0[0], g1[1] - g0[1], g1[2] - g0[2]); _X.addScaledVector(_Y, -_X.dot(_Y)).normalize();   // where it looks, square to that
  if (_X.lengthSq() < .5) _X.set(Math.cos(rotY), 0, -Math.sin(rotY));
  _Z.crossVectors(_X, _Y);
  const s = (hr ?? CANON_R) / CANON_R;   // (its size: the shape is built at the canon's)
  return M.makeBasis(_X.multiplyScalar(s), _Y.multiplyScalar(s), _Z.multiplyScalar(s)).setPosition(a[0], a[1], a[2]);
}
// A FACE'S GEOMETRY INDEXED: paintedGeometry repeats a vertex in every triangle it is in; each corner is its group's
// vertex `idx[i]`, and everything it carries -- position, normal (smoothed per point), colour, uv, masks, hollow -- is
// that vertex's, so those of one group and one source vertex are one (a far shape: a fifth of the vertices). The far
// heads' pools (FAR HEADS).
export function indexedGeometry(geo, built) {
  const names = Object.keys(geo.attributes), A = names.map((k) => geo.attributes[k]), n = geo.attributes.position.count;
  const index = new Uint32Array(n), first = [];
  let i = 0;
  for (const g of built.groups) {
    const I = g.idx; let top = 0;
    for (let j = 0; j < I.length; j++) if (I[j] > top) top = I[j];
    const of = new Int32Array(top + 1).fill(-1);
    for (let j = 0; j < I.length; j++, i++) { let u = of[I[j]]; if (u < 0) { of[I[j]] = u = first.length; first.push(i); } index[i] = u; }
  }
  if (i !== n) return geo;   // (not laid out as paintedGeometry lays out this face: as it is)
  const out = new THREE.BufferGeometry();
  names.forEach((k, j) => { const a = A[j], s = a.itemSize, arr = new Float32Array(first.length * s);
    for (let u = 0; u < first.length; u++) for (let c = 0; c < s; c++) arr[u * s + c] = a.array[first[u] * s + c];
    out.setAttribute(k, new THREE.Float32BufferAttribute(arr, s)); });
  out.setIndex(new THREE.BufferAttribute(index, 1));
  out.userData = geo.userData;
  return out;
}
export function createHeads(scene, { cap = 48, bank = ASSETS, lib = bank.get("items/materials")?.materials ?? {}, shade = {} } = {}) {
  const SH = { ...SHADE, ...shade }, mat = faceMaterial(SH);   // (one material for every face: the paint is in the vertices)
  const shapes = new Map();  // shape key -> { built } | { pending } | { missing }
  // WHICH CACHED FACE stands in (2026-11-22): its own if pregen/ has it, else another seed of its family -- and the SAME
  // seed for its near and its far shape where the cache has both (the entries say their seed), so a face keeps its jaw
  // and eyes as it crosses FAR.out: its own seed if both forms of it are there, else one of the seeds that are, by its
  // own. (Before, near and far each took the n-th of their own family's list, and the lists need not match.)
  const cachedKey = (f, s, key, fam, idx) => {
    const ns = faceShape(f), fs2 = farShape(f), paired = FAR.seeds === SEEDS && hasFar(ns);
    if (paired && fam?.length) {
      const seedsOf = (k) => new Map((PREGEN.faceFamilies.get(k) ?? []).filter((q) => idx[q]?.seed !== undefined).map((q) => [idx[q].seed, q]));
      const near = seedsOf(faceFamily(ns)), far = seedsOf(faceFamily(fs2)), both = [...near.keys()].filter((q) => far.has(q)).sort((a, b) => a - b);
      if (both.length) { const sd = both.includes(ns.seed) ? ns.seed : both[f.seed % both.length]; return (s.far ? far : near).get(sd); }
    }
    return idx[key] ? key : fam?.length ? fam[f.seed % fam.length] : null;
  };
  const kinds = new Map();   // shape key + colours -> { mesh, n } | null
  // THE SHAPE: from pregen/ (fetched the first time: the head is not drawn for the frames it takes), else built here --
  // a FAR one (FAR HEADS) in the worker, a near one at once
  const shapeOf = (f, far = false) => {
    const s = far ? farShape(f) : faceShape(f), key = faceKey(s, bank, SH);
    let e = shapes.get(key);
    if (e) return e;
    if (!bank.has("items/faces/" + s.kind)) { console.warn(`heads: no face "items/faces/${s.kind}"`); shapes.set(key, e = { missing: true }); return e; }
    if (far && !hasFar(s)) { shapes.set(key, e = { missing: true }); return e; }
    const idx = PREGEN.faceIndex, fam = idx && PREGEN.faceFamilies.get(faceFamily(s));
    const ck = idx ? cachedKey(f, s, key, fam, idx) : null;
    if (ck) {
      shapes.set(key, e = { pending: true, key });
      fetchFace(ck).then((b) => { e.built = b; e.pending = false; }, () => { if (far) farBuild(s, e); else { e.built = buildFace(s, bank, lib, SH); e.pending = false; } });
      return e;
    }
    if (pregenOn()) pregenMiss("face", faceFamily(s), key);
    if (far) { shapes.set(key, e = { pending: true, key }); farBuild(s, e); return e; }
    const t0 = performance.now();
    shapes.set(key, e = { built: buildFace(s, bank, lib, SH), key });
    HEAD_STATS.near++; HEAD_STATS.nearMs += performance.now() - t0;
    if (PREGEN.record) recordFor("faces", key, { buf: packFace(e.built), family: faceFamily(s), seed: s.seed });   // (a world recording keeps it: build/pregen.py)
    return e;
  };
  // THE FAR SHAPES: each handed to the worker (faceworker.js) as soon as it is asked for -- it queues them itself, so a
  // town's are made while the main thread builds the near ones in the first frames, not after; the face's definitions
  // are handed it once. Where there is no worker (or it fails, or the materials are not the bank's own) built here in
  // idle time, one a callback
  const waiting = new Map();   // job id -> [shape, entry]
  let worker = null, jobs = 0, noWorker = lib !== bank.get("items/materials")?.materials || typeof Worker === "undefined";
  const builtFar = (e, b) => { e.built = b; e.pending = false; if (PREGEN.record) recordFor("faces", e.key, { buf: packFace(b), family: e.family, seed: e.seed }); };
  const idleQueue = [];
  const idleBuild = (s, e) => {
    idleQueue.push([s, e]);
    if (idleQueue.length > 1) return;
    const idle = globalThis.requestIdleCallback ?? ((cb) => setTimeout(cb, 50));
    const next = () => idle(() => {
      const [s2, e2] = idleQueue[0], t0 = performance.now();
      try { builtFar(e2, buildFace(s2, bank, lib, SH)); } catch (err) { console.warn("heads: far face failed --", err); e2.pending = false; e2.missing = true; }
      HEAD_STATS.farMain++; HEAD_STATS.farMainMs += performance.now() - t0;
      idleQueue.shift(); if (idleQueue.length) next();
    }, { timeout: 500 });
    next();
  };
  const toMain = () => { noWorker = true; worker?.terminate(); worker = null; const w = [...waiting.values()]; waiting.clear(); for (const [s, e] of w) idleBuild(s, e); };
  const farBuild = (s, e) => {
    e.family = faceFamily(s); e.seed = s.seed;
    if (!noWorker && !worker) {
      try {
        worker = new Worker(new URL("./faceworker.js", import.meta.url), { type: "module" });
        worker.postMessage({ bank: [...bank].filter(([p]) => /^items\/(faces|hair|jewelry|flowers\/blooms)\//.test(p) || p === "items/materials") });
        worker.onmessage = ({ data }) => {
          const job = waiting.get(data.id);
          if (!job) return;
          waiting.delete(data.id);
          const [s2, e2] = job;
          if (data.error) { console.warn("heads: far face in the worker failed, building it here --", data.error.split("\n")[0]); idleBuild(s2, e2); return; }
          const b = unpackFace(data.buf), path = "items/faces/" + s2.kind;
          for (const g of b.groups) Object.defineProperty(g, "src", { value: path });   // (architecture.js itemBudget: by the item it came from)
          cavities.set(b, data.dark); (s2.stone ? carved : smoothed).set(b, data.sm);   // (its hollows and smoothed normals, worked out there)
          builtFar(e2, b); HEAD_STATS.far++; HEAD_STATS.farMs += data.ms; HEAD_STATS.farLast = Math.round(performance.now());
        };
        worker.onerror = (ev) => { console.warn("heads: no far-face worker (" + (ev.message ?? "") + "), building them here"); toMain(); };
      } catch { toMain(); }
    }
    if (noWorker) { idleBuild(s, e); return; }
    const id = ++jobs, [path, opts] = faceBuild(s, bank, SH);
    waiting.set(id, [s, e]);
    worker.postMessage({ id, path, opts, wet: WET, cav: CAVITY, smooth: s.stone ? CARVED_SMOOTH : LIVING_SMOOTH });
  };
  const pools = new Map();   // material -> its batched pool (the faces' one; a statue's stone)
  const poolOf = (m) => { let p = pools.get(m); if (!p) pools.set(m, p = batchPool(scene, m, { name: "heads" })); return p; };
  // (the far heads' own pools: their geometry INDEXED -- a fifth of the vertices -- where the near pool's is not, and a
  //  BatchedMesh takes one or the other; started with room for a town's hundreds of far kinds, so it seldom grows)
  const farPools = new Map();
  const farPoolOf = (m) => { let p = farPools.get(m); if (!p) farPools.set(m, p = batchPool(scene, m, { name: "heads far", copies: 64, verts: 1 << 18, indices: 1 << 20 })); return p; };
  // (a face's kind, kept by the face: its key -- the shape's hash, a JSON of it -- was built anew for every head of every
  //  frame; a face object is replaced, never edited, so once found it stays. Not kept while its shape is still coming.)
  const kindByFace = new WeakMap(), farByFace = new WeakMap();
  const kindOf = (f) => {
    let k = kindByFace.get(f);
    if (!k) { k = findKind(f); if (k) kindByFace.set(f, k); }
    return k;
  };
  // (a far kind: its shape asked of the worker the first time; its colourings made FAR.perFrame a frame -- `farLeft`)
  let farLeft = 0;
  const farKindOf = (f) => {
    let k = farByFace.get(f);
    if (k === undefined) {
      const sh = shapeOf(f, true);
      if (sh.missing) { farByFace.set(f, null); return null; }
      if (sh.pending || farLeft <= 0) return null;
      const t0 = performance.now(), n = kinds.size;
      k = findKind(f, true);
      if (kinds.size > n) { farLeft--; HEAD_STATS.farKinds++; HEAD_STATS.farKindMs += performance.now() - t0; }
      farByFace.set(f, k);
    }
    return k;
  };
  const findKind = (f, far = false) => {
    const sh = shapeOf(f, far);
    if (sh.missing) return null;
    if (sh.pending) return null;
    const painted = !f.stone || PAINTED.has(f.stone);   // (a living face, or a statue's painted: in its own colours)
    const key = `${sh.key}|${painted ? (SH.skin ? "" : f.skin) + "|" + f.hair : ""}`;
    if (kinds.has(key)) return kinds.get(key);
    // (a STATUE's head -- `stone`, its material: statues.js -- is carved: the stone's own material, not skin and hair; its
    //  hollows and its hair's locks cut in)
    const pool = (far ? farPoolOf : poolOf)(f.stone ? stoneMaterial(f.stone, { head: true }) : mat);
    const hs = bank.get("items/hair/" + f.style), curls = hs?.carve === "curls" || !!hs?.parts?.some((q) => q.carved?.carve === "curls");   // (its own, or what it is carved as: hair.js)
    const recolor = painted ? { [SKIN0]: f.skin, [HAIR0]: f.hair, [BROW0]: browOf(f.hair), [STUB0]: stubbleOf(SH.skin ?? f.skin, f.hair), [LIP0]: lipOf(SH.skin ?? f.skin) } : null;
    const geo = f.stone ? stoneFaceGeometry(sh.built, { curls, recolor }) : faceGeometry(sh.built, recolor);
    const k = { pool, shape: pool.add(far ? indexedGeometry(geo, sh.built) : geo), n: 0, far };
    kinds.set(key, k);
    return k;
  };
  const M = new THREE.Matrix4();
  return {
    // herds: every composite herd with people in it, after its update(); each animal with a `face` gets its head --
    // `eye` (the camera's position): those past FAR.out their far shape (FAR HEADS), near again inside FAR.in
    place(herds, eye = null) {
      for (const k of kinds.values()) if (k) k.n = 0;
      for (const p of pools.values()) p.begin();
      for (const p of farPools.values()) p.begin();
      farLeft = FAR.perFrame;
      const o2 = FAR.out * FAR.out, i2 = FAR.in * FAR.in;
      let nn = 0, nf = 0;
      for (const herd of herds) for (const an of herd.animals) {
        const f = an.face;
        if (!f || an.hidden || an._off || an._out) continue;
        let k = kindOf(f);
        if (!k) continue;
        const [a, b] = herd.ends(an, f.head);
        if (eye) {
          const d2 = (a[0] - eye.x) ** 2 + (a[1] - eye.y) ** 2 + (a[2] - eye.z) ** 2;
          an._headFar = an._headFar ? d2 > i2 : d2 > o2;
          if (an._headFar) { const kf = farKindOf(f); if (kf) k = kf; }
        }
        if (k.n >= cap) continue;
        const [g0, g1] = herd.ends(an, f.gaze);
        k.pool.put(k.shape, headMatrix(a, b, g0, g1, an.rotY, f.hr, M)); k.n++;
        if (k.far) nf++; else nn++;
      }
      for (const p of pools.values()) p.end();
      for (const p of farPools.values()) p.end();
      HEAD_STATS.drawnNear = nn; HEAD_STATS.drawnFar = nf;
    },
    dispose() {
      for (const p of [...pools.values(), ...farPools.values()]) p.dispose();
      pools.clear(); farPools.clear();
      mat.userData.ramp.dispose(); mat.dispose();
      kinds.clear();   // (and with them the faces' kinds: this heads object is done)
      worker?.terminate(); worker = null; waiting.clear(); idleQueue.length = 0;
    },
  };
}
