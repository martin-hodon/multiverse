# THE FORBIDDEN CITY's three great halls, Beijing (1420, the Hall of Supreme Harmony as it stands 1695): the outer court's marble terrace and the halls on it.
#   THE TERRACE (the Three Great Halls' platform): 8.13m in three equal tiers of white marble, I-shaped on plan, about 130m across and 232m long; 1,142 dragon-head
#   spouts under its balustrades, here one to every post (posts every 3.3m, not the real 1.7m: the same read at a tenth of the cost); stairs up every
#   tier: to the south and north three flights abreast either side of a carved imperial way, two more flanking, and one flight east and west.
#   THE HALL OF SUPREME HARMONY (Taihe Dian): 11 bays by 5, about 60 x 33m on its columns, 72 columns on a 12 x 6 grid (published bays: the middle 8.44m, the
#   others 5.55m and the ends 3.4m; across 8.86m and 3.37m), 26.92m from the terrace to the top of the ridge beasts, 35m over the court.
#     DOUBLE-EAVED, yellow-tiled, a true hip (`wudian`, the highest rank a roof could have): the lower roof a `pent` on the eave columns, a clerestory band over it,
#     the upper a `hip`, each eave carried on bracket sets (components/dougong) and with ten beasts down each hip (`hips`). A gallery one bay deep behind the
#     south front's eave columns; the door wall behind it (five bays of doors in the middle, windows either side); a solid wall round the other three sides.
#   Behind it on the terrace's waist the HALL OF CENTRAL HARMONY (Zhonghe Dian, square, pyramid roof, gilt finial) and on the north block the HALL OF PRESERVING HARMONY
#   (Baohe Dian, 9 bays, a gablet roof: its real one is double-eaved, here single -- components/chinese-hall).
#   South is +z, the Taihe Dian's middle at the origin. The court in front (30,000 square metres) and its gate are left out: only its axial way. Numbers are worked here.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q, PI = math.pi / 2, math.pi
r3 = lambda v: round(v, 3)

# ---- the terrace ------------------------------------------------------------------------------------------------------------
TH, IN = 2.71, 7.5                                # a tier's height (8.13m in three); how far each sets in
TOP = 3 * TH
X0, XW, S0, N0, ZB, ZC = 65.0, 37.0, 61.0, -171.0, -40.0, -100.0   # the lowest tier: half widths of the blocks and the waist, south and north edges, where the waist starts and ends
def tier(k):
    d = k * IN
    X, W, S, N, B, C = X0 - d, XW - d, S0 - d, N0 + d, ZB + d, ZC - d
    return dict(X=X, W=W, S=S, N=N, B=B, C=C, y=k * TH,
                pts=[[-X, S], [X, S], [X, B], [W, B], [W, C], [X, C], [X, N], [-X, N], [-X, C], [-W, C], [-W, B], [-X, B]])
T = [tier(k) for k in range(3)]
NM = ("lower", "middle", "upper")
for k, t in enumerate(T):
    add(f"{NM[k]} tier", {"type": "prism", "plan": {"points": t["pts"]}, "height": TH, "at": [[0, r3(t["y"]), 0, 0]], "railing": False,
                          **({"_about": "the terrace's three tiers of white marble, I-shaped: 8.13m in all"} if k == 0 else {})})
# the stairs
STEPS, RUN = 17, .32
FL = STEPS * RUN                                  # a flight's run: it lands on the tier below, IN metres out
SW, FW, EW = 3.0, 3.0, 3.0                        # the imperial way's width; the flights beside it; the flanking and the side flights
FLANK, ZSIDE = 26.0, 22.0                         # the flanking flights' x, the side flights' z
pitch = math.degrees(math.atan(TH / FL))
for k, t in enumerate(T):
    y0, S, N, X = t["y"], t["S"], t["N"], t["X"]
    fs, fn = S + FL - .03, N - FL + .03             # the foot of a flight on the south edge, on the north
    fl = []
    for xc in (-(SW + FW) / 2, (SW + FW) / 2):
        fl += [[r3(xc + FW / 2), y0, r3(fs), Q], [r3(xc - FW / 2), y0, r3(fn), -Q]]
    for xc in (-FLANK, FLANK):
        fl += [[r3(xc + EW / 2), y0, r3(fs), Q]]
    fl += [[r3(X + FL - .03), y0, r3(ZSIDE - EW / 2), PI], [r3(-X - FL + .03), y0, r3(ZSIDE + EW / 2), 0]]
    add(f"{NM[k]} stairs", {"type": "flight", "width": FW, "run": RUN, "steps": STEPS, "top": TH, "landing": 0, "at": fl,
                            **({"_about": "to the south and north a flight either side of the imperial way; two more flanking on the south; east and west one"} if k == 0 else {})})
    add(f"{NM[k]} imperial way", {"type": "roof", "form": "shed", "width": FL, "length": SW, "pitch": r3(pitch), "at": [[0, y0, r3(S + FL / 2 - .03), Q], [0, y0, r3(N - FL / 2 + .03), -Q]],
                                  **({"_about": "the carved slab up the middle (the emperor alone was carried over it): dragons in the clouds, a wedge from tier to tier"} if k == 0 else {})})
