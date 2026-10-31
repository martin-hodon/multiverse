#!/usr/bin/env python3
"""ATTRIBUTES (2026-10-30): what a figure of myth or allegory carries -- the palm of victory, the horn of plenty, a
scroll, a victor's wreath held out -- as items (assets/items/tools/*.json) of the language's own primitives: a frond's
leaflets and a wreath's leaves are `feathers` fans, the horn a `sweep` of growing radii with fruit from the food
catalogue (`use`) heaped in its mouth, a scroll a turned roll on its rods. Each has a `hold`, so a hand -- a statue's
(statues.js: carved, `@stone`), anyone's -- can carry it; `upright` in it: an attribute is shown, held up whatever
the hand does (a statue's grip notwithstanding: statues.js). Edit this for the numbers, then run it:

    python3 tools/attributegen.py
"""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ITEMS = os.path.join(ROOT, "assets", "items")


def write(path, doc):
    full = os.path.join(ITEMS, path + ".json")
    with open(full, "w") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")


def item(name, era, about, params, materials, parts, hold):
    return {"kind": "item", "name": name, "category": "tool", "era": era, "_about": about,
            "params": params, "materials": materials, "parts": parts, "hold": hold}


# THE PALM FROND: a rachis, and a fan of leaflets either side of it -- long at its foot, short at its tip, swept toward
# the tip and drooping. The fans lie in their part's x-z plane (feathers.js), so the frond is built along +z, and held
# by that: its axis the rachis, its face the fan's flat (+y), forward
def palm():
    side = lambda s: {"type": "feathers", "material": "leaf", "n": 16, "shape": "pointed", "lift": 0.0003, "droop": 0.5,
                      "lead": s, "roots": [[0, "L * 0.12"], [0, "L * 0.97"]], "dir": [s * -58, s * -18],
                      "length": ["L * 0.36", "L * 0.07"], "width": ["L * 0.035", "L * 0.012"]}
    parts = [{"id": "rachis", "type": "sweep", "material": "stem", "radii": [0.009, 0.007, 0.005, 0.003],
              "path": [[0, 0, 0], [0, 0, "L * 0.35"], [0, 0, "L * 0.7"], [0, 0, "L"]]},
             {"id": "leaflets out", **side(1)}, {"id": "leaflets in", **side(-1)}]
    return item("Palm frond", "-3000-1900", "a palm frond, carried in triumph -- the victor's palm, the martyr's: a rachis, its leaflets swept toward the tip",
                {"L": [0.8, 1.0]}, {"stem": "stem-green", "leaf": "leaf"}, parts,
                {"grip": [0, 0, "L * 0.06"], "axis": [0, 0, 1], "face": [0, 1, 0], "carry": {"axis": [0.2, 1, 0], "face": [1, 0, 0]}, "upright": True})


# THE HORN OF PLENTY: a goat's horn curling to its point below the hand, widening to its mouth above -- a rim round the
# mouth and the fruit heaped in it (grapes spilling over, an apple, a pear, a pomegranate)
def cornucopia():
    path = [[0.07, -0.16, 0], [0.09, -0.08, 0], [0.04, 0.02, 0], [0, 0.14, 0], [0.02, 0.26, 0]]
    mouth = path[-1]
    d = [mouth[0] - path[-2][0], mouth[1] - path[-2][1]]
    tilt = round(math.degrees(math.atan2(-d[0], d[1])), 1)   # (the rim turned to the horn's last direction, about z)
    fruit = [("grapes", [-0.02, 0.02, 0.01], [0, 0, 40]), ("apple", [0.04, 0.01, 0.03], [0, 0, -10]),
             ("pear", [0.0, 0.03, -0.04], [0, 0, 15]), ("pomegranate", [0.035, 0.0, -0.03], [0, 0, 0])]
    parts = [{"id": "horn", "type": "sweep", "material": "horn", "radii": [0.004, 0.016, 0.03, 0.05, 0.072], "path": path},
             {"id": "rim", "type": "ring", "material": "horn", "r": 0.072, "tube": 0.008, "at": [*mouth, 0, 0, tilt]}]
    for name, off, rot in fruit:
        parts.append({"id": name, "use": "items/food/" + name, "at": [round(mouth[0] + off[0], 3), round(mouth[1] + off[1] - 0.03, 3), round(off[2], 3), *rot]})
    return item("Cornucopia", "-800-1900", "the horn of plenty: a goat's horn curling to its point, its mouth heaped with fruit -- carried by Abundance, Fortune, a river god",
                {}, {"horn": "horn"}, parts,
                {"grip": [0.05, -0.03, 0], "axis": [-0.35, 1, 0], "face": [1, 0, 0], "carry": {"axis": [-0.35, 1, 0], "face": [1, 0, 0]}, "upright": True})


