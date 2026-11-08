# THE OLIVE BABOON (2026-11-05): a male, written in its standing pose (sk.py)
from common import build, rig_only
from sk import Frames, ell, sph, cone, tube, lerp, add, path_tail
from rigs import RIGS
import math

N = "baboon"
rig_only(N); F = Frames(N)
S = []
H, MN, FC = "@body", "@mane", "@face"
ag = {"pat": "agouti"}
shag = {"pat": "coarse"}   # (audit 2026-11-07, round 3: the mane in COARSE strands -- the shag pattern read as camouflage blotches)

# ---- the trunk: deep in the chest, the MANE a cape over the shoulders, the loin lean, the rump high and narrow
S += [
  ell("chest", [0.12, 0.54, 0], [0.17, 0.14, 0.125], H, k=0.05, rot=[0, 0, 8], **ag),
  ell("loin", [-0.05, 0.535, 0], [0.16, 0.095, 0.1], H, k=0.05, rot=[0, 0, -3], **ag),
  ell("belly", [0.01, 0.475, 0], [0.13, 0.045, 0.075], "@belly", k=0.04, kc=0.03),
  ell("rump", [-0.21, 0.52, 0], [0.11, 0.1, 0.105], H, k=0.05, rot=[0, 0, -8], **ag),
  ell("cape", [0.2, 0.64, 0], [0.22, 0.11, 0.16], MN, k=0.05, kc=0.04, rot=[0, 0, 14], **shag),
  ell("capeS", [0.2, 0.56, 0.092], [0.15, 0.13, 0.068], MN, k=0.045, kc=0.04, rot=[0, 0, 8], mirror=True, **shag),
  ell("capeB", [0.03, 0.6, 0], [0.13, 0.05, 0.1], MN, k=0.04, kc=0.04, rot=[0, 0, 4], **shag),
  # the CALLOSITIES: bare grey pads on the buttocks, under the tail's root
  # the mane's locks, hanging off the shoulders and the neck
  *[cone(f"maneH{j}", [0.27 - j * 0.045, 0.6 - j * 0.012, 0.075 + 0.012 * (j % 2)], [0.25 - j * 0.045, 0.49 - j * 0.015, 0.095 + 0.012 * (j % 2)],
         0.035, 0.012, MN, k=0.025, kc=0.02, mirror=True, **shag) for j in range(4)],
  ell("callus", [-0.315, 0.465, 0.032], [0.028, 0.045, 0.032], "@callus", k=0.012, kc=0.006, rot=[0, 0, -10], mirror=True,
      seat={"from": [-0.2, 0.47, 0.032], "out": -0.35}),
]
# ---- the head: a dog's long muzzle, the nostrils at its very end, the eyes deep under a heavy brow, pale lids
S += [
  ell("neck", [0.34, 0.6, 0], [0.085, 0.07, 0.065], MN, k=0.04, kc=0.03, bone="neck", **shag),
  ell("ruffN", [0.34, 0.655, 0], [0.09, 0.07, 0.095], MN, k=0.04, kc=0.03, bone="neck", **shag),
  ell("cranium", [0.425, 0.68, 0], [0.07, 0.065, 0.06], H, k=0.03, bone="head", **ag),
  ell("cheekR", [0.438, 0.652, 0.054], [0.062, 0.072, 0.044], MN, k=0.028, kc=0.02, mirror=True, bone="head", **shag),
  ell("cheekM", [0.478, 0.635, 0.034], [0.04, 0.035, 0.022], H, k=0.02, kc=0.015, mirror=True, bone="head", **ag),
  # (audit 2026-11-07: a HEAVY BROW SHELF over deep-set eyes -- before, the eyes bulged out of a flat grey mask; round 2: the
  #  shelf a bar just over the eyes, the FUR of the crown brought forward over the forehead to it -- not a grey dome)
  cone("brow", [0.49, 0.703, 0.036], [0.49, 0.703, -0.036], 0.017, 0.017, "@face", k=0.012, kc=0.008, bone="head"),
  ell("browRidge", [0.496, 0.705, 0], [0.016, 0.011, 0.048], "@face", k=0.01, kc=0.006, bone="head"),
  ell("browH", [0.458, 0.722, 0], [0.048, 0.03, 0.056], H, k=0.02, kc=0.008, bone="head", **ag),
  # the MUZZLE: long and deep, flat-sided, a ridge down each side of its top, the nose pad at its very end
  cone("muzzle", [0.47, 0.662, 0], [0.622, 0.606, 0], 0.046, 0.03, "@face", k=0.024, kc=0.012, bone="head"),
  cone("ridge", [0.5, 0.69, 0.03], [0.615, 0.64, 0.022], 0.02, 0.013, "@face", k=0.004, kc=0.004, mirror=True, bone="head"),
  cone("jaw", [0.46, 0.622, 0], [0.605, 0.582, 0], 0.04, 0.023, "@face", k=0.02, kc=0.008, bone="head"),
  sph("snout", [0.625, 0.605, 0], 0.027, "@face", k=0.012, kc=0.006, bone="head"),
  ell("lip", [0.613, 0.582, 0], [0.026, 0.011, 0.024], "@lip", k=0.008, kc=0.004, bone="head"),
  ell("nosepad", [0.65, 0.611, 0], [0.006, 0.021, 0.024], "@nose", k=0.006, kc=0.004, bone="head"),
  ell("nostril", [0.6585, 0.606, 0.0095], [0.004, 0.0085, 0.0058], "@nostril", k=0.002, kc=0.0015, mirror=True, bone="head"),
  ell("mouth", [0.62, 0.589, 0], [0.012, 0.0035, 0.022], "@nostril", k=0.003, kc=0.002, bone="head"),
  ell("ear", [0.408, 0.693, 0.06], [0.016, 0.026, 0.009], FC, k=0.006, kc=0.003, mirror=True, bone="head", rot=[-20, 0, 8]),
]
# ---- the limbs: long and even, standing on the PALMS and soles, the fingers flat
sh, el, wr = F.J("legFLu"), F.J("legFLl"), F.end("legFLl")
S += [
  tube("arm", [add(sh, [0, 0.02, -0.005]) + [0.055], lerp(sh, el, 0.5) + [0.045], el + [0.038]], H, k=0.03, bone="legFLu", mirror=True, **ag),
  cone("forearm", el, add(wr, [0.005, 0.01, 0]), 0.037, 0.024, H, k=0.02, bone="legFLl", mirror=True, **ag),
]
x0, z0 = wr[0], wr[2]
S += [ell("palm", [x0 + 0.025, 0.018, z0], [0.04, 0.018, 0.031], "@hand", k=0.01, kc=0.006, bone="footFL", mirror=True),
      cone("wrist", add(wr, [0, 0.03, 0]), [x0 + 0.015, 0.02, z0], 0.024, 0.02, H, k=0.01, kc=0.008, bone="footFL", mirror=True, **ag)]
