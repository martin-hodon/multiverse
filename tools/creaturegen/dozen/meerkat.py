# THE MEERKAT (2026-11-09, dozen/meerkat.py): the least weasel's rig and sculpt at 1.3 (a 26 cm body on a shorter trunk),
# the legs half again as long (the trunk raised with them), a thin 22 cm tail with a black tip, a pointed face with
# dark eye patches painted round the eyes, small round ears; tan-grey with faint darker bands painted across the back,
# a pale belly, dark feet and nose. The weasel's sentinel pose (upright) kept: a meerkat stands watch.
import sys, os, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dlib import *

S = 1.3
d = load("mammals/weasel")
scale_def(d, S)
d["name"] = "meerkat"; d["shy"] = 4; d["graze"] = 0.2; d["headTurn"] = 30
d.pop("hop", None); d["flex"] = 4
# a shorter trunk: the sculpt and the rig's x's at .85
stretch(d, fx=0.85)
def xs(v, f): return [x * f if i in (0, 3) else x for i, x in enumerate(v)]
for k in ("rear", "front"): d[k][0] *= 0.85; d[k][3] *= 0.85
for k in ("neck", "muzzle", "ears"): d[k] = xs(d[k], 0.85)
for k in ("head", "nose", "eyes"): d[k][0] *= 0.85
d["legs"]["front"][0] *= 0.85; d["legs"]["hind"][0] *= 0.85
# longer legs: hips raised, the trunk up with them
UP = 0.022
for k in ("front", "hind"): d["legs"][k][1] += UP; d["legs"][k][3] *= 1.5
d["legs"]["radii"] = [v * 0.9 for v in d["legs"]["radii"]]
for k in ("rear", "front", "head", "nose", "eyes"): d[k][1] += UP
for k in ("neck", "muzzle", "ears"): d[k][1] += UP; d[k][4] += UP
for i in ("rump", "loin", "waist", "chest", "neck", "cranium", "cheek", "muzzle", "jaw", "nose", "whiskers", "ear"): move(d, i, 0, UP, 0)
d["sculpt"]["eyes"]["at"][1] += UP; d["sculpt"]["eyes"]["from"][1] += UP
# the legs rewritten from the raised hips: thin, straight, dark feet
L = d["legs"]; fh, hh = L["front"], L["hind"]
drop(d, "arm", "forearm", "paw", "thigh", "shank", "foot")
add(d, {"id": "arm", "type": "cone", "bone": "legFLu", "a": [fh[0] - 0.004, fh[1] + 0.006, fh[2]], "b": [fh[0], fh[1] - fh[3], fh[2]], "ra": 0.0085, "rb": 0.0055, "k": 0.006, "color": "@body", "mirror": True, "hair": 0.1})
add(d, {"id": "forearm", "type": "cone", "bone": "legFLl", "a": [fh[0], fh[1] - fh[3], fh[2]], "b": [fh[0] + 0.002, 0.006, fh[2]], "ra": 0.0052, "rb": 0.004, "k": 0.003, "color": "@leg", "mirror": True, "hair": 0.1})
add(d, {"id": "paw", "type": "ell", "bone": "footFL", "c": [fh[0] + 0.008, 0.0032, fh[2]], "r": [0.011, 0.0032, 0.0048], "k": 0.003, "color": "@paw", "mirror": True})
add(d, {"id": "thigh", "type": "ell", "bone": "legHLu", "c": [hh[0] + 0.002, hh[1] - hh[3] * 0.45, hh[2]], "r": [0.014, 0.017, 0.008], "rot": [0, 0, 14], "k": 0.007, "color": "@body", "mirror": True, "hair": 0.1})
add(d, {"id": "shank", "type": "cone", "bone": "legHLl", "a": [hh[0], hh[1] - hh[3], hh[2]], "b": [hh[0] + 0.002, 0.006, hh[2]], "ra": 0.0055, "rb": 0.004, "k": 0.003, "color": "@leg", "mirror": True, "hair": 0.1})
add(d, {"id": "foot", "type": "ell", "bone": "footHL", "c": [hh[0] + 0.01, 0.0032, hh[2]], "r": [0.013, 0.0032, 0.0048], "k": 0.003, "color": "@paw", "mirror": True})
# the face: the muzzle a little longer and finer (pointed), the nose black; dark patches round the eyes
m = shape(d, "muzzle"); over(d, "muzzle", b=[m["b"][0] + 0.006, m["b"][1] - 0.001, 0], rb=m["rb"] * 0.85)
move(d, "nose", 0.006, -0.001, 0); d["nose"][0] += 0.006; d["muzzle"][3] += 0.006
e = d["sculpt"]["eyes"]["at"]
add(d, {"id": "eyePatch", "type": "ell", "op": "paint", "bone": "head", "c": [e[0] - 0.001, e[1], e[2] + 0.001], "r": [0.0105, 0.0075, 0.006], "rot": [0, 0, -20], "kc": 0.0015, "color": "@patch", "mirror": True})
w = shape(d, "whiskers"); w["len"] = [v * 0.9 for v in w["len"]]
# THE TAIL: thin, 22 cm, held back and a little up, black at the tip
a0, span, Rr = 1.3954, 0.40, 0.46
start = [-0.103 * S * 0.85, 0.047 * S + UP]
c = [start[0] - Rr * math.cos(a0), start[1] - Rr * math.sin(a0)]
d["tail"] = {"c": c, "R": Rr, "a0": a0, "a1": a0 + span, "r1": 0.011, "r2": 0.004, "n": 4, "sway": 16, "speed": 0.7}
pts = []
for i in range(8):
    t = i / 7; a = a0 + span * t
    pts.append([round(c[0] + Rr * math.cos(a) + (0.012 if i == 0 else 0), 4), round(c[1] + Rr * math.sin(a), 4), 0, round(0.0115 * (1 - t) + 0.0038 * t, 4)])
