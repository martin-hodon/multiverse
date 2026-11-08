from cetlib import *
import os

# PLESIOSAURUS (P. dolichodeirus, the Lower Jurassic of Lyme Regis), 3.3 m: a small head on a neck about as long as
# the trunk, the trunk a deep broad barrel, four big wing-like flippers (the hind a little smaller), a
# short tapering tail. Rest frame: x forward, y up, z left, metres; the snout's tip at x = +1.72, the tail's at -1.58.
HZ = 0.45                               # (a flipper stroke every ~2 s: underwater flight)
XH = 1.46                               # (the skull's back: the head joint)
NECK = [0.18, 0.5, 0.82, 1.14]          # (the neck's joints)
YN = lambda x: 0.22 * max(0.0, (x - 0.05) / (XH - 0.05)) ** 1.5   # (the neck's gentle upward curve at rest)
YH = YN(XH)
R = Rig()
R.add("body", None, [0, 0, 0], shape=tube_part([0.1, 0, 0], [-0.9, 0, 0], 0.3, 0.22), color="@body",
      anim={"axis": "z", "deg": 1.2, "speed": HZ, "phase": 1.2})
par, x0, y0 = "body", 0.0, 0.0
for j, x in enumerate(NECK):
    R.add(f"neck{j + 1}", par, [x - x0, YN(x) - y0, 0], shape={"shape": "sphere", "size": {"r": 0.12 - 0.02 * j}}, color="@body",
          anim={"axis": "y", "deg": 1.5 + 0.5 * j, "speed": HZ * 0.5, "phase": -0.6 * j})
    par, x0, y0 = f"neck{j + 1}", x, YN(x)
R.add("head", par, [XH - x0, YH - y0, 0], shape={"shape": "sphere", "size": {"r": 0.07}}, color="@body",
      anim={"axis": "y", "deg": 1.5, "speed": HZ * 0.5, "phase": -2.6})
R.add("tail1", "body", [-1.0, 0, 0], shape={"shape": "sphere", "size": {"r": 0.1}}, color="@body", anim={"axis": "y", "deg": 4, "speed": HZ * 0.5, "phase": 0.0})
R.add("tail2", "tail1", [-0.3, 0, 0], shape={"shape": "sphere", "size": {"r": 0.05}}, color="@body", anim={"axis": "y", "deg": 7, "speed": HZ * 0.5, "phase": -0.8})
# THE FLIPPERS: each a FLAP bone (axis x: the stroke, up and down) and on it a FEATHER bone (axis z: the twist about the
# span, a quarter beat ahead -- the leading edge down on the downstroke, up on the upstroke) and a tip bone (the
# outer half bending a beat behind); the hind pair a little more than a third of a stroke behind the fore. The blades
# REST angled 10 degrees down, so the stroke (20, the tip 6 more) sweeps from well below the horizontal to 16 degrees
# above it -- never up like a fin
FORE = [0.0, -0.12, 0.41]; HIND = [-0.8, -0.1, 0.3]
FLEN = {"fore": 1.4, "hind": 1.22}   # (2026-11-07: the hind pair a little smaller)
SDIR = {"fore": norm([-0.32, -0.18, 1.0]), "hind": norm([-0.5, -0.18, 1.0])}
FLAP = 20
for nm, P, lag in (("fore", FORE, 0.0), ("hind", HIND, -2.3)):
    tip = add(P, mul(SDIR[nm], 0.47 * FLEN[nm]))
    for side, sg in (("L", 1), ("R", -1)):
        R.add(f"{nm}{side}", "body", [P[0], P[1], sg * P[2]], shape={"shape": "sphere", "size": {"r": 0.05}}, color="@body",
              anim={"axis": "x", "deg": sg * FLAP, "speed": HZ, "phase": lag})
        R.add(f"{nm}F{side}", f"{nm}{side}", [0, 0, 0], shape={"shape": "sphere", "size": {"r": 0.04}}, color="@body",
              anim={"axis": "z", "deg": 12, "speed": HZ, "phase": lag + 1.57})
        R.add(f"{nm}T{side}", f"{nm}F{side}", [tip[0] - P[0], tip[1] - P[1], sg * (tip[2] - P[2])], shape={"shape": "sphere", "size": {"r": 0.03}},
              color="@body", anim={"axis": "x", "deg": sg * 6, "speed": HZ, "phase": lag - 0.7})

