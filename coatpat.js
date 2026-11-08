// THE COATS OF THE SCULPTED BODIES (2026-11-04): the patterns bodies.js paints per pixel over a sculpted creature's
// vertex colour -- a tiger's stripes, a zebra's, a leopard's rosettes, a giraffe's patches, a feather's vane and a
// peacock's eye -- written for the sculpted path only (the composite's own patternAt, banner_wgsl.js, still paints the
// shells, ?sculpt=0, and every other pattern here: scales, scutes, bark, piebald...).
//
// What a pattern is given (bodymesh.js lays it): p, the point in its shape's pattern FRAME (x along the frame's axis, y
// toward its `v` -- the spine on a trunk laid in the animal's frame, the OUTSIDE of a limb, the face of a head given a
// frame of its own -- z across), and r its shape's radius; both divided by the body's PATTERN SCALE (body.patScale: its
// trunk's girth against a tiger's, or as the definition says), so the numbers below are a tiger's and a leopard's
// rosettes come out a leopard's. The solid patterns (rosettes, spots, giraffe) take p as the rest pose's own space.
// px: the pixel's footprint in those same units -- what every edge is antialiased by, and what fades a pattern finer
// than the pixels into its average (no shimmer at a distance).
//   3 STRIPES (a tiger's): bands across the axis, wandering, each its own width, tapering to a point as it runs down
//     the flank from the spine (or round a leg from its outside), some FORKED below halfway, some DOUBLED by a thin
//     companion, some broken; on a thin part (a tail) they close into rings
//   4 BANDS (a zebra's): the same, broad, even and closing all the way round
//   5 PATCHES (a giraffe's): warped cells, each its own tone, parted by a thin pale network
//   18 ROSETTES (a leopard's): broken rings of dark blotches round a centre darker than the ground, a few solid spots
//     between; on a small part (head, legs, tail) small solid spots instead
//   21 SPOTS: solid, irregular, scattered (a cheetah's, a leopard's head)
//   22 PIEBALD (a cow's): the composite's blotches, laid near black
//   24 TABBY (a house cat's): 3's stripes, darkened from the coat itself, so a ginger cat's stay ginger
//   25 OSTEODERMS (a carnotaur's): the reptile scales with rows of big domed feature scales over the upper body
//   26-31 THE SEA'S (a lionfish's maroon bands, a pike's pale spots, a trout's, an octopus's mottle and suckers, a
//     clownfish's bars): below, before coatAt
//   32 ROW SCALES (a carp's): overlapping scales in staggered rows along the body; 33 FIN RAYS: below, before coatAt
//   36 SHAG (an ape's long hair: locks along the shape's axis), 37 AGOUTI (ticked fur, salt and pepper): below, before coatAt
//   23 FEATHER (bodymesh.js featherMesh): p = (metres along it, metres across from its shaft, its length, its half
//     width), q = (bars, the bars' darkness, where its eye is along it, the eye's size against its width) -- the barbs,
//     the pale rachis, the bars, and the OCELLUS: a peacock's eye, a kidney of deep blue-violet in a turquoise ring, in
//     bronze, in gold-green, in a thin dark rim
import { wgslFn } from "three/tsl";
import { patternAt } from "./banner_wgsl.js";

const hash33 = wgslFn(`
  fn hash33(c: vec3<f32>) -> vec3<f32> {
    return fract(sin(vec3<f32>(dot(c, vec3<f32>(127.1, 311.7, 74.7)), dot(c, vec3<f32>(269.5, 183.3, 246.1)), dot(c, vec3<f32>(113.5, 271.9, 124.6)))) * 43758.55);
  }
`);
const h11 = wgslFn(`
  fn h11(x: f32) -> f32 { return fract(sin(x * 91.37 + 1.73) * 43758.5453); }
`);
// smooth value noise, 0..1
const vn3 = wgslFn(`
  fn vn3(p: vec3<f32>) -> f32 {
    let g = floor(p); var f = fract(p); f = f * f * (3.0 - 2.0 * f);
    let a = hash33(g).x; let b = hash33(g + vec3<f32>(1.0, 0.0, 0.0)).x; let c = hash33(g + vec3<f32>(0.0, 1.0, 0.0)).x; let d = hash33(g + vec3<f32>(1.0, 1.0, 0.0)).x;
    let e = hash33(g + vec3<f32>(0.0, 0.0, 1.0)).x; let f1 = hash33(g + vec3<f32>(1.0, 0.0, 1.0)).x; let g1 = hash33(g + vec3<f32>(0.0, 1.0, 1.0)).x; let h = hash33(g + vec3<f32>(1.0, 1.0, 1.0)).x;
    return mix(mix(mix(a, b, f.x), mix(c, d, f.x), f.y), mix(mix(e, f1, f.x), mix(g1, h, f.x), f.y), f.z);
  }
`, [hash33]);
// the nearest point of a jittered grid (in its own units) -- and, w, the distance to the second nearest minus the nearest
// (the border between cells)
const vor3 = wgslFn(`
  fn vor3(p: vec3<f32>) -> vec4<f32> {
    let g = floor(p);
    var s1 = 9.0; var s2 = 9.0; var fp = vec3<f32>(0.0);
    for (var i: i32 = -1; i <= 1; i = i + 1) {
      for (var j: i32 = -1; j <= 1; j = j + 1) {
        for (var k: i32 = -1; k <= 1; k = k + 1) {
          let c = g + vec3<f32>(f32(i), f32(j), f32(k));
          let f = c + 0.1 + hash33(c) * 0.8;
          let d = length(f - p);
          if (d < s1) { s2 = s1; s1 = d; fp = f; } else if (d < s2) { s2 = d; }
        }
      }
    }
    return vec4<f32>(fp, s2 - s1);
  }
`, [hash33]);

// a tiger's (zebra 0) or a zebra's (zebra 1) stripes: how much of the pixel is stripe
const stripesOf = wgslFn(`
  fn stripesOf(p: vec3<f32>, r: f32, px: f32, zebra: f32) -> f32 {
    let rr = max(r, 0.015);
    let th = atan2(p.z, p.y);
    let a = th * rr;
    var sp = clamp(0.05 + 0.12 * rr, 0.05, 0.095);
    if (zebra > 0.5) { sp = clamp(0.09 + 0.16 * rr, 0.08, 0.15); }
    let wob = select(1.0, 0.45, zebra > 0.5);
    let n1 = vn3(vec3<f32>(p.x / sp * 0.45, a / sp * 0.32, 3.7)) - 0.5;
    let n2 = vn3(vec3<f32>(p.x / sp * 1.3 + 7.1, a / sp * 1.05, 9.2)) - 0.5;
    let X = p.x / sp + wob * (0.95 * n1 + 0.3 * n2 + 0.16 * sin(a / sp * 0.8));
    let id = floor(X);
    let fx = X - id - 0.5;
    let h1 = h11(id * 1.37 + 0.11); let h2 = h11(id * 2.71 + 3.3); let h3 = h11(id * 5.13 + 1.9); let h4 = h11(id * 9.7 + 4.4);
    let thin = 1.0 - smoothstep(0.05, 0.13, rr);
    var reach = mix(mix(1.3, 2.45, h1), mix(2.4, 3.6, h1), thin);
    var hw0 = mix(0.12, 0.25, h2);
    var hw = hw0;
    var tt = abs(th) / reach;
    if (zebra > 0.5) {
      reach = mix(2.7, 3.6, h1); tt = abs(th) / reach; hw0 = mix(0.24, 0.34, h2);
      hw = hw0 * pow(max(0.0, 1.0 - pow(min(tt, 1.0), 6.0)), 0.5);
    } else {
      hw = hw0 * pow(max(0.0, 1.0 - min(tt, 1.0) * min(tt, 1.0)), 0.8) * (0.85 + 0.3 * vn3(vec3<f32>(id, a / sp * 1.7, 1.3)));
    }
    var d = abs(fx) - hw;
    if (tt >= 1.0) { d = 1.0; }
    // forked: split in two below a point down the flank, the branches thinner
    if (h3 > 0.62 && zebra < 0.5) {
      let fs = mix(0.3, 0.55, h4);
      let k = clamp((tt - fs) / (1.0 - fs), 0.0, 1.0);
      if (k > 0.0 && tt < 1.0) {
        let off = hw0 * 1.25 * sqrt(k);
        let hwF = hw * mix(1.0, 0.6, k);
        d = min(abs(fx - off) - hwF, abs(fx + off) - hwF);
      }
    }
    // doubled: a thin companion beside it, shorter
    if (h3 < 0.22) {
      let reach2 = reach * mix(0.35, 0.7, h4);
      let t2 = abs(th) / reach2;
      let hw2 = hw0 * 0.42 * pow(max(0.0, 1.0 - min(t2, 1.0) * min(t2, 1.0)), 0.7);
      let off2 = select(0.34, -0.34, h4 > 0.5);
      if (t2 < 1.0) { d = min(d, abs(fx - off2) - hw2); }
    }
    // broken: a gap part way down
    if (h4 > 0.82 && zebra < 0.5) { let g = mix(0.35, 0.65, h1); d = max(d, 0.06 - abs(tt - g) * 1.6); }
    let aa = px / sp * 1.1 + 0.012;
    let m = 1.0 - smoothstep(-aa, aa, d);
    // (finer than the pixels: their average)
    return mix(m, select(0.28, 0.45, zebra > 0.5), smoothstep(0.3, 0.6, px / sp));
  }
`, [vn3, h11]);

// a leopard's: x the dark (rosette rings, spots), y the rosettes' darker centres
const rosettesOf = wgslFn(`
  fn rosettesOf(p: vec3<f32>, r: f32, px: f32) -> vec2<f32> {
    let small = 1.0 - smoothstep(0.075, 0.14, r);
    // rosettes, on the trunk
    let cs = 0.115;
    let v = vor3(p / cs);
    let d1 = length(v.xyz - p / cs);
    let h = hash33(floor(v.xyz) + 31.7);
    let R0 = mix(0.3, 0.42, h.x);
    let dirv = (p / cs - v.xyz) / max(d1, 1e-3);
    // (the ring broken into 3-5 blotches by short gaps -- not one long gap, which leaves an open "C")
    let br = vn3(dirv * 3.6 + h * 19.0);
    let aa = px / cs * 1.2 + 0.02;
    let ring = abs(d1 - R0) - mix(0.055, 0.095, h.y) * (0.75 + 0.5 * br);
    var dark = (1.0 - smoothstep(-aa, aa, ring)) * smoothstep(0.27, 0.35, br);
    var centre = 1.0 - smoothstep(R0 - 0.08 - aa, R0 - 0.08 + aa, d1);
    if (h.z < 0.16) { dark = 1.0 - smoothstep(-aa, aa, d1 * (1.0 + 0.4 * (br - 0.5)) - mix(0.1, 0.17, h.y)); centre = 0.0; }
    // small solid spots, on the head and the legs
    let cs2 = 0.05;
    let v2 = vor3(p / cs2);
    let d2 = length(v2.xyz - p / cs2);
    let h2 = hash33(floor(v2.xyz) + 7.3);
    let aa2 = px / cs2 * 1.2 + 0.02;
    let sp = 1.0 - smoothstep(-aa2, aa2, d2 * (1.0 + 0.35 * (vn3(p / cs2 * 2.7) - 0.5)) - mix(0.17, 0.3, h2.x));
    let fade = smoothstep(0.25, 0.55, px / cs);
    dark = mix(mix(dark, sp, small), 0.22, fade);
    centre = mix(centre * (1.0 - small), 0.15, fade);
    return vec2<f32>(dark, centre);
  }
`, [vor3, hash33, vn3]);

// a giraffe's: x the patch (1) against the pale network (0), y the patch's own tone
const giraffeOf = wgslFn(`
  fn giraffeOf(p: vec3<f32>, px: f32) -> vec2<f32> {
    let cs = 0.19;
    let w = vec3<f32>(vn3(p / cs * 1.6), vn3(p / cs * 1.6 + 5.2), vn3(p / cs * 1.6 + 9.4)) - 0.5;
    let q = p / cs + 0.32 * w;
    let v = vor3(q);
    let jag = 0.025 * (vn3(p / cs * 9.0) - 0.5);
    let aa = px / cs * 1.3 + 0.015;
    let m = smoothstep(0.075 - aa, 0.075 + aa, v.w + jag);
    let tone = hash33(floor(v.xyz) + 3.1).x;
    return vec2<f32>(mix(m, 0.8, smoothstep(0.3, 0.6, px / cs)), tone);
  }
`, [vn3, vor3, hash33]);

// a feather's vane (23)
const featherOf = wgslFn(`
  fn featherOf(col: vec3<f32>, pl: vec4<f32>, q: vec4<f32>, px: f32) -> vec3<f32> {
    let L = max(pl.z, 1e-4);
    let W = max(pl.w, 1e-4);
    let t = pl.x / L;
    let y = pl.y;
    // the barbs: fine lines from the shaft out and toward the tip
    let bs = max(W * 0.11, 0.0012);
    let barb = 0.5 + 0.5 * cos((pl.x - abs(y) * 0.8) / bs * 6.2832);
    var c = col * (1.0 - 0.16 * barb * (1.0 - smoothstep(0.3, 0.6, px / bs)));
    // the bars, across it
    if (q.x > 0.5) {
      let b = fract(t * q.x + 0.3 + 0.05 * sin(y / W * 3.0));
      let aa = px / L * q.x * 1.5 + 0.02;
      let m = smoothstep(0.42 - aa, 0.42 + aa, b) * (1.0 - smoothstep(0.72 - aa, 0.72 + aa, b));
      c = mix(c, c * q.y, m * smoothstep(0.06, 0.16, t));
    }
    // the eye
    if (q.w > 0.0) {
      let rx = W * q.w;
      let e = vec2<f32>((pl.x - q.z * L) / (rx * 1.3), y / rx);
      let rho = length(e);
      let aa = px / rx * 1.2 + 0.01;
      let heartR = length(vec2<f32>(e.x * 1.25 + 0.12, e.y * (1.25 + 0.35 * e.x)));
      let heart = 1.0 - smoothstep(0.36 - aa, 0.36 + aa, heartR);
      let ringT = 1.0 - smoothstep(0.55 - aa, 0.55 + aa, rho + 0.06 * e.x);
      let ringB = 1.0 - smoothstep(0.7 - aa, 0.7 + aa, rho);
      let ringG = 1.0 - smoothstep(0.9 - aa, 0.9 + aa, rho);
      let rim = (1.0 - smoothstep(0.97 - aa, 0.97 + aa, rho)) - ringG;
      var eye = mix(col, vec3<f32>(0.11, 0.2, 0.025), ringG);
      eye = mix(eye, vec3<f32>(0.03, 0.03, 0.01), rim * 0.8);
      eye = mix(eye, vec3<f32>(0.34, 0.17, 0.035), ringB);
      eye = mix(eye, vec3<f32>(0.015, 0.3, 0.38), ringT);
      eye = mix(eye, vec3<f32>(0.012, 0.012, 0.085), heart);
      c = mix(c, eye, 1.0 - smoothstep(0.6, 1.2, px / rx));
    }
    // the rachis, pale down the middle (fading on pale feathers, whose shafts are as pale as the vane:
    // a white wing otherwise blows out into bright lines)
    let rw = max(W * 0.045, 0.0005) * (1.0 - 0.6 * t);
    let ra = 1.0 - smoothstep(rw - px, rw + px, abs(y));
    let lum = dot(col, vec3<f32>(0.3, 0.59, 0.11));
    let rk = 1.0 - 0.75 * smoothstep(0.3, 0.9, lum);
    c = mix(c, col * 1.6 + vec3<f32>(0.02, 0.02, 0.015), ra * 0.6 * rk * (1.0 - smoothstep(0.88, 1.0, t)));
    return c;
  }
`);

