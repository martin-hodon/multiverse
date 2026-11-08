import sys; sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import *
PI = math.pi
def sub(a, b): return [a[i] - b[i] for i in range(3)]
BODY = [0, .08, 0]
def seg(a, b, r):
    return {"a": [0, 0, 0], "c": lerp([0, 0, 0], sub(b, a), .5), "b": sub(b, a), "r1": r, "r2": r * .8}
NECK, HEAD, TAIL = [.11, .06, 0], [.17, .072, 0], [-.115, .04, 0]
parts = [
    {"id": "body", "parent": None, "shape": "sphere", "size": {"r": .12}, "scale": [1.15, .5, .9], "pos": BODY, "color": "@shell"},
    {"id": "neck", "parent": "body", "shape": "tube", "size": seg(NECK, HEAD, .022), "pos": sub(NECK, BODY), "color": "@skin",
     "anim": {"axis": "y", "deg": 8, "speed": .3, "phase": 1}},
    {"id": "head", "parent": "neck", "shape": "sphere", "size": {"r": .026}, "scale": [1.3, .9, .9], "pos": sub(HEAD, NECK), "color": "@skin",
     "anim": {"axis": "y", "deg": 14, "speed": .3, "phase": 0}},
    {"id": "tail", "parent": "body", "shape": "tube", "size": seg(TAIL, [-.168, .028, 0], .014), "pos": sub(TAIL, BODY), "color": "@skin",
     "anim": {"axis": "y", "deg": 10, "speed": .4, "phase": 0}},
]
LEGS = {"F": ([.07, .04, .068], [.1, .006, .129]), "H": ([-.07, .038, .068], [-.1, .006, .128])}   # (the feet clear of the plastron's cut, z > .105)
for S, sz in (("L", 1), ("R", -1)):
    z = lambda v: [v[0], v[1], v[2] * sz]
    for fh, (a, b) in LEGS.items():
        ph = (0 if fh == "F" else PI) + (0 if S == "L" else PI)
        parts.append({"id": f"leg{fh}{S}", "parent": "body", "shape": "tube", "size": seg(z(a), z(b), .02), "pos": z(sub(a, BODY)), "color": "@skin",
                      "anim": {"axis": "z", "deg": 24, "speed": .8, "phase": round(ph % (2 * PI), 4)}})

sh = []
def S(id, **k):
    d = {"id": id}; d.update(k); sh.append(d); return d
# ---- the carapace: a dome (35 % of its length high) springing from its rim at y .034, its underside CARVED flat at
# y .022 -- the plastron (the carving's own colour) with 2 cm under it to the ground; the scutes drawn by their SEAMS --
# dark grooves laid on the dome point by point (so they follow it exactly: no tiles, no corners), each scute a shallow
# swell between them with its yellow streak; the marginals a scalloped band round the rim, the rear ones flared
DC, DR = [0, .034, 0], [.138, .095, .105]
def onDome(x, z, out=0.0):
    t = 1 - (x / DR[0]) ** 2 - (z / DR[2]) ** 2
    y = DC[1] + DR[1] * math.sqrt(max(t, 0))
    n = [x / DR[0] ** 2, (y - DC[1]) / DR[1] ** 2, z / DR[2] ** 2]; l = math.sqrt(sum(v * v for v in n)); n = [v / l for v in n]
    return add([x, y, z], n, out), n
def atLat(s, a, out=0.0):   # the dome at height fraction s, angle a (degrees from the front) round it
    q = math.sqrt(max(0, 1 - s * s)); x, z = DR[0] * q * math.cos(math.radians(a)), DR[2] * q * math.sin(math.radians(a))
    p = [x, DC[1] + DR[1] * s, z]; n = [x / DR[0] ** 2, (p[1] - DC[1]) / DR[1] ** 2, z / DR[2] ** 2]; l = math.sqrt(sum(v * v for v in n))
    return add(p, [v / l for v in n], out), [v / l for v in n]
def tilt(n):
    h = math.sqrt(n[1] ** 2 + n[2] ** 2)
    return [math.degrees(math.atan2(n[2], n[1])), 0, -math.degrees(math.atan2(n[0], h))]
S("dome", type="ell", c=DC, r=DR, k=.004, color="@shell")
SR, SW = .0028, -.0018      # a seam: its radius, and its axis this far under the dome (so it stands .001 proud, painted)
def seam(pid, xz, mirror=True, dense=3):
    pts = []
    for i in range(len(xz) - 1):
        for j in range(dense):
            t = j / dense; x = xz[i][0] + (xz[i + 1][0] - xz[i][0]) * t; z = xz[i][1] + (xz[i + 1][1] - xz[i][1]) * t
            pts.append(onDome(x, z, SW)[0] + [SR])
    pts.append(onDome(*xz[-1], SW)[0] + [SR])
    S(pid, type="tube", pts=pts, k=.001, kc=.0012, color="@seam", **({"mirror": True} if mirror else {}))
