import math, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import *

P = "dinosaurs/stegosaurus"
d = load(P)
d["_about"] = ("STEGOSAURUS STENOPS (sculpt overlay, 2026-11-05): 7 m -- hind legs twice the fore, the back peaked high over "
               "the hips and falling to a tiny long low head carried under a metre up; 17 rounded-pentagonal plates in two "
               "staggered rows along the spine, the largest (.65 m) over the hips and the root of the tail; the tail held off "
               "the ground, ending in the thagomizer's four spikes pointing out and back. Countershaded olive, the plates "
               "flushed rust with darker rims.")
d["rear"] = [-0.5, 1.85, 0, 1.0, 0.55, 0.7]
d["front"] = [0.7, 1.45, 0, 0.8, 0.45, 0.62]
d["neck"] = [1.3, 1.5, 0, 2.05, 1.27, 0, 0.36, 0.2]
d["head"] = [2.15, 1.25, 0, 0.18]
d["eyes"] = [2.3, 1.3, 0.1, 0.03]
HB = -0.2
d["legs"] = {"front": [1.0, 1.1, 0.44, 0.5], "hind": [-0.6 + HB, 1.85, 0.45, 1.0], "radii": [0.2, 0.16, 0.13],
             "foot": [0.22, 0.08, 0.2], "kneeH": 1, "kneeF": -1}
d["tail"] = {"c": [-1.3, -3.8], "R": 6, "a0": 1.5708, "a1": 2.1138, "r1": 0.42, "r2": 0.06, "n": 7, "links": True, "sway": 8, "speed": 0.3}
d.pop("pat", None); d.pop("patOn", None)
d["c"].update({"back": "#565b3c", "body": "#6b704d", "belly": "#b4ac82", "leg": "#5f6446", "foot": "#3c3e2e",
               "plate": "#b0603a", "plateRim": "#a05a38", "spike": "#b8a888", "spikeBase": "#7a6c54", "beak": "#4a4032", "eye": "#2a2014", "lid": "#2e3024"})
FR = {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.4}
sc = {"pat": "scales", "frame": FR}
S = Shapes()
# ---- trunk, arched to the hips
S.ell("torso", [-0.1, 1.7, 0], [1.45, 0.6, 0.58], "@body", k=0.16, **sc)
S.ell("hips", [-0.55, 2.03, 0], [0.9, 0.45, 0.5], "@back", k=0.16, kc=0.12, **sc)
S.ell("chest", [0.85, 1.42, 0], [0.65, 0.48, 0.5], "@body", k=0.14, **sc)
S.ell("spine", [0.0, 2.1, 0], [1.3, 0.25, 0.3], "@back", k=0.14, kc=0.12, **sc)
S.ell("belly", [0.1, 1.2, 0], [1.1, 0.25, 0.48], "@belly", k=0.12, kc=0.1, **sc)
# ---- neck and the tiny low head
S.ell("neckRoot", [1.15, 1.5, 0], [0.5, 0.45, 0.44], "@body", k=0.18, **sc)
S.tube("neck", [[1.2, 1.55, 0, 0.38], [1.7, 1.4, 0, 0.26], [2.08, 1.27, 0, 0.17]], "@body", bone="neck", k=0.12, **sc)
S.ell("throat", [1.6, 1.3, 0], [0.4, 0.14, 0.2], "@belly", bone="neck", k=0.08, kc=0.06, **sc)
S.ell("skull", [2.24, 1.26, 0], [0.24, 0.13, 0.12], "@body", bone="head", k=0.06, rot=[0, 0, -10], **sc)
S.cone("snout", [2.3, 1.23, 0], [2.58, 1.13, 0], 0.11, 0.055, "@body", bone="head", k=0.05, **sc)
S.ell("jaw", [2.38, 1.13, 0], [0.2, 0.06, 0.08], "@belly", bone="head", k=0.04, kc=0.02, rot=[0, 0, -12])
S.ell("beak", [2.6, 1.12, 0], [0.05, 0.05, 0.05], "@beak", bone="head", k=0.02, kc=0.006)
# ---- legs
S.ell("scapula", [0.92, 1.42, 0.42], [0.24, 0.42, 0.16], "@body", bone="legFLu", k=0.1, rot=[0, 0, 30], mirror=True, **sc)
S.cone("humerus", [1.0, 1.1, 0.44], [0.94, 0.6, 0.48], 0.2, 0.14, "@body", bone="legFLu", k=0.07, mirror=True, **sc)
S.cone("forearm", [0.94, 0.6, 0.48], [1.02, 0.14, 0.45], 0.13, 0.1, "@leg", bone="legFLl", k=0.05, mirror=True, **sc)
S.ell("hand", [1.05, 0.08, 0.45], [0.15, 0.08, 0.14], "@foot", bone="footFL", k=0.04, mirror=True)
S.ell("thigh", [-0.56, 1.45, 0.42], [0.36, 0.55, 0.24], "@body", bone="legHLu", k=0.12, rot=[0, 0, 8], mirror=True, **sc)
S.ell("knee", [-0.55, 0.88, 0.45], [0.19, 0.17, 0.18], "@leg", bone="legHLu", k=0.07, mirror=True, **sc)
S.cone("shank", [-0.57, 0.86, 0.45], [-0.62, 0.14, 0.45], 0.18, 0.12, "@leg", bone="legHLl", k=0.06, mirror=True, **sc)
S.ell("foot", [-0.55, 0.08, 0.45], [0.23, 0.08, 0.17], "@foot", bone="footHL", k=0.04, mirror=True)
for i, a in enumerate([-35, 0, 35]):
    t = math.radians(a)
    S.ell(f"nail{i}", [-0.55 + 0.22 * math.cos(t), 0.05, 0.45 + 0.16 * math.sin(t)], [0.05, 0.04, 0.04], "@beak", bone="footHL", k=0.01, kc=0.004, mirror=True)
