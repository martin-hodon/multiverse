# ST PETER'S BASILICA AND ST PETER'S SQUARE, Rome (basilica 1506-1626: Bramante, Michelangelo, Della Porta, Maderno;
# colonnade 1656-67: Bernini), from components:
#   THE SQUARE: the two arms of Bernini's colonnade (components/curved-colonnade, roman_baroque.py: four rows of Tuscan
#   columns on arcs round two centres either side of the obelisk, one entablature over them, the saints on the inner
#   balustrade, temple fronts at their ends and middles), the two straight corridors (bracci) closing the piazza retta up
#   to the facade, the steps up to the sagrato, the obelisk on its lions, the two fountains, the paving of sampietrini
#   with its travertine rays from the obelisk.
#   THE BASILICA on its podium: Maderno's front (a giant Corinthian order through two storeys, the five portals under it,
#   the Benediction loggia over them, the attic, the pediment over the middle columns, the balustrade with Christ, the
#   Baptist and eleven apostles, the clocks at the ends), the nave behind it with its clerestory roof, Michelangelo's
#   Greek cross with its three apses in the giant order and its attic; over the crossing the DRUM (16 buttresses each with
#   a pair of Corinthian columns, a window between each two under triangular and segmental pediments by turns), the attic,
#   the raised ribbed dome of Della Porta, the lantern, the ball and the cross; the two minor cupolas (Vignola's).
# Plan from OpenStreetMap (tools: the scratch plan of 2026-11-02), the obelisk at the origin, x north, z east: the basilica's
# front faces +z (east, down the Via della Conciliazione). The basilica is set on the obelisk's axis (OSM has it ~8 m off).
# Heights: the dome 136.57 m from the floor to the cross (sourced), its inner diameter 41.47 m (sourced), the drum's
# columns 15 m (sourced), its widest 58.9 m (sourced); the front 114.7 m wide and 45.5 m high (sourced); the obelisk 25.5 m
# (sourced), 41 m to the cross's top (sourced); the colonnade's 13 m columns, 18 m top and 3.1 m saints (estimated).
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from roman_baroque import arc_points, obelisk, fountain, giant_front, opening as op, write_components
from neoclassical import Balusters
from statuary import statue, capped, FACE_PZ
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
r3 = lambda v: round(v, 3)
Q = math.pi / 2
look = lambda dx, dz: r3(math.atan2(-dz, dx))      # a statue's turn to look along (dx, dz) (statuary.py: +x is its forward)

# ==== THE SQUARE ===========================================================================================================
AX, R0, ARC, D4 = 27.0, 68.5, 145.0, 15.0           # the arms' centres (+-AX on x), the inner row's radius, their arc, the rows' depth
COLH, ENTH, BALH = 13.0, 2.8, 1.6
TOPC = COLH + ENTH                                   # the colonnade's roof line (the balustrade on it)
for sx, nm in ((1, "north"), (-1, "south")):
    add(f"{nm} colonnade", comp("components/curved-colonnade", {"R": R0, "arc": ARC, "count": 33, "d2": 4.4, "d3": 10.6, "d4": D4, "colR": 0.8, "colH": COLH,
                                                                "entH": ENTH, "balH": BALH, "midW": 17.0, "midD": 3.2, "colGrow": 0.12},
                                [[sx * AX, 0, 0, sx * Q]], build=["row 1", "row 2", "row 3", "row 4", "entablature", "roof", "inner balustrade",
                                                                  "outer balustrade", "end fronts", "middle fronts", "end piers", "middle piers"],
                                **({"_about": "Bernini's colonnade: two arms of four rows of Tuscan columns, each arm on arcs round its own centre "
                                              "either side of the obelisk -- from those two points the four rows line up as one"} if sx > 0 else {})))
