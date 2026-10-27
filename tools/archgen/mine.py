#!/usr/bin/env python3
"""THE MINE (2026-10-03): a mine of the Middle Ages -- silver, copper or salt (`ore`) -- as an arch-engine definition
(assets/architecture/village/mine.json) and a finish for each ore (assets/finishes/mine-<ore>.json).

On the surface, in its yard (`footW` x `footD`, the definition's own origin at the hauling shaft):
  * the SHAFT HOUSE (Kaue) over the HAULING SHAFT (Treibschacht): a boarded hut, inside it the WINDLASS (Haspel) --
    two posts, the drum, a crank at each end, two men to turn it -- the rope down the shaft with a kibble on each end,
    the shaft's timber collar round its mouth, waist high, so no one walks in;
  * the WALKING SHAFT (Fahrschacht) beside it, under a little roof: steep flights (25 cm on 25 cm, ladder-steep as
    the miners' were) down its lining, turning on landings at each end -- the way down for the walker;
  * the SPOIL HEAP (Halde), the ore-dressing bench where the ore is picked over, a stack of pit timber.
Ten metres down (y -10):
  * the SHAFT BOTTOM (Füllort): a chamber under both shafts, the kibble on its floor, a hooker beside it;
  (the miners are the mine's own CREW -- spots with `crew: "miner"`, kept there day and night by the game in the
   wardrobe's "miner" outfit, not the villagers' daily round)
  * the GALLERIES (Strecken), 1.6 m wide and 2.1 high, held by DOOR SETS (Türstöcke: two posts and a cap) every
    1.5 m -- a salt mine's stand in the bare salt -- a plank track down the middle for the wooden carts (Hunte);
  * the STOPES (Abbaue) at their ends, where the VEIN is worked: miners at the face with pick and hammer, the ore on
    the floor and in the carts, oil lamps on the walls.
The ground is open over the hauling shaft (`site.dig`) and over the walking shaft's top (its floors are near the
surface); over the deep galleries it stays whole and is walked on.

    python3 tools/archgen/mine.py
"""
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PI, PI2 = math.pi, math.pi / 2
R = lambda v: round(v, 4)
parts = {}
TIMBERED = {"ore": ["silver", "copper"]}       # (the salt stands without timber)


def box(w, l, h, *pts, **k):   # w along x, l along z, h up from y (the placement is the box's bottom middle)
    return {"type": "box", "width": R(w), "length": R(l), "height": R(h), "at": [[R(p[0]), R(p[1]), R(p[2]), R(p[3] if len(p) > 3 else 0)] for p in pts], **k}


def rect(name, x0, x1, z0, z1, y, h, **k):   # a box from its extents
    parts[name] = box(x1 - x0, z1 - z0, h, ((x0 + x1) / 2, y, (z0 + z1) / 2), **k)


def item(path, *pts, **k):
    return {"type": "item", "item": path, "at": [[R(p[0]), R(p[1]), R(p[2]), R(p[3] if len(p) > 3 else 0)] for p in pts], **k}


def marker(role, *pts, **data):
    return {"type": "marker", "role": role, "at": [[R(p[0]), R(p[1]), R(p[2]), R(p[3] if len(p) > 3 else 0)] for p in pts], "data": data}


def minus(r, holes):   # a rectangle (x0, x1, z0, z1) less some rectangles inside it: strips of what is left
    xs = sorted({r[0], r[1], *[h[0] for h in holes], *[h[1] for h in holes]})
    out = []
    for a, b in zip(xs, xs[1:]):
        if b - a < 1e-6 or b <= r[0] or a >= r[1]: continue
        zs = [(r[2], r[3])]
        for h in holes:
            if h[0] <= a + 1e-6 and h[1] >= b - 1e-6:
                zs = [seg for z0, z1 in zs for seg in ((z0, min(z1, h[2])), (max(z0, h[3]), z1)) if seg[1] - seg[0] > 1e-6]
        out += [(a, b, z0, z1) for z0, z1 in zs]
    return out


Y, GH, GW, T = -10.0, 2.1, 1.6, 0.5          # the gallery level, a gallery's height and width, the rock round it
ROCK = []                                    # the parts that are the rock (for the finish)
TIMBER, FLOORS, VEINS = [], [], []


