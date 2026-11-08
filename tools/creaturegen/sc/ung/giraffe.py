# giraffe.py -- the giraffe, written from its rig's joints
from lib import *
J = joints("giraffe")
S = Sculpt()
B = "@body"; G = dict(pat="spots")
# ---- trunk: short, sloping steeply from the high withers to the rump; massive shoulders, the belly tucked up
S.ell("chest", [0.42, 2.4, 0], [0.48, 0.44, 0.34], k=0.1, color=B, **G)
S.ell("withers", [0.36, 2.66, 0], [0.48, 0.2, 0.22], rot=[0, 0, -16], k=0.16, color=B, **G)
S.ell("barrel", [-0.12, 2.34, 0], [0.58, 0.37, 0.35], rot=[0, 0, 9], k=0.1, color=B, **G)
S.ell("rump", [-0.62, 2.32, 0], [0.34, 0.3, 0.28], rot=[0, 0, 16], k=0.09, color=B, **G)
S.ell("haunch", [-0.6, 2.14, 0.15], [0.28, 0.34, 0.13], rot=[0, 0, 8], k=0.06, color=B, mirror=True, **G)
S.ell("belly", [-0.06, 2.04, 0], [0.48, 0.14, 0.3], rot=[0, 0, 6], k=0.08, color=B, **G)
S.ell("scapula", [0.55, 2.42, 0.22], [0.13, 0.42, 0.11], rot=[0, 0, 24], k=0.06, color=B, mirror=True, **G)
S.ell("breast", [0.74, 2.28, 0], [0.18, 0.28, 0.24], rot=[0, 0, 15], k=0.12, color=B, **G)
S.ell("dock", [-0.98, 2.47, 0], [0.16, 0.07, 0.07], rot=[0, 0, 20], k=0.08, color=B, **G)
# ---- the neck: thick where it leaves the shoulders, tapering to a slim throat under the head; a short upright dark mane
npts = [[0.74, 2.58, 0, 0.3], [1.02, 3.02, 0, 0.21], [1.3, 3.5, 0, 0.16], [1.58, 3.98, 0, 0.13], [1.82, 4.38, 0, 0.115], [1.92, 4.56, 0, 0.11]]
# (ONE smooth column, not a chain of ells -- the ells' rounded ends read as humps along the dorsal and ventral lines: nearly
#  straight from the withers to the head, its radius easing down from the shoulders to the throat)
n0, n1 = npts[0], npts[-1]
def NR(t): return 0.11 + 0.19 * (1 - t) ** 1.8
S.tube("neck", [[n0[0] + (n1[0] - n0[0]) * t, n0[1] + (n1[1] - n0[1]) * t, 0, NR(t)] for t in [i / 10 for i in range(11)]], bone="neck", k=0.1, color=B, **G)
S.tube("neckV", [[n0[0] + (n1[0] - n0[0]) * t + 0.04 * (1 - t), n0[1] + (n1[1] - n0[1]) * t - 0.05 * (1 - t), 0, NR(t) * 0.85] for t in [i / 8 for i in range(7)]], bone="neck", k=0.1, color=B, **G)   # (a little deeper than wide, below)
def neckY(x): return n0[1] + (n1[1] - n0[1]) * (x - n0[0]) / (n1[0] - n0[0])
# the mane: a short stiff brush on the dorsal line -- a dark tube set on the skin as measured, a thinner crest on it
mx = [0.9 + i * 0.12 for i in range(9)]
tops = surf(S, [{"x": x, "y": neckY(x), "dir": [1, 0]} for x in mx])
mp = [[x, neckY(x) + h["t"] + 0.045, 0, 0.058 - 0.016 * i / 8] for i, (x, h) in enumerate(zip(mx, tops)) if h["t"]]
S.tube("mane", mp, bone="neck", k=0.012, kc=0.004, color="@mane", hair=0.6)
S.tube("maneCrest", [[p[0] - 0.012, p[1] + 0.04, 0, p[3] * 0.55] for p in mp], bone="neck", k=0.01, kc=0.004, color="@maneTip", hair=0.6)
# ---- the head: long and tapering, a bulge of the median ossicone on the brow, the lips long and mobile
hb = J["head"]["o"]
poll = [hb[0] - 0.06, hb[1] + 0.1, 0]
tip = [J["snout"]["b"][0] + 0.03, J["snout"]["b"][1] - 0.03, 0]
tip = add(tip, norm(sub(tip, poll)), 0.13)   # (a giraffe's head is 0.6-0.7 m)
hf = Frame(poll, sub(tip, poll)); L = length(sub(tip, poll))
def H(t, h=0, z=0): return hf(t * L, h * L, z * L)
hr = hf.rot()
S.ell("cranium", H(0.2, -0.12), [0.2 * L, 0.24 * L, 0.21 * L], rot=hr, bone="head", k=0.04, color=B, pat="spots")
S.ell("boss", H(0.4, 0.04), [0.1 * L, 0.06 * L, 0.06 * L], rot=hr, bone="head", k=0.04, color=B)
S.cone("face", H(0.28, -0.08), H(0.82, -0.1), 0.17 * L, 0.1 * L, bone="head", k=0.04, color="@muzzle")
# (audit 2026-11-07: the face read as a bare cream blob -- the patches carried down the upper face to below the eyes)
S.cone("faceUp", H(0.26, -0.06), H(0.58, -0.08), 0.172 * L, 0.112 * L, bone="head", k=0.04, color=B, pat="spots")
S.ell("jaw", H(0.32, -0.25, 0.08), [0.22 * L, 0.11 * L, 0.06 * L], rot=hf.rot(-6), bone="head", k=0.03, color=B, mirror=True, pat="spots")
S.ell("muzzle", H(0.9, -0.12), [0.11 * L, 0.12 * L, 0.1 * L], rot=hr, bone="head", k=0.03, color="@muzzle")
S.ell("lipL", H(0.84, -0.24), [0.11 * L, 0.05 * L, 0.07 * L], rot=hf.rot(-6), bone="head", k=0.02, color="@muzzle")
S.ell("nostril", H(0.93, -0.03, 0.065), [0.06 * L, 0.014 * L, 0.024 * L], rot=hf.rot(40), bone="head", k=0.004, kc=0.002, color="@nose", mirror=True)
eye = H(0.3, -0.02, 0.19)
eb = H(0.1, 0.0, 0.16)
ed = norm([-0.4, 0.2, 0.9])
S.ell("ear", add(eb, ed, 0.1), [0.055, 0.115, 0.022], rot=orient(ed), bone="earL", k=0.012, kc=0.005, color="@ear", mirror=True)
# ---- legs: long and slim, the forearm longer than the hind's gaskin (the back falls away), knobby knees, pale and plain below
fx, fz = J["legFLu"]["o"][0], J["legFLu"]["o"][2]
kn = J["legFLl"]["o"][1]
hx, hz = J["legHLu"]["o"][0], J["legHLu"]["o"][2]
hk = J["legHLl"]["o"][1]
LG = "@leg"
S.ell("arm", [fx + 0.02, 1.95, fz * 0.75], [0.15, 0.3, 0.12], rot=[0, 0, -12], bone="legFLu", k=0.07, color=B, mirror=True, **G)
S.cone("forearm", [fx, 1.75, fz], [fx, kn + 0.06, fz], 0.1, 0.055, bone="legFLu", k=0.04, color=B, mirror=True, pat="spots", frame={"u": [0, 1, 0], "r": 0.07})
S.ell("knee", [fx + 0.005, kn, fz], [0.065, 0.075, 0.06], bone="legFLl", k=0.02, color=LG, mirror=True, pat="spots", frame={"u": [0, 1, 0], "r": 0.07})
S.cone("cannon", [fx, kn - 0.05, fz], [fx, 0.19, fz], 0.05, 0.042, bone="legFLl", k=0.015, color=LG, mirror=True)
S.ell("fetlock", [fx, 0.17, fz], [0.055, 0.05, 0.05], bone="legFLl", k=0.015, color=LG, mirror=True)
S.cone("pastern", [fx + 0.005, 0.16, fz], [fx + 0.04, 0.08, fz], 0.045, 0.05, bone="legFLl", k=0.012, color=LG, mirror=True)
S.ell("thigh", [hx + 0.02, 1.95, hz * 0.8], [0.22, 0.32, 0.12], rot=[0, 0, -8], bone="legHLu", k=0.07, color=B, mirror=True, **G)
S.cone("gaskin", [hx + 0.02, 1.7, hz], [hx - 0.04, hk + 0.08, hz], 0.1, 0.055, bone="legHLu", k=0.04, color=B, mirror=True, pat="spots", frame={"u": [0, 1, 0], "r": 0.07})
# (round 4: the back of the thigh straight from the point of the buttock down to the point of the hock)
ham(S, J, [0.19, 1.1], [0.055, 0.25], 0.12, 0.045, B, 0.05, zf=0.85, pat="spots", frame={"u": [0, 1, 0], "r": 0.07})
S.ell("hock", [hx - 0.02, hk, hz], [0.06, 0.07, 0.05], bone="legHLl", k=0.02, color=LG, mirror=True, pat="spots", frame={"u": [0, 1, 0], "r": 0.07})
S.sph("hockPt", [hx - 0.08, hk + 0.04, hz], 0.035, bone="legHLl", k=0.02, color=LG, mirror=True)
S.cone("hcannon", [hx - 0.02, hk - 0.05, hz], [hx, 0.15, hz], 0.05, 0.042, bone="legHLl", k=0.015, color=LG, mirror=True)
S.ell("hfetlock", [hx, 0.13, hz], [0.055, 0.05, 0.05], bone="legHLl", k=0.015, color=LG, mirror=True)
S.cone("hpastern", [hx + 0.005, 0.12, hz], [hx + 0.04, 0.05, hz], 0.045, 0.05, bone="legHLl", k=0.012, color=LG, mirror=True)
for tag, x0, z0, fy in (("", fx, fz, 0.0), ("h", hx, hz, -0.04)):
    bn = "footFL" if not tag else "footHL"
    for side, dz in (("o", 1), ("i", -1)):
        S.cone(tag + "toe" + side, [x0 + 0.02, fy + 0.085, z0 + dz * 0.028], [x0 + 0.11, fy + 0.028, z0 + dz * 0.036], 0.042, 0.03, bone=bn, k=0.008, kc=0.003, color="@foot", mirror=True)
