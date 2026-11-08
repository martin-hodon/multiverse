# equid.py horse|zebra -- the horse family's sculpt (horse frame), written from the rig's joints
import sys
from lib import *
import math
name = sys.argv[1]
J = joints(name)
Z = name == "zebra"
s = 0.85 if Z else 1.0
W = 1.06 if Z else 1.0           # (a zebra is stockier: wider and deeper for its height)
S = Sculpt()
B = "@body"
def P(x, y, z=0): return [x * s, y * s, z * s * W]
def r3(a, b, c): return [a * s, b * s * (W if Z else 1), c * s * W]
pat = {"pat": "bands", "frame": "body"} if Z else {}
# ---- the trunk: barrel, deep chest, withers, loin, a round croup over the haunches
S.ell("barrel", P(-0.06, 1.22), r3(0.58, 0.33, 0.31), k=0.1 * s, color=B, **pat)
S.ell("chest", P(0.4, 1.19), r3(0.35, 0.36, 0.26), k=0.1 * s, color=B, **pat)
S.ell("withers", P(0.36, 1.5), r3(0.3, 0.13, 0.11), rot=[0, 0, -14], k=0.09 * s, color=B if Z else "@back", **pat)
S.ell("scapula", P(0.55, 1.32, 0.16), r3(0.085, 0.27, 0.075), rot=[0, 0, 36], k=0.07 * s, color=B, mirror=True, **pat)
S.ell("breast", P(0.72, 1.12, 0.1), r3(0.12, 0.17, 0.1), rot=[0, 0, 15], k=0.07 * s, color=B, mirror=True, **pat)
S.ell("loin", P(-0.36, 1.42), r3(0.32, 0.16, 0.25), k=0.1 * s, color=B if Z else "@back", **pat)
S.ell("belly", P(0.0, 1.04), r3(0.44, 0.15, 0.28), rot=[0, 0, -6], k=0.1 * s, color=B if Z else "@flank", **pat)
# (the hindquarter in its own frame on a zebra: the stripes turn back over the haunch and lie down over the thigh)
#  (v given, up: ONE frame for croup, haunches and hind legs alike -- unsaid, the steep axis read as a limb's and each side
#  measured round from its own outer side, three frames crossfading over the rump and under the tail; 2026-11-08)
hq = {"pat": "bands", "frame": {"o": R3([J["legHLu"]["o"][0] + 0.25 * s, J["legHLu"]["o"][1] + 0.1 * s, 0]), "u": [-0.62, -0.785, 0], "v": [0, 1, 0], "r": round(0.12 * s, 3)}} if Z else {}
S.ell("croup", P(-0.56, 1.36), r3(0.36, 0.25, 0.28), rot=[0, 0, 0 if Z else -9], k=(0.04 if Z else 0.1) * s, color=B, **(hq if Z else {}))
S.ell("haunch", P(-0.6, 1.24, 0.15), r3(0.3, 0.3, 0.16), k=(0.04 if Z else 0.08) * s, color=B, mirror=True, **hq)
S.ell("buttock", P(-0.78, 1.2, 0.09) if Z else P(-0.79, 1.17, 0.1), r3(0.14, 0.27, 0.11) if Z else r3(0.15, 0.26, 0.12), rot=[0, 0, -8 if Z else -22], k=(0.04 if Z else 0.07) * s, color=B, mirror=True, **hq)
if not Z: S.ell("hip", P(-0.42, 1.46, 0.2), r3(0.1, 0.08, 0.08), k=0.06 * s, color=B, mirror=True, **(hq if Z else {}))
S.cone("dock", P(-0.8, 1.52) if Z else P(-0.8, 1.49), P(-0.95, 1.47) if Z else P(-0.93, 1.42), 0.075 * s, 0.06 * s, k=0.05 * s, color=B, **(hq if Z else {}))
# ---- the neck: deep at the chest, arching to the poll, narrow at the throat
npat = pat
S.ell("neckBase", P(0.7, 1.4), r3(0.3, 0.3, 0.21), rot=[0, 0, 45], k=0.1 * s, color=B, **(npat if Z else pat))
S.ell("neck", P(0.97, 1.68), r3(0.43, 0.235, 0.135), rot=[0, 0, 47], bone="neck", k=0.1 * s, color=B, **npat)
S.ell("crest", P(0.86, 1.8), r3(0.4, 0.075, 0.075), rot=[0, 0, 36], bone="neck", k=0.08 * s, color=B if Z else "@back", **npat)
S.ell("throat", P(1.17, 1.8), r3(0.14, 0.085, 0.085), rot=[0, 0, 62], bone="neck", k=0.07 * s, color=B, **npat)
# ---- the head: from the poll down the long face to the muzzle; big flat jowls behind
poll, tip = P(1.37, 2.1), P(1.75, 1.63)
if Z: poll, tip = P(1.36, 2.12), P(1.775, 1.6)
hf = Frame(poll, sub(tip, poll)); L = length(sub(tip, poll))
def H(t, h=0, z=0): return hf(t * L, h * L, z * L)
hr = hf.rot()
# (v given: one frame for the whole head -- unsaid, the face's steep axis read as a LIMB's and each jowl measured round
#  from its own outer side, three frames meeting behind the eye in a smear; 2026-11-08)
hpat = {"pat": "bands", "frame": {"o": R3(H(0.4)), "u": R3(hf.a), "v": [1, 0, 0], "r": round(0.038 * s, 3)}} if Z else {}
S.ell("cranium", H(0.16, -0.02), [0.22 * L, 0.18 * L, 0.17 * L], rot=hr, bone="head", k=0.05 * s, color=B, **hpat)
S.ell("forehead", H(0.3, 0.07), [0.24 * L, 0.06 * L, 0.16 * L], rot=hr, bone="head", k=0.05 * s, color=B, **hpat)
S.ell("jowl", H(0.3, -0.2, 0.09), [0.21 * L, 0.21 * L, 0.075 * L], rot=hf.rot(0, 0, 0), bone="head", k=0.05 * s, color=B, mirror=True, **hpat)
S.cone("face", H(0.3, 0.01), H(0.82, -0.02), 0.15 * L, 0.11 * L, bone="head", k=0.06 * s, color=B, **hpat)
S.ell("muzzle", H(0.87, -0.06), [0.14 * L, 0.15 * L, 0.105 * L], rot=hr, bone="head", k=0.05 * s, color="@muzzle")
S.ell("nostril", H(0.92, 0.03, 0.065), [0.05 * L, 0.025 * L, 0.025 * L], rot=hf.rot(25), bone="head", k=0.012 * s, kc=0.006, color="@nose", mirror=True)
S.cone("underjaw", H(0.42, -0.17), H(0.8, -0.15), 0.075 * L, 0.06 * L, bone="head", k=0.05 * s, color=B, **hpat)
S.ell("chin", H(0.8, -0.19), [0.08 * L, 0.05 * L, 0.065 * L], rot=hr, bone="head", k=0.05 * s, color="@muzzle")
# ears: tall and pointed, upright off the poll
eb = H(0.03, 0.1, 0.085)
et = add(eb, [0.03 * s, (0.17 if not Z else 0.19) * s, 0.035 * s])
ew = 0.045 if not Z else 0.06
S.ell("ear", lerp(eb, et, 0.5), [0.03 * s, length(sub(et, eb)) * 0.55, ew * s], rot=[-12, 0, -8], bone="earL", k=0.02 * s, kc=0.006, color="@ear", mirror=True)
S.ell("earIn", add(lerp(eb, et, 0.5), [0.022 * s, 0, 0]), [0.012 * s, length(sub(et, eb)) * 0.42, ew * 0.6 * s], rot=[-12, 0, -8], bone="earL", k=0.006 * s, kc=0.003, color="@earIn", mirror=True)
# mane: a crest of locks falling to the right (a zebra's stands up, short and stiff)
# (2026-11-07: these plates/ells and the forelock are only the placeholders -- var/mane/mane.py replaces them with the real
#  mane in locks (horse: mane.py horse.json horse.json horse; zebra: ... zebra) -- run it after this, and peg.py after that)
top0, top1 = P(0.44, 1.62), P(1.32, 2.11)
if Z:
    # (a stiff upright brush, 10-14 cm tall, its bands the neck's run on up into it: thin tall plates in the body frame)
    for i in range(9):
        t = i / 8
        c = lerp(top0, top1, t); h = (0.06 + 0.05 * math.sin(math.pi * min(1, t * 1.15))) * s
        S.ell(f"mane{i}", add(c, [0, h * 0.55, 0]), [0.075 * s, h, 0.022 * s], rot=[0, 0, 40], bone="neck", k=0.02 * s, kc=0.004, color=B, hair=0.6, **npat)
