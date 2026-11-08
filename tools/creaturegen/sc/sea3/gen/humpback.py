from cetlib import *
import os

# HUMPBACK WHALE (Megaptera novaeangliae), an adult, 14.0 m from the tip of the lower jaw to the fluke notch: the jaw's
# tip at x = +5.0, the notch at -9.0. Rest frame: x forward, y up, z left, metres; the body's axis about y = 0.
L, XS = 14.0, 5.0
X = lambda s: XS - s * L
HZ = 0.3                          # (a slow cruising beat, ~0.3 Hz)

XT = [X(0.56), X(0.72), X(0.86), X(0.95)]
R = Rig()
R.add("body", None, [0, 0, 0], shape=tube_part([3.0, 0, 0], [-2.5, 0, 0], 1.4, 1.2), color="@dark",
      anim={"axis": "z", "deg": 0.5, "speed": HZ, "phase": 2.6})
R.add("head", "body", [2.2, 0, 0], shape={"shape": "sphere", "size": {"r": 1.0}}, color="@dark")
PECT = [X(0.285), -1.05, 1.2]
for side, s in (("L", 1), ("R", -1)):
    R.add(f"pect{side}", "body", [PECT[0], PECT[1], s * PECT[2]], shape={"shape": "sphere", "size": {"r": 0.2}}, color="@dark",
          anim={"axis": "x", "deg": s * 3, "speed": HZ * 0.5, "phase": 0.4})
degs, ph = [2.5, 5.0, 8.0, 13.0], [0.0, -0.55, -1.1, -1.75]
par, x0 = "body", 0.0
for j, x in enumerate(XT):
    nm = f"tail{j + 1}" if j < 3 else "fluke"
    R.add(nm, par, [x - x0, 0.0, 0], shape={"shape": "sphere", "size": {"r": 0.6 - 0.12 * j}}, color="@dark",
          anim={"axis": "z", "deg": degs[j], "speed": HZ, "phase": ph[j]})
    par, x0 = nm, x
def bone_x(x):
    if x > 2.2: return "head"
    for b, xb in zip(["body", "tail1", "tail2", "tail3"], XT):
        if x > xb: return b
    return "fluke"

# a table's value at s (Catmull-Rom through the (s, v...) rows)
def tab(T, s, k=1):
    if s <= T[0][0]: return T[0][k]
    if s >= T[-1][0]: return T[-1][k]
    for i in range(len(T) - 1):
        if T[i][0] <= s <= T[i + 1][0]: break
    p0, p1, p2, p3 = T[max(0, i - 1)][k], T[i][k], T[i + 1][k], T[min(len(T) - 1, i + 2)][k]
    t = (s - T[i][0]) / (T[i + 1][0] - T[i][0])
    return 0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (3 * p1 - p0 - 3 * p2 + p3) * t ** 3)
sx = lambda x: (XS - x) / L

# THE BODY: ROBUST -- the trunk round (s, the axis's height, radius), deepest just behind the flippers (3.5 m with the
# throat: a quarter of the length), the stock tapering hard behind the hump; under it the THROAT and BELLY (s, its bottom,
# radius): one big rounded sagging volume from the chin to the navel, the pleated part
TR = [(0.17, -0.45, 0.8), (0.2, -0.42, 1.02), (0.23, -0.4, 1.2), (0.27, -0.38, 1.4), (0.3, -0.36, 1.52), (0.34, -0.35, 1.6),
      (0.4, -0.3, 1.6), (0.46, -0.25, 1.5), (0.52, -0.17, 1.35), (0.58, -0.05, 1.15), (0.63, 0.03, 0.95), (0.68, 0.08, 0.76),
      (0.73, 0.1, 0.6), (0.79, 0.1, 0.44), (0.86, 0.08, 0.29), (0.91, 0.07, 0.2), (0.945, 0.06, 0.15), (0.97, 0.05, 0.12)]
TH = [(0.0, -0.86, 0.3), (0.04, -1.15, 0.5), (0.08, -1.4, 0.68), (0.13, -1.62, 0.84), (0.19, -1.82, 0.97), (0.26, -2.0, 1.08),
      (0.33, -2.15, 1.15), (0.39, -2.2, 1.15), (0.45, -2.1, 1.1), (0.5, -1.85, 0.95), (0.55, -1.5, 0.75), (0.58, -1.2, 0.55)]
