import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, math
A = os.path.join(ROOT, 'assets/architecture/')
def save(p, d): open(A + p, 'w').write(json.dumps(d, indent=2) + "\n")

# ---- the orders, side by side -----------------------------------------------------------------------------
def orders():
  parts = {}; build = []
  def add(n, d): parts[n] = d; build.append(n)
  for i, (o, extra) in enumerate([("doric", {"triglyphs": {"w": "r * 1.1", "d": 0.12}}), ("tuscan", {}), ("ionic", {}), ("corinthian", {})]):
      add(o, {"type": "colonnade", "order": o, "count": 2, "spacing": 3.2, "columnR": "r", "height": "h",
              "entablature": {"h": "h * 0.2", "cornice": {"h": "h * 0.07", "out": 0.35}, **extra}, "at": [[f"gap * {i}", 0, 0, 0]]})
  add("pilasters", {"type": "colonnade", "order": "tuscan", "shaft": "square", "count": 3, "spacing": 2.4, "columnR": 0.3, "height": "h",
                    "entablature": {"h": "h * 0.15", "depth": 0.9}, "at": [["gap * 4", 0, 0, 0]],
                    "_about": "square shafts: pilasters against a wall, piers standing free"})
  save('elements/orders.json', {"name": "The orders",
   "_about": "THE CLASSICAL ORDERS as proportions of the shaft's radius (assemble.js ORDERS -- a new order is a new line of data): DORIC with no base, a sharp taper and a wide echinus, its frieze carrying TRIGLYPHS over every column and every gap; TUSCAN, its plain Roman cousin with a base; IONIC with its volutes; CORINTHIAN with a tall bell under a thin abacus. Each carries an entablature -- architrave and frieze, then a cornice standing proud of them. Last, square shafts: pilasters and piers.",
   "params": {"detail": 8, "r": 0.4, "h": 5.5, "gap": 7}, "build": build, "parts": parts})

# ---- a Greek temple from its components ------------------------------------------------------------------
from statuary import statue, pedestal, FACE_E, FACE_W, capped   # (the statue markers: shared by every generator with statues)


SEAT = 0.45   # a seated figure's seat, per unit of its scale (a chair's height: statues.js sits it on its top)


# a pediment figure's PROFILE by pose, per unit of its scale: [(height, how far out from its place it reaches that high)]
# -- a reclining figure's head and shoulders over its place (the pelvis), its legs low along the floor out to the corner;
# tallest first: each place takes the first that fits
PEDIMENT_POSES = [("stand", [(1.85, 0.32)]), ("sit", [(1.25 + SEAT, 0.45)]), ("kneel", [(1.32, 0.5)]), ("lie", [(0.82, 0.15), (0.3, 0.95)])]
PEDIMENT_GOD = 1.12    # the middle figure's size over the rest (the god the story is about)
PEDIMENT_GIVE = 0.85   # how far below the common size a figure may be drawn to stand, sit or kneel before it lies down


