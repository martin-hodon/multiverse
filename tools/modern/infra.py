"""THE INFRASTRUCTURE (2026-11-20; docs/modern.md): roads, rails, the railway station, the bus station, the airport --
all as ITEMS (assets/items/modern/infra/), not architecture. (Why items: the architecture engine (docs/arch.md) is a
masonry language -- walls with arched openings, vaults, orders, rings of bays -- and has no glass you see through, no
steel arch ribs, no loft; a station is mostly modular pieces that must also stand alone -- the track, the platform, the
canopy, the stair, the departure board -- and those are items anyway. So the big buildings here are items composed
of items by `use`, and the asset viewer shows them like a car.)

THE FRAMES. Every piece has its origin on the ground (y 0 the ground the road or the formation lies on), lengths in
metres, +x along the road or the track, +z across (to the right of a traveller heading +x). A straight piece is
centred on its middle; a curve and a turnout start at the origin heading +x and turn to the right (+z). Each piece's
_about gives its tile length and its ports, so pieces tile end to end.

THE NUMBERS that pieces share (kept here, so a station's platforms meet its track):
  road:   asphalt top y 0.02; two lanes of 3.5 m (carriageway z +-3.5); kerbs 0.15 wide, top 0.17; pavements to z +-5.5
  track:  formation y 0; ballast to 0.40; concrete sleepers 2.6 m every 0.625 m; rail foot 0.47, RAIL TOP RT = 0.642
          (a rail vehicle -- tools/modern/rail.py, its origin the rail's top -- stands at y RT); standard gauge 1.435,
          the rails' centres +-0.7535
  platform: its top 0.76 above the rail (y 1.40), its edge 1.65 m from the track's centre line
"""
import json, math
from kit import item, box, rod, lathe, loft, sphere, ring, sweep, plate, use, write, across, arc, hole, each, merge, runs, fill, panes, bars, face_box, window_wall

C = "modern/components/"
I = "modern/infra/"

# ---- THE SHARED NUMBERS ------------------------------------------------------------------------------------------
YA, YK, YP = 0.02, 0.17, 0.16           # (asphalt top, kerb top, pavement top)
LANE, CW2, KW, PW2 = 3.5, 3.5, 0.15, 5.5   # (a lane, half the carriageway, the kerb's width, the pavement's outer edge)
G = 1.435
RC = G / 2 + 0.036                      # (a rail's centre line: the gauge is taken between the heads' inner faces)
RF, RT = 0.47, 0.642                    # (the rail's foot, its top)
PH = RT + 0.758                         # (a platform's top: 1.40)
PE = 1.65                               # (a platform's edge from the track's centre)


# ---- SMALL HELPERS -----------------------------------------------------------------------------------------------
def bx(id_, mat, xr, yr, zr, yaw=0, **k):
    """a box by its extents [x0, x1], [y0, y1], [z0, z1] (turned by `yaw` about its own middle)"""
    at = [(xr[0] + xr[1]) / 2, (yr[0] + yr[1]) / 2, (zr[0] + zr[1]) / 2]
    if yaw: at += [yaw, 0, 0]
    return box(id_, mat, [abs(xr[1] - xr[0]), abs(yr[1] - yr[0]), abs(zr[1] - zr[0])], at, **k)


def flat(id_, mat, pts, top, thick, **k):
    """a plate lying flat: its outline in (x, z), its top at y `top` (items.js plate turned by pitch 90: (x, y) -> (x, z))"""
    return plate(id_, mat, pts, thick, [0, top - thick / 2, 0, 0, 90, 0], **k)


def arc_xz(cx, cz, r, a0, a1, n):
    """points of a circle in the ground plane, angles from +x toward +z in degrees"""
    return [[cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))] for i in range(n + 1)]


def on_arc(R, th, off=0.0, y=0.0):
    """a place on a right-hand curve that starts at the origin heading +x: its centre line radius R, `th` degrees round,
    `off` metres to the right of the centre line -- [x, y, z, yaw] (yaw turns +x onto the curve's heading)"""
    t, r = math.radians(th), R - off
    return [r * math.sin(t), y, R - r * math.cos(t), -th]


def arc_path(R, th0, th1, off, y, n):
    return [on_arc(R, th0 + (th1 - th0) * i / n, off, y)[:3] for i in range(n + 1)]


def yaw_of(dx, dz):
    """the yaw that turns +x onto the ground direction (dx, dz) (items.js: yaw turns +x toward -z)"""
    return -math.degrees(math.atan2(dz, dx))


def stripes(id_, mat, x0, x1, z, w, dash, gap, y=YA, t=0.004, **k):
    """a dashed line along x: dashes `dash` long with `gap` between, starting at x0"""
    xs, x = [], x0
    while x + dash <= x1 + 1e-6:
        xs.append([x + dash / 2, y + t / 2, z]); x += dash + gap
    return box(id_, mat, [dash, t, w], xs, **k) if xs else None


# ==================================================================================================================
# ROADS
# ==================================================================================================================
ROAD_MATS = {"asphalt": "asphalt", "line": "tarmac-line", "kerb": "#9b9a95", "pave": "#b3afa6", "joint": "#8a877f", "grate": "#2a2b2d"}


def road_straight():
    # A STRAIGHT ROAD, 10 m: two lanes of 3.5 m, the centre line dashed (3 m dash, 2 m gap: five metres a period, so
    # tiles repeat it), granite kerbs, pavements 1.85 m wide with their slabs' joints, a gully grate at the kerb
    L = 10.0
    parts = [
        bx("asphalt", "asphalt", [-L / 2, L / 2], [-0.12, YA], [-CW2, CW2]),
        bx("kerb", "kerb", [-L / 2, L / 2], [-0.12, YK], [CW2, CW2 + KW], mirror="z"),
        bx("pave", "pave", [-L / 2, L / 2], [-0.12, YP], [CW2 + KW, PW2], mirror="z"),
        box("joint", "joint", [0.025, 0.003, PW2 - CW2 - KW], [[x, YP + 0.0015, (PW2 + CW2 + KW) / 2] for x in (-4.0, -2.0, 0.0, 2.0, 4.0)], mirror="z"),
        stripes("centre", "line", -L / 2 + 1, L / 2, 0, 0.12, 3, 2, when="centre"),
        box("edge", "line", [L, 0.004, 0.12], [0, YA + 0.002, CW2 - 0.3], mirror="z", when="edges"),
        bx("grate", "grate", [2.6, 3.1], [YA, YA + 0.006], [CW2 - 0.45, CW2 - 0.05]),
    ]
    return item("Road, straight", "infrastructure",
        "a straight piece of town road, 10 m (TILE 10 m: ports at x -5 and +5, the road along x): two lanes of 3.5 m, the centre line dashed 3 m / 2 m, granite kerbs 15 cm high, pavements to 5.5 m each side (11 m in all); `edges` adds edge lines. Asphalt top y 0.02, pavement 0.16.",
        ROAD_MATS, parts, params={"edges": 0, "centre": 1})


def road_curve():
    # A QUARTER CURVE: the centre line a quarter circle of R 15, entering at the origin heading +x and leaving at
    # (R, 0, R) heading +z -- the carriageway, kerbs and pavements swept round it, the dashes laid on it
    R, n = 15.0, 18
    sw = lambda id_, mat, off, w, y0, y1: sweep(id_, mat, arc_path(R, 0, 90, off, (y0 + y1) / 2, n), section=[w, y1 - y0], up=[0, 1, 0], seg=1)
    parts = [
        sw("asphalt", "asphalt", 0, 2 * CW2, -0.12, YA),
        sw("kerbIn", "kerb", CW2 + KW / 2, KW, -0.12, YK), sw("kerbOut", "kerb", -CW2 - KW / 2, KW, -0.12, YK),
        sw("paveIn", "pave", (CW2 + KW + PW2) / 2, PW2 - CW2 - KW, -0.12, YP), sw("paveOut", "pave", -(CW2 + KW + PW2) / 2, PW2 - CW2 - KW, -0.12, YP),
    ]
    arcL = R * math.pi / 2; k = round(arcL / 5); per = arcL / k
    dashes = [on_arc(R, math.degrees((per * i + per * 0.3) / R), 0, YA + 0.002) + [0, 0] for i in range(k)]
    parts.append(box("centre", "line", [per * 0.6, 0.004, 0.12], dashes))
    return item("Road, curve", "infrastructure",
        "a quarter-circle bend of the same road (centre line R 15 m, 23.6 m along it): enters at the origin heading +x (port at x 0), turns right and leaves at (15, 0, 15) heading +z. Two lanes, the dashed centre line, kerbs and pavements swept round.",
        ROAD_MATS, parts)


def corner_pave(i, sx, sz, r, far):
    """the pavement and kerb round one corner of a junction, in quadrant (sx, sz): a kerb radius r, the arms to `far`"""
    a, b = CW2, CW2 + KW
    pts = [[far, b], [far, PW2], [PW2, PW2], [PW2, far], [b, far], [b, a + r]]
    pts += arc_xz(a + r, a + r, r - KW, 180, 270, 8)[1:-1] + [[a + r, b]]
    pts = [[x * sx, z * sz] for x, z in pts]
    kerb = [[far, a + KW / 2], [a + r, a + KW / 2]] + arc_xz(a + r, a + r, r - KW / 2, 270, 180, 8)[1:-1] + [[a + KW / 2, a + r], [a + KW / 2, far]]
    kerb = [[x * sx, (YK - 0.12) / 2, z * sz] for x, z in kerb]
    return [flat(f"pave{i}", "pave", pts, YP, YP + 0.12),
            sweep(f"kerb{i}", "kerb", kerb, section=[KW, YK + 0.12], up=[0, 1, 0], seg=1)]


def give_way_sign(id_, x, z, yaw):
    """a give-way sign on its post: a red-rimmed white triangle, point down"""
    tri = lambda s: [[0, -s], [s * 0.866, s * 0.5], [-s * 0.866, s * 0.5]]
    return [rod(id_ + "Post", "post", 0.035, [x, 0, z], [x, 2.6, z], 8),
            plate(id_ + "Rim", "signRed", tri(0.52), 0.02, [x, 2.25, z, yaw + 90, 0, 0]),
            plate(id_ + "Face", "signWhite", tri(0.36), 0.03, [x, 2.25, z, yaw + 90, 0, 0])]


def junction(arms, name, title):
    # A JUNCTION: the same road's arms meeting in a square 17 m across (each arm 5 m from the crossing's edge); kerbs
    # turn the corners on a 3 m radius; the arms without priority get a give-way line (a row of short dashes) and a sign
    H, r = 8.5, 3.0
    parts = [bx("asphaltX", "asphalt", [-H, H], [-0.12, YA], [-CW2, CW2]),
             bx("asphaltZ", "asphalt", [-CW2, CW2], [-0.12, YA], [-H if "-z" in arms else -CW2, H if "+z" in arms else CW2])]
    i = 0
    for sx in (1, -1):
        for sz in (1, -1):
            if (sz > 0 and "+z" in arms) or (sz < 0 and "-z" in arms):
                parts.append(bx(f"fill{i}", "asphalt", [sx * CW2, sx * PW2], [-0.12, YA], [sz * CW2, sz * PW2]))
                parts += corner_pave(i, sx, sz, r, H)
            i += 1
    if "-z" not in arms:   # (a T: the far side runs straight past)
        parts += [bx("kerbS", "kerb", [-H, H], [-0.12, YK], [-CW2 - KW, -CW2]), bx("paveS", "pave", [-H, H], [-0.12, YP], [-PW2, -CW2 - KW])]
    # (markings: the priority road's centre line dashed through, the side arms' give-way lines across their incoming lane)
    parts.append(stripes("centreX", "line", -H, -CW2 - 1, 0, 0.12, 2, 1.5))
    parts.append(stripes("centreX2", "line", CW2 + 1.5, H, 0, 0.12, 2, 1.5))
    gw = []
    for sz in (1, -1):
        if (sz > 0 and "+z" in arms) or (sz < 0 and "-z" in arms):
            zline = sz * (CW2 + r + 0.6)
            # (traffic coming in along -z*sz keeps right: on the +z arm it heads -z, so its lane is x > 0)
            xs = [sz * (0.35 + 0.75 * k) for k in range(5)]
            gw += [[x, YA + 0.002, zline] for x in xs]
            parts.append(box(f"centreZ{sz}", "line", [0.12, 0.004, H - CW2 - r - 1.2], [0, YA + 0.002, sz * (H + CW2 + r + 1.2) / 2]))
            parts += give_way_sign(f"gw{sz}", sz * (CW2 + KW + 0.6), sz * (CW2 + r + 1.6), 0 if sz > 0 else 180)
    if gw: parts.append(box("giveWay", "line", [0.5, 0.004, 0.3], gw))
    return item(title, "infrastructure",
        f"a {'crossroads' if len(arms) == 4 else 'T-junction'} of the two-lane road, 17 x 17 m (TILE 17 m: ports at x +-8.5{' and z +-8.5' if len(arms) == 4 else ' and z +8.5'}, each arm 5 m of road beyond the crossing): kerbs round the corners on a 3 m radius, the road along x has priority, the side {'arms' if len(arms) == 4 else 'arm'} a give-way line and sign.",
        {**ROAD_MATS, "post": "paint-grey", "signRed": "paint-red", "signWhite": "paint-white"}, parts)


def zebra():
    # A ZEBRA CROSSING: the straight road with seven white bars across the carriageway (0.5 m, 0.5 m apart, 4 m long
    # along the road), dropped kerbs with tactile paving, and a crossing sign on a post each side
    parts = [use("road", I + "road-straight", [0, 0, 0], {"centre": 0})]
    zs = [-3.0 + k for k in range(7)]
    parts.append(box("bars", "line", [4.0, 0.004, 0.5], [[0, YA + 0.0025, z] for z in zs]))
    parts.append(bx("tactile", "tactile", [-1.8, 1.8], [YP, YP + 0.012], [CW2 + KW + 0.05, CW2 + KW + 0.85], mirror="z"))
    for sz in (1, -1):
        x = 2.4 * sz
        parts += [rod(f"post{sz}", "post", 0.035, [x, YP, sz * 4.9], [x, 2.9, sz * 4.9], 8),
                  box(f"sign{sz}", "signBlue", [0.03, 0.6, 0.6], [x, 2.55, sz * 4.9]),
                  plate(f"signTri{sz}", "signWhite", [[0, 0.2], [0.21, -0.17], [-0.21, -0.17]], 0.04, [x, 2.55, sz * 4.9, 90, 0, 0]),
                  sphere(f"beacon{sz}", "beacon", 0.15, [x, 3.0, sz * 4.9], sides=12)]
    return item("Zebra crossing", "infrastructure",
        "the straight road (TILE 10 m, ports at x +-5) with a zebra crossing: seven white bars 0.5 m wide across both lanes, tactile paving at the kerbs, a blue crossing sign and an amber globe on a post each side.",
        {**ROAD_MATS, "tactile": "#d2c08a", "post": "paint-grey", "signBlue": "paint-blue", "signWhite": "paint-white", "beacon": "lamp-amber"}, parts)