# the arms' west ends, where the corridors (bracci) run on to the front, and the corridors themselves: a closed wing of a
# Tuscan order with its windows to the piazza, a balustrade on its head
th_end = math.radians(ARC / 2)
xE = AX + (R0 - 1.3) * math.cos(th_end)              # the inner face's x at the arms' west end
BW, BZ0, BZ1 = 10.0, -76.0, -186.0                   # the corridors' depth, from z BZ0 to the front's line
FW = 114.7                                           # the basilica's front's width
BX0, BX1 = 47.5, FW / 2 + 1.0                        # their inner face's x at BZ0 and at the front: the piazza retta is a TRAPEZE,
                                                     # widening to the front, the corridors meeting its ends (OSM)
bx = lambda z: BX0 + (BX1 - BX0) * (BZ0 - z) / (BZ0 - BZ1)
bal = Balusters(h=1.3, every=0.55)
L = math.hypot(BX1 - BX0, BZ0 - BZ1)
for sx, nm, face in ((1, "north", "3"), (-1, "south", "1")):
    yaw = -sx * math.atan2(BX1 - BX0, BZ0 - BZ1)
    nx, nz = math.cos(yaw), -math.sin(yaw)          # the corridor's local +x in the world (outward for the north one)
    cx, cz = sx * (BX0 + BX1) / 2 + sx * BW / 2 * nx, (BZ0 + BZ1) / 2 + sx * BW / 2 * nz
    add(f"{nm} corridor", {"type": "enclosure", "plan": {"rect": [BW, r3(L)]}, "thickness": 1.0, "height": r3(TOPC),
                           "faces": {face: [{"h": 5.0, "openings": {"pattern": "17", "width": 1.8, "gap": r3(L / 17 - 1.8 - 0.3), "sill": 0.8, "springing": 3.6,
                                                                       "head": {"profile": "flat"}, "surround": {"head": "cornice"}}},
                                            {"openings": {"pattern": "17", "width": 2.0, "gap": r3(L / 17 - 2.0 - 0.3), "sill": 2.0, "springing": 6.2,
                                                          "head": {"profile": "semicircular"}}}]},
                           "orders": [{"tier": 0, "kind": "tuscan", "span": 2}], "courses": True, "interior": True,
                           "at": [[r3(cx), 0, r3(cz), r3(yaw)]],
                           **({"_about": "the straight corridors (Braccio di Costantino north, di Carlo Magno south) from the colonnade to the front"} if sx > 0 else {})})
    add(f"{nm} corridor roof", {"type": "prism", "plan": {"rect": [BW, r3(L)]}, "height": 0.4, "flatRoof": True,
                                "at": [[r3(cx), r3(TOPC), r3(cz), r3(yaw)]]})
    bal.run((sx * (bx(BZ0) + 0.3 * nx), BZ0 + 0.3 * sx * nz), (sx * (bx(BZ1 + 0.5) + 0.3 * nx), BZ1 + 0.5 + 0.3 * sx * nz), TOPC + 0.4)

# the steps up to the sagrato, the platform before the front (the basilica's floor F over the piazza)
F = 3.0
ST, SO = 8, 1.0
add("sagrato steps", {"type": "crepidoma", "width": 76.0, "length": 36.0, "steps": ST, "stepH": r3(F / ST), "stepOut": SO,
                      "at": [[0, 0, -168.0, 0]], "_about": "the steps up from the piazza to the sagrato, the platform before the front"})

# Sts Peter (south, the keys) and Paul (north, the sword) on their pedestals before the steps
for sx, nm in ((1, "paul"), (-1, "peter")):
    add(f"{nm} pedestal", {"type": "box", "width": 3.0, "length": 3.0, "height": 3.6, "courses": True, "at": [[r3(sx * 17.0), 0, -139.5, 0]],
                           **({"_about": "the pedestals of Sts Peter and Paul at the foot of the steps"} if sx > 0 else {})})
# the obelisk and the fountains
top_ob = obelisk(add, 0.0, 0.0, shaft=25.5, foot=1.35, top=0.95, pedH=8.0, pedW=5.6, crown=4.2)
for sx, nm in ((1, "Maderno fountain"), (-1, "Bernini fountain")):
    fountain(add, sx * 59.8, 0.0, R=5.0, name=nm)

