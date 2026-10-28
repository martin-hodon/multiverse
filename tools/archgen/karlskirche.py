# KARLSKIRCHE, Vienna (1716-37), from components: the church round in plan (an enclosure of sixteen faces for its
# oval), on it a drum of windows and the tall dome with its lantern; before it a Corinthian PORTICO, a temple front
# of six columns under a pediment; either side of the portico one of the two GIANT COLUMNS (Trajan's column, twice)
# on its pedestal with a lantern on its capital; and the facade running out from the portico on both sides to a
# gate PAVILION at each end, its arch walked through, under a curved roof.
#   The front faces +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2

R, T, BH = 16.0, 1.6, 26.0                 # the church: radius, walls, height
DR, DT, DH = 12.0, 1.0, 9.0                # the drum
# ---- the church, its roof ring, the drum, the dome, the lantern
# (the sixteen faces run from the one just right of the axis, 0, round to the one just left, 14 -- the front's middle
#  face is 15, the diagonal ones the side halls stand against 1 and 13; `at` on a face from its middle)
HALL_DOOR = {"width": 1.4, "sill": 0, "springing": 3.6, "head": {"profile": "semicircular"}}
U_HALL = (1.57, 3.96)                      # where the east hall's end lies along face 1 (from its start): worked below
def church_face(k):
    doors = {"15": {"at": 0, "width": 4.0, "sill": 0, "springing": 8.0, "head": {"profile": "semicircular"}},
             "1": {"at": round((U_HALL[0] + U_HALL[1]) / 2 - R * math.sin(math.pi / 16), 3), **HALL_DOOR},
             "13": {"at": round(R * math.sin(math.pi / 16) - (U_HALL[0] + U_HALL[1]) / 2, 3), **HALL_DOOR}}
    return [{"h": 13, "openings": [doors[k]]}, {"openings": [{"at": 0, "width": 2.2, "sill": 2.0, "springing": 7.5, "head": {"profile": "segmental", "seg": 0.4}}]}]
add("church", {"type": "enclosure", "plan": {"sides": 16, "radius": R}, "thickness": T, "height": BH,
               "tiers": [{"h": 13, "openings": [{"at": 0, "width": 2.4, "sill": 4.0, "springing": 9.0, "head": {"profile": "semicircular"},
                                                 "surround": {"head": "pediment"}}]},
                         {"openings": [{"at": 0, "width": 2.2, "sill": 2.0, "springing": 7.5, "head": {"profile": "segmental", "seg": 0.4}, "surround": {"head": False}}]}],
               "faces": {**{k: church_face(k) for k in ("15", "1", "13")},
                         "7": [{"h": 13, "openings": []}, {"openings": [{"at": 0, "width": 2.2, "sill": 2.0, "springing": 7.5, "head": {"profile": "segmental", "seg": 0.4}}]}]},
               "courses": {"plinth": True, "clear": {"1": [[U_HALL[0] - 0.05, U_HALL[1] + 0.05]], "13": [[2 * R * math.sin(math.pi / 16) - U_HALL[1] - 0.05, 2 * R * math.sin(math.pi / 16) - U_HALL[0] + 0.05]]}},
               "orders": [{"tier": 0, "span": 2, "kind": "corinthian"}],
               "at": [[0, 0, 0, 0]], "interior": True, "_about": "the church, round (the real one is an oval): a giant Corinthian order of pilasters folded round its corners, two tiers of dressed windows between them, the door on the axis behind the portico, and doors into the side halls"})
apo = R * math.cos(math.pi / 16) - T        # its walls' inner face
add("roof ring", {"type": "ring", "count": 16, "rOuter": round(apo / math.cos(math.pi / 16), 4), "rInner": DR, "height": 0.6, "y": BH - 0.6, "turn": 0.5,
                  "solid": True, "place": [[0, 0, 0, 0]], "_about": "the flat roof round the drum, from the church's walls in to it"})
