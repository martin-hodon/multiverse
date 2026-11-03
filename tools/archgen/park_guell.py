# PARK GUELL (2026-11-02): Gaudi's garden city on the Muntanya Pelada, Barcelona, 1900-1914 -- its main entrance, as one
# landmark. Writes assets/architecture/park-guell.json and assets/finishes/park-guell.json; the pieces are gaudi.py's
# components (pavilion, mushroom, hyperboloid tower, cross) and its helpers (bench profile, leaning portico), the curves
# are `sweep`s (arch/sweep.js), the trencadis and the rubble the `shards` layer (ornament/shards.js).
#
# SOURCED (es/ca.wikipedia, $X/ref/pg_*.txt):
#   entrance wall 210 m long, 2-4 m high, rubble with a crest of white and red ceramic bands, 15 medallions 1.4 m across;
#   porter's lodge 14.80 x 7.66 m in plan, 21 m high, three floors, a tower with a mirador and a bell-shaped mushroom
#   cupola (an amanita); administration pavilion 12.60 x 6.60 m, 29 m high, a mushroom cupola, a hyperboloid tower at one
#   side in a white and blue chequer of trencadis with the four-armed cross 3.8 m tall; plans "ovalada" (ca);
#   the stair: two branches, 45 steps (11 + 11 + 11 + 12), 20 m long, 8.1 m wide, side walls elliptical, up to 5.8 m,
#   white and coloured ceramic, three fountains (the dragon, 2.4 m long, on the third), a bench on the last landing;
#   the hypostyle room: 1500 m2, 43 m long, 86 Doric columns 6.16 m tall and 1.20 m across, trencadis to 1.8 m, the outer
#   ones inclined; 90 planned, 4 left out for 4 ceiling rosettes 3 m across, 14 medallions 1 m across in the vaults;
#   the square over it: an oval of 2694 m2 (86 x 43 m), its cornice with lion-head gargoyles and triglyphs, edged by
#   the serpentine bench (110 m (es) / 150 m (ca) -- the sources differ), white trencadis below, many colours above;
#   the washerwoman's portico 83 m long, its outer columns upright, the inner ones leaning against an inclined wall.
# ESTIMATED (from photographs and the plan's logic, flagged here): the levels (the hypostyle's floor 7.0 m over the
# street, from 45 steps of 15.5 cm; the square 14.8 m); the column grid (9 x 10 at 4.25 x 4.0 m, the four rosettes'
# places); the outer columns' lean (4 degrees, feet out); which pavilion stands which side (the lodge west, the
# administration east, the tower at its street-side corner); the pavilions' wall heights, roofs and towers within the
# sourced totals; the stair walls' curve; the bench's wave (1.2 m deep, 7.5 m long); the portico's place and section;
# the hill.
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gaudi import oval, bench_profile, leaning_portico, hypostyle, resample, r3
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
PI2 = 1.5707963

# ---- levels and the plan (x east, +z south to the street, Carrer d'Olot at z = 0)
FLOOR = 7.0              # the hypostyle's floor: the stair's top
COLH = 6.16              # its columns (sourced)
SPRING = FLOOR + COLH    # the vaults spring from the capitals
SLAB = SPRING + 0.8      # the vaults' crown, the slab's underside
SQ = SLAB + 0.84         # the square
DX, DZ = 4.25, 4.0       # the column grid
Z0 = -37.6               # the front row
OA, OB, OC = 43.0, 21.5, -56.5   # the square's oval: half-axes and middle (z)

# ---- the ground
add("vestibule", {"type": "prism", "plan": {"points": [[-24, 0.5], [24, 0.5], [24, -16.2], [-24, -16.2]]}, "height": 0.3, "at": [[0, -0.3, 0, 0]], "walked": True,
                  "_about": "the vestibule inside the gate, 400 m2 between the pavilions and the stair, paved"})
add("street", {"type": "prism", "plan": {"points": [[-110, 12], [110, 12], [110, 0.5], [-110, 0.5]]}, "height": 0.3, "at": [[0, -0.3, 0, 0]], "walked": True,
               "_about": "Carrer d'Olot in front of the wall"})

