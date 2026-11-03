# THE CATHEDRAL-BASILICA OF OUR LADY OF THE PILLAR (El Pilar), Zaragoza (Felipe Sánchez and Francisco Herrera the
# Younger from 1681, Ventura Rodríguez 1750-66, the domes finished 1872, the towers 1907-61), rebuilt 2026-11-03 from
# OpenStreetMap and the published plans:
#   * the FOOTPRINT is OSM's building relation 1352311: a rectangle 131.3 x 69.3 m along the Ebro (its long axis on a
#     bearing of 119.6 degrees), and OSM's eleven `building:part`s (ways 421912392 ... 421912515) are the lanterns of the
#     eleven domes, each 5 m square: the great one at the middle (51-67 m), two middling ones on the middle nave's axis
#     33.4 m either side of it (39.1-51.7 m) and eight small ones over the side naves, 17.7 and 49.7 m out and 19 m off
#     the axis (34.1-46.7 m);
#   * the PLAN is the engraving "Planta de la Catedral de Nuestra Sra del Pilar de Zaragoza" (Manuel Navarro, Biblioteca
#     Nacional, on Wikimedia Commons) measured over the OSM rectangle, and Ventura Rodríguez's 1754 plan of the Santa
#     Capilla (Commons "Planta de la Santa Capilla del Pilar"): a HALL CHURCH of three naves of one height, seven bays on
#     two rows of cruciform piers (at 9.25, 25.6 and 41.2 m from the middle, 10.4 m off the axis), side chapels between
#     buttress walls along both flanks, three chapels across each end, and the four square towers in the corners;
#   * es.wikipedia "Catedral-basílica de Nuestra Señora del Pilar" for the rest: the Santa Capilla in the second bay
#     from the east under the middling dome, Damián Forment's alabaster retablo mayor (1512-18) under the great dome,
#     the coro in the middle nave's second bay from the west (its stalls in three tiers, the organ of 1529, Celma's
#     grille), the coreto at the east end (its organ, Goya's fresco on its vault), Goya's and the Bayeus' painted
#     cupolas, the plaza front of Teodoro Ríos (1940s) with its three portals and Pablo Serrano's relief.
# Frame: +x is the long axis toward the east-south-east (the Santa Capilla's end), +z toward the Plaza del Pilar
# (south-south-west), -z the Ebro, y up. Numbers are worked here and written as numbers.
#
# What is built: the hall of seven bays -- cruciform piers, arches pier to pier, PENDENTIVES under the eleven domes and
# SAIL VAULTS (the "bóvedas de plato", stretched to their oblong bays) everywhere else; the eleven `drum-dome`s on their
# cornice rings, octagonal, tiled, each with its lantern -- the great one on a tall drum of eight windows between
# buttresses with paired columns, its ribbed dome and lantern; hipped tile roofs over the vaulted bays, lean-to roofs
# over the chapels, clerestory windows over them; the brick walls round the rectangle in two storeys of windows in
# stone surrounds, a giant Corinthian order on the plaza front, its three portals (two pedimented porticoes and the
# great arched niche of the middle one with its relief), a balustrade with statues round the roof; the FOUR TOWERS
# (~89 m): brick shaft, clock stage, an arched stage, the belfry, the balustrade with urns, the copper `baroque-helm`
# of two lanterns -- the north-west one (the Torre de San Francisco de Borja, entered from the Paseo Echegaray y
# Caballero on the river side) climbed by a `tower-stair` and a LIFT to its glazed MIRADOR; inside, the Santa Capilla
# (an oval of twelve Corinthian columns, its entablature and the oval dome open in an oculus to the dome over it, the
# Virgin's jasper pillar and her image, the altar of the Venida), the retablo mayor with its three niches, predella and
# pinnacles, the coro (walls, stalls in tiers, the organ on its loft, the grille), the coreto (stalls, the organ over
# the east door), pews, altars, marble floors; the finish at the end (glazed tile domes in patterns, warm brick, pale
# stone, white and gilt stucco inside, painted cupolas, marble).
import os, json, math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from neoclassical import Balusters
import statuary as ST

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q, PI = math.pi / 2, math.pi
r3 = lambda v: round(v, 3)
arch = lambda at, w, sill, spr, **kw: {"at": r3(at), "width": r3(w), "sill": r3(sill), "springing": r3(spr), "head": {"profile": "semicircular"}, **kw}

# ---- the plan --------------------------------------------------------------------------------------------------------
X0, Z0, T = 65.6, 34.65, 1.6               # the outer walls' outer faces (half), their thickness
XI, ZI = X0 - T, Z0 - T                    # their inner faces: 64.0, 33.05
PX, PZ = [9.25, 25.6, 41.2], 10.4          # the piers' middles: along x either side, and off the axis
PW, PD = 4.0, 3.7                          # a pier: along x, across z (cruciform, measured off the engraving)
CZ = PZ - PD / 2                           # the middle nave's clear half-width: 8.55
SZ0, SZ1 = PZ + PD / 2, 26.5               # a side nave: from the piers' faces to the chapels' arcade wall
SZC, SS = (SZ0 + SZ1) / 2, SZ1 - SZ0       # its middle (19.375) and span (14.25)
AWT = 1.2                                  # the arcade wall between a side nave and its chapels
CH0 = SZ1 + AWT                            # the chapels from 27.7 to the outer wall's inside
EA0, EA1 = 55.0, 57.0                      # the end arcade walls (between the naves and the end chapels)
TW = 10.6                                  # the towers: square, in the corners of the rectangle
TX, TZ = X0 - TW / 2, Z0 - TW / 2          # a tower's middle: 60.3, 29.35
RH = 21.0                                  # the crown of every arch and the pendentives' ring
TOP = 21.35                                # the arches' and piers' tops (a hair under the decks' 21.4)
DECK = 0.4
WH = 16.0                                  # the outer walls' top (OSM: eaves 16, the roofs to 26)
CCR = 13.5                                 # the chapels' vault crowns
DIV = 3.0                                  # the buttress walls between the chapels

# the bays along x: their middles and clear spans between the piers' faces (the end bays to the end arcade wall)
edges = [-EA0, -PX[2] - PW / 2, -PX[2] + PW / 2, -PX[1] - PW / 2, -PX[1] + PW / 2, -PX[0] - PW / 2, -PX[0] + PW / 2,
         PX[0] - PW / 2, PX[0] + PW / 2, PX[1] - PW / 2, PX[1] + PW / 2, PX[2] - PW / 2, PX[2] + PW / 2, EA0]
BAYS = [((edges[2 * i] + edges[2 * i + 1]) / 2, edges[2 * i + 1] - edges[2 * i]) for i in range(7)]   # (x middle, clear span)
# the chapels between the buttress walls: their middles and spans
cedges = [-EA0, -PX[2] - DIV / 2, -PX[2] + DIV / 2, -PX[1] - DIV / 2, -PX[1] + DIV / 2, -PX[0] - DIV / 2, -PX[0] + DIV / 2,
          PX[0] - DIV / 2, PX[0] + DIV / 2, PX[1] - DIV / 2, PX[1] + DIV / 2, PX[2] - DIV / 2, PX[2] + DIV / 2, EA0]
CHAP = [((cedges[2 * i] + cedges[2 * i + 1]) / 2, cedges[2 * i + 1] - cedges[2 * i]) for i in range(7)]
BX = [b[0] for b in BAYS]                  # -49.1, -33.4, -17.425, 0, 17.425, 33.4, 49.1
LINES = sorted([-x for x in PX] + PX)      # the pier lines
SMALL = [(BX[i], s * SZC) for i in (0, 2, 4, 6) for s in (-1, 1)]   # the eight small domes over the side naves
MED = [(BX[1], 0.0), (BX[5], 0.0)]                                    # the two middling ones
# the bays without a dome: sail vaults ("bóvedas de plato")
NAVE_SAIL = [0, 2, 4, 6]                   # middle-nave bays (indices into BAYS)
AISLE_SAIL = [1, 3, 5]                     # side-nave bays


def barrel_x(x0, x1, zc, width, spr, top=TOP):
    """a barrel (an arch) running along x from x0 to x1, its arch spanning `width` across z round zc"""
    return {"type": "barrel", "width": r3(width), "length": r3(x1 - x0), "springing": r3(spr), "top": r3(top), "head": {"profile": "semicircular"},
            "at": [[r3(x1), 0, r3(zc), Q]]}


def barrel_z(z0, z1, xc, width, spr, top=TOP):
    """a barrel running along z from z0 to z1, its arch spanning `width` across x round xc"""
    return {"type": "barrel", "width": r3(width), "length": r3(z1 - z0), "springing": r3(spr), "top": r3(top), "head": {"profile": "semicircular"},
            "at": [[r3(xc), 0, r3(z1), 0]]}


