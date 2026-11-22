"""MODERN FURNITURE (2026-11-20; docs/modern.md): the furniture of the 20th and 21st centuries -- the sofa and the
armchair, the office swivel chair, the desk, the dining table and its chair, the coffee table, the bed, the wardrobe,
the bookshelf, the TV stand, a fitted kitchen, the bar stool, the floor lamp and the desk lamp.

THE FRAME is the PERIOD FURNITURE'S (assets/items/furniture/*.json), not the vehicles': the origin on the floor under
the piece's middle, its WIDTH along x, its FRONT toward +z and its back toward -z (a chair's back at -z, so one sits
facing +z; a wardrobe's doors at +z; a kitchen run's back against a wall at -z). A bed lies ALONG x with its head at
-x, as every period bed does, and its `bed` marker is turned 90 degrees so that the marker's +z is the foot (docs/items.md,
the markers). Seats carry a `seat` marker { w, d, top } at the origin and `spot`s (pose sit) where one person sits;
tables carry the `spot`s of the places round them, their `face` a heading (0 +x, pi/2 -z: a place on the +z side
faces -z, toward the table).

Three shared components are written here (group "components"), in that same frame:
- `modern/components/slab-door`: the flat door or drawer front of every modern carcass -- a kitchen's, a wardrobe's,
  a desk pedestal's, a TV stand's -- its back at z 0 and its face at +z, with a bar handle, a knob or none.
- `modern/components/bar-handle`: the bar on two posts -- the slab door's pull, the appliances' handles.
- `modern/components/star-base`: the five-star base of a swivel chair, its arms and castors round the y axis.
"""
import math, random
from kit import item, r3, hinge, slide, box, rod, lathe, loft, sphere, ring, sweep, plate, use, write, across, arc

C = "modern/components/"
HALF_PI = 1.5707963


# ---- SHARED COMPONENTS --------------------------------------------------------------------------------------------
def slab_door():
    # A SLAB DOOR (or a drawer's front): a plain flat panel, `w` wide (x) by `h` high (y), `t` thick, its back at z 0
    # and its face at z t, centred on its origin (`anchor` 0; 1: its face at z 0, as the period components/panel-door
    # stands -- the same param there, its default 1); a handle placed at (hx, hy) on its face: `pull` "hbar" a bar across,
    # "vbar" a bar upright (both `hl` long: C bar-handle, on two posts standing 28 mm off), "knob", "lip" an aluminium
    # strip along its top edge (a handleless kitchen's), "grip" a moulded strip `hl` long (a freezer drawer's), "none"
    # (a push-to-open front). The bars take `stand`, `r` and `sides` on to C bar-handle (its own defaults: 28 mm, 6.5 mm,
    # 8), and `pr`, `psides`, `inset` for its posts (5 mm, 6, 12 mm). The grip is `gh` high (20 mm) and stands `gd` proud
    # of the face (7 mm; 3 mm of it sunk into the face). `frame` (2026-11-22; 0, the default: the flat slab): a SHAKER
    # front instead -- the period components/panel-door (anchor 0, so it stands as the slab does; its knob off; its wood
    # the slab's `front`), its stiles and rails `frame` wide round the sunk panel, the same pull on the frame's face; the
    # sunk panel is role `panel` (the slab's `front` unless the user maps it: a shade darker, another wood)
    return item("Slab door", "components", "a modern carcass's flat door or drawer front: a plain slab looking +z, its back at z 0 and its face at t (`anchor` 0, the default; 1: its face at z 0, as components/panel-door stands), with a bar handle across or upright (`stand`, `r`, `sides`, `pr`, `psides`, `inset` passed on to modern/components/bar-handle), a knob, an edge lip, a moulded grip (`gh` high, `gd` proud) or nothing -- the kitchen's, the wardrobe's, the desk's, the TV stand's; `frame` > 0: a shaker front instead of the slab (components/panel-door, anchor 0, its stiles and rails that wide, no knob, role front; its sunk panel role panel, the front unless mapped)",
        {"front": "plastic-white", "metal": "aluminium", "panel": "front"}, [
            box("slab", "front", ["w", "h", "t"], [0, 0, "t / 2 - t * anchor"], when={"frame": 0}),
            use("shaker", "components/panel-door", [0, 0, "0 - t * anchor"], {"w": "w", "h": "h", "t": "t", "s": "frame", "anchor": 0, "knob": 0},
                {"wood": "front"}, when="frame"),
            use("hbar", C + "bar-handle", ["hx", "hy", "t - t * anchor"], {"l": "hl", "along": "across", "stand": "stand", "r": "r", "sides": "sides", "pr": "pr", "psides": "psides", "inset": "inset"}, when={"pull": "hbar"}),
            use("vbar", C + "bar-handle", ["hx", "hy", "t - t * anchor"], {"l": "hl", "along": "upright", "stand": "stand", "r": "r", "sides": "sides", "pr": "pr", "psides": "psides", "inset": "inset"}, when={"pull": "vbar"}),
            lathe("knob", "metal", [[0.006, 0], [0.006, 0.014], [0.014, 0.02], [0.013, 0.028], [0, 0.03]], ["hx", "hy", "t - t * anchor", 0, 90, 0], sides=10, when={"pull": "knob"}),
            box("lip", "metal", ["w", 0.014, 0.012], [0, "h / 2 - 0.007", "t + 0.003 - t * anchor"], when={"pull": "lip"}),
            box("grip", "metal", ["hl", "gh", "gd + 0.003"], ["hx", "hy", "t + gd / 2 - 0.0015 - t * anchor"], when={"pull": "grip"}),
        ], params={"w": 0.6, "h": 0.7, "t": 0.018, "pull": "hbar", "hx": 0, "hy": 0, "hl": 0.16, "anchor": 0,
                 "stand": 0.028, "r": 0.0065, "sides": 8, "pr": 0.005, "psides": 6, "inset": 0.012, "gh": 0.02, "gd": 0.007, "frame": 0})


def bar_handle():
    # A BAR HANDLE: a round bar `l` long standing `stand` off the face it is fixed to (z 0; the bar at z stand), on two
    # posts `inset` in from its ends; `along` "across" (x) or "upright" (y); the bar `r` round with `sides`, the posts
    # `pr` with `psides` -- a slab door's pull, an appliance's (turned to face +x by its `at`)
    def bar(tag, a, b):
        return [rod(tag, "metal", "r", a("0 - l / 2", "stand"), a("l / 2", "stand"), "sides", when={"along": b}),
                rod(tag + "Post", "metal", "pr", a(0, 0), a(0, "stand"), "psides", at=[a("0 - l / 2 + inset", 0), a("l / 2 - inset", 0)], when={"along": b})]
    return item("Bar handle", "components", "a bar handle: a round bar on two posts standing off the face it is fixed to (+z), across or upright -- a slab door's, an appliance's",
        {"metal": "aluminium"}, [
            *bar("bar", lambda u, z: [u, 0, z], "across"),
            *bar("vbar", lambda u, z: [0, u, z], "upright"),
        ], params={"l": 0.16, "stand": 0.028, "r": 0.0065, "pr": 0.005, "inset": 0.012, "sides": 8, "psides": 6, "along": "across"})


