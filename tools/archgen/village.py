#!/usr/bin/env python3
"""The village's buildings, written out as arch-engine definitions (docs/arch.md "The village").

    python3 tools/archgen/village.py      # -> assets/architecture/village/*.json, assets/architecture/furniture/*.json

Every building here is PARAMETRIC: a town house is one definition for any frontage, depth, storey height and number
of storeys, with or without a cellar, a shop front and a trade inside -- the village plan (town.js) picks the numbers
and the parts to build (`build`) from the seed. What varies within a definition is written as expressions over its
params; what varies BETWEEN definitions (a gable to the street or the eaves, a jetty, stone or timber) is what this
script writes differently. Life -- beds, doors, work places, seats, fires, the way up the stairs -- is written in as
MARKERS (arch/assemble.js), so it comes out wherever the part that carries it is built, turned with the house.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "assets", "architecture")
PI2 = "1.5707963"
PI2f = 1.5707963


def write(path, doc):
    full = os.path.join(OUT, path + ".json")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")


def write_finish(key, doc):
    full = os.path.join(ROOT, "assets", "finishes", key + ".json")
    with open(full, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")


def box(w, l, h, at, **k):
    return {"type": "box", "width": w, "length": l, "height": h, "at": at if isinstance(at[0], list) else [at], **k}


def col(r, h, at, sides=10, **k):
    return {"type": "column", "radius": r, "height": h, "sides": sides, "at": at if isinstance(at[0], list) else [at], **k}


def marker(role, at, **data):
    return {"type": "marker", "role": role, "at": at if isinstance(at[0], list) else [at], "data": data}


def comp(use, at, params=None, **k):
    return {"type": "component", "use": use, "at": at if isinstance(at[0], list) else [at], **({"params": params} if params else {}), **k}


def item(path, at, params=None, **k):
    """a thing out of assets/items (arch/assemble.js `item`): drawn in its own materials, its box walked round, its markers the room's"""
    return {"type": "item", "item": path, "at": at if isinstance(at[0], list) else [at], **({"params": params} if params else {}), **k}


# ---- FURNITURE: components that carry their own life ------------------------------------------------------------------
# (local frame: standing on the floor at y 0, centred; a bed lies along z with its head at -z.) The movables are ITEMS
# (assets/items/furniture: a bedstead, a trestle table and its benches, a chest, casks, a settle for a pew), each a
# little its own by `look` -- the seed a house passes in; the hearths, forges, ovens and counters stay masonry and joinery
# of the house's own.
def furniture():
    F = {}
    F["bed"] = {"name": "Bed", "_about": "a joined bedstead for two (items/furniture/bedstead, turned to lie along z), head against the wall at -z; the pallet on it is where two sleep (village-life lays them side by side) -- on the storey the house says",
                "params": {"detail": 4, "w": 1.45, "l": 2.05, "look": 1, "storey": 0},
                "parts": {"bed": item("items/furniture/bedstead", [0, 0, 0, "0 - " + PI2], {"w": "w", "l": "l"}, seed="look", data={"storey": "storey"})},
                "build": ["bed"]}
    F["table"] = {"name": "Table and benches", "_about": "a trestle table (items/furniture/trestle-table), a bench either side, a seat and two places to eat on each",
                  "params": {"detail": 4, "L": 1.8, "look": 1},
                  "parts": {"table": item("items/furniture/trestle-table", [0, 0, 0, 0], {"L": "L", "d": 0.8}, seed="look"),
                            "benches": item("items/furniture/bench", [[0, 0, 0.68, 0], [0, 0, -0.68, 3.14159265]], {"L": "L"}, seed="look + 1", markers=["seat"])},
                  "build": ["table", "benches"]}
    F["hearth"] = {"name": "Hearth", "_about": "a raised stone hearth against a wall (+z its front), the fire on it, framed as a fireplace: two jambs up from the hearth to the hood, the hood, and its flue on up to the ceiling (2026-10-24: the hood had hung in the air)",
                   "params": {"detail": 4},
                   "parts": {"hearth": box(1.5, 0.8, 0.45, [0, 0, 0, 0]), "hood": box(1.6, 0.6, 0.5, [0, 1.7, -0.1, 0]),
                             "jambs": box(0.2, 0.6, 1.25, [[-0.7, 0.45, -0.1, 0], [0.7, 0.45, -0.1, 0]]),
                             "flue": box(0.8, 0.4, 0.7, [0, 2.2, -0.2, 0]),
                             "fireback": box(1.2, 0.04, 1.25, [0, 0.45, -0.38, 0]),
                             "fire": marker("fire", [0, 0.46, 0.05, 0], r=0.25, h=0.5)},
                   "build": ["hearth", "jambs", "hood", "flue", "fireback", "fire"]}
    F["chest"] = {"name": "Chest", "_about": "a six-board chest bound with iron (items/furniture/plank-chest)", "params": {"detail": 4, "look": 1},
                  "parts": {"chest": item("items/furniture/plank-chest", [0, 0, 0, 0], {"w": 0.95}, seed="look")}, "build": ["chest"]}
    F["barrels"] = {"name": "Barrels", "_about": "a row of casks on their ends (items/furniture/cask), a cellar's or a cooper's",
                    "params": {"detail": 4, "n": 3, "look": 1},
                    "parts": {"casks": item("items/furniture/cask", ["0 - (n - 1) * 0.45", 0, 0, 0], seed="look", repeat={"count": "n", "step": [0.9, 0, 0, 0]})},
                    "build": ["casks"]}
    # the trades: each a WORKSHOP's furniture, about 3.6m square, the counter or door side at +z; the worker's place
    # (work: a job for a villager, gesture and tool from people.js) and a customer's
    def trade(name, about, parts, work, customer=(1.2, 0, 1.4)):
        wx, wy, wz, face, gesture, tool, pose = work
        p = dict(parts)
        p["worker"] = marker("spot", [wx, wy, wz, 0], work=1, gesture=gesture, face=face, pose=pose, **({"tool": tool} if tool else {}))
        p["customer"] = marker("spot", [customer[0], customer[1], customer[2], 0], face=1.5707963, pose="stand")
        return {"name": name, "_about": about, "params": {"detail": 4}, "parts": p, "build": list(p.keys())}
    # (parts are NAMED BY WHAT THEY ARE MADE OF -- town.js TRADE_MATERIALS finishes "brick", "iron", "clay", "cloth"...
    #  parts by those names, the rest is the town's wood; tools hang from racks head-up (an item's origin is its foot))
    hang = lambda path, x, y, z, L, a=0, **k: item(path, [x, round(y - L, 3), z, a], solid=False, **k)
    def rack(name, x, z, w, y=1.55, a=0):   # a board on the wall with pegs, the tools hung from it
        return {f"{name}": box(w, 0.04, 0.12, [x, y, z, a]), f"{name} pegs": box(0.03, 0.08, 0.03, [[x + (i - 1.5) * w / 4, y + 0.05, z + 0.05, a] for i in range(4)])}
    F["smithy"] = trade("Smithy", "the brick forge against the back wall, its fire under a hood and chimney, the bellows beside it; the anvil on its stump mid-room, the quench tub, iron stock leaning by the wall, the tools on their rack",
                        {"forge brick": box(1.9, 1.2, 0.9, [0.6, 0, -1.3, 0]), "forge hearth iron": box(1.2, 0.7, 0.04, [0.6, 0.9, -1.2, 0]),
                         "coals": marker("fire", [0.6, 0.94, -1.2, 0], r=0.22, h=0.45),
                         "hood brick": box(2.1, 1.3, 0.6, [0.6, 2.0, -1.3, 0]), "chimney brick": box(0.8, 0.7, 0.4, [0.6, 2.6, -1.4, 0]),
                         "bellows leather": box(0.55, 0.9, 0.22, [1.85, 0.75, -1.1, 0]), "bellows board": box(0.6, 0.95, 0.04, [1.85, 0.97, -1.1, 0]),
                         "bellows stand": box(0.5, 0.6, 0.75, [1.85, 0, -1.1, 0]),
                         "stump": col(0.3, 0.55, [-0.5, 0, 0.1, 0], sides=8, taper=0.9),
                         "anvil foot iron": box(0.34, 0.24, 0.1, [-0.5, 0.55, 0.1, 0]), "anvil waist iron": box(0.2, 0.15, 0.12, [-0.5, 0.65, 0.1, 0]),
                         "anvil face iron": box(0.5, 0.2, 0.12, [-0.53, 0.77, 0.1, 0]), "anvil horn iron": box(0.16, 0.11, 0.08, [-0.2, 0.8, 0.1, 0]),
                         "hammer": item("items/tools/hammer", [-0.62, 0.89, 0.05, 0.3], solid=False),
                         "quench": item("items/furniture/cask", [-1.4, 0, -1.2, 0], {"h": 0.6, "r": 0.34}),
                         "stock iron": box(0.03, 0.03, 1.4, [[-1.65 + k * 0.06, 0, -0.4 + k * 0.04, 0] for k in range(5)]),
                         **rack("rack", -0.4, -1.65, 1.0),
                         "tongs": hang("items/tools/tongs", -0.6, 1.6, -1.6, 0.42), "tongs 2": hang("items/tools/tongs", -0.4, 1.6, -1.6, 0.42),
                         "hammer 2": hang("items/tools/hammer", -0.15, 1.6, -1.6, 0.37)},
                        (-0.5, 0, 1.0, 1.5707963, "hammer", "hammer", "stand"))
    F["bakery"] = trade("Bakery", "the domed brick oven at the back with its mouth and the woodpile beside it, the peel against it; the kneading trough and table with the day's loaves, flour in sacks, a shelf of bread for sale",
                        {"oven brick": box(1.8, 1.5, 1.0, [0.5, 0, -1.2, 0]), "oven dome brick": {"type": "dome", "sides": 12, "radius": 0.75, "thickness": 0, "head": {"profile": "semicircular"}, "at": [[0.5, 1.0, -1.2, 0]]},
                         "oven mouth iron": box(0.5, 0.04, 0.35, [0.5, 0.3, -0.44, 0]),
                         "glow": marker("fire", [0.5, 0.35, -0.5, 0], r=0.2, h=0.3),
                         "firewood": box(0.6, 0.35, 0.12, [[1.65, k * 0.12, -1.3 + (k % 2) * 0.05, 1.5707963] for k in range(5)]),
                         "peel": box(0.05, 0.3, 1.8, [-0.45, 0, -1.55, 0]), "peel blade": box(0.32, 0.02, 0.36, [-0.45, 0.02, -1.42, 0]),
                         "table": item("items/furniture/kitchen-table", [-0.4, 0, 0.3, 0], {"L": 1.6, "d": 0.8, "h": 0.85}, markers=False),
                         "dough": col(0.17, 0.08, [[-0.8, 0.85, 0.3, 0], [-0.35, 0.85, 0.2, 0]], sides=8, taper=0.7),
                         "loaves": item("items/food/round-loaf", [[0.05, 0.85, 0.35, 0], [0.25, 0.85, 0.15, 1.2]], solid=False),
                         "flour": item("items/tools/sack-standing", [[-1.5, 0, -0.5, 0], [-1.45, 0, 0.1, 0.8]], solid=False),
                         "shelf": box(1.6, 0.4, 0.04, [[-0.6, 1.1, 1.5, 0], [-0.6, 1.5, 1.5, 0]]), "shelf posts": box(0.05, 0.4, 1.55, [[-1.38, 0, 1.5, 0], [0.18, 0, 1.5, 0]]),
                         "bread": item("items/food/bread", [[-1.1 + k * 0.28, 1.14, 1.5, 0] for k in range(5)] + [[-1.0 + k * 0.3, 1.54, 1.5, 0] for k in range(4)], solid=False)},
                        (-0.4, 0, 1.25, 1.5707963, "knead", None, "stand"))
    F["pottery"] = trade("Pottery", "the kick wheel with the clay on its head and the potter's stool; a small brick kiln in the corner; shelves of pots, jugs and jars drying; the clay tub",
                         {"wheel": col(0.36, 0.5, [0.2, 0, 0, 0], sides=12), "wheel head clay": col(0.24, 0.06, [0.2, 0.5, 0, 0], sides=12),
                          "pot clay": col(0.1, 0.16, [0.2, 0.56, 0, 0], sides=10, taper=0.75),
                          "stool": item("items/furniture/stool", [-0.6, 0, 0, 0], {"h": 0.45}, markers=False),
                          "kiln brick": col(0.55, 1.1, [1.3, 0, -1.25, 0], sides=12), "kiln dome brick": {"type": "dome", "sides": 12, "radius": 0.55, "thickness": 0, "head": {"profile": "semicircular"}, "at": [[1.3, 1.1, -1.25, 0]]},
                          "glow": marker("fire", [1.3, 0.25, -0.72, 0], r=0.12, h=0.22),
                          "shelf": box(2.0, 0.4, 0.04, [[-0.4, 0.5, -1.55, 0], [-0.4, 1.0, -1.55, 0], [-0.4, 1.5, -1.55, 0]]),
                          "shelf posts": box(0.05, 0.4, 1.55, [[-1.38, 0, -1.55, 0], [0.58, 0, -1.55, 0]]),
                          "pots clay": col(0.12, 0.26, [[-1.15 + k * 0.38, 0.54, -1.55, 0] for k in range(5)], sides=10, taper=0.7),
                          "jars clay": col(0.09, 0.3, [[-1.1 + k * 0.4, 1.04, -1.55, 0] for k in range(5)], sides=10, taper=0.55),
                          "bowls clay": col(0.13, 0.08, [[-1.1 + k * 0.33, 1.54, -1.55, 0] for k in range(6)], sides=10, taper=1.4),
                          "jugs": item("items/tableware/jug", [[1.4, 0, 0.5, 0], [1.2, 0, 0.75, 1.0], [1.5, 0, 0.85, 2.0]], solid=False),
                          "tub": item("items/furniture/cask", [-1.4, 0, 0.6, 0], {"h": 0.45, "r": 0.32})},
                         (-0.6, 0.47, 0, 0, "knead", None, "sit"))
    loom = {"loom posts": box(0.09, 0.09, 1.6, [[x, 0, z, 0] for x in (-0.9, 0.9) for z in (-1.2, 0.05)]),
            "loom top": box(1.95, 1.4, 0.09, [0, 1.6, -0.58, 0]), "loom rails": box(0.08, 1.3, 0.08, [[-0.9, 0.15, -0.58, 0], [0.9, 0.15, -0.58, 0]]),
            "warp beam": col(0.06, 1.7, [0, 0.85, -1.15, 0], sides=6), "breast beam": box(1.8, 0.1, 0.1, [0, 0.8, 0.05, 0]),
            "warp cloth": box(1.5, 1.1, 0.012, [0, 0.83, -0.55, 0]), "web cloth": box(1.5, 0.35, 0.02, [0, 0.82, -0.1, 0]),
            "heddles": box(1.6, 0.05, 0.5, [0, 1.0, -0.6, 0]), "treadles": box(0.12, 0.7, 0.04, [[-0.3 + k * 0.2, 0.08, -0.3, 0] for k in range(4)])}
    F["weaver"] = trade("Weaver", "a floor loom -- its frame, the warp running back to the warp beam, the woven cloth on the breast beam, heddles and treadles -- the weaver on its bench; the spinning wheel, baskets of wool, hanks of yarn hung up",
                        {**loom, "bench": item("items/furniture/bench", [0, 0, 0.55, 0], {"L": 1.4, "d": 0.35}, markers=False),
                         "wheel": item("items/furniture/spinning-wheel", [1.35, 0, -1.0, 0]),
                         "wool": item("items/tools/basket", [[1.45, 0, 0.3, 0], [1.2, 0, 0.75, 0.6]], solid=False),
                         "fleece wool": col(0.12, 0.12, [[1.45, 0.3, 0.3, 0], [1.2, 0.3, 0.75, 0]], sides=8, taper=0.6),
                         "yarn rail": box(1.2, 0.04, 0.04, [-1.0, 1.75, 1.2, 1.5707963]),
                         "yarn wool": col(0.05, 0.45, [[-1.6, 1.3, 0.75 + k * 0.28, 0] for k in range(4)], sides=6)},
                        (0, 0.47, 0.55, 1.5707963, "weave", None, "sit"))
    F["tailor"] = trade("Tailor", "the cutting table with a length of cloth laid out and the shears on it, bolts of cloth in their colours on the shelves behind, a garment on its form, the stool",
                        {"table": item("items/furniture/trestle-table", [0, 0, -0.2, 0], {"L": 1.8, "d": 0.9, "h": 0.85}, markers=False),
                         "laid cloth": box(1.2, 0.7, 0.01, [-0.1, 0.85, -0.2, 0.08]), "shears iron": box(0.03, 0.22, 0.012, [[0.55, 0.86, -0.15, 0.4], [0.57, 0.86, -0.15, -0.3]]),
                         "shelf": box(2.0, 0.45, 0.04, [[0, 0.8, -1.55, 0], [0, 1.45, -1.55, 0]]), "shelf posts": box(0.05, 0.45, 1.9, [[-0.98, 0, -1.55, 0], [0.98, 0, -1.55, 0]]),
                         "bolts madder": col(0.12, 0.6, [[-0.75, 0.84, -1.55, 0], [0.15, 1.49, -1.55, 0]], sides=8),
                         "bolts woad": col(0.12, 0.6, [[-0.45, 0.84, -1.55, 0], [0.45, 1.49, -1.55, 0]], sides=8),
                         "bolts weld": col(0.12, 0.6, [[-0.15, 0.84, -1.55, 0], [-0.75, 1.49, -1.55, 0]], sides=8),
                         "bolts linen": col(0.12, 0.6, [[0.15, 0.84, -1.55, 0], [0.75, 1.49, -1.55, 0]], sides=8),
                         "bolts russet": col(0.12, 0.6, [[0.45, 0.84, -1.55, 0], [0.75, 0.84, -1.55, 0], [-0.45, 1.49, -1.55, 0]], sides=8),
                         "form stand": col(0.03, 1.0, [1.35, 0, 0.6, 0], sides=6), "form foot": col(0.22, 0.05, [1.35, 0, 0.6, 0], sides=8),
                         "garment madder": col(0.2, 0.62, [1.35, 0.95, 0.6, 0], sides=10, taper=1.25),
                         "stool": item("items/furniture/stool", [0.9, 0, 0.6, 0], {"h": 0.5}, markers=False)},
                        (0, 0, 0.9, 1.5707963, "sew", None, "stand"))
    F["carpenter"] = trade("Carpenter", "the joiner's bench on its legs with a vice and the work on it, a sawhorse, planks and boards stacked against the wall, the tools on their rack, shavings on the floor",
                           {"bench legs": box(0.1, 0.1, 0.78, [[x, 0, z, 0] for x in (-0.95, 0.95) for z in (-0.52, -0.08)]), "bench top": box(2.2, 0.6, 0.1, [0, 0.78, -0.3, 0]),
                            "bench rails": box(1.9, 0.06, 0.08, [[0, 0.2, -0.52, 0], [0, 0.2, -0.08, 0]]), "vice": box(0.3, 0.12, 0.25, [-0.95, 0.62, 0.02, 0]),
                            "workpiece": box(0.9, 0.22, 0.04, [0.2, 0.88, -0.3, 0]),
                            "mallet": item("items/tools/mallet", [0.85, 0.88, -0.3, 0], solid=False),
                            "sawhorse": box(0.08, 0.08, 0.6, [[x, 0, 1.0, 0] for x in (-1.0, -0.2)]), "sawhorse top": box(1.0, 0.1, 0.1, [-0.6, 0.6, 1.0, 0]),
                            "plank": box(1.5, 0.25, 0.04, [-0.6, 0.7, 1.0, 0]),
                            "planks": box(0.28, 2.6, 0.05, [[-1.55 + k * 0.03, k * 0.05, -0.3, 0] for k in range(6)]),
                            "boards": box(0.04, 0.3, 2.0, [[1.55 - k * 0.05, 0, -1.3 + k * 0.2, 0] for k in range(4)]),
                            **rack("rack", 0, -1.62, 1.2), "saw": hang("items/tools/saw", -0.4, 1.6, -1.58, 0.72), "saw 2": hang("items/tools/saw", -0.15, 1.6, -1.58, 0.72),
                            "hammer": hang("items/tools/hammer", 0.15, 1.6, -1.58, 0.37), "mallet 2": hang("items/tools/mallet", 0.42, 1.6, -1.58, 0.35),
                            "shavings": box(0.6, 0.5, 0.02, [[0.4, 0, 0.35, 0.4], [-0.5, 0, 0.45, 1.1]])},
                           (0, 0, 0.55, 1.5707963, "saw", "saw", "stand"))
    F["cooper"] = trade("Cooper", "casks finished at the back, one in the making -- its staves raised in a ring, a hoop round their foot -- the block, staves stacked, hoops on the wall, the tools",
                        {"casks": comp("furniture/barrels", [0, 0, -1.3, 0], {"n": 3}), "block": col(0.35, 0.7, [-0.2, 0, 0.1, 0], sides=12),
                         "staves": {"type": "ring", "count": 16, "rOuter": 0.32, "rInner": 0.29, "height": 0.82, "y": 0, "solid": True, "at": [b for b in range(16) if b not in (3, 9)], "place": [[0.9, 0, 0.35, 0]]},   # (two staves still to go in)
                         "raising hoop iron": {"type": "ring", "count": 16, "rOuter": 0.34, "rInner": 0.31, "height": 0.05, "y": 0.1, "solid": True, "place": [[0.9, 0, 0.35, 0]]},
                         "stave stack": box(0.1, 0.85, 0.03, [[-1.5, k * 0.035, 0.5 + (k % 3) * 0.1, 0.1 * k] for k in range(8)]),
                         "hoops iron": {"type": "ring", "count": 16, "rOuter": 0.33, "rInner": 0.3, "height": 0.04, "y": 0, "solid": True, "place": [[-1.6, 1.0 + k * 0.08, -0.4, 0] for k in range(3)]},
                         "mallet": item("items/tools/mallet", [-0.3, 0.7, 0.05, 0], solid=False), "hammer": item("items/tools/hammer", [-0.05, 0.7, 0.15, 1.0], solid=False)},
                        (-0.2, 0, 0.85, 1.5707963, "hammer", "hammer", "stand"))
    F["butcher"] = trade("Butcher", "the counter at the front with its board and a joint on it, the chopping block behind, the meat rail with its hooks and the hams, sausages and flitches hanging from it",
                         {"counter": box(2.4, 0.7, 0.9, [0, 0, 0.9, 0]), "counter top": box(2.5, 0.8, 0.06, [0, 0.9, 0.9, 0]),
                          "block": col(0.4, 0.8, [0.3, 0, -0.4, 0], sides=12), "cleaver": item("items/tools/cleaver", [0.35, 0.8, -0.4, 0.5], solid=False),
                          "joint meat": box(0.35, 0.25, 0.14, [-0.5, 0.96, 0.95, 0.3]),
                          "rail iron": box(2.4, 0.06, 0.06, [0, 2.1, -1.4, 0]), "rail posts": box(0.06, 0.06, 2.16, [[-1.2, 0, -1.4, 0], [1.2, 0, -1.4, 0]]),
                          "hooks iron": box(0.015, 0.015, 0.12, [[-0.9 + k * 0.36, 1.98, -1.4, 0] for k in range(6)]),
                          "hams": item("items/food/ham", [[-0.9, 1.68, -1.4, 0], [-0.18, 1.68, -1.4, 0.5], [0.54, 1.68, -1.4, 1.0]], solid=False),
                          "flitch meat": box(0.3, 0.06, 0.5, [[-0.54, 1.48, -1.4, 0], [0.9, 1.48, -1.4, 0]]),
                          "sausages": item("items/food/sausages", [[0.18, 1.9, -1.4, 0]], solid=False),
                          "basket": item("items/tools/basket", [1.4, 0, 0.3, 0], solid=False)},
                         (0.3, 0, 0.3, -1.5707963, "chop", "cleaver", "stand"), customer=(0.3, 0, 1.75))
    F["tavern-room"] = {"name": "Tavern room", "_about": "the inn's ground floor: the bar with its keeper, the casks behind it and a shelf of jugs and mugs, two tables of benches (the fire is the house's own hearth, by its chimney)",
                        "params": {"detail": 4},
                        "parts": {"bar": box(2.6, 0.6, 1.0, [0, 0, -1.8, 0]), "bar top": box(2.7, 0.7, 0.06, [0, 1.0, -1.8, 0]),
                                  "casks": comp("furniture/barrels", [0, 0, -2.6, 0], {"n": 3}),
                                  "mugs": item("items/tableware/mug", [[-0.8 + k * 0.4, 1.06, -1.75, 0] for k in range(4)], solid=False),
                                  "jugs": item("items/tableware/jug", [[0.9, 1.06, -1.85, 0]], solid=False),
                                  "keeper": marker("spot", [0, 0, -2.25, 0], work=1, gesture="sell", face=-1.5707963, pose="stand"),
                                  "tables": comp("furniture/table", [[-1.4, 0, 0.8, 0], [1.6, 0, 0.8, 0]])},
                        "build": ["bar", "bar top", "casks", "mugs", "jugs", "keeper", "tables"]}
    F["pew"] = {"name": "Pew", "_about": "a church bench facing +x (the altar): a settle (items/furniture/settle) with a pew's low back, three places on it",
                "params": {"detail": 4, "L": 3.0},
                "parts": {"pew": item("items/furniture/settle", [0, 0, 0, PI2], {"L": "L", "backH": 0.95}, markers=["seat"]),
                          "places": marker("spot", [[0, 0.5, "0 - L / 3", 0], [0, 0.5, 0, 0], [0, 0.5, "L / 3", 0]], pose="sit", face=0)},
                "build": ["pew", "places"]}
    F["altar"] = {"name": "Altar", "_about": "the altar on its step, the priest's place before it facing the nave (-x)",
                  "params": {"detail": 4},
                  "parts": {"step": box(2.4, 3.2, 0.2, [0, 0, 0, 0]), "altar": box(1.0, 2.0, 1.0, [0.4, 0.2, 0, 0]),
                            "candles": item("items/tools/candlestick", [[0.55, 1.2, -0.7, 0], [0.55, 1.2, 0.7, 0]], solid=False),
                            "priest": marker("spot", [-0.6, 0.2, 0, 0], work=1, gesture="bless", face=3.14159265, pose="stand")},
                  "build": ["step", "altar", "candles", "priest"]}
    for k, v in F.items():
        write("furniture/" + k, {"name": v["name"], **({"_about": v["_about"]} if "_about" in v else {}), "params": v["params"], "parts": v["parts"], "build": v["build"]})
    return list(F)


