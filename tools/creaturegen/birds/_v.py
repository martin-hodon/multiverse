from bg import *
d = load("swan")
d["_about"] = "a mute swan afloat (swim.depth: the waterline at y = .18): a long full boat of a body, the wings held a little raised over the back with the primaries crossing over the short pointed tail, the neck in its S rising from the breast, the head held level with the bill pointing down, orange bill with the black knob, lores and nail"
d["colors"] = {"white": "#f4f2ec", "shade": "#e6e3da", "bill": "#e0702a", "black": "#141210", "eye": "#2a1a12"}
for p in d["parts"]:
    if p["id"] == "body": p["color"] = "@white"
    if p["id"] == "neck2": p["pos"] = [.06, .3, 0]
    if p["id"] == "head": p["pos"] = [.09, .28, 0]
W, SH = "@white", "@shade"
sh = [
    ell("hull", [-.02, .22, 0], [.34, .12, .2], W, k=.05),
    ell("belly", [0, .16, 0], [.32, .07, .18], SH, k=.05),
    ell("breast", [.2, .25, 0], [.16, .13, .165], W, k=.05),
    ell("back", [-.06, .32, 0], [.28, .07, .16], W, k=.05, rot=[0, 0, 3]),
    ell("stern", [-.28, .26, 0], [.13, .09, .12], W, k=.05, rot=[0, 0, -10]),
    # ---- the neck's S: forward off the breast, back, then up and forward to the head ----
    tube("neckA", [[.2, .3, 0, .085], [.3, .38, 0, .066], [.35, .48, 0, .054], [.36, .58, 0, .047]], W, k=.04, bone="neck"),
    tube("neckB", [[.36, .56, 0, .048], [.335, .68, 0, .042], [.34, .79, 0, .039], [.385, .875, 0, .037], [.43, .905, 0, .036]], W, k=.03, bone="neck2"),
    ell("skull", [.46, .906, 0], [.06, .038, .034], W, k=.02, bone="head", rot=[0, 0, -14]),
    ell("crown", [.45, .925, 0], [.04, .02, .028], W, k=.015, bone="head"),
    ell("lore", [.5, .894, .013], [.024, .016, .012], "@black", k=.006, kc=.002, bone="head", rot=[0, 0, -20], mirror=True),
    ell("knob", [.507, .913, 0], [.02, .017, .012], "@black", k=.006, kc=.002, bone="head", rot=[0, 0, -20]),
    ell("bill", [.556, .877, 0], [.055, .014, .02], "@bill", k=.008, kc=.002, bone="head", rot=[0, 0, -24]),
    ell("lowerBill", [.548, .866, 0], [.045, .008, .016], "@bill", k=.006, kc=.002, bone="head", rot=[0, 0, -22]),
    ell("nail", [.603, .855, 0], [.009, .006, .01], "@black", k=.003, kc=.001, bone="head", rot=[0, 0, -24]),
    # ---- the wings: raised a little over the back; tertials and secondaries over it, the primaries crossing the tail ----
    ell("wing", [-.06, .34, .125], [.28, .085, .07], W, k=.04, rot=[-32, 0, -4], mirror=True),
    fea("tail", fan([-.38, .3, 0], [[-1, .5, .35], [-1, .55, .12], [-1, .55, -.12], [-1, .5, -.35]], [.12, .13, .13, .12], .034), 7,
        W, SH, outline="round", up=[.4, 1, 0], camber=.12, curve=.03, seed=5),
]
# ---- the wings, arched a little over the back: the tracts of white coverts, the secondaries over the back, the primaries
#      crossing over the pointed tail ----
rig_fold(d, [.14, .4, .13], speed=.7, hind=[-80, 10, -40], neck=5, H=.11, px=-0.386, reach=.45, mid=.5, flyTurn={'neck': -72, 'head': 62})   # (aloft, the folded wing swung out: flight in the asset viewer)
fold_wing(sh, [.14, .4, .13], [-.42, .36, .03], .11, .045, {"cov": W, "gcov": W, "gcovTip": SH, "sec": W, "secTip": SH, "prim": SH, "primTip": SH},
          n=(4, 5, 6, 3), up=(0, .7, 1), bone="wrollL", pbone="wtipL", mbone="wmidL")
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; afloat at the waterline y = .18",
    "mesh": {"tris": [4400, 1300]},
    "eyes": {"at": [.485, .915, .03], "from": [.46, .906, 0], "r": .0075, "iris": "@eye", "pupil": "round", "lid": "@black"},
    "shape": sh,
}
save("swan", d)
