# ST PAUL'S CATHEDRAL, London (Wren, 1675-1710), from components: a Latin cross of nave, transepts and choir round a
# square crossing, pendentives in the crossing and the deck round their circle; over the roofs a round base, and on it
# the `drum-dome` -- the PERISTYLE of columns round the drum, the attic over it, the dome and the lantern; the west
# front's two-storey `portico` (the same component twice, one over the other, the pediment on the upper); the two
# west towers, each a square stage climbed by a `tower-stair` and an open belfry (`domed-tower`) under a bell cap.
#   The west front faces +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2

C, T, AH = 34.0, 2.0, 30.0                 # the crossing square, the walls, the arms' height
A = C / 2
NL, TL, CL = 50.0, 22.0, 36.0
ORD = [{"tier": 0, "kind": "corinthian"}, {"tier": 1, "kind": "corinthian"}]   # (two storeys of pilasters: order.js sizes each from its storey)
tiers = [{"h": 15, "openings": {"pattern": "3", "width": 2.6, "gap": 4.4, "sill": 4.0, "springing": 10.5, "head": {"profile": "semicircular"}}},
         {"openings": {"pattern": "3", "width": 2.4, "gap": 4.6, "sill": 3.0, "springing": 9.5, "head": {"profile": "semicircular"}}}]
arch = {"at": 0, "width": 20.0, "sill": 0, "springing": 14.0, "head": {"profile": "semicircular"}}
add("crossing", {"type": "enclosure", "plan": {"rect": [C, C]}, "thickness": T, "height": AH, "openings": [arch], "at": [[0, 0, 0, 0]],
                 "_about": "the crossing: eight piers in the real one, here four walls each opened by a great arch into an arm"})
# (the arms' COURSES -- arch/courses.js: a plinth, the string course at the floor line between the two storeys, the
#  cornice under the balustrade -- run round every face but the one against the crossing)
add("nave", {"type": "enclosure", "plan": {"rect": [C, NL]}, "thickness": T, "height": AH, "tiers": tiers, "courses": {"skip": [2]}, "orders": ORD,
             "faces": {"2": [arch], "0": [{"h": 15, "openings": [{"at": 0, "width": 4.0, "sill": 0, "springing": 7.0, "head": {"profile": "semicircular"}}]},
                                          {"openings": [{"at": 0, "width": 3.4, "sill": 2.0, "springing": 8.0, "head": {"profile": "semicircular"}}]}]},
             "at": [[0, 0, A + NL / 2, 0]], "_about": "the nave, in two storeys outside (the upper a screen wall hiding the aisle roofs)"})
for sx, nm, inner, outer in ((1, "north", "3", "1"), (-1, "south", "1", "3")):
    add(f"{nm} transept", {"type": "enclosure", "plan": {"rect": [TL, C]}, "thickness": T, "height": AH, "tiers": tiers, "courses": {"skip": [int(inner)]}, "orders": ORD,
                           "faces": {inner: [arch], outer: [{"h": 15, "openings": [{"at": 0, "width": 3.6, "sill": 0, "springing": 7.0, "head": {"profile": "semicircular"}}]},
                                                            {"openings": [{"at": 0, "width": 3.0, "sill": 2.0, "springing": 8.0, "head": {"profile": "semicircular"}}]}]},
                           "at": [[sx * (A + TL / 2), 0, 0, 0]], **({"_about": "the transepts, a door in each end"} if sx > 0 else {})})
    # the semicircular portico before each transept door: a half ring of columns under a half dome
    add(f"{nm} portico", {"type": "colonnade", "plan": "round", "arc": 180, "count": 6, "radius": 6.0, "order": "corinthian", "columnR": 0.6,
                          "height": 12.0, "taper": 0.86, "entablature": {"h": 1.8, "depth": 1.6}, "at": [[sx * (A + TL), 0, 0, sx * Q]],
                          **({"_about": "the transept porticoes: six columns on a half circle before each door, under a half dome"} if sx > 0 else {})})
    add(f"{nm} portico dome", {"type": "dome", "sweep": 0.5, "sides": 16, "radius": 6.8, "thickness": 0.6, "head": {"profile": "semicircular"},
                               "at": [[sx * (A + TL), 13.8, 0, sx * Q]]})
add("choir", {"type": "enclosure", "plan": {"rect": [C, CL]}, "thickness": T, "height": AH, "tiers": tiers, "courses": {"skip": [0]}, "orders": ORD,
              "faces": {"0": [arch], "2": [{"at": 0, "width": C - 2 * T - 1.0, "sill": 0, "springing": 14.0, "head": {"profile": "semicircular"}}]},
              "at": [[0, 0, -A - CL / 2, 0]], "_about": "the choir, open at its end into the apse"})