# ---- the entrance wall: rubble, a rolled crest of white and red bands, 15 medallions
for side, xs in (("west", [[-19.9, 0], [-45, 0.2], [-75, -1.5], [-105, -4.5]]), ("east", [[17.7, 0], [45, 0.2], [75, -1.5], [105, -4.5]])):
    path = xs if side == "east" else xs[::-1]
    add(f"{side} wall", {"type": "sweep", "path": path, "step": 1.0, "profile": [[-0.35, 0], [0.35, 0], [0.35, 2.7], [-0.35, 2.7]],
                         "_about": "the wall round the park (210 m of it built), of the hill's own stone laid rough, 2-4 m high"})
    add(f"{side} wall crest", {"type": "sweep", "path": path, "step": 1.0, "round": True,
                               "profile": [[-0.42, 2.7], [0.42, 2.7], [0.44, 2.95], [0.3, 3.2], [0, 3.3], [-0.3, 3.2], [-0.44, 2.95]],
                               "_about": "its crest, rolled and dressed in trencadis in bands of white and red"})
WALLZ = [[17.7, 0], [45, 0.2], [75, -1.5], [105, -4.5]]
def wallz(x):
    x = abs(x)
    for (x0, z0), (x1, z1) in zip(WALLZ, WALLZ[1:]):
        if x <= x1: return z0 + (z1 - z0) * max(0, x - x0) / (x1 - x0)
    return WALLZ[-1][1]
med = [[r3(x), 1.7, r3(wallz(x) + 0.33), 0] for x in [-23.5, -31.5, -39.5, -47.5, -55.5, -63.5, -71.5, -79.5, 23.0, 31.0, 39.0, 47.0, 55.0, 63.0, 71.0]]
add("medallions", {"type": "loft", "axis": "z", "sides": 20, "at": med,
                   "sections": [{"s": -0.05, "a": 0.7, "b": 0.7}, {"s": 0.06, "a": 0.7, "b": 0.7}, {"s": 0.12, "a": 0.6, "b": 0.6}],
                   "_about": "the 15 medallions on the street face, 1.4 m across, 'Park' and 'Guell' in trencadis (sourced number and size; their spacing estimated)"})

# ---- the gate: the palm-leaf iron gate from the Casa Vicens (1965), its two leaves standing open: a few uprights, the
# palm's fronds fanning from a point low in each leaf to its top rail
gx = []
for sx in (-4.0, 4.0):
    gx += [[sx, 0, r3(-0.15 - k * 0.5), sx, 2.9, r3(-0.15 - k * 0.5)] for k in range(8)]
    gx += [[sx, h, -0.15, sx, h, -3.66] for h in (0.15, 1.4, 2.85)]
    gx += [[sx, 0.3, -1.9, sx, 2.85, r3(-0.3 - k * 0.48)] for k in range(8)]
add("gate", {"type": "bars", "lines": gx, "w": 0.05, "h": 0.05, "caps": False, "kind": "moulding",
             "_about": "the wrought-iron gate's two leaves, swung back against the pavilions' ends: uprights, rails, and the fan of a palm leaf in each"})

# ---- the pavilions (gaudi-pavilion): the porter's lodge west of the gate, the administration east (side estimated)
add("porter's lodge", {"type": "component", "use": "components/gaudi-pavilion",
                       "params": {"w": 14.8, "l": 7.66, "ch": 2.4, "h": 7.0, "storeys": 2, "roofH": 5.8, "wave": 0.42,
                                  "towerR": 1.9, "towerX": 0, "towerZ": -0.3, "towerH": 17.4, "lookH": 2.4, "capR": 2.2, "capH": 3.6, "bell": 1.0,
                                  "chimneys": "yes", "spire": "no"},
                       "at": [[-12.45, 0, -4.25, 0]],
                       "_about": "the porter's lodge (now the park's interpretation centre): 14.80 x 7.66 m, two floors and the attic in the roof, the tower with its mirador and the amanita to 21 m"})
