import math, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import *

P = "dinosaurs/ankylosaurus"
d = load(P)
d["_about"] = ("ANKYLOSAURUS MAGNIVENTRIS (sculpt overlay, 2026-11-05): 7.4 m, 1.55 m at the hips and nearly 2 m across -- a "
               "low, very broad body under a flattened dome of armour: transverse bands of keeled osteoderms with a mosaic of "
               "small ossicles between, a skirt of flat lateral spikes; short sprawling-elbowed legs; a broad triangular head, "
               "the squamosal horns at its back corners and the quadratojugal horns below them, a narrow beak; half-rings of "
               "osteoderms over the neck; a stiff tail ending in a .9 m club of two great osteoderms and a small one at the tip.")
d["rear"] = [-0.6, 1.15, 0, 1.2, 0.45, 0.95]
d["front"] = [0.8, 1.05, 0, 0.9, 0.42, 0.95]
d["neck"] = [1.5, 1.05, 0, 2.05, 0.98, 0, 0.36, 0.3]
d["head"] = [2.25, 1.0, 0, 0.34]
d["eyes"] = [2.52, 1.04, 0.26, 0.03]
HB = -0.18
d["legs"] = {"front": [1.15, 0.85, 0.6, 0.42], "hind": [-1.0 + HB, 0.95, 0.6, 0.48], "radii": [0.24, 0.19, 0.17],
             "foot": [0.22, 0.09, 0.22], "kneeH": 1, "kneeF": -1}
d["tail"] = {"c": [-1.55, -10.8], "R": 12, "a0": 1.5708, "a1": 1.8149, "r1": 0.36, "r2": 0.12, "n": 6, "links": True,
             "sway": 6, "speed": 0.3}
d.pop("pat", None); d.pop("patOn", None)
d["c"].update({"back": "#625a45", "body": "#6e6650", "scute": "#7c7459", "keel": "#544c3a", "belly": "#a99b78", "leg": "#5e5642",
               "foot": "#3a3226", "horn": "#6e6852", "beak": "#4a4032", "head": "#6e604a", "eye": "#2a2014", "lid": "#2e281e"})
FR = {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.4}
sc = {"pat": "scales", "frame": FR}
cut = {"pat": "scutes"}
S = Shapes()
# ---- the body: a deep gut under a low dome of armour, peaking mid-back, the flanks curving out over the skirt
S.ell("torso", [-0.1, 0.98, 0], [1.55, 0.44, 0.86], "@body", k=0.16, **sc)
S.ell("belly", [-0.1, 0.7, 0], [1.25, 0.26, 0.74], "@belly", k=0.14, kc=0.1, **sc)
S.ell("carapace", [-0.2, 1.12, 0], [1.65, 0.38, 0.98], "@back", k=0.16, **cut)
S.ell("dome", [-0.25, 1.3, 0], [1.25, 0.34, 0.7], "@back", k=0.18, **cut)
S.ell("skirt", [-0.2, 0.98, 0], [1.55, 0.13, 1.02], "@back", k=0.1, **cut)
def shieldY(x, z):   # (the top of carapace + dome, roughly)
    q1 = 1 - ((x + 0.2) / 1.65) ** 2 - (z / 0.98) ** 2
    q2 = 1 - ((x + 0.25) / 1.25) ** 2 - (z / 0.7) ** 2
    return max(1.12 + 0.38 * math.sqrt(max(q1, 0)), 1.3 + 0.34 * math.sqrt(max(q2, 0)) if q2 > 0 else 0)
