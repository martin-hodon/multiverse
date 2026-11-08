from bg import *
from wader import legs, leg_shapes
import sys
d = load("peacock")
d["_about"] = "an Indian peacock walking with his train: a pheasant's body on grey-brown legs -- cobalt-blue neck and breast, the back bronze-green and scaled, the folded wing barred buff and black over dark secondaries -- a small blue head with the white face stripes and the fan of blue-tipped crest shafts; over the rump the domed mass of the train's bases, and the TRAIN itself: tiers of bronze-green feathers each ending in its eye and fringe, sloping down from the rump to the ground and trailing along it for half its length, the eyes scattered over it like scales (each tier its own length, the shorter laid over the longer); `display` (variants.display) raises it into the upright fan, a wall of eyes"
d["colors"] = {"blue": "#1a46b0", "deep": "#14307e", "bronze": "#4f6e26", "green": "#2e5a2a", "buff": "#c2ad80", "chestnut": "#5a3418",
               "dark": "#1b2430", "face": "#f2f0ea", "beak": "#a89a88", "leg": "#8f8579", "train": "#34501c", "trainTip": "#587a26", "eye": "#1a1210",
               "grey": "#6a6258", "belly": "#1c2a1e", "black": "#1a1814", "base": "#2f4a1c"}
d["colors"].update({"stripe": "#3a3024", "crestTip": "#1a46b0", "hgreen": "#25705a", "hbreast": "#86725a"})
d["params"] = {"display": False, "walking": True, "cock": True, "hen": False}
# (PEAHEN, the variant: no train at all -- `walking` and `display` both off, `cock` off (the train's domed bases, the
#  spurs), `hen` on (her short brown tail, the dark stripe through the white face, the white throat); brown-grey above,
#  the neck and upper breast metallic green, white below, the crest brown with green tips)
d["variants"] = {"display": {"params": {"display": True, "walking": False}},
                 "peahen": {"params": {"display": False, "walking": False, "cock": False, "hen": True},
                            "colors": {"blue": "#7a6650", "crestTip": "#2c7a58", "beak": "#8c8a84", "deep": "#5a4636", "bronze": "#7a6a56", "green": "#5e5444", "buff": "#8a7458",
                                       "dark": "#4a3e32", "belly": "#ece6da", "grey": "#6a6258", "base": "#6e604e", "train": "#6e604e", "trainTip": "#5a4e40",
                                       "stripe": "#3a3024"}}}
DY = -.085                       # (the legs a fifth shorter than they were: everything above them this much lower)
BY = .52 + DY
d["_bodyY"] = BY
parts = [p for p in d["parts"] if not p["id"].startswith(("plume", "tail"))]
for p in parts:
    if p["id"] == "body": p["pos"] = [0, BY, 0]; p["color"] = "@blue"; p["size"] = {"r": .1, "len": .26}
    if p["id"] == "neck": p["pos"] = [.15, .08, 0]; p["rot"] = [0, 0, -14]
    if p["id"] == "head": p["pos"] = [.011, .224, 0]; p.pop("scale", None)
    if p["id"] in ("legL", "legR"): p["pos"][0] = .02
parts.append({"id": "tail", "parent": "body", "shape": "sphere", "size": {"r": .02}, "pos": [-.19, .08, 0], "color": "@train",
              "anim": {"axis": "y", "deg": 2, "speed": .22, "phase": 0}})
d["parts"] = parts
legs(d, .43 + DY, .17 * .8, 20, .8, 24)
del d["_bodyY"]
for p in d["parts"]:
    if p["id"].startswith(("leg", "tars", "foot")): p["color"] = "@leg"
