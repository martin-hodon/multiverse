# ANGKOR WAT, Siem Reap (c. 1113-1150, Suryavarman II), in grey sandstone on laterite: the temple-mountain of the Khmer,
# Mount Meru in stone, facing WEST. From the causeway over the moat (a stretch of it here, the reflecting ponds either
# side) and the cruciform Terrace of Honour, the temple rises in three enclosures, each a GALLERY round a raised court,
# each higher than the last:
#   the third, outermost, on its terrace a few steps up -- its outer side a colonnade, its inner wall the bas-reliefs
#     (the Churning of the Ocean of Milk), gate-pavilions (gopuras) on its axes, the western one crowned by three towers,
#     pavilions on its corners; from its west side the CRUCIFORM CLOISTER (Preah Poan) of four courts, a library to
#     either side of it;
#   the second, on a platform the steep stairs climb to, two libraries in its court, a tower on each corner;
#   the BAKAN, the summit: a platform thirteen metres high climbed by stairs as steep as ladders, its square gallery
#     and the cross of galleries meeting under the CENTRAL TOWER, sixty-five metres up -- the QUINCUNX of five prangs,
#     each a redented tower bending in to a lotus bud (shikhara.js: the plan in offsets, the rekha curve, the storeys
#     banded, small spires standing on the corners of every storey as the antefixes do).
#   The plan is the site's (the survey's galleries, towers and libraries), made symmetric about the axis. The galleries
#   are RANGES (range.js), roofed, their faces opened as each side is (a colonnade, windows, doors where a gallery
#   crosses), running through the pavilions on their corners and axes.
#   East is +x, south is +z; the central tower at the origin. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
r4 = lambda v: round(v, 4)
Q = math.pi / 2
flat = {"profile": "flat"}

# ---- the levels ---------------------------------------------------------------------------------------------------
CW = 1.5                                   # the causeway and the Terrace of Honour
Y1 = 3.0                                   # the third enclosure's terrace
Y2 = 9.5                                   # the second's platform
Y3 = 22.5                                  # the bakan
# the galleries' middle lines
XA0, XA1, ZA = -114.4, 87.9, 85.5          # the third (outer) gallery
XB0, XB1, ZB = -65.0, 49.9, 47.8           # the second
C = 25.0                                   # the bakan's square gallery
P1 = (-121.4, 94.9, 92.5)                  # the third enclosure's terrace: west, east, half across
P2 = (-70.0, 55.0, 53.0)                   # the second's platform
PB = 32.0                                  # the bakan, half across
CL = (-23.5, 0.0, 23.5)                    # the cruciform cloister's galleries along the axis
CLX = -89.2                                # and the one across it
RUN, STEEP = 0.22, 0.3                     # the steep stairs: a rise at most STEEP on RUN

def door(at, w=3.2, h=3.6): return {"at": r4(at), "width": w, "sill": 0, "springing": h, "head": flat}

def flight(name, base, top, w, places, steep=False, about=None):
    """a flight up from `base` to `top`, `w` across, at each of `places` (foot point, the way it climbs: "e", "w", "n",
    "s"). (A flight climbs its local +x, its width over local -z..0: north is yaw pi/2 from x + w/2, west yaw pi from
    z - w/2 ... z + w/2, south -pi/2 from x - w/2, east yaw 0 from z + w/2.)"""
    run = RUN if steep else 0.3
    n = math.ceil((top - base) / (STEEP if steep else 0.19) - 1e-9)
    at = []
    for x, z, way in places:
        at.append({"n": [r4(x + w / 2), 0, r4(z), Q], "w": [r4(x), 0, r4(z - w / 2), math.pi],
                   "s": [r4(x - w / 2), 0, r4(z), -Q], "e": [r4(x), 0, r4(z + w / 2), 0]}[way])
    add(name, {"type": "flight", "width": w, "run": run, "rise": r4((top - base) / n), "base": base, "top": top, "landing": 0,
               **({"steep": True} if steep else {}), "at": at, **({"_about": about} if about else {})})
    return n * run

