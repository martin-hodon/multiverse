from sealib import *
from finsheet import mfin
_fin = fin
def fin(*a, **k):   # (every fin: its corners rounded, faint rays fanning from its root)
    k.setdefault("smooth", 2); k.setdefault("rays", True); return _fin(*a, **k)

# COMMON CARP (Cyprinus carpio), 60 cm total length; snout at +0.3, the caudal lobes' tips at -0.3
XM, XS, XT = 0.0, -0.13, -0.205
bone = bone_by_x(XM, XS, XT)
R = fish_rig(XM, XS, XT, 1.6, 0.09, 0.3, -0.3, degs=(3, 8, 14))
FR = {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.29}   # (the scales' pitch: 5% of r, 1.45 cm -- 35 along the lateral line)
# (x, top, bottom, half width): a small head, the back rising steeply behind it into the arch, deepest mid-body (its
#  depth a third of the standard length), a short deep caudal peduncle
st = [(0.291, 0.002, -0.013, 0.007), (0.282, 0.012, -0.025, 0.014), (0.26, 0.032, -0.04, 0.025), (0.22, 0.058, -0.055, 0.036),
      (0.18, 0.078, -0.066, 0.042), (0.12, 0.098, -0.078, 0.047), (0.06, 0.106, -0.083, 0.048), (0.0, 0.103, -0.08, 0.046),
      (-0.06, 0.092, -0.07, 0.04), (-0.12, 0.072, -0.052, 0.031), (-0.17, 0.052, -0.036, 0.021), (-0.2, 0.041, -0.028, 0.015),
      (-0.218, 0.038, -0.027, 0.012)]
sh = loft(st, 20, bone, "@body", ids="trunk", pat=[{"when": "koi", "v": "koi"}, {"when": "wild", "v": "rowscales"}, {"when": "ogon", "v": "rowscales"}], frame=FR, pat_x=0.19)   # (the head bare of scales)
sh += [
    # the head: the gill cover's swell, the snout, thick fleshy lips round a small mouth, the two pairs of barbels
    S("ell", id="cheek", c=[0.21, -0.008, 0], r=[0.045, 0.05, 0.039], k=0.006, color="@body"),
    S("ell", id="snout", c=[0.272, 0.006, 0], r=[0.03, 0.022, 0.02], k=0.006, color="@back"),
    S("ell", id="lip", c=[0.292, -0.011, 0], r=[0.012, 0.0075, 0.0115], k=0.003, kc=0.002, color="@lip"),
    S("ell", id="chin", c=[0.284, -0.0175, 0], r=[0.02, 0.0065, 0.0115], k=0.004, color="@lip"),
    S("ell", id="mouth", c=[0.309, -0.0105, 0], r=[0.0085, 0.0036, 0.0085], k=0.002, color="@dark", op="sub"),
    S("tube", id="barbelU", pts=[[0.293, -0.004, 0.008, 0.0022], [0.3, -0.009, 0.014, 0.0019], [0.303, -0.017, 0.019, 0.0016]], k=0.0015, color="@lip", mirror=True),
    S("tube", id="barbelL", pts=[[0.284, -0.016, 0.0115, 0.0025], [0.288, -0.026, 0.017, 0.0022], [0.284, -0.038, 0.022, 0.002], [0.276, -0.046, 0.024, 0.0018]], k=0.0015, color="@lip", mirror=True),
    S("tube", id="gill", pts=[[0.205, 0.05, 0.03, 0.0024], [0.186, 0.025, 0.041, 0.0025], [0.18, -0.005, 0.0445, 0.0025], [0.186, -0.035, 0.04, 0.0024], [0.2, -0.055, 0.03, 0.0022]], k=0.0018, color="@gill", op="sub", mirror=True),
]
# fins (thin plates, details beside the field): the long dorsal with its tall serrated leading ray and concave margin,
# the short anal, the pelvics under the dorsal's start, low pectorals, the forked tail with rounded lobes
sh += fin([[0.072, 0.097, 0], [0.064, 0.166, 0], [0.05, 0.162, 0], [0.024, 0.143, 0], [-0.03, 0.13, 0], [-0.09, 0.114, 0], [-0.128, 0.1, 0],
           [-0.142, 0.082, 0], [-0.13, 0.066, 0], [-0.06, 0.086, 0], [0.0, 0.098, 0]], 0.0009, "@fin", id="dorsal")