add("dome", comp("components/drum-dome", {"R": DR, "dt": DT, "H": DH, "n": 16, "every": 2, "winW": 2.0, "winSill": 2.0, "winH": 4.4,
                                          "profile": "pointed", "spread": 0.8, "domeT": DT, "lanternR": 2.2, "lanternH": 5.0},
                 [[0, BH, 0, 0]], _about="the drum with eight windows, the dome -- taller than a hemisphere, a steep pointed section -- and its lantern"))

# ---- the portico
PW, PD, CH, PZ = 22.0, 10.0, 13.0, R - 1.0     # portico width, depth, column height, where it meets the church
# (the portico stands between the side halls, whose inner ends are at x +-HX0 back to their fronts at z HZ1: its
#  STEPS only before them -- the stylobate from HZ1 + 1.5 out to the columns' front, its lowest step on HZ1 -- and
#  behind them a FLOOR at the stylobate's height filling the ground between the halls and the church's three front
#  faces; a short flight down through the door into the church, whose floor is the ground's)
PZ0 = PZ + 2.6 + 1.5                             # (the halls' front, HZ1 below, and the steps' spread)
add("portico steps", {"type": "crepidoma", "width": PW, "length": PZ + PD - PZ0, "steps": 4, "stepH": 0.2, "stepOut": 0.5,
                      "at": [[0, 0, (PZ0 + PZ + PD) / 2, 0]], "_about": "the portico's steps, before the halls"})
cn = lambda k: (round(R * math.sin(2 * math.pi * k / 16), 4), round(R * math.cos(2 * math.pi * k / 16), 4))   # the church's corners
zH = round(cn(1.5)[1] + (cn(2.5)[1] - cn(1.5)[1]) * (10.0 - cn(1.5)[0]) / (cn(2.5)[0] - cn(1.5)[0]), 4)          # face 1 crossing x = 10
add("portico floor", {"type": "prism", "walked": True, "height": 0.8, "at": [[0, 0, 0, 0]],
                      "plan": {"points": [[10.0, PZ0], [-10.0, PZ0], [-10.0, zH], [-cn(1.5)[0], cn(1.5)[1]], [-cn(0.5)[0], cn(0.5)[1]],
                                          [cn(0.5)[0], cn(0.5)[1]], [cn(1.5)[0], cn(1.5)[1]], [10.0, zH]]},
                      "_about": "the portico's floor behind its steps, between the halls, up to the church's front faces"})
add("portico entry", {"type": "flight", "width": 3.6, "run": 0.3, "base": 0, "top": 0.8, "steps": 4, "landing": 0.5,
                      "at": [[-1.8, 0, round(R * math.cos(math.pi / 16) - T + 0.02, 4), -Q]],
                      "_about": "four steps down from the portico through the door to the church's floor"})
add("portico columns", {"type": "colonnade", "order": "corinthian", "count": 6, "spacing": 4.0, "columnR": 0.7, "height": CH, "taper": 0.86,
                        "entablature": {"h": 2.2, "depth": 1.8}, "at": [[0, 0.8, PZ + PD - 1.2, 0]],
                        "_about": "six Corinthian columns and their entablature: a Greek temple's front"})
add("portico side columns", {"type": "colonnade", "order": "corinthian", "count": 2, "spacing": 4.0, "columnR": 0.7, "height": CH, "taper": 0.86,
                             "entablature": {"h": 2.2, "depth": 1.8}, "at": [[sx * 9.0, 0.8, PZ + PD / 2 - 1.2, Q] for sx in (-1, 1)],
                             "_about": "the portico's sides, inside its floor (at +-10 they stood in the halls' end walls)"})
# (the pediment's roof runs back only to the church's front face -- further, it came through the wall into the nave)
PF0 = round(R * math.cos(math.pi / 16), 4)
add("pediment", {"type": "roof", "form": "gable", "width": PW, "length": PZ + PD - PF0, "pitch": 20, "overhang": 0.4,
                 "at": [[0, 0.8 + CH + 2.2, (PF0 + PZ + PD) / 2, 0]], "_about": "the pediment over it"})

