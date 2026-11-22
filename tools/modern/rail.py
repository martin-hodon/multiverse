"""THE RAILWAY (2026-11-20; docs/modern.md): locomotives (electric, diesel, steam), a passenger carriage with its whole
inside, goods wagons and a tram -- each in the vehicle frame (kit.py: the ground, here THE RAIL'S TOP, under its
middle, +x its front, +z its right), on the standard gauge (1.435 m) and its bogies (components/bogie).

It also writes the shared components the railway needed and others can use:
  components/seat-row     a row of n seats in one piece, square-cut and cheap (a carriage's, an airliner's, a bus's
                          bench: 150 seats of components/seat would be 140k triangles; a row of three is ~200)
  components/pantograph   a single-arm pantograph on its insulators (a locomotive's, a tram's)
(the flat wagon's containers are the sea module's components/container)

And the LOFT HELPERS the air module uses too: `loft_eval` evaluates a loft's surface exactly as items.js builds it (the
same Catmull-Rom through the stations, the same rounded section), and `on_loft` gives the `at` that lays a thin pane
flat on that surface -- a windscreen on a locomotive's sloping nose, a cockpit window on an airliner's -- with
`euler` turning any three axes into items.js's yaw, pitch and roll."""
import math
from kit import item, merge, runs, slide, plug_slide, hinge, piece, cut, region, loft_z, shell_over, box, rod, lathe, loft, sphere, ring, sweep, plate, use, write, across, arc, hole, station_at, section_half, section_poly, loft_eval, euler, on_loft, handrail, spaced, window_holes, panes, _u_for, _half_point, _st

W = "modern/components/"
G = 1.435   # (the standard gauge: between the rails' inner faces)


def end_wall(id_, mat, s, rnd, x, thick=0.05, door=None, shrink=0.0, m=6, **k):
    """a flat wall across a loft at x, its outline the loft's section there (`shrink` inside it): an end wall, a
    bulkhead, a partition -- `door` (w, y0, y1) a doorway cut up from its bottom's middle"""
    st = [s[0], s[1] - shrink, s[2] + shrink, s[3] - shrink, (s[4] if len(s) > 4 else s[1]) - shrink]
    R = rnd if isinstance(rnd, (list, tuple)) else [rnd, rnd]
    poly = section_poly(st, [max(0.01, R[0] - shrink), max(0.01, R[1] - shrink)], m)
    if door:
        w, d0, d1 = door
        # (cut from the bottom's middle: out along the bottom to the doorway's right jamb, up, across its head, down)
        poly = [(w / 2, st[2])] + poly[1:] + [(-w / 2, st[2]), (-w / 2, d1), (w / 2, d1)]
    # (the plate's outline is in its x-y plane: turned by yaw 90 its x runs along -z)
    return plate(id_, mat, [[-zz, yy] for zz, yy in poly], thick, [x, 0, 0, 90, 0, 0], **k)


# ---- THE SHARED COMPONENTS ---------------------------------------------------------------------------------------
def seat_row():
    # A ROW OF SEATS in one piece: n seats side by side along z, their fronts at +x, the origin on the floor under the
    # row's middle -- square-cut boxes (a cushion, a raked back, an antimacassar or headrest, armrests between, two
    # legs and a beam), so a carriage's or an airliner's hundred seats stay cheap
    return item("Seat row", "components", "a row of n seats in one frame: cushions, raked backs, headrests (an antimacassar's white on a train), armrests between, the legs and beam under -- the fronts at +x, the origin on the floor under the row's middle; square-cut and cheap, for a carriage's or an airliner's many seats",
        {"cover": "upholstery", "frame": "plastic-grey", "head": "cover"}, [
            box("cushion", "cover", ["d", 0.11, "w - 0.05"], [0, "h - 0.055", 0], round=0, along={"n": "n", "from": [0, 0, "-(n - 1) * w / 2"], "to": [0, 0, "(n - 1) * w / 2"]}),
            box("back", "cover", [0.1, "back", "w - 0.06"], ["-d / 2 + 0.02", "h + back / 2 - 0.04", 0, 0, 0, "rake"], round=0, along={"n": "n", "from": [0, 0, "-(n - 1) * w / 2"], "to": [0, 0, "(n - 1) * w / 2"]}),
            box("headrest", "head", [0.11, 0.2, "w * 0.62"], ["-d / 2 - back * sin(rake * 0.017453) + 0.035", "h + back - 0.06", 0, 0, 0, "rake"], round=0, along={"n": "n", "from": [0, 0, "-(n - 1) * w / 2"], "to": [0, 0, "(n - 1) * w / 2"]}, when="headrest"),
            box("arm", "frame", ["d * 0.72", 0.05, 0.05], [0, "h + 0.17", 0], along={"n": "n + 1", "from": [0, 0, "-n * w / 2"], "to": [0, 0, "n * w / 2"]}, when="arms"),
            box("armPost", "frame", [0.04, 0.17, 0.04], ["d * 0.22", "h + 0.08", 0], along={"n": "n + 1", "from": [0, 0, "-n * w / 2"], "to": [0, 0, "n * w / 2"]}, when="arms"),
            box("beam", "frame", ["d * 0.5", 0.06, "n * w - 0.04"], [-0.02, "h - 0.14", 0]),
            box("leg", "frame", [0.05, "h - 0.17", 0.05], [-0.02, "(h - 0.17) / 2", 0], along={"n": 2, "from": [0, 0, "-(n * w / 2 - 0.12)"], "to": [0, 0, "n * w / 2 - 0.12"]}),
            box("foot", "frame", ["d * 0.8", 0.03, 0.05], [0, 0.015, 0], along={"n": 2, "from": [0, 0, "-(n * w / 2 - 0.12)"], "to": [0, 0, "n * w / 2 - 0.12"]}),
        ], params={"n": 3, "w": 0.46, "d": 0.47, "h": 0.45, "back": 0.66, "rake": 12, "headrest": 1, "arms": 1})


def pantograph():
    # A SINGLE-ARM PANTOGRAPH (the modern "Einholm", 1955-): the base frame on four insulators, the lower arm (two tubes
    # from the hinge forward and up to the knee), the upper arm (back to the head), the pan head across -- its two
    # contact bars with their carbon strips and horns. The origin at its feet on the roof, `h` the head's height raised
    # (about 1.0-2.6 m above the roof as the wire's height varies; folded ~0.45)
    kx, ky = "0.75", "0.42 + (h - 0.5) * 0.42"
    return item("Pantograph", "components", "a single-arm pantograph: the base frame on four ceramic insulators, the lower arm's two tubes to the knee, the upper arm back to the head, the pan head's contact bars and horns, ~1.95 m across -- raised to h above the roof",
        {"frame": "#3a3d40", "arm": "steel", "insulator": "#7a3a24", "carbon": "#1c1c1c"}, [
            lathe("insulator", "insulator", [[0, 0], [0.05, 0], [0.05, 0.04], [0.09, 0.06], [0.05, 0.09], [0.09, 0.12], [0.05, 0.15], [0.09, 0.18], [0.05, 0.21], [0.05, 0.26], [0, 0.26]], [[-0.7, 0, -0.42], [0.7, 0, -0.42], [-0.7, 0, 0.42], [0.7, 0, 0.42]], sides=8),
            box("base", "frame", [1.6, 0.08, 0.12], [0, 0.3, 0.42], mirror="z"),
            box("baseX", "frame", [0.12, 0.08, 0.96], [[-0.7, 0.3, 0], [0.7, 0.3, 0]]),
            rod("hinge", "frame", 0.05, [-0.62, 0.38, -0.36], [-0.62, 0.38, 0.36], 8),
            rod("lower", "arm", 0.035, [-0.62, 0.38, 0.3], [kx, ky, 0.1], 8, mirror="z"),
            rod("knee", "arm", 0.03, [kx, ky, -0.12], [kx, ky, 0.12], 8),
            rod("upper", "arm", 0.03, [kx, ky, 0], [-0.05, "h - 0.1", 0], 8),
            rod("tie", "arm", 0.012, [-0.45, 0.36, 0], [-0.2, "h - 0.16", 0], 6),
            rod("damper", "frame", 0.03, [-0.35, 0.36, 0.2], [0.1, "0.36 + (ky0 - 0.36) * 0.5", 0.16], 8, when="h"),
            rod("headPost", "arm", 0.02, [-0.05, "h - 0.14", -0.55], [-0.05, "h - 0.14", 0.55], 6),
            rod("bow", "frame", 0.012, [-0.05, "h - 0.12", 0], [0.15, "h - 0.04", 0], 6, mirror="x"),
            sweep("bar", "frame", [[0.15, "h - 0.2", -0.98], [0.15, "h - 0.04", -0.78], [0.15, "h - 0.01", -0.55], [0.15, "h - 0.01", 0.55], [0.15, "h - 0.04", 0.78], [0.15, "h - 0.2", 0.98]], 0.022, mirror="x"),
            box("strip", "carbon", [0.05, 0.03, 1.15], [0.15, "h + 0.02", 0], mirror="x"),
        ], params={"h": 1.6, "ky0": "0.42 + (h - 0.5) * 0.42"})


