"""THE ROAD'S VEHICLES (2026-11-20; docs/modern.md): a hatchback, a saloon and its taxi, a bicycle, a motorcycle, a
city bus with its inside, an intercity coach, a box lorry and a delivery van -- each in the vehicle frame (kit.py: the
ground under its middle, +x forward, +z its right), their wheels the shared road wheel, spoked wheel or cast wheel.

The shared components this module writes (modern/components/, group "components"): `cast-wheel` (a motorcycle's or a
scooter's: a round tyre, cast spokes, brake discs), `steering-wheel` (a car's, a bus's, a lorry's, a tractor's),
`door-leaf` (a glazed door panel hinged at one edge: a bus's folding doors, a coach's, a tram's, a shop's), and
`wing-mirror` (a car's on a short arm, a bus's hanging from its long one).

How a car is built (the pattern the van follows): THREE LOFTS. The lower body (paint) up to the waist; the glasshouse
(glass) sitting on it, the windscreen and the rear screen its top; the roof and the pillars (paint) a third loft just
outside the glass over the cabin, its side windows cut as `holes` so the glass shows through them. The glass is
opaque (the library's), so a bus's and a coach's side windows are left OPEN holes, framed: the seats are seen through
them."""
import math
from kit import item, box, rod, lathe, loft, sphere, ring, sweep, plate, use, write, across, arc, hole, station_at, cr_at, shell_over, loft_z, hinge, slide, plug_slide, region, piece, cut, merge, arches, body_arches, arch_gap, pan, steer, steer_in, fill, window_holes, bars

W = "modern/components/"


# ---- THE SHARED COMPONENTS (this module's) -------------------------------------------------------------------------
def cast_wheel():
    # A MOTORCYCLE'S WHEEL: a round-section tyre (a torus drawn out across), a cast rim, `n` straight cast spokes, the
    # hub, one or two brake discs (`discs` 2: both sides, a front wheel's) with their calipers -- the axle along z
    return item("Cast wheel", "components", "a motorcycle's cast wheel: the round-section tyre, the rim, cast spokes, the hub, brake discs and calipers -- the axle along z, a 17-inch rim on a 0.6 m tyre by default",
        {"tyre": "rubber", "rim": "gunmetal", "hub": "aluminium", "disc": "steel", "caliper": "#8a1c1c"}, [
            ring("tyre", "tyre", "r - t", "t", [0, 0, 0, 0, 90, 0], stretch=[1, 1, "wd / (t * 2)"], sides=10),
            lathe("rim", "rim", [["r - t * 1.9", "-wd * 0.42"], ["r - t * 1.75", "-wd * 0.42"], ["r - t * 1.75", "wd * 0.42"], ["r - t * 1.9", "wd * 0.42"]], [0, 0, 0, 0, 90, 0], sides=28),
            box("spoke", "rim", ["r - t * 1.9 - hubR", 0.03, 0.025], [0, 0, 0], around={"n": "n", "r": "(r - t * 1.9 + hubR) / 2", "plane": "xy"}),
            rod("hub", "hub", "hubR", [0, 0, "-wd * 0.55"], [0, 0, "wd * 0.55"], 12),
            lathe("disc", "disc", [["discR * 0.62", -0.003], ["discR", -0.003], ["discR", 0.003], ["discR * 0.62", 0.003]], [0, 0, "wd * 0.5", 0, 90, 0], sides=24, mirror="z", when={"discs": 2}),
            lathe("disc1", "disc", [["discR * 0.62", -0.003], ["discR", -0.003], ["discR", 0.003], ["discR * 0.62", 0.003]], [0, 0, "-wd * 0.5", 0, 90, 0], sides=24, when={"discs": 1}),
            box("caliper", "caliper", [0.09, 0.05, 0.04], ["-discR * 0.66", "discR * 0.66", "wd * 0.5 + 0.02", 0, 0, 45], mirror="z", when={"discs": 2}),
            box("caliper1", "caliper", [0.07, 0.04, 0.04], ["-discR * 0.66", "discR * 0.66", "-wd * 0.5 - 0.02", 0, 0, 45], when={"discs": 1}),
        ], params={"r": 0.3, "t": 0.06, "wd": 0.12, "n": 6, "hubR": 0.05, "discR": 0.15, "discs": 2})


def steering_wheel():
    # A STEERING WHEEL: the rim upright across the car (in the yz plane), three spokes, the boss facing the driver at
    # -x, the column running forward (+x) into the dash; the parent tilts it with a roll (a car's about -20, a bus's
    # almost flat, -55)
    return item("Steering wheel", "components", "a steering wheel: the rim, three spokes, the padded boss facing the driver (-x), the column running forward into the dash -- tilted by its parent",
        {"rim": "plastic-black", "hub": "plastic-black", "column": "plastic-grey"}, [
            ring("rim", "rim", "R", "tube", [0, 0, 0, 0, 0, 90], sides=8),
            rod("spokeD", "hub", 0.016, [0, 0, 0], [0, "-R", 0], 6),
            rod("spokeS", "hub", 0.016, [0, 0, 0], [0, "R * 0.17", "R * 0.98"], 6, mirror="z"),
            lathe("boss", "hub", [[0, -0.035], ["R * 0.3", -0.03], ["R * 0.34", 0.0], ["R * 0.26", 0.04], [0, 0.04]], [0, 0, 0, 0, 0, -90], sides=12),
            rod("column", "column", 0.035, [0.03, 0, 0], ["col", 0, 0], 8),
        ], params={"R": 0.19, "tube": 0.016, "col": 0.3})


def door_leaf():
    # A DOOR LEAF: a glazed panel hinged on its edge at x = 0, running `w` along +x, `h` up from y = 0, `t` thick
    # across z -- its frame (stiles, rails, a kick panel), the glass, a rubber seal on the closing edge, a grab handle
    # on both faces. A bus's folding doors are four of these, a coach's swing door one, a shop's one.
    return item("Door leaf", "components", "a glazed door leaf hinged at its edge (x = 0), w wide along +x and h high: the aluminium frame, a kick panel, the glass, a rubber seal on the closing edge, grab handles",
        {"frame": "aluminium", "glass": "glass", "seal": "rubber", "handle": "chrome", "kick": "plastic-grey"}, [
            box("stileH", "frame", ["s", "h", "t"], ["s / 2", "h / 2", 0]),
            box("stileF", "frame", ["s", "h", "t"], ["w - s / 2", "h / 2", 0]),
            box("railT", "frame", ["w - s * 2", "s", "t"], ["w / 2", "h - s / 2", 0]),
            box("railB", "kick", ["w - s * 2", "kick", "t"], ["w / 2", "kick / 2", 0]),
            box("railM", "frame", ["w - s * 2", "s * 0.7", "t"], ["w / 2", "mid", 0], when="mid"),
            box("glass", "glass", ["w - s * 2", "h - s - kick", "t * 0.35"], ["w / 2", "kick + (h - s - kick) / 2", 0]),
            box("seal", "seal", [0.03, "h", "t * 1.1"], ["w + 0.012", "h / 2", 0]),
            rod("handle", "handle", 0.013, ["w * 0.6", "h * 0.35", "t / 2 + 0.035"], ["w * 0.6", "h * 0.65", "t / 2 + 0.035"], 6, mirror="z", when="handle"),
        ], params={"w": 0.32, "h": 2.1, "t": 0.04, "s": 0.05, "kick": 0.25, "mid": 1.0, "handle": 1})


def wing_mirror():
    # A WING MIRROR: mounted at the origin, its arm swept out to (ax, ay, az), the housing there -- `out` 1 sets it
    # outboard of the arm's end (a car's), `hang` 1 hangs it below (a bus's rabbit-ear mirror) -- the glass on its back
    # (-x), looking behind. Placed on the right side; mirror="z" for the left.
    return item("Wing mirror", "components", "a wing mirror: an arm from its mount, the housing, the glass on its back looking behind -- a car's on a short arm, a bus's hanging from a long one",
        {"shell": "plastic-black", "arm": "plastic-black", "glass": "#b8c6d0"}, [
            sweep("arm", "arm", [[0, 0, 0], ["ax * 0.45", "ay", "az * 0.55"], ["ax", "ay", "az"]], "armR"),
            box("housing", "shell", ["d", "h", "w"], ["ax + d * 0.2", "ay - h / 2 * hang", "az + w / 2 * out"]),
            box("glass", "glass", [0.006, "h * 0.84", "w * 0.88"], ["ax + d * 0.2 - d / 2 - 0.003", "ay - h / 2 * hang", "az + w / 2 * out"]),
        ], params={"ax": 0.0, "ay": 0.0, "az": 0.14, "w": 0.2, "h": 0.12, "d": 0.08, "out": 1, "hang": 0, "armR": 0.016})


def car_seat():
    # A CAR'S SEAT: the origin on the floor under the cushion's middle, its front at +x -- the cushion (its top `h` up),
    # side bolsters (`bolster` wide; 0: a flat rear bench), the back raked 16 degrees with its own bolsters, the
    # headrest on two stalks; `w` wide (a bench: 1.3, its headrests `heads` apart)
    S, C = 0.276, 0.961   # (sin, cos of the rake)
    bx, by = "-d / 2 + 0.07", "h - 0.02"   # (the back's foot)
    return item("Car seat", "components", "a car's seat: the cushion with side bolsters, the back raked 16 degrees with its bolsters, headrests on stalks -- a front bucket seat, or with bolster 0 and w 1.3 the rear bench; its front at +x",
        {"cover": "upholstery-grey", "side": "upholstery-grey", "frame": "plastic-black", "stalk": "chrome"}, [
            box("base", "frame", ["d * 0.7", "h - 0.12", "w * 0.7"], [0, "(h - 0.12) / 2", 0]),
            box("cushion", "cover", ["d", 0.11, "w - bolster * 2"], [0, "h - 0.055", 0], round=0.03),
            box("bolsterC", "side", ["d * 0.95", 0.15, "bolster"], [0, "h - 0.035", "w / 2 - bolster / 2"], mirror="z", when="bolster", round=0.03),
            box("back", "cover", [0.11, "back", "w - bolster * 2"], [f"{bx} - {S} * back / 2", f"{by} + {C} * back / 2", 0, 0, 0, 16], round=0.03),
            box("bolsterB", "side", [0.17, "back * 0.85", "bolster"], [f"{bx} - {S} * back * 0.45 + 0.02", f"{by} + {C} * back * 0.45", "w / 2 - bolster / 2", 0, 0, 16], mirror="z", when="bolster", round=0.03),
            rod("stalk", "stalk", 0.007, [f"{bx} - {S} * back", f"{by} + {C} * back - 0.02", 0.07], [f"{bx} - {S} * (back + 0.07)", f"{by} + {C} * (back + 0.07)", 0.07], 6, mirror="z", when={"heads": 0}),
            box("headrest", "cover", [0.1, 0.16, "hw"], [f"{bx} - {S} * (back + 0.13)", f"{by} + {C} * (back + 0.13)", 0, 0, 0, 16], round=0.03, when={"heads": 0}),
            box("headrests", "cover", [0.1, 0.15, "hw"], [[f"{bx} - {S} * (back + 0.12)", f"{by} + {C} * (back + 0.12)", "heads / 2", 0, 0, 16]], mirror="z", round=0.03, when="heads"),
        ], params={"w": 0.52, "d": 0.5, "h": 0.3, "back": 0.6, "bolster": 0.07, "hw": 0.27, "heads": 0})


def car_dash():
    # A CAR'S DASHBOARD: its frame's origin on the cabin's middle line at the dash's driver-facing top edge -- the body
    # running `d` forward (+x) to the windscreen, `w` across, `h` down; the instrument hood and its dials before the
    # driver (at z = drive * sz: -1 the left, a left-hand drive's), the centre screen, the vents, the glovebox's line,
    # the steering wheel on its column
    return item("Car dashboard", "components", "a car's dashboard: the moulded body running forward to the windscreen, the instrument hood with its dials, the centre screen, four vents, the glovebox, the steering wheel on its column -- the driver at z = drive * sz",
        {"dash": "plastic-black", "dashTop": "plastic-black", "vent": "plastic-grey", "chromeTrim": "chrome"}, [
            loft("body", "dash", [[-0.04, "w / 2 - 0.03", "-h", -0.03, "w / 2 - 0.04"], [0.08, "w / 2", "-h", 0.0, "w / 2 - 0.02"], ["d", "w / 2", "-h * 0.7", -0.03, "w / 2 - 0.02"]], [0.03, 0.07], seg=2),
            box("hood", "dashTop", [0.2, 0.07, 0.44], [0.06, 0.025, "drive * sz", 0, 0, 8]),
            use("dials", W + "screen", [-0.02, -0.055, "drive * sz", 180, 0, -12], {"w": 0.34, "h": 0.11}),
            use("centre", W + "screen", [-0.045, -0.1, 0, 180, 0, -18], {"w": 0.24, "h": 0.15}),
            box("vent", "vent", [0.012, 0.05, 0.13], [[-0.045, -0.2, -0.52], [-0.05, -0.27, -0.09], [-0.05, -0.27, 0.09], [-0.045, -0.2, 0.52]]),
            box("ventTrim", "chromeTrim", [0.012, 0.006, 0.6], [-0.047, -0.31, 0]),
            box("glovebox", "vent", [0.008, 0.004, 0.36], [-0.05, -0.3, "-drive * sz"]),
            use("wheel", W + "steering-wheel", [-0.17, -0.1, "drive * sz", 0, 0, -24], {"R": 0.185, "col": 0.22}),
        ], params={"w": 1.42, "d": 0.42, "h": 0.4, "drive": -1, "sz": 0.37})


