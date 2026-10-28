# MARIA LAACH ABBEY CHURCH (Abteikirche Maria Laach, 1093-1216), on the Laacher See, in buff tuff with dark basalt
# dressings: the Rhenish Romanesque double-choir basilica with SIX TOWERS. The nave is the `basilica` definition --
# six round arches a side, clerestory, aisle walls, groin-vaulted aisles, the Lombard band on every wall -- under groin
# vaults of its own over OBLONG bays, one to an arch (Maria Laach's innovation); the EAST end the crossing under an
# octagonal tower on a square stage, the transept arms with their apsidioles, a short choir bay, its apse with a dwarf
# gallery, and the two slender square towers flanking the apse; the WEST end the westwork: a square bay under the great
# square tower, its west apse, and two ROUND STAIR TOWERS in the angles against the aisles, each a spiral from its aisle
# up to the tower's floor; before it the PARADISE, the atrium of open arcades round a court. Every tower roof is a
# RHENISH HELM (helm.js) -- a gable on every side and rhombi between them, nothing chosen but the gables' pitch.
#   The west front faces +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2
C8 = math.cos(math.pi / 8)
semi = {"profile": "semicircular"}
ROM1 = {"style": "romanesque", "orders": 1}
LOMBARD = {"arch": 0.7, "bay": 5.0, "lesene": 0.6}
arch = lambda w, spring, at=0, sill=0, **kw: {"at": at, "width": w, "sill": sill, "springing": spring, "head": semi, **kw}
r4 = lambda v: round(v, 4)

# ---------------------------------------------------------------- the nave: `basilica`, with its own vaults, one to a bay
NW, PT, AW, AT = 9.0, 1.4, 4.4, 1.2
BAYS, BAY = 6, 5.0
NL = BAYS * BAY                            # 30: the nave runs z -15 .. 15
HB = NW / 2 + PT                           # 5.9: the arcade wall's outer face; the crossing and the bays are 2 HB square
BW = NW + 2 * PT + 2 * AW + 2 * AT         # 23: the body across
OPEN, SPRING = 3.0, 5.0
CROWN = SPRING + OPEN / 2
ARC_H, CLEAR_H, TOP = 10.5, 15.0, 20.0
AISLE_TOP = CROWN + AW / 2 + 0.6
AISLE_WALL = AISLE_TOP + 1.2               # 10.5
add("nave", comp("basilica", {"bays": BAYS, "bayLen": BAY, "naveW": NW, "aisleW": AW, "pierT": PT, "aisleT": AT, "openW": OPEN,
                              "spring": SPRING, "crown": CROWN, "arcadeH": ARC_H, "clearH": CLEAR_H, "naveTop": TOP,
                              "aisleSpring": CROWN, "aisleTop": AISLE_TOP, "arch": "semicircular",
                              "winW": 1.4, "winSill": 4.0, "clearWinW": 1.4, "clearSill": 2.0, "clearSpring": 3.6, "lombard": 1, "lombardArch": 0.7},
                 [[0, 0, 0, 0]], build=["arcade", "clerestory", "aisle wall", "aisle vault"],
                 _about="the nave from the `basilica` definition: six round arches a side on square piers, the clerestory, the aisle walls with the Lombard band, and the aisles' groin vaults"))
b = BAY / 2; A = NW / 2
spread = (A * A - b * b) / (2 * b * b)     # the arch along a bay pointed just enough to rise as high as the round one across
add("nave vault", {"type": "groin", "width": NW, "length": BAY, "springing": CLEAR_H, "top": TOP, "clears": CROWN,
                   "across": semi, "along": {"profile": "pointed", "spread": r4(spread)},
                   "at": [[0, 0, -NL / 2 + b, 0]], "repeat": {"count": BAYS, "step": [0, 0, BAY, 0]},
                   "_about": "the nave's groin vaults over OBLONG bays, one to an arcade arch: round across, pointed along just enough to meet at one crown"})

PITCH = 45
add("nave roof", {"type": "roof", "form": "gable", "width": 2 * HB + 0.6, "length": NL, "pitch": PITCH, "at": [[0, TOP, 0, 0]],
                  "_about": "the nave's roof, from the crossing tower to the west tower"})
AR_W = BW / 2 - HB
add("aisle roofs", {"type": "roof", "form": "shed", "width": AR_W, "length": NL, "pitch": 15,
                    "at": [[-(BW / 2 + HB) / 2, AISLE_WALL, 0, 0], [(BW / 2 + HB) / 2, AISLE_WALL, 0, math.pi]]})
