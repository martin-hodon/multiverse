import sys, json; sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import *
# The hydra: a heavy reptile 5.5 m from its middle head's nose to its tail, its three necks rising from one broad base
# on the chest. The rig is as it was (the necks are arcs of tubes on the extras, mammals.js arcChain); the overlay
# draws it: a deep scaled trunk with a keeled pale belly, a row of spines down the back onto the tail, columnar legs
# set a little out from the body on clawed feet, and three dragon heads (a long snout, brow ridges, swept-back horns,
# the mouth line with its teeth, slit-pupilled yellow eyes -- written as shapes: the overlay's `eyes` makes ONE pair)
d0 = json.load(open(R + "monsters/hydra.json"))
for x in d0["extras"]:
    if x.get("id") in ("neckB", "neckC") and "arc" in x: x["arc"]["zEnd"] = 1.5 if x["id"] == "neckB" else -1.5
def sub(a, b): return [a[i] - b[i] for i in range(3)]
def nrm(v): l = math.sqrt(sum(x * x for x in v)); return [x / l for x in v]
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
sh = []
def S(id, **k):
    d = {"id": id}; d.update(k); sh.append(d); return d
scl = {"pat": "scales", "frame": "body"}
sclN = {"pat": "scales", "frame": {"u": [1, 0, 0], "v": [0, 1, 0], "r": .3}}   # (the necks' scales finer than the trunk's)
# ---- the trunk: barrel, chest, hips; the pale keeled belly; the shoulders and haunches over the legs
S("trunk", type="ell", c=[-.05, 1.45, 0], r=[1.3, .62, .6], k=.12, color="@body", **scl)
S("chest", type="ell", c=[.62, 1.42, 0], r=[.62, .62, .6], k=.12, color="@body", **scl)
S("hips", type="ell", c=[-.85, 1.48, 0], r=[.6, .56, .56], k=.12, color="@body", **scl)
S("belly", type="ell", c=[0, 1.1, 0], r=[1.15, .3, .46], k=.1, kc=.06, color="@belly")
S("breast", type="ell", c=[.95, 1.35, 0], r=[.35, .48, .5], k=.1, kc=.06, color="@belly")
S("shoulder", type="ell", bone="legFLu", c=[.7, 1.22, .45], r=[.32, .4, .2], k=.1, color="@body", mirror=True, **scl)
S("haunch", type="ell", bone="legHLu", c=[-.82, 1.25, .36], r=[.4, .45, .24], k=.1, color="@body", mirror=True, **scl)
# the necks' common base, swelling up off the chest
S("neckBase", type="ell", c=[1.12, 1.78, 0], r=[.42, .5, .72], k=.14, color="@body", **scl)
# ---- legs: thick upper legs, columnar forearm and shank, the elbows a little out; broad feet with four claws
for leg, (hip, kn, ank, ft) in {"F": ([.7, 1.0, .47], [.6, .55, .52], [.72, .14, .48], [.86, .07, .48]),
                                 "H": ([-.8, 1.02, .38], [-.62, .5, .44], [-.82, .14, .4], [-.66, .07, .4])}.items():
    u, l, fb = f"leg{leg}Lu", f"leg{leg}Ll", f"foot{leg}L"
    S(f"upper{leg}", type="tube", bone=u, pts=[hip + [.27], lerp(hip, kn, .5) + [.24], kn + [.2]], k=.08, color="@leg", mirror=True, **scl)
    S(f"lower{leg}", type="tube", bone=l, pts=[kn + [.2], lerp(kn, ank, .5) + [.16], ank + [.12]], k=.06, color="@leg", mirror=True, **scl)
    S(f"wrist{leg}", type="ell", bone=l, c=add(ank, [0, .02, 0]), r=[.14, .09, .13], k=.05, color="@leg", mirror=True, **scl)
    S(f"foot{leg}", type="ell", bone=fb, c=ft, r=[.22, .08, .19], k=.06, color="@leg", mirror=True)
    for i in range(4):
        a = math.radians(-42 + i * 28)
        o = [ft[0] + .14 * math.cos(a), .06, ft[2] + .15 * math.sin(a)]; dd = nrm([math.cos(a), -.45, math.sin(a) * .8])
        S(f"claw{leg}{i}", type="cone", bone=fb, a=o, b=add(o, dd, .17), ra=.052, rb=.01, k=.01, kc=.004, color="@claw", mirror=True)
# ---- the back's spines, from the necks' base down onto the tail
def spine(id, base, up, h, r, bone):
    S(id, type="cone", bone=bone, a=add(base, up, -.02), b=add(add(base, up, h), [-1, 0, 0], h * .45), ra=r, rb=r * .15, k=.02, kc=.008, color="@spine")
for i, x in enumerate([.75, .45, .15, -.15, -.45, -.75, -1.05, -1.3]):
    y = 1.45 + .62 * math.sqrt(max(0, 1 - ((x + .05) / 1.32) ** 2)) - .03
    if x > .4: y = max(y, 1.42 + .6 * math.sqrt(max(0, 1 - ((x - .62) / .64) ** 2)) - .03)
    spine(f"spine{i}", [x, y - .02, 0], [0, 1, 0], .3 + .08 * math.sin(math.pi * (i + 1) / 9), .085, "body")
