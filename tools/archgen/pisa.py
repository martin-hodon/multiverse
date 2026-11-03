# PISA, the Piazza dei Miracoli: the LEANING TOWER (1173-1372) with its CATHEDRAL (Buscheto, 1063-1118; Rainaldo's front).
#   THE TOWER. A hollow cylinder 15.48m across (well 7.37m), eight storeys, 55.86m on the low side and 56.67m on the high: the ground
#   storey's fifteen blind arches on engaged columns, then six open galleries of thirty arches on slender columns, round a core the
#   gallery walks; the belfry, narrower, on top (Tommaso Pisano, 1372). It LEANS 3.97 degrees to the south, the top 3.9m out -- and
#   it is CURVED: the builders made each new storey taller on the low side and so bent it back toward the plumb as they went. So each
#   storey is tipped by its own angle (`lean`, arch/assemble.js), each carried to where the one under it ended.
#   Round its foot the catino, the low stone ring that keeps the ground off the sunken base.
#   THE CATHEDRAL. A Latin cross 100m long and 72m across the transept, five aisles (the `basilica` part keeps three: see below), the
#   oval dome on the crossing, apses at the three ends. The front, 35.4m wide and 34.2m high, is the Pisan Romanesque itself: seven blind arches
#   with three doors, and over them four tiers of open loggias on small columns, walks behind them -- the two lower stepping in over
#   the aisles' slopes, the top one under the gable. All in white marble banded with grey.
#   West is +z (the cathedral's front looks that way), south is +x: the tower stands behind the apse on the south side, leaning away from the church.
#   Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
r4 = lambda v: round(v, 4)
Q = math.pi / 2
semi = {"profile": "semicircular"}

# ---------------------------------------------------------------- THE TOWER
TX, TZ = 38.0, -92.0                       # behind the apse, on the south side
R, WELL = 7.74, 3.684                      # its outer radius, the well's
H0, HG, HB = 11.4, 6.42, 6.0               # the ground storey, each gallery, the belfry (to 55.9 + the belfry's cornice)
FOOT = 0.5                                 # the storeys start this far down in the catino, so the low side doesn't lift off it
SOUTH = [1, 0]
# each storey's own lean: over the base a little more than the whole's, less and less going up, the belfry nearest the plumb
# (the curve); they come to 3.97 degrees and 3.9m over the height
LEANS = [4.25, 4.25, 4.2, 4.1, 3.95, 3.8, 3.6, 3.3]
chain = [(0.0, 0.0)]                       # where each storey's foot ends up: out along the lean, up
heights = [H0] + [HG] * 6 + [HB]
for h, d in zip(heights, LEANS):
    u, y = chain[-1]
    chain.append((u + h * math.sin(math.radians(d)), y + h * math.cos(math.radians(d))))
def tip(i, y0):
    """storey i's `lean`: drawn upright at height y0 over the tower's axis, tipped about its foot and carried to the top of the one under it"""
    u, y = chain[i]
    return {"deg": LEANS[i], "toward": SOUTH, "at": [TX, r4(y0), TZ], "shift": [r4(u), r4(y - y0), 0]}
def put(i, y0, name, d):
    add(name, {**d, "lean": tip(i, y0)})

add("catino", {"type": "enclosure", "plan": {"sides": 40, "radius": r4(R + 2.6)}, "thickness": 0.7, "height": 0.7, "glass": False,
               "at": [[TX, 0, TZ, 0]], "_about": "the catino: the low stone ring round the sunken foot of the tower (1838)"})
add("catino floor", {"type": "prism", "plan": {"sides": 40, "radius": r4(R + 2.2)}, "height": 0.25, "walked": True, "at": [[TX, 0, TZ, 0]]})

# the GROUND STOREY: fifteen blind arches on engaged columns, the skin's arches cut back to the core behind them; the door in one
N0 = 15
y = 0.0
ROPEN = dict(width=2.62, springing=7.9, head=semi)
put(0, y, "ground skin", {"type": "ring", "count": N0, "rOuter": R, "rInner": r4(R - 0.4), "height": H0 + FOOT, "y": -FOOT, "polygon": False, "opening": dict(ROPEN),
                          "courses": [{"y": 0, "h": 0.7, "out": 0.18, "profile": "band"}, {"y": r4(H0 - 0.5), "h": 0.5, "out": 0.42, "profile": "band"}],
                          "_about": "the ground storey's face: fifteen blind arches, the core showing behind them"})
