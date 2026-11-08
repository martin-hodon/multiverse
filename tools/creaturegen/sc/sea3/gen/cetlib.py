# shared helpers for the big swimmers (orca, humpback, plesiosaurus): sealib's, plus oriented ellipsoid slices
import sys, math, json
sys.path.insert(0, "/home/martin/store/apps/multiverse/tools/creaturegen/sc/sea2/gen")
from sealib import *

def euler_xyz(u, v, w):
    """three.js Euler XYZ (degrees) of the rotation whose columns are the local axes u, v, w (world vectors)"""
    R = [[u[0], v[0], w[0]], [u[1], v[1], w[1]], [u[2], v[2], w[2]]]
    m13 = max(-1, min(1, R[0][2]))
    y = math.asin(m13)
    if abs(m13) < 0.99999:
        x = math.atan2(-R[1][2], R[2][2]); z = math.atan2(-R[0][1], R[0][0])
    else:
        x = math.atan2(R[2][1], R[1][1]); z = 0
    return [math.degrees(x), math.degrees(y), math.degrees(z)]

def frame(u, v_hint):
    """an orthonormal frame: u, v (v_hint made square to u), w = u x v"""
    u = norm(u); v = norm(sub(v_hint, mul(u, dot(v_hint, u)))); w = cross(u, v)
    return u, v, w

def oell(id, c, r, u, v, w, bone=None, **kw):
    """an ellipsoid with its radii r along the frame u, v, w"""
    return S("ell", id=id, bone=bone, c=list(c), r=list(r), rot=euler_xyz(u, v, w), **kw)

def smooth(stations, x):
    return smooth_profile(stations, x)

def lerpf(a, b, t): return a + (b - a) * t
def sstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0))); return t * t * (3 - 2 * t)

def write_to(path_rel, d, digits=4):
    path = REPO + f"assets/creatures/{path_rel}.json"
    open(path, "w").write(dumps_def(d, digits))
    print("wrote", path, "shapes", len(d["sculpt"]["shape"]))

def body_loft(stations, n, bone_of, color, ids, kf=0.3, over=2.0, pat=None, colors=None, kc=None):
    """the trunk: n ellipsoids along x through stations (x, top, bottom, half width) -- loft() with a pattern"""
    out = loft(stations, n, bone_of, color, ids=ids, kf=kf, over=over, colors=colors, kc=kc)
    if pat:
        for s in out: s["pat"] = pat
    return out

def blade(id, root, span_dir, chord_dir, length, n, chord, thick, le_off, bone_of, color, k=None, kc=None, twist=None, sweep=None, droop=None, pat=None, over=1.6):
    """a flipper / fin / fluke half: n oriented ellipsoid slices along span_dir from root, each `chord(t)` long along
    chord_dir (its middle le_off(t) - chord/2 from the leading edge line), `thick(t)` thick; sweep(t): metres the
    slice is set back along -chord_dir; droop(t): metres along the blade's normal (a curve); twist(t): degrees about the span"""
    s_dir = norm(span_dir)
    cdir = norm(sub(chord_dir, mul(s_dir, dot(chord_dir, s_dir))))
    ndir = cross(cdir, s_dir)   # (the blade's normal)
    out = []
    ds = length / (n - 1)
    for i in range(n):
        t = i / (n - 1)
        ch, th = chord(t), thick(t)
        if ch <= 1e-4: continue
        cd, nd = cdir, ndir
        if twist:
            a = math.radians(twist(t))
            cd = add(mul(cdir, math.cos(a)), mul(ndir, math.sin(a))); nd = cross(cd, s_dir)
        le = add(root, mul(s_dir, t * length))
        if sweep: le = add(le, mul(cdir, -sweep(t)))
        if droop: le = add(le, mul(ndir, droop(t)))
        c = add(le, mul(cd, le_off(t) - ch / 2))
        rz = max(ds * over, th * 0.5)
        # (at the tip no further out than the blade's end)
        if i == n - 1: rz = max(th * .5, min(rz, ch * .5))
        kk = k if k is not None else round(0.45 * min(th / 2, rz), 5)
        out.append(oell(f"{id}{i}", c, [ch / 2, th / 2, rz], cd, nd, cross(cd, nd), bone=bone_of(t), k=kk, kc=kc, color=color(t) if callable(color) else color, pat=pat))
    return out

