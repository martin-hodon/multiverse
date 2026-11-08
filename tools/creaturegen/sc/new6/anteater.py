# anteater.py -- the giant anteater SCULPTED on its rig (rigs.py anteater_rig)
from rigs import *
N = "anteater"
rig = anteater_rig()
rig["c"] = {**rig["c"], "body": "#6e6458", "fore": "#7a7064", "head": "#7a7266", "snout": "#6a645a", "stripe": "#121010", "edge": "#e6e0d2",
            "hind": "#3e3630", "foot": "#1e1a16", "claw": "#4a4238", "band": "#141210", "tail": "#3a342e", "tailTip": "#4a4238", "lid": "#2a2420"}
rig["_about"] = ("a giant anteater SCULPTED on its rig (2026-11-05, gen: scratchpad sc/new6/anteater.py): a deep, narrow body 0.6 m at "
                 "the shoulder; the head drawn out into a long, tubular, slightly down-curved snout -- head and snout a third of "
                 "the head-and-body -- with tiny eyes and small round ears; coarse grizzled grey-brown hair, the hind legs dark; "
                 "the bold black band from the throat diagonally back and up over the shoulder to a point on the back, edged "
                 "in white on both sides (painted per pixel: the `anteater` pattern); pale forelegs with a black band at the wrist, knuckle-"
                 "walking on the outer edge of the fists, the great fore claws curled in under them; and a huge bushy flag of a "
                 "tail, long hair hanging in a tall flat sheet")
write_rig(N, rig)
J = joints_of(N)
S = Sculpt()
B = "@body"
o = lambda b: J[b]["o"]
FL, FK, FF = o("legFLu"), o("legFLl"), o("footFL")
HL, HK, HF = o("legHLu"), o("legHLl"), o("footHL")
# ---- trunk: deep and narrow, the back near level, rising a little over the hips
S.ell("chest", [0.2, 0.465, 0], [0.25, 0.225, 0.14], rot=[0, 0, -4], k=0.06, color="@fore", hair=0.8, pat="anteater")
S.ell("barrel", [-0.1, 0.48, 0], [0.3, 0.18, 0.135], rot=[0, 0, 4], k=0.06, color=B, hair=0.8, pat="anteater")
S.ell("rump", [-0.42, 0.49, 0], [0.22, 0.152, 0.12], rot=[0, 0, 8], k=0.06, color=B, hair=0.8, pat="anteater")
S.ell("belly", [-0.06, 0.36, 0], [0.3, 0.08, 0.1], k=0.05, color=B, hair=0.6, pat="anteater")
S.ell("crest", [-0.12, 0.65, 0], [0.4, 0.03, 0.04], rot=[0, 0, 3], k=0.04, color=B, hair=1, pat="anteater")
S.ell("scapula", [0.28, 0.52, 0.07], [0.1, 0.14, 0.06], rot=[0, 0, 15], k=0.04, color="@fore", mirror=True, hair=0.8, pat="anteater")
# ---- neck and head: a thick neck running straight into a narrow head; the tube of a snout, curving a little down
S.ell("neck", [0.46, 0.5, 0], [0.14, 0.11, 0.095], rot=[0, 0, -4], bone="neck", k=0.05, color="@fore", hair=0.8, pat="anteater")
S.ell("cranium", [0.62, 0.51, 0], [0.09, 0.07, 0.065], rot=[0, 0, -6], bone="head", k=0.04, color="@head")
S.tube("snout", [[0.65, 0.505, 0, 0.056], [0.75, 0.487, 0, 0.042], [0.87, 0.463, 0, 0.032], [0.97, 0.44, 0, 0.025], [1.025, 0.425, 0, 0.021]], bone="head", k=0.03, color="@snout")
S.ell("nose", [1.036, 0.421, 0], [0.012, 0.016, 0.016], bone="head", k=0.008, kc=0.004, color="@nose", wet=0.4)
S.ell("ear", [0.598, 0.565, 0.048], [0.01, 0.02, 0.018], rot=[20, -20, -10], bone="earL", k=0.008, kc=0.003, color="@head", mirror=True)
# ---- the fore legs: thick, pale; a black band at the wrist; knuckle-walking on a black fist, the claws curled in under it
S.cone("arm", [FL[0] - 0.01, FL[1] + 0.08, FL[2]], [FK[0], FK[1] + 0.01, FK[2]], 0.08, 0.06, bone="legFLu", k=0.04, color="@leg", mirror=True, hair=0.6, pat="anteater")
S.cone("forearm", [FK[0], FK[1] + 0.01, FK[2]], [FF[0] - 0.008, 0.075, FF[2]], 0.06, 0.044, bone="legFLl", k=0.03, color="@leg", mirror=True)
S.cone("wrist", [FF[0] - 0.01, 0.125, FF[2]], [FF[0] - 0.005, 0.075, FF[2]], 0.05, 0.047, bone="legFLl", k=0.01, kc=0.018, color="@band", mirror=True)
S.ell("fist", [FF[0] + 0.012, 0.038, FF[2] + 0.006], [0.05, 0.036, 0.04], rot=[0, 0, -10], bone="footFL", k=0.02, color="@foot", mirror=True)
for j, (dz, L0) in enumerate(((-0.011, 0.05), (0.008, 0.058))):
    x0 = FF[0] + 0.045
    # (thinner than 0.8 cell: drawn as smooth lathed detail on the foot's bone, rooted inside the fist -- in the field they were lumps)
    S.tube(f"claw{j}", [[x0 - 0.016, 0.036, FF[2] + dz, 0.0086], [x0 + 0.006, 0.03, FF[2] + dz, 0.0085], [x0 + 0.016, 0.016, FF[2] + dz, 0.0078], [x0 + 0.01, 0.0045, FF[2] + dz, 0.0055]],
           bone="footFL", k=0.004, kc=0.002, color="@claw", mirror=True)
