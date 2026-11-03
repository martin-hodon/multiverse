# THE ALBRECHTSBURG, MEISSEN (1471-1524, Arnold von Westfalen), the first German palace-castle, WITH MEISSEN CATHEDRAL beside
# it on the Burgberg above the Elbe -- the view from the river is the two together.
#
# THE FRAME: OpenStreetMap's, unturned -- x EAST, z SOUTH (north is -z), metres from the castle's centroid (51.16663 N,
# 13.47153 E); y up from the foot of the hill. So the Elbe front looks north-east (+x -z) and the cathedral lies south.
#
# THE CASTLE: OSM's outline (way 204553512) read as the wings it is made of, each a block with its own walls and hipped
# roof -- the Elbe wing in three (its middle stepped back), the west wing, the north block turned 45 degrees, the
# projection toward the cathedral, the south wing along the choir. A low ground floor and two high main floors with the
# great CURTAIN-ARCH windows (the `curtain` head, arch/profiles.js) under steep tiled roofs (one per wing, hipped); on
# the eave the ring of LUCARNES (components/lucarne) -- the "wreath of tower figures"; in the Elbe front's middle the
# one block carried up as a real tower; on the court the GROSSER WENDELSTEIN (components/wendelstein) at the corner of
# the projection, and the small stair tower in the corner of the north and Elbe wings (the same component, smaller).
# THE CATHEDRAL (OSM way 22764552, its axis 18.1 degrees north of east): a seven-bay HALL nave (the `basilica` part,
# `hall`), the short transept and the long choir with its polygonal end, the Hoeckriger Turm in the angle of the south
# transept and the choir, the two west towers -- three square stages, the 1903-09 octagons and OPENWORK spires to 81 m
# over the cathedral floor -- and the Fuerstenkapelle before the west front.
# THE HILL: a battered rock mass to a ring of terrace walls, the plateau (court and Domplatz) at H0.
#
# SOURCED: the plans (OSM), the spires' 81 m, the nave's 17.8 m vault and 97.3 m length, seven hall bays, the Hoeckriger
# Turm's place (de.wikipedia). ESTIMATED from photographs: the plateau's 14 m over the foot (the real hill is ~40 m
# above the river), the castle's storeys (4.6 / 6.4 / 6.2 m), its 52-degree roofs, the lucarnes' size and count, the
# Wendelsteins' size, the Elbe tower's height, the west towers' stages (square to 44 m, octagon to 54 m), the
# Hoeckriger Turm's height, the cathedral's roof pitch.
import os, json, math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from late_gothic import Frame, curtain_window, lucarne_row, write_components, r4, wing, rect_faces, along, clear_span, storeys, plain_storeys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n); return n
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
P2 = lambda pts: [[r4(x), r4(z)] for x, z in pts]

H0 = 32.0                                       # the plateau (court, Domplatz) over the river's level
SUB = 10.0                                      # the Elbe side's terrace wall: the rock's top that far under the plateau
SUBD = SUB + 2.0                                # the castle's walls on that side carried down to the rock, and into it
G, F1, F2 = 4.6, 6.4, 6.2                       # the castle's storeys: low ground floor, the two main floors
STOREYS = [G, F1, F2]
EAVE = G + F1 + F2                              # over the court
PITCH = 52; OV = 0.3

def area(pts): return sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(pts, pts[1:] + pts[:1]))
def outside_right(pts): return list(reversed(pts)) if area(pts) > 0 else list(pts)   # (planPoints' winding)

# ---------------------------------------------------------------- the castle: its wings as blocks on OSM's plan
# (the outline, OSM way 204553512, is read as the wings it is made of -- each a block with its own walls and hipped roof
#  (late_gothic.wing), the blocks overlapping where the wings meet; the jogs under a metre or two left out). The Elbe
# front stands on the edge: its wings are carried SUB metres down the slope to the rock, the plateau ending at their walls.
# the castle's main frame: the Elbe wing runs 39.4 degrees south of east (u along it to the south-east, v to the Elbe)
A = math.radians(39.4); EU = (math.cos(A), math.sin(A)); EV = (math.sin(A), -math.cos(A))
def W(u, v): return (u * EU[0] + v * EV[0], u * EU[1] + v * EV[1])
YAW_U = math.atan2(EU[0], EU[1])                # a part's +z along u (its +x then along v)
# the south wing's frame: along the cathedral (OSM's 60 -> 45), `a` east, `b` north into the castle
SA = math.atan2(18.5 - 23.0, 28.7 - 5.7)
SE_, SN = (math.cos(SA), math.sin(SA)), (math.sin(SA), -math.cos(SA))
def S(a, b): return (5.7 + a * SE_[0] + b * SN[0], 23.0 + a * SE_[1] + b * SN[1])
YAW_S = math.atan2(SE_[0], SE_[1])              # +z along a, +x along b

