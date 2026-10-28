#!/usr/bin/env python3
"""THE RIVERSIDE (2026-10-02, were village.js fisherHut and architecture.js watermill, landing): the fisherman's hut with
its jetty, the water mill with its pit, stones and sacks, the landing with its deck, stage and stair -- as arch-engine
definitions (assets/architecture/village/fisher-hut, watermill, landing) and their finishes. Each keeps its OWN ORIGIN
(`site.origin`: the game sets it against the bank by its yard, `footW` x `footD`, not by the piles over the water), and
hands the game its life as markers: the boat's `dock`, the wheel's `rotor`, the sacks' `drop`, the quay's `slot`s, the
dock hands' `path`, the barge's `berth`, `cobweb`s, the miller's and the fisher's places.

    python3 tools/archgen/riverside.py
"""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PI, PI2 = 3.14159265, 1.5707963


def write(base, path, doc):
    full = os.path.join(ROOT, "assets", base, path + ".json")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(json.dumps(doc, indent=1) + "\n")


def at(*pts): return [list(p) if len(p) == 4 else [*p, 0] for p in pts]
def box(w, l, h, *pts, **k): return {"type": "box", "width": w, "length": l, "height": h, "at": at(*pts), **k}
def col(r, h, *pts, sides=8, **k): return {"type": "column", "radius": r, "height": h, "sides": sides, "at": at(*pts), **k}
def item(path, *pts, **k): return {"type": "item", "item": path, "at": at(*pts), **k}
def marker(role, *pts, **data): return {"type": "marker", "role": role, "at": at(*pts), "data": data}
def opening(x, w, sill, top): return {"at": x, "width": w, "sill": sill, "springing": top, "head": {"profile": "flat"}, "glass": False}   # (shuttered: the game hangs the shutters at the `window` markers)


