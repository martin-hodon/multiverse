# bills.py SPECIES... | all : BILLS and BEAKS made the engine's `horn` (sharp.js), as the crane's (named.py crane()):
# TWO MANDIBLES, each a horn whose centreline runs along the line the bill closes on (the commissure) -- the upper's
# cross-section a dome above it (flat=1: its underside flat where it shuts on the lower), the lower's a dome below
# it (up -y, flat=1) -- so the two meet along the mouth line, and each ends in a real point (the lower's on that line,
# the upper's where the old bill ended, past a hooked tip's curve). Read from what drew the bill in the field:
#   a pair of tubes (upperBill/lowerBill, a raptor's upper/lower ...): r both half-width and half-height;
#   a chain of ells (upperBill0..21 ...): its long axes along the bill, ry the half-height, rz the half-width;
#   one tube or chain for both (a heron's bill, an owl's beak, a spoonbill): split at a line a little below its middle.
# The commissure where both mandibles are: halfway between the upper's underside and the lower's top (they overlapped in
# the field); past the lower's tip the upper's centreline follows its own underside (a hook's inner side). Widths and
# heights stay as they were (the outline does not change); a chain's colours become the horn's color / tip / tipAt.
# The roots sunk into the face (back along the bill, found on the body's field). The cere, gape, knob, casque of a
# cassowary stay in the field (blob parts); a hornbill's casque becomes a third horn riding on the upper. Paint ops on
# the bill's tip (vulture, griffin, spoonbill) become the horn's `tip` colour. RE-RUN after the species' generator.
import sys, re, math
from sharp2 import *
from claws import run as claws_run

EPS = 0.0003   # (half the gap between the two mandibles' flat faces)

class Smp:
    """a sample along a mandible: centre c, unit tangent t (in the xy plane), half-height h (along n, square to t, up),
    half-width w, colour"""
    def __init__(s, c, t, h, w, col):
        s.c, s.t, s.h, s.w, s.col = list(c), nrm([t[0], t[1], 0]), h, w, col
        s.n = [-s.t[1], s.t[0], 0]
    top = property(lambda s: add(s.c, s.n, s.h))
    bot = property(lambda s: add(s.c, s.n, -s.h))

def tube_smp(s):
    P = [list(p) for p in s["pts"]]; out = []
    # (a HOOK drawn as a tube that turns back down past a narrowed end -- a gull's, a pelican's, a vulture's: its girth
    # held through the turn, so the tip is the hook's, not a blob under a needle)
    if len(P) > 3 and P[-1][0] < P[-2][0] and P[-1][3] > P[-2][3]:
        P[-2][3] = (P[-3][3] + P[-1][3]) / 2
    for i, p in enumerate(P):
        a, b = P[max(0, i - 1)], P[min(len(P) - 1, i + 1)]
        out.append(Smp(p[:3], sub(b, a), p[3], p[3], s.get("color")))
    return out, P[-1][3]

def ell_smp(S, every=None):
    """a chain of ells (in order) as samples; `every`: keep every n-th (and the last)"""
    out = []
    for s in S:
        th = math.radians((s.get("rot") or [0, 0, 0])[2])
        out.append(Smp(s["c"], [math.cos(th), math.sin(th)], s["r"][1], s["r"][2], s.get("color")))
    # (the tangents from the chain itself where it is dense enough)
    for i in range(1, len(out) - 1):
        d = sub(out[i + 1].c, out[i - 1].c)
        if ln(d) > 1e-6: out[i].t = nrm([d[0], d[1], 0]); out[i].n = [-out[i].t[1], out[i].t[0], 0]
    if every and len(out) > every * 2:
        keep = list(range(0, len(out) - 1, every)) + [len(out) - 1]
        out = [out[i] for i in keep]
    return out, S[-1]["r"][0]