def pavilion(name, x, z, y, w, l, h, faces, roof=None, about=None):
    """a gate or corner pavilion: walls `w` x `l`, `h` high, `faces` {face: [openings]} (0 south, 1 east, 2 north, 3 west),
    roofed with a hip (or `roof` False: a flat slab, to carry a tower)"""
    add(name, {"type": "enclosure", "plan": {"rect": [w, l]}, "thickness": 0.8, "height": h, "glass": False, "openings": [],
               "faces": {str(k): v for k, v in faces.items()}, "at": [[x, y, z, 0]], **({"_about": about} if about else {})})
    if roof is False:
        add(f"{name} slab", {"type": "roof", "form": "flat", "width": r4(w + 0.6), "length": r4(l + 0.6), "thickness": 0.6,
                             "overhang": 0, "at": [[x, r4(y + h), z, 0]]})
    else:
        add(f"{name} roof", {"type": "roof", "form": "hip", "width": r4(w + 0.8), "length": r4(l + 0.8), "pitch": 38, "overhang": 0.4,
                             "at": [[x, r4(y + h), z, 0]]})

def prang(name, places, y, w, H, top=0.24, corners=True, bud=True, about=None):
    """a PRANG: the cornice on its pavilion, the redented tower bending in to its bud, the lotus finial"""
    add(f"{name} cornice", {"type": "prism", "plan": {"rect": [r4(w + 1.2), r4(w + 1.2)]}, "height": 0.6,
                            "at": [[x, y, z, 0] for x, z in places]})
    add(name, {"type": "shikhara", "width": w, "height": H, "rathas": 5, "step": r4(w * 0.035), "bhadra": 0.34, "top": top,
               "bend": 1.45, "bhumis": 5, "band": 0.07, "bandH": 0.3, "crown": False,
               **({"corners": {"scale": 0.2, "at": [0, 0.22, 0.44, 0.64]}} if corners else {}),
               "at": [[x, r4(y + 0.6), z, 0] for x, z in places], **({"_about": about} if about else {})})
    if bud:
        add(f"{name} finial", {"type": "dome", "radius": r4(w * top * 0.42), "thickness": 0.1, "sides": 12,
                               "head": {"profile": "onion", "bulge": 1.15, "neck": 0.55}, "atop": name,
                               "at": [[x, 0, z, 0] for x, z in places], "_about": "the lotus bud on the tower's top"})

# ---- the causeway, the ponds, the Terrace of Honour ----------------------------------------------------------------
XC0 = -310.0
add("causeway", {"type": "prism", "plan": {"rect": [r4(P1[0] - XC0), 9.4]}, "height": CW, "walked": True,
                 "at": [[r4((XC0 + P1[0]) / 2), 0, 0, 0]],
                 "_about": "the causeway from the western gate (a stretch of its 350m), raised over the court, paved"})
TH = (-156.9, 36.8, 12.0, 20.6)            # the Terrace of Honour: middle, the arm along the axis, its width, the arm across
tx, ta, tw, tc = TH
cross = [[r4(tx - tw / 2), r4(tc / 2)], [r4(tx + tw / 2), r4(tc / 2)], [r4(tx + tw / 2), r4(tw / 2)], [r4(tx + ta / 2), r4(tw / 2)],
         [r4(tx + ta / 2), r4(-tw / 2)], [r4(tx + tw / 2), r4(-tw / 2)], [r4(tx + tw / 2), r4(-tc / 2)], [r4(tx - tw / 2), r4(-tc / 2)],
         [r4(tx - tw / 2), r4(-tw / 2)], [r4(tx - ta / 2), r4(-tw / 2)], [r4(tx - ta / 2), r4(tw / 2)], [r4(tx - tw / 2), r4(tw / 2)]]
add("terrace of honour", {"type": "prism", "plan": {"points": cross}, "height": CW, "walked": True, "at": [[0, 0, 0, 0]],
                          "_about": "the cruciform Terrace of Honour before the west entrance, on its round columns"})
add("terrace naga balustrade", {"type": "enclosure", "plan": {"points": cross}, "thickness": 0.45, "height": 0.85, "glass": False, "openings": [],
                                "faces": {"0": [door(0, 4.4, 0.85)], "3": [door(0, 9.4, 0.85)], "6": [door(0, 4.4, 0.85)], "9": [door(0, 9.4, 0.85)]},
                                "at": [[0, CW, 0, 0]], "_about": "the naga's body along its edges, broken by the stairs and the causeway"})
