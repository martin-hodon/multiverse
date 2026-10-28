# HIMEJI CASTLE (Himeji-jo), Hyogo (Ikeda Terumasa, 1601-1609): the keep complex on the top of Himeyama -- the great
# keep (Dai-tenshu) and three small keeps (the East, the Inui and the West Ko-tenshu) joined by two-storey corridor
# turrets (watari-yagura) round a small court, the whole on one stone base (ishigaki) whose faces curve out toward the
# foot -- the fan slope (ogi-kobai).
#   The KEEPS are `tiered` parts (tiered.js): storeys stacked one inside the other, a skirt roof round each, the
#   crowning hip-and-gable roof (irimoya), the gables set on the skirts -- the cusped kara-hafu, the triangular chidori-
#   hafu, the great irimoya gables -- after the Japanese Wikipedia's account of the great keep, storey by storey; its
#   floors in ken (1 ken = 1.97m): the first floor 13 x 10 ken, the second as the first (here a little set in, so that
#   the first roof is a skirt), the third 11 x 8, the fourth and fifth 9 x 6 (the fourth hidden behind the third roof's
#   gables: no skirt of its own), the sixth 7 x 5; 31.5m from the stone base's top to the ridge.
#   The STONE BASE is a prism with a `batter`: its plan the top, carried out toward the foot as the square of the depth
#   (power 2: upright under the keeps, flaring at the ground). The court on it is walked; a stair climbs its west face.
#   The WATARI-YAGURA run from keep to keep, each a `tiered` of two floors under one hip-and-gable roof.
#   East is +x, south is +z; the great keep stands at the court's south-east corner. Numbers are worked here and
#   written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
Q = math.pi / 2
r4 = lambda v: round(v, 4)
KEN = 1.97

# ---- the stone base ------------------------------------------------------------------------------------------
HB = 14.85                               # the ishigaki under the great keep
BATTER, POWER = 4.5, 2                   # how far the foot reaches out beyond the top, and the curve
# the keeps' places: the great keep at the court's south-east corner, the West keep west of it, the Inui at the north-
# west, the East keep north of the great keep (the court between them)
MAIN = (0.0, 0.0)
WEST = (-38.0, 2.0)
INUI = (-38.0, -34.0)
EAST = (2.0, -34.0)
# the base's top: round all four keeps and the corridors between, the keeps' walls at its edge
X0, X1, Z0, Z1 = -46.6, 13.4, -41.1, 10.45
add("ishigaki", {"type": "prism", "plan": {"points": [[X0, Z0], [X1, Z0], [X1, Z1], [X0, Z1]]}, "height": HB,
                 "batter": {"out": BATTER, "power": POWER, "steps": 10}, "walked": True,
                 "_about": "the stone base: its top the court's floor, its faces carried out toward the foot as the square of the depth (the fan slope)"})

# the approach: a stair straight up the west face to the court, two flights with a landing between, carried on their
# own masonry over the stone's curve (which falls away under them), arriving at the base's edge between the West and
# the Inui keep, before the gate through the corridor turret between them (watari ha)
RISE, RUN, FW, LAND = .19, .3, 2.6, 2.0
ZA = -9.3                                # the stair's middle line, and the gate's
n1 = round(HB / 2 / RISE)
y1 = r4(n1 * RISE)
n2 = round((HB - y1) / RISE)
L1, L2 = n1 * RUN, n2 * RUN
# (climbing east, yaw 0: a flight lies over z -width .. 0 from where it is placed)
add("stair upper", {"type": "flight", "width": FW, "run": RUN, "top": HB, "rise": RISE, "base": y1, "ground": 0, "landing": 0,
                    "at": [[r4(X0 - L2), 0, r4(ZA + FW / 2), 0]]})
