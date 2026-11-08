# rooster.py -- the rooster: a game cock of its own (not the hen yard's chicken variant): the chicken's body with its
#   `rooster` params baked in, bigger (1.15) and taller, a red-junglefowl's colours -- the gold-orange hackles and saddle,
#   deep red back and coverts, a green-black breast and the black tail and sickles glossed green to blue-violet at the
#   tips (the sheen), longer arching sickles, a taller comb. Reads the chicken (chicken.py first), writes rooster.json
import json, copy
from bg import *
from raptor import scale_parts

P = {"rooster": True, "hen": False}
def resolve(o):
    if isinstance(o, dict):
        if "when" in o:
            names = o["when"] if isinstance(o["when"], list) else [o["when"]]
            if not all(P.get(n) for n in names): return None
            if "v" in o and len(o) == 2: return resolve(o["v"])
            o = {k: v for k, v in o.items() if k != "when"}
        return {k: resolve(v) for k, v in o.items()}
    if isinstance(o, list):
        return [x for x in (resolve(v) for v in o) if x is not None]
    return o

d = resolve(copy.deepcopy(load("chicken")))
d["name"] = "rooster"
d["_about"] = ("a rooster: a game cock -- the chicken's plump blended body bigger and more upright, the tall serrated comb and long "
               "wattles, the gold-orange hackles over the neck and the saddle falling over the wing's end, deep red back and "
               "coverts, a green-black breast, and the black tail under three long arching sickles glossed green and violet; "
               "he crows at dawn")
d.pop("params", None); d.pop("variants", None); d.pop("coats", None)
d["flags"] = {"shy": 4, "peck": 1.1, "print": "bird"}
d["colors"].update({"body": "#8a2414", "breast": "#16211d", "wing": "#7a1e12", "tail": "#122a22", "head": "#e0862a",
                    "comb": "#c8241c", "face": "#c8301f", "lobe": "#e8e0d0", "saddle": "#d4741c", "hackle": "#e69a2a",
                    "sickle": "#123a2e", "sickleTip": "#3a2a6a", "hackleTip": "#c05a14", "beak": "#c8a050", "leg": "#9a8a50"})
S = 1.15
scale_parts(d["parts"], S)
sh = shift(d["sculpt"]["shape"], [0, 0, 0], S)
for s in sh:
    if s.get("type") == "feathers":
        if s["id"].startswith("sickle"):
            s["tip"] = "@sickleTip"
            for r in s["rows"]:   # (a quarter longer, from the root)
                r["to"] = [a + (b - a) * 1.25 for a, b in zip(r["at"], r["to"])]
        if s["id"] == "tail": s["tip"] = "@sickleTip"
        if s["id"] in ("hackleF", "saddleF"): s["tip"] = "@hackleTip"
    if s.get("id", "").startswith("comb") and s.get("type") == "ell":
        s["r"][1] *= 1.2; s["c"][1] += .004
d["sculpt"]["shape"] = sh
d["sculpt"]["_about"] = "x forward, y up, z left, metres; the chicken's sculpt with its rooster shapes, scaled 1.15 (rooster.py)"
e = d["sculpt"]["eyes"]
for k in ("at", "from"): e[k] = [v * S for v in e[k]]
e["r"] *= S
save("rooster", d)
print("rooster:", len(d["parts"]), "parts,", len(sh), "shapes")
