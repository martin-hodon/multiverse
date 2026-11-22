"""THE MACHINES (2026-11-20; docs/modern.md): the building site's and the farm's -- an excavator, a bulldozer, a farm
tractor, a forklift, a tower crane, a concrete mixer truck -- in the vehicle frame (kit.py: the ground under the
machine's middle, +x its front, +z its right). They share the road wheel and the lamp (parts.py) and two components
written here (group "components"): `track` (a crawler track: its links' belt round the sprocket and the idler, the
grousers, the rollers, the frame), `lug-wheel` (a tractor's wheel: the deep tyre with its chevron lugs) and `cab` (a
glazed operator's cab: posts, roof, glass all round, a painted sill, a door's frame).

The helpers (`ram`, `cab`, `lattice_mast`, `lattice_jib`) are the machines' recurring sub-assemblies: a hydraulic
cylinder, the cab component placed by its box, a lattice truss."""
import math
from kit import item, box, rod, lathe, loft, sphere, ring, sweep, plate, use, write, across, arc, hole, ram, region, cr_at, loft_z, arches, body_arches, arch_gap, pan, steer, steer_in, hinge, piece, cut

C = "modern/components/"


# ---- COMPONENTS -----------------------------------------------------------------------------------------------------
def track():
    # A CRAWLER TRACK (an excavator's, a dozer's): its frame in the vehicle's frame -- the ground at y 0, its length
    # along x, centred, the axles along z. `L` over all, `H` its height (the sprocket's and idler's diameter), `w` the
    # shoes' width. The belt of links is one closed sweep round the oval; the grousers (the shoes' cleats) stand on it
    # all the way round; the SPROCKET is at -x (the drive, at the rear of a machine facing +x), the IDLER at +x; road
    # rollers under the frame, two carrier rollers over it.
    a = "L / 2 - H / 2"   # (the half-distance between the sprocket's and the idler's centres)
    n = 18
    path = ([[f"-({a}) + 2 * ({a}) * {i} / 3", 0.035, 0] for i in range(4)]
            + [[f"{a} + (H / 2 - 0.035) * cos({-90 + 180 * k / 8} * 0.0174533)", f"H / 2 + (H / 2 - 0.035) * sin({-90 + 180 * k / 8} * 0.0174533)", 0] for k in range(1, 8)]
            + [[f"{a} - 2 * ({a}) * {i} / 3", "H - 0.035", 0] for i in range(4)]
            + [[f"-({a}) + (H / 2 - 0.035) * cos({90 + 180 * k / 8} * 0.0174533)", f"H / 2 + (H / 2 - 0.035) * sin({90 + 180 * k / 8} * 0.0174533)", 0] for k in range(1, 8)])
    return item("Crawler track", "components",
        "a crawler track: the closed belt of steel shoes round the sprocket (-x) and the idler (+x), their grousers, five road rollers and two carrier rollers, the track frame between -- the ground at y 0, L long, H high, w wide",
        {"tshoe": "#3a3936", "tframe": "paint-yellow", "troller": "#5a5852"}, [
            sweep("belt", "tshoe", path, None, section=[0.06, "w"], up=[0, 0, 1], closed=True, seg=1),
            box("grouserB", "tshoe", [0.05, 0.045, "w"], [0, 0.0225, 0], along={"n": "round(2 * (L / 2 - H / 2) / 0.2) + 1", "from": [f"-({a})", 0, 0], "to": [a, 0, 0]}),
            box("grouserT", "tshoe", [0.05, 0.045, "w"], [0, "H - 0.0225", 0], along={"n": "round(2 * (L / 2 - H / 2) / 0.2) + 1", "from": [f"-({a})", 0, 0], "to": [a, 0, 0]}),
            box("grouserF", "tshoe", [0.05, 0.045, "w"], [a, "H / 2", 0], around={"n": 6, "r": "H / 2 - 0.0225", "plane": "xy", "start": -64, "span": 128}),
            box("grouserR", "tshoe", [0.05, 0.045, "w"], [f"-({a})", "H / 2", 0], around={"n": 6, "r": "H / 2 - 0.0225", "plane": "xy", "start": 116, "span": 128}),
            # (the sprocket: a toothed wheel, its teeth in the links; the idler: a plain wheel with a rim)
            lathe("sprocket", "troller", [[0, "-w * 0.32"], ["H / 2 - 0.1", "-w * 0.32"], ["H / 2 - 0.1", "w * 0.32"], [0, "w * 0.32"]], [f"-({a})", "H / 2", 0, 0, 90, 0], sides=18),
            box("tooth", "troller", [0.07, 0.1, "w * 0.5"], [f"-({a})", "H / 2", 0], around={"n": 12, "r": "H / 2 - 0.09", "plane": "xy"}),
            lathe("hubR", "tframe", [[0, "w * 0.32"], ["H * 0.2", "w * 0.32"], ["H * 0.16", "w * 0.5"], [0, "w * 0.52"]], [f"-({a})", "H / 2", 0, 0, 90, 0], sides=12, mirror="z"),
            lathe("idler", "troller", [[0, "-w * 0.36"], ["H / 2 - 0.12", "-w * 0.36"], ["H / 2 - 0.07", "-w * 0.1"], ["H / 2 - 0.07", "w * 0.1"], ["H / 2 - 0.12", "w * 0.36"], [0, "w * 0.36"]], [a, "H / 2", 0, 0, 90, 0], sides=18),
            lathe("roller", "troller", [[0, "-w * 0.3"], [0.1, "-w * 0.3"], [0.08, "-w * 0.1"], [0.08, "w * 0.1"], [0.1, "w * 0.3"], [0, "w * 0.3"]], [0, 0.17, 0, 0, 90, 0], sides=10, along={"n": 5, "from": [f"-({a}) + 0.45", 0, 0], "to": [f"{a} - 0.45", 0, 0]}),
            lathe("carrier", "troller", [[0, "-w * 0.25"], [0.07, "-w * 0.25"], [0.07, "w * 0.25"], [0, "w * 0.25"]], [0, "H - 0.13", 0, 0, 90, 0], sides=8, along={"n": 2, "from": [f"-({a}) * 0.4", 0, 0], "to": [f"({a}) * 0.4", 0, 0]}),
            # (the track frame: the box beam the rollers hang from, its sloped ends, a guard over the rollers)
            box("frame", "tframe", [f"2 * ({a}) - 0.2", "H - 0.5", "w * 0.62"], [0, "H / 2 + 0.02", 0]),
            box("guard", "tframe", [f"2 * ({a}) - 0.5", 0.12, "w * 0.7"], [0, 0.32, 0]),
        ], params={"L": 4.45, "H": 0.92, "w": 0.6})


