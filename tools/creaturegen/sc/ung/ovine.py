# ovine.py sheep|ram -- the sheep frame's sculpts: a fleece in lumps on thin dark legs
import sys
from lib import *
name = sys.argv[1]
# (round 4: the hind legs moved BACK 8 cm (x s) under the breech -- the fleece stood out behind the thigh as a shelf over a
#  thin shank -- and the rump drawn in; from the frame's values, so a re-run never shifts it twice)
FRM = json.load(open(ROOT + "assets/creatures/frames/sheep.json"))
pre = json.load(open(ROOT + f"assets/creatures/mammals/{name}.json"))
lg = {"front": FRM["legs"]["front"], "hind": ["-0.360*s"] + FRM["legs"]["hind"][1:]}
if pre.get("legs") != lg:
    pre["legs"] = lg; json.dump(pre, open(ROOT + f"assets/creatures/mammals/{name}.json", "w"), indent=2, ensure_ascii=False)
J = joints(name)
RAM = name == "ram"
s = 0.95 if RAM else 0.85
S = Sculpt()
F = "@body"
def P(x, y, z=0): return [x * s, y * s, z * s]
def r3(a, b, c): return [a * s, b * s, c * s]
K = lambda k: k * s
T = 1.2 if RAM else 1.0   # (a ram's legs: heavier)
UPF = 0.045   # (the fleece's lower edge raised: longer legs show)
# ---- the fleece: one heaped coat over barrel, chest, rump, neck and the tops of the legs
S.ell("fleece", P(-0.03, 0.68 + UPF / 2), r3(0.52, 0.29 - UPF / 2, 0.29), k=K(0.1), color=F, fleece=True)
S.ell("fleeceChest", P(0.3, 0.67 + UPF / 2 - (0.02 if RAM else 0)), r3(0.27, 0.29 - UPF / 2 + (0.03 if RAM else 0), 0.26), k=K(0.1), color="@fleeceB", fleece=True)
S.ell("fleeceRump", P(-0.37, 0.69 + UPF / 2), r3(0.27, 0.29 - UPF / 2, 0.28), k=K(0.1), color=F, fleece=True)
# the wool dirtier underneath and at the breech, a few dags behind
S.ell("belly", P(-0.05, 0.5), r3(0.4, 0.07, 0.2), k=K(0.06), kc=K(0.05), color="@dirt", fleece=True)
S.ell("breech", P(-0.585, 0.55), r3(0.07, 0.13, 0.16), k=K(0.06), kc=K(0.05), color="@dirt", fleece=True)
for i, (dz, dy) in enumerate(((0.07, 0.0), (-0.06, 0.03), (0.0, -0.03))):
    S.sph(f"dag{i}", P(-0.625, 0.5 + dy, dz), 0.03 * s, k=K(0.03), kc=K(0.02), color="@dirt", fleece=True)
