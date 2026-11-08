# THE FELID TEMPLATE: the tiger's sculpt (tiger_orig.json, s = 1) moved onto another cat's proportions.
# A species says where its shoulder and hip are (in tiger units), how much longer its legs are, its girths, its head
# size; the rig overrides (frame cat params) and every shape are mapped the same way, then scaled by s.
import copy, math
from lib import *

TIGER = orig("tiger")
T_SHAPES = TIGER["sculpt"]["shape"]
T_EYES = TIGER["sculpt"]["eyes"]
# the frame's numbers at s = 1, with the tiger's overrides
FR = {
    "rear": [-0.5, 0.8, 0, 0.52, 0.26, 0.3], "front": [0.34, 0.82, 0, 0.52, 0.27, 0.31],
    "neck": [0.66, 0.88, 0, 0.88, 1.0, 0, 0.21, 0.18], "head": [0.98, 1.05, 0, 0.22],
    "muzzle": [1.15, 0.97, 0, 0.17, 0.12, 0.15], "nose": [1.3, 1.02, 0, 0.04],
    "ears": [0.92, 1.24, 0.1, 0.9, 1.36, 0.15, 0.07, 0.03], "eyes": [1.12, 1.12, 0.1, 0.033],
    "legsF": [0.46, 0.64, 0.2, 0.3], "legsH": [-0.66, 0.66, 0.24, 0.32],
    "radii": [0.14, 0.1, 0.08], "foot": [0.1, 0.055, 0.09],
    "tailStart": [-1.021, 0.846], "tailR": 0.6, "a0": -0.59, "a1": -2.4, "r1": 0.068, "r2": 0.05,
}
HJ = [0.95, 1.035, 0.0]      # the tiger's head joint
NE = [0.88, 1.0, 0.0]        # the neck's end (the rig's headScale pivot)
HS0 = 0.7                    # the frame's headScale

class Map:
    def __init__(s, P):
        s.P = P
        s.sho, s.hip = P.get("sho", 0.46), P.get("hip", -0.66)
        s.dyF, s.dyH = P.get("dyF", 0.0), P.get("dyH", P.get("dyF", 0.0))
        s.S = P.get("s", 1.0)
    def fx(s, x):
        if x >= 0.46: return x + (s.sho - 0.46)
        if x <= -0.66: return x + (s.hip + 0.66)
        t = (x + 0.66) / 1.12
        return s.hip + t * (s.sho - s.hip)
    def kx(s, x):   # local stretch along x
        return 1.0 if (x >= 0.46 or x <= -0.66) else (s.sho - s.hip) / 1.12
    def dy(s, x):
        t = min(1, max(0, (x + 0.66) / 1.12))
        return s.dyH + t * (s.dyF - s.dyH)
    def trunk(s, p):     # a point of the trunk / neck: moved up whole
        return [s.fx(p[0]), p[1] + s.dy(p[0]), p[2]]
    def leg(s, p, fore):
        d = s.dyF if fore else s.dyH
        hipy = 0.64 if fore else 0.66
        return [s.fx(p[0]), p[1] + d * min(1, max(0, p[1]) / hipy), p[2]]
    def legk(s, fore):
        return 1 + (s.dyF if fore else s.dyH) / (0.64 if fore else 0.66)
    def head(s, p, hs):
        H2 = s.trunk(HJ)
        hsv = hs if isinstance(hs, list) else [hs, hs, hs]
        return [H2[k] + (p[k] - HJ[k]) * hsv[k] for k in range(3)]

def sc(v, S):
    return [x * S for x in v] if isinstance(v, list) else v * S

def region(sh):
    b = sh.get("bone", "body")
    if b in ("head",) or b.startswith("ear"): return "head"
    if b.startswith("legF") or b.startswith("footF"): return "fore"
    if b.startswith("legH") or b.startswith("footH"): return "hind"
    if b == "neck": return "neck"
    return "body"

