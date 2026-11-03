# SCHLOSS DRACHENBURG (Königswinter, 1882-84; Tüshaus & von Abbema, the Kunsthalle and the Nordturm by Leo von Abbema / Wilhelm
# Hoffmann) on its terrace high over the Rhine, from the historicist castle's vocabulary (tools/archgen/historicism.py).
# THE FRAME: the castle's long axis runs 159 degrees (NNW-SSE); +x is SOUTH-south-east along it, +z is the RHINE FRONT (west-south-west).
# The origin is OpenStreetMap's point 50.66867 N, 7.20634 E, and the PLAN IS OSM's: the building (way 118449147) and the terrace wall
# (way 118449146, the castle wall with the round bastion) turned into this frame. So: the plan measured; every HEIGHT estimated from
# photographs (Wikimedia Commons: the aerial from the Rhine side and the view from the Drachenfels), scaled by the Hauptturm's 7.8 m
# width -- the terrace 5 m, the main house's eaves 13 m over it, the Kunsthalle's 11.5, the Hauptturm about 41 m to its tip, the
# Nordturm 24. The hill is a battered mound (its top 3.4 m on the uphill -z side, falling to the Rhine front under the
# terrace); the Vorburg (the outer bailey, 95 m down the hill to the north-east) a plain gabled hall with its gate and dormers.
# Not built: the interiors (the stair hall, the Nibelungen hall): the doors open on plain rooms.
import os, json, math
from historicism import write_components, comp, block, gable, gabled, storey_row, row, crest_rect, parapets, flight, place, POINTED, ROOT, r4
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n); return n

G = 5.0                     # the terrace's top: the ground floor of every building on it
YK = G + 13.0               # the main house's eaves
EK = 11.5                   # the Kunsthalle's walls over the terrace
Q = math.pi / 2
TRAC = {"profile": "pointed", "spread": 0.55}
FLAT = {"profile": "flat"}
SEG = {"profile": "segmental", "rise": 0.35}
# A DOORWAY between rooms, the same in both walls where two blocks stand back to back (an opening on each block's face);
# THROUGH: one on every storey (the main house's three), GROUND: the ground storey's only
DOOR = lambda a, w=1.3, h=2.4: {"at": r4(a), "width": w, "sill": 0, "springing": h, "head": SEG, "glass": False}
THROUGH = lambda *ats: (lambda L, j, hs: [DOOR(a) for a in ats])
GROUND = lambda *ats: (lambda L, j, hs: [DOOR(a) for a in ats] if j == 0 else [])
PORTAL = lambda a: (lambda L, j, hs: [{"at": a, "width": 1.6, "sill": 0, "springing": 2.7, "head": POINTED, "glass": False}] if j == 0 else [])

# ---- THE TERRACE: OSM's castle wall as a podium G high, crenellated all round, the round bastion on the Rhine front
TP = [(-55.4, 13.7), (-50.8, 13.0), (-50.5, 15.0), (-49.6, 20.2), (-17.8, 14.5), (-17.3, 18.9), (-10.7, 18.0), (-11.1, 15.5), (-9.0, 15.1), (-8.6, 17.7), (0.4, 16.5),
      (2.1, 18.3), (4.4, 19.0), (7.3, 18.7), (9.6, 17.2), (11.1, 14.9), (19.4, 13.4), (19.0, 10.7), (29.7, 9.0), (29.3, 6.5), (49.9, 2.8), (52.3, 4.4), (55.5, -0.3),
      (53.1, -1.8), (49.8, -20.8), (25.5, -16.6), (25.2, -18.5), (8.2, -15.6), (7.1, -17.1), (5.1, -17.9), (0.2, -17.1), (-4.0, -16.4), (-5.7, -15.4), (-6.4, -13.5),
      (-21.5, -10.8), (-21.7, -12.3), (-24.6, -11.8), (-28.4, -11.1), (-28.2, -10.0), (-38.1, -8.4), (-37.6, -5.3), (-52.8, -2.8), (-51.6, 4.9), (-56.7, 5.8), (-56.1, 9.4)]

def z_at(p, q, x):          # (where the terrace's edge p-q crosses x)
    return p[1] + (q[1] - p[1]) * (x - p[0]) / (q[0] - p[0])
def inside(x, z, poly):     # (is (x, z) within the outline)
    c = False
    for i in range(len(poly)):
        (x0, z0), (x1, z1) = poly[i], poly[i - 1]
        if (z0 > z) != (z1 > z) and x < x0 + (x1 - x0) * (z - z0) / (z1 - z0): c = not c
    return c

# THE VENUSTERRASSE: the terrace's south end is a garden a flight LOWER than the rest (the 1887 plan: a walled garden
# beyond the house's south front, the fountain in its middle, the Freitreppe up from it to the terrace). Its frame is its
# own long walls' (OSM's), turned GA from the castle's: `gu` along it (away from the house), `gv` across it (toward the
# Rhine); its middle line half-way between them. The terrace is cut square to that frame GU0 from the garden's middle.
GL = 3.5                    # the garden's floor (the hill's top under it, 3.4)
GA = (math.atan2(TP[20][1] - TP[19][1], TP[20][0] - TP[19][0]) + math.atan2(TP[24][1] - TP[25][1], TP[24][0] - TP[25][0])) / 2
gu, gv, GYAW = (math.cos(GA), math.sin(GA)), (-math.sin(GA), math.cos(GA)), -GA      # (GYAW: a placement's yaw that turns its +x along gu)
GX = 39.5
GC = (GX, (z_at(TP[19], TP[20], GX) + z_at(TP[25], TP[24], GX)) / 2)
gat = lambda u, v: (r4(GC[0] + gu[0] * u + gv[0] * v), r4(GC[1] + gu[1] * u + gv[1] * v))   # (garden frame -> x, z)
gof = lambda p: ((p[0] - GC[0]) * gu[0] + (p[1] - GC[1]) * gu[1], (p[0] - GC[0]) * gv[0] + (p[1] - GC[1]) * gv[1])   # (x, z -> garden frame)
GU0 = -13.5                 # the cut: the retaining wall's face, the Freitreppe's top
def clip(poly, f):          # (Sutherland-Hodgman: the part of the outline where f >= 0, f linear)
    out = []
    for i in range(len(poly)):
        p, q = poly[i - 1], poly[i]; fp, fq = f(p), f(q)
        cut = lambda: (r4(p[0] + (q[0] - p[0]) * fp / (fp - fq)), r4(p[1] + (q[1] - p[1]) * fp / (fp - fq)))
        if fq >= 0:
            if fp < 0: out.append(cut())
            out.append(q)
        elif fp >= 0: out.append(cut())
    return out
