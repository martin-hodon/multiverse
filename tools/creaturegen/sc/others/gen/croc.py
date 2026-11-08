import sys; sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import *
PI = math.pi
DY = -.04
def tube(a, b, r1, r2, c=None):
    return {"a": a, "c": c or lerp(a, b, .5), "b": b, "r1": r1, "r2": r2}
parts = [
    {"id": "body", "parent": None, "shape": "tube", "size": tube([-0.62, 0, 0], [0.62, 0, 0], .19, .19, [0, .02, 0]), "pos": [0, .3 + DY, 0], "color": "@back"},
    {"id": "head", "parent": "body", "shape": "tube", "size": tube([0, 0, 0], [.55, -.02, 0], .1, .045), "pos": [.8, .02, 0], "color": "@back",
     "anim": {"axis": "y", "deg": 7, "speed": .25, "phase": 0}},
    {"id": "jaw", "parent": "head", "shape": "tube", "size": tube([0, 0, 0], [.5, -.01, 0], .06, .035), "pos": [.02, -.05, 0], "color": "@belly"},
    {"id": "tail1", "parent": "body", "shape": "tube", "size": tube([0, 0, 0], [-.6, -.01, 0], .17, .12), "pos": [-.62, -.01, 0], "color": "@back",
     "anim": {"axis": "y", "deg": 6, "speed": .8, "phase": .6}},
    {"id": "tail2", "parent": "tail1", "shape": "tube", "size": tube([0, 0, 0], [-.58, -.01, 0], .12, .07), "pos": [-.6, -.01, 0], "color": "@back",
     "anim": {"axis": "y", "deg": 9, "speed": .8, "phase": 1.4}},
    {"id": "tail3", "parent": "tail2", "shape": "tube", "size": tube([0, 0, 0], [-.55, 0, 0], .07, .02), "pos": [-.58, -.01, 0], "color": "@back",
     "anim": {"axis": "y", "deg": 13, "speed": .8, "phase": 2.2}},
]
for S, sz in (("L", 1), ("R", -1)):
    z = lambda v: [v[0], v[1], v[2] * sz]
    parts += [
        {"id": f"legF{S}u", "parent": "body", "shape": "tube", "size": tube([0, 0, 0], z([-.01, -.02, .2]), .07, .055), "pos": z([.45, -.05, .16]), "color": "@back",
         "anim": {"axis": "y", "deg": 22, "speed": .8, "phase": 0}},
        {"id": f"legF{S}l", "parent": f"legF{S}u", "shape": "tube", "size": tube([0, 0, 0], z([.03, -.15, .01]), .055, .04), "pos": z([-.01, -.02, .2]), "color": "@back"},
        {"id": f"legH{S}u", "parent": "body", "shape": "tube", "size": tube([0, 0, 0], z([.05, -.01, .24]), .085, .065), "pos": z([-.42, -.05, .16]), "color": "@back",
         "anim": {"axis": "y", "deg": 22, "speed": .8, "phase": PI}},
        {"id": f"legH{S}l", "parent": f"legH{S}u", "shape": "tube", "size": tube([0, 0, 0], z([-.04, -.155, .02]), .065, .045), "pos": z([.05, -.01, .24]), "color": "@back"},
    ]

B = "body"; F = "body"
sh = []
def S(id, **k):
    d = {"id": id}; d.update(k); sh.append(d); return d
scl = {"pat": "scales", "frame": "body"}
# ---- trunk: low, wide, flat-topped; pale belly; shoulders and hips; broad neck
S("trunk", type="ell", c=[.02, .285, 0], r=[.7, .135, .25], k=.08, color="@back", **scl)
S("flank", type="ell", c=[.0, .25, .0], r=[.6, .1, .27], k=.08, color="@flank", **scl)
S("belly", type="ell", c=[0, .2, 0], r=[.62, .075, .21], k=.08, color="@belly", **scl)
S("shoulder", type="ell", c=[.46, .27, .15], r=[.15, .1, .1], k=.06, color="@flank", mirror=True, **scl)
S("hip", type="ell", c=[-.42, .27, .15], r=[.17, .11, .11], k=.06, color="@flank", mirror=True, **scl)
S("neck", type="ell", c=[.72, .3, 0], r=[.22, .1, .17], k=.08, color="@back", **scl)
S("throat", type="ell", c=[.74, .25, 0], r=[.2, .06, .13], k=.06, color="@belly", **scl)
# dorsal osteoderms: two paired ridges of bumps over the back, the nuchal shields on the nape
def backY(x, z):   # the trunk's top there
    return .285 + .135 * math.sqrt(max(0, 1 - (x - .02) ** 2 / .49 - z * z / .0625))
