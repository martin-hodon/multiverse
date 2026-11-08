import sys; sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import *
PI = math.pi
def sub(a, b): return [a[i] - b[i] for i in range(3)]
HIP, KNEE, ANK = [-.04, .024, .012], [-.004, .012, .03], [-.045, .008, .028]
SH = [.022, .024, .014]
BODY = [-.005, .03, 0]
def cap(a, b, r):   # a part's own segment (not drawn): a tube from its joint to the next
    return {"a": [0, 0, 0], "c": lerp([0, 0, 0], sub(b, a), .5), "b": sub(b, a), "r1": r, "r2": r * .8}
parts = [
    {"id": "body", "parent": None, "shape": "sphere", "size": {"r": .03}, "scale": [1.5, .75, 1.1], "pos": BODY, "color": "@back"},
    {"id": "head", "parent": "body", "shape": "sphere", "size": {"r": .016}, "scale": [1.4, .8, 1.2], "pos": sub([.03, .036, 0], BODY), "color": "@back"},
]
for S, sz in (("L", 1), ("R", -1)):
    z = lambda v: [v[0], v[1], v[2] * sz]
    parts += [
        {"id": f"thigh{S}", "parent": "body", "shape": "tube", "size": cap(z(HIP), z(KNEE), .009), "pos": z(sub(HIP, BODY)), "color": "@back",
         "anim": {"axis": "z", "deg": 30, "speed": .8, "phase": 0}},
        {"id": f"shin{S}", "parent": f"thigh{S}", "shape": "tube", "size": cap(z(KNEE), z(ANK), .006), "pos": z(sub(KNEE, HIP)), "color": "@back"},
        {"id": f"foot{S}", "parent": f"shin{S}", "shape": "tube", "size": cap(z(ANK), z([-.0, .002, .036]), .003), "pos": z(sub(ANK, KNEE)), "color": "@back"},
        {"id": f"arm{S}", "parent": "body", "shape": "tube", "size": cap(z(SH), z([.03, .003, .022]), .005), "pos": z(sub(SH, BODY)), "color": "@back",
         "anim": {"axis": "z", "deg": 20, "speed": .8, "phase": 3.14}},
    ]
sh = []
def S(id, **k):
    d = {"id": id}; d.update(k); sh.append(d); return d
sp = lambda o, r=.02, u=[1, 0, 0]: {"pat": "patches", "frame": {"o": o, "u": u, "r": r}}
TR = sp([0, .03, 0])
# ---- trunk: tilted up at the shoulders, the sacral hump behind, a pale belly
S("trunk", type="ell", c=[-.012, .03, 0], r=[.042, .018, .022], rot=[0, 0, 14], k=.01, color="@back", **TR)
S("belly", type="ell", c=[-.008, .021, 0], r=[.04, .013, .02], rot=[0, 0, 14], k=.01, color="@belly")
S("hump", type="ell", c=[-.03, .036, 0], r=[.016, .01, .014], k=.008, color="@back", **TR)
S("flank", type="ell", c=[-.01, .027, .01], r=[.03, .012, .012], rot=[0, 0, 12], k=.008, color="@side", mirror=True, **TR)
# ---- head: wide and flat, the snout rounded, a pale throat, bulging eyes on top, the tympanum behind
S("head", type="ell", bone="head", c=[.03, .037, 0], r=[.024, .012, .02], rot=[0, 0, 6], k=.01, color="@back", **TR)
S("snout", type="ell", bone="head", c=[.046, .034, 0], r=[.012, .0075, .0125], k=.008, color="@back")
S("throat", type="ell", bone="head", c=[.026, .027, 0], r=[.024, .008, .018], k=.008, color="@belly")
S("eyeBump", type="ell", bone="head", c=[.027, .043, .0115], r=[.0085, .0075, .0075], k=.004, color="@back", mirror=True)
S("lidLine", type="ell", bone="head", c=[.027, .0485, .011], r=[.007, .002, .005], k=.002, kc=.001, color="@ridge", mirror=True)
S("tympanum", type="ell", bone="head", c=[.0135, .0385, .0172], r=[.0048, .0048, .0018], rot=[0, -25, 0], k=.0015, kc=.0006, color="@tymp", mirror=True)
S("mask", type="ell", bone="head", c=[.016, .037, .0165], r=[.012, .0055, .003], rot=[0, -20, -8], k=.002, kc=.001, color="@mask", mirror=True)
S("mouth", type="tube", bone="head", pts=[[.056, .0315, .003, .0011], [.05, .0298, .011, .0011], [.038, .0288, .017, .0011], [.022, .0292, .0195, .0011], [.012, .031, .0195, .001]], k=.001, kc=.0005, color="@mouth", mirror=True)
S("nostril", type="sphere", bone="head", c=[.0525, .0375, .0042], r=.0011, k=.0005, kc=.0003, color="@mouth", mirror=True)
S("ridge", type="tube", pts=[[.018, .0445, .0135, .0015], [-.008, .043, .0158, .0017], [-.036, .036, .0135, .0014]], k=.003, kc=.0012, color="@ridge", mirror=True)
# ---- forelegs: short, straight down, the hands turned in
S("arm", type="tube", bone="armL", pts=[[.02, .026, .012, .0068], [.025, .014, .018, .0052], [.029, .004, .02, .0042]], k=.004, color="@side", mirror=True)
for i, ang in enumerate([-70, -30, 10, 45]):
    a = math.radians(ang); o = [.03, .002, .02]; dd = [math.cos(a), 0, -math.sin(a) * .9]
    S(f"finger{i}", type="cone", bone="armL", a=o, b=add(add(o, dd, .009), [0, -.001, 0]), ra=.002, rb=.0016, k=.001, color="@side", mirror=True)
