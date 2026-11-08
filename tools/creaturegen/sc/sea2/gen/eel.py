from sealib import *

# EUROPEAN EEL (Anguilla anguilla), a yellow eel 80 cm long; snout at +0.4, the tail's tip at -0.4
HZ = 1.0
J = [0.25, 0.17, 0.09, 0.01, -0.07, -0.15, -0.23, -0.31]      # (the spine's joints: eight bones behind the head)
XT = -0.4
R = Rig()
R.add("body", None, [0, 0, 0], shape=tube_part([0.4, 0, 0], [J[0], 0, 0], 0.016, 0.016))
par, px = "body", 0.0
for j, x in enumerate(J):
    nx = J[j + 1] if j + 1 < len(J) else XT
    R.add(f"seg{j + 1}", par, [x - px, 0, 0], shape=tube_part([0, 0, 0], [nx - x, 0, 0], 0.015 - 0.0013 * j),
          anim={"axis": "y", "deg": 4 if j == 0 else 7 + 0.5 * j, "speed": HZ, "phase": -0.65 * j})
    par, px = f"seg{j + 1}", x
def bone(x):
    if x >= J[0]: return "body"
    for j in range(len(J) - 1):
        if x >= J[j + 1]: return f"seg{j + 1}"
    return f"seg{len(J)}"
# (x, top, bottom, half width): round in front, the head small and pointed, compressed toward the tail
st = [(0.401, 0.0035, -0.0045, 0.0038), (0.39, 0.007, -0.0075, 0.0072), (0.37, 0.011, -0.0112, 0.0108), (0.34, 0.0142, -0.0142, 0.0136),
      (0.3, 0.0158, -0.0162, 0.0148), (0.2, 0.0182, -0.0185, 0.0158), (0.1, 0.0192, -0.0195, 0.0158), (0.0, 0.0185, -0.0188, 0.0142),
      (-0.1, 0.0165, -0.0166, 0.0116), (-0.2, 0.0138, -0.0138, 0.0086), (-0.3, 0.0102, -0.0102, 0.0058), (-0.36, 0.0072, -0.0072, 0.0039),
      (-0.395, 0.0042, -0.0042, 0.0025)]
sh = loft(st, 44, bone, "@body", ids="trunk", over=2.2)
top = lambda x: smooth_profile(st, x)[0]
bot = lambda x: smooth_profile(st, x)[1]
sh += [
    # the small pointed head: the lower jaw a little longer, the gape to under the eye, the tubular nostrils, the
    # small gill opening just before the pectoral
    S("ell", id="jaw", c=[0.382, -0.0065, 0], r=[0.02, 0.0035, 0.0078], k=0.002, kc=0.0015, color="@pale"),
    S("tube", id="mouth", pts=[[0.403, -0.0028, 0.0, 0.001], [0.395, -0.0038, 0.0048, 0.0011], [0.381, -0.0052, 0.0078, 0.001]], k=0.0008, color="@dark", op="sub", mirror=True),
    S("tube", id="nostril", pts=[[0.394, 0.0032, 0.0028, 0.0017], [0.4, 0.0046, 0.0036, 0.0016]], k=0.0006, color="@body", mirror=True),
    S("ell", id="gillslit", c=[0.312, -0.0045, 0.0148], r=[0.0016, 0.0042, 0.002], k=0.0008, color="@dark", op="sub", mirror=True),
]
# THE ONE CONTINUOUS FIN: the dorsal rising far back (a third along), running round the tail's tip into the anal (which
# starts a little behind the dorsal) -- a low plate on each spine bone, each overlapping the next a little
XD, XA = 0.13, 0.05
hd = lambda x: 0.0125 * min(1, (XD - x) / 0.09) ** 0.7 if x < XD else 0
ha = lambda x: 0.0105 * min(1, (XA - x) / 0.07) ** 0.7 if x < XA else 0
edges = [J[0]] + J[1:] + [XT]
for j in range(len(J)):
    xa, xb = J[j], (J[j + 1] if j + 1 < len(J) else XT)
    b = f"seg{j + 1}"
    if xb == XT:   # (the last bone: the fin round the tip)
        xs = [xa + 0.004] + [xa + (XT + 0.01 - xa) * t for t in (0.33, 0.66, 1.0)]
        up = [[x, top(x) + hd(x), 0] for x in xs] + [[XT - 0.012, 0.007, 0], [XT - 0.018, 0.0, 0], [XT - 0.012, -0.007, 0]]
        dn = [[x, bot(x) - ha(x), 0] for x in reversed(xs)]
        base = [[XT + 0.012, 0.0, 0], [xa + 0.004, bot(xa) + 0.0015, 0]]
        sh += fin([[xa + 0.004, top(xa) - 0.0015, 0]] + up + dn + base, 0.0006, "@fin", bone=b, id=f"fin{j}_")
        continue
    xs = [xa + 0.004, (xa + xb) / 2, xb - 0.004]
    for nm, h, X0, edge_y, base_y, col in (("dors", hd, XD, lambda x: top(x) + hd(x), lambda x: top(x) - 0.0015, "@fin"),
                                            ("anal", ha, XA, lambda x: bot(x) - ha(x), lambda x: bot(x) + 0.0015, "@fin2")):
        if xs[-1] >= X0: continue
        xq = [x for x in xs if x < X0]
        if xs[0] >= X0: xq = [X0] + xq
        sh += fin([[x, base_y(x), 0] for x in xq] + [[x, edge_y(x) + (0.0004 if nm == "dors" else -0.0004) * (h(x) == 0), 0] for x in reversed(xq)],
                  0.0006, col, bone=b, id=f"{nm}{j}_")
# the small rounded pectorals, just behind the gill opening
pect = [[0.31, -0.002, 0.0145], [0.309, -0.008, 0.0145], [0.298, -0.011, 0.019], [0.288, -0.008, 0.021], [0.287, -0.002, 0.02], [0.296, 0.001, 0.0175]]
sh += fin(pect, 0.0005, "@fin2", id="pectoral", mirror=True)

d = {
    "name": "eel",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a European eel, a yellow eel 80 cm long -- long and serpentine, round in front and compressed toward the tail; a small pointed head, the lower jaw a little longer, the gape to under the small eye, tubular nostrils, the small gill opening just before the little rounded pectorals; ONE CONTINUOUS FIN, the dorsal rising far back (a third along) and running round the tail's tip into the anal, which starts a little behind it (low plates, details beside the field, on the spine's bones); dark olive-brown above, yellowish below (`shade`). A SWIMMER (the fish's plumbing: `fly`, `alt` its depth; not put in the lake). Its spine is NINE bones (the head and seg1-8), each beating a beat behind the one before: the anguilliform wave runs down the whole body, about one wavelength long.",
    "kind": "parts",
    "facet": False,
    "flags": {"fly": {"alt": [0.15, 0.9], "speed": [0.25, 0.7], "hz": HZ}},
    "colors": {"body": "#5e5a2c", "pale": "#d0bf6a", "fin": "#4e4a26", "fin2": "#8a8040", "dark": "#141208"},
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mesh": {"cell": 0.002, "tris": [3600, 1200]},
        "shade": {"back": "#36361c", "belly": "#cfc070", "k": 0.006, "at": -0.004, "mode": "mix", "tol": 0.3},
        "shape": sh,
        "eyes": {"at": [0.376, 0.0068, 0.0092], "from": [0.37, 0.004, 0], "r": 0.0027, "color": "#0a0804", "iris": "#b8a050", "pupil": "round", "lid": "@body", "sink": 0.35, "bone": "body"},
    },
}
write("eel", d)
