"""THE SEA'S MODERN SHIPPING (2026-11-20; docs/modern.md): the ISO freight container (20 ft and 40 ft) and the
container ship that carries them -- in the vehicle frame (kit.py: the origin under the item's middle, +x the bow,
y up from the keel, +z starboard). The ship's hull is the ships' own `hull` primitive (docs/items.md Ships), lofted from
its lines; its deck cargo is hundreds of copies of ONE container component (`use`), each a plain block where it stands
inside a stack and ribbed where it shows on the outside -- so the ship stays a few tens of thousands of triangles.

Components written here (group "components", shared): `container` (a box of any ISO length: corrugated sides, the
frame, the doors at -x and their locking bars) and `stockless-anchor` (a modern ship's Hall anchor)."""
import math, random
from kit import item, hinge, box, rod, lathe, loft, sphere, ring, sweep, plate, use, write, across, arc, hole, runs, spaced, panes

C = "modern/components/"

# ---- THE ISO CONTAINER ------------------------------------------------------------------------------------------------
# (ISO 668: 8 ft wide (2.438 m), 8 ft 6 in high (2.591 m); a "20 ft" box is 6.058 m long, a "40 ft" 12.192 m. Its side
# walls are corrugated steel, trapezoidal ribs ~ 0.28 m apart; its four corner posts and the top and bottom rails
# carry the stack's weight; the doors are at one end, two leaves, each shut by two vertical locking bars with cam handles.)
FT20, FT40, CW, CH = 6.058, 12.192, 2.438, 2.591