def roundabout():
    # A ROUNDABOUT: a ring 7 m wide round a grassed island (R 8 inside a cobbled overrun apron), four arms of the
    # road meeting it, each with a raised splitter island and a give-way line round the ring's edge; pavements round
    # the outside between the arms. Tile 50 x 50, ports at the four edges' middles.
    H, Ro, Ri, Ra = 25.0, 15.0, 8.0, 6.5
    parts = [
        lathe("ring", "asphalt", [[Ro, -0.12], [Ro, YA], [Ri - 0.1, YA]], [0, 0, 0], sides=56, caps=False),
        bx("armX", "asphalt", [-H, H], [-0.12, YA], [-CW2, CW2]), bx("armZ", "asphalt", [-CW2, CW2], [-0.12, YA], [-H, H]),
        lathe("apronKerb", "kerb", [[Ri + 0.15, YA], [Ri + 0.15, 0.08], [Ri, 0.1], [Ri, YA]], [0, 0, 0], sides=48, caps=False),
        lathe("apron", "cobbles", [[Ri, 0.1], [Ra, 0.1]], [0, 0, 0], sides=48, caps=False),
        lathe("islandKerb", "kerb", [[Ra + 0.15, 0.1], [Ra + 0.15, 0.25], [Ra, 0.25]], [0, 0, 0], sides=48, caps=False),
        lathe("island", "grass", [[Ra, 0.25], [Ra * 0.6, 0.45], [0, 0.55]], [0, 0, 0], sides=40, caps=False),
        sphere("bush", "bush", 1.2, [[2.2, 0.6, 1.4], [-1.8, 0.6, 2.0], [0.6, 0.6, -2.4], [-2.4, 0.55, -1.1]], stretch=[1, 0.7, 1], sides=10),
        rod("treeTrunk", "bark", 0.15, [0, 0.5, 0], [0, 3.0, 0], 8),
        sphere("treeCrown", "bush", 2.0, [0, 4.0, 0], stretch=[1, 1.1, 1], sides=12),
    ]
    a, b = CW2, CW2 + KW
    for i, (sx, sz) in enumerate([(1, 1), (1, -1), (-1, 1), (-1, -1)]):
        xa, xb = math.sqrt((Ro + KW) ** 2 - b ** 2), math.sqrt((Ro + KW + 1.85) ** 2 - PW2 ** 2)
        t0, t1 = math.degrees(math.atan2(b, xa)), math.degrees(math.atan2(PW2, xb))
        pts = [[H, b], [xa, b]] + arc_xz(0, 0, Ro + KW, t0, 90 - t0, 12)[1:-1] + [[b, xa], [b, H], [PW2, H], [PW2, xb]] + arc_xz(0, 0, Ro + KW + 1.85, 90 - t1, t1, 12)[1:-1] + [[xb, PW2], [H, PW2]]
        parts.append(flat(f"pave{i}", "pave", [[x * sx, z * sz] for x, z in pts], YP, YP + 0.12))
        xk = math.sqrt((Ro + KW / 2) ** 2 - (a + KW / 2) ** 2); tk = math.degrees(math.atan2(a + KW / 2, xk))
        kp = [[H, a + KW / 2], [xk, a + KW / 2]] + arc_xz(0, 0, Ro + KW / 2, tk, 90 - tk, 12)[1:-1] + [[a + KW / 2, xk], [a + KW / 2, H]]
        parts.append(sweep(f"kerb{i}", "kerb", [[x * sx, (YK - 0.12) / 2, z * sz] for x, z in kp], section=[KW, YK + 0.12], up=[0, 1, 0], seg=1))
    # (each arm: a splitter island -- a raised teardrop between the lanes -- and the give-way dashes across its entry)
    split = [[Ro + 0.5, 0], [Ro + 2.0, 0.75], [Ro + 7.0, 0.55], [Ro + 9.5, 0], [Ro + 7.0, -0.55], [Ro + 2.0, -0.75]]
    gwd = []
    for k, yaw in enumerate((0, 90, 180, 270)):
        c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        rot = lambda x, z: [x * c - z * s, z * c + x * s]
        parts.append(flat(f"split{k}", "kerb", [rot(x, z) for x, z in split], 0.15, 0.13))
        # (traffic coming in keeps right: on the +x arm it heads -x, its lane z < 0; its dashes curve along the ring)
        for j in range(4):
            z = -0.55 - 0.8 * j; x = math.sqrt((Ro + 0.25) ** 2 - z * z)
            gx, gz = rot(x, z)
            gwd.append([gx, YA + 0.002, gz, -yaw, 0, 0])
        parts.append(box(f"centre{k}", "line", [H - Ro - 9.5, 0.004, 0.12], [*[(rot((H + Ro + 9.5) / 2, 0))[0]], YA + 0.002, rot((H + Ro + 9.5) / 2, 0)[1], yaw, 0, 0]))
    parts.append(box("giveWay", "line", [0.3, 0.004, 0.5], gwd))
    return item("Roundabout", "infrastructure",
        "a roundabout on the two-lane road, 50 x 50 m (TILE 50 m: ports at x +-25 and z +-25): a ring 7 m wide round a cobbled overrun apron and a grassed island (R 6.5) with shrubs and a tree, a raised splitter island on each arm, give-way dashes at each entry, kerbs and pavements round the outside.",
        {**ROAD_MATS, "cobbles": "stone", "grass": "#5d7f3a", "bush": "leaf", "bark": "#5a4636"}, parts)


# ==================================================================================================================
# RAILWAY TRACK
# ==================================================================================================================
TRACK_MATS = {"ballast": "#7d7872", "sleeper": "concrete", "rail": "steel", "clip": "#3a3c3f"}


def rail_boxes(id_, x0, x1, z, mirror=True):
    """one flat-bottomed rail (UIC 60's: foot 150 mm, web 17, head 72; 172 tall) straight along x, its centre at z"""
    L, xc, m = x1 - x0, (x0 + x1) / 2, {"mirror": "z"} if mirror else {}
    return [box(id_ + "Foot", "rail", [L, 0.012, 0.15], [xc, RF + 0.006, z], **m),
            box(id_ + "Web", "rail", [L, 0.11, 0.017], [xc, RF + 0.067, z], **m),
            box(id_ + "Head", "rail", [L, 0.05, 0.072], [xc, RT - 0.025, z], **m)]


def rail_sweeps(id_, pts):
    """the same rail along a path of ground points [x, z]"""
    P = lambda y: [[x, y, z] for x, z in pts]
    return [sweep(id_ + "Foot", "rail", P(RF + 0.006), section=[0.15, 0.012], up=[0, 1, 0], seg=1),
            sweep(id_ + "Web", "rail", P(RF + 0.067), section=[0.017, 0.11], up=[0, 1, 0], seg=1),
            sweep(id_ + "Head", "rail", P(RT - 0.025), section=[0.072, 0.05], up=[0, 1, 0], seg=1)]


def ballast(id_, L, at=None, wide=0.0):
    """the ballast bed: a trapezoid 4.6 m at the formation, 3.2 m at the top (0.40), L long along x"""
    s = [[-L / 2, 2.3 + wide, 0, 0.40, 1.6 + wide], [L / 2, 2.3 + wide, 0, 0.40, 1.6 + wide]]
    return loft(id_, "ballast", s, [0.02, 0.06], seg=1, corner=2, **({"at": at} if at else {}))


def track_straight():
    # STRAIGHT TRACK, 10 m: 16 concrete sleepers on the ballast, two rails on them, a clip each side of each rail on
    # each sleeper (`clips` 0 leaves them off: a station's long platforms of track, seen from a distance)
    L, n = 10.0, 16
    parts = [ballast("ballast", L),
             box("sleeper", "sleeper", [0.26, 0.22, 2.6], [0, 0.36, 0], along={"n": n, "from": [-L / 2 + L / n / 2, 0, 0], "to": [L / 2 - L / n / 2, 0, 0]}),
             *rail_boxes("rail", -L / 2, L / 2, RC),
             box("clip", "clip", [0.07, 0.04, 0.05], [[0, RF + 0.02, RC + 0.105], [0, RF + 0.02, RC - 0.105]], along={"n": n, "from": [-L / 2 + L / n / 2, 0, 0], "to": [L / 2 - L / n / 2, 0, 0]}, mirror="z", when="clips")]
    return item("Track, straight", "infrastructure",
        "straight railway track, 10 m (TILE 10 m: ports at x +-5, the track along x): flat-bottomed rails on the standard gauge (1.435 m) on 16 concrete sleepers (2.6 m, 0.625 m apart) with their clips, on a ballast bed 4.6 m wide. The formation at y 0; the RAIL TOP at y 0.642 -- a train (its origin on the rail) stands there.",
        TRACK_MATS, parts, params={"clips": 1}, markers=[{"role": "rail", "at": [0, RT, 0], "data": {"gauge": G}}])


def track_curve():
    # CURVED TRACK: a 15 degree arc of R 150 (39.3 m along the centre line; 6 make a quarter turn), entering at the
    # origin heading +x, turning right; the sleepers laid radially, the rails swept, the ballast as short straight beds
    R, A = 150.0, 15.0
    Lc = R * math.radians(A); n = round(Lc / 0.625); nb = 8
    sl = [on_arc(R, A * (i + 0.5) / n, 0, 0.36) + [0, 0] for i in range(n)]
    bl = R * math.radians(A / nb) + 0.1
    parts = [ballast("ballast", bl, [on_arc(R, A * (i + 0.5) / nb) + [0, 0] for i in range(nb)]),
             box("sleeper", "sleeper", [0.26, 0.22, 2.6], sl),
             *rail_sweeps("railR", [[p[0], p[2]] for p in arc_path(R, 0, A, RC, 0, 16)]),
             *rail_sweeps("railL", [[p[0], p[2]] for p in arc_path(R, 0, A, -RC, 0, 16)])]
    clips = []
    for i in range(n):
        th = A * (i + 0.5) / n
        for o in (RC + 0.105, RC - 0.105, -RC + 0.105, -RC - 0.105): clips.append(on_arc(R, th, o, RF + 0.02) + [0, 0])
    parts.append(box("clip", "clip", [0.07, 0.04, 0.05], clips, when="clips"))
    e = on_arc(R, A)
    return item("Track, curve", "infrastructure",
        f"curved railway track: a {A:.0f} degree arc of radius {R:.0f} m ({Lc:.1f} m along it; six make a quarter turn), entering at the origin heading +x and turning right, leaving at ({e[0]:.2f}, 0, {e[2]:.2f}) heading {A:.0f} degrees toward +z. Rails, sleepers laid radially, clips, ballast; rail top at y 0.642.",
        TRACK_MATS, parts, params={"clips": 1}, markers=[{"role": "rail", "at": [0, RT, 0], "data": {"gauge": G}}])


def turnout():
    # A SET OF POINTS (a right-hand turnout, 1:7 on R 190): two stock rails, the left one straight, the right one
    # curving away; the two switch blades from the toe -- the straight route's right rail, the diverging route's left
    # -- crossing at the frog, with check rails opposite it; long timbers widening under both routes, a point machine
    # at the toe with its stretcher bars. 30 m: x -15..15; the toe at x -12.
    R, x0, L = 190.0, -12.0, 30.0
    d = lambda x: 0.0 if x <= x0 else R - math.sqrt(R * R - (x - x0) ** 2)
    xs = [x0 + (15 - x0) * i / 18 for i in range(19)]
    xf = x0 + math.sqrt(R * R - (R - (2 * RC)) ** 2)      # (the frog: where the two inner rails cross)
    angE = math.degrees(math.asin((15 - x0) / R))
    parts = [ballast("ballast", L)]
    nb = 5
    for i in range(nb):   # (the diverging route's ballast: short beds along its curve)
        xa = x0 + 8 + (15 - x0 - 8) * (i + 0.5) / nb
        parts.append(ballast(f"ballastD{i}", (15 - x0 - 8) / nb + 0.3, [xa, 0, d(xa), yaw_of(1, (xa - x0) / math.sqrt(R * R - (xa - x0) ** 2)), 0, 0]))
    sl = []
    n = 48
    for i in range(n):
        x = -L / 2 + L / n * (i + 0.5); z1 = RC + d(x) + 0.55
        sl.append(([x, 0.36, (z1 - 1.3) / 2], z1 + 1.3))
    # (the timbers as one part: x stepping on, z1 their far end over the diverging rail -- d(x) written out, rounded
    #  to the millimetre's tenth as each was)
    t = "max(0, 0.625 * i - 2.6875)"   # (x - x0, from the toe on)
    dx = f"(190 - sqrt(36100 - {t} * {t}))"   # (d(x))
    parts += each("timber", [box(f"timber{k}", "sleeper", [0.26, 0.22, ln], at) for k, (at, ln) in enumerate(sl)],
                  like=box("timber", "sleeper", [0.26, 0.22, f"round((2.6035 + {dx}) * 10000) / 10000"], ["-14.6875 + 0.625 * i", 0.36, f"round((0.0035 + {dx}) / 2 * 10000) / 10000"]))
    parts += rail_boxes("stockL", -L / 2, L / 2, -RC, mirror=False)
    parts += rail_sweeps("stockR", [[-L / 2, RC]] + [[x, RC + d(x)] for x in xs])
    parts += rail_boxes("bladeS", x0 + 0.3, L / 2, RC - 0.004, mirror=False)
    parts += rail_sweeps("bladeD", [[x0 + 0.3, -RC + 0.004]] + [[x, -RC + d(x)] for x in xs[1:]])
    parts += rail_boxes("checkL", xf - 2.5, xf + 2.5, -RC + 0.117, mirror=False)
    parts += rail_sweeps("checkR", [[x, RC + d(x) - 0.117] for x in (xf - 2.5, xf - 1.2, xf, xf + 1.2, xf + 2.5)])
    parts += [box("frog", "clip", [2.2, 0.06, 0.3], [xf + 0.6, RT - 0.08, RC, -angE / 4, 0, 0]),
              rod("stretcher", "clip", 0.02, [0, RT - 0.07, -RC - 0.05], [0, RT - 0.07, RC + 0.05], 6, at=[[x0 + 0.5, 0, 0], [x0 + 1.4, 0, 0]]),
              bx("machine", "machine", [x0 - 0.1, x0 + 0.9], [0.3, 0.62], [-RC - 1.2, -RC - 0.4]),
              rod("drive", "clip", 0.02, [x0 + 0.5, RT - 0.07, -RC - 0.45], [x0 + 0.5, RT - 0.07, -RC], 6),
              *[box("clip", "clip", [0.07, 0.04, 0.05], [[a[0], RF + 0.02, -RC + o] for (a, _) in sl for o in (0.105, -0.105)], when="clips")]]
    zE = d(15)
    return item("Points (turnout)", "infrastructure",
        f"a set of points: a right-hand turnout on R 190 m, 30 m long (x -15..15; the toe at x -12, the frog at x {xf:.1f}). Ports: x -15 (heading -x), x +15 straight on, and the diverging route at (15, 0, {zE:.2f}) heading {angE:.1f} degrees toward +z. Stock rails, switch blades, frog and check rails, long timbers under both routes, the point machine and stretcher bars. Rail top y 0.642.",
        {**TRACK_MATS, "machine": "paint-yellow"}, merge(parts), params={"clips": 1})


def buffer_stop():
    # THE END OF THE LINE: 10 m of track and a buffer stop on it -- a steel frame of rails bent up (two raking struts
    # each side), the red-and-white buffer beam with two sprung buffers at the standard height (1.06 m over the rail,
    # 1.75 m apart), and a red lamp. Trains come from -x.
    xb, yb = 3.0, RT + 1.06
    parts = [use("track", I + "track-straight", [0, 0, 0])]
    parts += [box("post", "frame", [0.15, yb + 0.25 - RT, 0.12], [xb + 0.1, (yb + 0.25 + RT) / 2, RC], mirror="z"),
              rod("strut", "frame", 0.07, [xb + 2.2, RT, RC], [xb + 0.2, yb + 0.2, RC], 6, mirror="z"),
              rod("strut2", "frame", 0.06, [xb + 1.4, RT, RC], [xb + 0.2, yb - 0.3, RC], 6, mirror="z"),
              box("beam", "beamRed", [0.3, 0.5, 2.6], [xb, yb, 0]),
              box("band", "beamWhite", [0.31, 0.51, 0.3], [[xb, yb, -0.9], [xb, yb, -0.3], [xb, yb, 0.3], [xb, yb, 0.9]]),
              lathe("buffer", "frame", [[0, 0], [0.12, 0], [0.12, 0.3], [0.08, 0.3], [0.08, 0.45]], [xb - 0.15, yb, 0.875, 0, 0, 90], sides=12, mirror="z"),
              lathe("bufferHead", "bufferFace", [[0, -0.03], [0.22, -0.03], [0.22, 0.03], [0, 0.03]], [xb - 0.62, yb, 0.875, 0, 0, 90], sides=16, mirror="z"),
              rod("lampPost", "frame", 0.03, [xb, yb + 0.25, 0], [xb, yb + 0.6, 0], 6),
              use("lamp", C + "lamp", [xb - 0.08, yb + 0.7, 0, 180, 0, 0], {"r": 0.09}, {"lens": "lamp-red", "bezel": "frame"}),
              box("lampBox", "frame", [0.14, 0.24, 0.24], [xb, yb + 0.7, 0])]
    return item("Buffer stop", "infrastructure",
        "the end of a line: 10 m of track (TILE 10 m, its one port at x -5; trains come from -x) with a buffer stop at x 3 -- a frame of bent rails with raking struts, a red-and-white buffer beam carrying two sprung buffers 1.06 m above the rail and 1.75 m apart, a red lamp on top.",
        {"frame": "#2d2f31", "beamRed": "paint-red", "beamWhite": "paint-white", "bufferFace": "steel"}, parts)