# bands of keeled osteoderms across the shield: low cones, the keel a darker point, sizes varying
import random
rng = random.Random(7)
for b, x in enumerate([1.1, 0.68, 0.26, -0.16, -0.58, -1.0, -1.38]):
    zs = [0.22, 0.6] if -1.2 < x < 0.9 else [0.22, 0.5]
    for j, z in enumerate(zs):
        y = shieldY(x, z) - 0.04
        nz = z / 0.98 * 0.9
        r = (0.13 - 0.02 * j) * (0.85 + 0.3 * rng.random())
        tip = [x - 0.02, y + 0.1 * (1 - nz * 0.6), z + 0.1 * nz]
        S.cone(f"scute{b}_{j}", [x, y, z], tip, r, 0.035, "@scute", k=0.03, kc=0.02, mirror=True)
    zm = 0.95 * math.sqrt(max(0, 1 - ((x + 0.2) / 1.66) ** 2))
    zz = [-zm, -zm * 0.66, -zm * 0.33, 0, zm * 0.33, zm * 0.66, zm]
    S.tube(f"band{b}", [[x, shieldY(x, abs(q)) - 0.02 - 0.06 * (abs(q) / max(zm, 1e-3)) ** 2, q, 0.055] for q in zz], "@keel", k=0.03, kc=0.02)
    yc = shieldY(x, 0) - 0.04
    S.cone(f"scuteM{b}", [x, yc, 0], [x - 0.02, yc + 0.09, 0], 0.1 * (0.85 + 0.3 * rng.random()), 0.03, "@scute", k=0.03, kc=0.02)
# the lateral spikes: flat-based cones off the skirt, out, back and down
DIR = [-math.sin(math.radians(20)) * math.cos(math.radians(25)), -math.sin(math.radians(25)), math.cos(math.radians(20)) * math.cos(math.radians(25))]
for j, x in enumerate([1.15, 0.65, 0.15, -0.35, -0.85, -1.3]):
    ze = 1.0 * math.sqrt(max(0, 1 - ((x + 0.2) / 1.6) ** 2))
    ln = 0.35 - 0.03 * j; ra = 0.12 - 0.008 * j
    a = [x, 1.0, ze - 0.08]; b = [a[0] + DIR[0] * (ln + 0.08), a[1] + DIR[1] * (ln + 0.08), a[2] + DIR[2] * (ln + 0.08)]
    S.cone(f"spike{j}", a, b, ra, 0.03, "@horn", k=0.025, kc=0.01, mirror=True)
# ---- the neck under its half-rings
S.tube("neck", [[1.35, 1.05, 0, 0.42], [1.75, 1.0, 0, 0.35], [2.05, 0.98, 0, 0.31]], "@body", bone="neck", k=0.12, **sc)
for j, x in enumerate([1.55, 1.85]):
    for i, a in enumerate([50]):
        t = math.radians(a)
        S.cone(f"collar{j}_{i}", [x, 1.0 + 0.33 * math.cos(t), 0.33 * math.sin(t)], [x - 0.02, 1.0 + 0.45 * math.cos(t), 0.45 * math.sin(t)],
               0.11, 0.035, "@scute", bone="neck", k=0.025, kc=0.015, mirror=True)
