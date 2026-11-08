import sys, copy
from lib import *
from canid import canid

import math
def species(name, rigmod, cols, opts, about, tris=(4200, 1400), extra=None, tail=None, shade=None, coat=None):
    d = orig(name)
    d = copy.deepcopy(d)
    for k, v in rigmod.items():
        if isinstance(v, dict) and isinstance(d.get(k), dict): d[k] = {**d[k], **v}
        else: d[k] = v
    d["c"] = {**d.get("c", {}), **cols}
    d.pop("sculpt", None)
    if tail: d["tail"] = {**d["tail"], "tuft": 0}; d["tail"].pop("tuftOut", None); d["tail"].pop("tuftColor", None)
    save(name, d)                      # the rig first: its joints are what the shapes are laid on
    shapes, eyes = canid(name, d, opts)
    if extra: shapes += extra(d)
    if name in ("dog", "fox"):   # (audit 2026-11-07: the coat read as plastic -- ticked fur, coatpat.js agouti, over the furred shapes)
        for q in shapes:
            if q.get("color") in ("@body", "@saddle", "@head", "@leg", "@mask", "@throat", "@belly", "@chestc", "@ear") and q.get("op") != "paint": q["pat"] = "agouti"
    keep = ["tail\\d*", "tailTuft"]
    if tail:
        # THE TAIL SCULPTED (the rig's tube was a plain sausage beside the body): its own girth down its length, the end its own colour
        tipc, t0 = tail.get("tip", (None, 1.1))
        ring = lambda t, P0, P1, r: {"color": tipc if t >= t0 else "@tail"}
        shapes += arc_tail(d["tail"], ring, n=tail.get("n", 9), k=0.45, kc=0.25, rad=tail["rad"], extra=tail.get("extra"), tip=tipc or "@tail")
        keep = []
    out = {"name": d["name"], "_about": about}
    out.update({k: v for k, v in d.items() if k not in ("name", "_about")})
    out["sculpt"] = {"keep": keep, "mesh": {"tris": list(tris)}, "shape": shapes, "eyes": eyes}
    if shade: out["sculpt"]["shade"] = shade
    if coat: out["sculpt"]["coat"] = coat
    save(name, out)

# NOTE (2026-11-07, sky-steeds/mammal agent): assets/creatures/mammals/wolf.json is FINISHED DOWNSTREAM of this function --
# scratchpad var/wlf.py takes its output (kept as var/wolf_r1.json) and adds the round-2 head, ears, jointed legs, agouti fur
# and coats' leg tones. Regenerating here alone reverts those: run  python3 var/wlf.py <this output> mammals/wolf.json  after.
def wolf():
    species("wolf",
            {"rear": [-0.2, 0.56, 0, 0.3, 0.2, 0.14], "front": [0.2, 0.57, 0, 0.3, 0.23, 0.15],
             "legs": {"front": [0.28, 0.45, 0.115, 0.205], "hind": [-0.24, 0.46, 0.1, 0.225], "radii": [0.068, 0.05, 0.036], "foot": [0.058, 0.034, 0.05], "shoulder": 1.15, "thigh": 1.4},
             "tail": {"c": [-0.85, 1.0], "R": 0.6, "a0": -0.89, "a1": -1.72, "r1": 0.05, "r2": 0.07, "n": 5, "sway": 14, "speed": 0.9, "tuft": 0.055, "tuftColor": "#2a2622", "tuftOut": 0.03}},
            {"body": "#6e685e", "saddle": "#36322e", "belly": "#d9d1c1", "chestc": "#cfc6b4", "throat": "#d6cebd", "mask": "#c6beae",
             "head": "#6c665c", "muzzleC": "#9a907e", "lip": "#ece6da", "nose": "#151210", "ear": "#6e655a", "earIn": "#d8cfbf",
             "leg": "#a8997e", "foot": "#b8ab92", "tail": "#5e584f", "eye": "#c79a32", "lid": "#1e1a16", "muzzle": "#b3a996", "tip": "#24201c"},
            {"ear": {"cup": {"bi": [0.0262, 0.0033, -0.0197], "bo": [-0.0148, -0.0164, 0.0476], "mid": [-0.0205, -0.0049, 0.0028], "bulge": [-0.0075, 0.0203, 0.0444], "tip": [-0.0082, 0.0886, 0.0246], "r": 0.0095, "k": 0.008, "apart": 0.004, "inTip": 0.55}}, "deep": 0.79, "tuck": 1.15, "kx": 1.08, "kh": 1.14, "throat": 0.85},
            "a grey wolf SCULPTED on its rig (2026-11-05, gen: scratchpad sc/carn/gen/canids.py): long-legged and narrow-chested over a deep pale brisket, a tucked loin, a sloping croup, big paws; a broad cranium with flared pale cheeks, a long muzzle, short erect ears; countershaded -- a dark saddle and nape, buff flanks, cream legs and belly, a white-lipped mask -- and a bushy dark-tipped tail hanging low",
            tris=(6400, 2000),
            shade={"back": 0.72, "belly": 1.25, "k": 0.12, "low": 1.25, "on": "@body"},
            tail={"rad": lambda t: 0.035 + 0.04 * math.sin(math.pi * min(1.0, 0.15 + t * 0.95)) ** 0.7, "tip": ("@tip", 0.8), "extra": {"hair": 1}})