DOOR = {"width": 2.4, "sill": 0, "springing": 2.8, "head": {"profile": "curtain", "rise": 0.5, "lobes": 1, "sag": 0.55, "seg": 6}}
UV = lambda u0, u1, v0, v1: (W((u0 + u1) / 2, (v0 + v1) / 2), v1 - v0, u1 - u0, YAW_U)   # (a wing in the castle's frame: faces 0 SE end, 1 river, 2 NW end, 3 court)
def castle_wing(name, g, faces, about, **kw): return wing(add, name, *g, faces, about, H0, STOREYS, pitch=PITCH, overhang=OV, **kw)

# the Elbe wing in three blocks -- the north part, the recessed middle, the south part with the tower -- the west wing
# across the north end of the court, the projection toward the cathedral, the south wing along the choir
G3, G4, G5, GW, G6 = UV(-20.0, -4.0, -9.0, 15.0), UV(-4.5, 7.5, -9.0, 9.0), UV(7.0, 26.0, -9.5, 14.0), UV(-38.5, -17.5, -19.5, 7.0), UV(1.5, 12.0, -16.5, -9.0)
G7 = (S(12.5, 5.0), 10.0, 25.0, YAW_S)          # (faces 0 east end, 1 north (in the castle), 2 west end, 3 south, to the cathedral)
B3, B4, B5, BW, B6, B7 = (rect_faces(*g) for g in (G3, G4, G5, GW, G6, G7))
castle_wing("elbe wing north", G3, {0: {"clear": [clear_span(B3[0], W(-4, -9.5), W(-4, 9.2))]}, 2: None,
                                    3: {"clear": [clear_span(B3[3], W(-20, -9), W(-17.3, -9)), clear_span(B3[3], W(-17.6, -9), W(-12.4, -9))]}},
            "the Elbe wing's north part: three storeys of curtain-arch windows to the river and the court", sub=SUBD, sub_open=(1,))
castle_wing("elbe wing middle", G4, {0: None, 2: None, 3: {"clear": [clear_span(B4[3], W(-2.6, -9), W(7.5, -9))]}},
            "the Elbe wing's middle, stepped back from the river front", sub=SUBD, sub_open=(1,))
castle_wing("elbe wing south", G5, {1: {"clear": [clear_span(B5[1], W(8.2, 14), W(14.4, 14))]}, 2: {"clear": [clear_span(B5[2], W(7, -9.5), W(7, 9.2))]}, 3: None},
            "the Elbe wing's south part, the tower in its river front", sub=SUBD, sub_open=(0, 1))
castle_wing("west wing", GW, {0: {"clear": [clear_span(BW[0], W(-17.5, -9.3), W(-17.5, 7))], "doors": [{**DOOR, "at": along(BW[0], W(-17.5, -14.5))}]}, 1: None},
            "the west wing, closing the court's north side; the castle's door from the court", ridge_along_l=False)
castle_wing("projection", G6, {0: None, 1: None, 2: None}, "the projection toward the cathedral, the Grosser Wendelstein before its end on the court")
castle_wing("south wing", G7, {1: None, 2: None}, "the south wing along the cathedral's choir")
NB = [(-25.7, -42.4), (-8.2, -45.9), (-5.8, -26.9), (-23.5, -28.2)]   # the north block, turned 45 degrees to the wings: OSM's own corners
add("north block", {"type": "enclosure", "plan": {"points": P2(NB)}, "thickness": 1.3, "height": EAVE, "glass": True, "tiers": storeys(STOREYS),
                    "courses": {"plinth": False, "strings": [G], "cornice": 0.45}, "at": [[0, H0, 0, 0]],
                    "_about": "the north block, the apartments turned 45 degrees to the wings, standing free over the valley on three sides"})
add("north block substructure", {"type": "enclosure", "plan": {"points": P2(NB)}, "thickness": 1.7, "height": SUBD, "glass": True,
                                 "tiers": plain_storeys([SUBD / 2, SUBD / 2]), "courses": {"plinth": 1.2, "strings": [], "cornice": False},
                                 "at": [[0, H0 - SUBD, 0, 0]], "_about": "its substructure down the slope to the rock"})
NBC = (sum(p[0] for p in NB) / 4, sum(p[1] for p in NB) / 4); NBA = math.atan2(-45.9 + 42.4, -8.2 + 25.7)
add("north block roof", {"type": "roof", "form": "hip", "width": 16.6, "length": 16.0, "pitch": 56, "overhang": OV,
                         "at": [[r4(NBC[0]), H0 + EAVE, r4(NBC[1]), r4(math.atan2(math.cos(NBA), math.sin(NBA)))]],
                         "_about": "its roof, steeper, hipped all round"})
