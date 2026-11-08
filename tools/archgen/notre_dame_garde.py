# NOTRE-DAME DE LA GARDE, Marseille (Henri Esperandieu, 1853-64; the tower's Virgin 1870), the Romanesque-Byzantine
# basilica on the summit of the old fort -- built (2026-11-04) on its real plan: the footprints of OpenStreetMap (the
# church, way 69137913; the tower, 1324841042 (41 m); the dome, 1558275295; the statue, 1558275296 (64.7 m); the
# terrace 103879962, the steps, the lift building 69131508 and the retaining walls 178027585/588/589), turned 49 degrees
# onto the church's axis, and the dimensions of the French and English Wikipedia:
#   https://fr.wikipedia.org/wiki/Basilique_Notre-Dame-de-la-Garde   https://en.wikipedia.org/wiki/Notre-Dame_de_la_Garde
#   THE UPPER CHURCH: a nave of three square bays, each under a CUPOLA on pendentives, between transverse arches; three
# side chapels a side under the bays (their twin windows the only light of the nave); the crossing under the DOME, its
# octagonal drum a window a face under a gable, the dome ribbed; transept arms that do not stand out of the walls, their
# fronts a rose over two windows under a gable; the choir and the APSE with its five blind arcades on red granite
# columns, the sacristies beside it. Inside polychrome marble -- the piers and every arch in courses of white Carrara
# and red La Celle marble -- and 1,200 m2 of mosaics: gold in the cupolas, the dome and the apse's half dome (vines on
# gold), blue strewn with gold over the lunettes. Outside the whole church in courses of white Calissanne limestone and
# green Golfolina sandstone.
#   THE TOWER (41 m) before the front, square: the porch with Revoil's bronze doors, two stages of five blind arches
# (the middle one a window over a balcony), the BELFRY (three openings a face on red granite colonnettes, the bourdon in
# it), the terrace with its balustrade and four angels at the corners, the round CAMPANILE of sixteen columns (12.5 m)
# and on it the gilt copper VIRGIN AND CHILD (Lequesne, 11.2 m). An octagonal stair turret against its south-west face
# climbs from the terrace to the tower's terrace.
#   THE CRYPT under the church, cut in the rock: a low barrel nave, six chapels, the altar and the Vierge au Bouquet in
# its apse; entered from the drawbridge through a passage under the porch terrace, the statues of Mazenod and Pius IX
# in its narthex; two stairs beside the choir climb from it to the sacristies.
#   THE FORT: the terrace round the basilica (walked all round it), its parapets, the bastion front with the DRAWBRIDGE
# over the ditch, the two flights from the drawbridge's platform up to the porch terrace (the crypt straight ahead),
# the stair pier and the LIFT tower (1892) in the ditch, the double staircase up from the road, the lower east terrace
# and its two flights, the fort's ranges round it.
#   The front faces +z (north-west); the origin is on the axis, at the forecourt's level (y 0).
#   python3 tools/archgen/notre_dame_garde.py -> assets/architecture/notre-dame-garde.json, assets/finishes/..., assets/doors/...
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import statuary as ST
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n); return n
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q, PI = math.pi / 2, math.pi
r3 = lambda v: round(v, 3)
SIDES = ((1, "east"), (-1, "west"))
ROUND = {"profile": "semicircular"}

# ---- the levels
YB = 7.3            # the drawbridge, its platform, the crypt's floor
T = 13.3            # the upper church's floor and the summit terrace round it
LD = 5.44           # the double staircase's landing (34 steps of 16 cm from the road)
TE = 10.6           # the lower east terrace
UP = 13.0           # the church's wall heads over its floor
SPR = 8.6           # the arches' and the pendentives' springing over the floor
# ---- the plan (x across, z along the axis)
NI, NO = 3.3, 4.0   # the nave's inner face, its walls' outer
CO = 4.6            # the crossing's and the choir's walls' outer face
OI, OO = 7.2, 8.2   # the outer walls
TX, TZ0, TZ1, TW = 4.5, 18.15, 27.15, 1.5     # the tower: half width, back and front faces, walls
TZC = (TZ0 + TZ1) / 2
ZF = TZ0                                      # the nave's inner front (the tower's back face)
BAYS = [(18.15, 11.55), (10.65, 4.05), (3.15, -3.45)]
BC = [(a + b) / 2 for a, b in BAYS]
PIERS = [(11.55, 10.65), (4.05, 3.15)]
X0, X1, X2, X3 = -3.45, -5.05, -11.65, -13.25  # the crossing's front piers, its square, its back piers
XC = (X1 + X2) / 2
ZA = -20.0          # the apse's middle; its walls 3.3 to 4.6 round it
SB = -22.6          # the sacristies' back walls (to -23.6)
CR = T - 0.6        # the crypt's ceiling (the church's floor slab under it)

def arch(at, w, sill, spring, glass=None, **kw):
    o = {"at": r3(at), "width": r3(w), "sill": r3(sill), "springing": r3(spring), "head": ROUND, **kw}
    if glass is not None: o["glass"] = glass
    return o

def wall_z(name, xa, xb, z0, z1, tiers, y=0, about=None, **kw):
    """a wall along z, from xa to xb thick, z0..z1 long; its tiers' openings `at` given as world z"""
    zc = (z0 + z1) / 2
    tt = [{**t, "openings": [{**o, "at": r3(zc - o["at"])} for o in t["openings"]]} for t in tiers]
    d = {"type": "wall", "width": r3(z1 - z0), "thickness": r3(xb - xa), "height": r3(sum(t.get("h", 0) for t in tiers)),
         "tiers": tt, "at": [[r3(xb), r3(y), r3(zc), Q]], **kw}
    if about: d["_about"] = about
    return add(name, d)

def wall_x(name, za, zb, x0, x1, tiers, y=0, about=None, **kw):
    """a wall along x, from za to zb thick, x0..x1 long; its tiers' openings `at` given as world x"""
    xc = (x0 + x1) / 2
    tt = [{**t, "openings": [{**o, "at": r3(o["at"] - xc)} for o in t["openings"]]} for t in tiers]
    d = {"type": "wall", "width": r3(x1 - x0), "thickness": r3(zb - za), "height": r3(sum(t.get("h", 0) for t in tiers)),
         "tiers": tt, "at": [[r3(xc), r3(y), r3(zb), 0]], **kw}
    if about: d["_about"] = about
    return add(name, d)

def box(name, x0, x1, z0, z1, y0, y1, about=None, **kw):
    d = {"type": "box", "width": r3(x1 - x0), "length": r3(z1 - z0), "height": r3(y1 - y0), "at": [[r3((x0 + x1) / 2), r3(y0), r3((z0 + z1) / 2), 0]], **kw}
    if about: d["_about"] = about
    return add(name, d)

def boxes(name, spans, y0, y1, about=None, **kw):
    """one part of several boxes the same height: spans [(x0, x1, z0, z1), ...] -- each its own box part, numbered"""
    for i, (x0, x1, z0, z1) in enumerate(spans):
        box(f"{name} {i + 1}" if len(spans) > 1 else name, x0, x1, z0, z1, y0, y1, about=about if i == 0 else None, **kw)

def arc(cx, cz, r, a0, a1, n):
    """points on a circle, the angle from +z toward +x (degrees)"""
    return [[r3(cx + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))), r3(cz + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)))] for i in range(n + 1)]

def interior(name, x0, x1, z0, z1, y, h, about=None):
    d = {"type": "interior", "plan": {"rect": [r3(x1 - x0), r3(z1 - z0)]}, "height": r3(h), "at": [[r3((x0 + x1) / 2), r3(y), r3((z0 + z1) / 2), 0]]}
    if about: d["_about"] = about
    return add(name, d)