def pediment_figures(z, y, half, ridge, face, n, seed, scale_max=2.0, stone="marble"):
    """a pediment's sculpture: `n` figures along its floor (the cornice at height y, z its front) that FIT THE TRIANGLE
    AT ONE SCALE, as a sculptor composed it -- the size the middle figure stands at under the ridge; each place takes the
    tallest pose whose profile stands under the raking cornice there (PEDIMENT_POSES: a little smaller if it must,
    PEDIMENT_GIVE), so the poses follow the slope down: STANDING in the middle, facing out; SEATED further out, turned
    toward the middle and the front; then a warrior KNEELING with spear and shield (Aegina's), turned further toward the
    middle, its shield on the side toward the tympanum; RECLINING in the corners, on its side along the floor, facing out,
    propped on the elbow with the head toward the middle -- in `stone` (marble, or "painted": its colours on the marble,
    as they were), the people of myth in Greek dress. (Each sized to
    its own room, a row of standing figures shrank toward the corners like a scale drawing)"""
    out = {}
    room = lambda ax: max(0.0, ridge * (1 - ax / half) * 0.9 - 0.1)   # the clear height at |x| = ax
    fits = lambda prof, sc, ax: all(H * sc <= room(ax + W * sc) for H, W in prof)
    fwd = -1 if face == FACE_E else 1                                    # (which way is out: +z for the east front, -z for the west)
    xs = [(i + 0.5) / n * 2 * half - half for i in range(n)]
    mid = min(range(n), key=lambda i: abs(xs[i]))
    s0 = scale_max                                                       # (the common size: the middle figure's, standing)
    while s0 > 0.35 and not fits(PEDIMENT_POSES[0][1], s0 * PEDIMENT_GOD, abs(xs[mid])): s0 *= 0.97
    for i, x in enumerate(xs):
        side = 1 if x > 0 else -1
        base = s0 * (PEDIMENT_GOD if i == mid else 1)
        pick = next(((ps, sc) for ps, prof in PEDIMENT_POSES[:-1]
                     for sc in (base, base * (1 + PEDIMENT_GIVE) / 2, base * PEDIMENT_GIVE) if fits(prof, sc, abs(x))), None)   # (the tallest upright pose, a little smaller if it must)
        if pick: pose, sc = pick
        else:    # (lying, as big as the corner leaves it)
            pose, sc = "lie", base
            while sc >= 0.35 and not fits(PEDIMENT_POSES[-1][1], sc, abs(x)): sc *= 0.92
        if sc < 0.35: continue                                           # (no room left in the very corner)
        # its turn: out (the front) in the middle; toward the middle and the front further out; along the floor in a corner
        if pose == "stand": ang = face
        elif pose == "sit": ang = math.atan2(fwd * 0.7071, -side * 0.7071)   # (rotY = atan2(-dz, dx) for the way (dx, dz) it looks)
        elif pose == "kneel": ang = math.atan2(fwd * 0.5, -side * 0.866)
        else: ang = face
        # (lying, its head toward the middle: on its left side where its left, -(sin, cos) of its turn, points there)
        head = {"head": "left" if math.sin(ang) * side > 0 else "right"} if pose == "lie" else {}
        # (kneeling, armed: the spear in one hand, the shield on the other arm, helmeted -- girt short or nude, as Aegina's
        #  warriors are (statuary.json dress `active`) -- the pose mirrored on the other half, so the shield is on the side
        #  toward the tympanum either side and the body is seen: toward the front it hid it)
        arms = {"pose": "kneeling left" if side > 0 else "kneeling",
                "hold": {"L": "items/weapons/spear", "R": "items/shields/aspis"} if side > 0 else {"R": "items/weapons/spear", "L": "items/shields/aspis"},
                "kind": "man", "wear": ["clothes/crested-helmet"]} if pose == "kneel" else {}
        name = f"pediment {'east' if face == FACE_E else 'west'} {i}"
        # (seated, on a seat of its own -- a rock, a stool -- as high as its knees: the figure sits ON something, its
        #  long skirt falling to the ledge, where it sat on the ledge's edge with its legs and its skirt hanging over it)
        if pose == "sit": out[name + " seat"] = pedestal((x, y, z), 0.5 * sc, 0.5 * sc, SEAT * sc, "a seated figure's seat")
        out[name] = statue((x, y + (SEAT * sc if pose == "sit" else 0), z), **{"pose": pose, "scale": round(sc, 3), "stone": stone, "style": "greek",
                           "kind": "woman" if (i + seed) % 3 == 0 else "man", "seed": seed * 31 + i, "face": round(ang, 4), **head, **arms})
    return out