def lug_wheel():
    # A TRACTOR'S WHEEL: a deep-walled tyre with its chevron lugs (the bars that bite the soil, each set at an angle,
    # the two halves offset so they meet in a V), on a steel disc rim -- the axle along z, the outside face at +z.
    # `r` the tyre's outer radius, `w` its width, `rim` the rim's share of r, `n` the lugs on each half.
    lug = 0.05
    return item("Lug wheel", "components",
        "a tractor's wheel: the deep tyre, its chevron lugs in two offset rows, the steel disc rim and hub with its nuts -- the axle along z, the outside face at +z",
        {"ltyre": "rubber", "lrim": "paint-yellow", "lhub": "steel"}, [
            lathe("tyre", "ltyre", [["r * rim * 1.01", "-w * 0.46"], ["r * 0.86", "-w / 2"], ["r - w * 0.1", "-w * 0.47"], [f"r - {lug}", "-w * 0.4"], [f"r - {lug}", "w * 0.4"], ["r - w * 0.1", "w * 0.47"], ["r * 0.86", "w / 2"], ["r * rim * 1.01", "w * 0.46"]], [0, 0, 0, 0, 90, 0], caps=False, sides=32),
            sweep("lugR", "ltyre", [[0, f"r - {lug} / 2", 0.02], ["w * 0.42", f"r - {lug} / 2 - w * 0.09", "w * 0.48"]], None, section=[0.07, lug * 1.9], up=[0, 1, 0], seg=1, around={"n": "n", "r": 0, "plane": "xy"}),
            sweep("lugL", "ltyre", [[0, f"r - {lug} / 2", -0.02], ["w * 0.42", f"r - {lug} / 2 - w * 0.09", "-w * 0.48"]], None, section=[0.07, lug * 1.9], up=[0, 1, 0], seg=1, around={"n": "n", "r": 0, "plane": "xy", "start": "180 / n"}),
            lathe("dish", "lrim", [[0, "w * 0.05"], ["r * rim * 0.45", "w * 0.12"], ["r * rim * 0.62", "w * 0.12"], ["r * rim * 0.98", "w * 0.36"], ["r * rim * 1.02", "w * 0.42"], ["r * rim * 1.02", "-w * 0.42"], [0, "-w * 0.42"]], [0, 0, 0, 0, 90, 0], sides=24),
            lathe("hub", "lhub", [[0, "w * 0.3"], ["r * 0.16", "w * 0.12"], ["r * 0.13", "w * 0.3"], [0, "w * 0.34"]], [0, 0, 0, 0, 90, 0], sides=12),
            sphere("nut", "lhub", "r * 0.022", [0, 0, "w * 0.14"], around={"n": 8, "r": "r * 0.22", "plane": "xy"}, sides=6),
        ], params={"r": 0.875, "w": 0.55, "rim": 0.6, "n": 20})


# ---- HELPERS (the machines' recurring sub-assemblies) ----------------------------------------------------------------
def cab_component():
    # A GLAZED OPERATOR'S CAB (an excavator's, a dozer's, a tractor's, a crane's): its origin on the floor under the
    # cab's middle, `hx` long (x), `hy` high, `hz` wide (z) -- four corner posts `post` square, the floor, the head, the
    # roof with its overhang, glass all round from `sill` up (painted panels below it); `door` -1 / 1 draws a door's
    # frame, its bar and handle on the -z / +z side (0: none). Roles: frame, roof, glass, chrome.
    gy = "(sill + hy) / 2"; gh = "hy - sill - 0.06"; dz = "door * (hz / 2 + 0.005)"
    corners = [[f"{sx}hx / 2 {'+' if sx == '-' else '-'} post / 2", "hy / 2", f"{sz}hz / 2 {'+' if sz == '-' else '-'} post / 2"] for sx in "-+" for sz in "-+"]
    corners = [[a.replace("+hx", "hx").replace("+hz", "hz") for a in c] for c in corners]
    return item("Operator's cab", "components", "a machine's glazed operator's cab: four corner posts, the floor, the head and the overhanging roof, glass all round above an optional painted sill, a door's frame on one side -- the origin on its floor's middle",
        {"frame": "paint", "roof": "paint", "glass": "glass", "chrome": "chrome"}, [
            box("post", "frame", ["post", "hy", "post"], corners),
            box("roof", "roof", ["hx + 0.14", 0.09, "hz + 0.14"], [0, "hy + 0.04", 0]),
            box("floor", "frame", ["hx", 0.08, "hz"], [0, 0.04, 0]),
            box("glassF", "glass", [0.02, gh, "hz - post * 2"], ["hx / 2 - 0.03", gy, 0]),
            box("glassB", "glass", [0.02, gh, "hz - post * 2"], ["0.03 - hx / 2", gy, 0]),
            box("glassL", "glass", ["hx - post * 2", gh, 0.02], [0, gy, "0.03 - hz / 2"]),
            box("glassR", "glass", ["hx - post * 2", gh, 0.02], [0, gy, "hz / 2 - 0.03"]),
            box("head", "frame", ["hx", 0.06, "hz"], [0, "hy - 0.03", 0]),
            box("panelF", "frame", [0.04, "sill", "hz"], ["hx / 2 - 0.02", "sill / 2", 0], when="sill"),
            box("panelB", "frame", [0.04, "sill", "hz"], ["0.02 - hx / 2", "sill / 2", 0], when="sill"),
            box("panelS", "frame", ["hx", "sill", 0.04], [[0, "sill / 2", "0.02 - hz / 2"], [0, "sill / 2", "hz / 2 - 0.02"]], when="sill"),
            box("doorFrame", "frame", [0.05, "hy - 0.1", 0.03], [["hx * 0.18 - hx / 2", "hy / 2", dz], ["hx * 0.7 - hx / 2", "hy / 2", dz]], when="door"),
            box("doorBar", "frame", ["hx * 0.52", 0.05, 0.03], ["hx * 0.44 - hx / 2", "max(sill, 0.5 * hy)", dz], when="door"),
            box("doorHandle", "chrome", [0.03, 0.12, 0.03], ["hx * 0.66 - hx / 2", "hy * 0.45", f"{dz} + door * 0.02"], when="door"),
        ], params={"hx": 1.9, "hy": 1.7, "hz": 0.95, "post": 0.07, "sill": 0.0, "door": 0})


def cab(id_, x0, x1, y0, y1, z0, z1, frame="paint", glass="glass", post=0.07, sill=0.0, roof="paint", door=None):
    """A GLAZED OPERATOR'S CAB (C cab) filling the box x0..x1, y0..y1, z0..z1; `door` the side ("left"/"right") its
    frame is drawn on"""
    return [use(id_, C + "cab", [(x0 + x1) / 2, y0, (z0 + z1) / 2], {"hx": x1 - x0, "hy": y1 - y0, "hz": z1 - z0, "post": post, "sill": sill, "door": {"left": -1, "right": 1}.get(door, 0)},
                {k: v for k, v in (("frame", frame), ("roof", roof), ("glass", glass)) if v != k})]   # (a role mapped to itself would hide the parent's own)


def lattice_mast(id_, mat, h, s, step, y0=0.0, r=0.06, rd=0.03):
    """A SQUARE LATTICE MAST (a tower crane's): four chords h high at the corners of an s-wide square, horizontals at
    every `step`, and the diagonals zigzagging up each face (a Warren truss)"""
    n = max(1, round(h / step))
    hs = s / 2
    out = [rod(id_ + "Chord", mat, r, [0, y0, 0], [0, y0 + h, 0], 6, at=[[hs, 0, hs], [hs, 0, -hs], [-hs, 0, hs], [-hs, 0, -hs]])]
    out.append(rod(id_ + "HorX", mat, rd, [-hs, 0, 0], [hs, 0, 0], 4, along={"n": n + 1, "from": [0, y0, 0], "to": [0, y0 + h, 0]}, at=[[0, 0, hs], [0, 0, -hs]]))
    out.append(rod(id_ + "HorZ", mat, rd, [0, 0, -hs], [0, 0, hs], 4, along={"n": n + 1, "from": [0, y0, 0], "to": [0, y0 + h, 0]}, at=[[hs, 0, 0], [-hs, 0, 0]]))
    up = (n + 1) // 2
    for k, (a, b) in enumerate([((-hs, 0), (hs, step)), ((hs, step), (-hs, 2 * step))]):
        cnt = up if k == 0 else n // 2
        if cnt < 1: continue
        # (each face: x faces at z = +-hs, z faces at x = +-hs)
        out.append(rod(f"{id_}DiagX{k}", mat, rd, [a[0], y0 + a[1], 0], [b[0], y0 + b[1], 0], 4, along={"n": cnt, "from": [0, 0, 0], "to": [0, (cnt - 1) * 2 * step, 0]}, at=[[0, 0, hs], [0, 0, -hs]]))
        out.append(rod(f"{id_}DiagZ{k}", mat, rd, [0, y0 + a[1], a[0]], [0, y0 + b[1], b[0]], 4, along={"n": cnt, "from": [0, 0, 0], "to": [0, (cnt - 1) * 2 * step, 0]}, at=[[hs, 0, 0], [-hs, 0, 0]]))
    return out


