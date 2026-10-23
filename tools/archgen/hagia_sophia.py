# HAGIA SOPHIA, Constantinople (532-37), at its real size, from the pieces of elements/byzantine.json: the 31m
# square between four piers and four great arches, the pendentives, the ring of forty windows and the ribbed
# dome; east and west the two semidomes on their half rings of windows, each over a two-storey half-ring arcade
# into the space behind it; the tympanum walls under the north and south arches; the aisles and, over them,
# the GALLERIES, walked on and reached by a stair along each outer wall; the narthex with its own gallery; the
# apse; the great buttresses; the four Ottoman minarets.
#   x runs across the church (north +x), z along it (east +z). Numbers are worked here and written as numbers.
#   (A `wall`'s thickness lies on the -z side of its placement -- the -x side, turned a quarter.)
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
Q = math.pi / 2

S, PIER, SPRING = 31.0, 5.0, 24.0                  # the square, its piers, the great arches' springing
R = S / 2
RING = SPRING + R                                  # the pendentives' top: the circle the dome's windows stand on
WIN, DOME_T, RISE = 4.5, 1.0, 11.5                 # the window ring, the dome's shell, how far it rises
GAL, ROOF, T = 13.0, 20.0, 1.5                     # the gallery floor, the aisle roofs, the outer walls
SLAB = 0.6
PC = R + PIER / 2                                  # the piers' middles
XA = R + PIER                                      # the aisles begin at the piers' outer faces
XO = XA + 14.0                                     # ...and run to the outer wall's inner face
ZO = 38.0                                          # the east and west walls' inner faces
RO = R + DOME_T                                    # the semidomes' half rings, outside
TY = 1.2                                           # the tympanum walls

# ---- the domed core
add("piers", {"type": "box", "width": PIER, "length": PIER, "height": SPRING,
              "at": [[sx * PC, 0, sz * PC, 0] for sx in (-1, 1) for sz in (-1, 1)],
              "_about": "the four great piers at the corners of the square"})
add("great arches", {"type": "barrel", "width": S, "length": PIER, "springing": SPRING, "top": RING + 1.5, "head": {"profile": "semicircular"},
                     "at": [[0, 0, -R, 0], [0, 0, R + PIER, 0], [-R, 0, 0, Q], [R + PIER, 0, 0, Q]],
                     "_about": "the four arches from pier to pier: their crowns carry the dome's ring"})
add("pendentives", {"type": "pendentives", "span": S, "springing": SPRING, "sides": 40, "at": [[0, 0, 0, 0]],
                    "_about": "the spherical triangles between the arches that turn the square into the dome's circle"})
add("dome", {"type": "component", "use": "components/drum-dome",
             "params": {"R": R, "dt": DOME_T, "H": WIN, "n": 40, "every": 1, "winW": 1.4, "winSill": 0.4, "winH": WIN - 1.4,
                        "profile": "segmental", "rise": RISE, "domeT": DOME_T, "ribW": 0.6},
             "build": ["drum", "dome", "ribs"], "at": [[0, RING, 0, 0]],
             "_about": "the ring of forty windows at the dome's foot -- the dome seems to float on light -- the dome, 31m across and rising less than a hemisphere, and its forty ribs"})

# ---- east and west: semidomes on half rings of windows, over two storeys of half-ring arcade
HALF = [0, 1, 2, 3, 4, 15, 16, 17, 18, 19]         # the bays of a ring of 20 that face away from the square
ENDS = [[0, 0, XA, 0], [0, 0, -XA, math.pi]]
half = lambda h, y, opening, **kw: {"type": "ring", "count": 20, "rOuter": RO, "rInner": R, "height": h, "y": y, "turn": 0.5,
                                    "at": HALF, "opening": opening, "place": ENDS, **kw}
add("exedra arcade", half(GAL, 0, {"width": 3.2, "sill": 0, "springing": 9.5, "head": {"profile": "semicircular"}},
                          _about="the ground storey of each half ring: arches into the space behind, under the gallery"))
add("exedra gallery", half(ROOF - GAL, GAL, {"width": 2.6, "sill": 1.0, "springing": 5.0, "head": {"profile": "semicircular"}}, glass=False,
                           _about="the gallery storey over it: open arches, their sills the gallery's parapet"))
add("semidome windows", half(SPRING - ROOF, ROOF, {"width": 1.6, "sill": 0.4, "springing": SPRING - ROOF - 1.0, "head": {"profile": "semicircular"}},
                             _about="the half ring of windows each semidome stands on, over the aisle roofs"))
add("semidomes", {"type": "dome", "sweep": 0.5, "sides": 20, "radius": RO, "thickness": DOME_T, "head": {"profile": "semicircular"},
                  "at": [[0, SPRING, XA, 0], [0, SPRING, -XA, math.pi]],
                  "_about": "the semidomes east and west, their crowns under the great arches': the nave is 70m long under one sweep of vaults"})

