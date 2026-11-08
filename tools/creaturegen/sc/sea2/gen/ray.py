from sealib import *

# COMMON STINGRAY (Dasyatis pastinaca), the disc 0.9 m across and 0.7 long, the whip tail to 1.15 m behind the snout
HZ = 0.45
ZT = 0.445                       # (the wingtip)
R = Rig()
R.add("body", None, [0, 0, 0], shape=tube_part([0.36, 0, 0], [-0.33, 0, 0], 0.06, 0.04))
JZ = [0.11, 0.23, 0.345]         # (the wing's joints, out along the span)
for side, s in (("L", 1), ("R", -1)):
    par, z0 = "body", 0
    for j, z in enumerate(JZ):
        R.add(f"wing{j + 1}{side}", par, [0.0 if j == 0 else 0, 0, s * (z - z0)], shape={"shape": "sphere", "size": {"r": 0.01}},
              anim={"axis": "x", "deg": s * (7 + 3 * j), "speed": HZ, "phase": -0.75 * j})
        par, z0 = f"wing{j + 1}{side}", z
# (2026-11-07, the MANTA variant: its wings reach twice as far -- one more joint out along the span, only on it)
ZM = 0.95
for side, s in (("L", 1), ("R", -1)):
    R.add(f"wing4{side}", f"wing3{side}", [0, 0, s * (0.6 - JZ[2])], shape={"shape": "sphere", "size": {"r": 0.01}},
          anim={"axis": "x", "deg": s * 14, "speed": HZ, "phase": -2.4})
    R.parts[-1]["when"] = "manta"
TX = [-0.33, -0.5, -0.7, -0.92, -1.15]
par = "body"
for j in range(4):
    R.add(f"tail{j + 1}", par, [TX[j] - (TX[j - 1] if j else 0), 0, 0], shape=tube_part([0, 0, 0], [TX[j + 1] - TX[j], 0, 0], 0.02 - 0.004 * j),
          anim={"axis": "y", "deg": 5 + 2 * j, "speed": HZ, "phase": -0.9 - 0.7 * j})
    par = f"tail{j + 1}"

def wbone(z):
    z = abs(z); side = "L"
    return "body" if z < JZ[0] else f"wing1{side}" if z < JZ[1] else f"wing2{side}" if z < JZ[2] else f"wing3{side}"
# THE DISC: slices across the span, each a flat ellipsoid along the chord -- a diamond, its leading edges a little
# convex, thick over the body and thinning to the wingtips
xf = lambda z: 0.36 - 0.86 * z + 0.035 * math.sin(math.pi * z / ZT)
xb = lambda z: -0.34 + 0.70 * z - 0.03 * math.sin(math.pi * z / ZT)
th = lambda z: 0.094 * max(0.0, 1 - z / (ZT + 0.01)) ** 1.5 + 0.016
sh = []
dz = 0.018
n = int(0.43 / dz) + 1
for i in range(n):
    z = i * dz
    ch = xf(z) - xb(z)
    sh.append(S("ell", id=f"disc{i}", bone=wbone(z), c=[(xf(z) + xb(z)) / 2, 0.002 - 0.005 * (z / ZT) ** 2, z], r=[ch / 2, th(z) / 2, 2.0 * dz],
                k=round(0.5 * min(th(z) / 2, 2.0 * dz), 5), color="@body", mirror=True if i else None))
