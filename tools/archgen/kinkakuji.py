# KINKAKU-JI, the Golden Pavilion (Rokuon-ji), Kyoto (1397; rebuilt 1955) on the north shore of the Mirror Pond (Kyoko-chi):
# three storeys in three manners -- the first in the palace manner (shinden), dark timber, deep shutters, a white plaster bay,
# the second in the warrior house's (buke), the third a Zen hall (zenshu-butsuden) with its bell-shaped windows (katomado: the `bell` profile) -- the upper
# two covered in gold leaf, a railed balcony round each, the shingled roofs, the phoenix on its gilded stepped base.
#   The PAVILION is a `tiered` part (tiered.js): the first and second storeys one plan, the first with no roof of its
#   own (`roof: false`); the skirt round the second up to the small square third, under its pyramid; bracket sets under
#   the eaves; floors and steep stairs inside. About 12.5 m to the top (proportions read off the south front's photograph).
#   The POND lies in FRONT, not round it: the pavilion's stone edge drops straight into the water on the south (`site.moat`
#   as a `pool`, set off to the south with its `z`), the land behind; rocks and islets stand in it; there is NO bridge.
#   The SOSEI, the small fishing pavilion, stands on piles off the west end, half over the water.
#   East is +x, south is +z. Numbers are worked here and written as numbers.
import os, json, math
import japanese as J
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
r4 = lambda v: round(v, 4)

W1, L1 = 13.6, 10.9                      # the first and second storeys (five bays by four)
W3 = 6.5                                 # the third, square (three bays)
H1, H2, H3 = 3.3, 2.9, 4.0               # (the third's lower part hidden behind the skirt that climbs to it)
EDGE = 1.3                               # the stone edge and veranda round the first storey
GW, GZ = W1 / 2 + EDGE, L1 / 2 + EDGE    # the base's half-width and half-depth: its south edge is the shore
PHW, PHD = 34.0, 22.0                    # the pond's half-width and half-depth (the real one is larger, about 6,600 m2)
PITCH, TOP = 17, 26
ROOF = {"pitch": PITCH, "overhang": 2.3, "lo": .25, "hi": .8, "upturn": .3, "flare": .22}
Y2, Y3 = H1, H1 + H2                     # the second storey's floor; the skirt's eave
YT = Y3 + H3                             # the wall head of the third
YA = YT + W3 / 2 * math.tan(math.radians(TOP))   # (the pyramid's apex: as tiered.js works it)

add("pavilion", {"type": "tiered", "storeys": [
                     {"w": W1, "l": L1, "h": H1, "roof": False,
                      "windows": {"every": 2.7, "width": 2.1, "end": 1.2, "sill": .35, "springing": 2.6, "head": {"profile": "flat"}}},
                     {"w": W1, "l": L1, "h": H2,
                      "windows": {"every": 4.2, "width": 1.5, "end": 1.6, "sill": .5, "springing": 2.2, "head": {"profile": "flat"}}},
                     {"w": W3, "l": W3, "h": H3,
                      "windows": {"every": 2.4, "width": .8, "end": 1.4, "sill": 1.75, "springing": 2.9, "head": {"profile": "bell"}}}],
                 "wall": {"t": .3}, "roof": ROOF, "top": {"form": "hip", "pitch": TOP, "overhang": 2.3},
                 "door": {"side": "n", "width": 1.8, "height": 2.4},
                 "brackets": {"s": .3, "every": 1.0},
                 "finial": {"height": .01, "radius": .02, "rings": 0, "base": .85},
                 "at": [[0, 0, 0, 0]],
                 "_about": "the pavilion: the first storey (the Chamber of Dharma Waters) under no roof of its own, the second (the Tower of Sound Waves) "
                           "on the same plan with the skirt roof over it, the third (the Cupola of the Ultimate) square under the pyramid"})

# the white plaster bays at the first storey's east end (the shuttered rest is dark)
add("plaster south", {"type": "box", "width": 2.6, "length": .06, "height": 2.7, "at": [[r4(W1 / 2 - 1.5), .25, r4(L1 / 2 + .03), 0]],
                      "_about": "the white plaster bay at the south front's east end"})
add("plaster east", {"type": "box", "width": .06, "length": r4(L1 - .8), "height": 2.7, "at": [[r4(W1 / 2 + .03), .25, 0, 0]]})

rail = lambda *a, **k: J.rail(add, *a, **k)
deck = lambda *a, **k: J.deck(add, *a, **k)

# the veranda round the first storey (dark boards just above the stone, a low rail, the back open to the land)
VW, VZ = W1 / 2 + .95, L1 / 2 + .95
deck("veranda", VW, VZ, W1 / 2 - .1, L1 / 2 - .1, .1, .1)
rail("veranda rail", VW - .05, VZ - .05, .1, .6, gap=2.4, posts=2.7, w=.08)
# the balcony of the second storey, carried on the first's beams, and its railing, gilded
BW, BZ = W1 / 2 + .85, L1 / 2 + .85
deck("second balcony", BW, BZ, W1 / 2 - .1, L1 / 2 - .1, Y2 + .05, .2)
rail("second rail", BW - .05, BZ - .05, Y2 + .05, .8, posts=1.35)
# the third's, on the skirt roof at the foot of its visible wall
Y3B = Y3 + (W1 / 2 + ROOF["overhang"] - W3 / 2) * math.tan(math.radians(PITCH)) - .25   # (where the skirt has climbed to the wall)
TW = W3 / 2 + .6
deck("third balcony", TW, TW, W3 / 2 - .1, W3 / 2 - .1, Y3B, .18)
rail("third rail", TW - .05, TW - .05, Y3B, .75, posts=1.2)

