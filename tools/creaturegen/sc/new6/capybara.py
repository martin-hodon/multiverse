# capybara.py -- the capybara SCULPTED on its rig (rigs.py capybara_rig)
from rigs import *
N = "capybara"
rig = capybara_rig()
rig["c"] = {**rig["c"], "body": "#8a5e3a", "head": "#7e5636", "muzzle": "#6a462c", "belly": "#a8825a", "foot": "#5a3e2a", "nostril": "#1c120c",
            "gland": "#2a1c14", "lid": "#3a2618", "lip": "#5a3c28", "earIn": "#4a3020", "web": "#4a3626", "nail": "#1a120c", "mouth": "#26180e"}
rig["_about"] = ("a capybara SCULPTED on its rig (2026-11-05, gen: scratchpad sc/new6/capybara.py): the largest rodent, 1.2 m long and "
                 "0.55 m at the shoulder -- a heavy barrel of a body on short legs, the rump a little higher than the shoulders and "
                 "no tail at all; a big blunt box of a head, deep and square-ended, with the eyes, the small round ears and the "
                 "nostrils all set high (an animal that lies in the water with only those above it), the male's dark scent gland "
                 "on top of the snout; coarse sparse reddish-brown hair, paler beneath; four toes in front and three behind, "
                 "webbed between")
write_rig(N, rig)
J = joints_of(N)
S = Sculpt()
B = "@body"
o = lambda b: J[b]["o"]
FL, FK, FF = o("legFLu"), o("legFLl"), o("footFL")
HL, HK, HF = o("legHLu"), o("legHLl"), o("footHL")
HC = 0.2   # (the coat's sheen: low -- coarse sparse hair, matt; its strands painted per pixel, the `coarse` pattern)
# ---- trunk: one heavy barrel, the rump round and high, the belly deep
S.ell("rump", [-0.25, 0.43, 0], [0.29, 0.205, 0.205], rot=[0, 0, 6], k=0.07, color=B, hair=HC, pat="coarse")
S.ell("barrel", [-0.01, 0.41, 0], [0.3, 0.195, 0.215], rot=[0, 0, -2], k=0.07, color=B, hair=HC, pat="coarse")
S.ell("chest", [0.22, 0.395, 0], [0.18, 0.165, 0.165], rot=[0, 0, -10], k=0.06, color=B, hair=HC, pat="coarse")
S.ell("belly", [-0.03, 0.3, 0], [0.3, 0.1, 0.17], k=0.06, kc=0.05, color="@belly", hair=HC, pat="coarse")
S.ell("haunch", [-0.33, 0.36, 0.1], [0.14, 0.14, 0.08], rot=[0, 0, 10], bone="legHLu", k=0.05, color=B, mirror=True, hair=HC, pat="coarse")
S.ell("shoulder", [0.25, 0.35, 0.1], [0.09, 0.12, 0.06], rot=[0, 0, 15], bone="legFLu", k=0.045, color=B, mirror=True, hair=HC, pat="coarse")
# ---- neck: short and thick, the head carried low and level
S.ell("neck", [0.41, 0.46, 0], [0.13, 0.125, 0.12], rot=[0, 0, 18], bone="neck", k=0.06, color=B, hair=HC, pat="coarse")
S.ell("throat", [0.45, 0.39, 0], [0.1, 0.07, 0.09], rot=[0, 0, 10], bone="neck", k=0.04, kc=0.03, color="@belly", hair=HC, pat="coarse")
# ---- head: a deep blunt box -- a flat top from the brow to the nose, a square deep muzzle, heavy cheeks
S.ell("cranium", [0.57, 0.545, 0], [0.12, 0.1, 0.085], rot=[0, 0, -6], bone="head", k=0.04, color="@head", hair=HC * 0.7, pat="coarse")
S.ell("bridge", [0.7, 0.565, 0], [0.15, 0.042, 0.062], rot=[0, 0, -9], bone="head", k=0.035, color="@head", hair=HC * 0.7, pat="coarse")
S.ell("cheek", [0.63, 0.48, 0.05], [0.1, 0.07, 0.04], rot=[0, 0, -8], bone="head", k=0.035, color="@head", hair=HC * 0.7, pat="coarse", mirror=True)
S.ell("face", [0.72, 0.5, 0], [0.11, 0.1, 0.072], rot=[0, 0, -8], bone="head", k=0.035, color="@head", hair=HC * 0.7, pat="coarse")
S.ell("snout", [0.805, 0.49, 0], [0.05, 0.088, 0.066], rot=[0, 0, -10], bone="head", k=0.03, color="@muzzle", hair=HC * 0.7, pat="coarse")
S.ell("lip", [0.79, 0.425, 0], [0.05, 0.035, 0.05], bone="head", k=0.02, kc=0.01, color="@lip")
S.ell("jaw", [0.66, 0.425, 0], [0.12, 0.045, 0.055], rot=[0, 0, -4], bone="head", k=0.03, color="@head", hair=HC * 0.7, pat="coarse")
S.ell("gland", [0.735, 0.598, 0], [0.042, 0.012, 0.028], rot=[0, 0, -9], bone="head", k=0.008, kc=0.004, color="@gland")
# the nostrils carved high on the blunt end, the upper lip cleft below them, the mouth's line carved back along the jaw
S.ell("nostril", [0.858, 0.527, 0.024], [0.0085, 0.016, 0.009], rot=[0, 0, 32], bone="head", k=0.005, op="sub", color="@nostril", mirror=True)
S.tube("cleft", [[0.856, 0.5, 0, 0.006], [0.85, 0.447, 0, 0.0065]], bone="head", k=0.005, op="sub", color="@mouth")
S.tube("mouth", [[0.846, 0.437, 0.004, 0.008], [0.832, 0.434, 0.032, 0.0085], [0.802, 0.434, 0.05, 0.008], [0.768, 0.438, 0.052, 0.006]], bone="head", k=0.006, op="sub", color="@mouth", mirror=True)
# ears: small, round, high and far back
S.ell("ear", [0.545, 0.645, 0.062], [0.012, 0.024, 0.024], rot=[15, -30, -10], bone="earL", k=0.01, kc=0.004, color="@ear", mirror=True)
S.ell("earIn", [0.552, 0.646, 0.064], [0.005, 0.017, 0.017], rot=[15, -30, -10], bone="earL", k=0.003, kc=0.002, color="@earIn", mirror=True)
# ---- legs: short and stout; four webbed toes in front, three behind
S.cone("forearm", [FL[0] - 0.01, FL[1] + 0.04, FL[2]], [FF[0] - 0.012, 0.05, FF[2]], 0.068, 0.042, bone="legFLl", k=0.035, color=B, mirror=True, hair=HC, pat="coarse")
S.ell("hand", [FF[0] + 0.012, 0.022, FF[2]], [0.052, 0.024, 0.042], bone="footFL", k=0.015, color="@foot", mirror=True)
for j, dz in enumerate((-0.027, -0.009, 0.009, 0.027)):
    S.ell(f"toe{j}", [FF[0] + 0.054, 0.016, FF[2] + dz * 1.15], [0.024, 0.016, 0.0125], rot=[0, -dz * 400, 0], bone="footFL", k=0.006, kc=0.003, color="@foot", mirror=True)   # (audit 2026-11-07: toes that read, not a pancake)
    S.ell(f"nail{j}", [FF[0] + 0.077, 0.013, FF[2] + dz * 1.2], [0.008, 0.008, 0.007], bone="footFL", k=0.003, kc=0.001, color="@nail", mirror=True)
