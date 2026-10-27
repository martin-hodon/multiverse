# ULM MINSTER (Ulmer Münster, Gothic, 1377-1890), from components: the world's tallest church steeple -- ONE WEST
# TOWER, 161.5m: four square `gothic-tower-stage`s (the porch hall with its triple portal at the foot, then storeys of
# tall traceried windows, the last under a parapet and pinnacles: the gallery at 70m), each climbed by its own
# `tower-stair` turret; then the openwork `gothic-octagon-stage` to 100m and the `gothic-spire`, cut off at the
# viewing gallery at 143m, through both of which one round stair (`round-stair-tower`) winds up the middle to that
# gallery and the belvedere and stone cap over it. The FIVE-AISLED BASILICA -- the `basilica` nave (arcades,
# clerestory, rib vault) with DOUBLE aisles either side, split by a row of slender columns under rib vaults of their
# own, flying buttresses over them -- and the CHOIR with its polygonal `apse`, flanked by the TWO EAST TOWERS, square
# stages, an octagon and a spire to 86m.
#   The west front faces +z. This script also writes the three components it introduces:
#     components/gothic-tower-stage.json   one square storey of a Gothic tower (walls, buttresses, pinnacles, stair)
#     components/gothic-octagon-stage.json the octagonal storey over a square tower, tall openings in every face
#     components/gothic-spire.json         the octagonal spire: ribs on its edges, gables at its foot, pinnacles round it
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMP = os.path.join(ROOT, "assets/architecture/components")
PI = 3.14159265
Q = math.pi / 2
pointed = lambda spread=1: {"profile": "pointed", "spread": spread}

# ================================================================ the components
# ---- GOTHIC TOWER STAGE: one square storey, stacked to build a tower
def stage_walls(door_faces):
    """the storey's walls: a blind lower band (`low`) and tall pointed windows over it; `door_faces` get openings
    in the lower band -- face 0 (+z) the arcade of `doorN` arches, face 2 (-z) one door `backW` wide"""
    upper = {"openings": {"pattern": "wins", "width": "winW", "gap": "winGap", "sill": "winSill", "springing": "winSpring",
                          "head": pointed(), "tracery": {"lights": "lights"}}, "glass": "glazed"}
    d = {"type": "enclosure", "plan": {"rect": ["W", "W"]}, "thickness": "t", "height": "H",
         "tiers": [{"h": "low", "openings": []}, upper], "at": [[0, 0, 0, 0]]}
    faces = {}
    if 0 in door_faces:
        faces["0"] = [{"h": "low", "openings": {"pattern": "doorN", "width": "doorW", "gap": "doorGap", "sill": 0, "springing": "doorSpring",
                                                "head": pointed()}, "glass": False}, upper]
    if 2 in door_faces:
        faces["2"] = [{"h": "low", "openings": {"pattern": "1", "width": "backW", "sill": 0, "springing": "backSpring", "head": pointed()},
                       "glass": False}, upper]
    if faces: d["faces"] = faces
    return d
# the buttresses: two at every corner, one continuing each face out (`bd` proud of it, `bw` wide); the FRONT ones are
# the four at the +z corners (a tower whose back stands against a nave has none there)
corners = [(sx, sz) for sz in (1, -1) for sx in (1, -1)]
def butt_at(sx, sz):
    return [[f"{sx} * (W / 2 - bw / 2)", 0, f"{sz} * (W / 2 + bd / 2)", 0, "bw", "bd"],
            [f"{sx} * (W / 2 + bd / 2)", 0, f"{sz} * (W / 2 - bw / 2)", 0, "bd", "bw"]]
def buttresses(cs):
    ws = [b for c in cs for b in butt_at(*c)]
    # two boxes (along x / along z), so each keeps its own proportions
    return ({"type": "box", "width": "bw", "length": "bd", "height": "H", "at": [b[:4] for b in ws if b[4] == "bw"]},
            {"type": "box", "width": "bd", "length": "bw", "height": "H", "at": [b[:4] for b in ws if b[4] == "bd"]})
