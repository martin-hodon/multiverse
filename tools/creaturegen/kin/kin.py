#!/usr/bin/env python3
"""KIN (2026-11-21): the species written as ANOTHER's kin -- a cheetah as the leopard, slimmer and paler; a jackal as the
wolf at .6 of its size in its own colours; a canary as the sparrow, yellow. Each is a small definition over its base
(`use`: the base's path -- defs.js chain), saying only what differs:

  size     the whole creature at that share of the base's size (creatures.js buildCreature `size`)
  tone     every colour of the base's turned toward a hue (`hue` degrees, `hm` how far, 1 all the way), its saturation
           and lightness scaled (`sat`, `lit`) -- but its eyes, nose, bill, teeth, tongue (KEEP) as they are
  colors   over the base's own colour table, after the tone (its keys: python3 kin.py --keys BASE)
  params   over the base's params (a frame's `s`, a horse's `mane`...)
  plain    True: no coat pattern (the base's spots and stripes taken off every shape, and its `pat`)
  recol    {id regex: "@colour"}: those shapes in another colour (a puma's belly spots in its belly's white)
  drop     [id regex]: those shapes taken out
  short    the tail (the shape `tail`'s points) cut to that share
  shape    sculpt shapes over the base's by id ({"id": "tail", "r": [...]} -- the named-list merge)
  coats    its own coats (else one, its own name -- never the base's black panther)

  python3 kin.py [names]      writes assets/creatures/<dir>/<name>.json and adds them to assets/index.json
  python3 kin.py --keys BASE  the base's colour keys
"""
import json, os, re, sys, colorsys
from kinlist import KIN
ROOT = "/home/martin/store/apps/multiverse/assets/"

def load(path): return json.load(open(ROOT + path + ".json"))
def flat(path):
    """the base with what it stands on (only what kin.py needs: its colours, its shapes)"""
    d = load(path)
    if "use" in d:
        b = flat(d["use"]); b.update({k: v for k, v in d.items() if k not in ("colors", "c")})
        b["colors"] = {**b.get("colors", {}), **(d.get("colors") or d.get("c") or {})}
        return b
    d["colors"] = d.get("colors") or d.get("c") or {}
    return d

KEEP = {"eye", "iris", "lid", "nose", "nostril", "tooth", "tongue", "mouth", "dark", "black", "pupil", "ring", "tear", "lip", "white"}
hls = lambda c: colorsys.rgb_to_hls(*(int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)))
def toned(c, hue=None, hm=1.0, sat=1.0, lit=1.0, to=None, amt=1.0, ref=None):
    h, l, s = hls(c)
    if to:                                   # (the base's REF colour -- its body's -- made `to`, every other moved with it)
        th, tl, ts = hls(to); rh, rl, rs = hls(ref)
        d = ((th - h + .5) % 1) - .5; h = (h + d * amt) % 1
        s = s + (min(1, ts * (s / rs) if rs > .02 else ts) - s) * amt
        l = min(1, max(0, l + (tl - rl) * amt * (l / rl if l < rl and rl > 0 else (1 - l) / (1 - rl) if rl < 1 else 1)))
    if hue is not None:
        d = ((hue / 360 - h + .5) % 1) - .5; h = (h + d * hm) % 1
    s = min(1, s * sat); l = min(1, l * lit) if lit <= 1 else l + (1 - l) * (lit - 1)
    return "#%02x%02x%02x" % tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l, s))