def map_shape(sh, M, P):
    sh = copy.deepcopy(sh)
    reg = region(sh)
    S = M.S
    g = P.get("g", 1.0); gF = P.get("legF", P.get("leg", 1.0)); gH = P.get("legH", P.get("leg", 1.0))
    hs = P.get("hs", 1.0); hsm = hs if not isinstance(hs, list) else sum(hs) / 3
    gn = P.get("gneck", g)
    def pt(p):
        if reg == "head": q = M.head(p[:3], hs)
        elif reg in ("fore", "hind"): q = M.leg(p[:3], reg == "fore")
        else: q = M.trunk(p[:3])
        if reg in ("fore", "hind"):
            # a leg keeps its side, but follows the trunk's width
            q[2] = p[2] * P.get("gz", g)
        elif reg in ("body", "neck"):
            q[2] = p[2] * (gn if reg == "neck" else g)
        return sc(q, S)
    def rr(r, axis=None, x=0):
        if reg == "head": return r * hsm * S
        if reg in ("fore", "hind"):
            gg = gF if reg == "fore" else gH
            if axis == 1: return r * M.legk(reg == "fore") * S
            return r * gg * S
        if reg == "neck": return r * gn * S
        if axis == 0: return r * M.kx(x) * S
        return r * g * S
    t = sh["type"]
    if t in ("ell", "sphere", "box"):
        x0 = sh["c"][0]
        sh["c"] = pt(sh["c"])
        if t == "sphere": sh["r"] = rr(sh["r"])
        else:
            if reg == "head" and isinstance(hs, list): sh["r"] = [sh["r"][k] * hs[k] * S for k in range(3)]
            else: sh["r"] = [rr(sh["r"][k], k if not sh.get("rot") else None, x0) for k in range(3)]
    elif t == "cone":
        sh["a"] = pt(sh["a"]); sh["b"] = pt(sh["b"]); sh["ra"] = rr(sh["ra"]); sh["rb"] = rr(sh["rb"])
    elif t == "tube":
        sh["pts"] = [pt(q) + [rr(q[3])] for q in sh["pts"]]
    for key in ("k", "kc"):
        if key in sh: sh[key] = sh[key] * S * (hsm if reg == "head" else 1)
    fr = sh.get("frame")
    if isinstance(fr, dict) and "r" in fr:
        fr = dict(fr); fr["r"] = rr(fr["r"]); sh["frame"] = fr
    return sh

def rig(M, P):
    """the frame overrides, as numbers in metres (the species' s folded in)"""
    S = M.S; g = P.get("g", 1.0); gF = P.get("legF", P.get("leg", 1.0)); gH = P.get("legH", P.get("leg", 1.0))
    hs = P.get("hs", 1.0); hsm = hs if not isinstance(hs, list) else sum(hs) / 3
    out = {}
    def body(v):
        c = M.trunk(v[:3]); return sc([c[0], c[1], 0, v[3] * M.kx(v[0]), v[4] * g, v[5] * g], S)
    out["rear"] = body(FR["rear"]); out["front"] = body(FR["front"])
    n = FR["neck"]; a = M.trunk(n[:3]); b = M.trunk(n[3:6]); gn = P.get("gneck", g)
    out["neck"] = sc(a + b + [n[6] * gn, n[7] * gn], S)
    # the head cluster: posed q_r = NE + (q - NE) * .7; wanted q_r' = head-map(q_r); q' = NE' + (q_r' - NE') / .7
    NE2 = M.trunk(NE)
    def hp(q):
        qr = [NE[k] + (q[k] - NE[k]) * HS0 for k in range(3)]
        q2 = M.head(qr, hs)
        return [NE2[k] + (q2[k] - NE2[k]) / HS0 for k in range(3)]
    h = FR["head"]; out["head"] = sc(hp(h[:3]) + [h[3] * hsm], S)
    m = FR["muzzle"]; out["muzzle"] = sc(hp(m[:3]) + [x * hsm for x in m[3:]], S)
    no = FR["nose"]; out["nose"] = sc(hp(no[:3]) + [no[3] * hsm], S)
    e = FR["ears"]; out["ears"] = sc(hp(e[:3]) + hp(e[3:6]) + [e[6] * hsm, e[7] * hsm], S)
    ey = FR["eyes"]; out["eyes"] = sc(hp(ey[:3]) + [ey[3] * hsm], S)
    def lg(v, fore):
        hip = M.leg([v[0], v[1], 0], fore); knee = M.leg([v[0], v[1] - v[3], 0], fore)
        return sc([hip[0], hip[1], v[2] * P.get("gz", g), hip[1] - knee[1]], S)
    out["legs"] = {"front": lg(FR["legsF"], True), "hind": lg(FR["legsH"], False),
                   "radii": sc([FR["radii"][0] * gF, FR["radii"][1] * (gF + gH) / 2, FR["radii"][2] * (gF + gH) / 2], S),
                   "foot": sc([x * (gF + gH) / 2 for x in FR["foot"]], S)}
    ts = M.trunk(FR["tailStart"] + [0])
    tp = P.get("tail", {})
    R = tp.get("R", FR["tailR"]); a0 = tp.get("a0", FR["a0"]); a1 = tp.get("a1", FR["a1"])
    c = [ts[0] - R * math.cos(a0), ts[1] - R * math.sin(a0)]
    out["tail"] = {"c": sc(c, S), "R": R * S, "a0": a0, "a1": a1, "r1": tp.get("r1", FR["r1"]) * S, "r2": tp.get("r2", FR["r2"]) * S}
    for k in ("n", "tuft", "sway", "speed", "tuftColor"):
        if k in tp: out["tail"][k] = tp[k]
    return out

