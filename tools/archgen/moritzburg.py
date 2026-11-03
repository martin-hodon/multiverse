# SCHLOSS MORITZBURG (Saxony): Augustus the Strong's baroque hunting lodge, rebuilt 1723-33 by Matthaeus Daniel Poeppelmann
# round the Renaissance lodge of 1542-46 (its four round towers and the chapel of 1661-72 kept), on its artificial island
# in the Schlossteich.
# THE FRAME: +x EAST, +z SOUTH (the front: the causeway and the town), y up; the origin is the middle of the four towers
# (OpenStreetMap: ways 246775517/521/529/533), the axes turned 2.77 degrees to the castle's own; y 0 is the island's
# ground. THE PLAN IS OSM's, turned into this frame: the castle (relation 20405783: the H of the two wings between the
# towers, the recessed north and south fronts, the chapel risalit on the west, the Speisesaal risalit on the east), its
# parts' heights (the Mittelbau 34 m, the ranges 29, the chapel 29 with the Dachreiter to 43), the terrace (relation
# 20408145, 5 m: its north and south bulges, the east and west lobes with their curved stairs), the ramps (north and
# south Auffahrten), the island (relation 124276, inner ring), the eight guardhouses, the bridges, the causeway, the
# trees. Storey heights from photographs (Wikimedia Commons: the view from the south-west, 2005; the aerials): the ground
# floor and three storeys over the terrace, the round towers' cornice level with the main one.
# THE INSIDE after the literature (de.wikipedia "Schloss Moritzburg (Sachsen)", museum-digital Sachsen, the SBG's
# guide): the vaulted entrance halls on the north-south axis; on the principal floor (1.OG) the four great halls, each two
# storeys high -- the Billardsaal (north), the Steinsaal (middle) and the Monstroesensaal (south) in the Mittelbau, the
# Speisesaal with its 71 red-deer trophies in the east risalit -- the chapel in the west risalit, two storeys high with
# the princely gallery; the apartments in the ranges and wings (the Federzimmer in the west wing), round rooms in the
# towers; two dog-leg stairs where the light wells are. Room walls where the plans' halls and the windows' axes put them.
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapes import bell_y_at
from historicism import comp, flight
from statuary import statue, capped
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n); return n
r4 = lambda v: round(v, 4)
Q, PI = math.pi / 2, math.pi

# ---- THE LEVELS
TT = 5.0                                   # the terrace's top: the castle's ground floor
HS = [4.8, 5.4, 4.6, 4.2]                  # its storeys: the ground floor, the principal floor, the second, the top storey
LV = [TT, TT + 4.8, TT + 10.2, TT + 14.8]  # their floors
EAVE = TT + sum(HS)                        # 24.0, the main cornice
T, IT = 1.0, 0.5                           # outer walls, inner walls
SLAB = 0.3
SEG = {"profile": "segmental", "rise": 0.3}
FLAT = {"profile": "flat"}
ROUND = {"profile": "semicircular"}

# ---- THE PLAN (OSM, in the frame)
WX0, WX1, EX0, EX1 = -28.8, -21.6, 21.4, 28.6        # the west wing, the east wing (x)
WZ0, WZ1 = -21.4, 21.6                               # both wings (z): tower to tower
BX0, BX1, BZ0, BZ1 = WX1, EX0, -15.0, 15.6           # the main body between them: the recessed north and south fronts
MX0, MX1 = -9.7, 7.4                                 # the Mittelbau (the three halls) within it
MXC = (MX0 + MX1) / 2                                # its axis: the portals, x -1.15
LZN, LZS = -4.9, 5.4                                 # the walls between the ranges and the middle strip (the light wells' line)
SX0, SX1 = 7.4, 14.6                                 # the east stair hall (OSM's east light wells)
WSX0, WSX1 = -14.5, -9.7                             # the west stair hall
TR = 6.9                                             # the round towers
TOWERS = {"SE": (26.9, 27.9), "NE": (26.9, -27.9), "NW": (-26.9, -27.9), "SW": (-26.9, 27.9)}
CX0, CX1, CZ0, CZ1 = -40.7, WX0, -5.3, 7.4           # the chapel
RX0, RX1, RZ0, RZ1 = EX1, 43.4, -6.4, 6.5            # the Speisesaal risalit
CH_EAVE = TT + 15.0                                  # the chapel's cornice
R_TIERS = [4.8, 7.6, 2.4, 5.2]; R_EAVE = TT + sum(R_TIERS)   # the risalit: ground floor, the hall, the top storey

def at_on(face, x0, x1, z0, z1, w):
    """a world coordinate along a rect enclosure's face -> that face's `at` (from its middle: face 0 runs +x, 1 -z, 2 -x, 3 +z)"""
    xm, zm = (x0 + x1) / 2, (z0 + z1) / 2
    return r4([w - xm, zm - w, xm - w, w - zm][face])

def encl(name, x0, x1, z0, z1, y0, tiers, faces, t=T, skip=(), interior=True, about="", **kw):
    """a storeyed block on the rect: `faces` {0: +z, 1: +x, 2: -z, 3: -x} each f(j, h) -> storey j's openings"""
    F = {}
    for k in range(4):
        f = faces.get(k)
        ts = [{"h": h, "openings": (f(j, h) if f else [])} for j, h in enumerate(tiers[:-1])]
        F[str(k)] = ts + [{"openings": (f(len(tiers) - 1, tiers[-1]) if f else [])}]
    d = {"type": "enclosure", "plan": {"rect": [r4(x1 - x0), r4(z1 - z0)]}, "thickness": t, "height": r4(sum(tiers)), "glass": True,
         "interior": interior, "faces": F, "courses": {"skip": [str(k) for k in skip]} if skip else True,
         "at": [[r4((x0 + x1) / 2), y0, r4((z0 + z1) / 2), 0]], "_about": about, **kw}
    return add(name, d)

# THE WINDOWS, storey by storey (j): the ground floor's under a segmental head, the principal floor's under a cornice,
# the second floor's and the top storey's plain -- every one in its white architrave; the halls' tall arched lights
def WIN(a, j, hall=False):
    if hall and j == 1: return {"at": r4(a), "width": 1.6, "sill": 0.6, "springing": 3.9, "head": ROUND, "surround": {"keystone": True}}
    if hall and j == 2: return {"at": r4(a), "width": 1.6, "sill": 0.6, "springing": 3.0, "head": SEG, "surround": {"head": False}}
    return [{"at": r4(a), "width": 1.3, "sill": 1.0, "springing": 3.3, "head": SEG, "surround": {"head": False}},
            {"at": r4(a), "width": 1.4, "sill": 0.9, "springing": 3.9, "head": FLAT, "surround": {"head": "cornice"}},
            {"at": r4(a), "width": 1.4, "sill": 0.8, "springing": 3.3, "head": FLAT, "surround": {"head": False}},
            {"at": r4(a), "width": 1.25, "sill": 0.7, "springing": 2.9, "head": FLAT, "surround": {"head": False}}][j]
DOOR = lambda a, w=1.3, h=2.7: {"at": r4(a), "width": w, "sill": 0, "springing": h, "head": SEG, "glass": False}
PORTAL = lambda a: {"at": r4(a), "width": 2.4, "sill": 0, "springing": 3.2, "head": ROUND, "glass": False, "surround": {"keystone": True}}

# ---- THE MAIN BODY: one block between the wings, its fronts the recessed north and south fronts (13 axes, the middle
# five the Mittelbau's: the portal, the balcony over it on the south front, the halls' tall arched lights over the
# ground floor), its ends standing against the wings (doorways through both walls)
BAYS = [r4(MXC + 3.2 * k) for k in range(-6, 7) if BX0 + 1.4 < MXC + 3.2 * k < BX1 - 1.4]
HALL_BAYS = [b for b in BAYS if MX0 < b < MX1]
PARTY_Z = [-9.5, 0.25, 10.0]                       # the doorways between the main body and the wings, every storey

def front(face, z):
    def f(j, h):
        out = []
        for b in BAYS:
            a = at_on(face, BX0, BX1, BZ0, BZ1, b)
            if abs(b - MXC) < 0.1 and j == 0: out.append(PORTAL(a)); continue
            if abs(b - MXC) < 0.1 and j == 1 and face == 0:   # (the balcony's door over the south portal)
                out.append({"at": a, "width": 1.6, "sill": 0, "springing": 3.9, "head": ROUND, "glass": False, "surround": {"keystone": True}}); continue
            out.append(WIN(a, j, hall=b in HALL_BAYS))
        return out
    return f
party_main = lambda face: (lambda j, h: [DOOR(at_on(face, BX0, BX1, BZ0, BZ1, z)) for z in PARTY_Z])
encl("main body", BX0, BX1, BZ0, BZ1, TT, HS, {0: front(0, BZ1), 2: front(2, BZ0), 1: party_main(1), 3: party_main(3)}, skip=(1, 3),
     about="the main body between the wings: the south front (the cour d'honneur's, toward the causeway) and the north front, thirteen axes each, the Mittelbau's five in the middle with the portal and the halls' tall lights")

# ---- THE WINGS: east and west, tower to tower; their outer fronts toward the terrace's lobes, the chapel and the
# Speisesaal standing against their middles; doorways into the main body, the risalits and the towers
def wing(name, x0, x1, outer, inner, block_z, door_z):
    xm = (x0 + x1) / 2
    zs = [r4(0.1 + 3.3 * k) for k in range(-6, 7)]
    out_zs = [z for z in zs if abs(z) < 19.0 and not (block_z[0] - 0.6 < z < block_z[1] + 0.6)]
    faces = {
        outer: lambda j, h: [WIN(at_on(outer, x0, x1, WZ0, WZ1, z), j) for z in out_zs] +
                            ([DOOR(at_on(outer, x0, x1, WZ0, WZ1, door_z), 2.0, 3.2)] if j in door_storeys[name] else []),
        inner: lambda j, h: [DOOR(at_on(inner, x0, x1, WZ0, WZ1, z)) for z in PARTY_Z] + [WIN(at_on(inner, x0, x1, WZ0, WZ1, z), j) for z in (-18.2, 18.6)],
        0: lambda j, h: [DOOR(at_on(0, x0, x1, WZ0, WZ1, -26.9 if x0 < 0 else 26.9), 1.2)],
        2: lambda j, h: [DOOR(at_on(2, x0, x1, WZ0, WZ1, -26.9 if x0 < 0 else 26.9), 1.2)]}
    return encl(name, x0, x1, WZ0, WZ1, TT, HS, faces, skip=(0, 2),
                about=f"the {name}: four storeys tower to tower, a room's depth, its outer front of eleven axes either side of the risalit")
door_storeys = {"west wing": (0, 1), "east wing": (0, 1, 3)}
wing("west wing", WX0, WX1, 3, 1, (CZ0 - 2.4, CZ1 + 2.2), 1.0)
wing("east wing", EX0, EX1, 1, 3, (RZ0, RZ1), 0.0)

