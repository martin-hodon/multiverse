# ST ISAAC'S CATHEDRAL, St Petersburg (Auguste de Montferrand, 1818-58), the late-classical Russian cathedral, rebuilt
# (2026-11-03) from its ground plan (Wikimedia Commons "Plan of St. Isaac's cathedral.png", scaled to Wikipedia's
# 111.3 x 97.6 m over the steps), OSM's outline (relation 3229838: proportions and orientation) and the cross-section:
#   THE BODY: a rectangle of grey Ruskeala marble, 52.8 x 90.3 m, on a granite podium 1.8 m high; a giant Corinthian
#   order of pilasters through its two storeys of windows, the entablature at the porticoes', an attic over it to the
#   flat roof (walked on) at 33 m; four CORNER TOWERS standing out of its flanks beside the north and south porticoes
#   (the north-west and south-east ones hold the spiral stairs to the roof -- the plan's two spirals), each carrying a
#   square BELFRY: an arched core, its paired corner columns, crossed pediments, a small gilded dome and its cross.
#   FOUR PORTICOES of red granite monoliths (17 m): north and south of sixteen -- eight in front and two rows of four
#   behind columns 1, 3, 6 and 8, as the plan has them -- east and west of eight in one row; their pediments with the
#   bronze reliefs (north the Resurrection, south the Adoration of the Magi, west St Isaac meeting Theodosius, east
#   St Isaac stopping Valens), an apostle at each apex and corner (12) -- angels with lamps on the attic's corners.
#   THE DOME: a round stylobate from the roof to 43 m (the visitors' colonnade walk, reached by a flight from the roof),
#   the drum (inner diameter 22 m, 12 windows) ringed by 24 granite columns of 14 m, the balustrade over them with
#   24 angels (Hermann's), the windowed attic, the gilded dome (25.8 m across) with its ribs, the colonnaded lantern,
#   the cross at 101.5 m.
#   INSIDE: three naves under barrel vaults crossed by the north-south arm, the dome over the crossing on pendentives;
#   the west bay behind the entrance; the iconostasis across the east end -- eight columns, six of malachite and two
#   smaller of lapis lazuli beside the royal doors -- the sanctuary behind it with the altar and the stained-glass
#   Resurrection in the apse window, a chapel either side of it.
#   FRAME: the main (west, entrance) front faces +z, the altar -z; +x is south (St Isaac's Square), -x north (the Neva).
#   Numbers are worked here and written as numbers.
import os, json, math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from statuary import statue, capped, FACE_PZ, FACE_NZ, FACE_PX, FACE_NX
from neoclassical import Balusters
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n); return n
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
r4 = lambda v: round(v, 4)
Q = math.pi / 2
ARCH = {"profile": "semicircular"}

# ---- the numbers
FL = 1.8                                   # the podium's top: the church's floor and the porticoes' (9 granite steps of 0.2)
RT = 33.0                                  # the flat roof's top, the walls' top
BX, BZ, T = 26.4, 45.15, 2.9               # the body: half across (x), half along (z), its walls
IX, IZ = BX - T, BZ - T                    # its inside, half: 23.5, 42.25
OH = 22.6                                  # the main cornice: the porticoes' columns (17 m) and entablature (3.8) over the floor
TX0, TX1, TZ0, TZ1 = 26.4, 33.7, 21.8, 29.1   # a corner tower, +x +z: against the body's flank, along the porticoes' sides
TW = TX1 - TX0                             # 7.3 square
TC = ((TX0 + TX1) / 2, (TZ0 + TZ1) / 2)    # its middle
TT = 1.2                                   # its walls
TH = 35.9                                  # its top (the belfry's floor over its head slab)
WH = RT - FL                               # the walls' height over the floor

# ---- THE PODIUM: granite, under the body and the towers and the north and south porches between them
add("podium", {"type": "prism", "walked": True, "height": FL,
               "plan": {"points": [[-BX, BZ], [BX, BZ], [BX, TZ1], [TX1, TZ1], [TX1, -TZ1], [BX, -TZ1], [BX, -BZ], [-BX, -BZ], [-BX, -TZ1], [-TX1, -TZ1], [-TX1, TZ1], [-BX, TZ1]]},
               "at": [[0, 0, 0, 0]], "_about": "the granite podium the church stands on: its floor, and the floors of the north and south porches between the corner towers"})

# ---- THE BODY: the grey marble walls, a giant Corinthian order through two storeys of windows, an attic to the roof
DOOR_BIG = lambda at: {"at": at, "width": 5.0, "sill": 0, "springing": 8.5, "head": ARCH, "glass": False}
WIN1 = lambda at: {"at": at, "width": 3.0, "sill": 4.0, "springing": 11.5, "head": ARCH, "surround": {"head": "pediment"}}
WIN2 = lambda at: {"at": at, "width": 2.4, "sill": 1.4, "springing": 5.0, "surround": {"head": "cornice"}}
AED = lambda at: {"at": at, "width": 3.4, "sill": 2.4, "springing": 8.8, "head": ARCH}
flank = [{"h": OH - FL, "openings": [DOOR_BIG(0)] + [WIN1(s * 10.6) for s in (-1, 1)] + [AED(s * 37.1) for s in (-1, 1)]},
         {"h": 7.4, "openings": [WIN2(s * z) for z in (10.6, 37.1) for s in (-1, 1)]},
         {"openings": []}]
