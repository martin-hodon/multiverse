# Carnotaurus, Dilophosaurus, Allosaurus (and the shared biped helpers gen_pachy.py imports) -- 2026-11-05
# Each is written from scratch onto the tyrannosaur's rig (mammal kind, biped, the same flags), its trunk, legs
# and tail from one normalised theropod plan (the T. rex's, in units of hip height, from the hip joint) stretched
# per species, its head, neck and arms its own. Notes: rework/newdinos.md.
import math, sys, copy, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import R, save, Shapes, fix_order, floorR

BASE = json.load(open(R + "dinosaurs/tyrannosaur.json"))

def rig(name, about, H, hz, upper, neck, head, tail, arms, mount, colours, extra=None):
    """the tyrannosaur's rig, re-proportioned: hips H up at x 0 (z +-hz), femur `upper`; neck [a, b, rA, rB];
    head [x, y, r]; tail (x0, y0, L, droop, r1); arms (shoulder, elbow, wrist)"""
    d = copy.deepcopy(BASE)
    for k in ("sculpt", "_about"): d.pop(k, None)
    d["name"] = name
    d["_about"] = about
    s = H / 3.15
    d["mount"] = mount
    d["rear"] = [-0.1 * s, H + 0.15 * s, 0, 1.5 * s, 0.75 * s, 0.62 * s]
    d["front"] = [arms[0][0] - 0.2 * s, H - 0.05 * s, 0, 1.2 * s, 0.8 * s, 0.6 * s]
    a, b, rA, rB = neck
    d["neck"] = [a[0], a[1], 0, b[0], b[1], 0, rA, rB]
    d["head"] = [head[0], head[1], 0, head[2]]
    d["eyes"] = [head[0] + 0.23 * head[2] * 2, head[1] + 0.2 * head[2], 0.6 * head[2], 0.06 * s]
    L = d["legs"]
    L["hind"] = [0, H, hz, upper]
    L["radii"] = [0.5 * s, 0.28 * s, 0.18 * s]
    L["foot"] = [0.3 * s, 0.12 * s, 0.2 * s]
    L["toe"] = 0.15 * s
    L["toes"] = {"n": 3, "len": 0.75 * s, "r": [0.1 * s, 0.045 * s], "spread": 0.45}
    L["bend"] = [1, 1.06]
    x0, y0, Lt, droop, r1 = tail
    Rr = Lt * Lt / (2 * droop)
    d["tail"] = {"c": [x0, y0 - Rr], "R": Rr, "a0": math.pi / 2, "a1": math.pi / 2 + Lt / Rr, "r1": r1, "r2": 0.08 * r1,
                 "n": 7, "sway": 7, "speed": 0.3}
    sh, el, wr = arms
    hx, hy, hr = head
    for x in d["extras"]:
        if x["id"] == "arm": x["from"] = sh; x["to"] = el; x["r1"] = 0.11 * s; x["r2"] = 0.08 * s
        if x["id"] == "fore": x["from"] = el; x["to"] = wr; x["r1"] = 0.08 * s; x["r2"] = 0.05 * s
        if x["id"] == "snout": x["from"] = [hx + 0.2 * hr, hy + 0.1 * hr, 0]; x["to"] = [hx + 2.2 * hr, hy - 0.1 * hr, 0]; x["r1"] = hr; x["r2"] = 0.55 * hr
        if x["id"] == "jaw": x["ell"] = [hx + hr, hy - 0.8 * hr, 0, 1.5 * hr, 0.36 * hr, 0.6 * hr]
        if x["id"] == "brow": x["from"] = [hx + 0.2 * hr, hy + 1.1 * hr, 0.6 * hr]; x["to"] = [hx + 0.9 * hr, hy + 1.05 * hr, 0.6 * hr]; x["r1"] = 0.2 * hr; x["r2"] = 0.1 * hr
    d["c"] = colours
    if extra: d.update(extra)
    return d

def frame(r, o=(0, 0, 0)):
    return {"o": list(o), "u": [1, 0, 0], "v": [0, 1, 0], "r": r}