def merge_at(defs):
    """one part from several of the same shape: their placements together"""
    out = dict(defs[0]); out["at"] = [a for d in defs for a in d["at"]]
    return out


# ---- the hall: piers, arches ------------------------------------------------------------------------------------------
PIERS = [[r3(sx * x), 0, r3(sz * PZ), 0] for x in PX for sx in (-1, 1) for sz in (-1, 1)]
add("piers", {"type": "box", "width": PW, "length": PD, "height": TOP, "at": PIERS,
              "_about": "the twelve piers of the hall, 4 x 3.7 m, up to the arches' tops (their arms below the imposts make them cruciform)"})
add("pier arms", {"type": "box", "width": r3(PW + 0.6), "length": 2.0, "height": 12.0, "at": PIERS,
                  "_about": "the piers' arms toward the naves: pilasters 30 cm proud, up to the impost"})
add("pier arms 2", {"type": "box", "width": 2.2, "length": r3(PD + 0.6), "height": 12.0, "at": PIERS})
add("pier bases", {"type": "box", "width": r3(PW + 0.9), "length": r3(PD + 0.9), "height": 0.6, "at": PIERS,
                   "_about": "the piers' marble bases"})
add("pier imposts", {"type": "box", "width": r3(PW + 0.9), "length": r3(PD + 0.9), "height": 0.45, "at": [[a[0], 12.0, a[2], 0] for a in PIERS],
                     "_about": "the gilt impost mouldings, under the lowest springing (12.45)"})
# the arches across the middle nave and the side naves, on the pier lines
add("nave arches", merge_at([barrel_x(x - PW / 2, x + PW / 2, 0, 2 * CZ, RH - CZ) for x in LINES]) | {
    "_about": "the arches across the middle nave from pier to pier, 4 m deep (the vaults' oblong ends are lost in them)"})
add("aisle arches", merge_at([barrel_x(x - PW / 2, x + PW / 2, s * SZC, SS, RH - SS / 2) for x in LINES for s in (-1, 1)]) | {
    "_about": "the arches across the side naves, from the piers to the arcade walls of the chapels"})
for i, (bx, span) in enumerate(BAYS):
    add(f"arcade arches {i + 1}", merge_at([barrel_z(s * PZ - PD / 2, s * PZ + PD / 2, bx, span, RH - span / 2) for s in (-1, 1)]) | (
        {"_about": "the arches along the naves, from pier to pier (and to the end walls), all crowned at 21 m: the hall's three naves are of one height"} if i == 0 else {}))

# ---- the vaults: pendentives under the domes, sail vaults over the other bays -------------------------------------------
DOMED = {}
for (x, z) in [(0.0, 0.0)] + MED:
    DOMED[(x, z)] = 2 * CZ
for (x, z) in SMALL:
    DOMED[(x, z)] = SS
add("great pendentives", {"type": "pendentives", "span": r3(2 * CZ), "springing": r3(RH - CZ), "sides": 8, "deck": {"thickness": DECK, "out": 0},
                          "at": [[0, 0, 0, 0]], "_about": "the pendentives under the great dome, and the deck round its drum's foot"})
add("middle pendentives", {"type": "pendentives", "span": r3(2 * CZ), "springing": r3(RH - CZ), "sides": 8, "deck": {"thickness": DECK, "out": 0},
                           "at": [[r3(x), 0, 0, 0] for x, _ in MED], "_about": "the pendentives under the two middling domes (the Santa Capilla's bay, the coro's)"})
add("small pendentives", {"type": "pendentives", "span": SS, "springing": r3(RH - SS / 2), "sides": 16, "deck": {"thickness": DECK, "out": 0},
                          "at": [[r3(x), 0, r3(z), 0] for x, z in SMALL], "_about": "the pendentives under the eight small domes over the side naves"})
SAILS = {}
for i in NAVE_SAIL:
    bx, span = BAYS[i]
    SAILS.setdefault(("nave", r3(span)), []).append((bx, 0.0))
for i in AISLE_SAIL:
    bx, span = BAYS[i]
    for s in (-1, 1): SAILS.setdefault(("aisle", r3(span)), []).append((bx, s * SZC))
SAIL_PARTS = []
for k, ((kind, span), pts) in enumerate(sorted(SAILS.items())):
    S = 2 * CZ if kind == "nave" else SS
    nm = f"{kind} vaults {k + 1}"
    SAIL_PARTS.append(nm)
    add(nm, {"type": "pendentives", "sail": True, "span": r3(S), "springing": r3(RH - S / 2), "sides": 16, "rows": 6,
             "stretch": [r3(span / S), 1, 1], "at": [[r3(x), 0, r3(z), 0] for x, z in pts],
             **({"_about": "the SAIL VAULTS ('bóvedas de plato') of the bays without a dome: the whole sphere over the bay, stretched to its oblong (the formerets' crowns at 21 m, the vault's at 24-25)"} if k == 0 else {})})
# their spaces up under the roofs (the hall's own space stops at the decks)
for k, ((kind, span), pts) in enumerate(sorted(SAILS.items())):
    w = 2 * CZ if kind == "nave" else SS
    add(f"{kind} vault space {k + 1}", {"type": "interior", "plan": {"rect": [r3(span), r3(w)]}, "height": 4.6,
                                        "at": [[r3(x), 21.4, r3(z), 0] for x, z in pts],
                                        **({"_about": "the sail vaults' spaces over the hall's: what is under them is inside"} if k == 0 else {})})

# ---- the walls: the outer rectangle between the towers, the arcade walls inside ---------------------------------------
WIN1 = lambda at: arch(at, 2.2, 3.0, 6.2, surround={"head": "cornice"})
WIN2 = lambda at: arch(at, 2.4, 1.2, 3.4, surround=True)
CH_X = [c[0] for c in CHAP]
south_doors = {0: (4.0, 5.8), 6: (3.2, 5.4), 3: (4.0, 5.8)}           # chapel index: (width, springing)
LOW = 8.4
def long_face(doors):
    t0 = [arch(x, w, 0, s, glass=False, surround={"head": "pediment" if i != 3 else "cornice"}) if i in doors else WIN1(x)
          for i, x in enumerate(CH_X) for (w, s) in [doors.get(i, (0, 0))]]
    return [{"h": LOW, "openings": t0}, {"openings": [WIN2(x) for x in CH_X]}]
add("south wall", {"type": "wall", "width": r3(2 * EA0), "thickness": T, "height": WH, "tiers": long_face({0: (3.2, 5.4), 3: (4.0, 5.8), 6: (3.2, 5.4)}),
                   "orders": [{"tier": 0, "kind": "corinthian", "span": 2}], "courses": True, "at": [[0, 0, Z0, 0]],
                   "_about": "the plaza front (Teodoro Ríos' of the 1940s): two storeys of windows in stone surrounds through a giant Corinthian order, the three portals"})
add("north wall", {"type": "wall", "width": r3(2 * EA0), "thickness": T, "height": WH, "tiers": long_face({3: (3.6, 5.6)}), "courses": True,
                   "at": [[0, 0, -Z0, PI]], "_about": "the river front over the Ebro: brick, two storeys of windows, the north door in the middle"})
ECH = (SZ0 + (Z0 - TW)) / 2                # the end chapels' middles off the axis (12.25 .. 24.05)
ECW = (Z0 - TW) - SZ0
end_face = [{"h": LOW, "openings": [arch(0, 3.6, 0, 5.6, glass=False, surround={"head": "pediment"})] + [WIN1(s * ECH) for s in (-1, 1)]},
            {"openings": [WIN2(0)] + [WIN2(s * 18.15) for s in (-1, 1)]}]
add("east wall", {"type": "wall", "width": r3(2 * (Z0 - TW)), "thickness": T, "height": WH, "tiers": end_face, "courses": True, "at": [[X0, 0, 0, Q]],
                  "_about": "the east front between the towers: the door of the Romanesque tympanum's portal, windows into the end chapels"})
add("west wall", {"type": "wall", "width": r3(2 * (Z0 - TW)), "thickness": T, "height": WH, "tiers": end_face, "courses": True, "at": [[-X0, 0, 0, -Q]],
                  "_about": "the west front between the towers"})
# the arcade walls: the chapels' mouths below, a clerestory window over the lean-to roofs in every bay
CLER = lambda at: arch(at, 2.0, 18.2 - 13.6, 19.4 - 13.6, surround={"head": False})
arc_face = [{"h": 13.6, "openings": [arch(x, w, 0, CCR - w / 2, glass=False) for (x, w) in CHAP]}, {"openings": [CLER(x) for x in BX]}]
for s, nm in ((1, "south"), (-1, "north")):
    add(f"{nm} arcade wall", {"type": "wall", "width": r3(2 * EA0), "thickness": AWT, "height": TOP, "tiers": arc_face,
                              "courses": {"plinth": False, "strings": False}, "at": [[0, 0, r3(s * CH0), 0 if s > 0 else PI]],
                              **({"_about": "the walls between the side naves and their chapels: an arch into each chapel, over the chapels' roofs a clerestory window in every bay"} if s > 0 else {})})
