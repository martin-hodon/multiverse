#!/usr/bin/env python3
"""The ornament family: assets/patterns/ornament.json (ornament.js, docs/ornament.md). Run from anywhere.
A star lattice has one proper aspect, so a pattern's size is worked out here from `U`, the height of its tile in metres."""
import json, math, os

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "patterns", "ornament.json")

def cell(n, k=2, gap=0):
    a = 1 / (2 * math.tan(math.pi / n)); d = 2 * a + gap; phi = k * math.pi / n
    return 2 * d * math.sin(phi), 2 * d * math.cos(phi)

def stars(about, n, k=2, gap=0, U=.8, cells=(1, 1), palette="iznik", palettes=("zellige", "kashan"), ground=0, res=512, **layer):
    w, h = cell(n, k, gap)
    W = U * (w * cells[0]) / (h * cells[1])
    L = {"kind": "stars", "n": n, "k": k, "gap": gap, "cells": list(cells), **layer}
    return {"size": [round(W, 5), U], "palette": palette, "palettes": list(palettes), "ground": ground, "res": res, "_about": about, "layers": [L]}

def knot(about, size, palette="zellige", palettes=("iznik", "marble-bw"), ground=0, res=512, **layer):
    return {"size": list(size), "palette": palette, "palettes": list(palettes), "ground": ground, "res": res, "_about": about, "layers": [{"kind": "knot", **layer}]}

# strapwork: a cream or dark band with a thin outline over glazed pieces. Slots of iznik and its kin: 0 ground, 1-4 colours, 5 dark
STRAP = dict(strap=0, strapEdge=5, band=.09, edge=.014, vary=.05)
GROUT = dict(strap="#2a2622", band=.03, edge=0, weave=False, vary=.05)     # zellige: cut glazed pieces in dark grout

PATTERNS = {
    # -- woven strapwork
    "star8 strap": stars("eight-point stars over octagons and squares, strapwork woven", 8, angle=67.5, fills=[1, 2, 3, 4], **STRAP),
    "star6 strap": stars("six-point stars over hexagons", 6, angle=60, U=.7, fills=[1, 2, 4], **STRAP),
    "star12 strap": stars("twelve-point stars over dodecagons and triangles", 12, angle=60, U=1, fills=[1, 2, 3, 4], **STRAP),
    "star12 square": stars("twelve-point stars on a square lattice", 12, k=3, angle=60, U=1, fills=[1, 2, 3, 4], **STRAP),
    "star10 girih": stars("ten-point stars: the girih's fifty-four degree lines", 10, angle=54, U=1, palette="kashan", palettes=["isfahan-girih", "zellige"], fills=[1, 2, 3, 4], **STRAP),
    "star16 strap": stars("sixteen-point stars on a square lattice", 16, k=4, angle=67.5, U=1.2, fills=[1, 2, 3, 4], **STRAP),
    "star 4-6-12": stars("twelve-point stars held apart by squares and hexagons", 12, gap=1, angle=60, U=1.2, fills=[1, 2, 3, 4], **STRAP),
    "star 3-4-6-4": stars("six-point stars held apart by squares and triangles", 6, gap=1, angle=60, U=.8, fills=[1, 2, 3, 4], **STRAP),
    "two-point": stars("two-point contact: each edge sends its lines from two places, so the bands double", 8, angle=67.5, delta=.1, fills=[1, 2, 3, 4], **STRAP),
    "alternate stars": stars("every other star in the other glaze", 8, angle=67.5, fills=[[1, 2], 3, 4, 0], **STRAP),
    "rosette 12": stars("a rosette: each ray carried on through its partner, so a ring of petals stands round a smaller star", 12, angle=60, depth=2, U=1, fills=[1, 3, 2, 4, 2], **STRAP),
    "rosette 16": stars("a sixteen-point rosette", 16, k=4, angle=67.5, depth=3, U=1.2, fills=[1, 3, 2, 4, 2], **STRAP),
    "rosette 10": stars("a ten-point rosette, the Seljuk and Isfahan figure", 10, angle=54, depth=2, U=1, palette="kashan", palettes=["isfahan-girih", "zellige"], fills=[3, 1, 0, 2, 1], **STRAP),
    "rosette 10 dome": stars("the same in a dome's calm colours: blue and turquoise, the pale lines between", 10, angle=54, depth=2, U=1, palette="isfahan-girih", palettes=["kashan", "zellige"], fills=[1, 0, 2, 0, 3], **STRAP),
    "rosette 8": stars("an eight-point rosette", 8, angle=67.5, depth=2, fills=[1, 3, 2, 4], **STRAP),
    # -- cut pieces in grout
    "zellige 8": stars("Moroccan zellige: glazed pieces in dark grout, each its own tone", 8, angle=67.5, U=.5, palette="zellige", palettes=["iznik", "mughal"], fills=[0, 1, 3, 2], **{**GROUT, "vary": .13}),
    "zellige 12": stars("zellige of twelve-point stars", 12, angle=60, U=.7, palette="zellige", palettes=["iznik", "mughal"], fills=[0, 1, 2, 3], **{**GROUT, "vary": .13}),
    "zellige 10": stars("zellige of ten-point stars", 10, angle=54, U=.7, palette="zellige", palettes=["iznik", "mughal"], fills=[0, 1, 3, 2], **{**GROUT, "vary": .13}),
    # -- knots: Celtic, Viking, Roman, Byzantine
    "guilloche": knot("a Roman guilloche: two strands twisting round eyes, a border (one cell high)", [.3, .15], cols=2, rows=1, wrap="x", margin=.012, band=.42, edge=.05, strap=1, strapEdge=4, core=0, coreWidth=.12, eye=3, eyeSize=.14, res=512),
    "braid": knot("a Byzantine braid: a plait, two cells high", [.4, .2], cols=4, rows=2, wrap="x", margin=.01, band=.34, edge=.05, strap=3, strapEdge=4, res=512),
    "cable": knot("a four-cell plait with a groove down the band", [.5, .3], cols=5, rows=3, wrap="x", margin=.012, band=.36, edge=.05, strap=2, strapEdge=4, core=4, coreWidth=.05, res=512),
    "celtic field": knot("a repeating Celtic knot: walls set symmetrically in the grid", [.8, .8], cols=6, rows=6, wrap="xy", breaks=.14, symmetry="xy", seed=3, band=.5, edge=.05, strap=3, strapEdge=4),
    "celtic border": knot("a Celtic knot running as a border", [.8, .2], cols=8, rows=2, wrap="x", breaks=.2, symmetry="x", seed=2, margin=.008, band=.48, edge=.05, strap=1, strapEdge=4),
    "celtic panel": knot("a closed knot panel, a page or a cross-slab", [1, 1], repeat=None, cols=8, rows=8, wrap="", breaks=.16, symmetry="r4", seed=5, margin=.04, band=.5, edge=.05, strap=3, strapEdge=4),
    "viking": knot("a broad Viking interlace: few walls, a wide band", [.8, .8], cols=4, rows=4, wrap="xy", breaks=.22, run=2, symmetry="r2", seed=7, band=.62, edge=.06, strap=5, strapEdge=4, core=4, coreWidth=.08, palette="zellige"),
}
def scroll(about, size, palette="iznik", palettes=("isfahan", "kashan"), ground=1, res=512, **layer):
    return {"size": list(size), "palette": palette, "palettes": list(palettes), "ground": ground, "res": res, "_about": about, "layers": [{"kind": "scroll", **layer}]}

