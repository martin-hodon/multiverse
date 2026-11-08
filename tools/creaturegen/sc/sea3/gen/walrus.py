from cetlib import *
import os, random

# WALRUS (Odobenus rosmarus), a BULL, 3.0 m from the muzzle to the tail, the hind flippers 0.5 m more. Rest frame: x
# forward, y up, z left, metres; the belly's bottom (the ground it lies on) at y = -0.5. Drawn LYING ON LAND: level,
# the fore flippers propped forward and out beside the chest, palms on the ground; the hind flippers back, fanned out
# on the ground. Its other poses -- the hind flippers turned forward under the pelvis to walk, the fore flippers swept
# back to swim, the head raised -- are the game's (haulout.js: an.pose per bone).
# (v3, 2026-11-06: ELONGATED -- a spindle, deepest and widest at the shoulders and chest, the back sloping and tapering
#  to a narrow pelvis (the shoulders 1.5x the hips' width from above); a SMALL head, a third of the shoulders' width, on
#  a thick but visible folded neck -- a dip in the outline between the head and the shoulders)
R = Rig()
HZ = 0.6
R.add("body", None, [0, 0, 0], shape=tube_part([0.6, 0, 0], [-0.45, 0, 0], 0.48, 0.42), color="@back")
R.add("neck", "body", [0.82, 0, 0], shape={"shape": "sphere", "size": {"r": 0.26}}, color="@back")
R.add("head", "neck", [0.4, 0.0, 0], shape={"shape": "sphere", "size": {"r": 0.17}}, color="@back")
R.add("hips", "body", [-0.5, -0.04, 0], shape={"shape": "sphere", "size": {"r": 0.34}}, color="@back",
      anim={"axis": "y", "deg": 7, "speed": HZ, "phase": 0})
R.add("tail", "hips", [-0.66, -0.1, 0], shape={"shape": "sphere", "size": {"r": 0.12}}, color="@back",
      anim={"axis": "y", "deg": 15, "speed": HZ, "phase": -0.9})
for side, s in (("L", 1), ("R", -1)):
    R.add(f"hflip{side}", "tail", [-0.22, -0.16, s * 0.09], shape={"shape": "sphere", "size": {"r": 0.05}}, color="@back")
    R.add(f"fflip{side}", "body", [0.55, -0.22, s * 0.42], shape={"shape": "sphere", "size": {"r": 0.06}}, color="@back")
CUT = [1.14, 0.7, -0.42, -1.08]
def bone_x(x):
    return "head" if x > CUT[0] else "neck" if x > CUT[1] else "body" if x > CUT[2] else "hips" if x > CUT[3] else "tail"
PAT = "walrus"
B = "@back"
# THE BODY (x, top, bottom, half width): the neck thick but narrower than the shoulders, the shoulders and chest the
# deepest and widest, the back sloping and tapering to the pelvis, the hindquarters drooping to the ground
ST = [(1.2, 0.17, -0.27, 0.19), (1.1, 0.13, -0.32, 0.2), (0.98, 0.22, -0.4, 0.29), (0.84, 0.35, -0.46, 0.38),
      (0.66, 0.46, -0.5, 0.47), (0.45, 0.51, -0.5, 0.49), (0.2, 0.49, -0.5, 0.48), (-0.1, 0.42, -0.49, 0.44),
      (-0.45, 0.32, -0.47, 0.4), (-0.8, 0.2, -0.44, 0.33), (-1.08, 0.08, -0.42, 0.24), (-1.28, -0.04, -0.4, 0.15),
      (-1.42, -0.14, -0.37, 0.08)]
RF = lambda t, b, w: w + 0.4 * ((t - b) / 2 - w)
sh = trunk_tubes(ST, [1.2, CUT[0], CUT[1], CUT[2], CUT[3], -1.42], ["head", "neck", "body", "hips", "tail"], B, step=0.1, ov=0.08, k=0.1, pat=PAT, rfun=RF)
# (the belly a little flattened on the ground, the chest's sides full)
sh += [S("ell", id="belly", c=[0.2, -0.3, 0], r=[0.75, 0.2, 0.48], k=0.15, color=B, pat=PAT),
       S("ell", id="belly2", bone="hips", c=[-0.7, -0.3, 0], r=[0.45, 0.14, 0.32], k=0.12, color=B, pat=PAT)]
