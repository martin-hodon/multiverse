from cetlib import *
import os

# HARBOUR SEAL (Phoca vitulina), an adult, 1.7 m from the nose to the end of the tail, the hind flippers 0.25 m more.
# Rest frame: x forward, y up, z left, metres; the body's axis at y = 0, the belly's bottom ~0.2 under it. Drawn as it
# swims and lies: level, the head in line, the hind flippers back (a true seal cannot turn them under itself). Its
# poses on land -- the head raised, the galumphing hump, the banana -- are the game's (haulout.js: an.pose per bone).

# THE RIG: body (root) -> neck -> head; body -> hips -> tail -> the hind flippers; the fore flippers on the body
R = Rig()
HZ = 0.9
R.add("body", None, [0, 0, 0], shape=tube_part([0.3, 0, 0], [-0.25, 0, 0], 0.19, 0.18), color="@back")
R.add("neck", "body", [0.40, 0, 0], shape={"shape": "sphere", "size": {"r": 0.12}}, color="@back")
R.add("head", "neck", [0.18, 0.02, 0], shape={"shape": "sphere", "size": {"r": 0.09}}, color="@back")
R.add("hips", "body", [-0.28, 0, 0], shape={"shape": "sphere", "size": {"r": 0.14}}, color="@back",
      anim={"axis": "y", "deg": 9, "speed": HZ, "phase": 0})
R.add("tail", "hips", [-0.30, 0, 0], shape={"shape": "sphere", "size": {"r": 0.06}}, color="@back",
      anim={"axis": "y", "deg": 18, "speed": HZ, "phase": -0.9})
for side, s in (("L", 1), ("R", -1)):
    R.add(f"hflip{side}", "tail", [-0.07, 0.01, s * 0.017], shape={"shape": "sphere", "size": {"r": 0.03}}, color="@back")
    R.add(f"fflip{side}", "body", [0.30, -0.12, s * 0.14], shape={"shape": "sphere", "size": {"r": 0.03}}, color="@back")
CUT = [0.56, 0.38, -0.26, -0.56]
def bone_x(x):
    return "head" if x > CUT[0] else "neck" if x > CUT[1] else "body" if x > CUT[2] else "hips" if x > CUT[3] else "tail"

PAT = [{"when": "harbour", "v": "seal"}, {"when": "greyseal", "v": "greyseal"}]
B = "@back"
# THE BODY (x, top, bottom, half width): a plump spindle, deepest a little ahead of the middle, no waist at the neck
# (the blubber carries the line from the back of the head to the shoulders), tapering hard behind the hips to the stub
ST = [(0.70, 0.095, -0.075, 0.085), (0.62, 0.112, -0.097, 0.1), (0.52, 0.136, -0.132, 0.124), (0.40, 0.168, -0.17, 0.16),
      (0.25, 0.195, -0.2, 0.198), (0.08, 0.205, -0.21, 0.212), (-0.08, 0.2, -0.205, 0.205), (-0.22, 0.178, -0.18, 0.176),
      (-0.36, 0.152, -0.152, 0.148), (-0.48, 0.112, -0.11, 0.106), (-0.58, 0.07, -0.068, 0.066), (-0.66, 0.046, -0.044, 0.044),
      (-0.72, 0.03, -0.028, 0.03)]
sh = trunk_tubes(ST, [0.70, CUT[0], CUT[1], CUT[2], CUT[3], -0.72], ["head", "neck", "body", "hips", "tail"], B, step=0.06, ov=0.05, k=0.05, pat=PAT,
                 rfun=lambda t, b, w: w + 0.4 * ((t - b) / 2 - w))
# (the belly a little flattened and wider -- it lies on it)
sh += [S("ell", id="belly", c=[0.02, -0.11, 0], r=[0.42, 0.085, 0.2], k=0.07, color=B, pat=PAT),
       S("ell", id="belly2", bone="hips", c=[-0.33, -0.07, 0], r=[0.24, 0.06, 0.125], k=0.06, color=B, pat=PAT)]

def ell_x(c, r, y, z):
    """the front of an ellipsoid (x) at height y, side z"""
    q = 1 - ((y - c[1]) / r[1]) ** 2 - ((z - c[2]) / r[2]) ** 2
    return c[0] + r[0] * math.sqrt(max(0.0, q))
