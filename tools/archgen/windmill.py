#!/usr/bin/env python3
"""THE TOWER WINDMILL (2026-10-03: walkable, its millwork whole), an arch-engine definition: a round stone tower in
three storeys, each a little narrower than the one under it, under the cap; the sail cross is its own item
(items/components/windmill-sails), turned by the game at (sx, sy, sz).

The way the grain goes, as in a small mill of the Middle Ages:
  * the BIN FLOOR under the cap: sacks hoisted up, emptied into the grain bin; above it, in the cap, the WINDSHAFT
    from the sails with the BRAKE WHEEL on it, driving the WALLOWER at the head of the MAIN SHAFT;
  * the STONE FLOOR: the grain runs down a chute into the HOPPER on its horse, the SHOE shakes it into the eye of the
    RUNNER STONE, turned by the main shaft over the fixed BEDSTONE inside the TUN;
  * the MEAL FLOOR (the ground): the meal falls from the tun's spout down the meal chute into the bin, and is sacked.
Steps wind up the inside of the wall from floor to floor, through a hatch in each. The gears, shafts and the runner are
`spin` markers: the game turns them with the sails (the brake wheel and the windshaft as fast, the wallower, the main
shaft and the runner four times as fast).

    python3 tools/archgen/windmill.py     # -> assets/architecture/windmill.json, assets/finishes/windmill.json
"""
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PI2 = 1.5707963
ST = [(0.0, 3.6, 3.6), (3.6, 3.4, 3.35), (7.0, 3.0, 3.1)]   # each storey: its foot, height, outer radius
T, NW = 0.6, 16                                             # the wall's thickness, its bays round
H = ST[-1][0] + ST[-1][1]                                   # the tower's top: the cap sits on it
SY, SZ = H + 0.9, ST[-1][2] + 1.6                           # the windshaft's height, the sails' hub out from the wall
P = {"detail": 4, "h": H, "sailR": 6.8, "sx": 0, "sy": SY, "sz": SZ,
     "_h": "the tower's top (the cap on it); sx/sy/sz where the sail cross's hub turns, sailR its arms' length"}
R3 = lambda v: round(v, 4)
parts = {}


def ring(name, r_out, r_in, h, y, bays=None, skip=None, opening=None, n=NW, solid=True):
    d = {"type": "ring", "count": n, "rOuter": R3(r_out), "rInner": R3(r_in), "height": R3(h), "y": R3(y), "place": [[0, 0, 0, 0]]}
    if bays is not None: d["at"] = bays
    if skip: d["skip"] = skip
    if opening: d["opening"] = opening
    elif solid: d["solid"] = True
    parts[name] = d


def bays_in(lo, hi, n):   # the bays of an n-bay ring whose middles lie between the angles lo and hi (radians, round from +z through +x)
    out = []
    for k in range(n):
        a = k * 2 * math.pi / n
        for w in (a, a + 2 * math.pi, a - 2 * math.pi):
            if lo <= w <= hi: out.append(k); break
    return out


win = {"width": 0.6, "sill": 1.2, "springing": 1.7, "head": {"profile": "semicircular"}, "glass": False}
door = {"width": 1.2, "sill": 0, "springing": 1.9, "head": {"profile": "semicircular"}, "glass": False}
OPEN = [(4, door), (12, win)], [(8, win), (12, win)], [(4, win), (10, win)]   # per storey: (bay, opening) -- bay 4 faces +x
windows = []
for i, ((y0, h, R), ops) in enumerate(zip(ST, OPEN)):
    ring(f"storey {i}", R, R - T, h, y0, skip=[b for b, _ in ops])
    for k, (b, o) in enumerate(ops):
        ring(f"storey {i} {'door' if o is door else 'window'} {k}", R, R - T, h, y0, bays=[b], opening=o, solid=False)
        a = b * 2 * math.pi / NW
        if o is win: windows.append([R3((R - T / 2) * math.sin(a)), R3(y0 + 1.2), R3((R - T / 2) * math.cos(a)), R3(a)])
