import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, math
p = os.path.join(ROOT, 'assets/architecture/elements/towers.json')
old = json.load(open(p))
parts = {}; build = []
def add(name, d): parts[name] = d; build.append(name)
params = {"detail": 8, "S": 5.4, "w": 1.1, "t": 0.8, "run": 0.32, "rise": 0.17, "n": 10, "fh": "n * rise", "storeyH": "4 * fh",
  "storeys": 3, "belfryH": 3.2, "slab": 0.3, "winW": 0.5, "winSill": 0.5, "winSpring": 1.3,
  "_S": "the square tower's inside: two corner landings (2w) and a flight (n x run) along each wall",
  "_fh": "one flight's climb: the landings are fh apart, four to a storey, round the well",
  "_win": "a slit window beside every landing, winSill over it: where the stair stops, never halfway up a flight",
  "R": 3.0, "rt": 0.8, "rTop": 15.0, "sRise": 0.18, "sTurn": 12, "gap": 14}
# ---- square tower: walls in pieces that start at the landings
top_n = 12   # flights: 4 * storeys
sides = [  # landing phase p (after flight p of each storey), wall name, window's x in the face, width, placement
  (1, "+x", "S - w / 2", "S", ["S / 2 + t", None, 0, "1.5707963"]),
  (2, "+z", "S + t - w / 2", "S + 2 * t", [0, None, "S / 2 + t", 0]),
  (3, "-x", "w / 2", "S", ["0 - S / 2", None, 0, "1.5707963"]),
  (4, "-z", "t + w / 2", "S + 2 * t", [0, None, "0 - S / 2", 0])]
def wall(width, height, y, pl, openings):
    return {"type": "wall", "width": width, "height": height, "thickness": "t", "openings": openings, "at": [[pl[0], y, pl[2], pl[3]]]}
for (p_, nm, wx, width, pl) in sides:
    win = [{"at": wx, "width": "winW", "sill": "fh + winSill", "springing": "fh + winSpring", "head": {"profile": "semicircular"}}]
    lands = [p_ + 4 * k for k in range(3) if p_ + 4 * k < top_n]
    if p_ > 1:
        ops = [{"at": "S / 2", "width": 1.2, "sill": 0, "springing": 2.2, "head": {"profile": "semicircular"}}] if nm == "-x" else []
        d = wall(width, f"{p_ - 1} * fh", 0, pl, ops)
        if ops: d["_about"] = "the door, under the flight that passes 3.4m up"
        add(f"wall {nm} foot", d)
    full = [l for l in lands if (l - 1 + 4) <= top_n]
    rest = [l for l in lands if l not in full]
    d = wall(width, "storeyH", f"{p_ - 1} * fh", pl, win); d["repeat"] = {"count": len(full), "step": [0, "storeyH", 0, 0]}
    add(f"wall {nm} at the landings", d)
    end = (p_ - 1) + 4 * len(full)
    for l in rest:
        add(f"wall {nm} top", wall(width, f"{top_n - (l - 1)} * fh", f"{l - 1} * fh", pl, win)); end = top_n
    if end < top_n:
        add(f"wall {nm} head", wall(width, f"{top_n - end} * fh", f"{end} * fh", pl, []))
for k in ("belfry z", "belfry x"):
    add(k, old["parts"][k])
    for a in parts[k]["at"]: a[1] = "4 * fh * storeys"
add("square stair", {"type": "staircase", "rise": "rise", "run": "run", "soffit": "slab", "flight": "n", "width": "w",
   "landing": {"depth": "w", "width": "w"}, "times": "4 * storeys", "from": "right", "at": "w / 2",
   "_about": "one flight and its corner landing, twelve times, each turning right off its landing: round the well three times, the last landing flush with the top floor",
   "place": [["0 - S / 2 + w", 0, "0 - S / 2 + w / 2", 0]]})
add("top floor", {"type": "box", "width": "S - w", "length": "S - w", "height": "slab",
   "_about": "the platform the stair arrives on: all of the inside but the hatch the last flight and a half come up through (the corner where it arrives is the stair's own last landing)",
   "at": [["w / 2", "4 * fh * storeys - slab", "0 - w / 2", 0]]})
add("top floor by the hatch", {"type": "box", "width": "w + 6 * run", "length": "w", "height": "slab",
   "_about": "the strip over the flight before last, as far as it still has 2m of headroom under the slab: its first six steps",
   "at": [["S / 2 - (w + 6 * run) / 2", "4 * fh * storeys - slab", "S / 2 - w / 2", 0]]})