add("administration", {"type": "component", "use": "components/gaudi-pavilion",
                       "params": {"w": 12.6, "l": 6.6, "ch": 2.1, "h": 6.0, "storeys": 2, "roofH": 4.2, "wave": 0.4, "winGap": 2.2, "doorH": 1.7,
                                  "towerR": 1.6, "towerX": -0.4, "towerZ": -0.2, "towerH": 12.2, "lookH": 1.8, "capR": 1.9, "capH": 2.6, "bell": 0.35,
                                  "chimneys": "yes",
                                  "spire": "yes", "spireX": 5.4, "spireY": 0, "spireZ": 1.2, "spireH": 23.0, "spireR": 2.0, "crossH": 3.8},
                       "at": [[11.3, 0, -3.75, 0]],
                       "_about": "the administration pavilion (now the shop): 12.60 x 6.60 m, two floors, its mushroom cupola, and at its street corner the hyperboloid tower in a white and blue chequer, the cross on it at 29 m"})

# ---- the stair: two branches either side of a spine of fountains, 45 steps, between elliptical walls
RISE = FLOOR / 45; RUN = 0.32; LAND = 1.9; SW = 3.0; SP = 1.05
z, y, flights = -16.2, 0.0, []
for k, n in enumerate([11, 11, 11, 12]):
    flights.append((z, y, n))
    z -= n * RUN + (LAND if k < 3 else 0); y += n * RISE
for k, (zs, ys, n) in enumerate(flights):
    for side, xr in (("west", -SP), ("east", SP + SW)):
        add(f"stair {side} {k + 1}", {"type": "flight", "width": SW, "run": RUN, "rise": RISE, "base": r3(ys), "top": r3(ys + n * RISE),
                                      "landing": 0, "ground": 0, "railing": False, "at": [[r3(xr), 0, r3(zs), PI2]],
                                      "_about": f"the {side} branch's flight {k + 1}: {n} steps" + (" and its landing" if k < 3 else ", arriving under the hypostyle")})
        if k < 3:
            zt = zs - n * RUN
            add(f"landing {side} {k + 1}", {"type": "prism", "plan": {"points": [[r3(xr - SW), r3(zt)], [r3(xr), r3(zt)], [r3(xr), r3(zt - LAND)], [r3(xr - SW), r3(zt - LAND)]]},
                                            "height": r3(ys + n * RISE), "at": [[0, 0, 0, 0]], "walked": True, "_about": f"the {side} branch's landing {k + 1}"})
STAIR_END = z
# the spine: a basin at every landing's level, the grotto, the coat of arms with its snake, the dragon, the tripod bench
spine = []
for k, (zs, ys, n) in enumerate(flights):
    top = ys + n * RISE
    spine.append([r3(zs), r3(zs - n * RUN - (LAND if k < 3 else 0)), r3(top)])
for k, (za, zb, top) in enumerate(spine):
    add(f"spine {k + 1}", {"type": "prism", "plan": {"points": [[-SP, za], [SP, za], [SP, zb], [-SP, zb]]}, "height": r3(top + 0.45), "at": [[0, 0, 0, 0]],
                           "_about": "the spine between the branches, stepping up with them: a fountain's basin at each level"})
add("basins", {"type": "prism", "plan": {"rect": [1.7, 1.2], "chamfer": 0.45}, "height": 0.35,
               "at": [[0, r3(spine[0][2] + 0.45), r3(spine[0][0] - 1.0), 0], [0, r3(spine[0][2] + 0.45), r3(spine[1][0] + 0.75), 0], [0, r3(spine[1][2] + 0.45), r3(spine[1][1] + 0.75), 0]],
               "_about": "the fountains' basins: the grotto's at the foot, the coat of arms' with its snake, and the one the dragon spits into"})
# the first fountain: a grotto of rough stones behind its basin
g0y, g0z = r3(spine[0][2] + 0.45), r3(spine[0][0] - 2.4)
add("grotto", {"type": "loft", "axis": "z", "sides": 9, "half": True, "smooth": 2, "at": [[0, g0y, g0z, 0]],
               "sections": [{"s": -1.3, "a": 0.7, "b": 0.6, "n": 1.6}, {"s": -0.7, "a": 1.0, "b": 1.25, "n": 1.7}, {"s": -0.1, "a": 0.95, "b": 1.05, "n": 1.5},
                            {"s": 0.45, "a": 0.6, "b": 0.45, "n": 1.4}],
               "_about": "the first fountain: a grotto of the hill's rough stones, the water welling from it into the basin"})
