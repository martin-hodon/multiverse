# gen.py (2026-11-08): the PREHISTORIC MAMMALS -- uintatherium, brontotherium (Megacerops), elasmotherium -- written
# from scratch as sculpted rig animals on the rhinoceros' body plan (a mammals.js rig of their own proportions: the
# same bones, IK legs, gaits, rider; the `sculpt` overlay their surface). Every horn, knob, tusk and nail a sharp
# `horn` (sharp.js), faired into the skin where it grows; the ears the rhinoceros' cupped `fin` moved and scaled.
#   python3 tools/creaturegen/prehistoric/gen.py [uintatherium brontotherium elasmotherium]
# It writes assets/creatures/mammals/<name>.json whole (nothing else made them: re-running is safe).
import sys, math, copy
from plib import *   # noqa

def legs(S, J, F, H):
    """the four legs' shapes on their bones from the rig's joints. F, H: dicts of the fore and hind leg's radii and
    feet -- arm (ra, rb), fore (ra, rb), foot (rx, ry, rz), scap (rx, ry, rz), thigh (rx, ry, rz), gaskin, cannon"""
    hf, kf, ff = J["legFLu"], J["legFLl"], J["footFL"]
    hh, kh, fh = J["legHLu"], J["legHLl"], J["footHL"]
    col = F.get("color", "@leg"); low = F.get("low", "@dust"); pat = F.get("pat")
    pk = {"pat": pat} if pat else {}
    hk = {"hair": F["hair"]} if F.get("hair") else {}
    # (the shoulder blade well inside the trunk's side and widely blended: standing proud of it, it read as a cylinder
    # pressed into the body, a hard groove behind it)
    S.ell("scapula", add(hf, [-0.08, 0.16, -0.02 - F.get("scapIn", 0.09)]), F["scap"], F.get("scapColor", "@skin"), bone="legFLu",
          k=F.get("scapK", 0.18), rot=[0, 0, 15], mirror=True, **pk, **hk)
    S.cone("arm", add(hf, [0, -0.04, 0]), kf, F["arm"][0], F["arm"][1], col, bone="legFLu", k=0.08, mirror=True, **pk, **hk)
    S.cone("fore", add(kf, [0, 0.01, 0]), add(ff, [0.0, 0.05, 0]), F["fore"][0], F["fore"][1], low, bone="legFLl", k=0.05, mirror=True, **pk)
    S.ell("foot", add(ff, [0.02, 0, 0]), F["foot"], "@foot", bone="footFL", k=0.04, mirror=True)
    S.ell("thigh", add(hh, [0.03, -0.12, -H.get("thighIn", 0.03)]), H["thigh"], H.get("thighColor", "@skin"), bone="legHLu", k=0.14, rot=[0, 0, -10], mirror=True, **pk, **hk)
    S.cone("gaskin", add(hh, [0.04, -0.36, 0]), kh, H["gaskin"][0], H["gaskin"][1], col, bone="legHLu", k=0.06, mirror=True, **pk, **hk)
    S.cone("cannon", add(kh, [0, 0.01, 0]), add(fh, [0, 0.05, 0]), H["cannon"][0], H["cannon"][1], low, bone="legHLl", k=0.04, mirror=True, **pk)
    S.ell("hfoot", add(fh, [0.02, 0, 0]), H["foot"], "@foot", bone="footHL", k=0.04, mirror=True)
    out = nails("nail", "footFL", add(ff, [0.02, 0, 0]), F["foot"][0], F["foot"][2], F["toes"], r=F.get("nailR", 0.034),
                **{k: F[k] for k in ("reach", "drop") if k in F})
    out += nails("hnail", "footHL", add(fh, [0.02, 0, 0]), H["foot"][0], H["foot"][2], H["toes"], r=H.get("nailR", 0.034),
                 **{k: H[k] for k in ("reach", "drop") if k in H})
    return out


def eye_mound(d, S):
    """a low mound under each eye, so the eyeball sits in a convex lid: on a face that falls away below the eye the
    socket's lower rim (painted wet, `lid`) showed as a pale tear-drop under it"""
    E = d["sculpt"]["eyes"]; r = E["r"]
    d["sculpt"]["shape"] = list(S)
    hit = probe(d, {"rays": [[[E["at"][0], E["at"][1], 1.0], [E["at"][0], E["at"][1], 0.0]]]})["hits"][0]
    S.ell("eyeMound", [E["at"][0], E["at"][1], round(hit[2] - 0.5 * r, 4)], [r * 1.8, r * 1.7, r * 1.1], "@skin",
          bone="head", k=round(r * 0.6, 4), mirror=True)


def finish(d, S, sharp, J, horn_ids=()):
    """the field shapes (and a mound under each eye), then the sharp parts with their roots sunk into the field"""
    eye_mound(d, S)
    d["sculpt"]["shape"] = list(S)
    sink_horns(d, [h for h in sharp if h["id"] in horn_ids])
    d["sculpt"]["shape"] = list(S) + sharp
    return d


