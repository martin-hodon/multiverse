#!/usr/bin/env python3
# wlf.py IN.json OUT.json : ROUND 2 of the wolf (2026-11-07) -- a canid's WEDGE skull in place of the long round tube: a
# broad cranium and wide cheekbones narrowing to a slim muzzle, the forehead rising in a clear STOP before the eyes, the
# muzzle's top straight and lower; upright triangular ears (a four-sided pyramid each, the pinna opening forward); a ruff
# of pale fur flaring off each cheek; the legs with joints -- a slim forearm to a narrow wrist with the carpal pad's
# bump behind it, a sloped pastern, four toe lobes; the gaskin tapering to a hock with its point (the calcaneus) behind
# -- and the legs tawny with the dark line down the front of the foreleg, not cream columns
import json, copy, sys
T = json.load(open(sys.argv[1]))
DROP = {'cranium', 'cheek', 'ruffC', 'bridge', 'muzzle', 'lip', 'jaw', 'nose', 'ear0', 'ear1', 'ear2', 'earIn0', 'earIn1', 'earIn2',
        'forearm', 'pastern', 'paw', 'gaskin', 'hock', 'hpaw'}
def E(id, c, r, color, k, bone='head', **kw): return {"id": id, "type": "ell", "bone": bone, "c": c, "r": r, "k": k, "color": color, **kw}
def C(id, a, b, ra, rb, color, k, bone='head', **kw): return {"id": id, "type": "cone", "bone": bone, "a": a, "b": b, "ra": ra, "rb": rb, "k": k, "color": color, **kw}
def TR(id, a, b, c, color, r=.008, bone='earL', **kw): return {"id": id, "type": "tri", "bone": bone, "a": a, "b": b, "c": c, "r": r, "k": .006, "kc": .002, "color": color, "mirror": True, **kw}
head = [
    E("cranium", [0.632, 0.846, 0], [0.088, 0.07, 0.082], "@head", .03),
    E("forehead", [0.69, 0.884, 0], [0.056, 0.034, 0.056], "@head", .022),
    E("zygo", [0.672, 0.818, 0.054], [0.058, 0.04, 0.04], "@mask", .024, mirror=True),
    C("bridge", [0.742, 0.862, 0], [0.838, 0.817, 0], .024, .017, "@head", .014),
    E("muzzle", [0.785, 0.806, 0], [0.066, 0.033, 0.029], "@muzzleC", .016),
    C("snoutU", [0.73, 0.79, 0], [0.832, 0.79, 0], .036, .022, "@muzzleC", .016),
    E("lip", [0.784, 0.774, 0.021], [0.056, 0.016, 0.013], "@lip", .011, kc=.006, mirror=True),
    C("jaw", [0.665, 0.772, 0], [0.812, 0.76, 0], .03, .015, "@lip", .016),
    E("nose", [0.8465, 0.794, 0], [0.016, 0.016, 0.02], "@nose", .006, kc=.002, wet=.55),
    # the ruff: pale fur flaring off each cheek, out and back and down, over the throat's sides
    E("ruffC", [0.605, 0.79, 0.07], [0.05, 0.082, 0.042], "@mask", .035, kc=.03, rot=[-14, 0, 14], mirror=True, pat="shag"),
    C("ruffP0", [0.63, 0.8, 0.075], [0.56, 0.752, 0.122], .04, .01, "@mask", .026, kc=.02, mirror=True, pat="shag"),
    C("ruffP1", [0.63, 0.765, 0.06], [0.565, 0.71, 0.1], .036, .009, "@mask", .024, kc=.02, mirror=True, pat="shag"),
    # the ears: erect, broad-based, pointed, the pinna open to the front
]
fi, fo, bi, bo, tip = [0.664, 0.892, 0.04], [0.652, 0.866, 0.093], [0.604, 0.888, 0.046], [0.6, 0.866, 0.088], [0.63, 0.97, 0.08]   # (tip lowered: the ears were jackal-tall)
ears = [
    TR("earF", fi, fo, tip, "@earIn"), TR("earB", bi, bo, tip, "@ear"), TR("earSi", fi, bi, tip, "@ear"), TR("earSo", fo, bo, tip, "@ear"),
    TR("earRim", [0.661, 0.895, 0.043], [0.649, 0.87, 0.09], [0.63, 0.966, 0.08], "@ear", r=.002),
]
Z, ZH = 0.084, 0.056
legs = [
    C("forearm", [0.272, 0.25, Z], [0.296, 0.118, Z], .042, .022, "@leg", .024, bone='legFLl', kc=.04, mirror=True),
    E("carpal", [0.29, 0.108, Z], [0.022, 0.026, 0.022], "@leg", .01, bone='footFL', mirror=True),
    E("carpalPad", [0.276, 0.104, Z], [0.012, 0.016, 0.012], "@foot", .006, bone='footFL', mirror=True),
    C("pastern", [0.298, 0.1, Z], [0.33, 0.04, Z], .021, .024, "@foot", .012, bone='footFL', mirror=True),
    E("paw", [0.338, 0.024, Z], [0.04, 0.02, 0.03], "@foot", .012, bone='footFL', mirror=True),
    C("foreLine", [0.284, 0.24, Z + .036], [0.306, 0.12, Z + .02], .012, .008, "@saddle", 0, bone='legFLl', op="paint", kc=.012, mirror=True),
    C("gaskin", [-0.215, 0.345, ZH], [-0.278, 0.24, ZH], .05, .024, "@leg", .024, bone='legHLu', kc=.04, mirror=True),
    E("calc", [-0.296, 0.232, ZH], [0.02, 0.026, 0.018], "@leg", .009, bone='legHLl', mirror=True),
    C("hock", [-0.283, 0.228, ZH], [-0.21, 0.05, ZH], .024, .019, "@foot", .014, bone='legHLl', mirror=True),
    E("hpaw", [-0.183, 0.022, ZH], [0.037, 0.019, 0.028], "@foot", .011, bone='footHL', mirror=True),
]
for nm, (cx, z0, bone, s) in {"toe": (0.338, Z, 'footFL', 1.0), "htoe": (-0.183, ZH, 'footHL', .9)}.items():
    for i, (dx, dz) in enumerate([(.026, -.024), (.034, -.008), (.034, .008), (.026, .024)]):
        legs.append(E(f"{nm}{i}", [round(cx + dx * s, 4), 0.017, round(z0 + dz * s, 4)], [round(.016 * s, 4), round(.017 * s, 4), round(.012 * s, 4)], "@foot", .005, bone=bone, mirror=True))