# ---- the giant columns
for sx, nm in ((-1, "west"), (1, "east")):
    X, Z = sx * 20.0, PZ + PD - 2.0
    add(f"{nm} column pedestal", {"type": "box", "width": 6.0, "length": 6.0, "height": 6.0, "at": [[X, 0, Z, 0]],
                                   **({"_about": "the two giant columns, each on its pedestal: a shaft wound with reliefs (a spiral band), a capital, a lantern with an eagle's cage of a cap"} if sx < 0 else {})})
    add(f"{nm} column", {"type": "column", "radius": 2.0, "height": 30.0, "sides": 16, "taper": 0.92, "at": [[X, 6.0, Z, 0]]})
    # (a CONTINUOUS band: 9 turns of 1.2m tall slabs overlapping along it, 20cm proud of the shaft as it tapers -- the
    #  160 short blocks it had been, 4.5m apart up the shaft, read as a stair wound round it)
    add(f"{nm} column band", {"type": "box", "width": 0.4, "length": 0.75, "height": 1.2,
                              "spiral": {"count": 504, "turns": 9, "radius": 2.0, "x": X, "z": Z, "y": 7.2, "dy": 27.0 / 504, "dr": -0.15 / 504},
                              "_about": "the relief band wound round the shaft"})
    add(f"{nm} column capital", {"type": "box", "width": 5.0, "length": 5.0, "height": 1.2, "at": [[X, 36.0, Z, 0]]})
    add(f"{nm} column lantern", comp("components/domed-tower", {"sides": 8, "R": 1.7, "H": 3.0, "t": 0.3, "drumR": 1.1, "drumH": 0.8, "cap": "bell",
                                                                "capR": 1.4, "waist": 0.75, "lift": 1.0, "kok": 0.2, "finial": 1.5, "doorH": 1.0},
                                     [[X, 37.2, Z, 0]], build=["tower", "cap", "finial"]))

# ---- the side wings: hallways from the church out to the gate pavilions
# Each is a building of its own, a storey of halls: its inner end is set into the church's wall (a door through the
# church's diagonal face opens into it), its outer end opens into the pavilion by an arch the pavilion's own size.
HZ0, HZ1, HH = 10.5, PZ + 2.6, 16.0          # the wings' depth (clear of the church's inside at their inner end) and height: their
                                              # entablature the portico's (its top 0.8 + 13 + 2.2)
HX0 = PW / 2 - 1.0                            # beside the portico
PV, PX = 9.0, 38.0                            # the pavilions
HX1 = PX - PV / 2
hz = (HZ0 + HZ1) / 2
# THE HALL'S PLAN: a pentagon -- its inner end follows the church: up from its back to where it meets the church's
# diagonal face 1, along that face (the two walls' faces in one plane, a door through both), and on to the portico's
# side -- so its rooms reach the church's door (face 1: between the corners 1.5 and 2.5 sixteenths of a turn round)
F0 = (R * math.sin(2 * math.pi * 1.5 / 16), R * math.cos(2 * math.pi * 1.5 / 16))
F1 = (R * math.sin(2 * math.pi * 2.5 / 16), R * math.cos(2 * math.pi * 2.5 / 16))
fe = ((F1[0] - F0[0]) / math.dist(F0, F1), (F1[1] - F0[1]) / math.dist(F0, F1))
on_face = lambda u: (F0[0] + fe[0] * u, F0[1] + fe[1] * u)
uz = (F0[1] - HZ0) / -fe[1]                   # where the face crosses the hall's back line, and its end line
ux = (HX0 - F0[0]) / fe[0]
assert abs(ux - U_HALL[0]) < 0.02 and abs(uz - U_HALL[1]) < 0.02, (ux, uz)
HT = 0.6
hall_pts = [on_face(uz), (HX1, HZ0), (HX1, HZ1), (HX0, HZ1), on_face(ux)]      # (east: from the back's foot on the church, round)
wing_win = lambda blank=False: [{"h": 8.4, "openings": []} if blank else {"h": 8.4, "openings": {"pattern": "4", "width": 2.0, "gap": 3.2, "sill": 1.2, "springing": 5.4, "head": {"profile": "semicircular"}, "surround": {"head": "cornice"}}},
                    {"openings": {"pattern": "4", "width": 2.0, "gap": 3.2, "sill": 1.6, "springing": 4.4, "head": {"profile": "segmental", "seg": 0.4}, "surround": {"head": False}}}]
