# ALEXANDER NEVSKY CATHEDRAL, Sofia (A. N. Pomerantsev, 1882 / 1904-12), neo-Byzantine, at its real size: OSM way
# 155447771 (73.5 x 52.2 m; the plan turned 10 degrees to its own axis), en/bg Wikipedia, cathedral.bg and photos.
# The cross-in-square: the 17 m square under the gilded dome on four piers, great arches and pendentives; the drum of
# twenty windows between colonnettes under an arched cornice, the dome 45 m up. North and south the transept arms end
# in SEMIDOMES on half rings (an arcade, the gallery, a row of windows), east the APSE under its semidome behind the
# bema's barrel vault, west the nave's barrel vault to the bell tower: the green cascade round the gold. Five aisles:
# the inner ones with the galleries (west), reached by a dog-leg stair in each; the outer ones single storey; the east
# corners round. The narthex across the west front with its two corner chapels under small domes; the frontispiece
# with the great arched gable over the three-arched porch; the BELL TOWER (53 m) on it -- the shaft with its triple
# window and the icon of St Alexander, the belfry of three arches a side, the gilded dome and cross. Inside: the
# central, Russian (north) and Bulgarian (south) iconostases, the solea, the thrones under their canopies, the altar's
# baldachin, the great chandelier under the dome and smaller ones in the arms; the walls painted, the vaults mosaic.
#   x runs across the church (south +x), z along it (west +z: the entrance front; the altar east, -z), y up from the
#   floor on the granite plinth (`base`, 1.4 m). Origin under the dome's middle.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n); return d
Q = math.pi / 2
def r4(v): return round(v, 4)
ARCH = {"profile": "semicircular"}

def iwall(name, a, b, t, ops, H, y0=0.0, about=None, glass=False, **kw):
    """a wall from a to b (x, z), its middle on that line, t thick, H high, standing at y0: its openings
    (distance from a, width, springing, sill[, arched]) -- springing and sill over the wall's foot"""
    L = math.dist(a, b); dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    # the openings in tiers, storey over storey: a cut wherever every opening under it is closed (its crown) before
    # every one over it begins (its sill) -- each tier's openings measured from its own foot
    ops = sorted([tuple(o) for o in ops], key=lambda o: o[3])
    crown = lambda o: o[2] + (o[1] / 2 if (o[4] if len(o) > 4 else True) else 0)
    groups = []
    for o in ops:
        if groups and not (max(crown(q) for q in groups[-1]) < o[3] - 0.05 and o[3] > 0.5): groups[-1].append(o)
        else: groups.append([o])
    tiers, foot = [], 0.0
    for gi, g in enumerate(groups):
        top = H if gi == len(groups) - 1 else r4((max(crown(q) for q in g) + min(q[3] for q in groups[gi + 1])) / 2)
        op = []
        for o in g:
            dd, w, sp, sl = o[:4]; hd = o[4] if len(o) > 4 else True
            op.append({"at": r4(dd - L / 2), "width": w, "sill": r4(sl - foot), "springing": r4(sp - foot), "head": ARCH if hd else {"profile": "flat"}, "glass": glass})
        tiers.append({"h": r4(top - foot), "openings": op} if gi < len(groups) - 1 else {"openings": op})
        foot = top
    if not tiers: tiers = [{"openings": []}]
    mx, mz = (a[0] + b[0]) / 2 - t / 2 * dz, (a[1] + b[1]) / 2 + t / 2 * dx
    d = {"type": "wall", "width": r4(L), "height": r4(H), "thickness": t, "tiers": tiers,
         "at": [[r4(mx), r4(y0), r4(mz), r4(math.atan2(-dz, dx))]], **kw}
    if about: d["_about"] = about
    return add(name, d)

def mirror(name, a, b, t, ops, H, **kw):
    """the same wall on the south (+x) side and, mirrored, the north (its openings measured from a either side)"""
    m = iwall(name, a, b, t, ops, H, **kw)
    # (the mirrored wall runs from -a to -b: a wall along z keeps its turn, one along x is turned half round -- either
    #  way an opening `d` from a lands mirrored, so one opening list serves both copies)
    a2, b2 = (-a[0], a[1]), (-b[0], b[1])
    L = math.dist(a2, b2); dx, dz = (b2[0] - a2[0]) / L, (b2[1] - a2[1]) / L
    mx, mz = (a2[0] + b2[0]) / 2 - t / 2 * dz, (a2[1] + b2[1]) / 2 + t / 2 * dx
    m["at"].append([r4(mx), m["at"][0][1], r4(mz), r4(math.atan2(-dz, dx))])
    return m

def box(name, x0, x1, z0, z1, y, h, **kw):
    return add(name, {"type": "box", "width": r4(x1 - x0), "length": r4(z1 - z0), "height": r4(h),
                      "at": [[r4((x0 + x1) / 2), r4(y), r4((z0 + z1) / 2), 0]], **kw})

def boxes(name, rects, y, h, **kw):
    """several boxes as one part: rects (x0, x1, z0, z1) of the same size are one part each -- so a list of parts"""
    out = []
    for k, (x0, x1, z0, z1) in enumerate(rects):
        out.append(box(f"{name} {k + 1}" if len(rects) > 1 else name, x0, x1, z0, z1, y, h, **kw))
    return out

def arc_pts(cx, cz, r, a0, a1, n):
    """points round (cx, cz), angles in degrees from +x toward +z"""
    return [[r4(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n))), r4(cz + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)))] for k in range(n + 1)]

def half_disc(r, n=12):
    return [[r4(r * math.cos(math.pi * k / n)), r4(r * math.sin(math.pi * k / n))] for k in range(n + 1)]

def annulus(ri, ro, n=16, spr=0.0):
    out = [[r4(ro * math.cos(math.pi * k / n)), r4(spr + ro * math.sin(math.pi * k / n))] for k in range(n + 1)]
    inn = [[r4(ri * math.cos(math.pi * k / n)), r4(spr + ri * math.sin(math.pi * k / n))] for k in range(n, -1, -1)]
    return out + inn

def hoods(name, places, r, depth, about=None, kind=None):
    """ZAKOMARY: the half-round hoods of the arched cornices -- a half disc r, `depth` deep, at each place
    (x, y, z, yaw: y its springing, the hood running along the placement's +z)"""
    d = {"type": "sweep", "profile": half_disc(r), "path": [[0, 0, 0], [0, 0, depth]], "at": [[r4(v) for v in p] for p in places]}
    if kind: d["kind"] = kind
    if about: d["_about"] = about
    return add(name, d)

crosses = []                                      # (x, top of the dome, z, size): a ball and a cross on every dome
def finials():
    """the balls and the Orthodox crosses on the domes (the central dome's carries no lantern: only these)"""
    ball, post, arm, arm2 = [], [], [], []
    for x, y, z, k in crosses:
        ball.append([r4(x), r4(y - 0.05 * k), r4(z), 0]); post.append([r4(x), r4(y + 0.55 * k), r4(z), 0])
        arm.append([r4(x), r4(y + 1.9 * k), r4(z), 0]); arm2.append([r4(x), r4(y + 2.45 * k), r4(z), 0])
    sec = lambda k: [{"s": 0, "a": 0.08, "b": 0.08}, {"s": 0.2, "a": 0.42, "b": 0.42}, {"s": 0.6, "a": 0.6, "b": 0.6}, {"s": 1.0, "a": 0.42, "b": 0.42}, {"s": 1.2, "a": 0.08, "b": 0.08}]
    # one part each, every dome's at its own size: the sizes differ, so a part a size
    for i, (x, y, z, k) in enumerate(crosses):
        add(f"finial ball {i + 1}", {"type": "loft", "axis": "y", "sides": 12, "smooth": 2, "at": [ball[i]],
                                     "sections": [{"s": r4(q["s"] * k), "a": r4(q["a"] * k), "b": r4(q["b"] * k)} for q in sec(k)]})
        add(f"finial cross {i + 1}", {"type": "box", "width": r4(0.16 * k), "length": r4(0.16 * k), "height": r4(2.6 * k), "at": [post[i]]})
        add(f"finial cross arm {i + 1}", {"type": "box", "width": r4(1.3 * k), "length": r4(0.14 * k), "height": r4(0.16 * k), "at": [arm[i]]})
        add(f"finial cross bar {i + 1}", {"type": "box", "width": r4(0.6 * k), "length": r4(0.14 * k), "height": r4(0.12 * k), "at": [arm2[i]]})
    parts["finial ball 1"]["_about"] = "the gilded balls and crosses on the domes"

