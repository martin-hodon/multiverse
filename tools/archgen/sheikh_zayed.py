# THE SHEIKH ZAYED GRAND MOSQUE, Abu Dhabi (1996-2007): white marble on a raised platform -- the great SAHN, its floor
# a floral inlay of marble, closed on three sides by the RIWAQ (arcades under a row of small domes, their pools outside),
# the PRAYER HALL on the fourth, toward the qibla in the west-south-west; four MINARETS (107m) on the court's corners;
# eighty-two domes in all, the greatest 85m to its finial, every one a little bulbous and crowned in gold.
#   The plan is OpenStreetMap's, its axis (12 degrees off west) turned to run east-west: the sahn 110 x 150m between
#   the riwaq's piers, the hall behind its portico on the west, the entrance hall and its portal on the east.
#   The RIWAQ is components/riwaq (`domed-arcade` rows: pointed arcades, a dome on pendentives over every bay), its
#   west side left out where the hall's portico (an `arcade-walk`) faces the court.
#   The HALL is walls round flat roofs, a forest of columns inside, and three CROSSINGS cut through the roofs -- four
#   piers, pointed arches, pendentives, tympana closing the arches over the roofs -- each crowned by a `drum-dome` on
#   the onion section (bulge 1.08: the slight swell of the real domes): the main dome (32.8m across) on the axis, the
#   two 65m domes either side of it; over the hall's entrance and on its roofs, small domes on drums.
#   The MINARETS are components/omani-minaret (square, then octagonal, balconies, a lantern under a small dome).
#   Everything stands on the platform (PH), the flights up to it on three sides.
#   East is +x, south is +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2
r4 = lambda v: round(v, 4)

# the onion's height over its springing (profiles.js onion): the bulb R1 = bulge a about a centre on the axis, the neck
# R2 = neck a turning it up to the tip
def onion_h(a, bulge, neck):
    R1, R2 = a * bulge, a * neck
    return math.sqrt(R1 * R1 - a * a) + math.sqrt(R1 * R1 + 2 * R1 * R2)
BULGE, NECK = 1.08, .45
ON = {"profile": "onion", "bulge": BULGE, "neck": NECK}
def finial(name, x, y, z, h, about=None):
    """the gold finial on a crown: a spike, a ball, the crescent's stem"""
    d = {"type": "column", "radius": r4(h * .045), "height": h, "sides": 8, "taper": .3, "at": [[r4(x), r4(y), r4(z), 0]]}
    if about: d["_about"] = about
    add(name, d)
    add(name + " ball", {"type": "column", "radius": r4(h * .1), "height": r4(h * .14), "sides": 10, "taper": .5, "at": [[r4(x), r4(y + h * .4), r4(z), 0]]})
def domed(name, x, y, z, R, dt, H, n, about, fin):
    """a dome on a drum (components/drum-dome on the onion section), its finial on the crown"""
    add(name, comp("components/drum-dome", {"R": R, "dt": dt, "H": H, "n": n, "every": 1, "winW": r4(R * .22), "winSill": r4(H * .2),
                                            "winH": r4(H * .5), "profile": "onion", "bulge": BULGE, "neck": NECK, "domeT": r4(dt * .7)},
                   [[r4(x), r4(y), r4(z), 0]], build=["drum", "dome"], _about=about))
    finial(name + " finial", x, y + H + onion_h(R + dt, BULGE, NECK) - .15, z, fin)

# ---- the sahn and the riwaq ------------------------------------------------------------------------------------------
NX, NZ, B, BP = 11, 15, 10.0, 1.8            # the riwaq's bays along x and z (odd: a gate in the middle of each row), their pitch, the piers
HX, HZ = NX * B / 2, NZ * B / 2               # the court's pier lines: 55 and 75 from the middle
EX, EZ = HX + B + BP / 2, HZ + B + BP / 2     # the riwaq's outside: 65.9, 85.9
add("riwaq", comp("components/riwaq", {"nx": NX, "nz": NZ, "B": B, "p": BP, "sL": 0, "SP": 6.0, "ow": 5.4, "os": 5.7, "cw": 4.6, "cs": 5.1,
                                       "wW": 2.0, "wSill": 1.7, "wSpr": 4.6, "gW": 5.0, "gS": 5.6, "dk": .55, "dh": 1.1, "dt": .4, "cn": 12},
                  [[0, 0, 0, 0]], _about="the riwaq round the court on three sides: pointed arcades, a small dome over every bay, gates through the middle of its back walls"))

