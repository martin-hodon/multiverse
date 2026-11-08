# rigs.py -- the mustelids' rigs (mammals.js params, root space: x forward, y up from the ground, z left, metres)
import sys, os
sys.path.insert(0, "/home/martin/store/apps/multiverse/tools/creaturegen/sc/new6")
from g6 import *

def badger_rig():
    # a European badger: 75 cm nose to rump, 15 cm tail, 12 kg -- low, a wedge broadest at the hips, short strong legs
    return {
        "name": "badger", "kind": "mammal", "headForm": "canid", "shy": 7, "graze": 0.45, "rest": 0.6, "print": "paw", "headTurn": 16,
        "rear": [-0.17, 0.2, 0, 0.2, 0.11, 0.13], "front": [0.1, 0.18, 0, 0.16, 0.09, 0.1],
        "neck": [0.2, 0.18, 0, 0.265, 0.16, 0, 0.075, 0.062],
        "head": [0.3, 0.162, 0, 0.06], "muzzle": [0.32, 0.152, 0, 0.41, 0.124, 0, 0.042, 0.018], "nose": [0.418, 0.124, 0, 0.014],
        "ears": [0.27, 0.2, 0.05, 0.266, 0.222, 0.058, 0.018, 0.015], "eyes": [0.345, 0.17, 0.034, 0.006],
        "legs": {"front": [0.13, 0.15, 0.075, 0.075], "hind": [-0.24, 0.17, 0.085, 0.085], "radii": [0.05, 0.036, 0.028], "foot": [0.04, 0.014, 0.03],
                 "kneeH": -1},
        "tail": {**arc_through([-0.37, 0.232], [-0.45, 0.188], -0.004), "r1": 0.04, "r2": 0.03, "n": 4, "sway": 9, "speed": 0.5},
        "gaits": {"walk": {"roll": 0.07}},
        "c": {"body": "#3c3a37", "muzzle": "#e8e6e0", "ear": "#121010", "leg": "#121010", "tail": "#4a4844", "eye": "#0e0a08", "nose": "#141010"},
    }

def weasel_rig():
    # a least weasel: 20 cm nose to rump, a 4.5 cm tail, 60-100 g -- a long thin tube on short legs, a long neck
    return {
        "name": "weasel", "kind": "mammal", "headForm": "rodent", "shy": 5, "graze": 0.25, "print": "paw", "headTurn": 26,
        "rear": [-0.05, 0.042, 0, 0.055, 0.016, 0.0165], "front": [0.02, 0.04, 0, 0.042, 0.0155, 0.0155],
        "neck": [0.045, 0.043, 0, 0.07, 0.047, 0, 0.012, 0.011],
        "head": [0.081, 0.049, 0, 0.0115], "muzzle": [0.088, 0.047, 0, 0.102, 0.0435, 0, 0.0085, 0.0045], "nose": [0.1035, 0.0435, 0, 0.0022],
        "ears": [0.075, 0.0585, 0.0085, 0.0735, 0.0625, 0.0105, 0.0042, 0.0036], "eyes": [0.0925, 0.0525, 0.0075, 0.0018],
        "legs": {"front": [0.03, 0.031, 0.0095, 0.0115], "hind": [-0.072, 0.035, 0.0105, 0.0135], "radii": [0.0065, 0.0045, 0.0035], "foot": [0.0065, 0.0025, 0.0042], "ankle": 0.0035,
                 "kneeH": -1},
        "tail": {**arc_through([-0.103, 0.047], [-0.148, 0.043], -0.003), "r1": 0.0055, "r2": 0.0042, "n": 3, "sway": 14, "speed": 0.7},
        "hop": {"period": 0.3, "h": 0.02, "sync": True}, "flex": 16, "flexPh": 2.5, "upright": {"deg": 72, "fold": 0.9},
        "gaits": {"walk": {"offsets": [-2.2, -2.0, -3.0, -2.8], "stride": 0.011, "lift": 0.009, "bob": 0, "pitch": 0.14, "pitchPh": 0.8},
                  "run": {"offsets": [-2.2, -2.0, -3.0, -2.8], "stride": 0.015, "lift": 0.012, "bob": 0, "pitch": 0.2, "pitchPh": 0.8}},
        "c": {"body": "#6e4129", "muzzle": "#6e4129", "ear": "#5e3822", "leg": "#653b24", "tail": "#653b24", "eye": "#060404", "nose": "#2a1a14", "belly": "#efe9dc"},
    }

RIGS = {"badger": badger_rig, "weasel": weasel_rig}
if __name__ == "__main__":
    for n in (sys.argv[1:] or RIGS):
        write_rig(n, RIGS[n]()); J = joints_of(n)
        print(n, {k: [round(x, 3) for x in v["o"]] for k, v in J.items() if k in ("body", "body2", "body3", "front", "neck", "head", "legFLu", "legFLl", "footFL", "legHLu", "legHLl", "footHL", "tail", "tail1", "earL")})