PATTERNS.update({
    "arabesque": scroll("an arabesque field: a waving stem, a curl under every crest, each ending in a split leaf", [.8, .8], cols=4, rows=4, stem=0, flower=3, heart=0, flowers=1, width=.085, leaf=.62, leaves=4, end=1.25),
    "arabesque double": scroll("two levels of vine: a thin one in the second colour running under the first", [.8, .8], cols=4, rows=4, palette="isfahan-girih", palettes=["iznik", "kashan"], ground=0, stem=2, under=1, underThin=.55, flower=3, heart=2, flowers=1, width=.085, leaf=.62, leaves=4, end=1.25),
    "arabesque border": scroll("the same vine as a single running border", [.8, .2], cols=4, rows=1, stem=0, flower=3, heart=0, flowers=1, width=.085, leaf=.62, leaves=4, end=1.25),
    "star arabesque": stars("eight-point strapwork with a vine inside every star", 8, angle=67.5, U=.8, palette="isfahan", palettes=["iznik", "kashan"], fills=[2, 1, 3, 4], inlay=dict(ranks=[0], stem=0, flower=3, heart=0), **STRAP),
    "star12 arabesque": stars("a rosette's central star holding the vine, Isfahan haft-rangi", 12, angle=60, depth=2, U=1.2, palette="isfahan-girih", palettes=["iznik", "kashan"], fills=[0, 1, 0, 3, 1], inlay=dict(ranks=[0], stem=2, flower=3, heart=2), strap=2, strapEdge=5, band=.09, edge=.014, vary=.04),
})
# (a hem along each edge, so a frieze stands off the field it runs over)
PATTERNS["arabesque border"]["layers"].append({"shape": "rect", "w": .8, "h": .014, "at": [[0, .093], [0, -.093]], "fill": 5})
for p in PATTERNS.values():
    for L in p["layers"]:
        if L.pop("repeat", 1) is None: p["repeat"] = False

doc = {"name": "Ornament", "_about": "GEOMETRIC ORNAMENT (ornament.js, docs/ornament.md): star patterns and knots, generated by tools/ornamentgen.py", "patterns": PATTERNS}
with open(OUT, "w") as f:
    json.dump(doc, f, indent=1)
# the family in the viewer's catalogue
IDX = os.path.join(os.path.dirname(__file__), "..", "assets", "index.json")
with open(IDX) as f: idx = json.load(f)
for c in idx["categories"] if isinstance(idx, dict) and "categories" in idx else []:
    if "patterns/greek" in c["paths"] and "patterns/ornament" not in c["paths"]:
        c["paths"].insert(c["paths"].index("patterns/greek") + 1, "patterns/ornament")
        with open(IDX, "w") as f: json.dump(idx, f, indent=2, ensure_ascii=False); f.write("\n")
print(len(PATTERNS), "patterns")
