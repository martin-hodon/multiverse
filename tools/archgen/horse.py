#!/usr/bin/env python3
# THE EQUESTRIAN STATUE (2026-11-03): a horse at the walk, head up, one foreleg lifted, and its rider seated on it -- the
# bronzes over Sacre-Coeur's porch (Joan of Arc and Saint Louis, Hippolyte Lefebvre), any square's king on horseback.
# The horse is carved as the stag is (stag.py): lofts -- the body along its length; the neck, the legs up (axis y, their
# middles drifting as they rise); the head along its length, the mane down the neck's crest, the tail. The rider is a
# `statue` marker (statues.js: a seated figure on its seat, the saddle), its legs down the horse's flanks lofts of their
# own, a stirrup under each boot. In metres for a horse of 1.6 m at the withers times `S`; +z its front, its hooves on
# the component's floor (stand it on a pedestal or a pier).
#   python3 tools/archgen/horse.py   ->   assets/architecture/components/equestrian.json
import os, json

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
r4 = lambda v: round(v, 4)
S = lambda v: f"{r4(v)} * S" if v else 0


def sec(s, u, v, a, b, n=2.0):
    return {"s": S(s), "u": S(u), "v": S(v), "a": S(a), "b": S(b), "n": n}


def loft(axis, secs, sides=12, smooth=2, about=None):
    d = {"type": "loft", "axis": axis, "sides": sides, "smooth": smooth, "sections": secs, "at": [[0, 0, 0, 0]]}
    if about: d["_about"] = about
    return d


parts, build = {}, []
def add(n, d): parts[n] = d; build.append(n)

# (axis z: u is x, v is y; axis y: u is x, v is z; axis x: u is z, v is y)
add("body", loft("z", [sec(-.92, 0, 1.24, .1, .12), sec(-.84, 0, 1.25, .24, .26), sec(-.62, 0, 1.24, .3, .33), sec(-.3, 0, 1.18, .31, .36),
                       sec(.05, 0, 1.17, .31, .37), sec(.38, 0, 1.24, .29, .37), sec(.6, 0, 1.3, .24, .33), sec(.74, 0, 1.33, .12, .2)],
                 sides=18, smooth=3, about="the body: the croup, the barrel under the saddle, the deep chest"))
add("neck", loft("y", [sec(1.2, 0, .52, .17, .3), sec(1.45, 0, .66, .14, .23), sec(1.7, 0, .79, .11, .17), sec(1.92, 0, .9, .085, .13),
                       sec(2.06, 0, .96, .075, .1)], sides=12, about="the neck, arched and carried high"))
add("head", loft("z", [sec(.86, 0, 2.1, .08, .12), sec(.98, 0, 2.06, .085, .12), sec(1.12, 0, 1.95, .075, .095), sec(1.26, 0, 1.83, .065, .075),
                       sec(1.36, 0, 1.75, .06, .07), sec(1.42, 0, 1.71, .045, .05), sec(1.44, 0, 1.7, .01, .01)], sides=12,
                 about="the head, the long face down to the muzzle"))
add("mane", loft("y", [sec(1.42, 0, .5, .03, .07), sec(1.7, 0, .66, .035, .07), sec(1.95, 0, .79, .03, .06), sec(2.16, 0, .86, .02, .04)],
                 sides=8, about="the mane on the neck's crest"))
