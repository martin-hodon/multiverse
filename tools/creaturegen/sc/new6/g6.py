# g6.py -- shared helpers for the six new mammals (anteater, pangolin, hyena, skunk, impala, capybara)
import json, math, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import *          # (the ungulates' Sculpt, Frame, horn, surf, decals ... copied here)
REPO = "/home/martin/store/apps/multiverse/"
MAM = REPO + "assets/creatures/mammals/"

def rnd(v, n=4):
    if isinstance(v, float):
        r = round(v, n); return 0.0 if r == 0 else r
    if isinstance(v, list): return [rnd(x, n) for x in v]
    if isinstance(v, dict): return {k: rnd(x, n) for k, x in v.items()}
    return v

def dumps(d):
    """the repo's style: indent 2, each sculpt shape on one line"""
    def enc(o, ind):
        sp = "  " * ind
        if isinstance(o, dict):
            if not o: return "{}"
            items = []
            for k, v in o.items():
                if k == "shape" and isinstance(v, list):
                    inner = ",\n".join("  " * (ind + 2) + json.dumps(rnd(x), separators=(", ", ": "), ensure_ascii=False) for x in v)
                    items.append(f'{sp}  "{k}": [\n{inner}\n{sp}  ]')
                else:
                    items.append(f'{sp}  {json.dumps(k)}: {enc(v, ind + 1)}')
            return "{\n" + ",\n".join(items) + "\n" + sp + "}"
        if isinstance(o, list):
            if all(not isinstance(x, (dict, list)) for x in o):
                s = json.dumps(rnd(o), separators=(", ", ": "), ensure_ascii=False)
                return s if len(s) < 140 else "[\n" + ",\n".join(sp + "  " + json.dumps(rnd(x)) for x in o) + "\n" + sp + "]"
            return "[\n" + ",\n".join(sp + "  " + enc(x, ind + 1) for x in o) + "\n" + sp + "]"
        return json.dumps(rnd(o), ensure_ascii=False)
    return enc(d, 0) + "\n"

def path_of(name): return MAM + name + ".json"

def write_rig(name, rig):
    """the rig alone first (no sculpt): its joints are what the shapes are laid on"""
    d = dict(rig); d.pop("sculpt", None)
    open(path_of(name), "w").write(dumps(d))

def joints_of(name):
    out = subprocess.run(["node", os.path.join(HERE, "jj.mjs"), name, path_of(name)], capture_output=True, text=True, cwd=HERE)
    if out.returncode: raise SystemExit(out.stderr[-3000:])
    return json.loads(out.stdout)

def finish(name, rig, sculpt):
    d = dict(rig); d["sculpt"] = sculpt
    ids = [s.get("id") for s in sculpt["shape"] if s.get("id")]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup: raise SystemExit("duplicate ids " + str(dup))
    open(path_of(name), "w").write(dumps(d))
    print("wrote", path_of(name), len(sculpt["shape"]), "shapes")

def arc_through(P0, P1, h):
    """a rig tail arc {c, R, a0, a1} from root P0 to tip P1 (xy), bulging h metres to the LEFT of P0->P1 (h > 0: a
    tail running back bulges up when h < 0 ... the sign is the left normal's: for a tail running -x, left is -y)"""
    dx, dy = P1[0] - P0[0], P1[1] - P0[1]; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    if abs(h) < 1e-4: h = 1e-4
    R = (L * L / 4 + h * h) / (2 * abs(h)); s = 1 if h > 0 else -1
    mx, my = (P0[0] + P1[0]) / 2, (P0[1] + P1[1]) / 2
    cx, cy = mx - nx * s * (R - abs(h)), my - ny * s * (R - abs(h))
    a0 = math.atan2(P0[1] - cy, P0[0] - cx); a1 = math.atan2(P1[1] - cy, P1[0] - cx)
    while a1 - a0 > math.pi: a1 -= 2 * math.pi
    while a0 - a1 > math.pi: a1 += 2 * math.pi
    return {"c": [round(cx, 4), round(cy, 4)], "R": round(R, 4), "a0": round(a0, 4), "a1": round(a1, 4)}

