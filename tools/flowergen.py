#!/usr/bin/env python3
"""FLOWERS (2026-10-06): blooms and whole plants as items (assets/items/flowers), in polygons -- the `petals` primitive
(petals.js: a whorl of curved blades) for the petals, sepals and leaves, lathes for the centres, rods and sweeps for the
stems. A BLOOM (items/flowers/blooms/<kind>) is the flower alone, its face up +y, at real size -- what a plant carries
and what is worn in the hair; a PLANT (items/flowers/<kind>) is its stem, leaves and blooms, standing on y = 0. Each a
few hundred triangles at most. Colours are each kind's own, picked by the seed where a kind comes in several.

    python3 tools/flowergen.py
"""
import json, math, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "assets", "items", "flowers")
def r(v): return round(v, 4)
def write(path, doc):
    full = os.path.join(OUT, path + ".json"); os.makedirs(os.path.dirname(full), exist_ok=True)
    json.dump(doc, open(full, "w"), indent=1, ensure_ascii=False)
def pick(*xs): return {"pick": list(xs)}
def petals(**k): d = {"type": "petals"}; d.update(k); return d
def lathe(profile, material, **k): d = {"type": "lathe", "material": material, "profile": [[r(a), r(b)] for a, b in profile]}; d.update(k); return d
def rod(a, b, rr, material="stem", **k): d = {"type": "rod", "material": material, "from": [r(x) for x in a], "to": [r(x) for x in b], "r": rr, "sides": 4}; d.update(k); return d
def sweep(path, rr, material="stem", **k): d = {"type": "sweep", "material": material, "path": [[r(x) for x in p] for p in path], "r": rr, "sides": 4, "seg": 2}; d.update(k); return d
BLOOM_SCALE = 1.6   # (on a plant the bloom is drawn larger than life -- at true size it vanishes at a few metres; a bloom alone, worn in the hair, keeps its own)
def use(path, at, scale=1, **k): d = {"type": "component", "use": path, "at": [r(x) for x in at], "scale": r(scale * BLOOM_SCALE)}; d.update(k); return d
def dome(rad, h, material="centre"): return lathe([[0, h], [rad * .6, h * .85], [rad, h * .3], [rad * .95, 0]], material, sides=8)

GREEN = {"stem": "#4a7a34", "leaf": "#4f8a3a"}
BLOOMS = {}
def bloom(key, name, about, parts, materials, category="flowers/blooms"):
    BLOOMS[key] = {"kind": "item", "name": name + " (bloom)", "category": category, "era": "everywhere", "region": "everywhere", "_about": about,
                   "materials": materials, "parts": parts}

bloom("daisy", "Ox-eye daisy", "twenty narrow white rays round a domed yellow disc",
      [petals(n=18, shape="strap", length=.021, width=.0048, r0=.006, cup=4, curl=-10, cupped=.15, rows=2, cols=1),
       dome(.0075, .004)], {"petal": "#f6f4ec", "centre": "#e8b820"})
bloom("poppy", "Corn poppy", "four broad crumpled scarlet petals in a shallow bowl, a black blotch at each base, the green seed head ringed by dark stamens",
      [petals(n=4, shape="round", length=.034, width=.042, r0=.003, cup=32, curl=14, cupped=.45, throat=.18, rows=4, cols=2, phase=45),
       lathe([[0, .011], [.004, .010], [.005, .006], [.003, 0]], "centre", sides=6),
       lathe([[0, .0045], [.008, .004], [.0085, .002]], "stamen", sides=8)],
      {"petal": pick("#d8261e", "#d8261e", "#e8442a"), "throat": "#1a1412", "centre": "#7a8a5a", "stamen": "#1e1a1e"})
bloom("sunflower", "Sunflower", "two whorls of pointed golden rays round a broad brown disc of seeds",
      [petals(n=24, shape="pointed", length=.075, width=.024, r0=.06, cup=2, curl=-12, cupped=.2, rows=2, cols=1),
       lathe([[0, .012], [.04, .01], [.062, .004], [.062, 0]], "centre", sides=10),
       lathe([[0, .0125], [.02, .012], [.022, .011]], "eye", sides=8)],
      {"petal": "#f0b818", "centre": "#4a2e16", "eye": "#2a1a0c"})