def parapet(name, x0, x1, z0, z1, y, h=1.1, pierced=True, about=None):
    """a parapet on a wall head or a terrace's edge: pierced with small round-headed openings (the frieze of the church's
    wall heads), or solid"""
    along_x = (x1 - x0) >= (z1 - z0)
    L = (x1 - x0) if along_x else (z1 - z0)
    if not pierced or L < 1.6:
        return box(name, x0, x1, z0, z1, y, y + h, about=about)
    n = max(1, int((L - 0.4) / 0.95))
    op = {"pattern": str(n), "width": 0.45, "gap": r3((L - 0.4) / n - 0.45), "sill": 0.3, "springing": r3(h - 0.45), "head": ROUND}
    if along_x:
        d = {"type": "wall", "width": r3(L), "thickness": r3(z1 - z0), "height": h, "openings": op, "glass": False, "at": [[r3((x0 + x1) / 2), r3(y), r3(z1), 0]]}
    else:
        d = {"type": "wall", "width": r3(L), "thickness": r3(x1 - x0), "height": h, "openings": op, "glass": False, "at": [[r3(x1), r3(y), r3((z0 + z1) / 2), Q]]}
    if about: d["_about"] = about
    return add(name, d)

def side(sx, a, b):
    """the span a..b (both >= 0) on side sx, ordered"""
    return (min(sx * a, sx * b), max(sx * a, sx * b))

# =====================================================================================================================
# THE ROCK AND THE CRYPT
box("rock", -OO, OO, -24.6, TZ0 + 1.0, 0, YB, walked=True,
    about="the rock the church stands on, its top the crypt's floor (the crypt is cut into the summit of the hill)")
box("tower rock", -TX, TX, TZ0 + 1.0, TZ1, 0, YB, walked=True)
box("passage floor", -1.6, 1.6, TZ1, 30.5, 0, YB, walked=True)
# the crypt's nave: a low barrel from the tower's foot to the apse, its side walls arched into the chapels
add("crypt vault", {"type": "barrel", "width": 2 * NI, "length": r3(ZF - ZA), "springing": r3(YB + 3.3), "top": CR, "head": {"profile": "segmental", "rise": 1.8},
                    "at": [[0, 0, ZF, 0]], "_about": "the crypt's low barrel vault, cut in the rock: from the tower's foot to the apse"})
CH = CR - YB                                   # the crypt's height
for sx, nm in SIDES:
    wall_z(f"crypt {nm} wall", *side(sx, NI, NO), X0, ZF, [{"h": CH, "openings": [arch(c, 2.4, 0, 2.1, False) for c in BC]}], y=YB,
           about="the crypt's nave walls: an arch into each of its six chapels" if sx > 0 else None)
    wall_z(f"crypt {nm} crossing wall", *side(sx, NI, CO), X3, X0, [{"h": CH, "openings": [arch(XC, 2.4, 0, 2.1, False)]}], y=YB)
    wall_z(f"crypt {nm} choir wall", *side(sx, NI, CO), ZA, X3, [{"h": CH, "openings": []}], y=YB)
    wall_z(f"crypt {nm} outer wall", *side(sx, OI, OO), -23.6, ZF + 1.0, [{"h": CH, "openings": []}], y=YB)
    for i, (za, zb) in enumerate(PIERS):
        box(f"crypt {nm} chapel wall {i + 1}", *side(sx, NO, OI), zb, za, YB, CR)
    box(f"crypt {nm} chapel front", *side(sx, NO, OO), ZF, ZF + 1.0, YB, CR)
    box(f"crypt {nm} transept front", *side(sx, NO, OI), X1, X0, YB, CR)
    wall_x(f"crypt {nm} transept back", X3, X2, *side(sx, CO, OI), [{"h": CH, "openings": [arch(sx * 5.2, 1.1, 0, 1.9, False)]}], y=YB,
           about="the door from the crypt's transept to the stair up to the sacristy" if sx > 0 else None)
    box(f"crypt {nm} stair fill", *side(sx, 5.8, OI), SB, X3, YB, CR)
    wall_x(f"{nm} sacristy back", SB - 1.0, SB, *side(sx, CO, OO), [{"h": CR - YB, "openings": []}, {"h": 0.6 + 7.0, "openings": [arch(sx * 6.6, 1.0, 2.0, 4.2)]}], y=YB)
# the crypt's apse: its wall, the half dome, the altar and the Vierge au Bouquet
NA = 10
HALF = [3, 4, 5, 6, 7]
add("crypt apse wall", {"type": "ring", "count": NA, "rOuter": CO, "rInner": NI, "height": 3.3, "y": YB, "turn": 0, "at": HALF, "solid": True, "place": [[0, 0, ZA, 0]],
                        "_about": "the crypt's apse"})
add("crypt apse vault", {"type": "dome", "sweep": 0.5, "sides": NA, "radius": 3.6, "thickness": 0.3, "head": {"profile": "segmental", "rise": 1.8}, "at": [[0, YB + 3.3, ZA, PI]]})
box("crypt altar", -1.1, 1.1, ZA - 0.4, ZA + 0.6, YB, YB + 1.05, about="the crypt's high altar in Golfolina stone")
box("crypt altar step", -1.8, 1.8, ZA - 0.6, ZA + 1.6, YB, YB + 0.15)
box("vierge au bouquet pedestal", -0.45, 0.45, ZA - 2.4, ZA - 1.6, YB, YB + 1.6, about="the pedestal of the Vierge au Bouquet behind the crypt's altar")
for k, v in ST.madonna((0, YB + 1.6, ZA - 2.0), scale=0.95, stone="painted", seed=21, prefix="vierge au bouquet").items(): add(k, v)
# the narthex in the tower's foot and the passage under the porch terrace from the drawbridge
for k, v in ST.row("crypt founder", [(-2.3, YB + 0.5, 21.4), (2.3, YB + 0.5, 21.4)], kind="man", pose=["prayer", "blessing"], style="monastic", stone="marble",
                   scale=1.05, face=[ST.FACE_PX, ST.FACE_NX]).items(): add(k, v)
add("crypt founders pedestals", {"type": "box", "width": 0.9, "length": 0.9, "height": 0.5, "at": [[-2.3, YB, 21.4, 0], [2.3, YB, 21.4, 0]],
                                 "_about": "Ramus's marble statues in the crypt's entrance: Mgr de Mazenod, who founded the basilica, and Pius IX"})
box("passage roof", -1.6, 1.6, TZ1, 30.5, CR + 0.1, T, walked=True)
wall_x("crypt portal", 30.5, 31.2, -2.4, 2.4, [{"h": T - YB, "openings": [arch(0, 2.4, 0, 3.0, False, surround={"style": "romanesque", "orders": 2})]}], y=YB,
       about="the crypt's door straight ahead from the drawbridge, in the bastion's face under the porch terrace")
# the stairs from the crypt to the sacristies (beside the choir, behind the back crossing piers)
for sx, nm in SIDES:
    add(f"{nm} sacristy stair", {"type": "flight", "width": 1.2, "run": 0.25, "base": YB, "top": T, "steps": 30, "landing": 1.3,
                                 "at": [[r3(5.8 if sx > 0 else -4.6), 0, r3(X3 - 0.15), Q]],
                                 **({"_about": "the stair from the crypt up to the sacristy, beside the choir"} if sx > 0 else {})})

# =====================================================================================================================
# THE UPPER CHURCH
box("church floor", -OO, OO, X3, ZF + 1.0, CR, T, walked=True, about="the upper church's floor, over the crypt")
box("choir floor", -CO, CO, ZA, X3, CR, T, walked=True)
add("apse floor", {"type": "prism", "walked": True, "plan": {"points": arc(0, 0, CO, 90, 270, 10)}, "height": 0.6, "at": [[0, CR, ZA, 0]]})
for sx, nm in SIDES:
    box(f"{nm} sacristy floor", *side(sx, CO, OO), -17.6, X3, CR, T, walked=True)
    box(f"{nm} sacristy floor back", *side(sx, 5.8, OO), SB, -17.6, CR, T, walked=True)
    box(f"{nm} stair parapet", *side(sx, CO, 5.8), -17.8, -17.6, T, T + 1.0)
    box(f"{nm} stair parapet side", *side(sx, 5.8, 6.0), -20.6, -17.6, T, T + 1.0)
