#!/usr/bin/env python3
"""FRUIT AND VEGETABLES (2026-09-30): the produce of the fields, orchards and markets as items (assets/items/food/*.json)
-- lathe-turned fruits and roots, sweeps for pods and cucumbers, clusters of spheres for grapes and berries, leaves as
plates -- each low-poly, seeded a little its own in size, with a `hold` so a hand can carry it, and the catalogue's
"Items: food" category. Edit this for the numbers, then run it:

    python3 tools/foodgen.py
"""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ITEMS = os.path.join(ROOT, "assets", "items")


def write(path, doc):
    full = os.path.join(ITEMS, path + ".json")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")


def item(key, name, kind, era, region, about, params, materials, parts, hold=None):
    doc = {"kind": "item", "name": name, "category": "food/" + kind, "era": era, "region": region, "_about": about,
           "params": params, "materials": materials, "parts": parts}
    doc["hold"] = hold or {"grip": [0, "s * 0.03", 0], "axis": [0, 1, 0], "face": [1, 0, 0]}
    return key, doc


def lathe(id_, material, profile, **kw):
    return {"id": id_, "type": "lathe", "material": material, "profile": profile, **kw}


def stem(y0, y1, r=0.003, lean=0.0, material="stem"):
    return {"id": "stem", "type": "rod", "material": material, "from": [0, y0, 0], "to": [lean, y1, 0], "r": r, "sides": 4}


# ---- LEAVES: as the stall sells them, with their greens on -- a fan of leaves is the `feathers` primitive (one vane a
# leaf, 7 triangles, seen from both sides), a lobed leaf (vine, fig, pumpkin) a thin plate.
#   fan(at, rot, n, length, width, spread, shape, material): the vanes from a point, +z along them before `rot`
#   (yaw, pitch, roll degrees: pitch -90 points them up, -30 out and up); lobed(at, rot, size, material)
def fan(at, rot, n, length, width, spread, shape="rounded", material="leaf", droop=0.5):
    return {"type": "feathers", "material": material, "n": n, "shape": shape, "lift": 0.0004, "droop": droop, "lead": 1,
            "roots": [[0, 0], [0, 0]], "dir": [-spread / 2, spread / 2], "length": [f"s * {length}", f"s * {length * 0.85}"], "width": [f"s * {width}", f"s * {width * 0.85}"],
            "at": [*at, *rot]}


def lobed(at, rot, size, material="leaf"):
    S = f"s * {size}"
    pts = [[0, 0], [.25, .15], [.55, .1], [.45, .4], [.6, .7], [.3, .65], [.15, 1], [0, .85], [-.15, 1], [-.3, .65], [-.6, .7], [-.45, .4], [-.55, .1], [-.25, .15]]
    return {"type": "plate", "material": material, "thick": 0.0008, "at": [*at, *rot], "outline": [[f"s * {x * size:.4f}", f"s * {y * size:.4f}"] for x, y in pts]}