# ---- hind legs folded in a Z: thigh forward, shank back, the long foot forward again, webbed toes splayed
LG = sp(HIP, .01)
S("thigh", type="tube", bone="thighL", pts=[HIP[:2] + [.01, .0095], lerp(HIP, KNEE, .5)[:2] + [.024, .0085], KNEE + [.0062]], k=.004, color="@back", mirror=True, **LG)
S("shank", type="tube", bone="shinL", pts=[KNEE + [.006], lerp(KNEE, ANK, .5) + [.0056], ANK + [.0036]], k=.003, color="@back", mirror=True, **LG)
S("tarsus", type="tube", bone="footL", pts=[ANK + [.0034], [-.03, .005, .033, .003], [-.018, .004, .036, .0026]], k=.002, color="@side", mirror=True)
for i, ang in enumerate([-20, 0, 20, 40, 62]):
    a = math.radians(ang); o = [-.019, .0035, .036]; dd = [math.cos(a), 0, math.sin(a)]
    L = [.013, .018, .024, .019, .012][i]
    S(f"toe{i}", type="cone", bone="footL", a=o, b=add(add(o, dd, L), [0, -.002, 0]), ra=.0019, rb=.0015, k=.001, color="@side", mirror=True)
S("web", type="ell", bone="footL", c=[-.007, .0018, .041], r=[.011, .0012, .009], rot=[0, -25, 0], k=.0015, color="@web", mirror=True)

d = {
    "name": "frog",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a common frog sitting, 10 cm snout to vent -- the trunk tilted up at the shoulders over a sacral hump, a wide flat head with the mouth line running back under a dark mask to the tympanum, bulging gold eyes with horizontal pupils, pale dorsolateral ridges, short forelegs with the hands turned in, the hind legs folded in a Z (thigh forward, shank back, the long foot forward again) on splayed webbed toes; dark spots over an olive-green back, a cream belly",
    "kind": "parts",
    "flags": {"shy": 3, "shore": True, "hop": {"period": .9, "h": .16}, "print": "paw"},
    "colors": {"back": "#5e8a3c", "side": "#7a9448", "belly": "#e6dfbc", "ridge": "#a8a466", "tymp": "#5c4426", "mask": "#4a3a22", "mouth": "#2a2216", "web": "#8a9a58", "eye": "#c89a3a", "eyeDark": "#6a5020"},
    "parts": parts,
    "sculpt": {
        "keep": [],
        "patScale": .16,
        "mesh": {"tris": [4500, 1400]},
        "shape": sh,
        "eyes": {"at": [.029, .045, .02], "from": [.029, .045, 0], "r": .0056, "color": "@eyeDark", "iris": "@eye", "pupil": "bar", "lid": "@back", "sink": .3},
    },
}
dump("others/frog.json", d)
print(len(sh), "shapes")