box("tower floor", -TX, TX, TZ0, TZ1, CR, T, walked=True)

# ---- the outer walls: the chapels' twin windows, the transepts' fronts (two windows and the rose), the cornice and the
# pierced frieze over it; pilaster strips at the bays
def outer_tiers():
    ops = []
    for c in BC:
        ops += [arch(c - 0.75, 0.95, 3.8, 6.6, surround={"style": "romanesque", "orders": 1}), arch(c + 0.75, 0.95, 3.8, 6.6, surround={"style": "romanesque", "orders": 1})]
    ops += [arch(XC - 1.6, 1.1, 3.4, 7.0, surround={"style": "romanesque", "orders": 1}), arch(XC + 1.6, 1.1, 3.4, 7.0, surround={"style": "romanesque", "orders": 1}),
            ]
    return [{"h": 8.8, "openings": ops}, {"h": UP - 8.8, "openings": [{"at": r3(XC), "width": 2.6, "sill": 1.7, "springing": 1.7, "head": ROUND, "foot": ROUND, "tracery": True}]}]
CORN = [{"y": 11.5, "h": 0.5, "out": 0.3, "profile": "cornice"}, {"y": 0.0, "h": 0.6, "out": 0.12, "profile": "band"}]
for sx, nm in SIDES:
    wall_z(f"{nm} outer wall", *side(sx, OI, OO), X3, ZF + 1.0, outer_tiers(), y=T, courses=CORN,
           about="the church's outer walls in white and green courses: the chapels' twin windows (the nave's light), the transept's front of two windows and a rose; the cornice" if sx > 0 else None)
    parapet(f"{nm} frieze", *side(sx, OO - 0.5, OO), X3, ZF + 1.0, T + UP, 1.2,
            about="the pierced frieze along the wall heads, hiding the low roofs" if sx > 0 else None)
    wall_x(f"{nm} front wall", ZF, ZF + 1.0, *side(sx, TX, OO), [{"h": UP, "openings": [arch(sx * 6.3, 0.95, 4.2, 6.6)]}], y=T, courses=CORN)
    parapet(f"{nm} front frieze", *side(sx, TX, OO - 0.5), ZF + 0.5, ZF + 1.0, T + UP, 1.2)
    add(f"{nm} pilasters", {"type": "box", "width": 0.35, "length": 1.1, "height": 11.5,
                            "at": [[r3(sx * (OO + 0.175)), T, r3(z), 0] for z in [ZF + 0.45] + [(a + b) / 2 for a, b in PIERS] + [(X0 + X1) / 2, (X2 + X3) / 2]],
                            **({"_about": "the pilaster strips along the outer walls at the transverse arches"} if sx > 0 else {})})
    # the sacristies: lower, flat-roofed, a door out onto the terrace
    wall_z(f"{nm} sacristy wall", *side(sx, OI, OO), SB - 1.0, X3, [{"h": 7.0, "openings": [arch(-16.4, 1.4, 0, 2.5, False), arch(-20.6, 1.0, 2.2, 4.4)]}], y=T,
           about="the sacristies' outer walls, their doors onto the terrace" if sx > 0 else None)
    box(f"{nm} sacristy roof", *side(sx, CO, OO + 0.2), SB - 1.2, X3, T + 7.0, T + 7.5, flatRoof=True)
    parapet(f"{nm} sacristy parapet", *side(sx, OO - 0.3, OO + 0.2), SB - 1.2, X3, T + 7.5, 0.7, pierced=False)

# ---- the nave: its walls on the chapels' arches, the transverse arches between the bays, a cupola on pendentives over each
for sx, nm in SIDES:
    wall_z(f"nave {nm} wall", *side(sx, NI, NO), X0, ZF, [{"h": SPR, "openings": [arch(c, 5.0, 0, 5.4, False) for c in BC]}, {"h": UP - SPR, "openings": []}], y=T,
           about="the nave's walls: an arch into each side chapel, the lunettes of the cupolas' arches over them" if sx > 0 else None)
    for i, (za, zb) in enumerate(PIERS):
        box(f"{nm} chapel wall {i + 1}", *side(sx, NO, OI), zb, za, T, T + SPR)
    box(f"{nm} chapel ceiling", *side(sx, NO, OI), X0, ZF, T + SPR, T + SPR + 0.4, flatRoof=True)
for i, (za, zb) in enumerate(PIERS):
    wall_x(f"transverse arch {i + 1}", zb, za, -NO, NO, [{"h": UP, "openings": [arch(0, 2 * NI, 0, SPR, False)]}], y=T,
           about="the transverse arches between the nave's bays, in courses of red and white marble" if i == 0 else None)
add("nave pendentives", {"type": "pendentives", "span": 2 * NI, "springing": T + SPR, "sides": 16, "at": [[0, 0, r3(c), 0] for c in BC],
                         "deck": {"thickness": 0.5, "out": 0.7}, "_about": "the pendentives of the nave's three bays"})
add("nave cupolas", {"type": "dome", "sides": 16, "turn": -0.5, "radius": NI + 0.3, "thickness": 0.3, "head": {"profile": "segmental", "rise": 1.9},
                     "at": [[0, r3(T + SPR + NI), r3(c), 0] for c in BC], "_about": "the three cupolas over the nave, gold mosaic inside (doves round a fleuron)"})

# ---- the crossing: four great arches, the pendentives, the dome on its octagonal drum; the transept arms' barrels
wall_x("crossing front arch", X1, X0, -CO, CO, [{"h": UP, "openings": [arch(0, 2 * NI, 0, SPR, False)]}], y=T, about="the crossing's four great arches on its piers")
wall_x("crossing back arch", X3, X2, -CO, CO, [{"h": UP, "openings": [arch(0, 2 * NI, 0, SPR, False)]}], y=T)
for sx, nm in SIDES:
    wall_z(f"crossing {nm} arch", *side(sx, NI, CO), X3, X0, [{"h": UP, "openings": [arch(XC, 2 * NI, 0, SPR, False)]}], y=T)
    box(f"{nm} transept front", *side(sx, CO, OI), X1, X0, T, T + UP)
    box(f"{nm} transept back", *side(sx, CO, OI), X3, X2, T, T + UP)
    add(f"{nm} transept vault", {"type": "barrel", "width": 2 * NI, "length": r3(OI - CO), "springing": r3(T + SPR), "top": T + UP, "head": ROUND,
                                 "at": [[r3(OI if sx > 0 else -CO), 0, r3(XC), Q]], **({"_about": "the barrels over the transept arms"} if sx > 0 else {})})
add("crossing pendentives", {"type": "pendentives", "span": 2 * NI, "springing": T + SPR, "sides": 16, "at": [[0, 0, r3(XC), 0]], "deck": {"thickness": 0.8, "out": 1.3},
                             "_about": "the crossing's pendentives (the four evangelists in mosaic)"})
DY = T + SPR + NI                                # the pendentives' crown: the drum's foot
DH = 9.4                                         # the drum
add("dome", comp("components/drum-dome", {"R": NI, "dt": 1.1, "H": DH, "n": 8, "every": 1, "winW": 1.4, "winSill": 3.8, "winH": 3.4, "profile": "pointed", "spread": 0.25,
                                          "domeT": 0.4, "ribsN": 32, "ribW": 0.16, "pedA": "triangular", "pedB": "triangular"},
                 [[0, r3(DY), r3(XC), 0]], build=["drum a", "drum b", "dome", "ribs", "interior"],
                 _about="the dome over the crossing: the octagonal drum, a window under a gable in every face, the ribbed dome in white and green courses (OSM: 45 m to the cross)"))