def star_base():
    # THE FIVE-STAR BASE of a swivel chair (an office chair's, a drafting stool's): `n` tapered arms out from a hub to
    # radius `R`, a twin-wheeled castor under each end (their axles across the arm), the hub's socket for the gas lift
    # at y `top`. Standing on the floor at the origin.
    return item("Five-star base", "components", "the five-star base of a swivel chair: tapered arms from a hub, a twin-wheeled castor at each arm's end, the socket for the gas lift -- on the floor, about y",
        {"frame": "plastic-black", "wheel": "plastic-black", "hub": "plastic-black"}, [
            rod("arm", "frame", 0.024, [0.02, "top - 0.01", 0], ["R", "top - 0.03", 0], 6, at=[0, 0, 0], around={"n": "n", "r": 0}, r1=0.014),
            box("armTip", "frame", [0.05, 0.022, 0.03], ["R - 0.01", "top - 0.035", 0], around={"n": "n", "r": 0}),
            lathe("hub", "hub", [[0.03, "top - 0.06"], [0.05, "top - 0.045"], [0.05, "top"], [0.032, "top + 0.01"], [0, "top + 0.01"]], [0, 0, 0], sides=12),
            rod("stem", "frame", 0.006, ["R", "top - 0.045", 0], ["R", 0.05, 0], 6, around={"n": "n", "r": 0}),
            box("fork", "wheel", [0.04, 0.03, 0.036], ["R - 0.012", 0.045, 0], around={"n": "n", "r": 0}),
            lathe("castor", "wheel", [[0, -0.024], [0.022, -0.024], ["cr", -0.02], ["cr", -0.004], [0, -0.004]], [0, "cr", 0, 0, 90, 0], around={"n": "n", "r": "R - 0.018"}, sides=12),
            lathe("castorB", "wheel", [[0, 0.004], ["cr", 0.004], ["cr", 0.02], [0.022, 0.024], [0, 0.024]], [0, "cr", 0, 0, 90, 0], around={"n": "n", "r": "R - 0.018"}, sides=12),
        ], params={"R": 0.33, "n": 5, "top": 0.12, "cr": 0.025})


# ---- HELPERS ------------------------------------------------------------------------------------------------------
def splayed_legs(id_, mat, x, z, h, r0, r1, splay=0.0, sides=8):
    """four round legs from the underside's corners (±x, h, ±z) down to the floor, each splayed `splay` out
    diagonally; tapered r0 at the top to r1 at the foot -- the mid-century's table, sofa and chair legs"""
    return rod(id_, mat, r0, [0, h, 0], [splay, 0, splay], sides, r0=r0, r1=r1,
               at=[[x, 0, z, 0], [x, 0, -z, 90], [-x, 0, -z, 180], [-x, 0, z, 270]])


def door(id_, x, y, z, w, h, pull="hbar", hx=0.0, hy=0.0, hl=0.16, mats=None, swing=None, max_=105, drawer=None, frame=0, **k):
    """a slab door / drawer front (C slab-door) whose back stands at z, its middle at (x, y); `swing` "left" or
    "right": HINGED at that edge (items.js hinge, the item's `open`), opening out toward +z -- only where there is an
    inside to see (a mirror on it mirrors the hinge too); `drawer` (its depth): a DRAWER (components/drawer, its
    front this slab), the front on its tray (bottom, sides, back) SLIDING out toward +z by .8 of it -- placed by `at`,
    so `| {"at": [...]}` still makes a stack of them; `frame` (its stiles' width): a SHAKER front -- C slab-door's `frame`,
    the period components/panel-door standing as the slab does (anchor 0), its wood the slab's `front`, its sunk panel role
    `panel` (the front unless `mats` names it) -- on a door or a
    drawer alike (the pull on the frame's face)"""
    fr = {"frame": frame} if frame else {}
    if drawer:   # (C drawer: the slab front, its tray in a pale finish)
        return use(id_, "components/drawer", [x, y, z], {"front": "slab", "w": w, "h": h, "pull": pull, "hx": hx, "hy": hy, "hl": hl, **fr, "depth": drawer,
                   "back": 0, "floor": 0.012, "lift": 0.024, "gap": 0.03, "rise": min(h * 0.62, 0.2) / h}, {**(mats or {}), "tray": "#d9d5cc"}, **k)
    leaf = use(id_ if not swing else "slab", C + "slab-door", [x, y, z], {"w": w, "h": h, "pull": pull, "hx": hx, "hy": hy, "hl": hl, **fr}, mats, **({} if swing else k))
    if not swing: return leaf
    ex = x - w / 2 if swing == "left" else x + w / 2         # (+y turns +x toward -z: a left-hung leaf opens by a negative angle)
    return hinge(id_, [ex, y, z], [leaf], max_=-max_ if swing == "left" else max_, **k)


def seat_marker(w, d, top, xs=(0.0,), z=0.0):
    """a seat's markers: the seat itself { w, d, top } and one `spot` (pose sit, facing +z) per sitter at xs"""
    return [{"role": "seat", "at": [0, 0, 0], "data": {"w": w, "d": d, "top": top}},
            {"role": "spot", "at": [[x, top, z] for x in xs], "data": {"pose": "sit", "face": -HALF_PI}}]


def table_spots(xs_front, zf, xs_back, zb, ends=None):
    """the places round a table: chairs pulled up on the +z side (facing -z), the -z side (facing +z), and its ends"""
    m = [{"role": "spot", "at": [[x, 0.46, zf] for x in xs_front], "data": {"pose": "sit", "face": HALF_PI}},
         {"role": "spot", "at": [[x, 0.46, zb] for x in xs_back], "data": {"pose": "sit", "face": -HALF_PI}}]
    m = [q for q in m if q["at"]]   # (a side with no places gives none -- an empty list would place one at the origin)
    if ends: m += [{"role": "spot", "at": [ends, 0.46, 0], "data": {"pose": "sit", "face": math.pi}},
                   {"role": "spot", "at": [-ends, 0.46, 0], "data": {"pose": "sit", "face": 0}}]
    return m


COVERS = {"pick": ["upholstery-grey", "upholstery", "upholstery-red", "wool", "#7d8a6a", "#b7ab96"]}


# ---- SEATS --------------------------------------------------------------------------------------------------------
def upholstered(W, D, n, arm=0.2, armH=0.62, backTop=0.86, seatTop=0.5, legH=0.12):
    """the body of a modern sofa or armchair (W wide, D deep, n seat cushions): a sprung base, two square arms, a
    back frame, the seat cushions and the loose back cushions leaning against it, on four tapered wooden legs"""
    inner = W - 2 * arm
    cw = inner / n
    zb = -D / 2 + 0.17             # (the back frame's front face)
    cush_d = D / 2 - 0.02 - zb      # (the seat cushions from the back frame to just short of the front)
    parts = [
        box("base", "cover", [inner + 0.02, 0.26, D - 0.03], [0, legH + 0.13, -0.015]),
        box("arm", "cover", [arm, armH - legH, D], [W / 2 - arm / 2, legH + (armH - legH) / 2, 0], round=0.03, mirror="x"),
        box("backFrame", "cover", [inner + 0.01, backTop - legH - 0.06, 0.17], [0, legH + (backTop - legH - 0.06) / 2, -D / 2 + 0.085]),
        box("seatCushion", "cover", [cw - 0.012, seatTop - legH - 0.26 + 0.02, cush_d], [0, (seatTop + legH + 0.24) / 2, zb + cush_d / 2], round=0.03,
            along={"n": n, "from": [-inner / 2 + cw / 2, 0, 0], "to": [inner / 2 - cw / 2, 0, 0]}),
        box("backCushion", "cover", [cw - 0.016, backTop - seatTop + 0.08, 0.2], [0, (backTop + seatTop + 0.08) / 2 - 0.01, zb + 0.08, 0, -10, 0], round=0.035,
            along={"n": n, "from": [-inner / 2 + cw / 2, 0, 0], "to": [inner / 2 - cw / 2, 0, 0]}),
        splayed_legs("legs", "wood", W / 2 - 0.08, D / 2 - 0.08, legH + 0.01, 0.022, 0.014, 0.02),
    ]
    return parts


