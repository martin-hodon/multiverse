from cetlib import *

# GREAT WHITE SHARK (Carcharodon carcharias), 3.2 m from the snout to the tail's tip: the snout at x = +1.45, the upper
# lobe's tip near -1.75. Rest frame: x forward, y up, z left, metres. Params gate the head: `pointed` (the white's
# conical snout) or `hm` (1: a HAMMERHEAD's cephalofoil, the eyes at its ends); `spots` the whale shark's pale spots.
HZ = 0.7
XT = [-0.35, -0.75, -1.08, -1.3]
R = Rig()
R.add("body", None, [0, 0, 0], shape=tube_part([1.0, 0, 0], [-0.4, 0, 0], 0.32, 0.28), color="@skin",
      anim={"axis": "y", "deg": 1.2, "speed": HZ, "phase": 2.6})
R.add("head", "body", [0.95, 0, 0], shape={"shape": "sphere", "size": {"r": 0.22}}, color="@skin",
      anim={"axis": "y", "deg": 1.5, "speed": HZ, "phase": 3.0})
PECT = [0.72, -0.2, 0.2]
for side, s in (("L", 1), ("R", -1)):
    R.add(f"pect{side}", "body", [PECT[0], PECT[1], s * PECT[2]], shape={"shape": "sphere", "size": {"r": 0.04}}, color="@skin",
          anim={"axis": "x", "deg": s * 3, "speed": HZ * 0.5, "phase": 0.4})
degs, ph = [4.0, 8.0, 11.0, 16.0], [0.0, -0.55, -1.1, -1.75]
par, x0 = "body", 0.0
for j, x in enumerate(XT):
    nm = f"tail{j + 1}" if j < 3 else "tail"
    R.add(nm, par, [x - x0, 0.0, 0], shape={"shape": "sphere", "size": {"r": 0.14 - 0.03 * j}}, color="@skin",
          anim={"axis": "y", "deg": degs[j], "speed": HZ, "phase": ph[j]})
    par, x0 = nm, x
def bone_x(x):
    if x > 0.95: return "head"
    if x > XT[0]: return "body"
    if x > XT[1]: return "tail1"
    if x > XT[2]: return "tail2"
    if x > XT[3]: return "tail3"
    return "tail"

# THE BODY (x, top, bottom, half width): a heavy spindle, deepest a third back, the snout a blunt cone over the
# underslung mouth; the caudal peduncle slim, flattened top to bottom and widened by its lateral KEELS
ST = [(1.2, 0.12, -0.18, 0.13), (1.1, 0.155, -0.225, 0.165), (0.98, 0.195, -0.27, 0.195), (0.8, 0.24, -0.315, 0.232), (0.55, 0.28, -0.35, 0.262),
      (0.3, 0.3, -0.355, 0.27), (0.0, 0.29, -0.325, 0.255), (-0.3, 0.25, -0.27, 0.22), (-0.6, 0.18, -0.185, 0.15), (-0.88, 0.12, -0.105, 0.095),
      (-1.08, 0.085, -0.06, 0.07), (-1.2, 0.068, -0.042, 0.068), (-1.3, 0.06, -0.034, 0.05)]
sh = trunk_tubes(ST, [1.22, 0.95, XT[0], XT[1], XT[2], XT[3], ST[-1][0]], ["head", "body", "tail1", "tail2", "tail3", "tail"], "@skin",
                 step=0.06, ov=0.06, k=0.05, pat={"when": "spots", "v": "palespots"}, rfun=lambda t, b, w: w + 0.3 * ((t - b) / 2 - w))
# (the whale shark's spots laid in ONE frame for the whole trunk -- the rest pose's space at the trunk's girth -- so they
#  are one size from snout to tail and the tubes' seams cannot garble them; the tail fin takes the same frame)
for p in sh:
    if p.get("pat"): p["patFrame"] = {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.26}
# the peduncle's lateral keels
sh += [S("tube", id="keel", bone=bone_x(x), pts=[[x + 0.1, 0.005, smooth(ST, x + 0.1)[2] - 0.01, 0.012], [x - 0.1, 0.008, smooth(ST, x - 0.1)[2] - 0.004, 0.014]],
         k=0.015, color="@skin", mirror=True) for x in [-1.06, -1.2]]