west = [{"h": OH - FL, "openings": [DOOR_BIG(0)] + [WIN1(s * x) for x in (9.0, 18.5) for s in (-1, 1)]},
        {"h": 7.4, "openings": [WIN2(s * x) for x in (9.0, 18.5) for s in (-1, 1)]},
        {"openings": []}]
east = [{"h": OH - FL, "openings": [{"at": 0, "width": 5.0, "sill": 4.2, "springing": 13.2, "head": ARCH}] + [WIN1(s * x) for x in (9.0, 18.5) for s in (-1, 1)]},
        {"h": 7.4, "openings": [WIN2(s * x) for x in (9.0, 18.5) for s in (-1, 1)]},
        {"openings": []}]
TCLR = [[BZ - TZ1, BZ - TZ0], [BZ + TZ0, BZ + TZ1]]    # where the towers stand against a flank (along the face)
add("body", {"type": "enclosure", "plan": {"rect": [2 * BX, 2 * BZ]}, "thickness": T, "height": WH,
             "faces": {"0": west, "1": flank, "2": east, "3": flank},
             "courses": {"clear": {"1": TCLR, "3": TCLR}},
             "orders": [{"tier": 0, "kind": "corinthian"}],
             "interior": True, "at": [[0, FL, 0, 0]],
             "_about": "the body in grey Ruskeala marble: a giant Corinthian order of pilasters through the two storeys of windows -- the lower under pediments, the upper "
                       "under cornices -- its entablature at the porticoes', the attic over it to the roof; the great doors behind the west, north and south porticoes, the altar window east"})
# the dressed windows at the flanks' ends: each between two Corinthian columns under a small pediment
for sx, nm in ((1, "south"), (-1, "north")):
    add(f"aedicules {nm}", {"type": "colonnade", "order": "corinthian", "count": 2, "spacing": 5.6, "columnR": 0.42, "height": 9.6, "taper": 0.9,
                            "entablature": {"h": 1.2, "depth": 1.1}, "at": [[sx * (BX + 0.55), FL, s * 37.1, Q] for s in (-1, 1)],
                            **({"_about": "the aedicules round the end windows of the flanks: two columns, an entablature"} if sx > 0 else {})})
    add(f"aedicule pediments {nm}", {"type": "roof", "form": "gable", "width": 7.0, "length": 1.3, "pitch": 22, "overhang": 0.1,
                                     "at": [[sx * (BX + 0.55), FL + 10.8, s * 37.1, Q] for s in (-1, 1)],
                                     **({"_about": "and their pediments"} if sx > 0 else {})})

# ---- INSIDE: the pier lines, the cross walls, the iconostasis wall -- walls with their arches, from the floor to the roof
def iwall(name, a, b, t, ops, H=RT - 0.4 - FL, y0=FL, about=None, **kw):
    """a wall from a to b (x, z), its middle on that line, `t` thick, H high: its openings (distance from a, width,
    springing, sill) as arches -- glass-less"""
    L = math.dist(a, b); dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    op = [{"at": r4(d - L / 2), "width": w, "sill": sl, "springing": sp, "head": ARCH if hd else {"profile": "flat"}, "glass": False}
          for d, w, sp, sl, hd in [tuple(o) + (0, True)[len(o) - 3:] for o in ops]]
    mx, mz = (a[0] + b[0]) / 2 - t / 2 * dz, (a[1] + b[1]) / 2 + t / 2 * dx
    d = {"type": "wall", "width": r4(L), "height": r4(H), "thickness": t, "tiers": [{"openings": op}],
         "at": [[r4(mx), y0, r4(mz), r4(math.atan2(-dz, dx))]], **kw}
    if about: d["_about"] = about
    return add(name, d)

PX, PT = 12.75, 3.5                        # the pier lines (the naves' arcades): their middle, their thickness
NV = PX - PT / 2                           # the central nave's half width: 11
SA = PX + PT / 2                           # the side naves' inner side: 14.5
SPR = 21.6                                 # the great arches' and the central vault's springing
GA = 2 * NV - 0.2                          # the great arches round the crossing: 21.8 (their crown under the roof)
for sx, nm in ((1, "south"), (-1, "north")):
    # (from the west wall to the east: the west bay's arch, the arch into the north-south arm's bay, the crossing, its
    #  eastern bay, the door into the chapel beside the sanctuary)
    iwall(f"pier line {nm}", (sx * PX, IZ), (sx * PX, -IZ), PT,
          [(IZ - 35.6, 8.0, 15.0 - FL), (IZ - 20.0, 11.0, 18.0 - FL), (IZ, GA, SPR - FL), (IZ + 20.0, 11.0, 18.0 - FL), (IZ + 35.6, 2.0, 4.0, 0, False)],
          about="the pier line between the central nave and the side nave: the great arch round the crossing, arches either side, a door into the chapel at the east end"
          if sx > 0 else None)
