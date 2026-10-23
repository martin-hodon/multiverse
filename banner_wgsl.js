// The shared SDF library in WGSL -- the twin of banner.js's SDF_GLSL, and the foundation of the WebGPU port.
// Every engine (instanced.js, composite.js, architecture.js) builds its shaders from these pieces, so the
// silhouette, the exact surface and the patterns cannot drift apart between them.
//
// Three rules learned the hard way, all of them in docs/webgpu.md:
//   * a wgslFn exposes only the FIRST function of its source -- so every function here is its own wgslFn, and
//     its dependencies are declared as includes (which DO nest: a caller lists only what it calls directly);
//   * WebGPU clip space runs z from 0 to 1, so a depth is c.z / c.w with none of GL's * 0.5 + 0.5;
//   * the maths is ported line for line. "Roughly equivalent" cost a day: every ray missed its solid and nine
//     animals rendered as nine flat cards.
//
// GLSL habits that do not survive the crossing, for whoever ports the next file: there is no implicit int to
// float (write f32(i)), no `mod` (x - y * floor(x / y)), no ternary (select(ifFalse, ifTrue, cond)), atan(y,x)
// is atan2(y, x), and a global like GLSL's gPatPx cannot exist -- it becomes a parameter.
import * as THREE from "three";
import { wgslFn, uniform } from "three/tsl";
import { lightWGSL } from "./light.js";   // the world's one static sun (config.json light)
import { OUTLINE, OUTLINE_COLOR, QUADS } from "./outline.js";

// The switches every banner engine shares, as node uniforms. They mirror the plain {value} objects the rest of
// the app already sets rather than inventing a second source of truth; each engine calls syncBannerUniforms()
// from its onBeforeRender, passing the grass mask (which cannot be imported here: grass.js imports
// composite.js, and composite.js imports this file).
export const U = {
  outline: uniform(0),                                   // 0 = flat fills, 1 = a one-pixel dark silhouette band
  quads: uniform(0),                                     // the geometry view (outline.js QUADS): the card itself, where the shape is not
  mask: uniform(0),                                      // the grass mask pass (grass.js MASK_MODE)
  border: uniform(new THREE.Color(OUTLINE_COLOR)),
};

export function syncBannerUniforms(maskMode) {
  U.outline.value = OUTLINE.value;
  U.quads.value = QUADS.value;
  U.mask.value = maskMode.value;
}

// ---------------------------------------------------------------- silhouettes

// 2D uneven capsule (iq): distance to the hull of two circles (pa,ra),(pb,rb)
export const sdUnevenCapsule = wgslFn(`
  fn sdUnevenCapsule(p: vec2<f32>, pa: vec2<f32>, pb: vec2<f32>, ra: f32, rb: f32) -> f32 {
    let d = pb - pa;
    let h = length(d);
    if (h < 1e-5) { return length(p - pa) - max(ra, rb); }
    let u = d / h;
    let q = vec2<f32>(abs(dot(p - pa, vec2<f32>(-u.y, u.x))), dot(p - pa, u));
    let b = clamp((ra - rb) / h, -0.999, 0.999);
    let a = sqrt(1.0 - b * b);
    let k = dot(q, vec2<f32>(-b, a));
    if (k < 0.0) { return length(q) - ra; }
    if (k > a * h) { return length(q - vec2<f32>(0.0, h)) - rb; }
    return dot(q, vec2<f32>(a, b)) - ra;
  }
`);

