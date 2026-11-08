#!/usr/bin/env python3
# gri.py OUT.json : the griffin -- the lion's body, rig and hindquarters (mammals/lion.json), an eagle's head, breast,
# forelegs and wings (birds/eagle.json, read only, scaled). Built at the lion's size, then 1.15x it (scaleBy).
import json, math, copy, sys
R0 = '/home/martin/store/apps/multiverse/assets/creatures/'
L = json.load(open(R0 + 'mammals/lion.json'))
E = json.load(open(R0 + 'birds/eagle.json'))
G = 1.15

def mk_tp(E0, W0, K, DI=0.0, SW=0.0):
    def tp(p):
        x, y, z = [(p[i] - E0[i]) * K for i in range(3)]
        c, s = math.cos(math.radians(DI)), math.sin(math.radians(DI))
        y, z = y * c + z * s, -y * s + z * c
        c, s = math.cos(math.radians(SW)), math.sin(math.radians(SW))
        x, z = x * c - z * s, x * s + z * c
        return [round(x + W0[0], 4), round(y + W0[1], 4), round(z + W0[2], 4)]
    return tp

# ---- the wing: the birds agent's flier.wing (scratchpad var/wlib: a copy, read only) -- the golden eagle's own wing call
# (birds/eagle.py) scaled F about its shoulder onto the lion's withers W0 (x: the root chord's middle), rising DIH per
# metre out (about 29 degrees), its covert tracts dense enough to close into one shingled surface (wlib/skywing.py)
sys.path.insert(0, '/home/martin/store/apps/multiverse/tools/creaturegen/var/wlib')
from skywing import big_wing
W0 = [0.17, 1.09, 0.13]
KW, DIH = 2.6, 0.55
wing, wr, half = big_wing(W0, KW, DIH, nk=1.0, bars={"n": 5, "dark": .82}, sec_n=12, prim_n=9, cov_n=(9, 10, 10, 6))   # (round 3: fewer coverts, ~a third fewer triangles)
wing = [q for q in wing if not q['id'].startswith('wUnder')]   # (the lining's bands: thinner than the grid at this size)
for q in wing:
    if q['id'] in ('wLesser', 'wMedian', 'wGreater', 'wPcov'): q.pop('bars', None)
wing.insert(0, {"id": "wRoot", "type": "ell", "bone": "wingL", "c": [W0[0] + .16, W0[1] - .03, W0[2] - .02], "r": [.2, .06, .09], "k": .06, "color": "@covert", "mirror": True})
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

# ---- the head: the eagle's, on the lion's head bone -- its skull where the lion's cranium was
HE0 = [0.30, 0.468, 0.0]
H0 = [0.905, 1.165, 0.0]
KH = 2.45
tph = mk_tp(HE0, H0, KH)
CH = {'@gold': '@nape', '@head': '@head', '@face': '@head', '@cere': '@cere', '@beak': '@beak'}
head = []
for s in E['sculpt']['shape']:
    if s.get('bone') == 'head':
        q = copy.deepcopy(s); q['id'] = 'e' + s['id']
        if 'c' in q: q['c'] = tph(q['c'])
        if 'r' in q: q['r'] = [round(v * KH, 4) for v in q['r']]
        if 'pts' in q: q['pts'] = [tph(p[:3]) + [round(p[3] * KH, 4)] for p in q['pts']]
        for k in ('k', 'kc'):
            if k in q: q[k] = round(q[k] * KH, 4)
        q['color'] = CH.get(q['color'], q['color'])
        head.append(q)
# (the hooked beak bigger than the eagle's own -- a griffin's: the upper mandible deeper, its hook further over)
for q in head:
    if q['id'] == 'eupper':
        q['pts'] = [[p[0], p[1], p[2], round(p[3] * 1.18, 4)] for p in q['pts']]
        t = q['pts'][-1]; q['pts'].append([round(t[0] - .018, 4), round(t[1] - .025, 4), 0, .003])
    if q['id'] == 'elower': q['pts'] = [[p[0], p[1], p[2], round(p[3] * 1.15, 4)] for p in q['pts']]
# the tip of the upper mandible dark, horn over the yellow
tip = [q for q in head if q['id'] == 'eupper'][0]['pts']
head.append({"id": "eBeakTip", "type": "ell", "bone": "head", "op": "paint", "c": tip[-2][:3], "r": [.035, .04, .03], "k": .02, "color": "@beakTip"})
# hackles: the nape's feathers drawn out into a ruff where the head meets the neck
for i, (dy, dz) in enumerate([(.0, .0), (-.05, .07), (-.05, -.07), (-.1, .1), (-.1, -.1), (-.15, .085), (-.15, -.085)]):
    head.append({"id": f"eHackle{i}", "type": "cone", "bone": "head", "a": [0.80, round(1.215 + dy, 3), dz], "b": [0.70, round(1.17 + dy * 1.1, 3), round(dz * 1.25, 3)],
                 "ra": .055, "rb": .012, "k": .04, "kc": .03, "color": "@nape"})
