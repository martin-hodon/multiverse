# THE GRAND PALACE, BANGKOK (Phra Borom Maha Ratcha Wang, from 1782) and WAT PHRA KAEW (Wat Phra Si Rattana Satsadaram),
# from the Thai library (tools/archgen/thai.py) and, for the Chakri Maha Prasat's European body, neoclassical.py.
#
# THE FRAME: OpenStreetMap's plan turned so the palace's own axes are the frame's -- the OSM metres (x east, z south of
# 13.7500 N, 100.4915 E) turned 2.83 degrees (the Chakri Maha Prasat's front and the ubosot's long sides come out square)
# and then half a turn, its origin at OSM (31.5, -82.0): so +Z is NORTH -- the front, the north wall on Na Phra Lan Road
# with the visitors' gate -- and +X is WEST. Every footprint below is OSM's in that frame: the palace wall (way 23482754)
# with its forts, Wat Phra Kaew's cloister (relation 10124: its outer and inner rings averaged into the galleries' middle
# line), the ubosot (23482983), the upper terrace's buildings, the eight prangs (23482991-98), the Chakri Maha Prasat
# (relation 18593471), the Dusit Maha Prasat (82541999), the Phra Maha Monthien (205631558, 82538505, 229772447), the
# inner walls, the lawns and the outer court's buildings. The positions OSM does not have -- the upper terrace's edges,
# the cloister's gates and the yakshas beside them, the twelve salas' roofs -- from the Commons plans ("Plan of Wat Phra
# Kaew (with labels).svg", "Plan of the Grand Palace, Bangkok (with labels).svg"). Heights from the literature and
# photographs: Phra Si Rattana Chedi 40 m, the Chakri Maha Prasat's central spire about 45 m, the Dusit Maha Prasat's 42.
#
# THE CUT: the palace north of OSM z = +68 -- the Outer Court, Wat Phra Kaew, the Middle Court (the Phra Maha Monthien, the
# Chakri Maha Prasat, the Dusit Maha Prasat, the Boromphiman) -- a wall across at Z = -150 standing for the Inner Court's.
# The Outer Court's offices and museums (grey on the plan) are rendered wings of one to three storeys, windowed, under hip
# roofs (the big ones ranges round a court, Sala Sahathai Samakhom under a Thai roof); the Inner Court is not built.
# WALKABLE: the cloister galleries (the murals on their outer walls' inner faces), the ubosot on its marble terrace (the
# Emerald Buddha on his gilded altar at its west end), the upper terrace and its buildings' doors, the throne halls (the
# Amarin Winitchai with the Busabok Mala throne, the Phaisan Thaksin, the Chakraphat Phiman, the Dusit Maha Prasat with
# its throne), the Chakri Maha Prasat (the entrance hall, the stair up to the throne hall on the principal floor, the
# wings' halls through the doors on both floors).
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from thai import (hall, cross, chedi, prang, gate, roof, wall_run, ridge_of, cross_top, write_components, r4, Q, CHEDI_Y, ROOT)
from neoclassical import block

WALLS = []                    # (every wall's line, kept: the Outer Court's buildings keep their doors and windows off them)
_wall_run = wall_run
def wall_run(add, name, pts, **kw):
    WALLS.append((list(pts) + ([pts[0]] if kw.get("closed") else []), kw.get("t", 1.4)))
    return _wall_run(add, name, pts, **kw)

parts = {}; build = []
def add(n, d):
    assert n not in parts, n
    parts[n] = d; build.append(n); return n
def comp(use, params, at, about=None, **kw):
    d = {"type": "component", "use": f"components/{use}", "params": params, "at": at, **kw}
    if about: d["_about"] = about
    return d
FLAT = {"profile": "flat"}
P = lambda x, y, z, yaw=0.0: [r4(x), r4(y), r4(z), r4(yaw)]
INDENT = lambda a: [[r4(x * a), r4(z * a)] for x, z in [(1, -0.72), (1, 0.72), (0.72, 0.72), (0.72, 1), (-0.72, 1), (-0.72, 0.72), (-1, 0.72),
                                                     (-1, -0.72), (-0.72, -0.72), (-0.72, -1), (0.72, -1), (0.72, -0.72)]]   # (a square, its corners indented)

def flight(name, x, z, d, y0, y1, w, run=0.3, about=None, **kw):
    """a straight flight `w` wide whose TOP edge's middle is (x, z), climbing toward `d` ("+x", "-x", "+z", "-z") from y0 to y1"""
    n = max(2, math.ceil((y1 - y0) / 0.17 - 1e-6)); L = n * run
    at = {"+x": [x - L, 0, z + w / 2, 0], "-x": [x + L, 0, z - w / 2, math.pi],
          "+z": [x - w / 2, 0, z - L, -Q], "-z": [x + w / 2, 0, z + L, Q]}[d]
    dd = {"type": "flight", "width": r4(w), "run": run, "rise": r4((y1 - y0) / n), "base": r4(y0), "top": r4(y1), "landing": 0,
          "at": [[r4(a) for a in at]], **kw}
    if about: dd["_about"] = about
    return add(name, dd)

def poly_area(p): return abs(sum(p[i][0] * p[i - 1][1] - p[i - 1][0] * p[i][1] for i in range(len(p)))) / 2

# =====================================================================================================================
# THE PALACE WALL: OSM's ring from the cut on the west side, up the west wall, along the north wall, down the east wall to
# the cut (its forts' bastions are in the line); white, crenellated with bai sema, 5 m high
CUT = -150.0
PALACE = [(212.2, CUT), (218.2, -118.5), (218.8, -115.2), (222.9, -115.9), (223.9, -116.1), (226.2, -103.9), (220.6, -103.1), (220.9, -100.3),
          (221.2, -97.7), (226.9, -98.1), (228.4, -86.0), (227.1, -85.9), (222.8, -85.3), (226.8, -41.3), (227.3, -34.3), (227.8, -26.2), (233.7, 45.3),
          (234.9, 63.0), (236.2, 78.9), (236.4, 81.2), (240.3, 81.0), (242.3, 80.8), (245.6, 118.5), (244.1, 118.6), (238.6, 119.3), (242.4, 164.8),
          (242.7, 168.7), (239.8, 174.9), (227.1, 175.0), (169.4, 174.0), (162.5, 173.9), (58.5, 171.8), (37.3, 171.5), (36.7, 176.1),
          (33.0, 178.8), (26.0, 178.6), (21.9, 174.6), (21.7, 170.8), (-86.8, 168.1), (-101.5, 167.8), (-174.3, 166.0), (-175.7, 172.1),
          (-182.5, 174.6), (-188.5, 168.8), (-187.0, 162.5), (-180.1, 160.8), (-185.6, 105.6), (-186.7, 95.0), (-187.5, 87.9), (-193.7, 29.6),
          (-200.2, 26.6), (-201.2, 19.4), (-195.5, 14.8), (-205.6, -80.5), (-209.5, -80.0), (-214.4, -83.7), (-215.2, -90.8), (-211.5, -94.7),
          (-206.8, -95.5), (-208.9, -116.3), (-209.7, -124.3), (-210.7, -133.4), (-212.5, CUT)]
WALL_H, WALL_T = 5.0, 1.6
# the gates in it: (name, (x, z), the wall's direction there, about)
def dir_at(pts, g):
    best = None
    for p, q in zip(pts, pts[1:]):
        L = math.dist(p, q); ex, ez = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        a = max(0, min(L, (g[0] - p[0]) * ex + (g[1] - p[1]) * ez)); c = (p[0] + ex * a, p[1] + ez * a)
        d = math.dist(c, g)
        if best is None or d < best[0]: best = (d, (ex, ez), c)
    return best[1], best[2]
PALACE_GATES = [("wiset chaisri gate", (8.0, 170.5), "Pratu Wiset Chaisri, the visitors' gate on Na Phra Lan Road"),
                ("manee noppharat gate", (-52.0, 169.0), "Pratu Manee Noppharat, the north gate by Wat Phra Kaew"),
                ("sawatdi sopha gate", (-192.8, 38.0), "Pratu Sawatdi Sopha, the east gate by Wat Phra Kaew"),
                ("thewaphithak gate", (-209.6, -123.8), "Pratu Thewaphithak, the east gate to the Middle Court"),
                ("west gate", (234.4, 55.0), "a gate in the west wall")]
GW = 9.0
wall_run(add, "palace wall", PALACE, H=WALL_H, t=WALL_T, out=-1, gaps=[(g, GW) for _, g, _ in PALACE_GATES],
         about="THE PALACE WALL (1782, OSM way 23482754): whitewashed brick, the bai sema merlons on its outer edge, round the forts' bastions")
for name, g, about in PALACE_GATES:
    (ex, ez), c = dir_at(PALACE, g)
    add(name, comp("thai-gate", gate(GW, WALL_T + 3.0, 4.2, 5.6, 19.0, "spire", "five"), [P(c[0], 0, c[1], math.atan2(-ez, ex))], about=about))
wall_run(add, "inner court wall", [(-212.5, CUT), (212.2, CUT)], H=WALL_H, t=1.2, out=1,
         about="the wall where this model ends: it stands for the Inner Court's (the women's quarter south of it is not built)")
FORTS = {"khan kuenphet": [(37.3, 171.5), (21.7, 170.8), (21.9, 174.6), (26.0, 178.6), (33.0, 178.8), (36.7, 176.1)],
         "phadet datsakon": [(-174.3, 166.0), (-180.1, 160.8), (-187.0, 162.5), (-188.5, 168.8), (-182.5, 174.6), (-175.9, 173.2), (-175.7, 172.1)],
         "sanchorn chaiwing": [(-193.7, 29.6), (-195.5, 14.8), (-201.2, 19.4), (-200.2, 26.6)],
         "singkhornkhan": [(-205.6, -80.5), (-206.8, -95.5), (-211.5, -94.7), (-215.2, -90.8), (-214.4, -83.7), (-209.5, -80.0)],
         "maha satta loha": [(221.2, -97.7), (222.8, -85.3), (227.1, -85.9), (228.4, -86.0), (226.9, -98.1)],
         "maha satta loha south": [(218.8, -115.2), (220.6, -103.1), (226.2, -103.9), (223.9, -116.1), (222.9, -115.9)],
         "thasana nikorn": [(243.5, 115.9), (233.7, 116.7), (230.6, 86.1), (240.4, 85.3)],
         "northwest": [(242.7, 168.7), (239.8, 174.9), (234.0, 175.0), (236.5, 168.4)]}
for i, (nm, pts) in enumerate(FORTS.items()):
    cx, cz = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    add(f"fort {nm}", {"type": "prism", "plan": {"points": [[r4(x - cx), r4(z - cz)] for x, z in pts]}, "height": 6.4,
                       "courses": [{"y": 5.9, "h": 0.5, "out": 0.2, "profile": "cornice"}], "at": [P(cx, 0, cz)],
                       **({"_about": "THE FORTS (pom) on the wall's corners and along it -- Khan Kuenphet, Phadet Datsakon, Sanchorn Chaiwing, "
                                     "Singkhornkhan, Maha Satta Loha, Thasana Nikorn (OSM): white bastions over the wall, a watch pavilion's spire on each"} if i == 0 else {})})
    add(f"fort {nm} spire", comp("thai-spire", {"w": 3.2, "H": 8.0, "tiers": "three", "detail": 2}, [P(cx, 6.4, cz)]))

# THE GROUND: the palace's paving within the wall; the lawns on it (OSM's grass)
add("paving", {"type": "prism", "plan": {"points": [[x, z] for x, z in PALACE]}, "height": 0.05, "walked": True, "at": [[0, 0, 0, 0]],
               "_about": "the paved courts within the walls"})