# the second: the arms of Catalonia, the snake of Asclepius coiled across them
c0y, c0z = spine[0][2] + 0.45, spine[1][0]
add("coat of arms", {"type": "box", "width": 1.3, "length": 0.12, "height": 1.15, "at": [[0, r3(c0y + 0.3), r3(c0z + 0.06), 0]],
                     "_about": "the second fountain: the four bars of the Catalan arms on the spine's face, in trencadis"})
add("snake", {"type": "sweep", "path": [[-0.5, r3(c0y + 0.45), r3(c0z + 0.19)], [0.35, r3(c0y + 0.7), r3(c0z + 0.19)], [-0.35, r3(c0y + 0.98), r3(c0z + 0.19)],
                                        [0.3, r3(c0y + 1.22), r3(c0z + 0.19)], [0.05, r3(c0y + 1.5), r3(c0z + 0.26)]],
              "step": 0.08, "round": True, "profile": [[-0.07, -0.05], [0.07, -0.05], [0.07, 0.05], [-0.07, 0.05]],
              "_about": "the snake's head over the arms, the water from its mouth (the serpent of Asclepius, or the Python of Delphi)"})
# the third: the dragon, El Drac, head down toward the street, its mouth open over the basin
d0z, d0y = spine[2][0] - 1.0, spine[2][2] + 0.45
add("dragon", {"type": "loft", "axis": "z", "sides": 14, "smooth": 3, "at": [[0, r3(d0y), r3(d0z), 0]],
               "sections": [{"s": -1.62, "u": 0.02, "v": 1.0, "a": 0.02, "b": 0.02},
                            {"s": -1.55, "u": 0.08, "v": 0.86, "a": 0.06, "b": 0.06},
                            {"s": -1.42, "u": 0.18, "v": 0.6, "a": 0.09, "b": 0.09},
                            {"s": -1.22, "u": 0.2, "v": 0.42, "a": 0.13, "b": 0.12},
                            {"s": -0.95, "u": 0.1, "v": 0.38, "a": 0.2, "b": 0.17},
                            {"s": -0.65, "u": 0, "v": 0.42, "a": 0.32, "b": 0.26},
                            {"s": -0.25, "u": 0, "v": 0.5, "a": 0.47, "b": 0.34},
                            {"s": 0.15, "u": 0, "v": 0.52, "a": 0.5, "b": 0.36},
                            {"s": 0.45, "u": 0, "v": 0.5, "a": 0.36, "b": 0.27},
                            {"s": 0.6, "u": 0, "v": 0.52, "a": 0.25, "b": 0.2}],
               "_about": "El Drac, the salamander (2.4 m, sourced), in many-coloured trencadis on the third fountain: its body and a tail that curls up and aside"})
add("dragon head", {"type": "loft", "axis": "z", "sides": 12, "smooth": 3, "at": [[0, r3(d0y), r3(d0z), 0]],
                    "sections": [{"s": 0.5, "v": 0.58, "a": 0.25, "b": 0.17}, {"s": 0.68, "v": 0.6, "a": 0.25, "b": 0.15},
                                 {"s": 0.84, "v": 0.57, "a": 0.18, "b": 0.09, "n": 2.6}, {"s": 0.9, "v": 0.55, "a": 0.06, "b": 0.03}],
                    "_about": "its head and upper jaw, eyes bulging"})
add("dragon jaw", {"type": "loft", "axis": "z", "sides": 10, "smooth": 3, "at": [[0, r3(d0y), r3(d0z), 0]],
                   "sections": [{"s": 0.5, "v": 0.4, "a": 0.2, "b": 0.08}, {"s": 0.68, "v": 0.33, "a": 0.17, "b": 0.06},
                                {"s": 0.8, "v": 0.29, "a": 0.12, "b": 0.045}, {"s": 0.85, "v": 0.28, "a": 0.04, "b": 0.02}],
                   "_about": "its lower jaw dropped: the open mouth the water runs from"})
