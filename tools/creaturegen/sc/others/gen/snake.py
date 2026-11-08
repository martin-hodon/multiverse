import sys; sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import *
def nrm(v):
    l = math.sqrt(sum(x * x for x in v)) or 1
    return [x / l for x in v]
Y = .022
def r_at(x):
    if x >= .68: return .0135
    if x >= .45: return .0135 + (.0215 - .0135) * (.68 - x) / .23
    if x >= -.22: return .0215
    return max(.0025, .0215 - (.0215 - .0025) * (-.22 - x) / .58)
# the spine: the body bone the front of the trunk (riders, the girth), then a chain of segments back to the tail's tip,
# resting in an S, each swinging on the gait a beat behind the one before (a wave running back down it)
L = [.2, .2, .2, .2, .18, .15, .13]
ROT = [30.7, -17.3, -45.1, 21.0, 42.6, -12.4, -36.3]   # (headings [31, 13, -32, -11, 32, 19, -17]: a sine along the chain, ~11 cm either side)
parts = [
    {"id": "body", "parent": None, "shape": "tube", "size": {"a": [0, 0, 0], "c": [.125, 0, 0], "b": [.25, 0, 0], "r1": .02, "r2": .014}, "pos": [.45, Y, 0], "color": "@body"},
    {"id": "head", "parent": "body", "shape": "sphere", "size": {"r": .016}, "scale": [1.6, .7, 1.1], "pos": [.25, 0, 0], "color": "@body",
     "anim": {"axis": "y", "deg": 12, "speed": .8, "phase": 0}},
    {"id": "tongue", "parent": "head", "shape": "cone", "size": {"r": .0018, "h": .018}, "pos": [.066, -.004, 0], "rot": [0, 0, -90], "color": "@tongue",
     "anim": {"axis": "y", "deg": 15, "speed": 2.5, "phase": 0}},
]
for i, (l, ro) in enumerate(zip(L, ROT)):
    parts.append({"id": f"seg{i + 1}", "parent": "body" if i == 0 else f"seg{i}", "shape": "tube",
                  "size": {"a": [0, 0, 0], "c": [-l / 2, 0, 0], "b": [-l, 0, 0], "r1": .02, "r2": .018},
                  "pos": [0, 0, 0] if i == 0 else [-L[i - 1], 0, 0], "rot": [0, ro, 0], "color": "@body",
                  "anim": {"axis": "y", "deg": 13, "speed": .8, "phase": round(1.4 + .9 * i, 3)}})
sh = []
def S(id, **k):
    d = {"id": id}; d.update(k); sh.append(d); return d
scl = {"pat": "scales", "frame": "body"}
# (x positions along the straight body, to size each segment by: the joints' own x as they would be laid out straight)
xs = [.45]
for l in L: xs.append(xs[-1] - l)
# the front: neck into the trunk, on the body bone
S("front", type="tube", pts=[["$body", .25, 0, 0, r_at(.7)], ["$body", .17, 0, 0, r_at(.62)], ["$body", .08, 0, 0, r_at(.53)], ["$body", 0, 0, 0, r_at(.45)]], k=.004, color="@body", **scl)
S("frontV", type="tube", pts=[["$body", .27, -.0045, 0, r_at(.7) * .7], ["$body", .2, -.0055, 0, r_at(.65) * .64], ["$body", 0, -.009, 0, r_at(.45) * .62]], k=.003, kc=.006, color="@belly")
for i in range(len(L)):
    b = f"seg{i + 1}"; x0, x1 = xs[i], xs[i + 1]; r0, rm, r1 = r_at(x0), r_at((x0 + x1) / 2), r_at(x1)
    prev = "$body" if i == 0 else f"$seg{i}.mid"
    pts = [[prev, 0, 0, 0, r_at(x0 + L[i - 1] / 2 if i else x0 + .06)], [f"${b}", 0, 0, 0, r0], [f"${b}.mid", 0, 0, 0, rm], [f"${b}.end", 0, 0, 0, r1]]
    if i + 1 < len(L): pts.append([f"$seg{i + 2}.mid", 0, 0, 0, r_at(x1 - L[i + 1] / 2)])
    S(b, type="tube", bone=b, pts=pts, k=.003, color="@body", **scl)
    S(b + "V", type="tube", bone=b, pts=[[f"${b}", 0, -r0 * .42, 0, r0 * .62], [f"${b}.end", 0, -r1 * .42, 0, r1 * .62]], k=.003, kc=.006, color="@belly")
sh = [p for p in sh if p]
# (the bars' centres: along each segment at t, on its flank -- written as joint offsets resolved here from the rest chain)
def joints():
    import math
    J = {}; W = {}
    def mat(rz): return rz
    pos = {"body": ([.45, Y, 0], 0.0)}
    ang = 0.0; at = [.45, Y, 0]
    out = {}
    for i, (l, ro) in enumerate(zip(L, ROT)):
        if i: at = [at[0] - l0 * math.cos(math.radians(ang)), Y, at[2] + l0 * math.sin(math.radians(ang))]
        ang += ro; l0 = l
        end = [at[0] - l * math.cos(math.radians(ang)), Y, at[2] + l * math.sin(math.radians(ang))]
        out[f"seg{i + 1}"] = (at, end, ang)
    return out
