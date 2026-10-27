import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, math
A = os.path.join(ROOT, 'assets/architecture/')
def save(p, d): open(A + p, 'w').write(json.dumps(d, indent=2) + "\n")

# ---- the orders, side by side -----------------------------------------------------------------------------
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
from statuary import statue, FACE_E, FACE_W, capped   # (the statue markers: shared by every generator with statues)


def pediment_figures(z, y, half, ridge, face, n, seed, scale_max=2.0):
    """a pediment's sculpture: `n` figures along its floor (the cornice at height y, z its front) that FIT THE TRIANGLE --
    each sized by the height the raking cornice leaves at its OUTER edge, with a margin: STANDING in the middle third,
    facing out; SEATED further out, turned toward the middle and the front; RECLINING in the corners, along the
    floor with the head toward the middle -- in marble, the people of myth in Greek dress"""
    out = {}
    room = lambda ax: max(0.0, ridge * (1 - ax / half) * 0.9 - 0.1)   # the clear height at |x| = ax
    fwd = -1 if face == FACE_E else 1                                    # (which way is out: +z for the east front, -z for the west)
    for i in range(n):
        x = (i + 0.5) / n * 2 * half - half
        t, side = abs(x) / half, (1 if x > 0 else -1)
        if t < 0.3:   pose, H, W = "stand", 1.85, 0.32       # its height and its half-width along the floor, per unit of scale
        elif t < 0.62: pose, H, W = "sit", 1.25, 0.45
        else:          pose, H, W = "lie", 0.45, 0.95
        sc = scale_max
        for _ in range(20):   # (the largest size whose outer edge still stands under the cornice)
            if H * sc <= room(abs(x) + W * sc): break
            sc *= 0.92
        if sc < 0.35: continue                                           # (no room left in the very corner)
        # its turn: out (the front) in the middle; toward the middle and the front further out; along the floor in a corner
        if pose == "stand": ang = face
        elif pose == "sit": ang = math.atan2(fwd * 0.7071, -side * 0.7071)   # (rotY = atan2(-dz, dx) for the way (dx, dz) it looks)
        else: ang = 0.0 if side < 0 else 3.1415927
        out[f"pediment {'east' if face == FACE_E else 'west'} {i}"] = statue((x, y, z), pose=pose, scale=round(sc, 3), stone="marble", style="greek",
                                                                             kind="woman" if (i + seed) % 3 == 0 else "man", seed=seed * 31 + i, face=round(ang, 4))
    return out


def temple(name, about, P, order="doric", dipteral=False, roofed=True, front_stair=False, statues=None, recess=0.0):
    """`order` the peristyle's; `dipteral`: a second ring of columns inside the first, one intercolumniation in (Didyma);
    `roofed` False: HYPAETHRAL -- the entablature, but no ceiling, roof or acroteria: the court open to the sky;
    `front_stair`: a stairway up the middle of the east front -- ONLY where the temple had one (Didyma's); the others are
    climbed by the crepidoma's own steps, as they were"""
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
    add("pronaos", {"type": "colonnade", "order": "doric", "count": "porch", "spacing": "(cellaW - D * 1.2) / (porch - 1)", "columnR": "D * 0.45",
                    "height": "colH * 0.97", "entablature": {"h": "entH * 0.8", "depth": "D"}, "at": [[0, "base", "cellaZ + cellaL / 2 + porchD", 0]],
                    "_about": "the porch before the door: columns across the front of the cella"})
    add("opisthodomos", {"type": "colonnade", "order": "doric", "count": "porch", "spacing": "(cellaW - D * 1.2) / (porch - 1)", "columnR": "D * 0.45",
                         "height": "colH * 0.97", "entablature": {"h": "entH * 0.8", "depth": "D"}, "at": [[0, "base", "cellaZ - cellaL / 2 - porchD", 0]],
                         "_about": "the matching porch at the back"})
    for k, v in capped(statues or {}).items(): add(k, v)
    if not roofed:
        save(name, {"name": about[0], "_about": about[1], "params": P, "build": build, "parts": parts}); return
    add("ceiling", {"type": "coffered-ceiling", "width": "W - 2 * inset - D * 1.1", "length": "L - 2 * inset - D * 1.1", "thickness": "entH + cornH",
                    "nx": "front * 2", "nz": "side * 2", "depth": 0.3, "steps": 1, "at": [[0, "base + colH", 0, 0]],
                    "_about": "the coffered marble ceiling inside the ring of the entablature, over the colonnade walk and the cella"})
    # (`recess`: the gable's ends -- the tympana -- set back that far behind the cornice, leaving the ledge the
    #  pediment's figures stand on, as they were)
    add("roof", {"type": "roof", "form": "gable", "width": "W - 2 * inset + D * 1.1 + 2 * cornOut", "length": f"L - 2 * inset + D * 1.1 + 2 * cornOut - {2 * recess}",
                 "pitch": "pitch", "at": [[0, "base + colH + entH + cornH", 0, 0]],
                 "_about": "one gable over the whole: its two ends are the pediments"})
    add("acroteria", {"type": "box", "width": "D * 0.5", "length": "D * 0.5", "height": "D * 0.9",
                      "at": [[0, "base + colH + entH + cornH + ridge", f"L / 2 - inset + D * 0.55 + cornOut - D * 0.25 - {recess}", 0],
                             [0, "base + colH + entH + cornH + ridge", f"0 - L / 2 + inset - D * 0.55 - cornOut + D * 0.25 + {recess}", 0]],
                      "_about": "the ornaments on the apex of each pediment"})
    save(name, {"name": about[0], "_about": about[1], "params": P, "build": build, "parts": parts})

