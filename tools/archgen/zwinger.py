# THE ZWINGER (Dresden, 1710-28, Poeppelmann): a court closed by galleries and pavilions -- all components: straight
# `gallery` wings, two `curved-gallery` ends, `pavilion`s at the corners and at the curves' apexes, and the Kronentor.
import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapes import onion_y_at
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
X, Z, D, H = 56.0, 46.0, 9.0, 8.0            # the court's half width (to the corner pavilions' middles), half depth, galleries' depth and height
PW = 16.0                                    # a pavilion's width
KG = 13.0                                    # the Kronentor's width
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
# THE DRESS, one decision for the whole court: the galleries' arches between Doric pilasters, an entablature under the
# terrace's balustrade (the arches crown under it); the pavilions Doric round their arcades, Corinthian above, windows framed
GAL = {"order": "doric", "head": 2.0, "dressed": 1}
# the long galleries on the south side, either side of the Kronentor; one along the north side
seg = (X - PW / 2) - KG / 2                  # from the gate to a corner pavilion
add("south galleries", comp("components/gallery", {"L": seg, "D": D, "H": H, "n": round(seg / 4.2), **GAL},
                            [[-(KG / 2 + seg / 2), 0, Z, 0], [KG / 2 + seg / 2, 0, Z, 0]],
                            _about="the Langgalerie, each side of the crown gate"))
add("north gallery", comp("components/gallery", {"L": 2 * X - PW, "D": D, "H": H, "n": round((2 * X - PW) / 4.2), **GAL}, [[0, 0, -Z, 0]],
                          _about="the side toward the Elbe (closed by Semper's gallery in 1855; a gallery wing here)"))
# the curved galleries at the two ends, from corner pavilion to corner pavilion round an apex pavilion
R = Z
# each end is two halves of a curve, the apex pavilion between them: 64 bays round, each half from the corner
# pavilion (bays reach into it, so the terrace meets its door) to the apex pavilion's side
for nm, fr, to in (("curved galleries north", -15, -3), ("curved galleries south", 2, 14)):
    add(nm, comp("components/curved-gallery", {"R": R, "D": D, "H": H, "count": 64, "from": fr, "to": to, **GAL},
                 [[X, 0, 0, 1.5707963], [-X, 0, 0, -1.5707963]],
                 _about="half of a Bogengalerie: the curves close each end of the court, a pavilion at the apex between the halves"))
# pavilions: the four corners, and the two at the curves' apexes (the Wallpavillon and the Glockenspielpavillon)
pav = {"W": PW, "D": 14, "H2": 9.5, "n": 3, "m": 3, "order1": "doric", "order2": "corinthian", "dressed": 1}
add("corner pavilions", comp("components/pavilion", pav, [[s * X, 0, t * Z, 0 if s > 0 else 3.14159265] for s, t in ((1, 1), (1, -1), (-1, -1), (-1, 1))],
                             _about="the corner pavilions, each turned so its stair stands on the court's side, away from the curve that runs into it"))
add("wallpavillon", comp("components/pavilion", {**pav, "W": 18, "D": 16, "H2": 11}, [[X + R, 0, 0, 1.5707963]],
                         _about="the Wallpavillon at the apex of the west curve"))
add("glockenspielpavillon", comp("components/pavilion", {**pav, "W": 18, "D": 16, "H2": 11}, [[-X - R, 0, 0, -1.5707963]],
                                 _about="the Glockenspielpavillon at the apex of the east curve"))
# the Kronentor: a square gate tower, a passage through it, a square onion crown and the crown on top
add("kronentor", {"type": "enclosure", "glass": False, "plan": {"rect": [KG, KG]}, "thickness": 1.2, "height": 17,
                  "tiers": [{"h": 9, "openings": [{"at": 0, "width": 2.8, "sill": 3.0, "springing": 6.0, "head": {"profile": "semicircular"}}]},
                            {"openings": [{"at": 0, "width": 3.0, "sill": 1.0, "springing": 5.2, "head": {"profile": "semicircular"}}]}],
                  "faces": {"0": [{"h": 9, "openings": [{"at": 0, "width": 5.0, "sill": 0, "springing": 5.0, "head": {"profile": "semicircular"}}]},
                                  {"openings": [{"at": 0, "width": 3.0, "sill": 1.0, "springing": 5.2, "head": {"profile": "semicircular"}}]}],
                            "2": [{"h": 9, "openings": [{"at": 0, "width": 5.0, "sill": 0, "springing": 5.0, "head": {"profile": "semicircular"}}]},
                                  {"openings": [{"at": 0, "width": 3.0, "sill": 1.0, "springing": 5.2, "head": {"profile": "semicircular"}}]}]},
                  "interior": True,   # (its hall, the passage up to the crown: a space closed but for its two arches, not the open air's)
                  "at": [[0, 0, Z, 0]], "_about": "the crown gate: a passage through it on the axis, arched windows above"})
