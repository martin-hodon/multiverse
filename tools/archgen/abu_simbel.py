# ABU SIMBEL, the Great Temple of Ramesses II (c. 1264-1244 BC), cut whole out of the Nubian cliff.
#   THE FRONT is a pylon carved in the living rock, 38m wide and 33m high, a torus and cornice at its top, and on the cornice the 22 baboons greeting the sunrise. Against it, in
#   the rock's own stone, sit FOUR COLOSSI of the king, 20m high, two either side of the door, on thrones with the rock behind their backs, hands on their knees, in the nemes and
#   double crown. The one just left of the door lost its head and chest in an earthquake about 27 BC; they still lie at its feet. Over the door in a tall NICHE stands the falcon-headed
#   sun god Ra-Horakhty with the disc on his head. A terrace runs before them behind a low balustrade, a ramp of stairs up its middle.
#   THE ROOMS run back into the hill on one axis, 62m, each lower and narrower: the great hall (18m x 16.7m) with its eight Osirid pillars, the king as Osiris standing against each; the
#   second hall with four square pillars; a vestibule; the sanctuary, its four seated gods at the back (the rising sun reaches them twice a year). The hill's stone is their walls and roof.
#   THE HILL. The rock is the building's mass: beds of it round the rooms, the front cut flat out of a concave bay.
#   The front (real: east, to the sunrise) is +z, its face at z = 0, the axis x = 0. Numbers are worked here and written as numbers.
import os, json, math
from statuary import statue, FACE_PZ, FACE_PX, FACE_NX
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
r4 = lambda v: round(v, 4)
Q = math.pi / 2
flat = {"profile": "flat"}
FW, FH, TERR = 38.0, 33.0, 1.2             # the front's width, height; the terrace it stands on

# ---- the terrace and its stair
TD = 22.0
add("terrace", {"type": "box", "width": FW + 10, "length": TD, "height": TERR, "walked": True, "at": [[0, 0, TD / 2, 0]], "_about": "the terrace before the colossi"})
SW = 7.0
add("terrace stair", {"type": "flight", "width": SW, "run": 0.32, "rise": 0.15, "base": 0, "top": TERR, "landing": 0, "at": [[SW / 2, 0, r4(TD + 8 * 0.32), Q]]})
for s in (-1, 1):
    x0 = s * (SW / 2 + (FW + 10 - SW) / 4)
    add(f"balustrade {'n' if s < 0 else 's'}", {"type": "wall", "width": r4((FW + 10 - SW) / 2), "height": 1.0, "thickness": 0.45, "glass": False, "at": [[r4(x0), TERR, r4(TD - 0.22), 0]],
                                                "courses": [{"y": 0.85, "h": 0.15, "out": 0.08, "profile": "band"}]})
add("falcon posts", {"type": "box", "width": 0.8, "length": 0.8, "height": 1.8, "at": [[r4(s * x), TERR, r4(TD - 0.22), 0] for s in (-1, 1) for x in (SW / 2 + 0.4, 10.0, 16.0, 23.0)], "_about": "the posts of the balustrade, where falcons and little kings stood"})