# ---- the body, written at the old height and lowered by DY at the end ----
sh = [
    ell("breast", [.14, .54, 0], [.105, .11, .09], "@blue", k=.05, kc=.012),
    ell("trunk", [-.02, .53, 0], [.21, .11, .108], "@bronze", k=.05, kc=.02),
    ell("back", [-.05, .6, 0], [.18, .05, .085], "@bronze", k=.04, pat="scales", frame="body"),
    ell("belly", [.02, .45, 0], [.16, .065, .085], "@belly", k=.05, kc=.02),
    # (the peahen's green stops at the upper breast: the lower breast brown-grey, scaled, down to the white belly)
    {"when": "hen", **ell("henBreast", [.142, .535, 0], [.108, .112, .093], "@hbreast", k=.04, kc=.02, pat="scales", frame="body")},
    # (the train's bases: a domed mass over the rump, scaled bronze-green, sloping down into the train)
    {"when": "cock", **ell("mass", [-.24, .585, 0], [.17, .075, .1], "@bronze", k=.06, kc=.04, rot=[0, 0, -22], pat="scales", frame="body")},
    tube("neck", [[.12, .58, 0, .052], [.17, .66, 0, .04], [.2, .74, 0, .032], [.21, .8, 0, .028]], "@blue", k=.03, kc=.008, bone="neck"),
    ell("skull", [.215, .815, 0], [.04, .03, .027], "@blue", k=.016, bone="head", rot=[0, 0, -8]),
    ell("brow", [.226, .826, .02], [.024, .006, .006], "@face", k=.004, kc=.0015, bone="head", rot=[0, 0, -4], mirror=True),
    ell("cheek", [.23, .806, .02], [.018, .008, .006], "@face", k=.004, kc=.0015, bone="head", rot=[0, 0, -10], mirror=True),
    tube("beak", [[.248, .815, 0, .0095], [.266, .809, 0, .0068], [.279, .8, 0, .0035], [.282, .794, 0, .0012]], "@beak", k=.004, kc=.0012, bone="head"),
    ell("wing", [-.01, .565, .075], [.15, .06, .035], "@bronze", k=.03, rot=[-14, 0, -4], mirror=True),
    # (the hen's: the dark stripe through the eye, the white throat, and her short brown tail -- no train)
    {"when": "hen", **ell("henStripe", [.236, .818, .021], [.028, .0045, .006], "@stripe", k=.002, kc=.0015, bone="head", rot=[0, 0, -6], mirror=True)},
    # (her metallic green: the lower neck only, a collar above the brown breast; the head and the upper neck brown)
    {"when": "hen", **ell("henNeckG", [.152, .632, 0], [.06, .056, .056], "@hgreen", k=.016, kc=.004, bone="neck", rot=[0, 0, 58])},
    {"when": "hen", **ell("henThroat", [.226, .795, 0], [.02, .014, .018], "@face", k=.008, kc=.003, bone="head")},
    {"when": "hen", **ell("henRump", [-.2, .57, 0], [.08, .05, .07], "@bronze", k=.04, kc=.02, rot=[0, 0, -14], pat="scales", frame="body")},
    {"when": "hen", **fea("henTail", fan([-.21, .575, 0], [[-1, .12, .42], [-1, .16, 0], [-1, .12, -.42]], [.2, .23, .2], .032), 9, "@bronze", "@dark",
                          bone="tail", outline="round", up=[0, 1, 0], camber=.12, curve=.02, seed=71)},
]
# (the crest: twenty bare shafts in a fan, each ending in its little blue fan)
for i in range(20):
    u = i / 19; a = -20 + 68 * u
    root = [.224 - .022 * u, .838 - .004 * abs(u - .5), .006 * (1 if i % 2 else -1)]
    dv = rotz([0, 1, 0], a); L = .056 - abs(a - 14) * .00018
    sh.append(cone(f"crest{i}", root, add(root, dv, L), .0011, .0008, "@deep", k=.0006, bone="head"))
    sh.append(ell(f"crestTip{i}", add(root, dv, L + .002), [.006, .0048, .0018], "@crestTip", k=.001, kc=.0006, bone="head", rot=[0, 0, a]))
# (the folded wing: barred buff coverts over the dark secondaries, the chestnut primaries tucked under the train)
fold_wing(sh, [.1, .6, .09], [-.15, .565, .075], .1, .026,
          {"cov": "@buff", "covTip": "@buff", "gcov": "@buff", "gcovTip": "@black", "sec": "@dark", "secTip": "@black", "prim": "@dark", "primTip": "@black"},
          n=(5, 5, 4, 2), bars=None, flush=True, base=.002, step=.0018)
for s in sh:
    if s.get("id") in ("cov", "gcov"):
        s["bars"] = {"n": 5, "dark": .45}
        for r in s["rows"]: r["w"] = round(r["w"] * .8, 4)
sh = shift(sh, [0, DY, 0])
sh += leg_shapes([.02, .43 + DY, .05], .17 * .8, .011, .013, .0095, "@leg", "@dark", [.05, .06, .042], .06, hallux=.03)
sh.append({"when": "cock", **cone("spur", [.025, .085, .05], [.005, .08, .05], .004, .0012, "@grey", k=.002, bone="tarsL", mirror=True)})

