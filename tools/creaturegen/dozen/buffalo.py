# THE WATER BUFFALO (2026-11-09): the ox at 1.05, heavier in the neck and chest, under sparse slate-grey skin (dark above,
# a little paler below, pale grey stockings low on the legs, a white chevron across the throat -- a paint); the ox's
# short lyre horns replaced by the buffalo's great crescents, sweeping back and out along the neck in one plane, the
# tips turning up, the section flattened. A mount, a draft animal (the ox's yoke numbers at the new size). Written whole
# by this script.
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dlib import *

f = 1.05
d = load("mammals/ox"); scale_def(d, f)
d["name"] = "water buffalo"; d["graze"] = 1.0; d["rest"] = 0.8
d["mount"] = {"h": 2.3, "speed": 1.2}
if "draft" in d: d["draft"] = {k: (round(v * f, 3) if k != "speed" else v) for k, v in d["draft"].items()}
d.pop("_quality", None)
d["_about"] = ("THE WATER BUFFALO (2026-11-09, tools/creaturegen/dozen/buffalo.py): the ox at 1.05, a heavier neck and chest, slate-grey "
               "skin with pale stockings and a white throat chevron (a paint), crescent horns sweeping back and out in one plane. A mount and a draft animal. Written whole by its script.")
# ---- heavier forehand
for i, g in (("neck", 1.12), ("neckBase", 1.1), ("chest", 1.08), ("crest", 1.15), ("brisket", 1.1)): grow(d, i, g)
over(d, "hump", r=[0.36, 0.12, 0.26])
# ---- the horns: one crescent a side, out to the side nearly level, sweeping back, the tip curling up and in; flattened (aspect .7)
root = shape(d, "horn")["pts"][0]
P = [[root[0], root[1], root[2], 0.082, 0.7],
     [1.30, 1.48, 0.17, 0.08, 0.7],
     [1.27, 1.50, 0.32, 0.072, 0.7],
     [1.19, 1.52, 0.47, 0.062, 0.7],
     [1.07, 1.54, 0.59, 0.052, 0.7],
     [0.95, 1.57, 0.67, 0.044, 0.7],
     [0.85, 1.62, 0.70, 0.034, 0.7],
     [0.79, 1.70, 0.69, 0.024, 0.7],
     [0.76, 1.80, 0.65, 0.012, 0.7],
     [0.76, 1.87, 0.61, 0.0, 0.7]]
over(d, "horn", pts=P, color="#3a3430", tip="#201c1a", tipAt=0.6, up=[0, 1, 0], fair=0.03)
# ---- the throat chevron: a pale V painted across the lower neck
add(d, {"id": "chevron", "type": "ell", "bone": "neck", "c": [1.0, 1.0, 0.0], "r": [0.05, 0.045, 0.2], "rot": [0, 0, 20], "k": 0.004, "kc": 0.006, "op": "paint", "color": "@chevron"})
# ---- the hide: slate grey; the stockings pale
recolor(d, body="#3a3a3c", muzzle="#2a2a2c", ear="#38383a", leg="#8a8882", foot="#1e1c1a", tail="#343436", eye="#1e1612", head="#343436", nose="#1c1a18",
        earIn="#6a6462", fore="#3e3e40", tuft="#2a2826", belly="#4a4a4c", chevron="#d8d4cc")
over(d, "belly", color="@belly")
for i in ("arm", "forearm", "stifle", "gaskin", "ham"): shape(d, i)["color"] = "@body"   # (the upper legs the body's dark; the ox's colours fall to @leg below the knee)
d["coats"] = [{"name": "slate"}, {"name": "slate"},
              {"name": "dark", "body": "#2c2c2e", "fore": "#303032", "head": "#28282a", "belly": "#3a3a3c", "leg": "#6e6c66", "ear": "#2a2a2c", "tail": "#28282a"},
              {"name": "grey", "body": "#56565a", "fore": "#5a5a5e", "head": "#4e4e52", "belly": "#66666a", "leg": "#9a9892", "ear": "#525256", "tail": "#4e4e52", "muzzle": "#3a3a3c"}]
d.pop("_coats", None)
save("mammals/water-buffalo", d)
index_add("creatures/mammals/water-buffalo", "Mammals")
if "--shot" in sys.argv: render("creatures/mammals/water-buffalo", "buffalo")