bloom("tulip", "Tulip", "six oval petals in two whorls closed into a goblet",
      [petals(n=3, layers=2, shrink=.96, shape="oval", length=.055, width=.042, r0=.004, cup=72, cupStep=-6, curl=8, cupped=.6, rows=4, cols=2)],
      {"petal": pick("#d8302a", "#e8a218", "#8e3aa8", "#ec6a9a", "#f2eee2")})
bloom("rose", "Rose", "four whorls of rounded petals, each closer and more upright than the one outside it, round a closed heart",
      [petals(n=5, layers=3, shrink=.7, shape="round", length=.03, width=.032, r0=.002, cup=26, cupStep=26, curl=24, cupped=.5, rows=2, cols=2),
       petals(n=5, shape="pointed", length=.018, width=.008, r0=.002, cup=-30, curl=-10, material="sepal", rows=2, cols=1, phase=36)],
      {"petal": pick("#b8142a", "#d8466a", "#f2c8cc", "#f4e6c8", "#e8b030"), "sepal": "#3e6a2c"})   # (one colour a rose: two picked apart would not match)
bloom("cornflower", "Cornflower", "a ring of fringed blue florets round a darker purple heart",
      [petals(n=9, shape="fringed", length=.014, width=.009, r0=.004, cup=22, curl=-6, cupped=.3, rows=2, cols=1),
       petals(n=7, shape="strap", length=.006, width=.0022, r0=.001, cup=60, rows=2, cols=1, material="heart")],
      {"petal": "#3a6ad8", "heart": "#4a2a7a"})
bloom("buttercup", "Buttercup", "five glossy round yellow petals in a cup round green-yellow stamens",
      [petals(n=5, shape="round", length=.011, width=.011, r0=.0015, cup=38, curl=10, cupped=.45, rows=3, cols=2), dome(.003, .0025, "centre")],
      {"petal": "#f6d21a", "centre": "#b8b030"})
bloom("bell", "Bluebell", "a narrow bell of six fused petals, their tips curled back",
      [petals(n=6, shape="pointed", length=.016, width=.008, r0=.0015, cup=82, curl=-80, cupped=.6, rows=4, cols=1)],
      {"petal": pick("#5a5ad0", "#6a50c0")})
bloom("foxglove", "Foxglove bell", "a long tubular bell, its lip spotted white and purple inside",
      [petals(n=5, shape="round", length=.034, width=.022, r0=.004, cup=80, curl=-35, cupped=.55, band=.3, rows=3, cols=1, tips="lip")],
      {"petal": pick("#b45ac2", "#d07ab0", "#c060b0"), "lip": "#e8d8e8"})
bloom("lavender", "Lavender", "a spike of tiny purple florets in whorls up a short stalk",
      [rod([0, 0, 0], [0, .07, 0], .0012),
       *[petals(n=3, shape="round", length=.005, width=.0048, r0=.0012, cup=55, curl=20, cupped=.4, rows=2, cols=1, phase=i * 60, at=[0, r(.018 + i * .009), 0])
         for i in range(6)]],
      {"petal": pick("#8a6ac8", "#7a5ab8"), "stem": "#6a8a5a"})
bloom("iris", "Iris", "three broad falls hanging from a yellow-bearded throat, three standards rising between them",
      [petals(n=3, shape="lance", length=.05, width=.034, r0=.004, cup=12, curl=-70, cupped=.35, throat=.32, rows=4, cols=2),
       petals(n=3, shape="oval", length=.042, width=.026, r0=.003, cup=78, curl=20, cupped=.5, rows=4, cols=1, phase=60)],
      {"petal": pick("#5a3aa8", "#3a4ab8", "#7a3a8a"), "throat": "#f0c030"})
bloom("lily", "Lily", "six recurved lance-shaped tepals, the throat gold, long stamens standing out",
      [petals(n=6, shape="lance", length=.07, width=.024, r0=.004, cup=40, curl=-75, cupped=.3, throat=.3, rows=4, cols=2),
       *[rod([0, .004, 0], [r(.018 * math.cos(a)), .05, r(.018 * math.sin(a))], .0006, "stamen") for a in [i * math.pi / 3 for i in range(6)]]],
      {"petal": pick("#f6f2ea", "#f08a2a", "#e8a8b8"), "throat": "#f2c840", "stamen": "#8a4a1a"})
