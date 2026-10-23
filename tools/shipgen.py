#!/usr/bin/env python3
"""SHIPS AND BOATS (2026-09-30): the vessels of the world up to 1800 as item definitions (assets/items/ships/*.json)
out of reusable COMPONENTS (assets/items/components/: mast, yard, square-sail, lateen-sail, junk-sail, crab-claw-sail,
oar, oars, steering-oar, rudder, figurehead, castle, cabin, outrigger, anchor, cannon, gun-row, ram, shield-row) and the
two primitives items.js gives them: `hull` (a lofted hull: sheer, keel, plan and section lines) and `sail` (a bellied
cloth between corners). Edit this script for the arithmetic, then run it:

    python3 tools/shipgen.py        # writes the JSON files and the catalogue's "Items: ships" category

A ship's frame: the stern at x = 0, the bow at +x, y up from the keel's lowest point, z across (starboard +z).
Every vessel says its `era` and `region`. Materials are roles: planks (the hull), deck, wood (spars, rails), cloth
(the sails), rope, metal."""
import json, os, collections

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ITEMS = os.path.join(ROOT, "assets", "items")


def write(path, doc):
    full = os.path.join(ITEMS, path + ".json")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")


def comp(name, about, params, materials, parts, **extra):
    return {"kind": "item", "name": name, "category": "component", "_about": about, "params": params, "materials": materials,
            "parts": parts, **extra}


# ---- COMPONENTS -----------------------------------------------------------------------------------------------------
COMPONENTS = {}

COMPONENTS["mast"] = comp("Mast", "a mast standing from 0 to h, tapering; `top`: none, a topmast doubled above it (top * h more), or a crow's nest (a cup near the head)",
    {"h": 10, "r": 0.16, "top": "none", "topH": 0.5}, {"wood": "pine"}, [
    {"id": "lower", "type": "rod", "material": "wood", "from": [0, 0, 0], "to": [0, "h", 0], "r0": "r", "r1": "r * 0.62"},
    {"id": "cap", "type": "box", "material": "wood", "size": ["r * 3", "r * 1.2", "r * 2"], "at": [0, "h", 0]},
    {"id": "topmast", "type": "rod", "when": {"top": "topmast"}, "material": "wood", "from": ["-r * 0.9", "h * 0.86", 0], "to": ["-r * 0.9", "h * (1 + topH)", 0], "r0": "r * 0.55", "r1": "r * 0.3"},
    {"id": "top", "type": "box", "when": {"top": "topmast"}, "material": "wood", "size": ["r * 9", "r * 0.6", "r * 9"], "at": [0, "h * 0.9", 0]},
    {"id": "nest", "type": "lathe", "when": {"top": "crowsnest"}, "material": "wood", "caps": False, "double": True, "at": [0, "h * 0.86", 0],
     "profile": [["r * 1.1", 0], ["r * 3.2", 0], ["r * 3.4", "r * 4"]]},
    {"id": "nest floor", "type": "lathe", "when": {"top": "crowsnest"}, "material": "wood", "at": [0, "h * 0.86", 0], "profile": [["r * 3.2", 0], ["r * 3.2", "r * 0.3"]]},
])

COMPONENTS["yard"] = comp("Yard", "a spar l long along x about its middle, tapering to both ends",
    {"l": 8, "r": 0.09}, {"wood": "pine"}, [
    {"id": "arm", "type": "rod", "material": "wood", "from": [0, 0, 0], "to": ["l / 2", 0, 0], "r0": "r", "r1": "r * 0.5", "mirror": "x"},
])

COMPONENTS["square-sail"] = comp("Square sail", "a yard w wide with its sail hung from it, h deep, its foot `foot` of its head, bellied `belly` toward +z (the wind behind it); `set` full or furled (rolled on the yard); turned by its parent so its x lies across the ship",
    {"w": 8, "h": 6, "foot": 0.92, "belly": "w * 0.1", "r": "w * 0.011", "set": "full"}, {"wood": "pine", "cloth": "canvas"}, [
    {"id": "yard", "use": "items/components/yard", "params": {"l": "w * 1.08", "r": "r"}},
    {"id": "cloth", "type": "sail", "when": {"set": "full"}, "material": "cloth", "belly": "belly", "at": [0, "-r * 0.6", 0],
     "corners": [["-w / 2", 0], ["w / 2", 0], ["w * foot / 2", "-h"], ["-w * foot / 2", "-h"]]},
    {"id": "furled", "type": "rod", "when": {"set": "furled"}, "material": "cloth", "from": ["-w * 0.5", "-r * 1.5", 0], "to": ["w * 0.5", "-r * 1.5", 0], "r": "h * 0.03", "sides": 8},
])

COMPONENTS["lateen-sail"] = comp("Lateen sail", "the triangular sail of the Mediterranean and the Indian Ocean: a long yard slung at `tilt` degrees, its tack low and forward (-x), its peak high and aft; the clew hangs below the peak. In the ship's frame as it is (its x fore and aft), bellied to +z",
    {"l": 14, "tilt": 52, "drop": 0.55, "belly": "l * 0.07", "r": "l * 0.009", "set": "full"}, {"wood": "pine", "cloth": "canvas"}, [
    {"id": "yard", "type": "rod", "material": "wood", "from": ["-l * 0.42 * cos(tilt * 0.017453)", "-l * 0.42 * sin(tilt * 0.017453)", 0],
     "to": ["l * 0.58 * cos(tilt * 0.017453)", "l * 0.58 * sin(tilt * 0.017453)", 0], "r0": "r", "r1": "r * 0.7"},
    {"id": "cloth", "type": "sail", "when": {"set": "full"}, "material": "cloth", "belly": "belly", "at": [0, 0, "-r"],
     "corners": [["-l * 0.42 * cos(tilt * 0.017453)", "-l * 0.42 * sin(tilt * 0.017453)"], ["l * 0.58 * cos(tilt * 0.017453)", "l * 0.58 * sin(tilt * 0.017453)"],
                 ["l * 0.58 * cos(tilt * 0.017453) - l * 0.12", "l * 0.58 * sin(tilt * 0.017453) - l * drop"]]},
    {"id": "furled", "type": "rod", "when": {"set": "furled"}, "material": "cloth", "from": ["-l * 0.4 * cos(tilt * 0.017453)", "-l * 0.4 * sin(tilt * 0.017453) - r * 2", 0],
     "to": ["l * 0.56 * cos(tilt * 0.017453)", "l * 0.56 * sin(tilt * 0.017453) - r * 2", 0], "r": "l * 0.018", "sides": 8},
])

COMPONENTS["junk-sail"] = comp("Junk sail", "the Chinese lug sail: a cloth stiffened by battens across it, its head narrower and raked aft, hung from a yard with a boom at its foot; set fore and aft, in the ship's frame as it is",
    {"w": 9, "h": 11, "battens": 5, "belly": "w * 0.05", "r": "w * 0.01"}, {"wood": "pine", "cloth": "sail-tan"}, [
    {"id": "yard", "type": "rod", "material": "wood", "from": ["-w * 0.42", 0, 0], "to": ["w * 0.3", 0, 0], "r": "r"},
    {"id": "cloth", "type": "sail", "material": "cloth", "belly": "belly", "battens": "battens", "battenR": "r * 0.6", "at": [0, "-r", 0],
     "corners": [["-w * 0.4", 0], ["w * 0.28", 0], ["w * 0.5", "-h"], ["-w * 0.5", "-h"]]},
    {"id": "boom", "type": "rod", "material": "wood", "from": ["-w * 0.55", "-h - r", 0], "to": ["w * 0.55", "-h - r", 0], "r": "r"},
])

COMPONENTS["crab-claw-sail"] = comp("Crab-claw sail", "the Oceanic sail: two spars from one tack spreading `spread` degrees apart, the cloth between them; the tack is the origin, the spars rise aft along +x and up",
    {"l": 6, "lift": 62, "spread": 42, "belly": "l * 0.06", "r": "l * 0.012"}, {"wood": "bamboo", "cloth": "matting"}, [
    {"id": "upper", "type": "rod", "material": "wood", "from": [0, 0, 0], "to": ["l * cos(lift * 0.017453)", "l * sin(lift * 0.017453)", 0], "r0": "r", "r1": "r * 0.6"},
    {"id": "lower", "type": "rod", "material": "wood", "from": [0, 0, 0], "to": ["l * cos((lift - spread) * 0.017453)", "l * sin((lift - spread) * 0.017453)", 0], "r0": "r", "r1": "r * 0.6"},
    {"id": "cloth", "type": "sail", "material": "cloth", "belly": "belly", "at": [0, 0, "-r"],
     "corners": [[0, 0], ["l * cos(lift * 0.017453)", "l * sin(lift * 0.017453)"], ["l * 0.82 * cos((lift - spread / 2) * 0.017453)", "l * 0.82 * sin((lift - spread / 2) * 0.017453)"],
                 ["l * cos((lift - spread) * 0.017453)", "l * sin((lift - spread) * 0.017453)"]]},
])

COMPONENTS["oar"] = comp("Oar", "an oar l long along +x from its handle at the origin: a round loom and a flat blade at its end",
    {"l": 4, "r": 0.03, "bladeL": "l * 0.28", "bladeW": 0.15}, {"wood": "ash"}, [
    {"id": "loom", "type": "rod", "material": "wood", "from": [0, 0, 0], "to": ["l - bladeL", 0, 0], "r0": "r", "r1": "r * 0.9"},
    {"id": "blade", "type": "box", "material": "wood", "size": ["bladeL", 0.02, "bladeW"], "at": ["l - bladeL / 2", 0, 0]},
])

COMPONENTS["oars"] = comp("Oars", "a bank of n oars a side, from x = from to x = to at the gunwale's height y and half-breadth z, thrust out and down `dip` degrees, on both sides",
    {"n": 12, "from": 3, "to": 20, "y": 1.6, "z": 2.2, "l": 4.5, "dip": 18, "reach": 0.3}, {"wood": "ash"}, [
    {"id": "oar", "use": "items/components/oar", "params": {"l": "l"}, "along": {"n": "n", "from": ["from", "y", "z * (1 - reach)"], "to": ["to", "y", "z * (1 - reach)"]},
     "at": [0, 0, 0, -90, 0, "-dip"], "mirror": "z"},
])

COMPONENTS["steering-oar"] = comp("Steering oar", "a side rudder: a broad-bladed oar hung down the starboard quarter, its tiller across the ship",
    {"l": 3.2, "r": 0.05, "bladeW": 0.42}, {"wood": "oak"}, [
    {"id": "loom", "type": "rod", "material": "wood", "from": [0, "l * 0.25", 0], "to": [0, "-l * 0.4", 0], "r0": "r", "r1": "r * 0.9"},
    {"id": "blade", "type": "box", "material": "wood", "size": ["bladeW", "l * 0.6", 0.05], "at": [0, "-l * 0.55", 0]},
    {"id": "tiller", "type": "rod", "material": "wood", "from": [0, "l * 0.2", 0], "to": [0, "l * 0.25", "-l * 0.35"], "r": "r * 0.6"},
])

COMPONENTS["rudder"] = comp("Rudder", "a stern-hung rudder: a blade h deep and w wide behind the sternpost (at x = 0, the ship's stern to +x), its tiller running forward over the deck",
    {"h": 3, "w": 0.7, "tiller": 2.5, "thick": 0.09}, {"wood": "oak", "metal": "iron"}, [
    {"id": "blade", "type": "plate", "material": "wood", "thick": "thick", "outline": [[0, 0], ["-w * 0.55", 0], ["-w", "-h * 0.35"], ["-w * 0.8", "-h"], [0, "-h"]]},
    {"id": "pintles", "type": "box", "material": "metal", "size": [0.12, 0.08, "thick + 0.06"], "along": {"n": 3, "from": [0, "-h * 0.1", 0], "to": [0, "-h * 0.9", 0]}},
    {"id": "tiller", "type": "rod", "material": "wood", "from": [0, "0.05", 0], "to": ["tiller", "0.25", 0], "r0": 0.06, "r1": 0.04, "when": "tiller"},
])

COMPONENTS["figurehead"] = comp("Figurehead", "what rises at the stem (or the stern): a dragon's head on a curling neck (the longship's), a swan's neck (the Roman merchantman's stern), a scroll, a lion; s scales it (1 = about 2 m)",
    {"s": 1, "style": "dragon"}, {"wood": "oak", "gilt": "gilt"}, [
    {"id": "dragon neck", "type": "sweep", "when": {"style": "dragon"}, "material": "wood", "path": [[0, 0, 0], ["s * 0.25", "s * 0.7", 0], ["s * 0.35", "s * 1.4", 0], ["s * 0.15", "s * 1.9", 0]], "radii": ["s * 0.24", "s * 0.2", "s * 0.15", "s * 0.13"]},
    {"id": "dragon head", "type": "box", "when": {"style": "dragon"}, "material": "wood", "size": ["s * 0.75", "s * 0.32", "s * 0.28"], "round": "s * 0.06", "at": ["s * 0.45", "s * 2.0", 0, 0, 0, 20]},
    {"id": "dragon jaw", "type": "box", "when": {"style": "dragon"}, "material": "wood", "size": ["s * 0.5", "s * 0.1", "s * 0.22"], "at": ["s * 0.5", "s * 1.8", 0, 0, 0, 35]},
    {"id": "dragon eye", "type": "sphere", "when": {"style": "dragon"}, "material": "gilt", "r": "s * 0.05", "at": ["s * 0.55", "s * 2.12", "s * 0.15"], "mirror": "z"},
    {"id": "dragon crest", "type": "plate", "when": {"style": "dragon"}, "material": "wood", "thick": "s * 0.04", "at": ["s * 0.2", "s * 1.5", 0, 90, 0, 0],
     "outline": [[0, 0], ["s * 0.3", "s * 0.35"], ["s * 0.12", "s * 0.3"], ["s * 0.15", "s * 0.6"], ["s * 0.0", "s * 0.55"]]},
    {"id": "swan neck", "type": "sweep", "when": {"style": "swan"}, "material": "wood", "path": [[0, 0, 0], ["s * 0.15", "s * 0.8", 0], ["s * 0.45", "s * 1.5", 0], ["s * 0.3", "s * 2.0", 0], ["s * -0.1", "s * 2.1", 0]], "radii": ["s * 0.2", "s * 0.16", "s * 0.13", "s * 0.13", "s * 0.1"]},
    {"id": "swan head", "type": "box", "when": {"style": "swan"}, "material": "wood", "size": ["s * 0.45", "s * 0.16", "s * 0.16"], "round": "s * 0.05", "at": ["s * -0.25", "s * 2.05", 0]},
    {"id": "scroll", "type": "sweep", "when": {"style": "scroll"}, "material": "gilt", "path": [[0, 0, 0], ["s * 0.3", "s * 0.5", 0], ["s * 0.5", "s * 0.95", 0], ["s * 0.35", "s * 1.2", 0], ["s * 0.15", "s * 1.05", 0], ["s * 0.28", "s * 0.9", 0]], "radii": ["s * 0.16", "s * 0.13", "s * 0.1", "s * 0.08", "s * 0.06", "s * 0.05"]},
    {"id": "lion body", "type": "box", "when": {"style": "lion"}, "material": "gilt", "size": ["s * 0.5", "s * 0.9", "s * 0.4"], "round": "s * 0.1", "at": ["s * 0.15", "s * 0.55", 0, 0, 0, -20]},
    {"id": "lion head", "type": "sphere", "when": {"style": "lion"}, "material": "gilt", "r": "s * 0.24", "at": ["s * 0.4", "s * 1.15", 0]},
    {"id": "lion mane", "type": "lathe", "when": {"style": "lion"}, "material": "gilt", "at": ["s * 0.32", "s * 1.05", 0, 0, 0, 70], "profile": [["s * 0.3", 0], ["s * 0.33", "s * 0.15"], ["s * 0.2", "s * 0.3"]]},
])

