# BURG HOHENZOLLERN (Hechingen, Zollernalb; rebuilt 1850-67 for Friedrich Wilhelm IV by Friedrich August Stüler, the
# fortifications by Moritz von Prittwitz) on the summit of the Hohenzollern, from the historicist castle's vocabulary
# (tools/archgen/historicism.py: crenellation, cone-turret, castle-tower and -- new here -- components/round-keep).
# THE FRAME: +x EAST, +z SOUTH, y up; the origin OpenStreetMap's point 48.32355 N, 8.96750 E, and the PLAN IS OSM's (ways
# 93612350 the castle wall with its bastions, 296628895/296628898/296628900 the main building, 282888746/282888748/
# 296628901/282888749/296628896 the Markgrafen-, Kaiser-, Bischofs-, Wart- and Michaelsturm, 282888752 the Christuskapelle,
# 282887645 St Michael's chapel, 275154208/275154209 the Adler- and the Torturm, 54228 the Rampenturm's ring and the
# Michaelsbastei, the service roads 275154210-218 for the approach). Heights from photographs (Wikimedia Commons, the
# aerials and the views from the south) and the clearances the roads need where they pass over one another.
# THE APPROACH (Prittwitz's serpentine): up the hill from the east to the ADLERTOR (y yA); through it, round the
# Wilhelmsturm on a ramp, back THROUGH THE ADLERTOR above the first passage; along the inner wall, round a second loop in
# the lower Zwinger and over a bridge across it into the RAMPENTURM yard (HV); the tunnel of the Rampenturm -- a full turn
# inside its ring, under the open turn above -- and out over its own entry, over a viaduct and the bridge to the
# TORTURM and the inner castle (G): three levels of bailey, a road that crosses itself three times.
# THE CASTLE: four ranges round the inner courtyard -- the north wing (Stammbaumhalle at its west end, the state rooms),
# the north-west range (the Grafensaal, rib vaulted on columns), the west range (the library, the Wartturm in the court
# angle), the south range (the king's and the queen's rooms, the Michaelsturm on its south front) -- the round towers in
# the angles (Kaiserturm, Bischofsturm with its square upper stage and spire, Markgrafenturm), the Christuskapelle east of
# the north wing and St Michael's chapel (the medieval castle's, the oldest building) east of the south range.
import os, json, math, re
from historicism import (write_components, write_castle_components, comp, parapets, flight, place, gable, POINTED, ROOT, r4)
parts = {}; build = []
def add(n, d):
    assert n not in parts, n
    parts[n] = d; build.append(n); return n
Q = math.pi / 2
FLAT = {"profile": "flat"}
SEG = {"profile": "segmental", "rise": 0.3}
SEMI = {"profile": "semicircular"}
PTD = {"profile": "pointed", "spread": 0.55}

# ------------------------------------------------------------------------------------------------ plane geometry
def area2(pts):
    """the engine's signed area (assemble planPoints): > 0 means it re-winds the outline"""
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
def outward(pts):
    """the outline wound as the engine keeps it (the outside on the right of every edge)"""
    return list(pts) if area2(pts) <= 0 else list(reversed(pts))
def inside(x, z, poly):
    c = False
    for i in range(len(poly)):
        (x0, z0), (x1, z1) = poly[i], poly[i - 1]
        if (z0 > z) != (z1 > z) and x < x0 + (x1 - x0) * (z - z0) / (z1 - z0): c = not c
    return c
def seg_dist(p, a, b):
    dx, dz = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dz * dz
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dz) / L2)) if L2 else 0.0
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dz)
def poly_dist(p, poly):
    return min(seg_dist(p, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))
def hull(pts):
    P = sorted(set((round(x, 3), round(z, 3)) for x, z in pts))
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0: hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]
def offset(poly, d):
    """each edge moved d outward (a convex outline grown; for d < 0 an outline inset) -- by its own winding"""
    P = outward(poly); n = len(P); out = []
    lines = []
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]; L = math.dist(a, b); ex, ez = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        nx, nz = -ez, ex                                # (right of a->b in x-east z-south: the outside)
        lines.append(((a[0] + nx * d, a[1] + nz * d), (ex, ez)))
    for i in range(n):
        (p, e), (q, f) = lines[i - 1], lines[i]
        den = e[0] * f[1] - e[1] * f[0]
        if abs(den) < 1e-9: out.append(q); continue
        t = ((q[0] - p[0]) * f[1] - (q[1] - p[1]) * f[0]) / den
        out.append((r4(p[0] + e[0] * t), r4(p[1] + e[1] * t)))
    return out
def clip(poly, f):
    """Sutherland-Hodgman: the part of the outline where f >= 0, f linear (drachenburg.py's)"""
    out = []
    for i in range(len(poly)):
        p, q = poly[i - 1], poly[i]; fp, fq = f(p), f(q)
        cut = lambda: (r4(p[0] + (q[0] - p[0]) * fp / (fp - fq)), r4(p[1] + (q[1] - p[1]) * fp / (fp - fq)))
        if fq >= 0:
            if fp < 0: out.append(cut())
            out.append(q)
        elif fp >= 0: out.append(cut())
    return out
def ngon(c, R, n):
    """the engine's regular polygon (planPoints `sides`): corner k at angle (k + .5) 2pi / n from +z"""
    return [(c[0] + R * math.sin((k + 0.5) * 2 * math.pi / n), c[1] + R * math.cos((k + 0.5) * 2 * math.pi / n)) for k in range(n)]