DTOP = DY + DH + 5.4                        # (the dome's crown: the drum's head and the dome's radius)
# the square base the drum stands on over the roofs, its corners round the octagon
ap = NI + 1.1
t8 = ap * math.tan(math.pi / 8)
add("drum base", {"type": "prism", "flatRoof": True, "plan": {"points": [[r3(ap), r3(t8)], [CO, r3(t8)], [CO, CO], [r3(t8), CO], [r3(t8), r3(ap)]]}, "height": 2.6,
                  "at": [[0, r3(DY + 0.8), r3(XC), a] for a in (0, Q, PI, -Q)], "_about": "the square base round the drum's foot, over the roofs"})
add("drum pinnacles", {"type": "pinnacle", "w": 0.45, "h": 1.0, "s": 1.6, "sides": 8,
                       "at": [[r3(ap / math.cos(math.pi / 8) * math.sin(a)), r3(DY + DH), r3(XC + ap / math.cos(math.pi / 8) * math.cos(a)), 0]
                              for a in [math.pi / 8 + k * math.pi / 4 for k in range(8)]],
                       "_about": "small pinnacles at the drum's corners"})
add("dome knob", {"type": "dome", "sides": 12, "radius": 0.45, "thickness": 0, "head": ROUND, "at": [[0, r3(DTOP - 0.15), r3(XC), 0]]})
add("dome cross", {"type": "bars", "w": 0.16, "lines": [[0, r3(DTOP + 0.3), r3(XC), 0, r3(DTOP + 3.0), r3(XC)], [-0.65, r3(DTOP + 2.2), r3(XC), 0.65, r3(DTOP + 2.2), r3(XC)]],
                   "_about": "the gilt cross over the dome"})

# ---- the choir and the apse: five blind arcades on red granite columns, the half dome (vines on gold); the sacristies
for sx, nm in SIDES:
    wall_z(f"choir {nm} wall", *side(sx, NI, CO), ZA, X3, [{"h": UP, "openings": [arch(-15.0, 1.2, 0, 2.2, False)]}], y=T,
           about="the choir's walls, a door through each into the sacristy" if sx > 0 else None)
add("choir vault", {"type": "barrel", "width": 2 * NI, "length": r3(X3 - ZA), "springing": r3(T + SPR), "top": T + UP, "head": ROUND, "at": [[0, 0, X3, 0]],
                    "_about": "the choir's barrel"})
APL = [[0, 0, ZA, 0]]
add("apse arcade", {"type": "ring", "count": NA, "rOuter": 3.8, "rInner": NI, "height": SPR, "y": T, "turn": 0, "at": HALF, "glass": False, "place": APL,
                    "opening": {"width": 1.3, "sill": 1.3, "springing": 5.0, "head": ROUND}, "_about": "the apse's five blind arcades"})
add("apse wall", {"type": "ring", "count": NA, "rOuter": CO, "rInner": 3.8, "height": UP, "y": T, "turn": 0, "at": HALF, "solid": True, "place": APL,
                  "_about": "the apse's outer wall, behind the arcades"})
add("apse columns", {"type": "column", "radius": 0.17, "height": 5.0, "sides": 12,
                     "at": [[r3(3.15 * math.sin(math.radians(a))), r3(T + 1.3), r3(ZA + 3.15 * math.cos(math.radians(a))), 0] for a in range(90, 271, 36)],
                     "_about": "the red granite columns between the apse's arcades"})
add("apse half dome", {"type": "dome", "sweep": 0.5, "sides": NA, "radius": 3.8, "thickness": 0.5, "head": ROUND, "at": [[0, r3(T + SPR), ZA, PI]],
                       "_about": "the apse's half dome: the ship in a medallion amid vine scrolls and birds on gold"})
add("apse dome band", {"type": "ring", "count": NA, "rOuter": r3(NI + 0.05), "rInner": r3(NI - 0.12), "height": 0.45, "y": r3(T + SPR - 0.45), "turn": 0, "at": HALF,
                        "solid": True, "place": APL, "_about": "the mosaic band at the half dome's springing (AVE MARIA GRATIA PLENA)"})
add("apse roof", {"type": "dome", "sweep": 0.5, "sides": NA, "radius": 4.85, "thickness": 0, "head": {"profile": "trigonal", "rise": 2.7}, "at": [[0, T + UP, ZA, PI]]})
box("altar platform", -2.6, 2.6, ZA - 1.0, X3 - 1.2, T, T + 0.45, walked=True, about="the sanctuary's platform")
box("altar step", -2.6, 2.6, X3 - 1.2, X3 - 0.85, T, T + 0.22, walked=True)
box("high altar", -1.3, 1.3, ZA + 0.6, ZA + 1.6, T + 0.45, T + 1.5, about="the high altar in marble and gilt bronze")
box("silver virgin column", -0.4, 0.4, ZA - 0.6, ZA + 0.2, T + 0.45, T + 3.3)
for k, v in ST.madonna((0, T + 3.3, ZA - 0.2), scale=0.75, stone="marble", seed=31, prefix="silver virgin").items(): add(k, v)
# pews
add("pews", {"type": "box", "width": 2.3, "length": 0.45, "height": 0.85,
             "at": [[r3(sx * 1.85), T, r3(z), 0] for c in BC for sx in (-1, 1) for z in [c + 2.3 - 1.0 * k for k in range(5)]] + [[r3(sx * 1.85), T, r3(z), 0] for sx in (-1, 1) for z in (-6.0, -7.0)],
             "_about": "the pews in the nave"})

# ---- the roofs: low gables in stone behind the frieze; the transepts' gables; the choir's; the half cone over the apse
add("nave roof", {"type": "roof", "form": "gable", "width": 2 * OO - 1.0, "length": r3(ZF + 1.0 - X0), "pitch": 13, "overhang": 0, "at": [[0, T + UP, r3((ZF + 1.0 + X0) / 2), 0]],
                  "_about": "the nave's low roof behind the frieze"})
add("transept roofs", {"type": "roof", "form": "gable", "width": r3(X0 - X3 + 0.3), "length": r3(OO + 0.2 - CO), "pitch": 33, "overhang": 0,
                       "at": [[r3(sx * (OO + 0.2 + CO) / 2), T + UP, r3(XC), Q] for sx in (-1, 1)], "_about": "the transepts' gabled roofs, their gables over the fronts"})
add("choir roof", {"type": "roof", "form": "gable", "width": 2 * CO, "length": r3(X3 - ZA), "pitch": 28, "overhang": 0, "at": [[0, T + UP, r3((X3 + ZA) / 2), 0]]})

# ---- interiors
interior("narthex", -TX + TW, TX - TW, TZ0 + TW, TZ1 - TW, T, SPR, about="the porch in the tower's foot, behind the bronze doors")
box("narthex ceiling", -TX + TW, TX - TW, TZ0 + TW, TZ1 - TW, T + SPR, T + SPR + 0.5, flatRoof=True)
interior("nave", -NI, NI, X0, ZF, T, SPR + NI + 1.9, about="the nave up into its cupolas")
for sx, nm in SIDES:
    for i, (a, b) in enumerate(BAYS):
        interior(f"{nm} chapel {i + 1}", *side(sx, NI, OI), b, a, T, SPR)
    interior(f"{nm} transept", *side(sx, NI, OI), X2, X1, T, UP)
    interior(f"{nm} sacristy", *side(sx, NI, OI), SB, X3, T, 7.0)
    interior(f"crypt {nm} chapels", *side(sx, NI, OI), X0, ZF, YB, CH)
    interior(f"crypt {nm} transept", *side(sx, NI, OI), X2, X1, YB, CH)
    interior(f"crypt {nm} stair", *side(sx, CO, 5.8), SB, X3 + 0.2, YB, T - YB + 2.2)
interior("crossing", -NI, NI, X3, X0, T, SPR + NI + 0.8)
add("drum interior", {"type": "interior", "plan": {"points": [[r3((NI + 0.5) * math.sin(math.pi / 8 + k * math.pi / 4)), r3((NI + 0.5) * math.cos(math.pi / 8 + k * math.pi / 4))] for k in range(8)]},
                        "height": DH, "at": [[0, r3(DY - 0.2), r3(XC), 0]], "_about": "inside the drum (its ring, its window reveals)"})