def room(name, x0, x1, z0, z1, h, gaps=(), holes=(), floor=True):
    """a chamber cut in the rock: its floor, its ceiling (less `holes`: shafts coming down into it), its four walls of
    rock, with `gaps` -- (side, from, to, height) where a gallery or a shaft leaves it ('n' +z, 's' -z, 'e' +x, 'w' -x)"""
    if floor:
        rect(f"{name} floor", x0, x1, z0, z1, Y - 0.3, 0.3, walked=True); FLOORS.append(f"{name} floor")
    for i, (a, b, c, d) in enumerate(minus((x0 - T, x1 + T, z0 - T, z1 + T), list(holes))):
        rect(f"{name} ceiling {i}", a, b, c, d, Y + h, 0.4); ROCK.append(f"{name} ceiling {i}")
    for side in "nsew":
        along = (x0 - T, x1 + T) if side in "ns" else (z0, z1)
        gs = sorted([g for g in gaps if g[0] == side], key=lambda g: g[1])
        pos, k = along[0], 0
        for _, g0, g1, gh in gs + [(side, along[1], along[1], 0)]:
            if g0 - pos > 1e-6:
                seg = (pos, g0)
                if side == "n": rect(f"{name} wall n{k}", seg[0], seg[1], z1, z1 + T, Y, h)
                if side == "s": rect(f"{name} wall s{k}", seg[0], seg[1], z0 - T, z0, Y, h)
                if side == "e": rect(f"{name} wall e{k}", x1, x1 + T, seg[0], seg[1], Y, h)
                if side == "w": rect(f"{name} wall w{k}", x0 - T, x0, seg[0], seg[1], Y, h)
                ROCK.append(f"{name} wall {side}{k}"); k += 1
            if g1 > g0 and gh < h:   # the rock over the gap, down to its head
                if side == "n": rect(f"{name} wall n{k}", g0, g1, z1, z1 + T, Y + gh, h - gh)
                if side == "s": rect(f"{name} wall s{k}", g0, g1, z0 - T, z0, Y + gh, h - gh)
                if side == "e": rect(f"{name} wall e{k}", x1, x1 + T, g0, g1, Y + gh, h - gh)
                if side == "w": rect(f"{name} wall w{k}", x0 - T, x0, g0, g1, Y + gh, h - gh)
                ROCK.append(f"{name} wall {side}{k}"); k += 1
            pos = max(pos, g1)


def gallery(name, axis, c, a0, a1):
    """a gallery along `axis` ('z' or 'x'), its middle line at `c`, from a0 to a1: floor, the rock either side and over
    it, the door sets every 1.5 m (where it is timbered), the plank track"""
    w = GW / 2
    def r(n, lo, hi, s0, s1, y, h, **k):   # across lo..hi, along s0..s1
        if axis == "z": rect(n, lo, hi, s0, s1, y, h, **k)
        else: rect(n, s0, s1, lo, hi, y, h, **k)
    r(f"{name} floor", c - w, c + w, a0, a1, Y - 0.3, 0.3, walked=True); FLOORS.append(f"{name} floor")
    r(f"{name} rock left", c - w - T, c - w, a0, a1, Y, GH + 0.4); r(f"{name} rock right", c + w, c + w + T, a0, a1, Y, GH + 0.4)
    r(f"{name} rock over", c - w - T, c + w + T, a0, a1, Y + GH, 0.4)
    ROCK.extend([f"{name} rock left", f"{name} rock right", f"{name} rock over"])
    n = max(1, int((a1 - a0) / 1.5))
    sets = [a0 + (i + 0.5) * (a1 - a0) / n for i in range(n)]
    P = lambda s, x: (x, Y, s) if axis == "z" else (s, Y, x)
    parts[f"{name} set posts"] = {**box(0.14, 0.14, GH - 0.16, *[P(s, c + sg * (w - 0.1)) for s in sets for sg in (-1, 1)]), "when": TIMBERED}
    caps = box(GW - 0.04, 0.16, 0.16, *[(*P(s, c)[:1], Y + GH - 0.16, P(s, c)[2], 0 if axis == "z" else PI2) for s in sets])
    parts[f"{name} set caps"] = {**caps, "when": TIMBERED}
    TIMBER.extend([f"{name} set posts", f"{name} set caps"])
    r(f"{name} track", c - 0.42, c - 0.3, a0, a1, Y, 0.04); r(f"{name} track 2", c + 0.3, c + 0.42, a0, a1, Y, 0.04)
    TIMBER.extend([f"{name} track", f"{name} track 2"])
    return sets