TRADES = ["smithy", "bakery", "pottery", "weaver", "tailor", "carpenter", "cooper", "butcher", "tavern-room"]


# ---- THE TOWN HOUSE -------------------------------------------------------------------------------------------------
# One layout for every kind: the street front at +z; a dog-leg STAIR up the -x side wall in two columns (col A, then
# col B beside it, one flight a storey, climbing -z then +z), each floor cut only over the flight that comes up
# through it; the DOOR on the +x side of the front, clear of the stair's foot; the BEDS upstairs on the +x side,
# heads to the back wall; a CELLAR (its own flight down in col B under the first floor's) when asked; a SHOP FRONT
# (a wide arch instead of door and window) with a trade's furniture in the front room when asked.
def house(kind):
    K = {"gable": dict(name="Gable house", about="the burgher's house of a German or Dutch town: narrow, deep, its GABLE to the street",
                       W=7, D=11, t=0.45, j=0, roof="gable", roofYaw=0, pitch=52, front=[0.3], upper=2, back=2, head={"profile": "flat"}),
         "eaves": dict(name="Eaves house", about="a broader house with its EAVES to the street -- a Traufhaus -- and three windows a storey",
                       W=10, D=9, t=0.45, j=0, roof="gable", roofYaw=1, pitch=45, front=[0.22, 0.45], upper=3, back=3, head={"profile": "flat"}),
         "jettied": dict(name="Jettied house", about="a timber-framed house whose upper storeys project over the street and the yard (the jetty)",
                         W=7, D=10, t=0.35, j=0.55, roof="gable", roofYaw=0, pitch=55, front=[0.3], upper=2, back=2, head={"profile": "flat"}),
         "stone": dict(name="Stone house", about="a merchant's stone house: thick walls, round-headed openings, a hipped roof",
                       W=8.5, D=9.5, t=0.65, j=0, roof="hip", roofYaw=0, pitch=40, front=[0.3], upper=2, back=2, head={"profile": "semicircular"})}[kind]
    params = {"detail": 4, "W": K["W"], "D": K["D"], "H": 2.9, "n": 2, "t": K["t"], "g": 0.15, "slab": 0.2, "j": K["j"],
              "pitch": K["pitch"], "over": 0.4, "sw": 1.15, "run": 0.26, "steps": "round(H / 0.19)", "stairL": "steps * run",
              "cellarH": 2.3, "csteps": "round((cellarH + g) / 0.19)", "cL": "csteps * run",
              "xl": "0 - W / 2 + t", "xr": "W / 2 - t", "zF": "D / 2 - t - 1.3",
              "winW": 0.95, "winSill": 0.85, "winTop": 2.15, "doorW": 1.1, "doorH": 2.2, "glazed": 1 if kind == "stone" else 0,
              "_glazed": "1: the windows are glass (a merchant's stone house); 0: wooden shutters, open by day (the game hangs them at the `window` markers) -- the openings are holes either way",
              "tanP": "sin(pitch * 0.0174533) / cos(pitch * 0.0174533)",
              "_W": "the frontage (x) and D the depth (z), outside the walls; H a storey floor to floor; n the storeys built (the roof sits on the n-th); j the jetty of the upper storeys, front and back",
              "_zF": "the foot of the first flight: 1.3m inside the front wall, the door's way in clear of it"}
    parts, build = {}, {}
    head = K["head"]

    def openings(n, sill, top, width, head, lo=0.0):
        # n windows evenly along a face of length "W" (a list's `at` is from the face's middle: on the front it is x)
        return [{"at": f"W * {i + 1} / {n + 1} - W / 2", "width": width, "sill": sill, "springing": top if head["profile"] == "flat" else f"{top} - {width} / 2", "head": head, "glass": False} for i in range(n)]

    # -- the walls, a storey at a time (storey 0 from the ground; the upper ones out by the jetty)
    for k in range(3):
        y0 = 0 if k == 0 else f"g + {k} * H"
        h = "g + H" if k == 0 else "H"
        dep = "D" if k == 0 else "D + 2 * j"
        if k == 0:
            door = {"at": "W / 2 - t - 0.95", "width": "doorW", "sill": 0, "springing": "doorH" if head["profile"] == "flat" else "doorH - doorW / 2", "head": head}
            wins = [{"at": f"W * {f} - W / 2", "width": "winW", "sill": "g + winSill", "springing": "g + winTop" if head["profile"] == "flat" else "g + winTop - winW / 2", "head": head, "glass": False} for f in K["front"]]
            faces = {"0": wins + [door], "2": openings(K["back"], "g + winSill", "g + winTop", "winW", head)}
        else:
            faces = {"0": openings(K["upper"], "winSill", "winTop", "winW", head), "2": openings(K["back"], "winSill", "winTop", "winW", head)}
        parts[f"walls {k}"] = {"type": "enclosure", "plan": {"rect": ["W", dep]}, "thickness": "t", "height": h, "openings": [], "faces": faces, "at": [[0, y0, 0, 0]]}
    # -- the WINDOWS' panes, a marker each (the game hangs shutters there, or glass where the house is `glazed`): their
    #    middles in the wall's middle line, the pane up to the opening's springing
    # (h the whole opening, sill to crown; an arched one's pane shaped to its head: `spring` and `head`, as a door's)
    winH = "winTop - winSill"
    wdata = {"w": "winW", "h": winH} if head["profile"] == "flat" else {"w": "winW", "h": winH, "spring": "winTop - winW / 2 - winSill", "head": head}
    ats = lambda n: [f"W * {i + 1} / {n + 1} - W / 2" for i in range(n)]
    for k in range(3):
        y = "g + winSill" if k == 0 else f"g + {k} * H + winSill"
        dep = "D" if k == 0 else "D + 2 * j"
        front = [f"W * {f} - W / 2" for f in K["front"]] if k == 0 else ats(K["upper"])
        if k == 0:
            parts["windows 0 front"] = {"type": "marker", "role": "window", "at": [[x, y, f"({dep}) / 2 - t / 2", 0] for x in front], "data": wdata}
            parts["windows 0 back"] = {"type": "marker", "role": "window", "at": [[f"0 - ({x})", y, f"0 - (({dep}) / 2 - t / 2)", 0] for x in ats(K["back"])], "data": wdata}
        else:
            parts[f"windows {k}"] = {"type": "marker", "role": "window", "data": wdata,
                                     "at": [[x, y, f"({dep}) / 2 - t / 2", 0] for x in front] + [[f"0 - ({x})", y, f"0 - (({dep}) / 2 - t / 2)", 0] for x in ats(K["back"])]}
    # the shop front: the ground storey with one wide arch (a trade's workshop open to the street) instead of door and window
    parts["walls 0 shop"] = {"type": "enclosure", "plan": {"rect": ["W", "D"]}, "thickness": "t", "height": "g + H", "openings": [],
                             "faces": {"0": [{"at": "0.9", "width": "W - 2.8", "sill": 0, "springing": 2.05, "head": {"profile": "segmental", "rise": 0.4}, "glass": False}],
                                       "2": openings(K["back"], "g + winSill", "g + winTop", "winW", head)}, "at": [[0, 0, 0, 0]]}

    # -- the floors: storey k's slab cut over flight k-1 (col A for an even flight, col B for an odd one); the ground
    #    floor whole, or cut over the cellar's flight in col B
    def slab_with_hole(name, y_top, colB, zh0, zh1, dep, under_walls=False):
        # (under_walls: the slab reaches under the walls to 2 cm of their outer face, as the whole ground floor does)
        ex = " + t - 0.02" if under_walls else ""
        zi0, zi1 = f"(0 - ({dep}) / 2 + t{(' - t + 0.02') if under_walls else ''})", f"(({dep}) / 2 - t{ex})"
        xo, xe = ("(xl - t + 0.02)", "(xr + t - 0.02)") if under_walls else ("xl", "xr")
        c0 = "(xl + sw)" if colB else xo
        c1 = "(xl + 2 * sw)" if colB else "(xl + sw)"
        y = f"{y_top} - slab"
        ps = {f"{name} beside": box(f"{xe} - {c1}", f"{zi1} - {zi0}", "slab", [f"({c1} + {xe}) / 2", y, f"({zi0} + {zi1}) / 2", 0]),
              f"{name} front": box(f"{c1} - {c0}", f"{zi1} - ({zh1})", "slab", [f"({c0} + {c1}) / 2", y, f"({zh1} + {zi1}) / 2", 0]),
              f"{name} back": box(f"{c1} - {c0}", f"({zh0}) - {zi0}", "slab", [f"({c0} + {c1}) / 2", y, f"({zi0} + {zh0}) / 2", 0])}
        if colB:
            ps[f"{name} col A"] = box(f"(xl + sw) - {xo}", f"{zi1} - {zi0}", "slab", [f"({xo} + xl + sw) / 2", y, f"({zi0} + {zi1}) / 2", 0])
        return ps
    # (the ground floor reaches under the walls to 2 cm of their outer face -- the slab with the cellar's hole too, below --
    #  so a doorway through the wall stands on floor, not over a gap down to the ground or the cellar)
    parts["floor 0"] = box("W - 0.04", "D - 0.04", "g", [0, 0, 0, 0])
    parts.update(slab_with_hole("floor 0 cellar", "g", False, "zF - stairL", "zF - stairL + cL", "D", under_walls=True))   # (col A, under flight 0: the cellar's flight runs beneath the stair, against the side wall)   # (open over the whole flight: the walker, testing a quarter metre ahead at its CURRENT height, must clear the slab's edge by 1.7 m -- a hole one tread shorter stopped it on the third step from the bottom)
    for k in (1, 2):
        even = (k - 1) % 2 == 0     # flight k-1: col A climbing -z (hole over its top end), or col B climbing +z
        # (the hole runs from the flight's top down as far as a walker's head would meet the slab: every tread less than
        #  1.7 m + the slab under the floor, three more for the quarter metre the walk tests ahead and its footprint on the tread above -- three treads in all left it shut)
        hole = "(ceil((1.7 + slab) / 0.19) + 3) * run"
        zh0, zh1 = ("zF - stairL", f"zF - stairL + {hole}") if even else (f"zF - {hole}", "zF")
        parts.update(slab_with_hole(f"floor {k}", f"g + {k} * H", not even, zh0, zh1, "D + 2 * j"))
    # -- the STRING COURSES (2026-10-24): a band of dressed stone round the house at each upper floor's line, standing
    #    a little proud of the wall (not on a jettied house: its jetty marks the storey)
    if not K["j"]:
        for k in (1, 2):
            parts[f"course {k}"] = {"type": "enclosure", "plan": {"rect": ["W + 0.12", "D + 0.12"]}, "thickness": 0.12, "height": 0.16, "openings": [],
                                    "at": [[0, f"g + {k} * H - 0.2", 0, 0]]}
    # -- the PLINTH (2026-10-24): a low wall of rough stone round the foot, 4 cm proud -- what a framed or plastered house
    #    stands on (the stone house is stone already); cut for the door, or the shop's arch
    plinth_door = {"at": "W / 2 - t - 0.95", "width": "doorW", "sill": 0, "springing": 0.55, "head": {"profile": "flat"}}
    plinth_arch = {"at": "0.9", "width": "W - 2.8", "sill": 0, "springing": 0.55, "head": {"profile": "flat"}}
    for nm, op in (("plinth", plinth_door), ("plinth shop", plinth_arch)):
        parts[nm] = {"type": "enclosure", "plan": {"rect": ["W + 0.08", "D + 0.08"]}, "thickness": 0.1, "height": 0.55, "openings": [], "faces": {"0": [op]}, "at": [[0, 0, 0, 0]]}
    # -- the JETTY's joist ends (2026-10-24): under a jettied storey's overhang, front and back, the floor's joists show
    #    as a row of beam ends carrying it, every half metre
    if K["j"]:
        for k in (1, 2):
            y = f"g + {k} * H - 0.09"
            parts[f"jetty {k}"] = box(0.13, "j + 0.1", 0.17, [[ "0 - W / 2 + 0.3", y, f"{sz} * (D / 2 + j / 2 - 0.05)", 0] for sz in (-1, 1)],
                                     repeat={"count": "floor((W - 0.6) / 0.5) + 1", "step": [0.5, 0, 0, 0]})
    # -- QUOINS (2026-10-24): dressed stones up each corner, long and short in turn (a long face on the front, then on
    #    the side), standing 2 cm proud of both faces -- the town builds them on a plastered or stone house, not a framed one
    if not K["j"]:
        n_q = "floor((g + n * H) / 0.64)"
        for nm, (w, l, y0) in {"quoins": ("0.56", "0.3", "0.16"), "quoins b": ("0.3", "0.56", "0.48")}.items():
            parts[nm] = box(w, l, 0.28, [[f"{sx} * (W / 2 + 0.02 - ({w}) / 2)", y0, f"{sz} * (D / 2 + 0.02 - ({l}) / 2)", 0] for sx in (-1, 1) for sz in (-1, 1)],
                            repeat={"count": n_q, "step": [0, 0.64, 0, 0]})
    # -- the JOISTS under the upper floors (2026-10-24): a beam across the house every 0.75 m, the ceiling's timbers seen
    #    from the room below -- only beside the stair's two columns (clear of the flights' headroom); they span the house's
    #    width, within its walls
    for k in (1, 2):
        dep = "D + 2 * j"
        parts[f"joists {k}"] = box("xr - (xl + 2 * sw)", 0.14, 0.16, [f"(xl + 2 * sw + xr) / 2", f"g + {k} * H - slab - 0.16", f"0 - ({dep}) / 2 + t + 0.35", 0],
                                   repeat={"count": f"floor((({dep}) - 2 * t - 0.7) / 0.75) + 1", "step": [0, 0, 0.75, 0]})
    # -- the flights: from storey k to k+1, arriving on the floor (landing 0)
    for k in (0, 1):
        if k % 2 == 0:
            at = ["xl + sw", f"g + {k} * H", "zF", PI2]
        else:
            at = ["xl + sw", f"g + {k} * H", "zF - stairL", "0 - " + PI2]
        # (an OPEN stair, a timber one on its strings: a soffit under its nosings and the room beneath it free -- over
        #  a cellar, the cellar's flight runs under the first, at the same slope: a storey's headroom all the way)
        parts[f"flight {k}"] = {"type": "flight", "run": "run", "rise": 0.19, "width": "sw", "base": 0, "top": "H", "landing": 0, "soffit": 0.2, "at": [at]}
    # -- the way up, for whoever sleeps upstairs: the foot, the top of each flight (and round to the next)
    parts["way 1"] = marker("way", [["xl + sw / 2", "g", "zF + 0.45", 0], ["xl + sw / 2", "g + H", "zF - stairL - 0.45", 0]], order=0, storey=0)
    parts["way 1"]["at"] = [["xl + sw / 2", "g", "zF + 0.45", 0]]
    parts["way 1 top"] = marker("way", ["xl + sw / 2", "g + H", "zF - stairL - 0.45", 0], order=1, storey=1)
    parts["way 2"] = marker("way", ["xl + 1.5 * sw", "g + H", "zF - stairL - 0.45", 0], order=2, storey=1)
    parts["way 2 top"] = marker("way", ["xl + 1.5 * sw", "g + 2 * H", "zF + 0.45", 0], order=3, storey=2)
    # -- the roof on the n-th storey (its ridge along z: the gable to the street; turned: the eaves), the chimney
    rl = ["W", "D + 2 * j"] if not K["roofYaw"] else ["D + 2 * j", "W"]
    parts["roof"] = {"type": "roof", "form": K["roof"], "width": rl[0], "length": rl[1], "pitch": "pitch", "overhang": "over",
                     "at": [[0, "g + n * H", 0, PI2 if K["roofYaw"] else 0]]}
    # (the chimney against the back wall on the +x side, clear of the roof by 0.8m wherever it comes through)
    if not K["roofYaw"]:
        rise = "(W / 2 - (W / 2 - t - 0.45) + 0.5) * tanP"
    else:
        rise = "((D + 2 * j) / 2 - (D / 2 - t - 0.4) + 0.5) * tanP"
    parts["chimney"] = box(0.75, 0.75, f"g + n * H + {rise} + 0.8", ["W / 2 - t - 0.45", 0, "0 - D / 2 + t + 0.4", 0])
    parts["hearth"] = comp("furniture/hearth", ["W / 2 - t - 0.45 - 1.2", "g", "0 - D / 2 + t + 0.4", 0])
    parts["table"] = comp("furniture/table", ["(xl + 2 * sw + xr) / 2", "g", "0 - D / 2 + t + 2.6", 0], {"L": "min(1.8, xr - xl - 2 * sw - 1.2)", "look": "round(W * 10 + D)"})
    # -- beds upstairs, one a storey on the +x side, head to the back wall
    for k in (1, 2):
        parts[f"bed {k}"] = comp("furniture/bed", ["xr - 0.85", f"g + {k} * H", "0 - (D + 2 * j) / 2 + t + 1.12", 0], {"storey": k, "look": f"round(W * 10 + D + {k})"})
    # -- the door: its panel in the doorway (the game's), and where the villagers go in and out
    # (the panel as wide as the opening, to its springing, under its head -- the same numbers as the opening's)
    parts["door"] = marker("door", ["W / 2 - t - 0.95", "g", "D / 2 - t / 2", 0], w="doorW", h="doorH - g",
                           spring="doorH - g" if head["profile"] == "flat" else "doorH - doorW / 2 - g", head=head)
    parts["door shop"] = marker("door", ["0.9", "g", "D / 2 - t / 2", 0], w=1.0, h=2.0, panel=0)
    # -- the cellar: walls under the ground storey, its floor, its flight up in col B, a row of casks
    parts["cellar walls"] = {"type": "enclosure", "plan": {"rect": ["W", "D"]}, "thickness": "t", "height": "cellarH + slab", "openings": [], "at": [[0, "0 - cellarH - slab", 0, 0]]}
    parts["cellar floor"] = box("W - 2 * t", "D - 2 * t", "slab", [0, "0 - cellarH - slab", 0, 0])
    # (the cellar flight in col A against the side wall, UNDER the first flight -- a flight's width lies on its left: yaw
    #  +pi/2 at xl + sw spans col A -- rising toward -z to the floor at the first flight's top end, where the way down is
    #  entered from behind the stair; a rail along its open side on the ground floor, as far as there is room under the stair)
    parts["cellar flight"] = {"type": "flight", "run": "run", "rise": 0.19, "width": "sw", "base": 0, "top": "cellarH + g", "landing": 0,
                              "at": [["xl + sw", "0 - cellarH", "zF - stairL + cL", PI2]]}
    rz0, rz1 = "zF - stairL + 0.05", "zF - 1.65"
    parts["cellar rail posts"] = box(0.06, 0.06, 0.95, [[f"xl + sw + 0.05", "g", f"{rz0} + ({rz1} - ({rz0})) * {i} / 5", 0] for i in range(6)])
    parts["cellar rail"] = box(0.06, f"{rz1} - ({rz0}) + 0.06", 0.06, ["xl + sw + 0.05", "g + 0.9", f"({rz0} + {rz1}) / 2", 0])
    # the cellar furnished: casks along the back wall and the +x wall, a chest and a stool by the stair's foot
    parts["cellar casks"] = comp("furniture/barrels", ["(xl + 2 * sw + xr) / 2", "0 - cellarH", "0 - D / 2 + t + 0.6", 0], {"n": 3, "look": "round(W * 10 + D)"})
    parts["cellar casks east"] = comp("furniture/barrels", ["xr - 0.6", "0 - cellarH", "0 - D / 2 + t + 3.0", PI2], {"n": 2, "look": "round(W * 10 + D + 7)"})
    parts["cellar chest"] = {"type": "item", "item": "items/furniture/plank-chest", "seed": "round(W + D)", "at": [["xl + 2 * sw + 1.2", "0 - cellarH", "zF + 0.6", 0]]}
    parts["cellar stool"] = {"type": "item", "item": "items/furniture/stool", "seed": "round(W + D)", "at": [["xl + 2 * sw + 2.4", "0 - cellarH", "zF + 0.2", 0]]}
    # -- the trades, in the front room (between the stair and the +x wall, the counter side to the street)
    for tr in TRADES:
        parts[f"trade {tr}"] = comp(f"furniture/{tr}", ["(xl + 2 * sw + xr) / 2 + 0.2", "g", "D / 2 - t - 2.1", 0])
        # ...and its SIGN over the street, on its bracket by the +x corner, just under the first floor
        parts[f"sign {tr}"] = item("items/components/trade-sign", ["W / 2 - 0.45", "g + H - 0.3", "D / 2", 0], {"kind": "tavern" if tr == "tavern-room" else tr}, solid=False)
    doc = {"name": K["name"], "_about": K["about"] + ". " + LAYOUT_ABOUT, "params": params,
           "_build": "the village plan builds: walls 0 (or walls 0 shop), walls 1..n-1 and their windows k, floor 0 (or floor 0 cellar + the cellar, and flight 0 open for flight 0), floor k + flight k-1 + way k for every upper storey, roof, chimney, beds, door (or door shop), a trade, hearth, table",
           "build": ["walls 0", "walls 1", "windows 0 front", "windows 0 back", "windows 1", "floor 0", "floor 1 beside", "floor 1 front", "floor 1 back", "joists 1", "flight 0", "way 1", "way 1 top",
                     "roof", "chimney", "hearth", "table", "bed 1", "door"],
           "walked": True, "parts": parts}
    write("village/" + kind + "-house", doc)