interior("choir", -NI, NI, ZA, X3, T, UP - 0.6)
add("apse interior", {"type": "interior", "plan": {"points": arc(0, 0, 4.2, 90, 270, 10)}, "height": SPR + NI, "at": [[0, T, ZA, 0]]})
interior("crypt nave", -NI, NI, ZA, ZF, YB, CH)
add("crypt apse interior", {"type": "interior", "plan": {"points": arc(0, 0, NI, 90, 270, 10)}, "height": CH, "at": [[0, YB, ZA, 0]]})
interior("crypt narthex", -TX + TW, TX - TW, TZ0 + TW, TZ1 - TW, YB, CH)
interior("crypt passage", -1.6, 1.6, TZ1 - TW, 30.5, YB, CH - 0.2)

# =====================================================================================================================
# THE TOWER: the porch, two stages of blind arcades, the belfry, the terrace, the campanile and the Virgin
S1, S2, BF, TT = T + 13.5, T + 21.0, T + 28.5, T + 39.0
stage = lambda: {"h": 7.5, "openings": [arch(0, 1.1, 1.6, 4.4)]}
belfry = {"h": 8.5, "openings": [arch(x, 1.5, 1.2, 6.2) for x in (-2.25, 0, 2.25)], "glass": False}
top = {"h": 2.0, "openings": []}
tface = lambda crypt, porch: [{"h": T - YB, "openings": crypt}, {"h": S1 - T, "openings": porch}, stage(), stage(), belfry, top]
add("tower", {"type": "enclosure", "plan": {"rect": [2 * TX, TZ1 - TZ0]}, "thickness": TW, "height": r3(TT - YB), "at": [[0, YB, TZC, 0]], "glass": True,
              "tiers": tface([], [arch(0, 1.0, 7.0, 9.6)]),
              "faces": {"0": tface([arch(0, 2.4, 0, 3.0, False)], [arch(0, 3.4, 0, 4.8, False, surround={"style": "romanesque", "orders": 3})]),
                        "2": tface([arch(0, 3.0, 0, 2.4, False)], [arch(0, 2.8, 0, 4.2, False)])},
              "courses": [{"y": r3(S1 - YB), "h": 0.45, "out": 0.25, "profile": "band"}, {"y": r3(S2 - YB), "h": 0.45, "out": 0.25, "profile": "band"},
                          {"y": r3(BF - YB), "h": 0.5, "out": 0.3, "profile": "band"}, {"y": r3(TT - YB - 1.2), "h": 0.7, "out": 0.45, "profile": "cornice"}],
              "_about": "the bell tower, 41 m over the terrace, in white and green courses: the porch (the bronze doors; the crypt's way under it), two stages, the belfry"})
# the blind arcades of the two stages: a screen of five arches standing proud of each face, the middle one round the window
def screens(y, k):
    sp = [arch(x, 1.25, 0.9, 4.9, False) for x in (-3.2, -1.6, 0, 1.6, 3.2)]
    wall_x(f"tower arcade front {k}", TZ1, TZ1 + 0.25, -TX - 0.25, TX + 0.25, [{"h": 7.0, "openings": sp}], y=y,
           about="the blind arcades of the tower's two stages: five arches a face, the middle one round its window" if k == 1 else None)
    wall_x(f"tower arcade back {k}", TZ0 - 0.25, TZ0, -TX - 0.25, TX + 0.25, [{"h": 7.0, "openings": sp}], y=y)
    for sx, nm in SIDES:
        wall_z(f"tower arcade {nm} {k}", *side(sx, TX, TX + 0.25), TZ0 - 0.25, TZ1 + 0.25, [{"h": 7.0, "openings": [{**o, "at": r3(TZC + o["at"])} for o in sp]}], y=y)
screens(S1 + 0.25, 1); screens(S2 + 0.25, 2)
add("tower balconies", {"type": "box", "width": 1.8, "length": 0.7, "height": 0.22,
                        "at": [[0, r3(y + 1.4), r3(TZ1 + 0.35), 0] for y in (S1, S2)] + [[0, r3(y + 1.4), r3(TZ0 - 0.35), 0] for y in (S1, S2)] +
                              [[r3(sx * (TX + 0.35)), r3(y + 1.4), TZC, Q] for y in (S1, S2) for sx in (-1, 1)],
                        "_about": "the small balconies under the middle windows"})
# the belfry's colonnettes in red granite, the bell
add("belfry columns", {"type": "column", "radius": 0.2, "height": 5.0, "sides": 12,
                       "at": [[r3(x), r3(BF + 1.2), r3(TZ1 + 0.05), 0] for x in (-3.375, -1.125, 1.125, 3.375)] + [[r3(x), r3(BF + 1.2), r3(TZ0 - 0.05), 0] for x in (-3.375, -1.125, 1.125, 3.375)] +
                             [[r3(sx * (TX + 0.05)), r3(BF + 1.2), r3(TZC + z), 0] for sx in (-1, 1) for z in (-3.375, -1.125, 1.125, 3.375)],
                       "_about": "the belfry's colonnettes of red granite and pink sandstone between its openings"})
box("belfry floor", -TX + TW, TX - TW, TZ0 + TW, TZ1 - TW, BF - 0.5, BF, flatRoof=True)
add("bourdon", {"type": "dome", "sides": 20, "radius": 1.25, "thickness": 0, "head": {"profile": "bell", "waist": 0.62, "lift": 1.0}, "at": [[0, BF + 1.6, TZC, 0]],
                "_about": "Marie-Josephine, the bourdon (8.2 t), hung in the belfry"})
box("bell beam", -2.9, 2.9, TZC - 0.3, TZC + 0.3, BF + 4.4, BF + 4.9)
# the terrace on the tower, the balustrade, the four angels
box("tower terrace", -TX, TX, TZ0, TZ1, TT - 0.6, TT, walked=True, about="the terrace on the tower, round the campanile's foot")
parapet("tower balustrade front", -TX - 0.3, TX + 0.3, TZ1 - 0.1, TZ1 + 0.3, TT, 1.1, about="the pierced balustrade round the tower's terrace")
parapet("tower balustrade back", -TX - 0.3, TX + 0.3, TZ0 - 0.3, TZ0 + 0.1, TT, 1.1)
parapet("tower balustrade east", TX - 0.1, TX + 0.3, TZ0 - 0.3, TZ1 + 0.3, TT, 1.1)
parapet("tower balustrade west", -TX - 0.3, -TX + 0.1, 21.5, TZ1 + 0.3, TT, 1.1)
box("tower balustrade west 2", -TX - 0.3, -TX + 0.1, TZ0 - 0.3, 19.7, TT, TT + 1.1)
add("angel pedestals", {"type": "box", "width": 0.9, "length": 0.9, "height": 1.1, "at": [[r3(sx * (TX - 0.35)), TT, r3(TZC + sz * (TX - 0.35)), 0] for sx in (-1, 1) for sz in (-1, 1)]})
for k, v in ST.row("tower angel", [(sx * (TX - 0.35), TT + 1.1, TZC + sz * (TX - 0.35)) for sx in (-1, 1) for sz in (-1, 1)], kind="woman", style="roman", stone="limestone",
                   wings="raised", scale=1.35, pose="aloft",
                   face=[math.atan2(-sz, sx) for sx in (-1, 1) for sz in (-1, 1)]).items(): add(k, v)
# the campanile: a round core in a ring of sixteen columns under its entablature and cap, the plinth and the Virgin on it
CB = TT
add("campanile plinth", {"type": "column", "radius": 3.0, "height": 0.8, "sides": 32, "at": [[0, CB, TZC, 0]],
                         "_about": "the campanile (12.5 m): a round core within sixteen columns, its cap, the pedestal of the statue"})
