# boar_stripes.py -- a wild piglet's pale stripes: points on the boar's flank (probed outward from inside), written to
# boar_stripes.json, which suid.py lays as paint tubes gated on `piglet`
import json, subprocess
SC = "/home/martin/store/apps/multiverse/tools/creaturegen/sc"
d = json.load(open("/home/martin/store/apps/multiverse/assets/creatures/mammals/boar.json"))
sh = [s for s in d["sculpt"]["shape"] if s.get("op") not in ("paint", "sub") and not s.get("when")]
json.dump(sh, open(SC + "/au/_bs.json", "w"))
xs = [0.42, 0.3, 0.18, 0.06, -0.06, -0.18, -0.3, -0.42, -0.52]
rows = [0.6, 0.68, 0.76, 0.83]
Q = [{"o": [x, y, 0.0], "d": [0, 0.15, 1]} for y in rows for x in xs]
json.dump(Q, open(SC + "/au/_bq.json", "w"))
r = json.loads(subprocess.check_output(["node", SC + "/m5/surf3.mjs", SC + "/au/_bs.json", SC + "/au/_bq.json"]))
L = (1 + 0.15 ** 2) ** 0.5
out = []
for j, y in enumerate(rows):
    pts = []
    for i, x in enumerate(xs):
        t = r[j * len(xs) + i]["t"]
        if t is None: continue
        pts.append([x, round(y + 0.15 * t / L, 4), round(t / L, 4), 0.016])
    out.append(pts)
json.dump(out, open(SC + "/au/boar_stripes.json", "w"))
print(out)
