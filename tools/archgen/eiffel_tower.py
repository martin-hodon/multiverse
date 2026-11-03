# THE EIFFEL TOWER, Paris (1887-89, Gustave Eiffel; Koechlin and Nouguier the structure, Sauvestre the arches): wrought iron, 300m to
# its top and 330m with today's mast, on a square of 125m. Four LEGS, each a square lattice box 25m across at its foot, lean in on a
# curve set by the wind -- the outer edges nearly exponential -- to merge above the second floor in one SHAFT; three floors (57.6, 115.7
# and 276m); four ARCHES, ornament that carries nothing, under the first floor's girders; the lantern on top.
#   Every member is a `truss` or `bars` part (arch/truss.js): real tubes with the sky between them, far cheaper than carved stone.
#   The lattice comes at two scales: the legs' great diagonals, and the fine lattice of the chords themselves.
#   Outer edge and inner edge are one table each of half-widths against height (Wo, Wi); everything leaning is set from them.
#   Symmetric about both axes: x and z are the same. Numbers are worked here and written as numbers.
import os, json, math, bisect
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
r3 = lambda v: round(v, 3)
pt = lambda p: [r3(p[0]), r3(p[1]), r3(p[2])]
TOP1, TOP2, TOP3 = 57.6, 115.7, 276.0            # the three floors
MERGE = 180.0                                    # where the legs have come together

def table(rows):
    """a smooth curve through (y, half-width) rows: a cubic through each span, its slopes the neighbours' (Catmull-Rom on uneven knots)"""
    ys = [r[0] for r in rows]; vs = [r[1] for r in rows]; n = len(ys)
    d = [(vs[min(i + 1, n - 1)] - vs[max(i - 1, 0)]) / (ys[min(i + 1, n - 1)] - ys[max(i - 1, 0)]) for i in range(n)]
    def f(y):
        i = max(0, min(n - 2, bisect.bisect_right(ys, y) - 1)); h = ys[i + 1] - ys[i]; t = (y - ys[i]) / h
        return ((2 * t**3 - 3 * t**2 + 1) * vs[i] + (t**3 - 2 * t**2 + t) * h * d[i] + (-2 * t**3 + 3 * t**2) * vs[i + 1] + (t**3 - t**2) * h * d[i + 1])
    return f
Wo = table([(0, 62.5), (28, 47.5), (57.6, 34.5), (86, 26.0), (115.7, 20.0), (150, 14.6), (195, 9.8), (240, 7.0), (276, 5.6), (300, 3.8)])
Wi = table([(0, 37.1), (28, 25.4), (57.6, 16.5), (86, 10.2), (115.7, 5.6), (150, 2.5), (180, .7), (200, .7)])

def turned(p, k):
    """a point on the +z side turned k quarters round the axis"""
    x, y, z = p
    for _ in range(k % 4): x, z = z, -x
    return [x, y, z]
def four(lines): return [turned(p, k) for k in range(4) for p in lines]

# ---- the masonry feet -----------------------------------------------------------------------------------------------------
FOOT = 2.4
fc = (Wo(0) + Wi(0)) / 2; fw = Wo(0) - Wi(0) + 2.0
add("feet", {"type": "prism", "plan": {"rect": [r3(fw), r3(fw)]}, "height": FOOT,
             "at": [[r3(sx * fc), 0, r3(sz * fc), 0] for sx in (-1, 1) for sz in (-1, 1)],
             "_about": "the masonry pedestal under each leg, 27m square"})

# ---- the legs -------------------------------------------------------------------------------------------------------------
# heights of the panels: each about 0.42 of the leg's width at that height, the floors landing on a station
def stops(y0, y1, share, fixed=()):
    out, y = [y0], y0
    while y < y1 - 1e-6:
        step = max(3.2, share * (Wo(y) - Wi(y) if y < MERGE else 2 * Wo(y)))
        n = y + step
        for f in fixed:
            if y < f - 1.5 and n > f - 1.5: n = f
        out.append(min(n, y1)); y = out[-1]
        if y1 - y < 1.5: out[-1] = y1; y = y1
    return out