def vault(name, cx, cz, length, ri, ro, spr, yaw=0.0, about=None):
    """a barrel vault with its roof: the shell between two half circles (ri inside, ro out), springing at spr,
    running `length` along the placement's +z -- `kind: vault`, so its underside and its flanks turned to its axis are
    the inside (finish.js), its back the roof"""
    d = {"type": "sweep", "kind": "vault", "profile": annulus(ri, ro, 20, spr), "path": [[0, 0, 0], [0, 0, r4(length)]],
         "at": [[r4(cx), 0, r4(cz), r4(yaw)]]}
    if about: d["_about"] = about
    return add(name, d)

# ======================================================================================================== numbers
S, PIER = 17.0, 3.0            # the square under the dome, the piers
R = S / 2                      # 8.5
XA = R + PIER                  # 11.5: the piers' outer faces, the half rings' centres
PC = R + PIER / 2              # 10: the pier lines' middle
GAL, SLAB = 9.5, 0.5           # the galleries' floor (its top), slabs
LOW = 9.6                      # the single-storey parts' roofs (outer aisles, east chapels, narthex)
MID = 14.5                     # the inner aisles' roofs over the galleries
ARM = 15.0                     # the transept arms' roofs
SPR = 18.0                     # the great arches, the vaults and the semidomes spring here
RING = SPR + R                 # 29: the pendentives' crown
DECK = 30.8                    # the drum's foot
XC = 17.5                      # the clerestory walls between the inner and outer aisles (middle)
XF = 24.3                      # the outer flanks' middle (outer face 24.8)
XE = 26.25                     # the transept arms' end walls (middle; 1.5 thick, outer face 27)
ZA = 12.0                      # the arms' side walls (middle; z 11.5..12.5)
ZW = 26.5                      # the nave's west wall, the narthex's east wall (middle)
ZN = 33.0                      # the narthex's west wall (middle)
ZT = 35.8                      # the frontispiece's west face
ZB = -20.6                     # the apse's centre (the bema runs from the piers to it)
WT = 1.0                       # outer walls
BASE = 1.4                     # the granite plinth everything stands on (`base`): the finish's heights are over the ground
FX = 11.8                      # the frontispiece's sides (outer face)

# ======================================================================================================== the crossing
add("piers", {"type": "box", "width": PIER, "length": PIER, "height": SPR,
              "at": [[sx * PC, 0, sz * PC, 0] for sx in (-1, 1) for sz in (-1, 1)],
              "_about": "the four great piers at the corners of the 17 m square, painted with saints"})
add("pier heads", {"type": "box", "width": PIER, "length": PIER, "height": RING - SPR,
                   "at": [[sx * PC, SPR, sz * PC, 0] for sx in (-1, 1) for sz in (-1, 1)],
                   "_about": "the piers carried up between the arches' haunches to the deck"})
add("great arches", {"type": "barrel", "width": S, "length": PIER, "springing": SPR, "top": DECK, "head": ARCH,
                     "at": [[0, 0, -R, 0], [0, 0, R + PIER, 0], [-R, 0, 0, Q], [R + PIER, 0, 0, Q]],
                     "_about": "the four great arches from pier to pier"})
add("pendentives", {"type": "pendentives", "span": S, "springing": SPR, "sides": 20, "at": [[0, 0, 0, 0]],
                    "_about": "the pendentives turning the square into the drum's circle"})
add("drum deck", {"type": "prism", "plan": {"rect": [2 * XA, 2 * XA], "well": {"radius": R, "sides": 20}}, "height": DECK - RING,
                  "at": [[0, RING, 0, 0]], "_about": "the square deck over the arches and pendentives the drum stands on, its roof copper"})
add("crossing gables", {"type": "sweep", "kind": "roof", "profile": half_disc(7.4, 16), "path": [[0, 0, 0], [0, 0, 2.3]],
                        "at": [[0, RING + 0.6, XA, math.pi], [0, RING + 0.6, -XA, 0], [XA, RING + 0.6, 0, -Q], [-XA, RING + 0.6, 0, Q]],
                        "_about": "the great arches' half-round gables (zakomary) on the four sides of the deck, their short barrel roofs running in to the drum"})
add("crossing gable rims", {"type": "sweep", "kind": "roof", "profile": annulus(7.4, 7.9, 16), "path": [[0, 0, 0], [0, 0, 0.45]],
                            "at": [[0, RING + 0.6, XA + 0.1, math.pi], [0, RING + 0.6, -XA - 0.1, 0], [XA + 0.1, RING + 0.6, 0, -Q], [-XA - 0.1, RING + 0.6, 0, Q]]})
DH, DT, DR = 6.4, 1.2, R + 1.2
add("dome", {"type": "component", "use": "components/drum-dome",
             "params": {"R": R, "dt": DT, "H": DH, "n": 20, "every": 1, "winW": 1.5, "winSill": 0.9, "winH": 4.5,
                        "profile": "segmental", "rise": 6.3, "domeR": DR, "domeT": 0.6, "ribsN": 20, "ribW": 0.28,
                        "colN": 20, "colR": 0.26, "colH": 5.6, "pw": 0.32,
                        "lanternR": 1.1, "lanternTop": -0.2},
             "build": ["drum", "peristyle", "dome", "ribs", "interior"],
             "at": [[0, DECK, 0, 0]],
             "_about": "the drum of twenty arched windows between colonnettes, the gilded dome over it (its top 45 m over the square), the ball and the cross (`drum-dome`)"})
crosses.append((0, DECK + DH + 6.3 - 0.1, 0, 0.9))
add("drum hoods", {"type": "sweep", "profile": half_disc(1.6), "path": [[0, 0, 0], [0, 0, 1.1]],
                   "at": [[r4((R + DT - 0.4) * math.sin(math.radians((k + 0.5) * 18))), DECK + DH - 0.2,
                           r4((R + DT - 0.4) * math.cos(math.radians((k + 0.5) * 18))), r4(math.radians((k + 0.5) * 18))] for k in range(20)],
                   "_about": "the drum's arched cornice: a half-round hood over every window, scalloping the dome's foot"})

# ======================================================================================================== the transept arms
HALF = list(range(9))                               # the bays of a ring of 18 on its +x side (turned 0.5: from +z round to -z)
HALF10 = list(range(5))
ARMS = [[XA, 0, 0, 0], [-XA, 0, 0, math.pi]]
RO = R + 1.0
add("arm arcade", {"type": "ring", "count": 10, "rOuter": RO, "rInner": R, "height": GAL - SLAB, "y": 0, "turn": 0.5, "at": HALF10,
                   "opening": {"width": 3.0, "sill": 0, "springing": 6.6, "head": ARCH}, "place": ARMS, "glass": False,
                   "_about": "each arm's half ring at the ground: five arches into the arm's aisle behind"})
add("arm gallery arcade", {"type": "ring", "count": 10, "rOuter": RO, "rInner": R, "height": ARM - GAL + SLAB, "y": GAL - SLAB, "turn": 0.5, "at": HALF10,
                           "opening": {"width": 2.4, "sill": 1.4, "springing": 4.4, "head": ARCH}, "place": ARMS, "glass": False,
                           "_about": "the gallery storey over it, its arches' sills the gallery's parapet"})
add("arm windows", {"type": "ring", "count": 18, "rOuter": RO, "rInner": R, "height": SPR - ARM, "y": ARM, "turn": 0.5, "at": HALF,
                    "opening": {"width": 1.3, "sill": 0.6, "springing": 2.2, "head": ARCH}, "place": ARMS,
                    "_about": "the half ring of nine windows each semidome stands on, over the arm's roofs"})
add("arm semidomes", {"type": "dome", "sweep": 0.5, "sides": 18, "radius": RO, "thickness": 1.0, "head": ARCH,
                      "at": [[XA, SPR, 0, Q], [-XA, SPR, 0, -Q]],
                      "_about": "the green semidomes north and south, their crowns under the great arches'"})