COMPONENTS["castle"] = comp("Castle", "a fighting platform raised on posts: a forecastle or an aftcastle, d long (along x, from its origin forward) and w wide, its floor h up, with a parapet round it (crenellated when `crenels`)",
    {"w": 5, "d": 4, "h": 2.5, "rail": 1.0, "crenels": 1, "posts": 4}, {"wood": "planks", "deck": "deck"}, [
    # (the floor's TOP is at h: the parapet stands on it from there up -- centred on h, its upper half lay inside the
    #  walls' feet, two textures over the same place)
    {"id": "floor", "type": "box", "material": "deck", "size": ["d", 0.12, "w"], "at": ["d / 2", "h - 0.06", 0]},
    {"id": "side", "type": "box", "material": "wood", "size": ["d", "rail", 0.08], "at": ["d / 2", "h + rail / 2", "w / 2 - 0.04"], "mirror": "z"},
    {"id": "end", "type": "box", "material": "wood", "size": [0.08, "rail", "w"], "at": ["d - 0.04", "h + rail / 2", 0]},
    {"id": "crenel side", "type": "box", "when": "crenels", "material": "wood", "size": [0.35, 0.3, 0.08], "along": {"n": "max(2, round(d / 0.8))", "from": [0.3, "h + rail + 0.15", "w / 2 - 0.04"], "to": ["d - 0.3", "h + rail + 0.15", "w / 2 - 0.04"]}, "mirror": "z"},
    {"id": "crenel end", "type": "box", "when": "crenels", "material": "wood", "size": [0.08, 0.3, 0.35], "along": {"n": "max(2, round(w / 0.8))", "from": ["d - 0.04", "h + rail + 0.15", "-w / 2 + 0.3"], "to": ["d - 0.04", "h + rail + 0.15", "w / 2 - 0.3"]}},
    {"id": "post", "type": "rod", "material": "wood", "r": 0.09, "from": [0, 0, 0], "to": [0, "h - 0.12", 0], "when": "posts",
     "at": [["d * 0.12", 0, "w * 0.4"], ["d * 0.88", 0, "w * 0.4"]], "mirror": "z"},
])

COMPONENTS["cabin"] = comp("Cabin", "a deckhouse: d long (from its origin forward), w wide, h high, a flat or pitched roof, windows along its sides and back",
    {"w": 4, "d": 5, "h": 2.2, "roof": "flat", "windows": 2}, {"wood": "planks", "roofm": "planks-tarred", "glass": "#3a4a54"}, [
    {"id": "walls", "type": "box", "material": "wood", "size": ["d", "h", "w"], "at": ["d / 2", "h / 2", 0]},
    {"id": "flat roof", "type": "box", "when": {"roof": "flat"}, "material": "roofm", "size": ["d + 0.3", 0.1, "w + 0.3"], "at": ["d / 2", "h + 0.05", 0]},
    {"id": "pitched roof", "type": "plate", "when": {"roof": "pitched"}, "material": "roofm", "thick": "d + 0.3", "at": ["d / 2", "h", 0, 90, 0, 0],
     "outline": [["-w / 2 - 0.15", 0], ["w / 2 + 0.15", 0], [0, "w * 0.35"]]},
    {"id": "window", "type": "box", "material": "glass", "size": [0.5, 0.5, 0.06], "along": {"n": "windows", "from": ["d * 0.25", "h * 0.6", "w / 2"], "to": ["d * 0.75", "h * 0.6", "w / 2"]}, "mirror": "z"},
    {"id": "stern window", "type": "box", "material": "glass", "size": [0.06, 0.5, 0.5], "along": {"n": "windows", "from": [0, "h * 0.6", "-w * 0.25"], "to": [0, "h * 0.6", "w * 0.25"]}},
])

COMPONENTS["outrigger"] = comp("Outrigger", "a float l long lying `out` to starboard on `booms` booms from the hull (their inboard ends at the origin's height)",
    {"l": 5, "r": 0.22, "out": 2.5, "booms": 2, "boomR": 0.05, "span": 2.4}, {"wood": "pine", "rope": "hemp"}, [
    {"id": "float", "type": "lathe", "material": "wood", "at": ["-l / 2", "-0.3", "out", 0, 0, -90],
     "profile": [[0, 0], ["r * 0.7", "l * 0.12"], ["r", "l * 0.5"], ["r * 0.7", "l * 0.88"], [0, "l"]]},
    {"id": "boom", "type": "rod", "material": "wood", "from": [0, 0, 0], "to": [0, "-0.2", "out"], "r": "boomR", "along": {"n": "booms", "from": ["-span / 2", 0, 0], "to": ["span / 2", 0, 0]}},
    {"id": "lashing", "type": "ring", "material": "rope", "r": "boomR * 1.6", "tube": "boomR * 0.4", "along": {"n": "booms", "from": ["-span / 2", "-0.2", "out"], "to": ["span / 2", "-0.2", "out"]}},
])

COMPONENTS["anchor"] = comp("Anchor", "an anchor h tall hanging by its ring at the origin: a shank, two curved arms with flukes, a wooden stock across the top",
    {"h": 2.2}, {"metal": "iron", "wood": "oak"}, [
    {"id": "ring", "type": "ring", "material": "metal", "r": "h * 0.07", "tube": "h * 0.012", "at": [0, "-h * 0.07", 0, 90, 0, 0]},
    {"id": "shank", "type": "rod", "material": "metal", "from": [0, "-h * 0.12", 0], "to": [0, "-h", 0], "r": "h * 0.02"},
    {"id": "arm", "type": "sweep", "material": "metal", "path": [[0, "-h", 0], ["h * 0.18", "-h * 0.96", 0], ["h * 0.34", "-h * 0.8", 0]], "r": "h * 0.02", "mirror": "x"},
    {"id": "fluke", "type": "plate", "material": "metal", "thick": "h * 0.012", "at": ["h * 0.34", "-h * 0.8", 0], "outline": [[0, 0], ["-h * 0.12", "-h * 0.1"], ["h * 0.02", "-h * 0.16"]], "mirror": "x"},
    {"id": "stock", "type": "box", "material": "wood", "size": ["h * 0.55", "h * 0.045", "h * 0.045"], "at": [0, "-h * 0.2", 0, 90, 0, 0]},
])

COMPONENTS["cannon"] = comp("Cannon", "a ship's gun on its carriage, its muzzle to +x: a bronze or iron barrel l long, the truck carriage under it",
    {"l": 2.4, "bore": 0.11}, {"metal": "iron", "wood": "oak"}, [
    {"id": "barrel", "type": "lathe", "material": "metal", "at": ["-l * 0.4", "bore * 3.2", 0, 0, 0, -90],
     "profile": [["bore * 1.6", 0], ["bore * 1.7", "l * 0.05"], ["bore * 1.5", "l * 0.06"], ["bore * 1.3", "l * 0.55"], ["bore * 1.35", "l * 0.57"], ["bore * 1.05", "l * 0.9"], ["bore * 1.3", "l * 0.96"], ["bore * 1.25", "l"]]},
    {"id": "cascabel", "type": "sphere", "material": "metal", "r": "bore * 0.7", "at": ["-l * 0.47", "bore * 3.2", 0]},
    {"id": "carriage", "type": "box", "material": "wood", "size": ["l * 0.5", "bore * 2.2", "bore * 3"], "at": ["-l * 0.2", "bore * 1.9", 0]},
    {"id": "truck", "type": "lathe", "material": "wood", "at": ["-l * 0.35", "bore * 0.9", "bore * 1.8", 0, 0, 0], "profile": [["bore * 0.9", "-bore * 0.3"], ["bore * 0.9", "bore * 0.3"]], "sides": 10,
     "stretch": [1, 1, 1], "mirror": "z"},
    {"id": "truck fore", "type": "lathe", "material": "wood", "at": ["-l * 0.05", "bore * 0.8", "bore * 1.8", 0, 0, 0], "profile": [["bore * 0.8", "-bore * 0.3"], ["bore * 0.8", "bore * 0.3"]], "sides": 10, "mirror": "z"},
])

COMPONENTS["gun-row"] = comp("Gun row", "a broadside: n gun ports along a side from x = from to x = to at height y in a hull of half-breadth z, each a dark port with a muzzle out of it -- on both sides",
    {"n": 10, "from": 4, "to": 40, "y": 3, "z": 5, "bore": 0.11, "reach": 0.5}, {"metal": "iron", "port": "#1a1612"}, [
    {"id": "port", "type": "box", "material": "port", "size": ["bore * 6", "bore * 5.5", 0.05], "along": {"n": "n", "from": ["from", "y", "z"], "to": ["to", "y", "z"]}, "mirror": "z"},
    {"id": "muzzle", "type": "rod", "material": "metal", "from": [0, 0, 0], "to": [0, 0, "reach"], "r0": "bore * 1.35", "r1": "bore * 1.25",
     "along": {"n": "n", "from": ["from", "y", "z - 0.1"], "to": ["to", "y", "z - 0.1"]}, "mirror": "z"},
])

COMPONENTS["ram"] = comp("Ram", "the bronze beak at a war galley's stem, at the waterline, thrust `l` forward of the origin",
    {"l": 1.6, "h": 0.5}, {"metal": "bronze"}, [
    {"id": "beak", "type": "plate", "material": "metal", "at": [0, 0, 0, 90, 0, 0], "thick": "h", "taper": ["h", "h * 0.6"],
     "outline": [[0, "h * 0.7"], ["l", "h * 0.4"], ["l * 1.02", "-h * 0.1"], ["l * 0.9", "-h * 0.45"], [0, "-h * 0.6"]]},
])

COMPONENTS["shield-row"] = comp("Shield row", "round shields hung overlapping along both gunwales, n a side from x = from to x = to at height y and half-breadth z, faces out",
    {"n": 10, "from": 3, "to": 20, "y": 1.7, "z": 2.3, "w": 0.85}, {}, [
    {"id": "shield", "use": "items/shields/round", "params": {"w": "w"}, "along": {"n": "n", "from": ["from", "y", "z"], "to": ["to", "y", "z"]}, "at": [0, 0, 0, 0, 0, 0], "mirror": "z"},
])

COMPONENTS["bowsprit"] = comp("Bowsprit", "the spar over the stem, l long, `steeve` degrees above the horizontal, from the origin forward",
    {"l": 12, "r": 0.16, "steeve": 22}, {"wood": "pine"}, [
    {"id": "spar", "type": "rod", "material": "wood", "from": [0, 0, 0], "to": ["l * cos(steeve * 0.017453)", "l * sin(steeve * 0.017453)", 0], "r0": "r", "r1": "r * 0.55"},
])

COMPONENTS["awning"] = comp("Awning", "a cloth roof on posts over a deck: d long from the origin forward, w wide, h up",
    {"w": 4, "d": 6, "h": 2}, {"wood": "pine", "cloth": "canvas"}, [
    {"id": "post", "type": "rod", "material": "wood", "r": 0.05, "from": [0, 0, 0], "to": [0, "h", 0], "at": [["d * 0.1", 0, "w * 0.45"], ["d * 0.9", 0, "w * 0.45"]], "mirror": "z"},
    {"id": "cloth", "type": "sail", "material": "cloth", "belly": "-w * 0.05", "at": [0, "h", "-w / 2", 0, -90, 0],
     "corners": [[0, 0], ["d", 0], ["d", "-w"], [0, "-w"]]},
])


# ---- SHIPS ------------------------------------------------------------------------------------------------------------
# helpers: the parts a kind of rig adds
def mast(x, y, h, r=None, top="none", topH=0.5):
    return {"id": f"mast {x}", "use": "items/components/mast", "params": {"h": h, "r": r or round(h * 0.014, 3), "top": top, "topH": topH}, "at": [x, y, 0]}


def square(x, y, w, h, belly=None, foot=0.92, set_="set"):
    p = {"w": w, "h": h, "foot": foot, "set": set_}
    if belly is not None:
        p["belly"] = belly
    return {"id": f"square sail {x} {y}", "use": "items/components/square-sail", "params": p, "at": [x, y, 0, 90, 0, 0]}


def lateen(x, y, l, tilt=52, drop=0.55, set_="set"):
    return {"id": f"lateen {x}", "use": "items/components/lateen-sail", "params": {"l": l, "tilt": tilt, "drop": drop, "set": set_}, "at": [x, y, 0]}


def stay(a, b, r=0.02):
    return {"id": f"stay {a[0]}-{b[0]}", "type": "rod", "material": "rope", "from": a, "to": b, "r": r, "sides": 4}


def hull(L, B, D, **kw):
    return {"id": "hull", "type": "hull", "material": "planks", "length": L, "beam": B, "depth": D, **kw}


def ship(name, era, region, about, params, materials, parts, **extra):
    mats = {"planks": "planks", "deck": "deck", "wood": "pine", "cloth": "canvas", "rope": "hemp", "metal": "iron"}
    mats.update(materials)
    ps = {"set": {"pick": ["full", "full", "furled"]}}
    ps.update(params)
    return {"kind": "item", "name": name, "category": "ship", "era": era, "region": region, "_about": about, "params": ps, "materials": mats, "parts": parts, **extra}


SHIPS = {}

SHIPS["dugout"] = ship("Dugout canoe", "-8000-1900", "everywhere", "a log hollowed out: the first boat, and a river's and a lagoon's boat still -- blunt ends, a round bottom, two thwarts",
    {"L": [4.2, 6], "B": 0.72, "D": 0.48}, {"planks": "oak-grey", "wood": "oak-grey"}, [
    hull("L", "B", "D", fullness=0.4, double=True, stations=16, sides=5, plan=[[0, 0.25], [0.15, 0.8], [0.5, 1], [0.85, 0.8], [1, 0.25]],
         keel=[[0, "D * 0.25"], [0.15, 0], [0.85, 0], [1, "D * 0.25"]], sheer=[[0, "D * 1.05"], [0.5, "D"], [1, "D * 1.05"]],
         thwarts={"n": 2, "y": "D * 0.7", "w": 0.18, "from": 0.3, "to": 0.7}),
])

