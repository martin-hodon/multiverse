from bg import *

def rig_wings(d, bodyY, shoulder, wristZ, deg, handDeg, speed, lag=-.8, dih=0, sweep=28):
    """wingL (the arm, turning at the shoulder), wristL at the wrist (sweeps the hand back on the upstroke: the wing
       closes as it rises) and handL on it (its own beat, a little behind the arm's). fold [0,0,0] on the wrist and hand:
       struck down only the arm folds back (the hand rides it)"""
    parts = [p for p in d["parts"] if not p["id"].startswith(("hand", "wrist"))]
    out = []
    for p in parts:
        out.append(p)
        if p["id"] in ("wingL", "wingR"):
            s = p["id"][-1]; sg = 1 if s == "L" else -1
            p["pos"] = [shoulder[0], shoulder[1] - bodyY, shoulder[2] * sg]
            p.pop("pivot", None)
            p["anim"] = {"axis": "x", "deg": deg * sg, "speed": speed, "phase": 0, "wing": True}
            col = p.get("color", "#808080")
            out.append({"id": "wrist" + s, "parent": p["id"], "shape": "sphere", "size": {"r": .01}, "color": col, "fold": [0, 0, 0],
                        "pos": [0, dih * (wristZ - shoulder[2]), (wristZ - shoulder[2]) * sg],
                        "anim": {"axis": "y", "deg": -sweep * sg, "speed": speed, "phase": -1.571 + lag * .4, "flick": 1, "wing": True}})
            out.append({"id": "hand" + s, "parent": "wrist" + s, "shape": "sphere", "size": {"r": .01}, "color": col, "fold": [0, 0, 0],
                        "pos": [0, 0, 0], "anim": {"axis": "x", "deg": handDeg * sg, "speed": speed, "phase": lag, "wing": True}})
    import sys
    if "--still" in sys.argv:
        for p in out:
            if p.get("anim", {}).get("wing"): p["anim"]["deg"] = 0
    if "--up" in sys.argv:   # (frozen at the top of the upstroke: the wrist flexed)
        for p in out:
            if p.get("anim", {}).get("wing"): p["anim"]["speed"] = 0; p["anim"]["phase"] = {"x": -1.571, "y": 1.571}[p["anim"]["axis"]] if not p["anim"].get("flick") else 1.571
    d["parts"] = out
    # (no `flight`: these are authored aloft, their wings spread and beating -- the flight pose would only re-pose them)
    d.pop("flight", None)

