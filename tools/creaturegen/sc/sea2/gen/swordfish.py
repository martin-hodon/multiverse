from sealib import *
from finsheet import mfin
_fin = fin
def fin(*a, **k):   # (every fin: its corners rounded, faint rays fanning from its root)
    k.setdefault("smooth", 1); k.setdefault("rays", True); return _fin(*a, **k)

# SWORDFISH (Xiphias gladius), 3.1 m with its bill; the bill's tip at +1.6, the caudal lobes' tips at -1.52
XM, XS, XT = -0.35, -0.9, -1.16
bone = bone_by_x(XM, XS, XT)
R = fish_rig(XM, XS, XT, 0.8, 0.22, 1.6, -1.52, degs=(2.5, 7, 13))
# (x, top, bottom, half width): a robust round-bodied torpedo, deepest a third back, tapering to a slim peduncle
st = [(0.86, 0.055, -0.06, 0.055), (0.78, 0.09, -0.1, 0.08), (0.66, 0.135, -0.14, 0.11), (0.5, 0.185, -0.18, 0.15),
      (0.3, 0.22, -0.205, 0.172), (0.05, 0.225, -0.205, 0.172), (-0.25, 0.195, -0.18, 0.152), (-0.55, 0.14, -0.13, 0.112),
      (-0.8, 0.09, -0.082, 0.072), (-1.0, 0.056, -0.05, 0.047), (-1.12, 0.045, -0.04, 0.042), (-1.19, 0.042, -0.038, 0.04)]
sh = loft(st, 22, bone, "@body", ids="trunk")
# the BILL: long, flat and broad (a third of the length), in line with the upper jaw, a low ridge down its middle
bill = [(1.59, 0.017, -0.002, 0.01), (1.45, 0.022, -0.006, 0.024), (1.25, 0.028, -0.011, 0.037), (1.05, 0.036, -0.018, 0.047),
        (0.92, 0.048, -0.03, 0.055), (0.84, 0.062, -0.045, 0.06)]
sh += loft(bill, 16, bone, "@bill", ids="bill", kf=.3)
sh += [
    S("tube", id="ridge", pts=[[1.5, 0.014, 0, 0.006], [1.2, 0.02, 0, 0.009], [0.92, 0.038, 0, 0.014]], k=0.01, color="@bill"),
    # the lower jaw: short and pointed, under the bill's root; the mouth's gape back under the eye
    S("ell", id="jaw", c=[0.84, -0.06, 0], r=[0.16, 0.032, 0.05], k=0.02, kc=0.01, color="@pale"),
    S("tube", id="mouth", pts=[[0.98, -0.038, 0.0, 0.009], [0.9, -0.044, 0.042, 0.01], [0.8, -0.058, 0.07, 0.01], [0.7, -0.072, 0.092, 0.009]], k=0.006, color="@dark", op="sub", mirror=True),
    S("tube", id="gill", pts=[[0.56, 0.12, 0.12, 0.009], [0.48, 0.04, 0.168, 0.01], [0.47, -0.06, 0.168, 0.01], [0.51, -0.14, 0.13, 0.009], [0.56, -0.17, 0.08, 0.008]], k=0.006, color="@dark", op="sub", mirror=True),
    # the caudal keel: one big ridge each side of the peduncle
    S("ell", id="keel", bone="stock", c=[-1.1, 0.0, 0.032], r=[0.13, 0.028, 0.026], k=0.015, color="@back", mirror=True),
]
# fins (thin plates, details): the TALL SICKLE first dorsal on a short base just behind the head, the tiny second
# dorsal and second anal by the tail, the first anal's smaller sickle, the long sickle pectorals set low; NO pelvics;
# the great lunate tail
sh += fin([[0.5, 0.18, 0], [0.47, 0.34, 0], [0.42, 0.5, 0], [0.34, 0.63, 0], [0.22, 0.73, 0], [0.18, 0.71, 0], [0.21, 0.6, 0],
           [0.22, 0.46, 0], [0.2, 0.34, 0], [0.15, 0.26, 0], [0.1, 0.215, 0], [0.3, 0.205, 0]], 0.004, "@fin", id="dorsal")
