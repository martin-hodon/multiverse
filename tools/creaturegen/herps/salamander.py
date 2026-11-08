# salamander.py -- writes assets/creatures/others/fire-salamander.json (2026-11-08): the FIRE SALAMANDER, Salamandra
# salamandra, a European urodele amphibian, 20 cm long (the tail a little shorter than the body). Run: python3
# tools/creaturegen/herps/salamander.py (two passes, like the wall lizard: the body written bare, its skin probed through
# sharp/fd.mjs, then the jaw line, the costal grooves and the markings laid on it and the file written again).
# The animal: stout and rounded -- a broad, flat, rounded head with a blunt snout, big black protruding eyes, the PAROTOID
# glands bulging behind them (kidney-shaped, diverging backward); a thick round trunk with shallow costal grooves down the
# flanks; short sturdy sprawled legs with four blunt fingers in front and five toes behind (no claws: round tips); a tail
# round in section, thick at the root and tapering to a blunt point, shorter than the body, lying on the ground. Its skin
# smooth and WET (`wet`: the shine), glossy black with bright yellow blotches (paints): over the eyelids and the
# parotoids, two irregular rows down the back, a few on the flanks, one on each upper leg, two rows down the tail.
# Coats: spotted yellow (base), striped yellow (S. s. terrestris / fastuosa: two continuous wavy dorsolateral stripes
# from the parotoids onto the tail -- `when: striped`), and the rare orange-red one (the spots red-orange). Its walk
# slow, the trunk and tail swinging well side to side.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hlib import *

SP = "others/fire-salamander"
OUT = SP + ".json"

Y0 = 0.0125
B = [-0.018, Y0, 0]
C = [0.010, Y0, 0]
N = [0.039, Y0, 0]
HD = [0.045, Y0 + 0.0005, 0]
TX = [-0.040, -0.062, -0.084, -0.106]
TIP = -0.1345
RT = [(-0.036, .0074), (-0.042, .0071), (-0.050, .0066), (-0.065, .0058), (-0.080, .0050), (-0.095, .0042), (-0.108, .0034),
      (-0.118, .0026), (-0.125, .0019), (-0.130, .0012), (-0.1333, .0006), (TIP, .00005)]
YT = [(-0.036, Y0 - 0.0005), (-0.044, Y0 - 0.0016), (-0.054, .0092), (-0.066, .0070), (-0.078, .0055)]
tr = lambda x: interp(RT, x)
ty = lambda x: interp(YT, x) if x >= -0.078 else tr(x) + 0.0002
FS, FE, FW = [0.031, 0.0120, 0.0075], [0.0285, 0.0095, 0.0160], [0.0340, 0.0024, 0.0185]
HH, HK, HA = [-0.036, 0.0118, 0.0075], [-0.0325, 0.0105, 0.0175], [-0.0390, 0.0024, 0.0200]
HAND = nrm([math.cos(math.radians(20)), 0, math.sin(math.radians(20))])
FOOT = nrm([math.cos(math.radians(35)), 0, math.sin(math.radians(35))])

parts = rig(B, C, N, HD, TX, TIP, ty, tr, (FS, FE, FW, HH, HK, HA, (0.0030, 0.0023, 0.0018), (0.0036, 0.0026, 0.0019)),
            body_r=0.0085, sw=12, speed=0.7, tail_deg=(12, 14, 16, 18), swing=30, lift=12, head_dir=(0.021, -0.001))

