# nbwing.py -- nb.py's folded wing, feather by feather, and the rig that spreads it aloft (2026-11-05, round 8)
#
# AT REST, six tracts from the bend S back to the primaries' tips T, each a row of real vanes laid on the flank and
#   stacked outward in this order: the primaries (a narrow pointed bundle reaching past the tertials toward the tail),
#   the secondaries (their lower edges showing as long strips), the tertials (long, over the secondaries at the back),
#   the greater coverts (a band of long overlapping strips across the middle), the primary coverts (at the bend) and
#   the lesser coverts (small, at the front). Under them, on the skin, FILLS of broad hidden secondaries and primaries.
# ALOFT, every row of every tract rides two bones of its own on wingL (which beats at the shoulder): a turn about x
#   that lays the feather flat (its top facing up) and lifts it level with the spread wing, and a turn about y that
#   aims it (straight back along the arm, fanned out on the hand). Each turn is about a pivot worked out so that the
#   row's root lands where the spread wing wants it: the arm from the shoulder out to the wrist (`armK` fold lengths,
#   the wrist `fwd` forward), the hand beyond it fanning the primaries from th[0] to th[1] degrees off straight back.
#   Feathers between two rows blend their bones, so a tract spreads across the span as its rows do.
from bg import *
import math

WING = dict(armK=1.0, fwd=.12, dih=.05, th=(22, 72), pointed=False, tert=.44, prim=.055, hand=.35, rounded=False)
COUNT = {"small": dict(prim=3, sec=2, tert=2, gcov=3, pcov=1, cov=2, fill=5, pfill=2),
         "med": dict(prim=4, sec=3, tert=2, gcov=4, pcov=2, cov=3, fill=6, pfill=3),
         "big": dict(prim=5, sec=4, tert=3, gcov=4, pcov=2, cov=3, fill=7, pfill=3)}

def _rx(v, a):
    c, s = math.cos(a), math.sin(a); return [v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c]
def _ry(v, b):
    c, s = math.cos(b), math.sin(b); return [v[0] * c + v[2] * s, v[1], -v[0] * s + v[2] * c]
def _rz(v, g):
    c, s = math.cos(g), math.sin(g); return [v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2]]
def _level(d, droop):
    """the turn about z that brings d's slope to -droop: x' sin g + y' cos g = -sin(droop) |d_xy|"""
    h = math.hypot(d[0], d[1]); ph = math.atan2(d[1], d[0])   # (its angle in the xy plane)
    tgt = math.pi + droop if d[0] < 0 else -droop               # (pointing back: level is pi, drooping a little below: pi + droop)
    g = tgt - ph
    return math.atan2(math.sin(g), math.cos(g))
def _solve2(R, t):   # (I - R) c = t, 2x2
    a, b, c_, d = 1 - R[0][0], -R[0][1], -R[1][0], 1 - R[1][1]; det = a * d - b * c_
    return [(d * t[0] - b * t[1]) / det, (-c_ * t[0] + a * t[1]) / det]

def darker(hx, f=.78):
    r, g, b = int(hx[1:3], 16), int(hx[3:5], 16), int(hx[5:7], 16)
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v * f))) for v in (r, g, b))

def _expand(rows, n):
    """the three spec rows as n, one per feather -- each feather then rides one row's bones whole (two rows' bones
       blended across a big turn squash the feathers between them)"""
    if n <= 1: return [rows[0]]
    out = []
    for j in range(n):
        x = j / (n - 1) * (len(rows) - 1); i = min(len(rows) - 2, int(x)); t = x - i; A, B = rows[i], rows[i + 1]
        lerp = lambda a, b: [round(u + (v - u) * t, 4) for u, v in zip(a, b)]
        out.append(row(lerp(A["at"], B["at"]), lerp(A["to"], B["to"]), round(A["w"] + (B["w"] - A["w"]) * t, 4)))
    return out

FOLDN = {"small": dict(prim=3, sec=2, tert=1, gcov=2, pcov=1, cov=2),
         "med": dict(prim=3, sec=2, tert=2, gcov=2, pcov=1, cov=2),
         "big": dict(prim=3, sec=3, tert=2, gcov=2, pcov=1, cov=2)}
SPREAD = dict(span=1.5, armF=.4, asp=2.4, kink=.12, hsweep=.3, tipC=.5, fingered=False, dih=5, pinch=.5, secMax=None)
SPREADN = {"small": dict(cov=2, gcov=2, prim=4, pcov=1),
           "med": dict(cov=2, gcov=2, prim=5, pcov=1),
           "big": dict(cov=2, gcov=3, prim=6, pcov=1)}

