"""THE HORSE-DRAWN CARRIAGES (2026-11-20; docs/modern.md): the road between the farm wagon (components/cart-*, the
carts of carts.js) and the motor car, ~1750-1910 -- a Concord stagecoach, a brougham, a hansom cab, a gig and a
knifeboard omnibus. Each is in the vehicle frame (kit.py: the ground under its middle, +x its front, +z its right);
the horse is NOT part of it, but its shafts (one horse) or its pole (a pair, a team) are, pointing +x and ending
where the horse's collar would be.

They share the components written here (group "components"): `carriage-wheel` (a finer wheel than the cart's: a
dished wheel of tapered spokes in a wooden felloe, the iron tyre, the turned nave and its brass cap) and
`carriage-lamp` (a square lantern on its bracket). The helpers (`axle`, `elliptic`, `shafts`, `pole`, `bench`) are
the running gear every carriage is built from."""
import math
from kit import item, box, rod, lathe, loft, sphere, ring, sweep, plate, use, write, across, arc, hole, hinge, piece, cut, region, loft_z

C = "modern/components/"
ERA = "1750-1910"


# ---- COMPONENTS -----------------------------------------------------------------------------------------------------
def carriage_wheel():
    # A CARRIAGE WHEEL (a coach's, a cab's, a gig's): `r` the tyre's outer radius, `n` the spokes, `w` the tyre's
    # width, `f` the felloe's depth; the spokes are DISHED -- they lean out from the nave to the felloe (`dish`), so the
    # wheel is a shallow cone, its outside at +z. The axle along z.
    return item("Carriage wheel", "components",
        "a dished carriage wheel: tapered spokes from the turned nave to the wooden felloe, the iron tyre shrunk on, iron bands and a brass cap on the nave -- the axle along z, the outside at +z",
        {"cwood": "#8a2a22", "ciron": "#2b2a28", "ccap": "brass"}, [
            lathe("tyre", "ciron", [["r - 0.012", "-w / 2"], ["r", "-w / 2"], ["r", "w / 2"], ["r - 0.012", "w / 2"], ["r - 0.012", "-w / 2"]], [0, 0, 0, 0, 90, 0], caps=False, sides=36),
            lathe("felloe", "cwood", [["r - 0.012 - f", "-w * 0.42"], ["r - 0.011", "-w * 0.42"], ["r - 0.011", "w * 0.42"], ["r - 0.012 - f", "w * 0.42"], ["r - 0.012 - f", "-w * 0.42"]], [0, 0, 0, 0, 90, 0], caps=False, sides=36),
            rod("spoke", "cwood", 0.018, ["hr * 0.85", 0, "-dish"], ["r - f", 0, 0], 6, r0="sr * 1.25", r1="sr * 0.8", around={"n": "n", "r": 0, "plane": "xy"}),
            lathe("nave", "cwood", [[0, "-hl * 0.5 - dish"], ["hr * 0.72", "-hl * 0.5 - dish"], ["hr", "-hl * 0.18 - dish"], ["hr", "hl * 0.05 - dish"], ["hr * 0.78", "hl * 0.32 - dish"], ["hr * 0.6", "hl * 0.5 - dish"], [0, "hl * 0.5 - dish"]], [0, 0, 0, 0, 90, 0], sides=14),
            ring("band", "ciron", "hr * 0.98", "hr * 0.08", [0, 0, "-hl * 0.18 - dish", 0, 90, 0], sides=6),
            ring("band2", "ciron", "hr * 0.7", "hr * 0.08", [0, 0, "hl * 0.4 - dish", 0, 90, 0], sides=6),
            lathe("cap", "ccap", [[0, "hl * 0.5 - dish"], ["hr * 0.55", "hl * 0.5 - dish"], ["hr * 0.5", "hl * 0.62 - dish"], ["hr * 0.3", "hl * 0.68 - dish"], [0, "hl * 0.69 - dish"]], [0, 0, 0, 0, 90, 0], sides=12),
        ], params={"r": 0.7, "n": 14, "w": 0.055, "f": 0.07, "sr": 0.018, "hr": 0.1, "hl": 0.3, "dish": 0.035}, era=ERA)


def carriage_lamp():
    # A CARRIAGE LAMP: a square lantern (a candle behind bevelled glass) on a bracket, its back on the body at the
    # origin and its face at +x, its roof a little pyramid with a chimney -- the coach's, the cab's, the gig's
    return item("Carriage lamp", "components",
        "a carriage lamp: a square glazed lantern with its reflector, a pyramid roof and chimney, on a bracket from the body -- facing +x",
        {"lbody": "#1d1d1f", "lglass": "lamp", "lmetal": "brass"}, [
            box("lantern", "lbody", [0.16, 0.22, 0.16], [0.12, 0, 0]),
            box("glass", "lglass", [0.012, 0.16, 0.12], [0.205, 0, 0]),
            box("glassSide", "lglass", [0.1, 0.14, 0.012], [0.12, 0.01, 0.085], mirror="z"),
            lathe("roof", "lbody", [[0.13, 0], [0.05, 0.08], [0.03, 0.08], [0.03, 0.13], [0.045, 0.14], [0, 0.15]], [0.12, 0.11, 0, 45, 0, 0], sides=4),
            rod("bracket", "lmetal", 0.012, [0, -0.06, 0], [0.06, -0.06, 0], 6),
            box("socket", "lmetal", [0.05, 0.1, 0.05], [0.12, -0.15, 0]),
            ring("bezel", "lmetal", 0.07, 0.008, [0.213, 0, 0, 0, 0, 90], sides=6),
        ], params={}, era=ERA)