LAWNS = [
    [(44.4, 79.5), (47.8, 82.0), (50.7, 147.5), (48.2, 151.9), (-16.0, 151.7), (-17.9, 148.8), (-14.6, 84.6), (-13.0, 82.2)],
    [(-23.0, 109.3), (-20.4, 109.1), (-18.6, 85.0), (-19.9, 82.4), (-24.0, 80.8), (-23.8, 84.2)],
    [(-23.1, 149.0), (-25.1, 152.1), (-30.9, 151.9), (-30.9, 117.6), (-22.9, 117.4), (-21.6, 117.3)],
    [(104.4, 111.2), (59.6, 114.8), (57.7, 79.6), (103.5, 77.2), (101.4, 79.2), (70.8, 81.9), (73.4, 111.2), (104.2, 108.6)],
    [(106.3, 126.3), (103.0, 117.5), (60.3, 122.5), (60.3, 151.0), (64.5, 151.0), (64.5, 149.4), (72.4, 149.6), (72.7, 138.2), (87.4, 138.5), (87.4, 135.0),
     (100.3, 135.5), (100.3, 132.1), (101.9, 129.3), (104.5, 126.6)],
    [(116.4, 132.7), (135.7, 133.1), (135.2, 125.2), (140.2, 124.9), (139.3, 119.4), (149.1, 118.3), (148.4, 115.0), (147.2, 114.0), (113.2, 117.0), (113.6, 128.0),
     (114.5, 128.6), (116.3, 131.9)],
    [(-69.0, -43.9), (-80.6, -43.2), (-81.8, -49.6), (-84.6, -57.3), (-89.1, -65.7), (-93.0, -71.2), (-96.9, -76.1), (-97.4, -78.1), (-96.2, -79.3), (-81.3, -80.1),
     (-72.4, -80.6), (-69.8, -78.9), (-69.0, -76.4)],
    [(-69.9, -39.5), (-81.0, -39.3), (-81.3, -33.9), (-82.1, -27.8), (-83.7, -22.0), (-85.3, -17.3), (-85.1, -16.0), (-83.8, -15.6), (-70.9, -16.5), (-70.0, -17.2),
     (-70.0, -29.5), (-72.4, -28.1), (-74.2, -26.4), (-78.3, -26.7), (-80.4, -29.6), (-80.2, -33.4), (-76.8, -35.6), (-73.3, -34.3), (-71.6, -32.4), (-70.0, -32.4)],
    [(-94.7, -32.2), (-84.5, -32.4), (-84.6, -28.6), (-85.7, -24.2), (-88.8, -15.5), (-93.5, -14.9), (-101.6, -14.7), (-104.5, -16.7), (-107.2, -19.9), (-107.9, -23.1),
     (-108.0, -27.0), (-107.9, -28.4), (-94.5, -29.0)],
    [(225.6, -85.9), (238.8, 81.0), (236.4, 81.2), (234.9, 63.0), (233.7, 45.3), (227.8, -26.2), (226.8, -41.3), (222.8, -85.3)],
    [(-187.5, 87.9), (-196.0, 88.7), (-212.6, -82.0), (-205.6, -80.5), (-201.8, -45.0), (-196.0, 9.0)],
    [(-185.6, 105.6), (-193.2, 107.3), (-188.2, 160.6), (-180.1, 160.8)],
    [(-205.0, -95.4), (-207.1, -116.3), (-208.9, -116.3), (-206.8, -95.5)],
    [(240.9, 164.8), (242.6, 119.0), (238.6, 119.3)],
    [(-50.2, 75.8), (-50.1, 73.7), (-48.7, 73.7), (-48.4, 72.5), (-48.8, 71.3), (-50.9, 71.3), (-52.8, 71.4), (-53.4, 72.3), (-54.3, 73.4), (-53.9, 74.7), (-53.1, 75.6)],
    [(-115.6, 73.7), (-115.5, 71.8), (-121.9, 71.7), (-121.8, 73.2), (-120.9, 74.2), (-116.7, 74.3)],
    [(105.9, -30.2), (105.8, -27.8), (79.9, -27.4), (83.1, -29.8)],
    # the Chakri Maha Prasat's front lawns (Sanam Chakri), either side of the walk to its stair (the Grand Palace plan)
    [(19.0, -57.0), (54.5, -57.0), (54.5, -23.0), (19.0, -23.0)],
    [(64.5, -57.0), (100.0, -57.0), (100.0, -23.0), (64.5, -23.0)]]
for i, L in enumerate(LAWNS):
    if poly_area(L) < 4: continue
    cx, cz = sum(p[0] for p in L) / len(L), sum(p[1] for p in L) / len(L)
    add(f"lawn {i + 1}", {"type": "prism", "plan": {"points": [[r4(x - cx), r4(z - cz)] for x, z in L]}, "height": 0.12, "flatRoof": True, "walked": True,
                          "at": [P(cx, 0.05, cz)], **({"_about": "the lawns (OSM's grass), the Chakri Maha Prasat's two before its front"} if i == 0 else {})})

# =====================================================================================================================
# WAT PHRA KAEW
# ---- THE CLOISTER (Phra Rabiang, 1782; the Ramakien murals inside): its middle line -- OSM's outer and inner rings
# averaged -- walked so its outside is on the right: along the south side eastward, up the east side (out round the bulge
# by the east gate), west along the north side, down the west side (its two jogs). Gates where the plan has them.
GAL_W, GAL_H = 5.6, 4.6
LOOP = [(-42.7, 8.9), (-148.2, 13.9), (-145.3, 43.2), (-141.9, 77.5), (-160.5, 79.7), (-158.4, 97.0), (-156.3, 115.1), (-136.9, 113.4),
        (-134.0, 151.2), (-34.0, 149.9), (-34.0, 113.5), (-26.4, 113.5), (-26.6, 74.8), (-36.6, 74.8), (-37.6, 24.7), (-42.7, 24.7)]
# the gates: (plan's number, its point on the line, crown, the yakshas beside it (inside) or None)
YAKSHAS = {30: (("sahatsadecha", "#e8e4d8"), ("thotsakan", "#2f8a4a")), 31: (("suriyaphop", "#b8342a"), ("inthorachit", "#3a8f3f")),
           32: (("chakkrawat", "#ece6da"), ("atikai", "#7a4a9a")), 33: (("mangkonkan", "#3f9a4c"), ("wirunhok", "#27406e")),
           34: (("thotsakiriwan", "#2e8a52"), ("thotsakirithon", "#b23a2e")), 35: (("wirunchambang", "#25386a"), ("maiyarap", "#6e4294"))}
WPK_GATES = [(32, (-51.5, 9.3), "prang"), (31, (-145.3, 43.2), "spire"), (30, (-158.4, 97.0), "prang"), (36, (-82.0, 150.6), "spire"),
             (29, (-93.0, 150.8), "spire"), (35, (-26.5, 109.4), "prang"), (34, (-26.6, 78.9), "spire"), (33, (-37.1, 45.0), "prang")]
GATE_L, GATE_D = 9.0, GAL_W + 1.6

def arcs(loop):
    segs, s = [], 0.0
    for i in range(len(loop)):
        p, q = loop[i], loop[(i + 1) % len(loop)]
        L = math.dist(p, q); segs.append((s, L, p, ((q[0] - p[0]) / L, (q[1] - p[1]) / L))); s += L
    return segs, s
SEGS, TOTAL = arcs(LOOP)
def s_of(g):
    best = None
    for s0, L, p, (ex, ez) in SEGS:
        a = max(0, min(L, (g[0] - p[0]) * ex + (g[1] - p[1]) * ez)); d = math.dist((p[0] + ex * a, p[1] + ez * a), g)
        if best is None or d < best[0]: best = (d, s0 + a)
    return best[1]
def pt_at(s):
    s %= TOTAL
    for s0, L, p, (ex, ez) in SEGS:
        if s <= s0 + L + 1e-9: return (p[0] + ex * (s - s0), p[1] + ez * (s - s0)), (ex, ez)
def dir_near(s):          # (the line's direction at s: at a fold, the mean of the two)
    (a, e0), (b, e1) = pt_at(s - 0.5), pt_at(s + 0.5)
    ex, ez = e0[0] + e1[0], e0[1] + e1[1]; L = math.hypot(ex, ez)
    return ex / L, ez / L
gs = sorted((s_of(g), n, cr) for n, g, cr in WPK_GATES)
for k, (sa, na, _) in enumerate(gs):
    sb = gs[(k + 1) % len(gs)][0] + (TOTAL if k == len(gs) - 1 else 0)
    a, b = sa + GATE_L / 2, sb - GATE_L / 2
    path = [pt_at(a)[0]] + [SEGS[i % len(SEGS)][2] for i in range(len(SEGS) * 2) if a < SEGS[i % len(SEGS)][0] + (TOTAL if i >= len(SEGS) else 0) < b] + [pt_at(b)[0]]
    path = [p for i, p in enumerate(path) if i == 0 or math.dist(p, path[i - 1]) > 0.3]
    add(f"gallery {k + 1}", {"type": "range", "path": [[r4(x), r4(z)] for x, z in path], "width": GAL_W, "height": GAL_H, "thickness": 0.6, "side": "right",
                             "faces": {"in": {"every": 3.3, "width": 2.4, "end": 1.0, "sill": 0, "springing": 3.5, "head": FLAT}},
                             "roof": {"pitch": 40, "overhang": 1.0, "ends": "gable", "shell": 0.3}, "at": [[0, 0, 0, 0]],
                             **({"_about": "THE CLOISTER GALLERIES (Phra Rabiang) round the temple: the outer wall blind, the Ramakien painted on its inner face "
                                           "(178 panels), the court side open between square pillars, a steep roof over"} if k == 0 else {})})
YA = []
for s, n, crown in gs:
    (cx, cz), _ = pt_at(s); ex, ez = dir_near(s)
    yaw = math.atan2(-ez, ex)
    add(f"gate {n}", comp("thai-gate", gate(GATE_L, GATE_D, 3.2, 4.6, 16.5 if crown == "spire" else 15.0, crown, "five", bh=6.6, lean=True), [P(cx, 0, cz, yaw)],
                          about="THE CLOISTER'S GATES: a pavilion over each way through the gallery, crowned -- a spire, or a prang -- in glass mosaic"
                          if n == 32 else None))
    if n in YAKSHAS:
        nx, nz = ez, -ex                                    # (into the court: the left of the line)
        for side, (nm, colour) in zip((-1, 1), YAKSHAS[n]):
            off = GATE_L / 2 + 1.9
            x = cx + ex * side * off + nx * (GAL_W / 2 + 2.6); z = cz + ez * side * off + nz * (GAL_W / 2 + 2.6)
            add(f"yaksha {nm}", comp("yaksha", {"S": 6.0, "plinthH": 1.3}, [P(x, 0.05, z, math.atan2(nx, nz))],
                                     about="THE TWELVE YAKSHAS (1830s), a pair inside each of six gates, from the Ramakien -- each giant in his own colour, "
                                           "the costume gilt, standing on his pedestal over the court" if not YA else None))
            YA.append((nm, colour))

# ---- THE UBOSOT on its marble terrace (the ordination hall, 1783; OSM 23482983: 60.4 x 27.6): the peristyle, the walls, the
# three doors at each end, the roof in three telescoped tiers; its front -- and the Emerald Buddha's gaze -- to the EAST (-X)
UX, UZ = -90.4, 43.8
TERR = 0.6
add("ubosot terrace", {"type": "prism", "plan": {"rect": [67.0, 35.0]}, "height": TERR, "walked": True, "at": [P(UX, 0.05, UZ)],
                       "courses": [{"y": 0.42, "h": 0.18, "out": 0.12, "profile": "cornice"}],
                       "_about": "the marble terrace round the ubosot, inside its low wall (kamphaeng kaeo)"})
for nm, (x, z, d, w) in {"ubosot terrace steps east": (UX - 33.5, UZ, "+x", 4.0), "ubosot terrace steps west": (UX + 33.5, UZ, "-x", 4.0),
                         "ubosot terrace steps north": (UX, UZ + 17.5, "-z", 6.0), "ubosot terrace steps south": (UX, UZ - 17.5, "+z", 6.0)}.items():
    flight(nm, x, z, d, 0.05, 0.05 + TERR, w)          # (d: the way it climbs, onto the terrace)
# its low wall round the rim, open at the four flights; the eight sema shrines (bai sema) on it
RIM = []
for (x0, z0, x1, z1) in [(-33.3, 17.3, -3.2, 17.3), (3.2, 17.3, 33.3, 17.3), (-33.3, -17.3, -3.2, -17.3), (3.2, -17.3, 33.3, -17.3),
                         (33.3, -17.3, 33.3, -2.2), (33.3, 2.2, 33.3, 17.3), (-33.3, -17.3, -33.3, -2.2), (-33.3, 2.2, -33.3, 17.3)]:
    L = math.dist((x0, z0), (x1, z1))
    RIM.append(P(UX + (x0 + x1) / 2, 0.05 + TERR, UZ + (z0 + z1) / 2, 0 if z0 == z1 else Q) + [L])
