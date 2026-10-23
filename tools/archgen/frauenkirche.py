# THE FRAUENKIRCHE (Dresden, 1726-43, George Baehr; rebuilt 1994-2005): a chamfered square church, the choir
# apse to the east, the stone BELL of a dome on its drum (the `bell` profile), a lantern, four corner stair towers.
import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
arched = lambda w, sill, spring: {"at": 0, "width": w, "sill": sill, "springing": spring, "head": {"profile": "semicircular"}}
lower = {"pattern": "1", "width": 2.6, "gap": 0, "pier": 0, "sill": 2.8, "springing": 6.8, "head": {"profile": "semicircular"}}
upper = {"pattern": "1", "width": 3.0, "gap": 0, "pier": 0, "sill": 2.2, "springing": 11.0, "head": {"profile": "semicircular"}}
tiers = lambda low, up: [{"h": "lowH", "openings": low}, {"openings": up}]
add("church", {"type": "enclosure", "plan": {"rect": ["W", "W"], "chamfer": "C", "split": {"main": [1, 1.1, 1]}}, "thickness": 1.6, "height": "wallH",
               "faces": {"main:0": tiers(lower, upper), "main:2": tiers(lower, upper),
                         "main:1": tiers([arched(3.6, 0, 5.0)], [arched(3.4, 1.4, 11.5)]),
                         "chamfer": tiers([arched(2.2, 3.2, 6.6)], [arched(2.4, 2.4, 10.6)])},
               "at": [[0, 0, 0, 0]],
               "_about": "the church's walls on its chamfered square, each face flank, portal bay and flank, in two tiers: arched windows below, the tall arched windows of the galleries above, a portal in the middle of each side"})
# THE GALLERIES (Emporen) round the inside, at the top of the lower tier, and the flight up to them: a ring of floor
# hugging the walls -- the enclosure part again, deep and thin -- and a straight flight along its inner edge
add("galleries", {"walked": True, "type": "enclosure", "plan": {"rect": ["W - 3.2", "W - 3.2"], "chamfer": "C - 1.3"}, "thickness": 5.0, "height": 0.5,
                  "openings": [], "at": [[0, "lowH - 0.5", 0, 0]],
                  "_about": "the galleries round the church inside, 5m deep, at the top of the lower windows"})
add("gallery stair", {"type": "flight", "width": 1.6, "run": 0.28, "rise": 0.18, "top": "lowH", "landing": 0,
                      "at": [["0 - 7.4", 0, "0 - (W / 2 - 1.6 - 5.0) + 1.6", 0]],
                      "_about": "the flight up to the galleries, along their inner edge: at its top you step off onto them"})
add("choir", {"type": "ring", "count": 12, "turn": 0.5, "rOuter": 9.5, "rInner": 8.0, "height": "wallH - 3", "at": [0, 1, 2, 3, 4, 5],
              "opening": {"width": 2.2, "sill": 3.0, "springing": 11.5, "head": {"profile": "semicircular"}},
              "place": [["W / 2 - 1.6", 0, 0, 0]], "_about": "the choir's apse to the east, a half ring of tall windows"})
add("choir roof", {"type": "dome", "sweep": 0.5, "radius": 9.9, "thickness": 0, "head": {"profile": "segmental", "rise": 4.5},
                   "at": [["W / 2 - 1.6", "wallH - 3", 0, "1.5707963"]]})
add("roof", {"type": "roof", "form": "mansard", "width": "W - 0.4", "length": "W - 0.4", "pitch": 18, "lowerPitch": 62, "breakH": 4.5,
             "overhang": 0.5, "at": [[0, "wallH", 0, 0]], "_about": "the attic roof, steep at its foot, from which the drum rises"})
add("drum", {"type": "enclosure", "plan": {"sides": 16, "radius": "domeR"}, "thickness": 1.4, "height": "drumH",
             "openings": [{"at": 0, "width": 2.0, "sill": 2.8, "springing": 6.4, "head": {"profile": "semicircular"}}],
             "at": [[0, "wallH + 2", 0, 0]], "_about": "the drum, windowed all round"})
add("dome", {"type": "dome", "sides": 16, "radius": "domeR", "thickness": 1.2, "oculus": "lanternR",
             "head": {"profile": "bell", "waist": 0.8, "lift": 0.95},
             "at": [[0, "wallH + 2 + drumH", 0, 0]], "_about": "THE STONE BELL: a dome whose skirt flares out to the drum below its waist, and is round above it"})
add("lantern", {"type": "component", "use": "components/domed-tower",
                "params": {"sides": 8, "R": "lanternR", "H": 9, "t": 0.5, "cap": "bell", "waist": 0.7, "lift": 1.3, "capR": "lanternR * 0.75",
                           "drumR": "lanternR * 0.7", "drumH": 3.0, "kok": 0.8, "finial": 5},
                "build": ["tower", "neck", "drum", "cap", "finial"],
                "at": [[0, 0, 0, 0]], "atop": "dome", "atopR": "lanternR",
                "_about": "the lantern on the bell, standing on its rim where it has narrowed to the lantern's width -- the same component as the corner towers"})
add("corner towers", {"type": "component", "use": "components/domed-tower",
                      "params": {"sides": 8, "R": 3.6, "H": "wallH + 6", "t": 0.6, "cap": "bell", "waist": 0.72, "lift": 1.2, "capR": 2.7,
                                 "drumR": 2.5, "drumH": 3.6, "kok": 1.0, "finial": 3.5},
                      "build": ["tower", "neck", "drum", "cap", "finial"],
                      "at": [[f"{s} * CT", 0, f"{t} * CT", 0] for s, t in ((1, 1), (1, -1), (-1, -1), (-1, 1))],
                      "_about": "the four stair towers on the chamfered corners, each with a small bell of its own"})
doc = {"name": "Frauenkirche, Dresden",
  "_about": "THE FRAUENKIRCHE, Dresden (1726-43), from components: walls round a chamfered square (`enclosure`, each face split into flank, portal bay and flank and built in two TIERS of arched windows), the choir's half ring and half dome to the east, a mansard attic, the windowed drum and on it THE STONE BELL -- a dome struck from the `bell` profile, concave below its waist and round above -- with its lantern, and the four stair towers on the chamfered corners, each a `domed-tower` with a small bell of its own.",
  "params": {"detail": 4, "W": 42, "C": 8.5, "wallH": 26, "lowH": 9.5, "domeR": 12.2, "drumH": 9, "lanternR": 3.0, "CT": 16.4,
             "_CT": "the corner towers stand on the chamfers' middles"},
  "base": {"height": 1.0, "steps": 4, "stepOut": 0.5, "margin": 5}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/frauenkirche.json"), "w").write(json.dumps(doc, indent=2) + "\n")