SH = Shapes(); S = SH.S
W = {"wet": 0.45}
# ---- the HEAD first (its cuts carve only the shapes before them): broad, flat, rounded, a blunt snout; the chin flat
H = "head"
S("headM", type="ell", bone=H, c=[0.0525, 0.0135, 0], r=[0.0130, 0.0058, 0.0092], k=0.0012, color="@head", **W)
S("snout", type="ell", bone=H, c=[0.0595, 0.0128, 0], r=[0.0068, 0.0046, 0.0070], k=0.0015, color="@head", **W)
S("cheek", type="ell", bone=H, c=[0.0480, 0.0120, 0.0050], r=[0.0070, 0.0050, 0.0045], k=0.0015, color="@head", mirror=True, **W)
S("cutChin", type="box", bone=H, op="sub", c=[0.0540, 0.0044, 0], r=[0.016, 0.004, 0.014], rot=[0, 0, 4], k=0.0008, color="@head", **W)
S("naris", type="sphere", bone=H, op="sub", c=[0.0650, 0.0140, 0.0024], r=0.00035, k=0.0001, color="@mouth", mirror=True)
h_end = len(SH)
# ---- the parotoids: kidney-shaped glands bulging on the head's top-sides behind the eyes, diverging backward
S("parotoid", type="ell", bone=H, c=[0.0440, 0.0172, 0.0060], r=[0.0066, 0.0034, 0.0038], rot=[0, -12, 6], k=0.0010, color="@head", mirror=True, **W)
S("parotoidB", type="ell", bone="nape", c=[0.0395, 0.0166, 0.0064], r=[0.0045, 0.0029, 0.0033], rot=[0, -12, 0], k=0.0010, color="@head", mirror=True, **W)
S("lidUp", type="ell", bone=H, c=[0.0555, 0.0168, 0.0052], r=[0.0030, 0.0016, 0.0024], k=0.0008, color="@head", mirror=True, **W)
# ---- neck, trunk (thick, round), belly; shoulders and pelvis
S("neck", type="ell", bone="nape", c=[0.0405, Y0 + 0.0004, 0], r=[0.0095, 0.0072, 0.0088], k=0.0018, color="@back", **W)
S("throat", type="ell", bone="nape", c=[0.0455, 0.0105, 0], r=[0.0085, 0.0045, 0.0075], k=0.0016, color="@belly", **W)
S("trunkM", type="ell", c=[-0.002, Y0, 0], r=[0.032, 0.0080, 0.0102], k=0.0022, color="@back", **W)
S("trunkF", type="ell", bone="chest", c=[0.024, Y0 + 0.0002, 0], r=[0.017, 0.0079, 0.0098], k=0.0022, color="@back", **W)
S("trunkR", type="ell", c=[-0.029, Y0 - 0.0002, 0], r=[0.016, 0.0076, 0.0094], k=0.0022, color="@back", **W)
S("belly", type="ell", c=[-0.002, Y0 - 0.0028, 0], r=[0.036, 0.0056, 0.0096], k=0.0020, color="@belly", **W)
S("shoulders", type="ell", bone="chest", c=[0.031, Y0, 0.0050], r=[0.0060, 0.0060, 0.0045], k=0.0018, color="@back", mirror=True, **W)
S("pelvis", type="ell", c=[-0.036, Y0 - 0.0004, 0.0048], r=[0.0065, 0.0058, 0.0045], k=0.0018, color="@back", mirror=True, **W)
# ---- the tail: round, thick at the root, lying on the ground, a blunt point
S("tailRoot", type="ell", c=[-0.041, Y0 - 0.0012, 0], r=[0.009, 0.0068, 0.0076], k=0.0018, color="@back", **W)
sweep_tail(S, -0.036, TIP, ty, tr, "@back", k=0.0018, n=18, **W)
# ---- the legs: short and sturdy, the hands and feet flat; four blunt fingers, five toes
limb_shapes(S, "legFLu", "legFLl", [0.030, 0.0118, 0.0060], FE, FW, 0.0031, 0.0024, 0.0020, 0.0017, k=0.0014, **W)
limb_shapes(S, "legHLu", "legHLl", [-0.035, 0.0116, 0.0060], HK, HA, 0.0038, 0.0027, 0.0021, 0.0018, k=0.0016, **W)
PALM = [FW[0] + HAND[0] * 0.0012, 0.0012, FW[2] + HAND[2] * 0.0012]
S("palm", type="ell", bone="legFLl", c=PALM, r=[0.0028, 0.0010, 0.0024], rot=[0, -20, 0], k=0.0010, color="@limb", mirror=True, **W)
SOLE = [HA[0] + FOOT[0] * 0.0018, 0.0012, HA[2] + FOOT[2] * 0.0018]
S("sole", type="ell", bone="legHLl", c=SOLE, r=[0.0034, 0.0011, 0.0028], rot=[0, -35, 0], k=0.0010, color="@limb", mirror=True, **W)
TOES = []
for i, (ang, bang, m, L) in enumerate([(-50, -45, 0.0018, 0.0030), (-17, -15, 0.0024, 0.0040), (14, 14, 0.0024, 0.0040), (46, 45, 0.0018, 0.0029)]):
    d_ = roty(HAND, ang); base = add([PALM[0], 0.0012, PALM[2]], roty(HAND, bang), m)
    TOES.append(digit(S, f"finger{i + 1}", "legFLl", base, d_, L, 0.00095, 0.0012, 0.00085, col="@limb", blunt=True, **W))
