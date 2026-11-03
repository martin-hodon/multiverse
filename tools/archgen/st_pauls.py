# ST PAUL'S CATHEDRAL, London (Sir Christopher Wren, 1675-1710), rebuilt 2026-11-03 from its real plan.
#
# SOURCES. The footprint is OpenStreetMap way 369161987 ("St Paul's Cathedral", Overpass API), turned 5 degrees onto the
# church's own axis: the body 37.6m across its outer walls, the four corner blocks round the crossing 51m square, the
# transept fronts 74.8m apart, the choir's end 63m east of the dome's centre and the apse past it, the west block with its
# chapels and towers 57m across, the portico's front 86m west of it (158m with the steps). The inside is read off Remi
# Parr's engraved plan (Yale Center for British Art B1977.14.16224, Wikimedia Commons) and Wren's plan and section: the
# nave 12.6m clear between its piers, three bays of 10.8m in nave and choir, each under a SAUCER DOME on pendentives
# between transverse arches; the aisles under smaller saucer domes; the west bay with its chapels (St Dunstan's,
# St Michael and St George's) and the towers' halls; the crossing an octagon of eight piers carrying the dome -- four
# great arches the nave's width into the arms, four smaller ones on the diagonals into the aisles. Heights from the
# Wikipedia figures: the Whispering Gallery 30m over the floor and 34m across, the Stone Gallery at 53m, the Golden
# Gallery round the lantern's foot at 85m, the cross at 111m; the walls two storeys of paired pilasters (Corinthian, and
# Composite over: here Corinthian twice) over a basement, the upper storey a SCREEN hiding the aisle roofs and the
# flying buttresses behind it.
#
# The model: the outer walls as one `enclosure` on the OSM outline (basement windows to the crypt, round-headed windows
# with keystones below, pedimented ones above, an order on each storey), the balustrade along their heads; nave, choir
# and transept arcades (`wall` tiers: the arcade, the clerestory lunettes), transverse arches, `pendentives` and saucer
# `dome`s; the crossing's octagon (`enclosure`) with its eight arches; the WHISPERING GALLERY on its head and the inner
# drum of 32 bays (windows in threes between niches) under the INNER DOME with its oculus; outside, the podium, the
# PERISTYLE of 32 columns (every fourth bay filled), the STONE GALLERY on its entablature, the attic, the lead outer dome
# with its ribs, the Golden Gallery and the lantern (`domed-tower`) with the gilt ball and cross; the west front's
# two-storey portico of paired columns under its pediment and the two baroque towers (the clock in the south-west one),
# the half-round porticoes before the transepts; the crypt under the whole church (Nelson's tomb under the dome).
# THE VISITORS' WAY UP: a spiral in the south-west corner block from the floor to the flat roofs round the dome; from
# there a door through the podium into a shaft in the drum's wall -- a door on into the Whispering Gallery, and a spiral
# up the shaft to a door onto the Stone Gallery. The Geometric Staircase in the south-west tower climbs to the upper
# loggia of the west portico; a stair down from the south transept to the crypt.
#   Frame: the dome's centre at the origin, the west front facing +z (north is -x), the church's floor F over the
# crypt's; numbers worked here and written as numbers.
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from neoclassical import Balusters
from statuary import statue, FACE_PZ, capped

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n); return n
r4 = lambda v: round(v, 4)
Q = math.pi / 2
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
SEMI = {"profile": "semicircular"}
FLAT = {"profile": "flat"}

# ---- the plan's numbers (m) -----------------------------------------------------------------------------------------
F = 4.0                    # the church's floor (the crypt's floor at 0, its vaults' slab under F)
SLAB = 0.5
L1 = 19.5                  # the storey line outside (the lower order's entablature); the upper storey to the walls' head
WT = 34.0                  # the walls' head (the balustrade over it)
BX, TW = 18.8, 2.2         # the body's outer face (nave, choir, transept arms) and the outer walls' thickness
BI = BX - TW               # their inner face: 16.6
CB = 25.5                  # the corner blocks round the crossing
TX = 37.4                  # the transept fronts
CHE = 63.0                 # the choir's east end (outer face)
WZ0, WX = 54.0, 28.5       # the west block: its chapels and towers
TWZ, VZ, PX = 84.0, 79.5, 14.0   # the towers' west faces, the vestibule's west wall, the portico's half width
AX, AT = 7.9, 3.2          # the arcades: their middle line and thickness (the nave 12.6 clear: 6.3 to 9.5)
AI, AO = AX - AT / 2, AX + AT / 2
AW = BI - AO               # an aisle's width, 7.1
SN = F + 19.0              # the nave's transverse arches and pendentives spring here (23.0)
SA = F + 10.5              # the aisles' (14.5)
ARCH_SPR = 10.0            # the arcade's arches spring 10m over the floor (crown 13.8)
# the pier lines (transverse arches' middles) and their thickness, nave (+z) / choir (-z); the bays between
NAVE_PL = [(20.85, 4.7), (32.4, 3.2), (43.2, 3.2), (54.0, 3.2), (66.0, 3.2)]
NAVE_BAYS = [27.0, 37.8, 48.6, 60.0]
CHOIR_PL = [(-20.85, 4.7), (-32.4, 3.2), (-43.2, 3.2), (-54.0, 3.2), (-58.2, 5.2)]
CHOIR_BAYS = [-27.0, -37.8, -48.6]
TR_PL = [(20.85, 4.7)]
TR_BAY = 29.2              # the transept's one bay (to its end wall's inner face at 35.2)

# ---- helpers ---------------------------------------------------------------------------------------------------------
def wall_at(a, b, t, y):
    """a wall's placement for its middle line a -> b (x, z): local x along it, its thickness centred on the line"""
    L = math.dist(a, b); dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    yaw = math.atan2(-dz, dx)
    mx, mz = (a[0] + b[0]) / 2 + t / 2 * math.sin(yaw), (a[1] + b[1]) / 2 + t / 2 * math.cos(yaw)
    return L, [r4(mx), r4(y), r4(mz), r4(yaw)]

def along(a, b, q):
    """an opening's `at` on the wall a -> b for the point q on its line: from the middle, along a -> b"""
    L = math.dist(a, b); dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    return r4((q[0] - (a[0] + b[0]) / 2) * dx + (q[1] - (a[1] + b[1]) / 2) * dz)

def win(at, w, sill, spr, head=SEMI, **kw):
    return {"at": r4(at), "width": w, "sill": sill, "springing": spr, "head": head, **kw}

def door(at, w=1.3, h=2.6):
    return {"at": r4(at), "width": w, "sill": 0, "springing": r4(h - w / 2), "head": SEMI, "glass": False}

def iwall(name, a, b, t, y0, h, tiers, about=None, **kw):
    """a wall inside on the middle line a -> b, `tiers` its openings ([{h, openings}]), one or more placements"""
    L, at = wall_at(a, b, t, y0)
    d = {"type": "wall", "width": r4(L), "height": r4(h), "thickness": t, "tiers": tiers, "at": [at], **kw}
    if about: d["_about"] = about
    return add(name, d)

def turned(p, yaw):
    """a plan point (x, z) turned by yaw as the engine turns a placement"""
    c, s = math.cos(yaw), math.sin(yaw)
    return (r4(p[0] * c + p[1] * s), r4(-p[0] * s + p[1] * c))

QUADS = [0.0, Q, math.pi, -Q]          # the crossing's four quarters: +x+z (south-west), +x-z, -x-z, -x+z

# =====================================================================================================================
# THE OUTER WALLS: one enclosure on the outline from OpenStreetMap (outer faces), clockwise from the north-west tower's front
# =====================================================================================================================
OUT = [(-WX, TWZ), (-PX, TWZ), (-PX, VZ), (PX, VZ), (PX, TWZ), (WX, TWZ),          # 0-5   the west front
       (WX, WZ0), (BX, WZ0), (BX, CB), (CB, CB), (CB, BX), (TX, BX),               # 6-11  south: chapel, nave, SW block, transept
       (TX, -BX), (CB, -BX), (CB, -CB), (BX, -CB), (BX, -CHE),                     # 12-16 south transept's front, SE block, choir
       (-BX, -CHE), (-BX, -CB), (-CB, -CB), (-CB, -BX), (-TX, -BX),                # 17-21 the choir's end, the north side
       (-TX, BX), (-CB, BX), (-CB, CB), (-BX, CB), (-BX, WZ0), (-WX, WZ0)]         # 22-27
NF = len(OUT)
T0, T1 = F, L1 - F                     # the basement storey, the lower storey (the upper: the rest, to WT)
BASE_WIN = lambda at: win(at, 1.4, 1.0, 2.5, FLAT)
LOW_WIN = lambda at, w=2.6: win(at, w, 3.2, 10.0, surround={"keystone": True, "sill": True})
UP_WIN = lambda at, w=2.3: win(at, w, 2.6, 9.6, FLAT, surround={"head": "alternate", "sill": True})

