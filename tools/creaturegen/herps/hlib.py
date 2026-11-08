# hlib.py -- helpers for the small sprawling herps written by agama.py, salamander.py and gila.py (2026-11-08).
# The rig is the wall lizard's (sc/others/gen/walllizard.py): body (the rear trunk, the root) -> chest (the front trunk,
# swinging about the middle of the back on the gait clock) -> nape (held against it, so the head keeps its line) -> head;
# body -> caud1..4 (the tail -- NOT named tail*: skeleton.js turns head|neck|tail parts on the world clock; these swing on
# the gait clock a beat apart and fade standing, amp); sprawled legs (prehistoric/rept.py limb_parts: the upper bone out
# to the side swinging fore and aft, the lower down, a lift on the forward swing). The sculpt overlay is written one shape
# a line (sc/others/gen/common.py dump, to the micrometre: these animals are a few centimetres thick), and the body field
# probed through sharp/fd.mjs (rept.fd) to lay the markings (paints: colour only) and root the SHARP parts on the skin.
import sys, os, math, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "prehistoric"))
from rept import *          # (vector helpers, interp, tube, Shapes, bent, fd, limb_parts, index_add)
import common

def _rnd6(v):   # (written to the micrometre, not common.rnd's tenth of a millimetre)
    if isinstance(v, float): return round(v, 6)
    if isinstance(v, list): return [_rnd6(x) for x in v]
    if isinstance(v, dict): return {k: _rnd6(x) for k, x in v.items()}
    return v
common.rnd = _rnd6

def rig(B, C, N, HD, TX, TIP, ty, tr, legs, body_r, sw=9, speed=0.9, tail_deg=(11, 13, 15, 17), swing=30, lift=14, head_dir=(0.015, -0.001)):
    """the wall lizard's parts rig. legs = (FS, FE, FW, HH, HK, HA, rf, rh): joints of the LEFT side, radii (3 each)"""
    parts = [
        {"id": "body", "parent": None, "shape": "tube", "size": tube([TX[0] - B[0], 0, 0], [C[0] - B[0], 0, 0], body_r, body_r), "pos": B, "color": "@back"},
        {"id": "chest", "parent": "body", "shape": "tube", "size": tube([0, 0, 0], [N[0] - C[0], N[1] - C[1], 0], body_r, body_r * 0.9), "pos": sub(C, B), "color": "@back",
         "anim": {"axis": "y", "deg": sw, "speed": speed, "phase": 0, "amp": True}},
        {"id": "nape", "parent": "chest", "shape": "tube", "size": tube([0, 0, 0], [HD[0] - N[0], HD[1] - N[1], 0], body_r * 0.7, body_r * 0.7), "pos": sub(N, C), "color": "@back",
         "anim": {"axis": "y", "deg": sw * 0.8, "speed": speed, "phase": PI, "amp": True}},
        {"id": "head", "parent": "nape", "shape": "tube", "size": tube([0, 0, 0], [head_dir[0], head_dir[1], 0], body_r * 0.6, body_r * 0.2), "pos": sub(HD, N), "color": "@back"},
    ]
    prev, at = "body", B
    for i, x in enumerate(TX):
        xe = TX[i + 1] if i + 1 < len(TX) else TIP
        p = [x, ty(x), 0]
        parts.append({"id": f"caud{i + 1}", "parent": prev, "shape": "tube", "size": tube([0, 0, 0], [xe - x, ty(xe) - ty(x), 0], tr(x), max(tr(xe), 1e-5)),
                      "pos": sub(p, at), "color": "@back",
                      "anim": {"axis": "y", "deg": tail_deg[i], "speed": speed, "phase": round(PI + 0.75 * (i + 1), 3), "amp": True}})
        prev, at = f"caud{i + 1}", p
    FS, FE, FW, HH, HK, HA, rf, rh = legs
    for S_, sz in (("L", 1), ("R", -1)):
        parts += limb_parts(S_, sz, "chest", "body", FS, FE, FW, HH, HK, HA, C, B, rf, rh, swing=swing, lift=lift, speed=speed)
    return parts

def sharp_ids(SH):
    return [s["id"] for s in SH if s.get("type") in ("horn", "fin")]

def frame(o, r, u=(1, 0, 0), v=(0, 1, 0)):
    return {"o": list(o), "u": list(u), "v": list(v), "r": r}