for i, (ang, bang, m, L) in enumerate([(-52, -48, 0.0022, 0.0028), (-24, -22, 0.0028, 0.0040), (2, 2, 0.0030, 0.0046), (28, 28, 0.0028, 0.0042), (58, 58, 0.0022, 0.0030)]):
    d_ = roty(FOOT, ang); base = add([SOLE[0], 0.0012, SOLE[2]], roty(FOOT, bang), m)
    TOES.append(digit(S, f"toe{i + 1}", "legHLl", base, d_, L, 0.00100, 0.0012, 0.00090, col="@limb", blunt=True, **W))

EYE = {"at": [0.0560, 0.0158, 0.0072], "from": [0.0560, 0.0150, 0], "r": 0.0024, "color": "@eyeDark", "iris": "@eye", "pupil": "round", "lid": "@head", "sink": 0.42, "socket": 1.04}
COLORS = {"back": "#141312", "head": "#141312", "limb": "#161514", "belly": "#2a2724", "mark": "#f0c41a", "mouth": "#0a0908", "jaw": "#0e0d0c",
          "eye": "#1a1614", "eyeDark": "#070606"}
RED = {"mark": "#dc4a1c"}
d = {
    "name": "fire salamander",
    "_about": "SCULPTED (2026-11-08, tools/creaturegen/herps/salamander.py): the FIRE SALAMANDER, Salamandra salamandra, 20 cm, "
              "the tail a little shorter than the body. Stout and rounded: a broad flat rounded head, a blunt snout, big black "
              "protruding eyes, the PAROTOID glands bulging behind them (kidney-shaped, diverging backward); a thick round trunk "
              "with shallow costal grooves down the flanks; short sturdy sprawled legs, four blunt fingers in front and five toes "
              "behind (round tips, no claws); a tail round in section, thick at the root, tapering to a blunt point (one `sweep`), lying on the "
              "ground. Smooth WET skin (`wet`), glossy black with bright yellow blotches (paints): over the eyelids and the "
              "parotoids, two irregular rows down the back, a few on the flanks, one on each upper leg, two rows down the tail. "
              "Coats: spotted yellow (base), striped yellow (S. s. terrestris / fastuosa: two continuous wavy dorsolateral "
              "stripes from the parotoids onto the tail, `when: striped`), the rare orange-red one. A slow walk, the trunk and "
              "tail swinging side to side.",
    "kind": "parts",
    "flags": {"print": "none", "legLen": 0.011, "shy": 2},
    "colors": COLORS,
    "params": {"spotted": True, "striped": False},
    "coats": [{"name": "spotted"}, {"name": "spotted"}, {"name": "striped", "params": {"spotted": False, "striped": True}},
              {"name": "spotted"}, {"name": "striped", "params": {"spotted": False, "striped": True}}, {"name": "orange-red", "colors": RED}],
    "variants": {"spotted": {"params": {}, "colors": {}},
                 "striped": {"params": {"spotted": False, "striped": True}, "colors": {}},
                 "orange-red": {"params": {}, "colors": RED}},
    "parts": parts,
    "sculpt": {
        "keep": [],
        "paint": 0.3,
        "mesh": {"cell": 0.0004, "tris": [13000, 3000], "anchor": 0, "symmetric": True, "focus": {"head": 3, "legFLl": 1.6, "legHLl": 1.6}},
        "shade": {"back": 1.0, "belly": 1.0, "on": "@back"},
        "shape": SH,
        "eyes": EYE,
    },
}
del d["sculpt"]["shade"]