def face_points(i):
    """where face i's windows stand (world points on its line), and its doors (lower storey), by what lies behind it"""
    a, b = OUT[i], OUT[(i + 1) % NF]
    xs = lambda zs, x: [(x, z) for z in zs]
    if i in (7, 25): return xs([28.2, 37.8, 48.6], a[0]), []                          # the nave's aisles
    if i in (15, 17): return xs([-28.2, -37.8, -48.6, -58.2], a[0]), []              # the choir's
    if i in (10, 12, 20, 22): return [(math.copysign(TR_BAY, a[0] + b[0]), a[1])], []           # the transepts' flanks
    if i in (8, 9, 13, 14, 18, 19, 23, 24): return [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)], []   # the corner blocks
    if i in (6, 26): return [((a[0] + b[0]) / 2, a[1])], []                           # the chapels' east faces
    if i in (5, 27): return xs([60.0, 72.0, 79.0], a[0]), []                          # the chapels', the towers' flanks
    if i in (0, 4): return [(math.copysign(21.25, a[0] + b[0]), a[1])], []            # the towers' fronts
    if i in (11, 21): return xs([-13.05, 13.05], a[0]), [(a[0], 0.0)]                 # the transept fronts: their doors
    return [], []

def face_tiers(i):
    a, b = OUT[i], OUT[(i + 1) % NF]
    if i == 16:                                    # the choir's end: the apse's arch the vessel's width, windows to the aisles
        return [{"h": T0, "openings": [BASE_WIN(along(a, b, (x, a[1]))) for x in (-13.05, 13.05)]},
                {"openings": [win(0, 12.6, 0, 19.0, glass=False)] + [LOW_WIN(along(a, b, (x, a[1]))) for x in (-13.05, 13.05)]}]
    if i == 2:                                     # the vestibule's west wall behind the portico: the great door and two
        return [{"h": T0, "openings": []},         #   lesser ones, a window from the upper loggia
                {"h": T1, "openings": [win(0, 4.4, 0, 8.5, glass=False), win(-8.4, 2.4, 0, 5.0, glass=False), win(8.4, 2.4, 0, 5.0, glass=False)]},
                {"openings": [win(0, 3.2, 1.6, 9.0), win(-8.4, 2.2, 2.6, 8.4), win(8.4, 2.2, 2.6, 8.4)]}]
    if i in (1, 3):                                # the portico's ends: the south one a door from the tower's upper floor
        return [{"h": T0, "openings": []}, {"h": T1, "openings": []},
                {"openings": [door(-1.2, 1.4, 2.8)] if i == 3 else []}]
    pts, doors = face_points(i)
    ats = [along(a, b, q) for q in pts]
    lower = [LOW_WIN(u) for u in ats]
    if doors:
        lower = [win(along(a, b, q), 3.6, 0, 7.4, glass=False) for q in doors] + lower
    upper = [UP_WIN(u) for u in ats] + ([UP_WIN(along(a, b, q), 2.6) for q in doors] if doors else [])
    return [{"h": T0, "openings": [BASE_WIN(u) for u in ats]}, {"h": T1, "openings": lower}, {"openings": upper}]

add("outer walls", {"type": "enclosure", "plan": {"points": [list(p) for p in OUT]}, "thickness": TW, "height": WT,
                    "faces": {str(i): face_tiers(i) for i in range(NF)},
                    "orders": [{"tier": 1, "kind": "corinthian"}, {"tier": 2, "kind": "corinthian"}], "courses": {"skip": []},
                    "at": [[0, 0, 0, 0]],
                    "_about": "the outer walls on the OSM outline: a basement storey with the crypt's windows, the lower storey's round-headed windows with keystones, the upper storey -- a screen hiding the aisle roofs -- its windows pedimented by turns; an order of paired pilasters on each storey"})

# the floor over the crypt: the outline's slab (its edge in the walls), a well for the stair down in the south transept
CRYPT_STAIR = (29.2, -13.05)
add("church floor", {"type": "prism", "plan": {"points": [list(p) for p in OUT], "well": {"rect": [5.7, 2.6], "at": [r4(CRYPT_STAIR[0] + 0.15), r4(CRYPT_STAIR[1] + 0.65)]}},
                     "height": SLAB, "at": [[0, F - SLAB, 0, 0]],
                     "_about": "the church's floor, the slab over the crypt's vaults (the black and white marble's), the stair down to the crypt coming up through it in the south transept"})

# =====================================================================================================================
# THE ARMS INSIDE: arcades, transverse arches, pendentives and saucer domes
# =====================================================================================================================
ARC = lambda at: win(at, 7.6, 0, ARCH_SPR, glass=False)
CLER = lambda at: win(at, 3.0, 1.0, 4.0)
# the nave's two arcades (x = -+AX) from the crossing to the west diaphragm; the choir's to its east wall
for nm, z0, z1, bays in (("nave", 17.0, 67.6, NAVE_BAYS), ("choir", -17.0, -61.0, CHOIR_BAYS)):
    for sx, side in ((1, "south"), (-1, "north")):
        a, b = (sx * AX, z0), (sx * AX, z1)
        iwall(f"{nm} arcade {side}", a, b, AT, F, WT - F,
              [{"h": SN - F, "openings": [ARC(along(a, b, (a[0], z))) for z in bays]},
               {"openings": [CLER(along(a, b, (a[0], z))) for z in bays]}],
              about=f"the {nm}'s arcade: its piers 3.2m square, an arch into the aisle in every bay, over the main entablature the clerestory's window in the lunette under the saucer dome" if sx > 0 else None)
for sx, side in ((1, "south"), (-1, "north")):
    for sz, half in ((1, "west"), (-1, "east")):
        a, b = (sx * 17.0, sz * AX), (sx * 35.6, sz * AX)
        iwall(f"{side} transept arcade {half}", a, b, AT, F, WT - F,
              [{"h": SN - F, "openings": [ARC(along(a, b, (sx * TR_BAY, a[1])))]}, {"openings": [CLER(along(a, b, (sx * TR_BAY, a[1])))]}],
              about="the transepts' arcades, one bay to the end wall" if (sx, sz) == (1, 1) else None)

# the transverse arches across the vessels: diaphragms the vessel's width plus the arcade walls, open in a round arch
# springing with the pendentives (their crown at the pendentives' foot circle), standing up into the roof space
DIA_H = 28.0                               # (to 32m: over the pendentives' crown and the saucer domes' rims)
def diaphragms(name, rows, about):
    for t, ats in rows.items():
        add(f"{name} {t}", {"type": "wall", "width": 2 * AO - 0.2, "height": DIA_H, "thickness": t,
                            "tiers": [{"openings": [win(0, 12.6, 0, SN - F, glass=False)]}], "at": ats,
                            **({"_about": about} if about else {})})
        about = None
rows = {}
for z, t in NAVE_PL + CHOIR_PL:
    rows.setdefault(t, []).append([0, F, r4(z + t / 2), 0])
for x, t in TR_PL:                         # (across the transepts: on the pier line's middle, running along z)
    for sx in (1, -1): rows.setdefault(t, []).append(wall_at((sx * x, -AO + 0.1), (sx * x, AO - 0.1), t, F)[1])
diaphragms("transverse arch", rows, "the transverse arches across the nave, choir and transepts, on the piers' lines")

# the saucer domes on pendentives, a square of the vessel's width centred in each bay (its corners buried in the arches)
VB = [[0, SN, z, 0] for z in NAVE_BAYS + CHOIR_BAYS] + [[sx * TR_BAY, SN, 0, 0] for sx in (1, -1)]
add("vessel pendentives", {"type": "pendentives", "span": 12.6, "springing": 0, "sides": 16, "at": VB,
                           "_about": "the pendentives in every bay of nave, choir and transepts, carrying..."})
add("vessel saucer domes", {"type": "dome", "radius": 6.6, "thickness": 0.3, "head": {"profile": "segmental", "rise": 2.3}, "sides": 16,
                            "at": [[a[0], SN + 6.3, a[2], 0] for a in VB], "_about": "...the saucer domes (in the choir, Richmond's mosaics)"})
add("west bay pendentives", {"type": "pendentives", "span": 12.6, "springing": 0, "sides": 16, "at": [[0, SN, 60.0, 0]]})
add("west bay saucer dome", {"type": "dome", "radius": 6.6, "thickness": 0.3, "head": {"profile": "segmental", "rise": 2.3}, "sides": 16,
                             "at": [[0, SN + 6.3, 60.0, 0]], "_about": "the west bay's dome, between the chapels"})

# THE AISLES: transverse arches across them on the piers' lines, pendentives and small saucer domes, a lead flat over
AB = []                                    # every aisle bay's centre (x, z)
for zc in NAVE_BAYS[:3] + CHOIR_BAYS:
    for sx in (1, -1): AB.append((sx * (AO + AW / 2), zc))
for sx in (1, -1):
    for sz in (1, -1): AB.append((sx * TR_BAY, sz * (AO + AW / 2)))
