#!/usr/bin/env python3
"""slim.py -- fewer shapes for the same animal (2026-11-21).

Three kinds of over-built shapes, each made with far fewer pieces and the same outline:

  fins     a flat fin authored as a fan of `tri`s (dorsal0..dorsal41, caudal0.., anal0..): the fan's outline traced back
           from its triangles, simplified (Douglas-Peucker, `--tol` of the fin's size) and cut again into triangles
           (ear clipping) -- a carp's dorsal from 42 triangles to about 10; only sheets that lie flat are touched
  tufts    a tuft of thin `horn` strands (earTuft0..30): every k-th kept, a little thicker, so a tuft is ~8 strands
  (the pieces kept keep their ids -- brush0, brush2, ... -- so a kin's `drop` of brush1[0-5] still shortens the tail)
  chains   a run of `ell`s along a tail (brush0..15): every other one kept, each drawn longer and a bit fuller so the
           smooth blend (`k`) still closes the gaps -- a squirrel's brush from 16 pieces to 8

  python3 slim.py                     every creature asset (assets/creatures/**.json): report what would change
  python3 slim.py --write [names]     write them (names: the files' stems -- carp squirrel ...; none: all)
  python3 slim.py --only fins ...     one kind only (fins | tufts | chains)
"""
import json, math, os, re, sys, glob
from collections import defaultdict

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../assets")) + "/"
TOL = .02          # (of the fin's size: how far the simpler outline may stray)
TUFT_MIN, TUFT_KEEP = 12, 8
CHAIN_MIN = 10

def sub(a, b): return [a[i] - b[i] for i in range(3)]
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def norm(a): l = math.sqrt(dot(a, a)) or 1; return [v / l for v in a]
def r4(v): return round(v, 4)

# ---- FINS -------------------------------------------------------------------------------------------------------------
def plane(pts):
    """a plane through the points if they lie in one: origin, u, v, normal -- else None"""
    o = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
    n = None
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            c = cross(sub(pts[i], o), sub(pts[j], o))
            if n is None or dot(c, c) > dot(n, n): n = c
    if not n or dot(n, n) < 1e-14: return None
    n = norm(n); size = max(math.dist(p, o) for p in pts)
    if max(abs(dot(sub(p, o), n)) for p in pts) > size * .02: return None
    u = norm(sub(max(pts, key=lambda p: math.dist(p, o)), o)); v = cross(n, u)
    return o, u, v, n

def loops(tris):
    """the outline(s) of a set of triangles: the edges only one triangle has, chained"""
    key = lambda p: tuple(round(x, 5) for x in p)
    cnt = defaultdict(int); pos = {}
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            ka, kb = key(a), key(b); pos[ka] = a; pos[kb] = b
            cnt[frozenset((ka, kb))] += 1
    nxt = defaultdict(list)
    for e, c in cnt.items():
        if c == 1 and len(e) == 2:
            a, b = tuple(e); nxt[a].append(b); nxt[b].append(a)
    if any(len(v) != 2 for v in nxt.values()): return None      # (not a clean sheet: left alone)
    out, seen = [], set()
    for s in list(nxt):
        if s in seen: continue
        lp, prev, cur = [s], None, s; seen.add(s)
        while True:
            a, b = nxt[cur]; nx = b if a == prev else a
            if nx == s: break
            if nx in seen: return None
            lp.append(nx); seen.add(nx); prev, cur = cur, nx
        out.append([pos[k] for k in lp])
    return out

def dp(pts, tol):
    """Douglas-Peucker on a closed 2-D loop"""
    if len(pts) < 5: return pts
    i0 = 0; i1 = max(range(len(pts)), key=lambda i: math.dist(pts[i], pts[0]))
    def run(a):
        if len(a) < 3: return a
        p, q = a[0], a[-1]; d = math.dist(p, q) or 1e-9
        far, fi = -1, 0
        for i in range(1, len(a) - 1):
            x = abs((q[0] - p[0]) * (p[1] - a[i][1]) - (p[0] - a[i][0]) * (q[1] - p[1])) / d
            if x > far: far, fi = x, i
        if far <= tol: return [p, q]
        return run(a[:fi + 1])[:-1] + run(a[fi:])
    A = run(pts[i0:i1 + 1]); B = run(pts[i1:] + [pts[0]])
    return A[:-1] + B[:-1]

def area(P): return sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P))) / 2