def door_card():
    # A DOOR'S INSIDE: the trim panel centred at the origin, `w` along x and `h` up, facing -z (into the cabin: a right
    # door's -- the left one mirrored); the cloth insert, the armrest and its pull, the handle, the speaker low at the front
    return item("Door card", "components", "the inside of a car's door: the trim panel facing -z (into the cabin), its cloth insert, the armrest with its pull, the opening handle, the speaker low at the front",
        {"card": "plastic-grey", "insert": "upholstery-grey", "pull": "plastic-black", "lever": "chrome"}, [
            box("panel", "card", ["w", "h", 0.03], [0, 0, 0]),
            box("insert", "insert", ["w * 0.6", "h * 0.22", 0.012], ["-w * 0.08", "h * 0.18", -0.018]),
            box("arm", "card", ["w * 0.5", 0.05, 0.08], ["-w * 0.12", "-h * 0.05", -0.05]),
            box("pull", "pull", [0.12, 0.035, 0.03], ["-w * 0.12", "-h * 0.05 + 0.045", -0.08]),
            box("lever", "lever", [0.08, 0.025, 0.012], ["w * 0.28", "h * 0.28", -0.02]),
            lathe("speaker", "pull", [[0, 0], [0.075, 0], [0.075, 0.01], [0, 0.012]], ["w * 0.3", "-h * 0.32", -0.015, 0, -90, 0], sides=14),
        ], params={"w": 1.0, "h": 0.55})


# ---- HELPERS -------------------------------------------------------------------------------------------------------
def wheels(xs, track, r, w, spokes=5, rim=0.62, mats=None, name="wheel", lock=None):
    """road wheels at each x, both sides (track: between the wheels' centres), their outside faces out; `lock` (degrees):
    the FIRST x's pair steered by the item's `steer` param (kit.steer), each about the upright through its centre"""
    one = lambda i, x, **k: use(f"{name}{i}", W + "wheel", [x, r, track / 2], {"r": r, "w": w, "spokes": spokes, "rim": rim}, mats, **k)
    return [q for i, x in enumerate(xs) for q in (steer("steer", [x, r, track / 2], [one(i, x)], lock) if lock and i == 0 else [one(i, x, mirror="z")])]


def screen_slab(id_, mat, st, x0, x1, width, n=6, lift=0.012, thick=0.02):
    """a rear screen (or any glazing) lying on a loft's top between x0 and x1: its side profile followed at the top
    (`lift` above it), extruded `width` across -- set over a painted roof that runs on to the tail"""
    xs = [x0 + (x1 - x0) * k / n for k in range(n + 1)]
    top = [[x, cr_at(st, x)[2] + lift] for x in xs]
    return plate(id_, mat, top + [[x, y - thick] for x, y in reversed(top)], width, [0, 0, 0])


def a_pillar(id_, mat, st, x0, x1, n=5, r=0.035):
    """the A-pillar: a tube down the glasshouse's front corner from the roof (x0) to the windscreen's foot (x1)"""
    pts = []
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n
        hw, y0, y1, tw = cr_at(st, x)
        pts.append([x, y1 - 0.035, tw - 0.012])
    return sweep(id_, mat, pts, r, mirror="z")


# ---- CARS ----------------------------------------------------------------------------------------------------------
# (a car's spec: its length, axles, wheel; the lower BODY's stations (x, half-width, bottom, top, top half-width), the
#  GLASSHOUSE's, where the windscreen's top meets the roof (`ws`), the side windows (x ranges), the door seams, the
#  handles, and the rear screen (x from the roof to its foot))
BODY_R, GLASS_R = [0.12, 0.1], [0.02, 0.13]
HATCH = dict(L=4.28, xf=1.27, xr=-1.37, r=0.315, track=1.54,
    body=[[-2.14, .80, .38, .98, .74], [-2.09, .87, .27, 1.02, .80], [-1.7, .89, .23, 1.03, .82], [-0.5, .895, .21, 1.0, .825],
          [0.9, .89, .22, .975, .82], [1.6, .875, .24, .92, .79], [1.98, .83, .27, .86, .74], [2.14, .76, .33, .8, .64]],
    glass=[[-2.06, .68, .9, 1.03, .6], [-1.95, .71, .9, 1.22, .6], [-1.75, .73, .9, 1.37, .61], [-1.2, .745, .9, 1.44, .625],
           [-0.15, .75, .9, 1.46, .63], [0.3, .77, .9, 1.31, .67], [0.9, .8, .9, .97, .745]],
    ws=-0.05, wins=[(-0.55, 0.0), (-1.3, -0.66)], rs=(-1.78, -2.05),
    doors=[dict(body=[(-0.55, 0.86)], glass=(-0.55, 0.9), handle=0.45), dict(body=[(-0.98, -0.66), (-1.32, -0.98, 0.72)], glass=(-1.3, -0.66), handle=-0.95)],
    seats=dict(front=-0.25, rear=-1.12, dash=0.47, boot=-1.5), gate=dict(x=-2.0, y=0.52, hinge=-1.77, roof=True))
SALOON = dict(L=4.7, xf=1.42, xr=-1.43, r=0.32, track=1.56,
    body=[[-2.35, .82, .40, 1.03, .78], [-2.28, .88, .30, 1.065, .82], [-1.8, .9, .25, 1.065, .83], [-0.5, .905, .22, 1.02, .83],
          [0.95, .9, .23, .975, .83], [1.75, .885, .25, .91, .8], [2.2, .84, .28, .85, .74], [2.35, .77, .33, .79, .64]],
    glass=[[-1.88, .72, .9, 1.06, .66], [-1.55, .745, .9, 1.24, .64], [-1.0, .755, .9, 1.43, .63], [-0.15, .76, .9, 1.46, .635],
           [0.35, .775, .9, 1.31, .67], [0.95, .8, .9, .97, .745]],
    ws=-0.05, wins=[(-0.55, 0.0), (-1.12, -0.66), (-1.42, -1.2)], rs=(-1.08, -1.85),
    doors=[dict(body=[(-0.55, 0.98)], glass=(-0.55, 0.95), handle=0.5), dict(body=[(-1.02, -0.66), (-1.2, -1.02, 0.76)], glass=(-1.12, -0.66), handle=-0.95)],
    seats=dict(front=-0.25, rear=-1.12, dash=0.52, boot=-1.45), gate=dict(x=-1.9, y=0.72, hinge=-1.9, roof=False))


def car_parts(S):
    """the parts of a car drawn from its spec (HATCH, SALOON): the three lofts -- the body, a shell open below; the
    glasshouse (window glass, seen through); the roof, pillars and rear quarters over it, the side windows holes in it --
    the rear screen laid on it; THE DOORS, each cut out of those same lofts (`only`) and hinged at its front edge, with
    its handle, waist trim and door card (a front one its mirror); INSIDE the floor pan and the wheel tubs, the
    dashboard and its wheel, the seats, the console, the headliner; under it the undertray; lamps, bumpers, wheels"""
    L, xf, xr, r, tr, B, g = S["L"], S["xf"], S["xr"], S["r"], S["track"], S["body"], S["glass"]
    nose, tail = L / 2, -L / 2
    belt, xa, xt = 1.0, g[-1][0] - 0.01, g[0][0]
    roof = shell_over(g, [xt + (S["ws"] - xt) * k / 10 for k in range(11)])
    zb = lambda x, y: loft_z(B, BODY_R, x, y)
    hz = loft_z(B, BODY_R, nose - 0.1, .7)
    zn = min(cr_at(B, nose)[0] - 0.13, 0.62)
    x0, x1 = S["rs"]
    sw = 2 * (cr_at(g, (x0 + x1) / 2)[3] - 0.13)
    D, ST = S["doors"], S["seats"]
    sill, top, gap = 0.3, 1.43, 0.006
    arch = body_arches([xf, xr], r)
    zin = tr / 2 - 0.205 / 2 - 0.07                     # (the wheel tubs' inner walls; the front's further in,
    zinF = steer_in(tr, r, 0.205)                        #  clear of the steered tyre at full lock)
    under = lambda x: cr_at(B, x)[1] + 0.004             # (the floor pan's underside: kit.pan's lift)
    BODY = loft("body", "paint", B, BODY_R, seg=6, arches=arch, bare=["bottom"], double=True)   # (the three lofts, once: the
    GLASS = loft("glass", "glazing", g, GLASS_R, seg=5, bare=["bottom"])                       #  body, the doors and the
    ROOF = loft("roof", "paint", roof, GLASS_R, seg=1, double=True, caps=[True, False], bare=["bottom"])   # gate cut from them)
    def door(i, d):
        """a door: the body's and the glass's stretch it closes, cut from their lofts, hinged at its front edge"""
        (ga, gb), skin = d["glass"], d["body"]       # (the skin: stretches (x0, x1[, y0 over the arch]) -- a rear door's
        a, b = min(q[0] for q in skin), max(q[1] for q in skin)   #  reaches back over its wheel above the arch, L-shaped)
        hx, hy = b, 0.62
        cx, cy = (a + b) / 2, 0.76 if i else 0.68
        cw = (b - a - 0.16) if not i else (b - a - 0.14)
        return hinge(f"door{i}", [hx, hy, zb(hx, hy) - 0.01], [
            piece(BODY, [region(q[0], q[1], q[2] if len(q) > 2 else sill) for q in skin], "skin"),
            piece(GLASS, [region(ga, gb, 0.0, top)], "pane"),
            sweep("waist", "trim", [[gb - 0.03, belt - 0.005, cr_at(g, gb - .03)[0] - 0.003], [ga + 0.01, belt + 0.004, cr_at(g, ga)[0] + 0.006]], 0.009),
            box("handle", "chrome", [0.16, 0.025, 0.02], [d["handle"], .86, zb(d["handle"], .86) + 0.006]),
            use("card", W + "door-card", [cx - (0.02 if i else 0.05), cy, zb(cx, cy) - 0.05], {"w": cw, "h": 0.5 if not i else 0.36}),
            use("mirror", W + "wing-mirror", [xa - 0.1, 1.0, cr_at(g, xa - .1)[0] - .02], {"az": 0.07, "w": 0.19, "h": 0.11, "d": 0.09}, {"shell": "paint"}) if not i else None,
        ], max_=62 if not i else 66, mirror="z")
    G = S["gate"]                                        # (THE TAILGATE -- a hatch's: the rear face above the bumper and the roof's tail
    gR = lambda grow=0.0: region(tail - 1, G["x"] - grow, G["y"] + grow, 9, "both", all=True)   #  with the screen; a saloon's boot lid: the deck)
    gx = G["hinge"]
    gy = cr_at(roof, gx)[2] + 0.012 if G["roof"] else cr_at(B, gx)[2] + 0.01
    def gate():
        return hinge("gate", [gx, gy, 0], [
            piece(BODY, [gR()], "skin"),
            *([piece(GLASS, [gR()], "glassG"), piece(ROOF, [gR()], "roofG")] if G["roof"] else []),
            *([screen_slab("rearScreen", "glass", roof, x0, x1, sw),
               sweep("screenSeal", "trim", [[x0 + .02, cr_at(roof, x0)[2] + 0.004, z] for z in (-sw / 2, sw / 2)], 0.012)] if G["roof"] else []),
                use("tail", W + "lamp", [tail - 0.006, .86, cr_at(B, tail)[0] - 0.2, 180, 0, 0], {"shape": "square", "r": 0.17, "h": 0.09}, {"lens": "lamp-red"}, mirror="z"),
            box("plateR", "plate", [0.01, 0.11, 0.52], [tail - 0.012, .6 if G["y"] < 0.6 else .8, 0]),
            box("spoiler", "paint", [0.2, 0.025, 1.08], [x0 + .0, cr_at(roof, x0)[2] + .01, 0, 0, 0, -6], when="hatch"),
            box("wiperR", "trim", [0.02, 0.012, 0.4], [x1 + 0.08, cr_at(roof, x1 + .08)[2] + 0.03, 0.1, 0, 0, 0], when="hatch"),
            box("gateHandle", "chrome", [0.012, 0.025, 0.18], [tail - 0.012, .72 if G["y"] < 0.6 else .9, 0]),
                ], axis=(0, 0, 1), max_=-72 if G["roof"] else -58)
    fl = 0.31                                            # (the floor's top)
    zc = zb(0, 0.7) - 0.06                               # (the cabin's inside at the waist)
    parts = [
        cut(BODY, [region(q[0], q[1], q[2] if len(q) > 2 else sill, 9, "both") for d in D for q in d["body"]] + [region(xt + 0.03, xa, belt - 0.1, 9, "both", all=True, z=[0, cr_at(g, 0)[0] - 0.02]), gR()]),
        cut(GLASS, [region(*d["glass"], 0.0, top, "both") for d in D] + ([gR()] if G["roof"] else [])),
        cut(ROOF, [hole(a, b, belt, top) for a, b in S["wins"]] + ([gR()] if G["roof"] else [])),
        loft("headliner", "headliner", shell_over(g, [xt + 0.02 + (S["ws"] - 0.04 - xt) * k / 10 for k in range(11)], -0.02), GLASS_R, seg=1,
             holes=[hole(a, b, belt - 0.05, top + 0.02) for a, b in S["wins"]] + ([gR(0.03)] if G["roof"] else []), bare=["bottom"], caps=False, double=True),
        gate(),
        *([] if G["roof"] else [screen_slab("rearScreen", "glass", roof, x0, x1, sw),
              sweep("screenSeal", "trim", [[x0 + .02, cr_at(roof, x0)[2] + 0.004, z] for z in (-sw / 2, sw / 2)], 0.012)]),
        a_pillar("aPillar", "paint", g, S["ws"] + 0.03, xa),
        *[door(i, d) for i, d in enumerate(D)],
        sweep("sill", "trim", [[xr + r + .1, .27, zb(0, .27) - 0.01], [xf - r - .1, .27, zb(0, .27) - 0.01]], 0.03, mirror="z"),
        # (INSIDE: the floor pan and its carpet, the firewall, the tubs' cups, the dash and its wheel, the console and
        #  the gear lever, two bucket seats and the rear bench, the boot's floor)
        box("floor", "carpet", [ST["dash"] + 0.45 - ST["rear"] + 0.35, 0.04, 2 * zc], [(ST["dash"] + 0.45 + ST["rear"] - 0.35) / 2, fl - 0.02, 0]),
        box("bootFloor", "carpet", [ST["boot"] - tail - 0.1, 0.04, 2 * zin - 0.02], [(ST["boot"] + tail + 0.1) / 2, 0.42, 0]),
        box("firewall", "under", [0.03, 0.5, 2 * zc], [ST["dash"] + 0.46, fl + 0.25, 0]),
        use("dash", W + "car-dash", [ST["dash"], 0.99, 0], {"w": 2 * zc + 0.04}),
        box("console", "trim", [0.62, 0.2, 0.2], [ST["dash"] - 0.25, fl + 0.12, 0]),
        rod("gear", "chrome", 0.008, [ST["dash"] - 0.1, fl + 0.22, 0], [ST["dash"] - 0.14, fl + 0.38, 0], 6),
        sphere("gearKnob", "trim", 0.025, [ST["dash"] - 0.14, fl + 0.39, 0]),
        use("seatF", W + "car-seat", [ST["front"], fl, 0.37], mirror="z"),
        use("bench", W + "car-seat", [ST["rear"], fl, 0], {"w": 2 * zin - 0.04, "bolster": 0, "h": 0.33, "back": 0.56, "heads": 0.74, "hw": 0.24}),
        # (UNDER IT: the floor pan, nose to tail and side to side under the open body, round the wheels' tubs)
        *pan("pan", "under", B, BODY_R, tail, nose, [arch_gap(x, r, under(x)) for x in (xf, xr)], [zinF, zin]),
        # (the nose: slim lamps joined by the upper grille, the wide intake below, its plate, the lip)
        use("head", W + "lamp", [nose + 0.006, .7, zn - 0.17], {"shape": "square", "r": 0.17, "h": 0.06}, mirror="z"),
        box("headSide", "lamp", [0.12, 0.05, 0.02], [nose - 0.1, .7, hz - 0.012, 40, 0, 0], mirror="z"),
        box("grille", "trim", [0.02, 0.07, (zn - 0.34) * 2], [nose + 0.004, .7, 0]),
        plate("intake", "trim", [[-.55, 0], [.55, 0], [.47, .2], [-.47, .2]], 0.02, [nose + 0.006, .36, 0, 90, 0, 0]),
        box("lip", "trim", [0.1, 0.035, 1.3], [nose - 0.04, .36, 0]),
        box("drl", "lamp", [0.02, 0.025, 0.16], [nose + 0.008, .42, 0.6], mirror="z"),
        box("plateF", "plate", [0.01, 0.11, 0.52], [nose + 0.018, .47, 0]),
        # (the tail: lamps wrapping round onto the sides, the plate, the diffuser; a hatch's spoiler and wiper)
        box("tailSide", "lamp-red", [0.14, 0.09, 0.02], [tail + 0.08, .86, zb(tail + 0.08, .86) + 0.004, -12, 0, 0], mirror="z"),
        box("diffuser", "trim", [0.1, 0.1, 1.3], [tail + 0.02, .36, 0]),
        box("wiper", "trim", [0.42, 0.012, 0.02], [[xa - 0.12, .985, -0.2, 8, 0, 8], [xa - 0.12, .985, 0.35, 8, 0, 8]]),
        *arches([xf, xr], r, zb(xf, r + .2) - 0.01, tr, inner=[zinF, zin], cup=True, skin=zb, low=lambda x: cr_at(B, x)[1], floor=under),
        *wheels([xf, xr], tr, r, 0.205, lock=35),
    ]
    return parts


