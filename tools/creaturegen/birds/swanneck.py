# swanneck.py (2026-11-08): the swan's FLIGHT NECK straight. Its neck is an S of two curved tubes on two bones (neck,
# neck2); aloft only the bones turn, so the tubes' own curves stayed: dipping off the breast, a hump, then a hook down
# into the head -- an S-dip where a flying swan holds its neck straight out, a little drooping. The upper tube (neckB)
# is split at its bend onto a third bone, NECK3 (child of neck2, the head's new parent), and each bone's `flyRot` turns
# its piece onto one line drooping ~8 degrees, the head held level on it (the numbers: each piece's middle tangent laid
# on that line, from the rest tangents of neckA 63, neckB's lower half 95, its upper half 48, the skull -14 degrees).
# Edits swan.json in place (the parts' and shapes' lines only; idempotent: each change made only where it is missing);
# swan.py runs it after writing the swan. Run from anywhere: python3 swanneck.py
import json
P = "/home/martin/store/apps/multiverse/assets/creatures/birds/swan.json"
FLY = {"neck": -71, "neck2": -31, "neck3": 47, "head": 52}
NECK3 = {"id": "neck3", "parent": "neck2", "shape": "tube", "size": {"a": [0, 0, 0], "c": [0.0, 0.06, 0], "b": [0.07, 0.11, 0], "r1": 0.04, "r2": 0.037},
         "pos": [-0.02, 0.17, 0], "color": "#f4f2ec", "anim": {"axis": "z", "deg": 4, "speed": 0.3, "phase": 1.5}}
NECKB = {"id": "neckB", "type": "tube", "bone": "neck2", "pts": [[0.36, 0.56, 0, 0.048], [0.335, 0.68, 0, 0.042], [0.34, 0.79, 0, 0.039]], "k": 0.03, "color": "@white"}
NECKC = {"id": "neckC", "type": "tube", "bone": "neck3", "pts": [[0.34, 0.79, 0, 0.039], [0.385, 0.875, 0, 0.037], [0.43, 0.905, 0, 0.036]], "k": 0.03, "color": "@white"}

L = open(P).read().split("\n")
def obj(l):
    s = l.strip(); return (json.loads(s.rstrip(",")), s.endswith(","), l[:len(l) - len(l.lstrip())]) if s.startswith("{\"id\"") else (None, 0, "")
def put(i, o, comma, ind): L[i] = ind + json.dumps(o) + ("," if comma else "")
have3 = any((obj(l)[0] or {}).get("id") == "neck3" and "parent" in (obj(l)[0] or {}) for l in L)
haveC = any((obj(l)[0] or {}).get("id") == "neckC" for l in L)
i = 0
while i < len(L):
    o, comma, ind = obj(L[i])
    if o and "parent" in o or (o and o.get("id") in ("neckB",) and "type" in o):
        pid = o["id"]
        if pid == "neck2" and "parent" in o:
            o["size"] = {"a": [0, 0, 0], "c": [-0.03, 0.08, 0], "b": [-0.02, 0.17, 0], "r1": 0.045, "r2": 0.04}
            o["flyRot"] = [0, 0, FLY["neck2"]]; put(i, o, comma, ind)
            if not have3: L.insert(i + 1, ind + json.dumps(dict(NECK3, flyRot=[0, 0, FLY["neck3"]])) + ","); i += 1
        elif pid == "head" and "parent" in o:
            o["parent"] = "neck3"; o["pos"] = [0.11, 0.11, 0]
            o["flyRot"] = [0, 0, FLY["head"]]; put(i, o, comma, ind)
        elif pid in FLY and "parent" in o:
            o["flyRot"] = [0, 0, FLY[pid]]; put(i, o, comma, ind)
        elif pid == "neckB" and "type" in o and not haveC:
            put(i, NECKB, True, ind); L.insert(i + 1, ind + json.dumps(NECKC) + ("," if comma else "")); i += 1
    i += 1
out = "\n".join(L); d = json.loads(out)
ab = d.get("_about", "")
tag = " (2026-11-08, swanneck.py) Aloft the neck is held STRAIGHT out, drooping a little, the head level on it: its upper tube split at the bend onto a third bone (neck3) so each piece turns onto one line (it dipped off the breast and rose in a hump: an S)."
if ab and "swanneck.py" not in ab:
    out = out.replace(json.dumps(ab), json.dumps(ab + tag), 1); json.loads(out)
open(P, "w").write(out)
print("swan neck: neck3", "kept" if have3 else "added", FLY)