FN = [Frame(NB[(i + 1) % 4], NB[i]) for i in range(4)] if area(NB) > 0 else [Frame(NB[i], NB[(i + 1) % 4]) for i in range(4)]   # (outside on the right)
LINK = [W(-36.0, 6.0), W(-19.5, 6.0), W(-19.5, 15.0), W(-21.5, 17.1), W(-36.0, 6.9)]
add("link", {"type": "prism", "plan": {"points": P2(outside_right(LINK))}, "height": EAVE + 0.4 + SUBD, "flatRoof": True, "at": [[0, H0 - SUBD, 0, 0]],
             "_about": "the mass where the north block meets the west and Elbe wings, under the roofs' valley, down to the rock"})

# ---- the Elbe tower: the one block of the river front carried up over the eave as a real tower, from the rock
ET = W(11.3, 14.2)
add("elbe tower", {"type": "enclosure", "plan": {"rect": [5.6, 5.6]}, "thickness": 0.9, "height": SUBD + EAVE + 7.0, "glass": True,
                   "tiers": [{"h": SUBD, "openings": curtain_window(0.9, 6.0, 7.4, rise=0.26, pattern="1", surround=False)},
                             {"h": G, "openings": curtain_window(1.15, 1.3, 3.0, rise=0.34, pattern="1", surround=False)},
                             {"h": F1, "openings": curtain_window(1.7, 1.0, 4.4, rise=0.48, pattern="1", surround=False)},
                             {"h": F2, "openings": curtain_window(1.7, 1.0, 4.2, rise=0.48, pattern="1", surround=False)},
                             {"openings": curtain_window(1.4, 1.2, 4.6, rise=0.4, pattern="1", surround=False)}],
                   "courses": {"plinth": 1.2, "strings": [SUBD, SUBD + G, SUBD + EAVE], "cornice": 0.4}, "at": [[r4(ET[0]), H0 - SUBD, r4(ET[1]), r4(YAW_U)]],
                   "_about": "the Elbe front's tower: the projecting block in its middle carried a storey over the eave, from the rock"})
add("elbe tower roof", {"type": "dome", "sides": 8, "radius": 3.0, "thickness": 0, "head": {"profile": "trigonal", "rise": 19.0},
                        "at": [[r4(ET[0]), H0 + EAVE + 7.0, r4(ET[1]), r4(YAW_U + math.pi / 8)]], "_about": "its slender slate needle"})
add("elbe tower finial", {"type": "column", "radius": 0.1, "height": 1.8, "sides": 6, "at": [[r4(ET[0]), H0 + EAVE + 7.0 + 19.0 - 0.2, r4(ET[1]), 0]]})

# ---------------------------------------------------------------- the lucarnes on the eave (components/lucarne)
LUC = {"W": 4.4, "D": 6.0, "H": 5.4, "GH": 3.6}
def lucs(name, f, pts):
    return lucarne_row(add, name, f, [along(f, p) for p in pts], H0 + EAVE, LUC)
lucs("lucarnes river north", B3[1], [W(-16.0, 15), W(-8.0, 15)])
lucs("lucarnes river middle", B4[1], [W(1.5, 9)])
lucs("lucarnes river south", B5[1], [W(18.0, 14), W(23.0, 14)])
lucs("lucarnes court", B3[3], [W(-9.5, -9), W(-5.5, -9)])
lucs("lucarnes court west", BW[0], [W(-17.5, -14.5)])
lucs("lucarnes west wing", BW[2], [W(-38.5, -14.0), W(-38.5, -6.0), W(-38.5, 2.0)])
lucs("lucarnes west end", BW[3], [W(-33.0, -19.5), W(-24.0, -19.5)])
lucs("lucarnes projection", B6[3], [W(6.75, -16.5)])
lucs("lucarnes south wing", B7[3], [S(6.0, 0), S(13.0, 0), S(20.0, 0)])
lucs("lucarnes north block", FN[0], [FN[0].at(-4.2), FN[0].at(4.2)])
lucs("lucarnes north block east", FN[1], [FN[1].at(-4.0), FN[1].at(4.0)])
lucs("lucarnes north block west", FN[3], [FN[3].at(-3.2), FN[3].at(3.2)])

# ---------------------------------------------------------------- the stair towers (components/wendelstein)
# the Grosser Wendelstein before the projection's end on the court (OSM's polygonal jut there), its back in the wall;
# the small one on the Elbe wing's court front by the west wing (OSM's rounded jut there)
WEND = {"R": 4.0, "t": 0.45, "H": EAVE, "footH": 3.8, "stageH": 4.0, "capRise": 14.0, "gableH": 3.0, "finial": 1.6, "turns": 4}
aW = WEND["R"] * math.cos(math.pi / 8)
add("grosser wendelstein", comp("components/wendelstein", WEND, [B6[2].place(0.0, aW - WEND["t"], H0)],
                                _about="the GROSSER WENDELSTEIN: the open stair tower at the corner of the projection on the court -- the open arcade at its foot, three storeys of great pointed arches over balustrade bands, the loggia, gables and pinnacles round the slate needle"))