TPU = clip(TP, lambda p: GU0 - gof(p)[0])
TPL = clip(TP, lambda p: gof(p)[0] - GU0)
k = next(i for i in range(len(TPL)) if abs(gof(TPL[i])[0] - GU0) < 1e-3 and abs(gof(TPL[(i + 1) % len(TPL)])[0] - GU0) < 1e-3)
TPL_RUN = TPL[k + 1:] + TPL[:k + 1]                       # (the garden's outline from one end of the cut round to the other)
add("terrace", {"type": "prism", "plan": {"points": [[x, z] for x, z in TPU]}, "height": G, "flatRoof": True, "walked": True, "at": [[0, 0, 0, 0]],
                "_about": "the terrace on the hillside: OSM's castle wall (way 118449146) as a podium, its round bastion on the Rhine front -- the house's level"})
add("venusterrasse", {"type": "prism", "plan": {"points": [[x, z] for x, z in TPL]}, "height": GL, "flatRoof": True, "walked": True, "at": [[0, 0, 0, 0]],
                      "_about": "the Venusterrasse: the terrace's south end, the walled garden a flight below the house's level"})


# THE HILL: a mound whose top (HILL) runs under the uphill (-z) half of the terrace, battered down toward the Rhine (+z),
# to the south, the north and the far uphill side
HILL = 3.4
add("hill", {"type": "prism", "plan": {"rect": [122, 45]}, "height": HILL, "flatRoof": True, "walked": True, "batter": {"out": 14, "power": 1}, "at": [[-1.0, 0, -22.5, 0]],
             "_about": "the hillside the terrace is cut into: its top 3.4 m up on the uphill side, falling to the Rhine front under the terrace"})

# THE BASTION: a pronounced half-round on the Rhine front, crenellated round its arc; the flights run down along its flanks
# to a landing before it, a flight goes down from that to the path and the gatehouse below
BC, BR = (5.6, 15.0), 7.5
add("bastion", {"type": "prism", "plan": {"sides": 32, "radius": BR}, "height": G, "flatRoof": True, "walked": True, "at": [[BC[0], 0, BC[1], 0]],
                "_about": "the round bastion on the Rhine front, its top the terrace's"})
arc = [a for a in range(-180, 181, 3) if not inside(BC[0] + BR * math.sin(math.radians(a)), BC[1] + BR * math.cos(math.radians(a)), TP)]
a0, a1 = min(arc) - 3, max(arc) + 3
ARC = [(r4(BC[0] + BR * math.sin(math.radians(a))), r4(BC[1] + BR * math.cos(math.radians(a)))) for a in [a0 + (a1 - a0) * k / 14 for k in range(15)]]
BASTION = parapets(add, "bastion parapet", ARC, G, closed=False)
SW = 2.4                    # the flights' width
LAND = 1.6                  # the landing before the bastion
STAIRS = {"bastion stair north": ((-3.4, z_at(TP[9], TP[10], -3.4)), (0, 1), LAND), "bastion stair south": ((14.8, z_at(TP[15], TP[16], 14.8)), (0, 1), LAND),
          "portal stair north": ((-3.0, z_at(TP[30], TP[31], -3.0)), (0, -1), HILL), "portal stair south": ((3.6, z_at(TP[29], TP[30], 3.6)), (0, -1), HILL)}
for nm, ((x, z), (dx, dz), base) in STAIRS.items():
    n = round((G - base) / 0.17)
    foot = (x + dx * n * 0.3, z + dz * n * 0.3)
    add(nm, flight(foot, (-dx, -dz), SW, base, G, _about="a flight from the hillside up to the terrace" if dz < 0 else "down from the terrace along the bastion's flank to the landing before it"))
# THE FREITREPPE: the flight from the garden up to the terrace on the garden's middle line, its top on the cut
FW, FN = 3.4, round((G - GL) / 0.17)
FTOP = gat(GU0, 0)
add("freitreppe", flight(gat(GU0 + FN * 0.3, 0), (-gu[0], -gu[1]), FW, GL, G, _about="the Freitreppe: up from the Venusterrasse to the terrace before the south front"))
PARAPET = parapets(add, "terrace parapet", TPU, G, gaps=[(xz, SW + 0.3) for xz, _, _ in STAIRS.values()] + [(FTOP, FW + 0.3)], holes=[(BC, BR)])
GREAR = ((TP[24][0] + TP[25][0]) / 2, (TP[24][1] + TP[25][1]) / 2)
GARDEN_WALL = parapets(add, "venusterrasse parapet", TPL_RUN, GL, closed=False, gaps=[(GREAR, 2.4)])
LX0, LX1, LZ0, LZ1 = -5.2, 16.6, 19.8, 27.5
add("landing", {"type": "prism", "plan": {"rect": [r4(LX1 - LX0), r4(LZ1 - LZ0)]}, "height": LAND, "flatRoof": True, "walked": True, "at": [[r4((LX0 + LX1) / 2), 0, r4((LZ0 + LZ1) / 2), 0]],
                "_about": "the landing before the bastion where its two flights meet"})
LANDING_WALL = parapets(add, "landing parapet", [(LX0, LZ1), (LX1, LZ1)], LAND, h=0.9, step=1.6, t=0.4, closed=False, gaps=[((BC[0], LZ1), 3.4)])
n = round(LAND / 0.17)
add("bastion stair", flight((BC[0], LZ1 + n * 0.3), (0, -1), 3.0, 0, LAND, _about="the flight from the path up to the landing"))
# the gatehouse on the path below: an arch through it, crenellated round its flat top
GX0, GX1, GZ0, GZ1, GH = 1.6, 9.6, 33.0, 38.0, 6.5
arch = lambda L, j, hs: [{"at": 0, "width": 3.0, "sill": 0, "springing": 3.2, "head": TRAC, "glass": False}]
block(add, "gatehouse", GX0, GX1, GZ0, GZ1, 0, GH, 1, {0: arch, 2: arch, 1: lambda L, j, hs: storey_row(L, [0], j, hs, w=0.8, head=TRAC), 3: lambda L, j, hs: storey_row(L, [0], j, hs, w=0.8, head=TRAC)},
      t=0.7, about="the gatehouse on the path up from the Rhine: a pointed arch through it", interior=False)
add("gatehouse deck", {"type": "prism", "plan": {"rect": [GX1 - GX0, GZ1 - GZ0]}, "height": 0.3, "flatRoof": True, "at": [[r4((GX0 + GX1) / 2), GH, r4((GZ0 + GZ1) / 2), 0]], "standsOn": ["gatehouse"]})
GATE = parapets(add, "gatehouse battlements", [(GX0, GZ0), (GX1, GZ0), (GX1, GZ1), (GX0, GZ1)], GH + 0.3, h=1.0, step=1.6, t=0.4)