PAT = "plesio"
sh = []
# THE TRUNK: a broad deep teardrop (1.2 m across, 0.66 deep), the back rounded, the belly flatter over the gastralia;
# widest at the shoulders, tapering to the hips
sh += [
    S("ell", id="trunk", c=[-0.36, 0.0, 0], r=[0.72, 0.29, 0.58], k=0.1, color="@body", pat=PAT),
    S("ell", id="chest", c=[-0.06, -0.02, 0], r=[0.42, 0.27, 0.52], k=0.1, color="@body", pat=PAT),
    S("ell", id="hips", bone="body", c=[-0.84, 0.0, 0], r=[0.34, 0.21, 0.36], k=0.1, color="@body", pat=PAT),
    S("ell", id="back", c=[-0.36, 0.08, 0], r=[0.62, 0.25, 0.44], k=0.12, color="@body", pat=PAT),
    S("ell", id="belly", c=[-0.4, -0.1, 0], r=[0.64, 0.23, 0.5], k=0.1, color="@body", pat=PAT),
]
# THE NECK: long and fairly stiff, curving gently up, thick and fleshy at its base where it flows into the shoulders and
# tapering smoothly to the head; one tube per neck bone along the curve
NR = lambda x: 0.052 + 0.206 * (1 - max(0.0, min(1.0, (x - 0.05) / (XH - 0.05)))) ** 2.2
cuts = [0.02] + NECK + [XH + 0.01]
bones = ["body", "neck1", "neck2", "neck3", "neck4"]
for j in range(len(cuts) - 1):
    xa, xb = cuts[j] - (0.06 if j else 0), cuts[j + 1] + 0.06
    n = 6
    pts = [[x, YN(x) + 0.005, 0, NR(x)] for x in (xa + (xb - xa) * i / (n - 1) for i in range(n))]
    sh.append(S("tube", id=f"neck{j}", bone=bones[j], pts=pts, k=0.05, color="@body", pat=PAT))
# (the neck's root blended broad and deep into the shoulders)
sh.append(S("ell", id="neckroot", c=[0.16, -0.0, 0], r=[0.32, 0.23, 0.3], k=0.1, color="@body", pat=PAT))
# THE TAIL: short, tapering to a point, a little flattened
TR = lambda x: lerpf(0.15, 0.012, ((-0.95 - x) / 0.63) ** 0.85)
for j, (xa, xb, b) in enumerate([(-0.88, -1.04, "body"), (-0.97, -1.34, "tail1"), (-1.26, -1.58, "tail2")]):
    pts = [[xa + (xb - xa) * i / 3, 0.0, 0, TR(min(-0.95, xa + (xb - xa) * i / 3))] for i in range(4)]
    sh.append(S("tube", id=f"tail{j}", bone=b, pts=pts, k=0.03, color="@body", pat=PAT))

# THE HEAD: small (25 cm) and DISTINCT -- a little wider than the neck behind it; the skull short and rounded-triangular
# seen from above (broad behind, the snout tapering), the EYES big, set up and forward; the JAW HINGE a knob behind and
# below the eye where the mouth's line ends; the jaws lined with slender interlocking needle TEETH
XT = XH + 0.245
H = lambda x, y, z=0.0: [x, YH + y, z]
sh += [
    S("ell", id="cranium", bone="head", c=H(XH + 0.07, 0.012), r=[0.088, 0.05, 0.074], k=0.03, color="@body", pat=PAT),
    S("ell", id="snout", bone="head", c=H(XH + 0.15, 0.0), r=[0.095, 0.03, 0.042], k=0.03, color="@body", pat=PAT),
    S("ell", id="jaw", bone="head", c=H(XH + 0.11, -0.036), r=[0.135, 0.021, 0.054], k=0.025, color="@body", pat=PAT),
    S("ell", id="throatH", bone="head", c=H(XH + 0.02, -0.03), r=[0.075, 0.036, 0.056], k=0.03, color="@body", pat=PAT),
    S("ell", id="hinge", bone="head", c=H(XH + 0.016, -0.03, 0.064), r=[0.03, 0.026, 0.022], k=0.01, color="@body", pat=PAT, mirror=True),
    S("ell", id="brow", bone="head", c=H(XH + 0.1, 0.036, 0.036), r=[0.036, 0.013, 0.018], k=0.012, color="@body", pat=PAT, mirror=True),
]
# (the mouth's line: a shallow cut between the jaws, from the tip back past the eye to just before the hinge)
def jaw_z(x):     # (the jaws' half width at the mouth line)
    t = (x - XH) / (XT - XH)
    return max(0.006, 0.062 * (1 - max(0.0, t) ** 1.8) ** 0.6)
MOUTH = [H(XT - 0.008, -0.02, 0.0) + [0.005]] + [H(x, -0.021, jaw_z(x) - 0.002) + [0.005] for x in (XH + 0.18, XH + 0.12)] + [H(XH + 0.075, -0.022, jaw_z(XH + 0.075) - 0.004) + [0.0035]]
sh.append(S("tube", id="mouth", bone="head", pts=MOUTH, k=0.004, color="@mouth", op="sub", mirror=True))
sh.append(S("sphere", id="nostril", bone="head", c=H(XH + 0.13, 0.024, 0.015), r=0.005, k=0.003, color="@mouth", op="sub", mirror=True))
# teeth: upper and lower alternating so they mesh, small slender needles leaning OUT and FORWARD (the front ones the
# longest), crossing the other jaw's lip as they do when the mouth is shut
teeth = []
NT = 11
for i in range(NT):
    t = 0.05 + i * 0.7 / (NT - 1)
    for up, off in ((1, 0.0), (-1, 0.5)):
        tt = t + off * 0.7 / (NT - 1)
        x = XT - 0.01 - tt * (XT - XH - 0.08)
        z = jaw_z(x) - 0.004
        ln = 0.017 * (1.0 - 0.55 * tt)
        a = H(x, -0.021 + up * 0.004, z - 0.002)
        dvec = norm([0.55 + 0.4 * (1 - tt), -up * 0.55, 0.75])
        b = add(a, mul(dvec, ln))
        teeth.append(S("cone", id=f"tooth{'U' if up > 0 else 'L'}{i}", bone="head", a=a, b=b, ra=0.0022, rb=0.0005, k=0.001, kc=0.0004,
                       color="@tooth", mirror=True))