over(d, "tail", pts=pts, k=0.006, kc=0.003, tip="#1a1410", tipAt=0.8)
add(d, {"id": "tailTipP", "type": "ell", "op": "paint", "bone": "tail", "c": [pts[-1][0] + 0.004, pts[-1][1], 0], "r": [0.03, 0.012, 0.012], "kc": 0.002, "color": "@tailTip"})
# the coat: the weasel's shader pattern is metric for the weasel -- gone; bands across the back and a pale belly painted
for sh in shapes(d): sh.pop("pat", None)
d.pop("pat", None); d.pop("patOn", None)
top = d["rear"][1] + d["rear"][4]
for i, x in enumerate([-0.095, -0.075, -0.055, -0.035, -0.015, 0.005, 0.025]):
    add(d, {"id": f"band{i}", "type": "ell", "op": "paint", "bone": "body" if x < -0.02 else ("body2" if x < 0.012 else "body3"), "c": [x, top - 0.006, 0], "r": [0.0045, 0.014, 0.03], "kc": 0.002, "color": "@band"})
add(d, {"id": "bellyP", "type": "ell", "op": "paint", "c": [-0.03, d["rear"][1] - d["rear"][4] * 0.55, 0], "r": [0.12, 0.016, 0.026], "kc": 0.004, "color": "@belly"})
add(d, {"id": "throatP", "type": "ell", "op": "paint", "bone": "neck", "c": [d["neck"][0] + 0.012, d["neck"][1] - 0.012, 0], "r": [0.03, 0.012, 0.016], "kc": 0.003, "color": "@belly"})
recolor(d, body="#b8a98a", muzzle="#c4b69a", ear="#8a7a5e", leg="#b0a284", tail="#a89878", belly="#e0d6c0", paw="#3a3028", nose="#161210", patch="#2a2018", band="#8a7a5c", tailTip="#1a1410", whisker="#2a1e18", whiskerW="#2a1e18")
d["_about"] = "THE MEERKAT (2026-11-09, tools/creaturegen/dozen/meerkat.py): the least weasel's rig and sculpt at 1.3 on a trunk shortened to .85, the legs half again as long and the body raised with them (the leg shapes rewritten from the new hips), a thin 22 cm tail black at the tip, a pointed face with dark eye patches (paints), tan-grey with seven faint bands painted across the back and a pale belly; the weasel's sentinel pose kept. Written whole by its script."
save("mammals/meerkat", d)
index_add("creatures/mammals/meerkat", "Mammals")
if "--shot" in sys.argv: render("creatures/mammals/meerkat", "meerkat", views=("side", "q", "rear", "head"))