# THE PAVING: sampietrini over the whole oval to the colonnades' outer rows and the piazza retta between the corridors; the
# travertine rays from the obelisk, and the ellipse's band round it (raised a hair, so they are their own stone)
PH = 0.12
outline = []
RP = R0 + D4 + 2.0
for k in range(25):                                   # the north arm's arc east to west, then the corridor's line
    th = math.radians(-ARC / 2 + ARC * k / 24)
    outline.append((AX + RP * math.cos(th), -RP * math.sin(th)))
zE = outline[-1][1]
outline += [(bx(zE), zE), (BX1, BZ1), (-BX1, BZ1), (-bx(zE), zE)]
for k in range(25):                                   # the south arm's, west to east
    th = math.radians(ARC / 2 - ARC * k / 24)
    outline.append((-AX - RP * math.cos(th), -RP * math.sin(th)))
add("paving", {"type": "prism", "plan": {"points": [[r3(x), r3(z)] for x, z in outline]}, "height": PH, "walked": True, "at": [[0, 0, 0, 0]],
               "_about": "the piazza's paving: sampietrini, the little basalt setts of Rome (finish), over the oval and the piazza retta"})
def reach(phi):
    """how far the ray at angle phi (from +z toward +x) runs from the obelisk before the colonnade's inner edge or the retta's"""
    dx, dz = math.sin(phi), math.cos(phi)
    best = 200.0
    for cx in (AX, -AX):
        b = dx * (-cx); c = cx * cx - (R0 - 3.0) ** 2   # |t d - c|^2 = r^2
        disc = b * b - c
        if disc > 0: best = min(best, -b + math.sqrt(disc)) if -b + math.sqrt(disc) > 0 else best
    return best
rays = []
for k in range(16):
    phi = k * 2 * math.pi / 16 + math.pi / 16
    d0, d1 = 7.5, min(reach(phi), 80.0 / max(0.2, abs(math.cos(phi))))
    if d1 - d0 < 3: continue
    rays.append([r3((d0 + d1) / 2 * math.sin(phi)), 0, r3((d0 + d1) / 2 * math.cos(phi)), r3(phi), r3(d1 - d0)])
for i, (x, y, z, a, l) in enumerate(rays):
    add(f"ray {i}", {"type": "box", "width": 0.6, "length": l, "height": PH + 0.03, "walked": True, "at": [[x, y, z, a]],
                     **({"_about": "the travertine rays from the obelisk across the setts"} if i == 0 else {})})
add("ellipse band", {"type": "sweep", "kind": "prism", "closed": True, "step": 2.0,
                     "path": [[r3(52.0 * math.sin(2 * math.pi * k / 24)), r3(40.0 * math.cos(2 * math.pi * k / 24))] for k in range(24)],
                     "profile": [[-0.35, 0], [0.35, 0], [0.35, PH + 0.03], [-0.35, PH + 0.03]], "walked": True,
                     "_about": "the travertine band of the ellipse round the obelisk, inside the fountains"})

# ==== THE BASILICA =========================================================================================================
FZ, FD = -186.0, 12.0                                # the front: its face, depth (the narthex)
G0, G1, GA, BAL = 18.0, 15.0, 11.0, 1.5              # the ground storey (portals), the loggia storey (the order's 33 m: its columns
                                                     # 26.4, the real 27.5), the tall attic (Maderno's 11); the balustrade
WT = G0 + G1 + GA                                    # the walls' head over the floor (44): Michelangelo's attic is level with the front's
NZ0, NZ1, NW = FZ - FD, -247.0, 76.0                 # the nave's east block (aisles and chapels), from behind the front
NZ2, NW2 = -270.0, 98.0                              # the west block of the nave, wider (the great side chapels)
CZ, CW, CL = -323.0, 107.0, 106.0                    # Michelangelo's Greek cross: the crossing's z, its square
AR = 23.0                                            # the three apses' radius

