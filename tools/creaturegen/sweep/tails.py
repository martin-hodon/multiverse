#!/usr/bin/env python3
"""TAILS AS SWEEPS (2026-11-08): a tail drawn as a chain of cones (tailSeg0, tailSeg1 ... one a few centimetres, each
blended into the next: a bead at every joint, and a staircase where it is a cell or two thick) or as one tube on one
bone, made ONE `sweep` (sculpt.js): a smooth centreline through the chain's joints, its radius monotone along it, its
skin handed from tail bone to tail bone at the rig's joints, its too-thin end drawn as exact rings (sharp.js
sweepMesh) -- see docs/engines.md "Sweeps".

  python3 tails.py SPECIES [--chain tail,tail1] [--end point] [--thin CELLS] [--keep REGEX] [--dry]
      SPECIES: the path under assets/creatures (mammals/cat)

What is joined: the shapes on a tail bone (^tail\\d*$) that are cones or tubes, not a root, brush, lock or tuft (their
ids), put in order by joining each cone's far end to the next one's near end. Its colour the commonest of theirs, the
others BANDS ([from, to, colour] by their share of the length: a ringed tail); a round tip shape at its end (tailTip)
taken in, its colour a band at the end. Its k, hair, pat and frame the first segment's. `--chain` the bones it runs
along (default those the segments rode). Idempotent: a species whose tail is already a sweep is skipped.
RE-RUN after the species' own generator (it writes the segments back)."""
import json, math, sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sharp"))
import shp
from necks import about

NOTE = (" (2026-11-08, tools/creaturegen/sweep/tails.py) The TAIL is one `sweep` (sculpt.js) along its bones, not a chain"
        " of cones blended one into the next: no beads, its thin end exact rings.")
SKIP = re.compile(r"root|brush|lock|tuft", re.I)

def opt(name, d=None):
    for i, a in enumerate(sys.argv):
        if a == "--" + name and i + 1 < len(sys.argv): return sys.argv[i + 1]
    return d

def run(sp, chain=None, end=None, thin=None, dry=False):
    txt, d = shp.load(sp)
    sh = d["sculpt"]["shape"]
    if any(p.get("type") == "sweep" and re.match(r"^tail\d*$", p.get("bone", "")) for p in sh):
        print(sp, "skipped: its tail is a sweep already"); return
    seg = [i for i, p in enumerate(sh) if p.get("type") in ("cone", "tube") and re.match(r"^tail\d*$", p.get("bone", "body"))
           and not SKIP.search(p.get("id", "")) and not p.get("mirror") and p.get("op") is None]
    if not seg: print(sp, "skipped: no tail segments"); return
    S = [sh[i] for i in seg]
    if all(p["type"] == "cone" for p in S):
        # (in order: from the one whose near end is no other's far end, each to the one that starts where it ends)
        near = lambda a, b: math.dist(a, b) < 1e-3
        first = [p for p in S if not any(near(p["a"], q["b"]) for q in S if q is not p)]
        if len(first) != 1: raise SystemExit(f"{sp}: the cones are not one chain ({len(first)} starts)")
        order = [first[0]]
        while len(order) < len(S):
            nx = [q for q in S if near(q["a"], order[-1]["b"]) and q not in order]
            if len(nx) != 1: raise SystemExit(f"{sp}: the chain breaks after {order[-1].get('id')}")
            order.append(nx[0])
        pts = [order[0]["a"] + [order[0]["ra"]]] + [p["b"] + [p["rb"]] for p in order]
        lens = [math.dist(p["a"], p["b"]) for p in order]
    elif len(S) == 1:
        order = S; pts = [list(q) for q in S[0]["pts"]]
        lens = [math.dist(pts[i][:3], pts[i + 1][:3]) for i in range(len(pts) - 1)]
    else: raise SystemExit(f"{sp}: a tail of {len(S)} tubes (or tubes and cones): join it by hand")
    pts = [[round(v, 5) for v in q[:3]] + [round(q[3], 5)] for q in pts]
    L = sum(lens)
    # (its colour: the commonest; the other segments' colours BANDS by their share of the length)
    cols = [p.get("color") for p in order]
    base = max(set(cols), key=lambda c: sum(l for c2, l in zip(cols, lens) if c2 == c)) if len(order) > 1 else cols[0]
    bands, s = [], 0.0
    for p, l in zip(order, lens):
        c = p.get("color")
        if len(order) > 1 and c != base:
            if bands and bands[-1][2] == c and abs(bands[-1][1] - s / L) < 1e-3: bands[-1][1] = round((s + l) / L, 4)
            else: bands.append([round(s / L, 4), round((s + l) / L, 4), c])
        s += l
    drop = set(seg)
    # (a round TIP shape at its end: taken in -- the sweep's round end -- its colour a band there)
    for i, p in enumerate(sh):
        if p.get("type") == "sphere" and re.match(r"^tail\d*$", p.get("bone", "")) and re.search("tip", p.get("id", ""), re.I) \
           and math.dist(p["c"], pts[-1][:3]) <= p["r"] * 1.01:
            drop.add(i)
            if p.get("color") != base:
                f = round(max(0.0, 1 - 2.2 * p["r"] / L), 4)
                if bands and bands[-1][2] == p.get("color") and bands[-1][1] >= f - 1e-4: bands[-1][1] = 1
                else: bands.append([f, 1, p.get("color")])
            pts[-1][3] = round(max(pts[-1][3], p["r"] * .92), 5)
    f0 = order[0]
    bones = chain.split(",") if chain else list(dict.fromkeys(p.get("bone", "body") for p in order))
    sw = {"id": "tail", "type": "sweep", "bones": bones, "pts": pts, "k": f0.get("k", 0)}
    for k in ("kc", "hair", "wet", "coat", "pat", "frame"):
        if k in f0: sw[k] = f0[k]
    sw["color"] = base
    if bands: sw["bands"] = bands
    if end: sw["end"] = end
    if thin: sw["thin"] = float(thin)
    first = min(drop)
    new = [sw if i == first else p for i, p in enumerate(sh) if i == first or i not in drop]
    print(sp, "bones", bones, "pts", len(pts), "r", pts[0][3], "->", pts[-1][3], "bands", bands, "dropped", len(drop))
    if dry: return
    shp.save(sp, new, txt)
    about(sp, NOTE)

if __name__ == "__main__":
    for sp in [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and not sys.argv[i - 1].startswith("--")]:
        run(sp, opt("chain"), opt("end"), opt("thin"), "--dry" in sys.argv)
