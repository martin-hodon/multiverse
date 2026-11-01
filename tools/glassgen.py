#!/usr/bin/env python3
"""The stained glass family: assets/patterns/glass.json (glass.js, docs/glass.md). Run from anywhere.
A pattern is one layer { kind: "glass", form, ... }; all its numbers are metres in the tile, a window's size being set by the finish's map."""
import json, os

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "patterns", "glass.json")

# 0 cobalt 1 ruby 2 gold 3 emerald 4 white 5 flesh 6 purple 7 sky blue 8 amber 9 dark blue
CHARTRES = ["#1d44a8", "#b0161c", "#e4ad22", "#1f7a45", "#dfe0cc", "#e0b596", "#6a2c7e", "#4f83c8", "#c9721c", "#142c74"]
PALETTES = {
    "chartres": CHARTRES,
    # (brighter and more red and violet, later: the Sainte-Chapelle's)
    "paris": ["#3550b4", "#c0182c", "#efc437", "#27884e", "#e8e6d4", "#e6bd9f", "#8a3596", "#6c98d8", "#de8a24", "#1d3288"],
    "cologne": ["#2a58a6", "#a72422", "#e8c04b", "#3b8253", "#eae5cf", "#e5c0a4", "#764084", "#79a4d2", "#d08a2c", "#1e3a7e"],
    # (the white glass of a Cistercian: shades of grey-green and straw, a little colour)
    "grisaille": ["#cfd2bb", "#bcc2a8", "#dcd8bd", "#a8b49d", "#e9e6d1", "#d6b98c", "#a4493f", "#7f97a8", "#c9a657", "#8d9a88"],
}

def rose(about, rings, ground=0, palette="chartres", **k):
    # (the armature: every ring's ground is sectors, its irons and leads running out from the eye; so a pane of ground holds one shape, not all of them)
    back = [{"shape": "sector", "r0": r["r0"], "r1": 1.02 if r is rings[-2] else rings[i + 1]["r0"] if rings[i + 1].get("r0") else r["r1"], "n": r["n"], "turn": r.get("turn", 0), "fill": ground, "role": "ground"} for i, r in enumerate(rings) if r.get("n", 1) > 1]
    rings = back + rings
    L = {"kind": "glass", "form": "rose", "opening": {"shape": "circle"}, "ground": ground, "rings": rings, "lead": .011, "minPane": .00035, "maxPane": .02, "seed": 3, **k}
    return {"size": [2, 2], "repeat": False, "palette": palette, "palettes": list(PALETTES), "ground": 0, "res": 512, "_about": about, "layers": [L]}

# THE CAST. Slots: 0 cobalt 1 ruby 2 gold 3 emerald 4 white 5 flesh 6 purple 7 sky 8 amber 9 dark blue
PETER = {"pose": "book", "robe": 7, "mantle": 2, "beard": 4, "hair": 4, "halo": 8, "holdL": "key", "holdR": "book", "attr": 2}
PAUL = {"pose": "bless", "robe": 3, "mantle": 1, "beard": 8, "hair": 8, "halo": 2, "holdR": "sword", "attr": 4}
BISHOP = {"pose": "bless", "robe": 4, "mantle": 6, "beard": 4, "hair": 4, "halo": 2, "mitre": 2, "holdR": "staff", "attr": 2}
VIRGIN = {"pose": "offer", "robe": 1, "mantle": 0, "veil": 4, "halo": 2, "crown": 2}
MAJESTY = {"pose": "sit", "robe": 1, "mantle": 0, "beard": 8, "hair": 8, "halo": 2, "crossNimbus": True, "bless": "L", "holdR": "book", "attr": 4}
ANGEL = {"pose": "orant", "robe": 4, "mantle": 2, "hair": 8, "halo": 2, "wings": 7}
MARTYR = {"pose": "orant", "robe": 2, "mantle": 1, "veil": 3, "halo": 4, "holdL": "palm", "attr": 3}
KING = {"pose": "stand", "robe": 6, "mantle": 1, "beard": 8, "hair": 8, "crown": 2, "holdL": "staff", "attr": 2}