LS = flight("terrace stairs", 0, CW, 4.0, [(tx, -tc / 2 - 2.4, "s"), (tx, tc / 2 + 2.4, "n")],
            about="the stairs down the ends of its arms across")
# the naga balustrades along the causeway, broken by the terrace, the stairs down to the ponds and the stair up to the temple
PX = -256.5                                # the ponds' middle, and the stairs down to them
rails = [(XC0, PX - 2.6), (PX + 2.6, tx - ta / 2), (tx + ta / 2, P1[0] - 2.4 - 2.6)]
for i, (a, b) in enumerate(rails):
    add(f"causeway naga {i + 1}", {"type": "box", "width": r4(b - a), "length": 0.45, "height": 0.85,
                                   "at": [[r4((a + b) / 2), CW, s * 4.475, 0] for s in (1, -1)],
                                   **({"_about": "the naga balustrades: the serpent's body on short posts along both sides"} if i == 0 else {})})
flight("pond stairs", 0, CW, 4.0, [(PX, -4.7 - 2.4, "s"), (PX, 4.7 + 2.4, "n")], about="the stairs down from the causeway to the ponds")
flight("causeway stair", 0, CW, 9.4, [(XC0 - 2.4, 0, "e")], about="the causeway's end (it runs on to the western gate)")
for nm, s in (("north pond", -1), ("south pond", 1)):
    add(nm, {"type": "prism", "plan": {"rect": [75.0, 48.0]}, "height": 0.06, "at": [[PX, 0, s * 57.5, 0]],
             "_about": f"the {nm.split()[0]}ern reflecting pond, the towers standing in it"})

# ---- the third enclosure: its terrace, its gallery, its gopuras and corner pavilions ---------------------------------
add("third terrace", {"type": "prism", "plan": {"rect": [r4(P1[1] - P1[0]), r4(2 * P1[2])]}, "height": Y1, "walked": True,
                      "at": [[r4((P1[0] + P1[1]) / 2), 0, 0, 0]], "_about": "the terrace the outer gallery and its court stand on"})
flight("third terrace stair west", CW, Y1, 9.4, [(P1[0] - 2.4, 0, "e")], about="the stair up from the causeway to the west entrance")
flight("third terrace stairs", 0, Y1, 6.0, [(0, -P1[2] - 4.8, "s"), (0, P1[2] + 4.8, "n"), (P1[1] + 4.8, 0, "w")],
       about="the stairs up to the north, south and east entrances")
OUT3 = {"every": 3.0, "width": 2.2, "end": 1.2, "sill": 0, "springing": 3.4, "head": flat}
IN3 = {"every": 3.0, "width": 1.4, "end": 1.2, "sill": 0.9, "springing": 2.8, "head": flat}
G3 = 15.0                                  # the west gopura's half-length along the gallery
add("third gallery", {"type": "range", "path": [[XA0, G3], [XA0, ZA], [XA1, ZA], [XA1, -ZA], [XA0, -ZA], [XA0, -G3]],
                      "width": 6.0, "height": 4.8, "thickness": 0.5,
                      "faces": {"out": OUT3, "in": IN3,
                                "in:0": {**IN3, "with": [door(CL[2] - (G3 + ZA) / 2)]}, "in:4": {**IN3, "with": [door((G3 + ZA) / 2 + CL[0])]},
                                "in:1": {**IN3, "with": [door(-(XA0 + XA1) / 2)]}, "in:2": {**IN3, "with": [door(0)]},
                                "in:3": {**IN3, "with": [door((XA0 + XA1) / 2)]},
                                "end": [door(0)]},
                      "roof": {"pitch": 35, "overhang": 0.5, "shell": 0.3}, "at": [[0, Y1, 0, 0]],
                      "_about": "the outer gallery: a colonnade outward, the bas-reliefs on its inner wall (the Churning of the Ocean of Milk, the battle of Kurukshetra), windows to the court; roofed in stone"})
