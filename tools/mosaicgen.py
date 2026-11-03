#!/usr/bin/env python3
"""The mosaic family: assets/patterns/mosaic.json (mosaic.js, docs/mosaic.md). Run from anywhere.
A pattern is one layer { kind: "mosaic", layers: [the drawing], ... }; its stones and grout are metres, so they stay true to the tile."""
import json, math, os

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "patterns", "mosaic.json")

PALETTES = {
    # 0 gold, 1 light gold, 2 dark gold, 3 ruby, 4 lapis, 5 white, 6 dark, 7 flesh, 8 green, 9 shadow flesh, 10 purple, 11 sky, 12 brown, 13 grey
    "gold-stone": ["#d0a845", "#efd478", "#a98332", "#8d2b20", "#27386b", "#efe6d0", "#2a211a", "#d0a27a", "#4d6b4a", "#9c6e4e", "#5b2a6e", "#5f7fa6", "#6a4a2c", "#8b8676"],
    "opus-bw": ["#e8e1d2", "#1d1c1f", "#c9bda6"],
    # 0 white marble, 1 black, 2 limestone, 3 terracotta, 4 flesh, 5 brown, 6 blue-grey, 7 green, 8 yellow, 9 deep red, 10 shadow flesh; then the shadow stones of 3, 6, 8, 7, 0, 2
    "opus-stone": ["#e7e0cf", "#1e1c1d", "#b9a27c", "#a8502f", "#cf9a6c", "#6f452b", "#566b70", "#6f7f52", "#d8b650", "#8a2f25", "#a06a45", "#7a3a22", "#3e4f54", "#a88a38", "#4d5a3a", "#c4bba4", "#8d7a5a"],
}

def floor(about, size, drawing, palette="opus-bw", palettes=("opus-stone",), stone=.016, res=512, **k):
    L = {"kind": "mosaic", "stone": stone, "joint": .11, "groutColor": "#6e685b", "seed": 3, **k, "layers": drawing}
    return {"size": list(size), "palette": palette, "palettes": list(palettes), "ground": 0, "res": res, "_about": about, "layers": [L]}

def meander(W, H, x0=0, n=2, band=.018):
    """a key running along x: rises, turns in, comes back out, and goes on; two bands up the tile's height"""
    u = W / n
    # (the key as closed strokes, tile by tile, so nothing depends on where it wraps)
    lines = []
    for i in range(n):
        o = -W / 2 + i * u
        path = [[o, -.3 * H], [o + .85 * u, -.3 * H], [o + .85 * u, .3 * H], [o + .2 * u, .3 * H], [o + .2 * u, -.08 * H], [o + .55 * u, -.08 * H], [o + .55 * u, .08 * H]]
        lines.append({"shape": "spline", "closed": False, "tension": 0, "points": path, "stroke": 1, "line": band, "cap": "square"})
        lines.append({"shape": "line", "from": [o + .85 * u, -.3 * H], "to": [o + u, -.3 * H], "stroke": 1, "line": band})
    return lines

bars = lambda W, y, t, s=1: [{"shape": "rect", "w": W * 3, "h": t, "at": [[0, y], [0, -y]], "fill": s}]