sh += [
    # the body's hump, the pointed snout, the eyes RAISED ON TOP with the spiracles behind them
    S("ell", id="hump", c=[0.0, 0.006, 0], r=[0.27, 0.045, 0.1], k=0.02, color="@body"),
    S("ell", id="snout", c=[0.31, 0.0, 0], r=[0.06, 0.016, 0.03], k=0.012, color="@body"),
    S("ell", id="eyebump", c=[0.165, 0.03, 0.052], r=[0.02, 0.013, 0.014], k=0.008, color="@body", mirror=True),
    S("ell", id="spiracle", c=[0.128, 0.043, 0.054], r=[0.013, 0.008, 0.009], k=0.004, color="@dark", op="sub", mirror=True),
    # underneath: the transverse mouth, the nostrils before it, five pairs of gill slits
    S("ell", id="mouth", c=[0.22, -0.037, 0], r=[0.005, 0.005, 0.02], k=0.003, color="@dark", op="sub"),
    S("ell", id="nostril", c=[0.245, -0.032, 0.018], r=[0.006, 0.004, 0.005], k=0.002, color="@dark", op="sub", mirror=True),
] + [S("tube", id=f"gill{g}", pts=[[0.135 - 0.019 * g, -0.04, 0.05 + 0.004 * g, 0.0055], [0.13 - 0.019 * g, -0.04, 0.07 + 0.003 * g, 0.0055]],
       k=0.002, color="@dark", op="sub", mirror=True) for g in range(5)] + [
    # the pelvic fins: lobes either side of the tail's root
    S("ell", id="pelvic", c=[-0.33, -0.006, 0.055], r=[0.07, 0.011, 0.042], rot=[0, -12, 0], k=0.01, color="@body", mirror=True),
]
for q in sh: q["when"] = "sting"            # (the stingray's disc and face: not the manta's)
# THE WHIP TAIL: tapering along its four bones, a low fold below, the serrated venomous BARB on top a third along it
TR = [0.022, 0.0138, 0.0095, 0.0068, 0.0056]
for j in range(4):
    sh.append(S("tube", id=f"tail{j + 1}", bone=f"tail{j + 1}", pts=[[TX[j] + (0.03 if j == 0 else 0.004), 0.0, 0, TR[j]], [TX[j + 1] - 0.004, 0.0, 0, TR[j + 1]]],
                k=0.004, color="@body", when="sting"))
# (the manta's tail: SHORT -- 0.5 behind the disc, about 0.7 of its length -- and thin, on the first three tail bones)
for j, (xa, xb, ra, rb) in enumerate([(-0.3, -0.5, 0.016, 0.009), (-0.496, -0.7, 0.009, 0.005), (-0.696, -0.83, 0.005, 0.0015)]):
    sh.append(S("tube", id=f"mtail{j + 1}", bone=f"tail{j + 1}", pts=[[xa, -0.007, 0, ra], [xb, -0.007, 0, rb]], k=0.004, color="@cape", when="manta"))   # (round 3b: dark on top, as the back)
sh += [
    S("ell", id="fold", bone="tail2", c=[-0.62, -0.01, 0], r=[0.1, 0.008, 0.004], k=0.004, color="@pale"),
    S("tube", id="barb", bone="tail2", pts=[[-0.53, 0.01, 0, 0.0055], [-0.57, 0.016, 0, 0.0045], [-0.62, 0.021, 0, 0.0036]], k=0.003, color="@barb"),
]
for q in sh[-2:]: q["when"] = "sting"

# THE MANTA (variant, param `manta`): the same rig and tail, its own disc -- a body longer than the stingray's and
# WINGS swept back to pointed tips nearly a metre out each side (the leading edge convex, the trailing edge hollowed),
# thick over the body and thin out along the span, held flat; the two CEPHALIC FINS as forward lobes either side of
# the wide terminal MOUTH, rolled like horns; the eyes on the head's sides behind them; two pale SHOULDER PATCHES on
# the black back; the belly white (the shade's midline through the wing)
def wbone_m(z):
    z = abs(z)
    return "body" if z < JZ[0] else "wing1L" if z < JZ[1] else "wing2L" if z < JZ[2] else "wing3L" if z < 0.6 else "wing4L"
