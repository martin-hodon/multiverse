#!/usr/bin/env python3
"""THE EVERYDAY THINGS, SECOND BATCH (2026-11-21; docs/items.md "Everyday things (2026-11-21)"): what a household,
a yard, a farm, a bathroom, a schoolroom and a band use and the world still lacked -- written in tools/craftgen.py's
manner (its helpers, its frame, materials as roles, seeded `style`s where one item covers its old and its modern form):

- KITCHEN AND TABLE: the cooking pot (earthen, copper or a saucepan), the frying pan (cast iron or steel), the kettle
  (a copper hob kettle or an electric jug, its lid on a `hinge`), the bowl (wood or ceramic, `fill`), the goblet
  (pewter, silver or glass), the bottle (wine glass or salt-glazed stoneware), the ladle, the wooden spoon and the
  kitchen knife
- THE YARD: the wheelbarrow (wood on a cart wheel, or a steel tray on a tyre), the ladder (`n` rungs, `lean`), the
  watering can, the flowerpot (a `plant` from assets/items/flowers in it), the suitcase (leather or a hard shell, the
  lid a `hinge`), the coil of rope, the chain
- THE FARM: the plough (ard or mouldboard), the plunge butter churn, the rotary quern
- BATH AND MEDICINE: the washstand with its basin and ewer, the bathtub (clawfoot or built in), the toilet (lid
  hinged), the wheelchair, the crutch (underarm or forearm)
- SCHOOL: the globe on its stand
- MUSIC AND PLAY: the drum (tabor or snare), the ball (leather, football or beach ball), the guitar (classical or
  steel-strung), the trumpet (valved or natural)

    python3 tools/craftgen2.py      # -> assets/items/{tableware,tools,furniture,modern/furniture}/*.json + catalogue

THE FRAME is craftgen's: the origin on the floor (the table) under the thing's middle, y up; furniture's front +z; a
held tool's handle up its own +y (as the hammer's) unless said; an instrument's neck up +y, its face +z (the lute's).
"""
import fcntl, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "modern"))
from kit import box, rod, sphere, lathe, sweep as _sweep, plate, loft, hinge, euler, arc, r3, station_at
from craftgen import item, beam, band, ring, body_outline, smooth, write, D2R, LUTE_HOLD, ROOT

ITEMS2 = {}


# ---- helpers ----------------------------------------------------------------------------------------------------
def rat(outer, y):
    """the radius of a profile [[r, y]...] (rising) at height y"""
    for (r0, y0), (r1, y1) in zip(outer, outer[1:]):
        if y0 <= y <= y1 and y1 > y0: return r0 + (r1 - r0) * (y - y0) / (y1 - y0)
    return outer[-1][0] if y > outer[-1][1] else outer[0][0]


def shell(outer, t, floor=None):
    """a vessel's lathe profile from its OUTSIDE (foot to rim, [[r, y]...]): up the outside, over the rim, down the
    inside t in from it to the floor (`floor` high) and in to the axis -- one closed turned wall"""
    floor = t if floor is None else floor
    inner = [[round(max(0.002, r - t), 4), y] for r, y in reversed(outer) if y > floor + 1e-6]
    return [[0, 0]] + [list(q) for q in outer] + inner + [[round(max(0.002, rat(outer, floor) - t), 4), floor], [0, floor]]


def surface(id_, mat, outer, t, y, at=None, **k):
    """a level disc inside a vessel (its stew, its water, its soil) at height y: the inside's radius there"""
    return lathe(id_, mat, [[round(rat(outer, y) - t - 0.0006, 4), y], [0, y]], at, **k)


def sweep(id_, mat, path, r=None, section=None, **k):
    """kit's sweep, 3 samples a span unless said (items.js's default 6 is a lot on a spout or a handle)"""
    k.setdefault("seg", 3)
    return _sweep(id_, mat, path, r, section, **k)


def ringx(id_, mat, r, tube, at, sides=10, **k):
    """craftgen's ring with `r` and `tube` both expressions (a chain's links sized by its `link` param)"""
    prof = []
    for i in range(5):
        a = math.pi * 2 * i / 4
        prof.append([f"({r}) + ({tube}) * {round(math.cos(a), 5)}", f"({tube}) * {round(math.sin(a), 5)}"])
    return lathe(id_, mat, prof, at, sides=sides, caps=False, **k)


