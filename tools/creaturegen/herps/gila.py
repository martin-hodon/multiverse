# gila.py -- writes assets/creatures/others/gila-monster.json (2026-11-08): the GILA MONSTER, Heloderma suspectum, a
# venomous lizard of the Sonoran and Mojave deserts, 50 cm long. Run: python3 tools/creaturegen/herps/gila.py (two passes,
# like the wall lizard: the body written bare, its skin probed through sharp/fd.mjs, then the claws, the jaw line, the ear
# slits and the markings laid on it and the file written again).
# The animal: heavy and stout -- a broad, blunt, rounded head on a thick neck nearly as wide, small dark eyes; a broad
# depressed trunk low on short strong sprawled legs, five short thick toes on each foot with sharp curved claws (`horn`s);
# a short FAT tail (its fat store: thick as a sausage nearly to its end, then rounded off blunt). Its skin BEADED (bony
# osteoderms under round bead scales: `scales`), black with pink-salmon: the BANDED form (H. s. cinctum, the base) broad
# black crossbands over the back (their edges ragged, black flecks in the pink between) and black rings round the tail; the
# RETICULATED form (H. s. suspectum) black blotches scattered over the pink, leaving it a broken net; the head, the legs
# and the feet black with a few pink flecks. Paints (colour only): `when: banded` / `when: reticulated`. Variant `young`
# (.4: a hatchling, the bands bright and clean). A slow waddle, the trunk swinging, the heavy tail less.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hlib import *

SP = "others/gila-monster"
OUT = SP + ".json"

Y0 = 0.042
B = [-0.060, Y0, 0]
C = [0.020, Y0, 0]
N = [0.112, Y0 + 0.002, 0]
HD = [0.128, Y0 + 0.003, 0]
TX = [-0.125, -0.170, -0.215, -0.260]
TIP = -0.3065
RT = [(-0.120, .0235), (-0.135, .0226), (-0.160, .0212), (-0.190, .0198), (-0.220, .0180), (-0.250, .0156), (-0.272, .0128),
      (-0.288, .0098), (-0.298, .0068), (-0.3035, .0038), (TIP, .0008)]
YT = [(-0.120, .0405), (-0.140, .0365), (-0.160, .0300), (-0.175, .0245), (-0.185, .0214)]
tr = lambda x: interp(RT, x)
ty = lambda x: interp(YT, x) if x >= -0.185 else tr(x) + 0.0016
FS, FE, FW = [0.095, 0.041, 0.022], [0.090, 0.033, 0.054], [0.105, 0.0075, 0.063]
HH, HK, HA = [-0.110, 0.040, 0.022], [-0.100, 0.035, 0.059], [-0.118, 0.0075, 0.067]
HAND = nrm([math.cos(math.radians(22)), 0, math.sin(math.radians(22))])
FOOT = nrm([math.cos(math.radians(36)), 0, math.sin(math.radians(36))])

parts = rig(B, C, N, HD, TX, TIP, ty, tr, (FS, FE, FW, HH, HK, HA, (0.014, 0.011, 0.0085), (0.016, 0.012, 0.009)),
            body_r=0.024, sw=8, speed=0.55, tail_deg=(6, 7, 8, 9), swing=24, lift=12, head_dir=(0.065, -0.003))

