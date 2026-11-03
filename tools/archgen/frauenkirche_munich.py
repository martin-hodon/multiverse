# THE FRAUENKIRCHE, Munich (Dom zu Unserer Lieben Frau, 1468-88, Jorg von Halsbach; the caps 1525), from components: a
# late-Gothic BRICK HALL CHURCH -- nave and aisles vaulted to one height on two rows of slender octagonal pillars, the
# buttresses drawn INSIDE as wall piers with the chapels between them, so the outside is a plain wall of tall lancets --
# under ONE huge steep roof of plain tiles with rows of little shed dormers; a pent roof round the wall-head under a light
# frieze; the polygonal choir; and the two WEST TOWERS, square and almost unbroken, banded in storeys by light friezes, each
# going over into a short octagon and crowned by its WELSCHE HAUBE (`components/welsche-haube`, written here), the
# recessed west front between them with its porch and the great gable over it; side portals with ogee heads.
#   Frame: the nave's axis along z, the WEST FRONT faces +z; south is +x (north -x). Mapped from OpenStreetMap
#   (way 225698612 and its parts): z = 9.15 - x_east, x = -3.85 - y_north (metres from 48.13860 N, 11.57345 E).
# SOURCED (de/en Wikipedia, OSM): length 109 m, width 40 m; towers 98.57 / 98.45 m; vault 31 m; 22 octagonal pillars,
#   22 m to their capitals; inner buttresses with chapels; five portals with ogee (Kielbogen) frames, two in each long
#   side; square towers to about ridge height, then octagons and the caps of 1525; the body 93 x 40 m on the plan with a
#   half-decagon apse (OSM); the towers' plan about 15.3 x 16.4 m, 8.8 m apart; the porch 3.5 m deep, 15 m high (OSM).
# ESTIMATED (from a 19th-century elevation and photographs): the wall-head 33.2 m, the roof's pitch 50 deg (ridge 57 m);
#   the windows' sill 4 m and head 26.5 m; the square shafts to 58 m, the octagons to 86 m, the caps 9 m and the finials;
#   the side portals' size; the dormers' rows and number; 10 bays (the windows) where the real hall has 11 pillars a side.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
r4 = lambda v: round(v, 4)
Q, PI = math.pi / 2, math.pi