PATTERNS = {
    "tessellatum plain": floor("a plain floor: white stones in straight rows, a little wandering", [1.28, 1.28], [], stone=.02, halo=0),
    "tessellatum dark": floor("the same in black, with lighter joints", [1.28, 1.28], [{"shape": "rect", "w": 4, "h": 4, "fill": 1}], stone=.02, halo=0),
    "bw chequer": floor("black and white squares, a row of stones hugging each", [.8, .8], [{"shape": "rect", "w": .2, "h": .2, "at": [[-.2, -.2], [0, 0], [.2, -.2], [-.4, 0], [.4, 0], [-.2, .2], [.2, .2], [0, -.4], [0, .4]], "fill": 1}], stone=.02),
    "bw meander": floor("a Greek key between two lines, the border and field of a Roman floor", [.72, .36], bars(.72, .155, .02) + meander(.72, .3, n=2, band=.042), stone=.012, lay="x"),
    "bw wave": floor("a running wave, black over white", [.6, .2], [{"shape": "wave", "h": .05, "amp": .05, "n": 2, "fill": 1}] + bars(.6, .085, .02), stone=.012),
    "bw hexagons": floor("hexagons in outline, the commonest Roman field", [2 * 3 ** .5 * .17, 3 * .17], [{"shape": "poly", "n": 6, "r": .17, "grid": {"n": [2, 2], "offset": .5}, "stroke": 1, "line": .024}], stone=.011),
    "bw scales": floor("overlapping scales in outline", [.6, .6], [{"shape": "circle", "r": .15, "grid": {"n": [2, 4], "offset": .5}, "fill": 0, "stroke": 1, "line": .018}], stone=.012),
    "bw star8": floor("eight-point stars laid in black over white: Islamic geometry's Roman cousin", [.8, .8], [{"kind": "stars", "n": 8, "k": 2, "gap": 0, "angle": 67.5, "cells": [1, 1], "fills": [1, 0, 2, 0], "band": .04, "edge": 0, "strap": 1, "weave": False}], stone=.014),
    "bw guilloche": floor("a guilloche in stone: two strands round white eyes", [.42, .21], [{"kind": "knot", "cols": 2, "rows": 1, "wrap": "x", "margin": .012, "band": .42, "edge": .06, "strap": 2, "strapEdge": 1, "eye": 1, "eyeSize": .14}], stone=.008),
}
def gold(about, size, drawing=(), stone=.014, res=512, **k):
    L = {"kind": "mosaic", "stone": stone, "joint": .13, "groutColor": "#54422a", "seed": 5, "tone": .05, "gleam": .34, "wander": .3, "jitter": [.4], "halo": 1, "mix": {"0": [0, 0, 0, 0, 0, 1, 2]}, **k, "layers": list(drawing)}
    return {"size": list(size), "palette": "gold-stone", "ground": 0, "res": res, "_about": about, "layers": [L]}

PATTERNS.update({
    "gold ground": gold("Byzantine gold ground: glass tesserae set by hand, each at its own angle to the light, the rows wandering", [1.28, 1.28]),
    "gold braid": gold("a plait in ruby and lapis on gold, for an arch or a band", [.48, .24], [{"kind": "knot", "cols": 4, "rows": 2, "wrap": "x", "margin": .01, "band": .38, "edge": .06, "strap": 3, "strapEdge": 6}, {"shape": "rect", "w": 2, "h": .012, "at": [[0, .105], [0, -.105]], "fill": 6}], stone=.0075),
    "gold scales": gold("gold scales edged in ruby, a vault's ornament", [.6, .6], [{"shape": "circle", "r": .15, "grid": {"n": [2, 4], "offset": .5}, "fill": 1, "stroke": 3, "line": .014}], stone=.012),
})

# FIGURES on gold (medieval.js): frontal, flat, every saint a line of ink and a colour. The tympanum's fathers stand on the piers between its windows.
def saint(x, foot, h, **F):
    return {"kind": "figure", "at": [x, foot], "h": h, "line": .012, "seed": 1 + round(x * 10), "figure": {"robe": 5, "mantle": 4, "skin": 7, "shoes": 6, "halo": 1, "attr": 3, **F}}
FLESH = {"3": [-.12, -.03, .05], "4": [-.12, -.03, .06], "5": [-.1, -.02, .03], "7": [-.12, -.04, .05, .08]}
PATTERNS.update({
    "gold fathers": gold("the church fathers of the tympana, one to a pier, a green ground under them: its tile three bays of the wall's windows", [3, 2.5], [
        {"shape": "rect", "w": 3.1, "h": .15, "at": [0, -1.15], "fill": 8},
        {"shape": "rect", "w": 3.1, "h": .018, "at": [0, -1.065], "fill": 3},
        saint(-1, -1.035, 1.56, pose="book", holdR="book", mantle=6, hair=5, beard=5),
        saint(0, -1.035, 1.56, pose="bless", hair=6, beard=6, mantle=3),
        saint(1, -1.035, 1.56, pose="book", holdR="book", mantle=4, hair=2, beard=6),
    ], stone=.02, model=FLESH),
    "gold virgin": gold("the Virgin and Child enthroned, for a half dome: a third of the way round it, so her neighbours fall off a half dome's sides, and as tall as a rule's reach up it", [3.84, 2.2], [
        {"shape": "rect", "w": 1.04, "h": 1.22, "at": [0, -.45], "fill": 2},
        {"shape": "rect", "w": .94, "h": .12, "at": [0, -.42], "fill": 3},
        {"shape": "rect", "w": 1.22, "h": .08, "at": [0, -1.05], "fill": 3},
        saint(0, -1.02, 1.7, pose="sit", robe=4, mantle=4, veil=4, shoes=3),
        saint(0, -.54, .62, pose="bless", robe=1, mantle=1, hair=6, crossNimbus=True, halo=5, shoes=2),
    ], stone=.013, res=1024, model=FLESH),
})
PATTERNS["gold virgin"]["across"] = 2   # (twice as wide as the array's layer: her stones at the game's texels)

