from bg import *
d = load("swan")
d["_about"] = "a mute swan afloat (swim.depth: the waterline at y = .18): a long full boat of a body, the wings held a little raised over the back with the primaries crossing over the short pointed tail, the neck in its S rising from the breast, the head held level with the bill pointing down, orange bill with the black knob, lores and nail -- aloft (the viewer's fly) the folded wings turn into the body and a broad white spread wing swings out feather by feather (swan.py, nbwing.aloft)"
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
    fea("tail", fan([-.38, .3, 0], [[-1, .5, .35], [-1, .55, .12], [-1, .55, -.12], [-1, .5, -.35]], [.08, .088, .088, .08], .05), 7,
        W, SH, outline="round", up=[.4, 1, 0], camber=.22, curve=.03, seed=5),
    ell("tailBase", [-.416, .318, 0], [.05, .015, .045], W, k=.012, kc=.004, rot=[0, 0, -27]),
]
# ---- the wings, arched a little over the back: the tracts of white coverts, the secondaries over the back, the primaries
#      crossing over the pointed tail ----
fold = fold_wing(sh, [.14, .4, .13], [-.42, .36, .03], .11, .045, {"cov": W, "gcov": W, "gcovTip": SH, "sec": W, "secTip": SH, "prim": SH, "primTip": SH},
                 n=(4, 5, 5, 3), up=(0, .7, 1), proot=.12)
# ---- ALOFT (2026-11-08): the folded tracts turned half round into the body and a SPREAD wing swung out feather by feather
#      (nbwing.aloft, as the duck's and the goose's) -- before, the folded wing itself swung out and rolled flat, its feathers
#      pointing out along the span: from the front a few separate white blades with gaps ----
import nbwing
d["parts"] = [p for p in d["parts"] if not (p["id"][-1] in "LR" and p["id"][:-1].startswith(("wfold", "wroll", "wext", "wlift", "wtip", "wmid", "ws", "wf")))]   # (wmid: an old rig's leftover)
for p in d["parts"]:
    if p["id"] in ("wingL", "wingR"): p.pop("flyRot", None)
    if p["id"] == "neck": p["flyRot"] = [0, 0, -72]   # (aloft: the neck reaching straight forward, the head levelled on it)
    if p["id"] == "head": p["flyRot"] = [0, 0, 62]
info = nbwing.aloft(d, sh, {"spread": dict(span=2.1, armF=.45, asp=3.2, tipC=.3, hsweep=.4, pinch=.7), "flight": {"speed": .7}},
                    [.14, .4, .13], 1.05, d["colors"], fold, dict(nbwing.WING), "big", nrm([0, .7, 1]), .0025, .56,
                    tk={"c": [-.02, .27, 0], "r": [.34, .12, .18]},   # (the hull's core, a little up: the wing set high on the back)
                    fold_bands=False, add_fold=False, drop=.06,   # (the fold, high over the back, let down to hide)
                    look_over={"sec": (W, SH), "gcov": (W, W), "cov": (W, W), "pcov": (W, W), "prim": (W, SH)})
print("  swan aloft:", info)
d["flags"]["flight"] = {"arm": 0, "hand": 0, "beat": 44, "bob": .03, "hind": [-80, 10, -40], "neck": 5}
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; afloat at the waterline y = .18",
    "mesh": {"tris": [2800, 1000]},
    "eyes": {"at": [.485, .915, .03], "from": [.46, .906, 0], "r": .0075, "iris": "@eye", "pupil": "round", "lid": "@black"},
    "shape": sh,
}
import varB; d = varB.apply(d, "swan")   # (B 2026-11-07: its named coats)
save("swan", d)
# (2026-11-08) the flight neck straight: the upper neck tube split onto a third bone and every neck bone's flyRot set --
#  swanneck.py, on the file just written (the neck/head flyRot above are its to override)
import subprocess, sys, os; subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "swanneck.py")], check=True)