end_arc = [{"h": 13.6, "openings": [arch(0, 3.6, 0, 5.4, glass=False)] + [arch(s * ECH, ECW, 0, CCR - ECW / 2, glass=False) for s in (-1, 1)]},
           {"openings": [arch(0, 2.4, 18.0 - 13.6, 19.2 - 13.6, surround={"head": False})] + [CLER(s * SZC) for s in (-1, 1)]}]
for s, nm in ((1, "east"), (-1, "west")):
    add(f"{nm} arcade wall", {"type": "wall", "width": r3(2 * (Z0 - TW)), "thickness": EA1 - EA0, "height": TOP, "tiers": end_arc,
                              "courses": {"plinth": False, "strings": False}, "at": [[r3(s * EA1), 0, 0, Q if s > 0 else -Q]],
                              **({"_about": "the walls across the ends of the naves: a door into the end vestibule, an arch into each end chapel, clerestory windows over"} if s > 0 else {})})
# the chapels: the buttress walls between them and their barrel vaults
add("chapel walls", {"type": "box", "width": DIV, "length": r3(ZI - CH0), "height": r3(CCR + 0.4),
                     "at": [[r3(x), 0, r3(s * (CH0 + ZI) / 2), 0] for x in LINES for s in (-1, 1)],
                     "_about": "the buttress walls between the side chapels, on the pier lines"})
add("end chapel walls", {"type": "box", "width": r3(XI - EA1), "length": PD, "height": r3(CCR + 0.4),
                         "at": [[r3(s * (EA1 + XI) / 2), 0, r3(t * PZ), 0] for s in (-1, 1) for t in (-1, 1)],
                         "_about": "and between the end chapels"})
cv = {}
for (x, w) in CHAP:
    for s in (-1, 1): cv.setdefault(r3(w), []).append(barrel_z(*sorted((s * CH0, s * ZI)), x, w, CCR - w / 2, CCR + 0.4))
for k, (w, ds) in enumerate(sorted(cv.items())):
    add(f"chapel vaults {k + 1}", merge_at(ds) | ({"_about": "the side chapels' barrel vaults, crowned at 13.5 m"} if k == 0 else {}))
ev = [barrel_x(*sorted((s * EA1, s * XI)), t * ECH, ECW, CCR - ECW / 2, CCR + 0.4) for s in (-1, 1) for t in (-1, 1)]
add("end chapel vaults", merge_at(ev) | {"_about": "the end chapels' vaults"})
add("end vestibule vaults", merge_at([barrel_x(*sorted((s * EA1, s * XI)), 0, 2 * CZ, CCR - CZ, CCR + 0.4) for s in (-1, 1)]) | {
    "_about": "the vestibules behind the end doors"})

# ---- the spaces -------------------------------------------------------------------------------------------------------
add("hall", {"type": "interior", "plan": {"rect": [r3(2 * EA0), r3(2 * SZ1)]}, "height": 21.4, "at": [[0, 0, 0, 0]],
             "_about": "THE HALL: the three naves up to the decks (the vaults over it are their own spaces)"})
for s, nm in ((1, "south"), (-1, "north")):
    add(f"{nm} chapels", {"type": "interior", "plan": {"rect": [r3(2 * EA0), r3(ZI - CH0)]}, "height": r3(CCR + 0.3), "at": [[0, 0, r3(s * (CH0 + ZI) / 2), 0]],
                          **({"_about": "the side chapels' space, up to their vaults"} if s > 0 else {})})
    add(f"{nm} arcade", {"type": "interior", "plan": {"rect": [r3(2 * EA0), AWT]}, "height": r3(CCR + 0.3), "at": [[0, 0, r3(s * (SZ1 + AWT / 2)), 0]]})
for s, nm in ((1, "east"), (-1, "west")):
    add(f"{nm} end chapels", {"type": "interior", "plan": {"rect": [r3(XI - EA0), r3(2 * (Z0 - TW))]}, "height": r3(CCR + 0.3), "at": [[r3(s * (EA0 + XI) / 2), 0, 0, 0]]})

# ---- the eleven domes --------------------------------------------------------------------------------------------------
# a cornice ring at the pendentives' crown under each drum (gilt inside), the drums standing on it
add("dome rings", {"type": "ring", "count": 16, "rOuter": r3(CZ + 0.05), "rInner": r3(CZ - 0.4), "height": 0.4, "y": RH, "turn": 0.5, "solid": True,
                   "place": [[0, 0, 0, 0]] + [[r3(x), 0, 0, 0] for x, _ in MED], "_about": "the cornice ring round the pendentives' crown under each dome"})
add("small dome rings", {"type": "ring", "count": 16, "rOuter": r3(SS / 2 + 0.03), "rInner": 6.0, "height": 0.4, "y": RH, "turn": 0.5, "solid": True,
                         "place": [[r3(x), 0, r3(z), 0] for x, z in SMALL], "_about": "...under the small domes, whose drums stand in from the pendentives' circle"})
# the eight small ones: low octagonal drums, a window in every other face, the tiled dome, the lantern (OSM: lantern 34.1 - 46.7)
SD = {"R": 6.3, "dt": 0.7, "H": 6.16, "n": 8, "every": 2, "winW": 1.4, "winSill": 1.5, "winH": 2.3, "profile": "semicircular", "domeT": 0.5,
      "lanternR": 2.5, "lanternH": 5.6}
add("small domes", comp("components/drum-dome", SD, [[r3(x), 21.4, r3(z), 0] for x, z in SMALL],
                        build=["drum", "drum piers", "dome", "lantern", "interior"],
                        _about="EIGHT SMALL DOMES over the side naves (bays 1, 3, 5, 7): a low octagonal drum, the dome in glazed tiles, the brick lantern under a lead cap"))
MD = {"R": CZ, "dt": 0.9, "H": 8.6, "n": 8, "every": 1, "winW": 1.8, "winSill": 2.4, "winH": 3.4, "profile": "semicircular", "domeT": 0.6,
      "lanternR": 2.5, "lanternH": 5.6}
add("middle domes", comp("components/drum-dome", MD, [[r3(x), 21.4, 0, 0] for x, _ in MED],
                         build=["drum", "dome", "lantern", "interior"],
                         _about="TWO MIDDLING DOMES on the axis -- over the Santa Capilla (east) and the coro (west): a window in each face of the drum, the tiled dome, the lantern"))
GB = 6.0                                   # the great dome's drum stands on a plain base storey over the roofs
add("great drum base", {"type": "ring", "count": 8, "rOuter": 10.05, "rInner": CZ, "height": GB, "y": 21.4, "turn": 0.5, "solid": True,
                        "place": [[0, 0, 0, 0]], "courses": True, "_about": "the great dome's base storey over the roofs, from the pendentives' deck"})
add("great drum well", {"type": "interior", "plan": {"sides": 8, "radius": 9.3}, "height": GB, "at": [[0, 21.4, 0, 22.5 / 180 * PI]],
                        "_about": "the hall's space on up through the base storey to the drum's own"})
GD = {"R": CZ, "dt": 1.5, "H": 14.0, "n": 8, "every": 1, "winW": 2.4, "winSill": 3.5, "winH": 6.0, "profile": "pointed", "spread": 0.8, "domeT": 0.8,
      "ribsN": 8, "ribW": 0.5, "lanternR": 2.95, "lanternH": 7.0}
add("great dome", comp("components/drum-dome", GD, [[0, 27.4, 0, 0]],
                       build=["drum", "buttresses", "paired columns", "buttress entablature", "buttress cornice", "dome", "ribs", "lantern", "interior"],
                       _about="THE GREAT DOME over the retablo mayor: the tall drum of eight windows between buttresses with paired Corinthian columns, the ribbed tiled dome, the lantern (OSM: 51 - 67 m)"))

# ---- the roofs ------------------------------------------------------------------------------------------------------
HIPS = []
for i in NAVE_SAIL:                        # over the middle nave's sail-vaulted bays: pier line to pier line
    xs = [-EA1] + LINES + [EA1]
    x0, x1 = xs[i], xs[i + 1]
    HIPS.append(("nave", (x0 + x1) / 2, 0.0, x1 - x0, 2 * PZ))