# ---- THE TURRETS of the terrace's corners, from the ground below it (components/cone-turret): slate spikes, the cone
# capR = R + corOut at its eave and 3 (on the house's towers 3.5) times that tall
def turret(name, x, z, y, about, **p):
    cr = p["R"] * 1.12
    p.setdefault("capR", r4(cr)); p.setdefault("capRise", r4(cr * p.pop("_k", 3.0)))
    add(name, comp("cone-turret", p, [[x, y, z, p.pop("_yaw", 0)]], _about=about))
turret("terrace turret north", TP[3][0], TP[3][1], 0, "the round turret on the terrace's north-west corner, from the slope below", R=2.1, H=G + 7.5, door="no")
turret("terrace turret east", TP[41][0], TP[41][1], 0, "the round turret on the terrace's north-east corner", R=2.1, H=G + 6.5, door="no")
turret("terrace turret south", 53.2, 1.6, 0, "the squat turret at the terrace's south end", R=1.8, H=G + 3.5, capR=2.2, capRise=2.2, door="no", capSides=12)

# ---- THE MAIN HOUSE (Kernbau): the block, the south wing with its gable, the corner by the round tower, the gable bay on the Rhine front
ROSE = lambda w, s: {"at": 0, "width": w, "sill": s, "springing": s, "head": {"profile": "semicircular"}, "foot": {"profile": "semicircular"}, "tracery": {}}
BAY_ARCH = lambda a: [{"at": a, "width": 2.4, "sill": 0, "springing": 2.3, "head": POINTED, "glass": False}]   # (the dining room into the gable bay)
# A: the block x -1..12.2, z -10.8..6.6 (the Hauptturm and the stair hall against its -x face, the south wing against its +x face)
block(add, "house", -1.0, 12.2, -10.8, 6.6, G, 13.0, 3,
      {0: lambda L, j, hs: storey_row(L, [4.8], j, hs, door=4.8) + (BAY_ARCH(-1.6) if j == 0 else []),
       2: lambda L, j, hs: storey_row(L, [5.6 - x for x in (0.3, 4.5, 7.5, 10.5)], j, hs, door=5.3, head=SEG),
       1: THROUGH(2.7, -6.6), 3: THROUGH(-2.7)},
      t=0.8, skip=(1, 3), about="the main house's block: three storeys over the terrace, the portal at the back (east) under its porch")
# B: the south wing, its front the south front between the round towers
block(add, "south wing", 12.2, 18.4, -6.6, 2.6, G, 13.0, 3,
      {1: lambda L, j, hs: ([{"at": 0.3, "width": 1.6, "sill": 0, "springing": 2.9, "head": POINTED, "glass": False}] if j == 0 else
                            [{"at": a, "width": 1.2, "sill": 1.2, "springing": 3.3, "head": TRAC} for a in (3.4, -2.6)] + ([{"at": 0.3, "width": 1.1, "sill": 0.5, "springing": 2.6, "head": FLAT}] if j == 1 else
                            [{"at": a, "width": 0.9, "sill": 1.0, "springing": 3.0, "head": TRAC} for a in (-0.35, 0.95)])),
       2: lambda L, j, hs: storey_row(L, [-2.0], j, hs, w=1.0), 3: THROUGH(-2.8)},
      t=0.8, skip=(0, 3), about="the south wing: its front the south front -- the porch, the oriel over it, the gable -- between the two round towers")
block(add, "corner wing", 12.2, 17.2, 2.6, 6.6, G, 13.0, 3,
      {0: lambda L, j, hs: storey_row(L, [-1.2, 1.3], j, hs, w=1.1, door=-1.2), 3: THROUGH(-0.1)},
      t=0.7, skip=(1, 2, 3), about="the corner between the south wing and the round tower, behind the loggia")
# C: the gable bay on the Rhine front, a storey's worth taller than the eaves for its rose
CH = 14.2
block(add, "gable bay", 0.4, 8.6, 6.6, 10.0, G, CH, 3,
      {0: lambda L, j, hs: ([{"at": a, "width": 1.5, "sill": 0.9, "springing": 3.4, "head": TRAC, "tracery": {}} for a in (-1.8, 1.8)] if j == 0 else
                            [{"at": a, "width": 1.2, "sill": 0.9, "springing": 3.4, "head": TRAC, "tracery": {}} for a in (-1.6, 0, 1.6)] if j == 1 else
                            [ROSE(3.0, 2.5)]),
       1: lambda L, j, hs: storey_row(L, [0], j, hs, w=0.9, head=TRAC), 3: lambda L, j, hs: storey_row(L, [0], j, hs, w=0.9, head=TRAC),
       2: lambda L, j, hs: BAY_ARCH(0.5) if j == 0 else []},
      t=0.8, skip=(2,), about="the gable bay on the Rhine front: tall traceried windows, a three-light one over them, the rose under its gable")
# (its roof running back into the house's, closed by its stone gable)
RG = gabled(add, "gable bay", 4.5, 10.0, 0, 8.5, 8.6, 56, G + CH, t=0.55, about="its stone gable, pinnacles on the kneelers and the apex")
# the loggia before the house (the Venusterrasse's arcade) and its balcony
block(add, "loggia", 9.0, 17.0, 6.6, 9.6, G, 5.0, 1,
      {0: lambda L, j, hs: row(L, 4, 1.35, 0, 3.3, TRAC, edge=0.6, glass=False), 1: lambda L, j, hs: [{"at": -0.4, "width": 1.3, "sill": 0, "springing": 3.3, "head": TRAC, "glass": False}],
       3: lambda L, j, hs: [{"at": 0.4, "width": 1.3, "sill": 0, "springing": 3.3, "head": TRAC, "glass": False}],
       2: lambda L, j, hs: PORTAL(2.6)(L, j, hs) + PORTAL(-0.5)(L, j, hs)},
      t=0.6, skip=(2,), about="the arcaded loggia on the Rhine front, open in four pointed arches", interior=False)
add("loggia deck", {"type": "prism", "plan": {"rect": [8.3, 3.2]}, "height": 0.3, "flatRoof": True, "walked": True, "at": [[13.0, G + 5.0, 8.1, 0]], "standsOn": ["loggia"]})
add("loggia balustrade", {"type": "cresting", "run": [[-4.1, 0], [4.1, 0]], "h": 0.95, "panel": 0.8, "t": 0.2, "bar": 0.1, "at": [[13.0, G + 5.3, 9.68, 0]], "standsOn": ["loggia deck"],
                          "_about": "the stone tracery balustrade round the balcony over it"})
add("loggia balustrade ends", {"type": "cresting", "run": [[-1.5, 0], [1.5, 0]], "h": 0.95, "panel": 0.8, "t": 0.2, "bar": 0.1,
                               "at": [[17.08, G + 5.3, 8.1, Q], [8.92, G + 5.3, 8.1, -Q]], "standsOn": ["loggia deck"]})