pavilion("west gopura", XA0, 0, Y1, 12.0, 2 * G3, 7.2,
         {3: [door(-9.0, 2.6, 3.8), door(0, 3.2, 4.6), door(9.0, 2.6, 3.8)], 1: [door(0, 3.2, 4.6)], 0: [door(0)], 2: [door(0)]}, roof=False,
         about="the western entrance pavilion: three gates through it, the middle one the king's")
prang("west gopura towers", [(XA0, -10.5), (XA0, 10.5)], r4(Y1 + 7.8), 6.5, 6.5, top=0.45, corners=False, bud=False,
      about="the western gopura's side towers, truncated")
prang("west gopura tower", [(XA0, 0)], r4(Y1 + 7.8), 9.0, 9.0, top=0.42, corners=False, bud=False,
      about="and its middle tower, truncated")
pavilion("east gopura", XA1, 0, Y1, 12.0, 14.0, 7.2, {1: [door(0, 3.2, 4.6)], 3: [door(0, 3.2, 4.6)], 0: [door(0)], 2: [door(0)]})
pavilion("north gopura", 0, -ZA, Y1, 14.0, 12.0, 7.2, {2: [door(0, 3.2, 4.6)], 0: [door(0, 3.2, 4.6)], 1: [door(0)], 3: [door(0)]})
pavilion("south gopura", 0, ZA, Y1, 14.0, 12.0, 7.2, {0: [door(0, 3.2, 4.6)], 2: [door(0, 3.2, 4.6)], 1: [door(0)], 3: [door(0)]},
         about="the gate pavilions on the outer gallery's other axes")
for nm, x, z, fs in (("southwest", XA0, ZA, (2, 1)), ("southeast", XA1, ZA, (2, 3)), ("northeast", XA1, -ZA, (0, 3)), ("northwest", XA0, -ZA, (0, 1))):
    pavilion(f"third {nm} pavilion", x, z, Y1, 11.0, 11.0, 7.2, {f: [door(0)] for f in fs},
             about="a corner pavilion, the gallery turning through it" if nm == "southwest" else None)

# ---- the cruciform cloister (Preah Poan) and its libraries ----------------------------------------------------------
OPEN = {"every": 2.6, "width": 1.8, "end": 1.0, "sill": 0, "springing": 3.0, "head": flat}
FOOT2 = P2[0] - math.ceil((Y2 - Y1) / STEEP - 1e-9) * RUN      # where the stairs up to the second platform start
for i, z in enumerate(CL):
    x0 = XA0 + (6.0 if z == 0 else 3.0)                        # (from the gopura's back, or the gallery's inner wall)
    L = FOOT2 - x0; at = r4(CLX - (x0 + FOOT2) / 2)
    add(f"cloister gallery {i + 1}", {"type": "range", "path": [[r4(x0), z], [r4(FOOT2), z]], "width": 4.2, "height": 4.0, "thickness": 0.45,
                                      "faces": {"out": {**OPEN, "with": [door(at, 3.0, 3.0)]}, "in": {**OPEN, "with": [door(at, 3.0, 3.0)]},
                                                "end": [door(0, 3.0, 3.0)]},
                                      "roof": {"pitch": 35, "overhang": 0.4, "shell": 0.3}, "at": [[0, Y1, 0, 0]],
                                      **({"_about": "the cruciform cloister (Preah Poan): three galleries along the axis from the outer gallery to the stairs up, one across them -- four courts, each with its basin; pillared both sides"} if i == 0 else {})})
add("cloister gallery across", {"type": "range", "path": [[CLX, CL[0]], [CLX, CL[2]]], "width": 4.2, "height": 4.0, "thickness": 0.45,
                                "faces": {"out": {**OPEN, "with": [door(0, 3.0, 3.0)]}, "in": {**OPEN, "with": [door(0, 3.0, 3.0)]}, "end": [door(0, 3.0, 3.0)]},
                                "roof": {"pitch": 35, "overhang": 0.4, "shell": 0.3}, "at": [[0, Y1, 0, 0]]})