def yline(pts):
    """y(x) along points [x, y] (the part of them where x still rises), clamped"""
    P = [pts[0]]
    for p in pts[1:]:
        if p[0] > P[-1][0]: P.append(p)
        else: break
    def f(x):
        if x <= P[0][0]: return P[0][1]
        for a, b in zip(P, P[1:]):
            if x <= b[0]: return a[1] + (b[1] - a[1]) * (x - a[0]) / ((b[0] - a[0]) or 1)
        return P[-1][1]
    return f

def colours(U):
    """a chain's colours as color, tip, tipAt (the share of the samples before the last colour starts)"""
    cs = [u.col for u in U]
    if len(set(cs)) == 1: return cs[0], None, None
    last = cs[-1]; k = len(cs) - 1
    while k > 0 and cs[k - 1] == last: k -= 1
    body = max(set(cs[:k]), key=cs[:k].count)
    return body, last, round(max(0.3, k / len(cs)), 2)

def clampa(a): return round(max(0.25, min(4.0, a)), 3)

def closest(P, q):
    """the point of polyline P nearest q, and whether it is P's last point reached from beyond it (q past its end)"""
    best = None
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]; ab = sub(b, a); L2 = dot(ab, ab) or 1e-12
        t = dot(sub(q, a), ab) / L2; tc = max(0.0, min(1.0, t)); p = add(a, ab, tc); dd = ln(sub(q, p))
        if best is None or dd < best[0]: best = (dd, p, i == len(P) - 2 and t > 1.0)
    return best[1], best[2]

def mandibles(U, tipU, L, tipL):
    """the two horns' points [x, y, z, r, aspect] from the upper's and lower's samples (tipU / tipL: how far past the
    last sample's centre each old bill reached). The commissure: halfway between the upper's underside and the
    NEAREST point of the lower's top (so a down-curved bill -- a hoopoe's, an ibis's -- is matched across, not by x)"""
    eU = add(U[-1].c, U[-1].t, tipU); eL = add(L[-1].c, L[-1].t, tipL)
    Etop = [l.top for l in L] + [eL]
    Bbot = [u.bot for u in U] + [eU]
    up = []
    free = [u for u in U if closest(Etop, u.bot)[1]]
    for u in U:
        B = u.bot; p, beyond = closest(Etop, B)
        if not beyond:
            m = lerp(B, p, 0.5)
            up.append(add(m, u.n, EPS) + [u.w, clampa(ln(sub(u.top, m)) / u.w)])
        else:
            # (past the lower's tip: from the underside back to the middle by the tip -- k 1 -> 0 -- the dome growing
            # round to match, so a hook's centreline is not thrown behind it)
            k = 1 - (free.index(u) + 1) / (len(free) + 1)
            up.append(add(u.c, u.n, -k * u.h) + [u.w, clampa((1 + k) * u.h / u.w)])
    up.append(eU + [0.0, up[-1][4]])
    lo = []
    for l in L:
        E = l.top; p, _ = closest(Bbot, E); m = lerp(E, p, 0.5)
        lo.append(add(m, l.n, -EPS) + [l.w, clampa(ln(sub(m, l.bot)) / l.w)])
    p, _ = closest(Bbot, eL)
    lo.append(add(lerp(eL, p, 0.5), L[-1].n, -EPS) + [0.0, lo[-1][4]])
    return up, lo

