from sealib import *
from finsheet import mfin

# RED LIONFISH (Pterois volitans), 30 cm; snout at +0.15, the caudal fin's edge at -0.152
XM, XS, XT = -0.02, -0.07, -0.095
bone = bone_by_x(XM, XS, XT)
R = fish_rig(XM, XS, XT, 1.1, 0.03, 0.15, -0.152, degs=(2, 5, 9))
# the pectoral fans: bones of their own at the root, fanning slowly (a lionfish hovers, herding its prey with them)
P0 = [0.07, -0.012, 0.021]
R.add("pectL", "body", P0, shape={"shape": "sphere", "size": {"r": 0.004}}, anim={"axis": "y", "deg": 7, "speed": 0.55, "phase": 0})
R.add("pectR", "body", mz(P0), shape={"shape": "sphere", "size": {"r": 0.004}}, anim={"axis": "y", "deg": -7, "speed": 0.55, "phase": 0})
FR = {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.04}    # (the bands: across the body)
FS = {"o": [-1, 0, 0], "u": [0, 1, 0], "v": [1, 0, 0], "r": 0.04}   # (the bands: along the spines)
# (x, top, bottom, half width): a big head, the forehead steep to the nape, deepest under the spines' start, compressed
st = [(0.151, 0.005, -0.006, 0.004), (0.14, 0.013, -0.014, 0.0095), (0.12, 0.025, -0.024, 0.0155), (0.095, 0.037, -0.032, 0.0205),
      (0.07, 0.045, -0.037, 0.0232), (0.04, 0.048, -0.039, 0.0235), (0.01, 0.046, -0.038, 0.0215), (-0.02, 0.04, -0.033, 0.0178),
      (-0.05, 0.03, -0.025, 0.0128), (-0.075, 0.018, -0.016, 0.0082), (-0.09, 0.0132, -0.0122, 0.0062), (-0.1, 0.0122, -0.0112, 0.0052)]
sh = loft(st, 18, bone, "@body", ids="trunk", pat="zebratone", frame=FR)
top = lambda x: smooth_profile(st, x)[0]
sh += [
    S("ell", id="cheek", c=[0.1, -0.006, 0], r=[0.03, 0.026, 0.0205], k=0.004, color="@body", pat="zebratone", frame=FR),
    # the big oblique mouth: the lower jaw jutting, the gape carved
    S("ell", id="jaw", c=[0.137, -0.009, 0], r=[0.019, 0.0055, 0.0095], rot=[0, 0, 22], k=0.003, kc=0.002, color="@pale"),
    S("tube", id="mouth", pts=[[0.153, -0.0015, 0.0, 0.0016], [0.147, -0.004, 0.0075, 0.0016], [0.136, -0.0085, 0.0118, 0.0014]], k=0.001, color="@dark", op="sub", mirror=True),
    S("tube", id="gill", pts=[[0.093, 0.03, 0.017, 0.0012], [0.082, 0.012, 0.0222, 0.0013], [0.079, -0.008, 0.0225, 0.0013], [0.084, -0.024, 0.0185, 0.0012]], k=0.001, color="@dark", op="sub", mirror=True),
    # the brow ridge and the SUPRAOCULAR TENTACLES -- banded, fleshy, over each eye
    S("ell", id="brow", c=[0.112, 0.022, 0.012], r=[0.012, 0.004, 0.005], k=0.003, color="@body", pat="zebratone", frame=FR, mirror=True),
    S("tube", id="tentacle", pts=[[0.113, 0.022, 0.0125, 0.0019], [0.116, 0.034, 0.014, 0.0016], [0.121, 0.047, 0.0135, 0.0013], [0.127, 0.056, 0.012, 0.0012]],
      k=0.0012, color="@pale", pat="zebratone", frame=FS, mirror=True),
    # (the little skin flap at the snout's tip)
    S("tube", id="flap", pts=[[0.146, 0.006, 0.006, 0.0014], [0.152, 0.012, 0.0085, 0.0012]], k=0.001, color="@pale", mirror=True),
]
# the DORSAL: thirteen long venomous spines standing SEPARATE, each banded, the membrane between them low and deeply
# incised (to under half their height)
xs13 = [0.086 - i * 0.0096 for i in range(13)]
hs = [0.06, 0.078, 0.09, 0.098, 0.1, 0.098, 0.092, 0.084, 0.074, 0.063, 0.052, 0.038, 0.024]
tips = []
for i, (x, h) in enumerate(zip(xs13, hs)):
    b = [x, top(x) - 0.004, 0]
    t = [x - 0.3 * h, top(x) + h, 0]
    tips.append((b, t))
    m = lerp(b, t, .5)
    sh.append(S("tube", id=f"spine{i}", bone=bone(x), pts=[b + [0.0019], [m[0] + 0.004, m[1], 0, 0.00145], t + [0.0012]], k=0.0012,
                color="@spine", pat="zebratone", frame=FS))
for i in range(12):
    (b0, t0), (b1, t1) = tips[i], tips[i + 1]
    q0 = lerp(b0, t0, .42 * hs[i] / max(hs[i], .05) if hs[i] > .05 else .5)
    q1 = lerp(b1, t1, .2)
    sh += fin([lerp(b0, t0, .08), lerp(b1, t1, .08), q1, q0], 0.0003, "@memb", bone=bone(b0[0]), id=f"web{i}_", pat="zebratone", frame=FR)
# the soft dorsal and anal (rounded, pale and banded), the anal's three spines, the rounded tail
soft = [[-0.031, top(-0.031) - 0.003, 0], [-0.034, 0.06, 0], [-0.046, 0.071, 0], [-0.062, 0.066, 0], [-0.077, 0.05, 0], [-0.087, 0.028, 0],
        [-0.086, 0.0125, 0], [-0.06, 0.023, 0]]
