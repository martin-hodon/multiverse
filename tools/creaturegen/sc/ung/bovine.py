# bovine.py cow|ox -- cattle sculpts on their own rigs, written from the joints
import sys, os
from lib import *
name = sys.argv[1]
OX = name == "ox"
# ---- the rig's head cluster moved back and down (the neck end, head, muzzle, ears, eyes): a real neck in front of the
#      withers, the head hanging below the topline. From the pristine rig, so a re-run never shifts it twice.
O = json.load(open(os.path.dirname(os.path.abspath(__file__)) + f"/orig_{name}.json"))
D = (-0.1, -0.12) if not OX else (-0.1, -0.11)
rig = {}
nk = list(O["neck"]); nk[3] += D[0]; nk[4] += D[1]; nk[0] -= 0.02; rig["neck"] = nk
for key in ("head", "muzzle", "eyes"):
    v = list(O[key]); v[0] += D[0]; v[1] += D[1]
    if key == "muzzle": v[3] += D[0]; v[4] += D[1]
    rig[key] = v
# the fore legs' IK joint moved up from the knee to the ELBOW (the hip into the shoulder, the bone below it forearm + cannon,
# as on the horse frame): a knee folding forward under the IK read as buck-kneed in the stride
lg = json.loads(json.dumps(O["legs"])); lg["front"][1] = round(lg["front"][1] + lg["front"][3], 4); rig["legs"] = lg
# (round 4: the hind legs moved BACK 15 cm, under the pins -- the rump stood out over them as a shelf, the thigh behind a
#  thin shank; a cow's hock stands about under its pin bones)
lg["hind"][0] = round(lg["hind"][0] - (0.16 if OX else 0.15), 4)
e = list(O["ears"]); e[0] += D[0]; e[1] += D[1]; e[3] += D[0]; e[4] += D[1]; rig["ears"] = e
HS, HJ = O["headScale"], [nk[3], nk[4], 0]
pre = json.load(open(ROOT + f"assets/creatures/mammals/{name}.json"))
if any(pre.get(k) != v for k, v in rig.items()):
    pre.update(rig); json.dump(pre, open(ROOT + f"assets/creatures/mammals/{name}.json", "w"), indent=2, ensure_ascii=False)
J = joints(name)
s = 1.065 if OX else 1.0
W = 1.22 if OX else 1.16   # (broad: a cow's trunk is half its height across)
LT = 1.25 if OX else 1.0   # (an ox's legs: a quarter thicker)
S = Sculpt()
B = "@body"
pat = {}   # (the cow's patches: sharp decals laid on the skin below -- the engine's piebald edge is soft)
def P(x, y, z=0): return [x * s, y * s, z * s * W]
def r3(a, b, c): return [a * s, b * s, c * s * W]
K = lambda k: k * s
# ---- trunk: a long deep barrel on a straight back, sharp withers, the hip bones (hooks) and pin bones under the skin
S.ell("barrel", P(-0.08, 1.08), r3(0.66, 0.35, 0.35), k=K(0.1), color=B, **pat)
FQ = "@fore" if OX else B   # (an ox's forequarters and neck: a shade darker)
S.ell("chest", P(0.36, 1.09), r3(0.34, 0.36, 0.29), k=K(0.1), color=FQ, **pat)
S.ell("brisket", P(0.6, 0.86), r3(0.15, 0.14, 0.14), k=K(0.08), color=FQ, **pat)
S.ell("withers", P(0.36, 1.37), r3(0.3, 0.1, 0.12), rot=[0, 0, -6], k=K(0.08), color=FQ, **pat)
if OX: S.ell("hump", P(0.38, 1.43), r3(0.34, 0.13, 0.19), rot=[0, 0, -8], k=K(0.15), color=FQ)   # (the draught hump: ~8 cm over the back)
S.ell("back", P(-0.18, 1.35 if OX else 1.32), r3(0.55, 0.1, 0.26), k=K(0.15 if OX else 0.1), color=B, **pat)
S.ell("hook", P(-0.52, 1.33 if OX else 1.34, 0.23), r3(0.09, 0.05, 0.055) if OX else r3(0.1, 0.06, 0.07), k=K(0.12 if OX else 0.06), color=B, mirror=True, **pat)
S.ell("rump", P(-0.72, 1.3), r3(0.27, 0.15, 0.25), k=K(0.14 if OX else 0.08), color=B, **pat)
S.ell("pin", P(-0.93, 1.27 if OX else 1.3, 0.09), r3(0.07, 0.07, 0.05), k=K(0.05), color=B, mirror=True, **pat)
S.ell("tailhead", P(-0.92, 1.39), r3(0.1, 0.06, 0.07), k=K(0.05), color=B, **pat)
S.ell("quarter", P(-0.76, 1.02, 0.16), r3(0.2, 0.3, 0.13), rot=[0, 0, -12], k=K(0.12 if OX else 0.07), color=B, mirror=True, **pat)
S.ell("belly", P(-0.12, 0.9), r3(0.52, 0.17, 0.33), k=K(0.1), color=B, **pat)
S.ell("scapula", P(0.48, 1.2, 0.22), r3(0.1, 0.24, 0.08), rot=[0, 0, 24], k=K(0.07), color=FQ, mirror=True, **pat)
# ---- the cow's black patches: paint-only ellipsoids hugging the inside of the trunk's shapes (the engine's piebald dark is a
#      mid grey), their poles a few mm under the skin so they colour it within kc without moving it
def patch(id, c0, r0, dx, dy, px, py, side, ax=2, pz=None):
    import math
    q = 1 - (dx / r0[0]) ** 2 - ((dy / r0[1]) ** 2 if ax == 2 else 0)
    pole = r0[ax] * math.sqrt(max(q, 0.05)) - 0.002
    if ax == 2:
        c = [c0[0] + dx, c0[1] + dy, side * (pole - 0.12)]; r = [px, py, 0.12]
    else:
        c = [c0[0] + dx, c0[1], 0]; r = [px, pole, pz]
    S.ell("patch" + id, P(*c), r3(*r), k=0, kc=K(0.11), color="@patch")