def container():
    # THE CONTAINER COMPONENT: its floor at y 0, its middle at x 0, its length along x, the DOOR END at -x. `ribs` the
    # corrugations along each side (0: a plain block -- a box hidden inside a stack); `both` 0 ribs on the +z side only
    # (an outer row's box, its ribs where they are seen); `full` 1 the frame, the doors, the end wall's ribs (the item
    # on its own; 0 inside a ship's stack, where nobody sees them). The roles are named `cbox`, `cframe`, `cbar` so a
    # parent's own roles never repaint it by accident.
    return item("Shipping container", "components",
        "an ISO freight container, L long (6.058 m a 20 ft, 12.192 m a 40 ft), 2.438 m wide, 2.591 m high: the corrugated walls, the corner posts and rails, two door leaves at -x with their locking bars, hinged just outside the corner posts and swung 265 degrees round flat against the sides by `open`, onto the hollow inside (its plank floor; a light load of pallets, a crate and drums unless `load` 0) -- or a plain block (full 0, ribs 0) for a stack's inner boxes",
        {"cbox": "paint-red", "cframe": "cbox", "cbar": "steel", "cfloor": "planks", "cwood": "#9a7a52", "ccarton": "#b08a5c", "cdrum": "#2f5e8c"}, [
            # (a plain block in a stack (full 0); the item on its own (full 1) a hollow box -- floor, roof, sides and the
            #  blind end as plates -- its doors opening onto the inside)
            box("block", "cbox", ["L - 0.02", "H - 0.02", "W - 0.04"], [0, "H / 2", 0], when={"full": [0]}),
            box("floor", "cfloor", ["L - 0.04", 0.03, "W - 0.06"], [0, 0.12, 0], when="full"),
            box("roof", "cbox", ["L - 0.02", 0.03, "W - 0.04"], [0, "H - 0.025", 0], when="full"),
            box("side", "cbox", ["L - 0.02", "H - 0.02", 0.03], [0, "H / 2", "W / 2 - 0.035"], mirror="z", when="full"),
            box("blind", "cbox", [0.03, "H - 0.02", "W - 0.04"], ["L / 2 - 0.025", "H / 2", 0], when="full"),
            box("under", "cframe", ["L - 0.04", 0.1, "W - 0.06"], [0, 0.055, 0], when="full"),
            # (the corrugation: one thin rib after another down each side, standing proud of the wall)
            box("ribR", "cbox", ["L / ribs * 0.42", "H - 0.3", 0.05], [0, "H / 2", "W / 2 - 0.032"], along={"n": "ribs", "from": ["-L / 2 + 0.3", 0, 0], "to": ["L / 2 - 0.3", 0, 0]}, when="ribs"),
            box("ribL", "cbox", ["L / ribs * 0.42", "H - 0.3", 0.05], [0, "H / 2", "-W / 2 + 0.032"], along={"n": "ribs", "from": ["-L / 2 + 0.3", 0, 0], "to": ["L / 2 - 0.3", 0, 0]}, when=["ribs", "both"]),
            box("roofRib", "cbox", ["L / ribs * 0.3", 0.03, "W - 0.3"], [0, "H - 0.01", 0], along={"n": "ribs / 2", "from": ["-L / 2 + 0.4", 0, 0], "to": ["L / 2 - 0.4", 0, 0]}, when=["ribs", "full"]),
            # (the frame: four corner posts, the top and bottom side rails, the end rails)
            box("post", "cframe", [0.16, "H", 0.16], [["L / 2 - 0.08", "H / 2", "W / 2 - 0.08"], ["-L / 2 + 0.08", "H / 2", "W / 2 - 0.08"]], mirror="z", when="full"),
            box("rail", "cframe", ["L - 0.1", 0.12, 0.06], [[0, "H - 0.06", "W / 2 - 0.03"], [0, 0.08, "W / 2 - 0.03"]], mirror="z", when="full"),
            box("endRail", "cframe", [0.07, 0.14, "W - 0.1"], [["L / 2 - 0.035", "H - 0.07", 0], ["L / 2 - 0.035", 0.09, 0], ["-L / 2 + 0.035", "H - 0.1", 0], ["-L / 2 + 0.035", 0.11, 0]], when="full"),
            box("casting", "cbar", [0.18, 0.12, 0.17], [["L / 2 - 0.09", "H - 0.06", "W / 2 - 0.085"], ["L / 2 - 0.09", 0.06, "W / 2 - 0.085"], ["-L / 2 + 0.09", "H - 0.06", "W / 2 - 0.085"], ["-L / 2 + 0.09", 0.06, "W / 2 - 0.085"]], mirror="z", when="full"),
            # (the blind end at +x: its own vertical ribs)
            box("endRib", "cbox", [0.05, "H - 0.35", 0.12], ["L / 2 - 0.005", "H / 2", 0], along={"n": 7, "from": [0, 0, "-W / 2 + 0.4"], "to": [0, 0, "W / 2 - 0.4"]}, when="full"),
            # (the doors at -x: two leaves, a seam between, each with two locking bars, their cam handles and hinges --
            #  each leaf hinged at its outer edge, just outside the corner post, and swung 265 degrees by `open` round
            #  flat against its side)
            hinge("door", ["-L / 2 - 0.03", "H / 2", "W / 2 + 0.035"], [
                box("leaf", "cbox", [0.04, "H - 0.26", "W / 2 - 0.137"], ["-L / 2 - 0.004", "H / 2", "W / 4 - 0.0615"]),
                box("rib", "cbox", [0.03, 0.06, "W / 2 - 0.2"], ["-L / 2 - 0.03", 0, "W / 4 - 0.02"], along={"n": 5, "from": [0, 0.45, 0], "to": [0, "H - 0.45", 0]}),
                rod("bar", "cbar", 0.016, ["-L / 2 - 0.05", 0.14, 0], ["-L / 2 - 0.05", "H - 0.14", 0], 6, at=[[0, 0, 0.2], [0, 0, 0.88]]),
                box("handle", "cbar", [0.03, 0.04, 0.28], [["-L / 2 - 0.075", 1.05, 0.32], ["-L / 2 - 0.075", 1.05, 1.0]]),
                box("hinge", "cbar", [0.06, 0.1, 0.06], ["-L / 2 - 0.02", 0, "W / 2 - 0.13"], along={"n": 4, "from": [0, 0.35, 0], "to": [0, "H - 0.35", 0]}),
                box("inner", "cbox", [0.02, "H - 0.3", "W / 2 - 0.17"], ["-L / 2 + 0.026", "H / 2", "W / 4 - 0.02"], inside=True),
            ], max_=265, mirror="z", when="full"),
            # (the load, seen only open and light: two rows of pallets of cartons lashed at the blind end, a crate, a
            #  drum or two by the doors; `load` 0 leaves it empty)
            box("pallet", "cwood", [1.2, 0.14, 1.0], [["L / 2 - 0.75", 0.205, z] for z in (-0.55, 0.55)] + [["L / 2 - 2.0", 0.205, -0.55]], inside=True, when=["full", "load"]),
            box("cartons", "ccarton", [1.16, 1.1, 0.96], [["L / 2 - 0.75", 0.825, z] for z in (-0.55, 0.55)] + [["L / 2 - 2.0", 0.825, -0.55]], inside=True, when=["full", "load"]),
            box("cartonsTop", "ccarton", [1.1, 0.5, 0.9], [["L / 2 - 0.75", 1.63, -0.55]], inside=True, when=["full", "load"]),
            box("strap", "cbar", [0.02, 1.14, 1.0], [["L / 2 - 0.75", 0.825, z] for z in (-0.55, 0.55)], inside=True, when=["full", "load"]),
            box("crate", "cwood", [1.0, 0.8, 0.8], ["L / 2 - 2.0", 0.535, 0.6, 8, 0, 0], inside=True, when=["full", "load"]),
            lathe("drum", "cdrum", [[0, 0], [0.29, 0], [0.29, 0.88], [0, 0.88]], [["-L / 2 + 0.9", 0.135, -0.7], ["-L / 2 + 1.5", 0.135, -0.75]], sides=14, inside=True, when=["full", "load"]),
        ], params={"L": FT40, "W": CW, "H": CH, "ribs": 44, "both": 1, "full": 1, "load": 1}, era="1956-2030")