# the balustrades, each tier's edge in runs between the stairs: panels (long boxes, one painted bay every 3.3m) and posts with their heads, a spout under each
STEP = 3.3
posts, heads, spouts = [], [], []
pk = 0
def run(y, x0, z0, x1, z1, out):
    """one run of balustrade along an edge, from (x0, z0) to (x1, z1); out: the unit vector off the edge; inset 25cm"""
    global pk
    L = math.hypot(x1 - x0, z1 - z0)
    if L < 1: return
    n = max(1, round(L / STEP)); ux, uz = (x1 - x0) / L, (z1 - z0) / L
    xa, za, xb, zb = x0 - out[0] * .25, z0 - out[1] * .25, x1 - out[0] * .25, z1 - out[1] * .25
    pk += 1
    add(f"panels {pk}", {"type": "box", "width": r3(L) if ux else .16, "length": .16 if ux else r3(L), "height": .85, "at": [[r3((xa + xb) / 2), r3(y), r3((za + zb) / 2), 0]],
                         **({"_about": "each tier's balustrade: a carved panel to every bay"} if pk == 1 else {})})
    for i in range(n + 1):
        a = i * L / n
        x, z = xa + ux * a, za + uz * a
        posts.append([r3(x), r3(y), r3(z), r3(x), r3(y + 1.05), r3(z)])
        heads.append([r3(x), r3(y + 1.05), r3(z), r3(x), r3(y + 1.42), r3(z)])
        spouts.append([r3(x + out[0] * .2), r3(y - .22), r3(z + out[1] * .2), r3(x + out[0] * 1.05), r3(y - .36), r3(z + out[1] * 1.05)])
def along_x(y, z, x0, x1, gaps, out):
    a = x0
    for g0, g1 in sorted(gaps):
        if g0 > a: run(y, a, z, min(g0, x1), z, out)
        a = max(a, g1)
    if a < x1: run(y, a, z, x1, z, out)
def along_z(y, x, z0, z1, gaps, out):
    a = z0
    for g0, g1 in sorted(gaps):
        if g0 > a: run(y, x, a, x, min(g0, z1), out)
        a = max(a, g1)
    if a < z1: run(y, x, a, x, z1, out)
GC = (-(SW / 2 + FW) - .4, SW / 2 + FW + .4)
GF = [(-FLANK - EW / 2 - .4, -FLANK + EW / 2 + .4), (FLANK - EW / 2 - .4, FLANK + EW / 2 + .4)]
GZ = (ZSIDE - EW / 2 - .4, ZSIDE + EW / 2 + .4)
for k, t in enumerate(T):
    y = t["y"] + TH; X, W, S, N, B, C = t["X"], t["W"], t["S"], t["N"], t["B"], t["C"]
    along_x(y, S, -X, X, [GC, *GF], (0, 1))
    along_x(y, N, -X, X, [GC], (0, -1))
    for sg in (-1, 1):
        along_z(y, sg * X, B, S, [GZ], (sg, 0))
        along_z(y, sg * X, N, C, [], (sg, 0))
        along_z(y, sg * W, C, B, [], (sg, 0))
        along_x(y, B, min(sg * W, sg * X), max(sg * W, sg * X), [], (0, -1))
        along_x(y, C, min(sg * W, sg * X), max(sg * W, sg * X), [], (0, 1))
add("balustrade posts", {"type": "bars", "w": .26, "lines": posts, "caps": False, "_about": "the balustrades' posts, one every 3.3m"})
add("balustrade heads", {"type": "bars", "w": .34, "lines": heads, "_about": "their carved cloud heads"})
add("dragon spouts", {"type": "bars", "w": .2, "h": .22, "lines": spouts, "_about": "the dragon heads that spout the terrace's rain, one under each post"})
print("posts", len(posts))