else:
    # (a continuous under-layer along the crest, and 16 thin overlapping locks off it falling to the right)
    S.tube("maneRidge", [add(lerp(top0, top1, t), [0, 0.03 * s, -0.015 * s]) + [r * s] for t, r in ((0.0, 0.035), (0.3, 0.05), (0.7, 0.05), (1.0, 0.04))], bone="neck", k=0.02 * s, kc=0.006, color="@mane", hair=0.45)
    for i in range(16):
        t = 0.03 + 0.94 * i / 15
        c = lerp(top0, top1, t)
        ln = (0.13 + 0.03 * ((i * 7) % 3)) * s
        S.ell(f"mane{i}", add(c, [-0.01 * s, -0.02 * s - ln * 0.45, -0.085 * s]), [0.05 * s, ln, 0.032 * s], rot=[12, 0, -16 + 6 * (i % 3)], bone="neck", k=0.015 * s, kc=0.004, color="@mane", hair=0.45)
S.ell("forelock", H(0.1, 0.17) if Z else H(0.16, 0.19), [0.13 * L, 0.05 * L, 0.06 * L] if Z else [0.18 * L, 0.075 * L, 0.08 * L], rot=hf.rot(-20), bone="head", k=0.015 * s, kc=0.005, color="@mane", hair=0.8 if Z else 0.45)
# ---- forelegs: upper arm into the chest, the muscled forearm, knee, cannon with its tendon, fetlock, pastern, hoof
fx, fz = J["legFLu"]["o"][0], J["legFLu"]["o"][2]
kn, an = J["legFLl"]["o"][1], J["footFL"]["o"][1]
lp = {"pat": "bands", "frame": {"o": R3([fx, J["legFLu"]["o"][1], 0]), "u": [0, -1, 0], "r": round(0.07 * s, 3)}} if Z else {}
LG = ["@sock", "@leg"]
lpl = {"pat": "bands", "frame": {"o": R3([fx, kn, 0]), "u": [0, -1, 0], "r": round(0.045 * s, 3)}} if Z else {}
S.ell("arm", [fx - 0.02 * s, 1.0 * s, fz * 0.85], r3(0.13, 0.17, 0.09), rot=[0, 0, -25], bone="legFLu", k=(0.03 if Z else 0.08) * s, color=B, mirror=True, **pat)
S.ell("elbow", [fx - 0.12 * s, 0.93 * s, fz * 0.95], r3(0.07, 0.07, 0.065), bone="legFLu", k=(0.025 if Z else 0.04) * s, color=B, mirror=True, **lp)
S.cone("forearm", [fx - 0.04 * s, 0.92 * s, fz], [fx + 0.005 * s, kn + 0.03 * s, fz], 0.105 * s, 0.05 * s, bone="legFLu", k=0.04 * s, color=B, mirror=True, **lp)
S.ell("knee", [fx + 0.005 * s, kn - 0.01 * s, fz], r3(0.052, 0.06, 0.05), bone="legFLl", k=0.03 * s, color=LG, mirror=True, **lp)
S.cone("cannon", [fx + 0.005 * s, kn - 0.03 * s, fz], [fx + 0.005 * s, 0.215 * s, fz], 0.04 * s, 0.038 * s, bone="legFLl", k=0.025 * s, color=LG, mirror=True, **lp)
S.cone("tendon", [fx - 0.03 * s, kn - 0.06 * s, fz], [fx - 0.03 * s, 0.24 * s, fz], 0.024 * s, 0.027 * s, bone="legFLl", k=0.02 * s, color=LG, mirror=True, **lp)
S.ell("fetlock", [fx - 0.005 * s, 0.2 * s, fz], r3(0.058, 0.055, 0.048), bone="legFLl", k=0.025 * s, color=LG, mirror=True, **lp)
S.cone("pastern", [fx + 0.0 * s, 0.19 * s, fz], [fx + 0.03 * s, 0.1 * s, fz], 0.043 * s, 0.045 * s, bone="legFLl", k=0.02 * s, color=LG, mirror=True)
S.cone("hoof", [fx + 0.03 * s, 0.1 * s, fz], [fx + 0.045 * s, 0.012 * s, fz], 0.05 * s, 0.066 * s, bone="footFL", k=0.008 * s, kc=0.004, color="@foot", mirror=True)
# ---- hind legs: thigh into the haunch, the stifle forward, gaskin back to the hock's point, cannon, fetlock, hoof
hx, hz = J["legHLu"]["o"][0], J["legHLu"]["o"][2]
hk = J["legHLl"]["o"][1]
hp = hq
hpl = {"pat": "bands", "frame": {"o": R3([hx, hk, 0]), "u": [0, -1, 0], "r": round(0.045 * s, 3)}} if Z else {}
S.ell("thigh", [hx + 0.02 * s, 0.98 * s, hz], r3(0.2, 0.25, 0.12), rot=[0, 0, -12], bone="legHLu", k=(0.035 if Z else 0.08) * s, color=B, mirror=True, **hq)
S.ell("stifle", [hx + 0.19 * s, 0.93 * s, hz * 0.95], r3(0.09, 0.12, 0.085), rot=[0, 0, -15], bone="legHLu", k=(0.04 if Z else 0.06) * s, color=B, mirror=True, **hq)
S.cone("gaskin", [hx + 0.08 * s, 0.86 * s, hz], [hx - 0.04 * s, hk + 0.05 * s, hz], 0.1 * s, 0.055 * s, bone="legHLu", k=0.05 * s, color=B, mirror=True, **hp)
S.ell("hamstring", [hx - 0.07 * s, 0.8 * s, hz], r3(0.06, 0.19, 0.06), rot=[0, 0, -12], bone="legHLu", k=0.05 * s, color=B, mirror=True, **hp)
# (round 4: the back of the thigh run straight from the point of the buttock down to the point of the hock)
ham(S, J, [0.28, 0.95], [0.1, 0.25], 0.09 * s, 0.035 * s, B, 0.05 * s, zf=0.9, **hp)
S.ell("hock", [hx - 0.025 * s, hk - 0.01 * s, hz], r3(0.07, 0.065, 0.048), bone="legHLl", k=0.03 * s, color=LG, mirror=True, **hp)
S.sph("hockPt", [hx - 0.085 * s, hk + 0.035 * s, hz], 0.036 * s, bone="legHLl", k=0.03 * s, color=LG, mirror=True, **hp)
S.cone("hcannon", [hx - 0.02 * s, hk - 0.03 * s, hz], [hx, 0.215 * s, hz], 0.043 * s, 0.039 * s, bone="legHLl", k=0.025 * s, color=LG, mirror=True, **hp)
S.cone("htendon", [hx - 0.055 * s, hk - 0.05 * s, hz], [hx - 0.03 * s, 0.24 * s, hz], 0.024 * s, 0.027 * s, bone="legHLl", k=0.02 * s, color=LG, mirror=True, **hp)
S.ell("hfetlock", [hx - 0.01 * s, 0.2 * s, hz], r3(0.057, 0.054, 0.047), bone="legHLl", k=0.025 * s, color=LG, mirror=True, **hp)
S.cone("hpastern", [hx - 0.005 * s, 0.19 * s, hz], [hx + 0.025 * s, 0.1 * s, hz], 0.042 * s, 0.044 * s, bone="legHLl", k=0.02 * s, color=LG, mirror=True)
S.cone("hhoof", [hx + 0.025 * s, 0.1 * s, hz], [hx + 0.04 * s, 0.012 * s, hz], 0.048 * s, 0.063 * s, bone="footHL", k=0.008 * s, kc=0.004, color="@foot", mirror=True)
# ---- the tail: a short dock, then (a horse's) a fall of hair widening to the hocks, or (a zebra's) a thin tail to a long black tassel
t0 = J["tail"]["o"]
if Z:
    S.cone("tailDock", t0, add(t0, [-0.07 * s, -0.2 * s, 0]), 0.035 * s, 0.022 * s, bone="tail", k=0.02 * s, color=B, **hq)
    S.cone("tailStem", add(t0, [-0.07 * s, -0.2 * s, 0]), add(t0, [-0.1 * s, -0.42 * s, 0]), 0.022 * s, 0.018 * s, bone="tail", k=0.01 * s, color=B)
    S.ell("tassel", add(t0, [-0.115 * s, -0.56 * s, 0]), [0.035 * s, 0.17 * s, 0.03 * s], rot=[0, 0, -6], bone="tail", k=0.015 * s, kc=0.004, color="@mane", hair=0.8)
