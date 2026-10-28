# HORYU-JI, the Western Precinct (Sai-in Garan), Ikaruga, Nara (rebuilt after 670): the oldest wooden buildings
# standing -- the five-storeyed pagoda and the Golden Hall (Kondo) side by side in a court closed by the covered
# corridor (kairo), entered through the Middle Gate (Chumon).
#   The PAGODA is a `tiered` part (tiered.js) of five square storeys, each a little smaller than the one below (the
#   fifth half the first), every roof deep-eaved -- a skirt round each storey, the crowning pyramid, the sorin on its
#   apex (the mast and its nine rings); not climbed: no floors inside.
#   The KONDO is `tiered` too: two storeys under a hip-and-gable roof, the upper set in; the GATE two storeys with
#   its passage through the middle.
#   Each stands on its stone platform (kidan), a stair up its south side.
#   The KAIRO is a `range` with a `roof`: one bay deep along the court's four sides from the gate round to the gate,
#   lattice windows (renji-mado) to the outside, open between its posts to the court, the roof mitred at its corners
#   and open under its rafters.
#   East is +x, south is +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
r4 = lambda v: round(v, 4)

RISE, RUN = .16, .32
ROOF = {"pitch": 25, "overhang": 2.8, "lo": .35, "hi": 1.0, "upturn": .3, "flare": .2}

def platform(name, at, w, l, h, stair_w):
    """a stone platform w x l, h high, with a flight up the middle of its south side"""
    add(f"{name} platform", {"type": "prism", "plan": {"rect": [w, l]}, "height": h, "walked": True, "at": [[r4(at[0]), 0, r4(at[1]), 0]]})
    n = max(1, round(h / RISE)); L = n * RUN
    # (climbing north, -z: yaw pi/2 lays the flight over x - width .. x)
    add(f"{name} stair", {"type": "flight", "width": stair_w, "run": RUN, "top": h, "rise": RISE, "base": 0, "landing": 0,
                          "at": [[r4(at[0] + stair_w / 2), 0, r4(at[1] + l / 2 + L), math.pi / 2]]})

# ---- the court and the corridor ------------------------------------------------------------------------------
CX, CZ = 45.0, 33.0                      # the kairo's middle line: 90 x 66m
GW, GL = 11.9, 8.4                       # the Middle Gate's first storey (four bays by three)
KW, KH = 3.7, 3.6                        # the corridor's depth and the height of its walls
path = [[r4(GW / 2), CZ], [CX, CZ], [CX, -CZ], [-CX, -CZ], [-CX, CZ], [r4(-GW / 2), CZ]]
BAY = 3.7
add("kairo", {"type": "range", "path": path, "width": KW, "height": KH, "thickness": .3, "interior": False,
              "faces": {"out": {"every": BAY, "width": 2.2, "end": 1.0, "sill": 1.0, "springing": 2.5, "head": {"profile": "flat"}},
                        "in": {"every": BAY, "width": 3.0, "end": 1.0, "sill": 0, "springing": 3.1, "head": {"profile": "flat"}},
                        "end": []},
              "roof": {"pitch": 24, "overhang": 1.1, "shell": .3},
              "_about": "the covered corridor round the court from the gate round to the gate: lattice windows outward, open to the court between its posts, its roof mitred at the corners and open under its rafters"})

# ---- the Middle Gate -------------------------------------------------------------------------------------------
add("chumon", {"type": "tiered", "storeys": [{"w": GW, "l": GL, "h": 5.2}, {"w": 10.0, "l": 6.6, "h": 3.4}], "wall": {"t": .35},
               "windows": False, "roof": ROOF, "top": {"pitch": 30, "hipH": .5}, "floors": False, "brackets": {"s": .8, "every": 2.0},
               "door": [{"side": "s", "at": -1.5, "width": 2.4, "height": 3.0}, {"side": "s", "at": 1.5, "width": 2.4, "height": 3.0},
                        {"side": "n", "at": -1.5, "width": 2.4, "height": 3.0}, {"side": "n", "at": 1.5, "width": 2.4, "height": 3.0}],
               "at": [[0, 0, CZ, 0]],
               "_about": "the Middle Gate: four bays wide, a column on its axis, the passage through the two middle bays; two storeys under a hip-and-gable roof"})

# ---- the Golden Hall and the pagoda ----------------------------------------------------------------------------
KD = (16.0, -3.0)
PH = 1.2
platform("kondo", KD, 22.0, 18.6, PH, 3.6)
add("kondo", {"type": "tiered", "storeys": [{"w": 14.3, "l": 10.8, "h": 5.4}, {"w": 10.6, "l": 7.2, "h": 3.6, "windows": False}],
              "wall": {"t": .4}, "windows": {"every": 3.0, "width": 1.4, "end": 1.6, "sill": 1.2, "springing": 3.4, "head": {"profile": "flat"}},
              "roof": ROOF, "top": {"pitch": 31, "hipH": .7, "overhang": 2.6}, "floors": False, "brackets": {"s": .9, "every": 2.0},
              "door": [{"side": "s", "width": 2.2, "height": 3.0}, {"side": "e", "width": 2.2, "height": 3.0}, {"side": "w", "width": 2.2, "height": 3.0}],
              "at": [[KD[0], PH, KD[1], 0]],
              "_about": "the Golden Hall: two storeys, the upper set in under the hip-and-gable roof; doors to the south, east and west"})

PG = (-15.0, -3.0)
platform("pagoda", PG, 13.6, 13.6, PH, 2.4)
add("pagoda", {"type": "tiered", "storeys": [{"w": 6.4, "l": 6.4, "h": 4.6}, {"w": 5.6, "l": 5.6, "h": 3.6}, {"w": 4.8, "l": 4.8, "h": 3.5},
                                             {"w": 4.0, "l": 4.0, "h": 3.4}, {"w": 3.2, "l": 3.2, "h": 3.4}],
               "wall": {"t": .35}, "windows": False, "roof": {**ROOF, "overhang": 2.6}, "top": {"form": "hip", "pitch": 28, "overhang": 2.4},
               "floors": False, "door": {"side": "s", "width": 1.6, "height": 2.4},
               "finial": {"height": 9.0, "radius": .16, "rings": 9, "base": 1.3}, "brackets": {"s": .8, "every": 1.6},
               "at": [[PG[0], PH, PG[1], 0]],
               "_about": "the five-storeyed pagoda: square storeys, the fifth half as wide as the first, every one under a deep eave; the sorin on the apex, its nine rings"})

doc = {
    "name": "Horyu-ji",
    "_about": "HORYU-JI, the Western Precinct (rebuilt after 670): the five-storeyed pagoda and the Golden Hall side by side in the court "
              "of the covered corridor, entered through the Middle Gate -- the pagoda, the hall and the gate `tiered`, the corridor a roofed "
              "`range`. Generated by tools/archgen/horyuji.py -- edit the script for arithmetic changes. East is +x, south +z.",
    "params": {"detail": 4},
    "base": {"height": .3, "steps": 1, "stepOut": .5, "margin": 6},
    "railing": {"type": "stone", "height": .9},
    "build": build,
    "parts": parts,
}
out = os.path.join(ROOT, "assets", "architecture", "horyuji.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts")
