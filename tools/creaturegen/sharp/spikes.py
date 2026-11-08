# spikes.py SPECIES... | all : SPIKES and the ceratopsians' HORNS made the engine's `horn` (sharp.js):
#  - a chain (the stout field tube and its thin detail tip `kTip...`) merged into ONE centreline (horns.py merge: the root
#    sunk a radius into the boss, the tip a point), the boss ells (hornRoot, browBoss, spikeBoss) kept in the field as
#    the fillet it grows from;
#  - a single cone (ankylosaurus, stegosaurus, pachycephalosaurus) as a claw is (claws.py), straight or barely curved;
#  - the unicorn's horn: one straight horn and a thin RIDGE horn wound round it (helix(): the engine's `twist` turns
#    only where a ring's vertices sit, not the section, so a keel cannot spiral), in place of its five band ellipsoids;
#  - the blackbuck's (cervicapra) horns, a rig part until now (`extras` spiralHorn + `keep`): the same, four turns;
#  - the ram's coiled horn: one horn along the coil, its growth rings relief in the horn itself (the radius raised and
#    sunk every half pitch) -- the 17 ridge spheres gone (laid under a horn they z-fought with it).
# Run once per species. RE-RUN after the species' generator.
import sys, math, re, json
from sharp2 import *
from horns import merge
from claws import run as run1

def chains(sp, groups, **kw):
    """groups: [[id, id...]...] each merged into one horn named after the first"""
    txt, d = load(sp); S = d["sculpt"]["shape"]; ids = {s.get("id"): s for s in S}
    groups = [g for g in groups if all(i in ids for i in g)]
    if not groups: print(sp, "nothing to merge"); return
    allids = [i for g in groups for i in g]
    def make(old):
        out = []
        for g in groups:
            src = [old[i] for i in g]
            P = merge(src)
            h = horn_of(r5(P), src[0], **{"up": [0, 1, 0], **kw})
            for kk in ("tip", "tipAt"):
                if kk in src[-1] and kk not in h: h[kk] = src[-1][kk]
            if src[-1].get("color") != src[0].get("color") and "tip" not in h: h["tip"] = src[-1]["color"]; h["tipAt"] = 0.6
            out.append(h)
        P = sink_many(sp, [h["pts"] for h in out], allids, need=0.4)
        for h, p in zip(out, P): h["pts"] = r5(p)
        return out
    replace(sp, allids, make)

def kt(*names):   # (each field tube with its kTip)
    return [[n, "kTip" + n[0].upper() + n[1:]] for n in names]

def helix(pts, turns=3.0, t0=0.04, t1=0.9, rr=0.2, out=0.9, n=40, up=(1, 0, 0)):
    """a RIDGE spiralling round a straight horn's cone (pts: its centreline): `turns` round it from t0 to t1 of its
    length, its centre at out x the cone's radius there, its own radius rr x that -- a thread whose inner half is
    inside the horn (so it reads as a raised spiral), ending in a point. (The engine's `twist` turns only where the
    ring's vertices sit, not its shape: a keel does not spiral -- hence this.)"""
    a = pts[1][:3]; b = pts[-1][:3]; d = nrm(sub(b, a)); L = ln(sub(b, a))
    u = perp_up(d, up); w = crs(d, u)
    def rad(t):   # (the cone's radius at t of its length: along its points)
        s = [dot(sub(p[:3], a), d) / L for p in pts[1:]]; r = [p[3] for p in pts[1:]]
        for i in range(len(s) - 1):
            if s[i] <= t <= s[i + 1]: f = (t - s[i]) / ((s[i + 1] - s[i]) or 1); return r[i] + (r[i + 1] - r[i]) * f
        return r[-1]
    Q = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n; ph = 2 * math.pi * turns * i / n; R = rad(t)
        c = add(add(a, d, L * t), add(mul(u, math.cos(ph)), w, math.sin(ph)), R * out)
        Q.append(c + [R * rr if i < n else 0.0])
    # (its root: back inside the horn, under its first point)
    Q.insert(0, add(add(a, d, L * t0 * 0.5), u, rad(t0) * 0.3) + [Q[0][3]])
    return Q