RING = .32                  # the marginals' inner seam: a ring round the dome at this height fraction
ringXZ = lambda a: (DR[0] * math.sqrt(1 - RING ** 2) * math.cos(math.radians(a)), DR[2] * math.sqrt(1 - RING ** 2) * math.sin(math.radians(a)))
S("ring", type="tube", pts=[atLat(RING, a, SW)[0] + [SR] for a in range(0, 181, 6)], k=.001, kc=.0012, color="@seam", mirror=True)
E = [.078, .026, -.026, -.078]                   # the vertebrals' transverse seams
for i, e in enumerate(E):
    seam(f"vx{i}", [(e, -.023), (e, 0), (e, .023)], mirror=False, dense=2)
x0 = ringXZ(14)                                   # the vertebrals' sides: narrow at the transverse seams, wide between
seam("vside", [x0, (.104, .033), (.078, .023), (.052, .035), (.026, .023), (0, .035), (-.026, .023), (-.052, .035), (-.078, .023), (-.104, .033), (x0[0] * -1, x0[1])], dense=3)
for i, (xs, a) in enumerate([(.052, 68), (0, 92), (-.052, 116)]):   # the costals' seams: from the vertebrals' corners out to the ring
    rx, rz = ringXZ(a); seam(f"cs{i}", [(xs, .035), ((xs + rx) / 2 + .002, (.035 + rz) / 2), (rx, rz)], dense=3)
MA = [7, 21, 35, 49, 63, 77, 91, 105, 119, 133, 147, 161, 174]       # the marginals' seams round the rim
for i, a in enumerate(MA):
    S(f"ms{i}", type="tube", pts=[atLat(s, a, SW)[0] + [SR] for s in (RING, .2, .1, .02)], k=.001, kc=.0012, color="@seam", mirror=True)
for i in range(len(MA)):                          # ... and each marginal a little swell at the rim between its seams: scallops
    a0 = MA[i - 1] if i else -7; a1 = MA[i]; am = (a0 + a1) / 2 if i else 0
    flare = max(0, (am - 120) / 60)
    c, n = atLat(.04 - .1 * flare, am, -.0035 + .004 * flare)
    S(f"marg{i}", type="ell", c=c, r=[.0075, .009 + .003 * flare, .016], rot=[0, -am, 0], k=.002, kc=.001, color="@shell", **({"mirror": True} if i else {}))
am = 180; c, n = atLat(-.06, am, .0005)
S("margB", type="ell", c=c, r=[.0075, .012, .02], rot=[0, -am, 0], k=.002, kc=.001, color="@shell")
# the scutes' swells and streaks: vertebrals down the middle, costals either side
plates = [(f"vert{i}", x, 0, .022, .022) for i, x in enumerate([.104, .052, 0, -.052, -.104])]
plates += [(f"cost{i}", x, z, .02, .02) for i, (x, z) in enumerate([(.078, .066), (.027, .072), (-.026, .072), (-.08, .065)])]
for pid, x, z, rx, rz in plates:
    c, n = onDome(x, z, -.0028)
    S(pid, type="ell", c=c, r=[rx, .004, rz], rot=tilt(n), k=.003, kc=.002, color="@shell2", **({"mirror": True} if z else {}))
    c2, n2 = onDome(x + .004, z, -.0006)
    S(pid + "s", type="ell", c=c2, r=[rx * .5, .0016, rz * .2], rot=tilt(n2), k=.001, kc=.0014, color="@streak", **({"mirror": True} if z else {}))
for i, a in enumerate([28, 56, 84, 112, 140, 166]):          # the marginals' own streaks
    c, n = atLat(.14, a, -.0006)
    S(f"mst{i}", type="ell", c=c, r=[.0016, .006, .006], rot=[0, -a, 0], k=.001, kc=.0012, color="@streak", mirror=True)
# the underside: carved flat (the plastron), the carving painted the plastron's colour
S("plastron", type="box", c=[0, -.03, 0], r=[.16, .052, .105], round=.005, op="sub", k=.003, color="@plastron")
S("plastronRim", type="ell", c=[0, .0255, 0], r=[.1415, .0045, .1075], k=.0015, kc=.001, color="@plastron")
for i, a in enumerate([140, 152, 164, 176]):
    t = math.radians(a); o = [DC[0] + DR[0] * .99 * math.cos(t), .03, DR[2] * .99 * math.sin(t)]; dd = [math.cos(t), -.25, math.sin(t)]
    S(f"serr{i}", type="cone", a=o, b=add(o, dd, .011), ra=.0055, rb=.0012, k=.0015, kc=.001, color="@shell", **({"mirror": True} if a < 176 else {}))