def _depth(sh, pts, floor=-1e9):
    """the shallowest of the points under the surface (> 0: all inside), the body taken as mirrored -- given up as soon
       as it is no better than `floor`"""
    m = 1e9
    for q in sorted(pts, key=lambda q: -abs(q[0]) - abs(q[2]))[:1] + pts:
        m = min(m, -field(sh, [q[0], q[1], abs(q[2])]))
        if m <= floor: return m
    return m

def _blade(at, to, w, up=(0, 1, 0)):
    """sample points over a blade: along its shaft and out to both vanes"""
    dr = sub(to, at); side = nrm([dr[1] * up[2] - dr[2] * up[1], dr[2] * up[0] - dr[0] * up[2], dr[0] * up[1] - dr[1] * up[0]])
    out = []
    for s_, k_ in ((.02, .35), (.25, 1), (.5, 1), (.75, .9), (.97, .2)):
        m = add(at, dr, s_); ww = w * k_
        out += [m, add(m, side, ww), add(m, side, -ww)]
    return out

def _lay(sh, fe, up, m):
    """a blade settled by its ends alone sinks in the middle on a round flank (the chord runs inside): each row lifted
       whole along `up` until its shaft clears the surface all along -- the feather then LIES on the wing, flat"""
    for r in fe["rows"]:
        for _ in range(300):
            dr = sub(r["to"], r["at"])
            if min(field(sh, add(r["at"], dr, s_)) for s_ in (.2, .4, .6, .8)) >= m: break
            r["at"] = add(r["at"], up, .0005); r["to"] = add(r["to"], up, .0005)
    return fe

def bands(fe, spec, dl, under=False):
    """BANDS across a feather group, as geometry: copies of it cut short at f of their length (the roots kept), each
       one colour, stacked on it (lifted dl a layer -- the shortest on top), so that from the tip back the colours run
       group, spec[0], spec[1] ... -- a white bar across black, which a shader that only darkens cannot paint; `under`:
       the same stack again beneath it, for the view from below"""
    import json
    out = []
    for sd in ((1, -1) if under else (1,)):
        for bi, (f, col) in enumerate(spec):
            b = json.loads(json.dumps(fe))
            b["id"] = fe["id"] + ("B" if sd > 0 else "U") + str(bi)
            for r in b["rows"]:
                r["to"] = [round(a + (t - a) * f, 4) for a, t in zip(r["at"], r["to"])]; r["w"] = round(r["w"] * .97, 4)
            b["curve"] = round(fe.get("curve", 0) * f, 4)
            b["lift"] = round(fe.get("lift", 0) + sd * dl * (bi + 1), 5)
            b["color"] = b["tip"] = col; b.pop("bars", None); b.pop("ocellus", None)
            out.append(b)
    return out

