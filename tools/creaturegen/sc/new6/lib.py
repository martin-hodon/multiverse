# lib.py -- helpers to write sculpt overlays for the ungulates (species JSON files)
import json, math, subprocess, os
ROOT = "/home/martin/store/apps/multiverse/"
HERE = os.path.dirname(os.path.abspath(__file__))
def joints(name, path=None):
    out = subprocess.run(["node", os.path.join(HERE, "jj.mjs"), name] + ([path] if path else []), capture_output=True, text=True, cwd=HERE)
    if out.returncode: raise SystemExit(out.stderr)
    return json.loads(out.stdout)
def R3(v): return [round(x, 4) for x in v]
def add(a, b, t=1): return [a[i] + b[i] * t for i in range(3)]
def sub(a, b): return [a[i] - b[i] for i in range(3)]
def mul(a, t): return [x * t for x in a]
def lerp(a, b, t): return [a[i] + (b[i] - a[i]) * t for i in range(3)]
def norm(a): l = math.sqrt(sum(x * x for x in a)) or 1; return [x / l for x in a]
def length(a): return math.sqrt(sum(x * x for x in a))
def ang(a): return math.degrees(math.atan2(a[1], a[0]))   # direction in the xy plane, degrees from +x
class Sculpt:
    def __init__(s): s.shapes = []
    def _p(s, d, kw):
        for k in ("k", "kc"):
            if k in kw and kw[k] is not None: kw[k] = round(kw[k], 4)
        d.update({k: v for k, v in kw.items() if v is not None})
        s.shapes.append(d); return d
    def ell(s, id, c, r, rot=None, bone=None, **kw):
        d = {"id": id, "type": "ell"}
        if bone: d["bone"] = bone
        d["c"] = R3(c); d["r"] = R3(r)
        if rot and any(abs(x) > 1e-6 for x in rot): d["rot"] = [round(x, 2) for x in rot]
        return s._p(d, kw)
    def sph(s, id, c, r, bone=None, **kw):
        d = {"id": id, "type": "sphere"}
        if bone: d["bone"] = bone
        d["c"] = R3(c); d["r"] = round(r, 4); return s._p(d, kw)
    def cone(s, id, a, b, ra, rb, bone=None, **kw):
        d = {"id": id, "type": "cone"}
        if bone: d["bone"] = bone
        d["a"] = R3(a); d["b"] = R3(b); d["ra"] = round(ra, 4); d["rb"] = round(rb, 4); return s._p(d, kw)
    def tube(s, id, pts, bone=None, **kw):
        d = {"id": id, "type": "tube"}
        if bone: d["bone"] = bone
        d["pts"] = [R3(p[:3]) + [round(p[3], 4)] for p in pts]; return s._p(d, kw)
    def tri(s, id, a, b, c, r, bone=None, **kw):   # a triangle thickened by r: a slab with rounded edges (a palm)
        d = {"id": id, "type": "tri"}
        if bone: d["bone"] = bone
        d["a"], d["b"], d["c"], d["r"] = R3(a), R3(b), R3(c), round(r, 4); return s._p(d, kw)
class Frame:
    """a local frame: o + t*a + h*n + z*Z  (a, n in the xy plane; Z = +z)"""
    def __init__(f, o, a):
        f.o = o; f.a = norm(a); f.n = [-f.a[1], f.a[0], 0]; f.deg = ang(f.a)
    def __call__(f, t, h=0, z=0): return [f.o[0] + f.a[0] * t + f.n[0] * h, f.o[1] + f.a[1] * t + f.n[1] * h, z]
    def rot(f, extra=0, rx=0, ry=0): return [rx, ry, f.deg + extra]
def write(name, sculpt, updates=None, path=None):
    p = path or ROOT + f"assets/creatures/mammals/{name}.json"
    d = json.load(open(p))
    if updates and "colors" in updates and "colors" not in d and "c" in d: updates = dict(updates); updates["c"] = updates.pop("colors")
    for k, v in (updates or {}).items():
        if v is None: d.pop(k, None)
        elif isinstance(v, dict) and isinstance(d.get(k), dict) and not k.startswith("!"): d[k] = {**d[k], **v}
        else: d[k.lstrip("!")] = v
    d["sculpt"] = "@@SCULPT@@"
    txt = json.dumps(d, indent=2, ensure_ascii=False)
    sc = sculpt
    lines = ["{"]
    items = list(sc.items())
    for i, (k, v) in enumerate(items):
        comma = "," if i < len(items) - 1 else ""
        if k == "shape":
            lines.append('    "shape": [')
            for j, q in enumerate(v):
                lines.append("      " + json.dumps(q, ensure_ascii=False) + ("," if j < len(v) - 1 else ""))
            lines.append("    ]" + comma)
        else:
            lines.append(f'    {json.dumps(k)}: ' + json.dumps(v, ensure_ascii=False) + comma)
    lines.append("  }")
    txt = txt.replace('"@@SCULPT@@"', "\n".join(lines))
    open(p, "w").write(txt + "\n")
    return p