for i in AISLE_SAIL:
    xs = [-EA1] + LINES + [EA1]
    x0, x1 = xs[i], xs[i + 1]
    for s in (-1, 1): HIPS.append(("aisle", (x0 + x1) / 2, s * (PZ + CH0) / 2, x1 - x0, CH0 - PZ))
hp = {}
for kind, x, z, w, l in HIPS:
    if w >= l: key, at = (r3(l), r3(w)), [r3(x), TOP, r3(z), Q]      # (the ridge along the longer side)
    else: key, at = (r3(w), r3(l)), [r3(x), TOP, r3(z), 0]
    hp.setdefault(key, []).append(at)
for k, ((w, l), at) in enumerate(sorted(hp.items())):
    add(f"bay roofs {k + 1}", {"type": "roof", "form": "hip", "width": w, "length": l, "pitch": 35, "overhang": 0.15, "at": at,
                               **({"_about": "hipped roofs of glazed tile over the sail-vaulted bays, between the domes"} if k == 0 else {})})
for s, nm in ((1, "south"), (-1, "north")):
    add(f"{nm} chapel roof", {"type": "roof", "form": "shed", "width": r3(ZI - CH0 + 0.2), "length": r3(2 * EA0), "pitch": 12, "at": [[0, WH, r3(s * (CH0 + ZI + 0.2) / 2), Q if s > 0 else -Q]],
                              **({"_about": "the lean-to roofs over the side chapels, from the outer walls' tops up to the arcade walls"} if s > 0 else {})})
for s, nm in ((1, "east"), (-1, "west")):
    add(f"{nm} chapel roof", {"type": "roof", "form": "shed", "width": r3(XI - EA1 + 0.2), "length": r3(2 * (Z0 - TW)), "pitch": 12,
                              "at": [[r3(s * (EA1 + XI + 0.2) / 2), WH, 0, PI if s > 0 else 0]]})
add("wall heads", {"type": "box", "width": r3(2 * EA0), "length": T, "height": 0.3, "flatRoof": True,
                   "at": [[0, WH, r3(s * (Z0 - T / 2)), 0] for s in (-1, 1)], "_about": "the coping of the outer walls under the balustrade"})
add("end wall heads", {"type": "box", "width": T, "length": r3(2 * (Z0 - TW)), "height": 0.3, "flatRoof": True,
                       "at": [[r3(s * (X0 - T / 2)), WH, 0, 0] for s in (-1, 1)]})

# ---- the balustrade round the roofs, the statues on the plaza front --------------------------------------------------
BAL = Balusters(h=1.05, every=0.42)
BY = WH + 0.3
for s in (-1, 1):
    BAL.run((-EA0, s * (Z0 - 0.5)), (EA0, s * (Z0 - 0.5)), BY)
    BAL.run((s * (X0 - 0.5), -(Z0 - TW)), (s * (X0 - 0.5), Z0 - TW), BY)

# ---- the plaza front: the portals ----------------------------------------------------------------------------------
for i in (0, 6):
    x = CH_X[i]
    add(f"portico {'west' if i == 0 else 'east'}", comp("components/portico", {"count": 2, "spacing": 6.0, "colR": 0.5, "colH": 9.4, "entH": 1.5, "depth": 1.9,
                                                                                  "order": "corinthian", "pitch": 22, "steps": 1, "stepH": 0.2},
                                                       [[r3(x), 0, Z0, 0]], build=["steps", "columns", "pediment"],
                                                       **({"_about": "the end portals on the plaza: a Corinthian column either side of the door, the entablature and a pediment"} if i == 0 else {})))
FW, FD = 14.0, 1.6                          # the middle portal: a frontispiece standing forward, the great arched niche through it
FZ = Z0 + FD
add("frontispiece", {"type": "wall", "width": FW, "thickness": FD, "height": WH,
                     "tiers": [{"h": WH, "openings": [arch(0, 7.0, 0, 10.0, glass=False, surround={"band": 0.9, "depth": 0.5, "head": False})]}],
                     "courses": {"plinth": True, "strings": False}, "at": [[0, 0, r3(FZ), 0]],
                     "_about": "the middle portal: the frontispiece standing forward of the front, the great round-arched niche through it, the door at its back"})
add("relief", {"type": "box", "width": 5.0, "length": 0.3, "height": 3.2, "at": [[0, 8.4, r3(Z0 + 0.15), 0]],
               "_about": "Pablo Serrano's relief of the Virgin's coming, in the niche over the door"})
for s, n in ((-1, "west"), (1, "east")):
    add(f"portal columns {n}", {"type": "colonnade", "order": "corinthian", "count": 2, "spacing": 2.5, "columnR": 0.6, "height": 13.4, "taper": 0.86,
                                "entablature": {"h": 2.2, "depth": 1.6}, "at": [[r3(s * 5.7), 0, r3(FZ + 0.7), 0]],
                                **({"_about": "paired giant Corinthian columns either side of the niche"} if s < 0 else {})})
BAL.run((-FW / 2, FZ - 0.5), (FW / 2, FZ - 0.5), BY)
# statues: on the balustrade over the pier lines and the portals, saints in the stone (statuary)
ST_PTS = [(r3(x), r3(BY), r3(Z0 - 0.5)) for x in LINES] + [(r3(s * 5.7), r3(BY), r3(FZ - 0.5)) for s in (-1, 1)]
add("statue pedestals", {"type": "box", "width": 1.0, "length": 1.0, "height": 1.2, "at": [[p[0], p[1], p[2], 0] for p in ST_PTS],
                         "_about": "pedestals on the balustrade for the saints over the plaza front"})
for k, v in ST.row("saint", [(p[0], p[1] + 1.2, p[2]) for p in ST_PTS], kind=["man", "woman", "man"], style="roman", stone="limestone", scale=1.6,
                   face=ST.FACE_PZ).items():
    add(k, v)

# ---- the four towers ------------------------------------------------------------------------------------------------
# A canonical tower is the south-east one (+x +z): its faces 2 (-z) and 3 (-x) toward the church, 0 and 1 outward;
# the others are it turned. Stages: the brick shaft (to 28), the clock stage, the stage of one great arch a face,
# the belfry of two arches a face, the deck with its balustrade and urns, the copper helm with two lanterns.
WI = 7.2                                   # the inside, the same all the way up
STG = [("shaft", 0.0, 28.0, 10.6), ("clock stage", 28.0, 39.0, 10.2), ("arch stage", 39.0, 54.0, 9.8), ("belfry", 54.0, 66.0, 9.4)]
YAW = {(1, 1): 0.0, (1, -1): Q, (-1, 1): -Q, (-1, -1): PI}
TOWERS = {k: [r3(k[0] * TX), 0, r3(k[1] * TZ), r3(y)] for k, y in YAW.items()}
CLIMB = (-1, -1)                            # the Torre de San Francisco de Borja: the north-west one, entered from the river
def stage_faces(name, H, climbed):
    if name == "shaft":
        lo = [arch(0, 1.6, 0, 2.6, glass=False)]   # the doors from the church (the others' only door: a sacristy below)
        street = [arch(0, 1.6, 0, 2.8, glass=False, surround=True)] if climbed else []
        win = lambda: [arch(0, 1.0, 6.0, 8.0, surround={"head": False})]
        return {"0": [{"h": 16.0, "openings": street + ([] if climbed else win())}, {"openings": [arch(0, 1.2, 4.0, 7.0, surround=True)]}],
                "1": [{"h": 16.0, "openings": win()}, {"openings": [arch(0, 1.2, 4.0, 7.0, surround=True)]}],
                "2": [{"h": 16.0, "openings": lo}, {"openings": [arch(0, 1.2, 4.0, 7.0, surround=True)]}],
                "3": [{"h": 16.0, "openings": lo if climbed else []}, {"openings": [arch(0, 1.2, 4.0, 7.0, surround=True)]}]}
    if name == "clock stage":
        return {"openings": [arch(0, 1.4, 7.6, 9.3, surround={"head": False})]}
    if name == "arch stage":
        return {"openings": [arch(0, 3.2, 1.0, 9.6, glass=False, surround={"head": "cornice"})]}
    return {"openings": [arch(s * 1.75, 2.0, 1.1, 7.6, glass=climbed, surround={"head": False}) for s in (-1, 1)]}
