from cetlib import *
import os

# ORCA (Orcinus orca), an adult MALE, 7.0 m from the snout to the fluke notch: the snout's tip at x = +2.8, the notch
# at -4.2. Rest frame: x forward, y up, z left, metres; the body's axis about y = 0.
L, XS = 7.0, 2.8
X = lambda s: XS - s * L          # (s: the share of the length back from the snout)
HZ = 0.62                         # (a cruising tail beat, ~0.6 Hz)

# THE RIG: body (root) -> head; the pectorals; four tail bones pitching (the stock and the flukes beat UP AND DOWN, each a
# beat behind the one before -- a whale's tail never sweeps sideways)
XT = [X(0.53), X(0.70), X(0.86), X(0.952)]
R = Rig()
R.add("body", None, [0, 0, 0], shape=tube_part([1.6, 0, 0], [-0.9, 0, 0], 0.7, 0.6), color="@black",
      anim={"axis": "z", "deg": 0.8, "speed": HZ, "phase": 2.6})
R.add("head", "body", [1.75, 0, 0], shape={"shape": "sphere", "size": {"r": 0.5}}, color="@black")
PECT = [X(0.205), -0.4, 0.46]
for side, s in (("L", 1), ("R", -1)):
    R.add(f"pect{side}", "body", [PECT[0], PECT[1], s * PECT[2]], shape={"shape": "sphere", "size": {"r": 0.1}}, color="@black",
          anim={"axis": "x", "deg": s * 4, "speed": HZ * 0.5, "phase": 0.4})
degs, ph = [3.0, 6.5, 9.0, 15.0], [0.0, -0.55, -1.1, -1.75]
par, x0 = "body", 0.0
for j, x in enumerate(XT):
    R.add(f"tail{j + 1}" if j < 3 else "fluke", par, [x - x0, 0.0, 0], shape={"shape": "sphere", "size": {"r": 0.3 - 0.07 * j}}, color="@black",
          anim={"axis": "z", "deg": degs[j], "speed": HZ, "phase": ph[j]})
    par, x0 = (f"tail{j + 1}" if j < 3 else "fluke"), x
def bone_x(x):
    if x > 1.75: return "head"
    if x > XT[0]: return "body"
    if x > XT[1]: return "tail1"
    if x > XT[2]: return "tail2"
    if x > XT[3]: return "tail3"
    return "fluke"

# THE BODY (x, top, bottom, half width): a robust spindle, deepest 0.36-0.45 back; the head a blunt rounded cone with
# only the hint of a beak; the tail stock laterally flattened, keeled above and below
ST = [(X(0.0), -0.075, -0.165, 0.05), (X(0.012), 0.0, -0.215, 0.12), (X(0.03), 0.1, -0.29, 0.2), (X(0.06), 0.225, -0.38, 0.3),
      (X(0.1), 0.35, -0.48, 0.41), (X(0.15), 0.47, -0.585, 0.51), (X(0.21), 0.575, -0.665, 0.585), (X(0.28), 0.65, -0.715, 0.63),
      (X(0.36), 0.695, -0.725, 0.645), (X(0.45), 0.69, -0.69, 0.625), (X(0.55), 0.63, -0.6, 0.555), (X(0.64), 0.54, -0.475, 0.44),
      (X(0.72), 0.44, -0.35, 0.3), (X(0.8), 0.34, -0.235, 0.18), (X(0.87), 0.245, -0.14, 0.11), (X(0.92), 0.17, -0.075, 0.085),
      (X(0.955), 0.115, -0.035, 0.075), (X(0.975), 0.075, -0.005, 0.06)]
# (2026-11-08: the stock on past X(.975), tapering INSIDE the flukes' swollen middle -- it ended there in a round cap,
#  a knot under the stock where the flukes leave it; pass 2: it ends at X(.975), already down to the flukes' swollen
#  depth -- run on past it, its flanks stood above the thin sheet as a rounded lip over the notch)
PAT = "orca"
sh = trunk_tubes(ST, [ST[0][0] + 0.02, 1.75, XT[0], XT[1], XT[2], XT[3], ST[-1][0]], ["head", "body", "tail1", "tail2", "tail3", "fluke"], "@black", k=0.12, pat=PAT,
                 rfun=lambda t, b, w: w + 0.4 * ((t - b) / 2 - w))