def trunk(S, H, fx=1.0, fy=1.0, fz=1.0, sc=None, belly_drop=1.0, chest=1.0, boot=True, breast=1.0):
    """the T. rex's trunk (Hartman), normalised by hip height from the hip joint; fx stretches it forward, fy deepens
    it below the hip line, fz widens it; chest deepens the ribcage alone"""
    sc = sc or {}
    def E(id, cn, rn, col, k, kc=None, ry=1.0):
        x = cn[0] * fx * H
        y = H * (1 + (cn[1] - 1) * (fy if cn[1] < 1 else 1.0))
        rr = [rn[0] * fx * H, rn[1] * H * (fy if cn[1] < 1.02 else 1.0) * ry, rn[2] * fz * H]
        kw = {"kc": kc * H} if kc else {}
        return S.ell(id, [x, y, 0], rr, col, k=k * H, **kw, **sc)
    E("hips", [0.0, 1.06], [0.29, 0.135, 0.17], "@back", 0.057)
    E("torso", [0.317, 0.978], [0.476, 0.21, 0.197], "@body", 0.063)
    E("ribs", [0.492, 0.937], [0.30, 0.241, 0.184], "@body", 0.057, ry=chest)
    E("spine", [0.286, 1.111], [0.508, 0.083, 0.114], "@back", 0.057, kc=0.038)
    E("belly", [0.365, 0.794 - 0.02 * (belly_drop - 1)], [0.365, 0.102 * belly_drop, 0.146], "@belly", 0.051, kc=0.038)
    if boot: E("boot", [0.111, 0.73], [0.114, 0.044, 0.063], "@belly", 0.044)
    E("chest", [0.683, 0.937], [0.159, 0.184, 0.152], "@body", 0.051, ry=chest)
    E("breast", [0.698, 0.832 + 0.03 * (1 - breast)], [0.133, 0.095, 0.121 * breast], "@belly", 0.038, kc=0.032, ry=chest * breast)

def tail(S, H, x0, Lt, y0, yend, r0, fz=1.0, sc=None, root_w=1.0, prof=None):
    """level tail on the `tail` bone: deep at the root (caudofemoralis), whip-thin at the end, the underside pale"""
    sc = sc or {}
    n = prof or [(0.0, 1.0), (0.23, 0.78), (0.45, 0.57), (0.64, 0.38), (0.82, 0.22), (0.95, 0.13), (1.0, 0.075)]
    y = lambda t: y0 + (yend - y0) * t ** 1.4
    S.tube("tail", [[x0 - Lt * t, y(t), 0, r0 * f] for t, f in n], "@body", bone="tail", k=0.2 * r0, **sc)
    S.ell("tailRoot", [x0 - 0.15 * Lt, y0 - 0.15 * r0, 0], [0.22 * Lt, 0.95 * r0, 0.75 * r0 * root_w * fz], "@body", bone="tail", k=0.27 * r0, **sc)
    S.tube("tailRidge", [[x0 + 0.05 * Lt, y(0) + 0.45 * r0, 0, 0.5 * r0], [x0 - 0.28 * Lt, y(0.28) + 0.42 * r0, 0, 0.36 * r0],
                         [x0 - 0.58 * Lt, y(0.58) + 0.22 * r0, 0, 0.22 * r0], [x0 - 0.85 * Lt, y(0.85) + 0.08 * r0, 0, 0.11 * r0]],
           "@back", bone="tail", k=0.23 * r0, kc=0.2 * r0, **sc)
    S.tube("tailBelly", [[x0 - 0.02 * Lt, y(0) - 0.55 * r0, 0, 0.68 * r0], [x0 - 0.3 * Lt, y(0.3) - 0.42 * r0, 0, 0.44 * r0],
                         [x0 - 0.6 * Lt, y(0.6) - 0.28 * r0, 0, 0.26 * r0], [x0 - 0.83 * Lt, y(0.83) - 0.15 * r0, 0, 0.13 * r0]],
           "@belly", bone="tail", k=0.23 * r0, kc=0.2 * r0, **sc)