SMALL = {"R": 2.6, "t": 0.4, "H": EAVE, "footH": 3.2, "stageH": 3.0, "capRise": 9.0, "gableH": 2.0, "finial": 1.2, "eye": 0.35,
         "pier": 0.3, "pinW": 0.28, "pinS": 1.0, "turns": 4}
aS = SMALL["R"] * math.cos(math.pi / 8)
add("small wendelstein", comp("components/wendelstein", SMALL, [B3[3].place(along(B3[3], W(-15.0, -9)), aS - SMALL["t"], H0)],
                              _about="the small stair tower on the court, in the corner of the west wing and the Elbe wing: the same tower, narrower"))

# ---------------------------------------------------------------- MEISSEN CATHEDRAL
CATH0 = len(build)
CA = math.radians(-18.1); CE = (math.cos(CA), math.sin(CA)); CN = (-math.sin(CA), math.cos(CA))   # along (east), across (south)
C0 = (-3.9 - CN[0], 43.2 - CN[1])               # the axis, a metre north of OSM's centroid: the nave symmetric on it
def C(u, v): return (C0[0] + u * CE[0] + v * CN[0], C0[1] + u * CE[1] + v * CN[1])
CYAW_W = math.atan2(-CE[0], -CE[1])             # a part's +z toward the west front
CYAW_E = math.atan2(CE[0], CE[1])
def cat(u, v, y=0.0, yaw=None): x, z = C(u, v); return [r4(x), r4(H0 + y), r4(z), r4(CYAW_W if yaw is None else yaw)]

BAYS, U0, U1 = 7, -22.0, 12.0                    # the hall: from the towers to the transept
BAY = (U1 - U0) / BAYS
NW, AW, T, TA, SPR, CP = 9.0, 5.4, 1.2, 1.2, 11.7, 58
OUT = NW / 2 + AW + TA / 2
add("cathedral nave", {"type": "basilica", "hall": True, "bays": BAYS, "bayLen": r4(BAY), "naveW": NW, "aisleW": AW, "t": T, "aisleT": TA, "apse": 0,
                       "spring": SPR, "aisleDrop": 0.6, "pierR": 0.75, "shaft": 0.22, "pitch": CP, "overhang": 0.5, "aisleSill": 4.0, "aisleWin": 2.6,
                       "buttressW": 1.3, "buttressD": 2.2, "flyers": False, "wimpergs": False, "tracery": False,
                       "pinnacleKinds": [{"h": 1.6, "s": 2.8, "gablets": 0.4, "crockets": 2}],
                       "at": [cat((U0 + U1) / 2, 0)],
                       "_about": "the seven-bay HALL nave (c. 1410): nave and aisles vaulted at one height on slender piers, tall traceried windows between buttresses, one steep roof over all"})
WALLTOP = SPR + (NW / 2 - T / 2) * 1.7321 * 0.9 + 0.8          # (gothic.js basilicaLevels, as the Stephansdom's)
# the transept: short arms, a gable at each end; the crossing under its own roof across the nave's
TR_U0, TR_U1, TR_V = 11.0, 22.0, 15.2
win_lancet = lambda w, sill, spring, tr=True: {"at": 0, "width": w, "sill": sill, "springing": spring, "head": {"profile": "pointed", "spread": 1.0}, "tracery": tr}
add("cathedral transept", {"type": "enclosure", "plan": {"rect": [2 * TR_V, TR_U1 - TR_U0]}, "thickness": 1.3, "height": r4(WALLTOP), "glass": True,
                           "faces": {"0": [], "2": [], "1": [{"openings": [win_lancet(3.6, 5.0, 13.0)]}], "3": [{"openings": [win_lancet(3.6, 5.0, 13.0)]}]},
                           "at": [cat((TR_U0 + TR_U1) / 2, 0, 0, CYAW_W)], "_about": "the transept, its arms short, a great window in each end"})
add("cathedral transept roof", {"type": "roof", "form": "gable", "width": TR_U1 - TR_U0 + 0.2, "length": 2 * TR_V + 0.4, "pitch": CP, "overhang": 0.4,
                                "at": [[*cat((TR_U0 + TR_U1) / 2, 0, WALLTOP)[:3], r4(CYAW_W + math.pi / 2)]], "_about": "the transept's roof, its ridge across the nave's"})
