# MAINZ CATHEDRAL (Mainzer Dom St. Martin, Romanesque, 975-1239), in red sandstone, from components: a DOUBLE-CHOIR
# basilica. The nave is the `basilica` definition (round arcades, clerestory, aisle walls, rib-vaulted aisles) under
# rib vaults of its own over DOUBLE bays (the "bound system": two arcade arches to a vault bay); the EAST end is a
# square choir under an octagonal crossing tower, its apse, and the two ROUND STAIR TOWERS in the angles between
# choir and apse -- `round-stair-tower` (components/), each a spiral from the choir to the terrace round the octagon's
# foot, under an open arcaded belvedere and a stone cone; the WEST end is the transept, the crossing under the tall
# stepped octagonal tower (Romanesque stage with its gables, Gothic belfry, Neumann's baroque stages, bell cap,
# lantern and spire, 83m), and the TREFOIL west choir: three apses round a square bay.
#   The west end faces +z (the show front toward the square). Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2
C8 = math.cos(math.pi / 8)                 # an octagon's in-radius over its circumradius
semi = {"profile": "semicircular"}
arch = lambda w, spring, at=0, sill=0, **kw: {"at": at, "width": w, "sill": sill, "springing": spring, "head": semi, **kw}

# ---------------------------------------------------------------- the nave: `basilica`, with its own double-bay vaults
NW, PT, AW, AT = 13.6, 1.8, 6.8, 1.6       # nave (between the arcades), arcade walls, aisles, aisle walls
BAYS, BAY = 10, 5.4                        # arcade arches; a vault bay is two of them
NL = BAYS * BAY                            # 54: the nave runs z -27 .. 27
HB = NW / 2 + PT                           # 8.6: the arcade wall's outer face; the choirs and crossing are 2*HB square
BW = NW + 2 * PT + 2 * AW + 2 * AT         # 34: the body across
OPEN, SPRING = 3.6, 7.5
CROWN = SPRING + OPEN / 2                  # the arcade's crown, 9.3
ARC_H, CLEAR_H, TOP = 16.0, 23.0, 31.0     # the arcade wall's top, the nave vault's springing, the walls' top
AISLE_TOP = CROWN + AW / 2 + 0.6
AISLE_WALL = AISLE_TOP + 1.2               # 14.5
add("nave", comp("basilica", {"bays": BAYS, "bayLen": BAY, "naveW": NW, "aisleW": AW, "pierT": PT, "aisleT": AT, "openW": OPEN,
                              "spring": SPRING, "crown": CROWN, "arcadeH": ARC_H, "clearH": CLEAR_H, "naveTop": TOP,
                              "aisleSpring": CROWN, "aisleTop": AISLE_TOP, "arch": "semicircular",
                              "winW": 2.0, "winSill": 5.0, "clearWinW": 2.0, "clearSill": 2.2, "clearSpring": 5.0,},
                 [[0, 0, 0, 0]], build=["arcade", "clerestory", "aisle wall", "aisle vault", "aisle ribs"],
                 _about="the nave from the `basilica` definition: ten round arches a side on square piers, the clerestory, the aisle walls, and the aisles' rib vaults, one to an arch"))
