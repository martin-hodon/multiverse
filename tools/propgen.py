#!/usr/bin/env python3
"""PROPS (2026-10-02): the world's moving and carried things as items, out of the code that used to build them --
the sack (architecture.js sack), the mill's water wheel (waterWheel), the windmill's sail cross (index.html), the river
barge and its gangplank (architecture.js barge, freight.js), the cart wheel and the three cart bodies with their five
loads each (carts.js wheelDef, cartBody, load), the arrow (archery.js). Same dimensions as before, from the same
period sources; the game builds them through items.js now (architecture.js itemGroup / itemInstanced).

    python3 tools/propgen.py
"""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ITEMS = os.path.join(ROOT, "assets", "items")
DARK, IRON, STAVE = "#4e3a24", "#3e3a38", "#9a7040"


def write(path, doc):
    full = os.path.join(ITEMS, path + ".json")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")


def item(name, category, about, params, materials, parts, markers=None, hold=None, era="-500-1900", region="everywhere"):
    d = {"kind": "item", "name": name, "category": category, "era": era, "region": region, "_about": about,
         "params": params, "materials": materials, "parts": parts}
    if markers: d["markers"] = markers
    if hold: d["hold"] = hold
    return d


def box(id_, mat, size, at, **k):
    return {"id": id_, "type": "box", "material": mat, "size": size, "at": at, **k}


def rod(id_, mat, r, a, b, sides=8, **k):
    return {"id": id_, "type": "rod", "material": mat, "r": r, "from": a, "to": b, "sides": sides, **k}


PROPS = {}

# ---- the sack: lying along x, its bottom at the origin, the tied neck at +x
PROPS["tools/sack"] = item("Sack", "tool", "a grain sack lying on its side, tied at the neck -- the mill's, a cart's load, the barge's cargo",
    {}, {"cloth": "#c4a672", "neck": "#9c8258"}, [
        {"id": "sack", "type": "sphere", "material": "cloth", "r": 0.3, "sides": 10, "at": [0, 0.24, 0], "stretch": [1.65, 0.8, 0.95]},
        {"id": "neck", "type": "sphere", "material": "neck", "r": 0.09, "sides": 6, "at": [0.525, 0.28, 0]}],
    hold={"grip": [0, 0.24, 0], "axis": [1, 0, 0], "face": [0, 1, 0]})

# ---- the sheaf: a bound bundle of cut corn lying along x, centred on the origin, its bottom at y 0 -- the butts at -x,
# the ears at +x fanning out past the band (a cart's harvest load: index.html CHORES)
PROPS["tools/sheaf"] = item("Sheaf", "tool", "a sheaf of corn bound with a twist of its own straw: the butts at -x, the ears fanning out at +x, a metre long -- the harvest wagon's load",
    {}, {"straw": "#d8bb62", "ears": "#c79f48", "band": "#a88a40"}, [
        rod("butts", "straw", 0.12, [-0.5, 0.15, 0], [0, 0.15, 0], 8, r0=0.12, r1=0.095),
        rod("ears", "ears", 0.12, [0, 0.15, 0], [0.5, 0.15, 0], 8, r0=0.095, r1=0.15),
        rod("band", "band", 0.1, [-0.06, 0.15, 0], [0.01, 0.15, 0], 8)],
    hold={"grip": [0, 0.15, 0], "axis": [1, 0, 0], "face": [0, 1, 0]})

# ---- the sack stood on its end, the neck up (tools/sack turned: an arch item turns only about y)
PROPS["tools/sack-standing"] = item("Sack (standing)", "tool", "a grain sack stood on its end, tied at the neck on top -- tools/sack rolled up, its bottom at the origin",
    {}, {}, [{"id": "sack", "use": "items/tools/sack", "at": [0.24, 0.495, 0, 0, 0, 90]}])

# ---- the water wheel: axis along z through the origin, the axle running back (-z) through the wall to the pit wheel
PROPS["components/water-wheel"] = item("Water wheel", "components", "an undershot mill wheel: two rims of fourteen felloes on seven spokes each, paddle boards between them, the axle back through the wall to the pit wheel inside -- turned about z by the game",
    {"r": 3.05, "w": 1.2, "axleBack": 5.2, "axleFwd": 0.95, "paddles": 14},
    {"dark": DARK, "plank": "#7a5a36"}, [
        rod("hub", "dark", 0.22, [0, 0, "0 - (w + 0.3) / 2"], [0, 0, "(w + 0.3) / 2"], 10),
        rod("axle", "dark", 0.14, [0, 0, "0 - axleBack"], [0, 0, "axleFwd"], 8),
        {"id": "pit wheel", "use": "items/components/face-gear", "params": {"r": 1.05, "w": 0.16, "n": 24}, "at": [0, 0, "0 - axleBack + 0.3"]},   # (its cogs toward -z: into the wallower)
        box("felloes", "dark", ["2 * (r - 0.08) * 0.2282 + 0.02", 0.16, 0.1], [[0, 0, "w / 2"], [0, 0, "0 - w / 2"]], around={"n": 14, "r": "r - 0.08", "plane": "xy", "start": 12.857}),
        box("spokes", "plank", ["r - 0.08 - 0.28", 0.1, 0.08], [[0, 0, "w / 2", 0, 0, 90], [0, 0, "0 - w / 2", 0, 0, 90]], around={"n": 7, "r": "(r - 0.08 - 0.08 + 0.2) / 2", "plane": "xy"}),
        box("paddles", "plank", [0.6, 0.05, "w - 0.12"], [0, 0, 0, 0, 0, 90], around={"n": "paddles", "r": "r - 0.32", "plane": "xy"})])