add("arm semidome hoods", {"type": "sweep", "profile": half_disc(1.15), "path": [[0, 0, 0], [0, 0, 0.8]],
                           "_about": "the arched cornice round each semidome's foot, a hood over every window (the north ones measured from +z toward -x)"})
parts["arm semidome hoods"]["at"] = [[r4(sx * (XA + (RO - 0.5) * math.sin(math.radians((k + 0.5) * 20)))), SPR - 0.15,
                                      r4((RO - 0.5) * math.cos(math.radians((k + 0.5) * 20))), r4(sx * math.radians((k + 0.5) * 20))]
                                     for sx in (1, -1) for k in range(9)]
# the arms' side walls and end walls
for nm, zs in (("arm west walls", 1), ("arm east walls", -1)):
    ops_w = [(3.0, 3.6, 6.6, 0), (9.5, 3.6, 6.0, 0)]                     # into the inner and the outer aisle
    if zs > 0: ops_w += [(3.0, 2.0, GAL + 2.6, GAL), (9.5, 1.6, 13.4, 11.0)]   # the door to the west gallery; a window over the outer aisle
    else: ops_w += [(3.0, 1.8, 13.4, 10.6), (9.5, 1.6, 13.4, 11.0)]
    mirror(nm, (XA, zs * ZA), (XE - 0.75, zs * ZA), WT, ops_w, ARM,
           about="the arms' side walls: arches at the ground into the aisles" + (", the door from the arm's gallery to the west gallery" if zs > 0 else "") + ", windows over the lower roofs")
mirror("arm end walls", (XE, -12.5), (XE, 12.5), 1.5,
       [(12.5, 4.4, 6.6, 0), (6.5, 1.8, 5.0, 0), (18.5, 1.8, 5.0, 0), (12.5, 2.0, 13.4, 10.6), (9.4, 1.5, 12.9, 10.6), (15.6, 1.5, 12.9, 10.6)], ARM,
       about="the arms' end walls: the great portal and two side doors, the triple window over them")
add("arm gables", {"type": "sweep", "profile": half_disc(6.5, 16), "path": [[0, 0, 0], [0, 0, 6.5]],
                   "at": [[XE + 0.75, ARM, 0, -Q], [-XE - 0.75, ARM, 0, Q]], "kind": "roof",
                   "_about": "the great half-round gable (zakomara) of each arm's end and the short barrel roof behind it"})
add("arm gable rims", {"type": "sweep", "profile": annulus(6.5, 7.0, 16), "path": [[0, 0, 0], [0, 0, 0.45]], "kind": "roof",
                       "at": [[XE + 0.95, ARM, 0, -Q], [-XE - 0.95, ARM, 0, Q]],
                       "_about": "its copper-covered rim"})

# ======================================================================================================== the west arm and the bema
PIERWALL = [(3.6, 3.6, 7.0, 0), (9.6, 3.6, 7.0, 0),                       # the arcade to the inner aisle
            (4.5, 3.0, 13.1, GAL + 1.2), (12.8, 1.8, GAL + 2.4, GAL),      # the gallery's arch (parapet) and the choir door
            (4.5, 1.8, 16.6, 15.0), (10.5, 1.8, 16.6, 15.0)]              # the clerestory over the gallery's roof
mirror("west pier walls", (PC, XA), (PC, ZW - 0.5), PIER, PIERWALL, SPR,
       about="the walls on the pier lines along the west arm: the arcade to the inner aisle, the gallery's arches over it, the clerestory")
mirror("bema walls", (PC, -XA), (PC, ZB), PIER, [(4.5, 3.6, 7.0, 0), (4.5, 2.2, 15.6, 11.0)], SPR,
       about="the bema's walls, an arch to the side chapel and a window over its roof")
vault("west vault", 0, XA, ZW - 0.5 - XA, R, R + 1.3, SPR, about="the nave's barrel vault to the west, its back the green roof")
vault("bema vault", 0, ZB, -ZB - XA, R, R + 1.3, SPR, about="the bema's barrel vault between the crossing and the apse")
add("west tympanum", {"type": "sweep", "profile": half_disc(R + 1.3, 20), "path": [[0, 0, 0], [0, 0, 1.0]], "at": [[0, SPR, ZW - 0.5, 0]],
                       "_about": "the tympanum closing the vault's west end"})
iwall("west wall", (-XA, ZW), (XA, ZW), 1.0, [(XA, 4.0, 6.0, 0), (XA - 5.0, 1.6, 4.0, 0), (XA + 5.0, 1.6, 4.0, 0)], SPR,
      about="the nave's west wall, the tympanum under the vault's end: the great door from the vestibule, two doors from the narthex")

# ======================================================================================================== the apse
APSE = [[0, 0, ZB, Q]]
add("apse lower", {"type": "ring", "count": 18, "rOuter": R + 2.3, "rInner": R, "height": LOW + 2.4, "y": 0, "turn": 0.5, "at": HALF,
                   "opening": {"width": 1.4, "sill": 4.0, "springing": 8.0, "head": ARCH}, "place": APSE,
                   "_about": "the apse's lower storey: the thick half ring with tall windows"})
add("apse upper", {"type": "ring", "count": 18, "rOuter": RO, "rInner": R, "height": SPR - LOW - 2.4, "y": LOW + 2.4, "turn": 0.5, "at": HALF,
                   "opening": {"width": 1.3, "sill": 1.0, "springing": 4.4, "head": ARCH}, "place": APSE,
                   "_about": "the upper storey of nine windows"})
add("apse semidome", {"type": "dome", "sweep": 0.5, "sides": 18, "radius": RO, "thickness": 1.0, "head": ARCH, "at": [[0, SPR, ZB, math.pi]],
                      "_about": "the semidome over the apse"})
add("apse hoods", {"type": "sweep", "profile": half_disc(1.15), "path": [[0, 0, 0], [0, 0, 0.8]],
                   "at": [[r4((RO - 0.5) * math.sin(math.radians(90 + (k + 0.5) * 20))), SPR - 0.15, r4(ZB + (RO - 0.5) * math.cos(math.radians(90 + (k + 0.5) * 20))),
                           r4(math.radians(90 + (k + 0.5) * 20))] for k in range(9)]})
add("apse cornice", {"type": "ring", "count": 18, "rOuter": R + 2.6, "rInner": RO, "height": 0.6, "y": LOW + 2.4, "turn": 0.5, "at": HALF, "place": APSE, "solid": True,
                     "_about": "the lower storey's cornice, its roof"})

# ======================================================================================================== aisles, chapels, outer walls
WIN3 = lambda *ds: [(d, 1.6, 6.2, 2.6) for d in ds]
mirror("clerestory walls", (XC, 12.5), (XC, ZW - 0.5), WT,
       [(1.8, 3.0, 6.2, 0), (3.5, 2.0, 13.4, 11.0), (10.0, 2.0, 13.4, 11.0)], MID,
       about="the walls between the inner and outer aisles: arches below, the gallery's windows over the outer aisle's roof")
mirror("west flanks", (XF, 12.5), (XF, ZN), WT, WIN3(3.5, 10.0, 17.0) + [(13.5, 2.0, 3.6, 0)], LOW,
       about="the outer walls along the west aisles and the narthex: tall windows and a side door")
mirror("east flanks", (XF, -12.5), (XF, -14.1), WT, [], LOW)
ER, EC = 9.8, (14.5, -14.1)
add("east rounds", {"type": "ring", "count": 24, "rOuter": ER + 0.5, "rInner": ER - 0.5, "height": LOW, "y": 0, "turn": 0.5, "at": [6, 7, 8, 9, 10, 11],
                    "opening": {"width": 1.4, "sill": 2.6, "springing": 6.2, "head": ARCH},
                    "place": [[EC[0], 0, EC[1], 0], [-EC[0], 0, EC[1], Q]],
                    "_about": "the rounded east corners of the outer aisles (OSM: quarter circles of 10 m), windows round them"})
