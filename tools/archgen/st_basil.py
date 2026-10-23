# ST BASIL'S CATHEDRAL (the Cathedral of the Intercession on the Moat, Moscow, 1555-61), from the
# `domed-tower` component: nine chapels on one platform, and the belfry beside them.
import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapes import tent_y_at
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
tower = lambda **params: {"type": "component", "use": "components/domed-tower", "params": params}
add("platform", {"type": "prism", "plan": {"rect": [46, 46], "chamfer": 9}, "height": "podklet", "at": [[0, 0, 0, 0]],
                 "_about": "the podklet: the vaulted basement all nine churches stand on"})
arcade = lambda n: {"pattern": str(n), "width": 1.6, "gap": 1.2, "pier": 1.2, "sill": 0.9, "springing": 2.6, "head": {"profile": "semicircular"}}
add("gallery", {"type": "enclosure", "plan": {"rect": [44, 44], "chamfer": 8.5, "split": {"main": [2, 1, 2]}}, "thickness": 0.7, "height": 4.2,
                "faces": {"main:0": arcade(3), "main:2": arcade(3), "chamfer": arcade(2),
                          "main:1": [{"at": 0, "width": 2.4, "sill": 0, "springing": 2.8, "head": {"profile": "semicircular"}}]},
                "at": [[0, "podklet", 0, 0]], "_about": "the gallery that runs round the platform and joins the chapels: arcaded, with a door in the middle of each side (the plan's `split`)"})
add("stairs", {"type": "flight", "width": 3.0, "run": 0.3, "rise": 0.17, "top": "podklet", "landing": 0,
               "at": [[1.5, 0, 23 + 32 * 0.3, 1.5707963]], "_about": "the flight up to the platform from Red Square"})
# the central tower: a tall tent, and a small domed tower on its tip
add("central tower", {**tower(sides=8, R=5.5, H=17, cap="trigonal", capRise=15, drumR=4.0, drumH=3.2, capR=4.3, finial=0.1),
                      "build": ["tower", "kokoshniki", "neck", "drum", "cap"], "at": [[0, "podklet", 0, 0]],
                      "_about": "the Intercession: the central tower, its tent roof 15m high"})
add("central lantern", {**tower(sides=8, R=1.3, H=2.4, drumR=0.9, drumH=1.0, bulge=1.45, neck=0.8, capR=1.15, finial=1.4),
                        "build": ["tower", "drum", "cap", "cap ribs", "finial"], "at": [[0, f"podklet + {17 + 5.5 * 0.5 + 3.2 + tent_y_at(4.3, 15, 1.3):.4f}", 0, 0]],
                        "_about": "the small onion on the tent's tip: the same component at a quarter the size, set where the tent is its width (tools/archgen/shapes.py)"})
# four big chapels on the axes, four smaller ones on the diagonals
# ...each its own part, so each can have its own colours: no two of St Basil's onions are alike
axial = [("north", [0, "podklet", 15.5, 0]), ("east", [15.5, "podklet", 0, 1.5707963]), ("south", [0, "podklet", -15.5, 3.14159265]), ("west", [-15.5, "podklet", 0, -1.5707963])]
for nm, at in axial:
    add(f"{nm} chapel", {**tower(sides=8, R=4.0, H=15, drumR=2.7, drumH=3.0, bulge=1.4, neck=0.85, capR=3.0, finial=2.2, capRibs=16),
                         "build": ["tower", "kokoshniki", "neck", "drum", "cap", "cap ribs", "finial"], "at": [at],
                         "_about": f"the {nm} chapel on the axis, an octagon with its drum and a ribbed onion"})
for nm, (sx, sz) in (("northeast", (1, 1)), ("southeast", (1, -1)), ("southwest", (-1, -1)), ("northwest", (-1, 1))):
    add(f"{nm} chapel", {**tower(sides=8, R=2.7, H=10.5, drumR=1.9, drumH=2.4, bulge=1.35, neck=0.9, capR=2.1, finial=1.6, capRibs=12),
                         "build": ["tower", "kokoshniki", "neck", "drum", "cap", "cap ribs", "finial"], "at": [[sx * 11.2, "podklet", sz * 11.2, 0]],
                         "_about": f"the smaller {nm} chapel on the diagonal"})
add("belfry", {**tower(sides=8, R=3.2, H=14, cap="trigonal", capRise=8, drumR=2.4, drumH=3.5, capR=2.6, finial=0.1, glazed=0),
               "build": ["tower", "neck", "drum", "cap"], "at": [[-27, 0, 18, 0]], "_about": "the belfry, standing apart: an octagon with an open drum and a tent"})
add("belfry onion", {**tower(sides=8, R=0.9, H=1.4, drumR=0.6, drumH=0.8, bulge=1.3, capR=0.75, finial=1.0),
                     "build": ["tower", "drum", "cap", "finial"], "at": [[-27, round(14 + 3.2 * 0.5 + 3.5 + tent_y_at(2.6, 8, 0.9), 4), 18, 0]]})
doc = {"name": "St Basil's Cathedral",
  "_about": "ST BASIL'S CATHEDRAL, Moscow (1555-61), from ONE component -- `domed-tower` -- used at five sizes: on its platform and gallery, the central tower of the Intercession with its tall tent and a small onion on the tip; four great chapels on the axes, each an octagon with a drum and a ribbed onion; four smaller ones on the diagonals; and the belfry standing apart with its own tent. Nothing here is drawn once for this building alone except the platform, the gallery and the stair.",
  "params": {"detail": 4, "podklet": 5.5}, "railing": {"type": "stone"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/st-basil.json"), "w").write(json.dumps(doc, indent=2) + "\n")
