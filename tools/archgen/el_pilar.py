# THE BASILICA OF OUR LADY OF THE PILLAR (El Pilar), Zaragoza (Baroque, 1681-1872), from components: a long brick
# HALL CHURCH of three naves of one height -- seven bays of square vaulted compartments on two rows of piers, the
# arches from pier to pier -- whose roof is crowned by ELEVEN DOMES of glazed tiles: the great central dome on its
# tall windowed drum, six smaller ones down the middle nave and four over the aisles, each a `drum-dome` (a low drum,
# the dome, its lantern) on PENDENTIVES over its bay; the bays without a dome have flat ceilings and, over the aisles,
# low hipped roofs. At the four corners a `baroque-tower` -- shaft, open belfry, chamfered upper stage, bulbous cap
# and lantern -- engaged in the body's corner; the one on the square's east corner is climbed by its `tower-stair` to
# the belfry, open all round (the real one has a lift to its viewpoint). Portals framed by a pair of columns and a
# pediment (`portico`) on the long side facing the Plaza del Pilar (+z), doors at both ends and toward the river.
#   The long axis is x. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2
r2 = lambda v: round(v, 3)

S, P = 15.5, 3.0                           # a bay (square) and a pier
B = S + P                                  # the bay spacing
NX, NZ = 7, 3                              # bays along (x) and across (z): three naves of one width
T = 2.2                                    # the brick walls
IX, IZ = 3 * B + S / 2, B + S / 2          # the inside, half: 63.25 x 26.25
L, W = 2 * (IX + T), 2 * (IZ + T)          # the body outside: 130.9 x 56.9
RH = 25.0                                  # the crowns of the arches, pendentives and ceilings
SPR = RH - S / 2                           # where the arches and pendentives spring
TH = 0.4                                   # the ceilings' and decks' thickness
WH = RH + TH + 1.8                         # the walls, their parapet over the roofs
bx = lambda i: i * B
bz = lambda j: j * B
DOMES = [(i, 0) for i in range(-3, 4)] + [(i, j) for i in (-2, 2) for j in (-1, 1)]
FLAT = [(i, j) for i in range(-3, 4) for j in (-1, 1) if (i, j) not in DOMES]

# ---- the body: the brick walls round the plan, doors and two tiers of windows
TE = 0.8                                   # the towers stand this far proud of the body at its corners
TW = 14.0                                  # the towers' shafts
TT = T + TE                                # their walls: the body's corners are buried in them
TX, TZ = L / 2 + TE - TW / 2, W / 2 + TE - TW / 2   # the towers' middles
doors_front = {-2: 4.0, 0: 5.0, 2: 4.0}     # the portals on the square, by bay: their widths
door = lambda at, w: {"at": at, "width": w, "sill": 0, "springing": 7.0 if w < 5 else 8.0, "head": {"profile": "semicircular"}}
win_low = lambda at: {"at": at, "width": 2.2, "sill": 4.5, "springing": 8.5, "head": {"profile": "semicircular"}}
win_high = lambda at: {"at": at, "width": 2.6, "sill": 3.0, "springing": 9.5, "head": {"profile": "semicircular"}}
LOW = 12.0
long_bays = [bx(i) for i in range(-2, 3)]  # (the end bays are the towers')
front = [{"h": LOW, "openings": [door(bx(i), doors_front[i]) if i in doors_front else win_low(bx(i)) for i in range(-2, 3)]},
         {"openings": [win_high(a) for a in long_bays]}]
back = [{"h": LOW, "openings": [door(0, 4.0) if i == 0 else win_low(bx(i)) for i in range(-2, 3)]},
        {"openings": [win_high(a) for a in long_bays]}]
end = [{"h": LOW, "openings": [door(0, 4.0)]}, {"openings": [win_high(0)]}]
add("body", {"type": "enclosure", "plan": {"rect": [r2(L), r2(W)]}, "thickness": T, "height": r2(WH),
             "faces": {"0": front, "1": end, "2": back, "3": end}, "at": [[0, 0, 0, 0]],
             "_about": "the body: red-brown brick walls round the long rectangle, three doors on the square (+z), one toward the river and one at each end, two tiers of arched windows"})
add("cornice", {"type": "enclosure", "plan": {"rect": [r2(L + 0.8), r2(W + 0.8)]}, "thickness": 0.7, "height": 0.6, "at": [[0, r2(WH - 0.6), 0, 0]],
                "standsOn": ["body"], "_about": "the stone cornice crowning the walls (its ends buried in the towers)"})