S.ell("fleeceBack", P(-0.05, 0.86), r3(0.45, 0.14, 0.22), k=K(0.08), color=F, fleece=True)
nb, nt = P(0.44, 0.8), P(0.64, 0.97)
S.ell("fleeceNeck", lerp(nb, nt, 0.45), r3(0.19, 0.17, 0.16) if not RAM else r3(0.17, 0.15, 0.15), rot=[0, 0, 40], bone="neck", k=K(0.08), color="@fleeceB", fleece=True)
if not RAM: S.ell("collar", lerp(nb, nt, 0.85), r3(0.12, 0.13, 0.15), rot=[0, 0, 50], bone="neck", k=K(0.07), color=F, fleece=True)   # (the face emerges from a fleece collar)
# ---- the head: a long narrow face under a wool cap, the nose and lips, the ears straight out to the sides
hb = J["head"]["o"]
poll = add(hb, P(0.02, 0.15))   # (the poll up and forward: a neck shows)
tip = add(hb, P(0.27, -0.1))
if RAM: tip = add(hb, P(0.27, -0.12))
hf = Frame(poll, sub(tip, poll)); L = length(sub(tip, poll))
def H(t, h=0, z=0): return hf(t * L, h * L, z * L)
hr = hf.rot()
HC = "@head"
S.ell("cranium", H(0.2, -0.05), [0.24 * L, 0.24 * L, 0.24 * L * (1.2 if RAM else 1.0)], rot=hr, bone="head", k=K(0.03), color=HC)
S.ell("cap", H(0.1, 0.1), [0.24 * L, 0.18 * L, 0.26 * L] if not RAM else [0.16 * L, 0.1 * L, 0.14 * L], rot=hf.rot(10), bone="head", k=K(0.03), kc=K(0.012), color=F, fleece=True)   # (the topknot; a ram's small, clear of the horns)
S.cone("face", H(0.25, 0.0), H(0.85, -0.06), 0.18 * L, 0.11 * L, bone="head", k=K(0.03), color=HC)
if RAM: S.ell("roman", H(0.55, 0.06), [0.28 * L, 0.08 * L, 0.11 * L], rot=hf.rot(-4), bone="head", k=K(0.03), color=HC)
S.ell("jaw", H(0.45, -0.15, 0.07), [0.24 * L, 0.12 * L, 0.07 * L], rot=hf.rot(-6), bone="head", k=K(0.025), color=HC, mirror=True)
S.ell("muzzle", H(0.88, -0.1), [0.12 * L, 0.12 * L, 0.11 * L], rot=hr, bone="head", k=K(0.02), color="@muzzle")
S.ell("nose", H(0.97, -0.05), [0.03 * L, 0.06 * L, 0.08 * L], rot=hr, bone="head", k=K(0.006), kc=0.002, color="@nose", wet=0.3)
S.ell("lip", H(0.88, -0.2), [0.09 * L, 0.04 * L, 0.07 * L], rot=hr, bone="head", k=K(0.015), color="@muzzle")
eye = H(0.36, 0.06, 0.2)
eb = H(0.18, 0.02, 0.2)
# the ears: leaves, out and down (~25 degrees), a narrow stalk off the skull swelling to a broad middle and a pointed tip,
# thick enough to read edge-on
ed = norm([0.05, -0.45, 1.0])
el, ew = 0.13 * s, 0.04 * s
S.cone("earStalk", add(eb, ed, -0.01 * s), add(eb, ed, el * 0.3), 0.017 * s, 0.02 * s, bone="earL", k=K(0.012), kc=0.004, color="@ear", mirror=True)
S.ell("ear", add(eb, ed, el * 0.55), [0.022 * s, el * 0.42, ew], rot=orient(ed), bone="earL", k=K(0.012), kc=0.003, color="@ear", mirror=True)
S.ell("earTip", add(eb, ed, el * 0.88), [0.016 * s, el * 0.16, ew * 0.5], rot=orient(ed), bone="earL", k=K(0.01), kc=0.003, color="@ear", mirror=True)
S.ell("earIn", add(add(eb, ed, el * 0.55), [0.01 * s, 0, 0]), [0.012 * s, el * 0.33, ew * 0.6], rot=orient(ed), bone="earL", k=K(0.003), kc=0.002, color="@earIn", mirror=True)
# ---- legs: the fleece down to the forearm and the thigh, then thin dark bone to two toes
fx, fz = J["legFLu"]["o"][0], J["legFLu"]["o"][2]
kn = J["legFLl"]["o"][1]
hx, hz = J["legHLu"]["o"][0], J["legHLu"]["o"][2]
hk = J["legHLl"]["o"][1]
LG = "@leg"
fl = 0.1 * s
S.ell("legWool", [fx, 0.52 * s, fz * 0.9], r3(0.1, 0.13, 0.08), bone="legFLu", k=K(0.06), color=F, fleece=True, mirror=True)
S.ell("sleeve", [fx, (0.45 * s + kn) / 2 + 0.035 * s, fz], r3(0.055 * T, 0.085, 0.05 * T), bone="legFLu", k=K(0.04), kc=K(0.02), color=F, fleece=True, mirror=True)   # (wool to just above the knee)
S.cone("forearm", [fx, 0.45 * s, fz], [fx, kn + 0.02 * s, fz], 0.042 * s * T, 0.03 * s * T, bone="legFLu", k=K(0.02), color=LG, mirror=True)
S.ell("knee", [fx, kn - 0.005 * s, fz], r3(0.033 * T, 0.032, 0.03 * T), bone="legFLl", k=K(0.012), color=LG, mirror=True)
S.cone("cannon", [fx, kn - 0.02 * s, fz], [fx + 0.004 * s, fl + 0.01 * s, fz], 0.027 * s * T, 0.025 * s * T, bone="legFLl", k=K(0.01), color=LG, mirror=True)
S.cone("pastern", [fx, fl, fz], [fx + 0.018 * s, 0.045 * s, fz], 0.025 * s * T, 0.024 * s * T, bone="legFLl", k=K(0.01), color=LG, mirror=True)
S.ell("thighWool", [hx + 0.03 * s, 0.55 * s, hz * 0.85], r3(0.15, 0.16, 0.1), bone="legHLu", k=K(0.07), color=F, fleece=True, mirror=True)
# (the breech wool down the back of the thigh, straight to above the hock)
ham(S, J, [0.56, 1.4], [0.15, 0.4], 0.1 * s, 0.045 * s * T, F, K(0.05), zf=0.85, fleece=True)
S.ell("hsleeve", [hx - 0.005 * s, (0.45 * s + hk) / 2 + 0.04 * s, hz], r3(0.06 * T, 0.09, 0.052 * T), rot=[0, 0, 15], bone="legHLu", k=K(0.04), kc=K(0.02), color=F, fleece=True, mirror=True)
S.cone("gaskin", [hx + 0.02 * s, 0.45 * s, hz], [hx - 0.03 * s, hk + 0.025 * s, hz], 0.047 * s * T, 0.03 * s * T, bone="legHLu", k=K(0.02), color=LG, mirror=True)
S.ell("hock", [hx - 0.018 * s, hk, hz], r3(0.034 * T, 0.032, 0.027 * T), bone="legHLl", k=K(0.012), color=LG, mirror=True)
S.cone("hcannon", [hx - 0.018 * s, hk - 0.02 * s, hz], [hx, fl + 0.01 * s, hz], 0.027 * s * T, 0.025 * s * T, bone="legHLl", k=K(0.01), color=LG, mirror=True)
S.cone("hpastern", [hx, fl, hz], [hx + 0.018 * s, 0.045 * s, hz], 0.025 * s * T, 0.024 * s * T, bone="legHLl", k=K(0.01), color=LG, mirror=True)
for side, dz in (("o", 1), ("i", -1)):
    S.ell("toe" + side, [fx + 0.03 * s, 0.022 * s, fz + dz * 0.012 * s], [0.032 * s, 0.024 * s, 0.014 * s * T], rot=[0, 0, -15], bone="footFL", k=K(0.003), kc=0.001, color="@foot", mirror=True)
    S.ell("htoe" + side, [hx + 0.03 * s, 0.022 * s, hz + dz * 0.012 * s], [0.032 * s, 0.024 * s, 0.014 * s * T], rot=[0, 0, -15], bone="footHL", k=K(0.003), kc=0.001, color="@foot", mirror=True)