for climbed in (False, True):
    keys = [CLIMB] if climbed else [k for k in YAW if k != CLIMB]
    pre = "nw tower" if climbed else "towers"
    at = [TOWERS[k] for k in keys]
    for name, y0, y1, W in STG:
        t = (W - WI) / 2
        f = stage_faces(name, y1 - y0, climbed)
        d = {"type": "enclosure", "plan": {"rect": [W, W]}, "thickness": r3(t), "height": r3(y1 - y0), "interior": True,
             "courses": {"skip": [2, 3], "strings": [16.0]} if name == "shaft" else {"plinth": False}, "at": [[a[0], y0, a[2], a[3]] for a in at]}
        if "openings" in f: d["openings"] = f["openings"]
        else: d["faces"] = f
        if name in ("arch stage", "belfry") and not (climbed and name == "belfry"): d["glass"] = False
        about = {"shaft": "the brick shaft from the ground, its faces toward the church blind but for a door (the climbed one has two, and its street door); the string course at the body's cornice",
                 "clock stage": "the clock stage over the roofs, a small window over each dial",
                 "arch stage": "the stage of one great arch a face, open",
                 "belfry": "the belfry, two arches a face" + (" -- glazed: the MIRADOR, the viewpoint visitors reach by the lift" if climbed else ", open")}[name]
        add(f"{pre} {name}", d | {"_about": about})
    # the slabs between the stages' walls (the floors you see through the arches) and the deck over the belfry
    add(f"{pre} deck", {"type": "box", "width": 9.4, "length": 9.4, "height": 0.6, "flatRoof": True, "at": [[a[0], 66.0, a[2], a[3]] for a in at],
                        "_about": "the deck over the belfry: its balustrade and urns round the helm's foot"})
    if not climbed:
        add(f"{pre} floors", {"type": "box", "width": WI + 0.2, "length": WI + 0.2, "height": 0.4, "flatRoof": True,
                              "at": [[a[0], y, a[2], a[3]] for a in at for y in (38.6, 53.6)], "_about": "the floors of the arched stage and the belfry"})
# the clocks: a dial on each face of the clock stage
dials = []
for k, a in TOWERS.items():
    for fx, fz, yaw in ((0, 1, 0.0), (1, 0, Q), (0, -1, PI), (-1, 0, -Q)):
        dials.append([r3(a[0] + fx * 5.1), 33.4, r3(a[2] + fz * 5.1), r3(yaw)])
add("clocks", comp("components/clock-dial", {"R": 1.5, "t": 0.12}, dials, _about="the clock dials on every face of the towers' clock stages"))
# the helms: the copper bell, the open lantern, the second bell and lantern, the spike, the gilt ball and the cross
HELM = {"sides": 8, "R": 3.9, "footH": 0.7, "profile": "bell", "waist": 0.8, "lift": 0.62, "LR": 2.0, "LH": 4.4, "glazed": 0, "lanterns": "two",
        "R2": 2.3, "L2R": 0.85, "L2H": 2.0, "spikeH": 3.2, "ballR": 0.55, "crossH": 2.6}
add("helms", comp("components/baroque-helm", HELM, [[a[0], 66.6, a[2], 0] for a in TOWERS.values()],
                  _about="the towers' helms: the green copper bell, the open lantern, a second bell and lantern, the spike, the gilt ball and the cross"))
for a in TOWERS.values():
    c = 4.25
    BAL.run((a[0] - c, a[2] - c), (a[0] + c, a[2] - c), 66.6); BAL.run((a[0] + c, a[2] - c), (a[0] + c, a[2] + c), 66.6)
    BAL.run((a[0] + c, a[2] + c), (a[0] - c, a[2] + c), 66.6); BAL.run((a[0] - c, a[2] + c), (a[0] - c, a[2] - c), 66.6)
for a in TOWERS.values():                   # and the balustrades over the clock and the arched stages, on their cornices
    for y, c in ((39.0, 4.75), (54.0, 4.55)):
        BAL.run((a[0] - c, a[2] - c), (a[0] + c, a[2] - c), y); BAL.run((a[0] + c, a[2] - c), (a[0] + c, a[2] + c), y)
        BAL.run((a[0] + c, a[2] + c), (a[0] - c, a[2] + c), y); BAL.run((a[0] - c, a[2] + c), (a[0] - c, a[2] - c), y)
URNS = [[r3(a[0] + sx * 4.3), y, r3(a[2] + sz * 4.3), 0] for a in TOWERS.values() for sx in (-1, 1) for sz in (-1, 1) for y in (66.6,)]
URNS += [[r3(a[0] + sx * c), y, r3(a[2] + sz * c), 0] for a in TOWERS.values() for sx in (-1, 1) for sz in (-1, 1) for y, c in ((39.0, 4.8), (54.0, 4.6))]
add("urns", {"type": "column", "radius": 0.32, "height": 1.3, "sides": 8, "taper": 0.45, "at": URNS, "_about": "the urns on the corners of the towers' balustrades"})
add("urn knobs", {"type": "dome", "radius": 0.36, "thickness": 0, "sides": 8, "head": {"profile": "onion", "bulge": 1.3, "neck": 0.6},
                  "at": [[u[0], r3(u[1] + 0.55), u[2], 0] for u in URNS]})

# ---- the climbed tower: the stair, the lift, the mirador -------------------------------------------------------------
TA = TOWERS[CLIMB]
tR = 1.8
c = WI / 2 - tR - 0.05
add("nw tower stair", comp("components/tower-stair", {"W": WI, "H": 54.0, "tR": tR, "tx": r3(c), "tz": r3(c)}, [TA],
                           _about="the stair up the Torre de San Francisco de Borja: its turret in the outer corner, the spiral from the street door's floor to the mirador's"))
LS = 2.0                                    # the lift shaft in the inner corner, a door toward the tower's middle
lc = WI / 2 - LS / 2
add("lift shaft", {"type": "enclosure", "plan": {"rect": [LS, LS]}, "thickness": 0.15, "height": 53.6,
                   "faces": {"0": [{"openings": [arch(0, 1.2, 0, 2.2, glass=False)]}], "1": [{"openings": [arch(0, 1.2, 0, 2.2, glass=False)]}], "2": [], "3": []},
                   "interior": True, "at": [[r3(TA[0] + lc), 0, r3(TA[2] + lc), 0]],
                   "_about": "the lift's shaft in the tower's inner corner (the real one rises 62 m)"})
add("lift", {"type": "marker", "role": "lift", "at": [[r3(TA[0] + lc), 0, r3(TA[2] + lc), 0]], "data": {"dy": 54.0},
             "_about": "the lift: from the shaft's foot to the mirador's floor (index.html: a stair shortcut)"})

# ---- inside: the retablo mayor ----------------------------------------------------------------------------------------
RX = PX[0] - PW / 2 + 0.5                    # its face, just inside the arch east of the great dome: 7.75
add("retablo predella", {"type": "box", "width": 1.6, "length": 13.0, "height": 3.4, "at": [[r3(RX + 0.8), 0, 0, 0]],
                         "_about": "THE RETABLO MAYOR (Damián Forment, 1512-18, alabaster): the predella of seven scenes"})
add("retablo", {"type": "wall", "width": 13.0, "thickness": 1.0, "height": 10.0,
                "tiers": [{"h": 10.0, "openings": [arch(0, 3.4, 1.4, 6.6, glass=False), arch(-4.3, 2.6, 1.4, 5.6, glass=False), arch(4.3, 2.6, 1.4, 5.6, glass=False)]}],
                "at": [[r3(RX), 3.4, 0, -Q]], "_about": "...its body: three great niches, the Assumption in the middle, the Nativity and the Presentation"})
add("retablo back", {"type": "box", "width": 0.5, "length": 13.0, "height": 10.0, "at": [[r3(RX + 1.25), 3.4, 0, 0]], "_about": "the back of the niches"})
add("retablo cornice", {"type": "box", "width": 1.9, "length": 13.6, "height": 0.5, "at": [[r3(RX + 0.6), 13.4, 0, 0]]})
for z, h, s in ((0.0, 2.6, 2.6), (-4.3, 1.9, 2.2), (4.3, 1.9, 2.2)):
    add(f"retablo pinnacle {'middle' if z == 0 else 'south' if z > 0 else 'north'}", comp("components/pinnacle", {"w": 1.0, "h": h, "s": s}, [[r3(RX + 0.6), 13.9, r3(z), 0]],
                                                                                       **({"_about": "the pinnacles of its crest"} if z == 0 else {})))
RP = [-6.25, -2.15, 2.15, 6.25]            # the buttresses between the niches, each under a pinnacle of the crest
add("retablo posts", {"type": "box", "width": 0.5, "length": 0.45, "height": 10.4, "at": [[r3(RX - 0.25), 3.4, z, 0] for z in RP],
                      "_about": "the slim buttresses framing its niches, carved with tracery, rising to the crest"})
add("retablo post pinnacles", comp("components/pinnacle", {"w": 0.45, "h": 1.2, "s": 1.6}, [[r3(RX - 0.25), 13.8, z, 0] for z in RP]))
add("retablo canopies", {"type": "box", "width": 0.6, "length": 3.6, "height": 0.35, "at": [[r3(RX - 0.3), 10.2, 0.0, 0]] + [[r3(RX - 0.3), 9.2, z, 0] for z in (-4.3, 4.3)],
                         "_about": "the canopies over its niches"})