# ---- RUNNING GEAR ---------------------------------------------------------------------------------------------------
def wheels(id_, x, r, track, n=14, w=0.055, f=0.07, hr=0.1, hl=0.3, sr=0.018):
    """(a pair of carriage wheels on one axle, both outsides out)"""
    return use(id_, C + "carriage-wheel", [x, r, track / 2], {"r": r, "n": n, "w": w, "f": f, "hr": hr, "hl": hl, "sr": sr}, {"cwood": "gear", "ciron": "iron", "ccap": "brass"}, mirror="z")


def axle(id_, x, y, track, bed=0.12, mat="gear"):
    """AN AXLE: the iron arm across between the naves, and the wooden bed over it"""
    return [rod(id_, "iron", 0.03, [x, y, -track / 2], [x, y, track / 2], 8),
            box(id_ + "Bed", mat, [0.12, bed, track - 0.36], [x, y + 0.03 + bed / 2, 0])]


def elliptic(id_, x, y, z, L, h, mat="iron", mirror="z"):
    """AN ELLIPTIC SPRING (the carriage's from ~1805): two leaf-spring arcs, the lower bowed down onto the axle, the upper
    bowed up under the body, joined at their eyes; its foot at y, its head at y + h, L long along x"""
    lo = [[x + L / 2 * math.cos(math.radians(a)), y + h / 2 + h / 2 * math.sin(math.radians(a)), z] for a in range(180, 361, 30)]
    hi = [[x + L / 2 * math.cos(math.radians(a)), y + h / 2 + h / 2 * math.sin(math.radians(a)), z] for a in range(0, 181, 30)]
    k = {"mirror": mirror} if mirror else {}
    return [sweep(id_ + "Lo", mat, lo, None, section=[0.03, 0.05], up=[0, 0, 1], seg=2, **k),
            sweep(id_ + "Hi", mat, hi, None, section=[0.03, 0.05], up=[0, 0, 1], seg=2, **k),
            box(id_ + "Clip", mat, [0.08, 0.05, 0.07], [[x, y + 0.02, z], [x, y + h - 0.02, z]], **k)]


def shafts(id_, x0, y0, z0, x1, y1, z1, mat="gear", r=0.035):
    """A PAIR OF SHAFTS (one horse between them): from the carriage's front at x0 forward to their tips at x1, closing
    in from z0 to z1 and curving up a little, the crossbar (and its swingletree) behind the horse"""
    xm, ym = x0 + (x1 - x0) * 0.55, (y0 + y1) / 2 + 0.06
    return [sweep(id_, mat, [[x0, y0, z0], [xm, ym, (z0 + z1) / 2 + 0.02], [x1, y1, z1]], None, radii=[r, r * 0.95, r * 0.7], seg=5, mirror="z"),
            sphere(id_ + "Tip", "iron", r * 0.9, [x1, y1, z1], sides=6, mirror="z"),
            box(id_ + "Bar", mat, [0.07, 0.07, 2 * z0], [x0 + 0.35, y0 + 0.02, 0]),
            rod(id_ + "Swingle", mat, 0.025, [x0 + 0.46, y0 + 0.02, -0.33], [x0 + 0.46, y0 + 0.02, 0.33], 6),
            ring(id_ + "Tug", "iron", 0.05, 0.008, [xm, ym + 0.03, (z0 + z1) / 2 + 0.02, 0, 0, 90], sides=4, mirror="z")]


def pole(id_, x0, y0, x1, y1, bars=1, mat="gear"):
    """A POLE (a pair or a team): from the front axle forward to the neck yoke at x1; the splinter bar across the front
    of the carriage, `bars` the evener and its swingletrees for each pair"""
    out = [rod(id_, mat, 0.045, [x0, y0, 0], [x1, y1, 0], 8, r0=0.05, r1=0.035),
           box(id_ + "Yoke", mat, [0.07, 0.07, 1.0], [x1 - 0.12, y1 - 0.01, 0]),
           sphere(id_ + "Tip", "iron", 0.04, [x1, y1, 0], sides=6),
           rod(id_ + "Evener", mat, 0.035, [x0 + 0.45, y0 + 0.08, -0.6], [x0 + 0.45, y0 + 0.08, 0.6], 6),
           rod(id_ + "Swingle", mat, 0.025, [x0 + 0.62, y0 + 0.08, -0.3], [x0 + 0.62, y0 + 0.08, 0.3], 6, at=[[0, 0, 0.5], [0, 0, -0.5]])]
    if bars > 1:   # (a team of four: the leaders' bars at the pole's tip)
        out += [rod(id_ + "LeadEvener", mat, 0.03, [x1 + 0.1, y1, -0.6], [x1 + 0.1, y1, 0.6], 6),
                rod(id_ + "LeadSwingle", mat, 0.022, [x1 + 0.25, y1, -0.3], [x1 + 0.25, y1, 0.3], 6, at=[[0, 0, 0.5], [0, 0, -0.5]])]
    return out


def bench(id_, x, y, w, facing=0, d=0.45, back=0.5, cover="seat"):
    """A CARRIAGE SEAT: an upholstered bench w wide on the floor at y, facing +x (0) or -x (180)"""
    return use(id_, C + "seat", [x, y, 0, facing, 0, 0], {"w": w, "d": d, "h": 0.42, "back": back, "headrest": 0, "pedestal": 1}, {"cover": cover, "frame": "inside"})


def lamps(id_, x, y, z, yaw=0):
    return use(id_, C + "carriage-lamp", [x, y, z, yaw, 0, 0], None, {"lbody": "black", "lglass": "lamp", "lmetal": "brass"}, mirror="z")


MATS = {"iron": "#2b2a28", "brass": "brass", "black": "#19191a", "lamp": "lamp", "leather": "leather-dark", "inside": "#3a2a20"}