put(0, y, "ground core", {"type": "ring", "count": N0, "rOuter": r4(R - 0.4), "rInner": WELL, "height": H0 + FOOT, "y": -FOOT, "solid": True, "skip": [0], "_about": "the wall, a well 7.37m across inside"})
put(0, y, "ground door", {"type": "ring", "count": N0, "rOuter": r4(R - 0.4), "rInner": WELL, "height": H0 + FOOT, "y": -FOOT, "at": [0],
                          "opening": {"width": 1.6, "sill": 0.5, "springing": 4.6, "head": semi}})
put(0, y, "ground columns", {"type": "colonnade", "plan": "round", "radius": r4(R + 0.05), "count": N0, "columnR": 0.34, "height": 7.9 + FOOT, "order": "corinthian", "sides": 8, "at": [[TX, -FOOT, TZ, r4(math.pi / N0)]],
                             "_about": "fifteen columns on the ground storey's piers"})
parts["ground skin"]["place"] = [[TX, 0, TZ, 0]]; parts["ground core"]["place"] = [[TX, 0, TZ, 0]]; parts["ground door"]["place"] = [[TX, 0, TZ, 0]]

# THE GALLERIES: thirty arches on slender columns, a core with a door in it, a floor under the walk, a cornice round the top
NG, RC = 30, 5.95                          # the arches round; the core's outer radius (the gallery walks 1.3m between it and the columns)
RA = 7.5                                   # the arcade's outer face
OW = 1.04                                  # an arch's width
SP = 4.45                                  # the arches' springing over the gallery's floor
for i in range(1, 7):
    y0 = H0 + (i - 1) * HG
    pl = [[TX, 0, TZ, 0]]
    put(i, y0, f"gallery {i} arcade", {"type": "ring", "count": NG, "rOuter": RA, "rInner": r4(RA - 0.42), "height": HG, "y": r4(y0), "place": pl, "polygon": True,
                                       "opening": {"width": OW, "springing": SP, "sill": 0, "head": semi},
                                       "courses": [{"y": r4(HG - 0.62), "h": 0.62, "out": 0.3, "profile": "band"}]})
    put(i, y0, f"gallery {i} columns", {"type": "colonnade", "plan": "round", "radius": r4(RA - 0.21), "count": NG, "columnR": 0.2, "height": SP, "order": "corinthian", "sides": 6, "at": [[TX, r4(y0), TZ, r4(math.pi / NG)]]})
    put(i, y0, f"gallery {i} core", {"type": "ring", "count": 15, "rOuter": RC, "rInner": WELL, "height": HG, "y": r4(y0), "place": pl, "polygon": True, "solid": True})
    put(i, y0, f"gallery {i} floor", {"type": "ring", "count": 15, "rOuter": r4(RA - 0.42), "rInner": RC, "height": 0.25, "y": r4(y0), "place": pl, "polygon": True, "solid": True})
    put(i, y0, f"gallery {i} vault", {"type": "ring", "count": 15, "rOuter": r4(RA - 0.42), "rInner": RC, "height": 0.6, "y": r4(y0 + HG - 0.6), "place": pl, "polygon": True, "solid": True})