CAR_MATS = {"glass": "glass", "glazing": "window-glass", "trim": "plastic-black", "well": "#141416", "chrome": "chrome", "plate": "plastic-white",
            "carpet": "carpet-grey", "headliner": "#c9c6bd", "under": "#232426"}
CAR_SEATS = [{"role": "seat", "at": [-0.25, 0.59, z], "data": {"face": 0}} for z in (-0.37, 0.37)]


def car():
    # A FAMILY HATCHBACK (the Golf's class, 4.28 x 1.79 x 1.46 m, wheelbase 2.64 m): a short bonnet, the windscreen
    # raked well back, the roof falling a little to the tailgate's raked screen; the waist rising toward the tail.
    return item("Car", "vehicle", "a five-door family hatchback of the 2010s-20s, 4.28 x 1.79 x 1.46 m, wheelbase 2.64 m: lofted body, glasshouse and roof (the side windows cut in it), slim wrap-round lamps, mirrors, a spoiler over the tailgate, four alloy wheels in their arches -- its paint drawn by the seed",
        {"paint": {"pick": ["paint-red", "paint-blue", "paint-white", "paint-silver", "paint-black", "paint-green", "paint-grey"]}, **CAR_MATS}, car_parts(HATCH), params={"hatch": 1, "open": 0, "steer": 0},
        markers=CAR_SEATS)


def saloon(taxi=False):
    # A SALOON (a four-door notchback, 4.7 x 1.8 x 1.46 m, wheelbase 2.85 m): the rear screen falling to a boot deck
    # between broad C-pillars, a small quarter light; the TAXI is it in yellow, a lit roof sign, a chequered band
    parts = car_parts(SALOON)
    if taxi:
        parts += [
            box("signBase", "trim", [0.32, 0.03, 0.62], [-0.55, 1.48, 0]),
            box("sign", "signLamp", [0.26, 0.13, 0.56], [-0.55, 1.56, 0]),
            box("signFace", "#1a1a1a", [0.02, 0.07, 0.36], [[-0.42, 1.565, 0], [-0.68, 1.565, 0]]),
            box("chequer", "#151515", [0.07, 0.035, 0.012], [0, .755, .9], along={"n": 14, "from": [-1.45, 0, 0], "to": [1.35, 0, 0]}, mirror="z"),
            box("chequer2", "#151515", [0.07, 0.035, 0.012], [0, .72, .9], along={"n": 14, "from": [-1.35, 0, 0], "to": [1.45, 0, 0]}, mirror="z"),
        ]
    paint = "paint-yellow" if taxi else {"pick": ["paint-silver", "paint-black", "paint-navy", "paint-white", "paint-maroon", "paint-grey"]}
    about = ("a city taxi: the saloon in taxi yellow, a lit TAXI sign on the roof, a chequered band along both sides" if taxi else
             "a four-door saloon of the 2010s-20s, 4.7 x 1.8 x 1.46 m, wheelbase 2.85 m: the rear screen falling to a boot deck between broad C-pillars, wrap-round lamps, four alloy wheels in their arches -- its paint drawn by the seed")
    return item("Taxi" if taxi else "Saloon", "vehicle", about,
        {"paint": paint, **CAR_MATS, "signLamp": "lamp"}, parts, params={"hatch": 0, "open": 0, "steer": 0}, markers=CAR_SEATS)


# ---- TWO WHEELS ----------------------------------------------------------------------------------------------------
def bicycle():
    # A BICYCLE (a town bike, the diamond frame): the frame of tubes, the fork, two spoked wheels, the saddle, the
    # handlebar and its grips, the chainset and the chain, the pedals
    r = 0.35
    BB, RA, FA, ST, HT, HB = [0, .3, 0], [-0.52, r, 0], [0.55, r, 0], [-0.13, .86, 0], [0.4, .84, 0], [0.45, .66, 0]
    f = "frame"
    parts = [
        use("rear", W + "spoked-wheel", [RA[0], r, 0], {"r": r}),
        use("front", W + "spoked-wheel", [FA[0], r, 0], {"r": r}),
        rod("seatTube", f, .016, BB, ST), rod("topTube", f, .016, [-0.1, .8, 0], HT), rod("downTube", f, .02, BB, HB),
        rod("headTube", f, .022, [0.39, .87, 0], [0.46, .63, 0]),
        rod("chainstay", f, .01, [0, .3, .04], [RA[0], r, .05], mirror="z"), rod("seatstay", f, .009, [-0.11, .79, .03], [RA[0], r, .05], mirror="z"),
        sweep("fork", f, [[0.46, .63, .045], [0.5, .48, .05], [0.555, r + .01, .05]], .012, mirror="z"),
        rod("post", "chrome", .013, [-0.12, .84, 0], [-0.16, .97, 0]),
        sphere("saddle", "saddle", 0.1, [-0.19, .985, 0], stretch=[1.4, 0.32, 0.85], sides=12),
        sphere("saddleNose", "saddle", 0.05, [-0.08, .98, 0], stretch=[1.6, 0.6, 0.9], sides=10),
        rod("stem", "chrome", .013, [0.39, .87, 0], [0.36, 1.0, 0]),
        sweep("bar", "chrome", [[0.25, 1.02, -.28], [0.33, 1.0, -.2], [0.36, 1.0, 0], [0.33, 1.0, .2], [0.25, 1.02, .28]], .011),
        rod("grip", "grip", .017, [0.27, 1.02, .2], [0.24, 1.02, .3], 8, mirror="z"),
        ring("chainring", "chrome", .095, .006, [0, .3, .07, 0, 90, 0]),
        ring("sprocket", "chrome", .04, .005, [RA[0], r, .07, 0, 90, 0]),
        sweep("chain", "chain", [[0, .395, .07], [RA[0], r + .04, .07], [RA[0] - .04, r, .07], [RA[0], r - .04, .07], [0, .205, .07], [0.095, .3, .07]], .004, closed=True),
        rod("crank", "chrome", .009, [0, .3, .085], [0.1, .14, .085]), rod("crankL", "chrome", .009, [0, .3, -.06], [-0.1, .46, -.06]),
        box("pedal", "trim", [.09, .02, .08], [[0.1, .14, .14], [-0.1, .46, -.12]]),
        rod("axleBB", "chrome", .012, [0, .3, -.07], [0, .3, .09]),
        sweep("fender", "paint", [[RA[0] + .3, r + .2, 0], [RA[0], r + .4, 0], [RA[0] - .32, r + .16, 0]], None, section=[0.05, 0.006], up=[0, 1, 0], when="fenders"),
        box("rack", "chrome", [0.34, 0.012, 0.14], [RA[0] + .02, r + .44, 0], when="fenders"),
        rod("rackStay", "chrome", .006, [RA[0] - .12, r + .435, .07], [RA[0], r, .06], 4, mirror="z", when="fenders"),
        rod("rackArm", "chrome", .006, [RA[0] + .18, r + .435, .06], [-0.12, .8, .03], 4, mirror="z", when="fenders"),
        sweep("fenderF", "paint", [[FA[0] - .26, r + .22, 0], [FA[0], r + .4, 0], [FA[0] + .3, r + .2, 0]], None, section=[0.05, 0.006], up=[0, 1, 0], when="fenders"),
    ]
    return item("Bicycle", "vehicle", "a town bicycle, the diamond frame: its tubes, the fork, two wire-spoked wheels, the saddle on its post, a swept handlebar, the chainset, chain and pedals, mudguard and rack",
        {"frame": {"pick": ["paint-green", "paint-navy", "paint-red", "paint-black", "paint-cream"]}, "paint": "paint-black", "chrome": "chrome", "saddle": "leather-dark", "grip": "leather-dark",
         "chain": "steel", "trim": "plastic-black"}, parts, params={"fenders": 1},
        markers=[{"role": "seat", "at": [-0.17, 1.0, 0], "data": {"face": 0}}])