def wing(y0, x0, z0, zW, zT, dih, chord, sec, prim, covs, colors, pcov=None, th=.06, kink=0, hsweep=None, htaper=.6, under=None, ucov=None):
    """a spread wing, the left one (mirrored): the arm from the shoulder (x0, y0, z0) to the wrist zW, the hand to zT;
       y rises dih per metre out (the dihedral). The leading edge runs forward `kink` m from shoulder to wrist (the wrist's
       angle), then back `hsweep` m to the tip; the chord narrows over the hand to htaper of the arm's. A thin slab (th of
       the chord thick, each side) of overlapping pieces from root to tip -- no window at the wrist -- with a fine leading
       edge; secondaries along the arm's trailing edge, rounded and overlapping into one trailing edge (sec["lens"]: five
       lengths root to wrist, the mid-wing bulge); primaries from the hand's rear half, fanned prim["a"] = (inner, outer)
       degrees from straight back (all behind the leading edge); covert tracts over the front half; `under`: the
       underwing lining's colour bands along the slab's underside ([{s, w, color}]: s its middle behind the leading edge,
       w its width, fractions of the chord)"""
    Y = lambda z: y0 + dih * (z - z0)
    A, Hd = "wingL", "handL"
    ry = chord * th
    LE0 = x0 + chord * .48
    hs = -.3 * (zT - zW) * .6 if hsweep is None else -hsweep
    def LE(z):
        if z <= zW: return LE0 + kink * (z - z0) / (zW - z0)
        return LE0 + kink + hs * (z - zW) / (zT - zW)
    def C(z):   # (the chord)
        return chord if z <= zW else chord * (1 - (1 - htaper) * (z - zW) / (zT - zW))
    out = []
    # (the slab: overlapping flat pieces along the span, each a third longer than its share, the hand's on the hand)
    for bone, za, zb, nP, rr, nm in ((A, z0, zW + .012, 4, 1.0, "arm"), (Hd, zW - .012, zT, 3, .8, "hand")):
        for i in range(nP):
            z = za + (zb - za) * (i + .5) / nP; c = C(z)
            out.append(ell(f"{nm}{i}", [LE(z) - c * .31, Y(z), z], [c * .36, ry * rr * (1 - .25 * (z - z0) / (zT - z0)), (zb - za) / nP * .72],
                           colors.get("hand", colors["arm"]) if nm == "hand" else colors["arm"], k=ry * .8, bone=bone, mirror=True))
    for j, u in enumerate(under or []):   # (the underwing lining: bands just inside the slab's underside)
        for i in range(3):
            z = z0 + .02 + (zW - z0 - .02) * (i + .5) / 3; c = C(z)
            out.append(ell(f"{'top' if u.get('top') else 'under'}{j}_{i}", [LE(z) - c * u["s"], Y(z) + (1 if u.get("top") else -1) * ry * .55, z], [c * u["w"] / 2, ry * .42, (zW - z0) / 3 * .75], u["color"],
                           k=ry * .3, kc=ry * .25, bone=A, mirror=True))
    out.append(tube("edge", [[LE(z0 + .02) - .004, Y(z0 + .02), z0 + .02, ry * 1.0], [LE(zW) - .004, Y(zW), zW, ry * .5]],
                    colors.get("edge", colors["arm"]), k=ry * .6, bone=A, mirror=True))
    out.append(tube("edgeH", [[LE(zW) - .004, Y(zW), zW, ry * .5], [LE(zT) - .004, Y(zT), zT, ry * .3]],
                    colors.get("edge", colors.get("hand", colors["arm"])), k=ry * .5, bone=Hd, mirror=True))
    # secondaries: rooted under the slab's trailing half, straight back, broad and round -- overlapping
    L0 = sec["len"]; LW = sec.get("lenW", L0 * .92)
    lens = sec.get("lens", [L0 + (LW - L0) * i / 4 for i in range(5)])
    rows = []
    for i, Ls in enumerate(lens):
        u = i / (len(lens) - 1); z = z0 + .01 + (zW - z0) * u
        at = [LE(z) - chord * .56, Y(z), z]
        rows.append(row(at, add(at, nrm([-1, 0, .04 + .08 * u]), Ls), sec["w"], bone=A))
    out.append(fea("sec", rows, sec["n"], sec["color"], sec["tip"], outline=sec.get("outline", "round"), up=[0, 1, 0], camber=.1, curve=-.01,
                   stagger=.0015, seed=11, mirror=True, **({"bars": sec["bars"]} if sec.get("bars") else {})))
    # primaries: rooted along the hand's rear half, fanned from a0 (inner, near straight back) to a1 (the outer)
    a0, a1 = prim["a"]; plens = prim["lens"]; K = len(plens); rows = []
    for i, Lp in enumerate(plens):
        u = i / (K - 1); z = zW + .02 + (zT - zW - .02) * u
        a = math.radians(a0 + (a1 - a0) * u)
        at = [LE(z) - C(z) * .5 + C(z) * .06 * u, Y(z), z]
        rows.append(row(at, add(at, [-math.cos(a), -.02, math.sin(a)], Lp), prim["w"], bone=Hd))
    out.append(fea("prim", rows, prim["n"], prim["color"], prim["tip"], outline=prim.get("outline", "flight"), up=[0, 1, 0], camber=.1, curve=prim.get("curve", .02),
                   lift=-.002, stagger=.0015, seed=12, mirror=True, **({"bars": prim["bars"]} if prim.get("bars") else {})))
    # coverts: tracts over the front half, each from s (its root, fraction of the chord forward of the arm's middle) back len
    for j, c in enumerate(covs):
        rows = []
        zz = [z0 + .015, z0 + (zW - z0) * .5, zW - .005]
        for i, z in enumerate(zz):
            at = [LE(z) - chord * (.48 - c["s"]), Y(z) + ry * c.get("h", .9) + .001, z]
            rows.append(row(at, add(at, nrm([-1, -c.get("drop", .04), .05]), c["len"]), c["w"], bone=A))
        out.append(fea(c.get("id", "cov%d" % j), rows, c["n"], c["color"], c["tip"], outline="round", up=[0, 1, 0], camber=.12, curve=-.02,
                       lift=.0015 * (len(covs) - j), stagger=.001, seed=13 + j, mirror=True, **({"bars": c["bars"]} if c.get("bars") else {})))
    # underwing coverts: tracts on the slab's UNDERSIDE, from s (as the coverts' s) straight back over the secondaries' roots --
    #  seen from below (a soaring bird's usual view) they close the arm into one feathered surface
    for j, c in enumerate(ucov or []):
        rows = []
        for z in [z0 + .015, z0 + (zW - z0) * .35, z0 + (zW - z0) * .7, zW - .005]:
            at = [LE(z) - chord * (.48 - c["s"]), Y(z) - ry * c.get("h", .85) - .001, z]
            rows.append(row(at, add(at, nrm([-1, -.01, .05]), c["len"]), c["w"], bone=A))   # (their face DOWN: seen from below, convex)
        out.append(fea(c.get("id", "ucov%d" % j), rows, c["n"], c["color"], c["tip"], outline="round", up=[0, -1, 0], camber=.05, curve=0,
                       lift=.0012 * (len(ucov) - j), stagger=.001, seed=17 + j, mirror=True, **({"bars": c["bars"]} if c.get("bars") else {})))
    if pcov:
        rows = []
        for i, z in enumerate([zW + .01, zW + (zT - zW) * .5, zT - .01]):
            a = math.radians(a0 + (a1 - a0) * i / 2 * .8)
            at = [LE(z) - C(z) * (.48 - pcov.get("s", .2)), Y(z) + ry * .7 + .001, z]
            rows.append(row(at, add(at, [-math.cos(a), -.03, math.sin(a)], pcov["len"]), pcov["w"], bone=Hd))
        out.append(fea("pcov", rows, pcov["n"], pcov["color"], pcov["tip"], outline="round", up=[0, 1, 0], camber=.12, lift=.001, seed=14, mirror=True,
                       **({"bars": pcov["bars"]} if pcov.get("bars") else {})))
    return out

def tail_fan(root, n, L, spread, w, color, tip, up=(0, 1, 0), lens=None, bars=None, tilt=0, outline="round", camber=.1, curve=.02, seed=21):
    """a fan of n rectrices from root, spread degrees each way, tilted (degrees, + up)"""
    k = 5; rows = []
    for i in range(k):
        u = i / (k - 1); a = math.radians(spread * (1 - 2 * u))
        dv = [-math.cos(a) * math.cos(math.radians(tilt)), math.sin(math.radians(tilt)), math.sin(a)]
        Lr = lens[i] if lens else L
        rows.append(row(add(root, [0, 0, (1 - 2 * u) * w * 1.2]), add(add(root, [0, 0, (1 - 2 * u) * w * 1.2]), dv, Lr), w))
    return fea("tail", rows, n, color, tip, outline=outline, up=list(up), camber=camber, curve=curve, stagger=.0015, seed=seed, **({"bars": bars} if bars else {}))