# ---- ROUND 2 (2026-11-07): the head an eagle's, not a ball -- the crown flatter, the heavy BROW RIDGE over each eye (the
# eagle's frown: a shelf of bone jutting out over the eye from the crown to the cere), small ear tufts behind the crown,
# and the hackles carried on down the neck as a ruff of long pointed feathers into the breast
for q in head:
    if q['id'] == 'eskull': q['r'] = [q['r'][0], round(q['r'][1] * .88, 4), q['r'][2]]
    if q['id'] == 'ecrown': q['c'] = [q['c'][0], round(q['c'][1] - .012, 4), 0]; q['r'] = [round(q['r'][0] * 1.1, 4), q['r'][1], round(q['r'][2] * 1.15, 4)]
    if q['id'] == 'eshelf': q.update({"c": [1.002, 1.2245, .079], "r": [.088, .022, .036], "rot": [0, -14, -9], "k": .012})
    if q['id'] == 'ebrow': q.update({"c": [0.982, 1.226, .066], "r": [.075, .03, .045], "k": .02})
head.append({"id": "eBrowTip", "type": "ell", "bone": "head", "c": [1.05, 1.2085, .066], "r": [.034, .016, .022], "rot": [0, -20, -14], "k": .01, "color": "@head", "mirror": True})
head.append({"id": "eTuft", "type": "cone", "bone": "head", "a": [0.84, 1.262, .062], "b": [0.765, 1.33, .088], "ra": .032, "rb": .006, "k": .014, "color": "@nape", "mirror": True})
RUFF = []
for i in range(6):
    t = i / 5
    for zs, dz in ((1, .02), (1, .07), (0, 0)):
        if zs == 0 and i < 2: continue
        x, y = .80 - .2 * t, 1.12 - .26 * t
        z = (.105 + .035 * t) if zs else 0
        ys = y - (.05 if zs == 0 else 0)
        RUFF.append({"id": f"nRuff{i}{'s' if zs else 'f'}{int(dz*100)}", "type": "cone", "bone": "neck",
                     "a": [round(x, 3), round(ys + (.03 if dz > .05 else 0), 3), round(z - (.03 if dz > .05 else 0), 3)],
                     "b": [round(x - .11, 3), round(ys - .07, 3), round((z - (.03 if dz > .05 else 0)) * 1.12 + dz * .3, 3)],
                     "ra": .05, "rb": .01, "k": .035, "kc": .03, "color": "@nape" if t < .45 else "@breast", **({"mirror": True} if zs else {})})
eyes = copy.deepcopy(E['sculpt']['eyes'])
eyes['at'] = tph(eyes['at']); eyes['from'] = tph(eyes['from']); eyes['r'] = round(eyes['r'] * KH, 4)
eyes['iris'] = '@eye'; eyes['lid'] = '@lid'

# ---- the forelegs: feathered to the wrist, then an eagle's yellow, scaled shank and four toes with black talons
Z = 0.1489
def toe(id, a, b, c, ra=.03):
    return {"id": id, "type": "tube", "bone": "footFL", "pts": [a + [ra], b + [ra * .82], c + [ra * .66]], "k": .012, "color": "@scale", "mirror": True}
def talon(id, t, d, r=.02):
    # from the toe's tip, on, curving down to a point on the ground
    return {"id": id, "type": "tube", "bone": "footFL", "pts": [t + [r], [round(t[0] + d * .03, 4), t[1] + .002, t[2]] + [r * .7],
            [round(t[0] + d * .055, 4), round(t[1] - .012, 4), t[2]] + [r * .4], [round(t[0] + d * .066, 4), 0.002, t[2]] + [.003]], "k": .003, "color": "@talon", "mirror": True}