add("dragon crest", {"type": "sweep", "path": [[0, r3(d0y + 0.5), r3(d0z - 1.22)], [0, r3(d0y + 0.6), r3(d0z - 0.9)], [0, r3(d0y + 0.73), r3(d0z - 0.55)],
                                               [0, r3(d0y + 0.85), r3(d0z - 0.2)], [0, r3(d0y + 0.86), r3(d0z + 0.15)], [0, r3(d0y + 0.75), r3(d0z + 0.5)], [0, r3(d0y + 0.72), r3(d0z + 0.7)]],
                     "step": 0.06, "profile": [[-0.07, -0.12], [0.07, -0.12], [0.03, 0.12], [0, 0.26], [-0.03, 0.12]],
                     "_about": "the ridge of plates along its back, from the head to the tail"})
add("dragon legs", {"type": "column", "radius": 0.09, "height": 0.3, "sides": 6,
                    "at": [[-0.4, r3(d0y), r3(d0z + 0.35), 0], [0.4, r3(d0y), r3(d0z + 0.35), 0], [-0.36, r3(d0y), r3(d0z - 0.45), 0], [0.36, r3(d0y), r3(d0z - 0.45), 0]],
                    "_about": "its four short legs, splayed"})
add("odeon bench", {"type": "sweep", "path": oval(0, r3(spine[3][1] + 2.4), 0.72, 0.85, math.pi * 1.15, math.pi * 1.85, 10)[::-1],
                    "step": 0.15, "profile": [[-0.22, 0], [0.22, 0], [0.22, 0.42], [0.3, 0.42], [0.3, 0.95], [0.12, 0.95], [0.12, 0.42], [-0.22, 0.42]],
                    "at": [[0, r3(spine[3][2] + 0.45), 0, 0]],
                    "_about": "the little odeon on the spine's last step: a curved bench facing the street, sheltered from the wind, in the sun (sourced; its size estimated)"})

# the walls either side of the stair, close along its flights and splaying out at the foot into the vestibule; rubble faced
# in a chequer of white and coloured trencadis, a planter along their top behind merlons; the planted beds behind them
def stair_y(z): return max(0.0, min(FLOOR, (-16.2 - z) / (-16.2 - STAIR_END) * FLOOR))
XW = SP + SW + 0.35
for s, nm in ((-1, "west"), (1, "east")):
    pl = [[s * XW, STAIR_END], [s * XW, -24.0], [s * (XW + 0.5), -20.0], [s * (XW + 1.9), -17.2], [s * 8.3, -14.6]]
    if s > 0: pl = pl[::-1]     # (traversed so its right is outward)
    path = [[x, r3(stair_y(z)), z] for x, z in pl]
    add(f"stair wall {nm}", {"type": "sweep", "path": path, "step": 0.4, "profile": [[-0.35, -7.6], [0.35, -7.6], [0.35, 2.0], [-0.35, 2.0]],
                             "_about": "the stair's side wall, close along its flights and splaying out at the foot, its face a chequer of white and coloured trencadis"})
    add(f"planter {nm}", {"type": "sweep", "path": path, "step": 0.4,
                          "profile": [[-0.02, 2.0], [0.5, 2.0], [0.5, 2.5], [0.38, 2.5], [0.38, 2.14], [0.12, 2.14], [0.12, 2.5], [-0.02, 2.5]],
                          "_about": "the planter trough along the wall's top, in trencadis"})
    add(f"planter soil {nm}", {"type": "sweep", "path": path, "step": 0.4, "profile": [[0.12, 2.14], [0.38, 2.14], [0.38, 2.4], [0.12, 2.4]],
                               "_about": "its earth"})
    mer = []
    for x, y, z, hd in resample(path, 1.1)[1:]:
        rx, rz = -math.cos(hd), math.sin(hd)
        mer.append([r3(x - rx * 0.17), r3(y + 2.0), r3(z - rz * 0.17), 0])
    add(f"stair merlons {nm}", {"type": "prism", "plan": {"sides": 8, "radius": 0.17}, "height": 0.5, "at": mer,
                                "_about": "the rounded merlons along the wall's inner edge, over the stair"})
    zf = -15.4; k = (FLOOR + 0.3 - 1.52) / (STAIR_END - zf)
    bed = [[8.1, 0], [19.6, 0], [19.6, r3(-38.9 - zf)], [17.0, r3(STAIR_END - zf)], [XW + 0.35, r3(STAIR_END - zf)], [XW + 0.35, r3(-24.0 - zf)],
           [XW + 0.85, r3(-20.0 - zf)], [XW + 2.25, r3(-17.2 - zf)]]
    bed = [[r3(s * x), z] for x, z in bed][::(1 if s > 0 else -1)]
    add(f"bed {nm}", {"type": "prism", "plan": {"points": bed}, "height": 1.52, "slope": [0, r3(k)], "at": [[0, 0, zf, 0]],
                      "_about": "the planted bank behind the stair's wall, falling to the vestibule"})