if False:
    BR, BC = (-0.08, 1.03), (0.66, 0.4, 0.35)
    CH, CC = (0.36, 1.05), (0.34, 0.39, 0.29)
    BK, BKC = (-0.18, 1.35), (0.55, 0.1, 0.26)
    patch("A", BR, BC, -0.12, 0.08, 0.26, 0.2, 1)
    patch("B", BR, BC, 0.2, 0.0, 0.12, 0.2, 1)
    patch("C", BR, BC, -0.5, 0.12, 0.1, 0.12, 1)
    patch("D", CH, CC, 0.06, 0.16, 0.14, 0.17, 1)
    patch("E", BK, BKC, -0.1, 0, 0.24, 0, 0, ax=1, pz=0.2)
    patch("F", BK, BKC, 0.32, 0, 0.12, 0, 0, ax=1, pz=0.14)
    patch("G", BR, BC, 0.02, 0.1, 0.3, 0.17, -1)
    patch("H", BR, BC, -0.48, -0.06, 0.13, 0.2, -1)
    patch("I", CH, CC, 0.0, -0.05, 0.12, 0.2, -1)
# ---- neck: a real neck, deep (the crest above, the dewlap below), from the shoulder down-forward to the poll
NB = 1.15 if OX else 1.0
S.ell("neckBase", P(0.66, 1.15), r3(0.3, 0.34 * NB, 0.25 * NB), rot=[0, 0, -8], k=K(0.12), color=FQ, **pat)
S.ell("neck", P(0.93, 1.16), r3(0.26, 0.25 * NB, 0.19 * NB), rot=[0, 0, -14], bone="neck", k=K(0.1), color=FQ, **pat)
if OX: S.ell("crest", P(0.8, 1.36), r3(0.32, 0.1, 0.15), rot=[0, 0, -20], bone="neck", k=K(0.1), color=FQ)
# the dewlap: one fold of skin hanging from the jaw to the brisket (white on the cow)
dw = 1.6 if OX else 1.3
DL = FQ if OX else "@white"
S.ell("dewlap", P(0.88, 0.93), [0.3 * s, 0.1 * s * dw, 0.05 * s], rot=[0, 0, 24], bone="neck", k=K(0.09), color=DL or B, **({} if DL else pat))
S.ell("dewlap2", P(0.64, 0.82), [0.17 * s, 0.09 * s * dw, 0.065 * s], rot=[0, 0, 18], k=K(0.09), color=DL or B, **({} if DL else pat))
# ---- head: a broad flat forehead under the poll, the eyes high on its corners, a long face to a broad wet muzzle,
#      big round jaws; ears straight out to the sides under the horns
hb = J["head"]["o"]
poll = [hb[0] - 0.01 * s, hb[1] + 0.17 * s, 0]
tip = add(poll, [0.36 * s, -0.47 * s, 0])   # (the face ~37 degrees off the vertical)
hf = Frame(poll, sub(tip, poll)); L = length(sub(tip, poll))
def H(t, h=0, z=0): return hf(t * L, h * L, z * L)
hr = hf.rot()
HC = "@head"
S.ell("poll", H(0.08, -0.02), [0.12 * L, 0.12 * L, 0.27 * L], rot=hr, bone="head", k=K(0.04), color=HC, **pat)
S.ell("forehead", H(0.3, 0.02), [0.26 * L, 0.11 * L, 0.24 * L], rot=hr, bone="head", k=K(0.04), color=HC, **pat)
S.ell("jaw", H(0.42, -0.2, 0.11), [0.28 * L, 0.2 * L, 0.09 * L], rot=hf.rot(-5), bone="head", k=K(0.045), color=HC, mirror=True, **pat)
S.cone("face", H(0.32, -0.02), H(0.82, -0.05), 0.2 * L, 0.17 * L, bone="head", k=K(0.045), color=HC, **pat)
S.ell("muzzle", H(0.88, -0.07), [0.13 * L, 0.17 * L, 0.2 * L * (1 if OX else 1.15)], rot=hr, bone="head", k=K(0.035), color="@muzzle")
S.ell("nose", H(0.985, -0.03), [0.028 * L, 0.12 * L, 0.18 * L], rot=hr, bone="head", k=K(0.012), kc=0.004, color="@nose", wet=0.45)
S.ell("lip", H(0.86, -0.22), [0.1 * L, 0.06 * L, 0.12 * L], rot=hr, bone="head", k=K(0.03), color="@muzzle")
for zz in (1,):   # nostril slits, carved in the pad
    S.ell("nostril", H(1.0, -0.02, 0.1), [0.02 * L, 0.04 * L, 0.025 * L], rot=hf.rot(-30), bone="head", k=K(0.006), op="sub", mirror=True)
