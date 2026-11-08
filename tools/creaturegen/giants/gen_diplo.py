import math, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import *

P = "dinosaurs/diplodocus"
d = load(P)
d["_about"] = ("DIPLODOCUS CARNEGII (sculpt overlay, 2026-11-05, after Hartman's and Paul's skeletals): 25 m -- a short deep "
               "body, the hips higher than the shoulders; a 6.5 m neck held out nearly level, rising a little to a small long "
               "low head with a broad square snout; a 12.5 m tail held off the ground, deep at its root and tapering to a "
               "whip; columnar legs, the forefeet hoof-like with one thumb claw, the hind with three claws; a row of low "
               "keratin spines along the midline. Countershaded drab olive, pale below.")
DY = 0.7
d["rear"] = [-1.5, 3.3 + DY, 0, 1.8, 1.0, 1.25]
d["front"] = [1.0, 3.1 + DY, 0, 1.6, 0.95, 1.25]
d["legs"] = {"front": [1.7, 2.55 + DY, 0.8, 1.55 * (2.55 + DY) / 2.95], "hind": [-1.9, 2.9 + DY, 0.75, 1.85 * (2.9 + DY) / 3.3], "radii": [0.42, 0.33, 0.29],
             "foot": [0.4, 0.15, 0.38], "kneeH": 1, "kneeF": -1}
def neckArc(S0, th0, xEnd, R):
    c = [S0[0] + R * math.sin(th0), S0[1] - R * math.cos(th0)]
    a0 = math.pi / 2 + th0; a1 = math.acos((xEnd - c[0]) / R)
    return {"c": c, "R": R, "a0": a0, "a1": a1}
NECK = neckArc([2.41, 3.3 + DY], math.radians(21), 9.0, 24.0)
print("neck end y", round(NECK["c"][1] + NECK["R"] * math.sin(NECK["a1"]), 2))
TAIL = {"c": [-3.0, -62.4 + DY], "R": 65.8, "a0": 1.5708, "a1": 1.7618}
d["tail"] = {**TAIL, "r1": 0.75, "r2": 0.05, "n": 8, "sway": 7, "speed": 0.25}
for x in d["extras"]:
    if x.get("id") == "neck":
        x["arc"].update({**NECK, "r1": 0.7, "r2": 0.22, "tuft": 0.22, "sway": 6, "speed": 0.25})
d.pop("pat", None); d.pop("patOn", None)
d["c"].update({"back": "#4a4834", "body": "#6c6a50", "belly": "#b8b090", "leg": "#5f5f4a", "foot": "#45443a",
               "claw": "#2e2c24", "spine": "#4a4836", "head": "#6e6c55", "eye": "#2a2014", "lid": "#3a3a2c", "mouth": "#3a2e26"})
sc = {"pat": "scales", "frame": {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.8}}
S = Shapes()

def arc_at(A, x):   # y on an arc at x (the arcs are shallow: one solution on the right side)
    c, R = A["c"], A["R"]
    return c[1] + math.sqrt(R * R - (x - c[0]) ** 2)

# ---- the body: short and deep, the hips the high point
S.ell("torso", [-0.3, 3.15, 0], [2.6, 1.12, 1.1], "@body", k=0.22, **sc)
S.ell("hips", [-1.7, 3.45, 0], [1.2, 0.7, 0.95], "@back", k=0.2, kc=0.15, **sc)
S.ell("chest", [1.35, 2.95, 0], [1.2, 0.95, 0.95], "@body", k=0.2, **sc)
S.ell("spine", [-0.4, 3.85, 0], [2.4, 0.3, 0.5], "@back", k=0.2, kc=0.15, **sc)
S.ell("belly", [0.0, 2.3, 0], [2.1, 0.42, 0.9], "@belly", k=0.18, kc=0.14, **sc)
# ---- the neck on its bone: out nearly level, tapering
xs = [1.9, 3.2, 4.5, 5.8, 7.1, 8.3, 8.95]
rs = [1.32, 1.0, 0.74, 0.56, 0.42, 0.3, 0.22]
S.tube("neck", [[x, arc_at(NECK, x) - (0.15 if i == 0 else 0), 0, r] for i, (x, r) in enumerate(zip(xs, rs))], "@body",
       bone="neck", k=0.16, **sc)