mirror("chapel east walls", (11.0, -23.9), (EC[0] + 0.3, -23.9), WT, [(1.8, 1.4, 6.2, 2.6)], LOW)
mirror("chapel inner walls", (11.0, ZB), (11.0, -23.9), WT, [], LOW)
# the roofs and floors
EAST_PLAN = [[11.0, -12.5], [XF + 0.5, -12.5], [XF + 0.5, EC[1]]] + arc_pts(EC[0], EC[1], ER + 0.5, 0, -90, 8)[1:] + [[11.0, -23.9 - 0.5]]
for sx, nm in ((1, "south"), (-1, "north")):
    add(f"east chapels roof {nm}", {"type": "prism", "plan": {"points": [[r4(sx * x), z] for x, z in (EAST_PLAN if sx > 0 else EAST_PLAN[::-1])]},
                                    "height": 0.6, "at": [[0, LOW - 0.6, 0, 0]], "flatRoof": True,
                                    "_about": "the flat roof over the east chapels and the rounded corners" if sx > 0 else None})
    if sx < 0: parts[f"east chapels roof {nm}"].pop("_about")
add("east round domes", {"type": "dome", "sweep": 0.25, "sides": 24, "radius": ER - 1.0, "thickness": 0.4, "head": {"profile": "segmental", "rise": 3.2},
                         "at": [[EC[0], LOW, EC[1], 2.3562], [-EC[0], LOW, EC[1], -2.3562]],
                         "_about": "the low green quarter-domes over the rounded corners"})
add("outer aisle roofs", {"type": "roof", "form": "shed", "width": XF + 0.9 - XC, "length": ZN + 0.5 - 12.5, "pitch": 12, "overhang": 0.3,
                          "at": [[r4((XF + XC) / 2 + 0.45), LOW, r4((ZN + 12.5) / 2), 0], [r4(-(XF + XC) / 2 - 0.45), LOW, r4((ZN + 12.5) / 2), math.pi]],
                          "_about": "the outer aisles' and the narthex ends' copper lean-to roofs"})
boxes("outer aisle ceilings", [(XC, XF, 12.5, ZN), (-XF, -XC, 12.5, ZN)], LOW - 0.6, 0.6)
boxes("narthex roofs", [(FX, XC, ZW, ZN), (-XC, -FX, ZW, ZN)], LOW - 0.6, 0.6, flatRoof=True)
boxes("inner aisle roofs", [(XA, XC + 0.5, 12.5, ZW - 0.5), (-XC - 0.5, -XA, 12.5, ZW - 0.5)], MID - SLAB, SLAB, flatRoof=True)
# the arms' roofs round their half rings, and the galleries under them
def u_plan(sx, rr):
    pts = [[XA, ZA + 0.5]] + [[r4(XA + rr * math.sin(math.radians(a))), r4(rr * math.cos(math.radians(a)))] for a in range(0, 181, 15)] \
          + [[XA, -ZA - 0.5], [XE, -ZA - 0.5], [XE, ZA + 0.5]]
    return [[r4(sx * x), z] for x, z in (pts if sx > 0 else pts[::-1])]
for sx, nm in ((1, "south"), (-1, "north")):
    add(f"arm roof {nm}", {"type": "prism", "plan": {"points": u_plan(sx, RO)}, "height": SLAB, "at": [[0, ARM - SLAB, 0, 0]], "flatRoof": True})
    add(f"arm gallery {nm}", {"type": "prism", "plan": {"points": u_plan(sx, RO)}, "height": SLAB, "at": [[0, GAL - SLAB, 0, 0]]})
parts["arm gallery south"]["_about"] = "the arms' galleries round their half rings, through the arm's west wall to the west galleries"

# the west galleries over the inner aisles, a hatch where each stair comes up; the choir across the nave's west end
W, GAP, RUN = 2.0, 0.4, 0.28
N1 = 28; RISE = GAL / (2 * N1)
Z0 = 24.6                                         # where the first flight starts, climbing east
FL1 = N1 * RUN
X1 = XC - 0.5 - 0.1 - W / 2                       # the first flight's middle (along the clerestory wall)
X2 = X1 - W - GAP                                 # the second's, beside the pier wall
Zt = Z0 - FL1                                     # the landing's near edge
for sx, nm in ((1, "south"), (-1, "north")):
    s = sx
    add(f"{nm} gallery stair", {"type": "staircase", "flight": N1, "width": W, "run": RUN, "rise": r4(RISE), "soffit": 0.3,
                                "landing": {"depth": 1.6, "width": r4(2 * W + GAP), "shift": r4(-(W / 2 + GAP / 2) * s),
                                            "then": [{"from": "back", "at": r4(-(W / 2 + GAP / 2) * s), "flight": N1, "width": W, "landing": {"depth": 1.0, "width": W}}]},
                                "at": [[r4(s * X1), 0, Z0, Q]],
                                "_about": "the stair to the gallery in the west end of the inner aisle: a flight east, a landing, a flight back beside it"})
    xh0, xh1 = X2 - W / 2 - 0.05, X2 + W / 2 + 0.05             # the hatch over the second flight
    rects = [(XA, xh0, 12.5, ZW - 0.5), (xh1, XC - 0.5, 12.5, ZW - 0.5), (xh0, xh1, 12.5, Zt - 1.6), (xh0, xh1, Z0, ZW - 0.5)]
    for k, (a, b, c, d) in enumerate(rects):
        x0, x1 = (a, b) if s > 0 else (-b, -a)
        box(f"west gallery {nm} {k + 1}", x0, x1, c, d, GAL - SLAB, SLAB)
parts["west gallery south 1"]["_about"] = "the galleries over the west inner aisles, open to the hatch the stair comes up through"
box("choir gallery", -PC + PIER / 2, PC - PIER / 2, ZW - 0.5 - 3.5, ZW - 0.5, GAL - SLAB, SLAB,
    _about="the choir gallery across the nave's west end, between the two galleries")
add("choir balustrade", {"type": "box", "width": S, "length": 0.3, "height": 1.0, "at": [[0, GAL, r4(ZW - 0.5 - 3.5 + 0.15), 0]],
                         "_about": "its parapet toward the nave"})
add("gallery columns", {"type": "column", "radius": 0.4, "height": GAL - SLAB, "sides": 12,
                        "at": [[sx * 14.5, 0, 13.9, 0] for sx in (-1, 1)],
                        "_about": "the columns under the west galleries"})

# ======================================================================================================== narthex, frontispiece, tower, porches
mirror("aisle west walls", (XA, ZW), (XC, ZW), WT, [(3.0, 2.2, 4.4, 0)], MID,
       about="the narthex's east wall: a door into each inner aisle (the wall up to the galleries' roof)")
mirror("narthex east walls", (XC, ZW), (XF + 0.5, ZW), WT, [(3.5, 2.2, 4.4, 0)], LOW, about="...and into each outer aisle")
mirror("narthex west walls", (FX, ZN), (XF + 0.5, ZN), WT, [(2.6, 2.0, 5.4, 0), (5.7, 2.0, 5.4, 0), (9.5, 1.8, 4.0, 0)], LOW,
       about="the narthex wings' west walls: the doors under the arcaded porches")
mirror("chapel walls", (18.5, ZW + 0.5), (18.5, ZN - 0.5), 0.8, [(3.0, 1.6, 3.4, 0)], LOW,
       about="the corner chapels' walls in the narthex's ends")
iwall("frontispiece", (-FX, ZT - 0.5), (FX, ZT - 0.5), 1.0, [(FX, 4.6, 7.0, 0), (FX - 3.8, 1.6, 4.6, 0), (FX + 3.8, 1.6, 4.6, 0),
                                                             (FX - 8.6, 1.3, 9.4, 6.2), (FX + 8.6, 1.3, 9.4, 6.2)], 15.5,
      about="the west front over the porch: the great door and two lesser, windows in the side bays")
mirror("frontispiece sides", (FX - 0.5, ZW + 0.5), (FX - 0.5, ZT), WT, [(3.0, 2.0, 4.0, 0), (7.0, 1.4, 6.0, 2.6)], 15.5)
add("frontispiece gable", {"type": "sweep", "profile": half_disc(6.6, 16), "path": [[0, 0, 0], [0, 0, 1.4]], "at": [[0, 15.5, ZT - 1.4, 0]],
                           "_about": "the great half-round gable of the west front"})
