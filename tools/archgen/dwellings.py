#!/usr/bin/env python3
"""DWELLINGS (2026-10-02): tents and houses of other times and peoples than the medieval town's -- the knight's
pavilion, the soldier's bell and wedge tents, the marquee, the Roman papilio, the Mongol ger, the Plains tipi, the
Bedouin black tent, the wigwam, the igloo, the Iron Age roundhouse and the crannog, the rondavel and the beehive hut,
the Navajo hogan, the sunken pit house, the Norse and the Iroquois longhouses, the stilt house, the Japanese minka,
the Roman domus, the Greek house, the Arab courtyard house, the Chinese siheyuan, the Egyptian house, the pueblo and
the Hebridean blackhouse -- as arch-engine definitions (assets/architecture/dwellings/*.json), each with its finish
(assets/finishes/<name>.json: felt, hide, thatch, adobe, turf, bark), and the "Dwellings" catalogue category.

    python3 tools/archgen/dwellings.py

Round ones have their door at +x (a ring's bay 0), straight ones on their +z face (an enclosure's face 0). A hearth
is a `fire` marker; nothing here is placed in the game yet -- they are the catalogue's, for other worlds.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ARCH = os.path.join(ROOT, "assets", "architecture")
FIN = os.path.join(ROOT, "assets", "finishes")
PI2 = 1.5707963


def write(base, path, doc):
    full = os.path.join(base, path + ".json")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")


def at(*xs):
    return [list(x) for x in xs] if isinstance(xs[0], (list, tuple)) else [list(xs)]


def box(w, l, h, *pos, **k):
    return {"type": "box", "width": w, "length": l, "height": h, "at": at(*pos), **k}


def col(r, h, *pos, sides=8, **k):
    return {"type": "column", "radius": r, "height": h, "sides": sides, "at": at(*pos), **k}


def ring(r, h, t, n=12, y=0, bays=None, opening=None, place=(0, 0, 0, 0), **k):
    d = {"type": "ring", "count": n, "rOuter": r, "rInner": round(r - t, 4), "height": h, "y": y, "place": [list(place)], **k}
    if bays is not None: d["at"] = bays
    if opening: d["opening"] = opening
    else: d["solid"] = True
    return d


def walls_with_door(r, h, t, n, door, y=0, place=(0, 0, 0, 0), windows=None):
    """a round wall of n bays, the door in bay 0 (+x), windows in the bays listed"""
    out = {"wall": ring(r, h, t, n, y, [b for b in range(1, n) if b not in (windows or {})], place=place),
           "door": ring(r, h, t, n, y, [0], door, place=place)}
    if windows: out["windows"] = ring(r, h, t, n, y, sorted(windows), windows[sorted(windows)[0]], place=place)
    return out


def cone(r, rise, y, sides=12, t=0, profile="trigonal", **k):
    # (no cap: the inside follows the outside -- a cone is a cone from within, not a flat ceiling at its eave)
    head = {"profile": profile, "rise": rise, **({} if profile == "trigonal" else {"seg": 6})}   # (a curved meridian keeps its curve at any detail: a small dome would else be a cone)
    return {"type": "dome", "sides": sides, "radius": r, "thickness": t, "head": head, "cap": False, "at": [[0, y, 0, 0]], **k}


def cone_with_door(name, r, rise, door_w, door_h, sides=12, t=0, profile="trigonal", y=0):
    """a cone or a dome down to the ground with a DOORWAY at its foot (+x): the band below the door's head as a dome
    cut off there (`oculus`) with a gap round it (`sweep`), and above it the rest -- for a cone a smaller cone, for a
    hemisphere a segmental cap (a sphere's top IS a segmental dome) -- so the door is a hole, not a painted flap"""
    if profile == "trigonal":
        a = r * (1 - door_h / rise); top = cone(a, rise - door_h, y + door_h, sides, t, "trigonal")
    else:   # semicircular
        a = math.sqrt(r * r - door_h * door_h); top = cone(a, r - door_h, y + door_h, sides, t, "segmental")
    band = {**cone(r, rise if profile == "trigonal" else r, y, sides, t, profile), "oculus": round(a, 4), "sweep": round(1 - door_w / (2 * math.pi * r), 4)}
    band["at"] = [[0, y, 0, -PI2]]   # (a part-dome is open toward -z: turned, its gap faces +x)
    return {name: band, name + " top": top}


def roof(form, w, l, pitch, y, yaw=0, over=0.3, shell=None, x=0, z=0, **k):
    d = {"type": "roof", "form": form, "width": w, "length": l, "pitch": pitch, "overhang": over, "at": [[x, y, z, yaw]], **k}
    if shell is not None: d["shell"] = shell
    return d


def door(w, h, head="flat", x=0):
    return {"at": x, "width": w, "sill": 0, "springing": h, "head": {"profile": head}}


def fire(*pos, r=0.25, h=0.5):
    return {"type": "marker", "role": "fire", "at": at(*pos), "data": {"r": r, "h": h}}


def ringpos(n, r, y=0, start=0):
    return [[round(r * math.cos(2 * math.pi * (k + start) / n), 4), y, round(r * math.sin(2 * math.pi * (k + start) / n), 4), 0] for k in range(n)]


def rule(parts, pattern, palette, **k):
    return {"parts": parts, "pattern": pattern, "palette": palette, **k}


DWELLINGS = {}


def dwelling(key, name, era, region, about, parts, rules, params=None, stone=None):
    DWELLINGS[key] = (name, era, region, about, parts, rules, params, stone)


# ---- TENTS ------------------------------------------------------------------------------------------------------
dwelling("pavilion", "Pavilion", "1250-1600", "Europe", "the knight's round pavilion of the tourney and the camp: a striped canvas wall on a ring, a conical roof over a centre pole, the valance round its eave, a pennant on top",
         {**walls_with_door(2.5, 2.0, 0.03, 12, door(1.1, 1.9)),
          "valance": ring(2.66, 0.35, 0.03, 12, y=1.85),
          "roof": cone(2.66, 2.3, 2.2, 12),
          "pole": col(0.06, 4.9, (0, 0, 0, 0), sides=6),
          "pennant": box(0.6, 0.02, 0.35, (0.3, 4.45, 0, 0))},
         [rule(["roof", "wall", "door"], "fabrics/stripes", "stripe-madder"), rule(["valance", "pennant"], "fabrics/plain", "or-gules"), rule("pole", "timber/bark", "oak")])
dwelling("bell-tent", "Bell tent", "1300-1900", "Europe", "the soldier's bell tent: a short canvas wall and a tall cone on one pole, eight or ten men to it",
         {**walls_with_door(2.2, 0.7, 0.03, 12, door(0.8, 0.65)),
          "roof": cone(2.2, 2.6, 0.7, 12),
          "pole": col(0.05, 3.4, (0, 0, 0, 0), sides=6)},
         [rule(["roof", "wall", "door"], "fabrics/linen", "canvas"), rule("pole", "timber/bark", "pine")])
dwelling("marquee", "Marquee", "1450-1800", "Europe", "the officers' and the feast's marquee: a long canvas room under a hipped roof on two poles",
         {"walls": {"type": "enclosure", "plan": {"rect": [6.0, 4.0]}, "thickness": 0.03, "height": 2.0, "openings": [], "faces": {"0": [door(1.6, 1.9)]}, "at": [[0, 0, 0, 0]]},
          "roof": roof("hip", 4.3, 6.3, 35, 2.0, yaw=PI2, over=0.2, shell=0.03),
          "poles": col(0.06, 3.5, (-1.4, 0, 0, 0), (1.4, 0, 0, 0), sides=6)},
         [rule(["roof"], "fabrics/stripes", "stripe-woad"), rule(["walls"], "fabrics/linen", "canvas"), rule("poles", "timber/bark", "oak")])
dwelling("wedge-tent", "Wedge tent", "1600-1900", "Europe, the Americas", "the ridge (wedge) tent of the line regiments: canvas over a ridge pole on two uprights, the ends laced shut",
         {"roof": roof("gable", 2.2, 2.6, 60, 0, yaw=PI2, over=0.0, shell=0.03, open="front"),
          "uprights": col(0.035, 1.95, (-1.25, 0, 0, 0), (1.25, 0, 0, 0), sides=6),
          "ridge pole": box(2.7, 0.06, 0.06, (0, 1.9, 0, 0))},
         [rule("roof", "fabrics/linen", "canvas"), rule(["uprights", "ridge pole"], "timber/bark", "pine")])
dwelling("roman-tent", "Papilio", "-100-400", "the Roman Empire", "the legion's leather tent, a contubernium's eight men under it: a ridge roof on low side walls, laced from goatskin panels",
         {"walls": {"type": "enclosure", "plan": {"rect": [3.0, 3.0]}, "thickness": 0.03, "height": 0.6, "openings": [], "faces": {"0": [door(1.2, 0.6)]}, "at": [[0, 0, 0, 0]]},
          "roof": roof("gable", 3.0, 3.0, 42, 0.6, over=0.05, shell=0.03, open="front"),
          "poles": col(0.04, 2.0, (0, 0, -1.45, 0), (0, 0, 1.45, 0), sides=6)},
         [rule(["roof", "walls"], "fabrics/leather", "leather"), rule("poles", "timber/bark", "oak")])
dwelling("yurt", "Ger (yurt)", "-500-1900", "the steppe: Mongols, Kazakhs, Turkic peoples", "the ger: a lattice wall wrapped in felt, roof poles to a crown ring that lets the smoke out, a painted wooden door to the south, the stove in the middle",
         {"wall": ring(3.0, 1.5, 0.12, 12, bays=list(range(1, 12))),
          "door": ring(3.0, 1.5, 0.12, 12, bays=[0], opening=door(0.9, 1.35)),
          "roof": cone(3.1, 1.2, 1.5, 12, oculus=0.6),
          "crown": ring(0.62, 0.12, 0.08, 8, y=2.46),
          "posts": col(0.06, 2.45, (0.3, 0, 0, 0), (-0.3, 0, 0, 0), sides=6),
          "stove": fire((0, 0, 0, 0), r=0.2, h=0.35)},
         [rule(["roof", "wall"], "fabrics/plain", "wool-white"), rule(["door", "crown", "posts"], "materials/lacquer", "lacquer-red")])
dwelling("tipi", "Tipi", "1500-1900", "the Great Plains", "the Plains tipi: buffalo hide sewn round a cone of lodgepoles, the poles crossing above the smoke hole, the fire inside",
         {**cone_with_door("cover", 2.6, 5.6, 0.8, 1.2, 14),
          "poles": {"type": "item", "item": "items/components/tent-poles", "params": {"n": 12, "r": 2.5, "h": 5.4, "over": 1.0}, "solid": False, "at": [[0, 0, 0, 0]]},
          "fire": fire((0, 0, 0, 0))},
         [rule(["cover", "cover top"], "fabrics/leather", "leather"), rule("poles", "timber/bark", "pine")])
dwelling("bedouin-tent", "Black tent", "-1000-1900", "Arabia, the Sahara, the Levant", "the Bedouin beit al-sha'ar, the house of hair: woven goat-hair strips over a low ridge of poles, the back wall pegged down, the front open to the shade",
         {"roof": roof("gable", 5.0, 9.0, 12, 1.7, yaw=PI2, over=0.0, shell=0.03),
          "poles": col(0.05, 2.25, (-3, 0, 0, 0), (0, 0, 0, 0), (3, 0, 0, 0), sides=6),
          "back wall": box(9.0, 0.03, 1.7, (0, 0, -2.5, 0)),
          "end curtains": box(0.03, 5.0, 1.7, (-4.5, 0, 0, 0), (4.5, 0, 0, 0)),
          "rug": box(4.0, 2.5, 0.02, (0, 0, -0.6, 0)),
          "hearth": fire((2.5, 0, 1.2, 0), r=0.2, h=0.3)},
         [rule(["roof", "back wall", "end curtains"], "fabrics/stripes", "sable-argent"), rule("rug", "fabrics/lozenge", "kilim"), rule("poles", "timber/bark", "walnut")])
dwelling("wigwam", "Wigwam", "-1000-1850", "the Eastern Woodlands (Algonquian peoples)", "the wigwam: saplings bent into a dome and covered with bark and reed mats, a low door, a smoke hole over the fire",
         {**walls_with_door(2.4, 1.0, 0.06, 12, door(0.8, 0.95)),
          "dome": cone(2.4, 1.4, 1.0, 12, profile="segmental", oculus=0.3),
          "fire": fire((0, 0, 0, 0))},
         [rule(["dome", "wall", "door"], "timber/boards", "birch")])

# ---- ROUND HOUSES --------------------------------------------------------------------------------------------------
dwelling("igloo", "Igloo", "1000-1900", "the Arctic (Inuit)", "the snow house: blocks laid in a rising spiral into a dome, entered by a low tunnel that keeps the cold out",
         {**cone_with_door("dome", 1.9, 1.9, 0.8, 0.75, 14, t=0.3, profile="semicircular"),
          "tunnel": {"type": "barrel", "width": 0.9, "length": 1.6, "springing": 0.35, "top": 0.8, "head": {"profile": "semicircular", "seg": 6}, "at": [[2.3, 0, 0, PI2]]},
          "tunnel walls": box(1.6, 0.25, 0.35, (2.3, 0, 0.55, 0), (2.3, 0, -0.55, 0))},
         [rule(["dome", "dome top", "tunnel", "tunnel walls"], "stone/ashlar", "plaster-white")])
dwelling("roundhouse", "Roundhouse", "-800-100", "Iron Age Britain and Gaul", "the Iron Age roundhouse: a wattle-and-daub wall in a ring of posts, a steep thatched cone down over it, the door toward the sunrise, the hearth in the middle",
         {**walls_with_door(4.0, 1.6, 0.25, 16, door(1.1, 1.5)),
          "roof": cone(4.6, 4.6, 1.4, 16, t=0.3),
          "floor": ring(3.75, 0.05, 3.7, 16),
          "posts": col(0.12, 3.2, *ringpos(8, 2.6), sides=6),
          "hearth": fire((0, 0.05, 0, 0))},
         [rule("roof", "roofs/thatch", "thatch", surface="roof"), rule(["wall", "door"], "stone/plaster", "plaster-ochre"), rule("floor", "stone/sand", "earth"), rule("posts", "timber/bark", "oak")])
CR = 3.5
dwelling("crannog", "Crannog", "-800-1600", "Ireland and Scotland", "the crannog: a roundhouse on a timber platform out in a loch, on piles driven into the bed, a walkway to the shore",
         {"platform": ring(5.5, 0.25, 5.45, 20, y=1.5),
          "piles": col(0.12, 1.6, *ringpos(14, 5.0), sides=6),
          "walkway": box(10.0, 1.2, 0.15, (10.5, 1.6, 0, 0)),
          "walkway piles": col(0.1, 1.6, *[[x, 0, z, 0] for x in (7.5, 10.5, 13.5) for z in (-0.5, 0.5)], sides=6),
          **{k: {**v, "place": [[0, 1.75, 0, 0]]} for k, v in walls_with_door(CR, 1.5, 0.2, 14, door(1.0, 1.4)).items()},
          "roof": cone(CR + 0.6, 4.0, 3.1, 14, t=0.3),
          "hearth": fire((0, 1.75, 0, 0))},
         [rule("roof", "roofs/thatch", "thatch", surface="roof"), rule(["wall", "door"], "stone/plaster", "plaster-ochre"),
          rule(["platform", "piles", "walkway", "walkway piles"], "timber/boards", "oak-grey")])
dwelling("rondavel", "Rondavel", "1000-1900", "Southern Africa", "the rondavel: a round wall of mud brick, plastered and limewashed, a thatched cone on top, a door and two small windows",
         {**walls_with_door(2.8, 2.0, 0.25, 12, door(0.9, 1.8), windows={3: {"width": 0.6, "sill": 0.9, "springing": 1.5, "head": {"profile": "flat"}}, 9: {"width": 0.6, "sill": 0.9, "springing": 1.5, "head": {"profile": "flat"}}}),
          "roof": cone(3.3, 2.6, 1.9, 12, t=0.2),
          "floor": ring(2.55, 0.05, 2.5, 12),
          "hearth": fire((0, 0.05, 0, 0))},
         [rule("roof", "roofs/thatch", "thatch", surface="roof"), rule(["wall", "door", "windows"], "stone/plaster", "plaster-white"), rule("floor", "stone/sand", "earth")])
dwelling("beehive-hut", "Beehive hut", "1000-1900", "Southern Africa (Zulu iqhugwane)", "the beehive hut: a dome of bent saplings thatched down to the ground, a low arched door you stoop through",
         {**walls_with_door(2.4, 0.9, 0.12, 12, door(0.65, 0.55, "semicircular")),
          "dome": cone(2.4, 2.2, 0.9, 12, t=0.15, profile="pointed"),
          "hearth": fire((0, 0, 0, 0))},
         [rule(["dome", "wall", "door"], "roofs/thatch", "thatch")])
dwelling("hogan", "Hogan", "1500-1900", "the Southwest (Navajo)", "the hogan: eight walls of logs, the roof corbelled inward in rings and covered with earth, the door to the east, the smoke hole over the fire",
         {"walls": {"type": "enclosure", "plan": {"sides": 8, "radius": 3.0}, "thickness": 0.35, "height": 1.6, "openings": [], "faces": {"0": [door(0.9, 1.5)]}, "at": [[0, 0, 0, 0]]},
          "roof": cone(3.3, 1.4, 1.6, 8, t=0.45, profile="segmental", oculus=0.35),
          "hearth": fire((0, 0, 0, 0))},
         [rule("roof", "stone/sand", "earth"), rule("walls", "timber/boards", "oak-grey")])

# ---- LONG HOUSES -------------------------------------------------------------------------------------------------
dwelling("pit-house", "Pit house", "400-1100", "Anglo-Saxon England, the Slavic lands (Grubenhaus)", "the sunken-floored house: a pit half a metre deep lined with planks, a gable of thatch down almost to the ground over it",
         {"pit floor": box(4.0, 3.0, 0.05, (0, -0.55, 0, 0)),
          "pit lining": {"type": "enclosure", "plan": {"rect": [4.4, 3.4]}, "thickness": 0.2, "height": 0.75, "openings": [], "at": [[0, -0.55, 0, 0]]},
          "roof": roof("gable", 4.8, 5.0, 52, 0.2, yaw=PI2, over=0.3, shell=0.25, open="front"),
          "steps": {"type": "flight", "run": 0.28, "rise": 0.18, "width": 0.9, "base": 0, "top": 0.55, "landing": 0, "at": [[2.2 + 3 * 0.28, -0.55, -0.45, 3.14159265]],
                    "_about": "down into the pit at the open end"},
          "ridge posts": col(0.1, 3.4, (-2.0, -0.55, 0, 0), (2.0, -0.55, 0, 0), sides=6),
          "hearth": fire((1.0, -0.5, 0, 0), r=0.2, h=0.35)},
         [rule("roof", "roofs/thatch", "thatch", surface="roof"), rule(["pit lining", "ridge posts"], "timber/boards", "oak-grey"), rule("pit floor", "stone/sand", "earth")])
dwelling("viking-longhouse", "Norse longhouse", "800-1100", "Scandinavia, Iceland", "the Norse longhouse: thick walls of turf and stone, a turf roof on two rows of posts, the long fire down the hall, a door in the long side",
         {"walls": {"type": "enclosure", "plan": {"rect": [20.0, 6.0], "chamfer": 1.2}, "thickness": 1.0, "height": 1.5, "openings": [], "faces": {"2": [door(1.1, 1.4, x=-4.0)]}, "at": [[0, 0, 0, 0]]},   # (face 2: the +z long side of a chamfered plan)
          "roof": roof("gable", 6.6, 20.6, 45, 1.5, yaw=PI2, over=0.2, shell=0.4),
          "posts": col(0.15, 3.6, *[[x, 0, z, 0] for x in (-7.5, -4.5, -1.5, 1.5, 4.5, 7.5) for z in (-1.3, 1.3)], sides=6),
          "long fire": fire((0, 0, 0, 0), r=0.5, h=0.4),
          "benches": box(16.0, 0.9, 0.4, (0, 0, -1.9, 0), (0, 0, 1.9, 0))},
         [rule("roof", "roofs/thatch", "green", surface="roof"), rule("walls", "stone/rubble", "stone"), rule(["posts", "benches"], "timber/bark", "oak-grey")])
dwelling("iroquois-longhouse", "Iroquois longhouse", "1100-1800", "the Northeast (Haudenosaunee)", "the longhouse of the Haudenosaunee: a barrel of bent poles sheathed in elm bark, a family's fire every few metres down the middle, doors at both ends",
         {"vault": {"type": "barrel", "width": 6.0, "length": 18.0, "springing": 1.6, "top": 4.6, "head": {"profile": "semicircular", "seg": 8}, "at": [[9.0, 0, 0, PI2]]},   # (a barrel runs from its `at` along its z: turned, toward -x)
          "side walls": box(18.0, 0.12, 1.6, (0, 0, 2.94, 0), (0, 0, -2.94, 0)),
          "ends": {"type": "enclosure", "plan": {"rect": [0.12, 6.0]}, "thickness": 0.12, "height": 1.6, "openings": [], "faces": {"1": [door(1.0, 1.5)], "3": [door(1.0, 1.5)]}, "at": [[-9.0, 0, 0, 0], [9.0, 0, 0, 0]]},
          "fires": fire((-6, 0, 0, 0), (-2, 0, 0, 0), (2, 0, 0, 0), (6, 0, 0, 0)),
          "bunks": box(16.0, 1.2, 0.5, (0, 0, -2.2, 0), (0, 0, 2.2, 0))},
         [rule(["vault", "side walls", "ends"], "timber/boards", "birch"), rule("bunks", "timber/bark", "pine")])
dwelling("stilt-house", "Stilt house", "500-1900", "Southeast Asia (Malay rumah panggung, Thai, Filipino bahay kubo)", "the house on posts: a floor raised two metres clear of the floods and the damp, plank walls, a steep thatched roof with deep eaves, a veranda and a ladder",
         {"posts": col(0.12, 2.1, *[[x, 0, z, 0] for x in (-2.8, -0.9, 0.9, 2.8) for z in (-1.9, 0, 1.9)], sides=6),
          "floor": box(6.0, 4.0, 0.15, (0, 2.0, 0, 0)),
          "veranda": box(6.0, 1.5, 0.12, (0, 2.0, 2.75, 0)),
          "walls": {"type": "enclosure", "plan": {"rect": [6.0, 4.0]}, "thickness": 0.06, "height": 2.4, "openings": {"pattern": "1", "width": 0.8, "sill": 0.8, "springing": 1.6, "head": {"profile": "flat"}},
                    "faces": {"0": [door(0.9, 1.9)]}, "at": [[0, 2.15, 0, 0]]},
          "roof": roof("gable", 4.2, 6.2, 50, 4.55, yaw=PI2, over=0.7, shell=0.2),
          "ladder": {"type": "flight", "steep": True, "run": 0.22, "rise": 0.27, "width": 0.8, "base": 0, "top": 2.12, "landing": 0, "at": [[0.4, 0, 3.5 + 8 * 0.22, PI2]]}},
         [rule("roof", "roofs/thatch", "thatch", surface="roof"), rule(["walls"], "timber/boards", "pine"), rule(["floor", "veranda", "posts", "ladder"], "timber/bark", "oak")])
dwelling("minka", "Minka", "1600-1900", "Japan (Edo farmhouse)", "the Japanese farmhouse: a timber frame on stones, plastered walls and sliding doors, a raised floor of boards beside the earthen floor, a great hipped thatch over all",
         {"raised floor": box(6.0, 7.0, 0.5, (-2.0, 0, 0, 0)),
          "earth floor": box(4.0, 7.0, 0.05, (3.0, 0, 0, 0)),
          "walls": {"type": "enclosure", "plan": {"rect": [10.0, 7.0]}, "thickness": 0.15, "height": 2.7, "openings": [], "faces": {"0": [door(1.8, 2.0, x=2.5), door(1.8, 2.0, x=-1.5)], "2": [{"at": 0, "width": 1.2, "sill": 1.0, "springing": 1.9, "head": {"profile": "flat"}}]}, "at": [[0, 0, 0, 0]]},
          "roof": roof("hip", 7.0, 10.0, 52, 2.7, yaw=PI2, over=0.9, shell=0.45),
          "hearth": fire((-2.0, 0.5, 0, 0), r=0.3, h=0.3)},
         [rule("roof", "roofs/thatch", "thatch", surface="roof"), rule("walls", "stone/plaster", "plaster-white"), rule("raised floor", "timber/boards", "pine"), rule("earth floor", "stone/sand", "earth")])

# ---- COURTYARD HOUSES (the `court` part: wings round an open court) ---------------------------------------------------
def court(rect, depth, storeys, h, roofspec, gate_w, gate_h, slab=0.2):
    return {"type": "court", "glass": False, "plan": {"rect": list(rect)}, "depth": depth, "storeys": storeys, "storeyH": h, "slab": slab,
            "gate": {"face": 0, "width": gate_w, "height": gate_h}, "roof": roofspec, "at": [[0, 0, 0, 0]]}
dwelling("domus", "Domus", "-200-400", "the Roman world", "the Roman town house: rooms round the atrium under a tiled roof sloping in to the open compluvium, the rain falling into the impluvium basin below",
         {"house": court((16.0, 20.0), 5.0, 1, 4.2, {"form": "shed", "pitch": 22}, 1.6, 2.8),
          "impluvium": box(3.0, 3.0, 0.3, (0, 0, 0, 0))},
         [rule("house", "roofs/coppi", "terracotta", surface="roof"), rule("house", "stone/plaster", "plaster-red"), rule("impluvium", "stone/marble", "carrara")])
dwelling("greek-house", "Greek house", "-600--100", "Greece", "the Greek house: plain walls to the street, its rooms round a court with an altar, a tiled roof",
         {"house": court((12.0, 14.0), 4.0, 1, 3.6, {"form": "shed", "pitch": 20}, 1.4, 2.4),
          "altar": box(0.8, 0.8, 0.9, (0, 0, 0, 0))},
         [rule("house", "roofs/coppi", "terracotta", surface="roof"), rule("house", "stone/plaster", "plaster-white"), rule("altar", "stone/marble", "carrara")])
dwelling("courtyard-house", "Courtyard house", "700-1900", "the Islamic world: Damascus, Cairo, Fez", "the courtyard house: blind walls to the lane, two storeys of rooms looking in on a court with its fountain, flat roofs walked on in the evening",
         {"house": court((14.0, 14.0), 4.5, 2, 3.5, {"form": "flat", "pitch": 0}, 1.4, 2.6),
          "fountain": box(1.6, 1.6, 0.5, (0, 0, 0, 0))},
         [rule("house", "stone/plaster", "plaster-ochre"), rule("fountain", "floors/basketweave", "zellige")])
dwelling("siheyuan", "Siheyuan", "1400-1900", "China (Ming and Qing)", "the courtyard house of the north: halls on four sides of a court, grey tiled roofs, the gate at the south-east corner (here a wing's middle)",
         {"house": court((18.0, 22.0), 5.0, 1, 3.6, {"form": "gable", "pitch": 28}, 1.8, 2.6)},
         [rule("house", "roofs/tube tiles", "slate", surface="roof"), rule("house", "stone/brick", "stone")])

# ---- FLAT-ROOFED HOUSES ----------------------------------------------------------------------------------------------
dwelling("egyptian-house", "Egyptian house", "-2000--500", "Egypt", "the mud-brick house of Egypt: small windows high in thick walls, a flat roof with its parapet where the family slept in summer, a stair up to it, a reed shelter on the roof",
         {"walls": {"type": "enclosure", "plan": {"rect": [8.0, 10.0]}, "thickness": 0.5, "height": 3.2, "openings": {"pattern": "2", "width": 0.5, "gap": 2.0, "sill": 2.3, "springing": 2.8, "head": {"profile": "flat"}}, "faces": {"0": [door(1.0, 2.1)]}, "at": [[0, 0, 0, 0]]},
          "roof": roof("flat", 8.0, 10.0, 0, 3.2, over=0.0, thickness=0.3),
          "parapet": {"type": "enclosure", "plan": {"rect": [8.0, 10.0]}, "thickness": 0.15, "height": 0.6, "openings": [], "at": [[0, 3.5, 0, 0]]},
          "shelter posts": col(0.08, 1.9, (-2.5, 3.5, -3.5, 0), (-2.5, 3.5, -1.0, 0), (0.5, 3.5, -3.5, 0), (0.5, 3.5, -1.0, 0), sides=6),
          "shelter roof": box(3.4, 3.0, 0.1, (-1.0, 5.4, -2.25, 0)),
          "stair": {"type": "flight", "run": 0.28, "rise": 0.2, "width": 0.9, "base": 0, "top": 3.5, "landing": 0, "at": [[-4.0, 0, 5.0 - 0.3, PI2]]}},   # (against the -x wall outside: a flight's width lies to its left)
         [rule(["walls", "parapet", "stair"], "stone/plaster", "plaster-ochre"), rule(["shelter roof", "shelter posts"], "roofs/thatch", "straw")])
P_ = {"rect": [12.0, 8.0]}
dwelling("pueblo", "Pueblo", "900-1900", "the Southwest (Ancestral Puebloans, Taos, Acoma)", "the pueblo: rooms of adobe stacked in terraces, each storey set back so its roof is the next one's yard, ladders between them, small doors",
         {"level 0": {"type": "enclosure", "plan": {"rect": [12.0, 8.0]}, "thickness": 0.45, "height": 2.6, "openings": [], "faces": {"0": [door(0.7, 1.4, x=-3.5), door(0.7, 1.4, x=1.0)]}, "at": [[0, 0, 0, 0]]},
          "roof 0": roof("flat", 12.0, 8.0, 0, 2.6, over=0.0, thickness=0.25),
          "level 1": {"type": "enclosure", "plan": {"rect": [8.0, 8.0]}, "thickness": 0.4, "height": 2.4, "openings": [], "faces": {"0": [door(0.7, 1.4)]}, "at": [[2.0, 2.85, 0, 0]]},
          "roof 1": roof("flat", 8.0, 8.0, 0, 5.25, x=2.0, over=0.0, thickness=0.25),
          "level 2": {"type": "enclosure", "plan": {"rect": [4.5, 8.0]}, "thickness": 0.4, "height": 2.2, "openings": [], "faces": {"0": [door(0.7, 1.3)]}, "at": [[3.75, 5.5, 0, 0]]},
          "roof 2": roof("flat", 4.5, 8.0, 0, 7.7, x=3.75, over=0.0, thickness=0.25),
          "ladder 0": {"type": "flight", "steep": True, "run": 0.22, "rise": 0.29, "width": 0.5, "base": 0, "top": 2.85, "landing": 0, "at": [[-4.75, 0, 4.0 + 10 * 0.22, PI2]]},
          "ladder 1": {"type": "flight", "steep": True, "run": 0.22, "rise": 0.29, "width": 0.5, "base": 0, "top": 2.65, "landing": 0, "at": [[-1.25, 2.85, 9 * 0.22 - 2.0, PI2]]}},   # (on roof 0, up the face of level 1 at z = -2 ... its foot 2 m in front of it)
         [rule(["level 0", "level 1", "level 2", "roof 0", "roof 1", "roof 2"], "stone/plaster", "plaster-ochre"), rule(["ladder 0", "ladder 1"], "timber/bark", "pine")])
dwelling("blackhouse", "Blackhouse", "1700-1900", "the Hebrides, the Highlands", "the blackhouse: walls of dry stone two metres thick, rounded at the corners, the thatch sitting on the inner edge roped down with stones, people at one end and the cattle at the other, the peat fire in the middle with no chimney",
         {"walls": {"type": "enclosure", "plan": {"rect": [14.0, 6.5], "chamfer": 1.8}, "thickness": 1.5, "height": 1.8, "openings": [], "faces": {"2": [door(0.9, 1.6, x=-1.0)]}, "at": [[0, 0, 0, 0]]},   # (face 2: the +z long side of a chamfered plan)
          "roof": roof("hip", 3.8, 11.2, 40, 1.8, yaw=PI2, over=0.3, shell=0.35),
          "fire": fire((-2.0, 0, 0, 0), r=0.3, h=0.3)},
         [rule("roof", "roofs/thatch", "thatch-grey", surface="roof"), rule("walls", "stone/rubble", "stone")])


TENT_POLES = {"kind": "item", "name": "Tent poles", "category": "components", "era": "everywhere", "region": "everywhere",
              "_about": "a cone of n poles leaning in from a ring of radius r on the ground to cross at height h, each running on `over` metres past the crossing -- a tipi's lodgepoles, a lavvu's",
              "params": {"n": 12, "r": 2.5, "h": 5.4, "over": 1.0},
              "materials": {"wood": "pine"},
              "parts": [{"id": "pole", "type": "rod", "material": "wood", "r": 0.035, "sides": 5,
                         "from": ["r", 0, 0], "to": ["0 - r * over / sqrt(r * r + h * h)", "h + h * over / sqrt(r * r + h * h)", 0],
                         "around": {"n": "n", "r": 0, "plane": "xz"}}]}


def main():
    for key, (name, era, region, about, parts, rules, params, stone) in DWELLINGS.items():
        for v in parts.values():   # (windows of these times and places are shutters, lattices, paper or a plain hole -- not glass)
            if v.get("type") in ("enclosure", "ring", "court"): v.setdefault("glass", False)
        write(ARCH, "dwellings/" + key, {"name": name, "_about": f"{about.upper()[:1]}{about[1:]} ({region}, {era})", "era": era, "region": region,
                                         "params": {"detail": 4, **(params or {})}, "parts": parts, "build": list(parts)})
        write(FIN, key, {"name": name, "building": "architecture/dwellings/" + key, "_about": f"{name}: as it was built ({region})",
                         "stone": stone or {"color": "#c8b89a", "accent": "#a89878", "pat": "ashlar"}, "rules": rules})
    with open(os.path.join(ROOT, "assets", "items", "components", "tent-poles.json"), "w") as f:
        json.dump(TENT_POLES, f, indent=1); f.write("\n")
    ipath = os.path.join(ROOT, "assets", "index.json")
    index = json.load(open(ipath))
    cats = {c["name"]: c for c in index["categories"]}
    if "Dwellings" not in cats:
        pos = index["categories"].index(cats["Village"]) + 1
        index["categories"].insert(pos, {"name": "Dwellings", "kind": "building", "paths": []})
        cats = {c["name"]: c for c in index["categories"]}
    cats["Dwellings"]["paths"] = ["architecture/dwellings/" + k for k in DWELLINGS]
    fins = cats["Finishes"]["paths"]
    fins += [p for p in ("finishes/" + k for k in DWELLINGS) if p not in fins]
    comps = cats["Items: components"]["paths"]
    if "items/components/tent-poles" not in comps: comps.append("items/components/tent-poles")
    json.dump(index, open(ipath, "w"), indent=2, ensure_ascii=False)
    print(len(DWELLINGS), "dwellings")


if __name__ == "__main__":
    main()