S.tube("neckBelly", [[x, arc_at(NECK, x) - r * 0.4 - (0.2 if i == 0 else 0), 0, r * 0.7] for i, (x, r) in enumerate(zip(xs[:-1], rs[:-1]))], "@belly", bone="neck",
       k=0.14, kc=0.1, **sc)
S.tube("neckTop", [[x, arc_at(NECK, x) + r * 0.5, 0, r * 0.5] for x, r in zip(xs[:-1], rs[:-1])], "@back", bone="neck",
       k=0.14, kc=0.1, **sc)
# ---- the head: small, long and low; the snout broad and square, the nostrils high over the eyes
hx, hy = 8.95, arc_at(NECK, 8.95)
S.ell("skull", [hx + 0.2, hy + 0.04, 0], [0.24, 0.16, 0.15], "@head", bone="neckTuft", k=0.06, **sc)
S.ell("snout", [hx + 0.5, hy - 0.06, 0], [0.26, 0.11, 0.15], "@head", bone="neckTuft", k=0.06, rot=[0, 0, -10], **sc)
S.ell("jaw", [hx + 0.42, hy - 0.15, 0], [0.26, 0.06, 0.13], "@head", bone="neckTuft", k=0.04, kc=0.02, rot=[0, 0, -8])
S.ell("mouth", [hx + 0.55, hy - 0.115, 0], [0.22, 0.01, 0.2], "@mouth", bone="neckTuft", k=0.01, op="sub")
S.ell("nares", [hx + 0.24, hy + 0.17, 0], [0.09, 0.05, 0.08], "@head", bone="neckTuft", k=0.04)
S.ell("brow", [hx + 0.3, hy + 0.11, 0.09], [0.06, 0.03, 0.04], "@head", bone="neckTuft", k=0.02, mirror=True)
# ---- the tail on its own bone: level and off the ground, to a whip
txs = [-2.0, -3.6, -5.4, -7.2, -9.0, -11.0, -13.0, -15.0]
trs = [0.85, 0.66, 0.48, 0.33, 0.2, 0.11, 0.06, 0.03]
S.tube("tail", [[x, arc_at(TAIL, x), 0, r] for x, r in zip(txs, trs)], "@body", bone="tail", k=0.16, **sc)
S.tube("tailBelly", [[x, arc_at(TAIL, x) - r * 0.4, 0, r * 0.65] for x, r in zip(txs[:5], trs[:5])], "@belly", bone="tail",
       k=0.14, kc=0.1, **sc)
S.tube("tailTop", [[x, arc_at(TAIL, x) + r * 0.45, 0, r * 0.5] for x, r in zip(txs[:5], trs[:5])], "@back", bone="tail",
       k=0.14, kc=0.1, **sc)
# ---- the midline spines (keratin, low): neck, back and tail
for j, x in enumerate([2.6, 3.6, 4.6, 5.6, 6.6, 7.6]):
    y = arc_at(NECK, x); r = 0.82 - 0.068 * j * 1.5
    S.tri(f"nspine{j}", [x + 0.12, y + r * 0.72, 0], [x - 0.12, y + r * 0.72, 0], [x - 0.08, y + r * 0.72 + 0.16, 0], 0.015,
          "@spine", bone="neck", k=0.01)
for j, x in enumerate([1.0, 0.2, -0.6, -1.4]):
    y = 4.12 if j else 4.05
    S.tri(f"bspine{j}", [x + 0.14, y, 0], [x - 0.14, y, 0], [x - 0.1, y + 0.18, 0], 0.015, "@spine", k=0.01)