# ---- THE ROCK. Below the rooms' roof a ring of it round them, its bay open at the rooms; above, a whole mass; two more beds on that, the hill's back
RH = 11.0                                  # the great hall's roof level, under the rock above
HW = 9.0                                   # the rooms' slot in the rock (the walls in it narrow further in)
RZ = -62.0                                 # the slot's back
bay = [(19.0, 0.0), (19.0, 4.0), (34.0, 1.0), (52.0, -10.0), (62.0, -28.0), (60.0, -60.0), (38.0, -78.0), (0.0, -82.0)]
half = bay + [(-x, z) for x, z in reversed(bay[:-1])]
# (from the slot's far side round the outside: a C)
ring = [[HW, -2.0], [HW, RZ], [-HW, RZ], [-HW, -2.0], [-19.0, -2.0]] + [[-x, z] for x, z in bay[1:-1]] + [[0.0, -82.0]] + [[x, z] for x, z in reversed(bay[1:-1])] + [[19.0, -2.0]]
add("rock foot", {"type": "prism", "plan": {"points": ring}, "height": RH, "at": [[0, 0, 0, 0]], "_about": "the hill's stone round the rooms: its flanks stand forward of the front in a bay cut out of the cliff"})
# THE HILL over it and round it, from the ground, one smooth lofted mound running up behind the front and falling away to both sides, its flanks coming forward beside the front (x, its middle's z, reach front, reach back, height)
HL = [(0.0, -42.0, 40.0, 36.0, 39.0), (24.0, -42.0, 40.0, 36.0, 36.0), (42.0, -40.0, 52.0, 36.0, 28.0), (60.0, -38.0, 48.0, 34.0, 15.0), (76.0, -38.0, 30.0, 26.0, 5.0), (86.0, -38.0, 5.0, 5.0, .1)]
add("hill", {"type": "loft", "axis": "x", "half": True, "sides": 20, "smooth": 3, "at": [[0, 0, 0, 0]],
             "sections": [{"s": sx * x, "u": z, "a": a, "a2": a2, "b": h, "n": 1.8} for sx, row in ((-1, HL[:0:-1]), (1, HL)) for (x, z, a, a2, h) in row],
             "_about": "the hill's stone over the rooms and round the front: one smooth mound, falling away to the flanks"})

# ...and at its foot the scree and blown sand: a low bell round the mound, wider than it, whose edge meets the ground flat, so the hill does not come down on the plain as a wall (x, its middle's z, reach front, back, height)
HS = [(0.0, -46.0, 44.0, 50.0, 20.0), (26.0, -46.0, 44.0, 50.0, 20.0), (40.0, -40.0, 64.0, 50.0, 20.0), (64.0, -38.0, 62.0, 46.0, 13.0), (84.0, -38.0, 42.0, 36.0, 5.0), (98.0, -38.0, 8.0, 8.0, .1)]
add("hill scree", {"type": "loft", "axis": "x", "half": True, "hill": True, "sides": 20, "smooth": 3, "at": [[0, 0, 0, 0]],
                   "sections": [{"s": sx * x, "u": z, "a": a, "a2": a2, "b": h} for sx, row in ((-1, HS[:0:-1]), (1, HS)) for (x, z, a, a2, h) in row],
                   "_about": "the scree and sand round the hill's foot, easing it into the plain"})

add("rock back", {"type": "prism", "plan": {"points": [[23.0, -7.0], [23.0, -3.0], [-23.0, -3.0], [-23.0, -7.0]]}, "height": 21.0, "at": [[0, RH, 0, 0]], "_about": "the living rock behind the front, to its shoulders"})
# ---- THE FRONT
FT = 3.0
DW, DH = 3.6, 8.0                          # the door
NW_, NB, NT = 5.2, 16.0, 26.0              # the niche: its width, its sill and head over the terrace
TOR, COR = 0.5, 2.0
add("front", {"type": "wall", "width": FW, "height": FH, "thickness": FT, "glass": False,
              "tiers": [{"h": r4(TERR + DH + 1.0), "openings": [{"at": 0, "width": DW, "sill": TERR, "springing": r4(TERR + DH), "head": flat}]},
                        {"h": r4(NB - DH - 1.0 - TERR + TERR), "openings": []},
                        {"h": r4(NT - NB), "openings": [{"at": 0, "width": NW_, "sill": 0.01, "springing": r4(NT - NB - 0.01), "head": flat}]},
                        {"openings": []}],
              "courses": [{"y": r4(FH - COR - TOR), "h": TOR, "out": 0.25, "profile": "torus"}, {"y": r4(FH - COR), "h": COR, "out": 1.0, "profile": "gorge"}],
              "at": [[0, 0, r4(-FT / 2), 0]], "_about": "the front cut from the rock, 38m by 33m: the door, the niche, the torus and cornice at its top"})
add("niche ledge", {"type": "box", "width": r4(NW_ + 1.4), "length": 3.8, "height": 0.35, "at": [[0, r4(NB - 0.35), -1.35, 0]], "_about": "the ledge the sun god stands on"})
add("niche back", {"type": "box", "width": NW_ + 0.4, "length": 0.5, "height": r4(NT - NB + 0.4), "at": [[0, r4(NB - 0.2 + DH * 0), r4(-FT - 0.25), 0]]})
add("door lintel", {"type": "box", "width": DW + 1.2, "length": 3.6, "height": 1.4, "at": [[0, r4(TERR + DH), -1.4, 0]], "_about": "the door's frame, a dedication carved over it"})