def sofa():
    # A THREE-SEAT SOFA of the late 20th century (2.1 m x 0.92 m; seat at 45 cm, arms 62 cm, back 86 cm): square
    # upholstered arms and back, three seat cushions, three loose back cushions, a scatter cushion, tapered legs
    W, D = 2.12, 0.92
    parts = upholstered(W, D, 3) + [
        box("scatter", "accent", [0.42, 0.4, 0.15], [-0.7, 0.69, -0.16, 22, -16, 6], round=0.04),
    ]
    return item("Sofa (modern)", "furniture/seat", "a three-seat sofa of the late 20th century, 2.12 m wide, 0.92 m deep: square upholstered arms and back, three seat cushions and three loose back cushions, a scatter cushion, four tapered wooden legs -- its back toward -z, the seat at 0.47 m",
        {"cover": COVERS, "accent": {"pick": ["velvet-green", "velvet-blue", "#c79a3e", "linen"]}, "wood": "oak"}, parts,
        markers=seat_marker(W - 0.4, D - 0.2, 0.47, xs=(-0.57, 0, 0.57), z=0.1), era="1950-2030")


def armchair():
    # AN ARMCHAIR to match (0.86 m square): one seat cushion and one back cushion between the arms
    W, D = 0.88, 0.88
    return item("Armchair (modern)", "furniture/seat", "an upholstered armchair of the late 20th century, 0.88 m square: square arms, one seat and one back cushion, tapered wooden legs -- its back toward -z, the seat at 0.47 m",
        {"cover": COVERS, "wood": "oak"}, upholstered(W, D, 1),
        markers=seat_marker(W - 0.4, D - 0.2, 0.47, z=0.1), era="1950-2030")


def office_chair():
    # AN OFFICE SWIVEL CHAIR (the 1990s' task chair): the five-star base on castors, the gas lift in its sleeve, the
    # tilt mechanism under a moulded seat with its cushion, a back on a curved spine with lumbar shape, T armrests.
    # Seat at 47 cm, the back's top 1.05 m.
    return item("Office chair", "furniture/seat", "an office swivel chair: a five-star base on twin-wheeled castors, the gas lift, the tilt mechanism under the moulded seat and its cushion, a padded back on a curved spine, two T-shaped armrests -- facing +z, the seat at 0.48 m",
        {"cover": {"pick": ["upholstery-grey", "upholstery", "#2b2c30", "upholstery-red"]}, "frame": "plastic-black", "chrome": "chrome"}, [
            use("base", C + "star-base", [0, 0, 0], {"R": 0.33, "n": 5, "top": 0.12}),
            rod("sleeve", "frame", 0.026, [0, 0.12, 0], [0, 0.3, 0], 12),
            rod("piston", "chrome", 0.014, [0, 0.29, 0], [0, 0.38, 0], 10),
            box("mechanism", "frame", [0.2, 0.05, 0.24], [0, 0.39, 0]),
            rod("lever", "frame", 0.006, [0.09, 0.39, 0.05], [0.2, 0.37, 0.09], 5),
            box("shell", "frame", [0.5, 0.03, 0.48], [0, 0.425, 0]),
            box("cushion", "cover", [0.5, 0.075, 0.47], [0, 0.465, 0.005], round=0.035),
            sweep("spine", "frame", [[0, 0.41, -0.08], [0, 0.42, -0.24], [0, 0.5, -0.31], [0, 0.66, -0.33]], None, section=[0.022, 0.07], up=[1, 0, 0]),
            box("backShell", "frame", [0.44, 0.52, 0.03], [0, 0.85, -0.315, 0, -8, 0]),
            box("back", "cover", [0.44, 0.52, 0.065], [0, 0.85, -0.272, 0, -8, 0], round=0.03),
            box("lumbar", "cover", [0.4, 0.14, 0.04], [0, 0.69, -0.24, 0, -8, 0], round=0.02),
            sweep("armPost", "frame", [[0.18, 0.41, -0.02], [0.25, 0.43, -0.02], [0.27, 0.5, -0.02], [0.27, 0.64, -0.02]], None, section=[0.022, 0.05], up=[0, 0, 1], mirror="x"),
            box("armPad", "frame", [0.075, 0.03, 0.26], [0.27, 0.655, 0.0], mirror="x"),
        ], markers=seat_marker(0.5, 0.47, 0.48), era="1975-2030")


def dining_chair():
    # A DINING CHAIR of the Danish modern kind (1950s on): a padded seat on a solid frame, four round tapered legs,
    # the back legs rising into posts that carry a curved back rail; side stretchers. Seat at 45 cm, 0.46 x 0.47 m.
    h = 0.45
    return item("Dining chair (modern)", "furniture/seat", "a Danish-modern dining chair: a padded seat on a solid frame, four tapered round legs, the back legs rising into posts that carry a curved back rail, side stretchers -- its back toward -z, the seat at 0.45 m",
        {"wood": {"pick": ["oak", "walnut", "ash"]}, "cover": {"pick": ["leather-dark", "upholstery-grey", "wool", "leather"]}}, [
            box("frame", "wood", [0.44, 0.04, 0.42], [0, h - 0.055, 0]),
            box("pad", "cover", [0.43, 0.045, 0.42], [0, h - 0.015, 0.005], round=0.02),
            rod("front", "wood", 0.018, [0.19, h - 0.05, 0.18], [0.205, 0, 0.205], 8, r1=0.012, mirror="x"),
            rod("back", "wood", 0.018, [0.19, h - 0.05, -0.18], [0.2, 0, -0.225], 8, r1=0.013, mirror="x"),
            rod("post", "wood", 0.018, [0.19, h - 0.06, -0.18], [0.2, 0.79, -0.235], 8, r1=0.015, mirror="x"),
            sweep("rail", "wood", [[-0.215, 0.735, -0.225], [-0.12, 0.735, -0.262], [0, 0.735, -0.272], [0.12, 0.735, -0.262], [0.215, 0.735, -0.225]], None,
                  section=[0.02, 0.09], up=[0, 1, 0]),
            rod("stretcher", "wood", 0.01, [0.198, 0.16, 0.185], [0.198, 0.16, -0.19], 6, mirror="x"),
        ], markers=seat_marker(0.44, 0.42, h), era="1945-2030")


