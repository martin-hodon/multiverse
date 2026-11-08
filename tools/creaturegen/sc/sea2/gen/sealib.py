# shared helpers for the sea creatures' generators (writes assets/creatures/sea/*.json)
import json, math

REPO = "/home/martin/store/apps/multiverse/"

def rnd(v, d=4):
    if isinstance(v, float):
        r = round(v, d)
        return 0 if r == 0 else r
    if isinstance(v, list): return [rnd(x, d) for x in v]
    if isinstance(v, tuple): return [rnd(x, d) for x in v]
    if isinstance(v, dict): return {k: rnd(x, d) for k, x in v.items()}
    return v

# ---------------------------------------------------------------- matrices (three.js Euler XYZ, degrees)
def mat_mul(A, B): return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def mat_vec(A, v): return [sum(A[i][k] * v[k] for k in range(3)) for i in range(3)]
def rot_xyz(deg):
    x, y, z = [d * math.pi / 180 for d in deg]
    Rx = [[1, 0, 0], [0, math.cos(x), -math.sin(x)], [0, math.sin(x), math.cos(x)]]
    Ry = [[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]]
    Rz = [[math.cos(z), -math.sin(z), 0], [math.sin(z), math.cos(z), 0], [0, 0, 1]]
    return mat_mul(mat_mul(Rx, Ry), Rz)
I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

def add(a, b): return [a[i] + b[i] for i in range(3)]
def sub(a, b): return [a[i] - b[i] for i in range(3)]
def mul(a, s): return [x * s for x in a]
def lerp(a, b, t): return [a[i] + (b[i] - a[i]) * t for i in range(len(a))]
def norm(a): l = math.sqrt(sum(x * x for x in a)) or 1; return [x / l for x in a]
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def mz(p): return [p[0], p[1], -p[2]] + list(p[3:])

class Rig:
    """parts as bones, with their REST world frames (as bodyspec.js convert chains them)"""
    def __init__(self): self.parts, self.W = [], {}
    def add(self, id, parent, pos, rot=None, shape=None, anim=None, color="@body", extra=None):
        R0, P0 = (I3, [0, 0, 0]) if parent is None else self.W[parent]
        R = mat_mul(R0, rot_xyz(rot)) if rot else R0
        P = add(P0, mat_vec(R0, pos))
        self.W[id] = (R, P)
        p = {"id": id, "parent": parent}
        p.update(shape or {"shape": "sphere", "size": {"r": 0.01}})
        p["pos"] = list(pos)
        if rot: p["rot"] = list(rot)
        p["color"] = color
        if anim: p["anim"] = anim
        if extra: p.update(extra)
        self.parts.append(p)
        return P
    def joint(self, id): return self.W[id][1]
    def to_world(self, id, v): R, P = self.W[id]; return add(P, mat_vec(R, v))
    def axis(self, id, v): return mat_vec(self.W[id][0], v)

def tube_part(a, b, r1, r2=None, bulge=0):
    c = mul(add(a, b), .5)
    s = {"a": list(a), "c": c, "b": list(b), "r1": r1, "r2": r2 if r2 is not None else r1}
    if bulge: s["bulge"] = bulge
    return {"shape": "tube", "size": s}

# ---------------------------------------------------------------- shapes
def S(type, **kw):
    d = {}
    if "id" in kw: d["id"] = kw.pop("id")
    d["type"] = type
    if "bone" in kw and kw["bone"] not in (None, "body"): d["bone"] = kw["bone"]
    kw.pop("bone", None)
    d.update({k: v for k, v in kw.items() if v is not None})
    return d

def smooth_profile(stations, x):
    """piecewise cubic (Catmull-Rom over x) through stations [(x, a, b, ...)] sorted by x descending or ascending"""
    st = sorted(stations, key=lambda s: s[0])
    xs = [s[0] for s in st]
    if x <= xs[0]: return list(st[0][1:])
    if x >= xs[-1]: return list(st[-1][1:])
    i = max(j for j in range(len(xs) - 1) if xs[j] <= x)
    t = (x - xs[i]) / (xs[i + 1] - xs[i])
    p0, p1, p2, p3 = st[max(0, i - 1)], st[i], st[i + 1], st[min(len(st) - 1, i + 2)]
    out = []
    for k in range(1, len(p1)):
        a, b, c, d = p0[k], p1[k], p2[k], p3[k]
        v = .5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t * t * t)
        lo, hi = min(b, c), max(b, c)
        out.append(min(max(v, lo - .25 * (hi - lo) - 1e-9), hi + .25 * (hi - lo) + 1e-9))
    return out