def single(S, tipe, split=0.2, lfrac=0.85):
    """one tube / chain drawing both mandibles: split at `split` x its half-height below the middle; the lower as far
    as lfrac of the way to the tip"""
    up, lo = [], []
    for s in S:
        m = add(s.c, s.n, -split * s.h)
        up.append(add(m, s.n, EPS) + [s.w, clampa((1 + split) * s.h / s.w)])
    e = add(S[-1].c, S[-1].t, tipe); up.append(e + [0.0, up[-1][4]])
    # (the lower: along the same line, ending at lfrac of the length, its tip on the line)
    Ls = [0.0]
    for a, b in zip(S, S[1:]): Ls.append(Ls[-1] + ln(sub(b.c, a.c)))
    Ltot = Ls[-1] + tipe; cut = Ltot * lfrac
    for s, sl in zip(S, Ls):
        if sl > cut: break
        m = add(s.c, s.n, -split * s.h)
        lo.append(add(m, s.n, -EPS) + [s.w * 0.92, clampa((1 - split) * s.h / (s.w * 0.92))])
    # (its tip: on the line at cut)
    j = max(i for i, sl in enumerate(Ls) if sl <= cut); s = S[j]
    nx = S[min(j + 1, len(S) - 1)]; f = (cut - Ls[j]) / ((Ls[j + 1] - Ls[j]) if j + 1 < len(Ls) else 1)
    c = add(s.c, sub(nx.c, s.c), min(1, f)); hh = s.h + (nx.h - s.h) * min(1, f)
    lo.append(add(add(c, s.n, -split * hh), s.n, -EPS) + [0.0, lo[-1][4]])
    return up, lo

def rooted(sp, Ps, exclude, need=0.5, maxk=4.0):
    """the roots sunk into the face, the aspect carried onto the points sink adds"""
    out = sink_many(sp, [[p[:4] for p in P] for P in Ps], exclude, need=need, maxk=maxk)
    res = []
    for Q, P in zip(out, Ps):
        k = len(Q) - len(P)
        mid = all(abs(p[2]) < 1e-6 for p in P)   # (a bill on the midline keeps its sunk root there too)
        res.append([q[:2] + [0.0 if mid else q[2]] + q[3:4] + [P[0][4]] for q in Q[:k]] + P)
    return res

def bill_horns(sp, src_u, src_l, up, lo, exclude, uk=None, lk=None, col=None, maxk=4.0):
    # (the sections' up: square to each mandible's own first segment -- taken before the roots are sunk, so a root
    # walked in up the field's gradient does not tip it)
    uu = perp_up(nrm(sub(up[1], up[0]))); ul = mul(perp_up(nrm(sub(lo[1], lo[0]))), -1)
    up, lo = rooted(sp, [up, lo], exclude, maxk=maxk)
    hu = horn_of(r5(up), src_u, up=r5(uu), flat=1, keel=0.06, sides=14, **(uk or {}))
    hl = horn_of(r5(lo), src_l, up=r5(ul), flat=1, sides=14, **(lk or {}))
    hu["id"] = src_u["id"] if not re.search(r"\d+$", src_u["id"]) else re.sub(r"\d+$", "", src_u["id"])
    hl["id"] = src_l["id"] if not re.search(r"\d+$", src_l["id"]) else re.sub(r"\d+$", "", src_l["id"])
    if col:
        for h, c in zip((hu, hl), col):
            if c and c[0]: h["color"] = c[0]
            if c and c[1]: h["tip"] = c[1]; h["tipAt"] = c[2]
    return hu, hl

def r5(x):
    if isinstance(x, list): return [r5(v) for v in x]
    if isinstance(x, float): return round(x, 5)
    if isinstance(x, dict): return {k: r5(v) for k, v in x.items()}
    return x

# ------------------------------------------------------------------------------------------------------------------
def hookend(up, ybot):
    """a HOOKED upper (a gull's, a pelican's, a vulture's: the old tube turned back down at its end, a knob under a
    needle): cut at its forward-most point, then one smooth turn down to a point at the old knob's underside (ybot)"""
    m = max(range(len(up) - 1), key=lambda i: up[i][0])
    a = up[m]; r = a[3]; drop = a[1] - ybot
    return up[:m + 1] + [[a[0] + r * 0.55, a[1] - drop * 0.42, a[2], r * 0.7, a[4]],
                         [a[0] + r * 0.35, a[1] - drop * 0.8, a[2], r * 0.35, a[4]],
                         [a[0] + r * 0.05, a[1] - drop, a[2], 0.0, a[4]]]