RIDGE = TOP + (2 * HB + 0.6) / 2 * math.tan(math.radians(PITCH))   # 26.2

# ---------------------------------------------------------------- the EAST end
S = 2 * HB                                 # 11.8
SLAB = 0.4
choir_arch = arch(NW - 0.6, CLEAR_H)
EZ = -NL / 2 - HB                          # the crossing's middle
add("crossing", {"type": "enclosure", "plan": {"rect": [S, S]}, "thickness": PT, "height": TOP, "openings": [choir_arch], "interior": True,
                 "at": [[0, 0, EZ, 0]], "_about": "the east crossing: a great arch in each face, to the nave, the choir and the transept arms"})
sq_vault = lambda at, L=NW: {"type": "groin", "width": NW, "length": L, "springing": CLEAR_H, "top": TOP, "across": semi, "along": semi, "at": at}
add("crossing vault", sq_vault([[0, 0, EZ, 0]]))
add("crossing floor", {"type": "box", "width": S, "length": S, "height": SLAB, "at": [[0, TOP, EZ, 0]], "flatRoof": True,
                       "_about": "the slab over the crossing's vault that its tower stands on"})
# (every enclosure of the church -- the crossing, the arms, the choir, the westwork's bay, and the towers' stages over
#  them -- is a space of it: `interior`, on its walls' middles up to its vault's top or its floor; the paradise's walks
#  are open arcades, the open air's)
# the crossing tower: a square stage up past the roofs' ridges (they run into it), then the octagon and its helm
CS_H = round(RIDGE - TOP - SLAB + 0.8, 2)
y = TOP + SLAB
add("crossing stage", {"type": "enclosure", "plan": {"rect": [S, S]}, "thickness": 1.2, "height": CS_H, "glass": False,
                       "tiers": [{"openings": [], "lombard": LOMBARD}],
                       "at": [[0, y, EZ, 0]], "standsOn": ["crossing floor"], "interior": True,
                       "_about": "the crossing tower's square stage, as high as the four roofs that run into it"})
y += CS_H
add("crossing stage top", {"type": "box", "width": S, "length": S, "height": SLAB, "at": [[0, y, EZ, 0]], "flatRoof": True, "standsOn": ["crossing stage"]})
add("crossing stage roof", {"type": "roof", "form": "pyramid", "width": S + 0.4, "length": S + 0.4, "pitch": 30, "at": [[0, r4(y + SLAB), EZ, 0]],
                            "standsOn": ["crossing stage top"], "_about": "a low tent roof over the square stage, the octagon rising out of it: it sheds the corners the octagon leaves"})
y += SLAB
OR_IN = 4.9                                # the octagon's in-radius
OR = OR_IN / C8
OH = 8.0
add("crossing tower", {"type": "enclosure", "plan": {"sides": 8, "radius": r4(OR)}, "thickness": 1.0, "height": OH, "glass": False,
                       "tiers": [{"h": 3.0, "openings": []},
                                 {"openings": {"pattern": "2", "width": 0.9, "gap": 0.7, "pier": 0.7, "sill": 0.5, "springing": 2.9, "head": semi, "surround": ROM1}, "lombard": {**LOMBARD, "arch": 0.6}}],
                       "at": [[0, r4(y), EZ, 0]], "standsOn": ["crossing stage top"], "interior": True,
                       "_about": "the octagon over the crossing: a pair of round-arched openings in every face under the arched corbel table"})
y += OH
add("crossing helm", {"type": "helm", "sides": 8, "radius": r4(OR), "pitch": 40, "frieze": {"arch": 0.55},
                      "at": [[0, r4(y), EZ, 0]], "standsOn": ["crossing tower"],
                      "_about": "its helm: a gable over every face of the octagon and a rhombus over every corner, all meeting at the point"})
add("crossing finial", {"type": "column", "radius": 0.12, "height": 2.0, "sides": 6, "at": [[0, 0, EZ, 0]], "atop": "crossing helm", "standsOn": ["crossing helm"]})