# the PODIUM the basilica stands on (its floor F over the piazza): the plan of the front, the nave and the cross, and the apses
pod = [(-FW / 2, FZ), (FW / 2, FZ), (FW / 2, NZ0), (NW / 2, NZ0), (NW / 2, NZ1), (NW2 / 2, NZ1), (NW2 / 2, NZ2), (CW / 2 + 1.5, NZ2),
       (CW / 2 + 1.5, CZ - CL / 2 - 1.5), (-CW / 2 - 1.5, CZ - CL / 2 - 1.5), (-CW / 2 - 1.5, NZ2), (-NW2 / 2, NZ2), (-NW2 / 2, NZ1), (-NW / 2, NZ1), (-NW / 2, NZ0), (-FW / 2, NZ0)]
add("podium", {"type": "prism", "plan": {"points": [[r3(x), r3(z)] for x, z in pod]}, "height": F, "walked": True, "at": [[0, 0, 0, 0]],
               "_about": "the podium the basilica stands on, its floor three metres over the piazza"})
APSES = [("north apse", CW / 2, CZ, Q), ("south apse", -CW / 2, CZ, -Q), ("west apse", 0.0, CZ - CL / 2, math.pi)]
add("apse podia", {"type": "column", "radius": AR + 0.5, "height": F - 0.02, "sides": 32, "at": [[r3(x), 0, r3(z), 0] for _, x, z, _ in APSES]})

# --- MADERNO'S FRONT (roman_baroque.giant_front): the giant order through the portals' storey and the loggia's, the
# attic over it; EIGHT columns before the middle (four under the pediment, two more either side), the end bays (the
# bell towers' feet, under the clocks) in pilasters alone
DOORS = [0.0, -10.6, 10.6, -21.2, 21.2]
ARCHES, ENDS = [-33.0, 33.0], [-47.5, 47.5]
ytop = giant_front(add, bal, z=FZ, y=F, W=FW, D=FD, G0=G0, G1=G1, GA=GA, doors=DOORS, arches=ARCHES, ends=ENDS,
                   cols=[5.3, 15.9, 26.6, 40.2], pedCols=[5.3, 15.9])
# the CLOCKS over the end bays (Valadier's, 1786-90): a raised bay with the dial in an arch, a small cupola on it
for sx, nm in ((1, "north"), (-1, "south")):
    x = sx * (FW / 2 - 5.2)
    add(f"{nm} clock", {"type": "enclosure", "plan": {"rect": [9.0, 7.0]}, "thickness": 1.0, "height": 6.5, "courses": True,
                        "faces": {"0": [{"openings": [op(0.0, 4.4, 1.0, 4.6, True, glass=False)]}]},
                        "at": [[r3(x), r3(ytop + 0.4), r3(FZ - 4.0), 0]], **({"_about": "the clocks over the end bays, a dial in each arch"} if sx > 0 else {})})
    add(f"{nm} clock dial", {"type": "box", "width": 3.6, "length": 0.2, "height": 3.6, "at": [[r3(x), r3(ytop + 0.4 + 1.6), r3(FZ - 0.9), 0]]})
    add(f"{nm} clock cupola", {"type": "dome", "sides": 12, "radius": 3.2, "thickness": 0, "head": {"profile": "semicircular"},
                               "at": [[r3(x), r3(ytop + 0.4 + 6.5), r3(FZ - 4.0), 0]]})

# --- THE NAVE (Maderno's, 1607-15): two blocks behind the front, in the same order and attic; its clerestory and lead roof
tiersN = lambda L, k: [{"h": 20.0, "openings": {"pattern": str(k), "width": 3.6, "gap": r3(L / k - 4.2), "sill": 6.0, "springing": 13.0, "head": {"profile": "flat"},
                                                 "surround": {"head": "pediment", "pediment": "alternate"}}},
                        {"h": G0 + G1 - 20.0, "openings": {"pattern": str(k), "width": 3.0, "gap": r3(L / k - 3.6), "sill": 3.0, "springing": 9.0, "head": {"profile": "semicircular"}}},
                        {"openings": {"pattern": str(k), "width": 2.4, "gap": r3(L / k - 3.0), "sill": 2.2, "springing": 5.0, "head": {"profile": "flat"}}}]