def lattice_jib(id_, mat, x0, x1, y, hw, h, step, r=0.05, rd=0.025):
    """A TRIANGULAR LATTICE JIB along +x from x0 to x1: two bottom chords at z = +-hw, a top chord h above the middle,
    the diagonals zigzagging along both slanted faces and across the bottom"""
    n = max(1, round((x1 - x0) / step))
    st = (x1 - x0) / n
    out = [rod(id_ + "Bottom", mat, r, [x0, y, 0], [x1, y, 0], 6, at=[[0, 0, hw], [0, 0, -hw]]),
           rod(id_ + "Top", mat, r, [x0, y + h, 0], [x1, y + h, 0], 6),
           rod(id_ + "Cross", mat, rd, [0, y, -hw], [0, y, hw], 4, along={"n": n + 1, "from": [x0, 0, 0], "to": [x1, 0, 0]})]
    up, dn = (n + 1) // 2, n // 2
    for k, (cnt, xa, xb) in enumerate([(up, 0, st), (dn, st, 2 * st)]):
        if cnt < 1: continue
        ya, yb = (y, y + h) if k == 0 else (y + h, y)
        za, zb = (hw, 0) if k == 0 else (0, hw)
        out.append(rod(f"{id_}Diag{k}", mat, rd, [x0 + xa, ya, za], [x0 + xb, yb, zb], 4, along={"n": cnt, "from": [0, 0, 0], "to": [(cnt - 1) * 2 * st, 0, 0]}, mirror="z"))
    out.append(rod(id_ + "DiagB", mat, rd, [x0, y, -hw], [x0 + st, y, hw], 4, along={"n": n, "from": [0, 0, 0], "to": [(n - 1) * st, 0, 0]}))
    return out


# ---- THE MACHINES ----------------------------------------------------------------------------------------------------
def excavator():
    # A HYDRAULIC EXCAVATOR (a 20-tonne class crawler, a Cat 320's size): tracks 4.45 m long on a 2.2 m gauge (2.8 m
    # over the shoes); the upper structure swinging on its ring -- the counterweight at the rear, the engine hood, the
    # cab on the left, a tool box on the right; the boom (5.7 m), the stick (2.9 m) and a 1 m3 bucket, each worked
    # by its cylinder; work lamps. Stood ready to dig: the boom up, the stick hanging, the bucket curled.
    P = "paint"
    perp = (0.939, 0.344)   # (square to the stick's line, in the plane: its outer face)
    parts = [
        use("track", C + "track", [0, 0, 1.1], {"L": 4.45, "H": 0.92, "w": 0.6}, {"tshoe": "shoe", "tframe": "paint", "troller": "roller"}, mirror="z"),
        box("carbody", "dark", [2.0, 0.45, 1.75], [0, 0.62, 0]),
        lathe("swing", "dark", [[0, 0.84], [1.0, 0.84], [1.0, 1.02], [0, 1.02]], [0, 0, 0], sides=24),
        box("deck", P, [3.6, 0.3, 2.5], [-0.3, 1.16, 0]),
        loft("counterweight", P, [[-2.9, 1.1, 1.05, 2.25, 1.12], [-2.75, 1.24, 1.0, 2.32, 1.2], [-2.05, 1.25, 1.0, 2.32, 1.22]], [0.3, 0.22], seg=3),
        box("hoodR", P, [1.85, 0.9, 1.45], [-1.1, 1.75, 0.5]),
        box("hoodL", P, [1.3, 0.8, 1.0], [-1.4, 1.7, -0.75]),
        box("grilleHood", "dark", [1.4, 0.03, 0.8], [-1.1, 2.21, 0.55]),
        box("vent", "dark", [1.2, 0.5, 0.02], [-1.2, 1.75, 1.236]),
        box("toolbox", P, [1.6, 0.62, 0.88], [0.7, 1.62, 0.8]),
        rod("exhaust", "dark", 0.06, [-1.5, 2.2, 0.85], [-1.5, 2.65, 0.85], 8),
        rod("rail", "dark", 0.025, [-2.0, 2.65, 1.2], [1.4, 2.0, 1.2], 6),
        rod("railPost", "dark", 0.025, [0, 1.9, 1.2], [0, 2.4, 1.2], 6, at=[[-1.6, 0.3, 0], [1.2, -0.3, 0]]),
        *cab("cab", -0.75, 1.15, 1.32, 3.05, -1.25, -0.3, frame="dark", door="left", roof=P),
        use("seat", C + "seat", [-0.2, 1.3, -0.78], {"w": 0.5, "h": 0.5, "back": 0.6}, {"cover": "plastic-black", "frame": "dark"}),
        box("console", "dark", [0.5, 0.5, 0.15], [0.0, 1.6, -0.45]),
        # (the boom, curved; its foot between the cab and the tool box)
        box("boomFoot", "dark", [0.6, 0.5, 0.7], [1.05, 1.45, 0]),
        sweep("boom", P, [[1.0, 1.6, 0], [1.9, 3.0, 0], [2.9, 4.25, 0], [3.6, 4.62, 0], [4.6, 4.52, 0], [5.42, 4.0, 0]], None, radii=[1.3, 1.2, 1.05, 1.0, 0.9, 0.75], section=[0.6, 0.46], up=[0, 0, 1], seg=4),
        sweep("stick", P, [[5.15, 4.75, 0], [6.45, 1.2, 0]], None, radii=[1.0, 0.8], section=[0.48, 0.36], up=[0, 0, 1], seg=2),
        rod("pinBoom", "chrome", 0.06, [5.42, 4.0, -0.3], [5.42, 4.0, 0.3], 8),
        *ram("boomRam", [1.55, 1.45, 0.33], [2.75, 3.5, 0.33], 0.1, barrel=P, mirror="z"),
        *ram("stickRam", [2.95, 4.72, 0], [5.05, 5.0, 0], 0.1, barrel=P),
        *ram("bucketRam", [5.15 + perp[0] * 0.38, 4.75 + perp[1] * 0.38 - 0.1, 0], [6.62, 1.95, 0], 0.085, barrel=P),
        rod("link", "dark", 0.05, [6.62, 1.95, 0.2], [6.25, 1.62, 0.2], 6, mirror="z"),
        rod("link2", "dark", 0.05, [6.62, 1.95, 0.24], [6.72, 1.15, 0.24], 6, mirror="z"),
        # (the bucket: its curved shell, the two side plates, the lip and five teeth)
        sweep("bucketShell", "steelp", [[6.35 + 0.55 * math.cos(math.radians(a)), 0.72 + 0.55 * math.sin(math.radians(a)), 0] for a in range(60, -151, -21)], None, section=[0.03, 1.0], up=[0, 0, 1], seg=2),
        plate("bucketSide", "steelp", [[6.35 + 0.55 * math.cos(math.radians(a)), 0.72 + 0.55 * math.sin(math.radians(a))] for a in range(60, -151, -21)] + [[6.25, 1.32], [6.6, 1.36]], 0.03, [0, 0, 0.5], mirror="z"),
        box("lip", "dark", [0.06, 0.08, 1.04], [5.87, 0.445, 0, 0, 0, -60]),
        box("tooth", "dark", [0.08, 0.2, 0.08], [5.82, 0.53, 0, 0, 0, 30], along={"n": 5, "from": [0, 0, -0.4], "to": [0, 0, 0.4]}),
        box("bucketEar", "dark", [0.3, 0.3, 0.06], [6.5, 1.25, 0.2], mirror="z"),
        # (the lamps: one on the boom, two on the cab roof; the beacon)
        use("boomLamp", C + "lamp", [2.3, 3.35, -0.3, 0, 0, -15], {"shape": "square", "r": 0.09, "h": 0.12}, {"lens": "lamp", "bezel": "dark"}),
        use("cabLamp", C + "lamp", [1.2, 3.12, -0.5, 0, 0, -10], {"shape": "square", "r": 0.08, "h": 0.1}, {"lens": "lamp", "bezel": "dark"}),
        sphere("beacon", "amber", 0.08, [-0.5, 3.17, -0.5], sides=8),
    ]
    return item("Excavator", "machine",
        "a 20-tonne hydraulic crawler excavator (a Cat 320's size): two crawler tracks 4.45 m long on a 2.2 m gauge, the upper structure on its swing ring -- counterweight, engine hood, the glazed cab on the left, tool box on the right -- the curved 5.7 m boom, the 2.9 m stick and a 1 m3 bucket with teeth, five hydraulic cylinders, work lamps; stood ready to dig",
        {"paint": {"pick": ["paint-yellow", "paint-yellow", "paint-orange"]}, "dark": "#2a2a2b", "shoe": "#3a3936", "roller": "#4d4b46", "chrome": "chrome", "glass": "glass",
         "steelp": "#3f3e3b", "amber": "lamp-amber"}, parts,
        markers=[{"role": "seat", "at": [-0.2, 1.8, -0.78], "data": {"face": 0}}], era="1990-2030")