// 25 OSTEODERMS (a carnotaur's feature scales, 2026-11-05): the reptile scales (17) with big domed feature scales
// among them -- the nearest point of a jittered 3D grid (vor3, cells 15 x 19 x 19 cm in the frame) is one where the
// surface passes within its radius, kept only near irregular rows along the body (every 24 cm up the flank) and above
// the frame's middle less 0.5 m (none on the belly), larger higher up; each a pale dome lit from above in a dark seam.
// p in metres in the shape's frame (y up from its origin), px the footprint (col: the small scales already laid)
const osteodermsOf = wgslFn(`
  fn osteodermsOf(col: vec3<f32>, p: vec3<f32>, px: f32) -> vec3<f32> {
    let S = vec3<f32>(0.15, 0.19, 0.19);
    let c = vor3(p / S);
    let fp = c.xyz * S;
    let h = hash33(floor(c.xyz * 7.31) + vec3<f32>(7.0, 3.0, 1.0));
    let rowd = abs(fract(fp.y / 0.24 + 0.5) - 0.5);
    let keep = (1.0 - smoothstep(0.13, 0.22, rowd)) * step(0.25, h.x) * smoothstep(-0.55, -0.25, fp.y);
    let R = (0.05 + 0.03 * h.z) * (0.85 + 0.5 * smoothstep(-0.2, 0.45, fp.y));
    let t = length(p - fp) / R;
    let aa = clamp(px / R, 0.03, 1.0);
    let disc = 1.0 - smoothstep(1.0 - aa, 1.0 + aa, t);
    let seam = smoothstep(0.86, 1.0, t) * (1.0 - smoothstep(1.04, 1.14 + aa, t));
    // (a dome lit from above: its upper half brighter, its lower in its own shadow)
    let lift = clamp((p.y - fp.y) / R, -1.0, 1.0) * sqrt(max(1.0 - t * t, 0.0));
    let dome = (1.16 - 0.2 * t * t) * (1.0 + 0.55 * lift);
    var o = mix(col, col * vec3<f32>(1.04, 1.0, 0.93) * dome, disc);
    o = mix(o, col * 0.6, seam * 0.45);
    let detail = 1.0 - smoothstep(0.6, 1.4, px / R);
    return mix(col, o, keep * detail);
  }
`, [vor3, hash33]);

// THE SEA'S COATS (2026-11-05, assets/creatures/sea). All but 26 take p in METRES in the shape's frame (as 25 does: not
// scaled by the body's patScale) and its frame's `r` as their measure, so the frame an author writes sizes them:
//   26 ZEBRATONE (a lionfish's): the zebra's bands (4), in the coat's own darker red -- maroon on cream (patScale-sized)
//   27 PALESPOTS (a pike's): rows of pale bean-shaped spots, longer than they are tall
//   28 TROUT (a brown trout's): black spots, thick above the frame's middle (y: up from the frame's origin, in r) and
//      few below it, and red spots ringed pale along the middle of the flank
//   29 MOTTLE (an octopus's, a crab's): two octaves of blotching, a dark net between cells, pale papillae
//   30 SUCKERS (an octopus's arm, in the arm's own frame: x along it, y up, r its radius): the mottle above, a pale
//      oral side below and on it two staggered rows of suckers, each a pale disc round a dark cup
//   31 CLOWN (a clownfish's, in a frame from the snout tip, u back along the body, r its length): the three white bars
//      edged in black -- the head's bowed back behind the eye, the body's bulging forward, the narrow one at the tail
// spots on a jittered grid (cells S metres): x how much of the pixel is spot (radius R cells, each its own size), y the
// spot's random number (to keep or drop it); the same seed and cells give concentric spots (a halo round a spot)
const spotsOf = wgslFn(`
  fn spotsOf(p: vec3<f32>, S: vec3<f32>, R: f32, px: f32, seed: f32) -> vec2<f32> {
    let q = p / S + vec3<f32>(seed, seed * 1.7, seed * 2.3);
    let c = vor3(q);
    let h = hash33(floor(c.xyz * 7.31) + vec3<f32>(seed, 1.0, 2.0));
    let rr = R * (0.75 + 0.5 * h.y);
    let d = length(q - c.xyz);
    let aa = px / min(S.x, min(S.y, S.z)) + 0.02;
    let fade = 1.0 - smoothstep(0.35, 0.8, px / (min(S.x, min(S.y, S.z)) * R));
    return vec2<f32>((1.0 - smoothstep(rr - aa, rr + aa, d)) * fade, h.x);
  }
`, [vor3, hash33]);
const palespotsOf = wgslFn(`
  fn palespotsOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    let m = spotsOf(p, vec3<f32>(0.62, 0.36, 0.36) * r, 0.3, px, 3.0);
    let pale = mix(vec3<f32>(0.52, 0.48, 0.2), col * 2.4, 0.25);
    return mix(col, pale, m.x * step(0.12, m.y) * 0.9);
  }
`, [spotsOf]);
const troutOf = wgslFn(`
  fn troutOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    let yn = p.y / r;
    let b = spotsOf(p, vec3<f32>(0.3) * r, 0.24, px, 1.0);
    let kb = step(b.y, mix(0.08, 0.85, smoothstep(-0.55, 0.5, yn)));
    let S2 = vec3<f32>(0.46) * r;
    let rd = spotsOf(p, S2, 0.19, px, 5.0);
    let halo = spotsOf(p, S2, 0.33, px, 5.0);
    let kr = step(rd.y, 0.6) * (1.0 - smoothstep(0.22, 0.55, abs(yn + 0.08)));
    var o = mix(col, col * 1.3 + vec3<f32>(0.1, 0.09, 0.06), halo.x * kr * 0.85);
    o = mix(o, vec3<f32>(0.42, 0.045, 0.02), rd.x * kr);
    return mix(o, vec3<f32>(0.02, 0.017, 0.014), b.x * kb * (1.0 - halo.x * kr) * 0.95);
  }
`, [spotsOf]);
const mottleOf = wgslFn(`
  fn mottleOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    let fine = 1.0 - smoothstep(0.3, 0.8, px / (r * 0.22));
    let n = vn3(p / (r * 0.55)) * 0.65 + mix(0.5, vn3(p / (r * 0.22) + vec3<f32>(5.0)), fine) * 0.35;
    let c = vor3(p / (r * 0.3));
    let net = (1.0 - smoothstep(0.04, 0.15, c.w)) * (1.0 - smoothstep(0.3, 0.8, px / (r * 0.3)));
    var o = col * (0.5 + 1.0 * n);
    o = mix(o, o * 0.5, net * 0.2);
    let pap = spotsOf(p, vec3<f32>(r * 0.16), 0.2, px, 9.0);
    return mix(o, col * 1.55 + vec3<f32>(0.04, 0.03, 0.025), pap.x * step(pap.y, 0.45) * 0.7);
  }
`, [vn3, vor3, spotsOf]);
const suckersOf = wgslFn(`
  fn suckersOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    var o = mottleOf(col, p, r * 2.2, px);
    let pale = vec3<f32>(0.66, 0.46, 0.38);
    o = mix(o, pale * 0.8, smoothstep(-0.15, -0.7, p.y / r));
    let th = atan2(p.z, -p.y);
    let s = r * 0.95;
    let R = r * 0.4;
    let x = p.x / s + select(0.0, 0.5, th > 0.0);
    let du = (fract(x) - 0.5) * s;
    let dv = (abs(th) - 0.46) * r;
    let d = length(vec2<f32>(du, dv)) / R;
    let aa = px / R + 0.03;
    let detail = 1.0 - smoothstep(0.4, 0.9, px / R);
    let disc = (1.0 - smoothstep(1.0 - aa, 1.0 + aa, d)) * detail;
    let cup = (1.0 - smoothstep(0.45 - aa, 0.45 + aa, d)) * detail;
    let rim = smoothstep(0.7, 0.95, d) * disc;
    o = mix(o, pale, disc);
    o = mix(o, pale * 0.62, rim * 0.6);
    return mix(o, pale * vec3<f32>(0.5, 0.36, 0.34), cup);
  }
`, [mottleOf]);
const clownOf = wgslFn(`
  fn clownOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    let x = p.x / r;
    let y = p.y / r;
    let c1 = 0.285 - 1.3 * y * y;
    let c2 = 0.535 - 0.075 * max(0.0, 1.0 - abs(y) / 0.2);
    let d = min(min(abs(x - c1) - 0.05, abs(x - c2) - 0.055), abs(x - 0.865) - 0.028);
    let aa = px / r + 0.0015;
    let white = 1.0 - smoothstep(-aa, aa, d);
    let black = 1.0 - smoothstep(-aa, aa, d - 0.013);
    let o = mix(col, vec3<f32>(0.012, 0.01, 0.01), black);
    return mix(o, vec3<f32>(0.86, 0.86, 0.84), white);
  }
`);
// 32 ROW SCALES (a carp's): overlapping cycloid scales in staggered rows along the body's axis (u, from the tail to
// the head), the rows counted round it by arc from the flank's equator -- each scale a disc the next one forward
// overlaps, so what shows of it is its rounded BACK edge: a dark rim there, a paler middle. Their pitch along the body
// is r * 0.05 (a carp's frame r 0.29: some 35 along the lateral line). Fades to the plain coat where a scale is under
// a few pixels.
const rowscalesOf = wgslFn(`
  fn rowscalesOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    let s = r * 0.05;
    let hs = s * 0.8;
    let rho = length(p.yz);
    let t = atan2(p.y, abs(p.z)) * rho;
    let ci = floor(p.x / s);
    var best = -1e9;
    var bd = 2.0;
    var bh = 0.5;
    for (var a = -1; a <= 1; a++) {
      for (var b = -1; b <= 1; b++) {
        let i = ci + f32(a);
        let off = 0.5 * (i - 2.0 * floor(i * 0.5));
        let j = floor(t / hs - off) + f32(b);
        let c = vec2<f32>((i + 0.5) * s, (j + off + 0.5) * hs);
        let q = (vec2<f32>(p.x, t) - c) / vec2<f32>(s * 0.78, hs * 0.82);
        let d = length(q);
        if (d < 1.0 && c.x > best) { best = c.x; bd = d; bh = h11(i * 7.31 + j * 1.73); }
      }
    }
    let detail = 1.0 - smoothstep(0.25, 0.8, px / (s * 0.3));
    let aa = px / (s * 0.78) + 0.04;
    let rim = smoothstep(0.8 - aa, 0.95, bd);
    let mid = 1.0 - smoothstep(0.0, 0.75, bd);
    var o = col * (0.94 + 0.12 * bh + 0.16 * mid * detail);
    o = mix(o, col * 0.52, rim * 0.75 * detail);
    return o;
  }
`, [h11]);
// 33 FIN RAYS (a fish's fins): faint darker rays fanning from the middle of the fin's root (the frame's o; u toward its
// farthest point, r its reach), the membrane lighter toward the free edge. Fades out where the rays come closer than
// a couple of pixels.
const finraysOf = wgslFn(`
  fn finraysOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    let rr = max(length(p.xy), 1e-5);
    let th = atan2(p.y, p.x);
    let per = 0.085;
    let f = abs(fract(th / per) - 0.5) * per * rr;
    let w = r * 0.005 + px * 0.35;
    let seen = 1.0 - smoothstep(1.0, 2.5, px / (per * rr * 0.5));
    let line = (1.0 - smoothstep(w, w + px + r * 0.004, f)) * smoothstep(0.06, 0.22, rr / r) * seen;
    var o = col * (1.0 - 0.3 * line);
    return mix(o, col * 1.28 + vec3<f32>(0.035), smoothstep(0.5, 1.0, rr / r) * 0.6);
  }
`);

// 34 RIDGES (a horn's, 2026-11-05: an impala's, a kudu's): rings round the horn, across the frame's u (laid along the
// horn's run, one frame per straight-ish stretch), a raised ring and a dark groove every 1.3 r (the frame's r, authored
// the same for every stretch so the pitch runs on unbroken). Fades to the smooth horn where a ring is under a few pixels.
const ridgesOf = wgslFn(`
  fn ridgesOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    let pitch = max(r * 1.3, 1e-4);
    // (round 2: no two rings alike -- the spacing wanders, each ring leans and waves a little round the horn, and each
    //  has its own depth: a horn's growth rings, not an accordion's)
    let u = p.x / pitch;
    let ang = atan2(p.z, p.y);
    let w = u + 0.22 * sin(u * 1.37 + 0.6) + 0.16 * sin(u * 0.61 + 2.1) + 0.18 * p.y / pitch + 0.07 * sin(ang * 2.0 + u * 0.9);
    let h = h11(floor(w) * 3.7 + 1.3);
    let g = abs(fract(w) - 0.5) * 2.0;
    let detail = 1.0 - smoothstep(0.3, 0.8, px / (pitch * 0.5));
    let groove = smoothstep(0.6 + 0.2 * h, 0.97, g);
    let crest = 1.0 - smoothstep(0.0, 0.5, g);
    return col * (1.0 + (0.2 * crest - (0.3 + 0.35 * h) * groove) * detail);
  }
`, [h11]);
// 35 PANGOLIN PLATES (a pangolin's, 2026-11-05): big overlapping horny scales in staggered rows along the body (laid in the
// animal's frame, u from the head to the tail; rows round it by arc from the flank's line, as the carp's row scales are), each scale's rounded
// FREE edge to the rear over the root of the one behind: a pale thick lip along that edge, a dark shadowed seam just
// behind it, fine grain along the scale, every scale its own shade. In METRES (a COAT pattern: x patScale) -- a 4 cm
// pitch, a ground pangolin's.
const pangolinOf = wgslFn(`
  fn pangolinOf(col: vec3<f32>, p0: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    let p = vec3<f32>(-p0.x, p0.y, p0.z);
    let s = 0.04;
    let hs = 0.044;
    let rho = length(p.yz);
    let t = atan2(p.y, abs(p.z)) * rho;
    let ci = floor(p.x / s);
    var best = -1e9;
    var bi = 0.0;
    var bd = 2.0;
    var bq = vec2<f32>(0.0, 0.0);
    var bh = 0.5;
    for (var a = -1; a <= 1; a++) {
      for (var b = -1; b <= 1; b++) {
        let i = ci + f32(a);
        let off = 0.5 * (i - 2.0 * floor(i * 0.5));
        let j = floor(t / hs - off) + f32(b);
        let c = vec2<f32>((i + 0.5) * s, (j + off + 0.5) * hs);
        let q = (vec2<f32>(p.x, t) - c) / vec2<f32>(s * 0.98, hs * 0.66);
        let d = length(q);
        if (d < 1.0 && c.x > best) { best = c.x; bi = i; bd = d; bq = q; bh = h11(i * 7.31 + j * 1.73); }
      }
    }
    // (the shadow: how near the point lies behind the rear edge of a scale one row FORWARD of the one it is on)
    var sh = 0.0;
    for (var a = 0; a <= 2; a++) {
      for (var b = -1; b <= 1; b++) {
        let i = ci + f32(a);
        if (i < bi + 0.5) { continue; }
        let off = 0.5 * (i - 2.0 * floor(i * 0.5));
        let j = floor(t / hs - off) + f32(b);
        let c = vec2<f32>((i + 0.5) * s, (j + off + 0.5) * hs);
        let d = length((vec2<f32>(p.x, t) - c) / vec2<f32>(s * 0.98, hs * 0.66));
        sh = max(sh, 1.0 - smoothstep(1.0, 1.28, d));
      }
    }
    let detail = 1.0 - smoothstep(0.3, 0.9, px / (s * 0.25));
    let lip = smoothstep(0.7, 0.96, bd) * smoothstep(0.2, -0.35, bq.x);
    let grain = 0.5 + 0.5 * sin(bq.y * 26.0);
    var o = col * (0.82 + 0.3 * bh + 0.07 * grain * detail + 0.12 * (0.5 - bq.x * 0.5) * detail);
    o = mix(o, col * 1.5 + vec3<f32>(0.025), lip * 0.55 * detail);
    o = mix(o, col * 0.3, sh * 0.85 * detail);
    return select(o, col * 0.35, bd > 1.5);
  }
`, [h11]);

