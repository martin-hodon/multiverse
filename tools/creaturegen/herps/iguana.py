# iguana.py -- writes assets/creatures/others/green-iguana.json (2026-11-08): the GREEN IGUANA, Iguana iguana, 1.5 m long,
# the tail two thirds of it. Run: python3 tools/creaturegen/herps/iguana.py (two passes, like the agama: the body written
# bare, its skin probed through sharp/fd.mjs, then the crests, the dewlap, the claws, the cheek shield, the tubercles,
# the jaw line and the markings laid on it and the file written again). Listed in assets/index.json (fd.mjs loads it).
# The animal: a blunt DEEP head, the crown flat, the snout short and rounded, heavy jowls; on the cheek below the
# eardrum the big round SUBTYMPANIC SHIELD (a pale raised disc); a large DEWLAP hanging under the throat (a thin `fin`
# sheet on the midline); a CREST of soft spines from the nape down the back (serrated `fin`s, one per bone: tallest on
# the neck, lower down the back) going on as a low comb down the first half of the tail; conical tubercles on the sides
# of the neck; a trunk a little deeper than wide on strong sprawled legs, long toes (the hind 4th the longest) with
# sharp curved claws (`horn`s); the tail long and whip-like, flattened a little side to side (ONE `sweep` along
# caud1..4, aspect 1.15), tapering to a point, with dark rings (its `bands`). Skin: small bead scales (`scales`).
# Coats: GREEN (the base, faint dark bars on the flanks), the ORANGE breeding male; variant `juvenile` (.3, bright green).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hlib import *

SP = "others/green-iguana"
OUT = SP + ".json"

Y0 = 0.085                                   # the trunk's axis
B = [-0.060, Y0, 0]                          # body (the root): the rear trunk
C = [0.060, Y0 + 0.003, 0]                   # chest
N = [0.170, Y0 + 0.012, 0]                   # nape
HD = [0.205, Y0 + 0.020, 0]                  # head: its pivot behind the skull
TX = [-0.170, -0.370, -0.590, -0.830]        # caud1..4 roots
TIP = -1.170
ASP = 1.15                                   # (the tail's section: deeper than wide)
RT = [(-0.160, .040), (-0.200, .037), (-0.280, .031), (-0.400, .024), (-0.550, .017), (-0.700, .011), (-0.850, .0068),
      (-0.980, .0040), (-1.080, .0022), (-1.140, .0010), (TIP, .0002)]
YT = [(-0.160, Y0 - 0.006), (-0.200, 0.073), (-0.260, 0.057), (-0.330, 0.041), (-0.400, ASP * .024 + 0.001)]
tr = lambda x: interp(RT, x)
ty = lambda x: interp(YT, x) if x >= -0.400 else ASP * tr(x) + 0.001
FS, FE, FW = [0.115, 0.080, 0.040], [0.105, 0.060, 0.098], [0.125, 0.014, 0.112]     # shoulder, elbow, wrist
HH, HK, HA = [-0.150, 0.078, 0.040], [-0.122, 0.068, 0.122], [-0.160, 0.014, 0.148]  # hip, knee, ankle
HAND = nrm([math.cos(math.radians(20)), 0, math.sin(math.radians(20))])
FOOT = nrm([math.cos(math.radians(35)), 0, math.sin(math.radians(35))])

parts = rig(B, C, N, HD, TX, TIP, ty, tr, (FS, FE, FW, HH, HK, HA, (0.016, 0.012, 0.009), (0.020, 0.014, 0.010)),
            body_r=0.045, sw=8, speed=0.6, tail_deg=(7, 9, 11, 13), swing=26, lift=14, head_dir=(0.12, -0.004))