# the choir: long, one vessel, closed in a polygon; its west end inside the transept
CH_U0, CH_U1, CH_W = 17.0, 48.5, 12.8
add("cathedral choir", {"type": "enclosure", "plan": {"rect": [CH_W, CH_U1 - CH_U0], "chamfer": 3.8}, "thickness": 1.2, "height": r4(WALLTOP - 0.8), "glass": True,
                        "openings": {"every": 4.4, "end": 0.6, **win_lancet(2.4, 4.5, 13.2)},
                        "at": [cat((CH_U0 + CH_U1) / 2, 0, 0, CYAW_W)], "_about": "the long choir (1250-1270), one vessel of tall traceried windows, closed in three sides"})
add("cathedral choir roof", {"type": "roof", "form": "hip", "width": CH_W, "length": CH_U1 - CH_U0, "chamfer": 3.8, "pitch": CP, "overhang": 0.4,
                             "at": [cat((CH_U0 + CH_U1) / 2, 0, WALLTOP - 0.8, CYAW_W)], "_about": "the choir's roof, hipped round its polygon"})
add("cathedral choir buttresses", {"type": "box", "width": 1.2, "length": 1.8, "height": r4(WALLTOP - 2.5),
                                   "at": [[*cat(u, s * (CH_W / 2 + 0.9), 0)[:3], r4(CYAW_W)] for u in (26.0, 30.4, 34.8, 39.2) for s in (-1, 1)],
                                   "_about": "the choir's buttresses down its straight flanks"})
# the Hoeckriger Turm, in the angle of the south transept and the choir
HT = (25.0, 10.3)
add("hoeckriger turm", {"type": "enclosure", "plan": {"rect": [5.4, 5.4]}, "thickness": 1.0, "height": 30.0, "glass": True,
                        "tiers": [{"h": 20.0, "openings": []}, {"openings": {"pattern": "1", **win_lancet(1.5, 2.0, 7.0, False)}}],
                        "courses": {"strings": [20.0], "cornice": 0.4},
                        "at": [cat(*HT, 0, CYAW_W)], "_about": "the Hoeckriger Turm, the cathedral's one spire for centuries: its square shaft..."})
add("hoeckriger turm octagon", comp("components/gothic-octagon-stage", {"R": 2.85, "H": 7.0, "t": 0.5, "low": 1.2, "lights": 0},
                                    [cat(*HT, 30.0, CYAW_W)], build=["walls"], _about="...its octagon, a lancet in every face..."))
add("hoeckriger turm spire", {"type": "dome", "sides": 8, "radius": 2.85, "thickness": 0, "head": {"profile": "trigonal", "rise": 16.0},
                              "at": [cat(*HT, 37.0, CYAW_W + math.pi / 8)], "_about": "...and its straight stone spire"})
add("hoeckriger turm finial", {"type": "column", "radius": 0.12, "height": 1.8, "sides": 6, "at": [cat(*HT, 52.8, 0)]})
# the west towers: three square stages to 46 m, the octagon (1903-09) to 62 m, its tall open lancets, the stone spire to 81 m
TW_U0, TW_U1, TW_V = -33.0, -22.0, 9.0
TWW, TWD = 9.4, TW_U1 - TW_U0
TU = (TW_U0 + TW_U1) / 2
SQ, OCT, SPIRE = 46.0, 16.0, 19.0
for s_, nm in ((-1, "north"), (1, "south")):
    add(f"{nm} tower", {"type": "enclosure", "plan": {"rect": [TWW, TWD]}, "thickness": 1.6, "height": SQ, "glass": True,
                        "tiers": [{"h": 18.0, "openings": []}, {"h": 14.0, "openings": {"pattern": "1", **win_lancet(2.2, 3.0, 10.0, False)}},
                                  {"openings": {"pattern": "2", "gap": 1.2, **win_lancet(1.6, 2.0, 10.0, False)}}],
                        "courses": {"strings": [18.0, 32.0], "cornice": 0.5},
                        "at": [cat(TU, s_ * TW_V, 0, CYAW_W)], "_about": f"the {nm} west tower: its three square stages (the third Arnold von Westfalen's), to 46 m"})
TOW = [cat(TU, s_ * TW_V, SQ, CYAW_W) for s_ in (-1, 1)]
add("west tower octagons", comp("components/gothic-octagon-stage", {"R": 5.0, "H": OCT, "t": 0.8, "low": 2.0, "lights": 0, "winW": "R * 0.46"},
                                TOW, build=["walls"], _about="the octagon on each tower (1903-09), a tall open lancet in every face"))