# THE BELFRY: narrower, on the sixth gallery's roof, its big round arches between pairs of engaged columns; a walk round it behind a low wall,
# the bells in the arches, a flat top with a low rail
y0 = H0 + 6 * HG
RB, NB = 6.1, 12
pl = [[TX, 0, TZ, 0]]
put(7, y0, "terrace", {"type": "prism", "plan": {"sides": 30, "radius": r4(RA)}, "height": 0.3, "at": [[TX, r4(y0), TZ, 0]]})
put(7, y0, "terrace rail", {"type": "ring", "count": 30, "rOuter": r4(RA), "rInner": r4(RA - 0.25), "height": 1.3, "y": r4(y0 + 0.3), "place": pl, "polygon": True, "opening": {"width": 0.9, "sill": 0.25, "springing": 0.8, "head": semi}})
put(7, y0, "belfry", {"type": "ring", "count": NB, "rOuter": RB, "rInner": r4(RB - 0.7), "height": HB - 0.3, "y": r4(y0 + 0.3), "place": pl, "polygon": True,
                      "opening": {"width": 2.2, "sill": 0.5, "springing": 3.3, "head": semi},
                      "courses": [{"y": r4(HB - 0.9), "h": 0.6, "out": 0.3, "profile": "band"}]})
put(7, y0, "belfry columns", {"type": "colonnade", "plan": "round", "radius": r4(RB + 0.1), "count": NB, "columnR": 0.25, "height": 3.9, "order": "corinthian", "sides": 8, "at": [[TX, r4(y0 + 0.3), TZ, r4(math.pi / NB)]]})
put(7, y0, "belfry top", {"type": "prism", "plan": {"sides": 24, "radius": r4(RB + 0.1)}, "height": 0.35, "at": [[TX, r4(y0 + HB), TZ, 0]]})

# ---------------------------------------------------------------- THE CATHEDRAL
ZF, FW, FH = 50.0, 35.4, 34.2              # the front's face, its width and height
NW, PT, AW, AT = 13.6, 1.3, 8.6, 1.3       # nave between the arcades, arcade walls, the aisle (the real two aisles a side as one), aisle walls
BAYS, BAY = 12, 4.5
NL = BAYS * BAY
ZN = ZF - 1.3 - NL / 2                     # the nave's middle, its west end behind the front's wall
ZE = ZN - NL / 2                           # its east end, the crossing's west side
HB = NW / 2 + PT                           # 8.1: the arcade wall's outer face
OPEN, SPRING = 3.0, 8.0
CROWN = SPRING + OPEN / 2
ARC_H, CLEAR_H, TOP = 17.0, 23.5, 29.5
AISLE_TOP = CROWN + 4.9; AISLE_WALL = AISLE_TOP + 1.2
LOMBARD = {"arch": 0.9, "bay": 4.5, "lesene": 0.6}
arch = lambda w, spring, at=0, sill=0, **kw: {"at": at, "width": w, "sill": sill, "springing": spring, "head": semi, **kw}
add("nave", comp("basilica", {"bays": BAYS, "bayLen": BAY, "naveW": NW, "aisleW": AW, "pierT": PT, "aisleT": AT, "openW": OPEN,
                              "spring": SPRING, "crown": CROWN, "arcadeH": ARC_H, "clearH": CLEAR_H, "naveTop": TOP,
                              "aisleSpring": CROWN, "aisleTop": AISLE_TOP, "arch": "semicircular",
                              "winW": 1.6, "winSill": 5.0, "clearWinW": 1.6, "clearSill": 2.2, "clearSpring": 4.6, "lombard": 1},
                 [[0, 0, r4(ZN), 0]], build=["arcade", "clerestory", "aisle wall"],
                 _about="the nave and aisles: twelve round arches a side, the clerestory, the aisle walls in blind arcades (the real five aisles and their galleries read as three)"))
BW = NW + 2 * PT + 2 * AW + 2 * AT
add("nave ceiling", {"type": "box", "width": r4(2 * HB), "length": NL, "height": 0.4, "flatRoof": True, "at": [[0, TOP, r4(ZN), 0]], "_about": "the flat coffered ceiling"})
add("nave roof", {"type": "roof", "form": "gable", "width": r4(2 * HB + 0.5), "length": NL, "pitch": 27, "at": [[0, TOP + 0.4, r4(ZN), 0]]})
AR = BW / 2 - HB
add("aisle ceilings", {"type": "box", "width": r4(AR), "length": NL, "height": 0.3, "flatRoof": True, "at": [[r4(s * (BW / 2 + HB) / 2), AISLE_WALL, r4(ZN), 0] for s in (-1, 1)]})
add("aisle roofs", {"type": "roof", "form": "shed", "width": r4(AR), "length": NL, "pitch": 14,
                    "at": [[r4(-(BW / 2 + HB) / 2), AISLE_WALL + 0.3, r4(ZN), 0], [r4((BW / 2 + HB) / 2), AISLE_WALL + 0.3, r4(ZN), math.pi]]})

