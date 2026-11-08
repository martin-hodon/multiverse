# flyck.py name -- the spread wing aloft, by forward kinematics of the row bones (flyRot fully on): each tract row's root and tip
import sys, json, math
from nbwing import _rx, _ry, _rz
d = json.load(open(f"/home/martin/store/apps/multiverse/assets/creatures/birds/{sys.argv[1]}.json"))
P = {p["id"]: p for p in d["parts"]}
def world(pid):
    o = [0, 0, 0]; q = pid
    while q: o = [a + b for a, b in zip(o, P[q]["pos"])]; q = P[q]["parent"]
    return o
for s in d["sculpt"]["shape"]:
    if s.get("type") != "feathers" or s["id"] == "tail": continue
    out = []
    for r in s["rows"]:
        xb = r["bone"]; zb = P[xb]["parent"] if P[xb]["parent"].startswith("wz") else None; yb = P[zb or xb]["parent"]
        c = world(xb); q = world(yb); pz = world(zb) if zb else None
        al = math.radians(P[xb]["flyRot"][0]); be = math.radians(P[yb]["flyRot"][1]); ga = math.radians(P[zb]["flyRot"][2]) if zb else 0
        def T(v):
            v = [v[k] - c[k] for k in range(3)]; v = _rx(v, al); v = [v[k] + c[k] for k in range(3)]
            if zb: v = [v[k] - pz[k] for k in range(3)]; v = _rz(v, ga); v = [v[k] + pz[k] for k in range(3)]
            v = [v[k] - q[k] for k in range(3)]; v = _ry(v, be); return [round(v[k] + q[k], 3) for k in range(3)]
        out.append((T(r["at"]), T(r["to"])))
    print(s["id"], out)