# ---- the windmill's sail cross: about z, the arm upright at its own +y; the game turns it
PROPS["components/windmill-arm"] = item("Windmill arm", "components", "one arm of a sail cross: the whip (spar) up its +y and the cloth sail laced to its lattice beside it -- the LATTICE in front of the cloth: bars across every ~45 cm and the hemlath along its outer edge (a component of the sail cross)",
    {"R": 5.0}, {"wood": "#6a5236", "cloth": "canvas"}, [
        box("whip", "wood", [0.28, "R", 0.16], [0, "R / 2", 0]),
        box("sail", "cloth", [1.5, "R * 0.78", 0.07], [0.85, "R * 0.56", 0]),
        box("bars", "wood", [1.62, 0.07, 0.06], [[0.85, f"R * 0.17 + {i} * R * 0.78 / 9", 0.065] for i in range(10)]),
        box("hemlath", "wood", [0.08, "R * 0.79", 0.08], [1.62, "R * 0.56", 0.03])])
PROPS["components/windmill-sails"] = item("Windmill sails", "components", "the sail cross of a post or tower mill: four arms on the windshaft, R long, the shaft running back into the cap",
    {"R": 5.0}, {"wood": "#6a5236", "cloth": "canvas"}, [
        {"id": "arms", "use": "items/components/windmill-arm", "params": {"R": "R"}, "around": {"n": 4, "r": 0, "plane": "xy", "start": 90}},
        rod("windshaft", "wood", 0.24, [0, 0, 0.2], [0, 0, -1.6], 8)])

# ---- the river barge: +x forward, its deck at deckY; the hold's ten cargo places, the gangplank's foot
PROPS["ships/barge"] = item("River barge", "ships", "a flat river barge for freight: a long hull with a raked bow and stern, a plank deck, gunwales, the cabin aft with its roof, the tiller, bollards; ten cargo places on deck (`hold` markers), the gangplank hinged at the north gunwale (its foot a `plank` marker)",
    {"deckY": 0.63, "halfL": 5.4, "halfW": 1.7},
    {"hull": "planks", "deck": "deck", "dark": DARK}, [
        box("hull", "hull", [11, 1.4, 3.5], [0, -0.1, 0]),
        box("bow", "hull", [2.4, 1.1, 3.2], [6.0, 0.05, 0, 0, 0, 32]),
        box("stern", "hull", [2.0, 1.1, 3.2], [-6.0, 0.05, 0, 0, 0, -28]),
        box("deck", "deck", [10.8, 0.06, 3.3], [0, 0.6, 0]),
        box("gunwales", "dark", [11, 0.35, 0.12], [[0, 0.8, 1.7], [0, 0.8, -1.7]]),
        box("cabin", "hull", [2.2, 1.5, 2.2], [-4.0, 1.38, 0]),
        box("cabin roof", "dark", [2.5, 0.1, 2.5], [-4.0, 2.18, 0]),
        box("tiller", "dark", [1.8, 0.08, 0.08], [-5.6, 1.15, 0, 0, 0, -20]),
        rod("bollards", "dark", 0.11, [0, 0.6, 0], [0, 1.1, 0], 8, at=[[-2.5, 0, -1.55], [2.5, 0, -1.55]])],
    markers=[{"role": "hold", "at": [-2.5 + (i % 5) * 1.3, 0.63, -0.75 if i < 5 else 0.75], "data": {"i": i}} for i in range(10)]
            + [{"role": "plank", "at": [-0.5, 0.63, -4.1]}], era="1000-1900", region="Europe's rivers")
PROPS["components/gangplank"] = item("Gangplank", "components", "a plank to walk aboard, hinged at its origin, running 2.6 m along -z",
    {}, {"wood": "#7a5a36"}, [box("plank", "wood", [1.2, 0.06, 2.6], [0, 0, -1.3])])

# ---- the cart wheel: axis along z, centred on its axle; hub, radial spokes, iron-shod felloes
PROPS["components/cart-wheel"] = item("Cart wheel", "components", "a spoked cart wheel r in radius: hub, n radial spokes, iron-shod felloe segments -- rolled about z by the game",
    {"r": 0.75, "n": 12}, {"dark": DARK, "spoke": "#846040"}, [
        rod("hub", "dark", 0.1, [0, 0, -0.12], [0, 0, 0.12], 10),
        box("spokes", "spoke", ["r - 0.04 - 0.035 - 0.08", 0.04, 0.04], [0, 0, 0, 0, 0, 90], around={"n": "n", "r": "(0.08 + r - 0.04 - 0.035) / 2", "plane": "xy"}),
        box("felloes", "dark", ["2 * (r - 0.04) * sin(3.14159265 / n) / cos(3.14159265 / n) + 0.015", 0.08, 0.06], [0, 0, 0], around={"n": "n", "r": "r - 0.04", "plane": "xy", "start": "180 / n"})])

# ---- the three cart bodies and their loads (carts.js CART_SIZES, load): origin on the ground under the bed's centre, +x forward
CARTS = {
    "small": {"name": "Cart", "bedL": 1.6, "bedW": 1.05, "floor": 0.8, "side": 0.35, "seatX": 0.5, "wheels": [(-0.1, 0.75)]},
    "medium": {"name": "Farm wagon", "bedL": 2.8, "bedW": 1.4, "floor": 0.85, "side": 0.45, "seatX": 1.05, "wheels": [(1.05, 0.45), (-1.05, 0.6)]},
    "large": {"name": "Freight wagon", "bedL": 4.2, "bedW": 1.7, "floor": 0.95, "side": 0.6, "seatX": 1.75, "wheels": [(1.55, 0.6), (-1.55, 0.75)]},
}
BIG = {"r": 0.35, "h": 0.95, "bulge": round(1 - 0.29 / 0.35, 3)}
KEG = {"r": 0.21, "h": 0.55, "bulge": round(1 - 0.17 / 0.21, 3)}


