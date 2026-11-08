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
