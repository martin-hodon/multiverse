from bg import *
from flier import rig_wings, wing, tail_fan
d = load("eagle")
d["_about"] = "a golden eagle soaring: wings spread flat in a shallow V -- a broad arm of secondaries under their coverts, the hand's seven slotted primaries spread like fingers -- the tail fanned; a deep chest, the head with its flat crown, the brow over the eye, the golden nape and the hooked beak with its yellow cere; feathered legs drawn up under the tail, the yellow toes and black talons closed"
d["colors"] = {"brown": "#3f2b1b", "dark": "#2c1f15", "warm": "#56402a", "gold": "#c99a52", "beak": "#3a3430", "cere": "#e0b030",
               "remex": "#4a3a2c", "tip": "#1e1610", "tail": "#5a4a3a", "foot": "#e0b030", "talon": "#151210", "eye": "#8a5a1a", "pale": "#7a6448"}
by = .4
for p in d["parts"]:
    if p["id"] == "body": p["color"] = "@brown"; p["size"] = {"r": .1, "len": .36}
    if p["id"] == "head": p["pos"] = [.29, .07, 0]
rig_wings(d, by, [.03, .44, .07], .48, 30, 16, .4, dih=.06)
B = "@brown"
sh = [
    ell("chest", [.1, .4, 0], [.2, .1, .1], B, k=.05),
    ell("belly", [-.06, .37, 0], [.2, .085, .085], "@dark", k=.05),
    ell("back", [-.02, .435, 0], [.22, .05, .085], B, k=.04),
    ell("rump", [-.2, .405, 0], [.1, .055, .065], B, k=.04),
    ell("nape", [.24, .47, 0], [.075, .055, .058], "@gold", k=.03, kc=.035, bone="head"),
    ell("skull", [.3, .468, 0], [.07, .05, .047], B, k=.025, kc=.01, bone="head"),
    ell("crown", [.28, .5, 0], [.06, .025, .035], "@gold", k=.015, kc=.025, bone="head"),
    ell("face", [.325, .45, 0], [.045, .035, .04], "@dark", k=.02, kc=.008, bone="head"),
    ell("brow", [.33, .49, .028], [.028, .01, .016], B, k=.008, kc=.004, bone="head", rot=[0, 0, -8], mirror=True),
    # (the supraorbital shelf: a hard ledge over each eye -- the frown)
    ell("shelf", [.337, .491, .034], [.022, .0055, .012], B, k=.004, kc=.002, bone="head", rot=[0, 0, -10], mirror=True),
    ell("cere", [.363, .476, 0], [.017, .017, .021], "@cere", k=.005, kc=.001, bone="head"),
    ell("gape", [.348, .456, .014], [.016, .005, .006], "@cere", k=.004, kc=.0015, bone="head", mirror=True),
    tube("upper", [[.365, .472, 0, .018], [.392, .466, 0, .015], [.413, .452, 0, .01], [.421, .434, 0, .006], [.417, .421, 0, .002]], "@beak", k=.006, kc=.0015, bone="head"),
    tube("lower", [[.36, .452, 0, .012], [.383, .448, 0, .009], [.4, .446, 0, .005]], "@beak", k=.004, kc=.0015, bone="head"),
    # ---- legs drawn up under the tail: the feathered trousers, the yellow toes closed, black talons ----
    ell("thigh", [-.06, .345, .05], [.11, .05, .042], "@warm", k=.03, rot=[0, 0, 18], mirror=True),
    ell("foot", [-.17, .335, .035], [.04, .018, .022], "@foot", k=.008, kc=.003, mirror=True),
    cone("talon", [-.19, .33, .035], [-.215, .322, .035], .008, .002, "@talon", k=.003, mirror=True),
] + wing(.44, .03, .07, .48, .74, .06, .22,
         sec={"n": 10, "len": .3, "lens": [.25, .3, .33, .315, .27], "w": .046, "outline": "round", "color": "@remex", "tip": "@dark", "bars": {"n": 5, "dark": .72}},
         prim={"n": 7, "a": (6, 44), "lens": [.3, .37, .41, .42, .39], "w": .046, "color": "@remex", "tip": "@tip", "curve": .04, "bars": {"n": 4, "dark": .75}},
         covs=[{"id": "lesser", "s": .4, "len": .1, "w": .041, "n": 3, "h": .7, "color": "@brown", "tip": "@warm"},
               {"id": "greater", "s": .18, "len": .15, "w": .043, "n": 5, "color": "@warm", "tip": "@brown"}],
         pcov={"s": .16, "len": .13, "w": .042, "n": 2, "color": "@warm", "tip": "@brown"},
         kink=.1, hsweep=.11, htaper=.62, under=[{"s": .22, "w": .36, "color": "@dark"}, {"s": .58, "w": .22, "color": "@pale"}],
         ucov=[{"id": "ulesser", "s": .34, "len": .1, "w": .04, "n": 6, "color": "@dark", "tip": "@brown"},
               {"id": "ugreater", "s": .16, "len": .15, "w": .044, "n": 8, "color": "@brown", "tip": "@warm"}],
         colors={"arm": "@brown"}) + [
    tail_fan([-.26, .41, 0], 7, .3, 26, .046, "@tail", "@dark", lens=[.27, .3, .31, .3, .27], bars={"n": 4, "dark": .7}),
]
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; aloft (the wings' rest is the glide)",
    "mesh": {"tris": [2800, 950]},
    "eyes": {"at": [.34, .478, .036], "from": [.3, .47, 0], "r": .011, "iris": "@eye", "pupil": "round", "sink": .7, "socket": 1.08},
    "shape": sh,
}
# (the perching agent's legs: perch/perchlegs.py's post-pass, kept through every regeneration of this file)
import os as _os, sys as _sys
_PL = "/home/martin/store/apps/multiverse/tools/creaturegen/perch"
if _os.path.exists(_PL + "/perchlegs.py"):
    _sys.path.insert(0, _PL); from perchlegs import apply as _perch; d = _perch(d, "eagle")
import varB; d = varB.apply(d, "eagle")   # (B 2026-11-07: its named coats)
save("eagle", d)