for k, v in ST.row("retablo figure", [(RX + 0.5, 3.4 + 1.4, 0.0), (RX + 0.5, 3.4 + 1.4, -4.3), (RX + 0.5, 3.4 + 1.4, 4.3)], kind="woman", style="gothic",
                   stone="marble", scale=[1.45, 1.15, 1.15], face=ST.FACE_NX).items():
    add(k, v)
add("high altar", {"type": "zone", "zone": "altar", "w": 4.0, "d": 1.8, "h": 8.0, "at": [[r3(RX - 1.6), 0, 0, 0]]})

# ---- the Santa Capilla (Ventura Rodríguez, 1750-65) -------------------------------------------------------------------
SCX = BX[5]
AXR, AZR = 4.4, 6.4                         # the oval of columns
SCOL = [[r3(SCX + AXR * math.cos(math.radians(15 + 30 * k))), 0, r3(AZR * math.sin(math.radians(15 + 30 * k))), 0] for k in range(12)]
add("santa capilla pedestals", {"type": "box", "width": 1.1, "length": 1.1, "height": 1.2, "at": SCOL,
                                "_about": "THE SANTA CAPILLA round the Virgin's pillar: the pedestals of its twelve columns on an oval, open between them on every side"})
add("santa capilla columns", {"type": "colonnade", "order": "corinthian", "count": 1, "spacing": 1, "columnR": 0.38, "height": 7.4, "taper": 0.88,
                              "at": [[a[0], 1.2, a[2], 0] for a in SCOL], "_about": "its Corinthian columns of jasper"})
add("santa capilla entablature", {"type": "enclosure", "plan": {"sides": 24, "radius": r3(AXR + 0.6)}, "thickness": 1.2, "height": 1.4, "interior": False,
                                  "courses": {"plinth": False}, "at": [[r3(SCX), 8.6, 0, 0]], "stretch": [1, 1, r3(AZR / AXR)],
                                  "_about": "the oval entablature over the columns"})
add("santa capilla dome", {"type": "dome", "radius": r3(AXR + 0.55), "thickness": 0.3, "sides": 24, "oculus": 1.6, "head": {"profile": "semicircular"},
                           "at": [[r3(SCX), 10.0, 0, 0]], "stretch": [1, 0.85, r3(AZR / AXR)],
                           "_about": "the oval dome, painted (González Velázquez), open in an oculus to the middling dome over it"})
add("santa capilla space", {"type": "interior", "plan": {"sides": 24, "radius": r3(AXR + 0.6)}, "height": 14.6, "at": [[r3(SCX), 0, 0, 0]], "stretch": [1, 1, r3(AZR / AXR)]})
add("venida", {"type": "box", "width": 0.5, "length": 5.4, "height": 7.2, "at": [[r3(SCX + 3.3), 0, 0, 0]],
               "_about": "the altar of the Venida at the back of the chapel (Carlos Salas' marble group of the Virgin's coming)"})
add("venida altar", {"type": "zone", "zone": "altar", "w": 2.8, "d": 1.4, "h": 6.0, "at": [[r3(SCX + 2.0), 0, 0, 0]]})
PX_, PZ_ = SCX + 2.4, 3.6                    # the Virgin's pillar, on the right of the altar
add("pillar base", {"type": "box", "width": 1.0, "length": 1.0, "height": 0.7, "at": [[r3(PX_), 0, PZ_, 0]], "_about": "the silver-clad foot of the pillar"})
add("pillar", {"type": "column", "radius": 0.3, "height": 1.7, "sides": 16, "at": [[r3(PX_), 0.7, PZ_, 0]], "_about": "THE PILLAR: the jasper column the Virgin stood on"})
add("pillar canopy", {"type": "dome", "radius": 0.9, "thickness": 0.08, "sides": 16, "head": {"profile": "semicircular"}, "at": [[r3(PX_), 3.6, PZ_, 0]],
                      "_about": "the gilt canopy over her image"})
add("pillar canopy posts", {"type": "column", "radius": 0.07, "height": 3.6, "sides": 6, "at": [[r3(PX_ + dx), 0, r3(PZ_ + dz), 0] for dx in (-0.75, 0.75) for dz in (-0.75, 0.75)]})
add("virgin", ST.statue((PX_, 2.4, PZ_), kind="woman", style="gothic", stone="gold", scale=0.42, face=ST.FACE_NX, seed=3))
for k, v in ST.row("santa capilla angel", [(SCX + AXR * math.cos(a) * 1.0, 10.0, AZR * math.sin(a)) for a in (0.0, PI / 2, PI, -PI / 2)],
                   kind="woman", style="roman", stone="marble", wings="raised", scale=1.2, face=[ST.FACE_PX, ST.FACE_PZ, ST.FACE_NX, ST.FACE_NZ]).items():
    add(k, v)

# ---- the coro (middle nave, second bay from the west) and the coreto (the east end) ------------------------------------
KX, KW = BX[1], BAYS[1][1]                    # -33.4, 11.6 between the piers' faces
K0, K1 = KX - KW / 2, KX + KW / 2
CWT, CWH = 0.8, 6.0
add("coro walls", {"type": "wall", "width": r3(KW), "thickness": CWT, "height": CWH, "at": [[r3(KX), 0, r3(-CZ + CWT), PI], [r3(KX), 0, r3(CZ - CWT), 0]],
                   "_about": "THE CORO: its walls between the piers (alabaster reliefs outside), open toward the high altar"})
add("trascoro", {"type": "wall", "width": r3(2 * CZ), "thickness": CWT, "height": CWH,
                 "tiers": [{"h": CWH, "openings": [arch(0, 2.6, 0.9, 3.4, glass=False)]}], "at": [[r3(K0 + CWT), 0, 0, -Q]],
                 "_about": "the trascoro wall at its west end, a blind niche for its altar"})
add("trascoro niche", {"type": "box", "width": 0.3, "length": 2.8, "height": 4.8, "at": [[r3(K0 + CWT + 0.15), 0, 0, 0]]})
ZC_ = CZ - CWT                              # inside the walls
TIER = 1.6
add("coro dais", {"type": "box", "width": r3(KW - CWT - 0.4), "length": TIER, "height": 0.45, "walked": True,
                  "at": [[r3(K0 + CWT + (KW - CWT - 0.4) / 2), 0, r3(s * (ZC_ - TIER / 2)), 0] for s in (-1, 1)] + [],
                  "_about": "the stalls' raised back tier along each side"})
add("coro dais west", {"type": "box", "width": TIER, "length": r3(2 * (ZC_ - TIER)), "height": 0.45, "walked": True, "at": [[r3(K0 + CWT + TIER / 2), 0, 0, 0]]})
SL = KW - CWT - 0.4 - TIER
for s in (-1, 1):
    yaw = -Q if s < 0 else Q
    add(f"coro stalls {'north' if s < 0 else 'south'}", {"type": "zone", "zone": "choir", "w": r3(KW - CWT - 0.4), "d": TIER, "h": 4.0,
                                                          "at": [[r3(K0 + CWT + (KW - CWT - 0.4) / 2), 0.45, r3(s * (ZC_ - TIER / 2)), yaw]],
                                                          **({"_about": "the oak stalls (Flemish, 16th century) in tiers along the coro's walls"} if s < 0 else {})})
    add(f"coro stalls {'north' if s < 0 else 'south'} front", {"type": "zone", "zone": "choir", "w": r3(SL), "d": TIER, "h": 4.0,
                                                                "at": [[r3(K0 + CWT + TIER + SL / 2), 0, r3(s * (ZC_ - 1.5 * TIER)), yaw]]})
add("coro stalls west", {"type": "zone", "zone": "choir", "w": r3(2 * (ZC_ - TIER)), "d": TIER, "h": 4.0, "at": [[r3(K0 + CWT + TIER / 2), 0.45, 0, 0]]})
add("coro lectern", {"type": "zone", "zone": "lectern", "w": 1.2, "d": 1.2, "h": 3.0, "at": [[r3(KX + 1.0), 0, 0, 0]]})
add("organ loft", {"type": "box", "width": 7.0, "length": 1.9, "height": 0.5, "at": [[r3(KX), CWH, r3(-CZ + 0.95), 0]], "_about": "the organ's loft on the coro's north wall"})
add("coro organ", {"type": "zone", "zone": "organ", "w": 6.0, "d": 1.6, "h": 10.0, "at": [[r3(KX), r3(CWH + 0.5), r3(-CZ + 1.0), -Q]],
                   "_about": "the coro's organ (its case of 1529) over the stalls"})
