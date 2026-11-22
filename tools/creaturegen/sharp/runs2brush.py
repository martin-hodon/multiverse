#!/usr/bin/env python3
# runs2brush.py (2026-11-22): a creature's runs of like `tube`s or `horn`s -- a horse's mane locks, a bumblebee's pile,
# a mosquito's antenna whorls, a butterfly's wing-pattern panels (fins: `items`) -- made into `brush` bundles (bodyspec.js brushStrands; README "Fins as sheets, manes as
# brushes"), in the JSON as it stands. bodyspec.js makes each back into the same tubes or horns, in the same order,
# with the same ids and keys, before anything else sees them: the mesh is the same.
#   python3 runs2brush.py [--min N] [--dry] [--only REGEX] FILE.json ...
# A RUN: shapes next to each other, all tubes, horns or fins, alike in every key but id, color and pts (a fin's root, edge), their ids one
# numbering -- STEM0, STEM1 ... (`first`, `step`), or STEMg_j with j 0..per-1 in each group g (`per`, `groups`). Colours: one
# `color`, or a `palette` and a `pick` a strand. Runs under --min shapes (default 10) are left; --only: ids matching it.
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tri2sheet import write

def numbering(ids):
    """the ids' rule: (stem, extra keys) or None"""
    m = [re.match(r"^(.*?[^\d_])(\d+)$", i) for i in ids]
    if all(m) and len({x[1] for x in m}) == 1:
        n0 = int(m[0][2]); st = int(m[1][2]) - n0 if len(m) > 1 else 1
        if st and all(int(x[2]) == n0 + j * st for j, x in enumerate(m)):
            return m[0][1], {**({"first": n0} if n0 else {}), **({"step": st} if st != 1 else {})}
    m = [re.match(r"^(.*?[^\d_])(\d+)_(\d+)$", i) for i in ids]
    if all(m) and len({x[1] for x in m}) == 1:
        per = 1 + max(int(x[3]) for x in m)
        gs = []
        for j, x in enumerate(m):
            if int(x[3]) != j % per: return None
            if j % per == 0: gs.append(int(x[2]))
            elif int(x[2]) != gs[-1]: return None
        if len(ids) % per: return None
        return m[0][1], {"per": per, "groups": gs}
    return None

def convert(shapes, mn, only):
    out, made, at, gone, i = [], [], {}, set(), 0
    OWN = {"tube": ("pts",), "horn": ("pts",), "fin": ("root", "edge")}   # (each one's own: a strand's points; a fin's lines)
    sig = lambda s: json.dumps({k: v for k, v in s.items() if k not in ("id", "color") + OWN.get(s.get("type"), ())}, sort_keys=True)
    stem = lambda s: re.sub(r"[\d_]+$", "", s.get("id", ""))
    ok = lambda s: s.get("type") in OWN and "id" in s and all(isinstance(s.get(k), list) for k in OWN[s["type"]]) and (not only or re.search(only, s["id"]))
    while i < len(shapes):
        s = shapes[i]
        if not ok(s): out.append(s); i += 1; continue
        j = i
        while j < len(shapes) and ok(shapes[j]) and sig(shapes[j]) == sig(s) and stem(shapes[j]) == stem(s): j += 1
        run = shapes[i:j]; rule = numbering([q["id"] for q in run]) if len(run) >= mn else None
        if not rule: out += run; i = j; continue
        pre, extra = rule
        own = OWN[s["type"]]; rest = {k: v for k, v in s.items() if k not in ("id", "type", "color") + own}
        cols = [q.get("color") for q in run]
        b = {"id": pre, "type": "brush"}
        if s["type"] != "tube": b["kind"] = s["type"]
        if "bone" in rest: b["bone"] = rest.pop("bone")
        b.update(extra)
        if len(set(map(json.dumps, cols))) == 1:
            if cols[0] is not None: b["color"] = cols[0]
        else:
            keys = list(dict.fromkeys(map(json.dumps, cols)))
            b["palette"] = {str(k): json.loads(c) for k, c in enumerate(keys)}; b["pick"] = [keys.index(json.dumps(c)) for c in cols]
        b.update(rest)
        if own == ("pts",): b["strands"] = [q["pts"] for q in run]
        else: b["items"] = [{k: q[k] for k in own} for q in run]
        out.append(b); at[run[0]["id"]] = b; gone.update(q["id"] for q in run[1:]); made.append((pre, len(run), s["type"]))
        i = j
    return out, made, at, gone

def main():
    a = sys.argv[1:]; mn = 10; dry = "--dry" in a; only = None
    if "--min" in a: mn = int(a[a.index("--min") + 1]); del a[a.index("--min"):a.index("--min") + 2]
    if "--only" in a: only = a[a.index("--only") + 1]; del a[a.index("--only"):a.index("--only") + 2]
    for f in [x for x in a if x != "--dry"]:
        txt = open(f).read(); d = json.loads(txt)
        shapes, made, at, gone = convert(d["sculpt"]["shape"], mn, only)
        print(f, "shapes", len(d["sculpt"]["shape"]), "->", len(shapes), " ".join(f"{p}({n} {t}s)" for p, n, t in made))
        if dry or not made: continue
        write(f, txt, d, shapes, at, gone)

if __name__ == "__main__": main()
