# SCHLOSS SCHWERIN (rebuilt 1845-57 by Demmler, Stüler and Willebrand on the old castle's foundations) ON ITS REAL PLAN. It is not a regular figure: an
# irregular ring of seven faces round a five-cornered court, every wing its own depth, height and roof, the old east and north ranges lower under their
# gables, the town front only 25 m wide between two towers with the gilded dome behind it. The plan and the first heights are OpenStreetMap's (relation
# 20744 and its building parts), turned 43.4 degrees so the town front looks to -z; the Wikipedia/Commons photographs and the 19th-century plan were read to
# place things and to correct OSM's towers, which it has too low (it gives the dome 38 m; the town-front photo, scaled by the 25 m front, gives about 45).
# So: plan measured; heights of walls and the big tower OSM's; turret stages read off photographs, not surveyed.
#   Standing in: the `court` is one ring of rooms; the wings' top storeys, roofs, gables, risalits, the towers and the chapel stand on and round it.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n); return n
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
r4 = lambda v: round(v, 4)

PHI = math.radians(-43.4)
def osm(x, y):                                  # OSM metres (x east, y north, from the castle) -> the plan (x, z), the town front to -z
    return (x * math.cos(PHI) - y * math.sin(PHI), -(x * math.sin(PHI) + y * math.cos(PHI)))
# the ring, walked from the town front's two ends: G A front, A B north, B C the link by the chapel, C D east, D E south-east, E F south, F G west
RING = {"G": (-26, 70), "A": (-8, 87), "B": (46, 75), "C": (53, 57), "D": (50, 26), "E": (4, -6), "F": (-35, 20)}
ORDER = ["A", "G", "F", "E", "D", "C", "B"]     # (the engine's winding: the outside to the right of every edge; face 0 the town front)
WING = ["front", "west", "south", "southeast", "east", "link", "north"]
DEPTHS = [19.0, 20.5, 19.0, 15.5, 18.5, 18.0, 20.0]      # (from OSM's court outline: the wings are not one depth)
raw = [osm(*RING[k]) for k in ORDER]
xs = [p[0] for p in raw]; zs = [p[1] for p in raw]
FORE = 22.0                                      # the forecourt before the portal
ox = (min(xs) + max(xs)) / 2; oz = (min(zs) - FORE + max(zs)) / 2
def pt(x, y): a, b = osm(x, y); return (a - ox, b - oz)
O = [pt(*RING[k]) for k in ORDER]
N, H = 4, 4.4; EAVE = N * H                      # the ring: four storeys; the town front, west and south wings have a fifth
HIGH = {"front", "west", "south"}; UP = 4.6
class F:                                         # a face's frame: `s` along it from its middle, `off` out from its wall
    def __init__(s, i):
        s.i = i; s.p, s.q = O[i], O[(i + 1) % len(O)]; s.L = math.dist(s.p, s.q); s.e = ((s.q[0] - s.p[0]) / s.L, (s.q[1] - s.p[1]) / s.L)
        s.n = (-s.e[1], s.e[0])                  # the outside is on the right of p->q in (x, z)
        cx = sum(a for a, _ in O) / len(O); cz = sum(b for _, b in O) / len(O)
        s.m = ((s.p[0] + s.q[0]) / 2, (s.p[1] + s.q[1]) / 2)
        if (s.m[0] - cx) * s.n[0] + (s.m[1] - cz) * s.n[1] < 0: s.n = (-s.n[0], -s.n[1])
        s.d = DEPTHS[i]; s.yaw = math.atan2(s.n[0], s.n[1]); s.eave = EAVE + (UP if WING[i] in HIGH else 0)
    def at(s, along=0.0, off=0.0): return (s.m[0] + s.e[0] * along + s.n[0] * off, s.m[1] + s.e[1] * along + s.n[1] * off)
    def place(s, along=0.0, off=0.0, y=0.0, turn=0.0): a, b = s.at(along, off); return [r4(a), r4(y), r4(b), r4(s.yaw + turn)]
FACE = {w: F(i) for i, w in enumerate(WING)}
def court_corner(i):                             # (where a face's depth line meets its neighbour's: the ring's own arithmetic, assemble.js insetBy)
    f0, f1 = FACE[WING[i - 1]], FACE[WING[i]]
    x0, z0 = f0.at(0, -f0.d); x1, z1 = f1.at(0, -f1.d); c = f0.e[0] * f1.e[1] - f0.e[1] * f1.e[0]
    u = ((x1 - x0) * f1.e[1] - (z1 - z0) * f1.e[0]) / c
    return (x0 + f0.e[0] * u, z0 + f0.e[1] * u)
