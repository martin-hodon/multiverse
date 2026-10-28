# ST BASIL'S CATHEDRAL (the Cathedral of the Intercession on the Moat, Moscow, 1555-61), from the
# `domed-tower` component: nine chapels on one platform, and the belfry beside them -- and RED SQUARE round it, on its
# real plan (OpenStreetMap, in metres east and north of the central tower): the KREMLIN WALL along the square's west
# side from the Konstantino-Eleninskaya tower by the slope to the river, past the Nabatnaya and the little Tsarskaya on
# the wall, to the SPASSKAYA, the gate tower, and on north-west to the Senate tower; Lenin's MAUSOLEUM before the wall,
# and the LOBNOYE MESTO, the round stone tribune, before the cathedral.
#   The cathedral's own frame: x east, z south; the chapels on the axes, the stair up from the square on the north,
#   the belfry against the gallery on the east.
#   The Kremlin's TOWERS are `kremlin-tower`s: a square body, the corbel band and the forked merlons of the walls
#   (Milanese masters built them), and on the deck a square tier, the open octagon and the tent -- or fewer of these;
#   the SPASSKAYA's body and its barbican are the same component built as gates (`gate`), and on it Christopher Galloway's
#   tiers of 1625 (`gothic-tower-stage` twice, a `gothic-octagon-stage`) under the tent and its star.
#   The WALL is a `curtain-wall` between each pair of towers, from the face of one to the face of the next, its
#   battlements toward the square.
import os, json, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapes import tent_y_at
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
tower = lambda **params: {"type": "component", "use": "components/domed-tower", "params": params}
add("platform", {"type": "prism", "plan": {"rect": [46, 46], "chamfer": 9}, "height": "podklet", "at": [[0, 0, 0, 0]],
                 "_about": "the podklet: the vaulted basement all nine churches stand on"})
arcade = lambda n: {"pattern": str(n), "width": 1.6, "gap": 1.2, "pier": 1.2, "sill": 0.9, "springing": 2.6, "head": {"profile": "semicircular"}}
add("gallery", {"type": "enclosure", "plan": {"rect": [44, 44], "chamfer": 8.5, "split": {"main": [2, 1, 2]}}, "thickness": 0.7, "height": 4.2,
                "faces": {"main:0": arcade(3), "main:2": arcade(3), "chamfer": arcade(2),
                          "main:1": [{"at": 0, "width": 2.4, "sill": 0, "springing": 2.8, "head": {"profile": "semicircular"}}]},
                "at": [[0, "podklet", 0, 0]], "_about": "the gallery that runs round the platform and joins the chapels: arcaded, with a door in the middle of each side (the plan's `split`)"})
add("stairs", {"type": "flight", "width": 3.0, "run": 0.3, "rise": 0.17, "top": "podklet", "landing": 0,
               "at": [[-1.5, 0, -(23 + 32 * 0.3), -1.5707963]], "_about": "the flight up to the platform from Red Square, on the north"})
# the central tower: a tall tent, and a small domed tower on its tip
add("central tower", {**tower(sides=8, R=5.5, H=17, cap="trigonal", capRise=15, drumR=4.0, drumH=3.2, capR=4.3, finial=0.1),
                      "build": ["tower", "kokoshniki", "neck", "drum", "cap"], "at": [[0, "podklet", 0, 0]],
                      "_about": "the Intercession: the central tower, its tent roof 15m high"})
add("central lantern", {**tower(sides=8, R=1.3, H=2.4, drumR=0.9, drumH=1.0, bulge=1.45, neck=0.8, capR=1.15, finial=1.4),
                        "build": ["tower", "drum", "cap", "cap ribs", "finial"], "at": [[0, f"podklet + {17 + 5.5 * 0.5 + 3.2 + tent_y_at(4.3, 15, 1.3):.4f}", 0, 0]],
                        "_about": "the small onion on the tent's tip: the same component at a quarter the size, set where the tent is its width (tools/archgen/shapes.py)"})
# four big chapels on the axes, four smaller ones on the diagonals
# ...each its own part, so each can have its own colours: no two of St Basil's onions are alike
axial = [("north", [0, "podklet", -15.5, 3.14159265]), ("east", [15.5, "podklet", 0, 1.5707963]), ("south", [0, "podklet", 15.5, 0]), ("west", [-15.5, "podklet", 0, -1.5707963])]
for nm, at in axial:
    add(f"{nm} chapel", {**tower(sides=8, R=4.0, H=15, drumR=2.7, drumH=3.0, bulge=1.4, neck=0.85, capR=3.0, finial=2.2, capRibs=16),
                         "build": ["tower", "kokoshniki", "neck", "drum", "cap", "cap ribs", "finial"], "at": [at],
                         "_about": f"the {nm} chapel on the axis, an octagon with its drum and a ribbed onion"})
