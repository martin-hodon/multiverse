import sys, copy
from lib import *
import smallrig  # noqa  (saves nothing when imported with argv? -- see main)

def add(a, d): return [a[i] + (d[i] if i < len(d) else 0) for i in range(3)]
def lerp(a, b, t): return [a[i] + (b[i] - a[i]) * t for i in range(3)]

# THE SMALL-MAMMAL TEMPLATE: a pear of a body on short legs (a rodent's, a hare's), laid on the rig's own joints
def small(J, rig, o):
    Rc, Rr = rig["rear"][:3], rig["rear"][3:6]
    Fc, Fr = rig["front"][:3], rig["front"][3:6]
    L = rig["legs"]; rH, rK, rA = L["radii"]; ft = L["foot"]
    hr = rig["head"][3]
    Hd, No = J["head"], J["nose"]
    S = []
    def sh(**k): S.append(k)
    kb = Rr[1] * 0.35
    # ---- the trunk: the haunches the widest of it, a short chest, the belly paler
    sh(id="rump", type="ell", c=add(Rc, [-0.1 * Rr[0], 0.04 * Rr[1]]), r=[Rr[0] * 0.95 * o.get("rumpX", 1), Rr[1] * o.get("rumpY", 1), Rr[2]], k=kb, color="@body", hair=o.get("hair", 0))
    sh(id="chest", type="ell", c=add(Fc, [0, -0.02 * Fr[1]]), r=[Fr[0] * 0.95, Fr[1], Fr[2]], k=kb, color="@front", hair=o.get("hair", 0))
    sh(id="loin", type="ell", c=lerp(Rc, Fc, 0.5), r=[(Fc[0] - Rc[0]) * 0.62, (Rr[1] + Fr[1]) * 0.45 * o.get("loinY", 1), (Rr[2] + Fr[2]) * 0.48], k=kb, color="@body", hair=o.get("hair", 0))
    sh(id="belly", type="ell", c=[(Rc[0] + Fc[0]) / 2, Rc[1] - Rr[1] * 0.5 + o.get("lift", 0), 0], r=[(Fc[0] - Rc[0]) * 0.75, Rr[1] * 0.42 * o.get("bellyY", 1), Rr[2] * 0.72 * o.get("bellyZ", 1)], k=kb * 0.7, kc=kb * 0.3, color="@belly")
    # ---- forelegs: short, a hand of a paw
    F, E, P = J["legFLu"], J["legFLl"], J["footFL"]
    sh(id="arm", type="cone", bone="legFLu", a=add(F, [0.3 * rH, 0.6 * rH]), b=E, ra=rH * 1.15 * o.get("fleg", 1), rb=rK * 1.05 * o.get("fleg", 1), k=rK * 0.8, color="@front", mirror=True)
    sh(id="forearm", type="cone", bone="legFLl", a=E, b=add(P, [0, ft[1] * 1.6]), ra=rK * o.get("fleg", 1), rb=rA * 0.9 * o.get("fleg", 1), k=rA * 0.5, color="@leg", mirror=True)
    sh(id="paw", type="ell", bone="footFL", c=[P[0] + ft[0] * 0.45, ft[1] * 1.05, P[2]], r=[ft[0] * o.get("fpaw", 1), ft[1], ft[2]], k=rA * 0.4, color="@foot", mirror=True)
    # ---- hind legs: the haunch, the shin, the long foot flat on the ground
    Hh, K, Q = J["legHLu"], J["legHLl"], J["footHL"]
    up = Hh[1] - K[1]
    th = o.get("thigh", 1.0)
    sh(id="thigh", type="ell", bone="legHLu", c=add(Hh, [0.05 * up, -0.25 * up]), r=[up * 0.7 * th, up * 0.85 * th, rH * 1.05 * th], rot=[0, 0, 20], k=kb * 0.8, color="@body", mirror=True, hair=o.get("hair", 0))
    sh(id="shin", type="cone", bone="legHLl", a=add(K, [0.01 * up, 0.05 * up]), b=add(Q, [-0.4 * ft[0], ft[1] * 1.4]), ra=rK * 1.1, rb=rA, k=rA * 0.5, color="@leg", mirror=True)
    hl = o.get("hfoot", 2.2) * ft[0]
    if o.get("hock"):
        sh(id="hock", type="ell", bone="footHL", c=[Q[0] - ft[0] * 0.35, ft[1] * 1.9, Q[2]], r=[ft[0] * 0.55, ft[1] * 1.6, ft[2] * 0.8], k=rA * 0.5, color="@leg", mirror=True)
    sh(id="hfoot", type="ell", bone="footHL", c=[Q[0] + hl * 0.55 - ft[0] * 0.5, ft[1] * 1.0, Q[2]], r=[hl, ft[1] * 1.05, ft[2] * o.get("hfootW", 1.0)], k=rA * 0.4, color="@foot", mirror=True)
    # ---- the neck, short and thick
    Nk = J["neck"]
    sh(id="neck", type="ell", bone="neck", c=lerp(Nk, Hd, 0.4), r=[hr * 1.1, hr * 0.95, hr * 0.95 * o.get("neckZ", 1)], k=hr * 0.4, color="@body")
    sh(id="throat", type="ell", bone="neck", c=add(lerp(Nk, Hd, 0.55), [0, -hr * 0.45]), r=[hr * 0.8, hr * 0.55, hr * 0.7], k=hr * 0.3, kc=hr * 0.15, color="@belly")
    # ---- the head: a domed skull, puffed cheeks, the muzzle, whisker pads round a small nose
    mz = rig["muzzle"]; Sn = mz[:3]; Mr = mz[3:6] if len(mz) == 6 else [hr * 0.6] * 3
    sh(id="skull", type="ell", bone="head", c=add(Hd, [-0.05 * hr, 0.08 * hr]), r=[hr * 1.05, hr * 0.88, hr * 0.86], k=hr * 0.3, color="@head")
    sh(id="cheek", type="ell", bone="head", c=add(Hd, [0.22 * hr, -0.3 * hr, 0.48 * hr]), r=[hr * 0.62, hr * 0.55, hr * 0.42], k=hr * 0.25, color="@cheek", mirror=True)
    sh(id="muzzle", type="ell", bone="head", c=add(Sn, [-0.1 * Mr[0], 0.05 * Mr[1]]), r=[Mr[0] * o.get("mzX", 1), Mr[1] * 0.95, Mr[2] * 0.95], k=hr * 0.25, color="@muzzle")
    sh(id="pad", type="ell", bone="head", c=[No[0] - Mr[0] * 0.55, No[1] - Mr[1] * 0.45, Mr[2] * 0.45], r=[Mr[0] * 0.5, Mr[1] * 0.55, Mr[2] * 0.48], k=hr * 0.12, kc=hr * 0.05, color="@pad", mirror=True)
    sh(id="chin", type="ell", bone="head", c=[No[0] - Mr[0] * 1.0, No[1] - Mr[1] * 1.0, 0], r=[Mr[0] * 0.6, Mr[1] * 0.4, Mr[2] * 0.5], k=hr * 0.1, kc=hr * 0.05, color="@chin")
    nr = rig["nose"][3] * o.get("nose", 1)
    sh(id="nose", type="ell", bone="head", c=add(No, [-nr * 0.3, 0]), r=[nr * 0.8, nr * 0.75, nr * 1.1], k=nr * 0.4, kc=nr * 0.2, color="@nose", wet=o.get("wet", 0.45))
    # the incisors: two chisels under the nose (explicit plates)
    # the INCISORS: one adjacent pair of chisels at the midline under the nose (tw: the pair's whole width, metres)
    tw, ih = o.get("tw", 0.004), o.get("teeth", [0.18, 0.5])[1]
    tl = Mr[1] * ih
    tc = [No[0] - nr * 1.5, No[1] - Mr[1] * 0.55 - tl * 0.45, tw * 0.29]
    sh(id="tooth", type="ell", bone="head", c=tc, r=[max(tw * 0.22, 0.0008), tl * 0.5, tw * 0.2], rot=[0, 0, -8], k=0.0004, kc=0.0002, color="@tooth", mirror=True)
    # the eyes SET IN: sunk deep in a socket of the lid's colour, a dark iris round the pupil
    eyes = {"at": J["eyeL"], "from": add(Hd, [0, 0.1 * hr, 0]), "r": rig["eyes"][3] * o.get("eye", 1), "iris": "@eye", "pupil": "round", "lid": "@lid",
            "sink": o.get("sink", 0.55), "socket": o.get("socket", 1.12), "color": o.get("eyeBall", "#0a0706")}
    return S, eyes

