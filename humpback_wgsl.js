// 42 HUMPBACK (2026-11-06, a humpback whale's colours: assets/creatures/sea/humpback.json, its generator scratchpad
// sc/sea3/gen/humpback.py writes these numbers), SOLID: the rest pose's own space, metres. Round the body's axis (AX: x,
// the axis's height, half height, half width) each point has its ELLIPTIC ANGLE from the belly's midline (0) to the spine
// (pi) and its girth share (rho: 1 on the trunk's surface):
//   the dark back; the white BELLY, its upper edge wandering (two noises) high under the flippers and low on the stock,
//   blotched grey inside and flecked white above it;
//   the THROAT PLEATS: 15 grooves either side from the chin to the navel, fanning out over the throat and converging at
//   both ends, darker lines in the white (faded once a pixel is wider than a groove);
//   the FLIPPERS (well out from the trunk, below its axis, between the head and the hump): white, mottled grey, dark at
//   the root;
//   the FLUKES (behind XF): dark above; below, white inside a black margin (HFP: x, |z|), blotched black;
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
    // (the flukes: below their mid-plane, white inside a black margin, blotched)
    let fl = step(p.x, -8.1100);
    let under = 1.0 - smoothstep(-aa, aa, p.y - 0.0300);
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