SH = Shapes(); S = SH.S
BD = {"pat": "scales", "frame": frame([0.0, Y0, 0], 0.07)}           # (small bead scales)
HB = {"pat": "scales", "frame": frame([0.27, 0.115, 0], 0.045)}      # (the head's finer)
# ---- the HEAD first (its cuts carve only the shapes before them): deep and blunt, the crown flat, heavy jowls
H = "head"
S("headM", type="ell", bone=H, c=[0.270, 0.119, 0], r=[0.064, 0.037, 0.028], k=0.006, color="@head", **HB)
S("snout", type="ell", bone=H, c=[0.318, 0.114, 0], r=[0.042, 0.031, 0.022], k=0.006, color="@head", **HB)
S("muzzle", type="box", bone=H, c=[0.322, 0.114, 0], r=[0.026, 0.020, 0.013], k=0.010, color="@head", **HB)   # (the box of the snout)
S("jowl", type="ell", bone=H, c=[0.230, 0.101, 0.015], r=[0.038, 0.036, 0.019], k=0.008, color="@head", mirror=True, **HB)
S("cutTop", type="box", bone=H, op="sub", c=[0.290, 0.1600, 0], r=[0.09, 0.012, 0.05], rot=[0, 0, -8], k=0.004, color="@head", **HB)
S("cutChin", type="box", bone=H, op="sub", c=[0.305, 0.0745, 0], r=[0.07, 0.010, 0.05], rot=[0, 0, 6], k=0.004, color="@head", **HB)
S("cutSide", type="box", bone=H, op="sub", c=[0.330, 0.114, 0.0335], r=[0.050, 0.04, 0.012], rot=[0, 7, 0], k=0.004, color="@head", mirror=True, **HB)   # (the snout's sides planed flat)
S("brow", type="ell", bone=H, c=[0.289, 0.1415, 0.0205], r=[0.025, 0.0085, 0.0100], rot=[0, 8, 0], k=0.0025, color="@head", mirror=True, **HB)
S("naris", type="sphere", bone=H, op="sub", c=[0.352, 0.125, 0.0095], r=0.0035, k=0.001, color="@mouth", mirror=True)
# ---- the neck thick, the throat; the trunk a little deeper than wide; shoulders, pelvis, belly
S("neck", type="ell", bone="nape", c=[0.185, 0.104, 0], r=[0.055, 0.044, 0.040], k=0.010, color="@back", **BD)
S("throat", type="ell", bone="nape", c=[0.215, 0.085, 0], r=[0.045, 0.026, 0.030], k=0.008, color="@throat", **BD)
S("trunkM", type="ell", c=[0.0, Y0, 0], r=[0.130, 0.054, 0.056], k=0.012, color="@back", **BD)
S("trunkF", type="ell", bone="chest", c=[0.075, Y0 + 0.004, 0], r=[0.085, 0.052, 0.054], k=0.012, color="@back", **BD)
S("trunkR", type="ell", c=[-0.090, Y0 - 0.002, 0], r=[0.080, 0.050, 0.052], k=0.012, color="@back", **BD)
S("shoulders", type="ell", bone="chest", c=[0.115, Y0 + 0.002, 0.026], r=[0.035, 0.035, 0.026], k=0.010, color="@back", mirror=True, **BD)
S("pelvis", type="ell", c=[-0.145, Y0 - 0.002, 0.026], r=[0.038, 0.034, 0.026], k=0.010, color="@back", mirror=True, **BD)
S("belly", type="ell", c=[-0.010, Y0 - 0.030, 0], r=[0.150, 0.025, 0.052], k=0.010, color="@belly", **BD)
# ---- the tail: thick at the root, then ONE sweep to a whip-thin point, lying on the ground, ringed dark
S("tailRoot", type="ell", c=[-0.170, Y0 - 0.008, 0], r=[0.050, 0.040, 0.040], k=0.010, color="@back", **BD)
BANDS = [(-0.330 - 0.098 * i, -0.330 - 0.098 * i - 0.036 + 0.002 * i, "@band") for i in range(8)]
sweep_tail(S, -0.160, TIP, ty, tr, "@back", k=0.008, n=26, pat="scales", r_frame=0.07, bands=BANDS, bandEdge=0.006, aspect=ASP)
# ---- legs: strong; long toes, the hands and feet flat
limb_shapes(S, "legFLu", "legFLl", [0.113, 0.079, 0.032], FE, FW, 0.0150, 0.0110, 0.0088, 0.0076, k=0.006, **BD)
limb_shapes(S, "legHLu", "legHLl", [-0.148, 0.077, 0.032], HK, HA, 0.0190, 0.0125, 0.0095, 0.0080, k=0.007, **BD)
S("thigh", type="ell", bone="legHLu", c=lerp([-0.150, 0.078, 0.040], HK, 0.40), r=[0.026, 0.018, 0.028], rot=[0, -20, 0], k=0.007, color="@limb", mirror=True, **BD)
S("forearmM", type="ell", bone="legFLl", c=lerp(FE, FW, 0.30), r=[0.013, 0.016, 0.012], k=0.005, color="@limb", mirror=True, **BD)
PALM = [FW[0] + HAND[0] * 0.008, 0.0062, FW[2] + HAND[2] * 0.008]
S("palm", type="ell", bone="legFLl", c=PALM, r=[0.014, 0.0055, 0.011], rot=[0, -20, 0], k=0.004, color="@limb", mirror=True, **BD)
SOLE = [HA[0] + FOOT[0] * 0.014, 0.0062, HA[2] + FOOT[2] * 0.014]
S("sole", type="ell", bone="legHLl", c=SOLE, r=[0.022, 0.0058, 0.013], rot=[0, -35, 0], k=0.004, color="@limb", mirror=True, **BD)
TOES = []
for i, (ang, bang, m, L) in enumerate([(-55, -50, 0.010, 0.018), (-26, -22, 0.012, 0.026), (-3, -2, 0.013, 0.032), (22, 22, 0.012, 0.034), (52, 52, 0.009, 0.022)]):
    d_ = roty(HAND, ang); base = add([PALM[0], 0.0060, PALM[2]], roty(HAND, bang), m)
    TOES.append(digit(S, f"finger{i + 1}", "legFLl", base, d_, L, 0.0042, 0.0060, 0.0034, col="@toe", **BD))