# the stock's keels (the dorsal one from behind the fin, the ventral one from the anus) -- laterally thin, deep
sh += [S("tube", id="keelD", bone=bone_x(x), pts=[[x + 0.25, smooth(ST, x + 0.25)[0] - 0.05, 0, 0.05], [x - 0.25, smooth(ST, x - 0.25)[0] - 0.02, 0, 0.04]],
         k=0.06, color="@black", pat=PAT) for x in [X(0.74), X(0.8), X(0.86), X(0.91)]]
sh += [S("tube", id="keelV", bone=bone_x(x), pts=[[x + 0.22, smooth(ST, x + 0.22)[1] + 0.05, 0, 0.05], [x - 0.22, smooth(ST, x - 0.22)[1] + 0.025, 0, 0.035]]
         + ([[x - 0.4, smooth(ST, x - 0.4)[1] + 0.022, 0, 0.012]] if x == X(0.91) else []),   # (2026-11-08: the last one run out to a thin
         k=0.06, color="@black", pat=PAT) for x in [X(0.8), X(0.86), X(0.91)]]            #  end -- its round cap stood out as a knot under the stock just ahead of the flukes)

def surf_z(x, y, out=0.0):
    """the loft's half width at (x, y): where its ellipse is (plus `out`)"""
    top, bot, hw = smooth(ST, x); yc, hh = (top + bot) / 2, (top - bot) / 2
    q = max(0.0, 1 - ((y - yc) / hh) ** 2)
    return hw * math.sqrt(q) + out

# THE HEAD: the rounded melon over a short indistinct beak, the lower jaw a little fuller below; the MOUTH LINE long and
# nearly straight, rising a little to its corner below and ahead of the eye
sh += [
    S("ell", id="melon", bone="head", c=[X(0.055), 0.07, 0], r=[0.42, 0.24, 0.27], k=0.12, color="@black", pat=PAT),
    S("ell", id="jaw", bone="head", c=[X(0.05), -0.25, 0], r=[0.36, 0.12, 0.22], k=0.12, color="@black", pat=PAT),
    S("ell", id="throat", c=[X(0.15), -0.47, 0], r=[0.6, 0.15, 0.36], k=0.16, color="@black", pat=PAT),
]
LIP = [(X(0.0) - 0.005, -0.135), (X(0.02), -0.14), (X(0.045), -0.145), (X(0.07), -0.145), (X(0.09), -0.14), (X(0.105), -0.125)]
MOUTH = (S("tube", id="mouth", bone="head", pts=[[x, y, surf_z(x, y, 0.006) if i else 0.0, 0.024 if i < len(LIP) - 1 else 0.016] for i, (x, y) in enumerate(LIP)],
            k=0.018, color="@black", op="sub", mirror=True))   # (not used: a groove finer than the mesh speckles -- the mouth is the white jaw's edge)
# the BLOWHOLE: a crescent on top, its open side forward, ~0.16 back
BX = X(0.165)
sh += [S("ell", id="blow", bone="head", c=[BX, smooth(ST, BX)[0] + 0.005, 0], r=[0.022, 0.03, 0.085], k=0.015, color="@black", op="sub"),
       S("ell", id="blowLip", bone="head", c=[BX + 0.035, smooth(ST, BX)[0] - 0.005, 0], r=[0.04, 0.03, 0.08], k=0.03, color="@black", pat=PAT)]

# THE DORSAL FIN (a male's): tall, erect, a near isosceles triangle 1.5 m over the back, its leading edge leaning a
# little back, its trailing edge near upright and a shade concave, the tip a little rounded. ONE SHEET (sharp.js `fin`):
# the rim exactly this outline, the leading edge blunt; a FAIRED into the back along its foot (`fair`)
FB0, FB1, FH = X(0.395), X(0.525), 1.52
yb = lambda x: smooth(ST, x)[0]
base_y = yb((FB0 + FB1) / 2) - 0.06
tipx = FB1 + 0.22
def f_le(t):
    return lerpf(FB0 + 0.12, tipx + 0.06, t) + 0.12 * (1 - t) ** 3 + (0.35 * (1 - t / 0.12) ** 2 if t < 0.12 else 0)
def f_te(t):
    return lerpf(FB1, tipx - 0.02, t) + 0.05 * math.sin(math.pi * min(1, t * 1.1)) - (0.18 * (1 - t / 0.12) ** 2 if t < 0.12 else 0)
f_y = lambda t: base_y + t * (FH + 0.06)
sh.append(dorsal_sheet("fin", "body", yb, f_le, f_te, f_y, (tipx + 0.015, f_y(1.0) + 0.025), 0.1, "@black", sink=0.1, n=48, rows=8, pat=PAT,
                       fair={"r": 0.12}))