# a guilloche for a frame: the slots of opus-stone, not a mosaic of its own: it's part of a drawing
PATTERNS["part guilloche"] = {"size": [.12, .06], "palette": "opus-stone", "ground": 0, "res": 256, "_about": "(a border's drawing, used inside the emblemata)", "layers": [{"kind": "knot", "cols": 2, "rows": 1, "wrap": "x", "margin": .004, "band": .5, "edge": .15, "strap": 3, "strapEdge": 1, "eye": 1, "eyeSize": .1}]}

def emblem(about, painting, seed=1, size=(1.2, 1.2), band=.095, stone=.0095, res=512, **k):
    """a panel: a figure scene, a guilloche round it on black lines: laid as one, so rows run on from one to the next"""
    W, H = size; X = W / 2 - .025 - band / 2; Y = H / 2 - .025 - band / 2; inner = [W - 2 * (band + .05), H - 2 * (band + .05)]
    def along(n, at, rot=0):       # (a whole number of the guilloche's turns along a side)
        t = n - .05; s = t / (max(1, round(t / (2 * band))) * .12)   # (one plait, as high as the band: a taller tile would start a second)
        return {"shape": "rect", "w": n, "h": .06 * s, "at": at, "rot": rot, "use": "mosaic/part guilloche", "useScale": s}
    corners = [[X, Y], [-X, Y], [X, -Y], [-X, -Y]]
    frame = [along(W, [0, Y]), along(W, [0, -Y]), along(H, [X, 0], 90), along(H, [-X, 0], 90),
             {"shape": "rect", "w": band * 1.04, "h": band * 1.04, "at": corners, "fill": 3},     # (the bands meet under a square, each corner the same)
             {"shape": "circle", "r": band * .28, "at": corners, "fill": 0},
             {"shape": "frame", "w": W - .012, "h": H - .012, "t": .018, "fill": 1},
             {"shape": "frame", "w": inner[0] + .02, "h": inner[1] + .02, "t": .014, "fill": 1}]
    L = {"kind": "mosaic", "stone": stone, "joint": .11, "groutColor": "#5a5448", "seed": 3 + seed, "halo": 2, "flow": [4, 10], "fine": {"3": .85, "4": .8, "10": .8}, "tone": .06, "ground": 0,
         "model": {"2": [-.14, -.04, .05], "3": [-.14, -.04, .05], "5": [-.14, -.04, .05], "6": [-.14, -.04, .05], "7": [-.14, -.04, .05], "4": [-.14, -.03, .06, .1], "10": [-.1, -.02, .04]}, **k, "layers": [{"kind": "greek", "painting": painting, "seed": seed, "box": inner}] + frame}
    return {"size": list(size), "repeat": False, "palette": "opus-stone", "ground": 0, "res": res, "_about": about, "layers": [L]}

WIDE = (1.76, 1.2)
PATTERNS.update({
    "emblem lions": emblem("an emblema: beasts, in a guilloche frame", "emblem-lions", size=WIDE, band=.14, stone=.0135),
    "emblem nemean": emblem("Herakles and the lion", "emblem-nemean", size=WIDE, band=.14, stone=.0135),
    "emblem thiasos": emblem("a Dionysian procession", "emblem-thiasos"),
    "emblem sphinxes": emblem("sphinxes", "emblem-sphinxes", size=WIDE, band=.14, stone=.0135),
    "emblem centaurs": emblem("a centaur going down", "emblem-centaurs"),
    "emblem duel": emblem("two warriors", "emblem-duel"),
})
# THE SEED'S FLOORS AND WALLS (mosaic/floor.js): a subject, or none; all else from the seed. Their people come from assets/story/canon.json
MODEL = {"2": [-.12, -.03, .05], "3": [-.14, -.04, .05], "4": [-.14, -.03, .06, .1], "5": [-.12, -.03, .05], "6": [-.14, -.04, .05], "7": [-.14, -.04, .05], "8": [-.1, -.02, .05], "9": [-.12, -.03, .05]}
def roman(about, subject="any", size=(1.6, 1.6), stone=.0115, across=1, **k):
    pl = {"kind": "floor", "subject": subject, **k}
    L = {"kind": "mosaic", "stone": stone, "joint": .11, "groutColor": "#5a5448", "seed": 3, "halo": 2, "flow": [4, 10], "fine": {"4": .9, "10": .9}, "thin": .45, "tone": .06, "ground": 0, "model": MODEL, "plan": pl, "layers": []}
    p = {"size": list(size), "repeat": False, "palette": "opus-stone", "ground": 0, "res": 512 * across, "_about": about, "layers": [L]}
    if across > 1: p["across"] = across
    return p