for i, (ang, bang, m, L) in enumerate([(-40, -34, 0.012, 0.020), (-20, -15, 0.016, 0.032), (-6, -2, 0.018, 0.045), (9, 10, 0.017, 0.060), (58, 62, 0.008, 0.032)]):
    d_ = roty(FOOT, ang); base = add([SOLE[0], 0.0060, SOLE[2]], roty(FOOT, bang), m)
    TOES.append(digit(S, f"toe{i + 1}", "legHLl", base, d_, L, 0.0045, 0.0060, 0.0034, col="@toe", **BD))

EYE = {"at": [0.287, 0.125, 0.0225], "from": [0.287, 0.124, 0], "r": 0.0074, "color": "@eyeDark", "iris": "@eye", "pupil": "round", "lid": "@head", "sink": 0.6, "socket": 1.05}
COLORS = {"back": "#5c8c38", "head": "#6a9844", "throat": "#80a454", "dewlap": "#80a454", "dewlapRim": "#5a7c3a", "belly": "#98b866", "limb": "#58863a",
          "toe": "#50783a", "crest": "#86a65c", "shield": "#bccaa2", "tub": "#6f8a58", "band": "#33372a", "bar": "#3e5a2c",
          "claw": "#2a2620", "mouth": "#2a2018", "ear": "#4c6a38", "eye": "#c08a30", "eyeDark": "#120c08"}
ORANGE = {"back": "#bc6a2c", "head": "#cc7a30", "throat": "#d68a38", "dewlap": "#d68a38", "dewlapRim": "#a85a1c", "belly": "#d89c56", "limb": "#b2642a",
          "toe": "#8c5226", "crest": "#c86a28", "shield": "#e2c48c", "tub": "#b8783a", "band": "#563218", "bar": "#8a4a20", "ear": "#8a5428"}
YOUNG = {"back": "#56b438", "head": "#64c042", "throat": "#7cc650", "dewlap": "#7cc650", "dewlapRim": "#4c9a34", "belly": "#a4d474", "limb": "#52ac36",
         "toe": "#46962e", "crest": "#7cc452", "shield": "#c4e2a4", "tub": "#5ea044", "band": "#2e5a24", "bar": "#3a7a2a"}
d = {
    "name": "green iguana",
    "_about": "SCULPTED (2026-11-08, tools/creaturegen/herps/iguana.py): the GREEN IGUANA, Iguana iguana, 1.5 m long, the "
              "tail two thirds of it. A deep box-like head, the crown flat, the snout long, blunt and planed at the sides, a clear brow ridge over the eye, heavy jowls; the big "
              "round SUBTYMPANIC SHIELD on the cheek below the eardrum (a pale raised disc); a large DEWLAP on the throat's "
              "midline from the chin to the chest (a `fin`, thicker at its root, its rim one convex arc, the throat's scales, a darker rim); a CREST of soft spines from the nape down the back (serrated `fin`s, one per bone, "
              "tallest on the neck) going on as a low comb down the first half of the tail; conical tubercles on the neck's "
              "sides; a trunk a little deeper than wide on strong sprawled legs; long toes (the hind 4th the longest) with "
              "sharp curved claws (`horn`s); the tail long and whip-like, flattened a little side to side, tapering to a "
              "point (one `sweep` along caud1..4), ringed dark (its `bands`). Small bead scales (`scales`). Coats: GREEN "
              "(base, faint dark bars on the flanks), the ORANGE breeding male; variant `juvenile` (.3, bright green). A slow "
              "sprawling walk, the trunk and tail swinging.",
    "kind": "parts",
    "flags": {"print": "none", "legLen": 0.07, "shy": 2},
    "colors": COLORS,
    "coats": [{"name": "green"}, {"name": "green"}, {"name": "orange male", "colors": ORANGE}],
    "variants": {"green": {"colors": {}},
                 "orange": {"colors": ORANGE},
                 "juvenile": {"scale": 0.3, "colors": YOUNG}},
    "parts": parts,
    "sculpt": {
        "keep": [],
        "paint": 0.3,
        "mesh": {"cell": 0.0022, "tris": [12000, 3200], "anchor": 0, "symmetric": True, "focus": {"head": 3, "legFLl": 1.6, "legHLl": 1.6}},
        "shape": SH,
        "eyes": EYE,
    },
}

