# THE SUMMER PALACE (Yiheyuan), Beijing (1750 as the Garden of Clear Ripples; rebuilt 1886-1895): the central axis of
# Longevity Hill, from the shore of Kunming Lake up to the hill's top -- the Yunhui Yuyu pailou on the lakeshore, the
# LONG CORRIDOR (Changlang) passing behind it along the lake, the Paiyun Gate, the Second Gate, the HALL OF DISPELLING
# CLOUDS (Paiyun Dian) in its court between its side and ear halls, the Hall of Moral Glory (Dehui Dian), the TOWER OF
# BUDDHIST INCENSE (Foxiang Ge) on its great stone terrace, and on the top the Sea of Wisdom (Zhihuihai) behind its
# glazed pailou (Zhongxiangjie).
#   The plan is OpenStreetMap's, its axis (four degrees off north) turned to run north-south: the Foxiang Ge at the
#   origin, the halls on the axis south of it at their mapped distances -- the Dehui Hall 39m, the Paiyun Dian 69m,
#   the Second Gate (moved 5m south to clear its flight) 112m, the Paiyun Gate 144m; the Sea of Wisdom 47m north.
#   The HILL is its terraces, prisms one behind another (3, 7 and 12m), the flights up between them on the axis and,
#   past the Paiyun Dian, either side of it; the FOXIANG GE stands on a stone terrace 19m over the Dehui Hall's (a
#   flight up each of its sides, and on along the summit's sides beyond), the summit 50m over the lake.
#   The TOWER is a `tiered` part on an octagonal plan (tiered.js `sides`): four storeys set in one above another, the
#   lowest its gallery, three skirts and the top on the jujia section seated on their walls (the four eaves of the
#   real tower; 36m to the jewel, the real one 41m), bracket sets along every face, floors and steep stairs inside.
#   The HALLS and GATES are components/chinese-hall; the PAILOUS columns, beams and three roofs of their own; the
#   CORRIDOR a roofed `range`, open between its posts both sides.
#   East is +x, south is +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2
r4 = lambda v: round(v, 4)

# ---- the hill: its terraces, front to back ------------------------------------------------------------------------
Y1, Y2, Y3, Y4, Y5 = 3.0, 7.0, 12.0, 31.0, 50.0     # the Second Gate's, the Paiyun Dian's, the Dehui Hall's, the tower's, the summit's
ZB = -70.0                                           # the hill's back (the terraces' far edge)
def terrace(name, x0, x1, z0, z1, h, about):
    add(name, {"type": "prism", "plan": {"rect": [r4(x1 - x0), r4(z1 - z0)]}, "height": h, "walked": True,
               "at": [[r4((x0 + x1) / 2), 0, r4((z0 + z1) / 2), 0]], "_about": about})
terrace("second terrace", -55, 55, ZB, 120, Y1, "the hill's first step, behind the Paiyun Gate: the Second Gate's court")
terrace("paiyun terrace", -48, 48, ZB, 95, Y2, "the Paiyun Dian's court")
terrace("dehui terrace", -40, 40, ZB, 52, Y3, "the Dehui Hall's terrace, at the foot of the tower's")
terrace("foxiang terrace", -20, 20, -20, 20, Y4, "the great stone terrace of the Foxiang Ge, 19m over the Dehui Hall's")
terrace("summit", -20, 20, -62, -20, Y5, "the top of Longevity Hill behind the tower")

# flights, climbing north (-z): yaw pi/2 lays one over x - width .. x from its `at`, its foot there
def flight(name, x, z, w, base, top, rise, run=.3, ground=None, about=None):
    n = max(1, round((top - base) / rise)); L = n * run
    d = {"type": "flight", "width": w, "run": run, "rise": r4((top - base) / n), "base": base, "top": top, "landing": 0,
         "at": [[r4(x + w / 2), 0, r4(z), Q]]}
    if ground is not None: d["ground"] = ground
    if about: d["_about"] = about
    add(name, d)
    return z - L
flight("first flight", 0, 126.4, 6.0, 0, Y1, .15, .32, about="up from the Paiyun Gate's court to the Second Gate's")
flight("second flight", 0, 102.5, 6.0, Y1, Y2, .16, about="up from the Second Gate to the Paiyun Dian's court")
for sx, nm in ((1, "east"), (-1, "west")):
    flight(f"dehui flight {nm}", sx * 18.0, 61.3, 3.0, Y2, Y3, .16, ground=Y2, about="up past the Paiyun Dian to the Dehui Hall's terrace")
    # along the tower terrace's side, then on along the summit's: a landing at each top
    zl = flight(f"foxiang flight {nm}", sx * 21.5, 20.0, 3.0, Y3, Y4, .17, ground=Y3, about="up the side of the tower's terrace")
    add(f"foxiang landing {nm}", {"type": "prism", "plan": {"rect": [3.0, r4(zl + 20)]}, "height": Y4, "walked": True,
                                  "at": [[r4(sx * 21.5), 0, r4((zl - 20) / 2), 0]]})
    zs = flight(f"summit flight {nm}", sx * 21.5, -20.0, 3.0, Y4, Y5, .17, ground=Y3, about="on up the summit's side to the Sea of Wisdom")
    add(f"summit landing {nm}", {"type": "prism", "plan": {"rect": [3.0, r4(zs + 62)]}, "height": Y5, "walked": True,
                                 "at": [[r4(sx * 21.5), 0, r4((zs - 62) / 2), 0]]})

