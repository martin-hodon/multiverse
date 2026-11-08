# porcupine.py -- the crested porcupine (Hystrix cristata) SCULPTED on its rig (rigs5.py porcupine_rig)
from rigs5 import *
N = "porcupine"
rig = porcupine_rig()
rig["c"] = {**rig["c"], "belly": "#2a221c", "paw": "#120e0c", "lid": "#0a0807", "claw": "#3a3029", "face": "#1a1512", "whisker": "#8a8078", "nose": "#3e302c", "crest": "#d8d2c6", "lip": "#2c231d",
            "nostril": "#0a0807", "white": "#e6e0d4"}
rig["variants"] = {"porcupette": {"scale": 0.5}}
rig["_about"] = ("a crested porcupine SCULPTED on its rig (2026-11-06, gen: scratchpad sc/new6/porcupine.py): 70 cm of stocky rodent "
                 "low on short legs, a blunt dark rounded face with small eyes and small round ears; coarse black-brown hair "
                 "below, and over the back and rump a coat of long quills (bodymesh.js coat, `bands`: black and white, sharp-"
                 "banded, white-tipped) lying back and raised into a fan over the rump, the longest there, and a crest of "
                 "long bristles (the same coat, `coat` over 1: longer) along the head and the neck; a short tail; it shuffles")
write_rig(N, rig)
J = joints_of(N)
S = Sculpt()
B = "@body"
o = lambda b: J[b]["o"]
FL, FK, FF = o("legFLu"), o("legFLl"), o("footFL")
HL, HK, HF = o("legHLu"), o("legHLl"), o("footHL")
H0 = 0.15
# ---- trunk: a round low barrel, the rump the highest and broadest (the quills grow on the `coat` shapes: the more,
#      the longer -- 1 the back, 1.5 the rump's fan, 1.3 the crest)
S.ell("chest", [0.07, 0.17, 0], [0.12, 0.095, 0.105], rot=[0, 0, -8], k=0.04, color=B, hair=H0, pat="coarse")
S.ell("barrel", [-0.05, 0.19, 0], [0.17, 0.118, 0.13], k=0.045, color=B, hair=H0, pat="coarse", coat=1.0)
S.ell("rump", [-0.17, 0.2, 0], [0.13, 0.128, 0.14], rot=[0, 0, -10], k=0.04, color=B, hair=H0, pat="coarse", coat=2.0)
S.ell("belly", [-0.05, 0.12, 0], [0.18, 0.06, 0.1], k=0.04, color="@belly", hair=H0, pat="coarse")
S.ell("haunch", [-0.22, 0.15, 0.07], [0.08, 0.08, 0.05], bone="legHLu", k=0.035, color=B, mirror=True, hair=H0, pat="coarse")
S.ell("shoulder", [0.11, 0.13, 0.06], [0.055, 0.07, 0.04], bone="legFLu", k=0.03, color=B, mirror=True, hair=H0, pat="coarse")
# ---- neck and head: a short thick neck; a big blunt rounded head, dark; a short deep muzzle, the nose's pad broad
S.ell("neck", [0.18, 0.168, 0], [0.075, 0.075, 0.075], bone="neck", k=0.035, color=B, hair=H0, pat="coarse", coat=1.0)
S.ell("crestN", [0.18, 0.225, 0], [0.07, 0.03, 0.035], bone="neck", k=0.03, color=B, hair=H0, pat="coarse", coat=1.5)
S.ell("cranium", [0.272, 0.165, 0], [0.06, 0.055, 0.055], rot=[0, 0, -8], bone="head", k=0.025, color="@face", hair=H0, pat="coarse")
S.ell("crestH", [0.255, 0.212, 0], [0.045, 0.02, 0.025], bone="head", k=0.02, color="@face", hair=H0, pat="coarse", coat=1.5)
S.ell("cheek", [0.29, 0.148, 0.03], [0.04, 0.035, 0.028], bone="head", k=0.02, color="@face", mirror=True, hair=H0, pat="coarse")
S.ell("muzzle", [0.338, 0.145, 0], [0.045, 0.038, 0.036], rot=[0, 0, -12], bone="head", k=0.02, color="@face", hair=H0, pat="coarse")
S.ell("nosePad", [0.379, 0.138, 0], [0.012, 0.02, 0.025], bone="head", k=0.008, kc=0.003, color="@nose", wet=0.5)
# whiskers: long, fine, swept out and back from the muzzle's sides
for j, (dy, dz2) in enumerate(((0.006, 0.0), (-0.004, 0.012), (-0.014, 0.004))):
    S.cone(f"whisker{j}", [0.355, 0.14 + dy, 0.03], [0.33, 0.135 + dy * 2, 0.115 + dz2], 0.0011, 0.0003, bone="head", k=0, color="@whisker", mirror=True)