def pinnacles(cs):
    return {"type": "component", "use": "components/pinnacle", "params": {"w": "pinW", "h": "pinH", "s": "pinS"},
            "at": [[b[0], "H", b[2], 0] for c in cs for b in butt_at(*c)]}
sparts = {}
sparts["walls"] = {**stage_walls(()), "_about": "the storey's walls: a blind band below, tall pointed windows (`wins` to a face) over it"}
sparts["walls door"] = {**stage_walls((0,)), "_about": "...or with `doorN` arches in the band below on the +z face"}
sparts["walls portal"] = {**stage_walls((0, 2)), "_about": "...or the porch: the arcade in front and a portal `backW` wide through the back"}
bx, bz = buttresses(corners)
sparts["buttresses"] = {**bx, "_about": "two buttresses at every corner, one continuing each face (`bd` proud, `bw` wide)"}
sparts["buttresses side"] = bz
fx, fz = buttresses(corners[:2])
sparts["front buttresses"] = {**fx, "_about": "...or only the four at the +z corners (a tower whose back stands against a nave)"}
sparts["front buttresses side"] = fz
sparts["pinnacles"] = {**pinnacles(corners), "_about": "a pinnacle on every buttress's head"}
sparts["front pinnacles"] = pinnacles(corners[:2])
sparts["corner pinnacles"] = {"type": "component", "use": "components/pinnacle", "params": {"w": "pinW", "h": "pinH", "s": "pinS"},
                              "at": [[f"{sx} * (W / 2 - pinW / 2)", "H", f"{sz} * (W / 2 - pinW / 2)", 0] for sx, sz in corners],
                              "_about": "a pinnacle on each corner of the walls' head"}
sparts["parapet"] = {"type": "enclosure", "plan": {"rect": ["W", "W"]}, "thickness": 0.4, "height": "parapetH", "openings": [],
                     "at": [[0, "H", 0, 0]], "_about": "the parapet round the walls' head (the gallery behind it)"}
sparts["stair"] = {"type": "component", "use": "components/tower-stair",
                   "params": {"W": "W - 2 * t", "H": "H", "tR": "tR", "tx": "tx", "tz": "tz", "hand": "hand", "n": "n"},
                   "at": [[0, 0, 0, 0]],
                   "_about": "the stair up this storey (`tower-stair`): a turret at (tx, tz), its door on the floor below, the floor at the top round its head. Stacked stages put their turrets in different corners"}
sparts["slab"] = {"type": "box", "width": "W - 2 * t + 0.2", "length": "W - 2 * t + 0.2", "height": 0.4, "at": [[0, "H - 0.4", 0, 0]],
                  "flatRoof": True, "_about": "...or a plain slab closing the storey's head, not walked (a tower not climbed)"}
