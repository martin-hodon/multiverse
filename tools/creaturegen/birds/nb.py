# nb.py -- a standing bird built from a body plan (units of its length, bill tip to tail tip), for the species that came
#   over from items/birds: the trunk, neck, head and bill, legs and toes, the folded wing (nbwing.py: its tracts and the
#   rig that spreads them aloft),
#   the tail fan and the species' own marks. bird(name, P) writes assets/creatures/birds/<name>.json
from bg import *
import math

def _rot(p, deg, o=(0, 0)):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a); x, y = p[0] - o[0], p[1] - o[1]
    return [o[0] + x * c - y * s, o[1] + x * s + y * c] + list(p[2:])

DEF = dict(
    tilt=20,                                  # (the trunk's pitch, front up)
    trunk=[.21, .13, .125], breast=[.13, .12, .115], bc=[.1, -.01],
    neck=[[.13, .07, .085], [.19, .11, .07]],  # (x, y, r) -- the last point under the head
    head=[.22, .14], hr=[.085, .075, .072],
    bill=dict(len=.08, r=.03, droop=12, curve=0, hook=0, depth=1.0, gape=.8),
    tail=dict(len=.36, w=.05, n=5, ang=-12, spread=.28, lens=None, outline="round", rows=5),
    fold=dict(S=[.1, .065, .115], T=[-.27, .005, .06], H=.11, w=.05, n=(2, 3, 3, 2), up=(0, .3, 1), pad=dict(), lay=True),
    tars=.13, legr=.011, toes=.1, legx=.01, legz=.05, web=None,
    eye=.022,
    mesh=[1800, 700], shade=(.85, 1.08),
    flags={"print": "bird", "shy": 6, "peck": 1.0},
    flight=dict(speed=1.6, beat=44, ext=.3, neck=None, flyTurn=None, hind=[-80, 10, -40], trail=70),
    walk=dict(deg=24, speed=1.0, flex=20),
    marks=[], extra=[],
)

def _rotM(deg):   # (sculpt.js's rotM: Euler XYZ, rows)
    x, y, z = [math.radians(v) for v in deg]; a, b, c, d, e, f = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    return [[c * e, -c * f, d], [a * f + b * e * d, a * e - b * f * d, -b * c], [b * f - a * e * d, b * e + a * f * d, a * c]]

