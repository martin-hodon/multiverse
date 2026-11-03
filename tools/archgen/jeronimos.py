# THE JERONIMOS MONASTERY (Mosteiro dos Jeronimos, Belem, Lisbon; 1501-1601, MANUELINE, in pale gold lioz limestone),
# from parts and components: the church of Santa Maria de Belem -- a HALL church (three naves of one height on six
# slender octagonal columns, one flat rib vault over all three), its transept a single vault without supports, the
# classical chancel under a barrel, the coro alto (the raised choir) over the west bay -- with the great SOUTH PORTAL
# (`manueline-portal`, components/) on its long south side and the west portal inside the narthex; the bell tower at the
# church's west end by the coro alto (`mitre-tower`: its pointed "mitre" dome); the CLOISTER north of the nave (a
# two-storey `court` on a chamfered square, four broad traceried arches a wing between massive pinnacled buttresses, the
# walks vaulted, a balustrade over the lower arcade); and the 19th-century range carrying the south front on west -- its
# ground storey an arcade between buttresses that rise through the eaves into pinnacles, carved window frames above,
# a crest along the top, a central body between two pinnacled turrets -- to the tall neo-Manueline WEST TOWER (`mitre-
# tower` with its crocketed spire and corner turret).
#   x runs along the church (east +x), +z is SOUTH: the long front toward the river and the Praca do Imperio.
#   SOURCED (Wikipedia en/pt; OSM relation 11318402 and the monastery's outline, turned 18.66 degrees so the church's axis
#   is x): the south portal about 32 m high and 12 m wide, two storeys of niches, twin doors with Henry the Navigator on the
#   trumeau, the Madonna above, the cross of the Order of Christ at the top; the nave three aisles of equal height, the
#   single vault 19-22 m wide on six octagonal columns, the transept vault spanning about 30 m without support, the transept
#   barely projecting; the cloister about 55 m square, two storeys, chamfered corners, the wings of four broad bays on
#   massive buttresses and the corner bays on the diagonal, a balustrade over the lower walk; the bell tower at the west end
#   of the church's north side; the plan's footprint (church x 29.5 to 124.6 m, the chancel rectangular, the cloister's
#   garth about 41 m, the whole front about 300 m) from OSM; the range's front: arcaded ground storey, buttresses with
#   pinnacles, the west tower (1860s-90s) with its spire.
#   ESTIMATED: the heights (vault springing 22, crown 25.6, walls 27, the coro alto at 9.5, cloister storeys 6.5, the
#   19th-century range 2 x 7, the bell tower about 44 and the west tower about 48 m), the bay divisions, the narthex and the
#   range west of the cloister, the window sizes, the range's court behind the front.
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapes import inset_points, plan_edges
from manueline import write_components, portal_doors, front_buttresses, crest, seg_edge, ROPE_FRAME, ROPE_FRAME1
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
r4 = lambda v: round(v, 4)
Q = math.pi / 2
semi = {"profile": "semicircular"}
OX = 23.0                                  # (the OSM numbers below, shifted so the site is centred on x)
rect_pts = lambda x0, z0, x1, z1: [[x0, z1], [x1, z1], [x1, z0], [x0, z0]]    # (a rect as an outline: faces 0 +z, 1 +x, 2 -z, 3 -x)

write_components(ROOT)                     # (L1: components/manueline-portal, components/mitre-tower -- manueline.py)