ST = [(X(s), yc + r, yc - r, r) for s, yc, r in TR]
PAT = "humpback"
sh = trunk_tubes(ST, [ST[0][0], 2.2, XT[0], XT[1], XT[2], XT[3], ST[-1][0]], ["head", "body", "tail1", "tail2", "tail3", "fluke"], "@dark",
                 k=0.25, pat=PAT, step=0.15, ov=0.25, rfun=lambda t, b, w: w)
for j, (s0, s1, bn) in enumerate([(0.0, sx(2.2) + 0.02, "head"), (sx(2.2) - 0.02, 0.58, "body")]):
    n = int((s1 - s0) / 0.012) + 2
    pts = []
    for i in range(n):
        s = s0 + (s1 - s0) * i / (n - 1); r = tab(TH, s, 2)
        pts.append([X(s) - (0.2 if s == 0 else 0), tab(TH, s, 1) + r, 0, r])
    sh.append(S("tube", id=f"throat{j}", bone=bn, pts=pts, k=0.3, color="@dark", pat=PAT))
trunk_top = lambda x: tab(TR, sx(x), 1) + tab(TR, sx(x), 2)
trunk_bot = lambda x: tab(TR, sx(x), 1) - tab(TR, sx(x), 2)

# THE HEAD (a third of the length): the ROSTRUM a broad flat plate, rounded seen from above, its edge rising back from
# the tip; under it the massive LOWER JAW -- two bowed rami, wider than the rostrum and a little ahead of it, their tops
# the MOUTH LINE (LIP): it arches up along the side and drops just in front of the eye to the corner, the eye above it
RX, RY, RZ, RC, RSL = 1.35, 0.25, 1.0, [X(0.105), -0.2, 0], 0.2
ru, rv, rw = frame([1, -RSL, 0], [0, 1, 0])
sh.append(oell("rostrum", RC, [RX, RY, RZ], ru, rv, rw, bone="head", k=0.2, color="@dark", pat=PAT))
def rost_top(x):
    u = (x - RC[0]) / RX
    return -1e9 if abs(u) >= 1 else RC[1] - RSL * (x - RC[0]) + RY * math.sqrt(1 - u * u)
LIP = [(0.0, -0.48), (0.03, -0.42), (0.07, -0.31), (0.11, -0.2), (0.15, -0.1), (0.175, -0.08), (0.19, -0.16), (0.2, -0.3), (0.207, -0.42)]
WJ = [(0.0, 0.26), (0.03, 0.62), (0.07, 0.95), (0.11, 1.15), (0.15, 1.24), (0.19, 1.22), (0.207, 1.16)]
RJ = [(0.0, 0.26), (0.03, 0.34), (0.07, 0.42), (0.11, 0.47), (0.15, 0.5), (0.19, 0.5), (0.207, 0.46)]
pts = []
n = 24
for i in range(n):
    s = 0.207 * i / (n - 1); r = tab(RJ, s)
    pts.append([X(s) - (0.25 if i == 0 else 0), tab(LIP, s) - r, max(0.0, tab(WJ, s) - r), r])
sh.append(S("tube", id="ramus", bone="head", pts=pts, k=0.12, color="@dark", pat=PAT, mirror=True))
def head_top(x):
    return max(rost_top(x), trunk_top(x) if sx(x) >= 0.17 else -1e9, tab(LIP, sx(x)) if sx(x) <= 0.207 else -1e9)
top = lambda x: head_top(x) if sx(x) < 0.3 else trunk_top(x)
bot = lambda x: trunk_bot(x) if sx(x) > 0.58 else min(trunk_bot(x), tab(TH, sx(x), 1))
BX = X(0.178)
sh += [S("ell", id="guard", bone="head", c=[BX + 0.24, head_top(BX + 0.24), 0], r=[0.22, 0.1, 0.32], k=0.12, color="@dark", pat=PAT,
         seat={"from": [BX + 0.24, -1.0, 0], "out": -0.45})]
sh.append(oell("blow", [BX, head_top(BX) + 0.03, 0.11], [0.2, 0.06, 0.045], *frame(norm([1, 0, -0.35]), [0, 1, 0]), bone="head", k=0.03,
               color="@dark", op="sub", mirror=True))
# THE TUBERCLES: distinct round knobs like golf balls -- a median row and two rows either side along the rostrum, rows on
# the lower jaw's tip and sides, and the big knobby lump of the chin
def knob(id, x, y, z, r, mirror=True, frm=None, out=0.05):
    return S("sphere", id=id, bone="head", c=[x, y, z], r=r, k=0.02, color="@dark", pat=PAT, mirror=True if mirror else None,
             seat={"from": frm or [x, y - 1.0, 0], "out": out})