# ---- the surface: the yard is the definition's own origin, the hauling shaft at it ----------------------------------
HX, HZ = 1.0, 0.8                                   # the hauling shaft's half sizes (inside its lining)
for nm, (a, b, c, d) in {"n": (-HX - 0.2, HX + 0.2, HZ, HZ + 0.2), "s": (-HX - 0.2, HX + 0.2, -HZ - 0.2, -HZ), "e": (HX, HX + 0.2, -HZ, HZ), "w": (-HX - 0.2, -HX, -HZ, HZ)}.items():
    rect(f"hauling shaft lining {nm}", a, b, c, d, Y + 3.0, -(Y + 3.0) + 0.9); TIMBER.append(f"hauling shaft lining {nm}")   # (up through the collar: 0.9 over the ground)
parts["shaft house"] = {"type": "enclosure", "plan": {"rect": [6.4, 5.2]}, "thickness": 0.12, "height": 2.6, "at": [[0, 0, 0, 0]], "openings": [],
                        "faces": {"0": [{"at": 1.4, "width": 1.3, "sill": 0, "springing": 2.0, "head": {"profile": "flat"}, "glass": False}],
                                  "2": [{"at": 0, "width": 0.8, "sill": 1.0, "springing": 1.7, "head": {"profile": "flat"}, "glass": False}]}}
parts["shaft house roof"] = {"type": "roof", "form": "gable", "width": 5.6, "length": 6.9, "pitch": 40, "overhang": 0.2, "at": [[0, 2.6, 0, PI2]]}
# the windlass: two posts beyond the collar, the drum over the shaft, a crank at each end
parts["windlass posts"] = box(0.18, 0.18, 1.25, (0, 0, -1.25), (0, 0, 1.25))
parts["windlass drum"] = box(0.28, 2.7, 0.28, (0, 0.92, 0))
# ...its AXLE through the posts and out past them, the crank ARMS fixed on its ends (one hanging, one standing: the two
# men's strokes half a turn apart) and the GRIPS out from the arms' far ends, along the axle -- each piece held by the
# one before (they hung beside the drum's ends, short of them)
parts["windlass axle"] = box(0.08, 2.9, 0.08, (0, 1.02, 0))
parts["windlass cranks"] = box(0.06, 0.06, 0.4, (0, 0.7, -1.42), (0, 1.02, 1.42))
parts["windlass handles"] = box(0.05, 0.24, 0.05, (0, 0.7, -1.55), (0, 1.37, 1.55))
TIMBER += ["windlass posts", "windlass drum", "windlass axle", "windlass cranks", "windlass handles"]
parts["ropes"] = {"type": "column", "radius": 0.014, "height": R(0.92 - (Y + 0.6)), "sides": 5, "at": [[0.3, R(Y + 0.6), 0, 0]]}
parts["rope up"] = {"type": "column", "radius": 0.014, "height": 2.4, "sides": 5, "at": [[-0.3, -1.5, 0, 0]]}
parts["kibbles"] = item("items/tools/bucket", (0.3, Y, 0), (-0.3, -1.9, 0), solid=False)
parts["windlass men"] = {"type": "marker", "role": "spot", "at": [[0.2, 0, -1.75, 0], [-0.2, 0, 1.75, 0]], "data": {"pose": "stand", "work": 1, "gesture": "lift", "face": [PI2, -PI2], "crew": "miner"}}
# the walking shaft: inside x 6 .. 10.7, z -1.2 .. 1.2; flights 10 steps of 25 cm on 25 cm, turning on landings at each end
# (each landing as deep as a flight is wide: room to stand at the foot of the next before climbing it)
FW_, SW = 1.1, 2.4      # a flight's width, the shaft's inside across (two flights and a hand's gap: the walker's room by its lining)
X0, Z0, LS, LD = 6.0, -1.2, 2.5, FW_
XL = X0 + 2 * LD + LS   # the shaft's east inside face
for nm, (a, b, c, d, y0) in {"n": (X0 - 0.2, XL + 0.2, Z0 + SW, Z0 + SW + 0.2, Y), "s": (X0 - 0.2, XL + 0.2, Z0 - 0.2, Z0, Y), "e": (XL, XL + 0.2, Z0, Z0 + SW, Y),
                             "w": (X0 - 0.2, X0, Z0, Z0 + SW, Y + 2.3)}.items():
    rect(f"walking shaft lining {nm}", a, b, c, d, y0, -y0 + (0 if nm == "w" else 0.9)); TIMBER.append(f"walking shaft lining {nm}")