NARCH = {"at": 0.0, "width": 22.0, "sill": 0, "springing": 21.0, "head": {"profile": "semicircular"}, "glass": False}
for nm, w, z0, z1, about in (("nave", NW, NZ0, NZ1, "the nave's east block: the nave and its aisles, Maderno's lengthening of Michelangelo's cross"),
                             ("nave chapels", NW2, NZ1, NZ2, "...its west block, wider by the great side chapels")):
    L = z0 - z1
    add(nm, {"type": "enclosure", "plan": {"rect": [w, r3(L)]}, "thickness": 2.4, "height": WT, "tiers": tiersN(L, max(1, round(L / 12))),
             "faces": {"0": [{"h": G0 + G1, "openings": [NARCH]}, {"openings": []}], "2": [{"h": G0 + G1, "openings": [NARCH]}, {"openings": []}]},
             "orders": [{"tier": 0, "kind": "corinthian", "span": 2}], "courses": {"skip": [0, 2]}, "interior": True,
             "at": [[0, F, r3((z0 + z1) / 2), 0]], "_about": about})
    add(f"{nm} roof", {"type": "prism", "plan": {"rect": [w, r3(L)]}, "height": 0.6, "flatRoof": True, "at": [[0, r3(F + WT), r3((z0 + z1) / 2), 0]]})
NC0, NC1 = NZ0 - 1.0, NZ2 - 6.0
add("clerestory", {"type": "enclosure", "plan": {"rect": [29.0, r3(NC0 - NC1)]}, "thickness": 1.4, "height": 6.0,
                   "tiers": [{"openings": {"pattern": "6", "width": 3.2, "gap": r3((NC0 - NC1) / 6 - 3.8), "sill": 1.0, "springing": 3.6, "head": {"profile": "segmental", "rise": 1.2}}}],
                   "faces": {"0": [{"openings": []}], "2": [{"openings": []}]},
                   "at": [[0, r3(F + WT + 0.6), r3((NC0 + NC1) / 2), 0]], "_about": "the nave's high wall over the aisles' terraces, its vault under the roof"})
add("nave gable", {"type": "roof", "form": "gable", "width": 30.0, "length": r3(NC0 - NC1), "pitch": 20, "overhang": 0.5,
                   "at": [[0, r3(F + WT + 6.6), r3((NC0 + NC1) / 2), 0]], "_about": "the nave's lead roof"})

# --- MICHELANGELO'S CROSS: the square round the crossing in the giant order, an apse on three sides, the attic; flat roofs
# its PLAN (OSM, simplified): the square's corners stand out as L-shaped blocks, the faces between them step back, and
# CHAMFERS lead from them out to each apse, meeting its ring where its first bay begins (so the apse, its last bays
# cut off, grows out of the wall); across each apse's mouth the wall is hidden inside. Face by face: s along the side
# as it is walked, n outward from the square's face
CA, CB = CW / 2, CL / 2                              # the square's half widths (x, z)
KO, K1, K2 = 1.5, 44.0, 32.0                         # the corner blocks' projection, where they end, where the chamfers begin
AE = math.radians(67.5)                              # the apses' rings end there (from their axis): the chamfers meet them
side = lambda s0: [(s0, KO), (K1, KO), (K1, -KO), (K2, -KO), (AR * math.sin(AE), AR * math.cos(AE)),
                   (-AR * math.sin(AE), AR * math.cos(AE)), (-K2, -KO), (-K1, -KO), (-K1, KO)]
