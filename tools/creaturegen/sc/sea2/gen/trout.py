from sealib import *
from finsheet import mfin
_fin = fin
def fin(*a, **k):   # (every fin: its corners rounded, faint rays fanning from its root)
    k.setdefault("smooth", 2); k.setdefault("rays", True); return _fin(*a, **k)

# BROWN TROUT (Salmo trutta), 40 cm total length; snout at +0.2, caudal edge at -0.2
XM, XS, XT = -0.02, -0.1, -0.142
bone = bone_by_x(XM, XS, XT)
R = fish_rig(XM, XS, XT, 2.4, 0.045, 0.2, -0.2, degs=(4, 10, 16))
TP = [{"when": "rainbow", "v": "rainbow"}, {"when": "brown", "v": "trout"}]   # (the brown trout's red and black spots, or the rainbow's band: its coats)
FR = {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.045}
# (x, top, bottom, half width): the lateral profile -- the snout's rise to the nape, deepest before the dorsal fin,
#  the long taper to a slim caudal peduncle
st = [(0.198, 0.003, -0.006, 0.004), (0.19, 0.008, -0.011, 0.008), (0.175, 0.015, -0.017, 0.0125), (0.15, 0.025, -0.023, 0.0175),
      (0.12, 0.034, -0.03, 0.021), (0.09, 0.041, -0.036, 0.024), (0.05, 0.048, -0.041, 0.026), (0.02, 0.05, -0.042, 0.0255),
      (-0.02, 0.046, -0.039, 0.023), (-0.06, 0.038, -0.03, 0.0185), (-0.09, 0.03, -0.023, 0.0135), (-0.12, 0.02, -0.017, 0.0085),
      (-0.135, 0.017, -0.0155, 0.0068), (-0.148, 0.0175, -0.0155, 0.0058)]
sh = loft(st, 22, bone, "@body", ids="trunk", pat=TP, frame=FR)
sh += [
    # the gill cover's swell, the lower jaw's pale underside, the snout darker
    S("ell", id="cheek", c=[0.128, -0.003, 0], r=[0.032, 0.026, 0.0215], k=0.004, color="@body", pat=TP, frame=FR),
    S("ell", id="jaw", c=[0.168, -0.014, 0], r=[0.032, 0.007, 0.0125], k=0.004, kc=0.003, color="@pale"),
    S("ell", id="snout", c=[0.183, 0.004, 0], r=[0.017, 0.0085, 0.0098], k=0.004, color="@back"),
    # (carved: the gape, running back past the eye; the gill cover's edge)
    S("tube", id="mouth", pts=[[0.2, -0.0035, 0.0, 0.0017], [0.19, -0.006, 0.0085, 0.0018], [0.172, -0.0095, 0.0128, 0.0018], [0.152, -0.0115, 0.0158, 0.0016]], k=0.001, color="@dark", op="sub", mirror=True),
    S("tube", id="gill", pts=[[0.124, 0.027, 0.0185, 0.0015], [0.108, 0.012, 0.0232, 0.0017], [0.102, -0.006, 0.0242, 0.0017], [0.108, -0.022, 0.02, 0.0016], [0.12, -0.031, 0.0128, 0.0015]], k=0.0012, color="@gill", op="sub", mirror=True),
]
# fins (thin plates: details beside the field)
sh += fin([[0.052, 0.045, 0], [0.04, 0.084, 0], [0.026, 0.085, 0], [0.01, 0.072, 0], [-0.008, 0.06, 0], [-0.016, 0.044, 0]], 0.0007, "@fin", id="dorsal", pat=TP, frame=FR)
sh += [S("ell", id="adipose", bone="mid", c=[-0.094, 0.031, 0], r=[0.012, 0.0085, 0.0028], rot=[0, 0, -18], k=0.002, color="@adipose")]
sh += fin([[-0.046, -0.026, 0], [-0.056, -0.06, 0], [-0.066, -0.063, 0], [-0.08, -0.05, 0], [-0.09, -0.02, 0]], 0.0007, "@fin", bone="mid", id="anal")
sh += mfin([[0.004, -0.036, 0.012], [-0.012, -0.036, 0.013], [-0.036, -0.05, 0.02], [-0.03, -0.056, 0.022], [-0.012, -0.052, 0.019]], 0.0007, "@fin", id="pelvic", mirror=True, smooth=2)   # (2026-11-07: one sheet -- finsheet.py)
sh += mfin([[0.11, -0.02, 0.019], [0.098, -0.024, 0.021], [0.06, -0.044, 0.034], [0.064, -0.05, 0.034], [0.082, -0.046, 0.03], [0.104, -0.03, 0.021]], 0.0007, "@fin", id="pectoral", mirror=True, smooth=2)   # (2026-11-07: one sheet -- finsheet.py)
sh += fin([[-0.138, 0.016, 0], [-0.165, 0.033, 0], [-0.2, 0.052, 0], [-0.197, 0.026, 0], [-0.193, 0.002, 0], [-0.197, -0.022, 0], [-0.2, -0.047, 0], [-0.165, -0.03, 0], [-0.138, -0.014, 0]], 0.0007, "@tail", bone="tail", id="caudal")

d = {
    "name": "trout",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a brown trout, 40 cm -- a fusiform body, deepest a little before the dorsal fin (its depth 22% of its length), a broad rounded snout, the long gape running back past the eye, the gill cover's swell and edge; the dorsal fin mid-back, the small fleshy ADIPOSE fin behind it (orange), the pelvics under the dorsal's rear, the anal behind them, low pectorals and a near-square caudal fin (the fins thin plates, details beside the field, their outlines rounded, faint rays fanning from each root and the membrane paler toward its edge: the coat pattern `finrays`, coatpat.js 33); olive-brown above over golden flanks to a creamy belly (`shade`), the coat pattern `trout` (coatpat.js 28): black spots thick above the lateral line and on the dorsal fin, red spots ringed pale along the flank. A SWIMMER (the fish's plumbing: `fly`, `alt` its depth; index.html addSwimmer: it joins the lake's fish). Its spine is four bones a beat apart (body, mid, stock, tail), so the rear half sweeps in a wave.",
    "kind": "parts",
    "facet": False,
    "flags": {"fly": {"alt": [0.3, 1.2], "speed": [0.5, 1.4], "hz": 2.4}},
    "colors": {"body": "#b0904c", "back": "#5f5a34", "pale": "#ecdcaa", "fin": "#8d7646", "tail": "#7a6438", "adipose": "#c0662a", "gill": "#4a4228", "dark": "#1a1610"},
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mesh": {"cell": 0.0019, "tris": [3400, 1100]},
        "shade": {"back": "@back", "belly": "@pale", "k": 0.024, "at": -0.006, "mode": "mix", "tol": 0.3},
        "shape": sh,
        "eyes": {"at": [0.158, 0.009, 0.0165], "from": [0.15, 0.008, 0], "r": 0.0072, "color": "#0c0a08", "iris": "#c49a3c", "pupil": "round", "lid": "@back", "sink": 0.4, "bone": "body"},
    },
}
write("trout", keep_coats("trout", d))