STAGE = {"name": "Gothic tower stage",
         "_about": "ONE SQUARE STOREY OF A GOTHIC TOWER, stacked to build one: walls `W` square and `H` high, a blind band (`low`) and over it tall pointed windows, `wins` to a face (open with `glazed` 0: a belfry); the walls may instead have an arcade of `doorN` arches in the band on the +z face (`walls door`) and a portal through the back as well (`walls portal`: the porch hall); two buttresses at every corner (`buttresses`, or only at the +z corners, `front buttresses`), pinnacles on them (`pinnacles` / `front pinnacles`) or on the walls' corners (`corner pinnacles`), a `parapet`; and the storey's STAIR -- a `tower-stair` turret at (`tx`, `tz`) from this storey's floor to the floor at its head, cut round the turret -- or a plain `slab`. Place it at its middle, at its floor. Ulm's west tower is four of these, each turret in another corner.",
         "params": {"detail": 4, "W": 20.0, "H": 18.0, "t": 1.6, "low": "H * 0.25",
                    "wins": 2, "winW": 2.4, "winGap": 2.4, "winSill": 1.0, "winSpring": "H - low - 1.4 - winW * 0.8661", "glazed": 1, "lights": 0,
                    "doorN": 1, "doorW": 3.0, "doorGap": 1.6, "doorSpring": "low - 1.0 - doorW * 0.8661",
                    "backW": 4.0, "backSpring": "low - 1.0 - backW * 0.8661",
                    "bw": 2.0, "bd": 1.8, "pinW": "min(bw, bd) * 0.8", "pinH": 3.0, "pinS": 5.0, "parapetH": 1.2,
                    "tR": 2.1, "c": "W / 2 - t - tR - 0.05", "tx": "c", "tz": "c", "hand": "right", "n": 8,
                    "_winSpring": "the windows' springing over the band: their heads (equilateral) end 1.4m under the storey's top",
                    "_c": "a turret touching two walls in the (+x, +z) inner corner; tx, tz place it",
                    "_lights": "the windows' tracery (tracery.js): how many lights, 0 for none -- glazed or open"},
         "build": ["walls", "buttresses", "buttresses side", "stair"], "parts": sparts}

# ---- GOTHIC OCTAGON STAGE: the octagonal storey over a square tower
def oct_walls(door):
    upper = {"openings": [{"at": 0, "width": "winW", "sill": "winSill", "springing": "winSpring", "head": pointed(), "tracery": {"lights": "lights"}}], "glass": "glazed"}
    d = {"type": "enclosure", "plan": {"sides": 8, "radius": "R"}, "thickness": "t", "height": "H",
         "tiers": [{"h": "low", "openings": []}, upper], "at": [[0, 0, 0, 0]]}
    if door:
        d["faces"] = {"0": [{"h": "low", "openings": [{"at": 0, "width": "doorW", "sill": 0, "springing": "doorSpring", "head": pointed()}],
                             "glass": False}, upper]}
    return d
OCT = {"name": "Gothic octagon stage",
       "_about": "THE OCTAGONAL STOREY OF A GOTHIC TOWER, over its square stages and under its spire: eight walls (`R` to the corners, `t` thick, `H` high), a band below and a tall lancet in every face -- open tracery with `glazed` 0; `walls door` has a door in the band of face 0; `slab` closes its head (not walked). Place it at its middle on the square tower's head; the spire (`gothic-spire`) stands on its walls.",
       "params": {"detail": 4, "R": 7.0, "H": 30.0, "t": 1.0, "low": 4.0, "winW": "R * 0.36", "winSill": 1.0,
                  "winSpring": "H - low - 1.5 - winW * 0.8661", "glazed": 0, "lights": 0, "doorW": 1.6, "doorSpring": 2.4,
                  "_lights": "the lancets' tracery (tracery.js): how many lights, 0 for none -- open, an openwork stage's"},
       "build": ["walls"],
       "parts": {"walls": {**oct_walls(False), "_about": "eight walls, a tall lancet in each over a blind band"},
                 "walls door": {**oct_walls(True), "_about": "...or with a door in the band of face 0"},
                 "slab": {"type": "prism", "plan": {"sides": 8, "radius": "R - t * 0.6"}, "height": 0.4, "at": [[0, "H - 0.4", 0, 0]],
                          "flatRoof": True, "_about": "a slab closing the head, its edge buried in the walls"}}}