BOXES = {"maersk": "#5d9ccb", "msc": "#d8c9a8", "cma": "#22427e", "evergreen": "#3b7148", "hapag": "#d0642b",
         "cosco": "#4a6f95", "one": "#b8366f", "red": "#a8342e", "grey": "#8c9196", "white": "#d9d9d4",
         "brown": "#73492f", "yellow": "#d9b13a", "teal": "#2f8487"}


def container_item(L, name, title):
    return item(title, "freight",
        f"an ISO {name} freight container: {L} m long, 2.438 m wide, 2.591 m high (8 ft 6 in) -- corrugated steel walls, corner posts and castings, the doors at -x with their four locking bars (`open` swings them round against the sides onto the inside: a plank floor, a light load or, `load` 0, none); its colour the line's that owns it, drawn by the seed",
        {"box": {"pick": list(BOXES.values())}}, [
            use("box", C + "container", [0, 0, 0], {"L": L, "ribs": round(L / 0.276), "load": "load"}, {"cbox": "box", "cframe": "box", "cbar": "steel"}),
        ], params={"open": 0, "load": {"pick": [1, 1, 0]}}, era="1956-2030")


def stockless_anchor():
    # A STOCKLESS ANCHOR (a Hall anchor, every merchant ship's since ~1890): hung by its shackle at the origin, the
    # shank down -y, the crown across x at its foot and the two flukes turned up beside the shank -- in the xy plane,
    # so it lies flat against a hull's side. `h` its height.
    return item("Stockless anchor", "components", "a stockless (Hall) anchor h tall, hung by its shackle at the origin: the shank, the crown, two broad flukes turned up beside the shank, all in the xy plane",
        {"metal": "paint-black"}, [
            ring("shackle", "metal", "h * 0.05", "h * 0.012", [0, "-h * 0.05", 0, 0, 0, 90]),
            box("shank", "metal", ["h * 0.09", "h * 0.78", "h * 0.07"], [0, "-h * 0.48", 0]),
            box("crown", "metal", ["h * 0.38", "h * 0.13", "h * 0.17"], [0, "-h * 0.9", 0]),
            plate("fluke", "metal", [["h * 0.08", "-h * 0.84"], ["h * 0.2", "-h * 0.97"], ["h * 0.29", "-h * 0.62"], ["h * 0.27", "-h * 0.47"], ["h * 0.17", "-h * 0.56"], ["h * 0.08", "-h * 0.74"]], "h * 0.08", [0, 0, 0], mirror="x"),
            box("palm", "metal", ["h * 0.06", "h * 0.2", "h * 0.13"], ["h * 0.13", "-h * 0.86", 0, 0, 0, 30], mirror="x"),
        ], params={"h": 3.6}, era="1890-2030")


