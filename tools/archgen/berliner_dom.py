# BERLINER DOM, Berlin (Raschdorff, 1894-1905), neo-Renaissance/Baroque Revival, from components: the square
# preaching church under a flat roof walked on; inside, four piers and great arches carry pendentives and their deck;
# over the roof a round stylobate, and on it the `drum-dome` -- a PERISTYLE of 32 columns round the tall drum, the
# green copper dome, the lantern and its cross (~97m); at the four corners of the roof a square tower stage, each under
# a small copper dome on a colonnaded drum with its lantern; the main front (+z, the Lustgarten) with a deep
# round-arched portal niche in a projecting centre, framed by paired giant Corinthian columns, the attic over it with
# its pediment and statues; the lower side wings (the Tauf- und Traukirche and the Denkmalskirche) either side.
# A `tower-stair` climbs from the church to the roof in the +x +z corner tower, whose stage opens onto the roof walk;
# a flight goes on from the roof to the gallery round the drum, inside the colonnade, which visitors walk.
#   Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2

BW, BL, T, BH = 72.0, 72.0, 2.5, 30.0      # the church: across (x), along (z), walls, the roof's underside
RT = BH + 0.4                              # the roof walk's top (and the body walls' top)
IX, IZ = BW / 2 - T, BL / 2 - T            # its inside, half
TW, TP = 13.0, 0.3                         # the corner towers: square, rising from the ground, standing TP proud of the fronts
TX, TZ = BW / 2 + TP - TW / 2, BL / 2 + TP - TW / 2    # a corner tower's middle (+x +z)
SW = TW - 2 * T                            # its inside (the stair's square in the front east one)
IN = BW / 2 + TP - TW                      # where the towers begin, from the middle (the roof is cut round them)
win1 = {"width": 2.4, "sill": 4.5, "springing": 11.0, "head": {"profile": "semicircular"}}
win2 = {"width": 2.2, "sill": 3.0, "springing": 9.5, "head": {"profile": "semicircular"}}
side = lambda door: [{"h": 15, "openings": {"pattern": "7", "gap": 5.4, **win1, **({"middle": {"width": 4.0, "sill": 0, "springing": 7.0, "glass": False}} if door else {})}},
                     {"openings": {"pattern": "7", "gap": 5.6, **win2}}]
FW, FD = 30.0, 4.0                         # the projecting centre of the front: its width, how far it stands out
fx = [16.0, 22.0]                          # the front's windows either side of the centre
add("body", {"type": "enclosure", "plan": {"rect": [BW, BL]}, "thickness": T, "height": RT,
             "faces": {"0": [{"h": 15, "openings": [{"at": 0, "width": 5.0, "sill": 0, "springing": 8.5, "head": {"profile": "semicircular"}, "glass": False}]
                                                     + [{"at": s * x, **win1} for x in fx for s in (-1, 1)]},
                             {"openings": [{"at": 0, "width": 3.2, "sill": 2.0, "springing": 6.5, "head": {"profile": "semicircular"}}] + [{"at": s * x, **win2} for x in fx for s in (-1, 1)]}],
                       "1": side(True), "3": side(True), "2": side(False)},
             "at": [[0, 0, 0, 0]], "_about": "the preaching church: two storeys of round-headed windows, the great door behind the portal niche, a door into either wing"})

# ---- inside: the crossing -- four piers, four great arches, the pendentives and their deck
S, PR = 34.0, 3.0                          # the square under the dome, the piers
SPR = BH - S / 2
add("piers", {"type": "box", "width": PR, "length": PR, "height": SPR,
              "at": [[sx * (S / 2 + PR / 2), 0, sz * (S / 2 + PR / 2), 0] for sx in (-1, 1) for sz in (-1, 1)],
              "_about": "the four great piers under the dome"})