# ---- the prayer hall -------------------------------------------------------------------------------------------------
PD = 10.0                                    # the portico's depth
X1 = -EX - PD                                # the hall's front wall (east): -75.9
X0 = -149.0                                  # its back (west), the qibla wall
HW, HC = X1 - X0, (X0 + X1) / 2              # its depth, its middle
HL = 2 * EZ                                  # its length, north to south: the riwaq's
HH, HT, RS = 20.0, 2.0, .8                   # its walls' height and thickness, the roof slab
# (a row of pointed windows `ev` apart that fits its face; a door in its middle)
win = lambda ev, sp=12.0, ww=3.0: {"every": ev, "width": ww, "end": 4.0, "sill": 3.0, "springing": sp, "head": {"profile": "pointed", "spread": .5}}
withdoor = lambda ev, dw, ds: {**win(ev), "with": [{"at": 0, "width": dw, "sill": 0, "springing": ds, "head": {"profile": "pointed", "spread": .5}}]}
add("prayer hall", {"type": "enclosure", "plan": {"rect": [r4(HW), r4(HL)]}, "thickness": HT, "height": HH, "interior": True,
                    "faces": {"1": withdoor(14.4, 6.0, 9.0), "0": withdoor(12.0, 4.0, 6.0), "2": withdoor(12.0, 4.0, 6.0), "3": win(14.4)},
                    "at": [[r4(HC), 0, 0, 0]],
                    "_about": "the prayer hall's walls: its great door toward the court, a door at each end, pointed windows; the qibla wall to the west"})
# the crossings: four piers, the arches from pier to pier, pendentives, and tympana closing the arches over the roofs
CROSS = [("main", -120.0, 0.0, 32.8, 4.0, 18.0, 10.0, 1.2, 24, 8.0, "the main dome, 32.8m across, 85m to its finial: the largest of the 82"),
         ("north", -116.0, -46.0, 21.0, 3.0, 16.0, 10.0, .8, 16, 6.0, "the north of the two 65m domes either side of the main one"),
         ("south", -116.0, 46.0, 21.0, 3.0, 16.0, 10.0, .8, 16, 6.0, "the south of the two 65m domes")]
holes = []
for nm, cx, cz, S, PR, SPR, DH, DT, DN, FIN, about in CROSS:
    CT = SPR + S / 2                         # the pendentives' top: the drum's foot
    RO = S / 2 + PR                          # the crossing's square reaches this far from its middle
    holes.append((cx - RO, cz - RO, cx + RO, cz + RO))
    add(f"{nm} piers", {"type": "box", "width": PR, "length": PR, "height": r4(CT + .5),
                        "at": [[r4(cx + sx * (S / 2 + PR / 2)), 0, r4(cz + sz * (S / 2 + PR / 2)), 0] for sx in (-1, 1) for sz in (-1, 1)],
                        "_about": f"the {nm} crossing's four piers, rising over the roofs"})
    add(f"{nm} arches", {"type": "barrel", "width": S, "length": PR, "springing": SPR, "top": r4(CT + .5), "head": {"profile": "semicircular"},
                         "at": [[cx, 0, r4(cz - S / 2), 0], [cx, 0, r4(cz + S / 2 + PR), 0], [r4(cx - S / 2), 0, cz, Q], [r4(cx + S / 2 + PR), 0, cz, Q]]})
    add(f"{nm} pendentives", {"type": "pendentives", "span": S, "springing": SPR, "sides": DN, "at": [[cx, 0, cz, 0]],
                              "deck": {"thickness": .5, "out": PR}})
    TY = HH + RS
    add(f"{nm} tympana", {"type": "wall", "width": S, "height": r4(CT + .5 - TY), "thickness": 1.0,
                          "openings": {"pattern": "3", "width": 2.4, "gap": r4(S / 5), "sill": 1.5, "springing": r4(min(6.0, CT - TY - 4.0)),
                                       "head": {"profile": "pointed", "spread": .5}},
                          "at": [[cx, TY, r4(cz - RO + .5), 0], [cx, TY, r4(cz + RO - .5), math.pi], [r4(cx - RO + .5), TY, cz, -Q], [r4(cx + RO - .5), TY, cz, Q]],
                          "_about": f"the tympana closing the {nm} crossing's arches over the roofs, three windows in each"})
    parts[f"{nm} crossing"] = {"type": "interior", "plan": {"rect": [2 * RO, 2 * RO]}, "height": r4(CT + .5), "at": [[cx, 0, cz, 0]],
                               "_about": f"the {nm} crossing's space, on its tympana's middle, up over the roofs to the drum's foot"}
    domed(f"{nm} dome", cx, CT + .5, cz, S / 2, DT, DH, DN, about, FIN)

