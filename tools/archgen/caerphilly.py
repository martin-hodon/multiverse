#!/usr/bin/env python3
"""CAERPHILLY CASTLE (2026-10-02, was architecture.js englishCastle): the concentric water castle as an arch-engine
definition (assets/architecture/caerphilly.json) and its finish. The island plinth carries a low outer curtain with its
corner turrets and a high inner ward -- four drum towers, the twin-towered gatehouse, the great hall against the rear
wall, straight stairs up both side walls to the wall-walk -- and the timber bridge over the moat to the front gate. The
definition keeps its OWN ORIGIN (the island's middle) and says its MOAT (`site.moat`: the game carves the water round
the island) and the LIFTS from the wall-walk onto the tower decks (`lift` markers: the top as `dx`, `dy`, `dz`).

    python3 tools/archgen/caerphilly.py
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
def opening(x, w, sill, top, glass=False): return {"at": x, "width": w, "sill": sill, "springing": top, "head": {"profile": "flat"}, "glass": glass}


IW, ID = 17, 13            # the inner ward's half extents (its curtain's middle lines)
OW, OD = 29, 25            # the outer curtain's outer faces
HW, HD = 34, 30            # the island's
MW = 13                    # the moat's width
Y0 = 0.4                   # the island's top: everything stands on it
wallH, wallT, outH, outT, towerR, towerH = 9, 2.2, 5.5, 1.5, 5.2, 14.5
walkY, deckY = Y0 + wallH, Y0 + towerH
parts = {}


def battlements(name, places, r, top, seg):
    """a drum's battlements: a parapet ring of `seg` facets 0.75 m high just inside its face, and merlons on it --
    every other bay of a ring of about 1.55 m bays (the 13th century's merlon and embrasure)"""
    n = max(6, round(2 * math.pi * (r - 0.2) / 1.55))
    parts[name + " parapet"] = {"type": "ring", "count": seg, "rOuter": round(r - 0.02, 3), "rInner": round(r - 0.38, 3), "height": 0.75, "y": round(top, 3),
                                "solid": True, "place": [[x, 0, z, 0] for x, z in places]}
    parts[name + " merlons"] = {"type": "ring", "count": 2 * n, "rOuter": round(r - 0.02, 3), "rInner": round(r - 0.38, 3), "height": 0.95, "y": round(top + 0.75, 3),
                                "solid": True, "at": list(range(0, 2 * n, 2)), "place": [[x, 0, z, 0] for x, z in places]}


parts["island"] = box(2 * HW, 2 * HD, Y0, (0, 0, 0), walked=True)
# the outer curtain: a low ring, its gates front (+z) and back
parts["outer curtain"] = {"type": "enclosure", "plan": {"rect": [2 * OW, 2 * OD]}, "thickness": outT, "height": outH, "openings": [], "at": [[0, Y0, 0, 0]],
                          "faces": {"0": [opening(0, 4.2, 0, 4.4)], "2": [opening(0, 4.2, 0, 4.4)]}}
turrets = [(sx * OW, sz * OD) for sx in (-1, 1) for sz in (-1, 1)]
parts["turrets"] = col(1.9, outH + 2.4, *[(x, Y0, z) for x, z in turrets], sides=10)
battlements("turret", turrets, 1.9, Y0 + outH + 2.4, 10)
# the inner ward: the high curtain, its top the wall-walk, parapets both sides (the inner one open where the stairs land)
parts["inner curtain"] = {"type": "enclosure", "plan": {"rect": [2 * IW + wallT, 2 * ID + wallT]}, "thickness": wallT, "height": wallH, "openings": [], "at": [[0, Y0, 0, 0]],
                          "faces": {"0": [opening(0, 3.6, 0, 4.4)], "2": [opening(0, 3.6, 0, 4.4)]}, "walked": True}
po = wallT / 2 - 0.15
parts["walk parapets"] = box(2 * IW + wallT, 0.3, 1.15, *[(0, walkY, sz * ID + o * po) for sz in (-1, 1) for o in (-1, 1)])
parts["walk parapets ends"] = box(0.3, 2 * ID, 1.15, (-(IW + po), walkY, 0), (IW + po, walkY, 0))
parts["walk parapets inner"] = box(0.3, ID + 5.6, 1.15, *[(sx * (IW - po), walkY, (-ID + 5.6) / 2) for sx in (-1, 1)])
parts["walk parapets inner 2"] = box(0.3, ID - 8.7, 1.15, *[(sx * (IW - po), walkY, (8.7 + ID) / 2) for sx in (-1, 1)])
# four drum towers, their decks reached by a lift from the walk
towers = [(sx * IW, sz * ID) for sx in (-1, 1) for sz in (-1, 1)]
parts["towers"] = col(towerR, towerH, *[(x, Y0, z) for x, z in towers], sides=14, walked=True)
battlements("tower", towers, towerR, deckY, 14)
parts["tower lifts"] = {"type": "marker", "role": "lift", "at": [[x, walkY, z - (1 if z > 0 else -1) * (towerR + 1.4), 0] for x, z in towers],
                        "data": {"dx": 0, "dy": round(deckY - walkY, 3), "dz": [(1 if z > 0 else -1) * (towerR + 1.4) for x, z in towers]}}
# the twin-towered gatehouse over the front gate
gt = [(sx * 4.5, ID + 1.2) for sx in (-1, 1)]
parts["gate towers"] = col(3.1, 12, *[(x, Y0, z) for x, z in gt], sides=12)
battlements("gate tower", gt, 3.1, Y0 + 12, 12)
parts["gatehouse"] = box(10.4, 6.2, 3.4, (0, Y0 + 5.5, ID + 0.8))
# the great hall against the rear wall: its front with the door and two windows, its ends, a slate roof; a table and chairs
parts["hall front"] = {"type": "wall", "width": 15, "height": 5.5, "thickness": 1, "at": [[-1, Y0, -ID + 7.5, 0]],
                       "openings": [opening(3.5, 1.6, 0, 2.6), opening(9.5, 1.6, 1.4, 3.2), opening(12.7, 1.6, 1.4, 3.2)]}
parts["hall ends"] = box(1, 6.5, 5.5, (-8.5, Y0, -ID + 3.75), (6.5, Y0, -ID + 3.75))
parts["hall roof"] = {"type": "roof", "form": "gable", "width": 8, "length": 16.5, "pitch": round(math.degrees(math.atan2(3.4, 4)), 3), "overhang": 0, "at": [[-1, Y0 + 5.5, -ID + 3.6, PI2]]}
parts["hall table"] = item("items/furniture/plain-table", (-3, Y0, -ID + 4))
parts["hall chairs"] = item("items/furniture/plain-chair", (-3, Y0, -ID + 5.2, PI), (-1.6, Y0, -ID + 3.2, PI2))
# straight stairs from the ward up to the wall-walk, hugging both side walls: 9 m in 47 steps along 13.5 m, then the walk
parts["wall stairs"] = {"type": "flight", "run": round(13.5 / 47, 4), "width": 1.8, "base": 0, "top": wallH, "steps": 47, "landing": 1.0,
                        "at": [[sx * (IW - 1.9) - 0.9, Y0, -6.5, -PI2] for sx in (-1, 1)], "_about": "(yaw -90: the flight climbs toward +z, its width toward +x from its placement)"}
# the timber bridge over the moat to the front gate (its deck from the road's end onto the island, an apron step down to
# the road), its rails, two piers wholly under the deck
parts["bridge deck"] = box(4.6, MW + 8, 0.5, (0, -0.05, HD + MW / 2 + 2), walked=True)
parts["bridge apron"] = box(4.6, 3, 0.3, (0, 0, HD + MW + 6.5), walked=True)
parts["bridge rails"] = box(0.3, MW + 8, 1.1, (-2.15, 0.45, HD + MW / 2 + 2), (2.15, 0.45, HD + MW / 2 + 2))
parts["bridge piers"] = col(0.9, 4, (0, -3.85, HD + 3.5), (0, -3.85, HD + MW - 3.5), taper=round(0.8 / 0.9, 4))
# its life: the gate leaf and the hall's door, the hall's window, cobwebs in the hall's corners
parts["doors"] = {"type": "marker", "role": "door", "at": [[0, Y0, ID, 0], [-5, Y0, -ID + 7, 0]], "data": {"w": [3.4, 1.6], "h": [4.2, 2.6]}}
parts["hall window"] = marker("window", (1, Y0 + 1.45, -ID + 7.5), w=1.5, h=1.7)
parts["cobwebs"] = {"type": "marker", "role": "cobweb", "at": [[-8, Y0 + 5.5, -ID + 6.5, 0], [6, Y0 + 5.5, -ID + 0.9, 0]], "data": {"sx": [1, -1], "sz": [-1, 1], "d": [0.7, 0.6]}}

write("architecture", "caerphilly", {"name": "Caerphilly Castle",
      "_about": "CAERPHILLY CASTLE: the concentric water castle (1268-71) -- the island plinth, a low outer curtain with gates front and back and corner turrets, the high inner ward with its wall-walk, four drum towers with lifts onto their decks, the twin-towered gatehouse, the great hall against the rear wall with a table and chairs, straight stairs up both side walls, and the timber bridge over the moat. Its own origin is the island's middle; `site.moat` is the water the game carves round it.",
      "site": {"origin": True, "moat": {"hw": HW, "hd": HD, "w": MW, "depth": 4.4}},
      "params": {"detail": 4, "footW": 2 * (HW + MW) + 4, "footD": 2 * (HD + MW) + 4}, "railing": {"type": "stone", "height": 1.0},
      "parts": parts, "build": list(parts)})
write("finishes", "caerphilly", {"name": "Caerphilly Castle", "building": "architecture/caerphilly", "_about": "Pennant sandstone ashlar, a slate roof on the hall, oak on the bridge, the ward gravelled",
      "stone": {"color": "#a9a294", "accent": "#8e887b", "pat": "ashlar"},
      "rules": [{"parts": "hall roof", "surface": "roof", "pattern": "roofs/slate", "palette": "slate"},
                {"parts": ["bridge deck", "bridge apron", "bridge rails", "bridge piers"], "pattern": "timber/boards", "palette": "oak"},
                {"parts": "island", "surface": "floor", "pattern": "stone/sand", "palette": "gravel"},
                {"pattern": "stone/ashlar", "palette": "pennant-sandstone"}]})
print("caerphilly:", len(parts), "parts")
