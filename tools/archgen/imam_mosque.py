# THE IMAM MOSQUE (Masjed-e Shah), Isfahan (1611-1630, Shah Abbas I; Ali Akbar Isfahani): the Safavid mosque on the
# south end of the Naqsh-e Jahan square, every surface of its court in haft-rangi tiles, cobalt and turquoise. The
# FOUR-IWAN plan: a court with an iwan in the middle of each side, two storeys of pointed niches between them; on the
# qibla side the great iwan's PISHTAQ (30m) flanked by two minarets (48m), and behind it the dome chamber under the
# double DOME (52m), its tiled onion swelling over a high drum; the winter prayer halls behind the side iwans, under
# their own domes; a MADRASA either side of the sanctuary round its own court. The ENTRANCE stands on the square,
# which runs north-south while Mecca lies to the south-west -- so its portal and the domed vestibule behind it are
# turned, the famous twist: the visitor turns some thirty degrees between the portal and the court.
#   The plan is OpenStreetMap's (the court, the sanctuary, the drum, the winter halls, the madrasa courts, the
#   entrance), its qibla axis turned to run toward -x, made symmetric about it. The court's sides are RANGES
#   (range.js) faced in two tiers of niches, broken where the iwans stand -- each iwan a `portal` set flush with the
#   court's face, its depth through the range. The dome chamber is a crossing as Sheikh Zayed's are (piers, arches,
#   pendentives, tympana over the roofs) under a `drum-dome` on the onion section; the minarets are `minaret`s with
#   one balcony and a kiosk (the `chhatri`) on top.
#   East is +x (toward the entrance), south is +z; the dome's axis at the origin. Numbers are worked here and written as
#   numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2
r4 = lambda v: round(v, 4)
POINTED = {"profile": "pointed", "spread": .5}

# the onion's height over its springing (profiles.js onion), as sheikh_zayed.py has it
def onion_h(a, bulge, neck):
    R1, R2 = a * bulge, a * neck
    return math.sqrt(R1 * R1 - a * a) + math.sqrt(R1 * R1 + 2 * R1 * R2)
def finial(name, x, y, z, h, about=None):
    """the gilt finial on a dome's crown: a spike and a ball"""
    add(name, {"type": "column", "radius": r4(h * .045), "height": h, "sides": 8, "taper": .3, "at": [[r4(x), r4(y), r4(z), 0]],
               **({"_about": about} if about else {})})
    add(name + " ball", {"type": "column", "radius": r4(h * .1), "height": r4(h * .14), "sides": 10, "taper": .5, "at": [[r4(x), r4(y + h * .4), r4(z), 0]]})
def door(at=0, w=3.2, s=4.5): return {"at": r4(at), "width": r4(w), "sill": 0, "springing": r4(s), "head": POINTED}
def iwan_door(w, it, s):
    """the door through a `portal`'s iwan (its own default), which the building behind must open to match"""
    return min(3.2, (w / 2 + it) * .5 - .25), s * .45
def side_away(path, c):
    """the `side` of a range whose OUT looks away from the point c (bandPoints: the right of a segment is (-e.z, e.x))"""
    (x0, z0), (x1, z1) = path[0], path[1]
    ex, ez = x1 - x0, z1 - z0
    return "right" if (-ez) * (c[0] - (x0 + x1) / 2) + ex * (c[1] - (z0 + z1) / 2) < 0 else "left"