# ---- THE CARRIAGES --------------------------------------------------------------------------------------------------
def stagecoach():
    # A CONCORD STAGECOACH (Abbot-Downing, Concord N.H., 1827-1900; the American West's mail coach): the egg-shaped body
    # hung on two leather THOROUGHBRACES slung between iron jacks on the axles; nine inside (three benches, the middle
    # one a jump seat with a strap back), the driver and a passenger on the box at the front over the front boot, the
    # leather-covered rear boot, luggage on the railed roof; rear wheels 1.52 m, front 1.12 m on a 1.57 m track; the
    # pole for a team of four (the leaders' bars at its tip). Body ~2.3 m long, the roof 2.4 m up.
    rr, rf, tr = 0.76, 0.56, 1.57
    xr, xf = -1.05, 1.15
    body = [[-1.15, 0.56, 1.28, 2.22, 0.6], [-0.95, 0.66, 1.02, 2.33, 0.66], [-0.4, 0.69, 0.92, 2.37, 0.67], [0.4, 0.69, 0.92, 2.37, 0.67], [0.85, 0.66, 1.02, 2.33, 0.66], [1.05, 0.56, 1.28, 2.22, 0.6]]
    win = [hole(0.45, 0.8, 1.7, 2.14), hole(-0.8, -0.45, 1.7, 2.14)]
    BODY = loft("body", "paint", body, [0.18, 0.07], holes=win, double=True, seg=4, corner=4)
    dX, dY = (-0.36, 0.36), (1.12, 2.22)                 # (the door: hinged at its rear edge, its window let down)
    zs = lambda x, y: loft_z(body, [0.18, 0.07], x, y)
    parts = [
        wheels("rear", xr, rr, tr, n=16, w=0.065, f=0.08, hr=0.11, hl=0.34, sr=0.021),
        wheels("front", xf, rf, tr, n=12, w=0.065, f=0.075, hr=0.1, hl=0.32, sr=0.019),
        *axle("rearAxle", xr, rr, tr), *axle("frontAxle", xf, rf, tr),
        ring("fifth", "iron", 0.42, 0.02, [xf, rf + 0.2, 0], sides=6),
        sweep("reach", "gear", [[xf, rf + 0.12, 0], [0, 0.78, 0], [xr, rr + 0.12, 0]], None, section=[0.09, 0.11], up=[0, 1, 0], seg=3),
        # (the jacks: iron standards rising from the axle beds, and the THOROUGHBRACES slung between them under the body)
        sweep("jackF", "iron", [[xf, rf + 0.15, 0.48], [xf - 0.15, rf + 0.45, 0.48], [0.92, 1.36, 0.48]], 0.025, seg=3, mirror="z"),
        sweep("jackR", "iron", [[xr, rr + 0.15, 0.48], [xr + 0.08, rr + 0.45, 0.48], [-0.92, 1.48, 0.48]], 0.025, seg=3, mirror="z"),
        sweep("brace", "leather", [[0.92, 1.38, 0.48], [0.6, 1.02, 0.48], [0, 0.86, 0.48], [-0.6, 1.0, 0.48], [-0.92, 1.5, 0.48]], None, section=[0.07, 0.11], up=[0, 0, 1], seg=4, mirror="z"),
        # (the body: its curved panels, the quarter windows open; THE DOORS cut from it, hinged at their rear edge (the
        #  rear wheel just clear below), each with its window let down, the belt, the handle, a leather lining inside)
        cut(BODY, [region(*dX, *dY, "both")]),
        hinge("door", [dX[0], 1.6, zs(dX[0], 1.6) - 0.01], [
            piece(BODY, [region(*dX, *dY)], "skin", holes=[region(-0.26, 0.26, 1.66, 2.12)]),
            sweep("doorBelt", "trim", [[dX[0] + 0.01, 1.6, zs(dX[0], 1.6) + 0.005], [dX[1] - 0.01, 1.6, zs(dX[1], 1.6) + 0.005]], 0.014, seg=1),
            box("handle", "brass", [0.08, 0.02, 0.02], [0.26, 1.5, zs(0.26, 1.5) + 0.015]),
            box("doorLining", "leather", [0.62, 0.42, 0.02], [0, 1.36, zs(0, 1.36) - 0.03]),
            box("glassTop", "glass", [0.5, 0.02, 0.012], [0, 1.655, zs(0, 1.65) - 0.015]),
            box("strapPull", "leather", [0.05, 0.22, 0.01], [0, 1.52, zs(0, 1.52) - 0.045]),
        ], max_=-85, mirror="z"),
        box("floor", "inside", [1.95, 0.04, 1.25], [-0.05, 0.98, 0]),
        bench("rearSeat", -0.8, 1.0, 1.15, 0),
        bench("frontSeat", 0.7, 1.0, 1.15, 180),
        box("jumpSeat", "seat", [0.36, 0.08, 1.15], [0.0, 1.38, 0]),
        box("strap", "leather", [0.03, 0.12, 1.2], [-0.12, 1.75, 0]),
        sweep("belt", "trim", [[-0.95, 1.6, 0.665], [-0.65, 1.6, 0.685], [dX[0] - 0.01, 1.6, zs(dX[0], 1.6) + 0.005]], 0.014, seg=3, mirror="z"),
        sweep("beltF", "trim", [[dX[1] + 0.01, 1.6, zs(dX[1], 1.6) + 0.005], [0.6, 1.6, 0.685], [0.85, 1.6, 0.665]], 0.014, seg=3, mirror="z"),
        sweep("curtain", "leather", [[-0.8, 2.17, 0.67], [-0.45, 2.17, 0.67]], 0.035, seg=1, at=[[0, 0, 0], [1.25, 0, 0]], mirror="z"),
        # (the roof's railing and its luggage)
        box("roofRail", "black", [1.9, 0.02, 0.02], [-0.05, 2.62, 0.6], mirror="z"),
        box("roofRailEnd", "black", [0.02, 0.02, 1.2], [[0.9, 2.62, 0], [-1.0, 2.62, 0]]),
        rod("railPost", "black", 0.01, [0, 2.36, 0], [0, 2.62, 0], 4, along={"n": 6, "from": [-1.0, 0, 0.6], "to": [0.9, 0, 0.6]}, mirror="z"),
        box("trunk", "trunk", [0.8, 0.42, 0.5], [-0.45, 2.58, 0.25]),
        box("trunkBand", "iron", [0.03, 0.43, 0.51], [[-0.7, 2.58, 0.25], [-0.2, 2.58, 0.25]]),
        box("trunk2", "trunk2", [0.6, 0.3, 0.45], [0.25, 2.52, -0.3, 8, 0, 0]),
        sphere("bag", "bag", 0.18, [-0.6, 2.5, -0.35], stretch=[1.6, 0.9, 1.0], sides=10),
        # (the driver's box: the seat on the front boot, its iron rail, the sloping footboard, the brake lever)
        box("frontBoot", "leather", [0.45, 0.92, 1.25], [1.25, 1.83, 0]),
        box("boxSeat", "seat", [0.42, 0.12, 1.35], [1.2, 2.34, 0]),
        box("boxBack", "seat", [0.06, 0.3, 1.35], [0.98, 2.52, 0]),
        sweep("boxRail", "iron", [[1.0, 2.42, 0.7], [1.0, 2.62, 0.7], [1.4, 2.6, 0.7]], 0.012, seg=2, mirror="z"),
        box("footboard", "gear", [0.42, 0.04, 1.3], [1.68, 1.72, 0]),
        box("toeboard", "gear", [0.3, 0.04, 1.3], [1.93, 1.82, 0, 0, 0, 55]),
        rod("footIron", "iron", 0.015, [1.48, 1.45, 0.62], [1.88, 1.72, 0.62], 6, mirror="z"),
        rod("brake", "iron", 0.018, [1.25, 1.45, 0.72], [1.4, 2.4, 0.74], 6),
        box("brakeBlock", "gear", [0.12, 0.1, 0.08], [xr + 0.62, rr + 0.18, 0.78], mirror="z"),
        rod("brakeBar", "iron", 0.02, [xr + 0.62, rr + 0.18, -0.78], [xr + 0.62, rr + 0.18, 0.78], 6),
        # (the rear boot: a platform on the irons behind, its leather apron buckled down over the bags)
        box("bootDeck", "gear", [0.5, 0.05, 1.2], [-1.4, 1.36, 0]),
        box("bootApron", "leather", [0.5, 0.65, 1.22], [-1.38, 1.7, 0, 0, 0, 12]),
        rod("bootIron", "iron", 0.015, [-1.15, 1.6, 0.58], [-1.65, 1.36, 0.58], 6, mirror="z"),
        rod("bootChain", "iron", 0.008, [-1.15, 2.1, 0.58], [-1.63, 1.4, 0.58], 4, mirror="z"),
        lamps("lamp", 1.0, 1.95, 0.66),
        *pole("pole", xf + 0.1, rf + 0.05, xf + 3.3, 1.0, bars=2),
    ]
    return item("Stagecoach", "carriage",
        "a Concord stagecoach (Abbot-Downing, 1827-1900): the egg-shaped body on two leather thoroughbraces slung between iron jacks, three benches inside for nine (seen through the quarters' and the doors' let-down windows; the doors hinged at their rear edge and opening), the driver's box over the front boot with its footboard and brake, the railed roof with trunks, the leather rear boot; dished wheels 1.52 m and 1.12 m on a 1.57 m track; the pole for a team of four, ~2.3 m body, 2.6 m over the luggage",
        {"paint": {"pick": ["#8c1f1c", "#2f4f36", "#20304f", "#7a1d2a"]}, "trim": "#d8b34a", "gear": {"pick": ["#d7a62a", "#c99a2a"]}, "seat": "leather",
         "trunk": "#5a3a22", "trunk2": "#384b5a", "bag": "#6b4b2a", "glass": "window-glass", **MATS}, parts, params={"open": 0},
        markers=[{"role": "seat", "at": [1.2, 2.42, -0.3], "data": {"face": 0}}, {"role": "seat", "at": [-0.8, 1.42, 0], "data": {"face": 0}}],
        era="1827-1910", region="North America")