for i, x in enumerate([.56, .44, .32, .2, .08, -.04, -.16, -.28, -.4, -.52]):
    for j, (z, f) in enumerate([(.05, 1), (.135, 1), (.205, .8)]):
        if j == 2 and not (-.45 < x < .5): continue
        y = backY(x, z); sl = math.degrees(math.atan2(backY(x, z + .01) - backY(x, z - .01), .02))
        S(f"osteo{j}_{i}", type="box", c=[x, y - .002, z], r=[.05 * f, .012, .038 * f], round=.006, rot=[sl, 0, 0], k=.004, kc=.002, color="@plate", mirror=True)
        S(f"keel{j}_{i}", type="cone", a=[x + .012, y + .004, z], b=[x - .012 * f, y + .006 + .026 * f, z], ra=.012 * f, rb=.004, k=.006, kc=.003, color="@keel", mirror=True)
S("dorsum", type="ell", c=[.02, .3, 0], r=[.62, .118, .24], k=.02, kc=.02, color="@scute")   # (the skin between the shields, dark)
for i, x in enumerate([.74, .66]):
    S(f"nuchal{i}", type="ell", bone=B, c=[x, .38, .045], r=[.035, .03, .035], k=.02, kc=.008, color="@scute", mirror=True)
# ---- tail: deep and flat-sided, carrying two crests of upright scutes that join into one
S("tail1", type="tube", bone="tail1", pts=[[-.5, .285, 0, .17], [-.9, .28, 0, .14], [-1.22, .275, 0, .115]], k=.06, color="@back", **scl)
S("tail1v", type="ell", bone="tail1", c=[-.9, .24, 0], r=[.36, .1, .1], k=.06, color="@belly", **scl)
def tailR(x): return .115 + (.065 - .115) * (x + 1.22) / -.58 if x > -1.8 else .065 + (.015 - .065) * (x + 1.8) / -.55
S("tail2a", type="tube", bone="tail2", pts=[[-1.22, .275, 0, .1], [-1.5, .27, 0, .066], [-1.8, .265, 0, .044]], k=.05, color="@back", **scl)
S("tail3a", type="tube", bone="tail3", pts=[[-1.8, .265, 0, .044], [-2.05, .262, 0, .03], [-2.35, .26, 0, .011]], k=.04, color="@back", **scl)
TX = [-1.3, -1.42, -1.54, -1.66, -1.78, -1.9, -2.02, -2.14, -2.26]
for i, x in enumerate(TX):
    r = tailR(x); bone = "tail2" if x > -1.8 else "tail3"
    S(f"tailC{i}", type="ell", bone=bone, c=[x, .267, 0], r=[.09, r * 1.12, r * .7], k=.04, color="@back", **scl)
S("tail2v", type="ell", bone="tail2", c=[-1.5, .238, 0], r=[.32, .06, .05], k=.05, color="@belly", **scl)
# crests: cones standing up off the tail's top (paired to x -1.55, one after)
def crest(bone, x, y0, z, h, r):
    return dict(type="cone", bone=bone, a=[x, y0, z], b=[x - h * .35, y0 + h, z], ra=r, rb=r * .2, k=r * .5, kc=r * .2, color="@scute")
xs = [-.62, -.74, -.86, -.98, -1.1, -1.22, -1.34, -1.46, -1.58]
for i, x in enumerate(xs):
    t = (x + .62) / -1.0
    r_t = .17 - (.17 - .09) * min(1, t)          # tail radius there (roughly)
    bone = "tail1" if x > -1.22 else "tail2"
    S(f"crest{i}", **crest(bone, x, .275 + r_t * .82, .06 - .03 * t, .085 + .02 * (1 - t), .03), mirror=True)
for i, x in enumerate([-1.7, -1.82, -1.94, -2.06, -2.17, -2.27]):
    t = (x + 1.7) / -.6
    bone = "tail2" if x > -1.8 else "tail3"
    S(f"crestS{i}", **crest(bone, x, .265 + (.07 - .045 * t) * .8, 0, .085 - .04 * t, .026 - .01 * t))
# dark cross-bands on the tail (proud of it by a hair, painted hard), pale interbands low on its flanks between them
BX = [(-1.0, "tail1"), (-1.24, "tail2"), (-1.48, "tail2"), (-1.72, "tail2"), (-1.96, "tail3"), (-2.18, "tail3")]
for i, (x, bone) in enumerate(BX):
    r = .125 if x > -1.22 else tailR(x); rz = r * .97 if x > -1.22 else r * .72
    S(f"band{i}", type="ell", bone=bone, c=[x, .27, 0], r=[.045, r * (1.0 if x > -1.22 else 1.14), rz * 1.03], k=0, color="@band")
    if i + 1 < len(BX):
        xm = (x + BX[i + 1][0]) / 2; r2 = .12 if xm > -1.22 else tailR(xm); rz2 = r2 * .97 if xm > -1.22 else r2 * .72
        S(f"inter{i}", type="ell", bone=bone, c=[xm, .24, 0], r=[.05, r2 * .55, rz2 * 1.03], k=0, color="@inter")