def stone(lights, about):
    L = {"kind": "glass", "form": "stone", "opening": {"shape": "circle"}, "lights": lights, "ground": 9, "fills": [0, 1], "hub": 2, "roundel": [1, 3, 2], "cast": [ANGEL, PETER, MARTYR, BISHOP, ANGEL, PAUL, KING, VIRGIN], "hubCast": [{**MAJESTY, "pose": "bless"}], "lead": .009, "minPane": .0004, "maxPane": .08, "depth": .4, "seed": 3}
    return {"size": [2, 2], "repeat": False, "palette": "chartres", "palettes": list(PALETTES), "ground": 0, "res": 512, "_about": about, "layers": [L]}

PATTERNS = {
    "rose wheel": rose("a wheel: spokes of lancet lights about a small eye, a ring of roundels", [
        {"shape": "petal", "r0": .16, "r1": .74, "n": 12, "fills": [1, 0], "gap": .05, "inner": {"k": .5, "fills": [2, 4]}},
        {"shape": "round", "r0": .74, "r1": .98, "n": 12, "turn": .5, "fills": [0, 1], "inner": {"k": .55, "fills": [2, 3]}},
        {"r1": .16, "fill": 2},
    ], ground=9),
    "rose chartres": rose("Chartres, the west rose: an eye, petals, then rings of squares and quatrefoils, cobalt ground", [
        {"shape": "round", "r0": .14, "r1": .44, "n": 12, "fills": [1], "inner": {"k": .62, "fills": [2]}},
        {"shape": "square", "r0": .44, "r1": .66, "n": 12, "fills": [1, 2], "inner": {"k": .55, "fills": [4]}},
        {"shape": "quatrefoil", "r0": .66, "r1": .98, "n": 12, "fills": [0, 1], "turn": .5, "inner": {"k": .55, "fills": [2, 3]}},
        {"r1": .15, "fill": 2}, {"r1": .08, "fill": 1},
    ], ground=0),
    "rose paris": rose("Paris, the north rose: twelve lights doubling to twenty-four, then twenty-four roundels at the rim", [
        {"shape": "petal", "r0": .13, "r1": .46, "n": 12, "fills": [0, 1], "gap": .04, "inner": {"k": .5, "fills": [2, 4]}},
        {"shape": "petal", "r0": .46, "r1": .78, "n": 24, "fills": [1, 0, 6, 0], "gap": .04, "inner": {"k": .45, "fills": [2, 4]}},
        {"shape": "round", "r0": .78, "r1": .985, "n": 24, "turn": .5, "fills": [0, 1, 2, 1], "inner": {"k": .5, "fills": [4, 2]}},
        {"r1": .13, "fill": 2},
    ], ground=9, palette="paris"),
    "rose stone 8": stone(8, "the glass for a stone rose of eight lights: what the mason's bars enclose"),
    "rose stone 10": stone(10, "of ten lights"),
    "rose stone 12": stone(12, "of twelve lights"),
    "rose stone 14": stone(14, "of fourteen lights"),
    "rose stone 16": stone(16, "of sixteen lights"),
}

def light(about, panels, h=3, palette="chartres", border=None, res=512, **k):
    # A LIGHT: what one row of an opening between mullions holds, a rectangle one wide and h tall that stacks on itself. The stone
    # decides the rows (arch/finish.js: tall ones of aspect 2.2-3.75, else near square) and a picture fills its row, so h is what it's nearest.
    B = {"t": .11, "fills": [1, 0, 2, 0], "pearl": 4, "line": 9, "block": .16} if border is None else border
    # (with no border, or one up its sides only, the opening runs past the tile, so no lead follows that edge: a field that repeats)
    grow = 1.04 if not B.get("t") else 1
    tall = 1.04 if B.get("sides") else grow
    L = {"kind": "glass", "form": "light", "lie": h > 1.3, "opening": {"shape": "rect", "w": grow, "h": h * tall}, "border": B, "panels": panels, "lead": .0075, "minPane": .00012, "maxPane": .08, "maxAspect": 6, "depth": .3, "ground": [1, 9], "fleuron": 7, "pearl": 4, "seed": 3, **k}
    if not L["lie"]: return {"size": [1, h], "repeat": True, "palette": palette, "palettes": list(PALETTES), "ground": 0, "res": res, "_about": about, "layers": [L]}
    # (kept lying, over as many layers of the game's tile array as it is long: a finish's rule gives it turn: 90)
    across = max(1, round(h))
    return {"size": [h, 1], "across": across, "repeat": True, "palette": palette, "palettes": list(PALETTES), "ground": 0, "res": res * across, "_about": about, "layers": [L]}