def bite(poly, labels, tower, tag):
    """the outline with the convex `tower` outline taken out of it, where the tower covers one corner or bites into one
    edge: the tower's own boundary takes the place of what it covers (its edges labelled `tag`: the faces against the tower)"""
    n, m = len(poly), len(tower)
    ev = []
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        for j in range(m):
            c, d = tower[j], tower[(j + 1) % m]
            den = (b[0] - a[0]) * (d[1] - c[1]) - (b[1] - a[1]) * (d[0] - c[0])
            if abs(den) < 1e-12: continue
            t = ((c[0] - a[0]) * (d[1] - c[1]) - (c[1] - a[1]) * (d[0] - c[0])) / den
            u = ((c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])) / den
            if 0 < t < 1 and 0 <= u <= 1: ev.append((i, t, j, (r4(a[0] + (b[0] - a[0]) * t), r4(a[1] + (b[1] - a[1]) * t))))
    assert len(ev) == 2, (tag, ev)
    if ev[0][0] == ev[1][0]:                         # (both on one edge: in at the nearer, out at the further)
        ent, ext = sorted(ev, key=lambda e: e[1])
    else:                                            # (a corner covered: the edge leaving it is where the outline comes out)
        ext, ent = (ev[0], ev[1]) if inside(*poly[ev[0][0]], tower) else (ev[1], ev[0])
    ie, te, je, N = ent; ix, tx, jx, X = ext
    out, lab = [X], [labels[ix]]
    k = (ix + 1) % n
    while True:
        out.append(poly[k]); lab.append(labels[k] if k != ie else labels[ie])
        if k == ie: break
        k = (k + 1) % n
    out.append(N); lab.append(tag)
    fwd = [tower[(je + 1 + q) % m] for q in range((jx - je) % m)]
    bwd = [tower[(je - q) % m] for q in range((je - jx) % m)]
    way = next(w for w in (fwd, bwd) if w and inside(*w[len(w) // 2], poly))
    for p in way: out.append((r4(p[0]), r4(p[1]))); lab.append(tag)
    return out, lab

def face_at(pts, i, x, z):
    """where (x, z) falls along face i of an outline as the engine keeps it: metres from the face's middle toward its end"""
    a, b = pts[i], pts[(i + 1) % len(pts)]; L = math.dist(a, b)
    return r4(((x - a[0]) * (b[0] - a[0]) + (z - a[1]) * (b[1] - a[1])) / L - L / 2)

# ------------------------------------------------------------------------------------------------ the levels
yA = 9.0                    # the lower Zwinger and the Adlertor's passage
DECK, HEAD = 0.7, 3.6       # a road's deck; the headroom under one road where another passes over it
CLEAR = DECK + HEAD
HW = 2.0                    # half a road's width (between its parapets)
PT = 0.35                   # a road parapet's thickness, and height over the road
PH = 1.0
RC, RR = (39.5, 21.5), 9.3  # the Rampenturm: its middle, the road's middle line round it
PITCH = 4.6                 # the helix's rise a turn
TH0, TH1 = 10.0, 45.0 - 720.0   # the helix from its foot (degrees, atan2(z, x) about RC, falling as it climbs) to its head
HMOUND = 2.0                # the hilltop the whole castle stands on
# the approach's own pieces (OSM's roads, in this frame) and their lengths; the heights follow from the crossings
S2 = [(69.8, 31.9), (65.1, 39.1), (64.5, 44.1), (67.4, 47.3), (72.6, 47.7), (77.3, 45.0), (79.1, 42.6), (81.0, 38.7), (80.9, 34.5), (79.5, 32.6)]
S3 = [(79.5, 32.6), (75.25, 29.4), (71.0, 26.2)]
S4 = [(71.0, 26.2), (65.3, 26.1), (58.1, 27.8), (51.6, 30.2), (46.2, 32.3), (41.2, 36.6), (40.6, 40.6), (41.2, 44.5), (44.8, 45.7), (48.6, 44.9), (53.8, 42.8), (57.0, 39.2), (57.7, 35.9), (56.1, 31.9)]
S5 = [(56.1, 31.9), (54.25, 29.05), (52.4, 26.2)]
plen = lambda P: sum(math.dist(P[i], P[i + 1]) for i in range(len(P) - 1))
def seg_cross(p, q, r, s):
    d = (q[0] - p[0]) * (s[1] - r[1]) - (q[1] - p[1]) * (s[0] - r[0])
    if abs(d) < 1e-9: return None
    t = ((r[0] - p[0]) * (s[1] - r[1]) - (r[1] - p[1]) * (s[0] - r[0])) / d
    u = ((r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])) / d
    return (t, u) if 0 <= t <= 1 and 0 <= u <= 1 else None
def along_at(P, X):
    """how far along the polyline P its crossing with the polyline X comes, and how far along X"""
    sp = 0.0
    for i in range(len(P) - 1):
        sx = 0.0
        for j in range(len(X) - 1):
            c = seg_cross(P[i], P[i + 1], X[j], X[j + 1])
            if c: return sp + c[0] * math.dist(P[i], P[i + 1]), sx + c[1] * math.dist(X[j], X[j + 1])
            sx += math.dist(X[j], X[j + 1])
        sp += math.dist(P[i], P[i + 1])
    raise ValueError("no crossing")
# S1 runs level through the Adlertor at yA; S2 climbs round the Wilhelmsturm to come back through the tower over it
S1 = [(80.7, 26.6), (69.8, 31.9)]
s13, s31 = along_at(S1, S3)
y2a, y2b = yA, yA + CLEAR - 0.15            # (S2's two ends)
g3 = 0.03                                   # (S3 a gentle rise through the tower)
assert y2b + g3 * s31 - yA >= CLEAR - 0.2, "S3 over S1"
y3b = y2b + g3 * plen(S3)
s45, s54 = along_at(S4, S5)
g4 = 0.095
y4b = y3b + g4 * plen(S4)
g5 = 0.03
assert (y4b + g5 * s54) - (y3b + g4 * s45) >= CLEAR, ("S5 over S4", (y4b + g5 * s54) - (y3b + g4 * s45))
HV = r4(y4b + g5 * plen(S5))               # the Rampenturm yard
HTOP = r4(HV + (TH0 - TH1) / 360 * PITCH)  # the helix's head
RT = r4(HTOP - 0.12)                        # the ring wall's top (the exit road just over it)
EXIT = [(59.7, 19.3), (62.5, 15.4), (61.1, 11.6), (56.1, 8.2)]
TOR_E, TOR_W = (45.84, 1.70), (39.64, 0.31)  # where the gate road meets the Torturm's east face and leaves its west face
BRIDGE = [(56.1, 8.2), (47.6, 2.1)]
G = round(HTOP + 0.075 * 52.0, 1)           # the inner castle: the exit run climbs ~7.5% to the Torturm
HILLW = round(min(G - 13.0, HV - 1.0), 1)   # the summit's rock under the inner castle's bastions (never showing in the Rampenturm yard)
print("HV", HV, "HTOP", HTOP, "G", G, "HILLW", HILLW); assert HILLW < HV - 0.5
print(f"levels: yA {yA}  S2 top {y2b:.2f}  S4 top {y4b:.2f}  HV {HV}  helix top {HTOP}  G {G}  hill {HILLW}")

# ------------------------------------------------------------------------------------------------ the zones
RING = [(-79.0, 2.3), (-61.9, 8.1), (-59.8, 5.3), (-34.0, 17.7), (-35.6, 20.2), (-30.8, 27.0), (-20.1, 26.3), (-15.3, 26.0), (5.3, 43.0), (36.5, 50.6), (37.2, 53.3),
        (48.9, 55.7), (57.5, 45.4), (61.4, 49.5), (67.9, 50.6), (72.2, 49.6), (75.2, 48.4), (78.5, 46.2), (81.1, 42.9), (82.7, 39.9), (82.7, 33.8), (81.4, 31.3),
        (78.3, 21.9), (84.8, 20.5), (73.8, 8.9), (69.9, 11.5), (56.6, -8.3), (60.6, -11.7), (54.8, -33.4), (33.3, -31.4), (33.8, -25.5), (-19.6, -45.5),
        (-23.6, -52.6), (-37.9, -57.3), (-52.2, -42.3), (-79.9, -32.1), (-74.7, -13.5)]
INNER_S = [(-18.6, 22.3), (-9.3, 27.7), (-0.3, 33.1), (3.5, 36.5), (11.6, 38.7), (20.7, 36.8), (26.8, 33.3), (32.5, 35.4), (67.9, 21.1), (73.0, 20.0), (75.0, 22.5), (78.3, 21.9)]
RAMP_R0 = 12.0              # (zone A's face round the Rampenturm: inside its ring wall, which stands 11.4 to 12.6)
arcA = [(r4(RC[0] + RAMP_R0 * math.cos(math.radians(a))), r4(RC[1] + RAMP_R0 * math.sin(math.radians(a)))) for a in range(-135, -50, 10)]
# the inner castle (A): the bastion ring west and north, the Neue Bastei, the Michaelsbastei, the Torturm's line
ZA = [(56.6, -8.3), (60.6, -11.7), (54.8, -33.4), (33.3, -31.4), (33.8, -25.5), (-19.6, -45.5), (-23.6, -52.6), (-37.9, -57.3), (-52.2, -42.3), (-79.9, -32.1),
      (-74.7, -13.5), (-79.0, 2.3), (-61.9, 8.1), (-59.8, 5.3), (-34.0, 17.7), (-35.6, 20.2), (-30.8, 27.0), (-20.1, 26.3), (-18.6, 22.3), (-9.3, 27.7), (-0.3, 33.1),
      (3.5, 36.5), (11.6, 38.7), (20.7, 36.8), (26.8, 33.3), (23.3, 25.2), (22.1, 23.3), (30.2, 15.0)] + arcA[1:] + [(42.9, 9.12), (46.77, -0.64), (48.4, -5.14)]
# the Rampenturm yard (B): between the inner castle, the Schnarrwacht and the inner wall over the lower Zwinger
ZB = [(56.6, -8.3), (48.4, -5.14), (46.77, -0.64), (42.9, 9.12)] + arcA[::-1][1:] + [(30.2, 15.0), (22.1, 23.3), (23.3, 25.2), (26.8, 33.3), (32.5, 35.4), (67.9, 21.1), (73.0, 20.0),
      (75.0, 22.5), (78.3, 21.9), (84.8, 20.5), (73.8, 8.9), (69.9, 11.5)]
# the lower Zwinger (C): between the inner wall and the outer ring, east of the Gartenbastei; the Adlertor in its east end
ZC = [(-18.6, 22.3), (-15.3, 26.0), (5.3, 43.0), (36.5, 50.6), (37.2, 53.3), (48.9, 55.7), (57.5, 45.4), (61.4, 49.5), (67.9, 50.6), (72.2, 49.6), (75.2, 48.4),
      (78.5, 46.2), (81.1, 42.9), (82.7, 39.9), (82.7, 33.8), (81.4, 31.3), (78.3, 21.9)] + INNER_S[::-1][1:-1]
for nm, Z, y in (("zone A", ZA, G), ("zone B", ZB, HV), ("zone C", ZC, yA)):
    add(nm, {"type": "prism", "plan": {"points": [list(p) for p in Z]}, "height": y, "flatRoof": False, "walked": True, "at": [[0, 0, 0, 0]],
             "_about": {"zone A": "the inner castle's platform: the bastions west and north (Scharfeck, Spitz, Fuchsloch), the Neue Bastei, the Michaelsbastei and the Gartenbastei, "
                                  "their walls rising sheer from the summit's rock -- the courtyard and the terraces round the castle at G",
                        "zone B": "the Rampenturm's yard under the inner castle's east front, behind the Schnarrwacht bastion: the road's middle level",
                        "zone C": "the lower Zwinger between the inner wall and the outer ring, the Adlertor at its east end: the road's lowest level"}[nm]})
# THE HILL: the hilltop under everything (a battered mound), and the summit's rock under the inner castle west and north,
# its foot battered out down the slope; neither must show inside the lower baileys
MOUND = hull([p for p in RING])
add("hilltop", {"type": "prism", "plan": {"points": [list(p) for p in offset(MOUND, 3.0)]}, "height": HMOUND, "flatRoof": False, "walked": True,
                "batter": {"out": 14, "power": 1}, "at": [[0, 0, 0, 0]], "_about": "the hill's top: the ground round the outer ring"})
SUMMIT_SRC = RING[RING.index((33.3, -31.4)):] + RING[:RING.index((-35.6, 20.2)) + 1]
SUMMIT = offset(hull(SUMMIT_SRC), 1.0)
SUMMIT_OUT = 18.0
add("summit", {"type": "prism", "plan": {"points": [list(p) for p in SUMMIT]}, "height": HILLW, "flatRoof": False, "walked": True,
               "batter": {"out": SUMMIT_OUT, "power": 1.3}, "at": [[0, 0, 0, 0]], "_about": "the summit's rock the inner castle's west and north bastions stand on"})
def hill_at(p):
    if inside(p[0], p[1], SUMMIT): return HILLW
    d = poly_dist(p, SUMMIT)
    return HILLW * (1 - (d / SUMMIT_OUT) ** (1 / 1.3)) if d < SUMMIT_OUT else 0.0     # (batterMesh: the foot d = out (1 - y / H) ^ power)
for p in ZC + [((ZC[i][0] + ZC[i + 1][0]) / 2, (ZC[i][1] + ZC[i + 1][1]) / 2) for i in range(len(ZC) - 1)]:
    assert hill_at(p) < yA - 0.2, ("the summit shows in the lower Zwinger", p, hill_at(p))

# ------------------------------------------------------------------------------------------------ the roads
def profile(depth, parapet=True):
    w, t = HW, PT
    if not parapet: return [[-w, -depth], [w, -depth], [w, 0], [-w, 0]]
    return [[-w - t, -depth], [w + t, -depth], [w + t, PH], [w, PH], [w, 0], [-w, 0], [-w, PH], [-w - t, PH]]
def graded(P, y0, y1):
    L = plen(P); s = 0.0; out = []
    for i, p in enumerate(P):
        if i: s += math.dist(P[i - 1], p)
        out.append([r4(p[0]), r4(y0 + (y1 - y0) * s / L), r4(p[1])])
    return out
ROADS = []
def road(name, path3, depth, about, parapet=True, step=0.8):
    ROADS.append(add(name, {"type": "sweep", "path": path3, "profile": profile(depth, parapet), "step": step, "_about": about}))
# the approach up the hillside from the east to the Adlertor's outer gate
APPROACH = [(122.0, -38.0), (119.0, -12.0), (110.0, 10.0), (98.0, 21.0), (86.8, 25.0), (79.6, 26.9)]
ap = graded(APPROACH[:-1], 0.0, yA) + [[79.6, yA, 26.9]]
ap[0][1] = -0.6
road("approach", ap, 14.0, "the road up the hillside from the east to the Adlertor, on its embankment between low walls")
road("ramp round the wilhelmsturm", graded(S2, y2a, y2b), y2b + 2, "the ramp round the Wilhelmsturm: out of the Adlertor's lower passage and up round the tower, back to the Adlertor")
road("adlertor upper passage", graded(S3, y2b, y3b), DECK, "the upper passage through the Adlertor, on a deck over the lower one")
road("zwinger ramp", graded(S4, y3b, y4b), y4b - yA + 1.0, "the ramp along the inner wall and round the second loop of the lower Zwinger")
road("zwinger bridge", graded(S5, y4b, HV), DECK, "the bridge over the ramp below it, into the Rampenturm's yard")
# THE RAMPENTURM: the helix, its first turn in the tunnel under the second (a deck), the second open to the sky
def helix_pts(a0, a1, y0, step=12.0):
    n = max(2, int(abs(a1 - a0) / step) + 1); out = []
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n; y = y0 + (a0 - a) / 360 * PITCH
        out.append([r4(RC[0] + RR * math.cos(math.radians(a))), r4(y), r4(RC[1] + RR * math.sin(math.radians(a)))])
    return out
TURN1 = TH0 - 360.0
road("rampenturm tunnel", [[52.4, HV, 26.2]] + helix_pts(TH0, TURN1, HV), PITCH + 1.0, "the first turn of the Rampenturm's road: the tunnel inside the ring, under the turn above", parapet=False)
road("rampenturm open turn", helix_pts(TURN1, TH1, HV + PITCH), DECK, "the second turn, open to the sky between the ring wall and the drum", parapet=False)
# out of the ring over its own entry, along the viaduct to the bridge and the Torturm
a1 = math.radians(TH1)
ex0 = [r4(RC[0] + RR * math.cos(a1)), HTOP, r4(RC[1] + RR * math.sin(a1))]
LEX = math.dist(ex0[::2], EXIT[0]) + plen(EXIT) + plen(BRIDGE)
gex = (G - HTOP) / (LEX + math.dist(BRIDGE[1], TOR_E))
def yex(s): return r4(HTOP + gex * s)
s_cross = math.dist(ex0[::2], (55.6, 22.3))
road("rampenturm exit", [ex0, [55.6, yex(s_cross), 22.3]], DECK, "out of the ring over the entry below it, on a deck")
s0 = s_cross; vi = [[55.6, yex(s0), 22.3]]
prev = (55.6, 22.3)
for p in EXIT:
    s0 += math.dist(prev, p); vi.append([p[0], yex(s0), p[1]]); prev = p
road("viaduct", vi, yex(s0) - HV + 1.0, "the road on its walled embankment north to the bridge")
yb0 = yex(s0)
road("torturm bridge", [[56.1, yb0, 8.2], [TOR_E[0], G, TOR_E[1]]], DECK, "the bridge to the Torturm")
add("bridge piers", {"type": "prism", "plan": {"rect": [2.0, 5.2]}, "height": r4(yb0 - DECK - HV), "flatRoof": True,
                     "at": [[r4(56.1 + (TOR_E[0] - 56.1) * f), HV, r4(8.2 + (TOR_E[1] - 8.2) * f), r4(math.atan2(-(TOR_E[1] - 8.2), TOR_E[0] - 56.1))] for f in (0.05, 0.5)],
                     "_about": "the bridge's piers in the yard"})
print(f"exit: HTOP {HTOP}  viaduct end {yb0}  G {G}  grade {gex:.3f}")


# ------------------------------------------------------------------------------------------------ the bastions' parapets
def runs(Z, keep):
    """the outline's edges kept by keep(a, b), as open runs of consecutive points"""
    n = len(Z); out = []; cur = None
    start = next((i for i in range(n) if not keep(Z[i - 1], Z[i])), 0)     # (begin after a dropped edge, so no run is split at the list's end)
    for k in range(n):
        i = (start + k) % n; a, b = Z[i], Z[(i + 1) % n]
        if keep(a, b):
            if cur is None: cur = [a]
            cur.append(b)
        elif cur: out.append(cur); cur = None
    if cur: out.append(cur)
    return out
def on(a, b, L):
    """is the edge a-b one of the polyline L's (either way)"""
    return any((a == L[i] and b == L[i + 1]) or (b == L[i] and a == L[i + 1]) for i in range(len(L) - 1))
BATTLEMENTS = []
def battlements(name, Z, y, keep, **kw):
    for k, R in enumerate(runs(Z, keep)):
        BATTLEMENTS.extend(parapets(add, f"{name} {k}", R, y, h=1.0, step=2.3, t=0.6, closed=False, **kw))
TORTURM = [(40.78, -2.86), (37.45, 6.38), (42.9, 9.12), (46.77, -0.64)]
TC = (sum(p[0] for p in TORTURM) / 4, sum(p[1] for p in TORTURM) / 4)
battlements("inner castle parapet", outward(ZA), G, lambda a, b: True, holes=[(TC, 6.2)])
battlements("rampenturm yard parapet", outward(ZB), HV, lambda a, b: on(a, b, INNER_S) or on(a, b, RING),
            gaps=[((53.3, 27.0), 6.0)])
ADLER = [(67.76, 29.33), (74.97, 22.46), (78.33, 21.94), (81.41, 31.32), (73.1, 33.45)]
AC = (sum(p[0] for p in ADLER) / 5, sum(p[1] for p in ADLER) / 5)
battlements("zwinger parapet", outward(ZC), yA, lambda a, b: on(a, b, RING), holes=[(AC, 7.6)])
# THE BARTIZANS on the bastions' salients: little round watch turrets corbelled out of the parapet's corner
SALIENTS = [((-79.9, -32.1), G), ((-79.0, 2.3), G), ((-37.9, -57.3), G), ((-23.6, -52.6), G), ((54.8, -33.4), G), ((60.6, -11.7), G), ((-30.8, 27.0), G),
            ((-52.2, -42.3), G), ((84.8, 20.5), HV), ((48.9, 55.7), yA), ((82.7, 39.9), yA), ((37.2, 53.3), yA)]
def into(p, Z, d):
    """the corner p of the outline Z, moved d in along its bisector"""
    i = Z.index(p); a, b = Z[i - 1], Z[(i + 1) % len(Z)]
    u = ((a[0] - p[0]) / math.dist(a, p) + (b[0] - p[0]) / math.dist(b, p), (a[1] - p[1]) / math.dist(a, p) + (b[1] - p[1]) / math.dist(b, p))
    L = math.hypot(*u) or 1
    c = (p[0] + u[0] / L * d, p[1] + u[1] / L * d)
    if not inside(c[0], c[1], Z): c = (p[0] - u[0] / L * d, p[1] - u[1] / L * d)
    return (r4(c[0]), r4(c[1]))
BART = []
for k, (p, y) in enumerate(SALIENTS):
    Z = ZA if y == G else ZB if y == HV else ZC
    c = into(p, Z, 0.9)
    BART.append(add(f"bartizan {k}", comp("cone-turret", {"sides": 10, "R": 1.5, "H": 4.2, "storeys": 1, "door": "no", "corH": 0.5, "corOut": 0.15, "capR": 1.85, "capRise": 3.4, "finial": 0.7},
                                       [[c[0], r4(y - 1.2), c[1], 0]], _about="a watch turret corbelled out of the bastion's salient")))
    BART.append(add(f"bartizan {k} corbel", {"type": "column", "radius": 0.5, "height": 1.8, "sides": 10, "taper": 3.0, "at": [[c[0], r4(y - 3.0), c[1], 0]],
                                             "_about": "the corbel cone it is carried on"}))

# ------------------------------------------------------------------------------------------------ the bastions' faces
# The bastion walls are the zones' own sides, 10 to 30 m of sheer stone: they get a battered plinth a few metres over
# the ground before them, a string course under the parapet, pilaster strips on the long faces and a gun loop in each
# bay between them -- all kept clear of the road wherever it runs along a wall, and of the gate towers and the
# Rampenturm's ring. (Their stone, rougher and darker than the palace's: the finish.)
def _road_samples():
    out = []
    for nm in ROADS:
        P3 = parts[nm]["path"]
        for a, b in zip(P3, P3[1:]):
            n = max(1, int(math.dist((a[0], a[2]), (b[0], b[2])) / 1.0))
            out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n, a[2] + (b[2] - a[2]) * k / n) for k in range(n + 1)]
    return out