sh += teeth

# THE FLIPPERS: long wing-shaped hydrofoils, broad at the root and tapering to a point, curving back; the hind nearly as
# big as the fore (1.0 m and 0.94); the leading edge thick and straight, the trailing thin. Each a stack of plates on its
# flap / feather / tip bones (the inner part on the feather bone, the outer on the tip bone)
def flipper(nm, P, chord0):
    length, sdir = FLEN[nm], SDIR[nm]
    # (2026-11-07: an elongated TEARDROP paddle -- a narrow wrist at the root, widest halfway out, then a curved taper to a
    # point; it was a straight-sided triangle spike. 1.4 m from the root inside the trunk: about 1 m of it showing)
    def chord(t):
        if t < 0.5: f = 0.3 + 0.7 * math.sin(0.5 * math.pi * t / 0.5)
        else: f = math.cos(0.5 * math.pi * min(1.0, (t - 0.5) / 0.5)) ** 1.15
        return chord0 * f + 0.004
    sweep = lambda t: 0.2 * t * t
    root = [P[0] + 0.02, P[1], P[2] - 0.06]
    cdir = sub([1, 0, 0], mul(sdir, dot([1, 0, 0], sdir)))
    ol = lambda inset, tmax: blade_outline(root, sdir, cdir, length, chord, le_off=lambda t: 0.2 * chord(t) * (1 - t), sweep=sweep, n=16, inset=inset, tmax=tmax)
    out = []
    span = lambda p: dot(sub(p, root), sdir) / length
    for li, (pts, r) in enumerate([(ol(0, 1.0), 0.011), (ol(0.38, 0.85), 0.022), (ol(0.62, 0.55), 0.034)]):
        for sp in fin(pts, r, "@body", bone=f"{nm}FL", id=f"{nm}{li}_", k=0.01, mirror=True, pat=PAT):
            c = [(sp["a"][k] + sp["b"][k] + sp["c"][k]) / 3 for k in range(3)]
            if span(c) > 0.47: sp["bone"] = f"{nm}TL"
            out.append(sp)
    return out
sh += flipper("fore", FORE, 0.36)
sh += flipper("hind", HIND, 0.31)

d = {
    "name": "plesiosaurus",
    "_about": "SCULPTED (2026-11-06, the sculpt overlay; generator scratchpad sc/sea3/gen/plesio.py): Plesiosaurus dolichodeirus, the Lower Jurassic marine reptile of Lyme Regis, 3.3 m -- NOT a dinosaur (a sauropterygian), so it is filed with the sea life and swims with the swimmers. A small DISTINCT head (25 cm, a little wider than the neck behind it: a short rounded-triangular skull, the eyes up and forward, the jaw's hinge behind them) on a neck about as long as the trunk (1.3 m, five bones, thick and fleshy at its root, tapering, curving gently up at rest); the trunk a deep broad barrel (1.2 m across, 0.66 deep, the back rounded); FOUR long hydrofoil flippers, elongated teardrops (a narrow wrist, broad in the middle, tapering to a swept-back point; 2026-11-07), the hind pair a little smaller, resting angled down; a short tapering tail; the jaws lined with small needle teeth leaning out and forward, interlocking. COUNTERSHADED (coatpat.js 43 `plesio`: the dark olive back crossfaded to a pale belly along the body's mid-height, finely blotched on top, a fine pebbled skin). It swims by UNDERWATER FLIGHT: each flipper flaps (axis x) and feathers (axis z, a quarter beat ahead) and its outer half bends behind, the hind pair a third of a stroke after the fore. It makes no sound. In the game it lives in the big lake (the Loch Ness wink: index.html seaLife, its head and neck breaking the surface now and then) and the open sea.",
    "kind": "parts",
    "facet": False,
    "flags": {"fly": {"alt": [1.0, 3.0], "speed": [1.2, 2.0], "hz": HZ}},
    "colors": {"body": "#4a4c3c", "belly": "#c8c0a4", "tooth": "#e4dcc4", "mouth": "#5a3030"},
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mottle": {"amount": 0},
        "mesh": {"cell": 0.012, "tris": [10000, 3000], "focus": {"head": 3}, "far": 10},
        "shape": sh,
        "eyes": {"at": H(XH + 0.105, 0.03, 0.05), "from": H(XH + 0.105, 0.0, 0), "r": 0.014, "color": "#100c06", "iris": "#6a5a26", "pupil": "round",
                 "lid": False, "sink": 0.35, "socket": 1.05, "bone": "head"},
    },
}
write_to("sea/plesiosaurus", d)