# THE SNOUT (`pointed`): a blunt cone over the mouth, the nostrils under its tip
SN = [[1.15, 0.015, 0, 0.17], [1.25, 0.025, 0, 0.125], [1.34, 0.03, 0, 0.082], [1.42, 0.03, 0, 0.044], [1.475, 0.026, 0, 0.016]]
sh += [S("tube", id="snout", bone="head", pts=SN, k=0.04, color="@skin", when="pointed"),
       S("ell", id="snoutLow", bone="head", c=[1.24, -0.08, 0], r=[0.13, 0.075, 0.115], k=0.04, color="@skin", when="pointed"),
       S("ell", id="nostril", bone="head", c=[1.38, -0.045, 0.045], r=[0.022, 0.006, 0.01], rot=[0, 25, 0], k=0.004, color="@dark", op="sub", mirror=True, when="pointed")]
# THE HAMMERHEAD'S CEPHALOFOIL (`hm`): a flat, broad wing across the front of the head, its front edge bowed and notched,
# the eyes at its ends
# (a blade of overlapping lobes out to each end: its chord narrowing a little, swept back, blunt at the eyes)
sh += [S("ell", id=f"foil{j}", bone="head", c=[1.31 - 0.2 * (z / 0.4) ** 1.6, 0.008, z], r=[0.15 - 0.07 * z / 0.4, 0.045 - 0.012 * z / 0.4, 0.075], k=0.04,
         color="@skin", mirror=True, when="hm") for j, z in enumerate([0.03, 0.1, 0.17, 0.24, 0.31, 0.37])]
sh += [S("ell", id="foilC", bone="head", c=[1.27, 0.0, 0], r=[0.13, 0.055, 0.16], k=0.05, color="@skin", when="hm"),
       S("ell", id="foilTip", bone="head", c=[1.12, 0.01, 0.405], r=[0.055, 0.04, 0.04], k=0.025, color="@skin", mirror=True, when="hm"),
       S("ell", id="foilNotch", bone="head", c=[1.39, 0.0, 0.0], r=[0.025, 0.06, 0.03], k=0.01, color="@skin", op="sub", when="hm")]
# THE MOUTH: a wide crescent under the head, the corners running back; and the LOWER JAW's rim
MO = [(1.2, -0.172, 0.0), (1.17, -0.174, 0.07), (1.11, -0.168, 0.125), (1.05, -0.152, 0.16)]
sh += [S("tube", id="mouth", bone="head", pts=[[x, y, z, 0.012 if i < 3 else 0.008] for i, (x, y, z) in enumerate(MO)], k=0.006, color="@dark", op="sub", mirror=True)]
# THE FIVE GILL SLITS: tall arcs on each side ahead of the pectorals, the last the shortest
for i in range(5):
    x = 0.96 - i * 0.055
    top, bot, hw = smooth(ST, x)
    yc, hh = (top + bot) / 2, (top - bot) / 2
    r = hw + 0.3 * (hh - hw)   # (the trunk tube's real radius here -- see trunk_tubes' rfun; on hw alone they sat inside it)
    if abs(x - 0.95) < 0.06: r += 0.05 / 4   # (where the head's and the body's trunk tubes overlap their smooth union swells k/4)
    pts = []
    for j in range(4):
        y = yc + hh * (0.25 - 0.55 * j / 3) * (1 - 0.06 * i)
        z = math.sqrt(max(0.0, r * r - (y - yc) ** 2)) + 0.002
        pts.append([x - 0.012 * j, y, z, 0.011])
    sh.append(S("tube", id=f"gill{i}", bone="head" if x > 0.95 else "body", pts=pts, k=0.004, kc=0.004, color="#2a3036", op="paint", mirror=True))

