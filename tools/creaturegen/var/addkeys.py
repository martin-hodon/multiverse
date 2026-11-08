#!/usr/bin/env python3
# addkeys.py FILE KEYS.json : insert top-level keys (coats, _coats, variants, _variants) into a creature JSON as text,
# before its "print" (or "sculpt") line -- one coat per line, the rest of the file untouched. Replaces a key already there.
import json, sys, re
fn, keys = sys.argv[1], json.load(open(sys.argv[2]))
s = open(fn).read()
d = json.loads(s)
lines = s.split('\n')
# drop existing top-level keys being replaced (they must be on lines starting with two spaces + "key")
for k in keys:
    if k in d:
        i = next(i for i, l in enumerate(lines) if l.startswith('  "%s":' % k))
        j = i
        depth = 0
        while True:
            l = lines[j]; depth += l.count('[') + l.count('{') - l.count(']') - l.count('}')
            if depth <= 0: break
            j += 1
        del lines[i:j + 1]
at = next((i for i, l in enumerate(lines) if l.startswith('  "print":')), None)
if at is None: at = next(i for i, l in enumerate(lines) if l.startswith('  "sculpt":'))
out = []
for k, v in keys.items():
    if isinstance(v, list):
        out.append('  "%s": [' % k)
        out += ['    ' + json.dumps(x, ensure_ascii=False) + (',' if n < len(v) - 1 else '') for n, x in enumerate(v)]
        out.append('  ],')
    elif isinstance(v, dict):
        out.append('  "%s": {' % k)
        it = list(v.items())
        out += ['    ' + json.dumps(a) + ': ' + json.dumps(b, ensure_ascii=False) + (',' if n < len(it) - 1 else '') for n, (a, b) in enumerate(it)]
        out.append('  },')
    else:
        out.append('  "%s": %s,' % (k, json.dumps(v, ensure_ascii=False)))
lines[at:at] = out
s2 = '\n'.join(lines)
d2 = json.loads(s2)
for k in keys: assert d2[k] == keys[k]
for k in d:
    if k not in keys: assert d2[k] == d[k], k
open(fn, 'w').write(s2)
print('ok', fn, list(keys))
