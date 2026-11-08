from cetlib import *

# BOTTLENOSE DOLPHIN (Tursiops truncatus), 2.6 m from the beak's tip to the fluke notch: the beak's tip at x = +1.2, the
# notch at -1.4. Rest frame: x forward, y up, z left, metres; the body's axis about y = 0. A coat param `common` paints
# the short-beaked common dolphin's hourglass instead (Delphinus delphis: the coat at scale .78, ~2 m).
HZ = 1.1
XT = [-0.3, -0.66, -0.98, -1.13]
R = Rig()
R.add("body", None, [0, 0, 0], shape=tube_part([0.8, 0, 0], [-0.3, 0, 0], 0.22, 0.2), color="@cape",
      anim={"axis": "z", "deg": 1.0, "speed": HZ, "phase": 2.6})
R.add("head", "body", [0.75, 0, 0], shape={"shape": "sphere", "size": {"r": 0.16}}, color="@cape")
PECT = [0.6, -0.15, 0.15]
for side, s in (("L", 1), ("R", -1)):
    R.add(f"pect{side}", "body", [PECT[0], PECT[1], s * PECT[2]], shape={"shape": "sphere", "size": {"r": 0.03}}, color="@cape",
          anim={"axis": "x", "deg": s * 5, "speed": HZ * 0.5, "phase": 0.4})
degs, ph = [3.5, 7.0, 10.0, 16.0], [0.0, -0.55, -1.1, -1.75]
par, x0 = "body", 0.0
for j, x in enumerate(XT):
    nm = f"tail{j + 1}" if j < 3 else "fluke"
    R.add(nm, par, [x - x0, 0.0, 0], shape={"shape": "sphere", "size": {"r": 0.1 - 0.02 * j}}, color="@cape",
          anim={"axis": "z", "deg": degs[j], "speed": HZ, "phase": ph[j]})
    par, x0 = nm, x
def bone_x(x):
    if x > 0.75: return "head"
    if x > XT[0]: return "body"
    if x > XT[1]: return "tail1"
    if x > XT[2]: return "tail2"
    if x > XT[3]: return "tail3"
    return "fluke"

# THE BODY (x, top, bottom, half width): a sleek spindle deepest ~40% back; the short stout BEAK set off from the
# rounded MELON by a crease; the tail stock laterally flattened and keeled
ST = [(1.2, -0.035, -0.07, 0.022), (1.17, -0.02, -0.083, 0.034), (1.12, -0.008, -0.097, 0.045), (1.06, 0.005, -0.112, 0.058),
      (1.02, 0.03, -0.124, 0.072), (0.97, 0.105, -0.142, 0.1), (0.9, 0.158, -0.168, 0.135), (0.79, 0.198, -0.2, 0.172),
      (0.62, 0.228, -0.236, 0.208), (0.42, 0.245, -0.252, 0.228), (0.2, 0.245, -0.244, 0.226), (0.0, 0.228, -0.222, 0.206),
      (-0.2, 0.198, -0.188, 0.17), (-0.4, 0.162, -0.146, 0.122), (-0.6, 0.128, -0.105, 0.078), (-0.8, 0.096, -0.07, 0.048),
      (-0.95, 0.07, -0.044, 0.034), (-1.06, 0.048, -0.024, 0.03), (-1.13, 0.034, -0.012, 0.03),
      (-1.19, 0.026, -0.002, 0.02), (-1.25, 0.019, 0.005, 0.01)]   # (the stock low and flat at its end: it runs out into the flukes --
      # 2026-11-08: on, tapering, INSIDE the flukes' swollen middle; it ended in a round cap at -1.13, a collar crease
      # round the root of the flukes seen from below)
sh = trunk_tubes(ST, [1.22, 0.75, XT[0], XT[1], XT[2], XT[3], ST[-1][0]], ["head", "body", "tail1", "tail2", "tail3", "fluke"], "@cape",
                 step=0.05, ov=0.05, k=0.04, rfun=lambda t, b, w: w + 0.4 * ((t - b) / 2 - w))
