# ST MARK'S BASILICA, Venice (1063-94, on the plan of Justinian's Holy Apostles; marble and mosaic through the 13th century, the high lead
# domes about 1230, the Gothic crown about 1400): 76.5m long, 62.6m across the transept, the outer domes 43m to their crosses, the
# west front 51.8m wide -- and the CAMPANILE (98.6m, its shaft 12m square, rebuilt 1912) out in the Piazza.
#   FIVE DOMES on a Greek cross, each a crossing as Hagia Sophia's is on a smaller scale (four piers, four barrel arches, pendentives): the
#   middle and the west domes 13m across inside, the north, south and east 11m (the sizes of the page's "larger" and "smaller"). Over each low
#   brick dome the Venetians raised a high shell of timber and lead: here a `drum-dome` on the onion section, slightly bulging, on its
#   ring of 16 windows, a small bulbous lantern and a gold cross on top.
#   THE WEST FRONT, 51.8m: below, FIVE deep round portals -- the middle one larger -- between piers faced in two tiers of marble columns, each portal
#   a stepped recess, a door, and over the door a mosaic lunette on its gold; then the terrace with its balustrade, the four horses over the
#   middle door, and above them FIVE arches: four lunettes of mosaic and the great glazed middle window, each under an OGEE GABLE edged with
#   carved leaves, its statue on the point (St Mark over the middle one), with six tabernacles (`pinnacle` with a figure) on the piers between.
#   The plan: x across (north +x), z along (east +z), the middle dome's axis at the origin. The narthex runs along the west and up the north side of the west arm,
#   the Treasury and Baptistery stand on its south side, so the west half reads as a rectangle and only the transept and chancel stand out as a cross.
#   Not on a survey: the sizes are the published ones, the positions (the Campanile's among them) worked from them. Numbers are worked here.
import os, json, math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapes import onion_height
from statuary import statue, FACE_NZ
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q, PI = math.pi / 2, math.pi
r3 = lambda v: round(v, 3)
SEMI = {"profile": "semicircular"}

# ---- the outline -----------------------------------------------------------------------------------------------------------
FW = 25.9                                        # the west front's half width (51.8m)
ZF = -40.0                                       # the front's face; 76.5m to the apse's foot
ZW0, ZW1 = -37.0, -36.0                          # the wall behind the portals' recesses, whose faces hold the door and the lunette
ZN = -32.5                                       # the narthex's back wall
XT, ZT = 31.3, 17.0                              # the transept's end walls (62.6m), its half width along z
XA, ZE = 17.0, 31.0                              # the arms' half width, the east wall
BH, WT = 17.0, 1.4                               # the body's walls and flat roofs, their thickness
OUT = [[FW, ZW0], [-FW, ZW0], [-FW, -ZT], [-XT, -ZT], [-XT, ZT], [-XA, ZT], [-XA, ZE], [XA, ZE], [XA, ZT], [XT, ZT], [XT, -ZT], [FW, -ZT]]   # (the winding enclosure keeps: face 0 is the west)
PX = [0.0, -11.0, 11.0, -20.8, 20.8]             # the five portals' middles
PW = [9.0, 7.0, 7.0, 6.6, 6.6]                   # ...their widths at the front

win = {"every": 6.5, "width": 1.9, "end": 3.5, "sill": 9.0, "springing": 12.2, "head": SEMI}
doors = [{"at": r3(x), "width": 3.2 if k else 4.0, "sill": 0, "springing": 4.2 if k else 5.0, "head": {"profile": "flat"}, "glass": False} for k, x in enumerate(PX)]   # (the body's glass is its windows', not its doors')
add("body", {"type": "enclosure", "plan": {"points": OUT}, "thickness": WT, "height": BH, "interior": True, "glass": True, "openings": win, "faces": {"0": doors, "2": [], "10": []}, "at": [[0, 0, 0, 0]],
             "_about": "the church's outer walls on the cross and the narthex's rectangle, faced in marble, windows high in them; on the west the five doors"})
add("narthex back wall", {"type": "wall", "width": 2 * XA, "height": BH, "thickness": 1.0, "at": [[0, 0, ZN, 0]],
                          "openings": [{"at": XA - 11.0, "width": 2.4, "sill": 0, "springing": 3.8, "head": SEMI}, {"at": XA, "width": 4.0, "sill": 0, "springing": 5.0, "head": SEMI}, {"at": XA + 11.0, "width": 2.4, "sill": 0, "springing": 3.8, "head": SEMI}],   # (a wall's openings are measured from its end)
                          "_about": "the wall between the narthex and the nave, with the great door and two lesser"})