# the floors: the ground under the walls (2cm in from their face); the stone floor and the bin floor boarded, an inner
# disc and an outer ring with the hatch the steps come up through
parts["ground floor"] = {"type": "column", "radius": ST[0][2] - 0.02, "height": 0.15, "sides": NW, "at": [[0, 0, 0, 0]], "walked": True}
# the steps: one tread a copy wound round the wall (spiral placement), from each floor to the next
def steps(name, y0, y1, r, a0):
    n = round((y1 - y0) / 0.2); dy = (y1 - y0) / n; da = 0.3 / (r - 0.35)
    parts[name] = {"type": "flight", "run": 0.3, "width": 0.7, "base": 0, "top": R3(dy), "steps": 1, "landing": 0,
                   "spiral": {"count": n, "radius": R3(r), "y": R3(y0), "dy": R3(dy), "turn": R3(a0), "turns": R3(n * da / (2 * math.pi))}}
    return n, dy, da
F1, F2 = ST[1][0] + 0.2, ST[2][0] + 0.2                     # the tops of the stone floor and the bin floor
n0, dy0, da0 = steps("steps up", 0.15, F1, ST[0][2] - T - 0.02, math.pi)
a1 = math.pi + n0 * da0 + 0.13 + 1.0 / (ST[1][2] - T - 0.35)   # (past the hatch's edge, a step's run and a stair's width of floor before it)
n1, dy1, da1 = steps("steps up 2", F1, F2, ST[1][2] - T - 0.02, a1)
NF = 24
def hatch(y_floor, y0, dy, da, a_start, n):   # the outer ring's bays over the steps that a head would meet under the floor
    k0 = math.ceil((y_floor - 2.0 - y0) / dy)
    return bays_in(a_start + k0 * da - 0.13, a_start + n * da + 0.13, NF)
# (each floor's outer ring, laid on the wall's offset, first: the inner disc is held at its edge by the ring)
ring("stone floor ring", ST[0][2] - T, 1.9, 0.2, ST[1][0], skip=hatch(ST[1][0], 0.15, dy0, da0, math.pi, n0), n=NF)
parts["stone floor"] = {"type": "column", "radius": 1.9, "height": 0.2, "sides": NW, "at": [[0, ST[1][0], 0, 0]]}
ring("bin floor ring", ST[1][2] - T, 1.7, 0.2, ST[2][0], skip=hatch(ST[2][0], F1, dy1, da1, a1, n1), n=NF)
ring("bin floor", 1.7, 0.25, 0.2, ST[2][0], n=NF)
# THE CURB the cap turns on: a timber ring laid on the wall head and reaching out under the cap's eaves -- the cap
# overhangs the tower by 45 cm, and its skin used to stand on nothing out there
CURB = 0.3
ring("curb", ST[-1][2] + 0.45, ST[-1][2] - T, CURB, H, n=NW)
parts["cap"] = {"type": "dome", "radius": ST[-1][2] + 0.45, "sides": NW, "thickness": 0.12, "cap": False, "head": {"profile": "trigonal", "rise": 3.6}, "oculus": 0.25, "at": [[0, H + CURB, 0, 0]]}
# the static millwork: the bedstone in its tun, the hopper on its horse, the chutes, the bins
item = lambda path, at, params=None, **k: {"type": "item", "item": path, "at": [at], **({"params": params} if params else {}), **k}
parts["bedstone"] = item("items/components/millstone", [0, F1, 0, 0], {"h": 0.24})
parts["tun"] = item("items/components/tun", [0, F1, 0, 0], solid=False)
parts["hopper"] = item("items/components/hopper-horse", [0.55, F1 + 0.55, 0, 0], solid=False)
parts["grain chute"] = {"type": "box", "width": 0.22, "length": 0.22, "height": R3(F2 - (F1 + 1.5)), "at": [[0.6, R3(F1 + 1.5), 0, 0]]}
parts["grain bin"] = {"type": "box", "width": 1.2, "length": 0.9, "height": 1.1, "at": [[0.7, F2, 0.2, 0]]}
parts["meal chute"] = {"type": "box", "width": 0.2, "length": 0.2, "height": R3(F1 + 0.15 - 1.0), "at": [[-1.0, 1.0, 0, 0]]}
parts["meal bin"] = {"type": "box", "width": 1.0, "length": 0.9, "height": 0.85, "at": [[-1.2, 0.15, 0, 0]]}
parts["flour"] = item("items/tools/sack-standing", [-1.6, 0.15, 1.0, 0], solid=False)
parts["flour 2"] = item("items/tools/sack-standing", [-1.0, 0.15, 1.2, 0.6], solid=False)
parts["grain sacks"] = item("items/tools/sack", [1.6, 0.15, -1.3, 0.4], solid=False)
parts["grain sacks 2"] = item("items/tools/sack", [1.2, F1, -1.3, 0.2], solid=False)
parts["grain sacks 3"] = item("items/tools/sack", [-1.0, F2, 0.6, 1.2], solid=False)
# the turning millwork (the game turns these with the sails): windshaft and brake wheel as fast as the sails, the
# wallower, the main shaft and the runner stone four times as fast (32 cogs on 8 staves) and the SAME way round their
# own axes: the wallower is under the brake wheel and takes its cogs at the wheel's bottom, on its own near (+z) side,
# where both move toward +x -- a positive turn about z drives a positive turn about y. (The water mill's wallower sits
# on top of its pit wheel, where the cogs move the other way: there the sign is negative.)
spin = lambda name, at, it, params, axis, ratio: parts.__setitem__(name, {"type": "marker", "role": "spin", "at": [at], "data": {"item": it, "params": params, "axis": axis, "ratio": ratio}})
spin("windshaft", [0, SY, SZ - 0.1, 0], "items/components/mill-shaft", {"L": R3(SZ + 1.7), "r": 0.15, "along": "z"}, "z", 1)
spin("brake wheel", [0, SY, 0.5, 0], "items/components/face-gear", {"r": 1.3, "n": 32}, "z", 1)
spin("wallower", [0, R3(SY - 1.5), 0, 0], "items/components/lantern-pinion", {"r": 0.36, "h": 0.4, "n": 8}, "y", 4)
spin("main shaft", [0, R3(F1 + 0.46), 0, 0], "items/components/mill-shaft", {"L": R3(SY - 1.5 - F1 - 0.46), "r": 0.11}, "y", 4)
spin("runner stone", [0, R3(F1 + 0.24), 0, 0], "items/components/millstone", {"h": 0.22}, "y", 4)
# its life: the miller at the stones, the door (+x), the windows' shutters
parts["miller"] = {"type": "marker", "role": "spot", "at": [[1.5, F1, -0.9, 0]], "data": {"pose": "stand", "work": 1, "gesture": "lift", "face": 2.4}}
parts["door marker"] = {"type": "marker", "role": "door", "at": [[R3(ST[0][2] - T / 2), 0.15, 0, -PI2]], "data": {"w": 1.2, "h": 2.35, "spring": 1.75, "head": {"profile": "semicircular"}}}
parts["windows"] = {"type": "marker", "role": "window", "at": windows, "data": {"w": 0.6, "h": 0.8, "spring": 0.5, "head": {"profile": "semicircular"}}}

