# badger.py -- the European badger SCULPTED on its rig (rigs.py badger_rig)
from rigs import *
N = "badger"
rig = badger_rig()
rig["c"] = {**rig["c"], "white": "#ecebe6", "paw": "#0e0c0b", "lid": "#0a0808", "claw": "#cdbfa6", "pad": "#1a1614"}
rig["_about"] = ("a European badger SCULPTED on its rig (2026-11-06, gen: scratchpad sc/must/badger.py): 75 cm nose to rump and a "
                 "short 15 cm tail, low and wedge-shaped, broadest and highest at the hips, on short thick black legs; long pale "
                 "digging claws on the forefeet; a small tapering head ending in a pig-like nose pad, small white-tipped ears set "
                 "low and far back. The face white with two sharp black stripes from beside the nose over the eyes and ears to the "
                 "neck, the throat black; the body coarse grizzled grey; legs and underside black -- painted per pixel (the `badger` "
                 "pattern, coatpat.js badgerOf) in the rest pose's own space")
write_rig(N, rig)
J = joints_of(N)
S = Sculpt()
B = "@body"
o = lambda b: J[b]["o"]
FL, FK, FF = o("legFLu"), o("legFLl"), o("footFL")
HL, HK, HF = o("legHLu"), o("legHLl"), o("footHL")
H0 = 0.08   # (the coat's sheen: low -- coarse matte fur, not a pelt that shines)
P = "badger"
# ---- trunk: a wedge -- low and narrow at the shoulders, rising and widening to the broad high hips; the belly slung low,
#      a fringe of long guard hair hanging along each lower flank so the short legs look shorter still
S.ell("chest", [0.1, 0.168, 0], [0.12, 0.08, 0.088], rot=[0, 0, 8], k=0.04, color=B, hair=H0, pat=P)
S.ell("barrel", [-0.06, 0.198, 0], [0.19, 0.1, 0.12], rot=[0, 0, -8], k=0.05, color=B, hair=H0, pat=P)
S.ell("rump", [-0.24, 0.222, 0], [0.14, 0.106, 0.138], rot=[0, 0, -12], k=0.045, color=B, hair=H0, pat=P)
S.ell("hips", [-0.25, 0.212, 0.066], [0.105, 0.094, 0.088], k=0.04, color=B, hair=H0, pat=P, mirror=True)
S.ell("belly", [-0.07, 0.135, 0], [0.21, 0.062, 0.105], k=0.04, color=B, hair=H0, pat=P)
S.ell("fringe", [-0.075, 0.117, 0.074], [0.175, 0.026, 0.04], rot=[0, 0, -3], k=0.03, color=B, hair=H0, pat=P, mirror=True, fleece={"amp": 0.003, "size": 0.012})
S.ell("shoulder", [0.115, 0.166, 0.042], [0.07, 0.066, 0.05], rot=[0, 0, -10], k=0.035, color=B, hair=H0, pat=P, mirror=True)
# ---- neck: short and thick, sloping down to the head carried low
S.tube("neck", [[0.15, 0.178, 0, 0.08], [0.2, 0.172, 0, 0.066], [0.245, 0.171, 0, 0.052]], bone="neck", k=0.045, color=B, hair=H0, pat=P)
# ---- head: a small wedge -- a broad flat-topped skull behind, no stop, tapering straight down to a long snout and the
#      pig-like nose pad; the lower jaw slung under it. Carried low, the nose a hand's breadth off the ground
S.ell("cranium", [0.29, 0.172, 0], [0.058, 0.046, 0.052], rot=[0, 0, -7], bone="head", k=0.022, color=B, hair=H0, pat=P)
S.ell("cheek", [0.312, 0.154, 0.026], [0.045, 0.032, 0.028], rot=[0, 0, -10], bone="head", k=0.018, color=B, hair=H0, pat=P, mirror=True)
S.cone("snout", [0.318, 0.166, 0], [0.41, 0.134, 0], 0.038, 0.0158, bone="head", k=0.02, color=B, hair=H0, pat=P)
S.ell("jaw", [0.352, 0.135, 0], [0.052, 0.018, 0.025], rot=[0, 0, -14], bone="head", k=0.016, color=B, hair=H0, pat=P)
S.ell("nose", [0.428, 0.1315, 0], [0.0085, 0.0145, 0.0175], bone="head", k=0.005, kc=0.002, color="@nose", wet=0.2)
# ---- ears: small and round, set low and far back but standing out of the head's line; black, rimmed white
S.ell("ear", [0.266, 0.211, 0.056], [0.0075, 0.0165, 0.017], rot=[10, -30, 0], bone="earL", k=0.007, color=B, mirror=True, hair=H0, pat=P)
# ---- legs: short, very thick, black; long pale digging claws on the forefeet, shorter ones behind; plantigrade feet
S.cone("arm", [FL[0] - 0.008, FL[1] + 0.03, FL[2]], FK, 0.046, 0.034, bone="legFLu", k=0.03, color=B, mirror=True, hair=H0, pat=P)
S.cone("forearm", FK, [FF[0] - 0.003, FF[1] + 0.012, FF[2]], 0.034, 0.025, bone="legFLl", k=0.016, color=B, mirror=True, hair=H0, pat=P)
S.ell("paw", [FF[0] + 0.012, 0.014, FF[2]], [0.034, 0.014, 0.029], rot=[0, -8, 0], bone="footFL", k=0.012, color="@paw", mirror=True, hair=H0, pat=P)
for j, dz in enumerate((-0.019, -0.0095, 0.0, 0.0095, 0.018)):
    L = 0.024 if j in (1, 2, 3) else 0.019
    a = [FF[0] + 0.036 - 0.004 * abs(j - 2), 0.012, FF[2] + dz]
    S.cone(f"claw{j}", a, [a[0] + L, 0.0025, a[2] + dz * 0.25], 0.0042, 0.0012, bone="footFL", k=0.002, color="@claw", mirror=True)