def saint(who, about, ground=1, arch=None, **k):
    return light(about, [{"form": "saint", "h": 1, "cast": [who], "ground": ground, "canopy": 2, "canopy2": 4, "base": 3, "spring": .74, **({"arch": arch} if arch is not None else {})}], **k)

SHIP = {"form": "medallion", "shape": "circle", "ground": 7, "cast": [{**PETER, "pose": "stand", "holdL": None, "holdR": None, "x": -14, "size": .55, "y": 22, "turn": .6}, {**PAUL, "holdR": None, "pose": "point", "x": 16, "size": .55, "y": 22, "turn": -.6}], "props": [{"is": "ship", "y": 8, "size": .85}, {"is": "wave", "y": 2, "size": 1.1}]}
ANNUNCIATION = {"form": "medallion", "shape": "circle", "ground": 0, "cast": [{**ANGEL, "pose": "point", "x": -22, "size": .78, "turn": .6}, {**VIRGIN, "pose": "stand", "crown": None, "x": 24, "size": .78, "turn": -.6}]}
KINGS = {"form": "medallion", "shape": "circle", "ground": 0, "cast": [{**KING, "x": -24, "size": .72, "turn": .6}, {**KING, "pose": "offer", "robe": 3, "x": 2, "size": .72, "turn": .6}], "props": [{"is": "tower", "x": 34, "size": .8, "fill": 4}, {"is": "ground", "y": 0, "fill": 3}]}
ENCOUNTER = {"form": "medallion", "shape": "circle", "ground": 0, "cast": [{**BISHOP, "x": -24, "size": .82, "turn": .6}, {**KING, "x": 26, "size": .82, "turn": -.6}]}
THRONED = {"form": "medallion", "shape": "quatrefoil", "ground": 0, "cast": [{**MAJESTY, "size": .95}], "props": [{"is": "throne", "fill": 2, "size": .95}]}
ANGELS = {"form": "medallion", "shape": "lozenge", "ground": 0, "cast": [{**ANGEL, "size": .72}], "drop": .25}
WHITE = {"palette": "grisaille", "border": {"t": .06, "sides": True, "fills": [6, 8], "line": 3, "block": .18}}

PATTERNS.update({
    "saint peter": saint(PETER, "Saint Peter under a canopy, a ruby ground, as in Chartres's choir clerestory"),
    "saint paul": saint(PAUL, "Saint Paul, on cobalt", ground=0, arch=1),
    "saint bishop": saint(BISHOP, "a bishop, on cobalt", ground=0, arch=1),
    "saint virgin": saint(VIRGIN, "the Virgin, on ruby", arch=0),
    "saint king": saint(KING, "a king, on ruby", arch=0),
    "saint martyr": saint(MARTYR, "a martyr with her palm, on cobalt", ground=0, arch=1),
    "medallion stack": light("three medallions on a red and blue diaper: a story told upwards", [ENCOUNTER, THRONED, ANGELS], h=3.3),
    "medallion story": light("a narrative light: a ship on the sea, an annunciation, the three kings at a tower", [SHIP, ANNUNCIATION, KINGS], h=3.3),
    "medallion ship": light("one medallion, for a short light", [SHIP], h=1.1),
    "medallion annunciation": light("one medallion: an annunciation", [ANNUNCIATION], h=1.1),
    "medallion kings": light("one medallion: the kings", [KINGS], h=1.1),
    "medallion majesty": light("one medallion: a majesty", [THRONED], h=1.1),
    "grisaille lattice": light("white glass painted with vine, the Cistercian's", [{"form": "grisaille", "h": 1, "d": 1 / 6}], h=1, fleuron=None, **WHITE),
    "grisaille strap": light("grisaille with a strapwork circle, colour at the knots", [{"form": "grisaille", "h": 1, "d": 1 / 6, "strap": {"n": 1, "fill": 4, "knot": 6, "knot2": 8}}], h=1, **WHITE),
    "quarries": light("plain diamonds in lead: a parish's window", [{"form": "grisaille", "h": 1, "vine": False, "d": .2}], h=1, palette="grisaille", border={"t": .035, "sides": True, "fills": [4], "line": 4, "block": .22}, minPane=.00006),
    "tracery diaper": light("what fills the eyes of a window's tracery: a lattice, plain metres, cut by the stone", [{"form": "grisaille", "h": 1, "whites": [1, 0, 1, 9], "vine": False, "d": .25}], h=1, border={"t": 0, "fills": [9], "block": 9}, ironBars=False),
    "tracery white": light("the same in grisaille", [{"form": "grisaille", "h": 1, "vine": False, "d": .25}], h=1, palette="grisaille", border={"t": 0, "fills": [4], "block": 9}, ironBars=False),
})
doc = {"name": "Stained glass", "_about": "STAINED GLASS (glass.js, docs/glass.md): generated by tools/glassgen.py", "palettes": PALETTES, "patterns": PATTERNS}
with open(OUT, "w") as f:
    json.dump(doc, f, indent=1)
