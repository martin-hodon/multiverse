# l4.py IN_JSON OUT_JSON -- lioness round 4 on top of round 3 (IN = var/lion_r3.json; run from scratch, never on its own output)
#   ears x~2, higher and forward, tufted; the muzzle integrated (flat-fronted, wide, soft cream); bigger darker nose;
#   white chin + lower lip; her head x1.15 (hs) with a narrower neck; eye x.8 under a heavier brow; heavier legs, paws ~1.4x
import json, sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from jfmt import dumps
d = json.load(open(sys.argv[1]))
SC = d['sculpt']; shapes = SC['shape']; by = {s['id']: s for s in shapes}
P = d['params']; V = d['variants']['lioness']; VP = V['params']
T = dict(EH=None)

# ---- params ----
P.update({'hs': 1, 'earS': 1.4, 'earX': 0.004, 'earY': 0.012, 'earZ': -0.004, 'mw': 1, 'nS': 1.15, 'eyeS': 1, 'pawS': 1.1})
VP.update({'hs': 1.15, 'earS': 1.55, 'earX': 0.012, 'earY': 0.026, 'earZ': -0.012, 'mw': 1.12, 'nS': 1.28, 'eyeS': 0.8,
           'neckG': 0.7, 'fore': 1, 'wrist': 1, 'pawS': 1.05, 'hock': 1, 'hind': 1})

# ---- ears: bigger (earS), higher and forward (earX/Y/Z), black-backed, a pale tufted inside ----
ear = by['L3ear']
ear.update(c=['0.86+earX', '1.226+earY', '0.126+earZ'], r=[0.024, '0.039*earS', '0.037*earS'], k=0.02)
by['L3earIn'].update(c=['0.86+earX+0.012*earS', '1.226+earY-0.01*earS', '0.126+earZ+0.009*earS'], r=[0.016, '0.021*earS', '0.017*earS'], kc=0.007)
by['L3earBase'].update(c=['0.85+earX', '1.226+earY-0.034*earS', '0.12+earZ'], r=[0.044, '0.022*earS', '0.044*earS'])
i = shapes.index(by['L3earIn'])
shapes.insert(i, {'id': 'L4earTuft', 'bone': 'earL', 'mirror': True, 'type': 'ell', 'c': ['0.872+earX', '1.226+earY-0.02*earS', '0.128+earZ+0.004*earS'],
                  'r': [0.012, '0.014*earS', '0.012*earS'], 'rot': [-38, -24, 0], 'k': 0.008, 'color': '@earIn'})

# ---- the muzzle: wide (mw), deep, flat-fronted, the pads part of it; the cream a soft paint grading into the cheek ----
mz = by['L3muzzle']; mz['r'] = [mz['r'][0], 0.062, f"0.054*(1+faceX*5)*mw"]
pad = by['L3pad']
pad.update(c=['1.122+faceX', 1.064, '0.04*(1+faceX*5)*mw'], r=[0.036, 0.04, '0.036*(1+faceX*5)*mw'], k=0.03, color='@head')
i = shapes.index(by['L3noseRim'])
shapes.insert(i, {'id': 'L4padCream', 'bone': 'head', 'op': 'paint', 'type': 'ell', 'c': ['1.14+faceX', 1.06, 0],
                  'r': [0.06, 0.05, '0.07*(1+faceX*5)*mw'], 'kc': 0.045, 'color': '@muzzle'})
# white lower lip and chin, larger and lower
by['L3chin'].update(c=['1.09+faceX', 0.998, 0], r=[0.044, 0.026, '0.042*mw'], k=0.02)
by['L3lipW'].update(r=[0.04, 0.02, '0.03*mw'])
shapes.insert(i + 1, {'id': 'L4lowLip', 'bone': 'head', 'op': 'paint', 'type': 'ell', 'c': ['1.108+faceX', 1.016, 0],
                      'r': [0.034, 0.018, '0.044*mw'], 'kc': 0.008, 'color': '@white'})
# the nose leather: broader (nS), the rim and leather paints with it
for k in ('L3nose', 'L3noseRim', 'L3noseLeather'):
    q = by[k]; q['r'] = [q['r'][0], f"{q['r'][1]}*nS", f"{q['r'][2]}*nS"]
# a heavier brow over a smaller eye
SC['eyes']['r'] = '0.0241*eyeS'
shapes.insert(shapes.index(by['L3cheek']) + 1, {'id': 'L4browR', 'bone': 'head', 'mirror': True, 'type': 'ell', 'c': ['1.008+eyeX*0.6', '1.206+eyeY', '0.064+eyeZ'],
                  'r': [0.03, 0.013, 0.028], 'rot': [0, 0, -12], 'k': 0.026, 'color': '@head'})