SH = Shapes(); S = SH.S
BD = {"pat": "scales", "frame": frame([0.0, Y0, 0], 0.04)}           # (the beads: round bead scales over the osteoderms)
HB = {"pat": "scales", "frame": frame([0.16, 0.047, 0], 0.03)}
# ---- the HEAD first (its cuts carve only the shapes before them): broad, blunt, rounded; the crown flat-ish, the chin flat
H = "head"
S("headM", type="ell", bone=H, c=[0.157, 0.0475, 0], r=[0.040, 0.0165, 0.0280], k=0.004, color="@head", **HB)
S("jowl", type="ell", bone=H, c=[0.138, 0.0445, 0.0160], r=[0.022, 0.0180, 0.0150], k=0.005, color="@head", mirror=True, **HB)
S("snout", type="ell", bone=H, c=[0.182, 0.0450, 0], r=[0.0190, 0.0125, 0.0195], k=0.004, color="@head", **HB)
S("cutChin", type="box", bone=H, op="sub", c=[0.160, 0.0233, 0], r=[0.05, 0.008, 0.04], rot=[0, 0, 4], k=0.002, color="@jaw", **HB)
S("cutTop", type="box", bone=H, op="sub", c=[0.160, 0.0690, 0], r=[0.05, 0.008, 0.04], rot=[0, 0, -7], k=0.0025, color="@head", **HB)
S("brow", type="ell", bone=H, c=[0.168, 0.0575, 0.0130], r=[0.010, 0.0030, 0.0050], rot=[0, 10, 0], k=0.002, color="@head", mirror=True, **HB)
S("naris", type="sphere", bone=H, op="sub", c=[0.1925, 0.0470, 0.0070], r=0.0016, k=0.0004, color="@mouth", mirror=True)
# ---- neck (thick, nearly as wide as the head), throat; the trunk broad and depressed; belly flat; shoulders, pelvis
S("neck", type="ell", bone="nape", c=[0.117, Y0 + 0.002, 0], r=[0.030, 0.0215, 0.0300], k=0.006, color="@back", **BD)
S("throat", type="ell", bone="nape", c=[0.132, Y0 - 0.006, 0], r=[0.026, 0.0125, 0.0240], k=0.005, color="@jaw", **BD)
S("trunkM", type="ell", c=[-0.015, Y0, 0], r=[0.100, 0.0245, 0.0420], k=0.008, color="@back", **BD)
S("trunkF", type="ell", bone="chest", c=[0.060, Y0 + 0.001, 0], r=[0.058, 0.0238, 0.0380], k=0.008, color="@back", **BD)
S("trunkR", type="ell", c=[-0.090, Y0 - 0.001, 0], r=[0.055, 0.0225, 0.0360], k=0.008, color="@back", **BD)
S("belly", type="ell", c=[-0.015, Y0 - 0.0085, 0], r=[0.120, 0.0155, 0.0400], k=0.007, color="@belly", **BD)
S("shoulders", type="ell", bone="chest", c=[0.095, Y0, 0.020], r=[0.020, 0.0175, 0.016], k=0.006, color="@back", mirror=True, **BD)
S("pelvis", type="ell", c=[-0.110, Y0 - 0.001, 0.019], r=[0.022, 0.0175, 0.016], k=0.006, color="@back", mirror=True, **BD)
# ---- the tail: short and FAT, thick nearly to its end, rounded off blunt
S("tailRoot", type="ell", c=[-0.128, Y0 - 0.003, 0], r=[0.030, 0.021, 0.026], k=0.007, color="@back", **BD)
sweep_tail(S, -0.120, -0.2995, ty, tr, "@back", k=0.006, n=14, end=None, pat="scales", r_frame=0.04)   # (its end rounded off: a hemisphere cap)
# ---- legs: short and strong; flat broad hands and feet, five short thick toes
limb_shapes(S, "legFLu", "legFLl", [0.093, 0.040, 0.016], FE, FW, 0.0145, 0.0112, 0.0096, 0.0086, k=0.005, **BD)
limb_shapes(S, "legHLu", "legHLl", [-0.108, 0.039, 0.016], HK, HA, 0.0165, 0.0122, 0.0102, 0.0090, k=0.006, **BD)
S("thigh", type="ell", bone="legHLu", c=lerp([-0.110, 0.040, 0.022], HK, 0.4), r=[0.020, 0.013, 0.020], rot=[0, -15, 0], k=0.005, color="@limb", mirror=True, **BD)
S("forearmM", type="ell", bone="legFLl", c=lerp(FE, FW, 0.35), r=[0.011, 0.012, 0.010], k=0.004, color="@limb", mirror=True, **BD)
PALM = [FW[0] + HAND[0] * 0.005, 0.0062, FW[2] + HAND[2] * 0.005]
S("palm", type="ell", bone="legFLl", c=PALM, r=[0.0125, 0.0058, 0.0115], rot=[0, -22, 0], k=0.003, color="@limb", mirror=True, **BD)
SOLE = [HA[0] + FOOT[0] * 0.007, 0.0062, HA[2] + FOOT[2] * 0.007]
S("sole", type="ell", bone="legHLl", c=SOLE, r=[0.0150, 0.0062, 0.0125], rot=[0, -36, 0], k=0.003, color="@limb", mirror=True, **BD)
TOES = []
for i, (ang, bang, m, L) in enumerate([(-58, -52, 0.0085, 0.0075), (-28, -25, 0.0105, 0.0100), (-3, -2, 0.0112, 0.0115), (22, 22, 0.0105, 0.0108), (52, 52, 0.0085, 0.0075)]):
    d_ = roty(HAND, ang); base = add([PALM[0], 0.0062, PALM[2]], roty(HAND, bang), m)
    TOES.append(digit(S, f"finger{i + 1}", "legFLl", base, d_, L, 0.0036, 0.0062, 0.0036, col="@limb", **BD))
