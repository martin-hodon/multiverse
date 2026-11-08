# skunk.py -- the striped skunk SCULPTED on its rig (rigs.py skunk_rig)
from rigs import *
N = "skunk"
rig = skunk_rig()
rig["c"] = {**rig["c"], "white": "#ecebe6", "paw": "#0e0c0c", "lid": "#0a0808", "claw": "#3a3430"}
rig["_about"] = ("a striped skunk SCULPTED on its rig (2026-11-05, gen: scratchpad sc/new6/skunk.py): small, stocky and low, the back "
                 "arched highest over the hips, short legs, a small pointed head; long coarse black fur, a thin white stripe up the "
                 "forehead, a white cap on the crown and nape that splits at the shoulders into two broad white bands along "
                 "the upper flanks to the rump -- painted per pixel (the `skunk` pattern) on the trunk and "
                 "head; a long round plume of a tail carried up and arched over the back, black with a white streak along its top and a white tip")
write_rig(N, rig)
J = joints_of(N)
S = Sculpt()
B = "@body"; W = "@white"
o = lambda b: J[b]["o"]
FL, FK, FF = o("legFLu"), o("legFLl"), o("footFL")
HL, HK, HF = o("legHLu"), o("legHLl"), o("footHL")
def stripe(base, id, dx, dy, fy, fz, col, dz=0.0, mirror=False, k=None, kc=0.0015, fx=1.0):
    """a paint layer: a copy of a shape shifted (dx, dy, dz) and narrowed -- it breaks the skin only where it is the outermost"""
    d = next(q for q in S.shapes if q["id"] == base)
    c = [d["c"][0] + dx, d["c"][1] + dy, d["c"][2] + dz]
    S.ell(id, c, [d["r"][0] * fx, d["r"][1] * fy, d["r"][2] * fz], rot=d.get("rot"), bone=d.get("bone"), k=k if k is not None else d.get("k", 0.01), kc=kc,
          color=col, mirror=mirror, hair=d.get("hair"))
# ---- trunk: a stout arched pear -- low and narrow at the shoulders, rising to the broad high hips (hair kept low: fur, not gloss)
H0 = 0.15   # the coat's sheen
S.ell("chest", [0.07, 0.12, 0], [0.085, 0.058, 0.058], rot=[0, 0, 10], k=0.03, color=B, hair=H0, pat="skunk")
S.ell("barrel", [-0.03, 0.15, 0], [0.13, 0.08, 0.084], rot=[0, 0, -9], k=0.035, color=B, hair=H0, pat="skunk")
S.ell("rump", [-0.125, 0.175, 0], [0.088, 0.09, 0.098], rot=[0, 0, -12], k=0.032, color=B, hair=H0, pat="skunk")
S.ell("hips", [-0.15, 0.16, 0.035], [0.06, 0.07, 0.055], k=0.03, color=B, hair=H0, pat="skunk", mirror=True)
S.ell("belly", [-0.02, 0.105, 0], [0.12, 0.05, 0.07], k=0.03, color=B, hair=H0, pat="skunk")
# ---- neck and head: a short thick neck; a small conical head, broad at the ears, a short snout; small round ears set low
S.ell("neck", [0.148, 0.133, 0], [0.058, 0.047, 0.047], rot=[0, 0, -4], bone="neck", k=0.025, color=B, hair=H0, pat="skunk")
S.ell("cranium", [0.196, 0.143, 0], [0.038, 0.035, 0.037], rot=[0, 0, -10], bone="head", k=0.018, color=B, hair=H0, pat="skunk")
S.ell("cheek", [0.203, 0.13, 0.018], [0.027, 0.023, 0.02], bone="head", k=0.012, color=B, mirror=True, hair=H0, pat="skunk")
S.cone("snout", [0.214, 0.137, 0], [0.249, 0.123, 0], 0.025, 0.0105, bone="head", k=0.012, color=B, hair=H0, pat="skunk")
S.ell("nose", [0.253, 0.122, 0], [0.0062, 0.0072, 0.0085], bone="head", k=0.004, kc=0.002, color="@nose", wet=0.5)
S.ell("ear", [0.19, 0.163, 0.031], [0.0075, 0.0105, 0.0115], rot=[25, -25, 0], bone="earL", k=0.007, color=B, mirror=True, hair=H0, pat="skunk")
# ---- the white: a thin stripe up the forehead; a cap on the crown and nape; two bands from the shoulders to the rump --
#      painted per pixel by the `skunk` pattern (coatpat.js skunkOf) on the trunk's and the head's shapes: clean edges at
#      any distance (laid as white tubes on the measured skin, the near mesh's vertices tore them up close)
# ---- legs: short, black; long fore claws for digging
S.cone("arm", [FL[0] - 0.005, FL[1] + 0.03, FL[2]], [FK[0], FK[1], FK[2]], 0.026, 0.019, bone="legFLu", k=0.018, color=B, mirror=True, hair=H0, pat="skunk")
S.cone("forearm", [FK[0], FK[1], FK[2]], [FF[0] - 0.004, 0.016, FF[2]], 0.018, 0.014, bone="legFLl", k=0.012, color="@leg", mirror=True, hair=H0, pat="skunk")
S.ell("paw", [FF[0] + 0.004, 0.009, FF[2]], [0.018, 0.009, 0.014], bone="footFL", k=0.008, color="@paw", mirror=True)
for j, dz in enumerate((-0.007, 0.0, 0.007)):
    S.cone(f"claw{j}", [FF[0] + 0.018, 0.008, FF[2] + dz], [FF[0] + 0.03, 0.002, FF[2] + dz], 0.0028, 0.0012, bone="footFL", k=0, color="@claw", mirror=True)
