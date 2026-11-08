# l3.py LION_JSON -- lioness round 3, applied to the live file (idempotent: drops the shapes it adds, then adds them again)
#   head: the lioness gets her own head (when: lean) -- rounded crown, steep stop, short boxy muzzle, puffy pads,
#         forward eyes, side-set ears with dark backs; the male's head shapes are kept as they were (when: jowls)
#   legs: both lions -- compact paws with toe lobes (<= ~1.3x the leg above), a bent wrist, a clear hock, tapered thighs
import json, sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from jfmt import dumps
fn = sys.argv[1]
d = json.load(open(fn))
SC = d['sculpt']; shapes = SC['shape']; SC['mesh']['cell'] = .014; SC['mesh']['tris'] = [12000, 3200]   # (the grid: 1.4cm, the face and toes need it -- from the area it was 2.5cm)
MINE = lambda s: s['id'].startswith('L3') or s['id'].startswith('toe') or s['id'].startswith('htoe')
shapes[:] = [s for s in shapes if not MINE(s)]
by = {s['id']: s for s in shapes}

# ---- params (the male's values keep him as he was, except the paws and legs) ----
P = d['params']
P.update({'pawS': 1, 'hock': 1, 'hind': 1, 'eyeX': 0, 'eyeY': 0, 'eyeZ': 0, 'eyeF': 0})
V = d['variants']['lioness']; VP = V['params']
VP.update({'neckG': .74, 'wrist': .82, 'pawS': .8, 'hock': .9, 'hind': .86})
for k in ('headW', 'headH', 'headL', 'snout', 'padS', 'earDy', 'earDz', 'earIn'): VP.pop(k, None)   # (her own head now: these drove the male's shapes)

# ---- the male's head shapes: his alone now ----
MALE = ['skull', 'bridge', 'muzzle', 'pad', 'chin', 'nose', 'brow', 'browR', 'eyeIn', 'eyeOut', 'tear', 'lip', 'ear', 'earIn', 'earBack']
for i in MALE:
    if i in by: by[i]['when'] = 'jowls'
shapes[:] = [s for s in shapes if s['id'] not in ('jawF', 'cheekF')]

# ---- eyes: forward and more frontal for her (params; 0 for him) ----
E = SC['eyes']
E['at'] = ['1.0119+eyeX', '1.1784+eyeY', '0.0828+eyeZ']; E['from'] = ['0.874+eyeF', 1.1523, 0.0]
VP.update({'eyeX': .026, 'eyeY': .006, 'eyeZ': -.014, 'eyeF': -.06})

H = lambda id, **kw: shapes.append({'id': id, 'when': 'lean', 'bone': 'head', **kw})
# skull: a rounded crown, the broad forehead dropping steeply to the bridge
H('L3cran', type='ell', c=[0.893, 1.166, 0], r=[0.13, 0.098, 0.106], k=0.05, color='@head')
H('L3brow', type='ell', c=[0.983, 1.19, 0], r=[0.066, 0.06, 0.082], k=0.035, color='@head')
H('L3cheek', type='ell', c=[0.935, 1.104, 0.058], r=[0.1, 0.056, 0.054], k=0.07, color='@head', mirror=True)
# the face: a short bridge, a boxy muzzle, puffy whisker pads with a crease to the cheek, a white chin
H('L3bridge', type='cone', a=[1.0, 1.183, 0], b=[1.122, 1.142, 0], ra=0.045, rb=0.03, k=0.03, color='@bridge')
H('L3muzzle', type='ell', c=[1.072, 1.074, 0], r=[0.078, 0.058, 0.054], k=0.03, color='@head')
H('L3pad', type='ell', c=[1.1, 1.068, 0.04], r=[0.046, 0.033, 0.034], k=0.016, color='@muzzle', mirror=True)
H('L3lipW', type='ell', c=[1.098, 1.036, 0.03], r=[0.04, 0.018, 0.028], k=0.012, color='@white', mirror=True)
H('L3chin', type='ell', c=[1.058, 1.006, 0], r=[0.048, 0.026, 0.04], k=0.018, color='@white')
H('L3jaw', type='cone', a=[0.86, 1.03, 0], b=[1.035, 1.012, 0], ra=0.062, rb=0.04, k=0.035, color='@pale')
H('L3nose', type='ell', c=[1.138, 1.11, 0], r=[0.022, 0.02, 0.032], k=0.012, kc=0.004, color='@nose', wet=0.45)
# paints: the nose leather's dark rim, the lip line and philtrum, the white under the eye, the tear line
H('L3noseRim', op='paint', type='ell', c=[1.152, 1.112, 0], r=[0.02, 0.026, 0.038], kc=0.004, color='@noseRim')
H('L3noseLeather', op='paint', type='ell', c=[1.156, 1.113, 0], r=[0.02, 0.019, 0.029], kc=0.004, color='@nose')
H('L3mouth', op='paint', type='tube', pts=[[1.03, 1.036, 0.056, 0.007], [1.08, 1.03, 0.048, 0.007], [1.12, 1.033, 0.028, 0.007], [1.138, 1.042, 0.006, 0.006]], kc=0.005, color='@black', mirror=True)
H('L3philtrum', op='paint', type='tube', pts=[[1.15, 1.09, 0, 0.006], [1.142, 1.045, 0, 0.006]], kc=0.004, color='@black')
H('L3underEye', op='paint', type='ell', c=[1.04, 1.165, 0.062], r=[0.032, 0.015, 0.026], kc=0.006, color='@white', mirror=True)
H('L3tear', op='paint', type='tube', pts=[[1.05, 1.18, 0.05, 0.007], [1.066, 1.15, 0.054, 0.0065], [1.078, 1.118, 0.058, 0.006]], kc=0.005, color='@tear', mirror=True)
H('L3lid', op='paint', type='ell', c=[1.04, 1.19, 0.064], r=[0.03, 0.03, 0.02], kc=0.003, color='@lidLine', mirror=True)
# ears: rounded, set to the sides, black backs, pale inside
EA = lambda id, **kw: shapes.append({'id': id, 'when': 'lean', 'bone': 'earL', 'mirror': True, **kw})
EA('L3ear', type='ell', c=[0.86, 1.226, 0.126], r=[0.02, 0.039, 0.037], rot=[-38, -24, 0], k=0.018, color='@earBack')
EA('L3earIn', op='paint', type='ell', c=[0.878, 1.218, 0.134], r=[0.014, 0.024, 0.02], rot=[-38, -24, 0], kc=0.004, color='@earIn')
EA('L3earBase', op='paint', type='ell', c=[0.85, 1.192, 0.114], r=[0.04, 0.024, 0.04], rot=[-38, -24, 0], kc=0.008, color='@head')