# ---- the hind legs: dark, plantigrade, short claws
S.ell("thigh", [HL[0] + 0.01, HL[1] + 0.02, HL[2] + 0.02], [0.12, 0.15, 0.065], rot=[0, 0, 10], bone="legHLu", k=0.045, color="@hind", mirror=True, hair=0.8)
S.cone("shank", [HK[0] + 0.01, HK[1] + 0.02, HK[2]], [HF[0] - 0.01, 0.045, HF[2]], 0.055, 0.04, bone="legHLl", k=0.03, color="@hind", mirror=True)
S.ell("foot", [HF[0] + 0.02, 0.022, HF[2]], [0.07, 0.022, 0.035], bone="footHL", k=0.015, color="@foot", mirror=True)
for j, dz in enumerate((-0.02, -0.007, 0.007, 0.02)):
    S.cone(f"nail{j}", [HF[0] + 0.074, 0.015, HF[2] + dz], [HF[0] + 0.1, 0.005, HF[2] + dz * 1.15], 0.006, 0.003, bone="footHL", k=0, color="@claw", mirror=True)
# ---- the tail: a huge flag -- a stout core, the long hair hanging below it (and a shorter crest above) in a tall flat sheet
T = rig["tail"]; P = arc_pts(T, 8)
for i in range(8):
    a, b = P[i] + [0], P[i + 1] + [0]; m = lerp(a, b, 0.5); d = sub(b, a); t = (i + 0.5) / 8
    rc = 0.065 - 0.03 * t
    S.ell(f"tail{i}", m, [length(d) * 0.75, rc, rc * 0.9], rot=[0, 0, ang(d)], bone="tail", k=0.04, color="@tail", hair=0.4)
    hang = 0.06 + 0.2 * math.sin(math.pi * min(1.0, 0.15 + t * 0.95)) ** 0.7   # (the sheet's depth below the core)
    for j, fx in enumerate((-0.22, 0.22)):   # (two locks a segment, staggered, streaming back: a ragged edge of long hair)
        c0 = add(lerp(a, b, 0.5 + fx), [0, -hang * (0.5 + 0.08 * j), 0])
        S.ell(f"flag{i}{'ab'[j]}", c0, [length(d) * 0.5, hang * 0.6 + rc * 0.4, 0.04 - 0.014 * t], rot=[0, 0, ang(d) * 0.5 + 78], bone="tail", k=0.045, kc=0.012,
              color="@tailTip" if (i + j) % 3 == 0 or i >= 6 else "@tail", hair=0.4, fleece=True)
        # (long coarse hair streaming from the sheet's lower edge, down and back: a brush, not a paddle)
        for k2, (dx, dz) in enumerate(((-0.02, 0.012), (0.025, -0.012))):
            top = add(c0, [dx, -hang * 0.45, dz]); L2 = hang * 0.5 + 0.06 + 0.015 * ((i + k2) % 3)
            S.cone(f"lockT{i}{'ab'[j]}{k2}", top, add(top, [-0.05 - 0.03 * t, -L2, dz * 0.5]), 0.024 - 0.006 * t, 0.008, bone="tail", k=0.012, kc=0.008,
                   color="@tailTip" if (i + j + k2) % 2 == 0 else "@tail", hair=0.4)
    S.ell(f"crestT{i}", add(m, [0, rc * 0.7, 0]), [length(d) * 0.7, rc * 0.7 + 0.03 * (1 - t), 0.032], rot=[0, 0, ang(d)], bone="tail", k=0.04, color="@tail", hair=0.4, fleece=True)
# ---- the band: black from the throat, back and up over the shoulder to a point on the back -- white-edged on both sides
BAND = [(0.4, -40, 0.045), (0.36, -26, 0.052), (0.33, -20, 0.055), (0.27, 2, 0.055), (0.2, 22, 0.05), (0.12, 40, 0.044), (0.04, 55, 0.036), (-0.04, 66, 0.027), (-0.11, 74, 0.017), (-0.16, 79, 0.008)]
BAND = [tuple(BAND[i][k] + (BAND[i + 1][k] - BAND[i][k]) * f for k in range(3)) for i in range(len(BAND) - 1) for f in (0, 1 / 3, 2 / 3)] + [BAND[-1]]   # (three ells a step: no scallops)
# (now painted per pixel, coatpat.js anteaterOf (pat 38), on the trunk's shapes -- the path above is its knots)
sc = {"keep": [], "mesh": {"tris": [6500, 2300], "cell": 0.011, "focus": {"head": 4, "footFL": 3}}, "shape": S.shapes,
      "eyes": {"at": [0.7, 0.535, 0.042], "from": [0.64, 0.52, 0], "r": 0.0075, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.5, "socket": 1.0},
      "shade": {"back": 0.95, "belly": 0.82, "k": 0.14, "on": B}}
finish(N, rig, sc)
