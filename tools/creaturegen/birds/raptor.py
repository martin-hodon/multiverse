# raptor.py [buzzard falcon] -- the medium raptors from the eagle's soaring plan (flier.py: spread wings on rig_wings, a
#   fanned tail, the legs drawn up): authored at the eagle's size with the species' own wing, tail, head and plumage, then
#   scaled (parts, rig and sculpt) to the bird's real size. Sky fliers like the eagle (flags.fly, no legs on the ground).
import sys
from bg import *
from flier import rig_wings, wing, tail_fan

def scale_parts(parts, s):
    for p in parts:
        for k in ("pos", "pivot"):
            if k in p: p[k] = [round(v * s, 4) for v in p[k]]
        sz = p.get("size", {})
        for k, v in list(sz.items()):
            sz[k] = [round(x * s, 4) for x in v] if isinstance(v, list) else round(v * s, 4)

def raptor(name, s, about, cols, W, T, head, extra, fly, tris=(2800, 950)):
    d = load("eagle")
    d["name"] = name; d["_about"] = about
    d["colors"] = cols
    d["flags"] = {"fly": fly, "active": "day", "print": "bird"}
    by = .4
    for p in d["parts"]:
        if p["id"] == "body": p["color"] = "@back"; p["size"] = {"r": .1, "len": .36}
        if p["id"] == "head": p["pos"] = [.29, .07, 0]; p["color"] = "@head"
        if p["id"] == "beak": p["color"] = "@beak"
        if p["id"] == "tail": p["color"] = "@tail"
        if p["id"].startswith("wing"): p["color"] = "@back"
    rig_wings(d, by, [.03, .44, .07], W["zW"], W["deg"], W["hand"], W["speed"], dih=W["dih"])
    bk = head.get("bill", 1.0)    # (the bill's length, of the eagle's)
    bx = lambda x: round(.363 + (x - .363) * bk, 4)
    sh = [
        ell("chest", [.1, .388, 0], [.2, .088, .1], "@chest", k=.05),
        ell("belly", [-.06, .37, 0], [.2, .085, .085], "@belly", k=.05),
        ell("back", [-.02, .435, 0], [.22, .05, .085], "@back", k=.04),
        ell("mantle", [.07, .452, 0], [.22, .042, .08], "@back", k=.03),   # (the upperparts' colour over the pale breast)
        ell("rump", [-.2, .405, 0], [.1, .055, .065], "@back", k=.04),
        ell("nape", [.24, .47, 0], [.075, .055, .058], "@nape", k=.03, kc=.035, bone="head"),
        ell("skull", [.3, .468, 0], [.07, .05 * head.get("dome", 1), .047], "@head", k=.025, kc=.01, bone="head"),
        ell("crown", [.28, .5, 0], [.06, .025, .035], "@crown", k=.015, kc=.025, bone="head"),
        ell("face", [.325, .45, 0], [.045, .035, .04], "@face", k=.02, kc=.008, bone="head"),
        ell("brow", [.33, .49, .028], [.028, .01, .016], "@head", k=.008, kc=.004, bone="head", rot=[0, 0, -8], mirror=True),
        ell("shelf", [.337, .491, .034], [.022, .0055 * head.get("shelf", 1), .012], "@head", k=.004, kc=.002, bone="head", rot=[0, 0, -10], mirror=True),
        ell("cere", [.363, .476, 0], [.017, .017, .021], "@cere", k=.005, kc=.001, bone="head"),
        ell("gape", [.348, .456, .014], [.016, .005, .006], "@cere", k=.004, kc=.0015, bone="head", mirror=True),
        tube("upper", [[.365, .472, 0, .018], [bx(.392), .466, 0, .015], [bx(.413), .452, 0, .01], [bx(.421), .434, 0, .006], [bx(.417), .421, 0, .002]], "@beak", k=.006, kc=.0015, bone="head"),
        tube("lower", [[.36, .452, 0, .012], [bx(.383), .448, 0, .009], [bx(.4), .446, 0, .005]], "@beak", k=.004, kc=.0015, bone="head"),
        ell("thigh", [-.06, .345, .05], [.11, .05, .042], "@thigh", k=.03, rot=[0, 0, 18], mirror=True),
        ell("foot", [-.17, .335, .035], [.04, .018, .022], "@foot", k=.008, kc=.003, mirror=True),
        cone("talon", [-.19, .33, .035], [-.215, .322, .035], .008, .002, "@talon", k=.003, mirror=True),
    ] + extra + wing(.44, .03, .07, W["zW"], W["zT"], W["dih"], W["chord"], sec=W["sec"], prim=W["prim"], covs=W["covs"], pcov=W["pcov"],
                     kink=W.get("kink", .1), hsweep=W["hsweep"], htaper=W["htaper"], under=W["under"], ucov=W.get("ucov"), colors={"arm": "@back", **W.get("cols", {})}) + [
        tail_fan([-.26, .41, 0], T["n"], T["len"], T["spread"], T["w"], "@tail", "@tailTip", lens=T["lens"], bars=T.get("bars")),
    ]
    # ---- to size ----
    scale_parts(d["parts"], s)
    sh = shift(sh, [0, 0, 0], s)
    d["sculpt"] = {
        "_about": "x forward, y up, z left, metres; aloft (the wings' rest is the glide); authored at the eagle's size and scaled %.2f" % s,
        "mesh": {"tris": list(tris)},
        "eyes": {"at": [round(v * s, 4) for v in [.34, .478, .036]], "from": [round(v * s, 4) for v in [.3, .47, 0]], "r": round(.011 * head.get("eye", 1) * s, 4),
                 "iris": "@eye", "pupil": "round", "sink": .7, "socket": 1.08, **({"lid": head["lid"]} if head.get("lid") else {})},
        "shape": sh,
    }
    # (the perching agent's legs, kept if it has given this bird its perch legs: perch/perchlegs.py's post-pass)
    import os as _os, json as _json
    _PL = "/home/martin/store/apps/multiverse/tools/creaturegen/perch"
    _f = "/home/martin/store/apps/multiverse/assets/creatures/birds/%s.json" % name
    if _os.path.exists(_PL + "/perchlegs.py") and _os.path.exists(_f) and '"perchleg"' in open(_f).read():
        sys.path.insert(0, _PL); from perchlegs import apply as _perch; d = _perch(d, name)
    else:   # (no perch legs yet: drop the leg bones the eagle's file now carries, as before)
        _L = {"legL", "legR", "shinL", "shinR", "footL", "footR"} | {f"toe{s_}{i_}" for s_ in "LR" for i_ in range(4)}
        d["parts"] = [p for p in d["parts"] if p["id"] not in _L]
    d.pop("coats", None); d.pop("params", None)   # (not the eagle's coats: its own -- B 2026-11-07)
    import varB; d = varB.apply(d, name)
    save(name, d)

