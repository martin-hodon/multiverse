"""MODERN ELECTRONICS (2026-11-20; docs/modern.md): the machines of the home and the office -- a desktop computer
with its monitor, keyboard and mouse, a laptop, a flat-screen television, a fridge-freezer, a washing machine, a
microwave, a cooker, a smartphone, a radio, a loudspeaker, a printer and a desk telephone.

THE FRAME is the modern one (kit.py), the same as a car's and the shared `screen`'s: the origin under the thing's
middle on whatever it stands on (the floor, a worktop, a desk), its FRONT -- the screen, the door, the keys -- toward
+x, y up, z across. (The furniture group faces +z, as the period furniture does: a television set on the TV stand is
turned yaw -90 to face the room the stand faces. Placed on a desk the computer set's +x is where its user sits.)
The appliances' rounded cabinets are `loft`s: a loft along x is a rounded-rectangle section in y-z, so a cabinet's
front outline -- its cap -- has rounded corners and its edges running back are soft, as pressed steel and moulded
plastic are.
"""
import math
from kit import item, box, rod, lathe, loft, sphere, ring, sweep, plate, use, write, across, arc, hinge, slide, runs

C = "modern/components/"
FACE = [0, 0, -90]   # (a lathe's y axis turned to +x: a knob, a speaker cone, a porthole facing the front)


def faces(x, y, z):
    """an `at` that turns a part's y axis to +x (roll -90) -- a lathe facing the front"""
    return [x, y, z, 0, 0, -90]


def knob(id_, mat, r, h, x, y, z, **k):
    """a round control knob standing h out of the face at x, a skirt and a grip; facing +x"""
    return lathe(id_, mat, [[0, 0], [r * 1.15, 0], [r * 1.15, h * 0.25], [r, h * 0.35], [r * 0.95, h], [0, h]], faces(x, y, z), sides=14, **k)


def key_rows(id_, mat, x0, y, z0, rows, pitch=0.019, key=(0.015, 0.008, 0.015), roll=0.0, zdir=-1):
    """rows of keys: each row (dx, dz, n, w) -- n keys from z0 + dz across, w their width in pitches (1 a letter,
    6 the space bar), at x0 + dx; their tops at y. One part a row (`along`), so a keyboard is a handful of parts.
    The rows run from z0 toward -z (zdir -1): a machine faces +x, so its user faces -x and his LEFT is +z -- z0 is the
    keyboard's left end, where Esc and Tab are."""
    out = []
    for i, (dx, dz, n, w) in enumerate(rows):
        kw = key[2] + (w - 1) * pitch
        z1 = z0 + zdir * (dz + kw / 2)
        z2 = z1 + zdir * (n - 1) * w * pitch
        out.append(box(f"{id_}{i}", mat, [key[0], key[1], kw], [0, 0, 0, 0, 0, roll], along={"n": n, "from": [x0 + dx, y - key[1] / 2, z1], "to": [x0 + dx, y - key[1] / 2, z2]}))
    return runs(id_ + "s", out)   # (rows alike but for x -- the numeric pad's -- one `each` part)


def keyboard_rows(x0, y, z0, mat="keys", pitch=0.019, key=(0.015, 0.008, 0.015), numpad=True, roll=0.0, zdir=-1):
    """a full keyboard's keys: the function row, the number row, three letter rows, the bottom row round the space
    bar, the numeric pad to the right -- in rows from the back (x0) toward the front"""
    p = pitch
    rows = [(0, 0, 13, 1),                                                    # (esc and the F keys)
            (0.022, 0, 13, 1), (0.022, 13 * p, 1, 2),                          # (numbers, backspace)
            (0.022 + p, 0, 1, 1.5), (0.022 + p, 1.5 * p, 12, 1), (0.022 + p, 13.5 * p, 1, 1.5),
            (0.022 + 2 * p, 0, 1, 1.75), (0.022 + 2 * p, 1.75 * p, 11, 1), (0.022 + 2 * p, 12.75 * p, 1, 2.25),
            (0.022 + 3 * p, 0, 1, 2.25), (0.022 + 3 * p, 2.25 * p, 10, 1), (0.022 + 3 * p, 12.25 * p, 1, 2.75),
            (0.022 + 4 * p, 0, 3, 1.25), (0.022 + 4 * p, 3.75 * p, 1, 6.25), (0.022 + 4 * p, 10 * p, 4, 1.25)]
    if numpad:
        rows += [(0.022 + k * p, 15.5 * p, 4, 1) for k in range(4)] + [(0.022 + 4 * p, 15.5 * p, 1, 2), (0.022 + 4 * p, 17.5 * p, 2, 1)]
    return key_rows("key", mat, x0, y, z0, rows, p, key, roll, zdir)


def cone(id_, x, y, z, R, mats=("cone", "surround", "trim")):
    """a loudspeaker driver facing +x: its paper cone dished in, the dust cap, the rubber surround, the trim ring"""
    c, s, t = mats
    return [
        lathe(id_, c, [[0, -0.006 * R / 0.2], [R * 0.25, -0.01 * R / 0.2], [R * 0.3, -0.026 * R / 0.2], [R * 0.82, -0.008 * R / 0.2]], faces(x, y, z), caps=False, double=True, sides=20),
        lathe(id_ + "Surround", s, [[R * 0.8, -0.009 * R / 0.2], [R * 0.88, 0.002], [R * 0.96, -0.004]], faces(x, y, z), caps=False, double=True, sides=20),
        ring(id_ + "Trim", t, R, 0.005, faces(x, y, z)),
    ]


def bar_handle(id_, x, y0, y1, z, stand=0.03, r=0.009, along="y"):
    """a bar handle (C bar-handle) standing `stand` off a front at x, from y0 to y1 at z (or from z=y0 to y1 at y=z,
    along "z") -- the component turned to face +x"""
    mid = (y0 + y1) / 2
    return use(id_, C + "bar-handle", [x, mid, z, 90, 0, 0] if along == "y" else [x, z, mid, 90, 0, 0],
               {"l": y1 - y0, "stand": stand, "r": r, "pr": r * 0.8, "inset": 0.015, "sides": 10, "psides": 8, "along": "upright" if along == "y" else "across"})