def pair(sp, uid="upperBill", lid="lowerBill", tipcol=None, extra=()):
    """a pair of tubes; tipcol: (paint ell id, its colour share) -> the upper's tip colour; extra: more ids removed"""
    ids = [uid, lid] + ([tipcol[0]] if tipcol else []) + list(extra)
    def make(o):
        U, tu = tube_smp(o[uid]); L, tl = tube_smp(o[lid])
        up, lo = mandibles(U, tu, L, tl)
        Q = o[uid]["pts"]
        if len(Q) > 3 and Q[-1][0] < Q[-2][0] and Q[-1][3] > Q[-2][3]: up = hookend(up, Q[-1][1] - Q[-1][3])
        uk = {}
        if tipcol: uk = {"tip": o[tipcol[0]]["color"], "tipAt": tipcol[1]}
        hu, hl = bill_horns(sp, o[uid], o[lid], up, lo, ids, uk=uk, lk=dict(uk) if tipcol and len(tipcol) > 2 else None)
        return [hu, hl]
    replace(sp, ids, make)

def chain(sp, upre, lpre, every=3, suffix="", when=None, extra_lower=None):
    """chains of ells upre0.. / lpre0.. (suffix: a variant's, e.g. 'T'); extra_lower: a single ell for the lower"""
    def ids_of(txtS):
        U = sorted([s for s in txtS if re.fullmatch(re.escape(upre) + r"\d+" + suffix, s.get("id", ""))], key=lambda s: int(re.findall(r"\d+", s["id"])[-1]))
        L = sorted([s for s in txtS if re.fullmatch(re.escape(lpre) + r"\d+" + suffix, s.get("id", ""))], key=lambda s: int(re.findall(r"\d+", s["id"])[-1]))
        return U, L
    txt, d = load(sp); U0, L0 = ids_of(d["sculpt"]["shape"])
    if extra_lower:
        L0 = [s for s in d["sculpt"]["shape"] if s.get("id") in extra_lower]
    ids = [s["id"] for s in U0 + L0]
    if extra_lower:   # (a parrot's lip ell at the lower's front: inside the new lower, drawn as a detail it z-fights)
        ids += [s["id"] for s in d["sculpt"]["shape"] if s.get("id") == "lowerLip"]
    def make(o):
        Us = [o[s["id"]] for s in U0]; Ls = [o[s["id"]] for s in L0]
        U, tu = ell_smp(Us, every);
        if extra_lower:
            L, tl = ell_smp(Ls[:1])
            # (a single ell -- a parrot's short deep lower mandible: back, centre and front samples)
            l = L[0]; f = Smp(add(l.c, l.t, Ls[0]["r"][0] * 0.5), l.t, l.h * 0.75, l.w * 0.8, l.col)
            b = Smp(add(l.c, l.t, -Ls[0]["r"][0] * 0.6), l.t, l.h * 0.8, l.w * 0.8, l.col)
            L = [b, l, f]; tl = Ls[0]["r"][0] * 0.5
        else:
            L, tl = ell_smp(Ls, every)
        up, lo = mandibles(U, tu, L, tl)
        cu, cl = colours(U), colours(L)
        # (a parrot's round face: a root not inside within a radius back is walked in up the field's gradient, not
        # carried on straight back out under the cheek)
        hu, hl = bill_horns(sp, Us[0], Ls[0], up, lo, ids, col=(cu, cl), maxk=1.0 if extra_lower else 4.0)
        hu["id"] = upre.rstrip("0123456789") + suffix; hl["id"] = lpre + suffix if not extra_lower else Ls[0]["id"]
        return [hu, hl]
    replace(sp, ids, make)

