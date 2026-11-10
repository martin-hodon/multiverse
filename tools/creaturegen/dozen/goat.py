# THE DOMESTIC GOAT (2026-11-09): the ibex (the deer frame at .826, bulk 1.37) brought to a goat's .72 (about .75 m at
# the withers), its sculpt scaled the same; the ibex's great knobbed scimitars replaced by short horns swept back over
# the neck (billy ~18 cm, nanny ~10 cm, the kid's buds kept); the ears drooped outward, horizontal; the tail short and
# carried up; the beard kept (billy). A white coat as the base, coats brown, black, pied (the `pinto` patches gated on
# `pied`) and grey; variants nanny and kid as the ibex's. Written whole by this script.
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dlib import *

S_IBEX, S = 0.826, 0.72
f = S / S_IBEX
d = load("mammals/ibex")
d["params"]["s"] = S
d["params"]["pied"] = False; d["params"]["plain"] = True
scale_sculpt(d["sculpt"], f)
d["name"] = "goat"; d["shy"] = 8; d["graze"] = 1.1
d["_about"] = ("THE GOAT (2026-11-09, tools/creaturegen/dozen/goat.py): the ibex at .72 of the deer frame, its sculpt scaled; short "
               "swept-back horns (billy 18 cm, nanny 10 cm, the kid's buds), drooped horizontal ears, a short upright tail, the billy's beard; "
               "a white base coat, coats brown, black, pied (pinto patches gated on `pied`), grey; variants nanny (.78) and kid (.45). Written whole by its script.")
d["_variants"] = "VARIANTS (species.js variantDef): `nanny` -- .78 the billy's size, short horns, no beard; `kid` -- .45, horn buds"

# ---- horns: a short curve back and up from the ibex's root, the section a little flattened (aspect .82 as the ibex's)
def horn(root, back, up, out, r0, n=9):
    pts = []
    for i in range(n):
        t = i / (n - 1)
        x = root[0] - back * t * t ** 0.6          # (sweeping back faster toward the tip)
        y = root[1] + up * (t - 0.35 * t * t)      # (rising, then levelling)
        z = root[2] + out * t
        r = r0 * (1 - t) ** 0.9 if i < n - 1 else 0.0
        pts.append([round(x, 4), round(y, 4), round(z, 4), round(r, 4), 0.82])
    return pts
rootB = shape(d, "hornB")["pts"][0][:3]
over(d, "hornB", pts=horn(rootB, back=0.12, up=0.12, out=0.03, r0=0.026))
rootN = shape(d, "hornN")["pts"][0][:3]
over(d, "hornN", pts=horn(rootN, back=0.07, up=0.07, out=0.02, r0=0.013, n=7))
# (the kid's buds stay)

# ---- the ears: a goat's -- long leaves standing out level from the side of the head, the tip a little down, the hollow forward
e = shape(d, "ear")
bl = fin_blade([0.638, 0.925, 0.05], [-0.35, 0.6, 0.35], [0.0, -0.5, 0.85], L=0.15, W=0.05, tipness=0.6)   # (out and down, the face turned forward-out: it shows from the front 3/4 and the side alike)
e.update(bl); e["face"] = [0.8, 0.35, 0.45]; e["cup"] = 0.4; e["thick"] = 0.007; e["fair"] = {"r": 0.012, "sink": 3}
d["ears"] = [0.638, 0.925, 0.05, 0.65, 0.85, 0.16, 0.04, 0.012]

# ---- a goat's trunk, not an ibex's: slimmer through the chest, neck and barrel
for i in ("chest", "withers", "barrel", "loin", "rump", "haunch", "belly", "girth", "neckBase", "neck", "throat", "chestFront", "bellyPale", "scapula", "breast"): grow(d, i, 1.0, 0.92, 0.86)
for i in ("rump", "haunch", "loin"): grow(d, i, 1.0, 0.94, 0.92)   # the ibex's heavy quarters eased off
# ---- the tail: short, carried up over the rump
t = shape(d, "tail"); t["c"] = [-0.555, 0.735, 0.0]; t["r"] = [0.018, 0.05, 0.02]; t["rot"] = [0, 0, 35]
td = shape(d, "tailDock"); td["pts"] = [[-0.49, 0.682, 0.0, 0.03], [-0.53, 0.705, 0.0, 0.024], [-0.555, 0.725, 0.0, 0.018]]
d["tail"] = {"c": [-0.52, 0.64], "R": 0.1, "a0": 1.2, "a1": 1.9, "r1": 0.028, "r2": 0.016, "n": 3, "sway": 14, "speed": 0.9}