# ================================================================ THE CHURCH (Santa Maria de Belem)
T = 2.0                                    # its walls
SPRING, RISE, TOP = 22.0, 3.6, 27.0        # the vault's springing, its rise, the walls' top
VTOP = SPRING + RISE + 0.3                 # the vault's extrados
NX0, NX1 = OX + 29.5, OX + 80.0            # the nave: x (west front .. the transept)
TX1 = OX + 99.0                            # the transept's east wall
CX1 = OX + 122.0                           # the chancel's east end
NZ0, NZ1 = 25.9, 51.5                      # the nave's north and south faces
TZ0, TZ1 = 22.9, 54.5                      # the transept's ends (it projects 3 m)
CZ0, CZ1 = 30.5, 47.0                      # the chancel's flanks
NZ = (NZ0 + NZ1) / 2                       # 38.7: the church's axis
OUT = [[NX0, NZ1], [NX1, NZ1], [NX1, TZ1], [TX1, TZ1], [TX1, CZ1], [CX1, CZ1], [CX1, CZ0], [TX1, CZ0], [TX1, TZ0], [NX1, TZ0], [NX1, NZ0], [NX0, NZ0]]
E = plan_edges(OUT)
at_x = lambda f, x: r4((x - E[f]["mid"][0]) * E[f]["e"][0])        # along a face running in x: the place of x
BAYS = 4
NI0, NI1 = NX0 + T, NX1 + T                # the nave's inside runs on to the transept's (no wall between: a hall)
BAY = (NI1 - NI0) / BAYS                   # 12.625
ZI0, ZI1 = NZ0 + T, NZ1 - T                # 27.9 .. 49.5: three aisles of 7.2
AIS = (ZI1 - ZI0) / 3
bayx = [NI0 + BAY * (k + .5) for k in range(BAYS)]
colx = [NI0 + BAY * k for k in range(1, BAYS)]
colz = [ZI0 + AIS, ZI0 + 2 * AIS]
PORTAL_BAY = 2                             # the south portal in the third bay
PX_ = bayx[PORTAL_BAY]
SP = {"W": 12.0, "H": 32.0, "D": 2.0, "pw": 1.6, "doorW": 2.6, "doorH": 6.2, "gap": 1.0, "tiers": 4, "taper": 0.88, "orders": 3}
WP = {"W": 7.6, "H": 15.0, "D": 1.2, "pw": 1.1, "doorW": 1.8, "doorH": 5.0, "gap": 0.8, "tiers": 1, "orders": 1}
win = lambda at, w=3.8, sill=9.0, spring=18.5, **kw: {"at": r4(at), "width": w, "sill": sill, "springing": spring, "head": semi, "tracery": {"lights": 3}, "surround": ROPE_FRAME, **kw}
south = [win(at_x(0, bayx[k])) for k in range(BAYS) if k != PORTAL_BAY] + portal_doors(SP, at_x(0, PX_))
north = [win(at_x(10, x), w=3.4, sill=16.0, spring=21.0) for x in bayx] + \
        [{"at": at_x(10, OX + 57.0), "width": 2.4, "sill": 0, "springing": 3.0, "head": semi, "glass": False}]   # (the door from the cloister)
add("church", {"type": "enclosure", "plan": {"points": [[r4(x), r4(z)] for x, z in OUT]}, "thickness": T, "height": TOP,
               "faces": {"0": south, "2": [win(0, w=6.0, sill=9.0, spring=19.0, tracery={"lights": 4})],
                         "4": [win(s * 5.5, w=3.0, sill=12.0, spring=19.0, tracery=False, surround={"head": "cornice"}) for s in (-1, 1)],
                         "6": [win(s * 5.5, w=3.0, sill=12.0, spring=19.0, tracery=False, surround={"head": "cornice"}) for s in (-1, 1)],
                         "8": [win(0, w=6.0, sill=12.0, spring=19.0, tracery={"lights": 4})],
                         "10": north,
                         "11": [{"h": 12.0, "openings": portal_doors(WP, 0)}, {"openings": [win(0, w=4.0, sill=7.5, spring=12.0)]}],
                         "1": [], "3": [], "5": [], "7": [], "9": []},
               "_about": "the church's walls on one outline: the nave and aisles (a hall), the transept projecting 3 m, the chancel; the south front's tall windows and the twin doors of the portal, the west portal's twin doors (inside the narthex), the door from the cloister, the windows over the cloister's roof"})
add("nave columns", {"type": "column", "radius": 0.65, "height": SPRING, "sides": 8, "at": [[r4(x), 0, r4(z), 0] for x in colx for z in colz],
                     "_about": "the six slender octagonal columns, carved all over in candelabra panels, the vault's ribs fanning from their heads"})
add("nave vaults", {"type": "groin", "width": r4(BAY), "length": r4(AIS), "springing": SPRING, "top": VTOP,
                    "across": {"profile": "segmental", "rise": RISE}, "along": {"profile": "segmental", "rise": RISE},
                    "at": [[r4(x), 0, r4(z), 0] for x in bayx for z in (ZI0 + AIS / 2, NZ, ZI1 - AIS / 2)],
                    "_about": "the hall's vault: one flat bay over every column square, all at one crown"})
add("nave ribs", {"type": "ribs", "on": "nave vaults", "width": 0.4, "depth": 0.3, "wall": {"width": 0.6, "depth": 0.3}})
TI0, TI1 = NX1 + T, TX1 - T
add("transept vault", {"type": "groin", "width": r4(TI1 - TI0), "length": r4(TZ1 - TZ0 - 2 * T), "springing": SPRING, "top": VTOP,
                       "across": {"profile": "segmental", "rise": RISE}, "along": {"profile": "segmental", "rise": RISE},
                       "at": [[r4((TI0 + TI1) / 2), 0, NZ, 0]], "_about": "the transept's one vault, nearly 28 m from end to end with nothing under it"})