def _rot(axis, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    if axis == "x": return [[1, 0, 0], [0, c, -s], [0, s, c]]
    if axis == "y": return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def _mm(A, B): return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def orient(pos, *rots):
    """an `at` turned by rotations ("x"|"y"|"z", degrees) applied IN THE ORDER GIVEN about the parent's axes -- a
    side board leaned out and then the whole tray tipped, which items.js's one yaw-pitch-roll cannot say"""
    M = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    for ax, d in rots: M = _mm(_rot(ax, d), M)
    return [*pos, *euler([M[r][0] for r in range(3)], [M[r][1] for r in range(3)], [M[r][2] for r in range(3)])]


def _n(v):
    l = math.sqrt(sum(c * c for c in v)) or 1
    return [c / l for c in v]


def _x(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def toward(pos, d):
    """an `at` at pos whose own +y points along d (a lathe's axis: a rose on a spout, a cap on a globe)"""
    ya = _n(d)
    hint = [0, 0, 1] if abs(ya[2]) < 0.9 else [1, 0, 0]
    xa = _n(_x(ya, hint)); za = _x(xa, ya)
    return [*pos, *euler(xa, ya, za)]


def cap(id_, mat, R, ang, at, sides=8, rings=2, **k):
    """a spherical cap of angular radius `ang` degrees on a ball of radius R, round its own +y: a continent on a
    globe, a pentagon on a football (sides 5)"""
    prof = [[0, R]] + [[round(R * math.sin(math.radians(ang * i / rings)), 5), round(R * math.cos(math.radians(ang * i / rings)), 5)] for i in range(1, rings + 1)]
    return lathe(id_, mat, list(reversed(prof)), at, sides=sides, caps=False, **k)


def flat_at(pos, tilt=0.0, yaw=0.0):
    """the `at` laying a plate flat (its outline's x along +x, its y toward -z, its face up), then tipped up `tilt`
    degrees about z (a pan's handle rising) and turned `yaw` about y"""
    return orient(pos, ("x", -90), ("z", tilt), ("y", yaw))


# ==== KITCHEN AND TABLE ============================================================================================
# ---- THE COOKING POT (`style`): an EARTHEN pot (the olla of every hearth: round-bellied, a rolled rim, two lugs), a
# COPPER marmite (straight-sided, riveted iron handles, a lid with a loop) or a modern steel SAUCEPAN (a long black
# handle along +x, a lid with a knob); `lid` on or off, the stew in it when `fill`
EARTH = [[0.07, 0], [0.1, 0.018], [0.121, 0.06], [0.127, 0.1], [0.117, 0.145], [0.097, 0.172], [0.095, 0.186], [0.104, 0.2]]
COPPER = [[0.118, 0], [0.128, 0.008], [0.13, 0.17], [0.134, 0.18]]
PAN = [[0.085, 0], [0.09, 0.006], [0.09, 0.105], [0.093, 0.11]]


def cooking_pot():
    E, C, S = {"style": "earthen"}, {"style": "copper"}, {"style": "saucepan"}
    lidE, lidC, lidS = [{**w, "lid": 1} for w in (E, C, S)]
    bare = lambda w: {**w, "lid": [0]}
    # (the lid on (`lid` 1) is hinged at its far edge, -x, and tipped up 75 degrees by `open`, as a cook lifts it by
    #  the knob; the stew under it is then `inside`, seen only open -- a pot without its lid shows it always)
    def stew(id_, outer, t, y, w):
        return [{**surface(id_, "stew", outer, t, y, sides=12), "when": bare(w)}, {**surface(id_ + "In", "stew", outer, t, y, sides=12), "when": {**w, "lid": 1}, "inside": True}]
    return item("Cooking pot", "tableware", "a cooking pot: an earthen one with a rolled rim and two lugs (style earthen), a straight-sided copper marmite with riveted handles (copper) or a modern steel saucepan with a long handle along +x (saucepan); its lid on (`lid`), hinged at its far edge and tipped up by `open` onto the stew in it (`fill`)",
        {"style": {"pick": ["earthen", "earthen", "copper", "saucepan"]}, "lid": {"pick": [0, 1]}, "fill": {"pick": [0, 1, 1]}, "open": 0},
        {"clay": {"pick": ["terracotta", "terracotta", "stoneware"]}, "copper": "copper-bright", "steel": "steel", "iron": "iron", "grip": "plastic-black",
         "stew": {"pick": ["crust-dark", "bean", "carrot", "pea"]}, "brass": "brass"}, [
            lathe("earthen", "clay", shell(EARTH, 0.007), sides=16, when=E),
            *stew("stewE", EARTH, 0.007, 0.13, E),
            ring("rimE", "clay", 0.104, 0.006, [0, 0.198, 0], sides=16, when=E),
            sweep("lugs", "clay", [[0.112, 0.168, 0], [0.142, 0.165, 0], [0.15, 0.148, 0], [0.12, 0.135, 0]], r=0.008, sides=5, mirror="x", when=E),
            hinge("lidE", [-0.104, 0.2, 0], [
                lathe("lidE", "clay", [[0.103, 0.2], [0.103, 0.206], [0.07, 0.222], [0.025, 0.232], [0.02, 0.244], [0.014, 0.25], [0, 0.25]], sides=16),
            ], axis=(0, 0, 1), max_=75, when=lidE),
            # the copper marmite, its handles riveted on the sides, the lid with a loop
            lathe("copper", "copper", shell(COPPER, 0.0035), sides=20, when=C),
            *stew("stewC", COPPER, 0.0035, 0.12, C),
            sweep("handlesC", "iron", [[0.13, 0.152, -0.04], [0.165, 0.157, -0.032], [0.172, 0.157, 0], [0.165, 0.157, 0.032], [0.13, 0.152, 0.04]], r=0.006, sides=5, mirror="x", when=C),
            box("rivetsC", "brass", [0.004, 0.024, 0.012], [[0.131, 0.152, 0.04], [0.131, 0.152, -0.04], [-0.131, 0.152, 0.04], [-0.131, 0.152, -0.04]], when=C),
            hinge("lidC", [-0.136, 0.18, 0], [
                lathe("lidC", "copper", [[0.136, 0.18], [0.136, 0.186], [0.1, 0.194], [0.03, 0.2], [0, 0.2]], sides=20),
                sweep("lidLoop", "brass", [[-0.03, 0.199, 0], [-0.025, 0.222, 0], [0.025, 0.222, 0], [0.03, 0.199, 0]], r=0.0045, sides=5),
            ], axis=(0, 0, 1), max_=75, when=lidC),
            # the saucepan
            lathe("saucepan", "steel", shell(PAN, 0.0025), sides=20, when=S),
            *stew("stewS", PAN, 0.0025, 0.075, S),
            box("strap", "steel", [0.07, 0.006, 0.02], [0.115, 0.096, 0, 0, 0, 12], when=S),
            rod("grip", "grip", 0.013, [0.15, 0.11, 0], [0.31, 0.144, 0], 8, r1=0.016, stretch=[1, 0.8, 1], when=S),
            hinge("lidS", [-0.095, 0.11, 0], [
                lathe("lidS", "steel", [[0.095, 0.11], [0.095, 0.115], [0.06, 0.125], [0, 0.128]], sides=20),
                lathe("knobS", "grip", [[0.012, 0.127], [0.016, 0.135], [0.018, 0.145], [0, 0.148]], sides=8),
            ], axis=(0, 0, 1), max_=75, when=lidS),
        ], hold={"grip": [0, 0.2, 0], "axis": [1, 0, 0], "face": [0, 0, 1], "carry": {"axis": [0, 0, 1], "face": [1, 0, 0]}},
        era="-3000-2030", region="everywhere")


# ---- THE FRYING PAN (`style`): a cast-IRON skillet (thick, a short cast handle with its hanging hole) or a modern
# STEEL pan (flared thin wall, its dark non-stick floor, a long riveted handle), the handle along +x; `egg` two eggs
# frying in it
SKILLET = [[0.108, 0], [0.122, 0.004], [0.133, 0.045], [0.136, 0.05]]
FRYPAN = [[0.098, 0], [0.104, 0.003], [0.13, 0.045], [0.133, 0.048]]


def frying_pan():
    I, S = {"style": "iron"}, {"style": "steel"}
    egg = lambda id_, w, y: [lathe(id_ + "White", "eggWhite", [[0.045, y], [0.04, y + 0.004], [0, y + 0.005]], [[0.04, 0, -0.03], [-0.035, 0, 0.035]], sides=10, stretch=[1, 1, 0.85], when=w),
                             sphere(id_ + "Yolk", "yolk", 0.016, [[0.043, y + 0.005, -0.028], [-0.032, y + 0.005, 0.037]], sides=8, stretch=[1, 0.5, 1], when=w)]
    return item("Frying pan", "tableware", "a frying pan, its handle along +x: a cast-iron skillet with a short cast handle and its hanging hole (style iron), or a modern steel pan, its dark non-stick floor, a long riveted handle (steel); two eggs frying in it with `egg`",
        {"style": {"pick": ["iron", "iron", "steel"]}, "egg": {"pick": [0, 0, 1]}},
        {"iron": "iron", "steel": {"pick": ["steel", "aluminium"]}, "coat": "plastic-black", "grip": {"pick": ["plastic-black", "walnut"]}, "dark": "mouth-dark",
         "eggWhite": "egg-white", "yolk": "paint-yellow"}, [
            lathe("skillet", "iron", shell(SKILLET, 0.006), sides=20, when=I),
            plate("handleI", "iron", [[0.12, -0.022], [0.2, -0.016], [0.27, -0.017], [0.29, -0.012], [0.295, 0], [0.29, 0.012], [0.27, 0.017], [0.2, 0.016], [0.12, 0.022]], 0.008,
                  flat_at([0, 0.043, 0], 10), when=I),
            lathe("hole", "dark", [[0.0055, -0.0045], [0.0055, 0.0045]], [0.275 * math.cos(math.radians(10)), 0.043 + 0.275 * math.sin(math.radians(10)), 0, 0, 0, 10], sides=8, when=I),
            lathe("pan", "steel", shell(FRYPAN, 0.0025), sides=20, when=S),
            lathe("coat", "coat", [[0.1, 0.0032], [0, 0.0032]], sides=20, when=S),
            rod("shank", "steel", 0.007, [0.12, 0.042, 0], [0.19, 0.06, 0], 6, when=S),
            rod("gripS", "grip", 0.013, [0.18, 0.058, 0], [0.36, 0.09, 0], 8, r1=0.011, stretch=[1, 0.75, 1], when=S),
            sphere("rivets", "steel", 0.004, [[0.125, 0.04, 0.012], [0.125, 0.04, -0.012]], sides=6, when=S),
            *egg("egg", {"egg": 1, "style": ["iron", "steel"]}, 0.007),
        ], hold={"grip": [0.25, 0.06, 0], "axis": [1, 0, 0], "face": [0, 1, 0], "carry": {"axis": [1, -0.3, 0], "face": [0, 1, 0]}, "follow": 0.7},
        era="-500-2030", region="everywhere")


# ---- THE KETTLE (`style`): a COPPER hob kettle (squat, a gooseneck spout at +x, a fixed arched handle over the lid
# with its wooden grip, the lid domed and knobbed) or an ELECTRIC jug kettle (a tapered body on its power base, the
# water window, the handle at -x, the spout's notch at +x, its flip lid on a `hinge` at the back)
KBODY = [[0.085, 0], [0.104, 0.01], [0.116, 0.05], [0.112, 0.095], [0.088, 0.13], [0.056, 0.148]]


def kettle():
    C, E = {"style": "copper"}, {"style": "electric"}
    return item("Kettle", "tableware", "a kettle: a copper hob kettle, squat, a gooseneck spout at +x, a fixed arched handle over the domed lid (style copper), or an electric jug kettle on its power base, a water window, the handle at -x and a flip lid hinged at the back (electric; `open` lifts it)",
        {"style": {"pick": ["copper", "copper", "electric"]}, "open": 0},
        {"copper": {"pick": ["copper-bright", "copper-bright", "brass"]}, "wood": {"pick": ["ebony", "walnut"]}, "body": {"pick": ["steel", "plastic-white", "paint-red", "paint-black"]},
         "plastic": "plastic-black", "window": "glass-light", "steel": "steel"}, [
            lathe("body", "copper", KBODY + [[0.056, 0.15], [0, 0.15]], sides=18, when=C),
            lathe("lid", "copper", [[0.058, 0.148], [0.058, 0.153], [0.04, 0.163], [0.012, 0.168], [0.011, 0.176], [0.017, 0.183], [0.01, 0.19], [0, 0.19]], sides=14, when=C),
            sweep("spout", "copper", [[0.095, 0.035, 0], [0.135, 0.055, 0], [0.165, 0.095, 0], [0.19, 0.14, 0], [0.205, 0.155, 0]], radii=[0.019, 0.014, 0.011, 0.009, 0.008], sides=8, when=C),
            sweep("handle", "copper", [[-0.075, 0.12, 0], [-0.085, 0.2, 0], [-0.04, 0.25, 0], [0.04, 0.25, 0], [0.085, 0.2, 0], [0.075, 0.12, 0]], r=0.0065, sides=6, when=C),
            rod("handleGrip", "wood", 0.014, [-0.05, 0.25, 0], [0.05, 0.25, 0], 8, when=C),
            band("foot", "copper", 0.086, 0.01, 0.003, [0, 0.004, 0], sides=18, when=C),
            # the electric jug: its base, body, window, handle and spout, the lid hinged at -x
            lathe("base", "plastic", [[0, 0], [0.098, 0], [0.098, 0.018], [0, 0.018]], sides=18, when=E),
            lathe("jug", "body", [[0, 0.018], [0.082, 0.018], [0.086, 0.028], [0.08, 0.2], [0.072, 0.232], [0, 0.232]], sides=18, when=E),
            box("window", "window", [0.012, 0.13, 0.03], [0.07, 0.11, 0.045, 50, 0, 0], when=E),
            plate("spoutLip", "body", [[0.06, 0.205], [0.105, 0.236], [0.066, 0.236]], 0.036, when=E),
            sweep("jugHandle", "plastic", [[-0.075, 0.2, 0], [-0.13, 0.19, 0], [-0.135, 0.07, 0], [-0.082, 0.05, 0]], section=[0.03, 0.022], sides=4, when=E),
            box("switch", "plastic", [0.02, 0.01, 0.016], [-0.12, 0.04, 0], when=E),
            hinge("flip", [-0.06, 0.234, 0], [
                lathe("flipLid", "plastic", [[0, 0.232], [0.066, 0.232], [0.064, 0.24], [0.04, 0.245], [0, 0.246]], sides=16, when=E),
                box("lidButton", "body", [0.022, 0.005, 0.016], [-0.045, 0.2475, 0], when=E),
            ], axis=(0, 0, 1), max_=85),
        ], hold={"grip": [0, 0.25, 0], "axis": [1, 0, 0], "face": [0, 0, 1], "carry": {"axis": [0, 0, 1], "face": [1, 0, 0]}},
        era="1700-2030", region="everywhere")


# ---- THE BOWL (`style`): a turned WOODEN bowl, or a CERAMIC one on its foot ring with a band painted round it; the
# porridge, soup or peas in it when `fill` (the mug's way: what you see in it, its level fixed)
WBOWL = [[0.045, 0], [0.052, 0.006], [0.074, 0.024], [0.089, 0.048], [0.095, 0.066]]
CBOWL = [[0.042, 0], [0.043, 0.007], [0.046, 0.009], [0.062, 0.025], [0.083, 0.052], [0.089, 0.068]]


def bowl():
    W, C = {"style": "wood"}, {"style": "ceramic"}
    return item("Bowl", "tableware", "a bowl: turned from a wood (style wood) or ceramic on its foot ring, a band painted round it (ceramic); porridge, soup or peas in it with `fill`",
        {"style": {"pick": ["wood", "ceramic"]}, "fill": {"pick": [0, 1, 1]}},
        {"wood": {"pick": ["birch", "ash", "oak", "walnut", "cherry"]}, "glaze": {"pick": ["faience-white", "paint-cream", "terracotta", "faience-blue", "stoneware"]},
         "band": {"pick": ["enamel-blue", "faience-green", "enamel-red", "paint-navy"]}, "food": {"pick": ["paint-cream", "carrot", "pea", "bean", "crust"]}}, [
            lathe("woodBowl", "wood", shell(WBOWL, 0.007, 0.009), sides=18, when=W),
            {**surface("foodW", "food", WBOWL, 0.007, 0.045, sides=14), "when": {"style": "wood", "fill": 1}},
            lathe("ceramicBowl", "glaze", shell(CBOWL, 0.004, 0.006), sides=18, when=C),
            lathe("band", "band", [[0.0805, 0.0475], [0.0855, 0.0565]], sides=18, caps=False, when=C),
            {**surface("foodC", "food", CBOWL, 0.004, 0.048, sides=14), "when": {"style": "ceramic", "fill": 1}},
        ], hold={"grip": [0, 0.03, 0], "axis": [0, 0, 1], "face": [0, 1, 0], "carry": {"axis": [1, 0, 0], "face": [0, 1, 0]}, "follow": 0.7},
        era="any", region="everywhere")


# ---- THE GOBLET (`style`): a PEWTER goblet (a heavy foot, a knopped stem), a SILVER chalice-shaped one (gilt within)
# or a GLASS one (window-glass: you see the wine in it); `fill` the wine
GOB = [[0.038, 0], [0.039, 0.004], [0.03, 0.009], [0.013, 0.02], [0.008, 0.04], [0.015, 0.055], [0.008, 0.07], [0.011, 0.088], [0.03, 0.098],
       [0.041, 0.118], [0.044, 0.148], [0.046, 0.17]]
GLASS = [[0.035, 0], [0.035, 0.003], [0.01, 0.006], [0.0045, 0.015], [0.0045, 0.07], [0.012, 0.085], [0.03, 0.1], [0.04, 0.125], [0.042, 0.155], [0.04, 0.18]]


def goblet():
    M, G = {"style": ["pewter", "silver"]}, {"style": "glass"}
    wine = lambda prof, t, y0, y1, w: lathe("wine" + ("G" if w == G else ""), "wine", [[0, y0], [round(rat(prof, y0) - t - 0.001, 4), y0]] +
                                            [[round(rat(prof, y) - t - 0.0008, 4), y] for y in (y0 + (y1 - y0) * f for f in (0.33, 0.66, 1.0))] + [[0, y1]],
                                            sides=14, when={**w, "fill": 1})
    return item("Goblet", "tableware", "a goblet: pewter with a heavy foot and a knopped stem (style pewter), silver (silver), or blown glass you see the wine in (glass: window-glass); the wine in it with `fill`",
        {"style": {"pick": ["pewter", "pewter", "silver", "glass"]}, "fill": {"pick": [0, 1]}},
        {"metal": "pewter", "silver": "silver", "glass": "window-glass", "wine": {"pick": ["cherry-red", "cherry-red", "grape-purple"]}}, [
            lathe("pewter", "metal", shell(GOB, 0.003, 0.1), sides=16, when={"style": "pewter"}),
            lathe("silver", "silver", shell(GOB, 0.0025, 0.1), sides=16, when={"style": "silver"}),
            ring("knop", "silver", 0.014, 0.004, [0, 0.055, 0], sides=12, when={"style": "silver"}),
            wine(GOB, 0.003, 0.1, 0.14, M),
            lathe("glass", "glass", shell(GLASS, 0.0015, 0.088), sides=16, when=G),
            wine(GLASS, 0.0015, 0.088, 0.14, G),
        ], hold={"grip": [0, 0.05, 0], "axis": [0, 1, 0], "face": [1, 0, 0], "carry": {"axis": [0, 1, 0], "face": [1, 0, 0]}, "follow": 0.7},
        era="1200-2030", region="Europe")


# ---- THE BOTTLE (`style`): a WINE bottle of dark green or brown glass, corked, a paper label on some (`label`), or a
# salt-glazed STONEWARE bottle (the Bartmann jug of the Rhineland: round-bellied, a narrow neck, a loop handle at -x and
# the bearded mask on its neck at +x)
def bottle():
    W, S = {"style": "wine"}, {"style": "stoneware"}
    return item("Bottle", "tableware", "a bottle: a corked wine bottle of dark green or brown glass, a paper label on some (style wine, `label`), or a salt-glazed stoneware Bartmann bottle, round-bellied, a loop handle at -x and the bearded mask on its neck at +x (stoneware)",
        {"style": {"pick": ["wine", "wine", "stoneware"]}, "label": {"pick": [0, 1]}},
        {"glass": {"pick": ["glass-green", "glass", "glass", "amber"]}, "cork": "pine", "label": {"pick": ["paint-cream", "faience-white"]}, "ware": "stoneware"}, [
            lathe("wine", "glass", [[0, 0.004], [0.03, 0], [0.036, 0.004], [0.037, 0.19], [0.034, 0.21], [0.022, 0.24], [0.0155, 0.265], [0.0145, 0.288], [0.017, 0.29], [0.017, 0.298], [0.012, 0.3], [0, 0.3]],
                  sides=14, when=W),
            lathe("cork", "cork", [[0.012, 0.3], [0.012, 0.31], [0, 0.31]], sides=8, when=W),
            lathe("labelBand", "label", [[0.0375, 0.07], [0.0375, 0.15]], sides=14, caps=False, when={"style": "wine", "label": 1}),
            lathe("bartmann", "ware", [[0, 0], [0.045, 0], [0.05, 0.008], [0.073, 0.06], [0.08, 0.1], [0.07, 0.15], [0.042, 0.182], [0.023, 0.198], [0.021, 0.222], [0.026, 0.23],
                                       [0.02, 0.233], [0, 0.23]], sides=14, when=S),
            sweep("handleS", "ware", [[-0.022, 0.21, 0], [-0.05, 0.208, 0], [-0.064, 0.18, 0], [-0.058, 0.162, 0]], r=0.007, sides=5, when=S),
            sphere("mask", "ware", 0.022, [0.037, 0.178, 0], sides=8, stretch=[0.35, 1.1, 0.9], when=S),
            lathe("stopper", "cork", [[0.017, 0.226], [0.017, 0.238], [0, 0.238]], sides=8, when=S),
        ], hold={"grip": [0, 0.14, 0], "axis": [0, 1, 0], "face": [1, 0, 0], "carry": {"axis": [0, 1, 0], "face": [1, 0, 0]}},
        era="1500-2030", region="Europe")


# ---- THE LADLE (`style`): a hearth's IRON ladle (a hemispherical bowl, a long flat handle ending in a hook) or a
# carved WOODEN one -- hung: its handle up +y, the bowl at the foot opening toward +z
def ladle():
    I, W = {"style": "iron"}, {"style": "wood"}
    bowlP = lambda R, t: [[0, -R], [R * 0.55, -R * 0.88], [R * 0.88, -R * 0.52], [R, 0], [R - t, 0], [(R - t) * 0.88, -(R - t) * 0.52], [(R - t) * 0.55, -(R - t) * 0.88], [0, -(R - t)]]
    return item("Ladle", "tool", "a ladle hung on its hook: an iron hearth ladle with a hemispherical bowl and a long flat handle ending in a hook (style iron), or a carved wooden one (wood) -- the handle up +y, the bowl at the foot opening toward +z",
        {"style": {"pick": ["iron", "wood"]}},
        {"iron": {"pick": ["iron", "steel", "copper-bright"]}, "wood": {"pick": ["birch", "ash", "cherry", "oak"]}}, [
            lathe("bowlI", "iron", bowlP(0.045, 0.002), [0, 0.045, 0, 0, 90, 0], sides=14, when=I),
            sweep("handleI", "iron", [[0, 0.088, -0.004], [0, 0.15, 0.012], [0, 0.3, 0.02], [0, 0.4, 0.016]], section=[0.014, 0.0035], up=[0, 0, 1], when=I),
            sweep("hook", "iron", [[0, 0.395, 0.016], [0, 0.425, 0.012], [0, 0.432, -0.005], [0, 0.415, -0.012]], r=0.003, sides=5, when=I),
            lathe("bowlW", "wood", bowlP(0.04, 0.005), [0, 0.04, 0, 0, 90, 0], sides=12, stretch=[1, 1.15, 1], when=W),
            sweep("handleW", "wood", [[0, 0.085, -0.008], [0, 0.13, 0.008], [0, 0.25, 0.014], [0, 0.33, 0.012]], radii=[0.011, 0.008, 0.008, 0.009], sides=6, when=W),
        ], hold={"grip": [0, 0.3, 0.014], "axis": [0, 1, 0], "face": [0, 0, 1], "carry": {"axis": [0, -1, 0.2], "face": [0, 0, 1]}},
        era="any", region="everywhere")


# ---- THE WOODEN SPOON: a long round handle into a shallow oval bowl, carved from one piece -- the handle up +y, the
# bowl at the foot, hollow toward +z
def wooden_spoon():
    return item("Wooden spoon", "tool", "a cook's wooden spoon carved from one piece: a long round handle into a shallow oval bowl -- the handle up +y, the bowl at the foot, hollow toward +z",
        {"L": [0.28, 0.34]},
        {"wood": {"pick": ["birch", "ash", "cherry", "oak", "walnut"]}}, [
            lathe("bowl", "wood", [[0, -0.011], [0.016, -0.009], [0.025, -0.004], [0.028, 0.0], [0.024, 0.001], [0.015, -0.004], [0, -0.006]], [0, 0.034, 0, 0, 90, 0], sides=12, stretch=[1, 1.45, 1]),
            rod("neck", "wood", 0.0055, [0, 0.07, 0.0], [0, 0.11, 0.002], 6, r1=0.0065),
            rod("handle", "wood", 0.0065, [0, 0.11, 0.002], [0, "L", 0.004], 6, r1=0.0085),
            sphere("end", "wood", 0.0085, [0, "L", 0.004], sides=6),
        ], hold={"grip": [0, 0.22, 0], "axis": [0, 1, 0], "face": [0, 0, 1], "carry": {"axis": [0, -1, 0.2], "face": [0, 0, 1]}},
        era="any", region="everywhere")


# ---- THE KITCHEN KNIFE (`style`): a modern CHEF's knife (a broad blade curving to the tip, a bolster, a black handle
# with three rivets) or an OLD one (a narrow iron blade, wooden scales, brass rivets) -- the handle up +y, its edge +x
def kitchen_knife():
    C, O = {"style": "chef"}, {"style": "old"}
    return item("Kitchen knife", "tool", "a kitchen knife, the handle up +y and its edge toward +x: a chef's knife with a broad blade curving to the tip, a bolster and a riveted black handle (style chef), or an old one with a narrow iron blade, wooden scales and brass rivets (old)",
        {"style": {"pick": ["chef", "old"]}},
        {"steel": "steel", "iron": "iron", "handle": {"pick": ["plastic-black", "walnut", "ebony"]}, "scales": {"pick": ["walnut", "oak", "bone", "horn"]}, "rivet": "brass"}, [
            plate("blade", "steel", [[-0.004, 0.115], [0.042, 0.115], [0.043, 0.16], [0.036, 0.23], [0.02, 0.28], [-0.004, 0.32], [-0.004, 0.2]], 0.0022, when=C),
            box("bolster", "steel", [0.046, 0.012, 0.01], [0.018, 0.112, 0], when=C),
            box("handleC", "handle", [0.026, 0.11, 0.017], [0.01, 0.052, 0], when=C),
            rod("rivetsC", "steel", 0.0028, [0, 0, -0.009], [0, 0, 0.009], 6, at=[[0.01, 0.025, 0], [0.01, 0.055, 0], [0.01, 0.085, 0]], when=C),
            plate("bladeO", "iron", [[-0.003, 0.105], [0.022, 0.105], [0.021, 0.2], [0.014, 0.25], [-0.003, 0.275], [-0.003, 0.2]], 0.0025, when=O),
            box("scales", "scales", [0.022, 0.105, 0.016], [0.008, 0.052, 0], when=O),
            rod("rivetsO", "rivet", 0.0028, [0, 0, -0.0085], [0, 0, 0.0085], 6, at=[[0.008, 0.02, 0], [0.008, 0.075, 0]], when=O),
        ], hold={"grip": [0.01, 0.055, 0], "axis": [0, 1, 0], "face": [1, 0, 0], "carry": {"axis": [0.1, -1, 0], "face": [1, 0, 0]}},
        era="any", region="everywhere")


# ==== THE YARD =====================================================================================================
# ---- THE WHEELBARROW (`style`): a WOODEN barrow (two shafts running forward to the wheel -- a small cart wheel, its
# axle between them -- a board tray on them with sloped sides and a forward-leaning front, two legs) or a STEEL one (a
# pressed steel tray, its rolled rim, on a tubular frame, a tyred wheel, the handles' grips). Its wheel at +x; resting
# on legs and wheel, the handles at -x
def wheelbarrow():
    W, S = {"style": "wood"}, {"style": "steel"}
    ax, ay = 0.56, 0.2                           # (the axle)
    hx, hy, hz = -0.78, 0.5, 0.27                # (the handles' ends)
    sh = lambda f, sz: [hx + (ax - hx) * f, hy + (ay - hy) * f, sz * (hz + (0.13 - hz) * f)]
    tilt = math.degrees(math.atan2(hy - ay, ax - hx)) * -1   # (the shafts' slope: the tray sits along them)
    def T(x, y, z=0.0):   # (a point of the tray's own frame -- x along the shafts, y up from their top -- in the item's)
        c, s = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        bx, by = -0.2, 0.43
        return [round(bx + x * c - y * s, 4), round(by + x * s + y * c, 4), z]
    sideO = [[-0.33, 0], [0.22, 0], [0.4, 0.26], [-0.42, 0.26]]
    # the steel tray: a loft along x, open at the top, seen from inside too
    st = [[-0.42, 0.19, 0.46, 0.72, 0.29], [-0.3, 0.22, 0.42, 0.72, 0.33], [0.05, 0.22, 0.4, 0.72, 0.34], [0.28, 0.17, 0.48, 0.72, 0.33], [0.5, 0.08, 0.67, 0.72, 0.27]]
    rim = [[x, 0.72, round(station_at(st, x)[4] + 0.004, 4)] for x in (0.5, 0.3, 0.1, -0.1, -0.3, -0.42)]
    rim = rim + [[x, y, -z] for x, y, z in reversed(rim)]
    return item("Wheelbarrow", "tool", "a wheelbarrow, its wheel at +x and the handles at -x, resting on two legs: a wooden one, two shafts running forward to a small cart wheel, a board tray on them with sloped sides and a forward-leaning front (style wood), or a steel one, a pressed tray with a rolled rim on a tubular frame, a tyred wheel (steel)",
        {"style": {"pick": ["wood", "wood", "steel"]}},
        {"wood": {"pick": ["oak", "ash", "oak-grey"]}, "boards": {"pick": ["planks", "planks-grey", "pine"]}, "iron": "iron",
         "tray": {"pick": ["paint-green", "paint-red", "aluminium", "paint-black", "paint-orange"]}, "frame": {"pick": ["paint-black", "steel", "paint-green"]},
         "tyre": "rubber", "hub": {"pick": ["paint-red", "paint-yellow", "steel"]}, "grip": "plastic-black"}, [
            # the wooden barrow
            beam("shaftL", "wood", sh(0, -1), sh(1.08, -1), 0.05, 0.06, when=W),
            beam("shaftR", "wood", sh(0, 1), sh(1.08, 1), 0.05, 0.06, when=W),
            {"id": "wheel", "use": "items/components/cart-wheel", "at": [ax, ay, 0], "params": {"r": ay, "n": 8}, "when": W},
            rod("axle", "iron", 0.012, [ax, ay, -0.14], [ax, ay, 0.14], 6, when=W),
            beam("legL", "wood", sh(0.3, -1), [sh(0.3, -1)[0] - 0.05, 0, -0.25], 0.045, 0.045, when=W),
            beam("legR", "wood", sh(0.3, 1), [sh(0.3, 1)[0] - 0.05, 0, 0.25], 0.045, 0.045, when=W),
            box("stay", "wood", [0.04, 0.04, 0.48], [sh(0.3, 1)[0] - 0.025, 0.13, 0], when=W),
            box("trayFloor", "boards", [0.58, 0.022, 0.42], orient(T(-0.06, 0.011), ("z", tilt)), when=W),
            plate("sideR", "boards", sideO, 0.02, orient(T(0, 0.0, 0.215), ("x", 22), ("z", tilt)), when=W),
            plate("sideL", "boards", sideO, 0.02, orient(T(0, 0.0, -0.215), ("x", -22), ("z", tilt)), when=W),
            box("front", "boards", [0.02, 0.3, 0.56], orient(T(0.31, 0.13), ("z", -34 + tilt)), when=W),
            box("back", "boards", [0.02, 0.2, 0.46], orient(T(-0.36, 0.1), ("z", 12 + tilt)), when=W),
            box("straps", "iron", [0.04, 0.006, 0.6], [orient(T(-0.25, 0.024), ("z", tilt)), orient(T(0.15, 0.024), ("z", tilt))], when=W),
            # the steel barrow: its tray, rim, frame, legs and wheel
            loft("tray", "tray", st, round_=0.08, bare=["top"], double=True, seg=2, corner=2, when=S),
            sweep("rim", "tray", rim + [rim[0]], r=0.011, sides=6, when=S),
            sweep("frameR", "frame", [[hx, hy, hz], [-0.45, 0.43, 0.23], [0.0, 0.36, 0.16], [0.35, 0.28, 0.09], [ax, ay + 0.02, 0.07]], r=0.016, sides=6, when=S),
            sweep("frameL", "frame", [[hx, hy, -hz], [-0.45, 0.43, -0.23], [0.0, 0.36, -0.16], [0.35, 0.28, -0.09], [ax, ay + 0.02, -0.07]], r=0.016, sides=6, when=S),
            sweep("legsS", "frame", [[-0.3, 0.4, -0.2], [-0.34, 0.02, -0.22], [-0.34, 0.02, 0.22], [-0.3, 0.4, 0.2]], r=0.014, sides=6, when=S),
            rod("brace", "frame", 0.012, [-0.05, 0.37, -0.17], [-0.05, 0.37, 0.17], 6, when=S),
            rod("grips", "grip", 0.019, [hx - 0.1, hy + 0.02, 0], [hx + 0.04, hy - 0.006, 0], 8, at=[[0, 0, hz], [0, 0, -hz]], when=S),
            ring("tyre", "tyre", 0.155, 0.042, [ax, ay, 0, 0, 90, 0], sides=18, stretch=[1, 1, 1.1], when=S),
            lathe("rimDisc", "hub", [[0.12, -0.035], [0.11, -0.02], [0.05, -0.03], [0.03, -0.05], [0, -0.05]], [ax, ay, 0, 0, 90, 0], sides=14, when=S),
            lathe("rimDisc2", "hub", [[0.12, 0.035], [0.11, 0.02], [0.05, 0.03], [0.03, 0.05], [0, 0.05]], [ax, ay, 0, 0, -90, 0], sides=14, when=S),
        ], hold={"grip": [hx + 0.02, hy, hz], "grip2": [hx + 0.02, hy, -hz], "axis": [0, 0, 1], "face": [1, 0, 0], "carry": {"axis": [0, 0, 1], "face": [1, 0, 0]}},
        era="1200-2030", region="everywhere")


# ---- THE LADDER: two rails and `n` round rungs a foot apart, in wood (oak rails, ash rungs) or ALUMINIUM (box rails,
# rubber feet); leaned `lean` degrees back toward -z about its feet (against the wall)
def ladder():
    c, s = f"cos(lean * {D2R})", f"sin(lean * {D2R})"
    P = lambda x, d: [x, f"({d}) * {c}", f"0 - ({d}) * {s}"]
    rail = lambda id_, mat, x, w, d, **k: box(id_, mat, [w, "L", d], [x, f"L * 0.5 * {c}", f"0 - L * 0.5 * {s}", 0, "0 - lean", 0], **k)
    W, A = {"style": "wood"}, {"style": "aluminium"}
    return item("Ladder", "tool", "a ladder: two rails and `n` round rungs 0.28 m apart -- wooden (style wood) or aluminium with box rails and rubber feet (aluminium) -- leaned `lean` degrees back toward -z about its feet (against a wall)",
        {"style": {"pick": ["wood", "wood", "aluminium"]}, "n": {"pick": [6, 8, 10, 12]}, "L": "n * 0.28 + 0.12", "lean": 0},
        {"rail": {"pick": ["oak", "pine", "ash", "oak-grey"]}, "rung": {"pick": ["ash", "oak"]}, "alu": "aluminium", "foot": "rubber"}, [
            rail("railsW", "rail", -0.22, 0.035, 0.07, mirror="x", when=W),
            rod("rungsW", "rung", 0.016, [-0.245, 0, 0], [0.245, 0, 0], 6, at=[0, 0, 0], along={"n": "n", "from": P(0, 0.2), "to": P(0, "L - 0.2")}, when=W),
            rail("railsA", "alu", -0.21, 0.025, 0.065, mirror="x", when=A),
            rod("rungsA", "alu", 0.016, [-0.21, 0, 0], [0.21, 0, 0], 6, at=[0, 0, 0], stretch=[1, 1, 1.25], along={"n": "n", "from": P(0, 0.2), "to": P(0, "L - 0.2")}, when=A),
            box("feet", "foot", [0.04, 0.05, 0.09], [[-0.21, 0.025, 0], [0.21, 0.025, 0]], when=A),
        ], hold={"grip": [0.22, 0.9, 0], "axis": [0, 1, 0], "face": [1, 0, 0], "carry": {"axis": [1, 0, 0], "face": [0, 1, 0]}, "follow": 0.3},
        era="any", region="everywhere")


# ---- THE WATERING CAN: an oval galvanised (or painted, or copper) body, the filling hole on top, the long spout from
# its foot at +x to the ROSE, its stay to the body, the top handle and the back handle
def watering_can():
    sp0, sp1 = [0.1, 0.04, 0], [0.43, 0.34, 0]
    d = [sp1[i] - sp0[i] for i in range(3)]
    return item("Watering can", "tool", "a watering can: an oval galvanised, painted or copper body, the filling hole on top, the long spout from its foot at +x to the rose, a stay to the body, the top handle arching over and the back handle",
        {}, {"metal": {"pick": ["aluminium", "aluminium", "paint-green", "copper-bright", "paint-red"]}, "rose": {"pick": ["brass", "aluminium"]}, "dark": "mouth-dark"}, [
            lathe("body", "metal", [[0, 0], [0.105, 0], [0.11, 0.012], [0.11, 0.235], [0.1, 0.258], [0.06, 0.272], [0, 0.274]], sides=16, stretch=[1.2, 1, 0.82]),
            band("hoops", "metal", 0.11, 0.012, 0.003, [[0, 0.02, 0], [0, 0.22, 0]], sides=16, stretch=[1.2, 1, 0.82]),
            lathe("fillHole", "metal", [[0.04, 0.27], [0.042, 0.29], [0.038, 0.29], [0.036, 0.275]], [-0.03, 0, 0], sides=12, caps=False, double=True),
            lathe("hole", "dark", [[0.037, 0.277], [0, 0.277]], [-0.03, 0, 0], sides=12),
            rod("spout", "metal", 0.018, sp0, sp1, 8, r1=0.011),
            lathe("roseCone", "rose", [[0.011, 0], [0.03, 0.035], [0.032, 0.04], [0, 0.042]], toward(sp1, d), sides=12),
            rod("stay", "metal", 0.005, [0.22, 0.145, 0], [0.13, 0.215, 0], 5),
            sweep("topHandle", "metal", [[0.075, 0.255, 0], [0.06, 0.33, 0], [-0.03, 0.365, 0], [-0.11, 0.34, 0], [-0.13, 0.25, 0]], r=0.0075, sides=6),
            sweep("backHandle", "metal", [[-0.13, 0.2, 0], [-0.175, 0.17, 0], [-0.175, 0.08, 0], [-0.13, 0.05, 0]], section=[0.022, 0.004], up=[0, 0, 1]),
        ], hold={"grip": [-0.05, 0.355, 0], "axis": [1, 0, 0], "face": [0, 0, 1], "carry": {"axis": [0, 0, 1], "face": [1, 0, 0]}},
        era="1700-2030", region="everywhere")


# ---- THE FLOWERPOT: a terracotta pot (its thick rolled rim, a drainage saucer under it), the soil in it, and a
# `plant` from assets/items/flowers growing out of it (empty: "")
FLOWERS = ["items/flowers/tulip", "items/flowers/daisy", "items/flowers/rose", "items/flowers/lavender", "items/flowers/poppy",
           "items/flowers/cornflower", "items/flowers/iris", "items/flowers/sunflower", ""]
POT = [[0.058, 0.012], [0.062, 0.014], [0.082, 0.14], [0.091, 0.142], [0.092, 0.168]]


def flowerpot():
    return item("Flowerpot", "tool", "a terracotta flowerpot on its saucer, its rim thickened, the soil in it, and a `plant` from assets/items/flowers growing in it (\"\": an empty pot); `ph` the plant's height param",
        {"plant": {"pick": FLOWERS}, "ph": [0.55, 0.75], "saucer": {"pick": [0, 1, 1]}},
        {"clay": {"pick": ["terracotta", "terracotta", "paint-cream", "faience-blue"]}, "soil": "crust-dark"}, [
            lathe("pot", "clay", shell(POT, 0.007, 0.022), [0, 0, 0], sides=16),
            lathe("saucer", "clay", [[0, 0], [0.085, 0], [0.095, 0.014], [0.09, 0.016], [0.08, 0.006], [0, 0.006]], sides=16, when="saucer"),
            {**surface("soil", "soil", POT, 0.007, 0.15, sides=12)},
            # (one literal `use` per flower, so a loader that fetches an item's uses before building finds them all)
            *[{"id": "plant", "use": f, "at": [0, 0.15, 0], "params": {"h": "ph"}, "when": {"plant": [f]}} for f in FLOWERS if f],
        ], hold={"grip": [0, 0.08, 0], "axis": [1, 0, 0], "face": [0, 0, 1], "carry": {"axis": [1, 0, 0], "face": [0, 0, 1]}, "follow": 0.7},
        era="any", region="everywhere")


# ---- THE SUITCASE (`style`), lying on its back: a LEATHER case (its two halves, brass corners, two straps round it,
# the locks and the handle at +z) or a modern HARD SHELL (ribbed, a zip line, a carry handle and the telescopic handle's
# housing) -- the lid the upper half, hinged along the back edge (`open`)
def suitcase():
    L, H = {"style": "leather"}, {"style": "hard"}
    W, D, h = 0.64, 0.42, 0.095
    piv = [0, h, -D / 2]
    corner = lambda y: [[sx * (W / 2 - 0.012), y, sz * (D / 2 - 0.012)] for sx in (-1, 1) for sz in (-1, 1)]
    return item("Suitcase", "tool", "a suitcase lying on its back, the handle at +z: a leather case with brass corners, two straps, locks (style leather), or a ribbed hard shell with a zip line and wheels at -x (hard) -- the lid the upper half, hinged along the back edge (`open` lifts it)",
        {"style": {"pick": ["leather", "leather", "hard"]}, "open": 0},
        {"leather": {"pick": ["leather", "leather-dark", "leather-red", "hide"]}, "strap": "leather-dark", "brass": "brass", "lining": {"pick": ["damask-red", "linen", "velvet-green"]},
         "shell": {"pick": ["plastic-grey", "paint-navy", "paint-black", "paint-red", "aluminium"]}, "trim": "plastic-black", "tyre": "rubber"}, [
            box("base", "leather", [W, h, D], [0, h / 2, 0], when=L),
            box("lining", "lining", [W - 0.02, 0.004, D - 0.02], [0, h - 0.001, 0], when=L),
            box("cornersB", "brass", [0.03, 0.05, 0.03], corner(0.03), when=L),
            box("strapsB", "strap", [0.04, h + 0.004, D + 0.008], [[-0.17, h / 2, 0], [0.17, h / 2, 0]], when=L),
            box("hasps", "brass", [0.03, 0.03, 0.006], [[-0.2, h - 0.01, D / 2 + 0.003], [0.2, h - 0.01, D / 2 + 0.003]], when=L),
            box("baseH", "shell", [W, h, D], [0, h / 2, 0], when=H),
            box("ribsB", "shell", [0.03, h - 0.02, D + 0.008], [[x, h / 2, 0] for x in (-0.18, -0.06, 0.06, 0.18)], when=H),
            box("zip", "trim", [W + 0.006, 0.012, D + 0.006], [0, h, 0], when=H),
            box("wheelBlocks", "trim", [0.03, 0.05, 0.05], [[-W / 2 - 0.012, 0.03, D / 2 - 0.04], [-W / 2 - 0.012, 0.03, -D / 2 + 0.04]], when=H),
            ring("wheels", "tyre", 0.022, 0.009, [[-W / 2 - 0.025, 0.03, D / 2 - 0.04, 0, 0, 90], [-W / 2 - 0.025, 0.03, -D / 2 + 0.04, 0, 0, 90]], sides=10, when=H),
            box("telescope", "trim", [0.03, 0.03, 0.26], [-W / 2 + 0.02, h + 0.02, 0], when=H),
            hinge("lid", piv, [
                box("lidL", "leather", [W, h, D], [0, h * 1.5, 0], when=L),
                box("liningL", "lining", [W - 0.02, 0.004, D - 0.02], [0, h + 0.001, 0], when=L),
                box("cornersL", "brass", [0.03, 0.05, 0.03], corner(2 * h - 0.03), when=L),
                box("strapsL", "strap", [0.04, h + 0.004, D + 0.008], [[-0.17, h * 1.5, 0], [0.17, h * 1.5, 0]], when=L),
                box("buckles", "brass", [0.05, 0.004, 0.035], [[-0.17, 2 * h + 0.004, 0.1], [0.17, 2 * h + 0.004, 0.1]], when=L),
                box("locks", "brass", [0.035, 0.03, 0.01], [[-0.2, h + 0.018, D / 2 + 0.004], [0.2, h + 0.018, D / 2 + 0.004]], when=L),
                box("handleBlocks", "strap", [0.03, 0.025, 0.02], [[-0.065, h + 0.04, D / 2 + 0.01], [0.065, h + 0.04, D / 2 + 0.01]], when=L),
                sweep("handle", "strap", [[-0.065, h + 0.045, D / 2 + 0.015], [-0.045, h + 0.05, D / 2 + 0.05], [0.045, h + 0.05, D / 2 + 0.05], [0.065, h + 0.045, D / 2 + 0.015]], r=0.009, sides=6, when=L),
                box("lidH", "shell", [W, h, D], [0, h * 1.5, 0], when=H),
                box("ribsL", "shell", [0.03, h - 0.02, D + 0.008], [[x, h * 1.5, 0] for x in (-0.18, -0.06, 0.06, 0.18)], when=H),
                box("ribsTop", "shell", [0.03, 0.006, D - 0.02], [[x, 2 * h + 0.002, 0] for x in (-0.18, -0.06, 0.06, 0.18)], when=H),
                sweep("handleH", "trim", [[-0.07, h + 0.045, D / 2], [-0.05, h + 0.045, D / 2 + 0.035], [0.05, h + 0.045, D / 2 + 0.035], [0.07, h + 0.045, D / 2]], section=[0.025, 0.012], sides=4, when=H),
            ], axis=(-1, 0, 0), max_=100),
        ], hold={"grip": [0, h + 0.045, D / 2 + 0.045], "axis": [1, 0, 0], "face": [0, 1, 0], "carry": {"axis": [1, 0, 0], "face": [0, 0, 1]}},
        era="1850-2030", region="everywhere")


# ---- THE COIL OF ROPE: a rope laid down in flat turns (an open lathe of its bumps), a second layer half over it, one
# loose turn on top and the end trailing off toward +x
def rope_coil():
    r0, n, t = 0.07, 6, 0.0125
    prof = [[r0, 0]]
    for k in range(n):
        c = r0 + t + 2 * t * k
        prof += [[round(c - t * 0.7, 4), round(t * 1.7, 4)], [round(c, 4), round(t * 2, 4)], [round(c + t * 0.7, 4), round(t * 1.7, 4)], [round(c + t, 4), round(t * 0.9, 4)]]
    prof += [[r0 + 2 * t * n, 0]]
    top = [[r0 + 2 * t * 2, round(t * 1.7, 4)]]
    for k in range(2, n - 1):
        c = r0 + t + 2 * t * k
        top += [[round(c - t * 0.7, 4), round(t * 3.6, 4)], [round(c, 4), round(t * 3.95, 4)], [round(c + t * 0.7, 4), round(t * 3.6, 4)], [round(c + t, 4), round(t * 2.9, 4)]]
    top += [[r0 + 2 * t * (n - 1), round(t * 1.7, 4)]]
    R = r0 + 2 * t * n
    return item("Rope coil", "tool", "a coil of rope laid down in flat turns, a second layer over the middle ones, a loose turn on top and the end trailing off toward +x",
        {}, {"rope": {"pick": ["hemp", "hemp", "straw"]}}, [
            lathe("coil", "rope", prof, sides=14, caps=False),
            lathe("layer", "rope", top, sides=14, caps=False),
            lathe("floor", "rope", [[r0, 0.001], [R, 0.001]], sides=18, caps=False, double=True),
            ring("loose", "rope", 0.12, t, [0.01, 4.2 * t, 0.0, 0, 0, 4], sides=16, stretch=[1, 1, 0.95]),
            sweep("end", "rope", [[R - t, t, 0.02], [R + 0.05, t, 0.05], [R + 0.13, t, 0.02], [R + 0.2, t, 0.06]], r=t, sides=6),
        ], hold={"grip": [0, 0.04, 0.12], "axis": [1, 0, 0], "face": [0, 1, 0], "carry": {"axis": [1, 0, 0], "face": [0, 0, 1]}},
        era="any", region="everywhere")


# ---- THE CHAIN: forged iron links, each across the last, hanging from a ring at its top -- `n` links, `link` long --
# its lower end on a hook just over the floor (its origin)
def chain():
    link = lambda id_, off, yaw: ringx(id_, "iron", "link * 0.32", "link * 0.1", [0, 0, 0, yaw, 90, 0], sides=7, stretch=[1, 1.55, 1],
                                      along={"n": f"n / 2", "from": [0, f"0.06 + link * (0.5 + {off})", 0], "to": [0, f"0.06 + link * (n - 1.5 + {off})", 0]})
    return item("Chain", "tool", "a forged iron chain hanging from the ring at its top, `n` links each across the last, `link` metres long, a hook at its lower end just over the floor (the origin)",
        {"n": {"pick": [12, 16, 20, 24]}, "link": [0.055, 0.075]},
        {"iron": {"pick": ["iron", "iron", "steel"]}}, [
            link("linksA", 0, 0), link("linksB", 1, 90),
            ringx("topRing", "iron", "link * 0.6", "link * 0.13", [0, "0.06 + link * (n - 0.2)", 0, 0, 90, 0], sides=10),
            sweep("hook", "iron", [[0, "0.06 + link * 0.2", 0], [0, 0.045, 0], [0.01, 0.012, 0], [0.04, 0.012, 0], [0.05, 0.04, 0]], radii=[0.008, 0.009, 0.009, 0.007, 0.004], sides=6),
        ], hold={"grip": [0, "0.06 + link * (n - 0.2)", 0], "axis": [1, 0, 0], "face": [0, 0, 1], "carry": {"axis": [1, 0, 0], "face": [0, 0, 1]}},
        era="any", region="everywhere")


# ==== THE FARM =====================================================================================================
# ---- THE PLOUGH (`style`): the ARD (a scratch plough: the beam curving down from the yoke to the sole, the sole on the
# ground with its iron share at the point, the stilt rising behind it into a handle) or the MOULDBOARD plough (a straight
# beam on a gallows wheel at the front, the coulter knife down from it, the share, the curved mouldboard turning the sod
# to +z, the landside, two handles). The team at +x, the ploughman at -x
def plough():
    A, M = {"style": "ard"}, {"style": "mouldboard"}
    # the mouldboard: four strips standing along a curve in plan from the share's heel back and out to +z, each leaned
    # further out than the last -- a twisted board, as the sod is turned over
    curve, leans = [(0.16, 0.045), (0.03, 0.09), (-0.11, 0.165), (-0.24, 0.265), (-0.36, 0.38)], [8, 24, 40, 56]
    mould = []
    for i in range(4):
        (fx, fz), (bx, bz) = curve[i], curve[i + 1]
        L = math.hypot(fx - bx, fz - bz) + 0.012
        mould.append(plate(f"mould{i}", "iron", [[-L / 2, 0], [L / 2, 0], [L / 2, 0.25 - 0.02 * i], [-L / 2, 0.25 - 0.02 * i]], 0.01,
                           orient([(fx + bx) / 2, 0.012, (fz + bz) / 2], ("x", leans[i]), ("y", math.degrees(math.atan2(-(fz - bz), fx - bx)))), when=M))
    return item("Plough", "tool", "a plough, the team at +x and the ploughman at -x: an ard, its beam curving down from the yoke to the sole with an iron share at the point, the stilt rising into a handle (style ard), or a mouldboard plough on a gallows wheel, the coulter, the share and the curved mouldboard turning the sod to +z, the landside, two handles (mouldboard)",
        {"style": {"pick": ["ard", "mouldboard", "mouldboard"]}},
        {"wood": {"pick": ["oak", "ash", "oak-grey"]}, "iron": "iron", "steel": "steel"}, [
            # the ard
            sweep("beamA", "wood", [[-0.25, 0.08, 0], [0.0, 0.35, 0], [0.6, 0.62, 0], [1.4, 0.78, 0], [2.1, 0.82, 0]], radii=[0.045, 0.045, 0.04, 0.035, 0.032], sides=7, when=A),
            beam("sole", "wood", [-0.5, 0.06, 0], [0.25, 0.03, 0], 0.09, 0.08, when=A),
            plate("share", "iron", [[0.0, -0.035], [0.2, 0.0], [0.0, 0.035]], 0.02, flat_at([0.22, 0.03, 0], -8), when=A),
            sweep("stilt", "wood", [[-0.42, 0.06, 0], [-0.55, 0.4, 0], [-0.75, 0.82, 0], [-0.8, 0.95, 0]], r=0.03, sides=6, when=A),
            rod("handleA", "wood", 0.02, [-0.8, 0.94, -0.12], [-0.8, 0.94, 0.12], 6, when=A),
            rod("wedges", "wood", 0.015, [-0.2, 0.0, 0], [-0.2, 0.28, 0], 5, when=A),
            rod("yokePin", "wood", 0.015, [2.0, 0.72, 0], [2.0, 0.92, 0], 5, when=A),
            # the mouldboard plough
            box("beamM", "wood", [2.1, 0.11, 0.09], [0.55, 0.62, 0], when=M),
            box("gallows", "wood", [0.06, 0.45, 0.06], [[1.42, 0.42, 0.12], [1.42, 0.42, -0.12]], when=M),
            box("gallowsTop", "wood", [0.08, 0.06, 0.32], [1.42, 0.66, 0], when=M),
            {"id": "gallowsWheel", "use": "items/components/cart-wheel", "at": [1.42, 0.2, 0], "params": {"r": 0.2, "n": 8}, "when": M},
            sweep("clevis", "iron", [[1.6, 0.62, 0], [1.68, 0.62, 0], [1.72, 0.58, 0]], r=0.012, sides=5, when=M),
            ring("hitch", "iron", 0.035, 0.008, [1.75, 0.58, 0, 0, 0, 90], sides=10, when=M),
            plate("coulter", "steel", [[-0.03, 0.0], [0.03, 0.0], [0.04, 0.62], [-0.02, 0.62]], 0.012, orient([0.42, 0.05, 0], ("z", -20)), when=M),
            box("frog", "iron", [0.4, 0.2, 0.06], [0.05, 0.12, 0], when=M),
            box("standard", "wood", [0.08, 0.45, 0.07], [0.0, 0.38, 0], when=M),
            plate("shareM", "steel", [[-0.05, -0.12], [0.33, 0.0], [0.05, 0.08], [-0.05, 0.08]], 0.012, flat_at([0.12, 0.012, 0.05], 0, 0), when=M),
            plate("landside", "iron", [[-0.35, 0.0], [0.25, 0.0], [0.25, 0.12], [-0.35, 0.1]], 0.012, [0.0, 0.0, -0.035], when=M),
            *mould,
            rod("mouldStay", "iron", 0.008, [-0.3, 0.2, 0.3], [-0.35, 0.4, 0.06], 5, when=M),
            beam("handleL", "wood", [-0.12, 0.3, -0.04], [-1.15, 0.92, -0.28], 0.045, 0.045, when=M),
            beam("handleR", "wood", [-0.12, 0.3, 0.04], [-1.15, 0.92, 0.28], 0.045, 0.045, when=M),
            rod("rungM", "wood", 0.015, [-0.9, 0.7, -0.22], [-0.9, 0.7, 0.22], 6, when=M),
            rod("gripsM", "wood", 0.02, [-1.15, 0.92, 0], [-1.25, 0.95, 0], 6, at=[[0, 0, -0.28], [0, 0, 0.28]], when=M),
        ], era="-3000-1950", region="everywhere")


# ---- THE PLUNGE BUTTER CHURN: a tall coopered churn, tapering to its top (its staves, three iron or willow hoops),
# a lid round the dasher's staff, the staff rising through it with its knob; a drip of cream on the lid
def butter_churn():
    return item("Butter churn", "tool", "a plunge butter churn: a tall coopered churn tapering to its top, three hoops, the lid with a collar round the dasher's staff, the staff rising through it to its knob",
        {"h": [0.62, 0.75]},
        {"wood": {"pick": ["oak", "pine", "ash"]}, "lid": {"pick": ["oak", "ash"]}, "hoop": {"pick": ["iron", "iron", "cane"]}, "staff": {"pick": ["ash", "birch"]}, "cream": "paint-cream"}, [
            lathe("staves", "wood", [[0, 0.015], [0.165, 0.015], [0.172, 0.03], ["0.13", "h"], ["0.118", "h"], [0.155, 0.04], [0, 0.04]], sides=14, faceted=True),
            lathe("chime", "wood", [[0.16, 0], [0.166, 0], [0.168, 0.02], [0, 0.02]], sides=14),
            band("hoops", "hoop", 0.168, 0.03, 0.005, [[0, 0.06, 0], [0, "h * 0.5", 0]], sides=14, stretch=[1, 1, 1]),
            band("hoopTop", "hoop", 0.133, 0.03, 0.005, [0, "h - 0.04", 0], sides=14),
            lathe("lidT", "lid", [[0.13, "h - 0.03"], [0.136, "h - 0.025"], [0.136, "h + 0.004"], [0.04, "h + 0.012"], [0.025, "h + 0.04"], [0.018, "h + 0.042"], [0, "h + 0.042"]], sides=14),
            lathe("cream", "cream", [[0.05, "h + 0.012"], [0.05, "h + 0.014"], [0, "h + 0.014"]], [0.06, 0, 0.03], sides=8),
            rod("staff", "staff", 0.016, [0, "h - 0.1", 0], [0, "h + 0.5", 0], 7),
            sphere("knob", "staff", 0.024, [0, "h + 0.5", 0], sides=7),
        ], hold={"grip": [0, "h + 0.4", 0], "axis": [0, 1, 0], "face": [1, 0, 0], "carry": {"axis": [0, 1, 0], "face": [1, 0, 0]}},
        era="1400-1950", region="Europe")


# ---- THE ROTARY QUERN: two round stones, the lower (bed) stone on a board, the upper (runner) turning on it -- its eye
# where the grain is fed, the wooden peg handle upright near its edge, the rynd's iron across the eye; meal spilt in a
# ring round it on the board
def quern():
    return item("Quern", "tool", "a rotary hand quern: the bed stone on its board, the runner stone over it with the eye where the grain is fed and the iron rynd across it, an upright wooden peg handle near its edge, the meal spilt round the stones",
        {}, {"stone": {"pick": ["stone", "granite-black", "granite-red"]}, "wood": {"pick": ["oak", "planks"]}, "iron": "iron", "meal": "bone", "grain": "maize", "dark": "mouth-dark"}, [
            box("board", "wood", [0.62, 0.03, 0.62], [0, 0.015, 0]),
            lathe("meal", "meal", [[0.2, 0.03], [0.23, 0.036], [0.27, 0.031], [0.28, 0.03]], sides=16, caps=False),
            lathe("bed", "stone", [[0, 0.03], [0.2, 0.03], [0.205, 0.095], [0.17, 0.11], [0, 0.118]], sides=16, faceted=True),
            lathe("runner", "stone", [[0.028, 0.118], [0.2, 0.112], [0.205, 0.17], [0.19, 0.19], [0.05, 0.198], [0.04, 0.2], [0.03, 0.17], [0.028, 0.118]], sides=16, caps=False),
            lathe("eye", "dark", [[0.029, 0.15], [0, 0.15]], sides=10),
            lathe("grain", "grain", [[0.03, 0.17], [0.012, 0.178], [0, 0.18]], sides=10),
            box("rynd", "iron", [0.058, 0.01, 0.012], [0, 0.155, 0]),
            rod("handle", "wood", 0.016, [0.16, 0.19, 0], [0.165, 0.38, 0], 7, r1=0.014),
            rod("spindle", "iron", 0.006, [0, 0.03, 0], [0, 0.16, 0], 5),
        ], era="-800-1900", region="everywhere")


# ==== BATH AND MEDICINE ============================================================================================
# ---- THE WASHSTAND: a 19th-century wooden stand -- a top of marble or wood on four legs, a splashback, a lower shelf,
# a towel rail at each end with a towel on one -- and on it the wash BASIN with the EWER standing in it, a soap dish
EWER = [[0.06, 0], [0.065, 0.008], [0.06, 0.02], [0.075, 0.08], [0.08, 0.14], [0.07, 0.2], [0.055, 0.24], [0.052, 0.27], [0.06, 0.3]]


def washstand():
    H = 0.78
    basin = [[0.09, 0], [0.12, 0.02], [0.17, 0.065], [0.2, 0.1], [0.215, 0.11]]
    return item("Washstand", "furniture", "a 19th-century washstand: a marble or wooden top on four legs, a splashback, a lower shelf, a towel rail at each end with a towel on one; on it the wash basin with the ewer standing in it, and a soap dish -- its front +z",
        {"water": {"pick": [0, 1]}},
        {"wood": {"pick": ["mahogany", "walnut", "oak", "pine"]}, "top": {"pick": ["marble", "marble", "marble-grey", "mahogany"]}, "ware": {"pick": ["faience-white", "paint-white", "faience-blue"]},
         "band": {"pick": ["enamel-blue", "faience-green", "gilt"]}, "towel": {"pick": ["linen", "canvas"]}, "water": "glass-light", "soap": "paint-cream"}, [
            {"id": "legs", "use": "items/components/turned-leg", "at": [[x, 0, z] for x in (-0.4, 0.4) for z in (-0.2, 0.2)], "params": {"h": H - 0.03, "r": 0.022, "style": "baluster", "block": 0.12}},
            box("apron", "wood", [0.82, 0.08, 0.42], [0, H - 0.07, 0]),
            box("top", "top", [0.9, 0.03, 0.5], [0, H - 0.015, 0]),
            plate("splashback", "top", [[-0.45, 0], [0.45, 0], [0.45, 0.16], [0.3, 0.2], [0.1, 0.22], [-0.1, 0.22], [-0.3, 0.2], [-0.45, 0.16]], 0.02, [0, H, -0.24]),
            box("shelf", "wood", [0.82, 0.02, 0.42], [0, 0.18, 0]),
            rod("rails", "wood", 0.012, [0, 0, -0.18], [0, 0, 0.18], 6, at=[[-0.49, H - 0.08, 0], [0.49, H - 0.08, 0]]),
            box("railBrackets", "wood", [0.08, 0.03, 0.02], [[sx * 0.46, H - 0.08, sz * 0.18] for sx in (-1, 1) for sz in (-1, 1)]),
            box("towel", "towel", [0.008, 0.45, 0.28], [0.497, H - 0.29, 0]),
            box("towelFold", "towel", [0.03, 0.012, 0.28], [0.49, H - 0.072, 0]),
            # the basin, its band, the water, the ewer in it, a soap dish
            lathe("basin", "ware", shell(basin, 0.006, 0.008), [0, H, 0.02], sides=22),
            lathe("basinBand", "band", [[0.2065, H + 0.096], [0.2125, H + 0.106]], sides=22, caps=False, at=[0, 0, 0.02]),
            {**surface("water", "water", basin, 0.006, 0.05, sides=16, at=[0, H, 0.02]), "when": "water"},
            lathe("ewer", "ware", EWER + [[0.055, 0.3], [0, 0.3]], [0, H + 0.008, 0.02], sides=14),
            lathe("ewerBand", "band", [[0.0802, H + 0.008 + 0.12], [0.0802, H + 0.008 + 0.15]], [0, 0, 0.02], sides=14, caps=False),
            plate("lip", "ware", [[0.0, 0.0], [0.06, 0.03], [0.0, 0.04]], 0.04, [0.04, H + 0.008 + 0.27, 0.02]),
            sweep("ewerHandle", "ware", [[-0.05, H + 0.27, 0.02], [-0.1, H + 0.26, 0.02], [-0.11, H + 0.17, 0.02], [-0.075, H + 0.1, 0.02]], r=0.009, sides=6),
            lathe("soapDish", "ware", [[0, H], [0.05, H], [0.055, H + 0.015], [0.048, H + 0.015], [0.044, H + 0.006], [0, H + 0.006]], [0.33, 0, 0.08], sides=12, stretch=[1.3, 1, 1]),
            box("soapBar", "soap", [0.07, 0.02, 0.045], [0.33, H + 0.016, 0.08]),
        ], era="1780-1930", region="Europe")


# ---- THE BATHTUB (`style`), its length along x, front +z: a CLAWFOOT roll-top (cast iron, painted outside and
# enamelled within, double-ended, on four claw-and-ball feet, the taps at +x) or a modern BUILT-IN one (an acrylic basin
# in its panelled apron and deck, a mixer tap at -x); `water` filled
CLAW = [[0.24, 0.17], [0.31, 0.2], [0.35, 0.28], [0.37, 0.45], [0.383, 0.6], [0.395, 0.635], [0.4, 0.655], [0.392, 0.672], [0.376, 0.672]]
CLAWIN = [[0.376, 0.672], [0.36, 0.6], [0.345, 0.45], [0.32, 0.3], [0.28, 0.215], [0.2, 0.195], [0, 0.195]]


def bathtub():
    C, B = {"style": "clawfoot"}, {"style": "built-in"}
    k = 2.12   # (the clawfoot's plan: its round lathe drawn out along x)
    feet = [[sx * 0.52, 0, sz * 0.2] for sx in (-1, 1) for sz in (-1, 1)]
    # the built-in basin: a loft along x, open at its top, seen from within
    st = [[-0.76, 0.24, 0.12, 0.54, 0.32], [-0.64, 0.27, 0.07, 0.54, 0.335], [0.55, 0.27, 0.07, 0.54, 0.335], [0.72, 0.22, 0.14, 0.54, 0.32]]
    return item("Bathtub", "furniture", "a bathtub, its length along x and its front +z: a cast-iron double-ended roll-top on four claw-and-ball feet, painted outside and enamelled within, the taps at +x (style clawfoot), or a modern built-in acrylic tub in its panelled apron and deck, a mixer tap at -x (built-in); filled with `water`",
        {"style": {"pick": ["clawfoot", "clawfoot", "built-in"]}, "water": {"pick": [0, 0, 1]}},
        {"outside": {"pick": ["paint-white", "paint-black", "paint-navy", "paint-maroon", "paint-cream", "copper-bright"]}, "enamel": "paint-white", "foot": {"pick": ["brass", "chrome", "iron", "gilt"]},
         "chrome": "chrome", "panel": "plastic-white", "water": "glass-light", "dark": "mouth-dark"}, [
            lathe("outer", "outside", [[0, 0.17]] + CLAW, sides=20, stretch=[k, 1, 1], caps=False, when=C),
            lathe("inner", "enamel", CLAWIN, sides=20, stretch=[k, 1, 1], when=C),
            lathe("waterC", "water", [[0.35, 0.47], [0, 0.47]], sides=20, stretch=[k, 1, 1], when={"style": "clawfoot", "water": 1}),
            sweep("legs", "foot", [[0, 0.2, 0], [0.03, 0.12, 0], [0.06, 0.05, 0], [0.07, 0.03, 0]], radii=[0.035, 0.03, 0.022, 0.02], sides=7, at=[[x, 0, z, 0 if x > 0 else 180, 0, 0] for x, _, z in feet], when=C),
            sphere("balls", "foot", 0.03, [[x + (0.075 if x > 0 else -0.075), 0.03, z] for x, _, z in feet], sides=7, when=C),
            lathe("plug", "dark", [[0.022, 0.197], [0, 0.197]], [-0.45, 0, 0], sides=8, when=C),
            rod("tapPosts", "chrome", 0.012, [0.79, 0.66, -0.06], [0.79, 0.76, -0.06], 8, at=[[0, 0, 0], [0, 0, 0.12]], when=C),
            sweep("spout", "chrome", [[0.79, 0.76, 0.0], [0.79, 0.81, 0.0], [0.75, 0.82, 0.0], [0.72, 0.77, 0.0]], r=0.011, sides=7, when=C),
            rod("tapBar", "chrome", 0.01, [0.79, 0.76, -0.06], [0.79, 0.76, 0.06], 6, when=C),
            box("tapHeads", "chrome", [0.05, 0.012, 0.012], [[0.79, 0.775, -0.06], [0.79, 0.775, 0.06]], when=C),
            # the built-in
            loft("basin", "panel", st, round_=0.16, bare=["top"], double=True, when=B),
            box("apron", "panel", [1.7, 0.53, 0.02], [0, 0.265, 0.365], when=B),
            box("ends", "panel", [0.02, 0.53, 0.74], [[-0.84, 0.265, 0], [0.84, 0.265, 0]], when=B),
            box("deckFront", "panel", [1.7, 0.03, 0.11], [0, 0.545, 0.32], when=B),
            box("deckBack", "panel", [1.7, 0.03, 0.11], [0, 0.545, -0.32], when=B),
            box("deckEnds", "panel", [0.15, 0.03, 0.75], [[-0.775, 0.545, 0], [0.775, 0.545, 0]], when=B),
            box("plinth", "dark", [1.66, 0.06, 0.02], [0, 0.03, 0.355], when=B),
            box("waterBox", "water", [1.36, 0.004, 0.62], [-0.03, 0.42, 0], when={"style": "built-in", "water": 1}),
            rod("mixer", "chrome", 0.014, [-0.78, 0.56, 0], [-0.78, 0.64, 0], 8, when=B),
            sweep("mixerSpout", "chrome", [[-0.78, 0.64, 0], [-0.76, 0.66, 0], [-0.7, 0.66, 0]], r=0.011, sides=7, when=B),
            box("lever", "chrome", [0.05, 0.01, 0.015], [-0.8, 0.672, 0], when=B),
            lathe("drain", "chrome", [[0.025, 0.073], [0, 0.073]], [-0.55, 0, 0], sides=8, when=B),
        ], era="1850-2030", region="everywhere")


# ---- THE TOILET (modern): a close-coupled pedestal pan -- its foot, the bowl with the water in its trap, the seat and
# the LID on a hinge at the back (`open` lifts it), the cistern on the back with its lid and flush button -- its back at
# -z against the wall
def toilet():
    k = 1.32
    pan = [[0.115, 0], [0.122, 0.01], [0.105, 0.05], [0.1, 0.17], [0.125, 0.28], [0.162, 0.355], [0.18, 0.392], [0.18, 0.4],
           [0.15, 0.4], [0.14, 0.37], [0.1, 0.3], [0.06, 0.245], [0, 0.235]]
    # (the lid over the seat ring: its outline in the plate's own frame, whose y runs toward -z)
    lidO = [[x * 0.178, -0.045 + z * 0.244] for x, z in [(math.sin(math.radians(a)), math.cos(math.radians(a))) for a in range(0, 360, 20)]]
    return item("Toilet", "furniture", "a close-coupled toilet, its back at -z against the wall: the pedestal pan, the water in its trap, the seat, the lid hinged at the back (`open` lifts it), the cistern with its lid and the flush button",
        {"open": 0},
        {"ware": {"pick": ["paint-white", "paint-white", "faience-white"]}, "seat": {"pick": ["plastic-white", "plastic-white", "oak", "paint-black"]}, "chrome": "chrome", "water": "glass-light"}, [
            lathe("pan", "ware", pan, [0, 0, 0.04], sides=20, stretch=[1, 1, k]),
            lathe("water", "water", [[0.075, 0.27], [0, 0.27]], [0, 0, 0.0], sides=12, stretch=[1, 1, 1.2]),
            box("neck", "ware", [0.22, 0.12, 0.14], [0, 0.34, -0.19]),
            box("cistern", "ware", [0.38, 0.36, 0.16], [0, 0.58, -0.27], round=0.02),
            box("cisternLid", "ware", [0.4, 0.025, 0.18], [0, 0.772, -0.27]),
            lathe("button", "chrome", [[0.02, 0.784], [0.02, 0.79], [0, 0.79]], [0, 0, -0.27], sides=10),
            ring("seatRing", "seat", 0.152, 0.024, [0, 0.413, 0.045], sides=20, stretch=[1, 0.42, 1.38]),
            box("hingeBlocks", "chrome", [0.03, 0.02, 0.035], [[-0.08, 0.413, -0.175], [0.08, 0.413, -0.175]]),
            hinge("lid", [0, 0.432, -0.175], [
                plate("lidBoard", "seat", lidO, 0.018, flat_at([0, 0.432, 0.0])),
            ], axis=(-1, 0, 0), max_=88),   # (up against the cistern, 1.5 cm behind the hinge: no further)
        ], markers=[{"role": "seat", "at": [0, 0, 0], "data": {"w": 0.36, "d": 0.4, "top": 0.43}}], era="1880-2030", region="everywhere")


# ---- THE WHEELCHAIR (modern): a folding wheelchair, its front +z -- the tubular side frames, the X brace under the
# sling seat, the sling back, the armrests, the push handles, the two big rear wheels with their spokes and push rims,
# the swivelling front castors, the footplates
def wheelchair():
    R, wx, wz, wy = 0.3, 0.3, -0.12, 0.3
    wheel = []
    for sx in (-1, 1):
        x = sx * wx
        wheel += [   # (the wire-spoked wheel is the bicycle's component, its axle turned across; the push rim outboard of it)
            {"id": f"wheel{sx}", "use": "items/modern/components/spoked-wheel", "at": [x, wy, wz, 90, 0, 0],
             "params": {"r": R, "t": 0.014, "n": 24, "sr": 0.0018, "hubW": 0.03, "hubR": 0.028}, "materials": {"rim": "frame", "hub": "frame"}},
            ringx(f"push{sx}", "frame", R - 0.035, 0.007, [x + sx * 0.035, wy, wz, 0, 0, 90], sides=16),
        ]
    caster = lambda x: [ring(f"caster{x}", "tyre", 0.07, 0.016, [x, 0.08, 0.3, 0, 0, 90], sides=12),
                        lathe(f"casterHub{x}", "frame", [[0.03, -0.012], [0.03, 0.012]], [x, 0.08, 0.3, 0, 0, 90], sides=8),
                        rod(f"fork{x}", "frame", 0.006, [x, 0.08, 0.3], [x, 0.2, 0.27], 5, at=[[-0.02, 0, 0], [0.02, 0, 0]]),
                        rod(f"swivel{x}", "frame", 0.014, [x, 0.2, 0.27], [x, 0.27, 0.27], 7)]
    side = lambda sx: sweep(f"side{sx}", "frame", [[sx * 0.24, 0.95, -0.24], [sx * 0.24, 0.5, -0.2], [sx * 0.24, 0.5, 0.25], [sx * 0.24, 0.27, 0.27], [sx * 0.22, 0.12, 0.38]],
                            r=0.012, sides=6)
    return item("Wheelchair", "furniture", "a folding wheelchair, its front +z: tubular side frames, an X brace under the sling seat, the sling back, armrests, push handles, two big rear wheels with spokes and push rims, swivelling front castors, footplates",
        {}, {"frame": {"pick": ["chrome", "aluminium", "paint-black"]}, "sling": {"pick": ["upholstery", "paint-black", "upholstery-grey", "leather-dark"]}, "tyre": "rubber",
             "spoke": "steel", "grip": "rubber", "arm": "plastic-black"}, [
            *wheel, *caster(-0.22), *caster(0.22), side(-1), side(1),
            rod("axleTube", "frame", 0.012, [-0.24, wy, wz], [0.24, wy, wz], 6),
            rod("crossA", "frame", 0.011, [-0.22, 0.5, 0.0], [0.22, 0.2, 0.0], 6),
            rod("crossB", "frame", 0.011, [0.22, 0.5, 0.0], [-0.22, 0.2, 0.0], 6),
            rod("seatRails", "frame", 0.012, [0, 0.5, -0.2], [0, 0.5, 0.25], 6, at=[[-0.22, 0, 0], [0.22, 0, 0]]),
            box("seat", "sling", [0.44, 0.02, 0.42], [0, 0.505, 0.03]),
            box("back", "sling", [0.46, 0.36, 0.015], [0, 0.73, -0.225, 0, -5, 0]),
            box("armPads", "arm", [0.05, 0.035, 0.3], [[-0.24, 0.74, 0.02], [0.24, 0.74, 0.02]]),
            rod("armPosts", "frame", 0.01, [0, 0.5, 0], [0, 0.72, 0], 6, at=[[sx * 0.24, 0, z] for sx in (-1, 1) for z in (-0.1, 0.14)]),
            rod("grips", "grip", 0.016, [0, 0.95, -0.24], [0, 0.95, -0.36], 8, at=[[-0.24, 0, 0], [0.24, 0, 0]]),
            box("footplates", "arm", [0.16, 0.012, 0.11], [[-0.13, 0.11, 0.42], [0.13, 0.11, 0.42]]),
        ], markers=[{"role": "seat", "at": [0, 0, 0], "data": {"w": 0.44, "d": 0.42, "top": 0.52}}], era="1930-2030", region="everywhere")


# ---- THE CRUTCH (`style`): an UNDERARM crutch (two bowed wooden rails from the padded armrest down to the single
# foot, the hand grip between them, a rubber tip) or a FOREARM crutch (an aluminium tube, the moulded hand grip out to
# +z, the cuff round the forearm above it)
def crutch():
    U, F = {"style": "underarm"}, {"style": "forearm"}
    return item("Crutch", "tool", "a crutch: an underarm one, two bowed wooden rails from the padded armrest down to the single foot, a hand grip between them, a rubber tip (style underarm), or an aluminium forearm crutch with a moulded grip out to +z and an open cuff round the forearm (forearm)",
        {"style": {"pick": ["underarm", "underarm", "forearm"]}},
        {"wood": {"pick": ["ash", "birch", "oak"]}, "pad": {"pick": ["leather", "rubber", "leather-dark"]}, "tip": "rubber", "alu": {"pick": ["aluminium", "paint-blue", "paint-grey"]},
         "grip": "plastic-black", "bolt": "steel"}, [
            sweep("rails", "wood", [[-0.02, 0.6, 0], [-0.07, 0.9, 0], [-0.09, 1.1, 0], [-0.08, 1.3, 0]], r=0.011, sides=6, mirror="x", when=U),
            rod("leg", "wood", 0.016, [0, 0.03, 0], [0, 0.66, 0], 7, when=U),
            box("ferrule", "wood", [0.05, 0.08, 0.032], [0, 0.62, 0], when=U),
            rod("handGrip", "wood", 0.015, [-0.085, 0.9, 0], [0.085, 0.9, 0], 7, when=U),
            sweep("armrest", "pad", [[-0.11, 1.305, 0], [-0.05, 1.33, 0], [0.05, 1.33, 0], [0.11, 1.305, 0]], section=[0.05, 0.03], up=[0, 0, 1], when=U),
            rod("bolts", "bolt", 0.004, [0, 0, -0.02], [0, 0, 0.02], 5, at=[[0, 0.7, 0], [0, 0.6, 0]], when=U),
            lathe("tipU", "tip", [[0, 0], [0.02, 0], [0.022, 0.01], [0.018, 0.045], [0, 0.045]], sides=8, when=U),
            rod("tube", "alu", 0.011, [0, 0.04, 0], [0, 0.82, 0], 7, when=F),
            rod("upper", "alu", 0.011, [0, 0.8, 0], [0, 1.02, -0.06], 7, when=F),
            box("gripF", "grip", [0.035, 0.04, 0.13], [0, 0.81, 0.06], when=F),
            sweep("cuff", "grip", [[0.05, 1.04, -0.02], [0.045, 1.04, -0.08], [0, 1.04, -0.1], [-0.045, 1.04, -0.08], [-0.05, 1.04, -0.02]], section=[0.04, 0.005], up=[0, 1, 0], when=F),
            rod("holes", "bolt", 0.0035, [-0.012, 0, 0], [0.012, 0, 0], 5, at=[[0, 0.3 + 0.03 * i, 0] for i in range(5)], when=F),
            lathe("tipF", "tip", [[0, 0], [0.02, 0], [0.022, 0.01], [0.016, 0.05], [0, 0.05]], sides=8, when=F),
        ], hold={"grip": [0, 0.9, 0], "axis": [1, 0, 0], "face": [0, 0, 1], "carry": {"axis": [1, 0, 0], "face": [0, 0, 1]}, "rest": "ground"},
        era="1500-2030", region="everywhere")


# ==== SCHOOL =======================================================================================================
# ---- THE GLOBE on its stand: a turned base and stem, the brass meridian ring holding the ball by its poles, the axis
# tilted 23.5 degrees, the seas and the continents (spherical caps in two or three colours) on it
LANDS = [(52, -100, 21, 0), (35, -93, 15, 0), (62, -125, 14, 0), (64, -152, 8, 0), (72, -40, 10, 2), (18, -97, 7, 0), (9, -82, 4, 0),
         (-5, -60, 17, 1), (-22, -58, 12, 1), (-40, -68, 7, 1), (50, 12, 10, 2), (60, 28, 10, 2), (54, -3, 3, 2), (8, 20, 19, 1), (-14, 26, 13, 1),
         (24, 15, 16, 1), (-28, 25, 8, 1), (55, 90, 24, 0), (42, 102, 17, 0), (30, 78, 11, 0), (19, 78, 8, 2), (66, 132, 15, 0), (24, 46, 10, 2),
         (14, 103, 6, 2), (37, 138, 3, 2), (-25, 134, 13, 1), (-85, 0, 13, 2), (-2, 115, 4, 0), (-19, 47, 3, 2)]


def globe():
    R, cy, tilt = 0.15, 0.32, 23.5
    T = _rot("z", tilt)
    caps = []
    for i, (lat, lon, a, c) in enumerate(LANDS):
        la, lo = math.radians(lat), math.radians(lon)
        d = [math.cos(la) * math.cos(lo), math.sin(la), -math.cos(la) * math.sin(lo)]
        d = [sum(T[r][k] * d[k] for k in range(3)) for r in range(3)]
        caps.append(toward([0, cy, 0], d))
    ax = [sum(T[r][k] * v for k, v in enumerate([0, 1, 0])) for r in range(3)]
    pole = lambda s: [round(ax[0] * s * (R + 0.012), 4), round(cy + ax[1] * s * (R + 0.012), 4), 0]
    return item("Globe", "tool", "a schoolroom globe on its stand: a turned base and stem, the brass meridian ring holding the ball by its poles, the axis tilted 23.5 degrees, the seas and the continents in two or three colours",
        {}, {"wood": {"pick": ["walnut", "mahogany", "ebony", "oak"]}, "brass": "brass", "sea": {"pick": ["faience-blue", "paint-cream", "enamel-blue"]},
             "land0": {"pick": ["faience-yellow", "paint-cream", "leaf-light"]}, "land1": {"pick": ["faience-green", "apple-green", "faience-red"]}, "land2": {"pick": ["paint-orange", "faience-yellow", "apple-red"]}}, [
            lathe("base", "wood", [[0, 0], [0.11, 0], [0.11, 0.015], [0.09, 0.03], [0.04, 0.045], [0.025, 0.06], [0, 0.06]], sides=14),
            lathe("stem", "wood", [[0.018, 0.06], [0.014, 0.1], [0.022, 0.12], [0.014, 0.14], [0.012, 0.155], [0, 0.155]], sides=10),
            sphere("ball", "sea", R, [0, cy, 0], sides=18),
            *[cap(f"land{i}", f"land{L[3]}", R + 0.003, L[2], caps[i], sides=6 if L[2] < 10 else 8, rings=1) for i, L in enumerate(LANDS)],
            ring("meridian", "brass", R + 0.014, 0.005, [0, cy, 0, 0, 90, -tilt], sides=24),
            sweep("arm", "brass", [[0, 0.155, 0], [0, cy - R - 0.012, 0]], r=0.007, sides=6),
            rod("pins", "brass", 0.004, pole(-1), pole(1), 5),
        ], era="1500-2030", region="everywhere")


# ==== MUSIC AND PLAY ===============================================================================================
# ---- THE DRUM (`style`), its heads up: a medieval TABOR (a deep wooden shell, two skin heads on their hoops, the cord
# laced in Vs between them, the snare across the top head, the stick) or a modern SNARE drum (a lacquered or chrome
# shell, the batter head, chrome hoops, the lugs and tension rods, the strainer, two sticks on it)
def drum():
    Tb, S = {"style": "tabor"}, {"style": "snare"}
    r, h = 0.15, 0.2
    a = math.radians(22.5)
    return item("Drum", "tool", "a drum, its heads up: a medieval tabor, a deep wooden shell with two skin heads on their hoops, the cord laced in Vs between them, the snare across the top and its stick (style tabor), or a modern snare drum, its shell lacquered or chrome, chrome hoops, the lugs and tension rods, the strainer, two sticks on it (snare)",
        {"style": {"pick": ["tabor", "snare"]}},
        {"wood": {"pick": ["oak", "ash", "walnut"]}, "skin": "paint-cream", "cord": {"pick": ["hemp", "cord-red"]}, "gut": "gut", "stick": {"pick": ["ash", "birch"]},
         "shell": {"pick": ["chrome", "paint-red", "paint-navy", "lacquer-black", "walnut"]}, "chrome": "chrome", "head": {"pick": ["plastic-white", "paint-cream"]}}, [
            lathe("shellT", "wood", [[r, 0.012], [r, h - 0.012]], sides=16, caps=False, double=True, when=Tb),
            lathe("skins", "skin", [[r + 0.002, 0], [0, 0]], [[0, 0.012, 0], [0, h - 0.012, 0, 0, 180, 0]], sides=16, when=Tb),
            band("hoopsT", "wood", r, 0.022, 0.007, [[0, 0.011, 0], [0, h - 0.011, 0]], sides=16, when=Tb),
            rod("laceA", "cord", 0.002, [r + 0.007, h - 0.02, 0], [round((r + 0.007) * math.cos(a), 4), 0.02, round(-(r + 0.007) * math.sin(a), 4)], 3, around={"n": 8, "r": 0}, when=Tb),
            rod("laceB", "cord", 0.002, [r + 0.007, h - 0.02, 0], [round((r + 0.007) * math.cos(a), 4), 0.02, round((r + 0.007) * math.sin(a), 4)], 3, around={"n": 8, "r": 0}, when=Tb),
            rod("snareT", "gut", 0.0012, [-r, h + 0.0015, 0.01], [r, h + 0.0015, 0.01], 3, when=Tb),
            rod("stickT", "stick", 0.008, [-0.03, h + 0.01, 0.1], [0.3, h + 0.01, 0.17], 6, r1=0.006, when=Tb),
            sweep("strapT", "cord", [[-r - 0.008, h - 0.03, 0], [-0.1, h + 0.28, 0.1], [0.1, h + 0.28, 0.1], [r + 0.008, h - 0.03, 0]], section=[0.025, 0.003], when=Tb),
            # the snare
            lathe("shellS", "shell", [[0.178, 0.01], [0.178, 0.13]], sides=20, caps=False, double=True, when=S),
            lathe("headS", "head", [[0.179, 0.135], [0, 0.135]], sides=20, when=S),
            lathe("bottomS", "head", [[0.179, 0.005], [0, 0.005]], [0, 0, 0, 0, 180, 0], sides=20, when=S),
            band("hoopsS", "chrome", 0.18, 0.018, 0.005, [[0, 0.007, 0], [0, 0.133, 0]], sides=20, when=S),
            box("lugs", "chrome", [0.018, 0.05, 0.016], [0.188, 0.07, 0], around={"n": 8, "r": 0}, when=S),
            rod("rods", "chrome", 0.0025, [0.19, 0.0, 0], [0.19, 0.14, 0], 4, around={"n": 8, "r": 0, "start": 22.5}, when=S),
            box("strainer", "chrome", [0.03, 0.04, 0.02], [0, 0.06, 0.19], when=S),
            rod("sticksS", "stick", 0.0075, [-0.15, 0.145, -0.06], [0.24, 0.145, 0.05], 6, r1=0.005, at=[[0, 0, 0], [0, 0.015, 0.04]], when=S),
        ], hold={"grip": [0, h + 0.28, 0.1], "axis": [1, 0, 0], "face": [0, 0, 1], "carry": {"axis": [1, 0, 0], "face": [0, 0, 1]}},
        era="1200-2030", region="everywhere")


# ---- THE BALL (`style`), on the ground: a stitched LEATHER ball (its panel seams and lacing), a FOOTBALL (white, its
# twelve black pentagons where an icosahedron's corners are) or a BEACH BALL (twelve coloured gores, white caps at the
# poles), its centre `r` up
def ball():
    L, Fb, Bb = {"style": "leather"}, {"style": "football"}, {"style": "beach"}
    phi = (1 + 5 ** 0.5) / 2
    ico = [v for a in (-1, 1) for b in (-phi, phi) for v in ([0, a, b], [a, b, 0], [b, 0, a])]
    fb = 0.11
    pents = [toward([0, fb, 0], v) for v in ico]
    # (the beach ball's gores: one lathe slice of the sphere per colour, 60 deg round, pole to pole -- smooth, not flat
    #  strips; the white caps close the poles)
    rb = 0.2
    prof = [[round(rb * math.sin(math.radians(th)), 4), round(rb - rb * math.cos(math.radians(th)), 4)] for th in [8 + 164 * i / 10 for i in range(11)]]
    gores = [lathe(f"gore{c}", f"g{c}", prof, [0, 0, 0], arc=[60 * c, 60 * c + 60], sides=8, smooth=True, when=Bb) for c in range(6)]
    return item("Ball", "tool", "a ball on the ground: a stitched leather one with its panel seams and lacing (style leather), a white football with twelve black pentagons (football), or a beach ball of twelve coloured gores with white caps at the poles (beach)",
        {"style": {"pick": ["leather", "football", "beach"]}},
        {"leather": {"pick": ["leather", "leather-dark", "hide"]}, "seam": "leather-dark", "lace": "linen", "white": "plastic-white", "black": "paint-black",
         "g0": "paint-red", "g1": "paint-white", "g2": "paint-yellow", "g3": "paint-white", "g4": "paint-blue", "g5": "paint-white", "cap": "plastic-white"}, [
            sphere("leatherBall", "leather", 0.11, [0, 0.11, 0], sides=16, when=L),
            ringx("seams", "seam", 0.1105, 0.0025, [[0, 0.11, 0, 0, 90, 0], [0, 0.11, 0, 90, 90, 0], [0, 0.11, 0]], sides=18, when=L),
            box("slot", "seam", [0.012, 0.064, 0.004], [0, 0.11, 0.1092], when=L),
            box("laces", "lace", [0.028, 0.004, 0.005], [[0, round(0.11 + dy, 4), round(math.sqrt(0.11 ** 2 - dy * dy) + 0.0015, 4), 0, round(-math.degrees(math.asin(dy / 0.11)), 2), 0]
                                                         for dy in [-0.028 + 0.0112 * i for i in range(6)]], when=L),
            sphere("football", "white", fb, [0, fb, 0], sides=18, when=Fb),
            cap("pentagons", "black", fb + 0.0025, 19, pents, sides=5, rings=2, when=Fb),
            *gores,
            cap("poles", "cap", rb + 0.002, 9, [[0, rb, 0], [0, rb, 0, 0, 180, 0]], sides=12, rings=1, when=Bb),
        ], hold={"grip": [0, 0.11, 0], "axis": [1, 0, 0], "face": [0, 0, 1], "carry": {"axis": [1, 0, 0], "face": [0, 0, 1]}},
        era="any", region="everywhere")


# ---- THE GUITAR (`style`), held as the lute is (neck up +y, face +z): a CLASSICAL guitar (a slotted head, its
# rollers across, nylon strings tied at the bridge) or a STEEL-STRUNG one (a solid head with six machine heads, bridge
# pins, a pickguard); figure-of-eight body, the rosette round the soundhole, twelve frets clear of the body
GTR = [(-0.245, 0), (-0.24, 0.07), (-0.222, 0.13), (-0.175, 0.176), (-0.11, 0.185), (-0.045, 0.165), (-0.005, 0.128), (0.03, 0.12), (0.085, 0.136),
       (0.145, 0.138), (0.2, 0.114), (0.234, 0.07), (0.245, 0)]


def outline(ctrl, k=1.0, n=3):
    """craftgen's body_outline with n samples a span (a guitar's long outline needs fewer than the fiddle's)"""
    half = smooth(ctrl, n)
    right = [[hw * k, y] for y, hw in half if hw > 1e-6]
    return [[0, ctrl[0][0]]] + right + [[0, ctrl[-1][0]]] + [[-x, y] for x, y in reversed(right)]


def guitar():
    C, St = {"style": "classical"}, {"style": "steel"}
    nut, saddle = 0.545, -0.105
    fret = lambda n: round(nut - (nut - saddle) * (1 - 2 ** (-n / 12)), 4)
    return item("Guitar", "tool", "a guitar held as the lute is, neck up +y and face +z: a figure-of-eight body, the rosette round the soundhole, twelve frets clear of the body -- classical with a slotted head and nylon strings (style classical) or steel-strung with six machine heads, bridge pins and a pickguard (steel)",
        {"style": {"pick": ["classical", "classical", "steel"]}},
        {"body": {"pick": ["mahogany", "walnut", "cherry"]}, "top": {"pick": ["pine", "cedar"]}, "neck": "mahogany", "board": "ebony", "dark": "mouth-dark", "rosette": {"pick": ["ebony", "walnut"]},
         "nylon": "gut", "steel": "steel", "bone": "bone", "guard": {"pick": ["lacquer-black", "amber"]}, "metal": {"pick": ["brass", "chrome"]}}, [
            plate("back", "body", outline(GTR), 0.004, [0, 0, -0.048]),
            plate("ribs", "body", outline(GTR, 0.975), 0.092, [0, 0, 0]),
            plate("top", "top", outline(GTR), 0.004, [0, 0, 0.048]),
            lathe("soundhole", "dark", [[0.043, 0.0], [0, 0.0]], [0, 0.085, 0.0505, 0, 90, 0], sides=18),
            lathe("rosetteRing", "rosette", [[0.05, 0.0], [0.0435, 0.0]], [0, 0.085, 0.0503, 0, 90, 0], sides=18, caps=False, double=True),
            box("neck", "neck", [0.054, nut - 0.24 + 0.01, 0.024], [0, (nut + 0.24) / 2, 0.034]),
            box("heel", "neck", [0.05, 0.05, 0.06], [0, 0.255, 0.02]),
            plate("fingerboard", "board", [[-0.026, nut], [0.026, nut], [0.029, 0.15], [-0.029, 0.15]], 0.006, [0, 0, 0.0495]),
            box("frets", "steel", [0.057, 0.0015, 0.002], [[0, fret(n), 0.0535] for n in range(1, 13)]),
            box("nut", "bone", [0.054, 0.005, 0.01], [0, nut, 0.054]),
            box("bridge", "rosette", [0.18, 0.026, 0.01], [0, saddle - 0.012, 0.055]),
            box("saddle", "bone", [0.075, 0.003, 0.005], [0, saddle, 0.0615]),
            rod("strings", "nylon", 0.0006, [0, saddle, 0.064], [0, nut, 0.0585], 3, along={"n": 6, "from": [-0.024, 0, 0], "to": [0.024, 0, 0]}, when=C),
            rod("stringsS", "steel", 0.0005, [0, saddle, 0.064], [0, nut, 0.0585], 3, along={"n": 6, "from": [-0.024, 0, 0], "to": [0.024, 0, 0]}, when=St),
            # the classical slotted head (its two cheeks, the rollers across) or the solid steel-string head with machine heads
            box("headCheeks", "neck", [0.014, 0.18, 0.018], [[-0.022, nut + 0.095, 0.028], [0.022, nut + 0.095, 0.028]], when=C),
            box("headEnd", "neck", [0.058, 0.02, 0.018], [0, nut + 0.18, 0.028], when=C),
            rod("rollers", "bone", 0.005, [-0.04, 0, 0], [0.04, 0, 0], 5, at=[[0, nut + 0.04 + 0.035 * i, 0.028] for i in range(3)], when=C),
            rod("keysC", "metal", 0.007, [0, 0, -0.004], [0, 0, 0.004], 6, at=[[sx * 0.05, nut + 0.04 + 0.035 * i, 0.028, 0, 0, 90] for sx in (-1, 1) for i in range(3)], stretch=[1, 1.6, 1], when=C),
            plate("headS", "neck", [[-0.028, nut], [0.028, nut], [0.04, nut + 0.17], [0.025, nut + 0.19], [-0.025, nut + 0.19], [-0.04, nut + 0.17]], 0.016, [0, 0, 0.032], when=St),
            box("machines", "metal", [0.022, 0.014, 0.012], [[sx * 0.044, nut + 0.045 + 0.05 * i, 0.03] for sx in (-1, 1) for i in range(3)], when=St),
            rod("buttons", "metal", 0.007, [0, 0, 0], [0.014, 0, 0], 6, at=[[sx * 0.055 - (0.014 if sx < 0 else 0), nut + 0.045 + 0.05 * i, 0.03] for sx in (-1, 1) for i in range(3)], stretch=[1, 1.4, 0.6], when=St),
            rod("pins", "bone", 0.0028, [0, 0, 0.058], [0, 0, 0.066], 5, at=[[-0.025 + 0.01 * i, saddle - 0.02, 0] for i in range(6)], when=St),
            plate("guard", "guard", [[0.045, -0.02], [0.065, 0.02], [0.075, 0.08], [0.055, 0.135], [0.035, 0.14], [0.05, 0.08]], 0.001, [0, 0, 0.0505], when=St),
        ], hold={"grip": [0, -0.05, 0.06], **LUTE_HOLD}, era="1800-2030", region="everywhere")


# ---- THE TRUMPET (`style`), its bell toward +x: a VALVED trumpet (the leadpipe from the mouthpiece to the three
# piston valves, the main tuning slide's U ahead of them, the bell bow behind and the bell yard alongside the valves to
# the flared bell) or a NATURAL trumpet (no valves: once folded, two long yards and two bows, a ball on the bell yard)
def trumpet():
    V, N = {"style": "valved"}, {"style": "natural"}
    bell = lambda id_, x0, y, z, L, R, w: lathe(id_, "brass", [[0.0062, 0], [0.008, L * 0.4], [0.014, L * 0.7], [0.03, L * 0.9], [R * 0.75, L * 0.97], [R, L], [R - 0.002, L], [0.004, 0.002]],
                                              [x0, y, z, 0, 0, -90], sides=18, caps=False, double=True, when=w)
    mouth = lambda id_, x, y, z, w: lathe(id_, "brass", [[0.0045, 0], [0.005, 0.05], [0.0085, 0.07], [0.013, 0.085], [0.0125, 0.09], [0.0095, 0.09]], [x, y, z, 0, 0, 90], sides=10, when=w)
    return item("Trumpet", "tool", "a trumpet, its bell toward +x: a valved trumpet, the leadpipe from the mouthpiece to the three piston valves, the main tuning slide ahead of them, the bell bow behind and the bell yard alongside to the flared bell (style valved), or a natural trumpet without valves, once folded, a ball on its bell yard (natural)",
        {"style": {"pick": ["valved", "valved", "natural"]}},
        {"brass": {"pick": ["brass", "brass", "silver", "gilt"]}, "pearl": "pearl", "dark": "mouth-dark"}, [
            mouth("mouthpiece", -0.17, 0.0, 0.0, V),
            rod("leadpipe", "brass", 0.0055, [-0.17, 0.0, 0.0], [-0.012, 0.0, 0.0], 8, r1=0.0068, when=V),
            # (each valve one lathe: its bottom cap, the casing, the top cap -- then the stem and its pearl button)
            lathe("valves", "brass", [[0, -0.083], [0.0105, -0.083], [0.0105, -0.075], [0.0095, -0.075], [0.0095, 0.035], [0.0105, 0.035], [0.0105, 0.043], [0, 0.043]], [[0.0, 0, 0], [0.026, 0, 0], [0.052, 0, 0]], sides=8, caps=False, when=V),
            rod("stems", "brass", 0.003, [0, 0.043, 0], [0, 0.068, 0], 6, at=[[0.0, 0, 0], [0.026, 0, 0], [0.052, 0, 0]], when=V),
            lathe("buttons", "pearl", [[0.009, 0], [0.009, 0.006], [0, 0.006]], [[0.0, 0.068, 0], [0.026, 0.068, 0], [0.052, 0.068, 0]], sides=8, when=V),
            sweep("tuningSlide", "brass", [[0.06, -0.012, 0], [0.16, -0.012, 0], [0.19, -0.035, 0], [0.16, -0.058, 0], [0.06, -0.058, 0]], r=0.0065, sides=8, when=V),
            sweep("bellBow", "brass", [[0.052, 0.02, -0.022], [0.0, 0.025, -0.024], [-0.12, 0.025, -0.024], [-0.155, -0.01, -0.024], [-0.12, -0.05, -0.024], [-0.02, -0.05, -0.024],
                                       [0.08, -0.04, -0.024]], r=0.0065, sides=8, when=V),
            sweep("thirdSlide", "brass", [[0.052, -0.02, 0.0], [0.09, -0.02, 0.018], [0.12, -0.03, 0.018], [0.09, -0.04, 0.018], [0.052, -0.04, 0.0]], r=0.005, sides=6, when=V),
            sweep("firstSlide", "brass", [[0.0, -0.02, 0.0], [-0.03, -0.02, 0.018], [-0.06, -0.03, 0.018], [-0.03, -0.04, 0.018], [0.0, -0.04, 0.0]], r=0.005, sides=6, when=V),
            rod("bellYard", "brass", 0.0065, [0.08, -0.04, -0.024], [0.2, -0.03, -0.024], 8, when=V),
            bell("bell", 0.2, -0.03, -0.024, 0.17, 0.062, V),
            rod("braces", "brass", 0.003, [0, 0, 0], [0, 0, 0.024], 5, at=[[-0.08, 0.0, -0.024], [0.15, -0.035, -0.024]], when=V),
            # the natural trumpet
            mouth("mouthN", -0.12, 0.0, 0.0, N),
            rod("yard1", "brass", 0.0055, [-0.12, 0.0, 0.0], [0.42, 0.0, 0.0], 8, when=N),
            sweep("frontBow", "brass", [[0.42, 0.0, 0.0], [0.47, 0.0, 0.0], [0.5, 0.035, 0.0], [0.47, 0.07, 0.0], [0.42, 0.07, 0.0]], r=0.0058, sides=8, when=N),
            rod("yard2", "brass", 0.006, [0.42, 0.07, 0.0], [-0.12, 0.07, 0.0], 8, when=N),
            sweep("backBow", "brass", [[-0.12, 0.07, 0.0], [-0.16, 0.07, 0.0], [-0.19, 0.05, 0.018], [-0.16, 0.035, 0.035], [-0.12, 0.035, 0.035]], r=0.0062, sides=8, when=N),
            rod("bellYardN", "brass", 0.0065, [-0.12, 0.035, 0.035], [0.3, 0.035, 0.035], 8, when=N),
            lathe("ballN", "brass", [[0.0068, -0.025], [0.016, -0.015], [0.018, 0], [0.016, 0.015], [0.0068, 0.025]], [0.12, 0.035, 0.035, 0, 0, -90], sides=10, caps=False, when=N),
            bell("bellN", 0.3, 0.035, 0.035, 0.24, 0.055, N),
            rod("bracesN", "brass", 0.003, [0, 0, 0], [0, 0.07, 0], 5, at=[[0.0, 0.0, 0.0], [0.3, 0.0, 0.0]], when=N),
        ], hold={"grip": [0.026, -0.02, 0], "axis": [0, 1, 0], "face": [1, 0, 0], "carry": {"axis": [0, -1, 0.2], "face": [1, 0, 0]}},
        era="1400-2030", region="everywhere")


ITEMS2.update({
    "tableware/cooking-pot": cooking_pot(), "tableware/frying-pan": frying_pan(), "tableware/kettle": kettle(), "tableware/bowl": bowl(),
    "tableware/goblet": goblet(), "tableware/bottle": bottle(),
    "tools/ladle": ladle(), "tools/wooden-spoon": wooden_spoon(), "tools/kitchen-knife": kitchen_knife(),
    "tools/wheelbarrow": wheelbarrow(), "tools/ladder": ladder(), "tools/watering-can": watering_can(), "tools/flowerpot": flowerpot(),
    "tools/suitcase": suitcase(), "tools/rope-coil": rope_coil(), "tools/chain": chain(),
    "tools/plough": plough(), "tools/butter-churn": butter_churn(), "tools/quern": quern(),
    "furniture/washstand": washstand(), "furniture/bathtub": bathtub(), "modern/furniture/toilet": toilet(), "modern/furniture/wheelchair": wheelchair(),
    "tools/crutch": crutch(), "tools/globe": globe(),
    "tools/drum": drum(), "tools/ball": ball(), "tools/guitar": guitar(), "tools/trumpet": trumpet(),
})


def main():
    for k, v in ITEMS2.items(): write(k, v)
    ipath = os.path.join(ROOT, "assets", "index.json")
    lock = open(ipath + ".lock", "w"); fcntl.flock(lock, fcntl.LOCK_EX)   # (other generators write the catalogue too)
    index = json.load(open(ipath))
    cats = {c["name"]: c for c in index["categories"]}
    where = {"tools": "Items: tools", "furniture": "Items: furniture", "tableware": "Items: tools", "modern": "Modern: furniture"}
    added = []
    for k in ITEMS2:
        c = cats[where[k.split("/")[0]]]["paths"]
        if "items/" + k not in c: c.append("items/" + k); added.append(k)
    # (the whole plants a flowerpot holds: written by flowergen.py but missing from the catalogue, so the viewer, which
    #  builds out of the catalogue alone, could not find them)
    fl = cats["Items: flowers"]["paths"]
    for f in FLOWERS:
        if f and f not in fl: fl.insert(len([q for q in fl if "/blooms/" not in q]), f); added.append(f)
    if added:
        with open(ipath, "w") as f: f.write(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
        print("registered", added)
    fcntl.flock(lock, fcntl.LOCK_UN)
    print(len(ITEMS2), "things:", ", ".join(f"{k} {len(v['parts'])}" for k, v in ITEMS2.items()))


if __name__ == "__main__":
    main()