def one(sp, ids, split=0.2, lfrac=0.85, tip=None, lid=None):
    """one tube / chain of tubes drawing both mandibles (ids in order: their points joined); tip: (colour, at) for
    the upper; lid: the id of the lower"""
    def make(o):
        S = []; te = 0
        cols = []
        for i in ids:
            s = o[i]
            if s["type"] != "tube": continue
            smp, te = tube_smp(s)
            if S and ln(sub(smp[0].c, S[-1].c)) < S[-1].w: smp = smp[1:]   # (a joint: one point)
            S += smp
        for k in range(len(S)):   # (the tangents once more, over the joined line)
            a, b = S[max(0, k - 1)], S[min(len(S) - 1, k + 1)]
            S[k].t = nrm([b.c[0] - a.c[0], b.c[1] - a.c[1], 0]); S[k].n = [-S[k].t[1], S[k].t[0], 0]
        up, lo = single(S, te, split, lfrac)
        src = o[ids[0]]; srcl = dict(src); srcl["id"] = lid or "lowerBill"
        uk = {"tip": tip[0], "tipAt": tip[1]} if tip else None
        hu, hl = bill_horns(sp, src, srcl, up, lo, list(o), uk=uk)
        hu["id"] = src["id"]; hl["id"] = lid or "lowerBill"
        return [hu, hl]
    return make

def one_r(sp, ids, extra=(), **kw):
    replace(sp, list(ids) + list(extra), one(sp, ids, **kw))

def ridge(sp, pre, every=3, sink_need=0.5):
    """a chain of ells riding on top of a bill (a hornbill's casque) as one more horn: its centreline along the chain's
    underside (inside the upper mandible), flat underneath, its dome the chain's height, colours as the chain's"""
    txt, d = load(sp)
    C0 = sorted([s for s in d["sculpt"]["shape"] if re.fullmatch(re.escape(pre) + r"\d+", s.get("id", ""))], key=lambda s: int(re.findall(r"\d+", s["id"])[-1]))
    ids = [s["id"] for s in C0]
    def make(o):
        Cs = [o[i] for i in ids]
        C, te = ell_smp(Cs, every)
        P = [add(c.c, c.n, -c.h * 0.9) + [c.w, clampa(1.9 * c.h / c.w)] for c in C]
        P.append(add(C[-1].c, C[-1].t, te) + [0.0, P[-1][4]])
        P = rooted(sp, [P], ids, need=sink_need)[0]
        h = horn_of(r5(P), Cs[0], up=r5(perp_up(nrm(sub(P[1], P[0])))), flat=1, sides=14)
        cs = [c.col for c in C]; body = max(set(cs), key=cs.count)   # (its own colour: a base ring of another lost)
        h["id"] = pre.rstrip("0123456789"); h["color"] = body
        if cs[-1] != body: h["tip"] = cs[-1]; h["tipAt"] = 0.8
        return [h]
    replace(sp, ids, make)

def roundend(P, f=0.5):
    """a horn's end ROUNDED (a duck's bill, a spoonbill's spoon) instead of a point drawn out: the full width carried on
    to within f x its radius of where the point was, a ring, then the end -- so the bill keeps its length"""
    a = P[-2]; e = P[-1]; d = nrm(sub(e[:3], a[:3])); L = ln(sub(e[:3], a[:3])); rr = a[3] * f
    if L > rr * 1.5:   # (the last full section moved up toward the end)
        q = add(e[:3], d, -rr); a = q + [a[3]] + a[4:]
        return P[:-1] + [a, add(q, d, rr * 0.6) + [a[3] * 0.75] + a[4:], add(q, d, rr) + [0.0] + a[4:]]
    return P[:-1] + [add(a, d, rr * 0.6) + [a[3] * 0.75] + a[4:], add(a, d, rr) + [0.0] + a[4:]]

def ell_at(s, f, hk=1.0, wk=1.0):
    """a sample on an ell's long axis, f (-1..1) of the way from its middle to its end"""
    th = math.radians((s.get("rot") or [0, 0, 0])[2]); t = [math.cos(th), math.sin(th), 0]
    k = (1 - min(0.95, abs(f)) ** 2) ** .5
    return Smp(add(s["c"], t, s["r"][0] * f), t, s["r"][1] * k * hk, s["r"][2] * k * wk, s.get("color"))