add("transept ribs", {"type": "ribs", "on": "transept vault", "width": 0.4, "depth": 0.3, "wall": {"width": 0.6, "depth": 0.3}})
add("chancel arch", {"type": "wall", "width": r4(CZ1 - CZ0), "height": TOP, "thickness": T,
                     "openings": [{"at": r4((CZ1 - CZ0) / 2), "width": 10.0, "sill": 0, "springing": 19.0, "head": semi, "glass": False}],
                     "at": [[TX1, 0, r4(NZ), Q]], "_about": "the arch from the transept into the chancel"})
add("chancel vault", {"type": "barrel", "width": r4(CZ1 - CZ0 - 2 * T), "length": r4(CX1 - T - TX1), "springing": 20.0, "top": 26.6, "head": semi,
                      "at": [[r4(CX1 - T), 0, NZ, Q]], "_about": "the chancel's coffered barrel (a barrel runs from its place back along -z: here from the east wall west) (Jeronimo de Ruao, 1570s)"})
# the coro alto: the raised choir over the west bay, on the walls and the first columns
add("coro alto", {"type": "box", "width": r4(BAY + T / 2), "length": r4(ZI1 - ZI0 + T), "height": 0.8, "at": [[r4(NI0 + (BAY - T / 2) / 2), 9.5, NZ, 0]], "walked": True,
                  "_about": "the coro alto, the monks' raised choir over the west bay"})
add("coro alto balustrade", {"type": "cresting", "run": [[r4(-(ZI1 - ZI0) / 2), 0], [r4((ZI1 - ZI0) / 2), 0]], "h": 1.1, "panel": 1.2, "t": 0.25,
                             "at": [[r4(colx[0] - 0.2), 10.3, NZ, Q]], "standsOn": ["coro alto"]})
# the south front: buttresses with their pinnacles, the openwork crest along every wall's top
BUT = [NX0 + 1.25, colx[0], NX1 - 1.4]
add("buttresses", {"type": "box", "width": 2.4, "length": 2.8, "height": 24.0, "at": [[r4(x), 0, NZ1 + 1.0, 0] for x in BUT] +
                   [[r4(x), 0, s, 0] for x in (NX1 + 1.4, TX1 - 1.4) for s in (TZ1 + 1.0,)] + [[r4(x), 0, TZ0 - 1.0, 0] for x in (NX1 + 1.4, TX1 - 1.4)] +
                   [[r4(CX1 + 1.0), 0, r4(z), 0] for z in (CZ0 + 1.4, CZ1 - 1.4)],
                   "_about": "the buttresses of the south front and at the transept's and chancel's corners"})
add("buttress pinnacles", comp("components/pinnacle", {"w": 1.6, "h": 2.4, "s": 5.0}, [[a[0], 24.0, a[2], 0] for a in parts["buttresses"]["at"]], standsOn=["buttresses"]))
crest(add, "crest", [e for e in E if e["L"] >= 4], TOP, about="the openwork crest along the walls' top")
add("nave roof", {"type": "roof", "form": "hip", "width": r4(NZ1 - NZ0 - 1.0), "length": r4(NX1 - NX0 - 1.0), "pitch": 18, "overhang": 0, "at": [[r4((NX0 + NX1) / 2 - 0.5), TOP, NZ, Q]]})
add("transept roof", {"type": "roof", "form": "hip", "width": r4(TX1 - NX1 - 1.0), "length": r4(TZ1 - TZ0 - 1.0), "pitch": 18, "overhang": 0, "at": [[r4((NX1 + TX1) / 2), TOP, NZ, 0]]})
add("chancel roof", {"type": "roof", "form": "hip", "width": r4(CZ1 - CZ0 - 1.0), "length": r4(CX1 - TX1), "pitch": 18, "overhang": 0, "at": [[r4((TX1 + CX1) / 2), TOP, NZ, Q]]})
# its portals
add("south portal", comp("components/manueline-portal", SP, [[r4(PX_), 0, NZ1, 0]],
                         _about="the SOUTH PORTAL (Joao de Castilho, 1516-18): 32 m of carved lioz round the twin doors -- Henry the Navigator on the trumeau, the Madonna in the tabernacle, the cross of the Order of Christ at the top"))
add("west portal", comp("components/manueline-portal", WP, [[NX0, 0, NZ, -Q]],
                        _about="the WEST PORTAL (Nicolau Chanterene, 1517), inside the narthex: the same screen, smaller"))