def loco_wheel():
    # A STEAM LOCOMOTIVE'S WHEEL (a driver, or a carrying wheel without its crank): the flanged tyre (the flange on
    # the inside, -z), the spokes cast with the centre, the hub, the crank's boss and pin at `crank` from the centre
    # (+x), the counterweight's crescent opposite it -- the axle along z, the outside face at +z, `r` the tread's radius
    return item("Locomotive wheel", "components", "a cast spoked locomotive wheel: the flanged tyre, n spokes, the hub, the crank pin at `crank` and the counterweight opposite -- the axle along z, the outside face at +z, the flange inside",
        {"wheel": "paint-black", "tyre": "steel", "pin": "steel"}, [
            lathe("tyre", "tyre", [["r * 0.86", -0.07], ["r + 0.035", -0.07], ["r + 0.035", -0.05], ["r", -0.035], ["r", 0.07], ["r * 0.86", 0.07], ["r * 0.86", -0.07]], [0, 0, 0, 0, 90, 0], caps=False, sides=28),
            lathe("rim", "wheel", [["r * 0.86", -0.05], ["r * 0.78", -0.05], ["r * 0.78", 0.05], ["r * 0.86", 0.05]], [0, 0, 0, 0, 90, 0], caps=False, sides=28),
            box("spoke", "wheel", ["r * 0.62", "r * 0.09", 0.06], [0, 0, 0], around={"n": "n", "r": "r * 0.47", "plane": "xy"}),
            lathe("hub", "wheel", [[0, 0.1], ["r * 0.2", 0.1], ["r * 0.22", 0.0], ["r * 0.2", -0.06], [0, -0.06]], [0, 0, 0, 0, 90, 0], sides=14),
            rod("boss", "wheel", "r * 0.12", ["crank", 0, 0], ["crank", 0, 0.09], 10, when="crank"),
            rod("pin", "pin", 0.05, ["crank", 0, 0.09], ["crank", 0, 0.22], 8, when="crank"),
            plate("weight", "wheel", [["r * 0.78 * cos(2.6)", "r * 0.78 * sin(2.6)"], ["r * 0.78 * cos(3.14)", 0], ["r * 0.78 * cos(3.68)", "r * 0.78 * sin(3.68)"], ["r * 0.4 * cos(3.4)", "r * 0.4 * sin(3.4)"], ["r * 0.4 * cos(2.88)", "r * 0.4 * sin(2.88)"]], 0.1, [0, 0, 0.01], when="weight"),
        ], params={"r": 0.85, "n": 16, "crank": 0.3, "weight": 1}, era="1830-1960")


# ---- RAILWAY HELPERS ---------------------------------------------------------------------------------------------
def buffers_and_hook(xe, y=1.06, mat="steel", head="buffer", frame="frame"):
    """at each end (x = +-xe, the headstock's face): two side buffers (1.75 m apart, their housings, plungers and
    heads) and the screw coupling's hook between them -- the European (UIC) draw-and-buffer gear"""
    out = []
    for i, (x, s) in enumerate([(xe, 1), (-xe, -1)]):
        out += [
            lathe(f"bufBody{i}", frame, [[0.13, 0], [0.1, 0.03], [0.1, 0.3], [0, 0.3]], [x, y, 0.875, 0, 0, -90 * s], sides=12, mirror="z"),
            lathe(f"bufRam{i}", mat, [[0.075, 0.28], [0.075, 0.5], [0, 0.5]], [x, y, 0.875, 0, 0, -90 * s], sides=12, mirror="z"),
            lathe(f"bufHead{i}", head, [[0, 0.5], [0.2, 0.5], [0.2, 0.54], [0.12, 0.57], [0, 0.575]], [x, y, 0.875, 0, 0, -90 * s], sides=16, mirror="z"),
            box(f"hook{i}", mat, [0.32, 0.12, 0.08], [x + s * 0.16, y, 0]),
            rod(f"screw{i}", mat, 0.025, [x + s * 0.3, y, 0], [x + s * 0.3, y - 0.35, 0], 6),
        ]
    return out


def knuckle_couplers(xe, y=0.88, mat="frame"):
    """the AAR (Janney) knuckle coupler at each end: the shank and the knuckle's head -- North American, no buffers"""
    out = []
    for i, (x, s) in enumerate([(xe, 1), (-xe, -1)]):
        out += [box(f"shank{i}", mat, [0.6, 0.18, 0.2], [x + s * 0.3, y, 0]),
                box(f"knuckle{i}", mat, [0.22, 0.3, 0.32], [x + s * 0.68, y, 0.04]),
                rod(f"cutLever{i}", "rail", 0.015, [x + s * 0.08, y + 0.35, -1.2], [x + s * 0.08, y + 0.35, 0.2], 6)]
    return out


def bogies(xs, r=0.46, base=2.5, mats=None):
    return [use(f"bogie{i}", W + "bogie", [x, 0, 0], {"r": r, "base": base}, mats) for i, x in enumerate(xs)]


def sliding_door(id_, x_open, y0, h, w, z, glass=True, mat="paint", **k):
    """a sliding door leaf (a plug door slid open alongside its doorway) at x_open, standing off the side at z, with
    its window"""
    out = [box(id_, mat, [w, h, 0.05], [x_open, y0 + h / 2, z], **k)]
    if glass: out.append(box(id_ + "Glass", "glass", [w - 0.24, h * 0.36, 0.012], [x_open, y0 + h * 0.66, z + 0.03], **k))
    return out