# the trunk's flank: dark bars down from the shields, pale between them (the tail's banding begun on the body)
for i, x in enumerate([.36, .16, -.04, -.24]):
    S(f"flankBar{i}", type="ell", c=[x, .3, .228], r=[.05, .08, .03], rot=[0, 0, 8], k=.008, kc=.035, color="@flankBar", mirror=True)
    S(f"flankPale{i}", type="ell", c=[x - .1, .275, .23], r=[.04, .05, .028], rot=[0, 0, 8], k=.008, kc=.02, color="@inter", mirror=True)
# ---- head: a flat skull table, raised orbits, a long flat tapering snout with the nostril bulb; teeth along the lips
def w_up(x):
    a = .088 * math.sqrt(max(0, 1 - ((x - 1.08) / .22) ** 2)) * .87
    b = .062 * math.sqrt(max(0, 1 - ((x - 1.31) / .055) ** 2)) * .87
    c = .115 if x < .95 else 0
    return max(a, b, c * math.sqrt(max(0, 1 - ((x - .9) / .12) ** 2)))
def w_lo(x):
    return max(.095 * math.sqrt(max(0, 1 - ((x - 1.04) / .31) ** 2)), .05 * math.sqrt(max(0, 1 - ((x - 1.3) / .05) ** 2)))
H = "head"; J = "jaw"
S("skull", type="box", bone=H, c=[.9, .33, 0], r=[.11, .035, .112], round=.03, k=.04, color="@back", **scl)
S("cheekJ", type="ell", bone=H, c=[.86, .305, .108], r=[.12, .055, .05], k=.04, color="@flank", mirror=True)
S("snout", type="tube", bone=H, pts=[[.96, .325, 0, .085], [1.1, .315, 0, .065], [1.24, .305, 0, .044], [1.3, .302, 0, .04]], k=.04, color="@back", **scl)
S("snoutW", type="ell", bone=H, c=[1.08, .305, 0], r=[.22, .033, .088], k=.04, color="@back", **scl)
S("rosette", type="ell", bone=H, c=[1.31, .302, 0], r=[.055, .04, .062], k=.03, color="@back", **scl)
S("nares", type="ell", bone=H, c=[1.33, .335, 0], r=[.028, .016, .03], k=.012, kc=.004, color="@scute")
S("orbit", type="ell", bone=H, c=[.93, .372, .062], r=[.05, .032, .036], k=.022, color="@back", mirror=True, **scl)
S("lid", type="ell", bone=H, c=[.947, .404, .084], r=[.04, .012, .025], rot=[-12, 0, 0], k=.012, color="@back", mirror=True, **scl)
S("lipCut", type="tube", bone=H, op="sub", pts=[[x, .282, w_up(x) * 1.03, .005] for x in (.86, .95, 1.05, 1.15, 1.25, 1.31, 1.35)], k=.006, color="@mouth", mirror=True)
S("lip", type="tube", bone=H, pts=[[x, .284, w_up(x) * .95, .008] for x in (.86, .95, 1.05, 1.15, 1.25, 1.31, 1.35)], k=.003, kc=.002, color="@mouth", mirror=True)
# lower jaw: on its own bone
S("mandible", type="ell", bone=J, c=[1.04, .258, 0], r=[.31, .028, .085], k=.04, color="@flank", **scl)
S("mandV", type="ell", bone=J, c=[1.04, .236, 0], r=[.3, .012, .065], k=.01, kc=.012, color="@belly")
S("jawHinge", type="ell", bone=J, c=[.83, .265, .118], r=[.1, .045, .045], k=.04, color="@flank", mirror=True)
S("chin", type="ell", bone=J, c=[1.3, .262, 0], r=[.05, .028, .05], k=.03, color="@belly")
# teeth (upper, pointing down over the lower lip; lower, up -- the 4th lower tooth the big one in the notch)
UPX = [.95, 1.03, 1.11, 1.19, 1.25, 1.33]; LOX = [.99, 1.07, 1.15, 1.285, 1.22]
for i, x in enumerate(UPX):
    z = w_up(x) * .99; h = .046 if i == 3 else .04
    S(f"toothU{i}", type="cone", bone=H, a=[x, .294, z], b=[x + .003, .294 - h, z + .008], ra=.0125, rb=.002, k=.002, kc=.001, color="@tooth", mirror=True)
for i, x in enumerate(LOX):
    z = w_up(x) + .006; h = .075 if i == 3 else .045
    S(f"toothL{i}", type="cone", bone=J, a=[x, .268, z], b=[x - .003, .268 + h, z + .005], ra=.0125, rb=.002, k=.002, kc=.001, color="@tooth", mirror=True)

