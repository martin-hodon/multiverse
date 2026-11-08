import json, re, sys
p = 'assets/creatures/mammals/lion.json'; s = open(p).read(); d0 = json.loads(s)
lines = s.split('\n')
def fmt(x): return ('%.4f' % x).rstrip('0').rstrip('.') if isinstance(x, float) else str(x)
TRUNK = {'chest', 'keel', 'withers', 'loin', 'rump', 'belly', 'pouch'}
NECK = {'neck', 'throat'}
HEADW = {'skull', 'cheek', 'jowl', 'muzzle'}
out = []
for ln in lines:
    m = re.match(r'(\s*)(\{"id": "([^"]+)".*\})(,?)$', ln)
    if not m: out.append(ln); continue
    ind, body, sid, comma = m.groups(); o = json.loads(body)
    if sid.startswith('mane') or re.fullmatch(r'lock\d', sid):
        o = {'id': sid, 'when': 'mane', **{k: v for k, v in o.items() if k != 'id'}}
    def mul(key, i, f):
        o[key][i] = '%s*%s' % (fmt(o[key][i]), f)
    if sid in TRUNK: mul('r', 1, 'girth'); mul('r', 2, 'girth')
    if sid in NECK: mul('r', 1, 'neckG'); mul('r', 2, 'neckG')
    if sid in HEADW: mul('r', 2, 'headW')
    if sid == 'skull': mul('r', 1, 'headH')
    if sid == 'cheek': mul('c', 2, 'headW')
    out.append(ind + json.dumps(o) + comma)
s = '\n'.join(out)
s = s.replace('"tailSway": 14\n  },', '"tailSway": 14,\n    "mane": true,\n    "girth": 1,\n    "neckG": 1,\n    "headW": 1,\n    "headH": 1\n  },', 1)
d = json.loads(s)
# the variant, after the colours
V = {"lioness": {
  "scale": 0.8,
  "params": {"mane": False, "tuft": 0.06, "girth": 0.9, "neckG": 0.9, "headW": 0.88, "headH": 0.94},
  "colors": {"body": "#c8a468", "head": "#c6a064", "leg": "#c09b5e", "tail": "#c09b5e", "bridge": "#c09a5c",
             "cream": "#e9d8b0", "pale": "#dcc28e", "muzzle": "#e4cfa4", "ear": "#4a3220", "tuft": "#1c130c"}}}
d['variants'] = V
assert 'variants' not in d0
# write: keep the file's text, add "variants" before "mount"
vtxt = '  "variants": {\n    "lioness": ' + json.dumps(V['lioness']) + '\n  },\n'
i = s.index('  "mount"'); s = s[:i] + vtxt + s[i:]
assert json.loads(s)['variants'] == V
open(p, 'w').write(s); print('ok')
