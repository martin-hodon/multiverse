# rigs5.py -- the five mammals of 2026-11-06 (lynx, chamois, giant panda, red panda, crested porcupine): their rigs
# (mammals.js params, root space: x forward, y up from the ground, z left, metres)
from g6 import *

def porcupine_rig():
    return {
        "name": "porcupine", "kind": "mammal", "headForm": "rodent", "shy": 6, "graze": 0.45, "rest": 0.6, "print": "paw", "headTurn": 14,
        "rear": [-0.15, 0.2, 0, 0.2, 0.12, 0.14], "front": [0.08, 0.17, 0, 0.15, 0.095, 0.1],
        "neck": [0.17, 0.17, 0, 0.23, 0.162, 0, 0.075, 0.065],
        "head": [0.27, 0.158, 0, 0.062], "muzzle": [0.3, 0.148, 0, 0.375, 0.13, 0, 0.048, 0.034], "nose": [0.382, 0.128, 0, 0.016],
        "ears": [0.258, 0.198, 0.048, 0.256, 0.21, 0.054, 0.013, 0.011], "eyes": [0.315, 0.175, 0.04, 0.0055],
        "legs": {"front": [0.12, 0.12, 0.07, 0.06], "hind": [-0.22, 0.14, 0.08, 0.07], "radii": [0.045, 0.032, 0.026], "foot": [0.04, 0.012, 0.03],
                 "kneeH": -1},
        "tail": {**arc_through([-0.33, 0.19], [-0.41, 0.13], -0.01), "r1": 0.03, "r2": 0.022, "n": 3, "sway": 8, "speed": 0.4},
        "gaits": {"walk": {"roll": 0.08}},
        "c": {"body": "#1e1915", "muzzle": "#221c17", "ear": "#1a1512", "leg": "#16120f", "tail": "#2a2420", "eye": "#0c0806", "nose": "#141010"},
    }