def orient(d):
    """rot (degrees, three's XYZ) that turns an ell's local y axis to the direction d (local x stays ~ forward)"""
    d = norm(d)
    phi = -math.asin(max(-1, min(1, d[0])))
    th = math.atan2(d[2], d[1])
    return [math.degrees(th), 0, math.degrees(phi)]
def along(a, b):
    """rot turning an ell's local x axis along a->b in the xy plane (z ignored)"""
    return [0, 0, ang(sub(b, a))]
def chain(S, id, pts, bone=None, depth=1.0, **kw):
    """ells laid along a polyline [x, y, z, r]: each between two points, long along the segment, `depth` x deeper than wide"""
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        c = lerp(a[:3], b[:3], 0.5); L = length(sub(b[:3], a[:3])); r = (a[3] + b[3]) / 2
        S.ell(f"{id}{i}", c, [L * 0.5 + r * 0.6, r * depth, r], rot=[0, 0, ang(sub(b[:3], a[:3]))], bone=bone, **kw)
def carriers(S, kp=0.006, only=None):
    """seams between pattern frames crossfade over max(k) of the two nearest patterned shapes (bodymesh patternsAt):
    give each patterned shape a coincident low-k twin that carries its pattern (listed first, so it wins the tie), and
    take the pattern off the shape that does the blending -- the frames then meet in a sharp seam"""
    out = []
    for d in S.shapes:
        if "pat" in d and (only is None or d["id"] in only):
            c = dict(d); c["id"] = d["id"] + "P"; c["k"] = kp; c["kc"] = kp * 0.5
            out += [c, d]
        else:
            out.append(d)
    S.shapes = out
import subprocess, os
_SD = os.path.dirname(os.path.abspath(__file__))
def surf(S, qs):
    """the sculpt so far, measured: for each query {x, y, dir: [dy, dz], z0} how far from (x, y, z0) along dir the skin is,
    and which colour wins there (surf.mjs runs sculpt.js's own field)"""
    json.dump(S.shapes, open(_SD + "/_s.json", "w")); json.dump(qs, open(_SD + "/_q.json", "w"))
    return json.loads(subprocess.check_output(["node", _SD + "/surf.mjs", _SD + "/_s.json", _SD + "/_q.json"]))
def band(S, id, xs, y, hy, color, depth=0.035, proud=0.01, k=0.012, kc=0.004, dy=0.0, mirror=True, **kw):
    """a mark laid ON the skin: a run of flat ells along x at height y (rising dy over the run), each set so it stands
    `proud` out of the surface measured there -- paint that takes, without a slab"""
    n = len(xs)
    ys = [y + dy * i / max(1, n - 1) for i in range(n)]
    hs = surf(S, [{"x": x, "y": yy, "dir": [0, 1]} for x, yy in zip(xs, ys)])
    pts = [[x, yy, h["t"] - hy + proud, hy] for x, yy, h in zip(xs, ys, hs) if h["t"] is not None]
    S.tube(id, pts, k=k, kc=kc, color=color, mirror=mirror, **kw)
def headPill(id, a, b, r1, r2, color, HJ, HS, mirror=True):
    """a rig extra on the head, from a to b where it should END UP: mammals.js pulls a head extra's root onto the skull
    shrunk by headScale about the neck joint (hP) and keeps its length -- so the root is written un-shrunk"""
    f = [HJ[i] + (a[i] - HJ[i]) / HS for i in range(3)]; t = add(f, sub(b, a))
    return {"id": id, "parent": "head", "from": R3(f), "to": R3(t), "r1": round(r1, 4), "r2": round(r2, 4), "color": color, **({"mirror": True} if mirror else {})}
