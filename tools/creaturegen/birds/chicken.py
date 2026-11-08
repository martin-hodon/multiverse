from bg import *
d = load("chicken")
parts = [p for p in d["parts"] if not p["id"].startswith(("toe", "hind", "footL", "footR"))]
for side, z in (("L", 1), ("R", -1)):
    parts.append({"id": "foot" + side, "parent": "leg" + side, "shape": "sphere", "size": {"r": .006}, "pos": [0, -.14, 0], "color": "@leg",
                  "anim": {"axis": "z", "deg": -28, "speed": .8, "phase": 0 if z > 0 else 3.14}})
for p in parts:
    if p["id"] == "head": p["pos"] = [.15, .17, 0]
d["parts"] = parts
d["params"] = {"rooster": False, "hen": True}
d["variants"]["rooster"]["params"] = {"rooster": True, "hen": False}
C = d["colors"]
C.setdefault("eye", "#c8861e"); C.setdefault("claw", "#b89a6a"); C.setdefault("face", "#c8372b")
d["variants"]["rooster"]["colors"].update({"saddle": "#d1902e", "hackle": "#d9a038"})
C.setdefault("saddle", C["body"]); C.setdefault("hackle", C["head"])
for c in d["coats"]:
    if "body" in c: c.setdefault("saddle", c["body"]); c.setdefault("hackle", c["head"])