def brougham():
    # A BROUGHAM (Lord Brougham's, 1838; every doctor's and town gentleman's until the motor car): a low closed body for
    # two, its front glass looking out over the horse, a door each side with a drop window, the coachman on a box out in
    # front on the fore-carriage; elliptic springs; front wheels 1.0 m, rear 1.2 m on a 1.4 m track; shafts for one
    # horse. Its doors are hinged at their front edge (set a little forward of the old place, so the rear one clears the
    # rear wheel as it swings), each with its drop window let down.
    rr, rf, tr = 0.6, 0.5, 1.42
    xr, xf = -0.85, 0.98
    body = [[-1.02, 0.52, 1.08, 1.92, 0.5], [-0.88, 0.62, 0.9, 2.0, 0.58], [0.3, 0.62, 0.88, 2.02, 0.58], [0.56, 0.6, 1.0, 1.98, 0.56]]
    BODY = loft("body", "paint", body, [0.12, 0.08], holes=[hole(-0.82, -0.62, 1.42, 1.78)], double=True, seg=4, corner=4)
    zb = lambda x, y: loft_z(body, [0.12, 0.08], x, y)
    dX, dY, wX, wY = (-0.32, 0.34), (0.92, 1.82), (-0.22, 0.24), (1.38, 1.76)
    parts = [
        wheels("rear", xr, rr, tr, n=14, w=0.045, f=0.06, hr=0.09, hl=0.28, sr=0.016),
        wheels("front", xf, rf, tr, n=12, w=0.045, f=0.055, hr=0.085, hl=0.26, sr=0.015),
        rod("rearAxle", "iron", 0.028, [xr, rr, -tr / 2], [xr, rr, tr / 2], 8),
        rod("frontAxle", "iron", 0.028, [xf, rf, -tr / 2], [xf, rf, tr / 2], 8),
        *elliptic("springR", xr, rr + 0.03, 0.5, 0.95, 0.28),
        *elliptic("springF", xf, rf + 0.03, 0.42, 0.85, 0.25),
        box("bolsterF", "gear", [0.12, 0.08, 1.0], [xf, rf + 0.32, 0]),
        ring("fifth", "iron", 0.35, 0.018, [xf, rf + 0.37, 0], sides=6),
        # (the body: the doors' openings, the quarter lights behind; THE DOORS cut from it, hinged at their front edge, the
        #  drop window let down into each (its glass's top edge at the sill, the strap to pull it up), the belt, the
        #  handle, the cushioned lining and its pull inside)
        cut(BODY, [region(*dX, *dY, "both")]),
        hinge("door", [dX[1], 1.36, zb(dX[1], 1.36) - 0.01], [
            piece(BODY, [region(*dX, *dY)], "skin", holes=[region(*wX, *wY)]),
            sweep("doorBelt", "trim", [[dX[0] + 0.01, 1.36, zb(dX[0], 1.36) + 0.005], [dX[1] - 0.01, 1.36, zb(dX[1], 1.36) + 0.005]], 0.012, seg=1),
            box("handle", "brass", [0.08, 0.02, 0.02], [-0.24, 1.3, zb(-0.24, 1.3) + 0.012]),
            box("glassTop", "glass", [0.44, 0.02, 0.01], [0.01, 1.39, zb(0.01, 1.39) - 0.012]),
            box("strap", "leather", [0.05, 0.2, 0.008], [0.01, 1.3, zb(0.01, 1.3) - 0.02]),
            box("doorLining", "cushion", [0.58, 0.4, 0.02], [0.01, 1.14, zb(0.01, 1.14) - 0.025]),
            box("doorPull", "trim", [0.2, 0.025, 0.03], [0.01, 1.2, zb(0.01, 1.2) - 0.05]),
        ], max_=72, mirror="z"),
        box("upper", "upper", [1.62, 0.03, 1.26], [-0.22, 2.0, 0]),
        box("frontGlass", "glass", [0.02, 0.5, 0.86], [0.565, 1.6, 0]),
        box("frontGlassFrame", "upper", [0.03, 0.04, 0.92], [[0.57, 1.86, 0], [0.57, 1.34, 0]]),
        box("floor", "inside", [1.3, 0.04, 1.15], [-0.25, 0.95, 0]),
        box("carpet", "carpet", [0.5, 0.01, 1.1], [0.1, 0.975, 0]),
        bench("seat", -0.68, 0.95, 1.1, 0, d=0.5, back=0.55, cover="cushion"),
        box("lining", "cushion", [0.02, 0.85, 1.1], [-0.93, 1.45, 0]),
        sweep("belt", "trim", [[-0.88, 1.36, zb(-0.88, 1.36) + 0.005], [dX[0] - 0.01, 1.36, zb(dX[0], 1.36) + 0.005]], 0.012, seg=1, mirror="z"),
        sweep("beltF", "trim", [[dX[1] + 0.01, 1.36, zb(dX[1], 1.36) + 0.005], [0.56, 1.36, 0.61]], 0.012, seg=1, mirror="z"),
        box("step", "iron", [0.2, 0.02, 0.14], [-0.15, 0.62, 0.72], mirror="z"),
        rod("stepIron", "iron", 0.01, [-0.15, 0.62, 0.66], [-0.15, 0.9, 0.62], 4, mirror="z"),
        # (the coachman's box: its seat on a frame over the fore-carriage, the curved leather dash, the footboard)
        box("boxFrame", "upper", [0.6, 0.38, 0.9], [0.85, 1.3, 0]),
        box("boxSeat", "seat2", [0.4, 0.1, 1.0], [0.85, 1.54, 0]),
        box("boxCloth", "upper", [0.04, 0.35, 1.0], [1.06, 1.38, 0]),
        box("footboard", "upper", [0.4, 0.04, 0.95], [1.28, 1.15, 0, 0, 0, -15]),
        sweep("dash", "leather", [[1.42, 1.1, 0], [1.5, 1.35, 0], [1.6, 1.55, 0]], None, section=[0.02, 1.0], up=[0, 0, 1], seg=3),
        sweep("dashIron", "iron", [[1.42, 1.08, 0.5], [1.5, 1.35, 0.5], [1.6, 1.56, 0.5]], 0.008, seg=3, mirror="z"),
        lamps("lamp", 0.56, 1.65, 0.62),
        *shafts("shaft", xf - 0.1, rf + 0.42, 0.56, 3.75, 1.02, 0.33),
    ]
    return item("Brougham", "carriage",
        "a brougham (1838-1910): the low closed body for two on elliptic springs, its front glass, a door each side hinged at its front edge, its drop window let down, opening on the upholstered seat and carpet -- the coachman's box with the curved leather dash out in front over the fore-carriage, lamps, dished wheels 1.0 m and 1.2 m on a 1.42 m track; shafts for one horse",
        {"paint": {"pick": ["#1c2a3a", "#2a1a1c", "#1d2d22", "#3a1a22"]}, "upper": "#141416", "trim": "#9a7b3a", "gear": {"pick": ["#1c1c1e", "#7a1e1a", "#2a3a2a"]},
         "glass": "glass", "cushion": {"pick": ["upholstery-grey", "#4a3c5a", "#3c4a5a", "upholstery-red"]}, "carpet": "#4a2a2a", "seat": "leather-dark", "seat2": "#2a2c38", **MATS, "glass": "window-glass"}, parts, params={"open": 0},
        markers=[{"role": "seat", "at": [0.85, 1.6, 0], "data": {"face": 0}}, {"role": "seat", "at": [-0.68, 1.37, 0], "data": {"face": 0}}],
        era="1838-1910", region="Europe, North America")