# ---- the head: wider than long, flat-topped, a box of armour; pyramidal horns at its back corners and cheeks
S.box("skull", [2.36, 1.0, 0], [0.3, 0.15, 0.4], "@head", bone="head", k=0.1, round=0.08, **cut)
S.box("snout", [2.66, 0.94, 0], [0.16, 0.12, 0.32], "@head", bone="head", k=0.1, round=0.07, **sc)
S.ell("beak", [2.82, 0.89, 0], [0.07, 0.065, 0.22], "@beak", bone="head", k=0.04, kc=0.015)
S.ell("jaw", [2.48, 0.83, 0], [0.3, 0.09, 0.26], "@body", bone="head", k=0.06, kc=0.03)
S.cone("squamosal", [2.12, 1.06, 0.3], [1.98, 1.1, 0.5], 0.12, 0.035, "@horn", bone="head", k=0.03, kc=0.01, mirror=True)
S.cone("quadratojugal", [2.22, 0.88, 0.34], [2.14, 0.72, 0.47], 0.11, 0.035, "@horn", bone="head", k=0.03, kc=0.01, mirror=True)
S.ell("brow", [2.5, 1.11, 0.24], [0.1, 0.05, 0.08], "@keel", bone="head", k=0.03, mirror=True)
# ---- legs: short, the elbows out
S.cone("humerus", [1.15, 0.88, 0.58], [1.08, 0.45, 0.68], 0.2, 0.15, "@leg", bone="legFLu", k=0.08, mirror=True, **sc)
S.cone("forearm", [1.08, 0.45, 0.68], [1.17, 0.12, 0.64], 0.14, 0.12, "@leg", bone="legFLl", k=0.05, mirror=True, **sc)
S.ell("hand", [1.2, 0.08, 0.64], [0.18, 0.08, 0.17], "@foot", bone="footFL", k=0.04, mirror=True)
S.ell("thigh", [-0.98, 0.8, 0.56], [0.3, 0.38, 0.2], "@leg", bone="legHLu", k=0.1, mirror=True, **sc)
S.cone("shank", [-0.98, 0.5, 0.6], [-1.02, 0.12, 0.6], 0.16, 0.13, "@leg", bone="legHLl", k=0.05, mirror=True, **sc)
S.ell("foot", [-0.96, 0.08, 0.6], [0.22, 0.08, 0.18], "@foot", bone="footHL", k=0.04, mirror=True)
for i, a in enumerate([-35, 0, 35]):
    t = math.radians(a)
    S.ell(f"nail{i}", [-0.96 + 0.21 * math.cos(t), 0.05, 0.6 + 0.16 * math.sin(t)], [0.045, 0.04, 0.04], "@horn", bone="footHL", k=0.01, kc=0.004, mirror=True)
    if 0: S.ell(f"fnail{i}", [1.2 + 0.17 * math.cos(t), 0.05, 0.64 + 0.15 * math.sin(t)], [0.04, 0.035, 0.035], "@beak", bone="footFL", k=0.01, kc=0.004, mirror=True)
# ---- the tail, stiff, to its club (on its root bone: the chain is rigid)
S.tube("tail", [[-1.5, 1.15, 0, 0.38], [-2.3, 1.08, 0, 0.27], [-3.2, 0.98, 0, 0.14], [-4.0, 0.9, 0, 0.1], [-4.3, 0.87, 0, 0.1]],
       "@body", bone="tail", k=0.1, **sc)
for j, (x, z) in enumerate([(-1.9, 0.33), (-2.6, 0.24), (-3.3, 0.16)]):
    S.cone(f"tailSpike{j}", [x, 1.04 - 0.07 * j, z - 0.04], [x - 0.12, 0.98 - 0.07 * j, z + 0.14], 0.08, 0.025, "@horn", bone="tail", k=0.02, kc=0.01, mirror=True)
S.ell("club", [-4.45, 0.87, 0.22], [0.34, 0.17, 0.33], "@back", bone="tail", k=0.06, kc=0.03, mirror=True, **cut)
S.ell("clubTip", [-4.74, 0.86, 0], [0.13, 0.11, 0.13], "@back", bone="tail", k=0.05, kc=0.02, **cut)
for p in S:   # (the hind legs set further back under the rump: no overhanging buttock)
    if p.get("bone", "") in ("legHLu", "legHLl", "footHL"):
        for key in ("c", "a", "b"):
            if key in p: p[key][0] += HB
        for q in p.get("pts", []): q[0] += HB
floorR(S, ("spike", "tailSpike", "squamosal", "quadratojugal"), 0.027)
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; each shape rides the bone it names; `mirror` makes the right one from the left",
    "keep": [],
    "mesh": {"cell": 0.046, "tris": [9000, 2800]},
    "shape": [fix_order(p) for p in S],
    "eyes": {"at": [2.52, 1.04, 0.26], "from": [2.4, 1.0, 0], "r": 0.028, "iris": "@eye", "pupil": "round", "lid": "@lid"},
}
d["sculpt"]["shade"] = {"back": 0.82, "belly": 1.1, "low": 0.96, "on": "@body"}
save(P, d)
print(len(S), "shapes")