for j in range(4):
    z = z0 + (j - 1.5) * 0.0175
    S += [cone(f"fing{j}", [x0 + 0.042, 0.0095, z], [x0 + 0.08 - abs(j - 1.5) * 0.006, 0.0075, z + (j - 1.5) * 0.003], 0.0072, 0.0066, "@hand", k=0.003, kc=0.002, bone="footFL", mirror=True)]
S += [cone("thumb", [x0 + 0.025, 0.013, z0 - 0.028], [x0 + 0.048, 0.008, z0 - 0.043], 0.0072, 0.0066, "@hand", k=0.003, kc=0.002, bone="footFL", mirror=True)]
S += [ell("delt", add(sh, [0.0, 0.0, 0.01]), [0.07, 0.085, 0.055], H, k=0.03, mirror=True, **ag)]
hp, kn, an = F.J("legHLu"), F.J("legHLl"), F.end("legHLl")
d = [kn[0] - hp[0], kn[1] - hp[1]]; th = math.degrees(math.atan2(d[0], -d[1]))
S += [
  ell("thigh", lerp(hp, kn, 0.45), [0.07, 0.13, 0.065], H, k=0.035, rot=[0, 0, th], bone="legHLu", mirror=True, **ag),
  cone("shank", kn, add(an, [0.005, 0.01, 0]), 0.04, 0.025, H, k=0.02, bone="legHLl", mirror=True, **ag),
]
fx, fz = an[0], an[2]
S += [ell("sole", [fx + 0.04, 0.017, fz + 0.004], [0.065, 0.017, 0.03], "@hand", k=0.01, kc=0.006, bone="footHL", mirror=True),
      ell("heel", [fx - 0.005, 0.03, fz], [0.03, 0.03, 0.026], H, k=0.012, kc=0.01, bone="footHL", mirror=True),
      cone("ankle", add(an, [0, 0.03, 0]), [fx + 0.01, 0.022, fz], 0.025, 0.022, H, k=0.01, kc=0.008, bone="footHL", mirror=True, **ag)]