gr = []
for z in [v * 0.18 for v in range(-44, 45)]:
    if abs(z) > 1.3: gr.append([r3(K1 - 0.1), 0, r3(z), r3(K1 - 0.1), 4.6, r3(z)])
gr += [[r3(K1 - 0.1), y, r3(-CZ), r3(K1 - 0.1), y, -1.3] for y in (0.1, 2.2, 4.6)] + [[r3(K1 - 0.1), y, 1.3, r3(K1 - 0.1), y, r3(CZ)] for y in (0.1, 2.2, 4.6)]
gr += [[r3(K1 - 0.1), 4.6, -1.3, r3(K1 - 0.1), 4.6, 1.3]]
add("coro grille", {"type": "bars", "lines": gr, "w": 0.05, "h": 0.05, "_about": "Juan Tomás Celma's grille across the coro's open end, its gate open"})
add("coro grille posts", {"type": "box", "width": 0.25, "length": 0.25, "height": 5.0, "at": [[r3(K1 - 0.1), 0, s * 1.3, 0] for s in (-1, 1)]})
# the coreto: stalls north and south, the organ on its loft over the east door, Goya's fresco on its vault
EX, EW = BX[6], BAYS[6][1]
for s in (-1, 1):
    add(f"coreto stalls {'north' if s < 0 else 'south'}", {"type": "zone", "zone": "choir", "w": 9.0, "d": 3.2, "h": 4.0,
                                                            "at": [[r3(EX + 0.4), 0, r3(s * (CZ - 1.7)), -Q if s < 0 else Q]],
                                                            **({"_about": "THE CORETO at the east end: its stalls"} if s < 0 else {})})
add("coreto organ loft", {"type": "box", "width": 1.8, "length": 6.0, "height": 0.5, "at": [[r3(EA0 - 0.9), 7.4, 0, 0]], "_about": "the coreto's organ loft over the east door"})
add("coreto organ", {"type": "zone", "zone": "organ", "w": 5.5, "d": 1.4, "h": 9.0, "at": [[r3(EA0 - 0.9), 7.9, 0, PI]], "_about": "the coreto's organ (1720)"})

# ---- pews, side altars ----------------------------------------------------------------------------------------------
add("seating", {"type": "zone", "zone": "seating", "w": 14.0, "d": 10.0, "h": 15.0, "at": [[r3(BX[2]), 0, 0, 0]],
                "_about": "pews in the middle nave, between the coro and the high altar, and before the Santa Capilla"})
add("seating east", {"type": "zone", "zone": "seating", "w": 14.0, "d": 10.0, "h": 15.0, "at": [[r3(BX[4]), 0, 0, 0]]})
add("seating crossing", {"type": "zone", "zone": "seating", "w": 13.0, "d": 6.0, "h": 15.0, "at": [[-3.4, 0, 0, 0]]})
SIDE = [i for i in range(7) if not (i in (0, 3, 6))]
add("chapel altars", {"type": "zone", "zone": "altar", "w": 3.0, "d": 1.4, "h": 6.0,
                      "at": [[r3(CHAP[i][0]), 0, r3(s * (ZI - 1.0)), Q if s > 0 else -Q] for i in SIDE for s in (-1, 1)] +
                            [[r3(CHAP[i][0]), 0, r3(-(ZI - 1.0)), -Q] for i in (0, 6)],
                      "_about": "an altar in each side chapel against the outer wall (the plaza side's portal bays are vestibules)"})
add("end chapel altars", {"type": "zone", "zone": "altar", "w": 3.0, "d": 1.4, "h": 6.0,
                          "at": [[r3(s * (XI - 1.0)), 0, r3(t * ECH), 0 if s > 0 else PI] for s in (-1, 1) for t in (-1, 1)]})

# ---- the balustrade parts, statues capped -------------------------------------------------------------------------
for k, v in BAL.parts("balustrade").items(): add(k, v)
statues = ST.capped({k: parts[k] for k in parts if parts[k].get("role") == "statue"})
for k in [k for k in parts if parts[k].get("role") == "statue" and k not in statues]:
    del parts[k]; build.remove(k)

