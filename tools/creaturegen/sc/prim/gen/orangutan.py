# THE ORANGUTAN (2026-11-05): a flanged Bornean male, written in its standing pose (sk.py)
from common import build, rig_only
from sk import Frames, ell, sph, cone, tube, lerp, add
import math

N = "orangutan"
rig_only(N); F = Frames(N)
S = []
H, SK, FC = "@body", "@skin", "@face"
shag = {"pat": "shag"}

def hank(id, top, drop, back, r0, bone, z=0.0, col=H):
    """a lock of the long coat HANGING from `top`: down `drop`, back `back`, tapering to a tip"""
    return cone(id, top, [top[0] - back, top[1] - drop, top[2] + z], r0, r0 * 0.62, col, k=r0 * 0.9, kc=r0 * 0.6, bone=bone, mirror=top[2] > 0.01, **shag)

# ---- the trunk: a pear -- narrow shoulders over a great pot belly, the rump small
S += [
  ell("chest", [0.1, 0.78, 0], [0.22, 0.21, 0.23], H, k=0.07, rot=[0, 0, 16], **shag),
  ell("shoulders", [0.2, 0.9, 0], [0.13, 0.1, 0.25], H, k=0.06, **shag),
  ell("belly", [-0.03, 0.61, 0], [0.22, 0.19, 0.22], H, k=0.07, rot=[0, 0, 8], **shag),
  ell("rump", [-0.19, 0.56, 0], [0.12, 0.13, 0.155], H, k=0.06, rot=[0, 0, 14], **shag),
]
# the long coat hanging off the flanks and belly, in a fringe
for j in range(8):
    x = 0.17 - j * 0.045; y = 0.6 - 0.12 * math.sin(math.pi * (j + 0.5) / 8); z = 0.19 - 0.03 * abs(j - 3.5) / 3.5
    S += [hank(f"flank{j}", [x, y, z], 0.12 + 0.03 * (j % 2), 0.035, 0.05, "body", z=0.012)]
for j in range(4):
    S += [hank(f"under{j}", [0.12 - j * 0.07, 0.48 + 0.02 * abs(j - 1.5), 0.085], 0.1 + 0.02 * (j % 2), 0.03, 0.05, "body", z=0.005)]
# ---- the head: the FLANGES -- a broad disc of cheek pad either side of a small flat face -- and the throat sac
S += [
  ell("neck", [0.39, 0.925, 0], [0.12, 0.12, 0.14], H, k=0.05, bone="neck", **shag),
  ell("cranium", [0.48, 0.93, 0], [0.09, 0.085, 0.085], H, k=0.04, bone="head", **shag),
  ell("crown", [0.46, 0.99, 0], [0.07, 0.04, 0.06], H, k=0.03, bone="head", **shag),
  ell("face", [0.532, 0.885, 0], [0.05, 0.07, 0.058], FC, k=0.025, kc=0.01, bone="head"),
  # the FLANGES: fleshy half-moon pads of the face's own skin framing it, curving forward at their rims
  ell("flange0", [0.5508, 0.9569, 0.0347], [0.03, 0.036, 0.02], "@flange", k=0.011, kc=0.008, rot=[-62.0, -28, 0], mirror=True, bone="head"),
  ell("flange1", [0.5534, 0.9210, 0.0671], [0.03, 0.036, 0.02], "@flange", k=0.011, kc=0.008, rot=[-25.0, -28, 0], mirror=True, bone="head"),
  ell("flange2", [0.5539, 0.8745, 0.0729], [0.03, 0.036, 0.02], "@flange", k=0.011, kc=0.008, rot=[10.0, -28, 0], mirror=True, bone="head"),
  ell("flange3", [0.5522, 0.8328, 0.0523], [0.03, 0.036, 0.02], "@flange", k=0.011, kc=0.008, rot=[45.0, -28, 0], mirror=True, bone="head"),
  cone("brow", [0.585, 0.925, 0.03], [0.585, 0.925, -0.03], 0.016, 0.016, FC, k=0.012, kc=0.006, bone="head"),
  ell("nose", [0.626, 0.877, 0], [0.012, 0.02, 0.022], FC, k=0.007, kc=0.004, bone="head"),
  sph("nostril", [0.636, 0.868, 0.008], 0.0055, "@nostril", k=0.002, kc=0.0015, mirror=True, bone="head"),
  ell("muzzle", [0.59, 0.833, 0], [0.042, 0.04, 0.055], "@lip", k=0.02, kc=0.01, bone="head"),
  ell("lip", [0.624, 0.846, 0], [0.013, 0.012, 0.036], "@lip", k=0.007, kc=0.004, bone="head"),
  ell("lipL", [0.618, 0.815, 0], [0.013, 0.014, 0.034], "@lip", k=0.007, kc=0.004, bone="head"),
  ell("mouth", [0.629, 0.83, 0], [0.004, 0.003, 0.03], "@nostril", k=0.002, kc=0.0015, bone="head"),
  ell("sac", [0.55, 0.755, 0], [0.065, 0.075, 0.085], "@sac", k=0.035, kc=0.02, bone="head", **shag),
  ell("beard", [0.598, 0.79, 0], [0.03, 0.05, 0.05], "@beard", k=0.02, kc=0.015, bone="head", **shag),
  ell("ear", [0.49, 0.915, 0.083], [0.016, 0.022, 0.01], FC, k=0.006, kc=0.003, mirror=True, bone="head"),
]
# ---- the arms: very long, the coat hanging off their backs in locks
sh, el, wr = F.J("legFLu"), F.J("legFLl"), F.end("legFLl")
S += [
  tube("arm", [add(sh, [0, 0.02, -0.01]) + [0.08], lerp(sh, el, 0.5) + [0.068], el + [0.058]], H, k=0.04, bone="legFLu", mirror=True, **shag),
  cone("forearm", el, add(wr, [0.0, 0.015, 0]), 0.058, 0.044, H, k=0.03, bone="legFLl", mirror=True, **shag),
]
for j, t in enumerate([0.15, 0.45, 0.75]):
    p = lerp(sh, el, t)
    S += [hank(f"armH{j}", [p[0] - 0.05, p[1], p[2] + 0.03], 0.14, 0.06, 0.05, "legFLu", z=0.02)]