# ---- the hypostyle room (gaudi.hypostyle): 86 Doric columns, shallow vaults between them, four rosettes where four were left out
H = hypostyle(add, files=9, rows=10, dx=DX, dz=DZ, z0=Z0, floor=FLOOR, colH=COLH, colR=0.6, gone={(2, 3), (6, 3), (2, 6), (6, 6)}, front=r3(STAIR_END))
assert sum(len(parts[g]["at"]) for g in ("columns", "front columns", "west columns", "east columns")) == 86
assert abs(H["spring"] - SPRING) < 1e-6 and abs(H["slab"] - SLAB) < 1e-6
# the front: architrave, the triglyphs, the lion-head gargoyles under the bench
add("architrave", {"type": "box", "width": 35.0, "length": 1.4, "height": 0.8, "at": [[0, SPRING, r3(Z0 + 0.5), 0]],
                   "_about": "the front's architrave over the inclined columns"})
add("triglyphs", {"type": "box", "width": 0.5, "length": 0.15, "height": 0.62, "at": [[r3(x), r3(SPRING + 0.09), r3(Z0 + 1.27), 0] for x in [k * 2.125 - 17 for k in range(17)]],
                  "_about": "the triglyphs on the frieze, one over each column and one between"})
add("gargoyles", {"type": "loft", "axis": "z", "sides": 10, "at": [[r3(x), r3(SQ - 0.55), r3(OC + OB * math.sqrt(max(0, 1 - (x / OA) ** 2)) - 0.05), 0] for x in [-36, -28, -20, -12, -4.25, 4.25, 12, 20, 28, 36]],
                  "sections": [{"s": 0, "a": 0.28, "b": 0.24}, {"s": 0.35, "a": 0.26, "b": 0.22}, {"s": 0.6, "a": 0.17, "b": 0.14}, {"s": 0.75, "a": 0.08, "b": 0.06}],
                  "_about": "lion-head gargoyles spouting the square's rain from its cornice (sourced; spacing estimated)"})

# ---- the square: an oval, the slab on the vaults, its ends on rubble terraces, the bench round its edge
ovp = oval(0, OC, OA, OB, 0, 2 * math.pi, 64)[:-1]
add("square", {"type": "prism", "plan": {"points": ovp}, "height": r3(SQ - SLAB), "at": [[0, SLAB, 0, 0]], "walked": True,
               "_about": "the Nature Square (the Greek theatre), 86 x 43 m, the stage for the colony's fiestas; its gravel drains into the columns"})
for s, nm in ((-1, "west"), (1, "east")):
    lune = [p for p in ovp if s * p[0] >= 19.6]
    lune = [[s * 19.6, r3(OC + OB * math.sqrt(1 - (19.6 / OA) ** 2))]] + sorted(lune, key=lambda p: -s * math.atan2(p[1] - OC, s * p[0])) + [[s * 19.6, r3(OC - OB * math.sqrt(1 - (19.6 / OA) ** 2))]]
    add(f"{nm} terrace", {"type": "prism", "plan": {"points": lune}, "height": r3(SLAB), "at": [[0, 0, 0, 0]],
                          "_about": "the square's end beyond the hypostyle, carried on the hill and its own retaining wall of rubble"})
zb = H["zb"] - 0.9; xb = OA * math.sqrt(1 - ((zb - OC) / OB) ** 2)
back = [[r3(xb), r3(zb)]] + [p for p in ovp if p[1] < zb and abs(p[0]) < xb] [::-1] + [[r3(-xb), r3(zb)]]
add("back terrace", {"type": "prism", "plan": {"points": back}, "height": r3(SLAB), "at": [[0, 0, 0, 0]],
                     "_about": "the square's back edge beyond the hall, on the hill"})