# ---- THE FISHERMAN'S HUT: a 5 x 4 m boarded hut on the bank, a reed thatch, inside a table with the catch, a stool, a
# cot; outside the nets on the west wall and a drying rack of fish; the plank jetty on piles out into the river
W, D, H, T, F = 5, 4, 2.4, 0.3, 0.12
jx, jz0, jz1, jy = 1.2, -3.4, -9.0, 0.25
hut = {
    "floor": box(W, D, F, (0, 0, 0), walked=True),
    "walls": {"type": "enclosure", "plan": {"rect": [W, D]}, "thickness": T, "height": H, "openings": [], "at": [[0, 0, 0, 0]],
              "faces": {"0": [opening(0, 1.1, 0, 2.0), opening(1.6, 0.8, 1.1, 1.9)], "2": [opening(1.2, 0.8, 1.1, 1.9)]},   # (face 2 runs -x: x -1.2 is at 1.2)
              "interior": True},   # (the hut's room: an interior, up to the ceiling; the loft over it the thatch's)
    "ceiling": box(W - 2 * T, D - 2 * T, 0.12, (0, H, 0)),
    "roof": {"type": "roof", "form": "gable", "width": D + 0.8, "length": W + 0.8, "pitch": 38.4, "overhang": 0, "at": [[0, H + 0.12, 0, PI2]], "_about": "reed thatch"},
    "table legs": box(0.08, 0.08, 0.7, (-1.8, F, 0.58), (-0.8, F, 1.02)), "table": box(1.2, 0.6, 0.06, (-1.3, F + 0.69, 0.8)),
    "basket": item("items/tools/basket", (-1.3, F + 0.75, 0.8), solid=False),
    "catch": item("items/food/fish", (-1.38, F + 0.9, 0.8, 0.3), (-1.24, F + 0.92, 0.78, -0.4), solid=False),
    "stool": col(0.18, 0.45, (-0.3, F, 1.0), taper=0.89),
    "cot": box(1.9, 0.8, 0.35, (1.3, F + 0.125, -1.2)), "cot mattress": box(1.8, 0.7, 0.12, (1.3, F + 0.47, -1.2)),
    "nets": box(0.04, 1.6, 1.3, (-W / 2 - 0.04, 0.65, 0.2)), "nets 2": box(0.04, 1.0, 0.9, (-W / 2 - 0.08, 1.05, -1.0)),
    "rack posts": col(0.06, 1.9, (W / 2 + 1.0, 0, -1.2), (W / 2 + 1.0, 0, 1.2), sides=6),
    "rack bar": box(0.06, 2.6, 0.06, (W / 2 + 1.0, 1.82, 0)),
    "drying fish": item("items/components/fish-hanging", *[(W / 2 + 1.0, 1.56, -1.0 + k * 0.4) for k in range(6)], solid=False),
    "jetty piles": col(0.1, 4.6, *[(jx + s * 0.6, jy - 4.6, z) for z in (-4.6, -6.8, -8.8) for s in (-1, 1)], sides=6),
    "jetty": box(1.4, jz0 - jz1, 0.08, (jx, jy - 0.04, (jz0 + jz1) / 2), walked=True),
    "mooring post": col(0.1, 0.5, (jx + 0.6, jy, -8.6), sides=6, taper=0.8),
    "fisher": marker("spot", (jx - 0.2, jy + 0.04, jz1 + 0.7, PI2), pose="stand", work=1, gesture="fish", tool="rod"),
    "boat dock": marker("dock", (jx + 1.75, "water + 0.28", -7.2)),
    "cobweb": marker("cobweb", (-(W / 2 - T), H, -(D / 2 - T)), sx=1, sz=1, d=0.5),
    "door": marker("door", (0, 0, D / 2 - T / 2, 0), w=1.1, h=2.0),
    "windows": {"type": "marker", "role": "window", "at": [[1.6, 1.1, D / 2 - T / 2, 0], [-1.2, 1.1, -(D / 2 - T / 2), 0]], "data": {"w": 0.8, "h": 0.8}},
}
write("architecture", "village/fisher-hut", {"name": "Fisherman's hut", "_about": "THE FISHERMAN'S HUT: a 5 x 4 m boarded hut on the bank under reed thatch, inside a table with the catch in a basket, a stool, a cot; the nets hung on the west wall and a drying rack of fish to the east; the plank jetty on piles out over the bank line into the river, the fisher at its end; the rowing boat (items/ships/fisher-boat) moors at its `dock`.",
                                             "site": {"origin": True}, "params": {"detail": 4, "water": -2.21, "footW": W + 2, "footD": D + 2}, "parts": hut, "build": list(hut)})
write("finishes", "fisher-hut", {"name": "Fisherman's hut", "building": "architecture/village/fisher-hut", "_about": "boards and reed: the hut",
      "stone": {"color": "#6b4a2c", "accent": "#5a3e24", "pat": "wood"},
      # (the roof: all of it thatch but its underside -- its gable ends are walls to `surface`, and the boards' catch-all
      #  took them; the walls weatherboard, not floorboards, 2026-10-24)
      "rules": [{"parts": "roof", "side": "in", "pattern": "timber/boards", "palette": "oak-grey"}, {"parts": "roof", "pattern": "roofs/thatch", "palette": "thatch-grey"},
                {"parts": ["nets", "nets 2"], "pattern": "fabrics/lozenge", "palette": "undyed"},
                {"parts": ["floor", "jetty"], "surface": "floor", "pattern": "timber/boards", "palette": "oak-grey"}, {"parts": "cot mattress", "pattern": "fabrics/linen", "palette": "linen"},
                {"parts": "walls", "side": "out", "pattern": "timber/weatherboard", "palette": "oak-grey"},
                {"pattern": "timber/boards", "palette": "oak"}]})

