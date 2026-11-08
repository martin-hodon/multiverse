# the horse's coats rewritten whole (every colour key a coat touches), a blaze, socks below stockings, coat patterns gated by params
import json, re, math, sys
p = '/home/martin/store/apps/multiverse/assets/creatures/mammals/horse.json'
s = open(p).read()
W = "#ece6da"   # white hair
def coat(name, params=None, **c):
    o = {"name": name}
    if params: o["params"] = params
    o.update(c); return o
def full(body, back, flank, muzzle, ear, sock, mane, tail=None, leg=None, **more):
    return dict(body=body, back=back, flank=flank, muzzle=muzzle, ear=ear, leg=leg or sock, sock=sock, mane=mane, tail=tail or mane, **more)
CH = full("#9c4f26", "#8a4220", "#b0602e", "#7e4428", "#8a4522", "#8a4522", "#7a3a1c")
coats = [
  coat("bay"),
  coat("chestnut", **CH),
  coat("black", **full("#2a2420", "#211c19", "#332b26", "#2a2420", "#221c18", "#1c1714", "#121010")),
  coat("grey", **full("#b9b5ad", "#aaa69e", "#c6c2ba", "#6a6560", "#a39f98", "#7a766f", "#dedad2", "#d4d0c8", leg="#8f8b84")),
  coat("dun", **full("#b09670", "#6e5236", "#bca480", "#4a3a2c", "#3a2a1c", "#2a201a", "#2a201a")),
  coat("chestnut, blaze and white stockings", {"blaze": True}, **{**CH, "muzzle": "#d6cabd", "sock": W, "blaze": W}),
  coat("bay, white socks", pastern=W),
  coat("dark bay", **full("#4e3020", "#3e2618", "#5c3a26", "#3a2a20", "#3a2618", "#161210", "#161210")),
  coat("dapple grey", {"dapple": True}, **full("#a4a29c", "#94928c", "#b2b0aa", "#57534e", "#8e8c86", "#55524d", "#dcdad4", "#d2d0ca", leg="#7a7872")),
  coat("palomino", **full("#d0a458", "#c0944c", "#dab066", "#a8845a", "#c09450", "#c09450", "#efe6cc", "#e6dbbf")),
  coat("buckskin", **full("#c8a46a", "#b8945c", "#d2b07a", "#4a3a2a", "#3a2a1c", "#1e1814", "#1a1410")),
  coat("flaxen chestnut", **full("#a4582a", "#924c24", "#b46a34", "#7e4428", "#924c24", "#924c24", "#e2cc98", "#dcc28c")),
  coat("piebald", {"pinto": True}, **full("#ece6da", "#e4ded2", "#f0eae0", "#cfc4ba", "#2a2420", W, "#2a2420", "#d8d2c6"), pastern=W),
  coat("appaloosa", {"spotted": True}, **full("#e6e0d4", "#dcd6ca", "#ece6dc", "#8a7f78", "#7a706a", "#d6d0c4", "#4a3e36", "#6a5e56")),
]
lines = ",\n".join("    " + json.dumps(c) for c in coats)
i = s.index('  "coats": ['); j = s.index('  ],\n', i) + 5
s = s[:i] + '  "coats": [\n' + lines + '\n  ],\n' + s[j:]
note = ("COATS (species.js coatDef, picked by the seed; creatures.js dressed): each a colour table over the horse's own, written out whole "
        "(the body, its darker back and paler flank, the muzzle, ears, legs, mane and tail) -- bay (its own), chestnut, black, grey, dun (the dark "
        "dorsal stripe: its `back`), chestnut with a blaze and white stockings, bay with white socks, dark bay, dapple grey, palomino, buckskin, "
        "flaxen chestnut, piebald, appaloosa. THE LEGS: `sock` is the leg from the knee down (a bay's black points; white: stockings), `pastern` "
        "the fetlock and pastern alone (white socks), each falling back to the one above. THE PARAMS a coat may set: `blaze` (a white stripe "
        "down the face, in `blaze`), `pinto` (black patches over a white coat), `spotted` (an appaloosa's leopard spots), `dapple` (a dapple "
        "grey's mottle) -- the patterns are the body's shapes' `pat`, gated on them")
s = re.sub(r'  "_coats": "[^"\n]*",\n', lambda m: '  "_coats": ' + json.dumps(note) + ',\n', s, count=1)
s = s.replace('  "params": {\n    "s": 1,\n    "mane": false\n  },',
              '  "params": {\n    "s": 1,\n    "mane": false,\n    "blaze": false,\n    "pinto": false,\n    "spotted": false,\n    "dapple": false\n  },', 1)
assert '"dapple": false' in s
# the coat patterns on the body's shapes (trunk, neck, head, upper legs)
PAT = [{"when": "pinto", "v": "piebald"}, {"when": "spotted", "v": "dots"}, {"when": "dapple", "v": "mottle"}]
n = 0
def addpat(m):
    global n
    line = m.group(0)
    d = json.loads(line.strip().rstrip(','))
    if d.get("color") in ("@body", "@back", "@flank") and "pat" not in d:
        n += 1
        return line.replace('"color": "%s"}' % d["color"], '"color": "%s", "pat": %s}' % (d["color"], json.dumps(PAT)))
    return line
s = re.sub(r'^      \{"id": .*\},?$', addpat, s, flags=re.M)
print("patterned shapes", n)
# socks below the stockings
for sid in ("fetlock", "pastern", "hfetlock", "hpastern"):
    a = '{"id": "%s",' % sid
    k = s.index(a); e = s.index('\n', k)
    ln = s[k:e]; assert '["@sock", "@leg"]' in ln, ln
    s = s[:k] + ln.replace('["@sock", "@leg"]', '["@pastern", "@sock", "@leg"]') + s[e:]
# the blaze: a thin plate down the front of the face cone, raised a hair off it
A, B = (1.4887, 1.9628), (1.6722, 1.707)
L = math.hypot(B[0] - A[0], B[1] - A[1]); u = ((B[0] - A[0]) / L, (B[1] - A[1]) / L); nrm = (-u[1], u[0])
if nrm[1] < 0: nrm = (-nrm[0], -nrm[1])
t = float(sys.argv[1]) if len(sys.argv) > 1 else .45
r_t = .0907 + (.0665 - .0907) * t
off = r_t - .009
c = (A[0] + u[0] * L * t + nrm[0] * off, A[1] + u[1] * L * t + nrm[1] * off)
ang = math.degrees(math.atan2(u[1], u[0])) - math.degrees(math.atan((.0907 - .0665) / L))
blaze = {"id": "blaze", "when": "blaze", "type": "ell", "bone": "head", "c": [round(c[0], 4), round(c[1], 4), 0.0], "r": [0.135, 0.012, 0.024],
         "rot": [0, 0, round(ang, 2)], "k": 0.008, "kc": 0.004, "color": ["@blaze", "@body"]}
if '"id": "blaze"' not in s:
    a = s.index('{"id": "muzzle",'); a = s.rindex('\n', 0, a) + 1
    s = s[:a] + '      ' + json.dumps(blaze) + ',\n' + s[a:]
json.loads(s)
open(p, 'w').write(s)
print(json.dumps(blaze))