for nm, (sx, sz) in (("northeast", (1, 1)), ("southeast", (1, -1)), ("southwest", (-1, -1)), ("northwest", (-1, 1))):
    add(f"{nm} chapel", {**tower(sides=8, R=2.7, H=10.5, drumR=1.9, drumH=2.4, bulge=1.35, neck=0.9, capR=2.1, finial=1.6, capRibs=12),
                         "build": ["tower", "kokoshniki", "neck", "drum", "cap", "cap ribs", "finial"], "at": [[sx * 11.2, "podklet", -sz * 11.2, 0]],
                         "_about": f"the smaller {nm} chapel on the diagonal"})
BX, BZ = 27.0, 2.0                       # the belfry (1680s), on the east
add("belfry", {**tower(sides=8, R=3.2, H=14, cap="trigonal", capRise=8, drumR=2.4, drumH=3.5, capR=2.6, finial=0.1, glazed=0),
               "build": ["tower", "neck", "drum", "cap"], "at": [[BX, 0, BZ, 0]], "_about": "the belfry, against the gallery on the east: an octagon with an open drum and a tent"})
add("belfry onion", {**tower(sides=8, R=0.9, H=1.4, drumR=0.6, drumH=0.8, bulge=1.3, capR=0.75, finial=1.0),
                     "build": ["tower", "drum", "cap", "finial"], "at": [[BX, round(14 + 3.2 * 0.5 + 3.5 + tent_y_at(2.6, 8, 0.9), 4), BZ, 0]]})

# ---- RED SQUARE and the KREMLIN ------------------------------------------------------------------------------------
r4 = lambda v: round(v, 4)
K = lambda E, N: (E + 4.7, -(N + 2.8))                 # OSM metres (east, north of the middle of the platform) -> (x, z)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
def yaw_along(a, b):
    """the turn that lays a part's +x from OSM point a toward b (its +z then to the right: the square's side)"""
    return math.atan2(b[1] - a[1], b[0] - a[0])
def at(E, N, y, yaw):
    x, z = K(E, N); return [r4(x), r4(y), r4(z), r4(yaw)]

HW, TW = 11.0, 4.5                                     # the wall: its walk's height, its thickness
# the towers along the wall from the south, their middles (OSM), each turned square to the wall (its +z to the square)
KE, NAB, TSAR, SPA, SEN = (-48.25, -148.4), (-78.35, -76.35), (-97.1, -28.9), (-110.5, 2.5), (-221.6, 110.9)
SPA_AX = math.radians(40.4)                            # the Spasskaya's passage: from the Kremlin out north-east to the square
TOWERS = {  # name: (middle, yaw, half its body's width)
    "konstantino-eleninskaya": (KE, yaw_along(KE, NAB), 7.75),
    "nabatnaya": (NAB, yaw_along(NAB, TSAR), 4.9),
    "spasskaya": (SPA, SPA_AX + math.pi / 2, 7.0),
    "senate": (SEN, yaw_along(SPA, SEN), 4.5),
}
KT = "components/kremlin-tower"
def ktower(name, H, W, build, **kw):
    c, yaw, _ = TOWERS[name]
    add(f"{name} tower", comp(KT, {"W": W, "H": H, **kw}, [at(*c, 0, yaw)], build=build))
ktower("konstantino-eleninskaya", 20.0, 15.5, ["body", "corbel band", "battlements", "deck", "tier", "tier slab", "octagon", "octagon slab", "tent"],
       cw=9.0, ch=5.0, oR=4.2, oH=4.0, rise=9.0)
parts["konstantino-eleninskaya tower"]["_about"] = "the Konstantino-Eleninskaya tower (1490), over the slope down to the river: its body, the tier, the octagon and the tent"
ktower("nabatnaya", 19.0, 9.8, ["body", "corbel band", "battlements", "deck", "tier", "tier slab", "octagon", "octagon slab", "tent"],
       cw=6.2, ch=4.5, oR=2.9, oH=4.0, rise=10.0)