um = lambda z: max(0.0, min(1.0, (z - 0.12) / (ZM - 0.12)))
xfm = lambda z: 0.24 - 0.5 * max(0.0, z - 0.12) + 0.07 * math.sin(math.pi * um(z))
xbm = lambda z: -0.36 if z < 0.12 else (-0.36 + (0.125) * um(z)) + 0.1 * math.sin(math.pi * um(z))
thm = lambda z: 0.11 * max(0.0, 1 - z / 0.32) ** 1.4 + 0.016 * (1 - 0.6 * um(z))
YM = -0.007
# (the wings: stacked PLATES on one exact outline -- the leading edge convex and swept back, the trailing edge hollowed,
# a pointed tip -- thin at the rim (6 mm: not under the grid's cut, or it is drawn unpainted) and thicker toward the body; each triangle on the bone its middle lies along)
def m_outline(inset, zmax, z0=0.05, n=22, tip=False):
    zs = [z0 + (zmax - z0) * (i / n) ** 0.9 for i in range(n + 1)]
    mid = lambda z: (xfm(z) + xbm(z)) / 2
    half = lambda z: max(0.004, (xfm(z) - xbm(z)) / 2 * (1 - inset))
    LE = [[mid(z) + half(z), YM, z] for z in zs]
    TE = [[mid(z) - half(z), YM, z] for z in zs][::-1]
    return LE + ([[xbm(ZM) - 0.03, YM, ZM + 0.03]] if tip else []) + TE
M = []
# (round 3: four layers in smaller steps, blended wider -- three left steps on the belly)
# (round 3b: the rim layer blended TIGHT -- wider than its own 6 mm, every station where its sliver triangles meet
# bulged into a rib: the scalloped rim and the ribbed belly)
for li, (ol, r) in enumerate([(m_outline(0.0, ZM - 0.01, tip=True), 0.006), (m_outline(0.22, 0.82), 0.0085), (m_outline(0.4, 0.62), 0.012), (m_outline(0.56, 0.44), 0.016)]):
    for q in fin(ol, r, "@body", bone="body", id=f"mwing{li}_", k=0.003 if li == 0 else 0.016, mirror=True):
        q["bone"] = wbone_m((q["a"][2] + q["b"][2] + q["c"][2]) / 3)
        M.append(q)
M += [
    S("ell", id="mhead", c=[0.12, YM + 0.004, 0], r=[0.15, 0.05, 0.12], k=0.03, color="@body"),
    S("ell", id="mback", c=[-0.1, YM + 0.008, 0], r=[0.26, 0.055, 0.15], k=0.03, color="@body"),
    # (the cephalic fins: rolled lobes reaching forward and a little in, either side of the mouth)
    S("tube", id="cephalic", pts=[[0.2, YM - 0.004, 0.115, 0.024], [0.27, YM - 0.008, 0.118, 0.02], [0.33, YM - 0.012, 0.108, 0.015], [0.37, YM - 0.016, 0.094, 0.009]],
      k=0.012, color="@body", mirror=True),
    S("ell", id="mmouth", c=[0.25, YM - 0.008, 0], r=[0.03, 0.014, 0.085], k=0.006, color="@dark", op="sub"),
    S("ell", id="meyebump", c=[0.215, YM + 0.01, 0.128], r=[0.025, 0.018, 0.016], k=0.01, color="@body", mirror=True),
    # (the gill slits on the belly, five a side, and the pelvic fins at the tail's root)
] + [S("tube", id=f"mgill{g}", pts=[[0.07 - 0.026 * g, YM - 0.05, 0.075 + 0.004 * g, 0.006], [0.065 - 0.026 * g, YM - 0.046, 0.115 + 0.003 * g, 0.006]],
       k=0.002, color="@dark", op="sub", mirror=True) for g in range(5)] + [
    S("ell", id="mpelvic", c=[-0.36, YM - 0.004, 0.055], r=[0.07, 0.01, 0.04], rot=[0, -12, 0], k=0.01, color="@body", mirror=True),
    # (the shoulder patches: pale, soft-edged, curving out behind the head)
    # (the black CAPE: everything above the wings' midline -- a crisp line round the rim however thin the wing; the body's
    # own colour is the white of the belly)
    # (round 3: its lower edge 4 mm under the wings' midline -- inside the rim's round, so the rim is dark on top and at its
    # edge, the line drawn on its underside, not along the outline)
    S("box", id="cape", c=[0.0, YM - 0.004 + 0.15, 0], r=[1.4, 0.15, 1.2], op="paint", kc=0.0015, color="@cape"),
    # (the SHOULDER PATCHES: small pale commas just behind the head, each curving back and out from beside the
    # midline -- the paint a swept round brush laid along the back's surface)
    S("tube", id="shoulder", pts=[[0.135, 0.044, 0.05, 0.014], [0.105, 0.03, 0.085, 0.017], [0.07, 0.02, 0.12, 0.015], [0.035, 0.014, 0.15, 0.01], [0.005, 0.011, 0.17, 0.005]],
      op="paint", kc=0.014, color="@pale", mirror=True),   # (round 3b: the blend two mesh cells wide, the brush narrower to keep the size -- under a cell, the edge stepped along the triangles)
    # (round 3b: the wings' MARGIN dark underneath too, a band 3 cm in from the rim -- the cape's line drawn in on the
    # belly, not along the outline, where the thin edge showed it as white jaggies)
    S("tube", id="mmargin", pts=[p + [0.03] for p in m_outline(0.0, ZM - 0.01, tip=True)[1:-1]], op="paint", kc=0.004, color="@cape", mirror=True),
]
for q in M: q["when"] = "manta"
sh += M