# (the face forward: nose to eye about eye to ear, as a lioness's -- every face shape moved FACE metres along x)
FACE = .032
for q in shapes:
    if q.get('when') != 'lean' or q.get('bone') != 'head' or q['id'] in ('L3cran', 'L3brow', 'L3cheek', 'L3underEye', 'L3lid'): continue
    if q['id'] in ('L3bridge', 'L3jaw'): q['b'][0] = round(q['b'][0] + FACE, 4)
    elif 'c' in q: q['c'][0] = round(q['c'][0] + FACE, 4)
    elif 'pts' in q: q['pts'] = [[round(p[0] + FACE * (1 if q['id'] != 'L3tear' else .5 * i / (len(q['pts']) - 1)), 4)] + p[1:] for i, p in enumerate(q['pts'])]
by2 = {q['id']: q for q in shapes}
by2['L3muzzle']['c'][0] = round(by2['L3muzzle']['c'][0] - .012, 4); by2['L3muzzle']['r'][0] = .092   # (reaching back to the cheeks still)
by2['L3bridge']['ra'] = .047
# (his muzzle longer than hers: faceX metres further forward, 0 for her)
for q in shapes:
    if q.get('when') != 'lean' or q.get('bone') != 'head' or q['id'] in ('L3cran', 'L3brow', 'L3cheek', 'L3underEye', 'L3lid'): continue
    if q['id'] in ('L3bridge', 'L3jaw'): q['b'][0] = f"{q['b'][0]}+faceX"
    elif 'c' in q: q['c'][0] = f"{q['c'][0]}+faceX"
    elif 'pts' in q: q['pts'] = [[f"{p[0]}+faceX" if q['id'] != 'L3tear' or i == len(q['pts']) - 1 else p[0]] + p[1:] for i, p in enumerate(q['pts'])]
for i in ('L3muzzle',): by2[i]['r'][0] = "0.092+faceX*0.6"
for i in ('L3muzzle', 'L3pad', 'L3lipW', 'L3chin', 'L3nose', 'L3noseRim', 'L3noseLeather'):   # (and broader: x1.15 for him)
    q = by2[i]; q['r'][2] = f"{q['r'][2]}*(1+faceX*5)"
    if 'c' in q and q['c'][2]: q['c'][2] = f"{q['c'][2]}*(1+faceX*5)"
P['faceX'] = .03; VP['faceX'] = 0

