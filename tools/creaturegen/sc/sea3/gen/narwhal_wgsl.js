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