SIDES = [(CB, lambda s_, n: (CA + n, s_)), (CA + KO, lambda s_, n: (s_, -CB - n)), (CB + KO, lambda s_, n: (-CA - n, -s_))]
cross_pts = [(-CA - KO, CB)] + [f(s_, n) for s0, f in SIDES for s_, n in side(s0)]
winC = lambda ped: [{"h": 20.0, "openings": [op(0.0, 3.6, 6.0, 8.0, False, surround={"head": "pediment", "pediment": ped})]},
                    {"h": G0 + G1 - 20.0, "openings": [op(0.0, 3.0, 3.0, 7.0, True)]}, {"openings": [op(0.0, 2.6, 2.0, 3.2, False)]}]
blank = [{"h": 20.0, "openings": []}, {"h": G0 + G1 - 20.0, "openings": []}, {"openings": []}]
facesC = {"0": [{"h": G0 + G1, "openings": [NARCH]}, {"openings": []}]}
for k in range(3):
    for j, ped in ((0, "segmental"), (2, "triangular"), (3, "segmental"), (5, "segmental"), (6, "triangular"), (8, "segmental")):
        facesC[str(1 + 9 * k + j)] = winC(ped)
add("cross", {"type": "enclosure", "plan": {"points": [[r3(x), r3(z)] for x, z in cross_pts]}, "thickness": 3.0, "height": WT, "tiers": blank,
              "faces": facesC, "orders": [{"tier": 0, "kind": "corinthian", "span": 2}], "courses": {"skip": [0]}, "interior": True,
              "at": [[0, F, CZ, 0]], "_about": "Michelangelo's Greek cross round the crossing: its corners standing out, chamfered to the apses; "
                                               "the giant Corinthian order, two rows of windows between its pilasters, the attic"})
add("cross roof", {"type": "prism", "plan": {"points": [[r3(x), r3(z)] for x, z in cross_pts], "well": {"radius": 20.4, "sides": 32}}, "height": 0.6, "flatRoof": True,
                   "railing": False, "at": [[0, r3(F + WT), CZ, 0]], "_about": "its flat roof, the terrace round the dome's base, the well over the crossing"})
VR = 2.5                                             # the apses' low vaults: a half dome of that rise, its cut end closed by a screen
_rho = (AR * AR + VR * VR) / (2 * VR)
VEND = [[r3(AR * (k / 8 - 1)), r3(math.sqrt(_rho ** 2 - (AR * (k / 8 - 1)) ** 2) - (_rho - VR))] for k in range(17)]
for nm, x, z, yaw in APSES:
    add(nm, {"type": "ring", "count": 16, "range": [-3, 2], "turn": 0.5, "rOuter": AR, "rInner": AR - 3.0, "height": G0 + G1,
             "opening": {"width": 3.4, "sill": 8.0, "springing": 18.0, "head": {"profile": "semicircular"}}, "orders": [{"kind": "corinthian"}],
             "courses": True, "place": [[r3(x), F, r3(z), r3(yaw)]], **({"_about": "the three apses, in the same order and attic: half rings on the cross's faces"} if nm.startswith("north") else {})})
    add(f"{nm} attic", {"type": "ring", "count": 16, "range": [-3, 2], "turn": 0.5, "rOuter": AR, "rInner": AR - 2.0, "height": GA, "y": G0 + G1,
                        "opening": {"width": 2.4, "sill": 2.0, "springing": 5.2, "head": {"profile": "flat"}}, "courses": True,
                        "place": [[r3(x), F, r3(z), r3(yaw)]], "standsOn": [nm]})
    add(f"{nm} vault", {"type": "dome", "sweep": 0.5, "sides": 16, "radius": AR, "thickness": 0.8, "head": {"profile": "segmental", "rise": VR},
                        "at": [[r3(x), r3(F + WT), r3(z), r3(yaw)]], "standsOn": [f"{nm} attic"]})
    add(f"{nm} vault end", {"type": "screen", "t": 0.6, "outline": VEND, "at": [[r3(x), r3(F + WT), r3(z), r3(yaw)]], "standsOn": [f"{nm} vault"],
                            **({"_about": "the vault's cut end over the cross's terrace, closed"} if nm.startswith("north") else {})})
    add(f"{nm} interior", {"type": "interior", "plan": {"sides": 16, "radius": AR - 1.5}, "arc": [-67.5, 67.5], "height": WT, "at": [[r3(x), F, r3(z), r3(yaw)]]})