print(len(PATTERNS), "patterns")

# THE WINDOWS OF EACH CHURCH: its rose and its palette, then the lights': what fills the tracery, and which pictures tall and short lights
# take in turn. The finishes' glass rules are written from this, line for line; the rest of each finish is left as it stands. A cell with no rule falls to painted glass.
SAINTS, TALES = ["saint peter", "saint bishop", "saint virgin", "saint paul", "saint king", "saint martyr"], ["medallion ship", "medallion annunciation", "medallion kings", "medallion majesty"]
WINDOWS = {
    "notre-dame": ("rose stone 16", "paris", "chartres", "tracery diaper", SAINTS + ["medallion stack", "medallion story"], TALES),
    "cologne": ("rose stone 16", "cologne", "cologne", "tracery diaper", SAINTS + ["medallion stack", "medallion story"], TALES),
    "milan": ("rose chartres", "paris", "paris", "tracery diaper", SAINTS + ["medallion story", "medallion stack"], TALES),
    "ulm": ("rose chartres", "cologne", "cologne", "tracery white", ["saint bishop", "saint virgin", "medallion story", "grisaille lattice"], ["grisaille lattice", "medallion annunciation"]),
    "mainz": ("rose chartres", "chartres", "chartres", "tracery white", ["saint peter", "saint paul", "medallion stack", "grisaille strap"], ["grisaille strap", "medallion majesty", "grisaille lattice"]),
    "maria-laach": ("rose chartres", "chartres", "chartres", "tracery white", ["grisaille lattice", "saint peter", "grisaille strap"], ["grisaille lattice", "grisaille strap", "medallion majesty"]),
}
def rule(shape, name, palette, nth=None):
    L = PATTERNS[name]["layers"][0]
    r = {"parts": "kind:glass", "opening": shape, **({"nth": nth} if nth else {}), "map": "opening", **({"turn": 90} if L.get("lie") else {}), "pattern": "glass/" + name, "palette": "grisaille" if PATTERNS[name]["palette"] == "grisaille" else palette}
    return "    " + json.dumps(r) + ","
FINISHES = os.path.join(os.path.dirname(__file__), "..", "assets", "finishes")
for church, (rose_, rp, pal, head, tall_, short) in WINDOWS.items():
    path = os.path.join(FINISHES, church + ".json")
    with open(path) as f: lines = f.read().split("\n")
    at = next(i for i, l in enumerate(lines) if '"map": "opening"' in l)
    lines = [l for l in lines if '"map": "opening"' not in l]
    lines[at:at] = [rule("round", rose_, rp), rule("head", head, pal)] + [rule("tall", n, pal, [len(tall_), i]) for i, n in enumerate(tall_)] + [rule("short", n, pal, [len(short), i]) for i, n in enumerate(short)]
    with open(path, "w") as f: f.write("\n".join(lines))