CV = [court_corner(i) for i in range(len(O))]

add("ring", {"type": "court", "plan": {"points": [[r4(x), r4(z)] for x, z in O]}, "depths": DEPTHS, "storeys": N, "storeyH": H, "axis": 3.3, "winH": 2.5,
             "gate": {"face": 0, "width": 4.2, "height": 3.9}, "roof": False, "courses": True, "stairFace": 6, "surroundCourt": False,
             "surround": [None, {"pediment": "alternate"}, {"head": "cornice"}, None],
             "_about": "the castle's ring of rooms: seven faces of different lengths and depths round the five-cornered court, walked all the way round, the gate through the town front"})

# ---- the fifth storey of the high wings, their roofs; a gable and its cross roof
def wing_upper(w):
    f = FACE[w]; i = f.i; L = f.L
    # (a trapezoid over the ring's walls, its inner corners the court's own)
    pts = [O[i], O[(i + 1) % len(O)], CV[(i + 1) % len(O)], CV[i]]; Li = math.dist(pts[2], pts[3])
    win = {"pattern": str(max(3, int(L / 3.3) - 1)), "width": 1.3, "gap": 2.0, "sill": 0.9, "springing": 3.0, "head": {"profile": "segmental", "seg": 0.35}, "surround": {"head": "cornice"}}
    add(f"{w} top storey", {"type": "enclosure", "plan": {"points": [[r4(x), r4(z)] for x, z in pts]}, "thickness": 0.8, "height": UP, "glass": True,
                            "faces": {"0": [{"openings": win}], "1": [{"openings": []}], "2": [{"openings": {**win, "pattern": str(int(Li / 3.3) - 1)} if Li > 10 else []}], "3": [{"openings": []}]},
                            "at": [[0, EAVE, 0, 0]], "_about": f"the {w} wing's fifth storey, over the ring"})
    add(f"{w} top floor", {"type": "prism", "plan": {"points": [[r4(x), r4(z)] for x, z in pts]}, "height": 0.3, "flatRoof": True, "at": [[0, EAVE + UP - 0.3, 0, 0]]})
for w in HIGH: wing_upper(w)

def wing_roof(w, form="mansard", pitch=62, cut=0.0, **kw):
    f = FACE[w]; a, b = f.at(0, -f.d / 2)
    add(f"{w} roof", {"type": "roof", "form": form, "width": f.d + 0.6, "length": f.L - cut, "pitch": pitch, "overhang": 0.5, **kw,
                      "at": [[r4(a), f.eave, r4(b), r4(math.atan2(f.e[0], f.e[1]))]], "_about": f"the {w} wing's roof, its own: a tall French mansard over the Renaissance front" if form == "mansard" else f"the {w} wing's roof"})
wing_roof("west", lowerPitch=68, breakH=5.0, pitch=28); wing_roof("south", lowerPitch=68, breakH=5.0, pitch=28)
wing_roof("southeast", lowerPitch=66, breakH=4.5, pitch=28); wing_roof("front", form="hip", pitch=50)
wing_roof("north", form="gable", pitch=46); wing_roof("east", form="gable", pitch=46); wing_roof("link", form="hip", pitch=50)

def stepped(w, h, steps=4):                      # a stepped gable's outline, feet at y 0, half width w/2
    pts = [(-w / 2, 0.0)]
    for k in range(steps):
        x0 = -w / 2 * (1 - k / steps); y1 = h * (k + 1) / (steps + 0.6)
        x1 = -w / 2 * (1 - (k + 1) / steps) if k + 1 < steps else -w / 2 / steps * 0.75
        pts += [(x0 + w * 0.02, y1), (x1, y1)]
    top = h
    pts += [(pts[-1][0], top), (-pts[-1][0], top)]
    return pts + [(-x, y) for x, y in reversed(pts[1:-2])] + [(w / 2, 0.0)]

