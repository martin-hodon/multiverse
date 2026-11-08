from felid import *

# THE HOUSE CAT on the big-cat frame at s = .22: 25 cm at the shoulder, 47 cm head-body, a 30 cm tail carried up;
# slimmer and a little longer-legged than a tiger, and a head of its own -- round, short-faced, big forward eyes and
# big upright ears. Colours are the COAT's keys (makeCat: species.js), so every coat of CAT_COATS paints it:
# body, head, front (the chest: a calico's black), belly, muzzle, leg, foot, tail, ear, earIn, nose, eye
P = {"s": 0.22, "sho": 0.4, "hip": -0.6, "dyF": 0.08, "dyH": 0.09, "g": 0.9, "legF": 0.95, "legH": 1.0, "gz": 0.88, "gneck": 0.95,
     "tail": {"R": 0.62, "a0": -0.43, "a1": 1.85, "r1": 0.062, "r2": 0.044, "n": 6, "sway": 20, "speed": 0.9}}
HEAD_IDS = ("skull", "cheek", "ruff", "bridge", "muzzle", "pad", "chin", "jowl", "nose", "brow", "ear", "earIn")

def build():
    M = Map(P)
    S = M.S
    # A TABBY (pat 24: the tiger's stripes darkened from the coat itself -- ginger on ginger, brown on grey; makeCat strips
    # it from the plain coats: black, white, tuxedo, calico); the trunk WIDER (a 10-12 cm chest)
    tb = {"pat": "tabby", "frame": "body"}
    LF = {"pat": "tabby", "frame": {"o": "$legFLu", "u": [0, -1, 0], "r": 0.016}}
    LH = {"pat": "tabby", "frame": {"o": "$legHLu", "u": [0, -1, 0], "r": 0.016}}
    wide = lambda f, e: (lambda q: {**q, **e, "r": [q["r"][0], q["r"][1], q["r"][2] * f]})
    edits = {k: tb for k in ("scapula", "arm", "triceps", "thigh")}
    edits.update({k: LF for k in ("forearm", "flexor")}); edits.update({k: LH for k in ("gaskin", "hock")})
    edits.update({
        "chest": wide(1.45, {**tb, "color": "@body"}), "withers": wide(1.3, {**tb, "color": "@front"}), "scapula": {**tb, "color": "@front"},
        "loin": wide(1.25, tb), "rump": wide(1.25, tb),
        "keel": wide(1.35, {"pat": None, "color": "@belly"}), "belly": wide(1.25, {"pat": None, "color": "@belly"}),
        "throat": {"color": "@belly"}, "neck": wide(1.2, {**tb, "color": "@head"}),
        "paw": {"color": "@foot"}, "hpaw": {"color": "@foot"}, "pastern": {"color": "@foot"},
        # a cat's belly skin hangs less than a tiger's
        "pouch": lambda q: {**q, "r": [q["r"][0] * 0.8, q["r"][1] * 0.7, q["r"][2] * 0.9], "color": "@belly"},
    })
    J = sc(M.head(HJ, 1.0), S)                      # the head's pivot, in metres
    o = lambda dx, dy, dz=0.0: [J[0] + dx, J[1] + dy, J[2] + dz]
    def add(M, P):
        hd = {"bone": "head"}
        # (the M: lines fore and aft over the crown -- bands across the head's width; the cheeks' lines back from the eye)
        HM = {"pat": "tabby", "frame": {"o": "$head", "u": [0, 0, 1], "v": [0, 1, 0], "r": 0.012}}
        # (the cheek's own frame is a THIRD one where the cheek, the skull and the neck (the body's frame) meet below the
        #  ear: bodymesh.js paints three slots per vertex since 2026-11-08, so the lines run on clean there)
        HC = {"pat": "tabby", "frame": {"o": "$head", "u": [0, 1, 0], "v": [1, 0, 0], "r": 0.014}}
        return [
            {"id": "skull", "type": "ell", **hd, "c": o(0.0, 0.012), "r": [0.043, 0.035, 0.036], "k": 0.012, "color": "@head", **HM},
            {"id": "crown", "type": "ell", **hd, "c": o(0.012, 0.026), "r": [0.03, 0.02, 0.028], "k": 0.012, "kc": 0.004, "color": "@head", **HM},
            {"id": "cheek", "type": "ell", **hd, "c": o(0.014, -0.008, 0.021), "r": [0.026, 0.022, 0.018], "k": 0.01, "color": "@head", "mirror": True, **HC},
            {"id": "bridge", "type": "cone", **hd, "a": o(0.02, 0.02), "b": o(0.052, 0.004), "ra": 0.016, "rb": 0.0085, "k": 0.008, "color": "@head"},
            {"id": "muzzle", "type": "ell", **hd, "c": o(0.042, -0.01), "r": [0.017, 0.014, 0.019], "k": 0.007, "color": "@head"},
            {"id": "pad", "type": "ell", **hd, "c": o(0.05, -0.0118, 0.0098), "r": [0.0132, 0.0112, 0.0124], "k": 0.004, "kc": 0.002, "color": "@muzzle", "mirror": True},
            {"id": "chin", "type": "ell", **hd, "c": o(0.04, -0.0245), "r": [0.0135, 0.0068, 0.0108], "k": 0.004, "kc": 0.002, "color": "@muzzle"},
            {"id": "jowl", "type": "ell", **hd, "c": o(0.008, -0.022), "r": [0.03, 0.014, 0.024], "k": 0.01, "color": "@belly"},
            {"id": "nose", "type": "ell", **hd, "c": o(0.0598, -0.0015), "r": [0.0042, 0.0045, 0.0062], "rot": [0, 0, 20], "k": 0.002, "kc": 0.001, "color": "@nose", "wet": 0.4},
            # big upright ears: broad-based triangles, cupped open to the front, the tips rounded; the hollow pale
            *cup_ear(o(-0.0005, 0.0315, 0.0085), o(-0.021, 0.0235, 0.0385), o(-0.0156, 0.029, 0.022), o(-0.0125, 0.0665, 0.0305), 0.0037, k=0.004),
        ]
    M, R, shapes, _ = felid(P, edits, add, drop=HEAD_IDS)
    eyes = {"at": o(0.034, 0.012, 0.019), "from": o(0.0, 0.01, 0.0), "r": 0.0084, "iris": "@eye", "pupil": "slit", "lid": "@lid", "sink": 0.58, "socket": 1.07, "color": "#2e2a12"}
    # the rig's ears where the cone ears stand (so they flick about their own base): the rig writes them before its headScale (.7, about the neck's end)
    NEm = R["neck"][3:6]
    un = lambda p: [NEm[k] + (p[k] - NEm[k]) / HS0 for k in range(3)]
    R["ears"] = un(o(-0.012, 0.03, 0.022)) + un(o(-0.009, 0.064, 0.031)) + [0.0185 / HS0, 0.0024 / HS0]
    R["eyes"] = un(o(0.034, 0.012, 0.019)) + [0.0088 / HS0]
    def ring(t, P0, P1, r):
        if t > 0.35 and int((t - 0.35) / 0.11) % 2 == 0: return {"color": "@ring"}
        return {"color": "@tail", "pat": "tabby", "frame": {"o": [P0[0], P0[1], 0], "u": [P1[0] - P0[0], P1[1] - P0[1], 0], "r": 0.012}}
    tail = arc_tail(R["tail"], ring, n=9, tip="@ring")
    tail[0]["ra"] *= 1.35; tail[0]["k"] *= 2.5   # (its root flared into the rump: no pinch)
    shapes += tail
    d = orig("cat")
    out = {"name": "cat",
           "_about": "the house cat SCULPTED on the big-cat frame at s = .22 (2026-11-05, gen: scratchpad sc/carn/gen/cat.py from the tiger's body): 25 cm at the shoulder, 47 cm head-body, slim and a little longer in the leg than a tiger, the tail carried up; a round short-faced head with big forward eyes and big upright ears. Its colours are the coat's keys (species.js makeCat builds every coat of mammals.js CAT_COATS from this file)",
           "use": "creatures/frames/cat",
           "shy": 5, "headTurn": 22, "pupil": "slit",
           "params": {"s": P["s"], "tuft": 0, "tailSway": 20},
           **{k: R[k] for k in ("rear", "front", "neck", "head", "muzzle", "nose", "ears", "eyes")},
           "legs": R["legs"], "tail": R["tail"],
           "colors": {"body": "#c77b3a", "head": "#c77b3a", "front": "#c77b3a", "belly": "#dba573", "muzzle": "#dba573", "ear": "#b06f34",
                      "earIn": "#e0a8a0", "leg": "#b06f34", "foot": "#b06f34", "tail": "#b06f34", "eye": "#8fa03a", "nose": "#d67c88", "lid": "#3a2a20", "ring": "#6e3a16"},
           "patScale": 0.21,   # (audit 2026-11-07: finer mackerel stripes -- at .3 they were a tiger's bands)
           "print": "paw",
           "sculpt": {"keep": [], "mesh": {"tris": [6000, 1900]}, "shape": shapes, "eyes": eyes}}
    save("cat", out)

build()