# THE SCROLL: a roll of papyrus wound on its rod, the rod's knobs out at either end; held upright in a fist
def scroll():
    parts = [{"id": "roll", "type": "lathe", "material": "sheet", "profile": [[0, 0], ["R", 0], ["R", "H"], [0, "H"]], "sides": 10, "at": [0, "-H / 2", 0]},
             {"id": "rod", "type": "rod", "material": "rod", "from": [0, "-H / 2 - 0.025", 0], "to": [0, "H / 2 + 0.025", 0], "r": 0.005, "sides": 6},
             {"id": "knobs", "type": "sphere", "material": "rod", "r": 0.009, "at": [[0, "-H / 2 - 0.028", 0], [0, "H / 2 + 0.028", 0]]}]
    return item("Scroll", "-3000-1500", "a scroll: papyrus or parchment rolled on its rod, its knobs out at either end -- a philosopher's, an orator's, a lawgiver's",
                {"R": [0.02, 0.028], "H": [0.22, 0.3]}, {"sheet": "linen", "rod": "ivory"}, parts,
                {"grip": [0, 0, 0], "axis": [0, 1, 0], "face": [1, 0, 0], "carry": {"axis": [0, 1, 0], "face": [1, 0, 0]}, "upright": True})


# A VICTOR'S WREATH held out: a ring of laurel, sprigs of leaves laid round it -- one sprig (a short fan along the ring's
# tangent) placed `n` times about the ring's axis; held by its rim, the ring's plane upright facing forward
def wreath():
    n, R = 12, 0.11
    at = []
    for i in range(n):
        a = 360 * i / n
        at.append([round(R * math.cos(math.radians(a)), 4), 0, round(-R * math.sin(math.radians(a)), 4), 0, a, 0])
    parts = [{"id": "ring", "type": "ring", "material": "stem", "r": R, "tube": 0.005},
             {"id": "sprigs", "type": "feathers", "material": "leaf", "n": 4, "shape": "pointed", "lift": 0.002, "droop": 0.2,
              "lead": 1, "roots": [[0, -0.02], [0, 0.03]], "dir": [-45, 45], "length": [0.05, 0.045], "width": [0.018, 0.016], "at": at}]
    return item("Victor's wreath", "-800-1900", "a wreath of laurel held out to crown a victor -- Victory's, Fame's: sprigs of leaves round a ring",
                {}, {"stem": "stem-green", "leaf": "leaf"}, parts,
                {"grip": [0, 0, R], "axis": [1, 0, 0], "face": [0, 1, 0], "upright": True})


