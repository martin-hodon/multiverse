# THE RING-TAILED LEMUR (2026-11-05), written in its standing pose (sk.py)
from common import build, rig_only
from sk import Frames, ell, sph, cone, tube, lerp, add, path_tail
from lib import cup_ear
from rigs import RIGS
import math

N = "lemur"
rig_only(N); F = Frames(N)
S = []
H = "@body"
fur = {"pat": "agouti"}

# ---- the trunk: slim, the back grey-brown, the belly and chest white; the hind legs longer, the rump the higher
S += [
  ell("chest", [0.06, 0.192, 0], [0.072, 0.058, 0.048], H, k=0.024, rot=[0, 0, -8], **fur),
  ell("loin", [-0.025, 0.225, 0], [0.075, 0.052, 0.048], H, k=0.024, rot=[0, 0, -16], **fur),
  ell("rump", [-0.09, 0.25, 0], [0.06, 0.058, 0.055], H, k=0.024, rot=[0, 0, -14], **fur),
  ell("belly", [0.005, 0.18, 0], [0.085, 0.024, 0.035], "@belly", k=0.016, kc=0.012, rot=[0, 0, -14]),
  ell("brisket", [0.11, 0.175, 0], [0.035, 0.035, 0.032], "@belly", k=0.016, kc=0.012),
  ell("neck", [0.16, 0.22, 0], [0.045, 0.033, 0.031], H, k=0.02, bone="neck", **fur),
  ell("throat", [0.175, 0.205, 0], [0.03, 0.022, 0.024], "@belly", k=0.014, kc=0.01, bone="neck"),
]
# ---- the head: a fox's face -- WHITE, a black triangle round each eye, a black snout; the crown dark grey
S += [
  ell("cranium", [0.212, 0.25, 0], [0.036, 0.032, 0.031], "@face", k=0.016, kc=0.008, bone="head"),
  ell("cap", [0.2, 0.276, 0], [0.034, 0.011, 0.027], "@cap", k=0.006, kc=0.004, bone="head"),
  ell("cheek", [0.222, 0.238, 0.02], [0.024, 0.02, 0.014], "@face", k=0.01, kc=0.006, mirror=True, bone="head"),
  # a fox's SHORT muzzle, WHITE over the bridge, only its end black
  cone("muzzle", [0.235, 0.241, 0], [0.262, 0.232, 0], 0.018, 0.0085, "@face", k=0.01, kc=0.004, bone="head"),
  cone("jaw", [0.232, 0.229, 0], [0.262, 0.223, 0], 0.013, 0.007, "@face", k=0.008, kc=0.004, bone="head"),
  ell("snoutTip", [0.264, 0.2295, 0], [0.012, 0.0105, 0.0095], "@mask", k=0.0025, kc=0.001, bone="head"),
  ell("nose", [0.274, 0.231, 0], [0.004, 0.006, 0.007], "@nose", k=0.003, kc=0.0015, bone="head", wet=0.1),
  # the black TRIANGLE round each eye, its point down toward the snout
  ell("mask", [0.245, 0.2535, 0.0175], [0.019, 0.0165, 0.0115], "@mask", k=0.004, kc=0.0015, rot=[0, -35, -30], mirror=True, bone="head",
      seat={"from": [0.215, 0.255, 0.007], "out": -0.5}),
  ell("maskP", [0.252, 0.242, 0.012], [0.011, 0.007, 0.0075], "@mask", k=0.003, kc=0.0015, rot=[0, -30, -40], mirror=True, bone="head",
      seat={"from": [0.22, 0.242, 0.004], "out": -0.8}),
]
# the ears: furred, pointed, white -- a flattened lobe each, seated in the crown, a darker hollow in its front
S += [ell("ear", [0.196, 0.291, 0.031], [0.0055, 0.022, 0.012], "@ear", k=0.005, kc=0.003, rot=[24, 0, 14], mirror=True, bone="earL"),
      ell("earIn", [0.2, 0.292, 0.031], [0.0025, 0.015, 0.0075], "@earIn", k=0.002, kc=0.0015, rot=[24, 0, 14], mirror=True, bone="earL"),
      sph("earB", [0.201, 0.276, 0.024], 0.01, "@face", k=0.006, kc=0.004, mirror=True, bone="earL")]