# ---- inside: the hall of piers, the arches from pier to pier
add("piers", {"type": "box", "width": P, "length": P, "height": r2(SPR),
              "at": [[r2(bx(i) + B / 2), 0, r2(sz * B / 2), 0] for i in range(-3, 3) for sz in (-1, 1)],
              "_about": "the two rows of piers down the hall"})
add("wall piers", {"type": "box", "width": P, "length": 1.0, "height": r2(SPR),
                   "at": [[r2(bx(i) + B / 2), 0, r2(sz * (IZ - 0.5)), 0] for i in range(-3, 3) for sz in (-1, 1)] +
                         [[r2(sx * (IX - 0.5)), 0, r2(sz * B / 2), Q] for sx in (-1, 1) for sz in (-1, 1)],
                   "_about": "pilasters on the walls, where the arches land"})
arch = {"type": "barrel", "width": S, "length": P, "springing": r2(SPR), "top": r2(RH + TH), "head": {"profile": "semicircular"}}
add("arches", {**arch, "at": [[r2(bx(i)), 0, r2(sz * B / 2 + P / 2), 0] for i in range(-3, 4) for sz in (-1, 1)],
               "_about": "the arches along the naves, from pier to pier"})
add("cross arches", {**arch, "at": [[r2(bx(i) + B / 2 + P / 2), 0, r2(bz(j)), Q] for i in range(-3, 3) for j in (-1, 0, 1)],
                     "_about": "the arches across the naves"})

# ---- the domed bays: pendentives and their decks, and on each a drum and dome
add("central pendentives", {"type": "pendentives", "span": S, "springing": r2(SPR), "sides": 16, "deck": {"thickness": TH, "out": P / 2},
                            "at": [[0, 0, 0, 0]], "_about": "pendentives over the domed bays, and the roof round each drum's foot (its polygon the drum's)"})
add("pendentives", {"type": "pendentives", "span": S, "springing": r2(SPR), "sides": 12, "deck": {"thickness": TH, "out": P / 2},
                    "at": [[r2(bx(i)), 0, r2(bz(j)), 0] for i, j in DOMES if (i, j) != (0, 0)]})
# ---- the flat bays: a ceiling each (cut round the towers in the corners)
tiles = []
for i, j in FLAT:
    x0, x1 = bx(i) - B / 2, bx(i) + B / 2
    z0, z1 = bz(j) - B / 2, bz(j) + B / 2
    x0, x1, z0, z1 = max(x0, -IX), min(x1, IX), max(z0, -IZ), min(z1, IZ)
    if abs(i) == 3:                        # the corner bay: the tower stands in its outer corner
        sx, sz = (1 if i > 0 else -1), (1 if j > 0 else -1)
        tin_x, tin_z = TX - TW / 2, TZ - TW / 2      # the tower's inner faces, from the middle (+x +z corner)
        # the strip along the nave, the whole bay long; and the strip along the end, from it to the wall
        ax0, ax1 = sorted((sx * (B * 2.5), sx * IX))
        az0, az1 = sorted((sz * B / 2, sz * tin_z))
        tiles.append((ax0, ax1, az0, az1))
        bx0, bx1 = sorted((sx * (B * 2.5), sx * tin_x))
        bz0, bz1 = sorted((sz * tin_z, sz * IZ))
        tiles.append((bx0, bx1, bz0, bz1))
    else:
        tiles.append((x0, x1, z0, z1))
ceil_parts = {}
for (x0, x1, z0, z1) in tiles:
    k = (r2(x1 - x0), r2(z1 - z0))
    ceil_parts.setdefault(k, []).append([r2((x0 + x1) / 2), r2(RH), r2((z0 + z1) / 2), 0])
for n, ((w, l), at) in enumerate(sorted(ceil_parts.items())):
    add(f"ceiling {n + 1}", {"type": "box", "width": w, "length": l, "height": TH, "at": at,
                             **({"_about": "the flat ceilings of the bays without a dome, and the roof over them"} if n == 0 else {})})
AR = 3 * B                                 # the aisles' hipped roofs over their three middle bays
add("aisle roofs", {"type": "roof", "form": "hip", "width": r2(B - P / 2 + 0.3), "length": r2(AR - P), "pitch": 28,
                    "at": [[0, r2(RH + TH), r2(sz * (B / 2 + (B - P / 2) / 2 - 0.15)), Q] for sz in (-1, 1)],
                    "_about": "low hipped roofs of tiles over the aisles' middle bays"})

