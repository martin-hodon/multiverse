# THE KOALA (2026-11-09, dozen/koala.py): the giant panda's rig and sculpt at .45 (a 70 cm body), the panda's markings
# gone; big round fluffy ears with a pale fringe, a large black leathery nose, no tail to speak of (the stub inside the
# rump), a stocky grey body with a cream chest and belly, darker grey legs and face. Not a mount.
import sys, os, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dlib import *

def fin_scale(s, f, dz=0.0):
    """a fin's edge scaled about the middle of its root (the root kept), and pushed out along z by dz"""
    r0, r1 = s["root"][0], s["root"][-1]
    o = [(r0[i] + r1[i]) / 2 for i in range(3)]
    s["edge"] = [[o[i] + (p[i] - o[i]) * f + (dz if i == 2 else 0) for i in range(3)] + list(p[3:]) for p in s["edge"]]
    s["root"] = [[o[i] + (p[i] - o[i]) * min(f, 1.3) for i in range(3)] for p in s["root"]]
    if "thick" in s: s["thick"] *= f ** 0.5

S = 0.45
d = load("mammals/giantpanda")
scale_def(d, S)
d["name"] = "koala"; d["graze"] = 0.3; d["rest"] = 0.8; d["headTurn"] = 18
d.pop("coats", None); d["params"] = {"koala": True}
d["variants"] = {"joey": {"scale": 0.45}}
for sh in shapes(d): sh.pop("pat", None)
drop(d, "patchCore")
# the ears: big, round, FLUFFY -- a thick pad of fur, not a sheet (the panda's fin, however thick, is a sharp-rimmed
# sheet: seen edge-on from the far side it was a white spike above the head, 2026-11-10). A fat ellipsoid standing off
# the top-rear of the skull, grey, a paler fringe painted on its outer face and a cream hollow inside that
drop(d, "ear")
add(d, {"id": "ear", "type": "ell", "bone": "earL", "c": [0.301, 0.356, 0.074], "r": [0.04, 0.043, 0.024], "k": 0.012, "kc": 0.004, "color": "@ear", "mirror": True}, after="cheek")
add(d, {"id": "earFringe", "type": "ell", "op": "paint", "bone": "earL", "c": [0.301, 0.356, 0.088], "r": [0.036, 0.039, 0.014], "kc": 0.003, "color": "@earRim", "mirror": True}, after="ear")
add(d, {"id": "earHollow", "type": "ell", "op": "paint", "bone": "earL", "c": [0.303, 0.354, 0.096], "r": [0.022, 0.025, 0.008], "kc": 0.002, "color": "@earIn", "mirror": True}, after="earFringe")
# the nose: large, black, leathery -- and the muzzle short under a broad flat face
grow(d, "nose", 1.9, 1.8, 1.6); move(d, "nose", -0.004, 0.004, 0)
over(d, "nose", wet=0.15)
grow(d, "muzzle", 0.9, 1.0, 1.15); grow(d, "forehead", 1.15, 1.1, 1.25); grow(d, "cheek", 1.15, 1.15, 1.1)
drop(d, "lipLine")
# stocky: the trunk a little rounder, the legs a little shorter and thicker
for i in ("chest", "barrel", "rump"): grow(d, i, 1.0, 1.08, 1.1)
for i in ("arm", "forearm", "gaskin", "shin"): grow(d, i, 1.12)
# the tail: a stub hidden in the rump
d["tail"] = {"c": [-0.62 * S, 0.5 * S], "R": 0.02, "a0": -0.6, "a1": -1.4, "r1": 0.012, "r2": 0.008, "n": 2, "sway": 0, "speed": 0.5}
# the cream chest and belly, painted
add(d, {"id": "chestP", "type": "ell", "op": "paint", "c": [0.26 * S, 0.40 * S, 0], "r": [0.2 * S, 0.19 * S, 0.2 * S], "kc": 0.01, "color": "@cream"})
add(d, {"id": "bellyP", "type": "ell", "op": "paint", "c": [-0.03 * S, 0.3 * S, 0], "r": [0.36 * S, 0.1 * S, 0.19 * S], "kc": 0.01, "color": "@cream"})
add(d, {"id": "chinP", "type": "ell", "op": "paint", "bone": "head", "c": [0.82 * S, 0.555 * S, 0], "r": [0.07 * S, 0.035 * S, 0.06 * S], "kc": 0.004, "color": "@cream"})
recolor(d, body="#8a8c88", muzzle="#7e807c", head="#84867f", ear="#7c7e78", earRim="#e8e2d2", earIn="#d8d0c0", leg="#6e706b", black="#6e706b", foot="#5a5c58", tail="#8a8c88", nose="#1a1614", lid="#2a2622", claw="#2e2a28", cream="#e8e2d2", eye="#1a120c")
d["sculpt"]["shade"] = {"back": 1.0, "belly": 0.96, "low": 0.94, "on": "@body"}
d["_about"] = "THE KOALA (2026-11-09, tools/creaturegen/dozen/koala.py): the giant panda's rig and sculpt at .45 -- 70 cm, the panda's markings and eye patches gone; big round fluffy ears (fat ellipsoids off the skull, a pale fringe and a cream hollow painted on), a large black leathery nose, a broad flat face, a stub of a tail inside the rump, stocky on shorter thicker legs; grey, the chest, belly and chin cream (paints), legs darker grey. Variant `joey` at .45. Written whole by its script."
save("mammals/koala", d)
index_add("creatures/mammals/koala", "Mammals")
if "--shot" in sys.argv: render("creatures/mammals/koala", "koala", views=("side", "q", "rear", "head"))