add("treasury wall", {"type": "wall", "width": -ZT - ZN, "height": BH, "thickness": 1.0, "openings": [{"at": r3((-ZT - ZN) / 2), "width": 2.4, "sill": 0, "springing": 3.8, "head": SEMI}],
                      "at": [[XA + .5, 0, r3((ZN - ZT) / 2), Q], [-XA + .5, 0, r3((ZN - ZT) / 2), Q]], "_about": "the walls between the west arm and, north, the narthex's arm, south, the Treasury and Baptistery"})
add("west door wall ends", {"type": "wall", "width": r3(FW - XA - WT), "height": BH, "thickness": 1.0, "openings": [], "at": [[r3(s * (XA + (FW - XA - WT) / 2)), 0, ZN, 0] for s in (-1, 1)]})

# ---- the five crossings ------------------------------------------------------------------------------------------------------
DOMES = [("middle", 0, 0, 13.0, 15.5, 3.0, ()), ("west", 0, -22.0, 13.0, 15.5, 3.0, ("w", "n", "s")),
         ("east", 0, 22.0, 11.0, 14.5, 3.0, ("e", "n", "s")), ("north", 22.0, 0, 11.0, 14.5, 3.0, ("n", "w", "e")), ("south", -22.0, 0, 11.0, 14.5, 3.0, ("s", "w", "e"))]
BULGE, NECK = 1.1, .3
holes = []
for nm, cx, cz, S, SPR, PR, closed in DOMES:
    R, RING = S / 2, SPR + S / 2
    pc = R + PR / 2
    add(f"{nm} piers", {"type": "box", "width": PR, "length": PR, "height": r3(RING + .5), "at": [[r3(cx + sx * pc), 0, r3(cz + sz * pc), 0] for sx in (-1, 1) for sz in (-1, 1)],
                        **({"_about": "each dome's four piers, rising over the roofs"} if nm == "middle" else {})})
    add(f"{nm} arches", {"type": "barrel", "width": S, "length": PR, "springing": SPR, "top": r3(RING + .5), "head": SEMI,
                         "at": [[cx, 0, r3(cz - R), 0], [cx, 0, r3(cz + R + PR), 0], [r3(cx - R), 0, cz, Q], [r3(cx + R + PR), 0, cz, Q]],
                         **({"_about": "its four barrel arches, pier to pier, their backs in lead over the flat roofs"} if nm == "middle" else {})})
    add(f"{nm} pendentives", {"type": "pendentives", "span": S, "springing": SPR, "sides": 16, "at": [[cx, 0, cz, 0]], "deck": {"thickness": .5, "out": PR}})
    TY = BH + .5
    PL = {"s": [cx, TY, r3(cz + R + PR - .3), PI], "n": None}
    walls = {"w": [cx, TY, r3(cz - R - PR + 1.0), 0], "e": [cx, TY, r3(cz + R + PR), 0], "s": [r3(cx - R - PR + 1.0), TY, cz, Q], "n": [r3(cx + R + PR), TY, cz, Q]}
    if nm in ("north", "south"): walls = {"n": [r3(cx + R + PR), TY, cz, Q], "s": [r3(cx - R - PR + 1.0), TY, cz, Q], "w": [cx, TY, r3(cz - R - PR + 1.0), 0], "e": [cx, TY, r3(cz + R + PR), 0]}
    if closed:
        add(f"{nm} tympana", {"type": "wall", "width": S, "height": r3(RING + .5 - TY), "thickness": 1.0, "at": [walls[k] for k in closed],
                              "openings": {"pattern": "3", "width": 1.5, "gap": 1.6, "sill": .8, "springing": 2.2, "head": SEMI},
                              **({"_about": "the lunettes closing a dome's outer arches over the roofs, three windows in each"} if nm == "west" else {})})
    add(f"{nm} crossing", {"type": "interior", "plan": {"rect": [S + 2 * PR, S + 2 * PR]}, "height": r3(RING + .5), "at": [[cx, 0, cz, 0]]})
    add(f"{nm} dome", comp("components/drum-dome", {"R": R, "dt": 1.0, "H": 2.8, "n": 16, "every": 1, "winW": .9, "winSill": .7, "winH": 1.1,
                                                    "profile": "onion", "bulge": BULGE, "neck": NECK, "domeT": .3},
                           [[cx, r3(RING + .5), cz, 0]], build=["drum", "dome"],
                           **({"_about": "the high outer dome the Venetians raised over the low brick one: lead on timber, gently bulging, on its ring of windows"} if nm == "middle" else {})))
    tip = RING + .5 + 2.8 + onion_height(R + 1.0, BULGE, NECK)
    LR = R * .2
    add(f"{nm} lantern", {"type": "column", "radius": r3(LR * .75), "height": r3(R * .22), "sides": 12, "at": [[cx, r3(tip - .5), cz, 0]],
                          **({"_about": "the small bulbous lantern on each dome and the gold cross on it"} if nm == "middle" else {})})
    LY = tip - .5 + R * .22
    add(f"{nm} cupola", {"type": "dome", "radius": r3(LR), "thickness": 0, "sides": 12, "head": {"profile": "onion", "bulge": 1.15, "neck": .6}, "at": [[cx, r3(LY), cz, 0]]})
    cr = LY + onion_height(LR, 1.15, .6) - .1; H = R * .28
    add(f"{nm} cross", {"type": "bars", "w": .13, "lines": [[cx, r3(cr), cz, cx, r3(cr + H), cz], [r3(cx - H * .32), r3(cr + H * .68), cz, r3(cx + H * .32), r3(cr + H * .68), cz],
                                                             [cx, r3(cr + H * .68), r3(cz - H * .32), cx, r3(cr + H * .68), r3(cz + H * .32)]]})
    if nm == "middle": print("the middle dome's cross reaches", round(cr + H, 2))
    holes.append((cx - R - PR, cz - R - PR, cx + R + PR, cz + R + PR))