add("stair landing", {"type": "prism", "plan": {"rect": [LAND, FW]}, "height": y1, "walked": True, "at": [[r4(X0 - L2 - LAND / 2), 0, ZA, 0]]})
add("stair lower", {"type": "flight", "width": FW, "run": RUN, "top": y1, "rise": RISE, "base": 0, "landing": 0,
                    "at": [[r4(X0 - L2 - LAND - L1), 0, r4(ZA + FW / 2), 0]]})

# ---- the keeps -----------------------------------------------------------------------------------------------
WIN = {"every": 2.0, "width": .9, "end": 1.2, "sill": 1.0, "springing": 2.0, "head": {"profile": "flat"}}
ROOF = {"pitch": 28, "overhang": 1.6, "lo": .45, "hi": 1.1, "upturn": .35, "flare": .25}

def keep(name, at, storeys, door, top=None, about=None, **kw):
    d = {"type": "tiered", "storeys": storeys, "wall": {"t": .45}, "windows": WIN, "roof": ROOF, "door": door,
         "top": top or {"pitch": 36, "hipH": .6}, "at": [[r4(at[0]), HB, r4(at[1]), 0]], **kw}
    if about: d["_about"] = about
    add(name, d)

k = lambda v: r4(v * KEN)
keep("great keep", MAIN, [
    {"w": k(13), "l": k(10), "h": 5.2, "gables": [{"side": "e", "kind": "kara", "width": 5.0}]},
    {"w": k(12.6), "l": k(9.6), "h": 5.0, "gables": [{"side": "s", "kind": "kara", "width": 5.0},
                                                 {"side": "e", "kind": "irimoya", "width": 9.0}, {"side": "w", "kind": "irimoya", "width": 9.0}]},
    {"w": k(11), "l": k(8), "h": 4.8, "gables": [{"side": "s", "kind": "irimoya", "width": 5.6, "at": -4.2}, {"side": "s", "kind": "irimoya", "width": 5.6, "at": 4.2},
                                             {"side": "n", "kind": "irimoya", "width": 5.6, "at": -4.2}, {"side": "n", "kind": "irimoya", "width": 5.6, "at": 4.2}]},
    {"w": k(9), "l": k(6), "h": 3.4, "roof": False, "windows": False},
    {"w": k(9), "l": k(6), "h": 3.6, "gables": [{"side": "s", "kind": "chidori", "width": 5.0}, {"side": "n", "kind": "chidori", "width": 5.0},
                                            {"side": "e", "kind": "kara", "width": 4.0}, {"side": "w", "kind": "kara", "width": 4.0}]},
    {"w": k(7), "l": k(5), "h": 4.2, "gables": [{"side": "s", "kind": "kara", "width": 4.0}, {"side": "n", "kind": "kara", "width": 4.0}]},
], {"side": "n", "width": 1.8, "height": 2.4, "at": -8.0},
    about="the great keep: five roofs outside, six floors within; the kara-hafu on the first roof's east face, the second's on its south "
          "with great irimoya gables east and west, twin gables south and north on the third, chidori and kara on the fourth, kara on the "
          "fifth under the crowning hip-and-gable roof, its gables to east and west")
