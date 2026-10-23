import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
A = os.path.join(ROOT, 'assets/architecture/elements/')
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
g = 16
# ---- battlements
add("curtain wall", {"type": "box", "width": 14, "length": 1.4, "height": 7, "at": [[0, 0, 0, 0]]})
add("merlons", {"type": "box", "width": 0.9, "length": 1.4, "height": 1.1, "at": [[-6.3, 7, 0, 0]], "repeat": {"count": 8, "step": [1.8, 0, 0, 0]},
                "_about": "BATTLEMENTS: merlons with crenels between, a box repeated along the wall head"})
add("tower", {"type": "ring", "count": 16, "rOuter": 3.6, "rInner": 2.4, "height": 9, "solid": True, "place": [[10, 0, 0, 0]]})
add("tower merlons", {"type": "box", "width": 1.0, "length": 1.2, "height": 1.1, "spiral": {"count": 12, "radius": 3.0, "x": 10, "y": 9},
                      "_about": "...and round a tower's head: the same box on a circle"})
# ---- balustrade
add("plinth", {"type": "box", "width": 8, "length": 0.5, "height": 0.25, "at": [[0, 0, g, 0]]})
add("balustrade", {"type": "colonnade", "order": "tuscan", "count": 16, "spacing": 0.47, "columnR": 0.08, "height": 0.75, "taper": 0.55,
                   "base": {"h": 0.06, "r": 0.1}, "capital": {"h": 0.08, "r": 0.1}, "entablature": {"h": 0.14, "depth": 0.3},
                   "at": [[0, 0.25, g, 0]], "_about": "a BALUSTRADE: small columns (balusters) under a rail -- a colonnade at the scale of a hand"})
# ---- obelisk
add("obelisk steps", {"type": "crepidoma", "width": 2.6, "length": 2.6, "steps": 3, "stepH": 0.35, "stepOut": 0.4, "at": [[12, 0, g, 0]]})
add("obelisk", {"type": "column", "radius": 1.3, "height": 16, "sides": 4, "taper": 0.65, "at": [[12, 1.05, g, 0.785398]],
                "_about": "an OBELISK: a four-sided shaft, tapering, turned so its faces are square to the steps..."})
add("pyramidion", {"type": "dome", "sides": 4, "radius": 0.845, "thickness": 0, "head": {"profile": "trigonal", "rise": 1.1}, "at": [[12, 17.05, g, 0]],
                   "_about": "...and its pyramidion, whose corners stand on the shaft's"})
# ---- buttresses
add("nave wall", {"type": "box", "width": 12, "length": 1.0, "height": 12, "at": [[0, 0, 2 * g, 0]]})
add("buttresses", {"type": "box", "width": 1.2, "length": 2.4, "height": 7, "at": [[-4, 0, 2 * g - 1.7, 0], [0, 0, 2 * g - 1.7, 0], [4, 0, 2 * g - 1.7, 0]]})
add("buttress offsets", {"type": "box", "width": 1.2, "length": 1.4, "height": 3.5, "at": [[-4, 7, 2 * g - 1.2, 0], [0, 7, 2 * g - 1.2, 0], [4, 7, 2 * g - 1.2, 0]]})
add("buttress weatherings", {"type": "roof", "form": "shed", "width": 1.4, "length": 1.2, "pitch": 45,
                             "at": [[-4, 10.5, 2 * g - 1.2, -1.5707963], [0, 10.5, 2 * g - 1.2, -1.5707963], [4, 10.5, 2 * g - 1.2, -1.5707963]],
                             "_about": "BUTTRESSES: stepped piers against a wall, each stage set back and capped with a sloping weathering"})
# ---- minaret
mx = 12
add("minaret base", {"type": "box", "width": 3.6, "length": 3.6, "height": 5, "at": [[mx, 0, 2 * g, 0]]})
add("minaret shaft", {"type": "column", "radius": 1.5, "height": 22, "sides": 16, "taper": 0.95, "at": [[mx, 5, 2 * g, 0]]})
add("balcony corbelling", {"type": "column", "radius": 1.43, "height": 0.9, "sides": 16, "taper": 1.68, "at": [[mx, 26.1, 2 * g, 0]],
                           "_about": "the flare that carries the balcony (the serefe) -- muqarnas, on a real one"})
add("balcony", {"type": "ring", "count": 16, "rOuter": 2.4, "rInner": 1.4, "height": 0.3, "y": 27.0, "solid": True, "place": [[mx, 0, 2 * g, 0]]})
add("balcony parapet", {"type": "ring", "count": 16, "rOuter": 2.4, "rInner": 2.25, "height": 1.0, "y": 27.3, "solid": True, "place": [[mx, 0, 2 * g, 0]]})
add("upper shaft", {"type": "column", "radius": 1.2, "height": 6, "sides": 16, "at": [[mx, 27.3, 2 * g, 0]]})
add("minaret cap", {"type": "dome", "sides": 16, "radius": 1.35, "thickness": 0, "head": {"profile": "trigonal", "rise": 6}, "at": [[mx, 33.3, 2 * g, 0]],
                    "_about": "a MINARET, Ottoman: a slender fluted shaft, a balcony on its corbelling, and the pencil-point cap"})
add("finial", {"type": "column", "radius": 0.08, "height": 1.6, "sides": 6, "at": [[mx, 39.2, 2 * g, 0]]})
# ---- window aedicula
add("facade", {"type": "wall", "width": 6, "height": 5, "thickness": 0.6,
               "openings": [{"at": 3, "width": 1.4, "sill": 1.0, "springing": 3.2, "head": {"profile": "flat"}}], "at": [[0, 0, 3 * g, 0]]})
add("aedicula pilasters", {"type": "colonnade", "order": "tuscan", "shaft": "square", "count": 2, "spacing": 2.1, "columnR": 0.15, "height": 3.0,
                           "entablature": {"h": 0.35, "depth": 0.36}, "at": [[0, 0.8, 3 * g + 0.12, 0]]})
add("aedicula pediment", {"type": "roof", "form": "gable", "width": 0.5, "length": 2.8, "pitch": 24, "at": [[0, 4.15, 3 * g + 0.12, 1.5707963]],
                          "_about": "a WINDOW AEDICULA: pilasters either side, their entablature, and a pediment over it -- the frame of a classical window or door"})
# ---- Romanesque portal: recessed orders
for i, (w, z) in enumerate([(4.4, 0.0), (3.6, -0.5), (2.8, -1.0)]):
    add(f"portal order {i + 1}", {"type": "wall", "width": 7, "height": 6.5, "thickness": 0.5,
                                  "openings": [{"at": 3.5, "width": w, "sill": 0, "springing": 3.2, "head": {"profile": "semicircular"}}],
                                  "at": [[12, 0, 3 * g + z, 0]],
                                  **({"_about": "a ROMANESQUE PORTAL: the doorway in RECESSED ORDERS, each arch set back and narrower than the one before"} if i == 0 else {})})
json.dump
open(A + 'details.json', 'w').write(json.dumps({"name": "Details before 1800",
  "_about": "COMMON PIECES of buildings before 1800, each from the engine's primitives: BATTLEMENTS on a curtain wall and round a tower's head; a BALUSTRADE; an OBELISK on its steps with its pyramidion; stepped BUTTRESSES with their weatherings against a wall; an Ottoman MINARET (Hagia Sophia has four); a classical WINDOW AEDICULA (pilasters, entablature, pediment); and a ROMANESQUE PORTAL in recessed orders.",
  "params": {"detail": 4}, "build": build, "parts": parts}, indent=2) + "\n")