def vfin(id, bone, x0, x1, y0, h, sweep, n, th0, color="@fin", down=False, conc=0.25):
    """a fin standing on (or hanging from) the back: horizontal slices, the leading edge swept back by `sweep`, the
    trailing edge concave"""
    out = []
    for i in range(n):
        t = i / (n - 1)
        y = y0 + (-1 if down else 1) * t * h
        le = x0 - sweep * t ** 1.1
        te = x1 - (sweep - (x0 - x1) * 0.1) * t ** 1.6 + conc * (x0 - x1) * math.sin(math.pi * t) * 0.6
        if t < 0.15: le += 0.25 * (x0 - x1) * (1 - t / 0.15) ** 2; te -= 0.15 * (x0 - x1) * (1 - t / 0.15) ** 2
        ch = max(0.012, le - te) if t < 0.97 else 0.016
        th = lerpf(th0, th0 * 0.18, t ** 0.8)
        out.append(S("ell", id=f"{id}{i}", bone=bone, c=[(le + te) / 2, y, 0], r=[ch / 2, h / n * 1.3, th / 2], k=round(min(0.012, th * .3), 4), color=color))
    return out
# (2026-11-07, v5) THE FINS AS EXACT SHEETS. Up to v4 every fin went into the 1 cm grid: the dorsal a stack of flat
# ellipsoids only 1-3 cm thick, the tail, the pectorals' edges and the pelvics triangles about a cell thick -- sampled
# into steps, so every fin edge came out sawtoothed and nicked and the dorsal's tip spurred. Now each fin's OUTLINE is
# one membrane sheet (finsheet.py mfin: drawn as it is, its edge exact and smooth) rooted inside the body, and only a
# thick, well inset CORE (3+ cells) goes into the grid for the bulk at its root -- its edge inside the outline.
sys.path.insert(0, "/home/martin/store/apps/multiverse/tools/creaturegen/sc/sea2/gen")
from finsheet import mfin
def tube_r(x):   # (the trunk tube at x: its middle and radius -- trunk_tubes' rfun)
    t, b, w = smooth(ST, x); return (t + b) / 2, w + 0.3 * ((t - b) / 2 - w)
