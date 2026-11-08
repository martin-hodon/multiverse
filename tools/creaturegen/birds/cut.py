# cut the blades hidden under other layers: fewer per tract, each a little wider to keep the tract closed
import json, sys
from bg import save
SRC = "/home/martin/store/apps/multiverse/assets/creatures/birds/"   # (run after the species' generator: python3 cut.py name)
PLAN = {
  "chicken": ({"sec": 4, ("hackleF", "hen"): 7, ("hackleF", "rooster"): 8, ("saddleF", "rooster"): 4, "tail": 4}, [3000, 1000]),
  "duck": ({"sec": 4, "gcov": 3, "cov": 3, "flankF": 5, "tail": 5}, [2400, 900]),
  "flamingo": ({"tert": 3}, None),
}
for name, (cuts, mesh) in PLAN.items():
    if len(sys.argv) > 1 and name not in sys.argv[1:]: continue
    d = json.load(open(SRC + name + ".json"))
    for s in d["sculpt"]["shape"]:
        if "rows" not in s: continue
        k = cuts.get((s["id"], s.get("when"))) or cuts.get(s["id"])
        if not k or k >= s["n"]: continue
        f = min(1.3, (max(1, s["n"] - 1) / max(1, k - 1)) ** .6)
        if k <= 2: f = min(1.3, (s["n"] / k) ** .5)
        s["n"] = k
        for r in s["rows"]: r["w"] = round(r["w"] * f, 4)
    if mesh: d["sculpt"]["mesh"]["tris"] = mesh
    save(name, d)
    print(name, [(s["id"], s["n"]) for s in d["sculpt"]["shape"] if "rows" in s])