LEAVES = {   # item -> its greens (ids given when applied)
    "apple": [fan([0.003, "s * 0.08", 0], (0, -25, 0), 1, 0.05, 0.025, 0)],
    "pear": [fan([0.004, "s * 0.11", 0], (40, -20, 0), 1, 0.05, 0.022, 0)],
    "plum": [fan([0, "s * 0.058", 0], (0, -15, 0), 1, 0.045, 0.02, 0, "pointed")],
    "cherries": [fan([0, "s * 0.052", 0], (160, -20, 0), 1, 0.045, 0.022, 0, "pointed")],
    "grapes": [lobed([0, "s * 0.125", 0], (0, 70, 0), 0.1, "vine-leaf")],
    "peach": [fan(["s * 0.01", "s * 0.062", 0], (0, 10, 0), 1, 0.06, 0.016, 0, "pointed")],
    "orange": [fan(["s * 0.012", "s * 0.064", 0], (0, 5, 0), 1, 0.045, 0.022, 0, "pointed")],
    "lemon": [fan([0, "s * 0.08", 0], (90, 20, 0), 1, 0.045, 0.02, 0, "pointed")],
    "fig": [lobed([0, "s * 0.066", 0], (0, 70, 0), 0.07)],
    "pomegranate": [fan(["s * 0.012", "s * 0.088", 0], (0, 10, 0), 2, 0.035, 0.012, 30, "pointed")],
    "melon": [lobed(["s * 0.02", "s * 0.17", 0], (0, 75, 0), 0.1), {"type": "rod", "material": "stem", "from": [0, 0, 0], "to": ["s * 0.03", "s * 0.02", 0], "r": 0.003, "sides": 4, "at": [0, "s * 0.172", 0]}],
    "strawberries": [fan([0, "s * 0.03", 0], (0, -45, 0), 3, 0.035, 0.022, 70), fan(["s * 0.025", "s * 0.03", "s * 0.008"], (120, -45, 0), 3, 0.03, 0.02, 70)],
    "carrot": [fan([0, "s * 0.178", 0], (0, -90, 0), 5, 0.08, 0.012, 70, "pointed", "leaf-light", 0.0), fan([0, "s * 0.178", 0], (90, -90, 0), 5, 0.07, 0.012, 70, "pointed", "leaf-light", 0.0)],
    "parsnip": [fan([0, "s * 0.198", 0], (0, -90, 0), 4, 0.07, 0.012, 60, "pointed", "leaf-light", 0.0), fan([0, "s * 0.198", 0], (90, -90, 0), 4, 0.06, 0.012, 60, "pointed", "leaf-light", 0.0)],
    "turnip": [fan([0, "s * 0.068", 0], (0, -70, 0), 3, 0.09, 0.035, 60), fan([0, "s * 0.068", 0], (180, -70, 0), 3, 0.08, 0.035, 60)],
    "beetroot": [fan([0, "s * 0.07", 0], (0, -70, 0), 3, 0.1, 0.035, 60, "rounded", "beet-leaf"), fan([0, "s * 0.07", 0], (180, -70, 0), 3, 0.09, 0.035, 60, "rounded", "beet-leaf")],
    "radish": [fan([0, "s * 0.03", 0], (0, -60, 0), 3, 0.07, 0.03, 60), fan(["s * 0.028", "s * 0.03", "s * 0.006"], (120, -60, 0), 3, 0.06, 0.03, 60), fan(["s * 0.012", "s * 0.03", "-s * 0.024"], (240, -60, 0), 3, 0.065, 0.03, 60)],
    "garlic": [fan([0, "s * 0.06", 0], (0, -80, 0), 3, 0.12, 0.008, 25, "pointed", "husk", 0.8)],
    "onion": [fan([0, "s * 0.1", 0], (0, -75, 0), 2, 0.1, 0.006, 20, "pointed", "husk", 0.6)],
    "pumpkin": [lobed(["s * 0.02", "s * 0.25", 0], (0, 75, 0), 0.14)],
    "marrow": [lobed([0, "s * 0.31", 0], (0, 60, 0), 0.12)],
    "cucumber": [lobed([0, "s * 0.005", 0], (90, 70, 0), 0.08)],
    "pea-pods": [fan([0, "s * 0.012", 0], (180, -30, 0), 2, 0.03, 0.02, 40)],
    "bean-pods": [fan([0, "s * 0.016", 0], (180, -30, 0), 2, 0.05, 0.03, 40)],
    "tomato": [fan([0, "s * 0.064", 0], (0, -30, 0), 1, 0.05, 0.02, 0, "pointed")],
}