# the baboons along the cornice: 22 little squatting figures, a block and a round head
BY = FH + 0.01
step = (FW - 3.0) / 21
bab = [[r4(-FW / 2 + 1.5 + k * step), BY, -0.5, 0] for k in range(22)]
add("baboons", {"type": "box", "width": 0.95, "length": 0.8, "height": 1.3, "at": bab, "_about": "the 22 baboons greeting the sunrise, on the cornice"})
add("baboon heads", {"type": "dome", "radius": 0.42, "thickness": 0, "sides": 8, "head": {"profile": "semicircular"}, "at": [[x, r4(y + 1.3), z, 0] for x, y, z, _ in bab]})

# ---- THE COLOSSI. On thrones built forward from the front; the statue's scale such that it stands 20m to its crown
SC = 12.5                                  # (statues.js: 1.78m a unit)
XI, XO = 7.6, 15.2                         # the colossi's places across
ZS = 4.3                                   # the seat's middle front to back
SEAT = TERR + 6.1                          # the seat's top
TW = 7.6
for x, nm in ((-XO, "north outer"), (-XI, "north inner"), (XI, "south inner"), (XO, "south outer")):
    add(f"throne {nm}", {"type": "box", "width": TW, "length": 8.2, "height": r4(SEAT - TERR), "at": [[x, TERR, 4.1, 0]]})
    add(f"throne back {nm}", {"type": "box", "width": TW, "length": 2.2, "height": 13.0, "at": [[x, r4(SEAT), 1.1, 0]], "_about": "the rock left standing behind the king's back"})
    add(f"king {nm}", statue((x, r4(SEAT), ZS), kind="man", style="egyptian", outfit={"bare": True}, pose="colossus", stone="sandstone", scale=SC, seed=4, anatomy="soft",
                             face=FACE_PZ, wear=["clothes/pharaoh-crown"], **({"broken": True} if nm == "north inner" else {})))
    # THE KILT, carved on the lap: the wardrobe's `kilt` is a skirt that hangs from the waist, and on a seated pose it falls in two tubes to the ankles. So the shendyt is the rock's own -- a broad squared mass over
    # the hips and thighs, stopping short of the knees, a raised belt round the waist and the pleated tab down its middle over the seat's edge. The statue's own thighs lie inside it
    add(f"kilt {nm}", {"type": "loft", "axis": "z", "sides": 16, "smooth": 2, "at": [[x, 0, 0, 0]],
                       "sections": [{"s": s_, "u": 0, "v": r4(SEAT + v), "a": a, "b": b_, "n": 3.2} for s_, v, a, b_ in ((3.0, 1.4, 2.4, 1.7), (4.6, 1.3, 2.6, 1.6), (7.2, 1.05, 2.6, 1.4), (8.7, 0.9, 2.4, 1.15))],
                       "_about": "the king's kilt, on his lap"})
    add(f"kilt belt {nm}", {"type": "box", "width": 4.7, "length": 3.0, "height": 0.45, "at": [[x, r4(SEAT + 2.75), 3.5, 0]]})
    add(f"kilt tab {nm}", {"type": "box", "width": 1.5, "length": 5.7, "height": 3.15, "at": [[x, r4(SEAT - 0.5), 6.0, 0]], "_about": "its tab, down the middle of the lap and over the edge between the knees"})
# (the broken one's head and chest where they fell, at its feet)
FX = -XI
add("fallen crown", {"type": "dome", "radius": 2.3, "thickness": 0, "sides": 12, "head": {"profile": "semicircular"}, "at": [[r4(FX - 2.2), TERR, 16.0, 0]], "_about": "the fallen head, where it lay"})
add("fallen blocks", {"type": "prism", "plan": {"points": [[-2.6, -1.8], [2.2, -2.2], [3.0, 1.2], [-1.6, 2.2]]}, "height": 1.7, "at": [[r4(FX + 1.8), TERR, 14.5, 0.5], [r4(FX - 0.2), TERR, 18.2, 2.0]], "_about": "the broken chest"})

