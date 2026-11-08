# beartail.py -- (2026-11-07 tail sweep) the bear's tail was a smooth rig sausage stuck to the rump by a thin neck
# (its root 1.6 cm clear of the skin): now a short furry stub sculpted on bone "tail", half buried in the rump, coarse
# fur like the coat; the rig chain (only its bone) a path rooted inside.
import json, sys
sys.path.insert(0, "/home/martin/store/apps/multiverse/tools/creaturegen/giants")
from lib import save, R
P = "mammals/bear"
d = json.load(open(R + P + ".json"))
sc = d["sculpt"]
sh = [q for q in sc["shape"] if not q["id"].startswith("tail")]
d["tail"] = {"path": [[-0.8, 0.84], [-0.92, 0.81], [-0.96, 0.74]], "r1": 0.05, "r2": 0.035, "tuft": 0, "sway": 10, "speed": 0.5}
sh.append({"id": "tail", "type": "ell", "bone": "tail", "c": [-0.895, 0.82, 0], "r": [0.055, 0.072, 0.06], "rot": [0, 0, 35],
           "k": 0.04, "color": "@body", "pat": "coarse"})
sc["shape"] = sh
sc["keep"] = [k for k in sc.get("keep", []) if k != "tail\\d*"]
save(P, d)
print(len(sh), "shapes, keep", sc["keep"])
