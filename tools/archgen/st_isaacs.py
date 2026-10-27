# ST ISAAC'S CATHEDRAL, St Petersburg (Montferrand, 1818-58), from components: a great rectangular body under a flat
# roof, walked on; inside, four piers and great arches carry pendentives and their deck; over the roof a round
# stylobate, and on it the `drum-dome` -- a PERISTYLE of 24 columns round the drum, the gilded dome, the lantern; on
# each of the four fronts an octastyle `portico`, the body's walls a giant order of pilasters carrying the porticoes'
# entablature round the building; four small gilded domes (`drum-dome` again, with a peristyle of eight)
# on square bases at the roof's corners. A `tower-stair` climbs to the roof in one corner, and a flight from the roof
# to the colonnade round the drum, which visitors walk.
#   The main front faces +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2

BW, BL, T, BH = 60.0, 76.0, 2.5, 30.0      # the body: across (x), along (z), walls, height
IX, IZ = BW / 2 - T, BL / 2 - T            # its inside, half
# THE WALLS' GRAMMAR: a GIANT CORINTHIAN ORDER of pilasters through the two storeys of windows, its entablature at the
# porticoes' (their columns' foot over four steps, 17 m of column, 3 m of entablature), and an ATTIC over it to the roof
# -- the pilasters on the piers between the window axes (order.js), the windows dressed: the lower row under triangular
# pediments, the upper under cornices, the attic's plain (surround.js), a granite plinth (courses)
OT = 0.8 + 17.0 + 3.0                      # the order's top: the porticoes' entablature's
front = lambda n: [{"h": OT / 2, "openings": {"pattern": str(n), "width": 2.6, "gap": 6.4, "sill": 3.0, "springing": 7.4, "head": {"profile": "semicircular"},
                                              "surround": {"head": "pediment"}, "middle": {"width": 5.0, "sill": 0, "springing": 7.4}}},
                   {"h": OT / 2, "openings": {"pattern": str(n), "width": 2.2, "gap": 6.8, "sill": 2.0, "springing": 6.6, "head": {"profile": "semicircular"},
                                              "surround": {"head": "cornice"}}},
                   {"openings": {"pattern": str(n), "width": 2.2, "gap": 6.8, "sill": 2.4, "springing": 5.2, "surround": {"head": False}}}]
add("body", {"type": "enclosure", "plan": {"rect": [BW, BL]}, "thickness": T, "height": BH,
             "faces": {"0": front(5), "2": front(5), "1": front(7), "3": front(7)},
             "courses": {"plinth": {"h": 1.4, "out": 0.35}}, "orders": [{"tier": 0, "span": 2, "kind": "corinthian"}],
             "at": [[0, 0, 0, 0]], "_about": "the body: a giant Corinthian order of pilasters through two storeys of dressed windows, its entablature at the porticoes', an attic over it; a great door in the middle of every front, behind its portico"})

# ---- inside: the crossing -- four piers, four great arches, the pendentives and their deck
S = 26.0                                   # the square under the dome
PR = 3.0
SPR = BH - S / 2
add("piers", {"type": "box", "width": PR, "length": PR, "height": SPR,
              "at": [[sx * (S / 2 + PR / 2), 0, sz * (S / 2 + PR / 2), 0] for sx in (-1, 1) for sz in (-1, 1)],
              "_about": "the four great piers under the dome"})
add("great arches", {"type": "barrel", "width": S, "length": PR, "springing": SPR, "top": BH + 0.4, "head": {"profile": "semicircular"},
                     "at": [[0, 0, -S / 2, 0], [0, 0, S / 2 + PR, 0], [-S / 2, 0, 0, Q], [S / 2 + PR, 0, 0, Q]],
                     "_about": "the arches from pier to pier"})
add("pendentives", {"type": "pendentives", "span": S, "springing": SPR, "sides": 24, "at": [[0, 0, 0, 0]], "deck": {"thickness": 0.4, "out": PR},
                    "_about": "the pendentives, and the roof round the drum's foot"})
# ---- the roof: walked on, round the crossing's deck; the corner the stair comes up in is the stair's own floor
R0 = S / 2 + PR                            # the deck reaches this far from the middle
SW = 8.0                                   # the stair's corner, +x +z
add("roof", {"walked": True, "type": "box", "width": 2 * IX, "length": IZ - R0, "height": 0.4, "at": [[0, BH, -(IZ + R0) / 2, 0]],
             "_about": "the flat roof, walked on: round the dome's deck, but for the corner the stair arrives in"})