gable_at = {}
def cross_gable(w, along, gw, gh, kind="stepped", roof=True, y=None, name=None, off=0.0, reach=None):
    """a gable standing on the wall of wing `w` at `along`, its own little roof running back into the wing's: what makes the north and east wings' skyline"""
    f = FACE[w]; n = gable_at.setdefault(w, 0); gable_at[w] += 1; y = f.eave if y is None else y; nm = name or f"{w} gable"
    outline = stepped(gw, gh) if kind == "stepped" else [(-gw / 2, 0), (gw / 2, 0), (0, gh)]
    add(f"{nm} {n}", {"type": "screen", "outline": [[r4(a), r4(b)] for a, b in outline], "t": 0.7, "at": [f.place(along, off + 0.15, y)], "_about": f"a gable of the {w} wing"})
    if roof:
        pitch = math.degrees(math.atan2(gh * 0.82, gw / 2))
        rl = reach or f.d * 0.5
        a, b = f.at(along, off - rl / 2)
        add(f"{nm} roof {n}", {"type": "roof", "form": "gable", "width": r4(gw * 0.92), "length": r4(rl), "pitch": r4(pitch), "overhang": 0.1,
                               "at": [[r4(a), y, r4(b), r4(f.yaw)]]})
    return n

# (the east wing, red: three great stepped gables; the north wing: six plain ones, OSM's six cross ridges; the south-east: five smaller, stepping down the wall's offsets)
for s in (-11.0, 0.0, 11.0): cross_gable("east", s, 8.5, 7.5, name="great gable")
for s in (-22.0, -13.0, -4.0, 5.0, 14.0, 23.0): cross_gable("north", s, 6.8, 6.0, name="north gable")
for s in (-17.0, -8.0, 1.0, 10.0, 19.0): cross_gable("southeast", s, 5.0, 4.5, kind="plain", name="dormer gable", reach=5.0, y=FACE["southeast"].eave + 0.2)

# ---- dormers on the mansards, risalits with their great gables
def dormers(w, alongs, y_off=0.6, gw=2.4, gh=3.0, into=1.3):
    f = FACE[w]; pl = [f.place(s, -into, f.eave + y_off) for s in alongs]
    add(f"{w} dormers", {"type": "screen", "outline": [[-gw / 2, 0], [gw / 2, 0], [gw / 2, gh * 0.55], [0, gh], [-gw / 2, gh * 0.55]], "t": 2.2, "at": pl, "_about": f"the {w} wing's dormers, a stone gable each"})
dormers("west", [-20.0, -14.0, 14.0, 20.0]); dormers("south", [-16.0, -10.5, 10.5, 16.0])

def risalit(w, along, rw, out, name, gh=7.0, kind="stepped"):
    f = FACE[w]; top = f.eave + 1.0
    win = {"pattern": str(max(2, int(rw / 3.0))), "width": 1.5, "gap": 1.5, "sill": 0.9, "springing": 3.0, "head": {"profile": "semicircular"}, "surround": {"head": "cornice"}}
    # (its face 0 looks out from the wall: the enclosure's front is its -z, turned to the wing's outside)
    add(name, {"type": "enclosure", "plan": {"rect": [rw, out * 2]}, "thickness": 0.7, "height": top, "glass": True,
               "tiers": [{"h": top / 5, "openings": []}] * 4 + [{"openings": []}],
               "faces": {"0": [{"h": top / 5, "openings": win}] * 4 + [{"openings": win}]}, "courses": True,
               "at": [f.place(along, 0.0, 0.0)], "_about": "a risalit, the wall stepping forward under its own gable"})
    a, b = f.at(along, out + 0.15)
    add(f"{name} gable", {"type": "screen", "outline": [[r4(x), r4(y)] for x, y in stepped(rw, gh)], "t": 0.9, "at": [f.place(along, out + 0.15, top)]})
    a, b = f.at(along, out - f.d * 0.28)
    add(f"{name} gable roof", {"type": "roof", "form": "gable", "width": r4(rw * 0.94), "length": r4(f.d * 0.56), "pitch": r4(math.degrees(math.atan2(gh * 0.82, rw / 2))), "overhang": 0.1, "at": [[r4(a), top, r4(b), r4(f.yaw)]]})
    add(f"{name} pinnacles", {"type": "pinnacle", "w": 0.8, "h": 2.2, "s": 1.8, "sides": 8, "at": [f.place(along + d * (rw / 2 + 0.05), out - 0.35, top) for d in (-1, 1)]})
risalit("west", 0.0, 13.0, 1.4, "west risalit"); risalit("south", 0.0, 11.0, 1.2, "south risalit", gh=6.0)

# ---- the towers: one tower of stages (components/stage-tower), differing by its numbers
def tower(name, x, y, **kw):
    a, b = pt(x, y); add(name, comp("components/stage-tower", kw, [[r4(a), 0, r4(b), 0]], _about=kw.pop("_about", "a round tower of stages")))