def bar_stool():
    # A BAR STOOL (counter height, seat at 76 cm): a round padded seat on a chrome column with a gas lift, a domed
    # chrome base, a footring held by three spokes
    return item("Bar stool", "furniture/seat", "a counter bar stool: a round padded seat at 0.76 m on a chrome column with a gas lift, a heavy domed chrome base, a chrome footring on three spokes at 0.3 m",
        {"cover": {"pick": ["leather-dark", "leather-red", "plastic-white", "leather"]}, "chrome": "chrome", "frame": "plastic-black"}, [
            lathe("base", "chrome", [[0, 0], [0.21, 0], [0.215, 0.006], [0.2, 0.018], [0.08, 0.04], [0.035, 0.05], [0, 0.05]], [0, 0, 0], sides=24),
            rod("column", "chrome", 0.03, [0, 0.05, 0], [0, 0.6, 0], 14),
            rod("lift", "frame", 0.034, [0, 0.6, 0], [0, 0.66, 0], 14),
            lathe("pan", "frame", [[0.03, 0.66], [0.12, 0.69], [0.17, 0.70], [0, 0.70]], [0, 0, 0], sides=18),
            lathe("seat", "cover", [[0, 0.695], [0.18, 0.695], [0.192, 0.71], [0.19, 0.745], [0.165, 0.762], [0, 0.765]], [0, 0, 0], sides=24),
            ring("footring", "chrome", 0.2, 0.011, [0, 0.3, 0]),
            rod("spoke", "chrome", 0.008, [0.03, 0.3, 0], [0.2, 0.3, 0], 6, around={"n": 3, "r": 0}),
            lathe("collar", "chrome", [[0.03, 0.29], [0.045, 0.29], [0.045, 0.315], [0.03, 0.315]], [0, 0, 0], sides=12),
        ], markers=seat_marker(0.38, 0.38, 0.765), era="1950-2030")


# ---- TABLES -------------------------------------------------------------------------------------------------------
def dining_table():
    # A DINING TABLE for six (1.8 x 0.9 m, 75 cm): a solid top, a shallow apron, four square legs set in at the corners
    L, D, h = 1.8, 0.9, 0.75
    return item("Dining table (modern)", "furniture/table", "a modern dining table for six, 1.8 x 0.9 m and 0.75 m high: a solid 40 mm top, a shallow apron, four square legs set in from the corners",
        {"wood": {"pick": ["oak", "walnut", "ash"]}}, [
            box("top", "wood", [L, 0.04, D], [0, h - 0.02, 0]),
            box("apron", "wood", [L - 0.24, 0.08, D - 0.2], [0, h - 0.08, 0]),
            box("leg", "wood", [0.06, h - 0.04, 0.06], [[L / 2 - 0.12, (h - 0.04) / 2, D / 2 - 0.1], [L / 2 - 0.12, (h - 0.04) / 2, -D / 2 + 0.1]], mirror="x"),
        ], markers=table_spots([-0.55, 0, 0.55], D / 2 + 0.25, [-0.55, 0, 0.55], -D / 2 - 0.25), era="1950-2030")


def coffee_table():
    # A COFFEE TABLE (1.1 x 0.55 m, 42 cm high): a walnut top on four splayed tapered legs, a lower shelf for magazines
    return item("Coffee table", "furniture/table", "a mid-century coffee table, 1.1 x 0.55 m and 0.42 m high: a top on four splayed, tapered round legs, a lower shelf between them",
        {"wood": {"pick": ["walnut", "oak", "ash"]}, "shelf": {"pick": ["walnut", "oak", "#2b2b2e"]}}, [
            box("top", "wood", [1.1, 0.035, 0.55], [0, 0.4025, 0]),
            box("rail", "wood", [0.95, 0.05, 0.42], [0, 0.36, 0]),
            splayed_legs("legs", "wood", 0.44, 0.17, 0.36, 0.022, 0.014, 0.035),
            box("shelf", "shelf", [0.9, 0.018, 0.38], [0, 0.13, 0]),
        ], era="1950-2030")


def desk():
    # A WRITING / COMPUTER DESK (1.4 x 0.7 m, 75 cm): a laminate top on two steel C-frames joined by a rail, a modesty
    # panel at the back, a three-drawer pedestal under the right end, a cable grommet
    L, D, h = 1.4, 0.7, 0.75
    fx = L / 2 - 0.04
    return item("Desk (modern)", "furniture/table", "an office desk, 1.4 x 0.7 m and 0.75 m high: a laminate top on two square steel frames with feet, a modesty panel, a three-drawer pedestal under its right end, a cable grommet -- its user sits on the +z side",
        {"top": {"pick": ["plastic-white", "oak", "#d8d2c4", "plastic-grey"]}, "steel": {"pick": ["paint-black", "aluminium", "paint-white"]},
         "front": "plastic-white", "metal": "aluminium", "grommet": "plastic-black"}, [
            box("top", "top", [L, 0.025, D], [0, h - 0.0125, 0]),
            box("legs", "steel", [0.04, h - 0.025, 0.04], [[fx, (h - 0.025) / 2, D / 2 - 0.06], [fx, (h - 0.025) / 2, -D / 2 + 0.06]], mirror="x"),
            box("foot", "steel", [0.05, 0.025, D - 0.06], [fx, 0.0125, 0], mirror="x"),
            box("bearer", "steel", [0.04, 0.04, D - 0.1], [fx, h - 0.045, 0], mirror="x"),
            box("rail", "steel", [L - 0.12, 0.05, 0.03], [0, h - 0.05, -D / 2 + 0.07]),
            box("modesty", "top", [L - 0.16, 0.34, 0.012], [0, h - 0.24, -D / 2 + 0.09]),
            box("pedestal", "front", [0.4, 0.6, 0.56], [0.42, 0.33, -0.05]),
            door("drawers", 0.42, 0.53, 0.23, 0.39, 0.145, "hbar", hl=0.13, drawer=0.42) | {"at": [[0.42, 0.535, 0.23], [0.42, 0.385, 0.23], [0.42, 0.175, 0.23]]},
            ring("grommet", "grommet", 0.03, 0.006, [-0.5, h + 0.002, -D / 2 + 0.08]),
        ], params={"open": 0}, markers=table_spots([-0.1], D / 2 + 0.3, [], 0), era="1960-2030")