def temple(name, about, P, order="doric", dipteral=False, roofed=True, front_stair=False, statues=None, recess=0.0, porches=True, inner=None):
    """`order` the peristyle's; `dipteral`: a second ring of columns inside the first, one intercolumniation in (Didyma);
    `roofed` False: HYPAETHRAL -- the entablature, but no ceiling, roof or acroteria: the court open to the sky;
    `front_stair`: a stairway up the middle of the east front -- ONLY where the temple had one (Didyma's); the others are
    climbed by the crepidoma's own steps, as they were; `porches` False: no columns before the cella's ends of its own --
    an AMPHIPROSTYLE temple (Athena Nike's), its colonnade `front` x 2, a row before each end, those its porches;
    `inner`: the naos's own colonnade round its cult statue, in TWO STOREYS of Doric columns, one standing on the other's
    architrave up to the ceiling (the Parthenon's): a row down each side `x` either side of the axis, `n` columns at
    `sp` from the front back to `z0`, where a row of `back` crosses behind the statue; the lower storey `h1` tall under its
    architrave `e1`, the upper `h2` under `e2`, the shafts `r` thick below and three quarters of it above -- and the
    CROSS WALL `wall` behind it, closing the naos off from the west room"""
    parts = {}; build = []
    def add(n, d): parts[n] = d; build.append(n)
    add("crepidoma", {"type": "crepidoma", "width": "W", "length": "L", "steps": "steps", "stepH": "stepH", "stepOut": "stepOut", "at": [[0, 0, 0, 0]],
                      "_about": "the stepped platform; its top step is the stylobate the columns stand on"})
    if front_stair: add("front steps", {"type": "flight", "width": "D * 1.6", "run": 0.32, "rise": 0.17, "top": "base", "landing": 0,
                        # (its top tread on the stylobate's edge, L / 2: it climbs OVER the crepidoma's steps, which it
                        #  hides, to the floor the columns stand on -- it used to stop on the lowest step, in the air)
                        "at": [["D * 0.8", 0, "L / 2 + base / 0.17 * 0.32", 1.5707963]],
                        "_about": "the stairway up the middle of the east front, as the temple had it, over the crepidoma's steps to the stylobate"})
    ent = {"h": "entH", "depth": "D * 1.1", "cornice": {"h": "cornH", "out": "cornOut"}, **({"triglyphs": {"w": "D * 0.55", "d": 0.14}} if order == "doric" else {})}
    add("peristyle", {"type": "colonnade", "plan": "peristyle", "order": order, "front": "front", "side": "side",
                      "width": "W - 2 * inset", "length": "L - 2 * inset", "columnR": "D / 2", "height": "colH",
                      "entablature": ent, "at": [[0, "base", 0, 0]], "_about": f"the ring of {order.title()} columns, its architrave, frieze and cornice"})
    if dipteral:
        add("inner peristyle", {"type": "colonnade", "plan": "peristyle", "order": order, "front": "front - 2", "side": "side - 2",
                                "width": "W - 2 * inset - 2 * (W - 2 * inset) / (front - 1)", "length": "L - 2 * inset - 2 * (L - 2 * inset) / (side - 1)",
                                "columnR": "D / 2", "height": "colH", "entablature": {**ent, "cornice": {"h": "cornH * 0.6", "out": 0.1}}, "at": [[0, "base", 0, 0]],
                                "_about": "the second ring of a DIPTERAL temple, one intercolumniation inside the first: the double colonnade round the naos"})
    # the cella: side walls, back wall, front wall with the great door
    add("cella sides", {"type": "box", "width": "wallT", "length": "cellaL", "height": "cellaH",
                        "at": [["0 - cellaW / 2 + wallT / 2", "base", "cellaZ", 0], ["cellaW / 2 - wallT / 2", "base", "cellaZ", 0]]})
    add("cella back", {"type": "box", "width": "cellaW - 2 * wallT", "length": "wallT", "height": "cellaH",
                       "at": [[0, "base", "cellaZ - cellaL / 2 + wallT / 2", 0]]})
    add("cella front", {"type": "wall", "width": "cellaW - 2 * wallT", "height": "cellaH", "thickness": "wallT",
                        "openings": [{"at": "(cellaW - 2 * wallT) / 2", "width": "doorW", "sill": 0, "springing": "doorH", "head": {"profile": "flat"}}],
                        # (its lintel one block of marble: the Parthenon's over a door near 5m wide, Didyma's -- some
                        #  seventy tonnes -- over 5.6m; check.js lintels)
                        "beam": 6.0,
                        "at": [[0, "base", "cellaZ + cellaL / 2", 0]], "_about": "the front wall of the naos, with its great door"})
    if porches:
      add("pronaos", {"type": "colonnade", "order": "doric", "count": "porch", "spacing": "(cellaW - D * 1.2) / (porch - 1)", "columnR": "D * 0.45",
                      "height": "colH * 0.97", "entablature": {"h": "entH * 0.8", "depth": "D"}, "at": [[0, "base", "cellaZ + cellaL / 2 + porchD", 0]],
                      "_about": "the porch before the door: columns across the front of the cella"})
      add("opisthodomos", {"type": "colonnade", "order": "doric", "count": "porch", "spacing": "(cellaW - D * 1.2) / (porch - 1)", "columnR": "D * 0.45",
                           "height": "colH * 0.97", "entablature": {"h": "entH * 0.8", "depth": "D"}, "at": [[0, "base", "cellaZ - cellaL / 2 - porchD", 0]],
                           "_about": "the matching porch at the back"})
    if inner:
        I = inner
        side_z = round(I["z0"] + I["sp"] * (I["n"] + 1) / 2, 3)        # (the side rows' middle: n columns on from the back row's)
        for st, (y, h, r, e) in enumerate([("base", I["h1"], I["r"], I["e1"]), (f"base + {I['h1'] + I['e1']}", I["h2"], round(I["r"] * 0.75, 3), I["e2"])]):
            nm = "inner colonnade" + (" upper" if st else "")
            ent = {"h": e, "depth": round(r * 2.3, 3)}
            add(nm, {"type": "colonnade", "order": "doric", "count": I["n"], "spacing": I["sp"], "columnR": r, "height": h, "entablature": ent,
                     "at": [[I["x"], y, side_z, 1.5707963], [-I["x"], y, side_z, 1.5707963]],
                     "_about": f"the naos's colonnade down either side of the statue, its {'upper' if st else 'lower'} storey"})
            add(nm + " back", {"type": "colonnade", "order": "doric", "count": I["back"], "spacing": round(2 * I["x"] / (I["back"] - 1), 3), "columnR": r, "height": h,
                               "entablature": ent, "at": [[0, y, I["z0"], 0]], "_about": f"the row across behind the statue, its {'upper' if st else 'lower'} storey"})
        add("cross wall", {"type": "box", "width": "cellaW - 2 * wallT", "length": 1.2, "height": "cellaH", "at": [[0, "base", I["wall"], 0]],
                           "_about": "the wall between the naos and the west room"})
    for k, v in capped(statues or {}).items(): add(k, v)
    if not roofed:
        save(name, {"name": about[0], "_about": about[1], "params": P, "build": build, "parts": parts}); return
    add("ceiling", {"type": "coffered-ceiling", "width": "W - 2 * inset - D * 1.1", "length": "L - 2 * inset - D * 1.1", "thickness": "entH + cornH",
                    "nx": "front * 2", "nz": "side * 2", "depth": 0.3, "steps": 1, "at": [[0, "base + colH", 0, 0]],
                    "_about": "the coffered marble ceiling inside the ring of the entablature, over the colonnade walk and the cella"})
    # (`recess`: the gable's ends -- the tympana -- set back that far behind the cornice, leaving the ledge the
    #  pediment's figures stand on, as they were; the RAKING CORNICE up the gable's slopes standing out over it, as deep
    #  as the cornice, so the pediment is framed on all three sides)
    add("roof", {"type": "roof", "form": "gable", "width": "W - 2 * inset + D * 1.1 + 2 * cornOut", "length": f"L - 2 * inset + D * 1.1 + 2 * cornOut - {2 * recess}",
                 "pitch": "pitch", "rake": {"h": "cornH", "out": max(recess, 0.15)}, "at": [[0, "base + colH + entH + cornH", 0, 0]],
                 "_about": "one gable over the whole: its two ends are the pediments"})
    # (the ACROTERIA: a floral one on each apex -- items/ornaments/acroterion, its palmette over two volutes, painted --
    #  standing on the raking cornice's meeting, as tall as the column is thick and half again)
    add("acroteria", {"type": "item", "item": "items/ornaments/acroterion", "params": {"h": "D * 1.6"}, "solid": False,
                      "at": [[0, "base + colH + entH + cornH + ridge", f"L / 2 - inset + D * 0.55 + cornOut - D * 0.25 - {recess}", 0],
                             [0, "base + colH + entH + cornH + ridge", f"0 - L / 2 + inset - D * 0.55 - cornOut + D * 0.25 + {recess}", 0]],
                      "_about": "the floral ornaments on the apex of each pediment"})
    save(name, {"name": about[0], "_about": about[1], "params": P, "build": build, "parts": parts})