tower("town tower north", -8, 86, R=4.7, H=24.5, Ru=4.0, Hu=6.5, tent=6.5, Lr=1.05, Lh=2.6, tip=1.8, _about="the town front's north tower: round, its upper stage set back, four gablets and corner turrets at the tent's foot, an open lantern")
tower("town tower south", -26, 69.5, R=4.7, H=24.5, Ru=4.0, Hu=6.5, tent=6.5, Lr=1.05, Lh=2.6, tip=1.8, _about="the town front's other tower")
tower("west tower", -35, 21, R=6.0, H=23.5, Ru=4.2, Hu=5.0, tent=6.5, Lr=1.0, Lh=2.2, tip=2.2, _about="the corner tower at the west wing's far end, OSM's r 6 foot and r 4 upper stage")
tower("south tower", 4, -6, R=5.8, H=23.0, Ru=4.0, Hu=5.0, tent=6.5, Lr=1.0, Lh=2.2, tip=2.2, _about="the south corner tower, between the south and south-east wings")
tower("great tower", 44.5, 28, R=6.5, H=33.0, Ru=5.3, Hu=3.6, tent=9.0, Lr=1.3, Lh=2.8, tip=2.6, storeys=7, turrets=1, _about="the great round tower over the Burggarten: the castle's tallest, OSM's 50 m, a keep's shaft with a ring of little turrets at its head")
for nm, x, y, h, r in (("north turret", 41.5, 76, 26, 2.5), ("chapel turret", 50.5, 62.5, 22, 2.5), ("court turret", 8.5, 17.5, 21.5, 2.6)):
    tower(nm, x, y, R=r, H=h, Ru=r * 0.82, Hu=2.2, tent=4.5, Lr=0.55, Lh=1.3, tip=1.4, storeys=5, _about="a slender round turret: OSM's r 2.5, a stair's")

# ---- the two domed towers, on the court's corners: gold over the town front, copper over the west
def dome_tower(name, x, y, R, H, drumR, drumH, capRise, kok, gold):
    a, b = pt(x, y)
    add(name, comp("components/domed-tower", {"sides": 16, "R": R, "H": H, "t": 0.9, "drumR": drumR, "drumH": drumH, "cap": "bell", "bulge": 1.0, "neck": 0.9, "waist": 0.86, "lift": 1.0, "capR": drumR * 1.04, "capRise": capRise,
                                              "kok": kok, "finial": 0.1, "doorH": 3.6, "winW": 1.3, "capRibs": 24}, [[r4(a), 0, r4(b), 0]], build=["tower", "head", "neck", "drum", "cornice", "cap"],
                   _about=f"{gold}: a round tower on the court's corner, its drum and its dome"))
    return a, b, H + kok + drumH + capRise
gx, gz, gt = dome_tower("gold tower", -4, 65, 5.0, 28.0, 4.2, 6.6, 4.4, 0.8, "the gilded dome over the town front")
cx_, cz_, ct = dome_tower("copper tower", -14, 30.5, 6.5, 24.0, 4.4, 3.2, 4.4, 0.6, "the green copper dome over the west wing, OSM's r 7 foot")
for nm, a, b, top, R, H, cap in (("gold lantern", gx, gz, gt - 0.5, 1.1, 2.4, 1.3), ("copper lantern", cx_, cz_, ct - 0.4, 0.9, 1.9, 1.0)):
    add(nm, comp("components/stage-tower", {"H": r4(top - 0.7), "Hu": 0, "tent": 0, "Lr": R, "Lh": H, "tip": 1.8}, [[r4(a), 0, r4(b), 0]], build=["lantern", "lantern cap", "spike"], _about="its lantern, open, a little dome and a spike on it"))
add("gold figure", {"type": "pinnacle", "w": 0.5, "h": 0.5, "s": 0.8, "sides": 8, "figure": 2.0, "at": [[r4(gx), r4(gt + 4.1), r4(gz), 0]], "_about": "the gilt figure on the lantern (a turned silhouette at this height)"})