keep("west keep", WEST, [
    {"w": 16.0, "l": 13.0, "h": 4.6, "gables": [{"side": "s", "kind": "chidori", "width": 4.5}]},
    {"w": 13.0, "l": 10.0, "h": 4.2, "gables": [{"side": "s", "kind": "kara", "width": 3.6}]},
    {"w": 10.0, "l": 8.0, "h": 4.0},
], {"side": "n", "width": 1.6, "height": 2.3, "at": 6.0}, top={"pitch": 36, "hipH": .5}, about="the West small keep: three storeys")
keep("inui keep", INUI, [
    {"w": 16.0, "l": 13.0, "h": 4.6, "gables": [{"side": "w", "kind": "chidori", "width": 4.5}, {"side": "n", "kind": "chidori", "width": 4.5}]},
    {"w": 13.0, "l": 10.0, "h": 3.6, "roof": False, "windows": False},
    {"w": 13.0, "l": 10.0, "h": 3.6, "gables": [{"side": "n", "kind": "kara", "width": 3.6}]},
    {"w": 10.0, "l": 8.0, "h": 4.0},
], {"side": "s", "width": 1.6, "height": 2.3, "at": 6.0}, top={"pitch": 36, "hipH": .5}, about="the Inui (north-west) small keep: three storeys outside, four floors within")
keep("east keep", EAST, [
    {"w": 13.0, "l": 11.0, "h": 4.4, "gables": [{"side": "e", "kind": "chidori", "width": 4.0}]},
    {"w": 10.0, "l": 8.5, "h": 4.0},
    {"w": 8.0, "l": 6.5, "h": 3.8},
], {"side": "s", "width": 1.6, "height": 2.3, "at": -5.2}, top={"pitch": 36, "hipH": .5}, about="the East small keep: three storeys")

# ---- the watari-yagura: two floors under one roof, from keep to keep -------------------------------------------
WY = 8.0                                 # their depth
def watari(name, a, b, along_x, half_a, half_b, doors=()):
    # from the face of keep a to the face of keep b, a little into each
    if along_x:
        x0, x1 = sorted((a[0], b[0]))
        ha, hb = (half_a, half_b) if a[0] < b[0] else (half_b, half_a)
        x0, x1 = x0 + ha - .3, x1 - hb + .3
        c, L = ((x0 + x1) / 2, a[1]), x1 - x0
        st = [{"w": r4(L), "l": WY, "h": 3.8, "roof": False}, {"w": r4(L), "l": WY, "h": 3.4}]
    else:
        z0, z1 = sorted((a[1], b[1]))
        ha, hb = (half_a, half_b) if a[1] < b[1] else (half_b, half_a)
        z0, z1 = z0 + ha - .3, z1 - hb + .3
        c, L = (a[0], (z0 + z1) / 2), z1 - z0
        st = [{"w": WY, "l": r4(L), "h": 3.8, "roof": False}, {"w": WY, "l": r4(L), "h": 3.4}]
    add(name, {"type": "tiered", "storeys": st, "wall": {"t": .45}, "windows": WIN, "roof": ROOF, "top": {"pitch": 32, "hipH": .5},
               **({"door": [{**d, "at": r4(d["at"] - (c[1] if d["side"] in "ew" else c[0]))} for d in doors]} if doors else {}), "at": [[r4(c[0]), HB, r4(c[1]), 0]]})
watari("watari ro", WEST, MAIN, True, 8.0, k(13) / 2)     # great keep -- West keep
watari("watari ha", INUI, WEST, False, 6.5, 6.5,          # West keep -- Inui keep, the gate through it
       [{"side": "w", "at": ZA, "width": 2.4, "height": 2.8}, {"side": "e", "at": ZA, "width": 2.4, "height": 2.8}])
watari("watari ni", INUI, EAST, True, 8.0, 6.5)           # Inui keep -- East keep
watari("watari i", EAST, MAIN, False, 5.5, k(10) / 2)     # East keep -- great keep

doc = {
    "name": "Himeji Castle",
    "_about": "HIMEJI CASTLE (1601-1609): the great keep and three small keeps joined by corridor turrets round their court, on the "
              "fan-sloped stone base -- the keeps `tiered` (storeys set in one above another, a curved skirt roof round each, kara, "
              "chidori and irimoya gables on the slopes, steep stairs from floor to floor). Generated by tools/archgen/himeji.py -- "
              "edit the script for arithmetic changes. East is +x, south +z.",
    "params": {"detail": 4},
    "base": {"height": .3, "steps": 1, "stepOut": .5, "margin": 8},
    "railing": {"type": "stone", "height": .9},
    "build": build,
    "parts": parts,
}
out = os.path.join(ROOT, "assets", "architecture", "himeji.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts")