SPF = [cat(TU, s_ * TW_V, SQ + OCT, CYAW_W) for s_ in (-1, 1)]
add("west spires", comp("components/gothic-spire", {"R": 4.8, "rise": SPIRE, "topR": 0.4, "pinR": 5.15, "pinW": 0.8, "pinH": 2.4, "pinS": 4.0, "gPitch": 66},
                        SPF, _about="the stone spires (1903-09), crocketed ribs on their edges, a gable on every face and pinnacles round their feet: 81 m"))
add("west tower pinnacles", comp("components/pinnacle", {"w": 1.4, "h": 3.4, "s": 5.0},
                                 [cat(TU + cu * (TWD / 2 - 0.9), s_ * TW_V + cv * (TWW / 2 - 0.9), SQ, CYAW_W) for s_ in (-1, 1) for cu in (-1, 1) for cv in (-1, 1)],
                                 _about="a pinnacle on each corner of the square towers' heads"))
# between the towers: the west front, two great windows over each other, its gable between the octagons
FW = 2 * TW_V - TWW
WFH = 40.0
add("west front", {"type": "wall", "width": r4(FW + 0.2), "height": WFH, "thickness": 1.6,
                   "tiers": [{"h": 8.0, "openings": []}, {"h": 15.0, "openings": [win_lancet(4.6, 1.5, 9.0)]}, {"openings": [win_lancet(4.6, 1.5, 9.5)]}],
                   "courses": {"strings": [8.0, 23.0], "cornice": 0.5},
                   "at": [cat(TW_U0 + 1.2, 0, 0, CYAW_W)], "_about": "the west front between the towers, two great windows over each other"})
add("west front middle", {"type": "box", "width": r4(FW + 0.2), "length": 7.9, "height": WFH, "at": [cat(-26.55, 0, 0, CYAW_W)],
                          "_about": "the mass between the towers"})
add("west gable", {"type": "screen", "outline": [[r4(-FW / 2 - 0.1), 0], [r4(FW / 2 + 0.1), 0], [0, 8.0]], "t": 1.2,
                   "at": [cat(TW_U0 + 1.2, 0, WFH, CYAW_W)], "_about": "the west gable between the octagons"})
# the Fuerstenkapelle before the west front (1415-46), the princes' burial chapel
FK_U0, FK_U1, FK_W, FK_C = -48.0, -33.0, 10.4, 3.0
ROSE = {"at": 0, "width": 2.6, "sill": 3.0, "springing": 3.0, "head": {"profile": "semicircular"}, "foot": {"profile": "semicircular"}}
add("fuerstenkapelle", {"type": "enclosure", "plan": {"rect": [FK_W, FK_U1 - FK_U0], "chamfer": FK_C}, "thickness": 1.1, "height": 13.0, "glass": True,
                        "openings": {"every": 4.2, "end": 1.2, **win_lancet(2.2, 4.0, 10.0, False)},
                        "faces": {"2": [{"h": 6.4, "openings": [{"at": 0, "width": 2.6, "sill": 0, "springing": 3.4, "head": {"profile": "pointed", "spread": 1.0}, "glass": False}]},
                                        {"openings": [ROSE]}], "6": [], "chamfer": [{"openings": [win_lancet(1.6, 4.0, 10.0, False)]}]},
                        "at": [cat((FK_U0 + FK_U1) / 2, 0, 0, CYAW_W)],
                        "_about": "the Fuerstenkapelle, the princes' chapel before the west front, its polygonal end with the portal (now the cathedral's door) and a rose over it"})
add("fuerstenkapelle roof", {"type": "roof", "form": "hip", "width": FK_W, "length": FK_U1 - FK_U0, "chamfer": FK_C, "pitch": 55, "overhang": 0.4,
                             "at": [cat((FK_U0 + FK_U1) / 2, 0, 13.0, CYAW_W)], "_about": "its roof, hipped round the polygon"})

CATH = build[CATH0:]
# ---------------------------------------------------------------- the hill: rock to the terrace walls, the plateau
# The plateau's Elbe edge is the castle itself: the edge runs a metre inside the river wings' and the north block's
# walls, which go down SUB to the rock (their substructures). Elsewhere the terrace walls stand on the rock: SUB high
# where the rock falls to the Elbe, lower (UPPER_WALL) on the town's and the cathedral's sides, where the rock comes up
# higher under them (`upper rock`). The rock itself is battered out wide toward the river.
def toward(p, c, d): L = math.dist(p, c); return (p[0] + (c[0] - p[0]) * d / L, p[1] + (c[1] - p[1]) * d / L)
NBI = [toward(q, NBC, 1.0) for q in NB]
PLATEAU = outside_right([NBI[2], NBI[1], NBI[0], (-28.5, -32), (-31.5, -26), (-47, -14), (-62, 2), (-70, 14), (-72, 40), (-66, 72), (-20, 76),
                         (30, 70), (52, 50), (52, 26), (44, 16), (36, 8.5), W(26.0, 13.0), W(7.5, 13.0), W(7.5, 8.0), W(-4.0, 8.0),
                         W(-4.0, 14.0), W(-19.5, 14.0)])
