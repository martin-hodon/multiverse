from bg import *
from flier import rig_wings, wing, tail_fan
d = load("parrot")
d["_about"] = "a scarlet macaw in flight: a slim scarlet body, the big head with its bare white face and the massive hooked beak (pale horn above, black below), long pointed wings -- scarlet at the shoulder, yellow median coverts tipped green, blue secondaries and primaries -- and the long graduated tail, scarlet with blue tips; grey zygodactyl feet drawn up"
d["colors"] = {"red": "#d2261c", "deep": "#a81810", "yellow": "#f2c21a", "green": "#2f9a3a", "blue": "#1f4fb4", "navy": "#17338a",
               "face": "#f2eee6", "horn": "#e8dcc6", "black": "#151312", "foot": "#6a6460", "eye": "#e8e0b0", "olive": "#a89a3a", "oliveTip": "#6a6a2a",
               "breast": "#d2261c", "lines": "#b01830"}
d["params"] = {"lines": False}   # (the green-winged's and the blue-and-yellow's: rows of tiny feathers across the bare face)
# (COATS, picked by seed in game: the macaws -- scarlet (the asset's own), blue-and-yellow, green-winged, hyacinth)
d["coats"] = [{"name": "scarlet macaw"},
    {"name": "blue-and-yellow macaw", "params": {"lines": True}, "lines": "#1c1a1a", "red": "#1f6ec4", "deep": "#16509a", "breast": "#f2b41a", "yellow": "#1f6ec4", "green": "#1a5aa8", "blue": "#1a56b0", "navy": "#123a80",
     "horn": "#1a1818", "olive": "#c8a420", "oliveTip": "#8a7018"},
    {"name": "green-winged macaw", "params": {"lines": True}, "red": "#a3122c", "deep": "#740c1e", "breast": "#a3122c", "yellow": "#2a9a4c", "green": "#1c7a3e", "blue": "#2348b0", "navy": "#162e86",
     "olive": "#8a2030", "oliveTip": "#5a1420"},
    {"name": "hyacinth macaw", "red": "#2c3a98", "deep": "#1e2a78", "breast": "#2c3a98", "yellow": "#2c3a98", "green": "#24308a", "blue": "#27358f", "navy": "#1a2470",
     "face": "#ecc232", "horn": "#1a1818", "olive": "#1c2048", "oliveTip": "#141834"}]
for p in d["parts"]:
    if p["id"] == "body": p["color"] = "@red"
    if p["id"] == "head": p["pos"] = [.13, .045, 0]
rig_wings(d, .3, [.02, .315, .045], .2, 40, 18, 1.3, dih=.04)
R = "@red"
sh = [
    ell("chest", [.04, .3, 0], [.1, .056, .055], "@breast", k=.03),
    ell("belly", [-.04, .285, 0], [.1, .045, .045], "@breast", k=.03),
    ell("back", [-.02, .325, 0], [.11, .03, .045], R, k=.03),
    ell("rump", [-.1, .3, 0], [.05, .035, .035], R, k=.025),
    ell("skull", [.13, .345, 0], [.045, .042, .038], R, k=.02, bone="head"),
    ell("face", [.152, .336, .021], [.026, .024, .013], "@face", k=.008, kc=.002, bone="head", mirror=True),
] + [{"when": "lines", **ell("faceLine%d" % i, [.146 + .005 * i, .344 - .008 * i, .0325 - .001 * abs(i - 1)], [.015, .0028, .004], "@lines", k=.0015, kc=.0008, bone="head", rot=[0, 0, -12], mirror=True)}
     for i in range(3)] + [
    tube("upper", [[.163, .352, 0, .02], [.186, .348, 0, .018], [.203, .334, 0, .013], [.208, .314, 0, .008], [.202, .299, 0, .003]], "@horn", k=.005, kc=.0015, bone="head"),
    tube("lower", [[.165, .322, 0, .015], [.183, .317, 0, .011], [.192, .314, 0, .006]], "@black", k=.004, kc=.0015, bone="head"),
    ell("foot", [-.06, .262, .025], [.025, .012, .014], "@foot", k=.006, kc=.002, mirror=True),
] + wing(.315, .02, .045, .2, .41, .04, .11,
         sec={"n": 5, "len": .16, "lens": [.15, .16, .165, .16, .15], "w": .034, "color": "@blue", "tip": "@navy"},
         prim={"n": 6, "a": (14, 30), "lens": [.2, .245, .29, .325, .35], "w": .036, "color": "@blue", "tip": "@navy", "curve": .015},
         covs=[{"id": "greater", "s": .2, "len": .1, "w": .034, "n": 6, "color": "@yellow", "tip": "@green"}],
         kink=.02, hsweep=.07, htaper=.5,
         under=[{"s": .3, "w": .5, "color": "@red"}, {"s": .52, "w": .3, "color": "@yellow", "top": True}],
         colors={"arm": R, "hand": "@blue", "edge": "@blue"}, th=.055) + [
    tail_fan([-.13, .298, 0], 5, .3, 9, .016, "@blue", "@navy", lens=[.26, .32, .34, .32, .26], camber=.08, curve=.01, seed=23),
    {**tail_fan([-.13, .302, 0], 3, .45, 4, .016, R, "@deep", lens=[.42, .48, .5, .48, .42], camber=.08, curve=.01, seed=24), "id": "tailC", "lift": .002},
]
# (the underwing: the flight feathers' undersides golden-olive -- a lining just beneath them)
for q in list(sh):
    if q.get("type") == "feathers" and q["id"] in ("sec", "prim"):
        u = json.loads(json.dumps(q)); u["id"] = q["id"] + "U"; u["color"] = "@olive"; u["tip"] = "@oliveTip"; u["n"] = q["n"]   # (one under each feather: n - 1 lay them in the gaps, seen from above as stripes)
        for r in u["rows"]: r["w"] *= 1.0; r["to"] = lerp(r["at"], r["to"], .9)
        u["lift"] = (q.get("lift", 0)) - .004; u.pop("bars", None); sh.append(u)
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; aloft (the wings' rest is the glide)",
    "mesh": {"tris": [3600, 1000], "focus": {"head": 3}},   # (C final: finer, the faceted slabs gone)
    "eyes": {"at": [.148, .352, .032], "from": [.13, .348, 0], "r": .0075, "iris": "@eye", "pupil": "round"},
    "shape": sh,
}
# (the perching agent's legs: perch/perchlegs.py's post-pass -- thighs, shins and gripping toes on their own bones -- kept
#  through every regeneration of this file)
import os as _os, sys as _sys
_PL = "/home/martin/store/apps/multiverse/tools/creaturegen/perch"
if _os.path.exists(_PL + "/perchlegs.py"):
    _sys.path.insert(0, _PL); from perchlegs import apply as _perch; d = _perch(d, "parrot")
save("parrot", d)