# the stock's keels, thin and deep
sh += [S("tube", id="keelD", bone=bone_x(x), pts=[[x + 0.09, smooth(ST, x + 0.09)[0] - 0.018, 0, 0.018], [x - 0.09, smooth(ST, x - 0.09)[0] - 0.008, 0, 0.014]],
         k=0.02, color="@cape") for x in [-0.6, -0.78, -0.94]]
sh += [S("tube", id="keelV", bone=bone_x(x), pts=[[x + 0.08, smooth(ST, x + 0.08)[1] + 0.018, 0, 0.017], [x - 0.08, smooth(ST, x - 0.08)[1] + 0.01, 0, 0.012]],
         k=0.02, color="@cape") for x in [-0.66, -0.82, -0.96]]

def surf_z(x, y, out=0.0):
    top, bot, hw = smooth(ST, x); yc, hh = (top + bot) / 2, (top - bot) / 2
    q = max(0.0, 1 - ((y - yc) / hh) ** 2)
    return hw * math.sqrt(q) + out

# THE HEAD: the MELON a rounded bulge over the beak's root, the lower jaw a little longer than the upper; the MOUTH a
# long line rising to its corner below and ahead of the eye (the "smile")
sh += [
    S("ell", id="melon", bone="head", c=[0.92, 0.075, 0], r=[0.13, 0.1, 0.115], k=0.04, color="@cape"),
    S("ell", id="jaw", bone="head", c=[1.05, -0.08, 0], r=[0.15, 0.035, 0.05], k=0.025, color="@pale"),
    S("ell", id="throat", c=[0.62, -0.15, 0], r=[0.26, 0.06, 0.15], k=0.06, color="@pale"),
]
LIP = [(1.205, -0.058), (1.15, -0.064), (1.08, -0.066), (1.02, -0.062), (0.97, -0.05), (0.945, -0.036)]
sh += [S("tube", id="mouth", bone="head", pts=[[x, y, surf_z(x, y, 0.0) if i else 0.0, 0.004 if i < len(LIP) - 1 else 0.003] for i, (x, y) in enumerate(LIP)],
         k=0.003, kc=0.002, color="@dark", op="paint", mirror=True)]
# the BLOWHOLE: a crescent on top, its open side forward
BX = 0.74
sh += [S("ell", id="blow", bone="head", c=[BX, smooth(ST, BX)[0] + 0.002, 0], r=[0.008, 0.012, 0.028], k=0.005, color="@dark", op="sub"),
       S("ell", id="blowLip", bone="head", c=[BX + 0.013, smooth(ST, BX)[0] - 0.002, 0], r=[0.014, 0.01, 0.026], k=0.01, color="@cape")]

# (2026-11-08) Each sheet is FAIRED into the body (sharp.js `fair`): its faces near the body are the smooth union of the
# body's field and the sheet, a fillet `r` wide that grows out of the skin -- no fillet shapes in the grid, no stump
FAIR_FIN, FAIR_PECT, FAIR_FLUKE = {"r": 0.04}, {"r": 0.02}, {"r": 0.035}

# THE DORSAL FIN: FALCATE -- the leading edge a smooth convex sweep back, the trailing edge concave, the tip curved back
# past the root; 0.26 m tall, a little behind the middle. ONE SHEET (sharp.js `fin`): its rim exactly this outline, its
# leading edge blunt, sharp behind; FAIRED into the back along its foot (`fair`)
FB0, FB1, FH = 0.12, -0.2, 0.26
base_y = smooth(ST, (FB0 + FB1) / 2)[0] - 0.025
def f_le(t):
    return FB0 - 0.36 * t ** 1.35 + 0.06 * (1 - t) ** 3 + (0.1 * (1 - t / 0.15) ** 2 if t < 0.15 else 0)
def f_te(t):
    return FB1 - 0.11 * t ** 2.2 + 0.12 * t * (1 - t) - (0.08 * (1 - t / 0.15) ** 2 if t < 0.15 else 0)