# the four courts' basins: the west two between the outer gallery and the gallery across, the east two between it and the stairs
BW = ((XA0 + 3.0, CLX - 2.1), (CLX + 2.1, FOOT2))
for k, (a, b) in enumerate(BW):
    add(f"cloister basins {['west', 'east'][k]}", {"type": "enclosure", "plan": {"rect": [r4(b - a - 2.0), 15.0]}, "thickness": 0.6, "height": 0.5,
                                                  "glass": False, "openings": [], "at": [[r4((a + b) / 2), Y1, s * 11.75, 0] for s in (-1, 1)],
                                                  **({"_about": "the kerbs of the basins in the cloister's four courts"} if k == 0 else {})})

def library(name, x, z, y, pw, pl, ph, hw, hl, hh, about):
    """a LIBRARY: its plinth, a stair up each end (east and west), the hall on it under a steep stone roof"""
    add(f"{name} plinth", {"type": "prism", "plan": {"rect": [pw, pl]}, "height": ph, "walked": True, "at": [[x, y, z, 0]], "_about": about})
    L = math.ceil(ph / 0.19 - 1e-9) * 0.3
    flight(f"{name} stairs", y, r4(y + ph), 2.2, [(r4(x + pw / 2 + L), z, "w"), (r4(x - pw / 2 - L), z, "e")])
    add(f"{name} hall", {"type": "enclosure", "plan": {"rect": [hw, hl]}, "thickness": 0.6, "height": hh, "glass": False, "openings": [],
                         "faces": {"1": [door(0, 1.6, 2.8)], "3": [door(0, 1.6, 2.8)],
                                   "0": {"every": 3.0, "width": 0.9, "end": 1.2, "sill": 0.9, "springing": 2.2, "head": flat},
                                   "2": {"every": 3.0, "width": 0.9, "end": 1.2, "sill": 0.9, "springing": 2.2, "head": flat}},
                         "at": [[x, r4(y + ph), z, 0]]})
    add(f"{name} roof", {"type": "roof", "form": "gable", "width": r4(hl + 0.6), "length": r4(hw + 0.6), "pitch": 48, "overhang": 0.3,
                         "at": [[x, r4(y + ph + hh), z, Q]]})
library("cloister library north", -89.7, -67.0, Y1, 24.0, 12.0, 1.2, 16.0, 6.0, 4.5, "the libraries either side of the cruciform cloister, on their plinths")
library("cloister library south", -89.7, 67.0, Y1, 24.0, 12.0, 1.2, 16.0, 6.0, 4.5, "")
parts["cloister library south plinth"].pop("_about")

# ---- the second enclosure ----------------------------------------------------------------------------------------
add("second platform", {"type": "prism", "plan": {"rect": [r4(P2[1] - P2[0]), r4(2 * P2[2])]}, "height": Y2, "walked": True,
                        "batter": {"out": 1.0}, "at": [[r4((P2[0] + P2[1]) / 2), 0, 0, 0]],
                        "_about": "the second enclosure's platform, its sides battered"})
flight("second platform stairs west", Y1, Y2, 3.0, [(FOOT2, z, "e") for z in CL], steep=True,
       about="the steep stairs up from the cloister's three galleries")
L2 = math.ceil((Y2 - Y1) / STEEP - 1e-9) * RUN
flight("second platform stairs", Y1, Y2, 3.0, [(0, -P2[2] - L2, "s"), (0, P2[2] + L2, "n"), (P2[1] + L2, 0, "w")], steep=True,
       about="and on the other three axes")
OUT2 = {"every": 3.2, "width": 1.2, "end": 1.2, "sill": 1.0, "springing": 3.0, "head": flat}
IN2 = {"every": 3.2, "width": 1.6, "end": 1.2, "sill": 0.6, "springing": 3.2, "head": flat}
G2 = 7.0
dz0 = r4(CL[2] - (G2 + ZB) / 2)
rows2 = lambda d: {"out": {**OUT2, "with": d}, "in": {**IN2, "with": d}}
add("second gallery", {"type": "range", "path": [[XB0, G2], [XB0, ZB], [XB1, ZB], [XB1, -ZB], [XB0, -ZB], [XB0, -G2]],
                       "width": 5.0, "height": 5.0, "thickness": 0.5,
                       "faces": {"out": OUT2, "in": IN2,
                                 **{f"{k}:0": v for k, v in rows2([door(dz0, 3.0)]).items()},
                                 **{f"{k}:4": v for k, v in rows2([door(-dz0, 3.0)]).items()},
                                 **{f"{k}:1": v for k, v in rows2([door(-(XB0 + XB1) / 2, 3.0)]).items()},
                                 **{f"{k}:2": v for k, v in rows2([door(0, 3.0)]).items()},
                                 **{f"{k}:3": v for k, v in rows2([door((XB0 + XB1) / 2, 3.0)]).items()},
                                 "end": [door(0, 3.0)]},
                       "roof": {"pitch": 35, "overhang": 0.5, "shell": 0.3}, "at": [[0, Y2, 0, 0]],
                       "_about": "the second gallery: closed to the outside but for its windows (the devatas carved between them), open to its court"})