# the transept arms, each with an apsidiole on its east face
TL = 7.0
TX = HB + TL / 2
aisle_at = (HB + AW / 2) - TX              # the aisle's middle along an arm's +z face, from its middle
APS_R = 2.4                                # an apsidiole's outer radius
APS_H, APS_W = 5.5, 8.0                    # its conch's springing, its wall's top
for sx, nm in ((1, "south"), (-1, "north")):
    front = {"h": 11.0, "openings": [arch(2.4, 4.0, surround={"style": "romanesque", "orders": 3})] if sx > 0 else [arch(1.6, 7.5, sill=4.5)], "lombard": LOMBARD}
    add(f"{nm} transept", {"type": "enclosure", "plan": {"rect": [TL, S]}, "thickness": PT, "height": TOP, "openings": [],
                           "tiers": [{"h": 11.0, "openings": []}, {"openings": [arch(1.6, 5.5, sill=2.5)], "lombard": LOMBARD}],
                           "faces": {("3" if sx > 0 else "1"): [choir_arch],
                                     "0": [{"h": 11.0, "openings": [arch(OPEN, SPRING, at=r4(sx * aisle_at))]}, {"openings": [arch(1.6, 5.5, sill=2.5)], "lombard": LOMBARD}],
                                     "2": [{"h": 11.0, "openings": [arch(2 * (APS_R - 0.7), APS_H)]}, {"openings": [arch(1.6, 5.5, sill=2.5)], "lombard": LOMBARD}],
                                     ("1" if sx > 0 else "3"): [front, {"openings": [{"at": 0, "width": 3.0, "sill": 2.0, "springing": 2.0, "head": semi, "foot": semi}], "lombard": LOMBARD}]},
                           "at": [[sx * TX, 0, EZ, 0]], "interior": True,
                           **({"_about": "the transept's arms: an arch from the crossing, an arch from the aisle, an arch into the apsidiole on the east; the south front with a portal in three orders, the north with a window, a round window over each, the Lombard band on both storeys"} if sx > 0 else {})})
    add(f"{nm} transept vault", {"type": "groin", "width": TL - 2 * PT, "length": NW, "springing": CLEAR_H, "top": TOP, "across": semi, "along": semi,
                                 "at": [[sx * (TX - PT / 2), 0, EZ, 0]]})
    add(f"{nm} transept roof", {"type": "roof", "form": "gable", "width": S + 0.6, "length": TL, "pitch": PITCH, "frieze": {"arch": 0.7, "ends": [1]},
                                "at": [[sx * TX, TOP, EZ, sx * Q]], **({"_about": "the arms' roofs, a rising arched frieze up the gable of each front"} if sx > 0 else {})})
    ring = {"type": "ring", "count": 12, "turn": 0.5, "at": [0, 1, 2, 9, 10, 11], "rOuter": APS_R, "rInner": APS_R - 0.7,
            "place": [[sx * TX, 0, EZ - HB, math.pi]]}
    add(f"{nm} apsidiole", {**ring, "height": APS_W, "opening": {"width": 0.8, "sill": 2.2, "springing": 4.2, "head": semi},
                            **({"_about": "the apsidioles, a small half-round chapel off each arm's east face, a stone conch, a half cone"} if sx > 0 else {})})
    add(f"{nm} apsidiole conch", {"type": "dome", "sweep": 0.5, "sides": 12, "radius": APS_R, "thickness": 0.7, "head": semi, "at": [[sx * TX, APS_H, EZ - HB, math.pi]]})
    parts[f"{nm} apsidiole interior"] = {"type": "interior", "plan": {"sides": 12, "radius": APS_R - 0.35}, "arc": [-90, 90], "height": APS_H, "at": ring["place"],
                                         **({"_about": "the apsidiole's space, on its wall's middle, up to its conch (whose inside is the conch's own)"} if sx > 0 else {})}
    add(f"{nm} apsidiole roof", {"type": "dome", "sweep": 0.5, "sides": 12, "radius": APS_R + 0.25, "thickness": 0, "head": {"profile": "trigonal", "rise": 2.2},
                                 "at": [[sx * TX, APS_W, EZ - HB, math.pi]]})

# the choir bay, the apse, the two east towers
CHL = 7.4
CZ = EZ - HB - CHL / 2
APH = 9.5                                  # the apse's conch springs at 9.5 (its gallery and roof follow: gallery-apse)
apse_arch = arch(NW - 0.6, APH)
add("choir", {"type": "enclosure", "plan": {"rect": [S, CHL]}, "thickness": PT, "height": TOP, "openings": [],
              "faces": {"0": [choir_arch], "2": [apse_arch],
                        "1": [{"h": 11.0, "openings": []}, {"openings": [arch(1.6, 5.5, sill=2.0)], "lombard": LOMBARD}],
                        "3": [{"h": 11.0, "openings": []}, {"openings": [arch(1.6, 5.5, sill=2.0)], "lombard": LOMBARD}]},
              "at": [[0, 0, CZ, 0]], "interior": True, "_about": "the choir, a short bay between the crossing and the apse, a window high in each flank"})
