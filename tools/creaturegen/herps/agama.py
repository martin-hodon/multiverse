# agama.py -- writes assets/creatures/others/agama.json (2026-11-08): the RAINBOW (red-headed) AGAMA, Agama agama, a West
# African agamid, 28 cm long, the tail 60% of it. Run: python3 tools/creaturegen/herps/agama.py (two passes, like the wall
# lizard: the body written bare, its skin probed through sharp/fd.mjs, then the crest, the claws, the ear openings and the
# markings laid on it and the file written again). Listed in assets/index.json (fd.mjs loads it from there).
# The animal: a triangular head, broad at the jowls and distinct from the neck, pointed to a blunt snout; a small nuchal
# crest (a `fin`, serrated) behind it; a slender depressed trunk carried HIGH on long thin legs (the upper bones out and
# down, the knees above the hips: it stands more upright than the wall lizard), the chest raised; five long thin toes on
# each foot (the hind 4th the longest) each with a small curved claw (`horn`); a long round tail tapering to a whip-thin
# point, lying on the ground behind the hips. Skin: fine keeled scales (`rowscales` in one frame for the whole body).
# Coats: the dominant MALE's breeding dress (the base) -- the head and nape bright orange-red, the body and legs deep
# indigo blue, the tail blue at its root, then a pale band, then orange, then a dark tip (the tail ONE `sweep` with colour `bands`); the FEMALE's --
# olive-brown, rows of pale spots down the back, orange patches on the flanks (paints `when: female`), the tail's bands
# faint; variant `juvenile` (.45, the female's dress, paler).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hlib import *

SP = "others/agama"
OUT = SP + ".json"

YB = lambda x: 0.0185 + 0.055 * x            # the trunk's axis: the chest raised
B = [-0.016, YB(-0.016), 0]                  # body (the root): the rear trunk
C = [0.004, YB(0.004), 0]                    # chest: the front trunk
N = [0.039, 0.0222, 0]                       # nape
HD = [0.047, 0.0240, 0]                      # head: its pivot behind the skull
TX = [-0.030, -0.070, -0.110, -0.150]        # caud1..4 roots
TIP = -0.205
RT = [(-0.026, .0050), (-0.034, .0046), (-0.045, .0040), (-0.06, .0033), (-0.08, .0026), (-0.10, .0020), (-0.12, .0016),
      (-0.14, .00128), (-0.16, .00100), (-0.18, .00075), (-0.195, .00056), (-0.201, .00046), (TIP, .00034)]   # (its tip kept visible: rounded off at .3 mm)
YT = [(-0.026, .0165), (-0.036, .0152), (-0.048, .0118), (-0.060, .0080), (-0.072, .0050)]
tr = lambda x: interp(RT, x)
ty = lambda x: interp(YT, x) if x >= -0.072 else tr(x) + 0.0002
FS, FE, FW = [0.034, 0.0205, 0.0060], [0.030, 0.0118, 0.0142], [0.0355, 0.0025, 0.0170]      # shoulder, elbow, wrist
HH, HK, HA = [-0.027, 0.0175, 0.0060], [-0.018, 0.0185, 0.0235], [-0.025, 0.0025, 0.0265]  # hip, knee, ankle
HAND = nrm([math.cos(math.radians(25)), 0, math.sin(math.radians(25))])
FOOT = nrm([math.cos(math.radians(38)), 0, math.sin(math.radians(38))])

parts = rig(B, C, N, HD, TX, TIP, ty, tr, (FS, FE, FW, HH, HK, HA, (0.0021, 0.0015, 0.0010), (0.0030, 0.0018, 0.0011)),
            body_r=0.0072, sw=7, speed=1.0, tail_deg=(9, 11, 13, 15), swing=28, lift=16, head_dir=(0.028, -0.002))