LAYOUT_ABOUT = ("The street front is +z. A dog-leg stair climbs the -x side wall in two columns, one flight a storey, and each "
                "floor is cut only over the flight that comes up through it; the door is on the +x side of the front; the beds are "
                "upstairs against the back wall; a cellar is dug under the whole house with its own flight in the second column; "
                "a shop front replaces door and window with one wide arch and a trade's furniture fills the front room.")


# ---- THE LONGHOUSE: a farmstead under one long low roof -- people at the +x end round the open hearth, beasts at the
# -x end beyond a partition; doors in the middle of both long sides and a wide byre door; box beds along the back wall
def longhouse():
    params = {"detail": 4, "L": 18, "B": 7, "t": 0.4, "eaveH": 3.0, "g": 0.15, "slab": 0.2, "pitch": 50, "over": 0.7, "xP": "0 - L / 6", "pz": "B / 2 - t - 1.4",
              "sw": 1.15, "run": 0.26, "steps": "round((eaveH - g) / 0.19)", "stairL": "steps * run", "xs": "xP + 1.0", "zs": "sw / 2",
              "_L": "the length (x) and B the breadth (z) outside the walls; eaveH the walls, the loft floor's top; xP the partition between the living end (+x) and the byre (-x)",
              "_xs": "the stair to the loft: its foot xs (a metre of floor before it by the partition), down the middle of the house (zs its +z side) under the ridge, climbing +x to where the roof is highest"}
    seg = {"profile": "segmental", "rise": 0.3}
    doors = {"door": ("L / 5", "0", 1.2), "back door": ("L / 5", "2", 1.1)}   # (x, face, width): the openings and their panels from one list
    faces = {"0": [{"at": "L / 5 + 2.6", "width": 0.7, "sill": 1.0, "springing": 1.7, "head": {"profile": "flat"}, "glass": False},
                   {"at": "L / 5 - 2.6", "width": 0.7, "sill": 1.0, "springing": 1.7, "head": {"profile": "flat"}, "glass": False}],
             "1": [{"at": 0, "width": 0.6, "sill": 1.0, "springing": 1.6, "head": {"profile": "flat"}, "glass": False}],
             "2": [{"at": "L / 3", "width": 2.2, "sill": 0, "springing": 2.2, "head": seg, "glass": False}],
             "3": [{"at": 0, "width": 0.6, "sill": 1.0, "springing": 1.6, "head": {"profile": "flat"}, "glass": False}]}
    for name, (at, face, w) in doors.items():
        faces[face].append({"at": at if face == "0" else f"0 - ({at})", "width": w, "sill": 0, "springing": 2.0, "head": seg})
    zi0, zi1, xi0, xi1 = "(0 - B / 2 + t)", "(B / 2 - t)", "(0 - L / 2 + t)", "(L / 2 - t)"
    # the bays of the frame: a pair of aisle posts every ~3 m, clear of the cross passage (the doors at L/5), the partition
    # and the hearth (L/4: its posts stand either side of it)
    POSTS = ["0 - L / 2 + t + 2.2", "0 - L / 2 + t + 5.2", "xP + 2.0", "L / 4 + 1.6", "L / 2 - t - 0.4"]   # (the last past the beds)
    parts = {
        "walls": {"type": "enclosure", "plan": {"rect": ["L", "B"]}, "thickness": "t", "height": "eaveH", "openings": [], "faces": faces, "at": [[0, 0, 0, 0]]},
        "floor": box("L - 0.04", "B - 0.04", "g", [0, 0, 0, 0]),
        "partition": {"type": "wall", "width": "B - 2 * t", "height": "eaveH - 0.24 - g", "thickness": 0.2,
                      "openings": [{"at": "(B - 2 * t) / 2 + 0.6", "width": 1.0, "sill": 0, "springing": 1.9, "head": {"profile": "flat"}}], "at": [["xP + 0.1", "g", 0, PI2]]},
        # NO LOFT: the roof open to the rafters over the whole house (2026-10-03, user) -- its FRAME seen: two rows of aisle
        # posts carrying a purlin each, tie beams across at the eaves on every pair of posts, the wall plates along the
        # wall heads; the smoke of the open hearth goes up through it and out under the thatch
        "aisle posts": box(0.22, 0.22, "eaveH + 0.6 - g", [[x, "g", z, 0] for x in POSTS for z in ("0 - pz", "pz")]),
        "purlins": box("L - 2 * t", 0.2, 0.22, [[0, "eaveH + 0.6", "0 - pz", 0], [0, "eaveH + 0.6", "pz", 0]]),
        "tie beams": box(0.2, "B - 2 * t", 0.24, [[x, "eaveH - 0.24", 0, 0] for x in POSTS]),
        "wall plates": box("L - 2 * t", 0.24, 0.16, [[0, "eaveH - 0.16", "0 - (B / 2 - t - 0.12)", 0], [0, "eaveH - 0.16", "B / 2 - t - 0.12", 0]]),
        "king posts": box(0.16, 0.16, 1.2, [[x, "eaveH", 0, 0] for x in POSTS]),
        "roof": {"type": "roof", "form": "jerkinhead", "width": "B", "length": "L", "pitch": "pitch", "clip": 0.3, "overhang": "over", "shell": 0.3,
                 "at": [[0, "eaveH", 0, PI2]]},
        # the OPEN HEARTH in the middle of the living end: a kerb of stones round a bed of ash on the floor, no chimney
        "hearth": {"type": "ring", "count": 8, "rOuter": 0.8, "rInner": 0.6, "height": 0.18, "y": "g", "solid": True, "place": [["L / 4", 0, 0, 0]]},
        "ash bed": {"type": "column", "radius": 0.6, "height": 0.04, "sides": 8, "at": [["L / 4", "g", 0, 0]]},
        "fire": marker("fire", ["L / 4", "g + 0.05", 0, 0], r=0.3, h=0.55),
        "beds": comp("furniture/bed", ["L / 2 - t - 1.6", "g", "0 - B / 2 + t + 1.1", 0], {"look": 2}),
        "beds 2": comp("furniture/bed", ["L / 2 - t - 3.4", "g", "0 - B / 2 + t + 1.1", 0], {"look": 3}),
        "table": comp("furniture/table", ["L / 4 + 0.3", "g", "B / 2 - t - 1.3", 0], {"L": 1.6}),
        "chest": comp("furniture/chest", ["L / 2 - t - 0.5", "g", "B / 2 - t - 0.5", PI2]),
        "stalls": box(0.15, 1.8, 1.2, [["0 - L / 2 + t + 2.4", "g", "0 - B / 2 + t + 0.9", 0], ["0 - L / 2 + t + 4.4", "g", "0 - B / 2 + t + 0.9", 0]]),
        "hay": box(2.0, 1.2, 1.1, ["0 - L / 2 + t + 1.3", "g", "B / 2 - t - 0.8", 0]),
    }
    for name, (at, face, w) in doors.items():   # the door panels: as wide as the opening, to its springing, under its head
        z = "B / 2 - t / 2" if face == "0" else "0 - B / 2 + t / 2"
        parts[name] = marker("door", [at, "g", z, 0], w=w, h="2.0 + 0.3 - g", spring="2.0 - g", head=seg)
    # the windows' shutters (the game's, at these markers): two in the front, one in each gable end
    parts["windows"] = {"type": "marker", "role": "window", "at": [["L / 5 + 2.6", 1.0, "B / 2 - t / 2", 0], ["L / 5 - 2.6", 1.0, "B / 2 - t / 2", 0]], "data": {"w": 0.7, "h": 0.7}}
    parts["windows ends"] = {"type": "marker", "role": "window", "at": [["L / 2 - t / 2", 1.0, 0, "0 - " + PI2], ["0 - (L / 2 - t / 2)", 1.0, 0, "0 - " + PI2]], "data": {"w": 0.6, "h": 0.6}}
    write("village/longhouse", {"name": "Longhouse", "_about": "A LONGHOUSE: the farmstead of the open country -- one long building under a steep half-hipped roof (thatched, as the finish says), people at the +x end round the open hearth, the beasts beyond a partition at the -x end, the roof open to its frame -- aisle posts, purlins, tie beams -- over it all, the open hearth in the middle of the living end (no chimney: the smoke goes out under the thatch); doors in the middle of both long sides, beds against the back wall.",
                                "params": params, "parts": parts, "build": list(parts), "walked": True})