# ---- BEDS ---------------------------------------------------------------------------------------------------------
def bed():
    # A DOUBLE BED (a 160 x 200 cm mattress): an upholstered frame on short legs, a tall padded headboard, a deep
    # mattress, two pillows, a duvet hanging over the sides and turned down at the head. It lies along x, head at -x.
    l, w = 2.0, 1.6
    return item("Bed (modern)", "furniture/bed", "a modern double bed for a 160 x 200 cm mattress: an upholstered frame on short legs, a tall padded headboard, a 22 cm mattress, two pillows, a duvet over the sides and turned down at the head -- along x, its head at -x",
        {"frame": COVERS, "wood": "oak", "sheet": "linen", "duvet": {"pick": ["linen", "#c9d4de", "#e9e3d6", "damask-blue", "#b9a48a"]}, "pillow": "linen"}, [
            box("frame", "frame", [l + 0.1, 0.27, w + 0.1], [0, 0.235, 0]),
            splayed_legs("legs", "wood", l / 2 - 0.05, w / 2 - 0.05, 0.11, 0.022, 0.018),
            box("headboard", "frame", [0.1, 1.05, w + 0.14], [-l / 2 - 0.1, 0.62, 0]),
            box("headPad", "frame", [0.08, 0.62, (w + 0.08) / 3 - 0.01], [-l / 2 - 0.03, 0.86, 0], round=0.025,
                along={"n": 3, "from": [0, 0, -(w + 0.08) / 3], "to": [0, 0, (w + 0.08) / 3]}),
            box("mattress", "sheet", [l, 0.22, w], [0, 0.45, 0], round=0.04),
            box("pillow", "pillow", [0.42, 0.13, 0.68], [-l / 2 + 0.25, 0.62, 0.38, 0, 0, -12], round=0.06, mirror="z"),
            # (the duvet a loft along the bed: its sides and foot hang over the mattress, its top edges soft)
            loft("duvet", "duvet", [[-l / 2 + 0.48, w / 2 + 0.05, 0.33, 0.6], [0.0, w / 2 + 0.06, 0.32, 0.61], [l / 2 - 0.1, w / 2 + 0.06, 0.32, 0.6], [l / 2 + 0.04, w / 2 + 0.05, 0.32, 0.6]], [0.0, 0.07], seg=2),
            loft("turnDown", "duvet", [[-l / 2 + 0.44, w / 2 + 0.035, 0.57, 0.645], [-l / 2 + 0.7, w / 2 + 0.035, 0.57, 0.64]], [0.0, 0.035], seg=1),
        ], markers=[{"role": "bed", "at": [0, 0, 0, 90], "data": {"top": 0.6, "foot": l / 2 + 0.35}}], era="1950-2030")


# ---- STORAGE ------------------------------------------------------------------------------------------------------
def wardrobe():
    # A TWO-DOOR WARDROBE (1.0 x 0.6 x 2.0 m): a carcass of boards on a recessed plinth -- hollow: the hat shelf, the
    # hanging rail and the clothes on it, a shoe board -- behind two full-height slab doors HINGED at the outer edges
    # (open: they swing out), long upright bar handles by their meeting edges
    W, D, H, t = 1.0, 0.6, 2.0, 0.018
    dw, dh = W / 2 - 0.004, H - 0.1
    zb, zf = -D / 2, D / 2 - 0.02                        # (the carcass's back, its front edge)
    rng = random.Random(1972)
    clothes = []
    for i, x in enumerate([-0.38, -0.27, -0.17, -0.06, 0.06, 0.18, 0.3, 0.39]):
        L = rng.choice([0.62, 0.7, 0.95, 1.1, 1.2])
        clothes.append(box(f"garment{i}", f"cloth{i % 4}", [0.06 + rng.random() * 0.03, L, 0.46], [x, 1.6 - L / 2, -0.02]))
    return item("Wardrobe (modern)", "furniture/storage", "a modern two-door wardrobe, 1.0 m wide, 0.6 m deep, 2.0 m high: a carcass of boards on a recessed plinth, inside the hat shelf, the hanging rail with clothes on hangers, a shoe board; two full-height slab doors hinged at the outer edges (open: swung out), long upright bar handles by their meeting edges",
        {"carcass": {"pick": ["plastic-white", "oak", "#d8d2c4", "walnut"]}, "front": {"pick": ["plastic-white", "oak", "#4b5059", "#c9c1b0"]}, "metal": "aluminium", "plinth": "#2a2a2c",
         "cloth0": {"pick": ["#2f3a52", "#5a5f66", "#7a2b2b"]}, "cloth1": {"pick": ["#d9d4c8", "#8a7a5c", "#3d4a3a"]}, "cloth2": {"pick": ["#1f1f22", "#6b4a8a", "#c27a4a"]}, "cloth3": {"pick": ["#9aa8b8", "#40506a", "#b8b0a0"]}}, [
            box("side", "carcass", [t, H - 0.08, D - 0.02], [W / 2 - t / 2, 0.08 + (H - 0.08) / 2, -0.01], mirror="x"),
            box("top", "carcass", [W - 2 * t, t, D - 0.02], [0, H - t / 2, -0.01]),
            box("bottom", "carcass", [W - 2 * t, t, D - 0.02], [0, 0.08 + t / 2, -0.01]),
            box("back", "carcass", [W - 2 * t, H - 0.08 - 2 * t, 0.006], [0, 0.08 + (H - 0.08) / 2, zb + 0.003]),
            box("hatShelf", "carcass", [W - 2 * t, t, D - 0.06], [0, 1.72, -0.03]),
            rod("rail", "metal", 0.012, [-W / 2 + t, 1.64, -0.02], [W / 2 - t, 1.64, -0.02], 10),
            *clothes,
            rod("hook", "metal", 0.004, [0, 1.6, -0.02], [0, 1.66, -0.02], 6, at=[[x, 0, 0] for x in [-0.38, -0.27, -0.17, -0.06, 0.06, 0.18, 0.3, 0.39]]),
            box("shoeBoard", "carcass", [W - 2 * t, t, D - 0.12], [0, 0.3, -0.05]),
            box("plinth", "plinth", [W - 0.04, 0.08, D - 0.08], [0, 0.04, -0.03]),
            door("door", -W / 4, 0.08 + 0.005 + dh / 2, zf, dw, dh, "vbar", hx=dw / 2 - 0.05, hy=0.0, hl=0.6, swing="left", mirror="x"),
        ], params={"open": 0}, era="1950-2030")


