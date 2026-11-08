# ears2.py (2026-11-08): EVERY remaining species' ears made cupped sheets (sharp.js `fin`) -- the field ellipsoids,
# cones, tubes and `tri` plates they were (bumpy: a blob a cell or two thick, its rim a staircase) gone, and the helpers
# that served them only (inner-colour ells, `earTip` / `earBase` / `earRoot` balls, paint ells, the rat's carved cup).
# Each ear: its rim exactly on an outline drawn from the animal's own ear (ear_shapes.py: a cat's upright triangle, a
# horse's leaf, a bear's round, a hare's long spoon...), sized and placed as the old ear (measured from its shapes: its
# axis, how far it reaches, how wide it is), on the same bone (`earL` mirrored: the ears still twitch); its root buried
# in the head where the axis leaves it and FAIRED in (`fair`); cupped (`cup`) with the hollow on the side the old
# inner-colour shape showed (or the anatomy's: forward, out), `inner` its lining, `rim` / `tip` the dark edges.
#   python3 ears2.py SPECIES... | FAMILY... | all       (species as in SPEC below; a family name runs its species)
#   python3 ears2.py --undo SPECIES...                 (the old shapes back from ears2_orig.json)
# It reads the shapes it replaces from ears2_orig.json (the backup, made on the first run per species), so it can be
# re-run after a change to SPEC; it rewrites only the ear shapes of the file as it is right before writing.
import json, math, os, sys, re
from shp import load, save, sub, add, mul, dot, crs, nrm, ln, lerp, axes_of, fd, note, r5
HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
BK = HERE + "ears2_orig.json"
ORIG = json.load(open(BK)) if os.path.exists(BK) else {}
from ear_shapes import SPEC, FAMILY

def rot(v, a, th):
    c, s = math.cos(th), math.sin(th)
    return add(add(mul(v, c), crs(a, v), s), a, dot(a, v) * (1 - c))

# ---- the species' params (an ear written over the frame's params: the lion's, the tiger's) ----------------------
def params_of(d):
    return dict(d.get("params") or {})

def ev(x, P):
    if isinstance(x, str): return float(eval(x, {"__builtins__": {}}, dict(P)))
    return x

def resolve(s, P):
    """a shape's numbers (expressions over the params evaluated)"""
    o = dict(s)
    for k in ("c", "a", "b"):
        if k in o: o[k] = [ev(v, P) for v in o[k]]
    if "r" in o: o["r"] = [ev(v, P) for v in o["r"]] if isinstance(o["r"], list) else ev(o["r"], P)
    for k in ("ra", "rb"):
        if k in o: o[k] = ev(o[k], P)
    if "pts" in o: o["pts"] = [[ev(v, P) for v in p] for p in o["pts"]]
    return o

# ---- what the old ear was: its points (a cloud on its surface) ---------------------------------------------------
def cloud(s, n=10):
    t = s["type"]
    if t == "sphere":
        s = {**s, "type": "ell", "r": [s["r"]] * 3, "rot": [0, 0, 0]}; t = "ell"
    if t == "ell":
        ax = axes_of(s.get("rot")); c = s["c"]; r = s["r"]; out = []
        for i in range(n):
            th = math.pi * (i + 0.5) / n
            for j in range(2 * n):
                ph = 2 * math.pi * j / (2 * n)
                u = [math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)]
                p = c
                for k in range(3): p = add(p, ax[k], u[k] * r[k])
                out.append(p)
        return out
    if t == "cone":
        return cloud({"type": "tube", "pts": [list(s["a"]) + [s["ra"]], list(s["b"]) + [s["rb"]]]}, n)
    if t == "tube":
        out = []
        P = s["pts"]
        for a, b in zip(P, P[1:]):
            d = nrm(sub(b, a)); u = nrm(crs(d, [0, 1, 0] if abs(d[1]) < .9 else [1, 0, 0])); v = crs(d, u)
            for i in range(n + 1):
                q = lerp(a, b, i / n)
                for j in range(12):
                    ph = 2 * math.pi * j / 12
                    out.append(add(add(q[:3], u, q[3] * math.cos(ph)), v, q[3] * math.sin(ph)))
        return out
    if t == "tri":
        out = []
        for i in range(n + 1):
            for j in range(n + 1 - i):
                a, b = i / n, j / n
                out.append([s["a"][k] + (s["b"][k] - s["a"][k]) * a + (s["c"][k] - s["a"][k]) * b for k in range(3)])
        return out
    raise ValueError(t)

def ell_axes(s):
    """the main shape's frame: [(unit axis, radius)] longest first"""
    t = s["type"]
    if t == "sphere": return [([0, 1, 0], s["r"]), ([0, 0, 1], s["r"]), ([1, 0, 0], s["r"])]
    if t == "ell":
        ax = axes_of(s.get("rot")); r = s["r"]
        return sorted([(nrm(ax[k]), r[k]) for k in range(3)], key=lambda e: -e[1])
    if t in ("cone", "tube"):
        P = [list(s["a"]) + [s["ra"]], list(s["b"]) + [s["rb"]]] if t == "cone" else s["pts"]
        L = nrm(sub(P[-1], P[0])); rr = max(p[3] for p in P)
        u = nrm(crs(L, [0, 1, 0] if abs(L[1]) < .9 else [1, 0, 0])); v = nrm(crs(L, u))
        return [(L, ln(sub(P[-1], P[0])) / 2 + rr * .3), (u, rr), (v, rr)]
    raise ValueError(t)

