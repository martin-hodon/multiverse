# lynx.py -- THE EURASIAN LYNX on the big-cat frame (felid.py: the tiger's sculpt moved onto a lynx's proportions)
# ~1 m head-body, 0.65 m at the shoulder: short in the body and HIGH on long legs, the hindquarters higher than the
# shoulders; big round furred paws; a short bobbed tail with a black tip; a small round head framed by a RUFF of long
# fur (side-whiskers: pale, down the jaw line to points beside the throat, a dark line along the cheek); tall pointed ears, black-
# backed, each topped with a long black TUFT; sandy-grey to reddish with dark spots, white beneath
from felid import *
import math

# the ruff's dark line on the skin, (x, y, z, r) -- written by lynx_line.py
RUFFLINE = [[0.537, 0.7032, 0.0755, 0.0042], [0.523, 0.6884, 0.0943, 0.0055], [0.508, 0.6736, 0.1122, 0.006], [0.494, 0.6555, 0.1201, 0.0058], [0.484, 0.6397, 0.1211, 0.0048]]

P = {"s": 0.55, "sho": 0.4, "hip": -0.54, "dyF": 0.2, "dyH": 0.26, "g": 0.86, "legF": 1.22, "legH": 1.3, "gz": 0.9, "gneck": 0.95,
     "hs": [1.0, 1.04, 1.06], "eye": 1.05,
     "tail": {"R": 0.34, "a0": -0.5, "a1": -1.38, "r1": 0.075, "r2": 0.07, "n": 3, "sway": 18, "speed": 0.8}}

