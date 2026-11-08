# rigs.py -- the six new mammals' rigs (mammals.js params, root space: x forward, y up from the ground, z left, metres)
from g6 import *

def hyena_rig():
    return {
        "name": "hyena", "kind": "mammal", "headForm": "canid", "shy": 9, "graze": 0.3, "rest": 0.7, "print": "paw", "headTurn": 16,
        "rear": [-0.24, 0.53, 0, 0.25, 0.17, 0.15], "front": [0.2, 0.64, 0, 0.3, 0.24, 0.18],
        "neck": [0.42, 0.72, 0, 0.6, 0.8, 0, 0.16, 0.13],
        "head": [0.68, 0.8, 0, 0.13], "muzzle": [0.76, 0.77, 0, 0.93, 0.73, 0, 0.085, 0.06], "nose": [0.95, 0.735, 0, 0.032],
        "ears": [0.66, 0.9, 0.075, 0.64, 0.99, 0.11, 0.05, 0.045], "eyes": [0.79, 0.84, 0.07, 0.018],
        "legs": {"front": [0.28, 0.52, 0.11, 0.25], "hind": [-0.3, 0.42, 0.1, 0.2], "radii": [0.08, 0.056, 0.04], "foot": [0.06, 0.035, 0.05],
                 "shoulder": 1.15, "thigh": 1.3},
        "tail": {**arc_through([-0.49, 0.565], [-0.6, 0.33], -0.03), "r1": 0.035, "r2": 0.045, "n": 4, "sway": 16, "speed": 0.8},
        "c": {"body": "#b39a72", "muzzle": "#2a221c", "ear": "#7a6450", "leg": "#a88e68", "tail": "#8a7458", "eye": "#3a2412", "nose": "#141010"},
    }

def skunk_rig():
    return {
        "name": "skunk", "kind": "mammal", "headForm": "canid", "shy": 4, "graze": 0.5, "print": "paw", "headTurn": 18,
        "rear": [-0.07, 0.17, 0, 0.15, 0.095, 0.095], "front": [0.08, 0.125, 0, 0.11, 0.065, 0.065],
        "neck": [0.14, 0.135, 0, 0.19, 0.138, 0, 0.05, 0.045],
        "head": [0.2, 0.137, 0, 0.042], "muzzle": [0.218, 0.132, 0, 0.25, 0.121, 0, 0.026, 0.012], "nose": [0.254, 0.121, 0, 0.007],
        "ears": [0.19, 0.16, 0.028, 0.19, 0.168, 0.034, 0.011, 0.01], "eyes": [0.222, 0.146, 0.022, 0.0045],
        "legs": {"front": [0.11, 0.1, 0.05, 0.05], "hind": [-0.12, 0.12, 0.055, 0.06], "radii": [0.03, 0.022, 0.016], "foot": [0.024, 0.009, 0.016],
                 "kneeH": -1},
        "tail": {**arc_through([-0.2, 0.225], [-0.08, 0.48], 0.095), "r1": 0.03, "r2": 0.045, "n": 6, "sway": 10, "speed": 0.5},
        "c": {"body": "#141212", "muzzle": "#161414", "ear": "#121010", "leg": "#121010", "tail": "#141212", "eye": "#140c08", "nose": "#2a2020"},
    }

def capybara_rig():
    return {
        "name": "capybara", "kind": "mammal", "headForm": "rodent", "shy": 6, "graze": 0.55, "rest": 0.8, "shore": True, "print": "paw", "headTurn": 14,
        "rear": [-0.22, 0.42, 0, 0.34, 0.22, 0.22], "front": [0.18, 0.4, 0, 0.3, 0.2, 0.2],
        "neck": [0.38, 0.44, 0, 0.52, 0.5, 0, 0.15, 0.13],
        "head": [0.58, 0.52, 0, 0.12], "muzzle": [0.64, 0.5, 0, 0.8, 0.45, 0, 0.1, 0.085], "nose": [0.82, 0.47, 0, 0.03],
        "ears": [0.55, 0.62, 0.065, 0.54, 0.65, 0.07, 0.025, 0.02], "eyes": [0.65, 0.59, 0.08, 0.014],
        "legs": {"front": [0.26, 0.27, 0.12, 0.13], "hind": [-0.33, 0.31, 0.13, 0.15], "radii": [0.07, 0.05, 0.036], "foot": [0.05, 0.02, 0.04]},
        "c": {"body": "#7a5636", "muzzle": "#6a4a30", "ear": "#5a3c26", "leg": "#6a4a30", "eye": "#1a100a", "nose": "#2a1e18"},
    }