# THE PECTORAL FLIPPERS: big rounded PADDLES (a male's, 1.3 m, broad as an oar's blade), set low just behind the head,
# hanging down, out and back; a sheet each (the tip round: no corner), FAIRED into the body (sharp.js `fair`)
sd = norm([-0.42, -0.72, 0.55]); cdir = [1.0, -0.15, 0.25]
chord = lambda t: (0.36 + 0.42 * math.sin(math.pi * min(1, t * 0.82 + 0.1)) ** 1.3) * math.sqrt(max(0.0, 1 - ((t - 0.62) / 0.38) ** 2)) if t > 0.62 else 0.36 + 0.42 * math.sin(math.pi * min(1, t * 0.82 + 0.1)) ** 1.3
root = [PECT[0] + 0.05, PECT[1], PECT[2] - 0.06]
sh.append(flipper_sheet("pect", "pectL", root, sd, cdir, 1.3, chord, 0.09, "@black", le_off=lambda t: 0.08 * math.sin(math.pi * t),
                        sweep=lambda t: 0.1 * t * t, sink=0.06, corner=False, pat=PAT, n=48, fair={"r": 0.06}))

# THE FLUKES: 2 m across, the leading edges swept back to pointed tips, the trailing edge a shallow curve to a small
# median notch; ONE sheet rooted across the stock (its white underside painted by the pattern), FAIRED into the stock
# (sharp.js `fair`) and swollen at its middle to the stock's thickness (`swell`): no stump
YF = 0.035
fl_le = lambda z: X(0.948) - 0.72 * z ** 2.1
fl_te = lambda z: X(1.0) + 0.06 * math.exp(-z / 0.05) - 0.3 * z ** 2.4 - 0.02
sh.append(fluke_sheet2("flukes", "fluke", fl_le, fl_te, lambda z: YF - 0.02 * z * z, 0.92, (-4.49, 0.955), -3.95, 0.05, 0.11, "@black",
                       n=64, rows=8, pat=PAT, fair={"r": 0.09}, swell=[0.13, 0.3]))

# (a slight SHEEN: the wet skin's faint glint and rim, so the black is not a flat silhouette)
for p in sh:
    if p.get("op") != "sub": p["wet"] = 0.14

d = {
    "name": "orca",
    "_about": "SCULPTED (2026-11-06, the sculpt overlay; generator scratchpad sc/sea3/gen/orca.py): a killer whale, an adult MALE, 7 m -- a robust spindle deepest 0.36-0.45 back, the rounded melon over a short indistinct beak and a long nearly straight MOUTH LINE rising to its corner below the small eye; the crescent blowhole; the male's TALL ERECT DORSAL FIN (1.5 m, a near isosceles triangle); big rounded PADDLE pectorals (1.3 m) set low behind the head; the stock laterally flattened and keeled; 2 m flukes, swept back to pointed tips, the median notch. Its MARKINGS are one per-pixel pattern (coatpat.js 41 `orca`, in the rest pose's own space, sharp-edged): the white EYE PATCH above and behind the eye, the white LOWER JAW, throat and belly narrowing between the flippers and sweeping up the flanks behind the fin in a lobe, the grey SADDLE behind the fin, the white UNDERSIDE of the flukes in a black margin. A SWIMMER of the open sea (index.html seaLife: a pod far offshore, its fin breaking the surface as it breathes). Its tail PITCHES (axis z, four bones a beat apart): the flukes beat up and down. (2026-11-08) The dorsal fin, the paddles and the flukes (one sheet across both, its white underside painted by the pattern) are `fin` SHEETS (sharp.js; cetlib.py): the rim exactly the outline, FAIRED into the body (sharp.js `fair`: each face near the body the smooth union of the sheet and the body, a fillet grown out of the skin -- no fillet shapes, no stump), the flukes' middle swollen to the stock's depth (`swell`). (2026-11-08) The stock tapers to the flukes' swollen depth where they begin (run on past it, its flanks stood above the thin sheet as a rounded lip), and the ventral keel runs out thin ahead of them (its round end was a knot under the stock). (2026-11-08, pass 2) The sheets' grids are solved harmonic (`grid: \"flow\"`: the columns curve with the outline, no bundle of slivers down a swept fluke or flipper) and their thickness is drawn on a SMOOTH rim distance (sharp.js smoothRimDist): no ridge line down the middle.",
    "kind": "parts",
    "facet": False,
    "flags": {"fly": {"alt": [1.5, 4], "speed": [2.2, 3.2], "hz": HZ}},
    "colors": {"black": os.environ.get("OC", "#0f1012")},
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mottle": {"amount": 0},
        "mesh": {"cell": 0.028, "tris": [10000, 3000], "focus": {"head": 4}, "far": 20},
        "shape": sh,
        "eyes": {"at": [X(0.118), -0.095, 0.4], "from": [X(0.118), -0.095, 0], "r": 0.028, "color": "#060606", "iris": "#2a1c12", "pupil": "round", "lid": False, "sink": 0.4, "socket": 1.05, "bone": "head"},
    },
}
write_to("sea/orca", d)
# (for coatpat.js orcaOf: the body's axis and half girths along x)
print("KNOTS", [(round(s[0], 3), round((s[1] + s[2]) / 2, 3), round((s[1] - s[2]) / 2, 3), s[3]) for s in ST])