JJ = joints()
extra = []
# the dark marks down each flank: irregular -- spaced unevenly, of varied length and breadth, some single bars, some in
# pairs, some broken in two, and smaller blotches high on the back between them; each side its own
import random
def seg_at(x):   # the segment, and how far along it, at x along the body laid straight
    for i in range(len(L)):
        if xs[i] >= x >= xs[i + 1]: return i, (xs[i] - x) / L[i]
    return len(L) - 1, 1.0
E_ = .0005   # how far a mark stands proud at its middle
def mark(id_, x, sg, lift, ex, ey, col):
    # a lens of paint: an ellipsoid curved a little tighter than the body, its middle E_ proud, so it meets the scales
    # at ex (along the body) and ey (round it) from its middle and lies flush everywhere else -- no slab, no step
    i, t = seg_at(x); b = f"seg{i + 1}"; a_, e_, ang = JJ[b]; c = lerp(a_, e_, t); rr = r_at(x)
    n = [sg * math.sin(math.radians(ang)), 0, sg * math.cos(math.radians(ang))]; L_ = math.radians(lift)
    dd = nrm([n[0] * math.cos(L_), math.sin(L_), n[2] * math.cos(L_)])
    tx = nrm([e_[k] - a_[k] for k in range(3)])
    ty = [dd[1] * tx[2] - dd[2] * tx[1], dd[2] * tx[0] - dd[0] * tx[2], dd[0] * tx[1] - dd[1] * tx[0]]
    cz = .82 * rr; h = math.sqrt(cz / (1 / rr + 2 * E_ / ey ** 2)); w = ex * math.sqrt(cz / (2 * E_))
    extra.append({"id": id_, "type": "ell", "bone": b, "c": c, "r": [w, h, cz], "axes": [tx, ty, dd], "k": .0012, "kc": .0012, "color": col, "_ray": (c, dd)})
for sg, S_ in ((1, "L"), (-1, "R")):
    rng = random.Random(11 if sg > 0 else 23); x = .43 - rng.uniform(0, .03); j = 0
    while r_at(x) >= .0075:
        rr = r_at(x); kind = rng.random(); col = "@bar" if rng.random() < .6 else "@bar2"
        ex, ey = rng.uniform(.0028, .006), rr * rng.uniform(.4, .75); lift = rng.uniform(-12, 18)
        if kind < .5:
            mark(f"bar{S_}{j}", x, sg, lift, ex, ey, col)
            if rng.random() < .45:   # a ragged blotch: a second lobe offset up or down and along
                mark(f"bar{S_}{j}c", x + rng.uniform(-.006, .006), sg, lift + rng.choice((-1, 1)) * rng.uniform(16, 26), ex * rng.uniform(.7, 1.0), ey * .5, col)
        elif kind < .75:   # a pair, close together
            mark(f"bar{S_}{j}", x, sg, lift, ex * .7, ey, col); mark(f"bar{S_}{j}b", x - rng.uniform(.011, .017), sg, lift + rng.uniform(-8, 8), ex * .65, ey * rng.uniform(.6, .9), col)
        else:              # broken: an upper and a lower piece
            mark(f"bar{S_}{j}", x, sg, lift + 26, ex, ey * .45, col); mark(f"bar{S_}{j}b", x - rng.uniform(-.004, .006), sg, lift - 16, ex * .9, ey * .45, col)
        j += 1; x -= rng.uniform(.034, .09)
    x = .41 - rng.uniform(0, .04); j = 0
    while r_at(x) >= .009:
        if rng.random() < .75:
            rs = rng.uniform(.0028, .005); mark(f"barD{S_}{j}", x, sg, rng.uniform(42, 60), rs * rng.uniform(.9, 1.5), rs, "@bar" if rng.random() < .5 else "@bar2")
        j += 1; x -= rng.uniform(.04, .095)