def loads(size, floor):
    """the five load variants, as item placements: big casks lying across the bed (chocked pyramids), standing casks,
    kegs filling the gaps, grain sacks across the bed in two courses (carts.js load, the same numbers)"""
    out = {k: [] for k in range(6)}
    def big_lying(v, xs, y=None):
        y = floor + BIG["r"] if y is None else y
        for x in xs: out[v].append(("cask", BIG, [x, round(y, 4), -BIG["h"] / 2, 0, 90, 0]))
    top = floor + BIG["r"] + BIG["r"] * math.sqrt(3)
    def kegs_up(v, pts):
        for x, z in pts: out[v].append(("cask", KEG, [x, floor, z]))
    def big_up(v, pts):
        for x, z in pts: out[v].append(("cask", BIG, [x, floor, z]))
    def sacks(v, xs, course=0):
        for x in xs: out[v].append(("sack", None, [x, round(floor + course * 0.4, 4), 0, 90, 0, 0]))
    def sheaves(v, L, courses):   # (the harvest load, 5: sheaves across the bed, butts out to either side in turn, heaped)
        for c in range(courses):
            half = (L - 0.36) / 2 - c * 0.14
            n = int(round(2 * half / 0.28)) + 1
            for j in range(n): out[v].append(("sheaf", None, [round(-half + j * 0.28, 4), round(floor + c * 0.22, 4), 0, 90 if (j + c) % 2 else -90, 0, 0]))
    if size == "small":
        big_lying(0, [-0.15]); kegs_up(0, [(0.5, 0)])
        kegs_up(1, [(-0.45, 0.25), (-0.45, -0.25), (0.05, 0.25), (0.05, -0.25), (0.5, 0)])
        big_up(2, [(-0.35, 0), (0.4, 0)])
        sacks(3, [-0.55, -0.03, 0.49]); sacks(3, [-0.29, 0.23], 1)
        big_lying(4, [-0.3]); sacks(4, [0.35])
        sheaves(5, 1.6, 3)
    elif size == "medium":
        big_lying(0, [-0.95, -0.2, 0.55]); big_lying(0, [-0.575, 0.175], top)
        big_up(1, [(-0.85, 0), (-0.1, 0)]); kegs_up(1, [(0.55, 0.4), (0.55, 0), (0.55, -0.4)])
        kegs_up(2, [(-1, 0.45), (-1, 0), (-1, -0.45), (-0.55, 0.45), (-0.55, 0), (-0.55, -0.45), (-0.1, 0.45), (-0.1, 0), (-0.1, -0.45), (0.35, 0.2), (0.35, -0.2)])
        sacks(3, [-1.15, -0.63, -0.11, 0.41, 0.93]); sacks(3, [-0.89, -0.37, 0.15, 0.67], 1)
        big_lying(4, [-0.95, -0.2]); sacks(4, [0.45, 0.97])
        sheaves(5, 2.8, 4)
    else:
        big_lying(0, [-1.6, -0.85, -0.1, 0.65]); big_lying(0, [-1.225, -0.475, 0.275], top); kegs_up(0, [(1.3, 0.45), (1.3, -0.45)])
        big_up(1, [(-1.5, 0.38), (-1.5, -0.38), (-0.75, 0.38), (-0.75, -0.38), (0, 0.38), (0, -0.38), (0.75, 0.38), (0.75, -0.38)])
        big_lying(2, [-1.6, -0.85, -0.1]); kegs_up(2, [(0.55, 0.55), (0.55, 0), (0.55, -0.55), (1.0, 0.55), (1.0, 0), (1.0, -0.55)])
        xs = [-1.82, -1.3, -0.78, -0.26, 0.26, 0.78, 1.3, 1.82]; sacks(3, xs); sacks(3, [x + 0.26 for x in xs[:-1]], 1)
        big_lying(4, [-1.6, -0.85, -0.1]); big_lying(4, [-1.225, -0.475], top); sacks(4, [0.6, 1.12, 1.64]); sacks(4, [0.86, 1.38], 1)
        sheaves(5, 4.2, 4)
    return out


for size, S in CARTS.items():
    L, W, F, H = S["bedL"], S["bedW"], S["floor"], S["side"]
    parts = [
        box("bed", "wood", [L, 0.06, W], [0, F - 0.03, 0]),
        box("sides", "wood", [L, H, 0.05], [[0, F + H / 2, W / 2 + 0.025], [0, F + H / 2, -W / 2 - 0.025]]),   # (an item's box is placed by its centre)
        box("headboard", "wood", [0.05, H, W + 0.1], [[L / 2 + 0.025, F + H / 2, 0], [-L / 2 - 0.025, F + H / 2, 0]]),
        box("driver's board", "dark", [0.42, 0.05, W - 0.1], [S["seatX"], F + 0.44, 0]),
        box("board legs", "dark", [0.05, 0.42, 0.06], [[S["seatX"], F + 0.21, W / 2 - 0.1], [S["seatX"], F + 0.21, -W / 2 + 0.1]]),
        box("footboard", "dark", [0.36, 0.04, W - 0.2], [L / 2 + 0.2, F + 0.08, 0]),
    ]
    for i, (x, r) in enumerate(S["wheels"]):
        parts.append(rod(f"axle {i + 1}", "dark", 0.05, [x, r, -(W + 0.5) / 2], [x, r, (W + 0.5) / 2], 8))
        bh = max(0.04, F - 0.06 - r)
        parts.append(box(f"bolster {i + 1}", "dark", [0.16, round(bh, 4), W * 0.8], [x, round((F - 0.06 + r) / 2, 4), 0]))
    if len(S["wheels"]) > 1:
        parts.append(box("reach", "dark", [L - 0.4, 0.08, 0.12], [0, F - 0.11, 0]))
    for v, pieces in loads(size, F).items():
        for j, (kind, P, at) in enumerate(pieces):
            if kind == "cask": parts.append({"id": f"load {v} cask {j + 1}", "use": "items/furniture/cask", "params": P, "at": at, "when": {"load": v}, "seed": j})
            else: parts.append({"id": f"load {v} {kind} {j + 1}", "use": f"items/tools/{kind}", "at": at, "when": {"load": v}})
    PROPS[f"components/cart-{size}"] = item(S["name"], "components", f"the body of a {S['name'].lower()} ({L} m bed on {len(S['wheels'])} axle(s)): bed, sides, head- and tailboards, the driver's board, footboard, axles and bolsters -- its wheels apart (components/cart-wheel), and its LOAD by `load` (0..4: casks lying in chocked pyramids, standing casks, kegs, sacks in two courses; 5 sheaves heaped, the harvest's, never on the road; -1 empty)",
        {"load": 0, "seatTop": round(F + 0.465, 4), "seatX": S["seatX"], "bedL": L, "bedW": W, "floor": F, "side": H,
         **{k: v for i, (x, r) in enumerate(S["wheels"]) for k, v in ((f"axle{i + 1}X", x), (f"wheel{i + 1}R", r))}}, {"wood": {"pick": ["#7a5a36", "#6f5433", "#846040", "#6a4a2c"]}, "dark": DARK}, parts)