for j, x in enumerate([-2.6, -3.6, -4.6, -5.6, -6.6, -7.6, -8.6]):
    r = trs[0] * (1 - (abs(x) - 2.0) / 9.0) if abs(x) < 10 else 0.1
    y = arc_at(TAIL, x) + max(r, 0.12) * 0.72
    h = 0.2 * (1 - j / 9)
    S.tri(f"tspine{j}", [x + 0.13, y, 0], [x - 0.13, y, 0], [x - 0.1, y + h, 0], 0.015, "@spine", bone="tail", k=0.01)
# ---- columnar legs
S.ell("scapula", [1.6, 3.0, 0.72], [0.45, 0.75, 0.25], "@body", bone="legFLu", k=0.16, rot=[0, 0, 20], mirror=True, **sc)
S.cone("humerus", [1.7, 2.5, 0.8], [1.68, 1.22, 0.82], 0.46, 0.34, "@leg", bone="legFLu", k=0.1, mirror=True, **sc)
S.cone("forearm", [1.68, 1.22, 0.82], [1.72, 0.2, 0.8], 0.34, 0.29, "@leg", bone="legFLl", k=0.08, mirror=True, **sc)
S.cone("manus", [1.72, 0.25, 0.8], [1.74, 0.0, 0.8], 0.3, 0.33, "@foot", bone="footFL", k=0.05, mirror=True)
S.cone("thumb", [1.92, 0.12, 0.9], [2.05, 0.03, 0.96], 0.06, 0.015, "@claw", bone="footFL", k=0.01, mirror=True)
S.ell("thigh", [-1.85, 2.2, 0.72], [0.7, 1.0, 0.48], "@body", bone="legHLu", k=0.18, rot=[0, 0, 6], mirror=True, **sc)
S.ell("knee", [-1.85, 1.35, 0.75], [0.42, 0.34, 0.4], "@leg", bone="legHLu", k=0.1, mirror=True, **sc)
S.cone("shank", [-1.88, 1.3, 0.75], [-1.92, 0.24, 0.75], 0.4, 0.33, "@leg", bone="legHLl", k=0.08, mirror=True, **sc)
S.ell("pes", [-1.82, 0.13, 0.75], [0.48, 0.15, 0.4], "@foot", bone="footHL", k=0.06, mirror=True)
for i, a in enumerate([-10, 15, 40]):
    t = math.radians(a)
    p0 = [-1.82 + 0.4 * math.cos(t), 0.1, 0.75 + 0.3 * math.sin(t)]
    S.cone(f"claw{i}", p0, [p0[0] + 0.16 * math.cos(t), 0.03, p0[2] + 0.16 * math.sin(t)], 0.06, 0.012, "@claw",
           bone="footHL", k=0.01, mirror=True)
FL, FH = (2.55 + DY) / 2.55, (2.9 + DY) / 2.9
for p in S:
    b = p.get("bone", "body"); f = None
    if b in ("legFLu", "legFLl") and not p["id"].startswith("scapula"): f = FL
    elif b in ("legHLu", "legHLl"): f = FH
    if f:
        for key in ("c", "a", "b"):
            if key in p: p[key][1] *= f
        if "r" in p and isinstance(p["r"], list): p["r"][1] *= f
    elif b == "body" or p["id"].startswith("scapula"):
        for key in ("c", "a", "b"):
            if key in p: p[key][1] += DY
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; each shape rides the bone it names; `mirror` makes the right one from the left",
    "keep": [],
    "mesh": {"cell": 0.09, "tris": [9500, 3000]},
    "shape": [fix_order(p) for p in S],
    "eyes": {"at": [hx + 0.3, hy + 0.06, 0.13], "from": [hx + 0.2, hy + 0.04, 0], "r": 0.035, "iris": "@eye", "pupil": "round",
             "lid": "@lid", "bone": "neckTuft"},
}
d["sculpt"]["shade"] = {"back": 0.8, "belly": 1.12, "low": 0.96, "on": "@body"}
save(P, d)
print(len(S), "shapes; head at", round(hx, 2), round(hy, 2), "tail tip y", round(arc_at(TAIL, -15.0), 2))