# ---- his mane (optional ask): a ragged rim of tufts round the face and down the chest, darker toward the chest ----
import math
by['maneChest']['color'] = '@maneD'
for q in shapes: q.pop('coat', None)   # (no quill coat: its flat cards read as shards at full size -- the ragged edge is the sculpted tufts alone)
SC.pop('coat', None)
tufts = []
for j, th in enumerate(range(0, 181, 15)):            # 0 = top, 180 = under the chin, round the +z side (mirrored)
    t = math.radians(th); jit = (0.02, -0.015, 0.01, -0.02, 0.015)[j % 5]
    R0, R1 = 0.23 + jit, 0.335 + jit * 1.8 + (0.02 if 30 < th < 150 else -0.035 if th <= 30 else 0)
    cy, cx = 1.1, 0.83 - 0.05 * math.sin(t)
    a = [round(cx, 4), round(cy + R0 * math.cos(t), 4), round(R0 * math.sin(t), 4)]
    b = [round(cx - 0.08, 4), round(cy + R1 * math.cos(t) - 0.03, 4), round(R1 * math.sin(t) + (0.004 if th in (0, 180) else 0), 4)]
    col = '@maneF' if th < 60 else '@maneM' if th < 120 else '@maneD'
    tufts.append({'id': f'tuft{j}', 'when': 'mane', 'bone': 'neck' if th > 90 else 'head', 'mirror': th not in (0, 180), 'type': 'cone',
                  'a': a, 'b': b, 'ra': 0.06, 'rb': 0.02, 'k': 0.045, 'kc': 0.03, 'color': col})
for j, (x, y, z) in enumerate([(0.74, 0.62, 0.06), (0.66, 0.56, 0.12), (0.58, 0.55, 0.0), (0.7, 0.72, 0.15)]):   # the chest fringe, hanging
    tufts.append({'id': f'tuftC{j}', 'when': 'mane', 'bone': 'neck', 'mirror': z > 0, 'type': 'cone', 'a': [x, y + 0.1, z], 'b': [x + 0.02, y - 0.04, z * 1.1],
                  'ra': 0.07, 'rb': 0.014, 'k': 0.04, 'kc': 0.03, 'color': '@maneD'})
i = shapes.index(by['maneBack']) + 1
shapes[i:i] = tufts

# ---- her head x hs about the head joint: every head and ear shape, and the eyes ----
O = (0.874, 1.126, 0.0)
def pos(v, ax): return v if ax == 2 and False else (f"{O[ax]}+(({v})-{O[ax]})*hs" if ax < 2 else f"({v})*hs")
def rad(v): return f"({v})*hs"
for q in shapes:
    if q.get('bone') not in ('head', 'earL'): continue
    for key in ('c', 'a', 'b'):
        if key in q: q[key] = [pos(v, ax) for ax, v in enumerate(q[key])]
    if 'pts' in q: q['pts'] = [[pos(p[0], 0), pos(p[1], 1), pos(p[2], 2), rad(p[3])] for p in q['pts']]
    if 'r' in q: q['r'] = [rad(v) for v in q['r']] if isinstance(q['r'], list) else rad(q['r'])
    for key in ('ra', 'rb'):
        if key in q: q[key] = rad(q[key])
E = SC['eyes']
E['at'] = [pos(v, ax) for ax, v in enumerate(E['at'])]; E['from'] = [pos(v, ax) for ax, v in enumerate(E['from'])]; E['r'] = rad(E['r'])

# ---- colours: a darker, broader nose ----
VC = V['colors']; VC.update({'nose': '#9a6152', 'noseRim': '#2e1e18', 'muzzle': '#dcc499', 'earIn': '#dccaa4'})
d['colors']['nose'] = '#8e5a4c'

d['_about'] += (" || ROUND 4 (2026-11-06): hs scales every head and ear shape and the eyes about the head joint (her head 1.15); "
  "earS/earX/earY/earZ the ears' size and place (hers about twice his old ones, higher and forward, a pale tuft inside); mw the muzzle's width, "
  "the whisker pads part of it and the cream a soft paint (L4padCream) grading into the cheek; nS the nose leather; a white lower lip and chin; "
  "eyeS the eye (hers .8) under a heavier brow (L4browR)")
V['_about'] = V['_about'].replace("faceX 0 (her shorter muzzle);", "faceX 0 (her shorter muzzle); hs 1.15 (her head larger for her size), earS, mw, nS, eyeS (bigger ears, a wider muzzle, a broader nose, a smaller eye);")
open(sys.argv[2], 'w').write(dumps(d))
print('ok', len(shapes))