# ---- the arrow: its tip at the origin, the shaft back along -x
PROPS["weapons/arrow"] = item("Arrow", "weapon/missile", "a war arrow: an iron bodkin head, a 76 cm shaft, two crossed fletchings -- its tip at the origin, back along -x",
    {}, {"shaft": "#9a7a4a", "head": "#5e6266", "fletch": "#d8d0c0", "cock": "#b03a2e"}, [
        rod("shaft", "shaft", 0.0045, [-0.8, 0, 0], [-0.04, 0, 0], 5),
        {"id": "head", "type": "rod", "material": "head", "r0": 0.009, "r1": 0.0005, "sides": 4, "from": [-0.05, 0, 0], "to": [0, 0, 0]},
        {"id": "fletch", "type": "plate", "material": "fletch", "thick": 0.001, "at": [0, 0, 0], "outline": [[-0.79, 0.022], [-0.79, -0.022], [-0.68, 0]]},
        {"id": "cock feather", "type": "plate", "material": "cock", "thick": 0.001, "at": [0, 0, 0, 0, 90, 0], "outline": [[-0.79, 0.022], [-0.79, -0.022], [-0.68, 0]]}],
    hold={"grip": [-0.72, 0, 0], "axis": [1, 0, 0], "face": [0, 1, 0]})


# ---- ALTERNATIVES (2026-10-02): the code-built versions of things the catalogue already had, kept as assets beside them
# (the game uses these: they are what it always drew) -- the fisherman's rowing boat (beside ships/skiff), its oars, the
# plain rod (beside tools/fishing-rod), the two-frustum stave barrel (beside furniture/cask), the tableware's mug, jug,
# bucket and trough and the plain foods on its plates (beside tools/pitcher, tools/bucket, food/*)
PROPS["ships/fisher-boat"] = item("Fisherman's boat", "ships", "the fisherman's rowing boat, 3.6 x 1.5 m: a box hull with a raked bow and stern, the dark bilge, two thwarts, the creel -- bow along +x, its origin at the waterline's centre (an alternative to ships/skiff)",
    {}, {"hull": "#4e3a24", "plank": "#7a5a36", "bilge": "#3a2a18", "creel": "#b8965a"}, [
        box("hull", "hull", [3.6, 0.55, 1.5], [0, 0, 0]),
        box("bow", "hull", [1.0, 0.5, 1.3], [2.0, 0.12, 0, 0, 0, 30]),
        box("stern", "hull", [0.8, 0.45, 1.3], [-1.9, 0.08, 0, 0, 0, -22]),
        box("bilge", "bilge", [3.2, 0.04, 1.2], [0, 0.02, 0]),
        box("thwarts", "plank", [0.25, 0.05, 1.4], [[-0.7, 0.3, 0], [0.6, 0.3, 0]]),
        box("creel", "creel", [0.5, 0.3, 0.6], [1.2, 0.3, 0.3])], era="-500-1900", region="everywhere")
PROPS["components/fisher-oar"] = item("Oar", "components", "a rowing boat's oar, hinged at its origin (the gunwale): the handle inboard, the loom and blade outboard along +z (`side` -1: along -z)",
    {"side": 1}, {"loom": "#7a5a36", "blade": "#6a4a2c"}, [
        rod("loom", "loom", 0.025, [0, 0, "side * -0.4"], [0, 0, "side * 2.2"], 6),
        box("blade", "blade", [0.14, 0.03, 0.5], [0, 0, "side * 2.0"])])
PROPS["tools/fishing-pole"] = item("Fishing pole", "tool", "a plain rod cut from a sapling, 2.4 m, thick at the hand -- along +y from its origin (an alternative to tools/fishing-rod)",
    {}, {"wood": "#8a6a3a"}, [{"id": "pole", "type": "rod", "material": "wood", "r0": 0.014, "r1": 0.006, "sides": 5, "from": [0, 0, 0], "to": [0, 2.4, 0]}],
    hold={"grip": [0, 0.3, 0], "axis": [0, 1, 0], "face": [1, 0, 0]})
PROPS["components/fishing-line"] = item("Fishing line", "components", "a fishing line hanging 1.8 m from its origin (the rod's tip) -- the game stretches it to the water",
    {}, {"line": "#d8d8d0"}, [{"id": "line", "type": "rod", "material": "line", "r0": 0.004, "r1": 0.004, "sides": 3, "from": [0, 0, 0], "to": [0, -1.8, 0]}])
PROPS["furniture/barrel"] = item("Barrel", "furniture/storage", "a stave barrel: two frustums meeting at the belly, iron hoops at the chimes and quarters -- stood on its end, its foot at the origin; `h`, `belly`, `head` (big 0.95 / 0.35 / 0.29, a keg 0.55 / 0.21 / 0.17; an alternative to furniture/cask)",
    {"h": 0.95, "belly": 0.35, "head": 0.29, "hoop1": 0.06, "hoop2": 0.3, "hoop3": 0.65, "hoop4": 0.89},
    {"stave": "#9a7040", "hoop": "#4a4644"}, [
        {"id": "staves", "type": "lathe", "material": "stave", "sides": 12, "profile": [["head", 0], ["belly", "h / 2"], ["head", "h"]]},
        {"id": "hoops", "type": "lathe", "material": "hoop", "sides": 12, "caps": False,
         "profile": [["head + (belly - head) * (1 - abs(t - h / 2) / (h / 2)) + 0.012", "t - 0.0225"], ["head + (belly - head) * (1 - abs(t - h / 2) / (h / 2)) + 0.012", "t + 0.0225"]],
         "_about": "(one hoop per t: the four below)"}], era="-100-1900", region="Europe")