def hansom():
    # A HANSOM CAB (Joseph Hansom, 1834; London's two-seater cab to the 1920s): two big wheels (1.65 m) on a cranked axle
    # that dips under the low body, the body open at the front behind two low folding doors, the seat for two inside,
    # the driver up behind on his dickey seat over the roof, the reins over it; the long shafts running under the body
    # for one horse; lamps at the front corners.
    r, tr = 0.82, 1.62
    body = [[-0.62, 0.58, 0.6, 2.02, 0.55], [-0.45, 0.64, 0.48, 2.08, 0.6], [0.12, 0.64, 0.48, 2.08, 0.6], [0.3, 0.62, 0.55, 2.04, 0.58]]
    parts = [
        wheels("wheel", 0.05, r, tr, n=14, w=0.045, f=0.06, hr=0.095, hl=0.28, sr=0.017),
        # (the cranked axle: out from the naves, down under the body, across)
        sweep("axle", "iron", [[0.05, r, 0.78], [0.05, r, 0.7], [0.05, 0.35, 0.62], [0.05, 0.3, 0.0], [0.05, 0.35, -0.62], [0.05, r, -0.7], [0.05, r, -0.78]], 0.03, seg=2),
        *elliptic("spring", 0.05, 0.32, 0.45, 0.8, 0.16),
        loft("body", "paint", body, [0.12, 0.1], holes=[hole(-0.42, -0.05, 1.48, 1.86)], caps=[True, False], double=True, seg=3, corner=4),
        box("floor", "inside", [0.85, 0.04, 1.15], [-0.15, 0.52, 0]),
        bench("seat", -0.3, 0.52, 1.05, 0, d=0.42, back=0.6, cover="cushion"),
        box("roof", "paint", [1.05, 0.05, 1.3], [-0.12, 2.08, 0]),
        box("frontGlassHead", "upper", [0.06, 0.12, 1.2], [0.3, 1.98, 0]),
        # (THE FOLDING DOORS across the front, knee-high, each hinged at the body's side and folding forward and out over
        #  the shaft (95 deg: clear of it); the step on the shaft)
        hinge("door", [0.34, 0.985, 0.6], [
            box("leaf", "paint", [0.04, 0.57, 0.58], [0.34, 0.985, 0.305]),
            box("doorTop", "trim", [0.05, 0.03, 0.59], [0.34, 1.285, 0.305]),
            box("doorPad", "cushion", [0.012, 0.36, 0.48], [0.315, 1.0, 0.31]),
            box("doorHinge", "brass", [0.03, 0.08, 0.03], [[0.34, 0.8, 0.6], [0.34, 1.17, 0.6]]),
        ], max_=-95, mirror="z"),
        box("step", "iron", [0.22, 0.02, 0.18], [0.55, 0.42, 0.5], mirror="z"),
        sweep("guard", "upper", [[0.05 + (r + 0.05) * math.cos(math.radians(q)), r + (r + 0.05) * math.sin(math.radians(q)), 0.72] for q in range(150, 59, -15)], None, section=[0.02, 0.14], up=[0, 0, 1], seg=2, mirror="z"),
        # (the driver's dickey: high behind the roof on its iron bracket, his footboard)
        box("dickey", "seat", [0.35, 0.12, 0.6], [-0.82, 2.18, 0]),
        box("dickeyBack", "upper", [0.05, 0.25, 0.6], [-1.0, 2.35, 0]),
        sweep("dickeyIron", "iron", [[-0.62, 1.6, 0.25], [-0.82, 1.9, 0.25], [-0.85, 2.12, 0.25]], 0.018, seg=3, mirror="z"),
        box("dickeyFoot", "upper", [0.3, 0.03, 0.5], [-0.82, 1.35, 0, 0, 0, 10]),
        rod("dickeyFootIron", "iron", 0.012, [-0.62, 1.2, 0.2], [-0.92, 1.35, 0.2], 4, mirror="z"),
        rod("reinRail", "brass", 0.008, [-0.7, 2.14, 0.4], [0.3, 2.14, 0.4], 4, mirror="z"),
        lamps("lamp", 0.3, 1.6, 0.62),
        # (the shafts run the length of the body under it, out to the horse)
        sweep("shaftUnder", "gear", [[-0.75, 0.55, 0.6], [0.3, 0.55, 0.62]], 0.035, seg=1, mirror="z"),
        *shafts("shaft", 0.3, 0.55, 0.62, 3.2, 1.05, 0.33),
    ]
    return item("Hansom cab", "carriage",
        "a hansom cab (1834-1920s): the low two-seater body on two 1.65 m wheels and a cranked axle, open in front behind two low folding doors on the seat inside, the driver's dickey high behind the roof with its iron bracket and footboard, a rail for the reins, lamps, mudguards; the long shafts running under the body for one horse",
        {"paint": {"pick": ["#1d1d22", "#1c2a3a", "#28331f", "#3a1c1c"]}, "upper": "#151517", "trim": "#9a7b3a", "gear": {"pick": ["#1c1c1e", "#5a1a16"]}, "seat": "leather-dark",
         "cushion": {"pick": ["upholstery-red", "#3c4a5a", "#5a4632"]}, **MATS}, parts, params={"open": 0},
        markers=[{"role": "seat", "at": [-0.82, 2.25, 0], "data": {"face": 0}}, {"role": "seat", "at": [-0.3, 0.94, 0], "data": {"face": 0}}],
        era="1834-1925", region="Europe")


