# dimetrodon.py -- writes assets/creatures/dinosaurs/dimetrodon.json (2026-11-08): DIMETRODON GRANDIS, an early Permian
# sphenacodontid synapsid (NOT a dinosaur: closer to mammals), 3.2 m long, sprawling.
# Run: python3 tools/creaturegen/prehistoric/dimetrodon.py   (two passes, like walllizard.py: the body is written without
# its sharp parts, its skin probed through sharp/fd.mjs, then the sail, the spines, the teeth and the claws are rooted on
# it and the file written again). The species must be listed in assets/index.json (fd.mjs loads it from there).
# Rig ("parts", the wall lizard's plan at 3 m): body (the whole trunk, RIGID: the sail spans it -- no chest swing) ->
# head (pivot at the neck's root); body -> caud1..4 (the tail, swinging on the gait clock, faded standing); sprawled legs
# (the upper bone out sideways swinging fore and aft, the lower down to the wrist / ankle, a lift on the forward swing).
# THE SAIL: one `fin` sheet in the midplane, rooted along the back from the neck's root to the hips, its rim the exact
# outline over 19 neural spines -- low over the shoulders, highest (.9 m over the back) at mid-back, falling to the
# sacrum, a semicircle-ish arc -- the rim sagging a little between the spine tips (scalloped; the tips `corners`); thin
# (12 mm, sharp rim), faired into the back. Each spine a thin `horn` rising from inside the back THROUGH the sheet to just
# past its rim: they stand out of both faces as ribs. Colour: the back's tone at the base, an ochre band up the middle
# (`tip`), a dark rim band.
# The SKULL deep and narrow: a tall snout, the upper jaw margin STEPPED (a notch between the premaxilla and the maxilla, the
# lower jaw's big front teeth fit up into it), the maxilla's margin bowed down at the canines; differentiated teeth
# (`horn`s): two premaxillary incisors, two great canine FANGS on each side, small cheek teeth behind; the lower's big
# front tusk and a row behind it. Five clawed toes on each foot (claws `horn`s), the 4th the longest.
# Skin: muted olive-brown, scaly (`scales`), dark transverse bars across the back fading down the flanks and rings down
# the tail (paints: colour only, so a coat recolours them); the belly pale.
import sys, os, math, json, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rept import *

SP = "dinosaurs/dimetrodon"
OUT = SP + ".json"

# ---- the rig's joints (metres; x forward, y up, z left; the ground at y = 0)
B = [0.10, 0.41, 0]              # body: the trunk's middle
HD = [0.80, 0.48, 0]             # head: its pivot at the neck's root
TX = [-0.36, -0.74, -1.10, -1.46]  # caud1..4 roots
TIP = -1.95
# the tail's axis height and radius along x
YT = [(-0.30, 0.41), (-0.55, 0.40), (-0.85, 0.37), (-1.15, 0.32), (-1.45, 0.26), (-1.75, 0.20), (TIP, 0.165)]
RT = [(-0.30, 0.135), (-0.55, 0.112), (-0.85, 0.088), (-1.15, 0.066), (-1.45, 0.046), (-1.70, 0.028), (-1.85, 0.016), (TIP, 0.004)]
ty = lambda x: interp(YT, x)
tr = lambda x: interp(RT, x)
FS, FE, FW = [0.55, 0.37, 0.15], [0.52, 0.33, 0.37], [0.575, 0.065, 0.405]     # shoulder, elbow, wrist
HH, HK, HA = [-0.29, 0.37, 0.15], [-0.25, 0.34, 0.41], [-0.335, 0.07, 0.455]   # hip, knee, ankle
HAND = nrm([math.cos(math.radians(25)), 0, math.sin(math.radians(25))])
FOOT = nrm([math.cos(math.radians(38)), 0, math.sin(math.radians(38))])

parts = [
    {"id": "body", "parent": None, "shape": "tube", "size": tube([-0.45, 0, 0], [0.5, 0, 0], 0.19, 0.19), "pos": B, "color": "@back"},
    {"id": "head", "parent": "body", "shape": "tube", "size": tube([0, 0, 0], [0.48, -0.03, 0], 0.11, 0.05), "pos": sub(HD, B), "color": "@back",
     "anim": {"axis": "y", "deg": 7, "speed": 0.25, "phase": 0}},
]
prev, at = "body", B
for i, x in enumerate(TX):
    xe = TX[i + 1] if i + 1 < len(TX) else TIP
    p = [x, ty(x), 0]
    parts.append({"id": f"caud{i + 1}", "parent": prev, "shape": "tube", "size": tube([0, 0, 0], [xe - x, ty(xe) - ty(x), 0], tr(x), tr(xe)),
                  "pos": sub(p, at), "color": "@back",
                  "anim": {"axis": "y", "deg": [5, 7, 9, 11][i], "speed": 0.8, "phase": round(PI + 0.7 * (i + 1), 3), "amp": True}})
    prev, at = f"caud{i + 1}", p