# ---- THE TOWN WALL: straight walls whose top is the WALK, and towers astride their outer face -----------------------
# A segment runs along x, the field outside at +z and the town at -z: a thick wall whose top is the wall-walk, a
# crenellated parapet on the field side, a low one on the town side -- both stopping `pc` short of each end, where a
# tower stands astride the wall -- and, when asked, a flight up from the town side, the low parapet open where it lands.
def wall_segment():
    params = {"detail": 4, "len": 30, "h": 6.0, "T": 2.4, "fp": 0.5, "ri": 0.15, "pa": 2.8, "pb": 2.8, "ia": 2.8, "ib": 2.8, "ka": 1, "kb": 1, "sx": -6.0, "run": 0.28, "Lf": "round(h / 0.19) * run",
              "_fp": "the field parapet's thickness (its inner face is the walk's field edge) and ri how far in from the town face the town-side rail stands: the walk's middle is (fp - ri) / 2 in from the wall's line toward the town (town.js frame.walkIn: the watchman and the sentry walk it)",
              "_len": "the segment's length (centre of one tower to the next, or to a gatehouse's face), h its walk's height, T its thickness; sx where the flight up starts (it climbs +x along the town face to a 1.3m landing: sx + Lf + 1.3 must stay short of the +x end)",
              "_pa": "where the field parapet stops short of the -x end (pa) and the +x end (pb): 2.8 at a tower astride the wall, where a flanking tower meets it (town.js flankStop; ia 0 there: the town side runs on), 0.7 at a corner tower (it runs into the tower), 0 at a gatehouse's face; ia/ib the same for the town-side parapet (T/2 - 0.15 at a corner: it runs to the corner, where it meets the other wall's), ka/kb 0 where its end post is the other wall's (one post at the corner, not two side by side)"}
    parts = {
        "body": box("len", "T", "h", [0, 0, 0, 0]),
        "parapet": comp("components/crenellation", ["(pa - pb) / 2", "h", "T / 2 - fp / 2", 0], {"L": "len - pa - pb", "t": "fp", "h": 1.0, "step": 1.8, "mh": 0.75}, build=["parapet", "merlons"]),
        # the town side of the walk: a TIMBER balustrade (components/fence, post-and-rail), not a stone parapet
        "inner parapet": comp("components/fence", ["0 - len / 2 + ia", "h", "0 - T / 2 + ri", 0], {"L": "len - ia - ib", "style": "rails", "bay": 1.8, "h": 1.0, "p0": "ka", "p1": "kb"}),
        # (the flight arrives on a landing of its own beside the walk, 1.3m long, and the walker steps off it through a
        #  gap in the balustrade -- stepped off the flight's side, its railing, rising where the wall's top falls below
        #  knee height, was in the way)
        "inner parapet by the stair": comp("components/fence", ["0 - len / 2 + ia", "h", "0 - T / 2 + ri", 0], {"L": "sx + Lf - 0.1 - (0 - len / 2 + ia)", "style": "rails", "bay": 1.8, "h": 1.0, "p0": "ka"}),
        "inner parapet past the stair": comp("components/fence", ["sx + Lf + 1.4", "h", "0 - T / 2 + ri", 0], {"L": "len / 2 - ib - (sx + Lf + 1.4)", "style": "rails", "bay": 1.8, "h": 1.0, "p1": "kb"}),
        "stair": {"type": "flight", "run": "run", "rise": 0.19, "width": 1.3, "base": 0, "top": "h", "landing": 1.3, "at": [["sx", 0, "0 - T / 2", 0]]},
    }
    write("village/wall", {"name": "Town wall", "_about": "A STRETCH OF TOWN WALL: its top is the wall-walk, behind a crenellated parapet on the field side (+z) and a low one on the town side; the parapets stop short of a tower astride the wall (the river ends), the field one runs into a tower flanking it (between: town.js) and the town-side one runs on behind it, run into a corner tower, and meet a gatehouse's face (pa/pb, ia/ib); built with `stair` (and the town-side parapet in two, `inner parapet by the stair` and `past the stair`) it has a flight up from the town.",
                           "params": params, "parts": parts, "build": ["body", "parapet", "inner parapet"], "walked": True})