# the barrels joining the middle dome's arches to the arms'
def join(nm, S, SPR, top, at, L): add(nm, {"type": "barrel", "width": S, "length": L, "springing": SPR, "top": top, "head": SEMI, "at": at})
RM = 6.5 + 3.0
G1 = 22.0 - 9.5 - RM                             # the west arm: its piers' reach, 9.5m, and the middle's: the gap between
join("west join", 13.0, 15.5, 22.5, [[0, 0, r3(-RM), 0]], r3(22.0 - 9.5 - RM))
G2 = 22.0 - 8.5 - RM                             # the lesser domes' reach
join("east join", 11.0, 14.5, 20.5, [[0, 0, r3(RM + G2), 0]], r3(G2))
join("north join", 11.0, 14.5, 20.5, [[r3(RM + G2), 0, 0, Q]], r3(G2))
join("south join", 11.0, 14.5, 20.5, [[r3(-RM), 0, 0, Q]], r3(G2))
for nm, x0, z0, x1, z1, top in (("west", -6.5, -RM - G1, 6.5, -RM, 22.5), ("east", -5.5, RM, 5.5, RM + G2, 20.5), ("north", RM, -5.5, RM + G2, 5.5, 20.5), ("south", -RM - G2, -5.5, -RM, 5.5, 20.5)):
    add(f"{nm} join room", {"type": "interior", "plan": {"rect": [x1 - x0, z1 - z0]}, "height": top, "at": [[r3((x0 + x1) / 2), 0, r3((z0 + z1) / 2), 0]]})
holes += [(-6.5, -RM - G1, 6.5, -RM), (-5.5, RM, 5.5, RM + G2), (RM, -5.5, RM + G2, 5.5), (-RM - G2, -5.5, -RM, 5.5)]

# the flat roofs, cut round every crossing and join
def tiles(x0, z0, x1, z1, holes):
    xs = sorted({x0, x1, *[c for h in holes for c in (h[0], h[2]) if x0 < c < x1]})
    zs = sorted({z0, z1, *[c for h in holes for c in (h[1], h[3]) if z0 < c < z1]})
    out = []
    for j in range(len(zs) - 1):
        run = None
        for i in range(len(xs) - 1):
            mx, mz = (xs[i] + xs[i + 1]) / 2, (zs[j] + zs[j + 1]) / 2
            free = not any(h[0] < mx < h[2] and h[1] < mz < h[3] for h in holes)
            if free and run is None: run = xs[i]
            if (not free or i == len(xs) - 2) and run is not None:
                out.append((run, zs[j], xs[i + 1] if free else xs[i], zs[j + 1])); run = None
    return out
k = 0
for (a, b, c, d) in [(-FW, ZW0, FW, -ZT), (-XT, -ZT, XT, ZT), (-XA, ZT, XA, ZE)]:
    for (x0, z0, x1, z1) in tiles(a, b, c, d, holes):
        k += 1
        add(f"roof {k}", {"type": "box", "flatRoof": True, "width": r3(x1 - x0), "length": r3(z1 - z0), "height": .5, "at": [[r3((x0 + x1) / 2), BH, r3((z0 + z1) / 2), 0]],
                          **({"_about": "the flat lead roofs round the domes"} if k == 1 else {})})
# the nave arcades: marble columns in the arms, under the walls' galleries
cols = [[r3(sx * 8.5), 0, r3(z), 0] for sx in (-1, 1) for z in (-28.5, -15.5, 15.5, 27.5)] + [[r3(x), 0, r3(sz * 8.5), 0] for sz in (-1, 1) for x in (-27.5, -15.5, 15.5, 27.5)]
add("nave columns", {"type": "column", "radius": .42, "height": 8.0, "sides": 12, "at": cols, "_about": "the marble columns that separate the arms from their aisles"})
add("apse", comp("components/apse", {"R": 6.0, "T": 1.0, "H": 10.6, "n": 12, "winW": 1.3, "winSill": 5.5, "winH": 3.4, "domeT": 1.0}, [[0, 0, ZE, 0]], _about="the main apse behind the high altar, its half dome roofed in lead"))
add("side apses", comp("components/apse", {"R": 2.8, "T": .8, "H": 8.0, "n": 8, "winW": .8, "winSill": 4.0, "winH": 2.0, "domeT": .8}, [[11.5, 0, ZE, 0], [-11.5, 0, ZE, 0]], _about="the two smaller apses beside it"))