# ---- THE PASSENGER CARRIAGE -------------------------------------------------------------------------------------
def carriage():
    # A PASSENGER CARRIAGE, the UIC type (26.4 m over buffers, 2.825 m wide, the roof 4.05 m over the rail): an open
    # saloon of eleven bays, the seats facing each other in fours over tables, between two vestibules -- one at each
    # end, its sliding doors standing open on both sides, its end door into the gangway's bellows open too.
    # THE SHELL is a hollow loft (the outside paint) lined by a second loft inside it (the cream lining, seen from the
    # saloon); the windows and doorways are cut through both.
    L2, hw, y0, y1, fl = 13.05, 1.41, 1.05, 4.05, 1.25
    rnd = [0.1, 0.8]
    body = [[-L2, hw - 0.04, y0 + 0.02, y1 - 0.06], [-L2 + 0.4, hw, y0, y1], [L2 - 0.4, hw, y0, y1], [L2, hw - 0.04, y0 + 0.02, y1 - 0.06]]
    lin = [[-L2 + 0.06, hw - 0.1, y0 + 0.06, y1 - 0.14], [-L2 + 0.4, hw - 0.06, y0 + 0.04, y1 - 0.06], [L2 - 0.4, hw - 0.06, y0 + 0.04, y1 - 0.06], [L2 - 0.06, hw - 0.1, y0 + 0.06, y1 - 0.14]]
    bay, nb, vx = 1.89, 11, 10.4                       # (the bays' pitch, how many; where the vestibules start)
    bays = [-(nb - 1) / 2 * bay + i * bay for i in range(nb)]
    wins = spaced(-nb / 2 * bay, nb / 2 * bay, nb, 1.24)   # (a window 1.24 wide in the middle of each bay)
    win = window_holes(wins, 2.0, 3.05)
    dx = (11.45, 12.35)                                 # (the side doors' openings, near both ends)
    doors = [hole(dx[0], dx[1], y0 + 0.08, 3.25), hole(-dx[1], -dx[0], y0 + 0.08, 3.25)]
    vwin = [hole(10.75, 11.2, 2.15, 3.0), hole(-11.2, -10.75, 2.15, 3.0)]
    parts = [
        loft("body", "paint", body, rnd, holes=win + doors + vwin, caps=False, seg=1, corner=5),
        loft("lining", "lining", lin, [0.08, 0.74], holes=win + doors + vwin, caps=False, seg=1, corner=5, double=True),
        # (the window frames: a dark rubber reveal between the shell and the lining round each window)
        *panes("sill", "trim", "z", hw - 0.03, wins, [(1.98, 2.02), (3.03, 3.07)], t=0.08, over=0.01, mirror="z"),   # (and the head over it)
        box("stripe", "stripe", [2 * dx[0] - 0.1, 0.14, 0.01], [0, 1.72, hw + 0.004], mirror="z"),
        box("stripeEnd", "stripe", [L2 - dx[1] - 0.3, 0.14, 0.01], [[(L2 + dx[1]) / 2 - 0.1, 1.72, hw + 0.004], [-(L2 + dx[1]) / 2 + 0.1, 1.72, hw + 0.004]], mirror="z"),
        box("floor", "floorc", [2 * L2 - 0.1, 0.1, 2 * hw - 0.1], [0, fl - 0.05, 0]),
        # (the ends: the end wall with its doorway and the door slid into it, the gangway's bellows and its plates)
        *[end_wall(f"end{i}", "paint", station_at(body, x * 0.9999), rnd, x, 0.06, door=(0.82, y0, 3.2), m=5) for i, x in enumerate([L2 - 0.01, -L2 + 0.01])],
        loft("bellowsF", "bellows", [[L2, 0.62, fl - 0.05, 3.35], [L2 + 0.32, 0.62, fl - 0.05, 3.35]], 0.12, caps=False, double=True, seg=1),
        loft("bellowsR", "bellows", [[-L2 - 0.32, 0.62, fl - 0.05, 3.35], [-L2, 0.62, fl - 0.05, 3.35]], 0.12, caps=False, double=True, seg=1),
        box("gangPlate", "frame", [0.3, 0.03, 0.9], [[L2 + 0.17, fl, 0], [-L2 - 0.17, fl, 0]]),
        box("endDoor", "paint", [0.04, 1.95, 0.8], [[L2 - 0.05, fl + 0.98, 0.78], [-L2 + 0.05, fl + 0.98, -0.78]]),
        # (the vestibules' inner partitions: each a doorway with its glazed door slid aside)
        *[end_wall(f"part{i}", "lining", station_at(lin, x), [0.08, 0.74], x, 0.05, door=(0.9, y0 + 0.05, 3.15), shrink=0.0, m=5) for i, x in enumerate([vx, -vx])],
        box("partDoor", "partdoor", [0.04, 1.9, 0.86], [[vx + 0.05, fl + 0.96, 0.85], [-vx - 0.05, fl + 0.96, -0.85]]),
        box("partGlass", "glass", [0.045, 1.0, 0.6], [[vx + 0.05, fl + 1.25, 0.85], [-vx - 0.05, fl + 1.25, -0.85]]),
        # (the sliding side doors: each plug leaf shut in its doorway -- open, slid out and inboard along the side; the steps under)
        slide("door", [-0.93, 0, 0.06], sliding_door("leaf", (dx[0] + dx[1]) / 2, y0 + 0.12, 2.08, 0.92, hw + 0.005), mirror="z"),
        slide("doorR", [0.93, 0, 0.06], sliding_door("leaf", -(dx[0] + dx[1]) / 2, y0 + 0.12, 2.08, 0.92, hw + 0.005), mirror="z"),
        box("step", "frame", [0.9, 0.04, 0.26], [[(dx[0] + dx[1]) / 2, 0.75, hw - 0.05], [-(dx[0] + dx[1]) / 2, 0.75, hw - 0.05]], mirror="z"),
        box("stepHanger", "frame", [0.9, 0.3, 0.03], [[(dx[0] + dx[1]) / 2, 0.9, hw - 0.17], [-(dx[0] + dx[1]) / 2, 0.9, hw - 0.17]], mirror="z"),
        rod("grabDoor", "chrome", 0.016, [0, 1.45, hw + 0.04], [0, 2.6, hw + 0.04], 6, at=[[dx[0] - 0.05, 0, 0], [dx[1] + 0.05, 0, 0], [-dx[0] + 0.05, 0, 0], [-dx[1] - 0.05, 0, 0]], mirror="z"),
        # (THE SALOON: in every bay two rows of two facing each other over a table, both sides of the aisle)
        *[use(f"seatsF{i}", W + "seat-row", [c - 0.6, fl, 0.79], {"n": 2, "w": 0.5, "d": 0.47, "back": 0.7, "arms": 1, "headrest": 1}, mirror="z") for i, c in enumerate(bays)],
        *[use(f"seatsB{i}", W + "seat-row", [c + 0.6, fl, 0.79, 180, 0, 0], {"n": 2, "w": 0.5, "d": 0.47, "back": 0.7, "arms": 1, "headrest": 1}, mirror="z") for i, c in enumerate(bays)],
        box("table", "table", [0.5, 0.035, 0.36], [[c, fl + 0.73, hw - 0.25] for c in bays], mirror="z"),
        rod("tableLeg", "frame", 0.025, [0, fl, 0], [0, fl + 0.72, 0], 6, at=[[c, 0, hw - 0.36] for c in bays], mirror="z"),
        # (the luggage racks over the windows, on brackets at every bay; the lamps' strip down the ceiling)
        box("rack", "rack", [2 * vx - 0.2, 0.025, 0.3], [0, 3.32, hw - 0.27], mirror="z"),
        rod("rackRail", "chrome", 0.015, [-vx + 0.1, 3.36, hw - 0.42], [vx - 0.1, 3.36, hw - 0.42], 6, mirror="z"),
        box("rackBracket", "chrome", [0.03, 0.18, 0.3], [[c - bay / 2, 3.25, hw - 0.27] for c in bays + [bays[-1] + bay]], mirror="z"),
        box("lamps", "lamp", [2 * vx - 0.4, 0.03, 0.22], [0, y1 - 0.09, 0]),
        box("binVest", "lining", [0.6, 1.1, 0.5], [[11.95, fl + 0.55, -0.95], [-11.95, fl + 0.55, 0.95]]),
        # (the roof's vents, the underframe: the solebars, the equipment, the bogies, the buffers and the hook)
        box("vent", "frame", [0.5, 0.1, 0.35], [[c, y1 - 0.01, 0] for c in bays[::2]]),
        box("solebar", "frame", [2 * L2 - 0.3, 0.22, 0.12], [0, y0 - 0.06, hw - 0.12], mirror="z"),
        box("headstock", "frame", [0.2, 0.45, 2 * hw - 0.1], [[L2 - 0.1, y0 - 0.02, 0], [-L2 + 0.1, y0 - 0.02, 0]]),
        box("equip", "frame", [3.2, 0.5, 1.6], [[-3.0, 0.75, 0], [3.0, 0.75, 0]]),
        box("battery", "frame", [1.6, 0.45, 0.6], [0, 0.75, 0.6]),
        box("bolsterC", "frame", [0.6, 0.3, 2.0], [[9.5, 0.86, 0], [-9.5, 0.86, 0]]),
        *bogies([9.5, -9.5], 0.46, 2.5),
        *buffers_and_hook(L2 + 0.02, 1.06),
    ]
    return item("Passenger carriage", "vehicle", "a UIC passenger carriage of the 1970s-2000s, 26.4 m over buffers, 2.825 m wide, 4.05 m high: a hollow lofted shell with its lining, eleven windows a side, an open saloon of 88 seats in facing bays over tables, luggage racks, vestibules at both ends with their sliding plug doors (open: slid out and along), partitions with glazed doors, end doors into the gangway's bellows, two bogies (19 m apart), buffers and screw couplings",
        {"paint": {"pick": ["paint-green", "paint-navy", "paint-maroon", "#2f5d8a", "#5e6a72"]}, "lining": "#e4dccb", "stripe": "paint-cream", "trim": "plastic-black",
         "floorc": "carpet-grey", "bellows": "rubber", "frame": "paint-black", "chrome": "aluminium", "glass": "glass", "partdoor": "#b8b2a2",
         "cover": {"pick": ["upholstery", "upholstery-red", "upholstery-grey"]}, "head": "#efece4", "table": "#8a6a4a", "rack": "aluminium", "lamp": "lamp", "steel": "steel", "buffer": "steel"},
        merge(parts), params={"open": 0}, markers=[{"role": "door", "at": [(dx[0] + dx[1]) / 2, fl, hw + 0.2]}, {"role": "door", "at": [-(dx[0] + dx[1]) / 2, fl, hw + 0.2]}])