# the crossing, the transept arms and the choir: square-ended halls under gables, an apse off each end
CW, CD = 2 * HB, 18.0                      # the crossing across and along
ZC = ZE - CD / 2                           # its middle
ARM_L, ARM_W, ARM_H = 19.0, 18.0, 25.0     # each arm from the crossing to its apse (72m across the ends with the apses), its width, its walls
CH_L = 15.0
ZCH = ZC - CD / 2 - CH_L / 2
great = arch(10.5, 17.0)
add("crossing", {"type": "enclosure", "plan": {"rect": [CW, CD]}, "thickness": PT, "height": TOP + 0.4, "openings": [], "glass": False,
                 "faces": {str(k): [great] for k in range(4)}, "at": [[0, 0, r4(ZC), 0]], "_about": "the crossing's four great arches"})
for s, nm in ((1, "south"), (-1, "north")):
    x = s * (CW / 2 + ARM_L / 2)
    add(f"{nm} arm", {"type": "enclosure", "plan": {"rect": [ARM_L, ARM_W]}, "thickness": PT, "height": ARM_H, "glass": True, "lombard": LOMBARD,
                      "openings": [],
                      "faces": {("3" if s > 0 else "1"): [arch(10.5, 13.0)], ("1" if s > 0 else "3"): [arch(10.5, 13.0)],
                                "0": [arch(1.8, 13, at=-5, sill=7), arch(1.8, 13, at=0, sill=7), arch(1.8, 13, at=5, sill=7)], "2": [arch(1.8, 13, at=-5, sill=7), arch(1.8, 13, at=0, sill=7), arch(1.8, 13, at=5, sill=7)]},
                      "at": [[r4(x), 0, r4(ZC), 0]], "_about": "a transept arm, three windows a side, open to the crossing and to its apse"})
    add(f"{nm} arm ceiling", {"type": "box", "width": ARM_L, "length": ARM_W, "height": 0.4, "flatRoof": True, "at": [[r4(x), ARM_H, r4(ZC), 0]]})
    add(f"{nm} arm roof", {"type": "roof", "form": "gable", "width": ARM_W + 0.5, "length": ARM_L, "pitch": 27, "at": [[r4(x), ARM_H + 0.4, r4(ZC), Q]]})
    add(f"{nm} apse", comp("components/gallery-apse", {"R": 8.0, "T": PT, "spring": 15.0, "conchT": 0.8, "arcT": 0.4, "pass": 0.7, "galH": 3.0, "roofRise": 3.6,
                                                        "winW": 1.6, "winSill": 5.0, "winSpring": 10.0, "galW": 0.8, "galSill": 1.0},
                           [[r4(s * (CW / 2 + ARM_L)), 0, r4(ZC), r4(s * Q)]]))
add("choir", {"type": "enclosure", "plan": {"rect": [CW, CH_L]}, "thickness": PT, "height": ARM_H, "glass": True, "lombard": LOMBARD, "openings": [],
              "faces": {"0": [arch(10.5, 13.0)], "2": [arch(10.5, 13.0)]}, "at": [[0, 0, r4(ZCH), 0]], "_about": "the choir, open to the crossing and the apse"})
add("choir ceiling", {"type": "box", "width": CW, "length": CH_L, "height": 0.4, "flatRoof": True, "at": [[0, ARM_H, r4(ZCH), 0]]})
add("choir roof", {"type": "roof", "form": "gable", "width": CW + 0.5, "length": CH_L, "pitch": 27, "at": [[0, ARM_H + 0.4, r4(ZCH), 0]]})
add("east apse", comp("components/gallery-apse", {"R": HB, "T": PT, "spring": 16.0, "conchT": 0.8, "arcT": 0.4, "pass": 0.7, "galH": 3.0, "roofRise": 3.6,
                                                   "winW": 1.6, "winSill": 5.0, "winSpring": 10.0, "galW": 0.8, "galSill": 1.0},
                      [[0, 0, r4(ZCH - CH_L / 2), math.pi]], _about="the great apse"))