# ================= pass 2: on the probed skin
def bone_at(x):
    if x > 0.205: return "head"
    if x > 0.170: return "nape"
    if x > 0.060: return "chest"
    if x > TX[0]: return "body"
    return "caud" + str(1 + sum(1 for t in TX[1:] if x < t))

def serrated(id_, bone, XF, XR, hs, top, sink, thick, notch=0.3, lean=0.3, fair=None):
    """a crest: a row of spines (heights hs, front to back between XF and XR) as one serrated sheet on the midline,
    its root sunk `sink` under the back's top (top(x)), each tip leaning back, the notches between at `notch` of the
    lower neighbour's height"""
    xs = [XF + (XR - XF) * i / (len(hs) - 1) for i in range(len(hs))]
    gap = (XF - XR) / max(1, len(hs) - 1)
    root = [[x, top(x) - sink, 0] for x in [XR - 0.4 * gap + (XF - XR + 0.8 * gap) * k / 8 for k in range(9)]]
    edge = [[XR - 0.4 * gap, top(XR - 0.4 * gap) + 0.1 * hs[-1], 0, 1.0]]; corners = []
    tips = [[x - lean * h, top(x - lean * h) + h, 0] for x, h in zip(xs, hs)]
    rev = list(reversed(tips)); rh = list(reversed(hs))
    for k, tp in enumerate(rev):
        if k:
            a = rev[k - 1]; xm = (a[0] + tp[0]) / 2
            q = [xm, top(xm) + notch * min(rh[k - 1], rh[k]), 0]
            corners.append(len(edge)); edge.append(q + [1.0])
        corners.append(len(edge)); edge.append(tp[:3] + [1.0])
    edge.append([XF + 0.4 * gap, top(XF + 0.4 * gap) + 0.1 * hs[0], 0, 1.0])
    return {"id": id_, "type": "fin", "bone": bone, "root": root, "edge": edge, "corners": corners, "thick": thick, "slope": 0.35,
            "fair": {"r": fair or thick * 1.2, "rows": 3}, "color": "@crest", "n": max(48, 7 * len(hs)), "across": 4}

def crests():
    T = back_table(SP, SH, [round(0.215 - 0.005 * k, 4) for k in range(160)], 0.004, 0.4)
    top = lambda x: interp(T, x)
    ramp = lambda a, b, n: [a + (b - a) * i / (n - 1) for i in range(n)]
    return [serrated("crestN", "nape", 0.204, 0.172, [0.022, 0.031, 0.035, 0.036], top, 0.006, 0.0026, notch=0.25),
            serrated("crestC", "chest", 0.164, 0.064, ramp(0.035, 0.017, 12), top, 0.006, 0.0024, notch=0.25),
            serrated("crestB", "body", 0.056, -0.162, ramp(0.016, 0.009, 22), top, 0.005, 0.0020, notch=0.3),
            serrated("comb1", "caud1", -0.176, -0.364, ramp(0.0085, 0.0055, 20), top, 0.004, 0.0016, notch=0.35),
            serrated("comb2", "caud2", -0.378, -0.580, ramp(0.0050, 0.0025, 18), top, 0.003, 0.0013, notch=0.4)]