# ---- head and neck: green skin with yellow stripes, the red patch behind the eye, a hooked beak
S("neck", type="tube", bone="neck", pts=[[.09, .06, 0, .024], [.13, .064, 0, .021], [.165, .07, 0, .02]], k=.006, color="@skin")
S("head", type="ell", bone="head", c=[.18, .075, 0], r=[.028, .02, .019], k=.006, color="@skin")
S("snout", type="ell", bone="head", c=[.205, .0715, 0], r=[.015, .0105, .0085], k=.006, color="@skin")   # (pointed, not a bulb)
S("beak", type="ell", bone="head", c=[.209, .066, 0], r=[.011, .0055, .0085], k=.003, kc=.0012, color="@beak")
S("hook", type="cone", bone="head", a=[.214, .0705, 0], b=[.2215, .0625, 0], ra=.0048, rb=.0018, k=.002, kc=.001, color="@beak")   # (the upper tomium's hook over the lower jaw)
S("jaw", type="ell", bone="head", c=[.183, .063, 0], r=[.024, .009, .016], k=.005, color="@skin")
S("mouth", type="tube", bone="head", pts=[[.2155, .0672, 0, .0022], [.204, .067, .0106, .0022], [.19, .0675, .0159, .0021], [.176, .069, .0183, .0019]], k=.0008, kc=.0006, color="@beak", mirror=True)
S("ear", type="ell", bone="head", c=[.168, .0775, .0178], r=[.013, .0042, .0022], rot=[0, -12, -6], k=.0012, kc=.0005, color="@red", mirror=True)
for j, (dy, rr) in enumerate([(.004, .0026), (-.006, .0024)]):
    S(f"stripe{j}", type="tube", bone="neck", pts=[[.192, .08 + dy * .5, .0155, rr], [.175, .078 + dy, .0185, rr], [.15, .07 + dy, .019, rr], [.12, .066 + dy, .0195, rr], [.1, .063 + dy, .021, rr * .9]],
      k=.0015, kc=.0007, color="@yellow", mirror=True)
S("throatStripe", type="tube", bone="head", pts=[[.195, .0566, .0065, .0022], [.18, .0542, .007, .0022], [.165, .0514, .0075, .0022], [.152, .049, .008, .002]], k=.0012, kc=.0006, color="@yellow", mirror=True)
S("chinStripe", type="tube", bone="head", pts=[[.198, .062, .006, .0024], [.18, .058, .011, .0024], [.16, .058, .012, .0022]], k=.0012, kc=.0006, color="@yellow", mirror=True)
S("tail", type="cone", bone="tail", a=[-.11, .04, 0], b=[-.168, .028, 0], ra=.014, rb=.003, k=.005, color="@skin")
# ---- legs: short and thick, the upper bone out sideways under the rim and the forearm down (sprawled), scaled, the
# fore with five claws on a flattened hand, the hind on a broad webbed foot
EL = {"F": [.092, .036, .116], "H": [-.095, .034, .112]}
for fh, (a, b) in LEGS.items():
    bone = f"leg{fh}L"; e = EL[fh]
    r0, r1, r2 = (.0145, .0128, .0115) if fh == "F" else (.02, .017, .015)
    S(f"leg{fh}", type="tube", bone=bone, pts=[a + [r0], e + [r1], [b[0], .016, b[2], r2]], k=.006, color="@skin", pat="scales", mirror=True)
    S(f"foot{fh}", type="ell", bone=bone, c=[b[0] + .008, .008, b[2] + .003], r=[.0187, .0065, .0162] if fh == "F" else [.024, .007, .021], k=.005, color="@skin", pat="scales", mirror=True)
    for i in range(5 if fh == "F" else 4):
        ang = math.radians(-50 + i * (25 if fh == "F" else 30))
        o = [b[0] + .01, .006, b[2] + .003]; dd = [math.cos(ang), -.2, math.sin(ang)]
        S(f"claw{fh}{i}", type="cone", bone=bone, a=add(o, dd, .012), b=add(o, dd, .027), ra=.0036, rb=.0015, k=.0008, kc=.0004, color="@claw", mirror=True)
sh = [p for p in sh if p]

d = {
    "name": "turtle",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a red-eared slider 27 cm long -- a domed carapace (height ~ a third of its length) of raised scutes, five vertebrals and four costals a side, each with a yellow streak, the dark seams showing between them, a rim of marginals flaring a little at the back; the flat pale plastron and bridge under it; a green head with yellow stripes running down the neck and the red patch behind the eye, a hooked beak; scaly fore legs with five claws, columnar hind legs on flat feet, a short pointed tail",
    "kind": "parts",
    "flags": {"shy": 2.5, "shore": True, "print": "paw", "legLen": .19},   # (legLen: gaitBase -- see scorpion.py)
    "colors": {"shell": "#46482a", "seam": "#1e1c0e", "streak": "#b8a448", "shell2": "#525632", "plastron": "#d8c784", "skin": "#55603a", "chin": "#9aa65a",
               "yellow": "#d6c85a", "red": "#d8342a", "beak": "#2e3420", "claw": "#2a2618", "eye": "#c8b24a"},
    "parts": parts,
    "sculpt": {
        "keep": [],
        "mesh": {"cell": .0032, "tris": [7000, 2200]},
        "shape": sh,
        "eyes": {"at": [.191, .081, .015], "from": [.18, .078, 0], "r": .0052, "iris": "@eye", "pupil": "round", "lid": "@skin", "sink": .3},
    },
}
dump("others/turtle.json", d)
print(len(sh), "shapes")
