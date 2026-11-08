from bg import *
from wader import legs, leg_shapes
d = load("flamingo")
d["_about"] = "a greater flamingo standing: a compact oval body held level on very long pink legs -- bare tibia, the backward 'knee' (the ankle) half-way down, long tarsus, webbed feet -- the neck in its S, a small head and the thick bill bent down at its middle, pale pink with a black end; folded wings of crimson coverts, the black flight feathers showing along the rear edge under the drooping pink tertials (2026-11-08) ALOFT the folded tracts turn into the body and a spread wing of its own swings out feather by feather (nbwing.aloft): crimson coverts over the arm, black secondaries along its trailing edge, long black primaries on the hand -- no longer the folded wing itself swung out as loose blades."
d["colors"] = {"body": "#f2a8b0", "pale": "#f7d0d4", "neck": "#f2aab4", "covert": "#e8607a", "tert": "#f0a0b0", "black": "#151214",
               "bill": "#f2d2d0", "leg": "#e5808e", "eye": "#f0d84a"}
d["_bodyY"] = .92
for p in d["parts"]:
    if p["id"] == "body": p["pos"] = [0, .92, 0]; p["color"] = "@body"; p["size"] = {"r": .12, "len": .2}
    if p["id"] == "neck": p["pos"] = [.17, .07, 0]
    if p["id"] == "neck2": p["pos"] = [.04, .28, 0]
    if p["id"] == "head": p["pos"] = [.05, .25, 0]
legs(d, .82, .44, 20, .6, 26)
del d["_bodyY"]
B, P = "@body", "@pale"
sh = [
    ell("trunk", [-.01, .93, 0], [.21, .11, .11], B, k=.04, rot=[0, 0, -4]),
    ell("breast", [.12, .94, 0], [.1, .1, .1], B, k=.04),
    ell("belly", [-.02, .86, 0], [.15, .06, .09], P, k=.04),
    ell("rump", [-.19, .93, 0], [.08, .07, .07], B, k=.035, rot=[0, 0, 10]),
    # ---- neck: up off the breast, back, and forward again to the head ----
    tube("neckA", [[.12, .98, 0, .056], [.19, 1.04, 0, .034], [.22, 1.12, 0, .024], [.215, 1.21, 0, .018]], "@neck", k=.03, bone="neck"),
    # (the lower bend's full front -- the neck heavy where it leaves the breast, not a uniform hose)
    ell("crop", [.207, 1.075, 0], [.03, .05, .027], "@neck", k=.02, kc=.006, bone="neck", rot=[0, 0, -20]),
    tube("neckB", [[.215, 1.2, 0, .018], [.19, 1.3, 0, .0135], [.17, 1.39, 0, .0118], [.19, 1.46, 0, .0145], [.235, 1.505, 0, .0172]], "@neck", k=.02, bone="neck2"),
    ell("skull", [.262, 1.515, 0], [.036, .027, .024], "@pale", k=.015, bone="head", rot=[0, 0, -10]),
    # (the bill: thick and straight from the face, then bent sharply down; its far half black)
    tube("billA", [[.285, 1.513, 0, .0125], [.315, 1.507, 0, .0125], [.34, 1.496, 0, .011], [.352, 1.48, 0, .0092]], "@bill", k=.008, kc=.002, bone="head"),
    tube("billB", [[.353, 1.481, 0, .009], [.362, 1.463, 0, .007], [.367, 1.448, 0, .005], [.368, 1.436, 0, .0025]], "@black", k=.006, kc=.0015, bone="head"),
    ell("jaw", [.315, 1.497, 0], [.03, .0095, .0105], "@bill", k=.006, kc=.002, bone="head", rot=[0, 0, -12]),
    # ---- the folded wing: crimson coverts high on the flank, tertials drooping over the tail, black flight feathers
    #      showing along the rear edge under them ----
    ell("wing", [-.02, .95, .07], [.17, .07, .05], B, k=.03, rot=[-12, 0, -4], mirror=True),
] 
# (the body a fifth bigger than it was and longer still -- a level oval on the legs and under the neck)
O, SC = [0, .88, 0], [1.25, 1.17, 1.2]
for q in sh:
    if q["id"] in ("trunk", "breast", "belly", "rump", "wing"):
        q["c"] = [round(O[i] + (q["c"][i] - O[i]) * SC[i], 4) for i in range(3)]; q["r"] = [round(q["r"][i] * SC[i], 4) for i in range(3)]; q["k"] = round(q["k"] * 1.2, 4)