# ---- THE COMPUTER -------------------------------------------------------------------------------------------------
def desktop():
    # A DESKTOP COMPUTER as it stands on a desk (the 2010s): a 24-inch monitor (53 x 30 cm) on its stand, a mid-tower
    # case (42 x 19 x 42 cm) to its left, a full keyboard (44 x 13.5 cm) and a mouse on its pad in front -- the user at
    # +x. The origin is on the desk's top.
    mx, my = -0.2, 0.275
    kx, kz = 0.07, 0.03
    parts = [
        use("monitor", C + "screen", [mx, my, 0], {"w": 0.531, "h": 0.299, "b": 0.009, "t": 0.018}),
        box("monitorBack", "case", [0.035, 0.2, 0.3], [mx - 0.03, my - 0.02, 0]),
        box("neck", "case", [0.024, 0.25, 0.07], [mx - 0.06, 0.135, 0, 0, 0, 6]),
        box("foot", "case", [0.2, 0.012, 0.25], [mx - 0.04, 0.006, 0]),
        box("logo", "trim", [0.002, 0.006, 0.03], [mx + 0.001, my - 0.155, 0]),
        # (the tower)
        box("tower", "case", [0.42, 0.42, 0.19], [-0.08, 0.21, 0.52]),
        box("towerFront", "panel", [0.008, 0.4, 0.18], [0.134, 0.21, 0.52]),
        box("towerVent", "port", [0.2, 0.12, 0.002], [-0.12, 0.3, 0.52 - 0.0955]),
        lathe("power", "trim", [[0, 0.004], [0.009, 0.004], [0.01, 0]], faces(0.138, 0.38, 0.52), sides=12),
        box("port", "port", [0.003, 0.005, 0.013], [0.139, 0.34, 0.52], along={"n": 3, "from": [0, 0, -0.03], "to": [0, 0, 0.03]}),
        box("vent", "port", [0.003, 0.004, 0.14], [0.139, 0, 0.52], along={"n": 9, "from": [0, 0.04, 0], "to": [0, 0.24, 0]}),
        # (the keyboard: a sloping plate, its keys in rows)
        box("kbBase", "case", [0.14, 0.02, 0.445], [kx, 0.012, kz, 0, 0, -2.5]),
        *keyboard_rows(kx - 0.055, 0.03, kz + 0.21),
        # (the mouse on its pad)
        box("pad", "padCloth", [0.22, 0.003, 0.25], [kx, 0.0015, -0.36]),
        loft("mouse", "case", [[-0.055, 0.018, 0.003, 0.022], [-0.03, 0.029, 0.003, 0.036], [0.005, 0.031, 0.003, 0.037], [0.035, 0.028, 0.003, 0.03], [0.058, 0.019, 0.003, 0.017]], [0.006, 0.016], seg=3, at=[kx, 0, -0.36]),
        lathe("wheel", "trim", [[0.006, -0.003], [0.007, 0], [0.006, 0.003]], [kx + 0.03, 0.032, -0.36, 0, 90, 0], sides=10),
        box("split", "port", [0.035, 0.002, 0.002], [kx + 0.04, 0.03, -0.36, 0, 0, -12]),
        sweep("cable", "case", [[mx - 0.05, 0.05, 0.05], [mx - 0.1, 0.01, 0.12], [-0.25, 0.006, 0.3], [-0.29, 0.1, 0.425]], 0.004, seg=4),
    ]
    return item("Desktop computer", "electronics", "a desktop computer set of the 2010s as it stands on a desk: a 24-inch monitor (53 x 30 cm picture) on its stand, a mid-tower case 42 cm high with a glass side to its left, a full-size keyboard (44 cm) with its keys in rows and a numeric pad, a mouse on its pad -- the user at +x, the origin on the desk",
        {"case": {"pick": ["plastic-black", "#2b2d31"]}, "panel": "#1d1e21", "keys": {"pick": ["#2c2e33", "plastic-grey"]}, "trim": "aluminium", "port": "#0d0d0f",
         "glass": "glass", "padCloth": "#30353c"}, parts, era="1995-2030")


def laptop():
    # A LAPTOP, OPEN (a 14-inch: 31 x 21.5 cm, 1.6 cm thick shut): the base with its keyboard in a darker well and a
    # trackpad, the lid opened to 110 degrees on its hinge, the screen in its bezel (the shared screen)
    D, W = 0.215, 0.31
    hx, hy, ang = -D / 2 + 0.006, 0.014, 18
    s, c = math.sin(math.radians(ang)), math.cos(math.radians(ang))
    lh = 0.19 / 2 + 0.008   # (from the lid's middle to its bottom edge)
    ox, oy = hx - s * lh + c * 0.006, hy + c * lh + s * 0.006
    return item("Laptop", "electronics", "a 14-inch laptop, open: the aluminium base (31 x 21.5 cm) with its keyboard in a darker well and a trackpad, the lid opened to 108 degrees on its hinge, the screen in a thin bezel -- facing +x",
        {"shell": {"pick": ["aluminium", "#2f3237", "paint-silver"]}, "keys": "#1b1c1f", "well": "#2a2c30", "pad": "#9aa0a8", "glass": "screen", "case": "#18191c"}, [
            loft("base", "shell", [[-D / 2, W / 2, 0, 0.015], [D / 2, W / 2, 0, 0.012]], [0.004, 0.004], seg=1),
            box("well", "well", [0.105, 0.001, 0.285], [-0.045, 0.0145, 0]),
            *key_rows("key", "keys", -0.088, 0.0158, 0.133, [(0, 0, 14, 1), (0.0185, 0, 14, 1), (0.037, 0, 13, 1), (0.037, 13 * 0.0185, 1, 1.5),
                                                               (0.0555, 0, 12, 1), (0.0555, 12 * 0.0185, 1, 2.3), (0.074, 0, 3, 1), (0.074, 3 * 0.0185, 1, 6), (0.074, 9 * 0.0185, 5, 1)],
                      pitch=0.0185, key=(0.0145, 0.0012, 0.015)),
            box("trackpad", "pad", [0.07, 0.0008, 0.11], [0.06, 0.0128, 0, 0, 0, -0.8]),
            rod("hinge", "case", 0.005, [hx, hy, -0.12], [hx, hy, 0.12], 10),
            use("lid", C + "screen", [ox, oy, 0, 0, 0, ang], {"w": 0.294, "h": 0.19, "b": 0.008, "t": 0.006}, {"case": "shell"}),
            box("bezel", "case", [0.0015, 0.19 + 0.012, 0.294 + 0.012], [ox + 0.0004 * c, oy, 0, 0, 0, ang]),
            sphere("camera", "keys", 0.0025, [ox - s * (lh - 0.004) + 0.001, oy + c * (lh - 0.004), 0], sides=6),
        ], era="2010-2030")


# ---- THE SITTING ROOM -------------------------------------------------------------------------------------------
def television():
    # A FLAT-SCREEN TELEVISION (a 55-inch: a 121 x 68 cm picture) on its pedestal stand: the panel in a thin bezel, the
    # deeper housing behind its lower part for the electronics, the neck and the foot plate
    return item("Flat-screen television", "electronics", "a 55-inch flat-screen television (a 121 x 68 cm picture) on its pedestal: the panel in a thin bezel, the electronics' housing behind, the neck and a foot plate -- facing +x, standing on a TV stand or a sideboard",
        {"glass": "screen", "case": "#1a1b1e", "stand": {"pick": ["#2a2b2f", "aluminium"]}, "led": "lamp-red", "logo": "aluminium"}, [
            use("panel", C + "screen", [0, 0.44, 0], {"w": 1.21, "h": 0.68, "b": 0.007, "t": 0.012}),
            box("housing", "case", [0.04, 0.4, 0.8], [-0.032, 0.36, 0]),
            box("neck", "stand", [0.03, 0.2, 0.09], [-0.04, 0.115, 0, 0, 0, 8]),
            box("foot", "stand", [0.24, 0.014, 0.4], [-0.04, 0.007, 0]),
            box("logo", "logo", [0.002, 0.004, 0.04], [0.001, 0.0975, 0]),
            box("led", "led", [0.003, 0.003, 0.006], [0.001, 0.097, 0.3]),
        ], era="2005-2030")


def radio():
    # A TABLE RADIO (the transistor portable of the 1960s-70s, 30 x 17 x 12 cm): a rounded case, a speaker grille of
    # slats on the left of its face, a tuning dial with its scale and needle on the right, two knobs, a chrome carrying
    # handle and a telescopic aerial
    return item("Radio", "electronics", "a transistor table radio of the 1960s-70s, 30 x 17 x 12 cm: a rounded case, a slatted speaker grille, a tuning dial with its scale and needle, two knobs, a chrome carrying handle and a telescopic aerial -- facing +x",
        {"body": {"pick": ["paint-cream", "paint-red", "#3f6b5c", "#2e2f33", "walnut"]}, "grille": "#c9bfa9", "slat": "#6f6a62", "dial": "#efe6cc", "mark": "#3a3632",
         "needle": "#c0392b", "knob": "#2a2a2c", "chrome": "chrome"}, [
            loft("case", "body", [[-0.06, 0.15, 0.006, 0.17], [0.06, 0.15, 0.006, 0.17]], 0.03, seg=1),
            box("foot", "knob", [0.1, 0.006, 0.02], [[0, 0.003, -0.1], [0, 0.003, 0.1]]),
            box("grille", "grille", [0.004, 0.12, 0.165], [0.06, 0.088, -0.05]),
            box("slat", "slat", [0.006, 0.004, 0.165], [0.061, 0, -0.05], along={"n": 10, "from": [0, 0.036, 0], "to": [0, 0.14, 0]}),
            box("dial", "dial", [0.004, 0.05, 0.095], [0.06, 0.122, 0.088]),
            box("mark", "mark", [0.002, 0.012, 0.0015], [0.0625, 0.13, 0], along={"n": 12, "from": [0, 0, 0.048], "to": [0, 0, 0.128]}),
            box("band", "mark", [0.002, 0.0015, 0.085], [0.0625, 0.112, 0.088]),
            box("needle", "needle", [0.003, 0.04, 0.0025], [0.0632, 0.122, 0.072]),
            knob("knob", "knob", 0.015, 0.016, 0.06, 0.05, 0.06),
            knob("knob2", "knob", 0.015, 0.016, 0.06, 0.05, 0.11),
            sweep("handle", "chrome", [[0, 0.168, -0.115], [0, 0.205, -0.1], [0, 0.222, 0], [0, 0.205, 0.1], [0, 0.168, 0.115]], 0.0055),
            rod("aerial", "chrome", 0.004, [-0.045, 0.165, 0.125], [-0.075, 0.42, 0.14], 6, r1=0.002),
            sphere("aerialTip", "chrome", 0.004, [-0.075, 0.42, 0.14], sides=6),
        ], era="1955-2030")