# THE DOME: on a drum of blind arches over the crossing, oval (its long axis across the church), a slightly pointed section, the Gothic loggia round its foot
DY = TOP + 0.4
add("crossing head", {"type": "box", "width": CW, "length": CD, "height": 0.4, "flatRoof": True, "at": [[0, DY, r4(ZC), 0]]})
DR = 7.0
add("drum", {"type": "ring", "count": 16, "rOuter": DR, "rInner": r4(DR - 1.0), "height": 5.0, "y": r4(DY + 0.4), "place": [[0, 0, r4(ZC), 0]], "polygon": True,
             "opening": {"width": 1.0, "sill": 1.0, "springing": 3.2, "head": semi}, "glass": False,
             "courses": [{"y": 4.3, "h": 0.7, "out": 0.3, "profile": "band"}], "stretch": [1.25, 1, 0.95]})
add("dome", {"type": "dome", "radius": DR, "thickness": 0, "sides": 24, "head": {"profile": "pointed", "spread": 0.35}, "at": [[0, r4(DY + 5.4), r4(ZC), 0]],
             "stretch": [1.25, 1, 0.95], "_about": "the oval dome, its section a little pointed"})
add("lantern", {"type": "column", "radius": 0.9, "height": 2.2, "sides": 8, "at": [[0, 0, r4(ZC), 0]], "atop": "dome"})

# THE FRONT, a stone screen on its silhouette: the aisles' slopes and the nave's gable (the door wall under it); the tiers stand 1.3m out from it
SW, ST = 1.2, 13.0                         # the screen's thickness, the door wall's top
shoulder = [(FW / 2, ST), (FW / 2, 17.8), (13.2, 22.8), (9.0, 22.8), (9.0, 31.4), (0, FH)]
add("front screen", {"type": "screen", "t": SW, "outline": [[r4(x), r4(y)] for x, y in shoulder] + [[r4(-x), r4(y)] for x, y in reversed(shoulder[:-1])],
                     "at": [[0, 0, ZF, 0]], "_about": "the front's silhouette: the aisles' slopes and the nave's low gable"})
BA = FW / 7
add("door wall", {"type": "wall", "width": FW, "height": ST, "thickness": SW, "glass": False,
                  "openings": [arch(3.0, 6.2, at=r4(FW / 2 - 2 * BA)), arch(4.0, 7.2, at=FW / 2), arch(3.0, 6.2, at=r4(FW / 2 + 2 * BA))], "at": [[0, 0, r4(ZF - SW / 2), 0]],
                  "_about": "the three bronze doors"})
add("blind arcade", {"type": "wall", "width": FW, "height": ST, "thickness": 0.5, "glass": False,
                     "openings": [arch(r4(BA - 1.1), 9.2, at=r4((i + 0.5) * BA)) for i in range(7)], "at": [[0, 0, r4(ZF + 0.25), 0]],
                     "courses": [{"y": r4(ST - 0.6), "h": 0.6, "out": 0.3, "profile": "band"}],
                     "_about": "seven tall blind arches across the foot, the doors in the middle and the third from each end"})