# --- THE DOME: the high base over the terraces, the drum-dome -- drum with its 16 buttresses and their paired columns, the
# windows under alternating pediments, the attic, the ribbed dome raised by Della Porta; the lantern, ball and cross
R_IN, DT, DH, ATT = 20.75, 3.0, 18.0, 7.0
BASEH = 8.4
yB = F + WT + 0.6
add("dome base", {"type": "ring", "count": 32, "rOuter": 30.6, "rInner": R_IN, "height": BASEH, "y": yB, "turn": 0.5, "solid": True, "courses": True,
                  "place": [[0, 0, CZ, 0]], "_about": "the high round base over the terraces the drum stands on"})
yD = yB + BASEH
SPREAD = 0.5
add("dome", comp("components/drum-dome", {"R": R_IN, "dt": DT, "H": DH, "n": 16, "every": 1, "winW": 3.0, "winSill": 4.0, "winH": 8.0, "winHead": "flat",
                                          "profile": "pointed", "spread": SPREAD, "domeT": 1.6, "colR": 0.85, "colH": 15.0, "butW": 4.4, "butD": 3.4,
                                          "attic": "yes", "atticH": ATT, "ribsN": 16, "ribW": 1.0, "lanternR": 4.6, "lanternH": 10.0, "lanternSides": 16,
                                          "lanternCapR": 3.4, "lanternDrumH": 2.2},
                 [[0, r3(yD), CZ, 0]], build=["drum a", "drum b", "buttresses", "paired columns", "buttress entablature", "buttress cornice",
                                              "drum entablature", "drum cornice", "attic piers", "attic strips", "attic strips 2", "dome", "rib pairs", "rib pairs 2",
                                              "lucarnes 1", "lucarne roofs 1", "lucarnes 2", "lucarne roofs 2", "lucarnes 3", "lucarne roofs 3",
                                              "ribbed lantern", "lantern columns", "lantern spire", "lantern ball", "lantern cross", "lantern cross arm"],
                 _about="Michelangelo's drum: sixteen buttresses with a pair of Corinthian columns on each, a window between each two under "
                        "triangular and segmental pediments by turns; the attic with its paired strips; Della Porta's raised dome with its "
                        "sixteen DOUBLE ribs and three rows of lucarnes; the lantern of paired columns, its spire, the ball and the cross, "
                        "standing on the dome where it narrows to them (drum-dome by name)"))
# the dome's interior seen from the church: the crossing's space on up through the base to the drum
add("dome well", {"type": "interior", "plan": {"sides": 32, "radius": R_IN + 0.4}, "height": BASEH + 0.6, "at": [[0, r3(F + WT), CZ, 0]],
                  "_about": "the church's space on up through the dome's base to the drum's"})

# the MINOR CUPOLAS (Vignola's, over the Gregorian and Clementine chapels) at the cross's front corners, and the small
# cupolas over the nave's side chapels
for sx, nm in ((1, "north"), (-1, "south")):
    add(f"{nm} cupola", comp("components/drum-dome", {"R": 6.0, "dt": 1.0, "H": 6.0, "n": 16, "every": 2, "winW": 1.4, "winSill": 1.6, "winH": 3.0,
                                                      "profile": "pointed", "spread": 0.45, "domeT": 0.6, "ribsN": 16, "ribW": 0.4,
                                                      "lanternR": 1.5, "lanternH": 4.0},
                             [[r3(sx * 37.0), r3(F + WT + 0.6), r3(CZ + 36.0), 0]], build=["drum", "drum piers", "dome", "ribs", "lantern"],
                             **({"_about": "the two minor cupolas (Vignola's) at the cross's front corners"} if sx > 0 else {})))
    for i, z in enumerate((-212.0, -232.0)):
        add(f"{nm} chapel cupola {i}", comp("components/drum-dome", {"R": 3.4, "dt": 0.6, "H": 2.4, "n": 8, "every": 2, "winW": 0.9, "winSill": 0.6, "winH": 1.2,
                                                                      "profile": "semicircular", "domeT": 0.4, "lanternR": 0.8, "lanternH": 2.0},
                                            [[r3(sx * 29.0), r3(F + WT + 0.6), z, 0]], build=["drum", "drum piers", "dome", "lantern"],
                                            **({"_about": "the small cupolas over the nave's side chapels"} if sx > 0 and i == 0 else {})))

