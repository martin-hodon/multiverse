#!/usr/bin/env python3
# tri2sheet.py (2026-11-21): a creature's runs of `tri` faces -- a fin, a flipper written face by face (sealib.fin,
# cetlib.plates) -- made into `sheet` shapes (sculpt.js prepareSheet; README "Fins as sheets, manes as brushes"), in the
# JSON as it stands (the scripts that wrote these no longer reproduce them).
#   python3 tri2sheet.py [--min N] [--dry] FILE.json ...
# A RUN: faces next to each other in the shape list, of one fin (their ids PREFIX_N, or PREFIXN) and alike in every
# other key (bone, r, k, colour, pat, frame, mirror ...). So each sheet is one bone and one thickness and hands back,
# through sheetTris, exactly the faces it was (same corners, order, r, bone; ids PREFIX_i -- a second run of the same
# fin PREFIXb, ...). Corners shared by faces are one point. Runs under --min faces (default 6) are left as they are.
# The file is written back in its own layout: one shape a line, or json indent 2 (as the fish scripts wrote it).
import json, re, sys

def prefix(i):   # (the fin a face is of: its id less the numbers -- web3_1, dorsal12 -> web, dorsal)
    return re.sub(r"[\d_]+$", "", i) or i

def ids_of(run, sid):   # (the faces' ids, when they run on: prefix + n, n + 1, ...; None when they are sid_0, sid_1 ...)
    ms = [re.match(r"^(.*?)(\d+)$", s["id"]) for s in run]
    if all(ms) and len({m[1] for m in ms}) == 1 and all(int(m[2]) == int(ms[0][2]) + j for j, m in enumerate(ms)):
        pre, n0 = ms[0][1], int(ms[0][2])
        return None if (pre, n0) == (sid + "_", 0) else [pre, n0]
    return False   # (they do not: the faces become sid_0, sid_1 ...)

def sheet_of(run, sid):
    pts, idx, tris = [], {}, []
    for s in run:
        for c in ("a", "b", "c"):
            key = tuple(round(v, 9) for v in s[c])
            if key not in idx: idx[key] = len(pts); pts.append([*s[c], s.get("r", 0)])
            tris.append(idx[key])
    rest = {k: v for k, v in run[0].items() if k not in ("id", "type", "a", "b", "c", "r")}
    out = {"id": sid, "type": "sheet"}
    ids = ids_of(run, sid)
    if ids: out["ids"] = ids
    if "bone" in rest: out["bone"] = rest.pop("bone")
    out["pts"] = pts; out["tris"] = tris; out.update(rest)
    return out

def convert(shapes, mn):
    out, i, used, made, at, gone = [], 0, {}, [], {}, set()
    sig = lambda s: (prefix(s["id"]), json.dumps({k: v for k, v in s.items() if k not in ("id", "a", "b", "c")}, sort_keys=True))
    while i < len(shapes):
        s = shapes[i]
        if s.get("type") != "tri" or "id" not in s: out.append(s); i += 1; continue
        j = i
        while j < len(shapes) and shapes[j].get("type") == "tri" and "id" in shapes[j] and sig(shapes[j]) == sig(s): j += 1
        run = shapes[i:j]
        if len(run) >= mn:
            m = re.match(r"^(.*)_0$", s["id"])   # (faces X_0, X_1 ...: the sheet is X, and needs no ids)
            if m and ids_of(run, m[1]) is None and m[1] not in used: sid = m[1]; used[sid] = 1
            else: p = prefix(s["id"]); n = used.get(p, 0); used[p] = n + 1; sid = p + ("" if n == 0 else "bcdefghijk"[n - 1])
            sh = sheet_of(run, sid); out.append(sh); made.append((sh["id"] + (" RENAMED" if ids_of(run, sh["id"]) is False else ""), len(run), len(sh["pts"])))
            at[run[0]["id"]] = sh; gone.update(r["id"] for r in run[1:])
        else: out += run
        i = j
    return out, made, at, gone

def main():
    a = sys.argv[1:]; mn = 6; dry = "--dry" in a
    if "--min" in a: mn = int(a[a.index("--min") + 1]); del a[a.index("--min"):a.index("--min") + 2]
    for f in [x for x in a if x != "--dry"]:
        txt = open(f).read(); d = json.loads(txt)
        shapes, made, at, gone = convert(d["sculpt"]["shape"], mn)
        print(f, "shapes", len(d["sculpt"]["shape"]), "->", len(shapes), " ".join(f"{i}({n} faces, {p} pts)" for i, n, p in made))
        if dry or not made: continue
        write(f, txt, d, shapes, at, gone)

def write(f, txt, d, shapes, at, gone):
    """the file written back in its own layout: a json dump dumped again; one shape a line, a run's first line the new
    shape (at: first id -> shape), its other lines gone (gone: ids) -- checked against the shape list"""
    if json.dumps(d, indent=2) + ("\n" if txt.endswith("\n") else "") == txt:   # (a json dump: dumped again)
        d["sculpt"]["shape"] = shapes; open(f, "w").write(json.dumps(d, indent=2) + ("\n" if txt.endswith("\n") else "")); return
    lines, new = txt.split("\n"), []   # (one shape a line: a run's first face's line the sheet, its others gone)
    sid = lambda l: (re.match(r'\s*\{"id": "([^"]+)"', l) or [None, None])[1]
    for l in lines:
        i = sid(l)
        if i in at: new.append(re.match(r"\s*", l)[0] + json.dumps(at[i]) + ","); continue
        if i in gone: continue
        new.append(l)
    for i in range(1, len(new)):   # (no comma before the list's end)
        if new[i].lstrip().startswith("]") and new[i - 1].rstrip().endswith(","): new[i - 1] = new[i - 1].rstrip()[:-1]
    out = "\n".join(new); d2 = json.loads(out)
    assert d2["sculpt"]["shape"] == shapes, "line rewrite disagrees with the shape list"
    open(f, "w").write(out)

if __name__ == "__main__": main()