# ---- the tail: short, docked, woolly
t0 = J["tail"]["o"]
S.ell("tail", add(t0, [-0.03 * s, -0.05 * s, 0]), r3(0.05, 0.075, 0.045), rot=[0, 0, -20], bone="tail", k=K(0.04), kc=K(0.02), color=F, fleece=True)
X = None
if RAM:
    # ---- the horns: ONE spiral each side -- up from the poll, back, down and forward round the ear in a turn, ending
    #      beside the cheek at eye level, pointing out and forward; thick at the root, amber, ridged
    e0 = J["earL"]["o"]
    C = [e0[0] - 0.035 * s, e0[1] - 0.005 * s]
    pts = []
    N = 20
    TL = math.tan(math.radians(20))   # (the coil's plane tilted 20 degrees: its front swings out)
    for i in range(N + 1):
        t = i / N
        th = math.radians(78 + 310 * t)
        r = (0.105 - 0.05 * t) * s   # (a tight coil: the hole no wider than the horn)
        x, y = C[0] + r * math.cos(th), C[1] + r * math.sin(th)
        z = (0.06 + 0.17 * t ** 0.8) * s + max(0, x - C[0]) * TL
        pts.append([x, y, z, (0.072 - 0.052 * t ** 1.2) * s])
    pts[0][2] = 0.045 * s
    S.tube("horn", pts, bone="head", k=0.012 * s, kc=0.004, color="@horn", lumps={"amp": 0.004 * s, "size": 0.02 * s}, mirror=True)
    for i in range(1, N - 2):   # the ridges: darker rings across the horn, every 2-3 cm
        p = pts[i]
        S.sph(f"ridge{i}", p[:3], p[3] * 1.04, bone="head", k=0.003, kc=0.002, color="@hornRidge", mirror=True)
    X = []
keep = []
cols = {"nose": "#2a2220", "foot": "#2a2420", "earIn": "#8a6a5a", "fleeceB": "#ddd5c6", "dirt": "#b8ab92"} if not RAM else {"nose": "#4a3a30", "foot": "#3a3028", "earIn": "#a08870", "fleeceB": "#cec4b2", "dirt": "#aa9c84", "horn": "#b5a587", "hornRidge": "#8a7a60"}
about = ("THE RAM (2026-11-05, 2nd pass: the horns built here, one continuous ridged amber spiral round each ear; heavier legs, a deeper chest, a broader poll, the wool kept off the horn roots): the sheep's body plan, bigger -- the fleece heaped in lumps over barrel, chest, rump, neck and the tops of the legs; a Roman nose (the face bowed out along the bridge) under the wool cap, the ears straight out to the sides; thin legs to two toes; the curled horns and the tail kept"
         if RAM else
         "THE SHEEP (2026-11-05, 2nd pass: wool sleeves to above the knees and hocks on stouter cannons, the poll raised out of a fleece collar, the fleece toned -- dirtier under the belly and at the breech, dags -- its lower edge raised, a short woolly tail): a ewe -- the fleece one heaped coat (lumps: `fleece`) over the barrel, chest, rump and neck and down to the forearms and thighs; a long narrow dark face under a wool cap, the nose and lips, the ears straight out to the sides; thin dark legs from the wool to two toes; the tail kept")
sc = {"_about": about, "keep": keep, "mesh": {"tris": [5000, 1600]}, "shape": S.shapes,
      "eyes": {"at": R3(eye), "from": R3(H(0.36, 0.0, 0)), "r": round(0.017 * s, 4), "iris": "@eye", "pupil": "bar", "lid": "#2a2420", "sink": 0.4}}
upd = {"colors": cols}
if RAM: upd["!extras"] = None
else:
    cs = json.load(open(ROOT + "assets/creatures/mammals/sheep.json"))["coats"]
    cs[6].update({"fleeceB": "#342e29", "dirt": "#2a2420"}); cs[7].update({"fleeceB": "#cfc3ad", "dirt": "#b0a28a"}); upd["!coats"] = cs
print(write(name, sc, upd), len(S.shapes), "shapes")