# ---- the outline: a half-width profile h(t) (t 0 at the head, 1 at the tip), a share of the greatest half-width ---
def prof(t, o):
    """o: base (the half-width at the root, a share), tc (where it is widest), m, pe (above tc: (1 - u^m)^pe --
    m 1 pe 1 a straight triangle, m 2 pe .5 an ellipse: a round tip, pe near 1 a pointed one)"""
    base, tc, m, pe = o.get("base", .7), o.get("tc", .3), o.get("m", 2.0), o.get("pe", .6)
    if t <= tc:
        return base + (1 - base) * math.sin(math.pi / 2 * (t / tc if tc > 0 else 1)) ** o.get("neck", 1.0)
    u = min(1.0, (t - tc) / (1 - tc))
    return max(0.0, 1 - u ** m) ** pe

def build_plane(sp, spec, olds, P):
    """A FLAT FAN (an elephant's): the outline authored in metres in the old ear's own plane -- `plane2d.outline`
    [[u, v]...], u back from the root along the plane's long-horizontal axis, v up its other -- from `origin` (the
    old root shape's centre, brought into the plane); the outline's first and last points (the root's ends) brought onto
    the head's surface and sunk, the root line deeper; the sheet otherwise exactly in the old ear's mid-plane."""
    main = olds[spec.get("main", "ear")]
    ex = spec.get("exclude", list(olds))
    pl = spec["plane2d"]
    ax = axes_of(main.get("rot")); r = main["r"]; c = main["c"]
    k = sorted(range(3), key=lambda i: r[i])   # (thin axis first)
    N = nrm(ax[k[0]])
    O = olds[pl["origin"]]["c"] if isinstance(pl["origin"], str) else pl["origin"]
    O = sub(O, mul(N, dot(sub(O, c), N)))
    U = nrm(ax[pl.get("uAxis", 0)]); U = nrm(sub(U, mul(N, dot(U, N))))
    if dot(U, sub(c, O)) < 0: U = mul(U, -1)
    V = nrm(crs(N, U))
    if V[1] < 0: V = mul(V, -1)
    No = N if dot(N, sub(c, olds[pl["origin"]]["c"] if isinstance(pl["origin"], str) else O)) >= 0 else mul(N, -1)
    if pl.get("outDir"): No = nrm(pl["outDir"])
    hint = spec.get("face", [0, 0, -1])
    if dot(N, hint) < 0: N = mul(N, -1)
    # (held `out` metres off the body -- along the plane's outward normal -- from `outRamp` of the way back on: an
    #  elephant's ear lies along its neck and shoulder, clear of them)
    def Pq(u, v):
        f = min(1.0, max(0.0, u / pl.get("outRamp", 0.3))); f = f * f * (3 - 2 * f)
        return add(add(add(O, U, u), V, v), No, pl.get("out", 0.0) * f)
    pts = [Pq(u, v) for u, v in pl["outline"]]
    th = spec.get("thick", 0.02)
    def proj(ps, h=0.004):
        ps = [list(q) for q in ps]
        for _ in range(5):
            q4 = [x for q in ps for x in ([q] + [add(q, e, h) for e in ([1, 0, 0], [0, 1, 0], [0, 0, 1])])]
            dd = fd(sp, {"exclude": ex, "points": q4})["d"]
            gs = [nrm([dd[4 * k + 1] - dd[4 * k], dd[4 * k + 2] - dd[4 * k], dd[4 * k + 3] - dd[4 * k]]) for k in range(len(ps))]
            ps = [add(q, g, -dd[4 * k]) for k, (q, g) in enumerate(zip(ps, gs))]
        return ps, gs
    cps, cgs = proj([pts[0], pts[-1]])
    m = max(th * 1.5, pl.get("sinkEnds", 0.03))
    first = [add(cps[k], cgs[k], -m) for k in range(2)]
    ra = pl.get("rootV", [pl["outline"][0][1] * 0.75, pl["outline"][-1][1] * 0.75])
    rps, rgs = proj([Pq(0, ra[0]), Pq(0, ra[1])])
    dr = pl.get("rootDepth", 0.08)
    R0 = add(rps[0], rgs[0], -dr); R1 = add(rps[1], rgs[1], -dr)
    dd = fd(sp, {"exclude": ex, "points": [R0, R1]})["d"]
    edge = [first[0]] + pts[1:-1] + [first[1]]
    de = fd(sp, {"exclude": ex, "points": edge})["d"]
    hw = max(abs(v) for _, v in pl["outline"])
    fin = {"id": spec.get("id", "ear"), "type": "fin", "bone": spec.get("bone", main.get("bone", "earL")),
           "root": [R0, R1], "edge": edge, "thick": th, "slope": spec.get("slope", 0.3), "face": N, "cup": spec.get("cup", 0.1),
           "color": spec.get("color", main.get("color"))}
    for kk in ("inner", "tip", "tipAt", "rim", "rimColor", "rimAt", "rimBack", "curl", "curlAt", "camber", "pat", "patFace", "hair", "swell"):
        if kk in spec: fin[kk] = spec[kk]
    if "inner" in fin: fin["innerRim"] = spec.get("innerRim", 0.05)
    if "rim" in spec: fin["rim"] = spec["rim"]
    if main.get("mirror", True): fin["mirror"] = True
    fin["fair"] = {"r": spec.get("fairM", 0.05), "sink": spec.get("fairSink", 3)}
    # (`edgeB`: the rim's bluntness on every edge point but the root's two ends -- sharp.js `b`: the sheet gains its
    #  thickness that many times faster in from the rim, so the edge shows a rounded thickness, not a knife's)
    if spec.get("edgeB"): fin["edge"] = [list(p) + ([spec["edgeB"]] if 0 < k < len(edge) - 1 else []) for k, p in enumerate(edge)]
    # (`patFrame` {u, r}: the `pat` laid in a frame of its own -- o the root's middle, u the given direction, v the
    #  sheet's normal -- not the nearest field shape's: an elephant's skin creases across the ear, as on its legs)
    if spec.get("patFrame"):
        pf = spec["patFrame"]; u = nrm(pf["u"]); v = nrm(sub(N, mul(u, dot(N, u))))
        fin["frame"] = {"o": lerp(R0, R1, 0.5), "u": u, "v": v, "r": pf["r"]}
    print("   rim distances to the body:", [round(x, 3) for x in de])
    return [fin], {"Lv": max(u for u, _ in pl["outline"]), "hw": hw, "th": th, "depth": dd}