# its space, and its furniture
add("church interior", {"type": "interior", "plan": {"points": inset_points(OUT, T / 2)}, "height": TOP, "at": [[0, 0, 0, 0]], "_about": "the church's space: nave, transept and chancel, to the walls' top"})
add("seating", {"type": "zone", "zone": "seating", "w": r4(AIS - 2.4), "d": r4(BAY * 2.6), "h": 9.0, "at": [[r4(colx[0] + BAY * 1.4), 0, NZ, 0]]})
add("altar", {"type": "zone", "zone": "altar", "w": 8.0, "d": 3.2, "h": 12.0, "at": [[r4(CX1 - T - 4.0), 0, NZ, 0]]})

# ================================================================ THE NARTHEX, THE BELL TOWER BY IT, THE WEST RANGE
AX1 = OX + 8.5                             # the 19th-century range's east end, the narthex's west wall
AZ1 = 48.0                                 # the front's line
NTX, NTZ = (AX1 + NX0) / 2, (AZ1 + NZ0) / 2   # the narthex's middle
NH = 18.0                                  # the narthex's height (over the west portal)
BTW = 10.0                                 # the bell tower: at the church's west end, north of the narthex, by the coro alto
BTX, BTZ = NX0 - BTW / 2, NZ0 - BTW / 2
THX = (AX1 + NX0 - BTW) / 2                # the stair hall west of it
add("narthex", {"type": "enclosure", "plan": {"rect": [r4(NX0 - AX1), r4(AZ1 - NZ0)]}, "thickness": 1.2, "height": NH,
                "faces": {"0": [{"h": 9.0, "openings": [{"at": 0, "width": 4.0, "sill": 0, "springing": 5.0, "head": semi, "glass": False, "surround": ROPE_FRAME}]},
                                {"openings": [win(0, w=4.0, sill=1.5, spring=6.0)]}],
                          "1": [{"at": 0, "width": WP["W"] + 0.4, "sill": 0, "springing": WP["H"] + 0.6, "head": {"profile": "flat"}, "glass": False}],
                          "2": [{"at": r4(-(BTX - NTX)), "width": 1.6, "sill": 0, "springing": 2.4, "head": semi, "glass": False},
                                {"at": r4(-(THX - NTX)), "width": 2.0, "sill": 0, "springing": 2.6, "head": semi, "glass": False}],
                          "3": [{"at": 0, "width": 2.4, "sill": 0, "springing": 3.0, "head": semi, "glass": False}]},
                "at": [[r4(NTX), 0, r4(NTZ), 0]],
                "_about": "the narthex before the west portal: its own door from the street, the portal filling its east side, the doors to the bell tower and the stair hall on the north, to the range on the west"})
add("narthex ceiling", {"type": "coffered-ceiling", "width": r4(NX0 - AX1 - 1.2), "length": r4(AZ1 - NZ0 - 1.2), "thickness": 0.6, "nx": 5, "nz": 5, "at": [[r4(NTX), NH - 0.6, r4(NTZ), 0]]})
add("narthex roof", {"type": "roof", "form": "hip", "width": r4(NX0 - AX1), "length": r4(AZ1 - NZ0), "pitch": 25, "overhang": 0.4, "at": [[r4(NTX), NH, r4(NTZ), 0]]})
add("narthex interior", {"type": "interior", "plan": {"rect": [r4(NX0 - AX1 - 1.2), r4(AZ1 - NZ0 - 1.2)]}, "height": NH, "at": [[r4(NTX), 0, r4(NTZ), 0]]})
add("bell tower", comp("components/mitre-tower", {"W": BTW, "H": 30.0, "t": 1.3, "belfryH": 7.5, "bells": 2, "doorAt": 0, "spread": 1.6},
                       [[r4(BTX), 0, r4(BTZ), 0]],
                       _about="the bell tower at the church's west end, over the coro alto, its pyramid replaced in 1867-68 by the pointed 'mitre' dome; its door from the narthex"))
WRZ0, WRZ1 = -29.1, BTZ - BTW / 2          # the west range: from the cloister's north side to the bell tower
WRX, WRZ = (AX1 + NX0) / 2, (WRZ0 + WRZ1) / 2
add("stair hall", {"type": "enclosure", "plan": {"rect": [r4(NX0 - BTW - AX1), BTW]}, "thickness": 1.0, "height": 14.0,
                   "faces": {"0": [{"at": 0, "width": 2.0, "sill": 0, "springing": 2.6, "head": semi, "glass": False}],
                             "2": [{"at": 0, "width": 2.0, "sill": 0, "springing": 2.6, "head": semi, "glass": False}], "1": [], "3": []},
                   "at": [[r4(THX), 0, r4(BTZ), 0]], "_about": "the stair hall between the narthex and the west range, beside the bell tower"})
