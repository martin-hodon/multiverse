# fchk.py names -- per feather tract: how far its rows' roots/tips stand off the body (max field, mm), vs the bird's size
import sys, json
from bg import field
for n in sys.argv[1:]:
    d = json.load(open(f"/home/martin/store/apps/multiverse/assets/creatures/birds/{n}.json")); sh = d["sculpt"]["shape"]
    o = []
    for s in sh:
        if s["type"] != "feathers": continue
        m = max(field(sh, p) for r in s["rows"] for p in (r["at"], r["to"]))
        o.append(f"{s['id']}:{m*1000:.1f}")
    print(n, " ".join(o))