def loft(stations, n, bone_of, color, ids="L", k=None, pat=None, frame=None, kc=None, over=2.0, colors=None, rx_end=None, kf=.35, pat_x=None):
    """a laterally compressed body: n ellipsoids along x through stations (x, top, bottom, half width)"""
    xs = [s[0] for s in stations]
    x0, x1 = max(xs), min(xs)
    sp = (x0 - x1) / (n - 1)
    out = []
    for i in range(n):
        x = x0 - i * sp
        top, bot, hw = smooth_profile(stations, x)
        ry, rz = (top - bot) / 2, hw
        rx = over * sp
        # (at the ends: no further than the profile's end, and round)
        rx = min(rx, (x0 - x) + max(ry, rz) * (rx_end or 1.0), (x - x1) + max(ry, rz) * (rx_end or 1.0))
        rx = max(rx, min(ry, rz))
        col = colors(x) if colors else color
        sh = S("ell", id=f"{ids}{i}", bone=bone_of(x), c=[x, (top + bot) / 2, 0], r=[rx, ry, rz], k=k if k is not None else round(kf * min(ry, rz), 5),
               kc=kc, color=col, pat=pat if (pat_x is None or x < pat_x) else None, frame=frame if (pat_x is None or x < pat_x) else None)
        out.append(sh)
    return out

# ---------------------------------------------------------------- fins: a planar outline cut into triangles
def _area2(p): return sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p))) / 2
def earclip(P2):
    idx = list(range(len(P2)))
    if _area2(P2) < 0: idx.reverse()
    tris = []
    def inside(p, a, b, c):
        def s(p1, p2, p3): return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        d1, d2, d3 = s(p, a, b), s(p, b, c), s(p, c, a)
        return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))
    guard = 0
    while len(idx) > 3 and guard < 1000:
        guard += 1
        best = None
        for j in range(len(idx)):
            i0, i1, i2 = idx[j - 1], idx[j], idx[(j + 1) % len(idx)]
            a, b, c = P2[i0], P2[i1], P2[i2]
            cr = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if cr <= 1e-14: continue
            if any(inside(P2[q], a, b, c) for q in idx if q not in (i0, i1, i2)): continue
            # (the fattest ear first: no slivers)
            la, lb, lc = math.dist(a, b), math.dist(b, c), math.dist(c, a)
            q = cr / (la * la + lb * lb + lc * lc)
            if best is None or q > best[0]: best = (q, j)
        if best is None: break
        j = best[1]
        tris.append((idx[j - 1], idx[j], idx[(j + 1) % len(idx)]))
        idx.pop(j)
    if len(idx) == 3: tris.append(tuple(idx))
    return tris

def chaikin(pts, it):
    """rounds an open outline (its two ends -- a fin's root -- kept where they are)"""
    for _ in range(it):
        out = [pts[0]]
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            out += [lerp(a, b, .25), lerp(a, b, .75)]
        out.append(pts[-1])
        pts = out
    return pts

def fin(pts, r, color, bone=None, id="fin", k=None, mirror=False, pat=None, frame=None, kc=None, smooth=0, rays=False):
    """a fin: its outline (3D points, about planar) as rounded triangles r thick. `smooth`: rounds its corners (Chaikin,
    the root's two ends kept); `rays`: the coat pattern `finrays` (coatpat.js 33) laid from the middle of its root"""
    if smooth: pts = chaikin([list(p) for p in pts], smooth)
    if rays and pat is None:
        o = mul(add(pts[0], pts[-1]), .5)
        far = max(pts, key=lambda q: math.dist(q, o))
        u = norm(sub(far, o))
        n0 = [0, 0, 0]
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            n0 = add(n0, cross(sub(a, o), sub(b, o)))
        v = norm(cross(norm(n0), u))
        pat, frame = "finrays", {"o": o, "u": u, "v": v, "r": math.dist(far, o)}
    n = len(pts)
    c = [sum(p[k] for p in pts) / n for k in range(3)]
    N = [0, 0, 0]
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        N[0] += (a[1] - b[1]) * (a[2] + b[2]); N[1] += (a[2] - b[2]) * (a[0] + b[0]); N[2] += (a[0] - b[0]) * (a[1] + b[1])
    N = norm(N)
    t = [1, 0, 0] if abs(N[0]) < .9 else [0, 1, 0]
    U = norm(cross(N, t)); V = cross(N, U)
    P2 = [(dot(sub(p, c), U), dot(sub(p, c), V)) for p in pts]
    out = []
    for j, (a, b, cc) in enumerate(earclip(P2)):
        bj = bone((pts[a][0] + pts[b][0] + pts[cc][0]) / 3) if callable(bone) else bone
        out.append(S("tri", id=f"{id}{j}", bone=bj, a=list(pts[a]), b=list(pts[b]), c=list(pts[cc]), r=r, k=k, kc=kc, color=color,
                     pat=pat, frame=frame, mirror=True if mirror else None))
    return out