def unicorn():
    sp = "monsters/unicorn"
    def make(old):
        h = old["horn"]; a, b = h["a"], h["b"]; d = nrm(sub(b, a)); L = ln(sub(b, a))
        ra = h["ra"]
        pts = [add(a, d, -ra * 0.9) + [ra], list(a) + [ra]] + [add(a, d, L * t) + [ra * (1 - t) ** 0.85] for t in (0.25, 0.5, 0.75, 0.92)] + [add(a, d, L * 1.06) + [0.0]]
        pts = sink(sp, pts, ["horn"] + ["hornBand%d" % i for i in range(5)], need=0.4)
        out = horn_of(r5(pts), h, up=r5(perp_up(d, (1, 0, 0))), sides=16)
        out["tip"] = "@hornRidge"; out["tipAt"] = 0.85
        rid = horn_of(r5(helix(pts, rr=0.26, out=0.95)), h, up=r5(perp_up(d, (1, 0, 0))), sides=6)
        rid["id"] = "hornRidge"; rid["tip"] = "@hornRidge"; rid["tipAt"] = 0.85
        return [out, rid]
    replace(sp, ["horn"] + ["hornBand%d" % i for i in range(5)], make)

def ram():
    """the ram's coiled horn: the field tube (lumpy, 17 ridge spheres blended on it -- the spheres z-fought with a horn
    laid over them, the last attempt) made ONE horn along the same coil, its GROWTH RINGS in the horn itself: the
    centreline resampled every half pitch (pitch 0.55 x the local radius) with the radius alternately raised and
    sunk (+5 % / -3 %), so each ring is real relief, never a second surface; the root sunk into the poll, the blunt
    end carried on to a point"""
    sp = "mammals/ram"
    def make(o):
        h = o["horn"]; P = [list(p) for p in h["pts"]]
        d = nrm(sub(P[-1], P[-2])); P.append(add(P[-1], d, P[-1][3] * 2.2) + [0.0])
        # (arc length along the polyline, and the point / radius at any length)
        acc = [0.0]
        for a, b in zip(P, P[1:]): acc.append(acc[-1] + ln(sub(b, a)))
        def at(s):
            for i in range(len(P) - 1):
                if s <= acc[i + 1]:
                    f = (s - acc[i]) / ((acc[i + 1] - acc[i]) or 1); return lerp(P[i][:4], P[i + 1][:4], f)
            return list(P[-1][:4])
        Q = [list(P[0][:4])]; s = 0.0; k = 0; Ltot = acc[-1]
        while True:
            r = at(s)[3]; s += max(0.55 * r, 0.004) / 2
            if s >= Ltot * 0.93: break
            q = at(s); k += 1
            q[3] *= 1.05 if k % 2 else 0.97
            Q.append(q)
        Q.append(at(Ltot * 0.965)); Q.append(list(P[-1][:3]) + [0.0])
        Q = sink(sp, Q, ["horn"] + ["ridge%d" % i for i in range(1, 18)], need=0.5)
        out = horn_of(r5(Q), h, up=[0, 1, 0], sides=16, n=len(Q) * 2)
        out.pop("n", None)
        return [out]
    replace(sp, ["horn"] + ["ridge%d" % i for i in range(1, 18)], make)