def loudspeaker():
    # A FLOOR-STANDING LOUDSPEAKER (a tower: 20 cm wide, 30 deep, 1 m high): a veneered cabinet on a plinth and
    # spikes, its black baffle carrying a dome tweeter and two 16 cm bass-mid cones, a bass port near the floor
    y0 = 0.045
    return item("Loudspeaker", "electronics", "a floor-standing loudspeaker, 20 x 30 x 100 cm: a veneered cabinet on a plinth and spikes, a black baffle with a dome tweeter, two 16 cm cones in their rubber surrounds, a bass port -- facing +x",
        {"cabinet": {"pick": ["walnut", "oak", "#1f1f22", "paint-white"]}, "baffle": "#151517", "cone": "#55575c", "surround": "#232326", "trim": "aluminium",
         "dome": "#3b3d42", "plinth": "#1a1a1c", "port": "#060607"}, [
            box("cabinet", "cabinet", [0.3, 0.95, 0.2], [0, y0 + 0.475, 0]),
            box("baffle", "baffle", [0.006, 0.94, 0.19], [0.152, y0 + 0.475, 0]),
            box("plinth", "plinth", [0.34, 0.025, 0.26], [0, 0.0325, 0]),
            lathe("spike", "trim", [[0.008, 0.02], [0.001, 0]], [[0.15, 0, 0.11], [0.15, 0, -0.11], [-0.15, 0, 0.11], [-0.15, 0, -0.11]], sides=6),
            lathe("tweetPlate", "baffle", [[0, 0.004], [0.038, 0.004], [0.04, 0]], faces(0.155, 0.89, 0), sides=16),
            lathe("tweeter", "dome", [[0, 0.016], [0.01, 0.013], [0.014, 0.006], [0.015, 0.004]], faces(0.155, 0.89, 0), sides=14),
            *cone("woofer", 0.166, 0.72, 0, 0.075),
            *cone("woofer2", 0.166, 0.52, 0, 0.075),
            ring("port", "trim", 0.026, 0.004, faces(0.156, 0.16, 0)),
            lathe("portHole", "port", [[0, 0.0], [0.024, 0.0]], faces(0.156, 0.16, 0), sides=14),
        ], era="1970-2030")


# ---- THE KITCHEN AND THE UTILITY ROOM -----------------------------------------------------------------------------
def bottle(id_, mat, r, h, at, **k):
    """a bottle standing at `at` (its foot): body, shoulder, neck -- or several, `at` a list"""
    return lathe(id_, mat, [[0, 0], [r, 0], [r, h * 0.62], [r * 0.38, h * 0.8], [r * 0.34, h], [0, h]], at, sides=8, **k)


def jar(id_, mat, r, h, at, lid="trim", **k):
    """a jar with its lid: the glass body and a cap a shade narrower"""
    return [lathe(id_, mat, [[0, 0], [r, 0], [r, h], [0, h]], at, sides=10, **k),
            lathe(id_ + "Lid", lid, [[0, h], [r * 0.92, h], [r * 0.92, h * 1.15], [0, h * 1.15]], at, sides=10, **k)]


def door_bin():
    # A DOOR BIN (2026-11-22): the open-topped tray on the inside of a fridge's door -- its floor (`t` thick, role liner),
    # the clear lip along its open side (-x, `lip` thick, role bin), the two ends (role liner) -- the origin on the
    # floor's middle, `w` across z, `d` deep along x, `h` high
    return item("Door bin", "components", "a fridge door's bin: the floor, a clear front lip and two ends -- open at the top, its lip at -x (into the cabinet), w across z, d deep, h high, the origin on the floor's middle",
        {"liner": "plastic-white", "bin": "window-glass"}, [
            box("floor", "liner", ["d", "t", "w"], [0, 0, 0]),
            box("lip", "bin", ["lip", "h", "w"], ["-(d + lip) / 2 + 0.001", "(h - t) / 2", 0]),
            box("end", "liner", ["d", "h", "lip"], [0, "(h - t) / 2", "w / 2 - lip / 2"], mirror="z"),
        ], params={"w": 0.48, "d": 0.09, "h": 0.08, "lip": 0.006, "t": 0.008})