add("great arches", {"type": "barrel", "width": S, "length": PR, "springing": SPR, "top": RT, "head": {"profile": "semicircular"},
                     "at": [[0, 0, -S / 2, 0], [0, 0, S / 2 + PR, 0], [-S / 2, 0, 0, Q], [S / 2 + PR, 0, 0, Q]],
                     "_about": "the arches from pier to pier"})
N = 32
add("pendentives", {"type": "pendentives", "span": S, "springing": SPR, "sides": N, "at": [[0, 0, 0, 0]], "deck": {"thickness": 0.4, "out": PR},
                    "_about": "the pendentives, and the roof round the drum's foot"})

# ---- the roof, walked on, round the crossing's deck and between the four corner towers
R0 = S / 2 + PR
add("roof", {"walked": True, "type": "box", "width": 2 * IX, "length": IN - R0, "height": 0.4, "at": [[0, BH, sz * (IN + R0) / 2, 0] for sz in (-1, 1)],
             "_about": "the flat roof, walked on: round the dome's deck, between the corner towers"})
add("roof ends", {"walked": True, "type": "box", "width": 2 * IN, "length": IZ - IN, "height": 0.4, "at": [[0, BH, sz * (IZ + IN) / 2, 0] for sz in (-1, 1)]})
add("roof sides", {"walked": True, "type": "box", "width": IX - R0, "length": 2 * R0, "height": 0.4, "at": [[sx * (IX + R0) / 2, BH, 0, 0] for sx in (-1, 1)]})
add("parapet", {"type": "enclosure", "plan": {"rect": [BW, BL]}, "thickness": 0.6, "height": 1.1, "at": [[0, RT, 0, 0]],
                "_about": "the parapet round the roof walk"})

# ---- the four corner towers, from the ground: open to the church by arches, a floor at the roof's level with doors onto the
# roof walk, windows over it; the front east one holds the stair (`tower-stair`, its turret in the corner toward the church)
TH = 14.0
arch = [{"at": 0, "width": 4.0, "sill": 0, "springing": 6.0, "head": {"profile": "semicircular"}, "glass": False}]
tdoor = [{"at": 0, "width": 1.4, "sill": 0, "springing": 2.4, "head": {"profile": "semicircular"}, "glass": False}]
twin = [{"at": 0, "width": 1.8, "sill": 1.6, "springing": 6.0, "head": {"profile": "semicircular"}}]
lwin = [{"at": 0, "width": 2.2, "sill": 5.0, "springing": 11.0, "head": {"profile": "semicircular"}}]
towers = []
for sx in (-1, 1):
    for sz in (-1, 1):
        inner = {"1" if sx < 0 else "3", "2" if sz > 0 else "0"}   # the faces toward the church (0 +z, 1 +x, 2 -z, 3 -x)
        faces = {str(f): [{"h": RT, "openings": arch if str(f) in inner else lwin}, {"h": 3.2, "openings": tdoor if str(f) in inner else []},
                          {"openings": twin}] for f in range(4)}
        name = "corner tower " + ("front" if sz > 0 else "back") + (" east" if sx > 0 else " west")
        add(name, {"type": "enclosure", "plan": {"rect": [TW, TW]}, "thickness": T, "height": RT + TH, "faces": faces,
                   "at": [[sx * TX, 0, sz * TZ, 0]], "_about": "a corner tower from the ground: arches into the church, a door onto the roof walk, windows over"})
        towers.append([sx * TX, sz * TZ])
        if not (sx > 0 and sz > 0):
            add(name + " floor", {"type": "box", "width": SW, "length": SW, "height": 0.4, "at": [[sx * TX, BH, sz * TZ, 0]],
                                  "_about": "the tower's floor at the roof's level, its doors onto the roof walk"})
c = SW / 2 - 2.1 - 0.05
add("roof stair", comp("components/tower-stair", {"W": SW, "H": RT, "tR": 2.1, "tx": -c, "tz": -c}, [[TX, 0, TZ, 0]],
                       _about="the stair in the front east tower: its turret in the corner toward the church, the spiral to the roof's level and the tower's floor round its head"))