SP = {}
def sp(f): SP[f.__name__] = f; return f

@sp
def buzzard():
    c = {"back": "#5e4029", "chest": "#cdb894", "belly": "#7a5634", "head": "#6a4a30", "nape": "#5a3e28", "crown": "#5e4029", "face": "#7a5a3a",
         "beak": "#2e2a28", "cere": "#e8c040", "thigh": "#6a4a30", "foot": "#e8c040", "talon": "#151210", "eye": "#6a3a18",
         "remex": "#b8ab98", "remTip": "#2a2018", "pTip": "#1e1812", "cov": "#5a3e28", "covTip": "#7a5838", "carpal": "#2e2016",
         "lining": "#a88a62", "tail": "#8a7058", "tailTip": "#5a4430", "streak": "#5a3e26", "edge": "#5a3e28"}
    W = dict(zW=.46, zT=.72, dih=.08, chord=.24, deg=26, hand=14, speed=.45, hsweep=.08, htaper=.7, kink=.08,
             ucov=[{"id": "ulesser", "s": .34, "len": .1, "w": .04, "n": 6, "color": "@lining", "tip": "@lining"},
                   {"id": "ugreater", "s": .16, "len": .15, "w": .044, "n": 8, "color": "@lining", "tip": "@chest"}],
             sec={"n": 10, "len": .27, "lens": [.24, .27, .29, .28, .25], "w": .048, "outline": "round", "color": "@remex", "tip": "@remTip", "bars": {"n": 6, "dark": .6}},
             prim={"n": 6, "a": (8, 40), "lens": [.27, .32, .35, .35, .32], "w": .05, "color": "@remex", "tip": "@pTip", "curve": .04, "bars": {"n": 5, "dark": .62}},
             covs=[{"id": "lesser", "s": .4, "len": .1, "w": .041, "n": 3, "h": .7, "color": "@cov", "tip": "@covTip"},
                   {"id": "greater", "s": .18, "len": .15, "w": .043, "n": 5, "color": "@covTip", "tip": "@cov"}],
             pcov={"s": .16, "len": .13, "w": .042, "n": 2, "color": "@cov", "tip": "@covTip"},
             under=[{"s": .2, "w": .3, "color": "@lining"}, {"s": .5, "w": .2, "color": "@carpal"}])
    T = dict(n=7, len=.26, spread=30, w=.05, lens=[.24, .26, .27, .26, .24], bars={"n": 9, "dark": .55})
    extra = [ell("band", [.14, .385, 0], [.1, .075, .095], "#e6dcc4", k=.03),          # (the pale U across the breast)
             ell("streakL", [.06, .36, .05], [.09, .02, .03], "@streak", k=.015, mirror=True)]
    raptor("buzzard", .6, "a common buzzard soaring in wide circles: broad, rounded wings held in a shallow V, the five fingered primaries spread, a short fanned tail finely barred; dark brown above, below the pale barred flight feathers with their dark trailing edge and the dark patch at the wrist, the pale band across the brown breast; a round head, the small hooked bill on its yellow cere, yellow feet drawn up",
           c, W, T, {"bill": .8, "shelf": .7, "dome": 1.1}, extra, {"alt": [18, 120], "speed": [4, 7], "hz": .45})