B = [0.465, 0.04, Z]
fore = [
    {"id": "gTrouser", "type": "cone", "bone": "legFLl", "a": [0.39, 0.5, Z], "b": [0.405, 0.37, Z], "ra": .1, "rb": .07, "k": .03, "color": "@feather", "mirror": True},
    {"id": "gShank", "type": "tube", "bone": "footFL", "pts": [[0.418, 0.2, Z, .046], [0.44, 0.12, Z, .04], [0.462, 0.05, Z, .038]], "k": .02, "color": "@scale", "mirror": True},
    {"id": "gBall", "type": "ell", "bone": "footFL", "c": B, "r": [.05, .032, .046], "k": .015, "color": "@scale", "mirror": True},
    toe("gToeM", B, [0.54, 0.034, Z], [0.6, 0.028, Z]),
    toe("gToeI", B, [0.53, 0.034, Z - .045], [0.58, 0.028, Z - .075], .028),
    toe("gToeO", B, [0.53, 0.034, Z + .045], [0.575, 0.028, Z + .07], .028),
    toe("gToeH", B, [0.42, 0.034, Z - .01], [0.385, 0.03, Z - .018], .026),
    talon("gTalM", [0.6, 0.028, Z], 1), talon("gTalI", [0.58, 0.028, Z - .075], 1), talon("gTalO", [0.575, 0.028, Z + .07], 1),
    talon("gTalH", [0.385, 0.03, Z - .018], -1, .018),
]
# the scutes: darker bands across the shank
for i, y in enumerate([0.07, 0.1, 0.13, 0.16]):
    fore.append({"id": f"gScute{i}", "type": "ell", "bone": "footFL", "op": "paint", "c": [round(0.418 + (0.2 - y) * .55, 4), y, Z], "r": [.06, .006, .06], "k": .004, "color": "@scaleD", "mirror": True})
for i, y in enumerate([0.21, 0.25, 0.29, 0.33]):
    fore.append({"id": f"gScuteU{i}", "type": "ell", "bone": "legFLl", "op": "paint", "c": [round(0.43 - (y - .165) * .117, 4), y, Z], "r": [.075, .006, .075], "k": .004, "color": "@scaleD", "mirror": True})