# ---- RA-HORAKHTY in the niche
add("sun god", statue((0, r4(NB + 0.01), -0.4), kind="man", style="egyptian", outfit={"name": "kilt"}, pose="contrapposto", stone="sandstone", scale=3.9, seed=7, face=FACE_PZ, wear=["clothes/falcon-head"]))

# ---- THE ROOMS, on one axis, in the slot. The floor at the terrace's level
# (the statues in here are drawn only for an eye that could see them: in the rock, or on the axis before the door -- SEEN, statues.js. From anywhere else the rock hides them whole)
SEEN = lambda x, z: [[-26.0 - x, 26.0 - x, -75.0 - z, 3.0 - z], [-9.0 - x, 9.0 - x, -3.0 - z, 45.0 - z]]
FL = TERR
add("rooms floor", {"type": "box", "width": HW * 2, "length": -RZ, "height": FL, "walked": True, "at": [[0, 0, r4(RZ / 2), 0]]})
Z0 = -FT                                   # the great hall from the front's inside
HL, HH = 18.0, 9.8
Z1 = Z0 - HL
for s in (-1, 1):
    add(f"hall pillars {'n' if s < 0 else 's'}", {"type": "box", "width": 1.8, "length": 1.8, "height": HH, "at": [[r4(s * 3.4), FL, r4(Z0 - 2.25 - k * 4.5), 0] for k in range(4)]})
    for k in range(4):
        add(f"osiris {'n' if s < 0 else 's'}{k}", statue((r4(s * 2.0), r4(FL), r4(Z0 - 2.25 - k * 4.5)), kind="man", style="egyptian", outfit={"name": "kilt"}, pose="prayer", stone="painted", scale=4.3, seed=3 + k,
                                                        face=FACE_NX if s > 0 else FACE_PX, wear=["clothes/pharaoh-crown"], seen=SEEN(s * 2.0, Z0 - 2.25 - k * 4.5)))
add("great hall ceiling", {"type": "box", "width": HW * 2, "length": HL, "height": r4(RH - FL - HH), "at": [[0, r4(FL + HH), r4((Z0 + Z1) / 2), 0]], "_about": "painted vultures on the roof down the middle aisle"})
def cross(name, z, door_w, door_h, about=None):
    add(name, {"type": "wall", "width": HW * 2, "height": r4(RH - FL), "thickness": 2.0, "glass": False, "at": [[0, FL, r4(z - 1.0), 0]],
               "openings": [{"at": HW, "width": door_w, "sill": 0, "springing": door_h, "head": flat}], **({"_about": about} if about else {})})
cross("hall back wall", Z1, 2.6, 5.0, "the great hall's end, its door on the axis")
# second hall, 4 pillars, its walls the rock's slot narrowed
Z2 = Z1 - 2.0
SL, SWD, SH = 11.0, 11.0, 7.0
Z3 = Z2 - SL
add("narrowing", {"type": "box", "width": r4(HW - SWD / 2), "length": r4(Z2 - RZ), "height": r4(RH - FL), "at": [[r4(s * (HW + SWD / 2) / 2), FL, r4((Z2 + RZ) / 2), 0] for s in (-1, 1)], "_about": "the rock left standing either side as the rooms narrow"})
add("second hall pillars", {"type": "box", "width": 1.5, "length": 1.5, "height": SH, "at": [[r4(sx * 2.7), FL, r4(z), 0] for sx in (-1, 1) for z in (Z2 - 3.0, Z2 - 8.0)]})
add("second hall ceiling", {"type": "box", "width": SWD, "length": SL, "height": r4(RH - FL - SH), "at": [[0, r4(FL + SH), r4((Z2 + Z3) / 2), 0]]})
cross("vestibule wall", Z3, 2.2, 3.4, "behind the second hall: the door to the vestibule")
Z4 = Z3 - 2.0
VL, VH = 3.0, 4.2
Z5 = Z4 - VL
add("vestibule ceiling", {"type": "box", "width": SWD, "length": VL, "height": r4(RH - FL - VH), "at": [[0, r4(FL + VH), r4((Z4 + Z5) / 2), 0]]})
add("sanctuary wall", {"type": "wall", "width": SWD, "height": r4(RH - FL), "thickness": 2.0, "glass": False, "at": [[0, FL, r4(Z5 - 1.0), 0]],
                       "openings": [{"at": SWD / 2, "width": 1.8, "sill": 0, "springing": 2.8, "head": flat}]})