SH = Shapes(); S = SH.S
FR = {"pat": "rowscales", "frame": frame([0.0, 0.0185, 0], 0.016)}        # (keeled scales .8 mm along; one frame for all)
HFR = {"pat": "rowscales", "frame": frame([0.06, 0.0255, 0], 0.010)}       # (the head's finer, .5 mm)

# ---- the HEAD first (its cuts carve only the shapes before them): one ellipsoid, the jowls, then cut flat on top and
# below and sliced back from the snout each side -- from above a triangle broad at the jowls, in profile a wedge
H = "head"
S("headM", type="ell", bone=H, c=[0.0605, 0.0262, 0], r=[0.0150, 0.0068, 0.0082], k=0.0012, color="@head", **HFR)
S("jowl", type="ell", bone=H, c=[0.0520, 0.0242, 0.0048], r=[0.0062, 0.0057, 0.0040], k=0.0015, color="@head", mirror=True, **HFR)
S("cutTop", type="box", bone=H, op="sub", c=[0.0620, 0.0344, 0], r=[0.016, 0.004, 0.012], rot=[0, 0, -16], k=0.0007, color="@head", **HFR)
S("cutChin", type="box", bone=H, op="sub", c=[0.0620, 0.0172, 0], r=[0.016, 0.004, 0.012], rot=[0, 0, 6], k=0.0006, color="@head", **HFR)
S("cutSide", type="box", bone=H, op="sub", c=[0.0692, 0.0255, 0.0091], r=[0.011, 0.008, 0.005], rot=[0, 14, 0], k=0.0007, color="@head", mirror=True, **HFR)
S("cutBevel", type="box", bone=H, op="sub", c=[0.0600, 0.0321, 0.0073], r=[0.016, 0.003, 0.006], rot=[45, 0, 0], k=0.0007, color="@head", mirror=True, **HFR)
S("brow", type="ell", bone=H, c=[0.0640, 0.0298, 0.0047], r=[0.0042, 0.0011, 0.0017], rot=[0, 8, 0], k=0.0008, color="@head", mirror=True, **HFR)
S("naris", type="sphere", bone=H, op="sub", c=[0.0735, 0.0262, 0.0020], r=0.00035, k=0.0001, color="@mouth", mirror=True)
h_end = len(SH)
# ---- neck and throat; the trunk depressed, widest at mid-back; the shoulders and the pelvis; a flat belly
S("neck", type="ell", bone="nape", c=[0.0425, 0.0226, 0], r=[0.0090, 0.0058, 0.0062], k=0.0018, color="@nape", **FR)
S("throat", type="ell", bone="nape", c=[0.0470, 0.0207, 0], r=[0.0085, 0.0040, 0.0055], k=0.0015, color="@throat", **FR)
S("trunkM", type="ell", c=[0.002, YB(0.002), 0], r=[0.024, 0.0074, 0.0098], k=0.0022, color="@back", **FR)
S("trunkF", type="ell", bone="chest", c=[0.024, YB(0.024), 0], r=[0.016, 0.0070, 0.0088], k=0.0022, color="@back", **FR)
S("trunkR", type="ell", c=[-0.020, YB(-0.020), 0], r=[0.016, 0.0066, 0.0085], k=0.0022, color="@back", **FR)
S("shoulders", type="ell", bone="chest", c=[0.033, YB(0.033) + 0.0004, 0], r=[0.0080, 0.0064, 0.0080], k=0.0018, color="@back", **FR)
S("pelvis", type="ell", c=[-0.029, YB(-0.029), 0], r=[0.0090, 0.0060, 0.0072], k=0.0018, color="@back", **FR)
S("belly", type="ell", c=[0.0, YB(0.0) - 0.0028, 0], r=[0.030, 0.0045, 0.0088], k=0.0018, color="@belly", **FR)
# ---- the tail: round, thick at the root behind the vent, falling to the ground, whip-thin to its point
S("tailRoot", type="ell", c=[-0.031, 0.0162, 0], r=[0.009, 0.0050, 0.0058], k=0.0018, color="@back", **FR)
sweep_tail(S, -0.026, TIP, ty, tr, "@back", k=0.0015, n=22, pat="rowscales", r_frame=0.005, end=None,   # (the scales drawn for the tail's own girth)
           bands=[(-0.052, -0.078, "@tailPale"), (-0.078, -0.140, "@tailOrange"), (-0.140, TIP, "@tailDark")], bandEdge=0.0004)
