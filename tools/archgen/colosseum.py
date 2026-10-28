# THE FLAVIAN AMPHITHEATRE (the Colosseum, Rome, AD 70-80) at its real size, built as its masons built it: on an OVAL OF
# FOUR CENTRES (assemble.js ovalOf -- the 3-4-5 layout Trevisan read from the building: 188 x 156m outside, an arena of
# 86 x 54, the cavea 51m deep all round), eighty bays, the main entrances on the two axes.
#   THE SECTION, from the facade in (s, metres in from the outer face; every ring an offset of the same four centres):
#     outer wall 0-2.4 (four storeys: Tuscan, Ionic and Corinthian arcades, the attic with its windows and pilasters),
#     ambulatory I 2.4-7.4, ring B, ambulatory II 9.2-14, ring C, the radial zone 15.8-28 (the masonry the cavea rests on,
#     cut by the passages), ring D, ambulatory III 29.6-32.6, ring E, the inner radial zone, the podium wall at 50.2-51.
#   THE LEVELS: the ground 0.2, the first floor 10.5, the second 22.4, the summa cavea 34.0 -- each the top of a facade
#   storey. The CAVEA is three maeniana and each ends on a level: the first rises from the podium (4.0) to a walkway at
#   10.5, the second from a high wall behind that walkway to a walkway at 22.4, the third from another wall to 34.0, where
#   the portico in summa cavea runs round under the attic. So every vomitorium is a LEVEL passage from an ambulatory out
#   through a maenianum's wall onto the walkway in front of it, and the seating is walked down from there (the first
#   maenianum also by a stair that climbs under it from ambulatory III and opens among its rows).
#   THE STAIRS between the levels climb ALONG ambulatory I on its inner half, three bays long: the floor above is open
#   over the last bay of the flight (a slab of its own over the outer half), the vault left out over the two it climbs
#   through and a flat ceiling put in their place.
#   THE MAIN ENTRANCES on the axes run through to the arena under the seating -- on the long axis, where the bays have
#   drawn together to a metre at the podium, as wide as three of them; under the arena the HYPOGEUM, its corridors 6m
#   down, reached by a stair at each end of the long axis through the arena floor.
#   Masses are SOLID (the seating is the top of its masonry, carried down to what it stands on); every passage is the
#   void left between solids, so the walk and its walls are read from the stone. Numbers are worked here and written as
#   numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
r4 = lambda v: round(v, 4)

# ---------------------------------------------------------------- the oval
NE, NS = 15, 25                       # bays in an end arc, in a side arc (odd: a bay on each axis)
AO, BO, CAV = 94.0, 78.0, 51.0        # the semi-axes outside, the cavea's depth
def layout(al):                       # the arena's half-axes (AO - CAV, BO - CAV) on an oval whose end arcs span 2 al
    c = (AO - BO) / (1 + math.tan(al) - 1 / math.cos(al))
    return c, c * math.tan(al), AO - c        # (r1: the end arcs' radius at the facade)
def misfit(al):                       # an end arc's facade bay less a side arc's: the half-angle that makes them equal
    c, d, r1 = layout(al); K = math.hypot(c, d)
    return r1 * 2 * al / NE - (r1 + K) * (math.pi - 2 * al) / NS
lo, hi = math.radians(35), math.radians(55)
for _ in range(60):
    m = (lo + hi) / 2
    lo, hi = (lo, m) if misfit(m) > 0 else (m, hi)
C_, D_, RO = (round(v, 3) for v in layout((lo + hi) / 2))
K = math.hypot(C_, D_); AL = math.atan2(D_, C_); BE = math.pi / 2 - AL
OVAL = {"c": C_, "d": D_, "ends": NE, "sides": NS}
N = 2 * (NE + NS)
ARCS = [(NE, 2 * AL / NE, math.pi / 2 - AL, (C_, 0), False), (NS, 2 * BE / NS, math.pi / 2 + AL, (0, D_), True),
        (NE, 2 * AL / NE, 3 * math.pi / 2 - AL, (-C_, 0), False), (NS, 2 * BE / NS, 3 * math.pi / 2 + AL, (0, -D_), True)]