VB = 2 * BAY                               # a nave vault bay: two arches (the bound system)
b = VB / 2; A = NW / 2
spread = (A * A - b * b) / (2 * b * b)     # the arch ALONG a bay pointed just enough to rise as high as the round one across
add("nave vault", {"type": "groin", "width": NW, "length": VB, "springing": CLEAR_H, "top": TOP, "clears": CROWN,
                   "across": semi, "along": {"profile": "pointed", "spread": round(spread, 5)},
                   "at": [[0, 0, -NL / 2 + b, 0]], "repeat": {"count": BAYS // 2, "step": [0, 0, VB, 0]},
                   "_about": "the nave's vaults, one over every TWO arcade arches: round across, a little pointed along, meeting at one crown"})
add("nave ribs", {"type": "ribs", "on": "nave vault", "width": 0.5, "depth": 0.3, "wall": {"width": 0.7, "depth": 0.35}})

# ---------------------------------------------------------------- roofs over the nave
PITCH = 45
add("nave roof", {"type": "roof", "form": "gable", "width": 2 * HB + 0.6, "length": NL, "pitch": PITCH, "at": [[0, TOP, 0, 0]]})
AR_W = BW / 2 - HB
add("aisle roofs", {"type": "roof", "form": "shed", "width": AR_W, "length": NL, "pitch": 15,
                    "at": [[-(BW / 2 + HB) / 2, AISLE_WALL, 0, 0], [(BW / 2 + HB) / 2, AISLE_WALL, 0, math.pi]],
                    "_about": "a lean-to over each aisle, under the clerestory's sills"})

# ---------------------------------------------------------------- the EAST choir, its apse and tower
S = 2 * HB                                 # 17.2: a square bay (choirs, crossing) outside
EZ = -NL / 2 - HB                          # the east choir's middle
SLAB = 0.4
choir_arch = arch(NW - 0.6, CLEAR_H)       # the great arch from a bay into the next (crown 29.5)
APH, APW, AP_ROOF = 20.0, 25.5, TOP - 25.5 # the apse's conch springs at 20 (closed by the choir wall over it), its wall runs on to 25.5
apse_arch = arch(NW - 0.6, APH)            # the arch into an apse: as high as its conch
TWR_R = 3.6                                # the round stair towers
TWR_OVER = 0.8                             # how far a tower stands into the choir's wall (its inside meets the wall's face)
TWR_X = HB + TWR_R - TWR_OVER
TWR_Z = EZ - HB + TWR_R                    # in the angle between the choir and its apse
door_at = TWR_Z - EZ                       # the tower door's place along the choir's flank, from the face's middle
#   (a face's `at` runs round the plan: -z along the +x face, +z along the -x face, +x along the +z face, -x along the -z face)
add("east choir", {"type": "enclosure", "plan": {"rect": [S, S]}, "thickness": PT, "height": TOP, "openings": [],
                   "faces": {"0": [choir_arch], "2": [apse_arch],
                             "1": [{"h": 12, "openings": [arch(1.4, 2.2, at=round(-door_at, 4))]}, {"openings": [arch(2.0, 5.0, sill=2.0)]}],
                             "3": [{"h": 12, "openings": [arch(1.4, 2.2, at=round(door_at, 4))]}, {"openings": [arch(2.0, 5.0, sill=2.0)]}]},
                   "at": [[0, 0, EZ, 0]],
                   "_about": "the east choir, a square bay open to the nave and to the apse; a door in each flank into a stair tower"})
sq_vault = lambda at: {"type": "groin", "width": NW, "length": NW, "springing": CLEAR_H, "top": TOP, "across": semi, "along": semi, "at": at}
add("east choir vault", sq_vault([[0, 0, EZ, 0]]))
add("east terrace", {"type": "box", "width": S, "length": S, "height": SLAB, "at": [[0, TOP, EZ, 0]], "walked": True,
                     "_about": "the terrace on the choir's walls and vault, round the octagon's foot: the stair towers come out onto it"})
PAR = {"type": "wall", "height": 1.1, "thickness": 0.4}
y = TOP + SLAB
free0 = TWR_Z + math.sqrt(TWR_R ** 2 - (HB - TWR_X) ** 2) - 0.05       # where along the flank the tower's wall ends
add("east terrace parapets", {**PAR, "width": S, "at": [[0, y, -NL / 2, 0], [0, y, EZ - HB, math.pi]],
                              "_about": "the terrace's parapets: across its two ends..."})
side_len = -NL / 2 - 0.4 - free0
add("east terrace flank parapets", {**PAR, "width": round(side_len, 4),
                                    "at": [[HB, y, round(free0 + side_len / 2, 4), Q], [-HB, y, round(free0 + side_len / 2, 4), -Q]],
                                    "_about": "...and down its flanks from the stair towers"})
ER = 7.0 / C8                              # the east octagon
EH = 13.0
add("east tower", {"type": "enclosure", "plan": {"sides": 8, "radius": round(ER, 4)}, "thickness": 1.2, "height": EH, "glass": False,
                   "tiers": [{"h": 6.0, "openings": []},
                             {"openings": {"pattern": "2", "width": 1.1, "gap": 0.9, "pier": 0.9, "sill": 0.6, "springing": 3.6, "head": semi}}],
                   "at": [[0, y, EZ, 0]], "_about": "the east crossing tower, an octagon on the choir, two round-arched belfry openings in every face"})
add("east tower head", {"type": "prism", "plan": {"sides": 8, "radius": round(ER - 0.7, 4)}, "height": 0.3, "at": [[0, y + EH - 0.3, EZ, 0]], "flatRoof": True,
                        "standsOn": ["east tower"]})
face = 2 * ER * math.sin(math.pi / 8)
add("east tower gables", {"type": "roof", "form": "gable", "width": round(face - 0.2, 4), "length": 0.6, "pitch": 50,
                          "spiral": {"count": 8, "radius": round(7.0 - 0.3, 4), "y": y + EH, "z": EZ}, "standsOn": ["east tower"],
                          "_about": "a gable over every face of the octagon"})
add("east tower roof", {"type": "dome", "sides": 8, "radius": round(ER + 0.3, 4), "thickness": 0, "head": {"profile": "trigonal", "rise": 13.0},
                        "at": [[0, y + EH, EZ, 0]], "standsOn": ["east tower head"], "_about": "its tent roof, rising between the gables"})
add("east tower finial", {"type": "column", "radius": 0.2, "height": 2.5, "sides": 6, "at": [[0, 0, EZ, 0]], "atop": "east tower roof", "standsOn": ["east tower roof"]})

def apse(name, place, yaw, about):
    """an apse: a half ring off a bay's face, its stone conch, a dwarf-gallery band above the conch's springing, and a half cone"""
    ring = {"type": "ring", "count": 16, "turn": 0.5, "at": [0, 1, 2, 3, 12, 13, 14, 15], "rOuter": HB, "rInner": NW / 2,
            "place": [[place[0], 0, place[1], yaw]]}
    add(name, {**ring, "height": APH, "opening": {"width": 2.0, "sill": 5.0, "springing": 11.0, "head": semi}, "_about": about})
    add(f"{name} gallery", {**ring, "count": 32, "at": [0, 1, 2, 3, 4, 5, 6, 7, 24, 25, 26, 27, 28, 29, 30, 31], "y": APH, "height": APW - APH,
                            "glass": False, "opening": {"width": 0.9, "sill": 1.2, "springing": 3.4, "head": semi}})
    add(f"{name} conch", {"type": "dome", "sweep": 0.5, "sides": 16, "radius": HB, "thickness": PT, "head": semi, "at": [[place[0], APH, place[1], yaw]]})
    add(f"{name} roof", {"type": "dome", "sweep": 0.5, "sides": 16, "radius": HB + 0.3, "thickness": 0, "head": {"profile": "trigonal", "rise": AP_ROOF},
                         "at": [[place[0], APW, place[1], yaw]]})
apse("east apse", (0, EZ - HB), math.pi, "the east apse: round-arched windows, a dwarf gallery under the eaves, the stone conch inside and a half cone over it")

# ---- the round stair towers
H_UP = TOP + SLAB                          # the terrace, where the stair arrives
steps = round(H_UP / 0.19)
while (steps * 24 + 49.5) % 360 > 15 and (steps * 24 + 49.5) % 360 < 345: steps -= 1   # (arriving facing the way it set off)
for sx, nm in ((1, "south"), (-1, "north")):     # (the door toward the choir: bay 9 faces -x, bay 3 +x)
    add(f"{nm} stair tower", comp("components/round-stair-tower",
                                  {"R": TWR_R, "H": H_UP, "steps": steps, "doorBay": 9 if sx > 0 else 3, "stageH": 4.2, "capRise": 7.0},
                                  [[sx * TWR_X, 0, TWR_Z, 0]],
                                  **({"_about": "the two ROUND STAIR TOWERS between the choir and its apse: a spiral from the choir up to the terrace round the octagon, an open belvedere at its head, a stone cone"} if sx > 0 else {})))

# the aisles' east ends
add("aisle east walls", {"type": "wall", "width": BW / 2 - HB, "height": AISLE_WALL, "thickness": AT,
                         "openings": [arch(2.0, 8.0, at=(BW / 2 - HB) / 2, sill=4.5)],
                         "at": [[sx * (HB + (BW / 2 - HB) / 2), 0, -NL / 2 - AT, math.pi] for sx in (1, -1)], "_about": "the aisles' east ends, a window in each"})

# ---------------------------------------------------------------- the WEST end: crossing, transept, trefoil choir
WZ = NL / 2 + HB                           # the west crossing's middle
add("west crossing", {"type": "enclosure", "plan": {"rect": [S, S]}, "thickness": PT, "height": TOP, "openings": [choir_arch],
                      "at": [[0, 0, WZ, 0]], "_about": "the west crossing: a great arch in each face, to the nave, the transept arms and the west choir"})
add("west crossing vault", sq_vault([[0, 0, WZ, 0]]))
TL = 15.0                                  # a transept arm's reach beyond the crossing
TX = HB + TL / 2
aisle_at = (HB + AW / 2) - TX              # the aisle's middle along the arm's -z face, from its middle
add("transept arms", {"type": "enclosure", "plan": {"rect": [TL, S]}, "thickness": PT, "height": TOP, "openings": [],
                      "tiers": [{"h": 14, "openings": {"pattern": "2", "width": 2.2, "gap": 4.4, "sill": 5.0, "springing": 10.5, "head": semi}},
                                {"openings": {"pattern": "2", "width": 2.0, "gap": 4.6, "sill": 2.5, "springing": 8.5, "head": semi}}],
                      "at": [[TX, 0, WZ, 0], [-TX, 0, WZ, math.pi]],
                      "faces": {"3": [choir_arch],
                                "2": [{"h": 14, "openings": [arch(5.0, 9.0, at=round(-aisle_at, 4))]}, {"openings": []}],
                                "0": [{"h": 14, "openings": [arch(5.0, 9.0, at=round(aisle_at, 4))]}, {"openings": []}],
                                "1": [{"h": 14, "openings": [arch(3.6, 5.2)]},
                                      {"openings": [{"at": 0, "width": 5.0, "sill": 3.0, "springing": 3.0, "head": semi, "foot": semi}]}]},
                      "_about": "the west transept's arms (the south one turned round, so its -z face is the north one's +z): an arch from the crossing, an arch from the aisle and a door opposite it, a portal and a round window in the end"})
add("transept vaults", {"type": "groin", "width": TL - 2 * PT, "length": NW, "springing": CLEAR_H, "top": TOP, "across": semi, "along": semi,
                        "at": [[TX, 0, WZ, 0], [-TX, 0, WZ, 0]]})
add("transept roofs", {"type": "roof", "form": "gable", "width": S + 0.6, "length": TL, "pitch": PITCH, "at": [[TX, TOP, WZ, Q], [-TX, TOP, WZ, Q]]})

CZ = WZ + S                                # the west choir's middle
add("west choir", {"type": "enclosure", "plan": {"rect": [S, S]}, "thickness": PT, "height": TOP, "openings": [apse_arch],
                   "faces": {"2": [choir_arch]}, "at": [[0, 0, CZ, 0]],
                   "_about": "the west choir, the TREFOIL: a square bay open to the crossing and by an arch on each other side into an apse"})
add("west choir vault", sq_vault([[0, 0, CZ, 0]]))
add("west choir roofs", {"type": "roof", "form": "gable", "width": S + 0.6, "length": S, "pitch": PITCH, "at": [[0, TOP, CZ, 0], [0, TOP, CZ, Q]],
                         "_about": "two gables crossing over the choir bay, one over each pair of its apses"})
apse("west apse", (0, CZ + HB), 0.0, "the trefoil's three apses: the west one...")
apse("north apse", (-HB, CZ), -Q, "...and the two at its sides")
apse("south apse", (HB, CZ), Q, "")
del parts["south apse"]["_about"]

# ---------------------------------------------------------------- the WEST crossing tower, in stages to 83m
add("west crossing floor", {"type": "box", "width": S, "length": S, "height": SLAB, "at": [[0, TOP, WZ, 0]], "flatRoof": True,
                            "_about": "the slab over the crossing's vault that the tower stands on"})
stages = [  # in-radius, height, wall, openings tier, glass
    (7.4, 13.0, 1.4, {"pattern": "2", "width": 1.2, "gap": 1.0, "pier": 1.0, "sill": 0.8, "springing": 3.8, "head": semi}, "Romanesque stage: paired round-arched openings"),
    (6.4, 10.5, 1.0, {"pattern": "1", "width": 2.0, "sill": 1.5, "springing": 6.5, "head": {"profile": "pointed", "spread": 1.0}}, "the Gothic belfry, a tall lancet in every face"),
    (5.1, 7.0, 0.8, {"pattern": "1", "width": 1.6, "sill": 1.2, "springing": 4.6, "head": semi}, "Neumann's baroque stages..."),
    (3.9, 5.0, 0.6, {"pattern": "1", "width": 1.2, "sill": 1.0, "springing": 3.2, "head": semi}, None),
]
y = TOP + SLAB
prev = "west crossing floor"
for i, (rin, h, t, op, about) in enumerate(stages):
    R = rin / C8
    nm = f"west tower {i + 1}"
    lower = 3.0 if i == 0 else 1.0
    add(nm, {"type": "enclosure", "plan": {"sides": 8, "radius": round(R, 4)}, "thickness": t, "height": h, "glass": False,
             "tiers": [{"h": lower, "openings": []}, {"openings": op}], "at": [[0, round(y, 4), WZ, 0]], "standsOn": [prev],
             **({"_about": about} if about else {})})
    add(f"{nm} head", {"type": "prism", "plan": {"sides": 8, "radius": round(R - t * 0.6, 4)}, "height": 0.3, "at": [[0, round(y + h - 0.3, 4), WZ, 0]],
                       "flatRoof": True, "standsOn": [nm]})
    add(f"{nm} cornice", {"type": "prism", "plan": {"sides": 8, "radius": round(R + 0.25, 4)}, "height": 0.35, "at": [[0, round(y + h, 4), WZ, 0]],
                          "flatRoof": True, "standsOn": [nm]})
    if i == 0:
        f = 2 * R * math.sin(math.pi / 8)
        add("west tower gables", {"type": "roof", "form": "gable", "width": round(f - 0.3, 4), "length": 0.6, "pitch": 48,
                                  "spiral": {"count": 8, "radius": round(rin - 0.1, 4), "y": round(y + h + 0.35, 4), "z": WZ}, "standsOn": [f"{nm} cornice"],
                                  "_about": "the Romanesque octagon's eight gables, round the foot of the belfry"})
    prev = f"{nm} cornice"
    y += h + 0.35
R4 = stages[-1][0] / C8
add("west tower cap", {"type": "dome", "sides": 8, "radius": round(R4 + 0.1, 4), "thickness": 0,
                       "head": {"profile": "bell", "waist": 0.72, "lift": 1.0, "rise": 6.5}, "at": [[0, round(y, 4), WZ, 0]], "standsOn": [prev],
                       "_about": "the baroque bell cap..."})
add("west tower lantern", {"type": "column", "radius": 1.3, "height": 3.2, "sides": 8, "at": [[0, 0, WZ, 0]], "atop": "west tower cap", "atopR": 1.3,
                           "standsOn": ["west tower cap"], "_about": "...its lantern..."})
add("west tower spire", {"type": "dome", "sides": 8, "radius": 1.5, "thickness": 0, "head": {"profile": "trigonal", "rise": 6.0},
                         "at": [[0, 3.2, WZ, 0]], "atop": "west tower cap", "atopR": 1.3, "standsOn": ["west tower lantern"], "_about": "...and the pointed spire (on the lantern: set from the cap, as `atop` does not chain)"})
add("west tower finial", {"type": "column", "radius": 0.12, "height": 2.2, "sides": 6, "at": [[0, 9.2, WZ, 0]], "atop": "west tower cap", "atopR": 1.3, "standsOn": ["west tower spire"]})

doc = {"name": "Mainz Cathedral",
       "_about": "MAINZ CATHEDRAL (Mainzer Dom St. Martin, 975-1239), Romanesque, in red sandstone: a DOUBLE-CHOIR basilica. The nave is the `basilica` definition -- ten round arches a side, clerestory, aisle walls, rib-vaulted aisles -- under rib vaults of its own over double bays (the bound system); the EAST choir, a square bay under the octagonal crossing tower with its gables and tent roof, its apse with a dwarf gallery under a half cone, and the two ROUND STAIR TOWERS (`round-stair-tower`) in the angles, each a spiral from the choir to the terrace round the octagon's foot and an open belvedere under a stone cone; the WEST transept with a portal and a round window in each end, the crossing under the tall stepped octagon -- Romanesque stage and its gables, Gothic belfry, Neumann's baroque stages, bell cap, lantern and spire, 83m -- and the TREFOIL west choir, a square bay with an apse on each of its three free sides.",
       "params": {"detail": 4}, "base": {"height": 0.6, "steps": 3, "stepOut": 0.5, "margin": 3}, "railing": {"type": "stone"},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/mainz.json"), "w").write(json.dumps(doc, indent=2) + "\n")

# ---------------------------------------------------------------- the component: a round stair tower
TOWER = {
  "name": "Round stair tower",
  "_about": "A ROUND STAIR TOWER standing on its own (against a wall, in the angle of a choir): a ring of `n` bays, a door at its foot in bay `doorBay`, a spiral inside from the ground up to `H`, where it arrives on its landing at a door out (bay `exitBay`, worked out from where the spiral ends) -- onto a terrace or a gallery the caller builds there; above that an open belvedere of arches over a parapet, a cornice and a cone. Place it at its middle. `steps` may be chosen (12-22cm each) so the stair arrives facing the way the caller wants. Mainz's east towers.",
  "params": {
    "detail": 4, "R": 3.6, "wall": 0.8, "H": 20.0, "n": 12, "newel": 0.2, "turn": 24,
    "steps": "round(H / 0.19)", "doorBay": 0, "stageH": 4.0, "capRise": 6.0, "finial": 1.6,
    "_R": "the tower's outside radius; `wall` its thickness; H the level the stair arrives at (the terrace's)",
    "_steps": "the spiral's steps: the landing's bearing follows from their number, so a caller picks it to arrive facing the door it wants",
    "sr": "R - wall - 0.05", "rA": "(sr + newel) / 2", "land": "max(1.2, sr - newel)",
    "exitBay": "round(doorBay + steps * turn * n / 360 + land / rA / 2 * n / 6.2831853)",
    "_exitBay": "the bay the landing reaches: the first step's bearing, the steps' turns, and half the landing's arc"
  },
  "build": ["shaft", "shaft door", "stair", "belvedere", "belvedere door", "cornice", "cap", "finial"],
  "parts": {
    "shaft": {"type": "ring", "count": "n", "rOuter": "R", "rInner": "R - wall", "height": "H", "place": [[0, 0, 0, 0]], "skip": ["doorBay"], "solid": True,
              "_about": "the round shaft, from the ground to the stair's head"},
    "shaft door": {"type": "ring", "count": "n", "rOuter": "R", "rInner": "R - wall", "height": "H", "place": [[0, 0, 0, 0]], "at": ["doorBay"],
                   "opening": {"width": 1.2, "sill": 0, "springing": 2.0, "head": {"profile": "semicircular"}}},
    "stair": {"type": "spiral-stair", "radius": "sr", "newel": "newel", "turn": "turn", "top": "H", "steps": "steps", "soffit": 0.2,
              "at": [[0, 0, 0, "doorBay * 6.2831853 / n"]], "_about": "the spiral, its first step at the door, its landing at the door out"},
    "belvedere": {"type": "ring", "count": "n", "rOuter": "R", "rInner": "R - wall", "height": "stageH", "y": "H", "place": [[0, 0, 0, 0]],
                  "skip": ["exitBay"], "glass": False,
                  "opening": {"width": 1.1, "sill": 1.0, "springing": "stageH - 0.6 - 0.55", "head": {"profile": "semicircular"}},
                  "_about": "the belvedere at the stair's head: an arch in every bay over a parapet..."},
    "belvedere door": {"type": "ring", "count": "n", "rOuter": "R", "rInner": "R - wall", "height": "stageH", "y": "H", "place": [[0, 0, 0, 0]],
                       "at": ["exitBay"], "glass": False,
                       "opening": {"width": 1.2, "sill": 0, "springing": "stageH - 0.6 - 0.6", "head": {"profile": "semicircular"}},
                       "_about": "...and the door out, where the landing arrives"},
    "cornice": {"type": "prism", "plan": {"sides": "n", "radius": "R + 0.2"}, "height": 0.35, "at": [[0, "H + stageH", 0, 0]], "flatRoof": True,
                "standsOn": ["belvedere"], "_about": "the ceiling over the belvedere and the cornice the cone stands on"},
    "cap": {"type": "dome", "sides": "n", "radius": "R + 0.2", "thickness": 0, "head": {"profile": "trigonal", "rise": "capRise"},
            "at": [[0, "H + stageH + 0.35", 0, 0]], "standsOn": ["cornice"]},
    "finial": {"type": "column", "radius": 0.12, "height": "finial", "sides": 6, "at": [[0, 0, 0, 0]], "atop": "cap", "standsOn": ["cap"]}
  }
}
open(os.path.join(ROOT, "assets/architecture/components/round-stair-tower.json"), "w").write(json.dumps(TOWER, indent=2) + "\n")
