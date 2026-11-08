import json, sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from jfmt import dumps
src, marks, dst = sys.argv[1:4]
d = json.load(open(src)); M = json.load(open(marks))
d['_about'] = d['_about'].split(' || ')[0] + (" || COATS AND VARIANTS (2026-11-06): params spots (the dark patches), ridges (the pale "
  "dorsolateral ridges and the lid line), mask (the dark mask behind the eye), stripe (a tree frog's dark side stripe, edged pale), midline (a pool "
  "frog's pale line down the spine), bands (a dart frog's yellow bands), flankBars (a red-eyed tree frog's pale bars on its blue flanks), pupilBar / "
  "pupilSlit (horizontal, vertical; neither: round), tympS (the eardrum's size); colours limb (arms and feet, else side), leg (thighs and shanks, "
  "else back), toe (fingers and toes, else limb), stripe, stripeEdge, midline, band, bar. The markings are PAINTS (op paint: colour only). Coats: the "
  "European ones the game picks from; variants: the exotic ones (asset manager only)")
P = {"spots": True, "ridges": True, "mask": True, "stripe": False, "midline": False, "bands": False, "flankBars": False, "pupilBar": True, "pupilSlit": False, "tympS": 1}
d = {**{k: d[k] for k in ('name', '_about', 'kind')}, 'params': P, **{k: v for k, v in d.items() if k not in ('name', '_about', 'kind', 'params')}}
d['colors'].update({"stripe": "#3a2a1a", "stripeEdge": "#e8e0b0", "midline": "#c4d474", "band": "#f0c020", "bar": "#efe6c0"})
sh = [q for q in d['sculpt']['shape'] if not q['id'].startswith('pf_')]
for q in sh:
    i = q['id']
    if q.get('pat') == 'patches': q['pat'] = {"when": "spots", "v": "patches"}
    if i in ('lidLine', 'ridge'): q['when'] = 'ridges'
    if i == 'mask': q['when'] = 'mask'
    if i == 'tympanum': q['r'] = ["0.0048*tympS", "0.0048*tympS", 0.0018]
    if i in ('arm', 'tarsus'): q['color'] = ["@limb", "@side"]
    if i.startswith(('finger', 'toe')): q['color'] = ["@toe", "@limb", "@side"]
    if i in ('thigh', 'shank'): q['color'] = ["@leg", "@back"]
    if i == 'mouth':   # (a closed frog mouth is a thin soft line: a paint, not a ridged tube -- the tube's hard vertex colours read as teeth)
        q['op'] = 'paint'; q.pop('k', None); q['kc'] = .001; q['pts'] = [p[:3] + [.0012] for p in q['pts']]
d['sculpt']['shape'] = sh + M
d['sculpt']['eyes']['pupil'] = [{"when": "pupilSlit", "v": "slit"}, {"when": "pupilBar", "v": "bar"}]
coats = [
  {"name": "common frog (olive)"},
  {"name": "common frog (brown)", "back": "#8a6a40", "side": "#9c7c4e", "belly": "#e8dcc0", "ridge": "#b89a64", "tymp": "#5a3e22", "mask": "#3e2a18", "web": "#8e7a54", "eye": "#c09040"},
  {"name": "pool frog", "scale": 0.9, "params": {"mask": False, "midline": True},
   "back": "#6aa23a", "side": "#88aa48", "belly": "#eee8ca", "ridge": "#b8b45a", "midline": "#bcd46c", "tymp": "#6a7a34", "web": "#8aa050", "eye": "#c8a43a"},
  {"name": "European tree frog", "scale": 0.45, "params": {"spots": False, "ridges": False, "mask": False, "stripe": True},
   "back": "#4caa2c", "side": "#4caa2c", "belly": "#f0ead2", "limb": "#4caa2c", "leg": "#4caa2c", "toe": "#bcae6a", "web": "#78ae48", "tymp": "#4a9e2c", "stripe": "#4a3420", "stripeEdge": "#eee6b8", "eye": "#c8a43a"},
]
variants = {
  "bullfrog": {"scale": 1.7, "params": {"ridges": False, "mask": False, "tympS": 1.7},
               "colors": {"back": "#5a6c38", "side": "#6e7a44", "belly": "#ece4c0", "tymp": "#585a32", "web": "#6a7444", "eye": "#b88a30"}},
  "blue poison dart frog": {"scale": 0.45, "params": {"ridges": False, "mask": False, "pupilBar": False},
               "colors": {"back": "#2c66c8", "side": "#2a5cba", "belly": "#2450a8", "limb": "#1d4296", "leg": "#2454b4", "toe": "#1d4296", "web": "#1d4296", "tymp": "#2a5cba", "ridge": "#2c66c8", "mouth": "#141820", "eye": "#0e0e12", "eyeDark": "#060608"}},
  "yellow-banded dart frog": {"scale": 0.38, "params": {"ridges": False, "mask": False, "pupilBar": False, "bands": True},
               "colors": {"back": "#171614", "side": "#171614", "belly": "#171614", "limb": "#e8b818", "leg": "#e8b818", "toe": "#171614", "web": "#171614", "band": "#f0c018", "tymp": "#171614", "ridge": "#171614", "eye": "#0e0e12", "eyeDark": "#060608"}},
  "red-eyed tree frog": {"scale": 0.6, "params": {"spots": False, "ridges": False, "mask": False, "flankBars": True, "pupilBar": False, "pupilSlit": True},
               "colors": {"back": "#52b03c", "side": "#2c5cb4", "belly": "#f2ecd6", "limb": "#52b03c", "leg": "#52b03c", "toe": "#f08c2a", "web": "#f08c2a", "tymp": "#52b03c", "bar": "#f0e6b4", "eye": "#d8241a", "eyeDark": "#6a0c0c"}},
}
out = {}
for k in d:
    out[k] = d[k]
    if k == 'colors': out['coats'] = coats; out['variants'] = variants
open(dst, 'w').write(dumps(out)); print('frog shapes', len(out['sculpt']['shape']))