def fridge():
    # A FRIDGE-FREEZER (60 cm wide, 65 deep, 1.85 m high): a pressed cabinet, the fridge's door above and the freezer's
    # below, each with an upright bar handle on its opening edge (hinged on the right, +z), a display, the kick grille.
    # HOLLOW (2026-11-21): the cabinet's front is open (caps [back, no front]) onto two moulded white liners -- the
    # fridge's with three glass shelves, a crisper drawer and a few jars and bottles; the freezer's with three drawers
    # that slide out -- behind a face frame (stiles, top rail, the mullion between the two). The doors are HINGED at
    # the +z edge (open: out to 110 degrees); the fridge door carries its liner panel and three door bins with bottles,
    # marked `inside` (the game's static, shut build leaves them out).
    D, W, H = 0.65, 0.6, 1.85
    xf = D / 2 - 0.06     # (the cabinet's front: the doors stand on it)
    xb = -D / 2 + 0.045   # (the liners' back)
    fy0, fy1, zy0, zy1 = 0.79, H - 0.05, 0.09, 0.72   # (the fridge's and the freezer's insides, bottom to top)
    hw = W / 2 - 0.045                                # (the liners' half-width)
    sx1 = xf - 0.13                                   # (the shelves' front: clear of the door bins shut)
    sx = (xb + sx1) / 2
    pv = [xf + 0.002, 0, W / 2]                       # (the hinges' line: the doors' back, outer edge)
    shelves = [1.06, 1.33, 1.58]
    # (the freezer drawers: C drawer turned to face +x, a slab front with a moulded grip, its tray and two packs in it)
    drawers = [use(f"freezerDrawer{i}", "components/drawer", [xf - 0.012, y + 0.095, 0, 90, 0, 0],
                   {"front": "slab", "w": 0.46, "h": 0.19, "t": 0.012, "back": -0.012, "pull": "grip", "hy": 0.075, "hl": 0.2, "depth": 0.4, "travel": 0.4,
                    "floor": 0.008, "lift": 0, "wall": 0.008, "gap": 0, "rise": 0.15 / 0.19, "stock": 1},
                   {"front": "drawer", "tray": "drawer", "metal": "trim", "goods": f"food{i % 3}", "goods2": f"food{(i + 1) % 3}"}, inside=True)
               for i, y in enumerate([0.12, 0.33, 0.54])]   # (each drawer's bottom; front 0.19 high)
    # (the door bins: components/door-bin, one use laid at the three bins' bottoms; its roles liner and bin are the fridge's)
    door_bins = [use("bin", "modern/components/door-bin", [[xf - 0.05, y, 0] for y in (0.88, 1.18, 1.48)], {"w": 0.48, "d": 0.09, "h": 0.08}, inside=True),
                 bottle("milk", "milk", 0.04, 0.25, [xf - 0.05, 0.884, -0.17], inside=True),
                  bottle("juice", "juice", 0.035, 0.22, [xf - 0.05, 0.884, -0.08], inside=True),
                  bottle("wine", "bottleGreen", 0.036, 0.3, [xf - 0.05, 0.884, 0.15], inside=True),
                  bottle("sauce", "jar", 0.025, 0.14, [[xf - 0.05, 1.184, z] for z in (-0.18, -0.12, 0.1)], inside=True),
                  box("eggs", "liner", [0.07, 0.03, 0.2], [xf - 0.05, 1.5, 0], inside=True)]
    return item("Fridge-freezer", "electronics", "a fridge-freezer, 60 cm wide, 65 cm deep, 1.85 m high: a pressed steel cabinet, the fridge door above and the freezer door below, each rounded and with an upright bar handle on its opening edge, a small display, the hinge covers, a kick grille; hinged at the right (+z), the doors open onto white moulded liners -- glass shelves, a crisper drawer, jars and bottles, bins on the door, three freezer drawers that slide out -- facing +x",
        {"body": {"pick": ["paint-white", "paint-silver", "paint-black", "paint-cream"]},
         "metal": "aluminium", "grille": "#2a2b2e", "display": "screen", "hinge": "plastic-grey",
         "liner": "plastic-white", "shelf": "window-glass", "bin": "window-glass", "drawer": "#dfe6ea", "trim": "plastic-grey", "lamp": "lamp",
         "milk": "paint-white", "juice": "#e2a23a", "jar": "#a33b2a", "bottleGreen": "#2f5a35", "veg": "#5d8f3c", "tomato": "#c0392b",
         "food0": "#3a6fb0", "food1": "#c9c1ad", "food2": "#b24a3a"}, [
            loft("cabinet", "body", [[-D / 2, W / 2, 0.01, H], [xf, W / 2, 0.01, H]], [0.004, 0.025], seg=1, caps=[True, False]),
            # (the liners, seen from inside; the face frame over their edges and the cabinet's)
            loft("fridgeLiner", "liner", [[xb, hw, fy0, fy1], [xf - 0.01, hw, fy0, fy1]], 0.02, seg=1, caps=[True, False], double=True),
            loft("freezerLiner", "liner", [[xb, hw, zy0, zy1], [xf - 0.01, hw, zy0, zy1]], 0.02, seg=1, caps=[True, False], double=True),
            box("stile", "body", [0.02, H - 0.035, 0.046], [xf - 0.01, 0.01 + (H - 0.035) / 2, W / 2 - 0.023], mirror="z"),
            rod("rimCorner", "body", 0.025, [xf - 0.02, H - 0.025, W / 2 - 0.025], [xf, H - 0.025, W / 2 - 0.025], 16, mirror="z"),   # (the loft's rounded top corners)
            box("topRail", "body", [0.02, H - fy1, W - 0.05], [xf - 0.01, (H + fy1) / 2, 0]),
            box("mullion", "body", [0.02, fy0 - zy1, W - 0.09], [xf - 0.01, (fy0 + zy1) / 2, 0]),
            box("sill", "body", [0.02, zy0 - 0.01, W - 0.09], [xf - 0.01, (zy0 + 0.01) / 2, 0]),
            # (the fridge: the lamp, three glass shelves on their runners, the crisper under the lowest's cover)
            box("lamp", "lamp", [0.08, 0.012, 0.06], [xb + 0.12, fy1 - 0.012, 0], inside=True),
            box("shelf", "shelf", [sx1 - xb, 0.006, 2 * hw - 0.01], [[sx, y, 0] for y in shelves], inside=True),
            box("shelfEdge", "trim", [0.012, 0.016, 2 * hw - 0.01], [[sx1 - 0.006, y, 0] for y in shelves], inside=True),
            box("runner", "liner", [sx1 - xb, 0.01, 0.012], [[sx, y - 0.008, hw - 0.006] for y in shelves], mirror="z", inside=True),
            box("crisperCover", "shelf", [sx1 - xb, 0.006, 2 * hw - 0.01], [sx, 0.99, 0], inside=True),
            # (the crisper: C drawer turned to face +x -- a clear 8 mm slab front with a moulded grip near its top, on a
            #  clear tray 38 cm deep that slides out .45 of it, three heads of veg and two tomatoes in it (`stock` "veg"))
            use("crisper", "components/drawer", [sx1 - 0.024, fy0 + 0.095, 0, 90, 0, 0],
                {"front": "slab", "w": 2 * hw - 0.03, "h": 0.18, "t": 0.008, "back": 0, "pull": "grip", "hy": 0.075, "hl": 0.16, "gd": 0.008,
                 "depth": 0.38, "travel": 0.45, "floor": 0.005, "lift": 0, "wall": 0.005, "gap": 0.005, "rise": 0.85, "stock": "veg"},
                {"front": "bin", "tray": "bin", "metal": "trim", "goods": "veg", "goods2": "tomato"}, inside=True),
            *jar("jam", "jar", 0.04, 0.1, [[sx1 - 0.1, shelves[0] + 0.003, 0.15], [sx1 - 0.08, shelves[1] + 0.003, -0.16]], inside=True),
            *jar("pot", "milk", 0.055, 0.08, [sx1 - 0.15, shelves[0] + 0.003, -0.05], inside=True),
            box("cheese", "food1", [0.12, 0.05, 0.16], [sx1 - 0.15, shelves[1] + 0.028, 0.08], inside=True),
            bottle("bottle", "bottleGreen", 0.035, 0.28, [sx1 - 0.25, shelves[1] + 0.003, -0.02], inside=True),
            box("tub", "food0", [0.14, 0.07, 0.14], [sx1 - 0.2, shelves[2] + 0.038, 0.1], inside=True),
            *drawers,
            # (the doors, hinged at the +z edge, swinging out; the fridge's display and bins ride on it)
            hinge("fridgeDoor", pv, [
                loft("fridgeDoor", "body", [[xf + 0.002, W / 2 - 0.001, 0.765, H - 0.005], [D / 2, W / 2 - 0.002, 0.767, H - 0.008]], 0.02, seg=1),
                bar_handle("handle", D / 2, 0.95, 1.5, -W / 2 + 0.045, stand=0.04, r=0.011),
                box("display", "display", [0.002, 0.035, 0.09], [D / 2 + 0.001, 1.62, 0.1]),
                box("doorLiner", "liner", [0.016, fy1 - fy0 - 0.02, 2 * hw - 0.02], [xf - 0.006, (fy0 + fy1) / 2, 0], inside=True),
                *door_bins,
            ], max_=-110),
            hinge("freezerDoor", pv, [
                loft("freezerDoor", "body", [[xf + 0.002, W / 2 - 0.001, 0.07, 0.755], [D / 2, W / 2 - 0.002, 0.072, 0.753]], 0.02, seg=1),
                bar_handle("handleLow", D / 2, 0.5, 0.72, -W / 2 + 0.045, stand=0.04, r=0.011),
                box("doorLiner", "liner", [0.006, zy1 - zy0 - 0.02, 2 * hw - 0.02], [xf - 0.001, (zy0 + zy1) / 2, 0], inside=True),
            ], max_=-100),
            box("hingeCap", "hinge", [0.05, 0.015, 0.04], [[xf + 0.02, H + 0.0075, W / 2 - 0.035], [xf + 0.03, 0.76, W / 2 - 0.006]]),
            box("grille", "grille", [0.006, 0.05, W - 0.04], [xf + 0.03, 0.04, 0]),
            box("slot", "body", [0.003, 0.004, W - 0.08], [xf + 0.034, 0, 0], along={"n": 4, "from": [0, 0.026, 0], "to": [0, 0.056, 0]}),
        ], params={"open": 0}, era="1960-2030")


def bitten(w, y0, y1, cy, r, n=12):
    """an outline [[u, y]] for a plate: the half u >= 0 of the rectangle |u| <= w/2, y0..y1, with a half-round bite of
    radius r out of its edge u = 0 at height cy -- two of them (one turned yaw 180) make a front with a round hole"""
    bite = [[r * math.sin(math.pi * i / n), cy + r * math.cos(math.pi * i / n)] for i in range(n + 1)]
    return [[0, y0], [w / 2, y0], [w / 2, y1], [0, y1], *bite]


