# TIKAL TEMPLE I, the Temple of the Great Jaguar (Peten, c. AD 732), the tomb of Jasaw Chan K'awiil on the east side of the Great Plaza; 47m to the top of
# its roof comb. It is the Peten form, the opposite of Chichen Itza's broad square: narrow and very steep.
#   NINE TERRACES (the nine levels of the underworld), each a battered wall under an apron moulding, set in at the corners -- the corners
#   recessed and rounded, the sharp re-entrant shadow up every angle of the pyramid being what makes it Tikal. Base about 36 x 34m, the terraces to 27.6m.
#   ONE STAIR, on the front alone, about 55 degrees, its head at the shrine's own platform (30.6m) -- it runs out well past the foot of the pyramid.
#   THE SHRINE on a two-stepped platform: walls 2m thick for rooms 2m wide -- three narrow corbel-vaulted chambers one behind another on the axis,
#   each door lower and its floor a step up, sapodilla beams over the doors. The shrine is almost all masonry.
#   THE ROOF COMB, as tall as the shrine and more: two parallel walls with a hollow between, stepping in as it rises, set over the back room so that it
#   weighs on the back wall; its front once carried the king enthroned between scrolls, of which a shadow remains.
#   The front (real: west, to the plaza) is +z here. Numbers are worked here and written as numbers.
import os, json, math
from statuary import statue, FACE_PZ
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
r4 = lambda v: round(v, 4)
Q = math.pi / 2
corbel = {"profile": "corbel", "cap": 0.15, "slope": 74}

N, HT = 9, 27.6 / 9                        # the terraces, each one's height
BX, BZ, TX, TZ = 36.0, 34.0, 15.0, 14.0    # the foot and the top of the terraces (the top is the shrine platform's own footprint)
CUT, ROUND = 1.1, 0.5                      # how far the corners are set in, and their rounding
def plan(a, b):
    """a terrace's plan, half-widths a and b: a rectangle with each corner recessed, its outer angles rounded"""
    c, r = CUT, ROUND
    q = [(a, b - c - r), (a - r, b - c), (a - c, b - c), (a - c, b - r), (a - c - r, b)]   # the +x+z corner, going from the east side round to the north
    pts = q + [(-x, z) for x, z in reversed(q)] + [(-x, -z) for x, z in q] + [(x, -z) for x, z in reversed(q)]
    return [[r4(x), r4(z)] for x, z in pts]
BAT, APRON = 0.55, 0.32                    # the batter, the apron's height share
for i in range(N):
    k = i / (N - 1)
    a, b = (BX + (TX - BX) * k) / 2, (BZ + (TZ - BZ) * k) / 2
    add(f"terrace {i + 1}", {"type": "prism", "plan": {"points": plan(a, b)}, "height": r4(HT), "batter": {"out": BAT},
                             "courses": [{"y": r4(HT * (1 - APRON)), "h": r4(HT * APRON * .35), "out": 0.3, "profile": "band"}, {"y": r4(HT * (1 - APRON * .65)), "h": r4(HT * APRON * .65), "out": 0.12, "profile": "band"}],
                             "at": [[0, r4(i * HT), 0, 0]],
                             **({"_about": "nine terraces, each a battered wall under an apron, set in at the corners"} if i == 0 else {})})
TOP = 30.6
W, RISE, RUN = 9.0, 0.3, 0.22
STEPS = round(TOP / RISE)
L = STEPS * RUN
ZHEAD = TZ / 2                             # the stair's head: the platform's front edge
add("stair", {"type": "flight", "steep": True, "width": W, "run": RUN, "rise": r4(TOP / STEPS), "base": 0, "top": TOP, "landing": 0,
              "at": [[r4(W / 2), 0, r4(ZHEAD + L), Q]], "_about": "the one stair, up the front: a hundred steep steps, out past the pyramid's foot, to the shrine's platform"})

