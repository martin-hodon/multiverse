"""THE AIR (2026-11-20; docs/modern.md): an airliner, a light aeroplane, a helicopter -- each in the vehicle frame
(kit.py: the ground under its middle, +x its nose, +z its right/starboard wing), standing on its own gear.

THE LIFTING SURFACES are lofts laid on their side (`surface`): the loft's x runs out along the span, its y along the
chord (y0 the leading edge, y1 the trailing edge, so a station's y0/y1 are just -x of the edges, and the sweep is
free), its half-width the half-thickness -- `hw` thick at the leading edge, `tw` thin at the trailing edge, the
leading edge's corner rounded by the whole half-thickness: a wedge with a round nose, the airfoil drawn simply. A
wing is turned with pitch 90 - dihedral and roll 90 (span to +z, rising), a fin with roll 90 (span up).
The fuselages are lofts too, hollow (`double`) where the inside is shown, the windows cut as `holes`; the panes on
the noses are laid flat on the loft's surface by rail.on_loft."""
import math
from kit import item, box, rod, lathe, loft, sphere, ring, sweep, plate, use, write, across, arc, hole, hinge, slide, plug_slide, piece, cut, region, loft_z, shell_over, runs, window_holes
from rail import on_loft, station_at, end_wall

W = "modern/components/"


def surface(id_, mat, secs, y, dihedral=0.0, vertical=False, x=0.0, z=0.0, te=0.015, **k):
    """a wing, a tailplane or a fin as a loft on its side: secs [(s, x_le, x_te, half_thick)] out along the span from
    the root (s 0); `y` the root's height, `dihedral` in degrees; `vertical` a fin (its span up from y)"""
    st = [[s, ht, -le, -tr, min(te, ht)] for s, le, tr, ht in secs]
    rnd = [max(ht for *_, ht in secs), 0.01]
    at = [x, y, z, 0, 0, 90] if vertical else [x, y, z, 0, 90 - dihedral, 90]
    return loft(id_, mat, st, rnd, at=at, corner=4, **k)


def nacelle(id_, x_rear, y, z, L, R, mats=("nacelle", "fan", "nozzle"), **k):
    """a turbofan's nacelle along +x from x_rear: the cowl a lathe (its intake lip turned in, the duct seen from both
    sides), the fan and its spinner inside the intake, the exhaust's nozzle and plug behind"""
    cowl, fan, noz = mats
    at = [x_rear, y, z, 0, 0, -90]
    return [
        lathe(id_, cowl, [[R * 0.6, 0], [R * 0.8, L * 0.12], [R * 0.95, L * 0.35], [R, L * 0.62], [R * 0.98, L * 0.86], [R * 0.9, L * 0.99], [R * 0.84, L], [R * 0.8, L * 0.97], [R * 0.8, L * 0.8]], at, caps=False, double=True, sides=24, **k),
        lathe(id_ + "Fan", fan, [[R * 0.8, L * 0.8], [R * 0.2, L * 0.8], [R * 0.12, L * 0.86], [0, L * 0.93]], at, sides=24, **k),
        lathe(id_ + "Plug", noz, [[R * 0.6, 0.02], [R * 0.42, -L * 0.1], [R * 0.25, -L * 0.18], [0, -L * 0.24]], at, sides=16, **k),
    ]


def leg(id_, x, y_top, z, r_wheel, wheels=2, span=0.5, w=0.3, strut=0.09, mats=None, **k):
    """an undercarriage leg: the strut from y_top down to the axle, the axle across and its wheels (road wheels with a
    plain disc), the torque link"""
    out = [rod(id_, "gear", strut, [x, y_top, z], [x, r_wheel + 0.05, z], 10, **k),
           rod(id_ + "Axle", "gear", strut * 0.6, [x, r_wheel, z - span / 2 - w / 2], [x, r_wheel, z + span / 2 + w / 2], 8, **k),
           box(id_ + "Link", "gear", [0.25, 0.3, 0.06], [x + 0.12, r_wheel + 0.35, z], **k)]
    if wheels == 1:
        out.append(use(id_ + "W", W + "wheel", [x, r_wheel, z], {"r": r_wheel, "w": w, "spokes": 0, "rim": 0.55}, mats, **k))
    else:
        out.append(use(id_ + "Wo", W + "wheel", [x, r_wheel, z + span / 2], {"r": r_wheel, "w": w, "spokes": 0, "rim": 0.55}, mats, **k))
        out.append(use(id_ + "Wi", W + "wheel", [x, r_wheel, z - span / 2, 180, 0, 0], {"r": r_wheel, "w": w, "spokes": 0, "rim": 0.55}, mats, **k))
    return out


