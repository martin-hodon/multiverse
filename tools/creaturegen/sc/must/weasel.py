# weasel.py -- the least weasel SCULPTED on its rig (rigs.py weasel_rig)
import math
from rigs import *
N = "weasel"
rig = weasel_rig()
rig["c"] = {**rig["c"], "paw": "#603822", "lid": "#1a100a", "whisker": "#2a1e18", "whiskerW": "#d8d0c4"}
rig["_about"] = ("a least weasel SCULPTED on its rig (2026-11-06, gen: scratchpad sc/must/weasel.py): 20 cm nose to rump and a "
                 "4.5 cm tail, a long thin tube of a body on short legs, a long neck as thick as the small flat head; small round "
                 "ears set low, black bead eyes, a short muzzle with whiskers. Russet brown above, white below -- the upper lip, "
                 "chin, throat, chest and belly -- the line between them crisp and a little wavy (the `weasel` pattern, coatpat.js "
                 "weaselOf); the short tail brown to its end (a black tip would make it a stoat)")
write_rig(N, rig)
J = joints_of(N)
S = Sculpt()
B = "@body"
o = lambda b: J[b]["o"]
FL, FK, FF = o("legFLu"), o("legFLl"), o("footFL")
HL, HK, HF = o("legHLu"), o("legHLl"), o("footHL")
H0 = 0.1
P = "weasel"
# ---- trunk: a long even tube, the back a little arched over the loins; each length on its own spine bone (the bound's flex)
S.ell("rump", [-0.072, 0.0435, 0], [0.036, 0.0162, 0.0162], rot=[0, 0, -4], k=0.012, color=B, hair=H0, pat=P)
S.ell("loin", [-0.038, 0.0445, 0], [0.038, 0.0162, 0.0158], rot=[0, 0, 2], k=0.012, color=B, hair=H0, pat=P)
S.ell("waist", [-0.002, 0.042, 0], [0.034, 0.0148, 0.0148], rot=[0, 0, 4], bone="body2", k=0.012, color=B, hair=H0, pat=P)
S.ell("chest", [0.03, 0.0405, 0], [0.028, 0.0148, 0.0142], rot=[0, 0, 2], bone="body3", k=0.012, color=B, hair=H0, pat=P)
# ---- the neck: long, nearly as thick as the head, rising a little to it
S.tube("neck", [[0.046, 0.0415, 0, 0.0122], [0.058, 0.0447, 0, 0.0106], [0.07, 0.0475, 0, 0.0098]], bone="neck", k=0.01, color=B, hair=H0, pat=P)
# ---- head: small and flat, broad across the ears, a short tapering muzzle
S.ell("cranium", [0.078, 0.0492, 0], [0.0158, 0.0074, 0.0104], rot=[0, 0, -4], bone="head", k=0.007, color=B, hair=H0, pat=P)
S.ell("cheek", [0.084, 0.0462, 0.0052], [0.0115, 0.0054, 0.0046], rot=[0, 0, -6], bone="head", k=0.005, color=B, hair=H0, pat=P, mirror=True)
S.cone("muzzle", [0.088, 0.0482, 0], [0.1018, 0.0442, 0], 0.0068, 0.0036, bone="head", k=0.005, color=B, hair=H0, pat=P)
S.ell("jaw", [0.0925, 0.0418, 0], [0.0085, 0.0028, 0.0042], rot=[0, 0, -10], bone="head", k=0.004, color=B, hair=H0, pat=P)
S.ell("nose", [0.1042, 0.0443, 0], [0.0016, 0.0019, 0.0023], bone="head", k=0.0015, kc=0.0008, color="@nose", wet=0.4)
S.ell("ear", [0.0722, 0.0548, 0.0092], [0.0015, 0.0032, 0.0036], rot=[25, -40, 0], bone="earL", k=0.0025, color="@ear", mirror=True, hair=H0, pat=P)
# ---- whiskers: fine hairs from the muzzle's sides, out, back and a little down
for j, (dy, ang, el, L) in enumerate(((0.0012, 28, 6, 0.019), (0.0, 22, -2, 0.022), (-0.0012, 16, -10, 0.018), (0.0006, 34, 14, 0.014))):
    a = [0.0985, 0.0448 + dy, 0.0035]
    d = [-math.sin(math.radians(ang)) * 0.35 + 0.2, math.sin(math.radians(el)), math.cos(math.radians(ang))]
    dl = math.sqrt(sum(x * x for x in d)); d = [x / dl for x in d]
    S.cone(f"whisker{j}", a, [a[0] + d[0] * L, a[1] + d[1] * L, a[2] + d[2] * L], 0.00026, 0.00008, bone="head", k=0, color="@whisker" if j < 3 else "@whiskerW", mirror=True)
# ---- legs: short; the forelegs under the chest, the hind ones under the loins
S.cone("arm", [FL[0] - 0.002, FL[1] + 0.006, FL[2]], FK, 0.0062, 0.0042, bone="legFLu", k=0.005, color=B, mirror=True, hair=H0, pat=P)
S.cone("forearm", FK, [FF[0] - 0.001, FF[1] + 0.003, FF[2]], 0.0042, 0.0032, bone="legFLl", k=0.003, color=B, mirror=True, hair=H0, pat=P)
S.ell("paw", [FF[0] + 0.0028, 0.0024, FF[2]], [0.0052, 0.0024, 0.0036], bone="footFL", k=0.003, color="@paw", mirror=True, hair=H0, pat=P)
S.ell("thigh", [HL[0] + 0.002, HL[1] + 0.001, HL[2] + 0.0005], [0.011, 0.012, 0.0062], rot=[0, 0, 16], bone="legHLu", k=0.006, color=B, mirror=True, hair=H0, pat=P)
S.cone("shank", [HK[0] + 0.001, HK[1] + 0.002, HK[2]], [HF[0] - 0.001, HF[1] + 0.003, HF[2]], 0.0044, 0.0031, bone="legHLl", k=0.003, color=B, mirror=True, hair=H0, pat=P)
S.ell("foot", [HF[0] + 0.004, 0.0024, HF[2]], [0.0072, 0.0024, 0.0036], bone="footHL", k=0.003, color="@paw", mirror=True, hair=H0, pat=P)
# ---- the tail: short and thin, brown to its rounded end
T = rig["tail"]; NT = 6; Pt = arc_pts(T, NT)
TP = [[q[0], q[1], 0, 0.0056 - 0.0012 * (i / NT) - (0.0016 if i == NT else 0)] for i, q in enumerate(Pt)]
S.tube("tail", TP, bone="tail", k=0.004, kc=0.002, color="@tail", hair=H0, pat=P)
sc = {"keep": [], "mesh": {"tris": [8000, 2600], "cell": 0.0012, "focus": {"head": 4}}, "shape": S.shapes,
      "eyes": {"at": [0.0925, 0.0516, 0.0075], "from": [0.08, 0.05, 0], "r": 0.0019, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.5, "socket": 0.9}}
finish(N, rig, sc)