def wing(d, sh, P, S, T, H, u, c):
    """the folded wing on the flank (seen standing; turned away inside the body aloft) and, apart from it, the SPREAD wing
       (hidden inside the body standing, each feather swung out aloft on a bone of its own)"""
    W = dict(WING); W.update(P.get("wing", {}))
    size = "small" if u < .2 else "med" if u < .5 else "big"
    N = dict(FOLDN[size]); N.update(W.get("n", {}))
    Lf = S[0] - T[0]; sl = (T[1] - S[1]) / Lf
    up = nrm(list(P["fold"]["up"]))
    sc_ = min(1, u / .5); base, step = .003 * sc_, .0022 * sc_
    FD = P["fold"]; stg = .0012 * sc_
    if FD.get("tight"): base, step, stg = .0011 * sc_, .0007 * sc_, .0004 * sc_   # (the tracts laid close: no air under the upper ones)
    def at(a, b): return [S[0] - a * Lf, S[1] + sl * a * Lf - b * H * (1 - .35 * a), S[2]]
    def dirv(dn): return nrm([-1, sl - dn, 0])
    axu, pn = [-1, sl], [0, -1]
    if FD.get("upright"):   # (an upright bird's: the fold laid along its own line from the bend to the tip -- not along x --
        #  its depth square to that line, its feathers as long as the line is: an owl's, a woodpecker's)
        Lt = math.hypot(T[0] - S[0], T[1] - S[1]); axu = [(T[0] - S[0]) / Lt, (T[1] - S[1]) / Lt]; pn = [-axu[1], axu[0]]
        def at(a, b): return [S[0] + axu[0] * a * Lt + pn[0] * b * H * (1 - .35 * a), S[1] + axu[1] * a * Lt + pn[1] * b * H * (1 - .35 * a), S[2]]
        def dirv(dn): return nrm([axu[0] + pn[0] * dn, axu[1] + pn[1] * dn, 0])
        Lf = Lt
    oa = "flight" if W["pointed"] else "round"
    for k in ("cov", "gcov", "sec", "prim", "tert"):
        if k == "tert" and "tert" not in c: c["tert"] = c.get("sec"); c["tertTip"] = c.get("secTip", c["sec"])
        if c.get(k + "Tip", c[k]) == c[k] and c[k].startswith("#"): c[k + "Tip"] = darker(c[k])
    tl = W["tert"]
    spec = [
        ("prim", (.26, .23, .2), (.36, .5, .64), None, None, W["prim"], "flight", "@prim", "@primTip", 0),
        ("sec", (.3, .33, .36), (.22, .5, .78), (.06, .08, .1), (.5, .48, .45), .085, "round", "@sec", "@secTip", 1),
        ("tert", (.4, .44, .48), (.02, .16, .3), (.04, .06, .08), (tl, tl, tl * .95), .07, oa, "@tert", "@tertTip", 2),
        ("gcov", (.15, .18, .21), (.06, .38, .7), (.1, .12, .14), (.3, .3, .28), .05, "round" if W["rounded"] else oa, "@gcov", "@gcovTip", 3),
        ("pcov", (.08, .1, .12), (.55, .68, .8), (.12, .14, .16), (.18, .18, .17), .04, "round", "@pcov" if "pcov" in c else "@cov", "@pcovTip" if "pcov" in c else "@covTip", 4),   # (pcov: the primary coverts' own colour -- a stork's black over the white arm)
        ("cov", (0, .03, .06), (.04, .26, .48), (.12, .14, .16), (.2, .2, .18), .045, "round", "@cov", "@covTip", 5),
    ]
    fold = []
    for id, A_, B_, dn, ln, w, outl, col, tip, j in spec:
        if not N.get(id) or P.get("flipper"): continue
        rows = []
        for i in range(3):
            r0 = at(A_[i], B_[i])
            if dn is None and FD.get("upright"): to = [T[0] + axu[0] * .02 * Lf * (i - 1) - pn[0] * .08 * H * (1 - i), T[1] + axu[1] * .02 * Lf * (i - 1) - pn[1] * .08 * H * (1 - i), T[2]]
            elif dn is None: to = [T[0] - .02 * Lf * (i - 1), T[1] + .08 * H * (1 - i), T[2]]
            else: to = add(r0, dirv(dn[i]), ln[i] * Lf)
            rows.append(row(r0, to, round(w * Lf * FD.get("fw", 1), 4)))
        fe = fea(id, rows, N[id], col, tip, outline=outl, up=list(up), camber=.14, curve=-.02, stagger=round(stg, 5), mirror=True, seed=31 + j)
        if id == "prim" and W.get("pbars"): fe["bars"] = W["pbars"]
        if id in ("sec", "tert") and W.get("sbars"): fe["bars"] = W["sbars"]
        settle(sh, fe, up, base + step * j)
        if FD.get("lay"): _lay(sh, fe, up, base + step * j)
        fold.append(fe)
    if P.get("flightless"): return _ground_wing(d, sh, P, S, T, H, u, fold, Lf)
    return aloft(d, sh, P, S, u, c, fold, W, size, up, step, Lf)