eye = H(0.27, 0.06, 0.25)
eb = H(0.13, 0.0, 0.25)
ed = norm([-0.15, -0.12, 1.0])
el, ew = 0.19 * s, 0.075 * s
S.ell("ear", add(eb, ed, el * 0.5), [0.022 * s, el * 0.5, ew], rot=orient(ed), bone="earL", k=K(0.012), kc=0.004, color="@ear", mirror=True)
S.ell("earIn", add(add(eb, ed, el * 0.5), [0, -0.012 * s, 0]), [0.012 * s, el * 0.4, ew * 0.7], rot=orient(ed), bone="earL", k=K(0.004), kc=0.002, color="@earIn", mirror=True)
if not OX:   # ---- a Holstein's black: big irregular patches, each two or three overlapping decals; not mirrored
    PK = "@patch"; L1, R1, UP = [0, 1], [0, -1], [1, 0]
    def G(*sp): return (sp[0], sp[1], sp[2], sp[3], sp[4], sp[5] * 1.45, sp[6] * 1.45) + sp[7:]   # (the patches a third bigger: their rims sink)
    decals(S, [G(*t) for t in [
        ("pA0", 0.34, 1.12, 0, L1, 0.2, 0.19, PK, 15), ("pA1", 0.5, 1.24, 0, L1, 0.12, 0.11, PK), ("pA2", 0.74, 1.16, 0, L1, 0.1, 0.12, PK, 30),
        ("pB0", -0.16, 1.08, 0, L1, 0.26, 0.2, PK, 8), ("pB1", -0.02, 1.25, 0, L1, 0.15, 0.1, PK), ("pB2", -0.34, 0.95, 0, L1, 0.1, 0.08, PK),
        ("pC0", -0.74, 1.17, 0, L1, 0.17, 0.15, PK, -20), ("pC1", -0.6, 1.0, 0, L1, 0.09, 0.11, PK),
        ("qA0", 0.28, 1.05, 0, R1, 0.21, 0.2, PK, -10), ("qA1", 0.12, 1.22, 0, R1, 0.12, 0.09, PK),
        ("qB0", -0.32, 1.18, 0, R1, 0.3, 0.16, PK, -8), ("qB1", -0.45, 1.02, 0, R1, 0.12, 0.1, PK), ("qB2", 0.02, 0.95, 0, R1, 0.09, 0.09, PK),
        ("qC0", -0.76, 1.08, -0.15, R1, 0.14, 0.19, PK, 10),
        ("tA", -0.22, 1.2, 0.0, UP, 0.22, 0.17, PK, 5), ("tB", 0.3, 1.2, 0.02, UP, 0.14, 0.15, PK),
        ("pD0", 0.84, 1.18, 0, L1, 0.13, 0.14, PK, 30), ("pD1", 0.64, 1.0, 0, L1, 0.1, 0.12, PK),
        ("qD0", 0.74, 1.12, 0, R1, 0.17, 0.15, PK, 25), ("qE0", 0.46, 1.26, 0, R1, 0.12, 0.1, PK),
        ("qC1", -0.6, 1.24, 0, R1, 0.16, 0.12, PK), ("pE0", -0.48, 1.26, 0, L1, 0.13, 0.1, PK),
        ("tC", -0.76, 1.2, 0.0, UP, 0.17, 0.18, PK), ("pF0", -0.78, 1.0, 0.1, L1, 0.1, 0.12, PK),
    ]], proud=0.009)