# ---- THE MARKINGS (coatpat.js orcaOf): written here, from the same numbers, and pasted there -----------------------
RM = 0.6
f = lambda v: f"{v:.4f}"
AX = [(round(s[0], 3), (s[1] + s[2]) / 2, (s[1] - s[2]) / 2, s[3]) for s in ST]
def phi_at(x, y):
    t, b, w = smooth(ST, x); yc, hh = (t + b) / 2, (t - b) / 2
    c = max(-1, min(1, (y - yc) / hh)); return math.atan2(math.sqrt(1 - c * c), -c)
XC = LIP[-1][0]
BELLY = [(XC + 0.03, phi_at(XC, LIP[-1][1] - 0.012)), (XC - 0.04, phi_at(XC - 0.04, LIP[-1][1] - 0.03)), (1.95, 1.12), (1.8, 0.88), (1.62, 0.66), (1.45, 0.52), (1.3, 0.45), (1.0, 0.42), (0.7, 0.45),
         (0.35, 0.5), (0.0, 0.56), (-0.35, 0.62), (-0.62, 0.7), (-0.8, 0.82), (-0.92, 1.05), (-1.02, 1.38), (-1.12, 1.64), (-1.26, 1.8),
         (-1.45, 1.88), (-1.7, 1.93), (-1.95, 1.97), (-2.08, 1.98), (-1.98, 1.84), (-1.84, 1.52), (-1.7, 1.12), (-1.6, 0.78), (-1.54, 0.56),
         (-1.68, 0.4), (-1.9, 0.27), (-2.1, 0.15), (-2.35, 0.0), (-2.35, -0.5), (XC + 0.03, -0.5)]
SADDLE = [(-0.82, 3.6), (-0.85, 2.66), (-0.98, 2.47), (-1.25, 2.38), (-1.55, 2.44), (-1.82, 2.64), (-1.95, 2.95), (-1.98, 3.6)]
# (the flukes' white underside: their outline in from the edge by a margin -- (x, |z|) knots of the leading edge out to the tip and the trailing edge back)
M = 0.045
FL = [(fl_le(z) - M * (1 - z), z) for z in [0.07, 0.25, 0.45, 0.65, 0.8]] + [(fl_le(0.9) - 0.03, 0.88)] + [(fl_te(z) + M, z) for z in [0.8, 0.6, 0.4, 0.2, 0.07]]
def arr(name, pts, scale_y=1.0):
    return f"var {name} = array<vec2<f32>, {len(pts)}>(" + ", ".join(f"vec2<f32>({f(x)}, {f(y * scale_y)})" for x, y in pts) + ");"
ax = "var AX = array<vec4<f32>, %d>(" % len(AX) + ", ".join(f"vec4<f32>({f(a)}, {f(b)}, {f(c)}, {f(dd)})" for a, b, c, dd in AX) + ");"
lip = "var LP = array<vec2<f32>, %d>(" % len(LIP) + ", ".join(f"vec2<f32>({f(x)}, {f(y - 0.012)})" for x, y in LIP) + ");"
EYE = (X(0.118) - 0.36, -0.095 + 0.185, 0.32, 0.092, math.radians(10))
W = {"AX": ax, "LIP": lip, "BELLY": arr("BP", BELLY, RM), "SADDLE": arr("SP", SADDLE, RM), "FLUKE": arr("FP", FL),
     "N": [len(AX), len(LIP), len(BELLY), len(SADDLE), len(FL)], "EYE": EYE, "XF": X(0.952) - 0.04, "YF": YF, "RM": RM}
json.dump(W, open("orca_wgsl.json", "w"), indent=1)