// signed distance to a 2D triangle (iq) -- the "tri" banner shape: flat membrane skins (bat wings) that no
// capsule silhouette can fake
export const sdTri = wgslFn(`
  fn sdTri(p: vec2<f32>, p0: vec2<f32>, p1: vec2<f32>, p2: vec2<f32>) -> f32 {
    let e0 = p1 - p0; let e1 = p2 - p1; let e2 = p0 - p2;
    let v0 = p - p0; let v1 = p - p1; let v2 = p - p2;
    let pq0 = v0 - e0 * clamp(dot(v0, e0) / dot(e0, e0), 0.0, 1.0);
    let pq1 = v1 - e1 * clamp(dot(v1, e1) / dot(e1, e1), 0.0, 1.0);
    let pq2 = v2 - e2 * clamp(dot(v2, e2) / dot(e2, e2), 0.0, 1.0);
    let s = sign(e0.x * e2.y - e0.y * e2.x);
    let d = min(min(vec2<f32>(dot(pq0, pq0), s * (v0.x * e0.y - v0.y * e0.x)),
                    vec2<f32>(dot(pq1, pq1), s * (v1.x * e1.y - v1.y * e1.x))),
                vec2<f32>(dot(pq2, pq2), s * (v2.x * e2.y - v2.y * e2.x)));
    return -sqrt(d.x) * sign(d.y);
  }
`);

// ---------------------------------------------------------------- depth

// The depth-buffer value of a view-space point through the camera's projection P -- in full, not the
// plain-perspective shortcut, so a mirror's camera (an oblique projection) puts the SDF figures at the same
// depths as the meshes around them. -1 where the point lies before the near plane: the caller discards it.
// WebGPU's clip space already runs 0..1, so there is no remapping here -- unlike the GLSL twin.
export const viewDepth = wgslFn(`
  fn viewDepth(P: mat4x4<f32>, pv: vec3<f32>) -> f32 {
    let c = P * vec4<f32>(pv, 1.0);
    let z = c.z / c.w;
    if (z < 0.0) { return -1.0; }
    return z;
  }
`);

// ---------------------------------------------------------------- tubes

// a quadratic Bezier centreline a -> (control c) -> b whose radius runs from r1 (at a) to r2 (at b) with a
// bulge in the middle. The radius slot of b packs -2 - (r2 in mm + 4096 * bulge in mm); a triangle's is -1.
export const tubeUnpack = wgslFn(`
  fn tubeUnpack(bw: f32) -> vec2<f32> {
    let v = -bw - 2.0;
    let bu = floor(v / 4096.0 + 1e-4);
    return vec2<f32>(v - bu * 4096.0, bu) * 0.001;
  }
`);

export const tubeR = wgslFn(`
  fn tubeR(t: f32, r1: f32, rb: vec2<f32>) -> f32 {
    return mix(r1, rb.x, t) + rb.y * 4.0 * t * (1.0 - t);
  }
`);

export const bezier3 = wgslFn(`
  fn bezier3(a: vec3<f32>, c: vec3<f32>, b: vec3<f32>, t: f32) -> vec3<f32> {
    let s = 1.0 - t;
    return s * s * a + 2.0 * s * t * c + t * t * b;
  }
`);

export const bezier2 = wgslFn(`
  fn bezier2(a: vec2<f32>, c: vec2<f32>, b: vec2<f32>, t: f32) -> vec2<f32> {
    let s = 1.0 - t;
    return s * s * a + 2.0 * s * t * c + t * t * b;
  }
`);

// the parameter of the point of a 2D quadratic Bezier (A, control B, C) nearest to p (iq's sdBezier cubic);
// a straight one (control at the middle) by plain projection
export const bezierT = wgslFn(`
  fn bezierT(p: vec2<f32>, A: vec2<f32>, B: vec2<f32>, C: vec2<f32>) -> f32 {
    let a = B - A; let b = A - 2.0 * B + C; let c = a * 2.0; let d = A - p; let ac = C - A;
    let L2 = max(dot(ac, ac), 1e-12);
    if (dot(b, b) < 1e-5 * L2) { return clamp(dot(p - A, ac) / L2, 0.0, 1.0); }
    let kk = 1.0 / dot(b, b);
    let kx = kk * dot(a, b);
    let ky = kk * (2.0 * dot(a, a) + dot(d, b)) / 3.0;
    let kz = kk * dot(d, a);
    let pp = ky - kx * kx;
    let q = kx * (2.0 * kx * kx - 3.0 * ky) + kz;
    var h = q * q + 4.0 * pp * pp * pp;
    if (h >= 0.0) {
      h = sqrt(h);
      let x = (vec2<f32>(h, -h) - q) / 2.0;
      let uv = sign(x) * pow(abs(x), vec2<f32>(1.0 / 3.0));
      return clamp(uv.x + uv.y - kx, 0.0, 1.0);
    }
    let z = sqrt(-pp);
    let v = acos(q / (pp * z * 2.0)) / 3.0;
    let m = cos(v);
    let n = sin(v) * 1.732050808;
    let tt = clamp(vec2<f32>(m + m, -n - m) * z - kx, vec2<f32>(0.0), vec2<f32>(1.0));
    let q0 = d + (c + b * tt.x) * tt.x;
    let q1 = d + (c + b * tt.y) * tt.y;
    return select(tt.y, tt.x, dot(q0, q0) < dot(q1, q1));
  }
`);

