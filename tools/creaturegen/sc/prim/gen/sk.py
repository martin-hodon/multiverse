# SCULPTING IN THE STANDING POSE: shapes written where they should be when the animal STANDS (skeleton.js, amp 0 --
# its legs folded by the IK), carried back onto each bone's REST frame (as bodyspec.js convert builds them: the legs
# hanging straight) -- so a crouched leg is drawn as it is seen, not guessed from a straight one.
import json, math, subprocess, sys
SP = "/home/martin/store/apps/multiverse/tools/creaturegen/"

def mat(e):  # THREE column-major -> rows
    return [[e[0], e[4], e[8], e[12]], [e[1], e[5], e[9], e[13]], [e[2], e[6], e[10], e[14]], [0, 0, 0, 1]]
def mul(A, B): return [[sum(A[i][k] * B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
def inv_rigid(M):
    R = [[M[j][i] for j in range(3)] for i in range(3)]; t = [M[i][3] for i in range(3)]
    ti = [-sum(R[i][k] * t[k] for k in range(3)) for i in range(3)]
    return [R[0] + [ti[0]], R[1] + [ti[1]], R[2] + [ti[2]], [0, 0, 0, 1]]
def ap(M, p): return [sum(M[i][k] * p[k] for k in range(3)) + M[i][3] for i in range(3)]
def rotm(rot):  # THREE Euler XYZ (degrees) -> 3x3
    x, y, z = [math.radians(a) for a in rot]
    a, b, c, d, e, f = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    ae, af, be, bf = a * e, a * f, b * e, b * f
    return [[c * e, -c * f, d], [af + be * d, ae - bf * d, -b * c], [bf - ae * d, be + af * d, a * c]]
def euler(m):
    y = math.asin(max(-1, min(1, m[0][2])))
    if abs(m[0][2]) < 0.9999999: x = math.atan2(-m[1][2], m[2][2]); z = math.atan2(-m[0][1], m[0][0])
    else: x = math.atan2(m[2][1], m[1][1]); z = 0
    return [round(math.degrees(v), 2) for v in (x, y, z)]

class Frames:
    def __init__(self, name):
        out = subprocess.run(["node", "--import", SP + "reg.mjs", SP + "sc/prim/t_frames.mjs", name], capture_output=True, text=True, cwd=SP)
        if out.returncode: raise SystemExit(out.stderr[-2000:])
        self.F = json.loads(out.stdout)
        self.M = {}
        for b, f in self.F.items():
            self.M[b] = mul(mat(f["rest"]), inv_rigid(mat(f["posed"])))   # posed world -> rest world, riding bone b
    def J(self, b): e = self.F[b]["posed"]; return [e[12], e[13], e[14]]
    def end(self, b):  # the far end of a leg bone, standing
        e = self.F[b]["posed"]; L = self.F[b]["len"]; return [e[12] - e[4] * L, e[13] - e[5] * L, e[14] - e[6] * L]
    def to_rest(self, s):
        b = s.get("bone", "body"); M = self.M[b]
        R3 = [r[:3] for r in M[:3]]
        if max(abs(R3[i][j] - (1 if i == j else 0)) for i in range(3) for j in range(3)) < 1e-6 and max(abs(M[i][3]) for i in range(3)) < 1e-6: return s
        s = dict(s)
        for k in ("c", "a", "b"):
            if k in s and isinstance(s[k], list) and (s["type"] != "tri" or k in "abc"): s[k] = [round(v, 4) for v in ap(M, s[k][:3])]
        if s["type"] == "tri" and "c" in s: pass
        if "pts" in s: s["pts"] = [[round(v, 4) for v in ap(M, p[:3])] + [p[3]] for p in s["pts"]]
        if "seat" in s and "from" in s["seat"]: s["seat"] = {**s["seat"], "from": [round(v, 4) for v in ap(M, s["seat"]["from"])]}
        if s["type"] == "ell":
            m = rotm(s.get("rot", [0, 0, 0])); R = [[sum(R3[i][k] * m[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
            s["rot"] = euler(R)
        return s

def r4(v):
    if isinstance(v, float): return round(v, 4)
    if isinstance(v, list): return [r4(x) for x in v]
    if isinstance(v, dict): return {k: r4(x) for k, x in v.items()}
    return v

# ---- shape makers (posed coordinates) ----
def ell(id, c, r, color, k=None, bone="body", rot=None, mirror=False, **kw):
    s = {"id": id, "type": "ell", "bone": bone, "c": c, "r": r, "k": k if k is not None else min(r) * .45, "color": color}
    if rot: s["rot"] = rot
    if mirror: s["mirror"] = True
    s.update(kw); return s
def sph(id, c, r, color, k=None, bone="body", mirror=False, **kw):
    s = {"id": id, "type": "sphere", "bone": bone, "c": c, "r": r, "k": k if k is not None else r * .4, "color": color}
    if mirror: s["mirror"] = True
    s.update(kw); return s
def cone(id, a, b, ra, rb, color, k=None, bone="body", mirror=False, **kw):
    s = {"id": id, "type": "cone", "bone": bone, "a": a, "b": b, "ra": ra, "rb": rb, "k": k if k is not None else min(ra, rb) * .5, "color": color}
    if mirror: s["mirror"] = True
    s.update(kw); return s
def tube(id, pts, color, k=None, bone="body", mirror=False, **kw):
    s = {"id": id, "type": "tube", "bone": bone, "pts": pts, "k": k if k is not None else min(p[3] for p in pts) * .5, "color": color}
    if mirror: s["mirror"] = True
    s.update(kw); return s
def tri(id, a, b, c, r, color, k=None, bone="body", mirror=False, **kw):
    s = {"id": id, "type": "tri", "bone": bone, "a": a, "b": b, "c": c, "r": r, "k": k if k is not None else r * .8, "color": color}
    if mirror: s["mirror"] = True
    s.update(kw); return s

def lerp(a, b, t): return [a[i] + (b[i] - a[i]) * t for i in range(len(a))]
def add(a, d): return [a[i] + d[i] for i in range(3)]
def nrm(v): l = math.sqrt(sum(x * x for x in v)) or 1; return [x / l for x in v]
def sub(a, b): return [a[i] - b[i] for i in range(3)]

def hand(pre, bone, wrist, fwd, n, length, r, color, spread, curl=0.0, knuckle=None, nail=None, z0=0.0, mirror=True, side=None, k=None):
    """fingers: n tapered pills fanned across the hand (z), from a row at `wrist` along `fwd` (unit), each `length`
    long, radius r; curl (0..1) bends each finger down at its middle (a knuckle-walker's curled fingers)"""
    out = []
    side = side or [0, 0, 1]
    for j in range(n):
        t = (j - (n - 1) / 2) / max(1, (n - 1) / 2) if n > 1 else 0
        base = [wrist[0], wrist[1], wrist[2] + z0 + t * spread]
        L = length * (1 - 0.18 * abs(t))
        mid = add(base, [fwd[0] * L * .55, fwd[1] * L * .55 + 0, fwd[2] * L * .55 + t * spread * .25])
        if curl:
            tip = add(mid, [fwd[0] * L * .45 * (1 - curl), -L * .5 * curl + fwd[1] * L * .45 * (1 - curl), t * spread * .1])
        else:
            tip = add(mid, [fwd[0] * L * .45, fwd[1] * L * .45, fwd[2] * L * .45 + t * spread * .2])
        kk = k if k is not None else r * .45
        out.append(cone(f"{pre}{j}a", base, mid, r * 1.05, r * .95, color, k=kk, bone=bone, mirror=mirror))
        out.append(cone(f"{pre}{j}b", mid, tip, r * .95, r * .8, color, k=kk, bone=bone, mirror=mirror))
        if knuckle: out.append(sph(f"{pre}{j}k", mid, r * 1.12, knuckle, k=r * .3, bone=bone, mirror=mirror))
    return out

def path_tail(P, n, rad, paint, z=0.0, pre="tail"):
    """THE TAIL SCULPTED down a rig's `path` (mammals.js pathChain: a quadratic B-spline through the polygon's mid points,
    one bone a span -- tail, tail1, ...): n cones a span; rad(t) the radius and paint(t) -> dict at t (0 root .. 1 tip)"""
    m = len(P) - 2
    M = [[(P[i][0] + P[i + 1][0]) / 2, (P[i][1] + P[i + 1][1]) / 2] for i in range(len(P) - 1)]
    out = []
    for i in range(m):
        A = P[0] if i == 0 else M[i]; B = P[-1] if i == m - 1 else M[i + 1]; C = P[i + 1]
        q = lambda t: [(1 - t) ** 2 * A[j] + 2 * t * (1 - t) * C[j] + t * t * B[j] for j in range(2)]
        bone = pre if i == 0 else f"{pre}{i}"
        for j in range(n):
            t0, t1 = j / n, (j + 1) / n
            g0, g1 = (i + t0) / m, (i + t1) / m
            a, b = q(t0), q(t1)
            ra, rb = rad(g0), rad(g1)
            s = {"id": f"{bone}S{j}", "type": "cone", "bone": bone, "a": [a[0], a[1], z], "b": [b[0], b[1], z], "ra": ra, "rb": rb,
                 "k": 0.4 * min(ra, rb), "kc": 0.12 * min(ra, rb)}
            s.update(paint((g0 + g1) / 2))
            out.append(s)
    return out

def tail_point(P, g):
    """the point at g (0..1, by span) along the same B-spline"""
    m = len(P) - 2
    M = [[(P[i][0] + P[i + 1][0]) / 2, (P[i][1] + P[i + 1][1]) / 2] for i in range(len(P) - 1)]
    i = min(m - 1, int(g * m)); t = g * m - i
    A = P[0] if i == 0 else M[i]; B = P[-1] if i == m - 1 else M[i + 1]; C = P[i + 1]
    return [(1 - t) ** 2 * A[j] + 2 * t * (1 - t) * C[j] + t * t * B[j] for j in range(2)]
