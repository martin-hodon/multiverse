#!/usr/bin/env python3
"""THE PYRAMIDS OF GIZA (2026-10-05, docs/murals.md): the landmark `giza` -- Khufu's, Khafre's and Menkaure's pyramids
at a quarter of their size (their proportions and their line across the plateau kept), each with the white casing near
its top (Khafre's keeps the most of it), a gilded pyramidion, a passage from the north face and a burial chamber in its
heart -- and its finish, which paints the chambers' walls with tomb scenes and the passages with the Pyramid Texts
(patterns/murals: one pattern per painting, sized to the wall by the rule's W and H).

    python3 tools/pyramidgen.py
"""
import json, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
K = .25   # the scale: a quarter of the real thing (Khufu's 230 m base would swallow the world)
# real numbers: base, height (m); the chamber's width x length x height (King's chamber, Khafre's, Menkaure's)
PYR = {
 "khufu": {"base": 230.3, "height": 146.6, "casing": .86, "at": [30, 0, 35], "chamber": [10.4, 5.2, 5.8], "depth": 7.5},
 "khafre": {"base": 215.3, "height": 143.5, "casing": .74, "at": [-28, 0, -22], "chamber": [14.2, 5.0, 6.8], "depth": 5.5},
 "menkaure": {"base": 102.2, "height": 65.0, "casing": .86, "at": [-66, 0, -66], "chamber": [6.6, 4.1, 3.5], "depth": 6},
}
ENTRANCE = {"width": 1.4, "height": 2.8}   # (the real passages are about 1.05 x 1.2 m: too low to walk upright in a game; the door
                                            #  on the face comes out lower, where the sloping ceiling meets it)
SLOPE = 26.5                                # the descending passages' angle (Khufu's 26.3, Khafre's 25.9)
import math
def chamber_floor(b, h, p):   # (as the assembler works it out: arch/assemble.js pyramid -- the depth the passage reaches)
    t, half = math.tan(math.radians(SLOPE)), b / 2
    return -min(p["depth"], max(1.5, (half - p["chamber"][1] / 2 - 2) * t))
def r(v): return round(v, 3)
parts = {}
for k, p in PYR.items():
    b, h = p["base"] * K, p["height"] * K
    parts[k] = {"type": "pyramid", "base": r(b), "height": r(h), "casing": r(h * p["casing"]), "cap": r(h * .035),
                "entrance": ENTRANCE, "slope": SLOPE, "depth": p["depth"], "chamber": {"width": p["chamber"][0], "length": p["chamber"][1], "height": p["chamber"][2]},
                "at": [[p["at"][0], 0, p["at"][2], 0]]}
    # the SARCOPHAGUS (items/furniture/sarcophagus): at the chamber's west end, along it, as Khufu's stands
    parts[k + " sarcophagus"] = {"type": "item", "item": "items/furniture/sarcophagus", "seed": len(parts), "at": [[r(p["at"][0] - p["chamber"][0] / 2 + 1.6), r(chamber_floor(b, h, p) + .02), p["at"][2], 90]]}
# THE GROUND OPEN where each passage goes down through it: from the door to where the sloping ceiling passes under the
# ground (site.dig, the building's frame) -- beyond that the passage and the chamber lie in the rock under the ground
DIG = []
for k, p in PYR.items():
    b = p["base"] * K; zF = b / 2; run = ENTRANCE["height"] / math.tan(math.radians(SLOPE)) + .6
    DIG.append([r(p["at"][0] - ENTRANCE["width"] / 2 - .25), r(p["at"][2] + zF - run), r(p["at"][0] + ENTRANCE["width"] / 2 + .25), r(p["at"][2] + zF + .05)])
GIZA = {"name": "The Pyramids of Giza", "_about": "Khufu's, Khafre's and Menkaure's pyramids at a quarter of their size, in their line across the plateau: the stepped core, the white Tura casing near the top (Khafre's keeps the most), a gilded pyramidion; in each a passage from the north face to a burial chamber painted with tomb scenes (Egypt, -2560 -- -2510)",
        "era": "-2560--2510", "region": "Egypt", "params": {"detail": 4}, "parts": parts, "build": list(parts), "site": {"dig": DIG}}
