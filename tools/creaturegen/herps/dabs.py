# dabs.py (2026-11-21) -- a coat's marks written as `dabs` shapes (bodyspec.js header, sculpt.js layDabs): ONE shape a
# run of marks, each a row of a few numbers, laid on the skin by the engine when the body is meshed -- where the
# painters (hlib.Painter, lizlib.Marks, snakelib.Snake) used to probe the skin themselves and write an ellipsoid a mark.
#
#   M = Dabs(axis=[[x, y, z, r], ...] (front first), aspect=1, reach=.5, id="pz", soft=None)    a curved axis (a snake's)
#   M = Dabs(axis_fn=lambda x: [x, y, z], ...)   a STRAIGHT one along x (a lizard's): a ray from axis_fn(x) square to x is
#                 written as a row [x, phi, ...], any other ray as itself; the axis written as the polyline the rows need
#   M.spot(s, phi, la, lr, color, rot=0, when=None, kc=None, depth=None, dep=None, box=False, bone=None)   on the axis
#                 (depth: a share of R; dep: metres -- either only where the set's rule would not give it)
#   M.ray(o, d, la, lr, color, along=None, r=None, ...)          a ray of its own (a mark on the head)
#   M.ring(s0, s1, color, ...)   M.stroke([(s, phi), ...], w, color, ...)   M.rays([(o, d), ...], w, color, ...)
#   M.shapes()  -> the dabs shapes: one a `when` (and mirror), in the order first met, the marks in theirs (a later one
#                 over an earlier), each in its commonest colour (a row names its own only when it differs)
import math
from collections import Counter

def _r(v, n=6):
    if isinstance(v, float): return round(v, n)
    if isinstance(v, (list, tuple)): return [_r(x, n) for x in v]
    return v

