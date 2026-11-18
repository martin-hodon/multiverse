"""THE GREAT MOSQUE OF CORDOBA at its peak, c. 988: after al-Mansur's extension, before any Christian work.

Run: python3 tools/archgen/cordoba.py (python3 tools/archgen/andalusi.py first, for its components) -- writes
assets/architecture/cordoba.json, assets/finishes/cordoba.json and assets/doors/cordoba.json.

WHAT IT IS. A walled rectangle 178 x 129 m, its long axis toward the qibla (+z here, south-south-east in the world):
the court (sahn) to the north with its galleries, the minaret in the north wall, and the prayer hall to the south --
19 aisles running to the qibla wall, each between two lines of the two-tier arcades (cordoban-arcade), 36 bays deep,
every aisle under its own gable roof. Built in four campaigns, all of them here as they stood in 988:
  Abd al-Rahman I (785-87)   11 aisles x 12 bays, the court
  Abd al-Rahman II (833-48)  +8 bays south
  Abd al-Rahman III (951-58) the minaret, the court's galleries, the hall's front to the court rebuilt
  al-Hakam II (961-76)       +12 bays south; the Villaviciosa bay (a skylit dome over three bays of the axial aisle at
                             its head) and the MAQSURA before the new mihrab: three ribbed domes over the last bays of
                             the three middle aisles, polylobed interlaced arches round them, the octagonal mihrab
                             behind the qibla wall under its shell dome
  al-Mansur (987-88)         +8 aisles east, the whole length, court included; ten gates in the new east wall
LEFT OUT, being Christian: the cathedral crossing and choir (1523-1607) cut through the middle of the hall, the
Villaviciosa Gothic nave (1489) and the Royal Chapel (1371), the chapels along the walls (from 1252), the walling-up
of the hall's front to the court, the bell tower that encases the minaret (1593-1617), the Puerta del Perdon (1377),
the court's present galleries (1510-16) and its 1597 garden; the roofs as raised in the 18th c. (the walls 1.2 m
higher).

SOURCED. Plan from OpenStreetMap (the building parts of the Mezquita, way 'Mezquita-Catedral de Cordoba' and its
phases), projected about 37.8789 N 4.7794 W; the dominant edge bears 60.73 deg, which is this frame's x. The
phases' edges on it: Abd al-Rahman I's hall x -64.25..13.95, al-Mansur's x 13.95..64.65, the hall's front to the
court at z 0, the qibla wall's outside at z 115.85, the enclosure 178 m long (es.wikipedia: 178 x 125; 23,400 m2).
Elevation (Hernandez Gimenez, quoted by Ewert 2009): column, capital and impost to 3.95 m; the upper arches' crowns
to 6.3 m and more; walls over the arcades 1.07 m thick, 9.805 m to the cornice; the flat painted ceiling at 9.5 m.
Aisles: the axial 7.30-7.85 m, the others about 6.4-7.0 m (Almagro 2020); al-Mansur's narrower. The Villaviciosa
bay three bays of the axial aisle, 7.25 x 8.80 m (Almagro). The maqsura three bays deep before the qibla, three
ribbed domes, polylobed interlaced arches (Marfil). The minaret 8.5 m square, about 47 m with its yamur (Ruiz
Cabrero; artencordoba). The mihrab a small octagonal room under a shell dome (965).
ESTIMATED (stated here so it can be checked): the bays 3.15 m along the aisles (36 to fill the hall; sources give 2.6
to 3.15 m by campaign); the outer walls 11 m tall and 1.25 m thick, buttresses every 7.4 m, stepped merlons; the
court's galleries 6.75 m deep on horseshoe arches; the lanterns 3.4 m over the arcades; the mihrab 3.5 m across; the
gates' places (the documented ones -- San Esteban, al-Hakam II's three west gates, al-Mansur's east gates, the north
gate by the minaret -- set where the bays allow).
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import Doc, r4, Q, comp, at, wall_at, tiles, split, plant, write_json

D = Doc()
NAME = "cordoba"

# ---- THE FRAME --------------------------------------------------------------------------------------------------
T = 1.25                                    # the outer walls
X0, X1 = -63.4, 63.4                        # their inside faces, east and west
ZN, ZQ = -60.5, 114.6                       # the north wall's inside face, the qibla wall's
ZF, FT = 0.0, 1.2                           # the hall's front to the court: from z 0, 1.2 thick
HW = 11.0                                   # the outer walls' height
TOP = 9.805                                 # the arcades' top: the gutters
CEIL = 9.5                                  # the flat ceilings' underside
AISLES = [6.95] * 5 + [7.85] + [6.95] * 5 + [6.18125] * 8   # west to east: Abd al-Rahman I's eleven, al-Mansur's eight
AXIAL = 5
E = [X0]
for k in range(len(AISLES)): E.append(r4(X0 + sum(AISLES[:k + 1])))
assert abs(E[-1] - X1) < 1e-3
AX = [r4((E[i] + E[i + 1]) / 2) for i in range(len(AISLES))]
LINES = E[1:-1]                             # the 18 arcade lines; line i stands between aisles i and i + 1
BAY, NB, Z0 = 3.15, 36, ZF + FT             # the bays along the aisles, from the front's inside face to the qibla
zb = lambda k: r4(Z0 + BAY * k)
assert abs(zb(NB) - ZQ) < 1e-6
MANSUR = E[11]                              # al-Mansur's extension east of here (the old east wall's line)
VV = (21, 24)                               # the Villaviciosa bay: bays 21-23 of the axial aisle, al-Hakam II's threshold
MQ = (33, 36)                               # the maqsura: the last three bays, aisles 4-6
MQA = (4, 5, 6)

# ---- 1. THE PRAYER HALL ------------------------------------------------------------------------------------------
HALL = {}                                                                     # the arcade's kinds
MAQSURA = {"low": "lobed", "lowOver": .3, "lowLobes": 5, "up": "lobed", "upOver": 0, "upLobes": 5, "interlace": "yes", "order": "caliphal"}


def runs(i):
    """line i's runs of bays: (first bay, last bay + 1, kind) -- polylobed and interlaced round al-Hakam II's domes"""
    cuts = []
    if i in (AXIAL - 1, AXIAL): cuts.append(VV)
    if i in (MQA[0] - 1, MQA[-1]) or i in (AXIAL - 1, AXIAL): cuts.append(MQ)
    out, k = [], 0
    for a, b in sorted(cuts):
        if a > k: out.append((k, a, "hall"))
        out.append((a, b, "maqsura")); k = b
    if k < NB: out.append((k, NB, "hall"))
    return out


# group the runs by what they are, one component part for each (N, kind, ends): the hall is a handful of parts
groups = {}
for i, x in enumerate(LINES):
    rs = runs(i)
    for j, (a, b, kind) in enumerate(rs):
        # (a run between two others leaves its end piers to them: `ends` 0 when it is the polylobed one in a line of plain)
        ends = 1 if kind == "hall" else 0
        groups.setdefault((b - a, kind, ends), []).append(at(x, 0, (zb(a) + zb(b)) / 2, -Q))
for (n, kind, ends), places in sorted(groups.items(), key=lambda g: (g[0][1], -g[0][0])):
    D.comp(f"arcades {kind} {n}" if ends else f"arcades {kind} {n} inner", "components/cordoban-arcade",
           {"N": n, "bay": BAY, "ends": ends, **(MAQSURA if kind == "maqsura" else {})}, places,
           about="the hall's arcades: 18 lines of columns, the two tiers of arches over them" if kind == "hall" and n == NB else
                 "al-Hakam II's arcades round the Villaviciosa bay and the maqsura: polylobed arches, interlaced over them" if kind == "maqsura" and n == 3 else None)

# the transverse screens of polylobed arches across the domed bays: the maqsura's front across its three aisles, the
# Villaviciosa's front and back across the axial aisle (its back the triple opening toward the mihrab)
for nm, z, aisles in (("maqsura screen", zb(MQ[0]), MQA), ("villaviciosa front", zb(VV[0]), (AXIAL,)), ("villaviciosa back", zb(VV[1]), (AXIAL,))):
    for a in aisles:
        n = 3 if a == AXIAL else 2
        D.comp(f"{nm} {a}", "components/cordoban-arcade", {"N": n, "bay": r4(AISLES[a] / n), "ends": 0, **MAQSURA}, [at(AX[a], 0, z)],
               about="a screen of polylobed interlaced arches across the aisle" if a == aisles[0] else None)

# the skylit domes: Villaviciosa's over the axial aisle, the maqsura's three before the mihrab
D.comp("villaviciosa lantern", "components/cordoban-lantern", {"W": AISLES[AXIAL], "L": r4(zb(VV[1]) - zb(VV[0]))},
       [at(AX[AXIAL], TOP, (zb(VV[0]) + zb(VV[1])) / 2)],
       about="the Villaviciosa bay's dome on its lantern: al-Hakam II's threshold, where his hall began (7.85 x 9.45 m)")
for a in MQA:
    D.comp(f"maqsura lantern {a}", "components/cordoban-lantern", {"W": AISLES[a], "L": r4(ZQ - zb(MQ[0]))},
           [at(AX[a], TOP, (zb(MQ[0]) + ZQ) / 2)],
           about="the maqsura's three domes, the middle one before the mihrab" if a == MQA[0] else None)

# the ceilings and the roofs, one gable to an aisle, open where a lantern stands
HOLES = [(E[AXIAL], zb(VV[0]), E[AXIAL + 1], zb(VV[1]))] + [(E[a], zb(MQ[0]), E[a + 1], ZQ) for a in MQA]
half = .535                                  # half the arcade wall
ceil, roofs = [], {}
for a, w in enumerate(AISLES):
    x0 = E[a] + (half if a > 0 else 0); x1 = E[a + 1] - (half if a < len(AISLES) - 1 else 0)
    hs = [h for h in HOLES if h[0] < AX[a] < h[2]]
    ceil += split([(x0, z0, x1, z1) for (_, z0, _, z1) in tiles(x0, Z0, x1, ZQ, [(x0, h[1], x1, h[3]) for h in hs])], 16)
    for (_, z0, _, z1) in tiles(E[a], Z0, E[a + 1], ZQ, [(E[a], h[1], E[a + 1], h[3]) for h in hs]):
        roofs.setdefault((r4(w), r4(z1 - z0)), []).append(at(AX[a], TOP, (z0 + z1) / 2))
D.slabs("ceiling", ceil, CEIL, h=.15, about="the flat ceilings, carved and painted pine, between the arcades' walls")
for k, ((w, l), places) in enumerate(sorted(roofs.items())):
    D.add(f"aisle roofs {k + 1}", {"type": "roof", "form": "gable", "width": w, "length": l, "pitch": 20, "at": places},
          "a gable roof over every aisle, the gutters between them on the arcades" if k == 0 else None)
D.add("hall", {"type": "interior", "plan": {"rect": [r4(X1 - X0), r4(ZQ - Z0)]}, "height": CEIL, "at": [at(0, 0, (Z0 + ZQ) / 2)]},
      "the hall's air, up to the ceilings")

# ---- 2. THE WALLS ------------------------------------------------------------------------------------------------
# the gates: (wall, where along it -- z on the east and west walls, x on the north and qibla walls, name)
GATES = [("west", 17.6, "Bab al-Wuzara (San Esteban)"), ("west", 79.0, "al-Hakam II's west gate"), ("west", 92.0, "al-Hakam II's west gate"),
         ("west", 101.5, "al-Hakam II's west gate"), ("west", -28.0, "the court's west gate"),
         ("east", -28.0, "the court's east gate")] + [("east", z, "al-Mansur's gate") for z in (9.5, 24.5, 39.5, 54.5, 69.5, 84.5, 99.5)] + \
        [("north", -18.0, "the north gate by the minaret")]
DW, DS, DOVER = 2.3, 3.2, .32
WALLS = {   # name: (centre x, centre z, length, yaw -- local +x along it, its outside toward local -z... see `out`)
    "west": (-(X1 + T / 2), (ZN - T + ZQ + T) / 2, ZQ - ZN + 2 * T, -Q),
    "east": (X1 + T / 2, (ZN - T + ZQ + T) / 2, ZQ - ZN + 2 * T, -Q),
    "north": (0, ZN - T / 2, X1 - X0, 0),
    "qibla": (0, ZQ + T / 2, X1 - X0, 0),
}
OUT = {"west": (-1, 0, -Q), "east": (1, 0, Q), "north": (0, -1, math.pi), "qibla": (0, 1, 0)}   # the outward normal, and a gate's yaw
start = lambda w: (WALLS[w][1] - WALLS[w][2] / 2) if w in ("west", "east") else (WALLS[w][0] - WALLS[w][2] / 2)
MIHRAB = {"w": 2.1, "s": 3.3, "over": .4}
for w, (cx, cz, L, yaw) in WALLS.items():
    ops = [{"at": r4(g - start(w)), "width": DW, "sill": 0, "springing": DS, "head": {"profile": "horseshoe", "over": DOVER}} for ww, g, _ in GATES if ww == w]
    if w == "qibla":
        ops.append({"at": r4(AX[AXIAL] - start(w)), "width": MIHRAB["w"], "sill": 0, "springing": MIHRAB["s"], "head": {"profile": "horseshoe", "over": MIHRAB["over"]}})
    D.add(f"{w} wall", {"type": "wall", "width": r4(L), "height": HW, "thickness": T, "glass": False, "openings": ops, "at": [wall_at(cx, 0, cz, yaw, T)]},
          "the outer walls, ashlar in stretchers and headers, 11 m to the merlons" if w == "west" else None)
    nx, nz, gy = OUT[w]
    D.comp(f"{w} merlons", "components/crenellation", {"L": r4(L), "t": .45, "h": .75, "step": 1.05, "mh": .85, "merlon": "stepped"},
           [at(cx + nx * (T / 2 - .225), HW, cz + nz * (T / 2 - .225), gy)], about="the stepped merlons along the top" if w == "west" else None)

# the buttresses: square pillars against the outside every 7.4 m or so, none in front of a gate
BUT = {}
for w, (cx, cz, L, yaw) in WALLS.items():
    nx, nz, gy = OUT[w]
    n = round(L / 7.4); s0 = start(w)
    gates = [g for ww, g, _ in GATES if ww == w] + ([AX[AXIAL]] if w == "qibla" else [])
    for k in range(n + 1):
        u = s0 + L * k / n
        if any(abs(u - g) < 4.2 for g in gates): continue
        bx, bz = (cx + nx * (T / 2 + .45), u) if w in ("west", "east") else (u, cz + nz * (T / 2 + .45))
        BUT.setdefault("x" if w in ("west", "east") else "z", []).append(at(bx, 0, bz))
for k, (ax_, places) in enumerate(sorted(BUT.items())):
    D.add(f"buttresses {ax_}", {"type": "box", "width": .9 if ax_ == "x" else 1.5, "length": 1.5 if ax_ == "x" else .9, "height": HW - .4, "at": places},
          "the buttresses, square-headed, against the walls' outside" if k == 0 else None)

# the gates' fronts: a bab over every doorway, on the wall's outside
for k, (w, g, nm) in enumerate(GATES):
    cx, cz, L, _ = WALLS[w]; nx, nz, gy = OUT[w]
    x, z = (cx + nx * T / 2, g) if w in ("west", "east") else (g, cz + nz * T / 2)
    D.comp(f"gate {k + 1}", "components/bab", {"W": 5.8, "H": 8.4, "dw": DW, "ds": DS, "over": DOVER}, [at(x, 0, z, gy)], about=nm)

# the hall's front to the court: an arch to every aisle, open (walled up only in Christian times)
fops = [{"at": r4(AX[a] - X0), "width": r4(min(4.6, w - 2.3)), "sill": 0, "springing": 4.4, "head": {"profile": "horseshoe", "over": .3}} for a, w in enumerate(AISLES)]
D.add("hall front", {"type": "wall", "width": r4(X1 - X0), "height": HW, "thickness": FT, "glass": False, "openings": fops, "at": [wall_at(0, 0, ZF + FT / 2, 0, FT)]},
      "the hall's front to the court, Abd al-Rahman III's: an open horseshoe arch at the head of every aisle")
D.comp("hall front merlons", "components/crenellation", {"L": r4(X1 - X0), "t": .45, "h": .75, "step": 1.05, "mh": .85, "merlon": "stepped"},
       [at(0, HW, ZF + .225, math.pi)])

# ---- 3. THE MIHRAB -----------------------------------------------------------------------------------------------
mx, mr = AX[AXIAL], 2.6
mz = ZQ + T / 2 + mr * math.cos(math.pi / 8)
hs = {"profile": "horseshoe", "over": MIHRAB["over"]}
D.add("mihrab chamber", {"type": "enclosure", "plan": {"sides": 8, "radius": mr}, "thickness": .7, "height": 7.2, "glass": False, "interior": 7.2,
                         "openings": [], "faces": {"3": [{"at": 0, "width": 1.5, "sill": 0, "springing": MIHRAB["s"], "head": hs}]},
                         "at": [at(mx, 0, mz)]},
      "the mihrab: a small octagonal room behind the qibla wall (3.8 m across inside), entered through the horseshoe arch and a narrower one in its own wall")
D.add("mihrab shell", {"type": "dome", "radius": r4(mr - .35), "sides": 8, "thickness": .25, "head": {"profile": "semicircular"}, "at": [at(mx, 7.2, mz)]},
      "its dome, a scallop shell cut from one block of marble")
D.comp("mihrab", "components/bab", {"W": 6.6, "H": 8.7, "D": .35, "dw": MIHRAB["w"], "ds": MIHRAB["s"], "over": MIHRAB["over"], "bn": 7, "crest": "none"},
       [at(mx, 0, ZQ, math.pi)],
       about="the mihrab's front on the qibla wall: the horseshoe arch in its alfiz, the blind arcade over it -- all in gold mosaic, the Byzantine emperor's gift")

# ---- 4. THE COURT ------------------------------------------------------------------------------------------------
GD = 6.75                                    # the galleries' depth, from the walls' inside to the arcade's axis
GX0, GX1, GZ0 = X0 + GD, X1 - GD, ZN + GD
MIN = (-32.25, -56.4, 8.5)                   # the minaret: centre x, z and side
GAL = {"detail": 4, "colH": 3.0, "impH": .3, "upSpr": 3.3, "top": 5.6, "up": "horseshoe", "upOver": .3, "upD": .38, "t": .8, "pierW": .7, "colR": .2}
gal_build = ["columns", "imposts", "piers", "upper arches"]
gl = [("west gallery", GX0, (GZ0, ZF), -Q), ("east gallery", GX1, (GZ0, ZF), -Q)]
for nm, x, (z0, z1), yaw in gl:
    n = round((z1 - z0) / 3.35)
    D.comp(nm, "components/cordoban-arcade", {**GAL, "N": n, "bay": r4((z1 - z0) / n)}, [at(x, 0, (z0 + z1) / 2, yaw)], build=gal_build,
           about="the court's galleries (Abd al-Rahman III's, 951-58): horseshoe arches on columns" if nm == "west gallery" else None)
for k, (x0, x1) in enumerate(((GX0, MIN[0] - MIN[2] / 2), (MIN[0] + MIN[2] / 2, GX1))):
    n = round((x1 - x0) / 3.35)
    D.comp(f"north gallery {k + 1}", "components/cordoban-arcade", {**GAL, "N": n, "bay": r4((x1 - x0) / n)}, [at((x0 + x1) / 2, 0, GZ0)], build=gal_build)
gr = .2 * GD                                 # (the roofs fall from the walls to the arcades)
D.add("west gallery roof", {"type": "roof", "form": "shed", "width": GD, "length": r4(ZF - GZ0), "pitch": 15, "at": [at(X0 + GD / 2, 5.6, (GZ0 + ZF) / 2, math.pi)]},
      "the galleries' roofs, falling from the walls to the court")
D.add("east gallery roof", {"type": "roof", "form": "shed", "width": GD, "length": r4(ZF - GZ0), "pitch": 15, "at": [at(X1 - GD / 2, 5.6, (GZ0 + ZF) / 2, 0)]})
D.add("north gallery roof", {"type": "roof", "form": "shed", "width": GD, "length": r4(X1 - X0), "pitch": 15, "at": [at(0, 5.6, ZN + GD / 2, Q)]})
gceil = [(X0, GZ0 + .4, GX0 - .4, ZF), (GX1 + .4, GZ0 + .4, X1, ZF)] + \
        [(X0, ZN, MIN[0] - MIN[2] / 2, GZ0 - .4), (MIN[0] + MIN[2] / 2, ZN, X1, GZ0 - .4)]
D.slabs("gallery ceiling", gceil, 5.3, h=.15, about="the galleries' flat ceilings")
for nm, (a, b, c, d) in (("west gallery air", gceil[0]), ("east gallery air", gceil[1]), ("north gallery air", (X0, ZN, X1, GZ0 - .4))):
    D.add(nm, {"type": "interior", "plan": {"rect": [r4(c - a), r4(d - b)]}, "height": 5.3, "at": [at((a + c) / 2, 0, (b + d) / 2)]})

D.comp("minaret", "components/alminar", {}, [at(MIN[0], 0, MIN[1])],
       about="Abd al-Rahman III's minaret (951-58), 8.5 m square, 47 m to the yamur: the model of every Andalusi and Maghrebi minaret after it")

# the trees, in rows on the aisles' axes (the court's planting carried the hall's columns on, it was said), and the
# ablution basins
BASINS = [(AX[1], -27.0), (AX[AXIAL], -27.0), (AX[10], -27.0), (AX[15], -27.0)]
oranges, palms = [], []
for i, x in enumerate(AX):
    if not GX0 + 2.5 < x < GX1 - 2.5: continue
    for j, z in enumerate([r4(-6.0 - 6.3 * k) for k in range(8)]):
        if z < GZ0 + 3 or any(math.hypot(x - bx, z - bz) < 3.5 for bx, bz in BASINS): continue
        (palms if (i + j) % 4 == 0 else oranges).append((x, 0, z))
plant(D, "orange", oranges, about="the court's orange trees, in rows on the aisles' axes")
plant(D, "palm", palms, about="and date palms among them (the court's palms are on Cordoba's seals of 1262 and 1445)")
D.add("basins", {"type": "prism", "plan": {"sides": 8, "radius": 1.5}, "height": .75, "at": [at(x, 0, z) for x, z in BASINS]},
      "the ablution basins (al-Mansur's cistern under the court fed them)")
D.add("basin water", {"type": "prism", "plan": {"sides": 8, "radius": 1.3}, "height": .7, "flatRoof": True, "at": [at(x, .05, z) for x, z in BASINS]})

# ---- 5. THE GROUND -----------------------------------------------------------------------------------------------
plat = split([(-(X1 + T), ZN - T, X1 + T, ZQ + T), (mx - 3.0, ZQ + T, mx + 3.0, mz + 2.6)], 16)
D.slabs("floor", plat, -.3, h=.3, walked=True, flatRoof=True, about="the floor: the hall's and the court's, one level")
D.first([n for n in D.build if n == "floor" or n.startswith("floor ")])

D.write(f"assets/architecture/{NAME}.json", "Great Mosque of Cordoba",
        "THE GREAT MOSQUE OF CORDOBA as it stood in 988, after al-Mansur's extension and before any Christian work: the walled "
        "court with its galleries, orange trees and palms and Abd al-Rahman III's minaret; the prayer hall of 19 aisles and 36 "
        "bays on some 600 columns, its two-tier arcades of red-and-white horseshoe arches; al-Hakam II's Villaviciosa dome and "
        "maqsura of polylobed interlaced arches under three ribbed domes; the octagonal mihrab; the gates in their alfiz frames. "
        "Built by tools/archgen/cordoba.py from the components of tools/archgen/andalusi.py (its docstring: what is sourced, "
        "what is estimated, what is left out). +z is toward the qibla (south-south-east).",
        railing={"type": "stone"})

# =====================================================================================================================
# THE FINISH: golden calcarenite outside; inside, the arches' red brick and white stone voussoirs, marble columns,
# ashlar piers, painted ceilings; the maqsura in gold mosaic and carved marble
# =====================================================================================================================
MQ_WITHIN = [E[MQA[0]], zb(MQ[0]) - .6, E[MQA[-1] + 1], ZQ + 4]
VV_WITHIN = [E[AXIAL], zb(VV[0]) - .6, E[AXIAL + 1], zb(VV[1]) + .6]
rules = [
    {"parts": ["basin water"], "color": "#3f8fa6", "accent": "#347c91", "_about": "the water"},
    {"parts": ["orange crowns"], "color": "#3e5f2a", "accent": "#2f4d20"},
    {"parts": ["palm fronds"], "color": "#6d8a3e", "accent": "#4d6a2c"},
    {"parts": ["orange trunks", "palm trunks"], "pattern": "timber/bark", "palette": "oak-grey"},
    {"parts": ["mihrab", "mihrab chamber"], "side": "in", "pattern": "painted/gold mosaic", "palette": "gold-mosaic",
     "_about": "the mihrab's front and its room: Byzantine gold mosaic, sent with a mosaicist by the emperor Nikephoros Phokas"},
    {"parts": ["mihrab shell"], "surface": "ceiling", "pattern": "ornament/rosette 12", "palette": "carrara", "_about": "the shell"},
    {"parts": ["kind:arch"], "pattern": "stone/voussoirs", "palette": "cordoba-voussoir",
     "_about": "every arch: white stone and red brick voussoirs in turn (al-Mansur's only painted so)"},
    {"parts": ["columns shafts"], "within": MQ_WITHIN, "pattern": "stone/marble", "palette": "marble-rose", "_about": "the maqsura's paired columns: rose and blue marble"},
    {"parts": ["columns shafts"], "within": VV_WITHIN, "pattern": "stone/marble", "palette": "marble-rose"},
    {"parts": ["columns shafts"], "pattern": "stone/marble", "palette": "marble-grey", "_about": "the hall's columns: reused Roman marbles, grey, blue and rose"},
    {"parts": ["columns capitals", "columns abaci", "columns bases"], "color": "#e7dcc4", "accent": "#cfc2a6", "_about": "the capitals, carved limestone"},
    {"parts": ["walls"], "side": "in", "pattern": "painted/gold mosaic", "palette": "gold-mosaic",
     "_about": "the lanterns' walls inside: gold mosaic between the windows"},
    {"parts": ["dome"], "surface": "ceiling", "pattern": "ornament/star8 strap", "palette": "gold-mosaic", "map": "conformal",
     "_about": "the ribbed domes: eight ribs crossing in a star, gold mosaic between"},
    {"parts": ["deck"], "surface": "ceiling", "pattern": "painted/gold mosaic", "palette": "gold-mosaic"},
    {"parts": ["ceiling", "gallery ceiling"], "surface": "ceiling", "pattern": "ornament/star8 strap", "palette": "walnut",
     "_about": "the flat ceilings: carved and painted pine, the beams' soffits in red and black strapwork"},
    {"parts": ["kind:roof"], "pattern": "roofs/coppi", "palette": "terracotta"},
    {"parts": ["dome"], "surface": "roof", "pattern": "roofs/coppi", "palette": "terracotta", "_about": "the domes' outsides under tiles"},
    {"surface": "floor", "within": [X0 - .1, Z0 - .1, X1 + .1, ZQ + 6], "pattern": "floors/terracotta", "_about": "the hall's floor, brick under the mats"},
    {"surface": "floor", "within": [GX0 + .5, GZ0 + .5, GX1 - .5, ZF - .1], "pattern": "stone/sand", "_about": "the court, beaten earth round the trees"},
    {"surface": "floor", "pattern": "floors/flagstones", "palette": "cordoba-stone"},
    {"parts": ["piers", "imposts"], "pattern": "stone/ashlar fine", "palette": "cordoba-stone", "_about": "the piers over the columns: dressed stone"},
    {"pattern": "stone/ashlar", "palette": "cordoba-stone", "_about": "the walls: golden calcarenite in stretchers and headers"},
]
write_json(f"assets/finishes/{NAME}.json", {"name": "Great Mosque of Cordoba", "building": f"architecture/{NAME}",
                                            "stone": {"color": "#d9bc8c", "accent": "#c7a676", "pat": "ashlar"}, "rules": rules})
write_json(f"assets/doors/{NAME}.json", {
    "name": "Great Mosque of Cordoba: doors", "building": NAME,
    "_about": "the gates' doors: two leaves of wood clad in bronze plates and studs",
    "doors": [{"_about": "the gates", "part": [f"{w} wall" for w in ("west", "east", "north")], "style": "andalusi"}]})
print("finish and doors written")