# the flat roofs round the crossings: the hall's top in strips, the crossings' squares left open
def tiles(x0, z0, x1, z1, holes):
    xs = sorted({x0, x1, *[c for h in holes for c in (h[0], h[2]) if x0 < c < x1]})
    zs = sorted({z0, z1, *[c for h in holes for c in (h[1], h[3]) if z0 < c < z1]})
    out = []
    for j in range(len(zs) - 1):
        run = None
        for i in range(len(xs) - 1):
            mx, mz = (xs[i] + xs[i + 1]) / 2, (zs[j] + zs[j + 1]) / 2
            free = not any(h[0] < mx < h[2] and h[1] < mz < h[3] for h in holes)
            if free and run is None: run = xs[i]
            if (not free or i == len(xs) - 2) and run is not None:
                end = xs[i + 1] if free else xs[i]
                out.append((run, zs[j], end, zs[j + 1])); run = None
    return out
roof = tiles(X0, -EZ, X1, EZ, holes)
for k, (a, b, c, d) in enumerate(roof):
    add(f"hall roof {k + 1}", {"flatRoof": True, "type": "box", "width": r4(c - a), "length": r4(d - b), "height": RS,
                               "at": [[r4((a + c) / 2), HH, r4((b + d) / 2), 0]]})
add("hall parapet", {"type": "box", "width": r4(HW), "length": .5, "height": 1.0,
                     "at": [[r4(HC), HH + RS, r4(sz * (EZ - .25)), 0] for sz in (-1, 1)], "_about": "the low parapet round the hall's roofs"})
add("hall parapet ends", {"type": "box", "width": .5, "length": r4(HL - 1.0), "height": 1.0, "at": [[r4(x), HH + RS, 0, 0] for x in (X0 + .25, X1 - .25)]})
# the columns inside: a grid under the roofs, none in the crossings
cols = []
for i in range(6):
    x = X0 + 6.0 + i * (HW - 12.0) / 5
    for j in range(15):
        z = -EZ + 6.0 + j * (HL - 12.0) / 14
        if any(h[0] - 1.5 < x < h[2] + 1.5 and h[1] - 1.5 < z < h[3] + 1.5 for h in holes): continue
        cols.append([r4(x), 0, r4(z), 0])
add("hall columns", {"type": "column", "radius": .9, "height": HH, "sides": 12, "at": cols,
                     "_about": "the hall's columns under its flat roofs, white marble"})
# the domes on the roofs: over the entrance, and rows of small ones
RY = HH + RS
domed("entrance hall dome", X1 - 6.0, RY, 0, 7.0, .6, 9.0, 16, "the dome over the hall's entrance, behind its great door", 4.0)
small = [(X1 - 6.0, z) for z in (-75, -63, -51, -39, -27, -15, 15, 27, 39, 51, 63, 75)] + \
        [(X0 + 6.0, z) for z in (-72, -60, -48, -36, -24, -12, 0, 12, 24, 36, 48, 60, 72)] + \
        [(-110.0, -26.0), (-110.0, 26.0), (-100.0, -72.0), (-100.0, 72.0), (-126.0, -72.0), (-126.0, 72.0)]
add("roof domes", comp("components/drum-dome", {"R": 3.0, "dt": .35, "H": 1.6, "n": 12, "every": 1, "winW": .6, "winSill": .4, "winH": .8,
                                                "profile": "onion", "bulge": BULGE, "neck": NECK, "domeT": .3},
                       [[r4(x), RY, r4(z), 0] for x, z in small], build=["drum", "dome"], _about="the small domes in rows on the hall's roofs"))
add("roof dome finials", {"type": "column", "radius": .09, "height": 1.6, "sides": 6, "taper": .3,
                          "at": [[r4(x), r4(RY + 1.6 + onion_h(3.35, BULGE, NECK) - .1), r4(z), 0] for x, z in small]})
# the portico along the hall's front, facing the court; its back the hall's own wall
add("portico", comp("components/arcade-walk", {"L": r4(HL), "D": PD, "H": 15.0, "t": 1.0, "bay": 7.2, "pw": 1.4, "spread": .5, "slab": .7},
                    [[r4(-EX - PD / 2), 0, 0, Q]], build=["front", "roof"],
                    _about="the hall's portico toward the court: tall pointed arches on piers along its whole front"))

# ---- the entrance: the hall through the riwaq's east gate, its dome, its portal ------------------------------------
EW, EL, EH = 16.0, 22.0, 14.0
EC = EX + EW / 2
add("entrance hall", {"type": "enclosure", "plan": {"rect": [EW, EL]}, "thickness": 1.4, "height": EH, "interior": True,
                      "faces": {"1": [{"at": 0, "width": 3.2, "sill": 0, "springing": 5.0, "head": {"profile": "pointed", "spread": .5}}],
                                "3": [{"at": 0, "width": 5.0, "sill": 0, "springing": 5.6, "head": {"profile": "pointed", "spread": .5}}]},
                      "at": [[r4(EC), 0, 0, 0]], "_about": "the entrance hall outside the riwaq's east gate"})
