#!/usr/bin/env python3
# padfly.py NAMES... | all -- (2026-11-18) a flying bird's FOLDED-WING PAD put away aloft. The pad (nb.py: the folded
# wing as a shape of its own, `wing`, with its marks `wingP*` / `wingBar*`, its `wingRim` and its primaries' `wingTip`)
# is part of the one skinned surface, on the body: aloft it stayed on the flank under the spread wing -- two wings a
# side. Here its shapes go onto a bone of their own, `wpad`, whose `flyScale` (skeleton.js) draws them in aloft to a
# point inside the body: the flank smooth again under the spread wing. (Carrying it in whole does not do: the pad is
# longer than the body -- its tip lies over the tail.) The point: under the pad's middle, just deep enough to hide it. Idempotent: run after the species' generator (and the sharp passes).
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bg import field, fmt, _R

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "assets", "creatures", "birds")
PAD = lambda i: i in ("wing", "wingRim", "wingTip") or i.startswith("wingP") or i.startswith("wingBar")
SOLID = ("ell", "sphere", "tube", "cone")
LEGS = ("legL", "tarsL", "footL")
SHRINK = .08   # (the pad's size aloft)
DEPTH = .004   # (and how far under the flank it is drawn)

def shell(s, n=8):
    """points over an ellipsoid shape's surface"""
    R, c, r = _R(s.get("rot", [0, 0, 0])), s["c"], s["r"]
    for i in range(1, n):
        th = math.pi * i / n
        for j in range(2 * n):
            ph = math.pi * j / n; l = [r[0] * math.cos(th), r[1] * math.sin(th) * math.cos(ph), r[2] * math.sin(th) * math.sin(ph)]
            yield [c[k] + sum(R[k][m] * l[m] for m in range(3)) for k in range(3)]

def run(name):
    path = os.path.join(ROOT, name + ".json")
    d = json.load(open(path)); sh = d["sculpt"]["shape"]
    if not any(p["id"].startswith("ws") for p in d["parts"]): return print(name, "-- no spread wing: nothing to do")
    pad = next((s for s in sh if s["id"] == "wing" and s["type"] == "ell"), None)
    if not pad: return print(name, "-- no pad")
    d["parts"] = [p for p in d["parts"] if not p["id"].startswith("wpad")]   # (an earlier run's)
    # the point it shrinks to: from the pad's middle in toward the midline, the first at which every point of the shrunk
    # pad is DEPTH inside the body (the body without the pad and the legs) -- the shallowest: the flank's skin round the
    # pad, half bound to its bone, is drawn in after it, and to a deep point that is a funnel; to a shallow one a dimple
    rest = [s for s in sh if s["type"] in SOLID and not PAD(s["id"]) and not s.get("op") and s.get("bone", "body") not in LEGS]
    pts = [q for s in sh if PAD(s["id"]) and s["type"] == "ell" and not s.get("op") for q in shell(s)]
    c = pad["c"]; best = None
    for i in range(0, 81):
        o = [c[0], c[1], c[2] * (1 - i / 80)]
        dp = min(-field(rest, [o[k] + (q[k] - o[k]) * SHRINK for k in range(3)]) for q in pts)
        if best is None or dp > best[0]: best = (dp, o)
        if dp >= DEPTH: break
    dp, o = best
    if dp < DEPTH: print(f"  {name}: the shrunk pad only {dp * 1000:.1f} mm in")
    bp = next(p for p in d["parts"] if p["id"] == "body")["pos"]
    out = []
    for p in d["parts"]:
        out.append(p)
        if p["id"] == "body":
            for s, sg in (("L", 1), ("R", -1)):
                out.append({"id": "wpad" + s, "parent": "body", "shape": "sphere", "size": {"r": .004}, "color": "@cov",
                            "pos": [round(o[0] - bp[0], 4), round(o[1] - bp[1], 4), round(o[2] * sg, 4)], "flyScale": [SHRINK] * 3, "fold": [0, 0, 0]})
    d["parts"] = out
    n = 0
    for s in sh:
        if PAD(s["id"]) and s.get("mirror"): s["bone"] = "wpadL"; n += 1
    open(path, "w").write(fmt(d) + "\n")   # (bg.save's layout, without its feather-root pass: nothing here moves a blade)
    print(f"{name}: {n} pad shapes on wpad, drawn in aloft to {(pad["c"][2] - o[2]) * 100:.1f} cm under its middle")

if __name__ == "__main__":
    names = sys.argv[1:]
    if names == ["all"]: names = sorted(f[:-5] for f in os.listdir(ROOT) if f.endswith(".json"))
    for n in names: run(n)