# ---- the coat: the body's shapes take the pied patches when the coat says so
for s in shapes(d):
    if s.get("pat") == "coarse": s["pat"] = [{"when": "pied", "v": "pinto"}]   # (plain: no pattern -- the ibex's coarse grizzle made a sheep of it)

# ---- colours: a white goat; the horns grey-brown, the hooves dark, pink in the ears
recolor(d, body="#e9e4da", front="#e2dcd0", neck="#e6e0d5", head="#e6e0d5", muzzle="#d9d2c6", ear="#ddd6ca", leg="#dcd5c9", foot="#3a3129",
        tail="#e2dcd0", belly="#f1ede5", throat="#e2dcd0", patch="#f1ede5", nose="#4a4038", chin="#d9d2c6", gland="#e6e0d5", earIn="#e9c9bf",
        upleg="#dcd5c9", ring="#f1ede5", back="#e0dacf", tailc="#e2dcd0", earTip="#cfc8bc", black="#3a3129", hornc="#8a8070", hornTip="#4e463c",
        brow="#e6e0d5", throatW="#f1ede5", limb="#dfd8cc", stripe="#cfc8bc", mask="#e6e0d5", beard="#d9d2c6")
d["coats"] = [
  {"name": "white"}, {"name": "white"},
  {"name": "brown", "body": "#7a5a3c", "front": "#5e4430", "neck": "#76563a", "head": "#6e5036", "muzzle": "#8a6e52", "ear": "#6e5036", "leg": "#4a3626", "tail": "#4a3626",
   "belly": "#9a8064", "throat": "#6e5036", "patch": "#9a8064", "chin": "#8a6e52", "gland": "#6e5036", "upleg": "#5e4430", "ring": "#9a8064", "back": "#6a4c32", "tailc": "#4a3626",
   "earTip": "#4a3626", "brow": "#6e5036", "throatW": "#8a6e52", "limb": "#6a4c32", "stripe": "#3e2c1e", "mask": "#6e5036", "beard": "#4a3626", "hornc": "#5a5046", "earIn": "#c8a898"},
  {"name": "black", "body": "#2e2a28", "front": "#262220", "neck": "#2e2a28", "head": "#2a2624", "muzzle": "#3a3634", "ear": "#2a2624", "leg": "#201c1a", "tail": "#201c1a",
   "belly": "#3a3634", "throat": "#2a2624", "patch": "#3a3634", "chin": "#3a3634", "gland": "#2a2624", "upleg": "#262220", "ring": "#3a3634", "back": "#262220", "tailc": "#201c1a",
   "earTip": "#1a1614", "brow": "#2a2624", "throatW": "#3a3634", "limb": "#262220", "stripe": "#1a1614", "mask": "#2a2624", "beard": "#201c1a", "hornc": "#4a443e", "earIn": "#6a5a54"},
  {"name": "pied", "params": {"pied": True, "plain": False}},
  {"name": "grey", "body": "#a8a49c", "front": "#8e8a82", "neck": "#a4a098", "head": "#9a968e", "muzzle": "#b4b0a8", "ear": "#9a968e", "leg": "#7a766e", "tail": "#7a766e",
   "belly": "#c4c0b8", "throat": "#9a968e", "patch": "#c4c0b8", "chin": "#b4b0a8", "gland": "#9a968e", "upleg": "#8e8a82", "ring": "#c4c0b8", "back": "#949088", "tailc": "#7a766e",
   "earTip": "#6a665e", "brow": "#9a968e", "throatW": "#b4b0a8", "limb": "#8e8a82", "stripe": "#5a564e", "mask": "#9a968e", "beard": "#7a766e", "hornc": "#6a6258", "earIn": "#c8b0a8"},
]
for v in d["variants"].values(): v.pop("colors", None)   # (the nanny and the kid in the coat picked, not the ibex's browner tones)
save("mammals/goat", d)
index_add("creatures/mammals/goat", "Mammals")
if "--shot" in sys.argv: render("creatures/mammals/goat", "goat")
