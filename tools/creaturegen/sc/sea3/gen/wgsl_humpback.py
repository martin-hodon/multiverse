# writes the humpback's colouring (coatpat.js 42) from humpback_wgsl.json
import json
W = json.load(open("humpback_wgsl.json"))
NA, NF = W["NA"], W["NF"]
CHIN, NAV, XF, YF = W["CHIN"], W["NAV"], W["XF"], W["YF"]
PX0, PX1 = W["PX"]
out = []
out.append("""// 42 HUMPBACK (2026-11-06, a humpback whale's colours: assets/creatures/sea/humpback.json, its generator scratchpad
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
//   the MOUTH LINE (LP): a dark crease from the jaw's tip to its corner""")
out.append(f'''const humpFluke = wgslFn(`
  fn humpFluke(q: vec2<f32>) -> f32 {{
    {W["FL"]}
    var d = dot(q - V[0], q - V[0]);
    var s = 1.0;
    var j = {NF - 1};
    for (var i = 0; i < {NF}; i++) {{
      let e = V[j] - V[i];
      let w = q - V[i];
      let b = w - e * clamp(dot(w, e) / dot(e, e), 0.0, 1.0);
      d = min(d, dot(b, b));
      let c1 = q.y >= V[i].y;
      let c2 = q.y < V[j].y;
      let c3 = e.x * w.y > e.y * w.x;
      if ((c1 && c2 && c3) || (!c1 && !c2 && !c3)) {{ s = -s; }}
      j = i;
    }}
    return s * sqrt(d);
  }}
`);''')
out.append(f'''const humpbackOf = wgslFn(`
  fn humpbackOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {{
    {W["AX"]}
    var a = AX[{NA - 1}];
    if (p.x >= AX[0].x) {{ a = AX[0]; }}
    for (var i = 0; i < {NA - 1}; i++) {{
      if (p.x <= AX[i].x && p.x >= AX[i + 1].x) {{ a = mix(AX[i], AX[i + 1], (AX[i].x - p.x) / (AX[i].x - AX[i + 1].x)); }}
    }}
    let dy = (p.y - a.y) / a.z;
    let dz = abs(p.z) / a.w;
    let rho = length(vec2<f32>(dy, dz));
    let ph = atan2(dz, -dy);
    let aa = max(px, 0.003);
    let n1 = vn3(p / 0.8) - 0.5;
    let n2 = vn3(p / 0.25) - 0.5;
    let n3 = vn3(p / 0.07) - 0.5;
    let s = ({CHIN:.4f} - p.x) / 14.0;
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
    let phP = 1.3 * sqrt(clamp(s / 0.05, 0.0, 1.0)) * pow(clamp(({(NAV - CHIN) / -14.0:.4f} - s) / 0.3, 0.0, 1.0), 0.6);
    let u = ph / max(phP, 0.001);
    let k = fract(u * 15.0);
    let dg = min(k, 1.0 - k) / 15.0 * phP * a.z;
    let g = (1.0 - smoothstep(0.012, 0.012 + aa, dg)) * (1.0 - smoothstep(0.85, 1.0, u)) * step(0.004, s) * (1.0 - smoothstep(0.03, 0.08, px));
    o = o * (1.0 - 0.6 * g);
    // (the flippers: white, mottled, dark at the root)
    let fp = smoothstep(1.06, 1.2, rho) * step(p.y, a.y) * step(p.x, {PX0:.4f}) * step({PX1:.4f}, p.x);
    let fm = smoothstep(0.17, 0.21, n2 + n3 * 0.4) * 0.65;
    let fw = mix(WH, GR, fm);
    o = mix(o, mix(dark, fw, smoothstep(1.15, 1.45, rho)), fp);
    // (the flukes: below their mid-plane, white inside a black margin, blotched -- only out on the blades, past the
    // local stock's half width (AX), so the stock and the flukes' root stay dark all round)
    let fl = step(p.x, {XF:.4f});
    let under = (1.0 - smoothstep(-aa, aa, p.y - {YF:.4f})) * smoothstep(2.0, 4.5, dz);
    let fwh = under * (1.0 - smoothstep(-aa, aa, humpFluke(vec2<f32>(p.x, abs(p.z))) + n2 * 0.12)) * (1.0 - smoothstep(0.07, 0.1, n1 + n2 * 0.6));
    o = mix(o, mix(dark, WH, fwh), fl);
    // (the mouth line: a dark crease from the tip of the jaw to its corner under the eye)
    {W["LIP"]}
    var ly = LP[0].y;
    for (var i = 0; i < {W["NL"] - 1}; i++) {{
      if (p.x <= LP[i].x && p.x >= LP[i + 1].x) {{ ly = mix(LP[i].y, LP[i + 1].y, (LP[i].x - p.x) / (LP[i].x - LP[i + 1].x)); }}
    }}
    let ml = (1.0 - smoothstep(0.012, 0.012 + aa, abs(p.y - ly))) * step(LP[{W["NL"] - 1}].x, p.x) * step(p.x, LP[0].x + 0.05);
    o = mix(o, col * 0.4, ml);
    return o;
  }}
`, [vn3, humpFluke]);''')
open("humpback_wgsl.js", "w").write("\n".join(out) + "\n")
print("ok")
