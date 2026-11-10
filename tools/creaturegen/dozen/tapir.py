# THE TAPIR (2026-11-09, the Brazilian / lowland tapir): the pig at 1.25 (1 m at the shoulder, 2 m long), the rump
# rounded and high, a short erect crest of mane from the crown down the neck, the pig's disc snout drawn out into a
# short drooping proboscis (a tube from the face, bending down past the jaw, the nostrils under its tip), small round
# short rounded upright ears, pale-edged, a stub of a tail; dark grey-brown, the cheeks and throat paler. Variant `calf` (.45):
# the young's pale stripes and spots (the `stripes` and `dots` patterns over its coat). Written whole by this script.
import sys, os, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dlib import *

f = 1.25
d = load("mammals/pig"); scale_def(d, f)
d["name"] = "tapir"; d["graze"] = 0.6; d["rest"] = 0.8; d["shy"] = 10
d.pop("mount", None); d.pop("young", None); d.pop("beg", None); d.pop("_quality", None); d.pop("_coats", None)
d["params"] = {"calf": False}
d["_about"] = ("THE TAPIR (2026-11-09, tools/creaturegen/dozen/tapir.py): the pig at 1.25, a rounded high rump, an erect crest down the "
               "neck, a short drooping proboscis, small round pale-edged ears, a stub tail; dark grey-brown, paler cheeks and throat; "
               "variant `calf` (.45) striped and spotted. Written whole by its script.")
# ---- the body: high round rump, a deeper barrel, no teats
drop(d, "teats")
grow(d, "rump", 1.12, 1.15, 1.05); move(d, "rump", 0, 0.03)
grow(d, "loin", 1.0, 1.2); move(d, "loin", -0.02, 0.03)
grow(d, "ham", 1.0, 1.08)
# ---- the crest: a ridge of hair from the crown to the withers
# (the centres ride the body's top line: the crown, the dip of the neck, up over the withers)
for i, (x, y) in enumerate([(1.06, 0.96), (0.96, 0.975), (0.86, 0.96), (0.74, 0.975), (0.6, 1.02), (0.46, 1.13)]):
    add(d, {"id": f"crest{i}", "type": "ell", "bone": "head" if i < 2 else ("neck" if i < 4 else "body"), "c": [x, y, 0.0], "r": [0.075, 0.055, 0.018], "k": 0.03, "color": "@crest", "hair": 0.9})
# the back one convex arc from the withers to the rump, no saddle
over(d, "back", c=[0.0, 1.0, 0.0], r=[0.5, 0.16, 0.26])
# ---- the proboscis: from the face, out and down past the jaw; the nostrils under its tip
drop(d, "disc", "nostril")
over(d, "snout", c=[1.33, 0.665, 0], r=[0.07, 0.085, 0.085], rot=[0, 0, -10])
add(d, {"id": "trunk", "type": "tube", "bone": "head", "pts": [[1.3, 0.67, 0, 0.085], [1.41, 0.655, 0, 0.072], [1.49, 0.615, 0, 0.06], [1.54, 0.56, 0, 0.05], [1.555, 0.5, 0, 0.042]],
        "k": 0.02, "color": "@snout"}, after="snout")
add(d, {"id": "trunkTip", "type": "ell", "bone": "head", "c": [1.555, 0.49, 0], "r": [0.045, 0.03, 0.045], "k": 0.01, "color": "@nose"}, after="trunk")
add(d, {"id": "nostril", "type": "sphere", "bone": "head", "c": [1.56, 0.47, 0.022], "r": 0.012, "k": 0.004, "op": "sub", "color": "@nostril", "mirror": True}, after="trunkTip")
over(d, "lip", c=[1.3, 0.56, 0], r=[0.08, 0.035, 0.06])
over(d, "face", b=[1.26, 0.69, 0])
d["muzzle"] = [1.16, 0.68, 0, 1.5, 0.6, 0, 0.17, 0.09]; d["nose"] = [1.55, 0.5, 0, 0.045]
# ---- the ears: short rounded ovals standing out of the skull's top-rear corner, above and behind the eye; solid (4 cm
# thick) so they never thin to a sliver edge-on; dark, the top edge painted pale (no separate rim piece)
drop(d, "ear")
add(d, {"id": "ear", "type": "ell", "bone": "head", "c": [1.0, 0.93, 0.145], "r": [0.045, 0.08, 0.028], "rot": [25, 0, -10], "k": 0.03, "color": "@ear", "mirror": True}, after="cranium")
add(d, {"id": "earEdge", "type": "ell", "bone": "head", "c": [1.0, 0.995, 0.158], "r": [0.042, 0.026, 0.032], "rot": [25, 0, -10], "k": 0.004, "kc": 0.006, "op": "paint", "color": "@earRim", "mirror": True}, after="ear")
# (2026-11-10: out at the skull's upper side where it is only 5 cm wide at that height, so the ear stands 10 cm proud and
#  clear of the crest -- centred ON the crown it was buried in the ridge, a white nub)
d["ears"] = [1.0, 0.86, 0.135, 1.0, 1.0, 0.16, 0.045, 0.025]
# ---- the tail: a stub
d["tail"] = {"c": [-0.76, 0.84], "R": 0.06, "a0": 0.3, "a1": -1.2, "r1": 0.02, "r2": 0.01, "n": 3, "sway": 12, "speed": 1.0}
add(d, {"id": "tail", "type": "cone", "bone": "tail", "a": [-0.73, 0.86, 0], "b": [-0.8, 0.8, 0], "ra": 0.022, "rb": 0.01, "k": 0.015, "color": "@tail"})
# ---- colours
recolor(d, body="#4a423c", back="#443c36", muzzle="#3e3632", ear="#4e4642", leg="#3e3632", tail="#3e3632", eye="#1e1612", nose="#2a2522", nostril="#1a1614", foot="#2a2420",
        snout="#3e3632", joint="#443c36", cheek="#8a8078", throat="#7a7068", earRim="#e8e4de", earIn="#6a605a", crest="#2a2624", pale="#c8bca8")
for i in ("cheek",): shape(d, i)["color"] = "@cheek"
for i in ("jowl", "jowlFold"): shape(d, i)["color"] = "@throat"
# the calf: striped and spotted over a browner coat
BODY = ("barrel", "back", "loin", "shoulderTop", "rump", "ham", "shoulder", "belly", "neck", "thigh", "arm")
for i in BODY: shape(d, i)["pat"] = [{"when": "calf", "v": "stripes"}]
d["coats"] = [{"name": "grey-brown"}]
d["variants"] = {"calf": {"params": {"calf": True}, "scale": 0.45,
                          "colors": {"body": "#5a4a3c", "back": "#4e4036", "cheek": "#8a7a68", "throat": "#7a6a58", "leg": "#4a3e34", "muzzle": "#4a3e34", "snout": "#4a3e34"},
                          "sculpt": {"shape": [{"id": f"crest{i}", "drop": True} for i in range(6)]}}}
d["_variants"] = "VARIANTS: `calf` -- .45, no crest, pale stripes along the body (the `stripes` pattern gated on `calf`)"
save("mammals/tapir", d)
index_add("creatures/mammals/tapir", "Mammals")
if "--shot" in sys.argv: render("creatures/mammals/tapir", "tapir")