def ell_x(c, r, y, z):
    q = 1 - ((y - c[1]) / r[1]) ** 2 - ((z - c[2]) / r[2]) ** 2
    return c[0] + r[0] * math.sqrt(max(0.0, q))
def ell_z(c, r, x, y):
    q = 1 - ((x - c[0]) / r[0]) ** 2 - ((y - c[1]) / r[1]) ** 2
    return c[2] + r[2] * math.sqrt(max(0.0, q))
def ring_at(x):
    t, b, w = smooth(ST, x); return (t + b) / 2, RF(t, b, w)

# THE NECK'S AND SHOULDERS' FAT FOLDS: thick rolls round the neck over the top and the sides, and the bull's knobbly
# BOSSES on the neck and shoulders
for j, x in enumerate([1.06, 0.96, 0.86, 0.75]):
    yc, rr = ring_at(x)
    pts = []
    for a in range(-6, 7):
        ang = math.radians(a * 14)   # (0 the top; +/-84 down the sides)
        pts.append([x - 0.025 * abs(a) / 6, yc + rr * math.cos(ang) * 0.985, rr * math.sin(ang) * 0.985, 0.045 - 0.004 * j])
    sh.append(S("tube", id=f"fold{j}", bone=bone_x(x), pts=pts, k=0.05, color=B, pat=PAT))
rnd_ = random.Random(7)
for nb in range(22):
    x = rnd_.uniform(0.42, 0.85); ang = math.radians(rnd_.choice([-1, 1]) * rnd_.uniform(22, 80))
    yc, rr = ring_at(x)
    sh.append(S("sphere", id=f"boss{nb}", bone=bone_x(x), c=[x, yc + rr * math.cos(ang) * 0.99, rr * math.sin(ang) * 0.99], r=rnd_.uniform(0.02, 0.032), k=0.03, color=B, pat=PAT))

# THE HEAD: small -- a third of the shoulders' width -- round-topped behind, and in front the MUZZLE: a broad, flattened,
# squarish pad (the two whisker pads side by side) carrying the moustache; the nostrils on TOP of it; the eyes small,
# high on the sides; no ears
CRN = ([1.29, 0.07, 0], [0.19, 0.18, 0.165])
PAD = ([1.45, -0.07, 0.08], [0.1, 0.12, 0.11])
sh += [S("ell", id="cranium", bone="head", c=CRN[0], r=CRN[1], k=0.06, color=B, pat=PAT),
       S("ell", id="snout", bone="head", c=[1.4, -0.02, 0], r=[0.14, 0.13, 0.16], k=0.05, color=B, pat=PAT),
       S("ell", id="pad", bone="head", c=PAD[0], r=PAD[1], k=0.035, color=B, pat=PAT, mirror=True),
       S("ell", id="face", bone="head", c=[1.49, -0.07, 0], r=[0.06, 0.12, 0.16], k=0.04, color=B, pat=PAT),
       S("ell", id="chin", bone="head", c=[1.41, -0.21, 0], r=[0.09, 0.05, 0.09], k=0.04, color=B, pat=PAT),
       S("ell", id="throat", bone="neck", c=[1.17, -0.17, 0], r=[0.16, 0.12, 0.17], k=0.07, color=B, pat=PAT)]
# (the nostrils: two short crescent slits on top of the muzzle's front, set wide, pale-rimmed by the pattern)
NY = 0.03
sh += [S("ell", id="nostril", bone="head", c=[1.49, NY, 0.05], r=[0.026, 0.012, 0.011], rot=[0, -30, 0], k=0.008, color="@dark", op="sub", mirror=True),
       S("ell", id="cleft", bone="head", c=[ell_x(PAD[0], PAD[1], -0.08, 0.0) + 0.005, -0.08, 0], r=[0.02, 0.08, 0.01], k=0.01, color="@dark", op="sub")]
EY = (1.3, 0.12)
EZ = ell_z(CRN[0], CRN[1], EY[0], EY[1])