add("roof front", {"walked": True, "type": "box", "width": 2 * IX - SW, "length": IZ - R0, "height": 0.4, "at": [[-SW / 2, BH, (IZ + R0) / 2, 0]]})
add("roof front corner", {"walked": True, "type": "box", "width": SW, "length": IZ - R0 - SW, "height": 0.4, "at": [[IX - SW / 2, BH, R0 + (IZ - R0 - SW) / 2, 0]]})
add("roof sides", {"walked": True, "type": "box", "width": IX - R0, "length": 2 * R0, "height": 0.4, "at": [[sx * (IX + R0) / 2, BH, 0, 0] for sx in (-1, 1)]})
add("roof stair", comp("components/tower-stair", {"W": SW, "H": BH + 0.4}, [[IX - SW / 2, 0, IZ - SW / 2, 0]],
                       _about="the stair to the roof, in the body's corner: its turret and spiral, and the corner of the roof round its head"))

# ---- the dome: the stylobate over the roof, the drum-dome with its peristyle
SB, BR = 5.0, 21.0
add("stylobate", {"walked": True, "type": "ring", "count": 24, "rOuter": BR, "rInner": S / 2, "height": SB, "y": BH, "turn": 0.5, "solid": True, "place": [[0, 0, 0, 0]],
                  "_about": "the round base the colonnade stands on: its top is the gallery walked round the drum"})
add("colonnade stair", {"type": "flight", "width": 3.0, "run": 0.3, "rise": 0.16, "base": BH + 0.4, "top": BH + SB, "landing": 0,
                        "at": [[1.5, 0, BR + round((SB - 0.4) / 0.16) * 0.3, Q]], "_about": "the flight from the roof up onto the colonnade's gallery"})
add("dome", comp("components/drum-dome", {"R": S / 2, "dt": 1.5, "H": 22.0, "n": 24, "every": 2, "winW": 2.0, "winSill": 4.0, "winH": 8.0,
                                          "profile": "pointed", "spread": 0.3, "domeT": 1.2, "colN": 24, "colR": 0.95, "colH": 17.0, "pw": 3.8,
                                          "lanternR": 3.0, "lanternH": 12.0},
                 [[0, BH + SB, 0, 0]], build=["drum", "drum piers", "peristyle", "peristyle deck", "dome", "lantern"],
                 _about="the drum and its peristyle of 24 columns, the gilded dome and the lantern"))

# ---- the four porticoes
por = {"count": 8, "spacing": 3.9, "colR": 0.95, "colH": 17.0, "entH": 3.0, "depth": 12.0, "order": "corinthian", "pitch": 16, "sideCount": 2}
add("porticoes", comp("components/portico", por, [[0, 0, BL / 2, 0], [0, 0, -BL / 2, math.pi], [BW / 2, 0, 0, Q], [-BW / 2, 0, 0, -Q]],
                      build=["steps", "columns", "side columns", "pediment"],
                      _about="an octastyle portico on every front, its columns in granite, under a pediment"))

# ---- the four small domes at the corners
add("belfry bases", {"flatRoof": True, "type": "box", "width": 8.0, "length": 8.0, "height": 6.0,
                     "at": [[sx * (IX - 4.5), BH + 0.4, sz * (IZ - 4.5 - (SW if sx > 0 and sz > 0 else 0)), 0] for sx in (-1, 1) for sz in (-1, 1)],
                     "_about": "the four belfries' square bases on the roof's corners (the one by the stair set in from it)"})
add("belfries", comp("components/drum-dome", {"R": 2.4, "dt": 0.5, "H": 4.5, "n": 8, "every": 2, "winW": 0.8, "winSill": 0.8, "winH": 2.0,
                                              "profile": "semicircular", "domeT": 0.3, "colN": 8, "colR": 0.28, "colH": 3.7, "pw": 0.9,
                                              "lanternR": 0.7, "lanternH": 2.2},
                     [[sx * (IX - 4.5), BH + 6.4, sz * (IZ - 4.5 - (SW if sx > 0 and sz > 0 else 0)), 0] for sx in (-1, 1) for sz in (-1, 1)],
                     build=["drum", "drum piers", "peristyle", "peristyle deck", "dome", "lantern"], _about="and on each a small gilded dome on a colonnaded drum"))

doc = {"name": "St Isaac's Cathedral",
       "_about": "ST ISAAC'S CATHEDRAL, St Petersburg (1818-58), from components: the great body under a flat roof walked on; inside, four piers and great arches carrying pendentives and their deck; over the roof a round stylobate, and on it the `drum-dome` -- a PERISTYLE of 24 columns, the gilded dome, the lantern; an octastyle `portico` on each of the four fronts; four small gilded domes on colonnaded drums at the roof's corners; a `tower-stair` to the roof in one corner, and a flight on up to the colonnade round the drum.",
       "params": {"detail": 4}, "base": {"height": 0.8, "steps": 4, "stepOut": 0.5, "margin": 4}, "railing": {"type": "iron"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/st-isaacs.json"), "w").write(json.dumps(doc, indent=2) + "\n")