# ---- the halls and gates (components/chinese-hall: the front +z, the long axis x) --------------------------------
HALL = {"s": .8, "over": 2.2, "pitch": 36}
add("paiyun gate", comp("components/chinese-hall", {**HALL, "nx": 5, "bw": 4.2, "nz": 2, "bd": 3.6, "H": 4.6, "plat": .9, "platOut": 1.8, "backSill": 0},
                        [[0, 0, 143.5, 0]], _about="the Paiyun Gate: five bays, its middle bay the way through"))
add("second gate", comp("components/chinese-hall", {**HALL, "nx": 3, "bw": 3.6, "nz": 2, "bd": 3.0, "H": 4.2, "plat": .6, "platOut": 1.5, "backSill": 0,
                                                    "over": 1.8},
                        [[0, Y1, 112.0, 0]], _about="the Second Gate (Ergongmen), into the Paiyun Dian's court"))
add("paiyun dian", comp("components/chinese-hall", {**HALL, "nx": 5, "bw": 5.3, "nz": 3, "bd": 6.4, "H": 7.0, "plat": 1.6, "platOut": 2.4,
                                                    "s": 1.0, "over": 2.6, "pitch": 38},
                        [[0, Y2, 69.4, 0]], _about="the Hall of Dispelling Clouds (Paiyun Dian), where the Empress Dowager kept her birthdays"))
add("ear halls", comp("components/chinese-hall", {**HALL, "nx": 3, "bw": 3.6, "nz": 2, "bd": 4.0, "H": 4.6, "plat": .8, "platOut": 1.2, "over": 1.8},
                      [[26.4, Y2, 64.0, 0], [-26.4, Y2, 64.0, 0]], _about="the ear halls either side of the Paiyun Dian"))
add("side halls", comp("components/chinese-hall", {**HALL, "nx": 4, "bw": 4.0, "nz": 2, "bd": 4.5, "H": 5.0, "plat": .8, "platOut": 1.5},
                       [[30.0, Y2, 84.0, -Q], [-30.0, Y2, 84.0, Q]],
                       _about="the side halls facing across the court: the Zixiao Dian east, the Fanghui Dian west"))
add("dehui hall", comp("components/chinese-hall", {**HALL, "nx": 5, "bw": 4.3, "nz": 2, "bd": 5.3, "H": 6.0, "plat": .8, "platOut": 1.6, "backSill": 0,
                                                   "s": .9, "over": 2.4},
                       [[0, Y3, 38.6, 0]], _about="the Hall of Moral Glory (Dehui Dian), at the foot of the tower's terrace"))
add("sea of wisdom", comp("components/chinese-hall", {**HALL, "nx": 7, "bw": 4.1, "nz": 2, "bd": 7.0, "H": 9.0, "plat": .6, "platOut": 1.4,
                                                      "s": .9, "over": 2.0, "pitch": 34},
                          [[0, Y5, -46.5, 0]], _about="the Sea of Wisdom (Zhihuihai): the beamless hall on the summit, its walls faced in glazed tiles"))

# ---- the Foxiang Ge: its plinth, the tower -------------------------------------------------------------------------
PL, PR = 1.2, 12.0
add("foxiang plinth", {"type": "prism", "plan": {"sides": 8, "radius": PR}, "height": PL, "walked": True, "at": [[0, Y4, 0, 0]],
                       "_about": "the tower's octagonal marble plinth on the terrace"})
flight("foxiang steps", 0, r4(PR * math.cos(math.pi / 8) + 8 * .3), 4.0, Y4, Y4 + PL, .15, ground=Y4, about="up to the tower's plinth")
add("foxiang ge", {"type": "tiered", "sides": 8,
                   "storeys": [{"r": 9.8, "h": 7.5}, {"r": 7.8, "h": 7.0}, {"r": 6.2, "h": 6.5}, {"r": 4.8, "h": 6.0}],
                   "wall": {"t": .35}, "windows": {"every": 2.4, "width": 1.2, "end": 1.0, "sill": 1.2, "springing": 3.0, "head": {"profile": "flat"}},
                   "roof": {"lo": .3, "hi": 1.0, "overhang": 2.0, "t": .35}, "top": {"lo": .4, "hi": 1.3, "overhang": 2.2},
                   "brackets": {"s": .6, "every": 1.6}, "door": {"side": "s", "width": 2.4, "height": 3.2},
                   "finial": {"height": 2.4, "radius": .22, "rings": 0, "base": 1.4},
                   "at": [[0, Y4 + PL, 0, 0]],
                   "_about": "the Tower of Buddhist Incense: four octagonal storeys under three skirts and the top, the lowest its gallery; "
                             "bracket sets along every face, the gilt jewel on the point"})