def leg(S, H, z, upper, s, slim=1.0, sc=None, ankle=0.215, mt=1.0, toes=(0.26, 0.197), toe_r=0.035, claw=0.048, hoof=False, calf=1.0, thigh=(0.585, 0.88)):
    """a theropod's hind leg: a massive thigh tilted 12 deg (its back running straight down toward the hock), a slim
    shank back to the ankle off the ground, a long metatarsus forward to three toes on the footHL bone"""
    sc = sc or {}
    kn = H - upper
    # the thigh: a muscle mass high under the hip, then a cone tapering straight down to the knee (no drumstick ball;
    # the back of the thigh runs nearly straight toward the hock)
    S.ell("thigh", [-0.02 * H, H - 0.36 * upper, z - 0.013 * H], [0.55 * upper * slim, 0.46 * upper, 0.34 * upper * slim], "@body",
          bone="legHLu", k=0.07 * H, rot=[0, 0, 10], mirror=True, **sc)
    S.cone("thighLow", [0.01 * H, H - 0.5 * upper, z - 0.01 * H], [0.032 * H, kn + 0.03 * H, z], 0.3 * upper * slim, 0.085 * H * slim, "@body",
           bone="legHLu", k=0.05 * H, mirror=True, **sc)
    S.ell("knee", [0.032 * H, kn + 0.006 * H, z], [0.089 * H * slim, 0.076 * H, 0.079 * H * slim], "@leg", bone="legHLu", k=0.032 * H, mirror=True, **sc)
    ay = ankle * H
    ax = -0.025 * H
    S.cone("shin", [0, kn, z], [ax, ay + 0.01 * H, z], 0.095 * H * slim, 0.063 * H * slim, "@leg", bone="legHLl", k=0.025 * H, mirror=True, **sc)
    S.ell("calf", [-0.038 * H, kn - 0.38 * (kn - ay), z], [0.086 * H * slim * calf, 0.32 * (kn - ay), 0.073 * H * slim * calf], "@leg", bone="legHLl", k=0.025 * H, mirror=True, **sc)
    S.sph("ankle", [ax, ay, z], 0.06 * H * slim, "@leg", bone="legHLl", k=0.019 * H, mirror=True, **sc)
    S.cone("metatarsus", [ax, ay, z], [0.054 * H * mt, 0.054 * H, z], 0.054 * H * slim, 0.041 * H * slim, "@leg", bone="legHLl", k=0.019 * H, mirror=True, **sc)
    for j, (ang, ln) in enumerate([(0, toes[0] * H), (26, toes[1] * H), (-26, toes[1] * H)]):
        a = math.radians(ang); ux, uz = math.cos(a), math.sin(a)
        b = [0.057 * H * mt - 0.03 * H, 0.038 * H, z]
        p = lambda t, y, r: [b[0] + ux * t, y, b[2] + uz * t, r]
        tr = toe_r * H
        S.tube(f"toe{j}", [p(0, 0.038 * H, tr), p(ln * 0.45, 0.027 * H, tr * 0.77), p(ln, 0.019 * H, tr * 0.5)], "@foot", bone="footHL", k=0.45 * tr, mirror=True)
        e = p(ln, 0.019 * H, 0)
        cl = claw * H
        if hoof:
            S.ell(f"claw{j}", [e[0] + ux * cl * 0.3, 0.014 * H, e[2] + uz * cl * 0.3], [cl * 0.55, 0.3 * tr, 0.5 * tr], "@claw", bone="footHL", k=0.1 * tr,
                  rot=[0, -ang, 0], mirror=True)
        else:
            S.cone(f"claw{j}", e[:3], [e[0] + ux * cl, 0.008 * H, e[2] + uz * cl], 0.41 * tr, 0.09 * tr, "@claw", bone="footHL", k=0.09 * tr, mirror=True)

def eyelids(S, at, r, col="@brow", out=(0, 0, 1)):
    """a lid fold over the eye and a softer one under it (the socket carves their inner edges: a rim round the eye)"""
    x, y, z = at
    S.ell("lidUp", [x - 0.1 * r, y + 0.95 * r, z - 0.15 * r], [1.55 * r, 0.42 * r, 0.75 * r], col, bone="head", k=0.35 * r, kc=0.12 * r, mirror=True)
    S.ell("lidLo", [x - 0.05 * r, y - 0.95 * r, z - 0.2 * r], [1.35 * r, 0.32 * r, 0.6 * r], col, bone="head", k=0.35 * r, kc=0.12 * r, mirror=True)

def finish(d, S, cell, tris, eye, shade, focus=None, keep=None):
    d["sculpt"] = {
        "_about": "x forward, y up, z left, metres; each shape rides the bone it names; `mirror` makes the right one from the left",
        "keep": keep or [],
        "mesh": {"cell": cell, "tris": tris, **({"focus": focus} if focus else {})},
        "shape": [fix_order(p) for p in S],
        "eyes": eye,
        "shade": shade,
    }
    return d

SHADE = {"back": 0.8, "belly": 1.1, "low": 0.96, "on": "@body"}

