# FUSHIMI INARI TAISHA, Kyoto (the shrine since 711; the halls rebuilt 1499 and after): the head shrine of Inari, at the
# foot of Mount Inari -- the great torii on the approach, the two-storey tower gate (romon), the worship hall (haiden)
# and the main hall (honden) behind it, and from beside the main hall the SENBON TORII: two tunnels of vermilion torii,
# side by side, each gate given by a worshipper, so close that their pillars make walls, climbing toward the mountain.
#   Every torii is one component (components/torii: pillars, nuki, plaque, the shimaki and the swept kasagi, both
#   `beam`s on one curve), the great one and the hundreds of small ones alike, the tunnels each one part placed again
#   and again along its line -- climbing with the path as it rises in flights between level stretches.
#   The GATE and the HALLS are `tiered` parts (tiered.js): the gate two storeys under one hip-and-gable roof, the
#   lower with no roof of its own, its passage through the middle; the halls one storey each.
#   East is +x, south is +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
r4 = lambda v: round(v, 4)

ROOF = {"pitch": 26, "overhang": 2.0, "lo": .35, "hi": 1.0, "upturn": .25, "flare": .2}

# ---- the approach: the great torii, the tower gate -------------------------------------------------------------
add("great torii", {"type": "component", "use": "components/torii",
                    "params": {"span": 6.4, "height": 7.2, "r": .42, "over": 1.9, "sori": .6}, "at": [[0, 0, 44.0, 0]],
                    "_about": "the great torii on the approach"})
add("romon", {"type": "tiered", "storeys": [{"w": 11.0, "l": 6.0, "h": 4.6, "roof": False}, {"w": 11.0, "l": 6.0, "h": 3.6}],
              "wall": {"t": .35}, "windows": False, "roof": ROOF, "top": {"pitch": 30, "hipH": .5}, "floors": False,
              "brackets": {"s": .55, "every": 1.5},
              "door": [{"side": "s", "width": 3.4, "height": 3.8}, {"side": "n", "width": 3.4, "height": 3.8}],
              "at": [[0, 0, 28.0, 0]],
              "_about": "the tower gate (romon, 1589): two storeys under one hip-and-gable roof, the passage through the middle"})

# ---- the halls ----------------------------------------------------------------------------------------------------
add("haiden", {"type": "tiered", "storeys": [{"w": 14.0, "l": 8.0, "h": 4.4}], "wall": {"t": .3},
               "windows": {"every": 2.8, "width": 2.2, "end": 1.6, "sill": .6, "springing": 3.2, "head": {"profile": "flat"}},
               "roof": ROOF, "top": {"pitch": 28, "hipH": .5, "overhang": 2.2}, "floors": False, "brackets": {"s": .5, "every": 1.4},
               "door": {"side": "s", "width": 2.8, "height": 2.9}, "at": [[0, 0, 12.0, 0]],
               "_about": "the worship hall (haiden), open to the court along its front"})
add("honden", {"type": "tiered", "storeys": [{"w": 16.0, "l": 9.6, "h": 4.8}], "wall": {"t": .3}, "windows": False,
               "roof": ROOF, "top": {"form": "gable", "pitch": 27, "overhang": 2.6}, "floors": False, "brackets": {"s": .55, "every": 1.5},
               "door": {"side": "s", "width": 2.6, "height": 3.2}, "at": [[0, 0, -4.0, 0]],
               "_about": "the main hall (honden, 1494), its long gable roof sweeping out over the front"})

# ---- the senbon torii: two tunnels of torii up the slope ------------------------------------------------------------
# each tunnel runs north from beside the main hall: level, a flight up, level, a flight up, level; a torii every GAP
# along it, standing on the path wherever it is (on the treads of a flight, at the tread's height)
GAP, TW, RUN, RISE = .62, 1.7, .4, .12
TORII = {"span": 1.5, "height": 3.0, "r": .085, "over": .38, "sori": .12, "plaque": "no"}
LANES = [-11.5, -8.6]                    # the tunnels' middle lines (x)
Z0 = -10.0                               # where they start
LEGS = [("level", 9.0), ("flight", 8), ("level", 7.0), ("flight", 10), ("level", 8.0)]   # level: its length; flight: its steps

def tunnel(name, x):
    z, y, gates = Z0, 0.0, []
    for j, (kind, v) in enumerate(LEGS):
        if kind == "level":
            add(f"{name} path {j + 1}", {"type": "prism", "plan": {"rect": [TW + .4, v]}, "height": r4(y + .15), "walked": True,
                                         "at": [[x, 0, r4(z - v / 2), 0]]})
            n = int(v / GAP)
            gates += [[x, r4(y + .15), r4(z - (i + .5) * GAP), 0] for i in range(n)]
            z -= v
        else:
            # (climbing north, -z: yaw pi/2 lays the flight over x - width .. x)
            top = y + v * RISE
            add(f"{name} stair {j + 1}", {"type": "flight", "width": TW + .4, "run": RUN, "rise": RISE, "base": r4(y + .15), "top": r4(top + .15),
                                          "landing": 0, "ground": 0, "at": [[r4(x + (TW + .4) / 2), 0, r4(z), math.pi / 2]]})
            for i in range(v):   # a torii on every other tread
                if i % 2 == 0: gates.append([x, r4(y + .15 + (i + 1) * RISE), r4(z - (i + .5) * RUN), 0])
            z -= v * RUN; y = top
    add(name, {"type": "component", "use": "components/torii", "params": TORII, "at": gates,
               "_about": "a tunnel of small torii, one close behind another, climbing with its path"})

tunnel("senbon west", LANES[0])
tunnel("senbon east", LANES[1])

doc = {
    "name": "Fushimi Inari Taisha",
    "_about": "FUSHIMI INARI TAISHA: the great torii, the tower gate, the worship and main halls, and the senbon torii -- two tunnels "
              "of small vermilion torii climbing toward the mountain, every gate one `torii` component placed again and again along "
              "its path. The gate and the halls `tiered`. Generated by tools/archgen/fushimi_inari.py -- edit the script for "
              "arithmetic changes. East is +x, south +z.",
    "params": {"detail": 4},
    "base": {"height": .3, "steps": 1, "stepOut": .5, "margin": 5},
    "railing": {"type": "stone", "height": .8},
    "build": build,
    "parts": parts,
}
out = os.path.join(ROOT, "assets", "architecture", "fushimi-inari.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts")
