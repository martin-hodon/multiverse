# THE HUNGARIAN PARLIAMENT, Budapest (Gothic Revival, 1885-1904), from repeated components: its two long halves are
# each a `court` -- a ring of rooms round its courtyard, three storeys under steep roofs, gated toward the middle --
# and between them the square central hall under the great ribbed dome (pendentives and their deck, then the
# `drum-dome`: a sixteen-sided drum windowed in every bay, the pointed dome, its ribs and its spire of a lantern);
# `domed-tower` turrets with stone spires on the courts' corners and the central hall's; the river front with its
# arcaded loggias (`gallery`), turrets and a row of `pinnacle`s; the porch on the square.
#   The river front faces +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}

CS, CH, T = 30.0, 30.0, 1.8                # the central hall: square, height, walls
A = CS / 2
CW, CD, ST, SH = 80.0, 70.0, 3, 6.0        # each court: along the river, deep, storeys and their height
WALL = ST * SH
# ---- the two halves: a court each, gated toward the central hall
for sx, nm, face in ((-1, "west", 1), (1, "east", 3)):
    add(f"{nm} court", {"type": "court", "plan": {"rect": [CW, CD]}, "depth": 13.0, "storeys": ST, "storeyH": SH, "axis": 3.6,
                        "winW": 1.4, "winH": 3.0, "head": {"profile": "pointed", "spread": 1.0},
                        "gate": {"face": face, "width": 4.0, "height": 5.5}, "roof": {"form": "hip", "pitch": 55},
                        "at": [[sx * (A + CW / 2), 0, 0, 0]],
                        **({"_about": "the two halves, each a ring of rooms round its courtyard, three storeys under steep roofs, gated toward the central hall"} if sx < 0 else {})})
# ---- the central hall and its dome
door = lambda w, h: [{"at": 0, "width": w, "sill": 0, "springing": h - w / 2, "head": {"profile": "pointed", "spread": 1.0}}]
tall = {"pattern": "3", "width": 2.2, "gap": 5.0, "sill": 6.0, "springing": 18.0, "head": {"profile": "pointed", "spread": 1.0}}
add("central hall", {"type": "enclosure", "plan": {"rect": [CS, CS]}, "thickness": T, "height": CH, "openings": tall,
                     "faces": {"1": door(4.0, 5.5), "3": door(4.0, 5.5), "2": door(5.0, 8.0)},
                     "at": [[0, 0, 0, 0]], "_about": "the domed central hall: the main door from the square, and a door through into each court"})
DR = A - T
add("pendentives", {"type": "pendentives", "span": CS - 2 * T, "springing": CH - DR, "sides": 16, "at": [[0, 0, 0, 0]],
                    "deck": {"thickness": 0.6, "out": T}, "_about": "the pendentives, and the roof round the drum's foot"})
add("dome", comp("components/drum-dome", {"R": DR, "dt": 1.2, "H": 22.0, "n": 16, "every": 1, "winW": 2.2, "winSill": 4.0, "winH": 12.0,
                                          "profile": "pointed", "spread": 0.75, "domeT": 1.0, "ribW": 0.6, "lanternR": 2.6, "lanternH": 16.0},
                 [[0, CH, 0, 0]], build=["drum", "dome", "ribs", "lantern"],
                 _about="the great dome: a sixteen-sided drum, a window in every bay, the pointed dome and its ribs, the spire of a lantern"))
# ---- the turrets: on the courts' outer corners, the central hall's corners
turret = {"sides": 8, "R": 3.0, "H": WALL + 8.0, "t": 0.6, "drumR": 2.0, "drumH": 2.0, "cap": "trigonal", "capRise": 12.0, "capR": 2.4,
          "kok": 0.8, "finial": 1.5, "winW": 0.7, "doorH": 2.6}
add("corner turrets", comp("components/domed-tower", turret,
                           [[sx * (A + CW), 0, sz * CD / 2, 0] for sx in (-1, 1) for sz in (-1, 1)] +
                           [[sx * A, 0, sz * CD / 2, 0] for sx in (-1, 1) for sz in (-1, 1)],
                           build=["tower", "kokoshniki", "drum", "cap", "finial"],
                           _about="Gothic turrets under stone spires, on the corners of the courts"))