FOOD = dict([
    # ---- fruits
    item("apple", "Apple", "fruit", "-1000-1900", "everywhere temperate", "an apple: round, dimpled at the stalk and the eye, a short stalk",
         {"s": [0.9, 1.1]}, {"skin": {"pick": ["apple-red", "apple-red", "apple-green", "apple-yellow"]}, "stem": "stem"}, [
        lathe("body", "skin", [[0, "s * 0.008"], ["s * 0.028", "s * 0.006"], ["s * 0.038", "s * 0.02"], ["s * 0.04", "s * 0.038"], ["s * 0.034", "s * 0.06"], ["s * 0.018", "s * 0.07"], [0, "s * 0.066"]], sides=10),
        stem("s * 0.064", "s * 0.085", 0.0025, 0.004)]),
    item("pear", "Pear", "fruit", "-1000-1900", "everywhere temperate", "a pear: its belly below, its neck narrowing up to the stalk",
         {"s": [0.9, 1.1]}, {"skin": {"pick": ["pear", "pear", "apple-green"]}, "stem": "stem"}, [
        lathe("body", "skin", [[0, "s * 0.004"], ["s * 0.03", "s * 0.004"], ["s * 0.04", "s * 0.03"], ["s * 0.035", "s * 0.055"], ["s * 0.02", "s * 0.075"], ["s * 0.012", "s * 0.09"], [0, "s * 0.096"]], sides=10),
        stem("s * 0.094", "s * 0.115", 0.0025, 0.005)]),
    item("plum", "Plum", "fruit", "-500-1900", "everywhere temperate", "a plum, dark and oval",
         {"s": [0.9, 1.1]}, {"skin": {"pick": ["plum", "plum", "plum-yellow"]}, "stem": "stem"}, [
        lathe("body", "skin", [[0, 0], ["s * 0.02", "s * 0.004"], ["s * 0.025", "s * 0.02"], ["s * 0.021", "s * 0.04"], [0, "s * 0.048"]], sides=10),
        stem("s * 0.046", "s * 0.06", 0.002)]),
    item("cherries", "Cherries", "fruit", "-500-1900", "everywhere temperate", "a pair of cherries on their stalks",
         {"s": [0.9, 1.1]}, {"skin": "cherry-red", "stem": "stem-green"}, [
        {"id": "cherry", "type": "sphere", "material": "skin", "r": "s * 0.011", "sides": 6, "at": [["s * 0.012", "s * 0.011", 0], ["-s * 0.012", "s * 0.011", "s * 0.006"]]},
        {"id": "stalk", "type": "rod", "material": "stem", "from": ["s * 0.012", "s * 0.018", 0], "to": [0, "s * 0.055", 0], "r": 0.0012, "sides": 4},
        {"id": "stalk 2", "type": "rod", "material": "stem", "from": ["-s * 0.012", "s * 0.018", "s * 0.006"], "to": [0, "s * 0.055", 0], "r": 0.0012, "sides": 4}]),
    item("grapes", "Bunch of grapes", "fruit", "-3000-1900", "the Mediterranean, the vine lands", "a bunch of grapes hanging from its stalk, purple or green",
         {"s": [0.9, 1.1], "n": 4}, {"skin": {"pick": ["grape-purple", "grape-green"]}, "stem": "stem-green"}, [
        {"id": "ring 1", "type": "sphere", "material": "skin", "r": "s * 0.0085", "sides": 5, "around": {"n": 7, "r": "s * 0.02", "plane": "xz"}, "at": [0, "s * 0.09", 0]},
        {"id": "ring 2", "type": "sphere", "material": "skin", "r": "s * 0.0085", "sides": 5, "around": {"n": 6, "r": "s * 0.017", "plane": "xz", "start": 25}, "at": [0, "s * 0.075", 0]},
        {"id": "ring 3", "type": "sphere", "material": "skin", "r": "s * 0.0085", "sides": 5, "around": {"n": 5, "r": "s * 0.013", "plane": "xz", "start": 10}, "at": [0, "s * 0.06", 0]},
        {"id": "ring 4", "type": "sphere", "material": "skin", "r": "s * 0.0085", "sides": 5, "around": {"n": 3, "r": "s * 0.008", "plane": "xz", "start": 40}, "at": [0, "s * 0.046", 0]},
        {"id": "tip", "type": "sphere", "material": "skin", "r": "s * 0.0085", "sides": 5, "at": [0, "s * 0.034", 0]},
        {"id": "core", "type": "sphere", "material": "skin", "r": "s * 0.011", "sides": 5, "at": [[0, "s * 0.085", 0], [0, "s * 0.068", 0]]},
        stem("s * 0.095", "s * 0.13", 0.002, 0.006, "stem")]),
    item("peach", "Peach", "fruit", "-300-1900", "China, Persia, the Mediterranean", "a peach, round with its seam and a soft dimple",
         {"s": [0.9, 1.1]}, {"skin": "peach"}, [
        lathe("body", "skin", [[0, "s * 0.004"], ["s * 0.028", "s * 0.004"], ["s * 0.036", "s * 0.02"], ["s * 0.035", "s * 0.045"], ["s * 0.02", "s * 0.064"], [0, "s * 0.062"]], sides=10)]),
    item("orange", "Orange", "fruit", "900-1900", "the Mediterranean, China, India", "an orange, a little flattened, the navel on top",
         {"s": [0.9, 1.1]}, {"skin": "orange"}, [
        lathe("body", "skin", [[0, "s * 0.005"], ["s * 0.03", "s * 0.005"], ["s * 0.038", "s * 0.025"], ["s * 0.035", "s * 0.052"], ["s * 0.015", "s * 0.066"], [0, "s * 0.066"]], sides=10)]),
    item("lemon", "Lemon", "fruit", "1000-1900", "the Mediterranean, Persia, India", "a lemon: an oval with a nipple at each end",
         {"s": [0.9, 1.1]}, {"skin": "lemon"}, [
        lathe("body", "skin", [[0, 0], ["s * 0.006", "s * 0.006"], ["s * 0.024", "s * 0.02"], ["s * 0.028", "s * 0.04"], ["s * 0.022", "s * 0.062"], ["s * 0.006", "s * 0.075"], [0, "s * 0.082"]], sides=9)]),
    item("fig", "Fig", "fruit", "-3000-1900", "the Mediterranean, the Near East", "a fig: a soft purple drop, its stalk on top",
         {"s": [0.9, 1.1]}, {"skin": {"pick": ["fig", "fig-green"]}, "stem": "stem"}, [
        lathe("body", "skin", [[0, 0], ["s * 0.022", "s * 0.006"], ["s * 0.026", "s * 0.02"], ["s * 0.018", "s * 0.04"], ["s * 0.008", "s * 0.052"], [0, "s * 0.056"]], sides=9),
        stem("s * 0.054", "s * 0.068", 0.002)]),
    item("pomegranate", "Pomegranate", "fruit", "-3000-1900", "Persia, the Mediterranean, India", "a pomegranate: a leathery red ball with its crown",
         {"s": [0.9, 1.1]}, {"skin": "pomegranate"}, [
        lathe("body", "skin", [[0, "s * 0.004"], ["s * 0.03", "s * 0.004"], ["s * 0.04", "s * 0.03"], ["s * 0.034", "s * 0.06"], ["s * 0.014", "s * 0.072"], ["s * 0.012", "s * 0.084"], ["s * 0.016", "s * 0.09"], [0, "s * 0.088"]], sides=10)]),
    item("melon", "Melon", "fruit", "-2000-1900", "Egypt, Persia, the Mediterranean", "a melon, green and netted, the size of a head",
         {"s": [0.9, 1.15]}, {"skin": {"pick": ["melon", "melon-yellow"]}}, [
        lathe("body", "skin", [[0, 0], ["s * 0.06", "s * 0.01"], ["s * 0.08", "s * 0.06"], ["s * 0.078", "s * 0.12"], ["s * 0.05", "s * 0.165"], [0, "s * 0.175"]], sides=12)],
         hold={"grip": [0, "s * 0.09", 0], "axis": [0, 1, 0], "face": [1, 0, 0]}),
    item("strawberries", "Strawberries", "fruit", "1300-1900", "Europe", "three strawberries with their green caps",
         {"s": [0.9, 1.1]}, {"skin": "strawberry", "cap": "leaf"}, [
        lathe("berry", "skin", [[0, 0], ["s * 0.009", "s * 0.006"], ["s * 0.011", "s * 0.016"], ["s * 0.006", "s * 0.026"], [0, "s * 0.028"]], sides=8,
              at=[[0, 0, 0], ["s * 0.025", 0, "s * 0.008"], ["-s * 0.02", 0, "s * 0.015"]]),
        lathe("cap", "cap", [["s * 0.004", "s * 0.024"], ["s * 0.012", "s * 0.027"], ["s * 0.002", "s * 0.028"]], sides=6, caps=False, double=True,
              at=[[0, 0, 0], ["s * 0.025", 0, "s * 0.008"], ["-s * 0.02", 0, "s * 0.015"]])]),
    # ---- vegetables
    item("carrot", "Carrot", "vegetable", "900-1900", "Persia, then everywhere", "a carrot: a long orange root tapering to its tip, the green tops cut short",
         {"s": [0.9, 1.15]}, {"skin": "carrot", "top": "leaf"}, [
        lathe("root", "skin", [[0, 0], ["s * 0.006", "s * 0.03"], ["s * 0.012", "s * 0.1"], ["s * 0.016", "s * 0.16"], ["s * 0.014", "s * 0.18"], [0, "s * 0.18"]], sides=8),
        ],
         hold={"grip": [0, "s * 0.12", 0], "axis": [0, 1, 0], "face": [1, 0, 0]}),
    item("turnip", "Turnip", "vegetable", "-1000-1900", "everywhere temperate", "a turnip: a flattened white globe blushing purple at the shoulder, a tap root below",
         {"s": [0.9, 1.15]}, {"skin": "turnip", "shoulder": "turnip-purple", "root": "root", "top": "leaf"}, [
        lathe("body", "skin", [[0, "s * 0.01"], ["s * 0.03", "s * 0.012"], ["s * 0.045", "s * 0.035"], ["s * 0.043", "s * 0.045"]], sides=10),
        lathe("shoulder", "shoulder", [["s * 0.043", "s * 0.045"], ["s * 0.04", "s * 0.055"], ["s * 0.028", "s * 0.066"], ["s * 0.012", "s * 0.07"]], sides=10),
        lathe("root", "root", [[0, 0], ["s * 0.006", "s * 0.006"], ["s * 0.028", "s * 0.012"]], sides=8),
        ]),
    item("onion", "Onion", "vegetable", "-3000-1900", "everywhere", "an onion in its papery brown skin, the neck twisted to a point",
         {"s": [0.9, 1.1]}, {"skin": {"pick": ["onion", "onion", "onion-red"]}}, [
        lathe("bulb", "skin", [[0, 0], ["s * 0.01", "s * 0.002"], ["s * 0.032", "s * 0.02"], ["s * 0.035", "s * 0.04"], ["s * 0.024", "s * 0.06"], ["s * 0.008", "s * 0.072"], ["s * 0.004", "s * 0.09"], [0, "s * 0.1"]], sides=9)]),
    item("garlic", "Garlic", "vegetable", "-3000-1900", "everywhere", "a head of garlic: the cloves' ridges under the white skin, the stalk cut",
         {"s": [0.9, 1.1]}, {"skin": "garlic"}, [
        lathe("head", "skin", [[0, 0], ["s * 0.012", "s * 0.002"], ["s * 0.026", "s * 0.016"], ["s * 0.025", "s * 0.03"], ["s * 0.012", "s * 0.044"], ["s * 0.005", "s * 0.05"], ["s * 0.004", "s * 0.06"]], sides=7, faceted=True)]),
    item("leek", "Leek", "vegetable", "-2000-1900", "Egypt, Europe", "a leek: the white shank below, the flat green leaves fanning above",
         {"s": [0.9, 1.15]}, {"shank": "leek-white", "leaf": "leek-green", "root": "root"}, [
        lathe("shank", "shank", [[0, 0], ["s * 0.012", "s * 0.005"], ["s * 0.014", "s * 0.15"], ["s * 0.012", "s * 0.2"]], sides=7),
        {"id": "leaf", "type": "box", "material": "leaf", "size": [0.002, "s * 0.2", "s * 0.022"], "at": [0, "s * 0.29", 0, 0, 0, -12], "around": {"n": 5, "r": "s * 0.012", "plane": "xz", "span": 300}},
        {"id": "roots", "type": "rod", "material": "root", "from": [0, "s * 0.004", 0], "to": ["s * 0.006", "-s * 0.02", 0], "r": 0.0012, "sides": 3, "around": {"n": 6, "r": 0.004, "plane": "xz"}}],
         hold={"grip": [0, "s * 0.15", 0], "axis": [0, 1, 0], "face": [1, 0, 0]}),
    item("cabbage", "Cabbage", "vegetable", "-500-1900", "Europe", "a cabbage: a pale green head with its darker outer leaves cupping it from below",
         {"s": [0.9, 1.15]}, {"head": "cabbage", "leaf": "cabbage-leaf"}, [
        {"id": "head", "type": "sphere", "material": "head", "r": "s * 0.075", "sides": 8, "at": [0, "s * 0.075", 0]},
        lathe("leaves", "leaf", [["s * 0.03", 0], ["s * 0.085", "s * 0.025"], ["s * 0.1", "s * 0.075"], ["s * 0.095", "s * 0.115"]], sides=9, caps=False, double=True, faceted=True)]),

    item("pumpkin", "Pumpkin", "vegetable", "1550-1900", "the Americas, then Europe", "a pumpkin: a ribbed orange globe, flattened, with a stalk",
         {"s": [0.85, 1.2]}, {"skin": {"pick": ["pumpkin", "pumpkin", "pumpkin-green"]}, "stem": "stem-green"}, [
        lathe("body", "skin", [[0, "s * 0.01"], ["s * 0.08", "s * 0.012"], ["s * 0.13", "s * 0.06"], ["s * 0.135", "s * 0.13"], ["s * 0.09", "s * 0.2"], ["s * 0.03", "s * 0.21"], ["s * 0.028", "s * 0.2"]], sides=12, faceted=True),
        lathe("stalk", "stem", [["s * 0.02", "s * 0.2"], ["s * 0.016", "s * 0.24"], ["s * 0.018", "s * 0.25"]], sides=6)],
         hold={"grip": [0, "s * 0.1", 0], "axis": [0, 1, 0], "face": [1, 0, 0]}),
    item("cucumber", "Cucumber", "vegetable", "-1000-1900", "India, then everywhere", "a cucumber, long and a little bent, dark green",
         {"s": [0.9, 1.15]}, {"skin": "cucumber"}, [
        {"id": "body", "type": "sweep", "material": "skin", "radii": ["s * 0.012", "s * 0.02", "s * 0.021", "s * 0.02", "s * 0.012"], "sides": 8, "seg": 1,
         "path": [[0, 0, 0], ["s * 0.06", "s * 0.006", 0], ["s * 0.12", "s * 0.012", 0], ["s * 0.18", "s * 0.01", 0], ["s * 0.24", "s * 0.002", 0]]}],
         hold={"grip": ["s * 0.12", 0, 0], "axis": [1, 0, 0], "face": [0, 1, 0]}),
    item("beetroot", "Beetroot", "vegetable", "-300-1900", "the Mediterranean, Europe", "a beetroot: a dark red globe, its tap root and red-veined leaves",
         {"s": [0.9, 1.15]}, {"skin": "beet", "leaf": "beet-leaf"}, [
        lathe("body", "skin", [[0, 0], ["s * 0.004", "s * 0.004"], ["s * 0.03", "s * 0.02"], ["s * 0.036", "s * 0.045"], ["s * 0.028", "s * 0.066"], ["s * 0.01", "s * 0.072"]], sides=9),
        ]),
    item("radish", "Radish", "vegetable", "-2000-1900", "everywhere", "a bunch of red radishes, their roots and leaves",
         {"s": [0.9, 1.1]}, {"skin": "radish", "leaf": "leaf"}, [
        lathe("radish", "skin", [[0, 0], ["s * 0.003", "s * 0.003"], ["s * 0.013", "s * 0.012"], ["s * 0.013", "s * 0.024"], ["s * 0.005", "s * 0.03"]], sides=8,
              at=[[0, 0, 0], ["s * 0.028", 0, "s * 0.006"], ["s * 0.012", 0, "-s * 0.024"]]),
        ]),
    item("parsnip", "Parsnip", "vegetable", "-300-1900", "Europe", "a parsnip: a pale tapering root, broad at the shoulder",
         {"s": [0.9, 1.15]}, {"skin": "parsnip", "top": "leaf"}, [
        lathe("root", "skin", [[0, 0], ["s * 0.004", "s * 0.02"], ["s * 0.012", "s * 0.1"], ["s * 0.022", "s * 0.17"], ["s * 0.02", "s * 0.19"], ["s * 0.006", "s * 0.2"]], sides=8),
        ],
         hold={"grip": [0, "s * 0.12", 0], "axis": [0, 1, 0], "face": [1, 0, 0]}),
    item("mushroom", "Mushroom", "vegetable", "everywhere", "everywhere", "a field mushroom: a pale cap, its gills brown beneath, on a short stem",
         {"s": [0.8, 1.2]}, {"cap": "mushroom", "gills": "mushroom-gills", "stem": "mushroom-stem"}, [
        lathe("stem", "stem", [[0, 0], ["s * 0.012", "s * 0.002"], ["s * 0.01", "s * 0.04"], ["s * 0.012", "s * 0.05"]], sides=7),
        lathe("gills", "gills", [["s * 0.012", "s * 0.048"], ["s * 0.045", "s * 0.052"]], sides=10, caps=False, double=True),
        lathe("cap", "cap", [["s * 0.045", "s * 0.052"], ["s * 0.04", "s * 0.066"], ["s * 0.024", "s * 0.078"], [0, "s * 0.082"]], sides=10, caps=False, double=True)],
         hold={"grip": [0, "s * 0.025", 0], "axis": [0, 1, 0], "face": [1, 0, 0]}),
    item("pea-pods", "Pea pods", "vegetable", "-1000-1900", "everywhere", "three pea pods, green and a little bent, their peas swelling them",
         {"s": [0.9, 1.1]}, {"skin": "pea"}, [
        {"id": "pod", "type": "sweep", "material": "skin", "radii": ["s * 0.004", "s * 0.007", "s * 0.007", "s * 0.007", "s * 0.003"], "sides": 6, "seg": 1,
         "path": [[0, 0, 0], ["s * 0.02", "s * 0.003", 0], ["s * 0.04", "s * 0.005", 0], ["s * 0.06", "s * 0.004", 0], ["s * 0.075", 0, 0]],
         "at": [[0, "s * 0.007", 0], ["-s * 0.01", "s * 0.007", "s * 0.02", 15, 0, 0], ["s * 0.005", "s * 0.007", "-s * 0.018", -10, 0, 0]]}],
         hold={"grip": ["s * 0.03", 0, 0], "axis": [1, 0, 0], "face": [0, 1, 0]}),
    item("bean-pods", "Bean pods", "vegetable", "-1000-1900", "everywhere", "broad bean pods, long and lumpy",
         {"s": [0.9, 1.1]}, {"skin": "bean"}, [
        {"id": "pod", "type": "sweep", "material": "skin", "radii": ["s * 0.006", "s * 0.011", "s * 0.01", "s * 0.011", "s * 0.005"], "sides": 6, "seg": 1,
         "path": [[0, 0, 0], ["s * 0.04", "s * 0.004", 0], ["s * 0.08", "s * 0.008", 0], ["s * 0.12", "s * 0.006", 0], ["s * 0.15", 0, 0]],
         "at": [[0, "s * 0.011", 0], ["-s * 0.01", "s * 0.011", "s * 0.028", 12, 0, 0]]}],
         hold={"grip": ["s * 0.07", 0, 0], "axis": [1, 0, 0], "face": [0, 1, 0]}),
    item("tomato", "Tomato", "vegetable", "1600-1900", "the Americas, then the Mediterranean", "a tomato: a red globe, ribbed a little, its green calyx on top",
         {"s": [0.9, 1.1]}, {"skin": "tomato", "cap": "leaf"}, [
        lathe("body", "skin", [[0, "s * 0.004"], ["s * 0.026", "s * 0.004"], ["s * 0.036", "s * 0.022"], ["s * 0.032", "s * 0.048"], ["s * 0.014", "s * 0.06"], [0, "s * 0.058"]], sides=10),
        lathe("calyx", "cap", [["s * 0.004", "s * 0.058"], ["s * 0.018", "s * 0.062"], ["s * 0.003", "s * 0.064"]], sides=5, caps=False, double=True)]),
    item("potatoes", "Potatoes", "vegetable", "1600-1900", "the Andes, then Europe", "three potatoes, lumpy and earthy",
         {"s": [0.9, 1.15]}, {"skin": "potato"}, [
        lathe("potato", "skin", [[0, 0], ["s * 0.02", "s * 0.006"], ["s * 0.026", "s * 0.03"], ["s * 0.022", "s * 0.055"], [0, "s * 0.064"]], sides=7, faceted=True,
              at=[[0, 0, 0, 0, 0, 80], ["s * 0.03", 0, "s * 0.045", 30, 0, 75], ["-s * 0.03", 0, "s * 0.03", -50, 0, 85]], stretch=[1.3, 1, 1])]),
    item("corn", "Ear of maize", "vegetable", "1550-1900", "the Americas, then the Mediterranean", "an ear of maize, its yellow kernels in rows, the husk peeled back",
         {"s": [0.9, 1.1]}, {"kernels": "maize", "husk": "husk"}, [
        lathe("ear", "kernels", [[0, 0], ["s * 0.018", "s * 0.01"], ["s * 0.024", "s * 0.06"], ["s * 0.022", "s * 0.14"], ["s * 0.01", "s * 0.18"], [0, "s * 0.19"]], sides=10, faceted=True),
        {"id": "husk", "type": "plate", "material": "husk", "thick": 0.001, "at": [0, 0, 0, 90, 12, 0],
         "outline": [[0, 0], ["s * 0.03", "s * 0.06"], ["s * 0.02", "s * 0.16"], [0, "s * 0.2"], ["-s * 0.02", "s * 0.16"], ["-s * 0.03", "s * 0.06"]],
         "around": {"n": 3, "r": "s * 0.024", "plane": "xz"}}],
         hold={"grip": [0, "s * 0.08", 0], "axis": [0, 1, 0], "face": [1, 0, 0]}),
    item("marrow", "Marrow", "vegetable", "1600-1900", "Europe", "a marrow: a long striped green gourd",
         {"s": [0.9, 1.15]}, {"skin": "marrow"}, [
        lathe("body", "skin", [[0, 0], ["s * 0.03", "s * 0.01"], ["s * 0.045", "s * 0.08"], ["s * 0.048", "s * 0.18"], ["s * 0.04", "s * 0.26"], ["s * 0.02", "s * 0.3"], [0, "s * 0.31"]], sides=10, faceted=True)],
         hold={"grip": [0, "s * 0.15", 0], "axis": [0, 1, 0], "face": [1, 0, 0]}),
    # ---- the market's other wares (2026-10-02: the stalls are assets now -- items/furniture/market-stall)
    item("bread", "Loaf", "bread", "-3000-1900", "everywhere", "a long loaf, its crust split along the top",
         {"s": [0.9, 1.1]}, {"crust": {"pick": ["crust", "crust-dark"]}}, [
        lathe("loaf", "crust", [[0, 0], ["s * 0.05", "s * 0.006"], ["s * 0.06", "s * 0.035"], ["s * 0.045", "s * 0.065"], [0, "s * 0.075"]], sides=8, stretch=[2.2, 1, 1])],
         hold={"grip": [0, "s * 0.04", 0], "axis": [1, 0, 0], "face": [0, 1, 0]}),
    item("round-loaf", "Round loaf", "bread", "-3000-1900", "everywhere", "a round country loaf, domed",
         {"s": [0.9, 1.15]}, {"crust": {"pick": ["crust", "crust-dark"]}}, [
        lathe("loaf", "crust", [[0, 0], ["s * 0.09", "s * 0.006"], ["s * 0.1", "s * 0.03"], ["s * 0.075", "s * 0.07"], [0, "s * 0.085"]], sides=10)]),
    item("cheese", "Cheese wheel", "dairy", "-1000-1900", "everywhere", "a wheel of hard cheese in its rind",
         {"s": [0.9, 1.1]}, {"rind": {"pick": ["cheese-rind", "cheese-rind-red"]}}, [
        lathe("wheel", "rind", [[0, 0], ["s * 0.16", 0], ["s * 0.17", "s * 0.045"], ["s * 0.16", "s * 0.09"], [0, "s * 0.09"]], sides=12)]),
    item("cheese-wedge", "Wedge of cheese", "dairy", "-1000-1900", "everywhere", "a wedge cut from the wheel",
         {"s": [0.9, 1.1]}, {"cheese": "cheese", "rind": "cheese-rind"}, [
        {"id": "wedge", "type": "plate", "material": "cheese", "thick": "s * 0.09", "at": [0, "s * 0.045", 0, 0, -90, 0],
         "outline": [[0, 0], ["s * 0.16", "s * -0.05"], ["s * 0.16", "s * 0.05"]]}]),
    item("ham", "Ham", "meat", "-500-1900", "everywhere", "a cured ham on its bone, hung by a cord",
         {"s": [0.9, 1.1]}, {"skin": "ham", "bone": "bone"}, [
        lathe("ham", "skin", [[0, 0], ["s * 0.06", "s * 0.02"], ["s * 0.1", "s * 0.1"], ["s * 0.08", "s * 0.2"], ["s * 0.03", "s * 0.26"], [0, "s * 0.27"]], sides=9, stretch=[1, 1, 0.75]),
        {"id": "bone", "type": "rod", "material": "bone", "r": "s * 0.012", "sides": 5, "from": [0, "s * 0.26", 0], "to": [0, "s * 0.32", 0]}],
         hold={"grip": [0, "s * 0.3", 0], "axis": [0, 1, 0], "face": [1, 0, 0]}),
    item("sausages", "String of sausages", "meat", "-500-1900", "everywhere", "a string of four sausages",
         {"s": [0.9, 1.1]}, {"skin": "sausage"}, [
        lathe("link", "skin", [[0, 0], ["s * 0.014", "s * 0.01"], ["s * 0.015", "s * 0.06"], [0, "s * 0.07"]], sides=6,
              at=[[0, 0, 0, 0, 0, -90], ["s * 0.072", 0, 0, 0, 0, -90], ["s * 0.144", 0, 0, 0, 0, -90], ["s * 0.216", 0, 0, 0, 0, -90]])],
         hold={"grip": [0, 0, 0], "axis": [1, 0, 0], "face": [0, 1, 0]}),
    item("fish", "Fish", "fish", "everywhere", "everywhere", "a fresh fish: a herring, a carp, a trout, its tail fanned",
         {"s": [0.8, 1.3]}, {"skin": {"pick": ["fish-silver", "fish-grey", "fish-trout"]}}, [
        lathe("body", "skin", [[0, 0], ["s * 0.02", "s * 0.03"], ["s * 0.025", "s * 0.1"], ["s * 0.01", "s * 0.18"], [0, "s * 0.2"]], sides=7, stretch=[1, 1, 0.45], at=[0, "s * 0.012", 0, 0, 0, -90]),
        {"id": "tail", "type": "plate", "material": "skin", "thick": 0.003, "at": ["s * -0.2", "s * 0.012", 0, 0, 0, 0],
         "outline": [[0, 0], ["s * -0.05", "s * 0.03"], ["s * -0.04", 0], ["s * -0.05", "s * -0.03"]]}],
         hold={"grip": ["s * -0.17", "s * 0.012", 0], "axis": [1, 0, 0], "face": [0, 1, 0]}),
    item("eggs", "Eggs", "dairy", "-3000-1900", "everywhere", "a few hen's eggs",
         {"s": [0.9, 1.1]}, {"shell": {"pick": ["egg-white", "egg-brown"]}}, [
        lathe("egg", "shell", [[0, 0], ["s * 0.018", "s * 0.006"], ["s * 0.021", "s * 0.022"], ["s * 0.015", "s * 0.045"], [0, "s * 0.052"]], sides=7,
              at=[[0, 0, 0, 0, 0, 80], ["s * 0.05", 0, "s * 0.02", 40, 0, 85], ["s * 0.02", 0, "s * -0.045", -30, 0, 82]])]),
])