add("blind arcade columns", {"type": "colonnade", "count": 8, "spacing": r4(BA), "columnR": 0.42, "height": 9.2, "order": "corinthian", "sides": 8, "at": [[0, 0, r4(ZF + 0.55), 0]]})
def loggia(i, hw, y, h, n):
    """one tier: a ledge, n arches of a thin arcade on columns 1.3m before the screen, its cornice"""
    w, s = 2 * hw, 2 * hw / n
    add(f"tier {i} ledge", {"type": "box", "width": r4(w), "length": 1.5, "height": 0.35, "at": [[0, r4(y), r4(ZF + 0.75), 0]]})
    add(f"tier {i} arcade", {"type": "wall", "width": r4(w), "height": r4(h - 0.35), "thickness": 0.32, "glass": False,
                             "openings": [{"at": r4((k + 0.5) * s), "width": r4(s - 0.5), "sill": 0, "springing": r4(h - 1.55 - s / 2 + 0.25), "head": semi} for k in range(n)],
                             "courses": [{"y": r4(h - 0.8), "h": 0.45, "out": 0.25, "profile": "band"}],
                             "at": [[0, r4(y + 0.35), r4(ZF + 1.34), 0]]})
    add(f"tier {i} columns", {"type": "colonnade", "count": n + 1, "spacing": r4(s), "columnR": 0.2, "height": r4(h - 1.55 - s / 2 + 0.25), "order": "corinthian", "sides": 6, "at": [[0, r4(y + 0.35), r4(ZF + 1.34), 0]]})
loggia(1, FW / 2, ST, 5.1, 19)
loggia(2, 13.2, ST + 5.1, 4.8, 15)
loggia(3, 9.0, ST + 9.9, 4.4, 9)
loggia(4, 9.0, ST + 14.3, 4.2, 9)

# the church's floor, under nave, crossing, arms and choir (their own plans)
add("nave floor", {"type": "box", "width": BW, "length": NL, "height": 0.12, "walked": True, "at": [[0, 0, r4(ZN), 0]], "_about": "the marble floor"})
for nm in ("crossing", "north arm", "south arm", "choir"):
    w, l = parts[nm]["plan"]["rect"]
    add(f"{nm} floor", {"type": "box", "width": w, "length": l, "height": 0.12, "walked": True, "at": [[parts[nm]["at"][0][0], 0, parts[nm]["at"][0][2], 0]]})
build.append(build.pop(build.index("front screen")))    # (the screen stands on what is built under it)
doc = {"name": "Pisa",
       "_about": "PISA: the Leaning Tower (15.48m across, 8 storeys, 56m, leaning 3.97 degrees south and curved back as it was built) and the Cathedral (100m long, 72m across the transept, its oval dome, its front of four tiers of loggias) (tools/archgen/pisa.py).",
       "params": {"detail": 3}, "railing": False, "build": build, "parts": parts}
out = os.path.join(ROOT, "assets", "architecture", "pisa.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1); f.write("\n")
# THE FINISH: white San Giuliano marble; the cathedral's walls banded with grey-blue courses, the tower's left nearly white; lead on the roofs and the dome
BANDED = ["nave", "north arm", "south arm", "choir", "crossing", "north apse", "south apse", "east apse", "door wall", "drum"]
bands = [{"parts": BANDED, "surface": "wall", "side": "out", "above": r4(y), "below": r4(y + 0.55), "pattern": "stone/marble", "palette": "marble-grey"} for y in [1.6 + 2.2 * k for k in range(10)]]
fin = {"name": "Pisa", "building": "architecture/pisa",
       "_about": "Pisa: white marble, the cathedral's walls banded in grey, the roofs and the dome in lead, the tower's interior and the church's plastered.",
       "stone": {"color": "#ece6d8", "accent": "#d6cfbf", "pat": "marble"},
       "rules": [{"parts": [f"gallery {i} core" for i in range(1, 7)] + ["front screen"], "pattern": "stone/marble", "palette": "marble-grey"},   # (the shade behind the arches: the galleries read open, the loggias stand off the front)
                 {"parts": "kind:glass", "pattern": "glass/tracery white", "palette": "grisaille"},
                 {"parts": ["dome", "lantern", "kind:roof"], "pattern": "roofs/sheet metal", "palette": "lead"},
                 {"surface": "floor", "side": "in", "pattern": "stone/marble", "palette": "marble-bw"},
                 {"surface": "floor", "pattern": "stone/marble", "palette": "carrara"},
                 {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white"}] + bands +
                [{"pattern": "stone/marble", "palette": "carrara"}]}
open(os.path.join(ROOT, "assets", "finishes", "pisa.json"), "w").write(json.dumps(fin, indent=1) + "\n")
print("pisa:", len(parts), "parts; top offset", round(chain[-1][0], 2), "height", round(chain[-1][1], 2))