def cervicapra():
    """the blackbuck's horns were a rig part (mammals.js spiralHorn: a straight taper, `extras` + sculpt `keep`):
    now the sculpt's own -- each a straight horn, its root sunk into the poll, the SPIRAL a ridge wound round it four
    times (helix): the extras entry and the keep go"""
    sp = "mammals/cervicapra"
    B, T, r0 = [0.659, 1.198, 0.024], [0.526, 1.737, 0.143], 0.0175   # (the part's cone in the rest frame: t_dump.mjs)
    d = nrm(sub(T, B)); L = ln(sub(T, B))
    pts = [add(B, d, -r0 * 1.5) + [r0], B + [r0]] + [add(B, d, L * f) + [r0 * (1 - f) ** 0.75] for f in (0.25, 0.5, 0.75, 0.92)] + [add(B, d, L * 1.03) + [0.0]]
    pts = r5(sink(sp, pts, [], need=0.5))
    u = r5(perp_up(d, (1, 0, 0)))
    h = {"id": "horn", "type": "horn", "bone": "head", "pts": pts, "color": "#2a2420", "up": u, "sides": 14, "mirror": True, "when": "horns", "wet": 0.25}
    rg = {"id": "hornRidge", "type": "horn", "bone": "head", "pts": r5(helix(pts, turns=4.0, t0=0.03, t1=0.85, rr=0.28, out=0.92)), "color": "#2a2420", "up": u, "sides": 6, "mirror": True, "when": "horns"}
    txt, D = load(sp)
    if any(s.get("id") == "horn" for s in D["sculpt"]["shape"]): print(sp, "already"); return
    if BK:
        import shutil, os
        dst = os.path.join(BK, sp.replace("/", "__") + ".json")
        if not os.path.exists(dst): shutil.copy(path_of(sp), dst)
    save(sp, D["sculpt"]["shape"] + [h, rg], txt)
    # (the extras entry and the keep: out of the text as written, its layout untouched)
    L = open(path_of(sp)).read().split("\n")
    i = next(k for k, l in enumerate(L) if re.match(r'^  "extras": \[\s*$', l))
    j = next(k for k in range(i + 1, len(L)) if re.match(r'^  \],?\s*$', L[k]))
    blk = "\n".join(L[i:j + 1])
    assert "spiralHorn" in blk and blk.count('"component"') == 1, "extras: more than the horns"
    L = L[:i] + L[j + 1:]
    L = [l for l in L if l.strip() != '"keep": ["horn.*"],']
    out = "\n".join(L); json.loads(out); open(path_of(sp), "w").write(out)
    print(sp, "horns: rig part -> sculpt horn + spiral ridge")

HY = [["neck%sHorn%s%s" % (n, k, s), "neck%sHorn%s%sTip" % (n, k, s)] for n in "ABC" for k in ("", "2") for s in "LR"]

SPEC = {
    "dinosaurs/triceratops": lambda: chains("dinosaurs/triceratops", kt("browHorn", "noseHorn")),
    "dinosaurs/diabloceratops": lambda: chains("dinosaurs/diabloceratops", kt("browHorn", "noseHorn", "hook0", "hook1", "hook2", "hook3", "hook4", "spikeP1")),
    "dinosaurs/styracosaurus": lambda: chains("dinosaurs/styracosaurus", kt("noseHorn", "hookP1", "hookP2", "spikeP3", "spikeP4", "spikeP5", "spikeP6")),
    "monsters/hydra": lambda: chains("monsters/hydra", HY),
    "dinosaurs/ankylosaurus": lambda: run1("dinosaurs/ankylosaurus", [(r"spike\d", dict(bend=0.04, ext=1.5, aspect=0.55, need=0.4, rk=1.0)), (r"tailSpike\d", dict(bend=0.04, ext=1.5, aspect=0.6, need=0.4, rk=1.0))]),
    "dinosaurs/stegosaurus": lambda: run1("dinosaurs/stegosaurus", [(r"spike\d", dict(bend=0.05, ext=1.6, aspect=1.0, need=0.4, rk=1.0))]),
    "dinosaurs/pachycephalosaurus": lambda: run1("dinosaurs/pachycephalosaurus", [(r"spike\d", dict(bend=0.08, ext=1.2, aspect=1.0, need=0.4, rk=1.0))]),
    "monsters/unicorn": unicorn,
    "mammals/cervicapra": cervicapra,
    "mammals/ram": ram,
}

if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["all"]: args = list(SPEC)
    for a in args:
        sp = a if "/" in a else next(k for k in SPEC if k.endswith("/" + a))
        SPEC[sp]()