# ---- THE CONTAINER SHIP -----------------------------------------------------------------------------------------------
# (the hull's lines, the same numbers the `hull` primitive reads -- here so the deck cargo, the anchors and the house
# can be fitted to the half-breadth the primitive will draw)
def line_at(line, t):
    if isinstance(line, (int, float)): return line
    for k in range(1, len(line)):
        if t <= line[k][0] + 1e-9:
            f = (t - line[k - 1][0]) / max(1e-9, line[k][0] - line[k - 1][0])
            return line[k - 1][1] + (line[k][1] - line[k - 1][1]) * max(0, min(1, f))
    return line[-1][1]


def hull_half(lines, B, t, y):
    """(the hull primitive's half-breadth at station t, height y: its quarter superellipse, solved by bisection)"""
    ky, sy, hb = line_at(lines["keel"], t), line_at(lines["sheer"], t), B / 2 * line_at(lines["plan"], t)
    if y <= ky: return 0.0
    if y >= sy: return hb
    n = 1 + 4 * max(0, min(1, line_at(lines["fullness"], t)))
    lo, hi = 0.0, math.pi / 2   # (phi: 0 at the gunwale, pi/2 at the keel)
    for _ in range(40):
        ph = (lo + hi) / 2
        yy = ky + (sy - ky) * (1 - math.sin(ph) ** (2 / n))
        if yy > y: lo = ph
        else: hi = ph
    return hb * math.cos((lo + hi) / 2) ** (2 / n)