# ======================================================================================================================
def uintatherium():
    d = {
        "name": "uintatherium", "kind": "mammal", "headForm": "bovid", "headScale": 0.8, "headTurn": 8, "graze": 0.35,
        "fur": False, "call": "rhinoceros", "print": "pad", "mount": {"h": 2.3, "speed": 1.2},
        "params": {"bull": True, "cow": False, "grown": True},
        "rear": [-0.85, 1.15, 0, 0.85, 0.55, 0.58],
        "front": [0.55, 1.22, 0, 0.8, 0.58, 0.58],
        "neck": [1.0, 1.32, 0, 1.3, 1.28, 0, 0.36, 0.3],
        "head": [1.5, 1.26, 0, 0.26],
        "muzzle": [1.62, 1.18, 0, 2.05, 1.06, 0, 0.15, 0.1],
        "ears": [1.33, 1.31, 0.14, 1.3, 1.43, 0.18, 0.05, 0.025],
        "eyes": [1.74, 1.24, 0.14, 0.02],
        "legs": {"front": [0.72, 1.08, 0.36, 0.55], "hind": [-0.92, 1.12, 0.34, 0.6], "radii": [0.19, 0.15, 0.13],
                 "foot": [0.15, 0.07, 0.15]},
        "tail": {"path": [[-1.33, 1.4], [-1.44, 1.35], [-1.51, 1.23], [-1.535, 1.09]], "r1": 0.05, "r2": 0.028, "tuft": 0,
                 "sway": 14, "speed": 1.0},
        "c": {"body": "#7a6f63", "skin": "#7a6f63", "back": "#6c6257", "belly": "#8a7e70", "front": "#7f7468",
              "muzzle": "#83786b", "dust": "#7e7365", "fold": "#665c52", "leg": "#6c6258", "foot": "#625850",
              "eye": "#2a2018", "lid": "#4e463e", "lip": "#6e655b", "knob": "#776b5e", "knobTip": "#655a4f",
              "tusk": "#dccfb2", "tuskTip": "#b9a988", "nail": "#8a7f70", "ear": "#7a6f63", "earIn": "#857a6d",
              "tail": "#7a6f63", "tuft": "#3e362e"},
    }
    d["sculpt"] = {"keep": [], "mesh": {"cell": 0.03, "tris": [8000, 2400], "focus": {"head": 4, "tail": 3}, "symmetric": True},
                   "eyes": {"at": [1.745, 1.245, 0.14], "from": [1.6, 1.245, 0], "r": 0.02, "iris": "#2a2018", "pupil": "round", "lid": "@lid", "sink": 0.4, "socket": 0.9},
                   "shade": {"back": 0.86, "belly": 1.1, "low": 0.95, "on": "@skin"}, "shape": []}
    HO, HS, dO = [1.45, 1.27, 0], 1.15, [0.03, 0.06, 0]   # (the head drawn below in a design frame, then scaled and raised)
    xrig(d, HO, HS, dO)
    J = joints(d)
    S = Shapes()
    # ---- the trunk: a heavy rhino-like barrel, withers and rump about level
    S.ell("barrel", [-0.15, 1.12, 0], [1.18, 0.48, 0.6], "@skin", k=0.16)
    S.ell("saddle", [-0.12, 1.42, 0], [0.75, 0.18, 0.4], "@back", k=0.14)
    S.ell("withers", [0.42, 1.38, 0], [0.55, 0.26, 0.46], "@back", k=0.18)
    S.ell("rump", [-0.9, 1.22, 0], [0.5, 0.42, 0.55], "@back", k=0.14, rot=[0, 0, 12])
    S.ell("belly", [-0.1, 0.85, 0], [0.82, 0.25, 0.54], "@belly", k=0.16)
    S.ell("chest", [0.62, 1.04, 0], [0.48, 0.42, 0.5], "@skin", k=0.18)
    S.ell("neck", [1.08, 1.25, 0], [0.34, 0.3, 0.3], "@skin", k=0.12, rot=[0, 0, -20])
    S.ell("dewlap", [1.12, 1.06, 0], [0.26, 0.14, 0.2], "@skin", k=0.1, rot=[0, 0, -10])
    sharp = legs(S, J,
                 {"scap": [0.26, 0.38, 0.17], "arm": [0.21, 0.15], "fore": [0.14, 0.13], "foot": [0.15, 0.07, 0.15],
                  "toes": [-48, -24, 0, 24, 48], "nailR": 0.03, "reach": 0.99, "drop": 0.05},
                 {"thigh": [0.34, 0.44, 0.24], "gaskin": [0.18, 0.13], "cannon": [0.13, 0.125], "foot": [0.15, 0.07, 0.14],
                  "toes": [-48, -24, 0, 24, 48], "nailR": 0.03, "reach": 0.99, "drop": 0.05})
    # ---- the head: long and low, a small brain case, the skull roof dished between three pairs of bony knobs
    S0 = Shapes(); S, Sb = S0, S
    S.ell("cranium", [1.47, 1.31, 0], [0.22, 0.16, 0.16], "@skin", bone="head", k=0.08, rot=[0, 0, -8])
    S.ell("roof", [1.68, 1.33, 0], [0.3, 0.06, 0.12], "@skin", bone="head", k=0.06, rot=[0, 0, -10])
    S.cone("face", [1.55, 1.27, 0], [2.03, 1.12, 0], 0.15, 0.095, "@skin", bone="head", k=0.07)
    S.ell("cheek", [1.6, 1.2, 0.11], [0.17, 0.09, 0.06], "@skin", bone="head", k=0.06, mirror=True)
    S.cone("jaw", [1.42, 1.13, 0], [1.9, 1.0, 0], 0.1, 0.06, "@skin", bone="head", k=0.06)
    # (the lower jaw's FLANGE: a flat bony blade hanging down each side of the chin, the tusk's tip resting outside it)
    S.append(gate(S.box("flange", [1.87, 0.895, 0.07], [0.07, 0.095, 0.015], "@skin", bone="head", k=0.03, round=0.022, rot=[0, 0, 14], mirror=True), ["bull"])); S.pop(-2)
    S.append(gate(S.box("flangeCow", [1.885, 0.935, 0.068], [0.07, 0.06, 0.015], "@skin", bone="head", k=0.03, round=0.013, rot=[0, 0, 14], mirror=True), ["cow"])); S.pop(-2)
    S.ell("chin", [1.93, 0.98, 0], [0.06, 0.05, 0.055], "@lip", bone="head", k=0.04)
    S.ell("lip", [2.06, 1.075, 0], [0.08, 0.065, 0.085], "@lip", bone="head", k=0.05)
    S.ell("nostril", [2.125, 1.11, 0.04], [0.02, 0.012, 0.014], "@lid", bone="head", k=0.008, op="sub", rot=[0, 25, -20], mirror=True)
    S.ell("mouth", [2.03, 1.022, 0], [0.07, 0.006, 0.075], "@lid", bone="head", k=0.008, op="sub")
    S = Sb
    for sh in S0: S.append(xshape(sh, HO, HS, dO))
    S.ell("tailDock", [-1.33, 1.4, 0], [0.08, 0.065, 0.07], "@back", k=0.05, rot=[0, 0, 30])
    S.tube("tail", [[-1.33, 1.4, 0, 0.052], [-1.41, 1.37, 0, 0.046], [-1.475, 1.3, 0, 0.039], [-1.515, 1.2, 0, 0.032], [-1.535, 1.09, 0, 0.025]],
           "@tail", bone="tail", k=0.02)
    S.tube("tailBrush", [[-1.533, 1.12, 0, 0.025], [-1.537, 1.07, 0, 0.03], [-1.54, 1.02, 0, 0.022], [-1.542, 0.98, 0, 0.006]],
           "@tuft", bone="tail", k=0.015, hair=1)
    # ---- the sharp parts: the three pairs of knobs, the bull's sabre tusks, the ears
    def K(id, b, t, r, f=1.0, **kw):   # (a knob; f < 1 the cow's: shorter, a little slimmer)
        t = add(b, sub(t, b), f); r = r * f ** 0.5
        return knob(id, b, t, r, fair={"r": round(r * 0.55, 4), "skin": 0.45}, tipc="@knobTip", tipAt=0.7, caps=(35, 62), **kw)
    def knobs(f, sfx, when):
        return [gate(h, when) for h in [
            K("knobP" + sfx, [1.44, 1.38, 0.09], [1.37, 1.6, 0.18], 0.072, f, bend=[0, 0, 1], bendAmt=0.05, up=[1, 0, 0], blunt=0.42),
            K("knobM" + sfx, [1.8, 1.29, 0.095], [1.83, 1.42, 0.15], 0.05, f, up=[1, 0, 0], blunt=0.42),
            K("knobN" + sfx, [2.05, 1.145, 0.048], [2.1, 1.215, 0.07], 0.032, f, up=[1, 0, 0], blunt=0.45)]]
    TP = [[1.9, 1.13, 0.082, 0.024], [1.905, 1.03, 0.09, 0.025], [1.895, 0.93, 0.1, 0.022], [1.875, 0.85, 0.104, 0.014], [1.85, 0.79, 0.106, 0.0]]
    def tusk(id, f, when):   # (the bull's dagger past the chin; the cow's a short canine, f of its length below the root)
        P = [[p[0], TP[0][1] + (p[1] - TP[0][1]) * f, p[2], p[3] * (0.75 + 0.25 * f)] for p in TP]
        return gate(curve_horn(id, P, "@tusk", mirror=True, fair=0.016, up=[1, 0, 0], aspect=1.5, tip="@tuskTip", tipAt=0.65), when)
    horns = knobs(1.0, "", ["bull"]) + knobs(0.62, "Cow", ["cow"]) + [tusk("tusk", 1.0, ["bull", "grown"]), tusk("tuskCow", 0.42, ["cow", "grown"])]
    horns = [xshape(h, HO, HS, dO) for h in horns]
    ear = ear_from_rhino(J["earL"], s=0.75, tilt=25, out=30, yaw=55)
    sharp = horns + sharp + [ear]
    finish(d, S, sharp, J, horn_ids=[h["id"] for h in horns])
    d["coats"] = [{"name": "grey-brown"},
                  {"name": "dun", "body": "#8b7a62", "skin": "#8b7a62", "back": "#7a6a54", "belly": "#a08e74", "front": "#90806a",
                   "leg": "#7a6a56", "dust": "#8c7c66", "knob": "#85745e", "tail": "#8b7a62"},
                  {"name": "slate", "body": "#5f5d5a", "skin": "#5f5d5a", "back": "#54524f", "belly": "#73706a", "front": "#64625e",
                   "leg": "#53514d", "dust": "#625f5a", "knob": "#5c5955", "fold": "#4e4c49", "tail": "#5f5d5a"}]
    d["variants"] = {"cow": {"params": {"bull": False, "cow": True}, "scale": 0.88,
                             "colors": {"skin": "#80766a", "body": "#80766a", "back": "#72685d", "belly": "#908476"}}}
    d["young"] = {"s": 0.35, "n": 1, "side": 1.6, "hop": 0.02, "name": "uintatherium calf"}
    d["_about"] = ("UINTATHERIUM (Eocene North America, 2026-11-08; generator tools/creaturegen/prehistoric/gen.py): a uintathere "
                   "about 3.9 m long and 1.6 m at the shoulder, some 2 t -- a heavy rhino-like barrel on stout pillar legs, "
                   "five-toed pad feet (five hoof-nails each); a long low skull with a small brain case, its roof dished "
                   "between THREE PAIRS of blunt skin-covered bony knobs -- a small pair on the nose tip, a pair before the "
                   "eyes, the largest at the back of the skull above the ears, leaning out; the bull's long dagger UPPER "
                   "CANINES hanging past the chin beside the bony downward FLANGE of the lower jaw that guards them; small "
                   "rhino-like ears, a short tail; grey-brown, near-hairless skin. Every knob, tusk and nail a sharp `horn` "
                   "faired into the skin; the ears the rhinoceros' cupped `fin` scaled. Coats grey-brown, dun, slate; "
                   "variant `cow` (smaller, short tusks and knobs).")
    return d