f_y = lambda t: base_y + t * (FH + 0.025)
sh.append(dorsal_sheet("fin", "body", lambda x: smooth(ST, x)[0], f_le, lambda t: f_te(t), f_y, (f_te(1.0) - 0.03, f_y(1.0) - 0.004), 0.034, "@cape", n=48, rows=8, le_max=0.82,
                       fair=FAIR_FIN))

# THE PECTORAL FLIPPERS: pointed, 0.38 m, set low behind the head, swept back, out and down; one sheet each, FAIRED
# into the flank
sd = norm([-0.62, -0.5, 0.6]); cdir = [1.0, -0.1, 0.25]
chord = lambda t: (0.14 - 0.1 * t ** 1.4) * (1 if t < 0.85 else math.sqrt(max(0.0, 1 - ((t - 0.85) / 0.15) ** 2)) * 0.6 + 0.4)
root = [PECT[0] + 0.03, PECT[1], PECT[2] - 0.02]
sh.append(flipper_sheet("pect", "pectL", root, sd, cdir, 0.38, chord, 0.024, "@fin", le_off=lambda t: 0.03 * math.sin(math.pi * t),
                        sweep=lambda t: 0.09 * t * t, sink=0.02, fair=FAIR_PECT, n=96, m=40))
# (2026-11-08, pass 2: n=96 rim samples, m=40 along each edge -- at the default 36 the samples were as far apart as the
#  fillet is wide, and the faired leading-edge root went in steps)

# THE FLUKES: 0.62 m across, the leading edges swept back to pointed tips, the trailing edge concave each side of a
# median notch; ONE sheet rooted across the stock and FAIRED into it (sharp.js `fair`): the stock, low and flattened
# at its end, runs out into the flukes with no stump
YF = 0.012
fl_le = lambda z: -1.12 - 0.42 * (z / 0.31) ** 1.9 * 0.62 + 0.05 * math.exp(-z / 0.03)   # (2026-11-08: swept forward into the stock's side
# near the root, so the leading edge comes out of it at a slant -- square to it, its rim stood out as a spike at each corner)
fl_te = lambda z: -1.4 + 0.03 * math.exp(-z / 0.02) + 0.02 * math.sin(math.pi * min(1.0, z / 0.31)) - 0.1 * (z / 0.31) ** 2.6 - 0.006
sh.append(fluke_sheet2("flukes", "fluke", fl_le, fl_te, lambda z: YF - 0.01 * (z / 0.31) ** 2, 0.31, (fl_te(0.31) - 0.02, 0.318), -1.1, 0.02,
                       0.04, "@cape", n=64, rows=8, nz=16, fair=FAIR_FLUKE, swell=[0.05, 0.12]))

# THE COMMON DOLPHIN'S HOURGLASS (`common`): the dark cape dipping to a V under the dorsal fin; ahead of it a buff-yellow
# THORACIC PATCH from the eye back along the flank, behind it a pale grey patch up the tail stock; the eye ringed dark,
# a dark stripe from the jaw to the flipper. Paints: colour without shape
def paint(id, c, r, color, when, rot=None, k=0.02, mirror=True, kc=None):
    p = S("ell", id=id, c=c, r=r, k=k, kc=kc if kc is not None else k * 2.5, color=color, op="paint", mirror=mirror, when=when)
    if rot: p["rot"] = rot
    return p
sh += [
    paint("thor", [0.5, -0.06, 0.16], [0.4, 0.085, 0.14], "@buff", "common", rot=[0, 0, -4]),
    paint("thorTip", [0.1, -0.075, 0.15], [0.16, 0.05, 0.14], "@buff", "common", rot=[0, 0, -14]),
    paint("rear", [-0.44, -0.02, 0.12], [0.42, 0.075, 0.13], "@grey", "common", rot=[0, 0, 14]),
    paint("rearUp", [-0.75, 0.04, 0.06], [0.2, 0.05, 0.09], "@grey", "common", rot=[0, 0, 10]),
    paint("belly", [0.25, -0.22, 0], [0.75, 0.07, 0.2], "@pale", "common", k=0.03, mirror=False),
    paint("eyeRing", [0.86, -0.02, 0.13], [0.04, 0.03, 0.06], "@dark", "common", k=0.012, kc=0.012),
    paint("flipStripe", [0.78, -0.1, 0.13], [0.16, 0.014, 0.08], "@dark", "common", rot=[0, 0, 32], k=0.01, kc=0.01),
]

