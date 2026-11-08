# caribou.py : the REINDEER's antlers rebuilt as a caribou bull's (2026-11-08, third sharp pass). Run AFTER
# antlers.py and review.py (it replaces what they made of the reindeer's antlers; it re-reads the file right before it
# writes and touches only the antler shapes -- the ears and the rest are other scripts'). Re-running it gives the same
# shapes (everything is built from the frozen centrelines below).
#   The BEAM: one `horn`, long, swept back and then forward over the top in one plane (its centreline as cervid.py and
#     antlers.py left it), tapering from the burr, FLATTENED in its own plane where it runs through the crown (a
#     per-point aspect, `up` the plane's normal), its forward end a pointed tine.
#   Three PALMS, each a thin `fin` SHEET in its own plane with the tines' bases exactly on its rim -- the crown (on the
#     upper, convex side of the beam's top, rooted along the beam), the bez palm (at the end of the bez tine) and the
#     shovels (the brow tines' vertical plates over the face, a mirrored pair: 2026-11-08 evening). The palm is thickest
#     at its root (`swell`, as thick as the flattened beam / stem there) and thins to a sharp rim; at each tine's base
#     the rim is blunter (b) so the sheet there is as thick as the tine. A bez / shovel palm is a FAN rooted across the
#     end of its stem (the stem's tip buried inside the palm, flattened into it).
#   Every TINE a `horn` in its palm's plane, rooted inside the palm at its base on the rim (as wide as the rim's lobe
#     there, as thick as the sheet), curving a little forward, tapering steadily to a point (r ~ (1 - s)^0.85: no knob,
#     no needle), its tip pale. The back tines rooted on the beam's centreline. The cow's (smaller) antlers keep their
#     course, their tips re-tapered (they ended in round knobs: the radius held to the end, then dropped to 0 in 1 mm).
import sys, math, json
from sharp2 import *

SP = "mammals/reindeer"
COL, TIPC = "#a89474", "#d2c6ac"

# the bull's beam centreline [x, y, z, r] (cervid.py's course, its root sunk by antlers.py)
BEAM = [[0.8764, 1.5672, 0.0109], [0.8607, 1.5799, 0.0304], [0.8269, 1.6073, 0.0726], [0.7784, 1.6474, 0.1328],
        [0.7277, 1.6939, 0.1919], [0.6749, 1.7459, 0.2454], [0.62, 1.8043, 0.2978], [0.5757, 1.8649, 0.3439],
        [0.5454, 1.9275, 0.3812], [0.5257, 1.9922, 0.4122], [0.5187, 2.0549, 0.4389], [0.5268, 2.1147, 0.4625],
        [0.5476, 2.1724, 0.4818], [0.5757, 2.2259, 0.4959], [0.6112, 2.2751, 0.504], [0.6542, 2.3201, 0.5068],
        [0.6992, 2.3589, 0.5054], [0.7506, 2.3912, 0.4977], [0.8041, 2.4173, 0.4857], [0.8417, 2.4348, 0.4769],
        [0.875, 2.456, 0.47], [0.903, 2.483, 0.463], [0.925, 2.514, 0.457], [0.94, 2.548, 0.452], [0.948, 2.58, 0.448]]
# its radius (the burr a little proud at the second point) and aspect (flattened through the crown)
BEAM_R = [.036, .039, .035, .0335, .0325, .0315, .0305, .0295, .029, .0284, .0278, .0272, .0266, .026, .0256, .0252,
          .0248, .0244, .024, .0232, .0215, .0185, .0145, .009, 0.0]
BEAM_A = [.92] * 12 + [.88, .8, .7, .62, .58, .56, .56, .58, .62, .68, .74, .8, .8]
BEAM_N = [0.45, -0.426, 0.785]   # (the plane the beam's C lies in: its normal, outward)

