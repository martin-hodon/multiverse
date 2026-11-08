# tailfix.py NAME -- (2026-11-07, after USER BUG #2, the elephant's tail) the same fix for the other kept RIG tails that
# stood off the rump: the rig chain (only its bone, "tail", now) is a path from INSIDE the rump at the dock, and the
# tail is sculpted on that bone -- out of a dock on the body, down close against the buttocks, ending in a brush of
# dark hair that tapers to a point (no faceted sphere). Patches the JSON in place; the old one is in sc/au/bak.
import json, sys
sys.path.insert(0, "/home/martin/store/apps/multiverse/tools/creaturegen/giants")
from lib import save, R

CFG = {
    # rhino: a short tail from high on the rump, flat against the buttocks, a flattened bristle brush at its end
    "rhinoceros": dict(
        path=[[-1.24, 1.62], [-1.53, 1.52], [-1.585, 1.2], [-1.56, 0.9]], sway=14, speed=1.0,
        dock=dict(c=[-1.33, 1.6, 0], r=[0.09, 0.07, 0.075], rot=[0, 0, 30], k=0.06),
        pts=[[-1.24, 1.62, 0, 0.062], [-1.37, 1.6, 0, 0.056], [-1.475, 1.5, 0, 0.048], [-1.557, 1.37, 0, 0.042],
             [-1.58, 1.22, 0, 0.038], [-1.567, 1.05, 0, 0.034]],
        brush=dict(a=[-1.567, 1.14, 0], b=[-1.557, 0.85, 0], ra=0.046),
        locks=dict(a_y=1.1, r=0.029, ends=[(0.045, 0.0, 0.88), (-0.04, 0.0, 0.87), (0.0, 0.045, 0.885), (0.0, -0.045, 0.885)]),
        k=0.022, cell=None),
    # cattle: from the tailhead straight down the back of the hindquarters to the hocks, the switch below them
    "cow": dict(
        path=[[-0.9, 1.43], [-1.05, 1.38], [-0.95, 0.9], [-0.88, 0.5]], sway=10, speed=0.6,
        dock=None,
        pts=[[-0.88, 1.43, 0, 0.046], [-0.98, 1.44, 0, 0.042], [-1.045, 1.37, 0, 0.037], [-1.018, 1.2, 0, 0.032],
             [-0.955, 1.0, 0, 0.029], [-0.915, 0.8, 0, 0.026], [-0.885, 0.6, 0, 0.025]],
        brush=dict(a=[-0.89, 0.7, 0], b=[-0.87, 0.34, 0], ra=0.052),
        locks=dict(a_y=0.66, r=0.026, ends=[(0.05, 0.0, 0.37), (-0.045, 0.0, 0.36), (0.02, 0.045, 0.38), (0.02, -0.045, 0.38), (-0.025, 0.04, 0.365), (-0.025, -0.04, 0.365)]),
        k=0.02, cell=None),
}
# giraffe: the tail rooted at the top of the steep rump and hanging close behind the buttocks (it was a rod 0.2-0.3 m
# behind them, joined by a stub of a dock), its long black tassel a spindle of hair
CFG["giraffe"] = dict(
    path=[[-0.78, 2.56], [-0.99, 2.45], [-0.95, 1.9], [-0.9, 1.3]], sway=10, speed=0.6, drop=["dock", "tassel"],
    dock=dict(c=[-0.84, 2.53, 0], r=[0.08, 0.055, 0.06], rot=[0, 0, 25], k=0.05),
    pts=[[-0.78, 2.56, 0, 0.05], [-0.88, 2.53, 0, 0.047], [-0.975, 2.42, 0, 0.042], [-1.0, 2.28, 0, 0.038], [-0.955, 2.1, 0, 0.033],
         [-0.93, 1.9, 0, 0.03], [-0.915, 1.7, 0, 0.028], [-0.905, 1.6, 0, 0.027]],
    brush=dict(a=[-0.905, 1.72, 0], b=[-0.893, 1.08, 0], ra=0.06),
    locks=dict(a_y=1.68, r=0.025, n=6),
    k=0.02, cell=None)
