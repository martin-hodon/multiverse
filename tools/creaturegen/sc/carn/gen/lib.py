import math
import os
# shared helpers for the carnivore generator: JSON in the repo's style, rounding, joints from the rig
import json, subprocess, math, copy, re
REPO = "/home/martin/store/apps/multiverse/"
SP = "/home/martin/store/apps/multiverse/tools/creaturegen/"
MAM = REPO + "assets/creatures/mammals/"

def rnd(v, n=4):
    if isinstance(v, float):
        r = round(v, n)
        return 0.0 if r == 0 else r
    if isinstance(v, list): return [rnd(x, n) for x in v]
    if isinstance(v, dict): return {k: rnd(x, n) for k, x in v.items()}
    return v

def dumps(d):
    """the repo's style: indent 2, but each sculpt shape on one line"""
    def enc(o, ind, key=None):
        sp = "  " * ind
        if isinstance(o, dict):
            if not o: return "{}"
            items = []
            for k, v in o.items():
                if k == "shape" and isinstance(v, list):
                    inner = ",\n".join("  " * (ind + 2) + json.dumps(rnd(x), separators=(", ", ": ")) for x in v)
                    items.append(f'{sp}  "{k}": [\n{inner}\n{sp}  ]')
                else:
                    items.append(f'{sp}  {json.dumps(k)}: {enc(v, ind + 1, k)}')
            return "{\n" + ",\n".join(items) + "\n" + sp + "}"
        if isinstance(o, list):
            if all(not isinstance(x, (dict, list)) for x in o):
                return json.dumps(rnd(o), separators=(", ", ": ")) if len(json.dumps(o)) < 140 else "[\n" + ",\n".join(sp + "  " + json.dumps(rnd(x)) for x in o) + "\n" + sp + "]"
            return "[\n" + ",\n".join(sp + "  " + enc(x, ind + 1) for x in o) + "\n" + sp + "]"
        return json.dumps(rnd(o))
    return enc(d, 0) + "\n"

def load(name): return json.load(open(MAM + name + ".json"))
def orig(name): return json.load(open(SP + "sc/carn/gen/" + name + "_orig.json"))
# THE HAUNCH (user review 2026-11-05: "too much protruding buttocks"): the wolf reads right -- its rump overhangs the back
# of its thigh by ~0.16 of the trunk (shoulder joint to hip joint). Each species saved through here with a sculpt is held
# to HAUNCH[name] (default 0.13): the shapes standing out behind the thigh drawn forward, the thigh set back, f : 1-f
HAUNCH = {"cat": 0.12, "lion": 0.12, "tiger": 0.12, "leopard": 0.12, "smilodon": 0.12, "bear": 0.12,
          "rat": 0.13, "hare": 0.12, "squirrel": 0.13, "beaver": 0.13, "dog": 0.13}
def _xmin(q):
    try:
        v = _xmin0(q); return v if isinstance(v, (int, float)) else None
    except TypeError: return None
def _xmin0(q):
    if q["type"] in ("ell", "sphere"):
        r = q["r"] if isinstance(q["r"], list) else [q["r"]] * 3; th = math.radians((q.get("rot") or [0, 0, 0])[2])
        return q["c"][0] - math.hypot(r[0] * math.cos(th), r[1] * math.sin(th))
    if q["type"] == "cone": return min(q["a"][0] - q["ra"], q["b"][0] - q["rb"])
    if q["type"] == "tube": return min(p[0] - p[3] for p in q["pts"])
    return None
def _shift(q, dx):
    for k in ("c", "a", "b"):
        if k in q and isinstance(q[k], list): q[k] = [q[k][0] + dx] + q[k][1:]
    if "pts" in q: q["pts"] = [[p[0] + dx] + p[1:] for p in q["pts"]]
    if isinstance(q.get("frame"), dict) and isinstance(q["frame"].get("o"), list): q["frame"] = {**q["frame"], "o": [q["frame"]["o"][0] + dx] + q["frame"]["o"][1:]}
def haunch(name, S, target, f=0.6):
    J = joints(name); L = J["legFLu"][0] - J["legHLu"][0]
    trunk = [q for q in S if (q.get("bone") or "body") == "body" and not q.get("mirror") and _xmin(q) is not None and not q["id"].startswith(("tail", "brush", "scut", "paddle"))]
    legs = [q for q in S if str(q.get("bone", "")).startswith("legHL") and _xmin(q) is not None]
    if not trunk or not legs: return None
    tr = min(_xmin(q) for q in legs)
    over = (tr - min(_xmin(q) for q in trunk)) / L
    if over <= target: return over
    d = (over - target) * L
    for q in trunk:
        if _xmin(q) < tr - 0.25 * d: _shift(q, f * d * min(1.0, (tr - _xmin(q)) / (over * L)))
    for q in legs:
        if q["id"] in ("thigh", "hams", "haunch") or _xmin(q) < tr + 0.3 * d: _shift(q, -(1 - f) * d)
    return over

def save(name, d):
    sc = d.get("sculpt") if isinstance(d, dict) else None
    if sc and sc.get("shape") and name in HAUNCH and os.path.exists(MAM + name + ".json"):
        was = haunch(name, sc["shape"], HAUNCH[name])
        if was is not None: print(f"  haunch {name}: overhang {was:.3f} -> held to {HAUNCH[name]}")
    open(MAM + name + ".json", "w").write(dumps(d))

