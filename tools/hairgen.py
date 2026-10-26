#!/usr/bin/env python3
"""HAIRSTYLES (2026-09-30): the hair as strands grown from the head's own vertices (hair.js, item part type `hair`),
one definition a style (assets/items/hair/*.json), and the catalogue's "Items: hair" category. A face definition
names its `hairstyle` (facegen.py: a pick by the kind of person); heads.js gives each person theirs. Edit this
for the numbers, then run it:

    python3 tools/hairgen.py

A style's `strands` are groups: a scalp REGION (heights y in the face's frame: the crown +.10, the forehead's
hairline ~.06, the ears' top ~.0, the nape -.06; angles th round the head: 0 the forehead, 90 the ears, 180 the
nape), `length` [front, back], `comb` (down | back | forward | out | up), `hang` (0 sticks out .. 1 falls), `wave`
{amp, per}, `curl` {r, per}, `width` [root, tip], `every`/`extra` (how many strands), `to` (a point the strands are
gathered at). `locks` are single long strands from named places; `gather` adds what holds it: a rope (ponytail), a
plait, a bun, a knot, each at a point, with or without a `tie`. The head's own parameters come from the face."""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ITEMS = os.path.join(ROOT, "assets", "items")
# the head's parameters a hairstyle takes from its face (the forehead's attributes too: face.js foreheadOf lifts the scalp
# to the forehead this face has -- the canon's here, face.js FACE_ATTRS)
HEAD = {"scale": 1, "faceW": 1, "forehead": 1, "occiput": 1, "crown": 1, "hairline": 0.06, "earS": 1, "fringe": 0, "seed": 1,
        "foreheadHeight": 0.062, "foreheadAngle": 12, "browRidge": 0.003}
# the hair PART maps them onto its fields (`scale` on a part is its placement's: the head's own size is its headScale)...
PART = {("headScale" if k == "scale" else k): k for k in HEAD}
# ...and the face hands them on to its hairstyle by their own names (as `headScale` the hair never read it: every
# hairstyle stayed the canon's size on a child's smaller head)
PASS = {k: k for k in HEAD}


def write(path, doc):
    full = os.path.join(ITEMS, path + ".json")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")


def style(key, name, about, strands=(), locks=(), gather=(), era="everywhere", region="everywhere", cap=None, sheets=(), spikes=()):
    part = {"id": "hair", "type": "hair", **PART, "strands": list(strands), "locks": list(locks), "gather": list(gather)}
    if sheets: part["sheets"] = list(sheets)
    if spikes: part["spikes"] = list(spikes)
    if cap is not None: part["cap"] = cap
    return key, {"kind": "item", "name": name, "category": "hair", "era": era, "region": region, "_about": about,
                 "params": dict(HEAD), "materials": {"hair": "hair-brown", "tie": "leather-dark"}, "parts": [part]}


# THE CAP (hair.js): the hair's body as one rounded shell over the skull, its edge lower at the sides (over the ears)
# and the back (the nape) than the skin's hairline; the strands hang from its edge (`edge` groups)
CAP = {"front": 0.058, "temple": 0.02, "side": -0.012, "nape": -0.072, "thick": 0.012, "crown": 0.012}
LOW = {**CAP, "front": -0.002, "temple": -0.006, "side": -0.018, "nape": -0.05, "fringe": -0.002}      # the bowl: cut level at the brows and the ears
BACK = {**CAP, "front": 0.062, "thick": 0.01, "crown": 0.006}                                          # drawn back tight
HANG = lambda th0, length, width=(0.036, 0.02), **kw: {"edge": True, "region": {"th": [th0, 180]}, "length": length, "comb": "down", "hang": 0.95, "width": list(width), "extra": 2, **kw}


ALL = {"y": [-1, 1], "th": [0, 180]}
FRINGE = {"region": {"y": [0.05, 0.2], "th": [0, 40]}, "length": 0.055, "comb": "forward", "hang": 0.9, "width": [0.022, 0.014], "extra": 1, "when": "fringe"}
PARTED = {"region": {"y": [0.05, 0.2], "th": [0, 30]}, "length": 0.1, "comb": [-0.7, -0.4, 1], "hang": 0.7, "width": [0.022, 0.012], "extra": 1, "unless": "fringe"}   # (no fringe: the front parted in the middle, swept back to the sides -- past the temples, not over the cheeks)
# (THE FACE'S GAP: hair hanging at the sides starts 55-60 degrees round from the front -- the cheekbones are at ~52 --
#  so it frames the face instead of hiding its sides)
SIDE = 60