for i, (ang, bang, m, L) in enumerate([(-52, -46, 0.0095, 0.0080), (-26, -22, 0.0120, 0.0110), (-6, -4, 0.0130, 0.0135), (14, 14, 0.0125, 0.0145), (50, 50, 0.0095, 0.0095)]):
    d_ = roty(FOOT, ang); base = add([SOLE[0], 0.0062, SOLE[2]], roty(FOOT, bang), m)
    TOES.append(digit(S, f"toe{i + 1}", "legHLl", base, d_, L, 0.0039, 0.0062, 0.0038, col="@limb", **BD))

EYE = {"at": [0.171, 0.0545, 0.0185], "from": [0.170, 0.0520, 0], "r": 0.0036, "color": "@eyeDark", "iris": "@eye", "pupil": "round", "lid": "@head", "sink": 0.62, "socket": 1.05}
COLORS = {"back": "#e0846a", "head": "#1e1a18", "jaw": "#2a2220", "limb": "#221d1b", "belly": "#8a5a4c", "black": "#1c1816", "pink": "#e88a6c",
          "claw": "#2e2824", "mouth": "#120e0c", "eye": "#2e1e14", "eyeDark": "#0a0706"}
RETIC = {"back": "#e07c5a", "pink": "#e4845e", "belly": "#8e5e48"}
YOUNG = {"back": "#f29a7a", "pink": "#f4a080", "belly": "#a06a58"}
d = {
    "name": "gila monster",
    "_about": "SCULPTED (2026-11-08, tools/creaturegen/herps/gila.py): the GILA MONSTER, Heloderma suspectum, 50 cm. Heavy and "
              "stout: a broad blunt rounded head on a thick neck nearly as wide, small dark eyes; a broad depressed trunk low on "
              "short strong sprawled legs, five short thick toes on each foot with sharp curved claws (`horn`s); a short FAT tail (one `sweep` along its four links) "
              "(its fat store), thick nearly to its end and rounded off blunt. BEADED skin (the osteoderms' bead scales: "
              "`scales`), black and pink-salmon (paints, colour only): the BANDED form (H. s. cinctum, base) broad black "
              "crossbands over the back with ragged edges, black flecks in the pink between, black rings round the tail; the "
              "RETICULATED form (H. s. suspectum) black blotches scattered over the pink, leaving a broken net; head, legs and "
              "feet black with a few pink flecks. Coats: banded, reticulated (`when: banded` / `reticulated`); variant `young` "
              "(.4, a hatchling: the bands bright and clean). A slow waddle, the trunk swinging, the heavy tail less.",
    "kind": "parts",
    "flags": {"print": "none", "legLen": 0.035, "shy": 1.5},
    "colors": COLORS,
    "params": {"banded": True, "reticulated": False},
    "coats": [{"name": "banded"}, {"name": "reticulated", "params": {"banded": False, "reticulated": True}, "colors": RETIC}],
    "variants": {"banded": {"params": {}, "colors": {}},
                 "reticulated": {"params": {"banded": False, "reticulated": True}, "colors": RETIC},
                 "young": {"scale": 0.4, "params": {}, "colors": YOUNG}},
    "parts": parts,
    "sculpt": {
        "keep": [],
        "paint": 0.3,
        "mesh": {"cell": 0.001, "tris": [12000, 3200], "anchor": 0, "symmetric": True, "focus": {"head": 3, "legFLl": 1.6, "legHLl": 1.6}},
        "shape": SH,
        "eyes": EYE,
    },
}