d = {
    "name": "ray",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'; the MANTA variant 2026-11-07: param `manta` swaps in its own disc -- wings swept back to pointed tips nearly 1 m out each side on one more joint, the rolled cephalic fins either side of the wide terminal mouth, the eyes on the head's sides, pale shoulder patches on a black back, a white belly; the stingray's own shapes say `sting`): a common stingray, the disc 0.9 m across -- a flat DIAMOND of wings (slices across the span, thick over the body and thinning to the tips, the leading edges a little convex) round a low hump and a pointed snout; the EYES RAISED ON TOP with the spiracles behind them; underneath, pale (`shade`), the transverse mouth, the nostrils and five pairs of gill slits; the pelvic lobes either side of the root of a long WHIP TAIL, its low fold below and the venomous barb on top a third along it. A SWIMMER (the fish's plumbing: `fly`, `alt` its depth -- kept low, near the bottom; not put in the lake -- a fish of the sea). The wings are three bones a side (wing1-3, out along the span) that FLAP in a wave travelling out to the tips (each a beat behind the one before, the right side mirrored); the tail is four bones that trail in a slow wave.",
    "kind": "parts",
    "facet": False,
    "flags": {"fly": {"alt": [0.15, 0.5], "speed": [0.25, 0.7], "hz": HZ}},
    "colors": {"body": "#7a6650", "pale": "#e8e0d2", "barb": "#d8ccb0", "dark": "#1a1410", "back": "#6c5a46", "belly": "#ece4d8", "cape": "#17191c"},
    "params": {"sting": True, "manta": False, "big": 0},   # (`big`: a number, for the mesh's budget -- the manta's is larger)
    # (the countershade's tones are colours of each coat's own now -- a fixed back tone had painted every coat's top the same)
    "coats": [{"name": "common stingray"}, {"name": "common stingray"}, {"name": "common stingray (dark)", "body": "#3e3a34", "back": "#36322c"},
              {"name": "common stingray (sandy)", "body": "#a89272", "back": "#9a8466"}],
    "variants": {"manta (reef manta)": {"scale": 1.7, "params": {"sting": False, "manta": True, "big": 1},
                                        "colors": {"body": "#ecece8", "back": "#ecece8", "belly": "#f0f0ec", "cape": "#17191c", "pale": "#d2d4d0", "dark": "#060606"}}},
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mesh": {"cell": 0.0068, "tris": ["6000 + 7000 * big", "2000 + 1500 * big"]},   # (2026-11-07: up from 4200; the manta's wide wings twice that again)
        "shade": {"back": "@back", "belly": "@belly", "on": "@body", "k": 0.006, "at": -0.007, "mode": "mix", "tol": 0.3},
        "shape": sh,
        "eyes": [{"when": "sting", "at": [0.165, 0.043, 0.054], "from": [0.165, 0.0, 0.05], "r": 0.009, "color": "#0a0806", "iris": "#8a7040", "pupil": "round", "lid": "@body", "sink": 0.4, "bone": "body"},
                 {"when": "manta", "at": [0.215, YM + 0.012, 0.15], "from": [0.2, YM + 0.01, 0.0], "r": 0.012, "color": "#0a0806", "iris": "#3a3020", "pupil": "round", "lid": "@cape", "sink": 0.35, "bone": "body"}],
    },
}
write("ray", d)