# ---- BUSES ---------------------------------------------------------------------------------------------------------
def bus_seat(id_, x, z, y, w=0.42, headrest=0, yaw=0, pedestal=1):
    """a bus's or a coach's seat at (x, z), standing on a floor or a podium at y: a moulded shell (flat, cheap) with a
    grab rail on its back"""
    return use(id_, W + "seat", [x, y, z, yaw, 0, 0], {"w": w, "d": 0.42, "h": 0.44, "back": 0.5 if not headrest else 0.62, "headrest": headrest, "pedestal": pedestal, "grab": 1 - headrest},
               {"cover": "moquette", "frame": "seatShell"})


def seat_pairs(id_, xs, side, y, outer, inner, **k):
    """pairs of seats at each x on one side (-1 left, +1 right): the window seat at `outer`, the aisle seat at `inner`"""
    out = []
    for i, x in enumerate(xs):
        out += [bus_seat(f"{id_}{i}o", x, side * outer, y, pedestal=0, **k), bus_seat(f"{id_}{i}i", x, side * inner, y, pedestal=0, **k)]
    # (the pair's frame: a slim leg under the aisle seat, a rail under both cushions to the wall)
    out.append(box(f"{id_}Leg", "seatShell", [0.05, 0.3, 0.05], [[x, y + 0.15, side * inner] for x in xs]))
    out.append(box(f"{id_}Rail", "seatShell", [0.06, 0.05, outer - inner + 0.4], [[x, y + 0.3, side * (outer + inner) / 2] for x in xs]))
    return out


def folding_door(id_, a, b, z, y0, h, side=1, fold=80):
    """a bus's folding (jack-knife) door between x = a and b in a side at z, shut: at each jamb two leaves in the
    side's plane, the first HINGED at the jamb, the second hinged on the first's far edge -- opening (items.js hinge,
    the item's `open`), the first swings in by `fold` degrees and the second folds back by twice that: a narrow V
    standing into the bus"""
    w = (b - a) / 4 - 0.008
    out = []
    for j, (x, s) in enumerate([(a + 0.012, 1), (b - 0.012, -1)]):
        yaw, ang = 0 if s > 0 else 180, fold * s * side          # (+y turns +x toward -z: a positive angle swings a leaf running +x inward on the +z side)
        out.append(hinge(f"{id_}L{j}", [x, y0, z], [
            use("a", W + "door-leaf", [x, y0, z, yaw, 0, 0], {"w": w, "h": h, "t": 0.035}),
            hinge("b", [x + s * (w + 0.008), y0, z], [
                use("b", W + "door-leaf", [x + s * (w + 0.008), y0, z, yaw, 0, 0], {"w": w, "h": h, "t": 0.035, "handle": 0}),
            ], max_=-2 * ang),
        ], max_=ang))
    return out


def jambs(id_, doors, z, y0, y1, mat="trim"):
    """the rubber-sealed frame round each door opening: two posts and a head, over the shell's cut edge"""
    out = []
    for i, (a, b) in enumerate(doors):
        out += [box(f"{id_}{i}p", mat, [0.06, y1 - y0, 0.07], [[a, (y0 + y1) / 2, z], [b, (y0 + y1) / 2, z]]),
                box(f"{id_}{i}h", mat, [b - a + 0.06, 0.06, 0.07], [(a + b) / 2, y1, z])]
    return out


def city_bus():
    # A CITY BUS (the 12 m low-floor single-decker, a Citaro's class: 12.0 x 2.55 x 3.1 m, wheelbase 5.9 m, the floor
    # 34 cm above the road from the front to the third door): a lofted shell, single-sided, and inside it a LINING (the
    # light grey walls and ceiling, seen from both sides) with the same windows and doors cut through both. Three
    # double doors on the right (+z: driving on the right), their folding leaves standing open; inside the floor, the
    # wheel housings with seats on podiums, rows of seats, the wheelchair bay opposite the middle door, yellow
    # stanchions and ceiling rails, stop buttons, the lights, the driver's cab with its seat, steering wheel and
    # dashboard; the rear platform over the engine, a step up. The windows are open (the glass is opaque): the seats
    # are seen through them.
    L, hw, r, xf, xr = 12.0, 1.275, 0.48, 3.3, -2.6
    y0, y1, ws0, ws1, fl = 0.28, 3.02, 1.12, 2.55, 0.36
    zl = hw - 0.04                                            # (the lining's side)
    D = [(4.2, 5.4), (0.0, 1.25), (-4.45, -3.35)]              # (the doors, right side)
    winL = [(4.95, 5.82)] + fill(-5.35, 4.8, 1.45)
    winR = [(5.55, 5.82)] + fill(1.4, 4.05, 1.3) + fill(-3.2, -0.15, 1.45) + [(-5.35, -4.6)]
    holes = window_holes(winL, ws0, ws1, "left") + window_holes(winR, ws0, ws1, "right") + window_holes(D, 0.15, ws1, "right")
    shell = [[-6.0, 1.24, .32, 2.98, 1.16], [-5.9, hw, y0, y1, 1.2], [5.88, hw, y0, y1, 1.2], [6.0, 1.245, .3, 2.99, 1.17]]
    lining = [[-5.96, zl, fl - 0.04, 2.72, zl - 0.06], [5.92, zl, fl - 0.04, 2.72, zl - 0.06]]
    hx = [(xf - 0.66, xf + 0.66), (xr - 0.66, xr + 0.66)]     # (the wheel housings' x)
    sideFloor = []                                            # (the floor beside the aisle, broken by the housings)
    xa = -4.65
    for a, b in sorted(hx) + [(5.96, 6)]:
        sideFloor.append((xa, a)); xa = b
    poleL, poleR = [2.85, 1.95, -0.2, -1.1, -2.0, -3.05, -3.85], [2.85, 1.4, -0.15, -1.15, -2.0, -3.1]
    poles = [[x, -0.34] for x in poleL] + [[x, 0.34] for x in poleR]
    parts = [
        # (THE SHELL and its lining, the floor, the podiums)
        loft("shell", "paint", shell, [0.1, 0.3], seg=1, holes=holes, arches=body_arches([xf, xr], r), bare=["bottom"]),
        loft("lining", "lining", lining, [0.02, 0.17], seg=1, holes=holes, arches=body_arches([xf, xr], r), caps=[True, False], double=True, bare=["bottom"]),   # (its bottom had run across through the wheels)
        # (UNDER IT: the floor pan, round the wheel housings -- the shell's bottom had run on under the wheels)
        *pan("pan", "under", shell, [0.1, 0.3], -6.0, 6.0, [arch_gap(x, r, cr_at(shell, x)[1] + 0.004) for x in (xf, xr)], 0.4),
        box("floor", "floor", [5.96 + 4.65, 0.06, 0.74], [(5.96 - 4.65) / 2, fl - 0.03, 0]),
        *[box(f"floorS{i}", "floor", [b - a, 0.06, zl - 0.37], [(a + b) / 2, fl - 0.03, (zl + 0.37) / 2], mirror="z") for i, (a, b) in enumerate(sideFloor)],
        box("platform", "floor", [1.31, 0.42, 2 * zl], [-5.305, 0.57, 0]),
        box("step", "floor", [0.2, 0.21, 2 * zl], [-4.55, 0.465, 0]),
        box("stepEdge", "pole", [0.03, 0.012, 2 * zl], [-4.46, 0.572, 0]),
        # (the wheel housings: a lid, an inner wall, two ends -- open to the arch, the wheel turning in them)
        *[p for i, (a, b) in enumerate(hx) for p in (
            box(f"hLid{i}", "lining", [b - a, 0.05, zl - 0.36], [(a + b) / 2, 1.05, (zl + 0.36) / 2], mirror="z"),
            box(f"hWall{i}", "lining", [b - a, 0.69, 0.03], [(a + b) / 2, 0.705, 0.375], mirror="z"),
            box(f"hEnd{i}", "lining", [0.03, 0.69, zl - 0.36], [[a, 0.705, (zl + 0.36) / 2], [b, 0.705, (zl + 0.36) / 2]], mirror="z"),
            box(f"hNose{i}", "pole", [b - a, 0.012, 0.03], [(a + b) / 2, 1.08, 0.365], mirror="z"))],
        # (THE SEATS: pairs on the housings' podiums and the floor, the platform's two rows; the wheelchair bay)
        *seat_pairs("sL", [xf, xr], -1, 1.075, 0.99, 0.57),
        *seat_pairs("sR", [xf, xr], 1, 1.075, 0.99, 0.57),
        *seat_pairs("sLf", [2.5, -0.65, -1.45, -3.45, -4.2], -1, fl, 0.99, 0.57),
        *seat_pairs("sRf", [2.5, 1.75, -0.75, -1.5], 1, fl, 0.99, 0.57),
        *seat_pairs("sP", [-5.05], -1, 0.78, 0.99, 0.57), *seat_pairs("sQ", [-5.05], 1, 0.78, 0.99, 0.57),
        *[bus_seat(f"back{i}", -5.62, z, 0.78, w=0.44) for i, z in enumerate([-0.96, -0.48, 0, 0.48, 0.96])],
        box("bayBoard", "seatShell", [0.08, 0.75, 0.6], [0.15, 0.95, -0.9]),
        box("bayPad", "moquette", [0.04, 0.5, 0.5], [0.21, 1.0, -0.9]),
        box("bayMark", "#2d5fa8", [1.4, 0.004, 0.75], [0.95, fl + 0.002, -0.82]),
        rod("bayRail", "pole", 0.018, [0.2, 0.9, -1.2], [1.85, 0.9, -1.2], 8),
        # (THE STANCHIONS: poles at the seats' aisle ends and in the doors, rails under the ceiling with their hangers,
        #  a red stop button on each pole, the ceiling's light strips)
        rod("pole", "pole", 0.019, [0, fl, 0], [0, 2.72, 0], 8, at=[[x, 0, z] for x, z in poles]),
        rod("doorPole", "pole", 0.019, [0, fl, 0], [0, 2.72, 0], 8, at=[[(a + b) / 2, 0, 0.95] for a, b in D[1:]] + [[4.3, 0, 0.9]]),
        box("stop", "#c41e1e", [0.05, 0.07, 0.05], [[x, 1.45, z + (0.03 if z > 0 else -0.03)] for x, z in poles]),
        rod("rail", "pole", 0.017, [-4.6, 2.05, 0.46], [4.7, 2.05, 0.46], 8, mirror="z"),
        rod("hanger", "pole", 0.012, [0, 2.05, 0.46], [0, 2.72, 0.46], 6, at=[[x, 0, 0] for x in (-4.4, -2.2, 0, 2.2, 4.4)], mirror="z"),
        box("light", "lamp", [9.8, 0.02, 0.16], [-0.3, 2.705, 0.72], mirror="z"),
        box("adPanel", "#e8e6df", [10.2, 0.14, 0.01], [-0.3, 2.62, zl - 0.07], mirror="z"),
        # (THE DRIVER'S CAB: a raised floor, the seat, the wheel, the dashboard and its screen, the partition, the ticket
        #  printer; the validators at the doors)
        box("cabFloor", "floor", [1.1, 0.2, zl - 0.4], [5.41, 0.46, -(zl + 0.4) / 2]),
        bus_seat("driver", 5.0, -0.76, 0.56, w=0.5, headrest=1),
        use("wheelD", W + "steering-wheel", [5.48, 1.2, -0.76, 0, 0, -58], {"R": 0.24, "col": 0.32}),
        box("dash", "trim", [0.42, 0.85, 2 * zl], [5.75, 0.785, 0]),
        box("dashTop", "trim", [0.3, 0.18, 1.1], [5.75, 1.26, -0.65, 0, 0, -20]),
        use("dials", W + "screen", [5.565, 1.33, -0.76, 180, 0, -20], {"w": 0.36, "h": 0.14}),
        box("partition", "seatShell", [0.04, 0.7, zl - 0.38], [4.85, 0.91, -(zl + 0.38) / 2]),
        box("partitionGlass", "glass-light", [0.02, 0.5, zl - 0.38], [4.85, 1.51, -(zl + 0.38) / 2]),
        box("printer", "plastic-grey", [0.16, 0.1, 0.18], [5.2, 1.05, -0.3]),
        box("validator", "#e8b420", [0.08, 0.2, 0.12], [[4.3, 1.35, 0.85], [0.63, 1.35, 0.85], [-3.9, 1.35, 0.85]]),
        # (THE DOORS: jambs, the folding leaves standing open)
        *jambs("jamb", D, hw + 0.005, 0.28, ws1 + 0.03),
        *[p for i, (a, b) in enumerate(D) for p in folding_door(f"door{i}", a, b, zl - 0.03, fl + 0.01, ws1 - fl - 0.04)],
        # (OUTSIDE: the flush window band, the front (windscreen, destination display, lamps, bumper, wipers, mirrors),
        #  the rear (screen, engine grille, lamps), the roof's pods, the wheels in their arches)
        *bars("postL", "trim", "z", -(hw + 0.006), winL, ws0 - 0.02, ws1 + 0.02, over=0.02, gap=0.6), *bars("postR", "trim", "z", hw + 0.006, winR, ws0 - 0.02, ws1 + 0.02, over=0.02, gap=0.6),
        box("bandTop", "trim", [11.7, 0.2, 0.012], [0, 2.67, hw + 0.004], mirror="z"),
        box("windscreen", "glass", [0.04, 1.58, 2.4], [6.0, 1.95, 0]),
        box("destination", "screen", [0.04, 0.24, 1.9], [6.0, 2.87, 0]),
        box("destText", "lamp-amber", [0.01, 0.08, 1.3], [6.022, 2.87, 0]),
        use("head", W + "lamp", [6.0, 0.66, 0.92], {"shape": "square", "r": 0.17, "h": 0.1}, mirror="z"),
        box("indicator", "lamp-amber", [0.02, 0.06, 0.3], [6.0, 0.8, 0.92], mirror="z"),
        box("intake", "trim", [0.02, 0.18, 1.1], [6.0, 0.6, 0]),
        box("bumper", "trim", [0.12, 0.2, 2.5], [5.99, 0.38, 0]),
        box("plateF", "plastic-white", [0.01, 0.11, 0.52], [6.055, 0.4, 0]),
        box("wiper", "trim", [0.02, 0.9, 0.03], [[6.03, 1.6, -0.5, 0, 0, 0], [6.03, 1.6, 0.6, 0, 0, 0]]),
        use("mirror", W + "wing-mirror", [5.92, 2.85, 1.13], {"ax": 0.42, "ay": -0.35, "az": 0.22, "w": 0.24, "h": 0.42, "d": 0.1, "out": 0, "hang": 1, "armR": 0.025}, mirror="z"),
        box("rearScreen", "glass", [0.04, 0.8, 2.1], [-6.0, 2.3, 0]),
        box("engineGrille", "trim", [0.03, 0.8, 1.7], [-6.0, 1.0, 0]),
        box("tailLamp", "lamp-red", [0.03, 0.55, 0.2], [-6.0, 1.05, 1.02], mirror="z"),
        box("tailInd", "lamp-amber", [0.03, 0.14, 0.2], [-6.0, 1.42, 1.02], mirror="z"),
        box("bumperR", "trim", [0.1, 0.2, 2.5], [-5.98, 0.38, 0]),
        box("plateR", "plastic-white", [0.01, 0.11, 0.52], [-6.035, 0.52, 0]),
        loft("acPod", "roofbox", [[1.0, 0.95, 3.0, 3.24], [3.8, 0.95, 3.0, 3.24]], 0.1, seg=1),
        loft("enginePod", "roofbox", [[-5.85, 1.0, 3.0, 3.2], [-4.4, 1.0, 3.0, 3.2]], 0.08, seg=1),
        *arches([xf, xr], r, hw + 0.006, 2.2, inner=0.4, lip=0.1, gap=0.05, skin=lambda x, y: loft_z(shell, [0.1, 0.3], x, y),
                low=lambda x: cr_at(shell, x)[1], floor=lambda x: cr_at(shell, x)[1] + 0.004, deep=0.07),
        *wheels([xf, xr], 2.2, r, 0.28, spokes=0, rim=0.6, lock=35),
        use("twin", W + "wheel", [xr, r, 0.8], {"r": r, "w": 0.28, "spokes": 0, "rim": 0.6}, mirror="z"),
    ]
    return item("City bus", "vehicle", "a 12 m low-floor city bus (12.0 x 2.55 x 3.1 m, wheelbase 5.9 m, the floor 34 cm up): the lofted shell and its light lining with open windows and three double doors cut through, their folding leaves hinged (open: each pair jack-knifes into the bus); inside the floor, the wheel housings with seats on podiums, 35 seats, the wheelchair bay, yellow stanchions and ceiling rails with stop buttons, light strips, the driver's cab (seat, steering wheel, dashboard, partition); the rear platform over the engine; outside the flush window band, windscreen and destination display, rabbit-ear mirrors, twin rear wheels in their arches -- its livery drawn by the seed",
        {"paint": {"pick": ["paint-white", "paint-yellow", "paint-red", "paint-cream", "paint-blue", "paint-green"]}, "lining": "#d3d5cf", "floor": "#4a5057",
         "moquette": {"pick": ["#2c4778", "#7a2632", "#35603f", "#4a3a6a"]}, "seatShell": "plastic-grey", "pole": "paint-yellow", "trim": "plastic-black",
         "glass": "glass", "well": "#141416", "under": CAR_MATS["under"], "roofbox": "plastic-white"}, merge(parts), params={"open": 0, "steer": 0},
        markers=[{"role": "seat", "at": [5.0, 1.0, -0.76], "data": {"face": 0, "driver": 1}}] +
                [{"role": "door", "at": [(a + b) / 2, 0.36, hw], "data": {"face": 90}} for a, b in D])