# the shrine's platform: two steps, on the top terrace
add("platform 1", {"type": "box", "width": TX, "length": TZ, "height": 1.8, "walked": True, "at": [[0, 27.6, 0, 0]]})
add("platform 2", {"type": "box", "width": TX, "length": TZ, "height": 1.2, "walked": True, "at": [[0, 29.4, 0, 0]],
                   "courses": [{"y": 0.9, "h": 0.3, "out": 0.15, "profile": "band"}], "_about": "the shrine's platform, the stair's head"})

# THE SHRINE: thick walls, three narrow rooms one behind another. Its floors a step up each room.
Y0 = TOP
SW, SD, T = 11.5, 9.6, 1.9                 # the shrine across and along, its side walls
ZB = ZHEAD - 1.2 - SD                      # its back wall's outer face
ZF = ZHEAD - 1.2                           # its front
RW = SW - 2 * T                            # a room's length across
ROOMS = [(1.5, 0.0), (1.5, 0.2), (1.5, 0.4)]    # each room's width along the axis, its floor over the shrine's
WALL = (SD - sum(w for w, _ in ROOMS)) / 4       # the front, the back, and the two cross walls between the rooms
HS, TH = 3.0, 6.4                          # the springing, the shrine's height to the roof
door = lambda w, h: [{"at": 0, "width": w, "sill": 0, "springing": h, "head": {"profile": "flat"}, "glass": False}]
add("shrine", {"type": "enclosure", "plan": {"rect": [SW, SD]}, "thickness": T, "height": TH, "glass": False, "openings": [],
               "faces": {"0": door(2.0, 2.9)},
               "courses": [{"y": 0, "h": 0.25, "out": 0.1, "profile": "band"}, {"y": 3.7, "h": 0.5, "out": 0.25, "profile": "string"}, {"y": 5.9, "h": 0.5, "out": 0.3, "profile": "band"}],
               "at": [[0, Y0, r4((ZF + ZB) / 2), 0]], "_about": "the shrine: walls nearly as thick as its rooms are wide, a medial moulding, one door"})
z = ZF - WALL
for i, (w, f) in enumerate(ROOMS):
    if f: add(f"room {i + 1} floor", {"type": "box", "width": r4(RW), "length": w, "height": r4(f), "walked": True, "at": [[0, Y0, r4(z - w / 2), 0]]})
    add(f"room {i + 1} vault", {"type": "barrel", "width": w, "length": r4(RW), "springing": r4(HS + f), "top": TH, "head": corbel, "at": [[r4(RW / 2), Y0, r4(z - w / 2), Q]],
                                **({"_about": "a corbel vault, spanning no more than a room's 1.5m"} if i == 0 else {})})
    z -= w
    if i < 2:
        add(f"cross wall {i + 1}", {"type": "wall", "width": r4(RW), "height": TH, "thickness": r4(WALL), "glass": False,
                                    "openings": [{"at": r4(RW / 2), "width": 1.5, "sill": ROOMS[i + 1][1], "springing": 2.4 + ROOMS[i + 1][1], "head": {"profile": "flat"}, "glass": False}],
                                    "at": [[0, Y0, r4(z - WALL / 2), 0]]})
        z -= WALL
add("lintel", {"type": "box", "width": 2.6, "length": 0.5, "height": 0.25, "at": [[0, r4(Y0 + 2.9), r4(ZF - 0.25), 0]], "_about": "a sapodilla beam over the door"})
add("shrine roof", {"type": "box", "width": SW, "length": SD, "height": 0.4, "flatRoof": True, "at": [[0, r4(Y0 + TH), r4((ZF + ZB) / 2), 0]]})

# THE ROOF COMB: two walls and the hollow between, three stages, stepping in, over the shrine's back; pierced by small openings
Y = Y0 + TH + 0.4
ZC = ZB + 2.3                              # the comb's middle, over the back room
STAGES = [(10.4, 3.4, 3.9), (8.4, 3.1, 3.0), (6.4, 2.7, 2.4)]    # each stage's width, depth and height: to 47m
def holes(w, h, n):
    s = w / n
    return [{"at": r4(s * (j + 0.5)), "width": r4(s * 0.34), "sill": r4(h * 0.25), "springing": r4(h * 0.68), "head": {"profile": "flat"}, "glass": False} for j in range(n)]