for p in sh:
    if p.get("op") not in ("sub", "paint"): p["wet"] = 0.16

d = {
    "name": "dolphin",
    "_about": "SCULPTED (2026-11-07, the sculpt overlay; generator scratchpad sc/sea3/gen/dolphin.py): a BOTTLENOSE dolphin, ~2.6 m -- a sleek spindle deepest ~40% back; the short stout BEAK set off from the rounded MELON by a crease, the lower jaw a shade longer, the long upturned MOUTH LINE; the crescent BLOWHOLE; the FALCATE dorsal fin (0.26 m, the tip curved back) a little behind the middle; pointed PECTORAL flippers swept back; the stock laterally flattened and keeled; 0.62 m flukes with a median notch. COUNTERSHADED (`sculpt.shade`): a dark grey cape over grey flanks to a pale belly. Its coat `common dolphin` (`params.common`, scale .78) paints the short-beaked common dolphin's HOURGLASS instead: the cape dipping to a V under the fin, a buff-yellow thoracic patch ahead of it, a pale grey patch behind, a dark eye ring and a stripe from the jaw to the flipper. A SWIMMER (the fish's plumbing: `fly`, `alt` its depth; index.html addSwimmer, only in a lake, and it leaps). Its tail PITCHES (axis z: the flukes beat up and down), on four bones a beat apart. (2026-11-08) The dorsal fin, the flippers and the flukes (one sheet across both) are `fin` SHEETS (sharp.js; cetlib.py dorsal_sheet / flipper_sheet / fluke_sheet2): the rim exactly the outline, the leading edge blunt, sharp behind, FAIRED into the body (sharp.js `fair`: each face near the body the smooth union of the sheet and the body, a fillet grown out of the skin -- no fillet shapes, no stump), the flukes' middle swollen to the stock's depth (`swell`). (2026-11-08) The stock runs on, tapering, inside the flukes' swollen middle (no round cap: no collar crease under their root), and the flukes' leading edges sweep forward into its sides (no spike where each leaves it). (2026-11-08, pass 2) The sheets' grids are solved harmonic (`grid: \"flow\"`: the columns curve with the outline, no bundle of slivers down a swept fluke or flipper) and their thickness is drawn on a SMOOTH rim distance (sharp.js smoothRimDist): no ridge line down the middle; the flippers sampled finer (96 round the rim: their faired leading-edge root went in steps).",
    "kind": "parts",
    "facet": False,
    "params": {"common": False, "bottle": True},
    "flags": {"fly": {"alt": [0.6, 1.8], "speed": [1.5, 3.2], "hz": HZ}},
    "colors": {"cape": "#5a6672", "pale": "#e2e2de", "dark": "#2a3138", "buff": "#c9b27a", "grey": "#9aa2a8", "fin": "#46505b"},
    "coats": [{"name": "bottlenose dolphin"}, {"name": "bottlenose dolphin"},
              {"name": "common dolphin", "scale": 0.78, "params": {"common": True, "bottle": False}, "cape": "#353d47", "fin": "#353d47", "grey": "#88909a"}],
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mottle": {"amount": 0},
        "shade": {"when": "bottle", "back": "#4c5662", "belly": "#dcdcd8", "k": 0.13, "at": -0.11, "mode": "mix", "on": "@cape", "tol": 0.2},
        "mesh": {"cell": 0.009, "tris": [9000, 2800], "focus": {"head": 3}, "far": 16},
        "shape": sh,
        "eyes": {"at": [0.865, -0.02, 0.125], "from": [0.865, -0.02, 0], "r": 0.011, "color": "#060606", "iris": "#2a1c12", "pupil": "round", "lid": False, "sink": 0.4, "socket": 1.05, "bone": "head"},
    },
}
write_to("sea/dolphin", d)