def motorcycle():
    # A MOTORCYCLE (a standard road bike, the naked 600-900 cc class: 2.1 m long, wheelbase 1.42 m, the seat 0.82 m up):
    # cast wheels (two front discs, one rear), telescopic forks raked 22 degrees, twin-spar frame, an inline four leaning
    # forward with its radiator, four headers sweeping under the crankcase to a muffler on the right, the swingarm and
    # its shock, the chain, the tank, the seat and tail, a round headlamp, the bars with mirrors and levers
    FA, RA, rf, rr = 0.71, -0.71, 0.3, 0.31
    parts = [
        use("rear", W + "cast-wheel", [RA, rr, 0], {"r": rr, "t": 0.07, "wd": 0.18, "discs": 1, "discR": 0.11}),
        # (THE FRONT END, steered (the `steer` param, 30 degrees at full lock) about the head's axis through the yokes,
        #  raked 21 degrees: the wheel, the forks, the yokes, bars, lamp, clocks, mudguard and mirrors)
        hinge("steer", [0.43, 1.0, 0], [
            use("front", W + "cast-wheel", [FA, rf, 0], {"r": rf, "t": 0.055, "wd": 0.12, "discs": 2, "discR": 0.15}),
            rod("stanchion", "chrome", 0.021, [0.43, 1.0, 0.1], [0.575, 0.64, 0.1], 10, mirror="z"),
            rod("forkLeg", "fork", 0.031, [0.56, 0.68, 0.1], [FA, rf, 0.1], 10, mirror="z"),
            box("yokeT", "alu", [0.09, 0.03, 0.27], [0.43, 1.0, 0, 0, 0, -22]),
            box("yokeB", "alu", [0.09, 0.04, 0.27], [0.48, 0.87, 0, 0, 0, -22]),
            sweep("bar", "chrome", [[0.36, 1.1, -0.37], [0.4, 1.07, -0.18], [0.42, 1.06, 0], [0.4, 1.07, 0.18], [0.36, 1.1, 0.37]], 0.011),
            rod("grip", "trim", 0.017, [0.37, 1.095, 0.27], [0.355, 1.105, 0.38], 8, mirror="z"),
            box("lever", "alu", [0.17, 0.012, 0.02], [0.43, 1.1, 0.3, 15, 0, 0], mirror="z"),
            box("clocks", "trim", [0.05, 0.1, 0.18], [0.47, 1.1, 0, 0, 0, -30]),
            box("clockFace", "screen", [0.005, 0.08, 0.15], [0.445, 1.11, 0, 0, 0, -30]),
            sphere("lampShell", "trim", 0.1, [0.56, 0.93, 0], stretch=[0.9, 1, 1], sides=12),
            use("head", W + "lamp", [0.64, 0.93, 0], {"r": 0.085}),
            box("indF", "lamp-amber", [0.05, 0.03, 0.03], [0.57, 0.93, 0.17], mirror="z"),
            sweep("guardF", "paint", [[p[0], p[1], 0] for p in arc(FA, rf, rf + 0.05, 140, 25, 8)], None, section=[0.14, 0.006], up=[0, 1, 0]),
            use("mirror", W + "wing-mirror", [0.37, 1.1, 0.28], {"ax": -0.03, "ay": 0.13, "az": 0.1, "w": 0.12, "h": 0.07, "d": 0.035, "out": 1, "armR": 0.007}, mirror="z"),
        ], axis=(-0.359, 0.933, 0), max_=30, by="steer"),
        # (the frame, the tank, the seat and the tail)
        # (the spars meet at the head tube, the steering's axis, between the forks; the yokes turn about it)
        rod("headTube", "alu", 0.032, [0.415, 1.04, 0], [0.49, 0.845, 0], 10),
        sweep("spar", "alu", [[0.44, 0.94, 0.02], [0.34, 0.92, 0.035], [0.24, 0.87, 0.15], [0.02, 0.76, 0.15], [-0.1, 0.62, 0.14], [-0.1, 0.4, 0.13]], 0.027, mirror="z"),
        loft("tank", "paint", [[-0.08, 0.1, 0.83, 0.98, 0.08], [0.04, 0.16, 0.8, 1.07, 0.12], [0.25, 0.17, 0.8, 1.1, 0.13], [0.33, 0.09, 0.88, 1.01, 0.06]], [0.05, 0.08], seg=4),   # (its nose clear of the yokes at full lock)
        loft("seat", "seat", [[-0.6, 0.09, 0.89, 0.99, 0.07], [-0.4, 0.14, 0.85, 0.93, 0.12], [-0.06, 0.12, 0.85, 0.93, 0.1]], 0.035, seg=3),
        loft("tail", "paint", [[-0.87, 0.06, 0.93, 0.99, 0.05], [-0.42, 0.12, 0.77, 0.89, 0.1]], 0.03, seg=3),
        box("sidePanel", "paint", [0.36, 0.17, 0.26], [-0.28, 0.76, 0]),
        box("tailLamp", "lamp-red", [0.02, 0.04, 0.08], [-0.875, 0.96, 0]),
        box("indR", "lamp-amber", [0.05, 0.03, 0.03], [-0.8, 0.9, 0.1], mirror="z"),
        rod("hugger", "trim", 0.012, [-0.75, 0.9, 0], [-0.85, 0.72, 0], 6),
        box("plate", "plateW", [0.01, 0.13, 0.19], [-0.86, 0.68, 0, 0, 0, -15]),
        # (the engine: crankcase, the cylinder block leaning forward, the head, the radiator, the clutch cover, headers
        #  and muffler)
        box("crankcase", "engine", [0.46, 0.25, 0.34], [0.02, 0.43, 0]),
        box("block", "engine", [0.2, 0.28, 0.36], [0.21, 0.66, 0, 0, 0, -25]),
        box("fins", "engine", [0.22, 0.012, 0.38], [0, 0, 0, 0, 0, -25], along={"n": 4, "from": [0.17, 0.58, 0], "to": [0.23, 0.72, 0]}),
        box("cylHead", "engineDark", [0.19, 0.09, 0.38], [0.27, 0.81, 0, 0, 0, -25]),
        box("radiator", "trim", [0.04, 0.28, 0.36], [0.37, 0.64, 0, 0, 0, -12]),   # (back clear of the forks at full lock)
        lathe("clutch", "engine", [[0, 0.04], [0.09, 0.04], [0.1, 0], [0.1, -0.02]], [-0.02, 0.44, 0.17, 0, -90, 0], sides=14),
        # (the headers bend down 4-6 cm behind the front tyre: they had touched it, and it sweeps past them steered)
        *[sweep(f"header{i}", "exhaust", [[0.33, 0.73, z], [0.4, 0.58, z * 1.1], [0.34, 0.3, z * 0.8], [0.15, 0.2, 0.04]], 0.017) for i, z in enumerate([-0.13, -0.05, 0.05, 0.13])],
        rod("collector", "exhaust", 0.035, [0.15, 0.2, 0.04], [-0.2, 0.3, 0.17], 10),
        rod("muffler", "chrome", 0.06, [-0.22, 0.34, 0.2], [-0.62, 0.56, 0.2], 12, r0=0.055, r1=0.07),
        # (the swingarm, its shock, the chain, the pegs, the stand)
        rod("swingarm", "alu", 0.028, [-0.1, 0.42, 0.13], [RA, rr, 0.12], 8, mirror="z"),
        rod("shock", "steel", 0.018, [-0.13, 0.8, 0], [-0.32, 0.46, 0], 8),
        rod("spring", "spring", 0.035, [-0.17, 0.72, 0], [-0.28, 0.53, 0], 10),
        ring("sprocketF", "steel", 0.045, 0.007, [-0.02, 0.38, 0.16, 0, 90, 0]),
        ring("sprocketR", "steel", 0.1, 0.007, [RA, rr, 0.155, 0, 90, 0]),
        sweep("chain", "steel", [[-0.02, 0.425, 0.16], [RA, rr + 0.1, 0.155], [RA - 0.1, rr, 0.155], [RA, rr - 0.1, 0.155], [-0.02, 0.335, 0.16], [0.025, 0.38, 0.16]], 0.006, closed=True),
        rod("peg", "alu", 0.014, [-0.1, 0.36, 0.12], [-0.1, 0.36, 0.24], 6, mirror="z"),
        rod("pegR", "alu", 0.012, [-0.4, 0.5, 0.12], [-0.4, 0.5, 0.22], 6, mirror="z"),
        rod("stand", "steel", 0.012, [-0.05, 0.33, -0.15], [-0.32, 0.3, -0.17], 6),
    ]
    return item("Motorcycle", "vehicle", "a standard road motorcycle (a naked 600-900 cc, 2.1 m long, wheelbase 1.42 m, seat 0.82 m): cast wheels with brake discs, telescopic forks, twin-spar frame, an inline four leaning forward with its radiator, four headers to a muffler on the right, swingarm and shock, chain, tank, seat and tail, a round headlamp, bars with mirrors -- its paint drawn by the seed",
        {"paint": {"pick": ["paint-red", "paint-black", "paint-blue", "paint-orange", "paint-white", "paint-green"]}, "chrome": "chrome", "fork": "gunmetal", "alu": "aluminium",
         "trim": "plastic-black", "seat": "leather-dark", "engine": "#6c6f74", "engineDark": "gunmetal", "exhaust": "steel", "steel": "steel", "spring": "#c43a1a", "plateW": "plastic-white", "screen": "screen"},
        parts, params={"steer": 0}, markers=[{"role": "seat", "at": [-0.25, 0.93, 0], "data": {"face": 0}}])


