// THE FIGURES' SHARED SHADER PIECES: how a part is packed into the textures, and what is painted on its
// surface -- a garment's cloth, a coat's fur -- in WGSL.
//
// This was the composite engine's own shader file: one quad per figure, every part of it evaluated per pixel,
// the lot joined by a smooth union, with screen cells, a stencil bound, a half-resolution pass and a marched
// 3D pre-pass, all built per configuration (buildComposite) because WGSL has no preprocessor. The figures are
// POLYGONS now (shell.js) and none of that is needed; what survives is the part ENCODING (texelFor, unpackAw,
// sdRoundCone) and the SURFACE (strandsAt, furAt), which the sweep calls with the same numbers the SDF did.
// docs/engines.md has what the rest was and what it cost.
import { wgslFn } from "three/tsl";
import * as LIB from "./banner_wgsl.js";

// RELIEF: what a surface shows in the LIGHT without showing it in the silhouette -- a skirt's pleats, a brow
// ridge, the hollow of an eye socket. Every producer adds the SURFACE (tangential) gradient of its own height
// field, world metres per metre; just before shadeOf the shading tilts the normal by it (n - grad). One field
// per feature: the same numbers darken the colour and tilt the normal, so the two can never drift apart.
// The world's light is deliberately FLAT (shadeOf: a gradient of .23), so an honest slope moves the shade by
// about 1%: every producer states its real depth in metres and RELIEF, shared by all of them, carries it into
// a light this flat. It is the only place the exaggeration lives. (WGSL has no file-scope constants inside a
// wgslFn, so these are repeated as locals where they are used, with the same names and values.)
const FOLD = 0.018, BALL = 0.002, BROWH = 0.004, SOCK = 0.002, RELIEF = 5.0;

// `mod` is GLSL's; WGSL's % is the remainder, which differs for negatives
const fmod = wgslFn(`
  fn fmod(x: f32, y: f32) -> f32 { return x - y * floor(x / y); }
`);

// The 3D round cone (a capsule with two radii): the shape every part of a figure is made of. The near pass
// marches it, and the shell engine (shell.js) pulls its ring vertices onto the smooth union of two of them.
export const sdRoundCone = wgslFn(`
  fn sdRoundCone(p: vec3<f32>, a: vec3<f32>, b: vec3<f32>, r1: f32, r2: f32) -> f32 {
    let ba = b - a;
    let l2 = dot(ba, ba);
    if (l2 < 1e-8) { return length(p - a) - max(r1, r2); }
    let rr = r1 - r2;
    let a2 = l2 - rr * rr;
    let il2 = 1.0 / l2;
    let pa = p - a;
    let y = dot(pa, ba);
    let z = y - l2;
    let w = pa * l2 - ba * y;
    let x2 = dot(w, w);
    let y2 = y * y * l2;
    let z2 = z * z * l2;
    let k = sign(rr) * rr * rr * x2;
    if (sign(z) * a2 * z2 > k) { return sqrt(x2 + z2) * il2 - r2; }
    if (sign(y) * a2 * y2 < k) { return sqrt(x2 + y2) * il2 - r1; }
    return (sqrt(x2 * a2 * il2) + y * rr) * il2 - r1;
  }
`);

// (one node per width: every function that reads a texel includes THIS node, so a shader declares `texel` once)
const texelNodes = new Map();
export const texelFor = (W) => texelNodes.get(W) ?? texelNodes.set(W, wgslFn(`
  fn texel(tex: texture_2d<f32>, i: i32) -> vec4<f32> {
    return textureLoad(tex, vec2<i32>(i % ${W}, i / ${W}), 0);
  }
`)).get(W);

// A.w packs three things: |A.w| = (k in 2mm steps * 2 + needC) * 4 + r1 -- r1 the part's first radius, k its
// blend radius, needC whether its third texel carries anything. Negative: a flat part.
export const unpackAw = wgslFn(`
  fn unpackAw(w: f32) -> vec3<f32> {
    let a = abs(w);
    let q = floor(a / 4.0);
    let r = a - 4.0 * q;
    let f = q - 2.0 * floor(q / 2.0);
    let k = floor(q / 2.0) * 0.002;
    return vec3<f32>(select(r, -r, w < 0.0), k, f);
  }
`);

