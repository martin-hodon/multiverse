# hyena.py -- the spotted hyena SCULPTED on its rig (rigs.py hyena_rig)
from rigs import *
N = "hyena"
rig = hyena_rig()
rig["c"] = {**rig["c"], "body": "#a48a60", "leg": "#9a8160", "head": "#73603f", "mask": "#4c3e2e", "mask2": "#332920", "muzzleC": "#221c17", "mouth": "#120e0c", "claw": "#2a221c", "toe": "#5a4836", "throat": "#c8b490", "belly": "#cdb994", "mane": "#5a4632",
            "earIn": "#7e6c56", "earRim": "#2a201a", "foot": "#4a3a2c", "tip": "#1a1512", "lid": "#1a1410", "lip": "#2a221c", "cheek": "#a38a63", "ear": "#3e3228", "mane": "#3a2d20"}
rig["_about"] = ("a spotted hyena SCULPTED on its rig (2026-11-05, gen: scratchpad sc/new6/hyena.py): 80 cm at the withers and 1.3 m head-body; "
                 "the high massive forequarters over long forelegs, the back sloping down to low narrow hindquarters on short crouched hind legs; "
                 "a thick long neck under a short dark bristly mane; a massive broad head, the cheeks bulging with jaw muscle, a short blunt dark muzzle "
                 "and a big black nose, rounded ears; sandy grey-buff, round dark spots over the body and legs, a darker face; a short tail with a black bushy end")
write_rig(N, rig)
J = joints_of(N)
S = Sculpt()
B = "@body"
o = lambda b: J[b]["o"]
FL, FK, FF = o("legFLu"), o("legFLl"), o("footFL")
HL, HK, HF = o("legHLu"), o("legHLl"), o("footHL")
BODYF = "body"
def spots(d, f=None): d["pat"] = "dots"; return d   # (one space for every spot -- the rest pose's: no seam, no crossfade between frames)
# ---- trunk: deep high chest and withers, the back falling to a low rump
spots(S.ell("chest", [0.2, 0.63, 0], [0.28, 0.2, 0.165], k=0.07, color=B))
spots(S.ell("withers", [0.24, 0.775, 0], [0.21, 0.088, 0.118], rot=[0, 0, -10], k=0.06, color=B))
S.ell("brisket", [0.33, 0.52, 0], [0.12, 0.1, 0.1], k=0.05, kc=0.04, color="@throat")
spots(S.ell("barrel", [-0.04, 0.59, 0], [0.24, 0.14, 0.145], rot=[0, 0, 13], k=0.07, color=B))
spots(S.ell("rump", [-0.31, 0.535, 0], [0.16, 0.12, 0.125], rot=[0, 0, 12], k=0.06, color=B))
S.ell("belly", [0.0, 0.5, 0], [0.22, 0.055, 0.1], rot=[0, 0, 10], k=0.05, kc=0.04, color="@belly")
spots(S.ell("scapula", [0.31, 0.64, 0.085], [0.075, 0.16, 0.05], rot=[0, 0, 22], k=0.045, color=B, mirror=True))
# ---- neck: long, thick, carried forward; the throat paler; a short bristly dark mane along the crest to the withers
spots(S.ell("neck", [0.51, 0.752, 0], [0.2, 0.152, 0.128], rot=[0, 0, 22], bone="neck", k=0.06, color=B))
S.ell("throat", [0.57, 0.69, 0], [0.11, 0.07, 0.075], rot=[0, 0, 30], bone="neck", k=0.04, kc=0.03, color="@throat")
S.ell("maneN", [0.54, 0.86, 0], [0.13, 0.05, 0.034], rot=[0, 0, -12], bone="neck", k=0.03, kc=0.012, color="@mane", hair=0.5, fleece=True)
S.ell("maneN2", [0.42, 0.86, 0], [0.1, 0.045, 0.034], rot=[0, 0, -6], bone="neck", k=0.03, kc=0.012, color="@mane", hair=0.5, fleece=True)
S.tube("maneB", [[0.36, 0.86, 0, 0.03], [0.26, 0.845, 0, 0.026], [0.14, 0.81, 0, 0.018], [0.04, 0.76, 0, 0.01]], k=0.03, kc=0.012, color="@mane", hair=0.5)
import random; random.seed(7)
MANE = [(0.62 - 0.02 * i, 0.011 * ((i % 3) - 1) + random.uniform(-0.004, 0.004)) for i in range(25)]
ht = surf(S, [{"x": x, "y": 0.6, "dir": [1, 0], "z0": z} for x, z in MANE])
for i, ((x, z), h) in enumerate(zip(MANE, ht)):   # a rough fringe of bristles along the crest of the neck and over the withers
    if not h["t"]: continue
    top = 0.6 + h["t"]; L = (0.034 - 0.016 * (0.62 - x) / 0.48) * random.uniform(0.75, 1.15); lean = random.uniform(0.75, 1.05)
    S.cone(f"bristle{i}", [x + 0.004, top - 0.01, z], [x - L * lean, top + L * 0.6, z * 1.8], 0.0105, 0.0035, bone="neck" if x > 0.36 else None, k=0.008, kc=0.004, color="@mane", hair=0.5)
