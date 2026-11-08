from felid import *

P = {"s": 0.66, "sho": 0.42, "hip": -0.6, "g": 0.93, "legF": 1.0, "legH": 0.96, "dyF": -0.07, "dyH": -0.06, "hs": [1.24, 1.14, 1.1], "gz": 0.95, "gneck": 1.0,
     "tail": {"R": 0.76, "a0": -0.62, "a1": -2.55, "r1": 0.064, "r2": 0.05}}
ROS, SPOT = 18, 21
LEGF = lambda M: {"o": "$legFLu", "u": [0, -1, 0], "r": 0.05 * M.S}
LEGH = lambda M: {"o": "$legHLu", "u": [0, -1, 0], "r": 0.05 * M.S}
HEADF = lambda M: {"o": "$head", "u": [0, 1, 0], "v": [1, 0, 0], "r": 0.05 * M.S}

def build():
    M = Map(P)
    ros = {"pat": ROS, "frame": "body"}
    spot_b = {"pat": SPOT, "frame": "body"}
    hf = {"pat": SPOT, "frame": HEADF(M)}
    edits = {
        "chest": ros, "loin": ros, "rump": ros, "scapula": ros,
        # the neck: the head's small spots growing toward the body's rosettes (a frame small enough to mix the two)
        "neck": {"pat": SPOT, "frame": "body"},   # (the head's small solid spots run on down the neck; rosettes from the shoulder)
        # the ground GRADED: golden back, cream lower flank, white below (wide paint blends between them)
        "keel": {"pat": None, "color": "@white", "kc": 0.05}, "pouch": {"pat": None, "color": "@white", "kc": 0.05},
        "belly": lambda q: {**q, "pat": None, "color": "@white", "kc": 0.06, "r": [q["r"][0], q["r"][1] * 1.08, q["r"][2] * 1.15]},
        "withers": {**ros, "color": "@back"},
        "arm": ros, "triceps": ros, "thigh": ros,
        "forearm": {"pat": SPOT, "frame": LEGF(M), "color": "@body"}, "flexor": {"pat": SPOT, "frame": LEGF(M), "color": "@body"},
        "pastern": {"pat": SPOT, "frame": LEGF(M), "color": "@body"}, "paw": {"pat": SPOT, "frame": LEGF(M), "color": "@leg"},
        "gaskin": {"pat": SPOT, "frame": LEGH(M), "color": "@body"}, "hock": {"pat": SPOT, "frame": LEGH(M), "color": "@body"},
        "hpaw": {"pat": SPOT, "frame": LEGH(M), "color": "@leg"},
        "throat": lambda q: {**q, "color": "@white", "kc": 0.02, "r": [q["r"][0] * 0.85, q["r"][1] * 0.75, q["r"][2] * 0.8], "c": [q["c"][0], q["c"][1] + 0.01, 0]},
        "skull": hf, "cheek": {**hf, "color": "@body"}, "ruff": {**hf, "color": "@body"},
        "bridge": {**hf, "color": "@body"}, "muzzle": {**hf, "color": "@body"},
        # the TIGER's head geometry, scaled (hs): ground colour on the muzzle, cream only on the whisker pads, white chin and throat
        "pad": {"color": "@cream"},
        "chin": {"color": "@white"},
        "jowl": {**hf, "color": "@body"},
        "brow": {**hf, "color": "@body"},
        "ear": lambda q: {**q, "color": "@body", "r": list(q["r"])},
        "earIn": lambda q: {**q, "color": "@cream", "r": list(q["r"])},
    }
    # the leopard's cheek is less flared than a tiger's ruff: pull the ruff in
    ruff0 = edits["ruff"]
    def ruff(q):
        q["r"] = [q["r"][0] * 0.8, q["r"][1] * 0.75, q["r"][2] * 0.75]; return {**q, **ruff0}
    edits["ruff"] = ruff
    mz0 = edits["muzzle"]
    edits["muzzle"] = lambda q: {**q, **mz0, "r": [q["r"][0] * 1.04, q["r"][1], q["r"][2] * 0.92]}   # slightly longer and narrower than the tiger's
    def add(M, P):
        S = M.S
        # a darker golden SPINE band, and the BELLY'S big solid black spots (decals: the coat's own spots are too small
        # there -- pat 21 is the head's small-spot cell -- and came out grey specks)
        out = [{"id": "spine", "type": "ell", "c": Tr(M, [-0.15, 0.93, 0]), "r": [0.6 * S, 0.035 * S, 0.1 * S], "k": 0.05 * S, "kc": 0.04 * S,
                "color": "@back", **ros}]
        import random
        rnd = random.Random(7)
        i = 0
        # (scattered: three staggered rows over a ~15 cm band, 2-6 cm, soft-edged; some places empty)
        for row, (z0, y0) in enumerate([(0.02, 0.293), (0.062, 0.31), (0.104, 0.338)]):
            x = -0.3 + row * 0.022
            while x < 0.21:
                if rnd.random() < 0.8:
                    r = rnd.uniform(0.009, 0.026) * (0.8 if row == 2 else 1.0)
                    zz = z0 + rnd.uniform(-0.014, 0.014)
                    out.append(decal(f"bspot{i}", "body", [x + rnd.uniform(-0.015, 0.015), y0 + (zz - z0) * 0.5, zz], [x, 0.47, 0], [r * rnd.uniform(1.0, 1.5), r, r], "@black",
                                     sink=0.6, kc=0.0045, rot=[0, rnd.uniform(-50, 50), 0]))
                    i += 1
                x += rnd.uniform(0.05, 0.08)
        for d in out:
            if d.get("bone") == "body": d.pop("bone")
        return out + [
            # the back of each ear black (its rim and inside the coat's), a white spot on it
            {"id": "earBack", "type": "ell", "bone": "earL", "c": H(M, P, [0.887, 1.181, 0.0935]), "r": [0.014 * S, 0.046 * S, 0.04 * S], "rot": [-20, 0, 0],
             "k": 0.006 * S, "kc": 0.002 * S, "color": "@ear", "mirror": True},
            {"id": "earSpot", "type": "ell", "bone": "earL", "c": H(M, P, [0.874, 1.183, 0.093]), "r": [0.006 * S, 0.015 * S, 0.015 * S], "rot": [-20, 0, 0],
             "k": 0.004 * S, "kc": 0.002 * S, "color": "@white", "mirror": True},
        ]
    M, R, shapes, eyes = felid(P, edits, add)
    eyes["iris"] = "@eye"
    hsm = sum(P["hs"]) / 3
    shapes = head_pass(shapes, eyes, lambda p: H(M, P, p), M.S * hsm, {"tear": "@tear", "tearW": 0.0036, "noseC": "@nose", "ears": 0.8, "earZ": 0.02, "earY": -0.012, "nose": 0.82, "eyeBall": "#6a5014", "eye": 0.8, "snout": 0.006})
    # (audit 2026-11-07, round 2) the EARS: proper rounded ears, not cream knobs -- each a thinner, broader shell, its back
    # black breaking through the back face, the white spot set on that black
    E = {q["id"]: q for q in shapes if q["id"] in ("ear", "earIn", "earBack", "earSpot")}
    if len(E) == 4:
        e, ei, eb, es = E["ear"], E["earIn"], E["earBack"], E["earSpot"]
        e["r"] = [e["r"][0] * 0.62, e["r"][1] * 1.12, e["r"][2] * 1.12]; e["k"] = e["k"] * 0.4
        ei["r"] = [ei["r"][0] * 0.8, e["r"][1] * 0.66, e["r"][2] * 0.66]; ei["c"] = [e["c"][0] + e["r"][0] * 0.55, ei["c"][1] - 0.003, ei["c"][2]]; ei["color"] = "@pale"
        # (the black wraps the back half and shows as a dark rim round the edge from the front)
        eb["r"] = [e["r"][0] * 0.75, e["r"][1] * 1.0, e["r"][2] * 1.0]; eb["c"] = [e["c"][0] - e["r"][0] * 0.42, e["c"][1], e["c"][2]]; eb["k"] = 0.002
        es["r"] = [es["r"][0] * 0.9, es["r"][1] * 1.25, es["r"][2] * 1.25]; es["c"] = [eb["c"][0] - eb["r"][0] + es["r"][0] * 0.35, es["c"][1] - 0.002, es["c"][2]]
    d = orig("leopard")
    out = {"name": "leopard",
           "_about": "the leopard SCULPTED on the cat frame (2026-11-05, gen: scratchpad sc/carn/gen/leopard.py from the tiger's shapes): long and low on short strong legs, a big broad head; true rosettes on the trunk and upper limbs, solid spots on the head, the lower legs and the white belly; white chin, throat and underparts; round ears black behind with a white spot",
           "use": "creatures/frames/cat",
           "params": {"s": P["s"], "tuft": 0.0, "tailSway": 14},
           **{k: R[k] for k in ("rear", "front", "neck", "head", "muzzle", "nose", "ears", "eyes")},
           "legs": R["legs"], "tail": R["tail"],
           "colors": {"body": "#c49a5c", "muzzle": "#eedcb4", "ear": "#231a12", "leg": "#be955a", "eye": "#c9b23a", "nose": "#a8705e",
                      "back": "#b0884c", "tuft": "#c29a58", "tail": "#be955a", "white": "#f2ede3", "cream": "#e6d2a8", "pale": "#dcbc84", "black": "#1a1410", "tear": "#5a3c22"},
           "pat": "rosettes", "patOn": ["body", "front", "neck", "head", "leg", "tail"],
           "print": "paw",
           "sculpt": {"patScale": 0.39, "keep": ["tail\\d*"], "mesh": {"tris": [10000, 3000], "cell": 0.0095}, "shape": shapes, "eyes": eyes}}
    # (audit 2026-11-07) COATS by seed: the spotted leopard three times to one BLACK PANTHER (melanistic: the rosettes still
    # there, a shade darker in the black -- the pattern darkens the coat's own colour); VARIANT `snow`: the snow leopard,
    # smoky grey-white with dark grey rosettes, pale grey-green eyes, smaller
    out["coats"] = [{"name": "spotted"}, {"name": "spotted"}, {"name": "spotted"},
                    {"name": "black panther", "body": "#221d18", "back": "#1c1814", "leg": "#201b16", "tail": "#201b16", "tuft": "#221d18",
                     "muzzle": "#2c2620", "cream": "#2a241e", "pale": "#26201b", "white": "#302a24", "ear": "#100d0b", "black": "#0c0a08",
                     "nose": "#2a2220", "tear": "#141110"}]
    out["variants"] = {"snow": {"scale": 0.85, "colors": {"body": "#d6d2c8", "back": "#cac5ba", "leg": "#d0ccc2", "tail": "#d2cec4", "tuft": "#d6d2c8",
                                                          "muzzle": "#ebe8e2", "cream": "#e2ded6", "pale": "#dad6ce", "white": "#f2f0ec",
                                                          "ear": "#3c3836", "black": "#3a3634", "eye": "#a4aea0", "nose": "#a08078", "tear": "#5a5654"}}}
    save("leopard", out)

build()