def wall(about, subject="any", size=(1.5, 1.5), stone=.0125, across=1, **k):
    p = gold(about, size, [], stone=stone, res=512 * across, model=FLESH, plan={"kind": "wall", "subject": subject, **k}); p["repeat"] = False
    if across > 1: p["across"] = across
    return p
LONG = {"size": (2.6, 1.3), "stone": .0135, "across": 2}   # (twice as wide as a layer of the array: a long wall at the same stones)
PATTERNS.update({
    "floor any": roman("a Roman floor: its frame, its layout, what's in it, all the seed's"),
    "floor wide": roman("a floor twice as long as it's wide: an emblema or two panels", size=(2.4, 1.2), stone=.0115, across=2),
    "floor hunt": roman("hunters after the boar, the stag, the lion, the hare", "hunt"),
    "floor arena": roman("gladiators, net-fighters, beast fights, a victor", "arena"),
    "floor neptune": roman("Neptune's triumph: frontal, drawn by sea horses, or among his creatures", "neptune"),
    "floor dionysus": roman("Dionysus: in his chariot, on his panther, or the vintage", "dionysus"),
    "floor orpheus": roman("Orpheus and the beasts, a wheel of compartments", "orpheus"),
    "floor seasons": roman("a story at the heart, the four seasons' heads at the corners", layout="seasons"),
    "floor sea": roman("the sea: fish, dolphins, an octopus", "sea"),
    "floor xenia": roman("xenia: what a host sets out, in compartments", "xenia"),
    "floor ostia": roman("Ostia's black and white: figures in black silhouette on white, their lines picked out", bw=True),
    "wall any": wall("a wall of a Byzantine church: what it shows, gold or night, its bands, the seed's", **LONG),
    "wall pantocrator": wall("Christ Pantocrator: the bust, the book, the blessing", "bust"),
    "wall virgin": wall("the Virgin and Child enthroned", "virgin"),
    "wall deesis": wall("the Deesis: Christ between his Mother and the Baptist", "deesis", **LONG),
    "wall emperor": wall("an emperor with his court", "court", **LONG),
    "wall empress": wall("an empress with her ladies", "empress", **LONG),
    "wall apostles": wall("the apostles in a row", "apostles", **LONG),
    "wall fathers": wall("church fathers, frontal, hieratic", "fathers", **LONG),
    "wall shepherd": wall("the Good Shepherd among his sheep", "shepherd", **LONG),
    "wall lambs": wall("twelve lambs and the Lamb", "lambs", **LONG),
    "wall cross": wall("an apse's jewelled cross in a starry heaven", "cross", ground="blue"),
    "wall roundels": wall("busts in roundels, jewelled", "roundels", **LONG),
    "wall arcade": wall("saints under arches", "arcade", **LONG),
})
def field(about, size=(1.2, 1.2), stone=.013, palette="opus-bw", schemes=[[1, 1, 2, 1, 0]], **k):
    p = floor(about, size, [], palette=palette, stone=stone, plan={"kind": "field", "schemes": schemes, **k})
    return p