SHIPS["reed-boat"] = ship("Reed boat", "-4000-1900", "Egypt, Mesopotamia, Lake Titicaca", "bundles of reed lashed into a boat, both ends swept up into points -- the Nile's papyrus skiff, the totora boat of Titicaca",
    {"L": [4, 6], "B": "L * 0.28", "D": "B * 0.45"}, {"planks": "reed", "wood": "reed", "rope": "hemp"}, [
    hull("L", "B", "D", fullness=0.45, stations=20, sides=6, plan=[[0, 0.02], [0.2, 0.75], [0.5, 1], [0.8, 0.75], [1, 0.02]],
         keel=[[0, "D * 1.3"], [0.1, "D * 0.3"], [0.3, 0], [0.7, 0], [0.9, "D * 0.3"], [1, "D * 1.3"]],
         sheer=[[0, "D * 2.1"], [0.15, "D * 1.2"], [0.5, "D"], [0.85, "D * 1.2"], [1, "D * 2.1"]], rail="B * 0.13", railMaterial="wood"),
    {"id": "lashing", "type": "ring", "material": "rope", "r": "B * 0.5", "tube": 0.02, "along": {"n": 6, "from": ["L * 0.2", "D * 0.65", 0], "to": ["L * 0.8", "D * 0.65", 0]}, "at": [0, 0, 0, 90, 0, 0]},
])

SHIPS["egyptian-boat"] = ship("Egyptian river boat", "-2500--500", "Egypt", "the Nile's timber boat of the pharaohs: a papyriform hull with both ends rising, a broad low sail on a single mast, two steering oars over the stern quarters and a shelter of a deckhouse",
    {"L": [12, 16], "B": "L * 0.24", "D": "B * 0.42", "mastH": "L * 0.7"}, {"planks": "planks-pine", "cloth": "linen", "wood": "pine"}, [
    hull("L", "B", "D", fullness=0.5, plan=[[0, 0.02], [0.15, 0.6], [0.5, 1], [0.85, 0.6], [1, 0.02]],
         keel=[[0, "D * 0.9"], [0.08, "D * 0.25"], [0.25, 0], [0.75, 0], [0.92, "D * 0.25"], [1, "D * 0.9"]],
         sheer=[[0, "D * 1.9"], [0.1, "D * 1.15"], [0.5, "D"], [0.9, "D * 1.15"], [1, "D * 1.9"]],
         deck=[{"y": "D * 0.88", "from": 0.08, "to": 0.92}], rail=0.06),
    mast("L * 0.48", "D * 0.88", "mastH", r=0.14),
    square("L * 0.48", "D * 0.88 + mastH * 0.93", "L * 0.55", "mastH * 0.5", foot=1.0),
    {"id": "boom", "use": "items/components/yard", "params": {"l": "L * 0.58", "r": 0.06}, "at": ["L * 0.48", "D * 0.88 + mastH * 0.42", 0, 90, 0, 0]},
    {"id": "cabin", "use": "items/components/cabin", "params": {"w": "B * 0.6", "d": "L * 0.18", "h": 1.5, "windows": 1}, "materials": {"wood": "reed", "roofm": "reed"}, "at": ["L * 0.2", "D * 0.88", 0]},
    {"id": "steering", "use": "items/components/steering-oar", "params": {"l": "L * 0.28", "bladeW": 0.5}, "at": ["L * 0.06", "D * 1.3", "B * 0.4", 0, 0, 12], "mirror": "z"},
    stay(["L * 0.48", "D * 0.88 + mastH", 0], ["L * 0.95", "D * 1.5", 0]), stay(["L * 0.48", "D * 0.88 + mastH", 0], ["L * 0.06", "D * 1.5", 0]),
])

SHIPS["trireme"] = ship("Trireme", "-550--300", "Greece, Phoenicia, Rome", "the warship of Salamis: long, low and light, a bronze ram at the waterline, three banks of oars a side (drawn as two), a single square sail furled for battle, the stern rising in its curled ornament",
    {"L": [35, 38], "B": "L * 0.15", "D": "B * 0.42", "mastH": "L * 0.3"}, {"planks": "planks-pine", "wood": "pine"}, [
    hull("L", "B", "D", fullness=0.3, plan=[[0, 0.02], [0.12, 0.55], [0.4, 1], [0.7, 0.95], [0.93, 0.35], [1, 0.02]],
         keel=[[0, "D * 0.45"], [0.1, 0], [0.92, 0], [1, "D * 0.2"]], sheer=[[0, "D * 2.6"], [0.06, "D * 1.3"], [0.15, "D * 1.05"], [0.5, "D"], [0.9, "D * 1.05"], [1, "D * 1.15"]],
         deck=[{"y": "D * 0.9", "from": 0.06, "to": 0.94}], rail=0.06, keelBeam=[0.22, 0.28]),
    {"id": "outrigger beam", "type": "box", "material": "wood", "size": ["L * 0.72", 0.15, 0.4], "at": ["L * 0.5", "D * 0.95", "B * 0.5"], "mirror": "z"},
    {"id": "oars upper", "use": "items/components/oars", "params": {"n": 27, "from": "L * 0.16", "to": "L * 0.84", "y": "D * 0.95", "z": "B * 0.55", "l": "L * 0.12", "dip": 20, "reach": 0.25}},
    {"id": "oars lower", "use": "items/components/oars", "params": {"n": 27, "from": "L * 0.17", "to": "L * 0.85", "y": "D * 0.65", "z": "B * 0.5", "l": "L * 0.11", "dip": 14, "reach": 0.3}},
    {"id": "ram", "use": "items/components/ram", "params": {"l": "L * 0.06", "h": "D * 0.35"}, "materials": {"metal": "bronze"}, "at": ["L * 0.99", "D * 0.3", 0]},
    mast("L * 0.45", "D * 0.9", "mastH", r=0.16),
    square("L * 0.45", "D * 0.9 + mastH * 0.92", "L * 0.28", "mastH * 0.55", set_="furled"),
    {"id": "steering", "use": "items/components/steering-oar", "params": {"l": "D * 2.6", "bladeW": 0.45}, "at": ["L * 0.06", "D * 1.2", "B * 0.42", 0, 0, 10], "mirror": "z"},
    {"id": "eye", "type": "lathe", "material": "gilt", "at": ["L * 0.88", "D * 0.85", "B * 0.44", 0, 0, 0], "profile": [[0, 0], [0.35, 0], [0.35, 0.04]], "sides": 12, "mirror": "z", "double": True},
])

SHIPS["roman-merchant"] = ship("Roman merchantman", "-100-400", "the Mediterranean", "the corbita of the grain fleets: a deep round hull, a broad square mainsail with a small artemon raked over the bow, a swan's neck over the stern, two steering oars, the master's cabin aft",
    {"L": [22, 28], "B": "L * 0.32", "D": "B * 0.5", "mastH": "L * 0.5"}, {"planks": "planks", "wood": "pine"}, [
    hull("L", "B", "D", fullness=0.55, plan=[[0, 0.02], [0.1, 0.55], [0.35, 0.98], [0.6, 1], [0.85, 0.7], [1, 0.02]],
         keel=[[0, "D * 0.5"], [0.1, 0], [0.9, 0], [1, "D * 0.3"]], sheer=[[0, "D * 1.35"], [0.12, "D * 1.08"], [0.5, "D"], [0.9, "D * 1.05"], [1, "D * 1.2"]],
         deck=[{"y": "D * 0.9", "from": 0.05, "to": 0.95}], rail=0.08, keelBeam=[0.3, 0.35], tumblehome=0.08),
    mast("L * 0.5", "D * 0.9", "mastH", r=0.2, top="crowsnest"),
    square("L * 0.5", "D * 0.9 + mastH * 0.9", "L * 0.5", "mastH * 0.6"),
    {"id": "artemon", "use": "items/components/mast", "params": {"h": "mastH * 0.4", "r": 0.12}, "at": ["L * 0.9", "D * 1.0", 0, 0, 0, -40]},
    square("L * 0.9 + mastH * 0.25", "D * 1.0 + mastH * 0.3", "L * 0.18", "mastH * 0.25"),
    {"id": "swan", "use": "items/components/figurehead", "params": {"style": "swan", "s": "D * 0.45"}, "at": [0.3, "D * 1.3", 0, 180, 0, 0]},
    {"id": "cabin", "use": "items/components/cabin", "params": {"w": "B * 0.6", "d": "L * 0.16", "h": 2.0, "windows": 2}, "at": ["L * 0.08", "D * 0.9", 0]},
    {"id": "steering", "use": "items/components/steering-oar", "params": {"l": "D * 1.6", "bladeW": 0.5}, "at": ["L * 0.12", "D * 1.15", "B * 0.45", 0, 0, 10], "mirror": "z"},
    stay(["L * 0.5", "D * 0.9 + mastH", 0], ["L * 0.96", "D * 1.3", 0]), stay(["L * 0.5", "D * 0.9 + mastH", 0], ["L * 0.05", "D * 1.35", 0]),
])

SHIPS["longship"] = ship("Longship", "800-1100", "Scandinavia", "the Viking longship: a clinker shell on a keel, the stem and stern sweeping up into a dragon's head and a curled tail, shields along the gunwales, a single striped square sail, sixteen oars a side and a side rudder on the starboard quarter",
    {"L": [20, 28], "B": "L * 0.2", "D": "B * 0.38", "mastH": "L * 0.45", "oarsN": "round(L * 0.65)"}, {"planks": {"pick": ["planks", "planks-tarred"]}, "wood": "pine", "cloth": {"pick": ["sail-striped", "canvas"]}}, [
    hull("L", "B", "D", fullness=0.35, double=True, stations=32, sides=7, plan=[[0, 0.02], [0.1, 0.45], [0.35, 0.95], [0.5, 1], [0.65, 0.95], [0.9, 0.45], [1, 0.02]],
         keel=[[0, "D * 0.9"], [0.08, "D * 0.15"], [0.2, 0], [0.8, 0], [0.92, "D * 0.15"], [1, "D * 0.9"]],
         sheer=[[0, "D * 2.2"], [0.06, "D * 1.5"], [0.15, "D * 1.12"], [0.5, "D"], [0.85, "D * 1.12"], [0.94, "D * 1.5"], [1, "D * 2.2"]],
         rail=0.06, keelBeam=[0.18, 0.3], postRise="D * 0.2", thwarts={"n": "oarsN", "y": "D * 0.55", "w": 0.22, "from": 0.16, "to": 0.84}, ribs={"n": 14, "w": 0.06}),
    {"id": "dragon", "use": "items/components/figurehead", "params": {"style": "dragon", "s": "D * 0.7"}, "at": ["L * 0.99", "D * 2.3", 0]},
    {"id": "tail", "use": "items/components/figurehead", "params": {"style": "scroll", "s": "D * 0.6"}, "at": [0.1, "D * 2.3", 0, 180, 0, 0]},
    {"id": "shields", "use": "items/components/shield-row", "params": {"n": "oarsN", "from": "L * 0.16", "to": "L * 0.84", "y": "D * 1.02", "z": "B * 0.5 - 0.02", "w": "B * 0.17"}},
    {"id": "oars", "use": "items/components/oars", "params": {"n": "oarsN", "from": "L * 0.17", "to": "L * 0.83", "y": "D * 0.82", "z": "B * 0.5", "l": "L * 0.2", "dip": 16, "reach": 0.28}},
    mast("L * 0.48", "D * 0.15", "mastH + D * 0.15", r=0.18),
    square("L * 0.48", "D * 0.3 + mastH * 0.94", "L * 0.42", "mastH * 0.62", belly="L * 0.05"),
    {"id": "steering", "use": "items/components/steering-oar", "params": {"l": "D * 2.2", "bladeW": 0.5}, "at": ["L * 0.1", "D * 1.05", "B * 0.5", 0, 0, 8]},
    stay(["L * 0.48", "D * 0.3 + mastH", 0], ["L * 0.96", "D * 1.6", 0]), stay(["L * 0.48", "D * 0.3 + mastH", 0], ["L * 0.05", "D * 1.6", 0]),
])

SHIPS["knarr"] = ship("Knarr", "800-1200", "Scandinavia, the North Atlantic", "the Norsemen's cargo ship, the one that reached Iceland, Greenland and Vinland: broader and deeper than the longship, half-decked at bow and stern with an open hold between, one square sail and a few oars for harbour work",
    {"L": [14, 18], "B": "L * 0.3", "D": "B * 0.45", "mastH": "L * 0.6"}, {"planks": {"pick": ["planks", "planks-tarred"]}, "wood": "pine"}, [
    hull("L", "B", "D", fullness=0.5, double=True, plan=[[0, 0.02], [0.1, 0.5], [0.4, 1], [0.6, 1], [0.9, 0.5], [1, 0.02]],
         keel=[[0, "D * 0.6"], [0.1, 0], [0.9, 0], [1, "D * 0.6"]], sheer=[[0, "D * 1.6"], [0.1, "D * 1.15"], [0.5, "D"], [0.9, "D * 1.15"], [1, "D * 1.6"]],
         rail=0.07, keelBeam=[0.2, 0.3], postRise="D * 0.15", deck=[{"y": "D * 0.75", "from": 0.05, "to": 0.28}, {"y": "D * 0.75", "from": 0.72, "to": 0.95}], ribs={"n": 10, "w": 0.07}),
    {"id": "oars", "use": "items/components/oars", "params": {"n": 3, "from": "L * 0.1", "to": "L * 0.22", "y": "D * 0.9", "z": "B * 0.5", "l": "L * 0.25", "dip": 16, "reach": 0.3}},
    {"id": "cargo", "type": "lathe", "material": "oak", "at": ["L * 0.5", "D * 0.15", 0], "profile": [[0.3, 0], [0.4, 0.5], [0.3, 1.0]], "sides": 12, "along": {"n": 4, "from": ["-L * 0.12", 0, "-B * 0.18"], "to": ["L * 0.12", 0, "B * 0.18"]}},
    mast("L * 0.45", "D * 0.15", "mastH", r=0.17),
    square("L * 0.45", "D * 0.15 + mastH * 0.94", "L * 0.55", "mastH * 0.6", belly="L * 0.06"),
    {"id": "steering", "use": "items/components/steering-oar", "params": {"l": "D * 2", "bladeW": 0.5}, "at": ["L * 0.1", "D * 1.1", "B * 0.5", 0, 0, 8]},
    stay(["L * 0.45", "D * 0.15 + mastH", 0], ["L * 0.96", "D * 1.5", 0]), stay(["L * 0.45", "D * 0.15 + mastH", 0], ["L * 0.05", "D * 1.5", 0]),
])