# =====================================================================================================================
def carnotaurus():
    H, hz, s = 2.1, 0.42, 2.1 / 3.15
    hx, hy = 2.52, 2.46            # the head's pivot: the skull 0.6 m from x 2.33 to the snout at 2.95
    about = ("CARNOTAURUS SASTREI (sculpt overlay, 2026-11-05, after the holotype skeletal, Hartman-style): 7.8 m nose to tail, "
             "the hips 2.1 m up, the body level over long slender legs (femur 1.03 m); a deep chest, a long tail broad at its root "
             "(the caudal ribs' caudofemoralis); a nearly straight, wide neck; a 0.6 m skull short, deep and boxy with a shallow "
             "upturned jaw and two thick conical horns over the eyes pointing out and up; absurdly small arms (the forearm a "
             "quarter of the humerus, the hand a stub). Rows of big feature scales along neck, back, flanks and tail (coat pattern "
             "`osteoderms`). Muted rust-brown back, grey-tan flanks, a pale belly.")
    sh, el, wr = [1.45, 1.82, 0.3], [1.3, 1.66, 0.35], [1.35, 1.62, 0.36]
    col = {"body": "#634c3a", "front": "#634c3a", "neck": "#634c3a", "head": "#584232", "muzzle": "#634c3a", "eye": "#c9921c",
           "leg": "#5f4c3d", "foot": "#3e3226", "tail": "#634c3a", "back": "#47362a", "flank": "#735e4a", "belly": "#bba98a",
           "lip": "#6c5440", "claw": "#2a231c", "nostril": "#2a2018", "lid": "#3c2c22", "mouth": "#3a2620", "brow": "#4e3a2c",
           "horn": "#4a3c30", "hornTip": "#2e261e"}
    d = rig("carnotaurus", about, H, hz, 1.0, ([1.55, 2.25], [2.3, 2.45], 0.33, 0.27), [hx, hy, 0.2],
            (-0.35, 2.2, 4.4, 0.25, 0.36), (sh, el, wr), {"h": 3.6, "speed": 1.8}, col)
    sc = {"pat": "osteoderms", "frame": frame(0.3, (0, H - 0.05, 0))}
    ss = {"pat": "scales", "frame": frame(0.3)}
    S = Shapes()
    trunk(S, H, fx=1.0, fy=1.08, fz=0.88, sc=sc, chest=1.0, belly_drop=1.0, breast=0.75)
    tail(S, H, -0.3, 4.45, 2.2, 1.98, 0.37, sc=sc, root_w=1.35)
    # ---- the neck: nearly straight, wide at its base (the double row of epipophyses), the head held low and forward
    S.tube("neck", [[1.45, 2.18, 0, 0.4], [1.85, 2.3, 0, 0.29], [2.15, 2.4, 0, 0.2], [2.36, 2.46, 0, 0.15]], "@body", bone="neck", k=0.1, **sc)
    S.ell("neckWide", [1.7, 2.31, 0], [0.36, 0.19, 0.32], "@body", bone="neck", k=0.1, **sc)
    S.tube("nape", [[1.4, 2.43, 0, 0.17], [1.9, 2.47, 0, 0.12], [2.3, 2.56, 0, 0.085]], "@back", bone="neck", k=0.08, kc=0.07, **sc)
    S.ell("throat", [1.98, 2.22, 0], [0.34, 0.11, 0.15], "@flank", bone="neck", k=0.08, kc=0.06, **ss)
    # ---- the head: short (0.66 m), very deep, boxy; a blunt deep snout, a shallow jaw curving up; horns over the eyes
    S.box("cranium", [2.44, 2.5, 0], [0.14, 0.17, 0.15], "@head", bone="head", k=0.07, round=0.08, **ss)
    S.box("snout", [2.72, 2.47, 0], [0.22, 0.15, 0.11], "@head", bone="head", k=0.07, round=0.07, rot=[0, 0, -4], **ss)
    S.ell("roof", [2.62, 2.63, 0], [0.3, 0.05, 0.11], "@brow", bone="head", k=0.05, **ss)
    S.ell("muzzle", [2.9, 2.44, 0], [0.07, 0.12, 0.09], "@head", bone="head", k=0.05, **ss)
    S.box("jawBack", [2.42, 2.3, 0], [0.13, 0.08, 0.14], "@head", bone="head", k=0.06, round=0.05, **ss)
    S.box("jaw", [2.67, 2.29, 0], [0.26, 0.045, 0.095], "@lip", bone="head", k=0.05, round=0.035, rot=[0, 0, 7], **ss)
    S.ell("jawPale", [2.6, 2.25, 0], [0.26, 0.035, 0.08], "@belly", bone="head", k=0.03, kc=0.015)
    S.ell("lipLine", [2.66, 2.335, 0], [0.27, 0.015, 0.113], "@mouth", bone="head", k=0.004, kc=0.002, rot=[0, 0, 3])
    S.ell("cheek", [2.45, 2.42, 0.14], [0.1, 0.08, 0.05], "@brow", bone="head", k=0.04, mirror=True)
    S.ell("nostril", [2.93, 2.5, 0.075], [0.03, 0.022, 0.02], "@nostril", bone="head", k=0.008, kc=0.002, mirror=True)
    # the frontal horns: thick cones grown from inside the skull over the eyes, out and up, a little back
    S.cone("horn", [2.53, 2.6, 0.08], [2.5, 2.83, 0.27], 0.075, 0.03, "@horn", bone="head", k=0.04, kc=0.02, mirror=True)
    S.cone("hornTip", [2.505, 2.77, 0.235], [2.495, 2.86, 0.29], 0.032, 0.015, "@hornTip", bone="head", k=0.015, kc=0.008, mirror=True)
    S.ell("hornBase", [2.53, 2.62, 0.11], [0.09, 0.06, 0.08], "@brow", bone="head", k=0.04, mirror=True)
    eye_at = [2.53, 2.52, 0.145]
    eyelids(S, eye_at, 0.032)
    # ---- the arms: absurdly small; the humerus 25 cm held back along the chest, the forearm a quarter of it, the hand a stub
    S.cone("arm", sh, el, 0.055, 0.045, "@body", bone="armL", k=0.03, mirror=True, **ss)
    S.cone("fore", el, wr, 0.045, 0.04, "@body", bone="foreL", k=0.02, mirror=True, **ss)
    S.sph("hand", [wr[0] + 0.02, wr[1] - 0.01, wr[2]], 0.038, "@body", bone="foreL", k=0.015, mirror=True)
    # ---- the legs: long and slender
    leg(S, H, hz, 1.0, s, slim=0.8, sc=ss, ankle=0.215, toes=(0.25, 0.19), calf=0.85, thigh=(0.52, 0.76))
    eye = {"at": eye_at, "from": [2.48, 2.5, 0], "r": 0.032, "iris": "@eye", "pupil": "round", "lid": "@lid"}
    finish(d, S, 0.04, [10000, 3200], eye, SHADE, focus={"head": 5})
    floorR(S, ["claw", "hornTip"], 0.022)
    d["sculpt"]["shape"] = [fix_order(p) for p in S]
    save("dinosaurs/carnotaurus", d)
    return len(S)