# ---- the limbs: slender, grey; long-fingered dark hands and feet, the great toe apart
sh, el, wr = F.J("legFLu"), F.J("legFLl"), F.end("legFLl")
S += [
  tube("arm", [add(sh, [0, 0.008, 0]) + [0.025], lerp(sh, el, 0.45) + [0.0205], el + [0.0165]], H, k=0.01, bone="legFLu", mirror=True, **fur),
  cone("forearm", el, add(wr, [0.002, 0.003, 0]), 0.0155, 0.0105, H, k=0.007, bone="legFLl", mirror=True, **fur),
]
x0, z0 = wr[0], wr[2]
S += [ell("palm", [x0 + 0.012, 0.0085, z0], [0.017, 0.008, 0.0145], "@hand", k=0.004, kc=0.002, bone="footFL", mirror=True),
      cone("wrist", add(wr, [0, 0.012, 0]), [x0 + 0.008, 0.008, z0], 0.009, 0.008, "@hand", k=0.004, kc=0.003, bone="footFL", mirror=True)]
for j in range(4):
    z = z0 + (j - 1.5) * 0.0088
    S += [cone(f"fing{j}", [x0 + 0.016, 0.0042, z], [x0 + 0.034 - abs(j - 1.5) * 0.003, 0.0034, z + (j - 1.5) * 0.002], 0.0035, 0.0034, "@digit", k=0.0012, kc=0.0008, bone="footFL", mirror=True)]
S += [cone("thumb", [x0 + 0.008, 0.0055, z0 - 0.012], [x0 + 0.02, 0.0042, z0 - 0.02], 0.0035, 0.0033, "@digit", k=0.0012, kc=0.0008, bone="footFL", mirror=True)]
hp, kn, an = F.J("legHLu"), F.J("legHLl"), F.end("legHLl")
d = [kn[0] - hp[0], kn[1] - hp[1]]; th = math.degrees(math.atan2(d[0], -d[1]))
S += [
  ell("thigh", lerp(hp, kn, 0.42), [0.043, 0.066, 0.035], H, k=0.012, rot=[0, 0, th], bone="legHLu", mirror=True, **fur),
  cone("shank", kn, add(an, [0.002, 0.004, 0]), 0.02, 0.0115, H, k=0.007, bone="legHLl", mirror=True, **fur),
  # the CALF: the muscle behind the upper shank (a leaper's hind leg is muscular, not a stick)
  ell("calf", add(lerp(kn, an, 0.3), [-0.006, 0, 0]), [0.018, 0.034, 0.018], H, k=0.01, rot=[0, 0, math.degrees(math.atan2(an[0] - kn[0], -(an[1] - kn[1])))], bone="legHLl", mirror=True, **fur),
]
fx, fz = an[0], an[2]
S += [ell("sole", [fx + 0.018, 0.0085, fz + 0.002], [0.027, 0.008, 0.0145], "@hand", k=0.004, kc=0.002, bone="footHL", mirror=True),
      cone("ankle", add(an, [0, 0.012, 0]), [fx + 0.006, 0.008, fz], 0.01, 0.008, H, k=0.004, kc=0.003, bone="footHL", mirror=True)]
for j in range(4):
    z = fz + 0.002 + (j - 1.5) * 0.0085
    S += [cone(f"toe{j}", [fx + 0.032, 0.0048, z], [fx + 0.049 - j * 0.002, 0.0044, z], 0.0036 + 0.0004 * (j == 3), 0.0035 + 0.0006 * (j == 3), "@digit", k=0.0012, kc=0.0008, bone="footHL", mirror=True)]