def bulldozer():
    # A CRAWLER BULLDOZER (a D6's size): tracks 3.3 m long on a 1.9 m gauge; the engine hood in front with its grille,
    # the ROPS cab behind it, the fuel tank at the rear; the curved blade 3.4 m wide on its push arms, raised by two
    # lift cylinders; a ripper behind.
    P = "paint"
    blade = [[3.95 + 1.3 * math.cos(math.radians(a)), 0.78 + 1.3 * math.sin(math.radians(a)), 0] for a in range(214, 143, -10)]
    parts = [
        use("track", C + "track", [0, 0, 0.95], {"L": 3.3, "H": 0.85, "w": 0.56}, {"tshoe": "shoe", "tframe": "paint", "troller": "roller"}, mirror="z"),
        box("belly", "dark", [3.0, 0.5, 1.4], [0.2, 0.75, 0]),
        box("platform", P, [3.5, 0.2, 2.5], [-0.25, 1.05, 0]),
        box("fender", P, [3.0, 0.06, 0.65], [-0.2, 1.17, 0.95], mirror="z"),
        loft("hood", P, [[-0.1, 0.6, 1.1, 2.15, 0.5], [1.4, 0.6, 1.1, 2.1, 0.5], [1.95, 0.6, 1.0, 1.95, 0.5]], [0.04, 0.08], seg=2),
        box("grille", "dark", [0.06, 0.8, 0.95], [1.96, 1.5, 0]),
        box("grilleBar", P, [0.05, 0.04, 1.0], [1.99, 0, 0], along={"n": 6, "from": [0, 1.15, 0], "to": [0, 1.85, 0]}),
        rod("stack", "dark", 0.07, [0.9, 2.1, 0.25], [0.9, 2.75, 0.25], 8),
        rod("precleaner", "dark", 0.1, [0.6, 2.1, -0.25], [0.6, 2.5, -0.25], 10),
        *cab("cab", -1.35, 0.0, 1.17, 3.2, -0.85, 0.85, frame=P, sill=0.55, door="left", roof=P),
        use("seat", C + "seat", [-0.8, 1.2, 0], {"w": 0.5, "h": 0.5, "back": 0.6}, {"cover": "plastic-black", "frame": "dark"}),
        box("tank", P, [0.5, 0.75, 1.9], [-1.65, 1.55, 0]),
        # (the blade: the curved moldboard, its cutting edge, the end bits, the push arms to the track frames, the lift
        #  cylinders from the hood's sides and the tilt brace)
        sweep("blade", P, blade, None, section=[0.06, 3.4], up=[0, 0, 1], seg=3),
        sweep("bladeRib", P, [[3.95 + 1.38 * math.cos(math.radians(a)), 0.78 + 1.38 * math.sin(math.radians(a)), 0] for a in range(212, 145, -11)], None, section=[0.12, 0.06], up=[0, 0, 1], seg=2, along={"n": 5, "from": [0, 0, -1.4], "to": [0, 0, 1.4]}),
        box("edge", "dark", [0.08, 0.14, 3.4], [2.9, 0.07, 0, 0, 0, -20]),
        plate("endBit", P, [[q[0], q[1]] for q in blade] + [[2.6, 1.5], [2.55, 0.1]], 0.04, [0, 0, 1.7], mirror="z"),
        sweep("pushArm", P, [[0.0, 0.45, 1.22], [1.5, 0.45, 1.25], [2.6, 0.45, 1.2]], None, section=[0.14, 0.2], up=[0, 1, 0], seg=1, mirror="z"),
        *ram("lift", [1.75, 1.95, 0.75], [2.55, 1.35, 0.9], 0.075, barrel=P, mirror="z"),
        *ram("tilt", [1.3, 0.95, 1.1], [2.6, 1.25, 1.1], 0.06, barrel=P),
        # (the ripper: its frame from the rear, the beam across and one shank down)
        box("ripperBeam", P, [0.25, 0.3, 1.8], [-2.6, 0.75, 0]),
        sweep("ripperArm", P, [[-1.75, 0.55, 0.6], [-2.55, 0.75, 0.6]], None, section=[0.14, 0.2], up=[0, 1, 0], seg=1, mirror="z"),
        sweep("shank", "dark", [[-2.6, 1.0, 0], [-2.7, 0.4, 0], [-2.55, 0.0, 0]], None, section=[0.08, 0.16], up=[0, 0, 1], seg=3),
        *ram("ripperRam", [-1.75, 1.15, 0.5], [-2.55, 0.85, 0.5], 0.06, barrel=P, mirror="z"),
        use("lamp", C + "lamp", [0.02, 3.1, 0.65], {"shape": "square", "r": 0.07, "h": 0.1}, {"lens": "lamp", "bezel": "dark"}, mirror="z"),
        use("rearLamp", C + "lamp", [-1.37, 3.1, 0.6, 180, 0, 0], {"shape": "square", "r": 0.07, "h": 0.1}, {"lens": "lamp", "bezel": "dark"}, mirror="z"),
    ]
    return item("Bulldozer", "machine",
        "a crawler bulldozer (a D6's size): two tracks 3.3 m long on a 1.9 m gauge, the engine hood with its grille and stack, the glazed ROPS cab, the fuel tank; the curved 3.4 m blade on its push arms with two lift cylinders and a tilt brace; a single-shank ripper at the rear",
        {"paint": {"pick": ["paint-yellow", "paint-yellow", "paint-orange"]}, "dark": "#2a2a2b", "shoe": "#3a3936", "roller": "#4d4b46", "chrome": "chrome", "glass": "glass"}, parts,
        markers=[{"role": "seat", "at": [-0.8, 1.7, 0], "data": {"face": 0}}], era="1950-2030")