def leg_section(y, sx, sz):
    a, b = Wi(y), Wo(y)
    return [[sx * a, y, sz * a], [sx * b, y, sz * a], [sx * b, y, sz * b], [sx * a, y, sz * b]]
YS = stops(FOOT, MERGE, .42, (TOP1, TOP2))
LOW = [y for y in YS if y <= TOP1]; MID = [y for y in YS if TOP1 <= y <= TOP2]; UP = [y for y in YS if y >= TOP2]
for nm, ys, ch, br in (("lower", LOW, [2.0, 1.5], .62), ("middle", MID, [1.5, 1.15], .5), ("upper", UP, [1.15, .9], .4)):
    add(f"{nm} legs", {"type": "truss", "bracing": "x", "chord": ch, "strut": br, "brace": br, "caps": False,
                       "stations": [[pt(p) for p in leg_section(y, 1, 1)] for y in ys],
                       "at": [[0, 0, 0, 0], [0, 0, 0, math.pi / 2], [0, 0, 0, math.pi], [0, 0, 0, -math.pi / 2]],
                       **({"_about": "one leg's great lattice, turned to its four corners: a square box of four chords, a strut and two crossing diagonals to a face"} if nm == "lower" else {})})

# THE FINE LATTICE, the second scale: a thin zigzag on the outward faces of each leg, panels a quarter of the great ones
def fine(ys, w):
    lines = []
    for sf, (A, B, C, D) in enumerate((((1, 0), (1, 1), (0, 1), (0, 0)),)):
        pass
    seq = []
    for y0, y1 in zip(ys, ys[1:]):
        for k in range(4): seq.append(y0 + (y1 - y0) * k / 4)
    seq.append(ys[-1])
    for f0, f1 in ((0, 1), (1, 2), (2, 3), (3, 0)):        # a face of the section at each pair of corners: a grid of parallel ribs and a zigzag
        for j in (.25, .5, .75):
            prev = None
            for i, y in enumerate(seq):
                S = leg_section(y, 1, 1); a, b = S[f0], S[f1]
                q = [a[c] + (b[c] - a[c]) * j for c in range(3)]
                if prev: lines.append(pt(prev) + pt(q))
                prev = q
    return lines
lower_fine = fine(LOW, .22) + fine(MID, .2)
add("leg ribs", {"type": "bars", "w": .24, "lines": lower_fine, "caps": False,
                 "at": [[0, 0, 0, 0], [0, 0, 0, math.pi / 2], [0, 0, 0, math.pi], [0, 0, 0, -math.pi / 2]],
                 "_about": "the fine lattice's ribs up each leg's faces, three to a face, so that from afar the leg's great diagonals have a screen of iron behind them"})

# ---- the shaft ------------------------------------------------------------------------------------------------------------
SH = stops(MERGE, TOP3, .34)
def shaft_section(y):
    b = Wo(y)
    return [[-b, y, -b], [b, y, -b], [b, y, b], [-b, y, b]]
add("shaft", {"type": "truss", "bracing": "x", "chord": [.95, .55], "strut": .32, "brace": .3, "caps": False,
              "stations": [[pt(p) for p in shaft_section(y)] for y in SH],
              "_about": "the four legs become one square lattice shaft, thinning to the third floor"})
# (the legs' tips are joined to the shaft's corners by the upper legs' last station, the outer corners being the shaft's)

# the lift's guides up the middle, second floor to third (the 1889 Edoux lift ran in the shaft)
add("lift guides", {"type": "bars", "w": .3, "caps": False, "lines": [[r3(sx * .9), TOP2, r3(sz * .9), r3(sx * .9), TOP3, r3(sz * .9)] for sx in (-1, 1) for sz in (-1, 1)],
                    "_about": "the lift's guides up the shaft's middle"})