def species(name, cols, opts, extra, keep, about, tris, tail=None):
    d = copy.deepcopy(smallrig.RIGS.get(name) or orig(name)); d.pop("sculpt", None); d["c"] = {**d["c"], **cols}
    for k, v in opts.get("rig", {}).items(): d[k] = v
    if tail: d["tail"] = {**d["tail"], **tail}
    save(name, d)
    J = joints(name)
    S, eyes = small(J, d, opts)
    # (per species: template shapes DROPPED for its own, or their fields SET outright)
    S = [q for q in S if q["id"] not in opts.get("drop", ())]
    for q in S:
        if q["id"] in opts.get("set", {}): q.update(opts["set"][q["id"]])
    S += extra(J, d)
    if opts.get("grizzle"):   # GRIZZLED AGOUTI: the leaf mottle over the coat's shapes, a patch a few mm across a shade darker
        for q in S:
            if q["id"] in ("rump", "loin", "chest", "thigh", "neck", "skull", "cheek", "arm") and "pat" not in q:
                q.update(pat=1, frame={"o": [0, 0, 0], "u": [1, 0, 0], "r": opts["grizzle"]})
    if opts.get("agouti"):   # (audit 2026-11-07) TICKED FUR (coatpat.js agouti) over the shapes painted in these keys
        for q in S:
            if q.get("color") in opts["agouti"] and "pat" not in q and q.get("op") != "paint": q["pat"] = "agouti"
    hk = opts.get("headK")
    if hk:   # the HEAD bigger: its shapes about the head joint, the ears ridden out with it, the eyes too
        Hd = J["head"]; big = lambda p: [Hd[i] + (p[i] - Hd[i]) * hk for i in range(3)]
        for q in S:
            if q.get("bone") == "head":
                for kk in ("c", "a", "b"):
                    if kk in q: q[kk] = big(q[kk])
                for kk in ("ra", "rb", "k", "kc"):
                    if kk in q: q[kk] *= hk
                if "r" in q: q["r"] = [x * hk for x in q["r"]] if isinstance(q["r"], list) else q["r"] * hk
            elif q.get("bone") == "earL":   # (half as far: set into the bigger skull's fur, not standing off it)
                for kk in ("c", "a", "b"):
                    if kk in q: q[kk] = [(x + y) / 2 for x, y in zip(q[kk], big(q[kk]))]
        eyes["at"] = big(eyes["at"]); eyes["r"] *= hk
    S += opts.get("post", lambda J, d, eyes: [])(J, d, eyes)
    mirror_ok(S)
    out = {"name": name, "_about": about}
    out.update({k: v for k, v in d.items() if k not in ("name", "_about")})
    out["sculpt"] = {"keep": keep, "mesh": {"tris": list(tris), **({"focus": opts["focus"]} if "focus" in opts else {})}, "shape": S, "eyes": eyes}
    if opts.get("shade"): out["sculpt"]["shade"] = opts["shade"]
    save(name, out)