def tractor():
    # A FARM TRACTOR (a 120 hp four-wheel-drive tractor of the 2010s): 2.6 m wheelbase, the rear wheels 1.75 m high on
    # a 1.8 m track, the front 1.2 m; the long bonnet with its grille and front weights, the cab with glass all round
    # over the rear axle, the mudguards, the exhaust up the cab's corner pillar, the three-point linkage behind.
    P = "paint"
    rr, rf = 0.875, 0.6
    xr, xf = -1.2, 1.4
    guard = [[xr + (rr + 0.1) * math.cos(math.radians(a)), rr + (rr + 0.1) * math.sin(math.radians(a)), 0.82] for a in range(160, 19, -20)]
    parts = [
        use("rear", C + "lug-wheel", [xr, rr, 0.9], {"r": rr, "w": 0.52, "rim": 0.62, "n": 22}, {"lrim": "rim", "ltyre": "tyre", "lhub": "steel"}, mirror="z"),
        # (the front wheels steered (`steer`, 35 degrees at full lock) with their mudguards, as a tractor's turn on the axle's ends)
        *steer("steer", [xf, rf, 0.85], [
            use("front", C + "lug-wheel", [xf, rf, 0.85], {"r": rf, "w": 0.38, "rim": 0.6, "n": 16}, {"lrim": "rim", "ltyre": "tyre", "lhub": "steel"}),
            sweep("frontGuard", P, [[xf + (rf + 0.1) * math.cos(math.radians(a)), rf + (rf + 0.1) * math.sin(math.radians(a)), 0.85] for a in range(150, 39, -22)], None, section=[0.42, 0.03], up=[0, 0, 1], seg=2)]),
        rod("rearAxle", "dark", 0.1, [xr, rr, -0.65], [xr, rr, 0.65], 10),
        box("transmission", "dark", [1.3, 0.75, 0.75], [xr + 0.2, 0.95, 0]),
        box("frontAxle", "dark", [0.25, 0.22, 1.1], [xf, rf, 0]),   # (its ends clear of the wheels' discs at full lock)
        box("sump", "dark", [2.0, 0.4, 0.6], [0.4, 0.75, 0]),
        # (the bonnet 37 cm a side: the steered tyres sweep in to 40 cm under it at full lock)
        loft("bonnet", P, [[-0.1, 0.37, 0.9, 1.75, 0.32], [1.6, 0.37, 0.9, 1.72, 0.32], [2.15, 0.35, 0.95, 1.6, 0.28], [2.3, 0.32, 1.0, 1.5, 0.25]], [0.06, 0.12], seg=3),
        box("grille", "dark", [0.03, 0.4, 0.5], [2.31, 1.25, 0]),
        use("head", C + "lamp", [2.25, 1.45, 0.24, 0, 0, 0], {"shape": "square", "r": 0.07, "h": 0.06}, {"lens": "lamp", "bezel": "dark"}, mirror="z"),
        box("weights", "dark", [0.35, 0.45, 0.9], [2.45, 0.85, 0]),
        box("weightPlate", "dark", [0.06, 0.4, 0.95], [2.52, 0.85, 0], along={"n": 5, "from": [-0.15, 0, 0], "to": [0.15, 0, 0]}),
        # (the cab: over the rear axle, its floor at the axle's height, steps up on the left)
        # (between the rear tyres' inner faces, z +-0.64: it had stood 4 cm into them)
        *cab("cab", -1.75, -0.1, 1.45, 2.85, -0.62, 0.62, frame="dark", roof="roof", door="left"),
        box("cabBase", P, [1.6, 0.25, 1.24], [-0.93, 1.35, 0]),
        use("seat", C + "seat", [-1.2, 1.5, 0], {"w": 0.5, "h": 0.45, "back": 0.6}, {"cover": "plastic-black", "frame": "dark"}),
        rod("column", "dark", 0.035, [-0.35, 1.5, 0], [-0.6, 2.0, 0], 8),
        ring("steering", "dark", 0.19, 0.018, [-0.62, 2.02, 0, 0, 0, 30]),
        box("step", "dark", [0.3, 0.04, 0.2], [-0.4, 0, -0.72], along={"n": 3, "from": [0, 0.5, 0], "to": [0, 1.2, 0]}),
        sweep("mudguard", P, guard, None, section=[0.58, 0.04], up=[0, 0, 1], seg=2, mirror="z"),
        rod("exhaust", "dark", 0.055, [-0.1, 1.5, 0.6], [-0.1, 3.15, 0.6], 8),
        use("cabLamp", C + "lamp", [-0.05, 2.82, 0.5], {"shape": "square", "r": 0.06, "h": 0.08}, {"lens": "lamp", "bezel": "dark"}, mirror="z"),
        sphere("beacon", "amber", 0.08, [-1.0, 2.98, -0.5], sides=8),
        use("tail", C + "lamp", [-1.95, 1.2, 0.75, 180, 0, 0], {"shape": "square", "r": 0.06, "h": 0.08}, {"lens": "lamp-red", "bezel": "dark"}, mirror="z"),
        # (the three-point linkage: two lower links, the top link, the PTO stub, the drawbar)
        rod("lowerLink", "dark", 0.04, [-1.5, 0.75, 0.3], [-2.3, 0.55, 0.42], 6, mirror="z"),
        rod("topLink", "dark", 0.04, [-1.6, 1.25, 0], [-2.3, 1.15, 0], 6),
        rod("liftRod", "dark", 0.03, [-1.75, 1.2, 0.35], [-2.0, 0.65, 0.38], 6, mirror="z"),
        rod("pto", "steel", 0.035, [-1.6, 0.85, 0], [-1.85, 0.85, 0], 8),
        box("drawbar", "dark", [0.6, 0.06, 0.15], [-1.8, 0.45, 0]),
    ]
    return item("Farm tractor", "machine",
        "a 120 hp four-wheel-drive farm tractor of the 2010s: 2.6 m wheelbase, rear wheels 1.75 m high and front 1.2 m on lugged tyres, the long bonnet with grille, lamps and front weights, the glazed cab over the rear axle with its seat and wheel, mudguards, the exhaust up the cab pillar, the three-point linkage, PTO and drawbar",
        {"paint": {"pick": ["paint-green", "paint-red", "paint-blue", "#e2c21c"]}, "rim": "paint-yellow", "tyre": "rubber", "roof": "plastic-white", "dark": "#2b2b2c", "steel": "steel", "glass": "glass", "chrome": "chrome", "amber": "lamp-amber"},
        parts, params={"steer": 0}, markers=[{"role": "seat", "at": [-1.2, 1.95, 0], "data": {"face": 0}}], era="1990-2030")