def washing_machine():
    # A FRONT-LOADING WASHING MACHINE (60 x 60 x 85 cm): the white cabinet, the control panel along its top (the
    # detergent drawer, the programme dial with its ring, a display, buttons), the round door with its bulging glass
    # porthole in a chrome ring, the rubber seal and the drum behind it, the door's pull, the filter flap at the foot.
    # OPEN (2026-11-21): the cabinet's front is two plates round the porthole's round hole (`bitten`), the rubber sleeve
    # and the deep steel drum behind it with three lifters and a little washing; the door HINGED at its -z side (open:
    # 100 degrees out), its glass see-through and dished into the drum; the detergent drawer SLIDES out of its dark
    # housing, its tray (marked `inside`) with the powder and conditioner compartments.
    D, W, H = 0.6, 0.6, 0.85
    xf = D / 2
    dy = 0.42
    yp = H - 0.135                  # (the control panel's bottom: the front plate runs up to it)
    dz, dw, dh, dyc = -0.18, 0.19, 0.085, H - 0.075   # (the detergent drawer: its middle across, width, height, middle up)
    return item("Washing machine", "electronics", "a front-loading washing machine, 60 x 60 x 85 cm: the cabinet, a control panel with the detergent drawer (it slides out), the programme dial, a display and buttons, the round door hinged at its side (its bulging glass porthole in a chrome ring) opening onto the rubber seal and the steel drum, the filter flap -- facing +x",
        {"body": "paint-white", "panel": {"pick": ["plastic-white", "#d6d8db", "#3a3d42"]}, "trim": {"pick": ["chrome", "plastic-grey", "aluminium"]},
         "glass": "window-glass", "seal": "#9da2a8", "drum": "aluminium", "knob": "plastic-white", "display": "screen", "button": "plastic-grey", "recess": "#55585e",
         "dark": "#1c1d20", "tray": "plastic-white", "powder": "#dfe7f0", "cloth": {"pick": ["#3b5a8a", "#a33b3b", "#d8d2c0"]}}, [
            loft("cabinet", "body", [[-D / 2, W / 2, 0.015, H], [xf, W / 2, 0.015, H]], [0.004, 0.012], seg=1, caps=[True, False]),
            plate("front", "body", bitten(W - 0.004, 0.017, yp, dy, 0.165), 0.01, [[xf - 0.005, 0, 0, 90, 0, 0], [xf - 0.005, 0, 0, -90, 0, 0]]),
            box("lip", "body", [0.01, 0.015, W - 0.03], [xf - 0.005, H - 0.0075, 0]),
            box("kick", "recess", [0.02, 0.015, W - 0.04], [xf - 0.03, 0.0075, 0]),
            # (the panel, round the drawer's opening; the drawer's dark housing behind it)
            box("panel", "panel", [0.008, 0.12, W / 2 - 0.004 - dz - dw / 2], [xf + 0.003, dyc, (W / 2 - 0.004 + dz + dw / 2) / 2]),
            box("panelEnd", "panel", [0.008, 0.12, W / 2 - 0.004 + dz - dw / 2], [xf + 0.003, dyc, (-W / 2 + 0.004 + dz - dw / 2) / 2]),
            box("panelRail", "panel", [0.008, (0.12 - dh) / 2, dw], [[xf + 0.003, dyc + (dh + 0.12) / 4, dz], [xf + 0.003, dyc - (dh + 0.12) / 4, dz]]),
            box("housing", "dark", [0.3, dh, dw], [xf - 0.151, dyc, dz]),
            # (the detergent drawer: C drawer turned to face +x -- a slab front 14 mm thick with a slim moulded grip near its
            #  foot (12 mm high, 2.5 mm proud: the strip it had when hand-built), its tray 25 cm deep sliding out .8 of it, two dividers and the powder in it (`stock` "powder"))
            use("drawer", "components/drawer", [xf + 0.002, dyc, dz, 90, 0, 0],
                {"front": "slab", "w": dw, "h": dh, "t": 0.014, "back": 0, "pull": "grip", "hy": -0.03, "hl": 0.08, "gh": 0.012, "gd": 0.0025, "depth": 0.25,
                 "floor": 0.006, "lift": 0.005, "wall": 0.006, "gap": 0.01, "rise": 0.06 / dh, "stock": "powder"},
                {"front": "panel", "metal": "recess", "goods": "powder"}),
            knob("dial", "knob", 0.03, 0.028, xf + 0.007, H - 0.075, 0.06),
            ring("dialRing", "button", 0.045, 0.0025, faces(xf + 0.008, H - 0.075, 0.06)),
            box("display", "display", [0.002, 0.03, 0.08], [xf + 0.008, H - 0.06, 0.185]),
            box("button", "button", [0.006, 0.012, 0.018], [xf + 0.009, H - 0.1, 0], along={"n": 3, "from": [0, 0, 0.155], "to": [0, 0, 0.215]}),
            # (behind the porthole: the rubber sleeve, the drum, its lifters, a little washing)
            ring("seal", "seal", 0.155, 0.018, faces(xf + 0.004, dy, 0)),
            lathe("sleeve", "seal", [[0.168, 0.0], [0.162, -0.03], [0.152, -0.06]], faces(xf, dy, 0), caps=False, double=True, sides=24),
            lathe("drum", "drum", [[0.152, -0.06], [0.2, -0.09], [0.215, -0.11], [0.215, -0.42], [0.0, -0.43]], faces(xf, dy, 0), caps=False, double=True, sides=24),
            box("lifter", "drum", [0.28, 0.035, 0.03], [[xf - 0.26, dy + 0.2 * math.cos(math.radians(a)), 0.2 * math.sin(math.radians(a)), 0, -a, 0] for a in (60, 180, 300)]),
            sphere("washing", "cloth", 0.09, [[xf - 0.25, dy - 0.15, 0.05], [xf - 0.33, dy - 0.14, -0.08]], stretch=[1.2, 0.55, 1.0], sides=8),
            # (the door, hinged at its -z side: the chrome ring, the bulging glass dished into the drum, the pull)
            hinge("door", [xf + 0.02, dy, -0.2], [
                lathe("glass", "glass", [[0, 0.055], [0.06, 0.052], [0.11, 0.04], [0.145, 0.018], [0.15, 0.006]], faces(xf, dy, 0), caps=False, double=True, sides=24),
                lathe("bowl", "glass", [[0.15, 0.006], [0.13, -0.02], [0.1, -0.045], [0.05, -0.06], [0, -0.062]], faces(xf, dy, 0), caps=False, double=True, sides=20),
                ring("doorRing", "trim", 0.165, 0.028, faces(xf + 0.02, dy, 0)),
                box("pull", "trim", [0.03, 0.08, 0.025], [xf + 0.03, dy, 0.19]),
            ], max_=100),
            box("hinge", "trim", [0.02, 0.03, 0.02], [[xf + 0.01, dy + 0.09, -0.185], [xf + 0.01, dy - 0.09, -0.185]]),
            box("flap", "panel", [0.004, 0.08, 0.1], [xf + 0.002, 0.075, 0.2]),
        ], params={"open": 0}, era="1960-2030")