# ---- THE FOUR ROUND TOWERS (the Renaissance lodge's, 1542-46): 24-sided drums of the same four storeys, a window every
# eighth of the way round except where the wing stands against them; the door through the wing's end wall on every
# storey; white lesenes between the windows over the ground floor; the cap -- components/baroque-helm: the red-tiled
# bell, its moulded foot over the cornice, the white open lantern -- and a copper cap with a gilt vane on the lantern
NS = 24
angoff = lambda a, b: abs((a - b + 180) % 360 - 180)
def tower_faces(cx, cz):
    wing_x = (WX0, WX1) if cx < 0 else (EX0, EX1)
    zend = WZ1 if cz > 0 else WZ0
    blocked = [math.degrees(math.atan2(wx - cx, zend - cz)) for wx in wing_x]   # (the wing's end corners seen from the middle)
    mid = math.degrees(math.atan2(sum(wing_x) / 2 - cx, zend - cz)); half = abs(blocked[0] - blocked[1]) / 2
    if half > 90: half = 180 - half
    lo, hi = mid, half
    door_face = 11 if cz > 0 else 23
    F = {}
    for i in range(NS):
        ang = (i + 1) * 360 / NS % 360
        if i == door_face: F[str(i)] = [{"h": h, "openings": [DOOR(0, 1.2)]} for h in HS[:-1]] + [{"openings": [DOOR(0, 1.2)]}]; continue
        if (i + 1) % 3 == 0 and not angoff(ang, lo) < hi + 8:
            F[str(i)] = [{"h": h, "openings": [WIN(0, j) if j else {**WIN(0, 0), "width": 1.1}]} for j, h in enumerate(HS[:-1])] + \
                        [{"openings": [{**WIN(0, 3), "width": 1.1}]}]
    return F, (lo, hi)
HELM = {"sides": NS, "R": 6.6, "footH": 0.7, "profile": "bell", "waist": 0.88, "lift": 0.32, "LR": 1.5, "LH": 3.2, "glazed": 1, "lanterns": "one"}
LEAD = []                                                       # (the lesenes' placements: one part)
for k, (cx, cz) in TOWERS.items():
    F, (lo, hi) = tower_faces(cx, cz)
    add(f"tower {k}", {"type": "enclosure", "plan": {"sides": NS, "radius": TR}, "thickness": T, "height": r4(sum(HS)), "glass": True, "interior": True,
                       "tiers": [{"h": h, "openings": []} for h in HS[:-1]] + [{"openings": []}], "faces": F, "courses": True,
                       "at": [[cx, TT, cz, 0]], "_about": f"the {k} tower: a round drum of four storeys, its door through the wing's end wall on every one"})
    for a in range(NS):
        ang = (a + 0.5) * 360 / NS
        if (a + 1) % 3 == 2 and not angoff(ang, lo) < hi + 12:   # (the vertex half-way between two windows)
            t_ = math.radians(ang); r = TR * math.cos(math.pi / NS) + 0.06
            LEAD.append([r4(cx + r * math.sin(t_)), LV[1], r4(cz + r * math.cos(t_)), r4(t_)])
# the caps (components/baroque-helm's stages, built here because the helm's lantern takes the bell's 24 sides, too narrow
# for its arches): the moulded foot, the red bell, the white octagonal lantern where it has narrowed, its cornice
BY0 = EAVE + HELM["footH"]
LBASE = BY0 + bell_y_at(HELM["R"], HELM["LR"], HELM["waist"], HELM["lift"]) - HELM["LR"] * 0.06
LHEAD = LBASE + HELM["LH"] * 1.1
TW = list(TOWERS.values())
add("tower cap feet", {"type": "prism", "plan": {"sides": NS, "radius": r4(HELM["R"] * 1.06)}, "height": HELM["footH"], "flatRoof": True,
                       "courses": [{"y": r4(HELM["footH"] * 0.55), "h": r4(HELM["footH"] * 0.45), "out": 0.26, "profile": "cornice"}],
                       "at": [[cx, EAVE, cz, 0] for cx, cz in TW], "_about": "the moulded foot each bell stands on, over the towers' cornice"})
add("tower bells", {"type": "dome", "sides": NS, "radius": HELM["R"], "thickness": 0, "head": {"profile": "bell", "waist": HELM["waist"], "lift": HELM["lift"]},
                    "at": [[cx, r4(BY0), cz, 0] for cx, cz in TW], "_about": "the towers' bells (Schweifkuppeln): the concave sweep and the round crown, red-tiled"})
add("tower lanterns", {"type": "enclosure", "plan": {"sides": 8, "radius": HELM["LR"]}, "thickness": 0.24, "height": HELM["LH"], "interior": False, "glass": True,
                       "openings": [{"at": 0, "width": 0.82, "sill": 0.5, "springing": 2.1, "head": ROUND}],
                       "at": [[cx, r4(LBASE), cz, r4(math.pi / 8)] for cx, cz in TW], "_about": "the open lantern on each bell's crown: an arched light in every face"})
add("tower lantern heads", {"type": "prism", "plan": {"sides": 8, "radius": r4(HELM["LR"] * 1.14)}, "height": r4(HELM["LH"] * 0.1), "flatRoof": True,
                            "at": [[cx, r4(LBASE + HELM["LH"]), cz, r4(math.pi / 8)] for cx, cz in TW], "_about": "its cornice"})
add("tower lantern caps", {"type": "dome", "sides": NS, "radius": 1.78, "thickness": 0, "head": {"profile": "bell", "waist": 0.62, "lift": 0.55},
                           "at": [[cx, r4(LHEAD), cz, 0] for cx, cz in TOWERS.values()], "_about": "the copper cap on every lantern"})
add("tower vane balls", {"type": "dome", "sides": 12, "radius": 0.22, "thickness": 0, "head": {"profile": "onion", "bulge": 2.2, "neck": 0.5},
                         "at": [[cx, r4(LHEAD + 2.0), cz, 0] for cx, cz in TOWERS.values()], "_about": "the gilt knob on the cap"})
add("tower vanes", {"type": "bars", "w": 0.06, "h": 0.06, "kind": "iron",
                    "paths": [[[0, 0, 0], [0, 1.6, 0]], [[0, 1.1, 0], [0.7, 1.15, 0], [0.75, 1.45, 0], [0.05, 1.5, 0]],
                              [[0.45, 1.5, 0], [0.55, 1.75, 0], [0.75, 1.85, 0]], [[0.25, 1.5, 0], [0.2, 1.75, 0], [0.05, 1.85, 0]]],
                    "at": [[cx, r4(LHEAD + 2.3), cz, 0.6] for cx, cz in TOWERS.values()], "_about": "the gilt vane on every tower: a banner with antlers over it"})
# the oeil-de-boeuf dormers in two rings round each bell, under little hoods
cy, R2 = HELM["R"] * HELM["lift"], HELM["R"] * HELM["waist"]
dorm, hoods, dorm2 = [], [], []
for cx, cz in TOWERS.values():
    for k in range(8):
        t_ = math.radians(22.5 + 45 * k); h = cy + 0.7; r = math.sqrt(R2 * R2 - (h - cy) ** 2)
        dorm.append([r4(cx + (r - 0.35) * math.sin(t_)), r4(BY0 + h - 0.6), r4(cz + (r - 0.35) * math.cos(t_)), r4(t_)])
        hoods.append([r4(cx + (r + 0.25) * math.sin(t_)), r4(BY0 + h + 0.62), r4(cz + (r + 0.25) * math.cos(t_)), r4(t_)])
    for k in range(4):
        t_ = math.radians(45 + 90 * k); h = cy + 3.3; r = math.sqrt(R2 * R2 - (h - cy) ** 2)
        dorm2.append([r4(cx + (r - 0.2) * math.sin(t_)), r4(BY0 + h - 0.4), r4(cz + (r - 0.2) * math.cos(t_)), r4(t_)])
add("bell dormers", {"type": "enclosure", "plan": {"rect": [1.1, 1.3]}, "thickness": 0.15, "height": 1.25, "interior": False, "glass": True,
                     "faces": {"0": [{"openings": [{"at": 0, "width": 0.6, "sill": 0.38, "springing": 0.8, "head": ROUND, "foot": ROUND}]}],
                               "1": [{"openings": []}], "2": [{"openings": []}], "3": [{"openings": []}]},
                     "at": dorm, "_about": "the lower ring of dormers round each bell: an oval light in a white frame"})
add("bell dormer hoods", {"type": "dome", "sides": 12, "radius": 0.68, "thickness": 0, "sweep": 0.5, "head": {"profile": "semicircular"},
                          "at": [[x, y, z, r4(yaw + PI)] for x, y, z, yaw in hoods], "_about": "the hood over each"})
add("bell oculi", {"type": "enclosure", "plan": {"rect": [0.9, 0.8]}, "thickness": 0.12, "height": 0.85, "interior": False, "glass": True,
                   "faces": {"0": [{"openings": [{"at": 0, "width": 0.5, "sill": 0.3, "springing": 0.45, "head": ROUND, "foot": ROUND}]}],
                             "1": [{"openings": []}], "2": [{"openings": []}], "3": [{"openings": []}]},
                   "at": dorm2, "_about": "the upper ring: four round oeils-de-boeuf"})

# ---- THE ROOFS: tall mansards over the ranges and the wings (dormers in their lower slopes), the Mittelbau's high hipped
# roof over the three halls, a leaded flat between the ranges where the light wells are
MP = {"form": "mansard", "lowerPitch": 62, "breakH": 4.0, "pitch": 25, "overhang": 0.45}
add("north range roof", {"type": "roof", **MP, "width": r4(LZN - BZ0), "length": r4(EX0 - WX1 + 7.2), "at": [[r4((BX0 + BX1) / 2), EAVE, r4((BZ0 + LZN) / 2), Q]],
                         "_about": "the north range's mansard, its hipped ends tucked under the wings' roofs"})
add("south range roof", {"type": "roof", **MP, "width": r4(BZ1 - LZS), "length": r4(EX0 - WX1 + 7.2), "at": [[r4((BX0 + BX1) / 2), EAVE, r4((LZS + BZ1) / 2), Q]],
                         "_about": "the south range's mansard"})
add("wing roofs", {"type": "roof", **MP, "width": r4(WX1 - WX0), "length": r4(WZ1 - WZ0 + 2.0), "at": [[r4((WX0 + WX1) / 2), EAVE, r4((WZ0 + WZ1) / 2), 0], [r4((EX0 + EX1) / 2), EAVE, r4((WZ0 + WZ1) / 2), 0]],
                   "_about": "the wings' mansards, running into the towers' bells"})
add("middle leads", {"type": "prism", "plan": {"rect": [r4(BX1 - BX0), r4(LZS - LZN)]}, "height": 0.35, "flatRoof": True, "at": [[r4((BX0 + BX1) / 2), EAVE, r4((LZN + LZS) / 2), 0]],
                     "_about": "the leaded flat between the ranges' roofs (over the light wells)"})
MRISE = 10.0
add("mittelbau roof", {"type": "roof", "form": "hip", "width": r4(MX1 - MX0), "length": r4(BZ1 - BZ0), "pitch": r4(math.degrees(math.atan2(MRISE, (MX1 - MX0) / 2))), "overhang": 0.45,
                       "at": [[r4(MXC), EAVE, r4((BZ0 + BZ1) / 2), 0]], "_about": "the Mittelbau's high hipped roof over the three halls, its ridge 34 m over the island"})
# the dormers: in the lower slopes of the mansards, on every other axis; and on the Mittelbau's
tp = math.tan(math.radians(62)); s0, s1 = 0.75, 2.3; dW, dH = 1.5, 1.75
yb = EAVE + s0 * tp - 0.35
dorms, droofs = [], []
def dormer_row(us, along_x, line, out):
    """dormers along a face line (x or z constant = line), `out` the outward sign"""
    for u in us:
        m = line - out * (s0 + s1) / 2
        x, z = (u, m) if along_x else (m, u)
        yaw = (0 if out > 0 else PI) if along_x else (Q if out > 0 else -Q)
        dorms.append([r4(x), r4(yb), r4(z), r4(yaw)])
        droofs.append([r4(x), r4(yb + dH), r4(z), r4(yaw)])
