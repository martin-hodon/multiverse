from bg import *
d = load("duck")
d["_about"] = "a mallard (coats: the drake, the hen) afloat (swim.depth: the waterline at y = .07 in its rest frame): a long boat of a body -- chestnut breast, vermiculated grey flanks, grey-brown back under the folded wings, black rump and curled tail coverts, white tail -- short neck with the white ring, glossy green head, flat yellow bill with its black nail; the hen (coat 1) mottled brown and buff all over, the dark crown and eye stripe, the orange bill with its dark saddle, the same blue speculum between white bars -- aloft (the viewer's fly) the folded wings turn into the body and a spread wing of its own swings out feather by feather (duck.py, nbwing.aloft): grey-brown coverts, the white bar, the blue speculum along the trailing edge, the long grey-brown primaries, pale beneath"
d["colors"] = {"flank": "#b4b0a6", "back": "#80776a", "breast": "#6a3626", "head": "#1d5636", "ring": "#f0eee8", "rump": "#141414",
               "tail": "#d6d3cc", "wing": "#8c847a", "tert": "#a39684", "prim": "#5f584f", "spec": "#2c46b0", "bar": "#f4f2ee",
               "bill": "#d2b838", "nail": "#262620", "eye": "#3a2410", "belly": "#d8d4cc"}
d["colors"].update({"stripe": "#3a2a1c", "saddle": "#3a2e26"})
# (COATS, picked by seed in game: the drake, and the HEN -- mottled brown and buff all over, every feather edged paler
#  (`hen`: the scales pattern over hull, back and breast), the dark crown and the dark stripe through the eye, the orange
#  bill with its dark saddle; her speculum the drake's, blue between white bars. `drake`: his alone -- the curled black
#  coverts over the tail, the white neck ring)
d["params"] = {"drake": True, "hen": False}
d["coats"] = [{"name": "mallard drake"},
              {"name": "mallard hen", "params": {"drake": False, "hen": True},
               "flank": "#9a7a52", "back": "#6a5034", "breast": "#a3845c", "head": "#a08864", "ring": "#a08864", "rump": "#6e5638",
               "tail": "#a88c68", "wing": "#76624c", "tert": "#8a7258", "prim": "#5a4a3a", "bill": "#dc7e2a", "belly": "#b49870",
               "stripe": "#3e2c1c", "saddle": "#3a2c22", "nail": "#2a2018"}]
for p in d["parts"]:
    if p["id"] == "body": p["color"] = "@flank"