# ---- the west front: below, the five portals ---------------------------------------------------------------------------------
LOW, Z1, Z2 = 15.0, ZF + 1.0, ZW0                 # the lower register's height; the front layer's back and the recess's
S_CROWN = {0: 14.2}                              # (the arches' crowns)
def spr(k): return 9.8 if k == 0 else (9.4 if k < 3 else 9.2)
ops = lambda dw: [{"at": r3(FW + x), "width": r3(w - dw), "sill": 0, "springing": spr(k), "head": SEMI} for k, (x, w) in enumerate(zip(PX, PW))]
add("portal orders", {"type": "wall", "width": 2 * FW, "height": LOW, "thickness": 1.0, "at": [[0, 0, r3(ZF + 1.0), PI]], "openings": ops(0), "_about": "the front's outer arch, a portal's first order"})
parts["portal orders"]["at"] = [[0, 0, ZF, PI]]
add("portal recesses", {"type": "wall", "width": 2 * FW, "height": LOW, "thickness": 2.0, "at": [[0, 0, Z1, PI]], "openings": ops(1.8),
                        "_about": "the deep recess behind it, its second order: 2m through, the door and the lunette at its back"})
def half_disc(R, sp): return [[r3(R * math.cos(PI * (1 - i / 16))), r3(sp + R * math.sin(PI * (1 - i / 16)))] for i in range(17)]
def rect(R, y0, y1): return [[-R, r3(y0)], [-R, r3(y1)], [R, r3(y1)], [R, r3(y0)]]
for k, (x, w) in enumerate(zip(PX, PW)):
    w2 = w - 1.8; R = w2 / 2; sp = spr(k)          # (a half disc and the band under it, each 2:1: one mosaic each)
    add(f"west lunette {k + 1}", {"type": "screen", "t": .06, "outline": half_disc(R, sp), "at": [[r3(x), 0, r3(ZW0 - .06), PI]], "kind": "plaque",
                                  **({"_about": "the mosaic over each door, on the wall at the recess's back: the Last Judgment over the middle one, the bringing of St Mark's body from Alexandria over the four others"} if k == 0 else {})})
    add(f"west panel {k + 1}", {"type": "screen", "t": .06, "outline": rect(R, sp - R, sp), "at": [[r3(x), 0, r3(ZW0 - .06), PI]], "kind": "plaque"})
# the columns, two tiers on every pier's face and down the recesses' sides
piers = [-(FW - .9), -15.9 - 1.2, -6.0, 6.0, 15.9 + 1.2, FW - .9]
C1, C2 = 5.2, 4.2                                # the tiers' heights
c_low, c_up = [], []
for x in piers:
    for dx in (-1.05, 0, 1.05):
        c_low.append([r3(x + dx), 0, r3(ZF - .45), 0]); c_up.append([r3(x + dx), C1 + .2, r3(ZF - .45), 0])
for x, w in zip(PX, PW):
    for s in (-1, 1):
        for dz in (.4, 1.3, 2.2):
            c_low.append([r3(x + s * (w / 2 - .3 - .26 * dz)), 0, r3(ZF + dz), 0])
            c_up.append([r3(x + s * (w / 2 - .3 - .26 * dz)), C1 + .2, r3(ZF + dz), 0])
for nm, data in (("lower", c_low), ("upper", c_up)):
    for j in range(3):
        add(f"{nm} columns {j + 1}", {"type": "column", "radius": .38 if nm == "lower" else .3, "height": C1 if nm == "lower" else C2, "sides": 10, "at": data[j::3],
                                      **({"_about": "two tiers of precious marble columns, brought from the East after 1204, on the piers and down the portals' sides: three stones, porphyry, verde antico, grey"} if nm == "lower" and j == 0 else {})})
add("column course", {"type": "box", "width": 3.0, "length": 1.15, "height": .22, "at": [[x, C1, r3(ZF - .3), 0] for x in piers], "_about": "the course between the tiers, on each pier"})
add("arch rings", {"type": "bars", "w": .42, "h": .35, "paths": [[[r3(x + (w / 2 + .2) * math.cos(PI * (1 - i / 14))), r3(spr(k) + (w / 2 + .2) * math.sin(PI * (1 - i / 14))), r3(ZF - .18)] for i in range(15)] for k, (x, w) in enumerate(zip(PX, PW))],
                   "_about": "the carved band round each portal's arch"})
