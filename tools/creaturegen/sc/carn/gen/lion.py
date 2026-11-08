from felid import *

# a male lion: taller on the leg and shorter in the body than a tiger (1.2 m at the shoulder, 2 m head-body), a longer
# squarer muzzle, a broad nose; the mane a heavy collar from behind the ears over the neck, shoulders and chest -- golden
# round the face, dark behind -- in locks (the coat's quills, long and leaning back); a long thin tail ending in a black tuft
P = {"s": 0.95, "sho": 0.43, "hip": -0.56, "dyF": 0.15, "dyH": 0.13, "g": 1.0, "legF": 1.45, "legH": 1.1, "gz": 0.95, "hs": [1.2, 1.12, 1.1],
     "tail": {"R": 0.6, "a0": -0.6, "a1": -2.45, "r1": 0.05, "r2": 0.034}}

def build():
    M = Map(P)
    def fwd(dx):
        def f(q):
            for k in ("c", "a", "b"):
                if k in q: q[k] = [q[k][0] + dx * M.S, q[k][1], q[k][2]]
            return q
        return f
    edits = {
        "chest": {"pat": None},
        # a deeper chest: the keel lower and fuller
        "keel": lambda q: {**q, "color": "@body", "pat": None, "c": [q["c"][0], q["c"][1] - 0.03 * M.S, 0], "r": [q["r"][0], q["r"][1] * 1.3, q["r"][2] * 1.1]}, "withers": {"pat": None}, "loin": {"pat": None},
        "rump": {"pat": None}, "belly": {"color": "@cream", "pat": None}, "pouch": {"color": "@cream"}, "scapula": {"pat": None},
        "arm": {"pat": None}, "triceps": {"pat": None}, "forearm": {"pat": None}, "flexor": {"pat": None}, "thigh": {"pat": None},
        "gaskin": {"pat": None}, "hock": {"pat": None}, "neck": {"pat": None}, "throat": {"color": "@pale"},
        "skull": {"pat": None, "color": "@head"}, "cheek": {"pat": None, "color": "@head"},
        "bridge": lambda q: {**fwd(0.015)(q), "color": "@bridge"},
        "muzzle": lambda q: {**fwd(0.02)(q), "color": "@head"},
        "pad": lambda q: {**fwd(0.02)(q), "color": "@muzzle"},
        "chin": lambda q: {**fwd(0.01)(q), "color": "@white"},
        "jowl": {"color": "@cream"},
        "nose": lambda q: {**fwd(0.02)(q), "r": [q["r"][0] * 1.0, q["r"][1] * 1.0, q["r"][2] * 1.15], "color": "@nose"},
        "brow": {"color": "@pale"},
        "ear": {"color": "@ear"},
        "earIn": {"color": "@cream"},
        "paw": {"color": "@pale"}, "hpaw": {"color": "@pale"},
    }
    def add(M, P):
        S = M.S
        # THE MANE a big smooth volume (soft locks: fleece), the coat's strands only at its edge (the rear rim, the hang under the chest)
        # (MATTE: no hair sheen, no fleece lumps -- both read as glossy zig-zag cracks on a volume this big)
        mane = {}
        edge = {"coat": True}
        h = lambda p: H(M, P, p)
        t = lambda p: Tr(M, p)
        return [
            # round the face: a ruff behind the cheeks and over the crown (on the head: it turns with it)
            {"id": "maneCrown", "type": "ell", "bone": "head", "c": h([0.92, 1.1, 0]), "r": [0.13 * S, 0.16 * S, 0.24 * S], "k": 0.06 * S, "color": "@maneF", **mane},
            {"id": "maneRuff", "type": "ell", "bone": "head", "c": h([0.95, 0.98, 0.16]), "r": [0.1 * S, 0.23 * S, 0.13 * S], "rot": [-22, 0, -8], "k": 0.06 * S, "color": "@maneF", "mirror": True, **mane},
            {"id": "maneBeard", "type": "ell", "bone": "head", "c": h([0.95, 0.85, 0]), "r": [0.13 * S, 0.15 * S, 0.17 * S], "k": 0.06 * S, "color": "@maneF", **mane},
            # the mass over the neck, and hanging under it to the chest (on the neck)
            {"id": "maneNeck", "type": "ell", "bone": "neck", "c": t([0.7, 0.98, 0]), "r": [0.37 * S, 0.34 * S, 0.3 * S], "rot": [0, 0, 28], "k": 0.1 * S, "color": "@mane", **mane},
            {"id": "maneChest", "type": "ell", "bone": "neck", "c": t([0.66, 0.64, 0]), "r": [0.25 * S, 0.34 * S, 0.24 * S], "rot": [0, 0, -12], "k": 0.09 * S, "color": "@mane", **edge},
            # the mane down over each SHOULDER (the pale shoulder showed through), and LOCKS: soft lobes laid on the volume a shade
            # lighter round the face and darker behind -- mass and tone without a gloss
            {"id": "maneShoulder", "type": "ell", "bone": "neck", "c": t([0.5, 0.8, 0.165]), "r": [0.24 * S, 0.3 * S, 0.165 * S], "rot": [0, 0, 12], "k": 0.09 * S, "kc": 0.06 * S, "color": "@mane", "mirror": True, **edge},
            *[{"id": f"lock{i}", "type": "ell", "bone": "neck", "c": t(c), "r": [r[0] * S, r[1] * S, r[2] * S], "rot": [0, 0, rz], "k": 0.05 * S, "kc": 0.05 * S, "color": col, "mirror": True}
              for i, (c, r, rz, col) in enumerate([([0.82, 1.02, 0.17], [0.1, 0.16, 0.08], 20, "@maneF"), ([0.7, 0.86, 0.2], [0.12, 0.17, 0.08], 10, "@maneM"),
                                                   ([0.6, 1.06, 0.16], [0.14, 0.12, 0.09], 30, "@maneD"), ([0.72, 0.68, 0.14], [0.11, 0.15, 0.08], -10, "@maneD"),
                                                   ([0.88, 0.8, 0.15], [0.08, 0.14, 0.08], 0, "@maneF")])],
            # ...and on down over the upper arm to the elbow (in profile the pale arm showed below the shoulder's mane)
            {"id": "maneArm", "type": "ell", "bone": "neck", "c": t([0.48, 0.6, 0.17]), "r": [0.18 * S, 0.17 * S, 0.155 * S], "rot": [0, 0, 8], "k": 0.08 * S, "kc": 0.05 * S, "color": "@mane", "mirror": True, **edge},
            # the mane's FRINGE low on the chest, back past the elbow (the keel's pale showed through there)
            {"id": "maneFringe", "type": "ell", "bone": "body", "c": t([0.46, 0.56, 0.085]), "r": [0.17 * S, 0.11 * S, 0.1 * S], "rot": [0, 0, -8], "k": 0.08 * S, "kc": 0.05 * S, "color": "@mane", "mirror": True, **edge},
            # ...and back over the withers, darkest at its end
            {"id": "maneBack", "type": "ell", "bone": "body", "c": t([0.45, 0.92, 0]), "r": [0.3 * S, 0.2 * S, 0.26 * S], "rot": [0, 0, 12], "k": 0.1 * S, "color": "@maneD", **edge},
            # the dark LIP line, and black ear backs
            {"id": "lip", "type": "ell", "bone": "head", "c": h([1.13, 0.926, 0.055]), "r": [0.05 * S, 0.006 * S, 0.012 * S], "rot": [0, 28, -8],
             "k": 0.004 * S, "kc": 0.002 * S, "color": "@black", "mirror": True,
             "seat": {"from": h([1.06, 0.93, 0]), "out": -0.1}},
            {"id": "earBack", "type": "ell", "bone": "earL", "c": h([0.887, 1.181, 0.0935]), "r": [0.014 * S, 0.046 * S, 0.04 * S], "rot": [-20, 0, 0],
             "k": 0.006 * S, "kc": 0.002 * S, "color": "@black", "mirror": True},
        ]
    M, R, shapes, eyes = felid(P, edits, add, drop=("ruff",))
    eyes["iris"] = "@eye"
    hsm = sum(P["hs"]) / 3
    shapes = head_pass(shapes, eyes, lambda p: H(M, P, p), M.S * hsm, {"tear": "@tear", "tearW": 0.006, "ears": 0.9, "earZ": 0.01, "nose": 0.9, "eyeBall": "#6a4a16", "lip": None})
    out = {"name": "lion",
           "_about": "a male lion SCULPTED on the cat frame (2026-11-05, gen: scratchpad sc/carn/gen/lion.py from the tiger's shapes): taller on the leg and shorter in the body than the tiger, a long square muzzle and broad nose; the mane a collar of locks (the coat's quills) from behind the ears over neck, shoulders and chest, golden round the face and dark behind; plain tawny, paler beneath; a long thin tail with a black tuft",
           "use": "creatures/frames/cat",
           "params": {"s": P["s"], "tuft": 0.075, "tailSway": 14},
           **{k: R[k] for k in ("rear", "front", "neck", "head", "muzzle", "nose", "ears", "eyes")},
           "legs": R["legs"], "tail": R["tail"],
           "colors": {"body": "#c49a52", "head": "#c99f58", "muzzle": "#dcc28e", "ear": "#5e3e22", "leg": "#bd934c", "eye": "#b8862e",
                      "nose": "#a06a58", "tuft": "#2a1c12", "tail": "#bd934c", "white": "#efe6d2", "cream": "#e3cfa2", "pale": "#d8b87a",
                      "black": "#1a1410", "bridge": "#bf9450", "maneF": "#a4742e", "mane": "#7a4e22", "maneD": "#4a2e16", "maneM": "#8e5e28", "tear": "#7a5530"},
           "mount": {"h": 2, "speed": 1.7},
           "print": "paw",
           "sculpt": {"keep": ["tail\\d*", "tailTuft"], "mesh": {"tris": [9000, 2800]}, "shape": shapes, "eyes": eyes,
                      "coat": {"gap": 0.04, "len": 0.11, "r": 0.014, "sides": 3, "lean": 1.0, "vary": 0.3, "skirt": -1.2, "drop": 0,
                               "face": 0.5, "rise": 0.4, "tip": "#a06a2c", "base": "#4a2e16", "dark": 0.45, "darkTip": "#2e1c0e", "hold": 0.55}}}
    save("lion", out)

build()