def _cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def _dot(a, b): return sum(a[i] * b[i] for i in range(3))
def decals(S, specs, proud=0.006, k=0.012, kc=0.003, d=0.04, c=None, **kw):
    """sharp-edged paint ON the skin: each spec (id, x, y, z0, dir[dy,dz], rx, ry, color[, spin]) -- a ray from (x, y, z0) out
    along dir finds the skin; an ellipsoid is laid tangent there, its axes rx (along x, spun by spin deg) and ry, its depth
    matched to the measured curvature so it stands `proud` over the whole patch and drops under the skin at its rim"""
    qs = []
    for sp in specs:
        _, x, y, z0, (dy, dz) = sp[:5]; L = math.hypot(dy, dz); dy, dz = dy / L, dz / L; q = (-dz, dy)
        for ox, oq in ((0, 0), (d, 0), (-d, 0), (0, d), (0, -d)):
            qs.append({"x": x + ox, "y": y + oq * q[0], "z0": z0 + oq * q[1], "dir": [dy, dz]})
    hs = surf(S, qs)
    for i, sp in enumerate(specs):
        id, x, y, z0, (dy, dz), rx, ry, color = sp[:8]; spin = sp[8] if len(sp) > 8 else 0
        L = math.hypot(dy, dz); dy, dz = dy / L, dz / L; q = (-dz, dy)
        h = hs[5 * i: 5 * i + 5]
        if any(e["t"] is None for e in h): print("decal miss", id); continue
        Pt = [[x + ox, y + oq * q[0] + e["t"] * dy, z0 + oq * q[1] + e["t"] * dz] for (ox, oq), e in zip(((0, 0), (d, 0), (-d, 0), (0, d), (0, -d)), h)]
        Tx, Tq = sub(Pt[1], Pt[2]), sub(Pt[3], Pt[4])
        n = norm(_cross(Tx, Tq))
        if _dot(n, [0, dy, dz]) < 0: n = mul(n, -1)
        kx = max(0.0, -_dot(sub(lerp(Pt[1], Pt[2], 0.5), Pt[0]), n)) * 2 / d ** 2
        kq = max(0.0, -_dot(sub(lerp(Pt[3], Pt[4], 0.5), Pt[0]), n)) * 2 / d ** 2
        c_ = c or min(0.25, max(0.025, 0.5 * (rx * rx * kx + ry * ry * kq)))
        ez = n if n[2] >= 0 else mul(n, -1)
        ex = norm(sub(Tx, mul(ez, _dot(Tx, ez)))); ey = _cross(ez, ex)
        a = math.radians(spin); ex, ey = add(mul(ex, math.cos(a)), ey, math.sin(a)), add(mul(ey, math.cos(a)), ex, -math.sin(a))
        ry_ = math.degrees(math.asin(max(-1, min(1, ez[0])))); rx_ = math.degrees(math.atan2(-ez[1], ez[2])); rz_ = math.degrees(math.atan2(-ey[0], ex[0]))
        S.ell(id, add(Pt[0], n, -(c_ - proud)), [rx, ry, c_], rot=[round(rx_, 2), round(ry_, 2), round(rz_, 2)], k=k, kc=kc, color=color, **kw)
# ---- HORNS AND ANTLERS as continuous tubes (2026-11-05): a chain of rig pills split between the field (thick) and the
#      detail cones (thin) came apart in the game -- the field's grid eats a pill thinner than ~a cell, and the thin ones
#      were open cones meeting at angles. Here a horn is ONE path: its thick run a field tube, its thin run one detail
#      lathe that starts inside the thick run; a pale tip is a sheath over the last part of the SAME path.
def _cr(P, per=3):
    """Catmull-Rom through [x, y, z, r] points: `per` steps a span, radii eased linearly"""
    if len(P) < 3: return [list(p) for p in P]
    out = []
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)]
        for j in range(per):
            t = j / per; t2, t3 = t * t, t * t * t
            out.append([0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in range(3)] + [p1[3] + (p2[3] - p1[3]) * t])
    out.append(list(P[-1]))
    return out
def _plen(P): return [0] + [sum(math.dist(P[i][:3], P[i + 1][:3]) for i in range(j)) for j in range(1, len(P))]
def _sub_path(P, f0):
    """the path from fraction f0 of its length to its end"""
    L = _plen(P); T = L[-1] * f0
    for i in range(len(P) - 1):
        if L[i + 1] >= T:
            u = (T - L[i]) / max(1e-9, L[i + 1] - L[i]); return [[P[i][k] + (P[i + 1][k] - P[i][k]) * u for k in range(4)]] + [list(p) for p in P[i + 1:]]
    return [list(P[-1])]
HORNS = []   # (every path laid, for the continuity check)
def _thin(t):   # (a lathe's rings: every other point of the dense path -- its tris halved, its ends kept)
    return t if len(t) <= 3 else t[:-1:2] + [t[-1]]
