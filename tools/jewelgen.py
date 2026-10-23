#!/usr/bin/env python3
"""JEWELRY (2026-10-06; docs/jewelry.md): writes assets/items/jewelry/ -- necklaces, collars and torcs (neck/), what is
worn on the head (head/), earrings (ears/), the jewelry wardrobe (wear.json: who wears what, by style of dress and kind
of person) -- the materials they are made of (assets/items/materials.json) and the catalogue's "Items: jewelry".

Everything lies on a FIT (jewelry.js): a neck piece on the neck's surface as the body and its clothes make it (levels
are DROPS: metres down the surface from the neck's base), a head piece on the skull and the hair's cap (levels are
HEIGHTS on the head in the face's canonical frame: the brows ~.02, the hairline ~.065, the crown .10), an earring at the
lobe. An item's `colourways` are the sets of materials that belong together; the seed picks one, or `colourway` names it.
"""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ITEMS = os.path.join(ROOT, "assets", "items")
OUT = os.path.join(ITEMS, "jewelry")

# ---- the stones, glass and enamel (plain paint), added to the library if missing -------------------------------
MATERIALS = {
    "lapis": "#2a4290", "carnelian": "#b03c22", "turquoise": "#3fb3a3", "faience-blue": "#2f8cbb", "faience-green": "#3f9b6c",
    "faience-white": "#e9e3d0", "faience-yellow": "#d9b23c", "faience-red": "#b8452e", "pearl": "#efe9da", "jade": "#4e9a6b", "jade-white": "#d9ddc8",
    "emerald": "#1d8a4e", "ruby": "#a5172d", "sapphire": "#2b409e", "garnet": "#7c1526", "amber": "#c98b24", "coral": "#d2573f",
    "obsidian": "#201d22", "glass-blue": "#2f60b2", "glass-yellow": "#dab437", "glass-green": "#3b8b3f", "glass-red": "#9c2b23",
    "cord-red": "#9e2c29", "cord-black": "#2b2523", "cord-green": "#4d6b34", "enamel-blue": "#2b50a2", "enamel-red": "#a8302c", "electrum": "#d7c27c",
}


def write(path, doc):
    full = os.path.join(OUT, path + ".json")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    json.dump(doc, open(full, "w"), indent=1, ensure_ascii=False)


def item(name, about, parts, colourways, era, region, params=None, category="jewelry"):
    first = next(iter(colourways.values()))
    return {"kind": "item", "name": name, "category": category, "era": era, "region": region, "_about": about,
            "params": params or {}, "materials": dict(first), "colourways": colourways, "parts": parts}


# ---- shapes ------------------------------------------------------------------------------------------------------
def r6(v): return round(v, 5)
def lance(L, W, n=9):   # a leaf along +x, its stalk at the origin
    top = [[r6(L * i / n), r6(W / 2 * math.sin(math.pi * i / n) ** .8)] for i in range(n + 1)]
    return top + [[x, -y] for x, y in reversed(top[1:-1])]
def disc_outline(r, n=12, c=(0, 0)): return [[r6(c[0] + r * math.cos(2 * math.pi * i / n)), r6(c[1] + r * math.sin(2 * math.pi * i / n))] for i in range(n)]
def oval(rx, ry, n=14, c=(0, 0)): return [[r6(c[0] + rx * math.cos(2 * math.pi * i / n)), r6(c[1] + ry * math.sin(2 * math.pi * i / n))] for i in range(n)]
def lathe_ring(R, r, n=8): return [[r6(R + r * math.cos(2 * math.pi * i / n)), r6(r * math.sin(2 * math.pi * i / n))] for i in range(n + 1)]
def dome(r, h, n=4): return [[0, 0]] + [[r6(r * math.cos(math.pi / 2 * i / n)), r6(h * math.sin(math.pi / 2 * i / n))] for i in range(n + 1)]   # (base out, then over the top to the axis)
def crescent(R, r, n=8):   # a crescent hanging under its top: the bottom halves of two circles, the inner one higher
    outer = [[r6(R * math.cos(math.pi + math.pi * i / n)), r6(-R + R * math.sin(math.pi + math.pi * i / n))] for i in range(n + 1)]
    inner = [[r6(r * math.cos(math.pi + math.pi * i / n)), r6(-R + (R - r) * 0.3 + r * math.sin(math.pi + math.pi * i / n) * 0.75)] for i in range(n, -1, -1)]
    return outer + inner[1:-1]


# a gem set in gold: a dome of the stone in a gold rim, facing out of the surface (lathe axis y turned to z)
def gem(at_on, r, stone="gem", rim="metal", scale=None):
    sc = {"scale": scale} if scale else {}
    return [{"id": "setting", "type": "lathe", "material": rim, "profile": [[0, 0], [r * 1.25, 0], [r * 1.25, r * .5], [0, r * .5]], "sides": 8, "on": at_on, "at": [0, 0, 0, 0, 90, 0], **sc},
            {"id": "stone", "type": "lathe", "material": stone, "profile": dome(r, r * .8), "sides": 8, "on": at_on, "at": [0, 0, r * .45, 0, 90, 0], **sc}]