def anteater_rig():
    return {
        "name": "anteater", "kind": "mammal", "headForm": "pig", "shy": 8, "graze": 0.5, "rest": 0.7, "print": "paw", "headTurn": 20,
        "rear": [-0.3, 0.46, 0, 0.33, 0.2, 0.15], "front": [0.14, 0.48, 0, 0.33, 0.22, 0.15],
        "neck": [0.4, 0.5, 0, 0.6, 0.5, 0, 0.12, 0.085],
        "head": [0.64, 0.5, 0, 0.07], "muzzle": [0.68, 0.49, 0, 1.03, 0.42, 0, 0.05, 0.022], "nose": [1.04, 0.418, 0, 0.014],
        "ears": [0.62, 0.55, 0.05, 0.615, 0.575, 0.055, 0.018, 0.012], "eyes": [0.72, 0.53, 0.042, 0.008],
        "legs": {"front": [0.3, 0.4, 0.1, 0.2], "hind": [-0.4, 0.38, 0.1, 0.19], "radii": [0.075, 0.055, 0.04], "foot": [0.05, 0.025, 0.04]},
        "tail": {**arc_through([-0.62, 0.48], [-1.42, 0.3], -0.06), "r1": 0.07, "r2": 0.05, "n": 6, "sway": 10, "speed": 0.5},
        "c": {"body": "#6e6458", "muzzle": "#5e564c", "ear": "#5e564c", "leg": "#cfc8ba", "tail": "#3a342e", "eye": "#0c0808", "nose": "#141010"},
    }

def pangolin_rig():
    return {
        "name": "pangolin", "kind": "mammal", "headForm": "rodent", "shy": 6, "graze": 0.6, "print": "paw", "headTurn": 16,
        "rear": [-0.07, 0.18, 0, 0.17, 0.1, 0.1], "front": [0.1, 0.14, 0, 0.12, 0.08, 0.08],
        "neck": [0.17, 0.13, 0, 0.23, 0.105, 0, 0.06, 0.045],
        "head": [0.255, 0.092, 0, 0.035], "muzzle": [0.27, 0.088, 0, 0.33, 0.07, 0, 0.026, 0.011], "nose": [0.335, 0.068, 0, 0.007],
        "ears": [0.245, 0.11, 0.03, 0.243, 0.117, 0.033, 0.006, 0.004], "eyes": [0.284, 0.1, 0.022, 0.005],
        "legs": {"front": [0.13, 0.09, 0.055, 0.045], "hind": [-0.13, 0.13, 0.07, 0.065], "radii": [0.04, 0.03, 0.022], "foot": [0.03, 0.012, 0.022]},
        "tail": {**arc_through([-0.22, 0.21], [-0.68, 0.06], -0.08), "r1": 0.075, "r2": 0.025, "n": 6, "sway": 8, "speed": 0.4},
        "c": {"body": "#7a6248", "muzzle": "#6a5440", "ear": "#5a4634", "leg": "#6a5440", "tail": "#7a6248", "eye": "#0c0806", "nose": "#2a201a"},
    }

RIGS = {"hyena": hyena_rig, "skunk": skunk_rig, "capybara": capybara_rig, "anteater": anteater_rig, "pangolin": pangolin_rig}
if __name__ == "__main__":
    for n in (sys.argv[1:] or RIGS):
        write_rig(n, RIGS[n]()); J = joints_of(n)
        print(n, {k: [round(x, 3) for x in v["o"]] for k, v in J.items() if k in ("body", "neck", "head", "legFLu", "legFLl", "footFL", "legHLu", "legHLl", "footHL", "tail", "tail1", "earL")})