def place_eye(d, S, x, y):
    """the eye (rig and sculpt) put on the field's surface at x, y: a ray in from the side"""
    d["sculpt"]["shape"] = list(S)
    hit = probe(d, {"rays": [[[x, y, 1.0], [x, y, 0.0]]]})["hits"][0]
    z = round(hit[2], 4)
    E = d["sculpt"]["eyes"]; E["at"] = [round(x, 4), round(y, 4), z]; E["from"] = [round(x - 0.15, 4), round(y, 4), 0]
    d["eyes"] = [round(x, 4), round(y, 4), z, d["eyes"][3]]
    return z


def hang_tail(d, S, y0, L, r1, r2, color="@tail", tuft="@tuft", brush=0.07, lean=0.16, hair=None):
    """a short hanging tail rooted ON the rump's rear surface at height y0 (found by a ray through the field shapes so
    far): the rig's tail path and its tube, a dark brush at the end"""
    d["sculpt"]["shape"] = list(S)
    hit = probe(d, {"rays": [[[d["rear"][0], y0, 0], [d["rear"][0] - 3, y0, 0]]]})["hits"][0]
    x0 = hit[0] + r1 * 0.3
    P = [[x0, y0], [x0 - L * lean * 0.9, y0 - L * 0.22], [x0 - L * lean * 1.4, y0 - L * 0.55], [x0 - L * lean * 1.55, y0 - L]]
    d["tail"] = {"path": [[round(a, 4), round(b, 4)] for a, b in P], "r1": r1, "r2": r2, "tuft": 0, "sway": 14, "speed": 1.0}
    n = 6; pts = []
    for i in range(n):   # (a Catmull-Rom-ish sampling of the path: piecewise linear is enough at this size)
        t = i / (n - 1) * 3; k = min(int(t), 2); u = t - k
        a, b = P[k], P[k + 1]
        pts.append([round(a[0] + (b[0] - a[0]) * u, 4), round(a[1] + (b[1] - a[1]) * u, 4), 0, round(r1 + (r2 - r1) * i / (n - 1), 4)])
    S.ell("tailDock", [x0, y0, 0], [r1 * 1.6, r1 * 1.3, r1 * 1.4], "@back", k=r1, rot=[0, 0, 30])
    hk = {"hair": hair, "pat": "shag"} if hair else {}
    S.tube("tail", pts, color, bone="tail", k=r2 * 0.8, **hk)
    e = pts[-1]
    S.tube("tailBrush", [[e[0] + 0.002, e[1] + brush * 0.45, 0, r2], [e[0] - 0.002, e[1], 0, r2 * 1.25], [e[0] - 0.004, e[1] - brush * 0.55, 0, r2 * 0.9],
                         [e[0] - 0.006, e[1] - brush, 0, r2 * 0.25]], tuft, bone="tail", k=r2 * 0.6, hair=1)