# ---- THE ELECTRIC LOCOMOTIVE -------------------------------------------------------------------------------------
def electric_loco():
    # AN ELECTRIC LOCOMOTIVE, a modern Bo'Bo' of the 2010s (19.98 m over buffers, 3.0 m wide, the roof 4.25 m over
    # the rail; 6.4 MW; Vectron- or Traxx-like): the body one loft, its two cabs' noses sloping back to the roof, the
    # windscreens laid on those slopes (on_loft), the cab's side windows and doors, the machine room's grilles, two
    # pantographs on the roof (the rear one raised, as running forward), the main breaker and the roof's busbar, the
    # transformer slung between the bogies (1.25 m wheels), buffers, hook, plough and lamps at both ends.
    L2, hw, y0 = 9.5, 1.5, 1.15
    rnd = [0.12, 0.5]
    half = [[9.5, 1.36, 1.2, 2.62, 1.14], [9.45, 1.42, 1.17, 2.75, 1.22], [9.1, 1.47, y0, 3.45, 1.3], [8.75, 1.5, y0, 4.15, 1.37], [8.3, hw, y0, 4.25, 1.4], [7.6, hw, y0, 4.25, 1.4]]
    body = [[-s[0], *s[1:]] for s in half] + [s for s in reversed(half)]
    roof = 4.25
    ends = [(1, "F"), (-1, "R")]
    BODY = loft("body", "paint", body, rnd, seg=3, corner=4)
    dX, dY = (6.99, 7.71), (1.325, 3.275)   # (a cab door's stretch: x |from, to|, y)
    ways = [region(s * dX[0], s * dX[1], *dY, "both") if s > 0 else region(-dX[1], -dX[0], *dY, "both") for s, _ in ends]
    parts = [cut(BODY, ways)]
    for s, n in ends:
        parts += [
            box(f"screen{n}", "glass", [0.03, 1.72, 1.12], on_loft(body, rnd, s * 9.1, z=0, off=0.015)),
            box(f"screenBar{n}", "trim", [0.035, 0.06, 1.12], on_loft(body, rnd, s * 9.1, z=0, off=0.016)),
            box(f"wiper{n}", "trim", [0.03, 0.04, 0.7], on_loft(body, rnd, s * 9.2, z=0.45, off=0.035)),
            box(f"sideWin{n}", "glass", [0.02, 0.62, 0.62], on_loft(body, rnd, s * 8.3, y=3.4, off=0.01), mirror="z"),
            # (THE CAB DOOR: the body's own stretch, dark as the door's panel was, hinged at its edge toward the middle and
            #  swung out 90 degrees by `open`, the window and a grab inside it)
            hinge(f"door{n}", [s * dX[0], 2.3, loft_z(body, rnd, dX[0], 2.3) - 0.005], [
                piece(BODY, [region(s * dX[0], s * dX[1], *dY) if s > 0 else region(-dX[1], -dX[0], *dY)], "skin", material="seam"),
                box("win", "glass", [0.02, 0.5, 0.45], on_loft(body, rnd, s * 7.35, y=2.9, off=0.012)),
                box("grip", "trim", [0.03, 0.3, 0.04], [s * 7.55, 2.3, loft_z(body, rnd, 7.55, 2.3) - 0.04], inside=True),
            ], max_=-90 * s, mirror="z"),
            # (THE CAB, seen only open: its floor, bulkhead, ceiling and side linings round the doors, the desk under the
            #  windscreen with its lining sloping up to the roof, the driver's seat)
            box(f"cabFloor{n}", "cabFloor", [2.35, 0.04, 2.84], [s * 7.92, 1.31, 0], inside=True),
            end_wall(f"cabBulk{n}", "lining", station_at(body, s * 6.75), rnd, s * 6.75, 0.04, shrink=0.06, inside=True),
            # (the lining: a loft just inside the body from the bulkhead to the nose, the door's opening cut through it,
            #  closed at the nose by a wall behind the windscreen)
            loft(f"cabLining{n}", "lining", shell_over(body, [6.73, 7.6, 8.3, 8.75, 9.0] if s > 0 else [-9.0, -8.75, -8.3, -7.6, -6.73], -0.06), [rnd[0] - 0.06, rnd[1] - 0.06], holes=[ways[0 if s > 0 else 1]], caps=False, seg=2, corner=5, double=True, inside=True),
            end_wall(f"cabNose{n}", "lining", station_at(body, s * 9.0), rnd, s * 9.0, 0.04, shrink=0.06, inside=True),
            box(f"desk{n}", "trim", [0.75, 1.0, 2.7], [s * 8.72, 1.81, 0], inside=True),
            box(f"deskTop{n}", "dash", [0.55, 0.04, 2.4], [s * 8.5, 2.33, 0, 0, 0, s * 14], inside=True),
            # (two screens on the desk, C screen laid back 60 degrees to face the driver: their middles where they were)
            use(f"screens{n}", W + "screen", [[s * 8.395, 2.42 + 0.01 * math.sin(math.radians(60)), z, 90 + 90 * s, 0, 60] for z in (-0.35, 0.05)],
                {"w": 0.31, "h": 0.19, "b": 0.015, "t": 0.02}, {"glass": "screen"}, inside=True),
            use(f"driver{n}", W + "seat", [s * 7.95, 1.33, -0.25, 0 if s > 0 else 180, 0, 0], {"w": 0.5, "h": 0.5, "arms": 1, "pedestal": 1}, inside=True),
            rod(f"grab{n}", "chrome", 0.018, [s * 6.9, 1.4, hw + 0.06], [s * 6.9, 2.9, hw + 0.04], 6, mirror="z"),
            rod(f"grab2{n}", "chrome", 0.018, [s * 7.8, 1.4, hw + 0.06], [s * 7.8, 2.9, hw + 0.04], 6, mirror="z"),
            box(f"step{n}", "frame", [0.6, 0.04, 0.28], [[s * 7.35, 0.62, hw - 0.1], [s * 7.35, 0.95, hw - 0.1]], mirror="z"),
            box(f"stepSide{n}", "frame", [0.04, 0.45, 0.28], [[s * 7.05, 0.8, hw - 0.1], [s * 7.65, 0.8, hw - 0.1]], mirror="z"),
            use(f"head{n}", W + "lamp", [s * 9.51, 1.78, 0.92, 0 if s > 0 else 180, 0, 0], {"shape": "square", "r": 0.13, "h": 0.12}, mirror="z"),
            use(f"tail{n}", W + "lamp", [s * 9.51, 1.78, 0.62, 0 if s > 0 else 180, 0, 0], {"shape": "square", "r": 0.06, "h": 0.12}, {"lens": "lamp-red"}, mirror="z"),
            use(f"top{n}", W + "lamp", [s * 8.55, 4.12, 0, 0 if s > 0 else 180, 0, 0], {"shape": "round", "r": 0.08}),
            box(f"headstock{n}", "frame", [0.3, 0.6, 2.9], [s * 9.38, 1.0, 0]),
            plate(f"plough{n}", "frame", [[-1.4, 0.75], [1.4, 0.75], [1.25, 0.12], [0, 0.12], [-1.25, 0.12]], 0.06, [s * 9.62, 0, 0, 90 + (12 if s > 0 else -12) * 0, 0, 0]),
            box(f"number{n}", "plate", [0.01, 0.16, 0.7], [s * 9.505, 2.35, 0, 0 if s > 0 else 180, 0, 0]),
        ]
    parts += [
        # (the machine room's sides: the grilles of the cooling air, the band of the livery)
        *[box(f"grille{i}", "grille", [0.02, 0.85, 1.25], on_loft(body, rnd, x, y=3.15, off=0.008), mirror="z") for i, x in enumerate([-4.4, -2.9, 2.9, 4.4])],
        *[box(f"louvre{i}", "grille", [0.02, 0.5, 2.2], on_loft(body, rnd, x, y=1.85, off=0.008), mirror="z") for i, x in enumerate([-1.3, 1.3])],
        box("band", "band", [0.012, 0.18, 13.2], on_loft(body, rnd, 0, y=2.62, off=0.006), mirror="z"),
        # (the roof: two pantographs, the breaker, the busbar on its insulators, the hatches)
        use("pantoF", W + "pantograph", [3.7, roof - 0.02, 0, 180, 0, 0], {"h": 0.48}),
        use("pantoR", W + "pantograph", [-3.7, roof - 0.02, 0], {"h": 1.75}),
        lathe("busIns", "insulator", [[0, 0], [0.05, 0], [0.08, 0.06], [0.05, 0.1], [0.08, 0.15], [0.05, 0.2], [0, 0.22]], [[-2.2, roof, 0], [0, roof, 0], [2.2, roof, 0]], sides=8),
        rod("busbar", "chrome", 0.025, [-3.5, roof + 0.25, 0], [3.5, roof + 0.25, 0], 6),
        box("breaker", "frame", [0.8, 0.3, 0.6], [0.9, roof + 0.13, 0.45]),
        box("hatch", "roofc", [2.6, 0.1, 2.2], [[-1.1, roof + 0.03, 0], [1.6, roof + 0.03, 0]]),
        # (under: the frame, the transformer, the bogies and the draw gear)
        box("frame", "frame", [2 * L2 - 0.6, 0.32, 2.85], [0, 1.02, 0]),
        box("transformer", "frame", [4.4, 0.7, 2.2], [0, 0.55, 0]),
        box("tank", "frame", [1.4, 0.5, 0.7], [[-1.5, 0.6, 0.95], [1.5, 0.6, -0.95]]),
        *bogies([4.95, -4.95], 0.625, 2.65),
        box("motor", "frame", [0.9, 0.5, 1.0], [[4.95, 0.7, 0], [-4.95, 0.7, 0]]),
        *buffers_and_hook(L2 + 0.03, 1.06),
    ]
    return item("Electric locomotive", "vehicle", "an electric Bo'Bo' locomotive of the 2010s, 19.98 m over buffers, 3.0 m wide, 4.25 m to the roof: a lofted body with two sloping cab noses and their windscreens, cab doors (hinged at their inner edge, swung out by `open` onto the cab: its floor, linings, desk, screens and the driver's seat) and side windows, cooling grilles, two single-arm pantographs (the rear raised), the roof's busbar and breaker, the transformer under the frame, two bogies with 1.25 m wheels, buffers, hooks, ploughs and lamps",
        {"paint": {"pick": ["paint-red", "#1f4f9a", "paint-silver", "#2c6e49", "paint-black"]}, "band": {"pick": ["paint-white", "paint-yellow", "paint-grey"]}, "glass": "glass", "trim": "plastic-black",
         "seam": "#2a2a2a", "chrome": "aluminium", "frame": "paint-black", "grille": "#3a3e44", "roofc": "paint-grey", "insulator": "#7a3a24", "plate": "plastic-white", "steel": "steel", "buffer": "steel",
         "lining": "#c9c6bd", "cabFloor": "#3e4044", "dash": "#2b2d31", "screen": "screen", "cover": "upholstery-grey"}, parts, params={"open": 0})