# ---- the tail: on its arc (mammals.js: c, R from a0 to a1), tapering to a point, its spines shrinking
T = d0["tail"]
def tpt(t, rr=None):
    a = T["a0"] + (T["a1"] - T["a0"]) * t; Rr = T["R"] if rr is None else rr
    return [T["c"][0] + Rr * math.cos(a), T["c"][1] + Rr * math.sin(a), 0]
TR = lambda t: .36 * (1 - t) + .045 * t
S("tail", type="tube", bone="tail", pts=[[-1.2, 1.5, 0, .45]] + [tpt(t) + [TR(t)] for t in (0, .25, .5, .75, .92)] + [tpt(1.0) + [.03]], k=.08, color="@body", **scl)
S("tailV", type="tube", bone="tail", pts=[tpt(t, T["R"] - TR(t) * .45) + [TR(t) * .6] for t in (0, .3, .6, .85)], k=.05, kc=.04, color="@belly")
for i, t in enumerate([.08, .22, .36, .5, .64, .78]):
    p = tpt(t, T["R"] + TR(t) * .9); up = nrm(sub(p, T["c"] + [0]))
    spine(f"tspine{i}", p, up, .26 * (1 - t * .7), .075 * (1 - t * .6), "tail")
# ---- the necks: tubes along their arcs (mammals.js arcChain: from a0 to a1 on the circle c, R, drifting z -> zEnd),
# two bones each (the arc's two tubes), thick at the base; a pale throat down the inside of the curve; small spines
# down the outside; and at the end a head, in a frame of its own (forward along the neck's last direction, levelled)
necks = {x["id"]: x for x in d0["extras"] if "arc" in x}
def heads(nid, flip):
    A = necks[nid]["arc"]; zs = -1 if flip else 1
    def npt(t, rr=None):
        a = A["a0"] + (A["a1"] - A["a0"]) * t; Rr = A["R"] if rr is None else rr
        return [A["c"][0] + Rr * math.cos(a), A["c"][1] + Rr * math.sin(a), A["z"] + (A["zEnd"] - A["z"]) * t]
    NR = lambda t: .34 * (1 - t) ** 1.4 + .15 * (1 - (1 - t) ** 1.4)
    b0, b1 = nid, nid + "1"
    S(f"{nid}N0", type="tube", bone=b0, pts=[npt(t) + [NR(t)] for t in (0, .17, .34, .52)], k=.06, color="@body", **sclN)
    S(f"{nid}N1", type="tube", bone=b1, pts=[npt(t) + [NR(t)] for t in (.46, .64, .82, 1.0)], k=.06, color="@body", **sclN)
    S(f"{nid}T0", type="tube", bone=b0, pts=[npt(t, A["R"] - NR(t) * .62) + [NR(t) * .5] for t in (.05, .28, .52)], k=.03, kc=.012, color="@belly")
    S(f"{nid}T1", type="tube", bone=b1, pts=[npt(t, A["R"] - NR(t) * .62) + [NR(t) * .5] for t in (.48, .72, .95)], k=.03, kc=.012, color="@belly")
    for i, t in enumerate([.2, .4, .6, .8]):
        p = npt(t, A["R"] + NR(t) * .85); c0 = A["c"] + [p[2]]; up = nrm(sub(p, c0))
        spine(f"{nid}sp{i}", p, up, .17, .055, b0 if t < .5 else b1)
    # the head: H at the neck's end; forward along the last direction, a little down; up levelled to the sky
    H = npt(1.0); f = nrm(sub(npt(1.0), npt(.9))); f = nrm([f[0], f[1] * .3 - .12, f[2] * .6])
    up = nrm(sub([0, 1, 0], [x * f[1] for x in f])); lat = cross(f, up)
    hb = nid + "Tuft"; g = 1.24 if nid == "neckA" else 1.14   # (the heads a third bigger than they were: 0.6 m)
    HL = {"neckA": 1.3, "neckB": 1.0, "neckC": .78}[nid]   # (each its own horns: the middle one's longest)
    P = lambda df, du, dl: [H[i] + g * (f[i] * df + up[i] * du + lat[i] * dl) for i in range(3)]
    # (an ell's rot: the head's yaw and pitch; z is left in the rest frame so yaw = atan2(-fz, fx))
    yaw = math.degrees(math.atan2(-f[2], f[0])); pitch = math.degrees(math.asin(f[1]))
    rot = [0, yaw, pitch]
    S(f"{nid}Cran", type="ell", bone=hb, c=P(.08, .05, 0), r=[.22 * g, .16 * g, .17 * g], rot=rot, k=.06, color="@body")
    S(f"{nid}Snout", type="ell", bone=hb, c=P(.4, .0, 0), r=[.26 * g, .09 * g, .11 * g], rot=rot, k=.06, color="@head")
    S(f"{nid}Jaw", type="ell", bone=hb, c=P(.3, -.09, 0), r=[.3 * g, .055 * g, .1 * g], rot=rot, k=.05, kc=.03, color="@belly")
    S(f"{nid}Nose", type="ell", bone=hb, c=P(.6, .015, 0), r=[.08 * g, .07 * g, .085 * g], rot=rot, k=.04, color="@head")
    if nid == "neckA":   # (the middle head's crest: a row of blades down the skull's midline)
        for j, (df, hh) in enumerate([(.12, .1), (-.02, .13), (-.16, .1)]):
            S(f"crest{j}", type="cone", bone=hb, a=P(df, .17, 0), b=P(df - .09, .17 + hh, 0), ra=.045 * g, rb=.006, k=.025, kc=.008, color="@spine")
    for s_ in (1, -1):
        L_ = "L" if s_ > 0 else "R"
        S(f"{nid}Brow{L_}", type="ell", bone=hb, c=P(.16, .14, .09 * s_), r=[.12 * g, .04 * g, .055 * g], rot=rot, k=.03, color="@body")
        S(f"{nid}Horn{L_}", type="cone", bone=hb, a=P(.0, .13, .09 * s_), b=P(-.36 * HL, .13 + .17 * HL, (.09 + .11 * HL) * s_), ra=.05 * g, rb=.008, k=.02, kc=.006, color="@horn")
        S(f"{nid}Horn2{L_}", type="cone", bone=hb, a=P(-.04, .02, .15 * s_), b=P(-.04 - .26 * HL, .02 + .03 * HL, (.15 + .15 * HL) * s_), ra=.035 * g, rb=.006, k=.015, kc=.006, color="@horn")
        S(f"{nid}Nostril{L_}", type="ell", bone=hb, c=P(.65, .05, .04 * s_), r=[.034 * g, .024 * g, .03 * g], rot=rot, k=.012, kc=.004, color="@mouth")
        S(f"{nid}Mouth{L_}", type="tube", bone=hb, pts=[P(.63, -.06, .055 * s_) + [.012 * g], P(.45, -.06, .1 * s_) + [.012 * g], P(.22, -.045, .13 * s_) + [.013 * g], P(.08, -.02, .13 * s_) + [.011 * g]],
          k=.008, kc=.006, color="@mouth")
        for j, df in enumerate((.55, .42, .29)):
            w = .08 + .05 * (.55 - df) / .26
            S(f"{nid}Tooth{L_}{j}", type="cone", bone=hb, a=P(df, -.04, w * s_), b=P(df - .012, -.125, w * s_), ra=.027 * g, rb=.004, k=.004, kc=.002, color="@tooth")
        E = P(.2, .085, .1 * s_)
        S(f"{nid}Eye{L_}", type="sphere", bone=hb, c=E, r=.05 * g, k=.008, kc=.004, color="@eye", wet=.9)
        dE = nrm([lat[i] * s_ * .78 + f[i] * .55 + up[i] * .08 for i in range(3)])   # (where the eye looks: out and forward)
        Po = [E[i] + dE[i] * .05 * g * .72 for i in range(3)]
        S(f"{nid}Pupil{L_}", type="tube", bone=hb, pts=[add(Po, up, -.028 * g) + [.02 * g], add(Po, up, .028 * g) + [.02 * g]], k=.003, kc=.002, color="@pupil")