MATERIALS = {
    "apple-red": "#b8302a", "apple-green": "#8fb54a", "apple-yellow": "#d8c45a", "pear": "#c9c26a", "plum": "#4a2a5a", "plum-yellow": "#d8b84a",
    "cherry-red": "#8a1a22", "grape-purple": "#5a2a62", "grape-green": "#a9c96a", "peach": "#e8a070", "orange": "#e88a2a", "lemon": "#e8d040",
    "fig": "#5a3a5a", "fig-green": "#8aa050", "pomegranate": "#b03a2a", "melon": "#9aa868", "melon-yellow": "#d8c060", "strawberry": "#c8302a",
    "carrot": "#e07a2a", "turnip": "#f0e8d8", "turnip-purple": "#8a4a8a", "root": "#c8b898", "onion": "#c89a5a", "onion-red": "#7a3a58",
    "garlic": "#ece4d8", "leek-white": "#eeeadc", "leek-green": "#4a8a3a", "cabbage": "#a8c47a", "cabbage-leaf": "#6a9a48", "leaf": "#4a8a3a",
    "pumpkin": "#e0802a", "pumpkin-green": "#7a9a48", "cucumber": "#3a7a2a", "beet": "#6a1a3a", "beet-leaf": "#5a7a3a", "radish": "#c8303a",
    "parsnip": "#e8dcb8", "mushroom": "#e0d8c8", "mushroom-gills": "#8a6a58", "mushroom-stem": "#ece6da", "pea": "#6aa848", "bean": "#7aa858",
    "crust": "#b8803e", "crust-dark": "#8a5a28", "cheese": "#f0d070", "cheese-rind": "#d8a840", "cheese-rind-red": "#b8402a",
    "ham": "#a84a3a", "bone": "#e8dcc4", "sausage": "#8a3a2a", "fish-silver": "#a6b0b8", "fish-grey": "#7a8a7a", "fish-trout": "#8a8a5a",
    "egg-white": "#f2ecd8", "egg-brown": "#d8b088",
    "leaf-light": "#6aa848", "vine-leaf": "#5a9a3a", "tomato": "#c8302a", "potato": "#b89a68", "maize": "#e8c040", "husk": "#c8c088", "marrow": "#4a7a3a", "stem": "#6a4a2a", "stem-green": "#6a8a3a",
}