# ======================================================================================================================
def rat():
    def toes(foot, base, n, L, r0, spread, col="@foot"):   # the TOES: thin pink cones fanned off the paw's front
        P = foot; out = []
        for i in range(n):
            u = (i - (n - 1) / 2) / max(1, (n - 1) / 2)
            a = [P[0] + base[0], base[1], P[2] + u * spread * 0.55]
            b = [a[0] + L * (1 - 0.18 * abs(u)), base[1] - 0.0012, P[2] + u * spread]
            out.append({"id": f"toe{'F' if col == '@hand' else 'H'}{i}", "type": "cone", "bone": "footFL" if col == "@hand" else "footHL", "a": a, "b": b,
                        "ra": r0, "rb": r0 * 0.7, "k": r0 * 0.5, "kc": r0 * 0.2, "color": col, "mirror": True})
        return out
    def whiskers():   # the VIBRISSAE: hair-thin tubes fanned back off each whisker pad
        out = []
        for i, (dy, dz, L) in enumerate(((0.004, 0.026, 0.032), (0.001, 0.03, 0.036), (-0.002, 0.03, 0.034), (-0.005, 0.026, 0.03))):
            A = [0.159, 0.055 + dy * 0.25, 0.0085]
            M = [A[0] - L * 0.25, A[1] + dy * 0.6, A[2] + dz * 0.55]
            B = [A[0] - L * 0.55, A[1] + dy * 1.1 - 0.003, A[2] + dz]
            out.append({"id": f"whisker{i}", "type": "tube", "bone": "head", "pts": [A + [0.00045], M + [0.0003], B + [0.00012]], "k": 0.0002, "kc": 0.0001,
                        "color": "@whisker", "mirror": True})
        return out
    def extra(J, d):
        Er = J["earL"]
        rad = lambda t: 0.0025 + 0.0085 * (1 - t) ** 1.7    # (a thick root tapering to a fine point)
        return [
            # the ears: thin round naked shells, pink
            # (round 8: the disc only grazed the narrow skull -- a gap of 1.5 mm, the ear its own island of the surface. Now a
            #  broader disc let 2.5 mm down into the head, a LOBE at its root sunk half into the skull and blended (its width
            #  ~.6 of the ear's), the pink-grey inside a lining in a shallow carved CUP. N = the disc's normal, (.906,.211,.366))
            {"id": "ear", "type": "ell", "bone": "earL", "c": add(Er, [-0.002, 0.0085, 0.0035]), "r": [0.004, 0.015, 0.0138], "rot": [-30, -25, 0], "k": 0.003, "kc": 0.001, "color": "@ear", "mirror": True},
            {"id": "earBase", "type": "ell", "bone": "earL", "c": add(Er, [0.001, -0.001, -0.004]), "r": [0.0048, 0.0065, 0.0085], "rot": [-30, -25, 0], "k": 0.004, "kc": 0.0015, "color": "@ear", "mirror": True},
            {"id": "earIn", "type": "ell", "bone": "earL", "c": add(Er, [-0.002 + 0.906 * 0.0025, 0.0085 + 0.211 * 0.0025, 0.0035 + 0.366 * 0.0025]), "r": [0.0015, 0.0118, 0.0108], "rot": [-30, -25, 0], "k": 0.001, "kc": 0.0005, "color": "@earIn", "mirror": True},
            {"id": "earCup", "type": "ell", "op": "sub", "bone": "earL", "c": add(Er, [-0.002 + 0.906 * 0.0087, 0.0085 + 0.211 * 0.0087 + 0.001, 0.0035 + 0.366 * 0.0087]), "r": [0.0062, 0.0105, 0.0095], "rot": [-30, -25, 0], "k": 0.0008, "color": "@earIn", "mirror": True},
            # THE SNOUT: a cone tapering from the skull to a narrow point, the nose a pink ball over the end of it, overhanging
            #  the receding chin; the whisker pads two swellings either side behind the nose
            {"id": "snout", "type": "cone", "bone": "head", "a": [0.122, 0.0655, 0], "b": [0.1635, 0.0585, 0], "ra": 0.0165, "rb": 0.0058, "k": 0.004, "kc": 0.0015, "color": "@muzzle"},
            {"id": "bridge", "type": "ell", "bone": "head", "c": [0.137, 0.0675, 0], "r": [0.02, 0.0085, 0.0105], "rot": [0, 0, -9], "k": 0.003, "kc": 0.001, "color": "@head"},
            {"id": "whiskerPad", "type": "ell", "bone": "head", "c": [0.1565, 0.0548, 0.0056], "r": [0.0085, 0.0062, 0.0056], "k": 0.0018, "kc": 0.0008, "color": "@pad", "mirror": True},
            {"id": "noseTip", "type": "ell", "bone": "head", "c": [0.1688, 0.0586, 0], "r": [0.0034, 0.0029, 0.0036], "k": 0.0012, "kc": 0.0005, "color": "@nose", "wet": 0.25},
            {"id": "lip", "type": "ell", "bone": "head", "c": [0.1585, 0.0505, 0], "r": [0.0055, 0.0032, 0.0062], "k": 0.001, "kc": 0.0005, "color": "@pad"},
            {"id": "jaw", "type": "ell", "bone": "head", "c": [0.141, 0.049, 0], "r": [0.0145, 0.0058, 0.0088], "rot": [0, 0, 6], "k": 0.0025, "kc": 0.001, "color": "@chin"},
            # the naked tail's root, thick where it leaves the rump
            {"id": "tailRoot", "type": "cone", "a": add(J["tail"], [0.022, 0.006]), "b": add(J["tail"], [-0.014, -0.003]), "ra": 0.0135, "rb": 0.0098, "k": 0.005, "color": "@body"},
        ] + toes(J["footFL"], [0.0105, 0.0032], 4, 0.0055, 0.0013, 0.0058, "@hand") + toes(J["footHL"], [0.03, 0.0032], 5, 0.0085, 0.0016, 0.0085) + whiskers() \
          + arc_tail(d["tail"], lambda t, P0, P1, r: {"color": "@tail" if int(t * 24) % 2 else "@ring"}, n=24, k=0.3, kc=0.05, rad=rad)
    species("rat", {"body": "#685748", "front": "#6e5c4c", "head": "#6a5949", "cheek": "#72604e", "belly": "#a99a88", "muzzle": "#6e5d4d", "pad": "#8e7e70", "chin": "#a89a8a",
                    "nose": "#e09aa2", "tooth": "#e6c27a", "ear": "#b8958c", "earIn": "#cdaba7", "leg": "#7a6656", "foot": "#e0aea4", "hand": "#e0aea4", "tail": "#c4a094", "ring": "#b48c82",
                    "lid": "#2a1e18", "eye": "#2a1610", "whisker": "#d8d0c6"},
            {"hfoot": 2.2, "hfootW": 0.75, "fpaw": 0.75, "thigh": 1.0, "eye": 0.7, "fleg": 0.9,
             "drop": ("muzzle", "pad", "chin", "nose"),
             # (the trunk set outright: long and low, the back arched highest over the hips, the belly clear of the ground)
             "set": {"rump": {"c": [-0.062, 0.067, 0], "r": [0.068, 0.035, 0.033]},
                     "loin": {"c": [-0.012, 0.064, 0], "r": [0.06, 0.03, 0.03]},
                     "chest": {"c": [0.034, 0.058, 0], "r": [0.042, 0.026, 0.026]},
                     "belly": {"c": [-0.012, 0.046, 0], "r": [0.068, 0.0135, 0.022]},
                     "skull": {"c": [0.112, 0.069, 0], "r": [0.026, 0.0195, 0.0185]},
                     "cheek": {"c": [0.121, 0.0605, 0.0105], "r": [0.0155, 0.0115, 0.0088]},
                     "neck": {"r": [0.0275, 0.0225, 0.0215]},
                     "tooth": {"c": [0.161, 0.0478, 0.00095], "r": [0.0009, 0.0034, 0.0009], "rot": [0, 0, -10]}},
             "focus": {"head": 6, "footFL": 2, "footHL": 2},
             "shade": {"back": 0.9, "belly": 1.12, "on": "@body"}},
            extra, [],
            "a brown rat SCULPTED on its rig (2026-11-05, gen: scratchpad sc/carn/gen/small.py): 22 cm head-body and a 20 cm naked scaly tail, pinkish, thick at the root; long and low, the back arched highest over the hips; a tapered pointed snout, the pink nose overhanging, whisker pads and whiskers, yellow incisors, round naked pink ears, fine pink hands and long pink hind feet with toes; grey-brown over a paler belly",
            (5200, 1200))