# ---- the arches: on the plane of the outer faces, leg to leg under the first floor --------------------------------------
GIRD0, GIRD1 = 47.5, TOP1 - .3                   # the first floor's girders, deep bands of lattice between the legs
SP, CROWN, SPRING = 34.0, 39.5, 6.0              # the arch's half span, its crown (the top of the intrados 39m up), where it springs off the legs
DEPTH = 2.6                                      # the arch's rib, intrados to extrados
def plane(x, y): return [x, y, Wo(y)]            # a point on the +z outer face
def arch_at(t, d=0):
    a = math.pi * t
    return plane((SP + d) * -math.cos(a), SPRING + (CROWN - SPRING + d) * math.sin(a))
NARCH = 22
st = [[arch_at(i / NARCH), arch_at(i / NARCH, DEPTH)] for i in range(NARCH + 1)]
arch_st = [[pt(p) for p in s] for s in st]
ARCH_TURN = [[0, 0, 0, 0], [0, 0, 0, math.pi / 2], [0, 0, 0, math.pi], [0, 0, 0, -math.pi / 2]]
add("arches", {"type": "truss", "bracing": "n", "chord": .75, "strut": .3, "brace": .3, "stations": arch_st, "caps": False, "at": ARCH_TURN,
               "_about": "Sauvestre's arch, 68m across and to 39.5m, a lattice rib along the tower's outer face: it carries nothing and is the tower's face"})
# the spandrels: verticals from the arch's back up to the girder, and a ring in each
sp = []
for i in range(1, NARCH):
    if i % 2: continue
    a = arch_at(i / NARCH, DEPTH)
    if a[1] < GIRD0 - 2:
        sp.append(pt(a) + pt(plane(a[0], GIRD0)))
for x, r, y in ((-22.0, 3.0, 40.0), (-12.0, 2.4, 43.0), (12.0, 2.4, 43.0), (22.0, 3.0, 40.0)):
    q = [plane(x + r * math.cos(k * math.pi / 6), y + r * math.sin(k * math.pi / 6)) for k in range(13)]
    sp += [pt(q[k]) + pt(q[k + 1]) for k in range(12)]
add("spandrels", {"type": "bars", "w": .28, "caps": False, "lines": sp, "at": ARCH_TURN, "_about": "uprights from the arch's back to the girder, and iron rings in the spandrels"})

# ---- the first floor's girders -------------------------------------------------------------------------------------------
def girder(y0, y1, half, n, w, w2, plane_):
    """a flat lattice girder across a side (x -half .. half), its depth y0..y1 on the given plane"""
    return {"type": "truss", "bracing": "x", "chord": w, "strut": w2, "brace": w2, "caps": False,
            "stations": [[pt(plane_(-half + 2 * half * i / n, y0)), pt(plane_(-half + 2 * half * i / n, y1))] for i in range(n + 1)], "at": ARCH_TURN}
add("first floor girders", {**girder(GIRD0, GIRD1, Wo(52), 12, .8, .36, plane), "_about": "the great girders that hold the legs together at the first floor, 10m deep, on the outer faces"})
add("first floor inner girders", {**girder(GIRD0, GIRD1, Wi(52), 6, .6, .3, lambda x, y: [x, y, Wi(y)]), "_about": "...and between the legs' inner faces"})
# the arcade along the first floor's cornice: little round arches between two rails
ARC_N = 26
half = Wo(TOP1) + .2
arcade = []
for i in range(ARC_N):
    x0 = -half + 2 * half * i / ARC_N; w_ = 2 * half / ARC_N; R = w_ / 2 * .86; cx = x0 + w_ / 2
    y0, ys_ = TOP1 - 4.0, TOP1 - 2.6
    prof = [[cx - R, y0], [cx - R, ys_]] + [[cx - R * math.cos(k * math.pi / 5), ys_ + R * math.sin(k * math.pi / 5)] for k in range(1, 5)] + [[cx + R, ys_], [cx + R, y0]]
    arcade += [pt(plane(*prof[k])) + pt(plane(*prof[k + 1])) for k in range(len(prof) - 1)]
for y in (TOP1 - 4.0, TOP1 - .8):
    arcade.append(pt(plane(-half, y)) + pt(plane(half, y)))
add("first floor arcade", {"type": "bars", "w": .24, "caps": False, "lines": arcade, "at": ARCH_TURN,
                           "_about": "the arcade of little arches under the first floor's gallery, the band the tower's waist is known by"})