# THE TUSKS: the upper canines out of the corners of the mouth under the pads, hanging down, a little back and in,
# 0.6 m of ivory, curved back a little, oval at the root
TR = [1.46, -0.18, 0.075]
NS = 4
for k in range(NS):
    t0, t1 = k / NS, (k + 1) / NS
    P = lambda t: [TR[0] - 0.12 * t - 0.12 * t * t, TR[1] - 0.6 * t, TR[2] - 0.018 * t]
    ra, rb = lerpf(0.038, 0.007, t0 ** 0.9), lerpf(0.038, 0.007, t1 ** 0.9)
    sh.append(S("cone", id=f"tusk{k}", bone="head", a=P(t0), b=P(t1 + (0.015 if k < NS - 1 else 0)), ra=ra, rb=rb, k=0, color="@ivory", mirror=True))
sh += [S("ell", id="tuskroot", bone="head", c=[TR[0], TR[1] + 0.03, TR[2]], r=[0.055, 0.05, 0.045], k=0.04, color=B, pat=PAT, mirror=True)]

# THE MOUSTACHE: hundreds of stiff, thick, pale whiskers in rows over the front and sides of the pads, aimed forward and
# down -- here 35 a side, the rows' tips making the bristling square front
nw = 0
for row in range(5):
    y = -0.02 - 0.035 * row
    for j in range(7):
        zz = 0.02 + 0.026 * j
        if zz > PAD[1][2] + PAD[0][2] - 0.02: continue
        x = ell_x(PAD[0], PAD[1], y, zz)
        if x <= PAD[0][0] + 0.02: continue
        a = [x - 0.004, y, zz]
        dirn = norm([0.75 - 0.05 * j, -0.55 - 0.03 * row, 0.15 + 0.07 * j])
        L = 0.07 + 0.012 * math.sin(nw * 2.3) - 0.004 * row
        sh.append(S("cone", id=f"wh{nw}", bone="head", a=a, b=add(a, mul(dirn, L)), ra=0.0028, rb=0.0011, k=0, color="@whisker", mirror=True))
        nw += 1

# THE FORE FLIPPERS (land pose): the arm out of the chest's lower side, down to the ground beside the chest, and the
# big paddle propped forward and a little out, palm flat on the ground -- broad, square-ended, hairless, five small
# nails set back from the edge
sh += [S("tube", id="farm", bone="fflipL", pts=[[0.48, -0.24, 0.34, 0.14], [0.55, -0.36, 0.47, 0.12], [0.6, -0.44, 0.54, 0.1]], k=0.08, color=B, pat=PAT, mirror=True)]
FR = [0.6, -0.455, 0.54]
fsd = norm([0.72, -0.04, 0.69]); fcd = [0.69, 0.0, -0.72]
FL = 0.5
fchord = lambda t: (0.25 + 0.09 * t) * (1 if t < 0.9 else math.sqrt(max(0.0, 1 - ((t - 0.9) / 0.1) ** 2)) * 0.5 + 0.5)
fthick = lambda t: lerpf(0.08, 0.03, t)
# (the leading edge the span line's inner side: the blade out beside it, away from the chest)
sh += blade("ffl", FR, fsd, fcd, FL, 12, fchord, fthick, lambda t: 0.0, lambda t: "fflipL", B, pat=PAT, over=1.3)
for s in sh:
    if s.get("id", "").startswith("ffl"): s["mirror"] = True
u, v, w = frame(fsd, fcd)
for c in range(5):
    tt = (c - 2) / 2.0
    nrm = cross(fsd, v); nrm = nrm if nrm[1] > 0 else mul(nrm, -1)
    p0 = add(add(FR, mul(fsd, FL - 0.075)), mul(v, -fchord(0.86) * (0.5 + tt * 0.36)))
    p0 = add(p0, mul(nrm, fthick(0.86) * 0.3))
    sh.append(S("cone", id=f"fnail{c}", bone="fflipL", a=p0, b=add(p0, mul(fsd, 0.03)), ra=0.009, rb=0.004, k=0.004, color="@dark", mirror=True))