SHIPS["cog"] = ship("Cog", "1200-1450", "the Hanseatic north", "the Hansa's cog: a flat bottom, straight raked stem and sternpost, high clinker sides, a stern rudder on the sternpost, one great square sail, a castle raised over the stern and a smaller over the bow",
    {"L": [20, 26], "B": "L * 0.31", "D": "B * 0.55", "mastH": "L * 0.85"}, {"planks": "planks", "wood": "pine"}, [
    hull("L", "B", "D", fullness=0.8, plan=[[0, 0.06], [0.12, 0.6], [0.4, 1], [0.6, 1], [0.88, 0.6], [1, 0.05]],
         keel=[[0, "D * 0.45"], [0.12, 0], [0.88, 0], [1, "D * 0.45"]], sheer=[[0, "D * 1.15"], [0.5, "D"], [1, "D * 1.2"]],
         deck=[{"y": "D * 0.85", "from": 0.04, "to": 0.96}], rail=0.09, keelBeam=[0.3, 0.3], postRise="D * 0.05"),
    {"id": "aftcastle", "use": "items/components/castle", "params": {"w": "B * 0.9", "d": "L * 0.22", "h": "D * 0.5", "rail": 1.1, "posts": 1}, "at": ["L * 0.02", "D * 0.85", 0]},
    {"id": "forecastle", "use": "items/components/castle", "params": {"w": "B * 0.6", "d": "L * 0.1", "h": "D * 0.35", "rail": 0.9, "posts": 1}, "at": ["L * 0.86", "D * 0.85", 0]},
    {"id": "rudder", "use": "items/components/rudder", "params": {"h": "D * 1.1", "w": "B * 0.09", "tiller": "L * 0.12"}, "at": [0, "D * 1.0", 0]},
    mast("L * 0.5", "D * 0.85", "mastH", r=0.24, top="crowsnest"),
    square("L * 0.5", "D * 0.85 + mastH * 0.86", "L * 0.55", "mastH * 0.58", belly="L * 0.07"),
    {"id": "anchor", "use": "items/components/anchor", "params": {"h": "D * 0.5"}, "at": ["L * 0.9", "D * 1.05", "B * 0.5"]},
    stay(["L * 0.5", "D * 0.85 + mastH", 0], ["L * 0.97", "D * 1.35", 0]), stay(["L * 0.5", "D * 0.85 + mastH", 0], ["L * 0.03", "D * 1.7", 0]),
])

SHIPS["carrack"] = ship("Carrack", "1450-1600", "Portugal, Spain, Genoa, England", "the ocean ship of the discoveries -- the Santa María, the Mary Rose: a deep round hull with tumblehome, a forecastle jutting over the stem and an aftcastle in two tiers, three masts -- square sails fore and main, a lateen mizzen -- and a bowsprit",
    {"L": [28, 36], "B": "L * 0.3", "D": "B * 0.6", "mastH": "L * 0.8"}, {"planks": "planks", "wood": "pine"}, [
    hull("L", "B", "D", fullness=0.55, tumblehome=0.15, plan=[[0, 0.2], [0.12, 0.7], [0.4, 1], [0.6, 1], [0.85, 0.7], [1, 0.03]],
         keel=[[0, "D * 0.3"], [0.1, 0], [0.9, 0], [1, "D * 0.45"]], sheer=[[0, "D * 1.15"], [0.5, "D"], [1, "D * 1.25"]],
         deck=[{"y": "D * 0.82", "from": 0.03, "to": 0.97}], rail=0.1, keelBeam=[0.35, 0.35]),
    {"id": "aftcastle", "use": "items/components/castle", "params": {"w": "B * 0.9", "d": "L * 0.3", "h": "D * 0.45", "rail": 1.0, "crenels": 0, "posts": 0}, "at": ["L * 0.02", "D * 0.82", 0]},
    {"id": "poop", "use": "items/components/castle", "params": {"w": "B * 0.75", "d": "L * 0.15", "h": "D * 0.4", "rail": 0.9, "crenels": 0, "posts": 0}, "at": ["L * 0.02", "D * 1.27", 0]},
    {"id": "aftcastle wall", "type": "box", "material": "planks", "size": ["L * 0.3", "D * 0.45", 0.1], "at": ["L * 0.17", "D * 1.05", "B * 0.45"], "mirror": "z"},
    {"id": "poop wall", "type": "box", "material": "planks", "size": ["L * 0.15", "D * 0.4", 0.1], "at": ["L * 0.095", "D * 1.47", "B * 0.37"], "mirror": "z"},
    {"id": "stern wall", "type": "box", "material": "planks", "size": [0.1, "D * 0.85", "B * 0.9"], "at": ["L * 0.02", "D * 1.25", 0]},
    {"id": "forecastle", "use": "items/components/castle", "params": {"w": "B * 0.7", "d": "L * 0.18", "h": "D * 0.4", "rail": 1.0, "crenels": 0, "posts": 0}, "at": ["L * 0.84", "D * 0.9", 0]},
    {"id": "forecastle wall", "type": "box", "material": "planks", "size": ["L * 0.18", "D * 0.4", 0.1], "at": ["L * 0.93", "D * 1.1", "B * 0.35"], "mirror": "z"},
    {"id": "rudder", "use": "items/components/rudder", "params": {"h": "D * 1.0", "w": "B * 0.08", "tiller": "L * 0.1"}, "at": [0, "D * 0.85", 0]},
    mast("L * 0.5", "D * 0.82", "mastH", r=0.3, top="topmast", topH=0.45),
    square("L * 0.5", "D * 0.82 + mastH * 0.85", "L * 0.55", "mastH * 0.5", belly="L * 0.07"),
    square("L * 0.5", "D * 0.82 + mastH * 1.4", "L * 0.28", "mastH * 0.3", belly="L * 0.03"),
    mast("L * 0.85", "D * 1.3", "mastH * 0.65", r=0.22, top="topmast", topH=0.4),
    square("L * 0.85", "D * 1.3 + mastH * 0.58", "L * 0.38", "mastH * 0.36", belly="L * 0.05"),
    mast("L * 0.15", "D * 1.67", "mastH * 0.5", r=0.18),
    lateen("L * 0.15", "D * 1.67 + mastH * 0.4", "L * 0.42", tilt=48, drop=0.5),
    {"id": "bowsprit", "use": "items/components/bowsprit", "params": {"l": "L * 0.35", "r": 0.2, "steeve": 28}, "at": ["L * 0.97", "D * 1.3", 0]},
    {"id": "anchor", "use": "items/components/anchor", "params": {"h": "D * 0.45"}, "at": ["L * 0.85", "D * 1.0", "B * 0.5"]},
    stay(["L * 0.5", "D * 0.82 + mastH * 1.45", 0], ["L * 0.97", "D * 1.35", 0]), stay(["L * 0.85", "D * 1.3 + mastH * 0.65", 0], ["L * 1.25", "D * 1.45", 0]),
    stay(["L * 0.5", "D * 0.82 + mastH", 0], ["L * 0.1", "D * 2.05", 0]),
])

SHIPS["caravel"] = ship("Caravel", "1440-1550", "Portugal, Spain", "the caravel of the African coast and the Atlantic islands: small, shallow and quick, lateen sails on two or three masts, a low aftcastle, a stern rudder",
    {"L": [18, 24], "B": "L * 0.28", "D": "B * 0.5", "mastH": "L * 0.75", "masts": {"pick": [2, 3]}}, {"planks": "planks", "wood": "pine"}, [
    hull("L", "B", "D", fullness=0.5, tumblehome=0.08, plan=[[0, 0.18], [0.15, 0.7], [0.45, 1], [0.7, 0.9], [0.9, 0.5], [1, 0.03]],
         keel=[[0, "D * 0.25"], [0.1, 0], [0.9, 0], [1, "D * 0.4"]], sheer=[[0, "D * 1.15"], [0.5, "D"], [1, "D * 1.2"]],
         deck=[{"y": "D * 0.82", "from": 0.03, "to": 0.97}], rail=0.08, keelBeam=[0.28, 0.3]),
    {"id": "aftcastle", "use": "items/components/castle", "params": {"w": "B * 0.85", "d": "L * 0.25", "h": "D * 0.35", "rail": 0.9, "crenels": 0, "posts": 0}, "at": ["L * 0.02", "D * 0.82", 0]},
    {"id": "aftcastle wall", "type": "box", "material": "planks", "size": ["L * 0.25", "D * 0.35", 0.08], "at": ["L * 0.145", "D * 1.0", "B * 0.42"], "mirror": "z"},
    {"id": "stern wall", "type": "box", "material": "planks", "size": [0.08, "D * 0.35", "B * 0.85"], "at": ["L * 0.02", "D * 1.0", 0]},
    {"id": "rudder", "use": "items/components/rudder", "params": {"h": "D * 0.95", "w": "B * 0.08", "tiller": "L * 0.1"}, "at": [0, "D * 0.85", 0]},
    mast("L * 0.55", "D * 0.82", "mastH", r=0.22),
    lateen("L * 0.55", "D * 0.82 + mastH * 0.9", "L * 0.8", tilt=50, drop=0.55),
    mast("L * 0.22", "D * 1.17", "mastH * 0.7", r=0.16),
    lateen("L * 0.22", "D * 1.17 + mastH * 0.62", "L * 0.55", tilt=52, drop=0.5),
    {"id": "foremast", "use": "items/components/mast", "when": {"masts": 3}, "params": {"h": "mastH * 0.5", "r": 0.13}, "at": ["L * 0.85", "D * 0.82", 0]},
    {"id": "fore lateen", "use": "items/components/lateen-sail", "when": {"masts": 3}, "params": {"l": "L * 0.4", "tilt": 52, "drop": 0.5, "set": "set"}, "at": ["L * 0.85", "D * 0.82 + mastH * 0.45", 0]},
    stay(["L * 0.55", "D * 0.82 + mastH", 0], ["L * 0.97", "D * 1.3", 0]),
])

SHIPS["galleon"] = ship("Galleon", "1550-1650", "Spain, England, the Netherlands", "the galleon of the Armada and the treasure fleets: long and lower than the carrack, a beakhead under the bowsprit, a towering stern in tiers, marked tumblehome, two gun decks, square sails on fore and main with topsails and lateens on mizzen and bonaventure",
    {"L": [40, 48], "B": "L * 0.26", "D": "B * 0.62", "mastH": "L * 0.7"}, {"planks": "planks", "wood": "pine", "trim": "gilt"}, [
    hull("L", "B", "D", fullness=0.55, tumblehome=0.28, plan=[[0, 0.25], [0.1, 0.65], [0.35, 1], [0.6, 0.97], [0.85, 0.6], [1, 0.05]],
         keel=[[0, "D * 0.25"], [0.08, 0], [0.9, 0], [1, "D * 0.3"]], sheer=[[0, "D * 1.1"], [0.4, "D"], [1, "D * 1.1"]],
         deck=[{"y": "D * 0.85", "from": 0.03, "to": 0.97}], rail=0.1, keelBeam=[0.4, 0.4]),
    {"id": "guns lower", "use": "items/components/gun-row", "params": {"n": 12, "from": "L * 0.12", "to": "L * 0.86", "y": "D * 0.5", "z": "B * 0.49", "bore": 0.12}},
    {"id": "guns upper", "use": "items/components/gun-row", "params": {"n": 11, "from": "L * 0.14", "to": "L * 0.84", "y": "D * 0.75", "z": "B * 0.46", "bore": 0.1}},
    {"id": "quarterdeck", "use": "items/components/castle", "params": {"w": "B * 0.88", "d": "L * 0.35", "h": "D * 0.4", "rail": 1.0, "crenels": 0, "posts": 0}, "at": ["L * 0.02", "D * 0.85", 0]},
    {"id": "quarterdeck wall", "type": "box", "material": "planks", "size": ["L * 0.35", "D * 0.4", 0.1], "at": ["L * 0.195", "D * 1.05", "B * 0.44"], "mirror": "z"},
    {"id": "poop", "use": "items/components/castle", "params": {"w": "B * 0.7", "d": "L * 0.17", "h": "D * 0.38", "rail": 0.9, "crenels": 0, "posts": 0}, "at": ["L * 0.02", "D * 1.25", 0]},
    {"id": "poop wall", "type": "box", "material": "planks", "size": ["L * 0.17", "D * 0.38", 0.1], "at": ["L * 0.105", "D * 1.44", "B * 0.35"], "mirror": "z"},
    {"id": "stern", "use": "items/components/cabin", "params": {"w": "B * 0.7", "d": "L * 0.04", "h": "D * 0.75", "windows": 4}, "at": ["L * 0.0", "D * 0.85", 0]},
    {"id": "stern trim", "type": "box", "material": "trim", "size": [0.08, 0.2, "B * 0.7"], "along": {"n": 3, "from": [0.0, "D * 1.0", 0], "to": [0.0, "D * 1.55", 0]}},
    {"id": "forecastle", "use": "items/components/castle", "params": {"w": "B * 0.7", "d": "L * 0.14", "h": "D * 0.3", "rail": 0.9, "crenels": 0, "posts": 0}, "at": ["L * 0.8", "D * 0.9", 0]},
    {"id": "beakhead", "type": "plate", "material": "planks", "thick": "B * 0.12", "at": ["L", "D * 0.75", 0, 90, 0, 0], "outline": [[0, 0], ["L * 0.1", "D * 0.12"], ["L * 0.1", "D * 0.2"], [0, "D * 0.45"]]},
    {"id": "rudder", "use": "items/components/rudder", "params": {"h": "D * 1.0", "w": "B * 0.07", "tiller": 0}, "at": [0, "D * 0.85", 0]},
    mast("L * 0.48", "D * 0.85", "mastH", r=0.34, top="topmast", topH=0.5),
    square("L * 0.48", "D * 0.85 + mastH * 0.85", "L * 0.5", "mastH * 0.45", belly="L * 0.06"),
    square("L * 0.48", "D * 0.85 + mastH * 1.42", "L * 0.28", "mastH * 0.32", belly="L * 0.03"),
    mast("L * 0.78", "D * 1.2", "mastH * 0.75", r=0.26, top="topmast", topH=0.5),
    square("L * 0.78", "D * 1.2 + mastH * 0.64", "L * 0.38", "mastH * 0.34", belly="L * 0.05"),
    square("L * 0.78", "D * 1.2 + mastH * 1.05", "L * 0.2", "mastH * 0.24", belly="L * 0.02"),
    mast("L * 0.22", "D * 1.63", "mastH * 0.5", r=0.2),
    lateen("L * 0.22", "D * 1.63 + mastH * 0.4", "L * 0.38", tilt=50, drop=0.5),
    mast("L * 0.07", "D * 1.63", "mastH * 0.35", r=0.15),
    lateen("L * 0.07", "D * 1.63 + mastH * 0.28", "L * 0.25", tilt=50, drop=0.5),
    {"id": "bowsprit", "use": "items/components/bowsprit", "params": {"l": "L * 0.35", "r": 0.22, "steeve": 25}, "at": ["L * 0.98", "D * 1.15", 0]},
    square("L * 0.98 + L * 0.2", "D * 1.15 + L * 0.09", "L * 0.2", "mastH * 0.18", belly="L * 0.02"),
    {"id": "lantern", "type": "lathe", "material": "trim", "at": ["L * 0.01", "D * 1.63 + 0.9", 0], "profile": [[0.2, 0], [0.32, 0.2], [0.32, 0.7], [0.15, 0.95], [0, 1.05]]},
    stay(["L * 0.48", "D * 0.85 + mastH * 1.5", 0], ["L * 0.98", "D * 1.25", 0]), stay(["L * 0.78", "D * 1.2 + mastH * 1.12", 0], ["L * 1.3", "D * 1.28", 0]),
    stay(["L * 0.48", "D * 0.85 + mastH", 0], ["L * 0.1", "D * 2.0", 0]),
])