# A ROUND TOWER astride the wall: its centre `zt` out from the wall's line, a solid base up to the walk, and above it a
# round stage with a door at the walk (bay 6, facing the town and the walk that passes behind it), a spiral from that
# door up to the platform at `top`; the top by the town's style: open behind merlons, or a room under a roof.
# The spiral stands free in the middle of the stage (`sr`, round a slender newel) and comes up through a WELL in the
# platform, which is a whole floor round it -- the walk behind the parapet, the well railed where it drops. (It had
# filled the stage wall to wall: the platform could only be the few bays not over its last turn, a ledge by a hole.)
def wall_tower():
    params = {"detail": 4, "R": 3.4, "wall": 0.8, "h": 6.0, "top": 10.6, "n": 12, "turn": 24, "rise": 0.19,
              "steps": "round((top - h) / rise)", "slab": 0.3, "roomH": 2.6, "zt": 0, "capRise": 5.0, "sr": 1.3,
              "_zt": "the tower's centre out from its placement (+z: the field) -- the village plan sets it so the tower stands astride the wall's outer face (at the corners and river ends), or flanks the wall between, its back on the walk's field edge (town.js FLANK)",
              "_h": "the walk's height (the wall's); top the platform the spiral arrives on"}
    parts = {
        "base": col("R", "h", [0, 0, "zt", 0], sides=12),
        "stage": {"type": "ring", "count": "n", "rOuter": "R", "rInner": "R - wall", "height": "top - h + 1.1", "y": "h", "place": [[0, 0, "zt", 0]],
                  "skip": [6], "opening": {"width": 0.4, "sill": 1.2, "springing": 2.0, "head": {"profile": "semicircular"}, "glass": False}},
        "walk door": {"type": "ring", "count": "n", "rOuter": "R", "rInner": "R - wall", "height": "top - h + 1.1", "y": "h", "place": [[0, 0, "zt", 0]],
                      "at": [6], "opening": {"width": 1.1, "sill": 0, "springing": 1.9, "head": {"profile": "semicircular"}}},
        "stair": {"type": "spiral-stair", "radius": "sr", "newel": 0.15, "turn": "turn", "top": "top - h", "steps": "steps", "soffit": 0.2,
                  "at": [[0, "h", "zt", "6 * 6.2831853 / n"]]},
        # the platform: a whole floor, its rim buried in the wall's thickness, with the well the spiral comes up through
        "platform": {"type": "prism", "plan": {"sides": "2 * n", "radius": "R - wall / 2", "well": {"radius": "sr + 0.08"}}, "height": "slab",
                     "at": [[0, "top - slab", "zt", 0]]},
        "merlons": {"type": "ring", "count": 16, "rOuter": "R", "rInner": "R - wall", "height": 0.9, "y": "top + 1.1", "place": [[0, 0, "zt", 0]],
                    "at": [0, 2, 4, 6, 8, 10, 12, 14], "solid": True},
        "room": {"type": "ring", "count": "n", "rOuter": "R", "rInner": "R - wall", "height": "roomH", "y": "top + 1.1", "place": [[0, 0, "zt", 0]],
                 "opening": {"width": 0.5, "sill": 0.9, "springing": 1.7, "head": {"profile": "semicircular"}, "glass": False}},
        "cone": {"type": "dome", "sides": 12, "radius": "R + 0.35", "thickness": 0, "head": {"profile": "trigonal", "rise": "capRise"}, "at": [[0, "top + 1.1 + roomH", "zt", 0]]},
        "bell": {"type": "dome", "sides": 12, "radius": "R + 0.35", "thickness": 0, "head": {"profile": "ogee", "neck": 0.9}, "at": [[0, "top + 1.1 + roomH", "zt", 0]]},
        "tent": {"type": "roof", "form": "pyramid", "width": "2 * R + 0.6", "length": "2 * R + 0.6", "pitch": 58, "at": [[0, "top + 1.1 + roomH", "zt", 0]]},
    }
    write("village/wall-tower", {"name": "Wall tower", "_about": "A ROUND WALL TOWER astride the town wall: solid up to the wall-walk, then a round stage entered from the walk that passes behind it (bay 6), a spiral up to a platform; its top the town's style -- merlons (open), or a room under a cone, an ogee bell or a pyramid.",
                                 "params": params, "parts": parts, "build": ["base", "stage", "walk door", "stair", "platform", "merlons"], "walked": True})


# A GATEHOUSE: a square tower over the gate passage, the walk passing through its upper storey (doors in its side faces)
def gatehouse():
    params = {"detail": 4, "W": 7.6, "D": 8.4, "t": 0.9, "h": 6.0, "upH": 3.4, "gateW": 3.6, "gateS": 3.0, "slab": 0.35, "pitch": 52,
              "_W": "along the wall (x), D across it (z, the field at +z); h the walk's height, upH the upper storey's"}
    arch = {"profile": "semicircular"}
    parts = {
        "walls": {"type": "enclosure", "plan": {"rect": ["W", "D"]}, "thickness": "t", "height": "h + upH",
                  "faces": {"0": [{"h": "h", "openings": [{"at": 0, "width": "gateW", "sill": 0, "springing": "gateS", "head": arch, "glass": False}]},
                                  {"openings": [{"at": -1.5, "width": 0.3, "sill": 0.8, "springing": 2.0, "head": {"profile": "flat"}, "glass": False},
                                                {"at": 1.5, "width": 0.3, "sill": 0.8, "springing": 2.0, "head": {"profile": "flat"}, "glass": False}]}],
                            "2": [{"h": "h", "openings": [{"at": 0, "width": "gateW", "sill": 0, "springing": "gateS", "head": arch, "glass": False}]},
                                  {"openings": [{"at": 0, "width": 0.9, "sill": 0.9, "springing": 2.0, "head": arch, "glass": False}]}],
                            "1": [{"h": "h", "openings": []}, {"openings": [{"at": 0, "width": 1.4, "sill": 0, "springing": 2.2, "head": arch, "glass": False}]}],
                            "3": [{"h": "h", "openings": []}, {"openings": [{"at": 0, "width": 1.4, "sill": 0, "springing": 2.2, "head": arch, "glass": False}]}]},
                  "at": [[0, 0, 0, 0]]},
        "upper floor": box("W - 2 * t", "D - 2 * t", "slab", [0, "h - slab", 0, 0]),
        "passage": box("W - 2 * t", "D - 2 * t", 0.12, [0, 0, 0, 0]),
        "roof": {"type": "roof", "form": "hip", "width": "W", "length": "D", "pitch": "pitch", "overhang": 0.35, "at": [[0, "h + upH", 0, 0]]},
        "flat roof": box("W", "D", 0.3, [0, "h + upH", 0, 0]),
        "battlements": comp("components/crenellation", [[0, "h + upH + 0.3", "D / 2 - 0.25", 0], [0, "h + upH + 0.3", "0 - D / 2 + 0.25", 0]],
                            {"L": "W", "t": 0.5, "h": 0.9, "step": 1.8, "mh": 0.7}, build=["parapet", "merlons"]),
        "battlements x": comp("components/crenellation", [["W / 2 - 0.25", "h + upH + 0.3", 0, PI2], ["0 - W / 2 + 0.25", "h + upH + 0.3", 0, PI2]],
                              {"L": "D - 1.0", "t": 0.5, "h": 0.9, "step": 1.8, "mh": 0.7}, build=["parapet", "merlons"]),
        "guards": marker("guard", [["0 - gateW / 2 - 0.9", 0, "D / 2 + 1.4", 0], ["gateW / 2 + 0.9", 0, "D / 2 + 1.4", 0]], face="0 - 1.5707963"),
    }
    write("village/gatehouse", {"name": "Gatehouse", "_about": "A GATEHOUSE: a square tower over the gate passage (through its field face +z and its town face -z), the wall-walk passing through its upper storey by doors in its side faces; roofed (hip) or battlemented as the town's style says; guards' places outside the gate.",
                                "params": params, "parts": parts, "build": ["walls", "upper floor", "passage", "roof"], "walked": True})


# ---- THE VILLAGE CHURCH: a nave, a lower chancel to the east (+x), a square WEST TOWER with a stair to its belfry; the
# tower's top by the town's style: a spire, a pyramid, a saddleback, an onion, battlements
def church():
    params = {"detail": 4, "L": 17, "B": 9, "t": 0.7, "hN": 6.8, "g": 0.2, "chL": 6.5, "chB": 6.6, "chH": 5.6, "S": 7.2, "tH": 17, "dz": 1.8,
              "belH": 3.4, "pitch": 50, "rows": 5, "tR": 1.8, "tn": 6,
              "_tR": "the stair turret's radius and bays (tn): a spiral a walker fits in wants 1.8m -- the tower is sized round it, and the way through its foot (dz off its middle) passes clear of it",
              "_L": "the nave, L long (x) and B broad; hN its walls; chL/chB/chH the chancel east of it; S the tower's square, tH its shaft (the belfry its last belH); dz the way through the tower's foot, off its middle clear of the stair turret"}
    rnd = {"profile": "semicircular"}
    tx = "0 - L / 2 - S / 2 + t"
    parts = {
        "nave": {"type": "enclosure", "plan": {"rect": ["L", "B"]}, "thickness": "t", "height": "hN", "openings": [],
                 "faces": {"0": {"pattern": "3", "width": 1.1, "gap": "L / 4 - 1.1", "pier": 0, "sill": 2.4, "springing": "hN - 1.4", "head": rnd},
                           "2": {"pattern": "3", "width": 1.1, "gap": "L / 4 - 1.1", "pier": 0, "sill": 2.4, "springing": "hN - 1.4", "head": rnd},
                           "1": [{"at": 0, "width": "chB - 2 * t - 0.6", "sill": 0, "springing": "chH - 1.9", "head": rnd, "glass": False}],
                           # (the west face: none where the tower stands -- its east wall is the wall there, door and all; a
                           #  nave wall in the same place flickered against it)
                           "3": [{"at": 0, "width": "S", "sill": 0, "springing": "hN", "head": {"profile": "flat"}, "glass": False}]}, "at": [[0, 0, 0, 0]]},
        "nave floor": box("L - 0.04", "B - 0.04", "g", [0, 0, 0, 0]),
        # (the side walls stop at the east wall's inner face: the east wall holds the corners)
        "chancel north": {"type": "wall", "width": "chL - t", "height": "chH", "thickness": "t", "openings": [{"at": "(chL - t) / 2", "width": 0.9, "sill": 2.0, "springing": "chH - 1.3", "head": rnd}],
                          "at": [["L / 2 + (chL - t) / 2", 0, "0 - chB / 2 + t", 0]]},
        "chancel south": {"type": "wall", "width": "chL - t", "height": "chH", "thickness": "t", "openings": [{"at": "(chL - t) / 2", "width": 0.9, "sill": 2.0, "springing": "chH - 1.3", "head": rnd}],
                          "at": [["L / 2 + (chL - t) / 2", 0, "chB / 2", 0]]},
        "chancel east": {"type": "wall", "width": "chB", "height": "chH", "thickness": "t", "openings": [{"at": "chB / 2", "width": 1.2, "sill": 2.0, "springing": "chH - 1.2", "head": rnd}],
                         "at": [["L / 2 + chL", 0, 0, PI2]]},
        "chancel floor": box("chL - t / 2 + 0.02", "chB - 2 * t", "g", ["L / 2 - 0.02 + (chL - t / 2 + 0.02) / 2", 0, 0, 0]),   # (from the nave floor's end: no two floors in the chancel arch)
        "nave roof": {"type": "roof", "form": "gable", "width": "B", "length": "L - t / 2", "pitch": "pitch", "overhang": 0.45, "at": [["t / 4", "hN", 0, PI2]],
                      "_about": "(its west gable in the middle of the wall, not in the tower's face)"},
        "chancel roof": {"type": "roof", "form": "gable", "width": "chB", "length": "chL + 0.4", "pitch": "pitch", "overhang": 0.35, "at": [["L / 2 + chL / 2", "chH", 0, PI2]]},
        # the west tower: its walls in tiers -- the door (west) and into the nave (east) at the foot, slits, the belfry at the top
        "tower": {"type": "enclosure", "plan": {"rect": ["S", "S"]}, "thickness": "t", "height": "tH", "at": [[tx, 0, 0, 0]],
                  "faces": {"3": [{"h": 3.4, "openings": [{"at": "dz", "width": 1.6, "sill": 0, "springing": 2.4, "head": rnd, "glass": False}]},
                                  {"h": "tH - 3.4 - belH", "openings": [{"at": 0, "width": 0.35, "sill": 3.0, "springing": 4.0, "head": rnd, "glass": False}]},
                                  {"openings": {"pattern": "2", "width": 0.9, "gap": 0.5, "pier": 0.9, "end": "(S - 2.3) / 2", "sill": 0.8, "springing": "belH - 0.9", "head": rnd, "glass": False}}],
                            "1": [{"h": 3.4, "openings": [{"at": "0 - dz", "width": 1.6, "sill": 0, "springing": 2.4, "head": rnd, "glass": False}]},
                                  {"h": "tH - 3.4 - belH", "openings": []},
                                  {"openings": {"pattern": "2", "width": 0.9, "gap": 0.5, "pier": 0.9, "end": "(S - 2.3) / 2", "sill": 0.8, "springing": "belH - 0.9", "head": rnd, "glass": False}}],
                            "0": [{"h": "tH - belH", "openings": [{"at": 0, "width": 0.35, "sill": 6.0, "springing": 7.0, "head": rnd, "glass": False}]},
                                  {"openings": {"pattern": "2", "width": 0.9, "gap": 0.5, "pier": 0.9, "end": "(S - 2.3) / 2", "sill": 0.8, "springing": "belH - 0.9", "head": rnd, "glass": False}}],
                            "2": [{"h": "tH - belH", "openings": []},
                                  {"openings": {"pattern": "2", "width": 0.9, "gap": 0.5, "pier": 0.9, "end": "(S - 2.3) / 2", "sill": 0.8, "springing": "belH - 0.9", "head": rnd, "glass": False}}]}},
        # (STRING COURSES round the tower at its stages -- over the door's storey and under the belfry -- standing proud:
        #  the shaft read as one plain block, 2026-10-24)
        "tower courses": {"type": "enclosure", "plan": {"rect": ["S + 0.24", "S + 0.24"]}, "thickness": 0.16, "height": 0.26, "openings": [],
                          "at": [[tx, 3.3, 0, 0], [tx, "tH - belH - 0.25", 0, 0]]},
        "tower floor": box("S - t", "S - 0.04", "g", [f"{tx} - t / 2 + 0.02", 0, 0, 0]),   # (to the nave floor's end, under the tower's east wall: one floor in its doorway)
        "tower stair": comp("components/tower-stair", [tx, "g", 0, 0], {"W": "S - 2 * t", "H": "tH - belH - g", "tR": "tR", "n": "tn", "wall": 0.3, "slab": 0.3,
                                                                          "tx": "S / 2 - t - tR - 0.02", "tz": "0 - (S / 2 - t - tR - 0.02)"}),
        # the tops (one of them)
        "spire": {"type": "dome", "sides": 8, "radius": "S / 2 + 0.3", "thickness": 0, "head": {"profile": "trigonal", "rise": "S * 2.4"}, "at": [[tx, "tH", 0, 0]]},
        "pyramid": {"type": "roof", "form": "pyramid", "width": "S + 0.5", "length": "S + 0.5", "pitch": 62, "at": [[tx, "tH", 0, 0]]},
        "saddleback": {"type": "roof", "form": "gable", "width": "S + 0.5", "length": "S + 0.5", "pitch": 58, "at": [[tx, "tH", 0, PI2]]},
        "onion drum": {"type": "ring", "count": 8, "rOuter": "S / 2 - 0.4", "rInner": "S / 2 - 0.9", "height": 1.4, "y": "tH + 0.3", "solid": True, "place": [[tx, 0, 0, 0]]},
        "onion base": box("S + 0.3", "S + 0.3", 0.3, [tx, "tH", 0, 0]),
        "onion": {"type": "dome", "sides": 16, "radius": "S / 2 - 0.2", "thickness": 0, "head": {"profile": "onion", "bulge": 1.3, "neck": 0.85}, "at": [[tx, "tH + 1.7", 0, 0]]},
        "battlement roof": box("S", "S", 0.3, [tx, "tH", 0, 0]),
        "battlements": comp("components/crenellation", [[tx, "tH + 0.3", "S / 2 - 0.25", 0], [tx, "tH + 0.3", "0 - S / 2 + 0.25", 0]],
                            {"L": "S", "t": 0.5, "h": 0.9, "step": 1.6, "mh": 0.7}, build=["parapet", "merlons"]),
        "battlements x": comp("components/crenellation", [[f"{tx} + S / 2 - 0.25", "tH + 0.3", 0, PI2], [f"{tx} - S / 2 + 0.25", "tH + 0.3", 0, PI2]],
                              {"L": "S - 1.0", "t": 0.5, "h": 0.9, "step": 1.6, "mh": 0.7}, build=["parapet", "merlons"]),
        "cross": col(0.08, 2.2, [tx, "tH + S * 2.4 - 0.2", 0, 0], sides=6),
        "cross pyramid": col(0.08, 2.0, [tx, "tH + (S + 0.5) / 2 * 1.8807 - 0.2", 0, 0], sides=6),
        # inside: the floor marked by use (zones, assets/architecture/furnishing.json): the nave's seating in two ranks on
        # an aisle, the altar in the chancel -- no organ (a village church has none, and its west door needs the nave end free)
        "seating": {"type": "zone", "zone": "seating", "w": "B - 2 * t - 0.6", "d": "L - 2 * t - 4.6", "h": "hN", "at": [["0 - L / 2 + t + 2.2 + (L - 2 * t - 4.6) / 2", "g", 0, 0]],
                    "_about": "the nave's seating: pews in two ranks on an aisle, from 2.2 m inside the west door up to 2.4 m short of the chancel arch"},
        "altar": {"type": "zone", "zone": "altar", "w": "chB - 2 * t - 1", "d": 3.2, "h": "chH", "at": [["L / 2 + chL - t - 1.6", "g", 0, 0]]},
        "door": marker("door", [f"{tx} - S / 2 + t / 2", "g", "dz", PI2], w=1.6, h="2.4 + 0.8 - g", spring="2.4 - g", head=rnd),
    }
    write("village/church", {"name": "Village church", "_about": "A VILLAGE CHURCH: a nave with round-headed windows, a lower chancel to the east (+x) through a round chancel arch, a square WEST TOWER entered from the west (its door the church's) with a spiral turret up to the belfry floor; the tower's top is the town's style -- a spire, a pyramid, a saddleback, an onion, or battlements. Its floor is marked by use (zones: seating, altar) and furnished by assets/architecture/furnishing.json.",
                             "params": params, "parts": parts,
                             "build": ["nave", "nave floor", "chancel north", "chancel south", "chancel east", "chancel floor", "nave roof", "chancel roof",
                                       "tower", "tower floor", "tower stair", "spire", "cross", "seating", "altar", "door"], "walked": True})