def aloft(d, sh, P, S, u, c, fold, W, size, up, step, Lf, tk=None, fold_bands=True, add_fold=True, look_over=None, drop=0):
    """ALOFT: the folded tracts `fold` (laid on the flank along `up`, the bend at S) each turned half round into the body on a
       bone of its own, and the SPREAD wing (P["spread"], P["flight"]["speed"]) built hidden in the body and swung out
       feather by feather on bones on wingL. wing() above calls it for its own fold; a bird with a fold of its own making
       (duck.py, swan.py: bg.fold_wing) calls it directly -- `tk` the body's main ellipsoid when it is not called "trunk",
       `fold_bands` off to keep W["bands"] off its fold, `add_fold` off when the fold is already in sh, `look_over`
       {tract: (colour, tip)} the spread tracts' colours in its own palette's names, `drop` (m) the turned fold let down that
       much further aloft (a pure translation, +-90 about x: a fold laid high over the back -- the swan's -- clears the
       back's top only lower down)"""
    sc_ = min(1, u / .5)
    # ---- aloft the fold turns half round about the vertical, into the body (one bone a tract, on the body) ----
    tk = tk or next(q for q in sh if q["id"] == "trunk"); tc, trr = tk["c"], tk["r"]
    body = next(p for p in d["parts"] if p["id"] == "body"); bp = body["pos"]
    hide = []
    for fe in fold:
        pts = []
        for r in fe["rows"]: pts += _blade(r["at"], r["to"], r["w"], up)
        pc = [sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts)]
        best = None
        for gd in (0, 20, 40, -20, -40, 60, -60):
            g_ = math.radians(gd); cg, sg_ = math.cos(g_), math.sin(g_)
            pp = [[pc[0] + (q[0] - pc[0]) * cg - (q[1] - pc[1]) * sg_, pc[1] + (q[0] - pc[0]) * sg_ + (q[1] - pc[1]) * cg, q[2]] for q in pts]
            for ix in range(17):
                qx = tc[0] + trr[0] * (-.8 + .1 * ix)
                for iz in range(10):
                    qz = S[2] * iz / 12
                    dp = _depth(sh, [[2 * qx - q[0], q[1] - drop, 2 * qz - q[2]] for q in pp], best[0] if best else -1e9)
                    if best is None or dp > best[0]: best = (dp, qx, qz, gd, pc)
        hide.append((fe, best))
        if best[0] < 0 and __import__("os").environ.get("NBDBG"): print("    fold out:", fe["id"], round(best[0], 4), best[3])
        fe["bone"] = "wf%szL" % fe["id"]
    BW = W.get("bands") or {}
    if fold_bands: fold += [b for fe in fold for b in bands(fe, BW.get(fe["id"], []), .3 * step)]
    # ---- the SPREAD wing, flat at yw (its dihedral is wingL's turn aloft) ----
    G = dict(SPREAD); G.update(P.get("spread", {}))
    NS = dict(SPREADN[size]); NS.update(G.get("n", {}))
    yw = round(min(S[1], tc[1] + .3 * trr[1]), 4)
    zs = S[2]   # (the flank at the shoulder)
    for _ in range(60):
        if field(sh, [S[0], yw, zs]) >= 0: break
        zs += .002 * u
    z0 = .8 * zs; zT = G["span"] * u / 2; b = zT - z0; zW = z0 + G["armF"] * b
    c0 = b / G["asp"]; hs = G["hsweep"] * (zT - zW)
    LE0 = S[0] + .05 * c0
    def LE(z): return LE0 + G["kink"] * c0 * min(1, (z - z0) / (zW - z0)) - (hs * (z - zW) / (zT - zW) if z > zW else 0)
    def C(z): return c0 * (1 - .12 * min(1, (z - z0) / (zW - z0))) * (1 - (1 - G["tipC"]) * max(0, (z - zW) / (zT - zW)) ** G["pinch"])
    hL = max(.0009, .0016 * sc_)   # (a layer)
    feathers = []   # (tract, aloft root, aim (deg off straight back, + out), length, half-width, outline)
    def tract(id, zs_, f_root, f_len, aim, wmul, outl, lay):
        n = len(zs_)
        for i, z in enumerate(zs_):
            dz = (zs_[1] - zs_[0]) if n > 1 else .1 * b
            feathers.append((id, [LE(z) - f_root * C(z), yw + lay, z], aim(i / max(1, n - 1)), f_len * C(z), dz * wmul, outl))
    lin = lambda a_, b_, n: [a_ + (b_ - a_) * i / max(1, n - 1) for i in range(n)]
    # secondaries: straight back along the arm, round, each overlapping the next by half -- as many as keep them
    #  twice as long as they are wide (to secMax)
    Ls = .74 * C((z0 + zW) / 2); nsec = max(4, min(G.get("secMax") or {"small": 5, "med": 7, "big": 8}[size], int(math.ceil((zW - z0) / (.5 * Ls * .55))) + 1))
    nsec = NS.get("sec", nsec)
    tract("sec", lin(z0 + .02 * b, zW + .02 * b, nsec), .3, .74, lambda f: 2 + 8 * f, 1 / (1.9 * .55), "round", hL)
    # the coverts: two smooth bands laid along the arm -- the lesser at the leading edge, the greater over the
    #  secondaries' roots
    def band(id, nb_, za, zb_, x0f, wf, lay, ang=86):
        nb_ = max(nb_, int(math.ceil(1.7 * (zb_ - za) / (1.9 * trr[0]))))   # (each short enough to lie hidden in the body)
        Lb = (zb_ - za) / nb_ * 1.7
        for i in range(nb_):
            z = za + (zb_ - za - Lb) * i / max(1, nb_ - 1)
            feathers.append((id, [LE(max(z, z0)) - x0f * C(max(z, z0)), yw + lay, z], ang, Lb, wf * c0, "round"))
    band("cov", NS["cov"], z0 - .04 * b, zW + .03 * b, .16, .14, 3 * hL)
    band("gcov", NS["gcov"], z0 - .04 * b, zW, .3, .13, 2 * hL, 87)
    # the primaries: from the hand's rear half, fanned to the outline of the hand and its tip
    npr = NS["prim"]; xt = lambda z: LE(z) - C(z)
    tipP = [LE(zT) - .45 * C(zT), zT]
    for i in range(npr):
        f = i / max(1, npr - 1)
        zr = zW - .02 * b + (zT - zW) * .5 * f
        root = [LE(zr) - .4 * C(zr), zr]
        zt = zW + (zT - zW) * (.28 + .72 * f)
        k_ = f ** 3
        tip = [xt(zt) * (1 - k_) + tipP[0] * k_, zt * (1 - k_) + tipP[1] * k_]
        if i == npr - 1: tip = tipP
        dx, dz = tip[0] - root[0], tip[1] - root[1]; ln = math.hypot(dx, dz)
        feathers.append(("prim", [root[0], yw, root[1]], math.degrees(math.atan2(dz, -dx)), ln, None, "flight"))
    # (their widths: each overlapping the next by half at the tips; fingered: the outer ones apart in their outer third)
    pr = [q for q in feathers if q[0] == "prim"]
    for i, q in enumerate(pr):
        def tipof(q_): return [q_[1][0] - math.cos(math.radians(q_[2])) * q_[3], q_[1][2] + math.sin(math.radians(q_[2])) * q_[3]]
        nb_ = [pr[j] for j in (i - 1, i + 1) if 0 <= j < len(pr)]
        dt = sum(math.dist(tipof(q), tipof(o)) for o in nb_) / len(nb_)
        f = i / max(1, len(pr) - 1)
        w = dt / (1.42 * .55)
        if G["fingered"] and f > .45: w = dt * .5
        feathers[feathers.index(q)] = q[:4] + (round(min(w, .3 * q[3]), 4),) + q[5:]
    # primary coverts: a band along the hand's leading edge
    ang = 90 - math.degrees(math.atan2(hs, zT - zW))   # (along the hand's swept-back leading edge)
    band("pcov", NS["pcov"], zW - .02 * b, zW + .55 * (zT - zW), .16, .13, 3 * hL, ang)
    # STRIPS: bars of a colour of their own laid across the spread wing (a band like the coverts', at x of the chord
    #  behind the leading edge, w its half-width): along the arm, or (hand) the hand's swept edge out to `to` of it
    SL = {}
    for i_, st in enumerate(G.get("strips", [])):
        idb = "bar%d" % i_
        if st.get("hand"): band(idb, st.get("n", 2), zW - .02 * b, zW + st.get("to", .7) * (zT - zW), st["x"], st["w"], st.get("lay", 1.5) * hL, ang)
        else: band(idb, st.get("n", 2), z0 - .02 * b, zW + .02 * b, st["x"], st["w"], st.get("lay", 1.5) * hL)
        SL[idb] = (st["col"], st["col"], 6 + i_)
    # ---- each spread feather hidden standing: on edge inside the body along its length (in the vertical plane
    #      through the middle), two turns carrying it out aloft -- a quarter roll about x that lays it flat, then the turn
    #      about the vertical that aims it -- each about the pivot that puts it where the spread wing wants it ----
    tt = math.radians(tk.get("rot", [0, 0, 0])[2]); al = math.pi / 2
    UPr = [0, 0, -1]   # (its top, standing: rolled a quarter about x it faces up)
    spreadB = []; groups = {}
    for k, (id, ra, aim, ln, w, outl) in enumerate(feathers):
        best = None
        for ph in (math.pi + tt, tt, tt + .35, tt + .6, tt + .85):
            dr = [math.cos(ph), math.sin(ph), 0]
            for ix in range(13):
                for iy in range(7):
                    cx = tc[0] + trr[0] * (-.3 + .1 * ix); cy = tc[1] + trr[1] * (-.3 + .15 * iy)
                    r0 = [cx - dr[0] * ln / 2, cy - dr[1] * ln / 2, 0]; r1 = add(r0, dr, ln)
                    d1 = _rx(dr, al); th1 = math.degrees(math.atan2(d1[2], -d1[0]))   # (rolled flat: its aim)
                    be = (aim - th1 + 180) % 360 - 180
                    pen = 1 if abs(be) < 40 else 0
                    dp = _depth(sh, _blade(r0, r1, w, UPr), (best[0] + pen) if best else -1e9) - pen
                    if best is None or dp > best[0]: best = (dp, r0, r1, be)
        dp, r0, r1, be = best
        if dp < 0 and __import__("os").environ.get("NBDBG"): print("    out:", id, k, round(dp, 4), "len", round(ln, 3), "w", round(w, 4))
        # the roll about x through c: r0 -> (r0.x, ra.y, 0)
        Rx = [[math.cos(al), -math.sin(al)], [math.sin(al), math.cos(al)]]
        rp = _rx(r0, al); cyz = _solve2(Rx, [ra[1] - rp[1], 0 - rp[2]])
        pr = [r0[0], ra[1], 0]
        bq = math.radians(be); R2 = [[math.cos(bq), math.sin(bq)], [-math.sin(bq), math.cos(bq)]]
        ry_ = _ry(pr, bq); qxz = _solve2(R2, [ra[0] - ry_[0], ra[2] - ry_[2]])
        bn = "ws%s%d" % (id, k)
        spreadB.append((bn, [qxz[0], ra[1], qxz[1]], be, [r0[0], cyz[0], cyz[1]], dp))
        groups.setdefault(id, []).append(row([round(v, 4) for v in r0], [round(v, 4) for v in r1], round(w, 4), bone=bn + "xL", up=UPr))
    look = {"sec": ("@sec", "@secTip", 1), "gcov": ("@gcov", "@gcovTip", 2), "cov": ("@cov", "@covTip", 3),
            "prim": ("@prim", "@primTip", 0), "pcov": ("@pcov", "@pcovTip", 3) if "pcov" in c else ("@cov", "@covTip", 3)}
    look.update(SL)
    for k_, v_ in (look_over or {}).items(): look[k_] = (v_[0], v_[1], look[k_][2])
    for id, rows in groups.items():
        col, tip, j = look[id]
        outl = next(q[5] for q in feathers if q[0] == id)
        sh.append(fea("sp" + id, rows, len(rows), col, tip, outline=outl, up=UPr, camber=0, curve=0,
                      stagger=round(.0007 * sc_, 5), mirror=True, seed=51 + j, **({"bars": W["pbars"]} if id == "prim" and W.get("pbars") else {"bars": W["sbars"]} if id == "sec" and W.get("sbars") else {})))
        sh += bands(sh[-1], BW.get(id, []), .3 * hL, under=W.get("bandsUnder", False))
    if add_fold: sh += fold
    # ---- the parts: wingL at the shoulder (the beat, the dihedral aloft), a bone per spread feather on it, a bone per
    #      folded tract on the body ----
    wpos = [S[0], yw, z0]
    out = []
    for p in d["parts"]:
        out.append(p)
        if p["id"] in ("wingL", "wingR"):
            s = p["id"][-1]; sg = 1 if s == "L" else -1
            p["pos"] = [round(wpos[0] - bp[0], 4), round(wpos[1] - bp[1], 4), round(wpos[2] * sg, 4)]
            p.pop("pivot", None); p.pop("rot", None)
            p["anim"] = {"axis": "x", "deg": .5 * sg, "speed": P["flight"]["speed"], "phase": 0, "wing": True}
            p["fold"] = [0, 0, 0]; p["flyRot"] = [round(-G["dih"] * sg, 2), 0, 0]
            for bn, q, be, cc, dp in spreadB:
                rel = lambda a_, b_: [round(a_[0] - b_[0], 4), round(a_[1] - b_[1], 4), round((a_[2] - b_[2]) * sg, 4)]
                out.append({"id": bn + "y" + s, "parent": p["id"], "shape": "sphere", "size": {"r": .004}, "color": "@cov",
                            "pos": rel(q, wpos), "flyRot": [0, round(be * sg, 2), 0], "fold": [0, 0, 0]})
                out.append({"id": bn + "x" + s, "parent": bn + "y" + s, "shape": "sphere", "size": {"r": .004}, "color": "@cov",
                            "pos": rel(cc, q), "flyRot": [round(math.degrees(al) * sg, 2), 0, 0], "fold": [0, 0, 0]})
            for fe, (dp, qx, qz, gd, pc) in hide:
                yb = fe["bone"][:-2] + "y" + s
                ybp = [round(qx - bp[0], 4), round(pc[1] - bp[1], 4), round(qz * sg, 4)]; ybpar = "body"
                if drop:   # (Rx(90) about A, then Rx(-90) about B = A + (0, h, h): every point let down 2h)
                    h_ = round(drop / 2, 4)
                    out.append({"id": yb[:-1] + "dA" + s, "parent": "body", "shape": "sphere", "size": {"r": .004}, "color": "@cov",
                                "pos": ybp, "flyRot": [90 * sg, 0, 0], "fold": [0, 0, 0]})
                    out.append({"id": yb[:-1] + "dB" + s, "parent": yb[:-1] + "dA" + s, "shape": "sphere", "size": {"r": .004}, "color": "@cov",
                                "pos": [0, h_, h_ * sg], "flyRot": [-90 * sg, 0, 0], "fold": [0, 0, 0]})
                    ybp, ybpar = [0, -h_, -h_ * sg], yb[:-1] + "dB" + s
                out.append({"id": yb, "parent": ybpar, "shape": "sphere", "size": {"r": .004}, "color": "@cov",
                            "pos": ybp, "flyRot": [0, 180 * sg, 0], "fold": [0, 0, 0]})
                out.append({"id": fe["bone"][:-1] + s, "parent": yb, "shape": "sphere", "size": {"r": .004}, "color": "@cov",
                            "pos": [round(pc[0] - qx, 4), 0, round(-qz * sg, 4)], "flyRot": [0, 0, gd], "fold": [0, 0, 0]})
    d["parts"] = out
    return {"span": round(2 * zT, 3), "Lf": round(Lf, 4), "hideFold": round(min([h[1][0] for h in hide] or [0]), 4),
            "hideSpread": round(min(q[4] for q in spreadB), 4)}

