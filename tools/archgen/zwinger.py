# THE ZWINGER, Dresden (Poeppelmann and Permoser, 1710-28; Semper's gallery 1847-55), from OpenStreetMap and the 1755 plans.
# THE FRAME: the court's long axis runs from the Wallpavillon (west-north-west) to the Glockenspielpavillon (east-south-east): +x
# points along it TO THE GLOCKENSPIEL (bearing 122.4 degrees), +z TOWARD THE KRONENTOR and the Zwingergraben (south-west) -- the
# front, as before; -z is the Sempergalerie and the Theaterplatz. (The old model had the Wallpavillon at +x: mirrored.) The origin
# is the court's middle, OSM 51.052999 N, 13.733772 E; y 0 the court's gravel.
# THE PLAN IS OSM's (ways 192745237 Langgalerie, 192745235 Kronentor, 23039959 Wallpavillon, 192745254 Glockenspielpavillon,
# 23039960 / 192745244 / 23039962 / 192745236 the corner pavilions, 3278037 / 192749266 / 243012354 the Bogengalerien, 3278006
# Sempergalerie, 148734764 Nymphenbad, 242553936 Zwingergraben), turned into this frame and made symmetric about both axes (OSM's
# outlines are a degree out of square; the east half is taken as the west's mirror). Heights from photographs, scaled by people and
# the Sempergalerie's 23.77 m (Wikipedia): the galleries' roof terraces 9.2 m over the court, the corner pavilions 16.8 m to their
# eaves, the Wallpavillon's Hercules 23 m, the Kronentor's crown 30 m.
#   THE COURT (107 x 116 m between the galleries) with its apsidal ends, its four lawns round four quatrefoil basins with jets, the
#   long basins along the Langgalerie; the raised walk (four steps) along the Bogengalerien.
#   THE GALLERIES: the Langgalerie either side of the Kronentor and the four Bogengalerien (a straight run and a quarter circle each,
#   from a corner pavilion to the Wallpavillon or the Glockenspielpavillon) -- one-storey halls of arched windows between Doric
#   pilasters, their floors raised over the court, their flat roofs the TERRACES, walked all round the court behind balustrades with
#   statues and vases.
#   THE PAVILIONS: the four corner pavilions (Mathematisch-Physikalischer Salon, Porzellanpavillon, Franzoesischer and Deutscher
#   Pavillon) -- a hall on the ground, a stair (dog-leg) to the upper hall level with the terraces, doors onto them at both ends,
#   a copper mansard, a raised front terrace and double perron to the court; the WALLPAVILLON on the rampart -- the grand stair
#   from the court through its middle arch to the grotto landing, then two arms back up to the festival hall, Hercules Saxonicus with
#   the globe on its roof; the GLOCKENSPIELPAVILLON -- the passage through, a stair to its upper hall, the forty Meissen bells.
#   THE KRONENTOR over the bridge across the moat: the passage, the open columned upper stage the terraces run through, the onion
#   and the gilt crown.  THE NYMPHENBAD behind the Franzoesischer Pavillon: a walled court below the pavilion's floor, its cascade down
#   from the rampart into a basin, the square fountain, the nymphs.  THE SEMPERGALERIE: two storeys of halls either side of the
#   domed triumphal arch, the ground storey rusticated, its stairs; the terraces from the pavilions to its upper floor.
#   THE RAMPART (the Wall) behind the Wallpavillon at the terraces' height; the ZWINGERGRABEN in front (a pool the game carves).
import os, json, math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapes import onion_y_at, onion_height
from neoclassical import Balusters
from statuary import statue, pedestal, capped, FACE_PZ, FACE_NZ, FACE_PX, FACE_NX
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
r4 = lambda v: round(v, 4)
parts = {}; build = []
def add(n, d):
    if n in parts: raise SystemExit(f"duplicate part {n}")
    parts[n] = d; build.append(n); return n
comp = lambda use, params, at, **kw: {"type": "component", "use": f"components/{use}", "params": params, "at": at, **kw}
Q = math.pi / 2

# ---- THE LEVELS
WK = 1.05            # the raised walk along the galleries, and the floor of every gallery and pavilion (six steps over the court)
GH = 8.6             # the galleries' walls
SL = 0.6             # the terrace slab on them
TY = GH + SL         # the TERRACES: the galleries' roofs, the pavilions' upper floors, the rampart, the Semper's upper floor
PH = TY + 7.6        # the corner pavilions' eaves
ARCH = {"profile": "semicircular"}
SEG = {"profile": "segmental", "rise": 0.35}
BAL = Balusters(h=1.0, every=0.45, post=0.15, rail=(0.34, 0.15), plinth=(0.36, 0.2))
INNER_RAIL = Balusters(h=1.0, every=0.4, post=0.07, rail=(0.08, 0.06), plinth=(0.1, 0.06))   # (round the stairwells inside: iron)
VASES, FLOORS, INTERIOR_WALLS, WATER, LAWNS, STONE_FLOORS = [], [], [], [], [], []

def op(at, w, sill, spring, head=ARCH, glass=True, **kw):
    return {"at": r4(at), "width": r4(w), "sill": r4(sill), "springing": r4(spring), "head": head, **({} if glass else {"glass": False}), **kw}
def door(at, w=1.6, h=3.4, head=ARCH):
    return op(at, w, 0, h, head, glass=False)
def row(L, n, w, sill, spring, head=ARCH, edge=1.0, skip=(), doors=None, **kw):
    """n openings w wide spread evenly along a face L long, from its middle; indices in `skip` left out, in `doors` {i: door} replaced"""
    if n <= 0: return []
    step = (L - 2 * edge) / n; out = []
    for k in range(n):
        a = -L / 2 + edge + step * (k + 0.5)
        if k in skip: continue
        if doors and k in doors: out.append({**doors[k], "at": r4(a)}); continue
        out.append(op(a, w, sill, spring, head, **kw))
    return out
def area(pts): return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
def oriented(pts, tags):
    """the engine's winding (negative area: face 0 of a rect is +z); `tags[i]` names edge pts[i] -> pts[i+1], kept with it"""
    if area(pts) <= 0: return pts, tags
    n = len(pts); P = pts[::-1]
    return P, [tags[(n - 2 - j) % n] for j in range(n)]
def edges(pts):
    n = len(pts); out = []
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]; L = math.dist(p, q)
        out.append({"p": p, "q": q, "L": L, "m": ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2), "d": ((q[0] - p[0]) / L, (q[1] - p[1]) / L)})
    return out
def along(e, x, z):
    """a world point's `at` on an edge (from its middle, along its run)"""
    return r4((x - e["m"][0]) * e["d"][0] + (z - e["m"][1]) * e["d"][1])
def P2(pts): return [[r4(x), r4(z)] for x, z in pts]
def mirror(pts, sx, sz):
    """a quadrant's outline copied to another (sx, sz = +-1), its winding as it was before the engine's"""
    q = [(sx * x, sz * z) for x, z in pts]
    return q if sx * sz > 0 else q[::-1]
def rect_pts(x0, x1, z0, z1): return [(x0, z1), (x1, z1), (x1, z0), (x0, z0)]

def iwall(name, a, b, y0, H, doors=(), t=0.45, about=""):
    """an internal wall from a to b (its middle line), standing at y0, H tall, with doorways (position from a, width, height)"""
    L = math.dist(a, b); dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    ops = [door(u - L / 2, w, h) for u, w, h in doors]
    add(name, {"type": "wall", "width": r4(L), "height": r4(H), "thickness": t, "tiers": [{"openings": ops}],
               "at": [[r4((a[0] + b[0]) / 2 - t / 2 * dz), r4(y0), r4((a[1] + b[1]) / 2 + t / 2 * dx), r4(math.atan2(-dz, dx))]], **({"_about": about} if about else {})})
    INTERIOR_WALLS.append(name)
def slab(name, x0, x1, z0, z1, y_top, h=0.5, walked=False, about="", floor=True):
    d = {"type": "prism", "plan": {"rect": [r4(x1 - x0), r4(z1 - z0)]}, "height": r4(h), "at": [[r4((x0 + x1) / 2), r4(y_top - h), r4((z0 + z1) / 2), 0]]}
    if walked: d["walked"] = True
    if about: d["_about"] = about
    add(name, d)
    if floor: FLOORS.append(name)
    return name
def flight_at(foot, d, w):
    """the placement of a flight (or a staircase's first flight) whose foot's middle is `foot` (x, z), climbing along d"""
    yaw = math.atan2(-d[1], d[0]); s, c = math.sin(yaw), math.cos(yaw)
    return [r4(foot[0] + w / 2 * s), r4(foot[1] + w / 2 * c), r4(yaw)]
def flight(name, foot, d, w, base, top, run=0.32, rise=0.175, about="", **kw):
    n = max(1, round((top - base) / rise)); x, z, yaw = flight_at(foot, d, w)
    add(name, {"type": "flight", "width": r4(w), "run": run, "rise": r4((top - base) / n), "base": r4(base), "top": r4(top), "landing": 0,
               "at": [[x, 0, z, yaw]], **kw, **({"_about": about} if about else {})})
    return n * run
def dogleg(name, foot, d, w, y0, y1, inward, run=0.29, gap=0.4, about=""):
    """a dog-leg stair: a flight up along d from `foot` (its middle), a landing, and the flight back beside it on the `inward`
    side (a unit (x, z) across d) up to y1, onto a landing of its own. Returns the run of a flight."""
    n = round((y1 - y0) / 0.177); n += n % 2; rise = (y1 - y0) / n; half = n // 2
    x, z, yaw = foot[0], foot[1], r4(math.atan2(-d[1], d[0]))   # (a staircase stands centred on its foot, unlike a flight)
    lz = (math.sin(yaw), math.cos(yaw))                       # (the flight's local +z in the world)
    sg = 1 if lz[0] * inward[0] + lz[1] * inward[1] > 0 else -1
    sh = sg * (w / 2 + gap / 2)
    add(name, {"type": "staircase", "flight": half, "width": r4(w), "run": run, "rise": r4(rise), "soffit": 0.3,
               "landing": {"depth": 2.0, "width": r4(2 * w + gap), "shift": r4(sh),
                           "then": [{"from": "back", "at": r4(sh), "flight": half, "width": r4(w), "landing": {"depth": 1.6, "width": r4(w)}}]},
               "at": [[x, r4(y0), z, yaw]], **({"_about": about} if about else {})})
    return half * run