# ---- THE DIESEL LOCOMOTIVE --------------------------------------------------------------------------------------
def diesel_loco():
    # A DIESEL-ELECTRIC HOOD UNIT, the North American road switcher (the EMD GP38-2 type, 1972-: 18.0 m over the
    # couplers, 3.13 m wide, 4.67 m high, 2,000 hp, Bo-Bo on 1.016 m wheels): the long hood with its engine-room doors,
    # the exhaust stack and three radiator fans, the dynamic brake's blister; the cab with its windows; the short hood
    # with the headlight and number boards; the walkways along both sides with their handrails; steps at the four
    # corners, the pilots, the fuel tank slung between the trucks, the air reservoirs, knuckle couplers (no buffers).
    deck, L2 = 1.5, 8.35
    CAB, CR = [[3.3, 1.48, deck, 4.62, 1.42], [6.0, 1.48, deck, 4.62, 1.42]], [0.02, 0.35]
    # (THE CAB'S REAR DOORS, one each side between the long hood and the cab's corner, their windows the cab's rear
    #  windows: hinged at the hood's side and swung back flat against it by `open`. The rear wall is the cab's section
    #  less the two doorways, which reach up past the hood's top.)
    dz, dtop = (0.995, 1.465), 4.15
    half = [(z, y) for y, z in section_half(CAB[0], CR, 6) if y > dtop]
    zt = 1.48 + (1.42 - 1.48) * (dtop - deck) / (4.62 - 0.35 - deck)
    outline = [(0, deck), (dz[0], deck), (dz[0], dtop), (zt, dtop)] + half[:-1]
    outline = outline + [(-z, y) for z, y in reversed(outline[1:])]
    rear_wall = plate("cabRear", "paint", [[-z, y] for z, y in outline], 0.04, [3.32, 0, 0, 90, 0, 0])
    rear_door = hinge("cabDoor", [3.30, 2.8, dz[0]], [
        box("panel", "paint", [0.04, dtop - deck - 0.02, dz[1] - dz[0]], [3.32, (deck + dtop) / 2, (dz[0] + dz[1]) / 2]),
        box("win", "glass", [0.02, 0.72, 0.38], [3.29, 3.75, 1.23]),
        box("handle", "chrome", [0.03, 0.03, 0.14], [3.285, 2.6, 1.36]),
        box("inner", "lining", [0.02, 1.2, 0.36], [3.35, 2.45, 1.23], inside=True),
    ], max_=-90, mirror="z")
    parts = [
        box("frame", "frame", [2 * L2, 0.3, 3.1], [0, deck - 0.15, 0]),
        box("deckEdge", "rail", [2 * L2, 0.06, 0.04], [0, deck - 0.27, 1.53], mirror="z"),
        loft("longHood", "paint", [[-8.1, 0.98, deck, 4.02], [3.3, 0.98, deck, 4.02]], [0.02, 0.18], seg=1),
        # (the cab: a double loft, its rear cap left off for a wall with the two doors out onto the walkways)
        loft("cab", "paint", CAB, CR, seg=1, caps=[False, True], double=True),
        rear_wall,
        loft("shortHood", "paint", [[6.0, 0.92, deck, 3.35], [7.95, 0.92, deck, 3.3]], [0.02, 0.16], seg=1),
        box("cabRoof", "roofc", [2.9, 0.06, 2.6], [4.65, 4.62, 0]),
        # (the hood's engine-room doors down both sides, their handles; the stack, the fans, the dynamic brake)
        box("hoodSeam", "seam", [0.02, 1.7, 0.012], [0, 2.55, 0.985], along={"n": 12, "from": [-7.95, 0, 0], "to": [3.05, 0, 0]}, mirror="z"),
        box("hoodSeamH", "seam", [11.0, 0.02, 0.012], [[-2.45, 1.7, 0.985], [-2.45, 3.4, 0.985]], mirror="z"),
        box("hoodHandle", "chrome", [0.03, 0.12, 0.03], [0.32, 2.5, 0.995], along={"n": 11, "from": [-7.5, 0, 0], "to": [2.6, 0, 0]}, mirror="z"),
        box("louvres", "grille", [1.4, 0.7, 0.014], [[-6.6, 3.45, 0.985], [-4.9, 3.45, 0.985]], mirror="z"),
        box("stack", "frame", [0.75, 0.22, 0.45], [0.2, 4.1, 0]),
        box("blister", "paint", [2.6, 0.22, 1.7], [-2.0, 4.1, 0]),
        box("blisterGrille", "grille", [1.9, 0.02, 1.4], [-2.0, 4.22, 0]),
        lathe("fanShroud", "frame", [[0.62, 0], [0.62, 0.1], [0.56, 0.1], [0.56, 0.02]], [[-7.2, 4.02, 0], [-5.95, 4.02, 0], [-4.7, 4.02, 0]], sides=20),
        lathe("fanGrill", "grille", [[0, 0.06], [0.57, 0.06]], [[-7.2, 4.02, 0], [-5.95, 4.02, 0], [-4.7, 4.02, 0]], sides=20),
        rod("fanBar", "frame", 0.015, [-0.56, 4.09, 0], [0.56, 4.09, 0], 4, at=[[-7.2, 0, 0, a, 0, 0] for a in (0, 60, 120)] + [[-5.95, 0, 0, a, 0, 0] for a in (0, 60, 120)] + [[-4.7, 0, 0, a, 0, 0] for a in (0, 60, 120)]),
        lathe("horn", "chrome", [[0.03, 0], [0.06, 0.25], [0, 0.25]], [4.0, 4.7, 0.3, 0, 0, -90], sides=8),
        lathe("bell", "brass", [[0.0, 0.2], [0.07, 0.18], [0.12, 0.0], [0, 0.0]], [6.8, 3.35, 0], sides=10),
        # (the cab: front windows, side windows, the rear windows beside the long hood, the door into the nose)
        box("cabFrontWin", "glass", [0.02, 0.72, 0.82], [6.01, 3.75, 0.62], mirror="z"),
        box("cabSideWin", "glass", [1.0, 0.72, 0.02], [4.6, 3.75, 1.48], mirror="z"),
        rear_door,
        # (INSIDE THE CAB, seen only open: the floor, the engineer's control stand and seat on the right, the
        #  fireman's seat on the left, the heater and the desk under the front windows)
        box("cabFloor", "cabFloor", [2.62, 0.04, 2.9], [4.65, deck + 0.02, 0], inside=True),
        box("stand", "doorc", [0.55, 1.05, 0.45], [5.45, deck + 0.55, 1.0], inside=True),
        box("standTop", "chrome", [0.5, 0.04, 0.4], [5.43, deck + 1.1, 1.0, 0, 0, 12], inside=True),
        box("frontDesk", "doorc", [0.35, 0.95, 2.8], [5.8, deck + 0.5, 0], inside=True),
        box("heater", "doorc", [0.6, 0.5, 0.35], [4.0, deck + 0.27, -1.2], inside=True),
        use("seatE", W + "seat", [4.75, deck + 0.02, 1.0], {"w": 0.5, "h": 0.5, "arms": 1, "pedestal": 1}, inside=True),
        use("seatF", W + "seat", [4.75, deck + 0.02, -1.0], {"w": 0.5, "h": 0.5, "arms": 0, "pedestal": 1}, inside=True),
        box("noseDoor", "doorc", [0.012, 1.25, 0.6], [7.96, 2.15, 0]),
        box("noseDoorWin", "glass", [0.014, 0.35, 0.35], [7.965, 2.45, 0]),
        box("lightBox", "frame", [0.12, 0.2, 0.5], [7.95, 3.12, 0]),
        use("headlight", W + "lamp", [8.02, 3.12, 0.13], {"shape": "round", "r": 0.075}, mirror="z"),
        box("numberBoard", "plate", [0.03, 0.22, 0.6], [6.02, 4.35, 0.62], mirror="z"),
        use("ditch", W + "lamp", [8.4, 1.25, 1.2], {"shape": "round", "r": 0.07}, mirror="z"),
        use("rearLight", W + "lamp", [-8.11, 3.6, 0.0, 180, 0, 0], {"shape": "round", "r": 0.1}),
        # (the walkways' handrails and the end railings, the corner steps, the pilots)
        *handrail("rail", "rail", -8.2, 3.2, deck + 0.95, 1.5, posts=8, post_h=0.95, mirror="z"),
        *handrail("railNose", "rail", 6.1, 8.2, deck + 0.95, 1.5, posts=3, post_h=0.95, mirror="z"),
        rod("endRail", "rail", 0.02, [8.3, deck + 0.95, -1.5], [8.3, deck + 0.95, -0.9], 6, mirror="z", at=[[0, 0, 0], [-16.6, 0, 0]]),
        box("stepTread", "rail", [0.62, 0.04, 0.3], [[x, y, 1.38] for x in (7.75, -7.75) for y in (0.45, 0.85, 1.2)], mirror="z"),
        box("stepSide", "frame", [0.04, 1.1, 0.3], [[x, 0.85, 1.38] for x in (7.42, 8.08, -7.42, -8.08)], mirror="z"),
        plate("pilot", "frame", [[-1.55, 1.3], [1.55, 1.3], [1.3, 0.2], [-1.3, 0.2]], 0.08, [[8.42, 0, 0, 90, 0, 0], [-8.42, 0, 0, 90, 0, 0]]),
        # (under: the fuel tank between the trucks, the air reservoirs, the trucks, the couplers)
        loft("fuelTank", "frame", [[-2.6, 1.15, 0.5, 1.3], [2.6, 1.15, 0.5, 1.3]], 0.32, seg=1),
        rod("reservoir", "frame", 0.2, [-3.0, 1.1, 1.3], [3.0, 1.1, 1.3], 10, mirror="z"),
        *bogies([4.57, -4.57], 0.508, 2.74),
        box("tractionMotor", "frame", [0.6, 0.55, 1.0], [[x, 0.62, 0] for x in (5.94, 3.2, -3.2, -5.94)]),
        *knuckle_couplers(L2, 0.88),
    ]
    return item("Diesel locomotive", "vehicle", "a North American diesel-electric road switcher (an EMD GP38-2 type, 1972-), 18.0 m over couplers, 3.13 m wide, 4.67 m high: the long hood with its doors, stack, three radiator fans and the dynamic brake's blister, the cab (its two rear doors swung back against the hood by `open` onto its floor, control stand and seats) and the short hood, walkways and handrails along both sides, corner steps, pilots, the fuel tank between two Bo trucks (1.016 m wheels), knuckle couplers",
        {"paint": {"pick": ["paint-orange", "paint-navy", "#7a1f1f", "#1d4e3a", "paint-yellow", "paint-black"]}, "roofc": "paint", "frame": "paint-black", "rail": "paint-yellow", "seam": "#2a2a2a", "doorc": "#3c3c3c", "chrome": "chrome", "grille": "#2e3136",
         "glass": "glass", "plate": "plastic-white", "brass": "brass", "steel": "steel",
         "lining": "#bdb8a8", "cabFloor": "#3e4044", "cover": "upholstery-grey"}, parts, params={"open": 0})