def main():
    for k, v in FOOD.items():
        for i, part in enumerate(LEAVES.get(k, [])):
            v["parts"].append({"id": f"leaf {i + 1}", **part})
            v["materials"].setdefault(part["material"], part["material"])
        write("food/" + k, v)
    mpath = os.path.join(ITEMS, "materials.json")
    lib = json.load(open(mpath))
    added = 0
    for k, v in MATERIALS.items():
        if k not in lib["materials"]:
            lib["materials"][k] = {"pattern": "materials/paint", "palette": [v, v, v, v]}; added += 1
    json.dump(lib, open(mpath, "w"), indent=1, ensure_ascii=False)
    ipath = os.path.join(ROOT, "assets", "index.json")
    index = json.load(open(ipath))
    cats = {c["name"]: c for c in index["categories"]}
    if "Items: food" not in cats:
        pos = index["categories"].index(cats["Items: furniture"]) + 1
        index["categories"].insert(pos, {"name": "Items: food", "kind": "item", "paths": []})
        cats = {c["name"]: c for c in index["categories"]}
    cats["Items: food"]["paths"] = ["items/food/" + k for k in FOOD]
    json.dump(index, open(ipath, "w"), indent=2, ensure_ascii=False)
    print(len(FOOD), "foods,", added, "materials added")


if __name__ == "__main__":
    main()