def crossing_barrier():
    # A LEVEL CROSSING'S BARRIER: the post with its boom (red and white, 4 m), the counterweight behind the pivot, a
    # St Andrew's cross above and twin red flashers facing the traffic (+x); the boom reaches across the lane to +z.
    # `down` 1 lowered, 0 raised.
    Lb, yp = 4.2, 1.0
    seg = 0.5
    parts = [bx("base", "concrete", [-0.3, 0.3], [0, 0.15], [-0.3, 0.3]),
             bx("post", "postGrey", [-0.12, 0.12], [0.15, 1.3], [-0.15, 0.15]),
             rod("mast", "postGrey", 0.05, [0, 1.3, 0], [0, 3.1, 0], 8),
             box("crossA", "crossWhite", [0.04, 1.25, 0.17], [0.06, 2.75, 0, 0, 45, 0]),
             box("crossB", "crossWhite", [0.04, 1.25, 0.17], [0.06, 2.75, 0, 0, -45, 0]),
             box("crossEdge", "crossRed", [0.035, 1.29, 0.21], [0.05, 2.75, 0, 0, 45, 0]),
             box("crossEdge2", "crossRed", [0.035, 1.29, 0.21], [0.05, 2.75, 0, 0, -45, 0]),
             box("lampBar", "postGrey", [0.06, 0.08, 0.9], [0.07, 2.05, 0]),
             use("flash", C + "lamp", [0.12, 2.05, 0.32], {"r": 0.1}, {"lens": "lamp-red", "bezel": "postGrey"}, mirror="z"),
             box("hood", "postGrey", [0.18, 0.02, 0.22], [0.16, 2.17, 0.32], mirror="z"),
             box("counter", "postGrey", [0.3, 0.3, 0.3], [0, yp, -0.45])]
    # (the boom: red and white lengths, lowered across the lane or raised to stand up)
    reds = [[0, yp, 0.3 + seg * (2 * k + 0.5)] for k in range(int(Lb / seg / 2))]
    whites = [[0, yp, 0.3 + seg * (2 * k + 1.5)] for k in range(int(Lb / seg / 2))]
    parts += [box("boomR", "crossRed", [0.08, 0.1, seg], reds, when="down"), box("boomW", "crossWhite", [0.08, 0.1, seg], whites, when="down"),
              box("boomRU", "crossRed", [0.08, seg, 0.1], [[0, yp + 0.3 + seg * (2 * k + 0.5), 0.22] for k in range(int(Lb / seg / 2))], when={"down": 0}),
              box("boomWU", "crossWhite", [0.08, seg, 0.1], [[0, yp + 0.3 + seg * (2 * k + 1.5), 0.22] for k in range(int(Lb / seg / 2))], when={"down": 0}),
              bx("pivotBox", "postGrey", [-0.14, 0.14], [yp - 0.15, yp + 0.15], [0.12, 0.32])]
    return item("Level crossing barrier", "infrastructure",
        "a level crossing's half barrier: a post with its red-and-white boom 4.2 m long (lowered across the lane toward +z, or raised: `down`), the counterweight, a St Andrew's cross on the mast and twin red flashers facing the traffic (+x).",
        {"postGrey": "paint-grey", "crossWhite": "paint-white", "crossRed": "paint-red", "concrete": "concrete"}, parts, params={"down": 1})


def level_crossing():
    # A LEVEL CROSSING: 20 m of track along x and the road crossing it along z; between and beside the rails the road
    # is laid in concrete panels flush with the rail heads (flangeways open inside each rail), ramps down to the road
    # each side; half barriers on each approach's right, lowered.
    H, xr = 10.0, CW2
    yt = RT - 0.004
    parts = [use("trackA", I + "track-straight", [-5, 0, 0]), use("trackB", I + "track-straight", [5, 0, 0]),
             bx("panelIn", "panel", [-xr, xr], [0.38, yt], [-RC + 0.08, RC - 0.08]),
             bx("panelOut", "panel", [-xr, xr], [0.38, yt], [RC + 0.06, 2.4], mirror="z")]
    # (the ramps: from the panels' edge down to the road's level at 7 m)
    z0, z1 = 2.4, 7.0
    sl = math.degrees(math.atan2(yt - YA, z1 - z0)); ln = math.hypot(yt - YA, z1 - z0)
    for s, nm in ((1, "rampP"), (-1, "rampN")):
        zc, yc = s * (z0 + z1) / 2, (yt + YA) / 2 - 0.15
        parts.append(box(nm, "asphalt", [2 * xr, 0.3, ln], [0, yc, zc, 0, s * sl, 0]))
        parts.append(box(nm + "Bank", "earth", [2 * xr + 3, 0.6, ln], [0, yc - 0.25, zc, 0, s * sl, 0]))
        parts.append(bx(nm + "Flat", "asphalt", [-xr, xr], [-0.12, YA], sorted([s * z1, s * H])))
        parts.append(box(nm + "Line", "line", [0.12, 0.004, H - z1], [0, YA + 0.002, s * (z1 + H) / 2]))
        parts.append(box(nm + "Edge", "line", [0.12, 0.004, H - z1], [xr - 0.3, YA + 0.002, s * (z1 + H) / 2], mirror="x"))
        parts.append(box(nm + "Stop", "line", [xr, 0.004, 0.4], [s * xr / 2, YA + 0.002, s * 8.6]))
    parts += [use("barrierA", I + "crossing-barrier", [xr + 0.9, 0, 7.4, -90, 0, 0], {"down": "down"}),
              use("barrierB", I + "crossing-barrier", [-xr - 0.9, 0, -7.4, 90, 0, 0], {"down": "down"})]
    return item("Level crossing", "infrastructure",
        "a level crossing, 20 x 20 m: track along x (ports x +-10, rail top 0.642) and the two-lane road along z (ports z +-10, asphalt at 0.02), the road laid in concrete panels flush with the rails and ramped down each side, stop lines, and a half barrier with St Andrew's cross and flashers on each approach's right (`down`: lowered).",
        {**TRACK_MATS, **ROAD_MATS, "panel": "#8f8c86", "earth": "#7a6a52"}, parts, params={"down": 1})


# ==================================================================================================================
# STATION FURNITURE (small items the stations share)
# ==================================================================================================================
def bench():
    # A PLATFORM BENCH: three perforated steel seats' worth (1.8 m) on two cast end frames, facing +x
    w = 1.8
    parts = [box("leg", "benchFrame", [0.42, 0.42, 0.06], [-0.02, 0.21, w / 2 - 0.15], mirror="z"),
             box("backPost", "benchFrame", [0.05, 0.45, 0.06], [-0.24, 0.66, w / 2 - 0.15, 0, 0, 12], mirror="z"),
             box("slat", "benchSeat", [0.12, 0.03, w], [[0.12, 0.44, 0], [-0.02, 0.44, 0], [-0.16, 0.44, 0]]),
             box("backSlat", "benchSeat", [0.03, 0.12, w], [[-0.25, 0.6, 0, 0, 0, 12], [-0.28, 0.76, 0, 0, 0, 12]])]
    return item("Bench", "infrastructure", "a platform or bus-stop bench, 1.8 m: slatted seat and back on two end frames, its front at +x, the seat 0.45 high",
        {"benchFrame": "#3b4045", "benchSeat": {"pick": ["oak", "#5a6e7c", "#7b2c2c"]}}, parts)


def departure_board():
    # A DEPARTURE BOARD: a wide screen facing +x (and -x, `double`), its rows of amber text -- the time, the
    # destination, the platform -- hung on two rods (`hang` metres) or standing on a post (`post` metres)
    parts = [use("face", C + "screen", [0.035, 0, 0], {"w": "w", "h": "h", "t": 0.035, "b": 0.03}, {"case": "boardCase", "glass": "screen"})]
    parts.append(use("back", C + "screen", [-0.035, 0, 0, 180, 0, 0], {"w": "w", "h": "h", "t": 0.035, "b": 0.03}, {"case": "boardCase", "glass": "screen"}, when="double"))
    rows = [[0.04, "h / 2 - h * (0.16 + 0.15 * k)".replace("k", str(k)), 0] for k in range(6)]
    for nm, mat, wd, zc in (("time", "textAmber", "w * 0.12", "-w * 0.4"), ("dest", "textAmber", "w * 0.48", "-w * 0.03"), ("plat", "textWhite", "w * 0.06", "w * 0.4")):
        parts.append(box(nm, mat, [0.004, "h * 0.075", wd], [[r[0], r[1], zc] for r in rows]))
        parts.append(box(nm + "B", mat, [0.004, "h * 0.075", wd], [[-r[0], r[1], f"0 - ({zc})"] for r in rows], when="double"))
    parts.append(box("header", "textHead", [0.004, "h * 0.1", "w * 0.96"], [[0.04, "h / 2 - h * 0.06", 0], [-0.04, "h / 2 - h * 0.06", 0]]))
    parts += [rod("hang", "boardCase", 0.02, [0, "h / 2", "-w * 0.35"], [0, "h / 2 + hang", "-w * 0.35"], 6, mirror="z", when="hang"),
              rod("post", "boardCase", 0.06, [0, "-h / 2", 0], [0, "-h / 2 - post", 0], 10, when="post")]
    return item("Departure board", "infrastructure", "a departure board: a wide screen with six rows of amber departures (time, destination, platform), facing +x and, if `double`, -x too; hung on rods `hang` m long or stood on a post `post` m tall. Its origin at the screen's middle.",
        {"boardCase": "#25282c", "textAmber": "lamp-amber", "textWhite": "paint-white", "textHead": "#2f6aa8"}, parts, params={"w": 2.4, "h": 0.8, "double": 1, "hang": 0, "post": 0})


def clock():
    # A STATION CLOCK: a two-faced round clock (faces +x and -x), white dials with black hour marks and hands, on a
    # bracket arm from its top
    R = 0.4
    ticks = []
    for k in range(12):
        a = math.radians(k * 30); ticks.append([0, 0.8 * R * math.cos(a), 0.8 * R * math.sin(a), 0, 0, 0])
    tk = [[s * 0.063, t[1], t[2], 0, k * 30, 0] for k, t in enumerate(ticks) for s in (1, -1)]
    parts = [lathe("case", "clockCase", [[0, -0.06], [R, -0.06], [R + 0.02, 0], [R, 0.06], [0, 0.06]], [0, 0, 0, 0, 0, -90], sides=28),
             lathe("dial", "dial", [[0, -0.062], [R * 0.93, -0.062], [R * 0.93, 0.062], [0, 0.062]], [0, 0, 0, 0, 0, -90], sides=28),
             box("tick", "hands", [0.006, 0.07, 0.025], tk),
             box("hour", "hands", [0.008, 0.2, 0.03], [[0.066, 0.08, 0.03, 0, -20, 0], [-0.066, 0.08, -0.03, 0, 20, 0]]),
             box("minute", "hands", [0.008, 0.3, 0.02], [[0.07, -0.02, -0.14, 0, 60, 0], [-0.07, -0.02, 0.14, 0, -60, 0]]),
             rod("arm", "clockCase", 0.03, [0, R, 0], [0, R + 0.4, 0], 8)]
    return item("Station clock", "infrastructure", "a station clock: two white dials 0.8 m across, back to back (facing +x and -x), black marks and hands, hung from an arm at its top; its origin at the dial's centre",
        {"clockCase": "#2a2c2f", "dial": "paint-white", "hands": "paint-black"}, parts)


def ticket_machine():
    # A TICKET MACHINE: a cabinet with its touch screen, a card slot, a coin slot and the ticket tray, facing +x
    parts = [bx("cab", "tmBody", [-0.25, 0.2], [0, 1.75], [-0.4, 0.4]),
             bx("hoodT", "tmBody", [-0.25, 0.3], [1.65, 1.8], [-0.42, 0.42]),
             use("screen", C + "screen", [0.205, 1.25, 0, 0, 0, 0], {"w": 0.5, "h": 0.4, "t": 0.02}, {"case": "tmFace", "glass": "screen"}),
             bx("pad", "tmFace", [0.2, 0.26], [0.85, 1.0], [-0.25, 0.25]),
             bx("slot", "hands", [0.2, 0.22], [0.6, 0.66], [-0.15, 0.15]),
             bx("tray", "hands", [0.19, 0.23], [0.3, 0.4], [-0.2, 0.2]),
             bx("band", "tmStripe", [0.2, 0.21], [1.55, 1.62], [-0.4, 0.4])]
    return item("Ticket machine", "infrastructure", "a ticket machine: a cabinet 1.8 m tall with a touch screen, keypad, card and coin slots and a ticket tray, facing +x",
        {"tmBody": {"pick": ["paint-red", "paint-blue", "#1f5f3a"]}, "tmFace": "#2c2f33", "hands": "paint-black", "tmStripe": "paint-white"}, parts)


def stair_flight():
    # A STAIR FLIGHT: steps of ~17 cm on 29 cm treads rising toward +x from its foot at the origin to `H` (the top
    # landing edge at x H * 1.7), `w` wide, on a sloping concrete slab, with handrails both sides
    parts = [box("step", "stepMat", ["H * 1.7 / (H / 0.17)", 0.17, "w"], [0, 0, 0], along={"n": "H / 0.17", "from": ["H * 1.7 / (H / 0.17) / 2", 0.085, 0], "to": ["H * 1.7 - H * 1.7 / (H / 0.17) / 2", "H - 0.085", 0]}),
             plate("string", "stairSide", [[0, 0], [0.35, 0], ["H * 1.7", "H - 0.35"], ["H * 1.7", "H + 0.08"], ["H * 1.7 - 0.25", "H + 0.08"], [-0.25, 0.08]], 0.08, [0, 0, "w / 2 + 0.04"], mirror="z"),
             rod("rail", "handrail", 0.025, [-0.2, 1.0, "w / 2 + 0.02"], ["H * 1.7", "H + 1.0", "w / 2 + 0.02"], 8, mirror="z"),
             rod("baluster", "handrail", 0.018, [0, 0.08, "w / 2 + 0.02"], [0, 1.0, "w / 2 + 0.02"], 6, along={"n": "H / 0.8 + 1", "from": [0, 0, 0], "to": ["H * 1.7", "H", 0]}, mirror="z"),
             box("under", "stairSide", ["H * 1.972", 0.2, "w"], ["H * 0.85 + 0.05", "H / 2 - 0.16", 0, 0, 0, 30.47])]
    return item("Stair flight", "infrastructure", "a straight stair: 17 cm risers on 29 cm treads, rising toward +x from its foot at the origin to a height H (its top edge at x 1.7 H), w wide, a sloping slab under it, stringers and handrails both sides",
        {"stepMat": "#a9a59c", "stairSide": "#8d8a84", "handrail": "steel"}, parts, params={"H": 3.4, "w": 2.0})