def forklift():
    # A COUNTERBALANCED FORKLIFT (2.5 t, an IC truck): 1.6 m wheelbase, 1.15 m wide; the drive wheels in front under
    # the mast, the steered wheels behind under the counterweight; the overhead guard 2.15 m up over the seat; the
    # two-stage mast 2.0 m lowered, the fork carriage with its load backrest and two forks 1.07 m long.
    P = "paint"
    CW, CWR = [[-1.62, 0.5, 0.3, 1.2, 0.45], [-1.5, 0.57, 0.28, 1.25, 0.52], [-1.05, 0.57, 0.3, 1.25, 0.52]], [0.15, 0.12]
    parts = [
        use("front", C + "wheel", [0.45, 0.33, 0.42], {"r": 0.33, "w": 0.22, "rim": 0.5, "spokes": 0, "seal": 1}, {"hub": "dark"}, mirror="z"),
        # (the rear wheels steered (`steer`: +1 turns the truck left, so they turn right; 60 degrees at full lock -- a
        #  forklift's turn tight)
        *steer("steer", [-1.1, 0.28, 0.4], [use("rear", C + "wheel", [-1.1, 0.28, 0.4], {"r": 0.28, "w": 0.18, "rim": 0.5, "spokes": 0, "seal": 1}, {"hub": "dark"})], -60),
        # (the frame between the wheels -- it had been a box the truck's full width, the wheels half sunk in it -- and the
        #  deck over them; the counterweight open below, notched round the steered wheels, their wells dark)
        box("chassis", P, [1.29, 0.6, 0.58], [-0.195, 0.65, 0]),   # (ending ahead of the steered wheels' sweep)
        box("deck", P, [1.6, 0.2, 1.1], [-0.35, 0.85, 0]),
        box("fenderF", P, [0.6, 0.1, 0.32], [0.45, 0.72, 0.42], mirror="z"),
        # (its front end cut off below the deck -- the end had stood across the wheels; `all` clips a loft's cap)
        loft("counterweight", P, CW, CWR, seg=2, arches=body_arches([-1.1], 0.28), bare=["bottom"], holes=[region(-1.06, -1.0, -1, 0.76, "both", all=True)]),
        *pan("cwPan", "dark", CW, CWR, -1.62, -1.05, [arch_gap(-1.1, 0.28, cr_at(CW, -1.1)[1] + 0.004)], [steer_in(0.8, 0.28, 0.18, 60)]),
        # (only the wells and their inner walls: the counterweight ends over the axle, so a lip round the notch would run
        #  on into the air; the walls in to clear the wheels at full lock, the two wells all but one)
        *[q for q in arches([-1.1], 0.28, 0.57, 0.8, inner=steer_in(0.8, 0.28, 0.18, 60), cup=True, floor=cr_at(CW, -1.1)[1] + 0.004) if q["id"].startswith(("house", "tub"))],
        box("hood", P, [0.85, 0.2, 1.0], [-0.55, 1.05, 0]),
        box("cowl", P, [0.35, 0.55, 1.0], [0.25, 1.1, 0]),
        use("seat", C + "seat", [-0.55, 1.15, 0], {"w": 0.5, "h": 0.12, "back": 0.5, "pedestal": 0}, {"cover": "plastic-black", "frame": "dark"}),
        rod("column", "dark", 0.03, [0.2, 1.3, 0], [0.0, 1.55, 0], 8),
        ring("steering", "dark", 0.17, 0.016, [-0.02, 1.57, 0, 0, 0, 55]),
        box("lever", "dark", [0.02, 0.2, 0.02], [0.15, 1.45, 0.25], along={"n": 3, "from": [0, 0, 0], "to": [0, 0, 0.12]}),
        # (the overhead guard: two front posts raked up from the cowl, two rear posts from the counterweight, the roof's
        #  frame and its slats)
        rod("postF", "dark", 0.04, [0.38, 1.35, 0.48], [0.1, 2.15, 0.48], 8, mirror="z"),
        rod("postR", "dark", 0.04, [-1.15, 1.2, 0.48], [-1.05, 2.15, 0.48], 8, mirror="z"),
        box("guardSide", "dark", [1.25, 0.06, 0.06], [-0.48, 2.17, 0.48], mirror="z"),
        box("slat", "dark", [0.05, 0.04, 1.0], [0, 2.17, 0], along={"n": 9, "from": [-1.05, 0, 0], "to": [0.1, 0, 0]}),
        use("lampF", C + "lamp", [0.18, 2.1, 0.52], {"shape": "round", "r": 0.06}, {"lens": "lamp", "bezel": "dark"}, mirror="z"),
        sphere("beacon", "amber", 0.06, [-0.95, 2.24, 0], sides=8),
        # (the mast: the outer channels from the front axle, the inner pair inside them, crossheads; the lift cylinder
        #  behind; two tilt cylinders from the frame)
        box("outer", "mast", [0.1, 2.0, 0.12], [0.72, 1.05, 0.38], mirror="z"),
        box("inner", "mast", [0.08, 1.95, 0.08], [0.76, 1.08, 0.29], mirror="z"),
        box("crossTop", "mast", [0.1, 0.1, 0.88], [0.72, 2.0, 0]),
        box("crossMid", "mast", [0.08, 0.08, 0.8], [0.72, 1.0, 0]),
        *ram("liftRam", [0.68, 0.3, 0], [0.68, 1.95, 0], 0.05, barrel="mast", frac=0.6),
        *ram("tiltRam", [0.35, 0.8, 0.45], [0.68, 1.1, 0.45], 0.04, barrel="mast", mirror="z"),
        rod("chain", "dark", 0.012, [0.85, 0.6, 0.12], [0.8, 1.95, 0.12], 4, mirror="z"),
        # (the fork carriage, its backrest grille and the two L-shaped forks)
        box("carriage", "mast", [0.06, 0.45, 1.05], [0.88, 0.38, 0]),
        box("backrestFrame", "mast", [0.04, 0.05, 1.05], [[0.88, 0.62, 0], [0.88, 1.22, 0]]),
        box("backrestBar", "mast", [0.03, 0.62, 0.03], [0.88, 0.92, 0], along={"n": 8, "from": [0, 0, -0.5], "to": [0, 0, 0.5]}),
        box("forkShank", "fork", [0.045, 0.55, 0.12], [0.94, 0.33, 0.3], mirror="z"),
        box("forkBlade", "fork", [1.07, 0.045, 0.12], [1.47, 0.08, 0.3], mirror="z"),
        sphere("forkHeel", "fork", 0.05, [0.94, 0.08, 0.3], mirror="z", sides=8),
        use("tail", C + "lamp", [-1.63, 0.95, 0.4, 180, 0, 0], {"shape": "square", "r": 0.05, "h": 0.07}, {"lens": "lamp-red", "bezel": "dark"}, mirror="z"),
        # (the LPG bottle lying across behind the seat on its cradle, and the step up on the left)
        rod("lpg", "lpg", 0.15, [-1.3, 1.42, -0.4], [-1.3, 1.42, 0.4], 12),
        sphere("lpgEnd", "lpg", 0.15, [-1.3, 1.42, 0.4], stretch=[1, 1, 0.5], sides=12, mirror="z"),
        box("cradle", "dark", [0.08, 0.2, 0.05], [-1.3, 1.3, 0.25], mirror="z"),
        box("stepL", "dark", [0.3, 0.04, 0.12], [0.0, 0.73, -0.6]),
    ]
    return item("Forklift", "machine",
        "a 2.5 t counterbalanced forklift: 1.6 m wheelbase, 1.15 m wide; drive wheels in front, steered wheels under the rounded counterweight; the seat under the overhead guard 2.15 m up; the two-stage mast 2.0 m lowered with its lift and tilt cylinders, the fork carriage, the load backrest and two 1.07 m forks",
        {"paint": {"pick": ["paint-orange", "paint-yellow", "paint-red", "paint-green"]}, "mast": "#2c2c2e", "dark": "#232324", "fork": "#3a3a3a", "lpg": "#c9ccd0", "tyre": "rubber", "rim": "plastic-black",
         "glass": "glass", "chrome": "chrome", "amber": "lamp-amber", "well": "#141416"}, parts,
        params={"steer": 0}, markers=[{"role": "seat", "at": [-0.55, 1.2, 0], "data": {"face": 0}}], era="1960-2030")


