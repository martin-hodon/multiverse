# THE GREEN SEA TURTLE (2026-11-09): the pond turtle (others/turtle, a `parts` rig) at 3.2 -- 1 m of shell -- then a sea
# turtle's: the carapace flattened and drawn out long, its raised scute plates gone (a sea turtle's are flat: the seams
# stay as lines), the fore legs long swept-back scythe FLIPPERS and the hind legs short rounded paddles (each one `fin` sheet on
# its leg bone, rooted under the shell, so they still beat with the leg's swing), no claws, a bigger blunt head that cannot draw in, the hooked beak kept.
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
# ---- the FLIPPERS (2026-11-18): each limb ONE sheet rooted under the shell's margin -- no leg tube showing (a tube with
# a sheet hung on it read as a leg carrying a sail). Planform in body space (x forward, z out to the left), y beside it.
# The fore flipper a long narrow scythe, ~half the carapace long: its leading edge blunt (the arm's bones run in it,
# bluntness 2.4) sweeping out and back to a pointed tip, the trailing edge thin and a little hollow; one small claw on
# the leading edge. The hind flipper a short rounded paddle trailing beside the tail. Both swell toward the root
# (`swell`: as deep as the limb they grew from) and are faired into the body.
drop(d, "legF", "footF", *[f"clawF{j}" for j in range(5)], "legH", "footH", *[f"clawH{j}" for j in range(4)])
def flip(id, bone, root, le, tip, te, y, thick, swell, **kw):
    """a flipper sheet: le / te the leading and trailing edges (x, z) from the root out, tip (x, z); y(z) its height"""
    edge = [[x, y(z), z, 2.4] for x, z in le] + [[tip[0], y(tip[1]), tip[1], 1]] + [[x, y(z), z, 1] for x, z in te[::-1]]
    add(d, {"id": id, "type": "fin", "bone": bone, "root": [[x, y(z), z] for x, z in root], "edge": edge, "corners": [len(le)],
            "thick": thick, "slope": 0.55, "grid": "flow", "swell": swell, "color": "@skin", "pat": "scales",
            "rim": 0.012, "rimColor": "@chin", "fair": {"r": 0.035}, "mirror": True, **kw}, after="dome")
fy = lambda z: 0.125 - 0.03 * max(0.0, z - 0.3)                      # (held level and flat, the far blade a little lower)
flip("flipper", "legFL", root=[(0.30, 0.22), (0.16, 0.23)],
     le=[(0.32, 0.29), (0.345, 0.37), (0.34, 0.45), (0.315, 0.53), (0.265, 0.61), (0.19, 0.68), (0.10, 0.735)],
     tip=(-0.02, 0.77),
     te=[(0.19, 0.29), (0.205, 0.37), (0.195, 0.45), (0.17, 0.53), (0.13, 0.61), (0.075, 0.68), (0.02, 0.735)],
     y=fy, thick=0.026, swell=[0.05, 0.16, 0.5])
add(d, {"id": "flipperClaw", "type": "horn", "bone": "legFL", "pts": [[0.315, fy(0.53) + 0.003, 0.53, 0.005], [0.33, fy(0.54) + 0.002, 0.55, 0.001]],
        "color": "@claw", "mirror": True}, after="flipper")
hy = lambda z: 0.115 - 0.03 * max(0.0, z - 0.25)
flip("hindFlipper", "legHL", root=[(-0.20, 0.20), (-0.34, 0.20)],
     le=[(-0.215, 0.27), (-0.25, 0.34), (-0.30, 0.40), (-0.36, 0.445)],
     tip=(-0.43, 0.46),
     te=[(-0.37, 0.25), (-0.42, 0.29), (-0.46, 0.34), (-0.47, 0.40)],
     y=hy, thick=0.02, swell=[0.04, 0.12, 0.5])
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