# ---- the sanctuary: the hall, the dome chamber in it, the great dome ------------------------------------------------
HX, HZ, HH, HT, RS = 19.0, 45.5, 14.0, 2.0, .6       # the hall: x -19..19, z -45.5..45.5, its walls' height and thickness, its roof slab
S, PR, SPR = 24.0, 3.0, 10.0                         # the chamber: its span between the piers, the piers, the arches' springing
CT, RO = SPR + S / 2, S / 2 + PR                     # the pendentives' top (the drum's foot), the chamber's reach from the axis
QW, QH, QD, Qw, Qs, Qit = 30.0, 30.0, 8.0, 14.0, 14.0, .8   # the qibla iwan's pishtaq: width, height, depth; its arch
qd, qs = iwan_door(Qw, Qit, Qs)
add("sanctuary", {"type": "enclosure", "plan": {"rect": [2 * HX, 2 * HZ]}, "thickness": HT, "height": HH, "interior": True, "glass": False,
                  "faces": {"1": [door(0, qd, qs)],
                            "3": {"every": 7.0, "width": 1.6, "end": 4.0, "sill": 8.0, "springing": 10.5, "head": POINTED}},
                  "at": [[0, 0, 0, 0]],
                  "_about": "the sanctuary: the dome chamber and the prayer halls either side of it under flat roofs; the door from the qibla iwan, a row of small windows high in the qibla wall"})
add("chamber piers", {"type": "box", "width": PR, "length": PR, "height": r4(CT + .5),
                      "at": [[r4(sx * (S / 2 + PR / 2)), 0, r4(sz * (S / 2 + PR / 2)), 0] for sx in (-1, 1) for sz in (-1, 1)],
                      "_about": "the dome chamber's four piers, rising over the roofs"})
add("chamber arches", {"type": "barrel", "width": S, "length": PR, "springing": SPR, "top": r4(CT + .5), "head": {"profile": "semicircular"},
                       "at": [[0, 0, r4(-S / 2), 0], [0, 0, r4(S / 2 + PR), 0], [r4(-S / 2), 0, 0, Q], [r4(S / 2 + PR), 0, 0, Q]]})
add("chamber pendentives", {"type": "pendentives", "span": S, "springing": SPR, "sides": 16, "at": [[0, 0, 0, 0]], "deck": {"thickness": .5, "out": PR}})
TY = HH + RS
add("chamber tympana", {"type": "wall", "width": S, "height": r4(CT + .5 - TY), "thickness": 1.0,
                        "openings": {"pattern": "3", "width": 1.8, "gap": 5.0, "sill": 1.2, "springing": 3.6, "head": POINTED},
                        "at": [[0, TY, r4(-RO + .5), 0], [0, TY, r4(RO - .5), math.pi], [r4(-RO + .5), TY, 0, -Q], [r4(RO - .5), TY, 0, Q]],
                        "_about": "the walls closing the chamber's arches over the roofs, three windows in each"})
parts["chamber"] = {"type": "interior", "plan": {"rect": [2 * RO, 2 * RO]}, "height": r4(CT + .5), "at": [[0, 0, 0, 0]],
                    "_about": "the dome chamber, up over the roofs to the drum's foot"}
DR, DT, DH, BULGE, NECK = S / 2, 1.6, 7.0, 1.06, .32
add("great dome", comp("components/drum-dome", {"R": DR, "dt": DT, "H": DH, "n": 16, "every": 1, "winW": 1.6, "winSill": 1.6, "winH": 3.4,
                                                "profile": "onion", "bulge": BULGE, "neck": NECK, "domeT": 1.0},
                       [[0, r4(CT + .5), 0, 0]], build=["drum", "dome"],
                       _about="the great dome on its high drum, sixteen windows round it: the tiled onion over the chamber, 52m to its crown"))
finial("great dome finial", 0, CT + .5 + DH + onion_h(DR + DT, BULGE, NECK) - .2, 0, 4.0, "the gilt finial on the great dome")
# the flat roofs round the chamber: the hall's top in strips, the chamber's square left open (as sheikh_zayed.py)
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
                out.append((run, zs[j], xs[i + 1] if free else xs[i], zs[j + 1])); run = None
    return out
for k, (a, b, c, d) in enumerate(tiles(-HX, -HZ, HX, HZ, [(-RO, -RO, RO, RO)])):
    add(f"sanctuary roof {k + 1}", {"flatRoof": True, "type": "box", "width": r4(c - a), "length": r4(d - b), "height": RS,
                                    "at": [[r4((a + c) / 2), HH, r4((b + d) / 2), 0]]})