dormer_row([b for i, b in enumerate(BAYS) if not (MX0 - 0.5 < b < MX1 + 0.5) and i % 2 == 0], True, BZ1, 1)
dormer_row([b for i, b in enumerate(BAYS) if not (MX0 - 0.5 < b < MX1 + 0.5) and i % 2 == 0], True, BZ0, -1)
dormer_row([-16.4, -9.8, 10.0, 16.6], False, WX0, -1)
dormer_row([-16.4, -9.8, 10.0, 16.6], False, EX1, 1)
dormer_row([-13.1, -6.5, 6.7, 13.3], False, WX1, 1)
dormer_row([-13.1, -6.5, 6.7, 13.3], False, EX0, -1)
add("dormers", {"type": "enclosure", "plan": {"rect": [dW, r4(s1 - s0)]}, "thickness": 0.2, "height": dH, "interior": False, "glass": True,
                "faces": {"0": [{"openings": [{"at": 0, "width": 0.8, "sill": 0.35, "springing": 1.15, "head": SEG}]}],
                          "1": [{"openings": []}], "2": [{"openings": []}], "3": [{"openings": []}]},
                "at": dorms, "_about": "the dormers in the mansards' steep lower slopes, a segmental light each"})
add("dormer roofs", {"type": "roof", "form": "hip", "width": dW, "length": r4(s1 - s0), "pitch": 45, "overhang": 0.12, "at": droofs})
mdz = BZ1 - 3.6
add("mittelbau dormers", {"type": "enclosure", "plan": {"rect": [1.8, 2.4]}, "thickness": 0.2, "height": 2.2, "interior": False, "glass": True,
                          "faces": {"0": [{"openings": [{"at": 0, "width": 0.9, "sill": 0.4, "springing": 1.3, "head": ROUND}]}],
                                    "1": [{"openings": []}], "2": [{"openings": []}], "3": [{"openings": []}]},
                          "at": [[r4(MXC), r4(EAVE + 3.0), r4(mdz), 0], [r4(MXC), r4(EAVE + 3.0), r4(BZ0 + 3.6), PI]],
                          "_about": "the round-headed dormer on the Mittelbau's roof, over each front's middle"})
add("mittelbau dormer roofs", {"type": "roof", "form": "hip", "width": 2.0, "length": 2.6, "pitch": 48, "overhang": 0.12,
                               "at": [[r4(MXC), r4(EAVE + 5.2), r4(mdz), 0], [r4(MXC), r4(EAVE + 5.2), r4(BZ0 + 3.6), PI]]})
add("chimneys", {"type": "box", "width": 0.9, "length": 0.65, "height": 6.4,
                 "at": [[x, r4(EAVE + 1.0), z, 0] for x in (-17.5, -12.0, 11.0, 17.0) for z in (-9.9, 10.5)] + [[-25.2, EAVE + 1.0, z, 0] for z in (-12, 12)] + [[25.0, EAVE + 1.0, z, 0] for z in (-12, 12)],
                 "_about": "the chimney stacks through the mansards' tops"})

# ---- THE LESENES: white pilaster strips through the three storeys over the ground floor, between every two axes of the
# fronts and the towers (the photographs' white bands); the ground floor's own rusticated strips on the corners
LH = r4(EAVE - LV[1] - 0.35)
def lesenes_front(line, xs, out):
    for a, b in zip(xs, xs[1:]):
        LEAD.append([r4((a + b) / 2), LV[1], r4(line + out * 0.07), 0])
lesenes_front(BZ1, BAYS, 1); lesenes_front(BZ0, BAYS, -1)
for x in (BX0 + 0.45, BX1 - 0.45): LEAD += [[r4(x), LV[1], r4(BZ1 + 0.07), 0], [r4(x), LV[1], r4(BZ0 - 0.07), 0]]
wz = [z for z in [r4(0.1 + 3.3 * k) for k in range(-6, 7)] if abs(z) < 19.0]
for line, out, blk in ((WX0, -1, (CZ0 - 2.4, CZ1 + 2.2)), (EX1, 1, (RZ0, RZ1))):
    zs = [z for z in wz if not (blk[0] - 0.6 < z < blk[1] + 0.6)]
    for a, b in zip(zs, zs[1:]):
        if b - a < 4: LEAD.append([r4(line + out * 0.07), LV[1], r4((a + b) / 2), Q])
add("lesenes", {"type": "box", "width": 0.62, "length": 0.14, "height": LH, "at": LEAD,
                "_about": "the white lesenes between the axes over the ground floor, fronts and towers"})

# ---- THE CHAPEL (1661-72, refitted 1723-33): the west risalit, two storeys high over the terrace, tall arched windows
# with an oculus over each; its two little side wings; the mansard roof and the Dachreiter -- a slate-hung square, an
# octagonal stage with the clocks, the slate bell, the lantern and the needle spire with its gilt finial, 43 m up
CXM, CZM = (CX0 + CX1) / 2, (CZ0 + CZ1) / 2
CH_T = [HS[0], 7.6, 15.0 - HS[0] - 7.6]          # the ground floor, the tall windows, the oculi
def chapel_side(face):
    xs = [-38.7]
    def f(j, h):
        if j == 0: return [{**WIN(at_on(face, CX0, CX1, CZ0, CZ1, x), 0), "width": 1.3} for x in xs]
        if j == 1: return [{"at": at_on(face, CX0, CX1, CZ0, CZ1, x), "width": 1.6, "sill": 1.0, "springing": 5.6, "head": ROUND, "surround": {"keystone": True}} for x in xs]
        return [{"at": at_on(face, CX0, CX1, CZ0, CZ1, x), "width": 1.2, "sill": 0.75, "springing": 0.75, "head": ROUND, "foot": ROUND} for x in xs]
    return f
def chapel_west(j, h):
    zs = [CZM - 3.4, CZM, CZM + 3.4]
    if j == 0: return [{**WIN(at_on(3, CX0, CX1, CZ0, CZ1, z), 0), "width": 1.3} for z in zs]
    if j == 1: return [{"at": at_on(3, CX0, CX1, CZ0, CZ1, z), "width": 1.7, "sill": 1.0, "springing": 5.6, "head": ROUND, "surround": {"keystone": True}} for z in zs]
    return [{"at": at_on(3, CX0, CX1, CZ0, CZ1, z), "width": 1.2, "sill": 0.75, "springing": 0.75, "head": ROUND, "foot": ROUND} for z in zs]
encl("chapel", CX0, CX1, CZ0, CZ1, TT, CH_T, {0: chapel_side(0), 2: chapel_side(2), 3: chapel_west,
                                             1: lambda j, h: [DOOR(at_on(1, CX0, CX1, CZ0, CZ1, 1.0), 1.6, 3.0)] if j < 2 else []}, skip=(1,),
     about="the Schlosskapelle: one room two storeys high, the altar at the west end, the princely gallery at the east; tall arched windows, an oculus over each")
for nm, zc, face in (("north", -6.5, 2), ("south", 8.5, 0)):
    encl(f"chapel {nm} wing", -36.5, -31.3, zc - 1.2, zc + 1.2, TT, [4.8, 5.2],
         {face: lambda j, h: [WIN(0, 0) if j == 0 else {"at": 0, "width": 1.3, "sill": 1.0, "springing": 3.4, "head": ROUND, "surround": {"keystone": True}}]},
         t=0.5, interior=False, about="one of the chapel's two low side wings (OSM: to 18 m with their roofs)")
add("chapel side wing roofs", {"type": "roof", "form": "hip", "width": 2.4, "length": 5.2, "pitch": 40, "overhang": 0.3,
                               "at": [[-33.9, TT + 10.0, -6.5, Q], [-33.9, TT + 10.0, 8.5, Q]]})
add("chapel roof", {"type": "roof", "form": "mansard", "lowerPitch": 66, "breakH": 5.0, "pitch": 32, "overhang": 0.45, "width": r4(CZ1 - CZ0), "length": r4(CX1 - CX0 + 1.0),
                    "at": [[r4(CXM + 0.5), CH_EAVE, r4(CZM), Q]], "_about": "the chapel's mansard roof, 29 m over the island"})
DR = (-31.85, 1.0)
add("dachreiter base", {"type": "box", "width": 4.4, "length": 4.4, "height": 8.0, "at": [[DR[0], TT + 18.5, DR[1], 0]],
                        "courses": [{"y": 7.6, "h": 0.4, "out": 0.15, "profile": "cornice"}], "_about": "the Dachreiter's slate-hung square base, rising from the ridge"})
DRY = TT + 26.5
add("dachreiter stage", {"type": "enclosure", "plan": {"sides": 8, "radius": 2.1}, "thickness": 0.25, "height": 3.0, "interior": False, "glass": True,
                         "openings": [{"at": 0, "width": 0.7, "sill": 0.5, "springing": 1.9, "head": ROUND}], "at": [[DR[0], DRY, DR[1], r4(math.pi / 8)]],
                         "_about": "the octagonal stage: an arched opening in every face"})
add("dachreiter clocks", comp("clock-dial", {"R": 0.55, "hour": 10, "minute": 10},
                              [[r4(DR[0] + 2.25 * math.sin(a)), r4(DRY + 2.25), r4(DR[1] + 2.25 * math.cos(a)), r4(a)] for a in (0, Q, PI, -Q)],
                              _about="the clocks on four faces of the octagon, over the arches"))
add("dachreiter helm", comp("baroque-helm", {"sides": 8, "R": 2.0, "footH": 0.4, "profile": "bell", "waist": 0.8, "lift": 0.5, "LR": 0.75, "LH": 1.5, "glazed": 0,
                                             "lanterns": "two", "R2": 0.85, "L2R": 0.32, "L2H": 0.8, "spikeProfile": "trigonal", "spikeH": 3.2, "ballR": 0.32, "crossH": 0.9},
                            [[DR[0], r4(DRY + 3.0), DR[1], r4(math.pi / 8)]],
                            _about="its slate helm: the bell, an open lantern, a second small bell and lantern, the needle spire, the gilt ball and finial -- 43 m up"))

# ---- THE SPEISESAAL RISALIT (east): the ground floor's vestibule with the door onto the terrace's east lobe, over it the
# Speisesaal two storeys high (tall arched lights with oculi), the top storey, a hipped roof
RXM, RZM = (RX0 + RX1) / 2, (RZ0 + RZ1) / 2
def ris(face, ws):
    def f(j, h):
        if j == 0:
            out = [{**WIN(at_on(face, RX0, RX1, RZ0, RZ1, w), 0)} for w in ws if not (face == 1 and abs(w - RZM) < 1)]
            return out + ([{**PORTAL(at_on(1, RX0, RX1, RZ0, RZ1, 0.0)), "width": 2.0}] if face == 1 else [])
        if j == 1:
            return [{"at": at_on(face, RX0, RX1, RZ0, RZ1, w), "width": 1.8, "sill": 0.9, "springing": 5.7, "head": ROUND, "surround": {"keystone": True}} for w in ws]
        if j == 2:
            return [{"at": at_on(face, RX0, RX1, RZ0, RZ1, w), "width": 1.2, "sill": 0.65, "springing": 0.65, "head": ROUND, "foot": ROUND} for w in ws]
        return [WIN(at_on(face, RX0, RX1, RZ0, RZ1, w), 3) for w in ws]
    return f
RWX = [31.0, 34.4, 37.8, 41.2]
encl("risalit", RX0, RX1, RZ0, RZ1, TT, R_TIERS, {1: ris(1, [-3.4, 0.05, 3.5]), 0: ris(0, RWX), 2: ris(2, RWX),
                                                  3: lambda j, h: [DOOR(at_on(3, RX0, RX1, RZ0, RZ1, 0.0), 2.0, 3.2 if j else 2.9)] if j != 2 else []}, skip=(3,),
     about="the east risalit: the vestibule on the ground floor, the Speisesaal over it two storeys high, the top storey")
