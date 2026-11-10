# THE GREEN SEA TURTLE (2026-11-09): the pond turtle (others/turtle, a `parts` rig) at 3.2 -- 1 m of shell -- then a sea
# turtle's: the carapace flattened and drawn out long, its raised scute plates gone (a sea turtle's are flat: the seams
# stay as lines), the fore legs long swept-back FLIPPERS (one `fin` sheet each on the leg bone, so they still beat with
# the leg's swing), the hind legs short paddles, no claws, a bigger blunt head that cannot draw in, the hooked beak kept.
# Olive-brown shell, pale yellow plastron, greenish-grey skin; loggerhead and hawksbill coats.
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dlib import *

S = 3.2
d = load("others/turtle")
scale_def(d, S)
d["name"] = "sea turtle"
d["flags"] = {"shy": 3.5, "shore": True, "print": "paw", "legLen": 0.19 * S, "swim": True}
# ---- the carapace: 1.25 long, .6 high, 1.05 wide about the dome's centre; the body part's own scale with it
y0 = 0.034 * S
FX, FY, FZ = 1.25, 0.6, 1.05
def aff(p): return [p[0] * FX, y0 + (p[1] - y0) * FY, p[2] * FZ] + list(p[3:])
shell_ids = [i for i in ids(d) if not shape(d, i).get("bone")]
drop(d, *[i for i in shell_ids if i.startswith(("vert", "cost", "mst", "serr"))])   # (the raised scutes and their streaks: flat on a sea turtle)
for i in [i for i in ids(d) if not shape(d, i).get("bone")]:
    s = shape(d, i)
    if "c" in s: s["c"] = aff(s["c"])
    if "pts" in s: s["pts"] = [aff(p) for p in s["pts"]]
    for k in ("a", "b"):
        if k in s: s[k] = aff(s[k])
    if i == "dome": s["r"] = [s["r"][0] * FX, s["r"][1] * FY, s["r"][2] * FZ]
    if i == "plastron": s["r"] = [s["r"][0] * FX, s["r"][1] * FY, s["r"][2] * FZ]
    if i == "plastronRim": s["r"] = [s["r"][0] * FX, s["r"][1], s["r"][2] * FZ]
    if i.startswith("marg"): s["r"] = [s["r"][0], s["r"][1] * 0.8, s["r"][2]]
body = next(p for p in d["parts"] if p["id"] == "body")
body["scale"] = [body["scale"][0] * FX, body["scale"][1] * FY, body["scale"][2] * FZ]
# the shell's radiating pattern: four pale streaks a side fanning back over the costals (paints: thin flat ells on the dome)
for j, (x, zz, ang) in enumerate([(0.07, 0.055, -20), (0.02, 0.07, -5), (-0.03, 0.07, 8), (-0.075, 0.055, 24)]):
    add(d, {"id": f"ray{j}", "type": "ell", "c": aff([x * S, 0.105 * S, zz * S]), "r": [0.045 * S, 0.0012 * S, 0.006 * S], "rot": [30, ang, 0], "k": 0.001 * S, "kc": 0.0012 * S, "color": "@streak", "mirror": True}, after="dome")
# ---- the head: a third bigger, blunt; the red ear patch gone (a plain dark scale); the neck thicker
hc = shape(d, "head")["c"]
for i in ids(d):
    s = shape(d, i)
    if s.get("bone") == "head":
        if "c" in s: s["c"] = [hc[j] + (s["c"][j] - hc[j]) * 1.3 for j in range(3)]
        if isinstance(s.get("r"), list): s["r"] = [v * 1.3 for v in s["r"]]
        if "pts" in s: s["pts"] = [[hc[j] + (p[j] - hc[j]) * 1.3 for j in range(3)] + p[3:] for p in s["pts"]]