# ---- GOODS WAGONS -----------------------------------------------------------------------------------------------
def box_wagon():
    # A COVERED GOODS WAGON on two bogies (the European Gabs / Habis type: 18.0 m over buffers, 2.83 m wide, 4.0 m
    # high): the body's planked steel sides stiffened by stanchions, two big sliding doors a side on their rails, the
    # arched roof, the end walls' ribs, the underframe and its solebars, the Y25 bogies, buffers and hooks
    L2, hw, y0, y1 = 8.4, 1.41, 1.2, 4.0
    rnd = [0.03, 0.55]
    body = [[-L2, hw, y0, y1], [L2, hw, y0, y1]]
    dx = [-3.3, 3.3]
    ribs = [x for x in [-7.8, -6.6, -5.4, -1.2, 0, 1.2, 5.4, 6.6, 7.8]]
    # (the doorways: behind each door's inner 2.35 m, where it slides off toward its end of the wagon)
    ways = [hole(1.65, 4.0, y0 + 0.12, y0 + 2.45), hole(-4.0, -1.65, y0 + 0.12, y0 + 2.45)]
    def door(x):
        """a sliding door on the rails: open, out 4 cm over the first fifth (clear of the stanchions), then 2.4 m
        toward its end of the wagon"""
        sg = 1 if x > 0 else -1
        return plug_slide(f"door{'F' if x > 0 else 'R'}", [sg * 2.4, 0, 0.04], [
            box("panel", "door", [3.4, 2.5, 0.06], [x, y0 + 1.33, hw + 0.07]),
            box("rib", "door", [0.07, 2.5, 0.05], [[x + d, y0 + 1.33, hw + 0.12] for d in (-1.1, 0, 1.1)]),
            box("handle", "frame", [0.05, 0.6, 0.05], [x - sg * 1.55, y0 + 1.2, hw + 0.13]),
        ], out=0.2, mirror="z")
    parts = [
        loft("body", "paint", body, rnd, seg=1, corner=5, holes=ways, double=True),
        box("rib", "paint", [0.1, y1 - y0 - 0.65, 0.06], [[x, y0 + (y1 - y0 - 0.65) / 2 + 0.03, hw + 0.03] for x in ribs], mirror="z"),
        box("ribEnd", "paint", [0.06, y1 - y0 - 0.6, 0.1], [[s * (L2 + 0.03), y0 + (y1 - y0 - 0.6) / 2, z] for s in (1, -1) for z in (-0.95, -0.32, 0.32, 0.95)]),
        *[door(x) for x in dx],
        rod("doorRailTop", "frame", 0.04, [-7.6, y0 + 2.62, hw + 0.08], [7.6, y0 + 2.62, hw + 0.08], 6, mirror="z"),
        box("doorRailBot", "frame", [15.2, 0.08, 0.1], [0, y0 + 0.04, hw + 0.07], mirror="z"),
        # (inside, seen only open: the plank floor, the lining's battens, a light load -- pallets of cartons, sacks)
        box("floorIn", "planks", [2 * L2 - 0.1, 0.04, 2 * hw - 0.1], [0, y0 + 0.05, 0], inside=True),
        box("battens", "planks", [2 * L2 - 0.3, 0.08, 0.04], [[0, y0 + 1.0, hw - 0.04], [0, y0 + 1.8, hw - 0.04]], mirror="z", inside=True),
        box("pallet", "planks", [1.2, 0.14, 0.8], [[x, y0 + 0.14, z] for x, z in [(-6.6, -0.5), (-6.6, 0.5), (-5.2, -0.5), (6.4, 0.45), (5.0, -0.5)]], inside=True),
        box("cartons", "carton", [1.15, 0.9, 0.78], [[x, y0 + 0.66, z] for x, z in [(-6.6, -0.5), (-6.6, 0.5), (-5.2, -0.5), (6.4, 0.45)]], inside=True),
        box("cartonsTop", "carton", [1.1, 0.5, 0.74], [[-6.6, y0 + 1.36, -0.5], [-6.6, y0 + 1.36, 0.5]], inside=True),
        box("sacks", "sacking", [0.85, 0.28, 0.5], [[5.0, y0 + 0.35, -0.65], [5.0, y0 + 0.35, -0.33], [5.0, y0 + 0.62, -0.5, 8, 0, 0]], round=0.1, inside=True),
        box("label", "plate", [1.6, 0.6, 0.012], [-5.9, y0 + 0.6, hw + 0.035], mirror="z"),
        box("solebar", "frame", [2 * L2, 0.32, 0.14], [0, y0 - 0.12, hw - 0.1], mirror="z"),
        box("headstock", "frame", [0.25, 0.42, 2.8], [[L2 - 0.12, y0 - 0.12, 0], [-L2 + 0.12, y0 - 0.12, 0]]),
        box("bolsterC", "frame", [0.5, 0.35, 2.2], [[6.2, 0.92, 0], [-6.2, 0.92, 0]]),
        box("brakeCyl", "frame", [1.2, 0.35, 0.4], [0, 0.95, 0.4]),
        *bogies([6.2, -6.2], 0.46, 1.8),
        *buffers_and_hook(L2, 1.06),
    ]
    return item("Covered goods wagon", "vehicle", "a covered goods wagon on two bogies (Gabs / Habis type), 18 m over buffers, 2.83 m wide, 4.0 m high: steel sides with their stanchions, two sliding doors a side on their rails (`open`: out and toward the ends, onto the hollow inside -- plank floor, battens, a light load of pallets and sacks), the arched roof, ribbed ends, solebars, Y25 bogies, buffers and hooks",
        {"paint": {"pick": ["#6b3a2a", "#5a2e24", "#7a4630", "#4f4a44"]}, "door": "#4a2a20", "frame": "paint-black", "plate": "#d8d4c8", "steel": "steel", "buffer": "steel",
         "planks": "planks", "carton": "#b08a5c", "sacking": "hemp"}, parts, params={"open": 0})


def flat_wagon():
    # A CONTAINER FLAT WAGON (the Sgns type, 19.74 m over buffers, the deck 1.155 m over the rail): an open frame of
    # two fish-bellied side sills and the cross members, carrying a 40-ft and a 20-ft container (components/container)
    # on its spigots; Y25 bogies, buffers and hooks
    L2, top = 9.2, 1.155
    sill = [[-L2, top], [L2, top], [L2, top - 0.3], [5.0, top - 0.6], [-5.0, top - 0.6], [-L2, top - 0.3]]
    parts = [
        plate("sideSill", "frame", sill, 0.2, [0, 0, 1.2], mirror="z"),
        plate("centreSill", "frame", sill, 0.3, [0, 0, 0]),
        box("cross", "frame", [0.18, 0.2, 2.4], [0, top - 0.1, 0], along={"n": 11, "from": [-L2 + 0.1, 0, 0], "to": [L2 - 0.1, 0, 0]}),
        box("walk", "deckc", [2 * L2, 0.03, 0.3], [0, top - 0.015, 1.15], mirror="z"),
        box("headstock", "frame", [0.25, 0.42, 2.8], [[L2 - 0.12, 1.0, 0], [-L2 + 0.12, 1.0, 0]]),
        box("spigot", "frame", [0.15, 0.06, 0.15], [[x, top + 0.03, 1.13] for x in (-9.05, 3.05, 3.12, 9.12)], mirror="z"),
        use("box40", W + "container", [-3.0, top, 0], {"L": 12.192, "ribs": 44}, {"cbox": "box40", "cframe": "box40", "cbar": "steel"}),
        use("box20", W + "container", [6.12, top, 0], {"L": 6.058, "ribs": 22}, {"cbox": "box20", "cframe": "box20", "cbar": "steel"}),
        box("bolsterC", "frame", [0.5, 0.3, 2.2], [[7.1, 0.86, 0], [-7.1, 0.86, 0]]),
        *bogies([7.1, -7.1], 0.46, 1.8),
        *buffers_and_hook(L2 + 0.02, 1.06),
    ]
    return item("Container flat wagon", "vehicle", "a container flat wagon (Sgns type), 19.74 m over buffers, its deck 1.155 m high: fish-bellied side and centre sills, cross members, spigots, a 40-ft and a 20-ft container, Y25 bogies, buffers and hooks",
        {"frame": {"pick": ["paint-black", "#5a2e24", "#3f4a3a"]}, "deckc": "steel", "box40": {"pick": ["#5d9ccb", "#a8342e", "#3b7148", "#8c9196", "#22427e"]}, "box20": {"pick": ["#d9b13a", "#d0642b", "#2f8487", "#d9d9d4", "#73492f"]}, "steel": "steel", "buffer": "steel"}, parts)