# ---- GOTHIC SPIRE
SPIRE = {"name": "Gothic spire",
         "_about": "A GOTHIC SPIRE: an octagonal (`sides`) stone spire `R` to its corners and `rise` to its tip -- a straight cone (`profile` trigonal) whose sides would meet at `rise` -- cut off where it has narrowed to `topR` -- a small head for its `finial`, or wide enough for a gallery or a lantern to stand on; crocketed RIBS on its edges, a GABLE (Wimperg) at its foot on every face, and a PINNACLE at each corner round it. Place it on the head of the stage it crowns (a `gothic-octagon-stage`); gables and pinnacles stand on that stage's walls. It is a hollow shell of stone: a stair may climb inside it.",
         "params": {"detail": 4, "sides": 8, "R": 6.0, "rise": 40.0, "profile": "trigonal", "topR": "R * 0.12", "shellT": "R * 0.05",
                    "ribW": "R * 0.07", "ribD": "R * 0.05",
                    "gW": "R * 0.6", "gR": "R * 0.84", "gPitch": 62,
                    "pinR": "R * 1.02", "pinW": "R * 0.2", "pinH": "R * 0.5", "pinS": "R * 0.9", "finial": "R * 0.35",
                    "_rise": "where its sides would meet: it is cut off at radius `topR` (a small flat head for the finial, or a gallery's width)",
                    "_shellT": "the spire's stone: a shell, hollow inside (a stair may climb in it)",
                    "_gR": "the gables' radius: on the faces, over the walls under the spire's foot",
                    "_pinR": "the pinnacles' radius, at the corners"},
         "build": ["spire", "ribs", "gables", "pinnacles"],
         "parts": {"spire": {"type": "dome", "sides": "sides", "radius": "R", "thickness": "shellT", "oculus": "topR",
                             "head": {"profile": "profile", "rise": "rise"}, "at": [[0, 0, 0, 0]],
                             "_about": "the spire: a stone shell of `sides` webs, hollow"},
                   "ribs": {"type": "ribs", "on": "spire", "width": "ribW", "depth": "ribD", "standsOn": ["spire"],
                            "_about": "the crocketed ribs on its edges"},
                   "gables": {"type": "roof", "form": "gable", "width": "gW", "length": 0.5, "pitch": "gPitch",
                              "spiral": {"count": "sides", "radius": "gR", "y": 0},
                              "_about": "a gable at the foot of every face, turned to face out"},
                   "pinnacles": {"type": "component", "use": "components/pinnacle", "params": {"w": "pinW", "h": "pinH", "s": "pinS"},
                                 "spiral": {"count": "sides", "radius": "pinR", "y": 0, "turn": "3.14159265 / sides"},
                                 "_about": "a pinnacle at every corner round its foot"},
                   "finial": {"type": "column", "radius": "topR * 0.9", "height": "finial", "sides": 6, "at": [[0, 0, 0, 0]], "atop": "spire", "atopR": "topR",
                              "standsOn": ["spire"], "_about": "the finial on its head"}}}

for nm, doc in (("gothic-tower-stage", STAGE), ("gothic-octagon-stage", OCT), ("gothic-spire", SPIRE)):
    open(os.path.join(COMP, nm + ".json"), "w").write(json.dumps(doc, indent=2) + "\n")

# ================================================================ the minster
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}

BAYS, BAY = 8, 8.5
NL = BAYS * BAY                            # the nave, 68m, from z = -34 (east) to +34 (west)
NW, PT, AW, AT = 15.2, 2.0, 13.3, 1.5      # nave, arcade walls, each DOUBLE aisle, aisle walls
BODY = NW + 2 * PT + 2 * AW + 2 * AT       # 48.8
HB = NW / 2 + PT                           # the arcade's outer face
SPR = 9.0                                  # the arcade's springing
CROWN = SPR + (BAY - PT) / 2 * 1.7321      # its crown
SUB = AW / 2                               # each of the two aisles on a side
SUB_RISE = SUB / 2 * 1.7321
AISLE_TOP = CROWN + SUB_RISE + 0.6
AISLE_WALL = AISLE_TOP + 1.2
ARC_H, CLEAR_H = 25.0, 31.5
NAVE_SPREAD = 0.5
NAVE_RISE = NW / 2 * math.sqrt(1 + 2 * NAVE_SPREAD)
NAVE_TOP = CLEAR_H + NAVE_RISE + 1.2       # 43.9: the vault's crown inside at 42.7 (41.6 on the real one)
along = lambda half_across, spread: ((1 + 2 * spread) * (half_across / (BAY / 2)) ** 2 - 1) / 2   # the lancet along a bay meeting the crown
Z0 = NL / 2