add("frontispiece gable rim", {"type": "sweep", "profile": annulus(6.6, 7.1, 16), "path": [[0, 0, 0], [0, 0, 0.45]], "kind": "roof", "at": [[0, 15.5, ZT - 0.1, 0]]})
iwall("frontispiece window", (-3.0, ZT + 0.05), (3.0, ZT + 0.05), 0.2, [(1.6, 1.2, 4.0, 0), (3.0, 1.4, 4.6, 0), (4.4, 1.2, 4.0, 0)], 5.4, y0=15.6, glass=True,
      about="the triple window in the gable")
boxes("frontispiece floor", [(-FX, FX, ZW + 0.5, ZT)], 15.0, SLAB, flatRoof=True)
# the tower: shaft, plinth stage, belfry, dome
TX, TZ0, TZ1 = 5.2, ZW - 0.5, ZT - 0.3            # the shaft's outer faces
TB, TT = 15.5, 38.0
TW = 1.2
mirror("tower flanks", (TX - TW / 2, TZ0), (TX - TW / 2, TZ1), TW, [(4.6, 1.2, 15.0, 11.0), (TZ1 - TZ0 - 3.0, 1.2, 15.0, 11.0)], TT - TB, y0=TB,
       about="the bell tower's shaft, north and south faces")
iwall("tower west", (-TX, TZ1 - TW / 2), (TX, TZ1 - TW / 2), TW, [(TX - 2.4, 1.3, 14.4, 10.0), (TX, 1.6, 15.2, 10.0), (TX + 2.4, 1.3, 14.4, 10.0)], TT - TB, y0=TB,
      about="its west face: the triple window, the icon of St Alexander Nevsky over it")
iwall("tower east", (TX, TZ0 + TW / 2), (-TX, TZ0 + TW / 2), TW, [(TX, 1.6, 15.2, 11.0)], TT - TB, y0=TB)
box("tower icon", -1.8, 1.8, TZ1, TZ1 + 0.2, TB + 17.6, 3.8, _about="the mosaic icon of St Alexander Nevsky on the tower's west face")
box("tower cornice", -TX - 0.4, TX + 0.4, TZ0 - 0.4, TZ1 + 0.4, TT, 0.7, kind="moulding", _about="the shaft's cornice")
add("tower pilasters", {"type": "box", "width": 1.0, "length": 1.0, "height": TT - TB,
                        "at": [[r4(sx * (TX - 0.35)), TB, r4(zz), 0] for sx in (-1, 1) for zz in (TZ0 + 0.35, TZ1 - 0.35)],
                        "_about": "the shaft's corner pilasters"})
box("tower band", -TX - 0.25, TX + 0.25, TZ0 - 0.25, TZ1 + 0.25, TB + 16.2, 0.45, kind="moulding", _about="the band between the triple windows and the icon")
box("belfry plinth", -TX + 0.2, TX - 0.2, TZ0 + 0.2, TZ1 - 0.2, TT + 0.7, 0.9)
BY = TT + 1.6
BW, BL = 2 * TX - 0.6, TZ1 - TZ0 - 0.6
add("belfry", {"type": "enclosure", "plan": {"rect": [r4(BW), r4(BL)]}, "thickness": 0.9, "height": 5.2,
               "tiers": [{"openings": {"pattern": "3", "width": 1.9, "gap": 0.9, "sill": 0.9, "springing": 3.6, "head": ARCH}, "glass": False}],
               "at": [[0, BY, r4((TZ0 + TZ1) / 2), 0]], "interior": False,
               "_about": "the belfry: three arches a side, its twelve bells inside"})
add("belfry hoods", {"type": "sweep", "profile": half_disc(1.3), "path": [[0, 0, 0], [0, 0, 0.7]],
                     "at": [[r4(dx), BY + 5.0, r4((TZ0 + TZ1) / 2 + BL / 2 - 0.5), 0] for dx in (-2.8, 0, 2.8)]
                          + [[r4(dx), BY + 5.0, r4((TZ0 + TZ1) / 2 - BL / 2 + 0.5), math.pi] for dx in (-2.8, 0, 2.8)]
                          + [[r4(BW / 2 - 0.5), BY + 5.0, r4((TZ0 + TZ1) / 2 + dz), Q] for dz in (-2.8, 0, 2.8)]
                          + [[r4(-BW / 2 + 0.5), BY + 5.0, r4((TZ0 + TZ1) / 2 + dz), -Q] for dz in (-2.8, 0, 2.8)],
                     "_about": "the belfry's arched cornice"})
box("belfry roof", -BW / 2 - 0.3, BW / 2 + 0.3, (TZ0 + TZ1) / 2 - BL / 2 - 0.3, (TZ0 + TZ1) / 2 + BL / 2 + 0.3, BY + 5.2, 0.5, flatRoof=True)
add("belfry dome", {"type": "component", "use": "components/drum-dome",
                    "params": {"R": 3.4, "dt": 0.6, "H": 1.8, "n": 12, "every": 1, "winW": 0.6, "winSill": 0.4, "winH": 0.8,
                               "profile": "segmental", "rise": 3.3, "domeR": 4.0, "domeT": 0.35, "ribsN": 12, "ribW": 0.16, "lanternR": 1.0, "lanternTop": -0.2},
                    "build": ["drum", "dome", "ribs"],
                    "at": [[0, BY + 5.7, r4((TZ0 + TZ1) / 2), 0]],
                    "_about": "the bell tower's gilded dome on its little drum, the cross 53 m over the square"})
crosses.append((0, BY + 5.7 + 1.8 + 3.3 - 0.05, r4((TZ0 + TZ1) / 2), 0.95))
# the small domes: the corner chapels' and the frontispiece's flanks
def small_dome(name, places, Rr, H, about):
    add(name, {"type": "component", "use": "components/drum-dome",
               "params": {"R": Rr, "dt": 0.45, "H": H, "n": 12, "every": 2, "winW": 0.6, "winSill": 0.5, "winH": 1.1,
                          "profile": "segmental", "rise": r4(Rr * 0.95), "domeR": r4(Rr + 0.6), "domeT": 0.3, "lanternR": 0.55, "lanternTop": -0.1},
               "build": ["drum", "dome"], "at": places, "_about": about})
    for x, y, z, _ in places: crosses.append((x, y + H + Rr * 0.95, z, 0.55))
small_dome("chapel domes", [[sx * 21.4, LOW, 30.0, 0] for sx in (1, -1)], 2.3, 2.8, "the green domes over the narthex's corner chapels")
small_dome("front domes", [[sx * 8.5, 15.5, 31.0, 0] for sx in (1, -1)], 1.9, 2.4, "the green domes either side of the tower over the frontispiece")
finials()
# the porches
PZ0, PZ1, PX = ZT, 40.2, 7.0
iwall("west porch front", (-PX, PZ1 - 0.4), (PX, PZ1 - 0.4), 0.8, [(PX - 4.4, 3.4, 5.6, 0), (PX, 3.6, 5.8, 0), (PX + 4.4, 3.4, 5.6, 0)], 8.2,
      about="the west porch: three arches on its columns before the great door")
mirror("west porch sides", (PX - 0.4, PZ0), (PX - 0.4, PZ1 - 0.8), 0.8, [(2.0, 2.4, 5.0, 0)], 8.2)
box("west porch roof", -PX - 0.2, PX + 0.2, PZ0, PZ1 + 0.2, 8.2, 0.6, flatRoof=True)
hoods("west porch hoods", [[dx, 8.8, PZ1 - 1.0, 0] for dx in (-4.4, 0, 4.4)], 2.1, 1.2, "the porch's three arched gables")
add("west porch columns", {"type": "column", "radius": 0.32, "height": 5.6, "sides": 12,
                           "at": [[dx, 0, PZ1 - 0.1, 0] for dx in (-6.5, -2.25, 2.25, 6.5)], "_about": "the porch's marble columns"})