add("choir vault", sq_vault([[0, 0, CZ, 0]], CHL - 2 * PT))
add("choir roof", {"type": "roof", "form": "gable", "width": S + 0.6, "length": CHL, "pitch": PITCH, "frieze": {"arch": 0.7, "ends": [0]}, "at": [[0, TOP, CZ, 0]],
                   "_about": "the choir's roof, its east gable over the apse with a rising frieze"})
AZ = CZ - CHL / 2
add("apse", comp("components/gallery-apse", {"R": HB, "T": PT, "spring": APH, "galH": 3.0, "roofRise": 4.6, "winW": 1.4, "winSill": 3.5, "winSpring": 7.5},
                 [[0, 0, AZ, math.pi]], _about="the east apse (`gallery-apse`): round-arched windows in their orders, the stone conch, the dwarf gallery round it under the eaves -- a passage on the conch's back -- and a half cone over it"))
ET_W = 4.6                                 # the east towers, square, in the angles between the choir and its apse
ET_X, ET_Z = HB + ET_W / 2, AZ - ET_W / 2
ET_H = 31.0
add("east towers", {"type": "enclosure", "plan": {"rect": [ET_W, ET_W]}, "thickness": 0.9, "height": ET_H, "glass": False,
                    "tiers": [{"h": 9.0, "openings": [], "lombard": {**LOMBARD, "arch": 0.55, "bay": 9}},
                              {"h": 7.0, "openings": [arch(0.6, 4.6, sill=3.2)], "lombard": {**LOMBARD, "arch": 0.55, "bay": 9}},
                              {"h": 7.0, "openings": [arch(0.7, 4.6, sill=2.8)], "lombard": {**LOMBARD, "arch": 0.55, "bay": 9}},
                              {"openings": {"pattern": "2", "width": 0.8, "gap": 0.6, "pier": 0.6, "sill": 2.2, "springing": 5.0, "head": semi, "surround": ROM1},
                               "lombard": {**LOMBARD, "arch": 0.55, "bay": 9}}],
                    "at": [[ET_X, 0, ET_Z, 0], [-ET_X, 0, ET_Z, 0]], "interior": True,
                    "_about": "the two slender east towers flanking the apse, in four storeys each closed by its arched corbel table, a pair of belfry openings in every face of the top one"})
add("east tower helms", {"type": "helm", "sides": 4, "width": ET_W, "pitch": 62, "frieze": {"arch": 0.5},
                         "at": [[ET_X, ET_H, ET_Z, 0], [-ET_X, ET_H, ET_Z, 0]], "standsOn": ["east towers"],
                         "_about": "their helms, steep: four gables and four rhombi"})

# ---------------------------------------------------------------- the WEST end: the westwork and its stair towers
WZ = NL / 2 + HB
ST_R, ST_WALL, ST_OVER = 2.8, 0.6, 0.6     # the round stair towers, each standing into the aisle's end wall and the bay's flank
ST_DOOR = 1.1                              # their doors: wide enough to walk through (a bay of 12 at the inner face is 1.14)
ST_X = HB + ST_R - ST_OVER
ST_Z = NL / 2 + AT + ST_R - ST_OVER
COURT_DOOR = (ST_Z + ST_R + WZ + HB) / 2      # the doors from the paradise's court into the bay: between the stair tower and the west apse
add("west bay", {"type": "enclosure", "plan": {"rect": [S, S]}, "thickness": PT, "height": TOP, "openings": [],
                 "faces": {"2": [choir_arch], "0": [{"h": 14.5, "openings": [apse_arch]}, {"openings": [], "lombard": LOMBARD}],
                           # (the flanks: the band stops at the stair tower standing against each -- faces run -z along +x, +z along -x)
                           "1": [{"h": 11.0, "openings": [arch(1.6, 2.6, at=r4(WZ - COURT_DOOR), surround=ROM1)]}, {"openings": [arch(1.4, 5.0, sill=2.5)], "lombard": {**LOMBARD, "clear": [[r4(WZ + HB - ST_Z - ST_R - 0.2), S]]}}],
                           "3": [{"h": 11.0, "openings": [arch(1.6, 2.6, at=r4(COURT_DOOR - WZ), surround=ROM1)]}, {"openings": [arch(1.4, 5.0, sill=2.5)], "lombard": {**LOMBARD, "clear": [[0, r4(ST_Z + ST_R + 0.2 - (WZ - HB))]]}}]},
                 "at": [[0, 0, WZ, 0]], "interior": True,
                 "_about": "the westwork's bay under the great tower, open to the nave and to the west apse, a door in each flank from the paradise's court"})