passage = [{"at": 0, "width": 4.2, "sill": 0, "springing": 6.0, "head": {"profile": "semicircular"}}]
# THE BELFRY STAIR: in each hall a flight up its back wall to the pavilion's floor (9m), a door at its head through
# the hall's end and the pavilion's face (back to back) -- a hand's breadth along from the back wall's inside
ST_W, ST_N, ST_RUN, BELFRY = 1.2, 50, 0.28, 9.0
ST_X1 = PX - PV / 2 - HT                      # the hall's end wall's inside: the landing's far edge
ST_X0 = ST_X1 - ST_N * ST_RUN - ST_W
STAIR_Z = HZ0 + HT + ST_W / 2                 # the flight's (and the door's) middle
STAIR_DOOR = hz - STAIR_Z                     # the door, from the end face's middle (the east hall's runs -z, the west's +z)
BELFRY_DOOR = {"width": 1.2, "springing": 2.3, "head": {"profile": "semicircular"}, "glass": False}
def inset(pts, d):
    # (a convex plan drawn in by `d` on every side: each edge moved in toward the middle, and the corners where the
    #  moved edges meet; `d` a list: each edge by its own, out where it is less than 0)
    n, cx, cz = len(pts), sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    lines = []
    for i in range(n):
        d_ = d[i] if isinstance(d, list) else d
        (x0, z0), (x1, z1) = pts[i], pts[(i + 1) % n]
        L = math.hypot(x1 - x0, z1 - z0); nx, nz = -(z1 - z0) / L, (x1 - x0) / L
        if nx * (cx - x0) + nz * (cz - z0) < 0: nx, nz = -nx, -nz
        lines.append(((x0 + nx * d_, z0 + nz * d_), (x1 - x0, z1 - z0)))
    out = []
    for i in range(n):
        (p, u), (q, v) = lines[i - 1], lines[i]
        t = ((q[0] - p[0]) * v[1] - (q[1] - p[1]) * v[0]) / (u[0] * v[1] - u[1] * v[0])
        out.append([round(p[0] + u[0] * t, 4), round(p[1] + u[1] * t, 4)])
    return out