# ================= pass 2: on the probed skin
def bone_at(x):
    if x > 0.0445: return "head"
    if x > 0.037: return "nape"
    if x > 0.010: return "chest"
    if x > TX[0]: return "body"
    return "caud" + str(1 + sum(1 for t in TX[1:] if x < t))

def axis(x):
    if x > 0.040: return [x, 0.0135, 0]
    if x > -0.036: return [x, Y0, 0]
    return [x, ty(x), 0]

def grooves():
    """the jaw line (a shallow groove from under the eye round the snout) and the costal grooves down the flanks"""
    out = []
    # (round the snout: rays fanned from a point inside the head, the groove's ellipsoid laid in the skin's tangent plane)
    angs = [6 + 4.0 * j for j in range(23)]       # (degrees from straight ahead toward the left)
    o = [0.050, 0.0102, 0]
    rays = [[o, add(o, [math.cos(math.radians(a)), 0, math.sin(math.radians(a))], 0.03)] for a in angs]
    hits = rays_hits(SP, SH, rays)
    ok = [h for h in hits if h]; ns = normals(SP, SH, ok)
    # (one groove: a thin tube carved along the skin points, its axis a little inside the skin)
    pts = [add(h, n, -0.00008) + [0.00042] for h, n in zip(ok, ns)]
    pts.sort(key=lambda p: -p[0])
    out.append({"id": "jaw", "type": "tube", "bone": "head", "op": "sub", "pts": pts, "k": 0.00042 * 0.5, "color": "@mouth", "mirror": True})
    xs = [0.026 - 0.0052 * j for j in range(12)]
    hits = rays_hits(SP, SH, [[[x, Y0 - 0.001, 0], [x, Y0 - 0.001, 0.03]] for x in xs])
    for j, (x, h) in enumerate(zip(xs, hits)):
        if not h: continue
        out.append({"id": f"costal{j}", "type": "ell", "bone": bone_at(x), "op": "sub", "c": h, "r": [0.00032, 0.0038, 0.00045], "rot": [0, 0, 0],
                    "k": 0.0003, "color": "@back", "mirror": True})
    return out

