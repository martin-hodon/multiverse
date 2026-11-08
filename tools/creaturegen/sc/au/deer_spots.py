# deer_spots.py -- a fallow deer's white spots: rows along the back and flank of the red deer's sculpt (probed outward from
# inside), written to deer_spots.json, which cervid.py lays as paint spheres gated on `fallow`
import json, subprocess, random
SC = "/home/martin/store/apps/multiverse/tools/creaturegen/sc"
d = json.load(open("/home/martin/store/apps/multiverse/assets/creatures/mammals/deer.json"))
sh = [s for s in d["sculpt"]["shape"] if s.get("op") not in ("paint", "sub") and not s.get("when") and s.get("bone") in (None, "body")]
json.dump(sh, open(SC + "/au/_ds.json", "w"))
rnd = random.Random(7)
# rows: a line of spots each side of the spine's dark stripe, then scattered rows down the flank; and the white line low on the flank
rows = [(1.14, 0.045, 0.012), (1.09, 0.055, 0.013), (1.03, 0.06, 0.013), (0.97, 0.065, 0.012)]
Q, meta = [], []
for y, step, r in rows:
    x = 0.3 - rnd.uniform(0, step)
    while x > -0.78:
        yy = y + rnd.uniform(-0.012, 0.012)
        Q.append({"o": [x, yy, 0.0], "d": [0, 0.35 if y > 1.1 else 0.0, 1]}); meta.append((x, yy, r * rnd.uniform(0.85, 1.15), 0.35 if y > 1.1 else 0.0))
        x -= step * rnd.uniform(0.85, 1.2)
json.dump(Q, open(SC + "/au/_dq.json", "w"))
res = json.loads(subprocess.check_output(["node", SC + "/m5/surf3.mjs", SC + "/au/_ds.json", SC + "/au/_dq.json"]))
out = []
for (x, y, r, dy), t in zip(meta, res):
    if t["t"] is None: continue
    L = (1 + dy * dy) ** 0.5
    out.append([round(x, 4), round(y + dy * t["t"] / L, 4), round(t["t"] / L, 4), round(r, 4)])
json.dump(out, open(SC + "/au/deer_spots.json", "w"))
print(len(out), "spots")