# ==================================================================================================================
# PLATFORM, CANOPY, SHED, FOOTBRIDGE
# ==================================================================================================================
def platform():
    # A PLATFORM SEGMENT, 10 m: its top 0.76 above the rail (y 1.40), `W` wide; an ISLAND (`island` 1: edges both
    # sides) or a side platform (edge at +z only, a railing at the back). The coping overhangs the wall, a white
    # safety line 0.9 m in, tactile strip; on top a canopy (`canopy`: columns down the middle, a cantilevered roof with
    # its fascia and lights, a hanging departure board and the platform's sign) or a lamp; benches and a bin.
    parts = [
        box("body", "platWall", [10, PH - 0.12, "W - 0.6"], [0, (PH - 0.12) / 2, 0], when="island"),
        box("bodyS", "platWall", [10, PH - 0.12, "W - 0.3"], [0, (PH - 0.12) / 2, -0.15], when={"island": 0}),
        box("top", "platTop", [10, 0.12, "W"], [0, PH - 0.06, 0]),
        box("coping", "coping", [10, 0.125, 0.5], [0, PH - 0.0625, "W / 2 - 0.25"], **{"mirror": "z"}, when="island"),
        box("copingS", "coping", [10, 0.125, 0.5], [0, PH - 0.0625, "W / 2 - 0.25"], when={"island": 0}),
        box("line", "safety", [10, 0.004, 0.1], [0, PH + 0.002, "W / 2 - 0.9"], mirror="z", when="island"),
        box("lineS", "safety", [10, 0.004, 0.1], [0, PH + 0.002, "W / 2 - 0.9"], when={"island": 0}),
        box("tactile", "tactile", [10, 0.008, 0.3], [0, PH + 0.004, "W / 2 - 0.6"], mirror="z", when="island"),
        box("tactileS", "tactile", [10, 0.008, 0.3], [0, PH + 0.004, "W / 2 - 0.6"], when={"island": 0}),
    ]
    # (the back of a side platform: a railing)
    parts += [rod("fenceTop", "fence", 0.03, [-5, PH + 1.1, "0.15 - W / 2"], [5, PH + 1.1, "0.15 - W / 2"], 6, when="fence"),
              rod("fenceMid", "fence", 0.015, [-5, PH + 0.55, "0.15 - W / 2"], [5, PH + 0.55, "0.15 - W / 2"], 6, when="fence"),
              rod("fencePost", "fence", 0.025, [0, PH, "0.15 - W / 2"], [0, PH + 1.1, "0.15 - W / 2"], 6, along={"n": 6, "from": [-5, 0, 0], "to": [5, 0, 0]}, when="fence")]
    # (the canopy: two columns down the middle -- at the back of a side platform -- each with a cantilever beam, the
    #  roof a shallow V draining to the middle, its fascia boards, light boxes under it)
    zc = "cz"
    hc = PH + 3.6
    parts += [
        box("col", "steelCol", [0.22, 3.6, 0.22], [[-2.5, PH + 1.8, zc], [2.5, PH + 1.8, zc]], when="canopy"),
        box("colBase", "steelCol", [0.36, 0.08, 0.36], [[-2.5, PH + 0.04, zc], [2.5, PH + 0.04, zc]], when="canopy"),
        box("arm", "steelCol", [0.2, 0.35, "W - 0.8"], [[-2.5, hc - 0.1, "cz + rz"], [2.5, hc - 0.1, "cz + rz"]], when="canopy"),
        box("roofA", "roof", [10.0, 0.12, "(W - 0.8) / 2"], [0, hc + 0.2, "cz + rz + (W - 0.8) / 4", 0, -4, 0], when="canopy"),
        box("roofB", "roof", [10.0, 0.12, "(W - 0.8) / 2"], [0, hc + 0.2, "cz + rz - (W - 0.8) / 4", 0, 4, 0], when="canopy"),
        box("fascia", "fascia", [10.0, 0.45, 0.06], [[0, hc + 0.3, "cz + rz + (W - 0.8) / 2"], [0, hc + 0.3, "cz + rz - (W - 0.8) / 2"]], when="canopy"),
        box("soffit", "soffit", [10.0, 0.04, "W - 0.9"], [0, hc + 0.02, "cz + rz"], when="canopy"),
        box("light", "lightBox", [3.2, 0.06, 0.18], [[-2.5, hc - 0.03, "cz + rz + W / 4"], [2.5, hc - 0.03, "cz + rz + W / 4"], [-2.5, hc - 0.03, "cz + rz - W / 4"], [2.5, hc - 0.03, "cz + rz - W / 4"]], when="canopy"),
        use("board", I + "departure-board", [0, hc - 0.85, "cz + rz", 0, 0, 0], {"w": 1.8, "h": 0.6, "hang": 0.5}, when=["canopy", "board"]),
        # (the platform's sign: a white board with a dark band, hung from the arm)
        box("sign", "signFace", [0.06, 0.45, 2.2], [-2.5, hc - 0.65, "cz + rz + W / 4"], when="canopy"),
        box("signBand", "signBand", [0.07, 0.12, 2.2], [-2.5, hc - 0.5, "cz + rz + W / 4"], when="canopy"),
        rod("signHang", "steelCol", 0.012, [-2.5, hc - 0.43, "cz + rz + W / 4 - 0.8"], [-2.5, hc - 0.1, "cz + rz + W / 4 - 0.8"], 4, at=[[0, 0, 0], [0, 0, 1.6]], when="canopy"),
        # (no canopy: a lamp post instead)
        rod("lampPost", "steelCol", 0.06, [0, PH, "cz"], [0, PH + 4.5, "cz"], 8, when={"canopy": 0}),
        box("lampHead", "lightBox", [0.5, 0.1, 0.25], [0.2, PH + 4.5, "cz"], when={"canopy": 0}),
        use("benchA", I + "bench", [3.8, PH, "cz + 0.5", -90, 0, 0], when="benches"),
        use("benchB", I + "bench", [-3.8, PH, "cz - 0.5", 90, 0, 0], when=["benches", "island"]),
        lathe("bin", "binMat", [[0, 0], [0.2, 0], [0.2, 0.8], [0.18, 0.8], [0.18, 0.75]], [1.0, PH, "cz"], sides=10, caps=False, double=True, when="benches"),
    ]
    return item("Platform", "infrastructure",
        "a railway platform, one 10 m segment (TILE 10 m, ports x +-5): its top 0.76 m above the rail (y 1.40), W wide (6); an island (`island` 1: edges at z +-W/2, each 1.65 m from its track's centre) or a side platform (edge at +z only, a railing behind if `fence`). Coping, white safety line, tactile strip; a canopy on two columns with a V roof, fascias, lights, a hanging departure board and a name sign (`canopy`, `board`) or else a lamp post; benches and a bin (`benches`).",
        {"platWall": "#8e8b85", "platTop": "#b9b5ac", "coping": "#d9d6cf", "safety": "paint-white", "tactile": "#d7d3c8", "fence": "paint-grey",
         "steelCol": "#3d4a57", "roof": "#56606a", "fascia": "#2f5e86", "soffit": "#c9c9c4", "lightBox": "lamp", "signFace": "paint-white", "signBand": "#2f5e86", "binMat": "#3a4048"},
        parts, params={"W": 6.0, "island": 1, "canopy": 1, "board": 1, "benches": 1, "fence": 0, "cz": 0, "rz": 0})


def arch_geom(S, f):
    """a segmental arch of span S and rise f: its radius and its centre's height below the springing"""
    R = (S * S / 4 + f * f) / (2 * f)
    return R, R - f


def shed_roof(id_, L, S, f, ys, n, mats, ribs, glassFrom=0.0, thick=0.06, zc=0.0):
    """a barrel roof of flat facets along x: span S, rise f over the springing ys, n facets (the middle ones glazed
    out to the angle `glassFrom` of the half-angle), ribs (plates) at the x's given, purlins at the facets' joints"""
    R, dc = arch_geom(S, f); yc = ys - dc
    ph0 = math.asin(S / 2 / R)
    out, purl, facets = [], [], []
    for k in range(n):
        a, b = -ph0 + 2 * ph0 * k / n, -ph0 + 2 * ph0 * (k + 1) / n
        m = (a + b) / 2; ch = 2 * R * math.sin((b - a) / 2); rho = R * math.cos((b - a) / 2)
        mat = mats[0] if abs(m) < ph0 * glassFrom else mats[1]
        facets.append((mat, box(f"{id_}F{k}", mat, [L, thick, ch + 0.01], [0, yc + rho * math.cos(m), zc + rho * math.sin(m), 0, math.degrees(m), 0])))
        purl.append([0, yc + (R + 0.05) * math.cos(a), zc + (R + 0.05) * math.sin(a)])
    # (the facets: a run of each material -- zinc, glass, zinc -- laid round the arch by `each`, its angle m in i)
    k0, q4 = 0, lambda e: f"round(({e}) * 10000) / 10000"
    while k0 < n:
        k1 = next((k for k in range(k0, n) if facets[k][0] != facets[k0][0]), n)
        m = f"({-ph0 + ph0 / n * (2 * k0 + 1)!r} + {2 * ph0 / n!r} * i)"
        ch, rho = 2 * R * math.sin(ph0 / n), R * math.cos(ph0 / n)
        like = box(f"{id_}F", facets[k0][0], [L, thick, ch + 0.01], [0, q4(f"{yc!r} + {rho!r} * cos({m})"), q4(f"{zc!r} + {rho!r} * sin({m})"), 0, q4(f"{180 / math.pi!r} * {m}"), 0])
        out += each(f"{id_}F{k0}", [p for _, p in facets[k0:k1]], like=like)
        k0 = k1
    purl.append([0, yc + (R + 0.05) * math.cos(ph0), zc + (R + 0.05) * math.sin(ph0)])
    out.append(box(id_ + "Purlin", mats[2], [L + 0.2, 0.12, 0.12], purl))
    # (the ribs: a deep arch plate each, its thickness along x)
    outer = [[R * math.sin(-ph0 + 2 * ph0 * i / 24) * -1, yc + R * math.cos(-ph0 + 2 * ph0 * i / 24)] for i in range(25)]
    inner = [[(R - 0.7) * math.sin(-ph0 + 2 * ph0 * i / 24) * -1, yc + (R - 0.7) * math.cos(-ph0 + 2 * ph0 * i / 24)] for i in range(24, -1, -1)]
    inner[0][1] = inner[-1][1] = ys - 0.2
    outer_pts = [[u, y] for u, y in outer]
    out.append(plate(id_ + "Rib", mats[2], outer_pts + inner, 0.3, [[x, 0, zc, 90, 0, 0] for x in ribs]))
    return out, R, yc, ph0


def train_shed():
    # A TRAIN SHED: a glazed barrel roof (Paddington's, Frankfurt's, York's kind, on a smaller span) 26.2 m across and
    # 60 m long: cast-iron columns every 7.5 m along both sides, arched plate ribs on them, the roof in flat facets --
    # zinc at the haunches, glass over the middle -- tie rods at the springing with hangers, a deep eaves girder each
    # side, and glazed end screens above the trains' height
    L, S, f, ys = 60.0, 26.2, 8.0, 8.0
    ribs = [-L / 2 + 7.5 * i for i in range(9)]
    roof, R, yc, ph0 = shed_roof("roof", L + 1.0, S, f, ys, 16, ["glazing", "zinc", "iron"], ribs, glassFrom=0.78)
    parts = list(roof)
    col = [[0.32, 0], [0.32, 0.5], [0.24, 0.6], [0.18, 0.8], [0.16, ys - 0.9], [0.22, ys - 0.6], [0.3, ys - 0.3], [0.3, ys]]
    parts.append(lathe("col", "iron", col, [[x, 0, s * S / 2] for x in ribs for s in (1, -1)], sides=10))
    parts.append(bx("eaves", "iron", [-L / 2 - 0.5, L / 2 + 0.5], [ys - 0.2, ys + 0.9], [S / 2 - 0.25, S / 2 + 0.25], mirror="z"))
    parts.append(bx("gutter", "zinc", [-L / 2 - 0.5, L / 2 + 0.5], [ys + 0.9, ys + 1.2], [S / 2 - 0.3, S / 2 + 0.45], mirror="z"))
    parts.append(rod("tie", "iron", 0.04, [0, ys + 0.2, -S / 2], [0, ys + 0.2, S / 2], 6, at=[[x, 0, 0] for x in ribs]))
    hang = [[x, 0, z] for x in ribs for z in (-S / 4, 0, S / 4)]
    parts.append(rod("hanger", "iron", 0.025, [0, ys + 0.2, 0], [0, ys + 2.0, 0], 4, at=[[h[0], 0, h[2]] for h in hang if True]))
    # (the end screens: glass in the arch above 6.5 m over the floor, with mullions)
    yb = ys + 0.4
    pts = [[-(R - 0.3) * math.sin(-ph0 + 2 * ph0 * i / 20), yc + (R - 0.3) * math.cos(-ph0 + 2 * ph0 * i / 20)] for i in range(21)]
    pts = [p for p in pts if p[1] >= yb] or pts
    screen = [[pts[0][0], yb]] + pts + [[pts[-1][0], yb]]
    parts.append(plate("endScreen", "glazing", screen, 0.04, [[s * L / 2, 0, 0, 90, 0, 0] for s in (1, -1)]))
    parts.append(box("endBeam", "iron", [0.25, 0.35, S], [[s * L / 2, yb, 0] for s in (1, -1)]))
    mull = []
    for k in range(1, 8):
        z = -S / 2 + S * k / 8; top = yc + math.sqrt(max(0, (R - 0.3) ** 2 - z * z))
        if top > yb: mull.append(([s * L / 2 for s in (1, -1)], z, top))
    for k, (xs_, z, top) in enumerate(mull):
        parts.append(box(f"mullion{k}", "iron", [0.1, top - yb, 0.12], [[x, (top + yb) / 2, z] for x in xs_]))
    return item("Train shed", "infrastructure",
        "a train shed: a glazed barrel roof 26.2 m across and 60 m long on cast-iron columns every 7.5 m (springing at 8 m, crown at 16 m): arched rib plates, faceted roofing -- zinc at the haunches, glass over the middle -- purlins, tie rods with hangers, eaves girders and gutters, glazed end screens above 8.4 m. Origin on the floor under its middle, x along the tracks.",
        {"glazing": "glass-light", "zinc": "#5c6670", "iron": "#3f4a52"}, merge(parts))