sh = []
# ---- trunk: a round breast forward and low, the back sloping up into the tail ----
sh += [
    ell("breast", [.07, .232, 0], [.088, .09, .074], "@breast", k=.03),
    ell("trunk", [-.03, .245, 0], [.13, .085, .074], "@body", k=.04, rot=[0, 0, -8]),
    ell("keel", [.02, .175, 0], [.085, .05, .062], "@breast", k=.035),
    ell("belly", [-.06, .19, 0], [.085, .06, .064], "@breast", k=.04),
    ell("saddle", [-.07, .3, 0], [.1, .042, .062], "@saddle", k=.035, rot=[0, 0, -14]),
    ell("rump", [-.125, .3, 0], [.06, .07, .05], "@saddle", k=.035, rot=[0, 0, -40]),
    ell("vent", [-.12, .215, 0], [.045, .05, .05], "@breast", k=.035),
]
# ---- neck: thick with hackles at its base, narrowing to the head ----
sh += [
    tube("neck", [[.075, .27, 0, .045], [.11, .325, 0, .034], [.138, .375, 0, .027], [.15, .395, 0, .025]], "@hackle", k=.022, bone="neck"),
    ell("hackle", [.07, .305, 0], [.05, .05, .058], "@hackle", k=.025, rot=[0, 0, -40], bone="neck"),
    ell("throat", [.115, .315, 0], [.03, .045, .034], "@breast", k=.018, bone="neck", rot=[0, 0, -35]),
]
# ---- head: a small round skull, red bare face, beak, comb, wattles, lobes ----
H = "head"
hs = [
    ell("skull", [.135, .388, 0], [.037, .032, .028], "@head", k=.016, bone=H),
    ell("nape", [.118, .372, 0], [.03, .03, .027], "@hackle", k=.016, bone=H),
    ell("face", [.152, .382, .014], [.02, .016, .012], "@face", k=.01, kc=.003, bone=H, mirror=True),
    ell("lobe", [.124, .37, .024], [.008, .01, .0045], "@lobe", k=.004, kc=.002, bone=H, mirror=True),
    tube("upperBill", [[.158, .392, 0, .0105], [.176, .389, 0, .0075], [.19, .382, 0, .0045], [.197, .373, 0, .0016]], "@beak", k=.004, kc=.001, bone=H),
    tube("lowerBill", [[.157, .378, 0, .008], [.172, .376, 0, .0055], [.184, .374, 0, .0022]], "@beak", k=.003, kc=.001, bone=H),
    # (hen: a small single comb and short wattles)
    {"when": "hen", **ell("comb", [.138, .42, 0], [.032, .011, .0055], "@comb", k=.006, kc=.002, bone=H, rot=[0, 0, -8])},
    {"when": "hen", **ell("combP1", [.115, .426, 0], [.007, .011, .005], "@comb", k=.005, kc=.002, bone=H, rot=[0, 0, 25])},
    {"when": "hen", **ell("combP2", [.13, .432, 0], [.007, .012, .005], "@comb", k=.005, kc=.002, bone=H, rot=[0, 0, 10])},
    {"when": "hen", **ell("combP3", [.146, .43, 0], [.007, .011, .005], "@comb", k=.005, kc=.002, bone=H, rot=[0, 0, -8])},
    {"when": "hen", **ell("combP4", [.16, .422, 0], [.006, .009, .0045], "@comb", k=.005, kc=.002, bone=H, rot=[0, 0, -25])},
    {"when": "hen", **ell("wattle", [.163, .358, .005], [.009, .014, .0045], "@comb", k=.005, kc=.002, bone=H, mirror=True)},
    # (rooster: the tall serrated comb, long wattles)
    {"when": "rooster", **ell("comb", [.135, .425, 0], [.042, .018, .006], "@comb", k=.007, kc=.002, bone=H, rot=[0, 0, -6])},
    {"when": "rooster", **ell("combP1", [.102, .438, 0], [.009, .018, .0055], "@comb", k=.006, kc=.002, bone=H, rot=[0, 0, 40])},
    {"when": "rooster", **ell("combP2", [.118, .452, 0], [.009, .02, .0055], "@comb", k=.006, kc=.002, bone=H, rot=[0, 0, 20])},
    {"when": "rooster", **ell("combP3", [.136, .456, 0], [.009, .02, .0055], "@comb", k=.006, kc=.002, bone=H, rot=[0, 0, 2])},
    {"when": "rooster", **ell("combP4", [.153, .45, 0], [.008, .018, .0055], "@comb", k=.006, kc=.002, bone=H, rot=[0, 0, -16])},
    {"when": "rooster", **ell("combP5", [.167, .436, 0], [.007, .014, .005], "@comb", k=.006, kc=.002, bone=H, rot=[0, 0, -35])},
    {"when": "rooster", **ell("wattle", [.164, .346, .006], [.011, .024, .005], "@comb", k=.006, kc=.002, bone=H, mirror=True)},
]
sh += shift(hs, [.02, .022, 0])
# ---- legs: feathered drumstick, bare yellow scaly tarsus, four toes (three forward, the hallux back) ----
sh += [
    ell("thigh", [.01, .175, .048], [.045, .05, .034], "@body", k=.025, bone="legL", rot=[0, 0, 12], mirror=True),
    ell("drum", [.012, .128, .044], [.026, .036, .022], "@breast", k=.015, bone="legL", mirror=True),
    cone("tarsus", [.014, .1, .042], [.016, .022, .042], .0078, .0064, "@leg", k=.004, bone="legL", mirror=True, pat="scales",
         frame={"o": "$legL", "u": [0, -1, 0], "r": .02}),
    {"when": "rooster", **cone("spur", [.012, .045, .042], [-.004, .04, .042], .003, .001, "@claw", k=.002, bone="legL", mirror=True)},
    cone("toeM", [.017, .016, .042], [.07, .006, .044], .0055, .003, "@leg", k=.003, bone="footL", mirror=True),
    cone("toeO", [.017, .016, .045], [.056, .006, .07], .005, .003, "@leg", k=.003, bone="footL", mirror=True),
    cone("toeI", [.017, .016, .039], [.058, .006, .018], .005, .003, "@leg", k=.003, bone="footL", mirror=True),
    cone("hallux", [.012, .018, .042], [-.016, .007, .04], .0045, .0028, "@leg", k=.003, bone="footL", mirror=True),
]
# ---- folded wing: the covert mass hugging the flank, the tracts of coverts, secondaries and primaries over it, the
#      primaries' tips crossing over the tail's base ----
sh += [ell("wing", [-.02, .262, .05], [.1, .055, .02], "@wing", k=.02, rot=[-8, 0, -6], mirror=True)]
fold_wing(sh, [.065, .285, .07], [-.13, .272, .05], .07, .02,
          {"cov": "@wing", "covTip": "@body", "gcov": "@wing", "gcovTip": "@tail", "sec": "@body", "secTip": "@tail", "prim": "@tail", "primTip": "@tail"},
          n=(4, 4, 5, 3), up=(0, .2, 1), flush=True, base=.0015, step=.0015)