# ---- the Hall of Supreme Harmony ---------------------------------------------------------------------------------------------
XB = [3.4] + [5.55] * 4 + [8.44] + [5.55] * 4 + [3.4]   # the bays along the front
ZB_ = [3.37, 8.86, 8.86, 8.86, 3.37]                   # the bays across
def lines(b):
    tot, out, a = sum(b), [], 0
    out.append(-tot / 2)
    for w in b: a += w; out.append(a - tot / 2)
    return [r3(v) for v in out]
XS, ZS = lines(XB), lines(ZB_)
L, D = XS[-1] * 2, ZS[-1] * 2                     # the columns' rectangle: 59.64 x 33.32
L2, D2 = XS[-2] * 2, ZS[-2] * 2                   # the inner ring's: 52.84 x 26.58
Y = TOP + .5                                      # the hall's floor: its low plinth on the top tier
H1, S1, OV1, P1 = 7.5, .95, 3.0, 28.0              # the eave columns; the lower brackets' scale; the lower eave's overhang; its pitch
BT = 1.06                                         # a set's height at scale 1 (components/dougong)
yCol = Y + H1
yP = yCol + BT * S1 + OV1 * math.tan(math.radians(P1))   # the lower roof's wall plane
yPT = yP + (L - L2) / 2 * math.tan(math.radians(P1))    # ...where it reaches the clerestory
yC1 = yPT + 2.0                                   # the clerestory's top
S2, OV2, P2, HIP = .95, 3.6, 28.0, .7               # the upper brackets; the upper eave; its pitch; how far the hips run in along the ridge, per width
yR = yC1 + BT * S2 + OV2 * math.tan(math.radians(P2))
RISE = D2 / 2 * math.tan(math.radians(P2))
print("the ridge's roof line at", round(yR + RISE - TOP, 2), "over the terrace")

add("hall plinth", {"type": "box", "width": 68.0, "length": 40.0, "height": .5, "at": [[0, TOP, 0, 0]], "_about": "the hall's low plinth on the top tier"})
add("plinth steps", {"type": "flight", "width": 18.0, "run": .32, "steps": 3, "top": .5, "landing": 0, "at": [[9.0, TOP, r3(20.0 + .96 - .03), Q]]})
outer = [[x, Y, z, 0] for x in XS for z in ZS if x in (XS[0], XS[-1]) or z in (ZS[0], ZS[-1])]
ring2 = [[x, Y, z, 0] for x in XS[1:-1] for z in ZS[1:-1] if x in (XS[1], XS[-2]) or z in (ZS[1], ZS[-2])]
inner = [[x, Y, z, 0] for x in XS[2:-2] for z in ZS[2:-2]]
GOLD = [a for a in inner if abs(a[0]) < 10.5 and (abs(a[0]) < 5 or a[2] < 0)]
PLAIN = [a for a in inner if a not in GOLD]
add("eave columns", {"type": "column", "radius": .45, "height": H1, "sides": 16, "at": outer, "_about": "72 red columns on the 12 x 6 grid: the outer ring carries the lower eave..."})
add("clerestory columns", {"type": "column", "radius": .5, "height": r3(yC1 - Y - .3), "sides": 16, "at": ring2, "_about": "...the next ring runs up through the lower roof to carry the upper..."})
add("inner columns", {"type": "column", "radius": .53, "height": 11.0, "sides": 16, "at": PLAIN})
add("gold columns", {"type": "column", "radius": .53, "height": 11.0, "sides": 16, "at": GOLD, "_about": "...and the six about the throne are gilded, with dragons coiling up them"})
# the walls
WT = .4
inner_x = XS[1:-1]
ops = []
for i in range(len(inner_x) - 1):
    a, b = inner_x[i] + L2 / 2, inner_x[i + 1] + L2 / 2
    door = 2 <= i <= 6
    w = b - a - 1.1
    if w > 4.5:                                   # (the middle bay's leaves, in two pairs: a post between)
        ops += [{"at": r3((a + b) / 2 + s * (w + .5) / 4), "width": r3((w - .5) / 2), "sill": 0, "springing": 6.2, "head": {"profile": "flat"}, "glass": False} for s in (-1, 1)]
        continue
    ops.append({"at": r3((a + b) / 2), "width": r3(w), "sill": 0 if door else 1.1, "springing": 6.2, "head": {"profile": "flat"}, **({"glass": False} if door else {})})   # (the doors: leaves of lattice, assets/doors/forbidden-city.json)
add("door wall", {"type": "wall", "width": L2, "height": H1, "thickness": WT, "glass": True, "openings": ops, "at": [[0, Y, r3(ZS[-2] - .2), PI]],
                  "_about": "the south front: a gallery one bay deep behind the eave columns, then the door wall -- five bays of lattice doors in the middle, windows on a low wall either side"})