UPPER_WALL = 4.0
UPPER = outside_right([(-28.5, -32), (-31.5, -26), (-47, -14), (-62, 2), (-70, 14), (-72, 40), (-66, 72), (-20, 76), (30, 70), (52, 50),
                       (52, 26), (44, 16), (20, 28), (-20, 12), (-24, -22)])
add("burgberg", {"type": "prism", "plan": {"points": P2(PLATEAU)}, "height": H0 - SUB, "batter": {"out": 30.0, "power": 1.4},
                 "at": [[0, 0, 0, 0]], "_about": "the Burgberg, the rock spur falling to the Elbe and the Triebisch: battered out wide under the walls"})
add("upper rock", {"type": "prism", "plan": {"points": P2(UPPER)}, "height": SUB - UPPER_WALL + 1.0, "batter": {"out": 7.0, "power": 1.3},
                   "at": [[0, H0 - SUB - 1.0, 0, 0]], "_about": "the rock higher under the town's and the cathedral's sides, the walls there lower"})
add("terrace walls", {"type": "prism", "plan": {"points": P2(PLATEAU)}, "height": SUB, "at": [[0, H0 - SUB, 0, 0]],
                      "_about": "the walls round the plateau's edge, rubble on the rock; the plateau over them"})
# the way up from the town: where the rock comes up under the west terrace wall, a flight laid along the wall's foot from a
# masonry forecourt on the rock to the Domplatz's edge (the rest of the way, the Burgstrasse up the slope, is the town's)
WD = (-72.0 + 70.0, 40.0 - 14.0); WL = math.hypot(*WD); WD = (WD[0] / WL, WD[1] / WL); WN = (-WD[1], WD[0])   # (the wall's line, its outward normal)
def wall_at(t, off): return (-70.0 + WD[0] * t + WN[0] * off, 14.0 + WD[1] * t + WN[1] * off)
FYAW = math.atan2(-WD[0], -WD[1]) - math.pi / 2          # (its +x up the wall toward the north, its -z out from the wall)
NST = round(UPPER_WALL / 0.18); FOOT_T = 4.0 + NST * 0.32 + 2.5
F0 = wall_at(FOOT_T, 0.05)
add("burg stair", {"type": "flight", "width": 3.0, "run": 0.32, "rise": 0.18, "base": H0 - UPPER_WALL, "top": H0, "landing": 2.5, "ground": H0 - UPPER_WALL - 6.0,
                   "at": [[r4(F0[0]), 0, r4(F0[1]), r4(FYAW)]], "_about": "the way up: a flight along the west terrace wall's foot to the Domplatz"})
FC = wall_at(FOOT_T + 2.0, 1.55)
add("burg stair forecourt", {"type": "box", "width": 4.0, "length": 3.2, "height": 8.0, "at": [[r4(FC[0]), H0 - UPPER_WALL - 8.0, r4(FC[1]), r4(FYAW)]],
                             "_about": "the masonry forecourt on the rock at the stair's foot"})

