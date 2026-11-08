import json, re
p = 'assets/creatures/mammals/lion.json'; s = open(p).read()
lines = s.split('\n'); out = []
def X(v, e): return '%s%s' % (v if isinstance(v, str) else ('%g' % v), e)
for ln in lines:
    m = re.match(r'(\s*)(\{"id": "([^"]+)".*\})(,?)$', ln)
    if not m: out.append(ln); continue
    ind, body, sid, comma = m.groups(); o = json.loads(body)
    if sid in ('cheek', 'jowl'):
        o = {'id': sid, 'when': 'jowls', **{k: v for k, v in o.items() if k != 'id'}}
    if sid == 'skull': o['r'][0] = '0.1881*headL'
    if sid == 'muzzle': o['c'][0] = '1.0621+snout'; o['r'][0] = '0.0863+snout'; o['r'][2] = 0.0885
    if sid in ('pad', 'chin', 'nose'): o['c'][0] = X(o['c'][0], '+snout')
    if sid == 'bridge': o['b'][0] = '1.1516+snout'
    if sid == 'lip': o['c'][0] = '1.0792+snout'; o['seat']['from'][0] = '0.9994+snout'
    if sid in ('paw', 'hpaw'): o['color'] = ['@paw', '@leg']
    if sid in ('belly', 'pouch'): o['kc'] = 0.075
    if sid == 'arm': o['pts'] = [q[:3] + [X(q[3], '*fore')] for q in o['pts']]
    if sid == 'triceps': o['r'] = [X(v, '*fore') for v in o['r']]
    if sid == 'forearm': o['ra'] = '0.1171*fore'; o['rb'] = '0.0799*wrist'
    if sid == 'pastern': o['ra'] = '0.0799*wrist'; o['rb'] = '0.0826*wrist'
    if sid in ('ear', 'earIn', 'earBack'):
        o['c'] = [o['c'][0], X(o['c'][1], '+earDy'), X(o['c'][2], '+earDz')]
    if sid == 'earIn':
        o['r'] = [X(v, '*earIn') for v in o['r']]; o['color'] = ['@earIn', '@cream']
    if sid in ('tear1', 'tear2'): continue
    if sid == 'tear0':
        # ONE soft stripe a side, from the inner corner of the eye down the muzzle: sunk under the surface (seat out < 0) so it
        # shapes nothing, and painted through it softly (kc) -- the old three seated slivers stood proud and read as cracks
        o = {"id": "tear", "type": "ell", "bone": "head", "c": [1.058, 1.122, 0.068], "r": [0.048, 0.007, 0.007], "rot": [0, 0, -64],
             "k": 0.002, "kc": 0.014, "color": "@tear", "mirror": True, "seat": {"from": [0.874, 1.1523, 0.0], "out": -0.2}}
        out.append(ind + json.dumps(o) + comma)
        # (and a lean jaw for the maneless: the jowls and the cheeks' pods off -- `jowls` -- and the jaw a clean line to the chin)
        o = {"id": "jawF", "when": "lean", "type": "cone", "bone": "head", "a": [0.85, 1.045, 0.0], "b": ["1.0+snout", 1.008, 0.0],
             "ra": 0.072, "rb": 0.046, "k": 0.05, "color": "@head"}
        out.append(ind + json.dumps(o) + comma)
        o = {"id": "cheekF", "when": "lean", "type": "ell", "bone": "head", "c": [0.9, 1.095, "0.07*headW"], "r": [0.105, 0.06, 0.05],
             "k": 0.045, "color": "@head", "mirror": True}
        out.append(ind + json.dumps(o) + comma)
        continue
    out.append(ind + json.dumps(o) + comma)
s = re.sub(r',(\s*\n\s*\])', r'\1', '\n'.join(out))
old = '"jaw": 1\n  },'
new = '"jaw": 1,\n    "jowls": true,\n    "lean": false,\n    "headL": 1,\n    "snout": 0,\n    "fore": 1,\n    "wrist": 1,\n    "earDy": 0,\n    "earDz": 0,\n    "earIn": 1\n  },'
assert s.count(old) == 1; s = s.replace(old, new, 1)
d = json.loads(s)
# colours: the paws as the legs (a touch paler), for him too -- they were @pale, slippers
assert s.count('"tear": "#7a5530"\n') == 1
s = s.replace('"tear": "#7a5530"\n', '"tear": "#6a4628",\n    "paw": "#c39b58"\n', 1)
d = json.loads(s)
v = d['variants']['lioness']
v['params'] = {"mane": False, "jowls": False, "lean": True, "tuft": 0.06, "girth": 0.88, "neckG": 1, "headW": 0.85, "headH": 0.9,
               "headL": 0.92, "snout": 0.03, "jaw": 1, "fore": 0.9, "wrist": 0.74, "earDy": -0.012, "earDz": 0.014, "earIn": 0.7}
v['colors'].update({"paw": "#c8a468", "tear": "#5e3e22", "earIn": "#d2b88e"})
i = s.index('    "lioness": {'); j = s.index('\n', i)
s = s[:i] + '    "lioness": ' + json.dumps(v) + s[j:]
assert json.loads(s)['variants']['lioness'] == v
open(p, 'w').write(s); print('ok')