# ---- head (audit 2026-11-07, round 4: rebuilt on a new base, after a spotted hyena's profile) -- a WEDGE: the forehead
#      climbing steeply from the muzzle to a high crown topped by the sagittal crest (no separate dome); from above broad
#      and triangular, widest across the cheeks (zygomatic arches over massive masseters) and narrowing to the muzzle; the
#      muzzle ~40% of the head, deep and BOXY with a square front and a big black nose pad; a deep straight lower jaw
def box(id, c, r, rnd, rot=None, bone=None, **kw):   # a rounded box (sculpt.js "box")
    d = {"id": id, "type": "box"}
    if bone: d["bone"] = bone
    d["c"] = R3(c); d["r"] = R3(r); d["round"] = round(rnd, 4)
    if rot and any(abs(x) > 1e-6 for x in rot): d["rot"] = [round(x, 2) for x in rot]
    return S._p(d, kw)
H = "head"
box("skull", [0.672, 0.852, 0], [0.078, 0.074, 0.07], 0.05, rot=[0, 0, -8], bone=H, k=0.03, color="@head")
S.ell("crest", [0.655, 0.93, 0], [0.08, 0.032, 0.022], rot=[0, 0, -6], bone=H, k=0.03, color="@head")
S.cone("forehead", [0.69, 0.89, 0], [0.822, 0.79, 0], 0.058, 0.04, bone=H, k=0.035, kc=0.05, color="@mask")
S.ell("zyg", [0.728, 0.818, 0.07], [0.062, 0.036, 0.034], rot=[0, 0, -10], bone=H, k=0.025, kc=0.04, color="@head", mirror=True)
S.ell("masseter", [0.7, 0.768, 0.072], [0.072, 0.05, 0.042], rot=[0, 0, -20], bone=H, k=0.032, kc=0.05, color="@head", mirror=True)
S.ell("brow", [0.77, 0.862, 0.04], [0.03, 0.018, 0.026], rot=[0, 0, -30], bone=H, k=0.02, color="@mask", mirror=True)
S.ell("eyePatch", [0.785, 0.836, 0.05], [0.03, 0.022, 0.02], rot=[0, 0, -20], bone=H, k=0.014, kc=0.02, color="@mask", mirror=True)
box("muzzle", [0.868, 0.771, 0], [0.067, 0.045, 0.053], 0.026, rot=[0, 0, -6], bone=H, k=0.026, kc=0.035, color="@mask2")
box("muzzleEnd", [0.912, 0.767, 0], [0.026, 0.048, 0.052], 0.022, rot=[0, 0, -4], bone=H, k=0.014, kc=0.02, color="@muzzleC")
S.cone("jaw", [0.69, 0.738, 0], [0.892, 0.716, 0], 0.052, 0.032, bone=H, k=0.026, kc=0.03, color="@lip")
S.ell("chin", [0.885, 0.706, 0], [0.034, 0.026, 0.038], bone=H, k=0.016, kc=0.02, color="@muzzleC")
S.ell("nose", [0.93, 0.787, 0], [0.017, 0.027, 0.042], bone=H, k=0.008, kc=0.003, color="@nose", wet=0.5)
S.ell("noseTop", [0.915, 0.807, 0], [0.024, 0.011, 0.038], rot=[0, 0, -15], bone=H, k=0.008, kc=0.003, color="@nose", wet=0.5)
# the nostrils carved into the pad, a groove from it to the lip; the mouth's line carved back along the measured skin
# to its corner below the eye
S.ell("nostril", [0.946, 0.788, 0.018], [0.01, 0.011, 0.009], rot=[0, -25, -20], bone=H, k=0.008, op="sub", color="@nose", mirror=True)
S.tube("philtrum", [[0.944, 0.768, 0, 0.005], [0.938, 0.738, 0, 0.005]], bone=H, k=0.006, op="sub", color="@nose")
MX = [0.93, 0.905, 0.88, 0.855, 0.83, 0.805, 0.782]; MY = [0.728, 0.727, 0.727, 0.728, 0.729, 0.731, 0.734]
hs = surf(S, [{"x": x, "y": y, "dir": [0, 1]} for x, y in zip(MX, MY)])
MP = [[x, y, h["t"] - 0.0025, 0.0075 if i < 6 else 0.006] for i, (x, y, h) in enumerate(zip(MX, MY, hs)) if h["t"]]
S.tube("mouth", MP, bone=H, k=0.008, op="sub", color="@mouth", mirror=True)
EYE = surf(S, [{"x": 0.787, "y": 0.842, "dir": [0, 1]}])[0]["t"]   # the eye set on the measured side of the forehead
# ears: rounded, small (~60% of the old width), on the upper corners of the skull; dark backs, paler insides
ec = [0.648, 0.952, 0.066]; ER = [20, -36, 12]
S.ell("earBase", [0.652, 0.912, 0.056], [0.026, 0.026, 0.022], bone="earL", k=0.018, color="@head", mirror=True)
S.ell("ear", ec, [0.014, 0.04, 0.027], rot=ER, bone="earL", k=0.01, kc=0.004, color="@ear", mirror=True)
S.ell("earIn", add(ec, [0.01, 0.002, 0.0]), [0.005, 0.03, 0.019], rot=ER, bone="earL", k=0.003, kc=0.002, color="@earIn", mirror=True)
# ---- forelegs: long, straight, strong; spotted to the toes
LF = {"o": FL, "u": [0, -1, 0], "r": 0.06}
spots(S.tube("arm", [[FL[0] + 0.03, 0.6, FL[2], 0.075], [FL[0] + 0.0, 0.47, FL[2], 0.068], [FK[0] - 0.01, FK[1] + 0.02, FK[2], 0.052]], bone="legFLu", k=0.04, color=B, mirror=True), LF)
spots(S.cone("forearm", [FK[0] - 0.005, FK[1] + 0.01, FK[2]], [FF[0] - 0.02, 0.1, FF[2]], 0.05, 0.029, bone="legFLl", k=0.03, color="@leg", mirror=True), LF)
spots(S.cone("pastern", [FF[0] - 0.02, 0.1, FF[2]], [FF[0], 0.04, FF[2]], 0.029, 0.03, bone="footFL", k=0.015, color="@leg", mirror=True), LF)
S.ell("paw", [FF[0] + 0.012, 0.026, FF[2]], [0.042, 0.024, 0.034], bone="footFL", k=0.014, kc=0.01, color="@foot", mirror=True)
for j, dz in enumerate((-0.026, -0.009, 0.009, 0.026)):   # four toes, the middle two longest; blunt dark claws
    fw = 0.012 if abs(dz) < 0.01 else 0.0
    tc = [FF[0] + (0.048 + fw) * (1 - abs(dz) * 4), 0.017, FF[2] + dz * 1.0]
    S.ell(f"ftoe{j}", tc, [0.019, 0.017, 0.0125], rot=[0, -dz * 300, 0], bone="footFL", k=0.008, kc=0.004, color="@toe", mirror=True)
    S.cone(f"fclaw{j}", add(tc, [0.012, 0.004, 0]), add(tc, [0.026, -0.01, 0]), 0.0052, 0.0034, bone="footFL", k=0.0, color="@claw", mirror=True)