HD = 0.6
add("tower heads", {"type": "box", "width": TW, "length": TW, "height": HD, "flatRoof": True,
                    "at": [[x, RT + TH, z, 0] for x, z in towers], "_about": "the slab over each tower, the small dome's floor"})
add("tower domes", comp("components/drum-dome", {"R": 3.6, "dt": 0.6, "H": 6.5, "n": 8, "every": 2, "winW": 1.0, "winSill": 1.0, "winH": 2.8,
                                                 "profile": "pointed", "spread": 0.5, "domeT": 0.3, "colN": 8, "colR": 0.32, "colH": 5.4, "pw": 1.3,
                                                 "lanternR": 1.1, "lanternH": 3.8},
                        [[x, RT + TH + HD, z, 0] for x, z in towers], build=["drum", "drum piers", "peristyle", "peristyle deck", "dome", "lantern"],
                        _about="on each corner tower a copper dome on a colonnaded drum, and its lantern"))

# ---- the great dome: the stylobate over the roof, the drum-dome with its peristyle, the lantern and the cross
SB = 6.0                                   # the stylobate: the drum's own base, only a walk's width round its colonnade
DR, DT, DH, LR, LH = S / 2, 1.5, 26.0, 4.0, 14.0
PW = 1.4                                   # (the columns close against the drum, in the real one's paired rhythm: no broad deck over them)
BR = DR + DT + PW + 2.8                     # (a 2m walk round the outside of the colonnade, at its foot)
add("stylobate", {"walked": True, "type": "ring", "count": N, "rOuter": BR, "rInner": S / 2, "height": SB, "y": BH, "turn": 0.5, "solid": True, "place": [[0, 0, 0, 0]],
                  "_about": "the round base the colonnade stands on: its top is the gallery walked round the drum"})
steps = round((BH + SB - RT) / 0.16)
add("gallery stair", {"type": "flight", "width": 3.0, "run": 0.3, "rise": 0.16, "base": RT, "top": BH + SB, "landing": 0,
                      "at": [[1.5, 0, BR + steps * 0.3, Q]], "_about": "the flight from the roof walk up onto the gallery round the drum"})
add("dome", comp("components/drum-dome", {"R": DR, "dt": DT, "H": DH, "n": N, "every": 2, "winW": 2.2, "winSill": 4.0, "winH": 9.0,
                                          "profile": "pointed", "spread": 0.7, "domeT": 1.2, "colN": N, "colR": 0.8, "colH": 21.0, "pw": PW,
                                          "lanternR": LR, "lanternH": LH},
                 [[0, BH + SB, 0, 0]], build=["drum", "drum piers", "peristyle", "peristyle deck", "dome", "ribs", "lantern"],
                 _about="the drum and its peristyle of 32 columns, the copper dome and its ribs, the lantern"))
# ---- the main front: the portal niche in the projecting centre, paired giant columns, the attic, pediment, statues
FZ = BL / 2 + FD
add("frontispiece", {"type": "wall", "width": FW, "thickness": FD, "height": RT,
                     "tiers": [{"h": RT, "openings": [{"at": 0, "width": 14.0, "sill": 0, "springing": 19.0, "head": {"profile": "semicircular"}, "glass": False}]}],
                     "at": [[0, 0, FZ, 0]], "_about": "the projecting centre of the front, the great round-arched portal niche through it"})
CR, CH, EH = 0.9, 20.0, 2.5
for s, n in ((-1, "west"), (1, "east")):
    add("paired columns " + n, {"type": "colonnade", "order": "corinthian", "count": 2, "spacing": 2.8, "columnR": CR, "height": CH, "taper": 0.86,
                                "entablature": {"h": EH, "depth": CR * 2.6}, "at": [[s * 10.4, 0, FZ + CR * 1.3, 0]],
                                "_about": "a pair of giant Corinthian columns beside the portal niche"})