# ---- legs: long and slender; the hands and feet flat on the ground
limb_shapes(S, "legFLu", "legFLl", [0.033, 0.0203, 0.0050], FE, FW, 0.0022, 0.0014, 0.0011, 0.0009, k=0.0012, **FR)
limb_shapes(S, "legHLu", "legHLl", [-0.027, 0.0175, 0.0050], HK, HA, 0.0033, 0.0017, 0.0013, 0.0009, k=0.0015, **FR)
S("thigh", type="ell", bone="legHLu", c=lerp([-0.027, 0.0175, 0.0060], HK, 0.35), r=[0.0045, 0.0030, 0.0055], rot=[0, -25, 0], k=0.0012, color="@limb", mirror=True, **FR)
PALM = [FW[0] + HAND[0] * 0.0012, 0.0011, FW[2] + HAND[2] * 0.0012]
S("palm", type="ell", bone="legFLl", c=PALM, r=[0.0022, 0.0007, 0.0014], rot=[0, -25, 0], k=0.0008, color="@limb", mirror=True, **FR)
SOLE = [HA[0] + FOOT[0] * 0.0028, 0.0011, HA[2] + FOOT[2] * 0.0028]
S("sole", type="ell", bone="legHLl", c=SOLE, r=[0.0042, 0.0008, 0.0017], rot=[0, -38, 0], k=0.0008, color="@limb", mirror=True, **FR)
S("heel", type="ell", bone="legHLl", c=[HA[0], 0.0016, HA[2]], r=[0.0014, 0.0012, 0.0013], k=0.0008, color="@limb", mirror=True)
TOES = []
for i, (ang, bang, m, L) in enumerate([(-55, -50, 0.0012, 0.0030), (-26, -22, 0.0017, 0.0045), (-2, 0, 0.0019, 0.0056), (22, 22, 0.0017, 0.0058), (52, 55, 0.0012, 0.0036)]):
    d_ = roty(HAND, ang); base = add([PALM[0], 0.0011, PALM[2]], roty(HAND, bang), m)
    TOES.append(digit(S, f"finger{i + 1}", "legFLl", base, d_, L, 0.00034, 0.0011, 0.00032))
for i, (ang, bang, m, L) in enumerate([(-38, -32, 0.0030, 0.0042), (-20, -14, 0.0036, 0.0062), (-6, -2, 0.0040, 0.0085), (9, 10, 0.0038, 0.0112), (58, 62, 0.0014, 0.0060)]):
    d_ = roty(FOOT, ang); base = add([SOLE[0], 0.0011, SOLE[2]], roty(FOOT, bang), m)
    TOES.append(digit(S, f"toe{i + 1}", "legHLl", base, d_, L, 0.00034, 0.0011, 0.00032))
# (the head's shapes first: its cuts carve only them)


EYE = {"at": [0.0645, 0.0285, 0.0058], "from": [0.0645, 0.0280, 0], "r": 0.0017, "color": "@eyeDark", "iris": "@eye", "pupil": "round", "lid": "@head", "sink": 0.62, "socket": 1.05}
COLORS = {"head": "#e0541c", "nape": "#d8501e", "throat": "#e88a2c", "crest": "#d04418", "back": "#232f80", "belly": "#34448c", "limb": "#2a3884",
          "toe": "#3c4c96", "claw": "#1c1814", "tailPale": "#d6dade", "tailOrange": "#e0782a", "tailDark": "#26221e", "spot": "#2a3a8e",
          "flank": "#2a3888", "lip": "#9a3014", "mouth": "#2a1a12", "ear": "#3a1a10", "eye": "#b0661c", "eyeDark": "#140c08"}