# the south porch (three arches) and the oriel over it
block(add, "south porch", 18.4, 21.0, -5.4, 0.8, G, 5.0, 1,
      {1: lambda L, j, hs: row(L, 3, 1.4, 0, 3.2, TRAC, edge=0.5, glass=False), 0: lambda L, j, hs: [{"at": 0, "width": 1.2, "sill": 0, "springing": 3.2, "head": TRAC, "glass": False}],
       2: lambda L, j, hs: [{"at": 0, "width": 1.2, "sill": 0, "springing": 3.2, "head": TRAC, "glass": False}], 3: PORTAL(0)},
      t=0.55, skip=(3,), about="the south porch: three pointed arches to the garden front", interior=False)
add("south porch deck", {"type": "prism", "plan": {"rect": [2.9, 6.5]}, "height": 0.3, "flatRoof": True, "at": [[19.75, G + 5.0, -2.3, 0]], "standsOn": ["south porch"]})
add("south oriel", comp("oriel", {"w": 3.6, "d": 1.4, "H": 3.6, "foot": 0.6, "cap": "flat"}, [[18.4, G + 5.9, -2.3, Q]], standsOn=["south porch deck"],
                        _about="the oriel over the porch, on the first floor of the south front, its flat top a balcony for the window over it"))
# the roofs: a mansard over the block (its flat top railed with iron cresting), the south wing's tall gable, a hip over the corner
add("house roof", {"type": "roof", "form": "mansard", "width": 14.0, "length": 18.2, "lowerPitch": 62, "breakH": 5.6, "pitch": 12, "overhang": 0.3, "at": [[5.6, YK, -2.1, 0]],
                   "_about": "the main house's roof: steep slate slopes to a flat top"})
BI = 5.6 / math.tan(math.radians(62))
crest_rect(add, "house cresting", 5.6, YK + 5.6 + 0.03, -2.1, 14.0 - 2 * BI - 0.4, 18.2 - 2 * BI - 0.4)
RS = gabled(add, "south wing", 18.4, -2.0, Q, 9.6, 8.4, 58, YK, t=0.6, pins=(0.8, 2.6, 2.4), finial=(0.5, 0.8, 1.8), about="the south front's gable, between the round towers")
add("corner roof", {"type": "roof", "form": "hip", "width": 4.4, "length": 5.4, "pitch": 55, "overhang": 0.2, "at": [[14.7, YK, 4.6, Q]]})
# (iron cresting along the two gabled roofs' ridges: a cresting runs along its own x, a roof's ridge along its own z)
ridge = lambda nm, x, y, z, L, yaw: add(nm, {"type": "cresting", "run": [[-L / 2, 0], [L / 2, 0]], "h": 0.6, "panel": 0.5, "t": 0.06, "bar": 0.04, "at": [[r4(x), r4(y), r4(z), r4(yaw)]],
                                             "_about": "iron cresting on the ridge"})
ridge("south wing cresting", 15.0, YK + RS - 0.02, -2.0, 5.6, 0)
ridge("gable bay cresting", 4.5, G + CH + RG - 0.02, 6.0, 6.0, Q)
# (the round towers at the south front's corners: tall slate spikes over the eaves -- components/cone-turret)
turret("south-west tower", 18.6, 4.6, G, "the round tower on the south-west corner, its tall slate cone over the eaves", R=2.5, H=16.5, _k=3.5, door="no", storeys=4)
turret("south-east tower", 14.0, -6.9, G, "the round tower on the south-east corner, set back from the south front", R=2.2, H=15.2, _k=3.5, door="no", storeys=4)
# (dormers on the house's back slope, their fronts 0.3 m inside the mansard's slope at their feet; chimneys)
DZ = (-2.1 - 18.2 / 2 - 0.3) + 0.2 / math.tan(math.radians(62)) + 0.3 + 1.2      # (the roof's eave with its overhang, up the slope to the dormer's foot, in 0.3, back half its depth)
for k, x in enumerate((3.0, 6.4, 9.8)):
    yaw = math.pi
    add(f"house dormer {k + 1}", {"type": "enclosure", "plan": {"rect": [1.6, 2.4]}, "thickness": 0.25, "height": 2.2, "glass": True,
                                   "faces": {"0": [{"openings": [{"at": 0, "width": 0.8, "sill": 0.4, "springing": 1.6, "head": FLAT}]}], "1": [{"openings": []}], "2": [{"openings": []}], "3": [{"openings": []}]},
                                   "at": [[x, YK + 0.2, r4(DZ), yaw]], "_about": "a dormer on the back slope"})
    add(f"house dormer {k + 1} roof", {"type": "roof", "form": "gable", "width": 1.9, "length": 2.6, "pitch": 55, "overhang": 0.1, "at": [[x, YK + 2.4, r4(DZ), yaw]]})
add("chimneys", {"type": "box", "width": 1.0, "length": 0.7, "height": 3.2, "at": [[1.5, YK + 4.0, -6.0, 0], [9.6, YK + 4.0, 1.5, 0], [-5.0, YK + 3.0, -7.5, 0]], "_about": "chimney stacks"})

# ---- THE STAIR HALL behind the Hauptturm, the back porch (the Hauptportal), THE HAUPTTURM (components/castle-tower, top spire)
block(add, "stair hall", -8.8, -1.0, -10.8, 2.5, G, 13.0, 3,
      {2: lambda L, j, hs: storey_row(L, [-1.6, 1.6], j, hs, w=1.1, head=TRAC), 1: THROUGH(0.65), 3: GROUND(-2.85)}, t=0.8, skip=(0, 1, 3),
      about="the stair hall between the Kunsthalle and the house")
add("stair hall roof", {"type": "roof", "form": "hip", "width": 8.2, "length": 13.7, "pitch": 52, "overhang": 0.2, "at": [[-4.9, YK, -4.15, 0]]})
block(add, "portal porch", -2.0, 2.6, -16.3, -10.8, G, 5.5, 1,
      {2: lambda L, j, hs: [{"at": 0, "width": 2.8, "sill": 0, "springing": 3.1, "head": TRAC, "glass": False}],
       1: lambda L, j, hs: [{"at": 0, "width": 2.0, "sill": 0, "springing": 3.2, "head": TRAC, "glass": False}],
       3: lambda L, j, hs: [{"at": 0, "width": 2.0, "sill": 0, "springing": 3.2, "head": TRAC, "glass": False}], 0: PORTAL(0)},
      t=0.6, skip=(0,), about="the portico before the main portal on the hill side (reconstructed 2008-11), open in pointed arches, the two flights to either side of it", interior=False)