sh += fin(soft, 0.0003, "@soft", bone=bone, id="soft", pat="zebratone", frame=FR, smooth=2)
anal = [[-0.028, -0.031, 0], [-0.036, -0.055, 0], [-0.051, -0.066, 0], [-0.067, -0.061, 0], [-0.079, -0.043, 0], [-0.085, -0.02, 0], [-0.08, -0.012, 0], [-0.05, -0.023, 0]]
sh += fin(anal, 0.0003, "@soft", bone=bone, id="anal", pat="zebratone", frame=FR, smooth=2)
for i, (x, h) in enumerate([(-0.026, 0.02), (-0.031, 0.028), (-0.036, 0.032)]):
    sh.append(S("tube", id=f"aspine{i}", bone=bone(x), pts=[[x, -0.028, 0, 0.0017], [x - 0.006, -0.028 - h, 0, 0.0012]], k=0.001, color="@spine", pat="zebratone", frame=FS))
caud = [[-0.095, 0.0105, 0], [-0.11, 0.026, 0], [-0.13, 0.034, 0], [-0.145, 0.027, 0], [-0.152, 0.0, 0], [-0.145, -0.027, 0], [-0.13, -0.034, 0], [-0.11, -0.026, 0], [-0.095, -0.0105, 0]]
sh += fin(caud, 0.0003, "@soft", bone="tail", id="caudal", pat="zebratone", frame=FR, smooth=2)
# the long dark PELVICS, spotted pale
pelv = [[0.064, -0.033, 0.007], [0.05, -0.035, 0.009], [0.0, -0.073, 0.028], [-0.022, -0.088, 0.034], [-0.014, -0.093, 0.033], [0.032, -0.068, 0.019]]
sh += mfin(pelv, 0.0003, "@pelv", id="pelvic", mirror=True, smooth=0, rays=False)   # (2026-11-07: one sheet -- finsheet.py)
# the FAN PECTORALS: long rays standing out past a membrane slung between them (a wedge each, the ray darker and
# banded), the fan spread back and out from the flank like a wing
d0 = norm([-0.75, 0, 0.66]); d1 = [0, 1, 0]
nrm_ = norm(cross(d0, d1))
NR = 14
rays = []
for i in range(NR):
    t = i / (NR - 1)
    ph = math.radians(44 - 108 * t)
    L = 0.098 + 0.042 * math.sin(math.pi * (t * 0.85 + 0.1)) - 0.012 * t
    u = add(mul(d0, math.cos(ph)), mul(d1, math.sin(ph)))
    rays.append((u, L))
root = lambda u, s: add(P0, add(mul(u, 0.006), mul(nrm_, s)))
for i, (u, L) in enumerate(rays):
    w = norm(cross(nrm_, u))
    a = add(root(u, 0.0), mul(w, 0.0013)); b = add(root(u, 0.0), mul(w, -0.0013)); tip = add(P0, mul(u, L))
    sh.append(S("tri", id=f"ray{i}", bone="pectL", a=a, b=b, c=tip, r=0.0008, color="@ray", pat="zebratone", frame=FR, mirror=True))
for i in range(NR - 1):
    (u0, L0), (u1, L1) = rays[i], rays[i + 1]
    um = norm(add(u0, u1))
    p0 = add(P0, mul(u0, 0.72 * L0)); p1 = add(P0, mul(u1, 0.72 * L1)); pm = add(P0, mul(um, 0.6 * (L0 + L1) / 2))
    sh += fin([add(P0, mul(u0, 0.006)), p0, pm, p1, add(P0, mul(u1, 0.006))], 0.0003, "@memb", bone="pectL", id=f"pweb{i}_", pat="zebratone", frame=FR, mirror=True)

d = {
    "name": "lionfish",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a red lionfish (Pterois volitans), 30 cm -- a big head with a steep forehead, an oblique mouth with the lower jaw jutting, banded fleshy SUPRAOCULAR TENTACLES over the eyes; ZEBRA BANDS, maroon on cream (the coat pattern `zebratone`, coatpat.js 26: the zebra's stripes toned red), running on across the fins; THIRTEEN LONG VENOMOUS DORSAL SPINES standing separate (in the field, banded along their length), the membrane between them low and deeply incised; the rounded soft dorsal, anal (its three spines) and tail; the long dark pelvics; and the great FAN PECTORALS spread back and out like wings, long rays standing past a membrane slung between them (thin plates, details beside the field, on bones of their own that fan slowly). A SWIMMER (the fish's plumbing: `fly`, `alt` its depth; not put in the lake -- a reef fish). Its spine is four bones a beat apart (body, mid, stock, tail): a slow hovering beat.",
    "kind": "parts",
    "facet": False,
    "flags": {"fly": {"alt": [0.3, 1.2], "speed": [0.08, 0.25], "hz": 1.1}},
    "colors": {"body": "#f2ddd0", "pale": "#f4e6dc", "spine": "#f0d8cc", "memb": "#e6c4b6", "soft": "#ead2c6", "ray": "#c86048", "pelv": "#4a1a18", "dark": "#2a0c08"},
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "patScale": 0.12,
        "mesh": {"cell": 0.0015, "tris": [4400, 1500]},
        "shade": {"back": 0.92, "belly": 1.06, "k": 0.02, "at": 0, "mode": "mix", "tol": 0.25},
        "shape": sh,
        "eyes": {"at": [0.112, 0.011, 0.0165], "from": [0.104, 0.01, 0], "r": 0.0068, "color": "#140606", "iris": "#a83a22", "pupil": "round", "lid": "@body", "sink": 0.35, "bone": "body"},
    },
}
write("lionfish", d)
