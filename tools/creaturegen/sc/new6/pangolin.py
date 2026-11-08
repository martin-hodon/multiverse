# pangolin.py -- the ground pangolin SCULPTED on its rig (rigs.py pangolin_rig)
from rigs import *
N = "pangolin"
rig = pangolin_rig()
rig["c"] = {**rig["c"], "body": "#4a3a2a", "scale": "#4a3a2a", "skin": "#74645a", "belly": "#857264", "face": "#6a584a", "claw": "#2a221c", "lid": "#3a2e26"}
rig["_about"] = ("a ground pangolin SCULPTED on its rig (2026-11-05, gen: scratchpad sc/new6/pangolin.py): 0.9 m nose to tail tip, the "
                 "back arched high over the hips, walking low on its hind legs with the forefeet's great claws curled under; a small "
                 "conical head tapering to a blunt snout; a thick broad tail as long as the body, tapering to its tip; armoured all "
                 "over the back, flanks, tail and crown in big overlapping scales -- the `pangolin` coat: staggered rows "
                 "lying back, each with its own shade, a paler free edge and its shadow on the next -- the "
                 "belly, face and inner limbs bare greyish skin")
write_rig(N, rig)
J = joints_of(N)
S = Sculpt()
o = lambda b: J[b]["o"]
FL, FK, FF = o("legFLu"), o("legFLl"), o("footFL")
HL, HK, HF = o("legHLu"), o("legHLl"), o("footHL")
SC = "@scale"
def sc(d, f="body"): d["pat"] = "pangolin"; d["frame"] = f; return d
# ---- trunk: the back arched high over the hips, falling to low shoulders
sc(S.ell("rump", [-0.08, 0.19, 0], [0.16, 0.11, 0.1], rot=[0, 0, 4], k=0.05, color=SC))
sc(S.ell("back", [0.04, 0.175, 0], [0.14, 0.09, 0.088], rot=[0, 0, -16], k=0.05, color=SC))
sc(S.ell("shoulder", [0.13, 0.135, 0], [0.085, 0.07, 0.07], rot=[0, 0, -24], k=0.04, color=SC))
S.ell("belly", [0.0, 0.125, 0], [0.15, 0.055, 0.075], rot=[0, 0, -6], k=0.04, kc=0.02, color="@belly")
S.ell("chestB", [0.12, 0.095, 0], [0.07, 0.04, 0.05], rot=[0, 0, -20], k=0.03, kc=0.015, color="@belly")
# ---- neck and head: short, then a small cone of a head to a blunt snout
sc(S.ell("neck", [0.195, 0.112, 0], [0.06, 0.05, 0.05], rot=[0, 0, -24], bone="neck", k=0.035, color=SC))
S.ell("throat", [0.2, 0.09, 0], [0.05, 0.03, 0.035], rot=[0, 0, -20], bone="neck", k=0.02, kc=0.01, color="@skin")
sc(S.ell("crown", [0.24, 0.11, 0], [0.04, 0.03, 0.032], rot=[0, 0, -18], bone="head", k=0.02, color=SC))
S.ell("cranium", [0.245, 0.098, 0], [0.042, 0.032, 0.033], rot=[0, 0, -18], bone="head", k=0.02, color="@face")
S.cone("snout", [0.255, 0.094, 0], [0.33, 0.069, 0], 0.03, 0.012, bone="head", k=0.015, color="@face")
S.ell("nose", [0.333, 0.068, 0], [0.008, 0.009, 0.01], bone="head", k=0.006, kc=0.003, color="@nose", wet=0.5)
S.ell("ear", [0.236, 0.112, 0.03], [0.005, 0.008, 0.007], bone="earL", k=0.006, color="@face", mirror=True)
# ---- tail: thick and broad at the root, flattened, tapering to its tip -- scaled all over, its edges too
T = rig["tail"]; P = arc_pts(T, 8)
for i in range(8):
    t0, t1 = i / 8, (i + 1) / 8; ra = 0.075 + (0.022 - 0.075) * t0; rb = 0.075 + (0.022 - 0.075) * t1
    a, b = P[i] + [0], P[i + 1] + [0]; m = lerp(a, b, 0.5); d = sub(b, a)
    sc(S.ell(f"tail{i}", m, [length(d) * 0.62, (ra + rb) / 2 * (0.9 - 0.18 * min(1, i / 3)), (ra + rb) / 2], rot=[0, 0, ang(d)], bone="tail", k=0.03, color=SC))
sc(S.ell("tailRoot", lerp(P[0] + [0], P[1] + [0], 0.2), [0.09, 0.075, 0.08], rot=[0, 0, ang(sub(P[2] + [0], P[0] + [0]))], k=0.04, color=SC))
# ---- fore legs: short and stout, the hand's three great claws curled down and back under it
sc(S.cone("arm", [FL[0] - 0.005, FL[1] + 0.03, FL[2]], [FK[0], FK[1], FK[2]], 0.03, 0.022, bone="legFLu", k=0.025, color=SC, mirror=True))
S.cone("forearm", [FK[0], FK[1], FK[2]], [FF[0], FF[1] + 0.012, FF[2]], 0.021, 0.017, bone="legFLl", k=0.015, color="@skin", mirror=True)
S.ell("hand", [FF[0] + 0.004, 0.016, FF[2]], [0.02, 0.014, 0.015], bone="footFL", k=0.012, color="@skin", mirror=True)
for j, dz in enumerate((-0.008, 0.0, 0.008)):
    L0 = 0.028 if j == 1 else 0.022
    S.tube(f"claw{j}", [[FF[0] + 0.016, 0.018, FF[2] + dz, 0.0055], [FF[0] + 0.016 + L0 * 0.6, 0.012, FF[2] + dz * 1.2, 0.004], [FF[0] + 0.016 + L0 * 0.85, 0.003, FF[2] + dz * 1.3, 0.0025]],
           bone="footFL", k=0, color="@claw", mirror=True)
# ---- hind legs: thick thighs under the arched hips, plantigrade feet with blunt nails
sc(S.ell("thigh", [HL[0] + 0.005, HL[1] - 0.005, HL[2] + 0.01], [0.055, 0.065, 0.035], rot=[0, 0, 12], bone="legHLu", k=0.03, color=SC, mirror=True))
S.cone("shank", [HK[0] + 0.004, HK[1] + 0.01, HK[2]], [HF[0], HF[1] + 0.014, HF[2]], 0.027, 0.02, bone="legHLl", k=0.015, color="@skin", mirror=True)
S.ell("foot", [HF[0] + 0.014, 0.011, HF[2]], [0.032, 0.011, 0.02], bone="footHL", k=0.01, color="@skin", mirror=True)
for j, dz in enumerate((-0.01, 0.0, 0.01)):
    S.cone(f"nail{j}", [HF[0] + 0.04, 0.008, HF[2] + dz], [HF[0] + 0.053, 0.003, HF[2] + dz * 1.15], 0.004, 0.002, bone="footHL", k=0, color="@claw", mirror=True)
sc_ = {"keep": [], "mesh": {"tris": [6800, 2300]}, "shape": S.shapes,
       "eyes": {"at": [0.272, 0.104, 0.024], "from": [0.24, 0.1, 0], "r": 0.0045, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.5, "socket": 1.0},
       "patScale": 1.15}
finish(N, rig, sc_)
