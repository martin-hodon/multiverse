from bg import *
from flier import rig_wings, wing, tail_fan
d = load("owl")
d["_about"] = "a Eurasian eagle-owl in flight: the huge round head with its tawny facial disc rimmed in black, the ear tufts, great orange eyes facing forward over a small black hooked beak half hidden in feathers; a stout streaked body, broad rounded wings with barred flight feathers and soft fringed tips, a short barred tail, the feathered feet drawn up"
d["colors"] = {"tawny": "#a27c4e", "dark": "#5a4028", "buff": "#c9a878", "face": "#bf9a6a", "disc": "#d9bd8e", "rim": "#2e2218", "beak": "#262220",
               "remex": "#b48e5e", "tip": "#6e5034", "cov": "#8a6a44", "eye": "#f08418", "talon": "#1a1612"}
for p in d["parts"]:
    if p["id"] == "body": p["color"] = "@tawny"; p["pat"] = None; p.pop("pat")
    if p["id"] == "head": p["pos"] = [.17, .1, 0]
    if p["id"] in ("wingL", "wingR"): p.pop("pat", None)
rig_wings(d, .35, [.03, .42, .07], .38, 34, 14, .6, dih=.03)
T = "@tawny"
sh = [
    ell("chest", [.05, .37, 0], [.15, .1, .1], "@buff", k=.065, kc=.03),
    ell("back", [-.02, .405, 0], [.17, .055, .09], T, k=.055, kc=.03),
    ell("belly", [-.05, .345, 0], [.15, .08, .088], "@buff", k=.065, kc=.03),
    ell("rump", [-.17, .37, 0], [.08, .05, .06], T, k=.04),
    # ---- the head: big and round, the disc in front rimmed dark, the tufts, the beak in the feathers ----
    ell("skull", [.16, .45, 0], [.095, .088, .108], T, k=.04, bone="head"),
    ell("rim", [.205, .445, 0], [.05, .078, .1], "@rim", k=.03, kc=.012, bone="head"),
    ell("disc", [.225, .44, .04], [.03, .064, .05], "@face", k=.025, kc=.008, bone="head", mirror=True),
    ell("brow", [.235, .48, .02], [.02, .012, .03], "@buff", k=.008, kc=.004, bone="head", rot=[0, 0, -15], mirror=True),
    # (C r9: the ear tufts FEATHERS, not horns -- five flat plumes each, rooted in a row along the brow's top, splayed
    #  a little outward and back, of uneven length so their tips are ragged)
    #  (C r10: more of them, flatter, leaning outward like a V and back, their lengths and angles jittered so the tips fray)
    fea("tuft", [row([.2 - .006 * i, .503 + .002 * i, .04 + .004 * i], [.184 - .011 * i, .552 + .04 * (1, .85, 1.0, .78, .9)[i] - .004 * i, .074 + .012 * i], .02 - .0015 * i, up=[1, 0, -.35])
                 for i in range(5)], 9, "@dark", "@tawny", outline="flight", bone="head", mirror=True, camber=.05, curve=-.03, lift=0, vary=.28, jitter=.3, seed=31),
    tube("beak", [[.258, .452, 0, .011], [.273, .44, 0, .009], [.278, .424, 0, .006], [.274, .41, 0, .002]], "@beak", k=.004, kc=.0015, bone="head"),
    # ---- the feathered feet tucked up, talons black ----
    ell("thigh", [-.05, .325, .05], [.09, .04, .03], "@buff", k=.05, kc=.03, rot=[0, 0, 15], mirror=True),
    ell("foot", [-.14, .315, .035], [.035, .02, .024], "@buff", k=.01, mirror=True),
    cone("talon", [-.16, .31, .035], [-.18, .303, .035], .007, .002, "@talon", k=.003, mirror=True),
] + wing(.42, .03, .07, .38, .62, .03, .22,
         sec={"n": 6, "len": .26, "lens": [.24, .262, .272, .265, .25], "w": .05, "color": "@remex", "tip": "@tip", "bars": {"n": 6, "dark": .6}},
         prim={"n": 7, "a": (8, 40), "lens": [.26, .295, .31, .295, .255], "w": .058, "color": "@remex", "tip": "@tip", "outline": "round",
               "bars": {"n": 6, "dark": .6}, "curve": .03},
         covs=[{"id": "lesser", "s": .4, "len": .1, "w": .04, "n": 4, "h": .7, "color": "@tawny", "tip": "@cov"},
               {"id": "greater", "s": .18, "len": .15, "w": .045, "n": 5, "color": "@cov", "tip": "@dark", "bars": {"n": 3, "dark": .7}}],
         pcov={"s": .16, "len": .13, "w": .044, "n": 2, "color": "@cov", "tip": "@dark", "bars": {"n": 3, "dark": .7}},
         kink=.035, hsweep=.045, htaper=.8, under=[{"s": .3, "w": .45, "color": "@buff"}],
         colors={"arm": "@tawny"}, th=.055) + [
    tail_fan([-.22, .38, 0], 7, .2, 26, .036, "@remex", "@tip", lens=[.18, .2, .21, .2, .18], bars={"n": 5, "dark": .6}),
]
# (the breast's streaks: dark dashes down the chest, bold above, finer below)
for k in range(16):
    ph = math.radians(-55 + 110 * ((k * 7) % 16) / 15); v = .25 - .75 * k / 15   # (from below the ruff down the breast: none at the face)
    c, r = [.05, .37, 0], [.15, .1, .1]; q = math.sqrt(max(0, 1 - v * v))
    at = [c[0] + r[0] * math.cos(ph) * q * .96, c[1] + r[1] * v * .96, c[2] + r[2] * math.sin(ph) * q * .96]   # (sunk: paint, not ribs)
    sh.append(ell(f"streak{k}", at, [.0055, .022 - .008 * k / 15, .0045], "@dark", k=.004, kc=.002))
# (the ruff: the disc's lower rim run smoothly down into the breast -- no lip under the face)
sh.append(ell("ruff", [.17, .39, 0], [.07, .05, .085], "@buff", k=.04, kc=.03))
# (C 2026-11-07: the facial disc made to read -- painted on the finished head: a dark rim round each half, the pale dish inside it)
sh += [ell("discRimP", [.24, .445, .045], [.05, .074, .064], "@rim", k=.004, kc=.004, bone="head", mirror=True, op="paint"),
       ell("discP", [.248, .447, .042], [.042, .062, .052], "@disc", k=.004, kc=.006, bone="head", mirror=True, op="paint")]
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; aloft (the wings' rest is the glide)",
    "mesh": {"tris": [2500, 900]},
    "eyes": {"at": [.245, .465, .036], "from": [.16, .462, .02], "r": .018, "iris": "@eye", "pupil": "round", "lid": "@face", "sink": .75, "socket": 1.08},
    "shape": sh,
}
import varB; d = varB.apply(d, "owl")   # (B 2026-11-07: its named coats)
save("owl", d)