def microwave():
    # A MICROWAVE OVEN (48 x 28 x 36 cm, on a worktop): the cabinet, the door with its dark mesh window and a pull,
    # the control panel to its right (-z, the user facing it) (a display, a keypad, a dial). OPEN (2026-11-21): the
    # cabinet's front is open onto the cavity -- its enamel lining, the light, the glass turntable on its roller ring
    # with a bowl on it -- behind a face frame; the door HINGED at its left edge (+z, the user facing it), swinging out
    # to 95 degrees.
    D, W, H = 0.36, 0.48, 0.28
    xf = D / 2
    xc = xf - 0.013                  # (the face frame's front: the door's back stands 3 mm before it)
    cz0, cz1, cy0, cy1, cx0 = -0.095, 0.225, 0.04, 0.25, -0.15   # (the cavity: across, up, its back)
    cz, cy = (cz0 + cz1) / 2, (cy0 + cy1) / 2
    cw, ch, cd = cz1 - cz0, cy1 - cy0, xc - cx0
    return item("Microwave", "electronics", "a countertop microwave oven, 48 x 28 x 36 cm: the cabinet on four feet, the door with its dark mesh window and a pull, hinged at its left edge and opening onto the lit cavity with its glass turntable, the control panel to its right (-z, the user facing it) with a display, a keypad and a dial -- facing +x",
        {"body": {"pick": ["paint-silver", "paint-white", "plastic-black", "steel"]}, "door": "#1c1d20", "window": "#2a3038", "panel": "#26272b",
         "display": "#0f2a1c", "button": "plastic-grey", "knob": "aluminium", "foot": "rubber", "cavity": "#d9d6cc", "plate": "glass-light", "roller": "plastic-grey",
         "lamp": "lamp", "bowl": {"pick": ["#e9e4d8", "#c9d8e0", "#d8b48a"]}}, [
            loft("cabinet", "body", [[-D / 2, W / 2, 0.012, H], [xc, W / 2, 0.012, H]], [0.005, 0.02], seg=1, caps=[True, False]),
            box("foot", "foot", [0.03, 0.012, 0.03], [[xf - 0.04, 0.006, W / 2 - 0.04], [xf - 0.04, 0.006, -W / 2 + 0.04], [-xf + 0.04, 0.006, W / 2 - 0.04], [-xf + 0.04, 0.006, -W / 2 + 0.04]]),
            # (the face frame round the cavity's mouth, flush with the cabinet's front)
            box("frameTop", "body", [0.012, H - cy1 - 0.002, W - 0.04], [xc - 0.006, (H + cy1) / 2 - 0.001, 0]),
            rod("frameCorner", "body", 0.02, [xc - 0.012, H - 0.02, W / 2 - 0.02], [xc, H - 0.02, W / 2 - 0.02], 16, mirror="z"),   # (the loft's rounded top corners)
            box("frameSill", "body", [0.012, cy0 - 0.014, W - 0.006], [xc - 0.006, (cy0 + 0.014) / 2, 0]),
            box("frameSide", "body", [0.012, H - 0.02 - cy0, W / 2 - 0.003 - cz1], [xc - 0.006, (H - 0.02 + cy0) / 2, (cz1 + W / 2 - 0.003) / 2]),
            box("frameMid", "body", [0.012, H - 0.02 - cy0, cz0 + W / 2 - 0.003], [xc - 0.006, (H - 0.02 + cy0) / 2, (cz0 - W / 2 + 0.003) / 2]),
            # (the cavity: back, floor, roof, sides; the light; the turntable on its roller ring, a bowl on it)
            box("cavityBack", "cavity", [0.006, ch, cw], [cx0 + 0.003, cy, cz]),
            box("cavityFloor", "cavity", [cd, 0.006, cw], [(xc + cx0) / 2, cy0 + 0.003, cz]),
            box("cavityRoof", "cavity", [cd, 0.006, cw], [(xc + cx0) / 2, cy1 - 0.003, cz]),
            box("cavitySide", "cavity", [cd, ch, 0.006], [[(xc + cx0) / 2, cy, cz0 + 0.003], [(xc + cx0) / 2, cy, cz1 - 0.003]]),
            box("lamp", "lamp", [0.04, 0.03, 0.002], [-0.02, cy1 - 0.04, cz1 - 0.007], inside=True),
            ring("roller", "roller", 0.07, 0.006, [(xc + cx0) / 2, cy0 + 0.012, cz], inside=True),
            lathe("turntable", "plate", [[0, 0.02], [0.13, 0.02], [0.135, 0.026], [0.137, 0.03], [0, 0.03]], [(xc + cx0) / 2, cy0, cz], sides=24, inside=True),
            lathe("bowl", "bowl", [[0, 0.03], [0.05, 0.03], [0.07, 0.055], [0.075, 0.08], [0.07, 0.08], [0.064, 0.058], [0.045, 0.036], [0, 0.036]], [(xc + cx0) / 2 + 0.01, cy0, cz + 0.02], sides=14, inside=True),
            # (the door, hinged at its +z edge, opening out to the user's left)
            hinge("door", [xf - 0.01, 0, 0.235], [
                box("door", "door", [0.014, H - 0.03, 0.34], [xf - 0.003, H / 2 + 0.006, 0.065]),
                box("window", "window", [0.002, H - 0.11, 0.25], [xf + 0.005, H / 2 + 0.008, 0.075]),
                box("pull", "knob", [0.016, 0.16, 0.014], [xf + 0.01, H / 2 + 0.006, -0.093]),
                box("doorLiner", "cavity", [0.003, ch - 0.01, cw - 0.01], [xf - 0.0115, cy, cz], inside=True),
            ], max_=-95),
            box("panel", "panel", [0.01, H - 0.03, 0.12], [xf - 0.005, H / 2 + 0.006, -0.172]),
            box("display", "display", [0.002, 0.025, 0.07], [xf + 0.001, H - 0.045, -0.172]),
            *[box(f"keys{r}", "button", [0.004, 0.014, 0.022], [xf + 0.001, H - 0.085 - r * 0.023, 0], along={"n": 3, "from": [0, 0, -0.202], "to": [0, 0, -0.142]}) for r in range(4)],
            knob("dial", "knob", 0.019, 0.016, xf, 0.06, -0.172),
        ], params={"open": 0}, era="1975-2030")