add("stair hall roof", {"type": "roof", "form": "hip", "width": r4(NX0 - BTW - AX1), "length": BTW, "pitch": 28, "overhang": 0.3, "at": [[r4(THX), 14.0, r4(BTZ), 0]]})
add("stair hall interior", {"type": "interior", "plan": {"rect": [r4(NX0 - BTW - AX1 - 1.0), BTW - 1.0]}, "height": 14.0, "at": [[r4(THX), 0, r4(BTZ), 0]]})
WIN3 = {"pattern": "3", "width": 1.6, "gap": 3.4, "sill": 1.0, "springing": 4.0, "head": semi}
add("west range", {"type": "enclosure", "plan": {"rect": [r4(NX0 - AX1), r4(WRZ1 - WRZ0)]}, "thickness": 1.0, "height": 14.0,
                   "tiers": [{"h": 7.0, "openings": []}, {"openings": []}],
                   "faces": {"0": [{"h": 7.0, "openings": [{"at": r4(THX - WRX), "width": 2.0, "sill": 0, "springing": 2.6, "head": semi, "glass": False}]}, {"openings": []}],
                             "1": [{"h": 7.0, "openings": [{"at": r4(-(-1.6 - WRZ)), "width": 2.4, "sill": 0, "springing": 3.0, "head": semi, "glass": False}]}, {"openings": []}],
                             "2": [{"h": 7.0, "openings": WIN3}, {"openings": WIN3}],
                             "3": [{"h": 7.0, "openings": [{"at": 0, "width": 2.4, "sill": 0, "springing": 3.0, "head": semi, "glass": False}]}, {"openings": []}]},
                   "at": [[r4(WRX), 0, r4(WRZ), 0]],
                   "_about": "the range west of the cloister, between it and the 19th-century court: doors through from one to the other and to the stair hall"})
add("west range floor", {"type": "prism", "plan": {"rect": [r4(NX0 - AX1 - 1.0), r4(WRZ1 - WRZ0 - 1.0)]}, "height": 0.35, "at": [[r4(WRX), 6.65, r4(WRZ), 0]]})
add("west range roof", {"type": "roof", "form": "hip", "width": r4(NX0 - AX1), "length": r4(WRZ1 - WRZ0), "pitch": 28, "overhang": 0.4, "at": [[r4(WRX), 14.0, r4(WRZ), 0]]})
add("west range interior", {"type": "interior", "plan": {"rect": [r4(NX0 - AX1 - 1.0), r4(WRZ1 - WRZ0 - 1.0)]}, "height": 14.0, "at": [[r4(WRX), 0, r4(WRZ), 0]]})

# ================================================================ THE CLOISTER (claustro, two storeys, 55 m, chamfered)
CL, CH, CD, CT = 55.0, 10.0, 7.0, 1.2       # its side, its corners' chamfer, its walks' depth, its walls
CS, CHs = 2, 6.5                           # storeys
CCX, CCZ = OX + 57.0, NZ0 - CL / 2         # against the church's north wall
EVERY, AW = 7.0, 5.0                       # a bay, its arch: four a wing, one on each diagonal
ARC = [{"every": EVERY, "width": AW, "springing": 3.3, "sill": 0.8, "end": 1.0, "tracery": {"lights": 3},
        "buttress": {"w": 1.4, "d": 2.0, "h": CHs + 1.0, "min": 2, "pinnacle": {"w": 1.0, "h": 0.8, "s": 2.2}},
        "vault": {"ribs": {"width": 0.3, "depth": 0.2}}},
       {"every": EVERY, "width": AW - 0.8, "springing": 2.6, "sill": 1.0, "end": 1.0}]
MAIN, CHAM = CL - 2 * CH, CH * math.sqrt(2)
add("cloister", {"type": "court", "plan": {"rect": [CL, CL], "chamfer": CH}, "depth": CD, "storeys": CS, "storeyH": CHs, "thickness": CT,
                 "axis": 6.0, "winW": 1.2, "sill": 1.6, "winH": 2.2, "head": semi, "stairFace": 4, "arcade": ARC,
                 "roof": {"form": "hip", "pitch": 18}, "courses": True,
                 # (blank outside all round -- the church, the west range, the refectory and the chapter house stand there --
                 #  and doors through to the church on the south and the west range on the west)
                 "joins": [{"face": f, "at": 0, "width": r4(MAIN if f % 2 == 0 else CHAM),
                            **({"door": {"width": 2.4, "height": 3.6}} if f in (0, 2) else {})} for f in range(8)],
                 "at": [[r4(CCX), 0, r4(CCZ), 0]],
                 "_about": "the CLOISTER: four walks round the garth in two storeys on a chamfered square, open to it in broad traceried arches between massive pinnacled buttresses (the court's own), the walks vaulted, the corner bays on the diagonal; joined to the church on the south (a door into the nave) and to the west range"})
