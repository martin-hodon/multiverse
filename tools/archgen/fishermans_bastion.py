# THE FISHERMAN'S BASTION (Halászbástya), Budapest (Frigyes Schulek, 1895-1902): a neo-Romanesque lookout terrace
# along the edge of Castle Hill, in white limestone. Three levels, all walked:
#   - the GROUND in front, and the lower hall behind a long open arcade (round arches on slender piers);
#   - the LOWER TERRACE on the hall's roof, crenellated along its drop, reached by the grand DOUBLE STAIR -- two
#     flights climbing along the front toward a projecting landing (a salient) in the middle;
#   - on it, set back, the UPPER GALLERY: an arcaded cloister walk open toward the view, windows toward the back,
#     and on its roof the UPPER WALK behind battlements, reached by a flight at each end.
# SEVEN towers stand on the lower terrace against the upper gallery, each with a door onto the terrace, an open
# belvedere and a steep tent cap (`domed-tower`, cap "trigonal"): the tallest in the middle behind the landing,
# three smaller each side, lower toward the ends.
#   x runs along the bastion, +z toward the Danube (the drop). Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
r4 = lambda v: round(v, 4)

# ---- the numbers
LL, DL, HL, SL, TLW = 144.0, 20.0, 6.0, 0.7, 1.2      # lower hall: length, depth, wall height, roof slab, walls
ZL = 3.0                                              # its middle (z from -7 to +13)
TL = HL + SL                                          # the lower terrace, 6.7
LU, DU, HU, SU, TUW = 116.0, 7.0, 5.3, 0.7, 0.9       # upper gallery
ZU = -3.8                                             # its middle (z from -7.3 to -0.3: flush with the terrace's back edge)
TU = TL + HU + SU                                     # the upper walk, 12.7
OV = 0.3                                              # the slabs' overhang
PT, PH, MH, MW, MS = 0.45, 1.0, 0.6, 0.8, 2.0         # parapet thickness, height; merlon height, width, spacing

arch = lambda w, s: {"width": w, "sill": s, "head": {"profile": "semicircular"}}

FW_, FP = 0.5, 35                                    # the weathered plinth at a wall's foot: out, pitch

def fillet(name, a, b, face, y, along, inner):
    """a sloped stone plinth (a weathering) at the foot of a wall face from a to b, `inner` the side it lies on:
    a chamfer where the floor meets the wall -- no ledge of floor too narrow to stand on is left along it"""
    c = face + inner * FW_ / 2
    add(name, {"type": "roof", "form": "shed", "width": FW_, "length": b - a, "pitch": FP,
               "at": [[r4((a + b) / 2), r4(y), r4(c), inner * math.pi / 2] if along == "x" else [r4(c), r4(y), r4((a + b) / 2), 0 if inner < 0 else math.pi]]})

