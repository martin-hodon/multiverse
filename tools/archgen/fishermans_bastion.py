# THE FISHERMAN'S BASTION (Halászbástya), Budapest (Frigyes Schulek, 1895-1902): a neo-Romanesque lookout along the
# edge of Castle Hill, east of the Matthias Church, in white limestone -- laid out here on its real plan (OpenStreetMap,
# the relation "Halászbástya", in metres east and north of the middle of its front) and built of `range`s: corridors one
# bay deep that follow the old city wall's folds, arcaded toward the Danube, open toward the square, and walked on top
# behind battlements.
#   THE HILL: Holy Trinity Square and the church's precinct are a platform `HS` above the foot of the wall, its side the
#     wall itself, faintly battered.
#   THE NORTH GROUP: a corridor along the wall north (about 45 m) to the MAIN TOWER, a great round foot under a terrace
#     round its tower, and from it a corridor west to the north-west tip tower.
#   THE MIDDLE: in front of the church's sanctuary only a parapet along the hill's edge, folding round a re-entrant --
#     and against it from the east the SCHULEK STAIR in three stages: two flights from the road to a lower terrace, one
#     broad flight west from it to a landing against the wall, and from that landing two arms along the wall, north and
#     south, up to the square.
#   THE SOUTH GROUP: a corridor round three sides of a court -- north, east (to the round tower on the salient) and
#     south-west -- where St Stephen stands in the middle on Strobl's pedestal.
# SEVEN towers with conical caps (`domed-tower`, cap "trigonal") stand on the walks: the main tower, the two end towers,
# and four on the outer side of the walks, each a round foot carried up from the ground and a tower on it at the walk's
# level, its door onto the walk. The walks are reached by a flight from the square at each group.
#   THE MATTHIAS CHURCH (Church of Our Lady, rebuilt by Schulek 1874-1896) on the hill behind, on its real plan along
#     its own axis (21.3 degrees north of east): a Gothic hall (`basilica`, hall) of seven bays and a five-sided apse
#     toward the bastion, chapels between the buttresses north and south, the west front with its portal and window,
#     the MATTHIAS TOWER at the south-west (square stages, the octagon and the spire, after the Gothic tower components)
#     and the low BELA TOWER at the north-west; the roof in Zsolnay's glazed diamonds (the finish).
#   THE HOLY TRINITY COLUMN (1713) in the square west of the church: steps, pedestal, shaft and clouds, the Trinity gilt
#     on top and three saints round the pedestal (statue markers).
#   x east, z south (OSM north is -z). Numbers are worked here and written as numbers.
import os, json, math
from statuary import statue
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
r4 = lambda v: round(v, 4)
P = lambda E, N: (E, -N)                               # OSM metres (east, north) -> (x, z)
xz = lambda pts: [[r4(x), r4(z)] for x, z in pts]