# the prayer halls either side of the chamber: piers carrying their roofs
add("sanctuary piers", {"type": "box", "width": 1.6, "length": 1.6, "height": HH,
                        "at": [[r4(x), 0, r4(sz * z), 0] for x in (-9.0, 0.0, 9.0) for z in (22.0, 30.0, 38.0) for sz in (-1, 1)],
                        "_about": "the piers of the prayer halls either side of the dome chamber"})
add("qibla iwan", comp("components/portal", {"W": QW, "Hh": QH, "D": QD, "w": Qw, "s": Qs, "spread": .5, "it": Qit},
                       [[HX, 0, 0, Q]], _about="the qibla iwan's pishtaq on the court's west side, 30m: the great arch, the half dome of muqarnas, the door into the dome chamber"))
# the two minarets beside it, on the sanctuary's roof
MR = 2.4
add("qibla minarets", comp("components/minaret", {"h": 27.0, "r": MR, "balconies": 1, "bw": 1.1},
                           [[r4(HX - MR - .5), HH + RS, r4(sz * (QW / 2 + MR + .3)), 0] for sz in (-1, 1)],
                           _about="the two minarets beside the qibla iwan, standing on the sanctuary's roof: a balcony on its muqarnas and a kiosk, 48m"))

# ---- the court: four sides of two-storey niches, an iwan in the middle of each --------------------------------------
CX0, CX1, CZ = HX + QD, 83.0, 37.5                   # the court's faces: x 27 (the qibla iwan's front) .. 83, z -37.5 .. 37.5
CW, CH = 8.0, 13.0                                   # the ranges round it: their depth and height
CC = ((CX0 + CX1) / 2, 0.0)                          # the court's middle
SW_, SH_, SD_, Sw_, Ss_, Sit_ = 24.0, 19.0, CW, 11.0, 9.0, .7    # the three other iwans' pishtaqs
sd, ss = iwan_door(Sw_, Sit_, Ss_)
niche = lambda sill, spr: {"every": 5.0, "width": 3.0, "end": 1.2, "sill": sill, "springing": spr, "head": POINTED}
COURT_FACE = {"in": [{"h": 6.5, "openings": niche(0, 3.8)}, {"openings": niche(1.0, 4.0)}]}
m = CW / 2
xi, xo, zo = CX0 - m, CX1 + m, CZ + m                 # the ranges' middle lines
a0, a1, b0 = CC[0] - SW_ / 2, CC[0] + SW_ / 2, SW_ / 2  # where the side iwans and the east iwan break them
ARC = [[[xi, -QW / 2], [xi, -zo], [a0, -zo]],
       [[a1, -zo], [xo, -zo], [xo, -b0]],
       [[xo, b0], [xo, zo], [a1, zo]],
       [[a0, zo], [xi, zo], [xi, QW / 2]]]
for k, path in enumerate(ARC):
    # (out: away from the court -- so `in` is the court's face; the faces are fitted rows, every segment a different length)
    add(f"court arcade {k + 1}", {"type": "range", "path": [[r4(x), r4(z)] for x, z in path], "width": CW, "height": CH, "thickness": .9,
                                  "side": side_away(path, CC), "faces": COURT_FACE, "walk": {"t": .5, "over": .2},
                                  "parapet": {"breast": 1.0, "merlon": 0, "t": .4},
                                  "_about": "two storeys of pointed niches round the court, broken where the iwans stand"})
add("south iwan", comp("components/portal", {"W": SW_, "Hh": SH_, "D": SD_, "w": Sw_, "s": Ss_, "spread": .5, "it": Sit_},
                       [[CC[0], 0, r4(CZ + SD_), math.pi]], _about="the iwan on the court's south side, into the winter hall behind it"))