# THE PATERA: the libation dish, a shallow bowl round a boss raised in its middle (the omphalos, where the fingers
# went under it), a ring of tongues radiating round the boss -- held level on the fingers, its rim out before them
def patera():
    R = 0.1
    parts = [{"id": "dish", "type": "lathe", "material": "metal", "double": True, "caps": False,
              "profile": [[0, 0.024], [0.012, 0.022], [0.02, 0.012], [0.03, 0.005], [0.06, 0.008], [0.088, 0.02], [R, 0.03]]},
             {"id": "rim", "type": "ring", "material": "metal", "r": R, "tube": 0.0035, "at": [0, 0.03, 0]},
             {"id": "tongues", "type": "box", "material": "metal", "size": [0.03, 0.006, 0.011], "round": 0.003,
              "around": {"n": 14, "r": 0.052, "plane": "xz"}, "at": [0, 0.009, 0]}]
    return item("Patera", "-800-500", "the libation dish: a shallow bowl round a raised boss, tongues radiating round it -- poured from by a priest, a god, an emperor at the altar",
                {}, {"metal": {"pick": ["gold", "bronze", "silver"]}}, parts,
                {"grip": [-R * 0.3, -0.012, 0], "axis": [0, 1, 0], "face": [1, 0, 0], "upright": True})


# THE LYRE: a tortoise-shell sound box (a turned dome laid on its back, its flat soundboard forward), two horns curving
# up out of it and in again, a yoke across their tips, seven strings from a bridge on the soundboard up to the yoke --
# stood on the hand by the foot of its box, its strings forward
def lyre():
    parts = [{"id": "shell", "type": "lathe", "material": "shell", "profile": [[0, 0.05], [0.06, 0.042], [0.095, 0.02], [0.11, 0]],
              "at": [0, 0, 0, 0, 0, 90], "stretch": [1, 1.12, 0.92]},
             {"id": "arms", "type": "sweep", "material": "horn", "radii": [0.013, 0.011, 0.009, 0.008, 0.006],
              "path": [[0, 0.07, 0.07], [0, 0.17, 0.1], [0, 0.27, 0.085], [0, 0.34, 0.078], [0, 0.39, 0.098]], "mirror": "z"},
             {"id": "yoke", "type": "rod", "material": "wood", "from": [0, 0.335, -0.1], "to": [0, 0.335, 0.1], "r": 0.008, "sides": 8},
             {"id": "bridge", "type": "box", "material": "wood", "size": [0.01, 0.012, 0.1], "round": 0.002, "at": [0.004, -0.045, 0]},
             {"id": "strings", "type": "rod", "material": "string", "from": [0.008, -0.045, 0], "to": [0.004, 0.33, 0], "r": 0.0012, "sides": 3,
              "along": {"n": 7, "from": [0, 0, -0.039], "to": [0, 0, 0.039]}}]
    return item("Lyre", "-1500-400", "the lyre: a tortoise-shell sound box, two horns rising from it, a yoke across them, seven strings -- Apollo's, Orpheus's, a Muse's",
                {}, {"shell": {"pick": ["horn", "walnut"]}, "horn": "horn", "wood": "ebony", "string": "gut"}, parts,
                {"grip": [-0.02, -0.15, 0], "axis": [0, 1, 0], "face": [1, 0, 0], "upright": True})


# THE TRIDENT: a shaft, a socket, and three prongs -- the middle one straight, the outer two bending out of a crossbar
# and up -- each tapering to its point with a barb under it; stood on its butt like a spear (`rest`)
def trident():
    top = "L"
    side = [[0, "L - 0.02", 0.01], [0, "L + 0.005", 0.06], [0, "L + 0.07", 0.085], [0, "L + 0.2", 0.08]]
    parts = [{"id": "shaft", "type": "rod", "material": "shaft", "from": [0, 0, 0], "to": [0, top, 0], "r": 0.014, "sides": 8},
             {"id": "socket", "type": "lathe", "material": "metal", "profile": [[0.017, 0], [0.019, 0.05], [0.024, 0.07], [0.016, 0.085]], "at": [0, "L - 0.07", 0]},
             {"id": "middle", "type": "sweep", "material": "metal", "radii": [0.013, 0.01, 0.008, 0.001], "path": [[0, "L", 0], [0, "L + 0.1", 0], [0, "L + 0.2", 0], [0, "L + 0.27", 0]]},
             {"id": "outer", "type": "sweep", "material": "metal", "radii": [0.011, 0.01, 0.008, 0.001], "path": side, "mirror": "z"},
             {"id": "barbs", "type": "sweep", "material": "metal", "radii": [0.006, 0.001],
              "path": [[0, "L + 0.21", 0.074], [0, "L + 0.165", 0.052]], "mirror": "z"},
             {"id": "barb", "type": "sweep", "material": "metal", "radii": [0.006, 0.001], "path": [[0, "L + 0.23", 0.004], [0, "L + 0.185", 0.025]], "mirror": "z"}]
    return item("Trident", "-800-500", "the three-pronged spear of the sea -- Poseidon's, Neptune's, a Triton's: a shaft, a socket, three barbed prongs",
                {"L": [1.6, 1.8]}, {"shaft": {"pick": ["ash", "oak"]}, "metal": "bronze"}, parts,
                {"grip": [0, "min(0.8, L * 0.42)", 0], "axis": [0, 1, 0], "face": [1, 0, 0], "follow": 0, "rest": "ground", "upright": True})