S.ell("thigh", [HL[0] + 0.005, HL[1] + 0.005, HL[2] + 0.005], [0.045, 0.055, 0.03], rot=[0, 0, 10], bone="legHLu", k=0.02, color=B, mirror=True, hair=H0, pat="skunk")
S.cone("shank", [HK[0] + 0.004, HK[1] + 0.006, HK[2]], [HF[0] - 0.006, 0.014, HF[2]], 0.02, 0.014, bone="legHLl", k=0.012, color="@leg", mirror=True, hair=H0, pat="skunk")
S.ell("foot", [HF[0] + 0.01, 0.008, HF[2]], [0.026, 0.008, 0.015], bone="footHL", k=0.008, color="@paw", mirror=True)
# ---- the tail: a long round plume, as long as the body and at its fullest as thick as the body is deep, carried up
#      and arched over the back -- one thick tube (round across, not a paddle) whose skin is heaped in small sharp
#      tufts (a `fleece` of fixed size: a fringe of hair tips), its fur, the white streak along its top (the side
#      toward the back: the dorsal side, the back's stripes running on up it) and its white tip painted per pixel by
#      the `skunk` pattern, which knows this arc (coatpat.js skunkOf)
T = rig["tail"]; NT = 16; P = arc_pts(T, NT); tb = tail_bones(T)
HT = 0.12
def smooth(a, b, x): x = min(1, max(0, (x - a) / (b - a))); return x * x * (3 - 2 * x)
TP = []
for i, q in enumerate(P):
    t = i / NT
    TP.append([q[0], q[1], 0, 0.024 + 0.036 * smooth(0, 0.4, t) - 0.02 * smooth(0.7, 1.0, t)])
FUR = {"amp": 0.003, "size": 0.011}
S.tube("tail", TP[:NT // 2 + 1], bone="tail", k=0.03, kc=0.004, color="@tail", hair=HT, pat="skunk", fleece=FUR)
S.tube("tail1", TP[NT // 2 - 1:], bone="tail1", k=0.03, kc=0.004, color="@tail", hair=HT, pat="skunk", fleece=FUR)
sc = {"keep": [], "mesh": {"tris": [6400, 2200], "cell": 0.0045, "focus": {"head": 6}}, "shape": S.shapes,
      "eyes": {"at": [0.22, 0.147, 0.0225], "from": [0.196, 0.142, 0], "r": 0.004, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.68, "socket": 1.0}}
finish(N, rig, sc)
