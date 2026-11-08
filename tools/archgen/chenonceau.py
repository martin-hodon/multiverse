# CHATEAU DE CHENONCEAU (Loire valley; the corps de logis 1514-22 for Thomas Bohier on the piers of the old mill in the
# Cher, Philibert de l'Orme's bridge 1556-59 for Diane de Poitiers, Jean Bullant's two-storey gallery on it 1576 for
# Catherine de Medicis; the Tour des Marques the keep of the Marques' castle, 15th century, re-dressed by Bohier).
# THE FRAME: the gallery's axis runs across the river: -z is the SOUTH bank (the gallery's far end), +z the NORTH --
# the forecourt, the Tour des Marques and the entrance avenue; +x is WEST (downstream: Catherine's garden), -x EAST
# (upstream: Diane's garden, the chapel and the library on the logis' east front). The origin is near the logis'
# middle (OpenStreetMap's local metres about 47.32476 N, 1.07043 E turned so the gallery runs along z: x = p.ex - 3.8,
# z = p.ez - 16, ex (-0.885, 0.466), ez (-0.466, -0.885)).
# THE PLAN IS OSM's: the logis (way 304289430 and its parts 304289396/423/426/431), the chapel and the library (304292286),
# the corner turrets (304289418/421/432/434), the gallery on the bridge (222468703, 304289408) and the pier cutwaters
# (222468979 ...), the Tour des Marques (222468693) on its moated terrace (the forecourt island 119209245), the river
# (363823721) and Diane's canal (200236124), Diane's parterre (200129081-097) and Catherine's (379358420, 200073915-930).
# THE HEIGHTS from photographs (Wikimedia Commons: the aerial from the west, the north front, the Tour des Marques, the
# gallery inside) scaled by the storeys: the water 2.2 m under the world's plain, the arches' crowns 6.8 m over it, the
# floors of the logis and the gallery 5.4 m over the plain, two storeys of 5.0 and 4.8 m, the cornice at 15.2 m, the logis'
# steep slate roof with its flat top 9.6 m over that, the rich dormers (lucarnes) standing on the cornice before their
# own steep slate hips, the gallery's hip 5.9 m tall with its oculus dormers.
# THE INSIDE (the plan as built, Androuet du Cerceau's and the visitor plan): the vestibule (the "galerie" through the
# middle, its rib vault of four bays), the Salle des Gardes and the Chambre de Diane to the east, the chapel and the
# library beyond them, the straight rampe-sur-rampe stair (one of the first in France) and the Chambre de Francois Ier
# and the Salon Louis XIV to the west; upstairs the same plan (the Vestibule Catherine Briconnet, the Cinq Reines, the
# Chambre de Catherine de Medicis, Cesar de Vendome, Gabrielle d'Estrees); the gallery on both levels, 60 m long, its
# floor below a black-and-white chequer laid diagonally, the great chimneypiece at its south end.
import os, json, math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from historicism import comp, flight, POINTED, ROOT, r4
COMP = os.path.join(ROOT, "assets/architecture/components")
parts, build = {}, []
def add(n, d): parts[n] = d; build.append(n); return n

Q = math.pi / 2
WL, BED = -2.2, -4.4         # the Cher (the world's water level), its bed
G = 2.4                      # the forecourt, the terraces, the gardens
F0, H1, H2 = 5.4, 5.0, 4.8   # the logis' and the gallery's floor; its two storeys
F1 = F0 + H1
TOP = F1 + H2                # the cornice: the walls' top
SLAB = 0.3
SEMI = {"profile": "semicircular"}
FLAT = {"profile": "flat"}
SEG = {"profile": "segmental", "rise": 0.35}
CROSS = {"style": "bars", "cols": 2, "rows": 2, "bar": 0.14}
def cross(at, w=1.9, sill=1.0, spr=4.1, **kw):
    """a Renaissance cross window (meneaux: a mullion and a transom of stone), its moulded frame under a little cornice"""
    return {"at": r4(at), "width": w, "sill": sill, "springing": spr, "head": FLAT, "tracery": CROSS, "surround": {"head": "cornice"}, **kw}
def door(at, w=1.3, h=2.5, head=SEG, **kw):
    return {"at": r4(at), "width": w, "sill": 0, "springing": h, "head": head, "glass": False, **kw}


# ================================================================================================ COMPONENTS
def loire_turret():
    """a Loire corner turret: a round shaft corbelled out (a cul-de-lampe of rings under its foot), its storeys under belt
    courses at the house's floors, a small window to the outside in each, a corbelled cornice, a tall slate cone and a
    lead finial"""
    p, b = {}, []
    def a(n, d): p[n] = d; b.append(n)
    win = lambda sill, spr: [{"at": 0, "width": "winW", "sill": sill, "springing": spr, "head": FLAT, "surround": {"head": "cornice", "band": 0.1}}]
    plain = [{"h": "h1", "openings": []}, {"h": "h2", "openings": []}, {"openings": []}]
    a("corbel", {"type": "prism", "plan": {"sides": "sides", "radius": "R"}, "height": "cor * 0.34", "flatRoof": True, "at": [[0, "0 - cor * 0.34", 0, 0]],
                 "_about": "the cul-de-lampe: rings narrowing down under the turret's foot"})
    a("corbel 2", {"type": "prism", "plan": {"sides": "sides", "radius": "R * 0.72"}, "height": "cor * 0.33", "flatRoof": True, "at": [[0, "0 - cor * 0.67", 0, 0]]})
    a("corbel 3", {"type": "prism", "plan": {"sides": "sides", "radius": "R * 0.42"}, "height": "cor * 0.33", "flatRoof": True, "at": [[0, "0 - cor", 0, 0]]})
    a("shaft", {"type": "enclosure", "plan": {"sides": "sides", "radius": "R"}, "thickness": "t", "height": "H", "glass": True, "interior": False,
                "tiers": plain, "faces": {"0": [{"h": "h1", "openings": win(1.2, "h1 - 1.4")}, {"h": "h2", "openings": win(1.0, "h2 - 1.3")},
                                                {"openings": win(0.5, "max(1.1, H - h1 - h2 - 0.7)")}]},
                "at": [[0, 0, 0, 0]], "_about": "the round shaft, a window in face 0 (looking out, +z) on each floor"})
    a("belts", {"type": "prism", "plan": {"sides": "sides", "radius": "R + 0.07"}, "height": 0.22, "flatRoof": True,
                "at": [[0, "h1 - 0.11", 0, 0], [0, "h1 + h2 - 0.11", 0, 0]], "_about": "belt courses at the house's floors"})
    a("corbels", {"type": "prism", "plan": {"sides": "sides", "radius": "R + corOut * 0.5"}, "height": "corH * 0.5", "flatRoof": True, "at": [[0, "H - corH * 0.5", 0, 0]],
                  "_about": "the corbel course under the cornice"})
    a("cornice", {"type": "prism", "plan": {"sides": "sides", "radius": "R + corOut"}, "height": "corH * 0.5", "flatRoof": True, "at": [[0, "H", 0, 0]], "standsOn": ["corbels"]})
    a("cap", {"type": "dome", "radius": "capR", "thickness": 0, "sides": "capSides", "head": {"profile": "trigonal", "rise": "capRise"},
              "at": [[0, "H + corH * 0.5", 0, 0]], "standsOn": ["cornice"], "_about": "the slate cone"})
    a("finial", {"type": "column", "radius": "max(0.05, capR * 0.045)", "height": "fin", "sides": 6, "taper": 0.35, "at": [[0, 0, 0, 0]], "atop": "cap", "standsOn": ["cap"],
                 "_about": "the lead finial (an epi) on the tip"})
    return {"name": "Loire turret",
            "_about": "A LOIRE CORNER TURRET (Chenonceau's, Azay-le-Rideau's): a round shaft (`sides`, R, H tall, `t` walls) standing on a cul-de-lampe `cor` deep under its foot "
                      "(three rings narrowing down -- corbelled out from a corner), belt courses at the house's floors (h1, h1 + h2 over its foot), a small window with a moulded frame "
                      "in face 0 (+z: yaw it to look out) on each floor, a corbelled cornice corOut proud, a tall slate cone capRise high from capR at its eave, a lead finial. "
                      "Place its foot at the house's ground floor, its +z out along the corner's diagonal.",
            "params": {"detail": 4, "sides": 12, "R": 1.5, "H": 12.0, "t": 0.35, "h1": 5.0, "h2": 4.8, "winW": "min(0.75, R * 0.36)", "cor": 2.0, "corOut": 0.22, "corH": 0.6,
                       "capR": "R + corOut + 0.12", "capRise": "capR * 3.4", "capSides": 16, "fin": "capRise * 0.2",
                       "_cor": "the cul-de-lampe's depth under the foot (hidden in a pier where the turret stands on one)",
                       "_h1": "the first belt over the foot (the house's first floor); h2 the second storey"},
            "build": b, "parts": p}


