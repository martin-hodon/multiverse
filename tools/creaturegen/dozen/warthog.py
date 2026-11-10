# THE WARTHOG (2026-11-09, dozen/warthog.py): the wild boar's rig and sculpt at .85 (70 cm at the shoulder), the boar's
# grizzled bark coat and stripes gone for sparse grey-brown skin; a flatter, longer head with two pairs of warts, big
# upper tusks curving up and back (a small lower pair), a long thin dark mane down the neck and back, pale whiskery
# cheeks, a thin tail, dark legs. Variant `piglet`. Not a mount.
import sys, os, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dlib import *

S = 0.85
d = load("mammals/boar")
scale_def(d, S)
d["name"] = "warthog"; d["shy"] = 9; d["graze"] = 0.6
d.pop("mount", None); d.pop("pat", None); d.pop("patOn", None)
for sh in shapes(d): sh.pop("pat", None); sh.pop("hair", None)
drop(d, "stripe0", "stripe1", "stripe2", "stripe3")
# the head: flatter and longer -- the face cone and brow stretched forward, the cranium lower
f = shape(d, "face"); f["b"] = [f["b"][0] + 0.05, f["b"][1] + 0.01, 0]; f["ra"] *= 0.95
b = shape(d, "brow"); b["b"] = [b["b"][0] + 0.05, b["b"][1] + 0.02, 0]; b["a"][1] -= 0.015; b["ra"] *= 0.9
grow(d, "cranium", 1.05, 0.88, 1.1)
for i in ("snout", "disc", "nostril", "lip", "flange"): move(d, i, 0.05, 0.01, 0)
d["muzzle"][3] += 0.05; d["nose"][0] += 0.05
shape(d, "cheek")["color"] = "@cheek"
# the warts: a pair under the eyes, a pair lower on the cheeks -- on the skin, half out of it
e = d["sculpt"]["eyes"]["at"]
add(d, {"id": "wartEye", "type": "ell", "bone": "head", "c": [e[0] + 0.02, e[1] - 0.05, 0.122], "r": [0.032, 0.028, 0.026], "k": 0.014, "kc": 0.004, "color": "@wart", "mirror": True}, after="cheek")
add(d, {"id": "wartJaw", "type": "ell", "bone": "head", "c": [e[0] + 0.07, e[1] - 0.1, 0.118], "r": [0.024, 0.022, 0.02], "k": 0.012, "kc": 0.003, "color": "@wart", "mirror": True}, after="cheek")
# the tusks: the upper pair long, out, up and back; a short lower pair against them
sn = shape(d, "snout")["c"]
x0, y0 = sn[0] - 0.08, sn[1] - 0.01
over(d, "tusk", pts=[[x0 - 0.03, y0 - 0.02, 0.02, 0.026], [x0, y0 - 0.01, 0.05, 0.026], [x0 + 0.03, y0 + 0.02, 0.085, 0.024], [x0 + 0.04, y0 + 0.07, 0.11, 0.021], [x0 + 0.03, y0 + 0.13, 0.125, 0.017], [x0 - 0.005, y0 + 0.18, 0.13, 0.011], [x0 - 0.045, y0 + 0.21, 0.125, 0.0]],
     fair=0.02, when=None, up=[0, 1, 0])
add(d, {"id": "tuskLo", "type": "horn", "bone": "head", "pts": [[x0 + 0.02, y0 - 0.055, 0.025, 0.013], [x0 + 0.045, y0 - 0.045, 0.055, 0.012], [x0 + 0.055, y0 - 0.02, 0.078, 0.009], [x0 + 0.05, y0 + 0.02, 0.09, 0.0]], "color": "@tusk", "mirror": True, "up": [0, 1, 0], "fair": 0.012, "sides": 10}, after="tusk")
# the mane: long, thin and dark, from the crown down the neck and the whole back to the rump -- a ridge lying ON the
# back (its centreline just under the skin's top, read off the barrel and rump ellipsoids), not a tube over it
cn = shape(d, "crestN"); cn["pts"] = [[p[0], p[1] - 0.01, p[2], p[3] * 0.5] for p in cn["pts"]]; cn.pop("when", None); cn["k"] = 0.03
def back_top(x):
    x /= S; best = 0
    for cx, cy, rx, ry in ((0.26, 0.73, 0.28, 0.25), (-0.05, 0.7, 0.43, 0.2), (-0.42, 0.66, 0.24, 0.2), (0.2, 0.87, 0.32, 0.12)):
        u = (x - cx) / rx
        if abs(u) < 1: best = max(best, cy + ry * math.sqrt(1 - u * u))
    return best * S
cr = shape(d, "crest"); cr.pop("when", None)
xs_ = [p[0] for p in cr["pts"]] + [round(cr["pts"][-1][0] - 0.035 * k, 4) for k in range(1, 7)]
xs_ = [x for x in xs_ if back_top(x) > 0.3 * S]   # (only while there is a back under it: off the rump the ridge would fall to the floor)
cr["pts"] = [[x, round(back_top(x) + 0.012, 4), 0, round(0.03 * (1 - 0.6 * i / (len(xs_) - 1)), 4)] for i, x in enumerate(xs_)]
cr["k"] = 0.03; cr["kc"] = 0.012
for i in ("crestN", "crest"): shape(d, i)["color"] = "@crest"
# the tail: the boar's own hanging arc (its tuft left off: the engine's tuft drew as a long dark rod), thin
d["tail"] = {"c": [-0.91 * S, 0.72 * S], "R": 0.24 * S, "a0": 0, "a1": -1.1, "r1": 0.016, "r2": 0.01, "n": 3, "sway": 14, "speed": 0.9}
# the skin
recolor(d, body="#6e6056", back="#5e5248", belly="#7a6c62", muzzle="#5e5248", leg="#4e433c", foot="#1c1816", cheek="#b8a898", crest="#2a221c", crestTip="#5a5048", tail="#5e5248", tusk="#e8e0cc", wart="#5a4e46", nose="#4a4039", nostril="#2a1e1a", ear="#5a4e46", stripe=None)
d["variants"] = {"piglet": {"params": {"adult": False, "piglet": True}, "scale": 0.3, "colors": {"body": "#8a7a6a", "back": "#7a6a5a", "belly": "#9a8a7a", "leg": "#6a5a4a", "muzzle": "#7a6a5a"}}}
d["_about"] = "THE WARTHOG (2026-11-09, tools/creaturegen/dozen/warthog.py): the wild boar's rig and sculpt at .85 -- 70 cm at the shoulder, the bark coat and the stripes gone; the head flatter and longer with two pairs of warts, big upper tusks curving out, up and back and a short lower pair (horns, faired), a long thin dark mane from the crown down the whole back, pale whiskery cheeks, a thin hanging tail; sparse grey-brown skin, dark legs. Variant `piglet` at .3. Written whole by its script."
save("mammals/warthog", d)
index_add("creatures/mammals/warthog", "Mammals")
if "--shot" in sys.argv: render("creatures/mammals/warthog", "warthog", views=("side", "q", "rear", "head"))