gabled(add, "portal porch", 0.3, -16.3, math.pi, 5.0, 5.9, 55, G + 5.5, t=0.5, pins=(0.5, 1.6, 1.5), finial=(0.4, 0.5, 1.3), about="the portico's gable")
HT = (-4.9, 6.4)
add("hauptturm", comp("castle-tower", {"w": 7.8, "H": 22.0, "top": "spire", "clock": "yes", "Hb": 5.6, "lights": 2, "gW": 4.6, "gH": 3.9, "tW": 1.35, "tS": 2.8, "rise": 14.5, "vane": 2.4},
                      [[HT[0], G, HT[1], 0]], _about="the Hauptturm on the Rhine front: square, a clock on every face, the belfry, four gables, four corner turrets with stone caps, the steep slate spire"))

# ---- THE KUNSTHALLE (the art hall, its dome over the middle) and its gable risalit; the wing to the Nordturm
KX0, KX1, KZ0, KZ1 = -26.5, -8.8, -9.0, 8.0
kcx, kcz = (KX0 + KX1) / 2, (KZ0 + KZ1) / 2
block(add, "kunsthalle", KX0, KX1, KZ0, KZ1, G, EK, 2,
      {0: lambda L, j, hs: [{"at": r4(x - kcx), "width": 1.6, "sill": 0.9 if j == 0 else 0.8, "springing": 4.0, "head": TRAC, "tracery": {}} for x in (-16.0, -12.2)],
       2: lambda L, j, hs: [{"at": r4(kcx - x), "width": 1.5, "sill": 0.9, "springing": 4.0, "head": TRAC} for x in (-24.0, -19.5, -15.0, -11.0)],
       3: lambda L, j, hs: [{"at": r4(z - kcz), "width": 1.4, "sill": 0.9, "springing": 4.0, "head": TRAC} for z in (-6.0, -2.5)] + GROUND(5.5)(L, j, hs),
       1: GROUND(6.5)},
      t=0.8, skip=(1,), about="the Kunsthalle: two tall storeys of traceried windows")
block(add, "kunsthalle risalit", -25.3, -18.3, 8.0, 9.6, G, EK + 2.0, 3,
      {0: lambda L, j, hs: ([{"at": a, "width": 1.4, "sill": 0.8, "springing": 3.3, "head": TRAC, "tracery": {}} for a in (-1.4, 1.4)] if j == 0 else
                            [{"at": a, "width": 1.0, "sill": 0.6, "springing": 3.0, "head": TRAC, "tracery": {}} for a in (-1.2, 0, 1.2)] if j == 1 else
                            [ROSE(2.6, 2.2)]),
       1: lambda L, j, hs: [], 3: lambda L, j, hs: []},
      t=0.7, skip=(2,), about="the Kunsthalle's risalit on the Rhine front: traceried windows and the rose under its gable")
gabled(add, "kunsthalle risalit", -21.8, 9.6, 0, 7.3, 5.6, 56, G + EK + 2.0, t=0.55, about="its stone gable")
# (a wall dormer -- a Zwerchhaus on the eaves -- toward the Hauptturm: components/lucarne)
add("kunsthalle dormer", comp("lucarne", {"W": 4.2, "D": 4.0, "H": 3.2, "GH": 3.2, "winW": 1.0}, [[-13.6, G + EK, KZ1, 0]],
                              _about="a wall dormer on the Kunsthalle's front, its gable and pinnacles of red stone"))
KB = 4.2
add("kunsthalle roof", {"type": "roof", "form": "mansard", "width": 17.9, "length": 18.0, "lowerPitch": 55, "breakH": KB, "pitch": 8, "overhang": 0.2, "at": [[kcx, G + EK, kcz, Q]],
                        "_about": "the Kunsthalle's roof: slate slopes to a flat top railed with iron, the dome rising from its middle"})
KI = KB / math.tan(math.radians(55))
crest_rect(add, "kunsthalle cresting", kcx, G + EK + KB + 0.03, kcz, 18.0 - 2 * KI - 0.4, 17.9 - 2 * KI - 0.4)
add("kunsthalle dome", comp("drum-dome", {"R": 2.6, "dt": 0.45, "H": 2.6, "n": 8, "every": 1, "winW": 0.9, "winSill": 0.5, "winH": 1.4, "profile": "pointed", "spread": 0.5,
                                          "domeT": 0.3, "lanternR": 0.55, "lanternH": 1.5},
                            [[-21.8, G + EK + KB + 0.1, -0.5, 0]], build=["drum", "dome", "lantern"],
                            _about="the Kunsthalle's dome (rebuilt 2001-03): an octagonal drum of windows on the flat of the roof, a pointed slate dome, a lantern"))
block(add, "north wing", -35.5, -26.5, 1.5, 9.8, G, 11.0, 2,
      {0: lambda L, j, hs: storey_row(L, [-2.0, 2.0], j, hs, w=1.2, head=TRAC), 2: lambda L, j, hs: storey_row(L, [-2.0, 2.0], j, hs, w=1.2, head=TRAC),
       1: GROUND(0.65)},
      t=0.7, skip=(1, 3), about="the wing between the Kunsthalle and the Nordturm")
add("north wing roof", {"type": "roof", "form": "hip", "width": 8.7, "length": 9.4, "pitch": 48, "overhang": 0.2, "at": [[-31.0, G + 11.0, 5.65, Q]]})

# ---- THE NORDTURM (components/castle-tower, top battlement) and its round turret
add("nordturm", comp("castle-tower", {"w": 8.5, "H": 21.5, "top": "battlement", "watch": "yes", "mOut": 0.5, "mH": 1.0, "pH": 1.1, "winW": 0.95},
                     [[-39.75, G, 5.25, 0]], _about="the Nordturm, the keep at the north end: square, machicolated, crenellated, its stair's turret over the deck"))
turret("nordturm turret", -37.8, 11.6, G, "the round turret before the Nordturm, its slate cone", R=2.0, H=10.5, door="yes")
NT, NW, NO = (-39.75, 5.25), 8.5, 0.5
add("nordturm bartizans", comp("cone-turret", {"R": 0.95, "H": 2.4, "storeys": 2, "door": "no", "sides": 12, "capR": 1.1, "capRise": 3.3, "corH": 0.4},
                               [[r4(NT[0] + sx * (NW / 2 + NO - 0.5)), G + 21.5 + 1.0, r4(NT[1] + sz * (NW / 2 + NO - 0.5)), 0] for sx, sz in ((-1, -1), (-1, 1), (1, 1))],
                               standsOn=["nordturm"], _about="the little corner turrets on the Nordturm's deck (the watch turret takes the fourth corner)"))