for i, a in enumerate(RIM):
    add(f"ubosot rail {i + 1}", {"type": "box", "width": r4(a[4]), "length": 0.4, "height": 0.9, "at": [a[:4]],
                                 **({"_about": "the low wall round the terrace"} if i == 0 else {})})
SEMA_AT = [(sx * 33.3, sz * 17.3) for sx in (-1, 0, 1) for sz in (-1, 0, 1) if (sx, sz) != (0, 0)]
SEMA_AT = [(x, z) for x, z in SEMA_AT if not (x == 0 or z == 0)] + [(0, 17.3), (0, -17.3), (33.3, 0), (-33.3, 0)]
SEMA_AT = [(x, z) for x, z in SEMA_AT if abs(z) > 1 or abs(x) > 1]
SEMA_AT = [(x if abs(z) < 1 or x != 0 else 0, z) for x, z in SEMA_AT]
SEMA_AT = [(-33.3, -17.3), (0.0, -19.3), (33.3, -17.3), (35.3, 0.0), (33.3, 17.3), (0.0, 19.3), (-33.3, 17.3), (-35.3, 0.0)]
add("sema shrines", {"type": "box", "width": 1.6, "length": 1.6, "height": 1.6, "at": [P(UX + x, 0.05, UZ + z) for x, z in SEMA_AT],
                     "_about": "the eight bai sema shrines round the ubosot, marking its consecrated ground"})
add("sema shrines caps", {"type": "dome", "radius": 0.75, "sides": 8, "thickness": 0.08, "head": {"profile": "bell", "waist": 0.7, "lift": 0.9},
                          "at": [P(UX + x, 1.65, UZ + z) for x, z in SEMA_AT]})
UB = hall(16.0, 48.0, H=11.0, ph=1.8, doors=3, lots=3, stairs="all", pm=2.0, ce=3.6, ld=1.1)   # (its end pieces dropped little: the porches walked under)
add("ubosot", comp("thai-hall", UB, [P(UX, 0.05 + TERR, UZ, -Q)],
                   about="THE UBOSOT (Phra Ubosot, 1783): its platform, the peristyle of indented pillars in glass mosaic, the walls with three doors at "
                         "each end and windows down the sides, the roof of three tiers telescoped at the ends over two layers, every gable gilt"))
UY = 0.05 + TERR + UB["ph"]                                # (its floor)
# THE ALTAR at the west end inside: the gilded tiers (the busabok throne, 1782-84), the canopy over its top, the Emerald
# Buddha seated in meditation in it (jade, 66 cm; here a little larger to be seen), facing the doors (east)
AX = UX + 15.5
for i, (w, h) in enumerate([(9.0, 1.1), (7.2, 1.1), (5.4, 1.1), (3.6, 1.1)]):
    add(f"altar {i + 1}", {"type": "prism", "plan": {"points": [[r4(x * w / 2), r4(z * w / 2)] for x, z in
                                                               [(1, -0.72), (1, 0.72), (0.72, 0.72), (0.72, 1), (-0.72, 1), (-0.72, 0.72), (-1, 0.72), (-1, -0.72),
                                                                (-0.72, -0.72), (-0.72, -1), (0.72, -1), (0.72, -0.72)]]}, "height": h,
                                                               "courses": [{"y": r4(h - 0.18), "h": 0.18, "out": 0.08, "profile": "cornice"}], "at": [P(AX, UY + 1.1 * i, UZ)],
                           **({"_about": "THE ALTAR: the gilded tiers stepping up at the hall's west end"} if i == 0 else {})})
AY = UY + 4.4
add("altar canopy posts", {"type": "column", "radius": 0.12, "sides": 8, "height": 2.2, "at": [P(AX + x, AY, UZ + z) for x in (-1.3, 1.3) for z in (-1.3, 1.3)],
                           "_about": "the busabok: the canopy over the image, on four posts"})
add("altar canopy", comp("thai-spire", {"w": 3.0, "H": 3.0, "tiers": "three", "detail": 2}, [P(AX, AY + 2.2, UZ)]))
add("emerald buddha", comp("seated-buddha", {"S": 0.85}, [P(AX, AY + 0.3, UZ, -Q)],
                           about="THE EMERALD BUDDHA (Phra Kaew Morakot): the jade image seated in meditation, facing the doors"))
add("emerald buddha cushion", {"type": "prism", "plan": {"sides": 8, "radius": 0.55}, "height": 0.3, "at": [P(AX, AY, UZ)]})

# ---- THE TWELVE SALAS round the ubosot (OSM's 'chapel's), open pavilions; the two small halls and the gilt prang at its
# west end; the bell tower; the Hor Phra Khanthararat
SALAS = [(-77.5, 22.5, Q), (-59.5, 22.5, Q), (-100.0, 23.0, Q), (-118.5, 23.5, Q), (-77.5, 64.5, Q), (-57.5, 64.5, Q), (-100.5, 64.0, Q),
         (-118.5, 64.5, Q), (-47.5, 35.0, 0), (-48.0, 52.0, 0), (-130.0, 35.0, 0), (-130.0, 52.0, 0)]
SALA = hall(3.0, 5.4, H=3.0, ph=0.6, peri=True, cm=0.35, walls=False, lots=1, stairs="ends", sw=1.6, detail=2)
add("salas", comp("thai-hall", SALA, [P(x, 0.05, z, y) for x, z, y in SALAS],
                  about="THE TWELVE SALAS (sala rai) round the ubosot: open pavilions on low platforms, a roof on pillars"))
SMALL = hall(3.4, 5.6, H=3.6, ph=0.8, peri=False, lots=1, chans=1, stairs="front", detail=2)
add("west halls", comp("thai-hall", SMALL, [P(-54.5, 0.05, 36.5, Q), P(-54.5, 0.05, 50.5, Q)],
                       about="the two small halls at the ubosot's west end (Hor Phra Rajakoramanusorn, Hor Phra Rajaphongsanusorn)"))
add("phothithat phiman", comp("prang", {**prang(3.6, 9.0, lean=True), "detail": 2}, [P(-56.3, 0.05, 43.6)],
                              about="Phra Phothithat Phiman, the small gilt prang at the ubosot's west end"))
add("bell tower base", {"type": "prism", "plan": {"sides": 8, "radius": 3.6}, "height": 1.6, "walked": True, "at": [P(-90.9, 0.05, 19.4, math.pi / 8)],
                        "courses": [{"y": 1.35, "h": 0.25, "out": 0.12, "profile": "cornice"}], "_about": "THE BELL TOWER (Hor Rakhang): an octagonal base"})
flight("bell tower steps", -90.9, 19.4 - 3.3, "+z", 0.05, 1.65, 1.6)
add("bell tower posts", {"type": "column", "radius": 0.22, "sides": 8, "height": 3.6,
                         "at": [P(-90.9 + 2.6 * math.cos(k * math.pi / 4), 1.65, 19.4 + 2.6 * math.sin(k * math.pi / 4)) for k in range(8)]})
add("bell tower beam", {"type": "prism", "plan": {"sides": 8, "radius": 3.1}, "height": 0.5, "at": [P(-90.9, 5.25, 19.4, math.pi / 8)]})
add("bell tower spire", comp("thai-spire", {"w": 5.6, "H": 11.0, "tiers": "three", "detail": 2}, [P(-90.9, 5.75, 19.4)],
                             about="its spire of tiers over the bell"))
add("bell", {"type": "dome", "radius": 0.7, "sides": 12, "thickness": 0.06, "head": {"profile": "bell", "waist": 0.75, "lift": 1.0}, "at": [P(-90.9, 3.6, 19.4)]})
add("khanthararat", comp("thai-hall", hall(6.4, 8.0, H=5.4, ph=1.2, peri=False, lots=1, chans=1, stairs="front", detail=2), [P(-137.5, 0.05, 22.0)],
                         about="Hor Phra Khanthararat (OSM 229771451): the small hall of the rain-calling Buddha"))

# ---- THE UPPER TERRACE (the Phra Si Rattana Chedi's, the Mondop's and the Prasat Phra Thep Bidon's, 1855-82), its
# northern arm under the Phra Wihan Yot; its edges from the Commons plan, its buildings OSM's
TY = 2.4
TERRACE = [(-133.0, 74.5), (-44.0, 74.5), (-44.0, 85.0), (-38.2, 85.0), (-38.2, 106.0), (-44.0, 106.0), (-44.0, 119.0), (-74.0, 119.0), (-74.0, 143.5),
           (-90.5, 143.5), (-90.5, 119.0), (-133.0, 119.0)]
add("upper terrace", {"type": "prism", "plan": {"points": [[x, z] for x, z in TERRACE]}, "height": TY, "walked": True, "at": [[0, 0.05, 0, 0]],
                      "courses": [{"y": 0, "h": 0.35, "out": 0.12, "profile": "torus"}, {"y": TY - 0.3, "h": 0.3, "out": 0.15, "profile": "cornice"}],
                      "_about": "THE UPPER TERRACE: a marble platform carrying the chedi, the mondop and the royal pantheon; its arm north to the Wihan Yot"})
TT = 0.05 + TY
for nm, (x, z, d, w) in {"terrace stair south porch": (-79.7, 74.5, "+z", 4.4), "terrace stair south west": (-59.3, 74.5, "+z", 3.6),
                         "terrace stair south east": (-104.0, 74.5, "+z", 3.6), "terrace stair north west": (-59.3, 119.0, "-z", 3.6),
                         "terrace stair north east": (-104.0, 119.0, "-z", 3.6), "terrace stair east": (-133.0, 96.0, "+x", 5.0),
                         "terrace stair west porch": (-38.2, 95.5, "-x", 5.0)}.items():
    flight(nm, x, z, d, 0.05, TT, w,
           about="the flights up the upper terrace: the porches on its south and west sides, two each side, one at the east end" if "porch" in nm and "south" in nm else None)
# PHRA SI RATTANA CHEDI (1855), the gilt bell chedi on its round steps, 40 m; a porch on each side of its base
CX, CZ = -58.4, 94.2
CH = chedi(40.0, r=5.15)
add("phra si rattana chedi", comp("chedi", CH, [P(CX, TT, CZ)],
                                  about="PHRA SI RATTANA CHEDI (1855, Rama IV, after Ayutthaya's Wat Phra Si Sanphet): the bell chedi in gold mosaic, 40 m"))
for i, yaw in enumerate((0, Q, math.pi, -Q)):
    add(f"chedi porch {i + 1}", {"type": "box", "width": 3.6, "length": 3.4, "height": 3.6, "at": [P(CX + math.sin(yaw) * 8.6, TT, CZ + math.cos(yaw) * 8.6, yaw)],
                                 **({"_about": "the four porches on the chedi's base, a niche in each"} if i == 0 else {})})
    add(f"chedi porch {i + 1} roof", {"type": "roof", "form": "gable", "width": 4.0, "length": 3.8, "pitch": 55, "overhang": 0.25,
                                      "at": [P(CX + math.sin(yaw) * 8.6, TT + 3.6, CZ + math.cos(yaw) * 8.6, yaw)]})
# PHRA MONDOP (1789), the library of the Tripitaka: its square body on a redented base, a door on each side, the
# seven-tiered spire over it
MX, MZ = -79.5, 93.0
add("mondop base", {"type": "prism", "plan": {"points": INDENT(6.8)}, "height": 1.4, "walked": True, "at": [P(MX, TT, MZ)],
                    "courses": [{"y": 0, "h": 0.3, "out": 0.12, "profile": "torus"}, {"y": 1.15, "h": 0.25, "out": 0.15, "profile": "cornice"}],
                    "_about": "PHRA MONDOP (1789): the library of the Tripitaka -- its redented base"})
for d in ("+z", "-z", "+x", "-x"):
    ex, ez = {"+z": (0, 1), "-z": (0, -1), "+x": (1, 0), "-x": (-1, 0)}[d]
    flight(f"mondop steps {d}", MX + ex * 6.8, MZ + ez * 6.8, {"+z": "-z", "-z": "+z", "+x": "-x", "-x": "+x"}[d], TT, TT + 1.4, 2.4)
MW = 9.6
add("mondop", {"type": "enclosure", "plan": {"rect": [MW, MW]}, "thickness": 0.8, "height": 6.6, "glass": False, "interior": True, "openings": [],
               "faces": {str(f): [{"at": 0, "width": 1.8, "sill": 0, "springing": 3.8, "head": FLAT}] for f in range(4)},
               "courses": {"list": [{"y": 0, "h": 0.4, "out": 0.12, "profile": "torus"}, {"y": 6.1, "h": 0.5, "out": 0.2, "profile": "cornice"}]},
               "at": [P(MX, TT + 1.4, MZ)], "_about": "its body, a door on each side, green glass mosaic on its walls"})