def _ground_wing(d, sh, P, S, T, H, u, fold, Lf):
    """a flightless bird's wing: the fold alone (an ostrich's plumes) or a penguin's FLIPPER -- a stiff flat paddle hanging down the
       flank, dark outside, white edged and white beneath -- on wingL, flapping a little with the walk"""
    sh += fold
    fl = P.get("flipper")
    if fl:   # (two flat blades, apart from the body's surface: the dark outer face, and under it a wider white one that
             #  shows as the pale leading and trailing edges and is the whole underside)
        L_ = fl["len"] * u; W_ = fl["w"] * u; a = math.radians(fl.get("ang", 76))
        r0 = list(S)   # (the root: out from the shoulder to the surface, then a hair inside it)
        for _ in range(600):
            if field(sh, r0) >= 0: break
            r0[2] += .0005 * u
        r0[2] -= .004 * u
        _x = lambda a_, b_: [a_[1] * b_[2] - a_[2] * b_[1], a_[2] * b_[0] - a_[0] * b_[2], a_[0] * b_[1] - a_[1] * b_[0]]
        for o in range(fl.get("out", 6), 45, 2):   # (angled away from the flank until no part of it is in the body)
            ob = math.radians(o); dv = [-math.cos(a) * math.cos(ob), -math.sin(a) * math.cos(ob), math.sin(ob)]
            sd = nrm(sub([1, 0, 0], [x * dv[0] for x in dv]))
            if all(field(sh, add(add(r0, dv, L_ * f), sd, W_ * e * (1 - .45 * f))) >= .006 * u for f in (.25, .45, .65, .85, 1.0) for e in (0, .55, -.55)): break
        up = nrm(_x(sd, dv))   # (points into the body: the blade's side is cross(d, up) = sd)
        tip = add(r0, dv, L_); R4 = lambda v: [round(x, 4) for x in v]
        inn = lambda v, t: R4(add(v, up, t))
        sh.append(fea("flipper", [row(R4(r0), R4(tip), round(W_ / 1.9, 4))], 1, "@flipper", fl.get("tipC", "@flipper"), outline="round", bone="wingL",
                      mirror=True, up=R4([-x for x in up]), camber=0, curve=0, seed=61))
        sh.append(fea("flipperIn", [row(inn(add(r0, dv, -.01 * u), .003 * u), inn(add(tip, dv, -.02 * u), .003 * u), round(W_ * 1.3 / 1.9, 4))], 1, "@flipperIn", "@flipperIn",
                      outline="round", bone="wingL", mirror=True, up=R4([-x for x in up]), camber=0, curve=0, seed=62))
        print("    flipper: out %d deg" % o)
    body = next(p for p in d["parts"] if p["id"] == "body"); bp = body["pos"]
    for p in d["parts"]:
        if p["id"] in ("wingL", "wingR"):
            sg = 1 if p["id"][-1] == "L" else -1
            p["pos"] = [round(S[0] - bp[0], 4), round(S[1] - bp[1], 4), round(S[2] * sg, 4)]
            p.pop("pivot", None); p.pop("rot", None)
            p["anim"] = {"axis": "x", "deg": (fl.get("flap", 8) if fl else 1.5) * sg, "speed": P["walk"]["speed"], "phase": 0 if sg > 0 else 3.14, "amp": True}
            p["fold"] = [0, 0, 0]
    return {"span": 0, "Lf": round(Lf, 4), "hideFold": 0, "hideSpread": 0}