for side, sx in (("right", 1), ("left", -1)):
    ear = [sec(.05, .9, 2.17, .03, .02), sec(.12, .88, 2.24, .028, .016), sec(.17, .86, 2.29, .01, .006)]
    add(f"ear {side}", loft("x", ear if sx > 0 else [dict(q, s=S(-float(q["s"].split(" ")[0]))) for q in reversed(ear)], sides=8,
                            about="an ear, pricked"))
    # the near foreleg (right) lifted at the walk, its knee bent and its hoof back under it; the rest on the ground
    fore = ([sec(.34, .15, .74, .04, .045), sec(.42, .15, .67, .035, .04), sec(.56, .15, .6, .04, .05), sec(.68, .15, .56, .055, .065),
             sec(.9, .16, .52, .08, .1), sec(1.08, .16, .5, .1, .13), sec(1.2, .15, .5, .11, .15)] if sx > 0 else
            [sec(0, -.15, .55, .05, .055), sec(.06, -.15, .55, .035, .04), sec(.3, -.15, .54, .035, .04), sec(.48, -.15, .53, .05, .055),
             sec(.7, -.15, .52, .055, .065), sec(.9, -.16, .52, .08, .1), sec(1.08, -.16, .5, .1, .13), sec(1.2, -.15, .5, .11, .15)])
    add(f"foreleg {side}", loft("y", fore, sides=10, about="a foreleg: the hoof, the cannon, the knee, the forearm up into the shoulder"))
    add(f"hindleg {side}", loft("y", [sec(0, sx * .15, -.7, .05, .055), sec(.06, sx * .15, -.7, .035, .04), sec(.36, sx * .15, -.74, .035, .045),
                                      sec(.54, sx * .15, -.8, .05, .07), sec(.74, sx * .16, -.74, .07, .11), sec(1.0, sx * .17, -.66, .12, .19),
                                      sec(1.2, sx * .16, -.62, .14, .22)], sides=10, about="a hind leg: the hock, the gaskin, the haunch"))
    # the rider's leg down the flank: thigh from the saddle, knee forward, the boot in its stirrup
    add(f"rider leg {side}", loft("y", [sec(.86, sx * .36, .2, .06, .075), sec(1.0, sx * .37, .2, .07, .085), sec(1.18, sx * .36, .12, .075, .09),
                                        sec(1.36, sx * .33, .0, .09, .11), sec(1.56, sx * .27, -.08, .1, .12), sec(1.62, sx * .22, -.1, .08, .1)],
                                  sides=10, about="the rider's leg down the horse's flank, the knee at the saddle's flap"))
    add(f"rider boot {side}", loft("z", [sec(.14, sx * .36, .82, .055, .05), sec(.2, sx * .36, .84, .06, .06), sec(.34, sx * .36, .83, .045, .04)],
                                   sides=8, about="the boot in its stirrup"))
add("tail", loft("y", [sec(.55, 0, -1.08, .04, .05), sec(.85, 0, -1.07, .07, .07), sec(1.1, 0, -1.02, .06, .06), sec(1.3, 0, -.96, .05, .05)],
                 sides=10, about="the tail, hanging"))
add("saddle cloth", {"type": "loft", "axis": "z", "sides": 16, "smooth": 3, "at": [[0, 0, 0, 0]],
                     "sections": [sec(-.42, 0, 1.2, .33, .37), sec(-.2, 0, 1.17, .335, .38), sec(.1, 0, 1.17, .335, .38), sec(.3, 0, 1.2, .33, .375)],
                     "_about": "the saddle cloth over the barrel, hanging low"})
add("rider", {"type": "marker", "role": "statue", "at": [[0, "1.56 * S", "-0.12 * S", 0]],
              "data": {"kind": "kind", "style": "style", "stone": "stone", "pose": "pose", "scale": "S", "seed": "seed", "face": -1.5707963,
                       "hold": {"R": "holdR", "L": "holdL"}},
              "_about": "the rider, seated on the saddle (a statue: statues.js), facing the way the horse does"})

doc = {"name": "Equestrian statue",
       "_about": "AN EQUESTRIAN STATUE: a horse at the walk, its near foreleg lifted, head up, and its rider seated on it -- the bronzes of Joan of Arc and Saint Louis over Sacre-Coeur's porch, any king on horseback. The horse carved in lofts as the stag is (body, neck, head, mane, ears, legs, tail, the saddle cloth), the rider a seated `statue` marker (kind, style, pose, what each hand holds, its stone), its legs down the flanks and its boots in the stirrups lofts of their own. `S` its size against a life-size horse (1.6 m at the withers); it faces +z, its hooves on the floor (stand it on a pier). Generated by tools/archgen/horse.py.",
       "params": {"detail": 4, "S": 1.0, "_S": "its size: 1 a life-size horse, 1.6 m at the withers (and a life-size rider)",
                  "kind": "man", "style": "gothic", "stone": "bronze", "pose": "enthroned", "_pose": "the rider's pose: a seated one (enthroned: the right hand up, a sword raised)",
                  "seed": 1, "holdR": "items/weapons/sword", "holdL": ""},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/components/equestrian.json"), "w").write(json.dumps(doc, indent=2) + "\n")
print("equestrian:", len(parts), "parts")