# ================= pass 2: on the probed skin
def bone_at(x):
    if x > 0.127: return "head"
    if x > 0.110: return "nape"
    if x > 0.020: return "chest"
    if x > TX[0]: return "body"
    return "caud" + str(1 + sum(1 for t in TX[1:] if x < t))

def axis(x):
    if x > 0.128: return [x, 0.046, 0]
    if x > -0.118: return [x, Y0, 0]
    return [x, ty(x), 0]

def rad(x):
    if x > -0.118: return 0.03
    return tr(x)

def grooves():
    """the jaw line round the snout and back under the eye to the jowl; the ear slit behind it"""
    out = []
    o = [0.150, 0.0385, 0]
    angs = [3 + 3.6 * j for j in range(26)]
    hits = rays_hits(SP, SH, [[o, add(o, [math.cos(math.radians(a)), -0.02, math.sin(math.radians(a))], 0.08)] for a in angs])
    # (and back along the side under the eye)
    xs = [0.146 - 0.0032 * j for j in range(5)]
    hits += rays_hits(SP, SH, [[[x, 0.0385 + 0.0012 * j, 0], [x, 0.0385 + 0.0012 * j, 0.06]] for j, x in enumerate(xs)])
    ok = [h for h in hits if h]; ns = normals(SP, SH, ok, h=0.0005)
    # (one groove: a thin tube carved along the skin points, its axis a little inside the skin)
    pts = [add(h, n, -0.0002) + [0.0011] for h, n in zip(ok, ns)]
    pts.sort(key=lambda p: -p[0])
    out.append({"id": "jaw", "type": "tube", "bone": "head", "op": "sub", "pts": pts, "k": 0.0011 * 0.5, "color": "@mouth", "mirror": True})
    e = rays_hits(SP, SH, [[[0.128, 0.0465, 0], [0.128, 0.0465, 0.06]]])[0]
    out.append({"id": "ear", "type": "ell", "bone": "head", "op": "sub", "c": e, "r": [0.0022, 0.0040, 0.0020], "rot": [0, 0, -15], "k": 0.0006, "color": "@mouth", "mirror": True})
    return out