for k in range(4):
    top = -LS * k
    if k % 2 == 0: at = [X0 + LD + LS, top - LS, Z0, PI]           # down eastward: climbs west from its foot at the east landing
    else: at = [X0 + LD, top - LS, Z0 + SW, 0]                    # down westward: climbs east from the west landing
    parts[f"walking flight {k}"] = {"type": "flight", "run": 0.25, "width": FW_, "base": 0, "top": LS, "steps": 10, "steep": True, "landing": 0,
                                    "at": [[R(v) for v in at]]}
for k in range(5):   # the landings: west at 0, -5, -10; east at -2.5, -7.5
    y = -LS * k
    x0 = X0 if k % 2 == 0 else X0 + LD + LS
    x0b = X0 - 0.2 - T if k == 4 else x0   # (the bottom one through the gap in the chamber's wall: one floor from the chamber in)
    rect(f"walking landing {k}", x0b, x0 + LD, Z0, Z0 + SW, y - 0.2, 0.2, walked=True); TIMBER.append(f"walking landing {k}")
rect("walking shaft bottom", X0 + LD, X0 + LD + LS, Z0, Z0 + SW, Y - 0.3, 0.3, walked=True); FLOORS.append("walking shaft bottom")
parts["walking shaft roof posts"] = box(0.14, 0.14, 2.3, (X0 - 0.3, 0, Z0 - 0.35), (XL + 0.3, 0, Z0 - 0.35), (X0 - 0.3, 0, Z0 + SW + 0.35), (XL + 0.3, 0, Z0 + SW + 0.35))
parts["walking shaft roof"] = {"type": "roof", "form": "gable", "width": 3.8, "length": R(XL - X0 + 1.3), "pitch": 32, "overhang": 0.1, "at": [[R((X0 + XL) / 2), 2.3, 0, PI2]]}
TIMBER += ["walking shaft roof posts"]
# the spoil heap, the dressing bench, the pit timber
parts["spoil heap"] = {"type": "column", "radius": 4.2, "height": 2.0, "sides": 12, "taper": 0.12, "at": [[-8.0, 0, 4.5, 0]]}
parts["dressing bench"] = box(2.2, 0.7, 0.8, (-6.5, 0, -5.0))
parts["ore pile"] = {"type": "column", "radius": 0.7, "height": 0.45, "sides": 8, "taper": 0.2, "at": [[-4.4, 0, -5.4, 0], [-6.5, 0.8, -5.0, 0]]}
parts["dressers"] = marker("spot", (-6.5, 0, -4.05, 0), pose="stand", work=1, gesture="tend", face=PI2)
parts["baskets"] = item("items/tools/basket", (-7.5, 0, -4.2), (-8.2, 0, -5.3, 0.6), solid=False)
parts["sacks"] = item("items/tools/sack-standing", (-5.0, 0, -4.0), (-4.6, 0, -3.6, 1.0), solid=False)
parts["pit timber"] = box(3.0, 0.16, 0.16, *[(4.0, 0.16 * i, 5.5 + 0.18 * j) for i in range(3) for j in range(4 - i)])
TIMBER += ["dressing bench", "pit timber"]