def footbridge():
    # A COVERED FOOTBRIDGE over the tracks: a deck `L` long along z (bays of 3.5 m), 3 m wide, its top at `D`;
    # steel posts each bay, a glazed upper side over a solid parapet, a roof with a fascia; supporting columns at both
    # ends (and under `mz` if `mid`). A bay's side can be left open for a stair to arrive (`w0`.. on -x, `e0`.. on +x);
    # stairs down to the ground at either end (`endA` at -z, `endB` at +z).
    nb, bay = 8, 3.5
    L = nb * bay
    D, hw, Hc = "D", 1.5, 2.6
    parts = [box("deck", "deck", [2 * hw + 0.2, 0.45, L], [0, "D - 0.225", 0]),
             box("floor", "floorTop", [2 * hw, 0.02, L], [0, "D + 0.01", 0]),
             box("roof", "roofB", [2 * hw + 0.6, 0.25, L + 0.4], [0, f"D + {Hc + 0.12}", 0]),
             box("fascia", "fasciaB", [0.08, 0.4, L + 0.4], [hw + 0.3, f"D + {Hc + 0.1}", 0], mirror="x"),
             box("post", "frameB", [0.15, Hc, 0.15], [[s * hw, f"D + {Hc / 2}", -L / 2 + bay * i] for i in range(nb + 1) for s in (1, -1)]),
             box("chord", "frameB", [0.15, 0.2, L], [hw, f"D + {Hc - 0.1}", 0], mirror="x")]
    parts = [p for p in parts if p]
    for s, side in ((-1, "w"), (1, "e")):   # (each bay's side its own, gated by its param: `when` "w{i}")
        zc = [-L / 2 + bay * (i + 0.5) for i in range(nb)]
        parts += each(f"para{side}", [box(f"para{side}{i}", "parapet", [0.08, 1.0, bay - 0.15], [s * hw, "D + 0.5", z], when=f"{side}{i}") for i, z in enumerate(zc)])
        parts += each(f"glaze{side}", [box(f"glaze{side}{i}", "glazing", [0.03, Hc - 1.3, bay - 0.15], [s * hw, f"D + {1.0 + (Hc - 1.3) / 2}", z], when=f"{side}{i}") for i, z in enumerate(zc)])
        parts += each(f"hand{side}", [rod(f"hand{side}{i}", "frameB", 0.025, [s * (hw - 0.1), "D + 0.95", z - bay / 2], [s * (hw - 0.1), "D + 0.95", z + bay / 2], 6, when=f"{side}{i}") for i, z in enumerate(zc)])
    for s, nm in ((-1, "endA"), (1, "endB")):
        parts.append(box(nm + "Wall", "parapet", [2 * hw, Hc, 0.12], [0, f"D + {Hc / 2}", s * L / 2], when={nm: 0}))
        parts.append(use(nm + "Stair", I + "stair-flight", [0, 0, f"{s} * ({L / 2} + D * 1.7)", 90 if s > 0 else -90, 0, 0], {"H": "D", "w": 2.4}, when=nm))
    parts.append(box("column", "frameB", [0.4, "D - 0.45", 0.4], [[s * (hw - 0.2), "(D - 0.45) / 2", z] for s in (1, -1) for z in (-L / 2 + 0.3, L / 2 - 0.3)]))
    parts.append(box("columnMid", "frameB", [0.4, "D - 0.45", 0.4], [[s * (hw - 0.2), "(D - 0.45) / 2", "mz"] for s in (1, -1)], when="mid"))
    params = {"D": 6.6, "endA": 1, "endB": 1, "mid": 0, "mz": 0}
    for i in range(nb): params[f"w{i}"] = 1; params[f"e{i}"] = 1
    return item("Footbridge", "infrastructure",
        f"a covered footbridge over the tracks: a deck {L:.0f} m long along z (eight bays of 3.5 m, z +-{L / 2:.0f}) and 3 m wide, its floor at D (6.6 m: over the trains' wires), steel posts, solid parapets and glazing, a roof; columns at both ends; stairs down to the ground at either end (`endA`, `endB`); any bay's side may be left open (`w0`..`w7` on -x, `e0`..`e7` on +x) for a stair from a platform.",
        {"deck": "#7f8389", "floorTop": "#56595e", "roofB": "#4b5560", "fasciaB": "#2f5e86", "frameB": "#3d4a57", "parapet": "#2f5e86", "glazing": "glass-light"}, parts, params=params)