e = d["sculpt"]["eyes"]
for k in ("at", "from"): e[k] = [hc[j] + (e[k][j] - hc[j]) * 1.3 for j in range(3)]
e["r"] *= 1.3
over(d, "ear", color="@skin")
n = shape(d, "neck"); n["pts"] = [[p[0], p[1], p[2], p[3] * 1.3] for p in n["pts"]]
# ---- the fore flippers: the leg tube kept short as the shoulder, the foot and claws gone, one swept-back fin sheet a side
drop(d, "footF", *[f"clawF{j}" for j in range(5)])
sh = [0.07 * S, 0.04 * S, 0.068 * S]
over(d, "legF", pts=[[sh[0], sh[1], sh[2], 0.0145 * S], [sh[0] + 0.03 * S, sh[1] - 0.005 * S, sh[2] + 0.05 * S, 0.014 * S]], pat=None)
R = lambda x, y, z: [sh[0] + x * S, sh[1] + y * S, sh[2] + z * S]
add(d, {"id": "flipper", "type": "fin", "bone": "legFL",
        "root": [R(0.045, 0.0, 0.02), R(-0.03, -0.004, 0.025)],
        "edge": [R(0.05, 0.0, 0.03), R(0.05, 0.002, 0.07), R(0.035, 0.004, 0.105), R(0.005, 0.006, 0.135), R(-0.035, 0.006, 0.152),
                 R(-0.055, 0.006, 0.14), R(-0.06, 0.004, 0.11), R(-0.05, 0.0, 0.075), R(-0.038, -0.003, 0.04)],
        "corners": [4], "thick": 0.012 * S, "slope": 0.28, "color": "@skin", "pat": "scales", "fair": {"r": 0.01 * S}, "camber": 0.04, "mirror": True}, after="legF")
# ---- the hind paddles: a shorter leg, a flat oval foot, no claws
drop(d, *[f"clawH{j}" for j in range(4)])
hp = [-0.07 * S, 0.038 * S, 0.068 * S]
over(d, "legH", pts=[[hp[0], hp[1], hp[2], 0.02 * S], [hp[0] - 0.02 * S, hp[1] - 0.006 * S, hp[2] + 0.04 * S, 0.016 * S]])
over(d, "footH", c=[hp[0] - 0.04 * S, hp[1] - 0.012 * S, hp[2] + 0.058 * S], r=[0.036 * S, 0.006 * S, 0.052 * S], rot=[0, 30, 0])   # (overlapping the shell margin: no gap)
for p in d["parts"]:
    if p["id"].startswith("legF"): p["anim"] = {"axis": "x", "deg": 22, "speed": 0.6, "phase": 0.0}   # (the flippers beat up and down together)
    if p["id"].startswith("legH"): p["anim"] = {"axis": "z", "deg": 10, "speed": 0.6, "phase": 3.1416}
recolor(d, shell="#5a5a3a", shell2="#6a6a44", seam="#2e2e1c", streak="#8c8c5c", plastron="#d8d0a8", skin="#6e7a5a", chin="#a8b088", yellow="#9aa86a", red="#6e7a5a", beak="#3a3a2a", claw="#2a2618", eye="#3a3020")
d["coats"] = [{"name": "green turtle"}, {"name": "green turtle"},
              {"name": "loggerhead", "shell": "#7a5a3a", "shell2": "#8a6a44", "seam": "#3a2a1a", "streak": "#9c7c58", "plastron": "#e0cc9a", "skin": "#8a7a5a", "chin": "#b8a888", "yellow": "#a89870", "red": "#8a7a5a", "scale": 0.95},
              {"name": "hawksbill", "shell": "#6a4a2a", "shell2": "#8a6a3a", "seam": "#2a1a0a", "streak": "#c09a58", "plastron": "#e8d8a8", "skin": "#5a6048", "chin": "#a8a888", "yellow": "#b0a068", "red": "#5a6048", "scale": 0.85}]
d["_about"] = ("THE GREEN SEA TURTLE (2026-11-09, tools/creaturegen/dozen/seaturtle.py): the pond turtle at 3.2, its carapace flattened (.6) and drawn out (1.25) "
               "with the raised scutes gone and pale rays over the costals, the fore legs one swept-back `fin` flipper each on the leg bone (beating up and down), "
               "the hind legs short paddles, no claws, the head a third bigger and blunt, the hooked beak kept. Olive-brown shell, pale plastron, greenish-grey "
               "skin; loggerhead and hawksbill coats. Written whole by its script; nothing patches it after.")
save("sea/sea-turtle", d)
index_add("creatures/sea/sea-turtle", "Sea life")
if "--shot" in sys.argv: render("creatures/sea/sea-turtle", "seaturtle", views=("side", "front", "q", "rear", "head", "top"))