def build(sp, spec, olds, P):
    """the new fin (and its extras: a lynx's tuft) from the old shapes (resolved) and the spec"""
    if spec.get("plane2d"): return build_plane(sp, spec, olds, P)
    main = olds[spec.get("main", "ear")]
    allp = [p for s in olds.values() if s.get("op") not in ("paint", "sub") and s["id"] not in spec.get("noreach", []) for p in cloud(s)]
    ids = list(olds)
    ex = spec.get("exclude", ids)
    if spec.get("skip"):   # (shapes the ear is measured without: a lion's mane -- the ear stands on the skull, in it)
        ex = ex + [s["id"] for s in load(sp)[1]["sculpt"]["shape"] if re.fullmatch(spec["skip"], s.get("id") or "")]
    spec = {**spec, "exclude": ex}
    # THE FRAME: L (toward the tip), W (across), N (the thin axis) -- from the main shape, or the spec's
    if main["type"] == "tri":
        tris = [olds[i] for i in spec.get("tris", [spec.get("main", "ear")])]
        apex = spec.get("apexPt") or main[spec.get("apex", "c")]
        bp = [t[k] for t in tris for k in ("a", "b", "c") if ln(sub(t[k], apex)) > 1e-5]
        base = spec.get("basePts") or max(((a, b) for a in bp for b in bp), key=lambda e: ln(sub(e[0], e[1])))
        L = nrm(sub(apex, lerp(base[0], base[1], .5))); W0 = nrm(sub(base[1], base[0]))
        c = lerp(lerp(base[0], base[1], .5), apex, .35)
        rl = ln(sub(apex, c)); rw = ln(sub(base[1], base[0])) / 2
    else:
        A = ell_axes(main); c = main["c"] if "c" in main else lerp(main["a"], main["b"], .5) if "a" in main else main["pts"][len(main["pts"]) // 2][:3]
        L, rl = A[0]; W0, rw = A[1]
        if spec.get("swapLW"): (L, rl), (W0, rw) = A[1], A[0]
        if spec.get("useAxis") == 2: (W0, rw) = A[2]
        # (a ROUND ear -- or `Lmode: "normal"` -- grows out along the head's normal there, square to its thin axis:
        #  its longest axis says little)
        mode = spec.get("Lmode", "axis" if rl > 1.35 * rw else "normal")
        if mode == "normal" and not spec.get("L"):
            Nt = A[2][0]; h = 0.004
            q = [c] + [add(c, e, h) for e in ([1, 0, 0], [0, 1, 0], [0, 0, 1])]
            dd = fd(sp, {"exclude": spec.get("exclude", list(olds)), "points": q})["d"]
            g = nrm([dd[1] - dd[0], dd[2] - dd[0], dd[3] - dd[0]])
            g = nrm(add(g, spec.get("Ladd", [0, 0, 0])))
            L = nrm(sub(g, mul(Nt, dot(g, Nt))))
            W0 = nrm(crs(Nt, L)); rw = max(rw, rl); rl = rw
    if spec.get("L"): L = nrm(spec["L"])
    # (L toward the outside: the end where the body field is further)
    if spec.get("Lhint") and not spec.get("L"):
        if dot(L, spec["Lhint"]) < 0: L = mul(L, -1)
    elif not spec.get("L"):
        pr = fd(sp, {"exclude": ex, "points": [add(c, L, rl), add(c, L, -rl)]})["d"]
        if pr[1] > pr[0]: L = mul(L, -1)
    if spec.get("Lplus"): L = nrm(add(L, spec["Lplus"]))   # (the ear's line nudged: out from the cheek, back)
    for ax_, deg in spec.get("tilt", []):   # (turns of the whole ear: [axis, degrees] ...)
        L = rot(L, nrm(ax_), math.radians(deg)); W0 = rot(W0, nrm(ax_), math.radians(deg))
    W = nrm(sub(W0, mul(L, dot(W0, L))))
    if spec.get("W"): W = nrm(sub(spec["W"], mul(L, dot(spec["W"], L))))
    if spec.get("turn"): W = rot(W, L, math.radians(spec["turn"]))
    if spec.get("faceTo"):   # (the hollow turned to look that way, as near as the ear's length allows)
        ft = spec["faceTo"]; Nt = nrm(sub(ft, mul(L, dot(ft, L))))
        W = nrm(crs(L, Nt))
    N = nrm(crs(W, L))
    hint = spec.get("faceTo") or spec.get("face", [1, 0, 0])
    if dot(N, hint) < 0: N = mul(N, -1)
    # THE EXTENT: the old ear's reach along L (all its shapes), its half-width along W
    c0 = spec.get("c", c)
    if spec.get("shift"): c0 = add(c0, spec["shift"])
    reach = max(dot(sub(p, c0), L) for p in allp) if not spec.get("reach") else spec["reach"]
    hw = spec.get("hw", max(abs(dot(sub(p, c0), W)) for p in cloud(main)) if main["type"] != "tri" else rw) * spec.get("wide", 1.0)
    T = add(c0, L, reach * spec.get("long", 1.0))
    def grad(q, h=0.002):
        dd = fd(sp, {"exclude": ex, "points": [q] + [add(q, e, h) for e in ([1, 0, 0], [0, 1, 0], [0, 0, 1])]})["d"]
        return dd[0], nrm([dd[1] - dd[0], dd[2] - dd[0], dd[3] - dd[0]])
    if spec.get("flat"):
        # A FLAT ear (a drop ear, a primate's, an elephant's): it lies along the head, its root where it leaves the skin
        # -- the old ear's root end (or `rootAt`) brought onto the surface; the root sunk along the head's normal there
        S = spec.get("rootAt") or add(c0, L, -rl * spec.get("rootK", 0.8))
        if isinstance(S, str): S = olds[S]["c"]
        for _ in range(4):
            d0, g = grad(S); S = add(S, g, -d0)
        _, D = grad(S)
        LD = nrm(spec["liftDir"]) if spec.get("liftDir") else D
        S = add(S, D, spec.get("lift0", 0.0) * hw)
        Lv = max(dot(sub(p, S), L) for p in allp) * spec.get("long", 1.0) if not spec.get("reach") else spec["reach"]
    else:
        # where the axis leaves the head: from deep inside, out to the tip -- or (`rootNear`: an ear whose axis only
        #  grazes the head, a horse's) the old ear's lower end, `rootNear` of its half-length below its centre, brought
        #  onto the skin
        k = 1.0
        if spec.get("rootNear"):
            S = add(c0, L, -rl * spec["rootNear"])
            for _ in range(5):
                d0, g = grad(S); S = add(S, g, -d0)
            D = L; LD = L; Lv = dot(sub(T, S), L)
            k = None
    if not spec.get("flat") and k is not None:
        while True:
            P0 = add(c0, L, -reach * k)
            if fd(sp, {"exclude": ex, "points": [P0]})["d"][0] < -0.002 or k > 6: break
            k += 0.5
        S = fd(sp, {"exclude": ex, "rays": [[P0, T]]})["hits"][0]
        if S is None:   # (the axis grazes past the head -- a horse's ear leans out over it: its root the head's
            #  surface nearest the axis, found by the field)
            qs = [lerp(P0, T, i / 40) for i in range(41)]
            dq = fd(sp, {"exclude": ex, "points": qs})["d"]
            S = qs[min(range(41), key=lambda i: dq[i])]
            for _ in range(4):
                d0, g = grad(S); S = add(S, g, -d0)
            note_ = "  (axis grazes: root at the nearest surface)"; print(sp + note_)
        S = add(S, L, -spec.get("sink", 0.0) * hw)
        D = L; LD = L
        Lv = dot(sub(T, S), L)
    o = spec.get("outline", {})
    skew = spec.get("skew", 0.0)   # (the tip leaning toward +W: a share of hw, growing as t^2)
    th = spec.get("thick", max(0.0006, min(0.03, 0.045 * Lv, 0.3 * hw)))
    # (the outline: across x = h(t) hw either side, t up the length; the root's ends in the head)
    ns = spec.get("ns", 9)
    ts = [0.0] + [(i / ns) ** 0.85 for i in range(1, ns)]
    x0 = prof(0.0, o) * hw
    # THE BASE: under each of its corners the head's surface found along D (the head curves away from the axis: a
    # corner of a broad ear stands lower than S) -- the rim's first and last points sunk below it there, so the rim
    # crosses the skin steeply instead of grazing along under it (a grazing rim, faired, drew a stepped seam down the
    # cheek); the root's ends deeper still
    def proj(ps, h=0.0015):
        """points brought onto the head's surface (Newton steps on its distance) -> (points, outward normals)"""
        ps = [list(q) for q in ps]
        for _ in range(4):
            q4 = [x for q in ps for x in ([q] + [add(q, e, h) for e in ([1, 0, 0], [0, 1, 0], [0, 0, 1])])]
            dd = fd(sp, {"exclude": ex, "points": q4})["d"]
            gs = [nrm([dd[4 * k + 1] - dd[4 * k], dd[4 * k + 2] - dd[4 * k], dd[4 * k + 3] - dd[4 * k]]) for k in range(len(ps))]
            ps = [add(q, g, -dd[4 * k]) for k, (q, g) in enumerate(zip(ps, gs))]
        return ps, gs
    # THE BASE: each corner of the outline's foot brought onto the head's surface (along its normal there), the rim's
    # first and last points sunk just under it there -- so the rim leaves the skin square to it; the root's ends deeper
    # still under points nearer the middle. (Run down the ear's own axis instead, a broad ear's outer corner on a round
    # head reached far down the cheek and the rim grazed along under the skin: faired, a stepped seam.)
    cps, cgs = proj([add(S, W, -x0 * 0.92), add(S, W, x0 * 0.92)])
    rps, rgs = proj([add(S, W, -x0 * 0.55), add(S, W, x0 * 0.55)])
    tsf = [round(dot(sub(q, S), D), 4) for q in cps]
    m = max(th * 1.5, spec.get("cornerSink", 0.2) * x0)
    dr = max(th * 2, x0 * 0.3)
    for it in range(12):   # (the root: deep enough that both ends are inside)
        R0 = add(rps[0], rgs[0], -dr); R1 = add(rps[1], rgs[1], -dr)
        dd = fd(sp, {"exclude": ex, "points": [R0, R1]})["d"]
        if max(dd) < -th * 0.6: break
        dr = min(dr * 1.3, 3 * x0)
    first = [add(cps[k], cgs[k], -m) for k in range(2)]
    lift = spec.get("lift", 0.0) * hw   # (a flat ear held that far off the skin, along the normal at its root)
    Pt = lambda x, t: add(add(add(S, L, t * Lv), W, x + skew * hw * t * t), LD, lift * min(1.0, t * 4) if D is not L else 0.0)
    # (a TUFT -- a lynx's -- is the outline itself run on past the tip as a narrow spike, `len` of the ear's length
    #  and `r` of its half-width: one sheet, black by the edge band `rim`, no piece of its own)
    tf = spec.get("tuft"); E1 = 1.0
    hfun = lambda t: prof(t, o)
    if tf:
        tl, rt = tf.get("len", 0.5), tf.get("r", 0.08); E1 = 1 + tl
        hfun = lambda t: max(prof(t, o), rt * (1 - max(0.0, t - 1) / tl) ** 0.8 if t < E1 else 0.0)
        ts = [x for x in ts if x < 0.93] + [0.97, 1.0 + 0.2 * tl, 1.0 + 0.5 * tl, 1.0 + 0.8 * tl]
    side = lambda sg: [Pt(sg * hfun(t) * hw, t) if t > 0 else first[(sg + 1) // 2] for t in ts]
    tipp = Pt(0.0, E1)
    if o.get("round"):   # (a round end: the tip point itself, the corner not kept)
        edge = side(-1) + [tipp] + side(1)[::-1]; corners = None
    else:
        edge = side(-1) + [tipp] + side(1)[::-1]; corners = [len(ts)]
    # (a fold or droop: points past `bendAt` of the length turned about W by `bend` degrees, toward -N (the back) --
    #  a pig's lop, a drop ear)
    if spec.get("bend"):
        ba = spec.get("bendAt", .5); ang = math.radians(spec["bend"])
        piv = add(S, L, ba * Lv)
        def bendp(p):
            t = dot(sub(p, S), L) / Lv
            if t <= ba: return p
            f = min(1.0, (t - ba) / (1 - ba))
            return add(piv, rot(sub(p, piv), W, ang * (0.4 + 0.6 * f)))
        edge = [bendp(p) for p in edge]
        N2 = rot(N, W, ang * .5)
    else:
        N2 = N
    fin = {"id": spec.get("id", "ear"), "type": "fin", "bone": spec.get("bone", main.get("bone", "earL")),
           "root": [R0, R1], "edge": edge}
    if corners: fin["corners"] = corners
    fin.update({"thick": th, "slope": spec.get("slope", 0.3), "face": N2, "cup": spec.get("cup", 0.6),
                "color": spec.get("color", main.get("color"))})
    for kk in ("inner", "tip", "tipAt", "rim", "rimColor", "rimAt", "rimBack", "curl", "curlAt", "camber", "pat", "patFace", "hair", "when", "n", "across", "swell"):
        if kk in spec: fin[kk] = spec[kk]
    if "inner" in fin: fin["innerRim"] = spec.get("innerRim", 0.15) * hw
    if "rim" in spec: fin["rim"] = spec["rim"] * hw
    if main.get("mirror", True): fin["mirror"] = True
    if "pat" not in spec and main.get("pat") and spec.get("keepPat", True): fin["pat"] = main["pat"]
    if fin.get("pat") is None: fin.pop("pat", None)
    # (the join: a fillet `fair` of the half-width; the sheet's buried part drawn `sink` cells under the skin where it
    #  nears it -- at the default 1 a buried root showed through a coarse head as a stepped ghost down the cheek)
    fin["fair"] = {"r": round(spec.get("fair", 0.35) * hw, 4), "sink": spec.get("fairSink", 3)}
    if spec.get("ribs"):   # (a pattern laid in the sheet's own frame: u up the ear from its root, v out of its back --
        #  a bat's transverse ribs as `ridges`, `ribs` the frame r, a share of the length: a groove every 1.3 r)
        fin["frame"] = {"o": S, "u": L, "v": mul(N2, -1), "r": round(spec["ribs"] * Lv, 5)}
    out = [fin]
    th_ = spec.get("tuftHorn")
    if th_:   # (a tuft of long hairs up the BACK of the ear and on past its tip -- a red squirrel's: a thin `horn`
        #  rooted in the head behind the ear's root, so it is joined to the body, not to the sheet)
        bk = mul(N, -1); r0 = th_.get("r", 0.15) * hw
        cb = th_.get("back", 0.45) * spec.get("cup", 0.6) * hw   # (clear of the cupped back: the hollow's middle sits behind the rim)
        hp = [add(add(S, L, -0.25 * Lv), bk, th + r0 * 0.6) + [r0],
              add(Pt(0, 0.45), bk, th + r0 + cb) + [r0 * 0.9],
              add(Pt(0, 0.9), bk, th + r0 + cb * 0.5) + [r0 * 0.7],
              Pt(0, 1.0 + th_.get("len", 0.6) * 0.5) + [r0 * 0.45],
              Pt(0, 1.0 + th_.get("len", 0.6)) + [r0 * 0.12]]
        horn = {"id": spec.get("id", "ear") + "Tuft", "type": "horn", "bone": fin["bone"], "pts": hp, "color": th_.get("color", fin["color"])}
        if th_.get("when"): horn["when"] = th_["when"]
        if th_.get("hair") is not None: horn["hair"] = th_["hair"]
        if main.get("mirror", True): horn["mirror"] = True
        out.append(horn)
    ts_ = spec.get("tassel")
    if ts_:   # (2026-11-08 evening, 2nd pass: a red squirrel's TUFT as a BUSHY BRUSH on the ear. It was `tuftHorn`, one thin
        #  horn behind the ear ("a separate single hair"), then a tall tassel drawn in to one point that edge-on read as an
        #  antenna. Now: hair strands (horn `strand`s, sharp.js strandMesh, the whiskers' kind; near mesh only) rooted
        #  along the upper rim on both edges from `from` of the ear's length and round over the tip, and a dense cluster on
        #  both faces round the tip; each FANS OUT from the ear's line -- `fan` degrees in the ear's plane toward its own
        #  side (most at the lowest roots), `across` degrees out of the plane (front or back), jittered -- curling a little
        #  back up, of VARIED lengths `len` [min, max] of the ear's length: a brush rising ~0.45 of the ear's length over
        #  the tip, wide and with volume from every side. Its CORE, for the far mesh (strands are near-only): a short, fat
        #  `horn` (`<id>Tassel`) from inside the ear's tip, flattened across the ear (`coreAspect`), `coreLen` of the ear's
        #  length past the tip -- a small dark tip shape. Coloured as the ear's back (`color`), darkening (`tip`).)
        import random
        rng = random.Random(ts_.get("seed", 7))
        cupk = spec.get("cup", 0.6); r0 = ts_.get("r", 0.0006); per = ts_.get("per", 8); t0 = ts_.get("from", 0.6)
        lmin, lmax = ts_.get("len", [0.25, 0.48]); fan = math.radians(ts_.get("fan", 32)); acr = math.radians(ts_.get("across", 18))
        nf = N2; bk = mul(nf, -1)
        onSheet = lambda q, d: add(q, bk, cupk * d)   # (a point d in from the rim, on the cupped sheet's middle)
        # -- the CORE (far mesh too) --
        cl = ts_.get("coreLen", 0.3); cr = ts_.get("coreR", 0.35) * hw
        base = onSheet(Pt(0.0, E1 - 0.22), 0.3 * hw)
        cpts = [base + [cr * 0.7], onSheet(Pt(0.0, E1 - 0.08), 0.1 * hw) + [cr],
                add(Pt(0.0, E1 + cl * 0.45), bk, 0.1 * hw) + [cr * 0.75], add(Pt(0.0, E1 + cl), bk, 0.15 * hw) + [0.0]]
        core = {"id": spec.get("id", "ear") + "Tassel", "type": "horn", "bone": fin["bone"], "pts": [[round(v, 5) for v in q] for q in cpts],
                "up": [round(v, 4) for v in nf], "aspect": ts_.get("coreAspect", 0.55), "sides": 8, "color": ts_.get("color", fin["color"])}
        if ts_.get("tip"): core.update({"tip": ts_["tip"], "tipAt": ts_.get("coreTipAt", 0.35)})
        if ts_.get("when"): core["when"] = ts_["when"]
        if main.get("mirror", True): core["mirror"] = True
        out.append(core)
        # -- the BRUSH --
        def strand(R, B, side, f, face=0):
            # (side -1 / 0 / 1: which way in the plane it fans; f: 0 at the tip .. 1 at the lowest root; face: -1 back, 1 front, 0 either)
            ang = side * fan * (0.35 + 0.65 * f) + rng.uniform(-0.25, 0.25) * fan
            d = rot(L, nf, ang)                                      # (fanned in the ear's plane)
            if dot(d, W) * side < 0: d = rot(L, nf, -ang)            # (toward its own side)
            ac = (face if face else rng.choice((-1, 1))) * rng.uniform(0.2, 1.0) * acr
            d = nrm(add(mul(d, math.cos(ac)), nf, math.sin(ac)))     # (and out of it, front or back)
            ln_ = rng.uniform(lmin, lmax) * Lv * (1.0 - 0.35 * f)
            e = nrm(add(d, L, 0.6))                                  # (its end curling back up)
            C = add(R, d, 0.5 * ln_); E = add(C, e, 0.5 * ln_)
            q = lambda u: [(1 - u) ** 2 * R[k] + 2 * (1 - u) * u * C[k] + u * u * E[k] for k in range(3)]
            rr = r0 * rng.uniform(0.85, 1.2)
            return [B + [rr], R + [rr], q(0.3) + [rr * 0.8], q(0.6) + [rr * 0.55], q(0.85) + [rr * 0.3], E + [0.0]]
        strands = []
        bury = 0.2 * hw
        for sg in (-1, 1):   # (along the upper rim, both edges)
            for i in range(per):
                tt = t0 + (0.97 - t0) * i / max(1, per - 1)
                R = Pt(sg * hfun(tt) * hw, tt)
                inn = nrm(sub(Pt(0.0, tt - 0.05), R))
                strands.append(strand(R, onSheet(add(R, inn, bury), bury), sg, (0.97 - tt) / (0.97 - t0)))
        for i in range(3):   # (over the tip)
            strands.append(strand(tipp, onSheet(Pt(0.0, E1 - 0.1), 0.2 * hw), (-1, 0, 1)[i], 0.0))
        nb = ts_.get("tipN", 12)
        for i in range(nb):   # (the dense cluster on both faces round the tip)
            tt = rng.uniform(0.74, 0.95); x = rng.uniform(-0.75, 0.75) * hfun(tt) * hw; fc = 1 if i % 2 else -1
            rd = hfun(tt) * hw - abs(x)
            mid = onSheet(Pt(x, tt), rd)
            R = add(mid, nf, fc * (0.5 * th + r0)); B = add(mid, nf, -fc * 0.3 * th)
            strands.append(strand(R, add(B, L, -0.05 * Lv), 1 if x > 0 else -1, (0.95 - tt) / 0.3 * 0.6, fc))
        for k, P_ in enumerate(strands):
            h = {"id": spec.get("id", "ear") + "Tuft%d" % k, "type": "horn", "strand": True, "bone": fin["bone"],
                 "pts": [[round(v, 5) for v in p] for p in P_], "color": ts_.get("color", fin["color"])}
            if ts_.get("tip"): h.update({"tip": ts_["tip"], "tipAt": ts_.get("tipAt", 0.4)})
            h["n"] = ts_.get("n", 4)
            if ts_.get("when"): h["when"] = ts_["when"]
            if main.get("mirror", True): h["mirror"] = True
            out.append(h)
    info = {"S": S, "T": T, "Lv": Lv, "hw": hw, "th": th, "dr": dr, "depth": dd + [round(x, 4) for x in tsf]}
    return out, info

# ---- writing: numbers, or (an ear written over the params: the lion's) expressions -------------------------------
def exprize(shapes, main_raw, P):
    """points p written as the main shape's own centre expression moved by (p - c) / (earS hs): its ear moves and
    grows with the params (the lioness's bigger ears)"""
    cx = main_raw["c"]
    cv = [ev(v, P) for v in cx]
    f = ev("earS*hs", P)
    names = ["earX", "earY", "earZ"]
    def pt(p):
        out = []
        for k in range(3):
            d = (p[k] - cv[k]) / f
            out.append(cx[k].replace(names[k], "(%s%+.5f*earS)" % (names[k], d), 1) if names[k] in cx[k] else round(p[k], 4))
        return out
    def ln_(v): return "%.5f*earS*hs" % (v / f)
    for s in shapes:
        if s["type"] == "fin":
            s["root"] = [pt(p) for p in s["root"]]; s["edge"] = [pt(p) for p in s["edge"]]
            for k in ("thick", "fair", "innerRim", "rim"):
                if k in s and isinstance(s[k], (int, float)): s[k] = ln_(s[k])
            if isinstance(s.get("fair"), dict): s["fair"]["r"] = ln_(s["fair"]["r"])
        if s["type"] == "horn":
            s["pts"] = [pt(p) + [ln_(p[3])] for p in s["pts"]]
    return shapes

def run(sp):
    spec = SPEC[sp]
    if spec.get("of"): return run_variant(sp, spec)
    txt, d = load(sp); sc = d["sculpt"]; sh = sc["shape"]
    if sp not in ORIG:
        ids = set(spec["ids"])
        ORIG[sp] = [s for s in sh if s.get("id") in ids]
        missing = ids - {s.get("id") for s in ORIG[sp]}
        if missing: raise RuntimeError(sp + ": not found " + str(missing))
        json.dump(ORIG, open(BK, "w"), indent=0)
    P = params_of(d)
    olds = {s["id"]: resolve(s, P) for s in ORIG[sp]}
    new, info = build(sp, spec, olds, P)
    new = [r5(s) for s in new]
    if spec.get("expr"): new = exprize(new, [s for s in ORIG[sp] if s["id"] == spec.get("main", "ear")][0], P)
    for s in new:
        if s["type"] == "fin":
            s["edge"] = [[round(v, 4) if isinstance(v, float) else v for v in p] for p in s["edge"]]
    # (the file as it is now: the old ear shapes -- or a previous run's fin -- replaced where the first of them stood)
    txt, d = load(sp); sh = d["sculpt"]["shape"]
    gone = set(spec["ids"]) | {s["id"] for s in new}
    idx = [i for i, s in enumerate(sh) if s.get("id") in gone]
    at = idx[0] if idx else len(sh)
    out = sh[:at] + new + [s for i, s in enumerate(sh) if i >= at and s.get("id") not in gone]
    save(sp, out, txt)
    print("%-22s fin Lv %.3f hw %.3f thick %.4f root depth %s  (-%d +%d shapes)" % (sp, info["Lv"], info["hw"], info["th"], [round(x, 4) for x in info["depth"]], len(idx), len(new)))
    if spec.get("about") and not note(sp, "(2026-11-08, ears2.py)", spec["about"]):
        note_sculpt(sp, "(2026-11-08, ears2.py)", spec["about"])

# ---- A VARIANT'S EARS (2026-11-08: the fennec, a fox variant): `of` the species, `variant` its name -- the ear built
# from the species' own old ear shapes (ears2_orig.json) as its SPEC builds it, with this entry's numbers over them
# (`long`, `wide`, its outline), and written into the variant's own `sculpt.shape` (creatures.js sculptOver: shapes over
# the base's by id), with the rest of the variant (`look`: scale, colors, its paints) -- every field of the base's ear
# the new one has not `null`, so nothing of the old ear is left over it. The base's shape build is shared (bodies.js):
# only the ear (a fin: a detail) and the paint are the variant's own.
def run_variant(key, spec):
    base = spec["of"]; name = spec["variant"]
    bspec = {**SPEC[base], **{k: v for k, v in spec.items() if k not in ("of", "variant", "look", "about")}}
    txt, d = load(base)
    P = params_of(d)
    olds = {s["id"]: resolve(s, P) for s in ORIG[base]}
    new, info = build(base, bspec, olds, P)
    new = [r5(s) for s in new]
    old_ids = {s["id"]: s for s in d["sculpt"]["shape"]}
    for s in new:
        if s["type"] == "fin": s["edge"] = [[round(v, 4) if isinstance(v, float) else v for v in p] for p in s["edge"]]
        for k in old_ids.get(s["id"], {}):
            if k not in s: s[k] = None
    look = json.loads(json.dumps(spec.get("look", {})))
    sh = [s for s in new] + look.pop("shape", [])
    var = {**look, "sculpt": {"shape": sh}}
    vs = d.get("variants") or {}
    vs[name] = var
    save_variants(base, vs, txt)
    print("%-22s %s: fin Lv %.3f hw %.3f thick %.4f root depth %s" % (base, name, info["Lv"], info["hw"], info["th"], [round(x, 4) for x in info["depth"]]))
    if spec.get("about"): note(base, "(2026-11-08, ears2.py %s)" % name, spec["about"])

def save_variants(sp, vs, txt):
    """the species' `variants` written again (2-space JSON as the file has it; a sculpt's shapes one a line), the
    rest of the file untouched"""
    from shp import path_of
    d = json.loads(txt)
    lines = txt.split("\n")
    a = next(i for i, l in enumerate(lines) if l.startswith('  "variants": {'))
    depth, b = 0, a
    for b in range(a, len(lines)):
        depth += lines[b].count("{") + lines[b].count("[") - lines[b].count("}") - lines[b].count("]")
        if depth == 0: break
    keep = {}
    def tok(v):
        if isinstance(v, dict):
            out = {}
            for k, x in v.items():
                if k == "shape" and isinstance(x, list):
                    out[k] = []
                    for s in x: t = "@@S%d@@" % len(keep); keep[t] = json.dumps(s); out[k].append(t)
                else: out[k] = tok(x)
            return out
        return v
    body = json.dumps(tok(vs), indent=2)
    for t, j in keep.items(): body = body.replace(json.dumps(t), j)
    body = "\n".join(("  " + l if i else l) for i, l in enumerate(body.split("\n")))
    tail = lines[b][lines[b].index("}") + 1:]
    out = "\n".join(lines[:a] + ['  "variants": ' + body + tail] + lines[b + 1:])
    assert json.loads(out)["variants"] == json.loads(json.dumps(vs)), "variants not written back as given"
    open(path_of(sp), "w").write(out)

def note_sculpt(sp, tag, text):
    """the same in the sculpt's own `_about` (a species whose top level has none: the generated hoofed ones)"""
    from shp import path_of
    path = path_of(sp); txt = open(path).read(); d = json.loads(txt)
    old = (d.get("sculpt") or {}).get("_about")
    if old is None: return False
    base = old.split(" " + tag)[0]
    new = base + " " + tag + " " + text
    for enc in (False, True):
        o = json.dumps(old, ensure_ascii=enc)
        if txt.count(o) == 1:
            open(path, "w").write(txt.replace(o, json.dumps(new, ensure_ascii=enc), 1)); json.loads(open(path).read()); return True
    raise RuntimeError(sp + ": sculpt _about not found verbatim once")

def undo(sp):
    txt, d = load(sp); sh = d["sculpt"]["shape"]
    spec = SPEC[sp]; newids = {spec.get("id", "ear"), spec.get("id", "ear") + "Tuft"}
    idx = [i for i, s in enumerate(sh) if s.get("id") in newids]
    at = idx[0] if idx else len(sh)
    out = sh[:at] + ORIG[sp] + [s for i, s in enumerate(sh) if i >= at and s.get("id") not in newids]
    save(sp, out, txt); print(sp, "undone")

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--undo":
        for a in args[1:]: undo(a if "/" in a else "mammals/" + a)
        sys.exit()
    todo = []
    for a in args:
        if a == "all": todo += list(SPEC)
        elif a in FAMILY: todo += FAMILY[a]
        else: todo.append(a if "/" in a else ("mammals/" + a if "mammals/" + a in SPEC else "monsters/" + a))
    for sp in todo: run(sp)