for j in range(3): build.remove(f"upper columns {j + 1}"); build.append(f"upper columns {j + 1}")
# ---- the terrace, its balustrade, the horses ---------------------------------------------------------------------------------
add("terrace", {"type": "box", "flatRoof": True, "width": 2 * FW, "length": r3(ZW0 - ZF), "height": .5, "at": [[0, LOW, r3((ZF + ZW0) / 2), 0]],
                "_about": "the terrace over the lower register, where the horses stand"})
BY = LOW + .5
bal = [[r3(-FW + .3 + i * .7), BY, r3(ZF + .3), r3(-FW + .3 + i * .7), BY + .9, r3(ZF + .3)] for i in range(int((2 * FW - .6) / .7) + 1)]
add("terrace balusters", {"type": "bars", "w": .14, "lines": bal, "caps": False, "_about": "the marble balustrade along the terrace"})
add("terrace rail", {"type": "box", "width": r3(2 * FW - .4), "length": .3, "height": .14, "at": [[0, BY + .9, r3(ZF + .3), 0]]})
def horse(x, z, yaw):
    """a horse in bars, its body along x from the shoulder: a stride, one foreleg lifted (the Quadriga's), the neck arched, the head dropped; 1.7m at the withers"""
    c, s = math.cos(yaw), math.sin(yaw)
    T = lambda p: [r3(x + p[0] * c + p[2] * s), r3(BY + .9 + p[1]), r3(z - p[0] * s + p[2] * c)]
    B = [([-.95, 1.3, .16], [.65, 1.42, .16], .62, .76), ([-.95, 1.3, -.16], [.65, 1.42, -.16], .62, .76), ([.65, 1.5, 0], [1.05, 2.1, 0], .34, .52), ([1.05, 2.15, 0], [1.42, 1.86, 0], .22, .34), ([-.8, 1.0, .18], [-.92, 0, .2], .16, .2), ([-.8, 1.0, -.18], [-.7, 0, -.2], .16, .2),
         ([.55, 1.1, .2], [.62, 0, .2], .16, .2), ([.55, 1.1, -.2], [1.0, .62, -.2], .16, .2), ([1.0, .62, -.2], [.86, .28, -.2], .13, .15), ([-.96, 1.42, 0], [-1.24, .62, 0], .12, .2)]
    return [(T(a), T(b), w, h) for a, b, w, h in B]
ST = [horse(x, ZF + 1.6, Q + t) for x, t in ((-3.2, -.28), (-1.1, -.12), (1.1, .12), (3.2, .28))]   # (turned a little outward, as they stand)
add("horses", {"type": "bars", "w": .3, "h": .46, "lines": [a + b for H_ in ST for (a, b, w, h) in H_ for a, b in [(a, b)]], "_about": "the four gilded horses of the Hippodrome, four abreast over the middle door, drawn in bars at their real 2.3m (one part: bars touch only as one piece)"})
add("horse plinths", {"type": "box", "width": 1.1, "length": 2.9, "height": .9, "at": [[x, BY, r3(ZF + 1.6), 0] for x in (-3.2, -1.1, 1.1, 3.2)]})
parts["horse plinths"]["at"] = [[x, BY, r3(ZF + 1.6), 0] for x in (-3.2, -1.1, 1.1, 3.2)]

# ---- above: the upper register, the five arches and their ogee gables --------------------------------------------------------
ZU = ZW0                                         # the upper wall's face (it stands on the terrace's back)
UT = 1.0                                         # its thickness
Y0 = LOW                                         # its foot
PIERTOP = 22.0                                   # the wall's height between the gables
UPX, UPW = [0.0, -11.5, 11.5, -21.0, 21.0], [9.4, 7.6, 7.6, 6.6, 6.6]
def ogee(cx, hw, y0, h, n=8):
    """an ogee's two S-curves, from its left foot to its point and down to its right (the half width falls as a smoothstep: vertical at the foot and at the tip)"""
    left = [[cx - hw * (1 - (3 * t * t - 2 * t * t * t)), y0 + h * t] for t in [i / n for i in range(n + 1)]]
    return left + [[2 * cx - a, b] for a, b in reversed(left[:-1])]
SPR_U = [20.8, 20.8, 20.8, 20.5, 20.5]           # the upper arches' springings
GH = [5.6, 4.6, 4.6, 4.2, 4.2]                   # ...and their gables' heights over the wall's top
G = lambda k: UPW[k] / 2 + .9
def left_of_centre(side):
    """the wall's silhouette on one side of the middle window, foot to foot: (side is the x sign)"""
    edge = UPW[0] / 2 + .4
    pts = [[edge, Y0], [FW, Y0], [FW, PIERTOP]]
    for k in (3, 1) if side < 0 else (4, 2):
        cx, hw = abs(UPX[k]), G(k)
        pts += [[a, b] for a, b in reversed(ogee(cx, hw, PIERTOP, GH[k]))]
    pts += [[edge, PIERTOP]]
    return pts