# ---- the lion's shapes kept: the body, the hind legs, the forearm (feathered now); the head, the mane, the paws gone
DROP_BONES = {'head', 'earL'}
# (the front's plumage: the birds' row scales -- each feather's rounded tip showing, tips toward the tail -- in a frame
#  laid along the trunk, a feather about 3.5 cm; the head's smaller)
FRB = {"o": [0.3, 0.95, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.7}
FRH = {"o": [0.9, 1.17, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.42}
FEATHERED = {'chest', 'keel', 'withers', 'scapula', 'arm', 'triceps', 'forearm', 'flexor', 'neck', 'throat'}
body = []
for s in L['sculpt']['shape']:
    b, id = s.get('bone', '-'), s['id']
    if b in DROP_BONES or b == 'footFL': continue
    if id.startswith(('mane', 'lock', 'tuft')): continue
    q = copy.deepcopy(s)
    if id in FEATHERED:
        q['color'] = '@breast' if id in ('keel', 'throat') else '@feather'
        q['kc'] = .16 if id in ('chest', 'keel', 'withers') else q.get('kc', q['k'])   # (a wide crossfade: the feathers going over into the fur at the waist)
    if id == 'neck': q['r'] = [q['r'][0], "0.165*neckG", "0.12*neckG"]
    if id in FEATHERED and id not in ('forearm',): q['pat'] = 'rowscales'; q['frame'] = FRB
    elif b not in ('footHL',) and not id.startswith(('tail1Seg9', 'tailTuft', 'tuft')) and q.get('op') != 'paint' and q.get('color') not in ('@nose', '@noseRim', '@black'): q['pat'] = 'agouti'
    # (the forearm is the eagle's shank: scaled and yellow, slimmer, down from a fringe of feathers at the elbow)
    if id == 'forearm': q.update({"color": "@scale", "ra": .062, "rb": .046, "k": .03})
    if id == 'flexor': q.update({"color": "@feather", "c": [0.395, 0.455, Z], "r": [.1, .085, .09]})
    body.append(q)

out = {
    "name": "griffin",
    "_about": ("The GRIFFIN (2026-11-07): an eagle in front, a lion behind -- the lion's body, rig, gait, hindquarters and "
               "tufted tail (mammals/lion.json), and the golden eagle's head with a bigger hooked beak, its breast and neck "
               "feathered (the lion's chest, withers and forelegs painted in its plumage, crossfading into the fur over the "
               "waist), an eagle's forelegs -- feathered to the wrist, then the yellow scaled shank and four toes with black "
               "talons -- and its wings (birds/eagle.json: arm, hand and feather rows) scaled " + str(KW) + "x onto the withers, a span of "
               "about " + str(round(2 * (half + W0[2]) * G, 1)) + " m. ROUND 2: the eagle's brow ridge over each eye, ear tufts, a ruff of hackles down the neck into the breast; the front's plumage in the birds' row scales, the lion's coat ticked (agouti) behind, crossfading over the waist; the head carried lower. Built at the lion's size and then " + str(G) + "x it (`scaleBy`). The wings are drawn SPREAD; on "
               "the ground they are folded along the flanks (skeleton.js PERCH; skysteeds.js SKYSTEEDS.griffin), and it flies "
               "as the pegasus does (skysteeds.js). Its coats: golden (a tawny lion, a golden-brown eagle), white-headed "
               "(a bald eagle's white head and dark brown plumage) and dark."),
    "use": L.get("use"),
}
for k in ('rear', 'front', 'neck', 'head', 'muzzle', 'nose', 'ears', 'eyes', 'legs', 'tail'):
    if k in L: out[k] = copy.deepcopy(L[k])
out.pop('use', None) if out.get('use') is None else None
out["params"] = {**L["params"], "mane": False, "jowls": False}
colors = {**L["colors"],
          "body": "#c49a52", "leg": "#bd934c", "paw": "#c39b58", "tail": "#bd934c", "cream": "#e3cfa2",
          "feather": "#8a5a2c", "breast": "#a06c36", "nape": "#c8963e", "head": "#7a4e26",
          "beak": "#e8b830", "beakTip": "#4a3a26", "cere": "#e8b830", "eye": "#c8901c", "lid": "#2a1c12",
          "scale": "#e2b032", "scaleD": "#b8862a", "talon": "#16120e",
          "wing": "#5a3e24", "wingTip": "#24180e", "covert": "#7a5230", "wingIn": "#4a3420", "tuft": "#3a2614"}
out["colors"] = colors
out["scaleBy"] = G
out["monster"] = True
out["rest"] = 0
out["call"] = "eagle"
out["print"] = "paw"
out["extras"] = bones('L') + bones('R')
out["coats"] = [
    {"name": "golden", "scale": G},
    {"name": "white-headed", "scale": G, "head": "#f0ece2", "nape": "#f4f0e6", "feather": "#3f2b1b", "breast": "#4a3220",
     "wing": "#3a2818", "wingTip": "#1a120c", "covert": "#4a3422", "wingIn": "#30221a", "eye": "#e8c84a",
     "beak": "#f0c030", "beakTip": "#f0c030"},
    {"name": "dark", "scale": G, "body": "#6a5440", "leg": "#5e4a38", "paw": "#5e4a38", "tail": "#5e4a38", "cream": "#9a8468",
     "feather": "#2c2018", "breast": "#3a2a1e", "nape": "#7a5a34", "head": "#2a1e16", "wing": "#241a12", "wingTip": "#120c08",
     "covert": "#30241a", "wingIn": "#1e1610", "tuft": "#140e0a"},
]
out["_coats"] = ("COATS (species.js coatDef): golden (its own), white-headed, dark -- each at " + str(G) + "x (`scale`: a coat "
                 "is dressed afresh, so it says its size again). The keys: `feather` the front half's plumage, `breast` the "
                 "keel and throat, `nape` the hackles and the back of the head, `head` the face, `beak`, `beakTip`, `cere`, "
                 "`scale` and `scaleD` the shank and its scutes, `talon`; `wing`, `wingTip`, `covert`, `wingIn` the wings; "
                 "the rest the lion's")
sc = copy.deepcopy(L['sculpt'])
sc['_about'] = "the lion's body and hindquarters (mammals/lion.json, 2026-11-07) with the eagle's head, forefeet and wings: gri.py"
for q in head:
    if q['id'] in ('enape', 'ecrown', 'eskull') or q['id'].startswith(('eHackle', 'eTuft')): q['pat'] = 'rowscales'; q['frame'] = FRH
for q in RUFF: q['pat'] = 'rowscales'; q['frame'] = FRB
# (level: the eagle's head and neck carried a little lower, so the front no longer stands above the lion's back)
HDY = -0.04
def dy(v, d): return [v[0], round(v[1] + d, 4), v[2]] + v[3:]
for q in head:
    for k in ('c', 'a', 'b'):
        if k in q: q[k] = dy(q[k], HDY)
    if 'pts' in q: q['pts'] = [dy(p, HDY) for p in q['pts']]
eyes['at'] = dy(eyes['at'], HDY); eyes['from'] = dy(eyes['from'], HDY)
for q in RUFF + [x for x in body if x['id'] in ('neck', 'throat')]:
    for k in ('c', 'a', 'b'):
        if k in q and isinstance(q[k][1], (int, float)): q[k] = dy(q[k], HDY * .6)
sc['shape'] = body + head + RUFF + fore + wing
sc['eyes'] = eyes
out["sculpt"] = sc
json.dump(out, open(sys.argv[1], 'w'), indent=1)
print('shapes', len(sc['shape']), 'head', len(head), 'wing', len(wing), 'wrist', wr, 'eye', eyes['at'])