json.dump(GIZA, open(os.path.join(ROOT, "assets", "architecture", "giza.json"), "w"), indent=1, ensure_ascii=False)
# the murals as patterns (patterns.js layer kind `mural`, murals.js): each one painting over a W x H tile
PAINTS = ["offering-to-osiris", "gods-procession", "adoration-of-ra", "the-dead-and-their-offerings", "anubis-guardian", "isis-and-hathor", "pyramid-texts"]
MURALS = {"name": "Murals", "_about": "TOMB PAINTINGS on walls (murals.js): each pattern one painting (assets/murals/paintings) over a W x H tile -- a finish's rule gives W and H as the wall's own size, so the painting fills it",
          "patterns": {n: {"size": ["W", "H"], "params": {"W": 6, "H": 3}, "palette": "limestone", "res": 1024, "repeat": n == "pyramid-texts", "layers": [{"kind": "mural", "painting": n}]} for n in PAINTS}}   # (the texts run on down a passage: they repeat; a scene is one panel)
json.dump(MURALS, open(os.path.join(ROOT, "assets", "patterns", "murals.json"), "w"), indent=1, ensure_ascii=False)
# the finish: the core's coursed limestone, the white casing, the gold cap; the chambers painted, the passages written
SCENES = {"khufu": ["offering-to-osiris", "adoration-of-ra", "anubis-guardian", "isis-and-hathor"],
          "khafre": ["gods-procession", "the-dead-and-their-offerings", "anubis-guardian", "isis-and-hathor"],
          "menkaure": ["adoration-of-ra", "offering-to-osiris", "anubis-guardian", "isis-and-hathor"]}
rules = []
for k, p in PYR.items():
    cw, cl, ch = p["chamber"]; sc = SCENES[k]
    # (a wall's u runs along it in the building's frame -- finish.js: x on a wall facing +z, -x facing -z, z facing -x,
    #  -z facing +x -- so each painting is centred on its wall by an offset of the wall's middle)
    X, Z = p["at"][0], p["at"][2]
    rules += [{"parts": f"{k} chamber south wall", "pattern": "murals/" + sc[0], "params": {"W": cw, "H": ch}, "align": "part", "offset": [-X, 0]},
              {"parts": f"{k} chamber north wall", "pattern": "murals/" + sc[1], "params": {"W": cw, "H": ch}, "align": "part", "offset": [X, 0]},
              {"parts": f"{k} chamber east wall", "pattern": "murals/" + sc[2], "params": {"W": cl, "H": ch}, "align": "part", "offset": [-Z, 0]},
              {"parts": f"{k} chamber west wall", "pattern": "murals/" + sc[3], "params": {"W": cl, "H": ch}, "align": "part", "offset": [Z, 0]},
              {"parts": f"{k} passage walls", "pattern": "murals/pyramid-texts", "params": {"W": 4.4, "H": ENTRANCE["height"]}, "align": "part"},   # (the texts' bands from the passage's lowest floor up)
              {"parts": [f"{k} chamber ceiling", f"{k} passage ceiling"], "pattern": "painted/starry vault"},
              {"parts": [f"{k} chamber floor", f"{k} passage floor"], "pattern": "stone/ashlar fine", "palette": "limestone"},
              {"parts": f"{k} casing", "pattern": "stone/ashlar fine", "palette": "plaster-white", "scale": 2},
              {"parts": f"{k} cap", "pattern": "roofs/gold leaf", "palette": "gold"},
              {"parts": f"{k} core", "pattern": "stone/plaster", "palette": "limestone"}]
FIN = {"name": "The Pyramids of Giza", "building": "architecture/giza", "_about": "Giza: the core's coursed yellow limestone, the casing's white Tura limestone near the top, the pyramidion gilded; inside, the burial chambers painted with tomb scenes (murals.js), the passages carved with the Pyramid Texts in blue, the ceilings starred",
       "stone": {"color": "#cdb48a", "accent": "#b9a47e", "pat": "ashlar"}, "rules": rules}
json.dump(FIN, open(os.path.join(ROOT, "assets", "finishes", "giza.json"), "w"), indent=1, ensure_ascii=False)
# the catalogue
ip = os.path.join(ROOT, "assets", "index.json"); idx = json.load(open(ip))
for c in idx["categories"]:
    if c["name"] == "Architecture" and "architecture/giza" not in c["paths"]: c["paths"].append("architecture/giza")
    if c["kind"] == "finish" and "finishes/giza" not in c["paths"]: c["paths"].append("finishes/giza")
    if c["kind"] == "pattern" and "patterns/murals" not in c["paths"]: c["paths"].append("patterns/murals")
json.dump(idx, open(ip, "w"), indent=2, ensure_ascii=False); open(ip, "a").write("\n")
print("giza:", len(PYR), "pyramids,", len(parts), "parts,", len(rules), "rules")
