# THE RED KANGAROO (2026-11-05), written in its standing pose (sk.py: the hind legs folded as the IK folds them)
from common import build, rig_only
from sk import Frames, ell, sph, cone, tube, lerp, add, path_tail
from rigs import RIGS
import math

N = "kangaroo"
rig_only(N); F = Frames(N)
S = []
H = "@body"
ag = {"pat": "agouti"}

# ---- the trunk: a PEAR tipped up -- the weight low in the haunches and the tail's root, the chest narrow and high
S += [
  ell("haunch", [-0.1, 0.5, 0], [0.2, 0.19, 0.17], H, k=0.06, rot=[0, 0, -20], **ag),
  ell("torso", [0.06, 0.68, 0], [0.12, 0.25, 0.115], H, k=0.06, rot=[0, 0, -38], **ag),
  ell("belly", [0.13, 0.66, 0], [0.07, 0.24, 0.085], "@belly", k=0.04, kc=0.045, rot=[0, 0, -34]),
  ell("chest", [0.19, 0.92, 0], [0.105, 0.135, 0.1], H, k=0.05, rot=[0, 0, -30], **ag),
  ell("bib", [0.25, 0.86, 0], [0.045, 0.11, 0.06], "@belly", k=0.03, kc=0.045, rot=[0, 0, -30]),
]
# ---- the neck and the head: a deer's -- long-muzzled, the big dark nose pad, the pale MALAR stripe; tall ears
S += [
  cone("neck", [0.22, 0.94, 0], [0.34, 1.14, 0], 0.1, 0.07, H, k=0.05, bone="neck", **ag),
  ell("throat", [0.29, 1.02, 0], [0.05, 0.09, 0.05], "@belly", k=0.03, kc=0.045, rot=[0, 0, -32], bone="neck"),
  ell("cranium", [0.365, 1.178, 0], [0.062, 0.056, 0.052], H, k=0.025, bone="head", **ag),
  # the muzzle SHORT and blunt, deep, the broad dark nose pad on its end
  cone("muzzle", [0.39, 1.165, 0], [0.495, 1.128, 0], 0.047, 0.034, "@muzzle", k=0.022, kc=0.01, bone="head"),
  cone("jaw", [0.385, 1.135, 0], [0.48, 1.105, 0], 0.032, 0.021, "@muzzle", k=0.016, kc=0.008, bone="head"),
  ell("nosepad", [0.527, 1.13, 0], [0.011, 0.025, 0.03], "@nose", k=0.007, kc=0.004, bone="head", wet=0.1),
  ell("malar", [0.44, 1.14, 0.034], [0.035, 0.007, 0.009], "@malar", k=0.005, kc=0.003, rot=[0, 0, -15], mirror=True, bone="head",
      seat={"from": [0.44, 1.145, 0.0], "out": -0.4}),
  ell("lip", [0.485, 1.106, 0], [0.016, 0.008, 0.018], "@lip", k=0.006, kc=0.003, bone="head"),
]
# the ears: tall, furred LOBES (thick enough for the field), a pale hollow down their fronts, seated in the crown
S += [ell("ear", [0.318, 1.3, 0.045], [0.011, 0.074, 0.03], "@ear", k=0.008, kc=0.004, rot=[10, 0, 12], mirror=True, bone="earL"),
      ell("earIn", [0.325, 1.3, 0.045], [0.004, 0.06, 0.02], "@earIn", k=0.003, kc=0.002, rot=[10, 0, 12], mirror=True, bone="earL"),
      sph("earB", [0.335, 1.232, 0.034], 0.02, "@body", k=0.01, kc=0.006, mirror=True, bone="earL", pat="agouti")]
# ---- the arms: SHORT, held in front of the chest, black-clawed paws
a0, a1 = [0.285, 0.875, 0.075], [0.38, 0.69, 0.08]
el = [0.33, 0.77, 0.088]
S += [
  cone("uarm", a0, el, 0.034, 0.024, H, k=0.018, bone="armL", mirror=True, **ag),
  cone("farm", el, a1, 0.024, 0.017, H, k=0.012, bone="armL", mirror=True, **ag),
  ell("paw", add(a1, [0.008, -0.014, 0]), [0.022, 0.02, 0.022], "@paw", k=0.007, kc=0.004, bone="armL", mirror=True),
]
# the five short digits, a black claw curving out of each
for j in range(5):
    z = a1[2] + (j - 2) * 0.0095
    b0 = [a1[0] + 0.014, a1[1] - 0.024, z]; b1 = [a1[0] + 0.022, a1[1] - 0.036 + abs(j - 2) * 0.003, z]
    S += [cone(f"pdig{j}", b0, b1, 0.0088, 0.0086, "@paw", k=0.003, kc=0.002, bone="armL", mirror=True),
          cone(f"pclaw{j}", [b1[0] + 0.002, b1[1] - 0.004, z], [b1[0] + 0.012, b1[1] - 0.016, z], 0.0042, 0.001, "@claw", k=0.0015, kc=0.001, bone="armL", mirror=True)]