CZ = NV + PT / 2                           # the cross walls round the crossing: 12.75
for sz, nm in ((1, "west"), (-1, "east")):
    iwall(f"crossing wall {nm}", (-IX, sz * CZ), (IX, sz * CZ), PT,
          [(IX - 19.0, 8.0, 18.0 - FL), (IX, GA, SPR - FL), (IX + 19.0, 8.0, 18.0 - FL)],
          about="the crossing's west and east sides: the great arch into the nave, arches into the side naves" if sz > 0 else None)
WZ = 27.25                                 # the west bay's wall, behind the vestibule
iwall("west bay wall", (-IX, WZ), (IX, WZ), PT, [(IX - 19.0, 7.0, 15.0 - FL), (IX, 16.0, 19.0 - FL), (IX + 19.0, 7.0, 15.0 - FL)],
      about="between the west bay (the vestibule behind the great west door) and the nave: a wide arch, a smaller one into each side nave")
EZ = -27.25                                # the sanctuary's wall, behind the iconostasis
iwall("sanctuary wall", (-IX, EZ), (IX, EZ), PT, [(IX - 19.0, 2.4, 4.2), (IX, 14.0, 14.0 - FL), (IX + 19.0, 2.4, 4.2)],
      about="the wall behind the iconostasis: the sanctuary's great arch, a door into each chapel either side of it")

# ---- the vaults, the crossing's pendentives and their deck, the roof over them
VT = RT - 0.4                              # the vaults' extrados: the roof slab's underside
# (each nave's vault in two lengths, from wall to wall: the west bay's and the sanctuary's walls stand under their joints)
for nm, segs in (("west", ((SA, WZ - PT / 2), (WZ + PT / 2, IZ))), ("east", ((-(-EZ - PT / 2), -SA), (-IZ, EZ - PT / 2)))):
    for k, (z0, z1) in enumerate(segs):
        tag = f"{nm} {'bay' if k else 'arm'}"
        add(f"nave vault {tag}", {"type": "barrel", "width": 2 * NV, "length": r4(z1 - z0), "springing": SPR, "top": VT, "head": ARCH, "at": [[0, 0, r4(z1), 0]],
                                  **({"_about": "the central nave's barrel vaults, west and east of the crossing, wall to wall"} if nm == "west" and not k else {})})
        add(f"aisle vaults {tag}", {"type": "barrel", "width": IX - SA, "length": r4(z1 - z0), "springing": 25.0, "top": VT, "head": ARCH,
                                    "at": [[sx * (IX + SA) / 2, 0, r4(z1), 0] for sx in (-1, 1)],
                                    **({"_about": "the side naves' barrel vaults"} if nm == "west" and not k else {})})
add("arm vaults", {"type": "barrel", "width": 2 * NV, "length": IX - SA, "springing": SPR, "top": VT, "head": ARCH,
                   "at": [[IX, 0, 0, Q], [-SA, 0, 0, Q]], "_about": "the north-south arm's vaults, from the crossing to the north and south doors"})
add("pendentives", {"type": "pendentives", "span": 2 * NV, "springing": SPR, "sides": 24, "at": [[0, 0, 0, 0]], "deck": {"thickness": 0.4, "out": PT},
                    "_about": "the pendentives over the crossing, and the roof round the drum's foot"})
add("roof ends", {"type": "box", "walked": True, "width": 2 * IX, "length": IZ - SA, "height": 0.4,
                  "at": [[0, VT, sz * (IZ + SA) / 2, 0] for sz in (-1, 1)], "_about": "the flat roof, walked on: west and east of the crossing"})
add("roof sides", {"type": "box", "walked": True, "width": IX - SA, "length": 2 * SA, "height": 0.4,
                   "at": [[sx * (IX + SA) / 2, VT, 0, 0] for sx in (-1, 1)], "_about": "and over the north-south arm"})
add("interior", {"type": "interior", "plan": {"rect": [2 * (BX - T / 2), 2 * (BZ - T / 2)]}, "height": VT - FL, "at": [[0, FL, 0, 0]],
                 "_about": "the church's space, from its floor to the vaults' crowns (to the walls' middles)"})

# ---- the iconostasis: its screen across the central nave, the solea before it, its columns (six of malachite, two
# small ones of lapis lazuli by the royal doors), the cornice over them; the altar and the window behind
IZS = -25.2                                # the screen's middle
SOL = 0.18
add("solea", {"type": "box", "width": 2 * NV, "length": 3.6, "height": SOL, "at": [[0, FL, IZS + 1.5, 0]],
              "_about": "the solea: the raised step before the iconostasis"})
iwall("iconostasis", (-NV, IZS), (NV, IZS), 0.6, [(NV, 3.6, 7.0), (NV - 6.3, 1.4, 3.4), (NV + 6.3, 1.4, 3.4)], H=18.5, y0=FL + SOL, inside=True,
      about="the iconostasis: its screen of icons in three tiers, the royal doors in the middle, the deacons' doors either side")