S.ell("lip", [0.36, 0.115, 0], [0.025, 0.012, 0.025], bone="head", k=0.012, kc=0.004, color="@lip", hair=H0)
S.ell("ear", [0.258, 0.2, 0.05], [0.006, 0.014, 0.014], rot=[0, -20, 0], bone="earL", k=0.006, color="@ear", mirror=True, hair=H0)
S.ell("nostril", [0.388, 0.138, 0.011], [0.005, 0.007, 0.004], rot=[0, 0, 20], bone="head", k=0.003, op="sub", color="@nostril", mirror=True)
# ---- legs: short and thick, dark; broad feet with long claws
S.cone("arm", [FL[0], FL[1] + 0.02, FL[2]], FK, 0.032, 0.024, bone="legFLu", k=0.016, color="@leg", mirror=True, hair=H0, pat="coarse")
S.cone("forearm", FK, [FF[0], 0.016, FF[2]], 0.024, 0.018, bone="legFLl", k=0.012, color="@leg", mirror=True, hair=H0, pat="coarse")
S.ell("paw", [FF[0] + 0.012, 0.01, FF[2]], [0.026, 0.01, 0.019], bone="footFL", k=0.008, color="@paw", mirror=True)
S.ell("thigh", [HL[0], HL[1], HL[2]], [0.05, 0.06, 0.035], bone="legHLu", k=0.02, color="@leg", mirror=True, hair=H0, pat="coarse")
S.cone("shank", HK, [HF[0], 0.016, HF[2]], 0.026, 0.019, bone="legHLl", k=0.012, color="@leg", mirror=True, hair=H0, pat="coarse")
S.ell("foot", [HF[0] + 0.014, 0.01, HF[2]], [0.034, 0.01, 0.02], bone="footHL", k=0.008, color="@paw", mirror=True)
for j, dz in enumerate((-0.012, -0.004, 0.004, 0.012)):
    S.cone(f"claw{j}", [FF[0] + 0.032, 0.008, FF[2] + dz], [FF[0] + 0.046, 0.002, FF[2] + dz * 1.1], 0.003, 0.0012, bone="footFL", k=0, color="@claw", mirror=True)
    S.cone(f"hclaw{j}", [HF[0] + 0.042, 0.008, HF[2] + dz], [HF[0] + 0.054, 0.002, HF[2] + dz * 1.1], 0.003, 0.0012, bone="footHL", k=0, color="@claw", mirror=True)
# ---- the tail: short, hidden in the rump's quills
T = rig["tail"]; P = arc_pts(T, 3)
S.cone("tail", P[0] + [0], P[3] + [0], 0.035, 0.02, bone="tail", k=0.02, color=B, hair=H0, pat="coarse", coat=1.9)
QUILLS = {"gap": 0.0245, "len": 0.12, "r": 0.0024, "sides": 3, "lean": 0.62, "vary": 0.1, "fan": 0.5, "fanAt": 1.55, "sparse": 0.75, "skirt": -0.15, "drop": 0.55, "face": 0.45, "rise": 1.0,
          "base": "#1a1512", "tip": "#efe9de", "dark": 0.0, "hold": 0.5,
          "bands": [[0.14, "#f0eae0"], [0.5, "#17120f"], [0.62, "#f2ede4"]]}
# ---- THE CREST (round 3): long slender bristles along the head and the neck, rooted on the measured skin and swept
#      BACK and up -- 8 cm at the brow growing to 21 cm over the shoulders, pale grey-white (thin: drawn as lathes)
import json as _j, subprocess as _sp, random as _rnd
def probe(qs):
    _j.dump(S.shapes, open(HERE + "/_s3.json", "w")); _j.dump(qs, open(HERE + "/_q3.json", "w"))
    return _j.loads(_sp.check_output(["node", HERE + "/surf3.mjs", HERE + "/_s3.json", HERE + "/_q3.json"]))
_rnd.seed(7)
roots = []
for i in range(15):
    x = 0.31 - i * 0.018
    for z in ((-0.016, 0.0, 0.016) if i % 2 else (-0.008, 0.008)):
        roots.append((x + _rnd.uniform(-0.004, 0.004), z + _rnd.uniform(-0.003, 0.003)))
hits = probe([{"o": [x, 0.17, z], "d": [0, 1, 0]} for x, z in roots])   # (from inside, out: the skin above)
for k, ((x, z), h) in enumerate(zip(roots, hits)):
    if h.get("t") is None: continue
    y = 0.17 + h["t"] - 0.003
    f = min(1, max(0, (0.31 - x) / 0.25))
    L = 0.08 + 0.13 * f + _rnd.uniform(-0.015, 0.015)
    a = math.radians(34 + 18 * f + _rnd.uniform(-7, 7))   # (above the backward horizontal: the crest half raised)
    tip = [x - L * math.cos(a), y + L * math.sin(a), z * 2.2 + _rnd.uniform(-0.006, 0.006)]
    S.cone(f"bristle{k}", [x, y, z], tip, 0.0026, 0.0005, bone="head" if x > 0.235 else "neck", k=0, color="@crest")
sc = {"keep": [], "coat": QUILLS, "mesh": {"tris": [3600, 1250], "cell": 0.0055, "focus": {"head": 5}}, "shape": S.shapes,
      "eyes": {"at": [0.318, 0.176, 0.04], "from": [0.27, 0.168, 0], "r": 0.0055, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.6, "socket": 1.0}}
finish(N, rig, sc)