# ---- legs and paws: both lions ----
f = lambda *a: [x if isinstance(x, str) else round(x, 4) for x in a]
by['pastern'].update(a=[0.428, 0.17, 0.1489], b=[0.468, 0.074, 0.1489], ra='0.074*wrist', rb='0.066*wrist', k=0.02)
by['forearm'].update(b=[0.43, 0.165, 0.1489], rb='0.076*wrist')
by['paw'].update(c=[0.49, '0.05*pawS', 0.1489], r=['0.088*pawS', '0.05*pawS', '0.082*pawS'], k=0.02)
by['hock'].update(a=[-0.578, 0.33, 0.1173], b=[-0.522, 0.082, 0.1173], ra='0.05*hock', rb='0.044*hock', k=0.02)
by['gaskin'].update(a=[-0.455, 0.53, 0.1173], b=[-0.58, 0.335, 0.1173], ra='0.082*hind', rb='0.05*hock', k=0.04)
by['thigh'].update(c=[-0.54, 0.7, 0.1173], r=['0.17*hind', '0.215*hind', '0.112*hind'], rot=[0, 0, 32])
by['hpaw'].update(c=[-0.478, '0.046*pawS', 0.1155], r=['0.078*pawS', '0.046*pawS', '0.06*pawS'], k=0.018)
L = lambda id, bone, **kw: shapes.append({'id': id, 'bone': bone, 'mirror': True, **kw})
L('L3carpal', 'footFL', type='ell', c=[0.405, 0.16, 0.1489], r=['0.03*wrist', '0.034*wrist', '0.04*wrist'], k=0.015, color='@leg')
L('L3heel', 'legHLl', type='ell', c=[-0.607, 0.345, 0.1173], r=['0.034*hock', '0.04*hock', '0.03*hock'], k=0.016, color='@leg')
for i, (dx, dz) in enumerate([(.078, -.052), (.088, -.018), (.088, .018), (.078, .052)]):   # four toe lobes round the paw's front
    L(f'toe{i}', 'footFL', type='ell', c=[f'0.49+{dx}*pawS', '0.034*pawS', f'0.1489+{dz}*pawS'], r=['0.033*pawS', '0.036*pawS', '0.026*pawS'], k=0.006, color=['@paw', '@leg'])
    L(f'htoe{i}', 'footHL', type='ell', c=[f'-0.478+{dx * .85:.4f}*pawS', '0.031*pawS', f'0.1155+{dz * .8:.4f}*pawS'], r=['0.027*pawS', '0.031*pawS', '0.02*pawS'], k=0.008, color=['@paw', '@leg'])

# ---- colours ----
C = d['colors']; C.setdefault('noseRim', '#3a2420'); C.setdefault('earBack', '#2a1c12'); C.setdefault('lidLine', '#1a1410'); C.setdefault('earIn', '#d2b88e')
VC = V['colors']; VC.update({'nose': '#b98270', 'noseRim': '#3e2a22', 'earBack': '#241810', 'earIn': '#e6d6b6', 'white': '#f1e8d6', 'muzzle': '#d8bf92', 'tear': '#4a3020'})
# (2nd pass: the new face for HIM too -- his old long-snouted face dropped, the cranium under his mane; his cheek pods and
#  jowls kept (when: jowls), and his eyes forward as hers)
SHARED = True
if SHARED:
    shapes[:] = [q for q in shapes if q['id'] not in MALE]
    for q in shapes:
        if q['id'].startswith('L3'): q.pop('when', None)
    for k in ('eyeX', 'eyeY', 'eyeZ', 'eyeF'): P[k] = VP.pop(k)
import re
_txt = json.dumps({k: v for k, v in d.items() if k not in ('params', 'variants', '_about')})
for k in list(P):   # (the params nothing reads any more: the male's old head factors)
    if k != 'earIn' and (k in ('s', 'tuft', 'tailSway') or re.search(r'\b' + k + r'\b', _txt) or k in ('mane', 'jowls', 'lean')): continue
    P.pop(k); VP.pop(k, None); print('param dropped', k)
d['_about'] = d['_about'].split(' || ')[0] + (" || THE FACE AND FEET (2026-11-06): one cat's face for both -- the L3 shapes: a rounded "
  "cranium and a broad forehead dropping steeply to a short bridge (L3cran, L3brow, L3bridge), broad cheeks, a boxy muzzle with puffy whisker "
  "pads creased off the cheek, a white upper lip and chin, a broad nose leather with a dark rim (paints), the lip line and philtrum and a tear line "
  "painted, white under the eyes; the eyes forward and frontal (eyeX/eyeY/eyeZ/eyeF on sculpt.eyes); round ears to the side, black-backed and "
  "pale inside. faceX: metres his muzzle sits further forward than hers. The paws compact (pawS) with four toe lobes each, about 1.25x the leg "
  "above; a carpal bump and a bent pastern at the wrist (wrist); a clear hock with the heel behind it (hock); the thigh tapering to the knee "
  "(hind). mesh.cell 1.4cm, 12000 triangles near: the face and toes need it")
V['_about'] = ("VARIANTS (2026-11-06; species.js variantDef, creatures.js dressed): `lioness` -- the mane off (every mane and lock shape "
  "says `when: mane`), his cheek pods and jowls off (`jowls`), and the factors he is written over turned down: girth (the trunk), neckG (the "
  "neck: clearly narrower than her head), fore / wrist (the foreleg above and at the wrist), pawS (the paws), hock / hind (the hind leg below and "
  "above the hock), faceX 0 (her shorter muzzle); a smaller tail tuft, sandy-buff colours paler beneath, a pinkish nose, and `scale` .8: the whole "
  "of her at .8 his size. The world keeps her in his pride (index.html: three with the meadow's lion, three of the Colosseum's four)")
open(fn, 'w').write(dumps(d))
print('shapes', len(shapes), 'lioness-only', sum(1 for s in shapes if s.get('when') == 'lean'))