# over the lower arcade, round the garth: a ledge on the buttresses' line and a pierced balustrade on it
CPLAN = [[-CL / 2, -CL / 2 + CH], [-CL / 2, CL / 2 - CH], [-CL / 2 + CH, CL / 2], [CL / 2 - CH, CL / 2], [CL / 2, CL / 2 - CH], [CL / 2, -CL / 2 + CH], [CL / 2 - CH, -CL / 2], [-CL / 2 + CH, -CL / 2]]
GE = plan_edges([[x + CCX, z + CCZ] for x, z in inset_points(CPLAN, CD)])
LEDGE = 1.5
for L in sorted({round(e["L"], 2) for e in GE}):
    add(f"cloister ledge {round(L)}", {"type": "box", "width": L, "length": LEDGE + 0.2, "height": 0.35,
                                       "at": [[r4(e["mid"][0] + e["n_in"][0] * (LEDGE - 0.2) / 2), CHs - 0.35, r4(e["mid"][1] + e["n_in"][1] * (LEDGE - 0.2) / 2), r4(e["yaw"])]
                                              for e in GE if round(e["L"], 2) == L],
                                       "_about": "the ledge over the lower arcade, round the garth, run into the court walls"})
crest(add, "cloister balustrade", GE, CHs, h=1.0, inset=LEDGE - 0.25, spire=None, panel=1.0, t=0.2, end=0.3,
      about="the pierced balustrade over the lower arcade, between the buttresses' pinnacles")

# ================================================================ THE 19TH-CENTURY RANGE (Barret, Rambois & Cinatti, 1860s-90s)
# the long SOUTH FRONT as its own range -- an arcade on the ground storey, buttresses through the eaves into pinnacles,
# carved frames to the upper windows, a crest, a central body between two turrets -- with the court behind it plain, and
# the tall neo-Manueline tower at its west end
AX0 = OX - 160.0
FZ0 = 33.0                                 # the front range's back (the court's south face)
FX, FZD = (AX0 + AX1) / 2, AZ1 - FZ0       # its middle, its depth
FL = AX1 - AX0                             # 168.5
SH_ = 7.0                                  # a storey
AXIS, NA = 8.0, 21                         # the arcade: an arch every 8 m, 21 of them (odd: the middle one the gate)
offs = [(k - (NA - 1) / 2) * AXIS for k in range(NA)]
TUR = 12.0                                 # the central body's turrets, either side of the gate
arch = lambda o: {"at": r4(o), "width": 4.5, "sill": 0 if o == 0 else 0.5, "springing": 4.2, "head": semi, "glass": o != 0}
upper = lambda o: ({"at": r4(o), "width": 2.6, "sill": 1.2, "springing": 4.4, "head": semi, "tracery": {"lights": 2}, "surround": ROPE_FRAME} if abs(o) < TUR
                   else {"at": r4(o), "width": 2.0, "sill": 1.4, "springing": 4.4, "head": semi, "surround": ROPE_FRAME1})
FRONT = rect_pts(AX0, FZ0, AX1, AZ1)
FE = plan_edges(FRONT)
add("front range", {"type": "enclosure", "plan": {"rect": [FL, FZD]}, "thickness": 1.0, "height": 2 * SH_,
                    "faces": {"0": [{"h": SH_, "openings": [arch(o) for o in offs]}, {"openings": [upper(o) for o in offs]}],
                              "1": [{"h": SH_, "openings": [{"at": r4(-(NTZ - (FZ0 + AZ1) / 2)), "width": 2.4, "sill": 0, "springing": 3.0, "head": semi, "glass": False}]}, {"openings": []}],
                              "2": [{"h": SH_, "openings": [{"at": 0, "width": 4.2, "sill": 0, "springing": 3.4, "head": semi, "glass": False}]}, {"openings": []}],
                              "3": []},
                    "at": [[r4(FX), 0, r4((FZ0 + AZ1) / 2), 0]],
                    "_about": "the range's SOUTH FRONT: its ground storey an arcade of glazed round arches every 8 m (the middle one the gate through to the court), the upper windows in carved rope frames, the three over the gate wider and traceried"})
