# THE TAJ MAHAL (Agra, 1632-53) from components: the tomb is walls round a chamfered plan whose openings are its
# iwans (the reveal of a 5m wall IS the recess), an `iwan` component closing each at the back; on its roof a drum,
# the onion and four `chhatri`s; on the plinth's corners four `minaret`s.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, C, T, H = 56.9, 9.5, 5.0, 29.0          # the tomb: width, chamfer, wall (= iwan depth), height to the roof
PL, PH = 95.0, 6.7                          # the plinth
MAIN = [9.0, 19.9, 9.0]                     # a main face: flank, the great iwan's bay, flank
big = {"w": 10.4, "s": 19.0}                # the great iwan
small = {"w": 4.6, "s": 9.0}                # the flanks' iwans, two storeys
cham = {"w": 6.0, "s": 9.0}                 # the chamfers' iwans, two storeys
TIER = H / 2
SPREAD = 0.3
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
iw = lambda o, sill: {"at": 0, "width": o["w"], "sill": sill, "springing": sill + o["s"], "head": {"profile": "pointed", "spread": SPREAD}}
two = lambda o: [{"h": TIER, "openings": [iw(o, 0)]}, {"openings": [iw(o, 1.2)]}]
add("plinth", {"type": "prism", "plan": {"rect": [PL, PL]}, "height": PH, "at": [[0, 0, 0, 0]], "_about": "the marble plinth, 95m square"})
add("tomb", {"type": "enclosure", "glass": False, "plan": {"rect": [W, W], "chamfer": C, "split": {"main": MAIN}}, "thickness": T, "height": H,
             "faces": {"main:1": [iw(big, 0)], "main:0": two(small), "main:2": two(small), "chamfer": two(cham)},
             "at": [[0, PH, 0, 0]],
             "_about": "the tomb's walls on its chamfered square, 5m thick: every iwan is an opening, its reveal the recess, its pointed head the recess's vault"})
# the iwans' backs, each at the inner end of its opening, facing out
faces = []                                  # (centre of the outer face, outward normal, length) for the eight faces
a, c = W / 2, C
for k in range(4):
    ang = k * math.pi / 2
    n = (math.sin(ang), math.cos(ang))      # a main face's outward normal
    faces.append(("main", (n[0] * a, n[1] * a), n))
    ang2 = ang + math.pi / 4
    n2 = (math.sin(ang2), math.cos(ang2)); dist = (a - c / 2) * math.sqrt(2) / math.sqrt(2) * math.sqrt(2) / math.sqrt(2)
    # the chamfer's middle: halfway between (a - c, a) and (a, a - c), rotated with the face
    mx, mz = (a - c / 2), (a - c / 2)
    cx, cz = mx * math.cos(-ang) - 0 * 0, 0
    faces.append(("chamfer", None, n2))
backs = {}
def place(key, o, y, pos, n):
    yaw = math.atan2(n[0], n[1])
    backs.setdefault(key, {"o": o, "at": []})["at"].append([round(pos[0], 4), round(y, 4), round(pos[1], 4), round(yaw, 6)])
for k in range(4):
    ang = k * math.pi / 2
    n = (math.sin(ang), math.cos(ang)); tdir = (math.cos(ang), -math.sin(ang))
    centre = (n[0] * (a - T), n[1] * (a - T))                   # the inner face's middle
    place("great", big, PH, centre, n)
    off = MAIN[1] / 2 + MAIN[0] / 2
    for s in (-1, 1):
        p = (centre[0] + tdir[0] * s * off, centre[1] + tdir[1] * s * off)
        place("flank", small, PH, p, n); place("flank upper", small, PH + TIER + 1.2, p, n)
    ang2 = ang + math.pi / 4
    n2 = (math.sin(ang2), math.cos(ang2))
    # the chamfer's middle on the outer face is (a - c/2) along both axes of this quadrant; inner: T in along n2
    q = [(a - c / 2) * v for v in (n[0] + tdir[0] * -1, n[1] + tdir[1] * -1)]
    mid = ((a - c / 2) * (n[0] + n2[0] * 0) , 0)
    om = ((a - c / 2) * (math.sin(ang) + math.cos(ang)), (a - c / 2) * (math.cos(ang) - math.sin(ang)))
    im = (om[0] - n2[0] * T, om[1] - n2[1] * T)
    place("chamfer", cham, PH, im, n2); place("chamfer upper", cham, PH + TIER + 1.2, im, n2)