add("kronentor crown", {"type": "dome", "sides": 4, "radius": KG / 2 * 1.414, "thickness": 0, "head": {"profile": "onion", "bulge": 1.08, "neck": 0.8},
                        "at": [[0, 17, Z, 0]], "_about": "its roof: an onion on a SQUARE plan -- a dome of four sides"})
add("kronentor lantern", comp("components/domed-tower", {"sides": 4, "R": 1.6, "H": 2.0, "t": 0.3, "drumR": 1.2, "drumH": 1.0, "kok": 0.3,
                                                        "capR": 1.5, "bulge": 1.3, "neck": 0.8, "finial": 1.2},
                              [[0, round(17 + onion_y_at(KG / 2 * 1.414, 1.6, 1.08, 0.8), 4), Z, 0]], build=["tower", "drum", "cap", "finial"],
                              _about="the crown on the crown: a small square lantern and onion"))
# THE BRIDGE over the moat (the Zwingergraben) to the Kronentor: three arches, the deck level with the gate's floor,
# and a short flight down at its far end to the ground. The moat itself is the ground's (the game carves it round
# the platform: architecture.js archBuilding `moat`).
MOAT_W, ISLAND_Z = 12.0, 57.0
BL = (ISLAND_Z + MOAT_W + 1.5) - (Z + KG / 2)
add("bridge", comp("components/bridge", {"L": BL, "W": 8, "depth": 5.0, "n": 3}, [[0, 0, Z + KG / 2, 0]],
                   _about="the bridge over the moat, from the crown gate"))
add("bridge steps", {"type": "flight", "width": 6, "run": 0.32, "rise": 0.15, "top": 0, "base": -0.6, "landing": 0,
                     "at": [[3, 0, Z + KG / 2 + BL + 4 * 0.32, 1.5707963]], "_about": "down from the deck to the ground beyond the moat"})
# THE STATUES (statuary.py): Hercules Saxonicus with the globe on his shoulders crowning the Wallpavillon's roof, and
# the figures along the Langgalerie's terrace, on low pedestals behind its balustrade -- sandstone (limestone here),
# looking out over the moat
import sys, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from statuary import statue, pedestal, capped, FACE_PZ, FACE_PX
W_, BRK = 18.0, 18.0 * 0.22
ridge = 8.7 + 11 + BRK + (W_ / 2 - BRK / math.tan(math.radians(68))) * math.tan(math.radians(25))   # the Wallpavillon's mansard: its ridge
stat = {"statue Hercules": statue((X + R, ridge - 0.2, 0), kind="man", style="roman", stone="limestone", scale=1.8, seed=5, face=FACE_PX)}
k = 0
for sx in (-1, 1):
    for i in range(6):
        x = sx * (KG / 2 + (i + 0.5) * seg / 6)
        stat[f"pedestal terrace {k}"] = pedestal((x, 8.7, Z + D / 2 - 0.45), 0.6, 0.6, 0.55, "a figure's pedestal on the gallery terrace")
        stat[f"statue terrace {k}"] = statue((x, 8.7 + 0.55, Z + D / 2 - 0.45), kind="woman" if k % 2 else "man", style="roman", stone="limestone", scale=1.1, seed=20 + k, face=FACE_PZ)
        k += 1
for kk, v in capped(stat).items(): add(kk, v)

doc = {"name": "Zwinger, Dresden",
  "_about": "THE ZWINGER, Dresden (1710-28), all components: two straight `gallery` wings either side of the Kronentor and one along the north side, a `curved-gallery` closing each end of the court, a `pavilion` at each corner and a larger one at the apex of each curve (the Wallpavillon and the Glockenspielpavillon), and the Kronentor itself -- a square gate tower under an onion on a square plan, with a golden crown of a lantern on top -- and the bridge over the moat to it. The court is about 112 x 92m between the pavilions' middles.",
  "params": {"detail": 4}, "base": {"height": 0.6, "steps": 2, "stepOut": 0.5, "plan": {"rect": [230, 2 * ISLAND_Z - 1]}}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/zwinger.json"), "w").write(json.dumps(doc, indent=2) + "\n")