# the bench: the profile swept round the front of the oval, waving in and out
bp = oval(0, OC, OA - 1.4, OB - 1.4, -0.12, math.pi + 0.12, 72)[::-1]
add("bench", {"type": "sweep", "path": bp, "step": 0.3, "wave": {"amp": 1.2, "length": 7.5}, "profile": bench_profile(1.0, 0.8), "round": False,
              "at": [[0, SQ, 0, 0]],
              "_about": "the serpentine bench round the square's edge (Gaudi and Jujol, 1910-1914): its back rolls over like a wave, its loops make little rooms; white trencadis below, every colour above"})

# ---- the hill behind, and the washerwoman's portico climbing its west flank
# the portico: 83 m (sourced) along the hill's south face from the square's west end, climbing west; the hill is shaped so
# the path runs along its flank -- the hill rising on its left (north) behind the wall, falling away on its right
PORT = [[-128.0, -98.0], [-108.0, -93.5], [-87.0, -87.0], [-66.0, -81.0], [-46.0, -76.0]]
_L = [0.0]
for (x0, z0), (x1, z1) in zip(PORT, PORT[1:]): _L.append(_L[-1] + math.hypot(x1 - x0, z1 - z0))
PCLIMB = 8.0
port3 = [[x, r3(SQ + PCLIMB * (1 - l / _L[-1])), z] for (x, z), l in zip(PORT, _L)]
# (the hill's half-width south of its crest a, north a2; at its middle the flank is about as steep as it is high over the run)
hs = [(-170, -121, 0), (-128, -121, 43.7), (-87, -110, 35.7), (-46, -99, 27.7), (-10, -118, 34), (30, -120, 36), (110, -112, 26), (150, -112, 0)]
add("hill", {"type": "loft", "axis": "x", "sides": 24, "half": True, "hill": True, "smooth": 3, "at": [[0, 0, 0, 0]],
             "sections": [{"s": x, "u": u, "v": 0, "a": 46, "a2": 30, "b": b} for x, u, b in hs],
             "_about": "the Muntanya Pelada behind the square, rising west toward the Turo de les Tres Creus, its south flank carrying the portico (its shape estimated)"})
for s_, nm in ((-1, "west"), (1, "east")):
    add(f"{nm} slope", {"type": "loft", "axis": "z", "sides": 20, "half": True, "hill": True, "smooth": 3, "at": [[0, 0, 0, 0]],
                        "sections": [{"s": -118, "u": s_ * 52, "v": 0, "a": 30, "a2": 30, "b": 17}, {"s": -80, "u": s_ * 50, "v": 0, "a": 30, "a2": 30, "b": 13},
                                     {"s": -45, "u": s_ * 47, "v": 0, "a": 30, "a2": 30, "b": 11}, {"s": -14, "u": s_ * 48, "v": 0, "a": 28, "a2": 28, "b": 3}],
                        "_about": "the hillside either side of the stair and the square, gardens climbing from the street (estimated)"})
leaning_portico(add, "portico", port3, 5.2, 4.0, step=3.0, lean=12)

# (what carries comes first: the floor before the columns on it, the square before its gargoyles, the legs before the dragon)
def before(a, b):
    build.remove(a); build.insert(build.index(b), a)
before("hypostyle fill", "columns"); before("floor", "columns"); before("square", "architrave"); before("dragon legs", "dragon")