add("west bay vault", sq_vault([[0, 0, WZ, 0]]))
add("west tower floor", {"type": "box", "width": S, "length": S, "height": SLAB, "at": [[0, TOP, WZ, 0]], "walked": True,
                         "_about": "the floor over the bay's vault, the tower's first floor: where the stair towers arrive"})
H_UP = TOP + SLAB
door_at = ST_Z - WZ                        # the door out along the tower's flank, from the face's middle
WT_H = 14.0
WT_DOOR = {"h": 4.0, "openings": [arch(1.2, 2.2, at=r4(-door_at))]}
add("west tower", {"type": "enclosure", "plan": {"rect": [S, S]}, "thickness": 1.3, "height": WT_H, "glass": False,
                   "tiers": [{"h": 4.0, "openings": []},
                             {"h": 4.5, "openings": [arch(0.9, 3.0, sill=1.2)], "lombard": LOMBARD},
                             {"openings": {"pattern": "2", "width": 1.1, "gap": 0.9, "pier": 0.9, "sill": 1.0, "springing": 3.6, "head": semi, "surround": ROM1}, "lombard": LOMBARD}],
                   "faces": {"1": [WT_DOOR, {"h": 4.5, "openings": [arch(0.9, 3.0, sill=1.2)], "lombard": LOMBARD},
                                   {"openings": {"pattern": "2", "width": 1.1, "gap": 0.9, "pier": 0.9, "sill": 1.0, "springing": 3.6, "head": semi, "surround": ROM1}, "lombard": LOMBARD}],
                             "3": [{"h": 4.0, "openings": [arch(1.2, 2.2, at=r4(door_at))]}, {"h": 4.5, "openings": [arch(0.9, 3.0, sill=1.2)], "lombard": LOMBARD},
                                   {"openings": {"pattern": "2", "width": 1.1, "gap": 0.9, "pier": 0.9, "sill": 1.0, "springing": 3.6, "head": semi, "surround": ROM1}, "lombard": LOMBARD}]},
                   "at": [[0, H_UP, WZ, 0]], "standsOn": ["west tower floor"], "interior": True,
                   "_about": "the great west tower over the bay: a door at its foot in each flank from a stair tower, then two storeys under arched corbel tables, paired openings in the belfry"})
add("west tower helm", {"type": "helm", "sides": 4, "width": S, "pitch": 52, "frieze": {"arch": 0.7},
                        "at": [[0, H_UP + WT_H, WZ, 0]], "standsOn": ["west tower"], "_about": "the west tower's helm"})
add("west tower finial", {"type": "column", "radius": 0.12, "height": 2.2, "sides": 6, "at": [[0, 0, WZ, 0]], "atop": "west tower helm", "standsOn": ["west tower helm"]})

# the west apse, low, its half cone under the tower
WAH, WAW = 7.0, 12.5
ring = {"type": "ring", "count": 16, "turn": 0.5, "at": [0, 1, 2, 3, 12, 13, 14, 15], "rOuter": HB, "rInner": NW / 2, "place": [[0, 0, WZ + HB, 0]]}
add("west apse", {**ring, "height": WAW, "opening": {"width": 1.2, "sill": 3.0, "springing": 5.8, "head": semi, "surround": ROM1}, "lombard": {**LOMBARD, "arch": 0.5, "lesene": 0.25, "bay": 9},
                  "_about": "the west apse, lower than the east: round-arched windows, the Lombard band under its eaves"})
add("west apse conch", {"type": "dome", "sweep": 0.5, "sides": 16, "radius": HB, "thickness": PT, "head": semi, "at": [[0, WAH, WZ + HB, 0]]})
parts["west apse interior"] = {"type": "interior", "plan": {"sides": 16, "radius": (HB + NW / 2) / 2}, "arc": [-90, 90], "height": WAH, "at": ring["place"],
                               "_about": "the west apse's space up to its conch"}