add("aisle pendentives", {"type": "pendentives", "span": 7.6, "springing": 0, "sides": 12, "at": [[r4(x), SA, r4(z), 0] for x, z in AB],
                          "_about": "the aisles' bays: pendentives and a small saucer dome in each"})
add("aisle saucer domes", {"type": "dome", "radius": 4.0, "thickness": 0.2, "head": {"profile": "segmental", "rise": 0.9}, "sides": 12,
                           "at": [[r4(x), SA + 3.8, r4(z), 0] for x, z in AB]})
ats = []
for z, t in NAVE_PL[:4] + CHOIR_PL[:4]:
    for sx in (1, -1):
        ats.append(wall_at((sx * (AO - 0.3), z), (sx * (BI + 0.3), z), t, F)[1] + [t])
for sx in (1, -1):
    for sz in (1, -1):
        ats.append(wall_at((TR_PL[0][0] * sx, sz * (AO - 0.3)), (TR_PL[0][0] * sx, sz * (BI + 0.3)), 4.7, F)[1] + [4.7])
for t in sorted({a[4] for a in ats}):
    # (the ones on the crossing's piers' line stand from 3m up: the doors into the corner blocks open under them, against
    #  the outer wall, where the arch's jamb would shut them)
    lift = 3.0 if t > 4 else 0.0
    add(f"aisle arch {t}", {"type": "wall", "width": r4(AW + 0.6), "height": r4(SA + 4.6 - F - lift), "thickness": t,
                            "tiers": [{"openings": [win(0, AW, 0, r4(SA - F - lift), glass=False)]}],
                            "at": [[a[0], r4(a[1] + lift), a[2], a[3]] for a in ats if a[4] == t],
                            **({"_about": "the aisles' transverse arches"} if t == 3.2 else {})})
# the east bay of the choir aisles (short, to the east wall) and the west bay's chapels: flat ceilings
# THE CROSSING'S CORNERS: where an aisle of the nave or choir meets a transept's, between the octagon's diagonal face and
# the corner block -- a flat ceiling over each (the four turned copies of one plan)
JUNC = [(9.3, 18.7), (16.8, 18.7), (16.8, 16.8), (18.7, 16.8), (18.7, 9.3), (17.2, 9.3), (9.3, 17.2)]
add("junction ceilings", {"type": "prism", "plan": {"points": [list(p) for p in JUNC]}, "height": 0.5, "flatRoof": True,
                          "at": [[0, F + 14.0, 0, r4(y)] for y in QUADS],
                          "_about": "the ceilings where the aisles meet round the crossing, by the diagonal arches into it"})
add("aisle end ceilings", {"type": "prism", "plan": {"rect": [AW + 0.4, 5.6]}, "height": 0.5, "flatRoof": True,
                           "at": [[r4(sx * (AO + AW / 2)), F + 14.0, -58.2, 0] for sx in (1, -1)]})
# the aisles' lead flats, behind the screen walls: one slab along each aisle of nave, choir and transepts
for nm, w, l, x, z in (("nave aisle roofs", AW + 0.4, WZ0 - 18.7, AO + AW / 2, (WZ0 + 18.7) / 2),
                       ("choir aisle roofs", AW + 0.4, CHE - 2.2 - 18.7, AO + AW / 2, -(CHE - 2.2 + 18.7) / 2)):
    add(nm, {"type": "prism", "plan": {"rect": [r4(w), r4(l)]}, "height": 0.4, "flatRoof": True,
             "at": [[r4(sx * x), 19.6, r4(z), 0] for sx in (1, -1)], **({"_about": "the aisles' lead flats behind the screen walls"} if nm[0] == "n" else {})})
add("transept aisle roofs", {"type": "prism", "plan": {"rect": [r4(TX - 2.2 - 18.7), r4(AW + 0.4)]}, "height": 0.4, "flatRoof": True,
                             "at": [[r4(sx * (TX - 2.2 + 18.7) / 2), 19.6, r4(sz * (AO + AW / 2)), 0] for sx in (1, -1) for sz in (1, -1)]})
# THE FLYING BUTTRESSES hidden behind the screen: from the screen's head across the aisle roof to the clerestory
FLY = [z for z, _ in NAVE_PL[1:4] + CHOIR_PL[1:4]]
add("flying buttresses", {"type": "flyer", "span": r4(AW), "low": 4.0, "high": 8.5, "top0": 9.5, "top1": 12.5, "width": 1.0,
                          "at": [[r4(sx * BI), 21.0, r4(z), 0 if sx < 0 else math.pi] for z in FLY for sx in (1, -1)],
                          "_about": "Wren's flying buttresses: out of sight behind the screen walls, from their head over the aisle roofs to the clerestory"})

# =====================================================================================================================
# THE CROSSING: the octagon of eight piers, its arches, the corner blocks round it
# =====================================================================================================================
OA = 19.0                                   # the octagon's outer apothem (its inner 15.5)
oct_pts = []
for k in range(8):                          # corners at 22.5 + 45k degrees from +z toward +x, walked clockwise (as OUT)
    ang = math.radians(-22.5 + 45 * k)
    rc = OA / math.cos(math.radians(22.5))
    oct_pts.append([r4(rc * math.sin(ang)), r4(rc * math.cos(ang))])
OCT_IN = OA - 3.5
card = [{"h": F, "openings": [win(0, 3.0, 0, 2.0, glass=False)]}, {"openings": [win(0, 12.6, 0, SN - F, glass=False)]}]
diag = [{"h": F, "openings": [win(0, 3.0, 0, 2.0, glass=False)]}, {"openings": [win(0, 5.4, 0, 8.0, glass=False)]}]
add("crossing", {"type": "enclosure", "plan": {"points": oct_pts}, "thickness": OA - OCT_IN, "height": WT,
                 "faces": {str(k): (card if k % 2 == 0 else diag) for k in range(8)}, "at": [[0, 0, 0, 0]],
                 "_about": "the crossing: an octagon of eight piers -- the four great arches the nave's width into the arms, four lesser ones on the diagonals into the aisles' corners; under it the crypt's arches"})
# the corner blocks: walls between the aisles' corners and the rooms in the blocks (the south-west one the dome stair's)
for k, yaw in enumerate(QUADS):
    A1, B1 = turned((BI + TW / 2, BI), yaw), turned((BI + TW / 2, CB), yaw)
    A2, B2 = turned((BI, BI + TW / 2), yaw), turned((CB, BI + TW / 2), yaw)
    nm = ["south-west", "south-east", "north-east", "north-west"][k]
    iwall(f"{nm} block wall a", A1, B1, TW, F, WT - F, [{"openings": [door(along(A1, B1, turned((BI + TW / 2, BX + 0.85), yaw)), 1.3, 2.7)]}],
          about="the corner blocks' walls toward the aisles, a door from the aisle into each block's room" if k == 0 else None)
    iwall(f"{nm} block wall b", A2, B2, TW, F, WT - F, [{"openings": []}])
add("corner room ceilings", {"type": "prism", "plan": {"rect": [CB - BX + 0.4, CB - BX + 0.4]}, "height": 0.5, "flatRoof": True,
                             "at": [[*turned(((BX + CB - TW) / 2, (BX + CB - TW) / 2), y)[:1], F + 10.0, turned(((BX + CB - TW) / 2, (BX + CB - TW) / 2), y)[1], 0] for y in QUADS[1:]],
                             "_about": "the vestries in the other three blocks, a ceiling over each"})

# THE DOME STAIR in the south-west block: a spiral from the floor to the flat roofs round the drum (the visitors' way
# up to the galleries -- 259 steps to the Whispering Gallery in the real one)
SWX = SWZ = 21.25                           # the room's middle (clear BX..CB-TW = 18.8..23.3)
SW_R = 1.75
add("dome stair", {"type": "spiral-stair", "radius": SW_R, "newel": 0.3, "turn": 14, "top": WT - F, "rise": 0.19, "soffit": 0.25,
                   "landing": 1.6, "at": [[r4(SWX + 0.3), F, r4(SWZ + 0.3), r4(math.radians(-112))]],
                   "_about": "the dome stair: a spiral in the south-west corner block from the church's floor to the flat roofs round the drum"})

# =====================================================================================================================
# THE FLAT ROOFS round the drum, the arms' roofs, the balustrades
# =====================================================================================================================
add("crossing roof", {"type": "prism", "walked": True,
                      "plan": {"points": [[-CB, CB], [BI, CB], [BI, BI], [CB, BI], [CB, -CB], [-CB, -CB]], "well": {"radius": 17.2, "sides": 32}},
                      "height": 0.4, "at": [[0, WT - 0.4, 0, 0]],
                      "_about": "the lead flats over the crossing's corner blocks, walked round the drum's podium"})
add("dome stair head", {"type": "prism", "walked": True,
                        "plan": {"rect": [CB - BI, CB - BI], "well": {"radius": SW_R + 0.12, "sides": 24, "at": [r4(SWX + 0.3 - (BI + CB) / 2), r4(SWZ + 0.3 - (BI + CB) / 2)]}},
                        "height": 0.4, "at": [[r4((BI + CB) / 2), WT - 0.4, r4((BI + CB) / 2), 0]],
                        "_about": "the flat over the south-west block, the dome stair coming up through it"})