@sp
def falcon():
    c = {"back": "#4e5c6c", "chest": "#ece4d4", "belly": "#d8ccb8", "head": "#222830", "nape": "#2a3038", "crown": "#20262e", "face": "#f0ebe2",
         "beak": "#3a4048", "cere": "#e8c030", "thigh": "#d0c4b0", "foot": "#e8c030", "talon": "#151210", "eye": "#1a120c",
         "remex": "#5a6674", "remTip": "#2a3038", "pTip": "#20252c", "cov": "#55657a", "covTip": "#3e4a58", "lining": "#cfc6b8", "bar": "#4a4a50",
         "tail": "#5a6878", "tailTip": "#2a3038", "edge": "#4a5868", "mous": "#1e232a"}
    W = dict(zW=.42, zT=.86, dih=.03, chord=.18, deg=34, hand=22, speed=.9, hsweep=.24, htaper=.42, kink=.07,
             ucov=[{"id": "ulesser", "s": .34, "len": .08, "w": .034, "n": 6, "color": "@lining", "tip": "@lining", "bars": {"n": 3, "dark": .75}},
                   {"id": "ugreater", "s": .16, "len": .12, "w": .038, "n": 8, "color": "@lining", "tip": "@lining", "bars": {"n": 4, "dark": .75}}],
             sec={"n": 9, "len": .22, "lens": [.2, .22, .22, .21, .19], "w": .046, "outline": "round", "color": "@remex", "tip": "@remTip", "bars": {"n": 7, "dark": .65}},
             prim={"n": 10, "a": (6, 22), "lens": [.32, .4, .46, .5, .48], "w": .058, "color": "@remex", "tip": "@pTip", "curve": .03, "bars": {"n": 7, "dark": .65}},
             covs=[{"id": "lesser", "s": .4, "len": .09, "w": .036, "n": 3, "h": .7, "color": "@cov", "tip": "@covTip"},
                   {"id": "greater", "s": .2, "len": .13, "w": .038, "n": 5, "color": "@cov", "tip": "@covTip"}],
             pcov={"s": .18, "len": .12, "w": .036, "n": 2, "color": "@cov", "tip": "@covTip"},
             under=[{"s": .25, "w": .4, "color": "@lining"}, {"s": .62, "w": .2, "color": "@bar"}])
    T = dict(n=7, len=.32, spread=11, w=.042, lens=[.31, .32, .33, .32, .31], bars={"n": 7, "dark": .6})
    extra = [ell("mous", [.33, .44, .036], [.012, .03, .012], "@mous", k=.006, kc=.003, bone="head", rot=[0, 0, -8], mirror=True),   # (the moustache)
             ell("hood", [.285, .485, 0], [.075, .045, .05], "@head", k=.02, kc=.01, bone="head"),
             ell("throat", [.27, .42, 0], [.05, .03, .04], "@face", k=.02, kc=.01, bone="head")] + \
            [ell("bar%d" % i, [.12 - i * .07, .345 + i * .004, .045], [.012, .016, .03], "@bar", k=.008, mirror=True) for i in range(4)]
    raptor("falcon", .47, "a peregrine falcon on the hunt: long, pointed, narrow wings swept back from the wrist, the stiff unslotted primaries, a longish narrow tail barred dark; slate-blue above, the black hood and the black moustache down the white cheek, below white barred dark; a short hooked bill on the yellow cere, the yellow eye-ring, yellow feet drawn up",
           c, W, T, {"bill": .72, "shelf": 1.2, "dome": 1.05, "eye": 1.15, "lid": "@cere"}, extra, {"alt": [25, 200], "speed": [6, 14], "hz": .9}, tris=(4000, 1000))   # (C final: finer -- the faceted belly slab gone)

if __name__ == "__main__":
    for n in (sys.argv[1:] or SP): SP[n]()