SHIPS["galley"] = ship("Galley", "1300-1750", "the Mediterranean", "the war galley of Lepanto and the corsairs: very long and low, a spur at the bow, twenty-five great oars a side on their outrigger, two lateen masts, guns on the bow platform and an awning over the stern where the captain sat",
    {"L": [40, 48], "B": "L * 0.13", "D": "B * 0.4", "mastH": "L * 0.42"}, {"planks": "planks", "wood": "pine", "cloth": {"pick": ["canvas", "sail-striped"]}}, [
    hull("L", "B", "D", fullness=0.4, plan=[[0, 0.15], [0.1, 0.6], [0.35, 1], [0.7, 0.95], [0.93, 0.4], [1, 0.03]],
         keel=[[0, "D * 0.35"], [0.08, 0], [0.92, 0], [1, "D * 0.2"]], sheer=[[0, "D * 1.3"], [0.15, "D * 1.05"], [0.5, "D"], [0.9, "D * 1.05"], [1, "D * 1.15"]],
         deck=[{"y": "D * 0.9", "from": 0.04, "to": 0.96}], rail=0.06, keelBeam=[0.25, 0.3]),
    {"id": "outrigger", "type": "box", "material": "wood", "size": ["L * 0.7", 0.18, 0.5], "at": ["L * 0.5", "D * 0.95", "B * 0.62"], "mirror": "z"},
    {"id": "oars", "use": "items/components/oars", "params": {"n": 25, "from": "L * 0.16", "to": "L * 0.85", "y": "D * 0.98", "z": "B * 0.75", "l": "L * 0.23", "dip": 20, "reach": 0.3}},
    {"id": "spur", "type": "rod", "material": "wood", "from": ["L * 0.97", "D * 1.1", 0], "to": ["L * 1.12", "D * 1.25", 0], "r0": 0.18, "r1": 0.08},
    {"id": "bow gun", "use": "items/components/cannon", "params": {"l": 2.6, "bore": 0.13}, "materials": {"metal": "bronze"}, "at": ["L * 0.9", "D * 0.9", 0]},
    {"id": "awning", "use": "items/components/awning", "params": {"w": "B * 0.9", "d": "L * 0.18", "h": 2.2}, "at": ["L * 0.03", "D * 0.9", 0]},
    mast("L * 0.55", "D * 0.9", "mastH", r=0.24),
    lateen("L * 0.55", "D * 0.9 + mastH * 0.9", "L * 0.75", tilt=55, drop=0.5),
    mast("L * 0.25", "D * 0.9", "mastH * 0.75", r=0.18),
    lateen("L * 0.25", "D * 0.9 + mastH * 0.66", "L * 0.5", tilt=55, drop=0.5),
    {"id": "rudder", "use": "items/components/rudder", "params": {"h": "D * 1.1", "w": "B * 0.1", "tiller": "L * 0.06"}, "at": [0, "D * 1.0", 0]},
])

SHIPS["dhow"] = ship("Dhow", "800-1900", "Arabia, the Persian Gulf, East Africa, India", "the trading dhow of the monsoon: a sharp raked stem, a square transom stern with a cabin, and great lateen sails on a mainmast and a mizzen",
    {"L": [18, 26], "B": "L * 0.27", "D": "B * 0.55", "mastH": "L * 0.65"}, {"planks": "planks-pine", "wood": "pine"}, [
    hull("L", "B", "D", fullness=0.45, plan=[[0, 0.3], [0.15, 0.75], [0.4, 1], [0.65, 0.95], [0.9, 0.45], [1, 0.03]],
         keel=[[0, "D * 0.2"], [0.1, 0], [0.85, 0], [1, "D * 0.7"]], sheer=[[0, "D * 1.15"], [0.5, "D"], [1, "D * 1.35"]],
         deck=[{"y": "D * 0.85", "from": 0.03, "to": 0.97}], rail=0.08, keelBeam=[0.28, 0.3]),
    {"id": "cabin", "use": "items/components/cabin", "params": {"w": "B * 0.85", "d": "L * 0.18", "h": 1.8, "windows": 2}, "at": ["L * 0.02", "D * 0.85", 0]},
    mast("L * 0.55", "D * 0.85", "mastH", r=0.24),
    lateen("L * 0.55", "D * 0.85 + mastH * 0.92", "L * 0.95", tilt=45, drop=0.5),
    mast("L * 0.2", "D * 0.85", "mastH * 0.6", r=0.16),
    lateen("L * 0.2", "D * 0.85 + mastH * 0.55", "L * 0.5", tilt=48, drop=0.5),
    {"id": "rudder", "use": "items/components/rudder", "params": {"h": "D * 1.1", "w": "B * 0.1", "tiller": "L * 0.1"}, "at": [0, "D * 1.0", 0]},
    stay(["L * 0.55", "D * 0.85 + mastH", 0], ["L * 0.97", "D * 1.4", 0]),
])

SHIPS["junk"] = ship("Junk", "1200-1900", "China, South-East Asia", "the sea-going junk: a flat-bottomed hull with a blunt bow and a high stern, bulkheads inside, a great stern rudder, and battened lug sails on three masts",
    {"L": [28, 40], "B": "L * 0.26", "D": "B * 0.5", "mastH": "L * 0.75"}, {"planks": "planks", "wood": "pine", "cloth": "sail-tan", "trim": "lacquer-red"}, [
    hull("L", "B", "D", fullness=0.85, plan=[[0, 0.35], [0.15, 0.8], [0.45, 1], [0.75, 0.95], [1, 0.45]],
         keel=[[0, "D * 0.5"], [0.15, 0], [0.85, 0], [1, "D * 0.3"]], sheer=[[0, "D * 1.7"], [0.25, "D * 1.1"], [0.5, "D"], [1, "D * 1.05"]],
         deck=[{"y": "D * 0.85", "from": 0.03, "to": 0.99}], rail=0.1, keelBeam=[0.3, 0.2]),
    {"id": "poop", "use": "items/components/cabin", "params": {"w": "B * 0.9", "d": "L * 0.22", "h": "D * 0.55", "windows": 3}, "materials": {"wood": "planks", "roofm": "trim"}, "at": ["L * 0.02", "D * 0.85", 0]},
    {"id": "rudder", "use": "items/components/rudder", "params": {"h": "D * 1.4", "w": "B * 0.16", "tiller": "L * 0.15", "thick": 0.12}, "at": [0, "D * 1.2", 0]},
    mast("L * 0.55", "D * 0.85", "mastH", r=0.3),
    {"id": "main sail", "use": "items/components/junk-sail", "params": {"w": "L * 0.3", "h": "mastH * 0.8", "battens": 6}, "at": ["L * 0.55", "D * 0.85 + mastH * 0.92", 0]},
    mast("L * 0.82", "D * 0.85", "mastH * 0.6", r=0.2),
    {"id": "fore sail", "use": "items/components/junk-sail", "params": {"w": "L * 0.2", "h": "mastH * 0.48", "battens": 4}, "at": ["L * 0.82", "D * 0.85 + mastH * 0.56", 0]},
    mast("L * 0.2", "D * 0.85 + D * 0.55", "mastH * 0.45", r=0.16),
    {"id": "mizzen sail", "use": "items/components/junk-sail", "params": {"w": "L * 0.14", "h": "mastH * 0.34", "battens": 3}, "at": ["L * 0.2", "D * 1.4 + mastH * 0.42", 0]},
    {"id": "eye", "type": "lathe", "material": "trim", "at": ["L * 0.9", "D * 0.9", "B * 0.46", 0, 0, 0], "profile": [[0, 0], [0.3, 0], [0.3, 0.04]], "sides": 12, "mirror": "z", "double": True},
])

SHIPS["sampan"] = ship("Sampan", "1000-1900", "China, South-East Asia", "the river and harbour boat of the East: flat-bottomed and blunt, an arched matting shelter amidships, sculled by a yuloh over the stern",
    {"L": [5, 7], "B": "L * 0.27", "D": "B * 0.4"}, {"planks": "planks-pine", "wood": "bamboo", "cloth": "matting"}, [
    hull("L", "B", "D", fullness=0.85, double=True, stations=16, sides=5, plan=[[0, 0.45], [0.2, 0.85], [0.5, 1], [0.8, 0.85], [1, 0.4]],
         keel=[[0, "D * 0.4"], [0.15, 0], [0.85, 0], [1, "D * 0.35"]], sheer=[[0, "D * 1.2"], [0.5, "D"], [1, "D * 1.15"]], rail=0.05,
         thwarts={"n": 2, "y": "D * 0.6", "w": 0.2, "from": 0.2, "to": 0.4}, deck=[{"y": "D * 0.35", "from": 0.1, "to": 0.9}]),
    {"id": "shelter", "type": "lathe", "material": "cloth", "double": True, "caps": False, "at": ["L * 0.65", "D * 0.4", 0, 0, 0, -90], "sides": 14,
     "profile": [["B * 0.48", 0], ["B * 0.48", "L * 0.3"]]},
    {"id": "hoop", "type": "ring", "material": "wood", "r": "B * 0.49", "tube": 0.02, "at": ["L * 0.5", "D * 0.4", 0, 0, 0, 90], "along": {"n": 4, "from": [0, 0, 0], "to": ["L * 0.3", 0, 0]}},
    {"id": "yuloh", "use": "items/components/oar", "params": {"l": "L * 0.6", "r": 0.035, "bladeW": 0.2}, "at": ["L * 0.08", "D * 1.1", 0, 180, 0, 25]},
])

SHIPS["outrigger-canoe"] = ship("Outrigger canoe", "-1000-1900", "Polynesia, Micronesia, Melanesia", "the Oceanic canoe: a narrow dugout hull with washstrakes, a float held out on two booms, a crab-claw sail on a raked mast",
    {"L": [7, 10], "B": "L * 0.1", "D": "B * 0.75", "mastH": "L * 0.5"}, {"planks": "oak-grey", "wood": "bamboo", "cloth": "matting", "rope": "hemp"}, [
    hull("L", "B", "D", fullness=0.45, double=True, stations=20, sides=5, plan=[[0, 0.02], [0.15, 0.7], [0.5, 1], [0.85, 0.7], [1, 0.02]],
         keel=[[0, "D * 0.5"], [0.12, 0], [0.88, 0], [1, "D * 0.5"]], sheer=[[0, "D * 1.5"], [0.15, "D * 1.05"], [0.5, "D"], [0.85, "D * 1.05"], [1, "D * 1.5"]],
         rail=0.04, thwarts={"n": 3, "y": "D * 0.7", "w": 0.15, "from": 0.25, "to": 0.75}),
    {"id": "outrigger", "use": "items/components/outrigger", "params": {"l": "L * 0.6", "r": "B * 0.3", "out": "L * 0.3", "span": "L * 0.35"}, "at": ["L * 0.5", "D * 0.85", 0]},
    {"id": "mast", "type": "rod", "material": "wood", "from": ["L * 0.55", "D * 0.3", 0], "to": ["L * 0.62", "D * 0.3 + mastH", 0], "r0": 0.06, "r1": 0.04},
    {"id": "sail", "use": "items/components/crab-claw-sail", "params": {"l": "mastH * 1.15", "lift": 65, "spread": 40}, "at": ["L * 0.62", "D * 0.4", 0]},
])

SHIPS["voyaging-canoe"] = ship("Voyaging canoe", "800-1800", "Polynesia", "the double-hulled canoe that settled the Pacific: two hulls under one platform with a shelter on it, two crab-claw sails, steered with a great paddle",
    {"L": [15, 20], "B": "L * 0.09", "D": "B * 0.9", "gap": "L * 0.22", "mastH": "L * 0.55"}, {"planks": "oak-grey", "wood": "bamboo", "cloth": "matting", "deck": "bamboo"}, [
    {**hull("L", "B", "D", fullness=0.45, stations=20, sides=5, plan=[[0, 0.02], [0.15, 0.7], [0.5, 1], [0.85, 0.7], [1, 0.02]],
            keel=[[0, "D * 0.5"], [0.12, 0], [0.88, 0], [1, "D * 0.5"]], sheer=[[0, "D * 1.6"], [0.15, "D * 1.05"], [0.5, "D"], [0.85, "D * 1.05"], [1, "D * 1.6"]],
            deck=[{"y": "D * 0.85", "from": 0.1, "to": 0.9}], rail=0.05), "at": [0, 0, "gap / 2"], "mirror": "z"},
    {"id": "platform", "type": "box", "material": "deck", "size": ["L * 0.5", 0.08, "gap + B * 0.6"], "at": ["L * 0.5", "D * 1.0", 0]},
    {"id": "beam", "type": "rod", "material": "wood", "from": [0, 0, "-gap / 2 - B * 0.3"], "to": [0, 0, "gap / 2 + B * 0.3"], "r": 0.07, "along": {"n": 4, "from": ["L * 0.28", "D * 0.95", 0], "to": ["L * 0.72", "D * 0.95", 0]}},
    {"id": "shelter", "use": "items/components/cabin", "params": {"w": "gap * 0.5", "d": "L * 0.16", "h": 1.4, "roof": "pitched", "windows": 0}, "materials": {"wood": "matting", "roofm": "matting"}, "at": ["L * 0.42", "D * 1.04", 0]},
    {"id": "mast", "type": "rod", "material": "wood", "from": ["L * 0.66", "D * 1.04", 0], "to": ["L * 0.7", "D * 1.04 + mastH", 0], "r0": 0.08, "r1": 0.05},
    {"id": "sail", "use": "items/components/crab-claw-sail", "params": {"l": "mastH * 1.1", "lift": 66, "spread": 40}, "at": ["L * 0.7", "D * 1.1", 0]},
    {"id": "mast aft", "type": "rod", "material": "wood", "from": ["L * 0.3", "D * 1.04", 0], "to": ["L * 0.34", "D * 1.04 + mastH * 0.8", 0], "r0": 0.07, "r1": 0.045},
    {"id": "sail aft", "use": "items/components/crab-claw-sail", "params": {"l": "mastH * 0.9", "lift": 66, "spread": 40}, "at": ["L * 0.34", "D * 1.1", 0]},
    {"id": "steering paddle", "use": "items/components/steering-oar", "params": {"l": "D * 2.5", "bladeW": 0.4}, "at": ["L * 0.05", "D * 1.1", "gap / 2", 0, 0, 15]},
])