common = {"detail": 4, "_inset": "stylobate edge to column axis", "_ridge": "the pediment's height: half the roof's width times the pitch's slope"}


def main():
  temple('hephaestus.json', ("Temple of Hephaestus",
    "THE TEMPLE OF HEPHAESTUS, Athens (c. 449 BC), the best preserved Doric temple, built from the engine's components at its real size: a three-step crepidoma with a 13.71 x 31.78m stylobate; a peristyle of 6 x 13 Doric columns 5.71m tall (a `colonnade` of plan `peristyle`) under its architrave, triglyph frieze and cornice; the cella with its great door, a porch of columns before it and a matching one behind; a coffered ceiling inside the ring of the entablature; one gable roof whose two ends are the pediments, with an acroterion on each apex."),
    {**common, "W": 13.71, "L": 31.78, "steps": 3, "stepH": 0.3, "stepOut": 0.33, "base": 0.9, "front": 6, "side": 13, "D": 1.02, "inset": 0.82,
     "colH": 5.71, "entH": 1.3, "cornH": 0.38, "cornOut": 0.3, "pitch": 14, "ridge": 1.7,
     "cellaW": 7.6, "cellaL": 17.5, "cellaZ": -0.6, "cellaH": 5.4, "wallT": 0.9, "doorW": 2.6, "doorH": 4.2, "porch": 2, "porchD": 2.4},
    # the cult statues by Alkamenes (421-415 BC): Hephaestus and Athena, bronze, side by side on one base at the back of the cella
    statues={"cult base": {"type": "box", "width": 3.2, "length": 1.4, "height": 0.7, "at": [[0, 0.9, -7.4, 0]], "_about": "the base of the cult statues"},
             "Hephaestus": statue((-0.75, 1.6, -7.4), kind="man", style="greek", stone="bronze", scale=1.3, hold={"R": "items/tools/hammer"}, seed=3, face=FACE_E),
             "Athena": statue((0.75, 1.6, -7.4), kind="woman", style="greek", stone="bronze", scale=1.3, hold={"R": "items/weapons/dory", "L": "items/shields/aspis"}, seed=5, face=FACE_E)})
  temple('parthenon.json', ("Parthenon",
    "THE PARTHENON, Athens (447-432 BC), from the same components as the Temple of Hephaestus and at its real size: a stylobate 30.88 x 69.5m on steps half a metre high, 8 x 17 Doric columns 10.43m tall and 1.91m thick, the entablature 3.29m deep with its triglyphs (ninety-six of them, one geometry drawn ninety-six times), the naos with six-column porches at both ends -- the pronaos before the door and the opisthodomos behind -- the coffered ceiling, and the low gable whose ends are the pediments."),
    {**common, "W": 30.88, "L": 69.5, "steps": 3, "stepH": 0.5, "stepOut": 0.7, "base": 1.5, "front": 8, "side": 17, "D": 1.91, "inset": 1.5,
     "colH": 10.43, "entH": 2.6, "cornH": 0.69, "cornOut": 0.6, "pitch": 13, "ridge": 3.5,
     "cellaW": 21.7, "cellaL": 48.3, "cellaZ": 0, "cellaH": 10.0, "wallT": 1.2, "doorW": 4.9, "doorH": 9.0, "porch": 6, "porchD": 3.8},
    # ATHENA PARTHENOS (Phidias, 438 BC): gold and ivory (chryselephantine: her robe, her helmet, her hair in gold,
    # her face and arms in ivory, her crested helmet gold), toward the back of the naos facing the door, the colonnade behind her, her shield
    # standing at her left side under her hand, her right held out (a Victory stood on it, offering a wreath: the wreath), on her 8 x 4 m base -- as tall as the ceiling lets her be here (she was 11.5 m); and the PEDIMENTS' figures:
    # the birth of Athena in the east, her contest with Poseidon in the west, eleven each -- standing in the middle,
    # seated further out, reclining in the corners -- on the ledge before the tympana (the gables set back 1 m)
    recess=1.0,
    # (the naos's two storeys of Doric columns round her -- nine down each side, five across behind her -- up to the
    #  ceiling, the cross wall behind them)
    inner={"x": 5.6, "z0": -4.6, "n": 9, "sp": 2.75, "back": 5, "h1": 5.6, "e1": 0.7, "h2": 3.5, "e2": 0.63, "r": 0.55, "wall": -7.7},
    statues={"Athena base": {"type": "box", "width": 8.06, "length": 4.09, "height": 0.9, "at": [[0, 1.5, -1.5, 0]], "_about": "the base of the Athena Parthenos"},
             "Athena Parthenos": statue((0, 2.4, -1.5), kind="woman", style="greek", stone="chryselephantine", scale=5.1, pose="offering", hold={"R": "items/tools/victor-wreath", "L": "items/shields/aspis"},
                                        grip={"L": "shield rest"}, wear=["clothes/crested-helmet"], seed=7, face=FACE_E),
             # (the pediments' figures PAINTED, as all Greek marble sculpture was: their dress in its colours, skin, hair and
             #  eyes -- statues.js "painted")
             **pediment_figures(34.35, 15.22, 14.4, 3.5, FACE_E, 11, 1, stone="painted"), **pediment_figures(-34.35, 15.22, 14.4, 3.5, FACE_W, 11, 2, stone="painted")})
  temple('didyma.json', ("Temple of Apollo, Didyma",
    "THE TEMPLE OF APOLLO AT DIDYMA (begun c. 300 BC, never finished), from the temple components at its real size: a seven-step crepidoma, the stylobate 51.13 x 109.34m; DIPTERAL -- a double ring of Ionic columns, 10 x 21 in the outer and 8 x 19 in the inner, nearly 20m tall -- and HYPAETHRAL: the entablature runs round, but the great adyton inside the naos walls stood open to the sky, so there is no ceiling and no roof. The naos walls as tall as the columns, the great door before them on its porch."),
    {**common, "W": 51.13, "L": 109.34, "steps": 7, "stepH": 0.45, "stepOut": 0.45, "base": 3.15, "front": 10, "side": 21, "D": 1.98, "inset": 1.6,
     "colH": 19.7, "entH": 3.4, "cornH": 0.9, "cornOut": 0.7, "pitch": 14, "ridge": 0,
     "cellaW": 29.0, "cellaL": 72.0, "cellaZ": -6.0, "cellaH": 19.7, "wallT": 2.0, "doorW": 5.6, "doorH": 14.0, "porch": 4, "porchD": 5.0},
    order="ionic", dipteral=True, roofed=False, front_stair=True,
    # the bronze Apollo Philesios (Kanachos) in the adyton, standing toward its back on a pedestal, the bow in his left
    statues={"Apollo base": {"type": "box", "width": 2.4, "length": 2.4, "height": 1.4, "at": [[0, 3.15, -37.0, 0]], "_about": "the pedestal of Apollo's statue"},
             "Apollo": statue((0, 4.55, -37.0), kind="man", style="greek", stone="bronze", scale=2.4, hold={"L": "items/weapons/longbow"}, seed=11, face=FACE_E)})


if __name__ == "__main__":
  orders()
  main()