def gig():
    # A GIG (the light two-wheeler for one horse, ~1780-1910: a doctor's, a farmer's, a dandy's): a seat for two on a
    # small box body, slung on springs over the axle, the curved dash in front of the footboard, the lazy-back rail,
    # 1.45 m wheels, the shafts running under the body, a lamp each side.
    r, tr = 0.72, 1.5
    parts = [
        wheels("wheel", 0.0, r, tr, n=14, w=0.04, f=0.055, hr=0.085, hl=0.26, sr=0.015),
        rod("axle", "iron", 0.026, [0, r, -tr / 2], [0, r, tr / 2], 8),
        *elliptic("spring", 0.0, r + 0.03, 0.5, 0.75, 0.22),
        sweep("shaftUnder", "gear", [[-0.85, r + 0.25, 0.55], [0.5, r + 0.25, 0.55]], 0.035, seg=1, mirror="z"),
        *shafts("shaft", 0.5, r + 0.25, 0.55, 3.2, 1.05, 0.33),
        box("crossbar", "gear", [0.06, 0.06, 1.12], [-0.85, r + 0.25, 0]),
        # (the body: a box with panelled sides, its seat and cushion, the lazy-back)
        box("body", "paint", [0.8, 0.4, 1.0], [-0.1, r + 0.5, 0]),
        box("panel", "trim", [0.7, 0.3, 0.012], [-0.1, r + 0.5, 0.505], mirror="z"),
        box("cushion", "cushion", [0.48, 0.1, 1.0], [-0.12, r + 0.75, 0]),
        sweep("lazyBack", "iron", [[-0.4, r + 0.72, 0.52], [-0.48, r + 1.0, 0.52], [-0.46, r + 1.08, 0.3], [-0.46, r + 1.08, -0.3], [-0.48, r + 1.0, -0.52], [-0.4, r + 0.72, -0.52]], 0.012, seg=3),
        box("backPad", "cushion", [0.05, 0.25, 0.75], [-0.47, r + 0.98, 0, 0, 0, 10]),
        sweep("seatRail", "iron", [[-0.3, r + 0.72, 0.52], [-0.3, r + 0.9, 0.53], [0.1, r + 0.88, 0.53]], 0.01, seg=2, mirror="z"),
        # (the footboard and the curved dash)
        box("floor", "gear", [0.6, 0.04, 0.95], [0.6, r + 0.3, 0]),
        sweep("dash", "leather", [[0.88, r + 0.3, 0], [0.98, r + 0.55, 0], [1.1, r + 0.78, 0]], None, section=[0.02, 0.95], up=[0, 0, 1], seg=3),
        sweep("dashIron", "iron", [[0.88, r + 0.28, 0.48], [0.98, r + 0.55, 0.48], [1.1, r + 0.8, 0.48]], 0.008, seg=3, mirror="z"),
        box("step", "iron", [0.16, 0.02, 0.12], [0.3, 0.45, 0.65], mirror="z"),
        rod("stepIron", "iron", 0.01, [0.3, 0.45, 0.62], [0.35, r + 0.25, 0.56], 4, mirror="z"),
        lamps("lamp", 0.3, r + 0.6, 0.52),
        sweep("whip", "black", [[0.25, r + 0.72, 0.5], [0.4, r + 1.6, 0.6], [0.9, r + 2.2, 0.7]], None, radii=[0.012, 0.008, 0.003], seg=4),
        rod("whipSocket", "black", 0.02, [0.24, r + 0.55, 0.5], [0.26, r + 0.8, 0.5], 6),
    ]
    return item("Gig", "carriage",
        "a gig (~1780-1910): the light two-wheeler for one horse -- a box body with its seat for two and the lazy-back rail, slung on springs over the axle; the curved leather dash, the footboard, a whip in its socket, lamps; 1.45 m wheels on a 1.5 m track, the shafts running under the body",
        {"paint": {"pick": ["#c9a64a", "#20304f", "#5a1a16", "#1d2d22", "#1c1c1e"]}, "trim": "#1c1c1e", "gear": {"pick": ["#7a1e1a", "#1c1c1e", "#c9a64a"]}, "cushion": {"pick": ["upholstery-red", "#3c4a5a", "#5a4632", "leather"]}, **MATS}, parts,
        markers=[{"role": "seat", "at": [-0.12, r + 0.8, -0.25], "data": {"face": 0}}, {"role": "seat", "at": [-0.12, r + 0.8, 0.25], "data": {"face": 0}}],
        era="1780-1910", region="Europe, North America")