// a segment with one end behind the near plane (the camera on a mount sits right over the body) is cut there,
// its radius interpolated
const hash2 = wgslFn(`
  fn hash2(q: vec2<f32>) -> f32 { return fract(sin(dot(q, vec2<f32>(127.1, 311.7))) * 43758.5453); }
`);

const vnoise = wgslFn(`
  fn vnoise(q: vec2<f32>) -> f32 {
    let i = floor(q);
    var f = fract(q);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash2(i), hash2(i + vec2<f32>(1.0, 0.0)), f.x),
               mix(hash2(i + vec2<f32>(0.0, 1.0)), hash2(i + vec2<f32>(1.0, 1.0)), f.x), f.y);
  }
`, [hash2]);

// HAIR AND BRAIDS: strands long down a fall of hair, a braid's chevrons (people.js: pattern 16, 15), in two colours
// in the part's own wrapped frame (or the figure's). What people WEAR is not here -- it is the tailor's layers of
// fabric (clothes.js, shell.js dressAt).
export const strandsAt = wgslFn(`
  fn strandsAt(c1: vec3<f32>, c2: vec3<f32>, pat: f32, codeIn: f32, pl: vec3<f32>, bodyFrame: bool,
               pw: vec3<f32>, aw: vec3<f32>, bw: vec3<f32>, r: f32, fq: f32) -> vec3<f32> {
    let sc = fmod(codeIn, 256.0);
    let q = partLocal(pw, aw, bw);                 // x along the axis from A, (y, z) round it
    // ROUND THE PART: the pattern's coordinate is the ANGLE times one radius for the whole part, chosen so a
    // WHOLE NUMBER of the pattern's periods fits the turn -- arc length at each pixel's own radius broke twice
    // at the back (the angle wraps there) and splayed the strands as the radius changed.
    let turns = max(1.0, floor(6.2832 * max(r, 0.02) * max(sc, 1.0) + 0.5));
    let K = turns / (6.2832 * max(sc, 1.0));
    let fz = vec2<f32>(pl.x / fq, pl.z);
    let uv = select(vec2<f32>(atan2(q.z, q.y) * K, -q.x), vec2<f32>(atan2(fz.y, fz.x) * K, pl.y), bodyFrame);
    let u = uv.x;
    let v = uv.y;
    var m = 0.0;
    if (pat > 15.5) {                              // 16 hair: strands, long along the fall
      m = 0.6 * smoothstep(0.3, 0.95, vnoise(vec2<f32>(u * sc, v * sc * 0.07)))
        + 0.25 * smoothstep(0.6, 1.0, vnoise(vec2<f32>(u * sc * 2.3, v * sc * 0.05 + 3.0)));
    } else if (pat > 14.5) {                       // 15 braid: chevrons down the plait
      m = step(0.5, fract(v * sc + abs(fract(u * sc * 0.5) - 0.5) * 1.6));
    }
    return mix(c1, c2, m);
  }
`, [fmod, vnoise, LIB.partLocal]);

// FUR (mammals' coats): short strands lying along the body (the animal frame's x, nose to tail) and down the
// limbs, two stretched value noises over whatever colour or pattern is there; gone once a strand falls under a
// couple of pixels (then not even worked out)
export const furAt = wgslFn(`
  fn furAt(col: vec3<f32>, p: vec3<f32>, patPx: f32) -> vec3<f32> {
    let ACROSS = 55.0;                            // strands ~2cm apart, ~12cm long
    let ALONG = 8.0;
    let detail = 1.0 - smoothstep(0.5, 1.2, patPx * ACROSS);
    if (detail < 0.01) { return col; }
    let n = 0.5 * vnoise(vec2<f32>(p.y * ACROSS, p.x * ALONG)) + 0.5 * vnoise(vec2<f32>(p.z * ACROSS + 7.0, p.x * ALONG + 3.0));
    return col * mix(1.0, 0.86 + 0.24 * n, detail);
  }
`, [vnoise]);