NECK, HEAD, EARS = {}, {}, {}

# ======================= NECKLACES (fit "neck": levels are drops below the neck's base, metres) ====================
NECK["wesekh"] = item("Wesekh broad collar", "the Egyptian broad collar: rows of cylinder beads strung between gold bands, from the neck's base over the shoulders and the chest, a fringe of teardrops round its edge (Tutankhamun's, the nobles' in the tomb paintings) -- in the king's gold, lapis, carnelian and turquoise, or the faience blues and greens of ordinary wear",
    [{"id": "collar", "type": "collar", "fit": "neck", "from": 0.0, "to": [0.105, 0.05], "thick": 0.005, "lift": 0.002, "step": 5,
      "rows": [{"share": 0.6, "kind": "band", "material": "metal"},
               {"share": 1.4, "kind": "beads", "materials": ["b1", "b2"], "n": 64, "ground": "metal"},
               {"share": 0.45, "kind": "band", "material": "metal"},
               {"share": 1.6, "kind": "beads", "materials": ["b3", "b1", "b2"], "n": 56, "ground": "metal"},
               {"share": 0.45, "kind": "band", "material": "metal"},
               {"share": 1.8, "kind": "beads", "materials": ["b2", "b3"], "n": 48, "ground": "metal"},
               {"share": 0.5, "kind": "band", "material": "metal"},
               {"kind": "drops", "n": 44, "length": 0.024, "width": 0.0095, "materials": ["b1", "b4"]}]},
     # (the falcon-headed terminals on the shoulders: a gold plate each, its eye inlaid)
     {"id": "terminal", "type": "plate", "material": "metal", "thick": 0.004, "outline": oval(0.017, 0.022, 12), "on": {"fit": "neck", "th": [88, -88], "level": 0.034, "lift": 0.006}},
     {"id": "terminal eye", "type": "plate", "material": "b1", "thick": 0.002, "outline": disc_outline(0.006, 8), "on": {"fit": "neck", "th": [88, -88], "level": 0.034, "lift": 0.009}}],
    {"royal": {"metal": "gold", "b1": "lapis", "b2": "carnelian", "b3": "turquoise", "b4": "gold"},
     "faience": {"metal": "faience-white", "b1": "faience-blue", "b2": "faience-green", "b3": "faience-white", "b4": "faience-blue"},
     "festival": {"metal": "gold", "b1": "faience-blue", "b2": "faience-red", "b3": "faience-yellow", "b4": "faience-green"}},
    "ancient", "Egypt")

NECK["pectoral"] = item("Pectoral", "an Egyptian pectoral: a plaque on the chest -- a winged scarab pushing the sun, in gold cells inlaid with lapis, carnelian and turquoise -- hung on a string of alternating beads",
    [{"id": "beads", "type": "strand", "fit": "neck", "level": [0.07, 0.012], "bead": "tube", "size": 0.0035, "length": 0.013, "materials": ["b1", "metal", "b2", "metal"]},
     {"id": "plaque", "type": "plate", "material": "metal", "thick": 0.004, "on": {"fit": "neck", "th": 0, "level": 0.1, "lift": 0.004},
      "outline": [[-0.045, 0.012], [-0.03, 0.026], [0.03, 0.026], [0.045, 0.012], [0.032, -0.022], [-0.032, -0.022]]},
     {"id": "wing L", "type": "plate", "material": "b3", "thick": 0.002, "on": {"fit": "neck", "th": 0, "level": 0.1, "lift": 0.0075},
      "outline": [[-0.04, 0.012], [-0.028, 0.02], [-0.012, 0.012], [-0.014, 0.0], [-0.03, -0.004]]},
     {"id": "wing R", "type": "plate", "material": "b3", "thick": 0.002, "on": {"fit": "neck", "th": 0, "level": 0.1, "lift": 0.0075},
      "outline": [[0.04, 0.012], [0.03, -0.004], [0.014, 0.0], [0.012, 0.012], [0.028, 0.02]]},
     {"id": "scarab", "type": "plate", "material": "b1", "thick": 0.003, "on": {"fit": "neck", "th": 0, "level": 0.1, "lift": 0.0075}, "outline": oval(0.01, 0.014, 12, (0, -0.002))},
     {"id": "sun", "type": "plate", "material": "b2", "thick": 0.003, "on": {"fit": "neck", "th": 0, "level": 0.1, "lift": 0.0075}, "outline": disc_outline(0.0065, 10, (0, 0.017))}],
    {"royal": {"metal": "gold", "b1": "lapis", "b2": "carnelian", "b3": "turquoise"},
     "faience": {"metal": "faience-white", "b1": "faience-blue", "b2": "faience-red", "b3": "faience-green"}},
    "ancient", "Egypt")