# ---- THE FARMYARDS (2026-10-01): fences, sheds and yards as assets (they were index.html/village.js code) --------------
# components/fence: one straight run along +x, L long, in a STYLE (rails: post-and-rail; picket; wattle: hurdles between
# posts; zigzag: the split-rail worm fence; stone: a dry-stone dyke) -- components/gate: a leaf of rails on its post,
# swung open by `open` degrees -- components/pigsty, hen-house, stable: the sheds -- village/pig-yard, hen-yard,
# stable-yard: a fence round the yard with a gate toward the street (-z), the shed, and the MARKERS the game's stock
# live by: `pen` (the animals' range: w by d about the marker, `kind`), `block` (rects they keep out of: the shed,
# the trough), `trough` (a water vessel, tableware.js). Everything wooden is finished by the town's style (town.js
# yardFinish); the fence's style is the yard's `fence` param.
def fence_component():
    deg = 25 * 3.14159265 / 180
    parts = {
        # (p0/p1 0: no post at the start/the end -- the run meets another at a corner, whose post is the other's)
        "posts": {**col(0.07, "h", [["(1 - p0) * L / round(L / bay)", 0, 0, 0]], sides=6), "repeat": {"count": "round(L / bay) - 1 + p0 + p1", "step": ["L / round(L / bay)", 0, 0, 0]}, "when": {"style": ["rails", "picket"]}},
        "rail low": {**box("L / round(L / bay)", 0.07, 0.09, ["L / round(L / bay) / 2", 0.46, 0, 0]), "repeat": {"count": "round(L / bay)", "step": ["L / round(L / bay)", 0, 0, 0]}, "when": {"style": "rails"}},
        "rail high": {**box("L / round(L / bay)", 0.07, 0.09, ["L / round(L / bay) / 2", "h - 0.2", 0, 0]), "repeat": {"count": "round(L / bay)", "step": ["L / round(L / bay)", 0, 0, 0]}, "when": {"style": "rails"}},
        "picket rails": {**box("L / round(L / bay)", 0.05, 0.07, [["L / round(L / bay) / 2", 0.3, 0, 0], ["L / round(L / bay) / 2", "h - 0.35", 0, 0]]), "repeat": {"count": "round(L / bay)", "step": ["L / round(L / bay)", 0, 0, 0]}, "when": {"style": "picket"}},
        "pickets": {**box(0.07, 0.025, "h - 0.15", ["L / round(L / 0.16) / 2", 0.1, 0.0325, 0]),   # (nailed to the rails: 5mm into their face, not 2.5mm off it)
        "repeat": {"count": "round(L / 0.16)", "step": ["L / round(L / 0.16)", 0, 0, 0]}, "when": {"style": "picket"}},
        "wattle posts": {**col(0.06, "h - 0.05", [[0, 0, 0, 0]], sides=6), "repeat": {"count": "round(L / 1.2) + 1", "step": ["L / round(L / 1.2)", 0, 0, 0]}, "when": {"style": "wattle"}},
        "hurdles": {**box("L", 0.06, "h - 0.25", ["L / 2", 0.08, 0, 0]), "when": {"style": "wattle"}},
        "zig": {**box("bay / 0.9063 + 0.3", 0.1, 0.11, [["bay / 2", 0.25, 0, deg], ["bay / 2", 0.6, 0, deg], ["bay / 2", 0.95, 0, deg]]), "repeat": {"count": "ceil(round(L / bay) / 2)", "step": ["2 * bay", 0, 0, 0]}, "when": {"style": "zigzag"}},
        "zag": {**box("bay / 0.9063 + 0.3", 0.1, 0.11, [["bay * 1.5", 0.25, 0, "0 - " + str(deg)], ["bay * 1.5", 0.6, 0, "0 - " + str(deg)], ["bay * 1.5", 0.95, 0, "0 - " + str(deg)]]), "repeat": {"count": "floor(round(L / bay) / 2)", "step": ["2 * bay", 0, 0, 0]}, "when": {"style": "zigzag"}},
        "dyke": {**box("L", 0.45, "h - 0.25", ["L / 2", 0, 0, 0]), "when": {"style": "stone"}},
        "coping": {**box("L", 0.55, 0.12, ["L / 2", "h - 0.25", 0, 0]), "when": {"style": "stone"}},
    }
    write("components/fence", {"name": "Fence", "_about": "a straight run of fence along +x, L long: `style` rails (post-and-rail, two rails), picket, wattle (hurdles woven between posts), zigzag (the split-rail worm fence, three rails a bay laid at 25 degrees either way) or stone (a dry-stone dyke with its coping); `bay` the posts' spacing, `h` the height",
                               "params": {"detail": 4, "L": 10, "style": "rails", "bay": 2.0, "h": 1.15, "p0": 1, "p1": 1, "_p0": "1/0: a post at the start / at the end (p1) -- 0 where the run meets another fence at a corner and shares its post"}, "parts": parts, "build": list(parts)})
    gate = {
        "post": col(0.09, 1.3, [[0, 0, 0, 0], ["W", 0, 0, 0]], sides=6),
        "stile": box(0.08, 0.08, 1.1, ["0.1 * cos(open * 0.0174533) + 0.1", 0.05, "0 - 0.1 * sin(open * 0.0174533)", "open * 0.0174533"]),
        "leaf rails": box("W - 0.3", 0.06, 0.09, [["(W - 0.3) / 2 * cos(open * 0.0174533) + 0.1", 0.3, "0 - (W - 0.3) / 2 * sin(open * 0.0174533)", "open * 0.0174533"],
                                                   ["(W - 0.3) / 2 * cos(open * 0.0174533) + 0.1", 0.65, "0 - (W - 0.3) / 2 * sin(open * 0.0174533)", "open * 0.0174533"],
                                                   ["(W - 0.3) / 2 * cos(open * 0.0174533) + 0.1", 1.0, "0 - (W - 0.3) / 2 * sin(open * 0.0174533)", "open * 0.0174533"]]),
        "brace": box("W - 0.3", 0.05, 0.07, ["(W - 0.3) / 2 * cos(open * 0.0174533) + 0.1", 0.55, "0 - (W - 0.3) / 2 * sin(open * 0.0174533)", "open * 0.0174533"], **{"_about": "the diagonal, drawn level: a rail at mid height"}),
    }
    write("components/gate", {"name": "Gate", "_about": "a field gate W wide between two posts on the x axis, its leaf of three rails hung on the first post and swung `open` degrees (positive: into -z... the yard side as the fence runs)",
                              "params": {"detail": 4, "W": 1.6, "open": 80}, "parts": gate, "build": list(gate)})


def sheds():
    # the pigsty: three boarded walls, open to -z (the yard), a lean-to roof sloping down to the back, the trough beside
    sw, sd, sh = 3.4, 2.6, 1.5
    sty = {
        "floor": box(sw, sd, 0.05, [0, 0, 0, 0]),
        "back wall": box(sw, 0.15, sh, [0, 0, sd / 2 - 0.075, 0]),
        "side walls": box(0.15, sd, sh, [[-(sw / 2 - 0.075), 0, 0, 0], [sw / 2 - 0.075, 0, 0, 0]]),
        "front posts": box(0.15, 0.15, sh + 0.5, [[-(sw / 2 - 0.075), 0, -(sd / 2 - 0.075), 0], [sw / 2 - 0.075, 0, -(sd / 2 - 0.075), 0]]),
        "roof": {"type": "roof", "form": "shed", "width": sd + 0.8, "length": sw + 0.4, "pitch": 11, "overhang": 0.1, "at": [[0, sh, 0, PI2]],
                 "_about": "a shed roof rises toward its own +x: turned so it rises toward the open front (-z)"},
        "trough": box(1.4, 0.45, 0.32, [-(sw / 2 + 1.2), 0, 0.6, 0]),
        "slop": box(1.25, 0.32, 0.03, [-(sw / 2 + 1.2), 0.3, 0.6, 0]),
        "block": marker("block", [0, 0, 0.15, 0], w=sw, d=sd - 0.3),
    }
    write("components/pigsty", {"name": "Pigsty", "_about": "a pigsty: three boarded walls open to -z under a lean-to roof, a trough beside it; its `block` marker keeps the pigs out of its walls", "params": {"detail": 4}, "parts": sty, "build": list(sty)})
    # the hen house on legs: a boarded box under a little gable, the pop-hole and its ladder plank toward -z
    hw, hd, legH, bh = 1.9, 1.5, 0.55, 1.1
    hen = {
        "legs": col(0.05, legH, [[a * (hw / 2 - 0.15), 0, b * (hd / 2 - 0.15), 0] for a in (-1, 1) for b in (-1, 1)], sides=6),
        # a boarded box, hollow, its floor on the legs; the POP-HOLE a real opening in the -z face (face 2 runs -x: its
        # `at` 0.4 is x -0.4)
        "floor": box(hw, hd, 0.05, [0, legH, 0, 0]),
        "house": {"type": "enclosure", "plan": {"rect": [hw, hd]}, "thickness": 0.04, "height": bh, "at": [[0, legH, 0, 0]], "openings": [],
                  "faces": {"2": [{"at": 0.4, "width": 0.36, "sill": 0.05, "springing": 0.47, "head": {"profile": "flat"}, "glass": False}]}},
        "roof": {"type": "roof", "form": "gable", "width": hd + 0.3, "length": hw + 0.3, "pitch": 30, "overhang": 0.1, "at": [[0, legH + bh, 0, PI2]], "_about": "(a roof's ridge runs along its `length`, its own z: turned so the ridge runs the house's long way, x)"},
        "perch": box(hw - 0.06, 0.04, 0.04, [0, legH + 0.45, 0.2, 0]),   # (its ends 1 cm into the end boards: it rests in them)
        # the hens' LADDER: a thin plank with cleats (a flight of little steps on a soffit), air under it, from the
        # ground up to the pop-hole's sill (yaw -pi/2: it climbs toward +z, its width toward +x of its placement)
        "ladder": {"type": "flight", "use": "ramp", "walk": False, "run": 0.22, "steps": 5, "base": 0, "top": legH + 0.1, "landing": 0, "width": 0.3, "soffit": 0.05,
                   "at": [[-0.55, 0, -(hd / 2) - 1.1, "0 - " + PI2]]},
        "bowl": col(0.2, 0.1, [[1.5, 0, 1.0, 0]], sides=10),
        "block": marker("block", [0, 0, 0, 0], w=hw + 0.4, d=hd + 0.4),
    }
    write("components/hen-house", {"name": "Hen house", "_about": "a hen house on four legs: a hollow boarded box under a little gable with a perch inside, the pop-hole opening toward -z and the hens' cleated ladder plank up to it (air beneath), a water bowl in the yard", "params": {"detail": 4}, "parts": hen, "build": list(hen)})
    # the stable: a stone plinth, boarded walls, a tiled gable roof, four 3 m stalls opening -z through half-doors
    bw, bd, bh = 12, 5, 2.6
    stable = {
        "floor": box(bw, bd, 0.12, [0, 0, 0, 0]),
        "plinth": box(bw, 0.3, 0.6, [0, 0, bd / 2 - 0.15, 0]),
        "back wall": box(bw, 0.25, bh - 0.6, [0, 0.6, bd / 2 - 0.125, 0]),
        "end plinths": box(0.3, bd, 0.6, [[-(bw / 2 - 0.15), 0, 0, 0], [bw / 2 - 0.15, 0, 0, 0]]),
        "end walls": box(0.25, bd, bh - 0.6, [[-(bw / 2 - 0.125), 0.6, 0, 0], [bw / 2 - 0.125, 0.6, 0, 0]]),
        "lintel": box(bw, 0.25, 0.25, [0, bh - 0.25, -(bd / 2 - 0.125), 0]),
        "roof": {"type": "roof", "form": "gable", "width": bd + 0.9, "length": bw + 0.8, "pitch": 35, "overhang": 0.2, "at": [[0, bh, 0, PI2]], "_about": "(a roof's ridge runs along its `length`, its own z: turned so it runs the block's 12 m, x)"},
        "stall posts": box(0.22, 0.22, bh, [[-bw / 2 + i * 3, 0, -(bd / 2 - 0.11), 0] for i in range(5)]),
        "half-doors": box(2.7, 0.08, 1.25, [[-bw / 2 + 1.5 + i * 3, 0, -(bd / 2 - 0.12), 0] for i in range(4)]),
        "partitions": box(0.08, bd - 0.5, bh - 0.3, [[-bw / 2 + 3 + i * 3, 0.15, 0.1, 0] for i in range(3)]),
        "hay": {"type": "dome", "sweep": 1, "sides": 8, "radius": 0.9, "thickness": 0, "head": {"profile": "pointed", "spread": 0.8}, "at": [[-bw / 2 + 1.5 + i * 3, 0.12, -(bd / 2 - 1.2), 0] for i in range(4)],
                "_about": "a heap of hay on the floor of each stall, its top showing over the half-door (it was a cap of it hung in the air at the door's height)"},
        "trough": marker("trough", [-(bw / 2 + 1.8), 0, -(bd / 2 + 1.4), 0], fill=0.6, drink="water"),
        "hitching posts": box(0.12, 0.12, 1.1, [[-1.5, 0, -(bd / 2 + 2.4), 0], [1.5, 0, -(bd / 2 + 2.4), 0]]),
        "hitching rail": box(3.6, 0.1, 0.1, [0, 0.95, -(bd / 2 + 2.4), 0]),
        "bales": {**col(0.6, 1.2, [[4.6, 0, -(bd / 2 + 1.6), 0], [5.9, 0, -(bd / 2 + 1.6), 0], [5.25, 1.2, -(bd / 2 + 1.6), 0]], sides=10)},
        "block": marker("block", [[0, 0, 0.15, 0], [-(bw / 2 + 1.8), 0, -(bd / 2 + 1.4), 0], [5.25, 0, -(bd / 2 + 1.6), 0]], w=[bw + 0.6, 2.8, 3.1], d=[bd + 0.3, 1.2, 1.6]),
    }
    write("components/stable", {"name": "Stable", "_about": "a stable block: a stone plinth, boarded walls and a tiled gable roof, four 3 m stalls opening -z through half-doors with the hay showing over them; a stone water trough (a `trough` marker: tableware.js fills it), a hitching rail and stacked bales in the yard before it; `block` markers keep the horses out of the walls, the trough and the bales", "params": {"detail": 4}, "parts": stable, "build": list(stable)})


