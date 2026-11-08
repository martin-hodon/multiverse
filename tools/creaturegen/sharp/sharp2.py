# sharp2.py: helpers for the second sharp pass (2026-11-08): every remaining POINTED part that was still a field shape
# (claws, nails, talons, teeth, spikes, horns, antlers, bills, beaks) converted to the engine's `horn` (sharp.js).
# Each family script (claws.py, teeth.py, spikes.py, antlers.py, bills.py ...) reads the field shapes it replaces from the
# species JSON and writes horns in their place, touching nothing else in the file; a second run finds them gone and stops.
# RE-RUN THESE AFTER ANY GENERATOR in tools/creaturegen/ that rewrites a species they touch (README "Reproducibility").
import os, shutil, json, math
from conv import *

BK = os.environ.get("SHARP2_BACKUP")   # (a folder: each species' JSON copied there once before its first write)

def replace(sp, ids, make, quiet=False):
    """the shapes `ids` of species `sp` replaced by make(old: {id: shape}) -> [new shapes], put where the first was;
    re-read just before writing (other agents edit other keys of the same files)"""
    txt, d = load(sp); sh = d["sculpt"]["shape"]
    idx = [i for i, s in enumerate(sh) if s.get("id") in ids]
    if not idx:
        if not quiet: print(sp, "nothing to convert:", ids)
        return False
    old = {s["id"]: s for s in sh if s.get("id") in ids}
    if any(s["type"] in ("horn", "fin") for s in old.values()):   # (converted already: a second run leaves it)
        if not quiet: print(sp, "already converted:", [i for i, s in old.items() if s["type"] in ("horn", "fin")][:6])
        return False
    new = [dedup(h) for h in make(old)]
    if BK:
        os.makedirs(BK, exist_ok=True)
        dst = os.path.join(BK, sp.replace("/", "__") + ".json")
        if not os.path.exists(dst): shutil.copy(path_of(sp), dst)
    txt2, d2 = load(sp)   # (once more: the file as it is now)
    sh2 = d2["sculpt"]["shape"]
    idx2 = [i for i, s in enumerate(sh2) if s.get("id") in ids]
    if not idx2: print(sp, "gone meanwhile"); return False
    out = sh2[:idx2[0]] + new + [s for i, s in enumerate(sh2) if i > idx2[0] and s.get("id") not in ids]
    save(sp, out, txt2)
    if not quiet: print(sp, "converted", len(old), "->", len(new), [s["id"] for s in new][:12])
    return True

def dedup(h, eps=1e-4):
    """a horn's points with no two at one place (sharp.js takes a zero-length segment's tangent as NaN and draws the
    horn as a sheet across the whole scene): a doubled point dropped -- at the tip, the one before it"""
    if h.get("type") != "horn": return h
    P = h["pts"]; out = [P[0]]
    for p in P[1:]:
        if ln(sub(p[:3], out[-1][:3])) < eps:
            if p is P[-1]: out[-1] = p   # (the tip keeps its place and its zero radius)
            continue
        out.append(p)
    h["pts"] = out
    return h

def pts_of(s):
    """a cone / tube / ell as a centreline [[x, y, z, r]...] (an ell: along its longest axis)"""
    t = s["type"]
    if t == "cone": return [list(s["a"][:3]) + [s["ra"]], list(s["b"][:3]) + [s["rb"]]]
    if t == "tube": return [list(p[:4]) for p in s["pts"]]
    if t == "horn": return [list(p[:4]) for p in s["pts"]]
    if t == "ell":
        ax = s.get("axes") or axes_of(s.get("rot")); r = s["r"]; i = max(range(3), key=lambda k: r[k])
        o = sorted(range(3), key=lambda k: r[k])
        rr = (r[o[0]] * r[o[1]]) ** .5
        a = nrm(ax[i]); c = s["c"]
        return [add(c, a, -r[i]) + [rr * .4], add(c, a, -r[i] * .5) + [rr * .87], list(c) + [rr], add(c, a, r[i] * .5) + [rr * .87], add(c, a, r[i]) + [rr * .4]]
    raise ValueError(t)