mirror("wing loggias", (FX, ZN + 2.6), (18.5, ZN + 2.6), 0.6, [(1.2, 1.6, 3.6, 0), (3.35, 1.6, 3.6, 0), (5.5, 1.6, 3.6, 0)], 5.6,
       about="the arcaded porches before the narthex wings' doors: three arches each")
boxes("wing loggia roofs", [(FX, 18.5, ZN + 0.5, ZN + 2.8), (-18.5, -FX, ZN + 0.5, ZN + 2.8)], 5.6, 0.5, flatRoof=True)
hoods("wing loggia hoods", [[sx * x, 6.1, ZN + 2.0, 0] for sx in (1, -1) for x in (13.0, 15.15, 17.3)], 0.95, 0.6)

# ======================================================================================================== inside: iconostases, thrones, altar, chandeliers
SOL = 0.35
box("solea", -R, R, -XA + 0.6, -R + 2.2, 0, SOL, _about="the solea: the raised step before the central iconostasis")
iwall("central iconostasis", (-R, -R - 1.4), (R, -R - 1.4), 0.5, [(R, 2.4, 4.0, 0), (R - 4.8, 1.3, 2.9, 0), (R + 4.8, 1.3, 2.9, 0)], 6.6, y0=SOL, inside=True,
      about="the central iconostasis in the east great arch: white and yellow marble, the royal doors and the deacons' doors, two tiers of icons")
add("central iconostasis columns", {"type": "column", "radius": 0.2, "height": 4.0, "sides": 10, "inside": True,
                                    "at": [[x, SOL, r4(-R - 1.1), 0] for x in (-6.9, -3.4, -1.5, 1.5, 3.4, 6.9)],
                                    "_about": "its columns of green marble"})
box("central iconostasis cornice", -R, R, -R - 1.75, -R - 1.05, SOL + 6.6, 0.5, inside=True)
add("central iconostasis crown", {"type": "sweep", "profile": half_disc(1.6), "path": [[0, 0, 0], [0, 0, 0.5]], "at": [[0, SOL + 7.1, r4(-R - 1.65), 0]], "inside": True,
                                  "_about": "the arched crest over the royal doors"})
for sx, nm, ab in ((-1, "russian", "the Russian iconostasis before the north chapel"), (1, "bulgarian", "the Bulgarian iconostasis before the south chapel")):
    a, b = (sx * (XA + 0.0), -14.0), (sx * (XC + 4.0), -14.0)
    if sx < 0: a, b = b, a
    iwall(f"{nm} iconostasis", a, b, 0.4, [(5.0, 1.8, 3.2, 0), (1.9, 1.0, 2.4, 0), (8.1, 1.0, 2.4, 0)], 5.0, y0=0.25, inside=True, about=ab)
    box(f"{nm} solea", min(a[0], b[0]), max(a[0], b[0]), -14.2, -12.8, 0, 0.25)
    box(f"{nm} altar", sx * 14.5 - 0.9, sx * 14.5 + 0.9, -19.0, -17.8, 0.0, 1.1, inside=True)
box("altar", -1.3, 1.3, ZB - 0.7, ZB + 0.7, 0, 1.15, inside=True, _about="the main altar")
box("altar step", -4.0, 4.0, ZB - 3.0, ZB + 3.0, 0, 0.3)
add("baldachin columns", {"type": "column", "radius": 0.2, "height": 4.6, "sides": 10, "inside": True,
                          "at": [[sx * 2.0, 0.3, ZB + sz * 1.8, 0] for sx in (-1, 1) for sz in (-1, 1)]})
box("baldachin entablature", -2.4, 2.4, ZB - 2.2, ZB + 2.2, 4.9, 0.7, inside=True, _about="the baldachin (ciborium) over the altar")
add("baldachin dome", {"type": "dome", "sides": 16, "radius": 1.9, "thickness": 0.2, "head": {"profile": "onion", "rise": 2.6}, "at": [[0, 5.6, ZB, 0]], "inside": True})
# the thrones under their canopies by the east piers: the royal (south) and the patriarch's (north)
for sx, nm in ((1, "royal"), (-1, "patriarchal")):
    cx, cz = sx * 6.6, -5.6
    add(f"{nm} throne canopy columns", {"type": "column", "radius": 0.13, "height": 3.2, "sides": 8, "inside": True,
                                        "at": [[r4(cx + dx), 0.3, r4(cz + dz), 0] for dx in (-0.9, 0.9) for dz in (-0.9, 0.9)]})
    box(f"{nm} throne dais", cx - 1.3, cx + 1.3, cz - 1.3, cz + 1.3, 0, 0.3)
    box(f"{nm} throne canopy", cx - 1.15, cx + 1.15, cz - 1.15, cz + 1.15, 3.5, 0.5, inside=True)
    add(f"{nm} throne dome", {"type": "dome", "sides": 12, "radius": 1.0, "thickness": 0.12, "head": {"profile": "onion", "rise": 1.5},
                              "at": [[cx, 4.0, cz, 0]], "inside": True})
    box(f"{nm} throne", cx - 0.45, cx + 0.45, cz - 0.4, cz + 0.4, 0.3, 1.5, inside=True)
parts["royal throne canopy"]["_about"] = "the thrones by the east piers under their marble canopies with little gilded domes: the royal and the patriarch's"
# the chandeliers: the great one under the dome -- gilt hoops hung with lights -- and lesser ones
CY = 24.0                                          # its lower hoop (27 m over the square on the outside's ground)
hoops = []
for r, y in ((4.2, CY), (3.4, CY + 1.2), (2.2, CY + 2.2)):
    n = 24
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        hoops.append([r4(r * math.cos(a0)), r4(y), r4(r * math.sin(a0)), r4(r * math.cos(a1)), r4(y), r4(r * math.sin(a1))])
for k in range(6):
    a = 2 * math.pi * k / 6
    hoops.append([r4(4.2 * math.cos(a)), CY, r4(4.2 * math.sin(a)), 0, CY + 6.0, 0])
hoops.append([0, CY + 6.0, 0, 0, DECK + DH + 5.3, 0])
add("great chandelier", {"type": "bars", "lines": hoops, "w": 0.12, "h": 0.12, "kind": "moulding", "inside": True, "solid": False,
                         "_about": "the great chandelier under the dome (2.5 t, Munich): its gilt hoops on their chains"})
lights = [[r4(r * math.cos(2 * math.pi * k / n)), r4(y + 1.5), r4(r * math.sin(2 * math.pi * k / n)), 0]
          for r, y, n in ((4.2, CY, 16), (3.4, CY + 1.2, 12), (2.2, CY + 2.2, 8))]
lights += [[0, CY + 1.0, 0, 0]]
CH = [[0, SPR - 2.5, 17.5, 0], [0, SPR - 2.5, -16.0, 0], [16.5, ARM - 1.0, 0, 0], [-16.5, ARM - 1.0, 0, 0],
      [16.0, LOW - 0.7, -18.5, 0], [-16.0, LOW - 0.7, -18.5, 0], [21.0, LOW - 0.7, 20.0, 0], [-21.0, LOW - 0.7, 20.0, 0],
      [14.5, MID - 0.6, 18.5, 0], [-14.5, MID - 0.6, 18.5, 0], [0, 14.0, 30.5, 0]]
add("chandeliers", {"type": "item", "item": "items/furniture/chandelier", "at": lights + CH, "solid": False,
                    "_about": "the lights on the great chandelier's hoops; chandeliers in the arms, the bema, the aisles and the vestibule"})
add("chandelier chains", {"type": "bars", "lines": [[p[0], p[1], p[2], p[0], top, p[2]] for p, top in
                                                    ((CH[0], SPR + R - 0.5), (CH[1], SPR + R - 0.5), (CH[2], SPR + R - 0.5), (CH[3], SPR + R - 0.5))],
                          "w": 0.05, "h": 0.05, "kind": "moulding", "inside": True, "solid": False})

# ======================================================================================================== interiors
def outline():
    """the whole church inside its outer walls' middles (the narthex with it): x, z"""
    s = [[FX, ZT - 0.5], [FX, ZN], [XF, ZN], [XF, ZA + 0.5], [XE, ZA + 0.5], [XE, -ZA - 0.5], [XF, -ZA - 0.5], [XF, EC[1]]] \
        + arc_pts(EC[0], EC[1], ER, 0, -90, 8)[1:] + [[11.0, -23.9]]
    # the apse is its own
    n = [[-x, z] for x, z in s[::-1]]
    return s + n