add("mondop pillars", {"type": "prism", "plan": {"points": INDENT(0.42)}, "height": 6.6,
                       "at": [P(MX + sx * (MW / 2 + 0.5), TT + 1.4, MZ + sz * (MW / 2 + 0.5)) for sx in (-1, 1) for sz in (-1, 1)]
                             + [P(MX + sx * (MW / 2 + 0.5), TT + 1.4, MZ + sz * 2.4) for sx in (-1, 1) for sz in (-1, 1)]
                             + [P(MX + sz * 2.4, TT + 1.4, MZ + sx * (MW / 2 + 0.5)) for sx in (-1, 1) for sz in (-1, 1)],
                       "_about": "the pillars round it"})
add("mondop spire", comp("thai-spire", {"w": 11.4, "H": 21.5, "tiers": "seven"}, [P(MX, TT + 8.0, MZ)], about="its spire of seven tiers"))
add("tripitaka cabinet", {"type": "box", "width": 2.6, "length": 2.6, "height": 3.2, "at": [P(MX, TT + 1.4, MZ)],
                          "_about": "the mother-of-pearl cabinet of the Tripitaka in its middle"})
# PRASAT PHRA THEP BIDON (1855; the royal pantheon): the cruciform hall, its prang over the crossing
TBX, TBZ = -106.05, 94.5
TB = cross(28.0, 29.0, 11.0, 8.0, ph=1.4, spire="prang", spireW=8.0, spireH=24.0, lots=2, stairs="four")
add("phra thep bidon", comp("thai-cross", TB, [P(TBX, TT, TBZ)],
                            about="PRASAT PHRA THEP BIDON (1855): the cruciform royal pantheon, its prang over the crossing in coloured porcelain"))
# THE GOLDEN CHEDIS (Phra Suwannachedi, 1st reign) at its eastern corners, the four decorated chedis at the terrace's west end
add("golden chedis", comp("chedi", chedi(16.0, r=3.0, plan_="square", n=12), [P(-127.6, TT, 79.6), P(-126.2, TT, 112.5)],
                          about="the two golden chedis (Phra Suwannachedi), redented, carried by yakshas and monkeys"))
add("decorated chedis", comp("chedi", {**chedi(8.0, r=0.92, plan_="square", n=10), "detail": 2},
                             [P(-45.2, TT, 101.7), P(-51.5, TT, 107.0), P(-45.5, TT, 86.5), P(-51.5, TT, 81.0)],
                             about="the four decorated chedis (Phra Chedi Song Khrueang) at the terrace's west end"))
# THE MODEL OF ANGKOR WAT (1860s, Rama IV) on the terrace's north edge
AKX, AKZ = -82.3, 112.0
for i, (w, h) in enumerate([(10.0, 0.5), (8.0, 0.45), (6.0, 0.45)]):
    add(f"angkor model {i + 1}", {"type": "prism", "plan": {"rect": [w, w * 0.8]}, "height": h, "at": [P(AKX, TT + [0, 0.5, 0.95][i], AKZ)],
                                  **({"_about": "THE MODEL OF ANGKOR WAT (Rama IV): its three galleried terraces in little"} if i == 0 else {})})
for nm, (xs, zs, r, h) in {"angkor model towers": ([-2.2, 2.2], [-1.6, 1.6], 0.5, 2.6), "angkor model tower": ([0], [0], 0.7, 3.8)}.items():
    at = [P(AKX + x, TT + 1.4, AKZ + z) for x in xs for z in zs]
    add(nm, {"type": "column", "radius": r, "taper": 0.35, "sides": 8, "height": h, "at": at, **({"_about": "its five towers in little"} if len(at) > 1 else {})})
    add(nm + " buds", {"type": "dome", "radius": r4(r * 0.36), "sides": 8, "thickness": 0.05, "head": {"profile": "onion", "bulge": 1.1, "neck": 0.6},
                       "at": [[a[0], r4(a[1] + h), a[2], 0] for a in at]})
# THE NORTH COURT: the Phra Wihan Yot on the terrace's arm, the Hor Phra Nak (west) and the Hor Monthien Tham (east)
WY = cross(16.8, 9.6, 6.0, 5.6, ph=0.8, spire="prasat", tiers="five", spireW=4.4, spireH=14.0, lots=1, stairs="four")
add("wihan yot", comp("thai-cross", WY, [P(-82.3, TT, 132.0)], about="PHRA WIHAN YOT: the small cruciform hall under a crown-shaped spire"))
flight("wihan yot terrace steps", -82.3, 143.5, "-z", 0.05, TT, 4.0)
add("hor phra nak", comp("thai-hall", hall(8.6, 21.4, H=6.6, ph=1.0, peri=False, lots=2, chans=1), [P(-52.3, 0.05, 138.3, Q)],
                         about="HOR PHRA NAK: the hall of the royal ashes, its ridge east-west"))
add("hor monthien tham", comp("thai-hall", hall(12.0, 26.0, H=7.6, ph=1.0, cm=1.6, lots=2, stairs="ends"), [P(-113.3, 0.05, 135.8, Q)],
                               about="HOR MONTHIEN THAM: the library, its peristyle"))

# ---- THE EIGHT PRANGS (Phra Atthamaha Chedi, 1st reign) outside the east gallery, each in its own colour
PRANGS = [(-144.3, 143.7), (-146.0, 124.5), (-146.0, 106.0), (-148.5, 87.0), (-151.5, 69.5), (-153.5, 51.5), (-155.5, 37.5), (-157.6, 19.0)]
PRANG_NAMES = ["sammasamphuttha", "sattham pariyat", "ariyasong", "ariyasawika", "patchekkaphothi", "borom chakkrawat", "phothisat", "si ariyametta"]
PRANG_AT = []
for i, ((x, z), nm) in enumerate(zip(PRANGS, PRANG_NAMES)):
    # (outside the gallery: carried out to its outer side where the OSM point stands under it)
    add(f"prang {nm}", comp("prang", {**prang(8.6, 19.0, lean=True), "detail": 2}, [P(x - 12.0, 0.05, z)],
                            about="THE EIGHT PRANGS (Phra Atthamaha Chedi) in a row outside the east gallery: the Buddha, the Dhamma, the Sangha, the "
                                  "nuns, the Paccekabuddhas, the Chakravartin, the Bodhisattva, the Maitreya -- each faced in porcelain of its colour" if i == 0 else None))

# =====================================================================================================================
# THE MIDDLE COURT
# ---- THE PHRA MAHA MONTHIEN (1785): the Amarin Winitchai throne hall in front (north), the Phaisan Thaksin behind it,
# the Chakraphat Phiman (the residence) behind that; their wall (OSM 229783141) and its gates
AM = hall(17.0, 20.6, H=10.0, ph=1.0, peri=False, lots=2, chans=1, stairs="none", pm=1.6)
add("amarin winitchai", comp("thai-hall", AM, [P(-22.0, 0.05, -41.9)],
                             about="THE AMARIN WINITCHAI throne hall (1785), the audience hall: its doors north to the porch and south to the Phaisan Thaksin"))
add("amarin porch", comp("thai-hall", hall(12.4, 3.6, H=6.8, ph=1.0, peri=True, cm=0.45, ce=0.45, walls=False, lots=1, stairs="front"), [P(-22.0, 0.05, -27.1)],
                         about="its porch on pillars before the north door"))
AMY = 0.05 + 1.0
add("busabok mala base", {"type": "prism", "plan": {"rect": [4.4, 3.0]}, "height": 1.8, "at": [P(-22.0, AMY, -49.2)],
                          "courses": [{"y": 1.6, "h": 0.2, "out": 0.1, "profile": "cornice"}],
                          "_about": "THE BUSABOK MALA MAHA CHAKRAPHAT PHIMAN: the throne at the hall's back, boat-shaped, under its spire"})
add("busabok mala posts", {"type": "column", "radius": 0.12, "sides": 8, "height": 2.0, "at": [P(-22.0 + x, AMY + 1.8, -49.2 + z) for x in (-1.6, 1.6) for z in (-1.0, 1.0)]})
add("busabok mala spire", comp("thai-spire", {"w": 3.6, "H": 5.0, "tiers": "seven", "detail": 2}, [P(-22.0, AMY + 3.8, -49.2)]))
add("phuttan throne", {"type": "prism", "plan": {"rect": [3.0, 3.0]}, "height": 1.3, "at": [P(-22.0, AMY, -43.5)],
                       "_about": "the Phuttan Kanchanasinghat throne before it"})
add("phuttan umbrella", {"type": "column", "radius": 1.3, "taper": 0.25, "sides": 12, "height": 3.6, "at": [P(-22.0, AMY + 4.0, -43.5)],
                         "_about": "the nine-tiered umbrella over it"})
add("phuttan umbrella pole", {"type": "column", "radius": 0.05, "sides": 6, "height": 7.4, "at": [P(-22.0, AMY + 1.3, -43.5)]})
PT = cross(23.0, 33.0, 13.0, 9.0, ph=1.0, spire="none", lots=2, stairs="four")
add("phaisan thaksin", comp("thai-cross", PT, [P(-21.5, 0.05, -66.6)],
                            about="THE PHAISAN THAKSIN hall (1785), where the kings are crowned: a cross of halls behind the Amarin"))
add("chakraphat phiman", comp("thai-hall", hall(16.0, 37.0, H=8.0, ph=1.0, peri=False, lots=2, chans=1, stairs="ends"), [P(-19.8, 0.05, -102.5, Q)],
                              about="THE CHAKRAPHAT PHIMAN (1785), the kings' residence, its ridge east-west"))
for nm, (x, z, w, l, yaw, about) in {"dusidaphirom": (-0.6, -30.0, 3.6, 6.0, 0, "Phra Thinang Dusidaphirom, the pavilion where the king mounted his elephant"),
                                     "racharuedee": (-45.5, -51.0, 4.4, 8.0, 0, "Phra Thinang Racharuedee"),
                                     "ho sastrakhom": (-46.5, -30.5, 4.6, 7.4, 0, "Ho Sastrakhom"),
                                     "ho suralai phiman": (-45.0, -76.5, 3.6, 8.6, 0, "Ho Suralai Phiman"),
                                     "ho phra that monthian": (2.5, -74.0, 3.8, 7.6, 0, "Ho Phra That Monthian")}.items():
    add(nm, comp("thai-hall", hall(w, l, H=4.6, ph=0.8, peri=False, lots=1, chans=1, stairs="front", detail=2), [P(x, 0.05, z, yaw)], about=about))
add("mahisorn prasat", comp("thai-cross", cross(12.0, 5.0, 3.6, 4.0, ph=1.2, spire="prasat", tiers="five", spireW=2.8, spireH=9.0, lots=1, stairs="front"),
                             [P(-58.4, 0.05, -108.6)], about="Phra Thinang Mahisorn Prasat, the small spired pavilion by the wall"))
MM = [(5.4, -67.9), (5.7, -77.8), (6.1, -144.3), (-11.4, -144.4), (-27.8, -145.0), (-46.2, -145.2), (-47.8, -82.7), (-48.3, -70.4), (-50.1, -70.4),
      (-50.8, -37.2), (-50.9, -24.1), (-51.2, -19.8), (-21.3, -19.3), (-3.7, -19.1), (-3.5, -24.6), (4.9, -24.6), (4.9, -35.2)]
MM_GATES = [((-22.6, -19.3), 5.0), ((5.2, -52.0), 4.0)]
wall_run(add, "maha monthien wall", MM, H=4.6, t=1.2, out=-1, closed=True, gaps=MM_GATES,
         about="the Phra Maha Monthien's wall (OSM 229783141), its gate before the Amarin's porch")
add("maha monthien gate", comp("thai-gate", gate(7.0, 3.4, 3.6, 4.8, 15.0, "spire", "five"), [P(-22.6, 0, -19.3)], about="its gate, the spire over it"))
add("maha monthien west gate", comp("thai-gate", gate(5.6, 3.0, 2.6, 3.6, 10.0, "spire", "three", bh=4.6), [P(5.2, 0, -52.0, Q)]))