# ---- hind legs: shorter, crouched -- thigh to a low hock, the metatarsus sloping forward to the paw
HFR = {"o": HL, "u": [0, -1, 0], "r": 0.06}
spots(S.ell("thigh", [HL[0] + 0.0, 0.44, HL[2]], [0.11, 0.15, 0.07], rot=[0, 0, 14], bone="legHLu", k=0.05, color=B, mirror=True), HFR)
spots(S.cone("gaskin", [HL[0] + 0.02, 0.36, HL[2] - 0.004], [HK[0] - 0.04, HK[1] + 0.0, HK[2]], 0.058, 0.03, bone="legHLu", k=0.03, color="@leg", mirror=True), HFR)
spots(S.cone("hock", [HK[0] - 0.04, HK[1], HK[2]], [HF[0] - 0.01, 0.05, HF[2]], 0.03, 0.026, bone="legHLl", k=0.02, color="@leg", mirror=True), HFR)
S.ell("hpaw", [HF[0] + 0.012, 0.024, HF[2]], [0.04, 0.022, 0.031], bone="footHL", k=0.013, kc=0.01, color="@foot", mirror=True)
for j, dz in enumerate((-0.026, -0.009, 0.009, 0.026)):   # four toes, the middle two longest; blunt dark claws
    fw = 0.012 if abs(dz) < 0.01 else 0.0
    tc = [HF[0] + (0.044160000000000005 + fw) * (1 - abs(dz) * 4), 0.017, HF[2] + dz * 0.92]
    S.ell(f"htoe{j}", tc, [0.01748, 0.01564, 0.011500000000000002], rot=[0, -dz * 300, 0], bone="footHL", k=0.008, kc=0.004, color="@toe", mirror=True)
    S.cone(f"hclaw{j}", add(tc, [0.011040000000000001, 0.004, 0]), add(tc, [0.02392, -0.01, 0]), 0.0052, 0.0034, bone="footHL", k=0.0, color="@claw", mirror=True)