add("iconostasis malachite", {"type": "colonnade", "order": "corinthian", "count": 1, "spacing": 1.0, "columnR": 0.45, "height": 9.66, "taper": 0.92, "inside": True,
                              "at": [[s * x, FL + SOL, IZS + 0.85, 0] for x in (5.0, 7.6, 10.2) for s in (-1, 1)],
                              "_about": "the six malachite columns (9.66 m) of the iconostasis, gilt bases and capitals"})
add("iconostasis lapis", {"type": "colonnade", "order": "corinthian", "count": 1, "spacing": 1.0, "columnR": 0.3, "height": 4.7, "taper": 0.92, "inside": True,
                          "at": [[s * 2.6, FL + SOL, IZS + 0.7, 0] for s in (-1, 1)],
                          "_about": "the two smaller lapis-lazuli columns beside the royal doors"})
add("iconostasis cornice", {"type": "box", "width": 2 * NV, "length": 1.6, "height": 1.0, "inside": True, "at": [[0, FL + SOL + 9.66, IZS + 0.6, 0]],
                            "_about": "the gilt entablature over the iconostasis columns"})
add("altar", {"type": "box", "width": 2.4, "length": 1.8, "height": 1.15, "inside": True, "at": [[0, FL, -36.5, 0]], "_about": "the altar table in the sanctuary"})

# ---- THE CORNER TOWERS: from the podium to over the roof, a door at their foot from the porch; the NW and SE ones
# hold the spiral stairs (`tower-stair`) to the roof, a door at its head onto the roof walk
TDOOR = lambda: {"at": 0, "width": 1.3, "sill": 0, "springing": 2.6, "head": ARCH, "glass": False}
TWIN = [{"at": 0, "width": 1.6, "sill": 6.0, "springing": 12.0, "head": ARCH}]
towers = []
for sx in (-1, 1):
    for sz in (-1, 1):
        cx, cz = sx * TC[0], sz * TC[1]
        stair = sx * sz < 0                # NW (-x +z) and SE (+x -z), as on the plan
        door_face = "2" if sz > 0 else "0"                 # toward the porch between the towers
        roof_face = "1" if sx < 0 else "3"                 # toward the roof
        outer = "3" if sx < 0 else "1"
        end = "0" if sz > 0 else "2"
        top = [{"at": 0, "width": 1.3, "sill": 3.0, "springing": 5.4, "head": {"profile": "flat"}, "glass": False}]
        faces = {door_face: [{"h": OH - FL, "openings": [TDOOR()]}, {"h": 7.4, "openings": []}, {"openings": []}],
                 roof_face: [{"h": OH - FL, "openings": []}, {"h": 7.4, "openings": []}, {"openings": top}],
                 outer: [{"h": OH - FL, "openings": TWIN}, {"h": 7.4, "openings": [WIN2(0)]}, {"openings": []}],
                 end: [{"h": OH - FL, "openings": TWIN}, {"h": 7.4, "openings": [WIN2(0)]}, {"openings": []}]}
        nm = ("north" if sx < 0 else "south") + ("west" if sz > 0 else "east")
        add(f"tower {nm}", {"type": "enclosure", "plan": {"rect": [TW, TW]}, "thickness": TT, "height": TH - FL, "faces": faces,
                            "orders": [{"tier": 0, "kind": "corinthian"}], "courses": {"skip": [int(roof_face)]}, "interior": True,
                            "at": [[r4(cx), FL, r4(cz), 0]],
                            **({"_about": "a corner tower: its order and windows like the body's, a door from the porch at its foot"} if not towers else {})})
        towers.append((cx, cz, stair, nm, sx, sz))
c = (TW - 2 * TT) / 2 - 1.8 - 0.05
for cx, cz, stair, nm, sx, sz in towers:
    if stair:
        add(f"stair {nm}", comp("components/tower-stair", {"W": r4(TW - 2 * TT), "H": WH, "tx": r4(sx * c), "tz": r4(sz * c), "hand": "right" if sx < 0 else "left"},
                                [[r4(cx), FL, r4(cz), 0]],
                                _about="the spiral stair in the tower's outer corner, from the porch up to the roof's level, its floor round the head and the door onto the roof walk"))
    else:
        add(f"tower floor {nm}", {"type": "box", "width": TW - 2 * TT, "length": TW - 2 * TT, "height": 0.4, "at": [[r4(cx), RT - 0.4, r4(cz), 0]],
                                  "_about": "the tower's floor at the roof's level"})
add("tower heads", {"type": "box", "width": TW + 0.4, "length": TW + 0.4, "height": 0.5, "flatRoof": True,
                    "at": [[r4(cx), TH, r4(cz), 0] for cx, cz, *_ in towers], "_about": "the cornice slab over each tower: the belfry's floor"})

# ---- THE BELFRIES: a square arched core, a pair of columns at each corner, crossed pediments, the gilded dome
BY = TH + 0.5
BC = 5.4
bel = [[r4(cx), BY, r4(cz), 0] for cx, cz, *_ in towers]
add("belfry cores", {"type": "enclosure", "plan": {"rect": [BC, BC]}, "thickness": 0.6, "height": 8.4, "outside": True,
                     "openings": [{"at": 0, "width": 2.6, "sill": 0, "springing": 6.2, "head": ARCH, "glass": False}], "at": bel,
                     "_about": "the belfry: a square core, an arch on every side for the bells"})
