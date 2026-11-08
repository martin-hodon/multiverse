# lynx_line.py -- the lynx ruff's dark line: points on the skin (probed outward from inside the head), written into lynx.py
import json, subprocess, re, math
HERE = "/home/martin/store/apps/multiverse/tools/creaturegen/sc/m5"
d = json.load(open("/home/martin/store/apps/multiverse/assets/creatures/mammals/lynx.json"))
sh = [s for s in d["sculpt"]["shape"] if s.get("op") != "paint"]
json.dump(sh, open(HERE + "/_lx.json", "w"))
# the path in (x, y), from the eye's outer corner back and down the cheek into the ruff, and its width
path = [(0.537, 0.694, 0.0042), (0.523, 0.677, 0.0055), (0.508, 0.66, 0.006), (0.494, 0.641, 0.0058), (0.484, 0.625, 0.0048)]
# ray from inside: the head's mid plane, outward and a little up (the cheek's normal)
Q = [{"o": [x, y, 0.0], "d": [0, 0.12, 1]} for x, y, _ in path]
json.dump(Q, open(HERE + "/_lq.json", "w"))
r = json.loads(subprocess.check_output(["node", HERE + "/surf3.mjs", HERE + "/_lx.json", HERE + "/_lq.json"]))
L = math.hypot(0.12, 1)
pts = [[x, round(y + 0.12 * t["t"] / L, 4), round(t["t"] / L - 0.001, 4), w] for (x, y, w), t in zip(path, r)]
print(pts)
f = HERE + "/lynx.py"; s = open(f).read()
s = re.sub(r"RUFFLINE = \[.*\]\n", "RUFFLINE = " + json.dumps(pts) + "\n", s, count=1)
open(f, "w").write(s)