# ===================================================================================================== THE COURT
# the gravel of the court: the rectangle between the Langgalerie and the Sempergalerie and the two apses, the Bogengalerien's
# inner line (a straight 25 m from the corner pavilions, then a quarter circle about (+-78, 0), 23.4 m round)
RI, RO, CX = 23.4, 33.4, 78.0          # the Bogengalerien's inner and outer radius, their centre's x
AI, AO = 61.0, 66.4                    # (the arcs' ends at the apex pavilions, degrees from +z: the inner line, the outer)
NA = 7                                 # bays round the arc
def arc(r, a0, a1, n, sx=1, sz=1):
    return [(sx * (CX + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))), sz * r * math.cos(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
court = [(-53.0, 60.0), (53.0, 60.0), (53.0, RI)] + arc(RI, 0, 90, 12)[0:] + [(p[0], -p[1]) for p in arc(RI, 0, 90, 12)[::-1][1:]] + [(53.0, -RI), (53.0, -60.0), (-53.0, -60.0), (-53.0, -RI)]
court += [(-p[0], -p[1]) for p in arc(RI, 0, 90, 12)] + [(-p[0], p[1]) for p in arc(RI, 0, 90, 12)[::-1][1:]] + [(-53.0, RI)]
court = [p for i, p in enumerate(court) if i == 0 or math.dist(p, court[i - 1]) > 0.01]
add("court", {"type": "prism", "plan": {"points": P2(court)}, "height": 0.04, "walked": True, "at": [[0, 0, 0, 0]],
              "_about": "the court's gravel, 107 m across between the galleries and 228 m from apse to apse"})
# THE FOUR LAWNS (OSM), each an L round its basin at the court's middle corner -- and the small lawns in the apses
def lawn_L(sx, sz):
    pts = [(24.6, 5.8), (39.4, 5.8), (39.4, 43.2), (5.6, 43.2), (5.6, 25.0), (24.6, 25.0)]
    pts = [(sx * x, sz * z) for x, z in pts]
    return pts if sx * sz < 0 else pts[::-1]
for sx in (-1, 1):
    for sz in (-1, 1):
        nm = f"lawn {'e' if sx > 0 else 'w'}{'n' if sz > 0 else 's'}"
        add(nm, {"type": "prism", "plan": {"points": P2(lawn_L(sx, sz))}, "height": 0.1, "walked": True, "at": [[0, 0.04, 0, 0]],
                 **({"_about": "the four lawns, each an L wrapped round its basin (OSM 218928418, 242994344, 244867856, 244965563)"} if sx < 0 and sz > 0 else {})})
        LAWNS.append(nm)
add("apse lawns", {"type": "prism", "plan": {"rect": [13.6, 11.0]}, "height": 0.1, "walked": True,
                   "at": [[sx * cx, 0.04, sz * 12.4, 0] for sx in (-1, 1) for sz in (-1, 1) for cx in (55.2, 79.6)], "_about": "the lawns in the apses either side of the middle path"})
LAWNS.append("apse lawns")
# THE FOUR BASINS (OSM 242996322 ...): quatrefoils 18 m across round a jet, their rims a low sandstone kerb
QF = [(r4((8.2 + 1.3 * math.cos(4 * t)) * math.sin(t)), r4((8.2 + 1.3 * math.cos(4 * t)) * math.cos(t))) for t in [2 * math.pi * k / 40 for k in range(40)]]
QF = QF if area(QF) < 0 else QF[::-1]
BASINS = [(sx * 15.0, sz * 15.0) for sx in (-1, 1) for sz in (-1, 1)]
add("basin rims", {"type": "enclosure", "plan": {"points": QF}, "thickness": 0.45, "height": 0.55, "openings": [], "glass": False, "interior": False, "courses": False,
                   "at": [[x, 0.04, z, 0] for x, z in BASINS], "_about": "the four basins' kerbs, quatrefoils about 18 m across"})
QW = [(r4(x * 0.94), r4(z * 0.94)) for x, z in QF]
add("basin water", {"type": "prism", "plan": {"points": QW}, "height": 0.38, "flatRoof": True, "at": [[x, 0.04, z, 0] for x, z in BASINS]}); WATER.append("basin water")
add("basin jet bowls", {"type": "column", "radius": 0.7, "height": 0.6, "sides": 12, "taper": 1.3, "at": [[x, 0.04, z, 0] for x, z in BASINS], "standsOn": ["basin water"]})
add("basin jets", {"type": "column", "radius": 0.16, "height": 5.5, "sides": 8, "taper": 0.25, "at": [[x, 0.64, z, 0] for x, z in BASINS], "standsOn": ["basin jet bowls"],
                   "_about": "the jets, a column of spray five metres high"}); WATER.append("basin jets")

# ===================================================================================================== THE LANGGALERIE
# either side of the Kronentor, x 3.5 .. 64, z 60 .. 67 (7 m deep): one storey of arched windows -- fifteen bays toward the court
# (to the corner pavilion at x 53; past it the pavilion stands against its court face), seventeen toward the moat -- between
# Doric pilasters; its floor 6 steps over the court, a door from the court beside the Kronentor and one into the corner pavilion
LZ0, LZ1, KX = 60.0, 67.0, 3.5
LGW = dict(w=2.1, sill=2.2, spring=5.4)
for sx in (-1, 1):
    x0, x1 = sx * KX, sx * 64.0; cx = (x0 + x1) / 2; W = abs(x1 - x0); D = LZ1 - LZ0
    nm = f"langgalerie {'east' if sx > 0 else 'west'}"
    # face 2 (-z, the court) runs toward -x: at = cx - x; its windows in x 4.9 .. 52
    court_ops = []
    for k in range(15):
        x = sx * (4.9 + (52.0 - 4.9) * (k + 0.5) / 15); a = cx - x
        court_ops.append(door(a, 1.8, 3.9) if k == 0 else op(a, LGW["w"], LGW["sill"], LGW["spring"]))
    court_ops.append(door(cx - sx * 58.35, 1.6, 3.6))                          # (into the corner pavilion)
    add(nm, {"type": "enclosure", "plan": {"rect": [r4(W), D]}, "thickness": 0.9, "height": GH, "glass": True, "interior": True,
             "faces": {"0": row(W, 17, 2.0, 2.4, 5.4, edge=2.0), "2": court_ops, "1": [], "3": []}, "courses": True,
             "orders": [{"tier": 0, "kind": "doric"}], "at": [[r4(cx), 0, r4((LZ0 + LZ1) / 2), 0]],
             "_about": "the Langgalerie: a hall of arched windows on both sides between Doric pilasters, its roof the terrace"})
    slab(f"{nm} floor", min(x0, x1), max(x0, x1), LZ0, LZ1, WK, h=WK)
    add(f"{nm} terrace", {"type": "prism", "plan": {"rect": [r4(W + 0.3), D + 0.6]}, "height": SL, "walked": True,
                          "at": [[r4(cx + sx * 0.15), GH, (LZ0 + LZ1) / 2, 0]], "_about": "the walked roof: the terrace along the Langgalerie"})
    BAL.run((x0, LZ1 + 0.1), (sx * 64.1, LZ1 + 0.1), TY)
    BAL.run((x0, LZ0 - 0.1), (sx * 52.9, LZ0 - 0.1), TY)
    BAL.run((sx * 64.1, LZ1 + 0.1), (sx * 64.1, LZ0 + 0.1), TY)
    VASES += [(sx * (KX + 4.0 + 7.2 * k), LZ1 + 0.1) for k in range(8)] + [(sx * 64.1, LZ1 + 0.1)] + [(sx * (KX + 4.0 + 7.2 * k), LZ0 - 0.1) for k in range(7)]
    flight(f"{nm} door steps", (sx * (4.9 + 47.1 / 30), LZ0 - 6 * 0.32), (0, 1), 2.6, 0, WK, about="up to the gallery's door beside the Kronentor")
# the long basins along its court face with the wall fountains (OSM 243089786, 243091982): a kerb and water, 26 m long
add("long basin kerbs", {"type": "enclosure", "plan": {"rect": [26.6, 3.0]}, "thickness": 0.35, "height": 0.6, "openings": [], "glass": False, "interior": False, "courses": False,
                         "at": [[sx * 26.4, 0.04, 58.4, 0] for sx in (-1, 1)], "_about": "the long basins at the Langgalerie's foot, its wall fountains spouting into them"})
add("long basin water", {"type": "prism", "plan": {"rect": [25.9, 2.3]}, "height": 0.45, "flatRoof": True, "at": [[sx * 26.4, 0.04, 58.4, 0] for sx in (-1, 1)]}); WATER.append("long basin water")
add("wall fountains", {"type": "box", "width": 1.6, "length": 0.5, "height": 2.6, "at": [[r4(sx * (13.1 + 26.6 * (k + 0.5) / 5)), 0.04, 59.75, 0] for sx in (-1, 1) for k in range(5)],
                       "_about": "the wall fountains on the piers, five each side, spouting into the long basins"})
add("wall fountain shells", {"type": "dome", "radius": 0.75, "thickness": 0, "head": {"profile": "semicircular"}, "sides": 10,
                             "at": [[r4(sx * (13.1 + 26.6 * (k + 0.5) / 5)), 2.64, 59.75, 0] for sx in (-1, 1) for k in range(5)], "standsOn": ["wall fountains"]})

# ===================================================================================================== THE KRONENTOR
# a gate tower on a chamfered square 7.0 x 6.8 (OSM 192745235) between the Langgalerie's halves: the passage on the axis from the
# court to the bridge; over it, at the terraces' height, an open stage of arches on every side with paired Corinthian columns at
# its cut corners -- the terraces run through it -- an attic, the ONION (dark copper, gilt) and the gilt Polish crown on top
KZ = (LZ0 + LZ1) / 2; KW, KD, KC = 7.0, 7.0, 1.55
KR = {"rect": [KW, KD], "chamfer": KC}          # faces: 0 -x, 2 +z, 4 +x, 6 -z, the odd ones the cut corners
add("kronentor", {"type": "enclosure", "plan": KR, "thickness": 1.1, "height": TY, "glass": False, "interior": False, "openings": [],
                  "faces": {"2": [op(0, 3.2, 0, 4.8, glass=False)], "6": [op(0, 3.2, 0, 4.8, glass=False)]}, "courses": True,
                  "orders": [{"tier": 0, "kind": "ionic", "ends": False}], "at": [[0, 0, KZ, 0]],
                  "_about": "the Kronentor's gate storey: the passage from the court to the bridge, under the terraces' height"})
add("kronentor passage floor", {"type": "prism", "plan": {"rect": [3.4, KD + 0.2]}, "height": 0.04, "walked": True, "at": [[0, 0, KZ, 0]]})
add("kronentor stage floor", {"type": "prism", "plan": KR, "height": 0.6, "at": [[0, r4(TY - 0.6), KZ, 0]], "_about": "the floor of the open stage, level with the terraces"})
FLOORS.append("kronentor stage floor")
KS = 6.6                                         # (the open stage's height)
add("kronentor stage", {"type": "enclosure", "plan": KR, "thickness": 0.8, "height": KS, "glass": False, "interior": False, "openings": [],
                        "faces": {str(f): [op(0, 2.8, 0, 3.9, glass=False)] for f in (0, 2, 4, 6)}, "courses": True,
                        "orders": [{"tier": 0, "kind": "corinthian", "ends": False}], "at": [[0, TY, KZ, 0]],
                        "_about": "the open stage: an arch on every side, the terraces passing through it from one half of the Langgalerie to the other"})
corner = [(sx * (KW / 2 - KC / 2 + 0.55), sz * (KD / 2 - KC / 2 + 0.55)) for sx in (-1, 1) for sz in (-1, 1)]
add("kronentor columns", {"type": "colonnade", "order": "corinthian", "count": 2, "spacing": 1.15, "columnR": 0.26, "height": r4(KS - 0.95),
                          "entablature": {"h": 0.95, "depth": 0.8}, "sides": 12,
                          "at": [[r4(x), TY, r4(KZ + z), r4(math.pi / 4 if x * z > 0 else -math.pi / 4)] for x, z in corner],
                          "_about": "the paired Corinthian columns standing at the stage's cut corners"})
add("kronentor attic", {"type": "prism", "plan": {"rect": [KW + 0.9, KD + 0.9], "chamfer": KC + 0.4}, "height": 0.8, "flatRoof": True, "at": [[0, r4(TY + KS), KZ, 0]]})
add("kronentor attic 2", {"type": "prism", "plan": {"rect": [KW - 0.6, KD - 0.6], "chamfer": KC - 0.2}, "height": 1.3, "flatRoof": True, "at": [[0, r4(TY + KS + 0.8), KZ, 0]]})
KY = TY + KS + 2.1                               # (the onion's foot)
KO = dict(r=3.3, bulge=1.15, neck=0.6)
add("kronentor onion", {"type": "dome", "sides": 8, "radius": KO["r"], "thickness": 0, "turn": 0.5, "head": {"profile": "onion", "bulge": KO["bulge"], "neck": KO["neck"]},
                        "at": [[0, r4(KY), KZ, 0]], "_about": "the onion over the gate: on an octagon, dark copper with gilt ribs"})
CY = KY + onion_y_at(KO["r"], 1.0, KO["bulge"], KO["neck"])
add("kronentor crown", comp("domed-tower", {"sides": 8, "R": 1.3, "H": 1.6, "t": 0.25, "drumR": 1.0, "drumH": 0.7, "kok": 0.25, "capR": 1.2, "bulge": 1.3, "neck": 0.7, "finial": 0.9},
                            [[0, r4(CY), KZ, 0]], build=["tower", "kokoshniki", "drum", "cap", "finial"],
                            _about="the Polish crown on the onion: a gilt circlet of points, its own small onion and the orb"))
add("kronentor crown eagles", {"type": "pinnacle", "w": 0.5, "h": 1.0, "s": 0.8, "sides": 4,
                               "at": [[r4(sx * 2.6), r4(KY + 0.2), r4(KZ + sz * 2.6), 0] for sx in (-1, 1) for sz in (-1, 1)],
                               "_about": "the four gilt eagles at the onion's foot (stand-ins: pinnacles)"})
# THE BRIDGE over the Zwingergraben to the gate, and the stretch of the moat's bank beyond
add("bridge", comp("bridge", {"L": 29.0, "W": 7.0, "depth": 5.0, "n": 3, "pier": 2.2, "parapet": 1.0}, [[0, 0, r4(KZ + KD / 2), 0]],
                   _about="the bridge of three arches over the Zwingergraben to the Kronentor"))

# ===================================================================================================== THE CORNER PAVILIONS
# x 53 .. 63.7, z 29.8 .. 60 (OSM): two storeys, the upper one at the terraces' height. Nine bays toward the court (a door in the
# middle onto the raised front terrace and its perron), nine toward the outside, three on the ends -- a door into the gallery on
# each end and, upstairs, onto its terrace. Inside: the hall, and the dog-leg stair up beside the outer wall.
PX0, PX1, PZ0, PZ1 = 53.0, 63.7, 29.8, 60.0
CORNER = {(-1, 1): "mathematisch-physikalischer salon", (1, 1): "porzellanpavillon", (-1, -1): "franzoesischer pavillon", (1, -1): "deutscher pavillon"}
PAV_ROOFS, PAVS = [], []
for (sx, sz), nm in CORNER.items():
    cx, cz = sx * (PX0 + PX1) / 2, sz * (PZ0 + PZ1) / 2; W, D = PX1 - PX0, PZ1 - PZ0
    fc, fo = ("3", "1") if sx > 0 else ("1", "3")               # (the court face, the outer face)
    fg, fb = ("0", "2") if sz > 0 else ("2", "0")               # (the end on the Langgalerie / Semper side, the end on the Bogengalerie side)
    ground_win = dict(w=2.0, sill=2.2, spring=5.6); up_win = dict(w=2.0, sill=0.7, spring=4.6)
    court = [row(D, 9, ground_win["w"], ground_win["sill"], ground_win["spring"], edge=1.2, doors={4: door(0, 2.0, 4.4)}),
             row(D, 9, up_win["w"], up_win["sill"], up_win["spring"], edge=1.2)]
    outer = [row(D, 9, 1.8, 2.6, 5.4, edge=1.2, **({"doors": {4: door(0, 1.6, 3.6)}} if (sx, sz) == (-1, -1) else {})),
             row(D, 9, up_win["w"], up_win["sill"], up_win["spring"], edge=1.2)]
    upd = door(0, 1.6, 3.2)
    ends = lambda gdoor: [[op(-3.4, 1.8, 2.2, 5.6), op(3.4, 1.8, 2.2, 5.6)] + ([door(0, 1.6, 3.6)] if gdoor else []),
                          [op(-3.4, 1.8, up_win["sill"], up_win["spring"]), upd, op(3.4, 1.8, up_win["sill"], up_win["spring"])]]
    tiers = lambda two: [{"h": TY, "openings": two[0]}, {"openings": two[1]}]
    add(nm, {"type": "enclosure", "plan": {"rect": [r4(W), r4(D)]}, "thickness": 0.9, "height": PH, "glass": True, "interior": True,
             "faces": {fc: tiers(court), fo: tiers(outer), fg: tiers(ends(sz > 0)), fb: tiers(ends(True))}, "courses": True,
             "orders": [{"tier": 0, "kind": "doric"}, {"tier": 1, "kind": "corinthian"}], "at": [[r4(cx), 0, r4(cz), 0]],
             "_about": "a corner pavilion: arched windows between Doric pilasters on the ground, Corinthian above, a door at each end into the gallery and upstairs onto its terrace"})
    PAVS.append(nm)
    xa, xb = sorted((sx * PX0, sx * PX1)); za, zb = sorted((sz * PZ0, sz * PZ1))
    slab(f"{nm} floor", xa, xb, za, zb, WK, h=WK)
    # the stair: up along z beside the outer wall from near the Bogengalerie end, back on the court side, onto the upper floor
    fx = sx * (PX1 - 0.9 - 0.95); fz = sz * (PZ0 + 0.9 + 2.4)
    runL = dogleg(f"{nm} stair", (fx, fz), (0, sz), 1.8, WK, TY, (-sx, 0), about="the dog-leg stair to the upper hall, level with the terraces")
    # the upper floor: the plan less the well over the flights (railed on the court side and at its far end)
    wx0, wx1 = sorted((sx * (PX1 - 0.9), sx * (PX1 - 0.9 - 4.2))); wz0, wz1 = sorted((fz, fz + sz * (runL + 2.0)))
    ix0, ix1 = sorted((sx * (PX0 + 0.45), sx * (PX1 - 0.45))); iz0, iz1 = sorted((sz * (PZ0 + 0.45), sz * (PZ1 - 0.45)))
    slab(f"{nm} upper floor", xa, xb, za, wz0, TY, about="the upper hall's floor, level with the terraces outside")
    slab(f"{nm} upper floor 2", xa, xb, wz1, zb, TY)
    if sx > 0: slab(f"{nm} upper floor 3", xa, wx0, wz0, wz1, TY)
    else: slab(f"{nm} upper floor 3", wx1, xb, wz0, wz1, TY)
    wi = wx0 if sx > 0 else wx1                                  # (the well's court-side edge)
    INNER_RAIL.run((wi, wz0), (wi, wz1), TY)
    far = wz1 if sz > 0 else wz0; near = wz0 if sz > 0 else wz1
    INNER_RAIL.run((wx0, far), (wx1, far), TY)
    hx = sx * (PX1 - 0.9 - 2.05)                                # (over the first flight's foot, where the floor drops)
    INNER_RAIL.run((hx, near), (sx * (PX1 - 0.9), near), TY)
    add(f"{nm} roof", {"type": "roof", "form": "mansard", "width": r4(W + 0.6), "length": r4(D + 0.6), "lowerPitch": 62, "breakH": 3.0, "pitch": 16, "overhang": 0.25,
                       "at": [[r4(cx), PH, r4(cz), 0]], "_about": "the curved copper mansard"})
    PAV_ROOFS.append(f"{nm} roof")
    # the raised FRONT TERRACE along its court face, and the double perron down from its middle
    tx0, tx1 = sorted((sx * PX0, sx * (PX0 - 3.6)))
    add(f"{nm} front terrace", {"type": "prism", "plan": {"rect": [3.6, r4(D - 2.0)]}, "height": WK, "walked": True, "at": [[r4(sx * (PX0 - 1.8)), 0, r4(cz), 0]],
                                "_about": "the raised terrace along the pavilion's court face"})
    add(f"{nm} perron", {"type": "prism", "plan": {"sides": 16, "radius": 3.2}, "height": WK, "walked": True, "at": [[r4(sx * (PX0 - 3.6)), 0, r4(cz), 0]],
                         "_about": "the perron's half-round landing before the middle door"})
    for side in (-1, 1):
        flight(f"{nm} perron flight {'a' if side < 0 else 'b'}", (sx * (PX0 - 3.6 - 6 * 0.34), r4(cz + side * 5.0)), (sx, 0), 2.6, 0, WK, run=0.34,
               about="the perron's flights either side of its half-round landing, up from the court to the front terrace")
    BAL.run((sx * (PX0 - 3.5), za + 1.0), (sx * (PX0 - 3.5), cz - 6.5), WK)     # (stopped at the flights)
    BAL.run((sx * (PX0 - 3.5), cz + 6.5), (sx * (PX0 - 3.5), zb - 1.0), WK)
    # balustrade round the roof's foot -- statues on it (below)

# ===================================================================================================== THE BOGENGALERIEN
# from each corner pavilion to the Wallpavillon (west) or the Glockenspielpavillon (east): a straight run of eight bays along the
# court (z +-23.4) to x +-78, then a quarter circle of seven round (+-78, 0) to the apex pavilion -- the band from the inner line
# (r 23.4) to the outer (r 33.4); one storey as the Langgalerie, its floor raised, the raised walk with its four steps along the court
def bogen_quadrant():
    """the band in the (+x, +z) quadrant, tagged by edge"""
    inner = [(PX0, RI), (CX, RI)] + arc(RI, 0, AI, NA)[1:]
    outer = arc(RO, 0, AO, NA)[::-1] + [(PX1, RO), (PX1, PZ0), (PX0, PZ0)]
    end = [(CX + 20.47, 8.7), (CX + 25.5, 8.7)]           # (round the apex pavilion's flank)
    pts = inner + end + outer
    tags = ["in-straight"] + ["in-arc"] * NA + ["apex-nook", "apex-flank", "apex-out"] + ["out-arc"] * NA + ["out-straight", "out-step", "pav-end", "court-end"]
    assert len(tags) == len(pts), (len(tags), len(pts))
    return pts, tags
QB, QT = bogen_quadrant()
GAL_NAMES = []
for sx in (-1, 1):
    for sz in (-1, 1):
        pts = [(sx * x, sz * z) for x, z in QB]
        pts, tags = oriented(pts, QT)
        E = edges(pts); faces = {}
        for i, (e, tg) in enumerate(zip(E, tags)):
            L = e["L"]
            if tg == "in-straight":
                ops = row(L, 8, 2.1, 2.2, 5.4, edge=0.9, doors={3: door(0, 1.8, 3.9)})
            elif tg == "in-arc":
                ops = [door(0, 1.8, 3.9)] if i == [j for j, t in enumerate(tags) if t == "in-arc"][3] else [op(0, 2.0, 2.2, 5.4)]
            elif tg == "out-arc": ops = [op(0, 1.9, 2.6, 5.4)]
            elif tg == "out-straight": ops = row(L, 4, 1.9, 2.6, 5.4, edge=1.0)
            elif tg == "pav-end": ops = [door(along(e, sx * (PX0 + PX1) / 2, sz * PZ0), 1.6, 3.6)]
            elif tg == "apex-flank": ops = [door(along(e, sx * (CX + 23.0), sz * 8.7), 1.6, 3.6)]
            else: ops = []
            faces[str(i)] = ops
        nm = f"bogengalerie {'e' if sx > 0 else 'w'}{'n' if sz > 0 else 's'}"
        add(nm, {"type": "enclosure", "plan": {"points": P2(pts)}, "thickness": 0.9, "height": GH, "glass": True, "interior": True, "faces": faces,
                 "courses": True, "orders": [{"tier": 0, "kind": "doric"}], "at": [[0, 0, 0, 0]],
                 "_about": "a Bogengalerie: eight bays straight along the court and seven round the quarter circle, arched windows between Doric pilasters"})
        GAL_NAMES.append(nm)
        add(f"{nm} floor", {"type": "prism", "plan": {"points": P2(pts)}, "height": WK, "at": [[0, 0, 0, 0]]}); FLOORS.append(f"{nm} floor")
        add(f"{nm} terrace", {"type": "prism", "plan": {"points": P2(pts)}, "height": SL, "walked": True, "at": [[0, GH, 0, 0]],
                              "_about": "its roof, the terrace walked round from the corner pavilion to the apex pavilion"})
        # the balustrades along both edges of the terrace (stopped at the pavilions)
        il = [(sx * x, sz * z) for x, z in [(PX0, RI + 0.15), (CX, RI + 0.15)] + arc(RI + 0.15, 0, AI - 1.0, NA)[1:]]
        ol = [(sx * x, sz * z) for x, z in [(PX1 + 0.1, RO - 0.15), (CX, RO - 0.15)] + arc(RO - 0.15, 0, AO - 0.8, NA)[1:]]
        for line in (il, ol):
            for a, b in zip(line, line[1:]): BAL.run(a, b, TY)
        VASES += [il[0], il[1], il[4], il[-1], ol[1], ol[4], ol[-1]]
        # THE RAISED WALK along the court face: a band 3 m out from the gallery, four steps down its whole length
        for k in range(4):
            off = 3.0 + (3 - k) * 0.36; y = (k + 1) * WK / 4
            inner = [(PX0, RI - off), (CX, RI - off)] + arc(RI - off, 0, AI + 2.0, NA * 2)[1:]
            band = [(PX0, RI)] + [(CX, RI)] + arc(RI, 0, AI + 2.0, NA * 2)[1:]
            pb = band + inner[::-1]
            pb = [(sx * x, sz * z) for x, z in pb]
            pb = pb if area(pb) < 0 else pb[::-1]
            add(f"{nm} walk {k + 1}", {"type": "prism", "plan": {"points": P2(pb)}, "height": r4(WK / 4), "walked": True, "at": [[0, r4(k * WK / 4), 0, 0]],
                                       **({"_about": "the raised walk along the gallery: four steps, each a band, the top one the walk"} if k == 0 else {})})
            STONE_FLOORS.append(f"{nm} walk {k + 1}")

# ===================================================================================================== THE WALLPAVILLON / GLOCKENSPIEL
# the apex pavilions (OSM 23039959, 192745254): the Wallpavillon's front at x -92.5 with its cut corners, its flanks at z +-8.7,
# its back on the rampart at -103.5 and the middle bay standing out to -107; the Glockenspielpavillon the same at +x, deeper.
def apex_plan(sx, x_front, x_back, x_rear, rear_w):
    q = [(x_front, -7.1), (x_front, 7.1), (x_front + 1.6, 8.7), (x_back, 8.7), (x_back, rear_w + 0.8), (x_rear, rear_w), (x_rear, -rear_w), (x_back, -rear_w - 0.8), (x_back, -8.7), (x_front + 1.6, -8.7)]
    tags = ["front", "corner", "flank", "back", "rear-side", "rear", "rear-side", "back", "flank", "corner"]
    pts = [(sx * x, z) for x, z in q]
    return oriented(pts, tags)
APEX = {"wallpavillon": (-1, 92.5, 103.5, 107.0, 2.6), "glockenspielpavillon": (1, 93.5, 107.3, 112.7, 5.2)}
AH = TY + 7.8                                                   # (their eaves)
for nm, (sx, xf, xb, xr, rw) in APEX.items():
    pts, tags = apex_plan(sx, xf, xb, xr, rw); E = edges(pts); faces = {}
    wall = nm == "wallpavillon"
    for i, (e, tg) in enumerate(zip(E, tags)):
        if tg == "front":
            g = [op(0, 3.6, 0, 4.8, glass=False), op(-4.9, 2.2, 0, 3.8, glass=False), op(4.9, 2.2, 0, 3.8, glass=False)]
            u = [op(0, 2.8, 0.5, 5.0), op(-4.5, 2.2, 0.8, 4.6), op(4.5, 2.2, 0.8, 4.6)]
        elif tg == "corner": g, u = [], [op(0, 1.1, 1.2, 4.4)]
        elif tg == "flank":
            g = [door(along(e, sx * (CX + 23.0), e["m"][1]), 1.6, 3.6)] if wall else []
            u = [door(along(e, sx * (CX + 23.0), e["m"][1]), 1.6, 3.4), op(along(e, sx * (xf + 3.6), e["m"][1]), 1.8, 0.8, 4.6)]
        elif tg == "back": g, u = [], [op(0, 1.6, 1.0, 4.4)]
        elif tg == "rear": g, u = ([op(0, 3.2, 0, 4.4, glass=False)] if not wall else []), [door(0, 1.8, 3.4)]
        else: g, u = [], []
        faces[str(i)] = [{"h": TY, "openings": g}, {"openings": u}]
    add(nm, {"type": "enclosure", "plan": {"points": P2(pts)}, "thickness": 0.9, "height": AH, "glass": True, "interior": True, "faces": faces, "courses": True,
             "orders": [{"tier": 0, "kind": "ionic"}, {"tier": 1, "kind": "corinthian"}], "at": [[0, 0, 0, 0]],
             "_about": ("the Wallpavillon: three arches to the court, the stair rising through the middle one; the festival hall over it, level with the terraces and the rampart"
                        if wall else "the Glockenspielpavillon: the passage through its middle arch to the street, its upper hall level with the terraces, the porcelain bells on its court front")})
    PAVS.append(nm)
    W = xb - xf
    add(f"{nm} roof", {"type": "roof", "form": "mansard", "width": r4(W + 0.6), "length": 18.0, "lowerPitch": 64, "breakH": 2.8, "pitch": 22, "chamfer": 1.8, "overhang": 0.25,
                       "at": [[r4(sx * (xf + xb) / 2), AH, 0, 0]], "_about": "the curved copper roof"})
    add(f"{nm} rear roof", {"type": "roof", "form": "hip", "width": r4(xr - xb + 0.4), "length": r4(2 * rw + 1.0), "pitch": 30, "overhang": 0.2,
                            "at": [[r4(sx * (xb + xr) / 2 + sx * 0.2), AH, 0, 0]]})
    PAV_ROOFS += [f"{nm} roof", f"{nm} rear roof"]
# --- the Wallpavillon's GRAND STAIR: six steps from the court to the middle arch, a flight inward to the grotto landing, the two
# arms back either side up to the festival hall's floor at the front (the 1755 plan; Wikipedia: "die Treppe teilt sich ... in zwei Arme")
XF, XB = -92.5, -103.5
flight("wallpavillon court steps", (XF + 6 * 0.36, 0), (-1, 0), 7.0, 0, WK, run=0.36, about="the six steps from the court before the Wallpavillon")
slab("wallpavillon threshold", XB, XF, -8.7, 8.7, WK, h=WK)
WR = 0.26
n1 = 24; rise = (TY - WK) / 46
x, z, yaw = XF - 0.9, 0, r4(math.pi)
add("wallpavillon stair", {"type": "staircase", "flight": n1, "width": 3.6, "run": WR, "rise": r4(rise), "soffit": 0.35,
                           "landing": {"depth": 2.4, "width": 8.8, "then": [{"from": "back", "at": s, "flight": 22, "width": 2.2, "landing": {"depth": 0.62, "width": 2.2}} for s in (-3.3, 3.3)]},
                           "at": [[x, WK, z, yaw]], "_about": "the grand stair: up through the middle arch to the grotto landing, then the two arms back either side to the festival hall"})
XL0 = XF - 0.9 - n1 * WR; XL1 = XL0 - 2.4                     # (the grotto landing)
YL = WK + n1 * rise
add("wallpavillon grotto", {"type": "prism", "plan": {"rect": [r4(abs(-107.0 + 0.9 - XL1) + 0.0), 5.2]}, "height": r4(YL), "at": [[r4((-107.0 + 0.9 + XL1) / 2), 0, 0, 0]],
                            "_about": "the grotto behind the landing, the big fountain on it"})
FLOORS.append("wallpavillon grotto")
add("wallpavillon fountain", {"type": "enclosure", "plan": {"sides": 12, "radius": 1.4}, "thickness": 0.3, "height": 0.6, "openings": [], "glass": False, "interior": False, "courses": False,
                              "at": [[-105.0, r4(YL), 0, 0]]})
add("wallpavillon fountain water", {"type": "prism", "plan": {"sides": 12, "radius": 1.15}, "height": 0.45, "flatRoof": True, "at": [[-105.0, r4(YL), 0, 0]]}); WATER.append("wallpavillon fountain water")
XA = XL0 + 22 * WR                                              # (where the arms arrive, at the front)
slab("wallpavillon upper floor front", XA, XF, -8.7, 8.7, TY, about="the festival hall's floor: along the front, where the arms arrive")
slab("wallpavillon upper floor back", XB, XL0 + 0.3, -8.7, 8.7, TY)
slab("wallpavillon upper floor rear", -107.0, XB, -2.6, 2.6, TY)
for s in (-1, 1):
    slab(f"wallpavillon upper floor side {'a' if s < 0 else 'b'}", XL0 + 0.3, XA, *sorted((s * 4.65, s * 8.7)), TY)
    INNER_RAIL.run((XL0 + 0.3, s * 4.7), (XA, s * 4.7), TY)
INNER_RAIL.run((XA, -1.8), (XA, 1.8), TY)
INNER_RAIL.run((XL0 + 0.3, -4.65), (XL0 + 0.3, 4.65), TY)
# --- the Glockenspielpavillon: the passage on its axis at the court's level, the stair beside it up to the upper hall
GF, GB = 93.5, 107.3
slab("glockenspielpavillon floor", GF, 112.7, -8.7, 8.7, 0.04, h=0.04)
gr = dogleg("glockenspielpavillon stair", (GF + 0.9 + 1.7, 6.5), (1, 0), 1.9, 0.04, TY, (0, -1), run=0.26, about="the stair from the passage hall up to the upper hall and the terraces")
gw0 = GF + 0.9 + 1.7; gw1 = gw0 + gr + 2.0
slab("glockenspielpavillon upper floor", GF, GB, -8.7, 2.5, TY, about="the upper hall's floor, the stair's well left open beside it")
slab("glockenspielpavillon upper floor 2", GF, gw0, 2.5, 8.7, TY)
slab("glockenspielpavillon upper floor 3", gw1, GB, 2.5, 8.7, TY)
slab("glockenspielpavillon upper floor rear", GB, 112.7, -5.2, 5.2, TY)
INNER_RAIL.run((gw0, 2.55), (gw1, 2.55), TY); INNER_RAIL.run((gw1, 2.55), (gw1, 7.8), TY)
INNER_RAIL.run((gw0, 5.3), (gw0, 7.8), TY)
# the forty Meissen porcelain BELLS (1933): hung in two groups of twenty on the court front's upper storey, either side of the middle window
BELLS = [[r4(GF - 0.2), r4(TY + 1.5 + 0.72 * j), r4(s * (1.725 + 0.45 * i)), 0] for s in (-1, 1) for i in range(4) for j in range(5)]
add("glockenspiel bell frame", {"type": "box", "width": 0.14, "length": 0.14, "height": 5.0, "at": [[r4(GF - 0.2), r4(TY), r4(s * z), 0] for s in (-1, 1) for z in (1.45, 3.35)],
                                "_about": "the gilt frames the bells hang in: posts and a beam"})
add("glockenspiel bell beams", {"type": "box", "width": 0.14, "length": 2.04, "height": 0.16, "at": [[r4(GF - 0.2), r4(TY + 1.66 + 0.72 * j), r4(s * 2.4), 0] for s in (-1, 1) for j in range(5)],
                                "standsOn": ["glockenspiel bell frame"]})
add("glockenspiel bells", {"type": "dome", "radius": 0.21, "thickness": 0, "sides": 10, "head": {"profile": "bell", "waist": 0.75, "lift": 1.0}, "at": BELLS,
                           "_about": "the forty porcelain bells of the Glockenspiel, white Meissen, in two groups of twenty between the windows"})
# ===================================================================================================== THE RAMPART AND THE NYMPHENBAD
# THE WALL behind the Wallpavillon, at the terraces' height: from the Bogengalerien's outer arcs out to x -135, the moat's bank in
# front (+z) and the Nymphenbad's back (-z); the cascade comes down from it into the Nymphenbad
nw = [(-x, z) for x, z in arc(RO, 15, AO, 6)]                     # (the NW gallery's outer arc, from 15 degrees to its end)
sw = [(-x, -z) for x, z in arc(RO, AO, 31, 5)]
ramp = [(-135.0, 55.0), (-86.6, 55.0)] + nw + [(XB, 8.7), (XB, 3.4), (-107.0, 2.6), (-107.0, -2.6), (XB, -3.4), (XB, -8.7)] + sw + [(-102.5, -37.0), (-102.5, -58.0), (-135.0, -58.0)]
ramp = [p for i, p in enumerate(ramp) if i == 0 or math.dist(p, ramp[i - 1]) > 0.05]
ramp = ramp if area(ramp) < 0 else ramp[::-1]
add("rampart", {"type": "prism", "plan": {"points": P2(ramp)}, "height": TY, "walked": True, "at": [[0, 0, 0, 0]],
                "_about": "the Wall: the old city rampart the Wallpavillon stands on, its top level with the terraces"})
BAL.run((-135.0 + 0.2, 54.8), (-86.8, 54.8), TY); BAL.run((-134.8, 54.8), (-134.8, -57.8), TY); BAL.run((-134.8, -57.8), (-102.7, -57.8), TY)
BAL.run((-102.7, -57.8), (-102.7, -37.2), TY)
add("rampart shell fountain", {"type": "enclosure", "plan": {"sides": 16, "radius": 6.0}, "thickness": 0.4, "height": 0.6, "openings": [], "glass": False, "interior": False, "courses": False,
                               "at": [[-121.5, TY, 27.5, 0]], "_about": "the Schalenbecken on the rampart (OSM 242554060)"})
add("rampart shell water", {"type": "prism", "plan": {"sides": 16, "radius": 5.7}, "height": 0.45, "flatRoof": True, "at": [[-121.5, TY, 27.5, 0]]}); WATER.append("rampart shell water")
# THE NYMPHENBAD (OSM 148734764): a walled court x -63.5 .. -102, z -33.5 .. -55, at the court's level -- six steps below the
# Franzoesischer Pavillon's floor, from whose door a flight comes down into it; at its west end the cascade falls from the
# rampart in four steps into a half-round basin; the square fountain in its middle, the nymphs along its walls
NB = (-88.5, -44.3); NRX, NRZ = 13.4, 10.4
apse = [(NB[0] - (NRX + 0.5) * math.sin(math.pi * k / 10), NB[1] - (NRZ + 0.5) * math.cos(math.pi * k / 10)) for k in range(11)]
add("nymphenbad paving", {"type": "prism", "plan": {"points": P2((lambda q: q if area(q) < 0 else q[::-1])([(-63.6, -33.5), (-88.5, -33.5)] + [(NB[0] - NRX * math.sin(math.pi * k / 10), NB[1] + NRZ * math.cos(math.pi * k / 10)) for k in range(1, 10)] + [(-88.5, -55.0), (-63.6, -55.0)]))},
                          "height": 0.04, "walked": True, "at": [[0, 0, 0, 0]], "_about": "the Nymphenbad's floor"})
STONE_FLOORS.append("nymphenbad paving")
path = [(-63.6, -55.5), (-88.5, -55.5)] + apse + [(-78.5, -33.9)]
add("nymphenbad walls", {"type": "range", "path": P2(path), "width": 1.0, "height": 6.8, "solid": True, "at": [[0, 0, 0, 0]],
                         "_about": "the Nymphenbad's walls, south side and the west apse, the cascade's wall"})
for k in range(4):                                              # (the cascade: four falls from the rampart into the basin)
    add(f"nymphenbad cascade {k + 1}", {"type": "prism", "plan": {"rect": [r4(1.4 * (4 - k)), 6.0]}, "height": r4(1.7 * (k + 1)), "flatRoof": True,
                                        "at": [[r4(-102.0 + 0.7 * (4 - k)), 0, NB[1], 0]], **({"_about": "the cascade, four falls of water down the apse's wall"} if k == 0 else {})})
    WATER.append(f"nymphenbad cascade {k + 1}")
semi = [(r4(-96.3 + 5.0 * math.sin(math.pi * k / 12)), r4(NB[1] + 5.0 * math.cos(math.pi * k / 12))) for k in range(13)]
semi = semi if area(semi) < 0 else semi[::-1]
add("nymphenbad cascade basin", {"type": "enclosure", "plan": {"points": semi}, "thickness": 0.4, "height": 0.7, "openings": [], "glass": False, "interior": False, "courses": False,
                                 "at": [[0, 0.04, 0, 0]], "_about": "the half-round basin at the cascade's foot"})
add("nymphenbad cascade pool", {"type": "prism", "plan": {"points": [[r4(-96.3 + (x + 96.3) * 0.92), r4(NB[1] + (z - NB[1]) * 0.92)] for x, z in semi]}, "height": 0.5, "flatRoof": True,
                                "at": [[0, 0.04, 0, 0]]}); WATER.append("nymphenbad cascade pool")
add("nymphenbad fountain", {"type": "enclosure", "plan": {"rect": [13.4, 12.7]}, "thickness": 0.45, "height": 0.6, "openings": [], "glass": False, "interior": False, "courses": False,
                            "at": [[-74.8, 0.04, -44.5, 0]], "_about": "the square fountain in the middle (OSM 242420721)"})
add("nymphenbad fountain water", {"type": "prism", "plan": {"rect": [12.5, 11.8]}, "height": 0.45, "flatRoof": True, "at": [[-74.8, 0.04, -44.5, 0]]}); WATER.append("nymphenbad fountain water")
add("nymphenbad jets", {"type": "column", "radius": 0.12, "height": 3.2, "sides": 8, "taper": 0.25, "at": [[r4(-74.8 + dx), 0.49, r4(-44.5 + dz), 0] for dx, dz in ((0, 0), (-3.5, -3.5), (-3.5, 3.5), (3.5, -3.5), (3.5, 3.5))]})
WATER.append("nymphenbad jets")
flight("nymphenbad steps", (-63.7 - 6 * 0.3 - 0.0, -44.9), (1, 0), 2.4, 0.04, WK, run=0.3, about="down from the Franzoesischer Pavillon's door into the Nymphenbad")

# ===================================================================================================== THE CORNER ANNEXES
# the later blocks behind the corner pavilions (OSM 192745243, 243081542, 243081543): one plain storey to the galleries' height
for nm, (x0, x1, z0, z1) in {"mathematisch-physikalischer salon annex": (-86.0, -63.7, 33.5, 55.0), "porzellanpavillon annex": (63.7, 86.0, 33.5, 60.5),
                             "deutscher pavillon annex": (63.7, 86.0, -60.5, -33.5)}.items():
    W, D = x1 - x0, z1 - z0
    add(nm, {"type": "enclosure", "plan": {"rect": [r4(W), r4(D)]}, "thickness": 0.8, "height": GH, "glass": True, "interior": True, "courses": True,
             "faces": {"0": row(W, 6, 1.6, 2.6, 5.4), "2": row(W, 6, 1.6, 2.6, 5.4), "1": row(D, 6, 1.6, 2.6, 5.4), "3": row(D, 6, 1.6, 2.6, 5.4)},
             "at": [[r4((x0 + x1) / 2), 0, r4((z0 + z1) / 2), 0]], "_about": "a later annex behind the corner pavilion: one plain storey"})
    add(f"{nm} roof", {"type": "prism", "plan": {"rect": [r4(W + 0.3), r4(D + 0.3)]}, "height": 0.5, "flatRoof": True, "at": [[r4((x0 + x1) / 2), GH, r4((z0 + z1) / 2), 0]]})

# ===================================================================================================== THE SEMPERGALERIE
# Gottfried Semper's gallery (1847-55) closing the court toward the Theaterplatz (OSM 3278006): 127 m long, z -69.6 .. -87, two
# storeys over a raised ground floor -- the ground storey rusticated with arched windows, the upper one tall arched windows
# between Corinthian pilasters -- 23.8 m to the balustrade; in the middle the TRIUMPHAL ARCH, the passage from the court to the
# square under the domed hall (the dome 9 m over the roof). Inside: a row of halls toward the court and of cabinets toward the
# square on both floors, doors in line, a dog-leg stair in each wing; the upper floor at the terraces' height, reached from the
# corner pavilions over the terraces between.
SF = 1.4                                                         # the ground floor
SZ0, SZ1 = -87.0, -69.6; SXR, SXE = 6.85, 63.75                   # (its depth; the arch's half width, the wings' ends)
SH1, SH2 = TY, 11.8                                               # (the storeys)
STOP = SH1 + SH2
SEMPER_GROUND, SEMPER_UPPER = [], []
for sx in (-1, 1):
    cx = sx * (SXR + SXE) / 2; W = SXE - SXR; D = SZ1 - SZ0; wing = "east" if sx > 0 else "west"
    inner_face, outer_face = ("3", "1") if sx > 0 else ("1", "3")
    g_court = row(W, 13, 2.2, 2.8, 6.2, edge=1.6)
    g_square = row(W, 13, 2.2, 2.8, 6.2, edge=1.6)
    u_court = row(W, 13, 2.4, 1.4, 7.2, edge=1.6, doors={(12 if sx > 0 else 0): door(0, 1.8, 3.6)})
    u_square = row(W, 13, 2.4, 1.4, 7.2, edge=1.6)
    add(f"sempergalerie {wing}", {"type": "enclosure", "plan": {"rect": [r4(W), r4(D)]}, "thickness": 1.0, "height": SH1, "glass": True, "interior": True, "courses": True,
                                  "faces": {"0": g_court, "2": g_square, inner_face: [door(0, 2.0, 4.0)], outer_face: row(D, 3, 2.2, 2.8, 6.2, edge=2.0)},
                                  "at": [[r4(cx), 0, r4((SZ0 + SZ1) / 2), 0]], "_about": "the Sempergalerie's ground storey: rusticated, arched windows"})
    add(f"sempergalerie {wing} upper", {"type": "enclosure", "plan": {"rect": [r4(W), r4(D)]}, "thickness": 0.9, "height": SH2, "glass": True, "interior": True, "courses": True,
                                        "faces": {"0": u_court, "2": u_square, inner_face: [door(0, 2.2, 4.4)], outer_face: row(D, 3, 2.4, 1.4, 7.2, edge=2.0)},
                                        "orders": [{"tier": 0, "kind": "corinthian"}], "at": [[r4(cx), SH1, r4((SZ0 + SZ1) / 2), 0]],
                                        "_about": "the upper storey: the picture galleries, tall arched windows between Corinthian pilasters"})
    SEMPER_GROUND.append(f"sempergalerie {wing}"); SEMPER_UPPER.append(f"sempergalerie {wing} upper")
    xa, xb = sorted((sx * SXR, sx * SXE))
    slab(f"sempergalerie {wing} floor", xa, xb, SZ0, SZ1, SF, h=SF)
    # the stair: in the first cabinet bay by the arch, up along x from the arch's side to the upper floor
    fx = sx * (SXR + 1.0 + 1.7); fz = SZ0 + 1.0 + 1.05
    sr = dogleg(f"sempergalerie {wing} stair", (fx, fz), (sx, 0), 2.0, SF, TY, (0, 1), run=0.29, about="the stair up to the picture galleries")
    hx0, hx1 = sorted((fx, fx + sx * (sr + 2.0)))
    zs = SZ0 + 1.0 + 4.6
    slab(f"sempergalerie {wing} upper floor", xa, xb, zs, SZ1, TY, h=0.6, about="the upper floor, the stair's well left open by the square's wall")
    slab(f"sempergalerie {wing} upper floor 2", *(sorted((sx * SXR, fx))), SZ0, zs, TY, h=0.6)
    slab(f"sempergalerie {wing} upper floor 3", *(sorted((sx * SXE, fx + sx * (sr + 2.0)))), SZ0, zs, TY, h=0.6)
    INNER_RAIL.run((hx0, zs), (hx1, zs), TY)
    INNER_RAIL.run((fx + sx * (sr + 2.0), SZ0 + 1.0), (fx + sx * (sr + 2.0), zs), TY)
    INNER_RAIL.run((fx, SZ0 + 1.0), (fx, SZ0 + 1.0 + 2.1), TY)
    # the INTERNAL WALLS: the spine between the halls (toward the court) and the cabinets (toward the square), cross walls
    # every 13.8 m in the halls and 6.9 in the cabinets, every doorway on one line -- on both floors
    zsp = -80.4
    for lv, (y0, H) in enumerate(((SF, SH1 - SF), (TY, SH2))):
        xs = [sx * (SXR + 0.5 + 13.8 * k) for k in range(5)]
        iwall(f"sempergalerie {wing} spine {lv}", (sx * (SXR + 1.0), zsp), (sx * (SXE - 1.0), zsp), y0, H,
              [(abs(x - sx * (SXR + 1.0)) - 6.9, 2.0, 3.6) for x in xs[1:]], t=0.6,
              about="the spine wall between the halls and the cabinets, a door into each hall")
        for k in range(1, 4):
            x = sx * (SXR + 0.5 + 13.8 * k)
            iwall(f"sempergalerie {wing} cross {lv}.{k}", (x, SZ1 - 1.0), (x, zsp), y0, H, [(abs(SZ1 - 1.0 - (-75.5)), 2.4, 4.2)], t=0.5)
            if not (lv == 0 and k == 1) and k != 1:
                iwall(f"sempergalerie {wing} cabinet {lv}.{k}", (x, zsp), (x, SZ0 + 1.0), y0, H, [(abs(zsp - (-83.7)), 1.4, 3.0)], t=0.4)
    add(f"sempergalerie {wing} roof", {"type": "roof", "form": "hip", "width": r4(W + 0.4), "length": r4(D + 0.4), "pitch": 14, "overhang": 0.2,
                                       "at": [[r4(cx), STOP, r4((SZ0 + SZ1) / 2), 0]], "_about": "the low roof over the top-lit galleries"})
    add(f"sempergalerie {wing} attic", {"type": "prism", "plan": {"rect": [r4(W + 0.5), 0.8]}, "height": 1.1, "flatRoof": True,
                                        "at": [[r4(cx), STOP, r4(z), 0] for z in (SZ1 - 0.15, SZ0 + 0.15)]})
    BAL.run((sx * (SXR + 0.2), SZ1 + 0.05), (sx * (SXE + 0.1), SZ1 + 0.05), STOP + 1.1)
    BAL.run((sx * (SXR + 0.2), SZ0 - 0.05), (sx * (SXE + 0.1), SZ0 - 0.05), STOP + 1.1)
    BAL.run((sx * (SXE + 0.1), SZ0 - 0.05), (sx * (SXE + 0.1), SZ1 + 0.05), STOP + 1.1)
# the TRIUMPHAL ARCH: the passage on the axis (z -59.7 .. -89.3), flights up to it at both ends; the domed hall over it
AZ0, AZ1 = -89.3, -59.7
arch_faces = lambda inner: {"0": [op(0, 5.0, 0, 6.2, glass=False)], "2": [op(0, 5.0, 0, 6.2, glass=False)],
                            "1": inner(1), "3": inner(3)}
add("semper arch", {"type": "enclosure", "plan": {"rect": [2 * SXR, r4(AZ1 - AZ0)]}, "thickness": 1.2, "height": SH1, "glass": False, "interior": False, "courses": True,
                    "faces": arch_faces(lambda f: [door(r4(((AZ0 + AZ1) / 2 - (SZ0 + SZ1) / 2) * (1 if f == 1 else -1)), 2.0, 4.0)]),
                    "orders": [{"tier": 0, "kind": "corinthian", "ends": False}], "at": [[0, 0, r4((AZ0 + AZ1) / 2), 0]],
                    "_about": "the triumphal arch through the gallery's middle: the passage from the court to the Theaterplatz"})
add("semper arch hall", {"type": "enclosure", "plan": {"rect": [2 * SXR, r4(AZ1 - AZ0)]}, "thickness": 1.0, "height": SH2, "glass": True, "interior": True, "courses": True,
                         "faces": {"0": [op(0, 3.6, 1.0, 7.0)], "2": [op(0, 3.6, 1.0, 7.0)],
                                   "1": [door(r4((AZ0 + AZ1) / 2 - (SZ0 + SZ1) / 2), 2.2, 4.4)], "3": [door(r4(-((AZ0 + AZ1) / 2 - (SZ0 + SZ1) / 2)), 2.2, 4.4)]},
                         "orders": [{"tier": 0, "kind": "corinthian"}], "at": [[0, SH1, r4((AZ0 + AZ1) / 2), 0]],
                         "_about": "the hall over the passage, under the dome, between the two wings' galleries"})
slab("semper arch passage", -SXR, SXR, AZ0, AZ1, SF, h=SF, about="the passage's floor, raised as the gallery's")
slab("semper arch hall floor", -SXR, SXR, AZ0, AZ1, TY, h=0.8)
for sz, z in ((1, AZ1), (-1, AZ0)):
    flight(f"semper arch steps {'court' if sz > 0 else 'square'}", (0, z + sz * 8 * 0.36), (0, -sz), 9.0, 0, SF, run=0.36,
           about="the broad flight up to the passage")
add("semper arch attic", {"type": "prism", "plan": {"rect": [2 * SXR + 0.6, r4(AZ1 - AZ0 + 0.6)]}, "height": 2.4, "flatRoof": True, "at": [[0, STOP, r4((AZ0 + AZ1) / 2), 0]],
                          "_about": "the attic over the arch, the dome's drum standing on it"})
add("semper dome", comp("drum-dome", {"R": 4.4, "dt": 0.8, "H": 3.0, "n": 8, "every": 1, "winW": 1.1, "winSill": 0.6, "winH": 1.6, "profile": "segmental", "rise": 3.6,
                                      "lanternR": 0.9, "lanternH": 1.6}, [[0, r4(STOP + 2.4), -75.9, 0]],
                        _about="the dome over the middle: an octagonal drum, a low copper dome and its lantern -- 9 m over the roof"))
# the EMBANKMENT on the court side (a lawn rising to the gallery's foot) and the terraces from the corner pavilions to the upper floor
for sx in (-1, 1):
    W = 44.0 - 8.4
    add(f"semper embankment {'east' if sx > 0 else 'west'}", {"type": "prism", "plan": {"rect": [r4(W), 10.3]},
                                                            "height": 0.75, "slope": [0, -0.068], "at": [[r4(sx * (8.4 + W / 2)), 0, -64.45, 0]],
                                                            "_about": "the lawn sloping up from the court to the gallery's foot"})
    LAWNS.append(f"semper embankment {'east' if sx > 0 else 'west'}")
    nm = f"semper terrace {'east' if sx > 0 else 'west'}"
    add(nm, {"type": "prism", "plan": {"rect": [r4(PX1 - 44.0), r4(-PZ1 - SZ1 + 0.0)]}, "height": TY, "walked": True, "at": [[r4(sx * (44.0 + PX1) / 2), 0, r4((-PZ1 + SZ1) / 2), 0]],
             "_about": "the terrace from the corner pavilion's upper floor to the Sempergalerie's, on its vaulted substructure"})
    BAL.run((sx * 44.2, -60.2), (sx * 44.2, -69.4), TY); BAL.run((sx * 44.2, -60.2), (sx * 52.8, -60.2), TY)
    VASES += [(sx * 44.2, -60.2), (sx * 44.2, -69.4)]

# ===================================================================================================== VASES AND STATUES
stat = {}
# Hercules Saxonicus carrying the globe, on the Wallpavillon's roof, looking over the court
WRF = (XF - XB + 0.6) / 2 - 2.8 / math.tan(math.radians(64))      # (the mansard's upper slope's half width)
hy = AH + 2.8 + WRF * math.tan(math.radians(22))
stat["hercules pedestal"] = pedestal((r4((XF + XB) / 2), r4(hy - 0.4), 0), 1.4, 1.4, 1.4, "the pedestal of Hercules on the Wallpavillon's roof")
stat["statue hercules"] = statue((r4((XF + XB) / 2), r4(hy + 1.0), 0), kind="man", style="roman", stone="sandstone", scale=2.2, seed=5, face=FACE_PX)
GY = AH + 2.8 + ((GB - GF + 0.6) / 2 - 2.8 / math.tan(math.radians(64))) * math.tan(math.radians(22))
stat["glockenspiel pedestal"] = pedestal((r4((GF + GB) / 2), r4(GY - 0.4), 0), 1.2, 1.2, 1.2)
stat["statue glockenspiel"] = statue((r4((GF + GB) / 2), r4(GY + 0.8), 0), kind="man", style="roman", stone="sandstone", scale=1.8, seed=9, face=FACE_NX)
k = 0
for sx in (-1, 1):                                                # the Langgalerie's terrace: figures over its court-side piers
    for i in range(7):
        x = sx * (KX + 4.0 + 7.2 * i + 3.6)
        stat[f"statue langgalerie {k}"] = statue((r4(x), TY + 0.2, LZ0 + 0.6), kind="woman" if k % 2 else "man", style="roman", stone="sandstone", scale=1.15, seed=20 + k, face=FACE_NZ)
        k += 1
for sx in (-1, 1):                                                # the Kronentor's stage: a figure over each cut corner
    for sz in (-1, 1):
        stat[f"statue kronentor {sx} {sz}"] = statue((r4(sx * 3.4), r4(TY + KS + 0.8), r4(KZ + sz * 3.4)), kind="woman" if sx * sz > 0 else "man", style="roman", stone="sandstone",
                                                     scale=1.2, seed=60 + sx + 2 * sz, face=FACE_NZ if sz < 0 else FACE_PZ)
for (sx, sz), nm in CORNER.items():                              # the corner pavilions: figures at the eaves of the court front
    for dz in (-9.0, 0.0, 9.0):
        stat[f"statue {nm} {dz}"] = statue((r4(sx * (PX0 + 0.4)), r4(PH + 0.1), r4(sz * (PZ0 + PZ1) / 2 + dz)), kind="woman" if dz else "man", style="roman", stone="sandstone",
                                           scale=1.3, seed=70 + int(dz) + 3 * sx + 5 * sz, face=FACE_NX if sx > 0 else FACE_PX)
for i, (x, z) in enumerate([(-66.0, -54.4), (-72.0, -54.4), (-78.0, -54.4), (-84.0, -54.4), (-93.0, -53.3), (-99.5, -48.5)]):
    stat[f"statue nymph {i}"] = statue((x, 0.04, z), kind="woman", style="greek", stone="sandstone", scale=1.1, seed=90 + i, face=FACE_PZ if z < -50 else 0.6)
for sx in (-1, 1):                                                # the Sempergalerie's arch: figures on its attic
    for d in (-4.5, 4.5):
        stat[f"statue semper {sx} {d}"] = statue((r4(d), r4(STOP + 2.4), r4(AZ1 + 0.4 if sx > 0 else AZ0 - 0.4)), kind="man" if d < 0 else "woman", style="roman",
                                                 stone="sandstone", scale=1.4, seed=110 + int(d) + sx, face=FACE_PZ if sx > 0 else FACE_NZ)
for kk, v in capped(stat).items(): add(kk, v)
for kk, v in BAL.parts("balustrade").items(): add(kk, v)
for kk, v in INNER_RAIL.parts("stair rail").items(): add(kk, v)
add("vase bodies", {"type": "column", "radius": 0.2, "height": 0.62, "sides": 10, "taper": 1.6, "at": [[r4(x), r4(TY + 1.0), r4(z), 0] for x, z in VASES if abs(z) > 1],
                    "_about": "the vases on the balustrades' posts"})
add("vase lids", {"type": "dome", "radius": 0.3, "thickness": 0, "sides": 10, "head": {"profile": "semicircular"}, "at": [[r4(x), r4(TY + 1.62), r4(z), 0] for x, z in VASES if abs(z) > 1],
                  "standsOn": ["vase bodies"]})

# ===================================================================================================== THE DEFINITION
# THE ZWINGERGRABEN (OSM 242553936): a pool the game carves along the Kronentor's side, x -168 .. 62, its shore OSM's outline
# (kept a metre clear of the Langgalerie's outer face, which stands in the water at its west end)
GRABEN = [(-164.8, 56.25), (-161.22, 57.53), (-144.0, 59.1), (-136.87, 59.96), (-122.07, 61.59), (-86.74, 64.43), (-64.06, 65.6), (-10.13, 69.8), (-3.1, 70.42), (-0.49, 70.56), (2.33, 70.79),
          (10.15, 71.58), (62.33, 75.63), (60.98, 98.09), (52.12, 98.17), (17.08, 94.77), (4.06, 94.64), (-2.75, 94.53), (-91.98, 90.36), (-167.62, 86.44)]
GRABEN = [(x, max(z, LZ1 + 0.6) if -66 < x < 66 else max(z, 56.0)) for x, z in GRABEN]
GRABEN = [(x, z) for x, z in GRABEN]
gx0, gx1 = min(p[0] for p in GRABEN), max(p[0] for p in GRABEN); gz0, gz1 = min(p[1] for p in GRABEN), max(p[1] for p in GRABEN)
GX, GZ = r4((gx0 + gx1) / 2), r4((gz0 + gz1) / 2)
shore = [[r4(x - GX), r4(z - GZ)] for x, z in GRABEN]
doc = {"name": "Zwinger, Dresden",
       "_about": "THE ZWINGER, Dresden (Poeppelmann and Permoser, 1710-28; the Sempergalerie 1847-55), after OpenStreetMap and the 1755 plans: the court "
                 "with its apsidal ends, lawns and four basins; the Langgalerie either side of the Kronentor and the four Bogengalerien, one-storey halls "
                 "whose roofs are the terraces walked all round the court behind balustrades with statues and vases; the four corner pavilions with their "
                 "stairs to the upper halls, the Wallpavillon with its grand stair and Hercules, the Glockenspielpavillon with the porcelain bells; the "
                 "Kronentor over the bridge across the Zwingergraben; the Nymphenbad with its cascade; the Sempergalerie with its domed arch, its halls "
                 "and stairs; the rampart. Generated by tools/archgen/zwinger.py. +x toward the Glockenspielpavillon, +z toward the Kronentor.",
       "params": {"detail": 4},
       "site": {"moat": {"pool": True, "hw": r4((gx1 - gx0) / 2), "hd": r4((gz1 - gz0) / 2), "shore": shore, "w": 0, "depth": 4.4, "surface": -0.5, "x": GX, "z": GZ}},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/zwinger.json"), "w").write(json.dumps(doc, indent=1) + "\n")

# ===================================================================================================== THE FINISH
GROUND_STONE = ["court"]
fin = {"name": "Zwinger, Dresden", "building": "architecture/zwinger",
       "_about": "The Zwinger: warm Saxon (Elbe) sandstone, its sculpture weathered darker; green copper on the pavilions' roofs, the Kronentor's onion dark with gilt ribs "
                 "and the crown gilt; the Sempergalerie in the darker sandstone, its ground storey rusticated, a slate roof and a copper dome; the court's red-brown gravel, "
                 "lawns, water; inside, marble floors and stucco walls, the stairs and floors of the galleries in sandstone flags.",
       "stone": {"color": "#d9c49c", "accent": "#b9a27a", "pat": "ashlar"},
       "rules": [
           {"parts": ["kronentor crown", "kronentor crown eagles"], "pattern": "roofs/gold leaf", "_about": "the gilt crown and eagles"},
           {"parts": ["kronentor onion"], "pattern": "roofs/sheet metal", "palette": "lead", "_about": "the onion's dark copper"},
           {"parts": ["glockenspiel bells"], "pattern": "stone/plaster", "palette": "plaster-white", "_about": "white Meissen porcelain"},
           {"parts": ["glockenspiel bell frame", "glockenspiel bell beams"], "pattern": "roofs/gold leaf"},
           {"parts": ["semper dome"], "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the Sempergalerie's copper dome"},
           {"parts": [f"sempergalerie {w} roof" for w in ("east", "west")], "pattern": "roofs/slate", "palette": "slate"},
           {"parts": ["vase bodies", "vase lids", "wall fountain shells", "wall fountains", "basin jet bowls", "kronentor attic", "kronentor attic 2"], "pattern": "stone/ashlar fine", "palette": "meissen-sandstone",
            "_about": "the vases, the fountains' shells and bowls: carved sandstone"},
           {"parts": PAV_ROOFS, "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the pavilions' green copper"},
           {"parts": "kind:roof", "pattern": "roofs/sheet metal", "palette": "copper"},
           {"parts": "kind:dome", "pattern": "roofs/sheet metal", "palette": "copper"},
           {"parts": WATER, "color": "#4f6a72", "accent": "#7d98a0", "_about": "the water of the basins, the cascade and the jets"},
           {"parts": LAWNS, "pattern": "materials/grass", "palette": "lawn"},
           {"parts": ["court", "kronentor passage floor"], "pattern": "stone/sand", "palette": "gravel", "_about": "the court's red-brown gravel"},
           {"parts": SEMPER_GROUND + ["semper arch"], "surface": "wall", "side": "out", "pattern": "stone/rusticated", "palette": "meissen-dark", "_about": "the Sempergalerie's rusticated ground storey"},
           {"parts": SEMPER_UPPER + ["semper arch hall", "semper arch attic"] + [f"sempergalerie {w} attic" for w in ("east", "west")], "surface": "wall", "side": "out",
            "pattern": "stone/ashlar", "palette": "meissen-dark", "_about": "its upper storey in the darker sandstone"},
           {"parts": ["rampart"], "surface": "floor", "pattern": "materials/grass", "palette": "lawn", "_about": "the lawns on the rampart"},
           {"parts": ["rampart", "nymphenbad walls"], "pattern": "stone/ashlar", "palette": "meissen-sandstone"},
           {"parts": INTERIOR_WALLS, "pattern": "stone/plaster", "palette": "plaster-ochre", "_about": "the halls' partitions in ochre stucco"},
           {"surface": "floor", "side": "in", "pattern": "floors/checker", "palette": "marble-grey"},
           {"surface": "floor", "pattern": "floors/flagstones", "palette": "sandstone"},
           {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-ochre"},
           {"surface": "wall", "pattern": "stone/ashlar", "palette": "meissen-sandstone", "_about": "the warm Elbe sandstone, ashlar"}]}
open(os.path.join(ROOT, "assets/finishes/zwinger.json"), "w").write(json.dumps(fin, indent=2) + "\n")
print(f"zwinger: {len(parts)} parts")