# ---- the tympanum walls under the north and south arches
add("tympana", {"type": "wall", "width": S, "height": RING, "thickness": TY, "at": [[PC + TY / 2, 0, 0, Q], [-PC + TY / 2, 0, 0, Q]],
                "tiers": [{"h": GAL, "openings": {"pattern": "5", "width": 3.2, "gap": 2.6, "sill": 0, "springing": 9.5, "head": {"profile": "semicircular"}}},
                          {"h": ROOF - GAL, "glass": False,
                           "openings": {"pattern": "7", "width": 2.2, "gap": 1.6, "sill": 1.0, "springing": 5.0, "head": {"profile": "semicircular"}}},
                          {"h": 9.0, "openings": {"pattern": "7", "width": 1.8, "gap": 1.8, "sill": 2.5, "springing": 6.5, "head": {"profile": "semicircular"}}},
                          {"openings": {"pattern": "5", "width": 1.6, "gap": 2.4, "sill": 1.5, "springing": 4.5, "head": {"profile": "semicircular"}}}],
                "_about": "the walls that close the north and south arches: an arcade to the aisle, the gallery's arcade, and two rows of windows in the lunette (the wall above the arch's curve is inside the arch)"})

# ---- the outer walls: aisles below, galleries above
win = lambda n, w, gap, sill, spring, **kw: {"pattern": str(n), "width": w, "gap": gap, "sill": sill, "springing": spring, "head": {"profile": "semicircular"}, **kw}
H = ROOF + SLAB + 0.6
add("outer walls", {"type": "enclosure", "plan": {"rect": [2 * (XO + T), 2 * (ZO + T)]}, "thickness": T, "height": H,
                    "tiers": [{"h": GAL, "openings": win(9, 1.8, 5.6, 4.0, 8.5)}, {"h": ROOF - GAL, "openings": win(9, 1.6, 5.8, 1.2, 4.5)}, {"openings": []}],
                    "faces": {"0": [{"h": GAL, "openings": [{"at": 0, "width": 11.0, "sill": 0, "springing": 7.0, "head": {"profile": "semicircular"}}]},
                                    {"h": ROOF - GAL, "openings": win(9, 1.6, 5.8, 1.2, 4.5)}, {"openings": []}],
                              "2": [{"h": GAL, "openings": win(9, 2.4, 3.2, 0, 5.0)}, {"h": ROOF - GAL, "openings": win(9, 1.6, 5.8, 0, 3.2, glass=False)}, {"openings": []}]},
                    "_about": "the walls round aisles and galleries: windows in both storeys; nine doors from the narthex (west), and the gallery doors over them; the apse's arch east"})

# ---- floors: the galleries (with a hatch where each stair comes up) and the roofs over them
def arc(r, z0, sgn):                              # the half ring's outside, a polygon of its own corners
    return [[round(r * math.cos(math.radians(a)), 4), round(z0 + sgn * r * math.sin(math.radians(a)), 4)] for a in range(180, -1, -18)]
def u_plan(sgn):                                  # round the semidome's half ring, out to the end wall and the aisles
    z0, z1 = sgn * XA, sgn * ZO
    return [[XA, z0], [XA, z1], [-XA, z1], [-XA, z0]] + arc(RO, z0, sgn)
def floors(y, name, hatch, **kw):
    boxes = []                                    # [x middle, width, z middle, length] on the north side, mirrored
    x0 = PC + TY / 2                              # from the tympanum, out to the wall
    if hatch:                                     # all but the stair's strip along the wall, where it comes up
        boxes += [[(x0 + XO - 2) / 2, XO - 2 - x0, 0, S], [XO - 1, 2, (-R - 8.2) / 2, R - 8.2], [XO - 1, 2, (R - 0.4) / 2, R + 0.4]]
    else:
        boxes += [[(x0 + XO) / 2, XO - x0, 0, S]]
    boxes += [[(XA + XO) / 2, XO - XA, sz * (R + ZO) / 2, ZO - R] for sz in (-1, 1)]
    k = 0
    for sx in (-1, 1):
        for (cx, w, cz, l) in boxes:
            k += 1
            add(f"{name} {k}", {"type": "box", "width": round(w, 4), "length": round(l, 4), "height": SLAB, "at": [[round(sx * cx, 4), y, round(cz, 4), 0]], **kw})
    for sgn, nm in ((1, "east"), (-1, "west")):
        add(f"{name} {nm}", {"type": "prism", "plan": {"points": u_plan(sgn)}, "height": SLAB, "at": [[0, y, 0, 0]], **kw})
floors(GAL - SLAB, "gallery floor", True)
floors(ROOF, "aisle roof", False, flatRoof=True)
parts["gallery floor 1"]["_about"] = "the galleries, walked on: over the aisles, round the semidomes' half rings, each with a hatch along the outer wall where its stair comes up"