# ---- THE INTERIOR, after the ground floor's plan of 1887 (Architektonische Rundschau; Wikimedia Commons "Königswinter
# Schloss Drachenburg Grundriss Erdgeschoss 1887"), fitted to OSM's walls: the portal under the portico opens on the
# VESTIBULE; from it the HALL runs the house's length on the hill side -- to the stair hall west, the south wing's salon
# east; off it the two rooms on the hill side (the Kneipzimmer and the Billardzimmer: the plan's e and c), and on the
# Rhine side the DINING ROOM, opening through a pointed arch into the gable bay, and the MUSIC ROOM behind the loggia
# with the corner room beyond it. The STAIR HALL holds the great stair: a dog-leg of 13 and 13 steps up each storey,
# two flights side by side round a landing at the Rhine end, a gallery railed beside its well. From the stair hall's
# far side the KUNSTHALLE: one tall hall (single-storey, as built), its domed end parted off by a screen of one wide
# arch; beyond it the north wing's room. The upper storeys repeat the ground floor's walls (their plans were not
# found): the hall and the rooms off it on every storey, reached by the great stair. Not built: the Nordturm's and
# the Hauptturm's rooms, the service stair, the cellars; the doors' leaves inside.
H3 = 13.0 / 3               # the main house's storey
SLAB = 0.3
def iwall(name, a, b, doors, about=None, y0=G, H=13.0, n=3, t=0.25, h=2.4):
    """an inner wall from a to b (x, z), its middle on that line, n storeys of H / n: a doorway `h` high at each
    distance along it from a in `doors`, on every storey"""
    L = math.dist(a, b); dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    ops = [DOOR(d - L / 2, h=h) for d in doors]
    tiers = [{"h": r4(H / n), "openings": ops} for _ in range(n - 1)] + [{"openings": ops}]
    mx, mz = (a[0] + b[0]) / 2 - t / 2 * dz, (a[1] + b[1]) / 2 + t / 2 * dx     # (its thickness lies to the right of a-b: moved half back)
    d = {"type": "wall", "width": r4(L), "height": H, "thickness": t, "tiers": tiers, "at": [[r4(mx), y0, r4(mz), r4(math.atan2(-dz, dx))]]}
    if about: d["_about"] = about
    return add(name, d)
def slab(name, x0, x1, z0, z1, ks=(1, 2), about=None):
    """a floor slab over the rect, its top on storey k's floor for each k"""
    d = {"type": "prism", "plan": {"rect": [r4(x1 - x0), r4(z1 - z0)]}, "height": SLAB, "flatRoof": False,
         "at": [[r4((x0 + x1) / 2), r4(G + k * H3 - SLAB), r4((z0 + z1) / 2), 0] for k in ks]}
    if about: d["_about"] = about
    return add(name, d)
INNER = [iwall("hall wall", (3.0, -6.0), (11.4, -6.0), [1.5, 6.0], about="the hall's wall on the hill side: the doors to the Kneipzimmer and the Billardzimmer"),
         iwall("vestibule wall", (3.0, -10.0), (3.0, -6.0), [], about="the vestibule's side"),
         iwall("billiard wall", (6.0, -10.0), (6.0, -6.0), [2.0], about="between the Kneipzimmer and the Billardzimmer, a door through"),
         iwall("hall front wall", (-0.2, -3.6), (11.4, -3.6), [2.2, 9.9], about="the hall's wall on the Rhine side: the doors to the dining room and the music room"),
         iwall("music wall", (8.0, -3.6), (8.0, 5.8), [3.6], about="between the dining room and the music room")]
FLOORS = [slab("house floors", -0.2, 11.4, -10.0, 5.8, about="the main house's upper floors"),
          slab("south wing floors", 13.0, 17.6, -5.8, 1.8), slab("corner wing floors", 12.9, 16.5, 3.3, 5.9),
          slab("stair hall floors", -8.0, -1.8, -10.0, -5.5, about="the stair hall's upper floors round the stair's well"),
          slab("stair hall gallery", -3.4, -1.8, -5.5, 1.7), slab("stair hall landing", -8.0, -5.4, -5.5, -4.5),
          add("thresholds", {"type": "prism", "plan": {"rect": [1.6, 1.3]}, "height": SLAB, "at": [[x, r4(G + k * H3 - SLAB), z, 0] for k in (1, 2) for x, z in ((-1.0, -4.8), (12.2, -4.8))],
                             "_about": "the floors through the doorways in the doubled walls, upstairs"}),
          add("thresholds corner", {"type": "prism", "plan": {"rect": [1.5, 1.3]}, "height": SLAB, "at": [[12.15, r4(G + k * H3 - SLAB), 4.5, 0] for k in (1, 2)]})]
add("great stair", {"type": "staircase", "rise": r4(H3 / 26), "run": 0.3, "soffit": 0.3, "flight": 13, "width": 2.0,
                    "landing": {"depth": 2.3, "width": 4.4, "shift": -1.2, "then": [{"from": "back", "at": -1.2, "flight": 13, "width": 2.0, "landing": {"depth": 1.0, "width": 2.0}}]},
                    "at": [[-6.8, G, -4.5, r4(-Q)]], "repeat": {"count": 2, "step": [0, r4(H3), 0, 0]},
                    "_about": "the great stair: up the stair hall to the landing at its Rhine end, back up beside itself to the next floor -- twice"})
add("stair balustrade", {"type": "box", "width": 0.15, "length": 6.2, "height": 1.0, "at": [[-3.325, r4(G + k * H3), -1.4, 0] for k in (1, 2)],
                         "_about": "the gallery's balustrade along the stair's well"})
add("kunsthalle screen", {"type": "wall", "width": 15.4, "height": EK, "thickness": 0.6, "tiers": [{"openings": [{"at": 0, "width": 4.4, "sill": 0, "springing": 5.2, "head": TRAC, "glass": False}]}],
                          "at": [[-18.0, G, -0.5, r4(Q)]], "_about": "the screen parting the Kunsthalle's domed end off: one wide pointed arch"})

# ---- THE VORBURG (the outer bailey, 95 m down the hill to the north-east): a plain two-storey hall, gabled, its gate in the
# middle of its front under a big Zwerchhaus, two small ones beside it (components/lucarne), stone gables at its ends
VX0, VX1, VZ0, VZ1, VH = -55.0, -23.0, -93.0, -81.0, 9.0
vx = (VX0 + VX1) / 2
block(add, "vorburg", VX0, VX1, VZ0, VZ1, 0, VH, 2,
      {0: lambda L, j, hs: storey_row(L, [-13, -9, -5, 0, 5, 9, 13], j, hs, w=1.2, head=SEG, door=0, doorW=2.6, doorH=2.4),
       2: lambda L, j, hs: storey_row(L, [-13, -9, -5, 0, 5, 9, 13], j, hs, w=1.2, head=SEG),
       1: lambda L, j, hs: storey_row(L, [-2.5, 2.5], j, hs, w=1.1, head=SEG), 3: lambda L, j, hs: storey_row(L, [-2.5, 2.5], j, hs, w=1.1, head=SEG)},
      t=0.7, about="the Vorburg: a two-storey hall, its gate in the middle of the front toward the castle")