for S_, sz in (("L", 1), ("R", -1)):
    parts += limb_parts(S_, sz, "body", "body", FS, FE, FW, HH, HK, HA, B, B, (0.07, 0.05, 0.035), (0.085, 0.058, 0.04), swing=24, lift=12, speed=0.8)

SH = Shapes(); S = SH.S
FR = {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.16}
SC = {"pat": "scales", "frame": FR}
HF = {"pat": "scales", "frame": {"o": [1.0, 0.5, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.12}}

# ---- the HEAD first (its cuts carve only what is before them: the head's own shapes)
H = "head"
S("cranium", type="ell", bone=H, c=[0.99, 0.54, 0], r=[0.14, 0.11, 0.075], k=0.03, color="@head", **HF)
S("snout", type="ell", bone=H, c=[1.165, 0.495, 0], r=[0.13, 0.088, 0.046], k=0.03, color="@head", **HF)
S("nasal", type="ell", bone=H, c=[1.115, 0.566, 0], r=[0.155, 0.036, 0.04], rot=[0, 0, -20], k=0.025, color="@head", **HF)
S("muzzle", type="ell", bone=H, c=[1.24, 0.485, 0], r=[0.058, 0.075, 0.042], k=0.02, color="@head", **HF)
S("maxilla", type="ell", bone=H, c=[1.05, 0.452, 0.018], r=[0.17, 0.038, 0.03], rot=[0, 0, -3], k=0.02, color="@head", mirror=True, **HF)
S("temple", type="ell", bone=H, c=[0.915, 0.535, 0.04], r=[0.08, 0.085, 0.04], k=0.025, color="@head", mirror=True, **HF)
S("jaw", type="ell", bone=H, c=[1.06, 0.395, 0], r=[0.205, 0.042, 0.045], rot=[0, 0, 5], k=0.025, color="@jaw", **HF)
S("jawAngle", type="ell", bone=H, c=[0.915, 0.405, 0], r=[0.08, 0.055, 0.062], k=0.025, color="@jaw", **HF)
S("chin", type="ell", bone=H, c=[1.215, 0.39, 0], r=[0.06, 0.034, 0.036], rot=[0, 0, 12], k=0.02, color="@jaw", **HF)
# (the mouth: a slit along the jaw margin each side, stepped -- the premaxilla's margin low, the notch, the maxilla's
#  bowed down at the canines and rising behind)
S("mouthRear", type="box", bone=H, op="sub", c=[1.01, 0.433, 0.07], r=[0.11, 0.0045, 0.035], rot=[0, 0, -3], round=0.003, k=0.004, color="@mouth", mirror=True)
S("mouthFront", type="box", bone=H, op="sub", c=[1.235, 0.424, 0.05], r=[0.055, 0.0045, 0.03], rot=[0, 0, 4], round=0.003, k=0.004, color="@mouth", mirror=True)
S("notch", type="ell", bone=H, op="sub", c=[1.168, 0.442, 0.05], r=[0.019, 0.022, 0.034], k=0.006, color="@mouth", mirror=True)
S("naris", type="sphere", bone=H, op="sub", c=[1.272, 0.505, 0.018], r=0.0085, k=0.004, color="@mouth", mirror=True)
S("fenestra", type="ell", bone=H, op="sub", c=[0.905, 0.56, 0.08], r=[0.04, 0.028, 0.014], k=0.012, color="@head", mirror=True)
S("brow", type="ell", bone=H, c=[0.985, 0.618, 0.052], r=[0.045, 0.014, 0.022], k=0.012, color="@head", mirror=True, **HF)
h_end = len(SH)
# ---- neck and trunk: a deep barrel, the belly low, the spines' muscles a ridge along the back
S("neck", type="ell", c=[0.76, 0.47, 0], r=[0.15, 0.12, 0.11], k=0.05, color="@back", **SC)
S("neckH", type="ell", bone=H, c=[0.85, 0.49, 0], r=[0.1, 0.11, 0.09], k=0.04, color="@back", **SC)
S("throat", type="ell", bone=H, c=[0.83, 0.42, 0], r=[0.12, 0.05, 0.07], k=0.04, color="@belly", **SC)
S("trunk", type="ell", c=[0.10, 0.415, 0], r=[0.52, 0.17, 0.225], k=0.07, color="@back", **SC)
S("chest", type="ell", c=[0.44, 0.405, 0], r=[0.24, 0.17, 0.19], k=0.06, color="@back", **SC)
S("hips", type="ell", c=[-0.24, 0.415, 0], r=[0.26, 0.145, 0.165], k=0.06, color="@back", **SC)
S("belly", type="ell", c=[0.12, 0.30, 0], r=[0.44, 0.085, 0.19], k=0.07, color="@belly", **SC)
S("dorsum", type="ell", c=[0.10, 0.55, 0], r=[0.66, 0.05, 0.075], k=0.06, color="@back", **SC)
S("shoulder", type="ell", c=[0.53, 0.39, 0.13], r=[0.12, 0.1, 0.08], k=0.05, color="@back", mirror=True, **SC)
S("pelvis", type="ell", c=[-0.28, 0.39, 0.12], r=[0.12, 0.09, 0.08], k=0.05, color="@back", mirror=True, **SC)
# ---- the tail: round, tapering to a point, drooping toward the ground
CUTS = [(-0.20, -0.80), (-0.70, -1.16), (-1.06, -1.52), (-1.42, TIP)]
for i, (x0, x1) in enumerate(CUTS):
    xs = [x0 + (x1 - x0) * t / 5 for t in range(6)]
    S(f"tail{i + 1}", type="tube", bone=f"caud{i + 1}", pts=[[x, ty(x), 0, tr(x)] for x in xs], k=0.02, color="@back", **SC)
S("tailBelly", type="tube", bone="caud1", pts=[[x, ty(x) - 0.5 * tr(x), 0, 0.55 * tr(x)] for x in (-0.25, -0.45, -0.65)], k=0.03, color="@belly", **SC)
# ---- the legs: sprawled -- the upper bones out to the side, the lower down; flat hands and feet
def limb(u, l, s0, e, w, r0, r1, r2, r3):
    S(u, type="tube", bone=u, pts=[s0 + [r0], lerp(s0, e, 0.45) + [(r0 + r1) / 2 * 1.05], e + [r1]], k=0.03, color="@limb", mirror=True, **SC)
    S(l, type="tube", bone=l, pts=[e + [r1 * 0.95], lerp(e, w, 0.5) + [r2], w + [r3]], k=0.02, color="@limb", mirror=True, **SC)
limb("legFLu", "legFLl", [0.55, 0.37, 0.10], FE, FW, 0.085, 0.062, 0.05, 0.039)
limb("legHLu", "legHLl", [-0.29, 0.37, 0.10], HK, HA, 0.10, 0.07, 0.056, 0.044)
S("elbow", type="ell", bone="legFLl", c=add(FE, [-0.01, 0, 0.01]), r=[0.055, 0.052, 0.048], k=0.02, color="@limb", mirror=True, **SC)
S("knee", type="ell", bone="legHLl", c=add(HK, [0.005, 0, 0.01]), r=[0.062, 0.058, 0.055], k=0.02, color="@limb", mirror=True, **SC)
PALM = [FW[0] + HAND[0] * 0.045, 0.026, FW[2] + HAND[2] * 0.045]
S("palm", type="ell", bone="legFLl", c=PALM, r=[0.065, 0.022, 0.05], rot=[0, -25, 0], k=0.02, color="@limb", mirror=True, **SC)
SOLE = [HA[0] + FOOT[0] * 0.07, 0.026, HA[2] + FOOT[2] * 0.07]
S("sole", type="ell", bone="legHLl", c=SOLE, r=[0.09, 0.024, 0.055], rot=[0, -38, 0], k=0.02, color="@limb", mirror=True, **SC)
S("heel", type="ell", bone="legHLl", c=[HA[0], 0.04, HA[2]], r=[0.04, 0.035, 0.04], k=0.02, color="@limb", mirror=True)
TOES = []   # (id, bone, base, dir, length, radius): the claws go on their tips in pass 2
def digits(pre, bone, palm, axis, spec, r0, y0):
    for i, (ang, bang, m, L) in enumerate(spec):
        d = roty(axis, ang); base = add([palm[0], y0, palm[2]], roty(axis, bang), m)
        tip = add(base, d, L); tip[1] = 0.016
        S(f"{pre}{i + 1}", type="tube", bone=bone, pts=[base + [r0], lerp(base, tip, 0.5) + [r0 * 0.85], tip + [r0 * 0.7]], k=0.008, color="@limb", mirror=True)
        TOES.append((f"{pre}{i + 1}", bone, tip, d, r0 * 0.7))
# (the manus: the 3rd and 4th longest; the pes: the 4th longest -- the reptile's plan)
digits("finger", "legFLl", PALM, HAND, [(-62, -55, 0.035, 0.04), (-30, -25, 0.05, 0.055), (-4, 0, 0.055, 0.065), (22, 22, 0.05, 0.065), (52, 55, 0.035, 0.045)], 0.0135, 0.022)
digits("toe", "legHLl", SOLE, FOOT, [(-55, -50, 0.045, 0.045), (-28, -25, 0.07, 0.06), (-8, -5, 0.08, 0.075), (12, 15, 0.075, 0.09), (48, 50, 0.04, 0.06)], 0.015, 0.022)

# ---- MARKINGS (paints, colour only): dark bars across the back, fading out down the flanks; rings down the tail
for i, x in enumerate([0.62, 0.47, 0.32, 0.17, 0.02, -0.13, -0.28]):
    S(f"bar{i}", type="ell", op="paint", c=[x, 0.57, 0], r=[0.04, 0.2, 0.32], rot=[0, 0, -8], k=0.02, kc=0.03, color="@stripe")
for i, x in enumerate([-0.46, -0.63, -0.80, -0.97, -1.14, -1.31, -1.48, -1.65, -1.80]):
    bone = "caud" + str(1 + sum(1 for t in TX[1:] if x < t))
    S(f"ring{i}", type="ell", bone=bone, op="paint", c=[x, ty(x) + 0.35 * tr(x), 0], r=[0.035 * (0.6 + 0.4 * tr(x) / 0.13), 1.05 * tr(x), 1.2 * tr(x)], k=0.01, kc=0.02, color="@stripe")
S("mask", type="ell", bone=H, op="paint", c=[0.94, 0.575, 0.07], r=[0.07, 0.025, 0.05], rot=[0, 0, -6], k=0.01, kc=0.02, color="@stripe", mirror=True)

EYE = {"at": [0.985, 0.59, 0.065], "from": [0.985, 0.59, 0], "r": 0.019, "color": "@eyeDark", "iris": "@eye", "pupil": "round", "lid": "@head", "sink": 0.6}
COLORS = {"back": "#5d583c", "head": "#5a553a", "limb": "#57523a", "jaw": "#8a7f5c", "belly": "#b0a07a", "stripe": "#35301f",
          "sail": "#6a5a3a", "sailMid": "#b8843e", "sailRim": "#3a2c1e", "spine": "#94784e", "spineTip": "#c8a46a",
          "claw": "#2a241c", "tooth": "#ece2c6", "toothBase": "#c8b48c", "mouth": "#3a2620", "eye": "#c89a3a", "eyeDark": "#1a120a"}
RUST = {"back": "#6a4a32", "head": "#664632", "limb": "#5e4430", "jaw": "#9a7a5a", "belly": "#c4a882", "stripe": "#3a2418",
        "sail": "#7a4a2e", "sailMid": "#c86a34", "sailRim": "#2e1a12", "spine": "#9a6a44", "spineTip": "#d09060"}
GREY = {"back": "#4e5248", "head": "#4c5046", "limb": "#484c42", "jaw": "#7e8070", "belly": "#a8a690", "stripe": "#2a2c26",
        "sail": "#5a5a4c", "sailMid": "#8e8a5e", "sailRim": "#24261e", "spine": "#7e7a62", "spineTip": "#aaa47a"}
d = {
    "name": "dimetrodon",
    "_about": "SCULPTED (2026-11-08, tools/creaturegen/prehistoric/dimetrodon.py): DIMETRODON GRANDIS, an early Permian "
              "sphenacodontid SYNAPSID (not a dinosaur: on the line to the mammals), 3.2 m long, sprawling. The SAIL: one "
              "`fin` sheet in the midplane rooted along the back from the neck's root to the hips, its rim the exact outline "
              "over 19 neural spines -- low over the shoulders, highest (.9 m over the back) at mid-back, falling to the "
              "sacrum, a semicircular arc -- sagging a little between the spine tips (scalloped); thin (12 mm, a sharp rim), "
              "faired into the back; each spine a thin `horn` rising from inside the back THROUGH the sheet to just past its "
              "rim, standing out of both faces as a rib; the back's tone at its base, an ochre band up the middle, a dark rim. "
              "A deep narrow skull with a tall snout, the upper jaw margin STEPPED (a notch between premaxilla and maxilla "
              "for the lower jaw's big front teeth), the maxilla bowed down at the canines; differentiated teeth (horns): "
              "two premaxillary incisors, two great canine fangs each side, small cheek teeth; the lower front tusk and its "
              "row. The temporal opening a shallow hollow behind the eye. A deep rigid barrel trunk (the sail spans it: no "
              "trunk swing), sprawled legs with five clawed toes (claws horns, the 4th toe longest), a long tapering tail "
              "swinging as it walks. Muted olive-brown, scaly, dark bars across the back fading down the flanks and rings "
              "down the tail (paints: a coat recolours them), the belly and jaw pale. Coats: olive (the sail ochre-banded), "
              "rust, slate; variant `juvenile` (.4).",
    "kind": "parts",
    "flags": {"dinosaur": True, "print": "paw", "legLen": 0.4},
    "colors": COLORS,
    "coats": [{"name": "olive"}, {"name": "rust", "colors": RUST}, {"name": "slate", "colors": GREY}],
    "variants": {"olive": {"colors": {}}, "rust": {"colors": RUST}, "slate": {"colors": GREY}, "juvenile": {"scale": 0.4, "colors": {}}},
    "parts": parts,
    "sculpt": {
        "keep": [],
        "mesh": {"cell": 0.013, "tris": [11000, 3200], "focus": {"head": 3, "legFLl": 1.5, "legHLl": 1.5}},
        "shade": {"back": 0.85, "belly": 1.1, "on": "@back"},
        "shape": SH,
        "eyes": EYE,
    },
}

# ================= pass 2: the sharp parts, rooted on the probed skin
def back_table(xs):
    """the back's top along the midline: y where a ray down from above meets the skin"""
    ex = [s["id"] for s in SH if s.get("type") in ("horn", "fin")]
    hits = fd(SP, {"exclude": ex, "rays": [[[x, 0.42, 0], [x, 1.6, 0]] for x in xs]})["hits"]
    return [(x, h[1]) for x, h in zip(xs, hits) if h]

def sail():
    N = 21; XF, XR = 0.70, -0.46                       # the first and last spine
    xs = [XF + (XR - XF) * i / (N - 1) for i in range(N)]
    T = back_table([round(0.78 - 0.02 * k, 3) for k in range(64)])
    top = lambda x: interp(T, x)
    HMAX = 0.78
    out = []; tips = []
    for i, x in enumerate(xs):
        t = (x - XR) / (XF - XR)                       # 0 at the sacrum .. 1 over the shoulders
        u = t ** 1.08                                  # (the peak a touch behind the middle of the trunk: mid-back)
        h = 0.07 + (HMAX - 0.07) * math.sin(PI * u) ** 0.72
        lean = math.radians(-7 * (0.5 - t) * 2)        # (a slight fan: the front spines lean forward, the rear back)
        d = nrm([math.sin(lean), math.cos(lean), 0])
        b = [x, top(x), 0]
        tip = add(b, d, h)
        tips.append(tip)
        # (the spine: from 7 cm inside the back up through the sheet to 12 mm past its rim; round, tapering)
        r0 = 0.0125 if h > 0.3 else 0.0105
        pts = []
        for f, rr in ((-0.075, r0 * 1.5), (0.0, r0 * 1.45), (0.1, r0 * 1.15), (0.35, r0 * 0.85), (0.7, r0 * 0.62), (0.92, r0 * 0.45), (1.0, r0 * 0.3)):
            pts.append(add(b, d, h * f if f >= 0 else f) + [rr])
        pts.append(add(b, d, h + 0.012) + [0.0])
        out.append({"id": f"spine{i}", "type": "horn", "bone": "body", "pts": pts, "up": [1, 0, 0], "aspect": 1.25, "sides": 8,
                    "color": "@spine", "tip": "@spineTip", "tipAt": 0.7})
    # the sheet: root along the back (2.5 cm in), rear -> front; its rim from the rear base up over the tips to the front base
    rx0, rx1 = XR - 0.045, XF + 0.05
    root = [[x, top(x) - 0.025, 0] for x in [rx0 + (rx1 - rx0) * k / 8 for k in range(9)]]
    edge = [[rx0 + 0.004, top(rx0) + 0.008, 0, 1.0]]
    rev = list(reversed(tips))    # (rear first)
    corners = []
    for k, tp in enumerate(rev):
        if k:
            a = rev[k - 1]; L = ln(sub(tp, a)); sag = 0.22 * L
            for s in (0.25, 0.5, 0.75):
                q = lerp(a, tp, s); q[1] -= sag * 4 * s * (1 - s)
                edge.append(q[:3] + [1.0])
        corners.append(len(edge)); edge.append(tp[:3] + [1.0])
    edge.append([rx1 - 0.004, top(rx1) + 0.008, 0, 1.0])
    fin = {"id": "sail", "type": "fin", "bone": "body", "root": root, "edge": edge, "corners": corners,
           "thick": 0.012, "slope": 0.35, "swell": [0.02, 0.06, 1.2], "fair": {"r": 0.022, "rows": 3},
           "color": "@sail", "tip": "@sailMid", "tipAt": 0.3, "rim": 0.03, "rimColor": "@sailRim", "rimAt": 0.0,
           "n": 190, "across": 6}
    return [fin] + out

def teeth():
    """the teeth as horns, rooted inside the jaws (sunk on the field): upper ones outside the lower jaw"""
    from sharp2 import sink_many
    U = []
    # (x, y of the margin, z, length, root radius, rake: + forward)
    up = [("incisor1", 1.262, 0.428, 0.026, 0.028, 0.0085, 0.25), ("incisor2", 1.237, 0.427, 0.034, 0.03, 0.009, 0.15),
          ("fang1", 1.132, 0.426, 0.05, 0.058, 0.0135, -0.12), ("fang2", 1.103, 0.428, 0.05, 0.046, 0.012, -0.12)]
    for k, x in enumerate([1.072, 1.049, 1.026, 1.003, 0.98]):
        up.append((f"cheek{k + 1}", x, 0.432 + 0.0005 * k, 0.047 + 0.0005 * k, 0.014 - 0.0012 * k, 0.0048 - 0.0002 * k, -0.15))
    for nm, x, y, z, L, r, rake in up:
        a = [x, y + 0.012, z]; b = [x + rake * L, y - L, z + 0.002]
        U.append((nm, a, b, r, [-1, 0, 0], 0.07))
    lo = [("tusk", 1.168, 0.434, 0.03, 0.034, 0.0105, 0.08)]
    for k, x in enumerate([]):
        lo.append((f"lower{k + 1}", x, 0.433, 0.036, 0.012, 0.0048, 0.1))
    for nm, x, y, z, L, r, rake in lo:
        a = [x, y - 0.014, z]; b = [x + rake * L, y + L - 0.004, z - 0.001]
        U.append((nm, a, b, r, [-1, 0, 0], 0.06))
    P = [bent(a, b, r, bend=bd, up=upv, n=4, pw=0.85) for nm, a, b, r, upv, bd in U]
    ex = [s["id"] for s in SH if s.get("type") in ("horn", "fin")]
    P = sink_many(SP, P, ex, need=0.6)
    out = []
    for (nm, a, b, r, upv, bd), pts in zip(U, P):
        out.append({"id": nm, "type": "horn", "bone": "head", "pts": pts, "up": [1, 0, 0], "aspect": 1.15, "sides": 8,
                    "color": "@tooth", "fair": {"r": 0.004}, "mirror": True})
    return out

def claws():
    from sharp2 import sink_many
    P, M = [], []
    for nm, bone, tip, dvec, r in TOES:
        a = add(tip, dvec, -0.012); a[1] = 0.02
        b = add(tip, dvec, 0.03 if nm.startswith("toe") else 0.026); b[1] = 0.002
        P.append(bent(a, b, r * 0.95, bend=0.16, up=[0, 1, 0], n=4, pw=0.75)); M.append((nm, bone))
    ex = [s["id"] for s in SH if s.get("type") in ("horn", "fin")]
    P = sink_many(SP, P, ex, need=0.5)
    return [{"id": "claw" + nm[0].upper() + nm[1:], "type": "horn", "bone": bone, "pts": pts, "up": [0, 1, 0], "aspect": 1.2,
             "flat": 0.3, "sides": 8, "color": "@claw", "fair": {"r": 0.006}, "mirror": True} for (nm, bone), pts in zip(M, P)]

if __name__ == "__main__":
    dump(OUT, d)                                       # (pass 1: the body bare, to be probed)
    index_add(["creatures/" + SP])
    sh2 = sail() + teeth() + claws()
    SH += sh2
    dump(OUT, d)
    print(len(SH), "shapes,", len(sh2), "sharp")