CFG["ox"] = dict(CFG["cow"],   # (the ox: its tailhead higher and further back, the hindquarters a little deeper)
    path=[[-0.93, 1.5], [-1.11, 1.46], [-1.02, 1.0], [-0.915, 0.5]],
    pts=[[-0.92, 1.5, 0, 0.046], [-1.03, 1.52, 0, 0.042], [-1.115, 1.44, 0, 0.037], [-1.085, 1.3, 0, 0.033], [-1.03, 1.1, 0, 0.03],
         [-0.995, 0.9, 0, 0.027], [-0.945, 0.7, 0, 0.025], [-0.92, 0.58, 0, 0.025]],
    brush=dict(a=[-0.925, 0.68, 0], b=[-0.905, 0.32, 0], ra=0.052),
    locks=dict(a_y=0.64, r=0.026, ends=[(0.05, 0.0, 0.35), (-0.045, 0.0, 0.34), (0.02, 0.045, 0.36), (0.02, -0.045, 0.36), (-0.025, 0.04, 0.345), (-0.025, -0.04, 0.345)]))

name = sys.argv[1]
C = CFG[name]
P = "mammals/" + name
d = json.load(open(R + P + ".json"))
sc = d["sculpt"]
sh = [q for q in sc["shape"] if not (q["id"].startswith("tail") and q["id"] != "tailhead") and q["id"] not in C.get("drop", [])]
old = d["tail"]
d["tail"] = {"path": C["path"], "r1": C["pts"][0][3], "r2": C["pts"][-1][3], "tuft": 0, "sway": C["sway"], "speed": C["speed"]}
if "tuftColor" in old: d["c"].setdefault("tuft", old["tuftColor"])
d["c"].setdefault("tail", d["c"].get("body") or d["c"].get("skin"))   # (the rig's tail colour, when it had none of its own)
T = "tail"
if C["dock"]: sh.append({"id": "tailDock", "type": "ell", **C["dock"], "color": "@" + ("back" if "back" in d["c"] else "body")})
sh.append({"id": "tail", "type": "tube", "bone": T, "pts": C["pts"], "k": C["k"], "color": "@tail"})
B = C["brush"]
# (the brush: a spindle of hair, fullest a little below where it starts, drawn to a point; locks bowing out round it)
lerp = lambda a, b, t: [a[i] + (b[i] - a[i]) * t for i in range(3)]
prof = [(0, 0.75), (0.22, 1), (0.45, 0.88), (0.7, 0.56), (1, 0.2)]
sh.append({"id": "tailBrush", "type": "tube", "bone": T, "pts": [lerp(B["a"], B["b"], t) + [round(B["ra"] * f, 4)] for t, f in prof],
           "k": C["k"], "color": "@tuft", "hair": 1})
import math
L = C["locks"]; A0, B0, ra = B["a"], B["b"], B["ra"]; n = L.get("n", 6)
for j in range(n):   # (locks round it, lying along its flanks as flutes, their ends a ragged point just past its own)
    th = j * 2 * math.pi / n + 0.2; cx, cz = math.cos(th), math.sin(th)
    at = lambda t, rf: [A0[0] + (B0[0] - A0[0]) * t + rf * ra * cx, A0[1] + (B0[1] - A0[1]) * t, rf * ra * cz]
    tip = at(1.04 + 0.02 * (j % 3), 0.38)
    sh.append({"id": f"tailLock{j}", "type": "tube", "bone": T, "pts": [at(0.08, 0.35) + [L["r"]], at(0.38, 0.74) + [L["r"]], at(0.72, 0.52) + [round(L["r"] * 0.72, 4)], tip + [0.008]],
               "k": round(C["k"] * 0.65, 4), "color": "@tuft", "hair": 1})
sc["shape"] = sh
sc["keep"] = [k for k in sc.get("keep", []) if k not in ("tail\\d*", "tailTuft", "tail")]
if C["cell"]: sc["mesh"]["cell"] = C["cell"]
if "focus" not in sc["mesh"]: sc["mesh"]["focus"] = {"head": 4}   # (the default it had)
sc["mesh"]["focus"]["tail"] = 4
save(P, d)
print(name, len(sh), "shapes, keep", sc["keep"])