for key, b in backs.items():
    o = b["o"]
    add(f"iwan backs ({key})", {"type": "component", "use": "components/iwan", "params": {"w": o["w"], "s": o["s"], "spread": SPREAD, "t": 0.5, "door": 2.4},
                                 "at": b["at"], **({"build": ["back", "back door", "hood"]} if key == "great" else {}),
                                 **({"_about": "the great iwans' backs have the doors into the tomb chamber"} if key == "great" else {})})
add("plinth stair", {"type": "flight", "width": 4.0, "run": 0.3, "rise": 0.18, "top": PH, "landing": 0, "at": [[2.0, 0, PL / 2 + 37 * 0.3, 1.5707963]],
                     "_about": "the flight up the plinth's front, onto the terrace the tomb stands on"})
add("roof", {"flatRoof": True, "type": "prism", "plan": {"rect": [W - 2 * T + 0.2, W - 2 * T + 0.2], "chamfer": C - T * 0.4}, "height": 1.5, "at": [[0, PH + H - 1.5, 0, 0]],
             "_about": "the roof over the chambers"})
add("parapet", {"type": "enclosure", "plan": {"rect": [W, W], "chamfer": C}, "thickness": 0.7, "height": 1.6, "openings": [], "at": [[0, PH + H, 0, 0]]})
add("pishtaq crowns", {"type": "box", "width": MAIN[1], "length": 1.6, "height": 4.2,
                       "spiral": {"count": 4, "radius": a - 0.8, "turn": 0, "y": PH + H},
                       "_about": "each great iwan's frame, the pishtaq, rising above the parapet"})
add("drum", {"type": "ring", "count": 32, "rOuter": 9.3, "rInner": 8.6, "height": 10, "y": PH + H, "solid": True, "place": [[0, 0, 0, 0]]})
add("dome", {"type": "dome", "radius": 9.3, "thickness": 0, "head": {"profile": "onion", "bulge": 1.12, "neck": 0.85}, "at": [[0, PH + H + 10, 0, 0]],
             "_about": "the onion, its bulb swelling past the drum"})
add("finial", {"type": "column", "radius": 0.35, "height": 10, "sides": 8, "taper": 0.3, "at": [[0, PH + H + 10 + 21.1, 0, 0]]})
add("chhatris", {"type": "component", "use": "components/chhatri", "params": {"r": 3.2, "floor": 0},
                 "at": [[s * 16.5, PH + H, t * 16.5, 0] for s, t in ((1, 1), (1, -1), (-1, -1), (-1, 1))],
                 "_about": "the four chhatris round the dome, over the corner chambers"})
add("minarets", {"type": "component", "use": "components/minaret", "params": {"h": 33, "r": 2.6, "balconies": 3},
                 "at": [[s * (PL / 2 - 4), PH, t * (PL / 2 - 4), 0] for s, t in ((1, 1), (1, -1), (-1, -1), (-1, 1))],
                 "_about": "the four minarets on the plinth's corners, three balconies each and a chhatri on top"})
doc = {"name": "Taj Mahal",
  "_about": "THE TAJ MAHAL, Agra (1632-53), from components at its real size. On a 95m plinth, the tomb: walls 5m thick round a chamfered square 57m across (`enclosure`, its main faces SPLIT into flank, great iwan and flank), every iwan an opening whose reveal is the recess and whose pointed head is its vault, closed at the back by the `iwan` component; two storeys of smaller iwans on the flanks and the chamfers (the faces' TIERS). On the roof the parapet, the pishtaq frames rising over the great iwans, the drum and the onion dome with its finial, and four `chhatri`s; on the plinth's corners the four `minaret`s, each with three balconies and a chhatri of its own. What is drawn for this building alone is its plinth, its roof slab, the drum and the dome -- the rest is components.",
  "params": {"detail": 4}, "railing": {"type": "stone"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/taj-mahal.json"), "w").write(json.dumps(doc, indent=2) + "\n")