for j, t in enumerate([0.1]):
    p = lerp(el, wr, t)
    S += [hank(f"foreH{j}", [p[0] - 0.035, p[1], p[2] + 0.015], 0.09, 0.035, 0.042, "legFLl", z=0.01)]
# ---- the hands (audit 2026-11-07): an ape's HOOK -- a long narrow palm running down and forward from the wrist, four long
# fingers, slightly apart, curled under in a hook grip (the backs of their middle joints on the ground, the tips turned back
# toward the palm), the knuckles standing on the back of the hand; a SHORT thumb set low, near the wrist
x0, z0 = wr[0], wr[2]
W, K = [x0 + 0.004, 0.086, z0], [x0 + 0.128, 0.05, z0]
pa = math.degrees(math.atan2(K[1] - W[1], K[0] - W[0]))
S += [ell("palm", lerp(W, K, 0.5), [0.068, 0.022, 0.044], SK, k=0.012, kc=0.006, rot=[0, 0, pa], bone="footFL", mirror=True),
      ell("handBack", add(lerp(W, K, 0.4), [0, 0.012, 0]), [0.058, 0.015, 0.04], H, k=0.014, kc=0.01, rot=[0, 0, pa], bone="footFL", mirror=True, **shag)]
for j in range(4):
    z = z0 + (j - 1.5) * 0.028
    L = 1.0 - 0.1 * abs(j - 1.5)                      # the middle two longest
    kx = K[0] - 0.006 * abs(j - 1.5)
    k0 = [kx, K[1] + 0.002, z]
    p1 = [kx + 0.062 * L, 0.03, z]                    # the proximal phalanx forward and down
    p2 = [kx + 0.052 * L, 0.0125, z]                  # the middle one turning under, its back on the ground
    p3 = [kx + 0.012 * L, 0.016, z]                   # the distal one tucked back toward the palm
    # each finger ONE round tube through its joints (a smooth spline of round cones, sampled on a fine grid), tapering to a
    # rounded tip, a faint swelling at each of the two joints; rooted inside the palm
    S += [tube(f"finger{j}", [add(k0, [-0.016, 0.004, 0]) + [0.0102], k0 + [0.0104], lerp(k0, p1, 0.5) + [0.0098], p1 + [0.0108],
                             lerp(p1, p2, 0.5) + [0.0094], p2 + [0.0099], lerp(p2, p3, 0.55) + [0.0086], p3 + [0.0072]], SK, k=0.003, kc=0.002, bone="footFL", mirror=True)]
S += [tube("thumb", [[x0 + 0.008, 0.078, z0 - 0.02, 0.0106], [x0 + 0.02, 0.07, z0 - 0.032, 0.0108], [x0 + 0.043, 0.052, z0 - 0.047, 0.0096],
                     [x0 + 0.058, 0.04, z0 - 0.057, 0.0101], [x0 + 0.07, 0.03, z0 - 0.062, 0.0072]], SK, k=0.003, kc=0.002, bone="footFL", mirror=True)]
