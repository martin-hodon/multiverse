import json,sys
coats=json.load(open(sys.argv[1]))
order=['name','params','body','head','front','belly','muzzle','ear','leg','foot','tail','ring','eye','nose']
p='assets/creatures/mammals/cat.json'; s=open(p).read()
lines=',\n'.join('    '+json.dumps({k:c[k] for k in order if k in c}) for c in coats)
anchor='    "ring": "#6e3a16"\n  },\n'
assert s.count(anchor)==1
note = "COATS (species.js makeCat, picked by seed; creatures.js dressed): each written out whole over the colours above -- ginger, black, white, grey, tuxedo (white face and socks), cream, brown, calico (patches) -- the plain ones with { \"tabby\": false }, which takes the tabby stripes off (the sculpt's `pat`, gated on that param). Until 2026-11-06 these were mammals.js CAT_COATS"
s=s.replace(anchor, anchor+'  "coats": [\n'+lines+'\n  ],\n  "_coats": '+json.dumps(note)+',\n')
a='"tailSway": 20\n  },'
assert s.count(a)==1
s=s.replace(a,'"tailSway": 20,\n    "tabby": true\n  },')
print('tabby pats',s.count('"pat": "tabby"'))
s=s.replace('"pat": "tabby"','"pat": {"when": "tabby", "v": "tabby"}')
old="Its colours are the coat's keys (species.js makeCat builds every coat of mammals.js CAT_COATS from this file)"
print('about', s.count(old))
s=s.replace(old,"Its colours are the coat's keys (its `coats`: species.js makeCat builds each from this file)")
json.loads(s)
open(p,'w').write(s)