def bookshelf():
    # A BOOKSHELF (the flat-pack kind, 0.8 x 0.28 x 2.02 m): two sides, a top, a plinth, five adjustable shelves, a
    # back -- and its books: each shelf a packed run of spines of different widths, heights and depths, a gap where one
    # leans, a short stack lying flat. The runs are `each` parts drawn by items.js `rnd` (2026-11-22; until then 121
    # boxes drawn here by random.Random(1966)), so every bookshelf's books are its own.
    W, D, H = 0.8, 0.28, 2.02
    t = 0.018
    rows = [0.08, 0.4, 0.74, 1.08, 1.42, 1.72]   # (the boards' tops: the bottom board on the plinth, then the shelves)
    rng = random.Random(1966)
    parts = [
        box("side", "board", [t, H, D], [W / 2 - t / 2, H / 2, 0], mirror="x"),
        box("top", "board", [W, t, D], [0, H - t / 2, 0]),
        box("plinth", "board", [W - 2 * t, 0.07, t], [0, 0.035, D / 2 - 0.03]),
        box("shelf", "board", [W - 2 * t, t, D - 0.02], [[0, y - t / 2, 0.005] for y in rows]),
        box("backPanel", "back", [W - 0.004, H - 0.01, 0.004], [0, H / 2, -D / 2 + 0.002]),
    ]
    S, J = 0.0325, 0.02   # (a book's slot, and how far each edge between two books wanders: widths 12.5..52.5 mm)
    seg, k = 0, 0         # (the run's own number, keying its draws; the colour count, cycling a b c d along the shelf)

    def run(x0, x1, y, head, hr):
        """a packed run of books from x0 to x1 on the board at y: m books, the edge before book j at
        E(j) = x0 + S'j + J (rnd(seg, j) - 0.5), the run's two ends held still -- so book j, from E(j) to E(j + 1), is
        as wide as its draws make it and the books touch without a gap or an overlap. One `each` part a colour."""
        nonlocal seg, k
        m = max(1, round((x1 - x0) / S)); s = (x1 - x0) / m; seg += 1
        lo, hi = hr
        g = lambda v: f"{v:.6g}"
        for c in range(4):
            jc = (c - k) % 4
            n = len(range(jc, m, 4))
            if not n: continue
            j = f"(4 * i + {jc})" if jc else "4 * i"
            jj = f"(4 * i + {jc + 1})"
            # (each edge's wander, (rnd - 0.5); the run's first edge and its last held still by a min(.., 1) that is 0 there)
            el = f"(rnd({seg}, {j}) - 0.5)" + ("" if jc else f" * min({j}, 1)")
            er = f"(rnd({seg}, {jj}) - 0.5)" + (f" * min({m - 1 - jc} - 4 * i, 1)" if (m - 1 - jc) % 4 == 0 else "")
            hd = f"{g(hi - lo)} * rnd({seg}, {j}, 1)"
            parts.append({"id": f"books{seg}{'abcd'[c]}", "each": n, "type": "box", "material": "abcd"[c],
                          "size": [f"{g(s - 0.002)} + {J} * ({er} - {el})", f"min({g(head)}, {lo} + {hd})" if hi > head else f"{lo} + {hd}", f"0.15 + 0.06 * rnd({seg}, {j}, 2)"],
                          "at": [f"{g(x0 + s / 2)} + {g(s)} * {j} + {J / 2} * ({el} + {er})",
                                 f"{g(y)} + min({g(head)}, {lo} + {hd}) / 2" if hi > head else f"{g(y + lo / 2)} + {g((hi - lo) / 2)} * rnd({seg}, {j}, 1)",
                                 f"0.045 - 0.03 * rnd({seg}, {j}, 2)"]})
        k += m

    x0, x1 = -W / 2 + t + 0.01, W / 2 - t - 0.01
    for si, y in enumerate(rows):
        head = (rows[si + 1] if si + 1 < len(rows) else H - t) - y - 0.03
        hr = (0.19, 0.27) if si else (0.26, 0.32)
        if si in (1, 3):   # (a gap after the first or third book, and a book leaning into it)
            n0 = rng.choice([1, 3]); xa = x0 + n0 * S
            run(x0, xa, y, head, hr)
            bw, bh, bd = rng.uniform(0.02, 0.045), min(head, rng.uniform(*hr)), rng.uniform(0.15, 0.21)
            parts.append(box(f"lean{si}", "abcd"[k % 4], [bw, bh, bd], [xa + bw / 2 + bh * 0.33, y + bh / 2 * 0.94, 0.12 - bd / 2, 0, 0, -20]))
            k += 1
            run(xa + 0.11 + bw, x1, y, head, hr)
        elif si == 2:      # (four books, then a short stack lying flat)
            xa = x0 + 4 * S
            run(x0, xa, y, head, hr)
            for j in range(3):
                bh = rng.uniform(0.025, 0.04)
                parts.append(box(f"flat{j}", "abcd"[k % 4], [0.22, bh - 0.002, 0.16], [xa + 0.11, y + 0.002 + j * 0.04 + bh / 2, 0.02]))
                k += 1
            run(xa + 0.25, x1, y, head, hr)
        else:
            run(x0, x1, y, head, hr)
    return item("Bookshelf", "furniture/storage", "a flat-pack bookshelf, 0.8 m wide, 0.28 m deep, 2.02 m high: two sides, a top, a plinth, five shelves, a hardboard back, and its books in runs of different heights and colours, a few leaning, a short stack lying flat",
        {"board": {"pick": ["plastic-white", "birch", "oak", "#2a2a2c"]}, "back": "#cfcbc2",
         "a": {"pick": ["#8a2f2a", "#2f4a6b", "#d9c9a3"]}, "b": {"pick": ["#33553d", "#e2ddd0", "#203040"]},
         "c": {"pick": ["#b48a3a", "#5a2c46", "#1f1f22"]}, "d": {"pick": ["#c45a2e", "#6e7b85", "#efe9dc"]}}, parts, era="1950-2030")


def tv_stand():
    # A TV STAND / MEDIA UNIT (1.6 x 0.42 x 0.5 m): a low carcass on tapered legs, a flap door at each end, an open
    # middle bay with a shelf for the boxes under the set
    W, D, y0, y1 = 1.6, 0.42, 0.12, 0.5
    t = 0.02
    bay = 0.6
    side = (W - bay - 4 * t) / 2
    xm = bay / 2 + t / 2
    return item("TV stand", "furniture/storage", "a low media unit, 1.6 m wide, 0.42 m deep, 0.5 m high: a carcass on four tapered legs, a push-to-open flap door at each end, an open middle bay with a shelf",
        {"carcass": {"pick": ["walnut", "oak", "plastic-white", "#2a2a2c"]}, "front": {"pick": ["walnut", "oak", "plastic-white", "#4b5059"]}, "wood": "oak", "back": "#2a2a2c", "metal": "aluminium"}, [
            box("top", "carcass", [W, t, D], [0, y1 - t / 2, 0]),
            box("bottom", "carcass", [W, t, D], [0, y0 + t / 2, 0]),
            box("side", "carcass", [t, y1 - y0, D], [W / 2 - t / 2, (y0 + y1) / 2, 0], mirror="x"),
            box("divider", "carcass", [t, y1 - y0 - 2 * t, D - 0.02], [xm, (y0 + y1) / 2, -0.01], mirror="x"),
            box("shelf", "carcass", [bay, t * 0.8, D - 0.04], [0, (y0 + y1) / 2, -0.02]),
            box("back", "back", [W - 2 * t, y1 - y0 - 2 * t, 0.005], [0, (y0 + y1) / 2, -D / 2 + 0.003]),
            door("flap", -(xm + t / 2 + side / 2), (y0 + y1) / 2, D / 2 - 0.018, side - 0.004, y1 - y0 - 2 * t - 0.004, "lip", mirror="x"),
            splayed_legs("legs", "wood", W / 2 - 0.08, D / 2 - 0.06, y0, 0.018, 0.012, 0.015),
        ], era="1960-2030")