# ---- probing the skin
def rays_hits(sp, SH, rays):
    """rays: [[from, to], ...] from inside the body out -> the skin points (or None)"""
    return fd(sp, {"exclude": sharp_ids(SH), "rays": rays})["hits"]

def normals(sp, SH, pts, h=0.0002):
    """the field's gradient at skin points"""
    q = []
    for p in pts: q += [p, add(p, [h, 0, 0]), add(p, [0, h, 0]), add(p, [0, 0, h])]
    D = fd(sp, {"exclude": sharp_ids(SH), "points": q})["d"]
    out = []
    for i in range(len(pts)):
        d0, a, b, c = D[4 * i:4 * i + 4]
        out.append(nrm([a - d0, b - d0, c - d0]))
    return out

class Painter:
    """markings as PAINTS (op paint: colour only), each an ellipsoid laid on the probed skin.
    A mark: around a ray from an axis point `o` out in direction `d` (the skin point found on it), its long axis `along`
    (projected into the skin's tangent plane), half-sizes la (along) x lr (across), `depth` into the body."""
    def __init__(self, sp, SH):
        self.sp, self.SH, self.M = sp, SH, []
    def mark(self, id_, o, d, la, lr, col, bone, along=(1, 0, 0), depth=None, when=None, k=None, kc=None, mirror=False):
        self.M.append(dict(id=id_, o=list(o), d=nrm(d), la=la, lr=lr, col=col, bone=bone, along=list(along), depth=depth, when=when, k=k, kc=kc, mirror=mirror))
    def lay(self, reach=0.2):
        if not self.M: return []
        hits = rays_hits(self.sp, self.SH, [[m["o"], add(m["o"], m["d"], reach)] for m in self.M])
        ok = [(m, h) for m, h in zip(self.M, hits) if h]
        for m, h in zip(self.M, hits):
            if not h: print("   (paint missed:", m["id"], ")")
        ns = normals(self.sp, self.SH, [h for m, h in ok])
        out = []
        for (m, h), n in zip(ok, ns):
            al = nrm(sub(m["along"], mul(n, dot(m["along"], n))))
            ar = nrm(crs(n, al))
            dep = m["depth"] if m["depth"] is not None else 0.6 * min(m["la"], m["lr"]) + 0.0005
            k = m["k"] if m["k"] is not None else 0.15 * min(m["la"], m["lr"])
            q = {"id": m["id"], "type": "ell", "bone": m["bone"], "op": "paint", "c": h, "r": [m["la"], m["lr"], dep], "axes": [al, ar, n],
                 "k": k, "kc": m["kc"] if m["kc"] is not None else k, "color": m["col"]}
            if m["mirror"]: q["mirror"] = True
            if m["when"]: q = {"when": m["when"], **q}
            out.append(q)
        return out

def blotch(P, id_, o, d, size, col, bone, rng, rad, n=3, when=None, elong=1.0, jit=0.55):
    """an irregular blotch round a ray from the axis point o (direction d, square to x): n overlapping ellipses jittered in
    size and offset -- along the body by moving o, round it by turning d about x (rad: the body's radius there)"""
    for j in range(n):
        if j == 0: oo, dd, s = o, d, size
        else:
            a = rng.uniform(0, 2 * PI); off = size * jit * rng.uniform(0.5, 1.0)
            oo = add(o, [1, 0, 0], math.cos(a) * off * elong)
            ang = math.sin(a) * off / rad
            c, sn = math.cos(ang), math.sin(ang)
            dd = [d[0], d[1] * c - d[2] * sn, d[1] * sn + d[2] * c]
            s = size * rng.uniform(0.5, 0.8)
        la = s * elong * rng.uniform(0.8, 1.2); lr = s * rng.uniform(0.75, 1.15)
        P.mark(f"{id_}_{j}", oo, dd, la, lr, col, bone, when=when)

def ring_dir(phi_deg, side=1):
    """a direction round the x axis: 0 up (the dorsal midline), 90 the left flank (side -1: the right), 180 down"""
    a = math.radians(phi_deg)
    return [0, math.cos(a), side * math.sin(a)]