S.ell("thigh", [HL[0] + 0.012, HL[1] + 0.005, HL[2] - 0.005], [0.075, 0.082, 0.05], rot=[0, 0, 12], bone="legHLu", k=0.03, color=B, mirror=True, hair=H0, pat=P)
S.cone("shank", [HK[0] + 0.004, HK[1] + 0.01, HK[2]], [HF[0] - 0.006, HF[1] + 0.012, HF[2]], 0.036, 0.025, bone="legHLl", k=0.016, color=B, mirror=True, hair=H0, pat=P)
S.ell("foot", [HF[0] + 0.022, 0.012, HF[2]], [0.046, 0.012, 0.027], bone="footHL", k=0.012, color="@paw", mirror=True, hair=H0, pat=P)
for j, dz in enumerate((-0.016, -0.008, 0.0, 0.008, 0.015)):
    a = [HF[0] + 0.062 - 0.003 * abs(j - 2), 0.009, HF[2] + dz]
    S.cone(f"hclaw{j}", a, [a[0] + 0.012, 0.0025, a[2] + dz * 0.2], 0.0033, 0.0011, bone="footHL", k=0.002, color="@claw", mirror=True)
# ---- the tail: short (a fifth of the body), thick at the root and blunt, carried level; coarse grizzled hair
T = rig["tail"]; NT = 8; Pt = arc_pts(T, NT)
def smooth(a, b, x): x = min(1, max(0, (x - a) / (b - a))); return x * x * (3 - 2 * x)
TP = [[q[0], q[1], 0, 0.04 - 0.01 * (i / NT) - 0.008 * smooth(0.75, 1.0, i / NT)] for i, q in enumerate(Pt)]   # (short, thick at the root, blunt)
S.tube("tail", TP, bone="tail", k=0.03, kc=0.006, color="@tail", hair=H0, pat=P, fleece={"amp": 0.002, "size": 0.012})
sc = {"keep": [], "mesh": {"tris": [8200, 2600], "cell": 0.0055, "focus": {"head": 5, "footFL": 3, "footFR": 3}}, "shape": S.shapes,
      "eyes": {"at": [0.35, 0.173, 0.033], "from": [0.31, 0.168, 0], "r": 0.0055, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.62, "socket": 1.0}}
finish(N, rig, sc)