def felid(P, edits=None, add=None, drop=(), eyes=None):
    M = Map(P)
    shapes = []
    for sh in T_SHAPES:
        if sh["id"] in drop: continue
        q = map_shape(sh, M, P)
        if edits and sh["id"] in edits:
            e = edits[sh["id"]]
            q = e(q) if callable(e) else {**q, **e}
            if q is None: continue
            if "pat" in q and q["pat"] is None: q.pop("frame", None)
            q = {k: v for k, v in q.items() if v is not None}
        shapes.append(q)
    if add: shapes += add(M, P)
    ey = copy.deepcopy(eyes or T_EYES)
    hs = P.get("hs", 1.0); hsm = hs if not isinstance(hs, list) else sum(hs) / 3
    if not eyes:
        ey["at"] = sc(M.head(ey["at"], hs), M.S); ey["from"] = sc(M.head(ey["from"], hs), M.S); ey["r"] = ey["r"] * hsm * M.S * P.get("eye", 1.0)
    return M, rig(M, P), shapes, ey

def H(M, P, p):
    """a point given in TIGER head coordinates, mapped to the species (for added head shapes)"""
    return sc(M.head(p, P.get("hs", 1.0)), M.S)
def Tr(M, p):
    return sc(M.trunk(p), M.S)
def Lg(M, p, fore):
    return sc(M.leg(p, fore), M.S)

