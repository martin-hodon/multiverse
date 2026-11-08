#!/usr/bin/env python3
# tgr.py IN.json OUT.json : ROUND 2 of the tiger (2026-11-07) -- the lion's cat face (mammals/lion.json: the L3/L4 shapes,
# the cheek pods, the eyes) moved onto the tiger's head (tX, tY: metres, the lion's face to the tiger's eye) and painted a
# tiger's (orange striped crown and brow, white cheeks striped, white pads, chin and eye spots, black-backed ears with
# a white spot), white cheek ruffs flaring out behind the jaw; every striped head shape laid in the body's frame (no
# seam where the head's stripes met the neck's); the lion's toe lobes and carpal pad on the tiger's paws
import json, copy, sys
R0 = '/home/martin/store/apps/multiverse/assets/creatures/'
T = json.load(open(sys.argv[1]))
L = json.load(open(R0 + 'mammals/lion.json'))
DROP = {'skull', 'cheek', 'ruff', 'bridge', 'muzzle', 'pad', 'chin', 'jowl', 'nose', 'ear', 'earIn', 'forehead', 'eyeSpot', 'earSpot',
        'browR', 'eyeIn', 'eyeOut', 'tear0', 'tear1', 'tear2', 'lipL0', 'lipL1', 'lipL2', 'paw', 'hpaw'}
def tx(v):
    if isinstance(v, str): return v.replace("0.874+((", "0.874+tX+((").replace("1.126+((", "1.126+tY+((")
    if isinstance(v, list): return [tx(x) for x in v]
    return v
COL = {'@head': '@body', '@bridge': '@body', '@cream': '@white', '@pale': '@white', '@earBack': '@black', '@earIn': '@white',
       '@lidLine': '@black', '@paw': '@pale'}
STRIPED = {'L3cran'}   # (round 3: the body's broad stripes stay on the crown and nape only; the face has its own fine marks, MARKS below)
P = lambda x, y, z: ["0.874+tX+((%s)-0.874)*hs" % x, "1.126+tY+((%s)-1.126)*hs" % y, "(%s)*hs" % z]
# ROUND 4: the head bigger (hs 1.2) and broader, the skull rounder; the muzzle SHORT (faceX -0.025 draws the lion's
# muzzle shapes back) and broad (mw 1.4), a squarer chin and big whisker pads; the lion's jowl ball (`cheek`, a sphere
# out to 0.23 m each side once the mane was gone) flattened to the cheek's breadth -- the ruff is a fringe (ruffU/P/L)
HEAD4 = {
    'L3cran': {'r': ['(0.13)*hs', '(0.104)*hs', '(0.118)*hs']},
    'L3brow': {'r': ['(0.066)*hs', '(0.06)*hs', '(0.09)*hs']},
    'cheek': {'c': P('0.89', '1.07', '0.072'), 'r': ['(0.11)*hs', '(0.088)*hs', '(0.08)*hs']},
    # (round 5) the white pads pulled back ~12% (centre 1 cm back, 4 mm less deep): the nose sits proud of them
    'L3pad': {'c': P('1.112+faceX', '1.064', '0.04*(1+faceX*5)*mw'), 'r': ['(0.038)*hs', '(0.046)*hs', '(0.038*mw)*hs']},
    'L3lipW': {'c': P('1.12+faceX', '1.036', '0.03*(1+faceX*5)')},
    'L3chin': {'c': P('1.085+faceX', '0.996', '0'), 'r': ['(0.046)*hs', '(0.034)*hs', '(0.046*mw)*hs'], 'k': 0.016},
}
face = []
for s in L['sculpt']['shape']:
    id = s['id']
    if not (id.startswith(('L3', 'L4')) or id in ('cheek', 'jowl')) or id in ('L3heel',): continue
    q = copy.deepcopy(s)
    for k in ('c', 'a', 'b', 'pts', 'r', 'ra', 'rb'):
        if k in q: q[k] = tx(q[k])
    if id == 'L3carpal': q['c'] = [0.465, 0.16, 0.165]
    q['color'] = COL.get(q['color'], q['color']) if isinstance(q['color'], str) else [COL.get(c, c) for c in q['color']]
    if id == 'L3cheek': q['color'] = '@white'   # (the white under the eye; the cheek behind it stays orange and striped)
    if id == 'L3pad': q['color'] = '@white'
    if id in STRIPED: q['pat'] = 'stripes'; q['frame'] = 'body'
    elif q.get('pat') == 'stripes': q.pop('pat'); q.pop('frame', None)
    if id == 'L3ear': q['r'] = ['(0.016)*hs', '(0.036*earS)*hs', '(0.036*earS)*hs']; q['k'] = 0.014; q['color'] = '@body'   # (a flat round shell, orange: its back painted black)
    if id == 'L3nose': q['wet'] = 0.25
    if id in HEAD4: q.update(HEAD4[id])
    face.append(q)
