# varB.py [names...] -- (2026-11-07, B) the named coats of the birds whose generators are their own files (the fliers
#   drawn aloft, the swan, the duck, the flamingo): apply(d, name) sets them on a definition -- each generator calls it
#   before it saves -- and run as a script it patches the assets in place (their shapes untouched but for the colour
#   keys a coat needs of its own: the eagle's head, the owls' tufts gated `tufts`).
import sys, json
from bg import load, save

def _recolour(d, ids, col):
    for q in d["sculpt"]["shape"]:
        if q.get("id") in ids: q["color"] = col

def eagle(d):
    d["colors"].setdefault("head", d["colors"]["brown"]); d["colors"].setdefault("face", d["colors"]["dark"]); d["colors"].setdefault("tailTip", d["colors"]["dark"])
    _recolour(d, ("skull", "brow", "shelf"), "@head"); _recolour(d, ("face",), "@face")
    for q in d["sculpt"]["shape"]:
        if q.get("id") == "tail" and q.get("type") == "feathers": q["tip"] = "@tailTip"
    return [{"name": "golden eagle"},
            {"name": "bald eagle", "head": "#f2f0ea", "face": "#eeece6", "gold": "#f2f0ea", "beak": "#e8b830", "cere": "#e8c040", "tail": "#f0eee8", "tailTip": "#e8e6e0",
             "eye": "#e8d890", "brown": "#3a2616", "warm": "#46301e", "pale": "#4a3a2c", "dark": "#2a1c12"}]

def owl(d):
    for q in d["sculpt"]["shape"]:
        if q.get("id") == "tuft": q["when"] = "tufts"
    d["params"] = {**(d.get("params") or {}), "tufts": True}
    return [{"name": "Eurasian eagle-owl"},
            {"name": "snowy owl", "scale": .85, "params": {"tufts": False}, "tawny": "#f2f0ea", "buff": "#f6f4ee", "face": "#f8f6f2", "rim": "#e8e6e0", "dark": "#3a3632",
             "remex": "#f0eee8", "tip": "#d8d4cc", "cov": "#ecebe4", "eye": "#f2cc2a", "beak": "#2a2826"},
            {"name": "barn owl", "scale": .62, "params": {"tufts": False}, "tawny": "#c8a060", "buff": "#f6f0e2", "face": "#f8f4ec", "rim": "#c49460", "dark": "#a89480",
             "remex": "#dcc08a", "tip": "#a88a62", "cov": "#c49a5e", "eye": "#141010", "beak": "#d8c8b0"}]

def swan(d):
    return [{"name": "mute swan"},
            {"name": "black swan", "scale": .92, "white": "#1e1c20", "shade": "#18161a", "bill": "#c4242a", "eye": "#c8302a", "black": "#1a181c"}]

def duck(d):
    cs = d.get("coats") or []
    cs = [c for c in cs if c.get("name") != "Pekin duck"]
    # (2026-11-08: was #f4f2ea all over -- under the lights a flat white blob, "pure white". Now cream with a yellow cast
    #  on the head and neck, the wing and tertials a shade darker so the folded feathers' edges read, the flank feathers
    #  edged (fedge), the belly shaded down (sculpt.shade, gated on "pekin"), the bill orange-yellow)
    return cs + [{"name": "Pekin duck", "params": {"pekin": True}, "flank": "#ece4ce", "back": "#e2d9c3", "breast": "#efe7d2", "head": "#efe5c8",
                  "ring": "#efe5c8", "rump": "#e0d7c2", "tail": "#e9e1cc", "wing": "#e0d7c1", "tert": "#d3c9b2", "prim": "#c9bfa8", "spec": "#dad1bb",
                  "bar": "#eee7d5", "bill": "#f2a02a", "nail": "#e8b468", "belly": "#f1ebdb", "stripe": "#efe5c8", "fedge": "#d8ceb6", "saddle": "#f2a02a", "eye": "#2a3a5a"}]

def flamingo(d):
    return [{"name": "greater flamingo"},
            {"name": "juvenile flamingo", "scale": .9, "body": "#e6dfd8", "pale": "#efeae4", "neck": "#e2dad2", "covert": "#b8aa9c", "tert": "#d4cac0", "bill": "#c8c0c0", "leg": "#9a9290"}]

def buzzard(d):
    return [{"name": "common buzzard"},
            {"name": "pale buzzard", "chest": "#f0e8d8", "belly": "#e4d6c0", "head": "#d8c8aa", "nape": "#b89a74", "crown": "#a88a64", "face": "#e8dcc6", "thigh": "#e2d2b8",
             "lining": "#ece2d0", "streak": "#9a7a56", "remex": "#d4cabc", "tail": "#b8a48a"},
            {"name": "dark buzzard", "back": "#3a2618", "chest": "#4a3220", "belly": "#3e2a1a", "head": "#3a2618", "nape": "#34221a", "crown": "#34221a", "face": "#44301e",
             "thigh": "#3e2a1a", "lining": "#3e2a1a", "cov": "#3a2618", "covTip": "#4a3422", "tail": "#5a4632", "tailTip": "#3a2a1c", "streak": "#2a1a10"}]

def falcon(d):
    return [{"name": "peregrine falcon"},
            {"name": "kestrel", "scale": .74, "back": "#b4643a", "cov": "#b4643a", "covTip": "#7e4226", "edge": "#b4643a", "head": "#7e8898", "nape": "#7e8898", "crown": "#7a8494",
             "face": "#ece2d2", "mous": "#4a4a50", "chest": "#ecd4aa", "belly": "#e2c69c", "thigh": "#e2c69c", "bar": "#6a3e26", "tail": "#7e8898", "tailTip": "#1e1e22",
             "remex": "#3e302a", "remTip": "#1e1a18", "pTip": "#1a1614", "lining": "#efe4d6"}]

def heron(d):
    W = "#f4f4f0"
    return [{"name": "grey heron"},
            {"name": "great egret", "grey": W, "dark": "#ecece8", "white": W, "pale": "#f0f0ec", "black": "#eeeeea", "bill": "#e8c040", "leg": "#1e1e20", "eye": "#e8d040"}]

COATS = {"heron": heron, "eagle": eagle, "owl": owl, "swan": swan, "duck": duck, "flamingo": flamingo, "buzzard": buzzard, "falcon": falcon}

def apply(d, name):
    if name in COATS: d["coats"] = COATS[name](d)
    return d

if __name__ == "__main__":
    for n in (sys.argv[1:] or COATS):
        d = apply(load(n), n); save(n, d, root=False); print(n, [c.get("name") for c in d["coats"]])
