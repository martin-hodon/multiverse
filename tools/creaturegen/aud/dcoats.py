# dcoats.py [--write] : the dinosaurs' coats (flat colour tables over `c`, creatures.js dressed) and `young`
# Each coat: a skin transform (hue toward a target, saturation and value factors) over the skin keys, plus optional
# display colours (frill, crest, plates). Coat 0 is the asset as it is (`{"name": ...}` only).
import json, colorsys, sys
D = "/home/martin/store/apps/multiverse/assets/creatures/dinosaurs/"
SKIN = {"body", "front", "neck", "head", "muzzle", "leg", "tail", "back", "flank", "belly", "lip", "brow", "cheek", "scute",
        "keel", "dome", "domeRim", "knob", "spine", "ridge", "face", "limb", "arm"}
def hx(c): return "#%02x%02x%02x" % tuple(max(0, min(255, round(v * 255))) for v in c)
def rgb(c):
    if isinstance(c, int): return ((c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255)
    return tuple(int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))
def tr(c, hue=None, hk=.6, s=1., v=1., belly=False):
    h, l, sat = colorsys.rgb_to_hls(*rgb(c))
    if hue is not None:
        d = ((hue / 360 - h + .5) % 1) - .5; h = (h + d * hk) % 1
    sat = min(1, sat * s); l = min(.92, l * (v if not belly else (1 + (v - 1) * .5)))
    return hx(colorsys.hls_to_rgb(h, l, sat))
