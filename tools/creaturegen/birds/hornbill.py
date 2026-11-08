# hornbill.py -- the great hornbill (2026-11-07): a flier from the macaw's plan (flier.py: spread wings on rig_wings, a
#   fanned tail, the legs perched -- perch/perchlegs.py), authored at the macaw's size and scaled to its own. A forest
#   percher: perchers.js PERCHERS.hornbill takes it down onto the boughs.
import sys, math
from bg import *
from flier import rig_wings, wing, tail_fan
from raptor import scale_parts

s = 1.3   # (authored at the macaw's size: bill tip to tail tip .85 m -> 1.1 m; span 1.5 m)
d = load("parrot")
d["name"] = "hornbill"
d["_about"] = "a great hornbill in flight: the big black-and-white bird of the forest canopy -- the huge, gently down-curved bill, blunt at its tip, yellow with an orange-red base, and over it the great flat-topped casque, broad, flat-topped and U-shaped from the front, yellow, black where it meets the forehead; the head and face black, the neck and shoulders creamy yellow-white; black wings crossed by a broad pale bar and edged white behind; the long white tail with a broad black band across it; white thighs and vent, a red eye; grey feet that close round a bough"
d["colors"] = {"black": "#141414", "back": "#161616", "cream": "#f2e8c4", "neck": "#efe2b0", "white": "#f4f2ea", "wbar": "#f0e6c0",
               "bill": "#f2c43a", "billR": "#e2622a", "billTip": "#f4e6a8", "lower": "#f0d27a", "casque": "#eaa83a", "casqueK": "#1a1614",
               "foot": "#5e6466", "eye": "#c8241c", "skin": "#1e1a1a", "lining": "#181818", "tipW": "#efece2"}
d["flags"] = {"fly": {"alt": [5, 40], "speed": [3.5, 6], "hz": 1.0}, "active": "day", "print": "bird"}
for k in ("coats", "params", "variants"): d.pop(k, None)
for p in d["parts"]:
    if p["id"] == "body": p["color"] = "@black"
    if p["id"] == "head": p["pos"] = [.145, .04, 0]; p["color"] = "@neck"
    if p["id"] == "beak": p["color"] = "@bill"; p["size"] = {"r": .02, "h": .17}
    if p["id"] == "tail": p["color"] = "@white"
    if p["id"].startswith("patch"): p["color"] = "@skin"
rig_wings(d, .3, [.02, .318, .05], .25, 34, 16, 1.0, dih=.03)

def bill(base, L):
    """the bill: big, deep and laterally flattened, GENTLY down-curved, as long as the head and neck together, its tip
       blunt -- an upper mandible of ellipsoids tapering only to a rounded point (orange-red at its base), the lower slimmer
       under it; and over the upper's basal half the CASQUE: broad, flat-topped and U-shaped seen from the front (its two
       side ridges standing a little above its middle), yellow, black where it meets the forehead"""
    out = []; n = 30   # (C r9: finer links -- a smooth curve, not a plank of blocks)
    # (C r7: shorter, thicker, only mildly decurved, tapering smoothly; the casque ONE mass with the upper mandible --
    #  its ellipsoids sunk deep into the culmen and blended, as wide as the bill, flat-topped with the side ridges a
    #  little proud of the middle (the U from the front), its front end squared and turned up; the red only a patch)
    def cl(f):   # (the culmen's line: a mild down-curve)
        a = math.radians(-(7 + 9 * f * f)); return [base[0] + math.cos(a) * L * f, base[1] + math.sin(a) * L * f]
    def ryf(f): return .025 * (1 - .62 * f ** 1.25)
    def rzf(f): return .0135 * (1 - .5 * f)
    for i in range(n):
        f = i / (n - 1); p = cl(f); a = -(7 + 9 * f * f)
        ry = ryf(f) * (1 if f < .93 else math.sqrt(max(.25, 1 - ((f - .93) / .1) ** 2))); rz = rzf(f)
        col = "@billR" if f < .03 else "@billTip" if f > .9 else "@bill"
        out.append(ell("upper%d" % i, [p[0], p[1] - ry * .2, 0], [L / (n - 1) * 1.8, max(ry, .004), max(rz, .0035)], col, k=.008, kc=.0015, bone="head", rot=[0, 0, round(a, 1)]))
    for i in range(20):
        f = .9 * i / 19; p = cl(f); ry = ryf(f); a = -(7 + 9 * f * f)
        out.append(ell("lower%d" % i, [p[0] + .002, p[1] - ry * 1.0, 0], [L * .9 / 19 * 1.8, max(ry * .5, .003), max(rzf(f) * .85, .003)],
                       "@billR" if f < .02 else "@lower", k=.004, kc=.0015, bone="head", rot=[0, 0, round(a, 1)]))
    # (C r9: the casque a distinct ROUNDED RIDGE riding the bill's basal half -- round in section, a little narrower than
    #  the bill, rising from the forehead, its front end swept up and rounded off; the bill's own curve smooth beneath)
    m = 16
    for i in range(m):
        f = .54 * i / (m - 1); p = cl(f); ry = ryf(f); a = -(7 + 9 * f * f); g = f / .54
        h = .024 * (1 - .15 * g) + .012 * max(0, (g - .7) / .3) ** 1.5      # (its height over the culmen; the front end up)
        h *= math.sqrt(max(.2, 1 - max(0, (g - .9) / .12) ** 2))             # (rounded off at the front)
        rz = rzf(f) * .78
        top = p[1] - ry * .2 + ry * .85 + h * .5
        col = "@casqueK" if i == 0 else "@casque"
        rot = [0, 0, round(a * .4 + 12 * max(0, g - .7), 1)]
        out.append(ell("casqueM%d" % i, [p[0] - .001, top, 0], [L * .54 / (m - 1) * 1.8, h * .55 + .002, rz], col, k=.007, kc=.002, bone="head", rot=rot))
    return out