SHIPS["gondola"] = ship("Gondola", "1500-1900", "Venice", "the gondola: long, narrow and black, its keel rockered so it turns on a point, the iron ferro at the prow and the curl at the stern, rowed standing by one oar on a forcola on the starboard quarter, a felze cabin for the passengers",
    {"L": [10.5, 11.5], "B": 1.42, "D": 0.62}, {"planks": "lacquer-black", "wood": "lacquer-black", "metal": "iron", "cloth": "lacquer-black"}, [
    hull("L", "B", "D", fullness=0.5, double=True, stations=30, sides=5, plan=[[0, 0.02], [0.12, 0.55], [0.4, 1], [0.6, 1], [0.88, 0.55], [1, 0.02]],
         keel=[[0, "D * 0.9"], [0.1, "D * 0.3"], [0.3, "D * 0.05"], [0.5, 0], [0.7, "D * 0.05"], [0.9, "D * 0.3"], [1, "D * 0.9"]],
         sheer=[[0, "D * 1.7"], [0.1, "D * 1.25"], [0.5, "D"], [0.9, "D * 1.25"], [1, "D * 1.75"]], rail=0.04, deck=[{"y": "D * 0.45", "from": 0.1, "to": 0.9}],
         thwarts={"n": 1, "y": "D * 0.75", "w": 0.4, "from": 0.45, "to": 0.45}),
    {"id": "ferro", "type": "plate", "material": "metal", "thick": 0.03, "at": ["L * 0.99", "D * 1.7", 0], "outline": [[0, 0], [0.25, 0.1], [0.2, 0.5], [0.35, 0.55], [0.15, 0.85], [-0.1, 0.9], [-0.05, 0.4], [-0.15, 0.1]]},
    {"id": "risso", "type": "sweep", "material": "metal", "path": [[0.05, "D * 1.7", 0], [-0.1, "D * 1.9", 0], [0.1, "D * 2.1", 0]], "r": 0.03},
    {"id": "felze", "use": "items/components/cabin", "params": {"w": "B * 0.8", "d": "L * 0.14", "h": 1.1, "windows": 1}, "materials": {"wood": "cloth", "roofm": "cloth"}, "at": ["L * 0.42", "D * 0.45", 0]},
    {"id": "forcola", "type": "sweep", "material": "wood", "path": [["L * 0.2", "D * 1.2", "B * 0.5"], ["L * 0.2", "D * 1.7", "B * 0.55"], ["L * 0.18", "D * 2.0", "B * 0.62"]], "radii": [0.06, 0.05, 0.03]},
    {"id": "oar", "use": "items/components/oar", "params": {"l": 4.2, "r": 0.03, "bladeW": 0.14}, "at": ["L * 0.13", "D * 2.05", "B * 0.3", -30, 0, -18]},
])

SHIPS["birchbark-canoe"] = ship("Birchbark canoe", "-1000-1900", "North America", "the canoe of the northern forests: birch bark sewn over cedar ribs and gunwales, its ends rising, three thwarts, light enough to carry",
    {"L": [4.5, 6], "B": "L * 0.18", "D": "B * 0.48"}, {"planks": "birch", "wood": "cedar"}, [
    hull("L", "B", "D", fullness=0.4, double=True, stations=20, sides=5, plan=[[0, 0.02], [0.15, 0.65], [0.5, 1], [0.85, 0.65], [1, 0.02]],
         keel=[[0, "D * 0.6"], [0.12, "D * 0.1"], [0.3, 0], [0.7, 0], [0.88, "D * 0.1"], [1, "D * 0.6"]], sheer=[[0, "D * 1.6"], [0.12, "D * 1.1"], [0.5, "D"], [0.88, "D * 1.1"], [1, "D * 1.6"]],
         rail=0.035, thwarts={"n": 3, "y": "D * 0.85", "w": 0.08, "from": 0.25, "to": 0.75, "thick": 0.025}, ribs={"n": 16, "w": 0.04}),
])

SHIPS["kayak"] = ship("Kayak", "-2000-1900", "the Arctic: Inuit, Aleut", "the hunter's kayak: sealskin stretched over a driftwood frame, decked over but for the round cockpit, low and narrow, a double paddle",
    {"L": [5, 6], "B": 0.56, "D": 0.3}, {"planks": "hide", "deck": "hide", "wood": "ash"}, [
    hull("L", "B", "D", fullness=0.35, stations=24, sides=4, plan=[[0, 0.02], [0.2, 0.6], [0.5, 1], [0.8, 0.6], [1, 0.02]],
         keel=[[0, "D * 0.5"], [0.15, 0], [0.85, 0], [1, "D * 0.5"]], sheer=[[0, "D * 1.25"], [0.5, "D"], [1, "D * 1.3"]], deck=[{"y": "D * 0.98", "from": 0.02, "to": 0.98}]),
    {"id": "coaming", "type": "lathe", "material": "wood", "caps": False, "double": True, "at": ["L * 0.45", "D * 0.95", 0], "sides": 14, "profile": [[0.26, 0], [0.27, 0.1]], "stretch": [1.7, 1, 1]},
    {"id": "paddle", "use": "items/components/oar", "params": {"l": 2.4, "r": 0.02, "bladeL": 0.5, "bladeW": 0.14}, "at": ["L * 0.45", "D * 1.3", "-1.2", -90, 0, 0]},
])

SHIPS["umiak"] = ship("Umiak", "-1000-1900", "the Arctic: Inuit", "the open skin boat of the Arctic for a family or a whaling crew: walrus hide over a lashed frame, broad and flat, rowed and paddled",
    {"L": [8, 10], "B": "L * 0.22", "D": "B * 0.45"}, {"planks": "hide", "wood": "ash"}, [
    hull("L", "B", "D", fullness=0.65, double=True, stations=20, sides=5, plan=[[0, 0.3], [0.2, 0.8], [0.5, 1], [0.8, 0.8], [1, 0.15]],
         keel=[[0, "D * 0.3"], [0.15, 0], [0.85, 0], [1, "D * 0.4"]], sheer=[[0, "D * 1.15"], [0.5, "D"], [1, "D * 1.25"]], rail=0.04,
         thwarts={"n": 5, "y": "D * 0.6", "w": 0.15, "from": 0.15, "to": 0.85}, ribs={"n": 12, "w": 0.05}),
    {"id": "oars", "use": "items/components/oars", "params": {"n": 4, "from": "L * 0.25", "to": "L * 0.75", "y": "D * 1.0", "z": "B * 0.5", "l": "L * 0.35", "dip": 18, "reach": 0.3}},
])

SHIPS["coracle"] = ship("Coracle", "-500-1900", "Wales, Ireland, Iraq, India", "the one-man basket boat: hide or tarred cloth over a woven frame, round, paddled from the bow",
    {"L": [1.5, 1.8], "B": "L * 0.92", "D": "L * 0.3"}, {"planks": "hide", "wood": "ash"}, [
    hull("L", "B", "D", fullness=0.45, double=True, stations=16, sides=6, plan=[[0, 0.05], [0.15, 0.75], [0.5, 1], [0.85, 0.75], [1, 0.05]],
         keel=[[0, "D * 0.35"], [0.2, 0], [0.8, 0], [1, "D * 0.35"]], sheer=[[0, "D * 1.05"], [0.5, "D"], [1, "D * 1.05"]], rail=0.03,
         thwarts={"n": 1, "y": "D * 0.6", "w": 0.15, "from": 0.5, "to": 0.5}, ribs={"n": 7, "w": 0.03}),
])

SHIPS["fishing-boat"] = ship("Fishing boat", "1000-1900", "the coasts of Europe", "the village's boat: a clinker-built open boat with a small mast and a lugsail, thwarts for the rowers, a rudder on the sternpost, the nets in the bottom",
    {"L": [6, 8], "B": "L * 0.34", "D": "B * 0.42", "mastH": "L * 0.7"}, {"planks": {"pick": ["planks", "planks-tarred"]}, "wood": "oak", "cloth": {"pick": ["canvas", "sail-tan"]}}, [
    hull("L", "B", "D", fullness=0.45, double=True, stations=20, sides=6, plan=[[0, 0.3], [0.15, 0.75], [0.45, 1], [0.8, 0.75], [1, 0.03]],
         keel=[[0, "D * 0.25"], [0.1, 0], [0.9, 0], [1, "D * 0.35"]], sheer=[[0, "D * 1.15"], [0.5, "D"], [1, "D * 1.3"]], rail=0.05, keelBeam=[0.1, 0.15],
         thwarts={"n": 3, "y": "D * 0.62", "w": 0.22, "from": 0.25, "to": 0.75}, ribs={"n": 8, "w": 0.05}),
    mast("L * 0.62", "D * 0.15", "mastH", r=0.07),
    square("L * 0.62", "D * 0.15 + mastH * 0.92", "L * 0.45", "mastH * 0.55", belly="L * 0.04", foot=0.85),
    {"id": "rudder", "use": "items/components/rudder", "params": {"h": "D * 1.0", "w": "B * 0.12", "tiller": "L * 0.15", "thick": 0.04}, "at": [0, "D * 1.05", 0]},
    {"id": "oars", "use": "items/components/oars", "params": {"n": 2, "from": "L * 0.35", "to": "L * 0.5", "y": "D * 1.0", "z": "B * 0.5", "l": "L * 0.45", "dip": 18, "reach": 0.3}},
    {"id": "net", "type": "box", "material": "hemp", "size": ["L * 0.2", "D * 0.25", "B * 0.5"], "round": 0.1, "at": ["L * 0.15", "D * 0.3", 0]},
])

SHIPS["skiff"] = ship("Skiff", "1200-1900", "everywhere", "a rowing boat: a transom stern, three thwarts, a pair of oars",
    {"L": [3.8, 5], "B": "L * 0.34", "D": "B * 0.4"}, {"planks": "planks", "wood": "oak"}, [
    hull("L", "B", "D", fullness=0.5, double=True, stations=16, sides=5, plan=[[0, 0.42], [0.2, 0.85], [0.5, 1], [0.8, 0.7], [1, 0.03]],
         keel=[[0, "D * 0.2"], [0.15, 0], [0.85, 0], [1, "D * 0.4"]], sheer=[[0, "D * 1.05"], [0.5, "D"], [1, "D * 1.25"]], rail=0.04,
         thwarts={"n": 3, "y": "D * 0.6", "w": 0.2, "from": 0.2, "to": 0.75}, ribs={"n": 7, "w": 0.04}),
    {"id": "oars", "use": "items/components/oars", "params": {"n": 1, "from": "L * 0.5", "to": "L * 0.5", "y": "D * 0.98", "z": "B * 0.5", "l": "L * 0.6", "dip": 15, "reach": 0.3}},
])

SHIPS["fluyt"] = ship("Fluyt", "1600-1750", "the Netherlands", "the Dutch fluyt that carried the Baltic trade: a capacious hull narrowing steeply at the deck (to dodge the Sound dues), a round stern, plain rigging on three masts with few hands",
    {"L": [28, 34], "B": "L * 0.24", "D": "B * 0.7", "mastH": "L * 0.75"}, {"planks": "planks", "wood": "pine"}, [
    hull("L", "B", "D", fullness=0.6, tumblehome=0.42, plan=[[0, 0.12], [0.1, 0.6], [0.35, 1], [0.65, 1], [0.9, 0.55], [1, 0.03]],
         keel=[[0, "D * 0.2"], [0.08, 0], [0.92, 0], [1, "D * 0.3"]], sheer=[[0, "D * 1.2"], [0.5, "D"], [1, "D * 1.1"]],
         deck=[{"y": "D * 0.85", "from": 0.03, "to": 0.97}], rail=0.1, keelBeam=[0.35, 0.35]),
    {"id": "poop", "use": "items/components/cabin", "params": {"w": "B * 0.5", "d": "L * 0.2", "h": "D * 0.35", "windows": 2}, "at": ["L * 0.02", "D * 0.85", 0]},
    {"id": "rudder", "use": "items/components/rudder", "params": {"h": "D * 1.0", "w": "B * 0.08", "tiller": "L * 0.1"}, "at": [0, "D * 0.9", 0]},
    mast("L * 0.5", "D * 0.85", "mastH", r=0.3, top="topmast", topH=0.5),
    square("L * 0.5", "D * 0.85 + mastH * 0.85", "L * 0.45", "mastH * 0.45", belly="L * 0.05"),
    square("L * 0.5", "D * 0.85 + mastH * 1.42", "L * 0.26", "mastH * 0.32", belly="L * 0.03"),
    mast("L * 0.82", "D * 0.85", "mastH * 0.8", r=0.24, top="topmast", topH=0.5),
    square("L * 0.82", "D * 0.85 + mastH * 0.68", "L * 0.36", "mastH * 0.36", belly="L * 0.04"),
    square("L * 0.82", "D * 0.85 + mastH * 1.14", "L * 0.2", "mastH * 0.25", belly="L * 0.02"),
    mast("L * 0.18", "D * 1.2", "mastH * 0.55", r=0.18),
    lateen("L * 0.18", "D * 1.2 + mastH * 0.45", "L * 0.35", tilt=48, drop=0.5),
    {"id": "bowsprit", "use": "items/components/bowsprit", "params": {"l": "L * 0.3", "r": 0.2, "steeve": 28}, "at": ["L * 0.98", "D * 1.05", 0]},
    stay(["L * 0.5", "D * 0.85 + mastH * 1.5", 0], ["L * 0.98", "D * 1.1", 0]), stay(["L * 0.82", "D * 0.85 + mastH * 1.2", 0], ["L * 1.25", "D * 1.19", 0]),
])