for sx, nm in ((-1, "west"), (1, "east")):
    pts = [(round(sx * x, 4), round(z, 4)) for x, z in hall_pts]
    # (walked so the outside is on the left of every face -- planPoints' way, so the faces keep the numbers given here)
    area = sum(pts[i][0] * pts[(i + 1) % 5][1] - pts[(i + 1) % 5][0] * pts[i][1] for i in range(5))
    turned = area > 0
    if turned: pts = [pts[0]] + pts[1:][::-1]
    # face i runs pts[i] -> pts[i+1]: 0 back, 1 outer end, 2 front, 3 inner end, 4 the church's -- or, walked the other way, the reverse
    F = {"church": "0", "inner": "1", "front": "2", "outer": "3", "back": "4"} if turned else {"back": "0", "outer": "1", "front": "2", "inner": "3", "church": "4"}
    add(f"{nm} hall", {"type": "enclosure", "plan": {"points": [list(p) for p in pts]}, "thickness": HT, "height": HH,
                       "faces": {F["back"]: wing_win(blank=True), F["front"]: wing_win(), F["outer"]: [{"h": 8.4, "openings": passage}, {"openings": [{"at": round(sx * STAIR_DOOR, 3), **BELFRY_DOOR, "sill": 9.0 - 8.4}]}],
                                 F["inner"]: [{"h": 8.4, "openings": []}, {"openings": []}], F["church"]: [{"h": 8.4, "openings": [{"at": 0, **HALL_DOOR}]}, {"openings": []}]},
                       "courses": {"plinth": True, "skip": [F["church"], F["outer"]]}, "orders": [{"tier": 0, "span": 2, "kind": "corinthian"}],
                       "at": [[0, 0, 0, 0]],
                       **({"_about": "the side wings: halls from the church to the gate pavilions -- their inner end following the church's diagonal face, a door through both walls there, an arch into the pavilion at the outer end -- a giant Corinthian order carrying the portico's entablature on out to the pavilions"} if sx < 0 else {})})
    # (THE HALL'S SPACE: on its walls' middle, but at the church's end on the church's wall's middle -- the two walls
    #  stand back to back there, the door through both a passage from the one space into the other)
    add(f"{nm} hall space", {"type": "interior", "plan": {"points": inset(pts, [-T / 2 if F["church"] == str(i) else HT / 2 for i in range(5)])},
                             "height": HH, "at": [[0, 0, 0, 0]],
                             **({"_about": "the halls inside, up to their roofs"} if sx < 0 else {})})
    add(f"{nm} hall ceiling", {"type": "prism", "plan": {"points": inset(pts, HT)}, "height": 0.4, "flatRoof": True, "at": [[0, HH - 0.4, 0, 0]],
                               **({"_about": "the halls' flat ceilings under their roofs, wall to wall"} if sx < 0 else {})})
    add(f"{nm} hall roof", {"type": "roof", "form": "hip", "width": HZ1 - HZ0, "length": HX1 - HX0, "pitch": 24, "overhang": 0.3,
                            "at": [[sx * (HX0 + HX1) / 2, HH, hz, Q]]})
    # (the pavilion's face the hall stands against: courses and pilasters stop at the hall's sides)
    cl = [[round(hz + PV / 2 - HZ1 - 0.05, 3), round(hz + PV / 2 - HZ0 + 0.05, 3)]]
    add(f"{nm} pavilion", {"type": "enclosure", "plan": {"rect": [PV, PV]}, "thickness": 1.4, "height": 20.0, "glass": False,
                           "tiers": [{"h": 9.0, "openings": passage}, {"openings": [{"at": 0, "width": 2.0, "sill": 3.0, "springing": 7.5, "head": {"profile": "semicircular"},
                                                                                     "surround": {"head": "pediment"}}]}],
                           "faces": {("3" if sx > 0 else "1"): [{"h": 9.0, "openings": passage},
                                                                {"openings": [{"at": 0, "width": 2.0, "sill": 3.0, "springing": 7.5, "head": {"profile": "semicircular"}, "surround": {"head": "pediment"}},
                                                                              {"at": round(-sx * STAIR_DOOR, 3), **BELFRY_DOOR, "sill": 0}]}]},
                           "courses": {"plinth": True, "clear": {("3" if sx > 0 else "1"): cl}},
                           "orders": [{"tier": 0, "kind": "doric"}, {"tier": 1, "kind": "ionic"}],
                           "at": [[sx * PX, 0, hz, 0]],
                           **({"_about": "a gate pavilion at each end of the front, an arch through it every way, its belfry over: a Doric order round the arches, an Ionic one over it"} if sx < 0 else {})})
    add(f"{nm} pavilion floor", {"type": "box", "width": PV - 2.8, "length": PV - 2.8, "height": 0.4, "at": [[sx * PX, 9.0 - 0.4, hz, 0]],
                                 **({"_about": "the belfry floor over the passage, reached by the hall's stair"} if sx < 0 else {})})
    add(f"{nm} belfry stair", {"type": "flight", "width": ST_W, "run": ST_RUN, "base": 0, "top": BELFRY, "steps": ST_N, "landing": ST_W,
                               "at": [[round(sx * ST_X0, 4), 0, round(STAIR_Z + ST_W / 2 if sx > 0 else STAIR_Z - ST_W / 2, 4), 0 if sx > 0 else math.pi]],
                               **({"_about": "up the hall's back wall to the pavilion's belfry floor, its landing at the door"} if sx < 0 else {})})
    add(f"{nm} pavilion belfry", {"type": "interior", "plan": {"rect": [PV - 1.4, PV - 1.4]}, "height": 20.0 - (9.0 - 0.4),
                                  "at": [[sx * PX, 9.0 - 0.4, hz, 0]],
                                  **({"_about": "the belfry over the passage, from under its floor to its ceiling's top (the passage under it, open every way, is the street's)"} if sx < 0 else {})})
    add(f"{nm} pavilion ceiling", {"type": "box", "width": PV - 2.8, "length": PV - 2.8, "height": 0.4, "at": [[sx * PX, 20.0 - 0.4, hz, 0]]})
    add(f"{nm} pavilion roof", {"type": "dome", "sides": 4, "radius": PV / 2 * 1.4142, "thickness": 0, "head": {"profile": "bell", "waist": 0.7, "lift": 0.6},
                                "at": [[sx * PX, 20.0, hz, 0]]})