hc = [.155, .345]
sh = [
    ell("chest", [.045, .3, 0], [.11, .062, .06], "@black", k=.03),
    ell("belly", [-.04, .284, 0], [.1, .05, .05], "@black", k=.03),
    ell("vent", [-.1, .284, 0], [.06, .038, .038], "@white", k=.02, kc=.01),
    ell("back", [-.02, .33, 0], [.12, .032, .05], "@back", k=.03),
    ell("rump", [-.11, .302, 0], [.055, .036, .038], "@back", k=.025),
    ell("neck", [.105, .33, 0], [.06, .042, .042], "@neck", k=.03, kc=.012, bone="head"),
    # (the cream of the neck spreading onto the shoulders -- the mantle at the wings' roots)
    ell("shoulder", [.06, .336, 0], [.06, .026, .062], "@neck", k=.025, kc=.01),
    # (the head black -- crown, face and chin; the cream only from the nape down)
    ell("skull", hc + [0], [.042, .04, .036], "@black", k=.02, bone="head"),
    ell("face", [hc[0] + .016, hc[1] - .006, .018], [.026, .022, .016], "@skin", k=.006, kc=.002, bone="head", mirror=True),
    ell("chin", [hc[0] + .012, hc[1] - .028, 0], [.03, .016, .022], "@skin", k=.006, kc=.003, bone="head"),
] + bill([hc[0] + .03, hc[1] + .008], .175) + wing(.318, .02, .05, .25, .56, .03, .155,
         # (the flight feathers white, black over their middles -- coatpat.js featherOf's bars, one band over 1/.51 of the
         #  length: the white bases a broad bar across the spread wing behind the coverts', the black, the white trailing edge)
         sec={"n": 12, "len": .2, "lens": [.19, .2, .21, .205, .195], "w": .062, "color": "@tipW", "tip": "@tipW", "bars": {"n": .51, "dark": .03}},
         prim={"n": 10, "a": (8, 30), "lens": [.21, .24, .265, .275, .27], "w": .06, "color": "@tipW", "tip": "@tipW", "curve": .015, "bars": {"n": .51, "dark": .03}},
         # (the coverts black, closed over the flight feathers' roots -- the pale bar across the wing is the flight
         #  feathers' own white bases beyond them, not a row of pale coverts)
         covs=[{"id": "lesser", "s": .34, "len": .07, "w": .05, "n": 6, "color": "@black", "tip": "@black"},
               {"id": "greater", "s": .2, "len": .085, "w": .054, "n": 6, "color": "@black", "tip": "@black"}],
         pcov={"n": 4, "len": .07, "w": .044, "color": "@black", "tip": "@black", "s": .25},
         ucov=[{"id": "ulesser", "s": .38, "len": .1, "w": .05, "n": 5, "color": "@lining", "tip": "@lining"}],
         kink=.02, hsweep=.05, htaper=.68,
         under=[{"s": .3, "w": .6, "color": "@lining"}],
         colors={"arm": "@black", "hand": "@black", "edge": "@black"}, th=.05)
tf = tail_fan([-.14, .3, 0], 9, .36, 9, .022, "@white", "@white", lens=[.33, .36, .37, .36, .33], camber=.07, curve=.01, seed=23)
# (the tail's band: the black across the white, in the feathers' own paint -- coatpat.js featherOf's bars, one period
#  over 1/.6 of the length, so its one dark band runs from 20% to 70% out: the white root under the coverts, the
#  broad black, the white end; no blades laid over it)
tf["bars"] = {"n": .6, "dark": .03}
sh.append(tf)

scale_parts(d["parts"], s)
sh = shift(sh, [0, 0, 0], s)
d["sculpt"] = {
    "_about": "x forward, y up, z left, metres; aloft (the wings' rest is the glide); authored at the macaw's size and scaled %.2f" % s,
    "mesh": {"tris": [2600, 900], "focus": {"head": 6}, "cell": .0045},
    "eyes": {"at": [round(v * s, 4) for v in [hc[0] + .02, hc[1] + .008, .03]], "from": [round(v * s, 4) for v in [hc[0], hc[1] + .006, 0]], "r": round(.0068 * s, 4),
             "iris": "@eye", "pupil": "round", "lid": "@skin", "sink": .55, "socket": 1.1},
    "shape": sh,
}
# (the perching agent's legs: perch/perchlegs.py's post-pass -- thighs, shins and gripping toes on their own bones)
import os as _os, sys as _sys
_PL = "/home/martin/store/apps/multiverse/tools/creaturegen/perch"
_sys.path.insert(0, _PL); from perchlegs import apply as _perch, SPEC as _SPEC
if "hornbill" in _SPEC: d = _perch(d, "hornbill")
else: d["parts"] = [p for p in d["parts"] if not (p["id"].startswith(("leg", "shin", "foot", "toe")))]
save("hornbill", d)