# ---- THE TRAIN (walking): from the rump R the SLOPE tiers run down to the ground, each its own length so their eyes lie
#      down the slope; from where they reach it the GROUND tiers lie flat behind, their roots hidden under the slope's
#      ends; one straight profile for every slope tier (curve ~ its length), each tier lifted over the one beneath ----
R = [-.36, .535 + DY]; GY = .052
TH, PH = 58, 18                  # (the slope: leaving the rump TH degrees down, reaching the ground PH degrees down -- concave)
th = math.radians(TH); KL = math.tan(math.radians(TH - PH)) / 2       # (kappa * L of the longest: its tangent turned TH - PH)
SL = (R[1] - GY) / (math.sin(th) - math.cos(th) * KL)               # (its length, to reach the ground)
KAP = KL / SL
XC = R[0] - SL * (math.cos(th) + math.sin(th) * KL)                  # (where it reaches the ground)
def eye_at(L, w, r=.78): return round(min(.87, 1 - .08 - 1.3 * r * w / L), 3)
def slope_tier(id, n, L, w0, w1, lift, seed):
    rows = []
    for i in range(5):
        s = 1 - 2 * i / 4
        at = [R[0] + .03 * abs(s), R[1] - .015 * abs(s), s * .07]
        dv = nrm([-math.cos(th), -math.sin(th), s * .42 * L / SL])
        rows.append(row(at, add(at, dv, L), w0 + (w1 - w0) * abs(s)))
    return fea(id, rows, n, "@train", "@trainTip", bone="tail", outline="train", up=[-math.sin(th), math.cos(th), 0],
               camber=.06, curve=round(KAP * L, 4), lift=lift, vary=.14, jitter=.06, stagger=.003, ocellus={"at": eye_at(L, w1, .74), "r": .74}, seed=seed)
def ground_tier(id, n, x0, x1, half0, half1, w, y, seed):
    rows = []
    for i in range(5):
        s = 1 - 2 * i / 4
        at = [x0 + .03 * abs(s), y, s * half0]
        to = [x1 + .05 * s * s, .02 + (y - .025) * .3, s * half1]
        rows.append(row(at, to, w))
    L = x0 - x1
    return fea(id, rows, n, "@train", "@trainTip", bone="tail", outline="train", up=[0, 1, 0], camber=.05, curve=.0,
               vary=.12, jitter=.05, stagger=.002, ocellus={"at": eye_at(L, w), "r": .8}, seed=seed, layer=True)
def bed(id, n, L, w, lift, seed, ground=False):
    """an underlay of broad plain blades beneath a tier group: the bronze between the feathers' eyes (their loose barbs)"""
    rows = []
    for i in range(3):
        s = 1 - i
        if ground:
            at = [XC + .16 + .03 * abs(s), .021, s * .18]; to = [-1.42, .02, s * .3]   # (its roots on the ramp, below)
            rows.append(row(at, to, w))
        else:
            at = [R[0] + .02, R[1] - .008, s * .09]
            rows.append(row(at, add(at, nrm([-math.cos(th), -math.sin(th), s * .45]), L), w))
    kw = {"layer": True} if ground else {"curve": round(KAP * L, 4)}   # (the ground's bed lies on the train, not the body: a LAYER, bg.root_feathers)
    return fea(id, rows, n, "@base", "@train", bone="tail", outline="round", up=[0, 1, 0] if ground else [-math.sin(th), math.cos(th), 0], camber=.03,
               lift=lift, seed=seed, **kw)
# (the RAMP: a hidden bronze sheet from the underside of the slope's bed down to the ground, through the ground tiers'
#  roots -- they rest on it, it on the bed (bg.root_feathers carries its root back along it until it meets the bed))
RK = .35
def ramp(id, n, w, seed):
    rows = []
    for i in range(5):
        s = 1 - 2 * i / 4
        A_ = [XC + .14 + .03 * abs(s), .026, s * .2]                  # (groundA's root: the ramp's line runs through it)
        rows.append(row(add(A_, [-1, RK, 0], .05), add(A_, [1, -RK, 0], .016 / RK), w))
    return fea(id, rows, n, "@base", "@train", bone="tail", outline="round", up=nrm([RK, 1, 0]), camber=.02, stagger=.0012, seed=seed, reach=True)