add("west apse roof", {"type": "dome", "sweep": 0.5, "sides": 16, "radius": HB + 0.3, "thickness": 0, "head": {"profile": "trigonal", "rise": 4.0},
                       "at": [[0, WAW, WZ + HB, 0]]})

# the aisles' west ends, a door in each into its stair tower
EW = BW / 2 - HB
for sx in (1, -1):
    add(f"{'south' if sx > 0 else 'north'} aisle west wall", {"type": "wall", "width": EW, "height": AISLE_WALL, "thickness": AT,
        "openings": [arch(1.2, 2.0, at=r4(ST_X - HB if sx > 0 else EW - (ST_X - HB)))], "lombard": {**LOMBARD, "lesenes": False},
        "at": [[sx * (HB + EW / 2), 0, NL / 2 + AT, 0]],
        **({"_about": "the aisles' west ends, each with the door into its stair tower"} if sx > 0 else {})})

# the round stair towers: a spiral from the aisle up to the tower's floor, the door out facing the tower
# (a ring's bay k faces bearing k * 30 degrees: 0 +z, 3 +x, 6 -z, 9 -x -- in at 6 toward the aisle's end wall, out at 9 or
#  3 toward the bay's flank; the number of steps sets where the spiral arrives)
def exit_bay(door, steps, R=ST_R, wall=ST_WALL, n=12, turn=24, newel=0.2):
    sr = R - wall - 0.05; rA = (sr + newel) / 2; land = max(1.2, sr - newel)
    return round(door + steps * turn * n / 360 + land / rA / 2 * n / (2 * math.pi)) % n
for sx, nm in ((1, "south"), (-1, "north")):
    want = 9 if sx > 0 else 3
    steps = min((s for s in range(int(H_UP / 0.21), int(H_UP / 0.15)) if exit_bay(6, s) == want), key=lambda s: abs(H_UP / s - 0.19))
    add(f"{nm} stair tower", comp("components/round-stair-tower",
                                  {"R": ST_R, "wall": ST_WALL, "H": H_UP, "steps": steps, "doorBay": 6, "stageH": 3.6, "capRise": 0, "doorW": ST_DOOR, "archW": 0.9,
                                   "finial": 0},
                                  [[sx * ST_X, 0, ST_Z, 0]], build=["shaft", "shaft door", "stair", "belvedere", "belvedere door", "cornice"],
                                  **({"_about": "the two ROUND STAIR TOWERS in the angles between the westwork and the aisles: a spiral from the aisle up to the great tower's floor, where the landing meets the door into it; an arcaded stage over it"} if sx > 0 else {})))
    add(f"{nm} stair helm", {"type": "helm", "sides": 8, "radius": r4(ST_R + 0.2), "pitch": 58, "at": [[sx * ST_X, r4(H_UP + 3.6 + 0.35), ST_Z, 0]],
                             "standsOn": [f"{nm} stair tower"], **({"_about": "and an octagonal helm over each"} if sx > 0 else {})})

# ---------------------------------------------------------------- the PARADISE: the atrium before the west apse
PH = 4.2                                   # its walls' height
PD = 3.6                                   # a wing's depth
CW = ST_X + ST_R + 0.2                     # the court's half width: clear of the stair towers
P0 = NL / 2 + AT                           # it begins at the aisles' west ends
P1 = WZ + HB + HB + 6.5                    # the court's west side, past the apse
PO = CW + PD                               # the wings' outer faces
ARCH_W, PIER = 1.5, 0.7
def arcade(length, passages=()):
    """the openings of an arcade wall `length` long: whole arches about ARCH_W wide on piers, low walls under them -- but
    where a passage is asked (its middle, from the left end) the arch nearest comes down to the ground"""
    n = max(1, round((length - PIER) / (ARCH_W + PIER))); w = (length - PIER) / n - PIER
    out = []
    for i in range(n):
        x = PIER + i * (w + PIER) + w / 2
        door = any(abs(x - p) < (w + PIER) / 2 for p in passages)
        out.append({"at": r4(x), "width": r4(w), "sill": 0 if door else 0.8, "springing": 2.6, "head": semi, "surround": ROM1})
    return out
LW = P1 - P0                               # the side wings' arcades, from the aisles' ends to the west wing's court face
WW = 2 * CW                                # the west wing's arcade, between them
add("paradise side arcades", {"type": "wall", "width": r4(LW), "height": PH, "thickness": 0.6, "glass": False, "openings": arcade(LW, (LW / 2,)),
                              "at": [[r4(CW), 0, r4(P0 + LW / 2), -Q], [r4(-CW), 0, r4(P0 + LW / 2), Q]],
                              "_about": "the PARADISE, the atrium: open arcades on low walls round the court, a passage in the middle of each"})