add("risalit roof", {"type": "roof", "form": "hip", "width": r4(RZ1 - RZ0), "length": r4(RX1 - RX0 + 1.5), "pitch": 42, "overhang": 0.45,
                     "at": [[r4(RXM + 0.75), R_EAVE, r4(RZM), Q]], "_about": "the risalit's hipped roof"})

# ---- PARTY WALLS: where two blocks stand back to back, the strip from one wall's middle to the other's is the rooms'
# (finish.js: the doorways' reveals inside)
for i, (x0, x1, z0, z1, h) in enumerate([(BX0 - T / 2, BX0 + T / 2, BZ0, BZ1, sum(HS)), (BX1 - T / 2, BX1 + T / 2, BZ0, BZ1, sum(HS)),
                                          (CX1 - T / 2, CX1 + T / 2, CZ0, CZ1, 15.0), (RX0 - T / 2, RX0 + T / 2, RZ0, RZ1, sum(R_TIERS))]):
    add(f"party wall {i + 1}", {"type": "interior", "plan": {"rect": [r4(x1 - x0), r4(z1 - z0)]}, "height": h, "at": [[r4((x0 + x1) / 2), TT, r4((z0 + z1) / 2), 0]]})
add("tower passages", {"type": "interior", "plan": {"rect": [1.6, 2.2]}, "height": sum(HS),
                       "at": [[cx, TT, r4(cz - math.copysign(TR - 0.55, cz)), 0] for cx, cz in TOWERS.values()], "_about": "the doorways from the wings into the towers"})

# ---- THE INSIDE
def iwall(name, a, b, doors, about=None, y0=TT, tiers=HS, t=IT):
    """an inner wall from a to b (x, z), its middle on the line: `doors` [(distance from a, storeys, width)]"""
    L = math.dist(a, b); dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    ts = []
    for j, h in enumerate(tiers):
        ops = [DOOR(d - L / 2, w, 2.9 if w > 1.5 else 2.6) for d, js, w in doors if j in js]
        ts.append({"h": h, "openings": ops} if j < len(tiers) - 1 else {"openings": ops})
    d = {"type": "wall", "width": r4(L), "height": r4(sum(tiers)), "thickness": t, "tiers": ts, "glass": False,
         "at": [[r4((a[0] + b[0]) / 2 - t / 2 * dz), y0, r4((a[1] + b[1]) / 2 + t / 2 * dx), r4(math.atan2(-dz, dx))]]}   # (a wall's `at` is its face: its middle on the line)
    if about: d["_about"] = about
    return add(name, d)
ALL, NO2 = (0, 1, 2, 3), (0, 1, 3)
IX0, IX1, IZ0, IZ1 = BX0 + T, BX1 - T, BZ0 + T, BZ1 - T         # the main body's inside
along = lambda xs: [(x - IX0, js, w) for x, js, w in xs]
LDOORS = [(-18.0, ALL, 1.3), (-12.1, ALL, 1.3), (MXC, NO2, 2.0), (11.0, ALL, 1.3), (17.6, ALL, 1.3)]
iwall("north hall wall", (IX0, LZN), (IX1, LZN), along(LDOORS), about="between the north range and the middle: the Billardsaal's south wall in the Mittelbau")
iwall("south hall wall", (IX0, LZS), (IX1, LZS), along(LDOORS), about="between the middle and the south range: the Monstroesensaal's north wall")
cross = lambda x, js_mid, nm, ab: iwall(nm, (x, IZ0), (x, IZ1), [(-9.5 - IZ0, js_mid, 1.3), (4.4 - IZ0, js_mid if x in (MX0, MX1) else ALL, 1.3), (10.0 - IZ0, js_mid, 1.3)], about=ab)
cross(WSX0, ALL, "west stair wall", "the west stair hall's west wall, on through the ranges")
cross(MX0, NO2, "mittelbau west wall", "the Mittelbau's west wall: the three halls' ends")
cross(MX1, NO2, "mittelbau east wall", "the Mittelbau's east wall")
cross(SX1, ALL, "east stair wall", "the east stair hall's east wall, on through the ranges")
# the wings: rooms in a row along the axis, a doorway in the middle of every cross wall (the enfilade), every storey
for nm, (x0, x1) in (("west", (WX0 + T, WX1 - T)), ("east", (EX0 + T, EX1 - T))):
    xm = (x0 + x1) / 2
    for k, z in enumerate((BZ0, LZN, LZS, BZ1)):
        iwall(f"{nm} wing wall {k + 1}", (x0, z), (x1, z), [((x1 - x0) / 2, ALL, 1.3)], about=f"a cross wall in the {nm} wing: the enfilade's doorway in its middle")
# the floors: every storey over the ground floor, the halls two storeys high (no floor at the second), the stair halls'
# wells; the towers' round floors; the chapel's gallery; the Speisesaal's floor and its ceiling
def slab(name, x0, x1, z0, z1, ks, well=None, about=None):
    d = {"type": "prism", "plan": {"rect": [r4(x1 - x0), r4(z1 - z0)]}, "height": SLAB, "flatRoof": False,
         "at": [[r4((x0 + x1) / 2), r4(LV[k] - SLAB), r4((z0 + z1) / 2), 0] for k in ks]}
    if well:   # (wx0, wx1, wz0, wz1) in the world
        d["plan"]["well"] = {"rect": [r4(well[1] - well[0]), r4(well[3] - well[2])], "at": [r4((well[0] + well[1]) / 2 - (x0 + x1) / 2), r4((well[2] + well[3]) / 2 - (z0 + z1) / 2)]}
    if about: d["_about"] = about
    return add(name, d)
E0, E1 = BX0 + T / 2, BX1 - T / 2; N0, S1 = BZ0 + T / 2, BZ1 - T / 2
slab("floors west bay", E0, WSX0, N0, S1, (1, 2, 3), about="the floors of the main body west of the west stair")
slab("floors west stair north", WSX0, MX0, N0, LZN, (1, 2, 3))
slab("floors west stair south", WSX0, MX0, LZS, S1, (1, 2, 3))
WWELL = (-14.25, -12.05, -3.6, 3.4)                  # (over the second flight: x -14.1..-12.2)
slab("floors west stair", WSX0, MX0, LZN, LZS, (1, 2, 3), well=WWELL, about="the west stair hall's floors, the well over the returning flights")
slab("floors mittelbau", MX0, MX1, N0, S1, (1, 3), about="the halls' floor on the principal floor; the top storey's floor over their ceilings")
slab("floors east stair north", MX1, SX1, N0, LZN, (1, 2, 3))
slab("floors east stair south", MX1, SX1, LZS, S1, (1, 2, 3))
EWELL = (8.95, 11.65, -3.9, 3.4)                     # (over the second flight: x 9.1..11.5)
slab("floors east stair", MX1, SX1, LZN, LZS, (1, 2, 3), well=EWELL, about="the great stair's hall: the floors round its well")
slab("floors east bay", SX1, E1, N0, S1, (1, 2, 3))
slab("floors west wing", WX0 + T / 2, WX1 - T / 2, WZ0 + T / 2, WZ1 - T / 2, (1, 2, 3))
slab("floors east wing", EX0 + T / 2, EX1 - T / 2, WZ0 + T / 2, WZ1 - T / 2, (1, 2, 3))
add("floors towers", {"type": "prism", "plan": {"sides": NS, "radius": r4(TR - T / 2)}, "height": SLAB, "flatRoof": False,
                      "at": [[cx, r4(LV[k] - SLAB), cz, 0] for cx, cz in TOWERS.values() for k in (1, 2, 3)], "_about": "the towers' round floors"})
add("floors risalit", {"type": "prism", "plan": {"rect": [r4(RX1 - RX0 - T), r4(RZ1 - RZ0 - T)]}, "height": SLAB, "flatRoof": False,
                       "at": [[RXM, r4(LV[1] - SLAB), RZM, 0], [RXM, r4(LV[3] - SLAB), RZM, 0]], "_about": "the Speisesaal's floor and the top storey's over its ceiling"})
GX = -32.3
add("chapel gallery", {"type": "prism", "plan": {"rect": [r4(CX1 + T / 2 - GX), r4(CZ1 - CZ0 - 2 * T)]}, "height": SLAB, "flatRoof": False,
                       "at": [[r4((CX1 + T / 2 + GX) / 2), r4(LV[1] - SLAB), CZM, 0]], "_about": "the princely gallery at the chapel's east end, on the principal floor, entered from the west wing"})