# the toes: the lion's four lobes on each paw, moved to the tiger's paws (the lion's paw middles 0.49 / -0.478 to 0.55 / -0.6)
for s in L['sculpt']['shape']:
    if s['id'].startswith(('toe', 'htoe')):
        q = copy.deepcopy(s)
        fr = s['id'].startswith('toe')
        q['c'] = [q['c'][0].replace('0.49+', '0.55+') if fr else q['c'][0].replace('-0.478+', '-0.6+'),
                  q['c'][1], q['c'][2].replace('0.1489+', '0.165+') if fr else q['c'][2].replace('0.1155+', '0.128+')]
        q['color'] = '@leg'; q['k'] = 0.006   # (round 4: the coat's colour, the lion's own lobes and blend: four round toe bumps)
        face.append(q)
extra = [
    # the paw's sole between the lobes (the old paw ell, lower and smaller: the lobes carry the paw's outline now)
    # (round 4) the paws: the lion's -- a big round pad of a paw under the toes' four lobes, the coat's colour on top
    {"id": "pawBase", "type": "ell", "bone": "footFL", "c": [0.565, "0.05*pawS", 0.165], "r": ["0.086*pawS", "0.05*pawS", "0.078*pawS"], "k": 0.02, "color": "@leg", "mirror": True},
    {"id": "hpawBase", "type": "ell", "bone": "footHL", "c": [-0.59, "0.046*pawS", 0.128], "r": ["0.076*pawS", "0.045*pawS", "0.058*pawS"], "k": 0.018, "color": "@leg", "mirror": True},
    # the white cheek ruffs: long fur flaring out and back below the ears, behind the jaw, striped
    # (round 4) the cheek RUFF: a flat fringe, not a ball -- three flattened locks sweeping back and down from the cheek to
    # below the ear, standing just out of the face's outline: the upper orange, the lower two white
    # (round 5) the locks THICK, their tips round (a round cone's end cap, ~2.5 cm across, not a 1 cm sliver the cell
    #  flattened into a card) and nearer the cheek, blended in wide (k .045): a soft flare, no hard edge or step under the jaw
    {"id": "ruffU", "type": "cone", "bone": "head", "a": P("0.9", "1.08", "0.118"), "b": P("0.815", "1.035", "0.15"), "ra": "(0.036)*hs", "rb": "(0.022)*hs", "k": 0.045, "color": "@body", "mirror": True},
    {"id": "ruffP", "type": "cone", "bone": "head", "a": P("0.895", "1.045", "0.116"), "b": P("0.805", "0.99", "0.146"), "ra": "(0.035)*hs", "rb": "(0.021)*hs", "k": 0.045, "color": "@white", "mirror": True},
    {"id": "ruffL", "type": "cone", "bone": "head", "a": P("0.9", "1.012", "0.104"), "b": P("0.825", "0.965", "0.13"), "ra": "(0.03)*hs", "rb": "(0.018)*hs", "k": 0.045, "color": "@white", "mirror": True},
    # the white spot over each eye, and on the back of each ear
    {"id": "eyeSpot", "bone": "head", "op": "paint", "type": "ell", "c": P("1.022+eyeX*0.5", "1.222+eyeY", "0.07+eyeZ"), "r": ["(0.026)*hs", "(0.014)*hs", "(0.022)*hs"], "kc": 0.006, "color": "@white", "mirror": True},
    # the ear's back black (its rim left orange), under the white spot
    {"id": "earBack", "bone": "earL", "op": "paint", "type": "ell", "c": P("0.848+earX", "1.226+earY+0.002*earS", "0.124+earZ"), "r": ["(0.012)*hs", "(0.03*earS)*hs", "(0.03*earS)*hs"], "rot": [-38, -24, 0], "kc": 0.004, "color": "@black", "mirror": True},
    {"id": "earSpot", "bone": "earL", "op": "paint", "type": "ell", "c": P("0.846+earX", "1.226+earY+0.004*earS", "0.132+earZ"), "r": ["(0.012)*hs", "(0.016*earS)*hs", "(0.016*earS)*hs"], "rot": [-38, -24, 0], "kc": 0.004, "color": "@white", "mirror": True},
]
# MARKS (round 3): a tiger's face is finely marked, not banded -- three thin stripes slanting down and forward over each
# cheek, the forehead's short bars stepping back over each eye, and the line down the middle of the forehead
def mark(id, c, r, rot, mirror=True, kc=0.003):
    return {"id": id, "bone": "head", "op": "paint", "type": "ell", "c": P(*[str(v) for v in c]), "r": ["(%s)*hs" % v for v in r],
            "rot": rot, "kc": kc, "color": "@black", **({"mirror": True} if mirror else {})}