// ---------------------------------------------------------------- cell grids

// distance to the nearest border of a jittered 3D voronoi grid: large in a cell's interior, ~0 on the seams --
// thresholded, that is the giraffe's coat
export const cellBorder3 = wgslFn(`
  fn cellBorder3(p: vec3<f32>) -> f32 {
    let g = floor(p); let f = fract(p);
    var s1 = 8.0; var s2 = 8.0;
    for (var i: i32 = -1; i <= 1; i = i + 1) {
      for (var j: i32 = -1; j <= 1; j = j + 1) {
        for (var k: i32 = -1; k <= 1; k = k + 1) {
          let o = vec3<f32>(f32(i), f32(j), f32(k));
          let h = fract(sin(vec3<f32>(dot(g + o, vec3<f32>(127.1, 311.7, 74.7)),
                                      dot(g + o, vec3<f32>(269.5, 183.3, 246.1)),
                                      dot(g + o, vec3<f32>(113.5, 271.9, 124.6)))) * 43758.55);
          let dd = length(o + 0.1 + h * 0.8 - f);
          if (dd < s1) { s2 = s1; s1 = dd; } else { s2 = min(s2, dd); }
        }
      }
    }
    return s2 - s1;
  }
`);

// the same grid for reptile scales: x = distance to the nearest seam, y = the nearest cell's own random tone
// (0..1), z = distance to that cell's middle
export const scaleCells3 = wgslFn(`
  fn scaleCells3(p: vec3<f32>) -> vec3<f32> {
    let g = floor(p); let f = fract(p);
    var s1 = 8.0; var s2 = 8.0; var id = 0.0;
    for (var i: i32 = -1; i <= 1; i = i + 1) {
      for (var j: i32 = -1; j <= 1; j = j + 1) {
        for (var k: i32 = -1; k <= 1; k = k + 1) {
          let o = vec3<f32>(f32(i), f32(j), f32(k));
          let h = fract(sin(vec3<f32>(dot(g + o, vec3<f32>(127.1, 311.7, 74.7)),
                                      dot(g + o, vec3<f32>(269.5, 183.3, 246.1)),
                                      dot(g + o, vec3<f32>(113.5, 271.9, 124.6)))) * 43758.55);
          let dd = length(o + 0.1 + h * 0.8 - f);
          if (dd < s1) { s2 = s1; s1 = dd; id = h.x; } else { s2 = min(s2, dd); }
        }
      }
    }
    return vec3<f32>(s2 - s1, id, s1);
  }
`);

// ---------------------------------------------------------------- the exact surface