else:
    S.cone("tailDock", t0, add(t0, [-0.1, -0.2, 0]), 0.06, 0.045, bone="tail", k=0.03, color="@mane", hair=0.6)
    S.ell("tailFall", add(t0, [-0.14, -0.38, 0]), [0.06, 0.26, 0.04], rot=[0, 0, -8], bone="tail", k=0.03, kc=0.01, color="@mane", hair=0.9)
    S.ell("tailFall2", add(t0, [-0.16, -0.62, 0]), [0.085, 0.24, 0.035], rot=[0, 0, -4], bone="tail", k=0.03, kc=0.01, color="@mane", hair=0.9)
if Z:
    S.ell("ventral", P(0.0, 0.9), r3(0.42, 0.03, 0.05), rot=[0, 0, -6], k=0.02 * s, kc=0.006, color="@mane")
if Z: carriers(S)
eyes = {"at": R3(H(0.31, 0.07, 0.16)), "from": R3(H(0.31, 0.0, 0)), "r": round(0.023 * s, 4), "iris": "@eye", "pupil": "bar", "lid": "@nose", "sink": 0.45}
sc = {"_about": "", "keep": [], "mesh": {"tris": [7000, 2200]}, "shape": S.shapes, "eyes": eyes}
if not Z: sc["shade"] = {"on": "@body", "back": 0.6, "belly": 1.3, "k": 0.15, "at": 0.02, "low": 1.0, "lowAt": -0.36}   # (countershaded: the topline darker, the belly paler -- a factor of the coat, so every coat keeps its hue)
if Z:
    sc["_about"] = "a plains zebra on the horse frame at .85, stockier: the horse's body plan (see horse.json) with the stripes laid as a zebra's are -- upright on the trunk and the neck (the body frame), turned back over the haunch and lying down over the thigh (the hindquarter's own frame), rings on the legs (each leg's), fine bands down the face; a short stiff mane banded black and white, broad round ears, a dark muzzle"
    upd = {"params": {"s": 0.85, "mane": False}, "colors": {"nose": "#1e1a18", "earIn": "#e8e4da", "muzzle": "#2a2622"}, "tail": {"r1": "0.03*s", "r2": "0.022*s", "tuft": "0.07*s"}}
else:
    sc["_about"] = "THE HORSE (2026-11-05): the frame's rig drawn by shapes written for a horse -- a deep chest under high withers and sloping shoulder blades, the barrel to a short loin and a round croup over full haunches and the points of the buttocks; the neck deep at the chest, arching to the poll (a crest), narrow at the throatlatch; a long face from a broad flat forehead to a soft muzzle, round flat jowls behind, tall pointed ears; forearm, knee, cannon with its tendon, fetlock, sloped pastern and hoof in front, the stifle, gaskin and the hock's point behind; the mane in locks falling to the right, the forelock; the rig's own tail kept"
    upd = {"colors": {"nose": "#2e241e", "earIn": "#3a2a20", "sock": "#1e1814", "back": "#7a4a28", "flank": "#a0703f", "muzzle": "#5e4030"}, "params": {"s": 1, "mane": False}}
print(write(name, sc, upd), len(S.shapes), "shapes")