# the cow's beam and tines (their courses as antlers.py left them; only the tips re-tapered)
COW = {
  "beamCow": [[0.8704, 1.572, 0.0183, 0.0218], [0.8607, 1.5799, 0.0304, 0.0218], [0.8438, 1.5936, 0.0515, 0.0212], [0.8196, 1.6137, 0.0816, 0.0206], [0.7942, 1.6369, 0.1111, 0.02], [0.7678, 1.6629, 0.1379, 0.0195], [0.7404, 1.6921, 0.1641, 0.0188], [0.7182, 1.7224, 0.1872, 0.0182], [0.703, 1.7537, 0.2058, 0.0179], [0.6932, 1.786, 0.2213, 0.0175], [0.6897, 1.8174, 0.2347, 0.0171], [0.6938, 1.8473, 0.2465, 0.0167], [0.7042, 1.8761, 0.2561, 0.0163], [0.7182, 1.9029, 0.2631, 0.0159], [0.7359, 1.9275, 0.2672, 0.0157], [0.7574, 1.95, 0.2686, 0.0155], [0.78, 1.9694, 0.2679, 0.0153], [0.8056, 1.9855, 0.2641, 0.0151], [0.8324, 1.9986, 0.2581, 0.0149], [0.8512, 2.0074, 0.2536, 0.0148], [0.8594, 2.0432, 0.2446, 0.0125], [0.8646, 2.0855, 0.2341, 0.01], [0.8655, 2.1255, 0.2241, 0.0]],
  "backCow": [[0.6897, 1.8174, 0.2347, 0.012], [0.6708, 1.8219, 0.2378, 0.0096], [0.6506, 1.8267, 0.2412, 0.0074], [0.6327, 1.8364, 0.2442, 0.006], [0.6278, 1.8392, 0.2449, 0.0]],
  "palmPt1Cow": [[0.8512, 2.0074, 0.2536, 0.0104], [0.862, 2.0202, 0.2504, 0.0096], [0.8713, 2.0313, 0.2476, 0.0096], [0.8906, 2.0594, 0.2406, 0.0081], [0.9034, 2.0834, 0.2346, 0.006], [0.9095, 2.0948, 0.2318, 0.0]],
  "bezCow": [[0.8196, 1.6137, 0.0816, 0.0165], [0.8316, 1.632, 0.0907, 0.0149], [0.842, 1.648, 0.0987, 0.0149], [0.8559, 1.6654, 0.1064, 0.0148], [0.8713, 1.6777, 0.1096, 0.0145], [0.8874, 1.6873, 0.1106, 0.0143], [0.9115, 1.7008, 0.1114, 0.0]],
}

def plen(P):
    return sum(ln(sub(P[i + 1], P[i])) for i in range(len(P) - 1))

def at_s(P, s):
    """the point of polyline P at arc length s (its components interpolated)"""
    acc = 0.0
    for i in range(len(P) - 1):
        l = ln(sub(P[i + 1], P[i]))
        if acc + l >= s or i == len(P) - 2: return lerp(P[i], P[i + 1], max(0.0, min(1.0, (s - acc) / (l or 1e-9))))
        acc += l

def retaper(P, frac=0.45, pw=0.85, n=6):
    """a horn's last `frac` of its length resampled (n points) with the radius falling steadily to 0 at the tip --
    (1 - s)^pw of the radius where the taper starts: a tapered point, not a knob"""
    L = plen(P); s0 = (1 - frac) * L
    keep = []; acc = 0.0
    for i, p in enumerate(P):
        if i: acc += ln(sub(p, P[i - 1]))
        if acc < s0 - 1e-6: keep.append(list(p))
    q0 = at_s(P, s0); r0 = q0[3]
    out = keep + [q0[:3] + [r0] + q0[4:]]
    for k in range(1, n + 1):
        f = k / n; q = at_s(P, s0 + f * (L - s0))
        out.append(q[:3] + [r0 * (1 - f) ** pw] + q[4:])
    out[-1][3] = 0.0
    return out

class Plane:
    """a palm's plane: origin O, normal n, e1 (projected `fwd`), e2 = the in-plane side with +y"""
    def __init__(s, O, n, fwd):
        s.O = list(O[:3]); s.n = nrm(n)
        s.e1 = nrm(sub(fwd, mul(s.n, dot(fwd, s.n)))); s.e2 = crs(s.n, s.e1)
        if s.e2[1] < 0: s.e2 = mul(s.e2, -1)
    def p3(s, u, v, w=0.0): return add(add(add(s.O, s.e1, u), s.e2, v), s.n, w)
    def uv(s, p): q = sub(p[:3], s.O); return (dot(q, s.e1), dot(q, s.e2))