add("square roof", old["parts"]["square roof"]); parts["square roof"]["at"][0][1] = "4 * fh * storeys + belfryH"
# ---- round towers: a spiral inside, windows where it passes each bay, a hatch in the floor it arrives on
turn = 12
perTurn = round(360 / turn)
win = {"width": 0.5, "sill": 1.0, "springing": 1.8, "head": {"profile": "semicircular"}}
def round_tower(pre, X, sTop, top_param, winBays=(3, 6, 9)):
    n = round(sTop / 0.18); rise = sTop / n; turnRise = round(perTurn * rise, 4)
    def tread_at_bay(b):   # the stair is placed at yaw 180; ring bay b of 12 is centred at 30b degrees
        j = ((30 * b - 180) / turn) % perTurn
        return (math.floor(j) + 1) * rise
    ring = lambda h, y, bays, **kw: {"type": "ring", "count": 12, "rOuter": "R + rt", "rInner": "R", "height": h, "at": bays,
                                     "place": [[X, y, 0, 0]], **kw}
    add(f"{pre}wall", ring(top_param, 0, [b for b in range(1, 12) if b not in winBays], solid=True))
    add(f"{pre}door", ring(top_param, 0, [0], opening={"width": 1.0, "sill": 0, "springing": 1.75, "head": {"profile": "semicircular"}},
                           _about="low enough to pass under the stair, whose soffit crosses this bay 2.4m up"))
    for b in winBays:
        base = tread_at_bay(b) - 0.2
        if base < 0: base += turnRise
        base = round(base, 4)
        m = 0
        while base + (m + 1) * turnRise <= sTop + 1e-9: m += 1
        if base > 1e-6: add(f"{pre}bay {b} foot", ring(base, 0, [b], solid=True))
        if m: add(f"{pre}bay {b} windows", ring(turnRise, base, [b], opening=win, repeat={"count": m, "step": [0, turnRise, 0, 0]}))
        y = round(base + m * turnRise, 4); rest = round(sTop - y, 4)
        if rest > 1e-6:
            add(f"{pre}bay {b} top", ring(rest, y, [b], opening=win) if rest >= 2.3 else ring(rest, y, [b], solid=True))
    add(f"{pre}spiral", {"type": "spiral-stair", "radius": "R - 0.05", "newel": 0.25, "turn": "sTurn", "top": top_param, "rise": "sRise",
                         "soffit": 0.25, "postAbove": 3, "at": [[X, 0, 0, "3.14159265"]]})
    hatch = sorted((15 + j) % perTurn for j in range(n - 13, n))
    add(f"{pre}top floor", {"type": "ring", "count": perTurn, "rOuter": "R", "rInner": 0.25, "height": "slab", "y": f"{top_param} - slab", "turn": 0.5,
       "solid": True, "skip": hatch, "place": [[X, 0, 0, 0]],
       "_about": "one bay per step of the stair (sTurn degrees each), the 13 over its last steps left out: the hatch it arrives through, wherever it has less than 2m under the slab"})
    return ring

ring = round_tower("round ", "gap", 15.0, "rTop")
add("round belfry", old["parts"]["round belfry"]); parts["round belfry"]["y"] = "rTop"
add("round roof", old["parts"]["round roof"]); parts["round roof"]["at"][0][1] = "rTop + 3"
# ---- the gallery tower: the stair arrives in a top room with a door onto a gallery round the outside
params.update({"gTop": 12.6, "gRoom": 3.4, "gW": 1.3,
               "_gTop": "the gallery tower's top floor, where the stair arrives and the gallery runs round outside"})
ring = round_tower("gallery tower ", "gap * 2", 12.6, "gTop", winBays=(3, 9))
add("gallery tower room", ring("gRoom", "gTop", [b for b in range(12) if b != 6], opening={"width": 0.7, "sill": 0.9, "springing": 1.9, "head": {"profile": "semicircular"}},
                              _about="the room at the top, windows all round"))
add("gallery tower gallery door", ring("gRoom", "gTop", [6], opening={"width": 1.0, "sill": 0, "springing": 1.9, "head": {"profile": "semicircular"}},
                              _about="the door out onto the gallery, on the far side from the one at the foot"))
add("gallery", {"type": "ring", "count": 24, "rOuter": "R + rt + gW", "rInner": "R + rt", "height": 0.3, "y": "gTop - 0.3", "solid": True,
                "place": [["gap * 2", 0, 0, 0]], "_about": "the gallery: a walk round the outside, level with the top floor"})
add("gallery parapet", {"type": "ring", "count": 24, "rOuter": "R + rt + gW", "rInner": "R + rt + gW - 0.2", "height": 1.0, "y": "gTop", "solid": True,
                        "place": [["gap * 2", 0, 0, 0]]})
add("gallery corbels", {"type": "box", "width": 0.35, "length": "gW", "height": 0.7,
                        "spiral": {"count": 16, "radius": "R + rt + gW / 2", "x": "gap * 2", "y": "gTop - 1.0"},
                        "_about": "the corbels the gallery stands on, one every sixteenth of the way round"})
add("gallery tower roof", {"type": "dome", "sides": 12, "radius": "R + rt + 0.3", "thickness": 0, "head": {"profile": "trigonal", "rise": "R * 1.8"},
                           "at": [["gap * 2", "gTop + gRoom", 0, 0]]})

d = {"name": "Towers with stairs",
 "_about": "STAIRS FITTED INSIDE TOWERS, and the towers fitted to their stairs. The square one climbs round an open well: a flight along each wall, turning on a corner landing, four to a storey -- ONE flight with `times` -- and arrives flush with a top floor cut away only where the last flight and a half need headroom. Its walls are built in pieces that start where the landings are, so every landing has a slit window beside it and no window falls halfway up a flight. The third is the common viewing tower: its spiral arrives through a hatch in a top room, and a door leads out onto a GALLERY that runs round the outside on corbels, behind a parapet. The round one holds a spiral wound to fill it, starting across from the door; its windows are staggered up the helix, each where the stair passes that bay, and it arrives through a hatch in the top floor (one floor bay per step, the ones over its last thirteen steps left out). The numbers are chained: ten 17cm risers on 32cm treads make a flight exactly as long as a wall between two landings.",
 "params": params, "build": build, "parts": parts}
open(p, 'w').write(json.dumps(d, indent=2) + "\n")