# ---- THE TRAM --------------------------------------------------------------------------------------------------
def tram():
    # A LOW-FLOOR TRAM of two sections (the Combino / Citadis / Flexity kind, 1996-: 26 m long, 2.4 m wide, 3.3 m to
    # the roof, the floor 0.35 m over the rail all through), driven from either end: each section a hollow loft with
    # its raked nose and windscreen, its band of windows, two double doors a side (plug leaves: open, slid out
    # and along), one bogie under its middle in the wheel arches; the bellows of the articulation between; inside, the
    # floor, the seats in facing pairs over the wheel housings and along the sides, the grab poles, the lights, the
    # cab's bulkhead and the driver's seat and desk. One pantograph on the front section, the converters and the air
    # conditioning on the roofs.
    hw, y0, y1, fl = 1.2, 0.2, 3.3, 0.35
    rnd = [0.1, 0.36]
    st = [[0.28, hw, y0, y1], [11.7, hw, y0, y1], [12.45, 1.18, y0 + 0.03, 3.22, 1.08], [12.95, 1.1, y0 + 0.06, 3.0, 0.95], [13.15, 0.98, y0 + 0.1, 2.72, 0.8]]
    bx = 7.0                                            # (the bogie under each section's middle)
    doors = [(1.25, 2.55), (9.05, 10.35)]
    wins = [(2.75, 4.45), (4.65, 6.35), (6.55, 8.85), (10.55, 11.45)]
    parts = [loft("bellows", "bellows", [[-0.3, 1.12, fl - 0.05, 3.12], [0.3, 1.12, fl - 0.05, 3.12]], 0.2, caps=False, double=True, seg=1),
             box("joint", "frame", [0.7, 0.06, 1.6], [0, fl - 0.02, 0])]
    for s_, n in [(1, "A"), (-1, "B")]:
        S = [[s_ * x, *rest] for x, *rest in st]
        S = S if s_ > 0 else S[::-1]
        X = lambda a, b: (min(s_ * a, s_ * b), max(s_ * a, s_ * b))
        holes = [hole(*X(a, b), 0.38, 2.62) for a, b in doors] + window_holes([X(a, b) for a, b in wins], 1.05, 2.78) + [hole(*X(11.75, 12.35), 1.15, 2.6)]
        yaw = 0 if s_ > 0 else 180
        parts += [
            loft(f"body{n}", "paint", S, rnd, holes=holes, caps=[False, True] if s_ > 0 else [True, False], seg=2, corner=5, double=True,
                 arches=[[s_ * (bx - 0.9), 0.33, 0.44], [s_ * (bx + 0.9), 0.33, 0.44]]),
            box(f"skirt{n}", "trim", [12.0, 0.16, 0.02], [s_ * 6.4, 0.3, hw + 0.004], mirror="z"),
            box(f"windscreen{n}", "glass", [0.02, 1.3, 1.5], [s_ * 13.16, 1.68, 0, yaw, 0, 0]),
            box(f"dest{n}", "screen", [0.02, 0.14, 0.9], [s_ * 13.165, 2.48, 0, yaw, 0, 0]),
            use(f"head{n}", W + "lamp", [s_ * 13.16, 0.72, 0.6, yaw, 0, 0], {"shape": "square", "r": 0.11, "h": 0.08}, mirror="z"),
            use(f"tail{n}", W + "lamp", [s_ * 13.16, 0.9, 0.6, yaw, 0, 0], {"shape": "square", "r": 0.06, "h": 0.05}, {"lens": "lamp-red"}, mirror="z"),
            box(f"coupler{n}", "trim", [0.25, 0.25, 0.6], [s_ * 13.22, 0.5, 0]),
            *bogies([s_ * bx], 0.33, 1.8),
            box(f"wheelHouse{n}", "trim", [2.5, 0.42, 2.3], [s_ * bx, fl + 0.21, 0]),
            # (the double doors: each leaf shut in its half of the opening; open (`open`), out of it by 5.5 cm over the
            #  first quarter, then along the side away from the opening's middle -- plug sliding leaves, kit.plug_slide;
            #  the section's eight one `each` grid, its joints `leaf<n>#i` and `~2` the mirrored side, each carrying `leaf`)
            *runs(f"leaf{n}", [plug_slide("leaf", [-s_ * 0.655, 0, 0.055], sliding_door("leaf", s_ * (a + 0.3275), 0.38, 2.22, 0.645, hw + 0.005, glass=True), mirror="z") for a, b in doors]
                  + [plug_slide("leaf", [s_ * 0.655, 0, 0.055], sliding_door("leaf", s_ * (b - 0.3275), 0.38, 2.22, 0.645, hw + 0.005, glass=True), mirror="z") for a, b in doors], least=2),
            rod(f"pole{n}", "pole", 0.02, [0, fl, 0], [0, y1 - 0.05, 0], 8, at=[[s_ * x, 0, z] for x in (1.25, 2.55, 9.05, 10.35) for z in (0.75, -0.75)]),
            rod(f"rail{n}", "pole", 0.017, [s_ * 1.0, 2.0, 0.42], [s_ * 11.0, 2.0, 0.42], 6, mirror="z"),
            # (the seats: in facing pairs over the wheel housing, and pairs along the sides between the doors)
            use(f"seatsA{n}", W + "seat-row", [s_ * (bx - 0.75), fl + 0.42, 0.62, yaw, 0, 0], {"n": 2, "w": 0.46, "h": 0.45, "back": 0.6, "arms": 0, "headrest": 0}, mirror="z"),
            use(f"seatsB{n}", W + "seat-row", [s_ * (bx + 0.75), fl + 0.42, 0.62, 180 - yaw, 0, 0], {"n": 2, "w": 0.46, "h": 0.45, "back": 0.6, "arms": 0, "headrest": 0}, mirror="z"),
            use(f"seatsC{n}", W + "seat-row", [s_ * 3.6, fl, 0.62, 180 - yaw, 0, 0], {"n": 2, "w": 0.46, "h": 0.45, "back": 0.6, "arms": 0, "headrest": 0}, mirror="z"),
            use(f"seatsD{n}", W + "seat-row", [s_ * 4.6, fl, 0.62, yaw, 0, 0], {"n": 2, "w": 0.46, "h": 0.45, "back": 0.6, "arms": 0, "headrest": 0}, mirror="z"),
            use(f"seatsE{n}", W + "seat-row", [s_ * 10.9, fl, 0.62, 180 - yaw, 0, 0], {"n": 2, "w": 0.46, "h": 0.45, "back": 0.6, "arms": 0, "headrest": 0}, mirror="z"),
            box(f"floor{n}", "floorc", [12.6, 0.06, 2 * hw - 0.08], [s_ * 6.15, fl - 0.03, 0]),
            box(f"lights{n}", "lamp", [10.5, 0.03, 0.3], [s_ * 6.0, y1 - 0.06, 0.55], mirror="z"),
            # (the cab: its bulkhead and door, the driver's seat and desk)
            end_wall(f"cabWall{n}", "lining", station_at(S, s_ * 11.6), rnd, s_ * 11.6, 0.05, door=(0.7, y0, 2.3), shrink=0.04),
            use(f"driver{n}", W + "seat", [s_ * 12.15, fl, 0, yaw, 0, 0], {"w": 0.5, "h": 0.5, "arms": 1, "pedestal": 1}),
            box(f"desk{n}", "trim", [0.45, 0.9, 1.5], [s_ * 12.75, fl + 0.45, 0]),
            # (the roof: the converters and the air conditioning)
            box(f"roofBox{n}", "roofc", [3.2, 0.35, 1.7], [s_ * 8.6, y1 + 0.15, 0]),
            box(f"hvac{n}", "roofc", [2.0, 0.3, 1.6], [s_ * 2.4, y1 + 0.13, 0]),
        ]
    parts += [use("panto", W + "pantograph", [5.0, y1 - 0.02, 0], {"h": 1.35}),
              box("pantoBase", "roofc", [2.0, 0.08, 1.4], [5.0, y1 + 0.02, 0])]
    return item("Tram", "vehicle", "a two-section low-floor tram (Combino / Citadis kind, 1996-), 26 m long, 2.4 m wide, 3.3 m to the roof, the floor 0.35 m: two hollow lofted sections with raked noses and windscreens, window bands, two double doors a side (plug sliding leaves: `open` slides them out and along), the articulation's bellows, a bogie under each section in its wheel arches; inside the floor, seats in facing pairs and over the wheel housings, grab poles and rails, lights, the cabs with their driver's seats and desks; a pantograph and the roof's equipment",
        {"paint": {"pick": ["paint-red", "paint-yellow", "#1f6fb2", "paint-white", "#2c6e49", "paint-silver"]}, "glass": "glass", "trim": "plastic-black", "bellows": "rubber", "frame": "paint-black",
         "lining": "#d9d6ce", "floorc": "#4a4c50", "pole": "paint-yellow", "lamp": "lamp", "screen": "#e09a1a", "roofc": "paint-grey", "cover": {"pick": ["upholstery", "upholstery-red", "upholstery-grey"]},
         "steel": "steel"}, parts, params={"open": 0})