# SHEETS (hair.js): the hair as a cloth from the cap's edge, cut in zig-zag rings -- pyramid locks, pointed tips
def ring(drop, out, zig, zy=0.0, phase=0, vary=0.4):
    return {"drop": drop, "out": out, "zig": zig, "zy": zy, "phase": phase, "vary": vary}
BANGS = {"region": {"th": [0, 50]}, "when": "fringe", "rings": [ring(0.02, 0.012, 0.005, phase=1), ring(0.035, 0.012, 0.007, 0.01)]}   # (tips above the brows)
LONG_SHEET = {"region": {"th": [SIDE + 2, 180]}, "rings": [ring(0.04, 0.02, 0.008), ring(0.12, 0.03, 0.016, phase=1), ring([0.2, 0.28], 0.034, 0.02),
                                                           ring([0.28, 0.38], 0.03, 0.014, 0.05, phase=1)]}
BOB_SHEET = {"region": {"th": [55, 180]}, "rings": [ring(0.035, 0.018, 0.008), ring([0.07, 0.06], 0.024, 0.014, phase=1), ring([0.11, 0.09], 0.02, 0.01, 0.03)]}
# UNDER A FALL OF STRANDS (2026-10-24): strands alone are a fan of ribbons with sky between them -- sticks, not hair.
# A sheet under them, hanging as far, is the hair's body; the strands lie over it as its clumps. `length` [front, back]
# as the strands'; the sheet a little shorter and closer in, so their tips and their waves stay in front of it
def under(th0, length, out=0.008):
    lo, hi = (length if isinstance(length, (list, tuple)) else (length, length))
    return {"region": {"th": [th0 + 2, 180]}, "rings": [ring(0.04, out * 0.8, 0.004), ring([lo * 0.5, hi * 0.5], out, 0.008, phase=1),
                                                         ring([lo * 0.85, hi * 0.85], out, 0.01, 0.02)]}
SPIKY_SHEET = {"region": {"th": [70, 180]}, "rings": [ring(0.025, 0.014, 0.008), ring(0.05, 0.01, 0.01, 0.022, phase=1)]}

# SPIKES (hair.js): thorns -- a lattice over the cap, a sparse checkerboard of its points pushed far out, each one's
# neighbours on the cap: sharp pyramids rising from the hair and falling back to it
def spikes(th, length, comb, blend, rows=8, cols=16, every=3, vary=0.35, y=None):
    d = {"region": {"th": list(th)}, "rows": rows, "cols": cols, "every": every, "length": length, "comb": comb, "blend": blend, "vary": vary}
    if y: d["region"]["y"] = list(y)
    return d
LONG_BANGS = {"region": {"th": [0, 42]}, "rings": [ring(0.022, 0.014, 0.006, phase=1), ring(0.036, 0.012, 0.01, 0.016)]}        # (pointed, their tips just over the eyes: with or without a fringe)
SIDE_LOCKS = {"region": {"th": [48, 72]}, "rings": [ring(0.05, 0.012, 0.006, phase=1), ring(0.11, 0.01, 0.008, 0.035)]}          # (framing the face, past the cheekbones)