def bird(name, about, L, colors, **kw):
    P = json.loads(json.dumps(DEF));
    for k, v in kw.items():
        if isinstance(v, dict) and isinstance(P.get(k), dict): P[k].update(v)
        else: P[k] = v
    t = P["tilt"]; u = L
    P["eye"] *= min(1, (.3 / L) ** .7)   # (an eye grows slower than its bird: a stork's is a pigeon's, not three of them)
    # ground: the belly's lowest point (tilted) above the toes by the tarsus
    tr = P["trunk"]
    low = min(_rot([tr[0] * math.cos(a), -tr[1] * abs(math.sin(a)) - .01], t)[1] for a in [i * math.pi / 12 for i in range(13)])
    Y = P["tars"] + P.get("tib", 0) - low + P.get("gap", .012)        # (trunk centre height, units)
    def B(p):   # (a body point: tilted about the trunk centre, then to metres)
        q = _rot(p, t); return [round(q[0] * u, 4), round((q[1] + Y) * u, 4)] + [round(x * u, 4) for x in p[2:]]
    def M(p): return [round(p[0] * u, 4), round((p[1] + Y) * u, 4)] + [round(x * u, 4) for x in p[2:]]   # (untilted)
    def R(r): return [round(x * u, 4) for x in r]
    def A(p): return [round(x * u, 4) for x in p]   # (absolute: ground at y 0)
    sh = []
    c = colors
    c.setdefault("wpad", c.get("cov", c["back"]))
    # ---- trunk ----
    KC = {"kc": P["kc"] * u} if P.get("kc") else {}   # (the body's paint blended sharper than its shape: a penguin's clean edges)
    sh += [
        ell("trunk", B([0, 0, 0]), R(tr), "@back", k=.06 * u, rot=[0, 0, t], **KC),
        ell("breast", B(P["bc"] + [0]), R(P["breast"]), "@under", k=.06 * u, rot=[0, 0, t], **KC),
        ell("belly", B([-.04, -.06, 0]), R([tr[0] * .7, tr[1] * .6, tr[2] * .8]), "@under", k=.06 * u, rot=[0, 0, t], **KC),
        ell("back", B([-.03, tr[1] * .55, 0]), R([tr[0] * .85, tr[1] * .45, tr[2] * .8]), "@back", k=.05 * u, rot=[0, 0, t], **KC),
        ell("rump", B([-tr[0] * .8, tr[1] * .15, 0]), R(P.get("rumpR", [.07, .06, .075])), "@rump", k=.05 * u, rot=[0, 0, t - 10], **KC),
        ell("vent", B([-tr[0] * .7, -tr[1] * .35, 0]), R(P.get("ventR", [.06, .05, .06])), "@vent", k=.04 * u, rot=[0, 0, t], **KC),
    ]
    # ---- neck and head (upright: the head is not tilted with the trunk) ----
    N = P["neck"]; nb2 = N[len(N) // 2] if len(N) > 2 else N[-1]
    nA = [M([p[0], p[1], 0, p[2]]) for p in N[:len(N) // 2 + 1]] if len(N) > 2 else [M([p[0], p[1], 0, p[2]]) for p in N]
    nB = [M([p[0], p[1], 0, p[2]]) for p in N[len(N) // 2:]] if len(N) > 2 else []
    nk = P.get("neckK", [.04, .03])   # (the neck tubes' blend: a slender neck wants less, or the blend fattens it)
    sh.append(tube("neckA", nA, "@neck", k=nk[0] * u, bone="neck"))
    if nB: sh.append(tube("neckB", nB, "@neck", k=nk[1] * u, bone="neck2"))
    hc, hr = P["head"], P["hr"]
    sh += [
        ell("skull", M(hc + [0]), R(hr), "@head", k=.035 * u, bone="head"),
        ell("crown", M([hc[0] - hr[0] * .1, hc[1] + hr[1] * .45, 0]), R([hr[0] * .75, hr[1] * .5, hr[2] * .75]), "@crown", k=.03 * u, kc=.02 * u, bone="head"),
        ell("cheek", M([hc[0] + hr[0] * .15, hc[1] - hr[1] * .2, hr[2] * .3]), R([hr[0] * .6, hr[1] * .55, hr[2] * .55]), "@cheek", k=.02 * u, kc=.015 * u, bone="head", mirror=True),
        ell("throat", M([hc[0] + hr[0] * .2, hc[1] - hr[1] * .7, 0]), R([hr[0] * .6, hr[1] * .45, hr[2] * .6]), "@throat", k=.02 * u, kc=.015 * u, bone="head"),
    ]
    # ---- the bill: upper and lower mandibles from the face, drooping `droop` deg, curving `curve` more at the tip ----
    b = P["bill"]; base = [hc[0] + hr[0] * b.get("baseX", .9), hc[1] - hr[1] * b.get("baseY", .12)]   # (baseX/baseY: where on the face the bill roots)
    def bp(f, dr):
        a = math.radians(-(b["droop"] + b["curve"] * f * f)); return [base[0] + math.cos(a) * b["len"] * f, base[1] + math.sin(a) * b["len"] * f + dr]
    up = []
    for i, f in enumerate([0, .35, .7, 1.0]):
        q = bp(f, b["r"] * .25 * b["depth"]); rr = b["r"] * (1 - .85 * f ** 1.3) * (1 if i < 3 else .4)
        up.append(M([q[0], q[1], 0, max(rr, .002 / u, b["r"] * b.get("tipR", 0) * (f >= .7))]))   # (tipR: the tip held this thick, so a hook stays joined on a coarse grid)
    if b["hook"]:   # (a raptor's or a gull's hooked tip)
        q = bp(1.0, b["r"] * .25 * b["depth"] - b["hook"]); up.append(M([q[0] - b["hook"] * .3, q[1], 0, .0025 / u + b["r"] * b.get("hookR", .12)]))   # (hookR: a long thin bill's nail kept thick enough to stay on the grid -- C 2026-11-07, the pelican's was a loose fleck)
    lo = []
    for f in [0, .4, .82 * b["gape"] + .1]:
        q = bp(f, -b["r"] * .45 * b["depth"]); lo.append(M([q[0], q[1], 0, max(b["r"] * .7 * (1 - .8 * f), .0018 / u)]))
    if b.get("comp"):   # (a toucan's: tall and narrow, laterally compressed -- each mandible a chain of ellipsoids, `comp` as wide as deep)
        def chain(b, when=None):
            out = []
            def bp(f, dr):
                a = math.radians(-(b["droop"] + b["curve"] * f * f)); return [base[0] + math.cos(a) * b["len"] * f, base[1] + math.sin(a) * b["len"] * f + dr]
            cm = b["comp"]; nU = 16; sp_ = b["len"] / (nU - 1); W = {"when": when} if when else {}
            if b.get("blade"):   # (a toucan's: the upper ONE smooth deep blade tapering to the tip, the lower a slimmer one
                #  set up inside it, so the two meet without a gap; the bill's colour zones (`zones`: [f0, f1, colour]) laid
                #  along the chain itself -- no marks standing proud of it)
                nU = 22; sp_ = b["len"] / (nU - 1); zn = b.get("zones", [])
                zc = lambda f, c0: next((z_[2] for z_ in zn if z_[0] <= f < z_[1]), c0)
                for i in range(nU):
                    f = i / (nU - 1); ry = b["r"] * (1 - b.get("tipK", .8) * f ** b.get("taper", 1.5)); rz = b["r"] * cm * (1 - b.get("wTip", .62) * f)
                    q = bp(f, b["r"] * .2 * b["depth"])
                    out.append({**W, **ell("upperBill%d" % i, M([q[0], q[1], 0]), R([sp_ * 1.8, max(ry, b.get("minR", .003) / u), max(rz, b.get("minR", .003) * .83 / u)]), zc(f, "@bill"),
                                           k=.02 * u, kc=.003 * u, bone="head", rot=[0, 0, round(-(b["droop"] + b["curve"] * f * f), 1)])})
                nL = 16; fl_ = .9
                for i in range(nL):
                    f = fl_ * i / (nL - 1); ry = b["r"] * (1 - b.get("tipK", .8) * f ** b.get("taper", 1.5))
                    q = bp(f, b["r"] * .2 * b["depth"] - ry * .9)
                    out.append({**W, **ell("lowerBill%d" % i, M([q[0], q[1], 0]), R([b["len"] * fl_ / (nL - 1) * 1.8, max(ry * b.get("lowK", .52), b.get("minR", .003) * .83 / u), max(b["r"] * cm * .9 * (1 - b.get("wTip", .62) * f), b.get("minR", .003) * .67 / u)]),
                                           "@billLo", k=.016 * u, kc=.003 * u, bone="head", rot=[0, 0, round(-(b["droop"] + b["curve"] * f * f), 1)])})
                return out
            for i in range(nU):
                f = i / (nU - 1); q = bp(f, b["r"] * .25 * b["depth"]); rr = max(b["r"] * (1 - .85 * f ** 1.3) * (1 if f < .95 else .6), .003 / u)
                out.append({**W, **ell("upperBill%d" % i, M([q[0], q[1], 0]), R([sp_ * 1.6, rr, rr * cm]), "@bill", k=.014 * u, kc=.002 * u, bone="head",
                              rot=[0, 0, round(-(b["droop"] + b["curve"] * f * f), 1)])})
            fl_ = .82 * b["gape"] + .1; nL = 12
            for i in range(nL):
                f = fl_ * i / (nL - 1); q = bp(f, -b["r"] * .45 * b["depth"]); rr = max(b["r"] * .7 * (1 - .8 * f), .0025 / u)
                out.append({**W, **ell("lowerBill%d" % i, M([q[0], q[1], 0]), R([b["len"] * fl_ / (nL - 1) * 1.6, rr, rr * cm]), "@billLo", k=.012 * u, kc=.002 * u, bone="head",
                              rot=[0, 0, round(-(b["droop"] + b["curve"] * f * f), 1)])})
            return out
        if b.get("alt"):   # (a second bill, `alt.s` times the first, for the coats whose params say so: the toco's, the biggest)
            al = b["alt"]; b2 = dict(b); b2["len"] *= al["s"]; b2["r"] *= al["s"]
            sh += chain(b, al["base"]) + [{**q, "id": q["id"] + "T"} for q in chain(b2, al["when"])]
        else: sh += chain(b)
    elif b.get("custom"): pass   # (a bill of the species' own, from its `extra`: a parrot's hooked one)
    else: sh += [tube("upperBill", up, "@bill", k=.008 * u, kc=.002 * u, bone="head"), tube("lowerBill", lo, "@billLo", k=.006 * u, kc=.002 * u, bone="head")]
    # ---- legs: the thigh in the belly feathers, the bare tarsus, toes (three forward, the hallux back) ----
    hipY = Y - tr[1] * .55; hx, hz = P["legx"], P["legz"]
    lr = P["legr"]; ta = P["tars"]; g = .012; hl = P.get("heel", 0)   # (heel: the ankle set back of the hip and the foot -- the bird's backward "knee")
    f0 = [hx + .01 + P.get("footFwd", 0), g, hz]   # (footFwd: the foot set forward of the ankle -- the tarsus slanting, the heel showing behind)
    sh += [
        ell("thigh", A([hx, hipY + .02, hz]), R(P.get("thighR", [.075, .08, .05])), "@thigh", k=.03 * u, bone="legL", mirror=True),
        cone("tibia", A([hx, hipY, hz]), A([hx - hl * (1 - P.get("tibBare", 0)), ta + .01 + (hipY - ta - .01) * P.get("tibBare", 0), hz]), lr * u * P.get("tibK", 1.25), lr * u * (1 + (P.get("tibK", 1.25) - 1) * P.get("tibBare", 0)), P.get("tibia", "@thigh"), k=.004 * u, bone="legL", mirror=True),   # (tibK: a drumstick's swell)
    ] + ([   # (tibBare: the lower part of the drumstick bare and scaly, the feathers ending above the heel -- a cassowary's)
        cone("tibiaLo", A([hx - hl * (1 - P["tibBare"]) + hl * .15, ta + .01 + (hipY - ta - .01) * P["tibBare"] * 1.15, hz]), A([hx - hl, ta + .01, hz]), lr * u * (1 + (P.get("tibK", 1.25) - 1) * P["tibBare"]) * .97, lr * u * .95, "@leg", k=.006 * u, bone="legL", mirror=True),
    ] if P.get("tibBare") else []) + [
        sph("ankle", A([hx - hl, ta + .01, hz]), lr * u * P.get("ankK", 1.05), "@leg", k=.004 * u, bone="tarsL", mirror=True),
        cone("tarsus", A([hx - hl, ta + .01, hz]), A(f0), lr * u, lr * u * .85, "@leg", k=.003 * u, bone="tarsL", mirror=True,
             pat="scales", frame={"o": "$tarsL", "u": [0, -1, 0], "r": .02}),
    ]
    tdz = P.get("toeDz", (.5, -.5))   # (toeDz: the outer and the inner toe's spread from the middle one)
    toes = (("toeM", 0, P["toes"]), ("toeO", .45, P["toes"] * .6)) if P.get("toes2") else (("toeM", 0, P["toes"]), ("toeO", tdz[0], P["toes"] * .85), ("toeI", tdz[1], P["toes"] * P.get("toeIK", .8)))
    tr_ = P.get("toeR", .7)
    if P.get("zygo"):   # (a parrot's, a woodpecker's, an owl's: two toes forward, two back)
        toes = (("toeM", .22, P["toes"]), ("toeI", -.22, P["toes"] * .85), ("toeO", -.35, -P["toes"] * .8), ("toeB", .3, -P["toes"] * .6))
    for nm, dz, Lt in toes:   # (an ostrich's two: the great inner toe and the small outer one; Lt < 0 points back)
        tipT = add(f0, nrm([1 if Lt > 0 else -1, -.1, dz]), abs(Lt))
        sh.append(cone(nm, A(f0), A(tipT), lr * u * tr_, lr * u * tr_ * .5, P.get("toeCol", "@leg"), k=.003 * u, bone="footL", mirror=True))
        if P.get("toePads"):   # (C final: a big walker's toe pads -- two swellings under each toe, so it reads as a padded toe, not a stick)
            dP = nrm([1 if Lt > 0 else -1, -.1, dz])
            for j_, f_ in enumerate((.22, .5, .76)):   # (three soft pads under the toe, inside its outline: a padded toe, no knobs)
                sh.append(sph(nm + "Pad%d" % j_, A(add(add(f0, dP, abs(Lt) * f_), [0, -lr * tr_ * .16, 0])), lr * u * tr_ * (1 - .5 * f_) * .98, P.get("toeCol", "@leg"), k=.006 * u, bone="footL", mirror=True))
        if P.get("talons") and not (P.get("dagger") and nm == "toeI"):   # (a raptor's or an owl's: a dark curved claw at each toe's tip, the toe itself feathered)
            dT = nrm([1 if Lt > 0 else -1, -.1, dz]); tl = P["talons"]
            sh.append(cone(nm + "Cl", A(add(tipT, dT, -.004)), A(add(add(tipT, dT, tl), [0, -tl * .55, 0])), lr * u * tr_ * P.get("clawK", .55), .0006, "@talon", k=.0015 * u, kc=.0005 * u, bone="footL", mirror=True))
        if P.get("dagger") and nm == "toeI":   # (a cassowary's: the inner toe's long straight dagger of a claw)
            # (pointing on forward, only a little inward -- along the toe's own line it crossed under the other foot --
            #  and level, its point clear of the ground)
            dT = nrm([1, -.02, dz * .3]); dl = P["dagger"]
            sh.append(cone("dagger", A(add(tipT, dT, -dl * .25)), A(add(add(tipT, dT, dl * .85), [0, dl * P.get("daggerUp", .03), 0])), lr * u * tr_ * P.get("daggerK", .62), .0012 * u, P.get("daggerCol", "@talon"),
                           k=.003 * u, kc=.001 * u, bone="footL", mirror=True))
    if not P.get("toes2") and not P.get("zygo") and not P.get("noHallux"):
        sh.append(cone("hallux", A(f0), A(add(f0, [-P["toes"] * .55, -.006, 0])), lr * u * .55, lr * u * .3, "@leg", k=.002 * u, bone="footL", mirror=True))
    if P["web"]:
        sh.append(ell("web", A(add(f0, [P["toes"] * .5, -.007, 0])), R([P["toes"] * .45, .004, P["toes"] * .4]), P["web"], k=.004 * u, bone="footL", mirror=True))
    # ---- the species' marks: ("b", ...) on the (tilted) body, ("h", ...) relative to the head's centre, ("m", ...) untilted ----
    for m in P["marks"]:
        kind, id, cc, rr, col = m[:5]; o = m[5] if len(m) > 5 else {}
        bone = o.pop("bone", "head" if kind == "h" else "body")
        if kind == "p":   # (a flat patch of paint: from a point by the head along `dir` to the surface)
            import nbwing
            sh.append(nbwing.paint(sh, id, M([hc[0] + cc[0], hc[1] + cc[1], cc[2]]), o.pop("dir"), *R(rr), col, bone=bone, **o)); continue
        if o.pop("bill", False) and b.get("alt"):   # (a mark on the bill: drawn for each bill, about its base, gated as it is)
            al = b["alt"]; bo = [base[0] - hc[0], base[1] - hc[1]]; kk = o.pop("k", .01); kc = o.pop("kc", kk * .4); rot = o.pop("rot", 0)
            for sfx, s_, w_ in (("", 1, al["base"]), ("T", al["s"], al["when"])):
                pp = [hc[0] + bo[0] + (cc[0] - bo[0]) * s_, hc[1] + bo[1] + (cc[1] - bo[1]) * s_, cc[2]]
                sh.append({"when": w_, **ell(id + sfx, M(pp), R([x * s_ for x in rr]), col, k=kk * u, kc=kc * u, bone=bone, rot=[0, 0, rot] if rot else None, **o)})
            continue
        if kind == "h": pos = M([hc[0] + cc[0], hc[1] + cc[1], cc[2]])
        elif kind == "b": pos = B(cc)
        else: pos = M(cc)
        rot = o.pop("rot", 0) + (t if kind == "b" else 0)
        kk = o.pop("k", .01); kc = o.pop("kc", kk * .4)
        sh.append(ell(id, pos, R(rr), col, k=kk * u, kc=kc * u, bone=bone, rot=[0, 0, rot] if rot else None, **o))
    if callable(P["extra"]): sh += P["extra"](B, M, R, u, sh) if P["extra"].__code__.co_argcount == 5 else P["extra"](B, M, R, u)
    # ---- the tail: a fan from the rump, angled `ang` from the trunk's line ----
    T_ = P["tail"]; root = [-tr[0] * .92, tr[1] * .12, 0]
    dirs, lens = [], []
    k = T_["rows"]
    for i in range(k):
        s_ = 1 - 2 * i / (k - 1)
        dirs.append(_rot([-1, 0, s_ * T_["spread"]], T_["ang"]))
        lens.append((T_["lens"][i] if T_["lens"] else 1) * T_["len"])
    rows = []
    for i, (d_, Ln) in enumerate(zip(dirs, lens)):
        a = B([root[0], root[1], (1 - 2 * i / (k - 1)) * T_["w"] * .8]); dd = _rot(d_, t)
        rows.append(row(a, [round(a[0] + dd[0] / math.sqrt(dd[0] ** 2 + dd[1] ** 2 + dd[2] ** 2) * Ln * u, 4),
                            round(a[1] + dd[1] / math.sqrt(dd[0] ** 2 + dd[1] ** 2 + dd[2] ** 2) * Ln * u, 4),
                            round(a[2] + dd[2] / math.sqrt(dd[0] ** 2 + dd[1] ** 2 + dd[2] ** 2) * Ln * u, 4)], T_["w"] * u))
    upv = _rot([0, 1, 0], t + T_["ang"])
    if T_.get("roof"):   # (the fan folded like a roof: each feather rolled out and its tip dropped by how far out it lies -- so seen from
        #  the side the outer feathers show their faces, and a band across the tail reads across it, not as a streak on its edge)
        ro = math.radians(T_["roof"])
        for i, r_ in enumerate(rows):
            s_ = 1 - 2 * i / (k - 1); L_ = math.dist(r_["at"], r_["to"])
            r_["to"] = [round(r_["to"][0], 4), round(r_["to"][1] - abs(s_) * math.tan(ro) * L_ * T_["spread"], 4), round(r_["to"][2], 4)]
            r_["up"] = [round(v, 4) for v in nrm([upv[0], upv[1] * math.cos(ro * s_), math.sin(ro * s_)])]
    sh.append(fea("tail", rows, T_["n"], "@tail", "@tailTip", outline=T_["outline"], up=[round(upv[0], 3), round(upv[1], 3), 0], camber=T_.get("camber", .12), curve=.02,
                  seed=5, **({"bars": T_["bars"]} if T_.get("bars") else {})))
    place(sh, ["tail"], [round(upv[0], 3), round(upv[1], 3), 0], .002 * u)
    if T_.get("band"):   # (a band straight across the tail: each tail feather's middle laid over in the band's colour, above and below)
        tb, tf = T_["band"], sh[-1]
        rr = [row([round(v, 4) for v in lerp(r_["at"], r_["to"], tb["f0"])], [round(v, 4) for v in lerp(r_["at"], r_["to"], tb["f1"])], r_["w"], up=r_.get("up")) for r_ in tf["rows"]]
        for sd, lf in (("B", .0007 * u), ("U", -.0007 * u))[:1 if tb.get("top") else 2]:   # (top: the upper face's band only)
            sh.append(fea("tail%s" % sd, json.loads(json.dumps(rr)), T_["n"], tb["col"], tb["col"], outline="round", up=tf["up"], camber=T_.get("camber", .12), curve=0,
                          lift=round(lf, 5), seed=5, layer=True, **({"bone": tf["bone"]} if tf.get("bone") else {})))
    if T_.get("strip"):   # (a band across the tail, above and below: three short blades over the fan, from its root out to the band's
        #  far edge, the tail's colour at the root and the band's at the tip -- rooted where the tail is, so none stands off it)
        ts, tf = T_["strip"], sh[-1]; r0_, rk_ = tf["rows"][0], tf["rows"][-1]; fe_ = ts["at"] + ts["w"] / 2
        lt = T_.get("camber", .12) * T_["w"] * u + .0006 * u
        for sd, lf in (("B", lt), ("U", -.0006 * u)):
            rr = [row(r_["at"], [round(v, 4) for v in lerp(r_["at"], r_["to"], fe_)], round(T_["w"] * u * .62, 4)) for r_ in (r0_, rk_)]
            sh.append(fea("tail%s" % sd, rr, 3, "@tail", ts["col"], outline="round", up=tf["up"], camber=0, curve=0,
                          lift=round(lf, 5), seed=9, **({"bone": tf["bone"]} if tf.get("bone") else {})))
    # ---- the folded wing ----
    F = P["fold"]; S = B(F["S"]); Tt = B(F["T"]); Hh = F["H"] * u
    if F.get("pad") is not None and not P.get("flipper"):   # (the folded wing as a SHAPE of its own: a flat teardrop laid ON the flank, standing
        #  `out` off it, blended in sharply -- its outline and edge crisp, its own shading -- the tracts then laid over it)
        pd = dict(out=.03, th=.035, k=.009, kc=.002, len=.5, h=.55, rim=0, tip=True); pd.update(F["pad"])   # (rim: a darker lip under the pad; off -- it read as a cavity on the dove and spiked on the pigeon)
        Lw = abs(F["S"][0] - F["T"][0])
        def onflank(x, y, out, th):   # (a centre on the flank at fold point (x, y): its far face `out` off the surface)
            c0 = B([x, y, 0]); zs = 0.
            while field(sh, [c0[0], c0[1], zs]) < 0 and zs < 2 * u: zs += .0005 * u
            return [c0[0], c0[1], round(zs + (out - th) * u, 4)]
        cx, cy = (F["S"][0] + F["T"][0]) / 2 + pd.get("dx", .03) + .1 * Lw, F["S"][1] - F["H"] * pd.get("dy", .45)
        rot = [pd.get("roll", -8), 0, t + pd.get("pitch", -6)]
        wc = onflank(cx, cy, pd["out"], pd["th"])
        if pd["rim"]:   # (the wing's outline: a darker skin of it, a shade larger, just under its face)
            h_ = c["wpad"].lstrip("#") if c["wpad"].startswith("#") else "808080"
            c["wrim"] = c.get("wrim") or "#%02x%02x%02x" % tuple(int(int(h_[i:i + 2], 16) * pd["rim"]) for i in (0, 2, 4))
            rz = pd.get("rimZ", .012)   # (its lip as deep as two mesh cells: a thinner one meshes in slivers)
            sh.append(ell("wingRim", [wc[0], wc[1], round(wc[2] - rz * u, 4)], R([Lw * pd["len"] * 1.05 + .008, F["H"] * pd["h"] * 1.05 + .008, pd["th"]]),
                          "@wrim", k=pd["k"] * u, kc=pd["kc"] * u, rot=rot, mirror=True))
        sh.append(ell("wing", wc, R([Lw * pd["len"], F["H"] * pd["h"], pd["th"]]), pd.get("col", "@wpad"), k=pd["k"] * u, kc=pd["kc"] * u, rot=rot, mirror=True))
        for i_, pt in enumerate(pd.get("patches", [])):   # (a wing's own marks on its face: a woodpecker's white shoulder, a hoopoe's bars)
            #  laid IN the pad: centred on its mid-plane, in its own frame, as thick as the pad is there and a hair more -- so it
            #  shows flush on the pad's face and can never stand off it (placed against the surface, they stood off as chips)
            ax_, ay_, at_ = Lw * pd["len"], F["H"] * pd["h"], pd["th"]
            qx, qy = F["S"][0] - pt["x"] * Lw - cx, F["S"][1] - pt["y"] * F["H"] - cy
            pa = math.radians(-pd.get("pitch", -6)); dx_, dy_ = qx * math.cos(pa) - qy * math.sin(pa), qx * math.sin(pa) + qy * math.cos(pa)
            hh = at_ * math.sqrt(max(.04, 1 - (dx_ / ax_) ** 2 - (dy_ / ay_) ** 2))
            Rm = _rotM(rot); off = [dx_ * u, dy_ * u, 0]
            pc = [round(wc[k_] + sum(Rm[k_][j_] * off[j_] for j_ in range(3)), 4) for k_ in range(3)]
            if pt.get("paint"):   # (C final: a PAINTED patch -- colour only, deep through the pad, so a thin bar shows its whole length)
                sh.append(ell("wingP%d" % i_, pc, R([pt["rx"] * Lw, pt["ry"] * F["H"], at_ * 2.5 + .004]), pt["col"], k=.0015 * u, kc=.0008 * u,
                              rot=[rot[0], 0, rot[2] + pt.get("rot", 0)], mirror=True, op="paint"))
                continue
            sh.append(ell("wingP%d" % i_, pc, R([pt["rx"] * Lw, pt["ry"] * F["H"], hh + .0025]), pt["col"], k=.0015 * u, kc=.0008 * u,
                          rot=[rot[0], 0, rot[2] + pt.get("rot", 0)], mirror=True))
        if pd.get("bars"):   # (a hoopoe's zebra: crisp bars ACROSS the pad's face -- each a row of short blades laid on it, in its own
            #  frame, at the face's height there and a hair off; short, so the face's curve never lifts their middles off or buries them)
            br = pd["bars"]; ax_, ay_, at_ = Lw * pd["len"], F["H"] * pd["h"], pd["th"]; Rm = _rotM(rot); nS = br.get("seg", 4)
            tl = math.tan(math.radians(br.get("tilt", 0)))
            def onpad(x, y, gap):
                z = at_ * math.sqrt(max(.02, 1 - (x / ax_) ** 2 - (y / ay_) ** 2))
                p_ = [wc[k_] + sum(Rm[k_][j_] * v * u for j_, v in enumerate((x, y, z))) for k_ in range(3)]
                n_ = nrm([sum(Rm[k_][j_] * v for j_, v in enumerate((x / ax_ ** 2, y / ay_ ** 2, z / at_ ** 2))) for k_ in range(3)])
                #  then onto the surface as MESHED (the pad melts into the flank, so its face stands above the bare ellipsoid's):
                #  along the normal to `gap` off the field
                lo_, hi_ = -.008 * u, .008 * u
                for _ in range(22):
                    m_ = (lo_ + hi_) / 2
                    if field(sh, add(p_, n_, m_)) < gap * u: lo_ = m_
                    else: hi_ = m_
                return [round(v, 4) for v in add(p_, n_, hi_)], n_
            for i_ in range(br["n"]):
                xb = ax_ * (br["x0"] + (br["x1"] - br["x0"]) * i_ / max(1, br["n"] - 1))
                Yb = ay_ * br.get("h", .8) * math.sqrt(max(0, 1 - (xb / ax_) ** 2)); sl = 2 * Yb / nS * 1.55   # (overlapping: one bar, not dashes)
                if br.get("paint"):   # (C final: a PAINTED bar -- colour through the pad, no blades: crisp, never beaded, no tris)
                    pc = [round(wc[k_] + Rm[k_][0] * xb * u, 4) for k_ in range(3)]
                    sh.append(ell("wingBar%d" % i_, pc, R([br["w"] * 1.3, Yb, at_ * 2.5 + .004]), br["col"], k=.0015 * u, kc=.0008 * u,
                                  rot=[rot[0], 0, rot[2] - br.get("tilt", 0)], mirror=True, op="paint"))
                    continue
                rows = []
                for j_ in range(nS):
                    yc = -Yb + 2 * Yb * (j_ + .5) / nS; y0, y1 = yc + sl / 2, yc - sl / 2
                    p0, n0 = onpad(xb + tl * y0, y0, br.get("gap", .0012)); p1, n1 = onpad(xb + tl * y1, y1, br.get("gap", .0012))
                    rows.append(row(p0, p1, round(br["w"] * u, 4), up=[round(v, 4) for v in nrm(add(n0, n1))]))
                sh.append(fea("wingBar%d" % i_, rows, nS, br["col"], br["col"], outline="round", camber=.02, curve=0, lift=0, seed=40 + i_, layer=True, mirror=True))
        if pd["tip"]:   # (the primaries' stack narrowing back to its point over the tail: the teardrop's tail)
            tx, ty = F["T"][0] + .3 * Lw, F["T"][1] - F["H"] * .15
            sh.append(ell("wingTip", onflank(tx, ty, pd["out"] * .8, pd["th"] * .7), R([Lw * .32, F["H"] * .26, pd["th"] * .7]), pd.get("tipCol", "@prim"),
                          k=pd["k"] * 1.5 * u, kc=pd["kc"] * u, rot=[rot[0], 0, rot[2] + 4], mirror=True))
    elif not P.get("flipper"): sh.append(ell("wing", B([(F["S"][0] + F["T"][0]) / 2 + .03, F["S"][1] - F["H"] * .45, F["S"][2] * .82]), R([abs(F["S"][0] - F["T"][0]) * .42, F["H"] * .5, .03]),
                  "@cov", k=.03 * u, rot=[-8, 0, t - 6], mirror=True))
    parts = make_parts(P, u, Y, hc, N, nb2, hipY, colors)
    d = {"name": name, "kind": "parts", "_about": about, "flags": dict(P["flags"]), "colors": c, "parts": parts}
    d["_bodyY"] = round(Y * u, 4)
    from wader import legs
    legs(d, round(hipY * u, 4), round((ta + .01) * u, 4), P["walk"]["deg"], P["walk"]["speed"], P["walk"]["flex"])
    for p in d["parts"]:   # (wader.legs puts the foot .012 m off the ground: here it is g units)
        if p["id"].startswith("foot"): p["pos"][1] = round((g - ta - .01) * u, 4)
        if hl and p["id"].startswith("tars"): p["pos"][0] = round(p["pos"][0] - hl * u, 4)   # (the heel's joint where the mesh's heel is)
        if (hl or P.get("footFwd")) and p["id"].startswith("foot"): p["pos"][0] = round(p["pos"][0] + (hl + P.get("footFwd", 0)) * u, 4)
    del d["_bodyY"]
    if P.get("waddle"):   # (a penguin's: the body rocked side to side once a stride)
        for p in d["parts"]:
            if p["id"] == "body": p["anim"] = {"axis": "x", "deg": P["waddle"], "speed": P["walk"]["speed"], "phase": 0, "amp": True}
    import nbwing
    info = nbwing.wing(d, sh, P, S, Tt, Hh, u, c)   # (the folded wing's tracts, and the rig that spreads them aloft)
    if callable(P.get("post")): sh += P["post"](B, M, R, u, sh)   # (shapes laid OVER the folded wing's roots: an owl's coverts)
    nbwing.flight(d, P)
    print("  %s: span %.2f m, fold %.3f m, hidden: fold %.4f spread %.4f" % (name, info["span"], info["Lf"], info["hideFold"], info["hideSpread"]))
    sh.sort(key=lambda s: s.get("type") == "feathers")
    hcM = M(hc + [0])
    d["sculpt"] = {
        "_about": "x forward, y up, z left, metres; built by nb.py from the body plan",
        "mesh": {"tris": P["mesh"], **({"focus": P["focus"]} if P.get("focus") else {}), **({"cell": P["cell"]} if P.get("cell") else {})},
        "shade": {"back": P["shade"][0], "belly": P["shade"][1], "k": round(.05 * u, 4), "on": "@back"},
        "eyes": {"at": M(add(hc + [0], P.get("eyeAt") or [hr[0] * .42, hr[1] * .12, hr[2] * .78])), "from": M(add(hc + [0], P.get("eyeFrom") or [hr[0] * .1, hr[1] * .08, 0])), "r": round(P["eye"] * u, 4),
                 "iris": "@eye", "pupil": "round", **({"lid": P["lid"]} if P.get("lid") else {}), **{k_: P[k_] for k_ in ("sink", "socket") if P.get(k_)}},
        "shape": sh,
    }
    for s_ in sh:   # (coat patterns on the body's shapes by id: pats = { "trunk": { "pat": "mottle", "frame": {...} } })
        if s_.get("id") in (P.get("pats") or {}): s_.update(P["pats"][s_["id"]])
    if P.get("patScale"): d["sculpt"]["patScale"] = P["patScale"]
    if P.get("coat"): d["sculpt"]["coat"] = P["coat"]   # (quills on the shapes that say `coat`: a crowned crane's straw crown)
    for k_ in ("coats", "variants", "params"):
        if P.get(k_): d[k_] = P[k_]
    for c_ in d.get("coats") or []:   # (a coat that recolours the secondaries recolours the tertials over them too, unless it says)
        for a_, b_ in (("sec", "tert"), ("secTip", "tertTip")):
            if a_ in c_ and b_ not in c_ and b_ in c: c_[b_] = c_[a_]
    if P.get("graze"): d["flags"]["graze"] = P["graze"]   # (a bird of `parts`: its flags are its species' words -- creatures.js; standing, the head lowered: index.html's wanderer, skeleton.js an.nod -- a spoonbill's bill in the water)
    if P.get("headAnim"):   # (the head's own idle swing over nb's look-about: a spoonbill's sweep, side to side)
        for p in d["parts"]:
            if p["id"] == "head": p["anim"] = dict(P["headAnim"])
    save(name.replace(" ", "-"), d)   # (a name of two words in a file with a dash: tawny-owl.json, as red-dragon.json)
    return d

def make_parts(P, u, Y, hc, N, nb2, hipY, c):
    m = lambda v: [round(x * u, 4) for x in v]
    n0 = N[0]; hb = hc
    tr = P["trunk"]
    parts = [
        {"id": "body", "parent": None, "shape": "capsule", "size": {"r": round(tr[1] * u, 4), "len": round(tr[0] * 2 * u, 4)}, "geomRot": [0, 0, 90], "pos": m([0, Y, 0]), "color": "@back"},
        {"id": "tail", "parent": "body", "shape": "cone", "size": {"r": round(.05 * u, 4), "h": round(P["tail"]["len"] * u, 4)}, "pos": m([-tr[0], 0, 0]), "rot": [0, 0, 100], "color": "@tail"},
        {"id": "wingL", "parent": "body", "shape": "sphere", "size": {"r": round(.05 * u, 4)}, "pos": [0, 0, 0], "color": "@cov"},
        {"id": "wingR", "parent": "body", "shape": "sphere", "size": {"r": round(.05 * u, 4)}, "pos": [0, 0, 0], "color": "@cov"},
        {"id": "neck", "parent": "body", "shape": "sphere", "size": {"r": round(n0[2] * u, 4)}, "pos": m([n0[0], n0[1], 0]), "color": "@neck",
         "anim": {"axis": "z", "deg": 6, "speed": .35, "phase": 0}},
        {"id": "neck2", "parent": "neck", "shape": "sphere", "size": {"r": round(nb2[2] * u, 4)}, "pos": m([nb2[0] - n0[0], nb2[1] - n0[1], 0]), "color": "@neck",
         "anim": {"axis": "z", "deg": 6, "speed": .35, "phase": 1}},
        {"id": "head", "parent": "neck2", "shape": "sphere", "size": {"r": round(P["hr"][1] * u, 4)}, "pos": m([hb[0] - nb2[0], hb[1] - nb2[1], 0]), "color": "@head",
         "anim": {"axis": "y", "deg": 22, "speed": .6, "phase": 0}},
        {"id": "beak", "parent": "head", "shape": "cone", "size": {"r": round(P["bill"]["r"] * u, 4), "h": round(P["bill"]["len"] * u, 4)}, "pos": m([P["hr"][0], -.01, 0]),
         "rot": [0, 0, -100], "color": "@bill"},
    ]
    for s, z in (("L", 1), ("R", -1)):
        parts.append({"id": "eye" + s, "parent": "head", "shape": "sphere", "size": {"r": round(P["eye"] * u, 4)},
                      "pos": m((lambda e: [e[0], e[1], z * e[2]])(P.get("eyeAt") or [P["hr"][0] * .42, P["hr"][1] * .12, P["hr"][2] * .78])), "color": "#141210", "edge": 0,
                      "dot": {"iris": c.get("eye", "#2a1a10"), "pupil": "round", "round": True, "role": "eye"}})
    for s, z, ph in (("L", 1, 0), ("R", -1, 3.14)):
        parts.append({"id": "leg" + s, "parent": "body", "shape": "capsule", "size": {"r": round(P["legr"] * u, 4), "len": .1}, "pos": m([P["legx"], hipY - Y, z * P["legz"]]),
                      "color": "@leg", "anim": {"axis": "z", "deg": 24, "speed": 1, "phase": ph}})
    return parts

def pal(back, under, head=None, wing=None, tail=None, bill="#2a2622", leg="#6a5444", eye="#1a120c", **kw):
    """the region colours from a few: back, underparts, head, wing, tail (each region's own key can be overridden)"""
    head = head or back; wing = wing or back; tail = tail or wing
    c = {"back": back, "under": under, "rump": back, "vent": under, "neck": head, "head": head, "crown": head, "cheek": head, "throat": under,
         "bill": bill, "billLo": bill, "thigh": under, "leg": leg, "tail": tail, "tailTip": tail, "cov": wing, "covTip": wing, "gcov": wing,
         "gcovTip": wing, "sec": wing, "secTip": wing, "prim": wing, "primTip": wing, "eye": eye, "wpad": wing}
    c.update(kw)
    if "wpad" not in kw:   # (the wing's own shade, a touch under its coverts': its outline reads on a bird all one colour)
        h_ = c["cov"].lstrip("#"); c["wpad"] = "#%02x%02x%02x" % tuple(int(int(h_[i:i + 2], 16) * .9) for i in (0, 2, 4))
    return c