# ---- the tail: ONE sweep (docs/engines.md "Sweeps") along caud1..4 from x0 to the tip -- no beads where per-bone
# tubes overlapped, and its whip-thin end drawn as exact rings (end "point") rather than left to the grid
def sweep_tail(S, x0, tip, ty, tr, color, k, n=18, bands=None, end="point", pat=None, r_frame=None, **kw):
    xs = [x0 + (tip - x0) * (1 - (1 - t / n) ** 1.4) for t in range(n + 1)]   # (closer together towards the tip)
    pts = [[x, ty(x), 0, tr(x)] for x in xs]
    q = dict(type="sweep", bones=["caud1", "caud2", "caud3", "caud4"], pts=pts, k=k, color=color, **kw)
    if end: q["end"] = end
    if bands:   # [[x_from, x_to, colour]] -> shares of the arc
        arc = [0.0]
        for a, b in zip(pts, pts[1:]): arc.append(arc[-1] + math.dist(a[:3], b[:3]))
        share = lambda x: interp([(p[0], s / arc[-1]) for p, s in zip(pts, arc)], x)
        q["bands"] = [[round(share(a), 4), round(share(b), 4), c] for a, b, c in bands]
    if pat:
        d = nrm([pts[1][i] - pts[0][i] for i in range(3)])
        q["pat"] = pat; q["frame"] = frame(pts[0][:3], r_frame or tr(x0), d)
    S("tail", **q)

# ---- legs, feet and toes
def limb_shapes(S, u, l, s0, e, w, r0, r1, r2, r3, k=0.0012, col="@limb", **pat):
    S(u, type="tube", bone=u, pts=[s0 + [r0], lerp(s0, e, .35) + [r0 * .92], lerp(s0, e, .7) + [(r0 + r1) / 2], e + [r1]], k=k, color=col, mirror=True, **pat)
    S(l, type="tube", bone=l, pts=[e + [r1 * .95], lerp(e, w, .5) + [r2], w + [r3]], k=k * 0.6, color=col, mirror=True, **pat)

def digit(S, id_, bone, base, d, L, r0, y0, yt, col="@toe", tip=None, tipAt=0.8, blunt=False, droop=1.0, **pat):
    """a toe from inside the palm out along d (horizontal), sloping from y0 to yt at its end; blunt: a rounded end"""
    pts = []
    prof = ((0, 1.0), (.35, .92), (.65, .82), (.85, .7), (1.0, .55)) if not blunt else ((0, 1.0), (.4, .95), (.75, .92), (.93, .85), (1.0, .7))
    for t, f in prof:
        p = add(base, d, L * t); pts.append([p[0], y0 + (yt - y0) * (t ** droop), p[2], r0 * f])
    s = S(id_, type="tube", bone=bone, pts=pts, color=col, mirror=True, **pat)
    if tip: s["tip"] = tip; s["tipAt"] = tipAt
    tp = pts[-1]
    return (id_, bone, tp[:3], d, tp[3])

def claws(sp, SH, toes, length, yfloor, col="@claw", bend=0.18, need=0.5, flat=0.3):
    """a claw a horn on each toe's end, curving down to the ground, its root sunk in the toe"""
    from sharp2 import sink_many
    P, M = [], []
    for nm, bone, tip, dvec, r in toes:
        a = add(tip, dvec, -r * 1.2); a = [a[0], tip[1] + r * 0.15, a[2]]
        b = add(tip, dvec, length); b = [b[0], max(yfloor, tip[1] - r * 0.9 - length * 0.35), b[2]]
        P.append(bent(a, b, r * 0.85, bend=bend, up=[0, 1, 0], n=4, pw=0.75)); M.append((nm, bone))
    P = sink_many(sp, P, sharp_ids(SH), need=need)
    return [{"id": "claw" + nm[0].upper() + nm[1:], "type": "horn", "bone": bone, "pts": pts, "up": [0, 1, 0], "aspect": 1.25,
             "flat": flat, "sides": 8, "color": col, "fair": {"r": r * 0.5}, "mirror": True} for (nm, bone), pts, (_, _, _, _, r) in zip(M, P, toes)]

def back_table(sp, SH, xs, yin, ytop):
    """the back's top along the midline: (x, y) where a ray down from above meets the skin"""
    hits = rays_hits(sp, SH, [[[x, ytop, 0], [x, yin, 0]] for x in xs])
    return [(x, h[1]) for x, h in zip(xs, hits) if h]