sh += extra
# ---- the head: distinct from the neck, flat-topped, wider at the jaws; big plates over the eyes; the yellow collar
# and the black one behind it
H = "head"
S("skull", type="ell", bone=H, c=[.738, Y + .002, 0], r=[.03, .0082, .0205], k=.004, color="@body", **scl)
S("snout", type="ell", bone=H, c=[.765, Y + .0005, 0], r=[.014, .0065, .012], k=.004, color="@body", **scl)
S("jaw", type="ell", bone=H, c=[.731, Y - .0045, 0], r=[.032, .0062, .0215], k=.004, color="@body", **scl)
S("chin", type="ell", bone=H, c=[.733, Y - .0075, 0], r=[.03, .0035, .0135], k=.003, kc=.005, color="@belly")   # (the pale only under the jaw, running on into the belly strip)
S("temple", type="ell", bone=H, c=[.727, Y + .0005, .0105], r=[.016, .0062, .009], k=.004, color="@body", mirror=True, **scl)
S("brow", type="ell", bone=H, c=[.753, Y + .0082, .0105], r=[.0085, .0026, .0042], k=.0015, kc=.001, color="@body", mirror=True)   # (the supraocular ridge over each eye)
TOP = Y + .0102   # the skull's crown: the head plates, near flat, each a dark rim under a body-coloured face
for pid, c, r, m in (("frontal", [.751, 0], [.0075, .0046], False), ("parietal", [.733, .0056], [.0095, .0055], True), ("supraoc", [.753, .0092], [.0062, .0026], True), ("internas", [.768, .0035], [.004, .0032], True)):
    yy = TOP - (.0015 if pid != "internas" else .0045)
    S(pid + "Rim", type="ell", bone=H, c=[c[0], yy - .0004, c[1]], r=[r[0] + .0008, .0012, r[1] + .0008], k=0, color="@plate", **({"mirror": True} if m else {}))
    S(pid, type="ell", bone=H, c=[c[0], yy, c[1]], r=[r[0], .0012, r[1]], k=0, color="@body", **({"mirror": True} if m else {}))
S("mouth", type="tube", bone=H, pts=[[.778, Y - .0025, .0045, .0009], [.765, Y - .003, .0112, .0009], [.745, Y - .003, .0185, .0009], [.722, Y - .002, .0195, .0008]], k=.0008, kc=.0004, color="@mouth", mirror=True)
S("tongue", type="tube", bone="tongue", pts=[[.768, Y - .0035, 0, .0013], [.782, Y - .0038, 0, .0012], [.792, Y - .0042, 0, .001]], k=.0006, color="@tongue")
for sg in (1, -1):
    a = math.radians(16 * sg)
    # (each tine one tube from inside the mouth along the tongue and out to its point -- rooted in the head, not
    #  chained on the tongue's end; the tongue's own tube is the thicker stem round them)
    b_ = [.791 + .011 * math.cos(a), Y - .0048, .011 * math.sin(a)]; a_ = [.770, Y - .0036, 0]
    S(f"fork{'L' if sg > 0 else 'R'}", type="tube", bone="tongue", pts=[a_ + [.00095], [.789, Y - .0042, 0, .0009], b_ + [.0004]], k=.0005, color="@tongue")
S("collarY", type="ell", c=[.706, Y + .0025, .0058], r=[.0085, .0085, .0048], rot=[25, 0, 0], k=.0015, kc=.008, color="@collar", mirror=True)
S("collarB", type="ell", c=[.689, Y + .0025, .0062], r=[.0085, .0095, .005], rot=[25, 0, 0], k=.0015, kc=.008, color="@bar", mirror=True)

d = {
    "name": "snake",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a grass snake 1.5 m long, resting in a gentle S on a chain of seven segments that swing a beat apart (a wave running back down it as it goes) -- round in section, 4.3 cm thick, a slender neck and a tail that tapers over its last third; olive scales over a pale belly, dark bars down each flank; a distinct flat-topped head with plates over the eyes, round pupils, the mouth line, the yellow collar and the black one behind it, the forked tongue flicking",
    "kind": "parts",
    "flags": {"print": "none"},
    "colors": {"body": "#5d6a3a", "belly": "#c9c3a0", "bar": "#1a1c12", "bar2": "#2c3020", "collar": "#e0c64a", "mouth": "#262418", "tongue": "#6a1c28", "plate": "#2e341c", "eye": "#b8902e"},
    "parts": parts,
    "sculpt": {
        "keep": [],
        "patScale": .075,
        "mesh": {"cell": .0036, "tris": [7600, 2000]},
        "shape": sh,
        "eyes": {"at": [.758, Y + .0045, .013], "from": [.753, Y + .004, 0], "r": .0034, "iris": "@eye", "pupil": "round", "lid": "@body", "sink": .5},
    },
}
rays = [p for p in sh if "_ray" in p]
for p in rays: p["_c"] = p.pop("_ray")
dump("others/snake.json", d)   # (pass 1: the body without the marks matters; the marks are excluded from the probe)
import subprocess, os
out = subprocess.check_output(["node", __file__.rsplit("/", 1)[0] + "/cprobe.mjs", "snake", "", json.dumps([p["_c"][0] + p["_c"][1] for p in rays])],
                              cwd="/home/martin/store/apps/multiverse", env={**os.environ, "RX": "bar"}).decode().strip().split("\n")
for p, line in zip(rays, out):
    sp = [float(v) for v in line.split("surface at ")[1].split(",")]; n = p.pop("_c")[1]
    rz = p["r"][2]
    p["c"] = [sp[i] - n[i] * (rz - E_) for i in range(3)]
dump("others/snake.json", d)
print(len(sh), "shapes,", len(rays), "marks set on the surface")