# ---- the town front (heights read off the photograph straight on, scaled by the 25 m between the tower centres): the arcaded loggia to 9.5 m under its balustrade, three arched
# lights over the gate, the great arched niche with Niklot from 18.5 m and a lesser arch either side, the block's crown before the gold drum
fr = FACE["front"]; PW, PH, OUT = 11.0, 26.5, 2.4
T1, T2, T3 = 9.6, 8.9, PH - 9.6 - 8.9
arch_ = lambda at, w, sill, spring, glass=False: {"at": at, "width": w, "sill": sill, "springing": spring, "head": {"profile": "semicircular"}, "glass": glass}
add("portal block", {"type": "enclosure", "plan": {"rect": [PW, OUT * 2]}, "thickness": 0.8, "height": PH, "glass": True,
                     "tiers": [{"h": T1, "openings": []}, {"h": T2, "openings": []}, {"openings": []}],
                     "faces": {"0": [{"h": T1, "openings": [arch_(0, 4.2, 0, 3.6)]},
                                     {"h": T2, "openings": [arch_(s, 1.05, 2.8, 5.3, True) for s in (-1.35, 0, 1.35)] + [arch_(s, 1.0, 2.8, 5.0) for s in (-3.9, 3.9)]},
                                     {"openings": [arch_(0, 3.8, 0.2, 4.9)] + [arch_(s, 1.5, 1.6, 4.2) for s in (-3.7, 3.7)]}]},
                     "at": [fr.place(0, 0.0, 0.0)], "_about": "the portal block standing forward of the town front: the gate, the three arched lights between two statue niches, the great arched niche with a lesser one either side"})
add("niche back", {"type": "box", "width": PW - 1.0, "length": 0.4, "height": T3, "at": [fr.place(0, 0.3, T1 + T2)], "_about": "the niches' back wall, dark in the finish (Niklot stands before it)"})
a, b = fr.at(0, 1.2)
add("niche floor", {"type": "box", "width": PW - 1.0, "length": 2.2, "height": 0.25, "flatRoof": True, "at": [[r4(a), T1 + T2, r4(b), r4(fr.yaw)]]})
add("niklot plinth", {"type": "box", "width": 1.6, "length": 1.6, "height": 1.0, "at": [[r4(a), T1 + T2 + 0.25, r4(b), r4(fr.yaw)]], "_about": "the plinth of Niklot's statue (the real one is on horseback)"})
add("niklot", {"type": "marker", "role": "statue", "at": [[r4(a), T1 + T2 + 1.25, r4(b), 0]],
               "data": {"kind": "man", "pose": "guard", "style": "gothic", "stone": "bronze", "scale": 1.5, "face": r4(fr.yaw - math.pi / 2), "seed": 7}, "_about": "Niklot (standing: the engine has no horseman yet)"})
add("portal crown", {"type": "screen", "outline": [[-PW / 2, 0], [PW / 2, 0], [PW / 2, 1.2], [3.4, 1.2], [2.8, 3.0], [1.1, 3.0], [0, 4.4], [-1.1, 3.0], [-2.8, 3.0], [-3.4, 1.2], [-PW / 2, 1.2]], "t": 1.0, "at": [fr.place(0, OUT, PH)], "_about": "the block's crown, a shaped gable before the gold drum"})
add("portal roof", {"type": "prism", "plan": {"rect": [PW - 1.6, OUT * 2 - 1.6]}, "height": 0.3, "flatRoof": True, "at": [fr.place(0, 0.0, PH - 0.3)]})
# (the loggia runs across the whole front, past the towers' middles: a wide gate arch, two narrower either side, one in each return, under a balustrade)
LD, LW, LH = 8.0, 27.0, 9.0
add("loggia", {"type": "enclosure", "plan": {"rect": [LW, LD]}, "thickness": 0.9, "height": LH, "glass": False, "tiers": [{"openings": []}], "interior": True,
               "faces": {"0": [{"openings": [arch_(0, 4.8, 0, 4.4)] + [arch_(s, 2.6, 0, 3.8) for s in (-5.2, 5.2, -9.8, 9.8)]}], "1": [{"openings": [arch_(0, 2.6, 0, 3.8)]}], "3": [{"openings": [arch_(0, 2.6, 0, 3.8)]}]},
               "at": [fr.place(0, LD / 2 - 0.1, 0.0)], "_about": "the arcaded porch before the gate, as in the photographs"})
add("loggia floor", {"type": "prism", "plan": {"rect": [LW + 0.5, LD + 0.5]}, "height": 0.5, "flatRoof": True, "at": [fr.place(0, LD / 2 - 0.1, LH)]})
hw = (LW + 0.2) / 2
add("loggia balustrade", {"type": "cresting", "run": [[-hw, 0], [hw, 0]], "h": 1.0, "panel": 1.1, "t": 0.22, "bar": 0.1, "at": [fr.place(0, LD + 0.1, LH + 0.5)]})