def cooker():
    # A FREESTANDING COOKER (60 x 60 cm, the hob at 90 cm): four gas burners under cast-iron pan supports, a
    # control panel of five knobs, the oven's door with its window and a bar handle, a storage drawer, the plinth.
    # OPEN (2026-11-21): the body is hollow round the oven -- the cavity's dark enamel lining, its lamp, four pairs of
    # runners, a wire rack and a roasting tin -- behind a face frame; the door is a frame round a see-through window,
    # HINGED along its BOTTOM edge (about z) so it drops down flat; the storage drawer SLIDES out, its tray (marked
    # `inside`) holding a baking tray.
    D, W, H = 0.6, 0.6, 0.9
    xf = D / 2
    oy0, oy1 = 0.27, 0.775            # (the oven's opening in the body, bottom and top)
    cx0, cx1, cz, cy0, cy1 = -0.24, xf - 0.01, 0.235, 0.29, 0.755   # (the cavity: back, front, half-width, floor, roof)
    cxm, cd = (cx0 + cx1) / 2, cx1 - cx0
    ry = 0.488                        # (the rack's height, on the second runner up)
    burners = [(-0.12, -0.14, 0.045), (-0.12, 0.14, 0.035), (0.11, -0.14, 0.035), (0.11, 0.14, 0.05)]
    parts = [
        box("bodyLow", "body", [D, oy0 - 0.075, W], [0, (oy0 + 0.075) / 2, 0]),
        box("bodyHigh", "body", [D, H - 0.005 - oy1, W], [0, (H - 0.005 + oy1) / 2, 0]),
        box("side", "body", [D, oy1 - oy0, 0.03], [0, (oy0 + oy1) / 2, W / 2 - 0.015], mirror="z"),
        box("back", "body", [0.04, oy1 - oy0, W - 0.06], [-D / 2 + 0.02, (oy0 + oy1) / 2, 0]),
        # (the oven: its lining, the face frame over the lining's edges, the lamp, the runners, a rack, a tin)
        box("cavityFloor", "cavity", [cd, cy0 - oy0, 2 * cz + 0.07], [cxm, (oy0 + cy0) / 2, 0]),
        box("cavityRoof", "cavity", [cd, oy1 - cy1, 2 * cz + 0.07], [cxm, (oy1 + cy1) / 2, 0]),
        box("cavityWall", "cavity", [cd, cy1 - cy0, W / 2 - 0.03 - cz], [cxm, (cy0 + cy1) / 2, (cz + W / 2 - 0.03) / 2], mirror="z"),
        box("cavityBack", "cavity", [0.02, cy1 - cy0, 2 * cz], [cx0 - 0.01, (cy0 + cy1) / 2, 0]),
        box("frameSide", "body", [0.01, oy1 - oy0, W / 2 - 0.03 - cz], [xf - 0.005, (oy0 + oy1) / 2, (cz + W / 2 - 0.03) / 2], mirror="z"),
        box("frameRail", "body", [0.01, cy0 - oy0, 2 * cz], [[xf - 0.005, (oy0 + cy0) / 2, 0], [xf - 0.005, (oy1 + cy1) / 2, 0]]),
        box("ovenLamp", "lamp", [0.002, 0.03, 0.03], [cx0 + 0.001, cy1 - 0.04, cz - 0.04]),
        box("runner", "cavity", [cd - 0.06, 0.008, 0.012], [[cxm, y, cz - 0.006] for y in (0.38, 0.48, 0.58, 0.68)], mirror="z"),
        rod("rackFrame", "rack", 0.0035, [cx0 + 0.02, ry, -cz + 0.008], [cx1 - 0.03, ry, -cz + 0.008], 5, at=[[0, 0, 0], [0, 0, 2 * cz - 0.016]]),
        rod("rackEnd", "rack", 0.0035, [0, ry, -cz + 0.008], [0, ry, cz - 0.008], 5, at=[[cx0 + 0.02, 0, 0], [cx1 - 0.03, 0, 0]]),
        rod("rackWire", "rack", 0.0025, [cx0 + 0.02, ry, 0], [cx1 - 0.03, ry, 0], 4, at=[[0, 0, -cz + 0.008 + (2 * cz - 0.016) * k / 10] for k in range(1, 10)]),
        box("tin", "tin", [0.36, 0.006, 0.36], [cxm, 0.395, 0]),
        box("tinSide", "tin", [0.36, 0.04, 0.006], [[cxm, 0.412, 0.177], [cxm, 0.412, -0.177]]),
        box("tinEnd", "tin", [0.006, 0.04, 0.36], [[cxm + 0.177, 0.412, 0], [cxm - 0.177, 0.412, 0]]),
        box("plinth", "plinth", [D - 0.05, 0.08, W - 0.02], [-0.025, 0.04, 0]),
        box("hob", "hob", [D, 0.01, W], [0, H, 0]),
        box("upstand", "body", [0.03, 0.06, W], [-D / 2 + 0.015, H + 0.035, 0]),
        box("panel", "panel", [0.012, 0.085, W - 0.004], [xf + 0.001, H - 0.06, 0]),
        *[knob(f"knob{i}", "knob", 0.017, 0.024, xf + 0.007, H - 0.06, -0.22 + i * 0.11) for i in range(5)],
        # (the oven door: a frame round the window, hinged along its bottom front edge -- open, it lies down flat)
        hinge("ovenDoor", [xf + 0.03, oy0, 0], [
            box("doorBottom", "door", [0.03, 0.095, W - 0.01], [xf + 0.015, oy0 + 0.0475, 0]),
            box("doorTop", "door", [0.03, 0.135, W - 0.01], [xf + 0.015, 0.7025, 0]),
            box("doorStile", "door", [0.03, 0.27, 0.085], [xf + 0.015, 0.5, 0.2525], mirror="z"),
            box("window", "window", [0.004, 0.285, 0.435], [xf + 0.022, 0.5, 0]),
            bar_handle("handle", xf + 0.03, -0.24, 0.24, 0.72, stand=0.035, along="z"),
        ], axis=(0, 0, 1), max_=-90),
        # (the storage drawer: C drawer turned to face +x -- a slab front 2 cm thick with its bar handle (10 sides, 25 mm
        #  off, r 7 mm; its posts 8-sided, r 5.6 mm, 15 mm in from the ends: the oven door's, a size smaller), on a steel
        #  tray 45 cm deep (the cooker's own `tray` role) that slides out .8 of it, a baking sheet in it (`stock`))
        use("drawer", "components/drawer", [xf + 0.015, 0.175, 0, 90, 0, 0],
            {"front": "slab", "w": W - 0.01, "h": 0.16, "t": 0.02, "back": -0.02, "pull": "hbar", "hy": 0.025, "hl": 0.24, "stand": 0.025, "r": 0.007, "sides": 10, "pr": 0.0056, "psides": 8, "inset": 0.015, "depth": 0.45,
             "floor": 0.008, "lift": 0.006, "wall": 0.008, "gap": 0.035, "rise": 0.75, "stock": "sheet"},
            {"front": "door", "goods": "tin"}),
    ]
    for i, (bx, bz, r) in enumerate(burners):
        parts += [lathe(f"burner{i}", "burner", [[0, 0.03], [r * 0.8, 0.028], [r, 0.016], [r * 1.15, 0.005], [r * 1.5, 0.0]], [bx, H + 0.005, bz], sides=16),
                  lathe(f"cap{i}", "cap", [[0, 0.036], [r * 0.6, 0.034], [r * 0.65, 0.026]], [bx, H + 0.005, bz], sides=12)]
    # (the pan supports: two cast-iron grids, each over a pair of burners -- bars along x and z, on little feet)
    gy = H + 0.042
    parts += [
        box("gridX", "iron", [D - 0.06, 0.012, 0.012], [[0, gy, z] for z in (-0.275, -0.015, 0.015, 0.275)]),
        box("gridZ", "iron", [0.012, 0.012, W / 2 - 0.04], [[x, gy, s * 0.145] for x in (-0.27, -0.005, 0.27) for s in (-1, 1)]),
        box("finger", "iron", [0.07, 0.01, 0.01], [[bx + dx, gy - 0.002, bz + dz] for bx, bz, _ in burners for dx, dz in ((0.065, 0), (-0.065, 0))]),
        box("gridFoot", "iron", [0.012, gy - H - 0.005, 0.012], [[x, (gy + H) / 2, z] for x in (-0.27, 0.27) for z in (-0.275, 0.275)]),
    ]
    return item("Cooker", "electronics", "a freestanding gas cooker, 60 x 60 cm, the hob at 0.9 m: four burners under cast-iron pan supports, a control panel of five knobs, the oven door with its window and a bar handle (hinged at the bottom, it drops down onto the enamelled oven with its rack), a storage drawer that slides out, a plinth -- facing +x",
        {"body": {"pick": ["paint-white", "steel", "paint-black", "paint-cream"]}, "hob": "steel", "panel": "#2b2c30", "knob": "aluminium", "door": "#1c1d20",
         "window": "window-glass", "metal": "aluminium", "burner": "#3a3b3f", "cap": "#141416", "iron": "#1d1e20", "plinth": "#202022",
         "cavity": "#2c2f36", "lamp": "lamp", "rack": "chrome", "tin": "#3a3b3f", "tray": "steel"}, parts, params={"open": 0}, era="1950-2030")


# ---- SMALL THINGS -------------------------------------------------------------------------------------------------
def smartphone():
    # A SMARTPHONE (14.7 x 7.15 x 0.78 cm) lying on its back: a rounded aluminium body, the glass screen in a thin
    # black border (the shared screen, turned to face up), the volume and power buttons on its sides, the earpiece slot
    L, hw, t = 0.147, 0.0358, 0.0078
    body = [[-L / 2, 0.026, 0, t], [-L / 2 + 0.0012, 0.0325, 0, t], [-L / 2 + 0.004, 0.0352, 0, t], [-L / 2 + 0.01, hw, 0, t],
            [L / 2 - 0.01, hw, 0, t], [L / 2 - 0.004, 0.0352, 0, t], [L / 2 - 0.0012, 0.0325, 0, t], [L / 2, 0.026, 0, t]]
    return item("Smartphone", "electronics", "a smartphone of the 2020s, 14.7 x 7.15 x 0.78 cm, lying on its back: a rounded body, the glass screen in a thin border facing up, volume and power buttons on its sides, the earpiece slot -- its top toward -x",
        {"body": {"pick": ["#2b2d31", "paint-silver", "#3c4a5c", "#e5ddd0", "#6b2232"]}, "case": "#0b0c0e", "glass": "#18202b", "slot": "#2a2b2e"}, [
            loft("body", "body", body, [0.0028, 0.0028], seg=2, corner=3),
            use("screen", C + "screen", [0, t - 0.0018, 0, 0, 0, 90], {"w": 0.064, "h": 0.138, "b": 0.0022, "t": 0.0015}),
            box("slot", "slot", [0.0015, 0.0006, 0.01], [-0.0712, t + 0.0012, 0]),
            box("volume", "body", [0.022, 0.0035, 0.0014], [-0.03, t / 2, -hw - 0.0004]),
            box("power", "body", [0.014, 0.0035, 0.0014], [-0.025, t / 2, hw + 0.0004]),
        ], era="2010-2030")