doc = {"name": "Windmill", "_about": "A TOWER WINDMILL of the Middle Ages, walkable: three storeys of round stone tower under the cap -- the meal floor (the meal chute into its bin, the flour sacked), the stone floor (bedstone and runner in the tun, the hopper on its horse fed from the bin above), the bin floor under the cap (the grain bin; overhead the windshaft and its brake wheel driving the wallower on the main shaft) -- steps winding up the wall through a hatch in each floor; the sail cross (items/components/windmill-sails) and the millwork turn with the wind.",
       "params": P, "parts": parts, "build": list(parts), "walked": True}
open(os.path.join(ROOT, "assets/architecture/windmill.json"), "w").write(json.dumps(doc, indent=1) + "\n")
fin = {"name": "Windmill", "building": "architecture/windmill", "_about": "the windmill: limewashed rubble, a tiled cap, boarded floors, oak bins and chutes",
       "stone": {"color": "#cfc4ae", "accent": "#b8ab92", "pat": "ashlar"},
       "rules": [{"parts": "cap", "side": "out", "pattern": "roofs/fish scale", "palette": "tile-brown"},
                 {"parts": "cap", "pattern": "timber/boards", "palette": "oak-grey"},
                 {"parts": ["curb", "stone floor", "stone floor ring", "bin floor", "bin floor ring", "grain chute", "grain bin", "meal chute", "meal bin", "kind:flight"], "pattern": "timber/boards", "palette": "oak-grey"},
                 {"parts": "ground floor", "surface": "floor", "pattern": "floors/flagstones", "palette": "stone"},
                 {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
                 {"pattern": "stone/rubble", "palette": "limestone"}]}
open(os.path.join(ROOT, "assets/finishes/windmill.json"), "w").write(json.dumps(fin, indent=1) + "\n")
print("windmill:", len(parts), "parts; hatches", parts["stone floor ring"]["skip"], parts["bin floor ring"]["skip"])
