from sealib import *

# CLOWN ANEMONEFISH (Amphiprion ocellaris), 9 cm; snout at +0.045, the caudal fin's edge at -0.048
XM, XS, XT = -0.006, -0.022, -0.031
bone = bone_by_x(XM, XS, XT)
R = fish_rig(XM, XS, XT, 3.2, 0.017, 0.045, -0.048, degs=(3, 9, 15))
# the pectorals row (they are what a clownfish swims with): bones of their own, sweeping fore and aft
R.add("pectL", "body", [0.021, -0.005, 0.0085], shape={"shape": "tri", "size": {"a": [0, 0, 0], "b": [-0.012, -0.004, 0.006], "c": [-0.01, 0.003, 0.006], "r": 0.0005}},
      color="@body", anim={"axis": "y", "deg": 28, "speed": 3.2, "phase": 0})
R.add("pectR", "body", [0.021, -0.005, -0.0085], shape={"shape": "tri", "size": {"a": [0, 0, 0], "b": [-0.012, -0.004, -0.006], "c": [-0.01, 0.003, -0.006], "r": 0.0005}},
      color="@body", anim={"axis": "y", "deg": -28, "speed": 3.2, "phase": 0})
FR = {"o": [0.045, 0, 0], "u": [-1, 0, 0], "v": [0, 1, 0], "r": 0.082}   # (the bars: laid along the body from the snout)
# (x, top, bottom, half width): an oval, deep (its depth near half its standard length), a blunt rounded snout
st = [(0.0445, 0.0012, -0.0048, 0.0022), (0.041, 0.0055, -0.0085, 0.0048), (0.034, 0.011, -0.0125, 0.0078), (0.024, 0.0155, -0.0152, 0.0098),
      (0.012, 0.0176, -0.0166, 0.0106), (0.0, 0.0172, -0.016, 0.0102), (-0.012, 0.0138, -0.0128, 0.0084), (-0.021, 0.0092, -0.0082, 0.006),
      (-0.027, 0.0066, -0.0058, 0.0042), (-0.0325, 0.0064, -0.0058, 0.0033)]
sh = loft(st, 16, bone, "@body", ids="trunk", pat="clown", frame=FR)
sh += [
    S("ell", id="cheek", c=[0.03, -0.003, 0], r=[0.011, 0.0105, 0.0088], k=0.0012, color="@body", pat="clown", frame=FR),
    S("ell", id="lips", c=[0.0418, -0.0036, 0], r=[0.0032, 0.0019, 0.0036], k=0.0008, color="@lip"),
    # (no carved gape: at this grid it leaves slivers -- the lips alone draw the small mouth)
]
# the fins: the dorsal's low spiny part notched from its taller, rounded soft part, the rounded anal, pelvics and
# fan of a tail -- all edged in black
dors = [[0.019, 0.0152, 0], [0.016, 0.0215, 0], [0.01, 0.0238, 0], [0.004, 0.0226, 0], [-0.001, 0.0218, 0], [-0.005, 0.0272, 0],
        [-0.012, 0.0292, 0], [-0.019, 0.0268, 0], [-0.0245, 0.0185, 0], [-0.026, 0.0078, 0], [-0.015, 0.012, 0], [0.0, 0.0165, 0], [0.012, 0.0172, 0]]
sh += fin(dors, 0.00047, "@body", bone=bone, id="dorsal", pat="clown", frame=FR, k=0.0003)
sh += edge(dors[1:10], 0.0006, "@edge", bone=bone, id="dorsalEdge", k=0.0002)
anal = [[-0.006, -0.0148, 0], [-0.0095, -0.0228, 0], [-0.0155, -0.0252, 0], [-0.0215, -0.0222, 0], [-0.0258, -0.0145, 0], [-0.0262, -0.0062, 0], [-0.016, -0.0108, 0]]
sh += fin(anal, 0.00047, "@body", bone=bone, id="anal", pat="clown", frame=FR, k=0.0003)
sh += edge(anal[1:6], 0.0006, "@edge", bone=bone, id="analEdge", k=0.0002)
pelv = [[0.0095, -0.0158, 0.003], [0.0035, -0.0163, 0.0036], [-0.0025, -0.0228, 0.0058], [0.0005, -0.0255, 0.0062], [0.0055, -0.0222, 0.005]]
sh += fin(pelv, 0.00047, "@body", id="pelvic", mirror=True, k=0.0003)
sh += edge(pelv[2:5], 0.0006, "@edge", id="pelvicEdge", mirror=True, k=0.0002)
pect = [[0.0215, -0.0035, 0.0086], [0.0205, -0.0072, 0.0086], [0.0125, -0.0105, 0.0128], [0.0085, -0.0078, 0.0142], [0.009, -0.0025, 0.0138], [0.0135, 0.0005, 0.0122]]
sh += fin(pect, 0.00047, "@pect", bone="pectL", id="pectoral", mirror=True, k=0.0003)
caud = [[-0.0305, 0.0058, 0], [-0.0355, 0.0118, 0], [-0.0425, 0.0142, 0], [-0.0468, 0.0088, 0], [-0.0482, 0.0, 0], [-0.0468, -0.0088, 0],
        [-0.0425, -0.0142, 0], [-0.0355, -0.0118, 0], [-0.0305, -0.0058, 0]]
sh += fin(caud, 0.00047, "@body", bone="tail", id="caudal", k=0.0003)
sh += edge(caud[1:8], 0.0006, "@edge", bone="tail", id="caudalEdge", k=0.0002)

d = {
    "name": "clownfish",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a clown anemonefish (Amphiprion ocellaris), 9 cm -- an oval body, deep (its depth near half its standard length), a blunt rounded snout with soft lips, a big eye; bright orange with THREE WHITE BARS edged in black (the coat pattern `clown`, coatpat.js 31, laid from the snout: the head's bowed back behind the eye, the body's bulging forward mid-flank, a narrow one on the caudal peduncle -- running on up into the dorsal fin); ROUNDED fins, the dorsal's low spiny part notched from its taller soft part, the anal, pelvics and the fan of a tail edged in black, orange pectorals that row (bones of their own: a clownfish swims with them). The fins are in the field (a 0.55 mm grid). A SWIMMER (the fish's plumbing: `fly`, `alt` its depth; not put in the lake -- a reef fish). Its spine is four bones a beat apart (body, mid, stock, tail): a quick waggle.",
    "kind": "parts",
    "facet": False,
    "flags": {"fly": {"alt": [0.2, 0.8], "speed": [0.15, 0.4], "hz": 3.2}},
    "colors": {"body": "#f06a14", "pect": "#f2862e", "lip": "#e86416", "edge": "#121010", "dark": "#2a1208"},
    "coats": [{"name": "ocellaris clownfish"}, {"name": "black ocellaris (Darwin)", "body": "#1c1816", "pect": "#2a2320", "lip": "#2a2018", "dark": "#0a0808"},
              {"name": "orange, deeper", "body": "#e04e10", "pect": "#ea6a22", "lip": "#d84a10"}],
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mesh": {"cell": 0.0004, "tris": [8000, 2400]},
        "shade": {"back": 0.85, "belly": 1.08, "k": 0.012, "at": 0, "mode": "mix", "tol": 0.3},
        "shape": sh,
        "eyes": {"at": [0.0318, 0.0052, 0.0082], "from": [0.03, 0.005, 0], "r": 0.0033, "color": "#080606", "iris": "#c86a1e", "pupil": "round", "lid": "@body", "sink": 0.35, "bone": "body"},
    },
}
write("clownfish", d, digits=5)
