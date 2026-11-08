import sys, json; sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import *
# the rig is kept as it was (ids, joints: the drider rides it); only how it is drawn is authored
d = json.load(open(R + "others/spider.json"))
J = {}
for ln in open(__file__.rsplit("/", 1)[0] + "/spider_joints.txt"):
    k, v = ln.split(None, 1); J[k] = json.loads(v)
sh = []
def S(id, **k):
    dd = {"id": id}; dd.update(k); sh.append(dd); return dd
# ---- prosoma: a low shield, the head region raised in front, a pale median band, the fovea; the sternum under it
S("prosoma", type="ell", c=[.003, .026, 0], r=[.0165, .0075, .0135], k=.003, color="@carapace", hair=.4)
S("cephalic", type="ell", bone="head", c=[.012, .0285, 0], r=[.0085, .0062, .0075], k=.003, color="@carapace", hair=.4)
S("band", type="ell", c=[.004, .0325, 0], r=[.015, .0018, .0032], k=.001, kc=.0012, color="@pale")
S("margin", type="ell", c=[.002, .0235, .0105], r=[.012, .0025, .0018], rot=[0, -8, 0], k=.001, kc=.0012, color="@pale", mirror=True)
S("fovea", type="ell", c=[-.003, .0333, 0], r=[.0028, .0009, .0009], k=.0005, kc=.0005, color="@dark")
S("sternum", type="ell", c=[.002, .0188, 0], r=[.011, .0035, .0085], k=.002, color="@dark")
S("pedicel", type="cone", a=[-.011, .0245, 0], b=[-.016, .0265, 0], ra=.0022, rb=.0022, k=.001, color="@dark")
# ---- chelicerae, fangs, the eyes (two big posterior medians forward, four small in the front row, two on top)
S("chelicera", type="ell", bone="head", c=[.0185, .0215, .0032], r=[.0038, .0058, .0032], rot=[0, 0, -18], k=.0012, color="@dark", hair=.3, mirror=True)
S("fang", type="cone", bone="head", a=[.0205, .0165, .0032], b=[.0195, .0145, .0012], ra=.0009, rb=.0003, k=.0003, color="@fang", mirror=True)
for i, z in enumerate([.0011, .003]):
    S(f"ame{i}", type="sphere", bone="head", c=[.0195, .0305, z], r=.00075, k=.0002, kc=.0002, color="@eye", wet=.9, mirror=True)
S("ple", type="sphere", bone="head", c=[.0115, .0345, .0042], r=.0011, k=.0003, kc=.0003, color="@eye", wet=.9, mirror=True)
# ---- opisthosoma: an oval abdomen with the dark heart mark and pale chevrons, the spinnerets behind
A = "abdomen"
S("abdomen", type="ell", bone=A, c=[-.034, .03, 0], r=[.021, .0145, .0158], k=.003, color="@abdomen", hair=.5)
def ay(x, z):   # the abdomen's top at (x, z)
    t = 1 - ((x + .034) / .021) ** 2 - (z / .0158) ** 2
    return .03 + .0145 * math.sqrt(max(t, 0))
S("heart", type="ell", bone=A, c=[-.026, ay(-.026, 0) - .0012, 0], r=[.008, .0014, .0026], rot=[0, 0, -10], k=.0005, kc=.0012, color="@dark")
for i, x in enumerate([-.036, -.042, -.048]):
    z = .0036 - .0006 * i
    S(f"chevron{i}", type="ell", bone=A, c=[x, ay(x, z) - .0011, z], r=[.0016, .0013, .0034 - .0005 * i], rot=[0, 35, 0], k=.0004, kc=.0011, color="@pale", mirror=True)
S("spinneret", type="cone", bone=A, a=[-.053, .0265, .0012], b=[-.0565, .025, .0018], ra=.0011, rb=.0007, k=.0004, color="@dark", mirror=True)
# ---- legs: coxa and trochanter at the body, the femur rising to the knee, patella and tibia arching on, metatarsus and
# tarsus falling to the ground (each leg's two bones), ringed pale at the joints
for i in range(4):
    f, t = f"femur{i}L", f"tibia{i}L"
    O, K, E = J[f + "|o"], J[t + "|o"], J[t + "|e"]
    E = [E[0], .0012, E[2]]
    S(f"coxa{i}", type="ell", bone=f, c=lerp(O, K, .12), r=[.0032, .0026, .0026], k=.0012, color="@leg", hair=.5, mirror=True)
    S(f"femur{i}", type="tube", bone=f, pts=[lerp(O, K, .1) + [.0026], lerp(O, K, .55) + [.0027], K + [.0023]], k=.001, color="@leg", hair=.6, mirror=True)
    P1 = add(lerp(K, E, .3), [0, .004, 0]); P2 = add(lerp(K, E, .62), [0, .0022, 0])
    S(f"tibia{i}", type="tube", bone=t, pts=[K + [.0023], P1 + [.002], P2 + [.0016], lerp(P2, E, .5) + [.0013], E + [.001]], k=.0008, color="@leg", hair=.6, mirror=True)
    for j, (P, r) in enumerate([(K, .0028), (P1, .0023), (P2, .0019)]):
        S(f"joint{i}{j}", type="sphere", bone=t, c=P, r=r * .92, k=.0004, kc=.0008, color="@ring", mirror=True)
# ---- palps: short leg-like feelers in front, the tips swollen
po, pe = J["palpL|o"], J["palpL|e"]
pe = lerp(po, pe, .8)
S("palp", type="tube", bone="palpL", pts=[po + [.0015], lerp(po, pe, .5) + [.0014], pe + [.0013]], k=.0008, color="@leg", hair=.5, mirror=True)
S("palpTip", type="ell", bone="palpL", c=pe, r=[.0019, .0016, .0016], k=.0008, color="@dark", mirror=True)

d["_about"] = "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a wolf spider, the rig as it was (the drider rides it) -- a low prosoma with the head region raised in front, a pale median band and margins, the fovea; chelicerae with fangs; eight eyes (two big posterior medians forward, four small below, two on top); a narrow pedicel to an oval abdomen with the dark heart mark and pale chevrons, spinnerets behind; each leg a coxa, a femur rising to the knee, patella and tibia arching on and the metatarsus falling to the ground, ringed pale at the joints; club-tipped palps"
d["colors"] = {"carapace": "#5a412c", "pale": "#a88a62", "dark": "#22180f", "fang": "#120c08", "abdomen": "#4c3826", "leg": "#5a4430", "ring": "#8c7050", "eye": "#0a0808"}
d["sculpt"] = {"keep": [], "mesh": {"cell": .00085, "tris": [5200, 1600]}, "shape": sh,
               "eyes": {"at": [.0168, .0335, .0026], "from": [.01, .03, .0005], "r": .0015, "color": "#060404", "iris": "#151010", "pupil": "round", "lid": "@dark", "sink": .2}}
keys = ["name", "_about", "kind", "flags", "colors", "parts", "sculpt"]
d = {k: d[k] for k in keys if k in d} | {k: v for k, v in d.items() if k not in keys}
dump("others/spider.json", d)
print(len(sh), "shapes")