def loire_dormer():
    """the Loire lucarne: a stone frontispiece on the cornice before a steep slate hip"""
    p, b = {}, []
    def a(n, d): p[n] = d; b.append(n)
    a("body", {"type": "enclosure", "plan": {"rect": ["W", "D"]}, "thickness": "t", "height": "H", "glass": True, "interior": False,
               "faces": {"0": [{"openings": [{"at": 0, "width": "winW", "sill": "sill", "springing": "H - 0.45", "head": FLAT, "tracery": CROSS}]}], "1": [], "2": [], "3": []},
               "at": [[0, 0, "0 - D / 2", 0]], "_about": "the stone front carried up over the cornice, a cross window in it"})
    a("pilasters", {"type": "box", "width": "pw", "length": 0.14, "height": "H", "at": [["pw / 2 - W / 2 - 0.02", 0, 0.07, 0], ["W / 2 - pw / 2 + 0.02", 0, 0.07, 0]],
                    "_about": "a pilaster each side of the window"})
    a("entablature", {"type": "box", "width": "W + 0.3", "length": 0.42, "height": 0.34, "at": [[0, "H", -0.06, 0]], "_about": "the entablature over the window"})
    a("gable", {"type": "screen", "outline": [["0 - W / 2 + 0.05", 0], ["W / 2 - 0.05", 0], ["W / 2 - 0.05", "GH * 0.22"], ["W * 0.22", "GH * 0.62"], [0, "GH"],
                                              ["0 - W * 0.22", "GH * 0.62"], ["0 - W / 2 + 0.05", "GH * 0.22"]], "t": 0.3,
                "at": [[0, "H + 0.34", 0.08, 0]], "_about": "the crowning gable: a stepped pediment of carved stone"})
    a("niche", {"type": "box", "width": "W * 0.3", "length": 0.08, "height": "GH * 0.42", "at": [[0, "H + 0.34 + GH * 0.12", 0.12, 0]], "_about": "the little niche (a shell) in the gable"})
    a("candelabra", {"type": "pinnacle", "w": "pinW", "h": "GH * 0.3", "s": "GH * 0.42", "sides": 4,
                     "at": [["pinW / 2 - W / 2 - 0.1", "H + 0.34", -0.07, 0], ["W / 2 - pinW / 2 + 0.1", "H + 0.34", -0.07, 0], [0, "H + 0.34 + GH - 0.1", -0.07, 0]],
                     "_about": "the candelabra (carved finials) on the gable's feet and apex"})
    a("roof", {"type": "roof", "form": "hip", "width": "RW", "length": "RL", "pitch": "P", "overhang": 0.08, "at": [[0, 0, "0 - back - RL / 2", 0]],
               "_about": "the dormer's own steep slate hip behind the stone, its ridge running back into the great roof"})
    return {"name": "Loire dormer",
            "_about": "A LOIRE LUCARNE (Chenonceau's, Blois', Azay's): a stone frontispiece standing on the cornice -- the wall carried up H over it, W wide and D back into the roof, "
                      "a cross window in it between two pilasters, an entablature, and a crowning gable GH tall (a stepped pediment, its niche, a candelabrum on each foot and the apex) -- "
                      "before its own steep slate HIP (RW wide, RL long, P degrees, `back` behind the front) that runs back into the great roof. Place it on the cornice, its front over "
                      "the wall's face, yawed so +z looks out.",
            "params": {"detail": 4, "W": 3.2, "H": 4.2, "GH": 2.4, "D": 2.4, "t": 0.35, "winW": 1.5, "sill": 0.45, "pw": 0.3, "pinW": 0.3,
                       "RW": "W + 2.8", "RL": 8.4, "P": 72, "back": 0.3,
                       "_RW": "the slate hip's width (wider than the stone: its slopes show either side)", "_P": "the hip's pitch: the Loire's steep 70-odd degrees"},
            "build": b, "parts": p}


def oculus_dormer():
    """the gallery's small dormer: a round window between pilasters under a pediment, a little slate gable behind"""
    p, b = {}, []
    def a(n, d): p[n] = d; b.append(n)
    a("body", {"type": "enclosure", "plan": {"rect": ["W", "D"]}, "thickness": "t", "height": "H", "glass": True, "interior": False,
               "faces": {"0": [{"openings": [{"at": 0, "width": "r * 2", "sill": "H * 0.48", "springing": "H * 0.48", "head": SEMI, "foot": SEMI,
                                              "surround": {"band": 0.12, "depth": 0.06, "head": False, "sill": False}}]}], "1": [], "2": [], "3": []},
               "at": [[0, 0, "0 - D / 2", 0]], "_about": "the stone front with its round window (an oculus)"})
    a("pilasters", {"type": "box", "width": 0.22, "length": 0.12, "height": "H", "at": [["0.11 - W / 2", 0, 0.06, 0], ["W / 2 - 0.11", 0, 0.06, 0]]})
    a("entablature", {"type": "box", "width": "W + 0.24", "length": 0.36, "height": 0.24, "at": [[0, "H", -0.06, 0]]})
    a("pediment", {"type": "screen", "outline": [["0 - W / 2 - 0.1", 0], ["W / 2 + 0.1", 0], [0, "GH"]], "t": 0.28, "at": [[0, "H + 0.24", 0.1, 0]],
                   "_about": "the triangular pediment"})
    a("finial", {"type": "pinnacle", "w": 0.2, "h": 0.25, "s": 0.45, "sides": 4, "at": [[0, "H + 0.24 + GH - 0.1", -0.04, 0]]})
    a("roof", {"type": "roof", "form": "gable", "width": "W + 0.1", "length": "D", "pitch": "atan2(GH * 0.92, W / 2 + 0.05) * 57.29578", "overhang": 0.06,
               "at": [[0, "H + 0.24", "0 - D / 2 - 0.05", 0]], "_about": "its little slate gable running back into the great roof"})
    return {"name": "Oculus dormer",
            "_about": "AN OCULUS DORMER (Chenonceau's gallery): a small stone front W wide and H tall standing on the eave, a round window (r) in it between two pilasters, "
                      "an entablature and a triangular pediment GH tall with a finial, its own little slate gable roof running D back into the great roof. Place it on the cornice, +z out.",
            "params": {"detail": 4, "W": 2.1, "H": 2.1, "GH": 1.0, "D": 2.8, "t": 0.3, "r": 0.46},
            "build": b, "parts": p}


COMPONENTS = {"loire-turret": loire_turret(), "loire-dormer": loire_dormer(), "oculus-dormer": oculus_dormer()}


# ================================================================================================ HELPERS
def inside(x, z, poly):
    c = False
    for i in range(len(poly)):
        (x0, z0), (x1, z1) = poly[i], poly[i - 1]
        if (z0 > z) != (z1 > z) and x < x0 + (x1 - x0) * (z - z0) / (z1 - z0): c = not c
    return c