def arc(a, b, bulge, n):
    """points from a to b bowed by `bulge` (a vector at the middle)"""
    return [add(lerp(a, b, i / (n - 1)), mul(bulge, 4 * (i / (n - 1)) * (1 - i / (n - 1)))) for i in range(n)]

# ---------------------------------------------------------------- writing
def dumps_def(d, digits=4):
    d = rnd(d, digits)
    lines = ["{"]
    keys = list(d.keys())
    for ki, k in enumerate(keys):
        v = d[k]; comma = "," if ki < len(keys) - 1 else ""
        if k == "parts":
            lines.append('  "parts": [')
            lines += ["    " + json.dumps(p) + ("," if i < len(v) - 1 else "") for i, p in enumerate(v)]
            lines.append("  ]" + comma)
        elif k == "sculpt":
            lines.append('  "sculpt": {')
            sk = list(v.keys())
            for si, s in enumerate(sk):
                c2 = "," if si < len(sk) - 1 else ""
                if s == "shape":
                    lines.append('    "shape": [')
                    lines += ["      " + json.dumps(p) + ("," if i < len(v[s]) - 1 else "") for i, p in enumerate(v[s])]
                    lines.append("    ]" + c2)
                else:
                    lines.append(f'    {json.dumps(s)}: {json.dumps(v[s])}{c2}')
            lines.append("  }" + comma)
        else:
            lines.append(f'  {json.dumps(k)}: {json.dumps(v)}{comma}')
    lines.append("}")
    return "\n".join(lines) + "\n"

def write(name, d, digits=4):
    path = REPO + f"assets/creatures/sea/{name}.json"
    open(path, "w").write(dumps_def(d, digits))
    print("wrote", path, "shapes", len(d["sculpt"]["shape"]))

def fish_rig(xm, xs, xt, hz, body_r, x_front, x_back, degs=(4, 10, 15), phases=(0, -0.9, -1.8), color="@body", tail_tri=None):
    """the swimmer's spine: body (the front, root) -> mid -> stock -> tail, each beating a beat behind the one before"""
    R = Rig()
    R.add("body", None, [0, 0, 0], shape=tube_part([x_front, 0, 0], [xm, 0, 0], body_r, body_r * .8), color=color)
    R.add("mid", "body", [xm, 0, 0], shape=tube_part([0, 0, 0], [xs - xm, 0, 0], body_r * .8, body_r * .5), color=color,
          anim={"axis": "y", "deg": degs[0], "speed": hz, "phase": phases[0]})
    R.add("stock", "mid", [xs - xm, 0, 0], shape=tube_part([0, 0, 0], [xt - xs, 0, 0], body_r * .5, body_r * .3), color=color,
          anim={"axis": "y", "deg": degs[1], "speed": hz, "phase": phases[1]})
    R.add("tail", "stock", [xt - xs, 0, 0], shape=tail_tri or {"shape": "tri", "size": {"a": [0, 0, 0], "b": [(x_back - xt), body_r, 0], "c": [(x_back - xt), -body_r, 0], "r": body_r * .1}},
          color=color, anim={"axis": "y", "deg": degs[2], "speed": hz, "phase": phases[2]})
    return R

def bone_by_x(xm, xs, xt):
    return lambda x: "body" if x >= xm else "mid" if x >= xs else "stock" if x >= xt else "tail"

def edge(pts, r, color, bone=None, id="edge", k=None, mirror=False):
    """a dark margin along points (a fin's free edge): one tube"""
    if not callable(bone):
        return [S("tube", id=id, bone=bone, pts=[list(p[:3]) + [r] for p in pts], k=k, color=color, mirror=True if mirror else None)]
    # (split where the bone changes: each run on its own bone, sharing the point where they meet)
    runs, cur = [], [pts[0]]
    for p in pts[1:]:
        if bone(p[0]) != bone(cur[0][0]) and len(cur) > 1:
            runs.append(cur); cur = [cur[-1]]
        cur.append(p)
    runs.append(cur)
    out = []
    for i, rp in enumerate(runs):
        if len(rp) < 2: continue
        bx = sum(q[0] for q in rp) / len(rp)
        out.append(S("tube", id=f"{id}{i}", bone=bone(bx), pts=[list(p[:3]) + [r] for p in rp], k=k, color=color, mirror=True if mirror else None))
    return out

def keep_coats(name, d, keys=("params", "coats", "variants")):
    """(2026-11-07) the coats, variants and params the asset already has (added by hand or by the audit's coats.py),
    carried through a regeneration -- set right after its `colors`"""
    try: old = json.load(open(REPO + "assets/creatures/sea/" + name + ".json"))
    except Exception: return d
    out = {}
    for k, v in d.items():
        if k in keys and k in old: continue
        out[k] = v
        if k == "colors":
            for kk in keys:
                if kk in old: out[kk] = old[kk]
    return out