doc = {"name": "El Pilar",
       "_about": "THE CATHEDRAL-BASILICA OF OUR LADY OF THE PILLAR, Zaragoza (1681-1872; towers 1907-61), from OpenStreetMap (the 131 x 69 m rectangle on the Ebro, the eleven domes' lanterns) and the published plans: the brick HALL CHURCH of three naves of one height, seven bays on two rows of cruciform piers -- pendentives under the domes, sail vaults ('bóvedas de plato') over the other bays --, side chapels and end chapels; ELEVEN DOMES in glazed tiles, each with its lantern: the great one on its tall drum between buttresses with paired columns over the retablo mayor, two middling ones over the Santa Capilla and the coro, eight small ones over the side naves; hipped and lean-to tile roofs, clerestory windows; two storeys of windows in stone surrounds, the plaza front's giant Corinthian order and its three portals (two pedimented porticoes, the great niche with Serrano's relief), the balustrade with saints; FOUR CORNER TOWERS of ~89 m -- shaft, clock stage, arched stage, belfry, balustrade and urns, the copper helm of two lanterns --, the north-west one (San Francisco de Borja) climbed by its stair and a lift to its glazed mirador. Inside: the Santa Capilla (oval of twelve columns, oval dome open in an oculus, the Virgin's pillar and image, the altar of the Venida), Forment's alabaster retablo mayor, the coro (stalls in tiers, organ, Celma's grille), the coreto (stalls, organ, Goya's fresco), pews, chapel altars (tools/archgen/el_pilar.py).",
       "params": {"detail": 4}, "base": {"height": 0.6, "steps": 3, "stepOut": 0.4, "margin": 4}, "railing": {"type": "iron"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/el-pilar.json"), "w").write(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

# ---- the doors -------------------------------------------------------------------------------------------------------
doors = {"name": "El Pilar: doors", "building": "el-pilar",
         "_about": "The Basilica of Our Lady of the Pillar: carved wooden doors in its three portals on the plaza, the river door, the end doors, and the tower's street door (the Paseo Echegaray y Caballero) and its doors from the church",
         "doors": [
             {"_about": "the middle portal on the plaza, in the great niche", "part": "south wall", "near": [0, Z0], "style": "baroque", "leafH": 7.2},
             {"_about": "the end portals on the plaza", "part": "south wall", "near": [[r3(CH_X[0]), Z0], [r3(CH_X[6]), Z0]], "style": "baroque", "leafH": 6.4},
             {"_about": "the river door", "part": "north wall", "near": [0, -Z0], "style": "baroque", "leafH": 6.6},
             {"_about": "the end doors (the east one the Romanesque tympanum's)", "part": ["east wall", "west wall"], "style": "baroque", "leafH": 6.4},
             {"_about": "the climbed tower's doors: the street door and the doors from the church", "part": "nw tower shaft", "style": "tower"},
             {"_about": "the other towers' doors from the church", "part": "towers shaft", "style": "tower"},
             {"_about": "the stair turret's door", "part": ["nw tower stair/turret", "nw tower stair/turret door"], "style": "tower"}]}
open(os.path.join(ROOT, "assets/doors/el-pilar.json"), "w").write(json.dumps(doors, indent=2, ensure_ascii=False) + "\n")

# ---- the finish ------------------------------------------------------------------------------------------------------
ALL_DOMES = ["small domes", "middle domes", "great dome"]
TOWER_PARTS = [f"{p} {n}" for p in ("towers", "nw tower") for n, *_ in STG]
INSIDE_BOX = [-EA0, -SZ1, EA0, SZ1]
fin = {"name": "El Pilar", "building": "architecture/el-pilar",
       "_about": "El Pilar: warm red-brown brick walls and towers, every dressing -- window surrounds, the orders, courses, portals, balustrades, statues -- in pale stone; the eleven domes in glazed tiles laid in diamonds of green, yellow, blue and white (the great one in a grey-green glaze of scales, its ribs in stone), the lanterns' caps in lead, the towers' helms in green copper with gilt balls, the roofs in buff glazed tile; inside, white stucco picked out in gold, the cupolas and the coreto's vault painted (Goya, the Bayeus, González Velázquez), Forment's retablo in alabaster, the Santa Capilla in jasper and gilt, the coro in oak, marble floors in patterns.",
       "stone": {"color": "#a65f45", "accent": "#8e4f39", "pat": "brick"},
       "rules": [
           {"parts": ["clocks/hands", "clocks/marks"], "pattern": "roofs/sheet metal", "palette": "iron", "_about": "the hands and hour marks"},
           {"parts": ["clocks/ring", "clocks/hub"], "pattern": "roofs/gold leaf"},
           {"parts": ["clocks/dial", "clocks"], "pattern": "stone/plaster", "palette": "plaster-white", "_about": "the white dials"},
           {"parts": ["helms/ball", "helms/cross", "great dome/lantern/finial", "small domes/lantern/finial", "middle domes/lantern/finial"], "pattern": "roofs/gold leaf",
            "_about": "the gilt balls, crosses and finials"},
           {"parts": ["helms/bulb", "helms/bulb 2", "helms/spike"], "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the towers' helms in green copper"},
           {"parts": ["small domes/lantern/cap", "middle domes/lantern/cap", "great dome/lantern/cap"], "pattern": "roofs/sheet metal", "palette": "lead",
            "_about": "the lanterns' caps in lead"},
           {"parts": ["great dome/dome"], "surface": "roof", "pattern": "roofs/fish scale", "palette": "pilar-glaze-grey", "scale": 2.2,
            "_about": "the great dome: glazed scales in grey-green and white"},
           {"parts": ["middle domes/dome"], "surface": "roof", "pattern": "roofs/glazed diamonds", "palette": "el-pilar-green", "scale": 4.0,
            "_about": "the middling domes: big diamonds of green and yellow tiles, white and blue at their crossings"},
           {"parts": ["small domes/dome"], "surface": "roof", "within": [-70, -40, 0, 0], "pattern": "roofs/glazed diamonds", "palette": "el-pilar", "scale": 3.5,
            "_about": "the small domes: diamonds of blue and yellow, of white and green, in turn"},
           {"parts": ["small domes/dome"], "surface": "roof", "within": [0, 0, 70, 40], "pattern": "roofs/glazed diamonds", "palette": "el-pilar", "scale": 3.5},
           {"parts": ["small domes/dome"], "surface": "roof", "pattern": "roofs/glazed diamonds", "palette": "el-pilar-white", "scale": 3.5},
           {"parts": ["great dome/ribs"], "pattern": "stone/ashlar fine", "palette": "limestone", "_about": "the great dome's ribs in stone"},
           {"parts": ["kind:roof", "great pendentives deck 1", "great pendentives deck 2", "great pendentives deck 3", "great pendentives deck 4",
                      "middle pendentives deck 1", "middle pendentives deck 2", "middle pendentives deck 3", "middle pendentives deck 4",
                      "small pendentives deck 1", "small pendentives deck 2", "small pendentives deck 3", "small pendentives deck 4"], "surface": "roof",
            "pattern": "roofs/coppi", "palette": "pilar-tile", "_about": "the roofs in buff glazed tile"},
           # inside
           {"parts": ["santa capilla columns shafts", "santa capilla columns bases", "pillar"], "pattern": "stone/marble", "palette": "pilar-jasper", "_about": "the Santa Capilla's columns and the pillar in jasper"},
           {"parts": ["pillar base"], "pattern": "materials/metal", "palette": "silver", "_about": "the pillar's silver foot"},
           {"parts": ["pillar canopy", "pillar canopy posts", "santa capilla entablature", "santa capilla columns capitals", "santa capilla columns abaci", "dome rings", "small dome rings", "pier imposts", "coro grille", "coro grille posts"],
            "pattern": "roofs/gold leaf", "_about": "gilt: the cornice rings under the domes, the piers' imposts, the Santa Capilla's entablature and canopy, Celma's grille"},
           {"parts": ["santa capilla dome"], "side": "in", "pattern": "stone/plaster", "palette": "pilar-fresco", "_about": "the Santa Capilla's painted dome"},
           {"parts": ["santa capilla dome"], "pattern": "roofs/gold leaf"},
           {"parts": ["santa capilla pedestals", "venida", "trascoro", "trascoro niche", "coro walls", "pier bases"], "pattern": "stone/marble", "palette": "marble-rose",
            "_about": "marble: the pedestals, the Venida's altar, the coro's walls, the piers' bases"},
           {"parts": ["retablo", "retablo predella", "retablo back", "retablo cornice", "retablo pinnacle middle", "retablo pinnacle north", "retablo pinnacle south",
                      "retablo posts", "retablo post pinnacles", "retablo canopies"],
            "pattern": "stone/marble", "palette": "alabaster", "_about": "Forment's retablo in alabaster"},
           {"parts": ["coro stalls north", "coro stalls south", "coro stalls north front", "coro stalls south front", "coro stalls west", "coreto stalls north", "coreto stalls south",
                      "coro dais", "coro dais west", "organ loft", "coreto organ loft"], "pattern": "timber/wood", "palette": "oak", "_about": "the coro's and coreto's oak stalls and lofts"},
           {"parts": ["small domes/dome", "middle domes/dome", "great dome/dome", "small pendentives", "middle pendentives", "great pendentives"] + SAIL_PARTS[:0],
            "side": "in", "pattern": "stone/plaster", "palette": "pilar-fresco",
            "_about": "the cupolas and their pendentives painted (Goya's Regina Martyrum on the Ebro side, the Bayeus')"},
           {"parts": SAIL_PARTS, "side": "in", "within": [r3(EA0 - 12.0), -10, r3(EA0 + 1), 10], "pattern": "stone/plaster", "palette": "pilar-fresco",
            "_about": "the coreto's vault: Goya's Adoration of the Name of God"},
           {"parts": ["kind:moulding"], "side": "in", "pattern": "roofs/gold leaf", "_about": "the mouldings inside gilt"},
           {"parts": TOWER_PARTS + ["nw tower deck", "towers deck", "towers floors", "lift shaft", "nw tower stair"], "surface": "floor", "side": "in",
            "pattern": "floors/flagstones", "palette": "pilar-tile", "_about": "the towers' floors in tile"},
           {"surface": "floor", "side": "in", "within": [r3(SCX - AXR - 0.6), -AZR - 0.6, r3(SCX + AXR + 0.6), AZR + 0.6], "pattern": "floors/compass", "palette": "marble-rose",
            "_about": "the Santa Capilla's floor, a marble star"},
           {"surface": "floor", "side": "in", "within": [r3(K0), -CZ, r3(K1), CZ], "pattern": "floors/checker", "palette": "marble-bw", "_about": "the coro's floor"},
           {"surface": "floor", "side": "in", "within": [-EA0, -CZ, EA0, CZ], "pattern": "floors/opus sectile", "palette": "marble-grey", "_about": "the middle nave in marble"},
           {"surface": "floor", "side": "in", "pattern": "floors/checker diagonal", "palette": "marble-grey", "_about": "marble floors"},
           {"surface": "ceiling", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white", "_about": "white stucco vaults and arches"},
           # the towers' faces toward the end and side chapels: in the chapels (the tower's own inside stays brick) -- a strip along each
           *[{"parts": ["towers shaft", "nw tower shaft"], "surface": "wall", "below": 16.0, "pattern": "stone/plaster", "palette": "plaster-white", "within": w,
              **({"_about": "the towers' faces toward the end and side chapels, in stucco as the chapels are"} if k == 0 else {})}
             for k, w in enumerate([b for sx in (1, -1) for sz in (1, -1) for b in (
                 [r3(min(sx * 54.8, sx * 65.0)), r3(min(sz * 23.8, sz * 24.3)), r3(max(sx * 54.8, sx * 65.0)), r3(max(sz * 23.8, sz * 24.3))],
                 [r3(min(sx * 54.8, sx * 55.3)), r3(min(sz * 23.8, sz * 34.4)), r3(max(sx * 54.8, sx * 55.3)), r3(max(sz * 23.8, sz * 34.4))])])],
           {"parts": TOWER_PARTS + ["nw tower deck", "towers deck", "towers floors", "lift shaft"], "side": "in", "pattern": "stone/brick", "palette": "pilar-brick",
            "_about": "the towers bare brick inside"},
           {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white", "_about": "white stucco walls"},
           # outside
           {"parts": ["kind:moulding", "kind:column", "kind:colonnade", "frontispiece", "relief", "portico west", "portico east", "portal columns west", "portal columns east",
                      "statue pedestals", "urns", "urn knobs", "wall heads", "end wall heads", "great dome/buttress entablature", "great dome/buttress cornice", "great dome/paired columns",
                      "nw tower deck", "towers deck", "helms/foot", "helms/lantern", "helms/lantern head", "helms/lantern 2", "helms/lantern 2 head"],
            "pattern": "stone/ashlar fine", "palette": "limestone", "_about": "pale stone: every course, surround, column, portal, balustrade, the helms' lanterns"},
           {"surface": "floor", "pattern": "floors/flagstones", "palette": "limestone", "_about": "the steps and the decks in stone"},
           {"surface": "wall", "pattern": "stone/brick", "palette": "pilar-brick", "_about": "warm red-brown brick"}]}
open(os.path.join(ROOT, "assets/finishes/el-pilar.json"), "w").write(json.dumps(fin, indent=2, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    print("el-pilar:", len(parts), "parts")
