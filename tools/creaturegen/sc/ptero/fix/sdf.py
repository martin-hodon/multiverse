# sdf.py [json]: rest membrane points vs the sculpt's rest surface (union, blends ignored): the tris that cross it
import json, sys, math
import numpy as np
F = sys.argv[1] if len(sys.argv) > 1 else "/home/martin/store/apps/multiverse/assets/creatures/dinosaurs/pteranodon.json"
d = json.load(open(F)); D = math.pi / 180
def e2m(e):
    a, b, c = [x * D for x in e]
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Rx @ Ry @ Rz
def seg(P, a, b, ra, rb):
    a, b = np.array(a), np.array(b); ab = b - a; L2 = ab @ ab or 1e-9
    t = np.clip(((P - a) @ ab) / L2, 0, 1); q = a + t[:, None] * ab
    return np.linalg.norm(P - q, axis=1) - (ra + (rb - ra) * t)
shapes = []
for s in d["sculpt"]["shape"]:
    if s["type"] == "membrane": continue
    for m in ([1, -1] if s.get("mirror") else [1]):
        s2 = json.loads(json.dumps(s))
        if m < 0:
            for k in ("a", "b", "c"):
                if k in s2 and isinstance(s2[k], list) and len(s2[k]) == 3: s2[k][2] *= -1
            if "pts" in s2: s2["pts"] = [[p[0], p[1], -p[2], p[3]] for p in s2["pts"]]
            if "rot" in s2: s2["rot"] = [-s2["rot"][0], -s2["rot"][1], s2["rot"][2]]
        shapes.append(s2)
def sdf_one(s, P):
    t = s["type"]
    if t == "sphere": return np.linalg.norm(P - np.array(s["c"]), axis=1) - s["r"]
    if t == "cone": return seg(P, s["a"], s["b"], s["ra"], s["rb"])
    if t == "tube":
        pts = s["pts"]; out = np.full(len(P), 9.0)
        for i in range(len(pts) - 1): out = np.minimum(out, seg(P, pts[i][:3], pts[i + 1][:3], pts[i][3], pts[i + 1][3]))
        return out
    if t in ("ell", "box"):
        M = e2m(s.get("rot", [0, 0, 0])); L = (P - np.array(s["c"])) @ M; r = np.array(s["r"])
        if t == "ell": k = np.linalg.norm(L / r, axis=1); return (k - 1) * r.min()
        rd = s.get("round", 0); q = np.abs(L) - (r - rd)
        return np.linalg.norm(np.maximum(q, 0), axis=1) + np.minimum(q.max(1), 0) - rd
    if t == "tri":
        a, b, c = [np.array(s[k]) for k in "abc"]; n = np.cross(b - a, c - a); n /= np.linalg.norm(n)
        # (rough: distance to the plane inside the triangle's box, else to its edges)
        e = np.minimum(np.minimum(seg(P, a, b, 0, 0), seg(P, b, c, 0, 0)), seg(P, c, a, 0, 0))
        return e - s["r"]
    return np.full(len(P), 9.0)
mem = [s for s in d["sculpt"]["shape"] if s["type"] == "membrane"][0]
P = np.array(mem["pts"]); T = np.array(mem["tris"]).reshape(-1, 3); B = mem["bones"]
best = np.full(len(P), 9.0); who = [""] * len(P)
for s in shapes:
    if s["type"] in ("cone",) and ("Claw" in s["id"] or s["id"].startswith("toe")): pass
    v = sdf_one(s, P)
    for i in np.where(v < best)[0]: who[i] = s["id"]
    best = np.minimum(best, v)
def bn(v): e = mem["skin"][v]; return B[e[0]] + "/" + B[e[1]] if isinstance(e, list) else B[e]
h = mem.get("r", .0016)
cross = [t for t in T if best[t].min() < -h and best[t].max() > h]
print("points", len(P), "inside", int((best < -h).sum()), "outside", int((best > h).sum()), "crossing tris", len(cross))
from collections import Counter
cnt = Counter()
for t in cross:
    v = t[np.argmax(best[t])]; cnt[(bn(v), who[v])] += 1
for k, n in cnt.most_common(40): print(n, k)
if "-v" in sys.argv:
    for t in cross[:400]:
        for v in t: print(v, np.round(P[v], 3), round(float(best[v]), 4), bn(v), who[v])
        print()
if "-p" in sys.argv:
    lo, hi = [int(x) for x in sys.argv[sys.argv.index("-p") + 1].split(":")]
    for v in range(lo, hi): print(v, np.round(P[v], 3), round(float(best[v]), 4), bn(v), who[v])
if "-s" in sys.argv:
    vs = sorted({int(v) for t in cross for v in t if h < best[v]})
    for v in vs: print(v, np.round(P[v], 3), round(float(best[v]), 4), bn(v), who[v])
if "-r" in sys.argv:
    v = 0; i = 0
    while v < len(P):
        n = 9 if v < 216 else 4
        row = best[v:v + n]; print("row", i, v, bn(v + n - 1), "d:", " ".join(f"{x*1000:5.0f}" for x in row))
        v += n; i += 1
if "-g" in sys.argv:   # grazing: tris whose samples peek out by under 8 mm while part lies inside -- a sliver's signature
    bc = [(1/3,1/3,1/3),(.5,.5,0),(.5,0,.5),(0,.5,.5),(.7,.15,.15),(.15,.7,.15),(.15,.15,.7)]
    Q = np.array([sum(w * P[t[k]] for k, w in enumerate(b)) for t in T for b in bc])
    bq = np.full(len(Q), 9.0)
    for s in shapes: bq = np.minimum(bq, sdf_one(s, Q))
    bq = bq.reshape(len(T), len(bc)); out = Counter()
    for ti, t in enumerate(T):
        a = np.concatenate([bq[ti], best[t]])
        if a.min() < 0 and h < a.max() < .008: out[bn(t[0]).split("/")[-1]] += 1
    print("grazing", sum(out.values()), dict(out))
    for ti, t in enumerate(T):
        a = np.concatenate([bq[ti], best[t]])
        if a.min() < 0 and h < a.max() < .008 and bn(t[0]).startswith("body"): print("  body graze", list(t), "max", round(float(a.max()), 4), "at", np.round(Q[ti * len(bc) + int(np.argmax(bq[ti]))], 3) if bq[ti].max() >= best[t].max() else np.round(P[t[int(np.argmax(best[t]))]], 3))
if "-f" in sys.argv:   # crumples: neighbouring faces folded back on each other (rest), and faces turned inside out vs flight
    FL = np.array(json.load(open(SPF))) if False else None
    edges = {}
    for ti, t in enumerate(T):
        for a_, b_ in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])): edges.setdefault((min(a_, b_), max(a_, b_)), []).append(ti)
    def fn(t): n = np.cross(P[t[1]] - P[t[0]], P[t[2]] - P[t[0]]); return n / (np.linalg.norm(n) or 1)
    def rowof(v): return v // 9 if v < 216 else 24 + (v - 216) // 4
    out = Counter()
    for e, ts in edges.items():
        if len(ts) == 2:
            c = fn(T[ts[0]]) @ fn(T[ts[1]])
            if c < -0.3:
                m = (P[e[0]] + P[e[1]]) / 2; dd = float(min(best[e[0]], best[e[1]]))
                print("fold", e, "rows", rowof(e[0]), rowof(e[1]), "cos", round(float(c), 2), "at", np.round(m, 3), "d", round(dd * 1000), "mm")