def perp_up(d, ref=(0, 1, 0)):
    """`ref` made square to d (its part across d); if d is nearly along ref, forward x instead"""
    u = sub(list(ref), mul(d, dot(ref, d)))
    if ln(u) < .25: u = sub([1, 0, 0], mul(d, d[0]))
    return nrm(u)

def depth(sp, pts, exclude):
    return fd(sp, {"exclude": exclude, "points": [p[:3] for p in pts]})["d"]

def sink(sp, P, exclude, need=0.5, maxk=4.0):
    """the root of centreline P made sure to be inside the body field: P[0] pushed back along the first segment until
    the body's distance there is below -need x its radius (at most maxk radii back); returns the new list"""
    return sink_many(sp, [P], exclude, need, maxk)[0]

def sink_many(sp, Ps, exclude, need=0.5, maxk=4.0):
    """sink() for many centrelines at once (one field build per step): first back along the first segment; a root still
    outside after maxk radii is walked DOWN THE FIELD'S GRADIENT instead (a tooth on the thin edge of a jaw: in toward
    its middle) -- the walk's end becomes the new root"""
    ks = [i * 0.5 for i in range(int(maxk / 0.5) + 1)]
    q = []
    for P in Ps:
        d0 = nrm(sub(P[0], P[1])); r = max(P[0][3], 1e-4)
        q += [add(P[0], d0, k * r) for k in ks]
    dd = depth(sp, [x + [0] for x in q], list(exclude))
    out, bad = [], []
    for j, P in enumerate(Ps):
        r = max(P[0][3], 1e-4); row = dd[j * len(ks):(j + 1) * len(ks)]
        k = next((i for i, v in enumerate(row) if v < -need * r), None)
        if k is None: bad.append(j); out.append(P); continue
        out.append(P if k == 0 else [q[j * len(ks) + k] + [P[0][3]]] + P)
    if bad:
        cur = {j: list(Ps[j][0][:3]) for j in bad}; done = {}
        for it in range(24):
            act = [j for j in bad if j not in done]
            if not act: break
            pts = []
            for j in act:
                c = cur[j]; h = max(Ps[j][0][3], 1e-4) * 0.25
                pts += [c] + [add(c, e, h) for e in ([1, 0, 0], [0, 1, 0], [0, 0, 1])]
            D = depth(sp, [p + [0] for p in pts], list(exclude))
            for n, j in enumerate(act):
                r = max(Ps[j][0][3], 1e-4); h = r * 0.25
                d0, gx, gy, gz = D[4 * n:4 * n + 4]
                if d0 < -need * r: done[j] = True; continue
                g = nrm([gx - d0, gy - d0, gz - d0])
                cur[j] = add(cur[j], g, -max(r * 0.35, (d0 + need * r) * 0.8))
        for j in bad:
            P = Ps[j]; c = cur[j]
            if j not in done: print("   (warning: root still not inside after the gradient walk)")
            # (the root, and a point between it and the old first point, so the spline turns in smoothly)
            out[j] = [c + [P[0][3]], lerp(c, P[0][:3], 0.6) + [P[0][3]]] + P
    return out

def bent(a, b, ra, bend=0.12, up=None, rmid=0.62, tip=0.0, ext=0.0, n=4, pw=0.8):
    """a straight claw a->b (radius ra at a) bent into an arc: its middle lifted `bend` of its length toward `up`
    (default: the up side square to it), ext carries the tip on past b (a share of the length) -- the points [x,y,z,r]"""
    d = nrm(sub(b, a)); L = ln(sub(b, a)) * (1 + ext); b2 = add(a, d, L)
    u = nrm(up) if up else perp_up(d)
    out = []
    for i in range(n + 1):
        t = i / n
        p = add(add(a, d, L * t), u, bend * L * 4 * t * (1 - t))
        # (the radius: full at the root, a smooth taper to the point -- a claw's outline)
        r = ra * (1 - t) ** pw if i < n else 0.0
        out.append(p + [r])
    return out

def chk(sp, horns, exclude=()):
    """each horn's root inside, its tip outside the body field: prints the depths"""
    for h in horns:
        P = h["pts"]; dd = depth(sp, [P[0], P[-1]], list(exclude))
        print("   ", h["id"], "root %.4f (r %.4f) tip %+.4f" % (dd[0], P[0][3], dd[1]))