for j in range(4):
    z = fz - 0.009 + j * 0.0165
    S += [cone(f"toe{j}", [fx + 0.082, 0.0095, z], [fx + 0.115 - j * 0.004, 0.0075, z + 0.002], 0.0072, 0.0066, "@hand", k=0.003, kc=0.002, bone="footHL", mirror=True)]
S += [cone("hallux", [fx + 0.055, 0.011, fz - 0.028], [fx + 0.08, 0.008, fz - 0.045], 0.0072, 0.0066, "@hand", k=0.003, kc=0.002, bone="footHL", mirror=True)]
# ---- the tail: the "BROKEN" tail -- up and back off the rump for a third of it, then hanging straight down
P = RIGS[N]["tail"]["path"]
S += [cone("tailRoot", [-0.29, 0.5, 0], [P[0][0] + 0.01, P[0][1] - 0.005, 0], 0.04, 0.03, "@body", k=0.015, kc=0.008, bone="tail", **ag)]
S += path_tail(P, 4, lambda t: 0.03 - 0.014 * t, lambda t: {"color": "@tail" if t < 0.85 else "@tip", "pat": "agouti"})

cols = {"body": "#5d5841", "mane": "#66634d", "belly": "#8a8364", "face": "#45403d", "lip": "#4b4440", "nose": "#36302d", "nostril": "#0b0909",
        "callus": "#56504c", "hand": "#2d2926", "tail": "#57523b", "tip": "#3f3b2a", "eye": "#5a3a1c", "lid": "#57504a",
        "leg": "#5d5841", "foot": "#2d2926"}
eyes = {"at": [0.49, 0.683, 0.021], "from": [0.43, 0.683, 0.012], "r": 0.0068, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.76, "socket": 1.2}
about = ("an olive baboon SCULPTED on its rig (2026-11-05, gen: scratchpad sc/prim/gen/baboon.py, written in its standing pose): a male "
         "Old World monkey walking on its palms and soles, flat fingers and toes forward, the limbs long and even; a dog's long dark "
         "MUZZLE with the nostrils at its very end, the eyes deep under a heavy brow, pale upper lids, small ears; olive ticked fur "
         "(agouti) and the male's MANE a cape over the shoulders and neck (shag); bare grey callosities on the buttocks under the "
         "BROKEN tail -- carried up and back off the rump for a third of its length, then hanging straight down")
# (audit 2026-11-07) COATS: the baboons of Africa -- the olive (as written), the YELLOW (slighter, sandy yellow, a pale belly
# and cheeks), the CHACMA (the largest, dark grey-brown, a near-black face) and the HAMADRYAS male (a silver-grey cape over
# a brown-grey body, a pink face)
coats = [{"name": "olive"},
         {"name": "yellow", "scale": 0.92, "body": "#9a8452", "mane": "#a48e5c", "belly": "#c8b88e", "tail": "#927c4c", "tip": "#5e5034",
          "leg": "#9a8452", "face": "#3e3834", "lip": "#4a4440"},
         {"name": "chacma", "scale": 1.08, "body": "#4a4436", "mane": "#4e483a", "belly": "#6a6250", "tail": "#463f32", "tip": "#2a2620",
          "leg": "#4a4436", "face": "#262222", "lip": "#2e2a28", "nose": "#1e1a18", "hand": "#1e1b19", "foot": "#1e1b19"},
         {"name": "hamadryas", "body": "#6e685e", "mane": "#9c978c", "belly": "#857f74", "tail": "#6e685e", "tip": "#56504a",
          "leg": "#6e685e", "face": "#c0827a", "lip": "#b07068", "nose": "#a8665e", "callus": "#c87a72", "lid": "#b88078"}]
build(N, about, cols, S, extra={"coats": coats}, eyes=eyes, mesh={"cell": 0.008, "tris": [7000, 2300], "focus": {"head": 5, "footFL": 3, "footFR": 3, "footHL": 3, "footHR": 3}})
print("saved", N, len(S), "shapes")
