#!/usr/bin/env python3
"""CAERPHILLY CASTLE (2026-10-02, was architecture.js englishCastle): the concentric water castle as an arch-engine
definition (assets/architecture/caerphilly.json) and its finish. The island plinth carries a low outer curtain and a
high inner ward, both `ward`s (arch/castle.js): their towers, gates, wall walks, loops and newel stairs follow from the
curtain's measures. The great hall stands against the inner ward's rear wall, and the timber bridge crosses the moat to
the front gate. The definition keeps its OWN ORIGIN (the island's middle) and says its MOAT (`site.moat`: the game carves
the water round the island).

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
parts = {}


parts["island"] = box(2 * HW, 2 * HD, Y0, (0, 0, 0), walked=True)
# THE TWO WARDS (arch/castle.js `ward`): the curtain's outer face, its height to the wall walk and its thickness; the
# rest -- towers on the corners projecting their whole radius to flank both faces, the gate between its pair of towers,
# the crenellated walk running through the towers, their floors, loops and newel stairs -- follows from the rules.
# CONCENTRIC: the inner ward stands higher than the outer, so that both lines can shoot over the outer one at once.
parapet = {"breast": 1.1, "merlon": 0.9, "t": 0.5, "step": 2.2, "crenel": 0.75}
parts["outer ward"] = {"type": "ward", "plan": {"rect": [2 * OW, 2 * OD]}, "height": outH, "thickness": outT, "parapet": parapet,
                       "towers": {"radius": 3.0, "wall": 0.8, "over": 3.6, "storeyH": 6, "flank": 60},
                       "gates": [{"face": 0, "width": 4.2, "height": 4.4, "radius": 2.8}, {"face": 2, "width": 4.2, "height": 4.4, "radius": 2.8}],
                       "at": [[0, Y0, 0, 0]], "_about": "the low outer curtain round the island, a turret on every corner and a gate front and back between two more"}
parts["inner ward"] = {"type": "ward", "plan": {"rect": [2 * IW + wallT, 2 * ID + wallT]}, "height": wallH, "thickness": wallT, "parapet": parapet,
                       "towers": {"radius": towerR, "wall": 1.6, "over": towerH - wallH, "storeyH": 4.5},
                       "gate": {"face": 0, "width": 3.6, "height": 4.4, "radius": 3.6},
                       "at": [[0, Y0, 0, 0]], "_about": "the high inner ward: four drum towers on its corners and the twin-towered gatehouse to the front (the great hall stands against the rear wall)"}
# the great hall against the rear wall: its front with the door and two windows, its ends, a slate roof; a table and chairs
parts["hall front"] = {"type": "wall", "width": 15, "height": 5.5, "thickness": 1, "at": [[-1, Y0, -ID + 7.5, 0]],
                       "openings": [opening(3.5, 1.6, 0, 2.6), opening(9.5, 1.6, 1.4, 3.2), opening(12.7, 1.6, 1.4, 3.2)]}
parts["hall ends"] = box(1, 6.5, 5.5, (-8.5, Y0, -ID + 3.75), (6.5, Y0, -ID + 3.75))
parts["hall roof"] = {"type": "roof", "form": "gable", "width": 8, "length": 16.5, "pitch": round(math.degrees(math.atan2(3.4, 4)), 3), "overhang": 0, "at": [[-1, Y0 + 5.5, -ID + 3.6, PI2]]}
parts["hall table"] = item("items/furniture/plain-table", (-3, Y0, -ID + 4))
parts["hall chairs"] = item("items/furniture/plain-chair", (-3, Y0, -ID + 5.2, PI), (-1.6, Y0, -ID + 3.2, PI2))
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
      "_about": "CAERPHILLY CASTLE: the concentric water castle (1268-71) -- the island plinth, a low outer curtain with turrets on its corners and a gate front and back between two more, the high inner ward with its crenellated wall walk running through four drum towers on its corners, each projecting to flank both curtains, with loops staggered storey by storey and a newel stair from the ward to its deck; the twin-towered gatehouse, the great hall against the rear wall with a table and chairs, and the timber bridge over the moat. Its own origin is the island's middle; `site.moat` is the water the game carves round it.",
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