def trunk_tubes(stations, cuts, bones, color, ids="trunk", step=0.15, ov=0.12, k=0.1, kc=None, pat=None, rfun=None):
    """the trunk as round tubes (exact distances: no ripples), one per bone between `cuts` (x descending: the front,
    the joints..., the back), each overlapping the next by ov; r = rfun(top, bottom, half width)"""
    rfun = rfun or (lambda t, b, w: (t - b) / 4 + w / 2)
    out = []
    for j in range(len(cuts) - 1):
        xa = cuts[j] + (ov if j else 0); xb = cuts[j + 1] - (ov if j < len(cuts) - 2 else 0)
        n = max(2, int(math.ceil((xa - xb) / step)) + 1)
        pts = []
        for i in range(n):
            x = xa - (xa - xb) * i / (n - 1)
            t, b, w = smooth_profile(stations, x)
            pts.append([x, (t + b) / 2, 0, rfun(t, b, w)])
        out.append(S("tube", id=f"{ids}{j}", bone=bones[j], pts=pts, k=k, kc=kc, color=color, pat=pat))
    return out

def blade_outline(root, span_dir, chord_dir, length, chord, le_off=None, sweep=None, n=24, inset=0.0, tmax=1.0, te_fn=None):
    """a flat blade's outline (3D points in one plane): the leading edge out from the root to the tip, the trailing edge
    back. inset: the chord that much narrower about its middle (a thicker layer inside the thin one); te_fn(t) -> a
    metres the trailing edge is moved forward (serrations)"""
    s_dir = norm(span_dir); cd = norm(sub(chord_dir, mul(s_dir, dot(chord_dir, s_dir))))
    LE, TE = [], []
    for i in range(n + 1):
        t = tmax * (i / n) ** 0.85 if i < n else tmax
        ch = chord(t) * (1 - inset)
        base = add(add(root, mul(s_dir, t * length)), mul(cd, -(sweep(t) if sweep else 0) + (le_off(t) if le_off else 0)))
        mid = add(base, mul(cd, -chord(t) / 2))
        le = add(mid, mul(cd, ch / 2)); te = add(mid, mul(cd, -ch / 2 + (te_fn(t) if te_fn else 0)))
        LE.append(le); TE.append(te)
    pts = LE + TE[::-1][:-1] if chord(tmax) * (1 - inset) < 1e-3 else LE + TE[::-1]
    return pts

def plates(id, layers, bone, color, k=0.02, kc=None, mirror=False, pat=None):
    """stacked plates: [(outline, r)] -- each a planar outline cut into triangles r thick, blended: a blade thin at its
    edges and thicker inside, its outline exact (no slice steps)"""
    out = []
    for li, (pts, r) in enumerate(layers):
        out += fin(pts, r, color, bone=bone, id=f"{id}{li}_", k=k, kc=kc, mirror=mirror, pat=pat)
    return out