def tower_crane():
    # A TOWER CRANE (a hammerhead, a 1990s-2020s building site's): the lattice mast 1.6 m square, 36 m to the slewing
    # unit, on a cross base with concrete ballast; the cab at the top on the jib's side; the jib 45 m along +x, the
    # counter-jib 13 m behind with its winch and counterweight blocks; the tower head and its pendants; the trolley
    # and the hook block hanging below. The origin at the mast's foot.
    M = "paint"
    Hm, s = 36.0, 1.6
    y = Hm + 1.2   # (the jib's bottom chords)
    parts = [
        # (the base: a cross of beams on concrete ballast)
        box("baseBeam", "paint", [9.0, 0.6, 0.6], [[0, 0.3, 0, 45, 0, 0], [0, 0.3, 0, -45, 0, 0]]),
        box("ballast", "concrete", [2.0, 1.0, 1.0], [[2.4, 0.6, 2.4, 45, 0, 0], [2.4, 0.6, -2.4, -45, 0, 0], [-2.4, 0.6, 2.4, -45, 0, 0], [-2.4, 0.6, -2.4, 45, 0, 0]]),
        box("footing", "concrete", [2.2, 0.4, 2.2], [0, 0.2, 0]),
        *lattice_mast("mast", M, Hm - 0.6, s, 1.6, y0=0.6, r=0.07),
        # (the slewing unit: a turntable on the mast's top, its platform)
        box("slewBase", M, [2.2, 0.4, 2.2], [0, Hm + 0.2, 0]),
        lathe("slewRing", "dark", [[0, Hm + 0.4], [1.0, Hm + 0.4], [1.0, Hm + 0.7], [0, Hm + 0.7]], [0, 0, 0], sides=20),
        box("slewTop", M, [2.4, 0.5, 2.4], [0, Hm + 0.95, 0]),
        # (the cab beside the jib's root, glazed)
        *cab("cab", 0.4, 2.4, Hm + 0.3, Hm + 2.6, 1.0, 2.6, frame=M, roof=M),
        # (the jib and the counter-jib)
        *lattice_jib("jib", M, 1.2, 46.0, y, 0.8, 1.6, 2.0),
        box("jibTip", M, [0.4, 1.6, 1.6], [46.1, y + 0.8, 0]),
        box("cjDeck", M, [13.0, 0.3, 2.2], [-7.7, y + 0.15, 0]),
        box("cjRail", M, [13.0, 0.05, 0.05], [-7.7, y + 1.1, 1.1], mirror="z"),
        box("cjPost", M, [0.05, 1.0, 0.05], [0, y + 0.6, 1.1], along={"n": 6, "from": [-13.5, 0, 0], "to": [-1.5, 0, 0]}, mirror="z"),
        box("counterweight", "concrete", [0.9, 2.6, 2.2], [0, y - 0.9, 0], along={"n": 4, "from": [-13.6, 0, 0], "to": [-10.9, 0, 0]}),
        box("winch", "dark", [1.6, 1.2, 1.6], [-7.0, y + 0.9, 0]),
        lathe("drum", "steel", [[0, -0.6], [0.45, -0.6], [0.45, 0.6], [0, 0.6]], [-5.8, y + 0.9, 0, 0, 90, 0], sides=12),
        box("cabinet", "white", [1.4, 1.6, 1.0], [-9.5, y + 1.1, 0]),
        # (the tower head: a pyramid of four legs to the apex, and the pendant ties to the jib and the counter-jib)
        rod("headLeg", M, 0.1, [0.9, y, 0.9], [0, y + 7.5, 0], 6, mirror="z"),
        rod("headLegB", M, 0.1, [-0.9, y, 0.9], [0, y + 7.5, 0], 6, mirror="z"),
        rod("pendant", "steel", 0.04, [0, y + 7.5, 0], [30.0, y + 1.6, 0], 4),
        rod("pendant2", "steel", 0.04, [0, y + 7.5, 0], [16.0, y + 1.6, 0], 4),
        rod("pendantB", "steel", 0.04, [0, y + 7.5, 0], [-12.5, y + 0.3, 0.9], 4, mirror="z"),
        sphere("aviation", "lamp-red", 0.15, [0, y + 7.7, 0], sides=8),
        # (the trolley on the jib's bottom chords and the hook block hanging below it on its falls)
        box("trolley", "paint", [1.2, 0.5, 1.9], [22.0, y - 0.25, 0]),
        rod("fall", "steel", 0.02, [22.0, y - 0.5, 0], [22.0, 18.6, 0], 4, at=[[-0.25, 0, 0], [0.25, 0, 0]]),
        box("hookBlock", "hook", [0.8, 0.7, 0.4], [22.0, 18.3, 0]),
        sweep("hook", "dark", [[22.0, 17.95, 0], [22.0, 17.5, 0], [22.2, 17.3, 0], [22.38, 17.5, 0], [22.33, 17.68, 0]], 0.06, seg=3),
        rod("ladder", M, 0.02, [0, 0.6, 0], [0, Hm, 0], 4, at=[[-0.5, 0, -0.85], [-0.1, 0, -0.85]]),
    ]
    return item("Tower crane", "machine",
        "a hammerhead tower crane: the 1.6 m square lattice mast 36 m high on a cross base with concrete ballast, the slewing unit and its glazed cab, the 45 m triangular lattice jib (+x) with its trolley and hook block, the 13 m counter-jib with the hoist winch and four counterweight blocks, the tower head and its pendant ties, a red aviation light",
        {"paint": {"pick": ["paint-yellow", "paint-red", "paint-white"]}, "dark": "#2b2b2c", "steel": "steel", "concrete": "concrete", "glass": "glass", "white": "plastic-white",
         "hook": "#e4b52a", "chrome": "chrome", "lamp-red": "lamp-red"}, parts,
        markers=[{"role": "seat", "at": [1.4, Hm + 0.4, 1.8], "data": {"face": 0}}], era="1950-2030")