// The 2D silhouette says which pixels a part covers; for depth and texturing the pixel's view ray is
// intersected with the real 3D primitive -- a round cone from a (radius ra) to b (radius rb), a capsule when
// the radii match, a sphere when a = b (iq). The ray starts at the camera, the view-space origin. One
// closed-form hit per covering part, no marching; -1 where the flattened silhouette overhangs the solid.
export const hitCone = wgslFn(`
  fn hitCone(rd: vec3<f32>, a: vec3<f32>, b: vec3<f32>, ra: f32, rb: f32) -> f32 {
    let ba = b - a; let oa = -a; let ob = -b;
    let m0 = dot(ba, ba);
    if (m0 < 1e-8) {
      let bq = dot(oa, rd); let c = dot(oa, oa) - ra * ra; let hs = bq * bq - c;
      if (hs < 0.0) { return -1.0; }
      return -bq - sqrt(hs);
    }
    let rr = ra - rb;
    let m1 = dot(ba, oa); let m2 = dot(ba, rd); let m3 = dot(rd, oa);
    let m5 = dot(oa, oa); let m6 = dot(ob, rd); let m7 = dot(ob, ob);
    let d2 = m0 - rr * rr;
    let k2 = d2 - m2 * m2;
    let k1 = d2 * m3 - m1 * m2 + m2 * rr * ra;
    let k0 = d2 * m5 - m1 * m1 + m1 * rr * ra * 2.0 - m0 * ra * ra;
    let h = k1 * k1 - k0 * k2;
    if (h < 0.0) { return -1.0; }
    if (abs(k2) > 1e-9) {
      let t = (-sqrt(h) - k1) / k2;
      let y = m1 - ra * rr + t * m2;
      if (y > 0.0 && y < d2) { return t; }     // the barrel
    }
    let h1 = m3 * m3 - m5 + ra * ra;           // the end caps
    let h2 = m6 * m6 - m7 + rb * rb;
    var r = 1e20;
    if (h1 > 0.0) { r = -m3 - sqrt(h1); }
    if (h2 > 0.0) { r = min(r, -m6 - sqrt(h2)); }
    if (r < 1e19) { return r; }
    return -1.0;
  }
`);

// Where the flattened silhouette overhangs the solid by a sliver the ray misses; the surface there is the limb
// of the primitive, at the depth of the ray's closest approach to its axis. Using it keeps a part's rim at the
// same depth as the pixels beside it, so a nearer part never loses its own edge to a farther one.
export const approachT = wgslFn(`
  fn approachT(rd: vec3<f32>, a: vec3<f32>, b: vec3<f32>) -> f32 {
    let ba = b - a;
    let m0 = dot(ba, ba); let m2 = dot(ba, rd); let m1 = dot(ba, a); let m3 = dot(rd, a);
    let den = m2 * m2 - m0;
    var s = 0.5;
    if (abs(den) > 1e-8) { s = clamp((m1 - m2 * m3) / den, 0.0, 1.0); }
    return max(m3 + m2 * s, 0.05);
  }
`);

// the surface along the ray: the exact hit, else the limb
export const surfaceT = wgslFn(`
  fn surfaceT(rd: vec3<f32>, a: vec3<f32>, b: vec3<f32>, ra: f32, rb: f32) -> f32 {
    let t = hitCone(rd, a, b, ra, rb);
    return select(approachT(rd, a, b), t, t > 0.0);
  }
`, [hitCone, approachT]);

// ---------------------------------------------------------------- shading

// SHADING without lights: brightness from the world-space normal alone (light.js: Lambert under the one static
// sun, an ambient floor), so a back reads lighter than a belly and a flank than a chest, and animals sit in the
// same light as the town.
export const shadeOf = wgslFn(`
  fn shadeOf(n: vec3<f32>) -> f32 { return ${lightWGSL("n")}; }
`);

export const capsuleNormal = wgslFn(`
  fn capsuleNormal(p: vec3<f32>, a: vec3<f32>, b: vec3<f32>) -> vec3<f32> {
    let ba = b - a;
    let l2 = max(dot(ba, ba), 1e-8);
    let s = clamp(dot(p - a, ba) / l2, 0.0, 1.0);
    let n = p - (a + ba * s);
    let l = length(n);
    if (l > 1e-5) { return n / l; }
    return vec3<f32>(0.0, 1.0, 0.0);
  }
`);

export const triNormal = wgslFn(`
  fn triNormal(A: vec3<f32>, B: vec3<f32>, C: vec3<f32>, toward: vec3<f32>) -> vec3<f32> {
    let n = normalize(cross(B - A, C - A));
    return select(n, -n, dot(n, toward) > 0.0);     // facing the viewer
  }
`);