sh += [S("tube", id="spine", pts=[[0.071, 0.096, 0, 0.0028], [0.067, 0.13, 0, 0.0022], [0.064, 0.162, 0, 0.0014]], k=0.002, color="@fin")]
sh += fin([[-0.098, -0.062, 0], [-0.112, -0.118, 0], [-0.128, -0.121, 0], [-0.158, -0.088, 0], [-0.16, -0.032, 0]], 0.0009, "@fin2", bone="stock", id="anal")
sh += mfin([[0.078, -0.077, 0.02], [0.056, -0.079, 0.023], [0.016, -0.108, 0.038], [0.022, -0.116, 0.036], [0.05, -0.105, 0.03]], 0.0009, "@fin2", id="pelvic", mirror=True, smooth=2)   # (2026-11-07: one sheet -- finsheet.py)
sh += mfin([[0.188, -0.046, 0.034], [0.176, -0.05, 0.037], [0.12, -0.083, 0.056], [0.124, -0.091, 0.054], [0.146, -0.083, 0.048], [0.18, -0.06, 0.036]], 0.0009, "@fin2", id="pectoral", mirror=True, smooth=2)   # (2026-11-07: one sheet -- finsheet.py)
sh += fin([[-0.205, 0.036, 0], [-0.24, 0.07, 0], [-0.284, 0.106, 0], [-0.3, 0.096, 0], [-0.286, 0.05, 0], [-0.262, 0.004, 0], [-0.284, -0.045, 0],
           [-0.298, -0.088, 0], [-0.284, -0.099, 0], [-0.24, -0.064, 0], [-0.205, -0.028, 0]], 0.0009, "@tail", bone="tail", id="caudal")

d = {
    "name": "carp",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a common carp, 60 cm -- deep-bodied (its depth a third of its standard length), the back rising steeply behind a small head into the arch; thick fleshy lips round a small protrusible mouth with two pairs of barbels (short on the upper lip, long at the mouth's corners), the gill cover's edge carved; the LONG dorsal fin from over the pelvics nearly to the tail, its leading ray a tall serrated spine over a concave margin, the short anal, low pectorals, a forked tail with rounded lobes (the fins thin plates, details beside the field, their outlines rounded, faint rays fanning from each root and the membrane paler toward its edge: the coat pattern `finrays`, coatpat.js 33); golden bronze over BIG overlapping scales in staggered rows, each one's back edge rimmed dark (the coat pattern `rowscales`, coatpat.js 32: some 35 along the lateral line), olive-bronze above to a pale gold belly (`shade`), the lower fins reddish. A SWIMMER (the fish's plumbing: `fly`, `alt` its depth; index.html addSwimmer: it joins the lake's fish). Its spine is four bones a beat apart (body, mid, stock, tail), so the rear half sweeps slowly.",
    "kind": "parts",
    "facet": False,
    "flags": {"fly": {"alt": [0.5, 1.6], "speed": [0.3, 0.9], "hz": 1.6}},
    "colors": {"body": "#b88e3e", "back": "#6a5a2a", "pale": "#e4cc8a", "lip": "#c8a874", "fin": "#7a5a36", "fin2": "#a8603a", "tail": "#8a5e38", "gill": "#4e4020", "line": "#6a5426", "dark": "#1a1408"},
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mesh": {"cell": 0.0026, "tris": [3600, 1200]},
        "shade": {"when": "wild", "back": "#5e5026", "belly": "#e8d08e", "k": 0.04, "at": -0.01, "mode": "mix", "tol": 0.3},
        "shape": sh,
        "eyes": {"at": [0.246, 0.02, 0.029], "from": [0.236, 0.018, 0], "r": 0.0085, "color": "#0c0a06", "iris": "#c8a050", "pupil": "round", "lid": "@back", "sink": 0.4, "bone": "body"},
    },
}
write("carp", keep_coats("carp", d))