# ---- plane geometry: lines walked with the outside on the right
def unit(v): l = math.hypot(*v); return (v[0] / l, v[1] / l)
def right(e): return (-e[1], e[0])                       # (x east, z south: walking north, the right is east)
def segs(line): return [(a, b, math.hypot(b[0] - a[0], b[1] - a[1]), unit((b[0] - a[0], b[1] - a[1]))) for a, b in zip(line, line[1:])]
dot = lambda a, b: a[0] * b[0] + a[1] * b[1]
sub = lambda a, b: (a[0] - b[0], a[1] - b[1])
def offset(line, ds):
    """the line moved d to its right (one d per segment), mitred at the folds -- range.js bandPoints' own arithmetic"""
    S = segs(line); ds = ds if isinstance(ds, list) else [ds] * len(S); out = []
    for i, v in enumerate(line):
        a = S[i - 1] if i > 0 else None; b = S[i] if i < len(S) else None
        if not a or not b:
            g, d = (a, ds[i - 1]) if a else (b, ds[i]); r = right(g[3]); out.append((v[0] + r[0] * d, v[1] + r[1] * d)); continue
        ra, rb = right(a[3]), right(b[3])
        pa = (v[0] + ra[0] * ds[i - 1], v[1] + ra[1] * ds[i - 1]); pb = (v[0] + rb[0] * ds[i], v[1] + rb[1] * ds[i])
        ea, eb = a[3], b[3]; cr = ea[0] * eb[1] - ea[1] * eb[0]
        if abs(cr) < 1e-9: out.append(((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2)); continue
        t = ((pb[0] - pa[0]) * eb[1] - (pb[1] - pa[1]) * eb[0]) / cr
        out.append((pa[0] + ea[0] * t, pa[1] + ea[1] * t))
    return out
def along(line, s):
    """the point s metres along a line, its direction, its segment"""
    for i, (a, b, L, e) in enumerate(segs(line)):
        if s <= L + 1e-9 or i == len(line) - 2: return (a[0] + e[0] * s, a[1] + e[1] * s), e, i
        s -= L
def length(line): return sum(L for _, _, L, _ in segs(line))
def stations(line): return [sum(L for _, _, L, _ in segs(line)[:i]) for i in range(len(line))]   # (each point's s)
def cut(line, s0, s1):
    """the stretch of a line from s0 to s1 metres along it"""
    out = [along(line, s0)[0]]
    for s, q in zip(stations(line), line):
        if s0 + 1e-6 < s < s1 - 1e-6: out.append(q)
    return out + [along(line, s1)[0]]
def inside(p, poly):
    c = False
    for (x0, z0), (x1, z1) in zip(poly, poly[1:] + poly[:1]):
        if (z0 > p[1]) != (z1 > p[1]) and p[0] < x0 + (p[1] - z0) * (x1 - x0) / (z1 - z0): c = not c
    return c
yawOf = lambda d: math.atan2(-d[1], d[0])               # a flight's yaw to climb along d (its local +x); it spreads to the climber's left
def flight_at(top, d, L, W):
    """a flight's placement: its last riser's middle at `top`, climbing along d, L long and W wide"""
    r = right(d)
    return [r4(top[0] - d[0] * L + r[0] * W / 2), r4(top[1] - d[1] * L + r[1] * W / 2)]

# ---- the numbers
HS = 12.0                                              # the square above the wall's foot
HC, WT, OV = 5.0, 0.5, 0.25                            # a corridor's walls to the walk; the walk's slab; its overhang
HW = HS + HC + WT                                      # the walks, 17.5
TW = 0.9                                               # the corridors' walls
RISE = 0.16

# THE OUTER LINES: the old city wall's face, each walked with the field (the Danube) on its right
S_OUT = [P(24, -56.5), P(27.1, -51.5), P(48.0, -38.7), P(27.0, -7.2), P(13.5, -9.2)]       # the south group: SW, SE, N of the court
S_W = [6.5, 6.5, 7.0, 4.6]
MID_OUT = [P(13.5, -9.2), P(13.5, -6.2), P(9.8, -5.8), P(8.0, 9.0), P(-3.4, 23.2), P(6.1, 27.3), P(9.6, 29.4)]   # the middle: the hill's edge
N_OUT = [P(9.6, 29.4), P(10.0, 34.0), P(6.1, 79.7)]     # the north wing
N_W = [7.0, 7.0]
MT_C, MT_R = P(-0.2, 85.2), 8.4                         # the main tower's foot
W_OUT = [P(-7.8, 88.0), P(-29.5, 83.0)]                  # the west wing, to the north-west tip
W_W = [6.0]
def path(out, ws): return offset(out, [-w / 2 for w in ws])
def band(out, ws): return out + offset(out, [-w for w in ws])[::-1]

# ---- the hill: the square's platform, its east side the outer lines
hill = S_OUT + MID_OUT[1:] + N_OUT[1:] + W_OUT + [P(-34, 80), P(-104, 62), P(-104, -64), P(16, -64)]   # (west over the church and the column)
add("hill", {"type": "prism", "plan": {"points": xz(hill)}, "height": HS, "batter": {"out": 0.6}, "walked": True, "at": [[0, 0, 0, 0]],
             "_about": "Castle Hill's top -- Holy Trinity Square and the church's precinct -- its side the old city wall, faintly battered"})

# ---- the corridors' openings, and the gaps in their walks' parapets
ARCADE_OUT = {"every": 3.2, "width": 2.2, "end": 1.4, "sill": 0.9, "springing": 3.3, "head": {"profile": "semicircular"}, "surround": {"style": "romanesque", "orders": 1}}
ARCADE_IN = {"every": 3.2, "width": 2.2, "end": 1.4, "sill": 0, "springing": 3.2, "head": {"profile": "semicircular"}, "surround": {"style": "romanesque", "orders": 1}}
def gap_on(out, ws, k, g, width, side="out"):
    """a gap in a walk's parapet at the point g, by segment k: `at` from that segment's middle on the path"""
    pth = path(out, ws); a, b = pth[k], pth[k + 1]; e = unit(sub(b, a))
    return {"seg": k, "side": side, "at": r4(dot(sub(g, a), e) - math.hypot(*sub(b, a)) / 2), "width": r4(width)}
def chords(out, ws, c, R):
    """the gaps a round tower at c of radius R cuts in the outer parapet: every outer segment it crosses"""
    line = offset(out, OV); gs = []
    for k, (a, b, L, e) in enumerate(segs(line)):
        u = dot(sub(c, a), e); d2 = dot(sub(c, a), sub(c, a)) - u * u
        if d2 >= R * R: continue
        h = math.sqrt(R * R - d2); u0, u1 = max(u - h, 0), min(u + h, L)
        if u1 - u0 < 0.3: continue
        m = (u0 + u1) / 2; gs.append(gap_on(out, ws, k, (a[0] + e[0] * m, a[1] + e[1] * m), u1 - u0))
    return gs

# ---- the towers: (name, centre, facing -- toward its door --, foot radius, tower radius, height, drum, cap rise, about)
def outer_tower(out, k, Rf, inset=0.5, s=None):
    """a tower on the outer side at point k of the line (a fold: out along the bisector), or s metres along it; its foot
    `inset` into the wall"""
    S = segs(out)
    if s is None:
        p = out[k]; n = unit(tuple(right(S[k - 1][3])[j] + right(S[k][3])[j] for j in range(2)))
    else: p, e, _ = along(out, s); n = right(e)
    return (p[0] + n[0] * (Rf - inset), p[1] + n[1] * (Rf - inset)), (-n[0], -n[1])
def end_tower(out, ws, last, Rf):
    """a tower on the path's line beyond its first or last end, its foot a metre over the range's end"""
    pth = path(out, ws); a, b = (pth[-2], pth[-1]) if last else (pth[1], pth[0]); e = unit(sub(b, a))
    return (b[0] + e[0] * (Rf - 1.0), b[1] + e[1] * (Rf - 1.0)), (-e[0], -e[1])
sS, sN = stations(S_OUT), stations(N_OUT)
TOWERS = [("tower south-east", *outer_tower(S_OUT, 2, 4.4, inset=4.4), 4.4, 3.6, 7.5, 2.8, 7.0, "the round tower on the salient over the Danube"),
          ("tower east", *outer_tower(S_OUT, 3, 3.6), 3.6, 3.0, 7.0, 2.6, 6.5, "the tower at the court's north-east corner"),
          ("tower court", *outer_tower(S_OUT, 0, 3.2, s=(sS[3] + sS[4]) / 2), 3.2, 2.6, 6.5, 2.4, 6.0, "a tower on the court's north range"),
          ("tower north", *outer_tower(N_OUT, 1, 3.6), 3.6, 3.0, 7.0, 2.6, 6.5, "the tower where the north wing folds"),
          ("tower north-west", *end_tower(W_OUT, W_W, True, 3.6), 3.6, 3.0, 7.5, 2.6, 7.0, "the tower on the north-west tip"),
          ("tower south", *end_tower(S_OUT, S_W, False, 3.6), 3.6, 3.0, 7.5, 2.6, 7.0, "the tower at the south end, over the Jesuit stair")]
gS = [g for t in TOWERS if t[0] in ("tower south-east", "tower east", "tower court") for g in chords(S_OUT, S_W, t[1], t[4] + 0.2)]
gN = [g for t in TOWERS if t[0] == "tower north" for g in chords(N_OUT, N_W, t[1], t[4] + 0.2)]

# THE WALKS' FLIGHTS from the square: the north one square against the north wing's inner face, the south one up to the
# court range's west end (where the ticket gate is)
nE = round((HW - HS) / RISE); RUN = 0.3; LE = nE * RUN; FW = 2.4
pN = path(N_OUT, N_W); eN = unit(sub(pN[2], pN[1])); sF = 12.0
innerN = offset(N_OUT, [-w for w in N_W])                 # the north wing's inner face (its wall's outside, on the square)
q = (innerN[1][0] + eN[0] * sF, innerN[1][1] + eN[1] * sF); d = right(eN)   # (it climbs toward the corridor: the path's right)
top = (q[0] - d[0] * OV, q[1] - d[1] * OV); a0 = flight_at(top, d, LE, FW)
add("walk stair north", {"type": "flight", "width": FW, "run": RUN, "rise": RISE, "base": HS, "top": HW, "landing": 0,
                         "at": [[a0[0], 0, a0[1], r4(yawOf(d))]],
                         "standsOn": ["hill"], "_about": "the flight from the square up onto the north wing's walk, square against its inner face"})
gN.append(gap_on(N_OUT, N_W, 1, q, FW + 0.2, side="in"))
# (the inner face runs against the walk: its middle is the segment's, the flight sF along it from the start -- from the
#  face's middle, walked backwards)
uIn = math.hypot(*sub(innerN[2], innerN[1])) / 2 - sF
inN = dict(ARCADE_IN, clear=[[r4(uIn - FW / 2 - 0.3), r4(uIn + FW / 2 + 0.3)]])

pS = path(S_OUT, S_W); eS = unit(sub(pS[-1], pS[-2])); d = (-eS[0], -eS[1])     # (it climbs east, along the range's last segment backwards)
top = (pS[-1][0] + eS[0] * OV, pS[-1][1] + eS[1] * OV); a0 = flight_at(top, d, LE, FW)
add("walk stair south", {"type": "flight", "width": FW, "run": RUN, "rise": RISE, "base": HS, "top": HW, "landing": 0,
                         "at": [[a0[0], 0, a0[1], r4(yawOf(d))]], "standsOn": ["hill"],
                         "_about": "the flight from the square up to the south group's walk, at the court range's west end"})
gS.append({"seg": 1, "side": "end", "at": 0, "width": FW + 0.2})

# THE SCHULEK STAIR. The landing against the wall round the middle line's fold at (8, 9): WL out from it, 3 m either side
# of the fold along the line; the arms along the line from its ends; the broad flight from the east onto it; the lower
# terrace and its two flights from the road.
sMid = stations(MID_OUT); sV = sMid[3]
WL, WA, WC, YL, YT = 5.5, 2.8, 5.0, 7.2, 2.4             # the landing's depth; an arm's width; the broad flight's; the landing's height; the terrace's
nA = round((HS - YL) / RISE)                             # an arm's steps
sA, sB = sV - 3.0, sV + 3.0
BG = 0.6 * (1 - YL / HS) + 0.02                           # (the arms clear of the hill's batter at their foot)
land = cut(MID_OUT, sA, sB); landOut = offset(land, WL)
add("schulek landing", {"type": "prism", "plan": {"points": xz(land + landOut[::-1])}, "height": YL, "walked": True, "at": [[0, 0, 0, 0]],
                        "_about": "the Schulek stair's landing against the wall, where the broad flight arrives and the two arms set off"})
# the north arm: from the landing's north end along the line to the re-entrant, where it comes up onto the square
eA = along(MID_OUT, sB + 0.1)[1]; p0 = along(MID_OUT, sB)[0]; r = right(eA)
runA = r4((sMid[4] - sB - 0.4) / nA)
add("schulek arm north", {"type": "flight", "width": WA, "run": runA, "rise": RISE, "base": YL, "top": HS, "ground": 0, "landing": 3.0,
                          "at": [[r4(p0[0] + r[0] * (WA + BG)), 0, r4(p0[1] + r[1] * (WA + BG)), r4(yawOf(eA))]],
                          "_about": "the north arm, along the wall from the landing up to the square"})
# the south arm: from the landing's south end back along the line to the hill's corner by the court range
eB = along(MID_OUT, sA - 0.1)[1]; dB = (-eB[0], -eB[1]); p0 = along(MID_OUT, sA)[0]; p0 = (p0[0] + right(eB)[0] * BG, p0[1] + right(eB)[1] * BG)
runB = r4((sA - sMid[2] - 0.2) / nA)
add("schulek arm south", {"type": "flight", "width": WA, "run": runB, "rise": RISE, "base": YL, "top": HS, "ground": 0, "landing": 3.0,
                          "at": [[r4(p0[0]), 0, r4(p0[1]), r4(yawOf(dB))]],
                          "_about": "the south arm, along the wall from the landing up to the square at the court's corner"})
# the broad flight west onto the landing, on its axis
nC = round((YL - YT) / RISE); runC = 0.6; LC = nC * runC
vOut = landOut[1]
topC = (vOut[0] - 0.4, vOut[1])                           # (its last riser a little into the landing)
a0 = flight_at(topC, (-1, 0), LC, WC)
add("schulek flight", {"type": "flight", "width": WC, "run": runC, "rise": RISE, "base": YT, "top": YL, "ground": 0, "landing": 0,
                       "at": [[a0[0], 0, a0[1], r4(yawOf((-1, 0)))]],
                       "_about": "the broad middle flight, west from the lower terrace to the landing"})
# the lower terrace, and the two flights up to it from the road, from the north and from the south
tx0, tz = topC[0] + LC - 0.4, topC[1]
TL, TD = 8.0, 12.0
add("schulek terrace", {"type": "box", "width": TL, "length": TD, "height": YT, "walked": True, "at": [[r4(tx0 + TL / 2), 0, r4(tz), 0]],
                        "_about": "the lower terrace, where the road's two flights arrive and the broad flight sets off"})
nL = round(YT / RISE); runL = 0.6; LL = nL * runL; WLw = 3.5; xc = tx0 + 1.5 + WLw / 2
fl = [flight_at((xc, tz - TD / 2), (0, 1), LL, WLw), flight_at((xc, tz + TD / 2), (0, -1), LL, WLw)]
add("schulek flights lower", {"type": "flight", "width": WLw, "run": runL, "rise": RISE, "base": 0, "top": YT, "landing": 0,
                              "at": [[fl[0][0], 0, fl[0][1], r4(yawOf((0, 1)))], [fl[1][0], 0, fl[1][1], r4(yawOf((0, -1)))]],
                              "_about": "the two flights from the road up to the lower terrace, from the north and from the south"})

# ---- the middle parapet along the hill's edge, open where the arms come up onto the square
MW = 0.6
openings = sorted([(sMid[4] - 0.2, sMid[4] + WA + 1.0), (sMid[1] + 0.3, sMid[2] - 0.3)])
pieces, s = [], 0.0
for a, b in openings:
    if a - s > 0.5: pieces.append((s, a))
    s = b
if length(MID_OUT) - s > 0.5: pieces.append((s, length(MID_OUT)))
for i, (a, b) in enumerate(pieces):
    add(f"parapet middle {i + 1}", {"type": "range", "solid": True, "path": xz(offset(cut(MID_OUT, a, b), -MW / 2)), "width": MW, "height": 1.15,
                                     "at": [[0, HS, 0, 0]], **({"_about": "the parapet along the hill's edge in front of the church's sanctuary"} if i == 0 else {})})

# ---- the corridors
def corridor(name, out, ws, faces, gaps, about):
    add(name, {"type": "range", "path": xz(path(out, ws)), "width": ws, "height": HC, "thickness": TW, "faces": faces,
               "walk": {"t": WT, "over": OV}, "parapet": {"breast": 1.0, "merlon": 0.6, "t": 0.45, "step": 2.0, "crenel": 0.7, "gaps": gaps},
               "at": [[0, HS, 0, 0]], "_about": about})
corridor("south range", S_OUT, S_W, {"out": ARCADE_OUT, "in": ARCADE_IN, "end": []}, gS,
         "the south group: corridors round three sides of St Stephen's court, arcaded toward the river, open to the court, walked on top")
corridor("north wing", N_OUT, N_W, {"out": ARCADE_OUT, "in": ARCADE_IN, "in:1": inN, "end": []}, gN + [{"seg": 1, "side": "end", "at": 0, "width": N_W[1] - 1.2}],
         "the north wing along the wall to the main tower")
corridor("west wing", W_OUT, W_W, {"out": ARCADE_OUT, "in": ARCADE_IN, "end": []},
         [{"seg": 0, "side": "end", "at": 0, "width": W_W[0] - 1.2}, {"seg": 1, "side": "end", "at": 0, "width": FW + 0.2}],
         "the north-west wing from the main tower to the tip tower")

# ---- the main tower: its foot, the terrace on it, its parapet open where the walks come in
add("main tower foot", {"type": "prism", "plan": {"sides": 24, "radius": MT_R}, "height": HW, "walked": True, "at": [[r4(MT_C[0]), 0, r4(MT_C[1]), 0]],
                        "_about": "the main tower's foot: a round mass from the wall's foot to the walks, its top a terrace round the tower"})
bands = [band(N_OUT, N_W), band(W_OUT, W_W)]
ring = {}
for k in range(24):
    t = (k + 1) * 2 * math.pi / 24                       # (planPoints' sides: face k's middle at bearing (k + 1) 2pi/n from +z toward +x)
    mid = (MT_C[0] + MT_R * math.sin(t) * 0.95, MT_C[1] + MT_R * math.cos(t) * 0.95)
    ring[str(k)] = [{"at": 0, "width": 1.2, "sill": 0, "springing": 1.6, "head": {"profile": "flat"}}] if any(inside(mid, bd) for bd in bands) else \
                   [{"at": 0, "width": 0.7, "sill": 1.0, "springing": 1.6, "head": {"profile": "flat"}}]
add("main tower parapet", {"type": "enclosure", "plan": {"sides": 24, "radius": MT_R}, "thickness": 0.45, "height": 1.6, "glass": False, "faces": ring,
                           "at": [[r4(MT_C[0]), HW, r4(MT_C[1]), 0]], "standsOn": ["main tower foot"]})

# ---- the towers: a round foot from the ground to the walk, the tower on it, its door onto the walk
bl = ["tower", "head", "neck", "drum", "cornice", "cap", "finial"]
def tower(name, c, facing, Rf, R, H, drumH, rise, about, sides=8, foot=True):
    w = math.atan2(facing[0], facing[1])                  # (the door's bearing from +z toward +x)
    if foot: add(name + " foot", {"type": "prism", "plan": {"sides": 16, "radius": Rf}, "height": HW, "at": [[r4(c[0]), 0, r4(c[1]), 0]]})
    add(name, comp("components/domed-tower", {"sides": sides, "R": R, "H": H, "t": 0.6, "drumR": r4(R * 0.78), "drumH": drumH, "cap": "trigonal",
                                              "capR": r4(R * 0.92), "capRise": rise, "capRibs": sides, "kok": r4(R * 0.12), "winW": r4(R * 0.2),
                                              "doorH": 2.6, "finial": r4(R * 0.3), "glazed": 0},
                   [[r4(c[0]), HW, r4(c[1]), r4(w - math.pi / sides)]], build=bl, standsOn=[name + " foot"], _about=about))
tower("main tower", MT_C, (-math.sqrt(.5), math.sqrt(.5)), MT_R, 5.0, 12.0, 4.5, 13.0,
      "the main tower, the tallest: an open belvedere on its terrace under a steep tent, its door toward the two walks", foot=False)
for t in TOWERS: tower(*t)

# ---- THE MATTHIAS CHURCH (the Church of Our Lady of Buda, rebuilt by Schulek 1874-96), on its plan (OpenStreetMap, the
# way "Budavári Nagyboldogasszony-templom", turned to the bastion's frame): a Gothic HALL church, nave and aisles under
# one steep roof of glazed Zsolnay tiles, the choir's polygonal apse toward the bastion; side chapels between deep
# buttresses along both flanks; the MATTHIAS TOWER at the south-west corner -- square stages, the open belfry, the
# octagon and the ribbed spire to 80m -- and the lower BELA TOWER at the north-west. Its axis runs 21.3 degrees north of
# east. Laid out in its own frame -- lz west along the axis from the hall's middle, lx south across it -- and turned onto
# the hill (`ch`): the west front faces +lz, the apse is at -lz.
CA = math.radians(21.3); UC = -39.65                     # the axis; the hall's middle, metres along it from the origin
YC = CA - math.pi / 2                                    # the church frame's yaw
def ch(lx, y, lz, yaw=0.0):
    u, v = UC - lz, -lx
    return [r4(u * math.cos(CA) - v * math.sin(CA)), r4(y), r4(-(u * math.sin(CA) + v * math.cos(CA))), r4(yaw + YC)]
BAYS, BAY = 7, 7.1                                       # the straight bays, west front to the apse
NW, AW, T, TA = 9.0, 5.4, 1.1, 1.2                       # the arcade's centre lines apart, pier line to wall, the walls
SPR, PITCH, OV, BW, BD = 15.0, 58, 0.6, 1.4, 4.0          # the springing, the roof, its eave; the buttresses (the chapels between them)
L = BAYS * BAY
OUT = NW / 2 + AW + TA / 2                               # the outer wall's face
CROWN = SPR + (NW / 2 - T / 2) * 1.7321 * 0.9
WALLTOP = CROWN + 0.5 + 0.3
RIDGE = WALLTOP + (OUT + OV) * math.tan(math.radians(PITCH))
add("church", {"type": "basilica", "hall": True, "bays": BAYS, "bayLen": BAY, "naveW": NW, "aisleW": AW, "t": T, "aisleT": TA,
               "apse": 5, "spring": SPR, "aisleDrop": 2.0, "pierR": 0.8, "shaft": 0.25, "pitch": PITCH, "overhang": OV,
               "aisleSill": 10.5, "aisleWin": 2.6, "buttressW": BW, "buttressD": BD, "skipButtress": [[0, 1]], "at": [ch(0, HS, 0)],
               "standsOn": ["hill"],
               "_about": "the Matthias Church as one HALL: piers, arcades and rib vaults over nave, aisles and ambulatory at nearly one height, the tall windows over the chapels, a buttress at every bay and round the apse, one steep roof over all"})
WF = 2.0
add("church west front", {"type": "wall", "width": 2 * OUT, "height": r4(WALLTOP), "thickness": WF, "at": [ch(0, HS, L / 2 + WF)],
                          "tiers": [{"h": 11, "openings": [{"at": 0, "width": 4.2, "sill": 0, "springing": 6.5, "head": {"profile": "pointed", "spread": 1.0}}]},
                                    {"openings": [{"at": 0, "width": 5.0, "sill": 1.5, "springing": r4(WALLTOP - 11 - 3.0 - 5 * 0.8661),
                                                   "head": {"profile": "pointed", "spread": 1.0}, "tracery": True}]}],
                          "_about": "the west front between the towers: the portal, and the great traceried window over it"})
GH = RIDGE - WALLTOP
TP = math.tan(math.radians(PITCH))
add("church west gable", {"type": "prism", "plan": {"rect": [OUT, WF]}, "height": r4(GH - OUT / 2 * TP), "slope": [r4(-TP), 0],
                          "at": [ch(OUT / 2, HS + WALLTOP, L / 2 + WF / 2), ch(-OUT / 2, HS + WALLTOP, L / 2 + WF / 2, math.pi)],
                          "_about": "the west gable over the front, its two halves falling with the roof"})
# the side chapels, one to a bay between the buttresses, under lean-to roofs against the aisle walls: along the north
# flank from the Bela tower to the choir, along the south from beyond the Matthias tower's porch
CW, CHH = BAY - BW - 0.05, 8.5
bayZ = lambda k: L / 2 - (k + 0.5) * BAY
CWIN = [{"at": 0, "width": 1.6, "sill": 2.4, "springing": 5.4, "head": {"profile": "pointed", "spread": 1.0}}]
for side, sx, face, bays in (("north", -1, "3", range(1, 7)), ("south", 1, "1", range(2, 6))):
    add(f"church {side} chapels", {"type": "enclosure", "plan": {"rect": [BD, r4(CW)]}, "thickness": 0.8, "height": CHH, "glass": False,
                                   "openings": [], "faces": {face: CWIN}, "at": [ch(sx * (OUT + BD / 2), HS, bayZ(k)) for k in bays],
                                   "_about": f"the chapels along the {side} flank, between the buttresses"})
    add(f"church {side} chapel roofs", {"type": "roof", "form": "shed", "width": BD, "length": r4(CW), "pitch": 22, "overhang": 0.3,
                                        "at": [ch(sx * (OUT + BD / 2), HS + CHH, bayZ(k), 0 if sx < 0 else math.pi) for k in bays]})
# the MATTHIAS TOWER at the south-west corner: the foot, the open belfry with pinnacles at its corners, the octagon, the spire
MTW = 9.5
mt = (OUT + MTW / 2, L / 2 + WF - MTW / 2)
ms = lambda **kw: {"W": MTW, "t": 1.2, "wins": 1, "winW": 1.8, "bw": 1.3, "bd": 1.1, **kw}
add("matthias tower foot", comp("components/gothic-tower-stage", ms(H=30.0, low=7.0, doorN=1, doorW=2.0), [ch(mt[0], HS, mt[1])],
                                build=["walls door", "slab"], _about="the Matthias tower (`gothic-tower-stage` twice, a `gothic-octagon-stage`, a `gothic-spire`): the foot, its door to the square..."))
add("matthias tower belfry", comp("components/gothic-tower-stage", ms(H=17.0, low=3.0, glazed=0, pinW=1.0, pinH=2.2, pinS=3.6), [ch(mt[0], HS + 30.0, mt[1])],
                                  build=["walls", "corner pinnacles", "slab"], _about="...the open belfry, pinnacles on its corners..."))
add("matthias tower octagon", comp("components/gothic-octagon-stage", {"R": 4.4, "H": 12.0, "t": 0.8, "low": 2.0}, [ch(mt[0], HS + 47.0, mt[1])],
                                   _about="...the octagon..."))
add("matthias tower spire", comp("components/gothic-spire", {"R": 4.0, "rise": 22.0, "finial": 3.0, "pinR": 4.0}, [ch(mt[0], HS + 59.0, mt[1])],
                                 build=["spire", "ribs", "gables", "pinnacles", "finial"], _about="...and the ribbed spire, to 80m over the square"))
# the BELA TOWER at the north-west corner: a plain square foot, a short octagon, a small spire
BTW = 6.4
bt = (-(OUT + BTW / 2), L / 2 + WF - BTW / 2)
add("bela tower foot", comp("components/gothic-tower-stage", {"W": BTW, "H": 24.0, "t": 1.0, "low": 5.0, "wins": 1, "winW": 1.2, "bw": 1.0, "bd": 0.9},
                            [ch(bt[0], HS, bt[1])], build=["walls", "slab"], _about="the Bela tower, the older and lower: its square foot..."))
add("bela tower octagon", comp("components/gothic-octagon-stage", {"R": 2.9, "H": 6.0, "t": 0.6, "low": 1.5}, [ch(bt[0], HS + 24.0, bt[1])]))
add("bela tower spire", comp("components/gothic-spire", {"R": 2.6, "rise": 12.0, "finial": 1.5, "pinR": 2.6}, [ch(bt[0], HS + 30.0, bt[1])],
                             build=["spire", "ribs", "gables", "pinnacles", "finial"], _about="...its octagon and small spire"))

# ---- THE HOLY TRINITY COLUMN in the square west of the church (1710-13): the plague column on its stepped base, a
# triangular pedestal with saints round it, the shaft and its clouds, the Trinity at the top
TC = P(-88.4, -50.5)
add("trinity column steps", {"type": "prism", "plan": {"sides": 6, "radius": 4.2}, "height": 0.6, "walked": True, "at": [[r4(TC[0]), HS, r4(TC[1]), 0]],
                             "standsOn": ["hill"], "_about": "the Holy Trinity Column: its steps..."})
add("trinity column pedestal", {"type": "prism", "plan": {"sides": 3, "radius": 3.0}, "height": 4.0, "at": [[r4(TC[0]), HS + 0.6, r4(TC[1]), 0]],
                                "standsOn": ["trinity column steps"], "_about": "...the triangular pedestal..."})
add("trinity column shaft", {"type": "prism", "plan": {"sides": 12, "radius": 0.75}, "height": 6.5, "at": [[r4(TC[0]), HS + 4.6, r4(TC[1]), 0]],
                             "standsOn": ["trinity column pedestal"], "_about": "...the shaft..."})
add("trinity column clouds", {"type": "prism", "plan": {"sides": 8, "radius": 1.4}, "height": 1.4, "at": [[r4(TC[0]), HS + 11.1, r4(TC[1]), 0]],
                              "standsOn": ["trinity column shaft"], "_about": "...the clouds the Trinity sits on"})
add("trinity", statue((TC[0], HS + 12.5, TC[1]), kind="man", pose="stand", style="gothic", stone="gold", scale=1.2, seed=5, face=1.5707963))
for i in range(3):
    t = math.pi / 3 + i * 2 * math.pi / 3                # (the pedestal's faces: between its corners)
    add(f"trinity saint {i + 1}", statue((TC[0] + 2.3 * math.sin(t), HS + 0.6, TC[1] + 2.3 * math.cos(t)), kind="man", pose="stand", style="gothic",
                                         stone="limestone", scale=1.0, seed=20 + i, face=r4(t)))

# ---- St Stephen in the court, on his pedestal
SC = P(17.0, -34.0)
add("st stephen pedestal", {"type": "box", "width": 3.2, "length": 5.0, "height": 3.6, "at": [[r4(SC[0]), HS, r4(SC[1]), 0]], "standsOn": ["hill"],
                            "_about": "Strobl's St Stephen in the middle of the court, on Schulek's pedestal"})
add("st stephen", statue((SC[0], HS + 3.6, SC[1]), kind="man", pose="stand", style="gothic", stone="bronze", scale=1.5, seed=11, face=1.5707963))

doc = {"name": "Fisherman's Bastion",
       "_about": "THE FISHERMAN'S BASTION (Halászbástya), Budapest (Schulek, 1895-1902), on its real plan: neo-Romanesque corridors along the folds of Castle Hill's old wall -- arcaded toward the Danube, open toward the square, walked on top behind battlements (`range`) -- in a north group (the north wing, the main tower on its great round foot, the wing to the north-west tip) and a south group round St Stephen's court; between them a parapet along the hill's edge before the church's sanctuary, and against it the three-stage Schulek stair; seven towers with steep conical caps (`domed-tower`) on the walks. Behind it on the hill the Matthias Church on its own plan -- a Gothic hall church, its apse toward the bastion, chapels along both sides, the Matthias tower at the south-west and the Béla tower at the north-west, the roof in glazed Zsolnay tiles -- and in the square west of it the Holy Trinity Column. Generated by tools/archgen/fishermans_bastion.py -- edit the script for arithmetic changes. East is +x, south +z.",
       "params": {"detail": 4}, "base": {"height": 0.4, "steps": 2, "stepOut": 0.5, "margin": 4}, "railing": {"type": "balusters"},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/fishermans-bastion.json"), "w").write(json.dumps(doc, indent=2) + "\n")
