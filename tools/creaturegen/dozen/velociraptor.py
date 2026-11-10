# THE VELOCIRAPTOR (2026-11-09) -- the one people expect, Jurassic Park's: 4 m long, the head at 1.5 m. The dilophosaurus
# at .6, then: the crests gone, a longer, lower snout and bigger eyes, a longer stiff tail, longer arms with the
# three-fingered hands further out, and on each foot the second (inner) toe held up off the ground with a big curved
# SICKLE CLAW. Tan with a darker back, a pale belly, amber eyes; a grey-green coat too.
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dlib import *

S = 0.6
d = load("dinosaurs/dilophosaurus")
scale_def(d, S)
d["name"] = "velociraptor"
d["mount"] = {"h": 2.4, "speed": 2.2}
d["headTurn"] = 16
# ---- the head: crests gone; the snout drawn out 1.25x from the cranium, lower; the eyes bigger
drop(d, "crest")
cx = shape(d, "cranium")["c"][0]
for i in ids(d):
    s = shape(d, i)
    if s.get("bone") == "head" and i not in ("cranium",):
        for k in ("c",):
            if k in s: s[k] = [cx + (s[k][0] - cx) * 1.25, s[k][1], s[k][2]]
        if "r" in s and isinstance(s["r"], list) and i in ("snout", "jaw", "jawPale", "roof", "jawBack"): s["r"] = [s["r"][0] * 1.25, s["r"][1], s["r"][2]]
        if "pts" in s: s["pts"] = [[cx + (p[0] - cx) * 1.25] + p[1:] for p in s["pts"]]
over(d, "snout", r=[shape(d, "snout")["r"][0], shape(d, "snout")["r"][1] * 0.9, shape(d, "snout")["r"][2] * 0.95])
d["sculpt"]["eyes"]["r"] = 0.021; d["eyes"][3] = 0.026
for e in d["extras"]:
    if e.get("id") in ("snout", "jaw", "brow"):
        for k in ("from", "to"):
            if k in e: e[k] = [cx + (e[k][0] - cx) * 1.25] + e[k][1:]
        if "ell" in e: e["ell"] = [cx + (e["ell"][0] - cx) * 1.25, e["ell"][1], e["ell"][2], e["ell"][3] * 1.25] + e["ell"][4:]
# ---- the tail: 1.2x longer, stiff and straight
tx = -0.22 * S
for i in ids(d, r"^tail"):
    s = shape(d, i)
    if "pts" in s: s["pts"] = [[tx + (p[0] - tx) * 1.2] + p[1:] for p in s["pts"]]
    if "c" in s: s["c"] = [tx + (s["c"][0] - tx) * 1.2] + s["c"][1:]; s["r"] = [s["r"][0] * 1.2] + s["r"][1:]
T = d["tail"]; T["c"][1] -= T["R"] * 0.2; T["R"] *= 1.2; T["sway"] = 4
# ---- the arms: 1.4x longer from the shoulder, the hand with them (its fingers and claws moved by the hand's shift, grown 1.15)
sh = [1.22 * S, 1.4 * S, 0.22 * S]
L = lambda p: [sh[i] + (p[i] - sh[i]) * 1.4 for i in range(3)] + list(p[3:])
old_hand = shape(d, "fore")["b"]
for i in ("arm", "fore"):
    s = shape(d, i); s["a"] = L(s["a"]); s["b"] = L(s["b"]); s["ra"] *= 1.1; s["rb"] *= 1.1
for e in d["extras"]:
    if e.get("id") in ("arm", "fore"): e["from"] = L(e["from"]); e["to"] = L(e["to"]); e["r1"] *= 1.1; e["r2"] *= 1.1
new_hand = shape(d, "fore")["b"]
dv = [new_hand[i] - old_hand[i] for i in range(3)]
for i in ids(d, r"^(palm|finger|fclaw)"):
    s = shape(d, i)
    g = lambda p: [new_hand[j] + (p[j] + dv[j] - new_hand[j]) * 1.15 for j in range(3)] + list(p[3:])
    if "c" in s: s["c"] = g(s["c"]); s["r"] = [v * 1.15 for v in s["r"]]
    if "pts" in s: s["pts"] = [g(p) for p in s["pts"]]