# =====================================================================================================================
def dilophosaurus():
    H, hz, s = 1.6, 0.3, 1.6 / 3.15
    hx, hy = 2.27, 2.28
    about = ("DILOPHOSAURUS WETHERILLI (sculpt overlay, 2026-11-05, after Marsh & Rowe 2020): 7 m, ~400 kg, the hips 1.6 m up -- "
             "slender and lightly built; a long neck flexed so the head is held level; a 0.59 m skull with a narrow snout and "
             "the subnarial notch (the kink in the upper jaw between premaxilla and maxilla, below the nostril); two thin, tall, "
             "arched crests side by side along the skull roof from the nostril to over the eye, splayed a little; long arms with "
             "three working fingers (the first short with a big claw); long legs, three toes. Olive-grey with a darker back, "
             "faint darker saddle, pale belly; the crests rufous.")
    sh, el, wr = [1.22, 1.4, 0.22], [1.12, 1.14, 0.27], [1.36, 1.02, 0.25]
    col = {"body": "#66624a", "front": "#66624a", "neck": "#66624a", "head": "#5e5a44", "muzzle": "#66624a", "eye": "#c79a2a",
           "leg": "#5f5b46", "foot": "#3b382a", "tail": "#66624a", "back": "#45432f", "flank": "#757058", "belly": "#c4b896",
           "lip": "#6e6850", "claw": "#28241c", "nostril": "#2a281c", "lid": "#36342a", "mouth": "#3a2a22", "brow": "#4c4a36",
           "crest": "#6e5a44", "crestRim": "#844c34"}
    d = rig("dilophosaurus", about, H, hz, 0.75, ([1.3, 1.72], [2.1, 2.22], 0.24, 0.14), [hx, hy, 0.13],
            (-0.25, 1.68, 3.95, 0.22, 0.27), (sh, el, wr), {"h": 2.9, "speed": 2.0}, col)
    sc = {"pat": "scales", "frame": frame(0.36)}
    S = Shapes()
    trunk(S, H, fx=1.12, fy=0.95, fz=0.78, sc=sc, chest=1.0)
    tail(S, H, -0.22, 4.0, 1.68, 1.5, 0.27, sc=sc, root_w=0.95)
    # ---- the neck: long and slim, rising from the chest and bending level into the head
    S.tube("neck", [[1.2, 1.62, 0, 0.27], [1.5, 1.82, 0, 0.18], [1.78, 2.05, 0, 0.13], [2.0, 2.2, 0, 0.11], [2.18, 2.27, 0, 0.105]],
           "@body", bone="neck", k=0.08, **sc)
    S.tube("nape", [[1.15, 1.85, 0, 0.13], [1.5, 1.98, 0, 0.1], [1.8, 2.18, 0, 0.075], [2.12, 2.36, 0, 0.065]], "@back", bone="neck", k=0.06, kc=0.05, **sc)
    S.tube("throat", [[1.45, 1.66, 0, 0.12], [1.8, 1.96, 0, 0.08], [2.1, 2.16, 0, 0.07]], "@flank", bone="neck", k=0.05, kc=0.04, **sc)
    # ---- the head: 0.59 m, narrow; the premaxilla a rounded hook in front of the notch
    x0 = 2.17
    S.box("cranium", [x0 + 0.1, 2.3, 0], [0.1, 0.1, 0.105], "@head", bone="head", k=0.05, round=0.05, **sc)
    S.box("snout", [x0 + 0.3, 2.3, 0], [0.16, 0.07, 0.06], "@head", bone="head", k=0.05, round=0.04, rot=[0, 0, -3], **sc)
    S.ell("premax", [x0 + 0.52, 2.26, 0], [0.085, 0.058, 0.045], "@head", bone="head", k=0.03, **sc)
    S.ell("roof", [x0 + 0.24, 2.36, 0], [0.24, 0.04, 0.07], "@brow", bone="head", k=0.04, **sc)
    S.box("jawBack", [x0 + 0.09, 2.2, 0], [0.1, 0.045, 0.095], "@head", bone="head", k=0.04, round=0.035, **sc)
    S.box("jaw", [x0 + 0.33, 2.205, 0], [0.24, 0.025, 0.05], "@lip", bone="head", k=0.03, round=0.022, rot=[0, 0, 2], **sc)
    S.ell("jawPale", [x0 + 0.28, 2.18, 0], [0.26, 0.02, 0.045], "@belly", bone="head", k=0.02, kc=0.01)
    # the subnarial notch: a kink cut up into the upper jaw's edge between the premaxilla and the maxilla
    S.ell("notch", [x0 + 0.46, 2.19, 0], [0.028, 0.032, 0.08], "@mouth", bone="head", k=0.012, op="sub")
    S.ell("nostril", [x0 + 0.5, 2.29, 0.04], [0.022, 0.014, 0.014], "@nostril", bone="head", k=0.005, kc=0.002, mirror=True)
    # the crests: two thin, tall half-discs side by side on the roof from the nostril back over the eye, splayed 10 deg
    S.ell("crest", [x0 + 0.27, 2.37, 0.064], [0.27, 0.125, 0.03], "@crest", bone="head", k=0.014, kc=0.006, rot=[14, 0, 0], mirror=True)
    S.ell("crestTop", [x0 + 0.27, 2.415, 0.07], [0.23, 0.08, 0.028], "@crestRim", bone="head", k=0.006, kc=0.014, rot=[14, 0, 0], mirror=True)
    eye_at = [x0 + 0.13, 2.335, 0.09]
    eyelids(S, eye_at, 0.024)
    # ---- the arms: long, strong, three working fingers (I short with a big claw), IV a nub
    S.cone("arm", sh, el, 0.07, 0.05, "@body", bone="armL", k=0.035, mirror=True, **sc)
    S.cone("fore", el, wr, 0.05, 0.036, "@body", bone="foreL", k=0.025, mirror=True, **sc)
    S.ell("palm", [1.4, 1.0, 0.245], [0.06, 0.035, 0.028], "@body", bone="foreL", k=0.015, rot=[0, 0, -35], mirror=True)
    for j, (dz, ln, cl) in enumerate([(0.026, 0.07, 0.07), (0.0, 0.12, 0.055), (-0.024, 0.1, 0.045)]):
        a = [1.44, 0.975, 0.245 + dz]
        b = [a[0] + ln * 0.55, a[1] - ln * 0.8, 0.245 + dz * 1.2]
        S.cone(f"finger{j}", a, b, 0.022, 0.017, "@body", bone="foreL", k=0.008, mirror=True)
        S.tube(f"fclaw{j}", [[b[0], b[1], b[2], 0.016], [b[0] + cl * 0.35, b[1] - cl * 0.5, b[2], 0.011], [b[0] + cl * 0.2, b[1] - cl * 1.0, b[2], 0.004]],
               "@claw", bone="foreL", k=0.004, mirror=True)
    leg(S, H, hz, 0.75, s, slim=0.8, sc=sc, ankle=0.22, toes=(0.27, 0.2), calf=0.8, thigh=(0.52, 0.76))
    eye = {"at": eye_at, "from": [x0 + 0.1, 2.32, 0], "r": 0.024, "iris": "@eye", "pupil": "round", "lid": "@lid"}
    finish(d, S, 0.03, [10000, 3200], eye, SHADE, focus={"head": 5})
    floorR(S, ["fclaw", "claw"], 0.012)
    d["sculpt"]["shape"] = [fix_order(p) for p in S]
    save("dinosaurs/dilophosaurus", d)
    return len(S)