add("front range floor", {"type": "prism", "plan": {"rect": [FL - 1.0, FZD - 1.0]}, "height": 0.35, "at": [[r4(FX), SH_ - 0.35, r4((FZ0 + AZ1) / 2), 0]]})
add("front range roof", {"type": "roof", "form": "hip", "width": FZD, "length": FL, "pitch": 28, "overhang": 0.3, "at": [[r4(FX), 2 * SH_, r4((FZ0 + AZ1) / 2), Q]]})
add("front range interior", {"type": "interior", "plan": {"rect": [FL - 1.0, FZD - 1.0]}, "height": 2 * SH_, "at": [[r4(FX), 0, r4((FZ0 + AZ1) / 2), 0]]})
# its buttresses between the arches (and at the corners), up through the eaves into pinnacles -- the turrets stand for two
bo = [o + AXIS / 2 for o in offs[:-1] if abs(abs(o + AXIS / 2) - TUR) > 0.1] + [s * (FL / 2 - 0.6) for s in (-1, 1)]
front_buttresses(add, "front buttresses", FE[0], bo, w=1.2, d=1.4, h=2 * SH_ + 1.5, pin={"w": 1.0, "h": 1.0, "s": 3.2},
                 about="the front's buttresses between the arches, rising through the eaves")
# the central body: an attic between two octagonal turrets with crocketed caps, a crest along it and along the front
TR_, TH = 1.6, 2 * SH_ + 9.0
AT_H = 5.5
add("turrets", {"type": "prism", "plan": {"sides": 8, "radius": TR_}, "height": TH, "at": [[r4(FX + s * TUR), 0, r4(AZ1 + 0.6), 0] for s in (-1, 1)],
                "_about": "the central body's two turrets, flanking the gate, rising past the attic"})
add("turret caps", {"type": "pinnacle", "w": TR_ * 2.2, "h": 1.0, "s": 7.0, "sides": 8, "crockets": 1, "at": [[r4(FX + s * TUR), TH, r4(AZ1 + 0.6), 0] for s in (-1, 1)],
                    "standsOn": ["turrets"]})
AW_ = 2 * (TUR - TR_) + 1.0
add("attic", {"type": "wall", "width": r4(AW_), "height": AT_H, "thickness": 1.0,
              "openings": [{"at": r4(AW_ / 2), "width": 3.2, "sill": 0.8, "springing": 3.4, "head": semi, "tracery": {"lights": 3}, "surround": ROPE_FRAME1}],
              "at": [[r4(FX), 2 * SH_, AZ1, 0]], "standsOn": ["front range"], "_about": "the central body's attic over the gate, between the turrets"})
crest(add, "attic crest", [seg_edge([FX - AW_ / 2, AZ1], [FX + AW_ / 2, AZ1])], 2 * SH_ + AT_H)
crest(add, "front crest", [seg_edge([AX0, AZ1], [FX - TUR - TR_, AZ1]), seg_edge([FX + TUR + TR_, AZ1], [AX1, AZ1])], 2 * SH_,
      about="the openwork crest along the front's top")
# the court behind it: plain on all its sides; the gate through on the south, doors to the west range and the narthex
AZ0 = -62.0
AMX, AMZ = (AX0 + AX1) / 2, (AZ0 + FZ0) / 2
aat = lambda z: r4(-(z - AMZ))             # (along its east face, which runs -z)
add("range", {"type": "court", "plan": {"rect": [r4(AX1 - AX0), r4(FZ0 - AZ0)]}, "depths": [8.0, 14.0, 18.0, 14.0], "storeys": 2, "storeyH": SH_, "thickness": 1.0,
              "axis": 8.0, "winW": 1.6, "sill": 1.1, "winH": 3.0, "head": semi, "courses": True,
              "gate": {"face": 0, "width": 4.2, "height": 5.5}, "roof": {"form": "hip", "pitch": 28},
              "joins": [{"face": 0, "at": 0, "width": r4(AX1 - AX0), "door": {"width": 4.2, "height": 5.5}},
                        {"face": 1, "at": aat(WRZ), "width": r4(WRZ1 - WRZ0), "door": {"width": 2.4, "height": 3.6}},
                        {"face": 1, "at": aat((WRZ1 + FZ0) / 2), "width": r4(FZ0 - WRZ1)}],
              "at": [[r4(AMX), 0, r4(AMZ), 0]],
              "_about": "the 19th-century range's court behind the front (now the archaeology and navy museums): plain, two storeys; the gate through from the front, doors to the west range"})