class Dabs:
    def __init__(self, axis=None, axis_fn=None, aspect=None, up=None, reach=None, id="pz", bone="body", soft=None, depth=None):
        self.axis, self.axis_fn, self.aspect, self.up, self.reach, self.id, self.bone, self.soft = axis, axis_fn, aspect, up, reach, id, bone, soft
        self.depth = depth   # (the set's depth rule: a share of R, or [f, m, g] -- sculpt.js layDabs)
        self.along = [1, 0, 0] if axis_fn else None
        self.M = []   # (when, colour, mark: a row without its colour or an object, extra: {kc, depth, box, bone})

    def _ov(self, kc=None, depth=None, box=False, bone=None, dep=None):
        o = {}
        if kc is not None: o["kc"] = _r(kc)
        if depth is not None: o["depth"] = _r(depth, 4)
        if dep is not None: o["depth"] = [0, _r(dep)]   # (a mark's own depth in metres)
        if box: o["box"] = True
        if bone == "head" and self.bone != "head": o["bone"] = bone   # (the pictures' baker reads a mark's part from it)
        return o

    def _on_axis(self, o, d):
        """a ray from the straight axis square to x: its (x, phi), else None"""
        if not self.axis_fn or abs(d[0]) > 1e-9: return None
        a = self.axis_fn(o[0])
        if max(abs(a[k] - o[k]) for k in range(3)) > 1e-9: return None
        return o[0], math.degrees(math.atan2(d[2], d[1]))

    def spot(self, s, phi, la, lr, color, rot=0, when=None, mirror=False, **ov):
        self.M.append(((when, mirror), color, ["row", _r(s, 5), _r(phi, 2), _r(la), _r(lr), _r(rot, 2)], self._ov(**ov)))
    def ray(self, o, d, la, lr, color, along=None, r=None, when=None, rot=0, mirror=False, **ov):
        sp = self._on_axis(o, d) if (along is None or list(along) == [1, 0, 0]) and not rot else None
        if sp: return self.spot(sp[0], sp[1], la, lr, color, when=when, mirror=mirror, **ov)
        m = {"o": _r(list(o)), "d": _r(list(d), 5), "la": _r(la), "lr": _r(lr)}
        if along is not None and list(along) != [1, 0, 0]: m["along"] = _r(list(along), 5)
        if r is not None: m["r"] = _r(r)
        if rot: m["rot"] = _r(rot, 2)
        self.M.append(((when, mirror), color, m, self._ov(**ov)))
    def ring(self, s0, s1, color, when=None, kc=None, bone=None, mirror=False):
        self.M.append(((when, mirror), color, {"ring": [_r(s0, 5), _r(s1, 5)]}, self._ov(kc=kc, bone=bone)))
    def stroke(self, pts, w, color, when=None, kc=None, bone=None, mirror=False):
        self.M.append(((when, mirror), color, {"stroke": [[_r(s, 5), _r(p, 2)] for s, p in pts], "w": _r(w)}, self._ov(kc=kc, bone=bone)))
    def rays(self, rays, w, color, when=None, kc=None, bone=None, mirror=False):
        on = [self._on_axis(o, d) for o, d in rays]
        if all(on): return self.stroke(on, w, color, when=when, kc=kc, bone=bone, mirror=mirror)
        self.M.append(((when, mirror), color, {"rays": [[_r(list(o)), _r(list(d), 5)] for o, d in rays], "w": _r(w)}, self._ov(kc=kc, bone=bone)))

    def _straight_axis(self):
        """the polyline over x the rows need: the axis at every row's x, the points a straight line would pass dropped"""
        xs = set()
        for _, _, m, _ in self.M:
            if isinstance(m, list): xs.add(m[1])
            elif "stroke" in m: xs.update(s for s, _ in m["stroke"])
        P = [list(self.axis_fn(x)) for x in sorted(xs, reverse=True)]   # (front first)
        if len(P) < 2: P = P + [[P[0][0] - 1e-3] + P[0][1:]] if P else []
        keep = [0, len(P) - 1]
        def dp(i, j):
            a, b = P[i], P[j]; best, bk = 0, None
            for k in range(i + 1, j):
                t = (P[k][0] - a[0]) / ((b[0] - a[0]) or 1e-12)
                e = max(abs(P[k][c] - (a[c] + (b[c] - a[c]) * t)) for c in (1, 2))
                if e > best: best, bk = e, k
            if bk is not None and best > 2e-6: keep.append(bk); dp(i, bk); dp(bk, j)
        dp(0, len(P) - 1)
        return [_r(P[k]) for k in sorted(set(keep))]

    def shapes(self):
        groups = []   # (one a `when` -- marks under different ones are never shown together but with the ungated: those
        for m in self.M:   #  only change places, a head's against a back's, so a script alternating sides makes no more sets)
            g = next((g for g in groups if g[0] == m[0]), None)
            if not g: groups.append(g := (m[0], []))
            g[1].append(m)
        out = []
        for gi, ((when, mirror), ms) in enumerate(groups):
            col = Counter(m[1] for m in ms).most_common(1)[0][0]
            marks = []
            for _, c, m, ov in ms:
                if isinstance(m, list):   # [s, phi, la, lr, rot, colour, {extra}] -- trailing defaults dropped
                    row = m[1:] + [c if c != col else None, ov or None]
                    while row[-1] is None or (len(row) == 5 and row[-1] == 0): row.pop()
                    marks.append(row)
                else:
                    o = dict(m); o.update(ov)
                    if c != col: o["color"] = c
                    marks.append(o)
            q = {"id": self.id + (str(gi) if len(groups) > 1 else ""), "type": "dabs", "color": col}
            if when: q = {"when": when, **q}
            if self.bone != "body": q["bone"] = self.bone
            if mirror: q["mirror"] = True
            if self.soft is not None: q["soft"] = self.soft
            if self.depth is not None: q["depth"] = self.depth
            if (self.axis is not None or self.axis_fn) and any(isinstance(m, list) or "ring" in m or "stroke" in m for m in marks):
                q["axis"] = self.axis if self.axis is not None else self._straight_axis()
                if self.along: q["along"] = self.along
                if self.up: q["up"] = self.up
                if self.aspect not in (None, 1): q["aspect"] = _r(self.aspect, 4)
            if self.reach: q["reach"] = _r(self.reach, 4)
            q["marks"] = marks
            out.append(q)
        return out