def brush(T, m=16):
    # THE PLUME: many overlapping flattened ellipses down the arc, laid end to end so the outline runs smooth (no lumps):
    # narrow at the root, broader than the body past the middle, held a little thinner across than in profile; matte
    import math
    cx, cy = T["c"]; R = T["R"]; a0, a1 = T["a0"], T["a1"]; nS = max(1, math.ceil(abs(a1 - a0) / 1.2)); out = []
    step = R * abs(a1 - a0) / m
    for i in range(m):
        t = (i + 0.5) / m; a = a0 + (a1 - a0) * t; seg = min(nS - 1, int(t * nS))
        c = [cx + R * math.cos(a), cy + R * math.sin(a), 0]; ang = math.degrees(a) + 90 * (1 if a1 > a0 else -1)
        g = min(1.0, t * 2.4) ** 0.8
        w = 0.02 + 0.04 * g - 0.012 * max(0.0, t - 0.72) / 0.28     # (its half-breadth in profile)
        out.append({"id": f"brush{i}", "type": "ell", "bone": "tail" if seg == 0 else f"tail{seg}", "c": c, "r": [step * 2.0, w, 0.016 + 0.026 * g], "rot": [0, 0, ang],
                    "k": 0.018, "kc": 0.01, "color": "@tail" if i < m - 3 else "@tailT"})
    return out