bloom("hibiscus", "Hibiscus", "five broad overlapping petals, a dark red eye, the long column of stamens standing out of it",
      [petals(n=5, shape="round", length=.065, width=.06, r0=.003, cup=22, curl=-8, cupped=.3, throat=.22, twist=12, rows=4, cols=2),
       rod([0, 0, 0], [0, .07, .012], .0016, "column"), {"type": "sphere", "material": "pollen", "r": .004, "sides": 6, "at": [0, .072, .012]}],
      {"petal": pick("#e01a3a", "#f06a1a", "#f2d22a", "#ec5aa0"), "throat": "#6a0a1a", "column": "#e8c0a0", "pollen": "#f2c020"})
bloom("frangipani", "Frangipani", "five waxy spoon-shaped petals turned like a pinwheel, the heart yellow",
      [petals(n=5, shape="spoon", length=.035, width=.022, r0=.002, cup=28, curl=-18, cupped=.3, twist=40, throat=.35, rows=4, cols=2)],
      {"petal": pick("#f8f4e8", "#f4c8d0"), "throat": "#f2c430"})

# ---- THE PLANTS -------------------------------------------------------------------------------------------------------
PLANTS = {}
def plant(key, name, about, parts, materials=None, category="flowers/plants"):
    PLANTS[key] = {"kind": "item", "name": name, "category": category, "era": "everywhere", "region": "everywhere", "_about": about,
                   "params": {"h": 1}, "materials": {**GREEN, **(materials or {})}, "parts": parts}
def leaf(y, yaw, L, W, cup=25, curl=-45, shape="lance", n=1):
    L, W = L * 1.4, W * 1.5   # (a little fuller than life too, to carry the larger blooms)
    return petals(n=n, shape=shape, length=L, width=W, cup=cup, curl=curl, cupped=.25, rows=2, cols=1, material="leaf", spread=150 if n > 1 else 360, at=[0, r(y), 0, yaw, 0, 0])
def stalk(h, bend=.03, rr=.0025):
    return sweep([[0, 0, 0], [bend * .4, h * .5, 0], [bend, h, 0]], rr)
B = "items/flowers/blooms/"
plant("daisy", "Ox-eye daisy", "a slender stem, a few toothed leaves at its foot, one bloom looking up and out",
      [stalk(.45, .03, .0018), leaf(.02, 0, .06, .012), leaf(.03, 140, .055, .012), leaf(.025, 250, .05, .011), leaf(.2, 260, .03, .007), leaf(.3, 80, .025, .006), use(B + "daisy", [.03, .45, 0, 0, 30, 0])])
plant("poppy", "Corn poppy", "a hairy stem bent under its nodding bloom, deeply cut leaves at the foot",
      [stalk(.55, .06, .0018), leaf(.03, 30, .08, .02, shape="fringed"), leaf(.04, 200, .07, .018, shape="fringed"), use(B + "poppy", [.06, .55, 0, 0, 25, 0])])
plant("sunflower", "Sunflower", "a tall thick stem, big heart-shaped leaves up it, the great head turned to the sun",
      [stalk(1.6, .08, .012), *[leaf(.3 + i * .3, i * 137, .22 - i * .02, .16 - i * .015, cup=10, curl=-40, shape="heart") for i in range(4)],
       use(B + "sunflower", [.08, 1.62, 0, 90, 60, 0])])
plant("tulip", "Tulip", "a straight stem from two broad grey-green leaves, the goblet upright",
      [stalk(.4, .01, .003), leaf(.02, 0, .2, .055, cup=70, curl=-25), leaf(.03, 180, .18, .05, cup=70, curl=-30), use(B + "tulip", [.01, .4, 0])])
plant("rose", "Rose", "a thorny cane with pinnate leaves, one open bloom",
      [stalk(.6, .05, .003), *[leaf(.15 + i * .13, 60 + i * 140, .05, .03, cup=20, curl=-25, shape="oval", n=3) for i in range(3)],
       use(B + "rose", [.05, .6, 0, 0, 20, 0])])
plant("cornflower", "Cornflower", "a wiry branched stem, narrow grey leaves, blue heads",
      [stalk(.5, .02, .0016), rod([.01, .3, 0], [.08, .45, .02], .0013), leaf(.1, 0, .07, .006), leaf(.2, 180, .06, .006),
       use(B + "cornflower", [.02, .5, 0, 0, 20, 0]), use(B + "cornflower", [.08, .45, .02, 90, 30, 0], scale=.85)])