# ---- THE AIRLINER -----------------------------------------------------------------------------------------------
def airliner():
    # A NARROW-BODY AIRLINER (the A320 type, 1988-: 37.6 m long, 35.8 m span, 11.8 m high; 150 seats in two classes'
    # worth of rows, here 29 rows of six): the fuselage one hollow loft (3.95 m wide, its floor 3.35 m over the ground),
    # its windows cut through both sides; the front left door (L1) shut in its opening, opening out and forward on its
    # arm (two hinges: the arm swings out from the forward jamb, the door turns back on its end, so it stays parallel to
    # the skin, as on the real thing); swept wings (25 deg) with their kinked trailing edge, two turbofans in their nacelles on pylons, the
    # tailplane and the fin, the tricycle gear on its tyres. INSIDE: the floor, 29 rows of 3+3 seats with their
    # armrests, the overhead bins down both sides, the ceiling's lights, the galley at the door, the cockpit's two seats
    # and its panel behind the bulkhead.
    y0, y1, hw = 1.8, 5.95, 1.98
    rnd = [1.6, 1.5]
    fus = [[18.75, 0.06, 3.55, 3.72], [18.45, 0.62, 3.0, 4.45], [17.9, 1.1, 2.5, 4.98], [17.0, 1.56, 2.08, 5.45], [15.8, 1.87, 1.86, 5.82],
           [14.2, hw, y0, y1], [-10.0, hw, y0, y1], [-13.0, 1.92, 2.12, y1], [-15.5, 1.58, 2.9, 5.93], [-17.5, 1.0, 3.8, 5.86], [-18.7, 0.36, 4.7, 5.62], [-19.0, 0.14, 5.05, 5.38]][::-1]   # (written nose to tail; a loft's stations run up x)
    fl = 3.35
    door = (13.55, 14.36)
    rows = [12.35 - i * 0.79 for i in range(29)]
    wins = [x for x in [12.85 - i * 0.533 for i in range(48)] if not (-0.6 < x < 0.3)]
    holes = window_holes([(x - 0.115, x + 0.115) for x in wins], 4.06, 4.4)
    FUS = loft("fuselage", "paint", fus, rnd, holes=holes, seg=2, corner=6, double=True)

    def plug_door(name, x0, x1, side):
        """A PLUG DOOR on its arm (parallel motion): the arm hinged at the forward jamb inside the skin (P), the door
        hinged on the arm's end (A, on its lining); the arm swings 110 deg out, the door back 110, so the door goes out
        ~.45 and forward ~.95 and stays parallel to the skin. Its skin and lining are pieces of the fuselage and of a
        lining loft just inside it; returns (the opening's region, the door's hinge, its sill)"""
        s, xc = (-1 if side == "left" else 1), (x0 + x1) / 2
        zs = s * loft_z(fus, rnd, xc, 4.25)
        R = region(x0, x1, fl + 0.01, 5.3, side)
        lin = loft(name + "Lining", "lining", shell_over(fus, [x0 - 0.35, xc, x1 + 0.35], -0.07), [rnd[0] - 0.07, rnd[1] - 0.07], seg=2, corner=6, double=True)
        pane = region(x0 + 0.31, x0 + 0.52, 4.08, 4.38, side)
        A, P = [x0 + 0.15, fl + 0.9, zs - s * 0.09], [x1 - 0.03, fl + 0.9, zs - s * 0.2]
        door_ = hinge(name, P, [
            rod(name + "Arm", "gear", 0.05, P, A, 8),
            rod(name + "ArmHi", "gear", 0.03, [P[0], P[1] + 0.12, P[2]], [A[0], A[1] + 0.12, A[2]], 6),
            box(name + "Boss", "gear", [0.12, 0.3, 0.1], [P[0], P[1] + 0.06, P[2]]),
            hinge("leaf", A, [
                piece(FUS, [R], name + "Skin", holes=[pane]),
                piece(lin, [region(x0 + 0.03, x1 - 0.03, fl + 0.06, 5.24, side)], name + "Lining", holes=[pane]),
                box(name + "Pane", "glass", [0.25, 0.34, 0.02], [x0 + 0.415, 4.23, zs - s * 0.035]),
                box(name + "HandleOut", "gear", [0.24, 0.05, 0.03], [x0 + 0.17, 4.5, zs + s * 0.012]),
                box(name + "HandleIn", "gear", [0.05, 0.5, 0.05], [x0 + 0.11, 4.35, zs - s * 0.11]),
                box(name + "Box", "gear", [0.6, 0.22, 0.08], [x0 + 0.405, fl + 0.35, zs - s * 0.11]),
                box(name + "Grip", "gear", [0.04, 0.3, 0.04], [x0 + 0.7, 4.6, zs - s * 0.12]),
            ], max_=-110 * s),
        ], max_=110 * s)
        sill = box(name + "Sill", "gear", [0.82, 0.03, 0.12], [xc, fl, s * (loft_z(fus, rnd, xc, fl + 0.1) - 0.04)])
        return R, door_, sill

    # (the four doors: L1/R1 forward of the galley, L2/R2 aft of the last row -- all opening forward)
    aft = (-14.6, -13.79)
    DOORS = [plug_door(n, *x, side) for n, x, side in [("doorL1", door, "left"), ("doorR1", door, "right"), ("doorL2", aft, "left"), ("doorR2", aft, "right")]]
    parts = [
        cut(FUS, [R for R, _, _ in DOORS]),
        box("cheat", "stripe", [0.012, 0.22, 25.0], on_loft(fus, rnd, 0.6, y=3.7, off=0.004), mirror="z"),
        # (the cockpit's panes, laid on the nose's surface)
        box("screen", "glass", [0.02, 0.62, 0.52], on_loft(fus, rnd, 17.62, z=0.36, off=0.012), mirror="z"),
        box("screenSide", "glass", [0.02, 0.42, 0.55], on_loft(fus, rnd, 17.12, y=4.98, off=0.012), mirror="z"),
        box("screenAft", "glass", [0.02, 0.36, 0.42], on_loft(fus, rnd, 16.55, y=5.08, off=0.012), mirror="z"),
        *[d for _, d, _ in DOORS], *[sl for _, _, sl in DOORS],
        # (the wings: root inside the fuselage, out through the kink to the tip; the sharklets; the flap-track fairings)
        surface("wing", "paint", [(0.0, 4.7, -2.7, 0.42), (2.0, 3.8, -2.45, 0.38), (6.3, 1.6, -2.3, 0.25), (12.0, -1.3, -4.05, 0.15), (17.4, -4.05, -5.5, 0.08)], 2.35, 5.1, mirror="z"),
        surface("sharklet", "paint", [(0.0, -4.0, -5.5, 0.07), (1.2, -4.9, -5.75, 0.05), (2.3, -5.45, -5.95, 0.03)], 2.35 + 17.35 * math.tan(math.radians(5.1)) - 0.02, 0, vertical=True, z=17.35 + 0.06, mirror="z"),
        *[lathe(f"fairing{i}", "paint", [[0, -0.6], [0.14, 0.2], [0.16, 1.4], [0.08, 2.4], [0, 2.8]], [x, 2.35 + s * math.tan(math.radians(5.1)) - 0.1, s, 0, 0, 90], sides=8, mirror="z") for i, (s, x) in enumerate([(4.2, -1.3), (8.3, -1.85), (11.4, -3.0), (14.2, -4.0)])],
        # (the engines under the wings, on their pylons)
        # (the nacelle's back third under the wing, its intake ~2.6 m ahead of the leading edge -- as on the A320, not hung
        #  wholly in front of it)
        *nacelle("engine", 1.45, 1.68, 5.75, 4.3, 1.06, mirror="z"),
        plate("pylon", "paint", [[4.0, 2.5], [2.4, 2.8], [-0.2, 2.95], [-1.2, 2.72], [0.0, 2.45], [3.8, 2.45]], 0.32, [0, 0, 5.75], mirror="z"),
        # (the tail: the fin and its rudder line, the tailplane)
        surface("fin", "tail", [(0.0, -12.4, -18.75, 0.33), (0.75, -12.95, -18.7, 0.3), (6.45, -16.9, -19.25, 0.1)], 5.25, vertical=True),
        surface("stab", "paint", [(0.0, -14.4, -18.6, 0.22), (1.3, -15.0, -18.7, 0.2), (6.2, -18.3, -19.75, 0.07)], 4.75, 6.0, mirror="z"),
        # (the gear: the nose leg with its two small wheels, the two main legs under the wing roots)
        *leg("noseLeg", 12.05, 2.05, 0.0, 0.38, 2, 0.42, 0.24, 0.08),
        *leg("mainLeg", -0.55, 2.55, 3.8, 0.585, 2, 0.88, 0.38, 0.12, mirror="z"),
        box("bay", "seam", [2.0, 0.02, 1.4], [-0.55, 1.82, 2.6], mirror="z"),
        lathe("beacon", "lamp-red", [[0, 0], [0.08, 0], [0.06, 0.08], [0, 0.1]], [2.0, y1 - 0.01, 0], sides=8),
        # INSIDE: the floor, the cockpit's bulkhead with its door, the galley, the rows, the bins, the lights
        box("floor", "carpet", [27.2, 0.1, 3.8], [1.2, fl - 0.05, 0]),
        box("floorNose", "carpet", [2.4, 0.1, 2.6], [16.0, fl - 0.05, 0]),
        end_wall("bulkhead", "lining", station_at(fus, 15.25), rnd, 15.25, 0.06, door=(0.8, y0, fl + 1.95), shrink=0.06, m=6),
        box("galley", "lining", [0.7, 1.95, 1.3], [13.0, fl + 0.975, 1.15]),
        box("galleyTop", "gear", [0.72, 0.04, 1.3], [13.0, fl + 1.0, 1.15]),
        box("lav", "lining", [0.62, 2.0, 1.1], [14.93, fl + 1.0, 1.25]),
        box("floorAft", "carpet", [2.6, 0.1, 3.2], [-13.7, fl - 0.05, 0]),
        box("galleyAft", "lining", [0.7, 1.95, 2.4], [-15.15, fl + 0.975, 0]),
        *runs("rows", [use(f"row{i}", W + "seat-row", [x, fl, 0.97], {"n": 3, "w": 0.46, "d": 0.46, "h": 0.44, "back": 0.68, "rake": 14, "arms": 1, "headrest": 1}, mirror="z") for i, x in enumerate(rows)]),
        plate("bin", "bin", [[-1.02, 4.92], [-1.84, 4.92], [-1.72, 5.32], [-1.5, 5.5], [-1.04, 5.46]], rows[0] - rows[-1] + 1.4, [(rows[0] + rows[-1]) / 2, 0, 0, 90, 0, 0], mirror="z"),
        box("binLip", "gear", [rows[0] - rows[-1] + 1.4, 0.03, 0.03], [(rows[0] + rows[-1]) / 2, 4.93, 1.03], mirror="z"),
        box("lights", "lamp", [rows[0] - rows[-1] + 1.0, 0.03, 0.5], [(rows[0] + rows[-1]) / 2, 5.88, 0]),
        box("psu", "lining", [rows[0] - rows[-1] + 1.4, 0.03, 0.3], [(rows[0] + rows[-1]) / 2, 4.9, 1.2], mirror="z"),
        # (the cockpit: two seats, the panel and its screens, the pedestal)
        use("captain", W + "seat", [16.35, fl, -0.5], {"w": 0.5, "h": 0.45, "arms": 1, "pedestal": 1}),
        use("firstOfficer", W + "seat", [16.35, fl, 0.5], {"w": 0.5, "h": 0.45, "arms": 1, "pedestal": 1}),
        box("panel", "gear", [0.35, 0.6, 2.0], [17.35, fl + 1.05, 0]),
        box("pedestalC", "gear", [0.8, 0.7, 0.35], [16.8, fl + 0.35, 0]),
    ]
    # (fix the screens' list placement: a use takes one `at`; spread them as separate parts)
    parts = [p for p in parts if p.get("id") != "display"] + [use(f"display{i}", W + "screen", [17.17, fl + 1.1, z], {"w": 0.2, "h": 0.2}) for i, z in enumerate((-0.75, -0.48, -0.12, 0.12, 0.48, 0.75))]
    return item("Airliner", "vehicle", "a narrow-body airliner of the A320 type, 37.6 m long, 35.8 m span, 11.8 m high: a hollow lofted fuselage with 46 windows a side and its four doors (L1, R1, L2, R2) on their arms (shut; each opens out and forward), swept wings with sharklets and flap-track fairings, two turbofans in lathe nacelles on pylons, the fin and tailplane, the tricycle gear -- and its cabin: 29 rows of 3+3 seats, overhead bins, lights, a galley, the cockpit's seats and panel behind the bulkhead",
        {"paint": "paint-white", "tail": {"pick": ["paint-navy", "paint-red", "#1f6fb2", "#0f6b5a", "paint-orange"]}, "stripe": "tail", "glass": "glass", "seam": "#8a8f96",
         "nacelle": "paint-silver", "fan": "gunmetal", "nozzle": "#5a5d62", "gear": "plastic-grey", "lining": "#e6e3dc", "carpet": "carpet-grey", "bin": "#f2f1ec", "lamp": "lamp",
         "cover": {"pick": ["upholstery", "upholstery-grey", "#2f3e6a"]}, "head": "#e8e6e0", "frame": "plastic-grey"}, parts, params={"open": 0},
        markers=[{"role": "door", "at": [(door[0] + door[1]) / 2, fl, -hw - 0.3]}])