TUCK = {   # (aloft, degrees about z added to the leg, the tarsus and the toes)
    "up": dict(leg=35, tars=-150, foot=70),        # (a songbird's, a crow's: drawn up against the belly)
    "back": dict(leg=-75, tars=-20, foot=-90),     # (a gull's, a pigeon's: laid back under the tail)
    "trail": dict(leg=-86, tars=0, foot=-90),      # (a stork's, a crane's: trailing straight back)
}

def flight(d, P):
    if P.get("flightless"): return   # (never the flight pose: no flags.flight, no flyRot)
    fl = P["flight"]; tk = P.get("tuck", "up"); T_ = TUCK[tk] if isinstance(tk, str) else tk
    for p in d["parts"]:
        pid = p["id"]
        if pid[:-1] in ("leg", "tars", "foot") and pid[-1] in "LR":
            if p.get("anim"): p["anim"]["amp"] = True   # (the legs' swing belongs to the stride: none standing, none aloft)
            p["flyRot"] = [0, 0, T_[pid[:-1]]]
        if fl.get("flyTurn") and pid in fl["flyTurn"]: p["flyRot"] = [0, 0, fl["flyTurn"][pid]]
    f = {"arm": 0, "hand": 0, "beat": fl["beat"], "bob": .03}
    if fl.get("hind"): f["hind"] = fl["hind"]
    if fl.get("neck") is not None: f["neck"] = fl["neck"]
    d.setdefault("flags", {})["flight"] = f