# THE PHOENIX on its stepped gilded base (the base about as wide as a door, the bird about a man's height at this scale): components/phoenix,
# facing south
J.phoenix_component()
add("phoenix", {"type": "component", "use": "components/phoenix", "params": {"s": 1.0, "bw": .62, "bh": .2}, "at": [[0, r4(YA + .85 * .3), 0, 0]],
                "_about": "the phoenix on its base, facing south (components/phoenix)"})

# THE SOSEI: the small fishing pavilion off the west end, its near half on the stone, its far half on piles in the water
SX, SZ, SW, SL = -(GW + 1.6), r4(L1 / 2 - 1.5), 3.2, 4.4
add("sosei deck", {"type": "box", "width": r4(SW + .4), "length": r4(SL + .4), "height": .15, "at": [[SX, 0, SZ, 0]]})
add("sosei walk", {"type": "box", "width": 2.0, "length": 1.6, "height": .15, "at": [[r4(SX + SW / 2 + .9), 0, SZ, 0]], "_about": "from the veranda across"})
add("sosei", {"type": "tiered", "storeys": [{"w": SW, "l": SL, "h": 2.5, "windows": {"every": 1.55, "width": 1.25, "end": .3, "sill": .8, "springing": 2.2, "head": {"profile": "flat"}}}],
              "wall": {"t": .12}, "roof": ROOF, "top": {"pitch": 28, "overhang": .75, "hipH": .9}, "floors": False,
              "door": {"side": "e", "width": 1.1, "height": 2.1},
              "at": [[SX, .15, SZ, 0]], "_about": "the sosei, the fishing pavilion joined to the west end"})
add("sosei piles", {"type": "bars", "lines": [[r4(SX + sx * (SW / 2)), -2.0, r4(SZ + sz * (SL / 2)), r4(SX + sx * (SW / 2)), 0, r4(SZ + sz * (SL / 2))] for sx in (-1, 1) for sz in (-1, 1)], "w": .2, "h": .2, "caps": False, "kind": "moulding"})

# the shore's stone edge, straight into the water under the veranda
add("shore", {"type": "box", "width": r4(2 * GW), "length": .8, "height": 4.4, "at": [[0, -4.4, r4(GZ - .4), 0]], "_about": "the stone edge on the water"})

# THE POND'S ROCKS AND ISLETS, standing in the water, each a low irregular prism from under it (the deep foot hides the water line)
PZ0 = GZ                                 # (the pond's north bank)
def rock(name, x, z, pts, h):
    add(name, {"type": "prism", "plan": {"points": [[r4(a), r4(b)] for a, b in pts]}, "height": 4.4 + h - .5, "batter": {"out": 1.2, "power": 2, "steps": 3}, "at": [[x, -4.4, z, 0]]})
R1 = [(-1, -.7), (.2, -1), (1.1, -.3), (.8, .7), (-.3, .9), (-1.2, .2)]
ISLE = [(-5, -2), (-2, -3.4), (2.4, -3.2), (5.2, -1.4), (4.4, 1.8), (.6, 3.2), (-3.4, 2.8), (-5.6, .6)]
rock("islet great", -9.0, r4(PZ0 + 20), ISLE, .35)
rock("islet small", 12.0, r4(PZ0 + 13), [(a * .42, b * .5) for a, b in ISLE], .3)
for k, (x, z, s, h) in enumerate(((-3.5, 5, 1.1, .4), (4.5, 3.5, .8, .3), (9, 7, 1.3, .5), (-13, 9, 1.0, .45), (17, 18, 1.2, .5), (-17, 13, .8, .3))):
    rock(f"rock {k + 1}", x, r4(PZ0 + z), [(a * s, b * s) for a, b in R1], h)

doc = {
    "name": "Kinkaku-ji",
    "_about": "KINKAKU-JI, the Golden Pavilion (1397, rebuilt 1955), on the north shore of the Mirror Pond: three storeys in three manners "
              "-- `tiered`, the first under no roof of its own, the upper two in gold leaf with railed balconies, the phoenix on its base, the sosei off the west end. "
              "The pond lies in front, a `pool` the game carves. Generated by tools/archgen/kinkakuji.py -- edit the script for arithmetic changes. "
              "East is +x, south +z.",
    "params": {"detail": 4, "footW": 2 * PHW + 8, "footD": 2 * (PZ0 + 2 * PHD) + 4},
    "site": {"origin": True, "moat": {"pool": True, "hw": PHW, "hd": PHD, "w": 0, "depth": 4.4, "surface": -.5, "z": r4(PZ0 + PHD)}},
    "base": {"height": .5, "steps": 0, "plan": {"rect": [r4(2 * GW), r4(2 * GZ)]}},
    "railing": {"type": "balusters"},
    "build": build,
    "parts": parts,
}
out = os.path.join(ROOT, "assets", "architecture", "kinkakuji.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts")