# ---- the neck's hackles: narrow pointed feathers draping from the nape over the shoulders (the hen's dark-centred,
#      the rooster's long and golden) ----
def hackles(L, w, n, col, tip, when, c=(.122, .352, 0), outline="flight", curve=-.02):
    ax = nrm([.51, .86, 0]); fw = [.86, -.51, 0]
    rows = []
    for i in range(5):
        ph = math.radians(35 + 140 * i / 4)                      # (round the neck from the throat's side to the nape)
        rad = add([fw[k] * math.cos(ph) for k in range(3)], [0, 0, math.sin(ph)])
        at = add(list(c), rad, .03)
        to = add(at, nrm(add([-a for a in ax], rad, .35 + .15 * i / 4)), L)
        rows.append(row(at, to, w, bone="neck", up=rad))
    return {"when": when, **fea("hackleF", rows, n, col, tip, outline=outline, bone="neck", camber=.1, curve=curve, stagger=.0012,
                                lift=.002, seed=41, mirror=True)}
sh.append(hackles(.05, .019, 9, "@hackle", "@hackle", "hen", outline="round", curve=-.03))   # (the hen's: soft rounded scales of a cape, not spikes)
sh.append(hackles(.1, .012, 10, "@hackle", "@saddle", "rooster"))
# ---- tail: a tent of broad rounded feathers, raised about 45 degrees ----
tail_dirs = [[-.35, 1, .1], [-.6, .85, .13], [-.82, .6, .15], [-.95, .32, .16], [-1, .1, .16]]
roots = [[-.1, .31, .012], [-.105, .31, .014], [-.11, .305, .016], [-.115, .3, .017], [-.12, .29, .017]]
sh += [
    fea("tail", fan(roots, tail_dirs, [.11, .13, .135, .125, .105], .03), 5, "@tail", "@tail", outline="round", up=[0, 0, 1], camber=.14, curve=.03,
        stagger=.002, seed=21, mirror=True, **{"when": "hen"}),
]
# (the rooster: the saddle hackles falling over the wing's end, a tail of black-green feathers and the sickles arching
#  up and over it in a cascade)
def sickle(id, root, ang, L, bend, w, z, seed):
    a = math.radians(ang); dv = [-math.cos(a), math.sin(a), z]; up = [-math.sin(a), -math.cos(a), 0]
    rows = [row(root, add(root, nrm(dv), L), w, up=up), row(add(root, [-.004, -.006, .006]), add(add(root, [-.004, -.006, .006]), nrm(dv), L * .96), w, up=up)]
    return {"when": "rooster", **fea(id, rows, 2, "@sickle", "@sickle", outline="flight", camber=.14, curve=bend, seed=seed, mirror=True)}
sh += [
    {"when": "rooster", **fea("tail", fan(roots, tail_dirs, [.15, .18, .19, .17, .14], .03), 5, "@sickle", "@sickle", outline="round", up=[0, 0, 1],
        camber=.14, curve=.03, stagger=.002, seed=21, mirror=True)},
    sickle("sickleA", [-.105, .33, .008], 64, .3, 1.3, .028, .03, 51),
    sickle("sickleB", [-.11, .32, .014], 54, .27, 1.1, .026, .06, 52),
    sickle("sickleC", [-.115, .31, .018], 44, .23, .9, .024, .09, 53),
    {"when": "rooster", **fea("saddleF", [row([-.03, .305, .04], [-.12, .24, .07], .009), row([-.06, .305, .03], [-.15, .25, .06], .009),
                                          row([-.09, .3, .02], [-.17, .26, .045], .009)], 7,
        "@saddle", "@saddle", outline="flight", up=[0, .6, 1], camber=.12, curve=.04, stagger=.0015, seed=31, mirror=True)},
]
for s in sh:
    if s.get("id") == "hackleF": conform(sh, s, .0025)
place(sh, ["saddleF"], [0, 1, .4], .004)
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; a hen's plump teardrop -- round breast low and forward, back sloping up into a tent of tail feathers -- thick hackled neck, small head with red bare face, comb, wattles and lobes, folded wings of coverts with secondaries and primaries over the flank, feathered drumsticks over bare scaly yellow tarsi and four toes (the feet kept level by footL/footR); `rooster`: tall comb, long wattles, saddle feathers, a black-green tail and three arched sickles",
    "mesh": {"tris": [4800, 1400], "cell": .0028},
    "shade": {"back": .82, "belly": 1.1, "k": .07},
    "eyes": {"at": [.171, .419, .026], "from": [.152, .414, 0], "r": .0072, "iris": "@eye", "pupil": "round"},
    "shape": sh,
}
save("chicken", d)