# (the hoops' t: written out, one part each -- an item's expressions have no loop)
PROPS["furniture/barrel"]["parts"] = [PROPS["furniture/barrel"]["parts"][0]] + [
    {"id": f"hoop {k}", "type": "lathe", "material": "hoop", "sides": 12, "caps": False,
     "profile": [[f"head + (belly - head) * (1 - abs(hoop{k} * h / 0.95 - h / 2) / (h / 2)) + 0.012", f"hoop{k} * h / 0.95 - 0.0225"],
                 [f"head + (belly - head) * (1 - abs(hoop{k} * h / 0.95 - h / 2) / (h / 2)) + 0.012", f"hoop{k} * h / 0.95 + 0.0225"]]} for k in (1, 2, 3, 4)]
PROPS["components/meal-chute"] = item("Meal chute", "components", "the mill's meal chute: a trough of a plank sloping down from the stones (its upper end at the origin) toward -z",
    {}, {"wood": "#6a5236"}, [box("chute", "wood", [0.35, 0.12, 1.4], [0, 0, -0.65, 0, -22, 0])])
# the tableware: a vessel's WALLS are one lathe (id "walls": the drink's level reads its inside from it, tableware.js),
# its floor `floor` thick; a trough's box by w, h, d, t, floor
def vessel(key, name, about, profile, floor, colour):
    PROPS["tableware/" + key] = item(name, "tableware", about, {"floor": floor}, {"ware": colour}, [
        {"id": "walls", "type": "lathe", "material": "ware", "sides": 10, "caps": False, "double": True, "profile": profile},
        {"id": "floor", "type": "lathe", "material": "ware", "sides": 10, "profile": [[profile[0][0], 0], [profile[0][0], floor]]}])
vessel("mug", "Mug", "a stoneware mug, open: you see the ale in it", [[0.045, 0], [0.045, 0.12]], 0.008, "#8b6a4a")
vessel("jug", "Jug", "a stoneware jug: a belly, then a mouth wider than its foot", [[0.065, 0], [0.085, 0.15], [0.075, 0.25]], 0.008, "#6f5a46")
vessel("bucket", "Wooden bucket", "a wooden bucket, the fountain's", [[0.11, 0], [0.13, 0.3]], 0.02, "#6b4a2c")
PROPS["tableware/trough"] = item("Water trough", "tableware", "a stone water trough, open at the top (the water at its level: tableware.js)",
    {"w": 2.2, "h": 0.5, "d": 0.7, "t": 0.09, "floor": 0.12}, {"stone": {"pattern": "stone/ashlar", "palette": "sandstone-grey"}}, [
        box("floor", "stone", ["w", "floor", "d"], [0, "floor / 2", 0]),
        box("long sides", "stone", ["w", "h", "t"], [[0, "h / 2", "(d - t) / 2"], [0, "h / 2", "0 - (d - t) / 2"]]),
        box("ends", "stone", ["t", "h", "d - 2 * t"], [["(w - t) / 2", "h / 2", 0], ["0 - (w - t) / 2", "h / 2", 0]])])
PROPS["food/plain-loaf"] = item("Loaf (plain)", "food/bread", "a plain loaf on a plate: one squashed ball", {}, {"crust": "#b8803e"},
    [{"id": "loaf", "type": "sphere", "material": "crust", "r": 0.085, "sides": 8, "at": [0, 0.06, 0], "stretch": [1.4, 0.6, 0.9]}])
PROPS["food/cheese-slice"] = item("Cheese (plain)", "food/dairy", "a plain wedge of cheese on a plate", {}, {"cheese": "#f0c95a"},
    [{"id": "wedge", "type": "plate", "material": "cheese", "thick": 0.05, "at": [-0.06, 0.04, 0.05, 0, -90, 0], "outline": [[-0.075, -0.06], [0.075, -0.06], [-0.075, 0.06]]}])
PROPS["food/sausage"] = item("Sausage", "food/meat", "one sausage, lying on a plate", {}, {"skin": "#8a3a2a"},
    [rod("sausage", "skin", 0.02, [-0.095, 0.035, 0], [0.095, 0.035, 0], 6)])
PROPS["food/cabbage-head"] = item("Cabbage head (field)", "food/vegetable", "a cabbage head standing in its field row: a pale round head in a cup of darker outer leaves spread open round it (2026-10-24: was one six-sided ball, which read as a green cube) -- still low-poly, for a field of hundreds", {"r": [0.16, 0.22]},
    {"head": {"pick": ["#b9d18c", "#aecb82"]}, "leaf": {"pick": ["#6f9a4c", "#628f45"]}},
    [{"id": "head", "type": "sphere", "material": "head", "r": "r * 0.62", "sides": 8, "at": [0, "r * 0.62", 0], "stretch": [1, 0.92, 1]},
     {"id": "leaves", "type": "lathe", "material": "leaf", "profile": [["r * 0.3", 0], ["r * 0.85", "r * 0.22"], ["r * 1.05", "r * 0.6"], ["r * 0.9", "r * 0.95"]], "sides": 9, "caps": False, "double": True, "faceted": True}])

PROPS["furniture/barrel-on-side"] = item("Barrel on its side", "furniture/storage", "a stave barrel laid on its side, its axis along z, chocked -- its lowest point at the origin's height (furniture/barrel turned)",
    {"h": 0.95, "belly": 0.35, "head": 0.29}, {}, [{"id": "barrel", "use": "items/furniture/barrel", "params": {"h": "h", "belly": "belly", "head": "head"}, "at": [0, "belly", "0 - h / 2", 0, 90, 0]}])