def mixer_truck():
    # A CONCRETE MIXER TRUCK (a three-axle chassis, 8 m3 drum): the forward-control cab, the chassis rails, the
    # drum tilted up toward the rear on its pedestals, its spiral rib outside, the hopper and the chute at the rear,
    # the water tank, the ladder; road wheels on three axles (one steered in front, a bogie of two behind).
    P = "paint"
    r = 0.52
    CAB, CABR = [[1.75, 1.2, 1.05, 3.2, 1.12], [2.3, 1.22, 1.0, 3.3, 1.15], [3.5, 1.22, 1.0, 3.25, 1.1], [3.75, 1.2, 1.05, 3.0, 1.05]], [0.08, 0.18]
    zc = lambda x, y: loft_z(CAB, CABR, x, y)
    CABL = loft("cab", "cab", CAB, CABR, seg=2, arches=body_arches([2.6], r), bare=["bottom"], double=True, caps=[True, False])   # (the loft, once: its doors cut from it)
    dX, dY, wX, wY = (2.42, 3.5), (1.16, 2.95), (2.55, 3.4), (2.2, 2.82)   # (the doors' stretch; their windows')
    # (the drum: a lathe about its own axis, laid along x and tilted 13 degrees, its mouth at the rear)
    drum = [[0.0, -2.2], [0.55, -2.15], [1.05, -1.6], [1.18, -0.6], [1.18, 0.4], [0.95, 1.3], [0.55, 2.0], [0.42, 2.2], [0.42, 2.35]]
    ax, ay, tilt = -0.9, 2.45, 13
    ca, sa = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))

    def rad(q):   # (the drum's radius at q along its axis, from the profile)
        for (r0, y0), (r1, y1) in zip(drum, drum[1:]):
            if y0 <= q <= y1 and y1 > y0: return r0 + (r1 - r0) * (q - y0) / (y1 - y0)
        return 0.4
    parts = [
        # (the front wheels steered (`steer`, 35 degrees at full lock), each on its knuckle: the stub turning with it, the
        #  axle's end short of it)
        *steer("steer", [2.6, r, 1.0], [use("wheelF", C + "wheel", [2.6, r, 1.0], {"r": r, "w": 0.32, "rim": 0.55, "spokes": 0}, {"hub": "steel"}),
                                        rod("knuckle", "dark", 0.07, [2.6, r, 0.71], [2.6, r, 0.88], 8)]),
        use("wheelR", C + "wheel", [[-1.0, r, 0.95], [-2.35, r, 0.95]], {"r": r, "w": 0.32, "rim": 0.55, "spokes": 0}, {"hub": "steel"}, mirror="z"),
        box("chassis", "dark", [7.6, 0.3, 0.9], [0.0, 0.95, 0]),
        rod("axle", "dark", 0.08, [0, r, -0.85], [0, r, 0.85], 8, at=[[-1.0, 0, 0], [-2.35, 0, 0]]),
        rod("axleF", "dark", 0.08, [2.6, r, -0.68], [2.6, r, 0.68], 8),   # (the steered axle's: its ends clear of the hubs at full lock)
        # (THE CAB, over the front axle: a rounded loft, a shell seen from inside (as the lorry's, 2026-11-22 -- it had
        #  been solid, its glass opaque boxes on it); its bottom open over the front wheels, notched round them, with the
        #  floor pan and the arches' liners -- the cab's flat bottom had run through the tyres' tops)
        cut(CABL, [region(*dX, *dY, "both"), region(3.55, 3.72, 2.2, 2.85, "both")]),
        *pan("pan", "dark", CAB, CABR, 1.75, 3.75, [arch_gap(2.6, r, cr_at(CAB, 2.6)[1] + 0.004)], [steer_in(2.0, r, 0.32)]),
        *arches([2.6], r, 1.2, 2.0, inner=steer_in(2.0, r, 0.32), cup=True, skin=zc, low=lambda x: cr_at(CAB, x)[1],
                floor=lambda x: cr_at(CAB, x)[1] + 0.004),
        # (its front, the loft's cap left off: panels round the windscreen)
        box("front", "cab", [0.03, 1.03, 2.3], [3.735, 1.565, 0]),
        box("frontTop", "cab", [0.03, 0.08, 1.7], [3.735, 2.955, 0]),
        box("frontPost", "cab", [0.03, 0.85, 0.07], [3.735, 2.5, 1.025], mirror="z"),
        box("windscreen", "glazing", [0.02, 0.85, 2.0], [3.75, 2.5, 0]),
        box("quarterWin", "glazing", [0.17, 0.65, 0.01], [3.635, 2.525, zc(3.635, 2.525) - 0.01], mirror="z"),
        # (THE DOORS: hinged at their front edge, the window in a hole of the skin, the pane, the handle, the card)
        hinge("cabDoor", [dX[1], 1.9, zc(dX[1], 1.9) - 0.01], [
            piece(CABL, [region(*dX, *dY)], "skin", holes=[region(*wX, *wY)]),
            box("pane", "glazing", [wX[1] - wX[0] + 0.02, wY[1] - wY[0] + 0.02, 0.01], [(wX[0] + wX[1]) / 2, (wY[0] + wY[1]) / 2, zc(3.0, 2.5) - 0.02]),
            box("handle", "chrome", [0.18, 0.03, 0.03], [2.65, 1.9, zc(2.65, 1.9) + 0.01]),
            use("card", C + "door-card", [2.97, 1.55, zc(2.97, 1.55) - 0.05], {"w": 0.9, "h": 0.6}),
        ], max_=70, mirror="z"),
        rod("grab", "chrome", 0.015, [2.38, 1.25, 1.24], [2.38, 2.3, 1.24], 6, mirror="z"),
        # (INSIDE: the floor over the wheel houses, the engine's hump, the dash with its wheel, two seats)
        box("cabFloor", "rubberMat", [1.93, 0.04, 2.3], [2.75, 1.13, 0]),
        box("hump", "rubberMat", [1.0, 0.3, 0.6], [3.05, 1.3, 0]),
        use("dash", C + "car-dash", [3.42, 1.88, 0], {"w": 2.2, "d": 0.4, "h": 0.5, "sz": 0.55}),
        use("seat", C + "car-seat", [2.72, 1.15, 0.58], {"h": 0.42, "back": 0.62, "heads": 0.2}, mirror="z"),
        box("grille", "trim", [0.04, 0.5, 1.4], [3.765, 1.55, 0]),
        box("bumper", "dark", [0.25, 0.3, 2.45], [3.85, 0.95, 0]),
        use("head", C + "lamp", [3.92, 1.0, 0.9], {"shape": "square", "r": 0.13, "h": 0.12}, {"lens": "lamp", "bezel": "dark"}, mirror="z"),
        use("mirror", C + "wing-mirror", [3.62, 2.75, 1.17], {"ax": 0.084, "ay": 0.025, "az": 0.13, "w": 0.18, "h": 0.35, "d": 0.08, "out": 1, "hang": 1, "armR": 0.015}, {"shell": "dark", "arm": "dark"}, mirror="z"),
        box("step", "dark", [0.35, 0.05, 0.25], [1.85, 0, 1.15], along={"n": 2, "from": [0, 0.55, 0], "to": [0, 0.85, 0]}, mirror="z"),   # (behind the front tyre: it had stood in it)
        sweep("fenderR", "dark", [[-2.9 + 0.0, 1.15, 0.95], [-0.5, 1.15, 0.95]], None, section=[0.36, 0.04], up=[0, 1, 0], seg=1, mirror="z"),
        # (the drum on its pedestals: the front one tall, the rear one short with the rollers; the spiral rib round it)
        lathe("drum", "drum", drum, [ax, ay, 0, 0, 0, 90 - tilt], sides=24),
        sweep("spiral", "drum", [[ax - ca * q + sa * (rad(q) + 0.02) * math.cos(k * 0.9), ay + sa * q + ca * (rad(q) + 0.02) * math.cos(k * 0.9), (rad(q) + 0.02) * math.sin(k * 0.9)]
              for k, q in [(k, -1.5 + 0.32 * k) for k in range(12)]], 0.03, seg=3),
        box("pedestalF", "dark", [0.3, 1.0, 1.0], [0.85, 1.55, 0]),
        box("pedestalR", "dark", [0.3, 0.6, 1.2], [-2.6, 1.35, 0]),
        # (the hopper over the drum's mouth, the chute below it swung out to the side, the water tank behind the cab)
        lathe("hopper", "paint2", [[0.2, 0], [0.55, 0.6], [0.6, 0.62]], [-3.35, 3.0, 0], caps=False, double=True, sides=12),
        sweep("chute", "paint2", [[-3.35, 2.2, 0], [-3.7, 1.8, 0.3], [-4.0, 1.5, 0.9]], None, section=[0.45, 0.05], up=[0, 1, 0], seg=2),
        rod("waterTank", "paint2", 0.32, [1.2, 2.0, 0.55], [1.2, 3.0, 0.55], 12),
        rod("ladderRail", "dark", 0.02, [-2.8, 1.0, 0.75], [-3.05, 3.1, 0.75], 4, at=[[0, 0, 0], [0, 0, -0.4]]),
        rod("ladderRung", "dark", 0.015, [0, 0, 0.35], [0, 0, 0.75], 4, along={"n": 7, "from": [-2.82, 1.2, 0], "to": [-3.02, 2.9, 0]}),
        use("tail", C + "lamp", [-3.15, 1.0, 1.0, 180, 0, 0], {"shape": "square", "r": 0.1, "h": 0.08}, {"lens": "lamp-red", "bezel": "dark"}, mirror="z"),
    ]
    return item("Concrete mixer truck", "vehicle",
        "a three-axle concrete mixer truck: the forward cab (its doors hinged, see-through windows; inside the dash and wheel, two seats), the chassis on three axles of road wheels, the 8 m3 drum tilted up toward the rear on its pedestals with its spiral rib, the hopper and the swung-out chute, the water tank and the ladder",
        {"cab": {"pick": ["paint-white", "paint-red", "paint-blue", "paint-orange"]}, "drum": {"pick": ["paint-white", "paint-orange", "paint-yellow", "paint-grey"]}, "paint2": "paint-grey",
         "dark": "#262627", "trim": "plastic-black", "well": "#141416", "rim": "paint-silver", "steel": "steel", "glass": "glass", "chrome": "chrome",
         "glazing": "window-glass", "rubberMat": "#2b2d30"}, parts, params={"open": 0, "steer": 0},
        markers=[{"role": "seat", "at": [2.72, 1.6, -0.58], "data": {"face": 0, "driver": 1}}], era="1960-2030")


def write_all():
    write("modern/components/track", track(), "components")
    write("modern/components/lug-wheel", lug_wheel(), "components")
    write("modern/components/cab", cab_component(), "components")
    for name, f in [("excavator", excavator), ("bulldozer", bulldozer), ("tractor", tractor), ("forklift", forklift), ("tower-crane", tower_crane), ("mixer-truck", mixer_truck)]:
        write("modern/machines/" + name, f(), "machines")

GROUPS = {"machines": "machines", "components": "components"}