def ell_z(c, r, x, y):
    q = 1 - ((x - c[0]) / r[0]) ** 2 - ((y - c[1]) / r[1]) ** 2
    return c[2] + r[2] * math.sqrt(max(0.0, q))

# THE HEAD: round, dog-like -- a domed cranium, a marked STOP down to a SHORT broad muzzle, the puffy WHISKER PADS
# making a W at the front, a small chin; the nose pad dark with its V of nostrils. (A grey seal's coats: the long
# straight "Roman" muzzle with no stop, the nostrils parallel -- `greyseal`)
CR = ([0.655, 0.035, 0], [0.128, 0.102, 0.1])
MZ = ([0.775, -0.012, 0], [0.09, 0.058, 0.062])
MZG = ([0.79, 0.0, 0], [0.12, 0.068, 0.066])
sh += [S("ell", id="cranium", bone="head", c=CR[0], r=CR[1], k=0.04, color=B, pat=PAT),
       {"when": "harbour", "v": S("ell", id="muzzle", bone="head", c=MZ[0], r=MZ[1], k=0.03, color=B, pat=PAT)},
       {"when": "greyseal", "v": S("ell", id="muzzleG", bone="head", c=MZG[0], r=MZG[1], k=0.045, color=B, pat=PAT)},
       {"when": "greyseal", "v": S("ell", id="noseG", bone="head", c=[0.79, 0.038, 0], r=[0.11, 0.035, 0.045], k=0.03, color=B, pat=PAT)},
       S("ell", id="pad", bone="head", c=[0.8, -0.03, 0.032], r=[0.056, 0.043, 0.036], k=0.02, color=B, pat=PAT, mirror=True),
       S("ell", id="chin", bone="head", c=[0.757, -0.07, 0], r=[0.066, 0.028, 0.042], k=0.022, color=B, pat=PAT),
       S("ell", id="cheek", bone="head", c=[0.69, -0.03, 0.06], r=[0.08, 0.06, 0.045], k=0.035, color=B, pat=PAT, mirror=True)]
# (the cleft between the pads under the nose, the mouth's line from it back round the pads)
sh += [S("tube", id="lip", bone="head", pts=[[0.845, -0.068, 0.0, 0.004], [0.83, -0.073, 0.024, 0.004], [0.8, -0.074, 0.045, 0.0035], [0.765, -0.066, 0.058, 0.003]],
         k=0.004, color="@nose", op="sub", mirror=True)]
NX = ell_x(MZ[0], MZ[1], 0.0, 0.0)
sh += [{"when": "harbour", "v": S("ell", id="nose", bone="head", c=[NX - 0.008, 0.004, 0], r=[0.013, 0.017, 0.022], k=0.01, color="@nosepad")},
       {"when": "greyseal", "v": S("ell", id="noseGp", bone="head", c=[0.903, 0.014, 0], r=[0.012, 0.02, 0.024], k=0.01, color="@nosepad")}]
# the NOSTRILS: slits meeting below in a V (harbour), or two near-parallel slits (grey)
sh += [{"when": "harbour", "v": S("tube", id="nostril", bone="head", pts=[[NX + 0.002, 0.018, 0.019, 0.0055], [NX + 0.006, -0.004, 0.006, 0.0045]], k=0.003, color="@nose", op="sub", mirror=True)},
       {"when": "greyseal", "v": S("tube", id="nostrilG", bone="head", pts=[[0.912, 0.03, 0.013, 0.005], [0.917, 0.0, 0.01, 0.0045]], k=0.003, color="@nose", op="sub", mirror=True)}]
# the EAR HOLES: no flap, a small hole behind the eye
EZ = ell_z(CR[0], CR[1], 0.6, 0.045)
sh += [S("sphere", id="ear", bone="head", c=[0.6, 0.045, EZ + 0.004], r=0.0065, k=0.003, color="@nose", op="sub", mirror=True)]