add("vorburg roof", {"type": "roof", "form": "gable", "width": VZ1 - VZ0, "length": VX1 - VX0, "pitch": 50, "overhang": 0.3, "at": [[vx, VH, (VZ0 + VZ1) / 2, Q]]})
VR = (VZ1 - VZ0) / 2 * math.tan(math.radians(50))
for nm, x, yaw in (("vorburg south gable", VX1, Q), ("vorburg north gable", VX0, -Q)):
    gable(add, nm, x, (VZ0 + VZ1) / 2, yaw, VZ1 - VZ0 + 1.0, r4(VR + 0.6), VH, t=0.5, overhang=0.3, pins=(0.6, 1.8, 1.6), finial=(0.4, 0.5, 1.3))
add("vorburg gate gable", comp("lucarne", {"W": 6.0, "D": 5.5, "H": 3.6, "GH": 4.2, "winW": 1.4}, [[vx, VH, VZ1, 0]], _about="the big Zwerchhaus over the gate"))
add("vorburg dormers", comp("lucarne", {"W": 3.4, "D": 4.0, "H": 3.4, "GH": 2.8, "winW": 0.9}, [[vx - 10, VH, VZ1, 0], [vx + 10, VH, VZ1, 0]],
                            _about="a Zwerchhaus to either side"))

# ---- THE VENUSTERRASSE'S GARDEN, square to its own walls: lawns in gravel round the fountain (an octagonal basin, the
# column in its middle with the figure on it -- Venus once, a robed figure since the 1930s), round flower beds in tiers
# ("Tortenbeete") in the lawns, the two gilt stags on their pedestals either side of the Freitreppe's foot
GU1 = min(gof(TP[23])[0], gof(TP[24])[0]) - 0.8          # (the garden's far end, in from its wall -- not the turret's corner past it)
GV1 = min(abs(gof(p)[1]) for p in TPL if GU0 + 3 < gof(p)[0] < GU1 - 3) - 1.2   # (half its width, in from the walls)
GA0 = GU0 + FN * 0.3 + 0.6                               # (the gravel from just past the flight's foot)
FU = (GA0 + GU1) / 2                                     # (the fountain: the gravel's middle)
FX, FZ = gat(FU, 0)
PATH = 1.5                                               # (half a gravel walk's width)
add("gravel walks", {"type": "prism", "plan": {"rect": [r4(GU1 - GA0), r4(2 * GV1)]}, "height": 0.05, "flatRoof": True, "walked": True,
                     "at": [[*gat(FU, 0)[:1], GL, gat(FU, 0)[1], r4(GYAW)]], "_about": "the gravel of the garden, square to its walls"})
LU, LV = r4(FU - GA0 - PATH - 0.8), r4(GV1 - PATH - 0.8)
lawn_at = [(r4(FU + su * (PATH + LU / 2)), r4(sv * (PATH + LV / 2))) for su in (-1, 1) for sv in (-1, 1)]
add("lawns", {"type": "prism", "plan": {"rect": [LU, LV]}, "height": 0.15, "flatRoof": True, "walked": True, "standsOn": ["gravel walks"],
              "at": [[gat(u, v)[0], GL + 0.05, gat(u, v)[1], r4(GYAW)] for u, v in lawn_at], "_about": "four lawns round the fountain, square to the garden"})
BR0 = r4(min(LU, LV) * 0.24)
add("flower beds", {"type": "prism", "plan": {"sides": 20, "radius": BR0}, "height": 0.3, "flatRoof": True, "standsOn": ["lawns"],
                    "at": [[gat(u, v)[0], GL + 0.2, gat(u, v)[1], 0] for u, v in lawn_at], "_about": "a round bed of flowers in each lawn, in tiers like a cake"})
add("flower beds top", {"type": "prism", "plan": {"sides": 16, "radius": r4(BR0 * 0.55)}, "height": 0.25, "flatRoof": True, "standsOn": ["flower beds"],
                        "at": [[gat(u, v)[0], GL + 0.5, gat(u, v)[1], 0] for u, v in lawn_at]})
add("lawn north", {"type": "prism", "plan": {"rect": [5.0, 11.0]}, "height": 0.15, "flatRoof": True, "walked": True,
                   "at": [[-48.5, G, 5.5, r4(math.atan2(TP[42][0] - TP[41][0], TP[42][1] - TP[41][1]))]], "_about": "the lawn by the Nordturm, square to the terrace's wall there"})
add("fountain basin", {"type": "enclosure", "plan": {"sides": 8, "radius": 2.8}, "thickness": 0.35, "height": 0.6, "glass": False, "openings": [], "at": [[FX, GL + 0.05, FZ, r4(GYAW)]],
                       "standsOn": ["gravel walks"], "_about": "the fountain's octagonal basin in the middle of the Venusterrasse"})
add("fountain water", {"type": "prism", "plan": {"sides": 8, "radius": 2.45}, "height": 0.45, "flatRoof": True, "at": [[FX, GL + 0.05, FZ, r4(GYAW)]], "standsOn": ["gravel walks"]})
add("fountain column base", {"type": "prism", "plan": {"sides": 8, "radius": 0.55}, "height": 0.7, "flatRoof": True, "at": [[FX, GL + 0.05, FZ, r4(GYAW)]], "standsOn": ["gravel walks"]})
add("fountain column", {"type": "column", "radius": 0.26, "height": 2.6, "sides": 16, "taper": 0.86, "at": [[FX, GL + 0.75, FZ, 0]], "standsOn": ["fountain column base"],
                        "_about": "the column in the basin's middle"})
add("fountain column capital", {"type": "prism", "plan": {"sides": 8, "radius": 0.42}, "height": 0.22, "flatRoof": True, "at": [[FX, GL + 3.35, FZ, r4(GYAW)]], "standsOn": ["fountain column"]})
add("fountain figure", comp("pedestal", {"W": 0.62, "L": 0.62, "H": 0.55, "kind": "woman", "style": "greek", "stone": "marble", "pose": "contrapposto", "scale": 1.0},
                            [[FX, GL + 3.57, FZ, r4(math.atan2(-gu[0], -gu[1]))]], standsOn=["fountain column capital"],
                            _about="on the column, the figure facing the house: Venus once (the terrace's name), a robed figure since the 1930s"))
SU = GU0 + 1.35                                          # (the stags: either side of the flight, against the terrace's wall)
add("stag pedestals", {"type": "box", "width": 1.9, "length": 0.8, "height": 1.1, "at": [[*gat(SU, sv * (FW / 2 + 1.0))[:1], GL, gat(SU, sv * (FW / 2 + 1.0))[1], r4(GYAW)] for sv in (-1, 1)],
                       "_about": "the stags' pedestals beside the Freitreppe's foot"})