def earclip(P):
    """triangles (index triples) of a simple 2-D polygon"""
    idx = list(range(len(P)))
    if area(P) < 0: idx.reverse()
    def inside(p, a, b, c):
        d1 = (p[0] - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (p[1] - b[1])
        d2 = (p[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (p[1] - c[1])
        d3 = (p[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (p[1] - a[1])
        return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))
    out, guard = [], 0
    while len(idx) > 3 and guard < 5000:
        guard += 1; n = len(idx); cut = False
        for k in range(n):
            i, j, l = idx[k - 1], idx[k], idx[(k + 1) % n]
            a, b, c = P[i], P[j], P[l]
            if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) <= 1e-12: continue
            if any(inside(P[m], a, b, c) for m in idx if m not in (i, j, l)): continue
            out.append((i, j, l)); idx.pop(k); cut = True; break
        if not cut: return None
    out.append(tuple(idx)); return out

def slim_fins(shapes):
    groups = defaultdict(list)
    for i, s in enumerate(shapes):
        if s.get("type") == "tri" and s.get("id") and re.fullmatch(r"[A-Za-z]+\d+", s["id"]):
            g = (re.sub(r"\d+$", "", s["id"]), s.get("bone"), json.dumps(s.get("color")), json.dumps(s.get("pat")), s.get("mirror"), s.get("op"))
            groups[g].append(i)
    drop, add, notes = set(), {}, []
    for g, ix in groups.items():
        if len(ix) < 8: continue
        tris = [[shapes[i]["a"], shapes[i]["b"], shapes[i]["c"]] for i in ix]
        pts = [p for t in tris for p in t]; pl = plane(pts)
        if not pl: continue
        L = loops(tris)
        if not L: continue
        o, u, v, n = pl; size = max(math.dist(p, o) for p in pts)
        new = []
        for lp in L:
            P2 = [(dot(sub(p, o), u), dot(sub(p, o), v)) for p in lp]
            S = dp(P2, size * TOL)
            if len(S) < 3: continue
            T = earclip(S)
            if not T: new = None; break
            back = lambda q: [r4(o[k] + u[k] * q[0] + v[k] * q[1]) for k in range(3)]
            new += [[back(S[a]), back(S[b]), back(S[c])] for a, b, c in T]
        if not new or len(new) >= len(ix): continue
        base = shapes[ix[0]]
        add[ix[0]] = [{**base, "id": shapes[ix[k]]["id"], "a": t[0], "b": t[1], "c": t[2]} for k, t in enumerate(new)]   # (the first ids kept: unique still)
        drop.update(ix); notes.append(f"{g[0]} {len(ix)}->{len(new)}")
    if not drop: return None, []
    out = []
    for i, s in enumerate(shapes):
        if i in add: out += add[i]
        elif i not in drop: out.append(s)
    return out, notes

# ---- TUFTS ------------------------------------------------------------------------------------------------------------
def slim_tufts(shapes):
    groups = defaultdict(list)
    for i, s in enumerate(shapes):
        if s.get("type") == "horn" and s.get("strand") and s.get("id") and re.fullmatch(r"[A-Za-z]+\d+", s["id"]):
            groups[(re.sub(r"\d+$", "", s["id"]), s.get("bone"))].append(i)
    keep, drop, notes = {}, set(), []
    for g, ix in groups.items():
        if len(ix) < TUFT_MIN: continue
        step = len(ix) / TUFT_KEEP; kept = sorted({ix[min(len(ix) - 1, int(k * step + step / 2))] for k in range(TUFT_KEEP)})
        f = math.sqrt(len(ix) / len(kept))
        for n, i in enumerate(kept):
            s = shapes[i]; keep[i] = {**s, "pts": [[*p[:3], r4(p[3] * f)] for p in s["pts"]]}
        drop.update(i for i in ix if i not in keep); notes.append(f"{g[0]} {len(ix)}->{len(kept)}")
    if not notes: return None, []
    return [keep.get(i, s) for i, s in enumerate(shapes) if i not in drop], notes

# ---- CHAINS -----------------------------------------------------------------------------------------------------------
def slim_chains(shapes):
    groups = defaultdict(list)
    for i, s in enumerate(shapes):
        if s.get("type") == "ell" and s.get("id") and re.fullmatch(r"(brush|plume|tuft)\d+", s["id"]):
            groups[re.sub(r"\d+$", "", s["id"])].append(i)
    keep, drop, notes = {}, set(), []
    for g, ix in groups.items():
        if len(ix) < CHAIN_MIN: continue
        ix = sorted(ix, key=lambda i: int(re.search(r"\d+$", shapes[i]["id"]).group()))
        kept = ix[::2] if (len(ix) - 1) % 2 == 0 else ix[::2] + [ix[-1]]
        for n, i in enumerate(kept):
            s = shapes[i]; r = s["r"]
            keep[i] = {**s, "r": [r4(r[0] * 1.45), r4(r[1] * 1.12), r4(r[2] * 1.12)], **({"k": r4(s["k"] * 1.4)} if s.get("k") else {})}
        drop.update(i for i in ix if i not in keep); notes.append(f"{g} {len(ix)}->{len(kept)}")
    if not notes: return None, []
    return [keep.get(i, s) for i, s in enumerate(shapes) if i not in drop], notes

KINDS = {"fins": slim_fins, "tufts": slim_tufts, "chains": slim_chains}

def main(argv):
    write = "--write" in argv; argv = [a for a in argv if a != "--write"]
    only = None
    if "--only" in argv: k = argv.index("--only"); only = argv[k + 1]; del argv[k:k + 2]
    names = set(argv)
    total = [0, 0]
    for f in sorted(glob.glob(ROOT + "creatures/**/*.json", recursive=True)):
        stem = os.path.basename(f)[:-5]
        if names and stem not in names: continue
        d = json.load(open(f)); sc = d.get("sculpt")
        if not isinstance(sc, dict) or not isinstance(sc.get("shape"), list): continue
        shapes, notes, n0 = sc["shape"], [], len(sc["shape"])
        for kind, fn in KINDS.items():
            if only and kind != only: continue
            out, nn = fn(shapes)
            if out is not None: shapes, notes = out, notes + nn
        if not notes: continue
        total[0] += n0; total[1] += len(shapes)
        print(f"{f[len(ROOT):]}: {n0} -> {len(shapes)} shapes  ({', '.join(notes)})")
        if write:
            sc["shape"] = shapes
            raw = open(f).read(); ind = 1 if raw.startswith("{\n \"") else 2 if raw.startswith("{\n  \"") else None
            json.dump(d, open(f, "w"), indent=ind, ensure_ascii=False); open(f, "a").write("\n") if raw.endswith("\n") else None
    print(f"{total[0]} -> {total[1]} shapes" + ("" if write else "  (--write to write them)"))

if __name__ == "__main__":
    main(sys.argv[1:])