FEMALE = {"head": "#7c6c48", "nape": "#76674a", "throat": "#cfc2a2", "crest": "#6e6044", "back": "#6c5c40", "belly": "#d6caac", "limb": "#685a40",
          "toe": "#7a6c52", "tailPale": "#8c7c5c", "tailOrange": "#7e6c4c", "tailDark": "#4e4232", "spot": "#d8cca0", "flank": "#d88a3c",
          "lip": "#4e4230", "ear": "#3a3024", "eye": "#9a6a2a"}
YOUNG = dict(FEMALE, **{"head": "#86764e", "back": "#76664a", "spot": "#e2d8b0", "flank": "#d89a4c", "tailPale": "#9a8a6a"})
d = {
    "name": "agama",
    "_about": "SCULPTED (2026-11-08, tools/creaturegen/herps/agama.py): the RAINBOW (red-headed) AGAMA, Agama agama, 28 cm long, "
              "the tail 60% of it. A triangular head broad at the jowls and distinct from the neck, cut flat on top and below and "
              "sliced back to a blunt snout; a small serrated nuchal crest (a `fin`); a slender depressed trunk carried high on "
              "long thin legs, the chest raised, the knees above the hips (more upright than the wall lizard); five long thin toes "
              "on each foot (the hind 4th the longest), each with a small curved claw (`horn`); a long round tail lying on the "
              "ground, tapering to a whip-thin point; fine keeled scales (`rowscales`). Its walk: the trunk and tail swing side "
              "to side (chest, nape against it, the tail's four links a beat apart, faded standing), the legs sweep and lift. "
              "Coats: the dominant MALE's breeding dress (base) -- head and nape bright orange-red, body and legs deep indigo "
              "blue, the tail blue at its root, then a pale band, orange, a dark tip (the tail one `sweep` along caud1..4, its colour `bands`); the FEMALE -- olive-brown, "
              "rows of pale spots down the back, orange patches on the flanks (paints, `when: female`), the tail's bands faint. "
              "Variants: male, female, juvenile (.45, the female's dress, paler).",
    "kind": "parts",
    "flags": {"print": "none", "legLen": 0.02, "shy": 3, "graze": -0.25, "nodPivot": sub(HD, N)},
    "colors": COLORS,
    "params": {"male": True, "female": False},
    "coats": [{"name": "male"}, {"name": "male"}, {"name": "female", "params": {"male": False, "female": True}, "colors": FEMALE}],
    "variants": {"male": {"params": {}, "colors": {}},
                 "female": {"params": {"male": False, "female": True}, "colors": FEMALE},
                 "juvenile": {"scale": 0.45, "params": {"male": False, "female": True}, "colors": YOUNG}},
    "parts": parts,
    "sculpt": {
        "keep": [],
        "paint": 0.2,
        "mesh": {"cell": 0.00045, "tris": [9000, 2800], "anchor": 0, "symmetric": True, "focus": {"head": 3, "legFLl": 2, "legHLl": 2, "caud1": 3, "caud2": 3}},
        "shape": SH,
        "eyes": EYE,
    },
}

# ================= pass 2: on the probed skin
def bone_at(x):
    if x > 0.0465: return "head"
    if x > 0.037: return "nape"
    if x > 0.004: return "chest"
    if x > TX[0]: return "body"
    return "caud" + str(1 + sum(1 for t in TX[1:] if x < t))

def axis(x):
    if x > 0.047: return [x, 0.0255, 0]
    if x > 0.037: return [x, 0.0222, 0]
    if x > -0.026: return [x, YB(x), 0]
    return [x, ty(x), 0]