# ---- the eleven domes
CD = {"R": S / 2, "dt": 1.0, "H": 14.0, "n": 16, "every": 2, "winW": 1.8, "winSill": 3.0, "winH": 5.5, "profile": "pointed", "spread": 0.85,
      "domeT": 0.8, "lanternR": 2.0, "lanternH": 7.5}
add("central dome", comp("components/drum-dome", CD, [[0, r2(RH + TH), 0, 0]], build=["drum", "drum piers", "dome", "lantern"],
                         _about="the great central dome: a tall drum with a window in every other bay, the tiled dome, the lantern"))
SD = {"R": S / 2, "dt": 0.8, "H": 3.6, "n": 12, "every": 2, "winW": 1.2, "winSill": 0.9, "winH": 1.4, "profile": "semicircular",
      "domeT": 0.6, "lanternR": 1.1, "lanternH": 3.6}
add("nave cupolas", comp("components/drum-dome", SD, [[r2(bx(i)), r2(RH + TH), 0, 0] for i in (-3, -2, -1, 1, 2, 3)],
                         build=["drum", "drum piers", "dome", "lantern"], _about="six cupolas down the middle nave: low drums, tiled domes, lanterns"))
add("aisle cupolas", comp("components/drum-dome", {**SD, "H": 2.8, "winSill": 0.6, "winH": 1.2, "lanternH": 3.0},
                          [[r2(bx(i)), r2(RH + TH), r2(bz(j)), 0] for i in (-2, 2) for j in (-1, 1)],
                          build=["drum", "drum piers", "dome", "lantern"], _about="and four over the aisles, lower"))

# ---- the four corner towers
TH_ = 42.0                                 # the belfry's floor
tower = {"W": TW, "t": TT, "H": TH_, "lowH": r2(WH), "doorW": 1.6, "doorH": 3.2, "winW": 1.4, "s": 0.8, "BH": 11.0, "archW": 3.8, "archSill": 1.0,
         "W3": 9.6, "t3": 0.9, "H3": 8.0, "capR": 5.0, "profile": "onion", "bulge": 1.15, "neck": 0.8, "lanternR": 1.5, "lanternH": 6.0, "tR": 2.2}
seats = {(1, 1): math.pi, (-1, 1): math.pi, (1, -1): 0, (-1, -1): 0}   # the door toward the church (-z for the front pair)
add("climbed tower", comp("components/baroque-tower", tower, [[r2(TX), 0, r2(TZ), seats[(1, 1)]]],
                          build=["shaft", "stair", "cornice", "belfry", "belfry head", "upper stage", "upper head", "cap", "lantern"],
                          _about="the east tower on the square, climbed: its door from the church, the stair up the shaft to the open belfry"))
add("towers", comp("components/baroque-tower", tower, [[r2(sx * TX), 0, r2(sz * TZ), seats[(sx, sz)]] for (sx, sz) in seats if (sx, sz) != (1, 1)],
                   build=["shaft", "belfry floor", "cornice", "belfry", "belfry head", "upper stage", "upper head", "cap", "lantern"],
                   _about="the other three corner towers"))

# ---- the portals on the square: a pair of columns, the entablature and a pediment round each door
for i, w in doors_front.items():
    big = w >= 5
    add(f"portal {i + 3}", comp("components/portico", {"count": 2, "spacing": r2(w + 2.6), "colR": 0.55 if big else 0.45, "colH": 11.0 if big else 9.5,
                                                       "entH": 1.4, "depth": 1.8, "order": "corinthian", "pitch": 24, "steps": 1, "stepH": 0.2},
                                [[r2(bx(i)), 0, r2(W / 2), 0]], build=["steps", "columns", "pediment"],
                                **({"_about": "the portals on the square: a column either side of the door, the entablature, a pediment"} if i == 0 else {})))

doc = {"name": "El Pilar",
       "_about": "THE BASILICA OF OUR LADY OF THE PILLAR, Zaragoza (1681-1872), from components: a long brick hall church of three naves of one height, seven bays on two rows of piers with arches from pier to pier; ELEVEN tiled domes -- the great central one on its tall drum, six down the middle nave, four over the aisles -- each a `drum-dome` on pendentives over its bay; flat ceilings and low hipped roofs over the other bays; four `baroque-tower`s at the corners (shaft, open belfry, chamfered upper stage, bulbous cap and lantern), the east one on the square climbed by its `tower-stair` to the belfry; `portico` portals on the square.",
       "params": {"detail": 4}, "base": {"height": 0.6, "steps": 3, "stepOut": 0.4, "margin": 4}, "railing": {"type": "iron"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/el-pilar.json"), "w").write(json.dumps(doc, indent=2) + "\n")