sh = [s for s in T['sculpt']['shape'] if s['id'] not in DROP]
T['sculpt']['shape'] = sh + head + ears + legs
T['sculpt']['mesh'] = {"tris": [8000, 2400], "cell": 0.009}
T['c'] = {**T['c'], "leg": "#857a68", "foot": "#8f8370"}   # (the rig's low-body lift brightens these a quarter)
T['sculpt']['eyes']['from'] = [0.6462, 0.8228, -0.01]   # (the gaze up and out a little: the iris sat low in the lid)
for c in T['coats']:   # (the legs a little darker than the belly in every coat: tawny-buff, the feet paler)
    if c.get('name') == 'red': c.update({"leg": "#a87c56", "foot": "#b48e68"})
    if c.get('name') == 'arctic': c.update({"leg": "#e2ddd2", "foot": "#ece8de"})
# (round 1, re-applied here 2026-11-07: an earlier restore of wolf.json had dropped them) ticked fur -- coatpat.js agouti
# -- on every furred shape, and the inner ear's darker tone
FUR = {'@body', '@saddle', '@head', '@tail', '@leg', '@belly', '@chestc', '@throat', '@mask', '@muzzleC', '@ear', '@tip', '@foot'}
for q in T['sculpt']['shape']:
    if q.get('color') in FUR and 'pat' not in q and q.get('op') != 'sub' and q.get('type') != 'feathers': q['pat'] = 'agouti'
T['c']['earIn'] = "#a69c8c"
T['_about'] += (" || ROUND 2 (2026-11-07, scratchpad var/wlf.py): a canid's wedge skull (broad cranium and cheekbones to a slim "
                "muzzle) with a clear stop below the forehead; upright triangular ears; a pale cheek ruff; the legs jointed -- a "
                "narrow wrist with the carpal pad's bump, sloped pasterns, toe lobes, the hock's point behind -- and tawny, with "
                "the dark line down the front of the foreleg")
json.dump(T, open(sys.argv[2], 'w'), indent=1)
print('shapes', len(T['sculpt']['shape']))