P = {"detail": 4}
add("nave", comp("basilica", {"bays": BAYS, "bayLen": BAY, "naveW": NW, "aisleW": AW, "pierT": PT, "aisleT": AT, "openW": BAY - PT,
                              "spring": SPR, "crown": round(CROWN, 4), "arcadeH": ARC_H, "clearH": CLEAR_H, "naveTop": round(NAVE_TOP, 4),
                              "aisleSpring": round(CROWN, 4), "aisleTop": round(AISLE_TOP, 4),
                              "arch": "pointed", "arcSpread": 1, "naveSpread": NAVE_SPREAD, "clearSpread": 1,
                              "naveAlongArch": "pointed", "naveAlongSpread": round(along(NW / 2, NAVE_SPREAD), 4),
                              "clearWinW": 2.8, "clearLights": 2, "clearSill": 2.4, "clearSpring": 5.6},
                 [[0, 0, 0, 0]], build=["arcade", "clerestory", "nave vault", "nave ribs"],
                 _about="the high nave from the `basilica` definition: pointed arcades, clerestory, and the rib vault 42m up"))
# ---- the DOUBLE aisles: tall windows in the outer walls, a row of slender columns down each, and rib vaults over both
HA = HB + AW                               # the aisle wall's inner face
add("aisle walls", {"type": "wall", "width": NL, "height": round(AISLE_WALL, 4), "thickness": AT,
                    "openings": {"pattern": str(BAYS), "width": 4.0, "gap": BAY - 4.0, "sill": 3.5, "springing": 13.0, "head": pointed(), "tracery": True},
                    "at": [[HA + AT, 0, 0, Q], [-HA - AT, 0, 0, -Q]],
                    "_about": "the outer walls of the double aisles, a tall traceried window in every bay"})
add("aisle columns", {"type": "column", "radius": 0.55, "height": round(CROWN, 4), "sides": 12,
                      "at": [[sx * (HB + SUB), 0, Z0 - BAY * k, 0] for sx in (-1, 1) for k in range(1, BAYS)],
                      "_about": "the slender columns splitting each aisle in two (the five aisles)"})
av = {"type": "groin", "width": SUB, "length": BAY, "springing": round(CROWN, 4), "top": round(AISLE_TOP, 4),
      "across": pointed(1), "along": pointed(round(along(SUB / 2, 1), 4))}
add("aisle vaults", {**av, "at": [[sx * (HB + SUB * (i + 0.5)), 0, Z0 - BAY / 2 - BAY * k, 0] for sx in (-1, 1) for i in (0, 1) for k in range(BAYS)],
                     "_about": "a rib vault over each bay of each of the four aisles"})
add("aisle ribs", {"type": "ribs", "on": "aisle vaults", "width": 0.35, "depth": 0.25, "wall": {"width": 0.45, "depth": 0.3}})
AE_W = BODY / 2 - HB
add("aisle east walls", {"type": "wall", "width": AE_W, "height": round(AISLE_WALL, 4), "thickness": AT, "openings": [],
                         "at": [[sx * (HB + AE_W / 2), 0, -Z0, 0] for sx in (-1, 1)],
                         "_about": "the aisles' east ends, the east towers against them"})
TW, TT = 21.0, 1.6                         # the west tower: 21m square, walls 1.6
AW_W = BODY / 2 - TW / 2
add("aisle west walls", {"type": "wall", "width": AW_W, "height": round(AISLE_WALL, 4), "thickness": AT,
                         "openings": {"pattern": "1", "width": 3.2, "sill": 0, "springing": 5.0, "head": pointed()},
                         "at": [[sx * (TW / 2 + AW_W / 2), 0, Z0 + AT, 0] for sx in (-1, 1)],
                         "_about": "the aisles' west ends either side of the tower, a portal in each"})