# THE FELID HEAD PASS (review 3): a cat's face, not a teddy's -- the eyes set in under a brow ridge (sunk, a thin rim, the
# almond's corners drawn out in black, the inner one down toward the nose), the tear line from the inner corner down to
# the mouth's corner, a flatter wider muzzle with defined pads, a short chin and a dark lip line, a small nose leather,
# broad cheeks under a flatter forehead, smaller ears set wide. Written in TIGER head coordinates: hm maps a point to the
# species' metres, f its sizes. o: tear (colour), tearW (its width), ears (scale), earZ (outward), nose (scale), noseC
def head_pass(shapes, eyes, hm, f, o=None):
    o = o or {}
    by = {q["id"]: q for q in shapes}
    def scl(id, rs, d=(0, 0, 0)):
        q = by.get(id)
        if not q: return
        if "r" in q and isinstance(q["r"], list): q["r"] = [q["r"][i] * rs[i] for i in range(3)]
        if "c" in q: q["c"] = [q["c"][i] + d[i] * f for i in range(3)]
    scl("muzzle", [0.86, 0.9, 1.1], (-0.006, 0.0, 0))
    scl("pad", [0.92, 0.86, 1.04], (-0.004, 0.0, 0.004))
    scl("chin", [0.72, 0.8, 0.85], (-0.012, 0.004, 0))
    scl("skull", [1.0, 0.88, 1.05], (0, -0.01, 0))
    scl("cheek", [1.0, 1.0, 1.12], (0, 0, 0.008))
    ns = o.get("nose", 0.9); scl("nose", [ns, ns * 0.9, ns], (0.004, 0.003, 0))   # (its leather at the muzzle's front top, not buried)
    fw = o.get("snout", 0.0)   # the muzzle drawn forward (a longer face)
    for id in ("nose", "pad", "chin", "muzzle"):
        if by.get(id): by[id]["c"] = [by[id]["c"][0] + fw * f, by[id]["c"][1], by[id]["c"][2]]
    if by.get("bridge"): by["bridge"]["b"] = [by["bridge"]["b"][0] + fw * f, by["bridge"]["b"][1], 0]
    q = by.get("bridge")
    if q:   # the BRIDGE long and straight, slimmer at the nose: no bulb over the muzzle
        q["rb"] *= 0.82; q["ra"] *= 0.95
    if by.get("nose") and o.get("noseC"): by["nose"]["color"] = o["noseC"]
    es = o.get("ears", 0.84)
    for id in ("ear", "earIn", "earBack", "earSpot"):
        q = by.get(id)
        if not q: continue
        if isinstance(q.get("r"), list): q["r"] = [x * es for x in q["r"]]
        elif "r" in q: q["r"] *= es
        dy = o.get("earY", -0.008)
        q["c"] = [q["c"][0], q["c"][1] + dy * f, q["c"][2] + o.get("earZ", 0.014) * f]
        if q.get("seat"): q["seat"]["from"] = [q["seat"]["from"][0], q["seat"]["from"][1] + dy * f, q["seat"]["from"][2] + o.get("earZ", 0.014) * f]
    # the eyes: sunk deep, a thin rim
    eyes.update(sink=0.56, socket=1.04, r=eyes["r"] * o.get("eye", 0.92))
    if o.get("eyeBall"): eyes["color"] = o["eyeBall"]   # (the eyeball round the iris in the iris' own darker tone: a cat shows no white)
    hb = hm([0.95, 1.06, 0.0])
    def dec(id, p, r, color, ang=0.0, yaw=0.0, sink=0.5, frm=None):
        R = [x * f for x in r]
        return {"id": id, "type": "ell", "bone": "head", "c": hm(p), "r": R, "rot": [0, yaw, ang], "k": 0.002 * f, "kc": 0.0012 * f, "color": color,
                "mirror": True, "seat": {"from": frm or hb, "out": -sink * min(R) / max(R)}}
    add = [
        # the BROW RIDGE over each eye (its underside carved by the socket: the upper lid's line)
        {"id": "browR", "type": "ell", "bone": "head", "c": hm([1.068, 1.118, 0.072]), "r": [0.036 * f, 0.016 * f, 0.03 * f], "rot": [12, -18, -10],
         "k": 0.014 * f, "kc": 0.01 * f, "color": o.get("browC", "@body"), "mirror": True},
        # the almond's corners, black: the inner one long and down toward the nose, the outer one short and up
        dec("eyeIn", [1.094, 1.07, 0.062], [0.016, 0.0055, 0.008], "@black", ang=-38, yaw=-30),
        dec("eyeOut", [1.048, 1.094, 0.093], [0.012, 0.005, 0.007], "@black", ang=-15, yaw=-60),
    ]
    tc, tw = o.get("tear"), o.get("tearW", 0.007)
    fw = o.get("snout", 0.0)
    if tc:
        pts = [[1.1, 1.06, 0.054], [1.112 + fw * 0.4, 1.03, 0.058], [1.122 + fw * 0.7, 1.0, 0.066], [1.126 + fw, 0.972, 0.078]]
        for i in range(3):
            a, b = pts[i], pts[i + 1]; c = [(a[k] + b[k]) / 2 for k in range(3)]
            L = math.dist(a, b) * 0.62
            add.append(dec(f"tear{i}", c, [tw, L, tw], tc, ang=math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), sink=0.45))
    lc = o.get("lip", "@black")
    if lc:
        for i, (p, ang) in enumerate([([1.158, 0.928, 0.03], -8), ([1.128, 0.928, 0.058], -30), ([1.095, 0.934, 0.074], -55)]):
            add.append(dec(f"lipL{i}", [p[0] + fw, p[1], p[2]], [0.017, 0.0045, 0.006], lc, yaw=ang, sink=0.4, frm=hm([1.08, 0.95, 0.0])))
    return shapes + add