add("campanile core", {"type": "column", "radius": 1.9, "height": 7.6, "sides": 32, "at": [[0, CB + 0.8, TZC, 0]]})
add("campanile columns", {"type": "column", "radius": 0.19, "height": 6.6, "sides": 12,
                          "at": [[r3(2.6 * math.sin(k * PI / 8)), CB + 0.8, r3(TZC + 2.6 * math.cos(k * PI / 8)), 0] for k in range(16)],
                          "_about": "the campanile's sixteen columns in red granite"})
add("campanile entablature", {"type": "column", "radius": 3.05, "height": 1.0, "sides": 32, "at": [[0, CB + 7.4, TZC, 0]]})
add("campanile cap", {"type": "dome", "sides": 32, "radius": 3.05, "thickness": 0, "head": {"profile": "segmental", "rise": 1.3}, "at": [[0, CB + 8.4, TZC, 0]]})
add("statue pedestal", {"type": "column", "radius": 1.35, "height": 2.6, "sides": 24, "at": [[0, CB + 9.0, TZC, 0]], "_about": "the round pedestal of the Virgin"})
add("statue pedestal cornice", {"type": "column", "radius": 1.6, "height": 0.45, "sides": 24, "at": [[0, CB + 11.6, TZC, 0]]})
SY = CB + 12.05
for k, v in ST.madonna((0, SY, TZC), scale=6.3, stone="gold", seed=7, prefix="bonne mere").items():
    add(k, v)
parts["bonne mere"]["_about"] = "La Bonne Mere: the Virgin and Child in gilt copper by Lequesne (11.2 m, 1870) over the campanile, the Child on her left arm blessing the city"
# the stair turret against the tower's south-west face, from the terrace to the tower's terrace
TRX, TRZ = -TX - 2.25, 20.6                     # (clear of the tower's bands and the church's front wall)
add("tower stair", comp("components/round-stair-tower", {"R": 1.75, "wall": 0.3, "H": r3(TT - T), "n": 8, "steps": 201, "doorBay": 6, "stageH": 3.0,
                                                         "doorW": 1.15, "archW": 0.8},
                        [[r3(TRX), T, TRZ, 0]], build=["shaft", "shaft door", "stair", "belvedere", "belvedere door", "cornice", "interior"],
                        _about="the octagonal stair turret against the tower's south-west face: from the terrace (its door to the west) to the tower's terrace"))
box("tower stair bridge", -TX - 0.6, -TX + 0.1, TRZ - 0.6, TRZ + 0.6, TT - 0.6, TT, walked=True, about="the step from the turret's belvedere onto the tower's terrace")

# =====================================================================================================================
# THE FORT: the summit terrace round the basilica, the porch terrace, the bastion front and the drawbridge
FW, FE, FB = -17.35, 16.0, -27.3                 # the summit terrace's west and east edges, its back
ZP = 30.5                                        # the porch terrace's front, over the drawbridge's platform
for nm, spans in (("summit terrace", [(FW, -OO, FB, TZ1), (OO, FE, FB, TZ1), (-OO, OO, FB, -23.6), (-OO, -TX, ZF + 1.0, TZ1), (TX, OO, ZF + 1.0, TZ1)]),
                  ("porch terrace", [(FW, -1.6, TZ1, ZP), (1.6, FE, TZ1, ZP)])):
    boxes(nm, spans, 0, T, walked=True,
          about={"summit terrace": "the summit terrace round the basilica on the old fort's rock, walked all round the church",
                 "porch terrace": "the porch terrace before the tower, over the crypt's passage"}[nm])
# the parapets round the terrace
PH = 1.0
for nm, (x0, x1, z0, z1) in (("west", (FW, FW + 0.4, 13.0, ZP)), 
                             ("back", (FW, FE, FB, FB + 0.4)),
                             ("east", (FE - 0.4, FE, 10.4, TZ1)), ("east 2", (FE - 0.4, FE, -21.4, 8.5)), ("east 3", (FE - 0.4, FE, FB + 0.4, -23.3)),
                             ("front", (-12.4, 12.4, ZP - 0.4, ZP)), ("front west", (FW, -15.0, ZP - 0.4, ZP)), ("front east", (15.0, FE, ZP - 0.4, ZP)),
                             ("porch east", (FE - 0.4, FE, TZ1, ZP))):
    parapet(f"terrace parapet {nm}", x0, x1, z0, z1, T, PH, pierced=False, about="the parapets round the terrace" if nm == "west" else None)
# the platform before the crypt's door, the gate and the drawbridge over the ditch
ZS = 34.0                                        # the scarp's face
box("platform", -15.6, 15.6, ZP, ZS, 0, YB, walked=True, about="the drawbridge's platform at the bastion's head, before the crypt's door")
wall_x("drawbridge gate", ZS - 0.6, ZS, -2.8, 2.8, [{"h": 4.6, "openings": [arch(0, 2.6, 0, 2.6, False, surround={"style": "romanesque", "orders": 1})]}], y=YB,
       about="the gate the drawbridge drops from")
for sx, nm in SIDES:
    box(f"platform parapet {nm}", *side(sx, 2.8, 15.6), ZS - 0.4, ZS, YB, YB + 1.0)
    add(f"{nm} flight", {"type": "flight", "width": 2.5, "run": 0.3, "base": YB, "top": T, "steps": 34, "landing": 2.5,
                         "at": [[r3(sx * 2.2), 0, r3(ZP if sx < 0 else ZP + 2.5), 0 if sx > 0 else PI]],
                         **({"_about": "the two flights from the drawbridge's platform up to the porch terrace on either side, the crypt's door between them"} if sx > 0 else {})})
    add(f"{nm} bartizan", {"type": "column", "radius": 0.95, "height": 3.2, "sides": 12, "taper": 1.0, "at": [[r3(sx * 15.3), YB - 0.6, ZS - 0.1, 0]],
                           **({"_about": "the bartizans at the bastion's corners"} if sx > 0 else {})})
    add(f"{nm} bartizan corbel", {"type": "column", "radius": 0.95, "height": 1.4, "sides": 12, "taper": 0.45, "at": [[r3(sx * 15.3), YB - 2.0, ZS - 0.1, 0]]})
    add(f"{nm} bartizan cap", {"type": "dome", "sides": 12, "radius": 1.15, "thickness": 0, "head": {"profile": "trigonal", "rise": 1.8}, "at": [[r3(sx * 15.3), YB + 2.6, ZS - 0.1, 0]]})
add("drawbridge", {"type": "box", "width": 2.6, "length": 3.6, "height": 0.35, "walked": True, "at": [[0, YB - 0.35, 35.8, 0]],
                   "_about": "the drawbridge over the ditch, timber on iron"})
add("drawbridge chains", {"type": "bars", "w": 0.06, "lines": [[sx * 1.25, YB, 37.5, sx * 1.25, YB + 3.8, ZS + 0.05] for sx in (-1, 1)]})
# the stair pier in the ditch and the lift tower beside it
add("pier flight", {"type": "flight", "width": 2.6, "run": 0.38, "base": LD, "top": YB, "steps": 12, "landing": 1.6, "ground": 0, "at": [[1.3, 0, 43.6, Q]],
                    "_about": "the stair pier in the ditch: from the double staircase's landing up to the drawbridge"})
LX0, LX1, LZ0, LZ1 = 1.6, 5.6, 35.1, 41.6
add("lift tower", {"type": "enclosure", "plan": {"rect": [r3(LX1 - LX0), r3(LZ1 - LZ0)]}, "thickness": 0.35, "height": r3(YB + 3.6), "at": [[r3((LX0 + LX1) / 2), 0, r3((LZ0 + LZ1) / 2), 0]],
                   "glass": True, "tiers": [{"h": YB, "openings": [arch(0, 1.0, 2.2, 3.6)]}, {"h": 3.6, "openings": [arch(0, 1.0, 0.9, 2.2)]}],
                   "faces": {"1": [{"h": YB, "openings": [arch(0, 1.4, 0, 2.4, False)]}, {"h": 3.6, "openings": [arch(0, 1.0, 0.9, 2.2)]}],
                             "3": [{"h": YB, "openings": []}, {"h": 3.6, "openings": [arch(0, 1.3, 0, 2.2, False)]}]},
                   "courses": [{"y": r3(YB + 3.2), "h": 0.4, "out": 0.25, "profile": "cornice"}],
                   "_about": "the lift tower (1892) in the ditch: its door at the road and its door at the top onto the drawbridge's pier"})