# ---- the hind legs: the THIGH massive, the shank long and slender, the FOOT longer still -- flat on the ground
hp, kn, an = F.J("legHLu"), F.J("legHLl"), F.end("legHLl")
d = [kn[0] - hp[0], kn[1] - hp[1]]; th = math.degrees(math.atan2(d[0], -d[1]))
S += [
  ell("thigh", lerp(hp, kn, 0.42), [0.15, 0.19, 0.125], H, k=0.06, rot=[0, 0, th], bone="legHLu", mirror=True, **ag),
  cone("knee", lerp(hp, kn, 0.7), kn, 0.085, 0.055, H, k=0.035, bone="legHLu", mirror=True, **ag),
  cone("shank", kn, add(an, [0.0, 0.0, 0]), 0.048, 0.028, H, k=0.02, bone="legHLl", mirror=True, **ag),
]
fx, fz = an[0], an[2]
S += [
  ell("heel", [fx - 0.005, 0.032, fz], [0.035, 0.03, 0.03], H, k=0.012, kc=0.01, bone="footHL", mirror=True),
  ell("foot", [fx + 0.12, 0.03, fz + 0.006], [0.14, 0.03, 0.04], "@foot", k=0.012, kc=0.008, bone="footHL", mirror=True),
  cone("toe4", [fx + 0.22, 0.026, fz + 0.002], [fx + 0.33, 0.018, fz + 0.004], 0.025, 0.017, "@foot", k=0.006, kc=0.004, bone="footHL", mirror=True),
  ell("pad4", [fx + 0.3, 0.011, fz + 0.004], [0.03, 0.009, 0.014], "@paw", k=0.004, kc=0.003, bone="footHL", mirror=True),
  cone("toe5", [fx + 0.17, 0.02, fz + 0.03], [fx + 0.25, 0.015, fz + 0.04], 0.0145, 0.011, "@foot", k=0.004, kc=0.003, bone="footHL", mirror=True),
  cone("claw4", [fx + 0.328, 0.019, fz + 0.004], [fx + 0.38, 0.006, fz + 0.004], 0.013, 0.003, "@claw", k=0.003, kc=0.002, bone="footHL", mirror=True),
]
# ---- the TAIL: thick at its root (a third leg to lean on), tapering, the end along the ground
P = RIGS[N]["tail"]["path"]
S += path_tail(P, 5, lambda t: 0.1 - 0.072 * t ** 0.7, lambda t: {"color": "@tail" if t < 0.88 else "@tip", "pat": "agouti"})

cols = {"body": "#a65530", "belly": "#cdb497", "muzzle": "#8f4b2e", "malar": "#e6dccd", "nose": "#1c1614", "lip": "#e0d4c4",
        "ear": "#a0502e", "earIn": "#c9ab90", "paw": "#2c201a", "claw": "#16110e", "foot": "#94492a", "tail": "#a3532f",
        "tip": "#5b2f1c", "eye": "#2b1a10", "lid": "#1a120e", "leg": "#a65530"}
eyes = {"at": [0.413, 1.193, 0.041], "from": [0.37, 1.188, 0.0], "r": 0.0115, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.62, "socket": 1.2}
about = ("a red kangaroo SCULPTED on its rig (2026-11-05, gen: scratchpad sc/prim/gen/kangaroo.py, written in its standing pose): a "
         "male, some 1.5 m standing, rust-red (agouti) over a pale belly; a pear tipped up -- the weight low in massive haunches, the "
         "chest narrow; short arms held in front, black-clawed; the hind legs folded as the IK folds them -- the thigh forward, a long "
         "slender shank back to the heel, and a FOOT longer still flat on the ground, its great fourth toe clawed; a deer's head "
         "with a long muzzle, a big dark nose pad, a pale malar stripe, side-set eyes and tall ears; the thick tail on the ground "
         "behind. It HOPS (hop.sync: index.html hopStep): both feet together, the stride locked to the bound")
# (audit 2026-11-07) COATS, picked by seed: the red kangaroo (twice), a blue-grey red-kangaroo doe ("blue flier", smaller), an
# EASTERN GREY -- grey-brown, a paler belly, the tail tipped dark
coats = [{"name": "red"}, {"name": "red"},
         {"name": "blue flier", "scale": 0.85, "body": "#8a8a8c", "leg": "#8a8a8c", "ear": "#848486", "foot": "#7e7e80", "tail": "#868688",
          "muzzle": "#76767a", "belly": "#d6d2cc", "tip": "#4a4a4e", "earIn": "#c4c0ba"},
         {"name": "eastern grey", "scale": 0.95, "body": "#857a6e", "leg": "#857a6e", "ear": "#7a6e62", "foot": "#6e6358", "tail": "#7e7468",
          "muzzle": "#6e645a", "belly": "#d9d2c6", "tip": "#2a2420", "earIn": "#c2b4a4", "malar": "#d8d0c4"}]
build(N, about, cols, S, eyes=eyes, extra={"coats": coats}, mesh={"cell": 0.0105, "tris": [7000, 2300], "focus": {"head": 5, "armL": 2.5, "armR": 2.5, "footHL": 2, "footHR": 2}})
print("saved", N, len(S), "shapes")