# ---- the pailous: four columns, the beams across, three roofs, the middle one high --------------------------------
def pailou(name, x, y, z, span, H, about):
    b = span / 3
    add(f"{name} columns", {"type": "column", "radius": .36, "height": H, "sides": 12,
                            "at": [[r4(x + sx * span / 2), y, z, 0] for sx in (-1, 1)], "_about": about})
    add(f"{name} middle columns", {"type": "column", "radius": .4, "height": r4(H + 1.6), "sides": 12,
                                   "at": [[r4(x + sx * b / 2), y, z, 0] for sx in (-1, 1)]})
    add(f"{name} beam", {"type": "box", "width": r4(span + .8), "length": .6, "height": 1.0, "at": [[x, r4(y + H - 1.0), z, 0]]})
    add(f"{name} middle beam", {"type": "box", "width": r4(b + .8), "length": .6, "height": 1.0, "at": [[x, r4(y + H + .6), z, 0]]})
    add(f"{name} plaque", {"type": "box", "width": r4(b * .55), "length": .72, "height": 1.1, "at": [[x, r4(y + H - 2.1), z, 0]]})
    add(f"{name} side roofs", {"type": "roof", "form": "gablet", "width": 2.0, "length": r4(b + .9), "pitch": 32, "overhang": .6, "hipH": .5,
                               "at": [[r4(x + sx * b), r4(y + H), z, Q] for sx in (-1, 1)]})
    add(f"{name} middle roof", {"type": "roof", "form": "gablet", "width": 2.2, "length": r4(b + 1.8), "pitch": 32, "overhang": .7, "hipH": .5,
                                "at": [[x, r4(y + H + 1.6), z, Q]]})
pailou("yunhui pailou", 0, 0, 172.0, 18.0, 7.0, "the Yunhui Yuyu pailou on the lakeshore, the axis's beginning")
pailou("zhongxiang pailou", 0, Y5, -31.0, 12.0, 5.6, "the glazed pailou Zhongxiangjie before the Sea of Wisdom")

# ---- the lakeshore: the Long Corridor, the embankment, the lake ----------------------------------------------------
ZC = 160.0
add("long corridor", {"type": "range", "path": [[-110.0, ZC], [110.0, ZC]], "width": 4.2, "height": 2.9, "thickness": .3,
                      "faces": {"out": {"every": 3.4, "width": 2.8, "end": .9, "sill": 0, "springing": 2.5, "head": {"profile": "flat"}},
                                "in": {"every": 3.4, "width": 2.8, "end": .9, "sill": 0, "springing": 2.5, "head": {"profile": "flat"}},
                                "end": []},
                      "roof": {"pitch": 26, "overhang": .9, "shell": .3}, "interior": False,
                      "_about": "the Long Corridor along the lake (728m; a stretch of it here): open between its posts both sides, its beams painted -- a covered walk, the open air's (no interior)"})
add("embankment", {"type": "prism", "plan": {"rect": [240.0, 4.0]}, "height": .5, "walked": True, "at": [[0, 0, 179.0, 0]],
                   "_about": "the stone embankment along Kunming Lake"})
add("kunming lake", {"type": "prism", "plan": {"rect": [240.0, 36.0]}, "height": .08, "at": [[0, 0, 199.0, 0]],
                     "_about": "the shallows of Kunming Lake"})

doc = {
    "name": "Summer Palace",
    "_about": "THE SUMMER PALACE (Yiheyuan, rebuilt 1886-1895): the central axis of Longevity Hill from Kunming Lake to the top -- the "
              "lakeshore pailou, the Long Corridor, the Paiyun Gate, the Second Gate, the Hall of Dispelling Clouds between its side "
              "and ear halls, the Dehui Hall, the octagonal TOWER OF BUDDHIST INCENSE (a `tiered` part on `sides` 8: its skirts jujia "
              "domes seated on the walls) on its stone terrace, the Sea of Wisdom on the summit; the hill its terraces, flights between. "
              "After OpenStreetMap, the axis turned to north. Generated by tools/archgen/summer_palace.py -- edit the script for "
              "arithmetic changes. East is +x, south +z.",
    "params": {"detail": 4},
    "base": {"height": .3, "steps": 1, "stepOut": .5, "margin": 6},
    "railing": {"type": "stone", "height": .9},
    "build": build,
    "parts": parts,
}
out = os.path.join(ROOT, "assets", "architecture", "summer-palace.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts")