def yards():
    for key, name, kind, w, d, shed, shed_at, about in (
            ("pig-yard", "Pig yard", "pigs", 20, 15, "pigsty", ["W / 2 - 2.3", 0, "D / 2 - 1.9", 0], "a fenced yard with a pigsty in its south-east corner, a trough beside it and a wallow in the middle"),
            ("hen-yard", "Hen yard", "hens", 15, 12, "hen-house", ["0 - W / 2 + 2.6", 0, "D / 2 - 2.2", 0], "a fenced yard with a hen house on legs in its south-west corner, grain scattered before it"),
            ("stable-yard", "Stable yard", "horses", 22, 16, "stable", ["0 - W / 2 + 7", 0, "D / 2 - 3.5", 0], "a fenced paddock with the stable block along its south side, a trough, a hitching rail and bales in the yard")):
        params = {"detail": 4, "W": w, "D": d, "fence": "rails", "gateW": 1.6, "gx": "0 - W / 2 + 3.5",
                  "_W": "the yard W by D inside the fence; the gate on the north side (-z, toward the street) gateW wide, gx from the middle; `fence` the fence's style (components/fence)"}
        F = lambda at, L: comp("components/fence", at, {"L": L, "style": "fence"})
        parts = {
            # the fence: runs along each side, the north one in two with the gate's gap between
            "fence north west": F(["0 - W / 2", 0, "0 - D / 2", 0], "gx - gateW / 2 - (0 - W / 2)"),
            "fence north east": F(["gx + gateW / 2", 0, "0 - D / 2", 0], "W / 2 - (gx + gateW / 2)"),
            "fence east": F(["W / 2", 0, "0 - D / 2", "0 - " + PI2], "D"),
            "fence south": F(["W / 2", 0, "D / 2", "3.14159265"], "W"),
            "fence west": F(["0 - W / 2", 0, "D / 2", PI2], "D"),
            "gate": comp("components/gate", ["gx - gateW / 2", 0, "0 - D / 2", 0], {"W": "gateW", "open": 80}),
            "shed": comp("components/" + shed, shed_at),
            "pen": marker("pen", [0, 0, 0, 0], w="W - 1.4", d="D - 1.4", kind=kind),
        }
        if kind == "pigs":
            # the wallow: trodden mud in overlapping rounds (no edge straight), and in its lowest middle the wet, darker and
            # a little proud of it so the two never fight
            parts["wallow"] = col(1.0, 0.03, [[-1, 0, 0.5, 0], [0.3, 0, 0.9, 0.4], [-2.3, 0, 0.1, 0.9], [-0.6, 0, -0.5, 1.3], [-1.7, 0, 1.4, 0.2], [0.6, 0, -0.2, 2.1]], sides=18)
            parts["wallow rim"] = col(0.6, 0.03, [[0.05, 0, -0.6, 0], [0.75, 0, 0.45, 0.6], [-0.6, 0, 1.45, 1.2], [-2.3, 0, 0.95, 1.8], [-1.6, 0, -0.5, 2.4]], sides=14)   # (the notches between the rounds filled)
            # the rest of the yard rooted up: bare earth in rounds (as the hen yard's, under the wallow)
            parts["scratched"] = col(1.9, 0.022, [[x, 0, z, (i * 0.9) % 3.14] for i, (x, z) in enumerate(
                [(-6.5, -3.5), (-4.0, -4.2), (-1.0, -3.8), (2.2, -3.2), (5.0, -3.6), (-6.8, 0.2), (3.6, 0.0), (6.4, 1.6), (-5.6, 3.6), (-2.6, 4.2), (1.2, 3.9), (4.2, 3.4),
                 (-1.0, 0.5), (1.0, 1.6), (-3.2, 0.6), (-1.4, -1.8), (0.8, -1.0), (-2.8, 2.2), (1.8, 0.2)])], sides=16)   # (and under the wallow: no ring of grass round it)
            parts["wallow wet"] = col(0.55, 0.04, [[-0.9, 0, 0.45, 0], [-0.2, 0, 0.7, 0.7], [-1.5, 0, 0.2, 1.4]], sides=12)
        if kind == "horses":   # trodden bare before the stable's stalls and on the way in from the gate
            parts["scratched"] = col(1.6, 0.022, [[x, 0, z, (i * 0.8) % 3.14] for i, (x, z) in enumerate(
                [(-9.5, 0.6), (-7.2, 0.4), (-4.9, 0.7), (-2.6, 0.5), (-0.3, 0.6), (1.6, 0.3), (-8.4, -1.5), (-5.8, -1.4), (-3.2, -1.6), (-0.8, -1.2),
                 (-7.4, -3.6), (-7.2, -5.8)])], sides=16)
        if kind == "hens":
            parts["grain"] = col(0.35, 0.03, [[-1.5, 0, -1.2, 0], [-1.1, 0, -1.0, 0.5], [-1.8, 0, -0.9, 1.1]], sides=10)   # (scattered, not a mat)
            # the ground the hens have scratched bare: earth in overlapping rounds over most of the yard, the grass left
            # along the fence (a hair under the grain, so the two never fight)
            parts["scratched"] = col(1.7, 0.022, [[x, 0, z, (i * 0.7) % 3.14] for i, (x, z) in enumerate(
                [(-4.5, 2.5), (-2.5, 3.8), (-1.5, 1.0), (0.8, 2.2), (2.8, 0.6), (-3.6, -0.4), (-0.8, -1.6), (1.6, -2.2), (3.8, -1.9), (-2.6, -2.9), (4.6, 2.6), (0.0, -3.6)])], sides=16)
        write("village/" + key, {"name": name, "_about": about.upper()[:1] + about[1:] + " -- the fence a `fence` component a side, the gate open to the street, the shed a component; `pen` and `block` markers say where the stock may go, `trough` where it drinks (index.html).",
                                 "params": params, "parts": parts, "build": list(parts)})


# ---- THE MARKET (2026-10-02, was village.js marketplace): a paved 14 x 12 m square open to the street on its +z side,
# the market cross in the middle, eight stalls round the other three sides (items/furniture/market-stall: its
# counter, its posts, its striped awning, its wares and its vendor), and the shoppers' places
def market():
    S = 3.14159265
    stalls = [  # x, z, yaw (the stall's counter toward +x, turned to face the square), wares, the awning's stripes
        (-5.6, -3.6, 0, "pottery", "stripe-madder"), (-5.6, 0, 0, "vegetables", "stripe-green"), (-5.6, 3.6, 0, "fish", "stripe-woad"),
        (5.6, -3.6, S, "meat", "stripe-madder"), (5.6, 0, S, "eggs", "canvas"), (5.6, 3.6, S, "bread", "stripe-woad"),
        (-2.2, -4.6, -PI2f, "fruit", "stripe-madder"), (2.2, -4.6, -PI2f, "cheese", "stripe-green")]
    parts = {"paving": box(14, 12, 0.1, [0, 0, 0, 0], walked=True),
             "cross step": col(1.2, 0.25, [0, 0.1, 0, 0], sides=12), "cross step 2": col(0.8, 0.25, [0, 0.35, 0, 0], sides=12),
             "cross shaft": col(0.2, 2.6, [0, 0.6, 0, 0], sides=8, taper=0.8),
             "cross": box(0.1, 0.1, 0.9, [0, 3.15, 0, 0]), "cross arms": box(0.5, 0.1, 0.1, [0, 3.7, 0, 0])}
    for i, (x, z, yaw, wares, stripes) in enumerate(stalls):
        parts[f"stall {wares}"] = {"type": "item", "item": "items/furniture/market-stall", "seed": i + 1, "params": {"wares": wares},
                                   "materials": {"awning": {"pattern": "fabrics/stripes", "palette": stripes}}, "at": [[x, 0.1, z, round(yaw, 7)]]}
    for i, (x, z, h) in enumerate([(-2.5, 1.5, 0.4), (2.8, -1.2, 2.6), (0.5, 3.6, -1.2)]):
        parts[f"shopper {i + 1}"] = marker("spot", [x, 0.1, z, h], pose="stand")
    write("village/market", {"name": "Market", "_about": "THE MARKET: a paved square open to the street on its +z side, the market cross in its middle, eight stalls (items/furniture/market-stall) round the other three sides -- pottery, vegetables, fish; meat, eggs, bread; fruit and cheese -- each with its vendor, and shoppers' places on the square",
                             "params": {"detail": 4}, "parts": parts, "build": list(parts)})


# ---- THE BEEKEEPER'S GARDEN (was village.js apiary): a fence with a gap in front, two rows of skeps on their stands,
# the bench with the smoker and a comb frame, the beekeeper among the hives
def apiary():
    F = lambda at, L: comp("components/fence", at, {"L": L, "style": "picket", "h": 0.8})
    parts = {"fence north": F([-5, 0, -4, 0], 10), "fence west": F([-5, 0, 4, PI2f], 8), "fence east": F([5, 0, -4, -PI2f], 8),
             "fence south west": F([-1, 0, 4, 3.14159265], 4), "fence south east": F([5, 0, 4, 3.14159265], 4),
             "skeps": {"type": "item", "item": "items/tools/skep", "at": [[round(-3.3 + k * 2.2, 2), 0, z, -PI2f] for z in (-2, 0.8) for k in range(4)]},
             "bench legs": box(0.08, 0.34, 0.43, [[2.55, 0, 2.9, 0], [3.85, 0, 2.9, 0]]), "bench": box(1.6, 0.4, 0.06, [3.2, 0.43, 2.9, 0]),
             "smoker": col(0.09, 0.22, [2.8, 0.49, 2.9, 0], sides=8), "comb frame": box(0.4, 0.03, 0.3, [3.5, 0.49, 2.9, 0]),
             "beekeeper": marker("spot", [-2.2, 0, -0.6, PI2f], pose="stand", work=1, gesture="tend")}
    write("village/apiary", {"name": "Beekeeper's garden", "_about": "THE BEEKEEPER'S GARDEN: a picket fence with a gap in front, eight skeps (items/tools/skep) in two rows, the bench with the smoker and a comb frame, the beekeeper's place among the hives",
                             "params": {"detail": 4}, "parts": parts, "build": list(parts)})