box("lift tower roof", LX0 - 0.1, LX1 + 0.1, LZ0 - 0.1, LZ1 + 0.1, YB + 3.6, YB + 3.9, flatRoof=True)
interior("lift interior", LX0 + 0.35, LX1 - 0.35, LZ0 + 0.35, LZ1 - 0.35, 0, YB + 3.6)
add("lift", {"type": "marker", "role": "lift", "at": [[r3((LX0 + LX1) / 2 + 0.6), 0, r3((LZ0 + LZ1) / 2), 0]], "data": {"dx": -3.6, "dy": YB},
             "_about": "the lift: from the road to the drawbridge's pier (index.html: a stair's shortcut)"})
# the double staircase up from the road, its landing on the counterscarp
ZC_ = 43.6
box("stair landing", -2.2, 2.2, ZC_, 48.3, 0, LD, walked=True, about="the landing of the double staircase, on the counterscarp")
parapet("stair landing parapet", -2.2, 2.2, 47.9, 48.3, LD, 1.0, pierced=False)
for sx, nm in SIDES:
    add(f"{nm} road flight", {"type": "flight", "width": 3.0, "run": 0.45, "base": 0, "top": LD, "steps": 34, "landing": 0,
                              "at": [[r3(sx * 17.5), 0, r3(ZC_ + 3.0 if sx < 0 else ZC_), 0 if sx < 0 else PI]],
                              **({"_about": "the double staircase from the road: two flights of 34 steps meeting on the landing"} if sx > 0 else {})})
    box(f"stair landing parapet {nm}", *side(sx, 2.2, 2.6), ZC_ + 3.0, 48.3, LD, LD + 1.0)
# the lower east terrace and its two flights up to the summit
box("east terrace", FE, 27.95, -28.0, 15.5, 0, TE, walked=True, about="the lower terrace east of the basilica, on the fort's casemates")
add("east flight north", {"type": "flight", "width": 1.6, "run": 0.35, "base": TE, "top": T, "steps": 17, "landing": 1.6, "at": [[FE, 0, 2.7, -Q]],
                          "_about": "the flights from the lower east terrace up to the summit"})
add("east flight south", {"type": "flight", "width": 1.6, "run": 0.35, "base": TE, "top": T, "steps": 17, "landing": 1.6, "at": [[FE + 1.6, 0, -15.6, Q]]})
for nm, (x0, x1, z0, z1) in (("east", (27.55, 27.95, -28.0, 15.5)), ("north", (FE, 27.95, 15.1, 15.5)), ("south", (FE, 27.95, -28.0, -27.6))):
    parapet(f"east terrace parapet {nm}", x0, x1, z0, z1, TE, PH, pierced=False)

# ---- the fort's buildings round the summit: plain ranges of the old fort (barracks, casemates, the rectory, shops)
def range_(name, x0, x1, z0, z1, h, about=None, y=0, floors=3):
    W, L = x1 - x0, z1 - z0
    th = h / floors
    def face(Lf):
        n = max(1, int(Lf / 3.2))
        hs = [r3(th)] * (floors - 1) + [r3(h - r3(th) * (floors - 1))]
        return [{"h": hh, "openings": {"pattern": str(n), "width": 1.0, "gap": r3((Lf - 2.0) / n - 1.0), "sill": 1.0, "springing": r3(min(2.2, th - 0.9)), "head": ROUND}} for hh in hs]
    add(name, {"type": "enclosure", "plan": {"rect": [r3(W), r3(L)]}, "thickness": 0.6, "height": r3(h), "at": [[r3((x0 + x1) / 2), r3(y), r3((z0 + z1) / 2), 0]], "glass": True,
               "faces": {"0": face(W), "2": face(W), "1": face(L), "3": face(L)}, "courses": [{"y": r3(h - 0.5), "h": 0.5, "out": 0.25, "profile": "cornice"}],
               **({"_about": about} if about else {})})
    box(f"{name} floor", x0 + 0.6, x1 - 0.6, z0 + 0.6, z1 - 0.6, y, y + h - 0.4, flatRoof=True)
    add(f"{name} roof", {"type": "roof", "form": "hip", "width": r3(W), "length": r3(L), "pitch": 22, "overhang": 0.4, "at": [[r3((x0 + x1) / 2), r3(y + h), r3((z0 + z1) / 2), 0]]})
range_("west range", -32.9, FW, -42.6, 13.0, T + 3.5, about="the fort's ranges beside the summit: the old barracks on the west, the casemates on the east -- plain stone under tiled hipped roofs", floors=4)
range_("east casemates", 27.95, 33.95, -28.0, 15.5, TE + 3.6, floors=3)