# ---- tail: short, from the low rump, a black bushy end
T = rig["tail"]; P = arc_pts(T, 8)
for i in range(8):
    t = (i + 0.5) / 8; ra = 0.022 + 0.006 * (i / 8) + (0.008 * max(0, (i - 4) / 4)); rb = 0.022 + 0.006 * ((i + 1) / 8) + (0.008 * max(0, (i - 3) / 4))
    S.cone(f"tail{i}", P[i] + [0], P[i + 1] + [0], ra, rb, bone="tail", k=0.4 * ra, kc=0.15 * ra, color="@tip" if i >= 4 else "@tail", hair=1)
S.cone("tailRoot", [-0.44, 0.578, 0], P[1] + [0], 0.032, 0.024, bone="tail", k=0.02, color="@tail", hair=1)   # (rooted INSIDE the rump: at the fine grid a pinch parted it)
S.ell("brush", lerp(P[5] + [0], P[8] + [0], 0.6), [0.034, 0.075, 0.03], rot=[0, 0, ang(sub(P[8] + [0], P[5] + [0])) - 90], bone="tail", k=0.03, kc=0.01, color="@tip", hair=1)
# (audit 2026-11-07) the head and throat ticked fur (coatpat.js agouti) -- the body and legs keep their spots
for q in S.shapes:
    if q.get("color") in ("@head", "@cheek", "@mask", "@throat", "@belly") and "pat" not in q and q.get("op") is None: q["pat"] = "agouti"
sc = {"keep": [], "mesh": {"tris": [6800, 2200], "cell": 0.006}, "shape": S.shapes,
      "eyes": {"at": [0.787, 0.842, round(EYE - 0.004, 4)], "from": [0.7, 0.83, 0], "r": 0.0135, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.5, "socket": 1.1},
      "shade": {"back": 0.92, "belly": 1.12, "k": 0.12, "on": B}, "patScale": 0.85}
finish(N, rig, sc)