for f, (dx, dz, yaw) in enumerate(((0, 1, 0), (1, 0, Q), (0, -1, 0), (-1, 0, Q))):
    add(f"belfry columns {f}", {"type": "colonnade", "order": "corinthian", "count": 2, "spacing": BC, "columnR": 0.32, "height": 7.6, "taper": 0.88,
                                "entablature": {"h": 1.0, "depth": 0.9},
                                "at": [[r4(p[0] + dx * (BC / 2 + 0.5)), BY, r4(p[2] + dz * (BC / 2 + 0.5)), yaw] for p in bel],
                                **({"_about": "the belfries' columns: two at each face, paired at the corners"} if f == 0 else {})})
add("belfry cornices", {"type": "box", "width": BC + 1.9, "length": BC + 1.9, "height": 0.5, "flatRoof": True,
                        "at": [[p[0], BY + 8.6, p[2], 0] for p in bel], "_about": "the cornice round the belfry's head"})
add("belfry pediments", {"type": "roof", "form": "gable", "width": BC + 1.9, "length": BC + 1.9, "pitch": 22, "overhang": 0.15,
                         "at": [[p[0], BY + 9.1, p[2], a] for p in bel for a in (0, Q)], "_about": "the crossed pediments, one over each face"})
add("belfry domes", comp("components/drum-dome", {"R": 2.0, "dt": 0.4, "H": 2.6, "n": 8, "every": 2, "winW": 0.6, "winSill": 0.9, "winH": 1.2,
                                                  "profile": "semicircular", "domeT": 0.25, "ribsN": 8, "ribW": 0.14,
                                                  "lanternR": 0.45, "lanternH": 1.6, "lanternSides": 8, "lanternCapR": 0.4},
                         [[p[0], BY + 9.1, p[2], 0] for p in bel],
                         build=["drum", "drum piers", "dome", "ribs", "ribbed lantern", "lantern ball", "lantern cross", "lantern cross arm"],
                         _about="on each belfry a small gilded dome on its drum, its lantern and cross"))

# ---- THE PORTICOES: red granite monoliths on granite steps, their pediments
PH = {"colR": 0.92, "colH": 17.0, "entH": 3.8, "order": "corinthian", "steps": 0, "pitch": 20}
NS_SP, NS_D = 5.29, 19.1                   # north and south: eight in front, 5.29 apart, standing 19.1 m out of the flank
WE_SP, WE_D = 5.5, 6.35                    # west and east: eight in one row
for nm, at, p in (("portico south", [BX, FL, 0, Q], {"count": 8, "spacing": NS_SP, "depth": NS_D}),
                  ("portico north", [-BX, FL, 0, -Q], {"count": 8, "spacing": NS_SP, "depth": NS_D}),
                  ("portico west", [0, FL, BZ, 0], {"count": 8, "spacing": WE_SP, "depth": WE_D}),
                  ("portico east", [0, FL, -BZ, math.pi], {"count": 8, "spacing": WE_SP, "depth": WE_D})):
    add(nm, comp("components/portico", {**PH, **p}, [at], build=["columns", "pediment"],
                 _about="an octastyle portico of red granite monoliths (17 m, Corinthian, bronze capitals) under its pediment and bronze relief"))
FR = BX + NS_D - 0.92 * 1.8                # the north and south front rows' line
for sx, nm in ((1, "south"), (-1, "north")):
    add(f"portico {nm} rows", {"type": "colonnade", "order": "corinthian", "count": 2, "spacing": 2 * NS_SP, "columnR": 0.92, "height": 17.0, "taper": 0.86,
                               "entablature": {"h": 3.8, "depth": 2.4},
                               "at": [[r4(sx * (FR - k * NS_SP)), FL, r4(sz * 2.5 * NS_SP), Q] for k in (1, 2) for sz in (-1, 1)],
                               "_about": "the two rows of four columns behind the front row's first, third, sixth and eighth"})
    add(f"steps {nm}", {"type": "crepidoma", "width": r4(BX + NS_D - TX1), "length": 43.6, "steps": 9, "stepH": 0.2, "stepOut": 0.42,
                        "at": [[r4(sx * (TX1 + BX + NS_D) / 2), 0, 0, 0]], "_about": "the portico's nine granite steps, on three sides"})
for sz, nm in ((1, "west"), (-1, "east")):
    add(f"steps {nm}", {"type": "crepidoma", "width": 44.0, "length": WE_D, "steps": 9, "stepH": 0.2, "stepOut": 0.45,
                        "at": [[0, 0, r4(sz * (BZ + WE_D / 2)), 0]], "_about": "the portico's nine granite steps"})