COLOUR = [[1, 3, 8, 1, 0], [6, 3, 8, 1, 0], [9, 5, 8, 1, 0], [7, 1, 8, 5, 2], [3, 6, 0, 1, 2], [5, 7, 8, 1, 0], [1, 9, 2, 1, 0], [6, 1, 2, 1, 15]]
PATTERNS.update({
    "field bw": field("a Roman geometric field in black and white; the seed picks which"),
    "field colour": field("a geometric field in the floor's stones; which and in which colours, the seed's", palette="opus-stone", schemes=COLOUR),
    "strip any": {**floor("a border's band, tiling along: guilloche, key, wave, dentils, chequer...", [.72, .24], [], palette="opus-stone", stone=.0075, plan={"kind": "strip", "schemes": COLOUR}), },
})
# (what the finishes hold keeps its drawing at its own seed; any other seed is the same kind of thing, newly drawn)
BW = {"field": lambda **k: {"kind": "field", "schemes": [[1, 1, 2, 1, 0]], **k}}
PATTERNS["bw hexagons"]["layers"][0]["plan"] = {"kind": "field", "field": "hexagons", "keep": 3, "n": 3, "schemes": [[1, 1, 2, 1, 0]]}
PATTERNS["bw chequer"]["layers"][0]["plan"] = {"kind": "field", "keep": 3, "fields": ["chequer", "chequer", "lozenges", "chevrons", "triangles", "basket"], "stone": .015, "set": {"wander": .35, "thin": .3}, "sets": {"chequer": {"stone": .02, "set": {"wander": .35}}}, "schemes": [[1, 1, 2, 1, 0]]}   # (`wander`: a true chequer's rows and columns average out, so nothing in the drawing masks the courses of stones running straight across the tile. `thin`: a sharp tip is no line, and a line's stones lie over what's beside it)
PATTERNS["bw scales"]["layers"][0]["plan"] = {"kind": "field", "field": "scales", "keep": 3, "schemes": [[1, 1, 2, 1, 0]]}
PATTERNS["bw star8"]["layers"][0]["plan"] = {"kind": "field", "keep": 3, "fields": ["octagons", "stars", "rosettes", "petals"], "n": 3, "stone": .0075, "schemes": [[1, 1, 2, 1, 0]]}
PATTERNS["bw meander"]["layers"][0]["plan"] = {"kind": "strip", "keep": 3, "strips": ["meander", "tkey", "wave", "lozenges", "dentil"], "schemes": [[1, 1, 2, 1, 0]]}
PATTERNS["bw wave"]["layers"][0]["plan"] = {"kind": "strip", "keep": 3, "strips": ["wave", "saw", "dentil", "beads"], "schemes": [[1, 1, 2, 1, 0]]}
PATTERNS["bw guilloche"]["layers"][0]["plan"] = {"kind": "strip", "keep": 3, "stone": .0062, "strips": ["guilloche", "plait", "ivy"], "schemes": [[1, 2, 0, 1, 0]]}
PATTERNS["gold braid"]["layers"][0]["plan"] = {"kind": "strip", "keep": 5, "stone": .0085, "strips": ["plait", "guilloche", "lozenges", "beads", "chequer", "saw"], "schemes": [[3, 4, 5, 6, 0], [4, 3, 1, 6, 0], [3, 8, 5, 6, 0], [5, 3, 1, 6, 4]]}
PATTERNS["gold scales"]["layers"][0]["plan"] = {"kind": "field", "field": "scales", "keep": 5, "schemes": [[1, 3, 5, 3, 0], [4, 3, 1, 6, 0], [3, 1, 5, 6, 0]]}
PATTERNS["gold virgin"]["layers"][0]["plan"] = {"kind": "wall", "subject": "virgin", "keep": 5, "bands": False, "reach": .74}
PATTERNS["gold fathers"]["pinned"] = True   # (its figures stand between one building's windows: every world keeps them there. architecture.js seedFinishes)
PATTERNS["gold fathers"]["layers"][0]["plan"] = {"kind": "wall", "subject": "fathers", "keep": 5, "bands": False, "ground": "gold", "piers": [-1, 0, 1], "h": 1.56, "foot": -1.035, "sill": [-1.15, .15]}
for n, s in [("lions", 3 + 1), ("nemean", 4), ("thiasos", 4), ("sphinxes", 4), ("centaurs", 4), ("duel", 4)]:
    PATTERNS[f"emblem {n}"]["layers"][0]["follow"] = -3    # (a seed here is a new painting of the same subject, drawn by the Greek engine)
for p in PATTERNS.values():
    for L in p["layers"]:
        for q in L.get("layers", []):
            if q.get("fill", 0) is None: del q["fill"]
doc = {"name": "Mosaic", "_about": "TESSERAE OVER A DRAWING (mosaic.js, docs/mosaic.md): generated by tools/mosaicgen.py", "palettes": PALETTES, "patterns": PATTERNS}
with open(OUT, "w") as f:
    json.dump(doc, f, indent=1)
print(len(PATTERNS), "patterns")