AR = A - T
APH = 18.0                                 # the apse lower than the choir: its half dome's face is closed by the choir's end wall
add("apse", {"type": "component", "use": "components/apse",
             "params": {"R": AR, "T": T, "H": APH, "n": 16, "winW": 2.4, "winSill": 5.0, "winH": 8.0, "domeT": T},
             "at": [[0, 0, -A - CL, math.pi]], "_about": "the apse, lower than the choir: its half dome rises into the choir's end wall, not above it"})
add("nave roof", {"type": "roof", "form": "gable", "width": C, "length": NL, "pitch": 22, "overhang": 0.3, "at": [[0, AH, A + NL / 2, 0]],
                  "_about": "low roofs behind the parapets"})
add("choir roof", {"type": "roof", "form": "gable", "width": C, "length": CL, "pitch": 22, "overhang": 0.3, "at": [[0, AH, -A - CL / 2, 0]]})
add("transept roofs", {"type": "roof", "form": "gable", "width": C, "length": TL, "pitch": 22, "overhang": 0.3,
                       "at": [[sx * (A + TL / 2), AH, 0, Q] for sx in (-1, 1)]})

# the balustrade along every wall's head, round the low roofs: a parapet pierced between its balusters
def balustrade(w, l):
    row = lambda L: {"pattern": str(int((L - 1.0) // 0.56)), "width": 0.28, "gap": 0.28, "sill": 0.25, "springing": 0.95,
                     "head": {"profile": "flat"}, "glass": False}
    return {"0": row(w), "2": row(w), "1": row(l), "3": row(l)}
for nm, w, l, x, z in (("nave", C, NL, 0, A + NL / 2), ("choir", C, CL, 0, -A - CL / 2), ("north transept", TL, C, A + TL / 2, 0),
                       ("south transept", TL, C, -A - TL / 2, 0)):
    add(f"{nm} balustrade", {"type": "enclosure", "plan": {"rect": [w, l]}, "thickness": 0.4, "height": 1.3, "faces": balustrade(w, l),
                             "at": [[x, AH, z, 0]], **({"_about": "the balustrade round every roof, on the walls' heads"} if nm == "nave" else {})})

# ---- the dome: pendentives and their deck, a round base over the roofs, the drum-dome with its peristyle
add("pendentives", {"type": "pendentives", "span": C - 2 * T, "springing": AH - (A - T), "sides": 32, "at": [[0, 0, 0, 0]],
                    "deck": {"thickness": 0.6, "out": T}, "_about": "the pendentives, and the deck round their circle"})
BASE = 7.5
add("dome base", {"flatRoof": True, "type": "ring", "count": 32, "rOuter": 21.5, "rInner": A - T, "height": BASE, "y": AH, "turn": 0.5, "solid": True,
                  "place": [[0, 0, 0, 0]], "_about": "the round base the peristyle stands on, clear of the roofs"})
add("dome", comp("components/drum-dome", {"R": A - T, "dt": 1.4, "H": 22.0, "n": 32, "every": 2, "winW": 1.8, "winSill": 15.5, "winH": 4.0,
                                          "profile": "pointed", "spread": 0.35, "domeT": 1.2, "colN": 32, "colR": 0.75, "colH": 14.0, "pw": 3.4,
                                          "lanternR": 3.2, "lanternH": 14.0},
                 [[0, AH + BASE, 0, 0]], build=["drum", "drum piers", "peristyle", "peristyle deck", "dome", "lantern"],
                 _about="the drum with its peristyle of 32 columns, the attic over them with its windows, the dome and the lantern"))

# ---- the west front: the two-storey portico and the towers
FZ = A + NL
add("lower portico", comp("components/portico", {"count": 8, "spacing": 3.6, "colR": 0.7, "colH": 12.0, "entH": 2.0, "depth": 8.0, "order": "corinthian"},
                          [[0, 0, FZ, 0]], build=["steps", "columns"], _about="the lower storey of the west portico: paired Corinthian columns, as here in a row"))
add("upper portico", comp("components/portico", {"count": 6, "spacing": 4.2, "colR": 0.6, "colH": 10.0, "entH": 2.0, "depth": 8.0, "order": "corinthian",
                                                 "steps": 0, "pitch": 24},
                          [[0, 4 * 0.2 + 12.0 + 2.0, FZ, 0]], build=["columns", "pediment"], _about="...and the upper, under the pediment"))
TWR = 12.0
for sx, nm in ((1, "north"), (-1, "south")):
    x, z = sx * (A + TWR / 2 - 1.0), FZ - TWR / 2
    # (its courses the arms' own -- the floor line at 15m runs on round it -- but for the face against the nave)
    add(f"{nm}west tower", {"type": "enclosure", "plan": {"rect": [TWR, TWR]}, "thickness": 1.5, "height": AH, "courses": {"skip": [3 if sx > 0 else 1]},
                            "tiers": [{"h": 15, "openings": [{"at": 0, "width": 2.4, "sill": 4.0, "springing": 10.0, "head": {"profile": "semicircular"}}]},
                                      {"openings": [{"at": 0, "width": 2.2, "sill": 3.0, "springing": 9.0, "head": {"profile": "semicircular"}}]}],
                            "faces": {"0": [{"h": 15, "openings": [{"at": 0, "width": 2.6, "sill": 0, "springing": 5.0, "head": {"profile": "semicircular"}}]},
                                            {"openings": [{"at": 0, "width": 2.2, "sill": 3.0, "springing": 9.0, "head": {"profile": "semicircular"}}]}]},
                            "at": [[x, 0, z, 0]], **({"_about": "the west towers: a square stage to the roofs' height, a door in its front..."} if sx > 0 else {})})
    add(f"{nm}west tower stair", comp("components/tower-stair", {"W": TWR - 3.0, "H": AH}, [[x, 0, z, 0 if sx < 0 else Q]],
                                      **({"_about": "...climbed by its stair to the floor at the top..."} if sx > 0 else {})))
    add(f"{nm}west belfry", comp("components/domed-tower", {"sides": 4, "R": TWR / 2 * 1.4142, "H": 14.0, "t": 1.2, "drumR": 4.2, "drumH": 7.0, "cap": "bell",
                                                            "capR": 4.6, "waist": 0.8, "lift": 1.1, "kok": 1.0, "finial": 5.0, "winW": 2.0, "glazed": 0, "doorH": 3.0},
                                 [[x, AH, z, 0]], build=["tower", "drum", "cap", "finial"],
                                 **({"_about": "...and on it the belfry, its open lantern stage and the bell cap"} if sx > 0 else {})))

# ---- the statues (statuary.py): St Paul on the apex of the west pediment, St Peter and St James at its corners; the
# four Evangelists at the west towers' front corners, over the roofs -- Portland stone (limestone), looking west
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from statuary import statue, FACE_PZ, capped
yPed = 4 * 0.2 + 12.0 + 2.0 + 10.0 + 2.0                             # the upper portico's top (it has no steps): the pediment's foot
WP = 5 * 4.2 + 4 * 0.6 + 1.0; rise = WP / 2 * math.tan(math.radians(24)); zG = FZ + 8.4
stat = {"statue St Paul": statue((0, yPed + rise - 0.3, zG - 0.7), kind="man", style="roman", stone="limestone", scale=1.9, seed=3, face=FACE_PZ, hold={"R": "items/weapons/sword"}),
        "statue St Peter": statue((-(WP / 2 - 0.9), yPed, zG - 0.6), kind="man", style="roman", stone="limestone", scale=1.6, seed=5, face=FACE_PZ),
        "statue St James": statue((WP / 2 - 0.9, yPed, zG - 0.6), kind="man", style="roman", stone="limestone", scale=1.6, seed=7, face=FACE_PZ, hold={"R": "items/tools/staff"})}
for i_, (sx, cx) in enumerate([(-1, -1), (-1, 1), (1, -1), (1, 1)]):
    x, z = sx * (A + TWR / 2 - 1.0) + cx * (TWR / 2 - 1.0), FZ - 1.0
    stat[f"statue evangelist {i_}"] = statue((x, AH, z), kind="man", style="roman", stone="limestone", scale=1.6, seed=11 + i_, face=FACE_PZ, hold={"R": "items/tools/book"})
for k, v in capped(stat).items(): add(k, v)

doc = {"name": "St Paul's Cathedral",
       "_about": "ST PAUL'S CATHEDRAL, London (Wren, 1675-1710), from components: a Latin cross of nave, transepts and choir with its apse round a square crossing, pendentives in the crossing and the deck round their circle; over the roofs a round base, and on it the `drum-dome` -- a PERISTYLE of 32 columns round the drum, the attic over it, the dome and the stone lantern; the west front's two-storey `portico`, the same component twice; and the two west towers, each a square stage climbed by a `tower-stair` and an open belfry under a bell cap.",
       "params": {"detail": 4}, "base": {"height": 0.8, "steps": 4, "stepOut": 0.5, "margin": 4}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/st-pauls.json"), "w").write(json.dumps(doc, indent=2) + "\n")