add("nave roof", {"type": "roof", "form": "gable", "width": 2 * AO, "length": VZ - CB, "pitch": 24, "overhang": 0.2,
                  "at": [[0, WT, r4((VZ + CB) / 2), 0]], "_about": "the lead roofs over the vessels behind the balustrades"})
add("choir roof", {"type": "roof", "form": "gable", "width": 2 * AO, "length": CHE - CB, "pitch": 24, "overhang": 0.2,
                   "at": [[0, WT, r4(-(CHE + CB) / 2), 0]]})
add("transept roofs", {"type": "roof", "form": "gable", "width": 2 * BX, "length": TX - CB, "pitch": 17, "overhang": 0.3,
                       "rake": True, "at": [[r4(sx * (TX + CB) / 2), WT, 0, Q] for sx in (1, -1)],
                       "_about": "the transepts' roofs, their gables the pediments of the transept fronts"})
add("west flats", {"type": "prism", "plan": {"rect": [WX - AO, TWZ - WZ0]}, "height": 0.4, "flatRoof": True,
                   "at": [[r4(sx * (WX + AO) / 2), WT - 0.4, r4((TWZ + WZ0) / 2), 0] for sx in (1, -1)],
                   "_about": "the flats over the west chapels and the towers' halls"})

# =====================================================================================================================
# THE DOME: the Whispering Gallery, the inner drum and dome; outside the podium, the peristyle, the Stone Gallery, the
# attic, the outer dome and the lantern
# =====================================================================================================================
G1, DT, PT, ATT, ODS = WT, 53.0, 37.0, 64.0, 64.0
DR0, DR1 = 16.0, 19.0                       # the drum's inner and outer faces
N = 32
NICHE = [k for k in range(N) if k % 4 == 2]                 # over the piers (22.5 + 45k): the eight niches
SHAFT = [3, 4, 5]                                            # the stair shaft in the drum's wall on the south-west diagonal
WINB = [k for k in range(N) if k not in NICHE and k not in SHAFT]
add("whispering gallery", {"type": "ring", "count": N, "rOuter": 17.2, "rInner": 14.3, "height": 0.45, "y": G1 - 0.45, "solid": True,
                           "walked": True, "place": [[0, 0, 0, 0]],
                           "_about": "the Whispering Gallery: the walk round the drum's foot over the crossing, 30m over the floor and 34m across"})
add("inner drum", {"type": "ring", "count": N, "rOuter": DR1, "rInner": DR0, "height": DT - G1, "y": G1, "at": WINB,
                   "opening": {"width": 1.7, "sill": 4.2, "springing": 11.5, "head": SEMI}, "place": [[0, 0, 0, 0]],
                   "_about": "the drum: windows in threes between the eight niches over the piers..."})
add("inner drum piers", {"type": "ring", "count": N, "rOuter": DR1, "rInner": DR0, "height": DT - G1, "y": G1, "at": NICHE, "solid": True,
                         "place": [[0, 0, 0, 0]], "_about": "...the niches' bays"})
add("inner dome", {"type": "dome", "radius": 16.8, "thickness": 0.8, "head": {"profile": "segmental", "rise": 12.0}, "oculus": 3.0,
                   "at": [[0, DT, 0, 0]], "_about": "the inner dome, Thornhill's grisaille, open at its crown to the light of the lantern"})
# outside: the podium over the flats, the peristyle and its deck -- the Stone Gallery -- the attic
SH1 = 19.45                                 # the shaft's outer face: it stands out of the drum's (19.0) behind the peristyle
add("podium", {"type": "ring", "count": N, "rOuter": 23.3, "rInner": DR1 - 0.1, "height": PT - G1, "y": G1, "solid": True, "flatRoof": True,
               "skip": SHAFT, "place": [[0, 0, 0, 0]], "_about": "the podium the peristyle stands on, over the flats"})
add("podium shaft", {"type": "ring", "count": N, "rOuter": 23.3, "rInner": SH1, "height": PT - G1, "y": G1, "solid": True, "flatRoof": True,
                     "at": [3, 4], "place": [[0, 0, 0, 0]]})
add("podium door", {"type": "ring", "count": N, "rOuter": 23.3, "rInner": SH1, "height": PT - G1, "y": G1, "at": [5],
                    "opening": {"width": 1.5, "sill": 0, "springing": 2.0, "head": SEMI}, "glass": False, "place": [[0, 0, 0, 0]],
                    "_about": "the way in from the flats: through the podium to the stair shaft in the drum's wall"})
add("peristyle", {"type": "colonnade", "plan": "round", "count": N, "radius": 21.3, "order": "corinthian", "columnR": 0.72,
                  "height": DT - 2.4 - PT, "taper": 0.86, "at": [[0, PT, 0, 0]],
                  "_about": "the PERISTYLE: 32 Corinthian columns round the drum"})
add("peristyle fill", {"type": "ring", "count": N, "rOuter": 21.0, "rInner": DR1 - 0.1, "height": DT - 2.4 - PT, "y": PT, "turn": 0.5,
                       "at": [k for k in range(2, N, 4)], "opening": {"width": 1.4, "sill": 3.0, "springing": 8.5, "head": SEMI}, "glass": False,
                       "place": [[0, 0, 0, 0]], "_about": "every fourth bay of the peristyle filled, a niche in each: Wren's buttresses for the dome"})
add("stone gallery", {"type": "ring", "count": N, "rOuter": 22.4, "rInner": DR1 - 0.4, "height": 2.4, "y": DT - 2.4, "solid": True,
                      "walked": True, "skip": SHAFT, "place": [[0, 0, 0, 0]],
                      "_about": "the peristyle's entablature, its top the STONE GALLERY round the attic's foot (53m)"})
add("stone gallery shaft", {"type": "ring", "count": N, "rOuter": 22.4, "rInner": SH1, "height": 2.4, "y": DT - 2.4, "solid": True,
                            "walked": True, "at": SHAFT, "place": [[0, 0, 0, 0]]})
add("attic", {"type": "ring", "count": N, "rOuter": 19.3, "rInner": 17.0, "height": ATT - DT, "y": DT, "skip": SHAFT, "every": 2, "only": "every",
              "opening": {"width": 1.2, "sill": 3.6, "springing": 7.0, "head": FLAT}, "place": [[0, 0, 0, 0]],
              "_about": "the attic over the Stone Gallery, a window every other bay..."})
add("attic piers", {"type": "ring", "count": N, "rOuter": 19.3, "rInner": 17.0, "height": ATT - DT, "y": DT, "skip": SHAFT, "every": 2,
                    "solid": True, "place": [[0, 0, 0, 0]], "_about": "...and between them"})
# the shaft in the drum's wall: two skins (the inner with the door to the Whispering Gallery, the outer with the door from
# the podium's passage), the ends on the bays' radial planes, the spiral up it to a floor at the Stone Gallery's level and
# the door out onto it
def skin(nm, r0, r1, y, h, door_=False, about=None):
    add(nm, {"type": "ring", "count": N, "rOuter": r1, "rInner": r0, "height": h, "y": y, "at": [3, 4], "solid": True, "place": [[0, 0, 0, 0]],
             **({"_about": about} if about else {})})
    add(nm + " door", {"type": "ring", "count": N, "rOuter": r1, "rInner": r0, "height": h, "y": y, "at": [5], "glass": False,
                       "place": [[0, 0, 0, 0]], **({"opening": {"width": 1.3, "sill": 0, "springing": 2.05, "head": SEMI}} if door_ else {"solid": True})})
skin("shaft inner skin", DR0, DR0 + 0.2, G1, ATT - G1, True, "the stair shaft in the drum's wall: its inner skin, the door into the Whispering Gallery")
skin("shaft outer skin", SH1 - 0.35, SH1, G1, DT - G1, True)
skin("shaft attic skin", 19.3 - 0.35, 19.3, DT, ATT - DT, True)
ends = []
for k in (3, 6):                            # the radial planes at the shaft's ends: bay k's first edge (bays centred on k * 11.25)
    a = math.radians((k - 0.5) * 360 / N)
    rm = (DR0 + SH1) / 2
    ends.append([r4(rm * math.sin(a)), G1, r4(rm * math.cos(a)), r4(a)])
add("shaft ends", {"type": "box", "width": 0.35, "length": SH1 - DR0, "height": ATT - G1, "at": ends,
                   "_about": "the walls closing the shaft at its ends"})