def build():
    M = Map(P)
    S = M.S
    hsm = sum(P["hs"]) / 3
    # (round 2: the LYNX pattern, coatpat.js 63 -- spots fine to bold, the bold ones on the flanks and legs; one solid
    #  space for all of it, so no per-part frames)
    dots = {"pat": "lynx", "frame": None}
    LF = lambda: dict(dots)
    LH = lambda: dict(dots)
    HEADF = dict(dots)
    big = lambda f, e: (lambda q: {**q, **e, "r": [q["r"][0] * f, q["r"][1] * 1.2, q["r"][2] * f]})
    edits = {
        "chest": dots, "loin": dots, "rump": dots, "scapula": dots, "withers": {**dots, "color": "@back"},
        "arm": dots, "triceps": dots, "thigh": dots, "neck": dots,
        "keel": {"pat": None, "color": "@white", "kc": 0.05}, "pouch": {"pat": None, "color": "@white", "kc": 0.05},
        "belly": lambda q: {**q, "pat": None, "color": "@white", "kc": 0.06, "r": [q["r"][0], q["r"][1] * 1.08, q["r"][2] * 1.12]},
        # (round 2) THE LEGS JOINTED: a thick forearm down to a WRIST, the pastern below it sloping forward (the carpal
        # bend) to a broad flat paw with four toe lobes; behind, the point of the HOCK and the long sloping metatarsus
        "forearm": lambda q: {**q, **LF(), "color": "@body", "b": [0.226, 0.1, q["a"][2]], "ra": 0.065, "rb": 0.036},
        "flexor": lambda q: {**q, **LF(), "color": "@body", "r": [x * 1.15 for x in q["r"]]},
        "pastern": lambda q: {**q, **LF(), "color": "@leg", "a": [0.228, 0.095, q["a"][2]], "b": [0.252, 0.042, q["a"][2]], "ra": 0.031, "rb": 0.035},
        "gaskin": lambda q: {**q, **LH(), "color": "@body", "ra": q["ra"] * 1.12, "rb": q["rb"] * 1.1},
        "hock": lambda q: {**q, **LH(), "color": "@body", "a": [-0.322, 0.215, q["a"][2]], "b": [-0.298, 0.062, q["a"][2]], "ra": 0.033, "rb": 0.029},
        # BROAD furred paws, flat on the ground, the leg's own colour (snowshoes): the palm here, the toes added below
        "paw": lambda q: {**q, "color": "@leg", "pat": None, "c": [0.268, 0.026, q["c"][2]], "r": [0.05, 0.026, 0.048]},
        "hpaw": lambda q: {**q, "color": "@leg", "pat": None, "c": [-0.27, 0.025, q["c"][2]], "r": [0.05, 0.025, 0.047]},
        "throat": lambda q: {**q, "color": "@white", "kc": 0.03},
        "skull": HEADF, "cheek": {**HEADF, "color": "@body"}, "bridge": {**HEADF, "color": "@body"},
        "muzzle": {"color": "@muzzle", "pat": None}, "pad": {"color": "@white"}, "chin": {"color": "@white"}, "jowl": {"color": "@white"},
        "brow": {"color": "@body"},
        # (round 2: the tiger's neck ruff dropped -- it read as a bib; the side-whiskers are added below, on the face)
        "ruff": lambda q: None,
    }
    J = sc(M.head(HJ, 1.0), S)                      # the head's pivot, in metres
    f = S * hsm
    o = lambda dx, dy, dz=0.0: [J[0] + dx * f, J[1] + dy * f, J[2] + dz * f]   # (tiger-head units from the head's pivot)
    def add(M, P):
        hd = {"bone": "head"}
        # (round 3) THE RUFF: a furry fringe on the back of each cheek -- from under the ear down the jaw line, widening
        # downward to POINTS hanging beside the throat; masses blended into the cheek and neck (no flap, no slot)
        rf = {**hd, "color": "@ruff", "mirror": True}
        out = [
            {"id": "ruffCheek", "type": "ell", **rf, "c": [0.474, 0.64, 0.083], "r": [0.034, 0.072, 0.036], "rot": [0, 0, -12], "k": 0.022, "kc": 0.01},
            {"id": "ruffLow", "type": "ell", **rf, "c": [0.476, 0.567, 0.08], "r": [0.044, 0.04, 0.036], "k": 0.022, "kc": 0.01},
            {"id": "ruffTipA", "type": "cone", **rf, "a": [0.478, 0.565, 0.084], "b": [0.458, 0.49, 0.1], "ra": 0.028, "rb": 0.005, "k": 0.014, "kc": 0.008},
            {"id": "ruffTipB", "type": "cone", **rf, "a": [0.503, 0.572, 0.078], "b": [0.5, 0.508, 0.074], "ra": 0.022, "rb": 0.004, "k": 0.012, "kc": 0.008},
            {"id": "ruffTipC", "type": "cone", **rf, "a": [0.452, 0.575, 0.082], "b": [0.425, 0.512, 0.094], "ra": 0.022, "rb": 0.004, "k": 0.012, "kc": 0.008},
        ]
        # its dark marking: a THIN line ON the outer face -- from the eye's outer corner back across the cheek and into
        # the ruff's top; dark brown, not black, ending on the tan cheek (points on the skin: RUFFLINE, probed by lynx_line.py)
        out.append({"id": "ruffLine", "type": "tube", **hd, "op": "paint", "pts": RUFFLINE, "kc": 0.0015, "color": "@line", "mirror": True})
        # the paws' TOE LOBES: four along each paw's front edge, the outer ones set back
        for i, dz in enumerate((-0.033, -0.011, 0.011, 0.033)):
            back = 0.008 if abs(dz) > 0.02 else 0.0
            out.append({"id": f"toeF{i}", "type": "ell", "bone": "footFL", "c": [0.3 - back, 0.019, 0.0817 + dz], "r": [0.021, 0.019, 0.0155], "k": 0.005, "kc": 0.002, "color": "@leg", "mirror": True})
            out.append({"id": f"toeH{i}", "type": "ell", "bone": "footHL", "c": [-0.236 - back, 0.018, 0.0634 + dz * 0.95], "r": [0.02, 0.018, 0.015], "k": 0.005, "kc": 0.002, "color": "@leg", "mirror": True})
        out += [
            {"id": "wrist", "type": "ell", "bone": "legFLl", "c": [0.227, 0.092, 0.0817], "r": [0.034, 0.026, 0.033], "k": 0.012, "color": "@leg", "pat": "lynx", "mirror": True},
            {"id": "carpal", "type": "ell", "bone": "footFL", "c": [0.205, 0.068, 0.0817], "r": [0.014, 0.019, 0.016], "k": 0.008, "color": "@leg", "mirror": True},
            {"id": "hockPt", "type": "sphere", "bone": "legHLl", "c": [-0.343, 0.205, 0.0644], "r": 0.02, "k": 0.012, "color": "@body", "pat": "lynx", "mirror": True},
        ]
        # TALL POINTED EARS (cupped triangles), black-backed, pale inside, each topped with a long black TUFT
        Bi, Bo, M0, T = o(-0.04, 0.10, 0.045), o(-0.09, 0.07, 0.14), o(-0.085, 0.095, 0.09), o(-0.085, 0.235, 0.125)
        out += cup_ear(Bi, Bo, M0, T, 0.0058, k=0.006 * f, col="@ear", colIn="@earIn")   # (5.8 mm: thick enough for the field's grid -- a thinner one is a flat detail and its tufts float)
        out += [
            {"id": "earBack", "type": "tri", "bone": "earL", "a": [Bi[0] - 0.012 * f, Bi[1] + 0.03 * f, Bi[2]], "b": [Bo[0] - 0.004 * f, Bo[1] + 0.03 * f, Bo[2]],
             "c": T, "r": 0.0056, "k": 0.004 * f, "kc": 0.002 * f, "color": "@black", "mirror": True},
            {"id": "earTuft", "type": "cone", "bone": "earL", "a": [T[0] + 0.004 * f, T[1] - 0.01 * f, T[2]], "b": [T[0] - 0.01 * f, T[1] + 0.12 * f, T[2] - 0.006 * f],
             "ra": 0.009 * f, "rb": 0.002 * f, "k": 0.004 * f, "kc": 0.002 * f, "color": "@black", "mirror": True},
            {"id": "earTuft2", "type": "cone", "bone": "earL", "a": [T[0], T[1] - 0.006 * f, T[2] + 0.004 * f], "b": [T[0] - 0.02 * f, T[1] + 0.1 * f, T[2] + 0.008 * f],
             "ra": 0.006 * f, "rb": 0.0015 * f, "k": 0.003 * f, "kc": 0.002 * f, "color": "@black", "mirror": True},
        ]
        return out
    M, R, shapes, eyes = felid(P, edits, add, drop=("ear", "earIn"))
    eyes["iris"] = "@eye"
    shapes = head_pass(shapes, eyes, lambda p: H(M, P, p), M.S * hsm, {"tear": "@tear", "tearW": 0.0045, "noseC": "@nose", "ears": 1.0, "earZ": 0.0,
                                                                     "earY": 0.0, "nose": 0.85, "eyeBall": "#6a5a24", "eye": 0.95, "snout": -0.004})
    # the rig's ears where the cupped ears stand (they flick about their own base: written before the frame's headScale)
    NEm = R["neck"][3:6]
    un = lambda p: [NEm[k] + (p[k] - NEm[k]) / HS0 for k in range(3)]
    Bm = o(-0.065, 0.085, 0.09)
    R["ears"] = un(Bm) + un(o(-0.08, 0.2, 0.12)) + [0.03 * f / HS0, 0.006 * f / HS0]
    # THE BOBBED TAIL: short and thick, its last third black
    tail = arc_tail(R["tail"], lambda t, P0, P1, r: {"color": "@black"} if t > 0.62 else {"color": "@tail", "pat": None}, n=3, tip="@black")
    tail[0]["ra"] *= 1.3; tail[0]["k"] *= 2.5
    shapes += tail
    out = {"name": "lynx",
           "_about": ("the Eurasian lynx SCULPTED on the cat frame (2026-11-06, gen: scratchpad sc/m5/lynx.py from the tiger's shapes): "
                      "a metre head-body and 65 cm at the shoulder -- short in the body and high on long legs, the hindquarters "
                      "above the shoulders; big round furred paws; a short bobbed tail with a black tip; a small round head framed "
                      "by a ruff of pale fur down the jaw line to points beside the throat, a thin dark line along each cheek, tall pointed black-backed ears each with "
                      "a long black tuft; sandy-grey to reddish, spotted small to medium (coats: grey, red, heavily spotted), white beneath. "
                      "Shy and solitary: one at the forest's edge"),
           "use": "creatures/frames/cat",
           "shy": 12, "headTurn": 22, "pupil": "slit",
           "params": {"s": P["s"], "tuft": 0.0, "tailSway": 18},
           **{k: R[k] for k in ("rear", "front", "neck", "head", "muzzle", "nose", "ears", "eyes")},
           "legs": R["legs"], "tail": R["tail"],
           "colors": {"body": "#b38f66", "back": "#a7825a", "muzzle": "#e2d6c2", "ear": "#8a6e50", "earIn": "#e6dccc", "leg": "#b08c64", "eye": "#b9a03c",
                      "nose": "#b07a6a", "tail": "#ae8a62", "white": "#efe9de", "ruff": "#d9cdb8", "black": "#1a1512", "tear": "#5a4430", "line": "#3b2c20"},
           "coats": [{},
                     {"name": "grey", "colors": {"body": "#a39886", "back": "#958a78", "leg": "#9e9482", "tail": "#9a907e", "ear": "#7a705f", "ruff": "#ddd6ca"}},
                     {"name": "red", "colors": {"body": "#b9845a", "back": "#ab764c", "leg": "#b48056", "tail": "#b07e54", "ear": "#8a6040"}}],
           "variants": {"spotted": {"params": {"ps": 0.8}, "colors": {"body": "#be8c5e", "back": "#b07e50", "leg": "#b88658"}}},
           "print": "paw",
           "sculpt": {"keep": [], "patScale": "ps", "mesh": {"tris": [7000, 2300], "cell": 0.0068, "focus": {"head": 5}, "anchor": 200}, "shape": shapes, "eyes": eyes,
                      "coat": {"gap": 0.0075, "len": 0.04, "r": 0.0024, "sides": 3, "lean": 0.95, "vary": 0.3, "skirt": -1.2, "drop": 0,
                               "face": 0.6, "rise": 0.3, "tip": "#e8e0d2", "base": "#8a7660", "dark": 0.3, "darkTip": "#2a221a", "hold": 0.55}}}
    out["params"]["ps"] = 1.0
    save("lynx", out)

build()