import random
rng = random.Random(7)
for row, (zf, n0) in enumerate([(0.0, 0), (0.3, 1), (0.58, 0)]):
    s = 0.02 + 0.007 * n0
    i = 0
    while s < 0.16:
        x = X(s)
        u = (x - RC[0]) / RX; hw = RZ * math.sqrt(max(0.0, 1 - u * u))
        z = zf * hw + rng.uniform(-0.03, 0.03)
        sh.append(knob(f"tub{row}_{i}", x, head_top(x) + 0.3, z, 0.14 + rng.uniform(-0.015, 0.015), mirror=row > 0,
                       frm=[x, head_top(x) - 0.8, z * 0.4], out=0.25))
        s += 0.029 + rng.uniform(-0.003, 0.004); i += 1
# (the jaw: two rows along each side of the front half, below the lip)
for row, dy in enumerate([0.32, 0.62]):
    for i, s in enumerate([0.012, 0.03, 0.05, 0.072, 0.095, 0.12][: 6 - 2 * row]):
        x = X(s); y = tab(LIP, s) - dy * tab(RJ, s) * 1.6
        sh.append(knob(f"jtub{row}_{i}", x, y, tab(WJ, s) + 0.3, 0.11 + rng.uniform(-0.01, 0.01), frm=[x, y, 0]))
# (the chin's lump: a big boss under the jaw's tip, knobs on it)
sh.append(S("ell", id="chinboss", bone="head", c=[X(0.012), -0.9, 0], r=[0.38, 0.26, 0.3], k=0.1, color="@dark", pat=PAT,
            seat={"from": [X(0.06), -0.5, 0], "out": -0.4}))
for i, (dx, dy, dz) in enumerate([(0.12, -0.62, 0.0), (0.02, -0.82, 0.15), (-0.2, -0.88, 0.22), (-0.15, -1.02, 0.0), (0.1, -0.78, 0.3)]):
    sh.append(knob(f"boss{i}", X(0.0) + dx, dy, dz, 0.11, mirror=dz > 0, frm=[X(0.0) - 0.7, -0.55, 0]))
# the stock's keels and the KNUCKLES: the low bumps along the ridge from the fin to the flukes
sh += [S("tube", id="keelD", bone=bone_x(x), pts=[[x + 0.5, top(x + 0.5) - 0.1, 0, 0.1], [x - 0.5, top(x - 0.5) - 0.05, 0, 0.08]],
         k=0.12, color="@dark", pat=PAT) for x in [X(0.75), X(0.81), X(0.87), X(0.92)]]
sh += [S("tube", id="keelV", bone=bone_x(x), pts=[[x + 0.45, bot(x + 0.45) + 0.1, 0, 0.1], [x - 0.45, bot(x - 0.45) + 0.05, 0, 0.07]],
         k=0.12, color="@dark", pat=PAT) for x in [X(0.8), X(0.86), X(0.91)]]
for i, s in enumerate([0.705, 0.74, 0.775, 0.81, 0.845]):
    x = X(s)
    sh.append(S("ell", id=f"knuckle{i}", bone=bone_x(x), c=[x, top(x), 0], r=[0.2, 0.09, 0.09 - 0.008 * i], k=0.08, color="@dark", pat=PAT,
                seat={"from": [x, 0.0, 0], "out": -0.35}))

# THE DORSAL FIN: small and low (0.35 m), set on a HUMP two thirds of the way back -- the whale's name
FB0, FB1 = X(0.625), X(0.672)
xm = (FB0 + FB1) / 2
sh.append(S("ell", id="hump", c=[xm + 0.25, top(xm + 0.25) - 0.12, 0], r=[1.0, 0.3, 0.42], k=0.3, color="@dark", pat=PAT, bone=bone_x(xm)))
base_y = top(xm) + 0.05
HC, HR = [xm + 0.25, top(xm + 0.25) - 0.12], [1.0, 0.3]
skin = lambda x: max(top(x), HC[1] + HR[1] * math.sqrt(max(0.0, 1 - ((x - HC[0]) / HR[0]) ** 2)))
f_le = lambda t: lerpf(FB0 + 0.15, FB1 - 0.2, t ** 0.8) + 0.2 * (1 - t) ** 3
f_te = lambda t: lerpf(FB1 - 0.05, FB1 - 0.32, t ** 0.6)
f_y = lambda t: base_y + t * 0.38
# ONE SHEET (sharp.js `fin`): the rim exactly the outline, its foot FAIRED into the hump (`fair`)
sh.append(dorsal_sheet("fin", bone_x(xm), skin, f_le, f_te, f_y, (FB1 - 0.31, f_y(1.0) + 0.03), 0.2, "@dark", sink=0.12, slope=0.5, pat=PAT,
                       n=40, rows=7, le_max=0.9, fair={"r": 0.25}))

