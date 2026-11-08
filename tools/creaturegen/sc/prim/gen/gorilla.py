# THE SILVERBACK (2026-11-05), written in its STANDING pose (sk.py carries each shape back to its bone's rest frame)
from common import build, rig_only
from sk import Frames, ell, sph, cone, tube, tri, lerp, add
import math

N = "gorilla"
rig_only(N); F = Frames(N)
S = []
H, SH, SI, SK, FC = "@body", "@shag", "@silver", "@skin", "@face"
shag = {"pat": "shag"}
ag = {"pat": "agouti"}

# ---- the trunk: a barrel of a chest under a hump of shoulder, the back falling from it to a narrow rump
S += [
  ell("chest", [0.15, 1.0, 0], [0.31, 0.3, 0.29], H, k=0.09, rot=[0, 0, 14], **shag),
  ell("hump", [0.2, 1.22, 0], [0.27, 0.16, 0.27], H, k=0.08, rot=[0, 0, 10], **shag),
  ell("delt", [0.3, 1.08, 0.26], [0.16, 0.19, 0.14], H, k=0.06, mirror=True, **shag),
  ell("pec", [0.41, 0.97, 0.1], [0.08, 0.13, 0.105], "@chest", k=0.045, kc=0.02, rot=[0, 0, -12], mirror=True, wet=0.12),
  ell("belly", [-0.02, 0.82, 0], [0.25, 0.22, 0.26], H, k=0.08, **shag),
  ell("loin", [-0.13, 0.93, 0], [0.24, 0.15, 0.2], SI, k=0.07, kc=0.09, rot=[0, 0, 20], **shag),
  ell("rump", [-0.29, 0.74, 0], [0.16, 0.16, 0.19], SI, k=0.07, kc=0.09, rot=[0, 0, 22], **shag),
  # the SADDLE: short silver hair from behind the shoulders over the loin and the rump
  # (small patches SEATED on the back's own surface, one after another down its slope: a long shell was a fin where the back fell away)
  *[ell(f"saddle{j}", [x, 1.2, 0], [0.12, 0.05, 0.17], SI, k=0.06, kc=0.08, rot=[0, 0, 18 + 8 * j], seat={"from": [x, 0.85, 0], "out": -0.24}, **shag)
    for j, x in enumerate([0.03, -0.07, -0.17])],
  ell("saddleR", [-0.27, 0.88, 0], [0.1, 0.05, 0.15], SI, k=0.05, kc=0.08, rot=[0, 0, 40], seat={"from": [-0.15, 0.72, 0], "out": -0.27}, **shag),
]
# ---- the head: low between the shoulders, a domed crown rising to the crest, the heavy brow, a bare black face
S += [
  ell("neck", [0.46, 1.13, 0], [0.15, 0.15, 0.17], H, k=0.07, bone="neck"),
  ell("cranium", [0.6, 1.19, 0], [0.13, 0.13, 0.125], H, k=0.05, bone="head"),
  ell("crest", [0.56, 1.31, 0], [0.13, 0.065, 0.05], "@crown", k=0.05, kc=0.03, rot=[0, 0, -22], bone="head"),
  ell("occiput", [0.5, 1.24, 0], [0.1, 0.1, 0.12], H, k=0.05, bone="head"),
  ell("cheek", [0.645, 1.12, 0.085], [0.07, 0.09, 0.05], H, k=0.035, mirror=True, bone="head"),
  ell("jaw", [0.67, 1.03, 0], [0.09, 0.07, 0.1], H, k=0.04, bone="head"),
  ell("face", [0.685, 1.14, 0], [0.07, 0.09, 0.09], FC, k=0.03, kc=0.012, bone="head"),
  cone("brow", [0.72, 1.218, 0.074], [0.72, 1.218, -0.074], 0.035, 0.035, FC, k=0.018, kc=0.008, bone="head"),
  sph("browC", [0.737, 1.224, 0], 0.033, FC, k=0.014, kc=0.007, bone="head"),
  ell("muzzle", [0.73, 1.07, 0], [0.065, 0.06, 0.085], FC, k=0.03, kc=0.01, bone="head"),
  cone("bridge", [0.745, 1.19, 0], [0.772, 1.13, 0], 0.018, 0.022, "@nose", k=0.012, kc=0.006, bone="head"),
  ell("nose", [0.772, 1.118, 0], [0.022, 0.026, 0.05], "@nose", k=0.012, kc=0.006, bone="head", wet=0.04),
  ell("ala", [0.78, 1.102, 0.036], [0.022, 0.024, 0.022], "@nose", k=0.008, kc=0.004, mirror=True, bone="head", wet=0.04),
  ell("nostril", [0.797, 1.098, 0.023], [0.0095, 0.013, 0.016], "@nostril", k=0.003, kc=0.002, rot=[0, 0, -30], mirror=True, bone="head"),
  ell("lip", [0.785, 1.06, 0], [0.024, 0.022, 0.062], "@lip", k=0.012, kc=0.006, bone="head"),
  ell("chin", [0.765, 1.015, 0], [0.032, 0.026, 0.056], "@lip", k=0.012, kc=0.006, bone="head"),
  ell("ear", [0.578, 1.19, 0.118], [0.024, 0.033, 0.013], FC, k=0.01, kc=0.005, mirror=True, bone="head"),
]
# ---- the arms: long, massive, straight, hairy to the wrist
sh, el, wr = F.J("legFLu"), F.J("legFLl"), F.end("legFLl")
S += [
  tube("arm", [add(sh, [0, 0.03, -0.01]) + [0.15], lerp(sh, el, 0.5) + [0.13], add(el, [0, 0, 0]) + [0.11]], H, k=0.05, bone="legFLu", mirror=True, **shag),
  cone("forearm", el, add(wr, [0.005, 0.02, 0]), 0.112, 0.08, H, k=0.04, bone="legFLl", mirror=True, **shag),
]
# ---- the hands: KNUCKLE-WALKING -- the fingers curled under, their middle joints' backs (bare pads) on the ground
x0, z0 = wr[0], wr[2]
S += [
  ell("handB", [x0 + 0.04, 0.11, z0], [0.08, 0.055, 0.08], H, k=0.03, bone="footFL", mirror=True),
]
for j in range(4):
    z = z0 + (j - 1.5) * 0.042 + 0.01
    xk = x0 + 0.115 - abs(j - 1.6) * 0.012
    S += [
      cone(f"fing{j}a", [xk - 0.05, 0.1, z], [xk, 0.044, z], 0.021, 0.019, SK, k=0.006, kc=0.003, bone="footFL", mirror=True),
      cone(f"fing{j}b", [xk + 0.002, 0.03, z], [xk - 0.042, 0.024, z], 0.019, 0.017, "@pad", k=0.005, kc=0.003, bone="footFL", mirror=True),
      sph(f"knk{j}", [xk + 0.004, 0.04, z], 0.021, "@pad", k=0.004, kc=0.002, bone="footFL", mirror=True),
    ]