// ---------------------------------------------------------------- solid textures

// Every pattern is a function of a 3D point in metres in the part's own frame, never of the screen plane -- so
// stripes keep their spacing from any angle and stay glued to the body. A part's frame: x along the segment
// from A, y up-ish, z sideways.
export const partLocal = wgslFn(`
  fn partLocal(pw: vec3<f32>, A: vec3<f32>, B: vec3<f32>) -> vec3<f32> {
    let d = B - A;
    let l = length(d);
    var u = vec3<f32>(1.0, 0.0, 0.0);
    if (l > 1e-4) { u = d / l; }
    var axis = vec3<f32>(0.0, 1.0, 0.0);        // not named ref: that is a reserved word in WGSL
    if (abs(u.y) > 0.9) { axis = vec3<f32>(1.0, 0.0, 0.0); }
    let w = normalize(cross(axis, u));
    let v = cross(u, w);
    let q = pw - A;
    return vec3<f32>(dot(q, u), dot(q, v), dot(q, w));
  }
`);

// BARK RELIEF (parallax on trunks and boughs) at s = (metres along the axis, metres round it) on a part of
// radius r; 1 the bark's face, 0 its deepest. 2 furrowed: ridges running up the trunk, wavering, parted into
// plates (oak, pine, most trees); 20 ringed: lenticels, short grooves across it (birch, cherry). Both repeat a
// whole number of times round the trunk, so there is no seam where the unwrap closes.
export const barkHeight = wgslFn(`
  fn barkHeight(pat: f32, s: vec2<f32>, r: f32) -> f32 {
    let C = 6.2832 * max(r, 0.01);
    if (pat > 19.5) {
      let row = floor(s.x / 0.035);
      let fv = fract(s.x / 0.035) - 0.5;
      let n = max(3.0, floor(C / 0.06 + 0.5));
      let dash = step(0.45, fract(s.y / C * n + row * 0.37 + 0.1 * sin(row * 3.1)));
      return 1.0 - 0.8 * smoothstep(0.2, 0.07, abs(fv)) * dash;
    }
    let n = max(3.0, floor(C / clamp(r * 0.5, 0.025, 0.09) + 0.5));
    let w = C / n;
    let c = s.y / w + 0.35 * sin(s.x / w * 0.45);
    let fu = fract(c);
    let cid = floor(c) - n * floor(floor(c) / n);        // mod(floor(c), n)
    let ridge = smoothstep(0.0, 0.3, fu) * smoothstep(1.0, 0.7, fu);
    let plate = smoothstep(0.0, 0.08, fract(s.x / (w * 3.0) + fract(sin(cid * 12.9898) * 437.585)));
    return 0.15 + 0.85 * ridge * (0.7 + 0.3 * plate);
  }
`);