def crest():
    """the nuchal crest: a low serrated sheet on the midline over the nape"""
    T = back_table(SP, SH, [round(0.052 - 0.001 * k, 4) for k in range(26)], 0.02, 0.04)
    top = lambda x: interp(T, x)
    XF, XR = 0.0495, 0.031
    hs = [0.0016, 0.0021, 0.0022, 0.0020, 0.0017, 0.0014, 0.0011, 0.0008]
    xs = [XF + (XR - XF) * i / (len(hs) - 1) for i in range(len(hs))]
    root = [[x, top(x) - 0.0006, 0] for x in [XR - 0.001 + (XF - XR + 0.002) * k / 6 for k in range(7)]]
    edge = [[XR - 0.0008, top(XR - 0.0008) + 0.0002, 0, 1.0]]; corners = []
    tips = [[x - 0.0006 * h / 0.002, top(x) + h, 0] for x, h in zip(xs, hs)]
    rev = list(reversed(tips))
    for k, tp in enumerate(rev):
        if k:
            a = rev[k - 1]; q = lerp(a, tp, 0.5); q[1] = min(a[1], tp[1]) - 0.45 * min(a[1] - top(a[0]), tp[1] - top(tp[0]))
            edge.append(q[:3] + [1.0])
        corners.append(len(edge)); edge.append(tp[:3] + [1.0])
    edge.append([XF + 0.0008, top(XF + 0.0008) + 0.0002, 0, 1.0])
    return [{"id": "crest", "type": "fin", "bone": "nape", "root": root, "edge": edge, "corners": corners, "thick": 0.00045, "slope": 0.35,
             "fair": {"r": 0.0005, "rows": 3}, "color": "@crest", "n": 90, "across": 4}]

def markings():
    P = Painter(SP, SH)
    # the head's colour down over the nape and onto the shoulders (male: the red reaches the forelegs' roots)
    # the lip line: a thin dark line along the jaw margin each side
    for j in range(13):
        x = 0.051 + 0.0019 * j; y = 0.0228 + 0.00012 * (x - 0.052) / 0.003
        P.mark(f"lip{j}", [x, y, 0], [0, -0.05, 1], 0.0021, 0.00016, "@lip", "head", depth=0.0004, k=0.00005, kc=0.00008, mirror=True)
    # the FEMALE's: pale spots in two rows down each side of the back, orange patches on the flanks
    rng = random.Random(11)
    for sg, S_ in ((1, "L"), (-1, "R")):
        for j, x in enumerate([0.030, 0.021, 0.012, 0.003, -0.006, -0.015, -0.024]):
            for row, phi in enumerate((28, 58)):
                xx = x + rng.uniform(-0.0015, 0.0015) + (0.0045 if row else 0)
                P.mark(f"spot{S_}{j}{row}", axis(xx), ring_dir(phi + rng.uniform(-6, 6), sg), 0.0013 * rng.uniform(.8, 1.2), 0.0011 * rng.uniform(.8, 1.2),
                       "@spot", bone_at(xx), when="female")
        for j, x in enumerate([0.026, 0.014, 0.002, -0.010]):
            blotch(P, f"flank{S_}{j}", axis(x + rng.uniform(-0.002, 0.002)), ring_dir(88 + rng.uniform(-6, 6), sg), 0.0030, "@flank", bone_at(x), rng, 0.009, n=3, when="female", elong=1.4)
    out = P.lay(0.05)
    # the ear openings: a hollow behind the jowl each side
    e = rays_hits(SP, SH, [[[0.0505, 0.0262, 0], [0.0505, 0.0262, 0.02]]])[0]
    out.append({"id": "ear", "type": "sphere", "bone": "head", "op": "sub", "c": [e[0], e[1], e[2] + 0.0004], "r": 0.0011, "k": 0.0002, "color": "@ear", "mirror": True})
    return out

if __name__ == "__main__":
    dump(OUT, d)                                       # (pass 1: the body bare, to be probed)
    index_add(["creatures/" + SP], after_prefix="creatures/others/")
    sh2 = crest() + claws(SP, SH, TOES, 0.0017, 0.0001, bend=0.2) + markings()
    SH += sh2
    dump(OUT, d)
    print(len(SH), "shapes,", len(sh2), "pass 2")