for side, nm in ((-1, "south"), (1, "north")):
    out = [[r3(side * a), r3(b)] for a, b in left_of_centre(side)]
    add(f"{nm} upper wall", {"type": "screen", "t": UT, "outline": out, "at": [[0, 0, r3(ZU), PI]], "_about": "the upper wall either side of the middle window, its top the ogee gables of two bays"})
    # (a screen's face is at the placement, its t behind it along -z: turned half round, behind it is +z, into the church -- and its x runs backward, which the outline's sign already answers: see below)
    parts[f"{nm} upper wall"]["outline"] = [[r3(-side * a), r3(b)] for a, b in left_of_centre(side)]
# the middle: a wall with the great window, and the great gable on it
WW, WSP = UPW[0], SPR_U[0]
CR = WSP + WW / 2 + .8
add("middle window wall", {"type": "wall", "width": r3(WW + .8), "height": r3(CR - Y0), "thickness": UT, "glass": True, "at": [[0, Y0, r3(ZU - UT + 1.0 - 1.0), PI]],
                           "openings": [{"at": r3((WW + .8) / 2), "width": WW, "sill": 1.6, "springing": WSP - Y0, "head": SEMI}], "_about": "the great window over the horses: blind until the fire of 1419"})
parts["middle window wall"]["at"] = [[0, Y0, r3(ZU), PI]]
add("middle gable", {"type": "screen", "t": UT, "outline": [[r3(-a), r3(b)] for a, b in reversed(ogee(0, WW / 2 + .8, CR, GH[0]))], "at": [[0, 0, r3(ZU), PI]], "_about": "the great ogee over it, St Mark and the angels on its point"})
# the lunettes, their rings
for k in (1, 2, 3, 4):
    w, x, sp = UPW[k], UPX[k], SPR_U[k]; R = w / 2
    add(f"upper lunette {k}", {"type": "screen", "t": .06, "outline": half_disc(R, sp), "kind": "plaque", "at": [[r3(x), 0, r3(ZU - .06), PI]],
                               **({"_about": "the four upper mosaics: the Descent from the Cross, the Harrowing, the Resurrection, the Ascension"} if k == 1 else {})})
    add(f"upper panel {k}", {"type": "screen", "t": .06, "outline": rect(R, sp - R, sp), "kind": "plaque", "at": [[r3(x), 0, r3(ZU - .06), PI]]})
# the great window's panes, dark, and their leads
RW = WW / 2; ZG = ZU + .9
add("window panes", {"type": "screen", "t": .05, "outline": [[-RW, Y0 + 1.6], *half_disc(RW, WSP), [RW, Y0 + 1.6]], "kind": "plaque", "at": [[0, 0, ZG, PI]], "_about": "the great window's dark glass (a pane stood in for it: what's behind it is the west dome's piers)"})
add("window leads", {"type": "bars", "w": .14, "h": .1, "lines": [[r3(i * RW / 2), Y0 + 1.6, ZG - .05, r3(i * RW / 2), r3(WSP + RW * math.sqrt(1 - (i / 2) ** 2)), ZG - .05] for i in (-1, 0, 1)] + [[-RW, r3(y), ZG - .05, RW, r3(y), ZG - .05] for y in (Y0 + 3.6, Y0 + 5.2, WSP)]})
rings = []
for k in range(5):
    w, x, sp = UPW[k], UPX[k], SPR_U[k]; R = w / 2 + .18
    rings.append([[r3(x + R * math.cos(PI * (1 - i / 16))), r3(sp + R * math.sin(PI * (1 - i / 16))), r3(ZU - .2)] for i in range(17)])
    rings.append([[r3(x - R), r3(sp - (3.2 if k else 6.0)), r3(ZU - .2)], [r3(x - R), r3(sp), r3(ZU - .2)]])
    rings.append([[r3(x + R), r3(sp - (3.2 if k else 6.0)), r3(ZU - .2)], [r3(x + R), r3(sp), r3(ZU - .2)]])
add("upper rings", {"type": "bars", "w": .38, "h": .34, "paths": rings, "_about": "a carved marble band round each upper arch"})
# the leaves up the gables, statues on the points
for k in range(5):
    cx, hw, y0, h = UPX[k], (WW / 2 + .8) if k == 0 else G(k), CR if k == 0 else PIERTOP, GH[k]
    add(f"gable leaves {k + 1}", {"type": "cresting", "run": [[r3(-a), r3(b)] for a, b in reversed(ogee(cx, hw, y0, h, 6))], "h": .75, "panel": .9, "t": .22, "bar": .13, "at": [[0, 0, r3(ZU - .1), PI]],
                                  **({"_about": "the Gothic crown: carved leaves climbing every gable's edges, white and gold"} if k == 0 else {})})