def markings():
    P = Painter(SP, SH)
    for sg, S_, seed in ((1, "L", 3), (-1, "R", 8)):
        rng = random.Random(seed)
        # (every coat) the eyelid's and the parotoid's patches, a fleck on the snout
        blotch(P, f"lid{S_}", [0.0555, 0.0135, 0], ring_dir(40 + rng.uniform(-5, 5), sg), 0.0022, "@mark", "head", rng, 0.006, n=3, elong=1.2)
        blotch(P, f"par{S_}", [0.0430, 0.0135, 0], ring_dir(42 + rng.uniform(-5, 5), sg), 0.0040, "@mark", "head", rng, 0.007, n=4, elong=1.5)
        blotch(P, f"parB{S_}", [0.0385, 0.0135, 0], ring_dir(48, sg), 0.0026, "@mark", "nape", rng, 0.007, n=2, elong=1.3)
        if rng.random() < 0.7:
            blotch(P, f"snout{S_}", [0.0610, 0.0130, 0], ring_dir(30, sg), 0.0013, "@mark", "head", rng, 0.005, n=2)
        # SPOTTED: two irregular rows down the back, some merging; a few lower on the flanks
        x = 0.032
        while x > -0.036:
            phi = 32 + rng.uniform(-10, 12); sz = 0.0024 * rng.uniform(0.75, 1.3)
            blotch(P, f"dsp{S_}{int(x * 1e4)}", axis(x), ring_dir(phi, sg), sz, "@mark", bone_at(x), rng, 0.0095, n=3, elong=rng.uniform(1.0, 1.7), when="spotted")
            x -= rng.uniform(0.0065, 0.0105)
        for x in [0.022 + rng.uniform(-0.003, 0.003), 0.004 + rng.uniform(-0.004, 0.004), -0.016 + rng.uniform(-0.004, 0.004)]:
            if rng.random() < 0.75:
                blotch(P, f"fsp{S_}{int(x * 1e4)}", axis(x), ring_dir(82 + rng.uniform(-10, 10), sg), 0.0017 * rng.uniform(0.8, 1.2), "@mark", bone_at(x), rng, 0.0095, n=2, when="spotted")
        # STRIPED: a continuous wavy dorsolateral stripe from the parotoid to the tail, a few flank spots
        x = 0.037; j = 0; ph = rng.uniform(0, 6)
        while x > -0.052:
            phi = 36 + 5 * math.sin(x / 0.006 + ph)
            P.mark(f"str{S_}{j}", axis(x), ring_dir(phi, sg), 0.0034, 0.0020 * rng.uniform(0.9, 1.15), "@mark", bone_at(x), when="striped")
            x -= 0.0028; j += 1
        for x in [0.016, -0.008]:
            blotch(P, f"fst{S_}{int(x * 1e4)}", axis(x + rng.uniform(-0.003, 0.003)), ring_dir(86 + rng.uniform(-8, 8), sg), 0.0015, "@mark", bone_at(x), rng, 0.0095, n=2, when="striped")
        # the tail: spots in two rows (both coats; the striped one's stripe runs onto it first)
        x = -0.048 if True else 0
        while x > -0.118:
            if not (x > -0.054 and False):
                blotch(P, f"tsp{S_}{int(-x * 1e4)}", axis(x), ring_dir(38 + rng.uniform(-10, 10), sg), 0.0020 * (tr(x) / 0.0065) ** 0.6 * rng.uniform(0.8, 1.2), "@mark", bone_at(x), rng, tr(x), n=2,
                       elong=1.3, when="spotted" if x > -0.056 else None)
            x -= rng.uniform(0.0085, 0.0125)
        # the legs: a patch on each upper arm and thigh, a fleck on the forearm or the shank
        for nm, a_, b_, bone, sz in (("arm", [0.030, 0.0118, 0.0060], FE, "legF" + S_ + "u", 0.0022), ("thigh", [-0.035, 0.0116, 0.0060], HK, "legH" + S_ + "u", 0.0026),
                                     ("fore", FE, FW, "legF" + S_ + "l", 0.0013), ("shank", HK, HA, "legH" + S_ + "l", 0.0014)):
            m = lerp(a_, b_, 0.55); m = [m[0], m[1], m[2] * sg]
            if nm in ("fore", "shank") and rng.random() < 0.4: continue
            P.mark(f"{nm}{S_}", m, [0, 1, 0.25 * sg], sz * 1.2, sz, "@mark", bone)
    return P.lay(0.05)

if __name__ == "__main__":
    dump(OUT, d)                                       # (pass 1: the body bare, to be probed)
    index_add(["creatures/" + SP], after_prefix="creatures/others/")
    sh2 = grooves() + markings()
    SH += sh2
    dump(OUT, d)
    print(len(SH), "shapes,", len(sh2), "pass 2")