sh = [
    # ---- the hull: a long boat, widest at the wings, the breast forward at the waterline ----
    ell("hull", [.0, .105, 0], [.17, .07, .11], "@flank", k=.035, pat={"when": "hen", "v": "scales"}, frame="body"),
    ell("stern", [-.13, .118, 0], [.07, .055, .07], "@flank", k=.035),
    ell("belly", [-.01, .072, 0], [.18, .045, .095], "@belly", k=.03),
    ell("breast", [.11, .12, 0], [.09, .078, .09], "@breast", k=.03, kc=.008, pat={"when": "hen", "v": "scales"}, frame="body"),
    ell("back", [-.02, .162, 0], [.15, .042, .072], "@back", k=.035, rot=[0, 0, 2], pat={"when": "hen", "v": "scales"}, frame="body"),
    ell("rump", [-.175, .15, 0], [.06, .04, .045], "@rump", k=.025, kc=.004, rot=[0, 0, -12]),
    ell("vent", [-.185, .12, 0], [.05, .038, .045], "@rump", k=.02, kc=.004, rot=[0, 0, 15]),
    # ---- neck and ring ----
    # (2026-11-08: on the rig's neck bone -- on the body's, the flight pose swung the head forward and down off a neck
    #  that stayed upright: a green hump standing behind the head, the "broken neck")
    tube("neck", [[.13, .16, 0, .038], [.165, .2, 0, .031], [.195, .24, 0, .03]], "@head", k=.02, kc=.005, bone="neck"),
    {"when": "drake", **ell("ring", [.153, .186, 0], [.005, .0365, .0365], "@ring", k=.002, kc=.0015, rot=[0, 0, 49], bone="neck")},
    # ---- head: round, a little puffed at the cheeks; the bill flat and broad, the nail at its tip ----
    ell("skull", [.212, .268, 0], [.046, .041, .033], "@head", k=.02, bone="head"),
    ell("cheek", [.205, .252, .012], [.036, .03, .024], "@head", k=.015, bone="head", mirror=True),
    ell("crown", [.208, .286, 0], [.04, .024, .027], "@head", k=.018, bone="head"),
    # (the bill: long -- as long as the head -- flat, and widening to its rounded tip: a spatula)
    ell("culmen", [.25, .262, 0], [.02, .01, .0135], "@bill", k=.008, kc=.002, bone="head", rot=[0, 0, -16]),
    ell("bill", [.272, .25, 0], [.03, .0068, .0145], "@bill", k=.006, kc=.002, bone="head", rot=[0, 0, -12]),
    ell("billTip", [.298, .243, 0], [.018, .0052, .0178], "@bill", k=.006, kc=.002, bone="head", rot=[0, 0, -10]),
    ell("lowerBill", [.275, .242, 0], [.034, .0045, .0135], "@bill", k=.004, kc=.002, bone="head", rot=[0, 0, -10]),
    ell("nail", [.314, .241, 0], [.006, .0035, .0075], "@nail", k=.002, kc=.001, bone="head", rot=[0, 0, -12]),
    # ---- tail: a short white fan; the drake's black coverts curling up over it ----
    fea("tail", fan([-.2, .148, 0], [[-1, .2, .5], [-1, .22, .25], [-1, .24, 0], [-1, .22, -.25], [-1, .2, -.5]], [.032, .036, .038, .036, .032], .032), 7,
        "@tail", "@tail", outline="round", up=[0, 1, 0], camber=.22, curve=.04, seed=7),
    # (the fan's thick base, so side-on the tail is a short wedge, not a wire)
    ell("tailBase", [-.214, .152, 0], [.024, .008, .028], "@tail", k=.005, kc=.002, rot=[0, 0, -12]),
    {"when": "drake", **tube("curl", [[-.19, .172, .004, .0065], [-.215, .19, .004, .0055], [-.207, .212, .004, .0045], [-.192, .203, .004, .0035]], "@rump", k=.003, kc=.001)},
    # (the hen's face: the dark crown, the dark stripe from the bill through the eye, the dark saddle on the orange bill)
    {"when": "hen", **ell("henCrown", [.216, .3, 0], [.046, .015, .025], "@stripe", k=.006, kc=.003, bone="head", rot=[0, 0, -6])},   # (proud of the crown by a few mm: it reads)
    {"when": "hen", **ell("eyeStripe", [.226, .274, .022], [.034, .0045, .008], "@stripe", k=.002, kc=.0015, bone="head", rot=[0, 0, -8], mirror=True)},
    {"when": "hen", **ell("saddle", [.262, .26, 0], [.022, .006, .0105], "@saddle", k=.002, kc=.0015, bone="head", rot=[0, 0, -14])},
]
# ---- the folded wings, high on the back: grey-brown coverts, the white bar of their tips over the blue speculum (the
#      secondaries, white-tipped), the primaries crossing over the rump; the tertials over them on the back ----
fold = fold_wing(sh, [.06, .178, .072], [-.175, .182, .03], .05, .017,
                 {"cov": "@wing", "gcov": "@wing", "gcovTip": "@bar", "sec": "@spec", "secTip": "@spec", "prim": "@prim"}, n=(4, 4, 5, 3), up=(0, .45, 1), proot=.12)
