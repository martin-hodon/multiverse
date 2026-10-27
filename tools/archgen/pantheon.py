import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, math
p = os.path.join(ROOT, 'assets/architecture/pantheon.json')
d = json.load(open(p))
P = d["params"]; old = d["parts"]
P.update({"floor": 0.6, "intColH": 10.2, "intEntH": 2.2, "atticH": "springH - floor - intColH - intEntH", "atticT": 0.5,
          "_floor": "the rotunda and portico floors stand on a podium: three steps up from the square",
          "_intColH": "the interior order: the columns screening the niches and the entablature they carry round the room",
          "_atticH": "the attic zone between that entablature and the dome's springing, with its blind windows"})
parts = {}; build = []
def add(n, dd): parts[n] = dd; build.append(n)
ring = lambda **kw: {"type": "ring", "place": [[0, 0, 0, 0]], **kw}
# ---- the floor, laid first: the niches stand on it
add("rotunda floor", ring(count=24, rOuter="R + nicheT", rInner=0.5, height="floor", solid=True,
                          _about="the rotunda's floor on its podium (a ring round a drain at the middle, where the rain through the oculus goes)"))
add("drain", {"type": "column", "radius": 0.5, "height": "floor - 0.05", "sides": 12, "at": [[0, 0, 0, 0]]})
# ---- the rotunda, lower zone: niches cut in the inner layer, to the top of the interior entablature
lowH = "floor + intColH + intEntH"
# (the niche layer STANDS ON the floor: a floor edge against a wall face is two faces in one place)
add("niches", ring(count=8, rOuter="R + nicheT", rInner="R", height="intColH + intEntH", y="floor", at=[1, 2, 3, 5, 6, 7],
                   opening={"width": 8.6, "sill": 0, "springing": "intColH", "head": {"profile": "flat"}},
                   _about="six exedrae, square-headed under the entablature their columns carry"))
add("entrance and apse", ring(count=8, rOuter="R + nicheT", rInner="R", height="intColH + intEntH", y="floor", at=[0, 4],
                   opening={"width": 8.6, "sill": 0, "springing": "intColH + intEntH - 0.4", "head": {"profile": "flat"}},
                   _about="the entrance bay and the apse opposite it: open the full height of the order, the entablature broken over them"))
add("attic inner", ring(count=16, glass=False, rOuter="R + atticT", rInner="R", height="atticH", y=lowH,
                        opening={"width": 2.2, "sill": 2.2, "springing": 5.2, "head": {"profile": "flat"}},
                        _about="the attic zone: a blind window in every bay (their backs are the wall behind)"))
add("attic back", ring(count=16, rOuter="R + nicheT", rInner="R + atticT", height="atticH", y=lowH, solid=True))
# THE DRUM'S THREE ZONES OUTSIDE are its COURSES (arch/courses.js), the ring's own: a cornice at the attic's level and
# one crowning the wall at the springing, round the wall and its entrance bay alike; a third crowning the drum
wallC = {"plinth": False, "strings": {"at": [12.4], "h": 0.6, "out": 0.5, "profile": "cornice"}, "cornice": {"h": 0.9, "out": 0.75}}
add("outer wall", {**old["outer wall"], "courses": wallC})
ent = old["entrance"]; ent["opening"] = {**ent["opening"], "sill": "floor", "springing": "floor + 7.5"}; ent["glass"] = False; add("entrance", {**ent, "courses": wallC})
add("drum", {**old["drum"], "courses": {"plinth": False, "strings": False, "cornice": {"h": 0.8, "out": 0.6}}})
# ---- interior order
bayA = 2 * math.pi / 8
colAt = []
for b in [1, 2, 3, 5, 6, 7]:
    for s in (-1, 1):
        a = b * bayA + s * 2.3 / 21.7
        colAt.append([f"{21.7 * math.sin(a):.4f}", "floor", f"{21.7 * math.cos(a):.4f}", f"{a:.6f}"])
add("niche columns", {"type": "colonnade", "order": "corinthian", "count": 1, "spacing": 1, "columnR": 0.55, "height": "intColH",
                      "at": colAt, "_about": "the pair of columns screening each exedra"})
add("interior entablature", ring(count=8, rOuter="R + nicheT", rInner="R - 0.7", height="intEntH", y="floor + intColH", at=[1, 2, 3, 5, 6, 7], solid=True,
                                 _about="the entablature round the room, carried across each exedra by its columns and broken over the entrance and the apse"))
add("aediculae", {"type": "box", "width": 3.0, "length": 1.4, "height": 2.2,
                  "spiral": {"count": 8, "radius": "R - 0.7", "turn": 0.3927, "y": "floor"},
                  "_about": "the eight aediculae between the exedrae: a podium..."})
add("aedicula columns", {"type": "colonnade", "order": "corinthian", "count": 2, "spacing": 2.2, "columnR": 0.25, "height": 3.6,
                         "entablature": {"h": 0.6, "depth": 1.0}, "spiral": {"count": 8, "radius": "R - 1.0", "turn": 0.3927, "y": "floor + 2.2"},
                         "_about": "...two columns on it and their entablature..."})
add("aedicula pediments", {"type": "roof", "form": "gable", "width": 3.0, "length": 1.2, "pitch": 22,
                           "spiral": {"count": 8, "radius": "R - 1.0", "turn": 0.3927, "y": "floor + 6.4"},
                           "_about": "...and a pediment on top"})