ROAD_PTS = _road_samples()
def clear_of_road(p, y0, y1, d=3.8):
    """nothing of the road within d of p (x, z) at a height from below y0 to over y1"""
    return not any(math.hypot(x - p[0], z - p[1]) < d and y0 - 1.5 < y < y1 + 3.0 for x, y, z in ROAD_PTS)
KEEP_OUT = [(TC, 9.0), (AC, 9.5), (RC, 15.0), ((72.6, 40.8), 6.0)]      # (the Torturm and the gatehouse, the Adlertor, the Rampenturm, the Wilhelmsturm)
def ground_before(p):
    """the ground just outside a bastion's face: a lower yard's floor, else the hill's"""
    if inside(p[0], p[1], ZB): return HV
    if inside(p[0], p[1], ZC): return yA
    return max(HMOUND, hill_at(p))
BFACES = []             # (zone top, a, b, along, out) for every face of a bastion that looks out over lower ground
for Z, top, keep in ((ZA, G, lambda a, b: True), (ZB, HV, lambda a, b: on(a, b, INNER_S) or on(a, b, RING)), (ZC, yA, lambda a, b: on(a, b, RING))):
    for i in range(len(Z)):
        a, b = Z[i], Z[(i + 1) % len(Z)]
        if not keep(a, b) or a in arcA or b in arcA: continue
        L = math.dist(a, b)
        if L < 2.5: continue
        u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L); n = (u[1], -u[0])
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if inside(m[0] + n[0] * 0.3, m[1] + n[1] * 0.3, Z): n = (-n[0], -n[1])
        if inside(m[0] + n[0] * 0.6, m[1] + n[1] * 0.6, ZA) and Z is not ZA: continue
        BFACES.append((top, a, b, L, u, n))
def free(p, y0, y1):
    return all(math.dist(p, c) > r for c, r in KEEP_OUT) and clear_of_road(p, y0, y1)
plinth, course, pil, loops, loopk = {}, [], {}, [], []      # (plinth and pilasters by height, every piece a copy of one part)
PIECE = 3.0
for top, a, b, L, u, n in BFACES:
    yaw = r4(math.atan2(-u[1], u[0]))
    samples = [(a[0] + u[0] * t, a[1] + u[1] * t) for t in [L * k / max(1, int(L / 1.5)) for k in range(int(L / 1.5) + 1)]]
    gmax = max(ground_before((q[0] + n[0] * 1.0, q[1] + n[1] * 1.0)) for q in samples)
    yc = top - 1.9                                                   # (the string course)
    py = math.ceil((gmax + 2.6) * 2) / 2                             # (the plinth's top, to half a metre)
    npc = max(1, math.ceil((L + 0.3) / PIECE)); sp = (L + 0.3 - PIECE) / max(1, npc - 1) if npc > 1 else 0.0
    for k in range(npc):
        t = -0.15 + PIECE / 2 + sp * k if npc > 1 else L / 2
        q = (a[0] + u[0] * t, a[1] + u[1] * t); ends = [(a[0] + u[0] * (t + e), a[1] + u[1] * (t + e)) for e in (-PIECE / 2, 0, PIECE / 2)]
        if py < yc - 4.0 and all(free(e, 0, py) for e in ends):
            plinth.setdefault(py, []).append([r4(q[0] + n[0] * 0.25), 0.0, r4(q[1] + n[1] * 0.25), yaw])
        if all(free(e, yc, yc + 0.35) for e in ends):
            course.append([r4(q[0] + n[0] * 0.12), r4(yc), r4(q[1] + n[1] * 0.12), yaw])
    # pilaster strips every ~11 m on the long faces, a gun loop in the middle of each bay
    if L > 13.0:
        nb = max(2, round(L / 11.0)); step = L / nb
        for k in range(1, nb):
            q = (a[0] + u[0] * step * k, a[1] + u[1] * step * k)
            if free(q, 0, yc):
                pil.setdefault(r4(yc), []).append([r4(q[0] + n[0] * 0.2), 0.0, r4(q[1] + n[1] * 0.2), yaw])
    nb = max(1, round(L / 11.0)) if L > 5.0 else 0
    for k in range(nb):
        q = (a[0] + u[0] * L * (k + 0.5) / nb, a[1] + u[1] * L * (k + 0.5) / nb); yl = top - 4.6
        if yl > gmax + 2.5 and free(q, yl, yl + 1.5):
            loops.append([r4(q[0] + n[0] * 0.04), r4(yl + 0.35), r4(q[1] + n[1] * 0.04), yaw])
            loopk.append([r4(q[0] + n[0] * 0.04), r4(yl), r4(q[1] + n[1] * 0.04), yaw])
for k, h in enumerate(sorted(plinth)):
    add(f"bastion plinth {k}", {"type": "prism", "plan": {"rect": [PIECE, 0.5]}, "height": h, "flatRoof": True, "batter": {"out": 0.7, "power": 1}, "at": plinth[h]} |
        ({"_about": "THE BASTIONS' BATTERED PLINTH: a skirt of rough dark stone, its top a little over the ground before the face, in pieces clear of the road "
                    "(a part for each height, a copy for every 3 m)"} if not k else {}))
add("bastion course", {"type": "box", "width": PIECE, "length": 0.45, "height": 0.35, "at": course, "_about": "the string course under the bastions' parapets"})
for k, h in enumerate(sorted(pil)):
    add(f"bastion pilaster {k}", {"type": "box", "width": 1.5, "length": 0.4, "height": h, "at": pil[h]} | ({"_about": "pilaster strips up the long bastion faces to the string course"} if not k else {}))
add("bastion gun loops", {"type": "box", "width": 0.16, "length": 0.1, "height": 1.3, "at": loops, "_about": "the gun loops: a tall slit over a round-ish mouth (keyhole loops)"})
add("bastion gun loop mouths", {"type": "box", "width": 0.42, "length": 0.1, "height": 0.36, "at": loopk})
print(f"bastion faces {len(BFACES)}: plinth {sum(map(len, plinth.values()))} in {len(plinth)}, course {len(course)}, pilasters {sum(map(len, pil.values()))}, loops {len(loops)}")

# ------------------------------------------------------------------------------------------------ the Rampenturm
RW_OUT = 12.6
ring_pts = ngon(RC, RW_OUT, 40)
def circle_cross(a, b, c, R):
    """where the segment a-b crosses the circle (c, R)"""
    dx, dz = b[0] - a[0], b[1] - a[1]; fx, fz = a[0] - c[0], a[1] - c[1]
    A = dx * dx + dz * dz; B = 2 * (fx * dx + fz * dz); C = fx * fx + fz * fz - R * R
    disc = math.sqrt(B * B - 4 * A * C)
    for t in ((-B - disc) / (2 * A), (-B + disc) / (2 * A)):
        if 0 <= t <= 1: return (a[0] + dx * t, a[1] + dz * t)
portal = circle_cross((52.4, 26.2), (RC[0] + RR * math.cos(math.radians(TH0)), RC[1] + RR * math.sin(math.radians(TH0))), RC, RW_OUT)
fi = min(range(40), key=lambda i: seg_dist(portal, ring_pts[i], ring_pts[(i + 1) % 40]))
# (one face of the forty is too narrow for the portal: three are merged into one straight face across it)
ring_pl = outward([p for k, p in enumerate(ring_pts) if k not in (fi, (fi + 1) % 40)])
fi = min(range(len(ring_pl)), key=lambda i: seg_dist(portal, ring_pl[i], ring_pl[(i + 1) % len(ring_pl)]))
add("rampenturm ring", {"type": "enclosure", "plan": {"points": [[r4(x - RC[0]), r4(z - RC[1])] for x, z in ring_pl]}, "thickness": 1.2, "height": r4(RT - HV), "glass": False, "interior": False,
                        "openings": [], "faces": {str(fi): [{"openings": [{"at": face_at(ring_pl, fi, *portal), "width": 4.8, "sill": 0, "springing": 3.4, "head": SEMI, "glass": False}]}]},
                        "courses": True, "at": [[RC[0], HV, RC[1], 0]],
                        "_about": "the Rampenturm's ring wall: the road goes in at the portal, once round inside it in the dark, once round on top and out over the portal"})
exit_x = circle_cross(ex0[::2], (55.6, 22.3), RC, RW_OUT - 0.3)
ARC_R = [(r4(RC[0] + RW_OUT * math.cos(math.radians(a))), r4(RC[1] + RW_OUT * math.sin(math.radians(a)))) for a in [-50 + 13.5 * k for k in range(21)]]
BATTLEMENTS.extend(parapets(add, "rampenturm battlements", ARC_R, RT, h=1.0, step=1.9, t=0.6, closed=False, gaps=[(exit_x, 6.4)]))
add("rampenturm drum", {"type": "enclosure", "plan": {"sides": 32, "radius": 7.3}, "thickness": 0.8, "height": r4(RT + 1.1 - HV), "glass": False, "interior": False,
                        "tiers": [{"h": 3.4, "openings": {"pattern": "1", "width": 0.9, "sill": 1.1, "springing": 2.5, "head": SEMI, "glass": False}}, {"openings": []}],
                        "faces": {str(k): [{"h": 3.4, "openings": []}, {"openings": []}] for k in range(32) if k % 4},
                        "courses": True, "at": [[RC[0], HV, RC[1], 0]], "_about": "the drum the road winds round: its light well open to the sky, windows from the tunnel into it"})
BATTLEMENTS.extend(parapets(add, "rampenturm drum battlements", ngon(RC, 7.35, 16), r4(RT + 1.1), h=0.8, step=1.6, t=0.45))
add("rampenturm well", {"type": "prism", "plan": {"sides": 32, "radius": 6.45}, "height": 0.06, "flatRoof": False, "walked": True, "at": [[RC[0], HV, RC[1], 0]],
                        "_about": "the grass at the light well's foot"})

# ------------------------------------------------------------------------------------------------ the Adlertor and the Wilhelmsturm
AD = outward(ADLER)
def face_of(P, p):
    i = min(range(len(P)), key=lambda i: seg_dist(p, P[i], P[(i + 1) % len(P)]))
    return i, face_at(P, i, *p)
def crossing(P, path):
    """where the polyline `path` crosses the outline P's edges: [(face, at, along the path)]"""
    out = []; s = 0.0
    for j in range(len(path) - 1):
        for i in range(len(P)):
            c = seg_cross(path[j], path[j + 1], P[i], P[(i + 1) % len(P)])
            if c: out.append((i, face_at(P, i, path[j][0] + (path[j + 1][0] - path[j][0]) * c[0], path[j][1] + (path[j + 1][1] - path[j][1]) * c[0]), s + c[0] * math.dist(path[j], path[j + 1])))
        s += math.dist(path[j], path[j + 1])
    return out
AH = 15.0
ad_open = {}
for f, a, s in crossing(AD, S1):
    ad_open.setdefault(f, []).append({"at": a, "width": 3.8, "sill": 0, "springing": 3.3, "head": PTD, "glass": False})
for f, a, s in crossing(AD, [(80.9, 33.2)] + S3[:1] + S3[1:] + [(69.3, 24.9)]):
    y = y2b + g3 * max(0.0, s - 2.0) - yA
    ad_open.setdefault(f, []).append({"at": a, "width": 4.2, "sill": r4(y), "springing": r4(y + 3.1), "head": PTD, "glass": False})
add("adlertor", {"type": "enclosure", "plan": {"points": [list(p) for p in AD]}, "thickness": 1.4, "height": AH, "glass": False, "interior": False,
                 "openings": [], "faces": {str(f): [{"openings": o}] for f, o in ad_open.items()}, "courses": True, "at": [[0, yA, 0, 0]],
                 "_about": "the ADLERTOR (Eagle Gate): the outer gate tower, the road through it twice -- below at the gate, above on its way back round from the Wilhelmsturm"})
add("adlertor roof deck", {"type": "prism", "plan": {"points": [list(p) for p in offset(AD, -1.0)]}, "height": 0.5, "flatRoof": True, "at": [[0, r4(yA + AH - 0.5), 0, 0]], "standsOn": ["adlertor"]})
add("adlertor machicolation", {"type": "prism", "plan": {"points": [list(p) for p in offset(AD, 0.45)]}, "height": 0.9, "flatRoof": True, "at": [[0, r4(yA + AH - 0.9), 0, 0]], "standsOn": ["adlertor"],
                               "_about": "the corbelled course round its head"})
BATTLEMENTS.extend(parapets(add, "adlertor battlements", offset(AD, 0.45), r4(yA + AH), h=1.3, step=1.7, t=0.55))
# its outer face: the gate under a tall pointed arch, the knight on horseback in the tympanum, the eagle's arms over it
fE, aE, _ = crossing(AD, S1)[0]
pE, qE = AD[fE], AD[(fE + 1) % len(AD)]
LE = math.dist(pE, qE); ue = ((qE[0] - pE[0]) / LE, (qE[1] - pE[1]) / LE); ne = (ue[1], -ue[0])     # (along the face; out of it: the right of p->q is (-uz, ux)... see below)
ne = (-ue[1], ue[0])
yawE = math.atan2(ne[0], ne[1])
mE = ((pE[0] + qE[0]) / 2 + ue[0] * aE, (pE[1] + qE[1]) / 2 + ue[1] * aE)
add("adlertor arch", {"type": "screen", "outline": [[-2.9, 0], [-2.5, 0], [-2.5, 6.2], [0, 9.0], [2.5, 6.2], [2.5, 0], [2.9, 0], [2.9, 6.2], [0, 9.5], [-2.9, 6.2]], "t": 0.25,
                      "at": [[r4(mE[0] + ne[0] * 0.25), yA, r4(mE[1] + ne[1] * 0.25), r4(yawE)]], "_about": "the tall pointed arch framing the gate"})
add("adlertor tympanum", {"type": "screen", "outline": [[-2.3, 4.2], [2.3, 4.2], [2.3, 6.0], [0, 8.6], [-2.3, 6.0]], "t": 0.2,
                          "at": [[r4(mE[0] + ne[0] * 0.45), yA, r4(mE[1] + ne[1] * 0.45), r4(yawE)]], "_about": "the tympanum over the gate"})