// The pattern at local point p; r = the part's radius (mottles scale with it). patPx is the pattern's pixel
// size in metres at the surface (0 = no fade, as in a vertex shader, which has no derivatives) and patAx how
// squarely the surface faces along the frame's x axis -- GLSL passed these as globals, which WGSL has not got.
//   1 leaf mottle, 2 bark streaks, 3 wavy tiger stripes, 4 straight zebra bands, 5 giraffe patches, (22 piebald: below)
//   6 butterfly wing spots, 7 turtle scutes, 8 beaver-tail diamonds, 17 reptile scales, 18 leopard rosettes,
//   19 twist (a horn's spiral ridges), 20 ringed bark
// A SCREW'S PITCH: how many of the part's own radii one turn of the twist pattern takes. The shell engine
// reads it too (shell.js builds the ridge as shape); one number, so the two can never drift apart.
export const TWIST_PITCH = 8;
export const patternAt = wgslFn(`
  fn patternAt(col: vec3<f32>, pat: f32, p: vec3<f32>, r: f32, patPx: f32, patAx: f32) -> vec3<f32> {
    if (pat > 21.5) {          // 22 PIEBALD (a cow's): large irregular dark blotches on a pale coat -- two octaves of
      // value noise over the coat's own frame, cut at a soft threshold, so the patches run on over rump, belly
      // and neck and are paint, not lumps (they were two ellipsoids once, and stood out of the flank)
      var nsum = 0.0;
      var amp = 0.65;
      var q3 = p / 0.34 + vec3<f32>(3.1, 7.7, 1.9);
      for (var o: i32 = 0; o < 2; o = o + 1) {
        let gi = floor(q3); var fq = fract(q3); fq = fq * fq * (3.0 - 2.0 * fq);
        var c8 = array<f32, 8>();
        for (var c: i32 = 0; c < 8; c = c + 1) {
          let off = vec3<f32>(f32(c & 1), f32((c >> 1) & 1), f32((c >> 2) & 1));
          c8[c] = fract(sin(dot(gi + off, vec3<f32>(127.1, 311.7, 74.7))) * 43758.55);
        }
        let x0 = mix(mix(c8[0], c8[1], fq.x), mix(c8[2], c8[3], fq.x), fq.y);
        let x1 = mix(mix(c8[4], c8[5], fq.x), mix(c8[6], c8[7], fq.x), fq.y);
        nsum = nsum + amp * mix(x0, x1, fq.z);
        amp = amp * 0.35;
        q3 = q3 * 2.3 + vec3<f32>(5.2, 1.3, 8.7);
      }
      let soft = clamp(patPx * 3.0, 0.02, 0.12);
      return mix(col, vec3<f32>(0.13, 0.1, 0.08), smoothstep(0.52 - soft, 0.52 + soft, nsum) * 0.95);
    }
    if (pat > 20.5) {          // 21 SPOTS ON A COAT (a leopard's): the giraffe's cells, but only each cell's
      // CORE is painted. Rosettes drawn as rings read as noise on a cat this size -- at any distance where the
      // ring itself is a pixel or two, the eye gets speckle -- so the shape is a filled cell, which holds all
      // the way out. Taking the whole cell, though, leaves a dark coat with thin pale veins: the cat's own
      // tawny is the COAT and the spots are the small dark thing on it, so the paint starts well inside each
      // cell (cb is the distance to its border) and the yellow between them is the animal's own colour.
      let cb = cellBorder3(p / 0.065);
      return mix(col, vec3<f32>(0.07, 0.05, 0.03), smoothstep(0.30, 0.44, cb) * 0.95);
    }
    if (pat > 19.5) {          // 20 RINGED BARK (birch, cherry): its lenticels dark -- short dashes across the axis
      return col * (0.55 + 0.45 * barkHeight(20.0, vec2<f32>(p.x, atan2(p.z, p.y) * r), r));
    }
    if (pat > 18.5) {          // 19 TWIST: ridges spiralling round the part's own axis (a screw) -- a horn's
      // (the SHELL engine turns the same phase into geometry, so the ridge the light draws and the ridge the
      //  silhouette shows are one ridge: TWIST_PITCH is shared, never copied)
      let ph = p.x / max(${TWIST_PITCH}.0 * r, 0.01) + atan2(p.z, p.y) / 6.2832;
      let rid = abs(fract(ph) - 0.5) * 2.0;
      // two-sided: a ridge CATCHES the light as well as its groove loses it, so it reads on a near-black horn
      return col * (0.62 + 0.68 * smoothstep(0.15, 0.7, rid));
    }
    if (pat > 17.5) {          // 18 ROSETTES: a leopard's -- laid out on the coat's own surface, not in space
      var s = vec2<f32>(p.x, atan2(p.z, p.y) * length(p.yz)) / 0.06;
      s.x = s.x + 0.5 * (floor(s.y) - 2.0 * floor(floor(s.y) / 2.0));      // alternate rows staggered
      let g = floor(s);
      let h = fract(sin(vec2<f32>(dot(g, vec2<f32>(127.1, 311.7)), dot(g, vec2<f32>(269.5, 183.3)))) * 43758.55);
      let d = length(s - (g + 0.5 + (h - 0.5) * 0.3));
      let ring = smoothstep(0.15, 0.19, d) * (1.0 - smoothstep(0.29, 0.33, d));
      let blob = step(0.38, scaleCells3(vec3<f32>(s * 2.4, 11.0)).y);
      let detail = (1.0 - smoothstep(0.35, 0.8, patPx / 0.06)) * (1.0 - smoothstep(0.6, 0.8, patAx));
      let inner = mix(col, col * vec3<f32>(0.9, 0.82, 0.72), 1.0 - smoothstep(0.13, 0.16, d));
      return mix(col, mix(inner, vec3<f32>(0.08, 0.06, 0.05), ring * blob * 0.92), detail);
    }
    if (pat > 16.5) {          // 17 SCALES (the dinosaurs): each a small dome, a dark seam round it, its own tone
      let sz = clamp(r * 0.07, 0.012, 0.05);
      let q = p / sz;
      let blot = sin(p.x * 2.1 + sin(p.z * 3.3)) * sin(p.y * 2.7 + p.z * 1.9);
      var c = scaleCells3(q);
      if (blot > 0.45) { c = scaleCells3(q * 0.6 + 17.0); }
      let dome = 1.12 - 0.42 * smoothstep(0.05, 0.55, c.z);
      let seam = mix(0.55, 1.0, smoothstep(0.01, 0.07, c.x));
      let tone = 0.86 + 0.26 * c.y;
      let base = col * (1.0 + 0.14 * blot);
      let detail = 1.0 - smoothstep(0.35, 0.8, patPx / sz);
      return mix(base * 0.86, base * tone * dome * seam, detail);
    }
    if (pat > 8.5) { return col; }                      // cloth patterns: the composite engine's clothAt
    if (pat > 7.5) {                                    // 8 beaver-tail diamonds
      let m = max(step(0.4, abs(fract((p.x + p.y) / 0.025) - 0.5)),
                  step(0.4, abs(fract((p.x - p.y) / 0.025) - 0.5)));
      return mix(col, vec3<f32>(0.03, 0.02, 0.02), m * 0.85);
    }
    if (pat > 6.5) {                                    // 7 turtle scutes
      return col * mix(0.5, 1.0, smoothstep(0.05, 0.16, cellBorder3(p / 0.055)));
    }
    if (pat > 5.5) {                                    // 6 butterfly wing spots
      let sp = fract(p.xy / 0.05) - 0.5;
      return mix(col, vec3<f32>(0.07, 0.05, 0.05), smoothstep(0.34, 0.2, length(sp)) * 0.85);
    }
    if (pat > 4.5) {                                    // 5 giraffe patches
      return mix(col, vec3<f32>(0.36, 0.19, 0.07), smoothstep(0.07, 0.15, cellBorder3(p / 0.5)) * 0.93);
    }
    if (pat > 2.5) {
      // 3/4 stripes across the axis (vertical on a body, rings on a leg), ~18cm apart; the tiger's wander with
      // height and depth, the zebra's run straight
      var wig = 0.0;
      if (pat < 3.5) { wig = sin(p.y * 9.0) * 0.6 + sin(p.z * 7.0) * 0.3; }
      return mix(col, vec3<f32>(0.045, 0.04, 0.04), smoothstep(0.45, 0.7, sin(p.x * 35.0 + wig)) * 0.96);
    }
    let q = p / max(r, 0.05);
    var m = smoothstep(0.2, 0.65, sin(q.x * 12.7 + 1.3) * sin(q.y * 13.9 + q.z * 7.1));        // 1 leaf mottle
    if (pat > 1.5) {                                    // 2 bark streaks along the axis, wavering round it
      m = smoothstep(0.55, 0.8, fract(q.x * 1.4 + 0.3 * sin(atan2(q.z, q.y) * 2.0)));
    }
    return col * (1.0 - m * 0.12);
  }
`, [barkHeight, cellBorder3, scaleCells3]);
