# THE RIGS of the five new mammals (2026-11-05): the skeleton each one walks on (mammals.js mammal()), in metres,
# x forward, y up from the ground, z to the left. The sculpt overlay (prim.py) is written on the joints these give.
import math
PI = math.pi
# a primate's walk is DIAGONAL-sequence: a hind foot, then the OPPOSITE fore (mammals' default is lateral) -- FL, FR, HL, HR
DIAG = [3 * PI / 2, PI / 2, 0, PI]

RIGS = {
  "gorilla": {
    "kind": "mammal", "headForm": False, "headTurn": 16, "graze": 0.22, "print": "paw",
    "rear": [-0.2, 0.72, 0, 0.3, 0.26, 0.28], "front": [0.2, 1.02, 0, 0.3, 0.36, 0.38],
    "neck": [0.38, 1.1, 0, 0.52, 1.13, 0, 0.17, 0.15],
    "head": [0.6, 1.13, 0, 0.14],
    "muzzle": [0.64, 1.08, 0, 0.75, 1.05, 0, 0.1, 0.08], "nose": [0.78, 1.07, 0, 0.03],
    "eyes": [0.72, 1.16, 0.045, 0.013],
    "legs": {"front": [0.3, 1.04, 0.29, 0.44], "hind": [-0.3, 0.6, 0.18, 0.28], "radii": [0.11, 0.09, 0.07],
             "foot": [0.13, 0.12, 0.08], "kneeF": -1, "kneeH": 1, "bend": [1.01, 1.06], "thigh": 1.2, "toe": 0.04},
    "gaits": {"walk": {"offsets": DIAG, "stride": 0.24, "lift": 0.1}, "run": {"stride": 0.36, "lift": 0.16}},
  },
  "orangutan": {
    "kind": "mammal", "headForm": False, "headTurn": 20, "graze": 0.2, "print": "paw",
    "rear": [-0.18, 0.52, 0, 0.24, 0.24, 0.22], "front": [0.15, 0.78, 0, 0.24, 0.26, 0.32],
    "neck": [0.3, 0.88, 0, 0.44, 0.96, 0, 0.12, 0.11],
    "head": [0.512, 0.966, 0, 0.13],
    "muzzle": [0.56, 0.918, 0, 0.656, 0.894, 0, 0.084, 0.066], "nose": [0.656, 0.93, 0, 0.024],
    "eyes": [0.632, 0.99, 0.036, 0.012],
    "legs": {"front": [0.26, 0.9, 0.27, 0.42], "hind": [-0.22, 0.45, 0.15, 0.2], "radii": [0.07, 0.055, 0.042],
             "foot": [0.1, 0.07, 0.06], "kneeF": -1, "kneeH": 1, "bend": [1.015, 1.08], "toe": 0.03},
    "gaits": {"walk": {"offsets": DIAG, "stride": 0.2, "lift": 0.08}, "run": {"stride": 0.3, "lift": 0.12}},
  },
  "baboon": {
    "kind": "mammal", "headForm": False, "headTurn": 22, "graze": 0.35, "print": "paw",
    "rear": [-0.2, 0.5, 0, 0.2, 0.15, 0.15], "front": [0.13, 0.55, 0, 0.22, 0.18, 0.15],
    "neck": [0.3, 0.6, 0, 0.4, 0.64, 0, 0.09, 0.08],
    "head": [0.43, 0.66, 0, 0.075],
    "muzzle": [0.46, 0.64, 0, 0.6, 0.575, 0, 0.055, 0.036], "nose": [0.62, 0.58, 0, 0.015],
    "eyes": [0.5, 0.68, 0.025, 0.01],
    "legs": {"front": [0.2, 0.5, 0.1, 0.24], "hind": [-0.25, 0.48, 0.09, 0.23], "radii": [0.05, 0.038, 0.028],
             "foot": [0.05, 0.03, 0.03], "kneeF": -1, "kneeH": 1, "bend": [1.02, 1.06], "toe": 0.03},
    "tail": {"path": [[-0.37, 0.53], [-0.45, 0.63], [-0.52, 0.62], [-0.55, 0.42], [-0.55, 0.22]], "r1": 0.03, "r2": 0.018, "sway": 9, "speed": 0.6},
    "gaits": {"walk": {"offsets": DIAG}},
  },
  "lemur": {
    "kind": "mammal", "headForm": False, "headTurn": 26, "graze": 0.3, "shy": 6, "print": "paw",
    "rear": [-0.08, 0.25, 0, 0.11, 0.07, 0.07], "front": [0.075, 0.19, 0, 0.1, 0.065, 0.06],
    "neck": [0.15, 0.21, 0, 0.2, 0.235, 0, 0.04, 0.035],
    "head": [0.215, 0.245, 0, 0.038],
    "muzzle": [0.235, 0.238, 0, 0.268, 0.228, 0, 0.02, 0.012], "nose": [0.272, 0.229, 0, 0.007],
    "ears": [0.2, 0.275, 0.024, 0.19, 0.31, 0.04, 0.014, 0.005],
    "eyes": [0.25, 0.255, 0.022, 0.009],
    "legs": {"front": [0.095, 0.165, 0.042, 0.075], "hind": [-0.105, 0.24, 0.045, 0.11], "radii": [0.02, 0.014, 0.01],
             "foot": [0.025, 0.008, 0.012], "kneeF": -1, "kneeH": 1, "bend": [1.07, 1.24], "toe": 0.012},
    "tail": {"path": [[-0.185, 0.26], [-0.27, 0.285], [-0.34, 0.385], [-0.36, 0.545], [-0.33, 0.685], [-0.26, 0.755]], "r1": 0.022, "r2": 0.02, "sway": 7, "speed": 0.5},
    "gaits": {"walk": {"offsets": DIAG}},
  },
  "kangaroo": {
    "kind": "mammal", "headForm": False, "headTurn": 24, "graze": 0.45, "shy": 10, "print": "paw", "biped": True,
    # (it HOPS: the two feet together, the leg phase locked to the bound -- index.html hopStep: `sync`)
    "hop": {"period": 0.72, "h": 0.28, "sync": True},
    "rear": [-0.08, 0.55, 0, 0.24, 0.19, 0.16], "front": [0.17, 0.82, 0, 0.2, 0.14, 0.12],
    "neck": [0.24, 1.0, 0, 0.32, 1.13, 0, 0.09, 0.075],
    "head": [0.36, 1.17, 0, 0.065],
    "muzzle": [0.39, 1.155, 0, 0.49, 1.12, 0, 0.045, 0.032], "nose": [0.505, 1.12, 0, 0.016],
    "ears": [0.33, 1.22, 0.035, 0.3, 1.36, 0.06, 0.03, 0.008],
    "eyes": [0.41, 1.19, 0.04, 0.012],
    "legs": {"front": [0.2, 0.5, 0.1, 0.2], "hind": [-0.06, 0.5, 0.11, 0.169], "radii": [0.09, 0.05, 0.025],
             "foot": [0.2, 0.03, 0.04], "kneeH": 1, "bend": [1, 1.15], "toe": 0.03, "thigh": 1.2},
    "tail": {"path": [[-0.22, 0.42], [-0.48, 0.18], [-0.78, 0.07], [-1.02, 0.04], [-1.2, 0.035]], "r1": 0.1, "r2": 0.02, "sway": 3, "speed": 0.4},
    "extras": [
      {"id": "armL", "parent": "body", "from": [0.29, 0.86, 0.085], "to": [0.38, 0.69, 0.08], "r1": 0.03, "r2": 0.02, "anim": {"axis": "z", "deg": 9, "speed": 0.8, "phase": 0.6, "amp": 1}},
      {"id": "armR", "parent": "body", "from": [0.29, 0.86, -0.085], "to": [0.38, 0.69, -0.08], "r1": 0.03, "r2": 0.02, "anim": {"axis": "z", "deg": 9, "speed": 0.8, "phase": 0.6, "amp": 1}},
    ],
    # (both feet together: phase -1.88 puts the swing of the stride in the air of the bound, the stance on the ground)
    "gaits": {"walk": {"offsets": [0, 0, -1.88, -1.88], "stride": 0.13, "lift": 0.1, "bob": 0}, "run": {"offsets": [0, 0, -1.88, -1.88], "stride": 0.13, "lift": 0.14, "bob": 0}},
  },
}