# ---- the chapel on the north-east corner (the Renaissance Schlosskirche, 1560-63, its choir of 1855): a Gothic body and a three-sided choir
c0 = pt(51.5, 62); dirx = (FACE["link"].n[0], FACE["link"].n[1]); CL, CW, CH = 13.0, 8.6, 14.5
ca = math.atan2(FACE["link"].n[0], FACE["link"].n[1])
goth = {"profile": "pointed"}
add("chapel", {"type": "enclosure", "plan": {"points": [[-CW / 2, -CL / 2], [CW / 2, -CL / 2], [CW / 2, CL / 2 - 3.2], [CW * 0.27, CL / 2], [-CW * 0.27, CL / 2], [-CW / 2, CL / 2 - 3.2]]}, "thickness": 0.8, "height": CH, "glass": True,
               "openings": {"pattern": "1", "width": 1.8, "gap": 0.6, "sill": 3.2, "springing": 9.0, "head": goth},
               "at": [[r4(c0[0]), 0, r4(c0[1]), r4(ca)]], "_about": "the castle chapel: its Gothic choir, tall pointed windows, three-sided, standing out of the ring by the great gables"})
add("chapel roof", {"type": "roof", "form": "hip", "width": CW + 0.4, "length": CL + 0.2, "pitch": 66, "overhang": 0.2, "at": [[r4(c0[0]), CH, r4(c0[1]), r4(ca)]]})
add("chapel pinnacles", {"type": "pinnacle", "w": 0.7, "h": 3.2, "s": 2.6, "sides": 4, "at": [[r4(c0[0] + math.cos(ca) * sx - (-math.sin(ca)) * 0 + math.sin(ca) * sz), CH, r4(c0[1] - math.sin(ca) * sx + math.cos(ca) * sz), 0] for sx, sz in ((-CW / 2, CL / 2 - 3.2), (CW / 2, CL / 2 - 3.2), (CW * 0.27, CL / 2), (-CW * 0.27, CL / 2))]})

# ---- chimneys (the roofs bristle with them)
chim = []
for w, alongs in (("west", (-8.5, 8.5)), ("south", (-6.5, 6.5)), ("southeast", (-13.0, 6.0)), ("north", (-17.5, 0.5, 18.5)), ("east", (-5.5, 5.5))):
    f = FACE[w]
    for s in alongs: a, b = f.at(s, -f.d * 0.42); chim.append([r4(a), f.eave + 3.0, r4(b), r4(f.yaw)])
add("chimneys", {"type": "box", "width": 1.3, "length": 0.9, "height": 7.0, "at": chim, "_about": "the tall stacks along the ridges"})

# ---- the island's terrace, the forecourt and the bridge (three arches over the water, its tall lamp columns)
xs = [p[0] for p in O]; zs = [p[1] for p in O]
HX = max(abs(v) for v in xs) + 12; HZ = max(abs(max(zs)) + 9, abs(min(zs)) + FORE)
MOAT_W = 22.0
fx, fz = fr.m
fe = min(zs) - FORE + 0.0
FW = 28.0
fb = -HZ
add("forecourt balustrade", {"type": "cresting", "run": [[-FW / 2, 0], [-5, 0]], "h": 1.1, "panel": 1.2, "t": 0.3, "bar": 0.12, "at": [[r4(fx), 0, r4(fb + 0.8), 0]], "_about": "the forecourt's balustrade either side of the bridge"})
add("forecourt balustrade east", {"type": "cresting", "run": [[5, 0], [FW / 2, 0]], "h": 1.1, "panel": 1.2, "t": 0.3, "bar": 0.12, "at": [[r4(fx), 0, r4(fb + 0.8), 0]]})
add("lodge", comp("components/stage-tower", {"R": 1.9, "H": 4.2, "Ru": 1.5, "Hu": 0.8, "tent": 2.0, "Lr": 0.3, "Lh": 0.5, "tip": 0.6, "storeys": 2}, [[r4(fx + s * FW / 2), 0, r4(fb + 2.6), 0] for s in (-1, 1)], _about="the forecourt's two round lodges (`h` on the old plan)"))
BL = MOAT_W + 3.0
add("bridge", comp("components/bridge", {"L": BL, "W": 10, "depth": 5.0, "n": 3}, [[r4(fx), 0, r4(fb + 1.5), math.pi]], _about="the Schlossbrücke to the forecourt, on the portal's axis"))
lamps = [[r4(fx + s * 4.3), 1.0, r4(fb - k * 7.5 + 1.0), 0] for s in (-1, 1) for k in range(0, 4)]
add("bridge lamps", {"type": "column", "radius": 0.28, "height": 5.2, "sides": 8, "at": lamps, "_about": "the tall candelabra along the bridge"})
add("bridge lanterns", {"type": "prism", "plan": {"sides": 6, "radius": 0.55}, "height": 1.0, "at": [[a, 6.2, b, c] for a, y, b, c in lamps]})
add("bridge steps", {"type": "flight", "width": 8, "run": 0.32, "rise": 0.15, "top": 0, "base": -0.6, "landing": 0,
                     "at": [[r4(fx - 4), 0, r4(fb + 1.5 - BL - 4 * 0.32), -1.5707963]], "_about": "down from the deck to the shore"})