TIP = [(UPX[k], ((CR if k == 0 else PIERTOP) + GH[k])) for k in range(5)]
add("gable statues", {"type": "pinnacle", "w": .55, "h": .5, "s": .35, "figure": 2.3, "at": [[r3(x), r3(y - .15), r3(ZU + .5), 0] for x, y in TIP[1:]], "_about": "the four warrior saints on the side gables"})
parts["st mark"] = statue((0, TIP[0][1] + .1, ZU + .5), kind="man", pose="stand", style="gothic", stone="gold", scale=1.5, face=FACE_NZ, seed=7)
build.append("st mark")
add("st mark foot", {"type": "box", "width": 1.3, "length": 1.5, "height": .25, "at": [[0, r3(TIP[0][1] - .15), r3(ZU + .5), 0]], "_about": "St Mark on the great gable"})
# the tabernacles on the wall's top between the gables
TX = [(UPX[0] + UPX[1]) / 2 - .1, (UPX[0] + UPX[2]) / 2 + .1, (UPX[1] + UPX[3]) / 2, (UPX[2] + UPX[4]) / 2, -FW + .95, FW - .95]
add("tabernacles", {"type": "pinnacle", "w": 1.9, "h": 3.2, "s": 4.2, "sides": 8, "gablets": 1.0, "crockets": 2, "figure": 1.9, "at": [[r3(x), PIERTOP, r3(ZU + .5), 0] for x in TX],
                    "_about": "the six tabernacles on the piers between the gables, their spires' figures for the Evangelists, the Virgin and Gabriel"})
# the same crown, a shorter run of it, along the top of the north and south flanks of the west arm
for nm, sg in (("north", 1), ("south", -1)):
    add(f"{nm} flank gables", {"type": "screen", "t": .9, "outline": [[r3(a), r3(b)] for a, b in ogee(0, 3.6, BH + .3, 4.0, 6)],
                               "at": [[r3(sg * FW), 0, z, r3(sg * Q)] for z in (-33.0, -25.0)], **({"_about": "the Gothic crown continued along the flanks"} if nm == "north" else {})})
    add(f"{nm} flank pinnacles", {"type": "pinnacle", "w": 1.3, "h": 2.2, "s": 3.0, "sides": 8, "gablets": .6, "crockets": 1, "at": [[r3(sg * (FW - .65)), BH + .5, z, 0] for z in (-29.0, -21.0)]})

# ---- the Campanile, out in the Piazza -----------------------------------------------------------------------------------------
CX, CZ, CW = -38.0, -86.0, 12.0                  # its middle: a front's width out to the south-west, by the map; 12m square
SH = 50.0                                        # the brick shaft
add("campanile shaft", {"type": "box", "width": CW - .5, "length": CW - .5, "height": SH, "at": [[CX, 0, CZ, 0]], "_about": "the Campanile's shaft, 12m square and 50m of brick, rebuilt 1902-12 as it was"})
strips = [[r3(CX + i * (CW / 2 - .15) + j * o), 0, r3(CZ + j * (CW / 2 - .15) * 0 + i * o), 0] for i, j, o in []]
ST_ = []
for k in (-2, -1, 0, 1, 2):
    o = k * 2.45
    ST_ += [[r3(CX + o), 0, r3(CZ + (CW / 2 - .1)), 0], [r3(CX + o), 0, r3(CZ - (CW / 2 - .1)), 0]]
add("campanile strips", {"type": "box", "width": 1.0, "length": .3, "height": SH - .6, "at": ST_, "_about": "the brick pilaster strips, five to a face"})
ST2 = []
for k in (-2, -1, 0, 1, 2):
    o = k * 2.45
    ST2 += [[r3(CX + (CW / 2 - .1)), 0, r3(CZ + o), 0], [r3(CX - (CW / 2 - .1)), 0, r3(CZ + o), 0]]
add("campanile strips side", {"type": "box", "width": .3, "length": 1.0, "height": SH - .6, "at": ST2})
add("campanile cornice", {"type": "box", "width": CW + .6, "length": CW + .6, "height": .6, "at": [[CX, SH - .6, CZ, 0]]})
BEL = 8.2
add("campanile belfry", {"type": "enclosure", "plan": {"rect": [CW, CW]}, "thickness": .9, "height": BEL, "interior": True,
                         "openings": {"pattern": "4", "width": 1.9, "gap": .72, "sill": 1.0, "springing": 5.4, "head": SEMI}, "glass": False, "at": [[CX, SH, CZ, 0]],
                         "_about": "the belfry: four arches to a side, in white Istrian stone, the five bells within"})
