#!/usr/bin/env python3
# THE STANDING STAG (2026-11-03): a red stag standing four-square, head up, its antlers spread -- the gilt stags beside
# Drachenburg's Freitreppe on the Venusterrasse, any park's or hunting lodge's. Carved as the couchant lion is (lion.py):
# lofts -- the body along its length; the neck, the legs and the antlers' beams up (axis y, their middles drifting as
# they rise); the head, the brow tines along it; the ears out to the sides. In metres for a life-size stag (shoulder
# 1.2 m) times `S`; +z its front, its hooves on the component's floor (stand it on a pedestal).
#   python3 tools/archgen/stag.py   ->   assets/architecture/components/standing-stag.json
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
add("body", loft("z", [sec(-.66, 0, 1.0, .1, .12), sec(-.58, 0, 1.0, .19, .21), sec(-.4, 0, .98, .22, .25), sec(-.1, 0, .97, .21, .27),
                       sec(.18, 0, 1.0, .21, .3), sec(.36, 0, 1.03, .18, .28), sec(.46, 0, 1.08, .1, .18)], sides=16, smooth=3,
                 about="the body: the rump, the barrel, the deep chest"))
add("neck", loft("y", [sec(.9, 0, .3, .14, .2), sec(1.15, 0, .4, .12, .15), sec(1.4, 0, .5, .1, .12), sec(1.6, 0, .58, .085, .1), sec(1.7, 0, .61, .08, .09)],
                 sides=12, about="the neck carried high, thick with the rut's mane at its foot"))
add("head", loft("z", [sec(.54, 0, 1.68, .075, .09), sec(.64, 0, 1.7, .08, .09), sec(.75, 0, 1.65, .06, .065), sec(.85, 0, 1.59, .045, .05),
                       sec(.89, 0, 1.575, .03, .035), sec(.91, 0, 1.57, .01, .01)], sides=12,
                 about="the head, the long face, the muzzle"))
for side, sx in (("right", 1), ("left", -1)):
    ear = [sec(.05, .6, 1.76, .035, .02), sec(.15, .58, 1.81, .035, .018), sec(.21, .56, 1.84, .012, .008)]
    add(f"ear {side}", loft("x", ear if sx > 0 else [dict(q, s=S(-float(q["s"].split(" ")[0]))) for q in reversed(ear)], sides=8,
                            about="an ear, out and up"))
    add(f"foreleg {side}", loft("y", [sec(0, sx * .11, .34, .03, .035), sec(.1, sx * .11, .34, .025, .03), sec(.3, sx * .11, .34, .028, .03),
                                      sec(.48, sx * .11, .33, .04, .045), sec(.7, sx * .11, .32, .055, .07), sec(.9, sx * .12, .3, .08, .11),
                                      sec(1.0, sx * .12, .3, .09, .12)], sides=10, about="a foreleg, the knee, the shoulder"))
    add(f"hindleg {side}", loft("y", [sec(0, sx * .11, -.48, .03, .035), sec(.1, sx * .11, -.48, .025, .03), sec(.32, sx * .11, -.52, .028, .035),
                                      sec(.48, sx * .11, -.57, .04, .06), sec(.66, sx * .12, -.52, .06, .1), sec(.86, sx * .13, -.48, .1, .16),
                                      sec(1.02, sx * .12, -.47, .12, .17)], sides=10, about="a hind leg, the hock, the haunch"))
    add(f"antler {side}", loft("y", [sec(1.74, sx * .06, .62, .028, .028), sec(1.95, sx * .17, .58, .025, .025), sec(2.2, sx * .28, .52, .022, .022),
                                     sec(2.45, sx * .35, .46, .019, .019), sec(2.62, sx * .34, .45, .014, .014), sec(2.72, sx * .3, .47, .004, .004)],
                               sides=8, about="an antler's beam, up and out and back"))
    add(f"brow tine {side}", loft("z", [sec(.6, sx * .1, 1.84, .015, .015), sec(.7, sx * .13, 1.88, .012, .012), sec(.78, sx * .14, 1.95, .004, .004)],
                                  sides=6, about="the brow tine, forward over the face"))
    add(f"trez tine {side}", loft("z", [sec(.49, sx * .28, 2.2, .013, .013), sec(.6, sx * .31, 2.27, .01, .01), sec(.67, sx * .32, 2.34, .003, .003)],
                                  sides=6, about="the tine half-way up, forward"))
    add(f"crown {side}", loft("y", [sec(2.5, sx * .36, .45, .013, .013), sec(2.62, sx * .42, .38, .01, .01), sec(2.72, sx * .45, .34, .003, .003)],
                              sides=6, about="the crown's points at the top"))
add("tail", loft("z", [sec(-.74, 0, .98, .02, .03), sec(-.7, 0, 1.0, .035, .05), sec(-.64, 0, 1.02, .04, .05)], sides=8, about="the short tail"))

doc = {"name": "Standing stag",
       "_about": "A STANDING STAG: a red stag four-square, head up, antlers spread -- the gilt stags beside Drachenburg's Freitreppe. Carved in lofts as the couchant lion is: the body, the neck, the head, the ears, the legs, the antlers' beams with their brow, trez and crown tines. `S` its size against a life-size stag (shoulder 1.2 m); it faces +z, its hooves on the floor (stand it on a pedestal). Generated by tools/archgen/stag.py.",
       "params": {"detail": 4, "S": 1.0, "_S": "its size: 1 a life-size red stag, its shoulder 1.2 m"},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/components/standing-stag.json"), "w").write(json.dumps(doc, indent=2) + "\n")
print("standing-stag:", len(parts), "parts")
