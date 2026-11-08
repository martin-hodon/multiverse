# conv.py: field shapes -> the engine's sharp types (sharp.js): an ear ellipsoid -> a cupped `fin`, a tube / a chain of
# cones -> a `horn`
from shp import *

def ear_fin(sp, e, exclude, face_hint=None, inner=None, tip=None, tipAt=None, point=0.8, cup=0.45, thick=None, fillet=True,
            fillet_color=None, inner_rim=0.18, wide=1.0, slope=0.3, id=None, extra=None, long_=1.0, curl=0.0):
    """an ear ellipsoid `e` (c, r, rot or axes) made a sheet: its outline the ellipsoid's own (pointed toward its tip by
    `point`: 0.5 round, 1 a corner), its root buried in the head where its axis leaves it (found on the body's field
    without the shapes `exclude`), cupped toward its thin axis on the side `face_hint` (a direction) -- with a small
    fillet ellipsoid in the field round its base"""
    c, r = e["c"], e["r"]
    ax = e.get("axes") or axes_of(e.get("rot"))
    order = sorted(range(3), key=lambda i: r[i])
    i_n, i_w, i_l = order[0], order[1], order[2]
    N, W, Ldir = nrm(ax[i_n]), nrm(ax[i_w]), nrm(ax[i_l])
    rl, rw, rn = r[i_l] * long_, r[i_w] * wide, r[i_n]
    # which end is the tip: the one further from the head's inside
    probe = fd(sp, {"exclude": exclude, "points": [add(c, Ldir, rl), add(c, Ldir, -rl)]})["d"]
    if probe[1] > probe[0]: Ldir = mul(Ldir, -1)
    T = add(c, Ldir, rl)
    # the base: from deep on the axis out to where it leaves the body
    k = 1.0
    while True:
        P0 = add(c, Ldir, -rl * k)
        if fd(sp, {"exclude": exclude, "points": [P0]})["d"][0] < -0.002 or k > 4: break
        k += 0.25
    S = fd(sp, {"exclude": exclude, "rays": [[P0, T]]})["hits"][0]
    if S is None: raise RuntimeError(f"{sp}: the ear's axis never leaves the body")
    Lv = ln(sub(T, S)); yc = dot(sub(c, S), Ldir)
    def xw(y):
        q = max(-1.0, min(1.0, (y - yc) / rl)); ex = 0.5 if q < 0 else point
        return rw * max(0.0, 1 - q * q) ** ex
    x0 = max(xw(0.0), rw * 0.35)
    th = thick if thick is not None else min(2 * rn, max(0.003, 0.22 * rw))
    # the root, buried: deep enough that both its ends are inside
    dr, xr = max(th, x0 * 0.5), x0 * 0.92
    for it in range(14):
        R0 = add(add(S, Ldir, -dr), W, -xr); R1 = add(add(S, Ldir, -dr), W, xr)
        dd = fd(sp, {"exclude": exclude, "points": [R0, R1]})["d"]
        if max(dd) < -th * 0.5: break
        if it % 2: xr *= 0.85
        else: dr = min(dr * 1.2, 2.5 * x0)
    ys = [-dr * 0.5, 0.0] + [Lv * f for f in (0.12, 0.26, 0.4, 0.54, 0.67, 0.78, 0.87, 0.94)]
    P = lambda x, y: add(add(S, Ldir, y), W, x)
    side = lambda s: [P(s * ((x0 + xr) / 2 if y < 0 else max(xw(y), 0.0)), y) for y in ys]
    edge = side(-1) + [T] + side(1)[::-1]
    root = [R0, R1]
    # the face: the thin axis, toward the hint (else forward)
    hint = face_hint or [1, 0, 0]
    face = N if dot(N, hint) >= 0 else mul(N, -1)
    fin = {"id": id or e.get("id", "ear"), "type": "fin", "bone": e.get("bone", "head"), "root": root, "edge": edge, "corners": [len(ys)],
           "thick": th, "slope": slope, "face": face, "cup": cup, "color": e.get("color")}
    if curl: fin["curl"] = curl
    if inner: fin["inner"] = inner; fin["innerRim"] = inner_rim * rw
    if tip: fin["tip"] = tip; fin["tipAt"] = tipAt if tipAt is not None else 0.75
    for kk in ("mirror", "pat", "hair", "when"):
        if kk in e: fin[kk] = e[kk]
    if extra: fin.update(extra)
    out = []
    if fillet:
        fc = add(S, Ldir, -x0 * 0.15)
        # (a flat ellipsoid round the base: its frame W, L, N as an Euler XYZ)
        u, v, w = W, Ldir, crs(W, Ldir)
        R = [[u[0], v[0], w[0]], [u[1], v[1], w[1]], [u[2], v[2], w[2]]]
        m13 = max(-1, min(1, R[0][2])); yy = math.asin(m13)
        xx = math.atan2(-R[1][2], R[2][2]); zz = math.atan2(-R[0][1], R[0][0])
        out.append({"id": fin["id"] + "Base", "type": "ell", "bone": fin["bone"], "c": fc, "r": [x0 * 0.95, x0 * 0.8, max(th * 1.1, x0 * 0.45)],
                    "rot": [math.degrees(xx), math.degrees(yy), math.degrees(zz)], "k": x0 * 0.5, "kc": x0 * 0.2,
                    "color": fillet_color or e.get("color"), **({"mirror": True} if e.get("mirror") else {}),
                    **({"pat": e["pat"]} if "pat" in e else {}), **({"when": e["when"]} if "when" in e else {})})
    out.append(fin)
    return [r5(s) for s in out]

def horn_of(pts, src, **kw):
    """a horn through pts ([x, y, z, r]...: root first, the tip last), the rest copied from the shape it replaces"""
    h = {"id": src.get("id"), "type": "horn", "bone": src.get("bone", "body"), "pts": pts, "color": src.get("color")}
    for kk in ("mirror", "pat", "frame", "when", "wet", "tip", "tipAt"):
        if kk in src: h[kk] = src[kk]
    h.update(kw)
    return r5(h)

def extend_tip(pts, f=0.6):
    """a tube's last point blunt (r > 0): carried on past it to a point, f of its radius x 3 further"""
    a, b = pts[-2], pts[-1]
    d = nrm(sub(b, a)); L = b[3] * 3 * f
    return pts[:-1] + [b[:3] + [b[3]], add(b, d, L) + [0.0]]