# ---- THE KITCHEN --------------------------------------------------------------------------------------------------
def kitchen():
    # A FITTED KITCHEN RUN (3.0 m: five 600 mm base units, the European standard): base carcasses on a recessed plinth
    # (worktop at 0.9 m), a three-drawer unit, the sink unit (two doors) under an inset steel sink with its drainer and
    # a swan-neck tap, an integrated dishwasher, a pan-drawer unit under a ceramic hob, a door unit; a tiled upstand;
    # wall units (0.72 m, 0.33 deep) from 1.45 m, a chimney hood over the hob. Its back against a wall at z -0.3.
    # THE FRONTS (2026-11-22): the seed picks flat slabs or shaker fronts (`frame` 0.06, the 17 cm drawer's .04: C slab-door's
    # frame, its sunk panel role `panel`), and a colourway pairing each front colour with a panel a shade darker.
    L, zB = 3.0, -0.3
    pl, top, wt = 0.14, 0.86, 0.04              # (plinth, the carcasses' top, the worktop's thickness)
    zF = 0.26                                   # (the base carcasses' front: the doors hang on it)
    U = [-1.2, -0.6, 0.0, 0.6, 1.2]             # (the units' middles)
    fh = top - pl - 0.006                       # (a full-height base front)
    wy0, wy1, wd = 1.45, 2.17, 0.33
    sx, sw, sd = -0.6, 0.46, 0.36               # (the sink's bowl opening: middle x, width, depth)
    sz0, sz1 = -0.2, -0.2 + sd
    hob = 0.6
    wtz = (zB + 0.33) / 2
    parts = [
        box("plinth", "plinth", [L, pl, 0.5], [0, pl / 2, zB + 0.25 - 0.02]),
        box("carcass", "carcass", [L, top - pl, zF - zB], [0, (pl + top) / 2, (zF + zB) / 2]),
        # (the worktop in four pieces round the sink's opening)
        box("worktopL", "worktop", [sx - sw / 2 + L / 2, wt, 0.63], [(-L / 2 + sx - sw / 2) / 2, top + wt / 2, wtz]),
        box("worktopR", "worktop", [L / 2 - sx - sw / 2, wt, 0.63], [(L / 2 + sx + sw / 2) / 2, top + wt / 2, wtz]),
        box("worktopB", "worktop", [sw, wt, sz0 - zB], [sx, top + wt / 2, (zB + sz0) / 2]),
        box("worktopF", "worktop", [sw, wt, 0.33 - sz1], [sx, top + wt / 2, (0.33 + sz1) / 2]),
        box("upstand", "tile", [L, 0.55, 0.01], [0, top + wt + 0.275, zB + 0.005]),
        # (the base fronts: drawers, the sink's doors, the dishwasher, the pan drawers, a door)
        door("drawer1", U[0], 0.772, zF, 0.592, 0.17, "hbar", hl=0.32, drawer=0.48, frame="frame * 2 / 3"),
        door("drawer2", U[0], 0.546, zF, 0.592, 0.266, "hbar", hy=0.08, hl=0.32, drawer=0.48, frame="frame") | {"at": [[U[0], 0.546, zF], [U[0], 0.276, zF]]},
        door("sinkDoor", U[1] - 0.15, pl + 0.003 + fh / 2, zF, 0.293, fh, "vbar", hx=0.11, hy=fh / 2 - 0.12, hl=0.16, frame="frame"),
        door("sinkDoorR", U[1] + 0.15, pl + 0.003 + fh / 2, zF, 0.293, fh, "vbar", hx=-0.11, hy=fh / 2 - 0.12, hl=0.16, frame="frame"),
        door("dishwasher", U[2], pl + 0.003 + fh / 2, zF, 0.592, fh, "hbar", hy=fh / 2 - 0.05, hl=0.4, frame="frame"),
        door("pan", U[3], 0.313, zF, 0.592, 0.34, "hbar", hy=0.11, hl=0.32, drawer=0.48, frame="frame"),
        door("pan2", U[3], 0.672, zF, 0.592, 0.37, "hbar", hy=0.125, hl=0.32, drawer=0.48, frame="frame"),
        door("door5", U[4], pl + 0.003 + fh / 2, zF, 0.592, fh, "vbar", hx=-0.25, hy=fh / 2 - 0.12, hl=0.16, frame="frame"),
        # (the sink: its bowl, rim and drainer, the tap)
        box("bowlFloor", "steel", [sw - 0.02, 0.006, sd - 0.02], [sx, top + wt - 0.19, (sz0 + sz1) / 2]),
        box("bowlSide", "steel", [0.006, 0.19, sd - 0.02], [[sx - sw / 2 + 0.013, top + wt - 0.095, (sz0 + sz1) / 2], [sx + sw / 2 - 0.013, top + wt - 0.095, (sz0 + sz1) / 2]]),
        box("bowlEnd", "steel", [sw - 0.02, 0.19, 0.006], [[sx, top + wt - 0.095, sz0 + 0.013], [sx, top + wt - 0.095, sz1 - 0.013]]),
        ring("waste", "chrome", 0.03, 0.006, [sx, top + wt - 0.185, (sz0 + sz1) / 2]),
        box("rimB", "steel", [sw + 0.04, 0.004, 0.03], [[sx, top + wt + 0.002, sz0 - 0.005], [sx, top + wt + 0.002, sz1 + 0.005]]),
        box("rimS", "steel", [0.03, 0.004, sd + 0.04], [[sx - sw / 2 - 0.005, top + wt + 0.002, (sz0 + sz1) / 2], [sx + sw / 2 + 0.005, top + wt + 0.002, (sz0 + sz1) / 2]]),
        box("drainer", "steel", [0.4, 0.004, sd + 0.04], [sx + sw / 2 + 0.22, top + wt + 0.002, (sz0 + sz1) / 2]),
        box("groove", "groove", [0.32, 0.002, 0.008], [sx + sw / 2 + 0.22, top + wt + 0.0045, 0], along={"n": 7, "from": [0, 0, sz0 + 0.04], "to": [0, 0, sz1 - 0.04]}),
        lathe("tapBase", "chrome", [[0, 0], [0.026, 0], [0.024, 0.04], [0.019, 0.06], [0, 0.06]], [sx, top + wt, sz0 - 0.045], sides=12),
        sweep("spout", "chrome", [[sx, top + wt + 0.05, sz0 - 0.045], [sx, top + wt + 0.28, sz0 - 0.04], [sx, top + wt + 0.33, sz0 + 0.03], [sx, top + wt + 0.28, sz0 + 0.12], [sx, top + wt + 0.24, sz0 + 0.13]], 0.012),
        rod("tapLever", "chrome", 0.006, [sx + 0.02, top + wt + 0.05, sz0 - 0.045], [sx + 0.09, top + wt + 0.07, sz0 - 0.045], 6),
        # (the ceramic hob: black glass, four rings, its touch controls)
        box("hob", "hobGlass", [0.58, 0.006, 0.51], [hob, top + wt + 0.003, 0.0]),
        ring("zone", "zone", 0.09, 0.0025, [[hob - 0.14, top + wt + 0.006, -0.12], [hob + 0.14, top + wt + 0.006, -0.12]]),
        ring("zoneS", "zone", 0.07, 0.0025, [[hob - 0.14, top + wt + 0.006, 0.1], [hob + 0.14, top + wt + 0.006, 0.1]]),
        box("touch", "zone", [0.2, 0.002, 0.03], [hob, top + wt + 0.0065, 0.22]),
        # (the wall units, the hood)
        box("wallCarcass", "carcass", [L / 2 + hob - 0.3, wy1 - wy0, wd], [(-L / 2 + hob - 0.3) / 2, (wy0 + wy1) / 2, zB + wd / 2]),
        box("wallCarcassR", "carcass", [L / 2 - hob - 0.3, wy1 - wy0, wd], [(L / 2 + hob + 0.3) / 2, (wy0 + wy1) / 2, zB + wd / 2]),
        door("wallDoor", U[0], (wy0 + wy1) / 2, zB + wd, 0.592, wy1 - wy0 - 0.004, "hbar", hy=-(wy1 - wy0) / 2 + 0.05, hl=0.2, frame="frame") | {"at": [[U[0], (wy0 + wy1) / 2, zB + wd], [U[1], (wy0 + wy1) / 2, zB + wd], [U[2], (wy0 + wy1) / 2, zB + wd], [U[4], (wy0 + wy1) / 2, zB + wd]]},
        box("hoodCanopy", "steel", [0.6, 0.07, 0.5], [hob, 1.605, zB + 0.25]),
        box("chimney", "steel", [0.28, 0.76, 0.26], [hob, 2.02, zB + 0.13]),
        box("hoodFilter", "groove", [0.56, 0.004, 0.44], [hob, 1.568, zB + 0.25]),
    ]
    d = item("Fitted kitchen", "furniture/kitchen", "a fitted kitchen run, 3.0 m: five 600 mm base units on a recessed plinth under a 40 mm worktop at 0.9 m (a drawer unit, a sink unit with an inset steel sink, drainer and swan-neck tap, an integrated dishwasher, pan drawers under a ceramic hob, a door unit), a tiled upstand, four wall units from 1.45 m and a chimney hood -- its back against a wall at -z; the seed picks flat slab fronts or shaker ones (`frame` 0.06: stiles and rails round a sunk panel a shade darker), and a colourway (front and panel)",
        {"carcass": "#c4c1ba", "front": "plastic-white", "panel": "#d0d0ca", "metal": "aluminium",
         "worktop": {"pick": ["oak", "granite-black", "marble", "#d8d2c4"]}, "plinth": "#2a2a2c", "tile": "#e8e4dc", "steel": "steel", "chrome": "chrome",
         "groove": "#8d9298", "hobGlass": "#131416", "zone": "#5c5f66"}, parts,
        markers=[{"role": "spot", "at": [[sx, 0, 0.65], [hob, 0, 0.65]], "data": {"pose": "stand", "face": HALF_PI, "work": 1}}], params={"open": 0, "frame": {"pick": [0, 0.06]}, "colourway": {"pick": ["white", "slate", "cream", "sage", "oak", "red"]}}, era="1950-2030")
    # (the fronts' colourways: each front with the panel a shaker front sinks in it, a shade darker -- unused when flat)
    # (the `colourway` param picks one -- the second draw of the seed's stream, so seeds 1-40 spread over the six about
    #  evenly; left to items.js's own pick after the roles, the third draw, seeds 1-40 gave 13 white to 3 slate)
    d["colourways"] = {"white": {"front": "plastic-white", "panel": "#d0d0ca"}, "slate": {"front": "#3f4a57", "panel": "#333c47"},
                       "cream": {"front": "#c9c1b0", "panel": "#b5ad9b"}, "sage": {"front": "#556b5a", "panel": "#47594b"},
                       "oak": {"front": "oak", "panel": "walnut"}, "red": {"front": "#8c2f2f", "panel": "#782828"}}
    return d