# =====================================================================================================================
statues = ST.capped({k: parts[k] for k in parts if parts[k].get("role") == "statue"})
assert len(statues) == sum(1 for k in parts if parts[k].get("role") == "statue")
doc = {"name": "Notre-Dame de la Garde",
       "_about": "NOTRE-DAME DE LA GARDE, Marseille (Esperandieu, 1853-64), the Romanesque-Byzantine basilica on the summit fort, on its OSM plan (church, tower, dome, statue, terrace, steps, lift building, retaining walls) and Wikipedia's dimensions: the UPPER CHURCH -- a nave of three square bays under cupolas on pendentives between transverse arches, three side chapels a side (their twin windows), the crossing under the DOME on an octagonal drum (a window under a gable in every face, 32 ribs, the cross), transept fronts of two windows and a rose, the choir's barrel and the APSE's half dome over five blind arcades on red granite columns, the sacristies; the 41 m TOWER before it (the porch and the bronze doors, two stages of blind arcades, the belfry on red colonnettes with its bourdon, the terrace with balustrade and four angels, the round CAMPANILE of sixteen columns and the gilt VIRGIN AND CHILD, 11 m, on it), its octagonal stair turret; the CRYPT in the rock (barrel nave, six chapels, the altar and the Vierge au Bouquet, Mazenod and Pius IX in its narthex, the stairs up to the sacristies); the whole in courses of white Calissanne and green Golfolina stone, inside red and white marble, mosaics in gold. THE FORT: the terrace walked round the church, the porch terrace, the bastion's platform and the DRAWBRIDGE over the ditch, the two flights up from it, the stair pier and the LIFT tower, the double staircase from the road, the lower east terrace and its flights, the fort's ranges (tools/archgen/notre_dame_garde.py).",
       "params": {"detail": 4}, "railing": {"type": "balusters"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/notre-dame-garde.json"), "w").write(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

# ---- the doors ------------------------------------------------------------------------------------------------------
doors = {"name": "Notre-Dame de la Garde: doors", "building": "notre-dame-garde",
         "_about": "Notre-Dame de la Garde: Revoil's bronze doors in the tower's porch, the crypt's doors, the sacristies' doors to the terrace, the stair turret's, the lift tower's",
         "doors": [
             {"_about": "the bronze doors of the upper church, in the tower's porch (Revoil)", "part": "tower", "near": [0, TZ1], "below": S1, "style": "bronze-great", "leafH": 4.8},
             {"_about": "the crypt's door from the drawbridge's platform", "part": "crypt portal", "style": "romanesque", "leafH": 3.0},
             {"_about": "the sacristies' doors out to the terrace", "part": ["east sacristy wall", "west sacristy wall"], "style": "plain", "leafH": 2.5},
             {"_about": "the stair turret's door", "part": "tower stair/shaft door", "style": "tower"},
             {"_about": "the lift tower's door at the road", "part": "lift tower", "near": [LX1, (LZ0 + LZ1) / 2], "style": "plain", "leafH": 2.4}]}
open(os.path.join(ROOT, "assets/doors/notre-dame-garde.json"), "w").write(json.dumps(doors, indent=2, ensure_ascii=False) + "\n")

# ---- the finish -----------------------------------------------------------------------------------------------------
STRIPES = {"pattern": "stone/striped courses", "palette": "garde-stripes"}
MARBLE = {"pattern": "stone/striped marble", "palette": "garde-marble", "scale": 0.65}
PALE = {"pattern": "stone/marble", "palette": "carrara", "scale": 1.4}
STRIPED_IN = ["transverse arch 1", "transverse arch 2", "crossing front arch", "crossing back arch", "crossing west arch", "crossing east arch",
              "nave west wall", "nave east wall", "west chapel wall 1", "west chapel wall 2", "east chapel wall 1", "east chapel wall 2"]
FORT = {"pattern": "stone/ashlar", "palette": "limestone"}
FORT_PARTS = ["summit terrace", "porch terrace", "platform", "platform parapet east", "platform parapet west", "stair landing", "stair landing parapet", "stair landing parapet east",
              "stair landing parapet west", "east terrace", "kind:flight", "east bartizan", "west bartizan", "east bartizan corbel", "west bartizan corbel",
              "west range", "east casemates", "west range floor", "east casemates floor", "lift tower", "lift tower roof", "drawbridge gate", "crypt portal", "terrace parapet", "east terrace parapet"]
fin = {"name": "Notre-Dame de la Garde", "building": "architecture/notre-dame-garde",
       "_about": "Notre-Dame de la Garde: outside, the whole church and tower in courses of white Calissanne limestone and green Golfolina sandstone, the colonnettes in red granite, the low roofs in stone, the Virgin gilt; inside, the piers and arches in courses of white Carrara and red La Celle marble, the cupolas, the dome and the apse in gold mosaic (vines on gold in the apse), the lunettes blue strewn with gold, the floors in mosaic; the crypt in bare stone; the fort in pale limestone.",
       "stone": {"color": "#e6dfcf", "accent": "#66705f", "pat": "ashlar"},
       "rules": [
           {"parts": ["bonne mere", "bonne mere child", "dome cross", "dome knob"], "pattern": "roofs/gold leaf", "_about": "the gilt Virgin and the cross"},
           {"parts": ["drawbridge", "drawbridge chains", "bell beam"], "surface": "floor", "pattern": "timber/wood", "palette": "oak", "_about": "the drawbridge's deck"},
           {"parts": ["drawbridge chains", "bourdon"], "pattern": "materials/metal", "palette": "bronze", "_about": "iron and bronze"},
           {"parts": ["belfry columns", "campanile columns", "apse columns"], "pattern": "stone/marble", "palette": "granite-red", "_about": "the colonnettes in red granite"},
           {"parts": ["pews"], "pattern": "timber/wood", "palette": "oak"},
           # inside the upper church
           {"parts": ["apse dome band"], "pattern": "mosaic/gold braid", "_about": "the band of gold mosaic at the half dome's springing"},
           {"parts": ["apse half dome"], "side": "in", "pattern": "ornament/arabesque double", "palette": "garde-vine", "scale": 3.6,
            "_about": "the apse's half dome: vine scrolls on gold (the ship's medallion amid them, Mora's mosaic)"},
           {"parts": ["dome/dome"], "side": "in", "map": "revolve", "count": 4, "pattern": "mosaic/gold virgin", "_about": "the dome: figures on gold (the four angels with the crown of roses)"},
           {"parts": ["nave cupolas"], "side": "in", "pattern": "mosaic/gold ground", "scale": 1.5, "_about": "the cupolas in gold mosaic"},
           {"parts": ["nave pendentives", "crossing pendentives"], "side": "in", "pattern": "mosaic/wall roundels", "_about": "the pendentives: medallions on gold (the evangelists)"},
           {"parts": ["dome/drum", "dome/drum piers", "dome/drum a", "dome/drum b"], "side": "in", "pattern": "mosaic/gold ground", "scale": 1.5, "_about": "the drum in gold mosaic"},
           {"parts": ["high altar", "silver virgin column", "altar platform", "altar step"], "pattern": "stone/marble", "palette": "carrara", "_about": "the high altar in white marble"},
           {"surface": "floor", "side": "in", "below": T - 1.0, "pattern": "floors/flagstones", "palette": "limestone", "_about": "the crypt's floor"},
           {"surface": "floor", "side": "in", "below": T + 1.0, "pattern": "mosaic/field colour", "scale": 1.2, "_about": "the church's floors in geometric mosaic"},
           {"side": "in", "below": T - 0.3, "pattern": "stone/ashlar", "palette": "limestone", "_about": "the crypt in bare dressed stone"},
           {"parts": ["choir vault", "transept vault", "west transept vault", "east transept vault", "dome/interior"], "side": "in", "pattern": "mosaic/gold ground", "scale": 1.5,
            "_about": "the choir's and the transepts' barrels in gold mosaic"},
           {"surface": "ceiling", "side": "in", "above": T + 0.5, **MARBLE, "_about": "the arches' soffits in red and white courses"},
           {"surface": "wall", "side": "in", "above": T + SPR + 0.05, "within": [-NI - 0.05, X0 - 0.2, NI + 0.05, ZF], "pattern": "painted/starry vault",
            "_about": "the lunettes over the nave's arcades: blue strewn with gold"},
           {"surface": "wall", "side": "in", "above": T + SPR + 0.05, "below": T + UP + 1.0, "pattern": "mosaic/gold ground", "scale": 1.5,
            "_about": "over the impost: the spandrels and the upper walls in gold mosaic"},
           {"parts": ["apse wall"], "side": "in", "pattern": "mosaic/gold ground", "scale": 1.5, "_about": "the apse's blind arcades lined with gold mosaic"},
           {"parts": STRIPED_IN, "side": "in", "above": T - 0.3, **MARBLE, "_about": "the piers and the arches up to the impost in courses of white Carrara and red La Celle marble"},
           {"surface": "wall", "side": "in", "above": T - 0.3, "below": T + 1.1, **MARBLE, "_about": "the dado: a band of red and white courses round the walls"},
           {"side": "in", "above": T - 0.3, **PALE, "_about": "the walls between: calm white marble"},
           {"side": "in", **MARBLE},
           # outside
           {"parts": ["dome/ribs"], "pattern": "stone/ashlar fine", "palette": "limestone", "_about": "the dome's ribs in white stone"},
           {"parts": ["dome/dome", "campanile cap", "apse roof"], **STRIPES, "_about": "the dome in courses of white and green"},
           {"parts": ["west range roof", "east casemates roof"], "pattern": "roofs/coppi", "palette": "tile-red", "_about": "the fort's roofs in Provencal tile"},
           {"parts": ["nave roof", "transept roofs", "choir roof", "drum base", "east sacristy roof", "west sacristy roof"], "surface": ["roof", "floor"], "pattern": "stone/ashlar fine", "palette": "limestone",
            "_about": "the low roofs in stone slabs"},
           {"parts": FORT_PARTS, "surface": "floor", "pattern": "floors/flagstones", "palette": "limestone", "_about": "the terraces paved"},
           {"parts": FORT_PARTS, **FORT, "_about": "the fort in pale limestone"},
           {"parts": ["kind:roof"], "pattern": "roofs/coppi", "palette": "tile-red"},
           {"surface": "floor", "pattern": "floors/flagstones", "palette": "limestone"},
           {"parts": ["kind:moulding", "kind:railing"], "pattern": "stone/ashlar fine", "palette": "limestone", "_about": "cornices, surrounds and balustrades in white stone"},
           {**STRIPES, "_about": "white Calissanne and green Golfolina in courses"}]}
open(os.path.join(ROOT, "assets/finishes/notre-dame-garde.json"), "w").write(json.dumps(fin, indent=2, ensure_ascii=False) + "\n")
print("notre-dame-garde:", len(parts), "parts,", len(statues), "statues")