add("wall returns", {"type": "wall", "width": 3.4, "height": H1, "thickness": WT, "at": [[s * r3(L2 / 2 + 1.7), Y, r3(ZS[-2] - .2), PI] for s in (-1, 1)]})
add("back wall", {"type": "wall", "width": r3(L + WT), "height": H1, "thickness": WT, "at": [[0, Y, r3(ZS[0] + .2), 0]], "glass": False,
                  "openings": [{"at": r3((L + WT) / 2), "width": 4.4, "sill": 0, "springing": 6.0, "head": {"profile": "flat"}}], "_about": "the other three sides are solid red walls, a door in the back"})
ES = ZS[-2] - ZS[0]
add("end walls", {"type": "wall", "width": r3(ES), "height": H1, "thickness": WT, "at": [[r3(L / 2 + .2), Y, r3((ZS[-2] + ZS[0]) / 2), Q], [r3(-L / 2 - .2), Y, r3((ZS[-2] + ZS[0]) / 2), -Q]]})
add("hall room", {"type": "interior", "plan": {"rect": [r3(L - .4), r3(ES - .4)]}, "height": 11.0, "at": [[0, Y, r3((ZS[-2] + ZS[0]) / 2), 0]]})
add("ceiling", {"type": "box", "width": r3(L), "length": r3(ES), "height": .3, "at": [[0, r3(Y + 11.0), r3((ZS[-2] + ZS[0]) / 2), 0]], "_about": "the coffered ceiling under the upper roof"})
add("throne dais", {"type": "box", "width": 10.0, "length": 7.0, "height": .9, "at": [[0, Y, -4.0, 0]], "_about": "the throne's dais, its seven steps implied"})
add("throne", {"type": "box", "width": 1.8, "length": 1.2, "height": 1.5, "at": [[0, r3(Y + .9), -4.0, 0]], "_about": "the Dragon Throne"})
add("throne screen", {"type": "box", "width": 5.6, "length": .3, "height": 4.0, "at": [[0, r3(Y + .9), -5.4, 0]]})
add("lower beam", {"type": "enclosure", "plan": {"rect": [r3(L + WT), r3(D + WT)]}, "thickness": WT, "height": .8, "at": [[0, r3(yCol - .8), 0, 0]], "_about": "the painted beam round the column heads"})
# the lower eave's brackets: on every column line and between, round the outer ring
def ring_at(xs, zs, y):
    a = []
    pts = lambda v: sorted({*v, *[(v[i] + v[i + 1]) / 2 for i in range(len(v) - 1)]})
    for x in pts(xs): a += [[r3(x), r3(y), zs[-1], 0], [r3(x), r3(y), zs[0], PI]]
    for z in pts(zs)[1:-1]: a += [[xs[-1], r3(y), r3(z), Q], [xs[0], r3(y), r3(z), -Q]]
    return a
add("lower brackets", comp("components/dougong", {"s": S1}, ring_at(XS, ZS, yCol), _about="bracket sets on every column and between them, under both eaves"))
hip = {"w": .6, "h": .5, "beasts": 10, "beast": .62}
add("lower roof", {"type": "roof", "form": "pent", "width": D, "length": L, "top": [D2, L2], "pitch": P1, "overhang": OV1, "lo": .4, "hi": .75, "upturn": .9, "flare": .5, "hips": hip,
                   "at": [[0, r3(yP), 0, Q]], "_about": "the lower roof: a ring of yellow glazed tile, its corners turned up, from the eave to the clerestory; ten beasts down each hip"})
add("clerestory", {"type": "enclosure", "plan": {"rect": [D2 and L2, D2]}, "thickness": WT, "height": r3(yC1 - yCol), "glass": True, "at": [[0, r3(yCol), 0, 0]],
                   "openings": {"every": 5.55, "width": 4.2, "end": 1.0, "sill": r3(yPT - yCol + .2), "springing": r3(yPT - yCol + 1.1), "head": {"profile": "flat"}},
                   "_about": "a band of lattice windows between the two roofs, to light the hall's high ceiling"})
add("upper beam", {"type": "enclosure", "plan": {"rect": [r3(L2 + WT), r3(D2 + WT)]}, "thickness": WT, "height": .6, "at": [[0, r3(yC1 - .6), 0, 0]]})
add("upper brackets", comp("components/dougong", {"s": S2}, ring_at(XS[1:-1], ZS[1:-1], yC1)))
add("upper roof", {"type": "roof", "form": "hip", "width": D2, "length": L2, "hipH": HIP, "pitch": P2, "overhang": OV2, "lo": .3, "hi": 1.2, "upturn": 1.1, "flare": .6, "hips": hip,
                   "at": [[0, r3(yR), 0, Q]], "_about": "the upper roof, the true hip (wudian), the highest rank a Chinese roof could have: yellow tile, which only the emperor might use"})