STYLES = dict([
    style("none", "No hair", "a bare skull (the face's own hairline says how bald)"),
    style("crop", "Crop", "hair cropped close all over: a thin cap, nothing hanging", cap={**CAP, "thick": 0.006, "crown": 0.004}),
    style("short", "Short", "short hair combed back from the forehead, a fringe forward when the face has one",
          [FRINGE], cap={**CAP, "thick": 0.012, "crown": 0.014}),
    style("flat", "Flat (under a hat)", "hair lying flat under a hat: a thin cap and a little hanging at the nape",
          [HANG(100, 0.03, (0.02, 0.012))], cap={**CAP, "thick": 0.006, "crown": 0.0}),
    style("bowl", "Bowl cut", "the medieval bowl: a straight fringe to the brows, the sides and back cut level at the ears",
          [HANG(0, 0.025, (0.026, 0.022), hang=1)], cap=LOW, era="1100-1500", region="Europe"),
    style("bob", "Bob", "hair to the jaw all round, straight, a fringe when the face has one (else parted)",
          [HANG(55, [0.12, 0.1]), FRINGE, PARTED], sheets=[under(55, [0.12, 0.1], 0.006)], cap={**CAP, "crown": 0.016}),
    style("egyptian", "Egyptian bob", "the blunt black wig of Egypt: a straight fringe and thick straight hair to the shoulders, cut level",
          [HANG(42, 0.2, (0.03, 0.028), hang=1)], cap={**LOW, "front": 0.0, "temple": 0.0, "side": -0.01, "nape": -0.04, "fringe": 0.0, "thick": 0.016, "crown": 0.01}, era="-2500--30", region="Egypt"),
    style("long", "Long", "long straight hair falling to the shoulder blades, the front swept back behind the ears",
          [HANG(SIDE, [0.3, 0.38]), FRINGE, PARTED], sheets=[under(SIDE, [0.3, 0.38])], cap={**CAP, "crown": 0.016}),
    style("long-wavy", "Long wavy", "long hair in waves to the waist",
          [HANG(SIDE, [0.34, 0.46], wave={"amp": 0.014, "per": 0.12}), {**PARTED, "wave": {"amp": 0.01, "per": 0.11}}, FRINGE], sheets=[under(SIDE, [0.34, 0.46])], cap={**CAP, "crown": 0.02}),
    style("curly", "Curly", "a head of curls: a thick cap, curls coiling from its edge and off the crown",
          [HANG(0, [0.02, 0.1], (0.02, 0.012), hang=0.5, extra=2, curl={"r": 0.012, "per": 0.04}, seg=10),
           {"region": {"y": [0.06, 0.2], "th": [0, 180]}, "length": [0.035, 0.06], "comb": "back", "hang": 0.4, "off": 0.4, "width": [0.018, 0.012], "extra": 1, "every": 2, "lift": 0.012, "curl": {"r": 0.01, "per": 0.035}, "seg": 8}],
          cap={**CAP, "thick": 0.024, "crown": 0.024}),
    style("ponytail", "Ponytail", "the hair drawn back to a tie at the nape and falling from it in a tail",
          gather=[{"kind": "rope", "at": [-0.095, -0.01, 0], "dir": [-0.3, -1, 0], "length": 0.3, "width": 0.075, "hang": 0.9, "tie": True}], cap=BACK),
    style("bun", "Bun", "the hair drawn up and back into a bun behind the crown",
          gather=[{"kind": "bun", "at": [-0.1, 0.045, 0], "r": 0.04}], cap=BACK),
    style("braid", "Braid", "the hair drawn back into one plait hanging down the back",
          gather=[{"kind": "plait", "at": [-0.095, -0.04, 0], "dir": [-0.35, -1, 0], "length": 0.42, "width": 0.068, "hang": 0.8, "per": 0.075, "tie": True}], cap=BACK),
    style("plaits", "Plaits", "two plaits, one at each side, hanging over the shoulders in front",
          gather=[{"kind": "plait", "at": [-0.02, -0.04, 0.075], "dir": [0.3, -1, 0.1], "length": 0.36, "width": 0.058, "hang": 0.7, "per": 0.065, "tie": True, "mirror": True}], cap=CAP),
    style("two-locks", "Long with two locks", "long hair behind, and a lock at each temple hanging down in front of the ear -- the Norse and the Frankish way",
          [HANG(SIDE, [0.28, 0.36], wave={"amp": 0.008, "per": 0.14})], sheets=[under(SIDE, [0.28, 0.36])],
          locks=[{"at": [62, 0.03], "n": 2, "length": 0.34, "comb": "down", "hang": 0.95, "width": [0.026, 0.014], "wave": {"amp": 0.008, "per": 0.1}}], cap=CAP, era="500-1100", region="the North"),
    style("viking", "Long with side plaits", "long hair with a thin plait at each temple",
          [HANG(95, [0.28, 0.36])], sheets=[under(95, [0.28, 0.36])],   # (the hanging hair from behind the plaits: none in front of them, at the temples)
          gather=[{"kind": "plait", "at": [0.04, 0.0, 0.078], "dir": [0.1, -1, 0.15], "length": 0.3, "width": 0.028, "hang": 0.9, "per": 0.05, "tie": True, "mirror": True}], cap=CAP, era="700-1100", region="Scandinavia"),
    style("topknot", "Topknot", "the hair drawn up from all round into a knot on top of the head -- the Chinese and the samurai's way",
          gather=[{"kind": "knot", "at": [-0.02, 0.135, 0], "r": 0.028, "tie": True, "dir": [-1, 0, 0]}], cap={**BACK, "crown": 0.0}, era="-200-1900", region="China, Japan"),
    style("tonsure", "Tonsure", "the monk's tonsure: a ring of short hair round a shaven crown",
          cap={**CAP, "top": 0.072, "thick": 0.01, "crown": 0.0}, era="500-1800", region="Christendom"),
    style("shoulder", "Shoulder length", "hair to the shoulders, parted in the middle, straight",
          [HANG(58, [0.2, 0.26]), PARTED, FRINGE], sheets=[under(58, [0.2, 0.26])], cap={**CAP, "crown": 0.014}),
    style("manga-long", "Long (drawn locks)", "long hair as one cloth from the cap's edge, cut in zig-zag rings: pyramid-shaped locks down the back and pointed tips, the face left open; pointed bangs when the face has a fringe",
          [PARTED], sheets=[LONG_SHEET, BANGS], cap={**CAP, "crown": 0.018}),
    style("manga-bob", "Bob (drawn locks)", "a bob as one zig-zag cloth: locks folding round the jaw, pointed tips, pointed bangs with a fringe",
          [PARTED], sheets=[BOB_SHEET, BANGS], cap={**CAP, "crown": 0.016}),
    style("spiky-back", "Spiky, swept back", "drawn hair in THORNS: long spikes swept back and up over the back of the head, each rising sharp from the hair between its neighbours, pointed bangs to the brows and a lock at each side of the face",
          [], sheets=[LONG_BANGS, SIDE_LOCKS], spikes=[spikes((0, 180), [0.06, 0.13], [-1, 0.7, 0], 0.6, rows=8, cols=18, every=3)], cap={**CAP, "thick": 0.016, "crown": 0.02}),
    style("spiky-up", "Spiky, standing", "thorns standing up all over the head, longest on the crown",
          [], spikes=[spikes((0, 180), [0.07, 0.1], [0, 1, 0], 0.55, rows=8, cols=16, every=3)], cap={**CAP, "thick": 0.016, "crown": 0.016}),
    style("spiky-wild", "Spiky, wild", "short thick thorns straight out all round, a shock of hair -- a mane's way",
          [], spikes=[spikes((0, 180), [0.05, 0.07], [0, 0.3, 0], 0.15, rows=10, cols=20, every=2, vary=0.5)], cap={**CAP, "thick": 0.018, "crown": 0.018}),
    style("manga-short", "Short (drawn locks)", "short hair whose edge breaks into pointed locks over the ears and the nape, pointed bangs with a fringe",
          [], sheets=[SPIKY_SHEET, BANGS], cap={**CAP, "thick": 0.014, "crown": 0.016}),
])