def horn(S, id, pts, color, cell, bone="head", k=0.006, tips=(), mirror=True, parent=None, fade=None):
    """one horn/antler/tine along pts [x, y, z, r] (a smooth path). tips: [(from fraction, colour, grow)] sheaths over the
    end of the same path (a tine's paling point). parent: the id of the path it grows out of (its root must be inside it)"""
    if parent:   # (rooted ON its parent's path, the nearest point to where it was asked for: never a gap)
        P = next(h[1] for h in HORNS if h[0] == parent)
        q = min(P, key=lambda q: math.dist(q[:3], pts[0][:3])); pts = [q[:3] + [pts[0][3]]] + [list(p) for p in pts[1:]]
    D = _cr(pts); thr, thd = 1.1 * cell, 0.78 * cell   # (thinner than ~a cell the grid erodes it: drawn as a lathe, under bodyspec's 0.8-cell detail cut)
    j = next((i for i, p in enumerate(D) if p[3] < thr), len(D))
    if j >= 2: S.tube(id, D[:min(j + 1, len(D))], bone=bone, k=k, kc=min(k, 0.003), color=color, mirror=mirror)
    if j < len(D):
        t = [p[:3] + [min(p[3], thd)] for p in D[max(j - 3, 0):]]
        re = t[-1][3]
        if re >= 0.0075:   # (round 7b: a blunt point -- a rounded cap of its end radius, not a needle)
            t = _thin(t); e, dv = t[-1], norm(sub(t[-1][:3], t[-2][:3]))
            t += [add(e[:3], mul(dv, re * math.sin(math.radians(a)))) + [max(re * math.cos(math.radians(a)), 0.002)] for a in (40, 65, 82)]
        else: t[-1][3] = min(re, 0.002); t = _thin(t)
        fd = {}
        if fade:   # (the thin run's colour fading to fade[1] from fade[0] of the WHOLE path's length on: no band)
            cum = _plen(D); j0 = max(j - 3, 0); tot = cum[-1] or 1
            fd = {"tip": fade[1], "tipAt": round(max(0.0, (fade[0] * tot - cum[j0]) / ((tot - cum[j0]) or 1)), 3)}
        S.tube(id + "d", t, bone=bone, k=0, color=color, mirror=mirror, **fd)
    for n, (f0, c, g) in enumerate(tips):
        t = [p[:3] + [min(p[3] * g, thd)] for p in _sub_path(D, f0)]; t[-1][3] = min(t[-1][3], 0.0025)
        S.tube(f"{id}t{n}", _thin(t), bone=bone, k=0, color=c, mirror=mirror)
    HORNS.append((id, D, parent))
def check_horns(tol=0.001):
    """every path that grows out of another starts INSIDE it (no gap > tol); every path's steps join (a tube is one piece)"""
    by = {h[0]: h for h in HORNS}
    for id, D, par in HORNS:
        for a, b in zip(D, D[1:]): assert math.dist(a[:3], b[:3]) < 0.2, f"{id}: a step of {math.dist(a[:3], b[:3]):.3f}"
        if par:
            P = by[par][1]; r0 = D[0][:3]
            gap = min(math.dist(r0, q[:3]) - q[3] for q in P)
            assert gap <= tol, f"{id}: its root is {gap * 1000:.1f} mm outside {par}"
    n = len(HORNS); HORNS.clear(); return n
# ---- the back of the thigh (2026-11-05 round 4): the hamstrings, a tapered tube on the thigh bone whose REAR surface runs
#      straight from the point of the buttock down to the point of the hock -- no shelf of rump over a thin shank
def ham(S, J, top, bot, r_top, r_bot, color, k, zf=0.85, id="ham", bone="legHLu", n=4, **kw):
    """top, bot: [over, f] -- the rear surface `over` x hipH behind the hip joint, at the height f of the way from the hock
    (f 0) up to the hip (f 1); the tube's axis is set r in front of it"""
    hip, hock = J["legHLu"]["o"], J["legHLl"]["o"]
    H, span = hip[1], hip[1] - hock[1]
    pts = []
    for i in range(n):
        t = i / (n - 1)
        over = top[0] + (bot[0] - top[0]) * t; f = top[1] + (bot[1] - top[1]) * t; r = r_top + (r_bot - r_top) * t
        pts.append([hip[0] - over * H + r, hock[1] + f * span, hip[2] * zf, r])
    S.tube(id, pts, bone=bone, k=k, color=color, mirror=True, **kw)