def bay(k):                           # (as assemble.js ovalOf: the bay's yaw, its angle, its arc's centre, a side arc?)
    g = (k + (NE - 1) // 2) % N
    for n, a, y0, C, side in ARCS:
        if g < n: return {"yaw": y0 + (g + .5) * a, "a": a, "C": C, "side": side}
        g -= n
def rad(s, side): return RO - s + (K if side else 0)
def at_angle(k, s, f):                # the point s in from the facade on the ray f of the way across bay k (-.5 .. .5)
    b = bay(k); R = rad(s, b["side"]); y = b["yaw"] + f * b["a"]
    return (b["C"][0] + R * math.sin(y), b["C"][1] + R * math.cos(y))
def bw(k, s): b = bay(k); return rad(s, b["side"]) * b["a"]     # a bay's width at s

def oring(name, typ, s_in, s_out, **kw):
    # (a ring's faces flat across each bay, chord to chord -- as a vault, a slab or a block of seating is cut, between
    #  the bay's radial planes: a wall that followed the arc stood off them by the arc's rise, 5-7cm in mid-bay, a slit
    #  open to the sky between the facade and every floor)
    d = {"type": typ, "oval": OVAL, "rInner": r4(RO - s_in), "rOuter": r4(RO - s_out)}
    if typ == "ring": d["polygon"] = True
    d.update(kw); add(name, d)

BAYS = list(range(N))
E = [0, 20, 40, 60]                                       # the main entrances, on the axes
EMAJ = [79, 0, 1, 39, 40, 41]                             # the long axis's, three bays wide inside ring E
EMIN = [20, 60]
SIDE = [k for k in BAYS if bay(k)["side"]]
V = [k for k in SIDE if k % 4 == 0 and k not in E]        # the vomitoria: every fourth bay of the side arcs
STAIR = {1: [14, 26, 54, 66], 2: [10, 30, 50, 70], 3: [18, 22, 58, 62]}   # the stairs up to each level, by the bay they centre on
def not_(*ls): return [k for k in BAYS if not any(k in l for l in ls)]

# ---------------------------------------------------------------- the measures
L0, L1, L2, L3 = 0.2, 10.5, 22.4, 34.0
SLAB = 0.15
S_A, S_AMB1, S_B, S_AMB2, S_C, S_D, S_AMB3, S_E = 2.4, 7.4, 9.2, 14.0, 15.8, 28.0, 29.6, 32.6
S_RZ2, S_POD, S_PW, S_AR = 34.2, 47.4, 50.2, 51.0          # ring E's inner face, the podium's edge, its wall, the arena
S_MID = (S_A + S_AMB1) / 2                                   # the middle of ambulatory I: the stairs climb on its inner half
PODY = 4.0
N1, N2, N3 = 13, 20, 20
WALK = 1.4                                                   # the walkways (praecinctiones)
RUN = (S_POD - S_AMB1 - 2 * WALK) / (N1 + N2 + N3)          # one row's tread, all three maeniana: the third ends on ring B
S_M1o = S_POD - N1 * RUN; S_P1o = S_M1o - WALK               # the first maenianum from the podium out, its walkway
S_M2o = S_P1o - N2 * RUN; S_P2o = S_M2o - WALK
R1 = (L1 - PODY) / N1
M2_FIRST, M3_FIRST = 13.3, 25.2                              # the first rows over their walls: a passage's height and a slab
R2 = (L2 - M2_FIRST) / (N2 - 1); R3 = (L3 - M3_FIRST) / (N3 - 1)
PASS, PASS_H = 3.0, 2.4                                      # a vomitorium passage
FLIGHT = 2.4                                                 # the stair under the first maenianum
EW, EH = 2.8, 3.7                                            # a main entrance's passage, its height under the seating

# ---------------------------------------------------------------- helpers
def block(name, s_in, s_out, y0, y1, at, plan="wedge", width=None, mirror=False, **kw):
    """a solid between two depths and two heights, in some bays: `wedge` the whole bay, `parallel` a strip a passage wide
    down its middle, `flank` the bay beside such a strip (`mirror`: both sides)"""
    d = {"run": r4(s_in - s_out), "rising": "out", "base": r4(y0), "top": r4(y1), "steps": 1, "at": at}
    if plan != "wedge": d["plan"] = plan; d["width"] = width
    if mirror: d["mirror"] = True
    d.update(kw)
    oring(name, "steps", s_in, s_out, **d)
def seats(name, s_in, n, base, first, top, at, landing=0.0, plan="wedge", width=None, mirror=False, soffit=None, **kw):
    """n rows of seating rising outward from s_in, the first tread at `first`, the last at `top`; `landing` carries the
    last tread on out (a walkway, and the mass under it); solid down to `base` (or to the slope `soffit` [in, out])"""
    d = {"run": r4(RUN), "rising": "out", "base": r4(base), "first": r4(first - base), "top": r4(top), "steps": n, "at": at}
    if landing: d["landing"] = r4(landing)
    if plan != "wedge": d["plan"] = plan; d["width"] = width
    if mirror: d["mirror"] = True
    if soffit: d["soffit"] = [r4(soffit[0]), r4(soffit[1])]
    d.update(kw)
    oring(name, "steps", s_in, r4(s_in - n * RUN), **d)
def ring_storey(name, s_in, s_out, y0, y1, opening, at, blind=None, **kw):
    """a ring wall between two heights: its opening in the bays `at`, blind in the bays `blind`"""
    base = {"height": r4(y1 - y0), "y": r4(y0)}; base.update(kw)
    if at: oring(name, "ring", s_in, s_out, opening=opening, at=at, **base)
    if blind: oring(name + " blind", "ring", s_in, s_out, solid=True, at=blind, **base)
arch = lambda w, crown: {"width": w, "springing": r4(crown - w / 2), "head": {"profile": "semicircular"}}
flat = lambda w, top, sill=0: {"width": w, "sill": sill, "springing": r4(top), "head": {"profile": "flat"}}

# ---------------------------------------------------------------- the ground, the arena, the hypogeum
oring("ground floor", "ring", S_PW, 0, height=L0, y=0, solid=True, walked=True,
      _about="the paving of every ground-floor space, from the facade to the podium wall (the masses stand on it)")
def outline(s, notch=None):
    """the arena's outline s in from the facade, four points a bay; `notch` (x0, hw): open where |x| > x0 and |z| < hw,
    at both ends of the long axis -- where the stairs go down through the floor"""
    pts = []
    for k in BAYS:
        for j in range(4): pts.append(at_angle(k, s, -.5 + j / 4))
    if not notch: return [[r4(x), r4(z)] for x, z in pts]
    x0, hw = notch
    cut = lambda p: abs(p[1]) < hw and abs(p[0]) > x0
    out = []
    for i, p in enumerate(pts):
        if cut(p): continue
        out.append(p)
        q = pts[(i + 1) % len(pts)]
        if cut(q):                    # into a notch: along its near edge, across its inner end, back out along its far one
            j = i + 1
            while cut(pts[j % len(pts)]): j += 1
            r = pts[j % len(pts)]
            sx, z1, z2 = math.copysign(1, q[0]), math.copysign(hw, p[1]), math.copysign(hw, r[1])
            xe = lambda a, b, z: a[0] + (b[0] - a[0]) * (z - a[1]) / (b[1] - a[1])
            out += [(xe(p, q, z1), z1), (sx * x0, z1), (sx * x0, z2), (xe(pts[(j - 1) % len(pts)], r, z2), z2)]
    return [[r4(x), r4(z)] for x, z in out]
AREND = RO - S_AR + C_                                       # the arena's half-length on its long axis
HY = -6.0                                                    # the hypogeum's floor
HSTEPS, HRUN, HW = 32, 0.28, 2.4                             # its stairs
NOTCH = (AREND - 5.0, HW / 2)
add("arena floor", {"type": "prism", "plan": {"points": outline(S_AR - 0.05, NOTCH)}, "height": 0.3, "at": [[0, 0.2, 0, 0]], "walked": True,
                    "_about": "the boards the games were fought on, over the hypogeum, the sand on them; open at each end of the long axis where a stair goes down"})
add("hypogeum floor", {"type": "prism", "plan": {"points": outline(S_AR - 0.05)}, "height": 0.3, "at": [[0, HY - 0.3, 0, 0]]})
oring("hypogeum wall", "ring", S_AR, S_PW, height=r4(L0 - HY), y=HY, solid=True,
      _about="the arena's wall carried down to the hypogeum's floor: its corridors' outer wall")
oring("podium wall", "ring", S_AR, S_PW, height=r4(PODY + 1.1 - L0), y=L0, solid=True, skip=EMAJ + EMIN,
      _about="the wall the games are fought in front of, from the sand to the podium's parapet")
oring("podium gates", "ring", S_AR, S_PW, height=r4(PODY + 1.1 - L0), y=L0, at=EMIN, opening=flat(EW, EH - L0),
      _about="where the minor axis's passages come out on the sand (the long axis's are three bays wide there, and have no wall)")
# the hypogeum: a corridor down the long axis and four more either side of it, their walls broken by doorways
HWALL = [1.6, 5.4, 9.2, 13.0, 16.8]
def reach(z, s):                      # how far the outline s in from the facade reaches along x at a given z
    best = 0
    for k in BAYS:
        for j in range(17):
            x, zz = at_angle(k, s, -.5 + j / 16)
            if abs(zz - z) < .3 and x > best: best = x
    return best
by_len = {}
for zl in HWALL:
    X = reach(zl, S_AR + 2.5)
    if X < 6: continue
    n = max(1, round(2 * X / 9)); seg = 2 * X / n
    for i in range(n):
        a = -X + i * seg + (0.6 if i else 0); b_ = -X + (i + 1) * seg - (0.6 if i + 1 < n else 0)
        for sz in (1, -1): by_len.setdefault(r4(b_ - a), []).append([r4((a + b_) / 2), HY, r4(sz * zl), 0])
for j, (l, at) in enumerate(sorted(by_len.items())):
    add(f"hypogeum wall {j + 1}", {"type": "box", "width": l, "length": 0.8, "height": r4(L0 - HY), "at": at,
                                   "_about": "the walls of the hypogeum's corridors, under the arena floor, doorways through them every nine metres"})
for sx, nm in ((1, "east"), (-1, "west")):
    x0 = AREND - 1.2 - HSTEPS * HRUN                         # (its landing at the top reaches the podium wall)
    add(f"hypogeum stair {nm}", {"type": "flight", "width": HW, "run": HRUN, "steps": HSTEPS, "base": HY, "top": 0.5, "landing": 1.2,
                                   "at": [[r4(sx * x0), 0, r4(sx * HW / 2), 0 if sx > 0 else r4(math.pi)]],
                                   "_about": "down from the end of the arena to the hypogeum's middle corridor, under the boards"})

build.remove("arena floor"); build.append("arena floor")      # (laid when the walls under it stand)

# ---------------------------------------------------------------- the facade
oring("arcade I", "ring", S_A, 0, height=L1, y=0, opening={"width": 4.2, "springing": 4.9, "head": {"profile": "semicircular"}},
      orders=[{"kind": "tuscan"}], _about="the ground storey: eighty arches, each numbered over its keystone but the four on the axes")
oring("arcade II", "ring", S_A, 0, height=r4(L2 - L1), y=L1, opening={"width": 4.2, "sill": 1.1, "springing": 6.6, "head": {"profile": "semicircular"}},
      orders=[{"kind": "ionic"}], _about="the second storey, Ionic: a parapet in each arch, where a statue stood")
oring("arcade III", "ring", S_A, 0, height=r4(L3 - L2), y=L2, opening={"width": 4.2, "sill": 1.1, "springing": 6.35, "head": {"profile": "semicircular"}},
      orders=[{"kind": "corinthian"}], _about="the third storey, Corinthian")
ATT = 48.5 - L3
oring("attic", "ring", S_A, 0, height=ATT, y=L3, every=2, offset=0, opening=flat(1.2, 6.2, 4.2),
      orders=[{"kind": "corinthian"}], _about="the attic: flat Corinthian pilasters, a window in every other bay lighting the portico behind it")
oring("attic blind", "ring", S_A, 0, height=ATT, y=L3, every=2, offset=0, only="every", solid=True,
      orders=[{"kind": "corinthian"}], _about="the attic's other bays, where the bronze shields hung")

# ---------------------------------------------------------------- the floors, the vaults they lie on, the stairs between
def wells(lv): return [k + 1 for k in STAIR[lv]]                 # the bay the stair arrives through
def climbs(lv): return [k + j for k in STAIR[lv] for j in (-1, 0, 1)]
PAR, PAR_H = 0.25, 1.0                                           # a parapet's thickness, its height over the floor
for lv, y, s_in in ((1, L1, S_RZ2), (2, L2, S_C), (3, L3, S_AMB1)):
    nm = {1: "first floor", 2: "second floor", 3: "summa cavea"}[lv]
    oring(nm, "ring", s_in, S_A, height=SLAB, y=r4(y - SLAB), solid=True, walked=True, skip=wells(lv),
          _about=f"the floor at {y}m, from the outer wall in")
    if s_in > S_AMB1:
        oring(f"{nm} beside the well", "ring", s_in, S_AMB1, height=SLAB, y=r4(y - SLAB), solid=True, walked=True, at=wells(lv),
              _about="the floor inside ambulatory I where the stair comes up through it")
    oring(f"{nm} over the well", "ring", S_MID, S_A, height=1.0, y=r4(y - 1.0), solid=True, walked=True, at=wells(lv),
          _about="the outer half of the floor where the stair comes up: a slab of its own, there being no vault under it")
    # THE WELL'S PARAPETS: round the hole the stair comes up through, on its three sides that drop -- along the outer
    # half's edge, along the inner wall's top, and across the end over the bay before (the flat ceiling's top); the
    # fourth is where the stair arrives
    oring(f"{nm} well parapet", "ring", S_MID, r4(S_MID - PAR), height=PAR_H, y=y, solid=True, at=wells(lv),
          _about="along the edge of the floor beside the stair's last bay")
    oring(f"{nm} well parapet inside", "ring", r4(S_AMB1 + PAR), S_AMB1, height=PAR_H, y=y, solid=True, at=wells(lv),
          _about="along the inner side of the hole, on the floor (the top row of the seating at the summa cavea)")
    ends = []
    for k in STAIR[lv]:
        b = bay(k); sc = (S_MID + S_AMB1) / 2; R = rad(sc, b["side"]); ya = b["yaw"] + b["a"] / 2 - PAR / 2 / R
        ends.append([r4(ya), r4(b["C"][0] + R * math.sin(ya)), y, r4(b["C"][1] + R * math.cos(ya))])
    add(f"{nm} well parapet across", {"type": "box", "width": PAR, "length": r4(S_AMB1 - S_MID + 2 * PAR), "height": PAR_H,
                                       "at": [[x, y_, z, a] for a, x, y_, z in ends],
                                       "_about": "across the hole's end, on the flat ceiling over the bay the stair climbs through before"})
for lv, (y0, top, spring) in enumerate(((L0, L1, 7.0), (L1, L2, 19.2), (L2, L3, 30.85)), 1):
    oring(f"ambulatory I vault {lv}", "vault", S_AMB1, S_A, springing=spring, clears=spring, top=r4(top - SLAB),
          skip=[k + j for k in STAIR[lv] for j in (0, 1)], head={"profile": "semicircular"}, _about="the barrel vault round ambulatory I")
    oring(f"ambulatory I ceiling {lv}", "ring", S_AMB1, S_A, height=r4(1.0 - SLAB), y=r4(top - 1.0), solid=True, at=STAIR[lv],
          _about="flat over the bay the stair climbs through, the vault left out")
    n = round((top - y0) / 0.2)
    rarc = RO - (S_MID + S_AMB1) / 2
    run = 3 * (2 * BE / NS) * (rarc + K) / n                 # (three side-arc bays long on its walking line)
    to = ['', 'the first floor', 'the second floor', 'the summa cavea'][lv]
    oring(f"stair to {to}", "steps", S_AMB1 + 0.1, r4(S_MID + PAR),
          plan="along", rArc=r4(rarc), run=r4(run), rising="out", base=r4(y0), top=r4(top), steps=n, use="stair", at=STAIR[lv],
          _about="up along ambulatory I on its inner half, three bays long, into the floor above through the bay it arrives in")
    # its open side, toward the outer half of the ambulatory: a parapet stepping up with it a metre over every tread
    # (the same steps on the same walking line, so tread for tread)
    oring(f"stair to {to} parapet", "steps", r4(S_MID + PAR), S_MID,
          plan="along", rArc=r4(rarc), run=r4(run), rising="out", base=r4(y0), first=r4((top - y0) / n + PAR_H), top=r4(top + PAR_H),
          steps=n, at=STAIR[lv], _about="the parapet on the stair's open side, stepping up with it")
for lv, (top, spring) in enumerate(((L1, 7.0), (L2, 19.2)), 1):
    oring(f"ambulatory II vault {lv}", "vault", S_AMB2, S_B, springing=spring, clears=spring, top=r4(top - SLAB), head={"profile": "semicircular"})
oring("ambulatory III vault", "vault", S_E, S_AMB3, springing=7.0, clears=7.0, top=r4(L1 - SLAB), head={"profile": "semicircular"})

# ---------------------------------------------------------------- the rings within
ring_storey("ring B", S_B, S_AMB1, 0, L1 - SLAB, arch(3.6, 7.0), at=not_(climbs(1)), blind=climbs(1))
ring_storey("ring B 1", S_B, S_AMB1, L1, L2 - SLAB, arch(3.6, 8.7), at=not_(climbs(2)), blind=climbs(2))
ring_storey("ring C", S_C, S_AMB2, 0, L1 - SLAB, arch(PASS, 6.5), at=V + E, blind=not_(V, E))
ring_storey("ring C 1", S_C, S_AMB2, L1, L2 - SLAB, flat(PASS, PASS_H), at=V, blind=not_(V))
ring_storey("ring D", S_AMB3, S_D, 0, L1 - SLAB, arch(PASS, 6.5), at=V + E, blind=not_(V, E))
ring_storey("ring E", S_RZ2, S_E, 0, L1 - SLAB, flat(FLIGHT, 3.2), at=V, blind=not_(V, EMAJ, EMIN))
ring_storey("ring E entrance", S_RZ2, S_E, 0, L1 - SLAB, flat(EW, EH), at=EMIN)

# ---------------------------------------------------------------- the masses: the radial zones, the seating, the podium
# the radial zone on the ground floor: masonry, but for the passages through it
block("radial zone", S_D, S_C, L0, L1 - SLAB, not_(V, E))
block("radial zone beside the passage", S_D, S_C, L0, L1 - SLAB, V, plan="flank", width=PASS, mirror=True)
block("radial zone beside the entrance", S_D, S_C, L0, L1 - SLAB, E, plan="flank", width=EW, mirror=True)
# (the passages' ceilings, level with the crowns of the arches they run between)
block("radial zone over the passage", S_D, S_C, 6.5, L1 - SLAB, V, plan="parallel", width=PASS)
block("radial zone over the entrance", S_D, S_C, 6.5, L1 - SLAB, E, plan="parallel", width=EW)
# ...on the first floor: masonry up to the second walkway, but for the level passages out to the first
block("upper radial zone", S_P2o, S_C, L1, L2, not_(V))
block("upper radial zone beside the passage", S_P2o, S_C, L1, L2, V, plan="flank", width=PASS, mirror=True)
block("upper radial zone over the passage", S_P2o, S_C, L1 + PASS_H, L2, V, plan="parallel", width=PASS)
# THE FIRST MAENIANUM, from the podium out to its walkway, the mass under the walkway carried out to ring E; solid to the
# ground but where its stair climbs under it and the main entrances pass
FILL = WALK + (S_P1o - S_RZ2)
J0 = 6                                                        # the row the stair arrives at
s_top = S_POD - J0 * RUN; y_top = PODY + J0 * R1
FL_N = round((y_top - L0) / 0.2); FL_RUN = (s_top - S_RZ2) / FL_N; FL_SLOPE = (y_top - L0) / (s_top - S_RZ2)
oring("stair to the first maenianum", "steps", s_top, S_RZ2, run=math.floor(FL_RUN * 1e4) / 1e4,   # (rounded down: all the treads fit)
      rising="in", base=L0, top=r4(y_top), steps=FL_N,
      plan="parallel", width=FLIGHT, use="stair", at=V, _about="from ambulatory III up under the seating, opening in its sixth row")
M1_PLAIN = not_(V, EMAJ, EMIN)
seats("first maenianum", S_POD, N1, L0, PODY + R1, L1, M1_PLAIN, landing=FILL)
seats("first maenianum beside the stair", S_POD, N1, L0, PODY + R1, L1, V, landing=FILL, plan="flank", width=FLIGHT, mirror=True)
seats("first maenianum below the stair's mouth", S_POD, J0, L0, PODY + R1, y_top, V, plan="parallel", width=FLIGHT)
J1 = J0 + 3                                                   # three rows of open mouth over the flight's top
s1 = S_POD - J1 * RUN
soff = lambda s: L0 + (s - S_RZ2) * FL_SLOPE + 2.4            # (a head's height over the nosings, and a hand)
seats("first maenianum over the stair", s1, N1 - J1, L0, PODY + (J1 + 1) * R1, L1, V, landing=FILL, plan="parallel", width=FLIGHT,
      soffit=(soff(s1), soff(S_RZ2)))
seats("first maenianum beside the entrance", S_POD, N1, L0, PODY + R1, L1, EMIN, landing=FILL, plan="flank", width=EW, mirror=True)
seats("first maenianum over the entrance", S_POD, N1, EH, PODY + R1, L1, EMIN, landing=FILL, plan="parallel", width=EW)
seats("first maenianum over the long axis", S_POD, N1, EH, PODY + R1, L1, EMAJ, landing=FILL,
      _about="over the long axis's entrances, three bays of seating carried on the passage's flat roof")
# THE SECOND MAENIANUM over its wall, and its walkway at 22.4 -- solid to the first floor but over the passages
seats("second maenianum", S_P1o, N2, L1, M2_FIRST, L2, not_(V), landing=WALK)
seats("second maenianum beside the passage", S_P1o, N2, L1, M2_FIRST, L2, V, landing=WALK, plan="flank", width=PASS, mirror=True)
seats("second maenianum over the passage", S_P1o, N2, L1 + PASS_H, M2_FIRST, L2, V, landing=WALK, plan="parallel", width=PASS)
# THE THIRD MAENIANUM, out to the summa cavea, on the second floor over ambulatory II and ring C
seats("third maenianum", S_P2o, N3, L2, M3_FIRST, L3, not_(V))
seats("third maenianum beside the passage", S_P2o, N3, L2, M3_FIRST, L3, V, plan="flank", width=PASS, mirror=True)
seats("third maenianum over the passage", S_P2o, N3, L2 + PASS_H, M3_FIRST, L3, V, plan="parallel", width=PASS)
# THE PODIUM: a terrace round the arena at 4m, the senators' seats
block("podium", S_PW, S_POD, L0, PODY, not_(EMAJ, EMIN))
block("podium beside the entrance", S_PW, S_POD, L0, PODY, EMIN, plan="flank", width=EW, mirror=True)
block("podium over the entrance", S_PW, S_POD, EH, PODY, EMIN, plan="parallel", width=EW)
block("podium over the long axis", S_PW, S_POD, EH, PODY, EMAJ)

# ---------------------------------------------------------------- the portico in summa cavea
COLS = 42.6
cols = []
for k in BAYS:
    if k in STAIR[3] or k in wells(3): continue              # (none either side of the hole the stair comes up through)
    x, z = at_angle(k, S_AMB1 - 0.6, .5)
    cols.append([r4(x), L3, r4(z), 0])
add("portico columns", {"type": "column", "radius": 0.42, "height": r4(COLS - L3), "at": cols,
                        "_about": "the colonnade round the top of the cavea, a column on every bay's line but where a stair comes up"})
oring("portico architrave", "ring", S_AMB1, S_AMB1 - 1.2, height=1.2, y=COLS, solid=True)
oring("portico roof", "ring", S_AMB1, S_A, height=0.5, y=r4(COLS + 1.2), solid=True, flatRoof=True,
      _about="the portico's roof, against the attic: its flat top the place the velarium's sailors worked from")

# ---------------------------------------------------------------- the interiors
# THE SPACES UNDER THE CAVEA, for the finishes (inside: brick-faced, plastered; outside: travertine): drawn on the middle
# of the walls round them (the facade's at 1.2, ring C's, ring E's), a vertex on every bay's radial plane as the rings
# are; the masses between the passages are solid, so a band takes them in with the passages through them. The cavea, its
# walkways and the arena are the open air, the portico in summa cavea an open colonnade: outside.
def band(s):                          # the oval s in from the facade, chord to chord across the bays
    return [[r4(x), r4(z)] for x, z in (at_angle(k, s, -.5) for k in BAYS)]
def interior(name, s_out, s_in, y0, y1, about):
    d = {"type": "interior", "plan": {"points": band(s_out)}}
    if s_in is not None: d["hole"] = {"points": band(s_in)}
    d.update({"height": r4(y1 - y0), "at": [[0, r4(y0), 0, 0]], "_about": about}); parts[name] = d
def strip(k, s_out, s_in, y0):        # a passage down the middle of bay k: its rect's length, its placement
    b = bay(k); sm = (s_out + s_in) / 2; R = rad(sm, b["side"])
    return r4(s_in - s_out), [r4(b["C"][0] + R * math.sin(b["yaw"])), r4(y0), r4(b["C"][1] + R * math.cos(b["yaw"])), r4(b["yaw"])]
MID_C, MID_E, MID_PW = (S_AMB2 + S_C) / 2, (S_RZ2 + S_E) / 2, (S_AR + S_PW) / 2
interior("ground storey", S_A / 2, MID_E, 0, L1, "ambulatories I-III, the radial passages between them and the solid masses round those, from the facade's middle to ring E's")
interior("first storey", S_A / 2, MID_C, L1, L2, "ambulatories I and II on the first floor, to ring C's middle")
interior("first storey passages", MID_C, S_P1o, L1, L1 + PASS_H, "the level vomitoria out through the upper radial zone onto the first walkway (the mass between them solid)")
interior("second storey", S_A / 2, S_AMB1 + .35, L2, L3, "ambulatory I on the second floor, to just inside the third maenianum's back (its top rows over it stand clear)")
interior("second storey passages", S_AMB1 + .35, S_P2o, L2, L2 + PASS_H, "the level vomitoria out through the third maenianum onto the second walkway")
interior("hypogeum", MID_PW, None, HY, L0, "the corridors under the arena floor, to the middle of their outer wall")
L_, at_ = zip(*(strip(k, MID_E, s1, L0) for k in V))
parts["stair passage"] = {"type": "interior", "plan": {"rect": [FLIGHT, L_[0]]}, "height": r4(soff(s1) - L0), "at": list(at_),
                          "_about": "the stair up under the first maenianum, from ring E's middle to where its soffit stops over the open mouth (the treads among the rows are the cavea's)"}
L_, at_ = zip(*(strip(k, MID_E, MID_PW, 0) for k in EMIN))
parts["minor entrance"] = {"type": "interior", "plan": {"rect": [EW, L_[0]]}, "height": EH, "at": list(at_),
                           "_about": "the passages of the short axis, under the seating and the podium from ring E to the podium gate"}
parts["major entrance"] = {"type": "interior", "plan": {"points": [[r4(x), r4(z)] for x, z in
                               [at_angle(k, MID_E, f) for k, f in ((79, -.5), (0, -.5), (0, .5), (1, .5))] +
                               [at_angle(k, S_PW, f) for k, f in ((1, .5), (0, .5), (0, -.5), (79, -.5))]]},
                           "height": EH, "at": [[0, 0, 0, 0], [0, 0, 0, r4(math.pi)]],
                           "_about": "the long axis's passages, three bays wide under the seating from ring E out onto the sand"}

doc = {"name": "Colosseum",
       "_about": "THE FLAVIAN AMPHITHEATRE at its real size on its four-centred oval (188 x 156m, the arena 86 x 54, 80 bays): the four-storey facade, three ambulatories, the three maeniana each ending on a floor, the level vomitoria out onto their walkways, the stairs along ambulatory I, the main entrances on the axes, the podium, the arena floor and the hypogeum under it. tools/archgen/colosseum.py",
       "params": {"detail": 4}, "railing": {"type": "stone"},
       "site": {"dig": [[r4(-AREND - 0.1), r4(-(RO - S_AR + K - D_) - 0.1), r4(AREND + 0.1), r4(RO - S_AR + K - D_ + 0.1)]],
                "_dig": "the ground opened under the whole arena (its box: the corners fall under the cavea's paving): the hypogeum is under it, and its stairs come up through the boards"},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/colosseum.json"), "w").write(json.dumps(doc, indent=1) + "\n")
print(len(build), "parts; oval c=%.3f d=%.3f K=%.3f RO=%.3f, facade bays %.2f / %.2f" % (C_, D_, K, RO, bw(0, 0), bw(20, 0)),
      "| rows: run %.3f, rises %.3f %.3f %.3f | arena %.1f x %.1f" % (RUN, R1, R2, R3, 2 * AREND, 2 * (RO - S_AR + K - D_)))