pavilion("second west gopura", XB0, 0, Y2, 10.0, 2 * G2, 7.2, {3: [door(0, 3.0, 4.2)], 1: [door(0, 3.0, 4.2)], 0: [door(0, 3.0)], 2: [door(0, 3.0)]},
         about="the second gallery's gate pavilions")
pavilion("second east gopura", XB1, 0, Y2, 10.0, 12.0, 7.2, {1: [door(0, 3.0, 4.2)], 3: [door(0, 3.0, 4.2)], 0: [door(0, 3.0)], 2: [door(0, 3.0)]})
pavilion("second north gopura", 0, -ZB, Y2, 12.0, 10.0, 7.2, {2: [door(0, 3.0, 4.2)], 0: [door(0, 3.0, 4.2)], 1: [door(0, 3.0)], 3: [door(0, 3.0)]})
pavilion("second south gopura", 0, ZB, Y2, 12.0, 10.0, 7.2, {0: [door(0, 3.0, 4.2)], 2: [door(0, 3.0, 4.2)], 1: [door(0, 3.0)], 3: [door(0, 3.0)]})
for nm, x, z, fs in (("southwest", XB0, ZB, (2, 1)), ("southeast", XB1, ZB, (2, 3)), ("northeast", XB1, -ZB, (0, 3)), ("northwest", XB0, -ZB, (0, 1))):
    pavilion(f"second {nm} pavilion", x, z, Y2, 9.0, 9.0, 7.2, {f: [door(0, 3.0)] for f in fs}, roof=False,
             about="a corner pavilion of the second gallery, a tower on it" if nm == "southwest" else None)
prang("second corner towers", [(XB0, ZB), (XB1, ZB), (XB1, -ZB), (XB0, -ZB)], r4(Y2 + 7.8), 7.4, 9.0, top=0.3, corners=False,
      about="the second gallery's corner towers")
library("library north", -48.4, -14.5, Y2, 14.0, 9.0, 1.0, 9.0, 4.5, 3.8, "the two libraries in the second enclosure's court")
library("library south", -48.4, 14.5, Y2, 14.0, 9.0, 1.0, 9.0, 4.5, 3.8, "")
parts["library south plinth"].pop("_about")

# ---- the bakan: the platform, its stairs, its galleries, the five towers --------------------------------------------
add("bakan", {"type": "prism", "plan": {"rect": [2 * PB, 2 * PB]}, "height": Y3, "walked": True, "batter": {"out": 3.0}, "at": [[0, 0, 0, 0]],
              "_about": "the BAKAN, the summit platform: thirteen metres over the second, its sides battered and moulded"})
LB = math.ceil((Y3 - Y2) / STEEP - 1e-9) * RUN
flight("bakan stairs", Y2, Y3, 3.0, [(-PB - LB, 0, "e"), (PB + LB, 0, "w"), (0, -PB - LB, "s"), (0, PB + LB, "n")], steep=True,
       about="the bakan's stairs, steep as ladders: the climb to the gods is hard")
OUTB = {"every": 3.0, "width": 1.0, "end": 1.0, "sill": 0.8, "springing": 2.6, "head": flat}
INB = {"every": 3.0, "width": 1.4, "end": 1.0, "sill": 0.5, "springing": 2.8, "head": flat}
rowsB = lambda d: {"out": {**OUTB, "with": d}, "in": {**INB, "with": d}}
add("bakan gallery", {"type": "range", "path": [[-C, 4.0], [-C, C], [C, C], [C, -C], [-C, -C], [-C, -4.0]],
                      "width": 4.5, "height": 4.0, "thickness": 0.5,
                      "faces": {"out": OUTB, "in": INB,
                                **{f"{k}:{s}": v for s in (1, 2, 3) for k, v in rowsB([door(0, 3.5, 3.5)]).items()},
                                "end": [door(0, 3.4, 3.0)]},
                      "roof": {"pitch": 35, "overhang": 0.4, "shell": 0.3}, "at": [[0, Y3, 0, 0]],
                      "_about": "the bakan's square gallery, balustered windows out over the temple"})