add("north iwan", comp("components/portal", {"W": SW_, "Hh": SH_, "D": SD_, "w": Sw_, "s": Ss_, "spread": .5, "it": Sit_},
                       [[CC[0], 0, r4(-CZ - SD_), 0]], _about="the iwan on the court's north side, into the winter hall behind it"))
add("east iwan", comp("components/portal", {"W": SW_, "Hh": SH_, "D": SD_, "w": Sw_, "s": Ss_, "spread": .5, "it": Sit_},
                      [[r4(CX1 + SD_), 0, 0, -Q]], _about="the iwan on the court's east side, facing the qibla iwan: the way in from the vestibule"))
add("pool", {"type": "prism", "plan": {"rect": [10.0, 16.0]}, "height": .45, "at": [[CC[0], 0, 0, 0]],
             "_about": "the pool for ablutions in the middle of the court"})

# ---- the winter halls behind the side iwans, under their domes --------------------------------------------------------
WX0, WX1, WZ0, WZ1 = 41.0, 69.0, CZ + CW, 76.0       # x 41..69, |z| 45.5..76
WH = 12.0
WC = ((WX0 + WX1) / 2, (WZ0 + WZ1) / 2)
win_out = {"every": 6.0, "width": 1.8, "end": 3.0, "sill": 2.5, "springing": 6.0, "head": POINTED}
for nm, sz in (("north", -1), ("south", 1)):
    toward_court, away = ("0", "2") if sz < 0 else ("2", "0")
    add(f"{nm} winter hall", {"type": "enclosure", "plan": {"rect": [WX1 - WX0, WZ1 - WZ0]}, "thickness": 1.5, "height": WH, "interior": True, "glass": False,
                              "faces": {toward_court: [door(0, sd, ss)], away: win_out, "3": [door(0, 3.0, 4.0)]},
                              "at": [[WC[0], 0, r4(sz * WC[1]), 0]],
                              "_about": f"the {nm} winter prayer hall behind its iwan: a door from the iwan, one from the madrasa's court, windows outward (its east wall against the corner block)"})
    add(f"{nm} winter hall roof", {"flatRoof": True, "type": "box", "width": WX1 - WX0, "length": WZ1 - WZ0, "height": .6,
                                   "at": [[WC[0], WH, r4(sz * WC[1]), 0]]})
    add(f"{nm} winter hall piers", {"type": "box", "width": 1.4, "length": 1.4, "height": WH,
                                    "at": [[x, 0, r4(sz * z), 0] for x in (48.0, 62.0) for z in (53.0, 68.5)]})
    add(f"{nm} winter hall dome", comp("components/drum-dome", {"R": 7.0, "dt": .6, "H": 2.0, "n": 16, "every": 2, "winW": .9, "winSill": .4, "winH": 1.1,
                                                                "profile": "pointed", "spread": .3, "domeT": .5},
                                       [[WC[0], WH + .6, r4(sz * WC[1]), 0]], build=["drum", "dome"],
                                       _about=f"the low dome over the {nm} winter hall"))