def squirrel():
    def post(J, d, eyes):
        # the pale EYE RING: a disc seated round the eye, the eye set in its middle
        e = eyes["at"]
        return [{"id": "eyeRing", "type": "ell", "bone": "head", "c": e, "r": [eyes["r"] * 1.45, eyes["r"] * 1.35, eyes["r"] * 0.6], "rot": [0, -38, 0], "k": 0.001, "kc": 0.0004,
                 "color": "@ring", "mirror": True, "seat": {"from": add(J["head"], [0, 0.002, 0]), "out": -0.5}}]
    def extra(J, d):
        Er = J["earL"]
        return [
            {"id": "ear", "type": "cone", "bone": "earL", "a": add(Er, [0, -0.002, 0]), "b": add(Er, [-0.006, 0.03, 0.006]), "ra": 0.0105, "rb": 0.003, "k": 0.003, "kc": 0.001, "color": "@ear", "mirror": True},
            {"id": "earTuft", "type": "cone", "bone": "earL", "a": add(Er, [-0.005, 0.026, 0.005]), "b": add(Er, [-0.013, 0.062, 0.01]), "ra": 0.0055, "rb": 0.0012, "k": 0.002, "kc": 0.001, "color": "@tuftE", "mirror": True, "hair": 1},
            {"id": "earIn", "type": "ell", "bone": "earL", "c": add(Er, [0.0035, 0.012, 0.002]), "r": [0.0015, 0.009, 0.0055], "k": 0.001, "kc": 0.0005, "color": "@earIn", "mirror": True},
            # THE BRUSH: seven overlapping flattened ellipses up the back from the rump and over in a curl (matte: no sheen)
            *brush(d["tail"]),
        ]
    species("squirrel", {"body": "#a2522a", "front": "#a85a30", "head": "#a2552c", "cheek": "#b0643a", "belly": "#f0e6d6", "muzzle": "#a85c34", "pad": "#b67048", "chin": "#efe4d2",
                         "nose": "#4a2c22", "tooth": "#e0b870", "ear": "#9a4a24", "earIn": "#c8845a", "tuftE": "#5e2810", "leg": "#9a4c26", "foot": "#8a4222", "tail": "#a8582c", "tailT": "#9a4c26",
                         "lid": "#2a1a12", "eye": "#5a3220", "ring": "#cf9a6c"},
            {"hfoot": 2.4, "thigh": 1.1, "hair": 0, "eye": 0.54, "sink": 0.66, "socket": 1.05, "nose": 0.8, "wet": 0.1, "post": post, "focus": {"head": 6, "earL": 3}},
            extra, [],
            "a red squirrel SCULPTED on its rig (2026-11-05, gen: scratchpad sc/carn/gen/small.py): 20 cm head-body, the great brush of a tail curled up over its back, tufted ears, big dark eyes in a pale ring, a white belly and chin; long hind feet, small clever hands",
            (5600, 1800), tail={"c": [-0.2, 0.16], "R": 0.085, "a0": -0.85, "a1": 2.2, "tuft": 0})