S += [cone("thumb", [x0 + 0.02, 0.09, z0 - 0.065], [x0 + 0.07, 0.04, z0 - 0.08], 0.022, 0.017, SK, k=0.008, kc=0.004, bone="footFL", mirror=True)]
# ---- the legs: short and bowed, the thigh thick, the foot an ape's -- a long sole, short toes, the great toe apart
hp, kn, an = F.J("legHLu"), F.J("legHLl"), F.end("legHLl")
d = [kn[0] - hp[0], kn[1] - hp[1]]; th = math.degrees(math.atan2(d[0], -d[1]))
S += [
  ell("thigh", lerp(hp, kn, 0.45), [0.12, 0.17, 0.125], H, k=0.05, rot=[0, 0, th], bone="legHLu", mirror=True, **shag),
  cone("shank", kn, add(an, [0.01, 0.01, 0]), 0.085, 0.068, H, k=0.035, bone="legHLl", mirror=True, **shag),
]
fx, fz = an[0], an[2]
S += [
  ell("heel", [fx - 0.025, 0.06, fz], [0.06, 0.055, 0.055], SK, k=0.02, kc=0.01, bone="footHL", mirror=True),
  ell("sole", [fx + 0.035, 0.045, fz + 0.005], [0.105, 0.042, 0.065], SK, k=0.02, kc=0.01, bone="footHL", mirror=True),
  ell("instep", [fx + 0.03, 0.08, fz], [0.08, 0.045, 0.06], H, k=0.025, kc=0.02, bone="footHL", mirror=True),
  cone("hallux", [fx + 0.06, 0.04, fz - 0.055], [fx + 0.13, 0.028, fz - 0.09], 0.02, 0.017, SK, k=0.006, kc=0.003, bone="footHL", mirror=True),
]
for j in range(4):
    z = fz - 0.018 + j * 0.025
    S += [cone(f"toe{j}", [fx + 0.115, 0.032, z], [fx + 0.185 - j * 0.007, 0.018, z + 0.005], 0.0158, 0.0128, SK, k=0.004, kc=0.002, bone="footHL", mirror=True)]

cols = {"body": "#222121", "shag": "#222121", "silver": "#5f5b56", "skin": "#2a2624", "face": "#262220", "chest": "#252221",
        "crown": "#33281f", "nose": "#1e1b1a", "nostril": "#0d0b0a", "lip": "#24201e", "pad": "#34302c", "eye": "#3a2415",
        "lid": "#0d0c0b", "leg": "#1d1b1a", "foot": "#141212", "tail": "#1d1b1a"}
eyes = {"at": [0.745, 1.172, 0.04], "from": [0.64, 1.172, 0.026], "r": 0.0125, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.64, "socket": 1.2}
about = ("a silverback mountain gorilla SCULPTED on its rig (2026-11-05, gen: scratchpad sc/prim/gen/gorilla.py, written in its standing "
         "pose): the game's first ape. Massive -- a barrel chest under a hump of shoulder, the back falling to a narrow rump; arms longer "
         "than its legs, KNUCKLE-WALKING on fingers curled under (bare pads on the ground), short bowed legs on an ape's foot with the "
         "great toe set apart; the head low between the shoulders, a domed crown rising to the sagittal crest (a rust tinge on it), a "
         "heavy brow over small dark forward-facing eyes, a bare black face, broad nostrils, small ears in the hair; black hair "
         "(shag: long locks on the arms, the chest's skin bare) and the SILVER SADDLE of an old male over the back and rump")
# (audit 2026-11-07) VARIANTS by name: a FEMALE (or a young blackback), about four-fifths his height, all black -- no silver saddle
variants = {"female": {"scale": 0.8, "colors": {"silver": "#262423", "crown": "#2a2420"}}}
build(N, about, cols, S, eyes=eyes, extra={"variants": variants}, mesh={"tris": [8400, 2800], "focus": {"head": 5, "footFL": 3, "footFR": 3, "footHL": 2.5, "footHR": 2.5}})
print("saved", N, len(S), "shapes")