def dewlap():
    """the dewlap: a sheet on the throat's midline from the chin back to the chest, its rim one smooth convex arc,
    thickest at its root; the throat's green and scales, its rim a little darker"""
    xs = [round(0.330 - 0.004 * k, 4) for k in range(50)]
    hits = rays_hits(SP, SH, [[[x, 0.0, 0], [x, 0.2, 0]] for x in xs])
    T = [(x, h[1]) for x, h in zip(xs, hits) if h]
    bot = lambda x: interp(T, x)
    XF, XR, D = 0.318, 0.140, 0.060
    root = [[x, bot(x) + 0.005, 0] for x in [XF - (XF - XR) * k / 14 for k in range(15)]]
    edge = []
    for k in range(25):   # (the rim: a skewed half-sine, deepest a little behind the middle -- under the jowls)
        u = k / 24; x = XF - (XF - XR) * u
        dd = D * math.sin(math.pi * u ** 1.25) ** 0.85
        edge.append([x, bot(x) - max(dd, 0.002), 0, 1.0])
    return [{"id": "dewlap", "type": "fin", "bone": "nape", "root": root, "edge": edge, "corners": [0, len(edge) - 1], "thick": 0.0040,
             "slope": 0.6, "swell": [0.008, 0.025, 1.2], "fair": {"r": 0.005, "rows": 3}, "color": "@dewlap", "rim": 0.004, "rimColor": "@dewlapRim",
             "pat": "scales", "frame": frame([0.25, 0.06, 0], 0.045), "n": 80, "across": 6}]

def head_details():
    out = []
    # the jaw line: one groove carved along the lip, round the snout and back under the eye
    o = [0.290, 0.100, 0]
    angs = [3 + 3.4 * j for j in range(25)]
    hits = rays_hits(SP, SH, [[o, add(o, [math.cos(math.radians(a)), -0.02, math.sin(math.radians(a))], 0.12)] for a in angs])
    xs = [0.284 - 0.007 * j for j in range(6)]
    hits += rays_hits(SP, SH, [[[x, 0.100 + 0.0012 * j, 0], [x, 0.100 + 0.0012 * j, 0.1]] for j, x in enumerate(xs)])
    ok = [h for h in hits if h]; ns = normals(SP, SH, ok, h=0.001)
    pts = sorted([add(h, n, -0.0005) + [0.0022] for h, n in zip(ok, ns)], key=lambda p: -p[0])
    out.append({"id": "jaw", "type": "tube", "bone": "head", "op": "sub", "pts": pts, "k": 0.0011, "color": "@mouth", "mirror": True})
    # the eardrum: an oval hollow behind the eye, high on the side of the head
    e = rays_hits(SP, SH, [[[0.222, 0.117, 0], [0.222, 0.117, 0.1]]])[0]
    out.append({"id": "ear", "type": "ell", "bone": "head", "op": "sub", "c": add(e, [0, 0, 1], 0.0015), "r": [0.0075, 0.0090, 0.0035], "rot": [0, 0, 10],
                "k": 0.0015, "color": "@ear", "mirror": True})
    # the subtympanic shield: a big round pale disc on the cheek below it, standing a little proud
    P = Painter(SP, SH)
    P.mark("shield", [0.232, 0.094, 0], [0, -0.1, 1], 0.0115, 0.0105, "@shield", "head", depth=0.004, k=0.001, kc=0.0008, mirror=True)
    s = P.lay(0.1)[0]
    disc = dict(s); disc.pop("op"); disc["id"] = "shieldDisc"; disc["r"] = [0.0112, 0.0102, 0.0030]; disc["k"] = 0.0015
    out += [disc, s]
    # the tubercles: conical bumps scattered over the sides of the neck behind the jowls
    rng = random.Random(5); T = Painter(SP, SH)
    for j in range(14):
        x = rng.uniform(0.150, 0.205); phi = rng.uniform(45, 115)
        T.mark(f"tub{j}", [x, 0.098, 0], ring_dir(phi), 0.0035, 0.0035, "@tub", bone_at(x), depth=0.003)
    for q in T.lay(0.1):
        n = q["axes"][2]
        out.append({"id": q["id"], "type": "sphere", "bone": q["bone"], "c": add(q["c"], n, 0.0004), "r": rng.uniform(0.0022, 0.0028), "k": 0.0010,
                    "color": "@tub", "mirror": True})
    return out

def markings():
    P = Painter(SP, SH)
    rng = random.Random(9)
    # faint dark bars down the flanks
    for j, x in enumerate([0.095, 0.040, -0.015, -0.070, -0.125]):
        P.mark(f"bar{j}", [x, Y0, 0], ring_dir(78), 0.010 * rng.uniform(.8, 1.2), 0.034, "@bar", bone_at(x), along=(1, 0.0, 0), depth=0.01, k=0.004, mirror=True)
    return P.lay(0.2)

if __name__ == "__main__":
    dump(OUT, d)                                       # (pass 1: the body bare, to be probed)
    index_add(["creatures/" + SP], after_prefix="creatures/others/")
    sh2 = crests() + dewlap() + head_details() + claws(SP, SH, TOES, 0.0095, 0.0005, bend=0.25) + markings()
    SH += sh2
    dump(OUT, d)
    print(len(SH), "shapes,", len(sh2), "pass 2")