add("church interior", {"type": "interior", "plan": {"points": [[r4(x), r4(z)] for x, z in outline()]}, "height": LOW - 0.6, "at": [[0, 0, 0, 0]],
                        "_about": "the church's space within its outer walls and the narthex, up to the single-storey roofs"})
INNER = [[XC, ZW], [XC, ZA], [XE, ZA], [XE, -ZA], [PC, -ZA], [PC, ZB], [-PC, ZB], [-PC, -ZA], [-XE, -ZA], [-XE, ZA], [-XC, ZA], [-XC, ZW]]
add("inner interior", {"type": "interior", "plan": {"points": INNER}, "height": MID - SLAB, "at": [[0, 0, 0, 0]],
                       "_about": "the nave, the arms and the inner aisles with their galleries, up to the inner aisles' roofs"})
add("arm interior", {"type": "interior", "plan": {"points": [[XA, ZA], [XE, ZA], [XE, -ZA], [XA, -ZA], [-XA, -ZA], [-XE, -ZA], [-XE, ZA], [-XA, ZA]]},
                     "height": ARM - SLAB, "at": [[0, 0, 0, 0]], "_about": "the arms up to their roofs"})
add("nave interior", {"type": "interior", "plan": {"points": [[PC, ZW], [PC, ZB], [-PC, ZB], [-PC, ZW]]}, "height": SPR, "at": [[0, 0, 0, 0]],
                      "_about": "the nave from the west wall to the apse, up to the vaults' springing"})
add("crossing interior", {"type": "interior", "plan": {"points": [[-R, -R], [R, -R], [R, R], [-R, R]]}, "height": DECK, "at": [[0, 0, 0, 0]],
                          "_about": "the square under the dome, up into the pendentives and the deck"})
add("arches interior", {"type": "interior", "plan": {"points": [[-XA, -XA], [XA, -XA], [XA, XA], [-XA, XA]]}, "height": RING, "at": [[0, 0, 0, 0]],
                        "_about": "...and out to the piers' backs up to the arches' crowns, so the great arches' soffits are the inside's"})
add("half ring interiors", {"type": "interior", "plan": {"sides": 36, "radius": R + 0.5}, "arc": [-90, 90], "height": SPR,
                            "at": [[XA, 0, 0, Q], [-XA, 0, 0, -Q], [0, 0, ZB, math.pi]],
                            "_about": "the half rings of the arms and the apse up to their semidomes"})
add("vestibule interior", {"type": "interior", "plan": {"points": [[-FX + 1, ZW + 0.5], [FX - 1, ZW + 0.5], [FX - 1, ZT - 0.5], [-FX + 1, ZT - 0.5]]},
                           "height": 15.0, "at": [[0, 0, 0, 0]], "_about": "the vestibule under the tower"})
add("tower interior", {"type": "interior", "plan": {"points": [[-TX + TW / 2, TZ0 + TW / 2], [TX - TW / 2, TZ0 + TW / 2], [TX - TW / 2, TZ1 - TW / 2], [-TX + TW / 2, TZ1 - TW / 2]]},
                       "height": TT - TB, "at": [[0, TB, 0, 0]], "_about": "the tower's shaft"})

# ======================================================================================================== cornices
def band(pts, closed=False):
    return [[r4(a[0]), 0, r4(a[1]), r4(b[0]), 0, r4(b[1])] for a, b in zip(pts, pts[1:] + (pts[:1] if closed else []))]
def at_y(lines, y): return [[l[0], r4(y), l[2], l[3], r4(y), l[5]] for l in lines]
low = band(outline()[1:-1])                             # (not across the frontispiece)
low = [l for l in low if not (abs(l[0]) < 12 and abs(l[3]) < 12 and l[2] > 30)]
add("low cornice", {"type": "bars", "lines": at_y(low, LOW - 0.25), "w": 1.6, "h": 0.5, "kind": "moulding",
                    "_about": "the cornice round the single-storey walls (aisles, east chapels, narthex)"})
mid = [[XC, 12.5, XC, ZW], [-XC, 12.5, -XC, ZW], [XA, ZW, XC, ZW], [-XA, ZW, -XC, ZW]]
arm = [[XE, -12.5, XE, 12.5], [-XE, -12.5, -XE, 12.5], [XA, ZA, XE, ZA], [XA, -ZA, XE, -ZA], [-XA, ZA, -XE, ZA], [-XA, -ZA, -XE, -ZA]]
add("upper cornices", {"type": "bars", "lines": [[a, MID - 0.25, b, c, MID - 0.25, d] for a, b, c, d in mid] + [[a, ARM - 0.25, b, c, ARM - 0.25, d] for a, b, c, d in arm],
                       "w": 1.5, "h": 0.5, "kind": "moulding", "_about": "the cornices of the galleries', the arms' and the vaults' walls"})
parts["upper cornices"]["lines"] += [[sx * PC, SPR - 0.25, ZW - 0.5, sx * PC, SPR - 0.25, XA] for sx in (1, -1)] + [[sx * PC, SPR - 0.25, -XA, sx * PC, SPR - 0.25, ZB] for sx in (1, -1)]
parts["upper cornices"]["lines"] += [[-FX, 15.25, ZT - 0.5, FX, 15.25, ZT - 0.5]] + [[sx * (FX - 0.5), 15.25, ZT, sx * (FX - 0.5), 15.25, ZW + 0.5] for sx in (1, -1)]

