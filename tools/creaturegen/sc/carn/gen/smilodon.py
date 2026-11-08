from felid import *

# Smilodon fatalis: ~1 m at the shoulder, 1.75 m head-body, built like a bear-cat -- a massive neck and forequarters, very
# heavy forelimbs, a short lumbar, the hindquarters lower than the shoulder, a bob tail; a shorter, taller face with a deep
# chin over which the 17 cm sabres reach; tawny, paler beneath
P = {"s": 0.92, "sho": 0.46, "hip": -0.42, "dyF": 0.03, "dyH": -0.05, "g": 1.06, "legF": 1.24, "legH": 1.06, "gz": 1.02,
     "gneck": 1.16, "hs": [1.06, 1.14, 1.12],
     "tail": {"R": 0.3, "a0": -0.35, "a1": -1.25, "r1": 0.075, "r2": 0.055, "n": 3, "tuft": 0}}

def build():
    M = Map(P)
    def mv(dx, dy, sr=None):
        def f(q):
            for k in ("c", "a", "b"):
                if k in q: q[k] = [q[k][0] + dx * M.S, q[k][1] + dy * M.S, q[k][2]]
            if sr and "r" in q and isinstance(q["r"], list): q["r"] = [q["r"][i] * sr[i] for i in range(3)]
            return q
        return f
    nopat = {"pat": None}
    edits = {k: nopat for k in ("chest", "withers", "loin", "rump", "scapula", "arm", "triceps", "forearm", "flexor", "thigh", "gaskin", "hock", "neck", "skull", "cheek")}
    edits.update({
        "keel": {"color": "@cream", "pat": None}, "belly": {"color": "@cream", "pat": None}, "pouch": {"color": "@cream"},
        "withers": lambda q: {**mv(0, 0.02, [1.05, 1.15, 1.08])(q), "pat": None},
        "throat": {"color": "@cream"},
        "cheek": lambda q: {**mv(0, 0, [0.95, 1.0, 0.9])(q), "pat": None, "color": "@head"},
        "ruff": {"pat": None, "color": "@head"},
        "skull": lambda q: {**mv(-0.005, 0.0, [0.96, 1.0, 1.0])(q), "pat": None, "color": "@head"},
        "bridge": lambda q: {**mv(0.005, -0.005)(q), "color": "@head"},
        "muzzle": lambda q: {**mv(0.01, -0.015, [1.05, 1.25, 1.05])(q), "color": "@head"},
        "pad": lambda q: {**mv(0.008, -0.022, [1.05, 1.35, 1.05])(q), "color": "@muzzle"},
        "nose": lambda q: {**mv(0.008, -0.004, [1.1, 1.1, 1.2])(q), "color": "@nose"},
        "chin": lambda q: {**mv(-0.01, -0.045, [1.05, 1.6, 0.8])(q), "color": "@muzzle"},
        "jowl": lambda q: {**mv(0, -0.02, [1, 1.2, 1])(q), "color": "@cream"},
        "brow": {"color": "@head"},
        "ear": lambda q: {**mv(0.0, -0.01, [1, 0.8, 0.85])(q), "color": "@ear"},
        "earIn": lambda q: {**mv(0.0, -0.01, [1, 0.8, 0.85])(q), "color": "@cream"},
        "paw": {"color": "@leg"}, "hpaw": {"color": "@leg"},
    })
    def add(M, P):
        S = M.S
        t = lambda p: Tr(M, p)
        return [
            # the hump of muscle over the shoulders and the heavy neck
            {"id": "nape", "type": "ell", "bone": "neck", "c": t([0.7, 0.98, 0]), "r": [0.2 * S, 0.16 * S, 0.16 * S], "rot": [0, 0, 25], "k": 0.08 * S, "color": "@body"},
        ]
    M, R, shapes, eyes = felid(P, edits, add)
    eyes["iris"] = "@eye"
    # REVIEW PASS (world metres): eyes 3 cm lower; a broad skull and cheekbones; tapered wrists and smaller feet
    hsm = sum(P["hs"]) / 3
    shapes = head_pass(shapes, eyes, lambda p: H(M, P, p), M.S * hsm, {"tear": "@tear", "tearW": 0.006, "ears": 0.9, "earZ": 0.01, "nose": 0.9, "eyeBall": "#6a4a16"})
    eyes["at"][1] -= 0.03; eyes["from"][1] -= 0.03
    for q in shapes:   # (the brow and the almond's corners come down with the eyes)
        if q["id"] in ("browR", "eyeIn", "eyeOut", "tear0"): q["c"][1] -= 0.03
        if q["id"] == "tear1": q["c"][1] -= 0.02
        if q["id"] == "tear2": q["c"][1] -= 0.01
    by = {q["id"]: q for q in shapes}
    by["skull"]["r"][2] = 0.17
    by["cheek"]["r"][2] = 0.1; by["cheek"]["c"][2] = 0.108
    by["forearm"]["rb"] = 0.056; by["pastern"]["ra"] = 0.05; by["pastern"]["rb"] = 0.054
    by["paw"]["r"] = [0.085, 0.042, 0.074]; by["paw"]["c"][0] -= 0.012
    by["hpaw"]["r"] = [0.077, 0.036, 0.064]
    # THE SABRES: flat blades behind the whisker pad (two plates each), 3 cm deep, curving back to the tip, which reaches
    # past the chin's flange
    # (each a run of small ellipsoids down a curve: a 2:1 oval in section, 2.5 x 1.2 cm at the root, tapering to the point --
    #  each under the mesher's cell, so explicit geometry, sharp at any size)
    import math
    R0, Cc, T = [0.992, 0.875], [1.004, 0.77], [0.966, 0.69]
    # (a TUBE down the curve, 1.8 cm round at the root tapering to the point: thinner than the mesher's cell, so explicit
    #  geometry; flattened to a 2:1 oval by a second, deeper tube along its front edge)
    pts, pf = [], []
    n = 7
    for i in range(n + 1):
        u = i / n
        p = [(1 - u) ** 2 * R0[k] + 2 * u * (1 - u) * Cc[k] + u * u * T[k] for k in range(2)]
        taper = 1 - 0.8 * u ** 1.2
        pts.append([p[0], p[1], 0.056 - 0.006 * u, 0.0115 * taper])
        pf.append([p[0] + 0.009 * taper, p[1], 0.056 - 0.006 * u, 0.0105 * taper])
    sab = [{"id": "sabre", "type": "tube", "bone": "head", "pts": pts, "k": 0.001, "kc": 0.0005, "color": "@ivory", "mirror": True},
           {"id": "sabreF", "type": "tube", "bone": "head", "pts": pf, "k": 0.001, "kc": 0.0005, "color": "@ivory", "mirror": True}]
    shapes += sab + [
               # the chin's FLANGE, each side of the deep lower jaw
               {"id": "flange", "type": "ell", "bone": "head", "c": [0.995, 0.765, 0.036], "r": [0.03, 0.036, 0.02], "k": 0.02, "color": "@muzzle", "mirror": True},
               # the darker back
               *[{"id": f"spine{i}", "type": "ell", "c": c, "r": [rx, 0.05, 0.13], "k": 0.06, "kc": 0.05, "color": "@back"}
                 for i, (c, rx) in enumerate([([0.4, 0.995, 0], 0.22), ([-0.13, 0.825, 0], 0.26), ([-0.45, 0.855, 0], 0.2)])]]
    out = {"name": "smilodon",
           "_about": "Smilodon fatalis SCULPTED on the cat frame (2026-11-05, gen: scratchpad sc/carn/gen/smilodon.py from the tiger's shapes): a bear-cat -- massive neck and forelimbs, a short loin, the hindquarters lower than the shoulder, a bob tail; a short tall face over a deep chin, and the sabres (rounded blades, 2:1 oval in section, behind the whisker pad, curving back) reaching past its flange; tawny, paler beneath",
           "use": "creatures/frames/cat",
           "params": {"s": P["s"], "tuft": 0, "tailSway": 10},
           **{k: R[k] for k in ("rear", "front", "neck", "head", "muzzle", "nose", "ears", "eyes")},
           "legs": R["legs"], "tail": {**R["tail"], "_tuft": "no tuft: the big-cat frame's tail has one, and a smilodon's bob tail does not"},
           "colors": {"body": "#ad8654", "head": "#b08a58", "muzzle": "#c9ab7e", "ear": "#5a4128", "leg": "#a37c4c", "eye": "#c08d3a",
                      "nose": "#3a2a20", "tuft": "#6a4a2a", "tail": "#a37c4c", "white": "#ece2cc", "cream": "#d9c49e", "pale": "#c9a878", "black": "#1a1410", "ivory": "#ece2c8", "back": "#8a6640", "tear": "#5a3e24"},
           "mount": {"h": 1.9, "speed": 1.6},
           "print": "paw",
           "sculpt": {"keep": ["tail\\d*"], "mesh": {"tris": [10000, 3000]}, "shape": shapes, "eyes": eyes,
                      "shade": {"back": 0.86, "belly": 1.14, "on": "@body"}}}
    save("smilodon", out)

build()