# ---- THE STONE BRIDGE (was village.js stoneBridge): three semicircular arches on two piers, the middle span clearing a
# barge, the side spans reaching the banks; the deck 2.9 m over the banks with earth ramps faced in stone at either end.
# It runs along z (across the river), x along the river. Its numbers are the river's where it stands (index.html gives
# them): `hw` the river's half-width, `water` its level, `bedL`/`bedR` the bed under the -z and +z piers, `bedAL`/`bedAR`
# under the abutments -- each footed .6 m into the bed (mapgen.js keeps a bridge off water deeper than MAX_PIER_DEPTH).
def bridge():
    P = {"detail": 4, "hw": 10.8, "water": -2.21, "deckW": 4.4, "bedL": -4.71, "bedR": -4.71, "bedAL": -4.71, "bedAR": -4.71,
         "spring": "water + 0.3", "rMid": 4.3, "pierT": 1.2, "wallT": 0.5, "halfL": "hw + 0.7", "zAbut": "halfL - 0.6", "zPier": "rMid + pierT / 2",
         "rSide": "max(1.6, (zAbut - 0.6 - (zPier + pierT / 2)) / 2)", "zSide": "zPier + pierT / 2 + rSide",
         "deckTop": "spring + rMid + 0.5", "deckBot": "deckTop - 0.4", "ramp": 14, "rampPitch": "atan2(deckTop, ramp) * 57.29578",
         "_hw": "the river's half-width where it stands, water its level, bedL/bedR the bed's height under the -z / +z pier (bedAL/bedAR under the abutments): the footings go down to them"}
    face = {"type": "wall", "width": "2 * zAbut", "height": "deckBot - spring", "thickness": "wallT", "glass": False,
            "openings": [{"at": "zAbut", "width": "2 * rMid", "sill": 0, "springing": 0, "head": {"profile": "semicircular"}},   # (a wall's openings are measured from its start)
                         {"at": "zAbut + zSide", "width": "2 * rSide", "sill": 0, "springing": 0, "head": {"profile": "semicircular"}},
                         {"at": "zAbut - zSide", "width": "2 * rSide", "sill": 0, "springing": 0, "head": {"profile": "semicircular"}}]}
    parts = {
        "faces": {**face, "at": [["deckW / 2 - wallT / 2", "spring", 0, PI2f], ["0 - deckW / 2 + wallT / 2", "spring", 0, PI2f]],
                  "_about": "the two faces from the springing to the deck, the three arches through them"},
        "pier L": box("deckW", "pierT + 0.3", "spring - bedL", [0, "bedL", "0 - zPier", 0]),
        "pier R": box("deckW", "pierT + 0.3", "spring - bedR", [0, "bedR", "zPier", 0]),
        "pier fill": box("deckW - wallT", "pierT", "deckBot - spring", [[0, "spring", "0 - zPier", 0], [0, "spring", "zPier", 0]]),
        "abutment L": box("deckW + 0.3", 1.2, "deckBot - bedAL", [0, "bedAL", "0 - zAbut", 0]),
        "abutment R": box("deckW + 0.3", 1.2, "deckBot - bedAR", [0, "bedAR", "zAbut", 0]),
        "cutwaters L": box(1.1, 1.1, "spring - bedL + 0.4", [["deckW / 2 + 0.2", "bedL", "0 - zPier", 0.7853982], ["0 - deckW / 2 - 0.2", "bedL", "0 - zPier", 0.7853982]]),
        "cutwaters R": box(1.1, 1.1, "spring - bedR + 0.4", [["deckW / 2 + 0.2", "bedR", "zPier", 0.7853982], ["0 - deckW / 2 - 0.2", "bedR", "zPier", 0.7853982]]),
        "deck": box("deckW", "2 * halfL", 0.4, [0, "deckTop - 0.4", 0, 0], walked=True),
        "parapets": box(0.35, "2 * halfL", 0.95, [["deckW / 2 - 0.175", "deckTop", 0, 0], ["0 - deckW / 2 + 0.175", "deckTop", 0, 0]]),
        "coping": box(0.45, "2 * halfL + 0.1", 0.1, [["deckW / 2 - 0.175", "deckTop + 0.94", 0, 0], ["0 - deckW / 2 + 0.175", "deckTop + 0.94", 0, 0]]),
        # the ramps: earth banks faced in stone, a solid one-slope wedge from the ground to the deck at each end (a `shed`
        # roof rises toward its own +x: turned to rise toward the bridge), their low walls a 0.6 m slab on the slope
        "ramps": {"type": "roof", "form": "shed", "width": "ramp", "length": "deckW", "pitch": "rampPitch", "overhang": 0,
                  "at": [[0, 0, "halfL + ramp / 2", PI2f], [0, 0, "0 - halfL - ramp / 2", -PI2f]], "walked": True},
        "ramp walls": {"type": "roof", "form": "shed", "width": "ramp", "length": 0.3, "pitch": "rampPitch", "overhang": 0, "shell": 0.6,
                       "at": [["deckW / 2 - 0.15", 0.6, "halfL + ramp / 2", PI2f], ["0 - deckW / 2 + 0.15", 0.6, "halfL + ramp / 2", PI2f],
                              ["deckW / 2 - 0.15", 0.6, "0 - halfL - ramp / 2", -PI2f], ["0 - deckW / 2 + 0.15", 0.6, "0 - halfL - ramp / 2", -PI2f]]},
    }
    write("village/bridge", {"name": "Stone bridge", "_about": "THE STONE BRIDGE: three semicircular arches on two piers (the middle span clears a barge, ~4.3 m over the water), the side spans reaching the banks, the deck 2.9 m over the banks between parapets, earth ramps faced in stone 14 m long at either end; each pier and abutment footed in the bed where it stands (hw, water, bedL, bedR, bedAL, bedAR: the river's numbers there).",
                             "params": P, "parts": parts, "build": list(parts), "walked": True})


# ---- THE FOUNTAIN (was village.js fountain): a paved square opening onto the street, an octagonal basin on a step, a
# column with a small basin and an upper bowl, four spouts whose jets fall into the small basin and spill into the pool;
# buckets on the rim, the villagers fetching water, the bard's pitch. The water is the game's (`flow` markers)
def fountain():
    import math
    R, wallH, step, base = 1.6, 0.75, 0.18, 0.1
    y0 = base + step
    ring8 = lambda ro, ri, h, y: {"type": "ring", "count": 8, "rOuter": ro, "rInner": ri, "height": h, "y": round(y, 4), "solid": True, "place": [[0, 0, 0, 0]]}
    sy, my, wy = y0 + 1.55, y0 + 0.86, y0 + wallH - 0.12
    parts = {"paving": box(8, 8, base, [0, 0, 0, 0], walked=True),
             "step": col(2.55, step, [0, base, 0, 0.3926991], sides=8, taper=round(2.45 / 2.55, 4), walked=True),
             "basin wall": ring8(R + 0.3, R, wallH, y0), "coping": ring8(R + 0.4, R - 0.1, 0.12, y0 + wallH),
             "column": col(0.28, 1.7, [0, y0, 0, 0], sides=8, taper=round(0.2 / 0.28, 4)),
             "small basin": col(0.85, 0.08, [0, y0 + 0.6, 0, 0.3926991], sides=8, taper=round(0.95 / 0.85, 4)),
             "small basin wall": ring8(0.96, 0.84, 0.3, y0 + 0.6), "small coping": ring8(1.02, 0.78, 0.08, y0 + 0.9),
             "bowl": col(0.38, 0.22, [0, y0 + 1.7, 0, 0.3926991], sides=8, taper=round(0.6 / 0.38, 4)), "brim": ring8(0.6, 0.52, 0.16, y0 + 1.92),
             "stem": col(0.12, 0.3, [0, y0 + 1.92, 0, 0], sides=8, taper=round(0.08 / 0.12, 4)),
             # (closed underneath: the disc under it sits on the stem -- an open skin stood on its rim, round the stem, in the air)
             "finial": {"type": "dome", "radius": 0.16, "sides": 8, "thickness": 0, "head": {"profile": "semicircular", "seg": 4}, "at": [[0, round(y0 + 2.22, 4), 0, 0]]},
             "spouts": box(0.45, 0.07, 0.07, [[round(0.45 * math.cos(k * math.pi / 2), 4), round(sy - 0.035, 4), round(0.45 * math.sin(k * math.pi / 2), 4), round(-k * math.pi / 2, 7)] for k in range(4)]),
             "pools": {"type": "marker", "role": "flow", "at": [[0, round(wy, 4), 0, 0]], "data": {"kind": "pool", "r": R, "seg": 8}},
             "small pool": {"type": "marker", "role": "flow", "at": [[0, round(my, 4), 0, 0]], "data": {"kind": "pool", "r": 0.8, "seg": 8}},
             "bowl pool": {"type": "marker", "role": "flow", "at": [[0, round(y0 + 1.95, 4), 0, 0]], "data": {"kind": "pool", "r": 0.52, "seg": 8}},
             "jets": {"type": "marker", "role": "flow", "at": [[round(0.66 * math.cos(k * math.pi / 2), 4), round(my - 0.02, 4), round(0.66 * math.sin(k * math.pi / 2), 4), 0] for k in range(4)],
                      "data": {"kind": "jet", "r": 0.04, "h": round(sy - my, 4)}},
             "bucket 1": marker("vessel", [R + 0.2, round(y0 + wallH + 0.12, 4), -0.9, 0], kind="bucket", fill=0.9, drink="water"),
             "bucket 2": marker("vessel", [-0.7, round(y0 + wallH + 0.12, 4), R + 0.25, 0], kind="bucket", fill=0.6, drink="water"),
             "fetching": marker("spot", [[R + 0.6, round(y0, 4), -0.9, 3.14159265], [-0.7, round(y0, 4), R + 0.75, PI2f]], pose="stand"),
             "bard": marker("spot", [-(R + 2.3), base, -1.3, 0], pose="stand", work=1, gesture="strum", tool="lute", bard=True),
             "neighbour": marker("spot", [-2.9, base, -2.6, -0.7853982], pose="stand")}
    write("village/fountain", {"name": "Fountain", "_about": "THE PUBLIC FOUNTAIN: a paved square opening onto the street, an octagonal basin on a step, the column with its small basin and upper bowl, four spouts whose jets fall into the small basin and spill into the pool (the water: `flow` markers), wooden buckets on the rim (`vessel`s), villagers fetching water, the bard's pitch on the paving.",
                               "site": {"origin": True}, "params": {"detail": 4, "footW": 9, "footD": 9, "square": 4}, "parts": parts, "build": list(parts)})
    write_finish("fountain", {"name": "Fountain", "building": "architecture/village/fountain", "_about": "the fountain: a flagged square, a grey ashlar basin, its bowls and coping in a finer pale stone, iron spouts",
                              "stone": {"color": "#9a9488", "accent": "#8a8478", "pat": "ashlar"},
                              "rules": [{"parts": "paving", "surface": "floor", "pattern": "floors/flagstones", "palette": "stone"},
                                        {"parts": ["coping", "small basin", "small basin wall", "small coping", "bowl", "brim", "stem", "finial"], "pattern": "stone/ashlar fine", "palette": "limestone"},
                                        {"parts": "spouts", "pattern": "stone/plaster", "palette": "iron"},
                                        {"pattern": "stone/ashlar", "palette": "stone"}]})


# ---- THE FIELDS, THE CURRANT ROWS, THE ORCHARD (were village.js cropField, berryRows, orchard): a tilled plot and what
# grows on it -- a grain's rows painted by the game from the field's `crop` marker (architecture.js cropPanels), the
# cabbages' heads as items, the plowed soil's furrows; the bushes and trees as `plant` markers the flora grows
def fields():
    import random
    for key, crop, w, d, seed, name in (("field-rye", "rye", 14, 12, 1, "Rye field"), ("field-barley", "barley", 14, 12, 2, "Barley field"),
                                        ("field-cabbage", "cabbage", 12, 10, 3, "Cabbage field"), ("field-beans", "beans", 12, 10, 4, "Bean field"),
                                        ("field-garlic", "garlic", 10, 8, 5, "Garlic field"), ("field-soil", "soil", 12, 10, 6, "Plowed field")):
        r = random.Random(seed * 131 + 7)
        parts = {"soil": box(w, d, 0.12, [0, 0, 0, 0], walked=True), "crop": marker("crop", [0, 0, 0, 0], crop=crop, w=w, d=d)}
        if crop == "soil":
            zs = []; z = -d / 2 + 0.5
            while z <= d / 2 - 0.5: zs.append(round(z, 3)); z += 0.55
            parts["furrows"] = box(w - 0.8, 0.24, 0.1, [[0, 0.12, z, 0] for z in zs])
        if crop == "cabbage":
            heads = [[], [], []]; x = -w / 2 + 0.5
            while x <= w / 2 - 0.5:
                z = -d / 2 + 0.5
                while z <= d / 2 - 0.5:
                    heads[r.randrange(3)].append([round(x + (r.random() - 0.5) * 0.12, 3), 0.12, round(z + (r.random() - 0.5) * 0.12, 3), round(r.random() * 6.28, 3)]); z += 0.65
                x += 0.7
            for i, hs in enumerate(heads): parts[f"heads {i + 1}"] = {"type": "item", "item": "items/food/cabbage-head", "seed": i + 1, "solid": False, "at": hs}
        write("village/" + key, {"name": name, "_about": f"A {name.upper()}: a tilled plot {w} x {d} m" + {"soil": ", plowed and not yet sown, its furrows the spade's work", "cabbage": ", its cabbages in rows"}.get(crop, f", its {crop} in rows (painted by the game from the `crop` marker)"),
                                 "site": {"origin": True}, "params": {"detail": 4, "footW": w + 1, "footD": d + 1}, "parts": parts, "build": list(parts)})
        write_finish(key, {"name": name, "building": "architecture/village/" + key, "_about": "the tilled soil" + (" and its furrows" if crop == "soil" else ""),
                           "stone": {"color": "#5b4634", "accent": "#4e3c2c", "pat": "ashlar"}, "rules": [{"pattern": "stone/sand", "palette": "earth"}]})
    # the currant rows: red, white and black, a row of each
    w, d, seed = 14, 9, 3; r = random.Random(seed * 61 + 3); per = int((w - 1) // 1.7); at = []
    for row, fruit in enumerate(("currant", "whitecurrant", "blackcurrant")):
        for k in range(per):
            s_ = 0.85 + r.random() * 0.3
            at.append(([round(-w / 2 + 0.9 + k * 1.7 + (r.random() - 0.5) * 0.2, 3), 0, round(-d / 2 + 1.2 + row * ((d - 2.4) / 2), 3), 0],
                       {"kind": "bush", "fruit": fruit, "seed": seed * 1000 + row * 50 + k, "height": round(1.15 * s_, 3), "rotY": round(r.random() * 6.2832, 3)}))
    parts = {f"bush {i + 1}": {"type": "marker", "role": "plant", "at": [a], "data": dd} for i, (a, dd) in enumerate(at)}
    write("village/berries", {"name": "Currant bushes", "_about": "CURRANT BUSHES in three rows -- red, white and black currants -- as `plant` markers: the flora grows them (makeBush) with their fruit cards.",
                              "site": {"origin": True}, "params": {"detail": 4, "footW": w + 1, "footD": d + 1}, "parts": parts, "build": list(parts)})
    # the orchard: apple and cherry trees on a 5 m grid
    w, d, seed = 22, 16, 5; r = random.Random(seed * 17 + 1); parts = {}
    for i in range(int((w - 2) // 5) + 1):
        for j in range(int((d - 2) // 5) + 1):
            cherry = (i + j) % 2 == 1; s_ = 0.9 + r.random() * 0.25
            parts[f"tree {i + 1}-{j + 1}"] = {"type": "marker", "role": "plant", "at": [[round(-w / 2 + 1 + i * 5 + (r.random() - 0.5) * 0.6, 3), 0, round(-d / 2 + 1 + j * 5 + (r.random() - 0.5) * 0.6, 3), 0]],
                                              "data": {"kind": "tree", "species": "cherry" if cherry else "apple", "seed": seed * 1000 + i * 20 + j, "height": round((5.6 if cherry else 4.8) * s_, 3), "rotY": round(r.random() * 6.2832, 3)}}
    write("village/orchard", {"name": "Orchard", "_about": "THE ORCHARD: apple and cherry trees in turn on a 5 m grid, as `plant` markers: the flora grows them (makeTree) with their fruit.",
                              "site": {"origin": True}, "params": {"detail": 4, "footW": w + 1, "footD": d + 1}, "parts": parts, "build": list(parts)})


if __name__ == "__main__":
    furniture()
    fence_component(); sheds(); yards(); market(); apiary(); bridge(); fountain(); fields()
    for kind in ("gable", "eaves", "jettied", "stone"):
        house(kind)
    longhouse(); wall_segment(); wall_tower(); gatehouse(); church()
    print("written: furniture, fence, gate, sheds, 3 yards, market, apiary, bridge, fountain, 6 fields, berries, orchard, 4 town houses, longhouse, wall, wall tower, gatehouse, church")
