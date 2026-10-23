import sys, re, unicodedata as ud; sys.path.insert(0, ".")
from jdump import write
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "glyphs") + os.sep
C = 1
def S(points, fill=None, **k):
    d = {"shape": "spline", "points": points}
    if fill: d["fill"] = fill
    d.update(k); return d
def L(points, fill, w, **k):
    d = {"shape": "limb", "points": points, "w": w, "fill": fill}; d.update(k); return d
def line(a, b, stroke="line", w=1.0, **k):
    d = {"shape": "line", "from": a, "to": b, "stroke": stroke, "line": w}; d.update(k); return d
def P(name, **k):
    d = {"part": name}; d.update(k); return d
def G(name, **k):
    d = {"sign": name}; d.update(k); return d
def uni(code):
    L_, n, v = re.match(r"([A-Za-z]+)(\d+)([A-Za-z]*)$", code).groups()
    try: return "%X" % ord(ud.lookup(f"EGYPTIAN HIEROGLYPH {L_.upper()}{int(n):03d}{v.upper()}"))
    except KeyError: return None
CATS = {"A": "Man and his occupations", "B": "Woman and her occupations", "C": "Anthropomorphic deities", "D": "Parts of the human body",
        "E": "Mammals", "F": "Parts of mammals", "G": "Birds", "H": "Parts of birds", "I": "Amphibious animals, reptiles", "K": "Fish and parts of fish",
        "L": "Invertebrates and lesser animals", "M": "Trees and plants", "N": "Sky, earth, water", "O": "Buildings and their parts", "P": "Ships and parts of ships",
        "Q": "Domestic and funerary furniture", "R": "Temple furniture and sacred emblems", "S": "Crowns, dress, staves", "T": "Warfare, hunting, butchery",
        "U": "Agriculture, crafts and professions", "V": "Rope, fibre, baskets, bags", "W": "Vessels of stone and earthenware", "X": "Loaves and cakes",
        "Y": "Writings, games, music", "Z": "Strokes, signs from hieratic, geometrical figures", "Aa": "Unclassified"}
def sign(name, layers, colors=None, freq=2, reading=None, **k):
    d = {"name": name}
    if reading: d["reading"] = reading
    d["freq"] = freq
    if colors: d["colors"] = colors
    d.update(k); d["layers"] = layers; return d
def category(cat, signs):
    out = {}
    for code, s in signs.items():
        u = uni(code)
        out[code] = {"name": s.pop("name"), **({"u": u} if u else {}), **s}
    write(OUT + cat + ".json", {"name": f"{cat} -- {CATS[cat]}", "category": cat,
        "_about": f"Gardiner's category {cat}, {CATS[cat].lower()} (glyphs.js): each sign in the quadrat (100 units, y up, the baseline at 0), facing left; `u` its Unicode code point, `reading` its sound value where it has one, `freq` how often texts use it (a wall of text draws by it), `colors` its roles in the painter's colours.",
        "signs": out})
    print(cat, len(out), "signs")
