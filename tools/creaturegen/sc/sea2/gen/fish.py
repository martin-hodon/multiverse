from sealib import *
from finsheet import mfin
import json as _json
_fin = fin
def fin(*a, **k):   # (every fin: its corners rounded, faint rays fanning from its root)
    k.setdefault("smooth", 2); k.setdefault("rays", True); return _fin(*a, **k)

# THE POND FISH (a roach's build, Rutilus rutilus), 0.25 m at k = 1: the snout at +0.112, the caudal lobes' tips near
# -0.15. The definition's rig (body, tail: written over k) and its coats are kept as they are; this writes its sculpt
# overlay anew (at k = 1, scaled by k through `sculptScale`)
P = REPO + "assets/creatures/sea/fish.json"
d = _json.load(open(P))
bone = lambda x: "body" if x > -0.075 else "tail"
FR = {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.12}   # (the scales' pitch: 5% of r, 6 mm -- ~42 along the lateral line)
# (x, top, bottom, half width): fusiform, deepest a third back (its depth ~27% of its standard length), a small head
st = [(0.112, -0.001, -0.008, 0.004), (0.106, 0.007, -0.015, 0.0075), (0.094, 0.015, -0.021, 0.0105), (0.075, 0.023, -0.026, 0.013),
      (0.05, 0.029, -0.029, 0.0145), (0.022, 0.0315, -0.03, 0.015), (-0.008, 0.03, -0.028, 0.0143), (-0.038, 0.025, -0.023, 0.0125),
      (-0.062, 0.018, -0.016, 0.0095), (-0.078, 0.0125, -0.011, 0.0068), (-0.09, 0.0105, -0.0095, 0.0055), (-0.097, 0.01, -0.009, 0.0048)]
sh = loft(st, 22, bone, "@body", ids="trunk", pat="rowscales", frame=FR, pat_x=0.072)   # (the head bare of scales)
sh += [
    # the head: the gill cover's swell, a blunt snout over a small terminal mouth
    S("ell", id="cheek", c=[0.078, -0.004, 0], r=[0.024, 0.022, 0.0128], k=0.003, color="@body"),
    S("ell", id="snout", c=[0.1, 0.002, 0], r=[0.013, 0.009, 0.0075], k=0.0025, color="@back"),
    S("ell", id="chin", c=[0.103, -0.01, 0], r=[0.01, 0.004, 0.0062], k=0.002, color="@pale"),
    S("ell", id="mouth", c=[0.1125, -0.0065, 0], r=[0.0035, 0.0016, 0.0042], k=0.001, color="@dark", op="sub"),
    S("tube", id="gill", pts=[[0.074, 0.021, 0.0095, 0.0011], [0.066, 0.009, 0.0128, 0.0011], [0.064, -0.004, 0.0134, 0.0011], [0.067, -0.016, 0.0118, 0.0011], [0.074, -0.024, 0.008, 0.001]],
      k=0.0008, color="@gill", op="sub", mirror=True),
    # the LATERAL LINE: a fine dark line curving down a little along the flank
    S("tube", id="line", pts=[[0.066, 0.008, 0.0136, 0.0011], [0.03, 0.002, 0.0152, 0.0011], [-0.01, 0.0, 0.0145, 0.001], [-0.045, 0.0, 0.0122, 0.001], [-0.075, 0.001, 0.0071, 0.0009]],
      k=0.0005, kc=0.0004, color="@line", op="paint", mirror=True),
]
# fins (thin plates beside the field): the dorsal over the pelvics, its margin straight; the anal behind; the pelvics,
# the low pectorals; a deeply FORKED tail with pointed lobes
sh += fin([[0.024, 0.03, 0], [0.012, 0.066, 0], [0.002, 0.065, 0], [-0.016, 0.044, 0], [-0.024, 0.028, 0]], 0.0006, "@fin", id="dorsal")
sh += fin([[-0.036, -0.022, 0], [-0.046, -0.046, 0], [-0.056, -0.047, 0], [-0.07, -0.026, 0], [-0.074, -0.013, 0]], 0.0005, "@fin", id="anal")
sh += mfin([[0.022, -0.024, 0.006], [0.01, -0.025, 0.007], [-0.008, -0.046, 0.015], [-0.002, -0.049, 0.014], [0.012, -0.04, 0.011]], 0.0005, "@fin", id="pelvic", mirror=True, smooth=2)   # (2026-11-07: one sheet -- finsheet.py)
sh += mfin([[0.066, -0.019, 0.0115], [0.06, -0.022, 0.013], [0.032, -0.036, 0.022], [0.034, -0.04, 0.021], [0.046, -0.035, 0.018], [0.064, -0.025, 0.012]], 0.0005, "@fin", id="pectoral", mirror=True, smooth=2)   # (2026-11-07: one sheet -- finsheet.py)
sh += fin([[-0.088, 0.011, 0], [-0.112, 0.03, 0], [-0.146, 0.05, 0], [-0.15, 0.044, 0], [-0.132, 0.016, 0], [-0.122, 0.0, 0], [-0.132, -0.015, 0],
           [-0.149, -0.042, 0], [-0.144, -0.047, 0], [-0.112, -0.028, 0], [-0.088, -0.01, 0]], 0.0006, "@tail", bone="tail", id="caudal")

d["_about"] = ("SCULPTED (2026-11-07, the sculpt overlay; generator scratchpad sc/sea2/gen/fish.py): a pond fish, 0.25-0.45 m -- a roach's "
    "fusiform body, deepest a third of the way back (its depth ~27% of its standard length), a small blunt head over a little terminal mouth, the gill "
    "cover's edge carved, a big eye; scales in staggered rows, each one's back edge rimmed dark (the coat pattern `rowscales`, coatpat.js 32: some 42 "
    "along the lateral line), the lateral line painted; the dorsal over the pelvics, the anal behind, low pectorals and a deeply FORKED tail with pointed "
    "lobes on the tail's bone (it beats) -- the fins thin plates, their corners rounded, faint rays fanning from each root (`finrays`, coatpat.js 33); "
    "countershaded (`shade`): the back the coat's dark, a pale silver belly. A SWIMMER: it rides the flier plumbing -- its `fly` alt its depth under the "
    "surface, its speed and tail-beat rate (index.html addSwimmer). Drawn at three sizes and in its coats by its seed (species.js makeFish).")
d["sculpt"] = {
    "keep": [],
    "mesh": {"cell": 0.0012, "tris": [3600, 1200]},
    "shade": {"back": "@back", "belly": "@pale", "k": 0.012, "at": -0.004, "mode": "mix", "tol": 0.3},
    "shape": sh,
    "eyes": {"at": [0.088, 0.007, 0.0118], "from": [0.08, 0.006, 0], "r": 0.0052, "color": "#101010", "iris": "@iris", "pupil": "round", "lid": "@body", "sink": 0.35, "bone": "body"},
}
d["colors"]["iris"] = "#b8402a"   # (a roach's red eye)
open(P, "w").write(dumps_def(d))
print("wrote", P, "shapes", len(sh))