SHIPS["xebec"] = ship("Xebec", "1650-1800", "the Barbary coast, Spain, France", "the corsairs' xebec: a fast lateen-rigged hull with a long overhanging stern, three masts, the foremast raked forward, oars for a calm",
    {"L": [30, 38], "B": "L * 0.24", "D": "B * 0.42", "mastH": "L * 0.6"}, {"planks": "planks", "wood": "pine"}, [
    hull("L", "B", "D", fullness=0.4, plan=[[0, 0.15], [0.12, 0.65], [0.4, 1], [0.7, 0.9], [0.95, 0.35], [1, 0.03]],
         keel=[[0, "D * 0.4"], [0.1, 0], [0.9, 0], [1, "D * 0.35"]], sheer=[[0, "D * 1.3"], [0.4, "D"], [1, "D * 1.15"]],
         deck=[{"y": "D * 0.85", "from": 0.03, "to": 0.97}], rail=0.08, keelBeam=[0.3, 0.3]),
    {"id": "stern overhang", "type": "box", "material": "planks", "size": ["L * 0.1", 0.15, "B * 0.7"], "at": ["-L * 0.04", "D * 1.28", 0]},
    {"id": "guns", "use": "items/components/gun-row", "params": {"n": 9, "from": "L * 0.2", "to": "L * 0.8", "y": "D * 0.95", "z": "B * 0.48", "bore": 0.08, "reach": 0.4}},
    mast("L * 0.5", "D * 0.85", "mastH", r=0.26),
    lateen("L * 0.5", "D * 0.85 + mastH * 0.92", "L * 0.85", tilt=50, drop=0.55),
    {"id": "foremast", "use": "items/components/mast", "params": {"h": "mastH * 0.8", "r": 0.2}, "at": ["L * 0.82", "D * 0.85", 0, 0, 0, -15]},
    lateen("L * 0.82 + mastH * 0.2", "D * 0.85 + mastH * 0.72", "L * 0.6", tilt=50, drop=0.55),
    mast("L * 0.15", "D * 0.85", "mastH * 0.6", r=0.16),
    lateen("L * 0.15", "D * 0.85 + mastH * 0.55", "L * 0.4", tilt=50, drop=0.5),
    {"id": "rudder", "use": "items/components/rudder", "params": {"h": "D * 1.0", "w": "B * 0.08", "tiller": "L * 0.08"}, "at": [0, "D * 0.9", 0]},
])

SHIPS["felucca"] = ship("Felucca", "1500-1900", "Egypt, the Levant", "the Nile's sailing boat: a shallow hull, a great lateen on a raked mast, a small mizzen, an awning aft",
    {"L": [10, 14], "B": "L * 0.3", "D": "B * 0.4", "mastH": "L * 0.65"}, {"planks": "planks-pine", "wood": "pine"}, [
    hull("L", "B", "D", fullness=0.5, plan=[[0, 0.35], [0.15, 0.8], [0.45, 1], [0.8, 0.7], [1, 0.03]],
         keel=[[0, "D * 0.25"], [0.1, 0], [0.9, 0], [1, "D * 0.5"]], sheer=[[0, "D * 1.1"], [0.5, "D"], [1, "D * 1.4"]],
         deck=[{"y": "D * 0.8", "from": 0.03, "to": 0.97}], rail=0.06),
    {"id": "mast", "use": "items/components/mast", "params": {"h": "mastH", "r": 0.15}, "at": ["L * 0.6", "D * 0.8", 0, 0, 0, -12]},
    lateen("L * 0.6 + mastH * 0.19", "D * 0.8 + mastH * 0.9", "L * 1.1", tilt=58, drop=0.55),
    {"id": "awning", "use": "items/components/awning", "params": {"w": "B * 0.9", "d": "L * 0.25", "h": 1.8}, "at": ["L * 0.03", "D * 0.8", 0]},
    {"id": "rudder", "use": "items/components/rudder", "params": {"h": "D * 1.1", "w": "B * 0.12", "tiller": "L * 0.12", "thick": 0.06}, "at": [0, "D * 0.95", 0]},
])

SHIPS["ship-of-the-line"] = ship("Ship of the line", "1700-1800", "England, France, Spain", "a 74-gun ship of the line: two full gun decks and a quarterdeck, the stern galleries with their windows, a lion at the head, three masts in three tiers of square sails, a bowsprit with its jibs",
    {"L": [50, 58], "B": "L * 0.26", "D": "B * 0.65", "mastH": "L * 0.7"}, {"planks": "planks", "wood": "pine", "trim": "gilt", "band": "#e0c46a"}, [
    hull("L", "B", "D", fullness=0.6, tumblehome=0.3, plan=[[0, 0.35], [0.1, 0.72], [0.35, 1], [0.65, 1], [0.88, 0.6], [1, 0.05]],
         keel=[[0, "D * 0.2"], [0.08, 0], [0.92, 0], [1, "D * 0.25"]], sheer=[[0, "D * 1.08"], [0.5, "D"], [1, "D * 1.05"]],
         deck=[{"y": "D * 0.9", "from": 0.03, "to": 0.97}], rail=0.12, keelBeam=[0.45, 0.45]),
    {"id": "band", "type": "box", "material": "band", "size": ["L * 0.9", 0.25, 0.04], "at": ["L * 0.5", "D * 0.56", "B * 0.5"], "mirror": "z"},
    {"id": "band upper", "type": "box", "material": "band", "size": ["L * 0.88", 0.25, 0.04], "at": ["L * 0.5", "D * 0.78", "B * 0.465"], "mirror": "z"},
    {"id": "guns lower", "use": "items/components/gun-row", "params": {"n": 14, "from": "L * 0.1", "to": "L * 0.88", "y": "D * 0.45", "z": "B * 0.5", "bore": 0.13}},
    {"id": "guns middle", "use": "items/components/gun-row", "params": {"n": 14, "from": "L * 0.11", "to": "L * 0.87", "y": "D * 0.67", "z": "B * 0.48", "bore": 0.11}},
    {"id": "guns upper", "use": "items/components/gun-row", "params": {"n": 8, "from": "L * 0.12", "to": "L * 0.5", "y": "D * 0.98", "z": "B * 0.44", "bore": 0.09}},
    {"id": "quarterdeck", "use": "items/components/castle", "params": {"w": "B * 0.88", "d": "L * 0.42", "h": "D * 0.3", "rail": 1.1, "crenels": 0, "posts": 0}, "at": ["L * 0.02", "D * 0.9", 0]},
    {"id": "quarterdeck wall", "type": "box", "material": "planks", "size": ["L * 0.42", "D * 0.3", 0.1], "at": ["L * 0.23", "D * 1.05", "B * 0.44"], "mirror": "z"},
    {"id": "poop", "use": "items/components/castle", "params": {"w": "B * 0.75", "d": "L * 0.14", "h": "D * 0.25", "rail": 1.0, "crenels": 0, "posts": 0}, "at": ["L * 0.02", "D * 1.2", 0]},
    {"id": "poop wall", "type": "box", "material": "planks", "size": ["L * 0.14", "D * 0.25", 0.1], "at": ["L * 0.09", "D * 1.32", "B * 0.37"], "mirror": "z"},
    {"id": "forecastle", "use": "items/components/castle", "params": {"w": "B * 0.8", "d": "L * 0.16", "h": "D * 0.3", "rail": 1.1, "crenels": 0, "posts": 0}, "at": ["L * 0.82", "D * 0.9", 0]},
    {"id": "stern galleries", "use": "items/components/cabin", "params": {"w": "B * 0.8", "d": "L * 0.06", "h": "D * 0.7", "windows": 6}, "at": ["-L * 0.03", "D * 0.55", 0]},
    {"id": "stern trim", "type": "box", "material": "trim", "size": [0.1, 0.22, "B * 0.82"], "along": {"n": 3, "from": ["-L * 0.03", "D * 0.75", 0], "to": ["-L * 0.03", "D * 1.25", 0]}},
    {"id": "figurehead", "use": "items/components/figurehead", "params": {"style": "lion", "s": "D * 0.3"}, "at": ["L * 1.0", "D * 0.9", 0]},
    {"id": "beakhead", "type": "plate", "material": "planks", "thick": "B * 0.1", "at": ["L", "D * 0.7", 0, 90, 0, 0], "outline": [[0, 0], ["L * 0.08", "D * 0.15"], ["L * 0.08", "D * 0.22"], [0, "D * 0.4"]]},
    {"id": "rudder", "use": "items/components/rudder", "params": {"h": "D * 0.95", "w": "B * 0.06", "tiller": 0}, "at": [0, "D * 0.9", 0]},
    mast("L * 0.5", "D * 0.9", "mastH", r=0.45, top="topmast", topH=0.55),
    square("L * 0.5", "D * 0.9 + mastH * 0.86", "L * 0.55", "mastH * 0.4", belly="L * 0.05"),
    square("L * 0.5", "D * 0.9 + mastH * 1.35", "L * 0.42", "mastH * 0.36", belly="L * 0.04"),
    square("L * 0.5", "D * 0.9 + mastH * 1.55 + mastH * 0.25", "L * 0.28", "mastH * 0.22", belly="L * 0.02"),
    {"id": "main royal mast", "type": "rod", "material": "wood", "from": ["L * 0.5", "D * 0.9 + mastH * 1.5", 0], "to": ["L * 0.5", "D * 0.9 + mastH * 1.85", 0], "r0": 0.14, "r1": 0.08},
    mast("L * 0.8", "D * 1.2", "mastH * 0.88", r=0.4, top="topmast", topH=0.55),
    square("L * 0.8", "D * 1.2 + mastH * 0.75", "L * 0.48", "mastH * 0.36", belly="L * 0.05"),
    square("L * 0.8", "D * 1.2 + mastH * 1.18", "L * 0.36", "mastH * 0.3", belly="L * 0.03"),
    square("L * 0.8", "D * 1.2 + mastH * 1.55", "L * 0.24", "mastH * 0.18", belly="L * 0.02"),
    {"id": "fore royal mast", "type": "rod", "material": "wood", "from": ["L * 0.8", "D * 1.2 + mastH * 1.32", 0], "to": ["L * 0.8", "D * 1.2 + mastH * 1.62", 0], "r0": 0.12, "r1": 0.07},
    mast("L * 0.17", "D * 1.45", "mastH * 0.65", r=0.3, top="topmast", topH=0.5),
    square("L * 0.17", "D * 1.45 + mastH * 0.56", "L * 0.34", "mastH * 0.26", belly="L * 0.03"),
    square("L * 0.17", "D * 1.45 + mastH * 0.88", "L * 0.22", "mastH * 0.18", belly="L * 0.02"),
    {"id": "spanker gaff", "type": "rod", "material": "wood", "from": ["L * 0.17", "D * 1.45 + mastH * 0.5", 0], "to": ["L * 0.02", "D * 1.45 + mastH * 0.62", 0], "r": 0.1},
    {"id": "spanker", "type": "sail", "material": "cloth", "belly": "L * 0.02", "at": ["L * 0.17", "D * 1.45 + mastH * 0.5", 0], "corners": [[0, 0], ["-L * 0.15", "mastH * 0.12"], ["-L * 0.2", "-mastH * 0.22"], [0, "-mastH * 0.28"]]},
    {"id": "bowsprit", "use": "items/components/bowsprit", "params": {"l": "L * 0.4", "r": 0.3, "steeve": 20}, "at": ["L * 0.98", "D * 1.1", 0]},
    {"id": "jib", "type": "sail", "material": "cloth", "belly": "L * 0.02", "at": ["L * 0.8", "D * 1.2 + mastH * 1.15", 0], "corners": [[0, 0], ["L * 0.5", "-mastH * 0.95"], ["L * 0.12", "-mastH * 1.0"]]},
    stay(["L * 0.5", "D * 0.9 + mastH * 1.85", 0], ["L * 0.8", "D * 1.2 + mastH * 1.3", 0]), stay(["L * 0.8", "D * 1.2 + mastH * 1.62", 0], ["L * 1.35", "D * 1.24", 0]),
    stay(["L * 0.5", "D * 0.9 + mastH * 1.5", 0], ["L * 0.17", "D * 1.45 + mastH * 1.0", 0]),
    {"id": "anchor", "use": "items/components/anchor", "params": {"h": "D * 0.5"}, "at": ["L * 0.86", "D * 0.95", "B * 0.5"], "mirror": "z"},
    {"id": "boats", "type": "hull", "material": "planks", "length": "L * 0.16", "beam": "B * 0.2", "depth": "B * 0.09", "fullness": 0.5, "stations": 10, "sides": 4, "plan": [[0, 0.4], [0.2, 0.85], [0.5, 1], [0.8, 0.7], [1, 0.03]], "at": ["L * 0.45", "D * 0.93", 0]},
])

