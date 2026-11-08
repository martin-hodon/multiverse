# dropear.py SPECIES [EAR_ID] : a DROP ear (a fin sheet hanging down the side of the head) stood OFF the skin.
# (2026-11-08) ears2.py measured the dog's drop ear from the old field shapes, which lay in the head: its rear rim ran up
# to 14 mm under the skin, so the flap showed only as a sliver of its hollow. Each outline point (not the root, which
# stays buried) is moved along the body field's normal until it stands `off` clear of the skin: a little at the root,
# more toward the tip (a hanging flap stands off the cheek at its lower end). Idempotent: it aims at distances.
import json, sys
from shp import fd, path_of

def stand_off(sp, eid="ear", off=(0.004, 0.014), iters=4, h=0.002):
    path = path_of(sp); txt = open(path).read(); d = json.loads(txt)
    e = next(s for s in d["sculpt"]["shape"] if s.get("id") == eid)
    old = json.dumps(e)
    top = max(p[1] for p in e["root"]); low = min(p[1] for p in e["edge"])
    for _ in range(iters):
        P = [p[:3] for p in e["edge"]]
        probe = []
        for p in P:
            probe.append(p)
            for k in range(3):
                q = list(p); q[k] += h; probe.append(q)
        D = fd(sp, {"exclude": [eid], "points": probe})["d"]
        for i, p in enumerate(e["edge"]):
            d0 = D[4 * i]; g = [(D[4 * i + 1 + k] - d0) / h for k in range(3)]
            gl = sum(v * v for v in g) ** .5 or 1
            s = (top - p[1]) / max(top - low, 1e-6)          # (0 at the root's height, 1 at the tip)
            want = off[0] + (off[1] - off[0]) * max(0.0, min(1.0, s))
            if d0 < want:
                for k in range(3): p[k] = round(p[k] + g[k] / gl * (want - d0), 4)
    new = json.dumps(e)
    if new != old:
        txt = txt.replace(old, new, 1); json.loads(txt); open(path, "w").write(txt)
    return new != old

if __name__ == "__main__":
    print(stand_off(sys.argv[1], *(sys.argv[2:3] or ["ear"])))