# THE FLIPPERS: a third of the length (4.5 m), long narrow wings hanging down, out and back; their leading edges KNOBBED
# (the tubercles that let a humpback turn tight: scallops of the sheet's rim, blunt), the trailing edge smooth; white,
# mottled dark (the pattern)
sd = norm([-0.6, -0.45, 0.66]); cdir = [1.0, 0.1, 0.3]
FLEN = 4.5
fchord = lambda t: 0.88 * (1 - 0.58 * t ** 1.3) * (math.sqrt(max(0.0, 1 - ((t - 0.85) / 0.15) ** 2)) if t > 0.85 else 1.0)
froot = [PECT[0] + 0.1, PECT[1], PECT[2] - 0.1]
fsweep = lambda t: 0.3 * t * t
def tubercles(t):
    if t < 0.2 or t > 0.93: return 0.0
    u = (t - 0.2) / 0.065
    return lerpf(0.09, 0.045, (t - 0.2) / 0.73) * abs(math.sin(math.pi * u)) ** 0.7 * min(1.0, (t - 0.2) / 0.04, (0.93 - t) / 0.04)
sh.append(flipper_sheet("pect", "pectL", froot, sd, cdir, FLEN, fchord, 0.26, "@dark", le_off=tubercles, sweep=fsweep, sink=0.15, blunt=2.2, slope=0.6,
                        pat=PAT, m=110, n=220, rows=8, corner=False, fair={"r": 0.15}))

# THE FLUKES: 4.6 m across, the leading edges swept back to pointed tips, the TRAILING EDGE SERRATED, the median notch;
# ONE sheet across both (its rim the serrated outline exactly), FAIRED into the stock (sharp.js `fair`), its middle
# swollen to the stock's thickness (`swell`)
YF = 0.03
FX0 = X(0.94)
fsd = norm([-0.52, 0, 1.0])
FSPAN = 2.4
flc = lambda t: 1.15 * (1 - t ** 1.6) ** 0.9 + 0.02
notch = lambda t: 0.2 * math.exp(-t / 0.06)
serr = lambda t: (0.12 * (0.5 + 0.5 * math.sin(2 * math.pi * (8 * t + 0.6 * t * t))) ** 2 * min(1, t / 0.12)) * (1 - t) ** 0.6 + notch(t)
flo = lambda inset, tmax, te=None: blade_outline([FX0, YF, 0.0], fsd, [1, 0, 0], FSPAN, flc, le_off=lambda t: 0.12 * math.sin(math.pi * t) ** 0.8,
                                                n=36 if te else 12, inset=inset, tmax=tmax, te_fn=te)   # (the pattern's outline of the white underside)
NF = 120
FO = blade_outline([FX0, YF, 0.0], fsd, [1, 0, 0], FSPAN, flc, le_off=lambda t: 0.12 * math.sin(math.pi * t) ** 0.8, n=NF, te_fn=serr)
# (2026-11-08, pass 2: the root's ends on the leading edges, "le" -- 10 cm ahead of them the rim ran back along the stock
#  into a concave corner and the sheet folded there: the pinched leading-edge root)
sh.append(fluke_sheet_blade("flukes", "fluke", FO[:NF + 1], FO[NF + 1:][::-1], "le", 0.14, 0.24, "@dark", slope=0.45, pat=PAT, n=260, rows=8,
                             fair={"r": 0.22}, swell=[0.28, 0.7]))