# ---- THE CHAKRI MAHA PRASAT (1876-82, John Clunis): the European body -- three storeys, the windows pedimented -- under
# THAI ROOFS, the three pavilions crowned with seven-tiered spires; on a base with the stair to its middle; the entrance
# hall, the stair up to the throne hall on the principal floor, the wings' halls through the doors
CB = 1.4                                                   # (its base)
CS = (5.5, 6.5, 5.0); CHH = sum(CS)
CZ0, CZ1 = -79.8, -66.7                                    # (the back, the wings' front)
add("chakri base", {"type": "prism", "plan": {"rect": [88.0, 19.6]}, "height": CB, "walked": True, "at": [P(59.2, 0.05, -70.5)],
                    "courses": [{"y": 0, "h": 0.3, "out": 0.1, "profile": "torus"}, {"y": CB - 0.25, "h": 0.25, "out": 0.12, "profile": "cornice"}],
                    "_about": "THE CHAKRI MAHA PRASAT (1876-82): its base, the terrace along its front"})
flight("chakri stair", 59.5, -60.7, "-z", 0.05, 0.05 + CB, 10.0, run=0.36, about="the stair up to its middle")
D = lambda f, u, k, w=2.0, h=3.4: (f, u, k, w, h, True)
WINGS = {"east pavilion": (15.7, 27.9), "east wing": (27.9, 53.4), "centre": (53.4, 65.6), "west wing": (65.6, 90.5), "west pavilion": (90.5, 102.7)}
for nm, (x0, x1) in WINGS.items():
    w = x1 - x0; xc = (x0 + x1) / 2
    if nm == "centre":
        d, zc = -61.3 - CZ0, (CZ0 - 61.3) / 2
        u = (CZ0 + CZ1) / 2 - zc
        doors = [D("+z", 0.0, 0, 3.0, 4.4), D("-x", u, 0), D("-x", u, 1), D("+x", u, 0), D("+x", u, 1)]
        against = {"-x": [(CZ0 - zc, CZ1 - zc)], "+x": [(CZ0 - zc, CZ1 - zc)]}
    else:
        d, zc = CZ1 - CZ0, (CZ0 + CZ1) / 2
        inner = "+x" if x1 < 59 else "-x"
        doors = [D(inner, 0.0, 0), D(inner, 0.0, 1)]
        against = {inner: [(-d / 2, d / 2)]}
        if "wing" in nm:
            outer = "-x" if inner == "+x" else "+x"
            doors += [D(outer, 0.0, 0), D(outer, 0.0, 1), D("+z", 0.0, 0, 2.2, 3.6)]
            against[outer] = [(-d / 2, d / 2)]
    block(add, f"chakri {nm}", w, d, xc, zc, y=0.05 + CB, storeys=CS, bay=3.6, doors=doors, against=against, order="corinthian" if nm == "centre" else None,
          T=0.9, roof=0.4, floors=nm != "centre",
          about="its body: rendered white, the ground storey rusticated, the windows pedimented, the doors between the parts on both floors" if nm == "east pavilion" else None)
CY0 = 0.05 + CB                                            # (the ground floor)
CY1 = CY0 + CS[0]                                          # (the principal floor)
CTOP = CY0 + CHH + 0.4
# the centre's floors: the entrance hall, the stair up its middle to the throne hall, the principal floor round its well
add("chakri centre floor", {"type": "box", "width": 12.16, "length": 18.46, "height": 0.1, "at": [P(59.5, CY0, (CZ0 - 61.3) / 2)]})
SN = math.ceil(CS[0] / 0.17)
SL = SN * 0.28
SZ0 = -63.4                                                # (the stair's foot, inside the door)
add("chakri grand stair", {"type": "flight", "width": 3.2, "run": 0.28, "rise": r4(CS[0] / SN), "base": r4(CY0), "top": r4(CY1), "landing": 0,
                           "at": [P(59.5 + 1.6, 0, SZ0, Q)], "_about": "THE GRAND STAIR: straight up from the entrance hall to the throne hall"})
STOP = SZ0 - SL
add("chakri principal floor back", {"type": "box", "width": 10.4, "length": r4(STOP - (CZ0 + 0.9)), "height": 0.4,
                                    "at": [P(59.5, CY1 - 0.4, (STOP + CZ0 + 0.9) / 2)], "_about": "the throne hall's floor, the stair arriving at its front"})
for sx in (-1, 1):
    add(f"chakri principal floor {'east' if sx < 0 else 'west'}", {"type": "box", "width": 3.2, "length": r4(-62.2 - STOP), "height": 0.4,
                                                                    "at": [P(59.5 + sx * 3.6, CY1 - 0.4, (STOP - 62.2) / 2)]})
add("chakri throne dais", {"type": "prism", "plan": {"rect": [5.0, 2.6]}, "height": 0.6, "at": [P(59.5, CY1, CZ0 + 2.4)],
                           "_about": "the throne under its nine-tiered umbrella, at the throne hall's back"})
add("chakri throne", {"type": "box", "width": 1.6, "length": 1.2, "height": 1.5, "at": [P(59.5, CY1 + 0.6, CZ0 + 2.4)]})
add("chakri throne umbrella", {"type": "column", "radius": 1.1, "taper": 0.25, "sides": 12, "height": 2.6, "at": [P(59.5, CY1 + 3.0, CZ0 + 2.4)]})
# THE ROOFS: the pavilions' crossed roofs with their spires, the wings' long roofs between
add("chakri centre thai roof", comp("thai-roof", roof(12.2, 20.6, 21.0, lots=2, spire="prasat", spireW=6.4, spireH=24.0), [P(59.5, CTOP, (CZ0 - 61.3) / 2)],
                                    about="THE THAI ROOFS: the three pavilions' crossed roofs, each crowned with a seven-tiered spire (the centre's the tallest), "
                                          "the wings' long roofs between them"))
for nm, x in (("east", 21.8), ("west", 96.6)):
    add(f"chakri {nm} pavilion thai roof", comp("thai-roof", roof(12.2, 15.2, 16.4, lots=2, spire="prasat", spireW=5.2, spireH=18.0), [P(x, CTOP, (CZ0 + CZ1) / 2)]))
    x0, x1 = WINGS[f"{nm} wing"]
    add(f"chakri {nm} wing thai roof", comp("thai-roof", roof(13.1, x1 - x0, pitch=45, lots=1), [P((x0 + x1) / 2, CTOP, (CZ0 + CZ1) / 2, Q)]))
# behind it: the Moon Satharn Borom Ard and the Sommuthi Thevaraj Uppabat halls (the residence's front halls), the links
for nm, (x0, x1) in {"moon satharn": (15.9, 50.0), "sommuthi thevaraj": (68.5, 103.4)}.items():
    block(add, f"{nm}", x1 - x0, 15.2, (x0 + x1) / 2, -95.8, y=0.05, storeys=(5.5, 5.0), bay=3.8, windows=[(1.2, 1.5, 2.6, True, None), (1.0, 1.5, 2.4, False, None)],
          doors=[("+z", -8.0, 0, 2.2, 3.4, True), ("+z", 8.0, 0, 2.2, 3.4, True)], order=None, T=0.8, roof=0.3,
          about="the Moon Satharn Borom Ard and the Sommuthi Thevaraj Uppabat halls behind the Chakri" if nm == "moon satharn" else None)
    add(f"{nm} thai roof", comp("thai-roof", roof(15.2, x1 - x0, pitch=45, lots=2), [P((x0 + x1) / 2, 0.05 + 10.8, -95.8, Q)]))
add("chakri links", {"type": "box", "width": 3.6, "length": 8.6, "height": 9.0, "at": [P(31.3, 0.05, -84.0), P(88.9, 0.05, -84.2)],
                     "_about": "the links from the Chakri's back to the halls behind"})

# ---- THE DUSIT MAHA PRASAT (1789), the cruciform throne hall with its seven-tiered spire; its court's wall (OSM 229892001)
# with the gate before it; the Aphorn Phimok pavilion on that wall; the Phiman Rattaya behind
DYAW = 0.1023
def drot(x, z): return (x * math.cos(DYAW) + z * math.sin(DYAW), -x * math.sin(DYAW) + z * math.cos(DYAW))
DX, DZ = 141.4, -57.5
DU = cross(34.0, 33.0, 11.0, 9.0, ph=2.6, spire="prasat", tiers="seven", spireW=7.6, spireH=26.0, lots=3, stairs="four")
add("dusit maha prasat", comp("thai-cross", DU, [P(DX, 0.05, DZ, DYAW)],
                              about="THE DUSIT MAHA PRASAT (1789): the cruciform throne hall on its high base, four porches, the roofs in four telescoped tiers, the "
                                    "seven-tiered spire over the crossing (42 m)"))
DY = 0.05 + DU["ph"]
tx, tz = drot(0, -10.5)
add("dusit throne base", {"type": "prism", "plan": {"rect": [3.6, 3.0]}, "height": 1.6, "at": [P(DX + tx, DY, DZ + tz, DYAW)],
                          "_about": "the mother-of-pearl throne and the busabok in the south arm"})
add("dusit throne spire", comp("thai-spire", {"w": 2.8, "H": 4.6, "tiers": "five", "detail": 2}, [P(DX + tx, DY + 1.6, DZ + tz, DYAW)]))
DW = [(171.6, -54.7), (174.2, -29.2), (177.1, -7.2), (175.3, -5.3), (166.9, -4.7), (123.2, -1.3), (120.1, -3.4), (118.6, -24.5), (117.7, -36.9)]
gx, gz = DX + drot(0, 1)[0] * 55.0 / 1.0 * 0, -2.7
wall_run(add, "dusit court wall", DW, H=4.6, t=1.2, out=-1, gaps=[((141.4, -2.7), 5.0)],
         about="the Dusit Maha Prasat's court wall (OSM 229892001), its gate before the hall's north porch")
add("dusit court gate", comp("thai-gate", gate(7.0, 3.4, 3.6, 4.8, 15.0, "prang", lean=True), [P(141.4, 0, -2.7, math.atan2(-(-0.078), -0.997) + math.pi)]))
add("aphorn phimok", comp("thai-cross", cross(12.0, 6.6, 4.0, 4.4, ph=2.6, walls=False, spire="prasat", tiers="five", spireW=2.8, spireH=9.6, lots=1, stairs="four"),
                          [P(117.1, 0.05, -44.3, DYAW)],
                          about="PHRA THINANG APHORN PHIMOK PRASAT: the little open pavilion on the court's wall where the king changed into his robes to mount "
                                "his palanquin -- the model of Thai proportion"))
add("phiman rattaya", comp("thai-hall", hall(15.4, 32.0, H=8.0, ph=1.0, peri=False, lots=2, chans=1), [P(137.5, 0.05, -101.0, DYAW)],
                           about="the Phiman Rattaya hall behind the Dusit"))
add("rachakaranya sapha", comp("thai-hall", hall(7.0, 12.4, H=6.0, ph=0.8, peri=False, lots=1, chans=1, detail=2), [P(115.7, 0.05, -74.7, DYAW)],
                               about="Phra Thinang Rachakaranya Sapha, the council hall"))
add("dusit walls", comp("thai-wall", {"L": 10.0, "H": 4.6, "t": 1.2}, [P(114.7, 0, -59.4, Q)]))
for nm, pts, out in (("dusit west wall", [(163.2, -133.3), (163.5, -129.6), (167.3, -89.2), (167.7, -84.9), (169.7, -62.0)], -1),
                     ("west court wall", [(208.5, 104.9), (208.2, 102.1), (193.8, -31.0), (192.8, -39.6)], 1),
                     ("chakri east wall", [(15.7, -77.4), (5.7, -77.8)], 1), ("chakri west wall", [(110.3, -80.5), (102.7, -79.8)], 1)):
    wall_run(add, nm, pts, H=4.6, t=1.2, out=out)
# THE WALL between the Outer Court and the Boromphiman's garden (OSM 229783135, 229783142), its gate
EW = [(-186.0, CUT), (-184.0, -131.3), (-185.6, -131.1), (-188.5, -127.5), (-187.8, -121.3), (-190.5, -121.0), (-178.2, -6.4), (-176.9, 9.6), (-59.4, 3.8),
      (-55.6, 3.6), (-55.0, -6.1), (-58.9, -6.3), (-59.1, -20.5), (-58.9, -26.3), (-50.9, -26.6)]
wall_run(add, "middle court wall", EW, H=4.6, t=1.2, out=-1, gaps=[((-120.0, 6.8), 4.6)],
         about="the wall round the Middle Court's east side, between the Outer Court and the Boromphiman's garden")