# ---- legs: stout; the forearm and the knee, short cannons, fetlocks with their dewclaws, two broad toes
fx, fz = J["legFLu"]["o"][0], J["legFLu"]["o"][2]
kn = O["legs"]["front"][1] - O["legs"]["front"][3]   # (the knee: where the old joint stood -- the rig's is the elbow now)
hx, hz = J["legHLu"]["o"][0], J["legHLu"]["o"][2]
hk = J["legHLl"]["o"][1]
LG = "@leg"
fl = 0.135 * s
S.ell("arm", [fx - 0.05 * s, 0.7 * s, fz * 0.85], mul(r3(0.14, 0.14, 0.1), LT), rot=[0, 0, -15], bone="legFLu", k=K(0.07), color=B, mirror=True, **pat)
S.cone("forearm", [fx - 0.02 * s, 0.64 * s, fz], [fx, kn + 0.03 * s, fz], 0.085 * s * LT, 0.052 * s * LT, bone="legFLl", k=K(0.04), color=B, mirror=True, **pat)
S.ell("knee", [fx + 0.003 * s, kn - 0.01 * s, fz], mul(r3(0.052, 0.055, 0.05), LT), bone="legFLl", k=K(0.025), color=LG, mirror=True)
S.cone("cannon", [fx, kn - 0.03 * s, fz], [fx + 0.004 * s, fl + 0.015 * s, fz], 0.045 * s * LT, 0.042 * s * LT, bone="legFLl", k=K(0.02), color=LG, mirror=True)
S.ell("fetlock", [fx - 0.004 * s, fl, fz], mul(r3(0.055, 0.05, 0.05), LT), bone="legFLl", k=K(0.02), color=LG, mirror=True)
S.sph("dewclaw", [fx - 0.05 * s, fl - 0.025 * s, fz], 0.017 * s, bone="legFLl", k=K(0.006), kc=0.002, color="@foot", mirror=True)
S.cone("pastern", [fx, fl - 0.01 * s, fz], [fx + 0.022 * s, 0.07 * s, fz], 0.045 * s * LT, 0.046 * s * LT, bone="legFLl", k=K(0.015), color=LG, mirror=True)
for side, dz in (("o", 1), ("i", -1)):
    S.ell("toe" + side, [fx + 0.04 * s, 0.034 * s, fz + dz * 0.025 * s * LT], [0.055 * s * LT ** 0.5, 0.034 * s, 0.024 * s * LT], rot=[0, 0, -15], bone="footFL", k=K(0.005), kc=0.002, color="@foot", mirror=True)
    S.ell("htoe" + side, [hx + 0.04 * s, 0.034 * s, hz + dz * 0.025 * s * LT], [0.054 * s * LT ** 0.5, 0.033 * s, 0.024 * s * LT], rot=[0, 0, -15], bone="footHL", k=K(0.005), kc=0.002, color="@foot", mirror=True)