AH = 5.0
add("attic", {"type": "box", "width": FW, "length": FD, "height": AH, "flatRoof": True, "at": [[0, RT, BL / 2 + FD / 2, 0]],
              "_about": "the attic over the portal"})
add("pediment", {"type": "roof", "form": "gable", "width": 18.0, "length": FD, "pitch": 20, "overhang": 0.3, "at": [[0, RT + AH, BL / 2 + FD / 2, 0]],
                 "_about": "the pediment crowning the attic"})
ped = [[s * x, RT + AH, BL / 2 + FD / 2, 0] for x in (11.8, 14.0) for s in (-1, 1)] + [[s * 10.4, CH + EH, FZ + CR * 1.3, 0] for s in (-1, 1)]
add("statue pedestals", {"type": "box", "width": 1.2, "length": 1.2, "height": 1.0, "at": ped, "_about": "pedestals on the attic and over each pair of columns"})
add("statues", {"type": "column", "radius": 0.35, "height": 2.4, "sides": 8, "at": [[x, y + 1.0, z, 0] for x, y, z, _ in ped], "_about": "the statues"})

# ---- the side wings, lower, against the church's flanks: a door from the church and one from outside
WW, WL, WH, WT = 16.0, 40.0, 14.0, 1.5
wwin = {"width": 2.2, "sill": 2.5, "springing": 8.0, "head": {"profile": "semicircular"}}
for s, n in ((1, "south"), (-1, "north")):
    x0 = s * BW / 2
    add(n + " wing outer wall", {"type": "wall", "width": WL, "thickness": WT, "height": WH,
                                 "openings": {"pattern": "7", "gap": 3.2, **wwin, "middle": {"width": 3.0, "sill": 0, "springing": 5.0, "glass": False}},
                                 "at": [[x0 + s * WW, 0, 0, Q if s > 0 else -Q]], "_about": "the wing's outer wall, a door in its middle"})
    ew = WW - WT
    add(n + " wing end walls", {"type": "wall", "width": ew, "thickness": WT, "height": WH, "openings": {"pattern": "2", "gap": 5.0, **wwin},
                                "at": [[x0 + s * ew / 2, 0, WL / 2, 0], [x0 + s * ew / 2, 0, -WL / 2, math.pi]], "_about": "its front and back walls"})
    add(n + " wing roof", {"type": "box", "width": WW, "length": WL, "height": 0.6, "flatRoof": True, "at": [[x0 + s * WW / 2, WH, 0, 0]],
                           "_about": "the wing's flat roof"})
    add(n + " wing parapet", {"type": "enclosure", "plan": {"rect": [WW, WL]}, "thickness": 0.5, "height": 1.0, "at": [[x0 + s * WW / 2, WH + 0.6, 0, 0]],
                              "_about": "its parapet"})

doc = {"name": "Berliner Dom",
       "_about": "BERLINER DOM, Berlin (1894-1905), neo-Renaissance/Baroque Revival, from components: the square preaching church under a flat roof walked on; inside, four piers and great arches carrying pendentives; over the roof a round stylobate, and on it the `drum-dome` -- a PERISTYLE of 32 columns round the tall drum, the green copper dome with its ribs, the lantern and the cross (~97m); four corner tower stages on the roof, each under a small copper dome on a colonnaded drum; the Lustgarten front with its deep round-arched portal niche between paired giant Corinthian columns, the attic, pediment and statues; the lower side wings. A `tower-stair` in the +x +z corner tower climbs to the roof, and a flight on to the gallery round the drum.",
       "params": {"detail": 4}, "base": {"height": 0.8, "steps": 4, "stepOut": 0.5, "margin": 4}, "railing": {"type": "balusters"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/berliner-dom.json"), "w").write(json.dumps(doc, indent=2) + "\n")