train = [
    # (C r10, the budget: 24k -> under 20k -- each tier a feather or two fewer, the blades as much broader (n_old/n_new)^.8)
    ramp("bedR", 5, .12, 38),
    bed("bedG", 5, 0, .13, -.004, 39, ground=True),
    bed("bedS", 7, SL * 1.08, .09, -.006, 40),
    ground_tier("groundA", 7, XC + .14, -1.46, .2, .36, 0.061, .026, 41),
    ground_tier("groundB", 6, XC + .12, -1.3, .2, .33, 0.068, .033, 42),
    ground_tier("groundC", 5, XC + .1, -1.14, .19, .29, 0.069, .04, 43),
    slope_tier("slopeA", 6, SL * 1.04, .052, .065, .0, 44),
    slope_tier("slopeB", 5, SL * .8, .052, .065, .007, 45),
    slope_tier("slopeC", 5, SL * .58, .044, .054, .014, 46),
    slope_tier("slopeD", 3, SL * .38, .05, .06, .021, 47),
]
# (the train's coverts: short eyed feathers from the rump over the mass's end and down the slope's start, each tier
#  shorter and higher -- the eyes begin a hand's breadth behind the rump, smaller there, and the wedge widens from it)
def cover_tier(id, n, L, w, x0, half, lift, seed):
    rows = []
    for i in range(5):
        s = 1 - 2 * i / 4
        at = [x0 + .02 * abs(s), R[1] + (x0 - R[0]) * .55 + .012, s * half]
        dv = nrm([-math.cos(th) * 1.25, -math.sin(th) * .8, s * .5])
        rows.append(row(at, add(at, dv, L), w))
    return fea(id, rows, n, "@train", "@trainTip", bone="tail", outline="train", up=[-math.sin(th) * .7, math.cos(th), 0], camber=.06, curve=.02,
               lift=lift, vary=.12, jitter=.06, stagger=.003, ocellus={"at": eye_at(L, w, .6), "r": .6}, seed=seed)
covers = [cover_tier("coverA", 6, .42, .053, -.3, .12, .028, 61), cover_tier("coverB", 5, .3, .058, -.26, .11, .034, 62),
          cover_tier("coverC", 4, .19, .058, -.22, .1, .04, 63)]
train += covers
print("slope", round(SL, 3), "contact", round(XC, 3))
sh += [{"when": "walking", **t} for t in train]
place(sh, ["coverA", "coverB", "coverC"], [-.3, 1, 0], .004)

# ---- DISPLAY (the variant): the train raised into the upright fan behind him -- four tiers, over a hundred feathers, a
#      wall of eyes (each tier's eyes a ring inside the last's) ----
def fanTier(id, n, L, half, w, back, seed):
    rows = []
    for i in range(5):
        a = math.radians(-half + 2 * half * i / 4)
        at = [-.2 - back, .6 + DY + .02, math.sin(a) * .04]
        dv = nrm([-.1, math.cos(a), math.sin(a)])
        rows.append(row(at, add(at, dv, L), w, up=[1, .1 * math.cos(a), 0]))
    return fea(id, rows, n, "@train", "@trainTip", bone="tail", outline="train", camber=.05, curve=.03,
               lift=back, vary=.05, stagger=.003, ocellus={"at": eye_at(L, w), "r": .78}, seed=seed)
disp = [fanTier("fanA", 30, .95, 80, .058, 0, 51), fanTier("fanB", 28, .78, 78, .054, .01, 52), fanTier("fanC", 24, .6, 76, .05, .02, 53),
        fanTier("fanD", 20, .42, 72, .045, .03, 54)]
sh += [{"when": "display", **t} for t in disp]
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres",
    "mesh": {"tris": [2800, 1200], "cell": .0045},
    "eyes": {"at": [.232, .818 + DY, .022], "from": [.215, .815 + DY, 0], "r": .0065, "iris": "@eye", "pupil": "round"},
    "shape": sh,
}
if "--display" in sys.argv: d["params"] = {"display": True, "walking": False, "cock": True, "hen": False}
for t in sh:   # (the TRAIN, every walking tier: exempt from the root pass -- its blades rest on the body or on the tier under it)
    if t.get("type") == "feathers" and t.get("when") == "walking": t["layer"] = True
save("peacock", d)