back = lambda x: sum(tube_r(x))
belly = lambda x: tube_r(x)[0] - tube_r(x)[1]
def qb(p0, c, p2, n, end=False):   # (a quadratic Bezier's points, its end left off unless `end`)
    return [[(1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p2[1], 0]
            for t in [j / n for j in range(n + (1 if end else 0))]]
def median_fin(id, bone, le0, ctl_le, tip, ctl_te, free, te0, down, r, n=12, sink=0.045):
    """a dorsal / anal fin's outline in the midplane, (x, height over the back / under the belly): the leading edge
    convex from le0 to the tip, the trailing edge concave down to its free rear tip, a short edge to te0 on the body,
    and the root buried `sink` under the skin"""
    sgn, base = (-1, belly) if down else (1, back)
    Y = lambda x, h: base(x) + sgn * h
    P = lambda q: (q[0], Y(q[0], q[1]))
    o = qb(P(le0), P(ctl_le), P(tip), n) + qb(P(tip), P(ctl_te), P(free), n) + [list(P(te0)) + [0]]
    o += [[te0[0], Y(te0[0], -sink), 0], [(le0[0] + te0[0]) / 2, Y((le0[0] + te0[0]) / 2, -sink), 0], [le0[0] + 0.02, Y(le0[0] + 0.02, -sink), 0]]
    if down: o = o[::-1]
    return mfin(o, r, "@fin", bone=bone, id=id, smooth=1, rays=False)
# THE FIRST DORSAL: a tall stiff triangle, 0.42 m, the leading edge convex, the trailing edge concave to a free rear tip
sh += median_fin("dorsal", "body", (0.3, 0.0), (0.19, 0.28), (-0.07, 0.42), (-0.04, 0.2), (-0.15, 0.02), (-0.122, 0.0), False, 0.005)
#   its root: one smooth fillet in the grid, 6 cm thick, its top 8 cm up (a stack of thin slices up the middle showed
#   as a stepped ridge through the sheet)
sh.append(S("ell", id="dorsalC", bone="body", c=[0.08, back(0.08) - 0.01, 0], r=[0.17, 0.09, 0.03], k=0.02, color="@fin"))
# the small SECOND DORSAL and the ANAL fin (no core: a sheet rooted in the stock)
sh += median_fin("dorsal2", "tail2", (-0.855, 0.0), (-0.872, 0.048), (-0.925, 0.062), (-0.928, 0.03), (-0.978, 0.012), (-0.955, 0.0), False, 0.003, n=8, sink=0.025)
sh += median_fin("anal", "tail2", (-0.875, 0.0), (-0.89, 0.044), (-0.935, 0.056), (-0.936, 0.028), (-0.985, 0.011), (-0.962, 0.0), True, 0.003, n=8, sink=0.025)

# THE PECTORALS: long, stiff, falcate -- 0.6 m, out, back and a little down from behind the gills; the sheet its exact
# outline, a smooth pad in the grid the bulk of its root (its edge well inside the sheet's)
#   (2026-11-07) rooted higher on the flank and hung 30 degrees down, so the sheet meets the skin square on: rooted on
#   the lower flank at 21 degrees it ran in nearly tangent and its root showed as a long ragged plank under the belly
sd = norm([-0.45, -0.45, 0.77]); cdir = [1.0, 0.0, 0.0]
chord = lambda t: (0.3 - 0.24 * t ** 1.2) * (1 if t < 0.88 else math.sqrt(max(0.0, 1 - ((t - 0.88) / 0.12) ** 2)) * 0.6 + 0.4)
_yc, _r = tube_r(PECT[0] + 0.03)
root = [PECT[0] + 0.03, -0.16, math.sqrt(_r * _r - (-0.16 - _yc) ** 2) - 0.03]
ol = lambda inset, tmax: blade_outline(root, sd, cdir, 0.6, chord, le_off=lambda t: 0.04 * math.sin(math.pi * t), sweep=lambda t: 0.2 * t ** 1.6, n=16, inset=inset, tmax=tmax)
#   (the root closed 6 cm deeper into the flank -- its edge showed, stood off the belly; the inset plate core sampled
#   into a lumpy slab, so a smooth pad at the root instead)
sh += mfin(bury(ol(0, 1.0), sd, 0.06), 0.004, "@fin", bone="pectL", id="pect", mirror=True, smooth=1, rays=False)
sh += root_pad("pectC", root, sd, cdir, chord(0), 0.024, "pectL", "@fin", k=0.02, along=0.05, mirror=True)
# THE PELVIC FINS: small, under the belly behind the middle (the root 1 cm inside the belly: it stood 4 cm out)
sdp = norm([-0.6, -0.5, 0.6])
chp = lambda t: (0.13 - 0.08 * t) * (1 if t < 0.8 else max(0.3, 1 - (t - 0.8) * 3))
olp = blade_outline([-0.52, -0.155, 0.06], sdp, [1, 0, 0], 0.2, chp, n=8)
sh += mfin(bury(olp, sdp, 0.04), 0.003, "@fin", bone="tail1", id="pelv", mirror=True, smooth=1, rays=False)

# THE TAIL: near LUNATE, the upper lobe a little the longer -- one sheet in the midplane (its outline exact), the
# leading edges convex, the trailing edges near straight to the fork; a thick core in the grid at its root
def edge_pts(a, b, bulge, n):
    nx, ny = -(b[1] - a[1]), b[0] - a[0]; l = math.hypot(nx, ny); nx, ny = nx / l, ny / l
    return [[a[0] + (b[0] - a[0]) * t + bulge * math.sin(math.pi * t) * nx, a[1] + (b[1] - a[1]) * t + bulge * math.sin(math.pi * t) * ny, 0] for t in [j / n for j in range(n)]]
A, TU, F, TL, B = (-1.24, 0.05), (-1.8, 0.6), (-1.5, 0.025), (-1.66, -0.42), (-1.24, -0.03)
cau = edge_pts(A, TU, 0.045, 14) + edge_pts(TU, F, -0.03, 10) + edge_pts(F, TL, -0.02, 9) + edge_pts(TL, B, 0.035, 12)
sh += mfin(cau, 0.005, "@fin", bone="tail", id="caud", smooth=1, rays=False, pat={"when": "spots", "v": "palespots"})
#   its root: the stock drawn out to a point into the sheet (the trunk ends in a round cap at -1.3), and a long thin
#   ellipsoid up into each lobe's base, 4 cm in behind its leading edge (a thick triangle there sampled into a lump)
sh.append(S("cone", id="caudCs", bone="tail", a=[-1.22, 0.014, 0], b=[-1.44, 0.02, 0], ra=0.045, rb=0.004, k=0.03, color="@fin"))
sh.append(S("ell", id="caudCu", bone="tail", c=[-1.365, 0.088, 0], r=[0.12, 0.03, 0.02], rot=[0, 0, -44.5], k=0.03, color="@fin"))
sh.append(S("ell", id="caudCl", bone="tail", c=[-1.337, -0.05, 0], r=[0.11, 0.028, 0.018], rot=[0, 0, 48.2], k=0.03, color="@fin"))

for p in sh:
    if p.get("op") not in ("sub", "paint") and p.get("type") != "membrane": p["wet"] = 0.1

EYE = ["1.215-0.075*hm", "0.035-0.02*hm", "0.105+0.335*hm"]
d = {
    "name": "shark",
    "_about": "SCULPTED (2026-11-07, the sculpt overlay; generator scratchpad sc/sea3/gen/shark.py): a GREAT WHITE, ~3.2 m -- a heavy spindle deepest a third back, the conical snout over a wide underslung crescent MOUTH, the black eye, FIVE GILL SLITS ahead of the long stiff falcate PECTORALS, the tall triangular FIRST DORSAL (its trailing edge concave), the small second dorsal and anal fins, the pelvics, the slim peduncle with its lateral KEELS and a near-LUNATE tail (the upper lobe a little the longer); sharply countershaded (`sculpt.shade`): slate above, white below. Its params gate the head and the coat: `pointed` the white's snout, `hm` (1) a hammerhead's CEPHALOFOIL with the eyes at its ends, `spots` the whale shark's pale spots (coatpat.js `palespots`; laid in ONE frame for the whole trunk, `patFrame`, so they are one size and the tubes' seams cannot garble them). COATS: great white (twice), blue shark (indigo over white, slimmer at .9). VARIANTS: `hammerhead` (great hammerhead, 1.1), `whale shark` (3.5: ~11 m, dark blue-grey with pale spots). A SWIMMER (the fish's plumbing: `fly`, `alt` its depth; index.html addSwimmer, only in a lake; it never leaps). Its tail SWEEPS (axis y: side to side), on four bones a beat apart.",
    "kind": "parts",
    "facet": False,
    "params": {"pointed": True, "hm": 0, "spots": False},
    "flags": {"fly": {"alt": [0.4, 1.4], "speed": [1.2, 2.4], "hz": HZ}},
    "colors": {"skin": "#5e6a74", "fin": "#505c66", "pale": "#ecebe6", "dark": "#1c2126"},
    "coats": [{"name": "great white"}, {"name": "great white"},
              {"name": "blue shark", "scale": 0.9, "skin": "#2f5a9a", "fin": "#284e86", "pale": "#eef0f2"}],
    "variants": {
        "hammerhead": {"scale": 1.1, "params": {"pointed": False, "hm": 1}, "colors": {"skin": "#7a7f74", "fin": "#6c7166", "pale": "#e8e6dc"}},
        "whale shark": {"scale": 3.5, "params": {"spots": True, "pointed": False}, "colors": {"skin": "#3c4a58", "fin": "#34414e", "pale": "#d8dcd8"}},
    },
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mottle": {"amount": 0},
        "shade": {"back": "@skin", "belly": "@pale", "k": 0.03, "at": -0.07, "mode": "mix", "on": "@skin", "tol": 0.012},
        "mesh": {"cell": 0.01, "tris": [9500, 3000], "focus": {"head": 3}, "far": 16},
        "shape": sh,
        "eyes": {"at": EYE, "from": [EYE[0], EYE[1], 0], "r": 0.016, "color": "#050505", "iris": "#101010", "pupil": "round", "lid": False, "sink": 0.35, "socket": 1.05, "bone": "head"},
    },
}
write_to("sea/shark", d)