# ---- THE INTERIOR'S ARCHITECTURE: a cornice round the round at the tiers' joint and under the roof ring, a pilaster
# in every corner, four side altars on the cross axis and the diagonals behind it, and the high altar's retable -- a
# gilt glory up the blind back face (the nave had been a bare pink cylinder)
rIn = round(apo / math.cos(math.pi / 16), 4)    # the inner faces' corner radius
add("interior cornice", {"type": "ring", "count": 16, "polygon": True, "rOuter": round(rIn + 0.05, 4), "rInner": round(rIn - 0.55, 4), "height": 0.5, "y": 12.7,
                         "turn": 0.5, "solid": True, "place": [[0, 0, 0, 0], [0, 11.8, 0, 0]],
                         "_about": "the cornices round the inside, over the lower windows and under the roof ring"})
pil = []
for k in range(16):
    a = 2 * math.pi * (k + 0.5) / 16                # the inner corners (faces' middles on the axes and the diagonals)
    for y0 in (0, 13.2):
        pil.append([round((rIn - 0.2) * math.sin(a), 4), y0, round((rIn - 0.2) * math.cos(a), 4), round(a, 6)])
add("interior pilasters", {"type": "box", "width": 1.1, "length": 0.5, "height": 11.3, "at": pil,
                           "_about": "a pilaster in each corner inside, under each cornice"})
sa, ss, sr = [], [], []
for k in (3, 5, 9, 11):                         # the side faces (90, 135, 225, 270 degrees round from the door)
    a = 2 * math.pi * (k + 1) / 16
    at = lambda r, y: [round(r * math.sin(a), 4), y, round(r * math.cos(a), 4), round(a, 6)]
    ss.append(at(apo - 1.1, 0)); sa.append(at(apo - 0.85, 0.15)); sr.append(at(apo - 0.2, 0.15))
add("side altar steps", {"type": "box", "width": 3.6, "length": 2.2, "height": 0.15, "at": ss, "walked": True})
add("side altars", {"type": "box", "width": 2.4, "length": 1.0, "height": 1.05, "at": sa})
add("side altar retables", {"type": "box", "width": 3.0, "length": 0.4, "height": 3.7, "at": sr,
                            "_about": "four side altars, each on a step before a marble retable under its window"})
add("high altar retable", {"type": "box", "width": 4.5, "length": 0.4, "height": 12.7, "at": [[0, 0, -(apo - 0.2), 0]],
                           "_about": "the high altar's retable, a gilt glory up the blind back face to the cornice"})
