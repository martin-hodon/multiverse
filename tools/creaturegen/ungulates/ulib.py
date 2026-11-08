# ulib.py (2026-11-08): helpers for the big northern ungulates' generator (gen.py: moose, bison, ibex) on top of
# prehistoric/plib.py (probe.mjs: a species JSON given as a FILE -- joints, field distances, rays; horns, sinking roots,
# `gate`). Here: the LEGS mapped off the chamois' (a cloven-hoofed leg modelled once: arm, forearm, knee, cannon, tendon,
# fetlock, pastern, two hooves, dewclaws; thigh, stifle, gaskin, ham, hock and its point), an EAR mapped off another
# species' `fin` ear by its own frame (root, axis to the tip, face), and the PALM sheets with tines on their rim
# (sharp/caribou.py's palm_fin / tine_pts, the colour a parameter).
import os, sys, json, math, copy
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "prehistoric"))
from plib import *   # noqa: E402,F401  (probe, joints, curve_horn, sink_horns, gate, Shapes, save, add, sub, mul, nrm, ln, lerp)


def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def crs(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def R4(p): return [round(v, 4) for v in p]


def load_species(path):
    return json.load(open(REPO + "assets/creatures/" + path + ".json"))


# ---- LEGS off the chamois -------------------------------------------------------------------------------------------
CHAM = load_species("mammals/chamois")
CH_HIP = {"F": [0.245, 0.49, 0.098], "H": [-0.343, 0.511, 0.105]}   # (its legFLu / legHLu rest joints)
LEG_F = ["arm", "forearm", "knee", "cannon", "tendon", "fetlock", "pastern", "toeo", "toei", "dewF"]
LEG_H = ["thigh", "stifle", "gaskin", "ham", "hock", "hockPt", "hcannon", "htendon", "hfetlock", "hpastern", "htoeo", "htoei", "dewH"]
Y0 = 0.1   # (below this height -- fetlock, pastern, hooves -- the chamois' leg is scaled as its girth, above it stretched)


def legs_from(J, fr, fx=None, cols=None, pat=None, hair=None, only=None):
    """the chamois' four legs moved onto this rig's hips (legFLu, legHLu of joints J): each point's height above Y0
    stretched so the hip lands on this one's, below Y0 scaled with the girth `fr` (a hoof keeps its proportions); fore
    and aft offsets x `fx` (default fr), across x fr; every radius and blend x fr. `fr` may be a pair (fore, hind).
    `cols` renames colours ({"@limb": "@body"}); `pat`/`hair` set on the haired parts (not the hooves)."""
    out = Shapes()
    shp = {s["id"]: s for s in CHAM["sculpt"]["shape"]}
    frs = fr if isinstance(fr, (list, tuple)) else (fr, fr)
    for side, ids, fq in (("F", LEG_F, frs[0]), ("H", LEG_H, frs[1])):
        Hs = CH_HIP[side]; Hn = J["leg%sLu" % side]; fxx = fx[0 if side == "F" else 1] if isinstance(fx, (list, tuple)) else (fx or fq)
        fy = (Hn[1] - Y0 * fq) / (Hs[1] - Y0)
        def mp(p):
            y = p[1] * fq if p[1] < Y0 else Y0 * fq + (p[1] - Y0) * fy
            return R4([Hn[0] + (p[0] - Hs[0]) * fxx, y, Hn[2] + (p[2] - Hs[2]) * fq]) + [round(v * fq, 4) for v in p[3:]]
        for i in ids:
            if only and i not in only: continue
            s = copy.deepcopy(shp[i])
            for k in ("c", "a", "b"):
                if k in s: s[k] = mp(s[k])
            if "pts" in s: s["pts"] = [mp(p) for p in s["pts"]]
            if "r" in s: s["r"] = [round(v * fq, 4) for v in s["r"]] if isinstance(s["r"], list) else round(s["r"] * fq, 4)
            for k in ("ra", "rb", "k", "kc"):
                if k in s: s[k] = round(s[k] * fq, 4)
            if cols and s.get("color") in cols: s["color"] = cols[s["color"]]
            s.pop("pat", None); s.pop("hair", None)
            if s["color"] != "@foot":
                if pat: s["pat"] = pat
                if hair: s["hair"] = hair
            out.append(s)
    return out


# ---- an EAR off another species' fin ear -----------------------------------------------------------------------------
def ear_frame(e):
    R0 = lerp(e["root"][0], e["root"][-1], 0.5)
    tip = e["edge"][e.get("corners", [len(e["edge"]) // 2])[0]][:3]
    A = nrm(sub(tip, R0)); F = nrm(sub(e["face"], mul(A, dot(e["face"], A)))); W = crs(A, F)
    return R0, A, F, W


def ear_onto(e, T, axis, face, sl, sw, color="@ear", inner="@earIn", fair=None, **kw):
    """ear `e` (a fin) moved so its root's middle lands on T, its axis (root to tip) along `axis`, its hollow toward
    `face` (made square to the axis); its length x sl, its width and cup x sw"""
    R0, A, F, W = ear_frame(e)
    A2 = nrm(axis); F2 = nrm(sub(face, mul(A2, dot(face, A2)))); W2 = crs(A2, F2)
    def tr(p):
        q = sub(p[:3], R0); a, f, w = dot(q, A), dot(q, F), dot(q, W)
        return R4(add(add(add(T, A2, a * sl), F2, f * sw), W2, w * sw))
    o = copy.deepcopy(e)
    o["root"] = [tr(p) for p in e["root"]]
    o["edge"] = [tr(p) + list(p[3:]) for p in e["edge"]]
    o["face"] = R4(F2)
    for k in ("thick", "innerRim", "rim"):
        if k in o: o[k] = round(o[k] * sw, 4)
    o["fair"] = fair or {"r": round(e["fair"]["r"] * sw, 4) if isinstance(e.get("fair"), dict) else 0.01, "sink": 3}
    o["color"] = color; o["inner"] = inner
    for k in ("pat", "patFace", "rimColor", "tip", "tipAt"):
        o.pop(k, None)
    o["bone"] = "earL"; o["mirror"] = True
    o.update(kw)
    return o


# ---- PALMS (sharp/caribou.py's, the colour a parameter) --------------------------------------------------------------
class Plane:
    """a palm's plane: origin O, normal n, e1 (projected `fwd`), e2 = the in-plane side with +y"""
    def __init__(s, O, n, fwd):
        s.O = list(O[:3]); s.n = nrm(n)
        s.e1 = nrm(sub(fwd, mul(s.n, dot(fwd, s.n)))); s.e2 = crs(s.n, s.e1)
        if s.e2[1] < 0: s.e2 = mul(s.e2, -1)
    def p3(s, u, v, w=0.0): return add(add(add(s.O, s.e1, u), s.e2, v), s.n, w)
    def uv(s, p): q = sub(p[:3], s.O); return (dot(q, s.e1), dot(q, s.e2))


def tine_pts(pl, base, ang, w, L, curve=-15, asp0=0.5, asp1=0.85, sink=1.3, pw=0.85, n=6, lift=0.0):
    """a tine in the plane: rooted `sink` x w inside the palm behind its base (u, v) on the rim, `ang` degrees in the
    plane (0: e1, 90: e2), turning `curve` degrees by its tip, its tip raised `lift` of its length off the plane (along
    the normal: a tine turning up out of a dished palm); r 1.08 w at the base tapering (1 - s)^pw to a point"""
    a = math.radians(ang); u, v = base
    P = [pl.p3(u - math.cos(a) * w * sink, v - math.sin(a) * w * sink) + [0.9 * w, asp0],
         pl.p3(u, v) + [1.08 * w, asp0]]
    x, y, steps = u, v, 60
    for k in range(1, steps + 1):
        f = k / steps; th = a + math.radians(curve) * f
        x += math.cos(th) * L / steps; y += math.sin(th) * L / steps
        if k % (steps // n) == 0 or k == steps:
            P.append(pl.p3(x, y, lift * L * f * f) + [1.08 * w * (1 - f) ** pw, asp0 + (asp1 - asp0) * min(1.0, f / 0.5)])
    P[-1][3] = 0.0
    return [R4(p[:3]) + [round(p[3], 4), round(p[4], 3)] for p in P]


def palm_fin(pl, pid, root, path, color, thick=0.02, slope=1.2, swell=(0.026, 0.06, 1.2), bt=1.3, n=110, across=8,
             flare=True, extra=None):
    """a PALM sheet in plane pl: its root (3-D points, along the beam), its rim from root[0] round to root[-1] through
    `path` -- ("p", u, v, b) a rim point, ("t", id, u, v, ang, w, L, curve[, lift]) a tine whose base is on the rim (the
    rim flares in along the lobe's side, round its end and out the other side) -- returns the fin and the tines' pts"""
    edge, tines = [], []
    prev = pl.uv(root[0])
    for it in path:
        if it[0] == "p":
            edge.append(R4(pl.p3(it[1], it[2])) + [it[3]]); prev = (it[1], it[2]); continue
        _, tid, u, v, ang, w, L, curve = it[:8]; lift = it[8] if len(it) > 8 else 0.0
        a = math.radians(ang); d = (math.cos(a), math.sin(a)); pp = (-d[1], d[0])
        sg = 1 if math.dist((u + pp[0] * w, v + pp[1] * w), prev) < math.dist((u - pp[0] * w, v - pp[1] * w), prev) else -1
        side = lambda k, back: (u + sg * k * pp[0] * w - d[0] * back * w, v + sg * k * pp[1] * w - d[1] * back * w)
        lobe = [(side(1, 0), bt), ((u + d[0] * 0.5 * w, v + d[1] * 0.5 * w), bt), (side(-1, 0), bt)]
        if flare: lobe = [(side(1.4, 0.8), (1 + bt) / 2)] + lobe + [(side(-1.4, 0.8), (1 + bt) / 2)]
        for q, b in lobe: edge.append(R4(pl.p3(*q)) + [b])
        prev = lobe[-1][0]
        H = thick * math.tanh(slope * bt * w / thick)
        asp0 = max(0.35, min(0.8, H / (2 * 1.08 * w)))
        tines.append((tid, tine_pts(pl, (u, v), ang, w, L, curve, asp0=asp0, lift=lift)))
    f = {"id": pid, "type": "fin", "bone": "head", "root": [R4(p[:3]) for p in root], "edge": edge, "thick": thick,
         "slope": slope, "swell": list(swell), "color": color, "n": n, "across": across}
    if extra: f.update(extra)
    return f, tines


def ray_hit(d, S, a, b):
    d["sculpt"]["shape"] = list(S)
    return probe(d, {"rays": [[a, b]]})["hits"][0]


def index_add(path):
    """the species listed in assets/index.json under Mammals (re-read right before writing; only its own line)"""
    f = REPO + "assets/index.json"; txt = open(f).read()
    if '"%s"' % path in txt: return False
    d = json.loads(txt)
    cat = next(c for c in d["categories"] if c["name"] == "Mammals")
    names = sorted(cat["paths"] + [path])
    before = names[names.index(path) + 1] if names.index(path) + 1 < len(names) else None
    if before:
        a = '        "%s",\n' % before
        assert a in txt, before
        txt = txt.replace(a, '        "%s",\n' % path + a, 1)
    else:
        last = cat["paths"][-1]; a = '        "%s"\n' % last
        txt = txt.replace(a, '        "%s",\n        "%s"\n' % (last, path), 1)
    json.loads(txt); open(f, "w").write(txt)
    return True