# (2026-11-07) FINS AS EXACT SHEETS. A fin sliced into the grid (a stack of flat ellipsoids, a keel a tube or two cells
# thick) came out with every edge sawtoothed: its thin slices sampled into steps. These draw the fin's OUTLINE as one
# membrane (finsheet.py mfin: exact, smooth, rooted inside the body); only a thick core at its root goes into the grid.
def qbez(p0, c, p2, n, end=False):
    """a quadratic Bezier's points (x, y, 0), its end left off unless `end`"""
    return [[(1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p2[1], 0]
            for t in [j / n for j in range(n + (1 if end else 0))]]

def median_sheet(id, bone, base, le0, ctl_le, tip, ctl_te, free, te0, r, color, down=False, n=12, sink=0.045, pat=None):
    """a dorsal / anal fin in the midplane, its points (x, height over the skin line `base(x)`, or under it if `down`):
    the leading edge from le0 bowed toward ctl_le to the tip, the trailing edge bowed toward ctl_te to its free rear tip,
    a short edge to te0 on the skin, and the root buried `sink` under it"""
    from finsheet import mfin
    sgn = -1 if down else 1
    P = lambda q: (q[0], base(q[0]) + sgn * q[1])
    o = qbez(P(le0), P(ctl_le), P(tip), n) + qbez(P(tip), P(ctl_te), P(free), n) + [list(P(te0)) + [0]]
    xm = (le0[0] + te0[0]) / 2
    o += [[te0[0], base(te0[0]) - sgn * sink, 0], [xm, base(xm) - sgn * sink, 0], [le0[0], base(le0[0]) - sgn * sink, 0]]
    if down: o = o[::-1]
    return mfin(o, r, color, bone=bone, id=id, smooth=1, rays=False, pat=pat)

def ridge_sheet(id, bone, base, x0, x1, h, r, color, down=False, n=16, sink=0.03, pat=None):
    """a keel along the midline from x0 (ahead) back to x1: its edge h(t) (t 0 -> 1) over the skin line base(x), or
    under it if `down`; its root buried `sink`. `bone` a name or a function of x"""
    from finsheet import mfin
    sgn = -1 if down else 1
    xs = [x0 + (x1 - x0) * j / n for j in range(n + 1)]
    o = [[x, base(x) + sgn * h(j / n), 0] for j, x in enumerate(xs)] + [[x, base(x) - sgn * sink, 0] for x in xs[::-1][1:-1]]
    if down: o = o[::-1]
    return mfin(o, r, color, bone=bone, id=id, smooth=1, rays=False, pat=pat)

def fluke_sheet(id, bone, le, te, y, r, color, n=16, pat=None, span=None, tip=None):
    """flukes as ONE horizontal sheet across both: the leading edge x = le(|z|) out to the tip (where it meets the
    trailing edge te(|z|), or at `span`; `tip` (x, z) its point if given), back along the trailing edge to the notch
    and out again the other side; y its height"""
    from finsheet import mfin
    zt = 0.0
    while le(zt + 0.002) - te(zt + 0.002) > 0 and (span is None or zt + 0.002 <= span): zt += 0.002
    zs = [zt * (1 - (1 - j / n) ** 1.5) for j in range(n + 1)]   # (closer toward the tip)
    tipx, tipz = tip if tip else ((le(zt) + te(zt)) / 2, zt)
    half = [[le(z), y, z] for z in zs[:-1]] + [[tipx, y, tipz]] + [[te(z), y, z] for z in zs[-2:0:-1]]
    o = half + [[te(0.0), y, 0.0]] + [[p[0], p[1], -p[2]] for p in half[::-1][:-1]]
    return mfin(o, r, color, bone=bone, id=id, smooth=1, rays=False, pat=pat)

def bury(pts, s_dir, d):
    """a blade_outline closed through its root `d` deeper along -s_dir (into the body), so no root edge shows"""
    s = norm(s_dir)
    return pts + [sub(pts[-1], mul(s, d)), sub(pts[0], mul(s, d))]

def root_pad(id, root, s_dir, chord_dir, chord0, thick, bone, color, k=0.02, along=0.04, mirror=False):
    """a smooth flat ellipsoid in the grid at a blade's root (its bulk where it meets the body), its edge inside the sheet"""
    u, v, w = frame(chord_dir, s_dir)
    c = add(add(root, mul(norm(s_dir), along)), mul(u, -chord0 / 2))
    return [oell(id, c, [chord0 * 0.36, along * 1.6, thick], u, v, w, bone=bone, k=k, color=color, mirror=mirror or None)]


# (2026-11-08) FINS AS ENGINE SHEETS (sharp.js `fin`): a fin is one sheet, its RIM exactly the authored outline, its
# thickness a function of the distance in from the rim (`thick` at most, `slope` per metre) -- sharp everywhere at the
# edge, a regular airfoil-like cross-section, no slices to step and no plates to crumble. Its root line is buried in the
# body; a soft fillet in the grid (an ordinary ell) makes the join. `b` on a rim point blunts the rim there (the leading
# edge's, ~1.8). (2026-11-08, pass 2) `grid: "flow"`: the sheet's grid solved harmonic, its columns curving with the
# outline -- straight columns fanned out of a short root bunched into a line of slivers down a swept fluke or flipper.
def fin_sheet(id, bone, root, edge, corners, thick, color, slope=0.3, pat=None, mirror=False, face=None, root_bone=None, n=None, rows=None, grid="flow", **kw):  # rows: the `across` count
    return S("fin", id=id, bone=bone, root=[list(p)[:3] for p in root], edge=[list(p) for p in edge], corners=corners, thick=thick, slope=slope,
             color=color, pat=pat, mirror=True if mirror else None, face=face, rootBone=root_bone, n=n, across=rows, grid=grid, **kw)

def dorsal_sheet(id, bone, skin, le, te, yt, tip, thick, color, sink=0.04, blunt=1.8, nt=16, slope=0.3, pat=None, n=None, rows=None, le_max=1.0, **kw):
    """a dorsal fin in the midplane: le(t), te(t), yt(t) its leading edge, trailing edge and height for t 0 (the root,
    under the skin `skin(x)`) to 1; `tip` (x, y) its point. The root runs along under the skin from the leading edge's
    foot to where the trailing edge comes down to the skin"""
    ts = [j / nt for j in range(nt)]
    LE = [[le(t), yt(t), 0, blunt] for t in ts if t <= le_max]   # (le_max: the leading edge's last knot, the spline then sweeps back to the tip)
    TE = [[te(t), yt(t), 0, 1] for t in ts[::-1] if yt(t) > skin(te(t))]
    xr = TE[-1][0] if TE else te(0)
    xs = [LE[0][0] + 0.01 + (xr - LE[0][0] - 0.01) * j / 5 for j in range(6)]
    root = [[x, skin(x) - sink, 0] for x in xs]
    edge = LE[1:] + [[tip[0], tip[1], 0, 1]] + TE
    return fin_sheet(id, bone, root, edge, [len(LE) - 1], thick, color, slope=slope, pat=pat, n=n, rows=rows, **kw)

def flipper_sheet(id, bone, root, span_dir, chord_dir, length, chord, thick, color, le_off=None, sweep=None, sink=0.04, blunt=1.8, slope=0.3,
                  pat=None, mirror=True, n=None, rows=None, droop=None, corner=True, m=16, **kw):
    """a pectoral flipper: blade_outline's leading edge out to its tip and trailing edge back, the root buried `sink`
    back along the span into the body; droop(t): metres along the blade's normal (its camber, down); m: the samples
    along each edge"""
    pts = blade_outline(root, span_dir, chord_dir, length, chord, le_off=le_off, sweep=sweep, n=m)
    LE, TE = pts[:m + 1], pts[m + 1:]
    if droop:
        s_dir = norm(span_dir); cd = norm(sub(chord_dir, mul(s_dir, dot(chord_dir, s_dir)))); nd = cross(cd, s_dir)
        ts = [(i / m) ** 0.85 if i < m else 1.0 for i in range(m + 1)]
        LE = [add(p, mul(nd, droop(t))) for p, t in zip(LE, ts)]
        TE = [add(p, mul(nd, droop(t))) for p, t in zip(TE, ts[::-1][-len(TE):])]
    tipP = mul(add(LE[-1], TE[0]), 0.5) if len(TE) == m + 1 else LE[-1]
    s = norm(span_dir)
    rt = [sub(LE[0], mul(s, sink)), sub(TE[-1], mul(s, sink))]
    edge = [list(p) + [blunt] for p in LE[:-1]] + [list(tipP) + [1]] + [list(p) + [1] for p in (TE[1:] if len(TE) == m + 1 else TE)]
    return fin_sheet(id, bone, rt, edge, [len(LE) - 1] if corner else [], thick, color, slope=slope, pat=pat, mirror=mirror, n=n, rows=rows, **kw)

def fluke_sheet2(id, bone, le, te, y, span, tip, root_x, root_w, thick, color, n=None, rows=None, blunt=1.8, slope=0.3, pat=None, nz=12, **kw):
    """both flukes as ONE sheet: rooted across the stock (x root_x, half width root_w), its rim out along the left
    leading edge le(z), round the pointed `tip` (x, z), back along the trailing edge te(z) to the notch at z = 0, and the
    same on the right; y(z) the height (a droop)"""
    zs = [span * (j / nz) ** 0.9 for j in range(1, nz)]
    left = [[le(z), y(z), z, blunt] for z in zs] + [[tip[0], y(tip[1]), tip[1], 1]] + [[te(z), y(z), z, 1] for z in zs[::-1]]
    notch = [te(0.0), y(0.0), 0.0, 1]
    right = [[p[0], p[1], -p[2], p[3]] for p in left[::-1]]
    root = [[root_x, y(0.0), root_w], [root_x, y(0.0), -root_w]]
    edge = left + [notch] + right
    return fin_sheet(id, bone, root, edge, [len(zs), len(left), len(left) + 1 + len(zs)], thick, color, slope=slope, pat=pat, n=n, rows=rows, **kw)

def fluke_sheet_blade(id, bone, LE, TE, root_x, root_w, thick, color, blunt=1.8, slope=0.3, pat=None, n=None, rows=None, **kw):
    """both flukes as ONE sheet from one side's blade outline (blade_outline's LE root -> tip and TE root -> tip, the
    left side, z >= 0, the root at the centreline): rooted across the stock (x root_x, half width root_w); the rim out
    the left leading edge, round the tip, back along the trailing edge to the notch (its point at z = 0), the right side
    mirrored"""
    tip = LE[-1] if len(sub(LE[-1], TE[-1])) < 1e-6 else mul(add(LE[-1], TE[-1]), 0.5)
    if root_x == "le":   # (2026-11-08, pass 2: the root's ends ON the leading edge, where it crosses z = root_w -- set ahead of
        #  it, the rim's first piece ran back along the stock into a concave corner where the edge turned out, and the
        #  sheet's columns from that end folded across it: the pinched leading-edge root)
        root_x = next(a[0] + (b[0] - a[0]) * (root_w - a[2]) / (b[2] - a[2]) for a, b in zip(LE, LE[1:]) if a[2] <= root_w < b[2])
    le = [list(p) + [blunt] for p in LE[:-1] if p[2] > root_w * 1.2]
    te = [list(p) + [1] for p in TE[::-1][1:] if p[2] > 1e-4]
    notch = list(TE[0][:2]) + [0.0, 1]
    for a, b in zip(TE, TE[1:]):   # (a trailing edge that starts past the midline: the notch where it crosses it)
        if a[2] <= 0 < b[2]:
            t = -a[2] / (b[2] - a[2]); notch = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, 0.0, 1]; break
    left = le + [list(tip) + [1]] + te
    right = [[p[0], p[1], -p[2], p[3]] for p in left[::-1]]
    root = [[root_x, notch[1], root_w], [root_x, notch[1], -root_w]]
    return fin_sheet(id, bone, root, left + [notch] + right, [len(le), len(left), len(left) + 1 + len(te)], thick, color, slope=slope, pat=pat,
                     n=n, rows=rows, **kw)