def container_ship():
    # A PANAMAX-SIZED CONTAINER SHIP (~4,000 TEU, built ~1995-2010): 220 m over all, 32.2 m beam (the old Panama locks'
    # limit), 19 m moulded depth, ~12 m draught. The house aft with the bridge on top, its wings spanning the beam; the
    # funnel behind it; twelve 40 ft bays forward of it on hatch covers, 3 to 6 tiers high, between lashing bridges;
    # the forecastle with the windlass, the anchors in their hawse pockets, a bulbous bow, the rudder and the screw.
    L, B, D, WL = 220.0, 32.2, 19.0, 12.0
    X0 = -L / 2   # (the stern; the hull primitive's x 0)
    lines = {
        "plan": [[0, .72], [.04, .86], [.1, .97], [.18, 1], [.68, 1], [.8, .9], [.9, .62], [.96, .3], [1, 0]],
        "fullness": [[0, .55], [.12, .9], [.7, .95], [.85, .7], [.95, .35], [1, .25]],
        "keel": [[0, 4.5], [.06, .6], [.1, 0], [.96, 0], [1, 1.5]],
        "sheer": [[0, D], [.88, D], [.9, D + 2.6], [1, D + 3.2]],
    }
    T = lambda x: (x - X0) / L   # (an x in the item's frame -> the hull's t)
    parts = [
        # (the hull: dark topsides; the red antifouling below the load waterline is a second hull of the same lines, a
        #  hair longer, whose sheer IS the waterline -- its sides lie just outside the first's all the way down)
        {"id": "hull", "type": "hull", "material": "hull", "length": L, "beam": B, "depth": D, **lines,
         "stations": 44, "sides": 8, "deck": [{"y": D, "from": 0, "to": 1, "material": "deck", "under": False}, {"y": D + 2.55, "from": .895, "to": 1, "material": "deck", "under": False}],
         "rail": 0.12, "railMaterial": "white", "at": [X0, 0, 0]},
        {"id": "bottom", "type": "hull", "material": "bottom", "length": L + 0.12, "beam": B * 1.002, "depth": WL,
         "plan": lines["plan"], "fullness": lines["fullness"], "keel": lines["keel"], "sheer": [[0, WL], [1, WL]],
         "stations": 44, "sides": 7, "at": [X0 - 0.06, 0, 0]},
        # (the bulbous bow: a rounded loft standing out ahead of the stem under the waterline)
        loft("bulb", "bottom", [[L / 2 - 12, 2.2, 1.0, 9.0], [L / 2 - 5, 2.6, 1.6, 8.8], [L / 2 + 1.5, 2.2, 2.6, 8.0], [L / 2 + 4.2, 0.7, 4.5, 6.4]], 2.0, seg=3, corner=4),
        # (the forecastle's front bulkhead, and the breakwater on it -- a V of plate to shed green seas off the boxes)
        box("fcBulk", "white", [0.4, 2.6, 2 * hull_half(lines, B, T(L * .39), D) - 0.6], [L * .39, D + 1.3, 0]),
        box("breakwater", "white", [0.3, 2.2, 9.0], [L * .405, D + 3.6, 6.6, 28, 0, 0], mirror="z"),
        box("bwStay", "white", [1.6, 0.2, 0.2], [L * .405 + 0.7, D + 3.4, 0], along={"n": 6, "from": [0, 0, -9], "to": [0, 0, 9]}),
    ]
    # ---- THE DECK CARGO: bays of 40 ft boxes forward of the house, each on its hatch cover, the stacks' heights drawn
    # (lower toward the bow: the bridge must see the water 500 m ahead), every colour one `use` part with its places
    rng = random.Random(7)
    pitch, bay0 = 13.2, -71.4
    lots = {}   # (colour, outer?) -> [at]
    small = {}  # (colour) -> [at]   (two 20 ft boxes in a 40 ft slot, now and then)
    names = list(BOXES)
    weights = [9, 7, 6, 6, 5, 5, 4, 3, 4, 2, 3, 2, 2]
    hatch = {k: [] for k in ("coaming", "cover", "lash", "lashRail", "lashPost")}   # (bay by bay: `each` runs where the beam holds)
    for i in range(12):
        x = bay0 + i * pitch
        hb = min(hull_half(lines, B, T(x + 6.1), D), hull_half(lines, B, T(x - 6.1), D))
        rows = max(4, min(12, int((2 * hb - 1.6) / 2.5)))
        width = rows * 2.5 + 0.4
        # (the hatch: its coaming on the deck, the cover on it -- the boxes' floor at D + 2)
        hatch["coaming"].append(box(f"coaming{i}", "deck2", [12.6, 1.4, width - 0.2], [x, D + 0.7, 0]))
        hatch["cover"].append(box(f"cover{i}", "cover", [12.9, 0.6, width + 0.3], [x, D + 1.7, 0]))
        # (a lashing bridge between this bay and the next aft: a gangway two tiers up and its posts)
        if i > 0:
            xb = x - pitch / 2
            hatch["lash"].append(box(f"lash{i}", "white", [0.9, 0.18, width + 0.2], [xb, D + 2 + 2 * CH, 0]))
            hatch["lashRail"].append(box(f"lashRail{i}", "white", [0.06, 0.06, width + 0.2], [xb + 0.4, D + 3 + 2 * CH, 0]))
            hatch["lashPost"].append(box(f"lashPost{i}", "white", [0.3, 2 * CH + 2, 0.3], [xb, D + 1 + CH, 0], along={"n": 5, "from": [0, 0, -width / 2], "to": [0, 0, width / 2]}))
        top = 6 if i > 1 else (4 if i == 1 else 3)
        for j in range(rows):
            z = (j - (rows - 1) / 2) * 2.5
            edge = j in (0, rows - 1)
            n = rng.choice([top, top, top - 1, top - 2, top]) - (1 if edge and rng.random() < .4 else 0)
            n = max(1, n)
            for k in range(n):
                col = rng.choices(names, weights)[0]
                y = D + 2.0 + k * (CH + 0.01)
                if k == n - 1 and rng.random() < .12:   # (two 20 ft boxes on top)
                    small.setdefault(col, []).append([x - 3.05, y, z, 0 if z >= 0 else 180, 0, 0])
                    small.setdefault(rng.choices(names, weights)[0], []).append([x + 3.05, y, z, 0 if z >= 0 else 180, 0, 0])
                    continue
                # (the outer rows' boxes turned so their ribbed side faces outboard)
                lots.setdefault((col, edge), []).append([x, y, z, 0 if z >= 0 else 180, 0, 0])
    for k, run in hatch.items(): parts += runs(k, run)
    for (col, edge), ats in sorted(lots.items()):
        parts.append(use(f"box-{col}-{'out' if edge else 'in'}", C + "container", ats, {"L": FT40, "ribs": 12 if edge else 0, "both": 0, "full": 0}, {"cbox": BOXES[col], "cframe": BOXES[col], "cbar": "steel"}))
    for col, ats in sorted(small.items()):
        parts.append(use(f"box20-{col}", C + "container", ats, {"L": FT20, "ribs": 6, "both": 1, "full": 0}, {"cbox": BOXES[col], "cframe": BOXES[col], "cbar": "steel"}))
    # ---- THE HOUSE: six decks of cabins, the bridge on top with its wings, the funnel behind
    hx0, hx1, hw = -93.0, -80.0, 11.5
    hy = D + 6 * 2.8   # (the bridge deck's floor)
    hm = (hx0 + hx1) / 2
    decks = [D + 2.8 * k + 1.6 for k in range(1, 6)]   # (the windows' middles, a deck each)
    parts += [
        box("house", "white", [hx1 - hx0, hy - D, 2 * hw], [hm, (D + hy) / 2, 0]),
        box("houseBase", "white", [hx1 - hx0 + 6, 2.6, 2 * hull_half(lines, B, T(hm), D) - 1.2], [hm - 3, D + 1.3, 0]),
        # (each deck's windows: rows across the front and down both sides)
        *panes("winF", "glass", "x", hx1 + 0.01, spaced(-hw + 1.2, hw - 1.2, 11, 1.3, ends=True), [(y - 0.55, y + 0.55) for y in decks], t=0.06),
        *panes("winS", "glass", "z", hw + 0.01, spaced(hx0 + 1.5, hx1 - 1.5, 6, 1.2, ends=True), [(y - 0.5, y + 0.5) for y in decks], t=0.06, mirror="z"),
        box("deckLine", "white2", [hx1 - hx0 + 0.3, 0.25, 2 * hw + 0.3], [hm, 0, 0], along={"n": 6, "from": [0, D + 2.8, 0], "to": [0, hy, 0]}),
        # (the bridge: the wheelhouse across the house's width, its windows a band leaning out, the wings to the ship's
        #  sides on their brackets, the roof overhanging and the mast on it)
        box("bridge", "white", [hx1 - hx0 - 1.0, 3.2, 2 * hw], [hm - 0.5, hy + 1.6, 0]),
        box("bridgeGlass", "glass", [0.12, 1.5, 2 * hw - 0.6], [hx1 - 0.92, hy + 1.9, 0, 0, 0, -10]),
        box("wing", "white", [4.2, 0.35, B / 2 - hw + 0.3], [hx1 - 3.2, hy, hw + (B / 2 - hw) / 2], mirror="z"),
        box("wingRail", "white", [4.2, 1.2, 0.12], [hx1 - 3.2, hy + 0.75, B / 2 + 0.1], mirror="z"),
        box("wingFront", "white", [0.12, 1.2, B / 2 - hw], [hx1 - 1.15, hy + 0.75, hw + (B / 2 - hw) / 2], mirror="z"),
        box("wingCab", "white", [3.2, 2.6, 1.6], [hx1 - 3.0, hy + 1.5, B / 2 - 0.8], mirror="z"),
        box("wingCabGlass", "glass", [0.08, 1.2, 1.4], [hx1 - 1.38, hy + 1.9, B / 2 - 0.8], mirror="z"),
        box("wingCabSide", "glass", [2.6, 1.2, 0.08], [hx1 - 3.0, hy + 1.9, B / 2 + 0.01], mirror="z"),
        box("wingBracket", "white", [0.3, 2.4, 0.3], [hx1 - 3.0, hy - 1.2, hw + 1.5], mirror="z"),
        *panes("bridgeSide", "glass", "z", hw + 0.01, spaced(hx0 + 1.5, hx1 - 3.0, 4, 1.4, ends=True), (hy + 1.3, hy + 2.5), t=0.06, mirror="z"),
        box("bridgeRoof", "white", [hx1 - hx0 + 0.4, 0.3, 2 * hw + 0.8], [hm - 0.3, hy + 3.35, 0]),
        rod("mast", "white", 0.35, [hm - 2, hy + 3.5, 0], [hm - 2, hy + 10.5, 0], 8),
        box("yard", "white", [0.4, 0.4, 7.0], [hm - 2, hy + 8.2, 0]),
        box("radar", "dark", [0.5, 0.25, 6.0], [hm + 0.5, hy + 4.4, 0, 30, 0, 0]),
        box("radar2", "dark", [0.4, 0.2, 4.0], [hm - 4.5, hy + 5.6, 0, -40, 0, 0]),
        rod("radarPost", "white", 0.25, [hm + 0.5, hy + 3.5, 0], [hm + 0.5, hy + 4.3, 0], 6),
        rod("radarPost2", "white", 0.2, [hm - 4.5, hy + 3.5, 0], [hm - 4.5, hy + 5.5, 0], 6),
        sphere("mastLight", "lamp", 0.3, [hm - 2, hy + 10.7, 0], sides=8),
        # (the funnel: a casing behind the house, the company's band and its black top, two exhaust pipes)
        loft("funnel", "white", [[-101.5, 3.4, D, hy + 6.5, 3.0], [-99.0, 3.8, D, hy + 7.0, 3.4], [-95.5, 3.8, D, hy + 7.0, 3.4], [-94.0, 3.2, D, hy + 6.8, 2.8]], 1.2, seg=2),
        box("funnelBand", "band", [6.4, 2.4, 7.0], [-97.6, hy + 3.4, 0]),
        box("funnelTop", "dark", [7.6, 0.8, 7.1], [-97.8, hy + 6.65, 0]),
        rod("exhaust", "dark", 0.7, [-98.5, hy + 6.5, 0], [-98.5, hy + 8.4, 0], 10, at=[[0, 0, 1.1], [0, 0, -1.1]]),
        # (the free-fall lifeboat on its ramp over the stern, orange, launched aft; the life-raft canisters)
        loft("lifeboat", "orange", [[-6.4, 0.2, 0.3, 1.1], [-5.5, 1.3, 0, 2.6, 1.0], [-1.0, 1.55, 0, 3.0, 1.2], [0, 1.0, 0.4, 2.4, 0.6]], [0.6, 0.8], seg=3, at=[-100.5, D + 8.5, 0, 0, 0, 32]),
        box("ramp", "white", [8.0, 0.4, 3.6], [-104.0, D + 6.4, 0, 0, 0, 32]),
        box("rampLeg", "white", [0.4, 7.0, 0.4], [[-103.0, D + 3.5, 1.6], [-103.0, D + 3.5, -1.6]]),
        rod("raft", "white2", 0.35, [-91.0, D + 2.9, hw + 0.6], [-89.4, D + 2.9, hw + 0.6], 10, along={"n": 3, "from": [0, 0, 0], "to": [6, 0, 0]}, mirror="z"),
    ]
    # ---- THE ENDS: the forecastle's windlass and bitts, the stern's mooring deck, the anchors in their pockets, the
    # rudder and the screw
    xa = L * .44   # (the hawse: where the anchor hangs)
    ya = D - 1.4
    za = hull_half(lines, B, T(xa), ya - 1.8) + 0.25
    za2 = hull_half(lines, B, T(xa + 1.5), ya - 1.8) + 0.25
    yaw = math.degrees(math.atan2(za - za2, 1.5))
    parts += [
        use("anchor", C + "stockless-anchor", [xa, ya, za, yaw, 0, 0], {"h": 3.8}, {"metal": "dark"}, mirror="z"),
        ring("hawse", "dark", 0.55, 0.14, [xa, ya + 0.1, za - 0.2, yaw, 0, 0], mirror="z"),
        lathe("windlass", "machine", [[0, -0.9], [0.9, -0.9], [0.9, 0.9], [0, 0.9]], [L * .43, D + 3.5, 2.8, 0, 90, 0], mirror="z", sides=14),
        box("windlassBed", "machine", [3.0, 0.8, 7.0], [L * .43, D + 2.95, 0]),
        rod("chain", "dark", 0.18, [L * .43 + 0.5, D + 2.6, 2.8], [xa - 0.5, D + 2.6, za - 1.4], 6, mirror="z"),
        rod("bitt", "machine", 0.35, [0, D + 2.5, 0], [0, D + 3.7, 0], 8, at=[[L * .42, 0, 5.0], [L * .42 - 1.2, 0, 5.0], [L * .46, 0, 3.0], [L * .46 - 1.2, 0, 3.0]], mirror="z"),
        rod("sternBitt", "machine", 0.35, [0, D, 0], [0, D + 1.2, 0], 8, at=[[-107, 0, 9.5], [-105.8, 0, 9.5], [-104, 0, 3.5], [-102.8, 0, 3.5]], mirror="z"),
        lathe("sternWinch", "machine", [[0, -0.8], [0.8, -0.8], [0.8, 0.8], [0, 0.8]], [-106.5, D + 1.2, 5.5, 0, 90, 0], mirror="z", sides=12),
        rod("foreMast", "white", 0.3, [L * .455, D + 2.6, 0], [L * .455, D + 13.0, 0], 8),
        sphere("foreLight", "lamp", 0.3, [L * .455, D + 13.2, 0], sides=8),
        box("rudder", "bottom", [6.5, 10.0, 0.9], [X0 + 2.2, 7.0, 0]),
        use("screw", C + "rotor", [X0 + 7.4, 4.6, 0, 0, 0, 90], {"n": 5, "R": 3.4, "c": 1.6, "t": 0.25, "pitch": 28, "hubR": 0.9, "hubH": 1.8}, {"blade": "bronze", "hub": "bronze"}),
        rod("shaft", "bronze", 0.5, [X0 + 7.4, 4.6, 0], [X0 + 11, 4.6, 0], 8),
    ]
    return item("Container ship", "ship",
        "a Panamax-sized container ship of ~4,000 TEU (built ~1995-2010): 220 m over all, 32.2 m beam, 19 m moulded depth, 12 m draught -- the hull lofted from its lines (dark topsides, red antifouling, a bulbous bow), the house aft with six decks of cabins, the bridge and its wings across the beam, the funnel, a free-fall lifeboat over the stern; twelve 40 ft bays forward on their hatch covers, 3 to 6 tiers, between lashing bridges; the forecastle, windlass, two stockless anchors in their hawse pockets, the rudder and the five-bladed screw",
        {"hull": {"pick": ["#1d2a3d", "#2a2a2c", "#23415e", "#3a3f45"]}, "bottom": "#8f2f28", "deck": "#5d6b54", "deck2": "#59614f",
         "cover": "#6f7563", "white": "#e3e2dc", "white2": "#c9c8c2", "glass": "glass", "dark": "#232426", "band": {"pick": ["#2b5ea8", "#c7382c", "#e0b030", "#2f7a52"]},
         "orange": "#e2671f", "machine": "#4f6a3e", "lamp": "lamp", "bronze": "brass"}, parts,
        markers=[{"role": "waterline", "at": [0, WL, 0], "data": {"draught": WL}}, {"role": "helm", "at": [hx1 - 2.5, hy, 0]},
                 {"role": "moor", "at": [L * .44, D + 2.6, 0], "data": {"end": "bow"}}, {"role": "moor", "at": [-105, D, 0], "data": {"end": "stern"}}],
        era="1995-2030")


def write_all():
    write("modern/components/container", container(), "components")
    write("modern/components/stockless-anchor", stockless_anchor(), "components")
    write("modern/sea/container", container_item(FT40, "40 ft", "Shipping container (40 ft)"), "sea")
    write("modern/sea/container-20", container_item(FT20, "20 ft", "Shipping container (20 ft)"), "sea")
    write("modern/sea/container-ship", container_ship(), "sea")

GROUPS = {"sea": "sea", "components": "components"}