PROPS["components/fish-hanging"] = item("Hanging fish", "components", "a fish hung by its tail from a drying rack: food/fish, head down", {}, {},
    [{"id": "fish", "use": "items/food/fish", "params": {"s": 1.0}, "at": [0, 0, 0, 0, 0, -90]}])


# ---- PLAIN FURNITURE (2026-10-02, were architecture.js furniture(): the palace's and the castle's) -- alternatives to the
# catalogue's finer pieces, a few boxes each; their sit and lie places markers
W_, CL_, GD_ = {"wood": "oak"}, {"cloth": "velvet-red"}, {"gold": "gilt"}
PROPS["furniture/plain-table"] = item("Table (plain)", "furniture/table", "a plain board table on four square legs, 1.8 x 0.95 m (an alternative to the kitchen and trestle tables)",
    {}, dict(W_), [box("top", "wood", [1.8, 0.08, 0.95], [0, 0.75, 0]),
                   box("legs", "wood", [0.09, 0.72, 0.09], [[a * 0.8, 0.36, b * 0.38] for a in (-1, 1) for b in (-1, 1)])])
PROPS["furniture/plain-chair"] = item("Chair (plain)", "furniture/seat", "a plain chair with a cushioned seat, its back toward -z",
    {}, {**W_, **CL_}, [box("seat", "cloth", [0.46, 0.07, 0.46], [0, 0.46, 0]), box("back", "wood", [0.46, 0.55, 0.07], [0, 0.77, -0.2]),
                        box("legs", "wood", [0.05, 0.44, 0.05], [[a * 0.19, 0.22, b * 0.19] for a in (-1, 1) for b in (-1, 1)])],
    markers=[{"role": "seat", "at": [0, 0, 0], "data": {"w": 0.46, "d": 0.46, "top": 0.495}}])
PROPS["furniture/plain-wardrobe"] = item("Wardrobe (plain)", "furniture/storage", "a tall plain wardrobe on four block feet, with a crown moulding and a gilt line where its doors meet (+z)",
    {}, {**W_, **GD_}, [box("body", "wood", [1.6, 2.3, 0.65], [0, 1.25, 0]), box("crown", "wood", [1.72, 0.14, 0.74], [0, 2.46, 0]),
                        box("doors", "gold", [0.04, 1.9, 0.06], [0, 1.2, 0.34]),
                        box("feet", "wood", [0.12, 0.11, 0.12], [[a * 0.72, 0.055, b * 0.24] for a in (-1, 1) for b in (-1, 1)])])
PROPS["furniture/plain-bed"] = item("Bed (plain)", "furniture/bed", "a plain bed: frame, mattress, a headboard at -z and a bolster",
    {}, {**W_, "bedding": "linen"}, [box("frame", "wood", [1.7, 0.35, 2.15], [0, 0.3, 0]), box("mattress", "bedding", [1.6, 0.22, 2.05], [0, 0.58, 0]),
                                     box("headboard", "wood", [1.7, 1.0, 0.09], [0, 0.8, -1.05]), box("bolster", "bedding", [1.2, 0.16, 0.5], [0, 0.74, -0.7]),
                                     box("legs", "wood", [0.09, 0.135, 0.09], [[a * 0.79, 0.0675, b * 1.0] for a in (-1, 1) for b in (-1, 1)])],
    markers=[{"role": "lie", "at": [0, 0, 0], "data": {"w": 1.6, "d": 2.05, "top": 0.69}}])
PROPS["furniture/sofa"] = item("Sofa", "furniture/seat", "an upholstered sofa (a canape) on four gilt legs, with its back toward -z and two arms",
    {}, {**CL_, **GD_}, [box("seat", "cloth", [2.1, 0.42, 0.85], [0, 0.35, 0]), box("back", "cloth", [2.1, 0.55, 0.18], [0, 0.82, -0.33]),
                    box("arms", "cloth", [0.18, 0.38, 0.85], [[-0.96, 0.73, 0], [0.96, 0.73, 0]]),
                    box("legs", "gold", [0.06, 0.15, 0.06], [[a * 0.98, 0.075, b * 0.36] for a in (-1, 1) for b in (-1, 1)])],
    markers=[{"role": "seat", "at": [0, 0, 0], "data": {"w": 2.1, "d": 0.85, "top": 0.56}}], era="1650-1900")
PROPS["furniture/chandelier"] = item("Chandelier", "furniture/light", "a gilt chandelier hanging 1.5 m below its origin (the ceiling): the rod, the bowl, its ring, the drop",
    {}, dict(GD_), [rod("rod", "gold", 0.035, [0, 0, 0], [0, -1.0, 0], 6),
                    {"id": "bowl", "type": "lathe", "material": "gold", "sides": 10, "profile": [[0.3, -1.26], [0.58, -0.98]]},
                    {"id": "ring", "type": "lathe", "material": "gold", "sides": 10, "profile": [[0.6, -0.995], [0.6, -0.925]]},
                    {"id": "drop", "type": "sphere", "material": "gold", "r": 0.14, "sides": 8, "at": [0, -1.35, 0]}], era="1600-1900")


# ---- THE TRADE SIGNS (2026-10-02): what hung over a medieval workshop's door -- a wrought bracket out from the wall and
# the trade's emblem on chains from it: the smith's anvil, the baker's pretzel, the potter's jug, the weaver's shuttle,
# the tailor's shears, the carpenter's saw, the cooper's cask, the butcher's ham, the inn's ale-bush and tankard.
# Origin on the wall's face, +z out over the street, the emblem in the y-z plane (seen from along the street); `kind`
# picks it (a word: `when`)
import math as _m
def _heart(n=20, k=0.016):
    pts = []
    for i in range(n):
        t = 2 * _m.pi * i / n
        pts.append([round(16 * _m.sin(t) ** 3 * k, 4), round((13 * _m.cos(t) - 5 * _m.cos(2 * t) - 2 * _m.cos(3 * t) - _m.cos(4 * t)) * k, 4)])
    return pts[::-1]