S += [cone("hallux", [fx + 0.014, 0.006, fz - 0.009], [fx + 0.03, 0.0042, fz - 0.02], 0.0035, 0.0034, "@digit", k=0.0012, kc=0.0008, bone="footHL", mirror=True)]
# ---- the TAIL: longer than the body, carried up in an arc, THIRTEEN black rings on white and a black tip
P = RIGS[N]["tail"]["path"]
NR = 27   # bands: white, black, ... ending black
# one cone a BAND, re-cut along the tail by arc length (so the 27 bands are even), each band's paint its own: their
# colours barely blended -- the rings' edges crisp
import sk
def resample(P, n):
    pts = [sk.tail_point(P, i / (n * 40)) for i in range(n * 40 + 1)]
    L = [0]
    for i in range(1, len(pts)): L.append(L[-1] + math.dist(pts[i], pts[i - 1]))
    out = []
    for b in range(n + 1):
        target = L[-1] * b / n
        k = next(i for i in range(len(L)) if L[i] >= target - 1e-9)
        out.append((pts[k], k / (n * 40)))
    return out
cuts = resample(P, NR)
S2 = []
m = len(P) - 2
for b in range(NR):
    (a, ga), (c, gc) = cuts[b], cuts[b + 1]
    g = (ga + gc) / 2; i = min(m - 1, int(g * m)); bone = "tail" if i == 0 else f"tail{i}"
    ra = 0.021 - 0.003 * ga + 0.002 * math.sin(math.pi * min(1, ga * 1.6)); rb = 0.021 - 0.003 * gc + 0.002 * math.sin(math.pi * min(1, gc * 1.6))
    S2.append({"id": f"ring{b}", "type": "cone", "bone": bone, "a": [a[0], a[1], 0], "b": [c[0], c[1], 0], "ra": ra, "rb": rb, "k": 0.007, "kc": 0.0008,
               "color": "@ringB" if b % 2 else "@ringW", "hair": 1})
S2.append({"id": "tailTip", "type": "sphere", "bone": "tail3", "c": [cuts[-1][0][0], cuts[-1][0][1], 0], "r": 0.019, "k": 0.007, "kc": 0.001, "color": "@ringB", "hair": 1})
S += S2
S += [cone("tailRoot", [-0.16, 0.222, 0], [P[0][0] + 0.01, P[0][1] - 0.002, 0], 0.03, 0.021, "@body", k=0.012, kc=0.006, bone="tail", **fur)]

cols = {"body": "#857a70", "belly": "#ece8e1", "face": "#efece6", "cap": "#4f4c4a", "mask": "#161414", "nose": "#0e0c0c",
        "ear": "#e9e5de", "earIn": "#b9b0a8", "hand": "#2a2725", "digit": "#3d3835", "ringW": "#ebe8e2", "ringB": "#1b1a19", "eye": "#e08418",
        "lid": "#141212", "leg": "#857a70", "foot": "#2a2725", "tail": "#ebe8e2"}
eyes = {"at": [0.248, 0.255, 0.0165], "from": [0.215, 0.255, 0.007], "r": 0.0058, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.75, "socket": 1.25, "color": "#3a2408"}
about = ("a ring-tailed lemur SCULPTED on its rig (2026-11-05, gen: scratchpad sc/prim/gen/lemur.py, written in its standing pose): "
         "a slim primate on all fours, the hind legs the longer; grey-brown back and limbs (agouti), white belly and chest; a fox's "
         "WHITE face, a black triangle round each forward-set ORANGE eye, a black snout, a dark grey cap, white pointed ears; dark "
         "long-fingered hands and feet; and THE TAIL, longer than its body and carried up in an arc: thirteen black rings on white "
         "and a black tip, one band a cone, crisp-edged")
build(N, about, cols, S, eyes=eyes, mesh={"cell": 0.0038, "tris": [7950, 2600], "focus": {"body": 1.6, "tail": 1.6, "head": 6, "footFL": 4.5, "footFR": 4.5, "footHL": 4.5, "footHR": 4.5, "legFLu": 2.8, "legFRu": 2.8, "legFLl": 2.8, "legFRl": 2.8, "legHLu": 2.8, "legHRu": 2.8, "legHLl": 2.8, "legHRl": 2.8}})
print("saved", N, len(S), "shapes")