def lorry():
    # A BOX LORRY (a two-axle rigid, 12-18 t: 8.6 x 2.55 x 3.95 m, wheelbase 4.75 m): the forward-control cab over the
    # front axle (its windscreen, grille, bumper, steps, doors with their windows, sun visor, roof deflector, big
    # mirrors), the ladder frame, the insulated box with its rear doors, hinges and locking bars, the fuel tank, the
    # battery box, side guards and the rear under-run bar; six wheels -- single at the front, twin at the back
    xf, xr, r = 3.25, -1.5, 0.5
    cab = [[2.15, 1.2, 0.72, 3.0, 1.1], [4.1, 1.22, 0.72, 3.0, 1.12], [4.3, 1.17, 0.76, 2.92, 1.06]]
    CR = [0.06, 0.16]
    zc = lambda x, y: loft_z(cab, CR, x, y)
    CAB = loft("cab", "paint", cab, CR, seg=3, arches=body_arches([xf], r, 0.08), double=True, caps=[True, False], bare=["bottom"])   # (its front: panels;
    uC = lambda x: cr_at(cab, x)[1] + 0.004                                                                                              #  under it, the pan)
    dX, dY, wX, wY = (2.62, 3.7), (1.12, 2.82), (2.72, 3.6), (2.02, 2.74)   # (the doors' stretch; their windows')
    def leaf(s):
        """a rear door of the box: hinged at its corner, swinging round flat against the side (270 degrees)"""
        z0 = 1.285
        return hinge("rearDoor", [-4.3, 1.2, z0], [
            box("panel", "boxPaint", [0.04, 2.72, 1.27], [-4.32, 2.56, z0 / 2 + 0.005]),
            box("hinge", "alu", [0.04, 0.08, 0.1], [-4.34, 0, 1.2], along={"n": 4, "from": [0, 1.45, 0], "to": [0, 3.65, 0]}),
            rod("lockBar", "chrome", 0.018, [-4.35, 1.22, 0], [-4.35, 3.88, 0], 6, at=[[0, 0, 0.3], [0, 0, 0.9]]),
            box("lockHandle", "chrome", [0.03, 0.03, 0.2], [[-4.37, 1.7, 0.2], [-4.37, 1.7, 0.8]]),
        ], max_=265, mirror="z")
    parts = [
        cut(CAB, [region(*dX, *dY, "both"), region(3.73, 4.07, 2.2, 2.7, "both")]),
        # (its front, the loft's cap left off: panels round the windscreen -- a loft's holes cut its sides, not its caps)
        box("front", "paint", [0.03, 1.25, 2.26], [4.285, 1.375, 0]),
        box("frontTop", "paint", [0.03, 0.13, 2.1], [4.285, 2.87, 0]),
        box("frontPost", "paint", [0.03, 0.84, 0.1], [4.285, 2.41, 1.08], mirror="z"),
        box("windscreen", "glazing", [0.02, 0.82, 2.06], [4.3, 2.4, 0]),
        box("quarterWin", "glazing", [0.35, 0.5, 0.01], [3.9, 2.45, zc(3.9, 2.45) - 0.01], mirror="z"),
        # (THE CAB'S DOORS: hinged at their front edge, the window in a hole of the skin)
        hinge("cabDoor", [dX[1], 1.9, zc(dX[1], 1.9) - 0.01], [
            piece(CAB, [region(*dX, *dY)], "skin", holes=[region(*wX, *wY)]),
            box("pane", "glazing", [wX[1] - wX[0] + 0.02, wY[1] - wY[0] + 0.02, 0.01], [(wX[0] + wX[1]) / 2, (wY[0] + wY[1]) / 2, zc(3.15, 2.38) - 0.02]),
            box("handle", "chrome", [0.18, 0.03, 0.03], [2.8, 1.85, zc(2.8, 1.85) + 0.01]),
            use("card", W + "door-card", [3.16, 1.5, zc(3.16, 1.5) - 0.05], {"w": 1.0, "h": 0.62}),
        ], max_=70, mirror="z"),
        box("visor", "paint", [0.28, 0.04, 2.25], [4.4, 2.88, 0, 0, 0, -8]),
        box("grille", "trim", [0.03, 0.62, 1.7], [4.305, 1.55, 0]),
        box("grilleBar", "chrome", [0.035, 0.03, 1.6], [4.31, 1.55, 0], along={"n": 4, "from": [0, -0.22, 0], "to": [0, 0.22, 0]}),
        use("head", W + "lamp", [4.31, 1.0, 0.85], {"shape": "square", "r": 0.18, "h": 0.12}, mirror="z"),
        box("ind", "lamp-amber", [0.03, 0.08, 0.12], [4.31, 1.0, 1.1], mirror="z"),
        box("bumper", "bumper", [0.26, 0.34, 2.45], [4.2, 0.62, 0]),
        box("plateF", "plastic-white", [0.01, 0.11, 0.52], [4.335, 0.62, 0]),
        rod("grab", "chrome", 0.015, [2.58, 1.2, 1.24], [2.58, 2.3, 1.24], 6, mirror="z"),
        box("step", "bumper", [0.42, 0.04, 0.26], [[2.45, 0.55, 1.08], [2.45, 0.9, 1.08]], mirror="z"),
        loft("deflector", "paint", [[2.25, 1.05, 2.98, 3.85, 0.95], [3.95, 1.0, 2.98, 3.05, 0.95]], [0.02, 0.1], seg=3),
        use("mirror", W + "wing-mirror", [4.15, 2.65, 1.12], {"ax": 0.15, "ay": 0.1, "az": 0.25, "w": 0.22, "h": 0.45, "d": 0.1, "out": 0, "hang": 1, "armR": 0.02}, mirror="z"),
        # (INSIDE THE CAB: the floor over the engine's hump, the dash, two seats, the sleeper's bunk behind)
        box("cabFloor", "rubberMat", [2.05, 0.04, 2.2], [3.2, 1.12, 0]),
        box("hump", "rubberMat", [1.3, 0.34, 0.7], [3.55, 1.3, 0]),
        use("dash", W + "car-dash", [4.0, 1.86, 0], {"w": 2.2, "d": 0.4, "h": 0.5, "sz": 0.55}),
        use("seat", W + "car-seat", [3.35, 1.14, 0.6], {"h": 0.42, "back": 0.62, "heads": 0.2}, mirror="z"),
        box("bunk", "moquette", [0.62, 0.14, 2.2], [2.5, 1.56, 0]),
        box("bunkBase", "under", [0.62, 0.4, 2.2], [2.5, 1.3, 0]),
        box("curtain", "moquette", [0.02, 1.1, 2.1], [2.86, 2.3, 0]),
        # (the frame and the box)
        box("rail", "frame", [8.3, 0.26, 0.08], [-0.1, 0.92, 0.42], mirror="z"),
        box("cross", "frame", [0.1, 0.2, 0.84], [0, 0.92, 0], along={"n": 6, "from": [-4.1, 0, 0], "to": [2.0, 0, 0]}),
        loft("box", "boxPaint", [[-4.3, 1.275, 1.15, 3.95], [2.05, 1.275, 1.15, 3.95]], 0.03, seg=1, caps=[False, True], double=True),
        leaf(1),
        rod("edge", "alu", 0.025, [-4.3, 3.93, 1.255], [2.05, 3.93, 1.255], 6, mirror="z"),
        rod("edgeLo", "alu", 0.03, [-4.3, 1.18, 1.26], [2.05, 1.18, 1.26], 6, mirror="z"),
        rod("post", "alu", 0.03, [0, 1.15, 1.255], [0, 3.95, 1.255], 6, at=[[-4.29, 0, 0], [2.04, 0, 0]], mirror="z"),
        box("tail", "lamp-red", [0.05, 0.12, 0.28], [-4.22, 0.92, 1.0], mirror="z"),
        box("tailInd", "lamp-amber", [0.05, 0.12, 0.1], [-4.22, 0.92, 0.78], mirror="z"),
        box("underrun", "bumper", [0.1, 0.12, 2.25], [-4.15, 0.5, 0]),
        rod("underrunArm", "frame", 0.03, [-4.15, 0.5, 0.42], [-4.0, 0.85, 0.42], 6, mirror="z"),
        box("plateR", "plastic-white", [0.01, 0.11, 0.52], [-4.21, 0.68, 0]),
        # (between the axles: the fuel tank on the right, the battery box on the left, the side guards)
        rod("tank", "alu", 0.27, [0.6, 0.78, 0.92], [1.95, 0.78, 0.92], 16),
        box("strap", "frame", [0.05, 0.56, 0.6], [[0.9, 0.78, 0.92], [1.65, 0.78, 0.92]]),
        box("battery", "frame", [0.6, 0.45, 0.5], [1.0, 0.8, -0.98]),
        box("guard", "alu", [1.3, 0.1, 0.03], [[-0.2, 0.48, 1.24], [-0.2, 0.8, 1.24]], mirror="z"),
        box("mudguard", "trim", [1.35, 0.02, 0.62], [xr, 2 * r + 0.1, 0.95], mirror="z"),
        box("mudflap", "trim", [0.01, 0.5, 0.6], [xr - 0.68, 0.55, 0.95], mirror="z"),
        *pan("pan", "under", cab, CR, 2.15, 4.3, [arch_gap(xf, r, uC(xf))], 0.55),
        *arches([xf], r, zc(xf, 1.0) + 0.005, 2.1, inner=0.55, lip=0.12, gap=0.05, skin=zc, low=lambda x: cr_at(cab, x)[1], floor=uC, notch=r + 0.08),
        box("subframe", "frame", [6.3, 0.1, 0.1], [-1.125, 1.1, 0.42], mirror="z"),   # (the box's runners on the rails)
        *wheels([xf], 2.1, r, 0.3, spokes=0, rim=0.58, lock=35),
        *wheels([xr], 2.22, r, 0.3, spokes=0, rim=0.58, name="rearO"),
        *wheels([xr], 1.58, r, 0.3, spokes=0, rim=0.58, name="rearI"),
    ]
    return item("Box lorry", "vehicle", "a two-axle rigid box lorry (12-18 t, 8.6 x 2.55 x 3.95 m, wheelbase 4.75 m): the forward-control cab over the front axle (its doors hinged, see-through windows; inside the dash, two seats, the sleeper's bunk) with grille, steps, visor, roof deflector and big mirrors; the ladder frame; the box with its rear doors swinging round to the sides (open), hinges and locking bars; fuel tank, battery box, side guards, rear under-run bar; single front and twin rear wheels -- its cab's paint drawn by the seed",
        {"paint": {"pick": ["paint-white", "paint-red", "paint-blue", "paint-orange", "paint-green", "paint-silver"]}, "boxPaint": "plastic-white", "glass": "glass", "trim": "plastic-black",
         "chrome": "chrome", "bumper": "plastic-grey", "frame": "paint-black", "alu": "aluminium", "well": "#141416", **{k: CAR_MATS[k] for k in ("glazing", "trim", "under")}, "rubberMat": "#2b2d30", "moquette": "#3a3f4a"}, parts,
        params={"open": 0, "steer": 0}, markers=[{"role": "seat", "at": [3.35, 1.6, -0.6], "data": {"face": 0, "driver": 1}}])