add("middle court gate", comp("thai-gate", gate(6.0, 3.0, 3.2, 4.4, 13.0, "spire", "three"), [P(-120.0, 0, 6.8, 0.049)]))
# THE PHIMAN CHAISRI GATES: the pair of gatehouses where the Chakri Charan road enters the Middle Court
for i, (x, z) in enumerate(((50.2, 4.2), (50.6, 15.0))):
    add(f"phiman chaisri gate {i + 1}", comp("thai-gate", gate(20.0, 5.4, 4.6, 6.0, 20.0, "spire", "five", bh=8.0), [P(x, 0, z)],
                                             about="THE PHIMAN CHAISRI GATES: the pair of gatehouses where the road enters the Middle Court" if i == 0 else None))

# (the doors: in at the front block, through to the main block, through to the wing; their shared walls blind)
BOROM_DOORS = {"boromphiman front": [("+z", 0.0, 0, 2.4, 3.6, True), ("-z", 0.0, 0, 2.0, 3.2, True)],
               "boromphiman": [("+z", -12.4, 0, 2.0, 3.2, True), ("-x", -6.0, 0, 2.0, 3.2, True)],
               "boromphiman wing": [("+x", 9.7, 0, 2.0, 3.2, True), ("+z", 0.0, 0, 2.2, 3.4, True)]}
BOROM_AGAINST = {"boromphiman front": {"-z": [(-5.45, 5.45)]}, "boromphiman": {"+z": [(-17.85, -6.95)], "-x": [(-12.25, 1.35)]},
                 "boromphiman wing": {"+x": [(3.45, 17.05)]}}
# ---- THE BOROMPHIMAN (1903), the European palace in the east garden: two storeys and a mansard
for nm, (x0, x1, z0, z1, about) in {"boromphiman": (-142.3, -96.6, -53.0, -28.5, "THE BOROMPHIMAN (1903): a neo-Renaissance palace, two storeys under mansards"),
                                    "boromphiman wing": (-165.0, -142.3, -73.5, -39.4, None),
                                    "boromphiman front": (-137.3, -126.4, -28.5, -12.6, None)}.items():
    block(add, nm, x1 - x0, z1 - z0, (x0 + x1) / 2, (z0 + z1) / 2, y=0.05, storeys=(6.0, 5.6), bay=3.8,
          windows=[(1.2, 1.6, 2.8, True, None), (1.0, 1.6, 2.6, False, {"head": "alternate", "sill": True})],
          doors=BOROM_DOORS[nm], against=BOROM_AGAINST[nm], order=None, T=0.8, roof=0.3, floors=False, about=about)
    add(f"{nm} mansard", {"type": "roof", "form": "mansard", "width": r4(x1 - x0 + 0.6), "length": r4(z1 - z0 + 0.6), "pitch": 30, "lowerPitch": 72,
                          "breakH": 3.0, "overhang": 0.0, "at": [P((x0 + x1) / 2, 0.05 + 11.6 + 0.3, (z0 + z1) / 2)]})
add("phra buddha rattanasathan", comp("thai-hall", hall(9.4, 15.6, H=6.6, ph=1.2, cm=1.1, lots=2), [P(-105.3, 0.05, -110.0, Q)],
                                      about="Phra Buddha Rattanasathan (1850s), the chapel in the Boromphiman's garden"))
add("sitalaphirom", comp("thai-hall", hall(3.6, 4.6, H=3.4, ph=0.6, cm=0.3, walls=False, lots=1, stairs="front", sw=1.6, detail=2), [P(-106.5, 0.05, -74.8)],
                         about="Phra Thinang Sitalaphirom, the open pavilion in the garden"))

# =====================================================================================================================
# THE OUTER COURT's offices and museums and the buildings along the walls (OSM; the plan's grey and brown blocks):
# white rendered wings with window rows, string courses and cornices under red-tiled hip roofs, each walked through its door
OUTER = [
    ("sala sahathai samakhom", [(37.4, 43.8), (-28.3, 47.4), (-27.1, 68.2), (-4.5, 66.9), (-4.3, 70.1), (19.2, 68.8), (19.1, 66.4), (38.6, 65.3)], 11.0),
    ("pavilion of regalia", [(45.2, 20.3), (-25.4, 23.5), (-25.5, 21.6), (-35.6, 22.0), (-34.8, 39.3), (45.9, 35.7)], 9.0),
    ("outer court range", [(36.0, -9.2), (36.6, 3.6), (-39.4, 6.9), (-39.5, 5.1), (-47.8, 5.5), (-48.3, -5.0), (-10.4, -6.6), (-10.5, -8.9), (2.1, -9.5)], 8.0),
    ("outer court range north", [(38.2, 16.2), (-39.3, 19.7), (-39.8, 8.9), (37.7, 5.4)], 8.0),
    ("principal private secretary", [(112.3, 5.8), (111.7, -12.3), (62.2, -10.6), (62.8, 7.4)], 9.0),
    ("emerald buddha museum", [(193.4, 56.1), (176.4, 57.9), (166.2, 58.9), (162.1, 19.5), (170.6, 18.7), (170.3, 15.3), (180.1, 14.3), (180.4, 17.5), (189.3, 16.6)], 9.0),
    ("textile museum", [(150.9, 169.1), (64.1, 167.2), (64.5, 149.4), (72.4, 149.6), (72.7, 138.2), (87.4, 138.5), (87.4, 135.0), (100.3, 135.5), (100.3, 132.1),
                        (104.5, 126.6), (108.8, 125.9), (113.6, 128.0), (116.3, 131.9), (116.9, 134.9), (128.6, 135.2), (128.5, 139.2), (145.1, 139.5),
                        (144.9, 151.1), (151.3, 151.3)], 11.0),
    ("sala luk khun nai", [(70.8, 81.9), (101.4, 79.2), (106.4, 74.2), (113.7, 73.8), (119.0, 77.7), (150.0, 75.0), (152.6, 104.7), (121.8, 107.4), (122.0, 109.6),
                           (104.4, 111.2), (104.2, 108.6), (73.4, 111.2)], 10.0),
    ("royal household bureau", [(143.5, 20.3), (144.0, 39.9), (141.7, 40.0), (142.3, 68.1), (79.8, 69.4), (79.4, 52.0), (73.1, 52.1), (72.9, 41.3), (80.3, 41.1),
                                (79.9, 21.7), (104.8, 21.2), (104.5, 14.6), (116.4, 14.3), (116.9, 20.9)], 10.0),
    ("north range", [(214.2, 169.8), (167.2, 170.0), (166.0, 148.6), (163.4, 148.7), (161.9, 132.1), (164.0, 131.9), (161.2, 109.3), (208.5, 104.9)], 8.0),
    ("hall by the museum", [(38.4, 96.9), (38.1, 87.2), (-10.7, 88.7), (-10.2, 104.0), (-3.8, 103.8), (-4.0, 98.3)], 8.0),
    ("row north 1", [(52.0, 158.4), (52.0, 167.0), (-32.6, 166.5), (-32.6, 158.5)], 6.0),
    ("row north 2", [(-32.5, 160.2), (-88.8, 159.7), (-88.9, 165.9), (-32.6, 166.5)], 6.0),
    ("row west 1", [(232.0, 167.0), (218.6, 168.2), (213.3, 111.1), (226.7, 109.8)], 6.0),
    ("row west 2", [(224.6, 94.0), (210.0, 95.6), (209.0, 86.4), (214.3, 85.8), (211.9, 64.1), (221.1, 63.1)], 6.0),
    ("row west 3", [(196.9, -39.0), (214.5, -40.8), (211.3, -69.7), (198.8, -68.4), (200.8, -49.2), (195.8, -48.7)], 6.0),
    ("row west 4", [(203.6, 45.5), (202.7, 37.5), (218.1, 35.8), (219.0, 43.8)], 6.0),
    ("row west 5", [(216.8, 3.9), (213.0, -27.4), (195.4, -25.3), (199.2, 6.0)], 6.0),
    ("row west 6", [(216.0, 62.0), (206.0, 63.1), (204.3, 48.0), (214.3, 46.9)], 6.0),
    ("row west 7", [(199.7, 8.3), (216.3, 6.6), (217.1, 14.3), (209.1, 15.1), (211.0, 32.5), (202.4, 33.4)], 6.0),
    ("row west 8", [(196.7, 55.8), (197.6, 64.4), (180.5, 66.1), (176.4, 57.9), (193.4, 56.1)], 6.0),
    ("row west 9", [(160.5, 91.6), (157.8, 64.0), (169.7, 62.9), (172.4, 90.5), (204.9, 87.5), (206.0, 99.5), (161.6, 103.7)], 6.0),
    ("row west 10", [(202.5, 78.6), (182.0, 80.7), (180.5, 66.1), (201.0, 64.1)], 6.0),
    ("row west 11", [(236.2, 78.9), (230.1, 79.4), (228.7, 63.5), (234.9, 63.0)], 5.0),
    ("row west 12", [(227.8, -26.2), (220.7, -25.7), (226.5, 45.9), (233.7, 45.3)], 5.0),
    ("row west 13", [(225.9, -41.3), (220.0, -40.7), (214.2, -96.8), (220.1, -97.4)], 5.0),
    ("row west 14", [(195.3, 2.5), (192.8, -24.1), (181.5, -23.0), (183.3, -3.3), (188.0, -3.7), (188.6, 3.1)], 6.0),
    ("row west 15", [(209.1, -70.6), (197.1, -69.3), (194.3, -95.4), (206.2, -96.6)], 6.0),
    ("row west 16", [(194.1, -104.6), (191.3, -117.6), (202.6, -120.0), (205.4, -107.0)], 6.0),
    ("row west 17", [(218.8, -103.9), (213.3, -103.2), (211.8, -115.0), (217.3, -115.7)], 5.0),
    ("row west 18", [(192.8, -39.6), (180.8, -38.6), (178.4, -64.2), (177.0, -80.3), (189.0, -81.4)], 6.0),
    ("row west 19", [(177.0, -80.3), (178.4, -64.2), (170.4, -63.4), (168.9, -79.6)], 6.0),
    ("row east 1", [(-191.0, 41.1), (-193.7, 10.4), (-184.0, 9.6), (-181.3, 40.3)], 6.0),
    ("row east 2", [(-175.5, 94.4), (-185.6, 95.5), (-189.5, 59.1), (-179.4, 58.0)], 6.0),
    ("row east 3", [(-194.3, 1.7), (-195.6, -10.8), (-187.4, -11.6), (-186.1, 0.9)], 5.0),
    ("row east 4", [(-164.5, 24.4), (-165.5, 11.1), (-178.5, 12.0), (-177.5, 25.4)], 6.0),
    ("row east 5", [(-167.9, 156.7), (-178.6, 157.8), (-184.2, 103.3), (-173.5, 102.2)], 6.0),
    ("row east 6", [(-178.6, -77.1), (-184.3, -76.7), (-187.9, -119.8), (-182.3, -120.2)], 5.0),
    ("dusit court halls", [(156.3, -10.6), (148.4, -10.1), (148.1, -14.6), (151.6, -14.8), (151.1, -24.1), (155.5, -24.4)], 5.0),
    ("dusit court halls 2", [(135.5, -8.9), (143.3, -9.5), (143.0, -14.0), (139.6, -13.7), (138.9, -23.1), (134.4, -22.7)], 5.0),
    ("middle court halls", [(120.3, -79.9), (120.1, -82.6), (134.3, -84.0), (134.6, -81.3)], 5.0),
    ("middle court halls 2", [(144.8, -82.4), (144.5, -85.2), (167.4, -87.7), (167.7, -84.9)], 5.0),
    ("middle court halls 3", [(139.9, -136.0), (140.6, -129.0), (128.0, -127.7), (127.2, -134.7)], 5.0),
    ("chakri rear hall", [(68.4, -103.6), (68.6, -88.6), (68.7, -80.3), (50.2, -80.3), (50.1, -88.3), (49.9, -103.4)], 12.0),
    ("monthien rear hall", [(-26.6, -113.7), (-26.3, -122.4), (-41.4, -123.0), (-40.8, -138.3), (-28.0, -137.9), (-27.8, -143.8), (-11.4, -143.4), (-11.6, -137.1),
                            (2.6, -136.6), (2.1, -122.3), (-11.4, -122.8), (-11.8, -114.4)], 7.0),
    ("museum annexes", [(64.6, 61.1), (59.2, 61.1), (59.1, 53.0), (64.5, 53.0)], 5.0),
    ("museum annexes 2", [(63.8, 39.8), (58.4, 39.8), (58.3, 31.7), (63.8, 31.6)], 5.0),
]
# THE BIG OUTLINES are ranges round a courtyard (the plan's and the photographs' quadrangles): an engine `court` -- a ring
# of rooms, windows all round outside, doors from the court, a gate in through one face, a hip roof over every side --
# on the outline simplified to its four corners; what of OSM's outline the quadrangle leaves (a porch, a wing) is cut
# into oblongs as the rest are. (name: (the quadrangle, its wings' depth))
COURTS = {"north range": ([(214.2, 169.8), (167.2, 170.0), (161.2, 109.3), (208.5, 104.9)], 12.0),
          "textile museum": ([(150.9, 169.1), (64.1, 167.2), (64.5, 138.4), (151.2, 139.5)], 10.0),
          "sala luk khun nai": ([(70.8, 81.9), (150.0, 75.0), (152.6, 104.7), (73.4, 111.2)], 10.0),
          "royal household bureau": ([(143.5, 20.3), (142.3, 68.1), (79.8, 69.4), (79.9, 21.7)], 12.0),
          "emerald buddha museum": ([(193.4, 56.1), (166.2, 58.9), (162.1, 19.5), (189.3, 16.6)], 9.0)}