def tine_pts(pl, base, ang, w, L, curve=-15, asp0=0.5, asp1=0.85, sink=1.3, pw=0.85, n=7):
    """a tine in the plane: rooted `sink` x w inside the palm behind its base (u, v) on the rim, `ang` degrees in the
    plane (0: e1, 90: e2), turning `curve` degrees by its tip; r = 1.08 w at the base (the lobe's sides inside it),
    tapering (1 - s)^pw to a point; its aspect (thickness / width, across the plane) from asp0 to asp1 by mid-length"""
    a = math.radians(ang); u, v = base
    P = [pl.p3(u - math.cos(a) * w * sink, v - math.sin(a) * w * sink) + [0.9 * w, asp0],
         pl.p3(u, v) + [1.08 * w, asp0]]
    x, y, steps = u, v, 60
    for k in range(1, steps + 1):
        f = k / steps; th = a + math.radians(curve) * f
        x += math.cos(th) * L / steps; y += math.sin(th) * L / steps
        if k % (steps // n) == 0 or k == steps:
            P.append(pl.p3(x, y) + [1.08 * w * (1 - f) ** pw, asp0 + (asp1 - asp0) * min(1.0, f / 0.5)])
    P[-1][3] = 0.0
    return P

def palm_fin(pl, pid, root, path, thick=0.02, slope=1.2, swell=(0.026, 0.06, 1.2), bt=1.3, n=110, across=8, flare=True, extra=None):
    """a PALM sheet in plane pl: its root (3-D points, buried in the beam / stem), its rim from root[0] round to
    root[-1] through `path` -- ("p", u, v, b) a rim point, ("t", id, u, v, ang, w, L, curve) a tine whose base is on the
    rim: the rim runs in along the lobe's side, round its end and out along the other side (bluntness bt) -- and the
    tines' horns"""
    edge, tines = [], []
    prev = pl.uv(root[0])
    for it in path:
        if it[0] == "p":
            edge.append(pl.p3(it[1], it[2]) + [it[3]]); prev = (it[1], it[2]); continue
        _, tid, u, v, ang, w, L, curve = it
        a = math.radians(ang); d = (math.cos(a), math.sin(a)); pp = (-d[1], d[0])
        sg = 1 if math.dist((u + pp[0] * w, v + pp[1] * w), prev) < math.dist((u - pp[0] * w, v - pp[1] * w), prev) else -1
        side = lambda k, back: (u + sg * k * pp[0] * w - d[0] * back * w, v + sg * k * pp[1] * w - d[1] * back * w)
        # (the lobe: the rim FLARES in to the tine -- out at 1.4 widths 0.8 of a width below the base, onto the tine's side at
        #  the base -- round an end half a width out (inside the tine) and back out the same way on the other side)
        lobe = [(side(1, 0), bt), ((u + d[0] * 0.5 * w, v + d[1] * 0.5 * w), bt), (side(-1, 0), bt)]
        if flare: lobe = [(side(1.4, 0.8), (1 + bt) / 2)] + lobe + [(side(-1.4, 0.8), (1 + bt) / 2)]
        for q, b in lobe: edge.append(pl.p3(*q) + [b])
        prev = lobe[-1][0]
        H = thick * math.tanh(slope * bt * w / thick)   # (the sheet's thickness a width in from the lobe's sides)
        asp0 = max(0.35, min(0.8, H / (2 * 1.08 * w)))
        tines.append((tid, tine_pts(pl, (u, v), ang, w, L, curve, asp0=asp0)))
    f = {"id": pid, "type": "fin", "bone": "head", "root": [list(p[:3]) for p in root], "edge": edge, "thick": thick,
         "slope": slope, "swell": list(swell), "color": COL, "n": n, "across": across}
    if extra: f.update(extra)
    return f, tines

def horn(hid, P, up, extra, aspect=None, tip=True):
    h = {"id": hid, "type": "horn", "bone": "head", "pts": P, "color": COL, "up": r5(up)}
    if aspect is not None: h["aspect"] = aspect
    if tip: h.update({"tip": TIPC, "tipAt": 0.5})
    h.update(extra)
    return h

def build():
    bull_m = {"mirror": True, "when": "bull"}; bull_1 = {"when": "bull"}
    out = []
    # ---- the beam ----
    B = [p + [r, a] for p, r, a in zip(BEAM, BEAM_R, BEAM_A)]
    out.append(horn("beam", B, BEAM_N, bull_m, tip=False))
    out[-1].update({"tip": TIPC, "tipAt": 0.93})
    # ---- the crown: on the beam's convex (upper) side over the top, rooted along it ----
    pc = Plane(BEAM[17], BEAM_N, sub(BEAM[18], BEAM[16]))
    crown, ct = palm_fin(pc, "crown", BEAM[15:22], [
        ("p", -0.145, 0.03, 1.0),
        ("t", "topT0", -0.12, 0.075, 108, 0.011, 0.10, -14),
        ("p", -0.075, 0.088, 1.0),
        ("t", "topT1", -0.03, 0.115, 93, 0.012, 0.135, -16),
        ("p", 0.022, 0.108, 1.0),
        ("t", "topT2", 0.07, 0.112, 78, 0.012, 0.12, -14),
        ("p", 0.118, 0.082, 1.0),
        ("t", "topT3", 0.152, 0.062, 60, 0.010, 0.085, -10),
        ("p", 0.19, 0.026, 1.0)], extra=bull_m)
    out.append(crown)
    for tid, P in ct: out.append(horn(tid, P, pc.n, bull_m))
    # ---- the back tines, off the beam behind (in the beam's plane, rooted on its centreline) ----
    for tid, i, ang, L, w, cv in (("back", 10, 168, 0.13, 0.016, -22), ("back2", 13, 140, 0.13, 0.014, -20)):
        u, v = pc.uv(BEAM[i]); a = math.radians(ang)
        P = tine_pts(pc, (u + math.cos(a) * 0.022, v + math.sin(a) * 0.022), ang, w, L, cv, asp0=0.9, asp1=0.9, sink=1.4)
        P[0] = list(BEAM[i]) + [w * 0.95, 0.9]
        out.append(horn(tid, P, pc.n, bull_m))
    # ---- the bez: a tine off the beam's base, forward and up, its upper side a small palm sheet with three points,
    #      the tine itself running on through it as the foremost point ----
    pb = Plane(BEAM[3], [-0.29, 0.0, 0.957], [1, 0, 0])
    a = math.radians(36); dd = (math.cos(a), math.sin(a)); pp = (-dd[1], dd[0]); c = (0.17, 0.123)
    ab = lambda A, Bb: (c[0] + A * dd[0] + Bb * pp[0], c[1] + A * dd[1] + Bb * pp[1])   # (along the tine from the palm's start, across it)
    stem = [((0.0, 0.0), .025, .9), (ab(-0.1, 0), .021, .8), (ab(0, 0), .018, .64), (ab(0.06, 0), .0165, .6),
            (ab(0.12, 0), .015, .62), (ab(0.155, 0.006), .011, .7), (ab(0.19, 0.016), .0055, .8), (ab(0.215, 0.026), 0.0, .8)]
    out.append(horn("bez", [pb.p3(*q) + [r, asp] for q, r, asp in stem], pb.n, bull_m))
    bez, bt_ = palm_fin(pb, "bezPalm", [pb.p3(*ab(A, 0)) for A in (0.0, 0.04, 0.08, 0.125)], [
        ("p", *ab(0.006, 0.022), 1.0),
        ("t", "bezP2", *ab(0.028, 0.048), 100, 0.009, 0.08, -16),
        ("p", *ab(0.05, 0.058), 1.0),
        ("t", "bezP1", *ab(0.075, 0.064), 76, 0.0095, 0.095, -12),
        ("p", *ab(0.098, 0.052), 1.0),
        ("t", "bezP0", *ab(0.115, 0.036), 54, 0.009, 0.08, -8),
        ("p", *ab(0.128, 0.014), 1.0)], thick=0.016, slope=1.6, swell=(0.018, 0.04, 1.2), across=7, flare=False, extra=bull_m)
    out.append(bez)
    for tid, P in bt_: out.append(horn(tid, P, pb.n, bull_m))
    # ---- the shovels (the brow tines, a PAIR, 2026-11-08 evening: the user wants the antlers symmetric -- before, the
    #      left brow alone was a shovel, its plate leaning in across the midline, and the right a plain tine): forward
    #      from the burr, rising, then along the top of a vertical plate that hangs over the face, three points on the
    #      plate's front edge and the tine's own tip the fourth; the plate's plane turned a little OUT (its normal
    #      [-0.08, 0, 0.997]) so each stays on its own side, ~10 cm apart at the front, and mirrored ----
    ps = Plane([0.8541, 1.5853, 0.0387], [-0.08, 0.0, 0.997], [1, 0, 0])
    stem = [((0.0, 0.0), .024, .9), ((0.03, 0.05), .021, .85), ((0.07, 0.08), .018, .72), ((0.11, 0.09), .0165, .62),
            ((0.17, 0.093), .0155, .6), ((0.25, 0.09), .014, .62), ((0.28, 0.097), .0095, .7), ((0.305, 0.108), .0045, .8),
            ((0.322, 0.117), 0.0, .8)]
    out.append(horn("shovel", [ps.p3(*q) + [r, asp] for q, r, asp in stem], ps.n, bull_m))
    sh, st = palm_fin(ps, "shovelLeaf", [ps.p3(*q) for q in ((0.075, 0.082), (0.11, 0.09), (0.17, 0.093), (0.25, 0.09))], [
        ("p", 0.1, 0.066, 1.0),
        ("p", 0.15, 0.05, 1.0),
        ("p", 0.2, 0.024, 1.0),
        ("t", "shovelPt0", 0.233, 0.003, -35, 0.0075, 0.042, 8),
        ("p", 0.256, 0.018, 1.0),
        ("t", "shovelPt1", 0.27, 0.036, -10, 0.008, 0.05, 6),
        ("p", 0.278, 0.054, 1.0),
        ("t", "shovelPt2", 0.278, 0.071, 6, 0.0075, 0.045, -4),
        ("p", 0.262, 0.084, 1.0)], thick=0.015, slope=1.6, swell=(0.018, 0.04, 1.2), across=7, flare=False, extra=bull_m)
    out.append(sh)
    for tid, P in st: out.append(horn(tid, P, ps.n, bull_m))
    # (the right brow's plain tine, browR, is gone: the right shovel is the left one's mirror)
    # ---- the cow's ----
    out.append(horn("beamCow", retaper(COW["beamCow"], 0.12), [0, 1, 0], {"mirror": True, "when": "cow", "tipAt": 0.9}, aspect=0.92))
    for tid in ("backCow", "palmPt1Cow", "bezCow"):
        out.append(horn(tid, retaper(COW[tid], 0.6), [0, 1, 0], {"mirror": True, "when": "cow"}, aspect=0.9))
    return [r5(dedup(h)) for h in out]

IDS = {"beam", "crown", "back", "back2", "bez", "bezPalm", "shovel", "shovelLeaf", "browR", "beamCow", "backCow",
       "palmPt1Cow", "bezCow"} | {"topT%d" % i for i in range(5)} | {"bezP%d" % i for i in range(4)} | {"shovelPt%d" % i for i in range(5)}

def main():
    new = build()
    txt, d = load(SP)
    sh = d["sculpt"]["shape"]
    idx = [i for i, s in enumerate(sh) if s.get("id") in IDS and s.get("type") in ("horn", "fin")]
    if not idx: raise SystemExit("no antler shapes found")
    out = sh[:idx[0]] + new + [s for i, s in enumerate(sh) if i > idx[0] and i not in idx]
    save(SP, out, txt)
    msg = ("The ANTLERS rebuilt as a caribou bull's: the beam long, swept back and then forward "
         "in one plane, tapering from the burr, flattened in its plane where it runs through the crown and ending in a "
         "point; the CROWN a thin `fin` sheet on the beam's upper side carrying four pointed tines (`horn`s rooted inside "
         "the sheet at their bases on its rim, in its plane), two back tines off the beam; the BEZ a tine forward from "
         "low on the beam ending in a small palm sheet with three points; the SHOVELS (both brow tines, mirrored -- 2026-11-08 evening, made symmetric: the left alone was a shovel leaning in "
         "across the midline, the right a plain tine) each a vertical sheet over its side of the face with four points on its front edge. Every tine tapers steadily to a pale "
         "point. The cow's antlers keep their course, their tips re-tapered (they ended in round knobs).")
    if not note(SP, "(2026-11-08, caribou.py)", msg):   # (the reindeer's `_about` is its sculpt's: no top-level one)
        from ears2 import note_sculpt
        note_sculpt(SP, "(2026-11-08, caribou.py)", msg)
    print(SP, "antler shapes", len(idx), "->", len(new))

if __name__ == "__main__":
    main()