# ---- the floors ------------------------------------------------------------------------------------------------------------
def floor(nm, y, a, hole, t, about):
    add(nm, {"type": "prism", "plan": {"rect": [r3(2 * a), r3(2 * a)], "well": {"rect": [r3(2 * hole), r3(2 * hole)], "at": [0, 0]}}, "railing": False, "height": t, "at": [[0, r3(y - t), 0, 0]], "_about": about})
def rail(nm, y, a, h=1.3, every=2.4, w=.09):
    n = max(2, round(2 * a / every)); L = []
    C = [[-a, a], [a, a], [a, -a], [-a, -a]]
    for j in range(4):
        (x0, z0), (x1, z1) = C[j], C[(j + 1) % 4]
        for lev in (h, h * .5):
            L.append([r3(x0), r3(y + lev), r3(z0), r3(x1), r3(y + lev), r3(z1)])
        for i in range(n):
            f = i / n; x, z = x0 + (x1 - x0) * f, z0 + (z1 - z0) * f
            L.append([r3(x), r3(y), r3(z), r3(x), r3(y + h), r3(z)])
    add(nm, {"type": "bars", "w": w, "caps": False, "lines": L})
A1 = Wo(TOP1) + 1.0; H1 = 16.2
floor("first floor", TOP1, A1, H1, .5, "the first floor, a square ring round its well, 71m across")
rail("first floor rail", TOP1, A1 - .1)
def pavilion(nm, y, L, D, at, h, about):
    add(nm, {"type": "enclosure", "plan": {"rect": [L, D]}, "thickness": .25, "height": h,
             "tiers": [{"openings": {"every": 2.6, "width": 1.9, "end": 1.0, "sill": .7, "springing": h - .5, "head": {"profile": "flat"}}}], "faces": {"0": [{"at": 0, "width": 2.0, "sill": 0, "springing": h - .6, "head": {"profile": "flat"}}]},
             "at": [[r3(x), y, r3(z), r3(a)] for x, z, a in at], "_about": about})
    add(nm + " roof", {"type": "roof", "form": "hip", "width": D, "length": L, "pitch": 18, "overhang": .5, "at": [[r3(x), y + h, r3(z), r3(a + math.pi / 2)] for x, z, a in at]})
RING1 = (A1 + H1) / 2
pavilion("first floor pavilions", TOP1, 26.0, 7.0, [(0, RING1, 0), (RING1, 0, math.pi / 2), (0, -RING1, math.pi), (-RING1, 0, -math.pi / 2)], 5.5,
         "the four pavilions of the first floor, between the legs")
# the second floor
A2 = Wo(TOP2) + 1.2; H2 = 5.6
GD2 = 4.0
floor("second floor", TOP2, A2, H2, .45, "the second floor, 42m across, the lift's well in its middle")
rail("second floor rail", TOP2, A2 - .1)
add("second floor girders", {**girder(TOP2 - GD2, TOP2 - .3, Wo(TOP2 - 2), 8, .55, .24, plane), "_about": "its girders, on the outer faces"})
RING2 = (A2 + H2) / 2
pavilion("second floor pavilions", TOP2, 10.0, 6.0, [(0, RING2, 0), (RING2, 0, math.pi / 2), (0, -RING2, math.pi), (-RING2, 0, -math.pi / 2)], 4.0,
         "the small pavilions of the second floor, between the legs' heads")
# the third floor: a closed glazed gallery and the open deck on it
A3 = Wo(TOP3) + 2.5
add("third floor", {"type": "prism", "plan": {"rect": [r3(2 * A3), r3(2 * A3)]}, "height": .5, "at": [[0, TOP3 - .5, 0, 0]], "_about": "the third floor, 16m across"})
G3 = 3.2
add("third floor gallery", {"type": "enclosure", "plan": {"rect": [r3(2 * A3 - .6), r3(2 * A3 - .6)]}, "thickness": .2, "height": G3, "interior": True,
                            "tiers": [{"openings": {"every": 1.8, "width": 1.4, "end": .6, "sill": .8, "springing": 2.8, "head": {"profile": "flat"}}}], "at": [[0, TOP3, 0, 0]],
                            "_about": "the glazed gallery all round the third floor"})