NECK["torc"] = item("Torc", "a Celtic torc: a rigid twisted bar round the neck, open at the front, swelling to two buffer terminals under the chin -- gold for a chieftain, bronze or silver for the rest",
    [{"id": "bar", "type": "strand", "fit": "neck", "level": -0.008, "th": [16, 344], "bead": "twist", "size": 0.0048, "swell": 0.45, "twist": 0.5, "lift": 0.003, "material": "metal"},
     {"id": "terminal", "type": "lathe", "material": "metal", "profile": [[0, -0.007], [0.0085, -0.006], [0.0095, 0.0], [0.0085, 0.006], [0, 0.007]], "sides": 10,
      "on": {"fit": "neck", "th": [16, -16], "level": -0.008, "lift": 0.012}, "at": [0, 0, 0, 0, 0, 90]}],
    {"gold": {"metal": "gold"}, "bronze": {"metal": "bronze"}, "silver": {"metal": "silver"}}, "iron age", "Celtic Europe")

NECK["chain-pendant"] = item("Gold chain with pendant", "a Greek or Roman gold chain of small links, a medallion on it -- a gold disc round a garnet -- hanging at the breastbone",
    [{"id": "chain", "type": "strand", "fit": "neck", "level": [0.052, 0.01], "vee": 0.008, "bead": "twist", "size": 0.0014, "twist": 0.9, "material": "metal"},
     {"id": "medallion", "type": "lathe", "material": "metal", "profile": [[0, 0], [0.013, 0], [0.014, 0.002], [0.012, 0.0035], [0, 0.0035]], "sides": 14,
      "on": {"fit": "neck", "th": 0, "level": 0.075, "lift": 0.002}, "at": [0, 0, 0, 0, 90, 0]},
     *gem({"fit": "neck", "th": 0, "level": 0.075, "lift": 0.004}, 0.0065, stone="gem")],
    {"garnet": {"metal": "gold", "gem": "garnet"}, "emerald": {"metal": "gold", "gem": "emerald"}, "lapis": {"metal": "electrum", "gem": "lapis"}},
    "classical", "Greece, Rome")

NECK["greek-fringe"] = item("Fringe necklace", "a Hellenistic gold necklace: a strap of links with a fringe of seed-shaped pendants hanging from it across the chest",
    [{"id": "strap", "type": "strand", "fit": "neck", "level": [0.03, 0.006], "bead": "twist", "size": 0.0022, "twist": 0.8, "material": "metal"},
     {"id": "seed", "type": "lathe", "material": "metal", "profile": [[0, 0.0], [0.0035, -0.003], [0.0045, -0.009], [0.003, -0.015], [0, -0.019]], "sides": 6,
      "on": {"fit": "neck", "ring": {"n": 17, "from": -64, "to": 64}, "level": [0.034, 0.01], "lift": 0.004}},
     {"id": "bead", "type": "sphere", "material": "gem", "r": 0.0028, "sides": 6, "on": {"fit": "neck", "ring": {"n": 17, "from": -64, "to": 64}, "level": [0.034, 0.01], "lift": 0.005}}],
    {"gold": {"metal": "gold", "gem": "garnet"}, "gold-blue": {"metal": "gold", "gem": "enamel-blue"}}, "hellenistic", "Greece")

NECK["pearls"] = item("String of pearls", "a strand of pearls, or pearls strung with emeralds or garnets between them -- a Roman lady's, a Renaissance one's",
    [{"id": "pearls", "type": "strand", "fit": "neck", "level": [0.04, 0.004], "bead": "round", "size": 0.0038, "gap": 0.0006, "materials": ["b1", "b1", "b2"]}],
    {"pearl": {"b1": "pearl", "b2": "pearl"}, "pearl-emerald": {"b1": "pearl", "b2": "emerald"}, "pearl-garnet": {"b1": "pearl", "b2": "garnet"}},
    "roman, renaissance", "Europe")

NECK["choker"] = item("Pearl choker", "a close string of pearls high round the neck, a drop hanging from it: a ruby in gold and a pearl under it",
    [{"id": "pearls", "type": "strand", "fit": "neck", "level": -0.012, "bead": "round", "size": 0.0033, "gap": 0.0004, "material": "b1", "lift": 0.001},
     *gem({"fit": "neck", "th": 0, "level": -0.002, "lift": 0.003}, 0.0055, stone="gem"),
     {"id": "drop pearl", "type": "sphere", "material": "b1", "r": 0.004, "sides": 8, "on": {"fit": "neck", "th": 0, "level": 0.012, "lift": 0.004}}],
    {"ruby": {"b1": "pearl", "gem": "ruby", "metal": "gold"}, "sapphire": {"b1": "pearl", "gem": "sapphire", "metal": "gold"}}, "renaissance", "Europe")

NECK["livery-collar"] = item("Livery collar", "a late medieval collar of office: flat gold links lying across the shoulders and down to a point on the chest, a jewel hung from it (the Lancastrian collar of esses)",
    [{"id": "links", "type": "strand", "fit": "neck", "level": [0.1, 0.035], "vee": 0.03, "bead": "cube", "size": 0.0042, "length": 0.012, "gap": 0.0012, "materials": ["metal", "b1"]},
     *gem({"fit": "neck", "th": 0, "level": 0.145, "lift": 0.004}, 0.009, stone="gem"),
     {"id": "rose", "type": "plate", "material": "metal", "thick": 0.003, "outline": disc_outline(0.016, 10), "on": {"fit": "neck", "th": 0, "level": 0.145, "lift": 0.002}}],
    {"gold": {"metal": "gold", "b1": "gold", "gem": "ruby"}, "silver-gilt": {"metal": "silver", "b1": "gold", "gem": "sapphire"}}, "late medieval", "England, Burgundy")