RL = r3(L2 - D2 * HIP + .6)
add("ridge", {"type": "box", "width": RL, "length": .85, "height": 1.0, "at": [[0, r3(yR + RISE - .25), 0, 0]], "_about": "the main ridge, and the chiwen -- the dragon-mouthed ridge ends, 3.4m tall"})
CY = yR + RISE + .6
ch = lambda s: [[s * (RL / 2 - .2), CY, 0, s * (RL / 2 - .2), CY + 2.3, 0], [s * (RL / 2 - .2), CY + 2.3, 0, s * (RL / 2 - 1.0), CY + 2.55, 0], [s * (RL / 2 - .2), CY + .2, 0, s * (RL / 2 - 1.2), CY + .3, 0], [s * (RL / 2 - 1.0), CY + 2.55, 0, s * (RL / 2 - 1.2), CY + 2.0, 0]]
add("chiwen", {"type": "bars", "w": .62, "h": .72, "lines": [[r3(v) for v in l] for s in (-1, 1) for l in ch(s)]})
print("the chiwen reach", round(CY + 2.55 - TOP, 2), "over the terrace,", round(CY + 2.55, 2), "over the court")
# the bronze vats on the terrace
add("bronze vats", {"type": "column", "radius": .85, "height": 1.3, "sides": 10, "at": [[r3(s * x), TOP, z, 0] for s in (-1, 1) for x, z in ((16.0, 24.0), (22.0, 24.0), (28.0, 24.0), (36.0, 19.0), (42.0, 19.0))],
                    "_about": "great gilded vats of water, for fires, along the terrace"})

# ---- the two halls behind ----------------------------------------------------------------------------------------------------
ZZ, ZBH = -70.0, -136.0
HALL = {"colR": .42, "t": .35, "archH": .8, "plat": .5, "platOut": 1.6, "backSill": 0, "lo": .3, "hi": 1.3, "upturn": 1.0, "flare": .6}
add("zhonghe dian", comp("components/chinese-hall", {**HALL, "nx": 5, "bw": 4.2, "nz": 5, "bd": 4.2, "H": 6.8, "s": .8, "over": 2.8, "pitch": 38, "roofForm": "pyramid", "hipH": 1.0}, [[0, TOP, ZZ, 0]],
                         _about="the Hall of Central Harmony, 24m square, where the emperor rested on his way: a pyramid roof and a gilt ball"))
ZY = TOP + .5 + 6.8 + 1.06 * .8 + 2.8 * math.tan(math.radians(38)) + (5 * 4.2) / 2 * math.tan(math.radians(38))
add("zhonghe finial", {"type": "dome", "radius": .85, "thickness": 0, "head": {"profile": "onion", "bulge": 1.3, "neck": .5}, "at": [[0, r3(ZY - .4), ZZ, 0]]})
add("baohe dian", comp("components/chinese-hall", {**HALL, "nx": 9, "bw": 5.4, "nz": 5, "bd": 3.9, "H": 9.2, "s": .95, "over": 3.4, "pitch": 34, "roofForm": "gablet", "hipH": .55}, [[0, TOP, ZBH, 0]],
                         _about="the Hall of Preserving Harmony, nine bays, its gablet roof a rank below the hip"))
# ---- the axial way across the court, in its slabs ------------------------------------------------------------------------------
add("axial way", {"type": "box", "width": 7.0, "length": 8.0, "height": .1, "walked": True, "at": [[0, 0, r3(S0 + FL + 6.0 + 8.0 * i), 0] for i in range(6)], "_about": "the imperial way's flagstones running on south across the great court"})

doc = {"name": "Forbidden City: Hall of Supreme Harmony",
       "_about": "THE FORBIDDEN CITY's three great halls (1420; the Taihe Dian 1695): the I-shaped white marble terrace in its three tiers, its balustrades, dragon spouts, stairs and imperial ways; the Hall of Supreme Harmony, double-eaved under the true hip (`pent` + `hip`, ten beasts on each hip), "
                 "brackets under both eaves, 72 red columns, a gallery behind the south front, the throne room; the Halls of Central and Preserving Harmony behind it (`chinese-hall`). Generated by tools/archgen/forbidden_city.py -- edit the script for arithmetic changes. South is +z.",
       "params": {"detail": 4}, "railing": {"type": "stone"}, "build": build, "parts": parts}
out = os.path.join(ROOT, "assets", "architecture", "forbidden-city.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts")