# ---- the madrasas either side of the sanctuary, round their own courts ------------------------------------------------
MX0, MX1 = -HX, WX0                                  # x -19..41, |z| 45.5..76
MW, MH = 6.0, 9.0
cell = lambda sill, spr: {"every": 3.6, "width": 1.8, "end": 1.0, "sill": sill, "springing": spr, "head": POINTED}
mwin = [{"h": 4.5}, {"openings": {"every": 3.6, "width": .9, "end": 1.5, "sill": 1.6, "springing": 2.6, "head": POINTED}}]
for nm, sz in (("north", -1), ("south", 1)):
    zi, zo2 = sz * (WZ0 + MW / 2), sz * (WZ1 - MW / 2)
    xa, xb = MX0 + MW / 2, MX1 - MW / 2
    gap = sz * (WC[1])                               # the way through to the winter hall: a gap in the ring on its east side
    path = [[xb, r4(gap - sz * 4.5)], [xb, zi], [xa, zi], [xa, zo2], [xb, zo2], [xb, r4(gap + sz * 4.5)]]
    c = ((xa + xb) / 2, (zi + zo2) / 2)
    add(f"{nm} madrasa", {"type": "range", "path": [[r4(x), r4(z)] for x, z in path], "width": MW, "height": MH, "thickness": .8,
                          "side": side_away(path, c),
                          "faces": {"in": [{"h": 4.5, "openings": cell(0, 2.4)}, {"openings": cell(.8, 2.6)}], "out:2": mwin, "out:3": mwin},
                          "walk": {"t": .4, "over": .2}, "parapet": {"breast": .9, "merlon": 0, "t": .35},
                          "_about": f"the {nm} madrasa: two storeys of students' cells round its court, open on the east to the winter hall"})
    add(f"{nm} corner block", {"type": "enclosure", "plan": {"rect": [xo + m - WX1, WZ1 - WZ0]}, "thickness": 1.0, "height": MH, "interior": True, "glass": False,
                               "faces": {("2" if sz < 0 else "0"): {"every": 5.0, "width": 1.2, "end": 2.0, "sill": 4.0, "springing": 6.0, "head": POINTED}},
                               "at": [[r4((WX1 + xo + m) / 2), 0, r4(sz * WC[1]), 0]],
                               "_about": f"the {nm}-east corner: service rooms behind the court"})
    add(f"{nm} corner block roof", {"flatRoof": True, "type": "box", "width": r4(xo + m - WX1), "length": WZ1 - WZ0, "height": .5,
                                    "at": [[r4((WX1 + xo + m) / 2), MH, r4(sz * WC[1]), 0]]})

# ---- the entrance: the portal on the square and the domed vestibule behind it, turned to the square -----------------
# the square's axis in this frame (OSM: the portal faces north; the qibla axis is 56.7 degrees from the square's)
YAW = math.atan2(.836, -.549)                         # the portal faces (0.836, -0.549): yaw 123.3 degrees
nx, nz = math.sin(YAW), math.cos(YAW)
VS = 16.0                                            # the vestibule, square, its back door looking at the east iwan's
EX = CX1 + SD_                                       # the east iwan's back (x 91), its door at z 0
back = (EX + 5.0, 5.0 * nz / nx)                     # the vestibule's back face 5m out: the line from its door hits the iwan's
vc = (back[0] + nx * VS / 2, back[1] + nz * VS / 2)
vf = (vc[0] + nx * VS / 2, vc[1] + nz * VS / 2)
EW, EH_, ED, Ew, Es, Eit = 26.0, 27.0, 9.0, 12.0, 13.0, .7
ed, es = iwan_door(Ew, Eit, Es)
add("vestibule", {"type": "enclosure", "plan": {"rect": [VS, VS]}, "thickness": 1.6, "height": 14.0, "interior": True, "glass": False,
                  "faces": {"0": [door(0, ed, es)], "2": [door(0, 3.2, 4.5)],
                            "1": [{"at": 0, "width": 2.0, "sill": 7.0, "springing": 9.5, "head": POINTED}],
                            "3": [{"at": 0, "width": 2.0, "sill": 7.0, "springing": 9.5, "head": POINTED}]},
                  "at": [[r4(vc[0]), 0, r4(vc[1]), r4(YAW)]],
                  "_about": "the domed vestibule behind the portal, square to the square: its back door turned toward the court's east iwan"})
add("vestibule roof", {"flatRoof": True, "type": "box", "width": VS, "length": VS, "height": .6, "at": [[r4(vc[0]), 14.0, r4(vc[1]), r4(YAW)]]})
add("vestibule dome", comp("components/drum-dome", {"R": 5.5, "dt": .6, "H": 2.4, "n": 16, "every": 2, "winW": .8, "winSill": .4, "winH": 1.3,
                                                    "profile": "onion", "bulge": BULGE, "neck": NECK, "domeT": .5},
                           [[r4(vc[0]), 14.6, r4(vc[1]), r4(YAW)]], build=["drum", "dome"], _about="the vestibule's dome"))