def fox():
    species("fox",
            {"rear": [-0.13, 0.29, 0, 0.17, 0.085, 0.08], "front": [0.1, 0.3, 0, 0.16, 0.09, 0.085],
             # (audit 2026-11-07) COATS by seed: the red, the CROSS fox (a dark cross over the shoulders, dark legs and belly), the
             # SILVER (black, frosted, the white tail tip kept); VARIANT `arctic`: the arctic fox's white winter coat, smaller
             "coats": [{"name": "red"},
                       {"name": "cross", "body": "#b0602c", "saddle": "#3a2a20", "head": "#b4642e", "mask": "#b86a34", "muzzleC": "#8a4a24",
                        "belly": "#3a2e26", "chestc": "#4a3a30", "throat": "#d8cfc2", "tail": "#a85a2a"},
                       {"name": "silver", "body": "#2e2a28", "saddle": "#1e1b1a", "head": "#34302e", "mask": "#3a3634", "muzzleC": "#2a2624",
                        "belly": "#2a2624", "chestc": "#3a3634", "throat": "#4a4644", "lip": "#9a9690", "ear": "#141010", "earIn": "#5a5652",
                        "leg": "#141210", "foot": "#121010", "tail": "#2e2a28", "muzzle": "#4a4644"}],
             "variants": {"arctic": {"scale": 0.82, "colors": {"body": "#ece8e0", "saddle": "#e4e0d6", "head": "#efebe3", "mask": "#efebe3",
                                                              "muzzleC": "#e8e4dc", "belly": "#f2efe8", "chestc": "#f4f1ea", "throat": "#f4f1ea",
                                                              "lip": "#f4f1ea", "ear": "#e2ded4", "earIn": "#d8d2c6", "leg": "#e6e2d8",
                                                              "foot": "#ece8e0", "tail": "#ece8e0", "tip": "#f4f1ea", "muzzle": "#efebe3",
                                                              "eye": "#9a6a2a"}}},
             "neck": [0.22, 0.35, 0, 0.34, 0.45, 0, 0.075, 0.066],
             "legs": {"front": [0.16, 0.255, 0.06, 0.12], "hind": [-0.16, 0.255, 0.065, 0.13], "radii": [0.04, 0.028, 0.02], "foot": [0.038, 0.022, 0.03]},
             "tail": {"c": [-0.54, 0.59], "R": 0.4, "a0": -0.81, "a1": -1.85, "r1": 0.05, "r2": 0.085, "n": 5, "tuft": 0.075, "tuftColor": "#efe9de", "sway": 14, "speed": 0.7, "tuftOut": 0.05}},
            {"body": "#c25a22", "saddle": "#a8481a", "belly": "#efe8dc", "chestc": "#f0eadf", "throat": "#f1ebe1", "mask": "#c96a30",
             "head": "#c66024", "muzzleC": "#c9692e", "lip": "#f2ede4", "nose": "#141010", "ear": "#1e1612", "earIn": "#efe6d8",
             "leg": "#2a1e16", "foot": "#1c1410", "tail": "#bb5520", "eye": "#c88a26", "lid": "#1a1210", "muzzle": "#d9c8b8", "tip": "#efe9de"},
            {"ear": {"cup": {"bi": [0.032, 0.004, -0.024], "bo": [-0.018, -0.02, 0.058], "mid": [-0.025, -0.006, 0.0034], "bulge": [-0.0092, 0.0248, 0.0542], "tip": [-0.01, 0.108, 0.03], "r": 0.011, "apart": 0.005, "col": "@head", "back": "@ear", "tipCol": "@ear", "inTip": 0.5, "inBase": 0.86, "inLift": 1.3}},
             "topline": {"occX": 0.06, "occY": 0.004, "ra": 0.058, "rb": 0.5}, "noNape": True, "kx": 1.08, "blunt": 0.8, "pupil": "slit", "leg": 0.9, "gneck": 1.35, "eyeY": -0.014, "bib": True, "throat": 1.1},
            "a red fox SCULPTED on its rig (2026-11-05, gen: scratchpad sc/carn/gen/canids.py): slender, long in the body and short in the leg; a narrow pointed muzzle with white lips, chin and throat, big pointed ears black behind, black stockings on all four legs, a white chest and belly, and the full brush with its white tip",
            tris=(6000, 1900),
            extra=lambda d: [{"id": "tailRoot", "type": "cone", "bone": "tail", "a": [-0.2, 0.306, 0], "b": [-0.292, 0.284, 0], "ra": 0.046, "rb": 0.04,
                              "k": 0.025, "kc": 0.012, "color": "@tail"}],
            tail={"rad": lambda t: 0.034 + 0.036 * math.sin(math.pi * min(1.0, t * 1.0)) ** 0.8 + 0.012 * t, "tip": ("@tip", 0.86), "extra": {}})