# THE HIND FLIPPERS: back and fanned a little out, lying flat on the ground -- each a broad fan of five webbed digits
# (the outer longest), hairless soles
HR = [-1.38, -0.31, 0.09]
hsd = norm([-1.0, -0.15, 0.5])
roll = math.radians(80)
hcd = norm([0.0, math.cos(roll), math.sin(roll)])
hcd = norm(sub(hcd, mul(hsd, dot(hcd, hsd))))
HL = 0.5
def hflip_outline(inset=0.0):
    half = lambda uu: 0.07 + 0.11 * (uu / HL) ** 1.3
    pts2 = [(HL * 0.86 * k / 6, -half(HL * 0.86 * k / 6)) for k in range(7)]
    toes = [(-1.0, HL), (-0.5, HL - 0.045), (0.0, HL - 0.065), (0.5, HL - 0.045), (1.0, HL)]
    hw = half(HL * 0.95)
    for j, (vv, uu) in enumerate(toes):
        pts2.append((uu, vv * hw * 0.97))
        if j < 4: pts2.append((min(uu, toes[j + 1][1]) - 0.03, (vv + toes[j + 1][0]) / 2 * hw))
    pts2 += [(HL * 0.86 * k / 6, half(HL * 0.86 * k / 6)) for k in range(6, -1, -1)]
    return [add(add(HR, mul(hsd, uu * (1 - inset * 0.25))), mul(hcd, vv * (1 - inset))) for uu, vv in pts2]
sh += plates("hfl", [(hflip_outline(0.0), 0.014), (hflip_outline(0.45), 0.03)], "hflipL", B, k=0.012, mirror=True, pat=PAT)
sh += [S("ell", id="hroot", bone="hflipL", c=add(HR, mul(hsd, 0.05)), r=[0.11, 0.06, 0.06], k=0.05, color=B, pat=PAT, mirror=True),
       S("ell", id="stub", bone="tail", c=[-1.46, -0.22, 0], r=[0.07, 0.035, 0.04], k=0.03, color=B, pat=PAT)]

for p in sh:
    if p.get("op") != "sub" and p.get("type") != "cone": p["wet"] = 0.05

d = {
    "name": "walrus",
    "_about": "SCULPTED (2026-11-06, the sculpt overlay; generator scratchpad sc/sea3/gen/walrus.py): a WALRUS (Odobenus rosmarus), a bull, 3 m muzzle to tail and its hind flippers 0.5 m more, ~1.2 t -- massive but ELONGATED: a spindle, deepest and widest (1.06 m) at the shoulders and chest, about a metre high lying, the back sloping and tapering to a narrow pelvis (the shoulders 1.5x the hips), thick FAT FOLDS round the neck and the bull's knobbly bosses; a SMALL head (a third of the shoulders' width) on a thick folded neck, the outline dipping between them; the MUZZLE a broad flattened squarish pad under a dense MOUSTACHE of stiff pale bristles, the nostrils on top of it, small eyes high on the sides, no ears; the TUSKS, 0.6 m of ivory hanging from the upper jaw. Drawn lying on land: the big paddle FORE FLIPPERS propped forward and out beside the chest, palms on the ground (broad, square-ended, hairless, small nails), the HIND FLIPPERS back, fanned out flat on the ground -- haulout.js turns them FORWARD under the pelvis when it walks, and sweeps the fore flippers back when it swims. Cinnamon-pink-brown, wrinkled, sparse-haired (coatpat.js `walrus`: creases across the folds and a net of them elsewhere, pinker low down and over the chest). In the world: a small herd (or one wanderer) on a sea's shore (haulout.js).",
    "kind": "parts",
    "facet": False,
    "colors": {"back": os.environ.get("WC", "#8a6352"), "dark": "#2a1c16", "ivory": "#e8dcc0", "whisker": "#dcc9a2"},
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mottle": {"amount": 0},
        "mesh": {"cell": 0.012, "tris": [10500, 3000], "focus": {"head": 4}, "far": 18},
        "shape": sh,
        "eyes": {"at": [EY[0] + 0.02, EY[1], EZ + 0.015], "from": [EY[0] - 0.02, EY[1], 0], "r": 0.019, "color": "#0a0605", "iris": "#3a120c", "pupil": "round", "lid": False, "sink": 0.35, "socket": 1.1, "bone": "head"},
    },
}
write_to("sea/walrus", d)
print("whiskers", nw)