# THE WHISKERS: beaded, pale, in rows on the pads, fanned out and back; two over each eye
ws = []
PADC, PADR = [0.8, -0.03, 0.03], [0.056, 0.043, 0.036]
i = 0
for row, (y, n) in enumerate([(-0.012, 3), (-0.026, 4), (-0.04, 4), (-0.053, 3)]):
    for j in range(n):
        x = 0.832 - 0.014 * j - 0.004 * row
        z = ell_z(PADC, PADR, x, y)
        if z <= PADC[2]: continue
        a = [x, y, z - 0.002]
        dirn = norm([-0.35 - 0.12 * j, -0.12 - 0.08 * row + 0.1, 1.0])
        L = 0.075 + 0.02 * math.sin(i * 1.7) - 0.008 * row
        ws.append(S("cone", id=f"wh{i}", bone="head", a=a, b=add(a, mul(dirn, L)), ra=0.0018, rb=0.0004, k=0, color="@whisker", mirror=True))
        i += 1
for j, dx in enumerate([0.0, -0.014]):
    x, y = 0.712 + dx, 0.093
    z = ell_z(CR[0], CR[1], x, y)
    a = [x, y, z - 0.002]
    ws.append(S("cone", id=f"brow{j}", bone="head", a=a, b=add(a, mul(norm([-0.4, 0.55, 0.75]), 0.05)), ra=0.0014, rb=0.0004, k=0, color="@whisker", mirror=True))
sh += ws

# THE FORE FLIPPERS: short, furred, held against the flank -- a flat paddle from the wrist, back, down and out, the
# five CLAWS along its tip (the arm inside the body: a swelling where it comes out)
sh += [S("ell", id="arm", bone="fflipL", c=[0.31, -0.125, 0.125], r=[0.085, 0.06, 0.05], k=0.045, color=B, pat=PAT, mirror=True)]
FR = [0.3, -0.155, 0.15]
fsd = norm([-0.78, -0.5, 0.36]); fcd = [1.0, -0.15, -0.1]
FL = 0.17
fchord = lambda t: 0.07 + 0.03 * math.sin(math.pi * min(1, t * 0.9)) - 0.03 * max(0, t - 0.8) / 0.2
fthick = lambda t: lerpf(0.04, 0.016, t)
sh += blade("ffl", FR, fsd, fcd, FL, 9, fchord, fthick, lambda t: 0.0, lambda t: "fflipL", B, kc=None, pat=PAT, over=1.4)
for s in sh:
    if s.get("id", "").startswith("ffl"): s["mirror"] = True
u, v, w = frame(fsd, fcd)
for c in range(5):
    t = (c - 2) / 2.0
    tip = add(add(FR, mul(fsd, FL - 0.012)), mul(v, -fchord(0.93) * (0.5 + t * 0.36)))
    sh.append(S("cone", id=f"fclaw{c}", bone="fflipL", a=tip, b=add(tip, mul(norm(add(fsd, mul(w, 0.3))), 0.026 - 0.004 * abs(t))), ra=0.0035, rb=0.0008, k=0.002, color="@claw", mirror=True))

# THE HIND FLIPPERS: pointing straight back, held together (palms facing), each a FAN of five webbed digits in a plane
# near upright (its top leaning out a little), the outer two digits longest so the trailing edge is a crescent; a small
# claw at each digit's tip; the stub of a tail between them
HR = [-0.66, 0.01, 0.017]
hsd = norm([-1.0, 0.04, 0.035])
roll = math.radians(9)
hcd = norm([0.0, math.cos(roll), math.sin(roll)])
hcd = norm(sub(hcd, mul(hsd, dot(hcd, hsd))))
HL = 0.31
def hflip_outline(inset=0.0, rscale=1.0):
    """(u along the span, v across): root to the tip along the bottom (digit 5), the toes, back along the top (digit 1)"""
    half = lambda uu: 0.04 + 0.058 * (uu / HL) ** 1.3
    pts2 = []
    for k in range(7):
        uu = HL * 0.88 * k / 6
        pts2.append((uu, -half(uu)))
    # the toes: tips (u) and webs between
    toes = [(-1.0, HL), (-0.5, HL - 0.03), (0.0, HL - 0.045), (0.5, HL - 0.03), (1.0, HL)]
    hw = half(HL * 0.95)
    for j, (vv, uu) in enumerate(toes):
        pts2.append((uu - 0.008, vv * hw - 0.009 * (1 if vv > 0 else -1 if vv < 0 else 0) * 0))
        pts2.append((uu, vv * hw * 0.97))
        if j < 4:
            nv = toes[j + 1][0]
            pts2.append((min(uu, toes[j + 1][1]) - 0.02, (vv + nv) / 2 * hw))
    for k in range(6, -1, -1):
        uu = HL * 0.88 * k / 6
        pts2.append((uu, half(uu)))
    # (dedupe the first toe point against the edge's end; inset: shrunk toward the mid line and the root)
    out = []
    for uu, vv in pts2:
        uu2 = uu * (1 - inset * 0.25); vv2 = vv * (1 - inset)
        out.append(add(add(HR, mul(hsd, uu2)), mul(hcd, vv2)))
    return out