# ==================================================================================================================
# THE RAILWAY STATION
# ==================================================================================================================
def station_hall():
    # THE STATION BUILDING (a 20th-century one, stone-faced): a tall booking hall in the middle (20 x 14 m, 13 m high)
    # with a glazed front of tall windows, three pairs of doors under a canopy, the clock and the name over them; two
    # wings of two storeys either side; at the back (-x) doors out to the first platform. Inside the hall: the ticket
    # counters with their glass, ticket machines, a departure board, benches, a kiosk, the hanging clock.
    # Its frame: the front (the street) +x, the long side along z (z +-25), the back wall at x -7.
    X0, X1, Z, Zh, Hh, Hw = -7.0, 7.0, 25.0, 10.0, 13.0, 9.0
    parts = [bx("floor", "floorStone", [X0, X1], [0, 0.15], [-Z, Z]),
             bx("plinth", "plinthStone", [X1, X1 + 0.15], [0, 0.6], [-Z, Z])]
    # (the hall's front: tall windows over the doors)
    parts += window_wall("hallFront", "x", X1 - 0.2, 0.5, -Zh, Zh, 0.15, Hh, [(0.15, 3.2, False, [1, 2, 3]), (3.8, 11.0, True, None)], 5, frac=0.7, mat="facade", mull="mullion")
    parts += window_wall("hallBack", "x", X0 + 0.2, 0.5, -Zh, Zh, 0.15, Hh, [(0.15, 3.2, False, [1, 3]), (4.5, 11.0, True, None)], 5, frac=0.6, mat="facade", mull="mullion")
    for s in (1, -1):   # (the wings: two storeys of windows, front and back, their ends windowed too)
        zr = sorted([s * Zh, s * Z])
        parts += window_wall(f"wingF{s}", "x", X1 - 0.2, 0.4, zr[0], zr[1], 0.15, Hw, [(1.0, 3.0, True, None), (4.8, 7.0, True, None)], 5, frac=0.5, mat="facade")
        parts += window_wall(f"wingB{s}", "x", X0 + 0.2, 0.4, zr[0], zr[1], 0.15, Hw, [(1.0, 3.0, True, None), (4.8, 7.0, True, None)], 5, frac=0.5, mat="facade")
        parts += window_wall(f"wingE{s}", "z", s * (Z - 0.2), 0.4, X0, X1, 0.15, Hw, [(1.0, 3.0, True, None), (4.8, 7.0, True, None)], 4, frac=0.5, mat="facade")
        parts.append(bx(f"wingRoof{s}", "roofFlat", [X0 - 0.3, X1 + 0.3], [Hw, Hw + 0.35], zr))
        parts.append(bx(f"wingFloor{s}", "inner", [X0 + 0.4, X1 - 0.4], [3.9, 4.1], zr))
        parts += window_wall(f"party{s}", "z", s * Zh, 0.4, X0 + 0.45, X1 - 0.45, 0.15, Hh, [(0.15, 2.6, False, [1])], 3, frac=0.5, mat="inner")
    parts = [p for p in parts if p]
    parts += [bx("hallRoof", "roofFlat", [X0 - 0.3, X1 + 0.3], [Hh, Hh + 0.4], [-Zh - 0.3, Zh + 0.3]),
              bx("cornice", "facadeDark", [X0 - 0.45, X1 + 0.45], [Hh - 0.6, Hh], [-Zh - 0.45, Zh + 0.45]),
              bx("ceiling", "ceiling", [X0 + 0.45, X1 - 0.45], [Hh - 0.62, Hh - 0.6], [-Zh + 0.2, Zh - 0.2]),
              bx("skylight", "glazing", [-3.5, 3.5], [Hh + 0.4, Hh + 1.4], [-6, 6]),
              bx("skyFrame", "facadeDark", [-3.7, 3.7], [Hh + 0.4, Hh + 0.6], [-6.2, 6.2]),
              # (the entrance canopy, the name band and the clock over the doors)
              bx("entCanopy", "canopyMetal", [X1, X1 + 3.0], [3.5, 3.8], [-7.5, 7.5]),
              rod("canopyTie", "canopyMetal", 0.04, [X1 + 2.8, 3.8, 0], [X1, 6.0, 0], 6, at=[[0, 0, z] for z in (-6, -2, 2, 6)]),
              bx("nameBand", "nameBg", [X1 + 0.05, X1 + 0.2], [11.3, 12.6], [-7, 7]),
              box("letters", "nameText", [0.04, 0.8, 0.6], [[X1 + 0.22, 11.95, -5.6 + 1.0 * k] for k in range(12)])]
    parts = [p for p in parts if p]
    # (inside: the ticket counters along the north party wall, with glass over them; machines; benches; a kiosk; the board)
    zc = -Zh + 0.6
    parts += [bx("counter", "counterWood", [-4.5, 4.5], [0.15, 1.1], [zc, zc + 0.7]),
              bx("counterTop", "counterTop", [-4.6, 4.6], [1.1, 1.15], [zc - 0.05, zc + 0.8]),
              box("counterGlass", "glazing", [9.0, 1.2, 0.02], [0, 1.8, zc + 0.75]),
              box("counterDiv", "canopyMetal", [0.06, 1.25, 0.1], [[-4.5 + 1.8 * k, 1.78, zc + 0.75] for k in range(6)]),
              bx("counterSign", "nameBg", [-4.6, 4.6], [2.5, 3.0], [zc + 0.6, zc + 0.8])]
    parts = [p for p in parts if p]
    parts += each("tm", [use(f"tm{k}", I + "ticket-machine", [X0 + 0.9, 0.15, 3.5 + 1.0 * k, 0, 0, 0]) for k in range(3)])
    parts += [use(f"benchH{k}", I + "bench", [0.3 + 1.0 * (k % 2) - 0.5, 0.15, 2.0 + 2.2 * (k // 2), 180 if k % 2 else 0, 0, 0]) for k in range(4)]
    parts += [use("hallBoard", I + "departure-board", [-1.0, 5.2, Zh - 0.5, 90, 0, 0], {"w": 5.0, "h": 1.6, "double": 0, "hang": 6.0}),
              use("hallClock", I + "clock", [0, 7.0, -3.0, 90, 0, 0]),
              rod("clockStem", "canopyMetal", 0.03, [0, 7.8, -3.0], [0, Hh - 0.6, -3.0], 6)]
    parts = [p for p in parts if p]
    parts += window_wall("kioskF", "x", 2.5, 0.12, 5.5, 9.2, 0.15, 2.9, [(1.0, 2.4, True, None)], 2, frac=0.8, mat="kioskMat")
    parts += [bx("kioskTop", "kioskMat", [2.4, 5.5], [2.9, 3.1], [5.4, 9.3]), bx("kioskSign", "nameBg", [2.38, 2.42], [2.6, 2.9], [5.5, 9.2]),
              bx("kioskSide", "kioskMat", [2.5, 5.5], [0.15, 2.9], [5.4, 5.55])]
    return item("Station building", "infrastructure",
        "a railway station's building (a 20th-century, stone-faced one), 50 x 14 m: the booking hall in the middle (20 m wide, 13 m high, a skylight) with a front of tall windows over three pairs of doors, its canopy and the name band; two-storey wings either side with their windows; doors at the back (-x) to the first platform. Inside: ticket counters behind glass, ticket machines, benches, a hanging departure board, a clock, a kiosk. Front +x, long side along z.",
        {"floorStone": "marble-grey", "plinthStone": "granite-black", "facade": "#c8bfae", "facadeDark": "#8f8676", "mullion": "#3d4a57", "glazing": "glass",
         "roofFlat": "#5a5d61", "inner": "#e2ddd2", "ceiling": "#ece8de", "canopyMetal": "#3d4a57", "nameBg": "#2f5e86", "nameText": "paint-white",
         "counterWood": "oak", "counterTop": "#d8d3c8", "kioskMat": "#a33a2c"}, merge(parts))


def railway_station():
    # THE RAILWAY STATION, composed of the pieces: three tracks through it (T1 at the building's platform, T2 at the
    # island, T3 a through line), the building's side platform P1 and the island P2, 100 m long; the train shed over
    # the middle 60 m; canopies on the platforms beyond it at -x; at +x the covered footbridge with its stairs down to
    # both platforms and to the far side; buffer-free through tracks 120 m long; signals at the platform ends.
    zB, zT1, zP2, zT2, zT3 = -25.0, -10.35, -4.7, 0.95, 5.45
    parts = [use("building", I + "station-hall", [0, 0, zB, 90, 0, 0])]
    for k, z in enumerate((zT1, zT2, zT3)):
        parts += runs(f"track{k}", [use(f"track{k}", I + "track-straight", [-55 + 10 * i, 0, z], {"clips": 0}) for i in range(12)])
    # (the platforms, 10 segments each: canopies outside the shed at -x; none where the stairs come down at +x -- `each`
    #  runs, cut where a segment's canopy or benches change)
    p1, p2 = [], []
    for i in range(10):
        x = -45 + 10 * i
        can = 1 if x < -30 else 0
        p1.append(use(f"p1_{i}", I + "platform", [x, 0, -15.0], {"W": 6.0, "island": 0, "canopy": can, "cz": -1.9, "rz": 1.4, "benches": 1 if x < 30 else 0, "board": 1, "fence": 0}))
        p2.append(use(f"p2_{i}", I + "platform", [x, 0, zP2], {"W": 8.0, "island": 1, "canopy": can, "cz": 0, "rz": 0, "benches": 1 if x < 30 else 0, "board": 1}))
    plain = lambda q: json.dumps({k: v for k, v in q.items() if k not in ("id", "at")}, sort_keys=True)   # (a run's params stay the same)
    parts += runs("p1", p1, key=plain, least=2) + runs("p2", p2, key=plain, least=2)
    parts.append(use("shed", I + "train-shed", [0, 0, -4.5]))
    # (the footbridge at x 40: open bays where the stairs from P1 (z -15.2) and P2 (z -4.7) arrive on its -x side)
    zf = -2.95
    fb = {"D": 6.6, "endA": 0, "endB": 1, "mid": 1, "mz": zP2 - zf, "w0": 0, "w3": 0}
    parts.append(use("footbridge", I + "footbridge", [40, 0, zf], fb))
    H = 6.6 - PH
    for nm, z in (("stairP1", -15.2), ("stairP2", zP2)):
        parts.append(use(nm, I + "stair-flight", [38.5 - H * 1.7, PH, z], {"H": H, "w": 2.2}))
    # (signals at the platforms' far ends: a mast, a head of three lights facing the trains)
    sig = {k: [] for k in ("sigMast", "sigHead", "sigLamp", "sigLampR")}   # (two ends by two tracks: `each` 4, rows of 2)
    for k, (x, z, yw) in enumerate(((52, zT1 - 2.2, 180), (52, zT2 + 2.2, 180), (-52, zT1 - 2.2, 0), (-52, zT2 + 2.2, 0))):
        sig["sigMast"].append(rod(f"sigMast{k}", "sigMast", 0.08, [x, 0, z], [x, 4.6, z], 8))
        sig["sigHead"].append(box(f"sigHead{k}", "sigHead", [0.2, 1.1, 0.5], [x, 4.6, z, yw, 0, 0]))
        sig["sigLamp"].append(use(f"sigLamp{k}", C + "lamp", [x + (0.11 if yw == 0 else -0.11), 4.9, z, yw, 0, 0], {"r": 0.08}, {"lens": "lamp-green", "bezel": "sigHead"}))
        sig["sigLampR"].append(use(f"sigLampR{k}", C + "lamp", [x + (0.11 if yw == 0 else -0.11), 4.35, z, yw, 0, 0], {"r": 0.08}, {"lens": "#3a1414", "bezel": "sigHead"}))
    for k, run in sig.items(): parts += runs(k, run)
    return item("Railway station", "infrastructure",
        "a through railway station, 120 x 60 m, composed of the infrastructure pieces: the station building on the town side (-z), its side platform P1 and an island platform P2 (100 m, 0.76 m over the rail) serving tracks T1 and T2, a through line T3; the glazed train shed over the middle 60 m, platform canopies beyond it, the covered footbridge at x 40 with stairs to both platforms and down to the far side, signals at the ends. Tracks along x at z -10.35, 0.95, 5.45 (rail top 0.642).",
        {"sigMast": "#5a6067", "sigHead": "#1e2022"}, parts)


# ==================================================================================================================
# THE BUS STATION
# ==================================================================================================================
def bus_shelter():
    # A BUS SHELTER: 4 m long, 1.6 deep, open to +x (the kerb): a glass back and glass ends in a steel frame, a roof
    # sloping back, a bench inside, a lit advertising panel at one end and the timetable case
    L, D, H = 4.0, 1.6, 2.5
    parts = [box("post", "frameS", [0.08, H, 0.08], [[x, H / 2, z] for x in (-D / 2 + 0.05,) for z in (-L / 2, -L / 6, L / 6, L / 2)] + [[D / 2 - 0.1, H / 2, s * L / 2] for s in (1, -1)]),
             box("back", "glazing", [0.02, H - 0.35, L - 0.1], [-D / 2 + 0.05, H / 2 + 0.1, 0]),
             box("end", "glazing", [D - 0.2, H - 0.35, 0.02], [0, H / 2 + 0.1, L / 2], mirror="z"),
             box("advert", "advert", [D - 0.25, 1.7, 0.08], [0, 1.25, -L / 2 + 0.06]),
             box("roofS", "roofS", [D + 0.4, 0.08, L + 0.3], [0.1, H + 0.05, 0, 0, 0, -4]),
             box("roofEdge", "fasciaS", [0.06, 0.16, L + 0.3], [D / 2 + 0.28, H + 0.06, 0]),
             use("bench", I + "bench", [-D / 2 + 0.45, 0, 0.3], {}),
             box("timetable", "timetable", [0.03, 0.7, 0.5], [-D / 2 + 0.08, 1.5, L / 2 - 0.5]),
             rod("flag", "frameS", 0.04, [D / 2 + 0.2, 0, L / 2 + 0.4], [D / 2 + 0.2, 3.0, L / 2 + 0.4], 8),
             box("flagSign", "flagSign", [0.04, 0.5, 0.5], [D / 2 + 0.2, 2.8, L / 2 + 0.4]),
             sphere("flagH", "flagMark", 0.17, [D / 2 + 0.2, 2.8, L / 2 + 0.4], stretch=[0.35, 1, 1], sides=12)]
    return item("Bus shelter", "infrastructure", "a bus shelter, 4 x 1.6 m: glass back and ends in a steel frame, a roof sloping back, a bench inside, a lit advertising panel, the timetable case, and the stop's flag on its pole by the kerb; open to +x",
        {"frameS": "#4a5560", "glazing": "glass-light", "advert": "lamp", "roofS": "#4a5560", "fasciaS": "#2f8a4a", "timetable": "paint-white", "flagSign": "paint-yellow", "flagMark": "#2f8a4a"}, parts)


def bus_station():
    # THE BUS STATION: an island 50 x 8 m raised to a bus kerb (18 cm), a long canopy on tree columns over it, three
    # bays each side marked on the asphalt (15 m, a sign and a seat row each), departure boards; at the east end the
    # waiting hall -- a glass box with its doors, the ticket desk, benches, a board, machines -- and two street
    # shelters on the apron's edge
    X0, X1, Zi, hk = -28.0, 22.0, 4.0, 0.18
    parts = [bx("apron", "asphalt", [-40, 40], [-0.12, YA], [-20, 20]),
             bx("island", "pave", [X0, X1], [YA, hk], [-Zi + 0.2, Zi - 0.2]),
             bx("kerbI", "kerbBus", [X0, X1], [YA - 0.1, hk + 0.005], [Zi - 0.2, Zi], mirror="z"),
             bx("kerbE", "kerbBus", [X0 - 0.2, X0], [YA - 0.1, hk + 0.005], [-Zi, Zi]),
             bx("edgeN", "pave", [-40, 40], [-0.12, YP], [18.5, 20.0]), bx("kerbN", "kerb", [-40, 40], [-0.12, YK], [18.35, 18.5]),
             bx("edgeS", "pave", [-40, 40], [-0.12, YP], [-20.0, -18.5]), bx("kerbS", "kerb", [-40, 40], [-0.12, YK], [-18.5, -18.35])]
    # (the bays: a yellow box on the asphalt along each side, a bay sign at its head)
    bays = [-21.0, -6.0, 9.0]
    for s in (1, -1):   # (a side's three bays: each part laid along x)
        z0 = s * Zi; z1 = s * (Zi + 3.2)
        bay = [[box(f"bayL{s}{k}", "lineY", [13.0, 0.004, 0.15], [[xb, YA + 0.002, z1]]),
                box(f"bayE{s}{k}", "lineY", [0.15, 0.004, 3.2], [[xb - 6.5, YA + 0.002, (z0 + z1) / 2], [xb + 6.5, YA + 0.002, (z0 + z1) / 2]]),
                box(f"bayT{s}{k}", "lineY", [3.0, 0.004, 0.5], [xb, YA + 0.002, (z0 + z1) / 2]),
                rod(f"baySignP{s}{k}", "frameS", 0.05, [xb + 5.5, hk, s * (Zi - 0.6)], [xb + 5.5, 3.2, s * (Zi - 0.6)], 8),
                box(f"baySign{s}{k}", "baySign", [0.5, 0.5, 0.06], [xb + 5.5, 3.0, s * (Zi - 0.6)]),
                use(f"bayBench{s}{k}", I + "bench", [xb, hk, s * (Zi - 1.6), 90 if s < 0 else -90, 0, 0])] for k, xb in enumerate(bays)]
        for run in zip(*bay): parts += each(run[0]["id"][:-1], list(run))
    parts = [p for p in parts if p]
    # (the canopy: tree columns -- a trunk branching into four struts -- under a long flat roof with a glazed spine)
    hc = 5.2
    cols = [X0 + 5 + 10 * k for k in range(5)]
    parts += [box("trunk", "frameS", [0.35, 3.2, 0.35], [[x, hk + 1.6, 0] for x in cols]),
              *[rod(f"branch{q}", "frameS", 0.09, [0, hk + 3.2, 0], [dx, hc - 0.25, dz], 8, at=[[x, 0, 0] for x in cols]) for q, (dx, dz) in enumerate(((2.2, 2.2), (2.2, -2.2), (-2.2, 2.2), (-2.2, -2.2)))],
              bx("canopyRoof", "roofS", [X0 - 1, X1 + 1], [hc - 0.25, hc + 0.1], [-6.2, -1.2]),
              bx("canopyRoof2", "roofS", [X0 - 1, X1 + 1], [hc - 0.25, hc + 0.1], [1.2, 6.2]),
              bx("canopySpine", "glazing", [X0 - 1, X1 + 1], [hc - 0.05, hc + 0.05], [-1.2, 1.2]),
              bx("canopyBeam", "frameS", [X0 - 1, X1 + 1], [hc - 0.45, hc - 0.25], [-1.3, 1.3]),
              bx("canopyFascia", "fasciaS", [X0 - 1, X1 + 1], [hc - 0.3, hc + 0.25], [6.2, 6.35], mirror="z"),
              box("canopyLight", "lightBox", [4.0, 0.06, 0.2], [[x, hc - 0.28, s * 3.5] for x in cols for s in (1, -1)]),
              use("boardI", I + "departure-board", [X0 + 10, 2.4, 0, 0, 0, 0], {"w": 2.4, "h": 1.2, "post": 2.4 - 0.6 - hk}),
              use("boardI2", I + "departure-board", [X0 + 30, 2.4, 0, 0, 0, 0], {"w": 2.4, "h": 1.2, "post": 2.4 - 0.6 - hk})]
    # (the waiting hall: a glass box 14 x 16 m, its roof running on to meet the canopy)
    HX0, HX1, HZ, Hh = 23.0, 37.0, 8.0, 4.6
    parts += [bx("hallFloor", "floorH", [HX0, HX1], [YA, hk], [-HZ, HZ]),
              *window_wall("hallW", "x", HX0 + 0.1, 0.2, -HZ, HZ, hk, Hh, [(hk, 2.6, True, [0, 1, 2, 4, 5, 6]), (2.6, 4.2, True, None)], 7, frac=0.94, mat="frameS"),
              *window_wall("hallE", "x", HX1 - 0.1, 0.2, -HZ, HZ, hk, Hh, [(hk, 4.2, True, None)], 7, frac=0.94, mat="frameS"),
              *window_wall("hallN", "z", HZ - 0.1, 0.2, HX0, HX1, hk, Hh, [(hk, 4.2, True, None)], 6, frac=0.94, mat="frameS"),
              *window_wall("hallS", "z", -HZ + 0.1, 0.2, HX0, HX1, hk, Hh, [(hk, 2.6, True, [0, 1, 3, 4, 5]), (2.6, 4.2, True, None)], 6, frac=0.94, mat="frameS"),
              bx("hallRoof", "roofS", [HX0 - 1.5, HX1 + 1.0], [Hh, Hh + 0.4], [-HZ - 1.0, HZ + 1.0]),
              bx("hallFascia", "fasciaS", [HX0 - 1.5, HX1 + 1.0], [Hh + 0.1, Hh + 0.55], [HZ + 1.0, HZ + 1.15], mirror="z"),
              bx("hallFasciaW", "fasciaS", [HX0 - 1.65, HX0 - 1.5], [Hh + 0.1, Hh + 0.55], [-HZ - 1.15, HZ + 1.15]),
              bx("hallName", "nameBgB", [HX0 - 1.7, HX0 - 1.66], [Hh + 0.12, Hh + 0.53], [-4, 4]),
              # (inside: the ticket desk, benches, a board, machines, the toilets' block)
              bx("desk", "deskMat", [HX1 - 2.6, HX1 - 1.8], [hk, hk + 1.1], [-3, 3]),
              bx("deskTop", "counterTop", [HX1 - 2.7, HX1 - 1.75], [hk + 1.1, hk + 1.15], [-3.1, 3.1]),
              bx("deskBack", "nameBgB", [HX1 - 0.4, HX1 - 0.3], [hk + 1.5, hk + 2.3], [-3, 3]),
              bx("wc", "wcMat", [HX1 - 4.5, HX1 - 0.3], [hk, 3.2], [-HZ + 0.3, -HZ + 4.0]),
              bx("wcDoor", "nameBgB", [HX1 - 4.55, HX1 - 4.5], [hk, hk + 2.1], [-HZ + 1.0, -HZ + 1.9]),
              *each("hb", [use(f"hb{k}", I + "bench", [[HX0 + 3 + 3.2 * k, hk, z, 0, 0, 0] for z in (5.8, 3.5)]) for k in range(3)]),
              use("hallBoard", I + "departure-board", [HX0 + 6, 3.2, -1.5, 0, 0, 0], {"w": 3.0, "h": 1.0, "hang": Hh - 3.7}),
              *each("tmB", [use(f"tmB{k}", I + "ticket-machine", [HX0 + 1.0, hk, -5.5 - k, 0, 0, 0]) for k in range(2)])]
    parts += [use("shelterA", I + "bus-shelter", [-10, YP, -17.6, -90, 0, 0]), use("shelterB", I + "bus-shelter", [10, YP, 17.6, 90, 0, 0])]
    return item("Bus station", "infrastructure",
        "a bus station, 80 x 40 m: a raised island (50 x 8 m, an 18 cm bus kerb) under a long canopy on tree columns with a glazed spine, three 15 m bays marked each side with their signs and benches, departure boards; the waiting hall at +x -- a glass box 14 x 16 m with its doors, ticket desk, benches, a board, ticket machines, the toilets -- and two street shelters on the apron's kerbs.",
        {**ROAD_MATS, "kerbBus": "#c4c0b6", "lineY": "paint-yellow", "frameS": "#4a5560", "roofS": "#5d656d", "fasciaS": "#2f8a4a", "glazing": "glass-light",
         "lightBox": "lamp", "baySign": "#2f8a4a", "floorH": "#9d9a93", "nameBgB": "#2f8a4a", "deskMat": "#cfcac0", "counterTop": "#e8e4dc", "wcMat": "#d8d3c8"}, merge(parts))


# ==================================================================================================================
# THE AIRPORT
# ==================================================================================================================
SEG7 = {"a": [0, 2, 3, 5, 6, 7, 8, 9], "b": [0, 1, 2, 3, 4, 7, 8, 9], "c": [0, 1, 3, 4, 5, 6, 7, 8, 9], "d": [0, 2, 3, 5, 6, 8, 9],
        "e": [0, 2, 6, 8], "f": [0, 4, 5, 6, 8, 9], "g": [2, 3, 4, 5, 6, 8, 9]}


def digit(id_, param, cx, cz, h, w, t, y, mat):
    """a seven-segment digit painted flat, read from -x (its top toward +x, its right toward +z): the segments a digit
    `param` lights (items.js `when` on the param's value)"""
    hs = h / 2
    seg = {"a": ([h * 0 + hs, cz], [t, w]), "d": ([-hs, cz], [t, w]), "g": ([0, cz], [t, w]),
           "b": ([hs / 2, cz + w / 2], [hs, t]), "c": ([-hs / 2, cz + w / 2], [hs, t]),
           "f": ([hs / 2, cz - w / 2], [hs, t]), "e": ([-hs / 2, cz - w / 2], [hs, t])}
    return [box(f"{id_}{k}", mat, [sz[0] + (t if k in "bcef" else 0), 0.004, sz[1] + (t if k in "adg" else 0)], [cx + c[0], y, c[1]], when={param: SEG7[k]}) for k, (c, sz) in seg.items()]


AIR_MATS = {"asphalt": "asphalt", "shoulder": "#57585b", "white": "tarmac-line", "yellow": "paint-yellow", "edgeLamp": "lamp", "blueLamp": "#3a6cff",
            "greenLamp": "lamp-green", "redLamp": "lamp-red", "lampPost": "#c9b23a", "grass": "#5d7f3a"}


def runway():
    # A RUNWAY SEGMENT, 50 m: 45 m of runway between 7.5 m shoulders, the white edge lines, the centre line's 30 m
    # stripe with its 20 m gap (shared with the next tile), flush centre-line lights every 12.5 m and an edge light
    # each side
    L, Wr, Ws = 50.0, 22.5, 30.0
    parts = [bx("runway", "asphalt", [-L / 2, L / 2], [-0.3, 0.05], [-Wr, Wr]),
             bx("shoulder", "shoulder", [-L / 2, L / 2], [-0.3, 0.04], [Wr, Ws], mirror="z"),
             box("edge", "white", [L, 0.004, 0.9], [0, 0.052, Wr - 0.45], mirror="z"),
             box("centre", "white", [30, 0.004, 0.9], [0, 0.052, 0]),
             box("cLight", "edgeLamp", [0.3, 0.012, 0.3], [[x, 0.055, 0] for x in (-18.75, -6.25, 6.25, 18.75)]),
             rod("edgePost", "lampPost", 0.04, [0, 0.04, Wr + 1.5], [0, 0.35, Wr + 1.5], 6, mirror="z"),
             sphere("edgeLight", "edgeLamp", 0.09, [0, 0.4, Wr + 1.5], mirror="z", sides=10)]
    return item("Runway", "infrastructure",
        "a runway segment, 50 m (TILE 50 m: ports x +-25, the runway along x): 45 m wide between 7.5 m shoulders, white edge lines, the centre line's 30 m stripe (its 20 m gap split between tiles), flush centre-line lights every 12.5 m, elevated edge lights.",
        AIR_MATS, parts)


def runway_end():
    # THE RUNWAY'S END, 150 m: the threshold green lights across the end, the threshold's piano keys (12 bars 30 m
    # long), the designation number (two seven-segment digits 9 m tall, `d1` `d2`: 0..9 -- runway 27 by default,
    # landing toward +x), then the centre line on; the runway's edge lines and shoulders as on the plain segment
    L, Wr, Ws, x0 = 150.0, 22.5, 30.0, -75.0
    keys = [s * (Wr - 3.0 - 3.6 * k) for s in (1, -1) for k in range(6)]
    parts = [bx("runway", "asphalt", [-L / 2, L / 2], [-0.3, 0.05], [-Wr, Wr]),
             bx("shoulder", "shoulder", [-L / 2, L / 2], [-0.3, 0.04], [Wr, Ws], mirror="z"),
             box("edge", "white", [L, 0.004, 0.9], [0, 0.052, Wr - 0.45], mirror="z"),
             box("keys", "white", [30, 0.004, 1.8], [[x0 + 6 + 15, 0.052, z] for z in keys]),
             box("centre", "white", [30, 0.004, 0.9], [[0, 0.052, 0], [50, 0.052, 0]]),
             box("thLight", "greenLamp", [0.35, 0.15, 0.35], [[x0 + 0.5, 0.12, -Wr + 1.5 + 3.0 * k] for k in range(15)]),
             box("endLight", "redLamp", [0.2, 0.15, 0.35], [[x0 + 0.2, 0.12, -Wr + 1.5 + 3.0 * k] for k in range(15)]),
             box("cLight", "edgeLamp", [0.3, 0.012, 0.3], [[x, 0.055, 0] for x in (-12.5, 12.5, 37.5, 62.5)]),
             rod("edgePost", "lampPost", 0.04, [0, 0.04, Wr + 1.5], [0, 0.35, Wr + 1.5], 6, at=[[x, 0, 0] for x in (-50, 0, 50)], mirror="z"),
             sphere("edgeLight", "edgeLamp", 0.09, [[x, 0.4, Wr + 1.5] for x in (-50, 0, 50)], mirror="z", sides=10)]
    parts += digit("dA", "d1", x0 + 6 + 30 + 12 + 4.5, -3.5, 9.0, 3.0, 0.9, 0.052, "white")
    parts += digit("dB", "d2", x0 + 6 + 30 + 12 + 4.5, 3.5, 9.0, 3.0, 0.9, 0.052, "white")
    return item("Runway end", "infrastructure",
        "a runway's threshold end, 150 m (x -75..75: the runway begins at x -75, aircraft land toward +x; port at x +75 for the runway segments): green threshold lights and red end lights across it, the piano keys (twelve 30 m bars), the designation number in 9 m digits (`d1`, `d2`, default 27), the centre line's stripes, edge lines, shoulders and edge lights.",
        AIR_MATS, parts, params={"d1": 2, "d2": 7})


def taxiway():
    # A TAXIWAY SEGMENT, 30 m: 23 m of pavement with 7.5 m shoulders, the yellow centre line, the edges' double yellow
    # lines, green centre-line lights and blue edge lights
    L, Wt, Ws = 30.0, 11.5, 19.0
    parts = [bx("taxi", "asphalt", [-L / 2, L / 2], [-0.3, 0.05], [-Wt, Wt]),
             bx("shoulder", "shoulder", [-L / 2, L / 2], [-0.3, 0.04], [Wt, Ws], mirror="z"),
             box("centre", "yellow", [L, 0.004, 0.15], [0, 0.052, 0]),
             box("edgeA", "yellow", [L, 0.004, 0.15], [[0, 0.052, Wt - 0.2], [0, 0.052, Wt - 0.5]], mirror="z"),
             box("cLight", "greenLamp", [0.25, 0.012, 0.25], [[x, 0.055, 0] for x in (-7.5, 7.5)]),
             rod("edgePost", "lampPost", 0.035, [0, 0.04, Wt + 1.0], [0, 0.32, Wt + 1.0], 6, mirror="z"),
             sphere("edgeLight", "blueLamp", 0.08, [0, 0.36, Wt + 1.0], mirror="z", sides=10)]
    return item("Taxiway", "infrastructure",
        "a taxiway segment, 30 m (TILE 30 m: ports x +-15): 23 m of pavement between 7.5 m shoulders, the yellow centre line with green lights, the double yellow edge lines, blue edge lights.",
        AIR_MATS, parts)



def ring_at(n, start, r, y, side=(0,), turn=0):
    # (n places on a floor ring r out, the first `start` degrees round from +x; each turned so its +x faces out (plus
    #  `turn` degrees), with `side` offsets taken along the ring's tangent -- the desks of a tower cab, a rotunda's seats)
    out = []
    for i in range(n):
        deg = start + 360 * i / n
        t = math.radians(deg)
        for s_ in side:
            out.append([round(r * math.cos(t) - s_ * math.sin(t), 4), y, round(-r * math.sin(t) - s_ * math.cos(t), 4), deg + turn, 0, 0])
    return out


def control_tower():
    # A CONTROL TOWER, 46 m: a round concrete shaft (7 m across, a stair-lit slot up it) from a two-storey base
    # building; under the cab a wider equipment floor; the cab -- sixteen panes leaning out (no reflections) between
    # mullions -- with its consoles and screens inside; the roof with its rail, antennas and the radar on a mast
    Hs, Hc = 38.0, 4.2
    yf = Hs + 2.5
    parts = [bx("base", "baseMat", [-12, 6], [0, 7.0], [-6, 6]),
             bx("baseWin", "glazing", [-12.05, 6.05], [1.0, 2.8], [-6.05, 6.05]),
             bx("baseWin2", "glazing", [-12.05, 6.05], [4.2, 6.0], [-6.05, 6.05]),
             bx("baseRoof", "roofMat", [-12.3, 6.3], [7.0, 7.3], [-6.3, 6.3]),
             lathe("shaft", "concreteT", [[3.6, 0], [3.6, 7.3], [3.5, 7.3], [3.2, Hs - 2], [3.6, Hs]], [0, 0, 0], sides=28, caps=False),
             box("slot", "glazing", [0.2, Hs - 12, 0.8], [3.35, 7.5 + (Hs - 12) / 2, 0, 0, 0, 0.5]),
             lathe("equip", "concreteT", [[3.6, Hs], [6.2, Hs + 0.6], [6.2, Hs + 2.2], [6.6, yf - 0.1], [6.6, yf]], [0, 0, 0], sides=16, faceted=True, caps=False),
             lathe("equipWin", "glazing", [[6.22, Hs + 1.0], [6.22, Hs + 1.8]], [0, 0, 0], sides=16, faceted=True, caps=False),
             lathe("cabFloor", "floorT", [[6.6, yf], [0, yf]], [0, 0, 0], sides=16, faceted=True, caps=False),
             lathe("sill", "frameT", [[6.6, yf], [6.6, yf + 0.9], [6.5, yf + 0.9]], [0, 0, 0], sides=16, faceted=True, caps=False, double=True),
             lathe("cabGlass", "glazing", [[6.5, yf + 0.9], [7.1, yf + Hc]], [0, 0, 0], sides=16, faceted=True, caps=False, double=True),
             rod("mullion", "frameT", 0.07, [6.5, yf + 0.9, 0], [7.1, yf + Hc, 0], 6, around={"n": 16, "r": 0}),
             lathe("roofT", "roofMat", [[7.4, yf + Hc], [7.4, yf + Hc + 0.6], [5.0, yf + Hc + 0.9], [0, yf + Hc + 0.9]], [0, 0, 0], sides=16, faceted=True),
             lathe("ceilingT", "ceilingT", [[0, yf + Hc - 0.01], [7.1, yf + Hc - 0.01]], [0, 0, 0], sides=16, faceted=True, caps=False),
             ring("roofRail", "frameT", 6.6, 0.03, [0, yf + Hc + 2.0, 0]),
             rod("radarMast", "frameT", 0.18, [0, yf + Hc + 0.9, 0], [0, yf + Hc + 4.5, 0], 8),
             box("radar", "radarMat", [0.6, 1.0, 5.0], [0, yf + Hc + 5.0, 0, 20, 0, 0]),
             rod("ant", "frameT", 0.04, [3.5, yf + Hc + 0.9, 0], [3.5, yf + Hc + 4.0, 0], 6, around={"n": 3, "r": 0, "start": 30}),
             sphere("beacon", "redLamp", 0.15, [0, yf + Hc + 5.6, 0], sides=10),
             # (inside the cab: a ring of consoles facing out, their screens, chairs)
             # (`around` only adds r along its angle and turns the part, it does not swing an offset `at` round the
             #  axis, so the ring of desks is placed explicitly with ring_at: a place r out at a heading, turned to face out)
             box("console", "consoleMat", [0.9, 0.9, 2.6], ring_at(8, 11.25, 5.4, yf + 0.45)),
             *[use(f"cscreen{k}", C + "screen", a, {"w": 0.55, "h": 0.35})
               for k, a in enumerate(ring_at(8, 11.25, 5.0, yf + 1.2, side=[-0.65, 0.65], turn=180))],
             *[use(f"chair{k}", C + "seat", a, {"h": 0.5, "w": 0.5, "headrest": 0}, {"cover": "#30343a", "frame": "#222222"})
               for k, a in enumerate(ring_at(8, 11.25, 4.1, yf))],
             lathe("core", "concreteT", [[1.6, yf], [1.6, yf + Hc]], [0, 0, 0], sides=12, caps=False),
             bx("door", "doorMat", [6.05, 6.1], [0, 2.4], [-1.0, 1.0])]
    parts = [p for p in parts if p]
    return item("Control tower", "infrastructure",
        "an airport control tower, 47 m to the radar: a concrete shaft 7 m across on a two-storey base building, a wider equipment floor, the cab at 40.5 m with sixteen panes leaning outward between mullions, consoles with screens and chairs inside, a roof with antennas, a rotating radar and a beacon. Origin at the shaft's foot.",
        {"baseMat": "#c9c5bc", "glazing": "glass", "roofMat": "#4f565d", "concreteT": "concrete", "floorT": "#6b6f75", "frameT": "#3a4046",
         "ceilingT": "#dcdcd6", "radarMat": "paint-white", "redLamp": "lamp-red", "consoleMat": "#4a4f57", "doorMat": "#3a4046"}, parts)


def jet_bridge():
    # A JET BRIDGE (an apron-drive passenger boarding bridge): the rotunda on its column at the terminal's gate (x 0),
    # two telescoping tunnels sloping from the gate's floor (`F`) down toward the aircraft's door, the cab with its
    # bellows at the far end, the drive column on its wheels under the outer tunnel, a service stair down from the cab
    F, Fc = 4.5, 3.6
    xa, xb, xc = 1.6, 13.0, 24.0
    yA = lambda x: F + (Fc - F) * (x - xa) / (xc - xa)
    tA = [[xa, 1.25, yA(xa) - 0.25, yA(xa) + 2.45], [xb + 0.5, 1.25, yA(xb + 0.5) - 0.25, yA(xb + 0.5) + 2.45]]
    tB = [[xb, 1.4, yA(xb) - 0.35, yA(xb) + 2.6], [xc, 1.4, yA(xc) - 0.35, yA(xc) + 2.6]]
    winA = [hole(xa + 1 + 2.0 * k, xa + 2.3 + 2.0 * k, F + 0.6, F + 1.6) for k in range(5)]
    winB = [hole(xb + 1.2 + 2.0 * k, xb + 2.5 + 2.0 * k, Fc + 0.9, Fc + 1.8) for k in range(5)]
    parts = [lathe("rotCol", "jbFrame", [[0.5, 0], [0.4, 0.2], [0.4, F - 0.3]], [0, 0, 0], sides=12, caps=False),
             lathe("rotunda", "jbSkin", [[1.8, F - 0.3], [1.8, F + 2.6], [0, F + 2.75]], [0, 0, 0], sides=18),
             lathe("rotFloor", "jbFloor", [[1.75, F - 0.3], [0, F - 0.3]], [0, 0, 0], sides=18, caps=False),
             loft("tunnelA", "jbSkin", tA, [0.08, 0.15], holes=winA, double=True, caps=[False, False], seg=1),
             loft("tunnelB", "jbSkin2", tB, [0.08, 0.15], holes=winB, double=True, caps=[False, False], seg=1),
             box("floorA", "jbFloor", [xb + 0.5 - xa, 0.05, 2.3], [(xa + xb + 0.5) / 2, (yA(xa) + yA(xb + 0.5)) / 2 - 0.15, 0, 0, 0, math.degrees(math.atan2(Fc - F, xc - xa))]),
             box("floorB", "jbFloor", [xc - xb, 0.05, 2.6], [(xb + xc) / 2, (yA(xb) + yA(xc)) / 2 - 0.25, 0, 0, 0, math.degrees(math.atan2(Fc - F, xc - xa))]),
             # (the cab: a wider box turned a little, its bellows reaching for the aircraft, a canopy over them)
             bx("cab", "jbSkin", [xc, xc + 3.0], [Fc - 0.45, Fc + 2.7], [-1.8, 1.8], yaw=0),
             bx("cabWin", "glazing", [xc + 0.6, xc + 2.4], [Fc + 0.9, Fc + 1.9], [-1.82, 1.82]),
             bx("bellows", "bellows", [xc + 3.0, xc + 3.9], [Fc - 0.25, Fc + 2.6], [-1.5, 1.5]),
             box("bellowsRib", "jbFrame", [0.08, 2.95, 3.1], [[xc + 3.15 + 0.25 * k, Fc + 1.17, 0] for k in range(3)]),
             bx("bumper", "bellows", [xc + 3.8, xc + 4.0], [Fc - 0.3, Fc - 0.1], [-1.2, 1.2]),
             # (the drive column: two legs on a bogie of two wheels)
             box("leg", "jbFrame", [0.35, yA(19.0) - 0.9, 0.35], [19.0, (yA(19.0) - 0.4) / 2 + 0.3, 1.0], mirror="z"),
             bx("driveBeam", "jbFrame", [18.5, 19.5], [0.7, 1.1], [-1.4, 1.4]),
             bx("driveCross", "jbFrame", [18.6, 19.4], [yA(19.0) - 0.75, yA(19.0) - 0.4], [-1.3, 1.3]),
             use("wheel", C + "wheel", [19.0, 0.5, 1.45], {"r": 0.5, "w": 0.35, "spokes": 0}, {"tyre": "rubber", "rim": "#bdbdb8", "hub": "steel"}, mirror="z"),
             use("stairS", I + "stair-flight", [xc + 1.5, 0, -1.8 - (Fc - 0.45) * 1.7 - 0.1, -90, 0, 0], {"H": Fc - 0.45, "w": 0.9}),
             bx("stairLanding", "jbFrame", [xc + 1.0, xc + 2.0], [Fc - 0.55, Fc - 0.45], [-2.0, -1.8])]
    parts = [p for p in parts if p]
    return item("Jet bridge", "infrastructure",
        f"an apron-drive jet bridge, 28 m: the rotunda (its floor at {F} m) on its column at the terminal's gate at x 0, two telescoping tunnels with windows (you see the floor through them) sloping to the cab at x 24 (floor {Fc} m, an A320's door sill), the bellows reaching toward +x, the drive column on two wheels, a service stair from the cab to the apron.",
        {"jbSkin": "#c7c9c9", "jbSkin2": "#b5b8b9", "jbFrame": "#4a5058", "jbFloor": "#585b60", "glazing": "glass", "bellows": "#26282b"}, parts)


def terminal():
    # AN AIRPORT TERMINAL, 120 x 40 m: landside (-x) a glass wall under a roof that waves out over the kerb, the
    # check-in hall with two islands of desks and belts and their screens, the security line, then the airside gate
    # floor raised 4.5 m on a mezzanine with seats, gate desks and boards, a stair and an escalator up; the airside
    # glass wall (+x) with three jet bridges at its gates. The roof on tree columns.
    X0, X1, Z, Hm = -20.0, 20.0, 60.0, 4.5
    parts = [bx("floorT", "floorT", [X0, X1], [0, 0.15], [-Z, Z]),
             bx("forecourt", "paveT", [X0 - 12, X0], [0, 0.15], [-Z, Z]),
             bx("kerbT", "kerbT", [X0 - 12.15, X0 - 12], [-0.05, 0.15], [-Z, Z]),
             bx("roadT", "asphalt", [X0 - 26, X0 - 12.15], [-0.1, 0.0], [-Z, Z])]
    # (the roof: a shell arched across the depth, 16 m at the landside eaves, 22 m over the middle, 15 m airside --
    #  a loft turned so its x runs across the building -- its overhang over the forecourt)
    rs = [[X0 - 10, Z + 2, 15.0, 15.6], [X0, Z + 2, 18.5, 19.2], [0, Z + 2, 21.5, 22.2], [X1, Z + 2, 16.0, 16.6], [X1 + 4, Z + 2, 14.8, 15.4]]
    parts.append(loft("roof", "roofT", rs, [0.1, 0.1], seg=3, corner=1))
    ytop = lambda x: 18.5 + (21.5 - 18.5) * (1 - (x / 20) ** 2) if abs(x) <= 20 else 16
    # (the landside and airside walls: glass with mullions every 3 m and transoms, up to the roof's underside)
    for nm, x, ytp in (("land", X0, 18.4), ("air", X1, 15.9)):
        parts += [face_box(nm + "Glass", "glazing", "x", x, (-Z, Z), (0.15, ytp), 0.06),
                  *bars(nm + "Mull", "mullT", "x", x, fill(-Z, Z, post=0, n=40), 0, ytp, t=0.25, w=0.12, ends=True),
                  *panes(nm + "Tran", "mullT", "x", x, [(-Z, Z)], [(y - 0.06, y + 0.06) for y in (3.2, 7.5, 12.0)], t=0.22)]
    # (the landside doors: dark revolving-door drums; the ends: solid panels)
    parts += each("door", [lathe(f"door{z}", "doorDrum", [[1.5, 0.15], [1.5, 2.8], [0, 2.9]], [X0, 0, z], sides=16) for z in (-30, 0, 30)])
    parts += each("endWall", [bx(f"endWall{s}", "panelT", [X0, X1], [0, 22.0], sorted([s * (Z - 0.2), s * Z])) for s in (1, -1)])
    parts = [p for p in parts if p]
    # (the tree columns: trunks with four branches to the roof)
    cols = [(x, z) for x in (-8.0, 8.0) for z in (-45, -15, 15, 45)]
    parts.append(lathe("trunk", "mullT", [[0.45, 0], [0.4, 9.0]], [[x, 0, z] for x, z in cols], sides=12, caps=False))
    for q, (dx, dz) in enumerate(((4, 5), (4, -5), (-4, 5), (-4, -5))):   # (a run along z for each row of trunks)
        for x0 in (-8.0, 8.0):
            parts += each(f"branch{q}_{x0:+.0f}", [rod(f"branch{q}_{i}", "mullT", 0.18, [x, 9.0, z], [x + dx, ytop(x + dx) - 0.05, z + dz], 8) for i, (x, z) in enumerate(cols) if x == x0])
    parts = [p for p in parts if p]
    # (the mezzanine: the airside gate floor, its edge rail, the stairs and an escalator up from the hall)
    xm = 4.0
    parts += [bx("mezz", "slabT", [xm, X1 - 0.2], [Hm - 0.35, Hm], [-Z + 0.3, Z - 0.3]),
              bx("mezzTop", "carpetT", [xm, X1 - 0.2], [Hm, Hm + 0.01], [-Z + 0.3, Z - 0.3]),
              box("mezzCol", "mullT", [0.4, Hm - 0.35, 0.4], [[xm + 1, (Hm - 0.35) / 2, z] for z in range(-50, 51, 12)]),
              bx("mezzGlass", "glazing", [xm - 0.02, xm + 0.02], [Hm, Hm + 1.1], [-Z + 0.3, -9]),
              bx("mezzGlass2", "glazing", [xm - 0.02, xm + 0.02], [Hm, Hm + 1.1], [9, Z - 0.3]),
              rod("mezzRail", "mullT", 0.03, [xm, Hm + 1.1, -Z + 0.3], [xm, Hm + 1.1, Z - 0.3], 6),
              use("stairT", I + "stair-flight", [xm - Hm * 1.7, 0.15, -6.0], {"H": Hm - 0.15, "w": 3.0}),
              box("escalator", "escT", [math.hypot(Hm * 1.73, Hm), 0.9, 1.2], [xm - Hm * 0.865, Hm / 2 + 0.2, 6.0, 0, 0, 30]),
              box("escSide", "glazing", [math.hypot(Hm * 1.73, Hm), 0.9, 0.04], [[xm - Hm * 0.865, Hm / 2 + 1.0, 6.65, 0, 0, 30], [xm - Hm * 0.865, Hm / 2 + 1.0, 5.35, 0, 0, 30]])]
    parts = [p for p in parts if p]
    # (check-in: two islands along x, each with eight desks a side, the belt behind, a screen over each desk, a fascia)
    isl = [[bx(f"isl{k}", "panelT", [-15, -6], [0.15, 2.6], [z - 1.5, z + 1.5]),
            bx(f"islFascia{k}", "fasciaT", [-15.2, -5.8], [2.6, 3.2], [z - 1.7, z + 1.7]),
            box(f"desk{k}", "deskT", [0.9, 1.0, 0.7], [[-14.2 + 1.15 * i, 0.65, z + s * 2.1] for i in range(8) for s in (1, -1)]),
            box(f"belt{k}", "beltT", [9.0, 0.06, 0.6], [[-10.5, 0.55, z + s * 1.75] for s in (1, -1)]),
            use(f"ckScreen{k}", C + "screen", [-14.2, 2.2, z + 1.53, -90, 0, 0], {"w": 0.6, "h": 0.35}, along={"n": 8, "from": [0, 0, 0], "to": [8.05, 0, 0]}),
            use(f"ckScreenB{k}", C + "screen", [-14.2, 2.2, z - 1.53, 90, 0, 0], {"w": 0.6, "h": 0.35}, along={"n": 8, "from": [0, 0, 0], "to": [8.05, 0, 0]})]
           for k, z in enumerate((-30, 30))]
    for run in zip(*isl): parts += each(run[0]["id"][:-1], list(run))   # (the two islands: each part laid twice)
    # (security: a line of walk-through arches and their belts across the hall's middle, before the stair)
    parts += [box("secArchL", "secT", [0.9, 2.2, 0.15], [[-1.0, 1.25, z + s * 0.5] for z in (-18, -14, 14, 18) for s in (1, -1)]),
              box("secArchT", "secT", [0.9, 0.25, 1.15], [[-1.0, 2.35, z] for z in (-18, -14, 14, 18)]),
              box("xray", "secT", [3.5, 1.1, 1.0], [[-3.0, 0.7, z + 1.4] for z in (-18, -14, 14, 18)]),
              use("hallBoard", I + "departure-board", [-17.0, 6.0, -9.0, 0, 0, 0], {"w": 4.0, "h": 1.6, "double": 1, "hang": 11.0}),
              use("hallBoard2", I + "departure-board", [-17.0, 6.0, 9.0, 0, 0, 0], {"w": 4.0, "h": 1.6, "double": 1, "hang": 11.0})]
    parts = [p for p in parts if p]
    # (the gates on the mezzanine: rows of seats facing the glass, a gate desk and a board at each, shops between)
    gates = (-40, 0, 40)
    parts += [*each("seats", [use(f"seats{g}", C + "seat-row", [[xm + 3.0 + 2.2 * r, Hm, zg + dz, 0, 0, 0] for r in range(5) for dz in (-6, -2.5, 2.5, 6)], {"n": 3}) for g, zg in enumerate(gates)]),
              *each("gateDesk", [bx(f"gateDesk{g}", "deskT", [X1 - 3.0, X1 - 2.2], [Hm, Hm + 1.05], [zg - 10.5, zg - 8.5]) for g, zg in enumerate(gates)]),
              *each("gateBoard", [use(f"gateBoard{g}", I + "departure-board", [X1 - 2.6, Hm + 2.4, zg - 9.5, 0, 0, 0], {"w": 1.4, "h": 0.6, "double": 1, "post": 1.6}) for g, zg in enumerate(gates)])]
    shops = (-20, 20)
    parts += [*each("shop", [bx(f"shop{k}", "shopT", [xm + 3, X1 - 3], [Hm, Hm + 3.5], [zs - 5, zs + 5]) for k, zs in enumerate(shops)]),
              *each("shopWin", [bx(f"shopWin{k}", "glazing", [xm + 2.95, xm + 3.0], [Hm + 0.3, Hm + 2.8], [zs - 4.5, zs + 4.5]) for k, zs in enumerate(shops)]),
              *each("shopSign", [bx(f"shopSign{k}", "fasciaT", [xm + 2.9, xm + 2.95], [Hm + 2.9, Hm + 3.4], [zs - 4, zs + 4]) for k, zs in enumerate(shops)])]
    # (the jet bridges at the airside gates, their rotundas against the glass at the mezzanine's floor)
    parts += [*each("bridge", [use(f"bridge{g}", I + "jet-bridge", [X1 + 2.0, 0, zg, 0, 0, 0]) for g, zg in enumerate(gates)]),
              *each("gateDoor", [bx(f"gateDoor{g}", "doorGap", [X1 - 0.08, X1 + 0.08], [Hm, Hm + 2.5], [zg - 1.0, zg + 1.0]) for g, zg in enumerate(gates)]),
              *each("gateLink", [bx(f"gateLink{g}", "panelT", [X1, X1 + 0.6], [Hm - 0.3, Hm + 2.75], [zg - 1.5, zg + 1.5]) for g, zg in enumerate(gates)])]
    parts.append(bx("apron", "apronT", [X1, X1 + 50], [-0.1, 0.02], [-Z - 10, Z + 10]))
    parts.append(box("standLine", "yellowT", [40, 0.004, 0.2], [[X1 + 25, 0.022, z] for z in (-40, 0, 40)]))
    parts.append(box("stopBar", "yellowT", [0.3, 0.004, 3.0], [[X1 + 38, 0.022, z] for z in (-40, 0, 40)]))
    return item("Airport terminal", "infrastructure",
        "an airport terminal, 120 x 40 m and 22 m high: a roof arched across the depth on tree columns, overhanging the landside forecourt and its road (-x); glass walls with mullions and transoms; landside doors, two check-in islands of sixteen desks with belts and screens, security arches and X-ray belts, departure boards; the airside gate floor on a mezzanine at 4.5 m (stair and escalator) with seat rows, gate desks and boards, shops; three jet bridges from the airside glass (+x) over the apron with its stand lines.",
        {"floorT": "#cfcbc2", "paveT": "#b3afa6", "kerbT": "#9b9a95", "asphalt": "asphalt", "roofT": "#d9dcde", "glazing": "glass", "mullT": "#9aa3ab",
         "doorDrum": "#2e3338", "panelT": "#c2c6c9", "slabT": "#a9adb1", "carpetT": "carpet-grey", "escT": "#5b6168", "fasciaT": "#2a5d9c", "deskT": "#e0ddd6",
         "beltT": "#2b2d30", "secT": "#7d858d", "shopT": "#b7413a", "doorGap": "#1a1d20", "apronT": "#8d8c88", "yellowT": "paint-yellow"}, merge(parts))


def hangar():
    # A HANGAR for airliners, 70 m wide and 60 deep: a barrel roof of steel (no glass, a band of rooflights) on a
    # lattice of ribs, the front (+x) one great opening with its sliding doors parked at the sides, the back wall with
    # workshops along it, a gantry crane rail, floor markings
    S, L, f, ys = 70.0, 60.0, 10.0, 14.0
    ribs = [-L / 2 + 7.5 * i for i in range(9)]
    roof, R, yc, ph0 = shed_roof("roof", L + 0.5, S, f, ys, 18, ["rooflight", "cladH", "steelH"], ribs, glassFrom=0.25)
    parts = list(roof)
    parts += [bx("floorH", "floorH", [-L / 2, L / 2 + 5], [0, 0.15], [-S / 2, S / 2]),
              bx("wallS", "cladH", [-L / 2, L / 2], [0, ys], [S / 2 - 0.3, S / 2], mirror="z"),
              bx("wallB", "cladH", [-L / 2 - 0.3, -L / 2], [0, ys], [-S / 2, S / 2])]
    pts = [[-(R) * math.sin(-ph0 + 2 * ph0 * i / 24), yc + R * math.cos(-ph0 + 2 * ph0 * i / 24)] for i in range(25)]
    gab = [[pts[0][0], ys]] + pts + [[pts[-1][0], ys]]
    parts.append(plate("gableB", "cladH", gab, 0.3, [-L / 2 - 0.15, 0, 0, 90, 0, 0]))
    parts.append(plate("gableF", "cladH", [[pts[0][0], ys]] + pts + [[pts[-1][0], ys]], 0.3, [L / 2, 0, 0, 90, 0, 0]))
    parts.append(bx("doorHead", "doorH", [L / 2 - 1.5, L / 2 + 0.3], [ys - 2.5, ys + 0.5], [-S / 2, S / 2]))
    # (the doors: six leaves each side, stacked open at the ends)
    for s in (1, -1): parts += each(f"leaf{s:+d}", [bx(f"leaf{k}", "doorH", [L / 2 - 0.3 - 0.4 * k, L / 2 - 0.05 - 0.4 * k], [0.15, ys - 2.5], sorted([s * (S / 2 - 0.3), s * (S / 2 - 6.0)])) for k in range(3)])
    parts += [box("leafWin", "rooflight", [0.05, 1.2, 4.5], [[L / 2 + 0.01, ys - 4.5, s * (S / 2 - 3.2)] for s in (1, -1)])]
    # (inside: workshops along the back wall, a gantry rail, floor markings)
    parts += [bx("workshop", "shopH", [-L / 2, -L / 2 + 8], [0.15, 6.5], [-S / 2 + 1, S / 2 - 1]),
              *window_wall("workshopF", "x", -L / 2 + 8, 0.2, -S / 2 + 1, S / 2 - 1, 0.15, 6.5, [(1.0, 2.6, True, None), (3.8, 5.4, True, None)], 12, frac=0.5, mat="shopH"),
              bx("gallery", "steelH", [-L / 2 + 8, -L / 2 + 10], [3.4, 3.6], [-S / 2 + 1, S / 2 - 1]),
              rod("galleryRail", "steelH", 0.03, [-L / 2 + 10, 4.6, -S / 2 + 1], [-L / 2 + 10, 4.6, S / 2 - 1], 6),
              bx("crane", "craneH", [-L / 2 + 2, L / 2 - 2], [ys - 1.2, ys - 0.6], [-0.4, 0.4]),
              box("floorLine", "yellowH", [L + 4, 0.004, 0.25], [[2.0, 0.152, 0], [2.0, 0.152, 14], [2.0, 0.152, -14]]),
              box("toolChest", "shopH", [1.2, 1.1, 0.6], [[-L / 2 + 9.5, 0.7, z] for z in (-20, -12, 12, 20)])]
    parts = [p for p in parts if p]
    return item("Hangar", "infrastructure",
        "an aircraft hangar, 70 m wide, 60 deep, 24 m high at the crown: a steel barrel roof on plate ribs with a band of rooflights, clad walls, the whole front (+x) open with the sliding door leaves parked at the sides, workshops of two storeys along the back with a gallery, a crane beam, floor markings.",
        {"rooflight": "glass-light", "cladH": "#8b949b", "steelH": "#4a5560", "floorH": "#a7a39b", "doorH": "#6f7a83", "shopH": "#c8c3b8", "craneH": "paint-yellow", "yellowH": "paint-yellow", "glazing": "glass"}, merge(parts))


# ==================================================================================================================
def write_all():
    for name, f in [("road-straight", road_straight), ("road-curve", road_curve),
                    ("road-t-junction", lambda: junction(("+x", "-x", "+z"), "t", "Road, T-junction")),
                    ("road-crossroads", lambda: junction(("+x", "-x", "+z", "-z"), "x", "Road, crossroads")),
                    ("zebra-crossing", zebra), ("roundabout", roundabout),
                    ("track-straight", track_straight), ("track-curve", track_curve), ("points", turnout), ("buffer-stop", buffer_stop),
                    ("crossing-barrier", crossing_barrier), ("level-crossing", level_crossing),
                    ("bench", bench), ("departure-board", departure_board), ("clock", clock), ("ticket-machine", ticket_machine), ("stair-flight", stair_flight),
                    ("platform", platform), ("train-shed", train_shed), ("footbridge", footbridge), ("station-hall", station_hall), ("railway-station", railway_station),
                    ("bus-shelter", bus_shelter), ("bus-station", bus_station),
                    ("runway", runway), ("runway-end", runway_end), ("taxiway", taxiway), ("control-tower", control_tower), ("jet-bridge", jet_bridge),
                    ("terminal", terminal), ("hangar", hangar)]:
        write(I + name, f(), "infra")


GROUPS = {"infra": "infrastructure"}