# ---- L1: THE WELSCHE HAUBE -- the Renaissance cap of a German tower (Munich's Frauenkirche 1525, the Augsburg and
# Ingolstadt towers after it): a copper BULB on an eave ring, rising from the tower's head without a drum, swelling as an
# onion or not at all and drawn in to a point, ribbed at its corners; a short neck, a little knob, the rod, the gilt ball
# and the cross. (A Baroque helm with open lanterns and a second bulb is `baroque-helm`.)
def welsche_haube():
    cp, cb = {}, []
    def ca(n, d): cp[n] = d; cb.append(n)
    ca("foot", {"type": "prism", "plan": {"sides": "sides", "radius": "R + 0.05"}, "height": "footH", "flatRoof": True, "at": [[0, 0, 0, 0]],
                "courses": [{"y": 0, "h": "footH", "out": "footOut", "profile": "batter"}],
                "_about": "the eave ring the bulb stands on, its copper skirt flaring footOut past it at the foot"})
    ca("bulb", {"type": "dome", "sides": "sides", "radius": "R", "thickness": 0, "turn": "turn", "at": [[0, "footH", 0, 0]], "standsOn": ["foot"],
                "head": {"profile": "onion", "bulge": "bulge", "neck": "neck"},
                "_about": "the bulb: an onion (bulge 1: rising vertical from its eave and not swelling past it, as Munich's; more: an onion) drawn in to its point (neck)"})
    ca("bulb ribs", {"type": "ribs", "on": "bulb", "count": "sides", "width": "ribW", "depth": "ribD", "standsOn": ["bulb"],
                     "_about": "the standing ribs up its corners"})
    ca("neck", {"type": "column", "radius": "knobR * 0.5", "height": "knobR * 1.4", "sides": 8, "at": [[0, "0 - knobR * 0.3", 0, 0]], "atop": "bulb",
                "standsOn": ["bulb"], "_about": "the neck out of the bulb's point"})
    ca("knob", {"type": "dome", "sides": 8, "radius": "knobR", "thickness": 0, "at": [[0, 0, 0, 0]], "atop": "neck", "standsOn": ["neck"],
                "head": {"profile": "onion", "bulge": "knobBulge", "neck": "knobNeck"}, "_about": "the little knob on it"})
    ca("rod", {"type": "column", "radius": "rodR", "height": "rodH", "sides": 6, "at": [[0, "0 - knobR * 0.2", 0, 0]], "atop": "knob", "standsOn": ["knob"],
               "_about": "the rod"})
    ca("ball", {"type": "dome", "sides": 8, "radius": "ballR * 0.4", "thickness": 0, "at": [[0, "0 - ballR * 0.6", 0, 0]], "atop": "rod", "standsOn": ["rod"],
                "head": {"profile": "onion", "bulge": 2.5, "neck": 0.45}, "_about": "the gilt ball"})
    ca("cross", {"type": "bars", "w": "crossW", "h": "crossW",
                 "lines": [[0, 0, 0, 0, "crossH", 0], ["0 - crossH * 0.3", "crossH * 0.68", 0, "crossH * 0.3", "crossH * 0.68", 0]],
                 "at": [[0, "0 - ballR * 0.3", 0, 0]], "atop": "ball", "standsOn": ["ball"], "_about": "the cross on the ball"})
    doc = {"name": "welsche haube",
           "_about": "THE WELSCHE HAUBE, the Renaissance cap of a German tower (the Frauenkirche's in Munich, 1525): a copper BULB on an eave ring set on the tower's head -- an onion struck from two radii (bulge, neck), rising without a drum, ribbed up its corners -- then a neck, a little knob, the rod, the gilt ball and the cross. Place it at the middle of the tower's head; `sides` faces to it (8 over an octagon), its faces on the axes like the tower's (`turn` -0.5: corners on them). Build without 'bulb ribs' for a smooth one. For a helm with open lanterns and a second bulb, use `baroque-helm`.",
           "params": {"detail": 4, "sides": 8, "R": 7.0, "footH": 0.6, "footOut": 0.3, "turn": 0, "bulge": 1.0, "neck": 0.32,
                      "ribW": "R * 0.035", "ribD": "R * 0.02", "knobR": "R * 0.06", "knobBulge": 1.3, "knobNeck": 0.8,
                      "rodR": "R * 0.012", "rodH": "R * 0.03", "ballR": "R * 0.03", "crossH": "R * 0.07", "crossW": "R * 0.012",
                      "_R": "the bulb's radius at its eave (to its corners); the eave ring footH tall, its skirt flaring footOut past it at the foot",
                      "_bulge": "the bulb's two radii in half-widths (profiles.js onion): bulge 1 rises vertical from the eave, more swells out past it; neck the concave draw to the point -- small, a short sharp point (height R * sqrt(1 + 2 neck) at bulge 1)",
                      "_knobR": "the neck (knobR / 2 across, 0.7 knobR tall) and the little knob on it (an onion of knobBulge, knobNeck)",
                      "_rodH": "the rod (rodR, rodH), the ball (ballR in radius, a drop 2.1 ballR tall) and the cross (crossH, its bars crossW); haube_height() in tools/archgen/frauenkirche_munich.py adds it all up"},
           "build": cb, "parts": cp}
    open(os.path.join(ROOT, "assets/architecture/components/welsche-haube.json"), "w").write(json.dumps(doc, indent=2) + "\n")


def onion_h(a, bulge, neck):               # an onion's height over its springing, `a` its half-width (profiles.js onion)
    R1, R2 = a * max(1, bulge), a * max(.05, neck)
    return math.sqrt(max(0, R1 * R1 - a * a)) + math.sqrt(R1 * R1 + 2 * R1 * R2)
def haube_height(R, footH, bulge, neck, knobR, kb=1.3, kn=0.8, rodH=None, ballR=None, crossH=None):
    rodH, ballR, crossH = rodH if rodH is not None else R * .03, ballR if ballR is not None else R * .03, crossH if crossH is not None else R * .07
    return (footH + onion_h(R, bulge, neck) + knobR * 1.1 + onion_h(knobR, kb, kn) - knobR * .2 + rodH
            + onion_h(ballR * .4, 2.5, .45) - ballR * .6 + crossH - ballR * .3)


welsche_haube()