d = {
    "name": "humpback",
    "_about": "SCULPTED (2026-11-06, the sculpt overlay; generator scratchpad sc/sea3/gen/humpback.py): a humpback whale, an adult, 14 m -- ROBUST: 3.5 m deep (a quarter of the length), deepest just behind the flippers, the throat and belly one big rounded sagging pleated volume, the stock tapering hard behind the hump; the head a third of the length, the rostrum broad and flat, the massive bowed LOWER JAW wider than it and a little ahead, the mouth line arching up along the side and dropping just before the eye to its corner; the TUBERCLES (golf-ball knobs: a median row and two rows either side on the rostrum, rows on the jaw's tip, the chin's knobby lump), the splashguard and paired blowholes; the long white FLIPPERS (4.5 m, a third of the length) with KNOBBED leading edges; the small dorsal fin on its HUMP and the knuckles behind it; 4.6 m flukes with a SERRATED trailing edge. Its COLOURS are one per-pixel pattern (coatpat.js 42 `humpback`, in the rest pose's own space): the dark back (matte, mottled, paler down the flanks, pale scars), the white belly mottled and blotched, the THROAT PLEATS (grooves from the chin to the navel), the white flippers, the flukes' white underside (out on the blades) with its black margin and blotches, the belly's white running out along the stock so that the stock and the flukes' root are dark all round (2026-11-08). A SWIMMER of the open sea (index.html seaLife: one or two far offshore, surfacing to BLOW, now and then diving flukes-up). Its tail PITCHES (axis z): the flukes beat up and down. (2026-11-08) The dorsal fin, the flippers (their KNOBBED leading edges scallops of the rim) and the flukes (one sheet, the SERRATED trailing edge in its outline) are `fin` SHEETS (sharp.js; cetlib.py): the rim exactly the outline, FAIRED into the body (sharp.js `fair`: each face near the body the smooth union of the sheet and the body, a fillet grown out of the skin -- no fillet shapes, no stump), the flukes' middle swollen to the stock's depth (`swell`). (2026-11-08, pass 2) The sheets' grids are solved harmonic (`grid: \"flow\"`: the columns curve with the outline, no bundle of slivers down a swept fluke or flipper) and their thickness is drawn on a SMOOTH rim distance (sharp.js smoothRimDist): no ridge line down the middle; the flukes' root ends on the leading edges (set ahead of them the sheet folded at the leading-edge root).",
    "kind": "parts",
    "facet": False,
    "flags": {"fly": {"alt": [3, 8], "speed": [1.6, 2.4], "hz": HZ}},
    "colors": {"dark": os.environ.get("HC", "#3b4048")},
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mottle": {"amount": 0},
        "mesh": {"cell": 0.068, "tris": [11000, 3400], "focus": {"head": 2.5}, "far": 40},
        "shape": sh,
        "eyes": {"at": [X(0.214), -0.24, 1.3], "from": [X(0.214), -0.24, 0], "r": 0.06, "color": "#060606", "iris": "#2a1c12", "pupil": "round",
                 "lid": False, "sink": 0.4, "socket": 1.05, "bone": "head"},
    },
}
write_to("sea/humpback", d)

# ---- THE COLOURS (coatpat.js humpbackOf) ---------------------------------------------------------------------------
f = lambda v: f"{v:.4f}"
def axs(s):
    x = X(s)
    t = top(x) if s > 0.01 else tab(LIP, s)
    bb = bot(x) if s >= 0.17 else tab(TH, s, 1)
    w = max(tab(TR, s, 2) if s >= 0.17 else 0.0, tab(WJ, s) if s <= 0.207 else 0.0)
    return (round(x, 3), (t + bb) / 2, (t - bb) / 2, w)
AX = [axs(s) for s in [0.0, 0.02, 0.05, 0.09, 0.13, 0.17, 0.21, 0.26, 0.3, 0.34, 0.4, 0.46, 0.52, 0.58, 0.63, 0.68, 0.73, 0.79, 0.86, 0.91, 0.945, 0.97]]
ax = "var AX = array<vec4<f32>, %d>(" % len(AX) + ", ".join(f"vec4<f32>({f(a)}, {f(b)}, {f(c)}, {f(dd)})" for a, b, c, dd in AX) + ");"
# (the flukes' outline in (x, |z|), in from the edge by a margin: the underside's white)
out = flo(0, 1.0)
M = 0.09
cx = sum(p[0] for p in out) / len(out); cz = sum(p[2] for p in out) / len(out)
FL = [(p[0] + (cx - p[0]) * 0.07, p[2] + (cz - p[2]) * 0.07) for p in out]
fl_arr = "var V = array<vec2<f32>, %d>(" % len(FL) + ", ".join(f"vec2<f32>({f(x)}, {f(z)})" for x, z in FL) + ");"
NAV = X(0.52)
lp = "var LP = array<vec2<f32>, %d>(" % len(LIP) + ", ".join(f"vec2<f32>({f(X(s))}, {f(y)})" for s, y in LIP) + ");"
W = dict(LIP=lp, NL=len(LIP), AX=ax, NA=len(AX), FL=fl_arr, NF=len(FL), XF=FX0 + 0.05, YF=YF, NAV=NAV, CHIN=X(0.0), PX=(X(0.24), X(0.62)))
json.dump(W, open("humpback_wgsl.json", "w"), indent=1)