# ---- the sickle claw: the inner toe (toe2) short and held up, its claw a big curved horn clear of the ground
z = 0.3 * S
over(d, "toe2", pts=[[0.026, 0.036, z, 0.034], [0.085, 0.062, z - 0.03, 0.03], [0.14, 0.092, z - 0.05, 0.024]])
zc = z - 0.05
over(d, "claw2", pts=[[0.122, 0.082, zc, 0.019], [0.165, 0.128, zc, 0.019], [0.212, 0.162, zc, 0.016], [0.262, 0.162, zc, 0.012], [0.302, 0.128, zc, 0.0075], [0.322, 0.085, zc, 0.003], [0.327, 0.062, zc, 0.0]],
     up=[0, 0, 1], aspect=0.8, fair={"r": 0.008, "skin": 0.2}, tipAt=0.5, color="#1a1510")
# (the thigh: a leaner animal's -- the round thigh ell of the base stood off the hip as a ball)
th = shape(d, "thigh"); th["r"] = [th["r"][0] * 0.92, th["r"][1] * 0.95, th["r"][2] * 0.8]; th["k"] *= 1.6; th["c"] = [th["c"][0], th["c"][1], th["c"][2] * 0.9]
pm = shape(d, "premax"); over(d, "premax", c=[pm["c"][0] + 0.01, pm["c"][1] + 0.009, 0.0], r=[0.05, 0.034, 0.03], k=0.03)   # (the snout tip blended into the snout box, not a knob under it)
# the middle and outer claws a little bigger too
for i in ("claw0", "claw1"): grow(d, i, 1.25)
d["legs"]["toes"]["n"] = 3
# ---- the colours: tan, a darker back, a pale belly, amber eyes; coats tan and grey-green
recolor(d, body="#9a8358", front="#9a8358", neck="#9a8358", head="#8c7650", muzzle="#9a8358", leg="#8a7650", foot="#5a4a32", tail="#9a8358",
        back="#5a4530", flank="#a89468", belly="#d8ccaa", lip="#7a6648", claw="#1e1812", lid="#5a4a36", brow="#6a5640", eye="#d9a830", crest=None, crestRim=None)
d["coats"] = [{"name": "tan"}, {"name": "tan"},
              {"name": "grey-green", "body": "#6e7a5a", "front": "#6e7a5a", "neck": "#6e7a5a", "head": "#626e50", "muzzle": "#6e7a5a", "leg": "#626e50", "tail": "#6e7a5a", "back": "#3e4a34", "flank": "#7c886a", "belly": "#c4c8a6", "lip": "#56624a", "brow": "#4a5640"},
              {"name": "rust", "body": "#9a6a44", "front": "#9a6a44", "neck": "#9a6a44", "head": "#8a5c3c", "muzzle": "#9a6a44", "leg": "#8a5c3c", "tail": "#9a6a44", "back": "#5a3a24", "flank": "#aa7c54", "belly": "#e0cfae", "lip": "#7a5236", "brow": "#6a4a30"}]
d["_about"] = ("THE VELOCIRAPTOR (2026-11-09, tools/creaturegen/dozen/velociraptor.py) -- the film's, 4 m long and 1.5 m at the head, not the turkey-sized "
               "real one: the dilophosaurus at .6, its crests gone, the snout drawn out 1.25x and lower, bigger amber eyes, the tail 1.2x longer and stiff, "
               "the arms 1.4x longer with the hands moved out on them, and the inner toe of each foot held up with a big curved sickle claw (a `horn`). "
               "Tan with a dark back and pale belly; grey-green and rust coats. Written whole by its script; nothing patches it after.")
save("dinosaurs/velociraptor", d)
index_add("creatures/dinosaurs/velociraptor", "Dinosaurs")
if "--shot" in sys.argv: render("creatures/dinosaurs/velociraptor", "velociraptor", views=tuple(sys.argv[sys.argv.index("--shot") + 1].split(",")) if len(sys.argv) > sys.argv.index("--shot") + 1 else ("side", "front", "q", "rear", "head", "feet"))