# ---- the tail on its own (rigid, swaying) chain: shapes on its root bone
S.tube("tail", [[-1.3, 2.2, 0, 0.42], [-2.0, 2.12, 0, 0.32], [-2.8, 1.95, 0, 0.21], [-3.6, 1.72, 0, 0.12], [-4.4, 1.45, 0, 0.05]],
       "@body", bone="tail", k=0.12, **sc)
S.tube("tailBelly", [[-1.3, 1.95, 0, 0.3], [-2.1, 1.92, 0, 0.21], [-2.9, 1.8, 0, 0.12]], "@belly", bone="tail", k=0.1, kc=0.08, **sc)
# ---- plates: two staggered rows along the spine's top line, pentagons (three slabs each) leaning a little out
top = [(1.5, 1.6), (1.0, 1.82), (0.4, 2.17), (-0.2, 2.38), (-0.6, 2.47), (-1.0, 2.44), (-1.4, 2.38), (-2.0, 2.3), (-2.8, 2.05), (-3.5, 1.76), (-4.0, 1.56)]
def topAt(x):
    for (x0, y0), (x1, y1) in zip(top, top[1:]):
        if x1 <= x <= x0:
            t = (x0 - x) / (x0 - x1); return y0 + (y1 - y0) * t, math.atan2(y1 - y0, x0 - x1)
    return top[-1][1], 0
plates = [(1.4, .2), (1.2, .26), (1.0, .33), (.78, .4), (.55, .48), (.3, .56), (.04, .63), (-.24, .68), (-.52, .72), (-.8, .74),
          (-1.08, .72), (-1.38, .66), (-1.68, .57), (-1.98, .47), (-2.28, .37), (-2.58, .28), (-2.88, .2)]
for i, (x, H) in enumerate(plates):
    y, slope = topAt(x)
    H *= 1.1
    rx = 0.08 + 0.3 * H
    side = 1 if i % 2 == 0 else -1
    lean = 12 * side
    t = math.radians(lean)
    bone = "body" if x > -1.25 else "tail"
    zb = 0.12 * side
    up = lambda h: [y + h * math.cos(t), zb + h * math.sin(t)]
    # a broad kite: a flattened oval sunk in the back, and its point a little behind its middle
    c0 = up(0.42 * H)
    S.ell(f"plate{i}", [x, c0[0], c0[1]], [rx, H * 0.48, 0.045], "@plate", bone=bone, k=0.04, kc=0.03, rot=[lean, 0, 6])
    a, b = up(0.7 * H), up(1.08 * H)
    S.cone(f"plateTip{i}", [x - 0.02, a[0], a[1]], [x - 0.09, b[0], b[1]], min(rx * 0.55, 0.16), 0.035, "@plateRim", bone=bone,
           k=0.04, kc=0.04)
# ---- the thagomizer: two pairs of spikes near the tip, out, up and back
for j, (x0, tip) in enumerate([(-3.7, [-4.1, 2.05, 0.5]), (-4.05, [-4.5, 1.85, 0.42])]):
    y0, _ = topAt(x0)
    S.cone(f"spike{j}", [x0, y0 - 0.1, 0.08], tip, 0.08, 0.03, "@spike", bone="tail", k=0.03, kc=0.01, mirror=True)
    S.ell(f"spikeBase{j}", [x0, y0 - 0.1, 0.1], [0.09, 0.08, 0.08], "@spikeBase", bone="tail", k=0.03, kc=0.02, mirror=True)
for p in S:   # (the hind legs set further back under the rump: no overhanging buttock)
    if p.get("bone", "") in ("legHLu", "legHLl", "footHL"):
        for key in ("c", "a", "b"):
            if key in p: p[key][0] += HB
        for q in p.get("pts", []): q[0] += HB
floorR(S, ("spike",), 0.025)
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; each shape rides the bone it names; `mirror` makes the right one from the left",
    "keep": [],
    "mesh": {"cell": 0.042, "tris": [9000, 2800]},
    "shape": [fix_order(p) for p in S],
    "eyes": {"at": [2.3, 1.3, 0.1], "from": [2.2, 1.27, 0], "r": 0.026, "iris": "@eye", "pupil": "round", "lid": "@lid"},
}
d["sculpt"]["shade"] = {"back": 0.8, "belly": 1.12, "low": 0.96, "on": "@body"}
save(P, d)
print(len(S), "shapes")