def flatbill(sp, upper, lower, nail=None):
    """a DUCK's / SWAN's bill from its ells (upper: the upper's in order, root to tip; lower: the lower's): broad and
    flat (aspect < 1), its end ROUNDED, not pointed; the nail at its tip a small rounded shell of its own"""
    ids = list(upper) + [lower] + ([nail] if nail else [])
    def make(o):
        U = []
        for k, i in enumerate(upper):
            fs = ((-0.6,) if k == 0 else ()) + ((0.0, 0.55) if k == len(upper) - 1 else (0.0,))
            U += [ell_at(o[i], f) for f in fs]
        L = [ell_at(o[lower], f) for f in (-0.6, 0.0, 0.55)]
        tu = o[upper[-1]]["r"][0] * 0.45; tl = o[lower]["r"][0] * 0.45
        up, lo = mandibles(U, tu, L, tl)
        up, lo = roundend(up), roundend(lo)
        hu, hl = bill_horns(sp, o[upper[0]], o[lower], up, lo, ids)
        hu["id"] = upper[0]; hl["id"] = lower
        out = [hu, hl]
        if nail:
            s = o[nail]; a, b = ell_at(s, -0.9), ell_at(s, 0.6)
            P = [a.c + [s["r"][2] * 0.6, 0.6], b.c + [s["r"][2] * 0.9, 0.6], add(b.c, b.t, s["r"][0] * 0.35) + [0.0, 0.6]]
            P = roundend(P[:2] + [add(b.c, b.t, s["r"][0] * 0.4) + [0.0, 0.6]], 0.45)
            out.append(horn_of(r5(P), s, up=r5(a.n), flat=0.8, sides=12))
        return out
    replace(sp, ids, make)

def chain1(sp, pre, split=0.1, lfrac=0.97, every=3, tipcol=None, rnd=False, reverse=False, two=True):
    """ONE chain of ells drawing a whole bill (a spoonbill's) -- or, two=False, a single horn on the chain's own
    centreline (a swordfish's sword: the chain from its tip, reverse=True)"""
    txt, d = load(sp)
    C0 = sorted([s for s in d["sculpt"]["shape"] if re.fullmatch(re.escape(pre) + r"\d+", s.get("id", ""))], key=lambda s: int(re.findall(r"\d+", s["id"])[-1]))
    if reverse: C0 = C0[::-1]
    ids = [s["id"] for s in C0] + ([tipcol[0]] if tipcol else [])
    def make(o):
        Cs = [o[s["id"]] for s in C0]
        S, te = ell_smp(Cs, every)
        if reverse:   # (its tangents from the chain, root to tip)
            for k in range(len(S)):
                a, b = S[max(0, k - 1)], S[min(len(S) - 1, k + 1)]
                S[k].t = nrm([b.c[0] - a.c[0], b.c[1] - a.c[1], 0]); S[k].n = [-S[k].t[1], S[k].t[0], 0]
        if two:
            up, lo = single(S, te, split, lfrac)
            if rnd: up = roundend(up)
            src = Cs[0]; srcl = dict(src); srcl["id"] = "lowerBill"
            uk = {"tip": o[tipcol[0]]["color"], "tipAt": tipcol[1]} if tipcol else None
            hu, hl = bill_horns(sp, src, srcl, up, lo, ids, uk=uk, lk=uk)
            hu["id"] = pre; hl["id"] = "lowerBill"
            return [hu, hl]
        P = [s.c + [s.w, clampa(s.h / s.w)] for s in S] + [add(S[-1].c, S[-1].t, te) + [0.0, clampa(S[-1].h / S[-1].w)]]
        P = rooted(sp, [P], ids)[0]
        h = horn_of(r5(P), Cs[0], up=[0, 1, 0], sides=14); h["id"] = pre
        return [h]
    replace(sp, ids, make)

PAIRS = ["blackbird", "cassowary", "chicken", "dove", "goose", "gull", "hoopoe", "ibis", "magpie", "ostrich", "pelican",
         "penguin", "pheasant", "pigeon", "robin", "rooster", "sparrow", "stork", "swallow", "tawny-owl", "turkey"]