# ---- the legs: short and BOWED, the knees out; the feet hand-like, the toes curled
hp, kn, an = F.J("legHLu"), F.J("legHLl"), F.end("legHLl")
bow = 0.035
knO = add(kn, [0, 0, bow])
d = [knO[0] - hp[0], knO[1] - hp[1]]; th = math.degrees(math.atan2(d[0], -d[1]))
S += [
  ell("thigh", lerp(hp, knO, 0.5), [0.068, 0.12, 0.072], H, k=0.04, rot=[0, 0, th], bone="legHLu", mirror=True, **shag),
  cone("shank", knO, add(an, [0.0, 0.01, 0]), 0.052, 0.038, H, k=0.03, bone="legHLl", mirror=True, **shag),
  hank("thighH", [hp[0] - 0.03, hp[1] - 0.08, hp[2] + 0.04], 0.11, 0.02, 0.045, "legHLu", z=0.01),
]
fx, fz = an[0], an[2]
# the feet (audit 2026-11-07): hand-like -- a long narrow sole, four long toes hooked under the same way, and the big toe
# OPPOSED: short, set far back on the inner side near the heel, turned in and forward like a thumb
FH, FK = [fx - 0.025, 0.04, fz + 0.01], [fx + 0.14, 0.036, fz + 0.012]
S += [
  ell("hfoot", lerp(FH, FK, 0.5), [0.088, 0.026, 0.046], SK, k=0.014, kc=0.006, bone="footHL", mirror=True),
  ell("instep", [fx + 0.02, 0.058, fz + 0.005], [0.06, 0.03, 0.04], H, k=0.02, kc=0.015, bone="footHL", mirror=True, **shag),
  ell("heel", [fx - 0.025, 0.035, fz + 0.01], [0.03, 0.03, 0.032], SK, k=0.012, kc=0.006, bone="footHL", mirror=True),
  tube("hallux", [[fx + 0.004, 0.036, fz - 0.016, 0.0106], [fx + 0.015, 0.032, fz - 0.03, 0.0108], [fx + 0.034, 0.026, fz - 0.052, 0.0098],
                 [fx + 0.05, 0.022, fz - 0.068, 0.0103], [fx + 0.064, 0.018, fz - 0.072, 0.009], [fx + 0.076, 0.016, fz - 0.072, 0.0072]], SK, k=0.003, kc=0.002, bone="footHL", mirror=True),
]
for j in range(4):
    z = fz + 0.016 + (j - 1.5) * 0.027
    L = 1.0 - 0.12 * abs(j - 1.2)
    kx = FK[0] - 0.006 * abs(j - 1.5)
    k0 = [kx, 0.036, z]; p1 = [kx + 0.052 * L, 0.026, z]; p2 = [kx + 0.044 * L, 0.0115, z]; p3 = [kx + 0.01 * L, 0.0145, z]
    S += [tube(f"toe{j}", [add(k0, [-0.016, 0.003, 0]) + [0.0098], k0 + [0.01], lerp(k0, p1, 0.5) + [0.0094], p1 + [0.0104],
                          lerp(p1, p2, 0.5) + [0.009], p2 + [0.0095], lerp(p2, p3, 0.55) + [0.0083], p3 + [0.007]], SK, k=0.003, kc=0.002, bone="footHL", mirror=True)]

cols = {"body": "#6f2d11", "skin": "#3b2c25", "face": "#463a33", "flange": "#3f332d", "lip": "#5a4538", "sac": "#5a2a13",
        "beard": "#6a2e0e", "nostril": "#140e0b", "eye": "#2c1a0f", "lid": "#1d1410", "leg": "#6f2d11", "foot": "#3b2c25", "tail": "#6f2d11"}
eyes = {"at": [0.592, 0.906, 0.024], "from": [0.5, 0.906, 0.015], "r": 0.009, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.55, "socket": 1.15}
about = ("a flanged Bornean orangutan SCULPTED on its rig (2026-11-05, gen: scratchpad sc/prim/gen/orangutan.py, written in its standing "
         "pose): a male, the great red ape. Very long arms (a span of some two metres) and short BOWED legs, walking on its FISTS and the "
         "curled hand-like feet; a pear of a body -- narrow shoulders over a pot belly; the long shaggy red-orange coat hanging in locks off "
         "the backs of its arms, its thighs and its flanks (shag); the FLANGES -- broad cheek pads either side of a small flat grey face -- "
         "a pendulous throat sac under a russet beard, small close-set forward-facing eyes, small ears")
# ---- HEAD CARRIAGE: on all fours a flanged male holds his head forward at the shoulders' height, looking ahead, and it is
# BIG (with its flanges a third of the shoulders' width): every head shape above was drawn hanging low and small -- grown
# 1.2x about the back of the skull and lifted onto the shoulder line (rigs.py moves the head bone with it)
HP, HS, HD = [0.42, 0.9, 0], 1.2, [0.02, 0.09, 0]
def lift(p): return [HP[i] + HS * (p[i] - HP[i]) + HD[i] for i in range(3)]
for sh_ in S:
    if sh_.get("bone") != "head": continue
    for k in ("c", "a", "b"):
        if k in sh_: sh_[k] = lift(sh_[k])
    for k in ("r", "ra", "rb", "k", "kc"):
        if k in sh_: sh_[k] = [v * HS for v in sh_[k]] if isinstance(sh_[k], list) else sh_[k] * HS
eyes = {**eyes, "at": lift(eyes["at"]), "from": lift(eyes["from"]), "r": eyes["r"] * HS}
build(N, about, cols, S, eyes=eyes, mesh={"tris": [12000, 3600], "cell": 0.0055, "focus": {"head": 3, "footFL": 2.5, "footFR": 2.5, "footHL": 2, "footHR": 2}})
print("saved", N, len(S), "shapes")