SA_ = math.radians(4 * 360 / N)             # the shaft's middle: bay 4's, the south-west diagonal
SR, GR = 17.65, 1.45                        # the spiral's axis from the dome's centre, its radius (the walker needs 1.4 and more)
SC = (r4(SR * math.sin(SA_)), r4(SR * math.cos(SA_)))
add("gallery stair", {"type": "spiral-stair", "radius": GR, "newel": 0.25, "turn": 16, "top": DT - G1, "rise": 0.19, "soffit": 0.25,
                      "landing": 1.3, "at": [[SC[0], G1, SC[1], r4(SA_ + Q)]],
                      "_about": "the spiral up the shaft from the Whispering Gallery's level to the Stone Gallery's: 100 steps"})
sector = lambda r0, r1, a0, a1, n=6: [[r4(r1 * math.sin(a0 + (a1 - a0) * i / n)), r4(r1 * math.cos(a0 + (a1 - a0) * i / n))] for i in range(n + 1)] + \
                                     [[r4(r0 * math.sin(a1 - (a1 - a0) * i / n)), r4(r0 * math.cos(a1 - (a1 - a0) * i / n))] for i in range(n + 1)]
A0, A1 = math.radians(2.5 * 360 / N), math.radians(5.5 * 360 / N)
add("shaft floor", {"type": "prism", "plan": {"points": sector(DR0 + 0.2, SH1 - 0.35, A0, A1), "well": {"radius": GR + 0.12, "sides": 20, "at": list(SC)}},
                    "height": 0.3, "at": [[0, DT - 0.3, 0, 0]],
                    "_about": "the floor at the Stone Gallery's level the spiral comes up through, the door out onto the gallery beside it"})
add("shaft roof", {"type": "prism", "plan": {"points": sector(DR0 + 0.2, 19.0, A0, A1)}, "height": 0.4, "flatRoof": True,
                   "at": [[0, ATT - 0.4, 0, 0]]})

# the outer dome, its ribs, the Golden Gallery and the lantern with the ball and cross
OD_R, OD_S = 18.5, 0.2
add("attic cornice", {"type": "ring", "count": N, "rOuter": 19.9, "rInner": 17.0, "height": 0.8, "y": ATT - 0.8, "solid": True, "flatRoof": True,
                      "place": [[0, 0, 0, 0]], "_about": "the attic's cornice, the outer dome's foot"})
add("outer dome", {"type": "dome", "radius": OD_R, "thickness": 0.6, "head": {"profile": "pointed", "spread": OD_S}, "oculus": 3.0,
                   "at": [[0, ODS, 0, 0]], "_about": "the outer dome: timber and lead over the brick cone, a little taller than a half sphere"})
add("outer dome ribs", {"type": "ribs", "on": "outer dome", "count": N, "width": 0.3, "depth": 0.18})
LR, LH = 3.5, 12.0
LDH, LCR = LH * 0.22, LR * 0.74
LTOP = LH + LR * 0.09 + LDH + LCR * 1.732 - LR * 0.1
add("golden gallery", {"type": "ring", "count": 16, "rOuter": 5.6, "rInner": 3.0, "height": 0.9, "y": -0.8, "solid": True, "place": [[0, 0, 0, 0]],
                       "atop": "outer dome", "atopR": 4.4,
                       "_about": "the Golden Gallery round the lantern's foot, 85m up"})
add("lantern", comp("components/domed-tower", {"sides": 8, "R": LR, "H": LH, "t": r4(LR * 0.13), "drumR": r4(LR * 0.7), "drumH": r4(LDH), "cap": "pointed",
                                               "capR": r4(LCR), "kok": r4(LR * 0.09), "finial": r4(LR * 0.13), "winW": r4(LR * 0.28), "doorH": r4(LH * 0.3), "capRibs": 8},
                    [[0, r4(-LR * 0.1), 0, 0]], build=["tower", "head", "neck", "drum", "cornice", "cap", "cap ribs"], atop="outer dome", atopR=LR,
                    _about="the stone lantern on the dome, its columned faces, its cupola"))
add("lantern columns", {"type": "colonnade", "plan": "round", "count": 8, "radius": r4(LR * 1.08), "order": "corinthian", "columnR": r4(LR * 0.065),
                        "height": r4(LH * 0.88), "sides": 8, "atop": "outer dome", "atopR": LR,
                        "at": [[0, r4(-LR * 0.1), 0, r4(math.pi / 8 + 0.075)], [0, r4(-LR * 0.1), 0, r4(math.pi / 8 - 0.075)]]})
add("lantern spire", {"type": "column", "radius": r4(LR * 0.11), "height": r4(LR * 0.6), "sides": 12, "taper": 0.55, "atop": "outer dome", "atopR": LR,
                      "at": [[0, r4(LTOP - 0.3 - LR * 0.1), 0, 0]]})
add("golden ball", {"type": "loft", "axis": "y", "sides": 16, "smooth": 3, "atop": "outer dome", "atopR": LR,
                    "at": [[0, r4(LTOP + LR * 0.45 - LR * 0.1), 0, 0]],
                    "sections": [{"s": 0, "a": r4(LR * 0.054), "b": r4(LR * 0.054)}, {"s": r4(LR * 0.11), "a": r4(LR * 0.23), "b": r4(LR * 0.23)},
                                 {"s": r4(LR * 0.27), "a": r4(LR * 0.27), "b": r4(LR * 0.27)}, {"s": r4(LR * 0.43), "a": r4(LR * 0.23), "b": r4(LR * 0.23)},
                                 {"s": r4(LR * 0.54), "a": r4(LR * 0.043), "b": r4(LR * 0.043)}], "_about": "the gilt ball..."})
add("golden cross", {"type": "box", "width": r4(LR * 0.1), "length": r4(LR * 0.1), "height": r4(LR * 0.98), "atop": "outer dome", "atopR": LR,
                     "at": [[0, r4(LTOP + LR * 0.95 - LR * 0.1), 0, 0]], "_about": "...and the cross, 111m over the churchyard"})
add("golden cross arm", {"type": "box", "width": r4(LR * 0.65), "length": r4(LR * 0.1), "height": r4(LR * 0.1), "atop": "outer dome", "atopR": LR,
                         "at": [[0, r4(LTOP + LR * 1.55 - LR * 0.1), 0, 0]]})

# =====================================================================================================================
# THE WEST END: the chapels, the vestibule, the towers' halls, the portico, the towers
# =====================================================================================================================
# the west bay's arches into the chapels are the arcades' last bay; the chapels' ceilings; the walls between chapels and towers
for sx, nm in ((1, "south"), (-1, "north")):
    a, b = (sx * AO, 66.0), (sx * (WX - TW + 0.2), 66.0)
    iwall(f"{nm} chapel wall", a, b, 3.2, F, WT - F, [{"openings": [door(along(a, b, (sx * 21.25, 66.0)), 1.4, 3.0)]}],
          about="between the west chapels and the towers' halls, a door through" if sx > 0 else None)
    a, b = (sx * (PX + 1.1), 67.6), (sx * (PX + 1.1), VZ - 0.2)
    iwall(f"{nm} vestibule wall", a, b, 2.2, F, WT - F, [{"openings": [door(along(a, b, (a[0], 78.0)), 1.4, 3.0)]}],
          about="the vestibule's sides, a door into each tower's hall" if sx > 0 else None)
add("chapel ceilings", {"type": "prism", "plan": {"rect": [r4(WX - TW - AO + 0.4), 10.0]}, "height": 0.5, "flatRoof": True,
                        "at": [[r4(sx * (WX - TW + AO) / 2), F + 14.0, 60.0, 0] for sx in (1, -1)],
                        "_about": "the chapels' ceilings (St Dunstan's to the north, St Michael and St George's to the south)"})
add("vestibule ceiling", {"type": "prism", "plan": {"rect": [2 * PX + 0.4, VZ - 2.2 - 66.0]}, "height": 0.5, "flatRoof": True,
                          "at": [[0, 32.0, r4((VZ - 2.2 + 66.0) / 2), 0]]})
# THE GEOMETRIC STAIRCASE in the south-west tower: a spiral round an open well, from the floor to the tower's upper floor
# and the door out onto the portico's upper loggia
GX, GZ = 21.25, 73.0
add("geometric staircase", {"type": "spiral-stair", "radius": 3.4, "newel": 1.2, "post": False, "turn": 9, "top": L1 - F, "rise": 0.18, "soffit": 0.3,
                            "landing": 1.8, "at": [[GX, F, GZ, 0]],
                            "_about": "the Geometric Staircase: a spiral round an open well, each step cantilevered from the wall, to the tower's upper floor"})
add("tower floor", {"type": "prism", "plan": {"rect": [r4(WX - TW - PX - 2.2), r4(TWZ - TW - 67.6)], "well": {"radius": 3.55, "sides": 24, "at": [r4(GX - (WX - TW + PX + 2.2) / 2), r4(GZ - (TWZ - TW + 67.6) / 2)]}},
                    "height": 0.5, "at": [[r4((WX - TW + PX + 2.2) / 2), L1 - 0.5, r4((TWZ - TW + 67.6) / 2), 0]],
                    "_about": "the south-west tower's upper floor round the stair's well (Wren's library is reached from it)"})