heads("neckA", False); heads("neckB", False); heads("neckC", True)
# dark bands across the back and onto the tail (soft-edged)
for i, x in enumerate([.5, .1, -.3, -.7, -1.1]):
    S(f"dband{i}", type="ell", c=[x, 1.92, 0], r=[.13, .3, .5], rot=[0, 0, -8], k=.02, kc=.08, color="@band")

d = {k: v for k, v in d0.items() if k not in ("sculpt", "_about")}
# (the necks' own pills are not drawn: their snouts and dot eyes stay as bones, the overlay draws the heads)
d["c"] = {**d0["c"], "body": "#486656", "front": "#527262", "tail": "#486656", "leg": "#3e584c", "head": "#527262", "band": "#2a3e34", "belly": "#b8b884", "spine": "#33503f", "claw": "#2a2a22", "horn": "#8e7c58",
          "mouth": "#2a1814", "tooth": "#ece4c8", "eye": "#d8d43a", "pupil": "#0a0a06"}   # (a mammal's colours: `c`, and the overlay's refs read them)
out = {"name": d0["name"],
       "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a heavy reptile 5.5 m from its middle head's nose to its tail -- a deep scaled trunk with a pale banded belly, a row of spines down the back onto the tail, columnar legs set a little out on broad four-clawed feet; three necks rising from one broad base on the chest (the rig's arcs, as they were), pale-throated and spined, each to a dragon head -- a long snout, brow ridges, swept-back horns, the mouth line with its teeth, slit-pupilled yellow eyes (shapes: the overlay's `eyes` makes one pair, the hydra has three)"}
out.update(d)
out["sculpt"] = {"keep": [], "shade": {"back": .74, "belly": 1.12, "k": .35, "on": "@body"}, "mesh": {"cell": .036, "tris": [8000, 2600]}, "shape": sh}
dump("monsters/hydra.json", out)
print(len(sh), "shapes")