add("hall turrets", comp("components/domed-tower", {**turret, "R": 1.8, "H": 6.0, "drumR": 1.2, "drumH": 1.4, "capR": 1.5, "capRise": 9.0, "doorH": 1.8, "winW": 0.5},
                         [[sx * (A - 1.2), CH, sz * (A - 1.2), 0] for sx in (-1, 1) for sz in (-1, 1)],
                         build=["tower", "drum", "cap", "finial"], _about="and four small ones on the central hall's corners, round the dome"))
# ---- the river front: an arcaded loggia along each half, its roof a terrace; turrets rising out of the front
LD, LH = 6.0, 7.0
add("river loggias", comp("components/gallery", {"L": CW - 8.0, "D": LD, "H": LH, "n": 14, "winW": 3.0, "sill": 0, "arch": "pointed", "slab": 0.6, "terrace": 0},
                          [[sx * (A + CW / 2), 0, CD / 2 + LD / 2, 0] for sx in (-1, 1)],
                          _about="the arcaded loggias along the river front, their roofs terraces behind a balustrade"))
add("river turrets", comp("components/domed-tower", {**turret, "R": 2.2, "H": WALL + 10.0, "drumR": 1.5, "drumH": 1.6, "capR": 1.8, "capRise": 10.0,
                                                     "doorH": 2.4, "winW": 0.6},
                          [[sx * (A + CW / 2 + dx), 0, CD / 2 + 0.8, 0] for sx in (-1, 1) for dx in (-22.0, 22.0)],
                          build=["tower", "kokoshniki", "drum", "cap", "finial"], _about="turrets rising out of the river front, over its roofs"))
# ---- the entrance from the square: a porch before the central hall's door
add("entrance porch", {"type": "enclosure", "plan": {"rect": [14.0, 8.0]}, "thickness": 1.2, "height": 12.0, "glass": False,
                       "openings": [{"at": 0, "width": 5.0, "sill": 0, "springing": 7.0, "head": {"profile": "pointed", "spread": 1.0}}],
                       "faces": {"1": [{"at": 0, "width": 3.0, "sill": 0, "springing": 5.5, "head": {"profile": "pointed", "spread": 1.0}}],
                                 "3": [{"at": 0, "width": 3.0, "sill": 0, "springing": 5.5, "head": {"profile": "pointed", "spread": 1.0}}]},
                       "at": [[0, 0, -A - 4.0, 0]], "_about": "the porch on the square: arches on three sides before the central hall's door"})
add("porch gable", {"type": "roof", "form": "gable", "width": 14.0, "length": 8.0, "pitch": 55, "overhang": 0.3, "at": [[0, 12.0, -A - 4.0, 0]]})

# ---- the river front's pinnacles
xs = [round(sx * (A + 4.5 + 7.2 * k), 3) for sx in (-1, 1) for k in range(10)]
add("river pinnacles", comp("components/pinnacle", {"w": 0.9, "h": 2.4, "s": 4.0}, [[x, WALL, CD / 2 - 0.45, 0] for x in xs],
                            _about="the pinnacles along the river front's parapet, one over every pier"))

doc = {"name": "Hungarian Parliament",
       "_about": "THE HUNGARIAN PARLIAMENT, Budapest (Gothic Revival, 1885-1904), from repeated components: its two halves each a `court` -- a ring of rooms round a courtyard, three storeys under steep roofs, walked all the way round and gated toward the middle -- and between them the square central hall under the great ribbed dome (pendentives with their deck, then the `drum-dome`: a sixteen-sided drum windowed in every bay, the pointed dome, its ribs, the spire of a lantern); Gothic turrets (`domed-tower` under stone spires) on the courts' corners and round the dome; the river front with its arcaded loggias (the `gallery` as an open arcade) under turrets and a row of `pinnacle`s; and the porch on the square before the central hall's door.",
       "params": {"detail": 4}, "base": {"height": 0.8, "steps": 4, "stepOut": 0.5, "margin": 4}, "railing": {"type": "stone"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/parliament.json"), "w").write(json.dumps(doc, indent=2) + "\n")