sh += leg_shapes([0, .82, .05], .44, .0105, .015, .009, "@leg", B, [.075, .09, .06], .06, web="@leg", hallux=.018, scales=False)
# ---- the folded wing: crimson coverts high on the flank, the black flight feathers along its rear lower edge, the pink
#      scapular plumes (tertials) drooping over them and the short tail (no tail of its own showing) ----
# (aloft: the legs trail straight back, the neck reaches forward and the head levels on it)
for p in d["parts"]:
    if p["id"] in ("legL", "legR"): p["flyRot"] = [0, 0, -82]
    if p["id"] == "neck": p["flyRot"] = [0, 0, -75]
    if p["id"] == "head": p["flyRot"] = [0, 0, 68]
fold = fold_wing(sh, [.125, 1.01, .102], [-.31, .93, .06], .12, .034,
          {"cov": "@covert", "covTip": "@covert", "gcov": "@covert", "gcovTip": "@tert", "sec": "@black", "prim": "@black"}, n=(4, 5, 5, 3), up=(0, .2, 1), proot=.12)
# ---- ALOFT (2026-11-08): the folded tracts each turned half round into the body, and a SPREAD wing of its own swung out
#      feather by feather (nbwing.aloft, as the duck's and the swan's) -- before (bg.rig_fold) the folded wing itself was
#      swung out and rolled flat: from above a few loose stubby blades either side, the black primaries a separate fan.
#      Now: crimson lesser and greater coverts over the arm, the black secondaries along its trailing edge, the long black
#      primaries on the hand ----
import nbwing
d["parts"] = [p for p in d["parts"] if not (p["id"][-1] in "LR" and p["id"][:-1].startswith(("wfold", "wroll", "wext", "wlift", "wtip", "witurn", "wfwd", "ws", "wf")))]
for p in d["parts"]:
    if p["id"] in ("wingL", "wingR"): p.pop("flyRot", None)
info = nbwing.aloft(d, sh, {"spread": dict(span=2.3, armF=.45, asp=3.0, tipC=.3, hsweep=.35, pinch=.7), "flight": {"speed": .7}},
                    [.125, 1.01, .102], 1.0, d["colors"], fold, dict(nbwing.WING), "big", nrm([0, .2, 1]), .0025, .435,
                    fold_bands=False, add_fold=False,
                    look_over={"sec": ("@black", "@black"), "gcov": ("@covert", "@covert"), "cov": ("@covert", "@covert"), "pcov": ("@covert", "@covert"), "prim": ("@black", "@black")})
print("  flamingo aloft:", info)
d["flags"]["flight"] = {"arm": 0, "hand": 0, "beat": 44, "bob": .03, "hind": [-90, 0, -20], "neck": 2}
sh.append(fea("tert", [row([-.0, 1.04, .072], [-.25, 1.0, .09], .034), row([-.06, 1.04, .06], [-.32, .965, .06], .032), row([-.11, 1.035, .042], [-.35, .945, .036], .03)], 6,
              "@tert", "@body", outline="round", up=[0, 1, .7], camber=.16, curve=-.08, lift=.004, vary=.15, stagger=.002, seed=4, mirror=True))
place(sh, ["tert"], [0, .6, 1], .012)
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres",
    "mesh": {"tris": [2900, 1000], "cell": .0035},
    "eyes": {"at": [.275, 1.523, .021], "from": [.262, 1.515, 0], "r": .0055, "iris": "@eye", "pupil": "round"},
    "shape": sh,
}
import varB; d = varB.apply(d, "flamingo")   # (B 2026-11-07: its named coats)
save("flamingo", d)