# ---- THE DOME: the stylobate (the colonnade walk at 43 m), the flight to it, the drum-dome
SB = 43.0
R, DT, PW = 11.0, 2.5, 2.8                 # the drum: its inside (the crossing's circle), its wall, the walk behind the columns
BR = 18.6                                  # the walk's outer edge
add("stylobate", {"type": "ring", "walked": True, "count": 24, "rOuter": BR, "rInner": R, "height": SB - VT, "y": VT, "turn": 0.5, "solid": True,
                  "courses": {"cornice": True}, "place": [[0, 0, 0, 0]],
                  "_about": "the round base of the dome over the roof: its top, round the drum, is the colonnade walk visitors climb to"})
add("dome well", {"type": "interior", "plan": {"sides": 24, "radius": R + DT / 2}, "height": SB - VT, "at": [[0, VT, 0, 0]],
                  "_about": "the church's space on up through the stylobate to the drum's"})
NST = round((SB - RT) / 0.17)
add("colonnade stair", {"type": "flight", "width": 2.4, "run": 0.3, "rise": 0.17, "base": RT, "top": SB, "landing": 0, "railing": {"type": "stone", "height": 0.9},
                        "at": [[-1.2, 0, r4(-(BR - 0.3) - NST * 0.3), -Q]],
                        "_about": "the flight from the roof walk up to the colonnade walk, on the east axis, stone parapets either side (iron ones read as two black strokes over the roof)"})
DH, AH, DP = 16.4, 9.0, 1.6               # the drum to the peristyle's deck, the attic over it, the dome's plinth
add("dome", comp("components/drum-dome", {"R": R, "dt": DT, "H": DH, "n": 24, "every": 2, "winW": 2.4, "winSill": 3.0, "winH": 7.5,
                                          "profile": "semicircular", "domeT": 0.9, "colN": 24, "colR": 0.7, "colH": 14.0, "pw": PW,
                                          "attic": "yes", "atticH": AH, "atticWin": 1.6, "atticSill": 3.6, "atticWinH": 3.2, "atticHead": "flat",
                                          "plinth": "yes", "domePlinth": DP, "domeR": 12.9, "ribsN": 24, "ribW": 0.32,
                                          "lanternR": 2.8, "lanternH": 8.4, "lanternSides": 8, "lanternCapR": 2.2},
                 [[0, SB, 0, 0]], build=["drum", "drum piers", "peristyle", "peristyle deck", "attic", "attic piers", "dome plinth", "dome", "ribs",
                                         "ribbed lantern", "lantern columns", "lantern spire", "lantern ball", "lantern cross", "lantern cross arm",
                                         "interior", "attic interior"],
                 _about="the drum with its 12 windows and its peristyle of 24 granite columns, the windowed attic over them, the gilded dome with its ribs, the lantern and the cross"))

# ---- balustrades: round the roof, round the colonnade walk (open where the flight arrives), over the peristyle
bal = Balusters(h=1.1, every=0.45)
E = 0.3                                    # (in from the walls' face)
for sx in (-1, 1):
    for z0, z1 in ((-BZ + E, -TZ1), (-TZ0, TZ0), (TZ1, BZ - E)):
        bal.run((sx * (BX - E), z0), (sx * (BX - E), z1), RT)
for sz in (-1, 1):
    bal.run((-BX + E, sz * (BZ - E)), (BX - E, sz * (BZ - E)), RT)
N = 48
pts = [(BR - 0.3) * math.cos(2 * math.pi * (k + 0.5) / N) for k in range(N)], [(BR - 0.3) * math.sin(2 * math.pi * (k + 0.5) / N) for k in range(N)]
for k in range(N):
    a, b = (pts[0][k], pts[1][k]), (pts[0][(k + 1) % N], pts[1][(k + 1) % N])
    if (a[1] + b[1]) / 2 < 0 and abs((a[0] + b[0]) / 2) < 2.0: continue     # the flight's arrival
    bal.run(a, b, SB)
PD = SB + DH                               # the peristyle's deck
bal.ring(0, 0, R + DT + PW - 0.4, PD, n=48)
parts.update(bal.parts("balustrade")); build += list(bal.parts("balustrade").keys())

# ---- THE STATUES: the apostles on the pediments, the angels with lamps on the attic's corners, Hermann's 24 angels over
# the colonnade (all bronze)
st = {}
tan20 = math.tan(math.radians(20))
for nm, (ox, oz, ux, uz, W, face) in {"south": (BX + NS_D - 0.6, 0, 0, 1, 7 * NS_SP + 4 * 0.92 + 1, FACE_PX),
                                      "north": (-(BX + NS_D - 0.6), 0, 0, 1, 7 * NS_SP + 4 * 0.92 + 1, FACE_NX),
                                      "west": (0, BZ + WE_D - 0.6, 1, 0, 7 * WE_SP + 4 * 0.92 + 1, FACE_PZ),
                                      "east": (0, -(BZ + WE_D - 0.6), 1, 0, 7 * WE_SP + 4 * 0.92 + 1, FACE_NZ)}.items():
    top = FL + 17.0 + 3.8
    st[f"apostle {nm} apex"] = statue((ox, top + W / 2 * tan20 + 0.2, oz), kind="man", style="roman", hold={"L": "items/tools/book"}, stone="bronze", scale=2.4, seed=len(st) + 3, face=face)
    for s in (-1, 1):
        u = s * (W / 2 - 1.2)
        st[f"apostle {nm} {'a' if s < 0 else 'b'}"] = statue((ox + ux * u, top, oz + uz * u), kind="man", style="roman",
                                                            hold={"R": "items/tools/staff"} if s < 0 else {"L": "items/tools/book"}, stone="bronze", scale=2.2, seed=len(st) + 5, face=face)