# ======================================================================================================================
def brontotherium():
    d = {
        "name": "brontotherium", "kind": "mammal", "headForm": "bovid", "headScale": 0.8, "headTurn": 8, "graze": 0.4,
        "fur": False, "call": "rhinoceros", "print": "pad", "mount": {"h": 3.2, "speed": 1.3},
        "params": {"bull": True, "cow": False, "grown": True},
        "rear": [-1.15, 1.75, 0, 1.0, 0.68, 0.72],
        "front": [0.7, 1.9, 0, 1.0, 0.75, 0.75],
        "neck": [1.35, 2.05, 0, 1.75, 1.85, 0, 0.5, 0.4],
        "head": [2.0, 1.9, 0, 0.36],
        "muzzle": [2.15, 1.8, 0, 2.72, 1.6, 0, 0.22, 0.16],
        "ears": [1.86, 2.1, 0.18, 1.82, 2.27, 0.24, 0.07, 0.03],
        "eyes": [2.3, 1.86, 0.19, 0.025],
        "legs": {"front": [1.0, 1.62, 0.46, 0.82], "hind": [-1.35, 1.6, 0.44, 0.84], "radii": [0.26, 0.2, 0.17],
                 "foot": [0.2, 0.09, 0.19]},
        "tail": {"path": [[-2.0, 2.0], [-2.1, 1.9], [-2.15, 1.72], [-2.16, 1.55]], "r1": 0.06, "r2": 0.03, "tuft": 0, "sway": 14, "speed": 1.0},
        "c": {"body": "#6e6458", "skin": "#6e6458", "back": "#62594e", "belly": "#80766a", "front": "#746a5e",
              "muzzle": "#776d61", "dust": "#655d53", "fold": "#5a5248", "leg": "#625a50", "foot": "#585048",
              "eye": "#24180f", "lid": "#463e36", "lip": "#665d53", "horn": "#6a6055", "hornTip": "#5c5348",
              "nail": "#857a6c", "ear": "#6e6458", "earIn": "#7a7064", "tail": "#6e6458", "tuft": "#332c26"},
    }
    d["sculpt"] = {"keep": [], "mesh": {"cell": 0.038, "tris": [8500, 2600], "focus": {"head": 4, "tail": 3}, "symmetric": True},
                   "eyes": {"at": [2.3, 1.86, 0.19], "from": [2.15, 1.86, 0], "r": 0.02, "iris": "#24180f", "pupil": "round", "lid": "@lid", "sink": 0.4, "socket": 0.9},
                   "shade": {"back": 0.86, "belly": 1.1, "low": 0.95, "on": "@skin"}, "shape": []}
    HO, HS, dO = [2.0, 1.9, 0], 1.1, [0.02, 0.02, 0]   # (the head drawn in a design frame, then scaled)
    xrig(d, HO, HS, dO)
    J = joints(d)
    S = Shapes()
    # ---- the trunk: the high withers hump over the shoulders (the long spines of the thoracic vertebrae), the back
    #      sloping down to a lower rump; a deep barrel
    S.ell("barrel", [-0.2, 1.58, 0], [1.6, 0.55, 0.75], "@skin", k=0.18)
    S.ell("hump", [0.55, 2.13, 0], [0.72, 0.4, 0.46], "@back", k=0.16, rot=[0, 0, -6])
    S.ell("spine", [0.42, 2.24, 0], [0.5, 0.22, 0.3], "@back", k=0.14, rot=[0, 0, -8])
    S.ell("saddle", [-0.6, 1.94, 0], [0.92, 0.2, 0.55], "@back", k=0.16, rot=[0, 0, 10])
    S.ell("rump", [-1.3, 1.72, 0], [0.6, 0.48, 0.68], "@back", k=0.16, rot=[0, 0, 10])
    S.ell("belly", [-0.15, 1.27, 0], [1.1, 0.3, 0.68], "@belly", k=0.18)
    S.ell("chest", [0.9, 1.6, 0], [0.6, 0.55, 0.6], "@skin", k=0.2)
    S.ell("shoulder", [0.82, 1.78, 0.22], [0.48, 0.55, 0.38], "@skin", k=0.2, mirror=True)
    S.tube("spineLine", [[-1.3, 1.82, 0, 0.36], [-0.6, 1.86, 0, 0.36], [0.1, 2.06, 0, 0.4], [0.6, 2.12, 0, 0.4], [1.1, 1.98, 0, 0.34]], "@back", k=0.22)
    S.ell("neck", [1.45, 1.95, 0], [0.45, 0.42, 0.4], "@skin", k=0.14, rot=[0, 0, -20])
    S.ell("dewlap", [1.5, 1.66, 0], [0.32, 0.18, 0.26], "@skin", k=0.12, rot=[0, 0, -10])
    sharp = legs(S, J,
                 {"scap": [0.33, 0.48, 0.21], "scapIn": 0.2, "arm": [0.27, 0.2], "fore": [0.19, 0.17], "foot": [0.2, 0.09, 0.19],
                  "toes": [-54, -18, 18, 54], "nailR": 0.04},
                 {"thigh": [0.44, 0.56, 0.3], "gaskin": [0.24, 0.17], "cannon": [0.17, 0.165], "foot": [0.2, 0.09, 0.18],
                  "toes": [-40, 0, 40], "nailR": 0.045})
    # ---- the head: a long skull, its profile SADDLE-SHAPED -- the back of the skull high, the face dipping, the nose
    #      rising again into the forked horn; wide cheekbones, small eyes
    H = "head"
    S0 = Shapes(); S, Sb = S0, S
    # (broad and heavy, a horse's face is the thing to avoid: the cranium wide, the face a deep box, a short blunt
    #  muzzle under and before the horns, the profile dipping behind the eyes and rising to the horn boss)
    S.ell("cranium", [1.92, 2.0, 0], [0.27, 0.21, 0.24], "@skin", bone=H, k=0.1, rot=[0, 0, -24])
    S.ell("occiput", [1.84, 2.17, 0], [0.13, 0.12, 0.2], "@skin", bone=H, k=0.08)
    S.ell("faceBox", [2.28, 1.76, 0], [0.32, 0.2, 0.22], "@skin", bone=H, k=0.09, rot=[0, 0, -6])
    S.ell("cheek", [2.1, 1.82, 0.18], [0.25, 0.09, 0.1], "@skin", bone=H, k=0.07, mirror=True, rot=[0, 0, -6])
    S.cone("jaw", [1.92, 1.7, 0], [2.6, 1.55, 0], 0.16, 0.12, "@skin", bone=H, k=0.08)
    S.ell("jawAngle", [1.97, 1.64, 0], [0.22, 0.17, 0.17], "@skin", bone=H, k=0.08)
    S.ell("boss", [2.5, 1.9, 0], [0.15, 0.13, 0.2], "@skin", bone=H, k=0.08)
    # (the horns' shared bony STEM: broad across, thin fore-and-aft, leaning forward; about a quarter of their height)
    S.append(gate(S.ell("stem", [2.535, 2.02, 0], [0.085, 0.14, 0.15], "@skin", bone=H, k=0.07, rot=[0, 0, -18]), ["bull"])); S.pop(-2)
    S.append(gate(S.ell("stemCow", [2.52, 1.98, 0], [0.075, 0.1, 0.13], "@skin", bone=H, k=0.07, rot=[0, 0, -18]), ["cow"])); S.pop(-2)
    S.ell("muzzle", [2.6, 1.66, 0], [0.14, 0.2, 0.2], "@muzzle", bone=H, k=0.08)
    S.ell("lip", [2.69, 1.57, 0], [0.08, 0.11, 0.17], "@lip", bone=H, k=0.06)
    S.ell("nostril", [2.755, 1.66, 0.07], [0.025, 0.016, 0.02], "@lid", bone=H, k=0.01, op="sub", rot=[0, 25, -20], mirror=True)
    S.ell("mouth", [2.68, 1.5, 0], [0.09, 0.008, 0.15], "@lid", bone=H, k=0.01, op="sub")
    S = Sb
    for sh in S0: S.append(xshape(sh, HO, HS, dO))
    hang_tail(d, S, 1.94, 0.62, 0.065, 0.034)
    ex, ey = xpt([2.26, 1.83, 0], HO, HS, dO)[:2]   # (small eyes, set low on the side of the face)
    place_eye(d, S, ex, ey)
    # ---- the sharp parts: the Y-forked nasal horn pair, flattened, flaring out, blunt-ended; the ears
    def horn(id, f, when):
        # (a Y: ONE shared bony stem -- a field shape, see `stem` above -- rising from the nose end, and from it two
        #  prongs diverging about 35 degrees, leaning forward-up; each flattened fore-and-aft -- `up` its thin axis --
        #  tapering a little to a blunt, squarish end; skin-covered, the face's colour)
        b = [2.545, 2.02, 0.045]; dv = nrm([0.3, 0.9, 0.31]); L = 0.42 * f
        P = [b + [0.105], add(b, dv, L * 0.35) + [0.098], add(b, dv, L * 0.68) + [0.088], add(b, dv, L * 0.86) + [0.087]]
        rc = 0.1; c = add(b, dv, L)   # (the end: swollen to a club ~1.15x the prong just below, closed by a hemisphere)
        P += [c + [rc]] + [add(c, dv, rc * math.sin(math.radians(a))) + [rc * math.cos(math.radians(a))] for a in (35, 62, 80)]
        P += [add(c, dv, rc) + [0.0]]
        P = [[round(v, 4) for v in p[:3]] + [round(p[3] * (0.7 + 0.3 * f), 4)] for p in P]
        return gate(curve_horn(id, P, "@skin", mirror=True, fair={"r": 0.05, "skin": 0.6}, up=[0.9, -0.3, 0], aspect=0.62,
                               sides=12), when)
    horns = [xshape(h, HO, HS, dO) for h in [horn("horn", 1.0, ["bull"]), horn("hornCow", 0.55, ["cow"])]]
    ear = ear_from_rhino(J["earL"], s=0.8, tilt=30, out=30, yaw=55)
    sharp = horns + sharp + [ear]
    finish(d, S, sharp, J, horn_ids=[h["id"] for h in horns])
    d["coats"] = [{"name": "grey-brown"},
                  {"name": "brown", "body": "#6e5844", "skin": "#6e5844", "back": "#5f4b39", "belly": "#836b55", "front": "#745e49",
                   "leg": "#5e4a39", "dust": "#715c48", "tail": "#6e5844", "horn": "#6a5644", "fold": "#574535"},
                  {"name": "grey", "body": "#77756f", "skin": "#77756f", "back": "#69675f", "belly": "#8a8780", "front": "#7d7b74",
                   "leg": "#66645d", "dust": "#7a776f", "tail": "#77756f", "horn": "#716e66", "fold": "#605e58"}]
    d["variants"] = {"cow": {"params": {"bull": False, "cow": True}, "scale": 0.86, "colors": {}}}
    d["young"] = {"s": 0.3, "n": 1, "side": 2.0, "hop": 0.02, "name": "brontotherium calf"}
    d["_about"] = ("BRONTOTHERIUM / MEGACEROPS (Eocene-Oligocene North America, 2026-11-08; generator "
                   "tools/creaturegen/prehistoric/gen.py): a brontothere bull about 5 m long and 2.5 m at the withers -- "
                   "rhino- and elephant-like, a high HUMP over the shoulders (the thoracic spines) and the back sloping "
                   "down to a lower rump, a deep barrel on thick pillar legs, four hoof-nails on the fore feet and three "
                   "on the hind; a long head with a concave, SADDLE-SHAPED profile (the back of the skull high, the face "
                   "dipping, the nose rising again), wide cheekbones, small eyes, and at the end of the nose the forked "
                   "BONY HORN -- a Y: one broad shared stem, two skin-covered prongs flattened fore-and-aft diverging up, "
                   "out and a little forward to blunt squarish ends; a short tail with a dark brush; grey-brown hide. Horns and nails sharp "
                   "`horn`s faired into the skin, the ears the rhinoceros' cupped `fin` scaled. Coats grey-brown, brown, "
                   "grey; variant `cow` (smaller, short horns).")
    return d