# ---- roofs
RIDGE = (NW / 2 + PT + 0.3) * math.tan(math.radians(55))
add("nave roof", {"type": "roof", "form": "gable", "width": NW + 2 * PT + 0.6, "length": NL, "pitch": 55, "at": [[0, round(NAVE_TOP, 4), 0, 0]],
                  "_about": "the steep grey-tiled roof of the high nave"})
AR_W = BODY / 2 - HB
add("aisle roofs", {"type": "roof", "form": "shed", "width": AR_W, "length": NL + AT, "pitch": 15,
                    "at": [[-(HB + AR_W / 2), round(AISLE_WALL, 4), AT / 2, 0], [HB + AR_W / 2, round(AISLE_WALL, 4), AT / 2, PI]],
                    "_about": "a lean-to over each pair of aisles"})
# ---- flying buttresses over the double aisles, at every bay's end
FX = BODY / 2 + 1.2
fb = {"pierH": 27.5, "span": round(FX - HB, 4), "low": 24.0, "high": CLEAR_H - 1.0, "top0": 26.8, "top1": CLEAR_H + 2.2, "pinH": 3.5, "pinS": 5.0}
add("flying buttresses", comp("components/flying-buttress", fb, [[FX, 0, -Z0 + BAY, PI], [-FX, 0, -Z0 + BAY, 0]],
                              repeat={"count": BAYS - 1, "step": [0, 0, BAY, 0]},
                              _about="a flying buttress at every bay's end, both sides, clearing the double aisles to the clerestory"))

# ---- the CHOIR, its apse, and the gable over the chancel arch
CW, CL, CT, CH = NW + 2 * PT, 26.0, 1.6, 27.0
CZ = -Z0 - CL / 2
lan = lambda at: {"at": at, "width": 2.6, "sill": 4.0, "springing": 16.0, "head": pointed()}
add("choir", {"type": "enclosure", "plan": {"rect": [CW, CL]}, "thickness": CT, "height": CH,
              "faces": {"0": [{"at": 0, "width": NW - 1.0, "sill": 0, "springing": 15.0, "head": pointed(0.6)}],
                        "1": [lan(2.5), lan(8.5)], "3": [lan(-2.5), lan(-8.5)],
                        "2": [{"at": 0, "width": CW - 2 * CT - 1.0, "sill": 0, "springing": 8.0, "head": pointed(0.3)}]},
              "openings": [], "at": [[0, 0, CZ, 0]],
              "_about": "the choir, open to the nave by the chancel arch and to its apse, tall lancets in its flanks east of the towers"})
add("chancel gable", {"type": "wall", "width": CW, "height": round(NAVE_TOP - CH, 4), "thickness": CT, "openings": [],
                      "at": [[0, CH, -Z0, 0]], "_about": "the wall over the chancel arch, closing the nave's east end above the choir"})
AR = CW / 2 - CT
add("apse", comp("components/apse", {"R": AR, "T": CT, "H": CH, "n": 16, "winW": 2.4, "winSill": 4.0, "winH": 12.0, "winHead": "pointed",
                                     "profile": "trigonal", "rise": 15.0, "domeT": 0, "over": 0.5},
                 [[0, 0, -Z0 - CL, PI]], _about="the polygonal apse, a tall lancet in each bay, under its half cone (`apse`)"))
add("choir roof", {"type": "roof", "form": "gable", "width": CW + 1.0, "length": CL - CT, "pitch": 57, "at": [[0, CH, CZ - CT / 2, 0]],
                   "_about": "the choir's roof, from the back of the chancel gable to the apse"})