def arc_pts(T, n=12):
    """points along a rig tail arc (root .. tip), with the angle's tangent"""
    cx, cy = T["c"]; R = T["R"]; out = []
    for i in range(n + 1):
        a = T["a0"] + (T["a1"] - T["a0"]) * i / n
        out.append([cx + R * math.cos(a), cy + R * math.sin(a)])
    return out

def tail_bones(T):
    """which bone a point t (0..1 along the tail) rides: mammals.js arcChain cuts one link per 1.2 rad"""
    nS = max(1, math.ceil(abs(T["a1"] - T["a0"]) / 1.2))
    return lambda t: "tail" if min(nS - 1, int(t * nS)) == 0 else f"tail{min(nS - 1, int(t * nS))}"

def skinband(S, id, path, color, proud=0.005, yc=0.47, k=0.006, kc=0.002, step=None, mirror=True, bone=None, da=8.0, cmax=0.09):
    """a band of paint laid ON the measured skin along a path round the body: each point (x, theta deg -- the angle round
    the trunk's axis from the flank's line, up positive -- half-width w), its skin found by a ray from (x, yc, 0) out
    along (0, sin, cos); flat ells laid tangent there, along the band, as deep as the skin's curvature across it so each
    stands `proud` over the band and sinks under the skin at its edges"""
    import math as _m
    qs = []
    for x, th, w in path:
        for dth in (0.0, -da, da):
            a = _m.radians(th + dth); qs.append({"x": x, "y": yc, "z0": 0.0, "dir": [0.0, _m.sin(a), _m.cos(a)]})
    hs = surf(S, qs)
    Q = []
    for i, (x, th, w) in enumerate(path):
        pts = []
        for j, dth in enumerate((0.0, -da, da)):
            h = hs[3 * i + j]
            if h["t"] is None: pts = None; break
            a = _m.radians(th + dth); pts.append([x, yc + h["t"] * _m.sin(a), h["t"] * _m.cos(a)])
        Q.append(pts)
    for i, (x, th, w) in enumerate(path):
        if Q[i] is None: print("skinband miss", id, i); continue
        P0, A, Bp = Q[i]
        nb = [q for q in (Q[i - 1] if i > 0 else None, Q[i + 1] if i + 1 < len(Q) else None)]
        prev = nb[0][0] if nb[0] else P0; nxt = nb[1][0] if nb[1] else P0
        along = sub(nxt, prev); across = sub(Bp, A)
        n = norm([along[1] * across[2] - along[2] * across[1], along[2] * across[0] - along[0] * across[2], along[0] * across[1] - along[1] * across[0]])
        a = _m.radians(th)
        if n[1] * _m.sin(a) + n[2] * _m.cos(a) < 0: n = mul(n, -1)
        ex = norm(sub(along, mul(n, sum(along[j] * n[j] for j in range(3)))))
        if ex[0] < 0: ex = mul(ex, -1)
        ey = [n[1] * ex[2] - n[2] * ex[1], n[2] * ex[0] - n[0] * ex[2], n[0] * ex[1] - n[1] * ex[0]]
        dd = length(across) / 2
        sag = max(0.0, -sum((lerp(A, Bp, 0.5)[j] - P0[j]) * n[j] for j in range(3)))
        kq = 2 * sag / max(dd * dd, 1e-9)
        rx = (step or (length(along) / (2 if (nb[0] and nb[1]) else 1))) * 0.8
        c = min(cmax, max(0.012, w * w * kq))
        ry_ = _m.degrees(_m.asin(max(-1, min(1, n[0])))); rx_ = _m.degrees(_m.atan2(-n[1], n[2])); rz_ = _m.degrees(_m.atan2(-ey[0], ex[0]))
        S.ell(f"{id}{i}", add(P0, n, -(c - proud)), [rx, w, c], rot=[round(rx_, 2), round(ry_, 2), round(rz_, 2)], bone=bone, k=k, kc=kc, color=color, mirror=mirror)