# ---- ten metres down ------------------------------------------------------------------------------------------------
# the shaft bottom: x -3 .. 5.8, z -3 .. 3, 3 m high; the hauling shaft comes down through its ceiling, the walking
# shaft opens from its east wall, the main gallery leaves north, the side gallery south
room("shaft bottom", -3.0, 5.8, -3.0, 3.0, 3.0,
     gaps=[("e", Z0, Z0 + SW, 2.3), ("n", -2.3, -0.7, GH), ("s", 0.7, 2.3, GH)],
     holes=[(-HX - 0.2, HX + 0.2, -HZ - 0.2, HZ + 0.2)])
parts["hooker"] = marker("spot", (1.2, Y, 0.0, 0), pose="stand", work=1, gesture="lift", face=PI, crew="miner")
parts["shaft bottom lamps"] = marker("fire", (-2.9, Y + 1.9, -1.5), (5.7, Y + 1.9, 2.0), r=0.035, h=0.09, candle=True)
parts["shaft bottom cart"] = {"type": "component", "use": "components/mine-cart", "at": [[-1.5, Y, 1.8, 0]]}
# the main gallery north to the first stope; the side gallery south to the second
s1 = gallery("main gallery", "z", -1.5, 3.0, 30.0)     # (from the chamber's inner face: its floor runs through the gap in the wall)
s2 = gallery("side gallery", "z", 1.5, -20.0, -3.0)
room("north stope", -5.0, 2.0, 30.0, 36.0, 3.4, gaps=[("s", -2.3, -0.7, GH)])
room("south stope", -2.0, 5.0, -26.0, -20.0, 3.2, gaps=[("n", 0.7, 2.3, GH)])
# the veins: bands in the stopes' far walls and down their sides, a little proud of the rock; the ore broken out on the floor
parts["vein north"] = box(6.6, 0.04, 1.3, (-1.5, Y + 0.7, 35.98))
parts["vein north side"] = box(0.04, 4.0, 0.9, (1.98, Y + 1.1, 33.5), (-4.98, Y + 0.9, 33.0))
parts["vein south"] = box(6.6, 0.04, 1.1, (1.5, Y + 1.0, -25.98))
parts["vein south side"] = box(0.04, 3.5, 0.8, (4.98, Y + 0.8, -23.5))
parts["broken ore"] = {"type": "column", "radius": 0.55, "height": 0.35, "sides": 7, "taper": 0.25, "at": [[0.6, Y, 35.0, 0], [-3.6, Y, 34.6, 0], [3.4, Y, -25.0, 0]]}
VEINS += ["vein north", "vein north side", "vein south", "vein south side", "broken ore"]
parts["miners north"] = {"type": "marker", "role": "spot", "at": [[-2.6, Y, 35.2, 0], [0.0, Y, 35.25, 0], [1.3, Y, 33.0, 0]],
                         "data": {"pose": "stand", "work": 1, "gesture": ["pick", "hammer", "pick"], "tool": ["items/tools/pickaxe", "items/tools/hammer", "items/tools/pickaxe"], "face": [-PI2, -PI2, 0], "crew": "miner"}}
parts["miners south"] = {"type": "marker", "role": "spot", "at": [[0.5, Y, -25.2, 0], [4.2, Y, -23.0, 0]],
                         "data": {"pose": "stand", "work": 1, "gesture": ["hammer", "pick"], "tool": ["items/tools/hammer", "items/tools/pickaxe"], "face": [PI2, 0], "crew": "miner"}}
parts["loader"] = marker("spot", (-0.9, Y, 32.4, 0), pose="stand", work=1, gesture="dig", tool="items/tools/spade", face=-PI2, crew="miner")
parts["carts"] = {"type": "component", "use": "components/mine-cart", "at": [[-1.5, Y, 31.4, 0], [-1.5, Y, 14.0, 0], [1.5, Y, -12.0, 0]]}
parts["gallery lamps"] = marker("fire", *[(-2.27, Y + 1.75, z) for z in s1[::4]], *[(0.77, Y + 1.75, z) for z in s2[::4]],
                                (-4.9, Y + 2.0, 32.0), (1.9, Y + 2.0, 34.5), (-1.9, Y + 2.0, -21.0), (4.9, Y + 2.0, -24.5), r=0.035, h=0.09, candle=True)
