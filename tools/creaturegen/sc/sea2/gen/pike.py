from sealib import *
from finsheet import mfin
_fin = fin
def fin(*a, **k):   # (every fin: its corners rounded, faint rays fanning from its root)
    k.setdefault("smooth", 2); k.setdefault("rays", True); return _fin(*a, **k)

# NORTHERN PIKE (Esox lucius), 80 cm total length; snout at +0.4, the caudal lobes' tips at -0.4
XM, XS, XT = -0.05, -0.2, -0.305
bone = bone_by_x(XM, XS, XT)
R = fish_rig(XM, XS, XT, 1.3, 0.06, 0.4, -0.4, degs=(3, 9, 16))
FR = {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.045}   # (the spots: cells 2.8 x 1.6 cm)
# (x, top, bottom, half width): a long low torpedo, nearly as deep from the gill to the dorsal fin, the head a third of
#  the standard length and its snout a flat DUCK BILL -- wider than it is deep
st = [(0.398, 0.002, -0.006, 0.009), (0.38, 0.006, -0.01, 0.017), (0.35, 0.011, -0.015, 0.022), (0.31, 0.019, -0.021, 0.026),
      (0.27, 0.03, -0.029, 0.03), (0.22, 0.043, -0.039, 0.035), (0.16, 0.054, -0.049, 0.039), (0.08, 0.061, -0.057, 0.042),
      (0.0, 0.063, -0.059, 0.042), (-0.08, 0.062, -0.057, 0.04), (-0.16, 0.057, -0.051, 0.034), (-0.22, 0.046, -0.041, 0.026),
      (-0.27, 0.034, -0.03, 0.018), (-0.3, 0.027, -0.025, 0.013), (-0.318, 0.026, -0.024, 0.011)]
sh = loft(st, 24, bone, "@body", ids="trunk", pat="palespots", frame=FR)
sh += [
    # the flat crown between the high-set eyes, the gill cover, the lower jaw a little longer than the upper, its long gape
    S("ell", id="cheek", c=[0.21, -0.006, 0], r=[0.06, 0.038, 0.035], k=0.006, color="@body"),
    S("ell", id="crown", c=[0.3, 0.012, 0], r=[0.1, 0.012, 0.026], k=0.008, color="@back"),
    S("ell", id="jaw", c=[0.335, -0.016, 0], r=[0.072, 0.008, 0.021], k=0.005, kc=0.003, color="@pale"),
    S("ell", id="chin", c=[0.398, -0.009, 0], r=[0.009, 0.005, 0.009], k=0.004, color="@pale"),
    S("tube", id="mouth", pts=[[0.403, -0.005, 0.0, 0.0022], [0.39, -0.006, 0.0135, 0.0024], [0.35, -0.0085, 0.0215, 0.0024], [0.3, -0.012, 0.026, 0.0022], [0.268, -0.016, 0.0285, 0.002]], k=0.0015, color="@dark", op="sub", mirror=True),
    S("tube", id="gill", pts=[[0.21, 0.04, 0.03, 0.0024], [0.188, 0.02, 0.0375, 0.0026], [0.18, -0.006, 0.0395, 0.0026], [0.188, -0.03, 0.036, 0.0024], [0.205, -0.045, 0.026, 0.0022]], k=0.0018, color="@gill", op="sub", mirror=True),
    S("ell", id="nostril", c=[0.335, 0.0175, 0.012], r=[0.005, 0.0032, 0.004], k=0.002, color="@dark", op="sub", mirror=True),
]
# fins (thin plates, details): the dorsal and the anal set FAR BACK, opposite each other just ahead of the tail, the
# pelvics mid-body, low pectorals, a forked caudal
sh += fin([[-0.168, 0.055, 0], [-0.184, 0.098, 0], [-0.214, 0.113, 0], [-0.25, 0.102, 0], [-0.28, 0.074, 0], [-0.292, 0.043, 0], [-0.28, 0.031, 0], [-0.22, 0.044, 0]], 0.0009, "@fin", bone=bone, id="dorsal")
sh += fin([[-0.176, -0.049, 0], [-0.192, -0.094, 0], [-0.222, -0.105, 0], [-0.256, -0.093, 0], [-0.284, -0.066, 0], [-0.294, -0.038, 0], [-0.28, -0.027, 0], [-0.22, -0.039, 0]], 0.0009, "@fin", bone=bone, id="anal")
sh += mfin([[0.004, -0.057, 0.02], [-0.018, -0.058, 0.022], [-0.058, -0.084, 0.034], [-0.052, -0.092, 0.033], [-0.024, -0.083, 0.028]], 0.0009, "@fin", bone=bone, id="pelvic", mirror=True, smooth=2)   # (2026-11-07: one sheet -- finsheet.py)
sh += mfin([[0.17, -0.04, 0.024], [0.158, -0.044, 0.028], [0.098, -0.07, 0.05], [0.1, -0.078, 0.049], [0.124, -0.071, 0.044], [0.162, -0.052, 0.025]], 0.0009, "@fin", id="pectoral", mirror=True, smooth=2)   # (2026-11-07: one sheet -- finsheet.py; its root sunk 8 mm into the flank: it stood 5 mm off it)
sh += fin([[-0.31, 0.024, 0], [-0.34, 0.05, 0], [-0.386, 0.086, 0], [-0.4, 0.079, 0], [-0.381, 0.03, 0], [-0.362, 0.0, 0], [-0.381, -0.03, 0],
           [-0.4, -0.077, 0], [-0.386, -0.085, 0], [-0.34, -0.05, 0], [-0.31, -0.022, 0]], 0.0009, "@tail", bone="tail", id="caudal")

d = {
    "name": "pike",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a northern pike, 80 cm -- a long low torpedo (its depth 18% of its standard length) with a long head, a third of the body, and a flat DUCK-BILL snout wider than it is deep; the lower jaw a little longer, the long gape back to under the eye, eyes set high on the flat crown, the gill cover's edge carved; the dorsal and anal fins set FAR BACK, opposite each other just ahead of a forked tail (the pike's dart), pelvics mid-body, low pectorals (the fins thin plates, details beside the field, their outlines rounded, faint rays fanning from each root and the membrane paler toward its edge: the coat pattern `finrays`, coatpat.js 33); olive green, darker above over a cream belly (`shade`), the flanks in rows of pale bean-shaped spots (the coat pattern `palespots`, coatpat.js 27), the fins orange-brown. A SWIMMER (the fish's plumbing: `fly`, `alt` its depth; index.html addSwimmer: it joins the lake's fish). Its spine is four bones a beat apart (body, mid, stock, tail).",
    "kind": "parts",
    "facet": False,
    "flags": {"fly": {"alt": [0.4, 1.6], "speed": [0.4, 1.3], "hz": 1.3}},
    "colors": {"body": "#6a7638", "back": "#3c4620", "pale": "#e4e2c4", "fin": "#a06a36", "tail": "#8a5c30", "gill": "#2e3418", "dark": "#141808"},
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mesh": {"cell": 0.0028, "tris": [3800, 1200]},
        "shade": {"back": "#3a4420", "belly": "#e8e6c8", "k": 0.03, "at": -0.018, "mode": "mix", "tol": 0.3},
        "shape": sh,
        "eyes": {"at": [0.268, 0.025, 0.024], "from": [0.26, 0.014, 0], "r": 0.0085, "color": "#0c0c06", "iris": "#c8b048", "pupil": "round", "lid": "@back", "sink": 0.4, "bone": "body"},
    },
}
write("pike", d)