# ---- THE CHURCH AS ITS STRUCTURE: the `basilica` part as a HALL (arch/gothic.js) -- one roof over all, the wall piers inside
BAYS, BAY = 10, 7.37                       # the straight bays, z from +L/2 (west) to -L/2, the half-decagon apse beyond
NW, AW, T, TA = 12.6, 12.6, 1.0, 1.6       # the pier lines apart, pier line to the outer wall's centre line, the walls
SPR, VR, PITCH, OV, ER = 22.0, 9.0, 50, 0.5, 1.4
L = BAYS * BAY
OUTR = NW / 2 + AW                         # the outer wall's centre line
FACE = OUTR + TA / 2                       # ...its face
WALLTOP = SPR + VR + 0.5 + 0.3 + ER        # the vault's keystone, its extrados, the wall carried on over it (hallLevels)
TP = math.tan(math.radians(PITCH))
EAVE = FACE + OV
RIDGE = WALLTOP + EAVE * TP
roofY = lambda r: WALLTOP + (EAVE - r) * TP  # the great roof's surface, r out from the axis
sideDoor = lambda bay, x: {"bay": bay, "x": x, "w": 2.8, "h": 6.0, "head": "ogee"}
add("church", {"type": "basilica", "hall": True, "bays": BAYS, "bayLen": BAY, "naveW": NW, "aisleW": AW, "t": T, "aisleT": TA,
               "apse": 5, "spring": SPR, "vaultRise": VR, "pierR": 0.95, "shaft": 0.16, "pitch": PITCH, "overhang": OV, "eaveRise": ER,
               "aisleSill": 4.0, "aisleWin": 3.0, "aisleWinTop": 26.5, "buttressW": 1.4, "buttressIn": 3.2, "buttressInTop": SPR,
               "flyers": False, "pinnacles": False, "pent": {"y": 31.0, "out": 2.6, "pitch": 45, "t": 0.25},
               "aisleDoors": [sideDoor(1, -1), sideDoor(6, -1), sideDoor(1, 1), sideDoor(6, 1)], "at": [[0, 0, 0, 0]],
               "_about": "nave, aisles and choir as one HALL: two rows of slender pillars to 22m, the rib vaults at 31m over all three vessels and round the apse, the wall piers inside with chapels between them, the plain outer wall with a tall lancet a bay, the side portals in the first and sixth bays, a pent roof round the wall-head, ONE steep roof over all"})

# ---- THE WEST TOWERS: square brick shafts to 58m, banded by friezes, then the octagons to 86m and the caps
TW, TT, GAP = 15.4, 2.6, 8.9               # the towers' plan (square), their walls, the gap between them
TZ = L / 2 + TW / 2                        # their middles, the east face on the hall's west end
TX = GAP / 2 + TW / 2
FRONT = TZ + TW / 2
SQ, OCT_H, OF = 58.0, 28.0, 13.0           # the square shafts' top, the octagons' height and width across the flats
CH = r4((OF - OF / (1 + math.sqrt(2))) / 2)  # the octagon's chamfer: a regular octagon
slit = lambda y: {"at": 0, "width": 0.8, "sill": y, "springing": y + 2.6, "head": {"profile": "pointed", "spread": 0.5}}
FRIEZE = [10.8, 20.4, 30.0, 39.6, 49.2, 56.4]   # the friezes' feet, each a whole number of the pattern's 1.2m
# THE TAPER ("verjuengen sich nach oben leicht"): three stages, each set in by INSET a side at a frieze, the walls thinner
# by as much so the inside stays one shaft (the stair's floor fits every stage)
INSET = 0.25
STAGES = [(0.0, [12.0, 9.6]), (21.6, [9.6, 9.6]), (40.8, [9.6, 7.6])]   # each stage's foot and its storeys
def tower(sx, k):
    y0, hs = STAGES[k]
    w, t = TW - 2 * k * INSET, TT - k * INSET
    tiers = [{"h": h, "openings": [slit(3.0)] if (k, j) != (0, 0) else []} for j, h in enumerate(hs)]
    front = [dict(tr) for tr in tiers]
    east = [dict(tr) for tr in tiers]
    if k == 0:
        front[0] = {"h": hs[0], "openings": [{"at": 0, "width": 1.4, "sill": 4.0, "springing": 7.0, "head": {"profile": "pointed", "spread": 0.5}}]}
        east[0] = {"h": hs[0], "openings": [{"at": -sx * 2.5, "width": 2.2, "sill": 0, "springing": 3.4, "head": {"profile": "pointed", "spread": 0.5}}]}
    inner = [{"h": h, "openings": []} for h in hs]   # the face toward the other tower: the porch and the front against it
    faces = {"0": front, "2": east, "3" if sx > 0 else "1": inner}
    courses = ([{"y": 0, "h": 1.0, "out": 0.25, "profile": "plinth"}] if k == 0 else []) + \
              [{"y": r4(y - y0), "h": 1.2, "out": 0.12, "profile": "band"} for y in FRIEZE if y0 <= y < y0 + sum(hs)]
    return {"type": "enclosure", "plan": {"rect": [w, w]}, "thickness": t, "height": sum(hs), "tiers": tiers, "faces": faces,
            "courses": {"list": courses, "skip": ["3" if sx > 0 else "1"]}, "interior": True, "at": [[sx * TX, y0, TZ, 0]],
            **({"standsOn": [f"{'south' if sx > 0 else 'north'} tower" + (f" {k}" if k > 1 else "")]} if k else {})}