# ---- the ossicones: thick, skin-covered, a tuft of black hair on each top
for z in (1,):
    # (round 4: SEATED -- the base measured on the skull roof and sunk 3.5 cm into it, blended (k), so the horn grows out of
    #  the head; the rig's guess stood ~3 cm clear of the field's skull. Angled a little back and out.)
    g = H(0.14, 0.0, 0.1)
    hit = surf(S, [{"x": g[0], "y": g[1], "z0": g[2], "dir": [1, 0]}])[0]
    top = [g[0], g[1] + hit["t"], g[2]]
    oa = [top[0], top[1] - 0.035, top[2]]
    ob = add(oa, norm([-0.22, 1.0, 0.2]), 0.035 + 0.13)
    print("ossicone base", R3(top), "gap was", round(H(0.14, 0.2, 0.11)[1] - 0.045 - top[1], 3))
    S.cone("ossicone", oa, ob, 0.05, 0.034, bone="head", k=0.04, color="@ossi", mirror=True)
    S.ell("ossiTuft", add(ob, sub(ob, oa), 0.12), [0.04, 0.035, 0.04], bone="head", k=0.015, kc=0.004, color="@tuft", hair=0.9, mirror=True)
# ---- the tail: long and thin, hanging to the hock, the long black tassel at its end
t0 = J["tail"]["o"]
S.cone("tailStem", t0, add(t0, [-0.1, -0.85, 0]), 0.05, 0.022, bone="tail", k=0.04, color=B)
S.ell("tassel", add(t0, [-0.13, -1.12, 0]), [0.055, 0.3, 0.045], rot=[0, 0, -4], bone="tail", k=0.03, color="@tuft", hair=0.9)
keep = []
import json
ex = json.load(open("/home/martin/store/apps/multiverse/assets/creatures/mammals/giraffe.json"))["extras"]
sc = {"_about": "THE GIRAFFE (2026-11-05, 2nd pass: a longer head with its boss, thick tufted ossicones, the patches down to the knees and hocks and on the jaw, a dark brush of a mane, the long tail with its black tassel, broad hooves): a short trunk falling steeply from high withers and massive shoulders to the rump, the belly tucked; the neck thick out of the shoulders and tapering to a slim throat, a short upright dark mane along it; a long tapering head, the median ossicone's boss on the brow, long mobile lips, ears out sideways under the kept ossicones; long slim legs, the forearm and gaskin patched, knobby knees and hocks, plain pale cannons to two-toed hooves; the coat the giraffe network (spots) on a pale ground, liver patches",
      "keep": keep, "mesh": {"tris": [7000, 2200]}, "patScale": 1.25, "shape": S.shapes,
      "eyes": {"at": R3(eye), "from": R3(H(0.3, -0.05, 0)), "r": 0.03, "iris": "@eye", "pupil": "bar", "lid": "#2a1c12", "sink": 0.62}}
cols = {"body": "#eadbb8", "muzzle": "#c9ad84", "leg": "#e6d8ba", "ear": "#d8c49c", "mane": "#7a5634", "maneTip": "#4e3420", "ossi": "#8a6a44", "tuft": "#1c1410", "nose": "#3a2a20", "foot": "#2e241c", "tail": "#d8c49c"}
print(write("giraffe", sc, {"colors": cols, "!extras": ex}), len(S.shapes), "shapes")
