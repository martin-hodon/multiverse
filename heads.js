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
import { paintedGeometry } from "./tools.js";
import { wgslFn, normalWorld, positionWorld, cameraPosition, attribute, uv, texture, vec3, vec4 } from "three/tsl";
import { LIGHT } from "./light.js";   // the world's one static sun
import { stoneMaterial } from "./shell.js";   // a statue's head: the stone its body is (statues.js)
import { PREGEN, pregenOn, pregenMiss, recordFor, hasher, fetchFace, packFace } from "./pregen.js";   // (heads built once by build/pregen.py)

const CANON_R = .090;   // the canon face's cranium radius (face.js LEVELS): scaled to each person's hr (a little under it: the SDF hair cap covers the skull)
const HAIRLINE = .042;  // the mesh's own hairline, under the cap's: whatever skull shows through the cap shows as hair
const SEEDS = 5;        // how many of a kind and colouring are told apart (their ranges drawn by the seed)

// A BUILT FACE AS ONE GEOMETRY: tools.js paintedGeometry, shaded by faceMaterial in the WORLD's light (light.js) -- the
// lips too: face.js gives every vertex the smooth surface's own normal, so their rolls take the light as the skin does
// WET: the eyes (all but the catchlight, which is the highlight already) and, less, the lips take a sharp specular
export const WET = { eye: 1, iris: 1, pupil: 1, limbus: 1, lip: .3 };
export const faceGeometry = (built, recolor = null) => paintedGeometry(built, { strands: ["hair"], wet: WET, recolor });
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
  const sheen = hairSheen({ n: normalWorld, p: positionWorld, tv: uv(), l: L, cam: cameraPosition, mask: attribute("hairMask", "float"), base0: attribute("color", "vec3"), lam,
                            k: vec4(K.shift1, K.shift2, K.s1, K.s2), e: vec4(K.exp1, K.exp2, K.jitter, 0), fb: vec4(K.fibre, K.freq, 0, 0) });
  m.colorNode = wetShine({ c: sheen, n: normalWorld, p: positionWorld, l: L, cam: cameraPosition, wet: attribute("wetMask", "float") });
  m.userData.ramp = ramp;
  return m;
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
export const DETAIL = { face: 1 };
// A FACE'S SHAPE: everything about it but its size (the copy's scale: hr over the canon's) and its skin's and hair's
// colours (painted on: built in placeholders) -- so pregen/ can keep it, and a village's heads share few builds.
// Its FAMILY: the kind, the hair, what is worn -- another seed of one family stands in for a face pregen/ has not got
// (heads.js is told the generator's faces were drawn at random: which seed of a family a person gets is no matter)
const SKIN0 = "#fe01fd", HAIR0 = "#fd02fe";
export const faceShape = (f) => ({ kind: f.kind, seed: f.seed % SEEDS, style: f.style ?? "", fringe: f.fringe ?? 0, stone: f.stone ?? 0, headwear: f.headwear ?? "", ears: f.ears ?? "" });
export const faceFamily = (s) => `${s.kind}|${s.style}|${s.fringe}|${s.stone ? 1 : 0}|${s.headwear}|${s.ears}`;
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
export const faceKey = (s, bank, SH) => hasher().str("face").str(faceContent(bank)).json({ ...s, detail: DETAIL.face, skin: SH.skin ?? null }).hex();
export function buildFace(s, bank, lib, SH) {
  return buildItem("items/faces/" + s.kind, bank, lib, { seed: 1 + s.seed, materials: { skin: SH.skin ?? SKIN0, hairColour: HAIR0 },
    params: { detail: DETAIL.face, scale: 1, hairline: s.style === "none" ? .2 : HAIRLINE, seed: 1 + s.seed, ...(s.style ? { hairstyle: "items/hair/" + s.style, fringe: s.fringe, ...hairFaceParams(bank, s.style) } : {}),
              ...(s.headwear ? { headwear: s.headwear } : {}), ...(s.ears ? { earrings: s.ears } : {}) } });   // (the person's own hairstyle, else the face's pick; what is worn on the head and the ears: jewelry.js)
}
// the generator (pregen.html): a person's face built and kept, unless it already is
export function recordFace(f, { bank = ASSETS, lib = bank.get("items/materials")?.materials ?? {}, shade = {} } = {}) {
  const SH = { ...SHADE, ...shade }, s = faceShape(f), key = faceKey(s, bank, SH);
  if (!bank.has("items/faces/" + s.kind) || PREGEN.record?.faces.has(key)) return false;
  recordFor("faces", key, { buf: packFace(buildFace(s, bank, lib, SH)), family: faceFamily(s) });
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
export function createHeads(scene, { cap = 48, bank = ASSETS, lib = bank.get("items/materials")?.materials ?? {}, shade = {} } = {}) {
  const SH = { ...SHADE, ...shade }, mat = faceMaterial(SH);   // (one material for every face: the paint is in the vertices)
  const shapes = new Map();  // shape key -> { built } | { pending } | { missing }
  const kinds = new Map();   // shape key + colours -> { mesh, n } | null
  // THE SHAPE: from pregen/ (fetched the first time: the head is not drawn for the frames it takes), else built here
  const shapeOf = (f) => {
    const s = faceShape(f), key = faceKey(s, bank, SH);
    let e = shapes.get(key);
    if (e) return e;
    if (!bank.has("items/faces/" + s.kind)) { console.warn(`heads: no face "items/faces/${s.kind}"`); shapes.set(key, e = { missing: true }); return e; }
    const idx = PREGEN.faceIndex, fam = idx && PREGEN.faceFamilies.get(faceFamily(s));
    const ck = idx?.[key] ? key : fam?.length ? fam[f.seed % fam.length] : null;
    if (ck) {
      shapes.set(key, e = { pending: true, key });
      fetchFace(ck).then((b) => { e.built = b; e.pending = false; }, () => { e.built = buildFace(s, bank, lib, SH); e.pending = false; });
      return e;
    }
    if (pregenOn()) pregenMiss("face", faceFamily(s), key);
    shapes.set(key, e = { built: buildFace(s, bank, lib, SH), key });
    if (PREGEN.record) recordFor("faces", key, { buf: packFace(e.built), family: faceFamily(s) });   // (a world recording keeps it: build/pregen.py)
    return e;
  };
  const pools = new Map();   // material -> its batched pool (the faces' one; a statue's stone)
  const poolOf = (m) => { let p = pools.get(m); if (!p) pools.set(m, p = batchPool(scene, m, { name: "heads" })); return p; };
  const kindOf = (f) => {
    const sh = shapeOf(f);
    if (sh.missing) return null;
    if (sh.pending) return null;
    const key = `${sh.key}|${f.stone ? "" : (SH.skin ? "" : f.skin) + "|" + f.hair}`;
    if (kinds.has(key)) return kinds.get(key);
    // (a STATUE's head -- `stone`, its material: statues.js -- is carved: the stone's own material, not skin and hair)
    const pool = poolOf(f.stone ? stoneMaterial(f.stone) : mat);
    const k = { pool, shape: pool.add(faceGeometry(sh.built, f.stone ? null : { [SKIN0]: f.skin, [HAIR0]: f.hair })), n: 0 };
    kinds.set(key, k);
    return k;
  };
  const M = new THREE.Matrix4();
  return {
    // herds: every composite herd with people in it, after its update(); each animal with a `face` gets its head
    place(herds) {
      for (const k of kinds.values()) if (k) k.n = 0;
      for (const p of pools.values()) p.begin();
      for (const herd of herds) for (const an of herd.animals) {
        const f = an.face;
        if (!f || an.hidden || an._off || an._out) continue;
        const k = kindOf(f);
        if (!k || k.n >= cap) continue;
        const [a, b] = herd.ends(an, f.head), [g0, g1] = herd.ends(an, f.gaze);
        k.pool.put(k.shape, headMatrix(a, b, g0, g1, an.rotY, f.hr, M)); k.n++;
      }
      for (const p of pools.values()) p.end();
    },
    dispose() {
      for (const p of pools.values()) p.dispose();
      pools.clear();
      mat.userData.ramp.dispose(); mat.dispose();
      kinds.clear();
    },
  };
}