add("paradise west arcade", {"type": "wall", "width": r4(WW), "height": PH, "thickness": 0.6, "glass": False, "openings": arcade(WW, (WW / 2,)),
                             "at": [[0, 0, r4(P1), math.pi]]})
OL = P1 + PD - P0                          # the side wings' outer walls, the whole length
add("paradise outer walls", {"type": "wall", "width": r4(OL), "height": PH, "thickness": 0.7, "lombard": {**LOMBARD, "arch": 0.6, "bay": 4.0},
                             "openings": [arch(0.6, 2.4, at=r4(x), sill=1.4) for x in (OL * 0.25, OL * 0.5, OL * 0.75)],
                             "at": [[r4(PO), 0, r4(P0 + OL / 2), Q], [r4(-PO), 0, r4(P0 + OL / 2), -Q]],
                             "_about": "its outer walls, small windows, the Lombard band"})
PW = 6.0                                   # the west portal's block
SEG = PO - PW / 2
add("paradise west walls", {"type": "wall", "width": r4(SEG), "height": PH, "thickness": 0.7, "lombard": {**LOMBARD, "arch": 0.6, "bay": 4.0},
                            "at": [[r4(-(PW / 2 + SEG / 2)), 0, r4(P1 + PD), 0], [r4(PW / 2 + SEG / 2), 0, r4(P1 + PD), 0]]})
PPH = 7.0
add("paradise portal", {"type": "wall", "width": PW, "height": PPH, "thickness": 1.4, "glass": False, "lombard": {**LOMBARD, "arch": 0.6, "lesenes": False},
                        "openings": [arch(2.0, 2.6, at=PW / 2, surround={"style": "romanesque", "orders": 3})],
                        "at": [[0, 0, r4(P1 + PD + 0.7), 0]],
                        "_about": "the paradise's west portal, in three orders, a gabled block standing forward of the wall"})
add("paradise portal roof", {"type": "roof", "form": "gable", "width": PW + 0.4, "length": 1.6, "pitch": 40, "frieze": {"arch": 0.6, "ends": [1]},
                             "at": [[0, PPH, r4(P1 + PD), 0]]})
add("paradise east ends", {"type": "wall", "width": r4(PO - BW / 2), "height": PH, "thickness": AT,
                           "at": [[r4((PO + BW / 2) / 2), 0, P0, 0], [r4(-(PO + BW / 2) / 2), 0, P0, 0]],
                           "_about": "the side wings' ends past the aisles"})
add("paradise side roofs", {"type": "roof", "form": "shed", "width": PD + 0.3, "length": r4(OL), "pitch": 18,
                            "at": [[r4(CW + PD / 2 - 0.15), PH, r4(P0 + OL / 2), 0], [r4(-(CW + PD / 2 - 0.15)), PH, r4(P0 + OL / 2), math.pi]],
                            "_about": "lean-to roofs, falling toward the court"})
add("paradise west roof", {"type": "roof", "form": "shed", "width": PD + 0.3, "length": r4(WW), "pitch": 18,
                           "at": [[0, PH, r4(P1 + PD / 2 - 0.15), -Q]]})