add("north tower floors", {"type": "prism", "plan": {"rect": [r4(WX - TW - PX - 2.2), r4(TWZ - TW - 67.6)]}, "height": 0.5, "flatRoof": True,
                           "at": [[r4(-(WX - TW + PX + 2.2) / 2), F + 12.0, r4((TWZ - TW + 67.6) / 2), 0]]})
# THE PORTICO: two storeys of paired columns (six pairs below, four above) under the pediment
PZ = 85.2
add("portico floor", {"type": "prism", "plan": {"rect": [2 * PX + 0.2, PZ + 1.2 - VZ]}, "height": F, "at": [[0, 0, r4((PZ + 1.2 + VZ) / 2), 0]],
                      "_about": "the portico's floor, level with the church's"})
add("west steps", {"type": "flight", "width": 30.0, "run": 0.42, "rise": 0.18, "base": 0, "top": F, "landing": 0,
                   "at": [[15.0, 0, r4(PZ + 1.2 + 22 * 0.42), Q]], "_about": "the broad flight of steps up to the west portico"})
pairs = lambda xs, z, y: [[r4(x), y, z, 0] for x in xs]
add("lower portico columns", {"type": "colonnade", "plan": "straight", "count": 2, "spacing": 1.75, "order": "corinthian", "columnR": 0.68,
                              "height": 13.0, "taper": 0.86, "at": pairs((-12.0, -7.2, -2.4, 2.4, 7.2, 12.0), PZ, F),
                              "_about": "the lower portico: six pairs of Corinthian columns"})
add("lower portico entablature", {"type": "box", "width": 2 * PX - 0.4, "length": r4(PZ + 1.0 - VZ), "height": L1 - F - 13.0,
                                  "at": [[0, F + 13.0, r4((PZ + 1.0 + VZ) / 2), 0]],
                                  "_about": "its entablature, the floor of the upper loggia"})
add("upper portico columns", {"type": "colonnade", "plan": "straight", "count": 2, "spacing": 1.6, "order": "corinthian", "columnR": 0.6,
                              "height": 12.0, "taper": 0.86, "at": pairs((-9.6, -3.0, 3.0, 9.6), PZ, L1),
                              "_about": "the upper: four pairs (Composite in the real one)"})
add("upper portico entablature", {"type": "box", "width": 24.6, "length": r4(PZ + 1.0 - VZ), "height": WT - L1 - 12.0,
                                  "at": [[0, L1 + 12.0, r4((PZ + 1.0 + VZ) / 2), 0]]})
add("pediment", {"type": "roof", "form": "gable", "width": 25.0, "length": r4(PZ + 1.4 - VZ + 2.0), "pitch": 22, "overhang": 0.3, "rake": True,
                 "at": [[0, WT, r4((PZ + 1.4 + VZ - 2.0) / 2), 0]], "_about": "the pediment over the upper portico (the Conversion of St Paul in its tympanum)"})

# THE WEST TOWERS over the roofs: a plinth (the clock in the south one), the belfry open in an arch on every face with
# paired columns at its corners, its cornice, the chamfered upper stage, the ogee cap and the gilt pineapple
TOW = [(21.25, 78.0), (-21.25, 78.0)]
TP, TB, TB1, TU1 = WT + 5.0, 39.0 + 11.0, 0, 0
add("tower plinths", {"type": "prism", "plan": {"rect": [11.0, 11.0]}, "height": 5.0, "flatRoof": True, "at": [[x, WT, z, 0] for x, z in TOW],
                      "_about": "the west towers: the plinth over the roofs..."})
add("tower belfries", {"type": "enclosure", "plan": {"rect": [9.4, 9.4]}, "thickness": 1.1, "height": 11.0, "glass": False, "interior": True,
                       "openings": [win(0, 3.4, 1.2, 7.4)], "at": [[x, TP, z, 0] for x, z in TOW],
                       "_about": "...the belfry, a tall arch in every face (the south-west tower's Great Paul, the north-west's ring of twelve)..."})
cols = []
for x, z in TOW:
    for f in range(4):
        yaw = f * Q
        for u in (-3.7, 3.7):
            px, pz = turned((u, 5.35), yaw)
            cols.append([r4(x + px), TP, r4(z + pz), r4(yaw)])
add("tower columns", {"type": "colonnade", "plan": "straight", "count": 2, "spacing": 1.2, "order": "corinthian", "columnR": 0.36,
                      "height": 9.6, "taper": 0.88, "at": cols, "_about": "...paired Corinthian columns at its corners..."})
add("tower cornices", {"type": "prism", "plan": {"rect": [11.8, 11.8]}, "height": 1.4, "flatRoof": True, "at": [[x, TP + 9.6, z, 0] for x, z in TOW]})
add("tower upper stages", {"type": "enclosure", "plan": {"rect": [7.4, 7.4], "chamfer": 1.6}, "thickness": 0.8, "height": 5.6, "interior": True,
                           "faces": {"main": [win(0, 1.8, 1.9, 1.9, foot=SEMI)], "chamfer": []}, "at": [[x, TP + 11.0, z, 0] for x, z in TOW],
                           "_about": "...the chamfered upper stage, a round window in each face..."})
add("tower upper cornices", {"type": "prism", "plan": {"rect": [8.2, 8.2], "chamfer": 1.9}, "height": 0.6, "flatRoof": True,
                             "at": [[x, TP + 16.6, z, 0] for x, z in TOW]})
for (x, z), nm in zip(TOW, ("south-west", "north-west")):
    add(f"{nm} tower cap", {"type": "dome", "radius": 3.9, "thickness": 0, "sides": 16, "head": {"profile": "bell", "waist": 0.72, "lift": 1.25},
                            "at": [[x, TP + 17.2, z, 0]], **({"_about": "...the ogee cap of lead..."} if x > 0 else {})})
    add(f"{nm} pineapple", {"type": "loft", "axis": "y", "sides": 12, "smooth": 2, "atop": f"{nm} tower cap", "at": [[x, -0.1, z, 0]],
                            "sections": [{"s": 0, "a": 0.25, "b": 0.25}, {"s": 0.5, "a": 0.7, "b": 0.7}, {"s": 1.3, "a": 0.85, "b": 0.85},
                                         {"s": 2.2, "a": 0.6, "b": 0.6}, {"s": 2.9, "a": 0.1, "b": 0.1}],
                            **({"_about": "...and the gilt pineapple on it"} if x > 0 else {})})
add("clock", comp("components/clock-dial", {"R": 1.6, "t": 0.12, "hour": 10, "minute": 10},
                  [[TOW[0][0], WT + 2.5, r4(TOW[0][1] + 5.55), 0], [r4(TOW[0][0] + 5.55), WT + 2.5, TOW[0][1], Q]],
                  _about="the clock on the south-west tower, its dials to the west and south"))

# THE TRANSEPT PORTICOES: a half round of six columns under a half dome before each door, on a half-round floor with
# a flight down to the street
for sx, nm in ((1, "south"), (-1, "north")):
    hp = [[r4(sx * TX), 7.6]] + [[r4(sx * (TX + 7.6 * math.sin(math.pi * i / 12))), r4(7.6 * math.cos(math.pi * i / 12))] for i in range(13)]
    if sx < 0: hp = hp[::-1]
    add(f"{nm} portico floor", {"type": "prism", "plan": {"points": hp}, "height": F, "at": [[0, 0, 0, 0]],
                                **({"_about": "the transept porticoes' floors, half rounds before the doors"} if sx > 0 else {})})
    add(f"{nm} portico", {"type": "colonnade", "plan": "round", "arc": 180, "count": 6, "radius": 6.2, "order": "corinthian", "columnR": 0.62,
                          "height": 12.4, "taper": 0.86, "entablature": {"h": 2.0, "depth": 1.7}, "at": [[r4(sx * TX), F, 0, sx * Q]],
                          **({"_about": "the transept porticoes: six columns on a half round before each door..."} if sx > 0 else {})})
    add(f"{nm} portico dome", {"type": "dome", "sweep": 0.5, "sides": 16, "radius": 7.0, "thickness": 0.6, "head": SEMI,
                               "at": [[r4(sx * TX), F + 14.4, 0, sx * Q]], **({"_about": "...under a half dome"} if sx > 0 else {})})
    add(f"{nm} portico steps", {"type": "flight", "width": 9.0, "run": 0.36, "rise": 0.18, "base": 0, "top": F, "landing": 0,
                                "at": [[r4(sx * (TX + 7.6 + 22 * 0.36)), 0, r4(-4.5 * sx), math.pi if sx > 0 else 0.0]],
                                **({"_about": "the flights down from the porticoes"} if sx > 0 else {})})

# THE APSE: a half round east of the choir, two storeys outside, its half dome inside springing with the vessel's
APZ, APR, APT = -(CHE - TW / 2), 6.3, 2.3
apse_ring = lambda nm, y, h, r0, r1, **kw: add(nm, {"type": "ring", "count": 16, "rOuter": r1, "rInner": r0, "height": h, "y": y, "turn": 0.5,
                                                    "range": [12, 19], "place": [[0, 0, APZ, math.pi]], **kw})