params = {"detail": 4}
out = {"name": "Park Guell", "_about": "PARK GUELL, Barcelona (Antoni Gaudi, 1900-1914): the main entrance of Eusebi Guell's garden city on the Muntanya Pelada -- the rubble wall with its medallions, the two gingerbread pavilions (the porter's lodge with its amanita, the administration with its chequered hyperboloid tower and four-armed cross), the double stair round the trencadis dragon, the hypostyle room of 86 Doric columns under shallow white vaults and Jujol's rosettes, the oval square on it edged by the serpentine bench, and the washerwoman's portico of leaning columns. Built by tools/archgen/park_guell.py from gaudi.py's components.",
       "params": params, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/park-guell.json"), "w").write(json.dumps(out, indent=1) + "\n")

# ---- the finish: rubble and trencadis
R = lambda parts, pattern, palette, **k: {"parts": parts, "pattern": pattern, "palette": palette, **k}
fin = {"name": "Park Guell", "building": "architecture/park-guell",
       "_about": "Park Guell: the hill's own stone laid rough (Montjuic-brown rubble), and everything Gaudi wanted seen dressed in trencadis -- broken glazed tile -- white on the vaults and the bench's foot, the bench and the dragon in every colour, the pavilions' roofs cream and brown, the lodge's amanita red with white spots, the tower white and blue in a chequer, the wall's crest white and red in bands.",
       "stone": {"color": "#9b7c57", "accent": "#7f6549", "pat": "ashlar"},
       "rules": [
           {"parts": "kind:glass", "color": "#5d6f6a", "accent": "#3f4b48"},
           R(["porter's lodge/cupola/cap"], "tiles/trencadis spotted", "trencadis-amanita"),
           R(["administration/cupola/cap", "chimneys/cap"], "tiles/trencadis spotted", "trencadis-white"),
           R(["cupola/stem", "chimneys/stem", "lookout", "merlons", "stair merlons west", "stair merlons east"], "tiles/trencadis", "trencadis-white"),
           R(["spire/shaft", "spire/crown"], "tiles/trencadis chequer", "trencadis-blue"),
           R(["cross/shaft", "cross/arms", "cross/tips"], "tiles/trencadis", "trencadis-white"),
           R(["roof", "roof lobes", "cornice"], "tiles/trencadis", "trencadis-ochre"),
           R(["walls surrounds", "plaques", "planter west", "planter east"], "tiles/trencadis", "trencadis"),
           R(["west wall crest", "east wall crest"], "tiles/trencadis bands", "trencadis-amanita"),
           R(["coat of arms"], "tiles/trencadis bands", "trencadis-ochre"),
           R(["snake"], "tiles/trencadis", "trencadis-green"),
           R(["medallions", "dragon", "dragon head", "dragon jaw", "dragon legs", "rosettes", "medallions in the vaults"], "tiles/trencadis", "trencadis"),
           R(["dragon crest"], "tiles/trencadis", "trencadis-ochre"),
           R(["stair wall west", "stair wall east"], "tiles/trencadis chequer", "trencadis", scale=2.4),
           R(["bench"], "tiles/trencadis", "trencadis", above=r3(SQ + 0.45)),
           R(["bench", "odeon bench", "vaults", "ceiling", "basins"], "tiles/trencadis", "trencadis-white"),
           R([f"{c} shafts" for c in ["columns", "front columns", "west columns", "east columns"]], "tiles/trencadis", "trencadis-white", below=r3(FLOOR + 1.8)),
           R([f"{c} {p}" for c in ["columns", "front columns", "west columns", "east columns"] for p in ("shafts", "capitals", "abaci")] + ["architrave", "triglyphs", "gargoyles"], "stone/plaster", "plaster-white"),
           R(["gate"], "materials/hammered", "iron"),
           R(["kind:flight"] + [f"landing {sd} {k}" for sd in ("west", "east") for k in (1, 2, 3)] + ["spine 1", "spine 2", "spine 3", "spine 4", "vestibule"],
             "floors/flagstones", "granite", surface="floor"),
           R(["kind:flight"], "stone/ashlar", "granite"),
           R(["hill", "west slope", "east slope", "portico bank", "planter soil west", "planter soil east"], "stone/sand", "earth"),
           R(["bed west", "bed east"], "stone/sand", "earth", surface="floor"),
           {"surface": "floor", "pattern": "stone/sand", "palette": "gravel"},
           {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-ochre"},
           {"surface": "ceiling", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
           R(["kind:prism", "kind:enclosure", "kind:column", "kind:box"], "stone/field rubble", "montjuic"),
       ]}
open(os.path.join(ROOT, "assets/finishes/park-guell.json"), "w").write(json.dumps(fin, indent=1) + "\n")
print(f"park-guell: {len(parts)} parts")