BY_KIND = {
    "man": ["short", "short", "crop", "bowl", "shoulder", "long", "ponytail", "two-locks", "curly", "manga-short", "spiky-back"],
    "woman": ["long", "long-wavy", "long-wavy", "bob", "braid", "plaits", "bun", "two-locks", "shoulder", "curly", "manga-long", "manga-bob"],
    "child": ["bowl", "crop", "plaits", "bob", "short", "curly"],
    "elder": ["short", "tonsure", "none", "crop", "shoulder"],
    "old-woman": ["bun", "bun", "braid", "shoulder", "plaits"],
    "beast-man": ["crop", "none", "topknot", "curly"],
    "face": ["short", "long", "bob", "curly", "braid", "topknot", "two-locks"],
}


def main():
    for k, v in STYLES.items():
        write("hair/" + k, v)
    # the faces name their hairstyle: a pick by kind, and the hair part that draws it with the head's own parameters
    for kind, picks in BY_KIND.items():
        path = os.path.join(ITEMS, "faces", kind + ".json")
        doc = json.load(open(path))
        doc["params"]["hairstyle"] = {"pick": ["items/hair/" + s for s in picks]}
        doc["params"]["fringe"] = {"pick": [0, 0, 1]}
        if kind == "face":
            doc["parts"] = [p for p in doc["parts"] if p.get("id") != "hair"] + [
                {"id": "hair", "use": "hairstyle", "params": {**PASS, "seed": "seed"}}]
            doc["params"]["seed"] = 1
        json.dump(doc, open(path, "w"), indent=1, ensure_ascii=False)
    ipath = os.path.join(ROOT, "assets", "index.json")
    index = json.load(open(ipath))
    cats = {c["name"]: c for c in index["categories"]}
    if "Items: hair" not in cats:
        pos = index["categories"].index(cats["Items: faces"]) + 1
        index["categories"].insert(pos, {"name": "Items: hair", "kind": "item", "paths": []})
        cats = {c["name"]: c for c in index["categories"]}
    cats["Items: hair"]["paths"] = ["items/hair/" + k for k in STYLES]
    json.dump(index, open(ipath, "w"), indent=2, ensure_ascii=False)
    print(len(STYLES), "hairstyles")


if __name__ == "__main__":
    main()