doc = {"name": "Alexander Nevsky Cathedral",
       "_about": "ALEXANDER NEVSKY CATHEDRAL, Sofia (A. N. Pomerantsev, 1882 / 1904-12), at its real size from OSM (way 155447771, 73.5 x 52.2 m) and photos: "
                 "the cross-in-square under the gilded dome on its drum of twenty windows (45 m), the transept arms ending in green semidomes on half rings of "
                 "windows, the apse's semidome behind the bema, the nave's barrel vault to the west; five aisles, the inner ones with galleries reached by "
                 "dog-leg stairs, the outer ones single storey, the east corners round under low quarter-domes; the narthex with its corner chapels under small "
                 "domes and arcaded porches; the frontispiece with its great arched gable over the three-arched porch, the bell tower on it (53 m) with its belfry "
                 "and gilded dome. Inside: the central, Russian and Bulgarian iconostases, the solea, the thrones under their canopies, the altar's baldachin, the "
                 "great chandelier under the dome; painted walls, mosaic vaults, the chequered marble floor.",
       "params": {"detail": 4}, "base": {"height": BASE, "steps": 4, "stepOut": 0.45, "margin": 1.5}, "railing": {"type": "stone"},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/alexander-nevsky.json"), "w").write(json.dumps(doc, indent=2) + "\n")

# ======================================================================================================== THE FINISH
LIME = ["#ece6d8", "#dfd8c6", "#cfc6b0", "#f4efe3"]       # the white Vratsa limestone
ACC = ["#c2b79f", "#ada08a", "#d3c9b2", "#9a8f79"]   # its darker mouldings, cornices, arches
GREENM = ["#2f5a46", "#1f4434", "#4f7f66", "#173528"]     # the iconostases' green marble columns
CHECK = ["#ece6d8", "#2c2a28", "#cfc6b0", "#4a4642"]      # the chequered marble floor
MURAL = ["#c9a24a", "#2c3a58", "#8a3a2a", "#d9b24a", "#a8452f", "#e2d2a8"]   # the painted walls and vaults: blue, gold, red
WMARBLE = ["#e8dfcc", "#d6c7a8", "#b9a27c", "#efe8da"]    # the marble, onyx and alabaster of the lower walls
OCHRE = ["#c9a24a", "#6e5a34", "#4a2e24", "#b08a3c", "#7a3a28", "#cdbb8e"]  # the vaults' muted ochre ground (index 1), gold and red ornament
RED = ["#c98f7e", "#b07062", "#e2bcae", "#8e5246"]        # the iconostasis' light red upper tier
dd = lambda *ks: [f"dome/{k}" for k in ks]
bd = lambda *ks: [f"belfry dome/{k}" for k in ks]
GOLD = dd("dome", "ribs") + bd("dome", "ribs") + [k for k in parts if k.startswith("finial")]
FLAT = [k for k, v in parts.items() if v.get("flatRoof")] + ["drum deck", "outer aisle ceilings 1", "outer aisle ceilings 2"]
fin = {"name": "Alexander Nevsky Cathedral", "building": "architecture/alexander-nevsky",
       "_about": "Alexander Nevsky Cathedral: walls of pale Vratsa limestone with darker cornices and arches on a granite plinth; the central and the "
                 "bell tower's domes gold leaf, every other dome, semidome, vault and roof green copper. Inside: the chequered marble floor, marble "
                 "lower walls, the piers and arcades painted with saints on gold, the vaults and walls painted in blue, red and gold, the dome's "
                 "God Sabaoth, the iconostases of white marble with their icons, green marble columns, the gilt chandeliers.",
       "stone": {"color": "#e4ddcc", "accent": "#c2b79f", "pat": "ashlar"},
       "rules": [
           {"parts": ["dome/dome"], "side": "in", "pattern": "mosaic/wall pantocrator", "scale": 6, "_about": "the dome's inside: God Sabaoth (Myasoedov)"},
           {"parts": GOLD + ["great chandelier", "chandelier chains", "royal throne dome", "patriarchal throne dome", "baldachin dome",
                             "central iconostasis cornice", "central iconostasis crown"],
            "pattern": "roofs/gold leaf", "_about": "the gilded domes, their ribs, balls and crosses; the chandeliers' gilt hoops; the canopies' little domes"},
           {"parts": ["tower icon"], "pattern": "mosaic/wall emperor", "scale": 4.2, "_about": "the mosaic icon of St Alexander Nevsky on the bell tower"},
           {"parts": ["central iconostasis columns"], "pattern": "stone/marble", "palette": GREENM, "_about": "the iconostasis' green marble columns"},
           {"parts": ["central iconostasis", "russian iconostasis", "bulgarian iconostasis"], "surface": "wall", "above": BASE + 4.3, "pattern": "stone/revetment", "palette": RED,
            "_about": "the iconostases' upper tier of light red marble"},
           {"parts": ["central iconostasis", "russian iconostasis", "bulgarian iconostasis"], "surface": "wall", "pattern": "mosaic/wall apostles", "scale": 2.2,
            "_about": "their icons in white and yellow marble frames"},
           {"parts": ["solea", "russian solea", "bulgarian solea", "altar step", "royal throne dais", "patriarchal throne dais"], "pattern": "stone/marble", "palette": "marble-rose"},
           {"parts": ["altar", "russian altar", "bulgarian altar", "baldachin columns", "baldachin entablature", "royal throne canopy columns", "patriarchal throne canopy columns",
                      "royal throne canopy", "patriarchal throne canopy", "royal throne", "patriarchal throne"], "pattern": "stone/marble", "palette": "alabaster",
            "_about": "the altars, the baldachin, the thrones and their canopies in white marble and alabaster"},
           {"parts": ["apse semidome"], "side": "in", "pattern": "mosaic/wall virgin", "scale": 5.5, "_about": "the apse's semidome: the Virgin, one great figure"},
           {"parts": ["arm semidomes"], "side": "in", "pattern": "mosaic/wall deesis", "scale": 5.5, "_about": "the arms' semidomes: the Deesis, three great figures -- their own register, not the piers' saints"},
           {"parts": ["dome/drum"], "side": "in", "pattern": "mosaic/wall apostles", "scale": 4.0, "_about": "the drum: one register of saints between the windows"},
           {"parts": ["piers", "pier heads"], "side": "in", "above": BASE + 3.0, "below": BASE + 8.0, "pattern": "mosaic/wall apostles", "scale": 3.8,
            "_about": "the piers: ONE register of saints on gold, 3-8 m over the floor (the rest of the pier the walls' blue)"},
           {"parts": ["kind:vault", "great arches", "drum deck", "pendentives"], "side": "in", "pattern": "painted/russian floral", "palette": OCHRE,
            "_about": "the vaults, arches and pendentives on a muted ochre ground, the gold only in the ornament"},
           {"surface": "wall", "side": "in", "above": BASE + 3.0, "pattern": "painted/russian floral", "palette": MURAL, "_about": "every other wall inside painted"},
           {"surface": "wall", "side": "in", "pattern": "stone/revetment", "palette": WMARBLE, "_about": "the lower walls in Italian marble, onyx and alabaster"},
           {"surface": "ceiling", "side": "in", "pattern": "painted/starry vault", "palette": MURAL, "_about": "the galleries' and aisles' ceilings"},
           {"surface": "floor", "side": "in", "pattern": "floors/checker", "palette": CHECK, "scale": 1.6, "_about": "the chequered marble floor"},
           {"parts": ["kind:column"], "pattern": "stone/marble", "palette": "alabaster"},
           {"parts": FLAT, "side": "out", "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the flat roofs, copper too"},
           {"parts": ["west vault", "bema vault", "arm semidomes", "apse semidome", "east round domes"], "side": "out", "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the vaults' backs"},
           {"surface": "roof", "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the semidomes, the small domes, the vaults' backs, the gables' barrels and every roof: green copper"},
           {"parts": ["base"], "pattern": "stone/granite", "palette": "granite", "_about": "the granite plinth and steps"},
           {"surface": "floor", "pattern": "stone/granite", "palette": "granite"},
           {"parts": ["kind:moulding", "drum hoods", "arm semidome hoods", "apse hoods", "belfry hoods", "west porch hoods", "wing loggia hoods",
                      "tower cornice", "tower band", "apse cornice", "crossing gable rims", "arm gable rims", "frontispiece gable rim"],
            "pattern": "stone/ashlar fine", "palette": ACC, "_about": "the darker cornices and arched hoods"},
           {"surface": "ceiling", "pattern": "stone/ashlar fine", "palette": LIME},
           {"surface": "wall", "pattern": "stone/ashlar fine", "palette": LIME, "_about": "the walls of pale Vratsa limestone"}]}
open(os.path.join(ROOT, "assets/finishes/alexander-nevsky.json"), "w").write(json.dumps(fin, indent=2) + "\n")

# ======================================================================================================== THE DOORS
OAK = "#4e3220"
door = lambda part, near, style="russian", about=None, **kw: {**({"_about": about} if about else {}), "part": part, "near": [list(p) for p in near], "style": style, "color": OAK, **kw}
doors = {"name": "Alexander Nevsky Cathedral: doors", "building": "alexander-nevsky",
         "_about": "the cathedral's eleven outer doors of carved Slavonian oak -- three under the west porch, the narthex wings' and chapels', "
                   "the transepts' portals and side doors -- and the great door from the vestibule into the nave",
         "doors": [door("frontispiece", [(0, ZT)], leafH=4.0, about="the great west door under the porch"),
                   door("frontispiece", [(-3.8, ZT), (3.8, ZT)], about="the lesser doors either side of it"),
                   door("west wall", [(0, ZW)], leafH=3.6, about="from the vestibule into the nave"),
                   door("narthex west walls", [(14.4, ZN + 0.5), (-14.4, ZN + 0.5), (17.5, ZN + 0.5), (-17.5, ZN + 0.5)], about="the narthex wings' doors under their arcaded porches"),
                   door("narthex west walls", [(21.3, ZN + 0.5), (-21.3, ZN + 0.5)], about="the corner chapels' west doors"),
                   door("arm end walls", [(XE + 0.75, 0), (-XE - 0.75, 0)], leafH=3.6, about="the transepts' great portals"),
                   door("arm end walls", [(XE + 0.75, -6), (XE + 0.75, 6), (-XE - 0.75, -6), (-XE - 0.75, 6)], about="their side doors"),
                   door("west flanks", [(XF + 0.5, 26.0), (-XF - 0.5, 26.0)], about="the side doors to the west aisles")]}
open(os.path.join(ROOT, "assets/doors/alexander-nevsky.json"), "w").write(json.dumps(doors, indent=2) + "\n")

if __name__ == "__main__":
    print("alexander-nevsky:", len(parts), "parts")
