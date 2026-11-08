#!/usr/bin/env python3
# THE BAROQUE GARDEN SPHINX (2026-11-04): a lion's body lying on its plinth and a woman's bust rising from its chest --
# the sphinxes on the Belvedere's garden stairs in Vienna (c. 1720, Zogelsdorf stone), the Mirabell garden's, any baroque
# parterre's guardians of a flight. The lion's lofts are couchant-lion's (lion.py): the body, the folded haunches and hind
# paws, the forelegs stretched before it, the tail laid round the flank; in place of the mane, the woman's upright torso
# with its breasts and shoulders, the neck and the head under a cap of braided hair with a ribbon bow. In units of its
# length (rump to the paws' tips) times `S`; +z its front, standing on the plinth's top.
#   python3 tools/archgen/sphinx.py   ->   assets/architecture/components/sphinx.json
import os, json

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
r4 = lambda v: round(v, 4)
S = lambda v: f"{r4(v)} * S" if v else 0                       # a length in the sphinx's units
LIFT = "plinthH"                                               # (everything stands on the plinth's top)


def sec(s, u, v, a, b, n=2.2, b2=None, a2=None):
    q = {"s": S(s), "u": S(u), "v": S(v), "a": S(a), "b": S(b), "n": n}
    if b2 is not None: q["b2"] = S(b2)
    if a2 is not None: q["a2"] = S(a2)
    return q


def loft(secs, sides=14, smooth=2, axis="z", at=None, about=None):
    d = {"type": "loft", "axis": axis, "sides": sides, "smooth": smooth, "sections": secs, "at": at or [[0, LIFT, 0, 0]]}
    if about: d["_about"] = about
    return d


parts, build = {}, []
def add(n, d): parts[n] = d; build.append(n)

add("plinth", {"type": "box", "width": "S * 0.62", "length": "S * 1.12", "height": "plinthH", "at": [[0, 0, 0, 0]],
               "_about": "the block it lies on"})
# the lion: couchant-lion's body, haunches, forelegs and tail (lion.py), the chest a little narrower under the bust
add("body", loft([sec(-.49, 0, .17, .03, .04), sec(-.45, 0, .2, .15, .16), sec(-.33, 0, .21, .19, .2), sec(-.14, 0, .2, .16, .18),
                  sec(.04, 0, .23, .17, .21), sec(.13, 0, .25, .14, .19), sec(.19, 0, .26, .05, .07)], sides=18, smooth=3,
                 about="the lion's body lying along the plinth: the rump, the lean waist, the chest under the bust"))
for side, sx in (("right", 1), ("left", -1)):
    add(f"haunch {side}", loft([sec(-.46, sx * .14, .2, .02, .05), sec(-.39, sx * .16, .2, .08, .15), sec(-.27, sx * .18, .16, .08, .14),
                                sec(-.15, sx * .2, .07, .06, .07), sec(-.03, sx * .2, .04, .055, .04), sec(.02, sx * .2, .035, .02, .02)],
                               about="the haunch and the hind leg folded along the flank, the hind paw by the elbow"))
    add(f"foreleg {side}", loft([sec(.0, sx * .13, .17, .05, .1), sec(.1, sx * .13, .1, .07, .1), sec(.2, sx * .13, .06, .06, .06),
                                 sec(.38, sx * .12, .05, .055, .05), sec(.46, sx * .12, .045, .065, .045), sec(.5, sx * .12, .04, .02, .02)],
                                about="the foreleg stretched forward, the paw broad on the plinth"))
add("tail", loft([sec(-.5, .04, .12, .025, .025, 2), sec(-.46, .17, .04, .025, .025, 2), sec(-.3, .25, .028, .022, .022, 2),
                  sec(-.12, .25, .03, .022, .022, 2), sec(-.06, .24, .035, .04, .035, 2), sec(-.03, .24, .035, .01, .01, 2)], sides=10,
                 about="the tail laid round the right flank, its tuft by the hind paw"))
# the woman: the torso upright out of the lion's chest (a loft up y: u across, v fore and aft), the breasts, the neck,
# the head and the cap of hair with its bow behind
add("torso", loft([sec(.2, 0, .12, .13, .11), sec(.28, 0, .135, .12, .085), sec(.34, 0, .14, .11, .075), sec(.4, 0, .135, .13, .07),
                   sec(.43, 0, .13, .1, .06), sec(.45, 0, .13, .035, .035)], sides=16, axis="y",
                  about="the woman's torso rising upright out of the lion's chest: the waist, the ribs, the broad shoulders"))
for side, sx in (("right", 1), ("left", -1)):
    add(f"breast {side}", loft([sec(.17, sx * .05, .345, .0, .0), sec(.19, sx * .05, .345, .04, .038), sec(.215, sx * .05, .34, .032, .03),
                                sec(.225, sx * .05, .34, .0, .0)], sides=10,
                               about="the breasts"))
add("neck", loft([sec(.44, 0, .13, .035, .033), sec(.48, 0, .132, .033, .031), sec(.5, 0, .135, .034, .032)], sides=10, axis="y"))
add("head", loft([sec(.49, 0, .14, .0, .0), sec(.5, 0, .14, .045, .05), sec(.53, 0, .145, .055, .062), sec(.57, 0, .142, .05, .058),
                  sec(.6, 0, .138, .03, .036), sec(.61, 0, .136, .0, .0)], sides=14, axis="y",
                 about="the head held up, looking ahead over the paws"))
add("face", loft([sec(.16, 0, .54, .0, .0), sec(.175, 0, .54, .03, .035), sec(.195, 0, .535, .024, .03), sec(.2, 0, .53, .0, .0)], sides=10,
                 about="the face: brow, nose and chin standing out of the head's front"))
add("hair", loft([sec(.51, 0, .125, .0, .0), sec(.53, 0, .125, .058, .06), sec(.58, 0, .12, .056, .06), sec(.62, 0, .115, .036, .042),
                  sec(.64, 0, .11, .0, .0)], sides=14, axis="y",
                 about="the cap of braided hair over the crown and the back of the head"))
add("bow", loft([sec(.05, 0, .58, .0, .0), sec(.065, 0, .58, .05, .025), sec(.085, 0, .58, .03, .02), sec(.095, 0, .57, .0, .0)], sides=8,
                about="the ribbon bow at the back of the hair"))

doc = {"name": "Sphinx",
       "_about": "A BAROQUE GARDEN SPHINX: a lion's body lying on its plinth and a woman's bust rising from its chest, her head under a cap of braided hair with a bow -- the sphinxes on the Belvedere's garden stairs (Vienna, c. 1720). The lion is couchant-lion's (body, haunches, forelegs, tail, in lofts); the torso, breasts, neck, head and hair are lofts up from its chest. `S` its length, rump to the paws' tips; it faces +z. Generated by tools/archgen/sphinx.py.",
       "params": {"detail": 4, "S": 2.4, "_S": "its length, rump to the paws' tips (metres)", "plinthH": 1.0, "_plinthH": "the plinth's height"},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/components/sphinx.json"), "w").write(json.dumps(doc, indent=2) + "\n")
print("sphinx:", len(parts), "parts")