for sx, nm in ((1, "south"), (-1, "north")):
    for k in range(3):
        add(f"{nm} tower" + (f" {k + 1}" if k else ""), {**tower(sx, k), "_about": f"the {nm} tower's square shaft, stage {k + 1} of 3, each set in {INSET}m at a frieze: banded in storeys by friezes, slit windows" + ("; its door into the church" if k == 0 else "")})
# the CORNER LESENES, storey by storey between the friezes (the friezes run on round the corner over them), each corner
# closed: the strip on the front reaches round the arris to meet the one on the side
LW, LD = 1.3, 0.35
STOREYS = [(1.0, 10.8), (12.0, 20.4), (21.6, 30.0), (31.2, 39.6), (40.8, 49.2), (50.4, 56.4)]
for j, (ya, yb) in enumerate(STOREYS):
    ins = (j // 2) * INSET
    fz, hw = FRONT - ins, TW / 2 - ins
    outer = [[r4(sx * (TX + hw + LD - (LW + LD) / 2)), ya, r4(fz + LD / 2), 0] for sx in (1, -1)]
    inner = [[r4(sx * (TX - hw + LW / 2)), ya, r4(fz + LD / 2), 0] for sx in (1, -1)]
    side = [[r4(sx * (TX + hw + LD / 2)), ya, r4(z), 0] for sx in (1, -1) for z in (fz - LW / 2, TZ - hw + LW / 2)]
    add(f"lesenes {j + 1}", {"type": "box", "width": LW + LD, "length": LD, "height": r4(yb - ya), "at": outer, "flatRoof": True,
                             "_about": "the corner lesenes on the towers' west faces, round their outer arrises"})
    add(f"inner lesenes {j + 1}", {"type": "box", "width": LW, "length": LD, "height": r4(yb - ya), "at": inner, "flatRoof": True})
    add(f"side lesenes {j + 1}", {"type": "box", "width": LD, "length": LW, "height": r4(yb - ya), "at": side, "flatRoof": True,
                                  "_about": "...and on their long sides"})
TW3, TT3 = TW - 4 * INSET, TT - 2 * INSET   # the top stage's width and walls: the inside is TW - 2 TT throughout
add("south stair", comp("components/tower-stair", {"W": TW - 2 * TT, "H": SQ, "tx": "0.15 - c", "tz": 0}, [[TX, 0, TZ, 0]],
                        _about="the south tower climbed: a stair turret against its inner wall (clear of the octagon's chamfers) to the floor at the shaft's head"))
add("tower heads", {"type": "box", "width": TW - 2 * TT, "length": TW - 2 * TT, "height": 0.4, "flatRoof": True,
                    "at": [[-TX, SQ - 0.4, TZ, 0]], "_about": "the north tower's floor at the shaft's head (the south one's is its stair's)"})
# THE BROACHES: at each corner of the square's head a sloping copper-clad triangle from the corner up onto the octagon's
# diagonal face, so the square goes over into the octagon without a flat ledge there
BU = TW3 / 2 * math.sqrt(2) - OF / 2 + 0.05          # from the diagonal face (a little inside it) out to the square's corner
BHW = OF / (1 + math.sqrt(2)) / 2                     # the diagonal face's half width
BH = BU * math.tan(math.radians(50))
broach_at = [[r4(sx * TX + dx * (OF / 2 - 0.05) / math.sqrt(2)), SQ, r4(TZ + dz * (OF / 2 - 0.05) / math.sqrt(2)), r4(math.atan2(-dz, dx))]
             for sx in (1, -1) for dx in (1, -1) for dz in (1, -1)]
add("broaches", {"type": "prism", "plan": {"points": [[0, r4(-BHW)], [r4(BU), 0], [0, r4(BHW)]]}, "height": r4(BH), "slope": [r4(-(BH - 0.08) / BU), 0],
                 "at": broach_at, "_about": "the broaches: the square's corners carried up in slopes onto the octagon's diagonal faces"})
belfry = {"at": 0, "width": 2.2, "sill": 1.0, "springing": 7.4, "head": {"profile": "pointed", "spread": 0.5}, "glass": False}
arcade = {"pattern": "3", "width": 0.75, "gap": 0.45, "sill": 0.8, "springing": 2.5, "head": {"profile": "semicircular"}, "glass": False}
oct_tiers = [{"h": 9.6, "openings": []}, {"h": 12.0, "openings": [belfry]}, {"h": 6.4, "openings": arcade}]
add("octagons", {"type": "enclosure", "plan": {"rect": [OF, OF], "chamfer": CH}, "thickness": 1.5, "height": OCT_H, "tiers": oct_tiers,
                 "courses": [{"y": 8.4, "h": 1.2, "out": 0.12, "profile": "band"}, {"y": 21.6, "h": 0.6, "out": 0.15, "profile": "string"},
                             {"y": OCT_H - 0.9, "h": 0.9, "out": 0.35, "profile": "cornice"}],
                 "at": [[sx * TX, SQ, TZ, 0] for sx in (1, -1)], "standsOn": ["south tower 3", "north tower 3"],
                 "_about": "the octagons: a blind storey (the clocks'), the belfry with a pointed opening in every face, a row of little arches under the cornice"})
add("octagon floors", {"type": "prism", "plan": {"rect": [OF - 2, OF - 2], "chamfer": r4(CH * (OF - 2) / OF)}, "height": 0.4, "flatRoof": True,
                       "at": [[sx * TX, SQ + OCT_H - 0.4, TZ, 0] for sx in (1, -1)], "_about": "the floor at the octagon's head the cap stands over"})
CLOCK_Y, CLOCK_R = 5.0, 1.6                 # the dials' middles over the octagons' feet, their radius
FACES = [(0, OF / 2, 0.0), (OF / 2, 0, math.pi / 2), (0, -OF / 2, math.pi), (-OF / 2, 0, -math.pi / 2)]   # the main faces, the yaw turning +z out to each
add("clocks", comp("components/clock-dial", {"R": CLOCK_R, "t": 0.1, "hour": 10, "minute": 9},
                   [[r4(sx * TX + fx), SQ + CLOCK_Y, r4(TZ + fz), r4(a)] for sx in (1, -1) for fx, fz, a in FACES],
                   _about="the clocks on the octagons' four main faces, in their blind storey"))
# THE CAPS, to the sourced 98.5m: the bulb's height from its two radii, the finial short (a knob, rod, ball and cross)
HR, HF, HB, HN = 7.15, 0.5, 1.0, 0.32
TOP, BASE = 98.5, 0.3                      # the cross's top over the ground; everything stands on the 0.3m base
crossH = TOP - BASE - (SQ + OCT_H) - haube_height(HR, HF, HB, HN, HR * 0.06, crossH=0)
assert 0.4 < crossH < 1.2, crossH
assert abs(BASE + SQ + OCT_H + haube_height(HR, HF, HB, HN, HR * 0.06, crossH=crossH) - TOP) < 1e-6
add("haubes", comp("components/welsche-haube", {"R": HR, "footH": HF, "footOut": 0.45, "bulge": HB, "neck": HN, "crossH": r4(crossH)},
                   [[sx * TX, SQ + OCT_H, TZ, 0] for sx in (1, -1)], build=["foot", "bulb", "bulb ribs", "neck", "knob", "rod", "ball", "cross"],
                   _about="the two Welsche Hauben of 1525, green copper, to 98.5m"))

# ---- THE WEST FRONT between the towers: the porch, the recessed front with its window, the gable to the ridge
GW = GAP + 4 * INSET                       # the gap at the towers' top stage (they taper): the front and its roof fill it
YW = roofY(GW / 2)                         # the great roof over the gap's edges
FZ = FRONT - 3.5                           # the recessed front's outer face, 3.5m behind the towers' (the porch's depth)
add("west front", {"type": "wall", "width": GW, "height": r4(YW), "thickness": 1.5, "at": [[0, 0, r4(FZ - 0.75), 0]],
                   "tiers": [{"h": 15.0, "openings": [{"at": 0, "width": 3.0, "sill": 0, "springing": 5.2, "head": {"profile": "ogee"}}]},
                             {"openings": [{"at": 0, "width": 3.4, "sill": 4.6, "springing": 12.0, "head": {"profile": "pointed", "spread": 0.6}, "tracery": True}]}],
                   "_about": "the recessed west front: the inner portal, the great window over the porch"})
add("porch", {"type": "wall", "width": GAP, "height": 15.0, "thickness": 1.2, "at": [[0, 0, r4(FRONT - 0.6), 0]],
              "tiers": [{"h": 11.0, "openings": [{"at": 0, "width": 4.2, "sill": 0, "springing": 6.0, "head": {"profile": "ogee"},
                                                  "surround": {"style": "romanesque", "orders": 3, "shafts": False}, "wimperg": {"pitch": 62}}]}, {"openings": []}],
              "courses": [{"y": 13.8, "h": 1.2, "out": 0.12, "profile": "band"}],
              "_about": "the porch's front between the towers: the main portal under its ogee frame"})
add("porch roof", {"type": "box", "width": GAP, "length": r4(FRONT - 1.2 - FZ), "height": 0.4, "flatRoof": True,
                   "at": [[0, 14.6, r4((FRONT - 1.2 + FZ) / 2), 0]], "_about": "the porch's flat roof"})
GH = RIDGE - YW
add("west gable", {"type": "prism", "plan": {"rect": [GW / 2, 1.5]}, "height": r4(GH - GW / 4 * TP), "slope": [r4(-TP), 0],
                   "at": [[GW / 4, r4(YW), r4(FZ - 0.75), 0], [-GW / 4, r4(YW), r4(FZ - 0.75), PI]],
                   "_about": "the gable over the front, cut to the great roof's pitch"})
add("narthex roof", {"type": "roof", "form": "gable", "width": GW, "length": r4(FZ - 1.5 - L / 2 + 0.2), "pitch": PITCH, "overhang": 0,
                     "at": [[0, r4(YW), r4((FZ - 1.5 + L / 2 - 0.2) / 2), 0]],
                     "_about": "the great roof carried on between the towers to the front's gable"})

# ---- THE DORMERS: rows of little shed dormers (Schleppgauben) up the great roof's long sides
DW, DD, DH, DP = 1.1, 2.0, 1.0, 18          # wide, deep (into the roof), the front's height, their roofs' pitch
dorm = []
for y, n in ((36.6, 13), (41.4, 13), (46.2, 11), (51.0, 7)):
    rf = EAVE - (y - WALLTOP) / TP          # the front's distance from the axis
    for sx in (1, -1):
        for k in range(n):
            z = (L / 2 - 3.0) - k * (L - 6.0) / (n - 1) + (0.9 if (n % 2) else 0)
            dorm.append([r4(sx * (rf - DD / 2)), r4(y - 0.15), r4(z), 0 if sx > 0 else PI])
add("dormers", {"type": "prism", "plan": {"rect": [DD, DW]}, "height": r4(DH + 0.15 + DD / 2 * math.tan(math.radians(DP))),
                "slope": [r4(-math.tan(math.radians(DP))), 0], "at": dorm,
                "_about": "the rows of shed dormers, their fronts standing out of the great roof, their roofs dragged out of it"})

doc = {"name": "Frauenkirche (Munich)",
       "_about": "THE FRAUENKIRCHE, Munich (1468-88; the caps 1525), from components: a late-Gothic BRICK HALL CHURCH -- nave and aisles one height, rib-vaulted at 31m on two rows of slender pillars, the buttresses drawn inside as wall piers with chapels between them, a tall lancet in every bay of the plain outer wall, the polygonal choir -- under ONE steep roof of plain tiles with rows of shed dormers, a pent roof round the wall-head under a light frieze; the side portals in ogee frames; the two WEST TOWERS, square and banded by friezes to 58m, then octagons, each under its WELSCHE HAUBE (`welsche-haube`) to 98.5m, the south one climbed by its `tower-stair`; between them the porch with the main portal and the recessed front under the great gable.",
       "params": {"detail": 4}, "base": {"height": BASE, "steps": 1, "stepOut": 0.4, "margin": 3}, "railing": {"type": "stone"},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/frauenkirche-munich.json"), "w").write(json.dumps(doc, indent=2) + "\n")

# ---- THE FINISH: red brick in monk bond, light friezes, the plain-tile roof, green copper caps, white inside
fin = {"name": "Frauenkirche (Munich)", "building": "architecture/frauenkirche-munich",
       "_about": "The Frauenkirche: red-brown brick in monk bond, the towers banded by light friezes of blind tracery and one more under the eave; the great roof in red plain tiles (Biberschwanz), the pent roof and the dormers too; the Welsche Hauben in green copper with gilt balls; the clocks' gilt dials; light leaded glass, coloured in the choir and the west window; inside, white plaster with ochre ribs over a floor of green-grey and red diamonds.",
       "stone": {"color": "#8c4a35", "accent": "#a39686", "pat": "brick"},
       "rules": [
           {"parts": "kind:glass", "within": [-30, -70, 30, r4(-L / 2)], "pattern": "painted/stained glass", "palette": "stained", "_about": "the choir's coloured windows"},
           {"parts": "west front glass", "pattern": "painted/stained glass", "palette": "stained", "_about": "and the west window's"},
           {"parts": "kind:glass", "pattern": "glass/quarries", "palette": "grisaille", "_about": "the rest light, in leaded quarries (only partly coloured)"},
           {"parts": ["haubes/ball", "haubes/cross", "clocks/dial", "kind:marks", "kind:hands"], "pattern": "roofs/gold leaf", "palette": "gold", "_about": "the gilt balls and crosses; the clocks' gilt rims, marks and hands"},
           {"parts": "clocks/ring", "color": "#1f2a3c", "accent": "#28344a", "pat": "plaster", "_about": "the clocks' dark blue faces"},
           {"parts": ["haubes", "broaches"], "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the caps and the broaches in green copper, standing seams"},
           {"parts": ["south tower 3", "north tower 3"], "surface": "floor", "above": r4(SQ - 0.5), "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the ledges round the octagons' feet, copper-clad"},
           {"parts": ["church/high roof", "church/pent roof", "narthex roof", "dormers", "kind:roof"], "surface": ["roof", "floor"], "side": "out",
            "pattern": "roofs/beaver tail", "palette": "fired-clay", "_about": "plain tiles"},
           {"parts": "dormers", "surface": "wall", "color": "#4a3328", "accent": "#5a4032", "pat": "plaster", "_about": "the dormers' dark faces"},
           {"parts": ["south tower courses", "north tower courses", "porch courses"], "below": 1.1, "pattern": "stone/ashlar", "palette": "sandstone-grey", "_about": "the plinths"},
           {"parts": [f"{t} tower{n} courses" for t in ("south", "north") for n in ("", " 2", " 3")] + ["octagons courses", "porch courses"], "pattern": "stone/tracery frieze", "align": "part",
            "_about": "the friezes of blind tracery between the storeys"},
           {"parts": "church/aisle wall", "side": "out", "above": 31.2, "below": 32.4, "pattern": "stone/tracery frieze", "align": "above",
            "_about": "the frieze under the eave, over the pent roof"},
           {"parts": ["kind:moulding", "kind:wimperg"], "pattern": "stone/ashlar", "palette": "sandstone-grey", "_about": "the portal's stone frame and gable"},
           {"parts": ["church/high ribs", "church/aisle ribs"], "pattern": "stone/plaster", "palette": "plaster-ochre", "_about": "the vault ribs picked out in ochre"},
           {"surface": "floor", "side": "in", "pattern": "floors/checker diagonal", "palette": "munich-floor", "_about": "the floor's diamonds of green-grey and red stone"},
           {"surface": ["wall", "ceiling"], "side": "in", "pattern": "stone/plaster", "palette": "plaster-white", "_about": "white inside"},
           {"surface": "floor", "pattern": "floors/flagstones", "palette": "granite"},
           {"surface": ["wall", "ceiling", "roof"], "pattern": "stone/brick monk bond", "palette": "munich-brick"}]}
open(os.path.join(ROOT, "assets/finishes/frauenkirche-munich.json"), "w").write(json.dumps(fin, indent=2) + "\n")
print("towers", TX, TZ, FRONT, "walltop", WALLTOP, "ridge", round(RIDGE, 2), "YW", round(YW, 2), "dormers", len(dorm))