def joints(name):
    out = subprocess.run(["node", SP + "t_joints.mjs", name], capture_output=True, text=True, cwd=SP)
    if out.returncode: raise SystemExit(out.stderr[-2000:])
    J = {}
    for line in out.stdout.splitlines():
        m = re.match(r"(\S+)\s+\[(.*)\]", line)
        if m: J[m.group(1)] = [float(x) for x in m.group(2).split(",")]
    return J

def mirror_ok(shapes):
    ids = [s.get("id") for s in shapes if s.get("id")]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup: raise SystemExit("duplicate ids " + str(dup))
    return shapes

def decal(id, bone, at, frm, r, color, out=None, rot=None, mirror=True, k=0.003, sink=0.55, kc=0.0015):
    """a mark SEATED on the surface the other shapes make, sunk by `sink` of its smallest radius (a cap stays proud)"""
    if out is None: out = -sink * (min(r) / max(r) if isinstance(r, list) else 1.0)
    s = {"id": id, "type": "ell" if isinstance(r, list) else "sphere", "bone": bone, "c": at, "r": r, "k": k, "kc": kc, "color": color,
         "seat": {"from": frm, "out": out}}
    if rot: s["rot"] = rot
    if mirror: s["mirror"] = True
    return s

def arc_tail(T, ring=None, n=8, k=0.4, kc=0.12, plain=None, tip=None, rad=None, extra=None):
    """THE TAIL SCULPTED from a rig's arc (mammals.js arcChain: one quadratic tube per 1.2 rad, its control where the end
    tangents cross): cones down each tube's curve on its own bone (tail, tail1, ...). ring(t) -> a shape's paint dict for
    the cone whose middle is t (0 root .. 1 tip) along the whole tail; k, kc as fractions of the local radius"""
    cx, cy = T["c"]; R = T["R"]; a0, a1 = T["a0"], T["a1"]; r1, r2 = T["r1"], T["r2"]
    nS = max(1, math.ceil(abs(a1 - a0) / 1.2)); dA = (a1 - a0) / nS
    pt = lambda a, rr=R: [cx + rr * math.cos(a), cy + rr * math.sin(a)]
    out = []
    for i in range(nS):
        A, B, C = pt(a0 + dA * i), pt(a0 + dA * (i + 1)), pt(a0 + dA * (i + 0.5), R / math.cos(dA / 2))
        rA, rB = r1 + (r2 - r1) * i / nS, r1 + (r2 - r1) * (i + 1) / nS
        bone = "tail" if i == 0 else f"tail{i}"
        q = lambda t: [(1 - t) ** 2 * A[j] + 2 * t * (1 - t) * C[j] + t * t * B[j] for j in range(2)]
        for j in range(n):
            t0, t1 = j / n, (j + 1) / n
            P0, P1 = q(t0), q(t1)
            ra, rb = rA + (rB - rA) * t0, rA + (rB - rA) * t1
            if rad: ra, rb = rad((i + t0) / nS), rad((i + t1) / nS)
            tg = (i + (t0 + t1) / 2) / nS
            s = {"id": f"{bone}Seg{j}", "type": "cone", "bone": bone, "a": [P0[0], P0[1], 0], "b": [P1[0], P1[1], 0], "ra": ra, "rb": rb,
                 "k": k * ra, "kc": kc * ra}
            s.update(ring(tg, P0, P1, ra) if ring else {"color": "@tail"})
            if extra: s.update(extra)
            out.append(s)
    if tip:
        E = pt(a1); out.append({"id": "tailTip", "type": "sphere", "bone": f"tail{nS - 1}" if nS > 1 else "tail", "c": [E[0], E[1], 0], "r": (rad(1.0) if rad else r2) * 1.02,
                                "k": 0.4 * r2, "kc": 0.1 * r2, "color": tip, **(extra or {})})
    return out

def cup_ear(Bi, Bo, M0, T, r, bone="earL", k=0.004, col="@ear", colIn="@earIn", ids=("ear", "earIn")):
    """THE CUPPED EAR (user review 2026-11-05: not a perfect cone): two thick triangles (field slabs, rounded at every edge
    and at the tip) from the base's inner and outer corners to the tip, folded along the midline M0 set back, so the front
    is an open hollow; the inside a pale plate laid in each half (mirrored to the other ear)"""
    sub3 = lambda u, v: [u[i] - v[i] for i in range(3)]
    cr3 = lambda u, v: [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
    out = []
    for j, (A, B) in enumerate(((Bi, M0), (M0, Bo))):
        out.append({"id": f"{ids[0]}{j}", "type": "tri", "bone": bone, "a": A, "b": B, "c": T, "r": r, "k": k, "kc": k * 0.4, "color": col, "mirror": True})
        nv = cr3(sub3(B, A), sub3(T, A)); ln = math.sqrt(sum(v * v for v in nv)); nv = [v / ln for v in nv]
        if nv[0] < 0: nv = [-v for v in nv]
        g = [(A[i] + B[i] + T[i]) / 3 for i in range(3)]
        p = lambda P, f: [g[i] + (P[i] - g[i]) * f + nv[i] * (r * 1.15 + 0.0004) for i in range(3)]
        out.append({"id": f"{ids[1]}{j}", "type": "tri", "bone": bone, "a": p(A, 0.7), "b": p(B, 0.7), "c": p(T, 0.62), "r": max(0.0003, r * 0.08), "color": colIn, "mirror": True})
    return out