def printer():
    # AN ALL-IN-ONE PRINTER (43 x 36 x 20 cm): the moulded body, the scanner's lid on top, a control panel tilted up at
    # the front with its small screen and buttons, the output slot with its tray pulled out and a sheet on it, the
    # paper cassette below
    D, W = 0.36, 0.43
    xf = D / 2
    ang = -30
    nx, ny = math.sin(math.radians(-ang)), math.cos(math.radians(-ang))
    px, py, pz = xf - 0.005, 0.158, -0.11
    return item("Printer", "electronics", "an all-in-one inkjet printer and scanner, 43 x 36 x 20 cm: a moulded body, the scanner's lid, a control panel tilted at the front with a small screen and buttons, the output tray pulled out with a printed sheet, the paper cassette -- facing +x",
        {"body": {"pick": ["plastic-black", "plastic-white", "#3a3c40"]}, "lid": {"pick": ["#26272b", "plastic-grey"]}, "trim": "#1b1c1f", "slot": "#08080a",
         "tray": "plastic-grey", "paper": "paint-white", "display": "#1b2c3a", "button": "plastic-grey", "led": "lamp-green"}, [
            loft("body", "body", [[-D / 2, W / 2, 0.0, 0.17], [xf, W / 2, 0.0, 0.17]], [0.008, 0.015], seg=1),
            loft("lid", "lid", [[-D / 2 + 0.005, W / 2 - 0.004, 0.172, 0.198], [xf - 0.02, W / 2 - 0.004, 0.172, 0.198]], [0.002, 0.01], seg=1),
            box("panel", "trim", [0.05, 0.018, 0.17], [px, py, pz, 0, 0, ang]),
            box("display", "display", [0.03, 0.002, 0.06], [px + nx * 0.0095, py + ny * 0.0095, pz + 0.035, 0, 0, ang]),
            box("button", "button", [0.012, 0.003, 0.012], [px + nx * 0.0095, py + ny * 0.0095, 0, 0, 0, ang], along={"n": 4, "from": [0, 0, pz - 0.07], "to": [0, 0, pz - 0.015]}),
            box("led", "led", [0.004, 0.003, 0.004], [px + nx * 0.0095, py + ny * 0.0095, pz + 0.075, 0, 0, ang]),
            box("slot", "slot", [0.004, 0.022, 0.3], [xf + 0.0005, 0.095, 0.04]),
            box("tray", "tray", [0.15, 0.004, 0.26], [xf + 0.07, 0.085, 0.04]),
            box("trayLip", "tray", [0.006, 0.02, 0.26], [xf + 0.145, 0.093, 0.04]),
            box("sheet", "paper", [0.14, 0.0015, 0.21], [xf + 0.05, 0.0875, 0.04]),
            box("cassette", "trim", [0.006, 0.05, 0.38], [xf + 0.001, 0.035, 0]),
            box("cassettePull", "slot", [0.004, 0.008, 0.08], [xf + 0.005, 0.045, 0]),
        ], era="1995-2030")


def coiled_cord(A, B, Cp, turns=16, r=0.006, per=6):
    """a telephone's coiled cord: a helix of radius r wound round the curve A -> B -> C (a quadratic Bezier), `per`
    points a turn"""
    n = turns * per
    pts = []
    def bez(t): return [(1 - t) ** 2 * A[i] + 2 * (1 - t) * t * B[i] + t * t * Cp[i] for i in range(3)]
    for i in range(n + 1):
        t = i / n
        p, q = bez(t), bez(min(1, t + 1e-3) if t < 1 else t)
        if t >= 1: q, p = p, bez(t - 1e-3)
        T = [q[k] - p[k] for k in range(3)]; lt = math.sqrt(sum(v * v for v in T)) or 1; T = [v / lt for v in T]
        up = [0, 1, 0] if abs(T[1]) < 0.9 else [1, 0, 0]
        N = [up[1] * T[2] - up[2] * T[1], up[2] * T[0] - up[0] * T[2], up[0] * T[1] - up[1] * T[0]]; ln = math.sqrt(sum(v * v for v in N)); N = [v / ln for v in N]
        Bv = [T[1] * N[2] - T[2] * N[1], T[2] * N[0] - T[0] * N[2], T[0] * N[1] - T[1] * N[0]]
        a = 2 * math.pi * i / per
        c = bez(t)
        pts.append([c[k] + r * (math.cos(a) * N[k] + math.sin(a) * Bv[k]) for k in range(3)])
    return pts


def desk_phone():
    # A DESK TELEPHONE (an office handset phone of the 1990s-2000s, 20 x 22 cm): the wedge-shaped base, a keypad of
    # twelve keys and a small display on its sloping face, the handset lying in its cradle on the left, its coiled cord
    top = lambda x: 0.055 - 0.2 * x     # (the slope's height along x)
    ang = -math.degrees(math.atan(0.2))
    hz = 0.05
    keys = []
    for r in range(4):
        for cc in range(3):
            x = -0.01 + r * 0.024
            keys.append([x, top(x) + 0.002, -0.03 - cc * 0.028, 0, 0, ang])
    return item("Desk telephone", "electronics", "an office desk telephone of the 1990s-2000s: a wedge-shaped base, twelve keys and a small display on its sloping face, the handset lying in its cradle, its coiled cord -- facing +x",
        {"body": {"pick": ["plastic-black", "#d7d3c8", "#3a3c40"]}, "key": "plastic-grey", "display": "#a9b59a", "cord": "plastic-black"}, [
            loft("base", "body", [[-0.1, 0.1, 0, 0.075], [0.1, 0.1, 0, 0.035]], [0.006, 0.012], seg=1),
            box("key", "key", [0.016, 0.006, 0.02], keys),
            box("display", "display", [0.03, 0.002, 0.075], [-0.06, top(-0.06) + 0.0005, -0.058, 0, 0, ang]),
            box("cradle", "body", [0.16, 0.012, 0.06], [0.0, top(0.0) + 0.002, hz, 0, 0, ang]),
            sphere("ear", "body", 0.03, [-0.072, top(-0.072) + 0.02, hz, 0, 0, ang], stretch=[1.05, 0.6, 0.9], sides=12),
            sphere("mouth", "body", 0.03, [0.072, top(0.072) + 0.02, hz, 0, 0, ang], stretch=[1.05, 0.6, 0.9], sides=12),
            rod("grip", "body", 0.015, [-0.072, top(-0.072) + 0.03, hz], [0.072, top(0.072) + 0.03, hz], 10),
            sweep("cord", "cord", coiled_cord([0.1, top(0.1) + 0.02, hz], [0.16, 0.0, 0.11], [-0.03, 0.006, 0.105], turns=14, per=4), 0.0016, seg=2, sides=4),   # (2026-11-22: 4 points a turn, the sweep rounding them -- was 6, 1930 tris)
        ], era="1985-2030")


def write_all():
    write("modern/components/door-bin", door_bin(), "components")
    for name, f in [("desktop-computer", desktop), ("laptop", laptop), ("television", television), ("fridge-freezer", fridge),
                    ("washing-machine", washing_machine), ("microwave", microwave), ("cooker", cooker), ("smartphone", smartphone),
                    ("radio", radio), ("loudspeaker", loudspeaker), ("printer", printer), ("desk-phone", desk_phone)]:
        write("modern/electronics/" + name, f(), "electronics")

GROUPS = {"electronics": "electronics", "components": "components"}