# ---- THE WATER MILL (2026-10-03: two storeys, the millwork whole): stone walls, a tiled roof; its wheel 6.1 m across on
# an axle only .5 m above the floor (the water is 2.35 m below it: a big low wheel is the only way the paddles reach the
# stream). The way the grain goes, as in a small mill of the Middle Ages:
#   * the STONE FLOOR upstairs: the sacks of grain, the HOPPER on its horse over the stones, its SHOE shaking the grain
#     into the eye of the RUNNER STONE over the fixed BEDSTONE inside the TUN;
#   * the MEAL FLOOR below: the PIT WHEEL on the wheel's axle turning in its fenced pit drives the WALLOWER, whose UPRIGHT
#     SHAFT goes up through the floor to the runner (underdrift); the meal falls from the tun's spout down the meal
#     chute into the meal bin and is sacked; barrels and kegs; the miller by the door, the sacks' `drop` outside it.
# The wheel (with its axle and pit wheel: items/components/water-wheel) turns at the `rotor`; the wallower, the shaft and
# the runner are `spin` markers turned six times as fast. A stair up the north wall to the stone floor.
W, D, H, T, F, AX, SF = 9, 6.5, 5.6, 0.5, 0.15, 0.5, 2.7
pitZ = D / 2 - 0.9; pitZ0 = pitZ - 1.05; pitZ1 = D / 2 - T; wheelZ = D / 2 + 4.6; sz = pitZ - 0.45   # sz: the stones' axis, the wallower's face to the pit wheel's
BIG, KEG = {"h": 0.95, "belly": 0.35, "head": 0.29}, {"h": 0.55, "belly": 0.21, "head": 0.17}
G = SF - 0.2                                                                                        # the ground storey's height (to the stone floor's foot)
xi, zi = W / 2 - T, D / 2 - T                                                                      # the inside's half-sizes
sx0, sx1, sz0, sz1 = -xi + 1.0, -xi + 1.0 + 13 * 0.25, -zi, -zi + 0.9                              # the stair: up the north wall, climbing +x (a stair's width of floor before it)
hx0, hx1, hz1 = sx0 + 1 * 0.25, sx1 + 0.05, sz1 + 0.3   # the stair's hole in the stone floor, 30cm wider than the stair (a walker's shoulder clears its edge)
tiers = lambda ground, upper: [{"h": G, "openings": ground}, {"openings": upper}]
mill = {
    "floor": box(W - 0.04, pitZ0 + D / 2 - 0.02, 0.3, (0, F - 0.3, (pitZ0 - D / 2 + 0.02) / 2), walked=True),
    "floor sides": box(W / 2 - 0.7 - 0.02, D / 2 - pitZ0 - 0.02, 0.3, (-(W / 2 + 0.7 - 0.02) / 2, F - 0.3, (pitZ0 + D / 2 - 0.02) / 2), ((W / 2 + 0.7 - 0.02) / 2, F - 0.3, (pitZ0 + D / 2 - 0.02) / 2), walked=True),
    "pit floor": box(1.4, pitZ1 - pitZ0, 0.1, (0, -1.6, (pitZ0 + pitZ1) / 2)),
    "pit walls": box(0.12, pitZ1 - pitZ0, 1.65, (-0.77, -1.525, (pitZ0 + pitZ1) / 2), (0.77, -1.525, (pitZ0 + pitZ1) / 2)),
    "pit back": box(1.66, 0.12, 1.65, (0, -1.525, pitZ0 - 0.07)),
    "pit rail posts": box(0.07, 0.07, 0.95, *[(x, F, z) for x, z in ((-0.85, pitZ0 - 0.1), (0.85, pitZ0 - 0.1), (-0.85, pitZ1 - 0.1), (0.85, pitZ1 - 0.1))]),
    "pit rails": box(1.8, 0.06, 0.06, (0, F + 0.89, pitZ0 - 0.1)),
    "pit rails sides": box(0.06, pitZ1 - pitZ0, 0.06, (-0.85, F + 0.89, (pitZ0 + pitZ1) / 2 - 0.1), (0.85, F + 0.89, (pitZ0 + pitZ1) / 2 - 0.1)),
    "walls": {"type": "enclosure", "plan": {"rect": [W, D]}, "thickness": T, "height": H, "openings": [], "at": [[0, 0, 0, 0]],
              "faces": {"0": tiers([opening(0, 0.6, AX - 0.2, AX + 0.2), opening(3.0, 0.9, 1.3, 2.3)], [opening(-2.2, 0.8, 0.7, 1.7)]),   # the river wall: the axle's hole, windows
                        "2": tiers([opening(2.5, 0.9, 1.3, 2.3)], [opening(-2.2, 0.8, 0.7, 1.7)]),
                        "1": tiers([opening(0, 1.3, 0, 2.3)], [opening(0, 0.8, 0.7, 1.7)]),
                        "3": tiers([opening(0, 0.9, 1.3, 2.3)], [opening(0, 0.8, 0.7, 1.7)])},
              "interior": True, "_about": "two storeys: the river wall (+z) with the axle's hole and windows, the north (face 2 runs -x), the door onto the street (east), the west; inside them the mill, an interior up to the eaves plate that closes it"},
    # (the wheel pit, under the floor: the mill's inside too)
    "pit interior": {"type": "interior", "plan": {"rect": [1.54, round(pitZ1 - pitZ0 + 0.07, 4)]}, "height": 1.55, "at": [[0, -1.55, round((pitZ0 - 0.07 + pitZ1) / 2, 4), 0]]},
    "roof": {"type": "roof", "form": "gable", "width": D + 0.8, "length": W + 0.8, "pitch": 37.5, "overhang": 0, "at": [[0, H, 0, PI2]]},
    "eaves plate": box(W + 1.0, D + 1.0, 0.25, (0, H - 0.225, 0)),
    # the stone floor: boards on joists over the meal floor, the stair's hole at the north-west
    "stone floor": box(2 * xi, zi - hz1, 0.2, (0, G, (zi + hz1) / 2)),
    "stone floor west": box(hx0 + xi, hz1 + zi, 0.2, ((hx0 - xi) / 2, G, (hz1 - zi) / 2)),
    "stone floor east": box(xi - hx1, hz1 + zi, 0.2, ((hx1 + xi) / 2, G, (hz1 - zi) / 2)),
    "joists": box(0.15, 2 * zi, 0.2, *[(x, G - 0.2, 0) for x in (-2.4, -0.9, 0.9, 2.4) if not hx0 < x < hx1]),
    # (over the stair's hole the joists stop at a trimmer along its edge: headroom for the climb)
    "joists short": box(0.15, zi - hz1, 0.2, *[(x, G - 0.2, (zi + hz1) / 2) for x in (-2.4, -0.9, 0.9, 2.4) if hx0 < x < hx1]),
    "trimmer": box(hx1 - hx0, 0.15, 0.2, ((hx0 + hx1) / 2, G - 0.2, hz1 + 0.075)),
    "stair": {"type": "flight", "run": 0.25, "width": 0.9, "base": 0, "top": SF - F, "steps": 13, "landing": 0, "soffit": 0.2, "at": [[sx0, F, sz1, 0]]},
    "wheel piles": col(0.2, 5.6, (-0.6, -4.7, wheelZ + 0.95), (0.6, -4.7, wheelZ + 0.95), taper=0.9),
    "bearing beam": box(1.8, 0.32, 0.28, (0, AX - 0.42, wheelZ + 0.95)),
    # the stones upstairs, the hopper over them; the meal chute down to the bin below
    "bedstone": item("items/components/millstone", (0, SF, sz), params={"h": 0.24}),
    "tun": item("items/components/tun", (0, SF, sz), solid=False),
    "hopper": item("items/components/hopper-horse", (0.55, SF + 0.55, sz), solid=False),
    "meal chute": box(0.2, 0.2, SF + 0.15 - 1.0, (-1.05, 1.0, sz)),
    "meal bin": box(1.0, 0.8, 0.85, (-1.55, F, sz - 0.3)),
    "flour": item("items/tools/sack-standing", (-2.4, F, sz - 0.2), (-2.3, F, sz - 0.9), solid=False),
    "grain upstairs": item("items/tools/sack", (2.6, SF, -1.6), (2.6, SF, -1.0), (2.6, SF + 0.4, -1.3), solid=False),
    "grain standing": item("items/tools/sack-standing", (1.6, SF, -1.9), solid=False),
    "sacks": item("items/tools/sack", *[(2.9, F + (0.4 if z in (-1.33, -0.78) else 0), z) for z in (-1.6, -1.05, -0.5, -1.33, -0.78)], solid=False),
    "sacks standing": item("items/tools/sack-standing", (1.7, F, -2.4), (3.2, F, -2.5), solid=False),
    "barrels": item("items/furniture/barrel", *[(x, F, 2.2) for x in (-3.6, -2.85, -2.1)], params=BIG),
    "kegs": item("items/furniture/barrel", (-3.6, F, 1.3), (-2.9, F, 1.3), params=KEG),
    "barrel on its side": item("items/furniture/barrel-on-side", (-3.6, F, 0.3), params=BIG),
    "sacks outside": item("items/tools/sack", (W / 2 + 1.6, 0, -1.9, PI2), (W / 2 + 1.6, 0, -2.5, PI2), solid=False),
    # the turning millwork (with the wheel: the pit wheel is on its axle): wallower, upright shaft, runner stone
    "wallower": marker("spin", (0, AX + 0.85, sz), item="items/components/lantern-pinion", params={"r": 0.36, "h": 0.4, "n": 8}, axis="y", ratio=-6),
    "upright shaft": marker("spin", (0, AX + 1.25, sz), item="items/components/mill-shaft", params={"L": round(SF + 0.46 - AX - 1.25, 3), "r": 0.11}, axis="y", ratio=-6),
    "runner stone": marker("spin", (0, SF + 0.24, sz), item="items/components/millstone", params={"h": 0.22}, axis="y", ratio=-6),
    "miller": marker("spot", (W / 2 - 1.6, F, -1.4, PI), pose="stand", work=1, gesture="lift"),
    "miller at the stones": marker("spot", (1.5, SF, sz - 0.9, 2.4), pose="stand", work=1, gesture="lift"),
    "drop": marker("drop", (W / 2 + 1.6, 0, -0.9)),
    "cobwebs": marker("cobweb", (-(W / 2 - T), H, -(D / 2 - T)), sx=1, sz=1, d=0.6),
    "cobweb 2": marker("cobweb", (W / 2 - T, G, -(D / 2 - T)), sx=-1, sz=1, d=0.5),
    "wheel": marker("rotor", (0, AX, wheelZ), r=3.05, w=1.2, axleBack=round(wheelZ - pitZ + 0.3, 4), axleFwd=0.95),
    "door": marker("door", (W / 2 - T / 2, 0, 0, -PI2), w=1.3, h=2.3),
    "windows": {"type": "marker", "role": "window", "at": [[3.0, 1.3, D / 2 - T / 2, 0], [-2.5, 1.3, -(D / 2 - T / 2), 0], [-(W / 2 - T / 2), 1.3, 0, -PI2]], "data": {"w": 0.9, "h": 1.0}},
    "windows upstairs": {"type": "marker", "role": "window", "at": [[-2.2, G + 0.7, D / 2 - T / 2, 0], [2.2, G + 0.7, -(D / 2 - T / 2), 0], [W / 2 - T / 2, G + 0.7, 0, -PI2], [-(W / 2 - T / 2), G + 0.7, 0, -PI2]], "data": {"w": 0.8, "h": 1.0}},
}
write("architecture", "village/watermill", {"name": "Water mill", "_about": "THE WATER MILL in two storeys: stone walls under a tiled roof; the wheel (items/components/water-wheel, its axle and pit wheel, turned by the game at the `rotor`) 6.1 m across on an axle only .5 m above the floor; the pit wheel in its fenced pit drives the wallower and the upright shaft up through the floor to the runner stone (`spin` markers, turned with the wheel); upstairs the stone floor -- bedstone and runner in the tun, the hopper on its horse, the grain -- reached by a stair up the north wall; below, the meal chute into the meal bin, the flour sacked; barrels and kegs; the miller by the door and at the stones, the sacks' `drop` outside.",
                                            "site": {"origin": True}, "params": {"detail": 4, "footW": W + 2, "footD": D + 2}, "parts": mill, "build": [n for n, d in mill.items() if d["type"] != "interior"]})