def paint(sh, id, frm, dirn, rt, rz, rn, col, bone="head", k=None, side=False, spin=0, mirror=False, kc=None, decal=False):
    """a flat patch of colour on the surface (no lump): from `frm` along `dirn` to the surface, an ellipsoid thin along the
       surface's normal (rn) and rt x rz across it, sunk so it stands only a hair proud"""
    dirn = nrm(dirn); p = list(frm)
    for _ in range(600):
        if field(sh, p) >= 0: break
        p = add(p, dirn, rn * .1)
    n = nrm(grad(sh, p))
    if decal:   # (a CARVING a hair deep that paints what it opens -- flush, its edge drawn by the field, not a plate's)
        sp_ = math.radians(spin); al = [math.cos(sp_), math.sin(sp_), 0] if side else [-n[1], n[0], 0]
        al = nrm(sub(al, [sum(x * y for x, y in zip(al, n)) * x for x in n])); w = [n[1] * al[2] - n[2] * al[1], n[2] * al[0] - n[0] * al[2], n[0] * al[1] - n[1] * al[0]]
        return {"id": id, "type": "ell", "c": [round(v, 4) for v in add(p, n, rn * .75)], "r": [round(rn, 4), round(rt, 4), round(rz, 4)],
                "axes": [[round(v, 4) for v in q] for q in (n, al, w)], "k": round(rn * .15, 4), "op": "sub", "color": col, "bone": bone, **({"mirror": True} if mirror else {})}
    cc = add(p, n, -rn * .75)
    if side:   # (on a flank or the side of the neck: the patch flat across x and y, `spin` about z)
        return ell(id, [round(v, 4) for v in cc], [round(rt, 4), round(rz, 4), round(rn, 4)], col, k=k if k is not None else rn * .3, kc=kc if kc is not None else rn * .5, bone=bone,
                   rot=[0, 0, spin] if spin else None, mirror=mirror)
    a = math.degrees(math.atan2(n[1], n[0]))
    return ell(id, [round(v, 4) for v in cc], [round(rn, 4), round(rt, 4), round(rz, 4)], col, k=k if k is not None else rn * .3, kc=kc if kc is not None else rn * .5, bone=bone, rot=[spin, 0, round(a, 1)] if spin else [0, 0, round(a, 1)], mirror=mirror)