for i, (w, d, h) in enumerate(STAGES):
    n = 5 - i
    for nm, zz in (("front", ZC + d / 2 - 0.35), ("back", ZC - d / 2 + 0.35)):
        add(f"comb {i + 1} {nm}", {"type": "wall", "width": w, "height": h, "thickness": 0.7, "glass": False, "openings": holes(w, h, n), "at": [[0, r4(Y), r4(zz), 0]],
                                   "courses": [{"y": r4(h - 0.4), "h": 0.4, "out": 0.2, "profile": "band"}]})
    add(f"comb {i + 1} ends", {"type": "wall", "width": r4(d - 1.4), "height": h, "thickness": 0.7, "glass": False, "at": [[r4(s * (w / 2 - 0.35)), r4(Y), r4(ZC), Q]  for s in (-1, 1)]})
    Y += h
    add(f"comb {i + 1} cap", {"type": "box", "width": w, "length": d, "height": 0.3, "flatRoof": True, "at": [[0, r4(Y), r4(ZC), 0]]})
    Y += 0.3 if i == 2 else 0
add("king", statue((0, r4(Y0 + TH + 0.4 + 5.0), r4(ZC + STAGES[0][1] / 2 + 0.55)), kind="man", style="maya", pose="seated", stone="limestone", scale=2.2, seed=9, face=FACE_PZ))
add("king's seat", {"type": "box", "width": 3.2, "length": 1.4, "height": 3.0, "at": [[0, r4(Y0 + TH + 0.4 + 2.0), r4(ZC + STAGES[0][1] / 2 + 0.5), 0]], "_about": "the block the king's enthroned figure stood out from"})
scroll = {"type": "box", "width": 1.2, "length": 1.4, "height": 1.2}
add("scrolls", {**scroll, "at": [[r4(s * x), r4(Y0 + TH + 0.4 + y), r4(ZC + STAGES[0][1] / 2 - 0.15), 0] for s in (-1, 1) for x, y in ((3.5, 2.6), (3.2, 5.2))], "_about": "the scrolls and serpents flanking the king, as worn lumps"})
TOPY = Y

doc = {"name": "Tikal Temple I",
       "_about": "TIKAL TEMPLE I, the Temple of the Great Jaguar: nine steep terraces with recessed corners (36 x 34m at the foot, 27.6m), one stair of a hundred steps up the front to the shrine's platform at 30.6m, the shrine of three narrow corbel-vaulted rooms one behind another, the two-walled roof comb to 47m with the king enthroned on its front (tools/archgen/tikal.py).",
       "params": {"detail": 4}, "base": {"height": 0.3, "steps": 1, "stepOut": 1.0, "margin": 2},
       "railing": {"type": "stone", "height": 1.0}, "_railing": "the stair's balustrades", "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/tikal.json"), "w").write(json.dumps(doc, indent=1) + "\n")
fin = {"name": "Tikal Temple I", "building": "architecture/tikal",
       "_about": "Grey-white Peten limestone gone dark with weather: the terraces and comb in rough courses, the stair and shrine dressed, the wood of the lintel.",
       "stone": {"color": "#c9c4b2", "accent": "#9c9786", "pat": "ashlar"},
       "rules": [{"parts": ["lintel"], "pattern": "timber/planks", "palette": "walnut"},
                 {"surface": "floor", "pattern": "floors/flagstones", "palette": "maya"},
                 {"parts": ["stair", "shrine", "kind:moulding"], "pattern": "stone/ashlar", "palette": "maya"},
                 {"surface": "wall", "pattern": "stone/rubble long", "palette": "maya"}]}
open(os.path.join(ROOT, "assets/finishes/tikal.json"), "w").write(json.dumps(fin, indent=1) + "\n")
print("tikal:", len(parts), "parts; top", round(TOPY, 2), "stair run", round(L, 1), "steps", STEPS)