def beaver():
    def post(J, d, eyes):   # (after the head is scaled up: these are written where they land on the bigger head)
        return [
            # THE INCISORS: two broad flat orange chisels side by side below the lip, a slot between (each a broad plate of two triangles, drawn as it is)
            *[{"id": f"incisor{j}", "type": "tri", "bone": "head", "a": A, "b": B, "c": C, "r": 0.0022, "color": "@tooth", "mirror": True}
              for j, (A, B, C) in enumerate((([0.4878, 0.147, 0.0036], [0.4878, 0.147, 0.0108], [0.4898, 0.1205, 0.0108]),
                                             ([0.4878, 0.147, 0.0036], [0.4898, 0.1205, 0.0108], [0.4898, 0.1205, 0.0036])))],
        ]
    def extra(J, d):
        Er, T = J["earL"], J["tail"]
        return [
            {"id": "ear", "type": "ell", "bone": "earL", "c": add(Er, [-0.005, 0.006, 0.004]), "r": [0.011, 0.016, 0.015], "k": 0.007, "kc": 0.002, "color": "@ear", "mirror": True},
            # THE PADDLE: flat, broad, scaled, black-grey; on a short furred root
            {"id": "tailRoot", "type": "cone", "bone": "tail", "a": add(T, [0.05, 0.02]), "b": add(T, [-0.06, -0.025]), "ra": 0.06, "rb": 0.04, "k": 0.03, "color": "@body"},
            {"id": "paddle", "type": "ell", "bone": "tail", "c": add(T, [-0.19, -0.065]), "r": [0.15, 0.016, 0.068], "rot": [0, 0, 14], "k": 0.025, "kc": 0.01, "color": "@tail",
             "pat": 17, "frame": {"o": add(T, [-0.19, -0.065]), "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.06}},
            # the webbed hind feet: the web a broad plate between the toes
            {"id": "web", "type": "ell", "bone": "footHL", "c": add(J["footHL"], [0.06, -0.001]), "r": [0.04, 0.006, 0.04], "k": 0.008, "color": "@foot", "mirror": True},
        ] + [{"id": f"toe{i}", "type": "cone", "bone": "footHL", "a": add(J["footHL"], [0.045, 0.006, dz * 0.5]), "b": add(J["footHL"], [0.1, 0.004, dz]), "ra": 0.008, "rb": 0.005,
              "k": 0.004, "color": "@foot", "mirror": True} for i, dz in enumerate((-0.03, -0.012, 0.006, 0.024, 0.04))] \
          + [{"id": f"finger{i}", "type": "cone", "bone": "footFL", "a": [J["footFL"][0] + 0.022, 0.017, J["footFL"][2] + dz * 0.45], "b": [J["footFL"][0] + 0.06, 0.007, J["footFL"][2] + dz],
              "ra": 0.0075, "rb": 0.0045, "k": 0.003, "kc": 0.002, "color": "@foot", "mirror": True} for i, dz in enumerate((-0.026, -0.011, 0.004, 0.019, 0.032))]   # (audit 2026-11-07: the hand's five clawed FINGERS -- it was a pancake)
    species("beaver", {"body": "#4e3524", "front": "#523827", "head": "#4a3222", "cheek": "#563b29", "belly": "#5e4532", "muzzle": "#5e4434", "pad": "#8a6c54", "chin": "#8e7058",
                       "nose": "#2c221e", "tooth": "#e2762a", "ear": "#3a2618", "leg": "#3e2a1c", "foot": "#2a1e18", "tail": "#2e2a28", "lid": "#1a120c", "eye": "#2a1810"},
            {"hfoot": 1.9, "hfootW": 1.05, "thigh": 1.1, "fpaw": 0.62, "mzX": 0.95, "nose": 1.1, "teeth": [0.26, 0.85], "tw": 0.02, "nose": 0.7, "wet": 0.0, "eye": 0.68, "drop": ("tooth",), "focus": {"head": 6}, "post": post, "rumpY": 1.04, "headK": 1.15, "shade": {"back": 0.85, "belly": 1.18, "on": "@body"}},
            extra, [],
            "a beaver SCULPTED on its rig (2026-11-05, gen: scratchpad sc/carn/gen/small.py): 80 cm head-body, hunched, its back highest over the haunches; short legs, small hands, big webbed hind feet; a broad blunt head with small ears and eyes and the orange incisors; the flat scaled paddle of a tail; dark brown",
            (5600, 1450))

def hare():
    def post(J, d, eyes):   # the pale eye ring
        return [{"id": "eyeRing", "type": "sphere", "bone": "head", "c": eyes["at"], "r": eyes["r"] * 1.45, "k": 0.002, "kc": 0.0008, "color": "@ring", "mirror": True,
                 "seat": {"from": add(J["head"], [0, 0.002, 0]), "out": -0.62}}]
    def extra(J, d):
        Er, T, T1, Q = J["earL"], J["tail"], J["tail1"], J["footHL"]
        tipE = add(Er, [-0.045, 0.115, 0.018])
        return [
            # THE EARS: long, black-tipped, their hollows pale
            {"id": "ear", "type": "ell", "bone": "earL", "c": lerp(Er, tipE, 0.5), "r": [0.019, 0.064, 0.007], "rot": [12, 0, 21], "k": 0.006, "kc": 0.002, "color": "@ear", "mirror": True},
            {"id": "earTip", "type": "ell", "bone": "earL", "c": lerp(Er, tipE, 0.9), "r": [0.012, 0.018, 0.0072], "rot": [12, 0, 21], "k": 0.004, "kc": 0.002, "color": "@earTip", "mirror": True},
            {"id": "earIn", "type": "ell", "bone": "earL", "c": add(lerp(Er, tipE, 0.48), [0.004, 0, 0.003]), "r": [0.011, 0.05, 0.004], "rot": [12, 0, 21], "k": 0.002, "kc": 0.001, "color": "@earIn", "mirror": True},
            # the tail: a white puff, black on top
            {"id": "scut", "type": "ell", "bone": "tail", "c": add(T, [0.002, 0.012]), "r": [0.026, 0.026, 0.024], "k": 0.008, "color": "@tail", "hair": 1},
            {"id": "scutTop", "type": "ell", "bone": "tail", "c": add(T, [-0.002, 0.03]), "r": [0.022, 0.012, 0.02], "k": 0.004, "kc": 0.0015, "color": "@tailTop", "hair": 1},
            # THE LONG HIND FOOT: from the heel set back behind the shin, tapering forward to the long toes flat on the ground
            {"id": "heel", "type": "cone", "bone": "footHL", "a": add(Q, [-0.03, 0.026]), "b": add(Q, [0.055, 0.009]), "ra": 0.016, "rb": 0.0105, "k": 0.006, "kc": 0.002, "color": "@leg", "mirror": True},
            {"id": "toesH", "type": "ell", "bone": "footHL", "c": add(Q, [0.06, 0.0085]), "r": [0.028, 0.0085, 0.0135], "k": 0.004, "kc": 0.0015, "color": "@foot", "mirror": True},
        ]
    species("hare", {"body": "#9c7f60", "front": "#a27c58", "head": "#9a8064", "cheek": "#a99070", "belly": "#e8e0d2", "muzzle": "#a68e72", "pad": "#c4b098", "chin": "#e4dccd",
                     "nose": "#6a4a3a", "tooth": "#efe6d2", "ear": "#937a5c", "earIn": "#c9b49a", "earTip": "#1e1a16", "leg": "#a08668", "foot": "#b8a488", "tail": "#f0eae0", "tailTop": "#1e1a16",
                     "lid": "#4a3826", "eye": "#c08a30", "ring": "#d9ccb4"},
            {"thigh": 1.08, "teeth": [0.16, 0.35], "tw": 0.006, "fleg": 0.78, "fpaw": 0.8, "eye": 0.92, "sink": 0.66, "post": post,
             "agouti": ("@body", "@front", "@head", "@cheek", "@leg", "@muzzle"), "shade": {"back": 0.9, "belly": 1.08, "on": "@body"},
             # (audit 2026-11-07) VARIANTS: the MOUNTAIN HARE, a little smaller -- `mountain` in its white winter coat (only the
             # ear tips black), `mountain summer` grey-brown with a white tail all round
             "rig": {"variants": {
                 "mountain": {"scale": 0.9, "colors": {"body": "#efebe4", "front": "#ece8e0", "head": "#eeeae2", "cheek": "#f0ece5", "belly": "#f4f2ec",
                                                      "muzzle": "#ece8e0", "pad": "#e8e2d8", "chin": "#f4f2ec", "ear": "#e8e4dc", "earIn": "#e2dcd2",
                                                      "leg": "#ece8e0", "foot": "#f0ece4", "tail": "#f4f2ec", "tailTop": "#f0ece4", "ring": "#f4f2ec",
                                                      "nose": "#7a6058"}},
                 "mountain summer": {"scale": 0.9, "colors": {"body": "#7e7262", "front": "#837562", "head": "#7c7060", "cheek": "#86796a", "belly": "#e2dcd0",
                                                             "muzzle": "#8a7e6e", "ear": "#786c5c", "leg": "#867a6a", "foot": "#a49a8a",
                                                             "tail": "#ece8e0", "tailTop": "#e2ded4"}}}},
             "drop": ("hfoot",),
             # (the trunk set outright: a lean runner's, the haunches high and round, the waist tucked up, the chest deep and narrow)
             "set": {"rump": {"c": [-0.135, 0.215, 0], "r": [0.112, 0.086, 0.07]},
                     "loin": {"c": [-0.02, 0.217, 0], "r": [0.1, 0.06, 0.056]},
                     "chest": {"c": [0.088, 0.197, 0], "r": [0.082, 0.074, 0.06]},
                     "belly": {"c": [-0.01, 0.16, 0], "r": [0.095, 0.024, 0.028]},
                     "skull": {"r": [0.0525, 0.044, 0.04]}},
             "focus": {"head": 5, "earL": 3, "footHL": 2}},
            extra, [],
            "a brown hare SCULPTED on its rig (2026-11-05, gen: scratchpad sc/carn/gen/small.py): 55 cm head-body, the back arched to the high haunches over long hind legs and longer hind feet; a blunt face, big amber eyes set high on the sides, long black-tipped ears; tawny grizzled, the belly and chin white, the tail black above, white below; it bounds (its gait the fore pair and the hind pair each together)",
            (5600, 1800))

for f in sys.argv[1:] or ["rat", "squirrel", "beaver", "hare"]: globals()[f]()