def van():
    # A DELIVERY VAN (a high-roof panel van, the Sprinter's class: 5.93 x 2.02 x 2.65 m, wheelbase 3.67 m): a short
    # bonnet, the windscreen raked well back, the cab's glasshouse, the tall cargo box behind it -- built as the car is,
    # its lofts shells: the cab's doors hinged (cut from the lower body and the glass, L-shaped round the front arch),
    # the side door SLIDING back on its rail, the twin rear doors hinged at the corners; inside the cab (dash, the
    # driver's seat and a two-seat bench), the bay (a plywood lining, its floor, the wheel boxes)
    xf, xr, r, tr = 1.97, -1.69, 0.35, 1.72
    lower = [[0.7, 1.0, 0.36, 1.24, 0.97], [1.6, 1.0, 0.37, 1.22, 0.96], [2.5, 0.97, 0.4, 1.12, 0.9], [2.965, 0.86, 0.45, 1.0, 0.76]]
    cargo = [[-2.965, 0.98, 0.42, 2.62, 0.92], [-2.9, 1.0, 0.36, 2.65, 0.94], [0.74, 1.0, 0.36, 2.65, 0.94]]
    glass = [[0.7, 0.985, 1.15, 2.22, 0.925], [1.0, 0.985, 1.15, 2.2, 0.925], [1.4, 0.98, 1.15, 1.8, 0.92], [1.88, 0.965, 1.15, 1.24, 0.9]]
    hood = [[0.7, 1.0, 2.1, 2.65, 0.94], [0.95, 0.99, 2.1, 2.6, 0.93], [1.12, 0.96, 2.14, 2.34, 0.88]]   # (the high roof's front over the cab)
    LR, CR, GR = [0.1, 0.1], [0.1, 0.12], [0.02, 0.12]
    zl = lambda x, y: loft_z(lower, LR, x, y)
    zk = lambda x, y: loft_z(cargo, CR, x, y)
    zin = tr / 2 - 0.225 / 2 - 0.07                      # (the wheel tubs' inner walls; the front's clear of the
    zinF = steer_in(tr, r, 0.225)                         #  steered tyre at full lock)
    uF, uR = (lambda x: cr_at(lower, x)[1] + 0.004), (lambda x: cr_at(cargo, x)[1] + 0.004)   # (the pans' undersides)
    cabD = [(0.76, 1.52, 0.45), (1.52, 1.78, 0.78)]      # (the cab door's skin: below, clear of the arch; above, up to the A-pillar)
    sD, fl, bay = (-0.65, 0.6, 0.45, 2.45), 0.6, 0.55   # (the sliding door's stretch; the cab's floor, the bay's)
    LOWER = loft("lower", "paint", lower, LR, seg=4, arches=body_arches([xf], r), bare=["bottom"], double=True)   # (the lofts, once:
    CARGO = loft("cargo", "paint", cargo, CR, seg=1, arches=body_arches([xr], r), bare=["bottom"], double=True, caps=[False, False])   # the
    GLASS = loft("glass", "glazing", glass, GR, seg=4, bare=["bottom"])                                           #  doors are cut from them)
    def rear_leaf():
        # (the right rear leaf, hinged at the corner; its window in a frame -- mirrored for the left)
        x, z0, z1 = -2.985, 0.95, 0.01
        w, zc = z0 - z1, (z0 + z1) / 2
        return hinge("rearDoor", [x, 1.5, z0], [
            box("panel", "paint", [0.04, 1.1, w], [x, 1.0, zc]),
            box("railTop", "paint", [0.04, 0.24, w], [x, 2.43, zc]),
            box("stileO", "paint", [0.04, 0.9, 0.12], [x, 2.0, z0 - 0.06]),
            box("stileI", "paint", [0.04, 0.9, 0.08], [x, 2.0, z1 + 0.04]),
            box("pane", "glazing", [0.015, 0.9, w - 0.2], [x, 2.0, zc - 0.01]),
            box("handle", "trim", [0.03, 0.03, 0.16], [x - 0.03, 1.25, z1 + 0.14]),
            box("lamp", "lamp-red", [0.04, 0.5, 0.1], [x + 0.005, 1.05, z0 - 0.06]),
        ], max_=100, mirror="z")
    parts = [
        cut(LOWER, [region(*q, 9, "both") for q in cabD] + [region(0.72, 1.86, 1.1, 9, "both", all=True, z=[0, 0.95])]),
        cut(CARGO, [region(sD[0], sD[1], sD[2], sD[3], "right")]),
        loft("lining", "ply", shell_over(cargo, [-2.94, -2.0, -1.0, 0.0, 0.72], -0.035), CR, seg=1, arches=body_arches([xr], r + 0.03),
             holes=[region(sD[0] - 0.02, sD[1] + 0.02, sD[2], sD[3] + 0.02, "right")], bare=["bottom"], caps=False, double=True),
        cut(GLASS, [region(0.78, 1.78, 1.15, 2.08, "both")]),
        loft("hood", "paint", hood, [0.08, 0.12], seg=2),
        a_pillar("aPillar", "paint", glass, 1.12, 1.87),
        box("bPillar", "paint", [0.06, 1.0, 0.04], [0.74, 1.7, loft_z(glass, GR, 0.74, 1.7) - 0.01], mirror="z"),
        # (THE CAB'S DOORS: hinged at the A-pillar)
        hinge("cabDoor", [1.78, 1.0, zl(1.78, 1.0) - 0.01], [
            piece(LOWER, [region(a, b, y) for a, b, y in cabD], "skin"),
            piece(GLASS, [region(0.78, 1.78, 1.15, 2.08)], "pane"),
            sweep("waist", "trim", [[0.79, 1.22, zl(0.79, 1.22) + 0.004], [1.76, 1.22, zl(1.76, 1.22) + 0.004]], 0.01),
            box("handle", "trim", [0.16, 0.03, 0.025], [1.5, 1.08, zl(1.5, 1.08) + 0.008]),
            use("card", W + "door-card", [1.2, 0.92, zl(1.2, 0.92) - 0.05], {"w": 0.86, "h": 0.5}),
            use("mirror", W + "wing-mirror", [1.8, 1.3, 0.96], {"ax": 0.05, "ay": 0.08, "az": 0.2, "w": 0.2, "h": 0.32, "d": 0.09, "out": 0, "hang": 0.4}),
        ], max_=65, mirror="z"),
        # (THE SLIDING DOOR on the right: out a little and back along its rail)
        plug_slide("sideDoor", [-1.32, 0, 0.07], [
            piece(CARGO, [region(*sD)], "skin"),
            box("handle", "trim", [0.16, 0.03, 0.025], [0.45, 1.15, zk(0.45, 1.15) + 0.008]),
            box("inner", "ply", [sD[1] - sD[0] - 0.1, sD[3] - sD[2] - 0.2, 0.012], [(sD[0] + sD[1]) / 2, (sD[2] + sD[3]) / 2, zk(0, 1.4) - 0.045]),
        ]),
        rod("slideRail", "trim", 0.018, [-0.65, 1.55, zk(-1, 1.55) + 0.01], [-2.6, 1.55, zk(-1, 1.55) + 0.01], 6),
        rear_leaf(),
        box("brakeHi", "lamp-red", [0.03, 0.05, 0.4], [-2.96, 2.57, 0]),
        box("bumperR", "trim", [0.14, 0.22, 1.98], [-2.92, 0.47, 0]),
        box("plateR", "plastic-white", [0.01, 0.11, 0.52], [-2.995, 0.6, 0]),
        # (the nose)
        use("head", W + "lamp", [2.985, 0.88, 0.5], {"shape": "square", "r": 0.17, "h": 0.12, }, mirror="z"),
        box("grille", "trim", [0.03, 0.26, 0.6], [2.975, 0.76, 0]),
        box("bumper", "trim", [0.16, 0.26, 2.0], [2.93, 0.5, 0]),
        box("plateF", "plastic-white", [0.01, 0.11, 0.52], [3.015, 0.5, 0]),
        box("wiper", "trim", [0.5, 0.012, 0.02], [[1.72, 1.29, -0.25, 6, 0, 10], [1.72, 1.29, 0.3, 6, 0, 10]]),
        box("stepR", "trim", [0.9, 0.05, 0.2], [0.2, 0.3, 0.93]),
        # (INSIDE THE CAB: its floor, the engine's hump, the dash, the driver's seat, the two-seat bench)
        # (the floor between the front tubs, and outboard only behind them; the firewall between them -- both had run
        #  across through the front tyres)
        box("cabFloor", "rubberMat", [1.16, 0.04, 2 * zinF], [1.32, fl - 0.02, 0]),
        box("cabFloorS", "rubberMat", [round(xf - r - 0.06 - 0.74, 3), 0.04, round(0.95 - zinF, 3)], [round((xf - r - 0.06 + 0.74) / 2, 3), fl - 0.02, round((0.95 + zinF) / 2, 3)], mirror="z"),
        box("firewall", "under", [0.03, 0.6, 2 * zinF], [1.9, fl + 0.3, 0]),
        use("dash", W + "car-dash", [1.62, 1.24, 0], {"w": 1.92, "d": 0.26, "h": 0.5, "sz": 0.5}),
        use("seatD", W + "car-seat", [1.18, fl, -0.5], {"h": 0.34, "back": 0.52}),
        use("bench", W + "car-seat", [1.18, fl, 0.42], {"w": 0.86, "bolster": 0, "h": 0.34, "back": 0.52, "heads": 0.44, "hw": 0.22}),
        # (THE BULKHEAD behind the cab: steel, a window in its top)
        box("bulkhead", "under", [0.03, 0.95, 1.94], [0.72, bay + 0.475, 0]),
        box("bulkTop", "under", [0.03, 0.55, 1.9], [0.72, 2.3, 0]),
        box("bulkSide", "under", [0.03, 0.53, 0.55], [0.72, 1.765, 0.7], mirror="z"),
        box("bulkPane", "glazing", [0.01, 0.53, 0.85], [0.72, 1.765, 0]),
        # (THE BAY: its plywood floor, the wheel boxes, the tie-down rails)
        # (the bay's floor: between the wheel boxes, and outboard of them only fore and aft -- one board across had run
        #  through the tubs, a ply band over each rear tyre)
        box("bayFloor", "ply", [3.66, 0.03, 2 * zin - 0.024], [-1.12, bay, 0]),
        box("bayFloorA", "ply", [round(xr - r - 0.07 + 2.95, 3), 0.03, round(0.96 - zin + 0.012, 3)], [round((xr - r - 0.07 - 2.95) / 2, 3), bay, round((0.96 + zin - 0.012) / 2, 3)], mirror="z"),
        box("bayFloorB", "ply", [round(0.71 - (xr + r + 0.07), 3), 0.03, round(0.96 - zin + 0.012, 3)], [round((0.71 + xr + r + 0.07) / 2, 3), bay, round((0.96 + zin - 0.012) / 2, 3)], mirror="z"),
        # (the wheel box over each rear tub: a ply hood just outside it, above the bay's floor, its inner end a disc --
        #  it had been a solid box standing down into the tub, its bottom seen from under the arch)
        lathe("wheelBox", "ply", [[0, zin - 0.012], [r + 0.065, zin - 0.012], [r + 0.065, zk(xr, 1.0) - 0.035]], [xr, r, 0, 0, 90, 0], caps=False, double=True, sides=20, mirror="z",
              arc=[round(math.degrees(math.asin((bay - r) / (r + 0.065))) - 180, 3), round(-math.degrees(math.asin((bay - r) / (r + 0.065))), 3)]),
        rod("tieRail", "aluminium", 0.012, [-2.9, 1.2, 0.9], [0.6, 1.2, 0.9], 6, mirror="z"),
        # (UNDER IT: the floor pans under the cab's and the box's open bottoms, round the wheels' tubs; the arches'
        #  liners laid on the skin)
        *pan("panF", "under", lower, LR, 0.74, 2.965, [arch_gap(xf, r, uF(xf))], [zinF]),
        *pan("panR", "under", cargo, CR, -2.965, 0.74, [arch_gap(xr, r, uR(xr))], zin),
        *arches([xf], r, zl(xf, r + 0.25) - 0.01, tr, inner=zinF, cup=True, skin=zl, low=lambda x: cr_at(lower, x)[1], floor=uF),
        *arches([xr], r, zk(xr, r + 0.25) - 0.01, tr, inner=zin, cup=True, skin=zk, low=lambda x: cr_at(cargo, x)[1], floor=uR, deep=0.07),
        *wheels([xf, xr], tr, r, 0.225, spokes=0, rim=0.6, lock=35),
    ]
    return item("Delivery van", "vehicle", "a high-roof panel van (5.93 x 2.02 x 2.65 m, wheelbase 3.67 m): a short bonnet, the raked windscreen and the cab's glasshouse, the tall cargo box; the cab's doors hinged, the side door sliding back on its rail, the twin rear doors swinging out (open: all of them); inside the cab's dash, seat and bench, the bay's plywood lining and floor; bumpers, big mirrors, four steel wheels in their arches -- its paint drawn by the seed",
        {"paint": {"pick": ["paint-white", "paint-white", "paint-silver", "paint-yellow", "paint-red", "paint-blue"]}, **CAR_MATS, "ply": "birch", "rubberMat": "#2b2d30"}, parts,
        params={"open": 0, "steer": 0}, markers=[{"role": "seat", "at": [1.18, 0.94, -0.5], "data": {"face": 0, "driver": 1}}])