plant("buttercup", "Buttercup", "a branching stem of shining yellow cups over cut leaves",
      [stalk(.35, .02, .0014), rod([.01, .2, 0], [-.06, .3, .03], .0012), rod([.015, .25, 0], [.05, .32, -.04], .0012),
       leaf(.02, 0, .05, .03, shape="fringed", cup=10, curl=-20), leaf(.02, 160, .05, .03, shape="fringed", cup=10, curl=-20),
       use(B + "buttercup", [.02, .35, 0]), use(B + "buttercup", [-.06, .3, .03], scale=.9), use(B + "buttercup", [.05, .32, -.04], scale=.85)])
BELLS = [(.36 - i * .03, .02 + i * .004, i * 70) for i in range(6)]
plant("bluebell", "Bluebell", "a stalk arching over at its top, the bells hanging along one side, strap leaves round its foot",
      [sweep([[0, 0, 0], [.01, .25, 0], [.04, .36, 0], [.07, .38, 0]], .0018),
       *[leaf(.01, i * 120, .22, .012, cup=75, curl=-50, shape="strap") for i in range(3)],
       *[use(B + "bell", [r(.07 - i * .012), r(.37 - i * .025), .01, 0, 160, 0]) for i in range(5)]])
plant("foxglove", "Foxglove", "a tall spike of hanging bells, all to one side, over a rosette of broad leaves",
      [stalk(1.2, .02, .005), *[leaf(.02, i * 90, .25, .09, cup=15, curl=-25, shape="oval") for i in range(4)],
       *[use(B + "foxglove", [r(.012), r(.62 + i * .075), r(.008), r(i * 30), 120, 0], scale=r(1 - i * .06)) for i in range(7)]])
plant("lavender", "Lavender", "a tuft of grey needle leaves, five flower spikes on long stalks",
      [*[sweep([[0, 0, 0], [r(.04 * math.cos(a)), .2, r(.04 * math.sin(a))], [r(.08 * math.cos(a)), .38, r(.08 * math.sin(a))]], .0012) for a in [i * 2.1 for i in range(3)]],
       *[use(B + "lavender", [r(.08 * math.cos(a)), .38, r(.08 * math.sin(a))]) for a in [i * 2.1 for i in range(3)]],
       petals(n=10, shape="strap", length=.09, width=.004, cup=55, curl=-30, rows=2, cols=1, material="leaf")], {"leaf": "#7a9a7a", "stem": "#6a8a5a"})
plant("iris", "Iris", "sword-like leaves in a fan, one tall stalk with its bloom",
      [stalk(.7, .01, .004), petals(n=5, shape="lance", length=.45, width=.03, cup=82, curl=-8, spread=70, rows=3, cols=1, material="leaf"),
       use(B + "iris", [.01, .7, 0])])
plant("lily", "Lily", "a stout leafy stem, whorled narrow leaves, two trumpets turned out",
      [stalk(.9, .02, .004), *[leaf(.15 + i * .14, i * 75, .1, .015, cup=30, curl=-35) for i in range(5)],
       use(B + "lily", [.02, .9, 0, 0, 55, 0]), use(B + "lily", [.02, .85, 0, 180, 60, 0], scale=.9)])

# ---- THE CATALOGUE --------------------------------------------------------------------------------------------------------
def main():
    for k, v in BLOOMS.items(): write("blooms/" + k, v)
    for k, v in PLANTS.items(): write(k, v)
    ip = os.path.join(ROOT, "assets", "index.json"); idx = json.load(open(ip))
    idx["categories"] = [c for c in idx["categories"] if c["name"] != "Items: flowers"]
    pos = next(i for i, c in enumerate(idx["categories"]) if c["name"] == "Items: food") + 1
    idx["categories"].insert(pos, {"name": "Items: flowers", "kind": "item", "paths": ["items/flowers/" + k for k in PLANTS] + ["items/flowers/blooms/" + k for k in BLOOMS]})
    json.dump(idx, open(ip, "w"), indent=2, ensure_ascii=False); open(ip, "a").write("\n")
    print(len(BLOOMS), "blooms,", len(PLANTS), "plants")

if __name__ == "__main__": main()
