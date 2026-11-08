from bg import *
from wader import legs, leg_shapes
d = load("heron")
d["_about"] = "a grey heron standing watchful: a long body sloping down to the tail on yellow-brown legs (the tibia bare above the backward 'knee'), the long neck drawn into its S so the head sits forward of the shoulders, the dagger bill; white head and neck with the black stripe from the eye back into the plumes and black streaks down the front of the neck, grey back and wings with the black shoulder patch and black primaries, the grey plumes falling over the breast (2026-11-08) ALOFT the folded tracts turn into the body and a broad spread wing of its own swings out feather by feather (nbwing.aloft): grey coverts, dark secondaries along the trailing edge, black primaries -- no longer the folded wing itself swung out as two loose blades."
d["colors"] = {"grey": "#737a83", "dark": "#5a616a", "white": "#eceeef", "pale": "#d8dcdf", "black": "#17171a", "bill": "#d8a634",
               "leg": "#a88f5c", "eye": "#e8d040"}
d["_bodyY"] = .56
for p in d["parts"]:
    if p["id"] == "body": p["pos"] = [0, .56, 0]; p["color"] = "@grey"; p["size"] = {"r": .1, "len": .22}
    if p["id"] == "neck": p["pos"] = [.15, .06, 0]
    if p["id"] == "neck2": p["pos"] = [.05, .1, 0]
    if p["id"] == "head": p["pos"] = [.1, .155, 0]
legs(d, .46, .22, 20, .55, 26)
del d["_bodyY"]
G = "@grey"
sh = [
    ell("trunk", [-.02, .575, 0], [.2, .08, .075], G, k=.04, rot=[0, 0, 14]),
    ell("breast", [.1, .61, 0], [.075, .075, .07], "@pale", k=.035),
    ell("belly", [.02, .53, 0], [.08, .04, .05], "@pale", k=.035, rot=[0, 0, 12]),
    # (the black at the bend of the wing, long; and the black stripe down the flank under the wing)
    ell("shoulder", [.085, .63, .056], [.05, .016, .016], "@black", k=.006, kc=.002, rot=[0, 0, -30], mirror=True),
    ell("flankS", [-.02, .54, .06], [.11, .014, .02], "@black", k=.006, kc=.002, rot=[0, 0, 12], mirror=True),
    # ---- the neck drawn in: up and forward off the breast, a kink back, up and forward to the head ----
    tube("neckA", [[.1, .63, 0, .036], [.16, .675, 0, .024], [.2, .73, 0, .02]], "@white", k=.025, bone="neck"),
    tube("neckB", [[.2, .72, 0, .02], [.205, .79, 0, .019], [.235, .84, 0, .019], [.28, .866, 0, .019]], "@white", k=.016, bone="neck2"),
    ell("plumes", [.1, .6, 0], [.035, .07, .04], "@pale", k=.02, rot=[0, 0, -25]),
    ell("skull", [.3, .875, 0], [.038, .024, .021], "@white", k=.012, bone="head", rot=[0, 0, -6]),
    ell("stripe", [.29, .885, .012], [.032, .009, .01], "@black", k=.004, kc=.0015, bone="head", rot=[0, 0, 8], mirror=True),
    tube("crest", [[.28, .885, 0, .007], [.24, .88, 0, .005], [.2, .862, 0, .0028]], "@black", k=.004, kc=.0015, bone="head"),
    # (two long black plumes from the nape, falling back over the neck)
    cone("plumeA", [.255, .884, .004], [.14, .845, .008], .0035, .001, "@black", k=.002, kc=.001, bone="head"),
    cone("plumeB", [.255, .88, -.004], [.155, .835, -.009], .0032, .001, "@black", k=.002, kc=.001, bone="head"),
    # (the dagger: long, straight, deep at the base, sharp)
    tube("bill", [[.325, .874, 0, .0115], [.37, .868, 0, .0085], [.41, .861, 0, .005], [.438, .856, 0, .0015]], "@bill", k=.006, kc=.0015, bone="head"),
    ell("jaw", [.36, .866, 0], [.04, .006, .008], "@bill", k=.004, kc=.0015, bone="head", rot=[0, 0, -8]),
    # ---- the folded wing: grey, its primaries black at the tip down the rear edge ----
    ell("wing", [-.03, .6, .05], [.18, .06, .035], G, k=.022, rot=[-10, 0, 14], mirror=True),
    fea("tail", fan([-.2, .54, 0], [[-1, -.35, .3], [-1, -.33, 0], [-1, -.35, -.3]], [.1, .11, .1], .024), 5, G, "@dark",
        outline="round", up=[0, 1, 0], camber=.1, seed=5),
] + leg_shapes([0, .46, .045], .22, .009, .0115, .0075, "@leg", "@pale", [.045, .05, .035], .065, hallux=.035)
for q in sh:
    if q.get("id") == "thigh": q["c"][1] += .035; q["r"] = [.035, .03, .026]; q["color"] = "@grey"
    if q.get("id") == "tibia": q["a"][1] = .49   # (the bare tibia runs up INTO the lifted thigh: it once stopped 2.6cm short of it, the legs hanging loose)