add("entrance roof", {"flatRoof": True, "type": "box", "width": EW, "length": EL, "height": .6, "at": [[r4(EC), EH, 0, 0]]})
domed("entrance dome", EC, EH + .6, 0, 6.4, .6, 9.0, 16, "the dome over the main entrance", 3.5)
add("entrance portal", comp("components/portal", {"W": 20.0, "Hh": 22.0, "D": 7.5, "w": 10.0, "s": 11.0, "spread": .5, "it": .7},
                           [[r4(EX + EW), 0, 0, Q]], _about="the main entrance's portal, on the east"))

# ---- the minarets on the court's corners --------------------------------------------------------------------------
MA = 9.0
add("minarets", comp("components/omani-minaret", {"h": 98.0, "a": MA, "hs": 36.0, "balconies": 3},
                     [[r4(sx * (EX + MA / 2 + .5)), 0, r4(sz * (EZ + MA / 2 + .5)), 0] for sx in (-1, 1) for sz in (-1, 1)],
                     _about="the four minarets, 107m: the square shaft, the octagon with three balconies, the lantern and its dome"))

# ---- the pools along the riwaq's outside ---------------------------------------------------------------------------
add("pools", {"type": "prism", "plan": {"rect": [46.0, 9.0]}, "height": .45, "at": [[r4(sx * 31.0), 0, r4(sz * (EZ + 15.0)), 0] for sx in (-1, 1) for sz in (-1, 1)],
              "_about": "the reflecting pools along the riwaq's north and south sides, either side of its gates"})
add("east pools", {"type": "prism", "plan": {"rect": [9.0, 56.0]}, "height": .45, "at": [[r4(EX + 24.0), 0, r4(sz * 46.0), 0] for sz in (-1, 1)],
                   "_about": "and either side of the main entrance"})

# ---- the platform everything stands on, and the flights up to it ------------------------------------------------
PH = 1.5
for d in parts.values():                    # (everything above was set out from the platform's top)
    for a in d.get("at", []): a[1] = r4(a[1] + PH)
PX0, PX1, PZ0, PZ1 = -157.0, 112.0, -114.0, 114.0
TX, TZ = 8, 7                               # in tiles, so that no one triangle of its top is vast
TW, TL = (PX1 - PX0) / TX, (PZ1 - PZ0) / TZ
add("platform", {"type": "box", "width": r4(TW), "length": r4(TL), "height": PH, "walked": True,
                 "at": [[r4(PX0 + TW * (i + .5)), 0, r4(PZ0 + TL * (j + .5)), 0] for i in range(TX) for j in range(TZ)],
                 "_about": "the raised platform of the whole mosque, its top the sahn's inlaid marble"})
build.remove("platform"); build.insert(0, "platform")   # (laid first: everything stands on it)
RISE, RUN = .15, .35
FL = round(PH / RISE) * RUN
add("east flight", {"type": "flight", "width": 20.0, "run": RUN, "rise": RISE, "top": PH, "landing": 0, "at": [[r4(PX1 + FL), 0, -10.0, math.pi]],
                    "_about": "the broad flight up to the platform before the main entrance"})
add("side flights", {"type": "flight", "width": 12.0, "run": RUN, "rise": RISE, "top": PH, "landing": 0,
                     "at": [[6.0, 0, r4(PZ1 + FL), Q], [-6.0, 0, r4(PZ0 - FL), -Q]], "_about": "and on the north and south"})

doc = {
    "name": "Sheikh Zayed Grand Mosque",
    "_about": "THE SHEIKH ZAYED GRAND MOSQUE, Abu Dhabi (1996-2007), in white marble on its platform: the sahn with its floral inlay, the "
              "`riwaq` of small domes round three sides and its pools, the prayer hall behind its portico (`arcade-walk`) -- walls, "
              "flat roofs on a forest of columns, three crossings of piers, arches and pendentives carrying the main dome and the two "
              "65m domes (`drum-dome` on the onion section), small domes on the roofs -- the entrance hall, its dome and `portal` on "
              "the east, and the four `omani-minaret`s on the court's corners. After OpenStreetMap, the axis turned to east-west. "
              "Generated by tools/archgen/sheikh_zayed.py -- edit the script for arithmetic changes. East is +x, south +z.",
    "params": {"detail": 4},
    "railing": {"type": "stone"},
    "build": build,
    "parts": parts,
}
out = os.path.join(ROOT, "assets", "architecture", "sheikh-zayed.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts")
