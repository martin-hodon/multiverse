# writes the orca's marking functions (coatpat.js) from orca_wgsl.json
import json
W = json.load(open("orca_wgsl.json"))
def poly_fn(name, decl, n):
    return f'''const {name} = wgslFn(`
  fn {name}(q: vec2<f32>) -> f32 {{
    {decl}
    var d = dot(q - V[0], q - V[0]);
    var s = 1.0;
    var j = {n - 1};
    for (var i = 0; i < {n}; i++) {{
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
`);'''
nA, nL, nB, nS, nF = W["N"]
ex, ey, ea, eb, et = W["EYE"]
out = []
out.append("""// 41 ORCA (2026-11-06, an adult male killer whale's markings: assets/creatures/sea/orca.json, its generator scratchpad
// sc/sea3/gen/orca.py writes these numbers), SOLID: the rest pose's own space, metres. Round the body's axis (AX: x, the
// axis's height, the half height and half width there) each point has its ELLIPTIC ANGLE from the belly's midline (0) to
// the spine (pi); the white and the grey are polygons in (x, that angle x RM metres), every edge antialiased by the
// pixel and sharp as an orca's are:
//   the white LOWER JAW (everything under the lip line, LP, ahead of the mouth's corner), the throat and the belly --
//   narrowing between the flippers, widening behind the navel and parting into the FLANK LOBES that sweep up and back
//   behind the dorsal fin, and a central prong back to the vent (BP);
//   the grey SADDLE behind the fin (SP), its edge a little softer;
//   the white EYE PATCH: an egg above and behind the eye, its narrow end forward, its long axis rising a little rearward;
//   the flukes' white UNDERSIDE (behind XF, under their mid-plane), inside a black margin (FP: x, |z|)""")
out.append(poly_fn("orcaBelly", W["BELLY"].replace("var BP", "var V"), nB))
out.append(poly_fn("orcaSaddle", W["SADDLE"].replace("var SP", "var V"), nS))
out.append(poly_fn("orcaFluke", W["FLUKE"].replace("var FP", "var V"), nF))
out.append(f'''const orcaOf = wgslFn(`
  fn orcaOf(col: vec3<f32>, p: vec3<f32>, r: f32, px: f32) -> vec3<f32> {{
    {W["AX"]}
    {W["LIP"]}
    var a = AX[{nA - 1}];
    if (p.x >= AX[0].x) {{ a = AX[0]; }}
    for (var i = 0; i < {nA - 1}; i++) {{
      if (p.x <= AX[i].x && p.x >= AX[i + 1].x) {{ a = mix(AX[i], AX[i + 1], (AX[i].x - p.x) / (AX[i].x - AX[i + 1].x)); }}
    }}
    let ph = atan2(abs(p.z) / a.w, -(p.y - a.y) / a.z);
    let q = vec2<f32>(p.x, ph * {W["RM"]:.4f});
    let aa = max(px, 0.002);
    let wn = vn3(p / 0.05) - 0.5;
    // (the jaw: under the lip line, ahead of the corner)
    var ly = LP[{nL - 1}].y;
    for (var i = 0; i < {nL - 1}; i++) {{
      if (p.x <= LP[i].x && p.x >= LP[i + 1].x) {{ ly = mix(LP[i].y, LP[i + 1].y, (LP[i].x - p.x) / (LP[i].x - LP[i + 1].x)); }}
    }}
    let jaw = (1.0 - smoothstep(-aa, aa, p.y - ly)) * smoothstep(-aa, aa, p.x - LP[{nL - 1}].x);
    var white = max(jaw, 1.0 - smoothstep(-aa, aa, orcaBelly(q)));
    // (the eye patch)
    let e = vec2<f32>(p.x - {ex:.4f}, p.y - {ey:.4f});
    let u = e.x * {__import__("math").cos(et):.4f} - e.y * {__import__("math").sin(et):.4f};
    let v = e.x * {__import__("math").sin(et):.4f} + e.y * {__import__("math").cos(et):.4f};
    let bb = {eb:.4f} * (1.0 - 0.32 * clamp(u / {ea:.4f}, -1.0, 1.0));
    let de = (length(vec2<f32>(u / {ea:.4f}, v / bb)) - 1.0) * bb;
    white = max(white, (1.0 - smoothstep(-aa, aa, de)) * step(0.12, abs(p.z)));
    // (the flukes: their underside, in from the edge)
    let fl = step(p.x, {W["XF"]:.4f});
    let under = 1.0 - smoothstep(-aa, aa, p.y - ({W["YF"]:.4f} - 0.02 * p.z * p.z));
    let fw = under * (1.0 - smoothstep(-aa, aa, orcaFluke(vec2<f32>(p.x, abs(p.z)))));
    white = mix(white, fw, fl);
    let grey = (1.0 - smoothstep(-aa - 0.012, aa + 0.012, orcaSaddle(q) + wn * 0.02)) * (1.0 - fl);
    let skin = 1.0 + wn * 0.06 * (1.0 - smoothstep(0.01, 0.04, px));
    var o = mix(col, vec3<f32>(0.25, 0.26, 0.28) * skin, grey);
    return mix(o, vec3<f32>(0.8, 0.81, 0.82) * skin, white);
  }}
`, [vn3, orcaBelly, orcaSaddle, orcaFluke]);''')
open("orca_wgsl.js", "w").write("\n".join(out) + "\n")
print(open("orca_wgsl.js").read()[:400])