NECK["cross-cord"] = item("Cross on a cord", "a small cross on a cord or a thong -- what most people wore, in wood, pewter or silver",
    [{"id": "cord", "type": "strand", "fit": "neck", "level": [0.07, 0.012], "bead": "cord", "size": 0.0013, "material": "cord"},
     {"id": "upright", "type": "box", "material": "cross", "size": [0.008, 0.032, 0.004], "on": {"fit": "neck", "th": 0, "level": 0.095, "lift": 0.003}},
     {"id": "arm", "type": "box", "material": "cross", "size": [0.022, 0.008, 0.004], "on": {"fit": "neck", "th": 0, "level": 0.095, "lift": 0.003}, "at": [0, 0.006, 0]}],
    {"wood": {"cord": "cord-black", "cross": "walnut"}, "pewter": {"cord": "leather-dark", "cross": "pewter"}, "silver": {"cord": "cord-red", "cross": "silver"}},
    "medieval", "Europe")

NECK["viking-festoon"] = item("Brooches and beads", "a Norse woman's pair of oval tortoise brooches holding her apron dress, with festoons of glass and amber beads hung between them across the chest",
    [{"id": "brooch", "type": "lathe", "material": "metal", "profile": [[0, 0], [0.024, 0], [0.022, 0.006], [0.014, 0.012], [0, 0.014]], "sides": 12, "on": {"fit": "neck", "th": [34, -34], "level": 0.075, "lift": 0.002}, "at": [0, 0, 0, 0, 90, 0], "stretch": [0.75, 1, 1]},
     {"id": "festoon", "type": "strand", "fit": "neck", "level": 0.082, "vee": 0.045, "th": [-30, 30], "bead": "round", "size": 0.0042, "gap": 0.001, "materials": ["b1", "b2", "b3", "b4", "b2"]},
     {"id": "festoon 2", "type": "strand", "fit": "neck", "level": 0.084, "vee": 0.02, "th": [-30, 30], "bead": "round", "size": 0.0036, "gap": 0.001, "materials": ["b3", "b1", "b4"]}],
    {"glass": {"metal": "bronze", "b1": "glass-blue", "b2": "amber", "b3": "glass-yellow", "b4": "carnelian"},
     "green": {"metal": "bronze", "b1": "glass-green", "b2": "amber", "b3": "glass-red", "b4": "glass-yellow"},
     "silver": {"metal": "silver", "b1": "glass-blue", "b2": "pearl", "b3": "carnelian", "b4": "amber"}}, "viking age", "Scandinavia")

NECK["jade-bi"] = item("Jade disc on a cord", "a Chinese jade bi -- a flat disc with a hole -- on a red silk cord, a knot bead above it",
    [{"id": "cord", "type": "strand", "fit": "neck", "level": [0.085, 0.012], "bead": "cord", "size": 0.0014, "material": "cord"},
     {"id": "bi", "type": "lathe", "material": "jade", "profile": [[0.006, -0.002], [0.021, -0.002], [0.022, 0.0], [0.021, 0.002], [0.006, 0.002], [0.005, 0.0], [0.006, -0.002]], "sides": 16,
      "on": {"fit": "neck", "th": 0, "level": 0.118, "lift": 0.003}, "at": [0, 0, 0, 0, 90, 0]},
     {"id": "knot", "type": "sphere", "material": "knot", "r": 0.0045, "sides": 6, "on": {"fit": "neck", "th": 0, "level": 0.091, "lift": 0.004}}],
    {"green": {"cord": "cord-red", "jade": "jade", "knot": "cord-red"}, "white": {"cord": "cord-red", "jade": "jade-white", "knot": "coral"}},
    "han, tang", "China")

NECK["bulla"] = item("Bulla", "a Roman freeborn boy's bulla: a lens-shaped gold (or leather) capsule holding an amulet, worn on a cord until he came of age",
    [{"id": "cord", "type": "strand", "fit": "neck", "level": [0.06, 0.01], "bead": "cord", "size": 0.0014, "material": "cord"},
     {"id": "bulla", "type": "lathe", "material": "metal", "profile": [[0, 0], [0.014, 0.0], [0.0145, 0.0025], [0.011, 0.006], [0, 0.0075]], "sides": 12,
      "on": {"fit": "neck", "th": 0, "level": 0.08, "lift": 0.002}, "at": [0, 0, 0, 0, 90, 0]},
     {"id": "loop", "type": "ring", "material": "metal", "r": 0.003, "tube": 0.001, "sides": 4, "on": {"fit": "neck", "th": 0, "level": 0.064, "lift": 0.004}, "at": [0, 0, 0, 0, 90, 0]}],
    {"gold": {"cord": "leather-dark", "metal": "gold"}, "leather": {"cord": "leather-dark", "metal": "leather-red"}}, "roman", "Rome")