S.ell("stifle", [hx + 0.12 * s, 0.74 * s, hz * 0.95], mul(r3(0.1, 0.13, 0.1), LT), rot=[0, 0, -15], bone="legHLu", k=K(0.06), color=B, mirror=True, **pat)
S.cone("gaskin", [hx + 0.04 * s, 0.72 * s, hz], [hx - 0.05 * s, hk + 0.04 * s, hz], 0.1 * s * LT, 0.05 * s * LT, bone="legHLu", k=K(0.04), color=B, mirror=True, **pat)
# (the hamstrings: the back of the thigh straight from under the pins to the point of the hock)
ham(S, J, [0.3, 1.2], [0.17, 0.2], 0.12 * s * LT, 0.05 * s * LT, B, K(0.07), zf=0.8, **pat)
S.ell("hock", [hx - 0.025 * s, hk - 0.005 * s, hz], mul(r3(0.058, 0.058, 0.045), LT), bone="legHLl", k=K(0.025), color=LG, mirror=True)
S.sph("hockPt", [hx - 0.08 * s, hk + 0.03 * s, hz], 0.032 * s * LT, bone="legHLl", k=K(0.025), color=LG, mirror=True)
S.cone("hcannon", [hx - 0.02 * s, hk - 0.03 * s, hz], [hx, fl + 0.015 * s, hz], 0.046 * s * LT, 0.042 * s * LT, bone="legHLl", k=K(0.02), color=LG, mirror=True)
S.ell("hfetlock", [hx - 0.004 * s, fl, hz], mul(r3(0.055, 0.05, 0.05), LT), bone="legHLl", k=K(0.02), color=LG, mirror=True)
S.sph("hdewclaw", [hx - 0.05 * s, fl - 0.025 * s, hz], 0.017 * s, bone="legHLl", k=K(0.006), kc=0.002, color="@foot", mirror=True)
S.cone("hpastern", [hx, fl - 0.01 * s, hz], [hx + 0.022 * s, 0.07 * s, hz], 0.045 * s * LT, 0.046 * s * LT, bone="legHLl", k=K(0.015), color=LG, mirror=True)
# ---- horns (rig extras, written to end up where they should on the shrunk skull)
hr0 = [O["extras"][0]["from"][0] + D[0], O["extras"][0]["from"][1] + D[1], O["extras"][0]["from"][2]]
R0 = [HJ[i] + (hr0[i] - HJ[i]) * HS for i in range(3)]
def HA(x, y, z): return add(R0, [x * s, y * s, z * s])
X = []
if OX:   # a lyre: out, then forward, then up; pale to dark tips
    pts = [(0, 0, 0, 0.064), (-0.02, 0.03, 0.14, 0.052), (0.06, 0.1, 0.26, 0.04), (0.13, 0.23, 0.31, 0.029), (0.12, 0.39, 0.29, 0.019), (0.08, 0.47, 0.27, 0.009)]
    cs = ["#e6dac2", "#dccfb4", "#cbbb9c", "#5a4c3e", "#2a2420"]
else:    # short horns, out and curving forward-up
    pts = [(0, 0, 0, 0.034), (0.0, 0.02, 0.09, 0.027), (0.05, 0.08, 0.14, 0.018), (0.09, 0.15, 0.13, 0.008)]
    cs = ["#e2d6bc", "#d8cbb0", "#5a4a3a"]
# (sculpted: ONE continuous path each, its thick run in the field and its thin point a detail lathe inside it, the dark
#  tip a sheath over the same path -- the rig's chain of pills came apart between the two)
CELL = 0.0285 if OX else 0.0302
horn(S, "horn", [HA(*p[:3]) + [p[3] * s] for p in pts], cs[1], CELL, k=K(0.01),
     tips=[(0.6, cs[-2], 1.04), (0.82, cs[-1], 1.08)] if OX else [(0.7, cs[-1], 1.06)])
if not OX:   # (audit 2026-11-07) the cow's horns gated `horns`: the polled breeds (an Angus) have none
    for q in S.shapes:
        if q["id"].startswith("horn"): q["when"] = "horns"
print("horn paths ok:", check_horns())
X += [x for x in O["extras"] if x["id"] not in ("horn", "udder", "teat")]
if not OX:   # (the udder SEATED: up against the belly between the thighs, blended in; two pairs of teats under it)
    ux = hx + 0.13
    X += [{"when": "grown", "id": "udder", "parent": "body", "ell": [round(ux, 3), 0.7, 0, 0.18, 0.15, 0.13], "color": "#e3b4a4", "k": 0.1},
          {"when": "grown", "id": "teat", "parent": "body", "from": [round(ux + 0.07, 3), 0.6, 0.055], "to": [round(ux + 0.075, 3), 0.5, 0.06], "r1": 0.019, "r2": 0.014, "color": "#d9a090", "mirror": True},
          {"when": "grown", "id": "teatB", "parent": "body", "from": [round(ux - 0.07, 3), 0.6, 0.055], "to": [round(ux - 0.075, 3), 0.5, 0.06], "r1": 0.019, "r2": 0.014, "color": "#d9a090", "mirror": True}]