# ==== THE STATUES (statuary.py; the 50 most prominent): Christ, the Baptist and eleven apostles on the front's balustrade
# (5.7 m), then the saints on the colonnade's inner balustrade, as many as the cap leaves (3.1 m; 140 in all in Rome)
stat = {}
yS = ytop + 0.4 + 1.3
xs = [0.0] + [s * x for x in (5.3, 10.6, 15.9, 21.2, 26.6, 31.8) for s in (-1, 1)]
holds = [{"R": "items/tools/staff"}, {"R": "items/tools/book"}, {"R": "items/weapons/sword"}, {"R": "items/tools/staff"}]
for i, x in enumerate(xs):
    stat[f"statue front {i}"] = statue((r3(x), r3(yS), r3(FZ - 0.6)), kind="man", style="roman", stone="limestone",
                                       scale=3.2, seed=31 + i, face=FACE_PZ, **({"hold": holds[i % len(holds)]} if i else {}))
yC = TOPC + BALH
rS = R0 - 0.8 * 1.6 - 0.7 + 0.1 + 0.25
for sx, nm in ((1, "north"), (-1, "south")):
    pts = arc_points(sx * AX, 0.0, rS, -ARC / 2 + 3, -8.0, 9, yC, sx * Q) + arc_points(sx * AX, 0.0, rS, 8.0, ARC / 2 - 3, 9, yC, sx * Q)
    for i, (x, y, z) in enumerate(pts):
        stat[f"statue {nm} colonnade {i}"] = statue((x, y, z), kind="man" if i % 5 else "woman", style="roman", stone="limestone", scale=1.75,
                                                    seed=101 + i + (0 if sx > 0 else 40), face=look(sx * AX - x, -z),
                                                    **({"hold": holds[i % len(holds)]} if i % 3 == 0 else {}))
for sx, nm, hold in ((1, "paul", "items/weapons/sword"), (-1, "peter", "items/tools/book")):
    stat[f"statue {nm}"] = statue((r3(sx * 17.0), 3.6, -139.5), kind="man", style="roman", stone="limestone", scale=2.6, seed=7 if sx > 0 else 8,
                                  face=FACE_PZ, hold={"R": hold})
for k, v in capped(stat).items(): add(k, v)
for k, v in bal.parts("balustrade").items(): add(k, v)

doc = {"name": "St. Peter's Basilica",
       "_about": "ST PETER'S BASILICA AND SQUARE, Rome: Bernini's colonnade of four rows of Tuscan columns in two arms round the obelisk and the two fountains, "
                 "the straight corridors to the front, the steps; Maderno's front in the giant order (eight columns) with its loggia, attic and thirteen statues, the nave, "
                 "Michelangelo's Greek cross with its apses and the dome on its drum of paired columns, raised by Della Porta, its lantern 136.57 m to the cross. "
                 "Written by tools/archgen/st_peters.py.",
       "params": {"detail": 4}, "build": build, "parts": parts}
write_components()                                   # the square's components first (roman_baroque.py)
open(os.path.join(ROOT, "assets/architecture/st-peters.json"), "w").write(json.dumps(doc, indent=2) + "\n")
print(len(parts), "parts;", sum(1 for v in parts.values() if v.get("role") == "statue"), "statues")