sh += fin([[-0.92, 0.072, 0], [-0.97, 0.15, 0], [-1.0, 0.145, 0], [-1.0, 0.06, 0]], 0.003, "@fin", bone="mid", id="dorsal2")
sh += fin([[-0.52, -0.13, 0], [-0.6, -0.28, 0], [-0.67, -0.32, 0], [-0.66, -0.25, 0], [-0.68, -0.14, 0], [-0.64, -0.115, 0]], 0.0035, "@fin", bone="mid", id="anal")
sh += fin([[-0.96, -0.05, 0], [-1.01, -0.12, 0], [-1.04, -0.115, 0], [-1.03, -0.045, 0]], 0.003, "@fin", bone="stock", id="anal2")
sh += mfin([[0.44, -0.14, 0.116], [0.3, -0.25, 0.22], [0.13, -0.35, 0.28], [-0.02, -0.43, 0.31], [0.07, -0.36, 0.27], [0.21, -0.26, 0.2], [0.34, -0.175, 0.131]], 0.004, "@fin", id="pectoral", mirror=True, smooth=1)   # (2026-11-07: one sheet -- finsheet.py; its root sunk 14 mm into the flank: it stood 8 mm off it)
sh += fin([[-1.17, 0.04, 0], [-1.25, 0.17, 0], [-1.35, 0.33, 0], [-1.45, 0.47, 0], [-1.53, 0.53, 0], [-1.5, 0.46, 0], [-1.42, 0.3, 0], [-1.34, 0.14, 0],
           [-1.3, 0.0, 0], [-1.34, -0.13, 0], [-1.42, -0.28, 0], [-1.49, -0.43, 0], [-1.52, -0.5, 0], [-1.44, -0.44, 0], [-1.34, -0.31, 0],
           [-1.25, -0.16, 0], [-1.17, -0.035, 0]], 0.004, "@fin", bone="tail", id="caudal")

d = {
    "name": "swordfish",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a swordfish, 3.1 m with its sword -- the BILL long, flat and broad (a third of its length, a low ridge down its middle) over a short pointed lower jaw, a big eye; a robust round-bodied torpedo, deepest a third back, to a slim peduncle with one big keel each side; the tall rigid SICKLE first dorsal on a short base just behind the head, the tiny second dorsal and second anal by the tail, the first anal's smaller sickle, long sickle pectorals set low, NO pelvic fins, and the great LUNATE tail (the fins thin plates, details beside the field, their outlines rounded, faint rays fanning from each root and the membrane paler toward its edge: the coat pattern `finrays`, coatpat.js 33); dark bronze-purple above shading to a pale silvery brown below (`shade`). A SWIMMER (the fish's plumbing: `fly`, `alt` its depth; not put in the lake -- a fish of the open ocean). Its spine is four bones a beat apart (body, mid, stock, tail): the tail beats, the body stays stiff (thunniform).",
    "kind": "parts",
    "facet": False,
    "flags": {"fly": {"alt": [0.6, 1.8], "speed": [1.6, 3.4], "hz": 0.8}},
    "colors": {"body": "#6a6272", "back": "#3a3444", "pale": "#c2bab2", "bill": "#4a4452", "fin": "#4c4456", "dark": "#141218"},
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mesh": {"cell": 0.0095, "tris": [5000, 1600]},
        "shade": {"back": "#3a3444", "belly": "#c8c0b8", "k": 0.12, "at": -0.03, "mode": "mix", "tol": 0.35},
        "shape": sh,
        "eyes": {"at": [0.66, 0.055, 0.105], "from": [0.62, 0.05, 0], "r": 0.036, "color": "#06060a", "iris": "#2a3040", "pupil": "round", "lid": "@back", "sink": 0.35, "bone": "body"},
    },
}
write("swordfish", d)