finial("vestibule dome finial", vc[0], 14.6 + 2.4 + onion_h(6.1, BULGE, NECK) - .1, vc[1], 1.8)
add("entrance portal", comp("components/portal", {"W": EW, "Hh": EH_, "D": ED, "w": Ew, "s": Es, "spread": .5, "it": Eit},
                            [[r4(vf[0]), 0, r4(vf[1]), r4(YAW)]],
                            _about="the entrance portal on the square, 27m: its half dome of muqarnas over the door, turned square to the square"))
ER = 2.2
sx_, sz_ = nz, -nx                                   # (across the portal)
add("entrance minarets", comp("components/minaret", {"h": 35.0, "r": ER, "balconies": 1, "bw": 1.0},
                              [[r4(vf[0] + k * sx_ * (VS / 2 + ER + .4) - nx * (ER + .4)), 0, r4(vf[1] + k * sz_ * (VS / 2 + ER + .4) - nz * (ER + .4)), 0]
                               for k in (-1, 1)],
                              _about="the two minarets behind the entrance portal's corners, 42m"))

# ---- the platform everything stands on: one riser, paved -- the court's flags, the halls' floors ----------------------
PH = .15
for d in parts.values():                    # (everything above was set out from the platform's top)
    for a in d.get("at", []):
        if isinstance(a, list): a[1] = r4(a[1] + PH)
PX0, PX1, PZ = -HX, EX, WZ1                          # the main block: x -19..91, z -76..76
TX, TZ = 5, 8                                        # in tiles, so that no one triangle of its top is vast
TW, TL = (PX1 - PX0) / TX, 2 * PZ / TZ
add("platform", {"type": "box", "width": r4(TW), "length": r4(TL), "height": PH, "walked": True,
                 "at": [[r4(PX0 + TW * (i + .5)), 0, r4(-PZ + TL * (j + .5)), 0] for i in range(TX) for j in range(TZ)],
                 "_about": "the low platform of the whole mosque: the court's paving, the halls' floors"})
# and under the entrance: the portal's and vestibule's band, from its front back to the main block's edge
front = (vf[0] + nx * ED, vf[1] + nz * ED)
c1, c2 = [(front[0] + k * sx_ * EW / 2, front[1] + k * sz_ * EW / 2) for k in (-1, 1)]
meet = lambda c: (EX, c[1] - (c[0] - EX) / nx * nz)  # (back along the band's side, -n, to x = 91)
quad = [meet(c1), c1, c2, meet(c2)]
add("entrance platform", {"type": "prism", "plan": {"points": [[r4(x), r4(z)] for x, z in quad]}, "height": PH, "walked": True, "at": [[0, 0, 0, 0]],
                          "_about": "the platform under the entrance portal and the vestibule, turned with them"})
for nm in ("platform", "entrance platform"): build.remove(nm)
build[:0] = ["platform", "entrance platform"]       # (laid first: everything stands on them)

doc = {
    "name": "Imam Mosque",
    "_about": "THE IMAM MOSQUE (Masjed-e Shah), Isfahan (1611-1630), in haft-rangi tiles: the four-iwan court -- `range`s of "
              "two-storey niches broken by the iwans' `portal`s -- the qibla iwan's 30m pishtaq and its two `minaret`s, the dome "
              "chamber (piers, arches, pendentives, tympana) under the great `drum-dome` on the onion section, 52m; the prayer "
              "halls either side of it; the winter halls behind the side iwans under their low domes; the madrasas round their "
              "courts; the entrance portal and domed vestibule turned to the square, its two minarets. After OpenStreetMap, the "
              "qibla axis turned to run west. Generated by tools/archgen/imam_mosque.py -- edit the script for arithmetic "
              "changes. East is +x, south +z.",
    "params": {"detail": 4},
    "railing": {"type": "stone"},
    "build": build,
    "parts": parts,
}
out = os.path.join(ROOT, "assets", "architecture", "imam-mosque.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts")