# ---- legs: sprawled -- upper bone out sideways, lower bone down; scaled, the toes spread
for (u, l, sh0, el, wr, r0, r1, r2) in [("legFLu", "legFLl", [.45, .21, .16], [.44, .19, .36], [.47, .04, .37], .062, .042, .034),
                                         ("legHLu", "legHLl", [-.42, .21, .16], [-.37, .2, .4], [-.41, .045, .42], .08, .052, .04)]:
    fr = {"pat": "scales", "frame": {"o": "$" + u, "u": [0, 0, 1], "r": .08}}
    S(u, type="tube", bone=u, pts=[sh0 + [r0], lerp(sh0, el, .5) + [r0 * .85], el + [r1]], k=.05, color="@back", mirror=True, **fr)
    S(l, type="tube", bone=l, pts=[el + [r1], lerp(el, wr, .5) + [r1 * .86], wr + [r2]], k=.03, color="@back", mirror=True, **fr)
    S(u + "V", type="tube", bone=u, pts=[add(sh0, [0, -r0 * .45, 0]) + [r0 * .62], add(el, [0, -r1 * .45, 0]) + [r1 * .62]], k=.02, kc=.01, color="@belly", mirror=True)
hind = [-.41, .0, .40]; fore = [.47, .0, .36]
S("hand", type="ell", bone="legFLl", c=[.5, .02, .38], r=[.055, .02, .05], k=.02, color="@flank", mirror=True)
for i, ang in enumerate([-40, -10, 20, 50, 80]):
    a = math.radians(ang); o = [.5, .018, .38]; d = [math.cos(a), 0, math.sin(a)]
    S(f"finger{i}", type="cone", bone="legFLl", a=add(o, d, .03), b=add(add(o, d, .095), [0, -.008, 0]), ra=.017, rb=.008, k=.01, color="@flank", mirror=True)
S("foot", type="ell", bone="legHLl", c=[-.37, .02, .44], r=[.085, .02, .055], rot=[0, -25, 0], k=.02, color="@flank", mirror=True)
for i, ang in enumerate([-30, -5, 20, 45]):
    a = math.radians(ang); o = [-.33, .018, .45]; d = [math.cos(a), 0, math.sin(a)]
    S(f"toe{i}", type="cone", bone="legHLl", a=add(o, d, .03), b=add(add(o, d, .12), [0, -.008, 0]), ra=.018, rb=.008, k=.01, color="@flank", mirror=True)
S("web", type="ell", bone="legHLl", c=[-.27, .011, .47], r=[.07, .01, .07], rot=[0, -25, 0], k=.012, color="@flank", mirror=True)

d = {
    "name": "crocodile",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a Nile crocodile 3.6 m long -- a low, wide trunk with a pale belly, sprawled limbs (upper bones out sideways, forearms and shanks down, the hind longer), six rows of keeled osteoderms in transverse bands down the back, a deep, laterally flattened tail with two crests of upright scutes joining into one, dark tail bands with pale interbands; a flat skull table with raised orbits, a long flat snout with the nostril bulb, the teeth showing along the shut jaws",
    "kind": "parts",
    "flags": {"shore": True, "print": "paw", "legLen": .61},   # (legLen: gaitBase -- see scorpion.py; .8 x .61 = the old capsule base)
    "colors": {"back": "#3b4030", "flank": "#5a5a40", "belly": "#d0c697", "scute": "#23271a", "band": "#191c12", "inter": "#77754e", "plate": "#4b5236", "flankBar": "#30352a", "keel": "#2c3120", "tooth": "#e4dcc2", "mouth": "#3a2e22", "eye": "#6e6228"},
    "parts": parts,
    "sculpt": {
        "keep": [],
        "mesh": {"cell": .017, "tris": [6000, 1900]},
        "shade": {"back": .85, "belly": 1.1, "k": .07, "on": "@back"},
        "shape": sh,
        "eyes": {"at": [.94, .385, .095], "from": [.94, .385, 0], "r": .022, "color": "@eye", "iris": "@eye", "pupil": "slit", "lid": "@back", "sink": .55},
    },
}
def shift(p):
    if str(p.get("bone", "body")).startswith("leg"): return
    for k in ("c", "a", "b"):
        if k in p: p[k] = [p[k][0], p[k][1] + DY, p[k][2]]
    if "pts" in p: p["pts"] = [[q[0], q[1] + DY, q[2], q[3]] for q in p["pts"]]
for p in sh: shift(p)
E = d["sculpt"]["eyes"]; E["at"][1] += DY; E["from"][1] += DY
dump("others/crocodile.json", d)
print(len(sh), "shapes")