# ---- THE BELFRIES: a bell in each, hung in a timber frame over the floor the stair arrives on
# (the frame across the hall, its posts north and south of the bell: through the side arches the bell hangs between them)
add("belfry frames", {"type": "box", "width": 0.3, "length": 0.3, "height": 7.0,
                      "at": [[sx * PX, 9.0, hz + dz, 0] for sx in (-1, 1) for dz in (-1.6, 1.6)],
                      "_about": "the bell frames' posts, standing on the belfry floors"})
add("belfry beams", {"type": "box", "width": 0.4, "length": 3.6, "height": 0.4, "at": [[sx * PX, 16.0, hz, 0] for sx in (-1, 1)]})
add("belfry bells", {"type": "dome", "sides": 16, "radius": 0.85, "thickness": 0.08, "cap": False, "head": {"profile": "bell", "waist": 0.6, "lift": 0.5},
                     "at": [[sx * PX, 16.0 - 0.94, hz, 0] for sx in (-1, 1)], "_about": "a bell under each beam, its crown (0.94m up its profile) on it"})
# ---- the high altar against the back of the round, facing the door; the pews before it
add("altar", {"type": "zone", "zone": "altar", "w": 6.0, "d": 3.0, "h": 8.0, "at": [[0, 0, -(apo - 2.0), -Q]],
              "_about": "the high altar at the back of the church, opposite the door"})
add("seating", {"type": "zone", "zone": "seating", "w": 12.0, "d": 11.0, "h": 8.0, "at": [[0, 0, 2.5, Q]],
                "_about": "the pews down the middle of the round, facing the altar"})

# ---- the statues (statuary.py): on the pediment, the figure crowning its apex and an angel at each of its lower corners;
# before the steps, on their pedestals, the two angels of the Old and the New Covenant -- limestone, looking out
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from statuary import statue, pedestal, FACE_PZ, capped
yP, zG, rise = 0.8 + CH + 2.2, PZ + PD + 0.4, (PW / 2) * math.tan(math.radians(20))   # the pediment's foot, its gable's face, its height
stat = {"statue pediment apex": statue((0, yP + rise - 0.3, zG - 0.6), kind="man", style="roman", stone="limestone", scale=1.7, seed=3, face=FACE_PZ),
        "statue pediment left": statue((-(PW / 2 - 0.8), yP, zG - 0.5), kind="woman", style="roman", stone="limestone", scale=1.4, seed=5, face=FACE_PZ),
        "statue pediment right": statue((PW / 2 - 0.8, yP, zG - 0.5), kind="woman", style="roman", stone="limestone", scale=1.4, seed=7, face=FACE_PZ)}
for sx, nm, sd in ((-1, "old covenant", 11), (1, "new covenant", 13)):
    x, z = sx * (PW / 2 - 1.4), PZ + PD + 2.6
    stat[f"pedestal {nm}"] = pedestal((x, 0, z), 1.6, 1.6, 2.2, f"the pedestal of the angel of the {nm}")
    stat[f"statue {nm}"] = statue((x, 2.2, z), kind="woman", style="roman", stone="limestone", scale=1.5, seed=sd, face=FACE_PZ, hold={"R": "items/tools/book"})
for k, v in capped(stat).items(): add(k, v)

doc = {"name": "Karlskirche",
       "_about": "THE KARLSKIRCHE, Vienna (1716-37), from components: the church round in plan (an `enclosure` of sixteen faces standing for its oval), a drum of eight windows and the tall dome with its lantern (`domed-tower`); before it a Corinthian PORTICO, six columns under a pediment, on its steps; either side of the portico a GIANT COLUMN after Trajan's, a relief band wound up its shaft, a lantern on its capital; and the front running out to a gate PAVILION at each end, arches through it, under a bell roof.",
       "params": {"detail": 4},
       "base": {"height": 0.6, "steps": 2, "stepOut": 0.5, "margin": 3}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/karlskirche.json"), "w").write(json.dumps(doc, indent=2) + "\n")