Z6 = Z5 - 2.0
QL = Z6 - RZ
add("sanctuary narrowing", {"type": "box", "width": 1.6, "length": r4(QL), "height": r4(RH - FL), "at": [[r4(s * (SWD / 2 - 0.8)), FL, r4((Z6 + RZ) / 2), 0] for s in (-1, 1)]})
add("sanctuary ceiling", {"type": "box", "width": r4(SWD - 3.2), "length": r4(QL), "height": r4(RH - FL - 4.0), "at": [[0, r4(FL + 4.0), r4((Z6 + RZ) / 2), 0]]})
add("gods' bench", {"type": "box", "width": r4(SWD - 3.2), "length": 1.6, "height": 0.9, "at": [[0, FL, r4(RZ + 0.8), 0]], "_about": "the bench the four gods sit on, cut from the back wall"})
for k in range(4):
    add(f"god {k + 1}", statue((r4(-2.55 + k * 1.7), r4(FL + 0.9), r4(RZ + 0.75)), kind="man", style="egyptian", outfit={"name": "kilt"}, pose="seated", stone="painted", scale=1.3, seed=11 + k, face=FACE_PZ,
                               wear=["clothes/falcon-head" if k == 3 else "clothes/pharaoh-crown"], seen=SEEN(-2.55 + k * 1.7, RZ + 0.75)))
add("rooms air", {"type": "interior", "plan": {"rect": [HW * 2, -RZ - FT]}, "height": r4(RH - FL), "at": [[0, FL, r4((RZ - FT) / 2), 0]]})

doc = {"name": "Abu Simbel",
       "_about": "ABU SIMBEL, the Great Temple of Ramesses II: the front cut in the cliff, 38m by 33m, four seated colossi 20m high (one broken since antiquity), Ra-Horakhty in his niche over the door, the 22 baboons on the cornice; on one axis into the hill, 62m, the hall of eight Osirid pillars, the second hall, the vestibule, the sanctuary's four gods (tools/archgen/abu_simbel.py).",
       "params": {"detail": 4}, "railing": {"type": "stone", "height": 1.0}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/abu-simbel.json"), "w").write(json.dumps(doc, indent=1) + "\n")
fin = {"name": "Abu Simbel", "building": "architecture/abu-simbel",
       "_about": "All one Nubian sandstone, the front smoothed, the hill left rough; hieroglyphs in sunk relief down the rooms' walls and the thrones.",
       "stone": {"color": "#d8ab70", "accent": "#b98a50", "pat": "ashlar"},
       "rules": [{"parts": [f"{k} {n}" for k in ("kilt", "kilt belt", "kilt tab") for n in ("north outer", "north inner", "south inner", "south outer")], "pattern": "stone/plaster", "palette": "nubian sandstone"},
                 {"parts": ["rock foot", "rock back", "hill", "hill scree"], "side": "out", "pattern": "stone/rock face", "palette": "nubian sandstone"},
                 {"surface": "floor", "pattern": "floors/flagstones", "palette": "nubian sandstone"},
                 {"surface": "wall", "side": "in", "pattern": "hieroglyphs/sunk relief", "palette": "nubian sandstone"},
                 {"parts": ["throne north outer", "throne north inner", "throne south inner", "throne south outer"], "pattern": "hieroglyphs/sunk relief", "palette": "nubian sandstone"},
                 {"surface": "wall", "pattern": "stone/ashlar fine", "palette": "nubian sandstone"}]}
open(os.path.join(ROOT, "assets/finishes/abu-simbel.json"), "w").write(json.dumps(fin, indent=1) + "\n")
print("abu simbel:", len(parts), "parts")