# ---- the TWO EAST TOWERS, either side of the choir against the aisles' east walls: square, octagon, spire, 86m
ETW, ETT = 8.5, 1.1
EX, EZ = CW / 2 + ETW / 2, -Z0 - AT - ETW / 2
es = lambda **kw: {"W": ETW, "t": ETT, "wins": 1, "winW": 1.6, "bw": 1.2, "bd": 1.0, **kw}
for sx, nm in ((1, "south"), (-1, "north")):
    yaw = sx * Q                                          # face 0 turned outward
    add(f"{nm} east tower foot", comp("components/gothic-tower-stage", es(H=26.0, low=6.0, doorN=1, doorW=1.8),
                                      [[sx * EX, 0, EZ, yaw]], build=["walls door", "slab"],
                                      **({"_about": "the east towers (`gothic-tower-stage` twice, a `gothic-octagon-stage`, a `gothic-spire`): the foot, a door at the side..."} if sx > 0 else {})))
    add(f"{nm} east tower belfry", comp("components/gothic-tower-stage", es(H=20.0, low=3.0, glazed=0, pinW=1.0, pinH=2.0, pinS=3.5),
                                        [[sx * EX, 26.0, EZ, yaw]], build=["walls", "corner pinnacles", "slab"],
                                        **({"_about": "...the open belfry, pinnacles on its corners..."} if sx > 0 else {})))
    add(f"{nm} east tower octagon", comp("components/gothic-octagon-stage", {"R": 3.8, "H": 14.0, "t": 0.7, "low": 2.0},
                                         [[sx * EX, 46.0, EZ, 0]], **({"_about": "...the octagon..."} if sx > 0 else {})))
    add(f"{nm} east tower spire", comp("components/gothic-spire", {"R": 3.4, "rise": 26.0, "finial": 3.0, "pinR": 3.4},
                                       [[sx * EX, 60.0, EZ, 0]], build=["spire", "ribs", "gables", "pinnacles", "finial"],
                                       **({"_about": "...and the ribbed spire with its gables and pinnacles, to 86m"} if sx > 0 else {})))

# ---- the WEST TOWER: four square stages, the octagon, the spire and the gallery at 143m
TZ = Z0 + TW / 2
C = TW / 2 - TT - 2.1 - 0.05               # a turret's middle in an inner corner
ws = lambda **kw: {"W": TW, "t": TT, "bw": 2.6, "bd": 2.4, **kw}
STAGES = [  # (y, H, what, turret corner, parts)
    (0.0, 20.0, dict(low=15.0, wins=2, winW=2.2, winGap=4.0, lights=2, doorN=3, doorW=4.2, doorGap=1.4, backW=6.0),
     (1, -1), ["walls portal", "front buttresses", "front buttresses side", "stair"],
     "the PORCH HALL at the tower's foot: the triple portal open to the west, the minster's portal through its back into the nave, its stair turret in a back corner..."),
    (20.0, 18.0, dict(low=3.0, wins=2, winW=3.6, winGap=1.6, lights=3), (-1, -1), ["walls", "front buttresses", "front buttresses side", "stair"],
     "...the storey of the great west windows..."),
    (38.0, 18.0, dict(low=3.0, wins=2, winW=3.4, winGap=1.8, lights=3), (-1, 1), ["walls", "front buttresses", "front buttresses side", "stair"],
     "...a third, each climbed by its own turret, in another corner..."),
    (56.0, 14.0, dict(low=2.0, wins=2, winW=3.2, winGap=2.0, lights=3, glazed=0, pinW=1.8, pinH=4.0, pinS=6.0),
     (1, 1), ["walls", "front buttresses", "front buttresses side", "front pinnacles", "corner pinnacles", "parapet", "stair"],
     "...and the open belfry, its head the FIRST GALLERY at 70m behind a parapet and pinnacles, round the octagon's foot"),
]
for i, (y, h, kw, (cx, cz), bl, about) in enumerate(STAGES):
    add(f"west tower stage {i + 1}", comp("components/gothic-tower-stage", ws(H=h, tx=round(cx * C, 4), tz=round(cz * C, 4), **kw),
                                          [[0, y, TZ, 0]], build=bl, _about=about))