apse_ring("apse basement", 0, F, APR, APR + APT, solid=True, _about="the apse: its basement...")
apse_ring("apse windows", F, L1 - F, APR, APR + APT, at=[13, 15, 0, 2], opening={"width": 2.2, "sill": 3.2, "springing": 10.0, "head": SEMI},
          orders=[{"kind": "corinthian"}], _about="...its lower storey, four windows...")
apse_ring("apse piers", F, L1 - F, APR, APR + APT, at=[12, 14, 1, 3], solid=True, orders=[{"kind": "corinthian"}])
apse_ring("apse upper", L1, WT - L1, APR + 1.0, APR + APT, solid=True, orders=[{"kind": "corinthian"}], _about="...its upper storey, round the half dome")
apse_ring("apse springer", L1, SN - L1, APR, APR + 1.0, solid=True)
add("apse half dome", {"type": "dome", "sweep": 0.5, "sides": 16, "radius": APR + 1.0, "thickness": 1.0, "head": SEMI,
                       "at": [[0, SN, APZ, math.pi]], "_about": "the apse's half dome, its mosaic of Christ in majesty"})
add("apse roof", {"type": "dome", "sweep": 0.5, "sides": 16, "radius": APR + APT + 0.2, "thickness": 0, "head": {"profile": "segmental", "rise": 2.0},
                  "at": [[0, WT, APZ, math.pi]], "_about": "its lead roof"})
add("apse floor", {"type": "prism", "plan": {"points": [[-APR - 0.5, APZ]] + [[r4(-(APR + 0.5) * math.cos(math.pi * i / 12)), r4(APZ - (APR + 0.5) * math.sin(math.pi * i / 12))] for i in range(13)]},
                   "height": SLAB, "at": [[0, F - SLAB, 0, 0]]})

# =====================================================================================================================
# THE CRYPT: piers under the arcades and the aisles' arches, Nelson's tomb under the dome, the stair down
# =====================================================================================================================
cp = []
for z, _ in NAVE_PL[1:4] + CHOIR_PL[1:4]:
    for x in (-13.05, -AX, AX, 13.05): cp.append([r4(x), 0, r4(z), 0])
for z in (27.0, 37.8, 48.6, -27.0, -37.8, -48.6):
    for x in (-AX, AX): cp.append([r4(x), 0, r4(z), 0])
for sx in (1, -1):
    for z in (-AX, AX, -13.05, 13.05):
        if (sx, z) != (1, -13.05): cp.append([r4(sx * TR_BAY), 0, r4(z), 0])   # (the crypt stair stands in that one's place)
add("crypt piers", {"type": "box", "width": 2.0, "length": 2.0, "height": F - SLAB, "at": cp,
                    "_about": "the crypt's piers under the arcades and the aisles' arches (the largest crypt in Europe)"})
add("nelson tomb", {"type": "box", "width": 2.4, "length": 3.6, "height": 1.0, "at": [[0, 0, 0, 0]], "_about": "Nelson's tomb under the dome: the plinth..."})
add("nelson sarcophagus", {"type": "box", "width": 1.5, "length": 2.8, "height": 1.2, "at": [[0, 1.0, 0, 0]], "_about": "...and the black marble sarcophagus"})
add("crypt stair", {"type": "staircase", "flight": 11, "width": 1.3, "run": 0.28, "rise": r4(F / 22), "soffit": 0.3,
                    "landing": {"depth": 1.3, "width": 2.6, "shift": -0.65, "then": [{"from": "back", "at": -0.65, "flight": 11, "width": 1.3}]},
                    "at": [[r4(CRYPT_STAIR[0] - 1.4), 0, r4(CRYPT_STAIR[1] + 1.3), 0]],
                    "_about": "the stair down to the crypt from the south transept's east aisle"})

# =====================================================================================================================
# FITTINGS: the congregation's chairs, the choir stalls, the organ, the high altar under the baldacchino
# =====================================================================================================================
add("seating", {"type": "zone", "zone": "seating", "w": 11.0, "d": 30.0, "h": 15, "at": [[0, F, 39.5, -Q]],
                "_about": "chairs down the nave, facing the dome and the choir"})
add("crossing seating", {"type": "zone", "zone": "seating", "w": 14.0, "d": 9.0, "h": 15, "at": [[0, F, 6.0, -Q]]})
for sx, nm in ((1, "south"), (-1, "north")):
    add(f"{nm} choir stalls", {"type": "zone", "zone": "choir", "w": 19.0, "d": 3.4, "h": 6, "at": [[r4(sx * 4.3), F, -36.0, 0 if sx < 0 else math.pi]],
                               **({"_about": "Grinling Gibbons's stalls, facing across the choir"} if sx > 0 else {})})
add("organ", {"type": "zone", "zone": "organ", "w": 5.0, "d": 1.4, "h": 10.0, "at": [[r4(sx * 5.4), F, -24.2, 0 if sx < 0 else math.pi] for sx in (1, -1)],
              "_about": "the organ, its cases either side of the choir's entrance"})
add("high altar", {"type": "zone", "zone": "altar", "w": 4.0, "d": 2.0, "h": 8, "at": [[0, F, -57.5, -Q]], "_about": "the high altar..."})
BAL = [(-2.6, -55.8), (2.6, -55.8), (-2.6, -59.6), (2.6, -59.6)]
add("baldacchino steps", {"type": "box", "width": 7.4, "length": 5.6, "height": 0.36, "at": [[0, F, -57.7, 0]], "_about": "...on its steps..."})
add("baldacchino columns", {"type": "column", "radius": 0.34, "height": 8.4, "sides": 12, "taper": 0.9,
                            "twist": {"lobes": 4, "depth": 0.12, "turns": 3, "rows": 16, "helix": 0.2}, "at": [[x, F + 0.36, z, 0] for x, z in BAL],
                            "_about": "...under the baldacchino: four barley-sugar columns (gilt)..."})
add("baldacchino canopy", {"type": "box", "width": 6.4, "length": 4.9, "height": 1.0, "flatRoof": True, "at": [[0, F + 8.76, -57.7, 0]], "_about": "...its entablature..."})
add("baldacchino crown", {"type": "dome", "radius": 2.0, "thickness": 0, "head": {"profile": "bell", "waist": 0.8, "lift": 1.0}, "sides": 12,
                          "at": [[0, F + 9.76, -57.7, 0]], "_about": "...and its crown"})

# =====================================================================================================================
# THE BALUSTRADES and the statues
# =====================================================================================================================
bal = Balusters(h=1.2, every=0.5)
area = sum(OUT[i][0] * OUT[(i + 1) % NF][1] - OUT[(i + 1) % NF][0] * OUT[i][1] for i in range(NF))
inward = lambda dx, dz: (-dz, dx) if area > 0 else (dz, -dx)
for i in range(NF):
    if i in (1, 2, 3, 11, 21): continue           # (the portico's: the pediment; the transept fronts: their gables)
    a, b = OUT[i], OUT[(i + 1) % NF]
    L = math.dist(a, b); dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, nz = inward(dx, dz)
    o = 0.4
    bal.run((a[0] + nx * o, a[1] + nz * o), (b[0] + nx * o, b[1] + nz * o), WT)
bal.ring(0, 0, 22.0, DT, 64)                       # the Stone Gallery's
bal.ring(0, 0, 14.6, G1, 64)                       # the Whispering Gallery's (over the crossing)
for k, v in bal.parts("balustrade").items(): add(k, v)

yPed = WT
WP = 25.0; rise = WP / 2 * math.tan(math.radians(22)); zG = PZ + 0.6
stat = {"statue St Paul": statue((0, yPed + rise + 0.1, zG), kind="man", style="roman", stone="limestone", scale=2.0, seed=3, face=FACE_PZ, hold={"R": "items/weapons/sword"}),
        "statue St Peter": statue((-(WP / 2 - 0.9), yPed, zG), kind="man", style="roman", stone="limestone", scale=1.7, seed=5, face=FACE_PZ),
        "statue St James": statue((WP / 2 - 0.9, yPed, zG), kind="man", style="roman", stone="limestone", scale=1.7, seed=7, face=FACE_PZ, hold={"R": "items/tools/staff"})}
for i_, x in enumerate((-27.7, -15.0, 15.0, 27.7)):
    stat[f"statue evangelist {i_ + 1}"] = statue((x, WT, TWZ - 0.4), kind="man", style="roman", stone="limestone", scale=1.7, seed=11 + i_, face=FACE_PZ, hold={"R": "items/tools/book"})
for k, v in capped(stat).items(): add(k, v)

# =====================================================================================================================
# THE INTERIORS (what finish.js reads in from out)
# =====================================================================================================================
def vol(name, plan, y, h, about=None, **kw):
    d = {"type": "interior", "plan": plan, "height": r4(h), "at": [[0, r4(y), 0, 0]] if "at" not in kw else kw.pop("at"), **kw}
    if about: d["_about"] = about
    return add(name, d)
