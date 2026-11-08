from bg import *

def legs(d, hipY, ankY, deg, speed, flex):
    """legL (hip -> ankle: the tibiotarsus), tarsL (the ankle -> toes, its flex on the swing: flick), footL (kept level)"""
    parts = [p for p in d["parts"] if not p["id"].startswith(("foot", "tars"))]
    for p in parts:
        if p["id"] in ("legL", "legR"):
            p["pos"][1] = hipY - d["_bodyY"]
            p["size"]["len"] = hipY - .01
            p["pivot"] = [0, -(hipY - .01) / 2, 0]
            p["anim"] = {"axis": "z", "deg": deg, "speed": speed, "phase": p["anim"]["phase"]}
    for side, ph in (("L", 0), ("R", 3.14)):
        parts.append({"id": "tars" + side, "parent": "leg" + side, "shape": "sphere", "size": {"r": .008}, "pos": [0, ankY - hipY, 0], "color": "@leg",
                      "anim": {"axis": "z", "deg": -flex, "speed": speed, "phase": round(ph + 1.571, 3), "flick": 1}})
        parts.append({"id": "foot" + side, "parent": "tars" + side, "shape": "sphere", "size": {"r": .008}, "pos": [0, .012 - ankY, 0], "color": "@leg",
                      "anim": {"axis": "z", "deg": -deg, "speed": speed, "phase": ph}})
    d["parts"] = parts

def leg_shapes(hip, ank, rT, rA, rTa, color, thigh, thighR, toes, web=None, hallux=.03, scales=True):
    x, hy, z = hip; ay = ank
    out = [
        ell("thigh", [x, hy + .01, z], thighR, thigh, k=thighR[2] * .8, bone="legL", mirror=True),
        cone("tibia", [x, hy - .02, z], [x, ay, z], rT, rA * .85, color, k=.004, bone="legL", mirror=True),
        sph("ankle", [x, ay, z], rA, color, k=.004, bone="tarsL", mirror=True),
        cone("tarsus", [x, ay, z], [x + .005, .02, z], rTa, rTa * .85, color, k=.003, bone="tarsL", mirror=True,
             **({"pat": "scales", "frame": {"o": "$tarsL", "u": [0, -1, 0], "r": .02}} if scales else {})),
    ]
    f0 = [x + .005, .015, z]
    for nm, dz, L in (("toeM", 0, toes), ("toeO", .5, toes * .85), ("toeI", -.5, toes * .8)):
        tip = add(f0, nrm([1, -.12, dz]), L)
        out.append(cone(nm, f0, tip, rTa * .7, rTa * .35, color, k=.003, bone="footL", mirror=True))
    out.append(cone("hallux", f0, add(f0, [-hallux, -.006, 0]), rTa * .5, rTa * .3, color, k=.002, bone="footL", mirror=True))
    if web:
        out.append(ell("web", add(f0, [toes * .5, -.006, 0]), [toes * .45, .003, toes * .38], web, k=.004, bone="footL", mirror=True))
    return out