COLB = {"every": 2.8, "width": 2.0, "end": 1.0, "sill": 0, "springing": 3.6, "head": flat}
SA = 7.5                                   # the sanctuary's half-width
for nm, (dx, dz) in (("west", (-1, 0)), ("east", (1, 0)), ("north", (0, -1)), ("south", (0, 1))):
    xing = r4((C - (SA + PB) / 2))
    add(f"bakan cross gallery {nm}", {"type": "range", "path": [[dx * SA, dz * SA], [dx * PB, dz * PB]], "width": 7.8, "height": 4.5, "thickness": 0.5,
                                      "faces": {"out": {**COLB, "with": [door(xing, 3.4, 3.0)]}, "in": {**COLB, "with": [door(xing, 3.4, 3.0)]},
                                                "end": [door(0, 2.6, 4.0)]},
                                      "roof": {"pitch": 35, "overhang": 0.4, "shell": 0.3}, "at": [[0, Y3, 0, 0]],
                                      **({"_about": "the cross of pillared galleries from the sanctuary to the stairs, the bakan's court in four"} if nm == "west" else {})})
add("sanctuary", {"type": "enclosure", "plan": {"rect": [2 * SA, 2 * SA]}, "thickness": 1.2, "height": 8.5, "glass": False, "openings": [],
                  "faces": {str(k): [door(0, 2.6, 4.8)] for k in range(4)}, "at": [[0, Y3, 0, 0]],
                  "_about": "the central sanctuary, once Vishnu's, its doors on the four axes"})
prang("central tower", [(0, 0)], r4(Y3 + 8.5), 15.0, 31.5, top=0.2,
      about="the CENTRAL TOWER: Meru's summit, sixty-five metres over the ground, five storeys bending in to the lotus bud")
for nm, x, z, fs in (("southwest", -C, C, (2, 1)), ("southeast", C, C, (2, 3)), ("northeast", C, -C, (0, 3)), ("northwest", -C, -C, (0, 1))):
    add(f"bakan {nm} pavilion", {"type": "enclosure", "plan": {"rect": [13.0, 13.0]}, "thickness": 1.0, "height": 6.2, "glass": False, "openings": [],
                                 "faces": {str(f): [door(0, 3.4, 3.4)] for f in fs}, "at": [[x, Y3, z, 0]],
                                 **({"_about": "the corner pavilions the square gallery turns through, each under its tower"} if nm == "southwest" else {})})
prang("corner towers", [(-C, C), (C, C), (C, -C), (-C, -C)], r4(Y3 + 6.2), 11.0, 21.0, top=0.22,
      about="the four corner towers of the quincunx, lower than the central one: Meru's other peaks")

doc = {
    "name": "Angkor Wat",
    "_about": "ANGKOR WAT (c. 1150): the temple-mountain facing west -- the causeway with its naga balustrades and the ponds, the "
              "Terrace of Honour, the outer gallery round its terrace (gopuras on its axes, the western crowned by three towers), "
              "the cruciform cloister and its libraries, the second gallery on its platform with its corner towers and libraries, "
              "and the bakan climbed by its ladder-steep stairs: the square gallery, the cross of galleries and the quincunx of "
              "prangs, the central one sixty-five metres up. The plan the survey's, made symmetric. Generated by "
              "tools/archgen/angkor_wat.py -- edit the script for arithmetic changes. East is +x, south +z.",
    "params": {"detail": 4},
    "base": {"height": 0.3, "steps": 1, "stepOut": 0.5, "margin": 4},
    "railing": {"type": "stone", "height": 0.9},
    "build": build,
    "parts": parts,
}
out = os.path.join(ROOT, "assets", "architecture", "angkor-wat.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts")