# ---- the stairs to the galleries: along each outer wall, two flights and a landing between, on their soffits
for sx, nm in ((1, "north"), (-1, "south")):
    X = sx * (XO - 1)                             # (a staircase stands centred on its line)
    add(f"{nm} gallery stair", {"type": "staircase", "flight": 40, "width": 2.0, "run": 0.32, "rise": GAL / 80, "soffit": 0.35,
                                "landing": {"depth": 2.0, "then": [{"from": "ahead", "flight": 40, "width": 2.0}]},
                                "at": [[X, 0, -30.0, -Q]],
                                "_about": "up the aisle along its wall: a flight, a landing halfway, a flight on to a landing flush with the gallery floor"})
# ---- columns under and over the galleries
cz = [-30.0, -22.5, -7.5, 0.0, 7.5, 22.5, 30.0]
add("aisle columns", {"type": "column", "radius": 0.55, "height": GAL - SLAB, "sides": 12,
                      "at": [[sx * (XA + 7), 0, z, 0] for sx in (-1, 1) for z in cz], "_about": "the columns that carry the galleries"})
add("gallery columns", {"type": "column", "radius": 0.45, "height": ROOF - GAL, "sides": 12,
                        "at": [[sx * (XA + 7), GAL, z, 0] for sx in (-1, 1) for z in cz]})

# ---- the narthex, its gallery and roof
ND = 7.0
add("narthex front", {"type": "wall", "width": 2 * (XO + T), "height": H, "thickness": T, "at": [[0, 0, -ZO - T - ND, 0]],
                      "tiers": [{"h": GAL, "openings": win(5, 3.0, 8.0, 0, 5.5)}, {"h": ROOF - GAL, "openings": win(9, 1.6, 5.8, 1.2, 4.5)}, {"openings": []}],
                      "_about": "the narthex's west front: five doors, the windows of the west gallery over them"})
add("narthex ends", {"type": "wall", "width": ND, "height": H, "thickness": T, "openings": [],
                     "at": [[XO + T, 0, -ZO - T - ND / 2, Q], [-XO, 0, -ZO - T - ND / 2, Q]]})
add("narthex gallery", {"type": "box", "width": 2 * XO, "length": ND, "height": SLAB, "at": [[0, GAL - SLAB, -ZO - T - ND / 2, 0]],
                        "_about": "the west gallery over the narthex, through doors from the nave's"})
add("narthex roof", {"type": "box", "flatRoof": True, "width": 2 * XO, "length": ND, "height": SLAB, "at": [[0, ROOF, -ZO - T - ND / 2, 0]]})

# ---- the apse
AR, AT = 5.5, 1.5
add("apse", {"type": "component", "use": "components/apse",
             "params": {"R": AR, "T": AT, "H": 14.0, "n": 16, "winW": 1.4, "winSill": 6.0, "winH": 4.5, "domeT": AT},
             "at": [[0, 0, ZO + T, 0]], "_about": "the apse beyond the east wall, windows high in it, under its half dome (`apse`)"})

# ---- the great buttresses, north and south, in line with the piers
add("buttresses", {"type": "box", "width": XO + T + 2.5 - XA, "length": PIER, "height": 34.0 - ROOF - SLAB,
                   "at": [[sx * (XA + XO + T + 2.5) / 2, ROOF + SLAB, sz * PC, 0] for sx in (-1, 1) for sz in (-1, 1)],
                   "_about": "the great buttresses over the aisle roofs, carrying the thrust of the north and south arches out to the walls"})
add("buttress feet", {"type": "box", "width": 2.5, "length": PIER, "height": ROOF + SLAB,
                      "at": [[sx * (XO + T + 1.25), 0, sz * PC, 0] for sx in (-1, 1) for sz in (-1, 1)]})

# ---- the Ottoman minarets
add("minarets", {"type": "component", "use": "components/minaret", "params": {"h": 48, "r": 2.1, "balconies": 2},
                 "build": ["plinth", "shaft", "corbelling", "balcony", "parapet", "pencil cap"],
                 "at": [[sx * (XO + T + 6), 0, z, 0] for sx in (-1, 1) for z in (-ZO - T - ND - 4, ZO - 2)],
                 "_about": "the four Ottoman minarets, pencil-capped"})

doc = {"name": "Hagia Sophia",
       "_about": "HAGIA SOPHIA, Constantinople (532-37), at its real size and from the Byzantine kit (elements/byzantine.json): the 31m square between four piers and four great arches; PENDENTIVES turning it into the circle of forty windows the ribbed dome stands on, 55m up; east and west the SEMIDOMES on their own half rings of windows, each over a two-storey half-ring arcade opening into the space behind; the TYMPANUM walls closing the north and south arches, arcaded below and full of windows above; aisles and over them the GALLERIES, walked on, reached by a stair along each outer wall; the NARTHEX with nine doors into the nave and its own gallery; the APSE; the great BUTTRESSES; and the four Ottoman `minaret`s.",
       "params": {"detail": 4}, "base": {"height": 0.6, "steps": 2, "stepOut": 0.5, "margin": 3}, "railing": {"type": "stone"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/hagia-sophia.json"), "w").write(json.dumps(doc, indent=2) + "\n")