SPEC = {("birds/" + b): (lambda b=b: pair("birds/" + b)) for b in PAIRS}
SPEC.update({
    "birds/vulture": lambda: pair("birds/vulture", tipcol=("billTip", 0.72)),
    "birds/eagle": lambda: pair("birds/eagle", "upper", "lower"),
    "birds/buzzard": lambda: pair("birds/buzzard", "upper", "lower"),
    "birds/falcon": lambda: pair("birds/falcon", "upper", "lower"),
    "birds/parrot": lambda: pair("birds/parrot", "upper", "lower"),
    "monsters/griffin": lambda: pair("monsters/griffin", "eupper", "elower", tipcol=("eBeakTip", 0.7)),
    "birds/crow": lambda: chain("birds/crow", "upperBill", "lowerBill"),
    "birds/raven": lambda: chain("birds/raven", "upperBill", "lowerBill"),
    "birds/kingfisher": lambda: chain("birds/kingfisher", "upperBill", "lowerBill"),
    "birds/puffin": lambda: chain("birds/puffin", "upperBill", "lowerBill"),
    "birds/woodpecker": lambda: chain("birds/woodpecker", "upperBill", "lowerBill"),
    "birds/toucan": lambda: (chain("birds/toucan", "upperBill", "lowerBill"), chain("birds/toucan", "upperBill", "lowerBill", suffix="T")),
    "birds/hornbill": lambda: (chain("birds/hornbill", "upper", "lower", every=4), ridge("birds/hornbill", "casqueM")),
    "birds/cockatoo": lambda: chain("birds/cockatoo", "upperBill", "lowerBill", every=1, extra_lower=["lowerBill"]),
    "birds/cockatiel": lambda: chain("birds/cockatiel", "upperBill", "lowerBill", every=1, extra_lower=["lowerBill"]),
    "birds/heron": lambda: one_r("birds/heron", ["bill"], extra=["jaw"], split=0.15, lfrac=0.97),
    "birds/flamingo": lambda: one_r("birds/flamingo", ["billA", "billB"], extra=["jaw"], split=-0.1, lfrac=0.9, tip=("@black", 0.62)),
    "birds/owl": lambda: one_r("birds/owl", ["beak"], split=0.25, lfrac=0.45),
    "birds/peacock": lambda: one_r("birds/peacock", ["beak"], split=0.2, lfrac=0.8),
    "birds/duck": lambda: flatbill("birds/duck", ["bill", "billTip"], "lowerBill", "nail"),
    "birds/swan": lambda: flatbill("birds/swan", ["bill"], "lowerBill", "nail"),
    "birds/spoonbill": lambda: chain1("birds/spoonbill", "bill", split=0.1, lfrac=0.97, every=3, tipcol=("billTipP", 0.8), rnd=True),
    # (a reptile's / dinosaur's horny beak drawn as one cone: a pointed horn, convex on top -- the cone's blunt end
    # carried on to a point; the turtle's hook on its blob beak (which stays in the field) likewise)
    "others/turtle": lambda: claws_run("others/turtle", [(r"hook", dict(bend=0.12, ext=1.2, aspect=1.0, rk=1.0, need=0.4))]),
    "dinosaurs/pachycephalosaurus": lambda: claws_run("dinosaurs/pachycephalosaurus", [(r"beak", dict(bend=0.06, ext=0.8, aspect=1.0, rk=1.0, need=0.4))]),
    "dinosaurs/stegosaurus": lambda: claws_run("dinosaurs/stegosaurus", [(r"beak", dict(bend=0.06, ext=0.8, aspect=1.0, rk=1.0, need=0.4))]),
    "sea/swordfish": lambda: chain1("sea/swordfish", "bill", every=1, reverse=True, two=False),
})

if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["all"]: args = list(SPEC)
    for a in args:
        sp = a if "/" in a else next(k for k in SPEC if k.endswith("/" + a))
        SPEC[sp]()