def coach():
    # AN INTERCITY COACH (the 12 m two-axle high-decker, a Setra's or a Tourismo's class: 12.2 x 2.55 x 3.65 m,
    # wheelbase 6.0 m): the passengers' floor 1.3 m up over the LUGGAGE BAYS (their doors drawn along both sides
    # between the axles), two doors on the right -- the front one by the driver, the middle one ahead of the rear axle
    # -- each a stairwell of three steps up and a swing-out leaf standing open; inside 2+2 seats with headrests on a
    # 0.82 m pitch, five across the back, luggage racks with their light strips over both rows, the driver low in
    # front at his wheel. The same shell-and-lining build as the city bus, its windows open.
    hw, r, xf, xr, fl = 1.275, 0.5, 3.4, -2.6, 1.3
    ws0, ws1 = 1.78, 3.15
    zl = hw - 0.04
    D = [(4.95, 5.8), (-1.85, -0.95)]
    winL = fill(-5.6, 5.92, 1.7)
    winR = fill(-0.8, 4.8, 1.7) + fill(-5.6, -2.0, 1.7)
    holes = window_holes(winL, ws0, ws1, "left") + window_holes(winR, ws0, ws1, "right") + window_holes(D, 0.2, ws1, "right")
    shell = [[-6.1, 1.24, 0.38, 3.6, 1.15], [-6.0, hw, 0.32, 3.65, 1.18], [5.6, hw, 0.32, 3.63, 1.18], [6.1, 1.25, 0.36, 3.45, 1.12]]
    lining = [[-5.95, zl, 0.96, 3.5, zl - 0.07], [6.0, zl, 0.96, 3.5, zl - 0.07]]
    rows = [x for x in [4.3 - 0.82 * k for k in range(12)] if x > -4.95]
    rowsR = [x for x in rows if not (-2.15 < x < -0.65)]
    bays = [(-0.85, 0.45), (0.5, 1.75), (1.8, 2.75)]
    parts = [
        loft("shell", "paint", shell, [0.12, 0.35], seg=1, holes=holes, arches=body_arches([xf, xr], r), bare=["bottom"]),
        loft("lining", "lining", lining, [0.02, 0.2], seg=1, holes=holes, arches=body_arches([xf, xr], r), caps=[True, False], double=True, bare=["bottom"]),   # (notched: the tyres' tops had grazed it)
        # (UNDER IT: the floor pan, round the wheel housings -- the shell's bottom had run on under the wheels, and the
        #  lining's across their tops)
        *pan("pan", "under", shell, [0.12, 0.35], -6.1, 6.1, [arch_gap(x, r, cr_at(shell, x)[1] + 0.004) for x in (xf, xr)], 0.55),
        box("floor", "floor", [10.85, 0.06, 2 * zl], [-0.55, fl - 0.03, 0]),
        box("floorFront", "floor", [1.15, 0.06, 2 * zl], [5.475, 0.97, 0]),
        box("riser", "lining", [0.03, 0.33, 2 * zl], [4.9, 1.135, 0]),
        # (the stairwells: three steps up from the door to the floor, walled at both ends)
        *[p for i, (a, b) in enumerate(D) for p in (
            box(f"st{i}a", "floor", [b - a, 0.06, 0.32], [(a + b) / 2, 0.52, zl - 0.16]),
            box(f"st{i}b", "floor", [b - a, 0.06, 0.32], [(a + b) / 2, (0.52 + (fl if i else 0.97)) / 2, zl - 0.48]),
            box(f"st{i}w", "lining", [0.03, (fl if i else 0.97) - 0.3, 0.75], [[a, ((fl if i else 0.97) + 0.3) / 2, zl - 0.375], [b, ((fl if i else 0.97) + 0.3) / 2, zl - 0.375]]),
            box(f"st{i}r", "lining", [b - a, 0.25, 0.03], [(a + b) / 2, 0.37, zl - 0.0]),
            rod(f"st{i}h", "chrome", 0.018, [a + 0.06, 0.6, zl - 0.06], [a + 0.06, (fl if i else 0.97) + 0.9, zl - 0.06], 8))],
        # (the seats, the racks, the lights)
        *seat_pairs("sL", rows, -1, fl, 0.98, 0.55, headrest=1),
        *seat_pairs("sR", rowsR, 1, fl, 0.98, 0.55, headrest=1),
        *[bus_seat(f"back{i}", -5.55, z, fl, w=0.44, headrest=1) for i, z in enumerate([-0.96, -0.48, 0, 0.48, 0.96])],
        box("rack", "rack", [10.6, 0.04, 0.42], [-0.45, 3.22, zl - 0.25], mirror="z"),
        box("rackLip", "rack", [10.6, 0.1, 0.02], [-0.45, 3.24, zl - 0.46], mirror="z"),
        box("rackLight", "lamp", [10.4, 0.012, 0.08], [-0.45, 3.195, zl - 0.38], mirror="z"),
        box("aisleLight", "lamp", [9.5, 0.015, 0.12], [-0.6, 3.49, 0]),
        # (the driver)
        bus_seat("driver", 5.3, -0.7, 0.97, w=0.5, headrest=1),
        use("wheelD", W + "steering-wheel", [5.78, 1.62, -0.7, 0, 0, -45], {"R": 0.23, "col": 0.3}),
        box("dash", "trim", [0.3, 0.7, 2 * zl], [5.95, 1.32, 0]),
        use("dials", W + "screen", [5.8, 1.72, -0.7, 180, 0, -25], {"w": 0.4, "h": 0.14}),
        box("guideSeat", "moquette", [0.4, 0.1, 0.42], [5.4, 1.42, 0.7]),
        # (the doors: jambs, the leaves swung out and along the side, as a coach's swing-plug doors open)
        *jambs("jamb", D, hw + 0.005, 0.3, ws1 + 0.03),
        # (each a swing-plug leaf, shut in its opening; open, it SLIDES out off the side and along it, clear of the door)
        slide("leaf0", [-(D[0][1] - D[0][0]) - 0.02, 0, 0.12], [use("leaf", W + "door-leaf", [D[0][1], 0.35, hw, 180, 0, 0], {"w": D[0][1] - D[0][0], "h": ws1 - 0.4, "t": 0.04, "mid": 1.35})]),
        slide("leaf1", [(D[1][1] - D[1][0]) + 0.02, 0, 0.12], [use("leaf", W + "door-leaf", [D[1][0], 0.35, hw], {"w": D[1][1] - D[1][0], "h": ws1 - 0.4, "t": 0.04, "mid": 1.35})]),
        rod("leafArm", "chrome", 0.015, [D[0][0] - 0.1, 2.0, hw], [D[0][0] - 0.1, 2.0, hw + 0.12], 6, at=[[0, 0, 0], [-0.2 + (D[1][1] - D[0][0]) + 0.2, 0, 0]]),
        # (outside: the window band, the luggage bays, the front and rear, the roof, the wheels)
        *bars("postL", "trim", "z", -(hw + 0.006), winL, ws0 - 0.02, ws1 + 0.02, over=0.02, gap=0.6), *bars("postR", "trim", "z", hw + 0.006, winR, ws0 - 0.02, ws1 + 0.02, over=0.02, gap=0.6),
        box("bandTop", "trim", [11.8, 0.3, 0.012], [0, 3.32, hw + 0.003], mirror="z"),
        *[p for i, (a, b) in enumerate(bays) for p in (
            box(f"bayV{i}", "trim", [0.012, 1.0, 0.01], [[a, 0.95, hw + 0.004], [b, 0.95, hw + 0.004]], mirror="z"),
            box(f"bayH{i}", "trim", [b - a, 0.012, 0.01], [[(a + b) / 2, 0.45, hw + 0.004], [(a + b) / 2, 1.45, hw + 0.004]], mirror="z"),
            box(f"bayK{i}", "chrome", [0.16, 0.03, 0.02], [(a + b) / 2, 1.3, hw + 0.01], mirror="z"))],
        box("windscreen", "glass", [0.04, 1.85, 2.4], [6.1, 2.3, 0]),
        box("destination", "screen", [0.04, 0.2, 1.6], [6.09, 3.33, 0]),
        box("destText", "lamp-amber", [0.01, 0.07, 1.1], [6.112, 3.33, 0]),
        use("head", W + "lamp", [6.1, 0.72, 0.9], {"shape": "square", "r": 0.2, "h": 0.1}, mirror="z"),
        box("ind", "lamp-amber", [0.02, 0.06, 0.3], [6.1, 0.86, 0.9], mirror="z"),
        box("grille", "trim", [0.02, 0.32, 1.2], [6.1, 0.8, 0]),
        box("bumper", "trim", [0.12, 0.24, 2.5], [6.08, 0.42, 0]),
        box("plateF", "plastic-white", [0.01, 0.11, 0.52], [6.145, 0.45, 0]),
        box("wiper", "trim", [0.02, 0.9, 0.03], [[6.13, 1.85, -0.5], [6.13, 1.85, 0.6]]),
        use("mirror", W + "wing-mirror", [5.95, 3.3, 1.13], {"ax": 0.5, "ay": -0.45, "az": 0.2, "w": 0.24, "h": 0.42, "d": 0.1, "out": 0, "hang": 1, "armR": 0.025}, mirror="z"),
        box("engineGrille", "trim", [0.03, 0.9, 1.9], [-6.1, 1.2, 0]),
        box("tailLamp", "lamp-red", [0.03, 0.7, 0.18], [-6.1, 1.3, 1.02], mirror="z"),
        box("tailInd", "lamp-amber", [0.03, 0.16, 0.18], [-6.1, 1.76, 1.02], mirror="z"),
        box("rearPanel", "trim", [0.03, 0.9, 2.0], [-6.1, 2.75, 0]),
        box("bumperR", "trim", [0.1, 0.24, 2.5], [-6.08, 0.44, 0]),
        box("plateR", "plastic-white", [0.01, 0.11, 0.52], [-6.12, 0.62, 0]),
        loft("acPod", "roofbox", [[-3.5, 0.95, 3.6, 3.78], [3.5, 0.95, 3.6, 3.78]], 0.1, seg=1),
        *arches([xf, xr], r, hw + 0.006, 2.2, inner=0.55, lip=0.1, gap=0.05, skin=lambda x, y: loft_z(shell, [0.12, 0.35], x, y),
                low=lambda x: cr_at(shell, x)[1], floor=lambda x: cr_at(shell, x)[1] + 0.004),
        *wheels([xf, xr], 2.2, r, 0.3, spokes=6, rim=0.6, lock=35),
        use("twin", W + "wheel", [xr, r, 0.78], {"r": r, "w": 0.3, "spokes": 0, "rim": 0.6}, mirror="z"),
    ]
    return item("Coach", "vehicle", "a 12 m two-axle intercity coach (12.2 x 2.55 x 3.65 m, wheelbase 6.0 m, the floor 1.3 m up over the luggage bays): the shell and its lining with open windows, two doors with stairwells, their swing-plug leaves shut (open: out and along the side); inside 2+2 seats with headrests, five across the back, luggage racks with light strips, the driver's seat, wheel and dashboard; outside the window band, the luggage bays' doors, windscreen and destination display, rabbit-ear mirrors, the roof's air-conditioning pod -- its livery drawn by the seed",
        {"paint": {"pick": ["paint-white", "paint-silver", "paint-blue", "paint-green", "paint-red"]}, "lining": "#d6d3cc", "floor": "#3d4247",
         "moquette": {"pick": ["#2c4778", "#5a2632", "#3a3f48"]}, "seatShell": "plastic-grey", "rack": "plastic-grey", "trim": "plastic-black", "chrome": "chrome",
         "glass": "glass", "well": "#141416", "under": CAR_MATS["under"], "roofbox": "plastic-white"}, merge(parts), params={"open": 0, "steer": 0},
        markers=[{"role": "seat", "at": [5.3, 1.4, -0.7], "data": {"face": 0, "driver": 1}}] +
                [{"role": "door", "at": [(a + b) / 2, 0.3, hw], "data": {"face": 90}} for a, b in D])


# ---- THE CATALOGUE -------------------------------------------------------------------------------------------------
COMPONENTS = [("cast-wheel", cast_wheel), ("steering-wheel", steering_wheel), ("door-leaf", door_leaf), ("wing-mirror", wing_mirror),
              ("car-seat", car_seat), ("car-dash", car_dash), ("door-card", door_card)]
VEHICLES = [("car", car), ("saloon", saloon), ("taxi", lambda: saloon(True)), ("bicycle", bicycle), ("bus", city_bus), ("motorcycle", motorcycle), ("lorry", lorry), ("van", van), ("coach", coach)]


def write_all():
    for name, f in COMPONENTS: write("modern/components/" + name, f(), "components")
    for name, f in VEHICLES: write("modern/vehicles/" + name, f(), "vehicles")

GROUPS = {"vehicles": "vehicles", "components": "components"}