S.ell("webF", [FF[0] + 0.045, 0.011, FF[2]], [0.02, 0.006, 0.034], bone="footFL", k=0.006, kc=0.003, color="@web", mirror=True)
S.cone("gaskin", [HL[0] + 0.02, HL[1] - 0.02, HL[2]], [HK[0] - 0.02, HK[1] + 0.005, HK[2]], 0.085, 0.05, bone="legHLu", k=0.04, color=B, mirror=True, hair=HC, pat="coarse")
S.cone("hock", [HK[0] - 0.022, HK[1], HK[2]], [HF[0] - 0.01, 0.03, HF[2]], 0.046, 0.034, bone="legHLl", k=0.02, color=B, mirror=True, hair=HC, pat="coarse")
S.ell("sole", [HF[0] + 0.02, 0.02, HF[2]], [0.065, 0.02, 0.038], bone="footHL", k=0.015, color="@foot", mirror=True)
for j, dz in enumerate((-0.022, 0.0, 0.022)):
    S.ell(f"htoe{j}", [HF[0] + 0.084, 0.016, HF[2] + dz * 1.1], [0.028, 0.017, 0.0135], rot=[0, -dz * 300, 0], bone="footHL", k=0.006, kc=0.003, color="@foot", mirror=True)
    S.ell(f"hnail{j}", [HF[0] + 0.112, 0.013, HF[2] + dz * 1.15], [0.009, 0.008, 0.008], bone="footHL", k=0.003, kc=0.001, color="@nail", mirror=True)
S.ell("webH", [HF[0] + 0.07, 0.011, HF[2]], [0.022, 0.006, 0.03], bone="footHL", k=0.006, kc=0.003, color="@web", mirror=True)
sc = {"keep": [], "mesh": {"tris": [6400, 2200], "cell": 0.007}, "shape": S.shapes,
      "eyes": {"at": [0.655, 0.6, 0.068], "from": [0.6, 0.57, 0], "r": 0.015, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.55, "socket": 1.05},
      "shade": {"back": 0.88, "belly": 1.15, "k": 0.14, "on": B}}
finish(N, rig, sc)