# ---- the folded wing: grey coverts, the darker secondaries, the black primaries crossing over the tail ----
# (aloft: the legs trail straight back; the neck stays drawn into its S, as a heron flies)
for p in d["parts"]:
    if p["id"] in ("legL", "legR"): p["flyRot"] = [0, 0, -82]
fold = fold_wing(sh, [.11, .64, .065], [-.24, .52, .04], .09, .026,
          {"cov": "@grey", "covTip": "@dark", "gcov": "@grey", "gcovTip": "@dark", "sec": "@dark", "secTip": "@black", "prim": "@black"}, n=(4, 4, 5, 3), up=(0, .2, 1))
# ---- ALOFT (2026-11-08): the folded tracts each turned half round into the body, and a SPREAD wing of its own swung out
#      feather by feather (nbwing.aloft, as the duck's and the swan's) -- before (bg.rig_fold) the folded wing itself was
#      swung out and rolled flat: from above two long grey blades either side with ragged ends. Now a broad wing: grey
#      lesser and greater coverts, the dark secondaries along the arm's trailing edge, the black primaries on the hand ----
import nbwing
d["parts"] = [p for p in d["parts"] if not (p["id"][-1] in "LR" and p["id"][:-1].startswith(("wfold", "wroll", "wext", "wlift", "wtip", "witurn", "wfwd", "ws", "wf")))]
for p in d["parts"]:
    if p["id"] in ("wingL", "wingR"): p.pop("flyRot", None)
info = nbwing.aloft(d, sh, {"spread": dict(span=2.3, armF=.45, asp=2.8, tipC=.3, hsweep=.3, pinch=.7), "flight": {"speed": .6}},
                    [.11, .64, .065], .85, d["colors"], fold, dict(nbwing.WING), "big", nrm([0, .2, 1]), .0025, .35,
                    fold_bands=False, add_fold=False,
                    look_over={"sec": ("@dark", "@black"), "gcov": ("@grey", "@dark"), "cov": ("@grey", "@grey"), "pcov": ("@black", "@black"), "prim": ("@black", "@black")})
print("  heron aloft:", info)
d["flags"]["flight"] = {"arm": 0, "hand": 0, "beat": 44, "bob": .03, "hind": [-90, 0, -20]}
# (the neck's streaks: a double row of fine black dashes down the front of the white neck)
NP = [([.1, .63], .036, "neck"), ([.16, .675], .024, "neck"), ([.2, .73], .02, "neck"), ([.205, .79], .019, "neck2"), ([.235, .84], .019, "neck2")]
k = 0
for j in range(len(NP) - 1):
    (p0, r0, b0), (p1, r1, _) = NP[j], NP[j + 1]
    tx, ty = p1[0] - p0[0], p1[1] - p0[1]; ln = math.hypot(tx, ty); tx, ty = tx / ln, ty / ln
    fx, fy = ty, -tx   # (the front: square to the neck, forward)
    if fx < 0: fx, fy = -fx, -fy
    m = max(1, round(ln / .013))
    for i in range(m):
        if j == 0 and i < m // 2: continue   # (not on the breast)
        u = (i + .5) / m; r = r0 + (r1 - r0) * u
        c = [p0[0] + tx * ln * u + fx * (r - .0012), p0[1] + ty * ln * u + fy * (r - .0002)]
        ang = math.degrees(math.atan2(ty, tx)) - 90
        for side in (1, -1):
            zz = side * r * .3
            sh.append(ell(f"dash{k}", [round(c[0] - (r - math.sqrt(max(0, r * r - zz * zz))), 4), round(c[1], 4), round(zz, 4)], [.0016, .0048, .0016], "@black",
                          k=.001, kc=.0006, bone=b0, rot=[0, 0, round(ang, 1)]))
            k += 1
place(sh, ["tail"], [0, 1, 0], .003)
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres",
    "mesh": {"tris": [3300, 1100], "cell": .003},
    "shade": {"back": .85, "belly": 1.04, "k": .05, "on": "@grey"},
    "eyes": {"at": [.317, .88, .016], "from": [.3, .875, 0], "r": .0055, "iris": "@eye", "pupil": "round"},
    "shape": sh,
}
import varB; d = varB.apply(d, "heron")   # (2026-11-07, B: its named coats -- the great egret)
save("heron", d)