add("adlertor rider", comp("equestrian", {"S": 0.62, "stone": "bronze"}, [[r4(mE[0] + ne[0] * 0.75), r4(yA + 4.25), r4(mE[1] + ne[1] * 0.75), r4(yawE + Q)]],
                           _about="the rider in the tympanum (St George? the relief of a mounted knight over the Eagle Gate)"))
add("adlertor arms", {"type": "box", "width": 1.6, "length": 0.3, "height": 1.9, "at": [[r4(mE[0] + ne[0] * 0.15), r4(yA + 11.0), r4(mE[1] + ne[1] * 0.15), r4(yawE)]],
                      "_about": "the Prussian eagle's shield under the battlements"})
add("wilhelmsturm", comp("round-keep", {"sides": 16, "R": 4.0, "H": 7.5, "storeys": 2, "door": "yes", "crown": "platform", "Hg": 2.4, "gOut": 0.35, "corH": 0.9, "pH": 1.0, "t": 0.8},
                         [[72.6, yA, 40.8, r4(-2.3)]], _about="the Wilhelmsturm, the round tower in the middle of the first loop of the ramp"))


# ================================================================================================ THE CASTLE
# THE STOREYS of the ranges over the courtyard (G): the ground floor (service, the treasury), the PRINCIPAL FLOOR (the
# state rooms: Stammbaumhalle, Grafensaal, library, the king's and the queen's rooms), the upper floor (the private
# rooms); the walls 17.5 m to the corbel table and the battlements, the hipped slate roofs behind them
E = [5.0, 6.5, 6.0]
EY = [0.0, 5.0, 11.5]       # each storey's floor over G
HW_ = sum(E)
SLAB = 0.35
WT = 1.0                    # the ranges' walls
SURR = {"band": 0.2, "depth": 0.08}
BARS = {"style": "bars", "cols": 2, "rows": 2}
WIN = [lambda a: {"at": a, "width": 1.1, "sill": 1.5, "springing": 3.5, "head": SEG, "surround": SURR},
       lambda a: {"at": a, "width": 1.5, "sill": 1.2, "springing": 4.9, "head": FLAT, "tracery": BARS, "surround": SURR},
       lambda a: {"at": a, "width": 1.3, "sill": 1.0, "springing": 4.2, "head": FLAT, "tracery": BARS, "surround": SURR}]
DOORW = lambda a, w=1.3, h=2.6: {"at": a, "width": w, "sill": 0, "springing": h, "head": SEG, "glass": False}

# THE OUTLINES of every walled body, registered first and built at the end, so a doorway can be cut through two
# walls standing back to back (a range and the tower in its angle) by one call
BODIES = {}
DOORWAYS = []
def body(name, pts, labels, tiers, y0, about, t=WT, interior=True, windows=None, skipc=("tower", "mitre", "end")):
    P = outward(pts)
    if P != list(pts): raise ValueError(f"{name}: wind its outline with the outside on the right")
    BODIES[name] = {"pts": P, "labels": labels, "tiers": tiers, "y0": y0, "about": about, "t": t, "interior": interior, "ops": {}, "windows": windows, "skipc": skipc}
    return BODIES[name]
def cut(name, face, tier, op):
    BODIES[name]["ops"].setdefault((face, tier), []).append(op)
def door(p, tier, w=1.3, h=2.6, head=SEG, only=None, glass=False, **kw):
    """a doorway at (x, z) in storey `tier`: through every registered wall whose face runs within 15 cm of the point"""
    hits = 0
    for nm, B in BODIES.items():
        if only and nm not in only: continue
        P = B["pts"]
        for i in range(len(P)):
            if math.dist(P[i], P[(i + 1) % len(P)]) < w + 0.3: continue
            if seg_dist(p, P[i], P[(i + 1) % len(P)]) < 0.15:
                cut(nm, i, tier, {"at": face_at(P, i, *p), "width": w, "sill": 0, "springing": h, "head": head, "glass": glass, **kw}); hits += 1
                DOORWAYS.append((nm, i, tuple(p), tier))
    assert hits, ("a doorway in no wall", p)
    return hits

# ---- THE TOWERS (their outlines first: the ranges are cut round them)
TOWERS = {"kaiserturm": ((-38.0, -36.6), 4.4, 16), "bischofsturm": ((-59.4, -26.5), 4.5, 16), "markgrafenturm": ((-63.4, -3.6), 4.6, 16),
          "michaelsturm": ((-40.6, 7.9), 4.3, 12)}
TP = {k: ngon(c, R, n) for k, (c, R, n) in TOWERS.items()}

# ---- THE RANGES: OSM's outlines, mitred where two meet, cut round the round towers in the angles
K_out, K_in = (-41.1, -36.1), (-42.76, -21.33)
J_out, J_in = (-61.29, -26.24), (-53.29, -17.19)
M_out, M_in = (-62.71, -1.15), (-52.79, -8.61)
SB_out, SB_in = (-36.64, 8.82), (-32.98, -1.33)
NA_out, NA_in = (9.53, -23.68), (3.75, -5.52)
N_JOG = [(-26.3, -31.97), (-26.1, -35.63)]
RANGES = {"north-west range": ([K_out, J_out, J_in, K_in], ["outer", "mitre", "court", "mitre"], ("kaiserturm", "bischofsturm")),
          "west range": ([J_out, M_out, M_in, J_in], ["outer", "mitre", "court", "mitre"], ("bischofsturm", "markgrafenturm")),
          "south range": ([M_out, SB_out, SB_in, M_in], ["outer", "end", "court", "mitre"], ("markgrafenturm", "michaelsturm")),
          "north wing": ([NA_out] + N_JOG + [K_out, K_in, NA_in], ["outer", "outer", "outer", "mitre", "court", "end"], ("kaiserturm",))}
ABOUT_R = {"north-west range": "the north-west range between the Kaiserturm and the Bischofsturm: the GRAFENSAAL on its principal floor",
           "west range": "the west range between the Bischofsturm and the Markgrafenturm: the LIBRARY on its principal floor, the Wartturm in its angle to the court",
           "south range": "the south range from the Markgrafenturm to St Michael's chapel: the KING'S rooms and the QUEEN'S (the Blue Salon), the Michaelsturm on its south front",
           "north wing": "the north wing, the deepest range: the STAMMBAUMHALLE at its west end behind the porch and the Freitreppe, the state stair, the rooms toward the Christuskapelle"}
FRAME = {}              # a range's own frame: its outer face's first corner, along it, and in from it
for nm, (pts, labs, tws) in RANGES.items():
    a, b = pts[0], pts[1]; L = math.dist(a, b); u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
    FRAME[nm] = (a, u, (u[1], -u[0]))          # (in: the left of the outer face's direction)
    P, lab = list(pts), list(labs)
    for tw in tws:
        P, lab = bite(P, lab, TP[tw], "tower")
    body(nm, P, lab, E, G, ABOUT_R[nm], windows=True)
def W(nm, u, v):
    a, e, n = FRAME[nm]; return (r4(a[0] + e[0] * u + n[0] * v), r4(a[1] + e[1] * u + n[1] * v))
def UV(nm, x, z):
    a, e, n = FRAME[nm]; return ((x - a[0]) * e[0] + (z - a[1]) * e[1], (x - a[0]) * n[0] + (z - a[1]) * n[1])
def yaw_of(nm):
    a, e, n = FRAME[nm]; return math.atan2(-e[1], e[0])     # (a placement turned so its +x runs along the range, its +z OUT of it)

# ---- the towers' lower shafts (to the ranges' cornice): rooms on the principal floor, doors from the ranges
for k, (c, R, n) in TOWERS.items():
    if k == "michaelsturm": continue
    body(k, TP[k], ["tower"] * n, E, G, f"the {k.title()}'s shaft below the ranges' cornice", t=1.0, windows="tower", skipc=())
body("michaelsturm", TP["michaelsturm"], ["tower"] * 12, E, G, "the Michaelsturm: the half-round tower on the south front, its room off the queen's salon", t=0.8, windows="tower", skipc=())
# THE WARTTURM: the slender stair tower in the court angle of the west range, its wall against the range's
WT_C = (r4(-53.08 + 3.1 * math.cos(math.pi / 12) - 0.12), -13.6)
WT_P = ngon(WT_C, 3.1, 12)
body("wartturm", WT_P, ["tower"] * 12, E, G, "the Wartturm: the stair tower in the court's west angle, its spiral from the court to the upper floor", t=0.6, windows="tower", skipc=())

# ---- THE CHAPELS
# the CHRISTUSKAPELLE (the Protestant chapel, Stüler's): a nave east of the north wing, its west wall the wing's end, a
# five-sided apse to the east; tall two-light windows between buttresses, a wimperg over each apse window
CK_W = lambda z: (r4(NA_in[0] + (NA_out[0] - NA_in[0]) * (z - NA_in[1]) / (NA_out[1] - NA_in[1])), z)
CK_Z0, CK_Z1, CK_AX, CK_R = -16.6, -8.2, 16.0, 4.546
CKA = [(r4(CK_AX + CK_R * math.cos(math.radians(t))), r4((CK_Z0 + CK_Z1) / 2 + CK_R * math.sin(math.radians(t)))) for t in (-112.5, -67.5, -22.5, 22.5, 67.5, 112.5)]
CK = outward([CK_W(CK_Z0)] + CKA + [CK_W(CK_Z1)])
CKH = 11.0
body("christuskapelle", CK, ["chapel"] * len(CK), [CKH], G, "the Christuskapelle, the Protestant chapel (1853-55): nave and five-sided apse, the tall traceried windows", t=0.9, windows="chapel", skipc=())
# ST MICHAEL'S CHAPEL (the Catholic chapel, the one medieval building left, 15th century): its west wall the south
# range's end, the nave, a narrower chancel and a three-sided apse to the east-south-east
MU = ((SB_in[0] - SB_out[0]), (SB_in[1] - SB_out[1])); ML = math.hypot(*MU)
mv = (MU[0] / ML, MU[1] / ML)                       # (across the chapel: from its south-west corner to its north-west one)
mu = (-mv[1], mv[0])                                # (along it, east-south-east)
if mu[0] < 0: mu = (-mu[0], -mu[1])
M0 = SB_out                                          # (its south-west corner; v runs north across it)
MW = 8.9
def MP(u, v): return (r4(M0[0] + mu[0] * u + mv[0] * v), r4(M0[1] + mu[1] * u + mv[1] * v))
MA_C, MA_R = 16.3, 3.2
MC = [MP(0, 0), MP(13.6, 0), MP(13.6, MW / 2 - 3.2)] + [MP(MA_C + MA_R * math.cos(math.radians(t)), MW / 2 + MA_R * math.sin(math.radians(t))) for t in (-90, -45, 0, 45, 90)][::-1] + \
     [MP(13.6, MW / 2 + 3.2), MP(13.6, MW), MP(0, MW)]
MC = [MC[0], MC[1], MC[2], MP(MA_C, MW / 2 - 3.2), MP(MA_C + MA_R * 0.7071, MW / 2 - MA_R * 0.7071), MP(MA_C + MA_R, MW / 2), MP(MA_C + MA_R * 0.7071, MW / 2 + MA_R * 0.7071),
      MP(MA_C, MW / 2 + 3.2), MP(13.6, MW / 2 + 3.2), MP(13.6, MW), MP(0, MW)]
MC = outward(MC)
MCH = 8.5
body("st michael's chapel", MC, ["chapel"] * len(MC), [MCH], G, "St Michael's chapel, the castle's Catholic chapel and its oldest building: plastered walls, small lancets, the chancel to the east", t=0.9,
     windows="michael", skipc=())

# ---- THE TORTURM AND THE GATEHOUSE (the inner gate: the bridge from the Rampenturm runs into its east face at G)
TORT = outward(TORTURM)
def on_edge(P, i, Q_):
    return poly_dist(P[i], Q_) < 0.05 and poly_dist(P[(i + 1) % len(P)], Q_) < 0.05
TOR_H = 13.0
body("torturm", TORT, ["gate"] * 4, [TOR_H], G, "the TORTURM, the inner gate tower: the passage from the bridge into the inner castle under a pointed arch at either end", t=1.2,
     interior=False, windows="gate", skipc=())
GH = outward([(43.8, -10.8), (40.78, -2.86), (46.77, -0.64), (48.4, -5.14)])
body("gatehouse", GH, ["tower" if on_edge(GH, i, TORT) else "outer" for i in range(4)], E[:2], G,
     "the gatehouse beside the Torturm (the guard's and the castle steward's rooms)", t=0.7, windows=True)

# ---- WHAT STANDS BEFORE THE WALLS (kept clear of windows): the Freitreppe and its porch on the north wing's court
# front, the two stair turrets on it -- by storey (None: all)
KC, NC_ = K_in, NA_in
LC = math.dist(KC, NC_); ec = ((NC_[0] - KC[0]) / LC, (NC_[1] - KC[1]) / LC); oc = (-ec[1], ec[0])       # (along the court front east; out of it, into the court)
def courtpt(s, o=0.0): return (r4(KC[0] + ec[0] * s + oc[0] * o), r4(KC[1] + ec[1] * s + oc[1] * o))
YAWC = math.atan2(-ec[1], ec[0])
FT0, FT1, PO0 = 21.6, 12.9, 9.3            # (the Freitreppe's foot and head, the porch's west end, metres from the court front's west corner)
STAIR_T = [31.5, 44.0]                     # (the stair turrets on the court front)
EXTRA = {"freitreppe": ([courtpt(PO0 - 0.6, 0), courtpt(FT0 + 0.4, 0), courtpt(FT0 + 0.4, 3.6), courtpt(PO0 - 0.6, 3.6)], (0, 1))}
for k, s in enumerate(STAIR_T): EXTRA[f"stair turret {k}"] = (ngon(courtpt(s, 0.9), 2.5, 8), None)

# ---- WINDOWS: in every face that looks out, storey by storey, kept clear of the towers, of what stands against it and
# of the doorways already cut
FOOT = {nm: B["pts"] for nm, B in BODIES.items()}
def covered(p, own, tier=None):
    """is the point (a metre and a half out from a face) inside another body, or a tower, or what stands before a front"""
    for nm, P in FOOT.items():
        if nm != own and inside(p[0], p[1], P): return True
    for nm, (P, tiers) in EXTRA.items():
        if (tiers is None or tier in tiers) and inside(p[0], p[1], P): return True
    return False