doc = {"name": "Maria Laach Abbey",
       "_about": "MARIA LAACH ABBEY CHURCH (1093-1216) on the Laacher See: Rhenish Romanesque, a double-choir basilica with SIX TOWERS, in buff tuff with dark basalt dressings. The nave is the `basilica` definition under groin vaults over oblong bays, the Lombard band -- lesenes and arched corbel tables -- on every wall; the EAST end the crossing under an octagonal tower on a square stage, the transept arms with their apsidioles and rising friezes up their gables, the choir bay, the apse with its dwarf gallery, and the two slender square towers flanking it; the WEST end the westwork, a bay under the great square tower, the west apse, and the two ROUND STAIR TOWERS from the aisles up to the tower's floor; before it the PARADISE, open arcades round a court. Every tower wears a RHENISH HELM (helm.js).",
       "params": {"detail": 4}, "base": {"height": 0.5, "steps": 3, "stepOut": 0.5, "margin": 3}, "railing": {"type": "stone"},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/maria-laach.json"), "w").write(json.dumps(doc, indent=2) + "\n")

# ---------------------------------------------------------------- the component: an apse with a dwarf gallery
HALF16 = [0, 1, 2, 3, 12, 13, 14, 15]
HALF32 = [0, 1, 2, 3, 4, 5, 6, 7, 24, 25, 26, 27, 28, 29, 30, 31]
GALLERY_APSE = {
  "name": "Gallery apse",
  "_about": "THE RHENISH APSE WITH ITS DWARF GALLERY (Zwerggalerie): a half ring of wall with a round-arched window in every bay, the stone CONCH inside springing from the wall's inner face, and above it, under the eaves, a PASSAGE round the apse within the wall's thickness -- an open arcade on the outer face, a solid wall behind -- on whose floor one can walk round. Its floor is not chosen: the conch's back rises inward from the springing, and the passage's floor is where the back has fallen below the passage's inner edge (a hand's breadth over it), so the walk never cuts into the vault. Over all a half cone. It bulges toward +z; place it at the middle of the end it stands against (that wall must stand higher than the cone's point), yawed outward.",
  "params": {
    "detail": 4, "R": 5.9, "T": 1.4, "spring": 9.5, "conchT": 0.9, "arcT": 0.45, "pass": 0.7, "galH": 3.2, "roofRise": 5.0, "over": 0.3,
    "winW": 1.4, "winSill": 3.5, "winSpring": 7.5, "galW": 0.7, "galSill": 0.9,
    "_R": "the apse's outside radius; T its walls; spring where the conch springs; galH the gallery's height; roofRise the half cone's",
    "_pass": "the passage's width, between the arcade (arcT thick, on the outer face) and the wall behind it",
    "ri": "R - T", "cr": "ri + conchT", "rp": "R - arcT - pass",
    "_cr": "the conch's outer radius: it springs from the wall's inner face, conchT thick",
    "floor": "spring + sqrt(max(0, cr * cr - rp * rp)) + 0.1",
    "_floor": "the passage's floor: where the conch's back has fallen below the passage's inner edge",
    "top": "floor + galH"
  },
  "build": ["walls", "conch", "gallery", "gallery wall", "roof"],
  "parts": {
    "walls": {"type": "ring", "count": 16, "turn": 0.5, "at": HALF16, "rOuter": "R", "rInner": "ri", "height": "floor", "place": [[0, 0, 0, 0]],
              "opening": {"width": "winW", "sill": "winSill", "springing": "winSpring", "head": {"profile": "semicircular"}, "surround": {"style": "romanesque", "orders": 1}},
              "_about": "the apse's wall up to the passage's floor, a window in every bay"},
    "conch": {"type": "dome", "sweep": 0.5, "sides": 16, "radius": "cr", "thickness": "conchT", "head": {"profile": "semicircular"}, "at": [[0, "spring", 0, 0]],
              "_about": "the conch, from the wall's inner face"},
    "gallery": {"type": "ring", "count": 32, "turn": 0.5, "at": HALF32, "rOuter": "R", "rInner": "R - arcT", "y": "floor", "height": "galH", "place": [[0, 0, 0, 0]],
                "glass": False, "outside": True, "opening": {"width": "galW", "sill": "galSill", "springing": "galH - 0.5 - galW / 2", "head": {"profile": "semicircular"}},
                "_about": "the dwarf gallery's arcade on the outer face, over a low parapet"},
    "gallery wall": {"type": "ring", "count": 16, "turn": 0.5, "at": HALF16, "rOuter": "rp", "rInner": "ri", "y": "floor", "height": "galH", "place": [[0, 0, 0, 0]], "outside": True,
                     "_about": "the wall behind the passage, over the conch's back: the passage is the open air's, though too narrow for the finishes' rays to see out of it"},
    "roof": {"type": "dome", "sweep": 0.5, "sides": 16, "radius": "R + over", "thickness": 0, "head": {"profile": "trigonal", "rise": "roofRise"}, "at": [[0, "top", 0, 0]],
             "_about": "the half cone over all"},
    "interior": {"type": "interior", "of": ["walls"], "plan": {"sides": 32, "radius": "(R + ri) / 2"}, "arc": [-90, 90], "height": "floor",
                 "_about": "the apse's space up to the dwarf gallery's floor (the gallery is the open air's)"}
  }
}
open(os.path.join(ROOT, "assets/architecture/components/gallery-apse.json"), "w").write(json.dumps(GALLERY_APSE, indent=2) + "\n")