def parapet(name, a, b, c, y, along="x", about=None, inner=None):
    """a crenellated parapet from a to b along x (at z = c) or along z (at x = c), standing at y; `inner` (+1/-1): the
    walked side, where a weathered plinth runs along its foot"""
    L = b - a; m = (a + b) / 2
    if inner: fillet(name + " plinth", a, b, c + inner * PT / 2, y, along, inner)
    wall = {"type": "box", "width": L if along == "x" else PT, "length": PT if along == "x" else L, "height": PH,
            "at": [[r4(m), r4(y), r4(c), 0] if along == "x" else [r4(c), r4(y), r4(m), 0]]}
    if about: wall["_about"] = about
    add(name, wall)
    n = int((L - MW) // MS) + 1
    if n < 1 or L < MW + 0.2: return
    s0 = m - (n - 1) * MS / 2
    pts = [s0 + k * MS for k in range(n)]
    add(name + " merlons", {"type": "box", "width": MW if along == "x" else PT, "length": PT if along == "x" else MW, "height": MH,
                            "at": [[r4(p), r4(y + PH), r4(c), 0] if along == "x" else [r4(c), r4(y + PH), r4(p), 0] for p in pts],
                            "standsOn": [name]})

# ---- the lower hall and its arcade
# (every opening dressed the Romanesque way -- surround.js: recessed orders, nook shafts, cushion capitals, imposts --
#  the arcades in one order or two, sharing their piers; the end doors as portals in three)
PORTAL = {"surround": {"style": "romanesque", "orders": 3}}
NL, WL = 36, 2.8
add("lower hall", {"type": "enclosure", "glass": False, "plan": {"rect": [LL, DL]}, "thickness": TLW, "height": HL,
                   "faces": {"0": {"pattern": str(NL), "width": WL, "gap": r4((LL - 2 - NL * WL) / NL), "pier": r4((LL - 2 - NL * WL) / NL),
                                   "sill": 0, "springing": r4(HL - WL / 2 - 0.9), "head": {"profile": "semicircular"}, "surround": {"style": "romanesque", "orders": 1}},
                             "1": [{"at": 0, **arch(3.0, 0), "springing": 3.2, **PORTAL}], "3": [{"at": 0, **arch(3.0, 0), "springing": 3.2, **PORTAL}],
                             "2": []},
                   "at": [[0, 0, ZL, 0]],
                   "_about": "the lower hall: a long open arcade of round arches on slender piers toward the river, a door at each end, the back closed against the hill"})
add("hall columns", {"type": "column", "radius": 0.45, "height": HL, "sides": 12,
                     "at": [[float(x), 0, z, 0] for z in (-0.45, 6.0) for x in range(-66, 67, 6)],
                     "_about": "two rows of columns down the hall, the first under the upper gallery's front wall"})
add("lower terrace", {"type": "box", "width": LL + 2 * OV, "length": DL + 2 * OV, "height": SL, "at": [[0, HL, ZL, 0]], "walked": True,
                      "standsOn": ["lower hall"], "_about": "the hall's roof: the lower terrace, walked"})
zf = ZL + DL / 2 + OV                                  # the terrace's front edge (13.3)
zb = ZL - DL / 2 - OV                                  # its back edge (-7.3)
xe = LL / 2 + OV                                       # its ends (72.3)

# ---- the upper gallery: a cloister walk, open arcade to the front, unglazed windows to the back
NU, WU = 34, 2.4
gapU = r4((LU - 2 - NU * WU) / NU)
spU = r4(HU - WU / 2 - 0.8)
add("upper gallery", {"type": "enclosure", "glass": False, "plan": {"rect": [LU, DU]}, "thickness": TUW, "height": HU,
                      "faces": {"0": {"pattern": str(NU), "width": WU, "gap": gapU, "pier": gapU, "sill": 0, "springing": spU, "head": {"profile": "semicircular"}, "surround": {"style": "romanesque", "orders": 1}},
                                "2": {"pattern": str(NU), "width": WU, "gap": gapU, "pier": gapU, "sill": 1.0, "springing": spU, "head": {"profile": "semicircular"}, "surround": {"style": "romanesque", "orders": 1}},
                                "1": [], "3": []},
                      "at": [[0, TL, ZU, 0]], "standsOn": ["lower terrace"],
                      "_about": "the upper gallery on the terrace: the arcaded walk, open to the view, windows over the drop behind"})
add("upper walk", {"type": "box", "width": LU + 2 * OV, "length": DU + 2 * OV, "height": SU, "at": [[0, TL + HU, ZU, 0]], "walked": True,
                   "standsOn": ["upper gallery"], "_about": "its roof: the upper walk behind battlements"})
xu = LU / 2 + OV                                       # the upper walk's ends (58.3)
zuf, zub = ZU + DU / 2 + OV, ZU - DU / 2 - OV          # its front (0.3) and back (-7.3) edges

# ---- the grand double stair and the landing it arrives on
SW, SD = 8.0, 5.2                                      # the landing: across, out
add("landing", {"type": "box", "width": SW, "length": SD, "height": TL, "at": [[0, 0, r4(zf + SD / 2), 0]], "walked": True,
                "_about": "the landing: a salient in front of the middle of the terrace, where the double stair arrives"})
FW = 2.8                                               # the flights' width
nS = round(TL / 0.16); runS = 0.32; LS = nS * runS
z0 = zf + 0.05
add("grand stair", {"type": "flight", "width": FW, "run": runS, "rise": 0.16, "base": 0, "top": TL, "landing": 0,
                    "at": [[r4(SW / 2 + LS), 0, r4(z0), math.pi], [r4(-SW / 2 - LS), 0, r4(z0 + FW), 0]],
                    "_about": "the grand double stair: two flights climbing along the front toward the landing in the middle"})

# ---- flights from the terrace up to the upper walk, one at each end
nE = round((TU - TL) / 0.1667); runE = 0.3; LE = nE * runE
zE = -5.0; FE = 2.5
add("walk stairs", {"type": "flight", "width": FE, "run": runE, "rise": 0.1667, "base": TL, "top": TU, "landing": 0,
                    "at": [[r4(xu + LE), 0, zE, math.pi], [r4(-xu - LE), 0, zE + FE, 0]], "standsOn": ["lower terrace"],
                    "_about": "a flight at each end of the upper gallery, from the terrace up onto its walk"})

# ---- parapets: the lower terrace (a gap at the landing), the landing, the upper walk (gaps at the stairs)
yT, yU = TL, TU
for s, nm in ((1, "east"), (-1, "west")):
    parapet(f"terrace parapet {nm}", *sorted((s * SW / 2, s * xe)), zf - PT / 2, yT, inner=-1,
            about="the battlemented parapet along the terrace's drop" if s > 0 else None)
    parapet(f"terrace end {nm}", zb + PT, zf - PT, s * (xe - PT / 2), yT, along="z", inner=-s)
    parapet(f"terrace back {nm}", *sorted((s * (LU / 2), s * (xe - PT))), zb + PT / 2, yT, inner=1)
    parapet(f"landing side {nm}", z0 + FW, zf + SD - PT, s * (SW / 2 - PT / 2), yT, along="z", inner=-s)
    parapet(f"walk end {nm} back", zub + PT, zE, s * (xu - PT / 2), yU, along="z", inner=-s)
    parapet(f"walk end {nm} front", zE + FE, zuf - PT, s * (xu - PT / 2), yU, along="z", inner=-s)
parapet("landing front", -SW / 2, SW / 2, zf + SD - PT / 2, yT, inner=-1)
parapet("walk front", -xu, xu, zuf - PT / 2, yU, about="the battlements along the upper walk", inner=-1)
parapet("walk back", -xu, xu, zub + PT / 2, yU, inner=1)

# ---- weathered plinths along the long plain walls' feet: the hall's back, inside and out; the upper gallery's back, inside
fillet("hall plinth", -LL / 2, LL / 2, ZL - DL / 2, 0, "x", -1)
fillet("hall inner plinth", -LL / 2 + TLW, LL / 2 - TLW, ZL - DL / 2 + TLW, 0, "x", 1)
fillet("gallery inner plinth", -LU / 2 + TUW, LU / 2 - TUW, ZU - DU / 2 + TUW, TL, "x", 1)

# ---- the seven towers on the terrace, against the upper gallery, doors toward the river
yaw = -math.pi / 8                                     # an octagon's door to +z: yaw 0 - 180/8 degrees
bl = ["tower", "head", "neck", "drum", "cornice", "cap", "finial"]
def tower(name, xs, R, H, drumH, rise, about):
    ap = R * math.cos(math.pi / 8)
    z = r4(zuf + 0.05 + ap)
    add(name, comp("components/domed-tower", {"sides": 8, "R": R, "H": H, "t": 0.7, "drumR": r4(R * 0.78), "drumH": drumH, "cap": "trigonal",
                                              "capR": r4(R * 0.92), "capRise": rise, "capRibs": 8, "kok": 0.5, "winW": r4(R * 0.2),
                                              "doorH": 3.0, "finial": r4(R * 0.35), "glazed": 0},
                   [[float(x), TL, z, yaw] for x in xs], build=bl, standsOn=["lower terrace"], _about=about))
tower("main tower", [0], 5.2, 14.0, 4.5, 14.0, "the main tower behind the landing, the tallest: an open belvedere under a steep tent")
tower("towers inner", [-17, 17], 4.2, 10.0, 3.2, 8.5, "the towers either side of it")
tower("towers middle", [-35, 35], 4.0, 9.0, 3.0, 7.5, "smaller toward the ends")
tower("towers outer", [-52, 52], 3.8, 8.0, 2.8, 6.5, "and the smallest at the gallery's ends")

doc = {"name": "Fisherman's Bastion",
       "_about": "THE FISHERMAN'S BASTION (Halászbástya), Budapest (Schulek, 1895-1902): a neo-Romanesque lookout terrace in white limestone along Castle Hill's edge, in three walked levels -- the lower hall behind its long open arcade; the lower terrace on its roof behind battlements, reached by the grand double stair to a projecting landing; the upper gallery set back on it, an arcaded cloister walk, and on its roof the upper walk behind battlements, climbed by a flight at each end -- and seven towers along the terrace with open belvederes and steep tent caps (`domed-tower`), the tallest in the middle.",
       "params": {"detail": 4}, "base": {"height": 0.4, "steps": 2, "stepOut": 0.5, "margin": 4}, "railing": {"type": "balusters"},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/fishermans-bastion.json"), "w").write(json.dumps(doc, indent=2) + "\n")
