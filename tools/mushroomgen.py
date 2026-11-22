#!/usr/bin/env python3
"""MUSHROOMS (2026-11-08): the woods' understory mushrooms as items (assets/items/mushrooms), in polygons -- lathes, as the
flowers are (tools/flowergen.py) -- in place of the last figures the game still made in the old part vocabulary (a pill for
the stem, a squashed sphere for the cap). Real sizes: a fly agaric 13-20 cm, a cep 10-16 cm, a chanterelle 6-9 cm. Each
`s` is its size, drawn by the seed; the fly agaric's spots turn with `spin`, so no two stand alike.

    python3 tools/mushroomgen.py
"""
import json, math, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "assets", "items", "mushrooms")
def e(v): return f"s * {round(v, 4)}"                       # a length, scaled by the size
def prof(points): return [[e(r) if r else 0, e(y) if y else 0] for r, y in points]
def lathe(points, material, sides=10, **k):
    d = {"type": "lathe", "material": material, "profile": prof(points), "sides": sides}; d.update(k); return d
def pick(*xs): return {"pick": list(xs)}
def write(name, doc):
    os.makedirs(OUT, exist_ok=True)
    json.dump(doc, open(os.path.join(OUT, name + ".json"), "w"), indent=1, ensure_ascii=False)
def item(name, about, materials, parts, params=None):
    return {"kind": "item", "name": name, "category": "nature/mushrooms", "era": "everywhere", "region": "everywhere", "_about": about,
            "params": {"s": [0.8, 1.3], **(params or {})}, "materials": materials, "parts": parts}

# a wart: a low dome `r` across and `k * r` high over the surface it stands on (its foot a little under it), five-sided
def wart(id_, r, k, at, around=None):
    d = {"id": id_, "type": "lathe", "material": "spot", "sides": 5, "caps": False, "smooth": True,
         "profile": prof([(r, -.25 * k * r), (.7 * r, .6 * k * r), (0, k * r)]), "at": at}
    if around: d["around"] = around
    return d

# the fly agaric: a white stem swelling to a bulb at the foot, a hanging skirt under the cap, cream gills, a scarlet dome
# flecked with white warts -- three rings of them, turned by `spin`, and one at the crown
R, Y0, H = .055, .108, .05                                   # the cap's rim radius, the rim's height, the dome's rise
def dome_y(r): return Y0 + H * math.sqrt(max(0, 1 - (r / R) ** 2))
amanita = item("Fly agaric", "a white stem out of a bulbous foot, a skirt hanging under the cap, cream gills, a scarlet dome flecked with white warts",
    {"stem": "#ece7db", "gills": "#efe6d2", "cap": pick("#c8301f", "#c8301f", "#d04a1c", "#b8281c"), "spot": "#f4efe3"},
    [lathe([(0, 0), (.016, 0), (.02, .008), (.013, .03), (.011, .085), (.012, .1)], "stem", sides=9),
     lathe([(.012, .085), (.024, .072)], "stem", sides=10, caps=False, double=True),             # the skirt
     lathe([(.012, .1), (R, Y0)], "gills", sides=12, caps=False),                                # (face down; the cap closes over it)
     lathe([(R, Y0), (.054, .118), (.046, .135), (.03, .15), (0, .158)], "cap", sides=12, caps=False),
     # the warts: low five-sided domes standing out of the cap (2026-11-22, the in-game budget: they were squashed
     # spheres, 36 triangles each, half of them under the cap -- 612 of the agaric's 991, and ~190 agarics stand in a world)
     wart("crown", .006, .45, [0, e(.157), 0]),
     wart("warts1", .0055, .45, [0, e(dome_y(.018)), 0], {"n": 3, "r": e(.018), "plane": "xz", "start": "spin"}),
     wart("warts2", .005, .45, [0, e(dome_y(.038)), 0], {"n": 6, "r": e(.038), "plane": "xz", "start": "spin + 30"}),
     wart("warts3", .004, .5, [0, e(dome_y(.05) - .002), 0], {"n": 7, "r": e(.05), "plane": "xz", "start": "spin + 55"})],
    params={"spin": [0, 120]})
write("amanita", amanita)

# the cep (boletus): a fat pale stem, swelling low, under a brown bun; its underside a pale yellow sponge of pores
boletus = item("Cep", "a fat pale stem swelling low under a brown bun of a cap, its underside a pale yellow sponge of pores",
    {"stem": pick("#cfbf98", "#c9b58c", "#d6c7a2"), "pores": "#d9c868", "cap": pick("#6e4423", "#5e3a1e", "#7a4f2a", "#8a5a30")},
    [lathe([(0, 0), (.018, .002), (.022, .025), (.02, .055), (.015, .075), (.014, .08)], "stem", sides=9),
     lathe([(.014, .08), (.05, .086)], "pores", sides=12, caps=False),                           # (one-sided: the cap closes over them)
     lathe([(.05, .086), (.05, .094), (.044, .11), (.03, .125), (0, .132)], "cap", sides=12, caps=False)])
write("boletus", boletus)

# the chanterelle: one golden funnel, the stem widening into a cap whose rim rolls over and whose middle dips
chanterelle = item("Chanterelle", "one golden funnel: a short stem widening into a wavy-rimmed cap whose middle dips",
    {"flesh": pick("#e4a12a", "#d99a2e", "#edb13a")},
    # (2026-11-22: the stem one-sided -- its inside is never seen -- the cap a shell seen from both sides, the foot's
    #  disc and the dip's last ring left out: 252 triangles, it was 360, and ~190 stand in a world)
    [lathe([(.006, 0), (.007, .03), (.012, .045)], "flesh", sides=9, caps=False),
     lathe([(.012, .045), (.02, .055), (.03, .064), (.031, .067), (.027, .068), (.015, .058), (0, .05)],
           "flesh", sides=9, caps=False, double=True)])
write("chanterelle", chanterelle)
print("wrote", sorted(os.listdir(OUT)))