add("belfry floor", {"type": "box", "width": CW - 1.4, "length": CW - 1.4, "height": .4, "at": [[CX, SH, CZ, 0]]})
Y1 = SH + BEL
ATT = 7.6
add("belfry cornice", {"type": "box", "width": CW + .9, "length": CW + .9, "height": .55, "at": [[CX, Y1, CZ, 0]]})
add("campanile attic", {"type": "box", "width": CW - .5, "length": CW - .5, "height": ATT, "at": [[CX, Y1 + .55, CZ, 0]], "_about": "the attic over the belfry, its reliefs of Venice as Justice and the Lion of St Mark"})
Y2 = Y1 + .55 + ATT
add("attic cornice", {"type": "box", "width": CW + .3, "length": CW + .3, "height": .5, "at": [[CX, Y2, CZ, 0]]})
Y3 = Y2 + .5
AT = 96.4
PIT = math.degrees(math.atan((AT - Y3) / (CW / 2 - .1)))
add("campanile spire", {"type": "roof", "form": "pyramid", "width": CW - .2, "length": CW - .2, "pitch": r3(PIT), "at": [[CX, Y3, CZ, 0]], "_about": "the green pyramid to 96m"})
add("spire pinnacles", {"type": "pinnacle", "w": .9, "h": 1.4, "s": 1.2, "at": [[r3(CX + sx * (CW / 2 - .5)), Y3, r3(CZ + sz * (CW / 2 - .5)), 0] for sx in (-1, 1) for sz in (-1, 1)]})
parts["gabriel"] = statue((CX, AT - .25, CZ), kind="man", pose="stand", style="gothic", stone="gold", scale=1.5, wings="raised", face=FACE_NZ, seed=11)
build.append("gabriel")
add("loggetta", {"type": "wall", "width": CW + 2.0, "height": 8.0, "thickness": 4.0, "at": [[CX, 0, r3(CZ + CW / 2 + 4.3), PI]], "glass": False,
                 "openings": {"pattern": "3", "width": 2.8, "gap": 1.5, "sill": .5, "springing": 4.6, "head": SEMI}, "_about": "Sansovino's Loggetta against the east face, three arches of red Verona and white marble"})
parts["loggetta"]["at"] = [[CX, 0, r3(CZ + CW / 2 + .3), PI]]
add("loggetta attic", {"type": "box", "width": CW + 2.0, "length": 4.0, "height": 1.4, "at": [[CX, 8.0, r3(CZ + CW / 2 + 2.3), 0]]})

# ---- the Piazza's paving: everything stands on it -----------------------------------------------------------------------------
PH = .12
for nm, d in parts.items():
    if d.get("type") == "marker": d["at"] = [[a[0], r3(a[1] + PH), a[2], *a[3:]] for a in d["at"]]; continue
    if d.get("lines"): d["lines"] = [[l[0], r3(l[1] + PH), l[2], l[3], r3(l[4] + PH), l[5]] for l in d["lines"]]
    if d.get("paths"): d["paths"] = [[[p[0], r3(p[1] + PH), p[2]] for p in q] for q in d["paths"]]
    for a in d.get("at", []):
        if isinstance(a, list): a[1] = r3(a[1] + PH)
    if d.get("type") in ("screen", "cresting"): pass
    if d.get("type") in ("bars",) and "at" in d: pass
PX0, PX1, PZ0, PZ1 = -50.0, 36.0, -96.0, 40.0
NX, NZ = 5, 8
TW, TL = (PX1 - PX0) / NX, (PZ1 - PZ0) / NZ
add("piazza", {"type": "box", "width": r3(TW), "length": r3(TL), "height": PH, "walked": True,
               "at": [[r3(PX0 + TW * (i + .5)), 0, r3(PZ0 + TL * (j + .5)), 0] for i in range(NX) for j in range(NZ)],
               "_about": "the paving of the Piazza and the Piazzetta: pale Istrian bands on grey trachyte, in tiles so no one triangle of it is vast"})
build.remove("piazza"); build.insert(0, "piazza")

doc = {"name": "St Mark's Basilica",
       "_about": "ST MARK'S BASILICA, Venice (1063-94; the lead domes about 1230, the Gothic crown about 1400): the five domes on a Greek cross, each a crossing under a `drum-dome` on the onion section, lantern and cross; the west front of "
                 "five deep portals, columns in two tiers and gold mosaic lunettes, the terrace and four horses, five arches under ogee gables with their leaves and statues, tabernacles between; the narthex; the Campanile, its Loggetta and the Piazza's paving. Generated by "
                 "tools/archgen/st_marks.py -- edit the script for arithmetic changes. West is -z, north +x.",
       "params": {"detail": 4}, "railing": {"type": "stone"}, "build": build, "parts": parts}
out = os.path.join(ROOT, "assets", "architecture", "st-marks.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts")