// 36 SHAG (2026-11-05, the apes': an orangutan's hanging coat, a gorilla's arms, a baboon's mane): long hair in the
// shape's own frame -- LOCKS a couple of centimetres across running along its axis (u: down a hanging arm, back along
// a trunk), dark partings between them, and fine strands in each; noise stretched along the axis, so seamless round it.
// In metres. Each scale fades to its average where it is under the pixels.
const shagOf = wgslFn(`
  fn shagOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    let dL = 1.0 - smoothstep(0.3, 0.9, px / 0.011);
    let dF = 1.0 - smoothstep(0.3, 0.9, px / 0.0035);
    let l = mix(0.5, vn3(vec3<f32>(p.y / 0.011, p.z / 0.011, p.x / 0.09)), dL);
    let f = mix(0.5, vn3(vec3<f32>(p.y / 0.0035, p.z / 0.0035, p.x / 0.04) + vec3<f32>(7.1, 3.3, 1.9)), dF);
    let part = (1.0 - smoothstep(0.18, 0.34, l)) * dL;
    var o = col * (0.8 + 0.42 * l) * (0.84 + 0.32 * f);
    return mix(o, col * 0.5, part * 0.45);
  }
`, [vn3]);
// 37 AGOUTI (2026-11-05, a baboon's olive, a kangaroo's grizzle, a silverback's saddle): TICKED fur -- every hair
// banded, so the coat is a fine salt-and-pepper of dark and pale tips over a soft mottle; a SOLID pattern (the rest
// pose's own space, so it runs on across the seams). In metres: a fine noise 2.2 mm across (no cells: no squares seen up
// close), faded to the mean under the pixels.
const agoutiOf = wgslFn(`
  fn agoutiOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    let c = 0.0022;
    let d = 1.0 - smoothstep(0.3, 0.9, px / c);
    let h = vn3(p / c + vec3<f32>(3.0, 1.0, 7.0));
    let n = vn3(p / 0.03);
    var o = col * (0.93 + 0.14 * n);
    o = o * mix(1.0, 0.8 + 0.4 * h, d);
    return mix(o, col * 1.5 + vec3<f32>(0.025, 0.022, 0.018), smoothstep(0.72, 0.9, h) * d * 0.35);
  }
`, [hash33, vn3]);
// a giant anteater's BAND (38, 2026-11-05), laid in the rest pose's own space (metres: x forward, y up, z left): black
// from the throat diagonally back and up over the shoulder to a point on the back, a white border either side -- the
// band a polyline in (x, the arc round the trunk's axis at y .47 from the flank's line up), its half-width along it.
// Per pixel, so its edges stay clean at any distance (laid as paint shapes, the near mesh's vertices tore them up)
const anteaterOf = wgslFn(`
  fn anteaterOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    var K = array<vec3<f32>, 11>(vec3<f32>(0.43, -78.0, 0.04), vec3<f32>(0.4, -40.0, 0.045), vec3<f32>(0.36, -26.0, 0.052),
      vec3<f32>(0.33, -20.0, 0.055), vec3<f32>(0.27, 2.0, 0.055), vec3<f32>(0.2, 22.0, 0.05), vec3<f32>(0.12, 40.0, 0.044),
      vec3<f32>(0.04, 55.0, 0.036), vec3<f32>(-0.04, 66.0, 0.027), vec3<f32>(-0.11, 74.0, 0.017), vec3<f32>(-0.16, 79.0, 0.006));
    let R = 0.17;
    let q = vec2<f32>(p.x, R * atan2(p.y - 0.47, max(abs(p.z), 1e-4)));
    var best = 1e9;
    var w = 0.0;
    for (var i = 0; i < 10; i++) {
      let a = vec2<f32>(K[i].x, R * radians(K[i].y));
      let b = vec2<f32>(K[i + 1].x, R * radians(K[i + 1].y));
      let ab = b - a;
      let t = clamp(dot(q - a, ab) / dot(ab, ab), 0.0, 1.0);
      let d = length(q - a - ab * t);
      if (d < best) { best = d; w = mix(K[i].z, K[i + 1].z, t); }
    }
    let aa = max(px, 0.0015);
    let wn = vn3(p / 0.012) - 0.5;
    let d = best + wn * 0.006;
    let black = 1.0 - smoothstep(w - aa, w + aa, d);
    let edge = (1.0 - smoothstep(w + 0.032 * (0.4 + w / 0.055 * 0.6) - aa, w + 0.032 * (0.4 + w / 0.055 * 0.6) + aa, d)) * step(0.004, w);
    var o = mix(col, vec3<f32>(0.74, 0.7, 0.61) * (0.92 + 0.16 * wn), edge);
    return mix(o, vec3<f32>(0.007, 0.006, 0.005), black);
  }
`, [vn3]);
// COARSE HAIR (2026-11-05, with the skunk's and the capybara's coats), in the rest pose's own space (metres): strands
// L long and W across -- value noise stretched along x on the trunk (hair lying back) and along y where `vert` says
// (a leg's, a raised tail's: hair hanging down it), wavering, in clumps; dark partings between them, `lift` added
// on the strands' crests (a black coat's grey glints), and `g` of pale tips (a grizzle). Faded to the mean under the pixels
const hairOf = wgslFn(`
  fn hairOf(col: vec3<f32>, p: vec3<f32>, px: f32, L: f32, W: f32, g: f32, lift: f32, vert: f32) -> vec3<f32> {
    let d = 1.0 - smoothstep(0.35, 1.0, px / W);
    let dc = 1.0 - smoothstep(0.35, 1.0, px / (W * 4.0));
    // (the two across-axes turned off the noise's grid, and two octaves at other turns: no squares seen up close)
    let wv = vn3(p / (L * 1.6) + vec3<f32>(2.3, 7.7, 4.1)) - 0.5;
    let ra = vec3<f32>(p.x, 0.8 * p.y + 0.6 * p.z, 0.8 * p.z - 0.6 * p.y);
    let rb = vec3<f32>(0.8 * p.x + 0.6 * p.z, p.y, 0.8 * p.z - 0.6 * p.x);
    let a = vn3(vec3<f32>(ra.x / L, ra.y / W + wv * 4.0, ra.z / W + wv * 2.0)) * 0.6
          + vn3(vec3<f32>(ra.x / (L * 0.7) + 3.1, (0.6 * ra.y + 0.8 * ra.z) / (W * 0.6), (0.8 * ra.y - 0.6 * ra.z) / (W * 0.6))) * 0.4;
    let b = vn3(vec3<f32>(rb.x / W + wv * 4.0, rb.y / L, rb.z / W + wv * 2.0) + vec3<f32>(5.3, 1.7, 9.1)) * 0.6
          + vn3(vec3<f32>((0.6 * rb.x + 0.8 * rb.z) / (W * 0.6), rb.y / (L * 0.7) + 2.2, (0.8 * rb.x - 0.6 * rb.z) / (W * 0.6))) * 0.4;
    let s = mix(a, b, vert);
    let ta = vn3(vec3<f32>(ra.x / (L * 0.6), ra.y / (W * 0.8), ra.z / (W * 0.8)) + vec3<f32>(11.0, 3.0, 6.0));
    let tb = vn3(vec3<f32>(rb.x / (W * 0.8), rb.y / (L * 0.6), rb.z / (W * 0.8)) + vec3<f32>(1.0, 13.0, 8.0));
    let t = mix(ta, tb, vert);
    let c = vn3(vec3<f32>(p.x / (W * 9.0), p.y / (W * 6.0), p.z / (W * 6.0)) + vec3<f32>(4.0, 4.0, 4.0));
    var o = col * mix(1.0, 0.84 + 0.32 * c, dc);
    o = o * mix(1.0, 0.66 + 0.68 * smoothstep(0.2, 0.8, s), d);
    o = o + vec3<f32>(lift) * smoothstep(0.6, 0.85, s) * d;
    return mix(o, col * 1.75 + vec3<f32>(0.035, 0.03, 0.022), smoothstep(0.66, 0.84, t) * d * g);
  }
`, [vn3]);
// a striped skunk's WHITE (39, 2026-11-05), in the rest pose's own space (metres): knots along x, each the trunk's (or the
// head's) axis height there, and the white's centre and half-width as angles round that axis from the top -- a thin
// blaze up the snout, a gap, the broad cap over crown and nape, parting at the shoulders into two bands along the back.
// All of it in coarse long fur (hairOf: black with grey glints). The TAIL is the rig's arc (skunk.json: centre C, radius
// R, from angle a0 for 2.3727 rad, .361 m): ta along it, dd in from it toward the arc's centre -- its fur runs along
// it, the back's two stripes running onto its root's flanks and meeting in a broad white band along its outer (convex)
// side, up and back, to the white tip
const skunkOf = wgslFn(`
  fn skunkOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    var K = array<vec4<f32>, 15>(vec4<f32>(0.262, 0.118, 0.0, 0.0), vec4<f32>(0.25, 0.121, 0.0, 4.0), vec4<f32>(0.236, 0.128, 0.0, 5.0),
      vec4<f32>(0.222, 0.134, 0.0, 5.0), vec4<f32>(0.21, 0.138, 0.0, 30.0), vec4<f32>(0.198, 0.142, 0.0, 56.0),
      vec4<f32>(0.17, 0.145, 0.0, 56.0), vec4<f32>(0.145, 0.148, 0.0, 48.0), vec4<f32>(0.11, 0.15, 14.0, 26.0),
      vec4<f32>(0.06, 0.155, 24.0, 18.0), vec4<f32>(0.0, 0.16, 30.0, 15.0), vec4<f32>(-0.06, 0.168, 32.0, 13.0),
      vec4<f32>(-0.12, 0.178, 30.0, 12.0), vec4<f32>(-0.175, 0.19, 24.0, 12.0), vec4<f32>(-0.25, 0.2, 26.0, 16.0));
    var k = K[14];
    for (var i = 0; i < 14; i++) {
      if (p.x <= K[i].x && p.x >= K[i + 1].x) { k = mix(K[i], K[i + 1], (K[i].x - p.x) / (K[i].x - K[i + 1].x)); }
    }
    let q = vec2<f32>(abs(p.z), p.y - k.y);
    let rl = length(q);
    let tv = p.xy - vec2<f32>(-0.0884, 0.3282);
    var da = -2.3951 - atan2(tv.y, tv.x);
    da = da - 6.2831853 * floor((da + 1.955) / 6.2831853);
    let ta = da / 2.3727;
    let dd = 0.152 - length(tv);
    let tail = smoothstep(0.02, 0.11, ta) * (1.0 - smoothstep(0.11, 0.14, abs(dd)));
    let phi = degrees(atan2(q.x, q.y));
    let wn = vn3(p / 0.006) - 0.5;
    let d = radians(abs(phi - k.z) - k.w) * rl + wn * 0.0016;
    let aa = max(px, 0.0006);
    let inX = step(p.x, K[0].x) * step(K[14].x, p.x);
    let white = (1.0 - smoothstep(-aa, aa, d)) * step(0.5, k.w) * inX * (1.0 - tail);
    let wc = vec3<f32>(0.8, 0.8, 0.76) * (0.94 + 0.12 * wn);
    let o = mix(col, wc, white);
    let legs = 1.0 - smoothstep(0.05, 0.09, p.y);
    let f = hairOf(o, p, px, 0.014, 0.0013, 0.0, 0.014 * (1.0 - white), legs);
    let fw = mix(f, mix(o, f, 0.45), white);   // (the white's fur gentler: it shows every crease)
    let tq = vec3<f32>(ta * 0.361, dd, p.z);
    let tn = vn3(vec3<f32>(tq.x / 0.03, tq.y / 0.003, tq.z / 0.003) + vec3<f32>(3.0, 7.0, 1.0)) - 0.5;
    let th = atan2(abs(p.z), -dd);   // (round the tail from its outer, convex side: 0, to its inner: pi)
    let mig = smoothstep(0.02, 0.3, ta);   // (the back's two stripes reach its root on its flanks, and meet on its outer side)
    let thc = mix(1.0, 0.0, mig);
    let tw0 = mix(1.0, 0.78, mig);
    let tw = max(1.0 - smoothstep(tw0 - 0.1, tw0 + 0.05, abs(th - thc) + tn * 0.25), smoothstep(0.84, 0.9, ta + tn * 0.07));
    let to = mix(col, wc, tw);
    let tf = hairOf(to, tq, px, 0.03, 0.0016, 0.0, 0.012 * (1.0 - tw), 0.0);
    return mix(fw, mix(tf, mix(to, tf, 0.3), tw), tail);
  }
`, [vn3, hairOf]);
// 40 COARSE (2026-11-05, a capybara's): sparse coarse brown hair, a few centimetres long -- hairOf's strands with a
// grizzle of pale tips, the hair running down the legs (below the trunk, y < .26 m)
const coarseOf = wgslFn(`
  fn coarseOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    return hairOf(col, p, px, 0.03, 0.0032, 0.55, 0.0, 1.0 - smoothstep(0.2, 0.28, p.y));
  }
`, [hairOf]);
// 41 ORCA (2026-11-06, an adult male killer whale's markings: assets/creatures/sea/orca.json, its generator scratchpad
// sc/sea3/gen/orca.py writes these numbers), SOLID: the rest pose's own space, metres. Round the body's axis (AX: x, the
// axis's height, the half height and half width there) each point has its ELLIPTIC ANGLE from the belly's midline (0) to
// the spine (pi); the white and the grey are polygons in (x, that angle x RM metres), every edge antialiased by the
// pixel and sharp as an orca's are:
//   the white LOWER JAW (everything under the lip line, LP, ahead of the mouth's corner), the throat and the belly --
//   narrowing between the flippers, widening behind the navel and parting into the FLANK LOBES that sweep up and back
//   behind the dorsal fin, and a central prong back to the vent (BP);
//   the grey SADDLE behind the fin (SP), its edge a little softer;
//   the white EYE PATCH: an egg above and behind the eye, its narrow end forward, its long axis rising a little rearward;
//   the flukes' white UNDERSIDE (behind XF, under their mid-plane), inside a black margin (FP: x, |z|)
const orcaBelly = wgslFn(`
  fn orcaBelly(q: vec2<f32>) -> f32 {
    var V = array<vec2<f32>, 33>(vec2<f32>(2.0950, 0.8393), vec2<f32>(2.0250, 0.8161), vec2<f32>(1.9500, 0.6720), vec2<f32>(1.8000, 0.5280), vec2<f32>(1.6200, 0.3960), vec2<f32>(1.4500, 0.3120), vec2<f32>(1.3000, 0.2700), vec2<f32>(1.0000, 0.2520), vec2<f32>(0.7000, 0.2700), vec2<f32>(0.3500, 0.3000), vec2<f32>(0.0000, 0.3360), vec2<f32>(-0.3500, 0.3720), vec2<f32>(-0.6200, 0.4200), vec2<f32>(-0.8000, 0.4920), vec2<f32>(-0.9200, 0.6300), vec2<f32>(-1.0200, 0.8280), vec2<f32>(-1.1200, 0.9840), vec2<f32>(-1.2600, 1.0800), vec2<f32>(-1.4500, 1.1280), vec2<f32>(-1.7000, 1.1580), vec2<f32>(-1.9500, 1.1820), vec2<f32>(-2.0800, 1.1880), vec2<f32>(-1.9800, 1.1040), vec2<f32>(-1.8400, 0.9120), vec2<f32>(-1.7000, 0.6720), vec2<f32>(-1.6000, 0.4680), vec2<f32>(-1.5400, 0.3360), vec2<f32>(-1.6800, 0.2400), vec2<f32>(-1.9000, 0.1620), vec2<f32>(-2.1000, 0.0900), vec2<f32>(-2.3500, 0.0000), vec2<f32>(-2.3500, -0.3000), vec2<f32>(2.0950, -0.3000));
    var d = dot(q - V[0], q - V[0]);
    var s = 1.0;
    var j = 32;
    for (var i = 0; i < 33; i++) {
      let e = V[j] - V[i];
      let w = q - V[i];
      let b = w - e * clamp(dot(w, e) / dot(e, e), 0.0, 1.0);
      d = min(d, dot(b, b));
      let c1 = q.y >= V[i].y;
      let c2 = q.y < V[j].y;
      let c3 = e.x * w.y > e.y * w.x;
      if ((c1 && c2 && c3) || (!c1 && !c2 && !c3)) { s = -s; }
      j = i;
    }
    return s * sqrt(d);
  }
`);
const orcaSaddle = wgslFn(`
  fn orcaSaddle(q: vec2<f32>) -> f32 {
    var V = array<vec2<f32>, 8>(vec2<f32>(-0.8200, 2.1600), vec2<f32>(-0.8500, 1.5960), vec2<f32>(-0.9800, 1.4820), vec2<f32>(-1.2500, 1.4280), vec2<f32>(-1.5500, 1.4640), vec2<f32>(-1.8200, 1.5840), vec2<f32>(-1.9500, 1.7700), vec2<f32>(-1.9800, 2.1600));
    var d = dot(q - V[0], q - V[0]);
    var s = 1.0;
    var j = 7;
    for (var i = 0; i < 8; i++) {
      let e = V[j] - V[i];
      let w = q - V[i];
      let b = w - e * clamp(dot(w, e) / dot(e, e), 0.0, 1.0);
      d = min(d, dot(b, b));
      let c1 = q.y >= V[i].y;
      let c2 = q.y < V[j].y;
      let c3 = e.x * w.y > e.y * w.x;
      if ((c1 && c2 && c3) || (!c1 && !c2 && !c3)) { s = -s; }
      j = i;
    }
    return s * sqrt(d);
  }
`);
const orcaFluke = wgslFn(`
  fn orcaFluke(q: vec2<f32>) -> f32 {
    var V = array<vec2<f32>, 11>(vec2<f32>(-3.8806, 0.0700), vec2<f32>(-3.9089, 0.2500), vec2<f32>(-3.9954, 0.4500), vec2<f32>(-4.1431, 0.6500), vec2<f32>(-4.2956, 0.8000), vec2<f32>(-4.4431, 0.8800), vec2<f32>(-4.3506, 0.8000), vec2<f32>(-4.2630, 0.6000), vec2<f32>(-4.2083, 0.4000), vec2<f32>(-4.1802, 0.2000), vec2<f32>(-4.1607, 0.0700));
    var d = dot(q - V[0], q - V[0]);
    var s = 1.0;
    var j = 10;
    for (var i = 0; i < 11; i++) {
      let e = V[j] - V[i];
      let w = q - V[i];
      let b = w - e * clamp(dot(w, e) / dot(e, e), 0.0, 1.0);
      d = min(d, dot(b, b));
      let c1 = q.y >= V[i].y;
      let c2 = q.y < V[j].y;
      let c3 = e.x * w.y > e.y * w.x;
      if ((c1 && c2 && c3) || (!c1 && !c2 && !c3)) { s = -s; }
      j = i;
    }
    return s * sqrt(d);
  }
`);
const orcaOf = wgslFn(`
  fn orcaOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    var AX = array<vec4<f32>, 18>(vec4<f32>(2.8000, -0.1200, 0.0450, 0.0500), vec4<f32>(2.7160, -0.1075, 0.1075, 0.1200), vec4<f32>(2.5900, -0.0950, 0.1950, 0.2000), vec4<f32>(2.3800, -0.0775, 0.3025, 0.3000), vec4<f32>(2.1000, -0.0650, 0.4150, 0.4100), vec4<f32>(1.7500, -0.0575, 0.5275, 0.5100), vec4<f32>(1.3300, -0.0450, 0.6200, 0.5850), vec4<f32>(0.8400, -0.0325, 0.6825, 0.6300), vec4<f32>(0.2800, -0.0150, 0.7100, 0.6450), vec4<f32>(-0.3500, 0.0000, 0.6900, 0.6250), vec4<f32>(-1.0500, 0.0150, 0.6150, 0.5550), vec4<f32>(-1.6800, 0.0325, 0.5075, 0.4400), vec4<f32>(-2.2400, 0.0450, 0.3950, 0.3000), vec4<f32>(-2.8000, 0.0525, 0.2875, 0.1800), vec4<f32>(-3.2900, 0.0525, 0.1925, 0.1100), vec4<f32>(-3.6400, 0.0475, 0.1225, 0.0850), vec4<f32>(-3.8850, 0.0400, 0.0750, 0.0750), vec4<f32>(-4.0250, 0.0350, 0.0550, 0.0700));
    var LP = array<vec2<f32>, 6>(vec2<f32>(2.7950, -0.1470), vec2<f32>(2.6600, -0.1520), vec2<f32>(2.4850, -0.1570), vec2<f32>(2.3100, -0.1570), vec2<f32>(2.1700, -0.1520), vec2<f32>(2.0650, -0.1370));
    var a = AX[17];
    if (p.x >= AX[0].x) { a = AX[0]; }
    for (var i = 0; i < 17; i++) {
      if (p.x <= AX[i].x && p.x >= AX[i + 1].x) { a = mix(AX[i], AX[i + 1], (AX[i].x - p.x) / (AX[i].x - AX[i + 1].x)); }
    }
    let ph = atan2(abs(p.z) / a.w, -(p.y - a.y) / a.z);
    let q = vec2<f32>(p.x, ph * 0.6000);
    let aa = max(px, 0.002);
    let wn = vn3(p / 0.05) - 0.5;
    // (the jaw: under the lip line, ahead of the corner)
    var ly = LP[5].y;
    for (var i = 0; i < 5; i++) {
      if (p.x <= LP[i].x && p.x >= LP[i + 1].x) { ly = mix(LP[i].y, LP[i + 1].y, (LP[i].x - p.x) / (LP[i].x - LP[i + 1].x)); }
    }
    let jaw = (1.0 - smoothstep(-aa, aa, p.y - ly)) * smoothstep(-aa, aa, p.x - LP[5].x);
    var white = max(jaw, 1.0 - smoothstep(-aa, aa, orcaBelly(q)));
    // (the eye patch)
    let e = vec2<f32>(p.x - 1.6140, p.y - 0.0900);
    let u = e.x * 0.9848 - e.y * 0.1736;
    let v = e.x * 0.1736 + e.y * 0.9848;
    let bb = 0.0920 * (1.0 - 0.32 * clamp(u / 0.3200, -1.0, 1.0));
    let de = (length(vec2<f32>(u / 0.3200, v / bb)) - 1.0) * bb;
    white = max(white, (1.0 - smoothstep(-aa, aa, de)) * step(0.12, abs(p.z)));
    // (the flukes: their underside, in from the edge)
    let fl = step(p.x, -3.9040);
    let under = 1.0 - smoothstep(-aa, aa, p.y - (0.0350 - 0.02 * p.z * p.z));
    let fw = under * (1.0 - smoothstep(-aa, aa, orcaFluke(vec2<f32>(p.x, abs(p.z)))));
    white = mix(white, fw, fl);
    let grey = (1.0 - smoothstep(-aa - 0.012, aa + 0.012, orcaSaddle(q) + wn * 0.02)) * (1.0 - fl);
    let skin = 1.0 + wn * 0.06 * (1.0 - smoothstep(0.01, 0.04, px));
    var o = mix(col, vec3<f32>(0.25, 0.26, 0.28) * skin, grey);
    return mix(o, vec3<f32>(0.8, 0.81, 0.82) * skin, white);
  }
`, [vn3, orcaBelly, orcaSaddle, orcaFluke]);
// 42 HUMPBACK (2026-11-06, a humpback whale's colours: assets/creatures/sea/humpback.json, its generator scratchpad
// sc/sea3/gen/humpback.py writes these numbers), SOLID: the rest pose's own space, metres. Round the body's axis (AX: x,
// the axis's height, half height, half width) each point has its ELLIPTIC ANGLE from the belly's midline (0) to the spine
// (pi) and its girth share (rho: 1 on the trunk's surface):
//   the dark back; the white BELLY, its upper edge wandering (two noises) high under the flippers, low on the stock and
//   running out before the flukes (the stock's end dark all round),
//   blotched grey inside and flecked white above it;
//   the THROAT PLEATS: 15 grooves either side from the chin to the navel, fanning out over the throat and converging at
//   both ends, darker lines in the white (faded once a pixel is wider than a groove);
//   the FLIPPERS (well out from the trunk, below its axis, between the head and the hump): white, mottled grey, dark at
//   the root;
//   the FLUKES (behind XF): dark above; below, out on the blades (past 2-4.5 local half widths), white inside
//   a black margin (HFP: x, |z|), blotched black -- the stock and the flukes' root dark all round;
//   the MOUTH LINE (LP): a dark crease from the jaw's tip to its corner
const humpFluke = wgslFn(`
  fn humpFluke(q: vec2<f32>) -> f32 {
    var V = array<vec2<f32>, 26>(vec2<f32>(-8.2186, 0.0712), vec2<f32>(-8.2984, 0.3340), vec2<f32>(-8.3745, 0.5387), vec2<f32>(-8.4508, 0.7247), vec2<f32>(-8.5288, 0.8987), vec2<f32>(-8.6091, 1.0634), vec2<f32>(-8.6921, 1.2207), vec2<f32>(-8.7777, 1.3715), vec2<f32>(-8.8659, 1.5169), vec2<f32>(-8.9566, 1.6574), vec2<f32>(-9.0496, 1.7936), vec2<f32>(-9.1452, 1.9257), vec2<f32>(-9.2484, 2.0514), vec2<f32>(-9.2649, 2.0429), vec2<f32>(-9.2936, 1.8486), vec2<f32>(-9.3086, 1.6590), vec2<f32>(-9.3170, 1.4700), vec2<f32>(-9.3207, 1.2804), vec2<f32>(-9.3206, 1.0893), vec2<f32>(-9.3171, 0.8957), vec2<f32>(-9.3104, 0.6988), vec2<f32>(-9.3002, 0.4976), vec2<f32>(-9.2856, 0.2907), vec2<f32>(-9.2649, 0.0757), vec2<f32>(-9.2347, -0.1528), vec2<f32>(-9.1840, -0.4308));
    var d = dot(q - V[0], q - V[0]);
    var s = 1.0;
    var j = 25;
    for (var i = 0; i < 26; i++) {
      let e = V[j] - V[i];
      let w = q - V[i];
      let b = w - e * clamp(dot(w, e) / dot(e, e), 0.0, 1.0);
      d = min(d, dot(b, b));
      let c1 = q.y >= V[i].y;
      let c2 = q.y < V[j].y;
      let c3 = e.x * w.y > e.y * w.x;
      if ((c1 && c2 && c3) || (!c1 && !c2 && !c3)) { s = -s; }
      j = i;
    }
    return s * sqrt(d);
  }
`);
const humpbackOf = wgslFn(`
  fn humpbackOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    var AX = array<vec4<f32>, 22>(vec4<f32>(5.0000, -0.6700, 0.1900, 0.2600), vec4<f32>(4.7200, -0.6547, 0.3347, 0.4889), vec4<f32>(4.3000, -0.6823, 0.5337, 0.7950), vec4<f32>(3.7400, -0.7206, 0.7256, 1.0650), vec4<f32>(3.1800, -0.7543, 0.8657, 1.2087), vec4<f32>(2.6200, -0.7028, 1.0528, 1.2394), vec4<f32>(2.0600, -0.6021, 1.2717, 1.0822), vec4<f32>(1.3600, -0.5149, 1.4851, 1.3552), vec4<f32>(0.8000, -0.4671, 1.6271, 1.5200), vec4<f32>(0.2400, -0.4579, 1.7079, 1.6000), vec4<f32>(-0.6000, -0.4469, 1.7469, 1.6000), vec4<f32>(-1.4400, -0.4056, 1.6556, 1.5000), vec4<f32>(-2.2800, -0.2674, 1.4474, 1.3500), vec4<f32>(-3.1200, -0.0500, 1.1500, 1.1500), vec4<f32>(-3.8200, 0.0300, 0.9500, 0.9500), vec4<f32>(-4.5200, 0.0800, 0.7600, 0.7600), vec4<f32>(-5.2200, 0.1000, 0.6000, 0.6000), vec4<f32>(-6.0600, 0.1000, 0.4400, 0.4400), vec4<f32>(-7.0400, 0.0800, 0.2900, 0.2900), vec4<f32>(-7.7400, 0.0700, 0.2000, 0.2000), vec4<f32>(-8.2300, 0.0600, 0.1500, 0.1500), vec4<f32>(-8.5800, 0.0500, 0.1200, 0.1200));
    var a = AX[21];
    if (p.x >= AX[0].x) { a = AX[0]; }
    for (var i = 0; i < 21; i++) {
      if (p.x <= AX[i].x && p.x >= AX[i + 1].x) { a = mix(AX[i], AX[i + 1], (AX[i].x - p.x) / (AX[i].x - AX[i + 1].x)); }
    }
    let dy = (p.y - a.y) / a.z;
    let dz = abs(p.z) / a.w;
    let rho = length(vec2<f32>(dy, dz));
    let ph = atan2(dz, -dy);
    let aa = max(px, 0.003);
    let n1 = vn3(p / 0.8) - 0.5;
    let n2 = vn3(p / 0.25) - 0.5;
    let n3 = vn3(p / 0.07) - 0.5;
    let s = (5.0000 - p.x) / 14.0;
    let wn = 1.0 + n3 * 0.1 * (1.0 - smoothstep(0.02, 0.08, px));
    let WH = vec3<f32>(0.6, 0.61, 0.62) * wn;
    let GR = vec3<f32>(0.17, 0.18, 0.19) * wn;
    // (the back: matte, not flat -- broad mottle, a little paler down the flanks, and pale SCARS: thin streaks,
    // mostly lengthwise, here and there)
    let n0 = vn3(p / 2.2) - 0.5;
    var dark = col * (1.0 + n0 * 0.35 + n1 * 0.2 + n2 * 0.1) * wn * mix(1.18, 0.92, smoothstep(1.4, 2.9, ph));
    let sn = vn3(vec3<f32>(p.x / 3.0, p.y / 0.1, p.z / 0.1));
    let scar = (1.0 - smoothstep(0.006, 0.006 + aa * 0.5, abs(sn - 0.5))) * smoothstep(0.22, 0.27, vn3(p / 1.3 + 7.0) - 0.5) * (1.0 - smoothstep(0.03, 0.1, px)) * smoothstep(0.22, 0.3, s);
    dark = mix(dark, vec3<f32>(0.36, 0.37, 0.38) * wn, scar * 0.5);
    // (the belly's white, its edge wandering; grey blotches in it, white flecks over it)
    var phw = mix(0.8, 1.3, smoothstep(0.04, 0.3, s));
    phw = mix(phw, 0.42, smoothstep(0.46, 0.78, s));
    phw = mix(phw, -0.6, smoothstep(0.84, 0.93, s));
    let wv = (ph - phw + n1 * 0.5 + n2 * 0.12) * a.z;
    var white = 1.0 - smoothstep(-aa, aa, wv);
    white = max(white, smoothstep(0.4, 0.43, n3 + n2 * 0.2) * (1.0 - smoothstep(0.0, 0.25, wv)));
    let blot = smoothstep(0.24, 0.27, n2 + n3 * 0.3) * 0.55;
    var o = mix(dark, mix(WH, GR, blot), white);
    // (the throat pleats: grooves from the chin to the navel)
    let phP = 1.3 * sqrt(clamp(s / 0.05, 0.0, 1.0)) * pow(clamp((0.5200 - s) / 0.3, 0.0, 1.0), 0.6);
    let u = ph / max(phP, 0.001);
    let k = fract(u * 15.0);
    let dg = min(k, 1.0 - k) / 15.0 * phP * a.z;
    let g = (1.0 - smoothstep(0.012, 0.012 + aa, dg)) * (1.0 - smoothstep(0.85, 1.0, u)) * step(0.004, s) * (1.0 - smoothstep(0.03, 0.08, px));
    o = o * (1.0 - 0.6 * g);
    // (the flippers: white, mottled, dark at the root)
    let fp = smoothstep(1.06, 1.2, rho) * step(p.y, a.y) * step(p.x, 1.6400) * step(-3.6800, p.x);
    let fm = smoothstep(0.17, 0.21, n2 + n3 * 0.4) * 0.65;
    let fw = mix(WH, GR, fm);
    o = mix(o, mix(dark, fw, smoothstep(1.15, 1.45, rho)), fp);
    // (the flukes: below their mid-plane, white inside a black margin, blotched -- only out on the blades, past the
    // local stock's half width (AX), so the stock and the flukes' root stay dark all round)
    let fl = step(p.x, -8.1100);
    let under = (1.0 - smoothstep(-aa, aa, p.y - 0.0300)) * smoothstep(2.0, 4.5, dz);
    let fwh = under * (1.0 - smoothstep(-aa, aa, humpFluke(vec2<f32>(p.x, abs(p.z))) + n2 * 0.12)) * (1.0 - smoothstep(0.07, 0.1, n1 + n2 * 0.6));
    o = mix(o, mix(dark, WH, fwh), fl);
    // (the mouth line: a dark crease from the tip of the jaw to its corner under the eye)
    var LP = array<vec2<f32>, 9>(vec2<f32>(5.0000, -0.4800), vec2<f32>(4.5800, -0.4200), vec2<f32>(4.0200, -0.3100), vec2<f32>(3.4600, -0.2000), vec2<f32>(2.9000, -0.1000), vec2<f32>(2.5500, -0.0800), vec2<f32>(2.3400, -0.1600), vec2<f32>(2.2000, -0.3000), vec2<f32>(2.1020, -0.4200));
    var ly = LP[0].y;
    for (var i = 0; i < 8; i++) {
      if (p.x <= LP[i].x && p.x >= LP[i + 1].x) { ly = mix(LP[i].y, LP[i + 1].y, (LP[i].x - p.x) / (LP[i].x - LP[i + 1].x)); }
    }
    let ml = (1.0 - smoothstep(0.012, 0.012 + aa, abs(p.y - ly))) * step(LP[8].x, p.x) * step(p.x, LP[0].x + 0.05);
    o = mix(o, col * 0.4, ml);
    return o;
  }
`, [vn3, humpFluke]);
// 43 PLESIO (2026-11-06, a plesiosaur's skin: assets/creatures/sea/plesiosaurus.json, its generator scratchpad
// sc/sea3/gen/plesio.py), SOLID: the rest pose's own space, metres. COUNTERSHADED: the painted back colour over the
// body's mid-height (y -0.03, rising with the neck's curve; out on a flipper its mid-plane -- the tops dark, the undersides pale), the
// pale belly under it, the line wandering a little; the back finely blotched darker, the belly faintly; a fine pebbled
// skin (faded once a pixel is wider than a pebble)
const plesioOf = wgslFn(`
  fn plesioOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    let aa = max(px, 0.0015);
    let n1 = vn3(p / 0.09) - 0.5;
    let n2 = vn3(p / 0.025) - 0.5;
    let pb = vn3(p / 0.004) - 0.5;
    // (the line: the body's mid-height, rising along the neck's upward curve; out on a flipper, its mid-plane, which
    // rests angled down)
    let yc = 0.22 * pow(clamp((p.x - 0.05) / 1.41, 0.0, 1.0), 1.5) - 0.03;
    let bw = 0.58 * sqrt(max(0.0, 1.0 - pow((p.x + 0.36) / 0.75, 2.0)));
    let onf = smoothstep(bw * 0.8, bw * 0.8 + 0.05, abs(p.z)) * step(p.x, 0.25);
    let lv = mix(yc, -0.11 - 0.18 * max(0.0, abs(p.z) - 0.35), onf);
    let cut = p.y - lv + n1 * 0.02 + n2 * 0.006;
    let up = smoothstep(-aa - 0.006, aa + 0.006, cut);
    let BL = vec3<f32>(0.56, 0.52, 0.38);
    let blot = smoothstep(0.16, 0.24, n1 + n2 * 0.35);
    let back = col * (1.0 - 0.22 * blot) * (1.0 + n2 * 0.15);
    let belly = BL * (1.0 - 0.08 * blot);
    let fine = 1.0 + pb * 0.16 * (1.0 - smoothstep(0.002, 0.008, px));
    return mix(belly, back, up) * fine;
  }
`, [vn3]);// the coat at a pixel: id the pattern, p4 its point (xyz) and radius (w), q4 a feather's numbers, px its footprint
// a European BADGER's coat (44, 2026-11-06: assets/creatures/mammals/badger.json, gen scratchpad sc/must/badger.py),
// SOLID: the rest pose's own space, metres. THE FACE round the head's axis: knots along x (K: x, the axis's height, the
// white blaze's half-angle and the black stripe's lower edge; Q: the white cheek's lower edge and how much of the face
// there is -- 1 on the head, 0 on the neck behind it), each point's angle from the top round that axis -- a white blaze up
// the middle, a black stripe either side from beside the nose pad over the eye and the ear (its rim white) to the neck,
// white cheeks and upper lip under it, the chin and throat black: every edge antialiased by the pixel and sharp as a
// badger's are. THE BODY coarse grizzled grey -- long guard hairs, pale tips and dark bands (hairOf) -- going black under
// a line along the flank (KB: x, its height): the legs, the chest between them, the belly
const badgerOf = wgslFn(`
  fn badgerOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    var K = array<vec4<f32>, 11>(vec4<f32>(0.44, 0.131, 18.0, 18.0), vec4<f32>(0.416, 0.134, 20.0, 40.0), vec4<f32>(0.39, 0.141, 25.0, 64.0), vec4<f32>(0.355, 0.152, 31.0, 84.0), vec4<f32>(0.325, 0.162, 35.0, 93.0), vec4<f32>(0.292, 0.169, 37.0, 98.0), vec4<f32>(0.262, 0.172, 37.0, 100.0), vec4<f32>(0.232, 0.176, 35.0, 99.0), vec4<f32>(0.2, 0.182, 29.0, 96.0), vec4<f32>(0.165, 0.188, 23.0, 92.0), vec4<f32>(0.13, 0.193, 18.0, 88.0));
    var Q = array<vec2<f32>, 11>(vec2<f32>(125.0, 1.0), vec2<f32>(128.0, 1.0), vec2<f32>(132.0, 1.0), vec2<f32>(136.0, 1.0), vec2<f32>(140.0, 1.0), vec2<f32>(145.0, 1.0), vec2<f32>(150.0, 1.0), vec2<f32>(134.0, 1.0), vec2<f32>(106.0, 0.6), vec2<f32>(93.0, 0.2), vec2<f32>(88.0, 0.0));
    var KB = array<vec2<f32>, 8>(vec2<f32>(0.26, 0.122), vec2<f32>(0.2, 0.15), vec2<f32>(0.13, 0.158), vec2<f32>(0.05, 0.138),
      vec2<f32>(-0.1, 0.13), vec2<f32>(-0.2, 0.14), vec2<f32>(-0.3, 0.15), vec2<f32>(-0.4, 0.17));
    var k = K[10];
    var q = vec2<f32>(Q[10].x, 0.0);
    // (behind the ears the face's edge looked up a little ragged -- fur, not a painted line)
    let xq = p.x + (vn3(p / 0.02) - 0.5) * 0.02 * (1.0 - smoothstep(0.2, 0.25, p.x));
    if (xq > K[0].x) { k = K[0]; q = Q[0]; }
    for (var i = 0; i < 10; i++) {
      if (xq <= K[i].x && xq >= K[i + 1].x) {
        let t = (K[i].x - xq) / (K[i].x - K[i + 1].x);
        k = mix(K[i], K[i + 1], t); q = mix(Q[i], Q[i + 1], t);
      }
    }
    var yb = KB[7].y;
    if (p.x > KB[0].x) { yb = KB[0].y; }
    for (var i = 0; i < 7; i++) {
      if (p.x <= KB[i].x && p.x >= KB[i + 1].x) { yb = mix(KB[i].y, KB[i + 1].y, (KB[i].x - p.x) / (KB[i].x - KB[i + 1].x)); }
    }
    let wn = vn3(p / 0.005) - 0.5;
    let aa = max(px, 0.0008);
    let hq = vec2<f32>(abs(p.z), p.y - k.y);
    let rl = length(hq);
    let phi = degrees(atan2(hq.x, hq.y));
    let d1 = radians(phi - k.z) * rl + wn * 0.0012;
    let d2 = radians(phi - k.w) * rl + wn * 0.0012;
    let d3 = radians(phi - q.x) * rl + wn * 0.0012;
    var black = smoothstep(-aa, aa, d1) * (1.0 - smoothstep(-aa, aa, d2));
    black = max(black, smoothstep(-aa, aa, d3));
    // (the ear: in the stripe, its upper rim white)
    let ear = step(0.04, abs(p.z)) * step(0.196, p.y) * step(0.245, p.x) * step(p.x, 0.29);
    black = mix(black, 1.0 - smoothstep(0.2232 - aa, 0.2232 + aa, p.y + wn * 0.001), ear);
    let face = q.y;
    let low = (1.0 - smoothstep(yb - 0.012, yb + 0.012, p.y + wn * 0.01)) * (1.0 - face * smoothstep(0.17, 0.21, p.x));
    let blk = vec3<f32>(0.011, 0.01, 0.009);
    let wc = vec3<f32>(0.78, 0.77, 0.73) * (0.95 + 0.1 * wn);
    let fc = mix(wc, blk, black);
    let o = mix(mix(col, fc, face), blk, low);
    let dark = max(low, face * black);
    let pale = face * (1.0 - black);
    let legs = (1.0 - smoothstep(0.1, 0.15, p.y)) * (1.0 - smoothstep(0.2, 0.26, p.x));
    let fh = smoothstep(0.14, 0.235, p.x);   // (the hair's length by x alone: the ragged edge above would curdle it)
    let L = mix(0.04, 0.009, fh);
    let W = mix(0.0019, 0.0009, fh);
    let f = hairOf(o, p, px, L, W, 0.0, 0.016 * dark, legs);
    // THE GRIZZLE: each guard hair's silver tip over its dark base -- strands up close, their mean (a silver-grey) when
    // too fine to draw; the tips denser down the flanks, sparser along the spine (darker there)
    let gz = (1.0 - dark) * (1.0 - face);
    let sp = smoothstep(yb + 0.08, yb + 0.17, p.y);
    // (the tips: hairOf's own strands, drawn on black -- what comes back is its tip mask x .035; a second set of
    // strands, offset, on the flanks only)
    let m1 = hairOf(vec3<f32>(0.0), p, px, L, W, 1.0, 0.0, legs).x / 0.035;
    let m2 = hairOf(vec3<f32>(0.0), p + vec3<f32>(0.37, 0.11, 0.23) * L, px, L, W, 1.0, 0.0, legs).x / 0.035;
    // (and the guard hair lying in locks a centimetre or two long, so the grizzle shows as a fine mottle from further off)
    let cq = vec3<f32>(p.x / 0.011, (0.8 * p.y + 0.6 * p.z) / 0.0045, (0.8 * p.z - 0.6 * p.y) / 0.0045);   // (turned off the noise's grid)
    let clump = smoothstep(0.2, 0.8, vn3(cq + vec3<f32>(3.0, 1.0, 8.0) + (vn3(cq * 0.37) - 0.5) * 2.5));
    let tip = clamp(max(m1, m2 * (1.0 - sp)) * 1.3, 0.0, 1.0) * (0.7 + 0.5 * clump);
    let cov = mix(0.32, 0.15, sp) * (0.7 + 0.6 * clump);
    let res = 1.0 - smoothstep(0.35, 1.0, px / W);
    let silver = vec3<f32>(0.5, 0.49, 0.46) * (0.92 + 0.16 * wn);
    let gr = mix(f, silver, gz * (tip + cov * (1.0 - res)));
    return mix(gr, mix(o, gr, 0.4), pale);
  }
`, [vn3, hairOf]);
// a least WEASEL's coat (45, 2026-11-06: assets/creatures/mammals/weasel.json, gen scratchpad sc/must/weasel.py),
// SOLID, in the rest pose's own space (metres): russet-brown above, white below -- the upper lip, chin, throat, chest and
// belly -- the line between them a crisp edge round the body's axis (K: x, the axis's height, the line's angle from the
// top), wavering a little along the flank as a weasel's does; the legs brown; short fine fur (hairOf) over all of it
const weaselOf = wgslFn(`
  fn weaselOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    var K = array<vec3<f32>, 10>(vec3<f32>(0.106, 0.0435, 100.0), vec3<f32>(0.096, 0.046, 104.0), vec3<f32>(0.086, 0.049, 100.0),
      vec3<f32>(0.074, 0.049, 96.0), vec3<f32>(0.06, 0.046, 98.0), vec3<f32>(0.04, 0.042, 104.0), vec3<f32>(0.015, 0.04, 116.0),
      vec3<f32>(-0.02, 0.041, 126.0), vec3<f32>(-0.06, 0.042, 140.0), vec3<f32>(-0.09, 0.044, 185.0));
    var k = K[9];
    if (p.x > K[0].x) { k = K[0]; }
    for (var i = 0; i < 9; i++) {
      if (p.x <= K[i].x && p.x >= K[i + 1].x) { k = mix(K[i], K[i + 1], (K[i].x - p.x) / (K[i].x - K[i + 1].x)); }
    }
    let wn = vn3(p / 0.0015) - 0.5;
    let wave = vn3(vec3<f32>(p.x / 0.009, 3.1, 7.3)) - 0.5;
    let aa = max(px, 0.00025);
    let hq = vec2<f32>(abs(p.z), p.y - k.y);
    let rl = length(hq);
    let phi = degrees(atan2(hq.x, hq.y));
    let d = radians(k.z + wave * 14.0 - phi) * rl + wn * 0.00035;
    let legs = 1.0 - smoothstep(0.016, 0.024, p.y);
    let white = (1.0 - smoothstep(-aa, aa, d)) * (1.0 - legs);
    let wc = vec3<f32>(0.8, 0.77, 0.69) * (0.96 + 0.08 * wn);
    // (the brown darker down the back, a little paler and warmer toward the line on the flanks)
    let tone = mix(vec3<f32>(0.8, 0.78, 0.76), vec3<f32>(1.1, 1.06, 1.0), smoothstep(15.0, k.z, phi)) * (0.95 + 0.1 * (vn3(p / 0.008) - 0.5));
    let o = mix(col * tone, wc, white);
    let f = hairOf(o, p, px, 0.0065, 0.00045, 0.0, 0.0, legs);
    return mix(f, mix(o, f, 0.5), white);
  }
`, [vn3, hairOf]);
// 46 DAPPLE (a dapple grey's, 2026-11-06): round pale dapples, soft-edged, in a net of the coat's own darker grey --
// cells about 7.5 cm, in the rest pose's own metres; finer than the pixels, the coat's own colour
const dappleOf = wgslFn(`
  fn dappleOf(col: vec3<f32>, p: vec3<f32>, px: f32) -> vec3<f32> {
    let q = p / 0.075;
    let c = vor3(q);
    let h = hash33(floor(c.xyz * 7.31));
    let rr = 0.33 + 0.14 * h.x;
    let soft = 0.1 + px / 0.075;
    let fade = 1.0 - smoothstep(0.3, 0.8, px / 0.03);
    let m = (1.0 - smoothstep(rr - soft, rr + soft, length(q - c.xyz))) * fade;
    let pale = min(col * 1.4 + vec3<f32>(0.03), vec3<f32>(1.0));
    return mix(mix(col, col * 0.8, fade), pale, m * 0.9);
  }
`, [vor3, hash33]);
// 47 PINTO (a piebald horse's, 2026-11-06): big patches with crisp wandering edges, near black over the coat (its white)
// -- noise at three sizes, the largest about 40 cm, cut at one level; in the rest pose's own metres
const pintoOf = wgslFn(`
  fn pintoOf(col: vec3<f32>, p: vec3<f32>, px: f32) -> vec3<f32> {
    let n = vn3(p / 0.42) * 0.62 + vn3(p / 0.13 + vec3<f32>(3.1)) * 0.28 + vn3(p / 0.045 + vec3<f32>(7.7)) * 0.1;
    let aa = px / 0.25 + 0.008;
    return mix(col, vec3<f32>(0.024, 0.02, 0.017), smoothstep(0.56 - aa, 0.56 + aa, n));
  }
`, [vn3]);
// 60 SEAL / 61 GREYSEAL (2026-11-06, a harbour seal's and a grey seal's coats: assets/creatures/sea/seal.json, its
// generator scratchpad sc/sea3/gen/seal.py), SOLID: the rest pose's own space, metres (x forward, the body's axis at y 0).
// COUNTERSHADED: the coat's own colour above, a pale silvery belly under a wandering line along the lower flank (a
// little higher on the head: the chin and throat pale). A harbour seal's (60): dense small DARK SPOTS over the back
// (cells ~3.6 cm, ~2.2 cm on the head), the back's middle darker, some in a pale ring, the belly's spots fewer and fainter; a grey seal's (61):
// big irregular BLOTCHES instead -- pale on a dark coat (a bull), dark on a pale one (a cow). Fur-fine noise over all;
// the marks fade once a pixel is wider than they are
const sealSpots = wgslFn(`
  fn sealSpots(q: vec3<f32>, px: f32, dens: f32) -> vec2<f32> {
    let c = vor3(q);
    let h = hash33(floor(c.xyz * 5.71));
    let rr = 0.2 + 0.2 * h.y;
    let d = length(q - c.xyz);
    let aa = 0.06 + px;
    let on = step(h.x, dens);
    let spot = (1.0 - smoothstep(rr - aa, rr + aa, d)) * on;
    let ring = (1.0 - smoothstep(rr * 1.75 - aa, rr * 1.75 + aa, d)) * (1.0 - spot) * on * step(0.62, h.z);
    return vec2<f32>(spot, ring);
  }
`, [vor3, hash33]);
const sealOf = wgslFn(`
  fn sealOf(col: vec3<f32>, p: vec3<f32>, px: f32, grey: f32) -> vec3<f32> {
    let n1 = vn3(p / 0.11) - 0.5;
    let n2 = vn3(p / 0.03 + vec3<f32>(4.1)) - 0.5;
    // (the line: low on the flank, a little higher toward the head; the chin and throat pale)
    let head = smoothstep(0.42, 0.6, p.x);
    let lv = mix(-0.085, -0.035, head) + n1 * 0.05 + n2 * 0.012;
    let aa = max(px, 0.004);
    let up = smoothstep(lv - aa - 0.025, lv + aa + 0.025, p.y);
    let pale = min(col * 1.8 + vec3<f32>(0.1, 0.1, 0.095), vec3<f32>(0.62, 0.61, 0.58));
    let dors = smoothstep(0.05, 0.17, p.y + n1 * 0.05) * (1.0 - head * 0.5);
    var base = mix(pale, col * (1.0 - 0.24 * dors), up) * (1.0 + n2 * 0.18);
    // (the marks, warped so they are not round)
    let wp = p + vec3<f32>(vn3(p / 0.05), vn3(p / 0.05 + vec3<f32>(7.3)), vn3(p / 0.05 + vec3<f32>(2.9))) * 0.03;
    if (grey < 0.5) {
      let fadeA = 1.0 - smoothstep(0.003, 0.01, px);
      let fadeB = 1.0 - smoothstep(0.002, 0.006, px);
      let a = sealSpots(wp / 0.036, px / 0.036, mix(0.45, 0.82, up));
      let b = sealSpots(wp / 0.022 + vec3<f32>(11.0), px / 0.022, 0.75);
      let s = mix(a, b, head);
      let fade = mix(fadeA, fadeB, head);
      let dark = mix(base * 0.62, col * 0.36, up);
      base = mix(base, min(base * 1.28 + vec3<f32>(0.015), vec3<f32>(0.8)), s.y * 0.55 * fade);
      return mix(base, dark, s.x * fade * mix(0.7, 0.95, up));
    }
    let m = vn3(wp / 0.08) * 0.6 + vn3(wp / 0.028 + vec3<f32>(3.3)) * 0.28 + vn3(wp / 0.011 + vec3<f32>(9.1)) * 0.12;
    let fade = 1.0 - smoothstep(0.01, 0.03, px);
    let k = smoothstep(0.55, 0.6, m) * fade;
    let lum = dot(col, vec3<f32>(0.3, 0.5, 0.2));
    let mark = select(col * 0.34, min(col * 2.1 + vec3<f32>(0.05), vec3<f32>(0.7)), lum < 0.12);
    return mix(base, mix(mark, mark * 0.8 + pale * 0.2, 1.0 - up), k * 0.9);
  }
`, [vn3, sealSpots]);
// 62 WALRUS (2026-11-06, a walrus bull's hide: assets/creatures/sea/walrus.json, its generator scratchpad
// sc/sea3/gen/walrus.py), SOLID: the rest pose's own space, metres (x forward, the body's axis at y 0). Cinnamon brown,
// darker along the back, PINKER low down and over the neck and chest (the blood in the skin of a walrus warm on land);
// WRINKLED: deep creases across the neck and shoulders (rings ~6 cm apart, wandering) and a net of finer ones over the
// rest, each with a paler ridge beside it; the flippers' bare soles darker; a sparse stipple of short hairs. The
// creases fade once a pixel is wider than they are
const walrusOf = wgslFn(`
  fn walrusOf(col: vec3<f32>, p: vec3<f32>, px: f32) -> vec3<f32> {
    let n1 = vn3(p / 0.3) - 0.5;
    let n2 = vn3(p / 0.07 + vec3<f32>(5.3)) - 0.5;
    let n3 = vn3(p / 0.018 + vec3<f32>(1.7)) - 0.5;
    let low = 1.0 - smoothstep(-0.25, 0.25, p.y + n1 * 0.2);
    let neck = smoothstep(0.55, 0.72, p.x) * (1.0 - smoothstep(1.06, 1.14, p.x));
    let pink = col * vec3<f32>(1.25, 0.95, 0.95) + vec3<f32>(0.035, 0.008, 0.01);
    var c = mix(col * (0.82 + 0.25 * n1), pink, clamp(low * 0.45 + neck * 0.3 + n1 * 0.25, 0.0, 1.0));
    // (the flippers' soles and the stub: darker, greyer)
    let sole = smoothstep(0.44, 0.5, abs(p.z)) * (1.0 - smoothstep(-0.47, -0.4, p.y)) + 1.0 - smoothstep(-1.36, -1.3, p.x);
    c = mix(c, col * vec3<f32>(0.6, 0.62, 0.66), clamp(sole, 0.0, 1.0) * 0.75);
    // (the creases: rings across the neck and shoulders, a net elsewhere; a ridge's paler side beside each)
    let ang = atan2(p.z, p.y);
    let s = (p.x + 0.035 * sin(ang * 2.3 + n1 * 5.0) + n2 * 0.08) / 0.06;
    let f = abs(fract(s) - 0.5) * 2.0;
    let aR = px / 0.06;
    let ring = smoothstep(0.78 - aR, 0.94, f) * smoothstep(0.38, 0.6, vn3(p / 0.14 + vec3<f32>(2.2)));
    let ridge = smoothstep(0.45, 0.6, f) * (1.0 - smoothstep(0.62, 0.76, f));
    let v = vor3(p / 0.06 + vec3<f32>(n3 * 0.4));
    let aN = px / 0.06;
    let net = 1.0 - smoothstep(0.02, 0.06 + aN, v.w);
    let fade = 1.0 - smoothstep(0.006, 0.02, px);
    let crease = mix(net * 0.35, ring * 0.6, neck) * fade;
    c = c * (1.0 + 0.1 * ridge * neck * fade) * (1.0 - 0.42 * crease);
    // (sparse short hairs: a fine stipple, gone at a distance)
    let h = smoothstep(0.32, 0.45, n3) * (1.0 - smoothstep(0.002, 0.006, px));
    return c * (1.0 + 0.12 * h) * (1.0 + n2 * 0.1);
  }
`, [vn3, vor3]);
// 63 LYNX (2026-11-06, a Eurasian lynx's spots: assets/creatures/mammals/lynx.json, its generator scratchpad sc/m5/lynx.py),
// SOLID, at the body's patScale (1: metres -- x forward, y up from the ground): solid dark spots of DIFFERENT sizes in
// three scattered layers -- a fine sprinkle (~8 mm) everywhere, densest low (the legs and flanks), middling ones
// (~1.5 cm) on the body and legs, and the largest (~2.5 cm: medium-small, not a leopard's blotches) on the flanks,
// haunches and legs (below the back's line, behind the neck); none of them on the head beyond the fine. Which spots are kept is decided at each spot's CENTRE (lynxSpots: spotsOf's jittered grid, returning
// the centre too), so a spot is whole or absent, never cut along a line. A slightly wobbled edge; faded to their
// average once a pixel is wider than the spot
const lynxSpots = wgslFn(`
  fn lynxSpots(p: vec3<f32>, S: vec3<f32>, R: f32, px: f32, seed: f32) -> vec4<f32> {
    let sv = vec3<f32>(seed, seed * 1.7, seed * 2.3);
    let q = p / S + sv;
    let c = vor3(q);
    let h = hash33(floor(c.xyz * 7.31) + vec3<f32>(seed, 1.0, 2.0));
    let rr = R * (0.75 + 0.5 * h.y);
    let d = length(q - c.xyz);
    let aa = px / min(S.x, min(S.y, S.z)) + 0.02;
    let fade = 1.0 - smoothstep(0.35, 0.8, px / (min(S.x, min(S.y, S.z)) * R));
    let ctr = (c.xyz - sv) * S;
    return vec4<f32>((1.0 - smoothstep(rr - aa, rr + aa, d)) * fade, h.x, ctr.x, ctr.y);
  }
`, [vor3, hash33]);
const lynxOf = wgslFn(`
  fn lynxOf(col: vec3<f32>, p: vec3<f32>, px: f32) -> vec3<f32> {
    let w = vec3<f32>(vn3(p / 0.03) - 0.5, vn3(p / 0.03 + vec3<f32>(4.1)) - 0.5, 0.0) * 0.006;
    let q = p + w;
    let a = lynxSpots(q, vec3<f32>(0.016), 0.26, px, 4.0);
    let b = lynxSpots(q, vec3<f32>(0.027, 0.025, 0.027), 0.28, px, 9.0);
    let c = lynxSpots(q, vec3<f32>(0.04, 0.036, 0.04), 0.3, px, 13.0);
    let lowA = 1.0 - smoothstep(0.5, 0.6, a.w);
    let bodyB = 1.0 - smoothstep(0.38, 0.46, b.z);
    let lowC = (1.0 - smoothstep(0.54, 0.64, c.w)) * (1.0 - smoothstep(0.38, 0.46, c.z));
    let m = max(max(a.x * step(a.y, 0.5 + 0.38 * lowA), b.x * step(b.y, 0.7 * bodyB)), c.x * step(c.y, 0.62 * lowC));
    return mix(col, col * vec3<f32>(0.24, 0.19, 0.15), m * 0.92);
  }
`, [vn3, lynxSpots]);
// 64 PANDA / 65 QINLING (2026-11-06, a giant panda's markings: assets/creatures/mammals/giantpanda.json, its generator
// scratchpad sc/m5/giantpanda.py prints these numbers), SOLID: the rest pose's own space, metres. Two ellipsoids, each
// its centre and the rows of its inverse frame (u = M (p - c): inside where |u| < 1) -- the EYE PATCHES (mirrored:
// |z|), big ovals slanting down and out round the eyes, and the SHOULDER BAND right round the trunk; black there (65:
// the Qinling panda's brown). Per pixel, the edge antialiased by the pixel and softened a little (fur): laid as paints
// the near mesh's vertices tore them into grey shards. The legs and ears are black shapes of their own
const pandaEll = wgslFn(`
  fn pandaEll(p: vec3<f32>, c: vec3<f32>, r0: vec3<f32>, r1: vec3<f32>, r2: vec3<f32>, soft: f32, px: f32) -> f32 {
    let q = p - c;
    let u = vec3<f32>(dot(r0, q), dot(r1, q), dot(r2, q));
    let l = max(length(u), 1e-4);
    let g = max(length(r0 * (u.x / l) + r1 * (u.y / l) + r2 * (u.z / l)), 1e-3);
    let d = (l - 1.0) / g;
    let w = soft + px;
    return 1.0 - smoothstep(-w, w, d);
  }
`);
const pandaOf = wgslFn(`
  fn pandaOf(col: vec3<f32>, p: vec3<f32>, px: f32, brown: f32) -> vec3<f32> {
    let pm = vec3<f32>(p.x, p.y, abs(p.z));
    let eye = pandaEll(pm, vec3<f32>(0.8432, 0.6417, 0.0657), vec3<f32>(17.044, -3.097, -4.591), vec3<f32>(0.0, 11.939, -8.053),
                       vec3<f32>(8.307, 14.296, 21.195), 0.003, px);
    let band = pandaEll(p, vec3<f32>(0.31, 0.5084, 0.0), vec3<f32>(7.986, -1.122, 0.0), vec3<f32>(0.374, 2.662, 0.0),
                        vec3<f32>(0.0, 0.0, 2.688), 0.008, px);
    let dark = mix(vec3<f32>(0.0083, 0.0066, 0.005), vec3<f32>(0.069, 0.034, 0.02), brown);
    return mix(col, dark, max(eye, band));
  }
`, [pandaEll]);
// 66 KOI (2026-11-07, a kohaku's: assets/creatures/sea/carp.json, its `koi` coat): big RED PATCHES with crisp wandering
// edges over the coat's white, mostly along the back and the upper flank (the belly stays white), then the row scales
// over all (32: each scale's back edge rimmed) -- in the rowscales' frame (r its size)
const koiOf = wgslFn(`
  fn koiOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    let q = p / r;
    let n = vn3(q / 0.26 + vec3<f32>(4.3)) * 0.72 + vn3(q / 0.09 + vec3<f32>(9.1)) * 0.28 + 0.12 * smoothstep(-0.25, 0.3, q.y);
    let aa = px / (r * 0.08) + 0.01;
    let m = smoothstep(0.6 - aa, 0.6 + aa, n) * smoothstep(-0.2, -0.02, q.y);
    return rowscalesOf(mix(col, vec3<f32>(0.62, 0.045, 0.012), m * 0.97), p, r, px);
  }
`, [vn3, rowscalesOf]);
// 67 RAINBOW (2026-11-07, a rainbow trout's: assets/creatures/sea/trout.json, its `rainbow` coat): small BLACK SPOTS,
// dense over the back and sparse below, and a broad PINK BAND along the flank's middle (no red spots, no pale halos)
const rainbowOf = wgslFn(`
  fn rainbowOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    let yn = p.y / r;
    let b = spotsOf(p, vec3<f32>(0.2) * r, 0.2, px, 3.0);
    let kb = step(b.y, mix(0.06, 0.9, smoothstep(-0.5, 0.45, yn)));
    let band = 1.0 - smoothstep(0.06, 0.3, abs(yn + 0.04));
    let o = mix(col, vec3<f32>(0.6, 0.12, 0.13), band * 0.62);
    return mix(o, vec3<f32>(0.02, 0.017, 0.014), b.x * kb * 0.95);
  }
`, [spotsOf]);
// 68 NARWHAL (2026-11-07, a narwhal's mottling: assets/creatures/sea/narwhal.json, its generator
// tools/creaturegen/sc/sea3/gen/narwhal.py; this block wgsl_narwhal.py), in the rest pose's own space, metres (the asset
// lays it in a frame that is that space). Round the body's axis (AX: x, the axis's height, half height, half width) each
// point has its ELLIPTIC ANGLE from the belly's midline (0) to the spine (pi):
//   the GROUND the painted colour, the belly paler and creamier under the flanks' mid-line (its edge wandering);
//   the BLOTCHES dark grey-brown, irregular (noise at three sizes, warped), near solid along the back with pale flecks
//   in it, spotting the flanks, few and small on the belly; darker and denser over the head's top and the tail stock;
//   the AGE from the ground's own brightness: a pale ground (an old male) fewer, smaller blotches; a dark grey ground
//   (a calf) none at all -- plain grey, the belly a shade paler;
//   the MOUTH LINE (LP): a short dark crease at the jaw's height, from its front to the corner, dipping a shade and
//   fainter across the front.
// The blotches fade into their average once a pixel is wider than they are.
const narwhalOf = wgslFn(`
  fn narwhalOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {
    var AX = array<vec4<f32>, 20>(vec4<f32>(1.9000, -0.0600, 0.0460, 0.0500), vec4<f32>(1.8460, -0.0500, 0.1260, 0.1300), vec4<f32>(1.7650, -0.0400, 0.1960, 0.2000), vec4<f32>(1.6520, -0.0300, 0.2530, 0.2550), vec4<f32>(1.5170, -0.0225, 0.2925, 0.2910), vec4<f32>(1.3600, -0.0200, 0.3200, 0.3140), vec4<f32>(1.2020, -0.0225, 0.3475, 0.3370), vec4<f32>(1.0000, -0.0250, 0.3950, 0.3830), vec4<f32>(0.7300, -0.0200, 0.4500, 0.4380), vec4<f32>(0.4600, -0.0125, 0.4875, 0.4770), vec4<f32>(0.1450, -0.0050, 0.5000, 0.4880), vec4<f32>(-0.1700, 0.0025, 0.4825, 0.4690), vec4<f32>(-0.5300, 0.0100, 0.4300, 0.4150), vec4<f32>(-0.8900, 0.0150, 0.3550, 0.3400), vec4<f32>(-1.2500, 0.0175, 0.2725, 0.2530), vec4<f32>(-1.6100, 0.0200, 0.1900, 0.1660), vec4<f32>(-1.9250, 0.0200, 0.1250, 0.1070), vec4<f32>(-2.1500, 0.0175, 0.0875, 0.0770), vec4<f32>(-2.2630, 0.0115, 0.0585, 0.0546), vec4<f32>(-2.3520, 0.0090, 0.0328, 0.0340));
    var a = AX[19];
    if (p.x >= AX[0].x) { a = AX[0]; }
    for (var i = 0; i < 19; i++) {
      if (p.x <= AX[i].x && p.x >= AX[i + 1].x) { a = mix(AX[i], AX[i + 1], (AX[i].x - p.x) / (AX[i].x - AX[i + 1].x)); }
    }
    let dy = (p.y - a.y) / a.z;
    let dz = abs(p.z) / a.w;
    let ph = atan2(dz, -dy);
    let aa = max(px, 0.002);
    let lum = dot(col, vec3<f32>(0.2126, 0.7152, 0.0722));
    let calf = 1.0 - smoothstep(0.26, 0.36, lum);
    let old = smoothstep(0.62, 0.78, lum);
    // (the noise, warped so the blotches are not round)
    let wp = p + (vec3<f32>(vn3(p / 0.06), vn3(p / 0.06 + vec3<f32>(7.3)), vn3(p / 0.06 + vec3<f32>(2.9))) - 0.5) * 0.04;
    let n0 = vn3(p / 0.5 + vec3<f32>(1.7)) - 0.5;
    let f1 = 1.0 - smoothstep(0.012, 0.03, px);
    let f2 = 1.0 - smoothstep(0.005, 0.012, px);
    let f3 = 1.0 - smoothstep(0.002, 0.005, px);
    let m = mix(0.5, vn3(wp / 0.038), f1) * 0.55 + mix(0.5, vn3(wp / 0.015 + vec3<f32>(3.3)), f2) * 0.32 + mix(0.5, vn3(wp / 0.0062 + vec3<f32>(9.1)), f3) * 0.13;
    // (the ground: the belly paler and creamier, its edge low on the flank and wandering)
    let bl = 1.0 - smoothstep(0.75, 1.35, ph + n0 * 0.5);
    let ground = mix(col, min(col * 1.1 + vec3<f32>(0.035, 0.032, 0.026), vec3<f32>(0.86, 0.84, 0.8)), bl);
    // (how much of the skin is dark: the threshold the noise must clear -- low on the back, high on the belly)
    var thr = mix(0.78, 0.55, smoothstep(0.85, 1.75, ph + n0 * 0.3));
    thr = mix(thr, 0.33, smoothstep(1.85, 2.6, ph + n0 * 0.3));
    thr = thr - 0.07 * smoothstep(1.6520, 1.8460, p.x) * smoothstep(1.2, 2.2, ph);   // (the head's top)
    thr = thr - 0.1 * smoothstep(1.2500, 2.2630, -p.x);   // (the stock)
    thr = thr + 0.13 * old + 0.08 * old * (1.0 - smoothstep(1.8, 2.6, ph));
    let w = 0.01 + (1.0 - f2) * 0.06 + (1.0 - f1) * 0.12;
    let k = smoothstep(thr - w, thr + w, m);
    let DK = vec3<f32>(0.0578, 0.0478, 0.0382) * (1.0 + n0 * 0.25);
    var o = mix(ground, DK * mix(1.0, 1.35, old), k * 0.96);
    // (the stock's end darkening into the flukes' colour, wholly so before the flukes' fairing comes out through the
    //  stock's surface -- the flukes, a mesh laid over the stock's end, carry this coat too, so the two meet in one colour)
    let FIN = mix(vec3<f32>(0.069, 0.054, 0.044), vec3<f32>(0.198, 0.167, 0.138), old);
    o = mix(o, FIN * (1.0 + n0 * 0.2), smoothstep(1.8800, 2.1500, -p.x));
    // (the mouth line)
    var LP = array<vec2<f32>, 5>(vec2<f32>(1.9100, -0.1680), vec2<f32>(1.8190, -0.1800), vec2<f32>(1.7290, -0.1860), vec2<f32>(1.6525, -0.1800), vec2<f32>(1.5940, -0.1660));
    var ly = LP[0].y;
    for (var i = 0; i < 4; i++) {
      if (p.x <= LP[i].x && p.x >= LP[i + 1].x) { ly = mix(LP[i].y, LP[i + 1].y, (LP[i].x - p.x) / (LP[i].x - LP[i + 1].x)); }
    }
    ly = ly - 0.018 * exp(-p.z * p.z / 0.0081);   // (dipping a little under the melon's front: a smile, not a slot)
    let ml = (1.0 - smoothstep(0.003, 0.003 + aa, abs(p.y - ly))) * smoothstep(LP[4].x, LP[4].x + 0.035, p.x) * step(p.x, LP[0].x + 0.08);
    // (a calf: plain grey, the belly a shade paler)
    o = mix(o, col * (1.0 + 0.16 * bl), calf);
    return mix(o, DK * 0.8, ml * mix(0.45, 0.75, smoothstep(0.04, 0.14, abs(p.z))));
  }
`, [vn3]);
// 70-74 LACERTA (2026-11-07, a common wall lizard's: assets/creatures/others/wall-lizard.json, its generator
// tools/creaturegen/sc/others/gen/walllizard.py): the markings laid round the body's axis (the frame: o on the trunk's
// axis at x .022, u toward the head) by the angle from the spine -- the back to ~47 deg, the pale dorsolateral stripe to
// ~58, the dark flank band to ~105, the pale lower stripe to ~116, the belly beyond (left to its paint) -- each edge
// wobbling along the body, each side its own dice; then the row scales over all (32, r their size). 70 a male's trunk
// (dark blotches netted over the back, the stripe broken, the band dark with pale spots in it, blue spots along the
// belly's edge), 71 a female's (a plain back, a thin dark line down the spine, the stripes and the band clean), 72 / 73
// the male's / the female's tail (no blue, its links' own frames), 74 a green-backed male's trunk (the belly blotched
// black too). The trunk's frame serves the head and the legs as well -- one pattern group, so no seam where they join:
// past x .049 the HEAD (lacertaHead: its crown shields' sutures, the dark temporal band, the pale upper lip and its
// labials, the mouth line, the pale chin), and away from the trunk's axis (the legs) a plain mottle. The markings fade
// where the body is thinner than ~1.5 mm (the tail's last half). In metres: a 20 cm lizard.
const lacertaSeg = wgslFn(`
  fn lacertaSeg(p: vec2<f32>, a: vec2<f32>, b: vec2<f32>) -> f32 {
    let pa = p - a; let ba = b - a;
    let t = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * t);
  }
`);
const lacertaHead = wgslFn(`
  fn lacertaHead(col: vec3<f32>, hx: f32, hy: f32, z: f32, px: f32, male: f32) -> vec3<f32> {
    // head-local: hx from the back of the skull (x .050) toward the snout, hy from y .009, z across
    let az = abs(z);
    let sd = select(0.0, 37.0, z < 0.0);
    let ph = degrees(atan2(az, hy));
    let pale = mix(col * 1.7, vec3<f32>(0.55, 0.5, 0.36), 0.45);
    var o = col;
    // the crown's shields: their sutures, thin dark lines on the flat top
    let q = vec2<f32>(hx, az * 0.0026 / max(0.0028 - 0.075 * hx, 0.0012));   // (the shields' plan fitted to the tapering crown)
    var d = 1.0;
    d = min(d, lacertaSeg(q, vec2<f32>(0.0004, 0.0), vec2<f32>(0.0046, 0.0)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0004, 0.0), vec2<f32>(0.0007, 0.0026)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0013, 0.0), vec2<f32>(0.0014, 0.0005)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0014, 0.0005), vec2<f32>(0.0031, 0.0004)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0031, 0.0004), vec2<f32>(0.0033, 0.0)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0046, 0.0), vec2<f32>(0.0048, 0.0012)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0048, 0.0012), vec2<f32>(0.0007, 0.0026)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0048, 0.0012), vec2<f32>(0.0094, 0.0007)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0094, 0.0007), vec2<f32>(0.0100, 0.0)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0048, 0.0012), vec2<f32>(0.0052, 0.0025)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0052, 0.0025), vec2<f32>(0.0099, 0.0019)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0099, 0.0019), vec2<f32>(0.0094, 0.0007)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0100, 0.0), vec2<f32>(0.0117, 0.0)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0099, 0.0019), vec2<f32>(0.0113, 0.0015)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0113, 0.0015), vec2<f32>(0.0117, 0.0)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0117, 0.0), vec2<f32>(0.0129, 0.0010)));
    d = min(d, lacertaSeg(q, vec2<f32>(0.0129, 0.0010), vec2<f32>(0.0140, 0.0)));
    let ytop = 0.0032 - 0.2126 * hx;   // (the crown cut: y .0120 at x .051, falling 12 deg)
    let top = smoothstep(ytop - 0.0010, ytop - 0.0005, hy);
    let w = 0.00004 + px * 0.6;
    o = mix(o, col * 0.62, (1.0 - smoothstep(w, w * 2.0, d)) * top * 0.75);
    // a few dark flecks over the crown (a male's)
    let fl = smoothstep(0.72, 0.75, vn3(vec3<f32>(hx / 0.0004, az / 0.0004, sd + 11.0))) * top * male;
    o = mix(o, col * 0.45, fl * 0.8);
    // the dark temporal band behind the eye to the ear and on to the neck's band; a male's broken by pale spots
    let ww = (vn3(vec3<f32>(hx / 0.0015, sd, 4.0)) - 0.5) * 10.0;
    let aa = degrees(px / 0.003) + 0.6;
    let tb = smoothstep(56.0 + ww - aa, 56.0 + ww + aa, ph) * (1.0 - smoothstep(98.0 + ww - aa, 98.0 + ww + aa, ph))
           * (1.0 - smoothstep(0.0066, 0.0080, hx + (ph - 77.0) * 0.00003));
    let cq = vec3<f32>(hx / 0.0012, hy / 0.0010, sd + 6.0);
    let v = vor3(cq);
    let sp = (1.0 - smoothstep(0.26, 0.3, length(v.xyz - cq))) * step(0.45, h11(v.x * 5.3 + v.y * 2.1)) * male;
    o = mix(o, mix(col * 0.3, mix(col, pale, 0.5), sp), tb);
    // a female's pale stripe along the crown's edge over the eye
    let ss = smoothstep(0.0021, 0.0023, az) * (1.0 - smoothstep(0.0027, 0.0029, az)) * smoothstep(ytop - 0.0016, ytop - 0.0011, hy)
           * smoothstep(0.0, 0.001, hx) * (1.0 - smoothstep(0.0095, 0.0105, hx)) * (1.0 - male);
    o = mix(o, pale, ss);
    // the mouth line, the pale upper lip over it (its labial shields' sutures a male's), the pale chin under it
    let ym = -0.0010 + 0.004 * hx;
    let side = smoothstep(80.0, 95.0, ph);
    let jaw = smoothstep(0.002, 0.004, hx);
    let lip = smoothstep(ym + 0.00005, ym + 0.00012, hy) * (1.0 - smoothstep(ym + 0.0008 - px, ym + 0.0009 + px, hy)) * side * jaw;
    let labl = 1.0 - smoothstep(0.00003 + px * 0.5, 0.00007 + px, abs(hx - (floor(hx / 0.0013) + 0.5) * 0.0013));
    o = mix(o, mix(col, pale, 0.75), lip * 0.9);
    o = mix(o, col * 0.75, lip * labl * 0.18);
    let chin = (1.0 - smoothstep(ym - 0.00012, ym - 0.00004, hy)) * smoothstep(100.0, 112.0, ph);
    o = mix(o, mix(mix(col, pale, 0.45), mix(pale, vec3<f32>(0.78, 0.74, 0.66), 0.5), smoothstep(118.0, 134.0, ph)), chin * 0.9);   // (the lower jaw's sides only a little paler; under it pale)
    let cs = smoothstep(0.74, 0.77, vn3(vec3<f32>(hx / 0.00045, az / 0.00045, sd + 13.0))) * chin * male * (1.0 - smoothstep(0.006, 0.009, hx));
    o = mix(o, col * 0.3, cs);
    let ml = (1.0 - smoothstep(0.00005 + px * 0.5, 0.0001 + px, abs(hy - ym))) * side * jaw;
    return mix(o, col * 0.28, ml * 0.9);
  }
`, [lacertaSeg, vn3, vor3, h11]);
const lacertaDrop = wgslFn(`
  fn lacertaDrop(x: f32) -> f32 {
    // the wall lizard's tail axis below the trunk's (y .008), by x (walllizard.py's ty)
    if (x > 0.0) { return -0.0004 + 0.05 * x; }
    if (x > -0.01) { return -0.0004 + 0.14 * x; }
    if (x > -0.02) { return -0.0018 + 0.16 * (x + 0.01); }
    if (x > -0.03) { return -0.0034 + 0.15 * (x + 0.02); }
    if (x > -0.045) { return -0.0049 + 0.0703 * (x + 0.03); }
    if (x > -0.06) { return -0.00595 + 0.0267 * (x + 0.045); }
    if (x > -0.09) { return -0.00635 + 0.016 * (x + 0.06); }
    return -0.00683 + 0.0198 * (x + 0.09);
  }
`);
const lacertaOf = wgslFn(`
  fn lacertaOf(col: vec3<f32>, p0: vec3<f32>, r0: f32, px: f32, kind: f32) -> vec3<f32> {
    let male = kind < 0.5 || (kind > 1.5 && kind < 2.5) || kind > 3.5;
    let trunk = kind < 1.5 || kind > 3.5;
    // (the TAIL in the trunk's own frame too -- no seam at its root: the frame's axis lowered to the tail's as it falls to
    //  the ground (lacertaDrop), its scales finer toward the tip)
    var p = p0;
    var r = r0;
    if (trunk && p0.x < -0.017 && r0 < 0.02) {
      p.y = p0.y - lacertaDrop(p0.x + 0.022);
      r = r0 * mix(0.67, 1.0, smoothstep(-0.13, -0.03, p0.x + 0.022));
    }
    let rho = max(length(p.yz), 1e-5);
    let ph = degrees(atan2(abs(p.z), p.y));
    let sd = select(0.0, 37.0, p.z < 0.0);
    let arc = radians(ph) * rho;
    let aa = degrees(px / rho) * 0.7 + 0.4;
    let ap = px / 0.0012 + 0.02;
    let fade = smoothstep(0.0011, 0.0021, rho);
    let w1 = (vn3(vec3<f32>(p.x / 0.0024, sd, 3.1)) - 0.5) * 12.0;
    let w2 = (vn3(vec3<f32>(p.x / 0.0019, sd, 8.3)) - 0.5) * 10.0;
    let e1 = 47.0 + w1 * 0.4;
    let e2 = 58.0 + w1;
    let e3 = 105.0 + w2;
    let e4 = 116.0 + w2 * 0.5;
    let back = 1.0 - smoothstep(e1 - aa, e1 + aa, ph);
    let dl = smoothstep(e1 - aa, e1 + aa, ph) * (1.0 - smoothstep(e2 - aa, e2 + aa, ph));
    let band = smoothstep(e2 - aa, e2 + aa, ph) * (1.0 - smoothstep(e3 - aa, e3 + aa, ph));
    let low = smoothstep(e3 - aa, e3 + aa, ph) * (1.0 - smoothstep(e4 - aa, e4 + aa, ph));
    let pale = mix(col * 1.7, vec3<f32>(0.55, 0.5, 0.36), 0.45);
    let dark = col * 0.26;
    var o = col;
    if (male) {
      let rq = vec2<f32>(p.x * 0.82 + arc * 0.57, arc * 0.82 - p.x * 0.57);
      let n = vn3(vec3<f32>(rq / 0.0015, sd + 1.0)) * 0.6 + vn3(vec3<f32>(rq.yx / 0.0007, sd + 5.0)) * 0.28 + vn3(vec3<f32>(rq / 0.0003, sd + 9.0)) * 0.12;
      o = mix(o, dark, smoothstep(0.57 - ap, 0.57 + ap, n) * back * 0.9);
      let br = smoothstep(0.42 - ap, 0.42 + ap, vn3(vec3<f32>(p.x / 0.0013, sd, 5.0)));
      o = mix(o, pale, dl * br);
      let cq = vec3<f32>(p.x / 0.0016, arc / 0.0013, sd + 3.0);
      let v = vor3(cq);
      let sr = length(v.xyz - cq) + (vn3(cq * 3.0) - 0.5) * 0.22;
      let spot = (1.0 - smoothstep(0.27 - ap, 0.27 + ap, sr)) * step(0.35, h11(v.x * 3.7 + v.y * 11.3));
      o = mix(o, mix(col * 0.3, mix(col, pale, 0.6), spot), band);
      let lb = smoothstep(0.35 - ap, 0.35 + ap, vn3(vec3<f32>(p.x / 0.0012, sd, 9.0)));
      o = mix(o, pale, low * lb * 0.8);
    } else {
      let fq = vec2<f32>(p.x * 0.82 + arc * 0.57, arc * 0.82 - p.x * 0.57);
      let sp = smoothstep(0.72 - ap, 0.72 + ap, vn3(vec3<f32>(fq / 0.0009, sd + 2.0)) * 0.75 + vn3(vec3<f32>(fq.yx / 0.0003, sd + 4.0)) * 0.25);
      o = mix(o, col * 0.55, sp * back);
      let vl = (1.0 - smoothstep(0.00016 - px, 0.00016 + px, abs(p.z))) * step(0.0, p.y) * smoothstep(0.3, 0.4, vn3(vec3<f32>(p.x / 0.002, 1.0, 2.0)));
      o = mix(o, col * 0.42, vl);
      o = mix(o, pale, dl);
      o = mix(o, col * 0.3, band);
      o = mix(o, pale, low * 0.85);
    }
    // the legs (the trunk's frame: far from its axis): mottled, dark flecks and a few pale ones
    let limb = select(0.0, smoothstep(0.0062, 0.0078, rho), trunk);
    if (kind < 0.5 || kind > 3.5) {
      let bx = p.x / 0.0032;
      let ci = floor(bx);
      let dx = (bx - ci - 0.5 - (h11(ci * 5.1 + sd) - 0.5) * 0.4) * 0.0032 / 0.00075;
      let dp = (ph - 124.0 - (h11(ci * 2.3 + sd) - 0.5) * 6.0) / 6.5;
      let a2 = px / 0.00075 + 0.05;
      let bs = (1.0 - smoothstep(1.0 - a2, 1.0 + a2, length(vec2<f32>(dx, dp)))) * step(0.2, h11(ci * 9.7 + sd + 1.0)) * step(-0.0165, p.x) * step(p.x, 0.0115) * (1.0 - limb);
      o = mix(o, vec3<f32>(0.025, 0.12, 0.5), bs);
    }
    if (kind > 3.5) {
      let gq = vec2<f32>(p.x * 0.82 + arc * 0.57, arc * 0.82 - p.x * 0.57);
      let nb = vn3(vec3<f32>(gq / 0.0011, sd + 7.0)) * 0.75 + vn3(vec3<f32>(gq.yx / 0.0004, sd + 3.0)) * 0.25;
      o = mix(o, vec3<f32>(0.012, 0.01, 0.008), smoothstep(0.62 - ap, 0.62 + ap, nb) * smoothstep(126.0, 132.0, ph) * (1.0 - limb));
    }
    if (limb > 0.0) {
      let lq = p / 0.0007;
      let dkf = smoothstep(0.66 - ap, 0.66 + ap, vn3(lq + vec3<f32>(sd + 2.0)));
      let plf = smoothstep(0.7 - ap, 0.7 + ap, vn3(lq * 1.3 + vec3<f32>(sd + 8.0))) * select(0.3, 1.0, male);
      let lo = mix(mix(col, col * 0.45, dkf * 0.85), mix(col, pale, 0.55), plf);
      o = mix(o, lo, limb);
    }
    var res = rowscalesOf(mix(col, o, fade), p, r, px);
    if (trunk) {
      let head = smoothstep(0.0265, 0.0285, p.x);
      if (head > 0.0) {
        let hc = lacertaHead(col, p.x - 0.028, p.y - 0.001, p.z, px, select(0.0, 1.0, male));
        res = mix(res, mix(rowscalesOf(hc, p, r, px), hc, smoothstep(0.0285, 0.031, p.x)), head);   // (the granules fading out over the back of the skull)
      }
    }
    return res;
  }
`, [vn3, vor3, h11, rowscalesOf, lacertaHead, lacertaDrop]);
export const coatAt = wgslFn(`
  fn coatAt(col: vec3<f32>, id: f32, p4: vec4<f32>, q4: vec4<f32>, patPx: f32, patAx: f32, px: f32) -> vec3<f32> {
    if (id > 22.5 && id < 23.5) { return featherOf(col, p4, q4, px); }
    if (id > 24.5 && id < 25.5) { return osteodermsOf(patternAt(col, 17.0, p4.xyz, p4.w, patPx, patAx), p4.xyz, px); }
    if (id > 25.5 && id < 26.5) {
      let m = stripesOf(p4.xyz, p4.w, px, 1.0);
      return mix(col, col * vec3<f32>(0.3, 0.05, 0.03), m * 0.95);
    }
    if (id > 26.5 && id < 27.5) { return palespotsOf(col, p4.xyz, p4.w, px); }
    if (id > 27.5 && id < 28.5) { return troutOf(col, p4.xyz, p4.w, px); }
    if (id > 28.5 && id < 29.5) { return mottleOf(col, p4.xyz, p4.w, px); }
    if (id > 29.5 && id < 30.5) { return suckersOf(col, p4.xyz, p4.w, px); }
    if (id > 30.5 && id < 31.5) { return clownOf(col, p4.xyz, p4.w, px); }
    if (id > 31.5 && id < 32.5) { return rowscalesOf(col, p4.xyz, p4.w, px); }
    if (id > 32.5 && id < 33.5) { return finraysOf(col, p4.xyz, p4.w, px); }
    if (id > 33.5 && id < 34.5) { return ridgesOf(col, p4.xyz, p4.w, px); }
    if (id > 34.5 && id < 35.5) { return pangolinOf(col, p4.xyz, p4.w, px); }
    if (id > 35.5 && id < 36.5) { return shagOf(col, p4.xyz, p4.w, px); }
    if (id > 36.5 && id < 37.5) { return agoutiOf(col, p4.xyz, p4.w, px); }
    if (id > 37.5 && id < 38.5) { return anteaterOf(col, p4.xyz, p4.w, px); }
    if (id > 38.5 && id < 39.5) { return skunkOf(col, p4.xyz, p4.w, px); }
    if (id > 39.5 && id < 40.5) { return coarseOf(col, p4.xyz, p4.w, px); }
    if (id > 40.5 && id < 41.5) { return orcaOf(col, p4.xyz, p4.w, px); }
    if (id > 41.5 && id < 42.5) { return humpbackOf(col, p4.xyz, p4.w, px); }
    if (id > 42.5 && id < 43.5) { return plesioOf(col, p4.xyz, p4.w, px); }
    if (id > 43.5 && id < 44.5) { return badgerOf(col, p4.xyz, p4.w, px); }
    if (id > 44.5 && id < 45.5) { return weaselOf(col, p4.xyz, p4.w, px); }
    if (id > 45.5 && id < 46.5) { return dappleOf(col, p4.xyz, px); }
    if (id > 46.5 && id < 47.5) { return pintoOf(col, p4.xyz, px); }
    if (id > 59.5 && id < 61.5) { return sealOf(col, p4.xyz, px, select(0.0, 1.0, id > 60.5)); }
    if (id > 61.5 && id < 62.5) { return walrusOf(col, p4.xyz, px); }
    if (id > 62.5 && id < 63.5) { return lynxOf(col, p4.xyz, px); }
    if (id > 63.5 && id < 65.5) { return pandaOf(col, p4.xyz, px, select(0.0, 1.0, id > 64.5)); }
    if (id > 65.5 && id < 66.5) { return koiOf(col, p4.xyz, p4.w, px); }
    if (id > 66.5 && id < 67.5) { return rainbowOf(col, p4.xyz, p4.w, px); }
    if (id > 67.5 && id < 68.5) { return narwhalOf(col, p4.xyz, p4.w, px); }
    if (id > 69.5 && id < 74.5) { return lacertaOf(col, p4.xyz, p4.w, px, id - 70.0); }
    if (id > 2.5 && id < 4.5) {
      let m = stripesOf(p4.xyz, p4.w, px, select(0.0, 1.0, id > 3.5));
      return mix(col, select(vec3<f32>(0.018, 0.014, 0.012), vec3<f32>(0.02, 0.02, 0.022), id > 3.5), m * 0.97);
    }
    if (id > 23.5 && id < 24.5) {
      // TABBY (a house cat's): the tiger's stripes, but darkened from the coat itself -- ginger on ginger, brown on grey
      let m = stripesOf(p4.xyz, p4.w, px, 0.0);
      return mix(col, col * vec3<f32>(0.34, 0.24, 0.17), m * 0.92);
    }
    if (id > 17.5 && id < 18.5) {
      let m = rosettesOf(p4.xyz, p4.w, px);
      let inner = mix(col, col * vec3<f32>(0.78, 0.6, 0.42), m.y * 0.9);
      return mix(inner, vec3<f32>(0.03, 0.022, 0.016), m.x * 0.95);
    }
    if (id > 20.5 && id < 21.5) {
      let m = rosettesOf(p4.xyz, 0.0, px);
      return mix(col, vec3<f32>(0.03, 0.022, 0.016), m.x * 0.95);
    }
    if (id > 4.5 && id < 5.5) {
      let m = giraffeOf(p4.xyz, px);
      let ptc = vec3<f32>(0.3, 0.12, 0.035) * (0.75 + 0.5 * m.y);
      return mix(col, ptc, m.x * 0.95);
    }
    if (id > 21.5 && id < 22.5) {
      // PIEBALD (a cow's): the old engine's blotches (banner_wgsl patternAt), but in a sculpted body's LINEAR colour
      // their 0.13 grey showed as mid grey -- the blotch's share is read back from a white coat and laid on near black
      let w = patternAt(vec3<f32>(1.0), id, p4.xyz, p4.w, patPx, patAx).x;
      let m = clamp((1.0 - w) / 0.87, 0.0, 1.0);
      return mix(col, vec3<f32>(0.016, 0.013, 0.011), m);
    }
    return patternAt(col, id, p4.xyz, p4.w, patPx, patAx);
  }
`, [featherOf, stripesOf, rosettesOf, giraffeOf, osteodermsOf, palespotsOf, troutOf, mottleOf, suckersOf, clownOf, rowscalesOf, finraysOf, ridgesOf, pangolinOf, shagOf, agoutiOf, anteaterOf, skunkOf, coarseOf, orcaOf, humpbackOf, plesioOf, badgerOf, weaselOf, dappleOf, pintoOf, sealOf, walrusOf, lynxOf, pandaOf, koiOf, rainbowOf, narwhalOf, lacertaOf, patternAt]);
