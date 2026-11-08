# the snake's coats and variants: girth, the grass snake's bars and collar gated, the patterns (snakemarks.mjs) as paints
import json, sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from jfmt import dumps
src, marks, dst = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(src))
M = json.load(open(marks))
f4 = lambda x: float('%.5g' % x)
d['_about'] = d['_about'].split(' || ')[0] + (" || COATS AND VARIANTS (2026-11-06): params girth (the trunk's thickness, the neck less, the "
  "belly kept on the ground), bars and collar (the grass snake's), zig (an adder's zig-zag, flank spots, the X on its crown, the stripe behind the "
  "eye), dots (a smooth snake's paired spots, dark crown, eye stripe), saddles (a corn snake's red saddles edged black, flank blotches, a chequered "
  "belly), rings (a coral snake's red-yellow-black), blotch (a python's), slit (a vertical pupil); colours mark (the dark of a pattern), fill "
  "(its inside: a saddle's red, a python's brown), band (a coral snake's yellow), head (the head's top, else body). The patterns are PAINTS "
  "(op paint: colour only, no shape) laid along the rest pose's curve by a script, written with girth so they stay on the skin. Coats: the "
  "temperate ones the meadow picks from; variants: the exotic ones (asset manager only)")
P = {"girth": 1, "bars": True, "collar": True, "zig": False, "dots": False, "saddles": False, "rings": False, "blotch": False, "slit": False}
d = {**{k: d[k] for k in ('name', '_about', 'kind')}, 'params': P, **{k: v for k, v in d.items() if k not in ('name', '_about', 'kind', 'params')}}
d['colors'].update({"mark": "#1a1c12", "fill": "#5d6a3a", "band": "#e0c64a"})
sh = [q for q in d['sculpt']['shape'] if not q['id'].startswith('pz_')]
W_FRONT = {0: .3, 1: .55, 2: .85, 3: 1}
W_FRONTV = {0: .25, 1: .45, 2: 1}
def g(w): return 'girth' if w == 1 else f'(1+{w}*(girth-1))'
for q in sh:
    i = q['id']
    if i.startswith(('barL', 'barR', 'barDL', 'barDR')): q['when'] = 'bars'
    if i in ('collarY', 'collarB'): q['when'] = 'collar'
    if i in ('skull', 'snout', 'jaw', 'temple', 'brow', 'frontal', 'parietal', 'supraoc', 'internas') and q.get('color') == '@body': q['color'] = ['@head', '@body']
    if q['type'] == 'tube' and (i == 'front' or i.startswith('seg')) and not i.endswith('V'):
        for j, p in enumerate(q['pts']):
            w = W_FRONT[j] if i == 'front' else 1
            r = p[4]
            p[2] = f'{f4(r)}*({g(w)}-1)' if w != 1 else f'{f4(r)}*(girth-1)'
            p[4] = f'{f4(r)}*{g(w)}'
    if q['type'] == 'tube' and i.endswith('V') and (i == 'frontV' or i.startswith('seg')):
        for j, p in enumerate(q['pts']):
            w = W_FRONTV[j] if i == 'frontV' else 1
            r, dy, rm = p[4], p[2], p[4] * 1.617
            p[2] = f'{f4(dy + rm)}*{g(w)}-{f4(rm)}'
            p[4] = f'{f4(r)}*{g(w)}'
d['sculpt']['shape'] = sh + M
d['sculpt']['eyes']['pupil'] = {"when": "slit", "v": "slit"}
d['sculpt']['eyes']['lid'] = ["@head", "@body"]
coats = [
  {"name": "grass snake"},
  {"name": "adder (male)", "scale": 0.42, "params": {"girth": 1.3, "bars": False, "collar": False, "zig": True, "slit": True},
   "body": "#8e8b80", "head": "#86837a", "belly": "#2c2a28", "mark": "#151311", "plate": "#86837a", "eye": "#a8452a", "tongue": "#3a1c22"},
  {"name": "adder (female)", "scale": 0.45, "params": {"girth": 1.35, "bars": False, "collar": False, "zig": True, "slit": True},
   "body": "#9c7446", "head": "#94703f", "belly": "#3a2e24", "mark": "#3a2210", "plate": "#94703f", "eye": "#b04a26", "tongue": "#3a1c22"},
  {"name": "smooth snake", "scale": 0.42, "params": {"girth": 0.9, "bars": False, "collar": False, "dots": True},
   "body": "#8c7862", "head": "#857058", "belly": "#6a4c38", "mark": "#3a2a1e", "plate": "#857058", "eye": "#b8702e"},
]
variants = {
  "corn snake": {"scale": 0.85, "params": {"girth": 0.95, "bars": False, "collar": False, "saddles": True},
                 "colors": {"body": "#dc7a3a", "head": "#d8763a", "belly": "#efe8da", "fill": "#c2361c", "mark": "#1c1410", "plate": "#d8763a", "eye": "#c86a2a"}},
  "coral snake": {"scale": 0.5, "params": {"girth": 0.8, "bars": False, "collar": False, "rings": True},
                  "colors": {"body": "#c8301e", "head": "#141210", "belly": "#141210", "fill": "#c8301e", "mark": "#141210", "band": "#eec83a", "plate": "#141210", "eye": "#141210"}},
  "green tree snake": {"scale": 0.8, "params": {"girth": 0.62, "bars": False, "collar": False},
                       "colors": {"body": "#4a9a2c", "head": "#4a9a2c", "belly": "#e2d84a", "plate": "#4a9a2c", "eye": "#b89a3c"}},
  "python": {"scale": 2.5, "params": {"girth": 1.55, "bars": False, "collar": False, "blotch": True, "slit": True},
             "colors": {"body": "#c4a26a", "head": "#c09c64", "belly": "#e6dec6", "fill": "#6e4a28", "mark": "#241a12", "plate": "#c09c64", "eye": "#a08050"}},
}
# (a coat is written flat, its colours beside its name and params, like the horse's; a variant carries `colors`)
keys = list(d)
out = {}
for k in keys:
    out[k] = d[k]
    if k == 'colors':
        out['coats'] = coats
        out['variants'] = variants
open(dst, 'w').write(dumps(out))
print('shapes', len(out['sculpt']['shape']), 'bytes', len(dumps(out)))