# ---- LAMPS --------------------------------------------------------------------------------------------------------
def floor_lamp():
    # A FLOOR LAMP (1.6 m): a weighted disc base, a slender stem with an inline switch, a drum shade of linen round
    # the bulb on its harp
    return item("Floor lamp", "furniture/lamp", "a standard floor lamp, 1.6 m: a heavy disc base, a slender metal stem, a linen drum shade 44 cm across over the bulb and its holder, the flex with its foot switch",
        {"metal": {"pick": ["paint-black", "brass", "chrome", "aluminium"]}, "shade": {"pick": ["linen", "#e8dfc9", "#2f3236", "canvas"]}, "bulb": "lamp", "flex": "plastic-black"}, [
            lathe("base", "metal", [[0, 0], [0.15, 0], [0.155, 0.01], [0.14, 0.03], [0.02, 0.04], [0, 0.04]], [0, 0, 0], sides=24),
            rod("stem", "metal", 0.011, [0, 0.03, 0], [0, 1.4, 0], 10),
            lathe("holder", "metal", [[0, 1.38], [0.022, 1.38], [0.022, 1.44], [0, 1.44]], [0, 0, 0], sides=10),
            sphere("bulb", "bulb", 0.032, [0, 1.47, 0], sides=12),
            lathe("shade", "shade", [[0.22, 1.33], [0.215, 1.6]], [0, 0, 0], caps=False, double=True, sides=28),
            rod("spider", "metal", 0.003, [0, 1.6, 0], [0.214, 1.6, 0], 4, around={"n": 3, "r": 0}),
            sweep("flex", "flex", [[0.01, 0.03, -0.12], [0.02, 0.006, -0.3], [0.1, 0.005, -0.55]], 0.0035),
            box("switch", "flex", [0.07, 0.02, 0.04], [0.1, 0.01, -0.55]),
        ], era="1920-2030")


def desk_lamp():
    # A BALANCED-ARM DESK LAMP (the Anglepoise of 1932, ~0.5 m reach): a weighted round base, a lower and an upper arm
    # of twin rods with their springs, a conical shade facing +z and down, the bulb inside it
    P0, P1, P2 = [0, 0.065, 0], [0, 0.36, 0.1], [0, 0.42, 0.4]
    tilt = -28
    return item("Desk lamp", "furniture/lamp", "a balanced-arm desk lamp (the Anglepoise kind): a weighted base, lower and upper arms of twin rods with the springs that balance them, a conical shade turned forward (+z) and down over the bulb",
        {"metal": {"pick": ["paint-black", "paint-red", "paint-cream", "paint-blue", "aluminium"]}, "steel": "steel", "bulb": "lamp"}, [
            lathe("base", "metal", [[0, 0], [0.085, 0], [0.085, 0.022], [0.06, 0.04], [0.02, 0.045], [0, 0.045]], [0, 0, 0], sides=20),
            lathe("turret", "metal", [[0.022, 0.04], [0.02, 0.07], [0, 0.07]], [0, 0, 0], sides=10),
            rod("lower", "metal", 0.006, [0.014, P0[1], P0[2]], [0.014, P1[1], P1[2]], 6, mirror="x"),
            rod("upper", "metal", 0.006, [0.014, P1[1], P1[2] - 0.05 * 0.3], [0.014, P2[1], P2[2]], 6, mirror="x"),
            rod("spring", "steel", 0.008, [0.03, 0.08, -0.01], [0.03, 0.27, 0.06], 8, mirror="x"),
            sphere("knuckle", "metal", 0.016, [[0, P1[1], P1[2]], [0, P2[1], P2[2]]], sides=8),
            lathe("shade", "metal", [[0.0, 0.0], [0.03, 0.0], [0.035, -0.04], [0.075, -0.13], [0.078, -0.135]], [0, P2[1], P2[2] + 0.02, 0, tilt, 0], caps=False, double=True, sides=20),
            sphere("bulb", "bulb", 0.026, [0, P2[1] - 0.06 * math.cos(math.radians(tilt)), P2[2] + 0.02 - 0.06 * math.sin(math.radians(tilt))], sides=10),
        ], era="1932-2030")


def write_all():
    write(C + "bar-handle", bar_handle(), "components")
    write(C + "slab-door", slab_door(), "components")
    write(C + "star-base", star_base(), "components")
    for name, f in [("sofa", sofa), ("armchair", armchair), ("office-chair", office_chair), ("desk", desk),
                    ("dining-table", dining_table), ("dining-chair", dining_chair), ("coffee-table", coffee_table),
                    ("bed", bed), ("wardrobe", wardrobe), ("bookshelf", bookshelf), ("tv-stand", tv_stand),
                    ("kitchen", kitchen), ("bar-stool", bar_stool), ("floor-lamp", floor_lamp), ("desk-lamp", desk_lamp)]:
        write("modern/furniture/" + name, f(), "furniture")

GROUPS = {"furniture": "furniture", "components": "components"}