common = {"detail": 4, "_inset": "stylobate edge to column axis", "_ridge": "the pediment's height: half the roof's width times the pitch's slope"}
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
  # ATHENA PARTHENOS (Phidias, 438 BC): gold and ivory, toward the west end of the naos facing the door, her shield at her
  # side, on her 8 x 4 m base -- as tall as the ceiling lets her be here (she was 11.5 m); and the PEDIMENTS' figures:
  # the birth of Athena in the east, her contest with Poseidon in the west, eleven each -- standing in the middle,
  # seated further out, reclining in the corners -- on the ledge before the tympana (the gables set back 1 m)
  recess=1.0,
  statues={"Athena base": {"type": "box", "width": 8.06, "length": 4.09, "height": 0.9, "at": [[0, 1.5, -6.0, 0]], "_about": "the base of the Athena Parthenos"},
           "Athena Parthenos": statue((0, 2.4, -6.0), kind="woman", style="greek", stone="gold", scale=5.1, hold={"L": "items/shields/aspis"}, seed=7, face=FACE_E),
           **pediment_figures(34.35, 15.22, 14.4, 3.5, FACE_E, 11, 1), **pediment_figures(-34.35, 15.22, 14.4, 3.5, FACE_W, 11, 2)})
temple('didyma.json', ("Temple of Apollo, Didyma",
  "THE TEMPLE OF APOLLO AT DIDYMA (begun c. 300 BC, never finished), from the temple components at its real size: a seven-step crepidoma, the stylobate 51.13 x 109.34m; DIPTERAL -- a double ring of Ionic columns, 10 x 21 in the outer and 8 x 19 in the inner, nearly 20m tall -- and HYPAETHRAL: the entablature runs round, but the great adyton inside the naos walls stood open to the sky, so there is no ceiling and no roof. The naos walls as tall as the columns, the great door before them on its porch."),
  {**common, "W": 51.13, "L": 109.34, "steps": 7, "stepH": 0.45, "stepOut": 0.45, "base": 3.15, "front": 10, "side": 21, "D": 1.98, "inset": 1.6,
   "colH": 19.7, "entH": 3.4, "cornH": 0.9, "cornOut": 0.7, "pitch": 14, "ridge": 0,
   "cellaW": 29.0, "cellaL": 72.0, "cellaZ": -6.0, "cellaH": 19.7, "wallT": 2.0, "doorW": 5.6, "doorH": 14.0, "porch": 4, "porchD": 5.0},
  order="ionic", dipteral=True, roofed=False, front_stair=True,
  # the bronze Apollo Philesios (Kanachos) in the adyton, standing toward its back on a pedestal, the bow in his left
  statues={"Apollo base": {"type": "box", "width": 2.4, "length": 2.4, "height": 1.4, "at": [[0, 3.15, -37.0, 0]], "_about": "the pedestal of Apollo's statue"},
           "Apollo": statue((0, 4.55, -37.0), kind="man", style="greek", stone="bronze", scale=2.4, hold={"L": "items/weapons/longbow"}, seed=11, face=FACE_E)})