def markings():
    P = Painter(SP, SH)
    rng = random.Random(7)
    # BANDED: broad black crossbands over the back, ragged; black rings round the tail; black flecks in the pink
    BANDS = [(0.100, 0.032), (0.034, 0.022), (-0.030, 0.022), (-0.094, 0.022), (-0.150, 0.015), (-0.193, 0.014), (-0.236, 0.014), (-0.284, 0.022)]
    for bi, (xc, hw) in enumerate(BANDS):
        tail = xc < -0.125
        phis = range(-150, 151, 25) if tail else range(-115, 116, 18)
        for phi in phis:
            sg = 1 if phi >= 0 else -1
            x = xc + rng.uniform(-0.25, 0.25) * hw
            la = hw * rng.uniform(0.8, 1.15); lr = (0.012 if not tail else 0.45 * tr(xc)) * rng.uniform(0.9, 1.3)
            P.mark(f"band{bi}_{phi + 200}", axis(x), ring_dir(abs(phi), sg), la, lr, "@black", bone_at(x), when="banded")
    # (black flecks in the pink bands, pink flecks in the black)
    for bi in range(len(BANDS) - 1):
        xa = BANDS[bi][0] - BANDS[bi][1]; xb = BANDS[bi + 1][0] + BANDS[bi + 1][1]
        if xa - xb < 0.012: continue
        for j in range(4 if xb > -0.125 else 2):
            x = rng.uniform(xb + 0.004, xa - 0.004); phi = rng.uniform(-80, 80)
            P.mark(f"fleck{bi}_{j}", axis(x), ring_dir(abs(phi), 1 if phi >= 0 else -1), 0.0045 * rng.uniform(.7, 1.2), 0.004 * rng.uniform(.7, 1.2), "@black", bone_at(x), when="banded")
    for bi, (xc, hw) in enumerate(BANDS[:4]):
        for j in range(2):
            x = xc + rng.uniform(-0.5, 0.5) * hw; phi = rng.uniform(-60, 60)
            P.mark(f"pfl{bi}_{j}", axis(x), ring_dir(abs(phi), 1 if phi >= 0 else -1), 0.0035, 0.003, "@pink", bone_at(x), when="banded")
    # RETICULATED: black blotches scattered over the pink (a jittered grid), the pink left as a broken net
    x = 0.120; row = 0
    while x > -0.300:
        tail = x < -0.125
        step = 24 if not tail else 40
        for phi in range(-120 if not tail else -150, 121 if not tail else 151, step):
            ph = phi + rng.uniform(-0.3, 0.3) * step + (step / 2 if row % 2 else 0)
            if abs(ph) > (125 if not tail else 160): continue
            xx = x + rng.uniform(-0.004, 0.004)
            sz = (0.0085 if not tail else 0.36 * tr(xx)) * rng.uniform(0.75, 1.25)
            blotch(P, f"ret{row}_{int(ph) + 200}", axis(xx), ring_dir(abs(ph), 1 if ph >= 0 else -1), sz, "@black", bone_at(xx), rng, rad(xx), n=2, when="reticulated", elong=1.15)
        x -= 0.0175 if not tail else 0.020; row += 1
    S_ = None
    # the head's and the legs' pink flecks (every coat)
    for sg, S_ in ((1, "L"), (-1, "R")):
        for j in range(3):
            x = rng.uniform(0.135, 0.165); phi = rng.uniform(10, 60)
            P.mark(f"hfl{S_}{j}", axis(x), ring_dir(phi, sg), 0.0030, 0.0025, "@pink", "head")
        for nm, a_, b_, bone in (("arm", [0.093, 0.040, 0.016], FE, "legF" + S_ + "u"), ("thigh", [-0.108, 0.039, 0.016], HK, "legH" + S_ + "u")):
            for j in range(2):
                m = lerp(a_, b_, 0.35 + 0.35 * j); m = [m[0] + rng.uniform(-0.004, 0.004), m[1], m[2] * sg]
                P.mark(f"{nm}{S_}{j}", m, [0, 1, 0.3 * sg], 0.0045, 0.0038, "@pink", bone)
    return P.lay(0.12)

if __name__ == "__main__":
    dump(OUT, d)                                       # (pass 1: the body bare, to be probed)
    index_add(["creatures/" + SP], after_prefix="creatures/others/")
    sh2 = claws(SP, SH, TOES, 0.0058, 0.0004, bend=0.25) + grooves() + markings()
    SH += sh2
    dump(OUT, d)
    print(len(SH), "shapes,", len(sh2), "pass 2")