parts["nabatnaya tower"]["_about"] = "the Nabatnaya, the alarm tower (1495; its tent 1676), where the alarm bell hung"
ktower("senate", 20.0, 9.0, ["body", "corbel band", "battlements", "deck", "tent"], ch=0, oH=0, tR=3.4, rise=12.0)
parts["senate tower"]["_about"] = "the Senate tower (1491) behind the mausoleum: its body and a plain stone tent straight on the deck"
# the SPASSKAYA: the gate tower's body and, before it toward the square, its barbican (the strelnitsa) -- both gates, the
# passage straight through -- and on the body Galloway's tiers, the octagon, the tent and the star
c, yaw, _ = TOWERS["spasskaya"]
GATE = ["body gate", "corbel band", "battlements", "deck"]       # (with gate "yes")
add("spasskaya tower", comp(KT, {"W": 14.0, "H": 26.0, "gate": "yes", "doorW": 4.2, "doorSpring": 6.0}, [at(*c, 0, yaw)], build=GATE,
                            _about="the Spasskaya, the Saviour's gate (1491): the body, the passage through it from the Kremlin to the square..."))
bc = (c[0] + 12.5 * math.cos(SPA_AX), c[1] + 12.5 * math.sin(SPA_AX))
add("spasskaya barbican", comp(KT, {"W": 11.0, "H": 12.0, "gate": "yes", "doorW": 4.2, "doorSpring": 5.0}, [at(*bc, 0, yaw)], build=GATE,
                               _about="...its barbican before it on the square, the passage carried on through..."))
st = lambda **kw: {"t": 1.0, "wins": 1, "winW": 1.8, "bw": 1.1, "bd": 0.9, **kw}
add("spasskaya tier", comp("components/gothic-tower-stage", st(W=10.5, H=9.0, low=2.4, pinW=1.0, pinH=3.0, pinS=3.2), [at(*c, 26.0, yaw)],
                           build=["walls", "corner pinnacles", "slab"], _about="...Galloway's tiers on the body (1625): the clock storey, pinnacles on its corners..."))
add("spasskaya upper tier", comp("components/gothic-tower-stage", st(W=8.2, H=6.5, t=0.8, low=1.6, winW=1.5, pinW=0.8, pinH=2.2, pinS=2.6), [at(*c, 35.0, yaw)],
                                 build=["walls", "corner pinnacles", "slab"], _about="...the arcaded storey over it..."))
add("spasskaya octagon", comp("components/gothic-octagon-stage", {"R": 4.0, "H": 6.5, "t": 0.6, "low": 1.2}, [at(*c, 41.5, yaw)],
                              build=["walls", "slab"], _about="...the open octagon, the bells..."))
add("spasskaya tent", comp("components/gothic-spire", {"R": 3.7, "rise": 19.0, "finial": 3.0}, [at(*c, 48.0, yaw)],
                           build=["spire", "ribs", "finial"], _about="...and the tent, its star 71m over the square"))

# the WALL: a stretch between each pair of towers, from face to face (the Tsarskaya stands on the stretch under it)
def face_point(tw, toward):
    """where the line from a tower's middle toward a point leaves its body, a little inside (so the stretch runs into it)"""
    (cx, cn), yaw, h = tw
    d = (toward[0] - cx, toward[1] - cn); l = math.hypot(*d); d = (d[0] / l, d[1] / l)
    ux, uz = (math.cos(yaw), math.sin(yaw)), (math.sin(yaw), -math.cos(yaw))
    t = min(h / max(1e-9, abs(d[0] * u[0] + d[1] * u[1])) for u in (ux, uz)) - 0.8
    return (cx + d[0] * t, cn + d[1] * t)