def write(name, k):
    base = k["base"]; d0 = flat(base); dir_ = k.get("dir", base.split("/")[1])
    out = {"name": name, "_about": k["about"], "use": base}
    if k.get("size", 1) != 1: out["size"] = k["size"]
    if k.get("params"): out["params"] = k["params"]
    if k.get("loose"): k = {**k, "colors": {c: v for c, v in k.get("colors", {}).items() if c in d0["colors"]}}   # (a palette written for several bases: what this one has)
    unknown = [c for c in k.get("colors", {}) if c not in d0["colors"]]
    if unknown: print(f"  {name}: colour keys the base lacks: {unknown}")
    cols = {}
    if k.get("tone"):
        t = dict(k["tone"]); keep = KEEP | set(t.pop("keep", ()))
        if t.get("to"): t["ref"] = d0["colors"][t.pop("on", None) or next((r for r in ("body", "back", "fill", "skin", "cape") if r in d0["colors"]), next(iter(d0["colors"])))]
        cols = {c: toned(v, **t) for c, v in d0["colors"].items() if c not in keep and isinstance(v, str) and v.startswith("#")}
    cols.update(k.get("colors", {}))
    k = {**k, "colors": cols}
    if k.get("colors"): out["colors" if "colors" in load(base) or "c" not in load(base) else "c"] = k["colors"]
    shape = {s["id"]: dict(s) for s in k.get("shape", [])}
    if k.get("plain"):
        if d0.get("pat"): out["pat"] = None
        for s in d0.get("sculpt", {}).get("shape", []) if isinstance(d0.get("sculpt"), dict) else []:
            if s.get("pat") is not None and s.get("id"): shape.setdefault(s["id"], {"id": s["id"]})["pat"] = None
    for rx, colour in k.get("recol", {}).items():          # (shapes by id -- a regular expression -- in another colour: the puma's belly spots)
        for s in d0.get("sculpt", {}).get("shape", []):
            if s.get("id") and re.fullmatch(rx, s["id"]): shape.setdefault(s["id"], {"id": s["id"]})["color" if "color" in s else "col"] = colour
    for rx in k.get("drop", ()):                           # (shapes by id taken out: the beluga's dorsal fin, a flounder's whip of a tail)
        for s in d0.get("sculpt", {}).get("shape", []):
            if s.get("id") and re.fullmatch(rx, s["id"]): shape[s["id"]] = {"id": s["id"], "drop": True}
        for q in d0.get("parts", []) if isinstance(d0.get("parts"), list) else []:   # (and parts so named: the ray's tail, from a flounder)
            if q.get("id") and re.fullmatch(rx, q["id"]): out.setdefault("parts", []).append({"id": q["id"], "drop": True})
    if k.get("short"):                                     # (the tail cut to that share of its points: a hamster's, a vole's)
        for s in d0.get("sculpt", {}).get("shape", []):
            if s.get("id") == "tail" and s.get("pts"): shape.setdefault("tail", {"id": "tail"})["pts"] = s["pts"][:max(2, round(len(s["pts"]) * k["short"]))]
    if shape: out["sculpt"] = {"shape": list(shape.values())}
    out["coats"] = k.get("coats", [{"name": name}])
    out["variants"] = None
    for w in ("flags", "young", "graze", "beg"):
        if w in k: out[w] = k[w]
    path = f"creatures/{dir_}/{name}"
    json.dump(out, open(ROOT + path + ".json", "w"), indent=1, ensure_ascii=False)
    return path, dir_

CATS = {"mammals": "Mammals", "birds": "Birds", "sea": "Sea life", "others": "Others"}
def index(paths):
    ix = json.load(open(ROOT + "index.json"))
    for p, dir_ in paths:
        cat = next(c for c in ix["categories"] if c.get("name", c.get("id")) == CATS[dir_] or any(q.startswith(f"creatures/{dir_}/") for q in c["paths"]))
        if p not in cat["paths"]: cat["paths"].append(p); cat["paths"].sort()
    json.dump(ix, open(ROOT + "index.json", "w"), indent=2, ensure_ascii=False); open(ROOT + "index.json", "a").write("\n")

if __name__ == "__main__":
    if sys.argv[1:2] == ["--keys"]:
        d = flat(sys.argv[2]); print(" ".join(f"{k}={v}" for k, v in d["colors"].items())); sys.exit()
    force = "--force" in sys.argv; names = [a for a in sys.argv[1:] if a != "--force"] or list(KIN)
    # (2026-11-21: every kin was rebuilt as its own model by rework/<group>/ -- cheetah, puma, pronghorn and pony still on
    #  a base's rig by `use`, with their own sculpt -- so this writes nothing unless told to overwrite those)
    kin_now = lambda n: False
    skipped = [n for n in names if not force and not kin_now(n)]
    if skipped: print(f"{len(skipped)} rebuilt in rework/, left alone (--force to write the kin over them)")
    names = [n for n in names if n not in skipped]
    index([write(n, KIN[n]) for n in names])
    print(len(names), "kin written")