sh += plates("hfl", [(hflip_outline(0.0), 0.009), (hflip_outline(0.45), 0.02)], "hflipL", B, k=0.008, mirror=True, pat=PAT)
# (the flipper's root rounded into the tail)
sh += [S("ell", id="hroot", bone="hflipL", c=add(HR, mul(hsd, 0.03)), r=[0.06, 0.04, 0.03], k=0.03, color=B, pat=PAT, mirror=True),
       S("ell", id="stub", bone="tail", c=[-0.72, 0.012, 0], r=[0.055, 0.022, 0.026], k=0.02, color=B, pat=PAT)]
hw = 0.04 + 0.058 * 0.95 ** 1.3
for j, vv in enumerate([-1.0, -0.5, 0.0, 0.5, 1.0]):
    uu = [HL, HL - 0.03, HL - 0.045, HL - 0.03, HL][j]
    a = add(add(HR, mul(hsd, uu - 0.01)), mul(hcd, vv * hw * 0.92))
    sh.append(S("cone", id=f"hclaw{j}", bone="hflipL", a=a, b=add(a, mul(hsd, 0.022)), ra=0.0028, rb=0.0007, k=0.002, color="@claw", mirror=True))

for p in sh:
    q = p.get("v", p)
    if q.get("op") != "sub" and q.get("type") != "cone": q["wet"] = 0.07

d = {
    "name": "seal",
    "_about": "SCULPTED (2026-11-06, the sculpt overlay; generator scratchpad sc/sea3/gen/seal.py): a HARBOUR SEAL (Phoca vitulina), 1.7 m nose to tail and its hind flippers 0.25 m more -- a plump spindle with no waist at the neck, the belly a little flattened; a round dog-like head, a domed cranium over a marked stop and a SHORT broad muzzle, the puffy whisker pads making a W at the front, the dark nose with its V-shaped NOSTRILS, big dark eyes, EAR HOLES and no ear flaps, pale beaded whiskers. Short furred FORE FLIPPERS with five claws, held against the flank; the HIND FLIPPERS point back and cannot turn under it, two fans of five webbed digits held palm to palm, the outer digits longest. Its coat a per-pixel pattern (coatpat.js `seal`): grey to brown above, densely spotted dark, paler and sparsely spotted beneath. `coats`: three harbour seals (silver grey, dark, brown) and two GREY SEALS (`greyseal`: the long straight Roman muzzle with no stop, parallel nostrils, blotched instead of spotted -- a dark bull at 1.25x, a pale cow). In the world (haulout.js): groups hauled out on the shore, lying with the head up, now and then galumphing down into the water, swimming, bottling with the head out, and hauling out again.",
    "kind": "parts",
    "facet": False,
    "params": {"harbour": True, "greyseal": False},
    "colors": {"back": os.environ.get("SC", "#77736b"), "nose": "#161413", "nosepad": "#2e2a28", "claw": "#2b2520", "whisker": "#ddd6c8"},
    "coats": [
        {"name": "harbour seal, silver grey"},
        {"name": "harbour seal, silver grey"},
        {"name": "harbour seal, dark", "back": "#4c4a47"},
        {"name": "harbour seal, brown", "back": "#6e604f"},
        {"name": "grey seal, bull", "back": "#4a4b4d", "scale": 1.25, "params": {"harbour": False, "greyseal": True}},
        {"name": "grey seal, cow", "back": "#8b8a86", "scale": 1.1, "params": {"harbour": False, "greyseal": True}},
    ],
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mottle": {"amount": 0},
        "mesh": {"cell": 0.0075, "tris": [10000, 3000], "focus": {"head": 4}, "far": 14},
        "shape": sh,
        "eyes": {"at": [0.722, 0.05, 0.09], "from": [0.68, 0.05, 0], "r": 0.021, "color": "#050505", "iris": "#140d08", "pupil": "round", "lid": False, "sink": 0.42, "socket": 1.05, "bone": "head"},
    },
}
write_to("sea/seal", d)