def _emb(id_, mat, outline, y, kind, thick=0.035, roll=0):
    return {"id": id_, "type": "plate", "material": mat, "thick": thick, "outline": outline, "at": [0, y, 0.6, 90, 0, roll], "when": {"kind": kind}}
_S = 1.3
PROPS["components/trade-sign"] = item("Trade sign", "components", "a hanging trade sign: a wrought-iron bracket out from the wall, two short chains, the trade's emblem (`kind`: smithy, bakery, pottery, weaver, tailor, carpenter, cooper, butcher, tavern) -- origin on the wall face, the bracket along +z",
    {"kind": "smithy"}, {"iron": "iron", "gold": "gilt", "clay": "terracotta", "wood": "oak", "cloth": "velvet-red", "bush": "#4f6b2c"}, [
        rod("arm", "iron", 0.018, [0, 0, 0], [0, 0, 1.0], 6), rod("stay", "iron", 0.014, [0, -0.55, 0], [0, 0, 0.7], 6),
        rod("scroll", "iron", 0.01, [0, -0.25, 0.05], [0, -0.08, 0.4], 6),
        rod("chain", "iron", 0.006, [0, 0, 0.42], [0, -0.13, 0.42], 4), rod("chain 2", "iron", 0.006, [0, 0, 0.78], [0, -0.13, 0.78], 4),
        _emb("anvil", "iron", [[round(x * _S, 3), round(y * _S, 3)] for x, y in [(-0.25, 0), (0.2, 0), (0.38, -0.02), (0.2, -0.08), (0.08, -0.08), (0.08, -0.2), (0.18, -0.2), (0.18, -0.28), (-0.2, -0.28), (-0.2, -0.2), (-0.1, -0.2), (-0.1, -0.08), (-0.25, -0.08)]], -0.13, "smithy", 0.06),
        _emb("pretzel", "gold", _heart(), -0.33, "bakery", 0.05),
        _emb("jug", "clay", [[round(x * _S, 3), round(y * _S, 3)] for x, y in [(-0.07, 0), (0.07, 0), (0.06, -0.06), (0.14, -0.18), (0.15, -0.3), (0.11, -0.42), (-0.11, -0.42), (-0.15, -0.3), (-0.14, -0.18), (-0.06, -0.06)]], -0.13, "pottery", 0.08),
        _emb("shuttle", "wood", [[-0.34, -0.09], [-0.2, 0], [0.2, 0], [0.34, -0.09], [0.2, -0.18], [-0.2, -0.18]], -0.15, "weaver", 0.06),
        _emb("shuttle yarn", "cloth", [[-0.1, -0.05], [0.1, -0.05], [0.1, -0.13], [-0.1, -0.13]], -0.15, "weaver", 0.08),
        _emb("blade", "iron", [[-0.03, 0], [0.03, 0], [0.025, -0.4], [0, -0.48], [-0.025, -0.4]], -0.15, "tailor", 0.025, 22),
        _emb("blade 2", "iron", [[-0.03, 0], [0.03, 0], [0.025, -0.4], [0, -0.48], [-0.025, -0.4]], -0.15, "tailor", 0.025, -22),
        _emb("saw blade", "iron", [[-0.38, -0.02], [0.24, -0.02]] + [[round(0.24 - k * 0.062 - d, 3), -0.15 - (0.025 if d else 0)] for k in range(10) for d in (0, 0.031)] + [[-0.38, -0.1]], -0.13, "carpenter", 0.02),
        _emb("saw handle", "wood", [[0.22, 0.02], [0.38, 0.02], [0.4, -0.18], [0.22, -0.16]], -0.13, "carpenter", 0.05),
        {"id": "cask", "use": "items/furniture/cask", "scale": 0.42, "at": [0, -0.56, 0.6, 0, 0, 0], "when": {"kind": "cooper"}},
        {"id": "ham", "use": "items/food/ham", "scale": 1.7, "at": [0, -0.62, 0.6, 90, 0, 0], "when": {"kind": "butcher"}},
        {"id": "bush", "type": "sphere", "material": "bush", "r": 0.22, "sides": 7, "at": [0, -0.3, 0.6], "when": {"kind": "tavern"}},
        {"id": "tankard", "use": "items/tableware/mug", "scale": 2.2, "at": [0, -0.82, 0.6, 90, 0, 0], "when": {"kind": "tavern"}}],
    era="1100-1800", region="Europe")


# ---- MILLWORK (2026-10-03): the gears, shafts and stones of the water mill and the windmill, each turned by the game
# about its own axis at a `spin` marker (architecture.js lifeOf) in step with the wheel or the sails
MW_ = {"oak": "oak-grey", "dark": DARK}
PROPS["components/face-gear"] = item("Face gear", "components", "a mill's big wooden gear with its cogs on one face -- the pit wheel, the brake wheel: in the x-y plane, its axle along z, the cogs pointing -z (into the pinion they drive)",
    {"r": 1.3, "w": 0.2, "n": 32}, MW_, [
        rod("hub", "dark", 0.2, [0, 0, "0 - w"], [0, 0, "w"], 10),
        box("felloes", "oak", ["2 * (r - 0.1) * 0.2611 + 0.03", 0.2, "w"], [0, 0, 0], around={"n": 12, "r": "r - 0.1", "plane": "xy", "start": 15}),
        box("arms", "oak", ["2 * r - 0.3", 0.14, 0.12], [[0, 0, 0], [0, 0, 0, 0, 0, 90]]),
        box("cogs", "dark", [0.08, 0.1, 0.2], [0, 0, "0 - w / 2 - 0.1"], around={"n": "n", "r": "r - 0.1", "plane": "xy"})])
