#!/usr/bin/env python3
# peg.py OUT.json : the pegasus -- the horse (mammals/horse.json) with the golden eagle's wing (birds/eagle.json,
# read only) scaled up and rooted at the withers. The wing is authored SPREAD (its glide); skeleton.js PERCH folds it
# along the flank on the ground (an.perch, an.perchFold: skysteeds.js).
import json, math, copy, sys
R0 = '/home/martin/store/apps/multiverse/assets/creatures/'
H = json.load(open(R0 + 'mammals/horse.json'))
E = json.load(open(R0 + 'birds/eagle.json'))

# ---- the wing: the birds agent's flier.wing (scratchpad var/wlib: a copy, read only) -- the golden eagle's own wing call
# (birds/eagle.py) scaled F about its shoulder and set on the withers W0 (x: the root chord's middle), rising DIH per metre
# out (about 33 degrees); its covert tracts denser so they close into one shingled surface (wlib/skywing.py)
sys.path.insert(0, '/home/martin/store/apps/multiverse/tools/creaturegen/var/wlib')
from skywing import big_wing
W0 = [0.05, 1.56, 0.2]
F, DIH = 2.9, 0.65
# (round 3: an eagle's outline, not a glider's strip -- 2.9 m of arm and hand, the tip about 3.4 m out: the inner
#  secondaries short, rounding into the trailing edge; the hand narrowing (htaper .5) and swept back, its eight
#  primaries broader (they overlap at the root), lengthening to the tip and fanned 10-44 degrees so the outer ones part
#  into fingers; fewer coverts (they shingle
#  still: about 34k triangles in all, from 48k))
WING = dict(sec_lens=(.22, .28, .31, .3, .29), sec_n=12, prim_lens=(.31, .4, .48, .54, .53), prim_a=(10, 44), prim_n=8,
            prim_w=.06, cov_n=(8, 9, 10, 6), htaper=.5, hsweep=.13, tips=("@wingTip", "@primTip"),
            quills=.017)   # (round 4: the quill-base tubes thick enough for the field at this mesh cell, 0.8 x 2 cm)
wing, wr, half = big_wing(W0, F, DIH, nk=1.0, **WING)
for q in wing:   # (flatter flight feathers: the eagle's camber, this size, put a bright ridge down every shaft)
    if q['id'] in ('wSec', 'wPrim'): q['camber'] = .04
wing = [q for q in wing if not q['id'].startswith('wUnder')]   # (the lining's bands: thinner than the grid at this size)
wing.insert(0, {"id": "wRoot", "type": "ell", "bone": "wingL", "c": [W0[0] + .25, W0[1] - .04, W0[2] - .03], "r": [.3, .08, .12],
                "k": .07, "color": "@covert", "mirror": True})
K, DI = F, round(math.degrees(math.atan(DIH)))
TIP = max(r['to'][2] for q in wing if q['id'] == 'wPrim' for r in q['rows'])
# ---- the rig's wing bones (the eagle's chain: arm, wrist, hand), at the withers
def bones(S):
    sg = 1 if S == 'L' else -1
    z = lambda v: [v[0], v[1], v[2] * sg]
    return [
        {"raw": {"id": "wing" + S, "parent": "body", "shape": "sphere", "size": {"r": .02}, "bone": True, "color": "#ffffff",
                 "anim": {"axis": "x", "deg": 32 * sg, "speed": .4, "phase": 0, "wing": True, "amp": True}}, "at": z(W0)},
        {"raw": {"id": "wrist" + S, "parent": "wing" + S, "shape": "sphere", "size": {"r": .02}, "bone": True, "color": "#ffffff",
                 "pos": z([round(wr[i] - W0[i], 4) for i in range(3)]),
                 "anim": {"axis": "y", "deg": -28 * sg, "speed": .4, "phase": -1.891, "flick": 1, "wing": True, "amp": True}}},
        {"raw": {"id": "hand" + S, "parent": "wrist" + S, "shape": "sphere", "size": {"r": .02}, "bone": True, "color": "#ffffff",
                 "pos": [0, 0, 0], "anim": {"axis": "x", "deg": 16 * sg, "speed": .4, "phase": -.8, "wing": True, "amp": True}}},
    ]