for sx in (-1, 1):
    for sz in (-1, 1):
        st[f"lamp angel {sx} {sz}"] = statue((sx * (BX - 0.9), RT + 1.2, sz * (BZ - 0.9)), kind="woman", style="roman", wings="raised", hold={"R": "items/tools/torch"},
                                             stone="bronze", scale=2.0, seed=40 + len(st), face=FACE_PZ if sz > 0 else FACE_NZ)
RA = R + DT + PW                           # over the columns
for k in range(24):
    a = 2 * math.pi * k / 24
    st[f"angel {k}"] = statue((RA * math.sin(a), PD + 0.2, RA * math.cos(a)), kind="woman", style="roman", wings="folded" if k % 2 else "raised",
                              hold={"R": "items/tools/torch"} if k % 3 == 0 else {}, stone="bronze", scale=2.0, seed=60 + k, face=a - Q)
for k, v in capped(st).items(): add(k, v)

doc = {"name": "St Isaac's Cathedral",
       "_about": "ST ISAAC'S CATHEDRAL, St Petersburg (Montferrand, 1818-58), from its ground plan, OSM and the cross-section: the grey marble body on its granite podium, "
                 "a giant Corinthian order round it; four porticoes of red granite monoliths (north and south of sixteen, east and west of eight) under pediments with "
                 "their bronze reliefs and apostles; four corner towers, the north-west and south-east ones holding spiral stairs to the flat roof, each under a square belfry "
                 "with a small gilded dome; the round stylobate to the colonnade walk at 43 m (a flight from the roof), the drum ringed by 24 columns with Hermann's angels "
                 "on its balustrade, the attic, the gilded dome and its lantern, the cross at 101.5 m. Inside: three naves under barrel vaults crossed by the north-south arm, "
                 "the dome on pendentives over the crossing, the iconostasis with its malachite and lapis columns, the sanctuary with the stained-glass Resurrection.",
       "params": {"detail": 4}, "base": {"height": 0.3, "steps": 1, "stepOut": 0, "margin": 4}, "railing": {"type": "iron"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/st-isaacs.json"), "w").write(json.dumps(doc, indent=2) + "\n")

# ---- THE FINISH
MALACHITE = ["#1f6b4a", "#0e4a32", "#3f9a6c", "#0a2f20"]
LAPIS = ["#26408b", "#1a2d66", "#3a5bb8", "#c9a24a"]
FLOOR = ["#9a9a96", "#b9b7b2", "#c98f8a", "#7e2f33"]     # grey Ruskeala, pink and cherry Tivdia
WHITE = ["#efece4", "#e2ddd2", "#d8d2c4", "#c9c2b0"]     # the white Italian marble of the walls
GILT = ["#f3ecd8", "#d9b45a", "#b88f2e", "#efe6cc"]      # the vaults: white and gold
PINK = ["#c98f8a", "#b07069", "#7e2f33", "#e2bdb5"]
PIERS = ["#ece6da", "#d9aaa2", "#e0d8c8", "#b9817a"]
BRONZE = ["#5b4a2e", "#3e3220", "#7a6440", "#2c2416"]
GREY = ["#a8a59d", "#9a978f", "#b3b0a8", "#8f8c85"]     # the grey Ruskeala marble outside
STATUES = [k for k in st if k in parts]
col = lambda name, *ks: [f"{name} {k}" for k in ks]
fin = {"name": "St Isaac's Cathedral", "building": "architecture/st-isaacs",
       "_about": "St Isaac's: walls of light grey Ruskeala marble, the podium and steps grey granite, the portico and colonnade columns red granite, the domes gilded, "
                 "the roofs grey sheet metal, the statues and pediment reliefs dark bronze. Inside: white Italian marble walls, pink and cherry marble columns, floors of grey "
                 "Ruskeala with pink and cherry, gilded and painted vaults, the dome painted, the iconostasis in gilt and mosaic icons, malachite and lapis columns, "
                 "the stained-glass Resurrection in the apse window.",
       "stone": {"color": "#a8a59d", "accent": "#94918a", "pat": "ashlar"},
       "rules": [
           {"parts": "kind:glass", "within": [-4, -46, 4, -42], "map": "opening", "pattern": "glass/window passion", "palette": "chartres",
            "_about": "the stained-glass Resurrection in the apse window"},
           {"parts": STATUES, "pattern": "materials/metal", "palette": BRONZE, "_about": "the bronze apostles and angels"},
           {"parts": ["portico south/pediment", "portico north/pediment", "portico west/pediment", "portico east/pediment"], "surface": "wall",
            "pattern": "stone/candi reliefs", "palette": BRONZE, "_about": "the pediments' bronze reliefs: the Resurrection (north), the Adoration of the Magi (south), "
                                                                         "St Isaac meeting Theodosius (west), St Isaac stopping Valens (east)"},
           {"parts": col("iconostasis malachite", "shafts"), "pattern": "stone/marble", "palette": MALACHITE, "_about": "the malachite columns"},
           {"parts": col("iconostasis lapis", "shafts"), "pattern": "stone/marble", "palette": LAPIS, "_about": "the lapis-lazuli columns"},
           {"parts": col("iconostasis malachite", "bases", "capitals", "abaci") + col("iconostasis lapis", "bases", "capitals", "abaci") + ["iconostasis cornice"],
            "pattern": "roofs/gold leaf", "_about": "their gilt bases and capitals, the gilt entablature over them"},
           {"parts": ["iconostasis"], "surface": "wall", "pattern": "mosaic/wall apostles", "scale": 2.5, "_about": "the iconostasis: its icons (mosaic) in tiers"},
           {"parts": ["altar", "solea"], "pattern": "stone/marble", "palette": "marble-rose"},
           {"parts": ["kind:dome"], "side": "in", "pattern": "painted/caisson", "palette": GILT, "_about": "the dome's inside painted and gilt (Bryullov's Virgin in glory)"},
           {"in": "dome/ribbed lantern", "pattern": "roofs/gold leaf", "_about": "the gilded lantern"},
           {"in": "belfry domes/ribbed lantern", "pattern": "roofs/gold leaf"},
           {"parts": ["kind:dome", "dome/ribs", "belfry domes/ribs", "dome/lantern ball", "dome/lantern cross", "dome/lantern cross arm", "dome/lantern spire",
                      "belfry domes/lantern ball", "belfry domes/lantern cross", "belfry domes/lantern cross arm", "belfry domes/lantern spire"]
                     + col("dome/lantern columns", "bases", "shafts", "capitals", "abaci"),
            "pattern": "roofs/gold leaf", "_about": "the gilded domes, their ribs, the lanterns and crosses"},
           {"parts": ["kind:roof"], "surface": "roof", "pattern": "roofs/sheet metal", "palette": "lead", "_about": "the pediments' roofs in grey sheet metal"},
           {"parts": [f"portico {n}/columns shafts" for n in ("south", "north", "west", "east")] + ["portico south rows shafts", "portico north rows shafts", "dome/peristyle shafts"],
            "pattern": "stone/granite", "palette": "granite-red", "_about": "the red granite monoliths of the porticoes and the drum's colonnade"},
           {"parts": [f"portico {n}/columns {k}" for n in ("south", "north", "west", "east") for k in ("bases", "capitals", "abaci")]
                     + col("portico south rows", "bases", "capitals", "abaci") + col("portico north rows", "bases", "capitals", "abaci"),
            "pattern": "materials/metal", "palette": BRONZE, "_about": "their bronze bases and capitals"},
           {"surface": "floor", "side": "in", "pattern": "floors/opus sectile", "palette": FLOOR, "_about": "the floors of grey Ruskeala with pink and cherry marble"},
           {"parts": ["podium", "steps south", "steps north", "steps west", "steps east", "base"], "pattern": "stone/granite", "palette": "granite",
            "_about": "the granite podium and steps"},
           {"parts": ["kind:barrel", "pendentives"], "side": "in", "pattern": "painted/caisson", "palette": GILT, "_about": "the coffered vaults, white and gold"},
           {"parts": ["kind:column"], "side": "in", "pattern": "stone/marble", "palette": PINK},
           {"surface": "ceiling", "side": "in", "pattern": "painted/caisson", "palette": GILT},
           {"parts": ["pier line north", "pier line south", "crossing wall west", "crossing wall east", "west bay wall", "sanctuary wall"], "surface": "wall",
            "pattern": "stone/revetment", "palette": PIERS, "_about": "the piers sheathed in white marble, framed in pink and cherry Tivdia marble"},
           {"surface": "wall", "side": "in", "pattern": "stone/revetment", "palette": WHITE, "_about": "the walls inside in white Italian marble on a dark base"},
           {"surface": "floor", "pattern": "stone/granite", "palette": "granite", "_about": "the porches, the roof walks and the colonnade walk"},
           {"parts": ["colonnade stair railing"], "pattern": "stone/ashlar fine", "palette": GREY, "_about": "the flight's stone parapets"},
           {"parts": ["kind:moulding"], "pattern": "stone/ashlar fine", "palette": GREY},
           {"surface": "ceiling", "pattern": "stone/ashlar fine", "palette": GREY},
           {"surface": "wall", "pattern": "stone/ashlar fine", "palette": GREY, "_about": "the grey Ruskeala marble walls"}]}
open(os.path.join(ROOT, "assets/finishes/st-isaacs.json"), "w").write(json.dumps(fin, indent=2) + "\n")

if __name__ == "__main__":
    print("st-isaacs:", len(parts), "parts,", len(STATUES), "statues")