extra += [
    # (round 5) two longer, slightly broader strokes along the ruff, softer-edged (kc .011), not three thin ones the cell sawed into teeth
    mark("cheekS0", (0.895, 1.092, 0.15), (0.088, 0.016, 0.06), [0, 0, 24], kc=0.011),
    mark("cheekS1", (0.872, 1.035, 0.15), (0.082, 0.0155, 0.06), [0, 0, 30], kc=0.011),
    mark("eyeLine", (0.985, 1.16, 0.115), (0.028, 0.009, 0.05), [0, 0, 8]),
    mark("browB0", (1.004, 1.236, 0.036), (0.009, 0.025, 0.022), [0, 26, 0]),
    mark("browB1", (0.983, 1.244, 0.042), (0.01, 0.025, 0.026), [0, 32, 0]),
    mark("browB2", (0.96, 1.25, 0.047), (0.01, 0.025, 0.028), [0, 38, 0]),
    mark("foreLine", (0.972, 1.252, 0), (0.03, 0.025, 0.009), [0, 0, 0], mirror=False),
]
sh = [s for s in T['sculpt']['shape'] if s['id'] not in DROP]
for s in sh:   # (the neck and throat in the body's frame too: they were already; the rest of the head's are new)
    if s.get('bone') == 'neck' and s.get('pat'): s['frame'] = 'body'
# (round 5) THE LEGS' HIDDEN CORES: bodymesh.js paints a vertex from its two nearest pattern GROUPS (the body's frame;
# each leg's own), the pair slotted by group order -- and on the inside of a leg the second nearest flipped between the
# body and the other leg from vertex to vertex, so the leg's frame jumped between the two slots and the stripes came out
# as a zigzag of fine lines (the "crease" above the paw). A thin core down each leg, deep inside it and laid in the
# body's frame, is always nearer than the other leg: every leg vertex pairs its own frame with the body's, in one order.
# (it never reaches the surface: 1.4 cm thick and ~5 cm under the skin, past the crossfade's band, so it paints nothing)
cores = [
    {"id": "coreFL", "type": "tube", "bone": "legFLl", "pts": [[0.5, 0.6, 0.155, 0.014], [0.445, 0.44, 0.165, 0.014], [0.465, 0.28, 0.165, 0.014], [0.49, 0.11, 0.165, 0.014]],
     "k": 0.002, "color": "@leg", "pat": "stripes", "frame": "body", "mirror": True},
    {"id": "coreHL", "type": "tube", "bone": "legHLl", "pts": [[-0.68, 0.62, 0.13, 0.014], [-0.6, 0.44, 0.13, 0.014], [-0.69, 0.28, 0.13, 0.014], [-0.655, 0.1, 0.13, 0.014]],
     "k": 0.002, "color": "@leg", "pat": "stripes", "frame": "body", "mirror": True},
]
T['sculpt']['shape'] = sh + cores + face + extra
eyes = copy.deepcopy(L['sculpt']['eyes'])
for k in ('at', 'from', 'r'): eyes[k] = tx(eyes[k])
eyes['color'] = '@eyeBall'
T['sculpt']['eyes'] = eyes
T["sculpt"]["mesh"] = {"tris": [13500, 3300], "cell": 0.0095}   # (round 4: a finer cell, for the toes and the face's marks; round 5: finer again, 0.013 -> 0.0095, so the cheek strokes come out smooth, not sawn)
lp = L['params']
T['params'] = {**T['params'], "tX": 0.04, "tY": -0.095, "hs": 1.2, "jowls": True, "headW": 1.06, "jaw": 1.0,
               **{k: lp[k] for k in ('eyeX', 'eyeY', 'eyeZ', 'eyeF', 'earX', 'earZ', 'eyeS')},
               "faceX": -0.025, "mw": 1.4, "nS": 0.9, "earS": 1.25, "earY": 0.03, "pawS": 1.12, "wrist": 1.0}
T['colors'] = {**T['colors'], "noseRim": "#2e1c18", "pale": "#e2a874", "nose": "#c07a6c"}   # (the nose a pink-brick leather, dark-rimmed)
T['sculpt']['_about'] = (T['sculpt'].get('_about', '') + " || ROUND 2 (2026-11-07, scratchpad var/tgr.py): the lion's cat face (the L3/L4 shapes) moved "
                         "on by tX/tY and painted a tiger's; white cheek ruffs (ruffT/ruffP/ruffL); the crown striped in the body's frame; the lion's toe lobes || ROUND 3: "
                         "the face's own fine marks (cheekS*, eyeLine, browB*, foreLine: thin paint ells deep along the surface's normal), "
                         "flat round ears orange-rimmed with black backs (earBack) and the white spot, a smaller pink-brick nose || ROUND 4: "
                         "a bigger, broader head (hs 1.2) with a rounder skull, a short broad muzzle (faceX -0.025, mw 1.4), big white pads "
                         "and a squarer chin; the jowl ball flattened and the ruff a fringe of three locks (ruffU/P/L) swept back and down, the "
                         "cheek marks along it; round cat paws in the coat's colour (pawBase/hpawBase and the lion's toe lobes) || ROUND 5: the ruff's locks "
                         "thick with round tips, blended into the cheek; two broader cheek strokes; the pads pulled back behind the nose; a thin "
                         "hidden core down each leg in the body's frame (coreFL/coreHL) so the leg stripes' frame never swaps slots on the inside of a leg")
json.dump(T, open(sys.argv[2], 'w'), indent=1)
print('shapes', len(T['sculpt']['shape']))