doc = {"name": "Schloss Schwerin",
       "_about": "SCHLOSS SCHWERIN on its island, on its real irregular plan (OpenStreetMap): a `court` of seven faces and differing depths, one ring of rooms; a fifth storey and a French mansard over the town, west and south wings; red stepped gables over the east wing, plain ones over the north; stage towers on the ring's corners, the great round tower over the Burggarten the tallest; the gilded and the copper domes on the court's corners; the portal block with its loggia and Niklot's niche; the chapel's Gothic choir; the forecourt and the bridge. The lake is carved round the island by the game.",
       "params": {"detail": 4}, "base": {"height": 0.6, "steps": 2, "stepOut": 0.5, "plan": {"rect": [r4(2 * HX), r4(2 * HZ)]}},
       "_moat": {"hw": round(HX + 0.5, 2), "hd": round(HZ + 0.5, 2), "w": MOAT_W},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/schwerin.json"), "w").write(json.dumps(doc, indent=2) + "\n")

# ---- the stage tower, a shared part: round, its shaft in storeys under belt courses, a corbelled cornice, an upper stage set back, a slate tent with gablets and little corner
# turrets at its foot, an open lantern with a small cap and a spike
wins = lambda: {str(k): None for k in range(16)}
SHAFT = 6
def shaft_faces(n):
    t = {}
    for k in range(16):
        opens = k % 2 == 1
        t[str(k)] = [{"h": f"H / {n}", "openings": [{"at": 0, "width": "R * 0.2", "sill": "H / {0} * 0.25".format(n), "springing": "H / {0} * 0.72".format(n), "head": {"profile": "segmental", "seg": 0.35}}] if opens and j > 0 else
                      ([{"at": 0, "width": "R * 0.3", "sill": 0, "springing": "H / {0} * 0.55".format(n), "head": {"profile": "semicircular"}, "glass": False}] if k == 1 and j == 0 else [])} for j in range(n - 1)] + \
               [{"openings": [{"at": 0, "width": "R * 0.2", "sill": "H / {0} * 0.25".format(n), "springing": "H / {0} * 0.72".format(n), "head": {"profile": "segmental", "seg": 0.35}}] if opens else []}]
    return t
ring_ = lambda r, y, h: {"type": "prism", "plan": {"sides": 16, "radius": r}, "height": h, "flatRoof": True, "at": [[0, y, 0, 0]]}
stage = {"name": "Stage tower",
         "_about": "A ROUND TOWER OF STAGES (Schwerin's, and Chambord's before it): a shaft in `storeys` under belt courses, a corbelled cornice at `H`, an upper stage `Ru` wide and `Hu` tall set back behind it, the tent `tent` tall with four gablets and four little octagonal turrets at its foot, an open lantern `Lr` wide, `Lh` tall, with a small cap and a spike `tip`. `turrets` 1 puts a ring of eight small turrets round the cornice's head, a keep's.",
         "params": {"detail": 4, "R": 6, "H": 25, "Ru": 5, "Hu": 5, "tent": 8, "Lr": 1.1, "Lh": 2.4, "tip": 2.2, "storeys": 6, "turrets": 0, "t": "max(0.3, R * 0.14)"},
         "build": ["shaft", "belts", "corbels", "cornice", "upper", "upper belt", "head", "gablets", "turrets", "tent", "lantern", "lantern cap", "spike"] ,
         "parts": {
             "shaft": {"type": "enclosure", "plan": {"sides": 16, "radius": "R"}, "thickness": "t", "height": "H", "glass": True, "interior": True,
                       "tiers": [{"h": "H / storeys", "openings": []}, {"openings": []}], "faces": shaft_faces(SHAFT), "at": [[0, 0, 0, 0]]},
             "belts": {"type": "prism", "plan": {"sides": 16, "radius": "R + 0.1"}, "height": 0.28, "flatRoof": True, "at": [[0, "H / storeys - 0.14", 0, 0]], "repeat": {"count": "storeys - 1", "step": [0, "H / storeys", 0, 0]}},
             "corbels": {"type": "prism", "plan": {"sides": 16, "radius": "R + 0.22"}, "height": 0.5, "flatRoof": True, "at": [[0, "H - 0.5", 0, 0]]},
             "cornice": {"type": "prism", "plan": {"sides": 16, "radius": "R + 0.42"}, "height": 0.45, "flatRoof": True, "at": [[0, "H", 0, 0]]},
             "upper": {"type": "enclosure", "plan": {"sides": 16, "radius": "Ru"}, "thickness": "t * 0.7", "height": "Hu", "glass": True, "interior": True, "at": [[0, "H + 0.45", 0, 0]],
                       "openings": {"pattern": "1", "width": "Ru * 0.17", "gap": 0.05, "sill": "Hu * 0.25", "springing": "Hu * 0.68", "head": {"profile": "semicircular"}}},
             "upper belt": {"type": "prism", "plan": {"sides": 16, "radius": "Ru + 0.25"}, "height": 0.35, "flatRoof": True, "at": [[0, "H + 0.45 + Hu - 0.05", 0, 0]]},
             "head": {"type": "prism", "plan": {"sides": 16, "radius": "Ru - 0.1"}, "height": 0.2, "flatRoof": True, "at": [[0, "H + 0.45 + Hu - 0.2", 0, 0]]},
             "gablets": {"type": "roof", "form": "gable", "width": "Ru * 0.8", "length": "Ru * 0.5", "pitch": 62, "overhang": 0.05, "spiral": {"count": 4, "radius": "Ru * 0.82", "y": "H + 0.45 + Hu + 0.3", "turn": 0.7853982}},
             "turrets": {"type": "pinnacle", "w": "Ru * 0.26", "h": "Hu * 0.55", "s": "Hu * 0.5", "sides": 8, "spiral": {"count": 4, "radius": "Ru + 0.05", "y": "H + 0.45"}},
             "tent": comp("components/gothic-spire", {"sides": 16, "R": "Ru + 0.1", "rise": "tent / (1 - Lr * 0.8 / (Ru + 0.1))", "topR": "Lr * 0.8", "finial": 0}, [[0, "H + 0.8 + Hu", 0, 0]], build=["spire"]),
             "lantern": {"type": "enclosure", "plan": {"sides": 8, "radius": "Lr"}, "thickness": "Lr * 0.22", "height": "Lh", "glass": False, "at": [[0, "H + 0.8 + Hu + tent - 0.1", 0, 0]],
                         "openings": {"pattern": "1", "width": "Lr * 0.45", "gap": 0.02, "sill": "Lh * 0.2", "springing": "Lh * 0.62", "head": {"profile": "semicircular"}}},
             "lantern cap": {"type": "dome", "radius": "Lr * 1.1", "thickness": 0, "head": {"profile": "bell", "waist": 0.7, "lift": 1.0, "rise": "Lr * 1.25"}, "at": [[0, "H + 0.8 + Hu + tent + Lh - 0.1", 0, 0]], "sides": 8},
             "spike": {"type": "column", "radius": "max(Lr * 0.08, 0.05)", "height": "tip", "sides": 6, "at": [[0, "H + 0.8 + Hu + tent + Lh + Lr * 1.25 - 0.3", 0, 0]]}}}
open(os.path.join(ROOT, "assets/architecture/components/stage-tower.json"), "w").write(json.dumps(stage, indent=2) + "\n")
print("moat", doc["_moat"], "parts", len(parts))
# the east and link wings' fronts are the old castle's red brick and terracotta: where on the plan (for the finish's `within`)
ew = [FACE["east"].p, FACE["east"].q, FACE["link"].p, FACE["link"].q]
lb = [fr.at(sa * LW / 2, sb) for sa in (-1, 1) for sb in (0, LD)]
print("loggia within", [round(min(a for a, _ in lb), 1), round(min(b for _, b in lb), 1), round(max(a for a, _ in lb), 1), round(max(b for _, b in lb), 1)])
print("brick within", [round(min(a for a, _ in ew) - 1, 1), round(min(b for _, b in ew) - 1, 1), round(max(a for a, _ in ew) + 1, 1), round(max(b for _, b in ew) + 1, 1)], [r4(v) for v in FACE["east"].m])