parts["lanterns"] = item("items/tools/lantern", (-4.5, Y, 31.0), (4.4, Y, -21.0), solid=False)

doc = {"name": "Mine",
       "_about": "A MINE of the Middle Ages (silver, copper or salt: `ore`): on the surface the shaft house over the hauling shaft with its windlass and kibbles, the walking shaft with its steep flights under a little roof, the spoil heap, the dressing bench, pit timber; ten metres down the shaft bottom, timbered galleries with a plank track and wooden carts, and the stopes where miners work the vein with pick and hammer by the light of their lamps. The ground is open only over the shafts.",
       "site": {"origin": True, "dig": [[-HX, -HZ, HX, HZ], [X0, Z0, XL, Z0 + SW]]},   # (the shafts' mouths: the ground open over them)
       "params": {"detail": 4, "ore": "silver", "footW": 24, "footD": 18,
                  "_ore": "silver | copper | salt: the rock and the vein (the finishes mine-<ore>), and whether the galleries are timbered (salt stands without)"},
       "parts": parts, "build": list(parts), "walked": True}
open(os.path.join(ROOT, "assets/architecture/village/mine.json"), "w").write(json.dumps(doc, indent=1) + "\n")

# the cart (Hunt): a plank box on four little wheels, its load of ore
cart = {"name": "Mine cart", "_about": "a Hunt: the miners' wooden cart, a plank box on four little wheels, loaded with ore",
        "params": {"detail": 4},
        "parts": {"body": box(0.62, 1.0, 0.42, (0, 0.2, 0)), "load": box(0.5, 0.86, 0.12, (0, 0.6, 0)),
                  "wheels": box(0.08, 0.22, 0.22, (-0.36, 0.0, 0.3), (0.36, 0.0, 0.3), (-0.36, 0.0, -0.3), (0.36, 0.0, -0.3))}}
cart["build"] = list(cart["parts"])
open(os.path.join(ROOT, "assets/architecture/components/mine-cart.json"), "w").write(json.dumps(cart, indent=1) + "\n")

HUT = ["shaft house", "shaft house roof", "walking shaft roof"]
ORES = {"silver": ("mine-gneiss", "vein-galena"), "copper": ("mine-slate", "vein-malachite"), "salt": ("rock-salt", "vein-salt")}
for ore, (rock, vein) in ORES.items():
    fin = {"name": f"Mine ({ore})", "building": "architecture/village/mine",
           "_about": f"the {ore} mine: its rock {rock}, the vein {vein}, the timber grey oak, the galleries' floors trodden earth, the shaft house boarded under thatch",
           "rules": [{"parts": VEINS + ["shaft bottom cart/load", "carts/load", "ore pile"], "pattern": "stone/ore vein", "palette": vein},
                     {"parts": ["shaft house roof", "walking shaft roof"], "surface": "roof", "pattern": "roofs/thatch", "palette": "thatch-grey"},
                     {"parts": ["shaft house"], "pattern": "timber/planks", "palette": "oak-grey"},
                     {"parts": TIMBER + ["kind:flight", "shaft bottom cart", "carts"], "pattern": "timber/bark", "palette": "oak-grey"},
                     {"parts": FLOORS, "surface": "floor", "pattern": "stone/sand", "palette": "earth" if ore != "salt" else rock},
                     {"parts": ["spoil heap"], "pattern": "stone/rock face", "palette": rock},
                     {"pattern": "stone/rock face", "palette": rock}]}
    open(os.path.join(ROOT, f"assets/finishes/mine-{ore}.json"), "w").write(json.dumps(fin, indent=1) + "\n")
print("mine:", len(parts), "parts; galleries", len(s1), "+", len(s2), "door sets")

# the catalogue: the mine with the village, its cart with the components, its finishes
ipath = os.path.join(ROOT, "assets", "index.json")
index = json.load(open(ipath))
for c in index["categories"]:
    add = {"Village": ["architecture/village/mine"], "Architecture components": ["architecture/components/mine-cart"],
           "Finishes": [f"finishes/mine-{o}" for o in ORES]}.get(c["name"], [])
    c["paths"] += [p for p in add if p not in c["paths"]]
json.dump(index, open(ipath, "w"), indent=2, ensure_ascii=False)