# ======================================================================================================================
def elasmotherium():
    d = {
        "name": "elasmotherium", "kind": "mammal", "headForm": "bovid", "headScale": 0.8, "headTurn": 8, "graze": 0.5,
        "fur": False, "call": "rhinoceros", "print": "pad", "mount": {"h": 2.9, "speed": 1.6},
        "params": {"bull": True, "cow": False, "grown": True},
        "rear": [-1.05, 1.55, 0, 0.9, 0.6, 0.62],
        "front": [0.6, 1.7, 0, 0.9, 0.65, 0.65],
        "neck": [1.15, 1.75, 0, 1.55, 1.5, 0, 0.42, 0.34],
        "head": [1.78, 1.45, 0, 0.32],
        "muzzle": [1.95, 1.33, 0, 2.55, 0.97, 0, 0.2, 0.15],
        "ears": [1.76, 1.78, 0.2, 1.72, 1.97, 0.28, 0.06, 0.03],   # (2026-11-09: forward and up, clear of the neck and the crest -- they sat buried in them)
        "eyes": [2.06, 1.42, 0.18, 0.022],
        "legs": {"front": [0.85, 1.42, 0.4, 0.72], "hind": [-1.25, 1.42, 0.38, 0.74], "radii": [0.21, 0.16, 0.14],
                 "foot": [0.15, 0.07, 0.14]},
        "tail": {"path": [[-1.8, 1.8], [-1.9, 1.7], [-1.95, 1.55], [-1.96, 1.4]], "r1": 0.05, "r2": 0.03, "tuft": 0, "sway": 14, "speed": 1.0},
        "c": {"body": "#5e4a38", "skin": "#5e4a38", "wool": "#4c3928", "back": "#4f3c2b", "belly": "#45331f", "front": "#624d3a",
              "muzzle": "#5e4a3a", "dust": "#47362a", "leg": "#47362a", "foot": "#3e3128", "fold": "#4a3524",
              "eye": "#22160e", "lid": "#3a2c22", "lip": "#4c3e34", "face": "#58442f", "horn": "#3f352c", "hornTip": "#2c2520",
              "nail": "#6e6252", "ear": "#58442f", "earIn": "#645040", "tail": "#5a4029", "tuft": "#2e231a"},
    }
    d["sculpt"] = {"keep": [], "mesh": {"cell": 0.034, "tris": [8500, 2600], "focus": {"head": 4, "tail": 3}, "symmetric": True},
                   "eyes": {"at": [2.06, 1.42, 0.17], "from": [1.9, 1.42, 0], "r": 0.022, "iris": "#22160e", "pupil": "round", "lid": "@lid", "sink": 0.4, "socket": 0.9},
                   "shade": {"back": 1.1, "belly": 0.85, "low": 0.85, "on": "@body"}, "shape": []}
    J = joints(d)
    S = Shapes()
    W = {"pat": "shag"}
    # ---- the trunk: the HUGE shoulder hump (the neck's great muscles over long spines), a long back falling to the
    #      rump, a barrel slimmer than a rhinoceros' on long legs: a runner of the cold steppe, in a shaggy coat
    S.ell("barrel", [-0.2, 1.42, 0], [1.3, 0.5, 0.62], "@body", k=0.16, **W)
    S.ell("hump", [0.78, 1.93, 0], [0.58, 0.4, 0.44], "@wool", k=0.18, rot=[0, 0, -18], **W)
    S.ell("humpTop", [0.8, 2.1, 0], [0.36, 0.2, 0.3], "@wool", k=0.16, rot=[0, 0, -12], **W)
    S.ell("saddle", [-0.38, 1.78, 0], [0.95, 0.2, 0.48], "@back", k=0.18, rot=[0, 0, 8], **W)
    S.ell("rump", [-1.15, 1.5, 0], [0.5, 0.45, 0.58], "@body", k=0.14, rot=[0, 0, 12], **W)
    S.ell("belly", [-0.15, 1.12, 0], [0.9, 0.26, 0.56], "@belly", k=0.16, **W)
    S.ell("fringe", [-0.05, 0.98, 0], [0.75, 0.12, 0.42], "@belly", k=0.12, **W)
    S.ell("chest", [0.82, 1.3, 0], [0.42, 0.45, 0.5], "@wool", k=0.12, **W)
    S.ell("neck", [1.26, 1.62, 0], [0.5, 0.48, 0.42], "@wool", k=0.18, rot=[0, 0, -25], **W)
    S.ell("dewlap", [1.32, 1.34, 0], [0.34, 0.24, 0.3], "@wool", k=0.14, rot=[0, 0, -15], **W)
    # (the hump runs on forward over the neck to the back of the head as one mass: a tube down the top line)
    S.tube("crest", [[0.55, 1.95, 0, 0.32], [0.95, 2.0, 0, 0.32], [1.28, 1.86, 0, 0.29], [1.45, 1.74, 0, 0.18]], "@wool", k=0.2, **W)
    S.tube("spineLine", [[-1.0, 1.6, 0, 0.3], [-0.4, 1.66, 0, 0.32], [0.2, 1.82, 0, 0.32], [0.55, 1.95, 0, 0.32]], "@back", k=0.22, **W)
    # (the shaggy coat in the OUTLINE: lumps of uneven size down the throat, chest and belly's lower edge, and a low
    #  mane of them along the hump's crest)
    for i in range(15):   # (the belly's lower edge: transverse ridges of uneven depth -- a wavy, hanging fringe)
        x = -0.85 + i * 0.125; r = (0.075, 0.055, 0.068, 0.05)[i % 4]
        S.ell("fringe%d" % i, [x, 0.88, 0], [0.075, r, 0.3], "@belly", k=0.05, **W)
    for i, (x, y, r) in enumerate([(1.0, 1.14, 0.1), (1.18, 1.2, 0.08), (1.34, 1.26, 0.09), (0.8, 1.04, 0.09)]):
        S.ell("throat%d" % i, [x, y, 0], [r, r * 1.2, r * 1.5], "@wool", k=0.07, **W)
    for i, (x, y, r) in enumerate([(0.4, 2.22, 0.1), (0.62, 2.3, 0.12), (0.85, 2.32, 0.11), (1.08, 2.27, 0.11), (1.28, 2.13, 0.1)]):
        S.ell("mane%d" % i, [x, y, 0], [r * 1.2, r, r * 0.8], "@wool", k=0.05, **W)
    sharp = legs(S, J,
                 {"scap": [0.28, 0.4, 0.18], "arm": [0.22, 0.155], "fore": [0.13, 0.12], "foot": [0.15, 0.07, 0.14],
                  "toes": [-40, 0, 40], "nailR": 0.03, "pat": "shag", "scapColor": "@wool"},
                 {"thigh": [0.36, 0.46, 0.25], "gaskin": [0.19, 0.13], "cannon": [0.125, 0.12], "foot": [0.15, 0.07, 0.14],
                  "toes": [-40, 0, 40], "nailR": 0.03, "thighColor": "@body"})
    # ---- the head: long, held low to a broad grazer's lip, a great DOME on the forehead between the eyes carrying
    #      the single long horn
    H = "head"; C = {"pat": "coarse"}
    S.ell("skull", [1.8, 1.55, 0], [0.3, 0.2, 0.21], "@face", bone=H, k=0.09, rot=[0, 0, -30], **C)
    S.ell("dome", [2.0, 1.57, 0], [0.23, 0.19, 0.19], "@face", bone=H, k=0.08, rot=[0, 0, -20])
    S.cone("face", [2.02, 1.42, 0], [2.48, 1.02, 0], 0.18, 0.15, "@face", bone=H, k=0.08, **C)
    S.ell("snout", [2.38, 1.04, 0], [0.18, 0.13, 0.17], "@face", bone=H, k=0.07, rot=[0, 0, -35], **C)
    S.ell("cheek", [1.82, 1.38, 0.15], [0.2, 0.15, 0.09], "@face", bone=H, k=0.07, mirror=True, **C)
    S.ell("jaw", [2.1, 1.1, 0], [0.34, 0.16, 0.18], "@face", bone=H, k=0.07, rot=[0, 0, -35], **C)
    S.ell("lip", [2.55, 0.94, 0], [0.1, 0.12, 0.2], "@lip", bone=H, k=0.07)
    S.ell("nostril", [2.615, 1.05, 0.08], [0.028, 0.015, 0.022], "@lid", bone=H, k=0.012, op="sub", rot=[0, 25, -20], mirror=True)
    S.ell("mouth", [2.58, 0.9, 0], [0.07, 0.008, 0.15], "@lid", bone=H, k=0.01, op="sub")
    hang_tail(d, S, 1.75, 0.5, 0.055, 0.03, color="@tail")
    # ---- the horn: one, very long, keratin, rising from the dome and curving gently forward
    def horn(id, f, when):
        # (about 1.4 m from a base some 28 cm across on the dome ABOVE THE EYE (2026-11-09: it stood behind it), leaning
        #  FORWARD from the root and straightening toward the tip, which curls a little back -- a sabre's curve, not a
        #  hook forward over the nose)
        P0 = [[2.12, 1.62, 0, 0.15], [2.24, 1.84, 0, 0.142], [2.37, 2.12, 0, 0.12], [2.47, 2.4, 0, 0.09], [2.53, 2.65, 0, 0.056],
              [2.55, 2.84, 0, 0.026], [2.53, 2.96, 0, 0.0]]
        b = P0[0]
        P = [[b[0] + (p[0] - b[0]) * f, b[1] + (p[1] - b[1]) * f, 0, p[3] * (0.7 + 0.3 * f)] for p in P0]
        return gate(curve_horn(id, P, "@horn", fair={"r": 0.1, "skin": 0.4}, tip="@hornTip", tipAt=0.55, up=[1, 0, 0], aspect=0.85), when)
    horns = [horn("horn", 1.0, ["bull"]), horn("hornCow", 0.6, ["cow"])]
    ear = ear_from_rhino(J["earL"], s=1.05, tilt=10, out=48, yaw=40, shift=(0.0, 0.1, 0.11), pat="coarse")   # (2026-11-09: larger, stood out from the head and higher -- it lay flat on it, half in the crest)
    sharp = horns + sharp + [ear]
    finish(d, S, sharp, J, horn_ids=[h["id"] for h in horns])
    d["coats"] = [{"name": "brown"},
                  {"name": "russet", "body": "#6e4529", "skin": "#6e4529", "wool": "#5c3820", "back": "#5e3a21", "belly": "#50311c",
                   "front": "#744a2c", "face": "#66422a", "tail": "#5e3a21", "ear": "#5e3a21"},
                  {"name": "dark", "body": "#4a3a2c", "skin": "#4a3a2c", "wool": "#3c2f24", "back": "#3e3126", "belly": "#36291f",
                   "front": "#4e3e30", "face": "#46372a", "tail": "#3e3126", "ear": "#3e3126", "leg": "#3a2d22"}]
    d["variants"] = {"cow": {"params": {"bull": False, "cow": True}, "scale": 0.9, "colors": {}}}
    d["young"] = {"s": 0.33, "n": 1, "side": 1.8, "hop": 0.03, "name": "elasmotherium calf"}
    d["_about"] = ("ELASMOTHERIUM, the 'Siberian unicorn' (Pleistocene steppe, 2026-11-08; generator "
                   "tools/creaturegen/prehistoric/gen.py): a giant rhinoceros about 4.5 m long and 2 m at the shoulder, "
                   "3.5-4 t -- a HUGE shoulder hump, a long back falling to the rump, a slimmer barrel on long legs (a "
                   "runner), three hoof-nails a foot; a long head held low to a broad grazer's lip, a great DOME on the "
                   "forehead between the eyes carrying ONE very long horn (keratin, about 1.4 m from a base some 28 cm across, "
                   "rising from above the eye, leaning forward and straightening to a tip that curls a little back -- "
                   "its length is a reconstruction: only the dome's bony base is known); a SHAGGY brown woolly coat "
                   "(coatpat `shag`, `coarse` on the head; in the outline a wavy fringe along the belly and a low lumpy mane "
                   "on the hump, which runs forward over a thick neck to the head) for the cold. Horn and nails sharp `horn`s faired into the "
                   "skin, the ears the rhinoceros' cupped `fin`. Coats brown, russet, dark; variant `cow` (smaller, a "
                   "shorter horn).")
    return d


ALL = {"uintatherium": uintatherium, "brontotherium": brontotherium, "elasmotherium": elasmotherium}

if __name__ == "__main__":
    for nm in (sys.argv[1:] or list(ALL)):
        d = ALL[nm]()
        save("mammals/" + nm, d)
        print("wrote", nm, len(d["sculpt"]["shape"]), "shapes")