PROPS["components/lantern-pinion"] = item("Lantern pinion", "components", "a lantern pinion -- the wallower, the stone nut: two discs and the staves between them, its axis vertical (y), its foot at the origin",
    {"r": 0.36, "h": 0.4, "n": 8}, MW_, [
        {"id": "discs", "type": "lathe", "material": "oak", "sides": 12, "profile": [["r", 0], ["r", 0.06]], "at": [[0, 0, 0], [0, "h - 0.06", 0]]},
        box("staves", "dark", [0.05, "h - 0.12", 0.05], [0, "h / 2", 0], around={"n": "n", "r": "r - 0.05", "plane": "xz"})])
PROPS["components/millstone"] = item("Millstone", "components", "a millstone: a ring of stone round its eye, lying flat, its foot at the origin (a bedstone or a runner)",
    {"r": 0.65, "h": 0.22, "eye": 0.12}, {"stone": "stone"}, [
        {"id": "stone", "type": "lathe", "material": "stone", "sides": 16, "caps": False, "profile": [["eye", 0], ["r", 0], ["r", "h"], ["eye", "h"], ["eye", 0]]}])
PROPS["components/tun"] = item("Tun", "components", "the wooden case round a pair of millstones, open at the top; its spout at -x where the meal comes out",
    {"r": 0.8, "h": 0.55}, MW_, [
        {"id": "case", "type": "lathe", "material": "oak", "sides": 16, "caps": False, "double": True, "profile": [["r", 0], ["r", "h"]]},
        box("spout", "oak", [0.3, 0.12, 0.2], ["0 - r - 0.12", 0.12, 0])])
PROPS["components/hopper-horse"] = item("Hopper and horse", "components", "the hopper on its horse (the frame standing on the tun), the shoe under it sloping down toward -x into the stones' eye",
    {}, MW_, [
        box("horse legs", "oak", [0.06, 0.4, 0.06], [[0.32, 0.2, 0.32], [-0.32, 0.2, 0.32], [0.32, 0.2, -0.32], [-0.32, 0.2, -0.32]]),
        box("horse rails", "oak", [0.7, 0.05, 0.05], [[0, 0.4, 0.32], [0, 0.4, -0.32]]),
        {"id": "hopper", "type": "lathe", "material": "oak", "sides": 4, "caps": False, "double": True, "profile": [[0.12, 0.38], [0.48, 1.0]], "at": [0, 0, 0, 45, 0, 0]},
        box("shoe", "oak", [0.55, 0.04, 0.16], [-0.3, 0.3, 0, 0, 0, 12])])
PROPS["components/mill-shaft"] = item("Mill shaft", "components", "a mill's shaft: an oak spindle L long and r thick, up along y from its origin (`along` y) or back along -z (`along` z: a windshaft)",
    {"L": 4.0, "r": 0.1, "along": "y"}, MW_, [
        rod("shaft", "oak", "r", [0, 0, 0], [0, "L", 0], 8, when={"along": "y"}),
        rod("shaft z", "oak", "r", [0, 0, 0], [0, 0, "0 - L"], 8, when={"along": "z"}),
        rod("iron", "dark", "r * 1.25", [0, 0, 0], [0, 0.12, 0], 8, when={"along": "y"})])


# ---- the chopping block and the woodpile: a stump with a round of log stood on it to split, the split billets stacked
# beside it at +x (index.html CHORES: wood chopping before winter); its origin at the block's foot
PROPS["furniture/woodpile"] = item("Chopping block and woodpile", "furniture", "a chopping block -- a stump with a round of log stood on it for the axe -- and the split billets stacked beside it at +x, a few lying where they fell",
    {}, {"stump": "#7a5a3a", "bark": "#6b4f35", "split": "#b08a5a"}, [
        rod("stump", "stump", 0.24, [0, 0, 0], [0, 0.45, 0], 10),
        rod("round", "bark", 0.11, [0, 0.45, 0], [0, 0.8, 0], 8),
        *[rod(f"pile {c} {j}", "bark" if (j + c) % 3 else "split", 0.085, [round(0.75 + j * 0.18 + (c % 2) * 0.09, 3), round(0.085 + c * 0.16, 3), -0.22], [round(0.75 + j * 0.18 + (c % 2) * 0.09, 3), round(0.085 + c * 0.16, 3), 0.22], 6)
          for c in range(4) for j in range(6 - c)],
        rod("fallen 1", "split", 0.07, [-0.45, 0.07, 0.15], [-0.62, 0.07, 0.5], 6),
        rod("fallen 2", "split", 0.07, [0.25, 0.07, -0.45], [0.55, 0.07, -0.6], 6)])

# ---- a fishing hole in the ice: dark water in a round cut, slush and broken ice about it; origin on the ice
PROPS["components/ice-hole"] = item("Ice hole", "components", "a hole cut in the ice to fish through: the dark water in it, the slush and the broken pieces round it -- lying on the ice at the origin",
    {}, {"water": "#1d2a30", "slush": "#e2eaee", "chunk": "#cfdde3"}, [
        rod("slush", "slush", 0.36, [0, 0, 0], [0, 0.008, 0], 14),
        rod("water", "water", 0.2, [0, 0, 0], [0, 0.014, 0], 12),
        box("chunks", "chunk", [0.12, 0.04, 0.09], [[0.42, 0.02, 0.1], [-0.3, 0.02, 0.33], [0.05, 0.02, -0.45], [-0.4, 0.02, -0.2]])])


def main():
    for k, v in PROPS.items(): write(k, v)
    ipath = os.path.join(ROOT, "assets", "index.json")
    index = json.load(open(ipath))
    cats = {c["name"]: c for c in index["categories"]}
    where = {"tools": "Items: tools", "components": "Items: components", "ships": "Items: ships", "weapons": "Items: weapons",
             "furniture": "Items: furniture", "food": "Items: food", "tableware": "Items: tools"}
    for k in PROPS:
        c = cats[where[k.split("/")[0]]]["paths"]
        if "items/" + k not in c: c.append("items/" + k)
    json.dump(index, open(ipath, "w"), indent=1, ensure_ascii=False)
    print(len(PROPS), "props")


if __name__ == "__main__":
    main()