# ---- ALOFT (2026-11-08): the folded tracts each turned half round into the body, and a SPREAD wing of its own swung out
#      feather by feather (nbwing.aloft, as the goose's) -- before, the folded wing itself was swung out and rolled flat, its
#      feathers then pointing OUT along the span: from the front and the quarter a few separate blades with gaps, the
#      speculum a thin blue line. Now: grey-brown lesser coverts at the leading edge, the greater coverts' white bar, the
#      blue speculum (the secondaries) along the arm's trailing edge, the primaries fanned on the hand; the greater
#      coverts white beneath (their own colour under the grey band laid over them). (The secondaries white under a blue
#      band read as blue scales rimmed white -- the band is a shorter blade -- so they are blue through.) ----
import nbwing
d["parts"] = [p for p in d["parts"] if not (p["id"][-1] in "LR" and p["id"][:-1].startswith(("wfold", "wroll", "wext", "wlift", "wtip", "ws", "wf")))]
for p in d["parts"]:
    if p["id"] in ("wingL", "wingR"): p.pop("flyRot", None)
W = dict(nbwing.WING); W["bands"] = {"gcov": [(.8, "@wing")]}
info = nbwing.aloft(d, sh, {"spread": dict(span=1.6, armF=.4, asp=3.0, tipC=.3, hsweep=.4, pinch=.7), "flight": {"speed": 1.4}},
                    [.06, .178, .072], .55, d["colors"], fold, W, "big", nrm([0, .45, 1]), .0025, .235,
                    tk={"c": [0, .13, 0], "r": [.17, .07, .1]},   # (the hull's core, a little up: the wing set high on the back)
                    fold_bands=False, add_fold=False,
                    look_over={"sec": ("@spec", "@spec"), "gcov": ("@bar", "@bar"), "cov": ("@wing", "@wing"), "pcov": ("@wing", "@wing"), "prim": ("@prim", "@prim")})
print("  duck aloft:", info)
d["flags"]["flight"] = {"arm": 0, "hand": 0, "beat": 44, "bob": .03, "hind": [-80, 10, -40], "neck": 8}
sh.append(fea("tert", [row([-.02, .198, .05], [-.15, .2, .03], .02), row([-.05, .198, .042], [-.17, .195, .02], .018)], 3,
              "@tert", "@back", outline="round", up=[0, 1, .5], camber=.14, curve=-.03, seed=5, mirror=True))
# (the flank: the drake's grey vermiculated feathers, covering the wing's lower edge down to the water)
FL = [row([.09, .15, .085], [-.03, .14, .1], .028), row([.04, .125, .1], [-.09, .125, .1], .028), row([-.02, .1, .1], [-.15, .11, .085], .026)]
sh.append({"when": "drake", **fea("flankF", json.loads(json.dumps(FL)), 8,
              "@flank", ["@fedge", "@flank"], outline="round", up=[0, .2, 1], camber=.08, curve=-.02, stagger=.001, vary=.3, jitter=.16, seed=8, mirror=True)})   # (fedge: the Pekin's feather edges)
# (the hen's: the same flank feathers, dark-centred and buff-edged, all of a length -- no hole in them showing the body's
#  mottling through as a round stamp)
sh.append({"when": "hen", **fea("flankH", json.loads(json.dumps(FL)), 10,
              "@back", "@flank", outline="round", up=[0, .2, 1], camber=.08, curve=-.02, stagger=.001, jitter=.04, seed=8, mirror=True)})
place(sh, ["tert"], [0, 1, .3], .004)
for s in sh:
    if s.get("id") in ("flankF", "flankH"): conform(sh, s, .0007)   # (lying on the flank, its edges sinking into the grey)
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; afloat at the waterline y = .07",
    "mesh": {"tris": [4400, 1300], "cell": .003},
    "shade": {"when": "pekin", "v": {"back": 1.0, "belly": .88, "k": .05}},   # (the Pekin's white shaded under: varB)
    "eyes": {"at": [.234, .276, .0245], "from": [.212, .266, 0], "r": .0065, "iris": "@eye", "pupil": "round"},
    "shape": sh,
}
d["flags"]["flight"].update(neck=12, head=.8)   # (2026-11-08: the neck reached straight forward, the head in line with it)
import varB; d = varB.apply(d, "duck")   # (B 2026-11-07: its named coats)
save("duck", d)