# ---- dome and its outside
add("dome", old["dome"])
# THE STEP RINGS round the dome's haunches start where the dome's outer surface is at their FOOT -- sqrt(domeR^2 - h^2)
# at their lowest height over the springing -- divided by cos 7.5 (a ring bay's face is a flat chord between its
# corners, nearer the axis than they are): set by their tops, they cut through the shell into the coffers.
import math as _m
for i, k in enumerate(("step 1", "step 2", "step 3")):
    part = dict(old[k]); h0 = 7.8 + 1.5 * i
    part["rInner"] = round(_m.sqrt(23.0 ** 2 - h0 ** 2) / _m.cos(_m.pi / 24), 3)
    add(k, part)
# ---- portico on its podium
add("portico steps", {"type": "crepidoma", "width": "portW", "length": "portD", "steps": 3, "stepH": 0.2, "stepOut": 0.6,
                      "at": [[0, 0, "portZ0 + portD / 2", 0]], "_about": "the portico's podium: three steps up from the square"})
blk = old["intermediate block"]; blk["openings"][0]["sill"] = "floor"; blk["openings"][0]["springing"] = "floor + 7.5"; blk["openings"][0]["glass"] = False; add("intermediate block", blk)
add("passage floor", {"type": "box", "width": 4.4, "length": "portZ0 - R - wallT + 9.2", "height": "floor",
                      "at": [[0, 0, "(portZ0 + R + wallT - 9.2) / 2 + 0.2", 0]], "_about": "the floor through the door, level with the portico's and the rotunda's"})
add("front columns", {**old["front columns"], "order": "corinthian", "at": [[0, "floor", "portZ0 + portD - 1.3", 0]]})
ic = old["inner columns"]; add("inner columns", {**ic, "order": "corinthian", "at": [[a[0], "floor", a[2], a[3]] for a in ic["at"]]})
add("portico ceiling", {**old["portico ceiling"], "at": [[0, "floor + colH", "portZ0 + portD / 2", 0]],
                        "_about": "the portico's entablature and the ceiling behind it, one block"})
add("portico cornice", {"type": "box", "width": "portW + 1.0", "length": "portD + 0.5", "height": 0.7,
                        "at": [[0, "floor + colH + entH", "portZ0 + portD / 2 + 0.25", 0]]})
add("pediment", {**old["pediment"], "at": [[0, "floor + colH + entH + 0.7", "portZ0 + portD / 2 + 0.25", 0]]})
# ---- the statues of the gods (statuary.py, statues.js): one in each of the six exedrae against its back wall on a
# pedestal, a greater one in the apse facing the door, and one in each of the eight aediculae on its podium between
# its columns -- Roman, in marble, every one turned to the middle of the rotunda
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from statuary import statue, pedestal, capped
for k in [k for k in parts if k.startswith("statue ") or k.startswith("pedestal ")]: del parts[k]; build.remove(k)
inward = lambda a: math.atan2(math.cos(a), -math.sin(a))   # (the figure's turn to look at the middle from angle a)
gods = []
for i, b in enumerate([1, 2, 3, 5, 6, 7]):
    a = b * bayA; r = 21.7 + 2.0 - 0.9
    gods.append((f"exedra {b}", (r * math.sin(a), 0.6, r * math.cos(a)), 1.9, 1.0, 1.3, a, i))
a = 4 * bayA; r = 21.7 + 2.0 - 1.1
gods.insert(0, ("apse", (r * math.sin(a), 0.6, r * math.cos(a)), 2.4, 1.2, 2.0, a, 9))
for k in range(8):
    a = k * bayA + 0.3927; r = 21.7 - 1.0
    gods.append((f"aedicula {k}", (r * math.sin(a), 0.6 + 2.2, r * math.cos(a)), 1.2, 0, 0, a, 20 + k))
stat = {}
for name, (x, y, z), sc, ph, pw, a, seed in gods:
    if ph: stat[f"pedestal {name}"] = pedestal((x, y, z), pw, pw, ph, f"the pedestal in the {name}")
    stat[f"statue {name}"] = statue((x, y + ph, z), kind="woman" if seed % 3 == 1 else "man", style="roman", stone="marble", scale=sc, seed=seed, face=round(inward(a), 4),
                                    **({"hold": {"R": "items/weapons/spear"}} if seed % 4 == 0 else {}))
for k, v in capped(stat).items(): add(k, v)
d["parts"] = parts; d["build"] = build
d["_about"] = ("THE PANTHEON at its real size, from the engine's primitives. The rotunda is 43.3m across inside and as high to its crown, so a sphere "
  "would fit it: a wall 6.2m thick in layers. Inside, the order: six exedrae each screened by a pair of Corinthian columns carrying an "
  "entablature round the room (broken over the entrance and the apse opposite it), eight aediculae between them -- a podium, two columns, a "
  "pediment -- and above, the attic zone with a blind window in every bay, up to the springing. The dome is a hemisphere with the 9m oculus, "
  "five rows of twenty-eight coffers sunk along the line of sight from the middle of the floor. Outside, two cornices band the drum and three "
  "step rings hold the dome's haunches. In front, the intermediate block (the door through it, flat on top) and the portico on its three "
  "steps: eight Corinthian columns 14.15m tall across the front, two rows of four behind making three aisles, the entablature and its "
  "cornice, and the low pediment.")
open(p, 'w').write(json.dumps(d, indent=2) + "\n")