add("stags", comp("standing-stag", {"S": 1.05}, [[*gat(SU, sv * (FW / 2 + 1.0))[:1], GL + 1.1, gat(SU, sv * (FW / 2 + 1.0))[1], r4(math.atan2(gu[0], gu[1]))] for sv in (-1, 1)],
                  standsOn=["stag pedestals"], _about="the two gilt stags beside the Freitreppe, looking out over the garden"))

doc = {"name": "Schloss Drachenburg",
       "_about": "SCHLOSS DRACHENBURG over the Rhine at Königswinter (1882-84): a historicist castle-villa on its terrace -- the main house with its gable bay and rose, the loggia, the south front's porch, oriel and gable between two round towers with tall slate cones; the Hauptturm with its clock, gables, corner turrets and steep slate spire; the Kunsthalle with its rose gable and dome; the crenellated Nordturm; the crenellated terrace on its hillside with the round bastion, its flights and corner turrets. Plan from OpenStreetMap, heights from photographs (tools/archgen/drachenburg.py).",
       "params": {"detail": 4}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/drachenburg.json"), "w").write(json.dumps(doc, indent=2) + "\n")

import re
DRESS = [n for n in parts if re.search(r" gable( pinnacles| finial)?$", n)] + ["loggia balustrade", "loggia balustrade ends"]
fin = {"name": "Schloss Drachenburg", "building": "architecture/drachenburg",
       "_about": "Schloss Drachenburg: buff sandstone walls with a red course now and then, every dressing -- gables, pinnacles, the tympana under them, the turrets' caps of stone -- in a "
                 "rose-red sandstone, the mouldings buff, pale silvery slate in diamond patterns on every roof and cone, iron cresting along the ridges and round the flat tops, the terrace "
                 "and the bastion in yellow ashlar, lawns in gravel round a fountain; leaded glass, roses and the Kunsthalle's windows in colour.",
       "stone": {"color": "#d8c39a", "accent": "#b27464", "pat": "ashlar"},
       "rules": [
           {"parts": ["hauptturm/clock/hands", "hauptturm/clock/marks"], "pattern": "roofs/sheet metal", "palette": "iron", "_about": "the hands and marks of iron"},
           {"parts": ["hauptturm/clock/dial"], "pattern": "roofs/gold leaf", "_about": "the gilt rim (the plate round the ring)"},
           {"parts": ["hauptturm/clock/ring", "hauptturm/clock"], "pattern": "stone/plaster", "palette": "plaster-white", "_about": "the pale faces, as on the photographs"},
           {"parts": ["hauptturm/finial", "hauptturm/spire/finial"], "pattern": "roofs/gold leaf"},
           {"parts": ["house cresting", "house cresting ends", "kunsthalle cresting", "kunsthalle cresting ends", "south wing cresting", "gable bay cresting"], "pattern": "roofs/sheet metal", "palette": "iron",
            "_about": "wrought-iron cresting"},
           {"parts": "kind:glass", "within": [KX0, KZ0, KX1, 9.7], "opening": "round", "map": "opening", "pattern": "glass/rose wheel", "palette": "chartres", "_about": "the Kunsthalle's rose in colour"},
           {"parts": "kind:glass", "within": [KX0, KZ0, KX1, 9.7], "opening": "tall", "nth": [2, 0], "map": "opening", "turn": 90, "pattern": "glass/medallion stack", "palette": "chartres",
            "_about": "the Kunsthalle's tall lights in coloured medallions"},
           {"parts": "kind:glass", "within": [KX0, KZ0, KX1, 9.7], "opening": "tall", "map": "opening", "turn": 90, "pattern": "glass/medallion story", "palette": "chartres"},
           {"parts": "kind:glass", "within": [KX0, KZ0, KX1, 9.7], "map": "opening", "pattern": "glass/tracery diaper", "palette": "chartres"},
           {"parts": "kind:glass", "opening": "round", "map": "opening", "pattern": "glass/rose stone 8", "palette": "cologne", "_about": "the roses"},
           {"parts": "kind:glass", "opening": "head", "map": "opening", "pattern": "glass/tracery diaper", "palette": "grisaille", "_about": "the pointed heads in leaded diaper"},
           {"parts": "kind:glass", "map": "opening", "pattern": "glass/quarries", "palette": "grisaille", "_about": "leaded quarries in every other light"},
           {"parts": ["kind:roof"], "surface": "wall", "pattern": "stone/ashlar", "palette": "rose-sandstone", "_about": "the gabled roofs' end triangles (behind the gables) in red stone"},
           {"parts": ["kind:roof", "kind:dome", "hauptturm/spire", "hauptturm/spire/spire"], "pattern": "roofs/diamond slate", "palette": "slate-light", "_about": "pale slate in diamond patterns"},
           {"parts": ["kind:moulding"], "pattern": "stone/ashlar", "palette": "sandstone", "_about": "the courses buff, like the walls"},
           {"parts": ["hauptturm/turrets", "hauptturm/gables", "hauptturm/gable finials", "gable", "pinnacles"] + DRESS, "pattern": "stone/ashlar", "palette": "rose-sandstone",
            "_about": "the red sandstone dressings: gables, pinnacles, finials, the balustrade"},
           {"parts": ["hill", "lawns", "lawn north"], "pattern": "materials/grass", "palette": "lawn", "_about": "grass on the hillside and the lawns"},
           {"parts": ["gravel walks"], "pattern": "stone/sand", "palette": "gravel"},
           {"parts": ["fountain water"], "color": "#4f6a72", "accent": "#425a62", "_about": "the basin's water"},
           {"parts": ["stags"], "pattern": "roofs/gold leaf", "_about": "the gilt stags"},
           {"parts": ["flower beds", "flower beds top"], "color": "#b8475e", "accent": "#e2b33c", "_about": "the beds' flowers, red and yellow"},
           {"parts": ["fountain figure/statue"], "pattern": "stone/plaster", "palette": "plaster-white", "_about": "the white marble figure"},
           {"parts": ["terrace", "venusterrasse", "bastion", "landing", "fountain basin", "fountain column base", "fountain column", "fountain column capital", "fountain figure",
                      "stag pedestals"] + PARAPET + GARDEN_WALL + BASTION + LANDING_WALL + GATE, "pattern": "stone/ashlar", "palette": "sandstone",
            "_about": "the terrace, the bastion and the fountain in yellow ashlar"},
           {"surface": "floor", "side": "in", "pattern": "floors/checker", "palette": "marble-bw"},
           {"surface": "floor", "pattern": "floors/flagstones", "palette": "sandstone"},
           {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
           {"surface": "wall", "pattern": "stone/banded ashlar", "palette": "drachenburg", "_about": "buff sandstone in courses, a red band now and then"}]}
open(os.path.join(ROOT, "assets/finishes/drachenburg.json"), "w").write(json.dumps(fin, indent=2) + "\n")

if __name__ == "__main__":
    write_components()
    print("drachenburg:", len(parts), "parts")