# ---- THE STEAM LOCOMOTIVE ----------------------------------------------------------------------------------------
def steam_loco():
    # A STEAM LOCOMOTIVE AND ITS TENDER, the "American" 4-4-0 (the commonest engine of the 1850s-1890s: the loco 10 m,
    # with its tender 17.4 m; 1.57 m drivers): the boiler and the smokebox (lathes along x), the diamond stack, the
    # steam and sand domes and the bell, the big oil headlamp, the wooden cab; the leading truck's four small wheels and
    # the four coupled drivers (components/loco-wheel) with their coupling and main rods, the cylinders and their
    # crosshead guides, the pilot (the cowcatcher); the tender's tank with its coal heap on two bogies. The +x the
    # smokebox's front, the origin under the middle of loco and tender together.
    by, br = 2.35, 0.68                                # (the boiler's centre line and radius)
    g2 = G / 2 + 0.07
    dr, lr = 0.785, 0.42                               # (the drivers' and the leading truck's tread radii)
    dx, lx = [1.55, 3.75], [6.05, 7.45]
    parts = [
        lathe("boiler", "boiler", [[br, 0], [br, 5.1], [0, 5.1]], [0.95, by, 0, 0, 0, -90], sides=24),
        *[lathe(f"band{i}", "brass", [[br + 0.015, 0], [br + 0.015, 0.06]], [x, by, 0, 0, 0, -90], caps=False, sides=24) for i, x in enumerate([1.6, 2.9, 4.2, 5.4])],
        lathe("smokebox", "smoke", [[0, 0], [br + 0.06, 0], [br + 0.06, 1.25], [br * 0.9, 1.3], [0, 1.3]], [6.05, by, 0, 0, 0, -90], sides=24),
        lathe("stack", "smoke", [[0.17, 0], [0.17, 0.55], [0.42, 1.05], [0.47, 1.28], [0.3, 1.36], [0, 1.36]], [6.7, by + br - 0.05, 0], sides=16),
        lathe("dome", "brass", [[0.36, 0], [0.33, 0.35], [0.28, 0.48], [0.12, 0.56], [0, 0.57]], [3.6, by + br - 0.08, 0], sides=16),
        lathe("sand", "boiler", [[0.3, 0], [0.27, 0.3], [0.18, 0.4], [0, 0.42]], [5.1, by + br - 0.08, 0], sides=14),
        lathe("bell", "brass", [[0, 0.32], [0.1, 0.3], [0.16, 0.06], [0.18, 0], [0, 0]], [4.35, by + br + 0.25, 0], sides=12),
        box("bellYoke", "smoke", [0.04, 0.3, 0.36], [4.35, by + br + 0.1, 0]),
        rod("whistle", "brass", 0.04, [1.4, by + br - 0.05, 0], [1.4, by + br + 0.35, 0], 8),
        box("lampBox", "lampc", [0.55, 0.6, 0.55], [7.05, by + br + 0.3, 0]),
        box("lampLens", "lamp", [0.02, 0.4, 0.4], [7.33, by + br + 0.3, 0]),
        box("lampShelf", "smoke", [0.6, 0.05, 0.6], [7.05, by + br - 0.02, 0]),
        # (the firebox, the cab: its walls, windows, roof)
        box("firebox", "smoke", [1.25, 1.0, 1.2], [0.85, 1.55, 0]),
        box("cabSide", "cab", [1.9, 1.35, 0.06], [0.2, 2.45, 1.32], mirror="z"),
        box("cabWin", "glassc", [0.55, 0.45, 0.07], [[0.6, 2.8, 1.32], [-0.2, 2.8, 1.32]], mirror="z"),
        box("cabFront", "cab", [0.06, 2.3, 2.7], [1.17, 2.95, 0]),
        box("cabFrontWin", "glassc", [0.07, 0.45, 0.42], [1.17, 3.25, 0.95], mirror="z"),
        box("cabPost", "cab", [0.1, 2.4, 0.1], [[-0.72, 3.0, 1.3], [1.12, 3.0, 1.3]], mirror="z"),
        box("cabUpper", "cab", [1.9, 0.45, 0.06], [0.2, 3.85, 1.32], mirror="z"),
        loft("cabRoof", "roof", [[-1.0, 1.55, 3.98, 4.22], [1.35, 1.55, 3.98, 4.22]], [0.02, 0.2], seg=1),
        box("cabFloor", "deck", [2.0, 0.08, 2.7], [0.2, 1.75, 0]),
        # (the running boards, the frames, the cylinders and their valve chests, the guides, the pilot)
        box("board", "smoke", [5.2, 0.05, 0.4], [3.5, 1.7, 1.12], mirror="z"),
        box("frame", "smoke", [7.6, 0.3, 0.1], [3.6, 1.05, g2 - 0.32], mirror="z"),
        box("buffer", "beam", [0.25, 0.4, 2.7], [8.2, 1.05, 0]),
        lathe("cylinder", "smoke", [[0.29, 0], [0.29, 0.75], [0, 0.75]], [6.4, 1.1, 1.1, 0, 0, -90], sides=16, mirror="z"),
        box("chest", "smoke", [0.7, 0.35, 0.4], [6.77, 1.5, 1.05], mirror="z"),
        lathe("steamPipe", "smoke", [[0.09, 0], [0.09, 1.0]], [6.6, 1.45, 0.72, 0, 0, -38], sides=8, mirror="z"),
        box("guide", "steel", [1.3, 0.05, 0.08], [[5.65, 1.22, 1.1], [5.65, 0.98, 1.1]], mirror="z"),
        box("crosshead", "steel", [0.25, 0.22, 0.12], [5.1, 1.1, 1.1], mirror="z"),
        rod("pistonRod", "steel", 0.035, [5.1, 1.1, 1.1], [6.4, 1.1, 1.1], 8, mirror="z"),
        loft("pilot", "pilot", [[8.25, 1.2, 0.1, 1.0], [8.5, 0.85, 0.1, 0.78], [9.05, 0.05, 0.1, 0.16]], 0.02, seg=2, corner=1),
        box("pilotSlat", "beam", [0.05, 0.06, 0.06], [8.6, 0.5, 0], along={"n": 7, "from": [0, 0, -0.75], "to": [0, 0, 0.75]}, when=0),
        box("pilotBar", "beam", [0.12, 0.08, 2.5], [8.35, 1.0, 0]),
        # (the wheels: the leading truck's four, the four coupled drivers; their rods -- the crank pins all forward)
        *[use(f"lead{i}", W + "loco-wheel", [x, lr, g2], {"r": lr, "n": 10, "crank": 0, "weight": 0}, mirror="z") for i, x in enumerate(lx)],
        box("truckFrame", "smoke", [2.1, 0.18, 0.1], [6.75, lr + 0.05, g2 + 0.2], mirror="z"),
        *[use(f"driver{i}", W + "loco-wheel", [x, dr, g2], {"r": dr, "n": 16, "crank": 0.32, "weight": 1}, mirror="z") for i, x in enumerate(dx)],
        rod("axle", "steel", 0.08, [0, 0, -g2], [0, 0, g2], 8, at=[[x, r, 0] for x, r in [(dx[0], dr), (dx[1], dr), (lx[0], lr), (lx[1], lr)]]),
        box("couplingRod", "steel", [dx[1] - dx[0] + 0.2, 0.1, 0.05], [(dx[0] + dx[1]) / 2 + 0.32, dr, g2 + 0.2], mirror="z"),
        rod("mainRod", "steel", 0.045, [dx[1] + 0.32, dr, g2 + 0.27], [5.1, 1.1, g2 + 0.27], 8, mirror="z"),
        box("splasher", "smoke", [1.8, 0.1, 0.25], [[x, dr * 2 + 0.06, 1.0] for x in dx], mirror="z"),
        # THE TENDER: the frame on two bogies, the tank with its flared top, the coal heap
        box("tFrame", "beam", [6.8, 0.28, 2.6], [-4.95, 1.18, 0]),
        box("tank", "tender", [6.6, 1.45, 2.7], [-5.0, 2.05, 0]),
        box("flare", "tender", [4.4, 0.3, 0.06], [-3.9, 2.9, 1.37, 0, 0, 0], mirror="z"),
        box("tankBack", "tender", [2.2, 0.3, 2.8], [-7.2, 2.9, 0]),
        sphere("coal", "coal", 1.0, [-3.9, 2.8, 0], stretch=[2.1, 0.55, 1.25], sides=12),
        box("letter", "brass", [3.0, 0.3, 0.012], [-5.0, 2.15, 1.355], mirror="z"),
        *bogies([-2.9, -7.0], 0.45, 1.6),
        box("tCoupler", "beam", [0.3, 0.3, 0.4], [-8.5, 1.05, 0]),
        box("drawbar", "steel", [0.6, 0.1, 0.2], [-1.25, 1.1, 0]),
    ]
    return item("Steam locomotive", "vehicle", "an American-type 4-4-0 steam locomotive and its tender (1850s-1890s), 17.4 m with the tender: the boiler and smokebox, a diamond stack, steam and sand domes, the bell, an oil headlamp, the wooden cab; a four-wheeled leading truck, four coupled 1.57 m drivers with their coupling and main rods, the cylinders, guides and crosshead, the cowcatcher; the tender's tank and coal on two bogies",
        {"boiler": {"pick": ["#2c4a3a", "#3a2a24", "#1e2a3a", "#5a1e1e"]}, "smoke": "paint-black", "brass": "brass", "cab": {"pick": ["#7a4a2a", "#8a2a20", "walnut"]}, "roof": "paint-black",
         "glassc": "glass", "lampc": "paint-black", "lamp": "lamp", "deck": "planks", "beam": "#6a2a1e", "pilot": "#8a2a20", "tender": "boiler", "coal": "#1a1a1c",
         "steel": "steel", "wheel": "#7a1e1a", "tyre": "steel", "pin": "steel", "frame": "paint-black"}, parts, era="1850-1900")


def write_all():
    write("modern/components/seat-row", seat_row(), "components")
    write("modern/components/pantograph", pantograph(), "components")
    write("modern/rail/carriage", carriage(), "rail")
    write("modern/rail/electric-locomotive", electric_loco(), "rail")
    write("modern/rail/diesel-locomotive", diesel_loco(), "rail")
    write("modern/rail/box-wagon", box_wagon(), "rail")
    write("modern/rail/flat-wagon", flat_wagon(), "rail")
    write("modern/rail/tram", tram(), "rail")
    write("modern/components/loco-wheel", loco_wheel(), "components")
    write("modern/rail/steam-locomotive", steam_loco(), "rail")

GROUPS = {"rail": "railway", "components": "components"}