P = copy.deepcopy(H)
out = {
    "name": "pegasus",
    "_about": ("The PEGASUS (2026-11-07): the horse (mammals/horse.json: its frame, rig, shapes and coats) with a pair of great "
               "feathered wings rooted at the withers -- built with the birds' own wing builder (flier.wing, as the eagle's: a "
               "covert-shingled arm, secondaries along the trailing edge, fingered primaries); its tip about " + str(round(TIP, 1)) + " m out from the spine, a span of about " + str(round(2 * TIP, 1)) + " m, raised " + str(int(DI)) + " degrees. The wing is drawn SPREAD, as it glides; "
               "on the ground it is folded along the flank (skeleton.js PERCH: an.perch 1, its fit an.perchFold -- skysteeds.js "
               "SKYSTEEDS.pegasus), and the game takes it up: a gallop, a climb on hard beats, wide circles gliding with bursts of "
               "beats, and down again to a meadow (skysteeds.js). White, as the myth has it; the coats a dapple grey, a black and a "
               "palomino, each with wings to match (`wing`, `wingTip`, `primTip`, `covert`, `wingIn`): the feathers a cooler, silvered "
               "grey-white against the warm grey-white hair, greying toward the tips, the primaries' tips darkest."),
    "use": H["use"],
    "params": {**H["params"], "mane": False},
    "colors": None,
    "monster": True,
    "rest": 0,
    "graze": H.get("graze", 1.25),
    "call": "horse",
    "print": "hoof",
    "extras": bones('L') + bones('R'),
    "coats": None,
    "_coats": ("COATS (species.js coatDef): white (its own), dapple grey, black, palomino -- the horse's own colour tables "
               "(mammals/horse.json), white's the unicorn's, each with its wings: `wing` the flight feathers, `wingTip` the "
               "secondaries' tips, `primTip` the primaries', `covert` the coverts over them and the arm, `wingIn` the under coverts"),
    "sculpt": None,
}
# (a grey horse gone white: the coat a warm off-white with the grey of the skin under it at the muzzle, round the eyes,
#  on the lower legs and the hooves; the feathers a cooler, brighter white than the hair, the flight feathers' tips grey,
#  the primaries' darker; round 3: the whites toned down so the feathers' pale shafts no longer blow out to white lines)
white = {"body": "#e4ded2", "back": "#d9d2c4", "flank": "#e8e3d8", "muzzle": "#9a928c", "ear": "#d4cdc0", "earIn": "#9a8c8c",
         "leg": "#d6cfc2", "sock": "#b8b2a8", "foot": "#54504c", "tail": "#ece8e0", "mane": "#f0ece4", "eye": "#2a1a10",
         "nose": "#5a5254", "blaze": "#e8e3d8",
         "wing": "#d6dade", "wingTip": "#bcc1c8", "primTip": "#969ca6", "covert": "#d8dbe0", "wingIn": "#c8ccd2"}
out["colors"] = {**H["colors"], **white}
hc = {c["name"]: c for c in H["coats"]}
dg = {**hc["dapple grey"], "wing": "#d4d2cc", "wingTip": "#a4a29c", "primTip": "#7a7874", "covert": "#c4c2bc", "wingIn": "#b6b4ae"}
bl = {**hc["black"], "foot": "#1e1a18", "wing": "#2a2624", "wingTip": "#141212", "primTip": "#0e0c0c", "covert": "#26221f", "wingIn": "#1e1b19", "nose": "#2a2420", "earIn": "#2a2420"}
pa = {**hc["palomino"], "wing": "#e2d8bc", "wingTip": "#d4bc88", "primTip": "#b89a64", "covert": "#e2c48a", "wingIn": "#d8b878", "foot": "#4a3a2c"}
out["coats"] = [{"name": "white"}, dg, bl, pa]
sc = copy.deepcopy(H["sculpt"])
sc["_about"] = "the horse's shapes (mammals/horse.json, at 2026-11-07) and a flier.wing (wlib/skywing.py) on the withers: peg.py"
# (round 4: the horse's forelock reached up between the ears and the field drew a thin web from its top to the ear --
#  a sliver from the poll that the ear's swivel stretched out; the forelock shorter and a little lower, clear of them)
for q in sc["shape"]:
    if q["id"] == "forelock": q["r"] = [0.078, 0.042, 0.046]; q["c"] = [1.536, 2.07, 0.0]
sc["shape"] = sc["shape"] + wing
sc["mesh"] = {**sc.get("mesh", {}), "tris": [8500, 2800], "cell": .02}
# (the horse's countershading darkens the back to .6 of the coat: the wing's arm, above it, went grey -- on a white coat
#  next to white feathers. Here the back keeps the coat's own tone, the belly a little paler)
sc["shade"] = {**sc["shade"], "back": 0.9, "belly": 1.06}
out["sculpt"] = sc
json.dump(out, open(sys.argv[1], 'w'), indent=1)
print('shapes', len(sc['shape']), 'wing', len(wing), 'wrist', wr)