WTW = 11.0
add("west tower", comp("components/mitre-tower", {"W": WTW, "H": 34.0, "t": 1.2, "belfryH": 7.0, "bells": 3, "wins": 2, "doorAt": 0, "spireH": 13.0},
                       [[r4(AX0 - WTW / 2), 0, r4(AZ1 - WTW / 2), -Q]],
                       build=["shaft", "stage floors", "courses", "stage pinnacles", "head", "balustrade", "pinnacles", "spire", "turret", "turret cap"],
                       _about="the tower at the front's west end (19th century, neo-Manueline): three pinnacled stages and the belfry, a crocketed spire, a stair turret at its outer corner; its door to the west"))

doc = {"name": "Jeronimos Monastery",
       "_about": "THE JERONIMOS MONASTERY, Belem (1501-1601, Manueline, in lioz): the church of Santa Maria -- a HALL church, one flat rib vault over three naves on six octagonal columns, the transept one unsupported vault, the barrel-vaulted chancel, the coro alto -- with the great SOUTH PORTAL (a `manueline-portal`: piers wound with ropes, a tabernacle of tapering niches, Henry the Navigator on the trumeau) on its long south side and the west portal in the narthex; the bell tower with its mitre dome at the west end (a `mitre-tower`); the two-storey CLOISTER on its chamfered square north of the nave (a `court` whose walks open in traceried arcades between pinnacled buttresses, vaulted, a balustrade over them); and the 19th-century range carrying the south front on west -- arcaded, buttressed, crested, a central body between turrets -- to its spired west tower, some 300 m in all. +z is south, the front.",
       "params": {"detail": 4}, "base": {"height": 0.6, "steps": 2, "stepOut": 0.5, "margin": 4}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/jeronimos.json"), "w").write(json.dumps(doc, indent=1) + "\n")

LIOZ = "lioz"
PLAIN = ["pier shafts", "archivolt", "trumeau", *[f"jamb {w} {k}" for k in (1, 2, 3) for w in ("order", "shafts")],
         *[f"niche {k} {w}" for k in (1, 2, 3, 4) for w in ("back", "posts", "canopy", "ledge")]]
fin = {"name": "Jeronimos Monastery", "building": "architecture/jeronimos",
       "_about": "Belem in lioz: the pale limestone in fine ashlar; the portals' piers and relief fields carved in the Manueline relief (twisted ropes, armillary spheres, the cross of the Order of Christ), their shafts and tabernacles plain, the nave's columns in candelabra panels, the crests, courses and frames in the Manueline band; terracotta roofs; the vaults bare stone; inside, the floors in grey and white marble, the chancel's barrel coffered.",
       "stone": {"color": "#ece3cc", "accent": "#d8cfb8", "pat": "ashlar"},
       "rules": [
           {"parts": "kind:glass", "opening": "head", "map": "opening", "pattern": "glass/tracery white", "palette": "grisaille"},
           {"parts": "kind:glass", "pattern": "glass/quarries", "palette": "grisaille", "_about": "clear leaded glass in the tall windows"},
           {"parts": PLAIN, "pattern": "stone/ashlar fine", "palette": LIOZ, "_about": "the portals' shafts, archivolt and tabernacle: plain lioz, so the carving reads against them"},
           {"parts": ["piers", "field"], "pattern": "stone/manueline relief", "palette": LIOZ, "scale": 0.6, "_about": "the portals' piers and the relief field over the doors, carved all over"},
           {"parts": ["nave columns"], "pattern": "stone/manueline candelabra", "palette": LIOZ, "_about": "the nave's columns: candelabra panels, grotesques and scrolls"},
           {"parts": "kind:moulding", "pattern": "stone/manueline band", "palette": LIOZ, "_about": "the crests, the string courses and the windows' frames: the Manueline band"},
           {"parts": ["chancel vault"], "pattern": "painted/caisson", "palette": LIOZ, "_about": "the chancel's coffered barrel"},
           {"parts": ["kind:groin", "kind:ribs"], "pattern": "stone/ashlar fine", "palette": LIOZ},
           {"parts": "kind:dome", "surface": "roof", "pattern": "stone/ashlar fine", "palette": LIOZ, "_about": "the stone mitre dome"},
           {"parts": "kind:roof", "surface": "roof", "pattern": "roofs/coppi", "palette": "terracotta"},
           {"surface": "floor", "side": "in", "pattern": "floors/checker diagonal", "palette": "marble-grey"},
           {"surface": "floor", "pattern": "floors/flagstones", "palette": "limestone"},
           {"surface": "wall", "pattern": "stone/ashlar fine", "palette": LIOZ, "_about": "everything else -- the walls, the buttresses -- in fine lioz ashlar"},
       ]}
open(os.path.join(ROOT, "assets/finishes/jeronimos.json"), "w").write(json.dumps(fin, indent=1) + "\n")
print(len(parts), "parts")