BAL = []                     # (the balustrades' names, for the finish)
def balustrade(name, pts, y, closed=True, gaps=(), poly=None, h=1.0, t=0.3, bp=0.9, skip=1.0):
    """a stone balustrade along the outline `pts` at height y, its outer face on the line (inside: toward `poly` or the
    outline itself): a wall with a row of baluster slots (the Versailles way), broken at the `gaps` ((x, z), width)"""
    poly = poly or pts; names = []
    n = len(pts)
    for i in range(n if closed else n - 1):
        p, q = pts[i], pts[(i + 1) % n]; L = math.dist(p, q)
        if L < skip: continue
        ex, ez = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        nx, nz = ez, -ex                                           # (a normal; turned outward below)
        mx, mz = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        if inside(mx + nx * 0.6, mz + nz * 0.6, poly): nx, nz = -nx, -nz
        runs = [(0.0, L)]
        for (gx, gz), gw in gaps:
            u = (gx - p[0]) * ex + (gz - p[1]) * ez; v = (gx - p[0]) * nx + (gz - p[1]) * nz
            if abs(v) < 1.5 and -gw / 2 < u < L + gw / 2:
                runs = [r for a, b in runs for r in ((a, min(b, u - gw / 2)), (max(a, u + gw / 2), b))]
        runs = [r for r in runs if r[1] - r[0] >= skip]
        yaw = math.atan2(nx, nz)
        for k, (a0, a1) in enumerate(runs):
            w = a1 - a0; m = (a0 + a1) / 2
            cx, cz = p[0] + ex * m, p[1] + ez * m
            nm = f"{name} {i}" + (f".{k}" if len(runs) > 1 else "")
            # (the wall's local +x must run along p->q or q->p: +z out, so +x = (nz, -nx))
            add(nm, {"type": "wall", "width": r4(w), "height": h, "thickness": t, "glass": False,
                     "openings": {"pattern": str(max(1, int((w - 0.5) // bp))), "width": r4(bp * 0.62), "gap": r4(bp * 0.38), "sill": 0.22, "springing": r4(h - 0.2),
                                  "head": FLAT, "glass": False},
                     "at": [[r4(cx), r4(y), r4(cz), r4(yaw)]]})
            names.append(nm); BAL.append(nm)
    return names

def iwall(name, a, b, doors0, doors1, about=None, t=0.5, y0=F0):
    """an inner wall of the logis from a to b (x, z), its middle on that line, two storeys (H1, then up to the cornice):
    doorways at the distances along it (from a) in doors0 (below) and doors1 (above) -- (d, width, height)"""
    L = math.dist(a, b); dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    ops = lambda ds: [door(d - L / 2, w, h) for d, w, h in ds]
    mx, mz = (a[0] + b[0]) / 2 - t / 2 * dz, (a[1] + b[1]) / 2 + t / 2 * dx
    d = {"type": "wall", "width": r4(L), "height": r4(TOP - y0), "thickness": t, "tiers": [{"h": H1, "openings": ops(doors0)}, {"openings": ops(doors1)}],
         "at": [[r4(mx), y0, r4(mz), r4(math.atan2(-dz, dx))]]}
    if about: d["_about"] = about
    return add(name, d)

def slab(name, x0, x1, z0, z1, y=F1, about=None):
    d = {"type": "prism", "plan": {"rect": [r4(x1 - x0), r4(z1 - z0)]}, "height": SLAB, "flatRoof": True, "walked": True,
         "at": [[r4((x0 + x1) / 2), r4(y - SLAB), r4((z0 + z1) / 2), 0]]}
    if about: d["_about"] = about
    return add(name, d)

def prism(name, pts, y0, y1, about=None, **kw):
    d = {"type": "prism", "plan": {"points": [[r4(x), r4(z)] for x, z in pts]}, "height": r4(y1 - y0), "flatRoof": True, "walked": True, "at": [[0, r4(y0), 0, 0]], **kw}
    if about: d["_about"] = about
    return add(name, d)

def item(name, path, at, about=None, **kw):
    d = {"type": "item", "item": "items/furniture/" + path, "at": [[r4(x), r4(y), r4(z), r4(yaw)] for x, y, z, yaw in at], **kw}
    if about: d["_about"] = about
    return add(name, d)


# ================================================================================================ THE CHER AND THE PIERS
# The logis stands on two piers of the old mill (the north pier under the chapel and the north rooms, the south one under
# the library and the south rooms), the mill race between them under a barrel vault; the bridge north to the forecourt
NP = [(-19.5, 4.6), (13.1, 4.6), (13.1, 12.6), (-13.0, 12.6), (-13.0, 11.6), (-19.0, 11.6), (-20.8, 10.2), (-20.8, 5.6)]
SP = [(-15.6, -1.2), (13.1, -1.2), (13.1, -15.5), (-0.2, -15.5), (-0.2, -17.9), (-4.8, -17.9), (-4.8, -12.6), (-12.8, -12.6), (-13.4, -10.4),
      (-19.0, -10.4), (-21.6, -8.0), (-21.6, -5.6), (-19.0, -3.6), (-15.6, -3.2)]
prism("north pier", NP, BED, F0, about="the logis' north pier in the Cher (the old mill's): the chapel and the north rooms stand on it")
prism("south pier", SP, BED, F0, about="the logis' south pier: the library, the south rooms and the gallery's first bay")
add("mill race vault", {"type": "barrel", "width": 5.8, "length": 28.9, "springing": 1.9, "top": F0, "head": SEMI, "at": [[13.1, 0, 1.7, Q]],
                        "_about": "the vault over the old mill race between the two piers: the arch under the logis"})
# the bridge to the forecourt: one arch, the deck at the floor; the flight up from the forecourt at its north end
add("north bridge", {"type": "wall", "width": 13.4, "height": r4(F0 - BED), "thickness": 10.1, "glass": False,
                     "tiers": [{"openings": [{"at": -0.3, "width": 5.0, "sill": 0, "springing": r4(1.0 - BED), "head": SEMI, "glass": False}]}],
                     "at": [[-5.3, BED, 19.3, r4(-Q)]], "_about": "the bridge from the forecourt to the logis' door: one arch over the Cher"})
FZ = 32.3                                                  # (the forecourt's edge at the bridge)
prism("north bridge foot", [(-5.3, 26.0), (4.8, 26.0), (4.8, FZ + 0.1), (-5.3, FZ + 0.1)], BED, G, about="the bridge's abutment on the forecourt")
add("north bridge stair", flight((-0.25, FZ), (0, -1), 10.1, G, F0, _about="the broad flight up from the forecourt onto the bridge"))
balustrade("north bridge balustrade", [(-5.3, 12.6), (-5.3, 26.0), (4.8, 26.0), (4.8, 12.6)], F0, closed=False,
           poly=[(-5.3, 12.6), (-5.3, 26.0), (4.8, 26.0), (4.8, 12.6)], gaps=[((-0.25, 26.0), 10.4)])

# ================================================================================================ THE LOGIS
LX0, LX1, LZ0, LZ1 = -12.8, 12.9, -12.1, 12.0
LCX, LCZ = (LX0 + LX1) / 2, (LZ0 + LZ1) / 2
an = lambda x: r4(x - LCX)            # (face 0, north: along +x)
aw = lambda z: r4(LCZ - z)            # (face 1, west: along -z)
as_ = lambda x: r4(LCX - x)           # (face 2, south: along -x)
ae = lambda z: r4(z - LCZ)            # (face 3, east: along +z)
UP = dict(sill=0.9, spr=3.8)
F_LOGIS = {
    "0": [{"h": H1, "openings": [cross(an(-7.25)), cross(an(7.05)), door(an(-0.8), 2.0, 2.9, SEMI, surround={"keystone": True})]},
          {"openings": [cross(an(-7.25), **UP), cross(an(7.05), **UP), {"at": an(-0.8), "width": 1.6, "sill": 0, "springing": 3.3, "head": FLAT, "tracery": {"style": "bars", "cols": 2, "rows": 1, "bar": 0.12}, "surround": {"head": "cornice"}}]}],
    "1": [{"h": H1, "openings": [cross(aw(7.1)), cross(aw(-7.2)), cross(aw(-0.25), w=1.4, sill=3.3, spr=4.55)]},
          {"openings": [cross(aw(7.1), **UP), cross(aw(-7.2), **UP), cross(aw(-0.25), w=1.4, **UP)]}],
    "2": [{"h": H1, "openings": [cross(as_(-8.0)), cross(as_(9.6)), door(as_(1.4), 1.4, 2.7)]},
          {"openings": [cross(as_(-8.0), **UP), cross(as_(9.6), **UP), door(as_(1.4), 1.4, 2.7)]}],
    "3": [{"h": H1, "openings": [door(ae(8.0), 1.4, 2.8, POINTED), door(ae(-6.6), 1.3, 2.6)]},
          {"openings": [door(ae(-6.6), 1.3, 2.6), door(ae(1.3), 1.3, 2.6)]}]}
add("logis", {"type": "enclosure", "plan": {"rect": [r4(LX1 - LX0), r4(LZ1 - LZ0)]}, "thickness": 1.0, "height": r4(TOP - F0), "glass": True, "interior": True,
              "faces": F_LOGIS, "courses": True, "at": [[r4(LCX), F0, r4(LCZ), 0]],
              "_about": "the corps de logis (1514-22): a square block of two storeys on its piers, cross windows in moulded frames, string course and cornice; "
                        "the door in the middle of the north front under the balcony, the gallery through the south front"})
# the door's frame and the balcony over it (on consoles), as on the north front
add("balcony", {"type": "box", "width": 4.2, "length": 1.1, "height": 0.35, "at": [[-0.8, F1 - 0.2, r4(LZ1 + 0.55), 0]], "_about": "the balcony over the door"})
add("balcony consoles", {"type": "box", "width": 0.45, "length": 0.9, "height": 0.9, "at": [[x, F1 - 1.1, r4(LZ1 + 0.45), 0] for x in (-2.6, 1.0)]})
balustrade("balcony balustrade", [(-2.9, LZ1 + 0.02), (-2.9, LZ1 + 1.1), (1.3, LZ1 + 1.1), (1.3, LZ1 + 0.02)], F1 + 0.15, closed=False,
           poly=[(-2.9, LZ1), (-2.9, LZ1 + 1.1), (1.3, LZ1 + 1.1), (1.3, LZ1)], h=0.9, t=0.18, bp=0.45, skip=0.8)
add("portal columns", {"type": "column", "radius": 0.2, "height": 4.6, "sides": 12, "taper": 0.9, "at": [[x, F0, r4(LZ1 + 0.3), 0] for x in (-2.35, 0.75)],
                       "_about": "the door's frame: a column each side carrying the balcony"})

# the pilaster strips framing each column of windows (the facade's Renaissance grid, as on the north front)
PH = r4(TOP - F0 - 1.1)
PIL = ([[r4(x + d), F0 + 0.7, r4(LZ1 + 0.06), 0] for x in (-7.25, 7.05) for d in (-1.35, 1.35)] + [[r4(-0.8 + d), F0 + 0.7, r4(LZ1 + 0.06), 0] for d in (-1.75, 1.75)]
       + [[r4(LX1 + 0.06), F0 + 0.7, r4(z + d), r4(Q)] for z in (7.1, -7.2) for d in (-1.35, 1.35)]
       + [[r4(x + d), F0 + 0.7, r4(LZ0 - 0.06), 0] for x in (-8.0, 9.6) for d in (-1.35, 1.35)])
add("pilaster strips", {"type": "box", "width": 0.34, "length": 0.12, "height": PH, "at": PIL, "_about": "the flat pilasters either side of every column of windows"})
# THE GREAT ROOF: the Loire's steep slate (62 degrees) to a flat lead top, chimneys through it
BRK = 8.6
add("logis roof", {"type": "roof", "form": "mansard", "width": r4(LX1 - LX0), "length": r4(LZ1 - LZ0), "lowerPitch": 62, "breakH": BRK, "pitch": 8, "overhang": 0.3,
                   "at": [[r4(LCX), TOP, r4(LCZ), 0]], "_about": "the logis' great roof: steep slate slopes to a flat top, as on the Loire"})
CH = [(-5.5, 5.6), (-5.5, -5.2), (4.6, 5.6), (4.6, -5.2), (9.4, -0.2)]
add("chimneys", {"type": "box", "width": 1.0, "length": 2.2, "height": 7.4, "at": [[x, TOP + 6.6, z, 0] for x, z in CH],
                 "_about": "the tall chimney stacks through the roof"})
add("chimney caps", {"type": "box", "width": 1.3, "length": 2.5, "height": 0.35, "at": [[x, TOP + 14.0, z, 0] for x, z in CH]})

# THE DORMERS (components/loire-dormer) on the cornice: three on the north front (the middle one the grandest), two west,
# two south, one east -- each before its steep slate hip
DORM = []
def dormer(name, x, z, yaw, **p):
    DORM.append(add(name, comp("loire-dormer", p, [[r4(x), TOP, r4(z), r4(yaw)]], _about="a lucarne on the cornice before its slate hip")))
for k, x in enumerate((-7.25, 7.05)): dormer(f"north dormer {k + 1}", x, LZ1 + 0.35, 0)
dormer("north dormer middle", -0.8, LZ1 + 0.35, 0, W=3.6, GH=3.0, H=4.6, RW=6.6, P=70, RL=9.0)
for k, z in enumerate((7.1, -7.2)): dormer(f"west dormer {k + 1}", LX1 + 0.35, z, Q)
for k, x in enumerate((-8.0, -3.0)): dormer(f"south dormer {k + 1}", x, LZ0 - 0.35, math.pi)
dormer("east dormer", LX0 - 0.35, 0.7, -Q)

# THE CORNER TURRETS (components/loire-turret): corbelled out at the corners, their cones over the cornice
TUR = []
def turret(name, x, z, R, over, yaw, cor=2.2, **p):
    TUR.append(add(name, comp("loire-turret", {"R": R, "H": r4(TOP + over - F0), "cor": cor, **p}, [[r4(x), F0, r4(z), r4(yaw)]],
                              _about="a corner turret, corbelled out, under its slate cone")))
turret("turret north-east", -12.75, 12.35, 1.55, 3.6, -Q / 2, capRise="capR * 3.6")
turret("turret north-west", 12.85, 12.35, 1.5, 2.2, Q / 2)
turret("turret south-west", 12.85, -12.45, 1.5, 2.2, 3 * Q / 2)
turret("turret south-east", -14.6, -12.3, 1.7, 2.8, -3 * Q / 2, cor=3.0)

# ---- THE CHAPEL (north-east, off the Salle des Gardes): one tall storey, a three-sided apse to the east, rib vaulted
CHP = [(-18.5, 11.2), (-12.8, 11.2), (-12.8, 4.6), (-18.5, 4.6), (-20.4, 5.9), (-20.4, 9.9)]
CHW = lambda at, w=1.3: {"at": r4(at), "width": w, "sill": 2.2, "springing": 6.6, "head": POINTED, "tracery": {}}
add("chapel", {"type": "enclosure", "plan": {"points": [[x, z] for x, z in CHP]}, "thickness": 0.8, "height": r4(TOP - F0), "glass": True, "interior": True,
               "faces": {"0": [{"openings": [CHW(-16.0 + 15.65), CHW(-14.0 + 15.65, 1.1)]}], "1": [{"openings": [door(-0.1, 1.4, 2.8, POINTED)]}],
                         "2": [{"openings": [CHW(15.65 - 17.0)]}], "3": [{"openings": [CHW(0, 0.9)]}], "4": [{"openings": [CHW(0, 1.2)]}], "5": [{"openings": [CHW(0, 0.9)]}]},
               "courses": {"skip": ["1"]}, "at": [[0, F0, 0, 0]],
               "_about": "the chapel (1521): one tall storey off the Salle des Gardes, its three-sided apse to the east, pointed traceried windows"})
add("chapel vault", {"type": "groin", "width": 4.9, "length": 5.0, "springing": 10.4, "top": TOP, "head": {"profile": "pointed", "spread": 0.55},
                     "at": [[-16.05, 0, 7.9, 0]], "_about": "the chapel's rib vault"})
add("chapel ribs", {"type": "ribs", "on": "chapel vault", "width": 0.22, "depth": 0.2, "wall": {"width": 0.2, "depth": 0.15}, "at": [[-16.05, 0, 7.9, 0]]})
add("chapel roof", {"type": "roof", "form": "hip", "width": 6.6, "length": 15.4, "pitch": 56, "overhang": 0.3, "at": [[-12.7, TOP, 7.9, Q]],
                    "_about": "the chapel's slate roof running into the logis' great roof"})
add("chapel lantern", {"type": "pinnacle", "w": 0.9, "h": 2.4, "s": 4.2, "sides": 8, "at": [[-17.4, r4(TOP + 3.3 * math.tan(math.radians(56)) - 0.9), 7.9, 0]],
                       "_about": "the openwork bell lantern on the chapel's roof"})
item("chapel altar", "altar-table", [(-19.4, F0, 7.9, -Q)], about="the altar in the apse")
item("chapel benches", "bench", [(x, F0, z, Q) for x in (-16.8, -15.0) for z in (6.4, 9.4)])

# ---- THE LIBRARY (Catherine's librairie, south-east, off the Chambre de Diane): two storeys over the river on corbels
BX0, BX1, BZ0, BZ1 = -21.4, -12.8, -10.0, -3.2
BCX, BCZ = (BX0 + BX1) / 2, (BZ0 + BZ1) / 2
add("library", {"type": "enclosure", "plan": {"rect": [r4(BX1 - BX0), r4(BZ1 - BZ0)]}, "thickness": 0.7, "height": r4(TOP - F0), "glass": True, "interior": True,
                "faces": {"0": [{"h": H1, "openings": [cross(r4(-18.6 - BCX), w=1.5)]}, {"openings": [cross(r4(-18.6 - BCX), w=1.5, **UP), door(r4(-14.2 - BCX), 1.2, 2.6)]}],
                          "1": [{"h": H1, "openings": [door(r4(BCZ + 6.6), 1.3, 2.6)]}, {"openings": [door(r4(BCZ + 6.6), 1.3, 2.6)]}],
                          "2": [{"h": H1, "openings": [cross(r4(BCX + 19.4), w=1.5), cross(r4(BCX + 14.9), w=1.5)]},
                                {"openings": [cross(r4(BCX + 19.4), w=1.5, **UP), cross(r4(BCX + 14.9), w=1.5, **UP)]}],
                          "3": [{"h": H1, "openings": [cross(0, w=1.5)]}, {"openings": [cross(0, w=1.5, **UP)]}]},
                "courses": {"skip": ["1"]}, "at": [[r4(BCX), F0, r4(BCZ), 0]],
                "_about": "the library and the Cabinet Vert beneath it: two storeys standing out over the river to the east"})
add("library corbels", {"type": "prism", "plan": {"rect": [r4(BX1 - BX0 + 0.2), r4(BZ1 - BZ0 + 0.2)]}, "height": 0.6, "flatRoof": True,
                        "at": [[r4(BCX), F0 - 0.6, r4(BCZ), 0]], "_about": "the corbel course carrying the library out over the pier's cutwater"})
add("library corbels 2", {"type": "prism", "plan": {"rect": [r4(BX1 - BX0 - 0.6), r4(BZ1 - BZ0 - 0.6)]}, "height": 0.6, "flatRoof": True, "at": [[r4(BCX), F0 - 1.2, r4(BCZ), 0]]})
add("library roof", {"type": "roof", "form": "hip", "width": r4(BZ1 - BZ0), "length": 16.4, "pitch": 56, "overhang": 0.3, "at": [[-13.2, TOP, r4(BCZ), Q]],
                     "_about": "the library's slate roof, running into the great roof"})
slab("library floor", BX0 + 0.7, BX1, BZ0 + 0.7, BZ1 - 0.7, about="the library's upper floor")
item("library tables", "refectory-table", [(-17.6, F0, -6.6, 0), (-17.6, F1, -6.6, 0)])
item("library bookcases", "bookcase", [(-20.4, F1, -6.6, Q), (-20.4, F0, -6.6, Q)])
# the terrace between the chapel and the library over the mill race, at the upper floor
prism("east terrace", [(-15.6, -3.2), (-12.8, -3.2), (-12.8, 4.6), (-15.6, 4.6)], F0, F1, about="the little terrace on the east front between the chapel and the library, at the upper floor")
balustrade("east terrace balustrade", [(-12.8, 4.6), (-15.6, 4.6), (-15.6, -3.2), (-12.8, -3.2)], F1, closed=False,
           poly=[(-15.6, -3.2), (-12.8, -3.2), (-12.8, 4.6), (-15.6, 4.6)], h=1.0, skip=1.5)
# the little annex on the south front (OSM's part by the gallery): one storey
add("south annex", {"type": "enclosure", "plan": {"rect": [4.6, 5.8]}, "thickness": 0.6, "height": H1, "glass": True, "interior": False,
                    "faces": {"0": [], "1": [], "2": [{"openings": [cross(0, w=1.2, sill=1.2, spr=3.8)]}], "3": [{"openings": [cross(0, w=1.2, sill=1.2, spr=3.8)]}]},
                    "courses": {"skip": ["0"]}, "at": [[-2.5, F0, -15.0, 0]], "_about": "the little annex against the south front by the gallery"})
add("south annex roof", {"type": "roof", "form": "hip", "width": 4.6, "length": 5.8, "pitch": 56, "overhang": 0.25, "at": [[-2.5, F1, -15.0, 0]]})

# ---- INSIDE THE LOGIS: the vestibule through the middle (rib vaulted), the rooms either side, the straight stair
VX0, VX1 = -3.65, 2.15                    # (the vestibule between its two walls' faces)
IZ0, IZ1 = LZ0 + 1.0, LZ1 - 1.0           # (the inner faces of the north and south walls)
IX0, IX1 = LX0 + 1.0, LX1 - 1.0
iwall("vestibule east wall", (-3.9, IZ0), (-3.9, IZ1), [(6.0 - IZ0, 1.4, 2.7), (-6.5 - IZ0, 1.4, 2.7)], [(6.0 - IZ0, 1.4, 2.7), (-6.5 - IZ0, 1.4, 2.7)],
      about="the vestibule's east wall: the doors to the Salle des Gardes and the Chambre de Diane (above: the Cinq Reines, Gabrielle d'Estrees)")
iwall("vestibule west wall", (2.4, IZ0), (2.4, IZ1), [(7.0 - IZ0, 1.4, 2.7), (1.0 - IZ0, 2.0, 2.8), (-7.0 - IZ0, 1.4, 2.7)],
      [(7.0 - IZ0, 1.4, 2.7), (-1.5 - IZ0, 2.0, 2.8), (-7.0 - IZ0, 1.4, 2.7)],
      about="the vestibule's west wall: the doors to the Salon Louis XIV, the stair's foot (its arrival above) and the Chambre de Francois Ier")
iwall("east rooms wall", (IX0, -1.9), (-4.15, -1.9), [(-8.0 - IX0, 1.3, 2.6)], [(-8.0 - IX0, 1.3, 2.6)], about="between the Salle des Gardes and the Chambre de Diane")
iwall("stair hall north wall", (2.65, 2.3), (IX1, 2.3), [], [(6.0 - 2.65, 1.3, 2.6)], about="the stair hall's north wall (above: a door into the room over the Salon Louis XIV)")
iwall("stair hall south wall", (2.65, -2.9), (IX1, -2.9), [], [(10.2 - 2.65, 1.2, 2.6)], about="the stair hall's south wall (above: a door from the landing to Catherine de Medicis' room)")
add("stair spine wall", {"type": "box", "width": 5.76, "length": 0.5, "height": H1, "at": [[5.53, F0, -0.25, 0]],
                         "_about": "the mur d'echiffre: the wall between the two flights of the straight stair"})
add("great stair", {"type": "staircase", "rise": 0.15625, "run": 0.36, "soffit": 0.35, "flight": 16, "width": 2.0,
                    "landing": {"depth": 3.4, "width": 4.5, "shift": -1.25,
                                "then": [{"from": "back", "at": -1.25, "flight": 16, "width": 2.0, "landing": {"depth": 1.2, "width": 2.0}}]},
                    "at": [[2.65, F0, 1.0, 0]],
                    "_about": "the great stair (1515-20, one of the first straight stairs in France): rampe sur rampe -- up from the vestibule toward the river, "
                              "round a landing lit by the west window, back up beside itself to the upper vestibule"})
# the vestibule's rib vault: four bays, its crown under the upper floor
VB = (IZ1 - IZ0) / 4
add("vestibule vault", {"type": "groin", "width": r4(VX1 - VX0), "length": r4(VB), "springing": 8.5, "top": r4(F1 - SLAB),
                        "across": {"profile": "segmental", "rise": 1.45}, "along": {"profile": "segmental", "rise": 1.45},
                        "at": [[r4((VX0 + VX1) / 2), 0, r4(IZ0 + VB * (k + 0.5)), 0] for k in range(4)],
                        "_about": "the vestibule's rib vault (four bays, its keystones offset along the axis as built)"})
add("vestibule ribs", {"type": "ribs", "on": "vestibule vault", "width": 0.2, "depth": 0.18, "wall": {"width": 0.2, "depth": 0.14},
                       "at": [[r4((VX0 + VX1) / 2), 0, r4(IZ0 + VB * (k + 0.5)), 0] for k in range(4)]})
add("vestibule paving", {"type": "prism", "plan": {"rect": [r4(VX1 - VX0), r4(IZ1 - IZ0)]}, "height": 0.04, "flatRoof": True, "walked": True,
                         "at": [[r4((VX0 + VX1) / 2), F0, r4((IZ0 + IZ1) / 2), 0]], "_about": "the vestibule's stone flags"})
# the upper floors
slab("east rooms floor", IX0, VX0, IZ0, IZ1, about="the floor over the Salle des Gardes and the Chambre de Diane")
slab("vestibule floor", VX0, VX1, IZ0, IZ1, about="the upper vestibule's floor, over the vault")
slab("salon floor", VX1, IX1, 2.05, IZ1, about="the floor over the Salon Louis XIV")
slab("francois floor", VX1, IX1, IZ0, -2.65, about="the floor over the Chambre de Francois Ier")
slab("stair hall floor", 2.65, IX1, -0.5, 2.05, about="the upper stair hall over the first flight")
slab("stair landing floor", 8.41, IX1, -2.65, -0.5, about="the upper landing over the half-landing")
# rooms
item("gardes table", "refectory-table", [(-8.0, F0, 5.0, 0)], about="the Salle des Gardes' long table")
item("diane bed", "four-poster", [(-9.5, F0, -7.5, Q)], about="the Chambre de Diane de Poitiers' bed")
item("catherine bed", "four-poster", [(9.0, F1, -7.5, -Q)], about="Catherine de Medicis' bed upstairs")
item("gabrielle bed", "four-poster", [(-9.5, F1, -7.5, Q)])
item("francois chairs", "fauteuil", [(6.0, F0, -7.0, 0), (7.4, F0, -7.0, 0)])
item("salon table", "console-table", [(9.5, F0, 9.6, math.pi)])
item("chandeliers", "chandelier", [(-8.0, F1 - 0.2, 5.0, 0), (6.5, F1 - 0.2, 6.5, 0), (6.5, F1 - 0.2, -7.0, 0), (-8.0, F1 - 0.2, -6.5, 0),
                                   (-8.0, TOP - 0.2, 5.0, 0), (6.5, TOP - 0.2, 6.5, 0)])
item("reines table", "plain-table", [(-8.0, F1, 5.0, 0)], about="the Cinq Reines' room")

# ================================================================================================ THE GALLERY
# Bullant's gallery (1576) on de l'Orme's bridge: two storeys 60 m long across the Cher, nine windows a side on each, the
# ground floor's round-headed over the piers; the hip roof with its oculus dormers; the five arches below, rounded
# bastions on the piers' upstream side (balconies at the floor), pointed cutwaters downstream
GX0, GX1, GZ0, GZ1 = -0.2, 7.4, -78.3, LZ0
GCX, GCZ = (GX0 + GX1) / 2, (GZ0 + GZ1) / 2
WZ = [-18.5, -23.0, -29.0, -35.0, -41.5, -47.9, -54.8, -61.8, -68.2]
PIERZ = (-23.0, -35.0, -47.9, -61.8)
def gwin(at, z, upper):
    if upper: return {"at": r4(at), "width": 1.4, "sill": 0.9, "springing": 3.4, "head": FLAT, "tracery": CROSS, "surround": {"head": "cornice"}}
    if z in PIERZ: return {"at": r4(at), "width": 1.4, "sill": 0.9, "springing": 3.3, "head": SEMI, "surround": {"keystone": True}}
    return {"at": r4(at), "width": 1.5, "sill": 0.9, "springing": 3.9, "head": FLAT, "tracery": CROSS, "surround": {"head": "cornice"}}
F_GAL = {"0": [{"h": H1, "openings": [door(r4(1.4 - GCX), 1.4, 2.7)]}, {"openings": [door(r4(1.4 - GCX), 1.4, 2.7)]}],
         "1": [{"h": H1, "openings": [gwin(GCZ - z, z, False) for z in WZ]}, {"openings": [gwin(GCZ - z, z, True) for z in WZ]}],
         "2": [{"h": H1, "openings": [door(r4(GCX - 1.4), 1.3, 2.7, SEMI), gwin(r4(GCX - 5.8), 0, True)]},
               {"openings": [gwin(r4(GCX - 1.4), 0, True), gwin(r4(GCX - 5.8), 0, True)]}],
         "3": [{"h": H1, "openings": [gwin(z - GCZ, z, False) for z in WZ]}, {"openings": [gwin(z - GCZ, z, True) for z in WZ]}]}
add("gallery", {"type": "enclosure", "plan": {"rect": [r4(GX1 - GX0), r4(GZ1 - GZ0)]}, "thickness": 0.8, "height": r4(TOP - F0), "glass": True, "interior": True,
                "faces": F_GAL, "courses": {"skip": ["0"]}, "at": [[r4(GCX), F0, r4(GCZ), 0]],
                "_about": "the Grande Galerie (Jean Bullant, 1576): two storeys across the Cher, nine windows a side on each, the door to the south bank at its far end"})
add("gallery paving", {"type": "prism", "plan": {"rect": [r4(GX1 - GX0 - 1.6), r4(GZ1 - GZ0 - 1.6)]}, "height": 0.04, "flatRoof": True, "walked": True,
                        "at": [[r4(GCX), F0, r4(GCZ), 0]], "_about": "the gallery's floor below: black and white marble laid diagonally"})
add("gallery floor", {"type": "prism", "plan": {"rect": [r4(GX1 - GX0 - 1.6), r4(GZ1 - GZ0 - 1.6)]}, "height": SLAB, "flatRoof": True, "walked": True,
                      "at": [[r4(GCX), F1 - SLAB, r4(GCZ), 0]], "_about": "the upper gallery's floor"})
add("gallery roof", {"type": "roof", "form": "hip", "width": r4(GX1 - GX0), "length": r4(GZ1 + 9.1 - GZ0), "pitch": 57, "overhang": 0.3,
                     "at": [[r4(GCX), TOP, r4((GZ1 + 9.1 + GZ0) / 2), 0]], "_about": "the gallery's slate hip, its north end running into the logis' roof"})
GDORM = add("gallery dormers", comp("oculus-dormer", {}, [[r4(GX1 + 0.32), TOP, z, r4(Q)] for z in WZ] + [[r4(GX0 - 0.32), TOP, z, r4(-Q)] for z in WZ],
                                    _about="the gallery's oculus dormers over its windows"))
add("gallery chimney", {"type": "box", "width": 1.8, "length": 1.0, "height": 9.0, "at": [[r4(GCX), TOP - 0.5, -77.6, 0]], "_about": "the chimney stack of the gallery's great fireplace, on its south end"})
add("gallery chimney cap", {"type": "box", "width": 2.1, "length": 1.3, "height": 0.35, "at": [[r4(GCX), TOP + 8.5, -77.6, 0]]})
add("gallery fireplace", {"type": "box", "width": 2.6, "length": 0.7, "height": 0.5, "at": [[r4(GCX), F0 + 2.0, -77.1, 0]], "_about": "the great chimneypiece at the gallery's south end: its mantel"})
add("gallery fireplace jambs", {"type": "box", "width": 0.35, "length": 0.6, "height": 2.0, "at": [[r4(GCX + d), F0, -77.15, 0] for d in (-1.1, 1.1)]})
add("gallery fireplace hood", {"type": "box", "width": 2.2, "length": 0.5, "height": 2.2, "at": [[r4(GCX), F0 + 2.5, -77.25, 0]]})
item("gallery benches", "bench", [(r4(GX0 + 1.3), F0, z, Q) for z in (-26.0, -38.0, -51.0, -65.0)] + [(r4(GX1 - 1.3), F0, z, -Q) for z in (-26.0, -38.0, -51.0, -65.0)])
item("gallery chandeliers", "chandelier", [(r4(GCX), F1 - 0.4, z, 0) for z in (-24.0, -40.0, -56.0, -70.0)] + [(r4(GCX), TOP - 0.3, z, 0) for z in (-30.0, -50.0, -68.0)])

# THE BRIDGE (Philibert de l'Orme): a solid as wide as the gallery from the river's bed to its floor, five arches through it
ARCH = [(-18.5, 5.0, 2.1), (-29.0, 8.0, 0.6), (-41.5, 9.0, 0.1), (-54.8, 9.6, -0.2), (-68.2, 8.4, 0.4)]   # (middle z, span, impost)
BZM = (-15.0 + GZ0) / 2
add("bridge", {"type": "wall", "width": r4(-15.0 - GZ0), "height": r4(F0 - BED), "thickness": r4(GX1 - GX0), "glass": False,
               "tiers": [{"openings": [{"at": r4(BZM - zc), "width": sp, "sill": 0, "springing": r4(imp - BED), "head": SEMI, "glass": False} for zc, sp, imp in ARCH]}],
               "at": [[GX1, BED, r4(BZM), r4(Q)]], "_about": "Philibert de l'Orme's bridge (1556-59): five arches across the Cher under the gallery"})
add("bridge band", {"type": "box", "width": 0.3, "length": r4(-15.0 - GZ0), "height": 0.35, "at": [[r4(GX0 - 0.1), F0 - 0.6, r4(BZM), 0], [r4(GX1 + 0.1), F0 - 0.6, r4(BZM), 0]],
                    "_about": "the moulded band along the bridge's faces under the gallery's floor"})
for k, zc in enumerate(PIERZ):
    prism(f"cutwater {k + 1}", [(GX1, zc + 2.0), (GX1 + 1.6, zc + 2.0), (GX1 + 3.2, zc), (GX1 + 1.6, zc - 2.0), (GX1, zc - 2.0)], BED, F0 - 0.9,
          about="a pointed cutwater on the pier's downstream face", walked=False)
    prism(f"cutwater cap {k + 1}", [(GX1, zc + 2.15), (GX1 + 1.65, zc + 2.15), (GX1 + 3.4, zc), (GX1 + 1.65, zc - 2.15), (GX1, zc - 2.15)], F0 - 0.9, F0 - 0.5, walked=False)
    add(f"bastion {k + 1}", {"type": "prism", "plan": {"sides": 20, "radius": 2.0, "arc": [180, 360]}, "height": r4(F0 - BED), "flatRoof": True, "walked": True,
                             "at": [[GX0, BED, zc, 0]], "_about": "the rounded bastion on the pier's upstream face, its top a balcony at the gallery's floor"})
# the far end: the abutment on the south bank and the flight down from the door
prism("south abutment", [(-0.6, GZ0 + 0.1), (3.4, GZ0 + 0.1), (3.4, -86.0), (-0.6, -86.0)], BED, F0, about="the abutment on the south bank, the landing before the gallery's door")
add("south stair", flight((1.4, -86.0 - round(F0 / 0.17) * 0.3), (0, 1), 4.0, 0, F0, _about="the flight down from the gallery's door to the south bank"))
balustrade("south abutment balustrade", [(-0.6, GZ0), (-0.6, -86.0)], F0, closed=False, poly=[(-0.6, GZ0), (3.4, GZ0), (3.4, -86.0), (-0.6, -86.0)])
balustrade("south abutment balustrade w", [(3.4, -86.0), (3.4, GZ0)], F0, closed=False, poly=[(-0.6, GZ0), (3.4, GZ0), (3.4, -86.0), (-0.6, -86.0)])

# ================================================================================================ THE FORECOURT AND THE TOUR DES MARQUES
ISL = [(11.4, 82.9), (11.8, 47.2), (14.4, 46.7), (15.7, 45.9), (16.7, 44.7), (17.3, 43.2), (17.4, 41.7), (17.0, 40.2), (16.1, 38.9), (14.8, 37.9), (13.2, 37.4),
       (11.8, 37.3), (11.4, 32.2), (10.1, 32.3), (2.1, 32.3), (1.3, 32.3), (-0.6, 32.4), (-3.0, 32.4), (-3.9, 32.3), (-30.4, 32.6), (-33.2, 81.0), (-4.4, 82.5),
       (-0.5, 82.7), (3.0, 82.8)]
prism("forecourt", ISL, BED, G, about="the forecourt on its island (the Marques' old castle terrace), walled round in stone, the Tour des Marques on its moated corner")
balustrade("forecourt balustrade", ISL, G, gaps=[((-0.25, 32.3), 10.6), ((0.0, 82.7), 6.6)], bp=1.0, skip=1.5)
# the entrance from the avenue: a causeway over the moat at the forecourt's north end, sloping up to it
add("entrance causeway", {"type": "prism", "plan": {"rect": [6.0, 15.4]}, "height": r4(G / 2 - BED), "slope": [0, r4(-G / 15.4)], "flatRoof": True, "walked": True,
                          "at": [[0.0, BED, 90.4, 0]], "_about": "the causeway from the avenue over the moat up to the forecourt"})
# THE TOUR DES MARQUES (the Marques' keep, re-dressed by Bohier): a round tower on its terrace, the older masonry below the
# machicolation ring, Bohier's white storeys above with a dormer in the cone, a lantern on top; its stair turret beside it
TX, TZ, TR = 12.3, 42.2, 5.0
TH0 = 8.7
TY = r4(math.atan2(-0.45, -0.89))          # (the door looks south-east, toward the bridge to the logis)
TWIN = lambda sill, spr, w=1.5: {"at": 0, "width": w, "sill": sill, "springing": spr, "head": FLAT, "tracery": CROSS, "surround": {"head": "cornice"}}
add("tour des marques", {"type": "enclosure", "plan": {"sides": 20, "radius": TR}, "thickness": 1.2, "height": TH0, "glass": True, "interior": True,
                         "tiers": [{"h": 4.4, "openings": []}, {"openings": []}],
                         "faces": {"0": [{"h": 4.4, "openings": [door(0, 1.4, 2.7, SEMI)]}, {"openings": [TWIN(0.9, 3.4)]}],
                                   "5": [{"h": 4.4, "openings": [TWIN(1.4, 3.6, 1.2)]}, {"openings": [TWIN(0.9, 3.4, 1.2)]}],
                                   "10": [{"h": 4.4, "openings": [TWIN(1.4, 3.6, 1.2)]}, {"openings": []}]},
                         "at": [[TX, G, TZ, TY]], "_about": "the Tour des Marques: the keep of the Marques' castle (15th century), its door toward the forecourt"})
add("tour machicolations", {"type": "prism", "plan": {"sides": 20, "radius": r4(TR + 0.3)}, "height": 0.8, "flatRoof": True, "at": [[TX, G + TH0, TZ, TY]],
                            "_about": "the machicolation ring, Bohier's white storey corbelled on it"})
add("tour upper", {"type": "enclosure", "plan": {"sides": 20, "radius": r4(TR + 0.3)}, "thickness": 0.6, "height": 2.4, "glass": True, "interior": False,
                   "faces": {"0": [{"openings": [TWIN(0.4, 2.0, 1.2)]}], "10": [{"openings": [TWIN(0.4, 2.0, 1.0)]}]},
                   "at": [[TX, r4(G + TH0 + 0.8), TZ, TY]], "_about": "the upper storey over the machicolations"})
add("tour cap floor", {"type": "prism", "plan": {"sides": 20, "radius": r4(TR - 0.2)}, "height": 0.3, "flatRoof": True, "at": [[TX, r4(G + TH0 - 0.3), TZ, 0]]})
TC = G + TH0 + 0.8 + 2.4
add("tour cornice", {"type": "prism", "plan": {"sides": 20, "radius": r4(TR + 0.55)}, "height": 0.35, "flatRoof": True, "at": [[TX, r4(TC), TZ, TY]]})
add("tour cone", {"type": "dome", "radius": r4(TR + 0.7), "thickness": 0, "sides": 24, "head": {"profile": "trigonal", "rise": 7.6}, "at": [[TX, r4(TC + 0.35), TZ, 0]],
                  "_about": "the slate cone"})
add("tour dormer", comp("loire-dormer", {"W": 1.9, "H": 2.4, "GH": 1.5, "D": 2.2, "winW": 1.0, "RW": 3.0, "RL": 4.0, "P": 70}, [[r4(TX - 0.45 * (TR + 0.15)), r4(TC + 0.35), r4(TZ - 0.89 * (TR + 0.15)), TY]],
                        _about="the lucarne in the cone toward the forecourt"))
add("tour lantern", {"type": "enclosure", "plan": {"sides": 8, "radius": 0.85}, "thickness": 0.15, "height": 2.4, "glass": False, "interior": False,
                     "openings": [{"at": 0, "width": 0.4, "sill": 0.6, "springing": 1.7, "head": SEMI, "glass": False}],
                     "at": [[TX, r4(TC + 0.35 + 7.6 - 0.9), TZ, 0]], "_about": "the lantern on the cone's tip"})
add("tour lantern cap", {"type": "dome", "radius": 1.0, "thickness": 0, "sides": 8, "head": {"profile": "trigonal", "rise": 2.0}, "at": [[TX, r4(TC + 0.35 + 7.6 + 1.5), TZ, 0]]})
add("tour finial", {"type": "column", "radius": 0.06, "height": 1.4, "sides": 6, "taper": 0.4, "at": [[TX, r4(TC + 0.35 + 7.6 + 3.5), TZ, 0]]})
add("tour chimney", {"type": "box", "width": 1.0, "length": 1.6, "height": 7.0, "at": [[r4(TX + 1.6), r4(TC + 1.0), r4(TZ + 3.0), 0]], "_about": "the tower's chimney through the cone"})
SX, SZ = 7.4, 46.0
add("stair turret", comp("loire-turret", {"R": 2.0, "H": r4(TC + 2.6 - G), "h1": 4.4, "h2": 4.3, "cor": 0.01, "capRise": 4.8, "winW": 0.6}, [[SX, G, SZ, r4(-Q * 0.6)]],
                         _about="the tower's stair turret, rising over its cornice under its own cone"))
item("tour table", "trestle-table", [(TX, G, TZ, 0)])

# ================================================================================================ THE GARDENS
# Diane de Poitiers' parterre (1551, re-laid): a square terrace on the river east of the forecourt, walled and moated,
# eight triangular lawns round the fountain; Catherine de Medicis' smaller parterre to the west, five lawns round its basin
DIANE = [(-228.4, 16.3), (-56.9, 22.9), (-56.2, 114.5), (-54.0, 128.0), (-71.0, 136.3), (-227.8, 128.8)]
prism("diane terrace", DIANE, BED, G, about="Diane de Poitiers' garden: the walled terrace over the Cher and the canal, its top gravel")
balustrade("diane parapet", DIANE, G, gaps=[((-55.1, 121.0), 4.4)], bp=1.6, skip=2.0, h=0.8)
DL = {"200129081": [(-213, 115), (-214, 76), (-193, 77), (-192, 79), (-190, 81), (-187, 82), (-184, 82), (-181, 80), (-180, 77), (-158, 78), (-157, 82)],
      "200129082": [(-214, 30), (-214, 70), (-193, 71), (-191, 68), (-189, 66), (-186, 66), (-183, 67), (-181, 68), (-179, 71), (-158, 72), (-158, 70), (-157, 69)],
      "200129083": [(-130, 70), (-129, 74), (-107, 74), (-105, 72), (-103, 70), (-100, 70), (-97, 70), (-95, 72), (-93, 75), (-72, 76), (-72, 36)],
      "200129084": [(-72, 119), (-72, 82), (-93, 81), (-95, 84), (-98, 85), (-101, 86), (-104, 85), (-106, 83), (-107, 80), (-129, 79), (-130, 83), (-74, 120)],
      "200129093": [(-141, 118), (-141, 90), (-138, 90), (-134, 88), (-132, 86), (-80, 121)],
      "200129094": [(-207, 31), (-155, 66), (-153, 64), (-149, 62), (-146, 61), (-146, 33)],
      "200129095": [(-80, 36), (-132, 67), (-134, 64), (-137, 62), (-140, 61), (-140, 33)],
      "200129097": [(-147, 118), (-206, 115), (-155, 85), (-152, 88), (-150, 90), (-147, 90)]}
LAWNS = []
for k, pts in DL.items():
    LAWNS.append(prism(f"diane lawn {k}", pts, G, G + 0.12, about="a lawn of Diane's parterre (OSM " + k + ")"))
DF = (-144.0, 76.0)
add("diane fountain ring", {"type": "prism", "plan": {"sides": 32, "radius": 9.8}, "height": 0.12, "flatRoof": True, "walked": True, "at": [[DF[0], G, DF[1], 0]],
                            "_about": "the lawn ring round the fountain"})
LAWNS.append("diane fountain ring")
add("diane fountain basin", {"type": "enclosure", "plan": {"sides": 24, "radius": 5.4}, "thickness": 0.45, "height": 0.55, "glass": False, "interior": False, "openings": [],
                             "at": [[DF[0], G + 0.12, DF[1], 0]], "_about": "the round basin of Diane's fountain (the single jet)"})
add("diane fountain water", {"type": "prism", "plan": {"sides": 24, "radius": 5.0}, "height": 0.4, "flatRoof": True, "at": [[DF[0], G + 0.12, DF[1], 0]]})
add("diane fountain jet", {"type": "marker", "role": "flow", "at": [[DF[0], G + 0.55, DF[1], 0]], "data": {"kind": "jet", "r": 0.15, "h": 6.0}})
NDF = round(G / 0.17)
add("diane stair", flight((-55.1 + NDF * 0.3, 121.0), (-1, 0), 3.6, 0, G, _about="the flight up from the bank into Diane's garden at its north-east corner"))

CATH = [(29, 99), (32, 103), (34, 109), (50, 104), (56, 102), (109, 86), (81, 7), (54, 17), (36, 27), (28, 30), (27, 36), (31, 36), (30, 37), (30, 38), (28, 38), (28, 40),
        (26, 40), (26, 43), (27, 48)]
prism("catherine terrace", CATH, BED, G, about="Catherine de Medicis' garden: the terrace west of the forecourt, its top gravel")
balustrade("catherine parapet", CATH, G, gaps=[((40.0, 107.1), 4.4)], bp=1.6, skip=2.0, h=0.8)
CL = {"200073915": [(66, 73), (63, 59), (59, 58), (55, 57), (51, 52), (50, 47), (50, 46), (34, 41), (33, 44), (33, 48), (34, 82)],
      "200073916": [(68, 77), (34, 86), (35, 98), (71, 89)],
      "200073917": [(97, 65), (69, 73), (66, 58), (70, 56), (72, 52), (94, 57)],
      "200073918": [(58, 36), (54, 38), (51, 42), (51, 43), (34, 39), (36, 34), (39, 30), (54, 22)],
      "200073919": [(60, 36), (56, 21), (77, 14), (92, 54), (73, 49), (73, 47), (71, 42), (68, 38), (64, 36)]}
for k, pts in CL.items():
    LAWNS.append(prism(f"catherine lawn {k}", pts, G, G + 0.12, about="a lawn of Catherine's parterre (OSM " + k + ")"))
CF = (61.9, 46.9)
add("catherine basin", {"type": "enclosure", "plan": {"sides": 32, "radius": 7.9}, "thickness": 0.45, "height": 0.55, "glass": False, "interior": False, "openings": [],
                        "at": [[CF[0], G, CF[1], 0]], "_about": "Catherine's round basin"})
add("catherine water", {"type": "prism", "plan": {"sides": 32, "radius": 7.5}, "height": 0.4, "flatRoof": True, "at": [[CF[0], G, CF[1], 0]]})
add("catherine stair", flight((40.0, 107.1 + NDF * 0.3), (0, -1), 3.6, 0, G, _about="the flight up from the bank into Catherine's garden"))

# the parterres drawn in box: a low clipped hedge round every lawn, so the pattern reads from above; yew cones at the
# lawns' corners (set in from each sharp corner along its bisector)
LG = G + 0.12
add("parterre hedges", {"type": "bars", "w": 0.45, "h": 0.5, "closed": True, "caps": False,
                        "paths": [[[x, r4(LG + 0.25), z] for x, z in pts] for pts in list(DL.values()) + list(CL.values())],
                        "_about": "the box hedges edging the parterres' lawns"})
def corners(pts, inset=1.8, maxang=125):
    n, out = len(pts), []
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    for i in range(n):
        (ax, az), (bx, bz), (cx, cz) = pts[i - 1], pts[i], pts[(i + 1) % n]
        u = (ax - bx, az - bz); v = (cx - bx, cz - bz); lu, lv = math.hypot(*u), math.hypot(*v)
        if lu < 3 or lv < 3: continue
        u = (u[0] / lu, u[1] / lu); v = (v[0] / lv, v[1] / lv)
        cross_ = u[0] * v[1] - u[1] * v[0]
        if (cross_ > 0) == (area > 0): continue                    # (a reflex corner)
        ang = math.degrees(math.acos(max(-1, min(1, u[0] * v[0] + u[1] * v[1]))))
        if ang > maxang: continue
        bis = (u[0] + v[0], u[1] + v[1]); lb = math.hypot(*bis)
        out.append((bx + bis[0] / lb * inset, bz + bis[1] / lb * inset))
    return out
TOPI = [p for pts in list(DL.values()) + list(CL.values()) for p in corners(pts)]
add("parterre topiary", {"type": "column", "radius": 0.6, "height": 2.2, "sides": 10, "taper": 0.05, "at": [[r4(x), r4(LG), r4(z), 0] for x, z in TOPI],
                         "_about": "clipped yew cones at the lawns' corners"})
add("fountain topiary", {"type": "loft", "axis": "y", "sides": 12, "smooth": 2,
                         "sections": [{"s": 0, "u": 0, "v": 0, "a": 0.05, "b": 0.05}, {"s": 0.35, "u": 0, "v": 0, "a": 0.75, "b": 0.75},
                                      {"s": 0.9, "u": 0, "v": 0, "a": 0.9, "b": 0.9}, {"s": 1.45, "u": 0, "v": 0, "a": 0.75, "b": 0.75}, {"s": 1.8, "u": 0, "v": 0, "a": 0.05, "b": 0.05}],
                         "at": [[r4(DF[0] + 8.0 * math.cos(a)), r4(LG), r4(DF[1] + 8.0 * math.sin(a)), 0] for a in [k * math.pi / 4 + math.pi / 8 for k in range(8)]]
                              + [[r4(CF[0] + 10.2 * math.cos(a)), r4(G), r4(CF[1] + 10.2 * math.sin(a)), 0] for a in [k * math.pi / 3 for k in range(6)]],
                         "_about": "clipped box balls round the fountain and the basin"})

# the forecourt: pale gravel, two lawns either side of the walk from the causeway to the bridge, a double row of clipped
# limes along it (the avenue of planes runs on beyond the causeway, off the site)
FL = {"east": [(-29.0, 40.0), (-6.5, 40.0), (-6.5, 78.5), (-31.2, 78.5)], "west": [(5.5, 51.0), (10.4, 51.0), (10.4, 78.5), (5.5, 78.5)]}
for k, pts in FL.items():
    LAWNS.append(prism(f"forecourt lawn {k}", pts, G, G + 0.12, about="a lawn strip beside the forecourt's walk"))
ALLEE = [(x, z) for x in (-8.3, 7.4) for z in (55.0, 61.0, 67.0, 73.0)] + [(-8.3, 43.0), (-8.3, 49.0)]
add("allee trunks", {"type": "column", "radius": 0.22, "height": 3.0, "sides": 8, "taper": 0.8, "at": [[x, r4(LG), z, 0] for x, z in ALLEE],
                     "_about": "the limes' trunks"})
add("allee crowns", {"type": "loft", "axis": "y", "sides": 14, "smooth": 2,
                     "sections": [{"s": 0, "u": 0, "v": 0, "a": 0.3, "b": 0.3}, {"s": 0.7, "u": 0, "v": 0, "a": 1.9, "b": 1.9}, {"s": 2.4, "u": 0, "v": 0, "a": 2.3, "b": 2.3},
                                  {"s": 4.0, "u": 0, "v": 0, "a": 1.7, "b": 1.7}, {"s": 4.8, "u": 0, "v": 0, "a": 0.1, "b": 0.1}],
                     "at": [[x, r4(LG + 2.6), z, 0] for x, z in ALLEE], "_about": "the limes' crowns, clipped round"})

# ================================================================================================ THE WATER (site.moat: a pool)
RIVER = [(545.2, 98.7), (350.1, 42.4), (271.1, 28.1), (174.6, 10.5), (80.7, 7.3), (53.7, 16.9), (36.0, 26.8), (27.8, 30.2), (27.1, 35.8), (30.5, 36.4), (30.4, 37.1),
         (30.2, 38.1), (28.0, 37.7), (27.6, 40.4), (26.4, 40.1), (26.2, 43.3), (26.7, 47.7), (28.5, 98.8), (1.7, 98.3), (-33.0, 97.9), (-33.2, 94.3), (-34.9, 93.6),
         (-36.3, 94.8), (-38.4, 95.0), (-40.4, 95.3), (-42.2, 93.8), (-44.2, 93.3), (-46.3, 94.2), (-47.5, 96.5), (-46.5, 98.6), (-46.9, 106.7), (-49.4, 108.9),
         (-50.4, 111.6), (-52.0, 114.3), (-56.2, 114.5), (-56.9, 22.9), (-233.5, 15.2), (-239.5, 15.0), (-239.6, 3.2), (-362.6, -22.4), (-393.0, -82.7),
         (-269.9, -63.6), (-186.0, -79.9), (-152.2, -84.5), (-113.7, -84.5), (-33.1, -83.7), (-19.1, -84.4), (-6.9, -83.8), (0.3, -83.2), (8.6, -82.1), (19.4, -79.8),
         (56.7, -75.1), (108.7, -66.3), (152.7, -60.7), (166.3, -61.2), (177.0, -59.7), (196.2, -55.5), (347.1, -34.0), (485.0, 1.8)]
CANAL = [(-228.3, 16.3), (-228.6, 20.1), (-227.8, 128.8), (-71.1, 136.3), (-71.1, 138.5), (-63.5, 138.8), (-63.4, 136.8), (-54.3, 137.2), (-54.0, 131.0), (-54.2, 128.1),
         (-51.4, 128.4), (-49.9, 129.1), (-47.7, 132.0), (-46.3, 136.2), (-46.0, 140.4), (-47.3, 144.1), (-50.1, 147.9), (-52.6, 149.1), (-53.3, 155.5), (-60.3, 187.7),
         (-3.4, 186.6), (-3.4, 190.3), (-3.5, 193.8), (-9.4, 193.9), (-62.8, 195.4), (-69.6, 194.7), (-67.7, 187.1), (-60.0, 155.3), (-59.3, 148.9), (-58.8, 144.8),
         (-61.2, 144.4), (-239.3, 139.7), (-239.5, 20.0)]
k = RIVER.index((-233.5, 15.2))
SHORE = RIVER[:k + 1] + CANAL + RIVER[k + 1:]
PX0, PX1, PZ0, PZ1 = -245.0, 118.0, -92.0, 150.0
def clip(poly, f):
    out = []
    for i in range(len(poly)):
        p, q = poly[i - 1], poly[i]; fp, fq = f(p), f(q)
        cut = lambda: (p[0] + (q[0] - p[0]) * fp / (fp - fq), p[1] + (q[1] - p[1]) * fp / (fp - fq))
        if fq >= 0:
            if fp < 0: out.append(cut())
            out.append(q)
        elif fp >= 0: out.append(cut())
    return out
for f in (lambda p: p[0] - PX0, lambda p: PX1 - p[0], lambda p: p[1] - PZ0, lambda p: PZ1 - p[1]): SHORE = clip(SHORE, f)
# where the clip left a straight cut along the site's edge (the river's two ends, the canal's), the bank is drawn round
# instead: the cut bowed in toward the water, so the river comes to a rounded end, not a square one
def round_cuts(P, e=0.01):
    edge = lambda p: ("x0" if abs(p[0] - PX0) < e else "x1" if abs(p[0] - PX1) < e else "z0" if abs(p[1] - PZ0) < e else "z1" if abs(p[1] - PZ1) < e else None)
    inward = {"x0": (1, 0), "x1": (-1, 0), "z0": (0, 1), "z1": (0, -1)}
    out = []
    for i in range(len(P)):
        p, q = P[i], P[(i + 1) % len(P)]
        out.append(p)
        ep = edge(p)
        if ep and ep == edge(q):
            L = math.hypot(q[0] - p[0], q[1] - p[1]); dep = min(0.45 * L, 32.0); nx, nz = inward[ep]
            for k in range(1, 16):
                t = k / 16; s = math.sin(math.pi * t) ** 0.7
                out.append((p[0] + (q[0] - p[0]) * t + nx * dep * s, p[1] + (q[1] - p[1]) * t + nz * dep * s))
    return out
SHORE = round_cuts(SHORE)
PCX, PCZ = (PX0 + PX1) / 2, (PZ0 + PZ1) / 2
rel = lambda pts: [[r4(x - PCX), r4(z - PCZ)] for x, z in pts]
RIVER_ISLAND = [(-90.7, -33.3), (-75.0, -41.4), (-76.1, -44.6), (-82.0, -47.6), (-91.5, -45.7), (-99.6, -47.0), (-124.0, -42.1), (-131.0, -38.0), (-133.1, -34.9), (-128.3, -32.2)]
MOAT = {"pool": True, "hw": r4((PX1 - PX0) / 2), "hd": r4((PZ1 - PZ0) / 2), "w": 0, "depth": 4.4, "surface": WL, "x": r4(PCX), "z": r4(PCZ),
        "shore": rel(SHORE), "islands": [rel(ISL), rel(RIVER_ISLAND)]}

# ================================================================================================ THE DEFINITION
doc = {"name": "Chateau de Chenonceau",
       "_about": "THE CHATEAU DE CHENONCEAU on the Cher (the logis 1514-22, Philibert de l'Orme's bridge 1556-59, Jean Bullant's gallery 1576): the square corps de logis on the "
                 "piers of the old mill in the river -- white tuffeau, cross windows, four corbelled corner turrets under slate cones, the steep slate roof with its rich lucarnes "
                 "and tall chimneys, the chapel with its apse and the library on the east front -- the two-storey gallery 60 m across the river on five arches with its oculus "
                 "dormers, the bridge north to the forecourt island and the Tour des Marques on its moated corner, Diane de Poitiers' and Catherine de Medicis' parterres; "
                 "the water a pool from OSM's river and canal. Inside: the rib-vaulted vestibule, the rooms either side on both floors, the straight rampe-sur-rampe stair, "
                 "the chapel, the library, the gallery on both levels (the chequered floor below). (tools/archgen/chenonceau.py)",
       "params": {"detail": 4}, "railing": {"type": "balusters"}, "site": {"moat": MOAT}, "build": build, "parts": parts}

# ================================================================================================ THE FINISH
fin = {"name": "Chateau de Chenonceau", "building": "architecture/chenonceau",
       "_about": "Chenonceau: the white tuffeau of the Loire in fine ashlar on every wall, blue-grey slate on every roof, cone and dormer hip, lead on the roof's flat and the "
                 "finials; the piers, the bridge and the terrace walls in coursed stone, the Tour des Marques' older masonry greyer under its white top; inside, the vestibule "
                 "flagged, the rooms in terracotta tiles, the gallery's lower floor a diagonal chequer of black and white, its upper floor oak, timber ceilings.",
       "stone": {"color": "#e8e2d2", "accent": "#cfc7b2", "pat": "ashlar fine"},
       "rules": [
           {"parts": ["chimney caps", "gallery chimney cap", "tour finial"], "pattern": "roofs/sheet metal", "palette": "lead", "_about": "lead"},
           {"parts": [f"{t}/finial" for t in TUR + ["stair turret"]], "pattern": "roofs/sheet metal", "palette": "lead", "_about": "the lead finials"},
           {"parts": ["kind:glass"], "pattern": "glass/quarries", "palette": "grisaille", "map": "opening", "_about": "leaded quarries"},
           {"parts": ["parterre hedges", "parterre topiary", "fountain topiary"], "color": "#34502a", "accent": "#2a4322", "_about": "clipped box and yew"},
           {"parts": ["allee crowns"], "color": "#4a6a32", "accent": "#3c5a28", "_about": "the limes' clipped crowns"},
           {"parts": ["allee trunks"], "color": "#5a4a3a", "accent": "#4a3c2e", "_about": "their trunks"},
           {"parts": ["chapel"], "surface": "wall", "side": "in", "pattern": "stone/ashlar fine", "palette": "tuffeau"},
           {"parts": ["vestibule vault", "chapel vault"], "pattern": "stone/ashlar fine", "palette": "tuffeau"},
           {"parts": ["vestibule ribs", "chapel ribs"], "pattern": "stone/ashlar fine", "palette": "limestone"},
           {"surface": "ceiling", "side": "in", "pattern": "timber/boards", "palette": "walnut", "_about": "the joisted ceilings"},
           {"parts": ["kind:roof", "kind:dome", "tour lantern cap"], "surface": "wall", "pattern": "stone/ashlar fine", "palette": "tuffeau", "_about": "a roof's upright ends in stone"},
           {"parts": ["kind:roof", "kind:dome", "tour lantern cap"] + [f"{t}/cap" for t in TUR + ["stair turret"]], "pattern": "roofs/slate", "palette": "chenonceau-slate",
            "_about": "blue-grey slate on every roof and cone"},
           {"parts": [f"{d}/roof" for d in DORM + ["tour dormer"]] + [f"{GDORM}/roof"], "pattern": "roofs/slate", "palette": "chenonceau-slate"},
           {"parts": LAWNS, "surface": "floor", "pattern": "materials/grass", "palette": "lawn", "_about": "the parterres' lawns"},
           {"parts": LAWNS, "pattern": "stone/ashlar", "palette": "limestone", "_about": "their kerbs"},
           {"parts": ["diane terrace", "catherine terrace"], "surface": "floor", "pattern": "stone/sand", "palette": "loire-gravel", "_about": "pale sandy gravel walks"},
           {"parts": ["forecourt", "entrance causeway"], "surface": "floor", "pattern": "stone/sand", "palette": "loire-gravel"},
           {"parts": ["diane fountain water", "catherine water"], "color": "#4f6a72", "accent": "#425a62", "_about": "the basins' water"},
           {"parts": ["north pier", "south pier", "bridge", "north bridge", "north bridge foot", "south abutment", "mill race vault", "diane terrace", "catherine terrace",
                      "forecourt", "entrance causeway"] + [f"cutwater {k + 1}" for k in range(4)] + [f"bastion {k + 1}" for k in range(4)],
            "surface": "wall", "pattern": "stone/ashlar", "palette": "sandstone-grey", "_about": "the piers, the bridge and the terrace walls in coursed stone, weathered"},
           {"parts": ["mill race vault"], "pattern": "stone/ashlar", "palette": "sandstone-grey"},
           {"parts": ["tour des marques"], "side": "out", "pattern": "stone/ashlar", "palette": "sandstone-grey", "_about": "the keep's older masonry, greyer"},
           {"parts": ["gallery paving"], "pattern": "floors/checker diagonal", "palette": "marble-bw"},
           {"parts": ["bridge"], "surface": "floor", "within": [GX0, GZ0, GX1, GZ1], "pattern": "floors/checker diagonal", "palette": "marble-bw",
            "_about": "the gallery's floor: the black-and-white chequer, laid diagonally"},
           {"parts": ["gallery floor"], "surface": "floor", "pattern": "timber/herringbone", "palette": "oak", "_about": "the upper gallery's oak floor"},
           {"parts": ["vestibule floor", "east rooms floor", "salon floor", "francois floor", "stair hall floor", "stair landing floor", "library floor"], "surface": "floor",
            "pattern": "floors/terracotta", "palette": "terracotta", "_about": "the upper rooms' tiled floors"},
           {"parts": ["vestibule paving", "great stair"], "pattern": "floors/flagstones", "palette": "limestone", "_about": "the vestibule's flags, the stair's stone"},
           {"surface": "floor", "side": "in", "pattern": "floors/terracotta", "palette": "terracotta", "_about": "terracotta tiles in the rooms"},
           {"surface": "wall", "side": "in", "pattern": "stone/ashlar fine", "palette": "tuffeau", "_about": "the tuffeau walls inside"},
           {"parts": ["kind:moulding"], "pattern": "stone/ashlar fine", "palette": "tuffeau"},
           {"parts": BAL, "pattern": "stone/ashlar fine", "palette": "tuffeau", "_about": "the balustrades"},
           {"surface": "floor", "pattern": "floors/flagstones", "palette": "limestone", "_about": "terraces and steps outside"},
           {"surface": "roof", "pattern": "floors/flagstones", "palette": "limestone"},
           {"surface": "wall", "pattern": "stone/ashlar fine", "palette": "tuffeau", "_about": "the white tuffeau"}]}

doors = {"name": "Chateau de Chenonceau: doors", "building": "chenonceau",
         "_about": "Chenonceau: the main door of the logis under its balcony, the gallery's door to the south bank, the chapel's, the Tour des Marques' -- carved oak",
         "doors": [{"_about": "the logis' main door on the north front", "part": "logis", "near": [[-0.8, LZ1]], "style": "palace", "color": "#3b2616", "leafH": 2.9},
                   {"_about": "the gallery's door to the south bank", "part": "gallery", "near": [[1.4, GZ0]], "style": "classical", "color": "#3b2616"},
                   {"_about": "the chapel's door from the Salle des Gardes", "part": "chapel", "near": [[-12.8, 8.0]], "style": "gothic", "color": "#3b2616"},
                   {"_about": "the Tour des Marques' door", "part": "tour des marques", "near": [[r4(TX - 0.45 * TR), r4(TZ - 0.89 * TR)]], "style": "tower", "color": "#3b2616"}]}

W = lambda rel_, d: open(os.path.join(ROOT, rel_), "w").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
if __name__ == "__main__":
    for nm, d in COMPONENTS.items(): W(f"assets/architecture/components/{nm}.json", d)
    W("assets/architecture/chenonceau.json", doc)
    W("assets/finishes/chenonceau.json", fin)
    W("assets/doors/chenonceau.json", doors)
    print("chenonceau:", len(parts), "parts; shore", len(SHORE), "points")