rect = lambda x0, z0, x1, z1: {"points": [[r4(x0), r4(z1)], [r4(x1), r4(z1)], [r4(x1), r4(z0)], [r4(x0), r4(z0)]]}
vol("crypt", {"points": [list(p) for p in OUT]}, 0, F - SLAB, "the crypt under the whole church")
vol("nave and aisles", rect(-BX + 1.1, 18.5, BX - 1.1, 66.0), F, 15.0, "nave, choir and transepts with their aisles up to the aisles' domes...")
vol("choir and aisles", rect(-BX + 1.1, -61.9, BX - 1.1, -18.5), F, 15.0)
vol("transepts and aisles", rect(18.5, -BX + 1.1, TX - 1.1, BX - 1.1), F, 15.0, at=[[0, F, 0, 0], [0, F, 0, math.pi]])
vol("vessels", rect(-AX, -61.9, AX, 66.0), F, 27.9, "...and the vessels up to their saucer domes")
vol("transept vessels", rect(18.5, -AX, TX - 1.1, AX), F, 27.9, at=[[0, F, 0, 0], [0, F, 0, math.pi]])
vol("crossing", {"points": [[r4(p[0] * 17.25 / OA), r4(p[1] * 17.25 / OA)] for p in oct_pts]}, F, WT - F, "the crossing, up to the Whispering Gallery...")
vol("drum", {"sides": 32, "radius": 17.5}, G1, DT - G1, "...and the drum to the inner dome's foot")
vol("junctions", {"points": [list(p) for p in JUNC]}, F, 14.0, at=[[0, F, 0, r4(y)] for y in QUADS])
vol("corner rooms", rect(BX - 1.1, BX - 1.1, CB - 1.1, CB - 1.1), F, 10.0, at=[[0, F, 0, r4(y)] for y in QUADS[1:]])
vol("dome stair room", rect(BX - 1.1, BX - 1.1, CB - 1.1, CB - 1.1), F, WT - F, "the dome stair's room in the south-west block")
vol("west chapels", rect(AO, 55.1, WX - 1.1, 64.4), F, 14.0, "the west chapels either side of the west bay")
add("west chapels north", {"type": "interior", "plan": rect(-(WX - 1.1), 55.1, -AO, 64.4), "height": 14.0, "at": [[0, F, 0, 0]]})
vol("vestibule", rect(-PX - 1.1, 66.0, PX + 1.1, VZ - 1.1), F, 28.0, "the west vestibule between the towers")
vol("tower halls", rect(PX + 1.1, 66.0, WX - 1.1, TWZ - 1.1), F, WT - F, "the towers' halls (the Geometric Staircase in the south one)")
add("tower halls north", {"type": "interior", "plan": rect(-(WX - 1.1), 66.0, -(PX + 1.1), TWZ - 1.1), "height": WT - F, "at": [[0, F, 0, 0]]})
vol("apse", {"sides": 32, "radius": APR + APT / 2}, F, SN - F, "the apse to its half dome", arc=[90, 270], at=[[0, F, APZ, 0]])
vol("shaft", {"points": sector(DR0 + 0.3, SH1 - 0.45, A0 + 0.01, A1 - 0.01)}, G1, ATT - G1, "the stair shaft in the drum's wall")

doc = {"name": "St Paul's Cathedral",
       "_about": "ST PAUL'S CATHEDRAL, London (Wren, 1675-1710), on its real plan (OSM way 369161987; Parr's and Wren's plans): the Latin cross 158m long with its outer walls in two storeys over a basement -- the upper a screen hiding the aisle roofs and the flying buttresses --, nave and choir of three bays under saucer domes on pendentives, aisles under smaller ones, transepts with half-round porticoes; the crossing an octagon of eight arches carrying the Whispering Gallery, the drum and the inner dome; outside the podium, the peristyle of 32 columns, the Stone Gallery, the attic, the lead outer dome, the Golden Gallery and the lantern with the gilt ball and cross at 111m; the west front's two-storey portico of paired columns under the pediment between the two baroque towers (the clock in the south-west one); the crypt under it all. Walked: the dome stair from the floor to the roofs round the drum, the shaft in the drum's wall to the Whispering Gallery and up to the Stone Gallery, the Geometric Staircase to the portico's upper loggia, the crypt (tools/archgen/st_pauls.py).",
       "params": {"detail": 4}, "base": {"height": 0.3, "steps": 1, "stepOut": 0.4, "margin": 5}, "railing": {"type": "stone"},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/st-pauls.json"), "w").write(json.dumps(doc, indent=2) + "\n")

# =====================================================================================================================
# THE FINISH: Portland stone, weathered pale; lead roofs and domes; gilt ball, cross and pineapples; inside pale stone,
# the choir's saucer domes and the apse in gold mosaic, the inner dome painted in grisaille, the floor black and white
# =====================================================================================================================
fin = {"name": "St Paul's Cathedral", "building": "architecture/st-pauls",
       "_about": "St Paul's: Portland stone, weathered pale and streaked; the roofs and the domes in lead, the ball, the cross and the towers' pineapples gilt. Inside, pale stone, the choir's saucer domes and the apse in Richmond's gold mosaics, Thornhill's grisaille in the inner dome, the floor black and white marble (the compass under the dome).",
       "stone": {"color": "#e4dfd2", "accent": "#cdc6b5", "pat": "ashlar"},
       "rules": [
           {"parts": ["golden ball", "golden cross", "golden cross arm", "lantern spire", "south-west pineapple", "north-west pineapple", "clock/hands", "clock/marks", "clock/ring"],
            "pattern": "roofs/gold leaf", "_about": "the gilt ball and cross, the towers' pineapples, the clock's hands"},
           {"parts": ["baldacchino columns", "baldacchino crown"], "pattern": "roofs/gold leaf", "_about": "the baldacchino's gilt"},
           {"parts": "baldacchino canopy", "color": "#3b3330", "accent": "#7a6a52", "pat": "marble"},
           {"parts": "nelson sarcophagus", "color": "#1d1b1a", "accent": "#3a3633", "pat": "marble", "_about": "Nelson's black marble"},
           {"parts": "clock/dial", "color": "#1e2430", "accent": "#2c3442", "_about": "the clock's dark faces"},
           {"parts": ["kind:dome", "kind:roof", "outer dome ribs", "lantern/cap", "lantern/cap ribs", "south-west tower cap", "north-west tower cap"],
            "surface": "roof", "pattern": "roofs/sheet metal", "palette": "lead", "_about": "lead: the domes, the caps, the roofs"},
           {"parts": ["aisle roofs", "nave aisle roofs", "choir aisle roofs", "transept aisle roofs", "crossing roof", "dome stair head", "west flats"],
            "surface": "floor", "pattern": "roofs/sheet metal", "palette": "lead", "_about": "the lead flats"},
           {"parts": "inner dome", "side": "in", "pattern": "mosaic/wall arcade", "palette": "thornhill-grisaille", "scale": 3,
            "_about": "Thornhill's grisaille in the inner dome: painted architecture and the life of St Paul in browns and greys"},
           {"parts": "vessel saucer domes", "within": [-10, -62, 10, -20], "side": "in", "pattern": "painted/gold mosaic",
            "_about": "the choir's saucer domes, Richmond's gold mosaics"},
           {"parts": ["vessel pendentives"], "within": [-10, -62, 10, -20], "side": "in", "pattern": "painted/gold mosaic"},
           {"parts": "apse half dome", "side": "in", "pattern": "mosaic/gold ground", "_about": "Christ in majesty in the apse"},
           {"surface": "floor", "side": "in", "above": F - 0.2, "below": F + 0.2,
            "pattern": "floors/compass", "palette": "marble-bw", "fit": [-14, -14, 14, 14], "_about": "the compass under the dome"},
           {"surface": "floor", "side": "in", "above": F - 0.2, "below": F + 0.2, "pattern": "floors/checker diagonal", "palette": "marble-bw",
            "_about": "the church's floor, black and white marble"},
           {"surface": "floor", "side": "in", "pattern": "floors/flagstones", "palette": "limestone"},
           {"surface": "floor", "pattern": "floors/flagstones", "palette": "limestone"},
           {"surface": ["wall", "ceiling"], "side": "in", "pattern": "stone/ashlar fine", "palette": "limestone", "_about": "pale stone inside"},
           {"surface": "wall", "below": F, "pattern": "stone/rusticated", "palette": "limestone", "_about": "the basement storey, rusticated"},
           {"parts": "kind:moulding", "pattern": "stone/ashlar fine", "palette": "limestone"},
           {"surface": ["wall", "ceiling", "roof"], "pattern": "stone/ashlar", "palette": "limestone", "_about": "Portland stone outside"},
       ]}
open(os.path.join(ROOT, "assets/finishes/st-pauls.json"), "w").write(json.dumps(fin, indent=1) + "\n")
print("st-pauls:", len(parts), "parts")