OCT_R, OCT_Y, OCT_H = 7.0, 70.0, 30.0
add("west tower octagon", comp("components/gothic-octagon-stage", {"R": OCT_R, "H": OCT_H, "t": 1.0, "low": 4.0, "lights": 2},
                               [[0, OCT_Y, TZ, 0]], build=["walls door"],
                               _about="the openwork OCTAGON from the gallery to 100m, a tall lancet in every face and a door from the gallery"))
# the spire: a lancet turned, so its sides stay nearly straight to the tip at 161.5m, cut off at the viewing gallery
SP_Y, SP_R, TIP, GAL = OCT_Y + OCT_H, 6.2, 161.5, 143.0
SLAB = 0.4
CUT, TOP_R = GAL - SLAB - SP_Y, 3.3
V_RISE = CUT * SP_R / (SP_R - TOP_R)       # where its sides would meet
add("west tower spire", comp("components/gothic-spire", {"R": SP_R, "rise": round(V_RISE, 4),
                                                         "topR": TOP_R, "pinR": 6.6, "pinW": 1.2, "pinH": 3.0, "pinS": 6.0},
                             [[0, SP_Y, TZ, 0]],
                             _about="the openwork SPIRE on the octagon, ribbed, gabled and ringed by pinnacles at its foot (`gothic-spire`), cut off at the viewing gallery"))
# the stair up the middle of octagon and spire: 384 steps from the gallery at 70m to the one at 143m, arriving in the
# belvedere at the top, whose stone cap and finial are the spire's crown
SR = 2.2
add("west tower stair", comp("components/round-stair-tower", {"R": SR, "wall": 0.4, "H": GAL - OCT_Y, "n": 10, "doorBay": 0,
                                                              "stageH": 3.4, "capRise": 12.0, "finial": 2.8},
                             [[0, OCT_Y, TZ, 0]],
                             _about="the round stair up the middle of the octagon and the spire (`round-stair-tower`), to the VIEWING GALLERY at 143m; its belvedere, cap and finial are the spire's crown at 161.5m"))
GAL_R = 4.2
add("viewing gallery", {"type": "ring", "count": 10, "rOuter": GAL_R, "rInner": SR, "height": SLAB, "y": GAL - SLAB,
                        "place": [[0, 0, TZ, 0]], "solid": True, "walked": True,
                        "_about": "the viewing gallery at 143m, round the stair's belvedere, on the spire's cut"})
add("viewing gallery parapet", {"type": "ring", "count": 10, "rOuter": GAL_R, "rInner": GAL_R - 0.3, "height": 1.1, "y": GAL,
                                "place": [[0, 0, TZ, 0]], "solid": True})

doc = {"name": "Ulm Minster",
       "_about": "ULM MINSTER (Ulmer Münster, 1377-1890), from components: the ONE WEST TOWER, 161.5m -- the porch hall with its triple portal, three more square `gothic-tower-stage`s of tall traceried windows (each climbed by its own `tower-stair` turret) to the first gallery at 70m, the openwork `gothic-octagon-stage` to 100m and the ribbed `gothic-spire` with its gables and pinnacles, a round stair (`round-stair-tower`) up the middle of both to the VIEWING GALLERY at 143m and the belvedere and stone cap over it; the FIVE-AISLED basilica -- the `basilica` nave with its rib vault 42m up, double aisles split by slender columns under rib vaults of their own, `flying-buttress`es over them -- and the choir with its polygonal `apse` flanked by the TWO EAST TOWERS, square stages, an octagon and a spire to 86m; pale sandstone under steep grey-tiled roofs.",
       "params": P, "base": {"height": 0.6, "steps": 2, "stepOut": 0.5, "margin": 4}, "railing": {"type": "stone"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/ulm.json"), "w").write(json.dumps(doc, indent=2) + "\n")
print(f"spire virtual rise {V_RISE:.2f}; nave top {NAVE_TOP:.2f}, aisle top {AISLE_TOP:.2f}")