write("finishes", "watermill", {"name": "Water mill", "building": "architecture/village/watermill", "_about": "the mill: rubble stone, a tiled roof, oak works, millstones",
      "stone": {"color": "#b8ad98", "accent": "#a89c86", "pat": "ashlar"},
      "rules": [{"parts": "roof", "surface": "roof", "pattern": "roofs/fish scale", "palette": "tile-brown"},
                {"parts": ["floor", "floor sides"], "surface": "floor", "pattern": "floors/flagstones", "palette": "stone"},
                {"parts": ["stone floor", "stone floor west", "stone floor east", "kind:flight"], "pattern": "timber/boards", "palette": "oak-grey"},
                {"parts": ["pit rail posts", "pit rails", "pit rails sides", "eaves plate", "wheel piles", "bearing beam", "joists", "joists short", "trimmer", "meal chute", "meal bin"], "pattern": "timber/bark", "palette": "oak-grey"},
                {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
                {"pattern": "stone/rubble", "palette": "stone"}]})

# ---- THE LANDING: a gravel apron on the quay top (the storage rows, the carts' turning place), a plank deck on piles
# reaching out over the bank line, a stair down to a floating stage at the barge's deck height with mooring bollards
L_ = {
    "apron": box(20, 12, 0.1, (0, -0.05, 0), walked=True),
    "deck": box(12, 5.2, 0.16, (0, 0.02, 6.5), walked=True),
    "deck piles": col(0.18, 5, *[(x, -4.8, z) for x in (-5.5, -2, 2, 5.5) for z in (4.6, 8.6)], taper=0.89),
    "stage": box(8, 4, 0.14, (0, -1.37, 11), walked=True),
    "stage piles": col(0.18, 4, *[(x, -5.2, z) for x in (-3.6, 0, 3.6) for z in (9.5, 12.6)], taper=0.89),
    # the stair from the deck's edge (z 9.1) down onto the stage, its foot on the stage with a metre and a half of it
    # before it (it used to come down beside the stage, past its end, onto the water); the deck's rail broken for it
    "stair": {"type": "flight", "run": 0.28, "rise": 0.17625, "width": 1.4, "base": 0, "top": 1.41, "landing": 0, "at": [[3.9, -1.23, 9.1 + 8 * 0.28, PI2]], "_about": "down to the stage, east side"},
    "rail posts": box(0.08, 0.08, 0.95, *[(x, 0.18, 9.05) for x in (-6, -4, -2, 0, 2.46, 3.94, 6)]),
    "rail": box(8.54, 0.06, 0.06, (-1.77, 1.07, 9.05)),
    "rail east": box(2.14, 0.06, 0.06, (4.97, 1.07, 9.05)),
    "bollards": col(0.14, 0.7, (-3, -1.3, 12.7), (1, -1.3, 12.7), taper=0.86),
    "slots": {"type": "marker", "role": "slot", "at": [[-5 + i * 2, 0.05, round(-4.6 + r * 2.2, 3), 0] for r in range(3) for i in range(6)], "data": {}},
    **{f"path {i}": marker("path", p, i=i) for i, p in enumerate([(0.6, -1.23, 12.4), (3.2, -1.23, 12.0), (3.2, 0.18, 8.6), (3.0, 0.18, 4.6)])},
    "berth": marker("berth", (0, 0, 15.5)),
}
write("architecture", "village/landing", {"name": "Landing", "_about": "THE RIVER LANDING: a gravel apron on the quay top (the goods' `slot`s, the carts' turning place), a plank deck on piles out over the bank line, a stair down to the floating stage at the barge's deck height with its bollards; the dock hands' way (`path` markers in order) from the stage up to the quay, the moored barge's `berth`.",
                                          "site": {"origin": True}, "params": {"detail": 4, "footW": 22, "footD": 14}, "parts": L_, "build": list(L_)})
write("finishes", "landing", {"name": "Landing", "building": "architecture/village/landing", "_about": "the landing: gravel and planks",
      "stone": {"color": "#7a5a36", "accent": "#5a4228", "pat": "wood"},
      "rules": [{"parts": "apron", "pattern": "stone/sand", "palette": "gravel"}, {"parts": ["deck", "stage"], "pattern": "timber/boards", "palette": "oak-grey"},
                {"pattern": "timber/bark", "palette": "oak-grey"}]})
print("riverside: fisher hut, watermill, landing")