NECK["lunula"] = item("Lunula", "a Bronze Age gold lunula: a thin crescent beaten from a sheet, broad over the chest and narrowing to its two ends behind the neck, engraved bands along its edges",
    [{"id": "crescent", "type": "collar", "fit": "neck", "from": 0.002, "to": [0.098, 0.01], "th": [-150, 150], "thick": 0.0018, "lift": 0.002,
      "rows": [{"share": 0.12, "kind": "band", "material": "edge"}, {"share": 1, "kind": "band", "material": "metal"}, {"share": 0.12, "kind": "band", "material": "edge"}]}],
    {"gold": {"metal": "gold", "edge": "gilt"}}, "bronze age", "Ireland")

# ======================= HEADWEAR (fit "head": levels are heights on the canonical head) ===========================
LEAF_L = lance(0.026, 0.009, 5)
def wreath(material_leaf, n=26, lv=(0.07, 0.044), size=1.0):
    out = [{"id": "stem", "type": "band", "fit": "head", "level": list(lv), "width": 0.004, "thick": 0.0025, "lift": 0.001, "material": "stem"}]
    L = [[r6(x * size), r6(y * size)] for x, y in LEAF_L]
    for side, (a, b), roll0 in (("R", (8, 172), 180), ("L", (-172, -8), 0)):
        for k, (dl, tilt) in enumerate(((0.004, 28), (-0.004, -28))):
            out.append({"id": f"leaves {side}{k}", "type": "plate", "material": material_leaf, "thick": 0.0012, "outline": L, "scale": "scale",
                        "on": {"fit": "head", "ring": {"n": n // 2, "from": a, "to": b}, "level": [lv[0] + dl, lv[1] + dl], "lift": 0.003},
                        "at": [0, 0, 0, 0, 0, roll0 + (tilt if side == "L" else -tilt)]})
    return out

HEAD["uraeus-diadem"] = item("Uraeus diadem", "a royal Egyptian diadem: a gold band round the brow with the rearing cobra -- the uraeus -- at its front, its hood inlaid with carnelian and lapis",
    [{"id": "band", "type": "band", "fit": "head", "level": [0.062, 0.052], "width": 0.012, "thick": 0.0025, "crest": 0.4, "material": "metal"},
     {"id": "hood", "type": "plate", "material": "metal", "thick": 0.004, "scale": "scale", "on": {"fit": "head", "th": 0, "level": 0.07, "lift": 0.004},
      "outline": [[0, -0.008], [0.007, -0.002], [0.009, 0.008], [0.007, 0.018], [0.003, 0.024], [0, 0.026], [-0.003, 0.024], [-0.007, 0.018], [-0.009, 0.008], [-0.007, -0.002]]},
     {"id": "hood inlay", "type": "plate", "material": "b2", "thick": 0.002, "scale": "scale", "on": {"fit": "head", "th": 0, "level": 0.07, "lift": 0.0068},
      "outline": [[0, -0.003], [0.004, 0.002], [0.005, 0.01], [0.002, 0.017], [0, 0.019], [-0.002, 0.017], [-0.005, 0.01], [-0.004, 0.002]]},
     {"id": "eye", "type": "sphere", "material": "b1", "r": 0.0016, "sides": 6, "scale": "scale", "on": {"fit": "head", "th": 0, "level": 0.07, "lift": 0.007}, "at": [0, 0.021, 0]}],
    {"royal": {"metal": "gold", "b1": "lapis", "b2": "carnelian"}}, "ancient", "Egypt", {"scale": 1})

HEAD["seshed-circlet"] = item("Seshed circlet", "an Egyptian circlet (seshed): a gold fillet round the head set with rosettes of carnelian, with two streamers at the back",
    [{"id": "band", "type": "band", "fit": "head", "level": [0.062, 0.05], "width": 0.008, "thick": 0.0022, "material": "metal"},
     {"id": "rosette", "type": "lathe", "material": "metal", "profile": [[0, 0], [0.0075, 0], [0.0075, 0.0015], [0, 0.0025]], "sides": 10, "scale": "scale",
      "on": {"fit": "head", "ring": {"n": 9, "from": -150, "to": 150}, "level": [0.062, 0.05], "lift": 0.003}, "at": [0, 0, 0, 0, 90, 0]},
     {"id": "rosette heart", "type": "sphere", "material": "b1", "r": 0.0035, "sides": 6, "scale": "scale", "on": {"fit": "head", "ring": {"n": 9, "from": -150, "to": 150}, "level": [0.062, 0.05], "lift": 0.0045}},
     {"id": "streamer", "type": "box", "material": "metal", "size": [0.008, 0.07, 0.0015], "scale": "scale", "on": {"fit": "head", "th": [168, -168], "level": 0.05, "lift": 0.003}, "at": [0, -0.035, 0]}],
    {"carnelian": {"metal": "gold", "b1": "carnelian"}, "turquoise": {"metal": "gold", "b1": "turquoise"}}, "ancient", "Egypt", {"scale": 1})

HEAD["laurel-wreath"] = item("Laurel wreath", "a wreath of laurel or olive leaves round the head, their tips meeting over the brow -- of gold for a victor or a god's priest (the Greek stephane), of the green leaves themselves for a Roman triumph",
    wreath("leaf"),
    {"gold": {"stem": "gold", "leaf": "gold"}, "green": {"stem": "stem-green", "leaf": "leaf"}, "olive": {"stem": "silver", "leaf": "leaf-light"}},
    "classical", "Greece, Rome", {"scale": 1})

HEAD["circlet"] = item("Circlet", "a medieval circlet: a gold band round the head set with cabochons -- rubies, sapphires and emeralds in turn",
    [{"id": "band", "type": "band", "fit": "head", "level": [0.074, 0.058], "width": 0.01, "thick": 0.0025, "material": "metal"},
     *[dict(g, id=g["id"] + " " + str(k)) for k, s in enumerate(["gem1", "gem2", "gem3"]) for g in
       gem({"fit": "head", "ring": {"n": 3, "from": -150 + 30 * k, "to": 150 - 60 + 30 * k}, "level": [0.074, 0.058], "lift": 0.002}, 0.0042, stone=s, scale="scale")]],
    {"gold": {"metal": "gold", "gem1": "ruby", "gem2": "sapphire", "gem3": "emerald"}, "silver": {"metal": "silver", "gem1": "garnet", "gem2": "pearl", "gem3": "sapphire"}},
    "medieval", "Europe", {"scale": 1})

FLEUR = [[0, 0.03], [0.004, 0.022], [0.0035, 0.014], [0.012, 0.022], [0.016, 0.016], [0.011, 0.008], [0.006, 0.006], [0.008, 0.0], [-0.008, 0.0], [-0.006, 0.006], [-0.011, 0.008], [-0.016, 0.016], [-0.012, 0.022], [-0.0035, 0.014], [-0.004, 0.022]]
HEAD["coronet"] = item("Coronet", "a coronet: a gold band with fleurons -- lily-flowers -- standing up round it and a jewel under each",
    [{"id": "band", "type": "band", "fit": "head", "level": [0.072, 0.062], "width": 0.014, "thick": 0.003, "material": "metal"},
     {"id": "fleuron", "type": "plate", "material": "metal", "thick": 0.003, "outline": FLEUR, "scale": "scale", "on": {"fit": "head", "ring": {"n": 8, "from": -180, "to": 180}, "level": [0.079, 0.069], "lift": 0.004}},
     *gem({"fit": "head", "ring": {"n": 8, "from": -180, "to": 180}, "level": [0.072, 0.062], "lift": 0.003}, 0.0035, stone="gem", scale="scale")],
    {"ruby": {"metal": "gold", "gem": "ruby"}, "sapphire": {"metal": "gold", "gem": "sapphire"}}, "late medieval", "Europe", {"scale": 1})

HEAD["flower-chaplet"] = item("Flower chaplet", "a chaplet of flowers: fresh blooms bound on a green cord round the head -- a May Day or a wedding (the flower assets themselves)",
    [{"id": "cord", "type": "band", "fit": "head", "level": [0.076, 0.05], "width": 0.004, "thick": 0.003, "material": "stem"},
     {"id": "bloom", "use": "bloom", "scale": "scale * 0.45", "on": {"fit": "head", "ring": {"n": 11, "from": -165, "to": 165}, "level": [0.076, 0.05], "lift": 0.002}, "at": [0, 0, 0, 0, 90, 0]}],
    {"green": {"stem": "stem-green"}}, "medieval", "Europe",
    {"scale": 1, "bloom": {"pick": ["items/flowers/blooms/daisy", "items/flowers/blooms/rose", "items/flowers/blooms/cornflower", "items/flowers/blooms/buttercup"]}})

HEAD["hairpins"] = item("Hairpins", "a pair of Chinese hairpins (zan) through the hair at the back of the head, each with a flower of gold at its end and beads dangling from it (buyao: 'step-shake')",
    [{"id": "pin", "type": "rod", "material": "metal", "from": [-0.07, 0, 0], "to": [0.07, 0, 0], "r": 0.0016, "sides": 5, "scale": "scale", "on": {"fit": "head", "th": [150, -150], "level": 0.075, "lift": 0.008}},
     {"id": "flower", "type": "plate", "material": "metal", "thick": 0.003, "outline": [[r6(0.012 * math.cos(2 * math.pi * i / 10) * (0.6 + 0.4 * (i % 2))), r6(0.012 * math.sin(2 * math.pi * i / 10) * (0.6 + 0.4 * (i % 2)))] for i in range(10)],
      "scale": "scale", "on": {"fit": "head", "th": [150, -150], "level": 0.075, "lift": 0.01}, "at": [0.07, 0, 0]},
     {"id": "dangle", "type": "sphere", "material": "gem", "r": 0.003, "sides": 6, "scale": "scale", "on": {"fit": "head", "th": [150, -150], "level": 0.075, "lift": 0.012}, "at": [0.07, -0.016, 0]},
     {"id": "dangle 2", "type": "sphere", "material": "gem", "r": 0.0025, "sides": 6, "scale": "scale", "on": {"fit": "head", "th": [150, -150], "level": 0.075, "lift": 0.012}, "at": [0.07, -0.026, 0]}],
    {"gold-jade": {"metal": "gold", "gem": "jade"}, "silver-coral": {"metal": "silver", "gem": "coral"}, "gold-pearl": {"metal": "gold", "gem": "pearl"}}, "tang", "China", {"scale": 1})

HEAD["headband"] = item("Woven headband", "a tablet-woven band tied round the head (a Norse woman's, a Greek or Roman girl's fillet, the vitta)",
    [{"id": "band", "type": "band", "fit": "head", "level": [0.07, 0.055], "width": 0.018, "thick": 0.0018, "material": "band"}],
    {"red": {"band": "braid-gold"}, "blue": {"band": "braid-blue"}, "black": {"band": "braid-black"}, "linen": {"band": "linen"}}, "everywhere", "everywhere", {"scale": 1})

# ======================= EARRINGS (fit "ear": th +90 / -90 the two lobes) ==========================================
BOTH = {"fit": "ear", "th": [90, -90]}
EARS["hoops"] = item("Hoop earrings", "a gold hoop through each lobe",
    [{"id": "hoop", "type": "ring", "material": "metal", "r": 0.011, "tube": 0.0013, "sides": 5, "scale": "scale", "on": BOTH, "at": [0, -0.011, 0, 0, 90, 0]}],
    {"gold": {"metal": "gold"}, "silver": {"metal": "silver"}, "bronze": {"metal": "bronze"}}, "everywhere", "everywhere", {"scale": 1})
EARS["pearl-drops"] = item("Pearl drop earrings", "a gold stud and a pearl hanging under it (the Roman crotalia, the Renaissance drop)",
    [{"id": "stud", "type": "sphere", "material": "metal", "r": 0.0025, "sides": 6, "scale": "scale", "on": BOTH},
     {"id": "wire", "type": "rod", "material": "metal", "from": [0, 0, 0], "to": [0, -0.012, 0], "r": 0.0006, "sides": 4, "scale": "scale", "on": BOTH},
     {"id": "pearl", "type": "sphere", "material": "gem", "r": 0.0045, "sides": 8, "scale": "scale", "on": BOTH, "at": [0, -0.016, 0]}],
    {"pearl": {"metal": "gold", "gem": "pearl"}, "emerald": {"metal": "gold", "gem": "emerald"}, "garnet": {"metal": "gold", "gem": "garnet"}}, "roman, renaissance", "Europe", {"scale": 1})
EARS["disc-studs"] = item("Disc ear studs", "large Egyptian ear studs: a gold disc in each lobe, a coloured boss at its middle",
    [{"id": "disc", "type": "lathe", "material": "metal", "profile": [[0, 0], [0.011, 0], [0.011, 0.002], [0, 0.003]], "sides": 12, "scale": "scale", "on": BOTH, "at": [0, 0, 0.001, 0, 90, 0]},
     {"id": "boss", "type": "sphere", "material": "gem", "r": 0.004, "sides": 6, "scale": "scale", "on": BOTH, "at": [0, 0, 0.003]}],
    {"carnelian": {"metal": "gold", "gem": "carnelian"}, "lapis": {"metal": "gold", "gem": "lapis"}, "faience": {"metal": "faience-white", "gem": "faience-blue"}}, "ancient", "Egypt", {"scale": 1})
EARS["crescents"] = item("Crescent earrings", "gold crescents hanging from the lobes (Greek, Roman and Byzantine)",
    [{"id": "crescent", "type": "plate", "material": "metal", "thick": 0.0018, "scale": "scale", "on": BOTH, "at": [0, -0.004, 0],
      "outline": crescent(0.011, 0.0075)},
     {"id": "bead", "type": "sphere", "material": "gem", "r": 0.0022, "sides": 6, "scale": "scale", "on": BOTH, "at": [0, -0.012, 0.001]}],
    {"gold": {"metal": "gold", "gem": "garnet"}, "gold-blue": {"metal": "gold", "gem": "enamel-blue"}}, "classical, byzantine", "Mediterranean", {"scale": 1})

# ======================= THE JEWELRY WARDROBE: who wears what (people.js drawJewelry) ==============================
N, H, E = "items/jewelry/neck/", "items/jewelry/head/", "items/jewelry/ears/"
def look(w, neck=None, head=None, ears=None):
    o = {"weight": w}
    if neck: o["neck"] = [N + k for k in neck]
    if head: o["head"] = [H + k for k in head]
    if ears: o["ears"] = [E + k for k in ears]
    return o
WEAR = {"name": "Jewelry wardrobe", "kind": "jewelry-wear",
        "hidesNeck": ["hood"],
        "_about": "who wears what on top of their clothes (no necklace under a garment of `hidesNeck`: a hood's cape covers the neck), by style of dress (people.js: makePerson's `style`, `village` for the world's own) and kind of person (a child's list by sex: child10f, child5m...): looks with weights, each a pick of necklaces, headwear and earrings (jewelry.js items) -- a look without one wears none",
        "styles": {
    "village": {"woman": [look(6), look(2, neck=["cross-cord"]), look(1, neck=["pearls"]), look(0.6, neck=["viking-festoon"]), look(1, head=["flower-chaplet"]), look(0.8, head=["headband"]), look(0.4, neck=["cross-cord"], ears=["hoops"])],
                "man": [look(9), look(1.2, neck=["cross-cord"]), look(0.3, neck=["torc"])],
                "child10f": [look(5), look(2, head=["flower-chaplet"]), look(1, neck=["cross-cord"])], "child5f": [look(6), look(2, head=["flower-chaplet"])],
                "child10m": [look(8), look(1, neck=["cross-cord"])], "child5m": [look(1)]},
    "gothic": {"woman": [look(3), look(2, neck=["pearls", "choker"]), look(1.5, head=["circlet"]), look(0.5, neck=["livery-collar"], head=["coronet"]), look(1, neck=["choker"], ears=["pearl-drops"])],
               "man": [look(5), look(2, neck=["livery-collar"]), look(0.5, head=["circlet"])],
               "child10f": [look(3), look(1, head=["flower-chaplet", "headband"])], "child10m": [look(1)], "child5f": [look(1)], "child5m": [look(1)]},
    "greek": {"woman": [look(3), look(2, neck=["greek-fringe"], ears=["crescents"]), look(1.5, neck=["chain-pendant"]), look(1.5, head=["headband"], ears=["crescents", "hoops"]), look(0.6, head=["laurel-wreath"])],
              "man": [look(6), look(1.5, head=["laurel-wreath"])],
              "child10f": [look(3), look(1, head=["headband"])], "child10m": [look(1)], "child5f": [look(1)], "child5m": [look(1)]},
    "roman": {"woman": [look(3), look(2, neck=["pearls"], ears=["pearl-drops"]), look(1.5, neck=["chain-pendant"], ears=["pearl-drops", "crescents"]), look(1, head=["headband"])],
              "man": [look(6), look(0.8, head=["laurel-wreath"])],
              "child10m": [look(2), look(3, neck=["bulla"])], "child5m": [look(1), look(3, neck=["bulla"])], "child10f": [look(3), look(1, head=["headband"])], "child5f": [look(1)]},
    "chinese": {"woman": [look(2), look(3, head=["hairpins"]), look(1.5, neck=["jade-bi"], head=["hairpins"]), look(1, ears=["hoops"], head=["hairpins"])],
                "man": [look(6), look(1, neck=["jade-bi"])],
                "child10f": [look(3), look(1, head=["hairpins"])], "child10m": [look(1)], "child5f": [look(1)], "child5m": [look(1)]},
    "egyptian": {"woman": [look(1), look(3, neck=["wesekh"], ears=["disc-studs"]), look(1, neck=["wesekh"], head=["seshed-circlet"], ears=["disc-studs"]), look(1, neck=["pectoral"])],
                 "man": [look(2), look(3, neck=["wesekh"]), look(1, neck=["pectoral"]), look(0.2, neck=["wesekh"], head=["uraeus-diadem"])],
                 "child10f": [look(2), look(1, neck=["wesekh"])], "child10m": [look(2), look(1, neck=["wesekh"])], "child5f": [look(1)], "child5m": [look(1)]},
}}


def main():
    for k, v in NECK.items(): write("neck/" + k, v)
    for k, v in HEAD.items(): write("head/" + k, v)
    for k, v in EARS.items(): write("ears/" + k, v)
    write("wear", WEAR)
    mpath = os.path.join(ITEMS, "materials.json")
    lib = json.load(open(mpath)); added = 0
    for k, v in MATERIALS.items():
        if k not in lib["materials"]: lib["materials"][k] = {"pattern": "materials/paint", "palette": [v, v, v, v]}; added += 1
    json.dump(lib, open(mpath, "w"), indent=1, ensure_ascii=False)
    ip = os.path.join(ROOT, "assets", "index.json"); idx = json.load(open(ip))
    idx["categories"] = [c for c in idx["categories"] if c["name"] != "Items: jewelry"]
    pos = next(i for i, c in enumerate(idx["categories"]) if c["name"] == "Items: flowers") + 1
    idx["categories"].insert(pos, {"name": "Items: jewelry", "kind": "item", "paths": [N + k for k in NECK] + [H + k for k in HEAD] + [E + k for k in EARS]})
    json.dump(idx, open(ip, "w"), indent=2, ensure_ascii=False); open(ip, "a").write("\n")
    print(len(NECK), "necklaces,", len(HEAD), "headwear,", len(EARS), "earrings;", added, "materials added")


if __name__ == "__main__": main()