# ---------------------------------------------------------------- the components, the building, the finish
write_components()
HILL = ["burgberg", "upper rock", "terrace walls", "burg stair forecourt", "burg stair"]
build = HILL + [n for n in build if n not in HILL]           # (the hill first: everything stands on it)
doc = {"name": "Albrechtsburg",
       "_about": ("THE ALBRECHTSBURG with MEISSEN CATHEDRAL on the Burgberg over the Elbe (x east, z south, from OSM). The castle (1471-1524, "
                  "Arnold von Westfalen): walls on its real hook-shaped plan, a low ground floor and two high main floors of CURTAIN-ARCH windows, "
                  "steep tiled roofs, the ring of LUCARNES on the eave (`lucarne`), the Elbe front's tower, and on the court the GROSSER "
                  "WENDELSTEIN, the open stair tower whose windows climb with its stair (`wendelstein`), and a smaller one. The cathedral: "
                  "the seven-bay hall nave, the short transept, the long choir, the Hoeckriger Turm, the west towers with their 1903-09 "
                  "octagons and openwork spires to 81 m, the Fuerstenkapelle; all on the plateau over the rock and its terrace walls."),
       "params": {"detail": 2}, "railing": {"type": "stone"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/albrechtsburg.json"), "w").write(json.dumps(doc, indent=2) + "\n")

# ---------------------------------------------------------------- the finish
reg = json.load(open(os.path.join(ROOT, "assets/finishes/regensburg.json")))
CATH_ALL = [m for n in CATH for m in (n, n + " courses", n + " tracery", n + " surrounds", n + " rake")]
CATH_GLASS = ["cathedral nave/glass"] + [n + " glass" for n in CATH]
CATH_ROOFS = ["cathedral nave/high roof", "cathedral transept roof", "cathedral choir roof", "fuerstenkapelle roof"]
DARK = [m for n in ["north tower", "south tower", "west tower octagons", "west spires", "west tower pinnacles", "west front", "west front middle",
                    "west gable", "hoeckriger turm", "hoeckriger turm octagon", "hoeckriger turm spire", "hoeckriger turm finial"]
        for m in (n, n + " courses", n + " tracery")]
WEND_ = ["grosser wendelstein", "small wendelstein"]
STAIRS = ["burg stair", "burg stair forecourt"]
rules = [{**r, "parts": CATH_GLASS} for r in reg["rules"] if r.get("parts") == "kind:glass"] + [   # (Regensburg's glass, held to the cathedral's windows)
  {"parts": "kind:glass", "pattern": "glass/quarries", "_about": "the castle's windows: plain diamond quarries in lead"},
  {"parts": CATH_ROOFS, "surface": "roof", "pattern": "roofs/fish scale", "palette": "tile-brown", "_about": "the cathedral's roofs: brown plain tile, older and darker than the castle's"},
  {"parts": CATH_ALL, "surface": "wall", "side": "in", "pattern": "stone/ashlar", "palette": "sandstone-grey", "_about": "inside the cathedral: the light sandstone"},
  {"parts": CATH_ALL, "surface": "floor", "pattern": "floors/flagstones", "palette": "sandstone-grey"},
  {"parts": DARK, "pattern": "stone/ashlar", "palette": "meissen-dark", "_about": "the towers, the west front and the spires: the Elbe sandstone weathered almost black"},
  {"parts": CATH_ALL, "pattern": "stone/ashlar", "palette": "meissen-sandstone", "_about": "the rest of the cathedral outside: Elbe sandstone, weathered brown-grey"},
  {"parts": [w + "/cap" for w in WEND_] + ["elbe tower roof"], "surface": "roof", "pattern": "roofs/slate", "palette": "slate", "_about": "the needles of the stair towers and the Elbe tower: slate"},
  {"parts": "kind:roof", "surface": "roof", "pattern": "roofs/fish scale", "palette": "tile-saxon", "_about": "the castle's steep roofs and its lucarnes': bright orange-red beaver-tail tile"},
  {"parts": WEND_ + STAIRS, "surface": "floor", "pattern": "floors/flagstones", "palette": "sandstone-grey", "_about": "the Wendelsteins' treads; the stair from the town"},
  {"parts": WEND_ + ["elbe tower finial", "pinnacles"], "pattern": "stone/ashlar fine", "palette": "sandstone-grey", "_about": "the Wendelsteins in dressed sandstone, the stair's cage bare; the lucarnes' pinnacles"},
  {"parts": ["terrace walls"] + STAIRS, "surface": "wall", "pattern": "stone/rubble long", "palette": "acropolis-rock", "_about": "the terrace walls round the Burgberg and the stair's masonry: rubble"},
  {"parts": ["burgberg", "upper rock"], "pattern": "stone/rock face", "palette": "earth", "_about": "the rock spur itself"},
  {"surface": "floor", "side": "in", "pattern": "floors/flagstones", "palette": "sandstone-grey"},
  {"surface": "floor", "pattern": "floors/flagstones", "palette": "sandstone", "_about": "the court and the Domplatz: sandstone setts"},
  {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white", "_about": "the castle's rooms: whitewashed"},
  {"pattern": "stone/plaster", "palette": "plaster-white", "_about": "the castle: white lime plaster over the stone, its courses too"}]
fin = {"name": "Albrechtsburg", "building": "architecture/albrechtsburg",
       "_about": ("The Albrechtsburg and Meissen Cathedral (written by tools/archgen/albrechtsburg.py): the castle in white lime plaster under bright "
                  "orange-red beaver-tail tile (palette tile-saxon), its Wendelsteins in bare sandstone under slate helms; the cathedral in weathered "
                  "brown-grey Elbe sandstone (palette meissen-sandstone), its towers, west front and spires near black (meissen-dark), brown tile and Regensburg's stained glass; "
                  "the Burgberg's rock and rubble terrace walls, sandstone setts on the plateau; the castle's windows in leaded quarries."),
       "stone": {"color": "#ece6da", "accent": "#d8d0c0", "pat": "ashlar"}, "rules": rules}
open(os.path.join(ROOT, "assets/finishes/albrechtsburg.json"), "w").write(json.dumps(fin, indent=2) + "\n")
print("parts", len(parts), "rules", len(rules))