# per family: [name, transform] ; base name first
CAMO = [("forest", dict(hue=95, hk=.55, s=1.15, v=.78)), ("sand", dict(hue=38, hk=.7, s=.9, v=1.22)), ("slate", dict(hue=215, hk=.95, s=.32, v=.92))]
TERRA = [("dark", dict(hue=25, hk=.4, s=1.1, v=.72)), ("ochre", dict(hue=34, hk=.75, s=1.35, v=1.18)), ("grey", dict(hue=40, hk=.5, s=.3, v=1.02))]
PLAN = {
  "tyrannosaur": ("olive", TERRA), "allosaurus": ("brown", CAMO), "carnotaurus": ("umber", [("rust", dict(hue=14, hk=.6, s=1.5, v=1.08)), ("dun", dict(hue=40, hk=.6, s=.9, v=1.25)), ("charcoal", dict(hue=30, hk=.2, s=.5, v=.62))]),
  "dilophosaurus": ("olive", CAMO), "pachycephalosaurus": ("brown", CAMO), "diplodocus": ("olive", [("grey", dict(hue=40, hk=.5, s=.3, v=1.05)), ("rufous", dict(hue=22, hk=.6, s=1.3, v=.95)), ("dusk", dict(hue=80, hk=.3, s=.9, v=.72))]),
  "parasaurolophus": ("green", [("tan", dict(hue=36, hk=.7, s=1.0, v=1.12)), ("russet", dict(hue=16, hk=.6, s=1.2, v=.9)), ("deep green", dict(hue=110, hk=.5, s=1.2, v=.75))]),
  "stegosaurus": ("green", [("tan", dict(hue=38, hk=.7, s=.95, v=1.15)), ("grey-blue", dict(hue=210, hk=.95, s=.3, v=.95)), ("dark", dict(hue=90, hk=.3, s=.9, v=.68))]),
  "ankylosaurus": ("khaki", [("rust", dict(hue=18, hk=.55, s=1.3, v=.9)), ("charcoal", dict(hue=40, hk=.2, s=.4, v=.68)), ("sand", dict(hue=42, hk=.6, s=1.1, v=1.22))]),
  "triceratops": ("olive", CAMO), "styracosaurus": ("tawny", [("olive", dict(hue=70, hk=.6, s=1.0, v=.9)), ("grey", dict(hue=40, hk=.5, s=.3, v=1.0)), ("dark", dict(hue=28, hk=.3, s=1.0, v=.7))]),
  "diabloceratops": ("grey-brown", [("rust", dict(hue=16, hk=.5, s=1.4, v=.95)), ("olive", dict(hue=75, hk=.6, s=1.1, v=.92)), ("sand", dict(hue=40, hk=.65, s=1.0, v=1.22))]),
}
# display colours a coat may also change (the ceratopsians' frills, the crests, the plates): per coat name
DISPLAY = {
  "triceratops": {"forest": {"frill": "#6e4a2c", "frillIn": "#9a7a48"}, "sand": {"frill": "#a8642e", "frillIn": "#d0a060"}, "slate": {"frill": "#5a4a58", "frillIn": "#9a8478", "rim": "#2e2630"}},
  "styracosaurus": {"olive": {"frill": "#7a3a22", "frillIn": "#a86a3a"}, "grey": {"frill": "#5c4c54", "frillIn": "#9a8a80"}, "dark": {"frill": "#b0402a", "frillIn": "#d88a4a"}},
  "diabloceratops": {"rust": {"frill": "#8a2a1c", "frillIn": "#c88a3a"}, "olive": {"frill": "#5a3424", "frillIn": "#a07040"}, "sand": {"frill": "#9a5028", "frillIn": "#d8a858"}},
  "parasaurolophus": {"tan": {"crest": "#b0703a", "crestTop": "#804a2a"}, "russet": {"crest": "#c8a040", "crestTop": "#8a6a2a"}, "deep green": {"crest": "#c04a30", "crestTop": "#8a2a1c"}},
  "stegosaurus": {"tan": {"plate": "#a84a2e", "plateRim": "#8a3a24"}, "grey-blue": {"plate": "#9a7040", "plateRim": "#7a5430"}, "dark": {"plate": "#c87040", "plateRim": "#a85a30"}},
  "dilophosaurus": {"forest": {"crest": "#7a4a30", "crestRim": "#a84a2a"}, "sand": {"crest": "#8a6a48", "crestRim": "#b0582e"}, "slate": {"crest": "#6a5a60", "crestRim": "#c0582e"}},
  "pachycephalosaurus": {"forest": {"dome": "#6a6a48"}, "sand": {"dome": "#b0a07a"}, "slate": {"dome": "#7a7a80"}},
}
YOUNG = {"triceratops": dict(s=.3, n=1, side=2.4, hop=.04, name="triceratops calf"),
         "parasaurolophus": dict(s=.3, n=1, side=2.0, hop=.05, name="parasaurolophus juvenile"),
         "stegosaurus": dict(s=.3, n=1, side=2.2, hop=.03, name="stegosaurus juvenile")}
w = "--write" in sys.argv
for sp, (base, coats) in PLAN.items():
    f = D + sp + ".json"; txt = open(f).read(); d = json.loads(txt)
    t = d.get("c") or d.get("colors")
    out = [{"name": base}]
    for nm, x in coats:
        c = {"name": nm}
        for k, v in t.items():
            if k in SKIN: c[k] = tr(v, **x, belly=(k == "belly"))
        c.update(DISPLAY.get(sp, {}).get(nm, {}))
        out.append(c)
    d["coats"] = out
    if sp in YOUNG: d["young"] = YOUNG[sp]
    print(sp, [c["name"] for c in out], "young" if sp in YOUNG else "")
    if w:
        # keep the file's layout: the new keys appended as one line each before the final brace
        assert txt.rstrip().endswith("}")
        body = txt.rstrip()[:-1].rstrip()
        for key in ("coats", "young"):
            if key not in d or f'"{key}"' in txt: continue
            body += ',\n  "%s": %s' % (key, json.dumps(d[key]) if key == "young" else "[\n    " + ",\n    ".join(json.dumps(c) for c in d[key]) + "\n  ]")
        open(f, "w").write(body + "\n}\n"); json.load(open(f))
