# coats.py NAME... -- adds coats / variants / params to the audit's animals, textually (each file read fresh, its other
# lines untouched): a "params"/"coats"/"variants" line after its "colors" line; pattern and shade gates by exact replace
import json, sys
R = "/home/martin/store/apps/multiverse/assets/creatures/"
J = lambda o: json.dumps(o, ensure_ascii=False)

SPEC = {
  "others/crocodile": dict(
    coats=[{"name": "Nile crocodile"}, {"name": "Nile crocodile"},
           {"name": "saltwater crocodile", "scale": 1.25, "back": "#4a4632", "flank": "#7a7048", "belly": "#e0d4a8", "scute": "#2c2a1c", "band": "#1e1c12",
            "inter": "#8a8458", "plate": "#5a5638", "flankBar": "#3a3624", "keel": "#34301e"}],
    variants={"American alligator (colour)": {"scale": 1.0, "colors": {"back": "#1e221c", "flank": "#2a2e26", "belly": "#d8d4c0", "scute": "#121410", "band": "#0c0e0a",
              "inter": "#3a3c30", "plate": "#262a20", "flankBar": "#181a14", "keel": "#161812", "eye": "#8a7a3a"}}}),
  "others/turtle": dict(
    coats=[{"name": "red-eared slider"}, {"name": "red-eared slider"},
           {"name": "yellow-bellied slider", "red": "#e2c43e", "plastron": "#e6d26e", "streak": "#d4bc4a"},
           {"name": "European pond turtle", "scale": 0.72, "shell": "#26261c", "shell2": "#2e2e22", "seam": "#101008", "streak": "#c8aa44",
            "skin": "#2a2c20", "chin": "#a8963e", "yellow": "#c8aa44", "red": "#2a2c20", "plastron": "#b0944a", "beak": "#1a1c14"}]),
  "others/spider": dict(
    coats=[{"name": "wolf spider"}, {"name": "wolf spider"},
           {"name": "wolf spider (grey)", "carapace": "#4a4440", "pale": "#9a9288", "abdomen": "#3e3a36", "leg": "#4a4440", "ring": "#8a8278", "dark": "#1a1816"}],
    variants={"tarantula (Mexican red-knee)": {"scale": 3.0, "colors": {"carapace": "#2a2420", "pale": "#c86a2a", "dark": "#100c0a", "abdomen": "#1c1816",
              "leg": "#201a16", "ring": "#e0702a"}},
              "garden cross spider": {"scale": 0.65, "colors": {"carapace": "#8a6a40", "abdomen": "#a8783c", "pale": "#f2ead8", "leg": "#9a7a4a",
              "ring": "#5a4024", "dark": "#3a2614"}}}),
  "others/scorpion": dict(
    coats=[{"name": "brown scorpion"}, {"name": "brown scorpion"},
           {"name": "deathstalker (yellow)", "body": "#b8a050", "body2": "#a89040", "under": "#d8c890", "pale": "#e0d8b0", "leg": "#c8b060",
            "claw": "#b09848", "sting": "#c0a050", "tip": "#3a2a18"}],
    variants={"emperor scorpion": {"scale": 1.8, "colors": {"body": "#141618", "body2": "#101214", "under": "#2a2c2e", "leg": "#1a1c1e", "claw": "#121416",
              "sting": "#3a2a1a", "tip": "#0a0808", "pale": "#5a5040"}}}),
  "sea/octopus": dict(
    coats=[{"name": "common octopus"}, {"name": "common octopus (flushed red)", "body": "#b8442a"}, {"name": "common octopus (pale, camouflaged)", "body": "#c4a486"}],
    variants={"giant Pacific octopus": {"scale": 3.0, "colors": {"body": "#a83c26"}}}),
  "sea/ray": dict(
    coats=[{"name": "common stingray"}, {"name": "common stingray"}, {"name": "common stingray (dark)", "body": "#3e3a34"},
           {"name": "common stingray (sandy)", "body": "#a89272"}]),
  "sea/trout": dict(
    params={"brown": True, "rainbow": False},
    coats=[{"name": "brown trout"}, {"name": "brown trout"},
           {"name": "rainbow trout", "params": {"brown": False, "rainbow": True}, "body": "#a8ac98", "back": "#56644c", "pale": "#eeeee6", "fin": "#8c8a74",
            "tail": "#6e7260", "adipose": "#7a7c66", "gill": "#7a5a50"}],
    reps=[('"pat": "trout"', '"pat": [{"when": "rainbow", "v": "rainbow"}, {"when": "brown", "v": "trout"}]'),
          ('"shade": {"back": "#5a5630", "belly": "#efe0b0",', '"shade": {"back": "@back", "belly": "@pale",')]),
  "sea/carp": dict(
    params={"wild": True, "koi": False, "ogon": False},
    coats=[{"name": "common carp"}, {"name": "common carp"},
           {"name": "common carp (dark, river)", "body": "#8a7a3e", "back": "#4a4424", "pale": "#d8c88e", "fin2": "#8a5a36"}],
    variants={"koi (kohaku)": {"params": {"wild": False, "koi": True}, "colors": {"body": "#f2eee8", "back": "#c43a1c", "pale": "#f4f0ea", "lip": "#f0e2d8",
              "fin": "#ece6de", "fin2": "#f0e4da", "tail": "#ece2d8", "gill": "#c8b8a8", "line": "#d8d0c6"}},
              "koi (yamabuki ogon)": {"params": {"wild": False, "ogon": True}, "colors": {"body": "#e8b43a", "back": "#d8a028", "pale": "#f0c860", "lip": "#e8c070",
              "fin": "#e0aa40", "fin2": "#e8b048", "tail": "#d8a438", "gill": "#a87a20", "line": "#c89a30"}}},
    reps=[('"pat": "rowscales"', '"pat": [{"when": "koi", "v": "koi"}, {"when": "wild", "v": "rowscales"}, {"when": "ogon", "v": "rowscales"}]'),
          ('"shade": {"back": "#5e5026"', '"shade": {"when": "wild", "back": "#5e5026"')]),
  "others/dragonfly": dict(
    coats_add=[{"name": "banded demoiselle", "body": "#1c58c8", "thorax": "#1440a0", "wing": "#8098c4"}]),
}

for name in sys.argv[1:]:
    sp = SPEC[name]; p = R + name + ".json"
    s = open(p).read()
    lines = s.split("\n")
    d = json.loads(s)
    for a, b in sp.get("reps", []):
        n = s.count(a); assert n > 0, (name, a)
    for a, b in sp.get("reps", []):
        s = s.replace(a, b)
    lines = s.split("\n")
    ci = [i for i, l in enumerate(lines) if l.startswith('  "colors": ')]
    assert len(ci) == 1, name
    ins = []
    for key in ("params", "coats", "variants"):
        if key in sp:
            assert key not in d, (name, key)
            ins.append('  "%s": %s,' % (key, J(sp[key])))
    if "coats_add" in sp:
        ki = [i for i, l in enumerate(lines) if l.startswith('  "coats": ')]
        assert len(ki) == 1, name
        cs = d["coats"] + sp["coats_add"]
        lines[ki[0]] = '  "coats": %s,' % J(cs)
    lines[ci[0] + 1:ci[0] + 1] = ins
    out = "\n".join(lines)
    json.loads(out)
    open(p, "w").write(out)
    print("ok", name, len(ins), "lines;", sum(s.count(b) for a, b in sp.get("reps", [])), "replaced")