D3 = A3 + 1.0
add("third floor deck", {"type": "prism", "plan": {"rect": [r3(2 * D3), r3(2 * D3)]}, "height": .3, "at": [[0, TOP3 + G3, 0, 0]], "_about": "the open deck over it, overhanging"})
rail("third floor rail", TOP3 + G3 + .3, D3 - .1)
# ---- the crown: four arched ribs from the deck's corners in to the lantern, the lantern, the mast --------------------------
Y0 = TOP3 + G3 + .3; LY = 296.0; LR = 2.6
def crown(t): return LR * .72 + (A3 - .5 - LR * .72) * (1 - t) ** 1.8
CN = 8
add("crown", {"type": "truss", "bracing": "n", "chord": .38, "strut": .16, "brace": .14, "caps": False,
              "stations": [[pt(p) for p in ((-crown(k / CN), Y0 + (LY - Y0) * k / CN, -crown(k / CN)), (crown(k / CN), Y0 + (LY - Y0) * k / CN, -crown(k / CN)),
                                            (crown(k / CN), Y0 + (LY - Y0) * k / CN, crown(k / CN)), (-crown(k / CN), Y0 + (LY - Y0) * k / CN, crown(k / CN)))] for k in range(CN + 1)],
              "_about": "the crown that carries the lantern over the deck: four ribs curving in as the tower's own edges do, braced"})
add("crown room", {"type": "enclosure", "plan": {"rect": [8.4, 8.4]}, "thickness": .2, "height": 3.0, "interior": True,
                   "tiers": [{"openings": {"every": 2.0, "width": 1.2, "end": .8, "sill": .8, "springing": 2.2, "head": {"profile": "semicircular"}}}], "faces": {"0": [{"at": 0, "width": 1.2, "sill": 0, "springing": 2.2, "head": {"profile": "flat"}}]},
                   "at": [[0, Y0, 0, 0]], "_about": "Eiffel's own small room on the deck"})
add("crown room roof", {"type": "roof", "form": "pyramid", "width": 8.4, "length": 8.4, "pitch": 18, "overhang": .3, "at": [[0, Y0 + 3.0, 0, 0]]})
add("lantern deck", {"type": "column", "radius": LR + .5, "height": .3, "sides": 12, "at": [[0, LY, 0, 0]], "_about": "the lantern's small deck where the ribs meet"})
add("lantern", {"type": "column", "radius": LR - .4, "height": 3.2, "sides": 12, "at": [[0, LY + .3, 0, 0]], "_about": "the lighthouse lantern at 300m"})
add("lantern dome", {"type": "dome", "radius": LR - .2, "thickness": 0, "sides": 12, "head": {"profile": "semicircular"}, "at": [[0, LY + 3.5, 0, 0]]})
add("mast", {"type": "column", "radius": .55, "taper": .2, "height": 29.0, "sides": 6, "at": [[0, LY + 5.0, 0, 0]], "_about": "the mast, to 330m (1889's flagstaff stood to 312m)"})

doc = {"name": "Eiffel Tower",
       "_about": "THE EIFFEL TOWER, Paris (1887-89): four lattice legs on a 125m square, leaning in on a nearly exponential curve to merge in one shaft; floors at 57.6, 115.7 and 276m; "
                 "Sauvestre's four arches under the first floor's girders; the lantern at 300m and the mast to 330m. Every iron member is a real bar (`truss`, `bars`: arch/truss.js). "
                 "Generated by tools/archgen/eiffel_tower.py -- edit the script for arithmetic changes.",
       "params": {"detail": 4}, "railing": {"type": "iron"}, "build": build, "parts": parts}
out = os.path.join(ROOT, "assets", "architecture", "eiffel-tower.json")
with open(out, "w") as f:
    json.dump(doc, f, separators=(",", ":"))
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts", sum(len(p.get("lines", [])) for p in parts.values()), "lines")
