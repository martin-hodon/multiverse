# USER BUG #2 (2026-11-07): the elephant's tail stood off the rump -- a rig arc rooted 0.28 m behind the buttocks,
# hanging ~8 cm clear of them, ending in a faceted sphere. Now: the rig chain (only its bone, "tail") is a path from
# INSIDE the rump at the dock, and the tail itself is sculpted on that bone -- a dock swelling out of the skin, a tube
# down the groove between the buttocks close against them, a brush of dark hair tapering to a point.
# Patches the current JSON in place (the generator, gen_elephant.py, is older than the audit's edits).
import json, sys
sys.path.insert(0, "/home/martin/store/apps/multiverse/tools/creaturegen/giants")
from lib import save, R
P = "mammals/elephant"
d = json.load(open(R + P + ".json"))
sc = d["sculpt"]
sh = [q for q in sc["shape"] if not q["id"].startswith("tail")]

# the rig: a path from inside the rump (the bone's pivot: the sway turns the tail about its root, which stays put)
d["tail"] = {"path": [[-1.3, 2.47], [-1.63, 2.36], [-1.69, 1.95], [-1.665, 1.35]], "r1": 0.09, "r2": 0.04, "tuft": 0,
             "sway": 10, "speed": 0.7}
d["c"]["tuft"] = "#2a241e"

T = "tail"
sh += [
    # the dock: the root's swelling at the top of the buttocks, on the body -- the skin the tail grows out of
    {"id": "tailDock", "type": "ell", "c": [-1.42, 2.41, 0], "r": [0.13, 0.11, 0.11], "rot": [0, 0, 35], "k": 0.08, "color": "@skin"},
    # the tail: back and down out of the dock, then hanging straight down the groove, just clear of the buttocks
    {"id": "tail", "type": "tube", "bone": T, "pts": [[-1.32, 2.47, 0, 0.092], [-1.46, 2.43, 0, 0.082], [-1.6, 2.32, 0, 0.07],
                                                     [-1.682, 2.13, 0, 0.058], [-1.675, 1.93, 0, 0.05], [-1.667, 1.75, 0, 0.044], [-1.665, 1.6, 0, 0.04]],
     "k": 0.025, "color": "@tail", "pat": "bark"},
    # the brush: the last third of the tail clothed in coarse black hair -- a spindle, fullest a little below where
    # the hair starts, tapering to a point, and six locks of it bowing out round it and drawn to points at the tip
    {"id": "tailBrush", "type": "tube", "bone": T, "pts": [[-1.665, 1.67, 0, 0.042], [-1.665, 1.56, 0, 0.057], [-1.662, 1.45, 0, 0.05],
                                                          [-1.658, 1.36, 0, 0.032], [-1.655, 1.29, 0, 0.012]],
     "k": 0.025, "color": "@tuft", "hair": 1},
]
import math
for j in range(8):   # (eight locks round it, lying along its flanks as flutes, their ends a ragged point just past its own)
    th = j * math.pi / 4 + 0.2; cx, cz = math.cos(th), math.sin(th); y = 1.28 + 0.012 * (j % 3)
    sh.append({"id": f"tailLock{j}", "type": "tube", "bone": T, "pts": [[-1.665 + 0.02 * cx, 1.64, 0.02 * cz, 0.028], [-1.664 + 0.042 * cx, 1.5, 0.042 * cz, 0.028],
                                                                       [-1.659 + 0.03 * cx, 1.37, 0.03 * cz, 0.02], [-1.656 + 0.022 * cx, y, 0.022 * cz, 0.008]],
               "k": 0.014, "color": "@tuft", "hair": 1})
sc["shape"] = sh
sc["keep"] = []
# a finer grid (was 0.055: a 7 cm tail was two cells across, its tuft a polygon), the tail kept fine by the simplifier
sc["mesh"]["cell"] = 0.032
sc["mesh"]["focus"]["tail"] = 6
save(P, d)
print(len(sh), "shapes")