add("chapel gallery balustrade", {"type": "wall", "width": r4(CZ1 - CZ0 - 2 * T), "height": 1.0, "thickness": 0.22, "glass": False,
                                  "openings": {"pattern": str(int((CZ1 - CZ0 - 2 * T - 0.6) // 0.4)), "width": 0.22, "gap": 0.18, "sill": 0.18, "springing": 0.82, "head": FLAT, "glass": False},
                                  "at": [[r4(GX + 0.11), LV[1], CZM, -Q]], "_about": "its balustrade over the chapel"})
# THE STAIRS: dog-legs where the light wells are -- each storey's its own part (a repeated staircase's landings get
# railed over the next flight)
def dogleg(name, x0, z0, W, run, gap, about):
    for k in range(3):
        n = {0: 30, 1: 34, 2: 28}[k]
        add(f"{name} {k + 1}", {"type": "staircase", "rise": r4(HS[k] / n), "run": run, "soffit": 0.3, "flight": n // 2, "width": W,
                                "landing": {"depth": 2.0, "width": r4(2 * W + gap), "shift": r4(-(W / 2 + gap / 2)),
                                            "then": [{"from": "back", "at": r4(-(W / 2 + gap / 2)), "flight": n // 2, "width": W, "landing": {"depth": 1.0, "width": W}}]},
                                "at": [[x0, LV[k], z0, Q]], "_about": about if k == 0 else f"the {['', 'second', 'third'][k]} storey's"})
dogleg("great stair", 13.1, 3.4, 2.4, 0.3, 0.4, "the great stair in the east light well's place: up the hall toward the north, a landing, back up beside itself -- every storey")
dogleg("west stair", -10.95, 3.4, 1.9, 0.28, 0.3, "the west stair, in the west light well's place")

# THE HALLS' FURNISHING: THE TROPHIES -- red-deer antlers on carved boards round the Speisesaal (its 71), the Steinsaal
# and the Monstroesensaal (the abnormal ones), in two rows
def antler(s):
    beam = [[0.08, 0, 0.06], [0.3, 0.28, 0.18], [0.48, 0.7, 0.22], [0.52, 1.1, 0.14], [0.42, 1.42, 0.05]]
    tines = [[[0.3, 0.28, 0.18], [0.18, 0.42, 0.42]], [[0.42, 0.55, 0.21], [0.3, 0.7, 0.45]], [[0.5, 0.95, 0.2], [0.68, 1.15, 0.3]],
             [[0.52, 1.1, 0.14], [0.66, 1.42, 0.16]], [[0.42, 1.42, 0.05], [0.32, 1.62, 0.1]]]
    out = []
    for sx in (1, -1):
        out.append([[r4(sx * x * s), r4(y * s), r4(z * s)] for x, y, z in beam])
        out += [[[r4(sx * x * s), r4(y * s), r4(z * s)] for x, y, z in t] for t in tines]
    return out
TROPHY = []
def trophies_on(x0, z0, x1, z1, yaw, ys, step=2.1):
    L = math.dist((x0, z0), (x1, z1)); n = max(1, int(L // step))
    for i in range(n):
        f = (i + 0.5) / n
        for y in ys: TROPHY.append([r4(x0 + (x1 - x0) * f), r4(y), r4(z0 + (z1 - z0) * f), r4(yaw)])
ri0, ri1, rz0, rz1 = RX0, RX1 - T, RZ0 + T, RZ1 - T          # (an enclosure's wall stands inside its rect: its inner face T in)
# (the Speisesaal: in columns between the windows, four high, and one over every window; round the door from the wing)
ROWS = [LV[1] + 2.5, LV[1] + 4.0, LV[1] + 5.5, LV[1] + 7.0]
for x in (32.7, 36.1, 39.5):
    for y in ROWS: TROPHY += [[x, r4(y), r4(rz0 + 0.02), 0], [x, r4(y), r4(rz1 - 0.02), PI]]
for x in RWX:
    for z, yaw in ((rz0 + 0.02, 0), (rz1 - 0.02, PI)): TROPHY.append([x, r4(LV[1] + 7.0), r4(z), yaw])
for z in (-5.0, -1.68, 1.78, 5.1):
    for y in ROWS: TROPHY.append([r4(ri1 - 0.02), r4(y), z, -Q])
for z in (-3.4, 0.05, 3.5): TROPHY.append([r4(ri1 - 0.02), r4(LV[1] + 7.0), z, -Q])
for z in (-4.6, -2.6, 2.6, 4.6):
    for y in ROWS: TROPHY.append([r4(ri0 + 0.02), r4(y), z, Q])
for y in (LV[1] + 4.6, LV[1] + 6.2): TROPHY.append([r4(ri0 + 0.02), r4(y), 0.0, Q])
for zz0, zz1 in ((IZ0, LZN - IT / 2), (LZN + IT / 2, LZS - IT / 2), (LZS + IT / 2, IZ1)):   # (the halls' end walls: the Billardsaal, the Steinsaal, the Monstroesensaal)
    trophies_on(MX0 + IT / 2 + 0.02, zz0 + 1.2, MX0 + IT / 2 + 0.02, zz1 - 1.2, Q, (LV[1] + 5.0, LV[1] + 7.4), 2.4)
    trophies_on(MX1 - IT / 2 - 0.02, zz0 + 1.2, MX1 - IT / 2 - 0.02, zz1 - 1.2, -Q, (LV[1] + 5.0, LV[1] + 7.4), 2.4)
add("trophy boards", {"type": "box", "width": 0.42, "length": 0.08, "height": 0.55, "at": [[x, r4(y - 0.35), z, yaw] for x, y, z, yaw in TROPHY],
                      "_about": "the carved boards the trophies hang on"})
add("trophies", {"type": "bars", "w": 0.06, "h": 0.06, "kind": "iron", "paths": antler(0.75), "at": [[x, y, z, yaw] for x, y, z, yaw in TROPHY],
                 "_about": "the red-deer antlers round the halls: the Speisesaal's 71, the Steinsaal's, the Monstroesensaal's abnormal ones"})
add("hall chandeliers", {"type": "item", "item": "items/furniture/chandelier", "solid": False,
                         "at": [[r4(MXC), r4(LV[3] - 1.6), z, 0] for z in (-9.9, 0.25, 10.5)] + [[RXM, r4(LV[3] - 1.6), RZM, 0]],
                         "_about": "a chandelier in each of the four halls"})
add("billiard table", {"type": "item", "item": "items/furniture/plain-table", "at": [[r4(MXC), LV[1], -9.9, 0]], "_about": "the Billardsaal's table"})
add("dining tables", {"type": "item", "item": "items/furniture/refectory-table", "at": [[r4(RXM - 2.6), LV[1], RZM, Q], [r4(RXM + 2.6), LV[1], RZM, Q]],
                      "_about": "the Speisesaal's long tables"})
add("federzimmer bed", {"type": "item", "item": "items/furniture/four-poster", "at": [[-25.2, LV[1], 12.5, PI]],
                        "_about": "the Federbett of the Federzimmer (the west wing's south rooms on the principal floor): its hangings of two million feathers"})
add("chapel altar", {"type": "box", "width": 1.0, "length": 2.6, "height": 1.0, "at": [[r4(CX0 + T + 0.9), TT, r4(CZM), 0]], "_about": "the altar at the chapel's west end"})
add("chapel retable", {"type": "box", "width": 0.5, "length": 3.4, "height": 6.5, "at": [[r4(CX0 + T + 0.25), r4(TT + 1.0), r4(CZM), 0]], "_about": "the retable over it"})
add("chapel pews", {"type": "item", "item": "items/furniture/bench", "at": [[r4(x), TT, r4(CZM + s * 2.1), Q] for x in (-37.0, -35.6, -34.2, -32.8) for s in (-1, 1)],
                    "_about": "the benches"})

# ---- THE BALCONY over the south portal
add("balcony", {"type": "box", "width": 4.6, "length": 1.5, "height": 0.35, "at": [[r4(MXC), r4(LV[1] - 0.35), r4(BZ1 + 0.75), 0]], "walked": True,
                "_about": "the balcony over the south portal, before the Monstroesensaal's middle window"})
add("balcony balustrade", {"type": "wall", "width": 4.6, "height": 1.0, "thickness": 0.2, "glass": False,
                           "openings": {"pattern": "10", "width": 0.24, "gap": 0.18, "sill": 0.2, "springing": 0.82, "head": FLAT, "glass": False},
                           "at": [[r4(MXC), LV[1], r4(BZ1 + 1.4), 0]]})
add("balcony balustrade ends", {"type": "wall", "width": 1.3, "height": 1.0, "thickness": 0.2, "glass": False,
                                "openings": {"pattern": "3", "width": 0.24, "gap": 0.18, "sill": 0.2, "springing": 0.82, "head": FLAT, "glass": False},
                                "at": [[r4(MXC - 2.1), LV[1], r4(BZ1 + 0.7), Q], [r4(MXC + 2.1), LV[1], r4(BZ1 + 0.7), -Q]]})

# ---- THE TERRACE (relation 20408145: the podium 5 m high, of grey sandstone): the north and south bulges round the cours
# d'honneur, the east and west lobes; doors and windows of the vaults inside it in its face; the balustrade round its
# edge with piers, vases, putti and huntsmen; the ramps north and south; the curved stairs down the lobes
TERRACE = [(-18.3, 44.2), (-41.8, 44.3), (-42.3, 20.1), (-44.9, 18.3), (-47.6, 15.1), (-49.4, 9.4), (-49.5, -8.9), (-48.3, -12.9), (-44.1, -17.9), (-43.1, -18.6),
           (-43.6, -43.6), (-20.5, -43.6), (-17.5, -46.9), (-15.4, -48.1), (-13.0, -48.7), (11.5, -48.6), (14.0, -47.9), (16.2, -46.7), (19.1, -43.7), (42.9, -43.7),
           (42.8, -19.8), (46.5, -17.8), (49.9, -13.9), (51.9, -8.3), (51.8, 8.2), (49.9, 13.5), (45.5, 18.0), (42.6, 19.6), (42.5, 44.1), (18.2, 44.1),
           (15.3, 47.2), (13.2, 48.4), (10.9, 49.1), (-10.8, 49.4), (-14.4, 48.3), (-17.1, 46.2)]
add("terrace", {"type": "prism", "plan": {"points": [list(p) for p in TERRACE]}, "height": TT, "flatRoof": True, "walked": True, "at": [[0, 0, 0, 0]],
                "courses": [{"y": 0, "h": 0.5, "out": 0.12, "profile": "plinth"}, {"y": r4(TT - 0.35), "h": 0.35, "out": 0.14, "profile": "cornice"}],
                "_about": "the terrace the castle stands on: OSM's podium (relation 20408145), 5 m of grey sandstone over the island"})
area = sum(TERRACE[i][0] * TERRACE[(i + 1) % len(TERRACE)][1] - TERRACE[(i + 1) % len(TERRACE)][0] * TERRACE[i][1] for i in range(len(TERRACE)))
def edges(pts):
    out = []
    for i in range(len(pts)):
        p, q = pts[i], pts[(i + 1) % len(pts)]; L = math.dist(p, q)
        ex, ez = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        nx, nz = (ez, -ex) if area > 0 else (-ez, ex)        # (outward)
        out.append((p, q, L, ex, ez, nx, nz))
    return out
TE = edges(TERRACE)
# the vaults' doors and windows in the terrace's face (OSM's doors; windows between them on the long faces)
TDOORS = [(-17.5, -46.9), (-43.2, -24.8), (-43.3, -28.6), (-43.4, -36.8), (-43.5, -40.2), (-36.6, -43.6), (-26.5, -43.6), (-8.7, -48.7), (36.4, -43.7),
          (26.0, -43.7), (42.8, -37.1), (42.8, -30.0), (42.6, 25.7), (42.6, 29.5), (42.5, 33.4), (36.0, 44.1), (25.3, 44.1), (-26.1, 44.2), (-36.8, 44.3),
          (-49.4, 5.4), (-49.5, 1.8), (-49.6, -1.4), (52.0, -3.7), (52.0, 3.6), (52.0, 0.1)]
GATES = [(42.5, 41.1), (42.5, 36.8)]
def on_face(pts, w, out=0.04):
    res = []
    for x, z in pts:
        best = min(TE, key=lambda e: abs((x - e[0][0]) * e[5] + (z - e[0][1]) * e[6]) + 10 * max(0, -((x - e[0][0]) * e[3] + (z - e[0][1]) * e[4])) + 10 * max(0, (x - e[0][0]) * e[3] + (z - e[0][1]) * e[4] - e[2]))
        (p, q, L, ex, ez, nx, nz) = best
        u = (x - p[0]) * ex + (z - p[1]) * ez
        res.append([r4(p[0] + ex * u + nx * out), 0, r4(p[1] + ez * u + nz * out), r4(math.atan2(nx, nz))])
    return res
twin = []
for (p, q, L, ex, ez, nx, nz) in TE:
    if L < 14: continue
    n = int(L // 5.5)
    for i in range(n):
        u = (i + 0.5) * L / n
        x, z = p[0] + ex * u, p[1] + ez * u
        if any(math.dist((x, z), d) < 2.6 for d in TDOORS + GATES) or abs(x) < 10 and abs(z) > 40: continue
        twin.append((x, z))
add("terrace doors", {"type": "box", "width": 1.3, "length": 0.08, "height": 2.5, "at": on_face(TDOORS, 1.3), "_about": "the doors into the vaults under the terrace (OSM)"})
add("terrace gates", {"type": "box", "width": 2.6, "length": 0.08, "height": 3.0, "at": on_face(GATES, 2.6), "_about": "the carriage gates into the terrace's south-east corner"})
add("terrace windows", {"type": "box", "width": 1.1, "length": 0.08, "height": 1.4, "at": [[x, 1.3, z, yaw] for x, _, z, yaw in on_face(twin, 1.1)],
                        "_about": "the vaults' windows in the terrace's face"})
# the stairs: down each lobe, three flights of eleven steps a quarter (OSM's steps), the landings between them
STAIRS = {"west south": [((-50.9, 7.1), (-50.7, 11.3)), ((-49.9, 14.0), (-48.0, 17.2)), ((-45.8, 19.5), (-42.3, 21.7))],
          "west north": [((-51.2, -4.8), (-51.1, -9.1)), ((-50.3, -12.0), (-48.5, -15.4)), ((-46.6, -17.7), (-43.1, -20.2))],
          "east north": [((53.6, -6.1), (53.2, -10.1)), ((52.0, -13.5), (49.6, -16.9)), ((47.0, -19.4), (42.8, -21.4))],
          "east south": [((53.5, 6.0), (53.0, 10.1)), ((51.7, 13.4), (49.4, 16.8)), ((46.7, 19.1), (42.6, 21.2))]}
SW_ = 2.4
STAIR_TOPS = []
for nm, fl in STAIRS.items():
    for k, ((ax, az), (bx, bz)) in enumerate(fl):
        L = math.dist((ax, az), (bx, bz)); d = ((bx - ax) / L, (bz - az) / L)
        base, top = k * TT / 3, (k + 1) * TT / 3
        land = 0
        if k < 2:
            (cx_, cz_), _ = fl[k + 1]
            land = r4(max(0.6, (cx_ - bx) * d[0] + (cz_ - bz) * d[1] + 0.5))
        f = flight((ax, az), d, SW_, r4(base), r4(top), run=r4(L / 11), rise=r4(TT / 33), landing=land, **({"ground": 0} if k else {}))
        # (the flight's width lies to its right: shift it so OSM's line is its middle)
        add(f"stair {nm} {k + 1}", {**f, "_about": "a flight of the curved stair down the lobe" if k == 0 else "its next flight"})
        if k < 2:
            (cx_, cz_), _ = fl[k + 1]
            ex_, ez_ = bx + d[0] * land, bz + d[1] * land
            px, pz = -d[1], d[0]
            (cx2, cz2), (dx2, dz2) = fl[k + 1]
            L2 = math.dist((cx2, cz2), (dx2, dz2)); d2 = ((dx2 - cx2) / L2, (dz2 - cz2) / L2); p2 = (-d2[1], d2[0])
            quad = [(bx + px * SW_ / 2, bz + pz * SW_ / 2), (ex_ + px * SW_ / 2, ez_ + pz * SW_ / 2), (cx2 + p2[0] * SW_ / 2, cz2 + p2[1] * SW_ / 2),
                    (cx2 - p2[0] * SW_ / 2, cz2 - p2[1] * SW_ / 2), (ex_ - px * SW_ / 2, ez_ - pz * SW_ / 2), (bx - px * SW_ / 2, bz - pz * SW_ / 2)]
            add(f"stair {nm} landing {k + 1}", {"type": "prism", "plan": {"points": [[r4(x), r4(z)] for x, z in quad]}, "height": r4(top), "flatRoof": True, "walked": True,
                                                "at": [[0, 0, 0, 0]], "_about": "the landing where the stair turns with the lobe"})
        else:
            STAIR_TOPS.append((bx, bz))
# the ramps (Auffahrten): north and south, sloping from the terrace's bulges to the island, flaring at their feet
def ramp(name, zt, zf, top_hw, foot_hw, xc):
    s = 1 if zf > zt else -1
    zs = [zt, zt + s * 17.4, zt + s * 25.4, zt + s * 31.4, zf]
    hw = [top_hw[0], top_hw[0], top_hw[0] + 1.0, top_hw[0] + 2.6, foot_hw[0]]
    he = [top_hw[1], top_hw[1], top_hw[1] + 1.2, top_hw[1] + 3.0, foot_hw[1]]
    west = [(r4(xc - w), r4(z)) for w, z in zip(hw, zs)]; east = [(r4(xc + w), r4(z)) for w, z in zip(he, zs)]
    sz = r4((TT - 0.1) / (zt - zf)); H = r4(TT - sz * zt)
    add(name, {"type": "prism", "plan": {"points": [list(p) for p in west + east[::-1]]}, "height": H, "slope": [0, sz], "walked": True, "at": [[0, 0, 0, 0]],
               "_about": "the Auffahrt: the carriage ramp from the island up to the terrace, its sides of sandstone"})
    for side, line, o in (("west", west, 1), ("east", east, -1)):
        inner = [(x + o * 0.45, z) for x, z in line]
        add(f"{name} parapet {side}", {"type": "prism", "plan": {"points": [list(p) for p in line + inner[::-1]]}, "height": r4(H + 1.0), "slope": [0, sz], "at": [[0, 0, 0, 0]],
                                       "_about": "its parapet, sloping with it"})
    return west, east
NRW, NRE = ramp("north ramp", -48.6, -84.4, (4.3, 4.3), (8.8, 8.8), -1.3)
SRW, SRE = ramp("south ramp", 49.3, 85.9, (4.25, 4.25), (8.85, 8.85), -0.35)
RAMP_TOPS = [((-1.3, -48.6), 8.8), ((-0.35, 49.3), 8.7)]
# the balustrade round the edge: a pierced parapet between piers, broken for the ramps and the stairs
BAL = []; PIERS = []
for i, (p, q, L, ex, ez, nx, nz) in enumerate(TE):
    runs = [(0.0, L)]
    for (gx, gz), gw in [(t, 3.4) for t in STAIR_TOPS] + RAMP_TOPS:
        u = (gx - p[0]) * ex + (gz - p[1]) * ez; v = (gx - p[0]) * nx + (gz - p[1]) * nz
        if abs(v) < 1.8 and -gw / 2 < u < L + gw / 2:
            runs = [r for a, b in runs for r in ((a, min(b, u - gw / 2)), (max(a, u + gw / 2), b))]
    for a, b in runs:
        if b - a < 0.9: continue
        m = (a + b) / 2; w = b - a
        x, z = p[0] + ex * m - nx * 0.15, p[1] + ez * m - nz * 0.15
        k = max(1, int((w - 0.5 + 0.16) // 0.4))
        nm = f"terrace balustrade {len(BAL) + 1}"
        add(nm, {"type": "wall", "width": r4(w), "height": 1.0, "thickness": 0.3, "glass": False,
                 "openings": {"pattern": str(k), "width": 0.24, "gap": 0.16, "sill": 0.22, "springing": 0.82, "head": FLAT, "glass": False},
                 "at": [[r4(x), TT, r4(z), r4(math.atan2(nx, nz))]]})
        BAL.append(nm)
        for u in (a, b):
            PIERS.append((r4(p[0] + ex * u - nx * 0.3), r4(p[1] + ez * u - nz * 0.3), math.atan2(nx, nz)))
        if w > 9:
            n = int(w // 6.5)
            for j in range(1, n + 1):
                u = a + w * j / (n + 1)
                PIERS.append((r4(p[0] + ex * u - nx * 0.3), r4(p[1] + ez * u - nz * 0.3), math.atan2(nx, nz)))
# (one pier where two runs meet at a corner)
uniq = []
for x, z, yaw in PIERS:
    if all(math.dist((x, z), (a, b)) > 0.9 for a, b, _ in uniq): uniq.append((x, z, yaw))
PIERS = uniq
add("terrace piers", {"type": "box", "width": 0.6, "length": 0.6, "height": 1.2, "at": [[x, TT, z, r4(yaw)] for x, z, yaw in PIERS],
                     "courses": [{"y": 1.05, "h": 0.15, "out": 0.06, "profile": "cornice"}], "_about": "the balustrade's piers"})
# statues on the piers by the ramps and the stairs (putti and huntsmen), vases on the rest
def near_any(x, z, pts, r): return any(math.dist((x, z), p) < r for p in pts)
STAT_AT = [(x, z, yaw) for x, z, yaw in PIERS if near_any(x, z, [t for t, _ in RAMP_TOPS] + STAIR_TOPS, 6.0)]
VASE_AT = [(x, z, yaw) for x, z, yaw in PIERS if (x, z, yaw) not in STAT_AT]
add("vase feet", {"type": "column", "radius": 0.13, "height": 0.25, "sides": 10, "at": [[x, TT + 1.2, z, 0] for x, z, _ in VASE_AT]})
add("vases", {"type": "dome", "sides": 12, "radius": 0.24, "thickness": 0, "head": {"profile": "onion", "bulge": 1.35, "neck": 0.55},
              "at": [[x, TT + 1.45, z, 0] for x, z, _ in VASE_AT], "_about": "the stone vases on the balustrade's piers"})
STATS = {}
kinds = [("man", "striding", {"R": "items/weapons/spear"}, 0.8), ("woman", "contrapposto", {"L": "items/weapons/longbow"}, 0.8),
         ("man", "contrapposto", {}, 0.55), ("woman", "offering", {}, 0.55)]
for i, (x, z, yaw) in enumerate(STAT_AT):
    kd, pose, hold, sc = kinds[i % 4]
    STATS[f"terrace statue {i + 1}"] = statue((x, TT + 1.2, z), kind=kd, pose=pose, style="roman", stone="sandstone", scale=sc, seed=i + 3,
                                              face=r4(yaw - Q), **({"hold": hold} if hold else {}))
# the two Piqueurs (huntsmen with their hounds' leashes and horns) on their pedestals at the south ramp's foot (OSM's
# artworks); vases on pedestals at the north ramp's
add("piqueurs", comp("pedestal", {"W": 1.4, "L": 1.1, "H": 1.9, "kind": "man", "style": "roman", "stone": "sandstone", "pose": "spear bearer", "scale": 1.0, "holdR": "items/weapons/spear"},
                     [[8.6, 0.1, 85.8, 0], [-9.1, 0.1, 85.9, 0]], _about="the two Piqueurs, the hunt's huntsmen, on their pedestals either side of the south ramp's foot"))
add("north ramp pedestals", {"type": "box", "width": 1.3, "length": 1.3, "height": 1.8, "at": [[-10.5, 0.1, -84.4, 0], [8.3, 0.1, -84.4, 0]],
                             "courses": [{"y": 1.6, "h": 0.2, "out": 0.08, "profile": "cornice"}]})
add("north ramp urns", {"type": "dome", "sides": 16, "radius": 0.55, "thickness": 0, "head": {"profile": "onion", "bulge": 1.3, "neck": 0.6},
                        "at": [[-10.5, 2.15, -84.4, 0], [8.3, 2.15, -84.4, 0]], "_about": "the great urns at the north ramp's foot"})

# ---- THE ISLAND (relation 124276's inner ring): its quay walls of sandstone, lawns, gravel walks; the trees; the eight
# guardhouses (white, pyramid roofs); the boat landings in the east and west coves; the bridges north and south; the
# causeway (the Schlossallee) to the shore
ISLAND = [[1.48, -124.73], [-3.04, -124.94], [-16.76, -116.65], [-16.67, -108.39], [-61.39, -107.99], [-60.72, -41.36], [-77.32, -41.2], [-77.12, -21.89],
          [-86.9, -21.8], [-92.12, -21.76], [-96.21, -20.03], [-99.56, -17.54], [-102.24, -13.83], [-104.35, -13.86], [-104.42, -5.41], [-96.67, -5.35], [-96.8, 9.79],
          [-104.6, 9.72], [-104.68, 18.7], [-101.89, 18.72], [-97.15, 23.33], [-93.24, 25.17], [-77.47, 25.1], [-77.36, 46.36], [-61.81, 46.29], [-61.46, 111.79],
          [-15.97, 111.57], [-15.93, 118.41], [-3.44, 127.62], [3.63, 126.79], [15.39, 118.34], [15.47, 110.76], [61.33, 111.3], [62.07, 44.71], [77.26, 44.89],
          [77.5, 24.0], [89.96, 24.15], [94.32, 22.95], [98.17, 20.45], [101.01, 16.7], [103.91, 15.62], [103.97, 8.61], [97.82, 8.55], [97.97, -7.63], [103.86, -7.57],
          [103.93, -14.42], [101.62, -14.44], [97.2, -19.69], [93.72, -20.97], [89.36, -22.56], [76.67, -22.53], [76.62, -42.23], [59.7, -42.2], [59.51, -108.56],
          [14.46, -108.46], [14.43, -116.23]]
G0 = 0.1                                              # the island's ground (over the game's own, which it covers)
QD = 2.7                                              # (the quay walls reach under the water: -2.2 without a map, ground - 0.9 with one)
add("island", {"type": "prism", "plan": {"points": ISLAND}, "height": QD, "flatRoof": True, "walked": True, "at": [[0, r4(G0 - QD), 0, 0]],
               "_about": "the island in the Schlossteich (OSM relation 124276): its quay walls of sandstone standing in the water, lawn on top"})
CAUSE_END = 165.0
add("causeway", {"type": "prism", "plan": {"points": [[-7.8, 133.7], [-3.8, 130.8], [3.2, 130.9], [7.9, 134.3], [7.9, CAUSE_END], [-7.8, CAUSE_END]]}, "height": QD,
                 "flatRoof": True, "walked": True, "at": [[0, r4(G0 - QD), 0, 0]], "_about": "the causeway (the Schlossallee) south across the lake to the shore -- its first 35 m"})
grav = lambda nm, pts, about=None: add(nm, {"type": "prism", "plan": {"points": [[r4(x), r4(z)] for x, z in pts]}, "height": 0.05, "flatRoof": True, "walked": True,
                                            "at": [[0, G0, 0, 0]], **({"_about": about} if about else {})})
grav("gravel north walk", [(-4.5, -123.0), (3.0, -123.0), (8.0, -84.4), (-10.5, -84.4)], "the gravel walks: on the axis from the north bridge to the ramp")
grav("gravel south walk", [(-10.0, 85.9), (9.5, 85.9), (3.2, 126.0), (-3.8, 126.0)])
grav("gravel causeway", [(-4.0, 128.0), (3.6, 128.0), (3.6, CAUSE_END), (-4.0, CAUSE_END)])
for nm, s in (("west", -1), ("east", 1)):
    grav(f"gravel {nm} walk", [(s * (52.5 if s > 0 else 50.0), -4.0), (s * 76.0, -4.0), (s * 76.0, 4.0), (s * (52.5 if s > 0 else 50.0), 4.0)])
    add(f"gravel {nm} round", {"type": "prism", "plan": {"sides": 24, "radius": 10.0}, "height": 0.05, "flatRoof": True, "walked": True, "at": [[r4(s * 85.5), G0, 0.5, 0]],
                               "_about": "the round place on the lobe, before the boat landing"})
    grav(f"gravel {nm} landing walk", [(s * 94.0, -3.2), (s * (97.9 if s > 0 else 96.7), -3.2), (s * (97.9 if s > 0 else 96.7), 7.5), (s * 94.0, 7.5)])
grav("gravel terrace ring north", [(-56.0, -54.5), (56.0, -54.5), (56.0, -46.0), (19.5, -46.0), (14.0, -50.6), (-14.0, -50.6), (-20.0, -46.0), (-56.0, -46.0)],
     "the walk round the terrace's foot")
grav("gravel terrace ring south", [(-56.0, 46.0), (-19.0, 46.0), (-14.0, 51.0), (14.0, 51.0), (19.0, 46.0), (56.0, 46.0), (56.0, 54.5), (-56.0, 54.5)])
grav("gravel terrace ring west", [(-58.5, -46.0), (-53.0, -46.0), (-53.0, 46.0), (-58.5, 46.0)])
grav("gravel terrace ring east", [(55.0, -46.0), (60.5, -46.0), (60.5, 46.0), (55.0, 46.0)])
# trees (OSM's on the island and along the causeway, and the park's avenue on the north shore)
TREES = [(57.7, 107.0), (48.9, 107.0), (42.3, 106.7), (27.9, 106.2), (35.7, 106.4), (-56.9, 108.0), (20.1, 105.2), (-48.6, 108.0), (-42.1, 108.2), (-36.2, 108.2), (-30.3, 108.4),
         (-24.3, 108.6), (-18.4, 108.9), (58.9, 105.9), (-57.2, 99.4), (58.8, 97.3), (-57.3, 91.0), (58.1, 88.3), (-56.6, 81.7), (-56.1, 74.4), (58.1, 79.3), (-56.1, 65.2),
         (58.1, 70.4), (-55.9, 57.4), (58.1, 61.1), (-56.1, 49.4), (57.8, 54.0), (-73.2, 42.9), (-66.7, 42.8), (-61.8, 42.8), (-55.8, 43.1), (69.5, 46.7), (75.2, 46.9),
         (57.9, 45.4), (63.9, 45.7), (74.7, 41.8), (-72.8, 34.3), (74.9, 36.7), (-73.2, 27.9), (74.5, 30.7), (-90.7, 22.5), (-84.3, 22.2), (-78.3, 22.3), (-73.3, 22.1),
         (-95.8, 20.7), (74.9, 25.1), (89.5, 21.1), (82.2, 20.5), (95.0, 19.7), (-75.7, 12.4), (78.3, 15.6), (-75.7, -7.3), (76.3, -4.3), (-95.5, -14.7), (-89.9, -15.5),
         (-84.3, -16.2), (-78.1, -16.4), (-72.9, -16.9), (73.9, -13.4), (79.1, -13.4), (85.5, -13.3), (91.9, -13.3), (-73.0, -22.3), (74.1, -18.9), (-73.0, -27.1),
         (-73.1, -30.9), (73.7, -24.4), (-73.3, -36.1), (-67.6, -36.2), (-62.2, -36.2), (74.4, -29.7), (-56.7, -36.4), (63.3, -34.7), (68.8, -34.8), (74.3, -34.8),
         (57.9, -36.2), (-56.9, -43.5), (57.6, -42.0), (-56.9, -50.8), (57.7, -48.6), (-56.9, -59.0), (57.4, -53.9), (57.0, -60.1), (-56.8, -68.2), (57.0, -68.0),
         (-56.6, -75.6), (56.7, -75.1), (-57.0, -84.5), (56.4, -83.5), (-57.6, -92.9), (56.9, -92.6), (-57.9, -102.9), (-43.8, -103.3), (-49.5, -103.7), (-36.7, -103.1),
         (-30.8, -102.9), (-24.9, -103.0), (17.5, -102.8), (23.0, -103.0), (29.4, -102.8), (35.6, -102.8), (41.9, -102.8), (48.8, -102.5), (56.6, -102.2),
         (5.4, 121.6), (-5.9, 122.1), (8.8, 119.4), (-9.2, 119.5), (12.4, 117.3), (-13.0, 116.4), (-13.5, -114.5), (11.9, -114.4), (8.4, -116.0), (-9.8, -117.0),
         (5.1, -117.6), (-6.0, -119.3)]
TREES += [(s * 6.2, z) for s in (-1, 1) for z in range(138, 164, 6)]
SHORE_TREES = [(4.2, -137.5), (-6.7, -138.2), (-7.4, -144.1), (4.5, -144.7), (-7.6, -150.3), (4.3, -150.7), (-7.4, -157.5), (4.1, -157.3), (4.3, -163.3), (-7.6, -164.0),
               (56.1, -141.3), (55.4, -147.7), (54.9, -154.4), (54.4, -161.1), (-57.5, -140.0), (-57.4, -147.2), (-57.5, -153.1), (-57.5, -160.6)]
add("tree trunks", {"type": "column", "radius": 0.2, "height": 3.2, "sides": 8, "taper": 0.8,
                    "at": [[x, G0, z, 0] for x, z in TREES] + [[x, 0, z, 0] for x, z in SHORE_TREES], "_about": "the trees' trunks (OSM's trees)"})
add("tree crowns", {"type": "dome", "sides": 12, "radius": 2.3, "thickness": 0, "head": {"profile": "bell", "waist": 0.98, "lift": 0.5},
                    "at": [[x, r4(G0 + 2.6), z, 0] for x, z in TREES] + [[x, 2.5, z, 0] for x, z in SHORE_TREES], "_about": "their crowns, clipped round"})
# the guardhouses: eight little pavilions at the island's corners and lobes, white, under red pyramid roofs (OSM)
GUARD = [((-17.0, -8.5, -112.0, -103.0), 1, 4.4 + 2.0), ((6.4, 14.5, -112.0, -103.0), 3, -4.4 - 1.95), ((-15.2, -8.1, 107.4, 114.9), 1, -2.25),
         ((8.3, 15.1, 107.4, 114.9), 3, -2.25), ((-104.5, -96.5, -14.0, -5.0), 1, 2.0), ((-104.5, -96.5, 9.7, 18.9), 1, -2.0),
         ((96.7, 104.0, -14.5, -7.6), 3, -2.0), ((96.7, 104.0, 8.8, 15.5), 3, 2.0)]
GROOF = []
for i, ((x0, x1, z0, z1), df, dat) in enumerate(GUARD):
    wins = lambda face, L: (lambda j, h: [{"at": 0, "width": 1.1, "sill": 0.9, "springing": 2.3, "head": SEG, "surround": {"head": False}}])
    faces = {k: wins(k, 0) for k in range(4)}
    faces[df] = (lambda d: (lambda j, h: [DOOR(d, 1.2, 2.3)]))(r4(max(-1.5, min(1.5, dat))))
    encl(f"guardhouse {i + 1}", x0, x1, z0, z1, G0, [3.6], faces, t=0.5, about="a guardhouse (Wachhaus): one room, white walls, a door toward the walk")
    GROOF.append(((x0 + x1) / 2, (z0 + z1) / 2, x1 - x0, z1 - z0))
for i, (cx, cz, w, l) in enumerate(GROOF):
    add(f"guardhouse {i + 1} roof", {"type": "roof", "form": "hip", "width": r4(w), "length": r4(l), "pitch": 34, "overhang": 0.45, "at": [[r4(cx), r4(G0 + 3.6), r4(cz), 0]]})
# the boat landings: a water stair down into each lobe's cove, mooring posts
add("boat landing west", flight((-102.14, 2.2), (1, 0), 8.0, -2.4, G0, run=0.34, rise=0.16, _about="the boat landing in the west cove: a water stair down to the gondolas"))
add("boat landing east", flight((103.34, 0.5), (-1, 0), 8.0, -2.4, G0, run=0.34, rise=0.16, _about="the boat landing in the east cove"))
add("mooring posts", {"type": "column", "radius": 0.14, "height": 3.6, "sides": 8, "at": [[x, -2.9, z, 0] for x in (-99.0, -102.2) for z in (-4.6, 8.9)] + [[x, -2.9, z, 0] for x in (99.0, 102.4) for z in (-6.6, 7.6)],
                         "_about": "the mooring posts in the coves"})
# the bridges: the south bridge from the island to the causeway (sandstone, one arch); the north footbridge to the park
add("south bridge", comp("bridge", {"L": 5.2, "W": 7.4, "depth": 3.0, "n": 1, "pier": 1.0, "parapet": 1.0}, [[0.0, G0, 126.9, 0]],
                         _about="the stone bridge from the island to the causeway, on the axis"))
add("north bridge", comp("bridge", {"L": 4.8, "W": 3.2, "depth": 2.6, "n": 1, "pier": 0.8, "parapet": 1.0}, [[-1.3, G0, -123.6, PI]],
                         _about="the footbridge from the island to the park on the north shore"))

parts.update(capped(STATS)); build.extend(STATS.keys())

# ---- THE LAKE: the Schlossteich round the island, carved by the game (architecture.js: a pool, its shore the lake's own
# shore from OSM -- the north bank with the dam to the park, the causeway to the south -- cut to the site's rectangle)
SHORE = [[-135.0, -145.1], [-66.4, -151.6], [-64.2, -134.0], [-8.8, -134.3], [-8.8, -131.5], [-3.0, -127.4], [1.5, -127.2], [5.7, -130.4], [5.9, -134.0], [62.4, -134.8],
         [62.0, -165.0], [135.0, -165.0], [135.0, 165.0], [7.9, 165.0], [7.9, 134.3], [3.2, 130.9], [-3.8, 130.8], [-7.8, 133.7], [-7.8, 165.0], [-135.0, 165.0]]
MOAT = {"pool": True, "hw": 135.0, "hd": 165.0, "w": 0, "depth": 4.4, "surface": -0.9, "shore": SHORE, "islands": [ISLAND]}

doc = {"name": "Schloss Moritzburg",
       "_about": "SCHLOSS MORITZBURG, Augustus the Strong's baroque hunting lodge (Poeppelmann, 1723-33, round the Renaissance lodge) on its island in the Schlossteich, "
                 "from OpenStreetMap's plan: the main body and the two wings between four round towers under red bells and white lanterns, the chapel risalit "
                 "with its Dachreiter on the west, the Speisesaal risalit on the east; ochre walls, white lesenes and window surrounds, red mansards; the terrace "
                 "with its balustrade, piers, vases and statues, the north and south ramps, the curved stairs down the lobes; the island with its guardhouses, "
                 "walks, trees, boat landings, the bridges and the causeway. Inside: the vaulted entrance halls, the four great halls of the principal floor "
                 "(Billardsaal, Steinsaal, Monstroesensaal, the Speisesaal with its antlers), the chapel and its gallery, the apartments, the towers' rooms, "
                 "two dog-leg stairs (tools/archgen/moritzburg.py).",
       "params": {"detail": 4, "footW": 270.0, "footD": 330.0}, "railing": {"type": "balusters"},
       "site": {"origin": True},
       "_moat": MOAT,
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/moritzburg.json"), "w").write(json.dumps(doc, indent=1) + "\n")

# ---- THE FINISH
TOWER_PARTS = [f"tower {k}" for k in TOWERS]
TERRACE_STONE = ["terrace", "terrace piers", "vase feet", "vases", "north ramp", "south ramp", "north ramp parapet west", "north ramp parapet east", "south ramp parapet west",
                 "south ramp parapet east", "north ramp pedestals", "north ramp urns", "piqueurs", "south bridge", "north bridge", "boat landing west", "boat landing east",
                 ] + BAL + [n for n in parts if n.startswith("stair ")]
fin = {"name": "Schloss Moritzburg", "building": "architecture/moritzburg",
       "_about": "Schloss Moritzburg: ochre-yellow plastered walls, every dressing white -- the lesenes, the cornices and string courses, the window surrounds, the "
                 "lanterns -- the roofs in red Saxon plain tiles, the bells' lanterns under copper, gilt vanes; the chapel's Dachreiter hung with slate; the "
                 "terrace, its balustrade, the ramps and stairs in grey Elbe sandstone; inside, sandstone flags on the ground floor, parquet upstairs, the "
                 "Steinsaal's walls of stone, the Speisesaal's and the Monstroesensaal's gilt leather hangings; the island's lawns and gravel, its white guardhouses.",
       "stone": {"color": "#e7b24f", "accent": "#f4efe4", "pat": "plaster"},
       "rules": [
           {"parts": ["tower vanes", "tower vane balls", "dachreiter helm/ball", "dachreiter helm/cross", "dachreiter helm/finial"],
            "pattern": "roofs/gold leaf", "_about": "gilt vanes, balls and finials"},
           {"parts": ["dachreiter clocks/hands", "dachreiter clocks/marks"], "pattern": "roofs/gold leaf"},
           {"parts": ["dachreiter clocks/dial", "dachreiter clocks/ring", "dachreiter clocks"], "pattern": "roofs/sheet metal", "palette": "slate"},
           {"parts": ["tower lantern caps"], "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the lanterns' copper caps"},
           {"parts": ["tower lanterns", "tower lantern heads", "bell dormers", "bell oculi"], "pattern": "stone/plaster", "palette": "plaster-white", "_about": "the white lanterns and dormer frames"},
           {"parts": ["bell dormer hoods"], "pattern": "roofs/sheet metal", "palette": "copper"},
           {"parts": ["tower cap feet"], "pattern": "stone/plaster", "palette": "plaster-white"},
           {"parts": ["tower bells"], "pattern": "roofs/fish scale", "palette": "tile-red", "_about": "the bells in red plain tiles"},
           {"parts": ["dachreiter base", "dachreiter stage", "dachreiter helm", "dachreiter helm/foot", "dachreiter helm/bulb", "dachreiter helm/lantern", "dachreiter helm/lantern head",
                      "dachreiter helm/bulb 2", "dachreiter helm/lantern 2", "dachreiter helm/lantern 2 head", "dachreiter helm/spike"],
            "pattern": "roofs/slate", "palette": "slate", "_about": "the Dachreiter hung with slate"},
           {"parts": ["trophies"], "color": "#d9c9a8", "accent": "#9c8463", "_about": "the antlers, bone and brown"},
           {"parts": ["trophy boards"], "pattern": "timber/wood", "palette": "walnut"},
           {"parts": ["lesenes", "balcony", "balcony balustrade", "balcony balustrade ends", "chapel gallery balustrade"], "pattern": "stone/plaster", "palette": "plaster-white",
            "_about": "the white lesenes"},
           {"parts": ["kind:railing"], "within": [WX0 - 1, WZ0 - 1, EX1 + 1, WZ1 + 1], "above": TT + 0.5, "pattern": "stone/plaster", "palette": "plaster-white", "_about": "the stairs' railings inside"},
           {"parts": ["kind:railing"], "pattern": "stone/ashlar", "palette": "sandstone-grey", "_about": "the railings outside: sandstone"},
           {"parts": ["kind:moulding"], "below": TT + 0.2, "pattern": "stone/ashlar", "palette": "sandstone-grey", "_about": "the terrace's mouldings in grey sandstone"},
           {"parts": ["kind:moulding"], "pattern": "stone/plaster", "palette": "plaster-white", "_about": "every cornice, string course and window surround white"},
           {"parts": ["terrace doors", "terrace gates"], "pattern": "timber/boards", "palette": "oak-grey", "_about": "the vaults' doors"},
           {"parts": ["terrace windows"], "color": "#2f3436", "accent": "#202426", "_about": "the vaults' windows, dark"},
           {"parts": ["kind:roof", "chimneys"], "surface": "wall", "pattern": "stone/plaster", "palette": "plaster-ochre"},
           {"parts": ["middle leads"], "pattern": "roofs/sheet metal", "palette": "lead"},
           {"parts": ["kind:roof"], "pattern": "roofs/beaver tail", "palette": "tile-red", "_about": "the red plain-tile roofs"},
           {"parts": ["tree trunks"], "pattern": "timber/bark", "palette": "oak"},
           {"parts": ["tree crowns"], "color": "#4d7034", "accent": "#3c5a28", "_about": "the clipped limes"},
           {"parts": ["island", "causeway"], "surface": "floor", "pattern": "materials/grass", "palette": "lawn", "_about": "the island's lawns"},
           {"parts": ["island", "causeway", "mooring posts"], "pattern": "stone/ashlar", "palette": "sandstone-grey", "_about": "its quay walls"},
           {"parts": [n for n in parts if n.startswith("gravel ")], "pattern": "stone/sand", "palette": "gravel"},
           {"parts": [n for n in parts if n.startswith("guardhouse") and not n.endswith("roof")], "side": "out", "surface": "wall", "pattern": "stone/plaster", "palette": "plaster-white",
            "_about": "the guardhouses white"},
           {"parts": ["north ramp", "south ramp"], "surface": "floor", "pattern": "floors/sampietrini", "palette": "sampietrini", "_about": "the ramps' setts"},
           {"parts": TERRACE_STONE, "surface": "floor", "side": "out", "pattern": "floors/flagstones", "palette": "sandstone-grey", "_about": "the terrace's paving"},
           {"parts": TERRACE_STONE, "pattern": "stone/ashlar", "palette": "sandstone-grey", "_about": "the terrace, its balustrade, ramps and stairs in grey Elbe sandstone"},
           # inside
           {"surface": "floor", "side": "in", "below": LV[1] - 0.5, "pattern": "floors/flagstones", "palette": "sandstone", "_about": "the ground floor's sandstone flags"},
           {"parts": ["chapel retable"], "pattern": "stone/marble", "palette": "marble-rose", "_about": "the chapel's marble retable"},
           {"parts": ["chapel altar"], "pattern": "stone/marble", "palette": "carrara"},
           {"surface": "floor", "side": "in", "within": [CX0, CZ0, CX1 - 0.6, CZ1], "below": LV[1] - 0.5, "pattern": "floors/checker diagonal", "palette": "marble-bw", "_about": "the chapel's marble floor"},
           {"surface": "wall", "side": "in", "within": [CX0, CZ0, CX1 - 0.6, CZ1], "pattern": "stone/stucco lines", "palette": "plaster-white", "_about": "its white stucco"},
           {"surface": "floor", "side": "in", "within": [MX0, BZ0, MX1, BZ1], "below": LV[2], "pattern": "floors/checker", "palette": "marble-grey", "_about": "the halls' stone floors"},
           {"surface": "floor", "side": "in", "within": [RX0, RZ0, RX1, RZ1], "below": LV[2], "pattern": "floors/checker", "palette": "marble-grey"},
           {"surface": "floor", "side": "in", "pattern": "timber/basket parquet", "palette": "oak", "_about": "parquet upstairs"},
           {"surface": "wall", "side": "in", "within": [MX0, LZN, MX1, LZS], "above": LV[1], "below": LV[3], "pattern": "stone/ashlar fine", "palette": "sandstone",
            "_about": "the Steinsaal: walls of stone"},
           {"surface": "wall", "side": "in", "within": [RX0, RZ0, RX1, RZ1], "above": LV[1] + 1.2, "below": LV[3], "pattern": "fabrics/leather", "palette": "leather-red",
            "_about": "the Speisesaal's gilt leather hangings"},
           {"surface": "wall", "side": "in", "within": [MX0, LZS, MX1, BZ1], "above": LV[1] + 1.2, "below": LV[3], "pattern": "fabrics/leather", "palette": "leather",
            "_about": "the Monstroesensaal's"},
           {"surface": "wall", "side": "in", "within": [MX0, BZ0, MX1, LZN], "above": LV[1] + 1.2, "below": LV[3], "pattern": "fabrics/leather", "palette": "leather-dark",
            "_about": "the Billardsaal's"},
           {"surface": "wall", "side": "in", "above": LV[1], "below": LV[1] + 1.2, "pattern": "panels/wainscot", "palette": "baroque", "_about": "the wainscots"},
           {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
           {"surface": "wall", "below": TT + 0.05, "pattern": "stone/ashlar", "palette": "sandstone-grey"},
           {"surface": "wall", "pattern": "stone/plaster", "palette": "plaster-ochre", "_about": "the ochre walls"}]}
open(os.path.join(ROOT, "assets/finishes/moritzburg.json"), "w").write(json.dumps(fin, indent=1) + "\n")

if __name__ == "__main__":
    nst = sum(1 for v in parts.values() if v.get("role") == "statue")
    print("moritzburg:", len(parts), "parts,", nst, "statues,", len(TREES) + len(SHORE_TREES), "trees, moat", {k: v for k, v in MOAT.items() if not isinstance(v, list)})
