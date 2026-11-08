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
`, [vn3]);