CW = "components/curtain-wall"
for a, b in (("konstantino-eleninskaya", "nabatnaya"), ("nabatnaya", "spasskaya"), ("spasskaya", "senate")):
    p, q = face_point(TOWERS[a], TOWERS[b][0]), face_point(TOWERS[b], TOWERS[a][0])
    add(f"wall {a} to {b}", comp(CW, {"L": r4(math.hypot(q[0] - p[0], q[1] - p[1])), "T": TW, "H": HW},
                                 [at((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, 0, yaw_along(p, q))],
                                 _about=f"the Kremlin wall from the {a} tower to the {b}: its walk behind the swallowtail merlons"))

# the TSARSKAYA: no tower but a pavilion on the wall's walk -- four piers and their arches under a tent (1680)
add("tsarskaya tower", comp(KT, {"W": 4.6, "H": 0, "cw": 4.6, "ch": 3.0, "ct": 0.45, "cwin": 3.0, "csill": 0, "tierIn": 0, "oH": 0, "tR": 2.9, "rise": 5.0, "finial": 1.0},
                            [at(*TSAR, HW, TOWERS["nabatnaya"][1])], build=["tier", "tier slab", "tent"],
                            _about="the Tsarskaya, the tsar's tower: a little open pavilion on the wall's walk, its tent on four arches, where the tsar watched the square"))

# LENIN'S MAUSOLEUM (Shchusev, 1930) before the Senate tower: red granite in steps up to the colonnade on its top, the
# tribunes either side; square to the wall, its front to the square
MC, MY = (-204.3, 132.4), yaw_along(SPA, SEN)
steps = [(24.0, 16.0, 0.0, 3.6), (20.0, 13.0, 3.6, 1.8), (16.0, 10.0, 5.4, 1.8), (12.0, 8.0, 7.2, 1.6)]
add("mausoleum", {"type": "prism", "plan": {"rect": [steps[0][0], steps[0][1]]}, "height": steps[0][3], "at": [at(*MC, 0, MY)],
                  "_about": "Lenin's mausoleum (1930): the granite base, its door toward the square..."})
for i, (w, d, y, h) in enumerate(steps[1:], 2):
    add(f"mausoleum step {i}", {"type": "prism", "plan": {"rect": [w, d]}, "height": h, "at": [at(*MC, y, MY)]})
add("mausoleum colonnade", {"type": "enclosure", "plan": {"rect": [10.0, 6.0]}, "thickness": 0.5, "height": 2.6, "glass": False,
                            "openings": {"every": 1.6, "width": 1.0, "end": 0.8, "sill": 0, "springing": 2.6, "head": {"profile": "flat"}},
                            "at": [at(*MC, 8.8, MY)], "_about": "...the square piers of the colonnade on its top..."})
add("mausoleum top", {"type": "box", "width": 10.6, "length": 6.6, "height": 0.5, "at": [at(*MC, 11.4, MY)], "flatRoof": True,
                      "_about": "...and the slab over them"})
side = lambda s: (MC[0] + s * 17.0 * math.cos(MY), MC[1] + s * 17.0 * math.sin(MY))
add("mausoleum tribunes", {"type": "prism", "plan": {"rect": [10.0, 9.0]}, "height": 2.4, "at": [at(*side(-1), 0, MY), at(*side(1), 0, MY)],
                           "_about": "the tribunes either side, low along the wall"})

# the LOBNOYE MESTO (1534, rebuilt 1786): the round stone tribune before the cathedral, its stair from the south-west
LC, LR, LH = (-36.9, 81.2), 6.0, 1.6
add("lobnoye mesto", {"type": "prism", "plan": {"sides": 24, "radius": LR}, "height": LH, "walked": True, "at": [at(*LC, 0, 0)],
                      "_about": "the Lobnoye Mesto, the round tribune where the tsars' decrees were read"})
ld = (math.cos(math.radians(50.6)), math.sin(math.radians(50.6)))   # the stair climbs north-east, to the middle
n = round(LH / 0.16); FL, FWD = n * 0.32, 2.4
foot = (LC[0] - ld[0] * (LR - 0.3 + FL) + ld[1] * FWD / 2, LC[1] - ld[1] * (LR - 0.3 + FL) - ld[0] * FWD / 2)
add("lobnoye mesto stair", {"type": "flight", "width": FWD, "run": 0.32, "rise": r4(LH / n), "top": LH, "base": 0, "landing": 0,
                            "at": [at(*foot, 0, math.radians(50.6))]})

doc = {"name": "St Basil's Cathedral",
  "_about": "ST BASIL'S CATHEDRAL, Moscow (1555-61), from ONE component -- `domed-tower` -- used at five sizes: on its platform and gallery, the central tower of the Intercession with its tall tent and a small onion on the tip; four great chapels on the axes, each an octagon with a drum and a ribbed onion; four smaller ones on the diagonals; and the belfry standing apart with its own tent. Nothing here is drawn once for this building alone except the platform, the gallery and the stair. Round it Red Square on its real plan: the Kremlin wall along the west side (`curtain-wall`, the forked merlons) from the Konstantino-Eleninskaya tower past the Nabatnaya and the little Tsarskaya to the Spasskaya gate and on to the Senate tower (`kremlin-tower`; on the Spasskaya Galloway's Gothic tiers and the tent with its star), Lenin's mausoleum before the wall, the Lobnoye Mesto before the cathedral. Generated by tools/archgen/st_basil.py -- edit the script for arithmetic changes. East is +x, south +z.",
  "params": {"detail": 4, "podklet": 5.5}, "railing": {"type": "stone"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/st-basil.json"), "w").write(json.dumps(doc, indent=2) + "\n")