# ---- THE LIGHT AEROPLANE ----------------------------------------------------------------------------------------
def light_plane():
    # A LIGHT AEROPLANE, high-winged, single-engined (the Cessna 172 type, 1956-: 8.28 m long, 11.0 m span, 2.72 m
    # high; four seats): the fuselage a hollow loft, its rear side windows cut through so the four seats show, a door
    # each side cut from it (its window glazed) and hinged at its front edge;
    # the windscreen laid on its slope; the wing on top of the cabin, straight inboard and tapering out, braced by a
    # strut each side; the cowling, the spinner and a two-bladed propeller (components/rotor); the fin and the
    # tailplane; the tricycle gear on its spring legs.
    rnd = [0.22, 0.2]
    fus = [[3.32, 0.28, 0.82, 1.32], [3.05, 0.47, 0.66, 1.46], [2.3, 0.53, 0.6, 1.6], [1.55, 0.56, 0.58, 1.9], [0.9, 0.58, 0.58, 2.0], [0.0, 0.57, 0.6, 2.0],
           [-0.85, 0.52, 0.68, 1.95], [-2.0, 0.38, 0.9, 1.74], [-3.4, 0.2, 1.14, 1.56], [-4.55, 0.09, 1.3, 1.46]][::-1]
    fl = 0.68
    FUS = loft("fuselage", "paint", fus, rnd, holes=[hole(-0.75, 0.3, 1.25, 1.84)], seg=3, corner=4, double=True)
    dX, dY, wX, wY = (0.42, 1.38), (0.74, 1.86), (0.5, 1.3), (1.2, 1.8)
    zf = lambda x, y: loft_z(fus, rnd, x, y)
    parts = [
        cut(FUS, [region(*dX, *dY, "both")]),
        piece(FUS, [region(-0.75, 0.3, 1.25, 1.84, "both")], "rearPane", gap=0, material="pane"),   # (the rear side windows' glass)
        # (THE DOORS, hinged at their front edge: the skin cut from the fuselage, its window glazed, the trim inside)
        hinge("door", [dX[1], 1.3, zf(dX[1], 1.3) - 0.01], [
            piece(FUS, [region(*dX, *dY)], "skin", holes=[region(*wX, *wY)]),
            piece(FUS, [region(*wX, *wY)], "pane", material="pane"),
            box("stripe", "stripe", [0.01, 0.08, 0.94], on_loft(fus, rnd, 0.9, y=1.05, off=0.006)),
            box("handle", "trim", [0.12, 0.025, 0.02], [0.55, 1.12, zf(0.55, 1.12) + 0.008]),
            box("card", "trim", [0.82, 0.4, 0.02], [0.9, 0.98, zf(0.9, 0.98) - 0.03]),
            box("armrest", "trim", [0.4, 0.05, 0.06], [0.95, 1.08, zf(0.95, 1.08) - 0.06]),
        ], max_=75, mirror="z"),
        box("windscreen", "glass", [0.02, 0.86, 0.72], on_loft(fus, rnd, 1.78, z=0, off=0.012)),
        box("stripe", "stripe", [0.01, 0.08, 4.11], on_loft(fus, rnd, -1.645, y=1.05, off=0.006), mirror="z"),   # (the stripe, broken by the door)
        box("stripeF", "stripe", [0.01, 0.08, 0.92], on_loft(fus, rnd, 1.84, y=1.05, off=0.006), mirror="z"),
        # (the nose: the cowling's intakes, the spinner and the propeller)
        box("intake", "trim", [0.02, 0.1, 0.18], [3.31, 1.12, 0.14], mirror="z"),
        lathe("spinner", "spinner", [[0.15, 0], [0.13, 0.12], [0.07, 0.24], [0, 0.29]], [3.32, 1.06, 0, 0, 0, -90], sides=16),
        use("prop", W + "rotor", [3.42, 1.06, 0, 0, 0, -90], {"n": 2, "R": 0.94, "c": 0.12, "t": 0.03, "pitch": 18, "hubR": 0.06, "hubH": 0.1}, {"blade": "prop", "hub": "spinner"}),
        rod("exhaust", "trim", 0.03, [2.7, 0.66, 0.2], [2.5, 0.55, 0.22], 6),
        # (the wing on the cabin's roof, its struts; the tail)
        surface("wing", "paint", [(0.0, 1.22, -0.42, 0.11), (2.6, 1.22, -0.42, 0.11), (5.45, 1.05, -0.12, 0.07)], 2.06, 1.7, mirror="z"),
        rod("strut", "paint", 0.03, [0.3, 0.82, 0.52], [0.45, 1.98, 2.55], 8, mirror="z"),
        surface("fin", "paint", [(0.0, -2.95, -4.6, 0.07), (0.25, -3.4, -4.6, 0.06), (1.22, -4.2, -4.7, 0.04)], 1.46, vertical=True),
        surface("stab", "paint", [(0.0, -3.7, -4.6, 0.06), (1.72, -4.0, -4.58, 0.04)], 1.38, 0.0, mirror="z"),
        use("nav", W + "lamp", [0.2, 2.06, 5.47, -90, 0, 0], {"shape": "round", "r": 0.04}, {"lens": "lamp-green"}),
        use("navL", W + "lamp", [0.2, 2.06, -5.47, 90, 0, 0], {"shape": "round", "r": 0.04}, {"lens": "lamp-red"}),
        # (the gear: the main wheels on their spring-steel legs, the nose wheel on its strut, the fairings)
        rod("springLeg", "paint", 0.035, [-0.2, 0.66, 0.45], [-0.25, 0.26, 1.2], 8, mirror="z"),
        use("mainWheel", W + "wheel", [-0.25, 0.25, 1.24], {"r": 0.25, "w": 0.14, "spokes": 0, "rim": 0.5}, mirror="z"),
        sphere("pant", "paint", 0.2, [-0.25, 0.27, 1.25], stretch=[1.9, 1.05, 0.55], sides=12, mirror="z"),
        rod("noseStrut", "gear", 0.035, [2.75, 0.75, 0], [2.75, 0.2, 0], 8),
        use("noseWheel", W + "wheel", [2.75, 0.2, 0], {"r": 0.2, "w": 0.12, "spokes": 0, "rim": 0.5}),
        # INSIDE: the floor, four seats, the panel and its screen, the yokes
        box("floor", "carpet", [2.4, 0.04, 1.0], [0.3, fl, 0]),
        use("seatF", W + "seat", [0.62, fl, 0.26], {"w": 0.44, "h": 0.32, "back": 0.6, "d": 0.46, "pedestal": 1}, mirror="z"),
        use("seatR", W + "seat", [-0.42, fl, 0.26], {"w": 0.44, "h": 0.32, "back": 0.6, "d": 0.46, "pedestal": 1}, mirror="z"),
        box("panel", "trim", [0.12, 0.42, 1.06], [1.5, 1.45, 0]),
        use("display", W + "screen", [1.43, 1.47, 0.0, 180, 0, 0], {"w": 0.3, "h": 0.22}),
        rod("yoke", "trim", 0.015, [1.44, 1.33, 0.26], [1.15, 1.33, 0.26], 6, mirror="z"),
        box("yokeBar", "trim", [0.03, 0.08, 0.28], [1.15, 1.35, 0.26], mirror="z"),
    ]
    return item("Light aeroplane", "vehicle", "a high-winged single-engined light aeroplane of the Cessna 172 type, 8.28 m long, 11.0 m span, 2.72 m high: a hollow lofted fuselage with its rear windows open on the four seats and a front-hinged door each side (glazed), the windscreen, a strut-braced wing on the cabin, cowling, spinner and two-bladed propeller, fin and tailplane, tricycle gear with spats",
        {"paint": "paint-white", "stripe": {"pick": ["paint-red", "paint-navy", "#1f6fb2", "paint-maroon", "paint-orange"]}, "glass": "glass", "trim": "plastic-black", "spinner": "stripe",
         "prop": "plastic-black", "gear": "steel", "carpet": "carpet-grey", "cover": {"pick": ["upholstery", "upholstery-red", "leather-dark"]}, "pane": "window-glass"}, parts, params={"open": 0})


