#!/usr/bin/env python3
"""DWELLINGS (2026-10-02): tents and houses of other times and peoples than the medieval town's -- the knight's
pavilion, the soldier's bell and wedge tents, the marquee, the Roman papilio, the Mongol ger, the Plains tipi, the
Bedouin black tent, the wigwam, the igloo, the Iron Age roundhouse and the crannog, the rondavel and the beehive hut,
the Navajo hogan, the sunken pit house, the Norse and the Iroquois longhouses, the stilt house, the Japanese minka,
the Roman domus, the Greek house, the Arab courtyard house, the Chinese siheyuan, the Egyptian house, the pueblo, the
Hebridean blackhouse, and (2026-10-27) the Russian izba, the Maya house, the Indian village hut and the haveli -- as arch-engine definitions (assets/architecture/dwellings/*.json), each with its finish
(assets/finishes/<name>.json: felt, hide, thatch, adobe, turf, bark), and the "Dwellings" catalogue category.

    python3 tools/archgen/dwellings.py

Round ones have their door at +x (a ring's bay 0), straight ones on their +z face (an enclosure's face 0). A hearth
is a `fire` marker. A period's town (assets/world/periods.json `town.houses`) builds its streets of them, and the
houses it builds of are FURNISHED (`furnish` below): a door marker, beds, a table and its places.
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
    """a cone or a dome down to the ground with a DOORWAY at its foot (+x): the dome's own `door`, a hole cut in it
    (whole faces, jambs, a lintel) -- it was a band under a cap, two parts whose meridians never met"""
    d = cone(r, rise if profile == "trigonal" else r, y, sides, t, profile)
    d["door"] = {"width": door_w, "height": door_h}
    return {name: d}


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
          "pole": col(0.06, 4.9, (0, 0, 0, 0), sides=6),
          "roof": cone(2.66, 2.3, 2.2, 12),
          "valance": ring(2.66, 0.35, 0.03, 12, y=1.85),
          "pennant": box(0.6, 0.02, 0.35, (0.3, 4.45, 0, 0))},
         [rule(["roof", "wall", "door"], "fabrics/stripes", "stripe-madder"), rule(["valance", "pennant"], "fabrics/plain", "or-gules"), rule("pole", "timber/bark", "oak")])
dwelling("bell-tent", "Bell tent", "1300-1900", "Europe", "the soldier's bell tent: a short canvas wall and a tall cone on one pole, eight or ten men to it",
         {**walls_with_door(2.2, 0.7, 0.03, 12, door(0.8, 0.65)),
          "roof": cone(2.2, 2.6, 0.7, 12),
          "pole": col(0.05, 3.4, (0, 0, 0, 0), sides=6)},
         [rule(["roof", "wall", "door"], "fabrics/linen", "canvas"), rule("pole", "timber/bark", "pine")])
dwelling("marquee", "Marquee", "1450-1800", "Europe", "the officers' and the feast's marquee: a long canvas room under a hipped roof on two poles",
         # (the roof's plan is the walls' outline, its eave 15 mm over their heads so the 3 cm sheet takes them in, the
         #  skirt running on down past them; the two poles stand under the ridge's ends and up into the sheet -- the roof
         #  used to stand 25 cm clear of the walls and the poles short of it, everything in the air)
         {"walls": {"type": "enclosure", "plan": {"rect": [6.0, 4.0]}, "thickness": 0.03, "height": 2.0, "openings": [], "faces": {"0": [door(1.6, 1.9)]}, "at": [[0, 0, 0, 0]]},
          "roof": roof("hip", 4.0, 6.0, 35, 2.015, yaw=PI2, over=0.2, shell=0.03),
          "poles": col(0.06, round(2.015 + 2.0 * math.tan(math.radians(35)) - 0.015, 3), (-1.0, 0, 0, 0), (1.0, 0, 0, 0), sides=6)},
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
         [rule("cover", "fabrics/leather", "leather"), rule("poles", "timber/bark", "pine")])
dwelling("bedouin-tent", "Black tent", "-1000-1900", "Arabia, the Sahara, the Levant", "the Bedouin beit al-sha'ar, the house of hair: woven goat-hair strips over a low ridge of poles, the back wall pegged down, the front open to the shade",
         {"poles": col(0.05, 2.25, (-3, 0, 0, 0), (0, 0, 0, 0), (3, 0, 0, 0), sides=6),
          "back wall": box(9.0, 0.03, 1.7, (0, 0, -2.5, 0)),
          "end curtains": box(0.03, 5.0, 1.7, (-4.5, 0, 0, 0), (4.5, 0, 0, 0)),
          "roof": roof("gable", 5.0, 9.0, 12, 1.7, yaw=PI2, over=0.0, shell=0.03),
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
          # (the tunnel from 3.2 m out back to 1.4, into the dome's wall round the door; its side walls under the barrel's
          #  springing along the same stretch -- they stood 0.8 m out past its mouth, and it ran on into the house)
          "tunnel": {"type": "barrel", "width": 0.9, "length": 1.8, "springing": 0.35, "top": 0.8, "head": {"profile": "semicircular", "seg": 6}, "at": [[3.2, 0, 0, PI2]]},
          "tunnel walls": box(1.8, 0.25, 0.35, (2.3, 0, 0.55, 0), (2.3, 0, -0.55, 0))},
         [rule(["dome", "tunnel", "tunnel walls"], "stone/ashlar", "plaster-white")])
dwelling("roundhouse", "Roundhouse", "-800-100", "Iron Age Britain and Gaul", "the Iron Age roundhouse: a wattle-and-daub wall in a ring of posts, a steep thatched cone down over it, the door toward the sunrise, the hearth in the middle",
         {**walls_with_door(4.0, 1.6, 0.25, 16, door(1.1, 1.5)),
          "roof": cone(4.6, 4.6, 0, 16, t=0.3, seat="wall"),   # (seated: on the wall head, wherever that puts it)
          "floor": ring(3.75, 0.05, 3.7, 16),
          "posts": col(0.12, 3.2, *ringpos(8, 2.6), sides=6),
          "hearth": fire((0, 0.05, 0, 0))},
         [rule("roof", "roofs/thatch", "thatch", surface="roof"), rule(["wall", "door"], "stone/plaster", "plaster-ochre"), rule("floor", "stone/sand", "earth"), rule("posts", "timber/bark", "oak")])
CR = 3.5
dwelling("crannog", "Crannog", "-800-1600", "Ireland and Scotland", "the crannog: a roundhouse on a timber platform out in a loch, on piles driven into the bed, a walkway to the shore",
         {"piles": col(0.12, 1.6, *ringpos(14, 5.0), sides=6),
          "platform": ring(5.5, 0.25, 5.45, 20, y=1.5),
          "walkway piles": col(0.1, 1.6, *[[x, 0, z, 0] for x in (7.5, 10.5, 13.5) for z in (-0.5, 0.5)], sides=6),
          "walkway": box(10.0, 1.2, 0.15, (10.5, 1.6, 0, 0)),
          **{k: {**v, "place": [[0, 1.75, 0, 0]]} for k, v in walls_with_door(CR, 1.5, 0.2, 14, door(1.0, 1.4)).items()},
          "roof": cone(CR + 0.6, 4.0, 0, 14, t=0.3, seat="wall"),
          "hearth": fire((0, 1.75, 0, 0))},
         [rule("roof", "roofs/thatch", "thatch", surface="roof"), rule(["wall", "door"], "stone/plaster", "plaster-ochre"),
          rule(["platform", "piles", "walkway", "walkway piles"], "timber/boards", "oak-grey")])
dwelling("rondavel", "Rondavel", "1000-1900", "Southern Africa", "the rondavel: a round wall of mud brick, plastered and limewashed, a thatched cone on top, a door and two small windows",
         {**walls_with_door(2.8, 2.0, 0.25, 12, door(0.9, 1.8), windows={3: {"width": 0.6, "sill": 0.9, "springing": 1.5, "head": {"profile": "flat"}}, 9: {"width": 0.6, "sill": 0.9, "springing": 1.5, "head": {"profile": "flat"}}}),
          "roof": cone(3.3, 2.6, 0, 12, t=0.2, seat="wall"),
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
          "roof": cone(3.6, 1.5, 0, 8, t=0.45, profile="segmental", oculus=0.35, seat="walls"),   # (its soffit out past the walls: the cribbed logs start on their heads)
          "hearth": fire((0, 0, 0, 0))},
         [rule("roof", "stone/sand", "earth"), rule("walls", "timber/boards", "oak-grey")])

# ---- LONG HOUSES -------------------------------------------------------------------------------------------------
dwelling("pit-house", "Pit house", "400-1100", "Anglo-Saxon England, the Slavic lands (Grubenhaus)", "the sunken-floored house: a pit half a metre deep lined with planks, a gable of thatch down almost to the ground over it",
         {"pit floor": box(4.0, 3.0, 0.05, (0, -0.55, 0, 0)),
          # (the lining open at the +x end, face 1, where the steps come up through it)
          "pit lining": {"type": "enclosure", "plan": {"rect": [4.4, 3.4]}, "thickness": 0.2, "height": 0.75, "openings": [],
                         "faces": {"1": [{"at": -0.65, "width": 0.9, "sill": 0, "springing": 0.75, "head": {"profile": "flat"}, "glass": False}]}, "at": [[0, -0.55, 0, 0]]},
          "roof": roof("gable", 4.8, 5.0, 52, 0.2, yaw=PI2, over=0.3, shell=0.25, open="front"),
          # (from the pit floor up through the lining's open end, the top tread on its outer face and the ground beyond:
          #  it used to start outside the pit, under the ground, and climb inward to the lining's top)
          "steps": {"type": "flight", "run": 0.28, "rise": 0.18, "width": 0.9, "base": 0, "top": 0.55, "landing": 0, "at": [[2.2 - 3 * 0.28, -0.55, 1.1, 0]],   # (beside the ridge post at the gable end)
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
         {"side walls": box(18.0, 0.12, 1.6, (0, 0, 2.94, 0), (0, 0, -2.94, 0)),
          # (each end a WALL across the barrel's mouth with its door: its face on the end line, its bark sheathing inside)
          "ends": {"type": "wall", "width": 6.0, "height": 1.6, "thickness": 0.12, "openings": [door(1.0, 1.5, x=3.0)], "at": [[-9.0, 0, 0, -PI2], [9.0, 0, 0, PI2]]},
          "vault": {"type": "barrel", "light": True, "width": 6.0, "length": 18.0, "springing": 1.6, "top": 4.6, "head": {"profile": "semicircular", "seg": 8}, "at": [[9.0, 0, 0, PI2]]},   # (a barrel runs from its `at` along its z: turned, toward -x)
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
          # (on roof 0's terrace, up level 1's west face -- x = -2, where its rooms begin -- onto roof 1; it used to climb
          #  along z inside level 1, under its roof)
          "ladder 1": {"type": "flight", "steep": True, "run": 0.22, "rise": 0.29, "width": 0.5, "base": 0, "top": 2.65, "landing": 0, "at": [[-2.0 - 9 * 0.22, 2.85, 1.5, 0]]}},
         [rule(["level 0", "level 1", "level 2", "roof 0", "roof 1", "roof 2"], "stone/plaster", "plaster-ochre"), rule(["ladder 0", "ladder 1"], "timber/bark", "pine")])
dwelling("blackhouse", "Blackhouse", "1700-1900", "the Hebrides, the Highlands", "the blackhouse: walls of dry stone two metres thick, rounded at the corners, the thatch sitting on the inner edge roped down with stones, people at one end and the cattle at the other, the peat fire in the middle with no chimney",
         {"walls": {"type": "enclosure", "plan": {"rect": [14.0, 6.5], "chamfer": 1.8}, "thickness": 1.5, "height": 1.8, "openings": [], "faces": {"2": [door(0.9, 1.6, x=-1.0)]}, "at": [[0, 0, 0, 0]]},   # (face 2: the +z long side of a chamfered plan)
          "roof": roof("hip", 3.8, 11.2, 40, 1.8, yaw=PI2, over=0.3, shell=0.35),
          "fire": fire((-2.0, 0, 0, 0), r=0.3, h=0.3)},
         [rule("roof", "roofs/thatch", "thatch-grey", surface="roof"), rule("walls", "stone/rubble", "stone")])

# ---- INDIA, THE MAYA, RUSSIA (the towns of the periods of the Kandariya and the Taj, of Chichen Itza, of St Basil's) --
def win(x, w, sill, top):
    return {"at": x, "width": w, "sill": sill, "springing": top, "head": {"profile": "flat"}}
dwelling("izba", "Izba", "900-1900", "Russia", "the Russian izba: a box of round logs notched at the corners, its gable to the street with three small windows in carved and painted frames, a plank roof, the great whitewashed stove inside, its flue through the roof",
         {"walls": {"type": "enclosure", "plan": {"rect": [6.4, 7.6]}, "thickness": 0.24, "height": 2.9, "openings": [], "faces": {"0": [door(0.9, 1.9, x=-2.1), win(-0.3, 0.6, 1.0, 1.75), win(1.0, 0.6, 1.0, 1.75), win(2.3, 0.6, 1.0, 1.75)], "2": [win(0, 0.5, 1.1, 1.7)]}, "at": [[0, 0, 0, 0]]},
          "log ends": col(0.13, 2.9, *[(sx * 3.32, 0, sz * 3.92, 0) for sx in (-1, 1) for sz in (-1, 1)], sides=8),
          # (the nalichniki: jambs and a sill round each window, a carved head over it -- round the hole, not over it)
          "frames": box(0.1, 0.06, 0.85, *[(x + dx, 0.95, 3.83, 0) for x in (-0.3, 1.0, 2.3) for dx in (-0.35, 0.35)]),
          "frame sills": box(0.9, 0.12, 0.08, *[(x, 0.9, 3.84, 0) for x in (-0.3, 1.0, 2.3)]),
          "frame heads": box(1.0, 0.1, 0.32, *[(x, 1.76, 3.85, 0) for x in (-0.3, 1.0, 2.3)]),
          "roof": roof("gable", 6.4, 7.6, 42, 2.9, over=0.45, shell=0.12),
          "stove": box(1.8, 2.0, 1.6, (-1.9, 0, -2.4, 0)),
          "chimney": box(0.55, 0.55, 4.0, (-1.9, 1.6, -2.4, 0))},
         [rule("roof", "timber/planks", "oak-grey", surface="roof"), rule(["walls", "log ends"], "timber/logs", "oak-grey"), rule("roof", "timber/weatherboard", "oak-grey"),
          rule(["frames", "frame sills"], "materials/paint", "plaster-white"), rule("frame heads", "painted/russian floral", "russian"), rule("stove", "stone/plaster", "plaster-white"), rule("chimney", "stone/brick", "brick")])
dwelling("maya-house", "Maya house", "-1000-1900", "Yucatan, Guatemala (the Maya na)", "the Maya na: a long house with rounded ends, walls of poles daubed with mud and limewashed, on a low platform of stones, a tall steep roof of palm thatch, the three hearth stones inside",
         {"platform": box(8.6, 5.6, 0.45, (0, 0, 0, 0)),
          "walls": {"type": "enclosure", "plan": {"rect": [7.2, 4.2], "chamfer": 1.3}, "thickness": 0.18, "height": 2.3, "openings": [], "faces": {"2": [door(0.9, 1.8)]}, "at": [[0, 0.45, 0, 0]]},   # (face 2: the +z long side of a chamfered plan)
          "roof": roof("hip", 4.2, 7.2, 62, 2.75, yaw=PI2, over=0.35, shell=0.3, chamfer=1.3),
          "hearth": fire((-1.8, 0.45, -0.6, 0), r=0.22, h=0.25)},
         [rule("roof", "roofs/thatch", "thatch"), rule("walls", "stone/plaster", "plaster-white"), rule("platform", "stone/rubble", "maya")])
dwelling("indian-hut", "Village hut", "-500-1900", "India", "the Indian village house: mud walls on a raised plinth, plastered and limewashed, a low door and small windows, a hipped thatch, the veranda posts in front, the clay hearth (chulha) inside",
         {"plinth": box(6.4, 5.8, 0.4, (0, 0, 0.3, 0)),
          "walls": {"type": "enclosure", "plan": {"rect": [5.6, 4.2]}, "thickness": 0.35, "height": 2.3, "openings": [], "faces": {"0": [door(0.9, 1.75, x=-0.8), win(1.4, 0.5, 1.0, 1.6)], "1": [win(0, 0.5, 1.1, 1.6)]}, "at": [[0, 0.4, 0, 0]]},
          "roof": roof("hip", 5.6, 4.2, 32, 2.7, over=1.0, shell=0.25),
          "posts": col(0.07, 1.6, (-2.6, 0.4, 2.9, 0), (0, 0.4, 2.9, 0), (2.6, 0.4, 2.9, 0), sides=6),   # (up to the eave's underside)
          "chulha": fire((1.6, 0.4, -1.0, 0), r=0.2, h=0.25)},
         [rule("roof", "roofs/thatch", "thatch"), rule("walls", "stone/plaster", "earth", below=1.2), rule("walls", "stone/plaster", "plaster-ochre"),
          rule("plinth", "stone/plaster", "earth"), rule("posts", "timber/bark", "chestnut")])
dwelling("haveli", "Haveli", "1400-1900", "North India (Rajasthan, Gujarat, Delhi)", "the haveli: a merchant's house of two storeys round an open court, blind and plain to the lane but for its carved oriels (jharokhas) over the gate, flat roofs walked on in the evening, the tulsi altar in the court",
         {"house": court((15.0, 15.0), 4.2, 2, 3.4, {"form": "flat", "pitch": 0}, 1.6, 2.8),
          "jharokhas": box(1.8, 0.7, 2.2, (-3.6, 4.2, 7.85, 0), (3.6, 4.2, 7.85, 0)),   # (each over an upper window of the front: court's row, every 3.6m)
          "jharokha brackets": box(0.25, 0.6, 0.5, *[(x, 3.7, 7.8, 0) for x in (-4.3, -2.9, 2.9, 4.3)]),
          "jharokha roofs": roof("hip", 2.2, 1.0, 30, 6.4, over=0.05, x=-3.6, z=7.9),
          "jharokha roofs b": roof("hip", 2.2, 1.0, 30, 6.4, over=0.05, x=3.6, z=7.9),
          "tulsi altar": box(0.9, 0.9, 0.9, (0, 0, 0, 0))},
         [rule("jharokhas", "panels/jali", "red-sandstone", side="out"), rule(["jharokhas", "jharokha brackets", "jharokha roofs", "jharokha roofs b"], "stone/ashlar fine", "red-sandstone"),
          rule("house", "stone/plaster", "plaster-rose"), rule("tulsi altar", "stone/plaster", "plaster-white")])


# ---- FURNISHED (2026-10-27): the houses the period towns are built of, lived in -- a DOOR marker in the doorway (its
# panel, the way in and out: village-life.js), beds of the time and place, a table or a tray and seats with a guest's
# place at each (the town's inn is one of these houses: its guests eat there), the chest, the hearth. Whatever the
# villagers use -- a bed, a place at table -- stands in the room the door opens into, in a straight line from a step
# inside it (they walk straight from there: a court house's front wing, beside the gate's passage); the rest of the
# house is furnished for the look (`markers` False). Coordinates in the house's frame: the door's face +z.
def thing(path, x, y, z, yaw=0, seed=1, params=None, **k):
    return {"type": "item", "item": "items/furniture/" + path, "at": [[x, y, z, round(yaw, 7)]], "seed": seed, **({"params": params} if params else {}), **k}


FACE = {"+x": 0, "-x": round(math.pi, 7), "-z": PI2, "+z": -PI2}   # (a spot's heading: 0 faces +x, pi/2 -z)
YAW = {"+z": 0, "+x": PI2, "-z": math.pi, "-x": -PI2}             # (a chair's turn to face that way: its front is its +z)


def seated(name, path, x, y, z, faces, top, seed=1, params=None):
    """a chair or a stool facing `faces`, and a sitting place on it (a guest's, at the inn)"""
    return {name: thing(path, x, y, z, YAW[faces], seed, params, markers=["seat"]),
            name + " place": {"type": "marker", "role": "spot", "at": [[x, round(y + top, 3), z, 0]], "data": {"pose": "sit", "face": FACE[faces]}}}


def doorway(x, y, z, w, h, arch=False):
    """the door marker: its panel in the opening (as wide as it, to its springing, under a round head if it has one)"""
    return {"door": {"type": "marker", "role": "door", "at": [[x, y, z, 0]],
                     "data": {"w": w, "h": h, **({"spring": round(h - w / 2, 3), "head": {"profile": "semicircular"}} if arch else {})}}}


def furnish(key, parts, rules=()):
    DWELLINGS[key][4].update(parts)
    DWELLINGS[key][5].extend(rules)


def court_door(L, gate_w, gate_h, t=0.9):   # (a court's gate: the middle of its +z face, in the outer wall)
    return doorway(0, 0, round(L / 2 - t / 2, 3), gate_w, gate_h, arch=True)


def several(part, *places):   # (one item at several places)
    return {**part, "at": [[x, y, z, round(a, 7)] for x, y, z, a in places]}


# the domus: the front wing (z 5.9..9.1) a cubiculum west of the fauces -- two lecti, heads to the wall -- and a
# popina's table east, stools round it; the triclinium in the back wing, three couches round its table
furnish("domus", {**court_door(20.0, 1.6, 2.8),
    "bed 1": thing("roman-couch", -6.0, 0, 6.6, 0, seed=1), "bed 2": thing("roman-couch", -6.0, 0, 8.5, 0, seed=2),
    "table": thing("roman-table", 4.6, 0, 7.5, 0, seed=3),
    **seated("stool 1", "stool", 3.85, 0, 7.5, "+x", 0.44, 1, {"h": 0.44}), **seated("stool 2", "stool", 5.35, 0, 7.5, "-x", 0.44, 2, {"h": 0.44}),
    **seated("stool 3", "stool", 4.6, 0, 6.75, "+z", 0.44, 3, {"h": 0.44}), **seated("stool 4", "stool", 4.6, 0, 8.25, "-z", 0.44, 4, {"h": 0.44}),
    "triclinium table": thing("roman-table", 0, 0, -7.3, 0, seed=5),
    "triclinium": several(thing("roman-couch", 0, 0, 0, 0, seed=6, markers=False), (0, 0, -8.55, 0), (-1.55, 0, -7.0, -PI2), (1.55, 0, -7.0, PI2))})
# the Greek house: the front wing (z 3.9..6.1) a kline and a pallet west of the passage, a table and klismoi east
furnish("greek-house", {**court_door(14.0, 1.4, 2.4),
    "bed 1": thing("roman-couch", -4.05, 0, 5.6, 0, seed=1), "bed 2": thing("pallet", -4.1, 0, 4.4, 0, seed=2),
    "table": thing("roman-table", 3.4, 0, 5.0, 0, seed=3, params={"r": 0.36}),
    **seated("chair 1", "klismos", 2.65, 0, 5.0, "+x", 0.5, 1), **seated("chair 2", "klismos", 4.15, 0, 5.0, "-x", 0.5, 2),
    **seated("stool", "stool", 3.4, 0, 4.3, "+z", 0.44, 3, {"h": 0.44})})
# the courtyard house: the front wing (z 3.4..6.1) the family's mattresses west; east the guests' room: a divan along
# either wall, the tray between them (the divans' own places); upstairs another
furnish("courtyard-house", {**court_door(14.0, 1.4, 2.6),
    "bed 1": thing("pallet", -5.1, 0, 3.95, 0, seed=1), "bed 2": thing("pallet", -5.1, 0, 5.6, 0, seed=2),
    "divan 1": thing("divan", 4.2, 0, 5.68, math.pi, seed=3, params={"L": 2.0}), "divan 2": thing("divan", 4.2, 0, 3.82, 0, seed=4, params={"L": 2.0}),
    "tray": thing("low-table", 4.2, 0, 4.75, 0, seed=5, params={"r": 0.42}),
    "upper divan": thing("divan", 4.0, 3.5, -5.65, 0, seed=6, markers=False), "upper tray": thing("low-table", 4.0, 3.5, -4.6, 0, seed=7)})
# the siheyuan: the front wing (z 6.9..10.1) two canopy beds west, a table and horseshoe chairs east; the main hall
# across the court (the back wing) its altar table against the wall, cabinets either side, chairs for the elders
furnish("siheyuan", {**court_door(22.0, 1.8, 2.6),
    "bed 1": thing("chinese-bed", -7.0, 0, 7.6, 0, seed=1), "bed 2": thing("chinese-bed", -7.0, 0, 9.4, 0, seed=2),
    "table": thing("plain-table", 5.2, 0, 8.5, 0, seed=3, materials={"wood": "lacquer-red"}),
    **seated("chair 1", "horseshoe-chair", 4.7, 0, 7.6, "+z", 0.5, 1), **seated("chair 2", "horseshoe-chair", 5.7, 0, 7.6, "+z", 0.5, 2),
    **seated("chair 3", "horseshoe-chair", 4.7, 0, 9.4, "-z", 0.5, 3), **seated("chair 4", "horseshoe-chair", 5.7, 0, 9.4, "-z", 0.5, 4),
    "screen": thing("folding-screen", -3.6, 0, 7.0, 0, seed=5),
    "hall altar table": thing("altar-table", 0, 0, -9.8, 0, seed=6),
    "hall cabinets": several(thing("chinese-cabinet", 0, 0, 0, 0, seed=7), (-3.0, 0, -9.82, 0), (3.0, 0, -9.82, 0)),
    "hall chairs": several(thing("horseshoe-chair", 0, 0, 0, 0, seed=8, markers=False), (-1.0, 0, -8.6, 0), (1.0, 0, -8.6, 0))})
# the haveli: the front wing (z 4.2..6.6) two charpais west; east a brass tray on its stand, stools round it
furnish("haveli", {**court_door(15.0, 1.6, 2.8),
    "bed 1": thing("charpai", -5.6, 0, 4.75, 0, seed=1), "bed 2": thing("charpai", -5.6, 0, 6.05, 0, seed=2),
    "tray": thing("low-table", 4.5, 0, 5.4, 0, seed=3, params={"r": 0.42}),
    **seated("stool 1", "stool", 3.7, 0, 5.4, "+x", 0.4, 1, {"h": 0.4}), **seated("stool 2", "stool", 5.3, 0, 5.4, "-x", 0.4, 2, {"h": 0.4}),
    **seated("stool 3", "stool", 4.5, 0, 4.6, "+z", 0.4, 3, {"h": 0.4}), **seated("stool 4", "stool", 4.5, 0, 6.2, "-z", 0.4, 4, {"h": 0.4}),
    "upper charpai": thing("charpai", 3.6, 3.4, -5.45, 0, seed=5, markers=False)})
# the Egyptian house: two beds, heads to the side walls; stools round a table at the back of the hall (z -4.5..4.5)
furnish("egyptian-house", {**doorway(0, 0, 4.75, 1.0, 2.1),
    "bed 1": thing("egyptian-bed", -2.5, 0, 1.6, 0, seed=1), "bed 2": thing("egyptian-bed", 2.5, 0, 1.6, math.pi, seed=2),
    "table": thing("plain-table", 0, 0, -2.2, 0, seed=3, materials={"wood": "cedar"}),
    **seated("stool 1", "stool", -0.45, 0, -1.4, "-z", 0.44, 1, {"h": 0.44}), **seated("stool 2", "stool", 0.45, 0, -1.4, "-z", 0.44, 2, {"h": 0.44}),
    **seated("stool 3", "stool", -0.45, 0, -3.0, "+z", 0.44, 3, {"h": 0.44}), **seated("stool 4", "stool", 0.45, 0, -3.0, "+z", 0.44, 4, {"h": 0.44})})
# the izba: sleeping benches along the back and east walls, a pallet on each; the table in the beautiful corner
# (diagonal to the stove), a bench either side of it (the table's own places); a chest by the door
furnish("izba", {**doorway(-2.1, 0, 3.68, 0.9, 1.9),
    "sleeping benches": box(0.9, 2.0, 0.45, (2.5, 0, -2.5, 0), (0.55, 0, -3.1, PI2)),
    "bed 1": thing("pallet", 2.5, 0.45, -2.5, -PI2, seed=1), "bed 2": thing("pallet", 0.55, 0.45, -3.1, 0, seed=2),
    "table": thing("kitchen-table", 1.6, 0, 2.3, 0, seed=3, params={"L": 1.5}),
    "benches": several(thing("bench", 0, 0, 0, 0, seed=4, params={"L": 1.5}, markers=["seat"]), (1.6, 0, 2.93, math.pi), (1.6, 0, 1.67, 0)),
    "chest": thing("plank-chest", -2.7, 0, 0.6, PI2, seed=5)},
    [rule("sleeping benches", "timber/planks", "oak-grey")])
# the Maya house: two hammocks slung east of the door, the hearth west with stools round it
furnish("maya-house", {**doorway(0, 0.45, 2.01, 0.9, 1.8),
    "bed 1": thing("hammock", 1.8, 0.45, -0.5, 0, seed=1), "bed 2": thing("hammock", 1.8, 0.45, 0.7, 0, seed=2),
    **seated("stool 1", "stool", -1.0, 0.45, -0.6, "-x", 0.4, 1, {"h": 0.4}), **seated("stool 2", "stool", -1.8, 0.45, 0.25, "-z", 0.4, 2, {"h": 0.4}),
    **seated("stool 3", "stool", -2.6, 0.45, -0.6, "+x", 0.4, 3, {"h": 0.4})})
# the village hut: a charpai along the west wall, head to the back; a tray and two stools by the window
furnish("indian-hut", {**doorway(-0.8, 0.4, 1.925, 0.9, 1.75),
    "bed": thing("charpai", -1.95, 0.4, -0.75, -PI2, seed=1),
    "tray": thing("low-table", 1.4, 0.4, 0.8, 0, seed=2, params={"r": 0.4}),
    **seated("stool 1", "stool", 0.65, 0.4, 0.8, "+x", 0.4, 1, {"h": 0.4}), **seated("stool 2", "stool", 2.15, 0.4, 0.8, "-x", 0.4, 2, {"h": 0.4})})


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