keep = ["tail\\d*", "tailTuft"] + ([] if OX else ["udder", "teat.*"])
if OX:
    cols = {"head": "#5a2f1a", "fore": "#5e321c", "nose": "#2a201a", "earIn": "#a07860", "muzzle": "#c2a688", "leg": "#4e2c1a"}
    about = "THE OX (2026-11-05): a draught ox -- the cattle body plan heavier: a deep barrel on a straight back, a muscled hump of shoulder over the withers, the hip bones and pins under the hide, a deep dewlap swinging from the throat to the brisket; a broad flat forehead under the poll, a long face to a broad wet muzzle (pale), big jaws, ears straight out under the long horns; stout legs to the dewclaws and two broad toes; the horns and the tufted tail kept"
else:
    cols = {"head": "#1c1816", "ear": "#1c1816", "nose": "#c49088", "earIn": "#5a4440", "patch": "#1c1816", "white": "#e8e2d0", "muzzle": "#d8c8bc"}
    about = "THE COW (2026-11-05): a dairy cow -- a long deep barrel on a straight back, sharp withers, the angular hip bones (hooks) and pin bones and the tail head over a flat rump, thin quarters, a low round belly; a short deep neck with its dewlap; a broad flat forehead under the poll, the eyes high on its corners, a long face to a broad wet pink muzzle, big round jaws, the ears straight out under the horns; stout legs with the knee, short cannons, dewclaws, two broad toes; piebald patches over it all (the solid pattern, in the rest pose's space); the horns, the udder and the tufted tail kept"
if not OX:   # the blaze: a white stripe down the black face, laid on the measured forehead and face
    nh = norm(sub(H(0, 1), H(0, 0))); bz = []
    for t in [0.06 + 0.08 * i for i in range(10)]:
        a = H(t, -0.05); h = surf(S, [{"x": a[0], "y": a[1], "z0": 0, "dir": [1, 0]}])[0]
        if h["t"] is None: continue
        r = (0.05 + 0.035 * (1 - abs(t - 0.4) / 0.5)) * s
        bz.append([a[0] - nh[0] * (r - 0.008 * s), a[1] + h["t"] - nh[1] * (r - 0.008 * s), 0, r])
    S.tube("blaze", bz, bone="head", k=K(0.008), kc=0.004, color="@white")
sc = {"_about": about, "keep": keep, "mesh": {"tris": [6500, 2000]}, "shape": S.shapes,
      **({"shade": {"on": "@body", "back": 0.82, "belly": 1.2, "k": 0.22, "at": 0.0, "low": 0.92, "lowAt": -0.5}} if OX else {}),
      "eyes": {"at": R3(eye), "from": R3(H(0.27, 0.0, 0)), "r": round(0.024 * s, 4), "iris": "@eye", "pupil": "bar", "lid": "#2a2018", "sink": 0.4}}
UPD = {"colors": cols, "!extras": X}
if not OX:   # (audit 2026-11-07) BREEDS, picked by seed: Holstein black-and-white (twice: the dairy herd's own), a red Holstein,
    # a JERSEY (small, fawn, a dark muzzle in a pale ring), a polled black ANGUS, a red HEREFORD with its white face
    UPD["params"] = {"grown": True, "horns": True}
    UPD["!coats"] = [{"name": "holstein"}, {"name": "holstein"},
        {"name": "red holstein", "patch": "#7a3420", "head": "#7a3420", "ear": "#7a3420"},
        {"name": "jersey", "scale": 0.86, "body": "#b0814f", "patch": "#a4723f", "white": "#c7a27a", "head": "#8e6038", "ear": "#7e5430",
         "leg": "#9a6c42", "tail": "#8a5e38", "muzzle": "#2c2420", "nose": "#2a2220", "earIn": "#6a4a30"},
        {"name": "angus", "params": {"horns": False}, "body": "#1d1a19", "patch": "#1d1a19", "white": "#1d1a19", "head": "#1d1a19",
         "ear": "#1d1a19", "leg": "#1d1a19", "tail": "#1d1a19", "muzzle": "#2a2422", "nose": "#2a2422", "earIn": "#3a302c"},
        {"name": "hereford", "body": "#8a3a1c", "patch": "#8a3a1c", "head": "#ece4d4", "ear": "#8a3a1c", "leg": "#8a3a1c",
         "tail": "#7a3218", "muzzle": "#dcc0b0", "earIn": "#6a3020"}]
print(write(name, sc, UPD), len(S.shapes), "shapes")