# ---- THE HELICOPTER ---------------------------------------------------------------------------------------------
def helicopter():
    # A LIGHT TWIN HELICOPTER (the EC135 / Bell 206 class: 10.2 m rotor, 12 m overall with the rotor turning, the
    # fuselage 10 m, 3.5 m high): the cabin a hollow loft running out into the tail boom, its doors cut from it -- the
    # front doors hinged at their front edge, the rear doors sliding out and back along the side on a rail -- each
    # glazed, so the two pilots' seats, the panel and the rear bench show; the glazed nose;
    # the engines' fairing on the roof, the mast and a four-bladed main rotor, the fin with its two-bladed tail rotor,
    # the stabiliser with its endplates; the skids on their cross tubes.
    rnd = [0.34, 0.42]
    body = [[1.62, 0.8, 0.46, 2.32], [1.0, 0.8, 0.45, 2.38], [-0.6, 0.8, 0.45, 2.42], [-1.55, 0.72, 0.6, 2.38], [-2.3, 0.45, 1.1, 2.2],
            [-3.1, 0.22, 1.52, 1.98], [-5.2, 0.16, 1.62, 1.92], [-7.6, 0.1, 1.72, 1.9]][::-1]
    nose = [[1.62, 0.8, 0.46, 2.32], [2.1, 0.72, 0.5, 2.12], [2.45, 0.5, 0.62, 1.72], [2.62, 0.1, 1.02, 1.22]]
    fl = 0.62
    BODY = loft("body", "paint", body, rnd, caps=[True, False], seg=3, corner=5, double=True)
    fX, rX, dY = (0.42, 1.55), (-1.3, 0.3), (0.95, 2.02)
    fW, rW, wY = (0.5, 1.47), (-1.2, 0.2), (1.32, 1.95)
    zb = lambda x, y: loft_z(body, rnd, x, y)
    parts = [
        cut(BODY, [region(*fX, *dY, "both"), region(*rX, *dY, "both")]),
        # (THE FRONT DOORS, hinged at their front edge; THE REAR DOORS, out and back along the side on their rail)
        hinge("frontDoor", [fX[1], 1.4, zb(fX[1], 1.4) - 0.01], [
            piece(BODY, [region(*fX, *dY)], "skin", holes=[region(*fW, *wY)]),
            piece(BODY, [region(*fW, *wY)], "pane", material="pane"),
            box("handle", "trim", [0.12, 0.025, 0.02], [0.55, 1.2, zb(0.55, 1.2) + 0.008]),
            box("card", "trim", [0.95, 0.3, 0.02], [0.98, 1.1, zb(0.98, 1.1) - 0.03]),
        ], max_=70, mirror="z"),
        plug_slide("rearDoor", [-0.95, 0, 0.07], [
            piece(BODY, [region(*rX, *dY)], "skin", holes=[region(*rW, *wY)]),
            piece(BODY, [region(*rW, *wY)], "pane", material="pane"),
            box("handle", "trim", [0.12, 0.025, 0.02], [0.18, 1.2, zb(0.18, 1.2) + 0.008]),
            box("card", "trim", [1.2, 0.3, 0.02], [-0.45, 1.1, min(zb(-1.05, 1.1), zb(0.15, 1.1)) - 0.03]),
        ], mirror="z"),
        rod("doorRail", "trim", 0.015, [0.25, 2.04, zb(0.25, 2.04) + 0.02], [-1.65, 2.04, zb(-1.65, 2.04) + 0.02], 6, mirror="z"),
        loft("nose", "glass", nose, rnd, caps=[False, True], seg=3, corner=5),
        box("chin", "paint", [0.6, 0.18, 1.2], [2.0, 0.6, 0]),
        box("pillar", "paint", [0.06, 1.1, 0.06], on_loft(nose, rnd, 2.0, y=1.55, off=0.0), mirror="z"),
        # (the roof: the engines' fairing, its intakes and exhausts; the mast and the rotor)
        loft("cowl", "paint", [[-2.7, 0.3, 2.2, 2.6], [-2.2, 0.48, 2.28, 2.98], [0.0, 0.5, 2.34, 3.02], [0.75, 0.32, 2.36, 2.7]], [0.05, 0.28], seg=3),
        box("intake", "trim", [0.03, 0.18, 0.3], [0.62, 2.72, 0.2], mirror="z"),
        rod("exhaust", "trim", 0.1, [-2.0, 2.75, 0.32], [-2.5, 2.8, 0.4], 8, mirror="z"),
        rod("mast", "steel", 0.08, [-0.4, 2.95, 0], [-0.4, 3.35, 0], 10),
        use("rotor", W + "rotor", [-0.4, 3.38, 0], {"n": 4, "R": 4.85, "c": 0.3, "t": 0.05, "pitch": 4, "hubR": 0.22, "hubH": 0.26}),
        # (the tail: the boom ends in the fin with its tail rotor, the stabiliser and its endplates)
        plate("fin", "paint", [[-7.0, 1.82], [-7.7, 1.72], [-8.15, 2.95], [-7.8, 3.0], [-7.3, 2.05]], 0.08, [0, 0, 0]),
        plate("ventral", "paint", [[-7.2, 1.75], [-7.75, 1.75], [-7.95, 1.3], [-7.6, 1.3]], 0.06, [0, 0, 0]),
        rod("tailSkid", "steel", 0.015, [-7.6, 1.3, 0], [-7.95, 1.25, 0], 6),
        lathe("trHub", "steel", [[0.06, -0.08], [0.06, 0.12], [0, 0.14]], [-7.85, 2.4, 0.04, 0, 90, 0], sides=8),
        use("tailRotor", W + "rotor", [-7.85, 2.4, 0.18, 0, 90, 0], {"n": 2, "R": 0.75, "c": 0.14, "t": 0.025, "pitch": 8, "hubR": 0.06, "hubH": 0.1}),
        box("stab", "paint", [0.5, 0.05, 2.0], [-6.1, 1.85, 0]),
        box("endplate", "paint", [0.45, 0.4, 0.04], [-6.15, 1.9, 1.0], mirror="z"),
        # (the skids on their cross tubes)
        sweep("skid", "steel", [[-1.75, 0.04, 1.1], [1.2, 0.04, 1.1], [1.55, 0.12, 1.1], [1.75, 0.32, 1.1]], 0.04, mirror="z"),
        sweep("crossTube", "steel", [[0, 0.04, -1.1], [0, 0.4, -1.0], [0, 0.55, -0.72], [0, 0.56, 0.72], [0, 0.4, 1.0], [0, 0.04, 1.1]], 0.04, at=[[1.0, 0, 0], [-1.05, 0, 0]]),
        use("strobe", W + "lamp", [-7.9, 3.02, 0, 0, 0, 90], {"shape": "round", "r": 0.04}, {"lens": "lamp-red"}),
        # INSIDE: the floor, the pilots' seats, the panel, the sticks, the rear bench
        box("floor", "carpet", [3.3, 0.04, 1.4], [0.1, fl, 0]),
        use("pilot", W + "seat", [1.1, fl, 0.36], {"w": 0.46, "h": 0.4, "back": 0.65, "d": 0.45, "pedestal": 1}, mirror="z"),
        use("bench", W + "seat-row", [-0.75, fl, 0], {"n": 3, "w": 0.47, "d": 0.45, "h": 0.42, "back": 0.62, "arms": 0, "headrest": 1}),
        box("panel", "trim", [0.25, 0.4, 1.2], [2.05, 1.35, 0, 0, 0, 15]),
        use("display", W + "screen", [1.92, 1.42, 0.25, 180, 0, -15], {"w": 0.22, "h": 0.18}, mirror="z"),
        rod("cyclic", "trim", 0.015, [1.4, fl, 0.36], [1.32, fl + 0.6, 0.36], 6, mirror="z"),
        rod("collective", "trim", 0.018, [0.95, fl + 0.15, 0.08], [1.25, fl + 0.4, 0.08], 6),
    ]
    return item("Helicopter", "vehicle", "a light twin-engined helicopter of the EC135 / Bell 206 class, 10.2 m rotor, the fuselage 10 m long, 3.5 m high: a hollow lofted cabin and tail boom, its glazed doors (the front ones hinged, the rear ones sliding back) on the pilots' seats, panel and the rear bench, the glazed nose, the engines' fairing, the mast with a four-bladed rotor, the fin and its two-bladed tail rotor, the stabiliser with endplates, skids on cross tubes",
        {"paint": {"pick": ["paint-red", "paint-yellow", "paint-navy", "paint-white", "#2b4a2b", "paint-black"]}, "glass": "glass", "trim": "plastic-black", "steel": "aluminium", "blade": "#2a2a2c",
         "carpet": "carpet-grey", "cover": "upholstery-grey", "frame": "plastic-grey", "pane": "window-glass"}, parts, params={"open": 0})


def write_all():
    write("modern/air/airliner", airliner(), "air")
    write("modern/air/light-plane", light_plane(), "air")
    write("modern/air/helicopter", helicopter(), "air")

GROUPS = {"air": "aircraft"}