def clear_of(nm, i, j, at, w):
    return all(abs(at - o["at"]) > (w + o["width"]) / 2 + 0.5 for o in BODIES[nm]["ops"].get((i, j), []))
def lancet(at, w, sill, spring, **kw):
    return {"at": r4(at), "width": w, "sill": sill, "springing": spring, "head": PTD, **kw}
def fill_windows():
    for nm, B in BODIES.items():
        kind = B["windows"]
        if not kind: continue
        P = B["pts"]
        for i in range(len(P)):
            a, b = P[i], P[(i + 1) % len(P)]; L = math.dist(a, b); lab = B["labels"][i]
            e = ((b[0] - a[0]) / L, (b[1] - a[1]) / L); nrm = (-e[1], e[0])
            pt = lambda at, o=1.5: (a[0] + e[0] * (L / 2 + at) + nrm[0] * o, a[1] + e[1] * (L / 2 + at) + nrm[1] * o)
            if kind is True:
                if lab not in ("outer", "court", "end") or L < 3.2: continue
                n = int((L - 2.0) // 3.5)
                if n <= 0: continue
                step = (L - 2.0) / n
                for k in range(n):
                    at = r4(-L / 2 + 1.0 + step * (k + 0.5))
                    if any(math.dist(pt(at, 0), c) < R + 1.2 for c, R, _ in TOWERS.values()) or math.dist(pt(at, 0), WT_C) < 4.4: continue
                    for j in range(len(B["tiers"])):
                        if covered(pt(at), nm, j) or not clear_of(nm, i, j, at, 1.5): continue
                        cut(nm, i, j, WIN[j](at))
            elif kind == "tower":
                if covered(pt(0, 1.2), nm) or L < 1.2 or i % 2: continue
                w = min(0.9, L * 0.45)
                for j, (s_, sp) in enumerate(((1.6, 3.4), (1.4, 4.6), (1.2, 4.1))):
                    if clear_of(nm, i, j, 0, w): cut(nm, i, j, {"at": 0, "width": w, "sill": s_, "springing": sp, "head": SEMI, "surround": SURR})
            elif kind == "chapel":                  # (the Christuskapelle: tall two-light windows, sandstone tracery)
                if covered(pt(0), nm) or L < 2.8: continue
                ats = [-L / 4, L / 4] if L > 8 else [0.0]
                for at in ats:
                    w = 1.7 if L > 8 else 1.5
                    if clear_of(nm, i, 0, at, w): cut(nm, i, 0, lancet(at, w, 3.2, 8.4, tracery={"lights": 2}, surround=SURR))
            elif kind == "michael":                 # (St Michael's: small lancets in the plastered walls)
                if covered(pt(0), nm) or L < 2.0: continue
                ats = [-L / 4, L / 4] if L > 8 else [0.0]
                for at in ats:
                    if clear_of(nm, i, 0, at, 0.7): cut(nm, i, 0, lancet(at, 0.7, 3.0, 6.0, surround=SURR))
            elif kind == "gate":                    # (the Torturm: slits over the gate)
                if L < 5: continue
                for j in range(len(B["tiers"])):
                    for at in (-1.6, 1.6):
                        if clear_of(nm, i, j, at, 0.6): cut(nm, i, j, {"at": at, "width": 0.6, "sill": 8.0, "springing": 9.6, "head": SEMI})

# ---- DOORWAYS (before the windows, which keep clear of them)
DOOR_SEEN = set()
def mitre_doors():
    for nm in RANGES:
        P = BODIES[nm]["pts"]
        for i, lab in enumerate(BODIES[nm]["labels"]):
            if lab != "mitre": continue
            a, b = P[i], P[(i + 1) % len(P)]
            m = (r4((a[0] + b[0]) / 2), r4((a[1] + b[1]) / 2)); key = (round(m[0], 1), round(m[1], 1))
            if key in DOOR_SEEN: continue
            DOOR_SEEN.add(key)
            for j in range(3): assert door(m, j, w=1.4, h=2.9) == 2, (nm, m)
mitre_doors()
def tower_doors(nm, tw, tiers=(0, 1, 2), w=1.1, h=2.5):
    """a doorway from the range into the tower in its angle, through the middle one of the faces they share, on each storey"""
    P, labs = BODIES[nm]["pts"], BODIES[nm]["labels"]; c = TOWERS[tw][0]
    fs = [i for i in range(len(P)) if labs[i] == "tower" and abs(math.dist(((P[i][0] + P[(i + 1) % len(P)][0]) / 2, (P[i][1] + P[(i + 1) % len(P)][1]) / 2), c) - TOWERS[tw][1] * 0.97) < 0.4
          and math.dist(P[i], P[(i + 1) % len(P)]) > w + 0.35]
    i = fs[len(fs) // 2]
    m = (r4((P[i][0] + P[(i + 1) % len(P)][0]) / 2), r4((P[i][1] + P[(i + 1) % len(P)][1]) / 2))
    for j in tiers: assert door(m, j, w=w, h=h, only=(nm, tw)) == 2, (nm, tw)
tower_doors("north wing", "kaiserturm")
tower_doors("north-west range", "bischofsturm")
tower_doors("west range", "markgrafenturm")
tower_doors("south range", "michaelsturm")
# (the Wartturm: in from the court at its foot, out on its landings into the west range's principal and upper floors)
WT_A = 3.1 * math.cos(math.pi / 12)
def wt_pt(deg, d=WT_A): return (r4(WT_C[0] + d * math.sin(math.radians(deg))), r4(WT_C[1] + d * math.cos(math.radians(deg))))
door(wt_pt(90), 0, w=1.1, h=2.5, head=PTD, only=("wartturm",))
for j in (1, 2): assert door(wt_pt(270, WT_A - 0.06), j, w=1.1, h=2.5) == 2
# (in from the court: the north wing's stair hall and its rooms, the Grafensaal's range, the south range)
def on_line(a, b, s): L = math.dist(a, b); return (r4(a[0] + (b[0] - a[0]) * s / L), r4(a[1] + (b[1] - a[1]) * s / L))
NC_LINE = lambda u: on_line(KC, NC_, (50.41 - u) / 0.995)
door(NC_LINE(12.25), 0, w=1.6, h=3.0, head=PTD, only=("north wing",))
door(NC_LINE(22.0), 0, w=1.4, h=2.8, only=("north wing",))
door(on_line(J_in, K_in, math.dist(J_in, K_in) / 2), 0, w=1.6, h=3.0, head=PTD, only=("north-west range",))
door(on_line(SB_in, M_in, math.dist(SB_in, M_in) * 0.45), 0, w=1.6, h=3.0, head=PTD, only=("south range",))
# (the Freitreppe's door: the visitors' way in, to the Stammbaumhalle on the principal floor)
door(courtpt(11.1), 1, w=1.8, h=3.4, head=PTD, only=("north wing",), wimperg=True)
# (the chapels: their portals from the court, and through the ranges' end walls)
door(CK_W(-12.4), 0, w=1.4, h=2.8, head=PTD)
door(((CK[0][0] + CK[1][0]) / 2, -8.2), 0, w=1.8, h=3.6, head=PTD, only=("christuskapelle",), wimperg=True)
door(MP(0, MW / 2), 0, w=1.4, h=2.8, head=PTD)
door(MP(4.5, MW), 0, w=1.5, h=3.0, head=PTD, only=("st michael's chapel",))
# (the Torturm's gate, the gatehouse's door)
door(TOR_E, 0, w=4.0, h=4.4, head=PTD, only=("torturm",))
door(TOR_W, 0, w=4.0, h=4.4, head=PTD, only=("torturm",))
door(((43.8 + 40.78) / 2, (-10.8 - 2.86) / 2), 0, w=1.3, h=2.6, only=("gatehouse",))
fill_windows()

# ---- THE WALLS, BUILT: every body an enclosure, storey by storey
for nm, B in BODIES.items():
    P, hs = B["pts"], B["tiers"]
    F = {}
    for i in range(len(P)):
        F[str(i)] = [({"h": h} if j < len(hs) - 1 else {}) | {"openings": sorted(B["ops"].get((i, j), []), key=lambda o: o["at"])} for j, h in enumerate(hs)]
    skip = [str(i) for i, l in enumerate(B["labels"]) if l in B["skipc"]]
    add(nm, {"type": "enclosure", "plan": {"points": [[r4(x), r4(z)] for x, z in P]}, "thickness": B["t"], "height": r4(sum(hs)), "glass": True, "interior": B["interior"],
             "faces": F, "courses": {"skip": skip} if skip else True, "at": [[0, B["y0"], 0, 0]], "_about": B["about"]})

# ---- FLOORS: a slab under the principal and the upper floor and the roof deck over all, in every range and tower; the
# north wing's with the state stair's well
TOPW = G + HW_
def slab_pts(P, d=0.5): return [[r4(x), r4(z)] for x, z in offset(P, -d)]
FLOORS = []
for nm in ("north-west range", "west range", "south range"):
    FLOORS.append(add(f"{nm} floors", {"type": "prism", "plan": {"points": slab_pts(BODIES[nm]["pts"])}, "height": SLAB, "flatRoof": False,
                                       "at": [[0, r4(G + y - SLAB), 0, 0] for y in EY[1:]], "_about": f"the {nm}'s floors"}))
    FLOORS.append(add(f"{nm} roof deck", {"type": "prism", "plan": {"points": slab_pts(BODIES[nm]["pts"])}, "height": SLAB, "flatRoof": True, "at": [[0, r4(TOPW - SLAB), 0, 0]]}))
for tw in ("kaiserturm", "bischofsturm", "markgrafenturm", "michaelsturm"):
    c, R, n = TOWERS[tw]
    FLOORS.append(add(f"{tw} floors", {"type": "prism", "plan": {"points": [[r4(x), r4(z)] for x, z in ngon(c, R - 0.5, n)]}, "height": SLAB, "flatRoof": False,
                                       "at": [[0, r4(G + y - SLAB), 0, 0] for y in EY[1:]]}))
    FLOORS.append(add(f"{tw} deck", {"type": "prism", "plan": {"points": [[r4(x), r4(z)] for x, z in ngon(c, R - 0.5, n)]}, "height": SLAB, "flatRoof": True, "at": [[0, r4(TOPW - SLAB), 0, 0]]}))
FLOORS.append(add("wartturm deck", {"type": "prism", "plan": {"points": [[r4(x), r4(z)] for x, z in ngon(WT_C, 2.8, 12)]}, "height": SLAB, "flatRoof": True,
                                    "at": [[0, r4(TOPW - SLAB), 0, 0]]}))
# the north wing's, in its own frame (local x along the outer front westward, local z out of it: (u, -v)), the stair's well cut
NWF = FRAME["north wing"]
def nloc(p): u, v = UV("north wing", *p); return [r4(u), r4(-v)]
nyaw = r4(yaw_of("north wing"))
NW_SL = [nloc(p) for p in offset(BODIES["north wing"]["pts"], -0.5)]
SA, SB_, S_V0 = 13.45, 11.05, 4.0          # (the state stair: its first flight's and its return's middle lines, where it starts)
for k, (y, v1) in enumerate(((EY[1], 10.7), (EY[2], 11.9))):
    FLOORS.append(add(f"north wing floor {k + 1}", {"type": "prism", "plan": {"points": NW_SL, "well": {"rect": [4.4, r4(v1 - S_V0)], "at": [12.25, r4(-(S_V0 + v1) / 2)]}},
                                                    "height": SLAB, "flatRoof": False, "at": [[NWF[0][0], r4(G + y - SLAB), NWF[0][1], nyaw]],
                                                    "_about": "the north wing's floor, the state stair's well in it"}))
FLOORS.append(add("north wing roof deck", {"type": "prism", "plan": {"points": NW_SL}, "height": SLAB, "flatRoof": True, "at": [[NWF[0][0], r4(TOPW - SLAB), NWF[0][1], nyaw]]}))
_g0 = (sum(p[0] for p in GH) / 4, sum(p[1] for p in GH) / 4)
def _gs():                  # the gatehouse's newel stair in its east corner, 1.85 m in from both walls
    c, a, b = GH[3], GH[2], GH[0]
    ua = ((a[0] - c[0]) / math.dist(a, c), (a[1] - c[1]) / math.dist(a, c)); ub = ((b[0] - c[0]) / math.dist(b, c), (b[1] - c[1]) / math.dist(b, c))
    bis = (ua[0] + ub[0], ua[1] + ub[1]); lb = math.hypot(*bis); bis = (bis[0] / lb, bis[1] / lb)
    sin_half = abs(ua[0] * bis[1] - ua[1] * bis[0])
    return (r4(c[0] + bis[0] * 1.85 / sin_half), r4(c[1] + bis[1] * 1.85 / sin_half))
GS_C = _gs()
GS_N, GS_T = 27, 24.0
GS_A0 = math.degrees(math.atan2(_g0[0] - GS_C[0], _g0[1] - GS_C[1])) - GS_N * GS_T - 30.0      # (so that it comes out toward the room)
FLOORS.append(add("gatehouse floor", {"type": "prism", "plan": {"points": slab_pts(GH, 0.35), "well": {"radius": 1.08, "sides": 16, "at": list(GS_C)}}, "height": SLAB, "flatRoof": False, "at": [[0, r4(G + E[0] - SLAB), 0, 0]]}))
FLOORS.append(add("gatehouse ceiling", {"type": "prism", "plan": {"points": slab_pts(GH, 0.35)}, "height": SLAB, "flatRoof": True, "at": [[0, r4(G + E[0] + E[1] - SLAB), 0, 0]]}))
FLOORS.append(add("torturm vault", {"type": "prism", "plan": {"points": slab_pts(TORT, 0.6)}, "height": 0.6, "flatRoof": True, "at": [[0, r4(G + 5.6), 0, 0], [0, r4(G + TOR_H - 0.6), 0, 0]],
                                    "_about": "the gate passage's ceiling, and the deck at the top"}))

# ---- STAIRS: the state stair in the north wing (a dog-leg round a landing at the court end, a pair of flights a storey);
# the Wartturm's spiral from the court to the west range's floors
nin = (NWF[2][0], NWF[2][1])               # (in from the outer front, toward the court)
syaw = r4(math.atan2(-nin[1], nin[0]))
for k, (y0, h, n) in enumerate(((0.0, E[0], 15), (EY[1], E[1], 19))):
    add(f"state stair {k + 1}", {"type": "staircase", "rise": r4(h / (2 * n)), "run": 0.3, "soffit": 0.3, "flight": n, "width": 2.0,
                                 "landing": {"depth": 2.2, "width": 4.4, "shift": -1.2, "then": [{"from": "back", "at": -1.2, "flight": n, "width": 2.0, "landing": {"depth": 1.0, "width": 2.0}}]},
                                 "at": [[*W("north wing", SA, S_V0)[:1], r4(G + y0), W("north wing", SA, S_V0)[1], syaw]],
                                 "_about": "the state stair in the north wing: up toward the court to the landing, back beside itself to the floor above"})
for k, (y0, h, n) in enumerate(((0.0, E[0], GS_N),)):
    add(f"gatehouse stair {k + 1}", {"type": "spiral-stair", "radius": 0.98, "newel": 0.15, "turn": GS_T, "top": h, "steps": n, "landing": 0.9, "soffit": 0.15,
                                     "at": [[GS_C[0], r4(G + y0), GS_C[1], r4(math.radians(GS_A0))]],
                                     "_about": "the gatehouse's newel stair to its upper floor"})
WT_STAIR = [(0.0, E[0], 26, 150.0, 17.46), (EY[1], E[1], 34, 297.0, 19.6)]
for k, (y0, h, n, a0, tn) in enumerate(WT_STAIR):
    add(f"wartturm stair {k + 1}", {"type": "spiral-stair", "radius": 2.3, "newel": 0.25, "turn": tn, "top": h, "steps": n, "landing": 1.2, "soffit": 0.2,
                                    "at": [[WT_C[0], r4(G + y0), WT_C[1], r4(math.radians(a0))]],
                                    "_about": "the Wartturm's spiral: from the court to the principal floor, on to the upper floor"})

# ---- INNER WALLS with their doorways (each storey's in its own tier)
def iwall(name, a, b, doors, t=0.3, about=None):
    """an inner wall from a to b (x, z), through all three storeys: `doors` {storey: [metres along from a]}"""
    L = math.dist(a, b); dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    tiers = []
    for j, h in enumerate(E):
        ops = [{"at": r4(d - L / 2), "width": 1.2, "sill": 0, "springing": 2.6, "head": SEG, "glass": False} for d in doors.get(j, [])]
        tiers.append(({"h": h} if j < 2 else {}) | {"openings": ops})
    mx, mz = (a[0] + b[0]) / 2 - t / 2 * dz, (a[1] + b[1]) / 2 + t / 2 * dx
    d = {"type": "wall", "width": r4(L), "height": HW_, "thickness": t, "tiers": tiers, "at": [[r4(mx), G, r4(mz), r4(math.atan2(-dz, dx))]]}
    if about: d["_about"] = about
    return add(name, d)
COURT_V = lambda u: 19.0 + (u - 1.54) * (14.08 - 19.0) / (50.41 - 1.54)
INNER = []
for u, about in ((9.0, "the stair hall's east wall"), (15.5, "the stair hall's west wall"), (26.0, "between the rooms of the north wing"),
                 (37.0, "the Stammbaumhalle's east wall")):
    v0, v1 = 0.5, COURT_V(u) - 0.5
    INNER.append(iwall(f"north wing wall {u:g}", W("north wing", u, v0), W("north wing", u, v1), {0: [2.0, v1 - v0 - 3.0], 1: [2.0, v1 - v0 - 3.0], 2: [2.0, v1 - v0 - 3.0]}, about=about))
for u, about in ((11.0, "between the king's rooms"), (19.0, "between the king's and the queen's rooms (the Blue Salon beyond)")):
    INNER.append(iwall(f"south range wall {u:g}", W("south range", u, 0.5), W("south range", u, 10.3), {0: [5.0], 1: [7.8], 2: [5.0]}, about=about))

# ---- THE GRAFENSAAL (north-west range, principal floor): rib vaults on slender columns, three bays by two
GU0, GU1, GV0, GV1 = 8.3, 16.1, 1.0, 10.9
gw, gl = (GU1 - GU0) / 2, (GV1 - GV0) / 3
nwyaw = r4(yaw_of("north-west range"))
G_SPR, G_TOP = r4(G + EY[1] + 3.55), r4(G + EY[2] - SLAB)
bays = [[*W("north-west range", GU0 + gw * (i + 0.5), GV0 + gl * (k + 0.5))[:1], 0, W("north-west range", GU0 + gw * (i + 0.5), GV0 + gl * (k + 0.5))[1], nwyaw]
        for i in range(2) for k in range(3)]
add("grafensaal vault", {"type": "groin", "width": r4(gw), "length": r4(gl), "springing": G_SPR, "top": G_TOP, "head": {"profile": "pointed", "spread": 0.3},
                         "at": bays, "_about": "the GRAFENSAAL's rib vaults: six bays on the walls and on two columns down the hall's middle"})
add("grafensaal ribs", {"type": "ribs", "on": "grafensaal vault", "width": 0.18, "depth": 0.16, "wall": {"width": 0.2, "depth": 0.12}, "at": bays})
GCOL = [W("north-west range", GU0 + gw, GV0 + gl * k) for k in (1, 2)]
add("grafensaal columns", {"type": "column", "radius": 0.26, "height": r4(G_SPR - G - EY[1] - 0.45), "sides": 12, "taper": 0.9,
                           "at": [[c[0], r4(G + EY[1]), c[1], 0] for c in GCOL], "_about": "the Grafensaal's slender marble columns"})
add("grafensaal capitals", {"type": "column", "radius": 0.26, "height": 0.45, "sides": 12, "taper": 1.62, "at": [[c[0], r4(G_SPR - 0.45), c[1], 0] for c in GCOL]})
add("grafensaal capital tops", {"type": "prism", "plan": {"rect": [0.9, 0.9]}, "height": 0.12, "flatRoof": True, "at": [[c[0], r4(G_SPR - 0.12), c[1], nwyaw] for c in GCOL]})

# ---- THE STAMMBAUMHALLE, the library, the royal rooms, the chapels: their furniture (docs/items.md)
def item(name, path, at, about=None, **kw):
    d = {"type": "item", "item": "items/furniture/" + path, "at": [[r4(x), r4(y), r4(z), r4(yaw)] for x, y, z, yaw in at], **kw}
    if about: d["_about"] = about
    return add(name, d)
wyaw = yaw_of("west range")
item("library bookcases", "bookcase", [(*W("west range", u, 1.25)[:1], G + EY[1], W("west range", u, 1.25)[1], wyaw + math.pi) for u in (6.0, 7.4, 8.8, 13.2, 14.6, 16.0)] +
     [(*W("west range", u, 7.6)[:1], G + EY[1], W("west range", u, 7.6)[1], wyaw) for u in (9.5, 10.9, 12.3)], about="the library's bookcases (Stüler's library on the principal floor)")
item("library table", "refectory-table", [(*W("west range", 11.0, 4.4)[:1], G + EY[1], W("west range", 11.0, 4.4)[1], wyaw)])
syaw_ = yaw_of("south range")
item("king's bed", "four-poster", [(*W("south range", 6.5, 3.0)[:1], G + EY[1], W("south range", 6.5, 3.0)[1], syaw_ + Q)], about="the king's bedroom in the south range")
item("blue salon sofas", "sofa", [(*W("south range", 23.0, 8.8)[:1], G + EY[1], W("south range", 23.0, 8.8)[1], syaw_)])
item("christuskapelle altar", "altar-table", [(18.6, G, -12.4, -Q)], about="the altar in the Christuskapelle's apse")
item("christuskapelle pews", "bench", [(x, G, z, Q) for x in (8.0, 10.0, 12.0) for z in (-14.2, -10.6)])
item("st michael's altar", "altar-table", [(*MP(17.6, MW / 2)[:1], G, MP(17.6, MW / 2)[1], math.atan2(-mu[1], mu[0]) - Q)])
item("st michael's pews", "bench", [(*MP(u, v)[:1], G, MP(u, v)[1], math.atan2(-mu[1], mu[0]) + Q) for u in (5.0, 7.5, 10.0) for v in (2.6, 6.3)])

# (the Stammbaumhalle: a beamed oak ceiling, the family tree painted on its walls -- the finish)
SB_U0, SB_U1 = 37.4, 49.6
CEIL1 = r4(G + EY[2] - SLAB)            # (the principal floor's ceiling: the underside of the upper floor)
item("grafensaal chandeliers", "chandelier", [(b[0], G_TOP - 0.05, b[2], 0.0) for b in bays], about="a gilt chandelier hanging in every bay of the Grafensaal", solid=False)
item("stammbaumhalle chandeliers", "chandelier", [(*W("north wing", u, 6.8)[:1], CEIL1, W("north wing", u, 6.8)[1], 0.0) for u in (SB_U0 + 2.0 + 1.6 * 1, SB_U0 + 2.0 + 1.6 * 4)],
     about="chandeliers between the Stammbaumhalle's beams", solid=False)
item("library chandeliers", "chandelier", [(*W("west range", u, 4.4)[:1], CEIL1, W("west range", u, 4.4)[1], 0.0) for u in (8.0, 14.0)], solid=False)
item("royal chandeliers", "chandelier", [(*W("south range", u, 5.4)[:1], CEIL1, W("south range", u, 5.4)[1], 0.0) for u in (8.5, 15.0, 24.0)], about="in the king's rooms and the Blue Salon", solid=False)
add("stammbaumhalle beams", {"type": "box", "width": 0.3, "length": 13.0, "height": 0.4,
                             "at": [[*W("north wing", u, 6.8)[:1], r4(G + EY[2] - SLAB - 0.4), W("north wing", u, 6.8)[1], nyaw] for u in [SB_U0 + 1.2 + 1.6 * k for k in range(7)]],
                             "_about": "the Stammbaumhalle's oak beams"})
# ---- THE FREITREPPE AND ITS PORCH on the north wing's court front
add("freitreppe", flight(courtpt(FT0, 1.2), (-ec[0], -ec[1]), 2.0, G, G + EY[1], _about="the Freitreppe up the court front to the porch at the Stammbaumhalle's door"))
add("porch", {"type": "prism", "plan": {"rect": [r4(FT1 - PO0), 3.2]}, "height": EY[1], "flatRoof": False, "walked": True,
              "at": [[*courtpt((FT1 + PO0) / 2, 1.6)[:1], G, courtpt((FT1 + PO0) / 2, 1.6)[1], r4(YAWC)]], "_about": "the porch at the head of the Freitreppe"})
add("porch parapet", {"type": "box", "width": r4(FT1 - PO0 + 0.3), "length": 0.3, "height": 1.0, "at": [[*courtpt((FT1 + PO0) / 2 - 0.15, 3.05)[:1], G + EY[1], courtpt((FT1 + PO0) / 2 - 0.15, 3.05)[1], r4(YAWC)]]})
add("porch parapet end", {"type": "box", "width": 0.3, "length": 3.2, "height": 1.0, "at": [[*courtpt(PO0 + 0.15, 1.6)[:1], G + EY[1], courtpt(PO0 + 0.15, 1.6)[1], r4(YAWC)]]})
add("freitreppe parapet", {"type": "sweep", "path": [[*courtpt(FT0, 2.35)[:1], G, courtpt(FT0, 2.35)[1]], [*courtpt(FT1, 2.35)[:1], G + EY[1], courtpt(FT1, 2.35)[1]]],
                           "profile": [[-0.15, -5.6], [0.15, -5.6], [0.15, 1.0], [-0.15, 1.0]], "step": 1.0, "_about": "the Freitreppe's parapet"})

# ---- THE WALL HEADS: the corbel table and the battlements over every face that looks out, the slate roofs behind them
HEADS = []
for nm, B in BODIES.items():
    if nm not in RANGES and nm != "gatehouse": continue
    P = B["pts"]; top = G + sum(B["tiers"])
    for i, lab in enumerate(B["labels"]):
        if lab not in ("outer", "court", "end"): continue
        a, b = P[i], P[(i + 1) % len(P)]; L = math.dist(a, b)
        if L < 1.5: continue
        e = ((b[0] - a[0]) / L, (b[1] - a[1]) / L); o = (-e[1], e[0])
        m = ((a[0] + b[0]) / 2 + o[0] * 0.14, (a[1] + b[1]) / 2 + o[1] * 0.14)
        HEADS.append(add(f"{nm} corbel table {i}", {"type": "box", "width": r4(L + 0.28), "length": 0.28, "height": 0.55, "at": [[r4(m[0]), r4(top - 0.55), r4(m[1]), r4(math.atan2(-e[1], e[0]))]]}))
        a2, b2 = (a[0] + o[0] * 0.28 - e[0] * 0.28, a[1] + o[1] * 0.28 - e[1] * 0.28), (b[0] + o[0] * 0.28 + e[0] * 0.28, b[1] + o[1] * 0.28 + e[1] * 0.28)
        BATTLEMENTS.extend(parapets(add, f"{nm} battlements {i}", [a2, b2], r4(top), h=1.1, step=1.9, t=0.55, closed=False))
def hip(name, rng, u0, u1, v0, v1, pitch=52, along="u", y=None, about=None):
    """a hipped slate roof over the rect u0..u1, v0..v1 of a range's frame, its ridge along u (or v)"""
    a, e, n = FRAME[rng]; c = W(rng, (u0 + u1) / 2, (v0 + v1) / 2)
    d = e if along == "u" else n
    Lr, Wr = (u1 - u0, v1 - v0) if along == "u" else (v1 - v0, u1 - u0)
    r = {"type": "roof", "form": "hip", "width": r4(Wr), "length": r4(Lr), "pitch": pitch, "overhang": 0.25, "at": [[c[0], r4(TOPW if y is None else y), c[1], r4(math.atan2(d[0], d[1]))]]}
    if about: r["_about"] = about
    return add(name, r)
ROOFS = [hip("north wing roof", "north wing", 1.8, 37.4, 0.4, 14.9, about="the north wing's great slate roof"),
         hip("north wing west roof", "north wing", 37.0, 50.0, -3.2, 13.6, along="v", about="the roof over the Stammbaumhalle's end, ridge across the wing"),
         hip("north-west range roof", "north-west range", 4.0, 19.2, 0.4, 11.4),
         hip("west range roof", "west range", 5.5, 20.0, 0.4, 8.6),
         hip("south range roof", "south range", 4.5, 27.4, 0.4, 10.2),
         add("gatehouse roof", {"type": "roof", "form": "hip", "width": 5.0, "length": 7.4, "pitch": 50, "overhang": 0.2,
                                "at": [[44.9, r4(G + E[0] + E[1]), -4.9, r4(math.atan2(-3.02, 7.94))]]})]
CHIMNEYS = add("chimneys", {"type": "box", "width": 0.9, "length": 0.7, "height": 3.4,
                            "at": [[*W("north wing", u, v)[:1], r4(TOPW + 4.0), W("north wing", u, v)[1], nyaw] for u, v in ((8.0, 4.5), (22.0, 10.0), (31.0, 4.5))] +
                                  [[*W("south range", u, v)[:1], r4(TOPW + 3.0), W("south range", u, v)[1], r4(syaw_)] for u, v in ((10.0, 7.0), (21.0, 3.5))],
                            "_about": "chimney stacks"})

# ---- THE TURRETS: slender slate spikes corbelled out at the ranges' corners, two stair turrets on the court front
def bis_out(P, i, d):
    """corner i of an outline as the engine keeps it, moved d out along its bisector"""
    p, a, b = P[i], P[i - 1], P[(i + 1) % len(P)]
    u = ((a[0] - p[0]) / math.dist(a, p) + (b[0] - p[0]) / math.dist(b, p), (a[1] - p[1]) / math.dist(a, p) + (b[1] - p[1]) / math.dist(b, p))
    L = math.hypot(*u) or 1; s = -1 if inside(p[0] + u[0] / L * 0.3, p[1] + u[1] / L * 0.3, P) else 1
    return (r4(p[0] + s * u[0] / L * d), r4(p[1] + s * u[1] / L * d))
TURRETS = []
CORNERS = [("north wing", NA_out), ("north wing", N_JOG[1]), ("north wing", NA_in), ("north wing", K_in), ("west range", J_in), ("west range", M_in), ("south range", SB_in)]
for k, (nm, p) in enumerate(CORNERS):
    P = BODIES[nm]["pts"]; i = min(range(len(P)), key=lambda i: math.dist(P[i], p))
    c = bis_out(P, i, 0.55)
    TURRETS.append(add(f"corner turret {k + 1}", comp("cone-turret", {"sides": 8, "R": 1.25, "H": 4.4, "storeys": 1, "door": "no", "corH": 0.5, "corOut": 0.15, "capR": 1.6, "capRise": 6.0, "finial": 0.9},
                                                     [[c[0], r4(TOPW - 1.5), c[1], 0]], _about="a slender corner turret corbelled out at the wall head, its slate spike")))
    TURRETS.append(add(f"corner turret {k + 1} corbel", {"type": "column", "radius": 0.45, "height": 2.2, "sides": 8, "taper": 2.8, "at": [[c[0], r4(TOPW - 3.7), c[1], 0]]}))
for k, s in enumerate(STAIR_T):
    c = courtpt(s, 0.9)
    TURRETS.append(add(f"stair turret {k + 1}", comp("cone-turret", {"sides": 8, "R": 1.6, "H": r4(HW_ + 3.0), "storeys": 4, "door": "no", "corH": 0.6, "corOut": 0.18, "capR": 1.95, "capRise": 6.5, "finial": 1.0},
                                                    [[c[0], G, c[1], 0]], _about="a stair turret on the north wing's court front, rising over the battlements")))

# ---- THE TOWERS' HEADS over the ranges' wall heads (components/round-keep, castle-tower, cone-turret)
def keep(tw, y, about, **p):
    c, R, n = TOWERS[tw] if tw in TOWERS else (WT_C, 3.1, 12)
    return add(f"{tw} head", comp("round-keep", {"sides": n, "R": R, **p}, [[r4(c[0]), r4(y), r4(c[1]), 0]], _about=about))
TOWERHEADS = [keep("kaiserturm", TOPW, "the KAISERTURM's head: three storeys over the roofs, the corbelled gallery, the tall slate cone", H=9.5, storeys=3, crown="cone", capRise=13.0, t=0.8),
              keep("markgrafenturm", TOPW, "the MARKGRAFENTURM's head over the south-west corner: the gallery and the slate cone", H=7.0, storeys=2, crown="cone", capRise=13.5, t=0.8),
              keep("bischofsturm", TOPW, "the BISCHOFSTURM's round stage, crenellated round the square belfry stage that stands on it", H=6.0, storeys=2, crown="platform", t=0.8),
              keep("wartturm", TOPW, "the WARTTURM's head over the court, crenellated, the flag on its deck", H=9.5, storeys=2, crown="platform", flag="yes", Hg=2.4, t=0.55)]
BT = TOWERS["bischofsturm"]
TOWERHEADS.append(add("bischofsturm spire", comp("castle-tower", {"w": 6.0, "H": 12.0, "top": "spire", "clock": "no", "rise": 11.0, "lights": 2, "doorH": 1.4, "doorW": 1.0, "winW": 0.55},
                                                   [[BT[0][0], r4(TOPW + 6.0 + 3.2 + 0.45), BT[0][1], r4(yaw_of("north-west range"))]],
                                                   _about="the Bischofsturm's square upper stage: the belfry, the gables, the corner turrets, the tallest spire of the castle")))
MT = TOWERS["michaelsturm"]
TOWERHEADS.append(add("michaelsturm head", comp("cone-turret", {"sides": 12, "R": 4.3, "H": 3.6, "storeys": 1, "door": "no", "corH": 0.8, "corOut": 0.3, "capR": 4.9, "capRise": 7.5, "finial": 1.6, "t": 0.6},
                                                  [[MT[0][0], TOPW, MT[0][1], 0]], _about="the Michaelsturm's head: a short storey over the wall head, its tall cap")))
# the Torturm's head: machicolation, battlements, a corner turret at each corner, a hip roof
add("torturm machicolation", {"type": "prism", "plan": {"points": [list(p) for p in offset(TORT, 0.45)]}, "height": 0.9, "flatRoof": True, "at": [[0, r4(G + TOR_H - 0.9), 0, 0]],
                              "_about": "the corbelled course round the Torturm's head"})
BATTLEMENTS.extend(parapets(add, "torturm battlements", offset(TORT, 0.45), r4(G + TOR_H), h=1.2, step=1.8, t=0.5))
for k, p in enumerate(TORT):
    c = bis_out(TORT, k, 0.4)
    TURRETS.append(add(f"torturm turret {k + 1}", comp("cone-turret", {"sides": 8, "R": 1.1, "H": 3.6, "storeys": 1, "door": "no", "corH": 0.45, "corOut": 0.12, "capR": 1.4, "capRise": 4.6, "finial": 0.7},
                                                      [[c[0], r4(G + TOR_H - 1.6), c[1], 0]])))
td = (37.45 - 40.78, 6.38 + 2.86); tl = math.hypot(*td)
ROOFS.append(add("torturm roof", {"type": "roof", "form": "hip", "width": 5.4, "length": 9.0, "pitch": 55, "overhang": 0.2,
                                  "at": [[r4(TC[0]), r4(G + TOR_H), r4(TC[1]), r4(math.atan2(td[0] / tl, td[1] / tl))]], "_about": "the Torturm's slate roof inside its battlements"}))

# ---- THE CHAPELS' ROOFS AND STONEWORK
# the Christuskapelle: a steep slate roof, the apse under a half-octagon of it, buttresses with pinnacles, the flèche
CKR = add("christuskapelle roof", {"type": "roof", "form": "gable", "width": 9.4, "length": r4(CK_AX - 6.0), "pitch": 58, "overhang": 0.3,
                                   "at": [[r4((CK_AX + 6.0) / 2), r4(G + CKH), r4((CK_Z0 + CK_Z1) / 2), Q]], "_about": "the Christuskapelle's steep slate roof"})
CK_RISE = r4(4.7 * math.tan(math.radians(58)))
CKA_R = add("christuskapelle apse roof", {"type": "dome", "radius": r4(CK_R + 0.45), "thickness": 0, "sides": 8, "head": {"profile": "trigonal", "rise": CK_RISE},
                                          "at": [[CK_AX, r4(G + CKH), r4((CK_Z0 + CK_Z1) / 2), 0]], "_about": "the apse's slate roof"})
CK_PIN = []
for t in (-67.5, -22.5, 22.5, 67.5):
    d = (math.cos(math.radians(t)), math.sin(math.radians(t)))
    c = (CK_AX + d[0] * (CK_R + 0.35), (CK_Z0 + CK_Z1) / 2 + d[1] * (CK_R + 0.35))
    CK_PIN.append([r4(c[0]), r4(c[1]), r4(math.atan2(d[0], d[1]))])
CK_PIN += [[14.26, r4(CK_Z0 - 0.35), 0.0], [14.26, r4(CK_Z1 + 0.35), 0.0], [8.6, r4(CK_Z0 - 0.35), 0.0]]
add("christuskapelle buttresses", {"type": "box", "width": 0.7, "length": 0.9, "height": r4(CKH - 0.6), "at": [[x, G, z, yaw] for x, z, yaw in CK_PIN],
                                   "_about": "the buttresses between the windows"})
add("christuskapelle pinnacles", {"type": "pinnacle", "w": 0.6, "h": 1.4, "s": 2.4, "sides": 4, "at": [[x, r4(G + CKH - 0.6), z, yaw] for x, z, yaw in CK_PIN],
                                  "_about": "the pinnacles on the buttresses, red sandstone"})
add("christuskapelle fleche", {"type": "pinnacle", "w": 1.1, "h": 3.2, "s": 8.5, "sides": 8, "at": [[r4(CK_AX - 2.6), r4(G + CKH + CK_RISE - 1.6), r4((CK_Z0 + CK_Z1) / 2), 0]],
                               "_about": "the flèche over the chancel: an openwork lantern and a needle spire"})
# (inside: a painted ceiling under the roof, over nave and apse)
add("christuskapelle ceiling", {"type": "prism", "plan": {"points": [[r4(x), r4(z)] for x, z in offset(CK, -0.45)]}, "height": 0.3, "flatRoof": True,
                                "at": [[0, r4(G + CKH - 0.3), 0, 0]], "_about": "the ceiling over the vault and the apse"})
# St Michael's: a steep gable roof over the nave, a lower one over the chancel, the apse's half cone, the ridge turret
mvyaw = math.atan2(mu[0], mu[1])            # (a roof's ridge along the chapel)
c_n, c_c = MP(6.8, MW / 2), MP((13.6 + MA_C) / 2 - 0.1, MW / 2)
ROOFS.append(add("st michael's roof", {"type": "roof", "form": "gable", "width": r4(MW + 0.2), "length": 13.8, "pitch": 55, "overhang": 0.3,
                                       "at": [[c_n[0], r4(G + MCH), c_n[1], r4(mvyaw)]], "_about": "St Michael's steep roof"}))
ROOFS.append(add("st michael's chancel roof", {"type": "roof", "form": "gable", "width": 6.8, "length": r4(MA_C - 13.6 + 0.4), "pitch": 55, "overhang": 0.2,
                                               "at": [[c_c[0], r4(G + MCH), c_c[1], r4(mvyaw)]]}))
ca = MP(MA_C, MW / 2)
ROOFS.append(add("st michael's apse roof", {"type": "dome", "radius": r4(MA_R + 0.25), "thickness": 0, "sides": 16, "head": {"profile": "trigonal", "rise": r4(3.4 * math.tan(math.radians(55)))},
                                            "at": [[ca[0], r4(G + MCH), ca[1], 0]]}))
cw = MP(1.2, MW / 2)
add("st michael's ridge turret", {"type": "pinnacle", "w": 0.8, "h": 1.6, "s": 2.6, "sides": 6, "at": [[cw[0], r4(G + MCH + 4.65 * math.tan(math.radians(55)) - 0.9), cw[1], 0]],
                                  "_about": "the little bell turret on the west end of the ridge"})

# ---- THE KINGS ON THE SOUTH TERRACE, the kiosk in the outer court
KINGS = []
for k, u in enumerate((7.0, 11.0, 15.0)):
    p = W("south range", u, -3.2)
    KINGS.append(add(f"king {k + 1}", comp("pedestal", {"W": 1.3, "L": 1.3, "H": 2.0, "kind": "man", "style": "gothic", "stone": "bronze", "pose": "stand", "seed": k + 3},
                                           [[p[0], G, p[1], r4(syaw_ + math.pi)]], _about="a bronze king of Prussia on his pedestal on the south terrace")))
KIOSK = [(-9.85, 18.85), (-6.08, 10.66), (-3.77, 11.4), (-1.38, 12.35), (-5.28, 20.94)]
add("kiosk", {"type": "enclosure", "plan": {"points": [list(p) for p in outward(KIOSK)]}, "thickness": 0.4, "height": 3.6, "glass": True, "interior": True,
              "openings": {"pattern": "1", "width": 1.0, "sill": 0.9, "springing": 2.4, "head": SEG}, "courses": True, "at": [[0, G, 0, 0]],
              "_about": "the little house 'Unter den Linden' in the court below the chapels"})
ROOFS.append(add("kiosk roof", {"type": "roof", "form": "hip", "width": 4.2, "length": 9.0, "pitch": 45, "overhang": 0.3, "at": [[-5.6, r4(G + 3.6), 15.8, r4(math.atan2(3.6, -8.2))]]}))


# ================================================================================================ THE DOORS' LEAVES
# (doors.js hangs a leaf at the wall's face nearer the frame's origin -- here the origin lies in the court east of the
# castle, so `flip` is set wherever the inside is the farther face)
LEAVES = []
def leaf(nm, p, style, about, **kw):
    rec = min((d for d in DOORWAYS if d[0] == nm), key=lambda d: math.dist(d[2], p))
    P = BODIES[nm]["pts"]; i = rec[1]; a, b = P[i], P[(i + 1) % len(P)]; L = math.dist(a, b)
    o = (-(b[1] - a[1]) / L, (b[0] - a[0]) / L); t = BODIES[nm]["t"]
    q = rec[2]; inner = (q[0] - o[0] * t, q[1] - o[1] * t)
    e = {"_about": about, "part": nm, "near": [[r4(q[0] - o[0] * t / 2), r4(q[1] - o[1] * t / 2)]], "style": style, "color": "#3a2818", **kw}
    if math.hypot(*q) < math.hypot(*inner): e["flip"] = True        # (the engine takes the farther face for the outside)
    LEAVES.append(e)
leaf("north wing", courtpt(11.1), "gothic-great", "the door at the head of the Freitreppe, into the Stammbaumhalle", leafH=3.0)
leaf("north wing", NC_LINE(12.25), "gothic", "the north wing's door from the court to the state stair")
leaf("north wing", NC_LINE(22.0), "plain", "a door from the court into the north wing's ground floor")
leaf("north-west range", on_line(J_in, K_in, math.dist(J_in, K_in) / 2), "gothic", "the north-west range's door from the court")
leaf("south range", on_line(SB_in, M_in, math.dist(SB_in, M_in) * 0.45), "gothic", "the south range's door from the court")
leaf("christuskapelle", ((CK[0][0] + CK[1][0]) / 2, -8.2), "gothic-great", "the Christuskapelle's portal", leafH=3.2)
leaf("st michael's chapel", MP(4.5, MW), "gothic", "St Michael's door")
leaf("wartturm", wt_pt(90), "tower", "the Wartturm's door from the court")
leaf("gatehouse", ((43.8 + 40.78) / 2, (-10.8 - 2.86) / 2), "plain", "the gatehouse's door")

# ================================================================================================ THE FINISH
P0, P1 = r4(G + EY[1]), r4(G + EY[2])
_bb = [W("south range", u, v) for u in (19.0, 40.0) for v in (-2.0, 12.0)]
BLUE_BOX = [r4(min(p[0] for p in _bb)), r4(min(p[1] for p in _bb)), r4(max(p[0] for p in _bb)), r4(max(p[1] for p in _bb))]
_sb = [W("north wing", u, v) for u in (SB_U0, SB_U1) for v in (-3.6, 14.5)]
STAMM_BOX = [r4(min(p[0] for p in _sb)), r4(min(p[1] for p in _sb)), r4(max(p[0] for p in _sb)), r4(max(p[1] for p in _sb))]
TOWER_TOPS = [n for n in TOWERHEADS]
fin = {"name": "Burg Hohenzollern", "building": "architecture/hohenzollern",
       "_about": "Burg Hohenzollern: the walls of the castle and its bastions in the hill's own Jurassic limestone and sandstone, a muted buff-grey ashlar (warmer than the "
                 "'grey-white' it is often called; the photographs show buff and ochre), the window surrounds and the chapels' dressings a shade darker; dark blue-grey slate on "
                 "every roof, cone and spire; the Michaelsturm's cap and the flèche's lead; St Michael's chapel plastered white; the courts and the road in gravel and setts, the "
                 "summit's slopes grass. Inside: plastered walls, the Grafensaal's vaults ochre on grey marble columns, marble floors in the state rooms, flagstones in the chapels.",
       "stone": {"color": "#cbb68c", "accent": "#a08b64", "pat": "ashlar"},
       "rules": [
           {"parts": "kind:glass", "within": [4.0, -17.5, 21.0, -7.5], "opening": "tall", "map": "opening", "turn": 90, "pattern": "glass/medallion story", "palette": "chartres",
            "_about": "the Christuskapelle's windows in coloured glass"},
           {"parts": "kind:glass", "within": [4.0, -17.5, 21.0, -7.5], "map": "opening", "pattern": "glass/tracery diaper", "palette": "chartres"},
           {"parts": "kind:glass", "opening": "head", "map": "opening", "pattern": "glass/tracery diaper", "palette": "grisaille"},
           {"parts": "kind:glass", "map": "opening", "pattern": "glass/quarries", "palette": "grisaille", "_about": "leaded quarries"},
           # ---- THE STATE ROOMS on the principal floor (P0 its floor, CEIL1 its ceiling): walnut or oak dado, silk or painted walls over it, painted ceilings
           {"parts": ["stammbaumhalle beams"], "pattern": "timber/boards", "palette": "walnut", "_about": "dark oak beams"},
           {"parts": ["grafensaal vault"], "pattern": "painted/starry vault", "palette": "starry", "_about": "the Grafensaal's webs deep blue strewn with gold stars"},
           {"parts": ["grafensaal ribs", "grafensaal capitals", "grafensaal capital tops"], "pattern": "stone/plaster", "palette": "brass", "_about": "its ribs and capitals gilt"},
           {"parts": ["grafensaal columns"], "pattern": "stone/marble", "palette": "marble-green", "_about": "its columns of dark green marble"},
           {"parts": ["north-west range"], "surface": "wall", "side": "in", "above": P0 - 0.3, "below": P0 + 1.0, "pattern": "timber/panelling", "palette": "walnut", "align": "part",
            "_about": "the Grafensaal's walnut dado"},
           {"parts": ["north-west range"], "surface": "wall", "side": "in", "above": P0, "below": G_SPR, "pattern": "fabrics/damask", "palette": "damask-red", "scale": 3.0,
            "_about": "red silk damask over it"},
           {"parts": ["north-west range"], "surface": "wall", "side": "in", "above": P0, "below": P1, "pattern": "painted/starry vault", "palette": "starry", "_about": "the lunettes under the vault as its webs"},
           {"parts": ["north-west range floors"], "surface": "ceiling", "above": P0, "below": P1, "pattern": "painted/starry vault", "palette": "starry", "_about": "the flat ceiling beyond the vaults the same"},
           {"parts": ["north-west range floors"], "surface": "floor", "above": P0 - 0.5, "below": P0 + 0.5, "pattern": "floors/star and cross", "palette": "porphyry", "scale": 2.2,
            "_about": "the Grafensaal's floor: stars and crosses of coloured marble"},
           {"parts": ["north wing", "north wing wall"], "surface": "wall", "side": "in", "within": STAMM_BOX, "above": P0 - 0.3, "below": P0 + 1.0, "pattern": "timber/panelling", "palette": "oak",
            "align": "part", "_about": "the Stammbaumhalle's oak dado"},
           {"parts": ["north wing", "north wing wall"], "surface": "wall", "side": "in", "within": STAMM_BOX, "above": CEIL1 - 1.2, "below": P1, "pattern": "stone/tracery frieze", "palette": "gold",
            "align": "above", "_about": "a frieze of gilt blind tracery under its ceiling"},
           {"parts": ["north wing", "north wing wall"], "surface": "wall", "side": "in", "within": STAMM_BOX, "above": P0, "below": P1, "pattern": "stone/plaster", "palette": "plaster-red",
            "_about": "the Stammbaumhalle's red walls (the family tree painted on them)"},
           {"surface": "ceiling", "within": STAMM_BOX, "above": P0, "below": P1, "pattern": "timber/panelling", "palette": "walnut", "_about": "its ceiling panelled between the beams"},
           {"parts": ["north wing floor 1"], "surface": "floor", "within": STAMM_BOX, "pattern": "floors/opus sectile", "palette": "porphyry", "scale": 0.6, "_about": "its floor in coloured marble"},
           {"parts": ["west range", "south range", "south range wall"], "surface": "wall", "side": "in", "above": P0 - 0.3, "below": P0 + 1.0, "pattern": "timber/panelling", "palette": "oak",
            "align": "part", "_about": "an oak dado in the library and the royal rooms"},
           {"parts": ["west range"], "surface": "wall", "side": "in", "above": P0, "below": P1, "pattern": "fabrics/damask", "palette": "damask-green", "scale": 3.0, "_about": "the library in green silk"},
           {"parts": ["south range", "south range wall"], "surface": "wall", "side": "in", "within": BLUE_BOX, "above": P0, "below": P1, "pattern": "fabrics/brocade", "palette": "damask-blue", "scale": 3.0,
            "_about": "the Blue Salon"},
           {"parts": ["south range", "south range wall"], "surface": "wall", "side": "in", "above": P0, "below": P1, "pattern": "fabrics/damask", "palette": "damask-red", "scale": 3.0, "_about": "the king's rooms in red silk"},
           {"parts": ["west range floors", "south range floors"], "surface": "ceiling", "above": P0, "below": P1, "pattern": "timber/panelling", "palette": "oak", "_about": "panelled ceilings"},
           {"parts": ["west range floors", "south range floors", "north wing floor 1"], "surface": "floor", "above": P0 - 0.5, "below": P0 + 0.5, "pattern": "timber/herringbone", "palette": "oak",
            "_about": "herringbone parquet in the library, the royal rooms and the north wing's state rooms"},
           # ---- THE BASTIONS: a rougher, darker stone than the palace's; the plinth darker again, rusticated; the pilasters and the course in the palace's
           {"parts": ["bastion plinth"], "pattern": "stone/rusticated", "palette": "hohenzollern-plinth", "_about": "the battered plinth rusticated in dark stone"},
           {"parts": ["bastion gun loops", "bastion gun loop mouths"], "pattern": "stone/plaster", "palette": "ebony", "_about": "the loops' dark mouths"},
           {"parts": ["bastion course"], "pattern": "stone/ashlar", "palette": "sandstone"},
           {"parts": ["bastion pilaster"], "pattern": "stone/ashlar", "palette": "hohenzollern"},
           {"parts": ["zone A", "zone B", "zone C"], "surface": "wall", "pattern": "stone/ashlar", "palette": "hohenzollern-bastion", "scale": 1.25,
            "_about": "the bastions' faces in bigger, darker blocks than the palace's"},
           {"parts": BATTLEMENTS, "surface": "wall", "pattern": "stone/ashlar", "palette": "hohenzollern-bastion", "scale": 1.25},
           {"parts": ["michaelsturm head/cap", "christuskapelle fleche"], "surface": "roof", "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the Michaelsturm's cap and the flèche in green copper"},
           {"parts": ["kind:roof"], "surface": "wall", "pattern": "stone/ashlar", "palette": "hohenzollern", "_about": "the roofs' end triangles in the wall's stone"},
           {"parts": ["kind:roof", "kind:dome"], "pattern": "roofs/slate", "palette": "slate", "_about": "dark slate on every roof, cone and spire"},
           {"parts": ["bischofsturm spire/spire"], "pattern": "roofs/slate", "palette": "slate"},
           {"parts": ["chimneys"], "pattern": "stone/brick", "palette": "red-sandstone"},
           {"parts": ["kind:moulding"], "pattern": "stone/ashlar", "palette": "sandstone", "_about": "the window surrounds and courses a shade darker and warmer"},
           {"parts": ["st michael's chapel"], "surface": "wall", "side": "out", "pattern": "stone/plaster", "palette": "plaster-white", "_about": "St Michael's plastered walls"},
           {"parts": ["hilltop", "summit", "rampenturm well"], "pattern": "materials/grass", "palette": "lawn", "_about": "the summit's grassy slopes, the Rampenturm's well"},
           {"parts": ROADS, "surface": "floor", "pattern": "stone/sand", "palette": "gravel", "_about": "the ramp's surface"},
           {"parts": ["zone A", "zone B", "zone C"], "surface": "floor", "pattern": "floors/flagstones", "palette": "sandstone-grey", "_about": "the courts and terraces paved"},
           {"parts": ["christuskapelle ceiling"], "pattern": "stone/plaster", "palette": "plaster-byzantine", "_about": "the chapel's painted ceiling"},
           {"parts": ["christuskapelle", "st michael's chapel"], "surface": "floor", "side": "in", "pattern": "floors/flagstones", "palette": "sandstone"},
           {"surface": "floor", "side": "in", "above": G + 1.0, "pattern": "timber/boards", "palette": "oak", "_about": "board floors upstairs"},
           {"surface": "floor", "side": "in", "pattern": "floors/flagstones", "palette": "sandstone", "_about": "flagstones on the ground floor"},
           {"surface": "ceiling", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
           {"surface": "floor", "pattern": "floors/flagstones", "palette": "sandstone-grey"},
           {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
           {"surface": "wall", "pattern": "stone/ashlar", "palette": "hohenzollern", "_about": "buff-grey ashlar"}]}
doors_doc = {"name": "Burg Hohenzollern: doors", "building": "hohenzollern",
             "_about": "Burg Hohenzollern: the Freitreppe's door into the Stammbaumhalle, the ranges' doors from the court, the chapels' portals, the Wartturm's door -- dark oak",
             "doors": LEAVES}


# ================================================================================================ OUT
doc = {"name": "Burg Hohenzollern",
       "_about": "BURG HOHENZOLLERN (1850-67, Friedrich August Stüler for King Friedrich Wilhelm IV; the fortifications by Moritz von Prittwitz) on the summit of the "
                 "Hohenzollern, after OpenStreetMap's plan: the bastion ring; the serpentine approach through the Adlertor (twice), round the Wilhelmsturm and the lower "
                 "Zwinger, and the Rampenturm's spiral; the Torturm; the four ranges round the inner court with the Kaiser-, Bischofs-, Markgrafen-, Michaels- and Wartturm; "
                 "the Christuskapelle and St Michael's chapel. Walkable: the courtyards and the ramp, the principal floor's Stammbaumhalle, Grafensaal (rib vaults on columns), "
                 "library, the royal rooms, the chapels, the upper floor; the state stair and the Wartturm's spiral between the floors. Generated by tools/archgen/hohenzollern.py.",
       "params": {"detail": 4}, "build": build, "parts": parts}
if __name__ == "__main__":
    write_castle_components()
    open(os.path.join(ROOT, "assets/architecture/hohenzollern.json"), "w").write(json.dumps(doc, indent=1) + "\n")
    open(os.path.join(ROOT, "assets/finishes/hohenzollern.json"), "w").write(json.dumps(fin, indent=1) + "\n")
    open(os.path.join(ROOT, "assets/doors/hohenzollern.json"), "w").write(json.dumps(doors_doc, indent=1) + "\n")
    print("hohenzollern:", len(parts), "parts")