# THE CADUCEUS: the herald's wand -- a short staff, a knob, a pair of wings at its head, and two snakes wound up it
# the opposite ways (one the other's mirror across the staff: they cross before it and behind), their heads meeting
# under the wings
def caduceus():
    L, turns, n = 0.56, 2.5, 26
    path = []
    for i in range(n + 1):
        f = i / n
        t = f * turns * 2 * math.pi
        r = 0.012 + 0.022 * math.sin(math.pi * min(1, f * 1.15)) ** 0.7
        path.append([round(r * math.sin(t), 4), round(0.08 + f * (L - 0.16), 4), round(r * math.cos(t), 4)])
    end = path[-1]
    path += [[round(end[0] + 0.012, 4), round(end[1] + 0.02, 4), round(end[2] * 0.5, 4)], [0.02, round(end[1] + 0.03, 4), 0.012]]
    radii = [0.002, 0.005, 0.007, 0.007, 0.007, 0.006, 0.005, 0.008]
    wing = {"type": "feathers", "material": "feather", "n": 6, "shape": "rounded", "lift": 0.0008, "droop": 0.6, "lead": 1,
            "roots": [[0, 0.008], [-0.012, 0.01]], "dir": [10, 75], "length": [0.075, 0.045], "width": [0.022, 0.018],
            "at": [0, L - 0.035, 0, 0, 0, -90], "mirror": "z"}
    parts = [{"id": "staff", "type": "rod", "material": "staff", "from": [0, 0, 0], "to": [0, L, 0], "r": 0.008, "sides": 8},
             {"id": "knob", "type": "sphere", "material": "metal", "r": 0.015, "at": [0, L, 0]},
             {"id": "snakes", "type": "sweep", "material": "snake", "radii": radii, "path": path, "mirror": "z"},
             {"id": "wings", **wing}]
    return item("Caduceus", "-800-1900", "the herald's wand: a staff, two snakes wound up it to meet under a pair of wings -- Hermes's, Mercury's, a herald's",
                {}, {"staff": {"pick": ["gold", "ivory"]}, "metal": "gold", "snake": "bronze", "feather": "gold"}, parts,
                {"grip": [0, 0.07, 0], "axis": [0, 1, 0], "face": [1, 0, 0], "carry": {"axis": [0.15, 1, 0], "face": [1, 0, 0]}, "upright": True})


if __name__ == "__main__":
    ipath = os.path.join(ROOT, "assets", "index.json")
    index = json.load(open(ipath))
    tools = next(c for c in index["categories"] if c["name"] == "Items: tools")
    for key, doc in [("palm-frond", palm()), ("cornucopia", cornucopia()), ("scroll", scroll()), ("victor-wreath", wreath()),
                     ("patera", patera()), ("lyre", lyre()), ("trident", trident()), ("caduceus", caduceus())]:
        write("tools/" + key, doc)
        if "items/tools/" + key not in tools["paths"]: tools["paths"].append("items/tools/" + key)   # (the catalogue lists it)
        print("items/tools/" + key)
    json.dump(index, open(ipath, "w"), indent=2, ensure_ascii=False)
