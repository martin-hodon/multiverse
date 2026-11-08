#!/usr/bin/env python3
"""NECKS AS SWEEPS (2026-11-08): a long-necked bird's neck -- drawn as a tube a bone (neckA on `neck`, neckB on
`neck2`, neckC on `neck3`), each blended into the next -- made ONE `sweep` (sculpt.js: a smooth centreline through all
their points, its radius monotone along it, its skin handed from bone to bone at the rig's joints). The tubes' smooth
union bulged at every overlap (a bead at each joint: the swan's neck was a string of them).

  python3 necks.py SPECIES [SPECIES ...]     (birds/<species>.json; --dry: print, write nothing)

The tubes' points are joined in order; where one tube's last point and the next one's first lie within their radius of
each other they become one (their middle). The sweep takes neckA's place, its k and colour; `aspect` (default 1.1:
a bird's neck a little deeper than wide) with every radius divided by its square root (the same girth). Idempotent: a
species with no neckA/neckB left is skipped. RE-RUN after the species' own generator (it writes the tubes back)."""
import json, re, math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sharp"))
import shp   # (its save: one shape a line, the rest of the file untouched)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ASPECT = 1.1
NOTE = (" (2026-11-08, tools/creaturegen/sweep/necks.py) The NECK is one `sweep` (sculpt.js) along the chain of neck bones,"
        " not a tube a bone blended into the next: no bead at the joints.")

def merge(tubes):
    out = []
    for t in tubes:
        pts = [list(p) for p in t["pts"]]
        if out:
            a, b = out[-1], pts[0]
            if math.dist(a[:3], b[:3]) <= max(a[3], b[3]):
                out[-1] = [round((a[k] + b[k]) / 2, 5) for k in range(4)]
                pts = pts[1:]
        out += pts
    return out

def run(name, dry=False, aspect=ASPECT):
    path = os.path.join(ROOT, "assets/creatures/birds", name + ".json")
    d = json.load(open(path))
    sh = d["sculpt"]["shape"]
    ids = [i for i, p in enumerate(sh) if p.get("id") in ("neckA", "neckB", "neckC") and p.get("type") == "tube"]
    if len(ids) < 2:
        print(name, "skipped: no neck tubes to join"); return
    tubes = [sh[i] for i in ids]
    bones = [t.get("bone", "body") for t in tubes]
    pts = merge(tubes)
    f = 1 / math.sqrt(aspect)
    pts = [[p[0], p[1], p[2], round(p[3] * f, 5)] for p in pts]
    sw = {k: v for k, v in tubes[0].items() if k not in ("pts", "bone", "per", "id", "type")}
    sw = {"id": "neck", "type": "sweep", "bones": bones, "pts": pts, "aspect": aspect, **sw}
    new = [p for i, p in enumerate(sh) if i not in ids[1:]]
    new[ids[0]] = sw
    print(name, "bones", bones, "pts", len(pts), "r", [p[3] for p in pts])
    if dry: return
    sp = "birds/" + name
    shp.save(sp, new)
    about(sp, NOTE)

def about(sp, note):
    """the species' `_about` line with `note` added (once), the rest of the file as it is"""
    txt = open(shp.path_of(sp)).read(); d = json.loads(txt); a = d.get("_about", "")
    if note in txt: return
    old = '"_about": ' + json.dumps(a, ensure_ascii=False)
    if txt.count(old) != 1: old = '"_about": ' + json.dumps(a)
    if txt.count(old) == 1: txt = txt.replace(old, '"_about": ' + json.dumps(a + note, ensure_ascii=False))
    else:   # (written with other escapes: the one line that holds it, re-encoded)
        m = [mm for mm in re.finditer(r'"_about": ("(?:[^"\\]|\\.)*")', txt) if json.loads(mm.group(1)) == a or not a]   # (or nested, not at the top)
        assert len(m) == 1, "no one _about line"
        txt = txt[:m[0].start(1)] + json.dumps(json.loads(m[0].group(1)) + note, ensure_ascii=False) + txt[m[0].end(1):]
    json.loads(txt); open(shp.path_of(sp), "w").write(txt)

if __name__ == "__main__":
    dry = "--dry" in sys.argv
    for n in [a for a in sys.argv[1:] if not a.startswith("--")]: run(n, dry)