THAI_ROOFED = {"sala sahathai samakhom"}                     # (a Thai hall's roof, gabled and gilt, on a rendered body)
MIDDLE = ("dusit court halls", "middle court halls", "monthien rear hall")   # (the Middle Court's halls: roofs of glazed tiles)

def inside(pt, poly):
    x, z = pt; c = False
    for (x0, z0), (x1, z1) in zip(poly, poly[1:] + poly[:1]):
        if (z0 > z) != (z1 > z) and x < x0 + (z - z0) * (x1 - x0) / (z1 - z0): c = not c
    return c
def seg_dist(p, a, b):
    L2 = (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2
    s = 0 if L2 == 0 else max(0, min(1, ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / L2))
    return math.dist(p, (a[0] + s * (b[0] - a[0]), a[1] + s * (b[1] - a[1])))
def axes_of(pts):
    """an outline's own axes: its longest side's direction, turned by quarters to lie nearest the frame's x"""
    a, b = max(zip(pts, pts[1:] + pts[:1]), key=lambda e: math.dist(*e))
    L = math.dist(a, b); ex, ez = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    return max([(ex, ez), (-ez, ex), (-ex, -ez), (ez, -ex)], key=lambda e: e[0])
def oblongs(pts, ex, ez, keep=lambda p: True, res=0.5, least=3.0):
    """the outline cut into the largest oblongs it holds, on the axes (ex, ez) (local z (-ez, ex)), greedily, the biggest
    first; `keep`: the cells counted (a world point -> bool). Returns [(cx, cz, w, d)] (w along ex)."""
    U = [x * ex + z * ez for x, z in pts]; V = [-x * ez + z * ex for x, z in pts]
    u0, v0 = min(U), min(V); nu, nv = int((max(U) - u0) / res) + 1, int((max(V) - v0) / res) + 1
    W = lambda u, v: (u * ex - v * ez, u * ez + v * ex)
    g = [[inside(W(u0 + (i + .5) * res, v0 + (j + .5) * res), pts) and keep(W(u0 + (i + .5) * res, v0 + (j + .5) * res)) for i in range(nu)] for j in range(nv)]
    total, out, mn = sum(map(sum, g)), [], int(least / res)
    while True:
        best, hts = None, [0] * nu
        for j in range(nv):
            hts = [h + 1 if c else 0 for h, c in zip(hts, g[j])]
            st = []
            for i in range(nu + 1):
                h = hts[i] if i < nu else 0; s = i
                while st and st[-1][1] >= h:
                    s, hh = st.pop()
                    if hh >= mn and i - s >= mn and (best is None or hh * (i - s) > best[0]): best = (hh * (i - s), s, i, j - hh + 1, j + 1)
                st.append((s, h))
        if best is None or best[0] * res * res < 25: break
        _, i0, i1, j0, j1 = best
        for j in range(j0, j1):
            for i in range(i0, i1): g[j][i] = False
        uc, vc = u0 + (i0 + i1) / 2 * res, v0 + (j0 + j1) / 2 * res
        out.append((*W(uc, vc), (i1 - i0) * res, (j1 - j0) * res))
        if sum(map(sum, g)) < 0.06 * total: break
    return out

STOREYS = lambda h: (h,) if h <= 6 else (h / 3,) * 3 if h >= 12 else (h / 2, h / 2)
# every building's ground: the oblongs and the quadrangles, for the probes (a face against another, or a wall, is blind)
plans, OBST = {}, []
for nm, pts, h in OUTER:
    ex, ez = axes_of(COURTS[nm][0] if nm in COURTS else pts)
    q = COURTS.get(nm, (None,))[0]
    rects = oblongs(pts, ex, ez, keep=(lambda p, q=q: not inside(p, q)) if q else (lambda p: True))
    plans[nm] = (ex, ez, rects)
    for cx, cz, w, d in rects:
        OBST.append([(cx + a * w / 2 * ex - b * d / 2 * ez, cz + a * w / 2 * ez + b * d / 2 * ex) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    if q: OBST.append(list(q))
OBST += [list(p) for p in FORTS.values()]
def blocked(p, far=False):
    if any(inside(p, o) for o in OBST): return True
    return any(seg_dist(p, a, b) < t / 2 + (2.2 if far else 0.5) for pts, t in WALLS for a, b in zip(pts, pts[1:]))
def free_runs(probe, L, step=0.5):
    """the stretches along a face (-L/2..L/2) whose probe point outside is free"""
    runs, s = [], None
    for k in range(int(L / step) + 1):
        t = -L / 2 + k * step; ok = not probe(t)
        if ok and s is None: s = t
        if not ok and s is not None: runs.append((s, t - step)); s = None
    if s is not None: runs.append((s, L / 2))
    return runs

GEN, MIDDLE_ROOFS = [], []
BAY = 5.2                     # (a window every 5.2 m: the triangles)
DOOR = lambda at: {"at": r4(at), "width": 1.8, "sill": 0, "springing": 2.9, "head": FLAT, "glass": False}
def window_row(sh, clear, k):
    wh = min(2.3, sh - 1.9)
    return {"every": BAY, "width": 1.3, "end": 1.4, "sill": 0.9 if k else 1.0, "springing": r4((0.9 if k else 1.0) + wh), "head": FLAT,
            **({"clear": clear} if clear else {})}
first = True
for nm, pts, h in OUTER:
    ex, ez, rects = plans[nm]
    yaw = math.atan2(-ez, ex)
    sts = STOREYS(h); H = sum(sts)
    middle, thai = nm.startswith(MIDDLE), nm in THAI_ROOFED
    about = ("THE OUTER COURT's offices, halls and museums and the ranges along the walls, on OSM's outlines: rendered blocks of two "
             "storeys (the ranges along the wall of one), a window every 5.2 m, string courses and cornices, hipped roofs of red tiles -- cut into wings "
             "on the outline's own axes, the big ones a ring of rooms round a court; each wing walked inside through its door") if first else None
    if nm in COURTS:
        q, D = COURTS[nm]
        cx, cz = sum(p[0] for p in q) / 4, sum(p[1] for p in q) / 4
        loc = [(x - cx, z - cz) for x, z in q]
        if sum(loc[i][0] * loc[(i + 1) % 4][1] - loc[(i + 1) % 4][0] * loc[i][1] for i in range(4)) > 0: loc = loc[::-1]
        # the gate: through the longest face whose outside is open
        cand = []
        for i in range(4):
            a, b = loc[i], loc[(i + 1) % 4]; L = math.dist(a, b); mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            nx, nz = mx / math.hypot(mx, mz), mz / math.hypot(mx, mz)        # (out from the middle, near enough on a quadrangle)
            free = not blocked((cx + mx + nx * 3.0, cz + mz + nz * 3.0), True)
            cand.append((free, L, i))
        gf = max(cand)[2]
        add(nm, {"type": "court", "plan": {"points": [[r4(x), r4(z)] for x, z in loc]}, "depth": D, "storeys": len(sts), "storeyH": r4(sts[0]),
                 "thickness": 0.7, "axis": BAY, "winW": 1.3, "sill": 0.9, "winH": r4(min(2.3, sts[0] - 1.9)), "head": FLAT, "doorW": 1.6, "doorH": 2.9,
                 "gate": {"face": gf, "width": 4.0, "height": 3.8, "head": FLAT}, "roof": {"form": "hip", "pitch": 28, "overhang": 0.7},
                 "courses": {"plinth": False}, "surroundCourt": False, "at": [P(cx, 0.05, cz)], **({"_about": about} if about else {})})
        GEN += [f"{nm}/roof {i + 1}" for i in range(4)]
        first = False
    for k, (cx, cz, w, d) in enumerate(rects):
        wn = nm if k == 0 and nm not in COURTS else f"{nm} wing {k + 1}"
        w, d = w - 0.06, d - 0.06                                        # (wings side by side: their walls not in one plane)
        W = lambda u, v: (cx + u * ex - v * ez, cz + u * ez + v * ex)
        # the faces: 0 +z (w long), 1 +x (d), 2 -z (w), 3 -x (d); a face's `at` runs along +x on 0, -z on 1, -x on 2, +z on 3
        geo = {0: (w, lambda t, o: W(t, d / 2 + o)), 1: (d, lambda t, o: W(w / 2 + o, -t)), 2: (w, lambda t, o: W(-t, -d / 2 - o)),
               3: (d, lambda t, o: W(-w / 2 - o, t))}
        faces, doors = {}, []
        for f, (L, at) in geo.items():
            runs = free_runs(lambda t: blocked(at(t, 0.9)), L)
            clear, prev = [], -L / 2
            for a, b in runs:
                if a - prev > 0.4: clear.append([r4(prev), r4(a)])
                prev = b
            if L / 2 - prev > 0.4: clear.append([r4(prev), r4(L / 2)])
            faces[f] = clear
        # the doors: on the longest faces, where the way out is open (a probe 3 m out), nearest the middle
        for f in sorted(geo, key=lambda f: -geo[f][0]):                  # (a big wing has two, on different faces)
            L, at = geo[f]
            runs = [(a + 1.4, b - 1.4) for a, b in free_runs(lambda t: blocked(at(t, 0.9)) or blocked(at(t, 3.0), True), L) if b - a >= 3.6]
            if not runs: continue
            doors.append((f, min((max(a, min(b, 0.0)) for a, b in runs), key=abs)))
            if len(doors) >= (2 if w * d > 500 else 1): break
        dmap = {f: [DOOR(t)] for f, t in doors}
        tiers = {str(f): [{**({"h": r4(sh)} if j < len(sts) - 1 else {}),
                           "openings": {**window_row(sh, faces[f], j), **({"with": dmap[f]} if j == 0 and f in dmap else {})}}
                          for j, sh in enumerate(sts)] for f in geo}
        add(wn, {"type": "enclosure", "plan": {"rect": [r4(w), r4(d)]}, "thickness": 0.6, "height": r4(H), "glass": True, "faces": tiers,
                 "interior": True, "courses": {"plinth": False}, "at": [P(cx, 0.05, cz, yaw)], **({"_about": about} if first else {})})
        first = False
        GEN.append(wn)
        if thai:
            add(f"{wn} thai roof", comp("thai-roof", roof(d + 0.4, w + 0.4, pitch=40, lots=1), [P(cx, 0.05 + H, cz, yaw + Q)]))
        else:
            add(f"{wn} roof", {"type": "roof", "form": "hip", "width": r4(w + 0.2), "length": r4(d + 0.2), "pitch": 38 if middle else 28,
                               "overhang": 0.7, "at": [P(cx, 0.05 + H, cz, yaw)]})
            (MIDDLE_ROOFS if middle else GEN).append(f"{wn} roof")

for n, d in parts.items():          # (the European blocks' doors open: the block glazes every opening)
    if d.get("type") == "enclosure" and isinstance(d.get("faces"), dict) and d.get("glass"):
        for tiers in d["faces"].values():
            for t in (tiers if isinstance(tiers, list) else [tiers]):
                for o in (t.get("openings") if isinstance(t.get("openings"), list) else []):
                    if o.get("sill", 1) == 0: o["glass"] = False
for n, d in parts.items():          # (the merlons 2.6 m apart, not 1.8, on the long runs: thousands of them)
    if d.get("use") == "components/thai-wall": d["params"]["ms"] = 2.6

doc = {"name": "Grand Palace",
       "_about": "THE GRAND PALACE, BANGKOK (from 1782) and WAT PHRA KAEW: the white crenellated palace wall with its forts and spired gates; the temple's "
                 "cloister of the Ramakien murals with its gates and twelve yakshas; the ubosot of the Emerald Buddha on its marble terrace, the twelve "
                 "salas and the bell tower; the upper terrace with the gilt Phra Si Rattana Chedi, the Phra Mondop, the Prasat Phra Thep Bidon and the "
                 "model of Angkor Wat; the eight prangs; the Middle Court's throne halls -- the Phra Maha Monthien (Amarin Winitchai, Phaisan Thaksin, "
                 "Chakraphat Phiman), the Chakri Maha Prasat (a European body under three spired Thai roofs), the Dusit Maha Prasat and the Aphorn "
                 "Phimok; the Boromphiman; the Outer Court's offices and lawns. Plan from OpenStreetMap and the Commons plans, the Inner Court not built "
                 "(tools/archgen/grand_palace.py).",
       "params": {"detail": 4}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/grand-palace.json"), "w").write(json.dumps(doc, indent=1) + "\n")

# =====================================================================================================================
# THE FINISH
# (a part nested in a component is named by its full path, its last name or its component's: the Thai roofs' pieces, the
#  spires' and prangs' parts are listed by their last names, read from the components)
def comp_build(n): return json.load(open(os.path.join(ROOT, f"assets/architecture/components/{n}.json")))["build"]
ROOF_PIECES, EAVES = [], []
for pre in ("roof", "roof lower", "roof single", "roof across"):
    for v in (1, 2, 3):
        for k in range(v):
            nm = f"{pre} {v}" + ("" if k == 0 else f" end {k}")
            ROOF_PIECES.append(nm); EAVES.append(nm + " eaves")
SPIRE_PARTS, PRANG_PARTS = comp_build("thai-spire"), comp_build("prang")
GALLERIES = [f"gallery {k + 1}" for k in range(len(gs))]
SKIN = ["leg right", "leg left", "foot right", "foot left", "upper arm right", "upper arm left", "forearm right", "forearm left", "torso", "head", "ears"]
PRANG_PAL = ["trencadis-white", "trencadis-blue", "trencadis-rose", "trencadis-green", "trencadis-violet", "trencadis-ochre", "trencadis-amanita", "trencadis-rose"]
GATE_PAL = ["trencadis-ochre", "trencadis-green", "trencadis-blue", "trencadis-rose"]
fin = {"name": "Grand Palace", "building": "architecture/grand-palace",
       "_about": "The Grand Palace and Wat Phra Kaew: whitewashed walls, roofs of orange glazed tiles edged in green, every gable, chofa and bai raka "
                 "gilt, the pillars and the ubosot's walls in gold glass mosaic, the chedi in gold, the prangs in coloured porcelain, the Chakri Maha "
                 "Prasat rendered white under its Thai roofs; marble on the terraces and inside, the cloister painted with the Ramakien, the halls "
                 "painted inside; the yakshas each in his colour, gilt costumes; the courts paved, the lawns green.",
       "stone": {"color": "#f1ece0", "accent": "#d8d0bc", "pat": "plaster"},
       "rules": (
           [{"in": f"yaksha {nm}", "parts": SKIN, "color": col, "accent": col,
             **({"_about": "the yakshas' skins, each his own colour"} if i == 0 else {})} for i, (nm, col) in enumerate(YA)]
           + [{"parts": [f"yaksha {nm}" for nm, _ in YA], "pattern": "roofs/gold leaf", "palette": "gold", "_about": "their costumes, crowns and clubs gilt"},
              {"parts": ["emerald buddha"], "color": "#3f8f5f", "accent": "#2a6a45", "_about": "the Emerald Buddha: green jade"},
              {"parts": ["emerald buddha cushion", "altar 1", "altar 2", "altar 3", "altar 4", "altar canopy", "altar canopy posts", "busabok mala base",
                         "busabok mala posts", "busabok mala spire", "phuttan throne", "phuttan umbrella", "phuttan umbrella pole", "chakri throne",
                         "chakri throne umbrella", "dusit throne base", "dusit throne spire", "tripitaka cabinet", "sema shrines caps", "bell"],
               "pattern": "roofs/gold leaf", "palette": "gold", "_about": "the altars, thrones, canopies and umbrellas gilt"},
              {"parts": ["chakri throne dais"], "pattern": "materials/lacquer", "palette": "lacquer-red"},
              {"parts": [f"fort {nm} spire" for nm in FORTS], "pattern": "stone/plaster", "palette": "plaster-white", "_about": "the forts' white pavilions"},
              {"parts": ["angkor model 1", "angkor model 2", "angkor model 3", "angkor model towers", "angkor model tower", "angkor model towers buds", "angkor model tower buds"], "pattern": "stone/ashlar",
               "palette": "sandstone-grey", "_about": "the model of Angkor in grey stone"}]
           + [{"in": f"prang {nm}", "pattern": "tiles/trencadis", "palette": pal,
               **({"_about": "the eight prangs faced in broken porcelain, each of its own colour"} if i == 0 else {})} for i, (nm, pal) in enumerate(zip(PRANG_NAMES, PRANG_PAL))]
           + [{"in": f"gate {n}/prang", "pattern": "tiles/trencadis", "palette": GATE_PAL[i % 4],
               **({"_about": "the cloister gates' prangs in porcelain"} if i == 0 else {})} for i, (_, n, cr) in enumerate(gs) if cr == "prang"]
           + [{"in": "phra thep bidon/prang", "pattern": "tiles/trencadis", "palette": "trencadis-ochre", "_about": "Phra Thep Bidon's prang in coloured porcelain"},
              {"in": "aphorn phimok", "parts": ["pillars", "beams"], "pattern": "painted/gold mosaic", "palette": "gold-mosaic"},
              {"parts": ["phra si rattana chedi", "golden chedis", "phothithat phiman", "mondop spire", "chedi porch 1 roof", "chedi porch 2 roof", "chedi porch 3 roof",
                         "chedi porch 4 roof", "chedi porch 1", "chedi porch 2", "chedi porch 3", "chedi porch 4"], "pattern": "painted/gold mosaic", "palette": "gold",
               "_about": "the Phra Si Rattana Chedi, the golden chedis and the mondop's spire in gold mosaic"},
              {"parts": ["decorated chedis"], "pattern": "tiles/trencadis", "palette": "trencadis-ochre", "_about": "the decorated chedis in porcelain"},
              {"parts": ["mondop", "mondop pillars"], "surface": "wall", "pattern": "tiles/trencadis", "palette": "trencadis-green",
               "_about": "the mondop's walls in green glass mosaic"},
              {"parts": EAVES, "pattern": "roofs/glazed diamonds", "palette": "glazed-green", "_about": "the green tiles along every eave"},
              {"parts": ["na ban"], "pattern": "painted/gold mosaic", "palette": "gold-mosaic", "_about": "the gables' pediments, gilt and set with glass"},
              {"parts": ["bai raka", "chofa"], "pattern": "roofs/gold leaf", "palette": "gold", "_about": "the bai raka and the chofa gilt"},
              {"parts": SPIRE_PARTS + PRANG_PARTS, "pattern": "roofs/gold leaf", "palette": "gold", "_about": "every spire gilt"},
              {"parts": [n for n in GEN if n.endswith(" roof") or "/roof " in n] + ["boromphiman mansard", "boromphiman wing mansard", "boromphiman front mansard"],
               "pattern": "roofs/tube tiles", "palette": "tile-red", "_about": "the European buildings' and the offices' roofs"},
              {"parts": MIDDLE_ROOFS, "pattern": "roofs/glazed diamonds", "palette": "thai-orange", "_about": "the Middle Court's lesser halls under glazed tiles"},
              {"parts": ROOF_PIECES, "side": "in", "pattern": "painted/starry vault", "palette": "thai-ceiling",
               "_about": "the ceilings under the roofs red, strewn with gold stars"},
              {"parts": GALLERIES, "surface": "ceiling", "pattern": "painted/starry vault", "palette": "thai-ceiling"},
              {"parts": ROOF_PIECES, "pattern": "roofs/glazed diamonds", "palette": "thai-orange", "_about": "the roofs of orange glazed tiles"},
              {"parts": GALLERIES, "surface": "roof", "pattern": "roofs/glazed diamonds", "palette": "thai-orange", "_about": "the cloister's roofs"},
              {"parts": ["pillars", "pillars ends", "capitals", "capitals ends", "mondop pillars"], "pattern": "painted/gold mosaic", "palette": "gold-mosaic",
               "_about": "the pillars in glass mosaic"},
              {"parts": GALLERIES, "surface": "wall", "side": "in", "pattern": "painted/cloud scroll", "palette": "thai-mural", "scale": 1.6,
               "_about": "THE RAMAKIEN MURALS along the galleries"},
              {"parts": ["walls", "walls three"], "surface": "wall", "side": "in", "pattern": "painted/cloud scroll", "palette": "thai-mural", "scale": 1.6,
               "_about": "the halls painted inside"},
              {"in": "ubosot", "parts": ["walls three"], "surface": "wall", "pattern": "painted/gold mosaic", "palette": "gold-mosaic",
               "_about": "the ubosot's walls outside in gilt and glass"},
              {"parts": ["platform", "ubosot terrace", "upper terrace", "mondop base", "bell tower base", "chakri base"], "surface": "floor",
               "pattern": "floors/checker", "palette": "marble-grey", "_about": "marble on the terraces and platforms"},
              {"parts": ["platform", "ubosot terrace", "upper terrace", "mondop base", "bell tower base", "sema shrines", "chakri base"], "pattern": "stone/marble",
               "palette": "carrara", "_about": "and their faces"},
              {"parts": [f"lawn {i + 1}" for i in range(len(LAWNS))], "pattern": "materials/grass", "palette": "lawn", "_about": "the lawns"},
              {"parts": ["paving"], "pattern": "floors/flagstones", "palette": "marble-grey", "_about": "the courts paved in pale stone"},
              {"surface": "floor", "side": "in", "pattern": "floors/checker", "palette": "marble-bw", "_about": "marble floors inside"},
              {"surface": "floor", "pattern": "floors/flagstones", "palette": "marble-grey"},
              {"surface": "wall", "pattern": "stone/plaster", "palette": "plaster-white", "_about": "everything else whitewashed"}])}
open(os.path.join(ROOT, "assets/finishes/grand-palace.json"), "w").write(json.dumps(fin, indent=1) + "\n")

THAI_COMPS = ["ubosot", "salas", "west halls", "khanthararat", "hor phra nak", "hor monthien tham", "amarin winitchai", "amarin porch", "chakraphat phiman",
              "dusidaphirom", "racharuedee", "ho sastrakhom", "ho suralai phiman", "ho phra that monthian", "phiman rattaya", "rachakaranya sapha",
              "phra buddha rattanasathan", "sitalaphirom", "wihan yot", "phaisan thaksin", "dusit maha prasat", "aphorn phimok", "mahisorn prasat",
              "phra thep bidon"]

CLOSED = [n for n in THAI_COMPS if n not in ("salas", "amarin porch", "sitalaphirom", "aphorn phimok")]
DOORS = {"name": "Grand Palace: doors", "building": "grand-palace",
         "_about": "The Grand Palace: the ubosot's doors inlaid with mother-of-pearl on black lacquer, the halls' and throne halls' red-lacquered and gilt",
         "doors": [{"_about": "the ubosot's three doors at each end, mother-of-pearl on black lacquer", "part": "ubosot/walls three", "style": "chinese-hall",
                    "color": "#1e1a18"},
                   {"_about": "the halls' and throne halls' doors, red lacquer and gold", "part": [f"{n}/walls" for n in CLOSED if n != "ubosot"],
                    "style": "chinese-hall", "color": "#8c1f18"}]}
open(os.path.join(ROOT, "assets/doors/grand-palace.json"), "w").write(json.dumps(DOORS, indent=1) + "\n")

if __name__ == "__main__":
    write_components()
    print("grand-palace:", len(parts), "parts")