def dog():
    species("dog",
            {"headScale": 0.92, "neck": [0.29, 0.47, 0, 0.405, 0.57, 0, 0.115, 0.095], "head": [0.46, 0.625, 0, 0.12], "muzzle": [0.46, 0.615, 0, 0.645, 0.578, 0, 0.078, 0.045], "nose": [0.65, 0.592, 0, 0.025], "ears": [0.428, 0.712, 0.066, 0.412, 0.585, 0.092, 0.05, 0.035], "eyes": [0.54, 0.665, 0.065, 0.02], "rear": [-0.14, 0.42, 0, 0.22, 0.145, 0.13], "front": [0.13, 0.43, 0, 0.23, 0.15, 0.14],
             "legs": {"front": [0.2, 0.34, 0.09, 0.15], "hind": [-0.17, 0.35, 0.1, 0.17], "radii": [0.062, 0.043, 0.031]}, "coats": [{"name": "tan"},
                       {"name": "black sheepdog", "body": "#2a2624", "saddle": "#221e1c", "head": "#2a2624", "mask": "#2a2624", "leg": "#2a2624", "foot": "#e8e2d6", "belly": "#e8e2d6",
                        "chestc": "#e8e2d6", "throat": "#e8e2d6", "muzzleC": "#e8e2d6", "lip": "#e8e2d6", "ear": "#1f1c1a", "earIn": "#1f1c1a", "tail": "#2a2624", "muzzle": "#e8e2d6"},
                       {"name": "grey", "body": "#8e8a84", "saddle": "#7a766f", "head": "#8e8a84", "mask": "#8e8a84", "leg": "#7a766f", "foot": "#8e8a84", "belly": "#b0aca4",
                        "chestc": "#b0aca4", "throat": "#b0aca4", "muzzleC": "#a09c95", "lip": "#b0aca4", "ear": "#5e5a54", "earIn": "#5e5a54", "tail": "#7a766f", "muzzle": "#b0aca4"},
                       # (audit 2026-11-07: more of the farm dogs' colours -- the one drop-eared body in a retriever's gold, a
                       #  black-and-tan, a chocolate, a black, a white with a liver saddle)
                       {"name": "golden", "body": "#cf9e5c", "saddle": "#c08c4c", "head": "#cc9a58", "mask": "#cc9a58", "leg": "#c8955a", "foot": "#d2a466",
                        "belly": "#e0bc84", "chestc": "#e2c08a", "throat": "#dcb67e", "muzzleC": "#c8955a", "lip": "#b88a52", "ear": "#b8844a",
                        "earIn": "#b8844a", "tail": "#c8955a", "muzzle": "#d4a864"},
                       {"name": "black and tan", "body": "#1e1a18", "saddle": "#161312", "head": "#1e1a18", "mask": "#8a5628", "leg": "#8a5628",
                        "foot": "#8a5628", "belly": "#7e4e24", "chestc": "#8a5628", "throat": "#1e1a18", "muzzleC": "#8a5628", "lip": "#8a5628",
                        "ear": "#161312", "earIn": "#161312", "tail": "#1e1a18", "muzzle": "#8a5628"},
                       {"name": "chocolate", "body": "#5a3a24", "saddle": "#4e321e", "head": "#5a3a24", "mask": "#5a3a24", "leg": "#52341f", "foot": "#5a3a24",
                        "belly": "#6a4630", "chestc": "#6a4630", "throat": "#5e3e28", "muzzleC": "#5a3a24", "lip": "#4e321e", "ear": "#4a2e1c",
                        "earIn": "#4a2e1c", "tail": "#52341f", "muzzle": "#5e3e28"},
                       {"name": "black", "body": "#1c1918", "saddle": "#161413", "head": "#1c1918", "mask": "#1c1918", "leg": "#181615", "foot": "#1c1918",
                        "belly": "#242020", "chestc": "#242020", "throat": "#1c1918", "muzzleC": "#1c1918", "lip": "#161413", "ear": "#141211",
                        "earIn": "#141211", "tail": "#181615", "muzzle": "#201c1b"},
                       {"name": "white and liver", "body": "#ece6da", "saddle": "#6a3e26", "head": "#6a3e26", "mask": "#ece6da", "leg": "#ece6da",
                        "foot": "#f2ede4", "belly": "#f2ede4", "chestc": "#f2ede4", "throat": "#ece6da", "muzzleC": "#ece6da", "lip": "#e2dace",
                        "ear": "#5e3620", "earIn": "#5e3620", "tail": "#ece6da", "muzzle": "#ece6da"}],
             "tail": {"c": [-0.261, 0.173], "R": 0.35, "a0": 1.7, "a1": 2.6, "r1": 0.04, "r2": 0.02, "n": 5, "sway": 25, "speed": 1.3},
             "_coats": "COATS (species.js coatDef): tan, a black sheepdog with a white muzzle, chest and socks, a grey; golden, black and tan, chocolate, black, white with a liver saddle and head (audit 2026-11-07) -- each the whole table the sculpt's shapes paint by"},
            {"body": "#a8743e", "saddle": "#3a2a1e", "belly": "#d2b080", "chestc": "#ece2d0", "throat": "#d8c09a", "mask": "#a8743e",
             "head": "#a06c38", "muzzleC": "#8a5c32", "lip": "#6a4a2c", "nose": "#221a17", "ear": "#6b4423", "earIn": "#6b4423", "black": "#141010",
             "leg": "#8e6234", "foot": "#a87a48", "tail": "#86592e", "eye": "#4a2f1a", "lid": "#2a1a10", "muzzle": "#b88d58"},
            {"ear": {"drop": True, "soft": True, "len": 1.3, "out": 0.02}, "skullW": 1.2, "eyeX": 0.047, "sink": 0.6, "blunt": 1.45, "dome": -0.5, "throat": 0.8, "kb": 1.12, "brisket": 0.72, "kx": 1.0, "kh": 1.12, "gneck": 1.38, "eye": 0.95, "flews": 1.5, "stop": 0.03, "stepStop": True, "lab": True, "mouthLine": True, "seamL": 0.026, "noseBig": 1.3, "noseFlat": 0.78, "noseZ": 1.1, "noseX": 0.0105, "noseWet": 0.15, "mouth": True, "saddle": 1.3},
            "a dog SCULPTED on its rig (2026-11-05, gen: scratchpad sc/carn/gen/canids.py): a medium farm dog -- a deep chest and tucked waist, a broad skull with a marked stop over a blunt muzzle, drop ears; its coats (species.js coatDef) recolour the same keys",
            tris=(6200, 1900),
            shade={"back": 0.9, "belly": 1.12, "on": "@body"},
            tail={"rad": lambda t: 0.036 - 0.02 * t, "extra": {"hair": 1}})

for f in sys.argv[1:] or ["wolf", "fox", "dog"]: globals()[f]()