def omnibus():
    # A KNIFEBOARD OMNIBUS (London General, ~1850-1890): a box body 3.4 m long for twelve inside on two long benches
    # facing each other under the windows, the open platform and the door at the rear, the iron steps and rungs up to
    # the roof, where ten more sit back to back on the KNIFEBOARD down the middle behind an iron rail; the driver's
    # box at the roof's front; advertisement boards along the sides; wheels 1.0 m and 1.4 m; the pole for a pair.
    rr, rf, tr = 0.7, 0.5, 1.7
    xr, xf = -1.25, 1.2
    y0, y1, hw = 0.85, 2.55, 0.85
    body = [[-1.9, hw, y0, y1, hw - 0.04], [1.0, hw, y0, y1, hw - 0.04]]
    win = [hole(-1.65 + 0.52 * i, -1.65 + 0.52 * i + 0.4, 1.6, 2.2) for i in range(5)]
    parts = [
        wheels("rear", xr, rr, tr, n=16, w=0.07, f=0.08, hr=0.11, hl=0.34, sr=0.022),
        wheels("front", xf, rf, tr, n=12, w=0.065, f=0.07, hr=0.1, hl=0.3, sr=0.019),
        *axle("rearAxle", xr, rr, tr), *axle("frontAxle", xf, rf, tr),
        sweep("springRear", "iron", [[xr - 0.55, y0, 0.55], [xr, rr + 0.17, 0.55], [xr + 0.55, y0, 0.55]], None, section=[0.04, 0.06], up=[0, 0, 1], seg=3, mirror="z"),
        *elliptic("springF", xf, rf + 0.17, 0.5, 0.75, 0.2),
        ring("fifth", "iron", 0.4, 0.02, [xf, rf + 0.4, 0], sides=6),
        # (the body: the windows down both sides, the rear open; the benches inside)
        loft("body", "paint", body, [0.06, 0.05], holes=win, caps=[False, True], double=True, seg=1, corner=3),
        box("floor", "inside", [2.9, 0.04, 1.6], [-0.45, y0 + 0.04, 0]),
        box("benchSeat", "seat", [2.6, 0.08, 0.4], [-0.5, y0 + 0.44, 0.6], mirror="z"),
        box("benchBase", "inside", [2.6, 0.4, 0.3], [-0.5, y0 + 0.22, 0.65], mirror="z"),
        box("benchBack", "seat", [2.6, 0.45, 0.06], [-0.5, y0 + 0.75, 0.78], mirror="z"),
        box("waist", "trim", [2.9, 0.06, 0.02], [-0.45, 1.56, hw + 0.005], mirror="z"),
        box("board", "board", [2.8, 0.3, 0.02], [-0.45, 2.38, hw + 0.01], mirror="z"),
        box("boardText", "boardText", [1.6, 0.12, 0.01], [-0.6, 2.38, hw + 0.025], mirror="z"),
        # (the rear: the platform, the step, the door frame, the iron rungs up the back to the roof)
        box("platform", "gear", [0.5, 0.06, 1.3], [-2.15, y0 - 0.05, 0]),
        box("lowStep", "iron", [0.3, 0.03, 0.5], [-2.3, 0.45, 0.3]),
        box("doorPost", "upper", [0.06, y1 - y0, 0.08], [-1.9, (y0 + y1) / 2, 0.45], mirror="z"),
        rod("rung", "iron", 0.012, [-1.95, 0, 0.55], [-1.95, 0, 0.82], 4, along={"n": 6, "from": [0, 1.0, 0], "to": [0, 2.45, 0]}),
        rod("rungRail", "iron", 0.015, [-1.98, 0.9, 0.82], [-1.98, 2.9, 0.82], 4),
        # (the roof: the knifeboard -- the back-to-back seats down the middle -- the iron rail all round, the driver's
        #  box at the front with its footboard)
        box("roof", "upper", [2.95, 0.04, 2 * hw - 0.02], [-0.45, y1 + 0.02, 0]),
        box("knife", "gear", [2.2, 0.55, 0.05], [-0.65, y1 + 0.32, 0]),
        box("knifeSeat", "seat", [2.2, 0.06, 0.32], [-0.65, y1 + 0.42, 0.2], mirror="z"),
        box("knifeFoot", "gear", [2.2, 0.04, 0.2], [-0.65, y1 + 0.1, 0.62], mirror="z"),
        box("roofRail", "iron", [2.9, 0.02, 0.02], [-0.45, y1 + 0.42, hw - 0.02], mirror="z"),
        rod("roofPost", "iron", 0.01, [0, y1, 0], [0, y1 + 0.42, 0], 4, along={"n": 7, "from": [-1.85, 0, hw - 0.02], "to": [0.95, 0, hw - 0.02]}, mirror="z"),
        box("driverBox", "gear", [0.45, 0.4, 1.2], [0.85, y1 + 0.2, 0]),
        box("driverSeat", "seat", [0.4, 0.1, 1.2], [0.85, y1 + 0.45, 0]),
        box("footboard", "gear", [0.45, 0.04, 1.4], [1.22, y1 - 0.12, 0]),
        box("toeboard", "gear", [0.28, 0.04, 1.4], [1.47, y1 - 0.02, 0, 0, 0, 55]),
        rod("footIron", "iron", 0.015, [1.0, y1 - 0.55, 0.65], [1.42, y1 - 0.13, 0.65], 4, mirror="z"),
        lamps("lamp", 1.0, 2.0, hw - 0.05),
        *pole("pole", xf + 0.1, rf + 0.05, xf + 3.2, 1.0),
    ]
    return item("Horse omnibus", "carriage",
        "a London knifeboard omnibus (~1850-1890): a box body 3 m long for twelve inside on two benches facing each other under five windows a side, the open rear platform and door, iron rungs up to the roof where ten more sit back to back on the knifeboard behind an iron rail, the driver's box at the roof's front, advertisement boards along the sides, lamps; wheels 1.0 m and 1.4 m on a 1.7 m track; the pole for a pair",
        {"paint": {"pick": ["#7a1d1a", "#20304f", "#2f4f36", "#c9a64a"]}, "upper": "#1c1c1e", "trim": "#d8b34a", "gear": {"pick": ["#1c1c1e", "#d7a62a"]}, "seat": "leather-dark",
         "board": "#e2d8b8", "boardText": "#7a1d1a", **MATS}, parts,
        markers=[{"role": "seat", "at": [0.85, y1 + 0.52, 0], "data": {"face": 0}}],
        era="1829-1914", region="Europe")


def write_all():
    write("modern/components/carriage-wheel", carriage_wheel(), "components")
    write("modern/components/carriage-lamp", carriage_lamp(), "components")
    for name, f in [("stagecoach", stagecoach), ("brougham", brougham), ("hansom", hansom), ("gig", gig), ("omnibus", omnibus)]:
        write("modern/carriages/" + name, f(), "carriages")

GROUPS = {"carriages": "carriages", "components": "components"}