SHIPS["frigate"] = ship("Frigate", "1750-1800", "England, France, America", "a frigate: one gun deck, fast and weatherly, a full ship rig in three tiers, the eyes of the fleet",
    {"L": [42, 48], "B": "L * 0.25", "D": "B * 0.55", "mastH": "L * 0.7"}, {"planks": "planks", "wood": "pine", "band": "#e0c46a", "trim": "gilt"}, [
    hull("L", "B", "D", fullness=0.5, tumblehome=0.22, plan=[[0, 0.3], [0.1, 0.65], [0.35, 1], [0.65, 0.97], [0.9, 0.55], [1, 0.04]],
         keel=[[0, "D * 0.2"], [0.08, 0], [0.92, 0], [1, "D * 0.25"]], sheer=[[0, "D * 1.08"], [0.5, "D"], [1, "D * 1.05"]],
         deck=[{"y": "D * 0.9", "from": 0.03, "to": 0.97}], rail=0.1, keelBeam=[0.4, 0.4]),
    {"id": "band", "type": "box", "material": "band", "size": ["L * 0.9", 0.22, 0.04], "at": ["L * 0.5", "D * 0.66", "B * 0.49"], "mirror": "z"},
    {"id": "guns", "use": "items/components/gun-row", "params": {"n": 14, "from": "L * 0.1", "to": "L * 0.88", "y": "D * 0.6", "z": "B * 0.49", "bore": 0.11}},
    {"id": "guns upper", "use": "items/components/gun-row", "params": {"n": 6, "from": "L * 0.12", "to": "L * 0.42", "y": "D * 0.98", "z": "B * 0.44", "bore": 0.08}},
    {"id": "quarterdeck", "use": "items/components/castle", "params": {"w": "B * 0.88", "d": "L * 0.4", "h": "D * 0.28", "rail": 1.0, "crenels": 0, "posts": 0}, "at": ["L * 0.02", "D * 0.9", 0]},
    {"id": "quarterdeck wall", "type": "box", "material": "planks", "size": ["L * 0.4", "D * 0.28", 0.1], "at": ["L * 0.22", "D * 1.04", "B * 0.44"], "mirror": "z"},
    {"id": "forecastle", "use": "items/components/castle", "params": {"w": "B * 0.8", "d": "L * 0.15", "h": "D * 0.28", "rail": 1.0, "crenels": 0, "posts": 0}, "at": ["L * 0.83", "D * 0.9", 0]},
    {"id": "stern", "use": "items/components/cabin", "params": {"w": "B * 0.78", "d": "L * 0.05", "h": "D * 0.45", "windows": 5}, "at": ["-L * 0.03", "D * 0.72", 0]},
    {"id": "figurehead", "use": "items/components/figurehead", "params": {"style": "scroll", "s": "D * 0.3"}, "at": ["L * 1.0", "D * 0.85", 0]},
    {"id": "rudder", "use": "items/components/rudder", "params": {"h": "D * 0.95", "w": "B * 0.06", "tiller": 0}, "at": [0, "D * 0.9", 0]},
    mast("L * 0.5", "D * 0.9", "mastH", r=0.38, top="topmast", topH=0.55),
    square("L * 0.5", "D * 0.9 + mastH * 0.86", "L * 0.52", "mastH * 0.4", belly="L * 0.05"),
    square("L * 0.5", "D * 0.9 + mastH * 1.35", "L * 0.4", "mastH * 0.34", belly="L * 0.04"),
    square("L * 0.5", "D * 0.9 + mastH * 1.78", "L * 0.26", "mastH * 0.2", belly="L * 0.02"),
    {"id": "main royal mast", "type": "rod", "material": "wood", "from": ["L * 0.5", "D * 0.9 + mastH * 1.5", 0], "to": ["L * 0.5", "D * 0.9 + mastH * 1.85", 0], "r0": 0.12, "r1": 0.07},
    mast("L * 0.8", "D * 1.18", "mastH * 0.88", r=0.34, top="topmast", topH=0.55),
    square("L * 0.8", "D * 1.18 + mastH * 0.75", "L * 0.46", "mastH * 0.36", belly="L * 0.05"),
    square("L * 0.8", "D * 1.18 + mastH * 1.18", "L * 0.34", "mastH * 0.3", belly="L * 0.03"),
    square("L * 0.8", "D * 1.18 + mastH * 1.55", "L * 0.22", "mastH * 0.18", belly="L * 0.02"),
    {"id": "fore royal mast", "type": "rod", "material": "wood", "from": ["L * 0.8", "D * 1.18 + mastH * 1.32", 0], "to": ["L * 0.8", "D * 1.18 + mastH * 1.62", 0], "r0": 0.1, "r1": 0.06},
    mast("L * 0.18", "D * 1.18", "mastH * 0.66", r=0.26, top="topmast", topH=0.5),
    square("L * 0.18", "D * 1.18 + mastH * 0.57", "L * 0.32", "mastH * 0.26", belly="L * 0.03"),
    square("L * 0.18", "D * 1.18 + mastH * 0.9", "L * 0.2", "mastH * 0.18", belly="L * 0.02"),
    {"id": "spanker gaff", "type": "rod", "material": "wood", "from": ["L * 0.18", "D * 1.18 + mastH * 0.5", 0], "to": ["L * 0.02", "D * 1.18 + mastH * 0.62", 0], "r": 0.09},
    {"id": "spanker", "type": "sail", "material": "cloth", "belly": "L * 0.02", "at": ["L * 0.18", "D * 1.18 + mastH * 0.5", 0], "corners": [[0, 0], ["-L * 0.16", "mastH * 0.12"], ["-L * 0.21", "-mastH * 0.22"], [0, "-mastH * 0.3"]]},
    {"id": "bowsprit", "use": "items/components/bowsprit", "params": {"l": "L * 0.4", "r": 0.26, "steeve": 20}, "at": ["L * 0.98", "D * 1.05", 0]},
    {"id": "jib", "type": "sail", "material": "cloth", "belly": "L * 0.02", "at": ["L * 0.8", "D * 1.18 + mastH * 1.15", 0], "corners": [[0, 0], ["L * 0.5", "-mastH * 0.95"], ["L * 0.12", "-mastH * 1.0"]]},
    stay(["L * 0.5", "D * 0.9 + mastH * 1.85", 0], ["L * 0.8", "D * 1.18 + mastH * 1.3", 0]), stay(["L * 0.8", "D * 1.18 + mastH * 1.62", 0], ["L * 1.35", "D * 1.19", 0]),
    stay(["L * 0.5", "D * 0.9 + mastH * 1.5", 0], ["L * 0.18", "D * 1.18 + mastH * 1.0", 0]),
    {"id": "anchor", "use": "items/components/anchor", "params": {"h": "D * 0.5"}, "at": ["L * 0.86", "D * 0.95", "B * 0.5"], "mirror": "z"},
])

SHIPS["east-indiaman"] = ship("East Indiaman", "1700-1800", "England, the Netherlands, France, Sweden", "an East India Company ship: as big as a ship of the line and armed like a frigate, a merchant's hull with a high stern and galleries, a full ship rig",
    {"L": [46, 54], "B": "L * 0.26", "D": "B * 0.65", "mastH": "L * 0.68"}, {"planks": "planks", "wood": "pine", "band": "#d8c890", "trim": "gilt"}, [
    hull("L", "B", "D", fullness=0.62, tumblehome=0.25, plan=[[0, 0.35], [0.1, 0.72], [0.35, 1], [0.65, 1], [0.88, 0.6], [1, 0.05]],
         keel=[[0, "D * 0.2"], [0.08, 0], [0.92, 0], [1, "D * 0.25"]], sheer=[[0, "D * 1.12"], [0.5, "D"], [1, "D * 1.05"]],
         deck=[{"y": "D * 0.9", "from": 0.03, "to": 0.97}], rail=0.12, keelBeam=[0.45, 0.45]),
    {"id": "band", "type": "box", "material": "band", "size": ["L * 0.9", 0.3, 0.04], "at": ["L * 0.5", "D * 0.68", "B * 0.485"], "mirror": "z"},
    {"id": "guns", "use": "items/components/gun-row", "params": {"n": 13, "from": "L * 0.1", "to": "L * 0.88", "y": "D * 0.62", "z": "B * 0.49", "bore": 0.1}},
    {"id": "quarterdeck", "use": "items/components/castle", "params": {"w": "B * 0.88", "d": "L * 0.45", "h": "D * 0.3", "rail": 1.1, "crenels": 0, "posts": 0}, "at": ["L * 0.02", "D * 0.9", 0]},
    {"id": "quarterdeck wall", "type": "box", "material": "planks", "size": ["L * 0.45", "D * 0.3", 0.1], "at": ["L * 0.245", "D * 1.05", "B * 0.44"], "mirror": "z"},
    {"id": "poop", "use": "items/components/castle", "params": {"w": "B * 0.75", "d": "L * 0.16", "h": "D * 0.25", "rail": 1.0, "crenels": 0, "posts": 0}, "at": ["L * 0.02", "D * 1.2", 0]},
    {"id": "poop wall", "type": "box", "material": "planks", "size": ["L * 0.16", "D * 0.25", 0.1], "at": ["L * 0.1", "D * 1.32", "B * 0.37"], "mirror": "z"},
    {"id": "forecastle", "use": "items/components/castle", "params": {"w": "B * 0.8", "d": "L * 0.16", "h": "D * 0.3", "rail": 1.1, "crenels": 0, "posts": 0}, "at": ["L * 0.82", "D * 0.9", 0]},
    {"id": "stern galleries", "use": "items/components/cabin", "params": {"w": "B * 0.8", "d": "L * 0.06", "h": "D * 0.75", "windows": 6}, "at": ["-L * 0.03", "D * 0.55", 0]},
    {"id": "stern trim", "type": "box", "material": "trim", "size": [0.1, 0.22, "B * 0.82"], "along": {"n": 3, "from": ["-L * 0.03", "D * 0.75", 0], "to": ["-L * 0.03", "D * 1.28", 0]}},
    {"id": "figurehead", "use": "items/components/figurehead", "params": {"style": "scroll", "s": "D * 0.3"}, "at": ["L * 1.0", "D * 0.88", 0]},
    {"id": "rudder", "use": "items/components/rudder", "params": {"h": "D * 0.95", "w": "B * 0.06", "tiller": 0}, "at": [0, "D * 0.9", 0]},
    mast("L * 0.5", "D * 0.9", "mastH", r=0.42, top="topmast", topH=0.55),
    square("L * 0.5", "D * 0.9 + mastH * 0.86", "L * 0.54", "mastH * 0.4", belly="L * 0.05"),
    square("L * 0.5", "D * 0.9 + mastH * 1.35", "L * 0.42", "mastH * 0.36", belly="L * 0.04"),
    square("L * 0.5", "D * 0.9 + mastH * 1.78", "L * 0.28", "mastH * 0.22", belly="L * 0.02"),
    {"id": "main royal mast", "type": "rod", "material": "wood", "from": ["L * 0.5", "D * 0.9 + mastH * 1.5", 0], "to": ["L * 0.5", "D * 0.9 + mastH * 1.85", 0], "r0": 0.13, "r1": 0.08},
    mast("L * 0.8", "D * 1.2", "mastH * 0.88", r=0.38, top="topmast", topH=0.55),
    square("L * 0.8", "D * 1.2 + mastH * 0.75", "L * 0.48", "mastH * 0.36", belly="L * 0.05"),
    square("L * 0.8", "D * 1.2 + mastH * 1.18", "L * 0.36", "mastH * 0.3", belly="L * 0.03"),
    square("L * 0.8", "D * 1.2 + mastH * 1.55", "L * 0.24", "mastH * 0.18", belly="L * 0.02"),
    {"id": "fore royal mast", "type": "rod", "material": "wood", "from": ["L * 0.8", "D * 1.2 + mastH * 1.32", 0], "to": ["L * 0.8", "D * 1.2 + mastH * 1.62", 0], "r0": 0.11, "r1": 0.07},
    mast("L * 0.17", "D * 1.45", "mastH * 0.65", r=0.28, top="topmast", topH=0.5),
    square("L * 0.17", "D * 1.45 + mastH * 0.56", "L * 0.34", "mastH * 0.26", belly="L * 0.03"),
    square("L * 0.17", "D * 1.45 + mastH * 0.88", "L * 0.22", "mastH * 0.18", belly="L * 0.02"),
    {"id": "spanker gaff", "type": "rod", "material": "wood", "from": ["L * 0.17", "D * 1.45 + mastH * 0.5", 0], "to": ["L * 0.02", "D * 1.45 + mastH * 0.62", 0], "r": 0.1},
    {"id": "spanker", "type": "sail", "material": "cloth", "belly": "L * 0.02", "at": ["L * 0.17", "D * 1.45 + mastH * 0.5", 0], "corners": [[0, 0], ["-L * 0.15", "mastH * 0.12"], ["-L * 0.2", "-mastH * 0.22"], [0, "-mastH * 0.28"]]},
    {"id": "bowsprit", "use": "items/components/bowsprit", "params": {"l": "L * 0.4", "r": 0.3, "steeve": 20}, "at": ["L * 0.98", "D * 1.1", 0]},
    {"id": "jib", "type": "sail", "material": "cloth", "belly": "L * 0.02", "at": ["L * 0.8", "D * 1.2 + mastH * 1.15", 0], "corners": [[0, 0], ["L * 0.5", "-mastH * 0.95"], ["L * 0.12", "-mastH * 1.0"]]},
    stay(["L * 0.5", "D * 0.9 + mastH * 1.85", 0], ["L * 0.8", "D * 1.2 + mastH * 1.3", 0]), stay(["L * 0.8", "D * 1.2 + mastH * 1.62", 0], ["L * 1.35", "D * 1.24", 0]),
    stay(["L * 0.5", "D * 0.9 + mastH * 1.5", 0], ["L * 0.17", "D * 1.45 + mastH * 1.0", 0]),
    {"id": "anchor", "use": "items/components/anchor", "params": {"h": "D * 0.5"}, "at": ["L * 0.86", "D * 0.95", "B * 0.5"], "mirror": "z"},
])


# ---- MATERIALS the ships add to the library -----------------------------------------------------------------------
MATERIALS = {
    "planks": {"pattern": "timber/boards", "palette": "oak", "scale": 1.5},
    "planks-pine": {"pattern": "timber/boards", "palette": "pine", "scale": 1.5},
    "planks-grey": {"pattern": "timber/boards", "palette": "oak-grey", "scale": 1.5},
    "planks-tarred": {"pattern": "timber/boards", "palette": ["#2a2018", "#4a3a2a", "#3a2c1e", "#5a4632"], "scale": 1.5},
    "deck": {"pattern": "timber/boards", "palette": "pine", "scale": 1.2},
    "sail-striped": {"pattern": "fabrics/stripes", "palette": "stripe-madder", "scale": 4},
    "sail-tan": {"pattern": "fabrics/linen", "palette": ["#b89a6a", "#a48858", "#c8ac7c", "#8a7048"]},
    "matting": {"pattern": "fabrics/straw", "palette": "straw", "scale": 3},
    "reed": {"pattern": "fabrics/straw", "palette": ["#c9b076", "#a8905a", "#dcc48e", "#8a7444"], "scale": 2},
    "bamboo": {"pattern": "timber/wood", "palette": ["#7a6a3a", "#c8b070", "#a89050", "#d8c890"]},
    "cedar": {"pattern": "timber/bark", "palette": ["#5a3a26", "#a87050", "#8a5a3c", "#c08868"]},
    "hide": {"pattern": "fabrics/leather", "palette": ["#7a5a3a", "#a88060", "#8e6a48", "#c09a78"], "scale": 2},
}


def main():
    for k, v in COMPONENTS.items():
        write("components/" + k, v)
    for k, v in SHIPS.items():
        write("ships/" + k, v)
    # the materials, added to the library where the library has none of that name
    mpath = os.path.join(ITEMS, "materials.json")
    lib = json.load(open(mpath))
    added = 0
    for k, v in MATERIALS.items():
        if k not in lib["materials"]:
            lib["materials"][k] = v; added += 1
    json.dump(lib, open(mpath, "w"), indent=1, ensure_ascii=False)
    # the catalogue: the ships' own category, the components in theirs
    ipath = os.path.join(ROOT, "assets", "index.json")
    index = json.load(open(ipath))
    cats = {c["name"]: c for c in index["categories"]}
    comps = cats["Items: components"]
    for k in COMPONENTS:
        if "items/components/" + k not in comps["paths"]:
            comps["paths"].append("items/components/" + k)
    if "Items: ships" not in cats:
        pos = index["categories"].index(cats["Items: furniture"]) + 1
        index["categories"].insert(pos, {"name": "Items: ships", "kind": "item", "paths": []})
        cats = {c["name"]: c for c in index["categories"]}
    cats["Items: ships"]["paths"] = ["items/ships/" + k for k in SHIPS]
    json.dump(index, open(ipath, "w"), indent=2, ensure_ascii=False)
    print(len(COMPONENTS), "components,", len(SHIPS), "ships,", added, "materials added")


if __name__ == "__main__":
    main()
