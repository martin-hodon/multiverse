# hydra heads: real eyes (sculpt eyes list), round ridged curved horns, recessed mouth groove
import json, math, re, sys
F = sys.argv[1]; L = open(F).read().split("\n")
def V(a,b,f=1): return [x+f*y for x,y in zip(a,b)]
def S(a,f): return [x*f for x in a]
def N(a): l=math.sqrt(sum(x*x for x in a)); return [x/l for x in a]
def D(a,b): return sum(x*y for x,y in zip(a,b))
def R4(a): return [round(x,4) for x in a]
shapes = {}; idx = {}
for i,l in enumerate(L):
    m = re.match(r'\s*(\{"id": "(neck[ABC][A-Za-z0-9]+)".*\}),?$', l)
    if m: shapes[m.group(2)] = json.loads(m.group(1)); idx[m.group(2)] = i
eyes = []; out = {}
for X in "ABC":
    cran = shapes[f"neck{X}Cran"]["c"]
    for s in "LR":
        e = shapes[f"neck{X}Eye{s}"]; c = e["c"]; o = N(V(c, cran, -1))
        eyes.append({"at": R4(V(c, o, e["r"] * .6)), "from": R4(cran), "bone": f"neck{X}Tuft", "r": round(e["r"] * .8, 4),
                     "iris": "#e39a1e", "pupil": "slit", "color": "#3a2408", "mirror": False})
        out[f"neck{X}Eye{s}"] = None; out[f"neck{X}Pupil{s}"] = None
        # mouth: a groove carved along the lip, not a rod laid on it
        m = dict(shapes[f"neck{X}Mouth{s}"]); m["pts"] = [p[:3] + [0.021] for p in m["pts"]]
        m.update({"op": "sub", "k": 0.006, "kc": 0.004}); out[f"neck{X}Mouth{s}"] = [m]
        # horns: a curved tube, round and tapering, growth rings painted on, a crisp dark tip
        for h, bow, lift in ((f"neck{X}Horn{s}", .10, .07), (f"neck{X}Horn2{s}", .06, .03)):
            q = shapes[h]; a, b, ra = q["a"], q["b"], q["ra"]; d = V(b, a, -1); Ln = math.sqrt(D(d, d)); u = N(d)
            up = N(V([0, 1, 0], u, -u[1]))
            P = lambda t: V(V(a, d, t), up, Ln * (-bow * math.sin(math.pi * t) + lift * t * t))
            ts = [0, .22, .45, .65, .8]; rs = [ra, ra * .84, ra * .64, ra * .46, ra * .34]
            tube = {"id": h, "type": "tube", "bone": q["bone"], "pts": [R4(P(t)) + [round(r, 4)] for t, r in zip(ts, rs)], "k": 0.02, "kc": 0.006,
                    "color": "@horn", "pat": "ridges", "frame": {"o": R4(a), "u": R4(u), "r": 0.028}}
            tip = {"id": h + "Tip", "type": "cone", "bone": q["bone"], "a": R4(P(.78)), "b": R4(P(1.0)), "ra": round(min(ra * .34, .02), 4), "rb": 0.004,
                   "k": 0.004, "kc": 0.01, "color": "@hornTip", "pat": "ridges", "frame": {"o": R4(a), "u": R4(u), "r": 0.028}}
            out[h] = [tube, tip]
res = []
for i, l in enumerate(L):
    m = re.match(r'\s*\{"id": "(neck[ABC][A-Za-z0-9]+)"', l)
    if m and m.group(1) in out:
        for q in out[m.group(1)] or []: res.append("      " + json.dumps(q) + ",")
        continue
    if l.startswith('    "mesh": {"cell"'):
        res.append(l); res.append('    "eyes": ' + json.dumps(eyes) + ","); continue
    res.append(l)
t = "\n".join(res).replace('"horn": "#8e7c58",', '"horn": "#8e7c58", "hornTip": "#3e3222",')
json.loads(t); open(F, "w").write(t)
print(len(eyes), "eyes;", sum(1 for v in out.values() if v is None), "removed")