# =====================================================================================================================
def allosaurus():
    H, hz, s = 2.15, 0.4, 2.15 / 3.15
    hx, hy = 2.78, 2.92
    about = ("ALLOSAURUS FRAGILIS (sculpt overlay, 2026-11-05, after Hartman's and Paul's skeletals): 8.5 m, the hips 2.15 m up, the "
             "body level and the tail held out level; an S-curved neck lifting the head to 3 m; a long, narrow 0.85 m skull with "
             "small triangular lacrimal horns in front of the eyes and a low paired ridge along the nasals; strong three-fingered "
             "arms (the forearm a little shorter than the humerus) with big curved claws, the thumb's the biggest; long legs, "
             "three toes. Ochre-tan with a darker brown back, faint bands, a cream belly; the horns rufous.")
    sh, el, wr = [1.62, 1.8, 0.33], [1.54, 1.5, 0.38], [1.8, 1.38, 0.37]
    col = {"body": "#7a6144", "front": "#7a6144", "neck": "#7a6144", "head": "#6d5639", "muzzle": "#7a6144", "eye": "#d4a224",
           "leg": "#6e583e", "foot": "#40342a", "tail": "#7a6144", "back": "#523f2b", "flank": "#88704f", "belly": "#cbb892",
           "lip": "#7a6448", "claw": "#262019", "nostril": "#2a2018", "lid": "#3c3022", "mouth": "#3a2620", "brow": "#5a4630",
           "horn": "#6a4630", "ridge": "#5e4630"}
    d = rig("allosaurus", about, H, hz, 0.88, ([1.75, 2.35], [2.55, 2.92], 0.4, 0.26), [hx, hy, 0.2],
            (-0.33, 2.3, 4.65, 0.22, 0.4), (sh, el, wr), {"h": 3.8, "speed": 1.9}, col)
    sc = {"pat": "scales", "frame": frame(0.45)}
    S = Shapes()
    trunk(S, H, fx=1.08, fy=1.0, fz=0.82, sc=sc, chest=1.03)
    tail(S, H, -0.3, 4.7, 2.28, 2.06, 0.38, sc=sc, root_w=1.0)
    # ---- the S-neck: up out of the chest, then forward into the head
    S.tube("neck", [[1.62, 2.22, 0, 0.4], [1.98, 2.42, 0, 0.29], [2.25, 2.68, 0, 0.21], [2.48, 2.84, 0, 0.165], [2.66, 2.9, 0, 0.145]],
           "@body", bone="neck", k=0.12, **sc)
    S.tube("nape", [[1.55, 2.5, 0, 0.2], [1.95, 2.62, 0, 0.14], [2.25, 2.85, 0, 0.1], [2.55, 3.0, 0, 0.08]], "@back", bone="neck", k=0.09, kc=0.07, **sc)
    S.tube("throat", [[1.9, 2.22, 0, 0.18], [2.25, 2.5, 0, 0.12], [2.55, 2.74, 0, 0.1]], "@flank", bone="neck", k=0.08, kc=0.06, **sc)
    # ---- the head: long, narrow, fairly deep behind; the snout tapering; horns in front of the eyes, the nasal ridge
    x0 = 2.62
    S.box("cranium", [x0 + 0.15, 2.96, 0], [0.15, 0.16, 0.135], "@head", bone="head", k=0.06, round=0.06, **sc)
    S.box("snout", [x0 + 0.52, 2.93, 0], [0.32, 0.105, 0.08], "@head", bone="head", k=0.05, round=0.045, rot=[0, 0, -7], **sc)
    S.ell("muzzle", [x0 + 0.8, 2.87, 0], [0.07, 0.075, 0.065], "@head", bone="head", k=0.035, **sc)
    S.ell("roof", [x0 + 0.38, 3.05, 0], [0.38, 0.05, 0.1], "@brow", bone="head", k=0.05, rot=[0, 0, -7], **sc)
    S.ell("upperLip", [x0 + 0.45, 2.835, 0], [0.36, 0.045, 0.085], "@lip", bone="head", k=0.03, kc=0.02, **sc)
    S.box("jawBack", [x0 + 0.14, 2.78, 0], [0.15, 0.065, 0.13], "@head", bone="head", k=0.06, round=0.05, **sc)
    S.box("jaw", [x0 + 0.47, 2.785, 0], [0.33, 0.04, 0.075], "@lip", bone="head", k=0.045, round=0.035, rot=[0, 0, 2], **sc)
    S.ell("jawPale", [x0 + 0.4, 2.75, 0], [0.36, 0.03, 0.07], "@belly", bone="head", k=0.03, kc=0.015)
    S.ell("jugal", [x0 + 0.14, 2.86, 0.125], [0.12, 0.05, 0.04], "@brow", bone="head", k=0.04, mirror=True)
    S.ell("nostril", [x0 + 0.8, 2.93, 0.06], [0.03, 0.02, 0.02], "@nostril", bone="head", k=0.008, kc=0.002, mirror=True)
    # lacrimal horns: small triangles just in front of and above the eye; the nasal ridge forward from them
    S.tri("lacrimal", [x0 + 0.19, 3.07, 0.075], [x0 + 0.36, 3.06, 0.07], [x0 + 0.23, 3.2, 0.085], 0.034, "@horn", bone="head", k=0.025, kc=0.01, mirror=True)
    S.tube("nasalRidge", [[x0 + 0.33, 3.06, 0.05, 0.032], [x0 + 0.5, 3.03, 0.045, 0.03], [x0 + 0.68, 2.98, 0.04, 0.026], [x0 + 0.8, 2.95, 0.035, 0.02]],
           "@ridge", bone="head", k=0.02, kc=0.01, mirror=True)
    S.ell("lipLine", [x0 + 0.5, 2.82, 0], [0.36, 0.016, 0.083], "@mouth", bone="head", k=0.004, kc=0.002, rot=[0, 0, -2])
    eye_at = [x0 + 0.19, 3.0, 0.12]
    eyelids(S, eye_at, 0.035)
    # ---- the arms: strong, three fingers, big curved claws, the thumb's the biggest
    S.cone("arm", sh, el, 0.1, 0.07, "@body", bone="armL", k=0.05, mirror=True, **sc)
    S.cone("fore", el, wr, 0.07, 0.05, "@body", bone="foreL", k=0.03, mirror=True, **sc)
    S.ell("palm", [1.85, 1.35, 0.37], [0.08, 0.05, 0.045], "@body", bone="foreL", k=0.02, rot=[0, 0, -40], mirror=True)
    for j, (dz, ln, cl, cr) in enumerate([(0.04, 0.1, 0.17, 0.03), (0.0, 0.17, 0.12, 0.025), (-0.035, 0.14, 0.1, 0.022)]):
        a = [1.9, 1.31, 0.37 + dz]
        b = [a[0] + ln * 0.6, a[1] - ln * 0.8, 0.37 + dz * 1.4]
        S.cone(f"finger{j}", a, b, 0.034, 0.026, "@body", bone="foreL", k=0.01, mirror=True)
        S.tube(f"fclaw{j}", [[b[0], b[1], b[2], cr], [b[0] + cl * 0.45, b[1] - cl * 0.4, b[2], cr * 0.7], [b[0] + cl * 0.4, b[1] - cl * 0.95, b[2], cr * 0.25]],
               "@claw", bone="foreL", k=0.006, mirror=True)
    leg(S, H, hz, 0.88, s, slim=0.84, sc=sc, ankle=0.215, toes=(0.26, 0.2), calf=0.9, thigh=(0.52, 0.76))
    eye = {"at": eye_at, "from": [x0 + 0.15, 2.97, 0], "r": 0.035, "iris": "@eye", "pupil": "round", "lid": "@lid"}
    finish(d, S, 0.042, [10000, 3200], eye, SHADE, focus={"head": 5})
    floorR(S, ["fclaw", "claw"], 0.02)
    d["sculpt"]["shape"] = [fix_order(p) for p in S]
    save("dinosaurs/allosaurus", d)
    return len(S)

if __name__ == "__main__":
    which = sys.argv[1:] or ["carnotaurus", "dilophosaurus", "allosaurus"]
    for w in which: print(w, globals()[w](), "shapes")
