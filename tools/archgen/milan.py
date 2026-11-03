# MILAN CATHEDRAL (Duomo di Milano, 1386-1965; the fabric and its forest of spires), 158m long, 68m across the front, the
# transept 93m: five aisles west of the crossing stepping down -- nave vault 45m, inner aisles 28m, outer 18m -- three
# east of it round the apse (the outer aisles' place there the sacristies'), a transept with an aisle down each side of its
# arms, two tiers of flying buttresses and a different pinnacle by turns down both flanks; the front a broken gable to
# 56.5m between six great buttresses, none of the three pairs alike; the three great apse windows; the tiburio on the
# crossing, four guglie at its corners, its openwork spire and the gilded Madonnina at 108.5m. Spiral turrets up to the
# aisles' flat roofs, which are walked on (a stair between the two terraces).
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
P = {"detail": 4, "bays": 14, "bayLen": 9.35, "naveW": 16.4, "aisleW": 9.6, "pierT": 2.8, "aisleT": 2.0,
     "naveL": "bays * bayLen", "spring": 20.0, "arcadeH": 27.0, "clearH": 32.0, "aisleRise": 2.4,
     "crown": "spring + (bayLen - pierT) / 2 * 1.7321", "aisleTop": "crown + aisleRise + 0.6", "naveTop": "clearH + naveW / 2 * 1.7321 + 1.2",
     "innerX": "naveW / 2 + pierT + aisleW", "outerX": "innerX + aisleT + aisleW", "wallX": "outerX + aisleT",
     "outerSpring": 11.0, "outerTop": "outerSpring + aisleW / 2 * 1.7321 + 0.8", "outerWallH": "outerTop + 1.2",
     "innerWallH": "aisleTop + 1.8", "crossZ": "0 - naveL / 2 + 4 * bayLen",
     "_innerX": "the inner aisles' outer edge: the arcade between the two aisles on each side stands there",
     "_crossZ": "the crossing's middle, four bays from the apse: the choir's two, the transept's east aisle, half the crossing"}
# THE NAVE, ITS AISLES AND THE TRANSEPT ACROSS THEM (2026-10-27: were the `basilica` component's arcade, clerestory and
# vaults, with a low transept arm off each outer aisle -- the crossing vaulted like any other bay and the tiburio shut
# off over it. Now the transept crosses the whole body at the nave's height in the two bays either side of crossZ, the
# aisles passing through its walls, and the crossing opens up into the tiburio's dome.)
BAYS, BAY = P["bays"], P["bayLen"]; NAVE_L = BAYS * BAY
CROSS_BAYS = (3, 4)                           # (the bays either side of crossZ, counted from the east end: the transept's nave; 2 and 5 its aisles, 0 and 1 the choir)
NAVE_BAYS = [i for i in range(BAYS) if i not in CROSS_BAYS]
zc = lambda i: -NAVE_L / 2 + (i + .5) * BAY   # (bay i's middle)
HALF_B = P["naveW"] / 2 + P["pierT"]          # the nave walls' outer faces
INNER_X = HALF_B + P["aisleW"]
WALL_X = INNER_X + 2 * P["aisleT"] + P["aisleW"]
CROSS_Z = -NAVE_L / 2 + 4 * BAY
LINE = lambda k: -NAVE_L / 2 + k * BAY          # (bay line k)
TZ0, TZ1 = CROSS_Z - BAY - 1, CROSS_Z + BAY + 1   # the transept walls' outer faces: 2m walls on the bay lines either side of it
TR_IN = TZ1 - TZ0 - 4                             # (17m between them)
ARM_X = WALL_X + 12.5                             # an arm's end wall, its outer face (the transept 93m across)
POINTED = {"profile": "pointed", "spread": 1}
FLANK_WINDOW = {"width": 5.0, "sill": 3.0, "springing": 12.0, "head": {"profile": "pointed", "spread": 1.2}, "tracery": True}
UP_WINDOW = {"width": 3.0, "sill": 1.4, "springing": 3.4, "head": POINTED, "tracery": 2}   # (the inner aisles' own windows, over the outer aisles' terrace)
CROWN_W = BAY - 1.6                               # (a parapet's length between the buttresses on the bay lines)
def cresting(name, x, y, zs, h=1.3, every=2, **kw):
    # a run of openwork parapet down both flanks, on the line x: one bay's length repeated (pinnacle.js)
    add(name, {"type": "cresting", "run": [[-round(CROWN_W / 2, 3), 0], [round(CROWN_W / 2, 3), 0]], "h": h, "panel": 1.9, "t": 0.25, "every": every,
               "spirelet": {"w": 0.22, "s": 0.8}, "at": [[f"{sx} * ({x})", y, round(z, 4), sx * 1.5707963] for sx in (1, -1) for z in zs], **kw})
def flank(name, x, z0, z1, tiers, y=0, **wall):
    # a stretch z0..z1 of a wall down both flanks on the line x: turned a quarter, as a flank's walls are (so it reaches
    # inward from its line), its openings given by their z -- `at` is from the wall's middle, along -z on the right
    # and +z on the left
    m = (z0 + z1) / 2
    for sx, nm in ((1, "right"), (-1, "left")):
        tt = [{**t, "openings": [{**{k: v for k, v in o.items() if k != "z"}, "at": round(-sx * (o["z"] - m), 4)} for o in t["openings"]]} for t in tiers]
        add(f"{name} {nm}", {"type": "wall", "width": round(z1 - z0, 4), **wall, "tiers": tt, "at": [[f"{sx} * ({x})", y, round(m, 4), f"{sx} * 1.5707963"]]})
# the nave's walls: the arcade into the inner aisles, broken off at the crossing (the transept opens there to the
# floor), and the clerestory over it, its window in every bay, and over the crossing the arch into the transept arm
ARCH = {"width": "bayLen - pierT", "sill": 0, "springing": "spring", "head": POINTED}
flank("nave arcade east", "naveW / 2 + pierT", -NAVE_L / 2, TZ0 + 2, [{"openings": [{"z": zc(i), **ARCH} for i in NAVE_BAYS if i < 3]}], height="arcadeH", thickness="pierT")
flank("nave arcade west", "naveW / 2 + pierT", TZ1 - 2, NAVE_L / 2, [{"openings": [{"z": zc(i), **ARCH} for i in NAVE_BAYS if i > 2]}],
      height="arcadeH", thickness="pierT")
flank("clerestory", "naveW / 2 + pierT", -NAVE_L / 2, NAVE_L / 2,
      [{"openings": [{"z": zc(i), "width": 3.4, "sill": 5.0, "springing": 9.5, "head": POINTED, "tracery": 2} for i in NAVE_BAYS] +
                    [{"z": CROSS_Z, "width": TR_IN, "sill": 0, "springing": "clearH - arcadeH", "head": POINTED, "glass": False}]}],
      y="arcadeH", height="naveTop - arcadeH", thickness="pierT")
add("nave vaults", {"type": "groin", "width": "naveW", "length": "bayLen", "springing": "clearH", "top": "naveTop", "clears": "crown",
                    "across": POINTED, "along": {"profile": "pointed", "spread": "((naveW / bayLen) * (naveW / bayLen) * 3 - 1) / 2"},
                    "at": [[0, 0, round(zc(i), 4), 0] for i in NAVE_BAYS],
                    "_about": "the nave's vault, bay by bay, but for the crossing's two"})
add("nave ribs", {"type": "ribs", "on": "nave vaults", "width": 0.45, "depth": 0.3, "wall": {"width": 0.6, "depth": 0.35}})
add("inner vaults", {"type": "groin", "width": "aisleW", "length": "bayLen", "springing": "crown", "top": "aisleTop", "clears": "crown",
                     "across": {"profile": "segmental", "rise": "aisleRise"}, "along": {"profile": "segmental", "rise": "aisleRise"},
                     "at": [[f"{sx} * (naveW / 2 + pierT + aisleW / 2)", 0, round(zc(i), 4), 0] for sx in (1, -1) for i in NAVE_BAYS]})
add("inner ribs", {"type": "ribs", "on": "inner vaults", "width": 0.35, "depth": 0.25})
# the arcade between the inner and outer aisles and the outer walls, each in two stretches either side of the transept
# (the stretches' end bays' arches drawn in a little, to leave a pier against the transept's walls). Over the outer
# terrace the arcade's wall goes on up as the inner aisles' own clerestory, a window a bay. East of the transept the
# outer aisles are the SACRISTIES, shut off from the choir aisles but for a door.
AISLE_ARCH = {"sill": 0, "springing": "outerSpring - 1", "head": POINTED}
SAC_DOOR = {"width": 2.4, "sill": 0, "springing": 3.2, "head": POINTED, "glass": False}
TIER = round(P["outerSpring"] + P["aisleW"] / 2 * 1.7321 + 0.8 + 1.2, 4)          # (the outer wall's height, outerWallH)
AL = lambda i: {"z": zc(i) + (0.5 if i == 5 else -0.5 if i == 2 else 0), "width": 6.5 if i in (2, 5) else "bayLen - aisleT", **AISLE_ARCH}
FL_BAY = BAYS - 2                                 # (the bay the stair between the terraces stands in, against this wall)
flank("aisle arcade east", "innerX + aisleT", -NAVE_L / 2, TZ0, [{"h": TIER, "openings": [{"z": zc(0), **SAC_DOOR}, {"z": zc(1), **SAC_DOOR}, AL(2)]},
                                                                 {"openings": [{"z": zc(i), **UP_WINDOW} for i in (0, 1, 2)]}], height="innerWallH", thickness="aisleT")
flank("aisle arcade west", "innerX + aisleT", TZ1, NAVE_L / 2, [{"h": TIER, "openings": [AL(i) for i in range(5, BAYS)]},
                                                                {"openings": [{"z": zc(i), **UP_WINDOW} for i in range(5, BAYS) if i != FL_BAY]}], height="innerWallH", thickness="aisleT")
# (the outer walls' bays beside the transept -- its aisles' -- are arches through into the arm's aisle)
ARM_ARCH = {"width": 6.5, "sill": 0, "springing": "outerSpring - 1", "head": POINTED, "glass": False}
flank("outer wall east", "wallX", -NAVE_L / 2, TZ0, [{"openings": [{"z": zc(0), **FLANK_WINDOW}, {"z": zc(1), **FLANK_WINDOW}, {"z": zc(2) - 0.5, **ARM_ARCH}]}], height="outerWallH", thickness="aisleT")
# (the westernmost bay's window narrower and west of the stair turret, between it and the facade)
flank("outer wall west", "wallX", TZ1, NAVE_L / 2, [{"openings": [{"z": zc(5) + 0.5, **ARM_ARCH}] + [{"z": zc(i), **FLANK_WINDOW} for i in range(6, BAYS - 1)]
                                                    + [{"z": NAVE_L / 2 - 2.4, **FLANK_WINDOW, "width": 2.3}]}], height="outerWallH", thickness="aisleT")
add("sacristy ends", {"type": "wall", "width": "wallX - innerX - aisleT", "height": "outerWallH", "thickness": 2.0,
                      "tiers": [{"openings": [{"at": 0, "width": 3.4, "sill": 4.0, "springing": 12.0, "head": {"profile": "pointed", "spread": 1.2}, "tracery": True}]}],
                      "at": [[f"{sx} * (wallX + innerX + aisleT) / 2", 0, "0 - naveL / 2 - 2", 3.14159265] for sx in (1, -1)],
                      "_about": "the sacristies' east ends: the outer aisles stop with the choir, the apse is the inner aisles' only"})
add("outer vaults", {"type": "groin", "width": "aisleW", "length": "bayLen", "springing": "outerSpring", "top": "outerTop",
                     "across": POINTED, "along": {"profile": "pointed", "spread": "((aisleW / bayLen) * (aisleW / bayLen) * 3 - 1) / 2"},
                     "at": [[f"{sx} * (innerX + aisleT + aisleW / 2)", 0, round(zc(i), 4), 0] for sx in (1, -1) for i in NAVE_BAYS if i < BAYS - 1],
                     "_about": "the outer aisles' vaults, all but the transept's bays and the westernmost: that one is the stair turret's, under a flat terrace"})
add("outer ribs", {"type": "ribs", "on": "outer vaults", "width": 0.35, "depth": 0.25})
# THE ROOFS ARE WALKED: the nave's a gable (broken off round the tiburio), but the aisles' two flat marble TERRACES
# stepping down either side -- the outer one at the outer wall's head (the turret comes up onto it, its west bay the
# turret's own terrace), the inner one at the inner arcade's, a short flight up between them; a parapet along every
# edge that drops. (East of the transept, over the first bay, they are roofs only: the transept stands between.)
# And the nave's own roof is walked too, the highest terrace: low (its marble slabs laid at some 15 degrees, as the
# transept's), reached by a stair up the clerestory from each inner terrace (below).
ROOF_PITCH = 15
add("nave roof", {"type": "roof", "form": "gable", "width": "naveW + 2 * pierT + 0.4", "length": round(NAVE_L / 2 - TZ1, 4), "pitch": ROOF_PITCH, "walked": True,
                  "at": [[0, "naveTop", round((TZ1 + NAVE_L / 2) / 2, 4), 0]]})
add("nave roof east", {"type": "roof", "form": "gable", "width": "naveW + 2 * pierT + 0.4", "length": round(TZ0 + NAVE_L / 2, 4), "pitch": ROOF_PITCH,
                       "at": [[0, "naveTop", round((TZ0 - NAVE_L / 2) / 2, 4), 0]]})
for nm, (z0, z1), walked in (("", (TZ1, NAVE_L / 2), True), (" east", (-NAVE_L / 2, TZ0), False)):
    add(f"inner aisle terraces{nm}", {**({"walked": True} if walked else {}), "type": "box", "width": "aisleW", "length": round(z1 - z0, 4), "height": 0.4,
        "at": [[f"{sx} * (naveW / 2 + pierT + aisleW / 2)", "innerWallH - 0.4", round((z0 + z1) / 2, 4), 0] for sx in (-1, 1)],
        **({"_about": "the inner aisles' roofs: flat, level with the inner arcade's head, against the clerestory"} if walked else {})})
for nm, (z0, z1), walked in (("", (TZ1, NAVE_L / 2 - BAY), True), (" east", (-NAVE_L / 2, TZ0), False)):
    add(f"outer aisle terraces{nm}", {**({"walked": True} if walked else {}), "type": "box", "width": "aisleW", "length": round(z1 - z0, 4), "height": 0.4,
        "at": [[f"{sx} * (innerX + aisleT + aisleW / 2)", "outerWallH - 0.4", round((z0 + z1) / 2, 4), 0] for sx in (-1, 1)],
        **({"_about": "the outer aisles' roofs, level with the outer wall's head (the west bay is the turret's terrace)"} if walked else {})})
for nm, (z0, z1) in (("", (TZ1, NAVE_L / 2)), (" east", (-NAVE_L / 2, TZ0))):
    add(f"outer parapets{nm}", {"type": "box", "width": 0.5, "length": round(z1 - z0, 4), "height": 1.1,
        "at": [[f"{sx} * (wallX - aisleT + 0.25)", "outerWallH", round((z0 + z1) / 2, 4), 0] for sx in (-1, 1)],
        **({"_about": "along the outer wall's head, the terrace's edge over the street"} if not nm else {})})
# the stair from the outer terrace up to the inner one, against the inner arcade in the bay east of the turret's: two
# flights and a landing (a straight one would need a bay and a half, and pass under a flyer's foot), rising east along the
# outer side and back west along the arcade's face; its head level with the arcade's, the way across onto the inner terrace
# (the parapet along that head left open there)
FL_N, FL_RUN, FL_W = 24, 0.27, 1.4
FL_Z = round(LINE(BAYS - 1) - 2.2, 4)
add("terrace stair right", {"type": "staircase", "flight": FL_N, "width": FL_W, "run": FL_RUN, "rise": "(innerWallH - outerWallH) / 48", "soffit": 0.3,
                            "landing": {"depth": FL_W, "width": 2 * FL_W, "shift": -FL_W / 2, "then": [{"flight": FL_N, "width": FL_W, "from": "back", "at": -FL_W / 2}]},
                            "place": [["innerX + aisleT + 2.1", "outerWallH", FL_Z, 1.5707963]],
                            "_about": "up from the outer terrace to the inner: two flights turning on a landing"})
add("terrace stair left", {"type": "staircase", "flight": FL_N, "width": FL_W, "run": FL_RUN, "rise": "(innerWallH - outerWallH) / 48", "soffit": 0.3,
                           "landing": {"depth": FL_W, "width": 2 * FL_W, "shift": FL_W / 2, "then": [{"flight": FL_N, "width": FL_W, "from": "back", "at": FL_W / 2}]},
                           "place": [["0 - innerX - aisleT - 2.1", "outerWallH", FL_Z, 1.5707963]]})
# the stair from each inner terrace up the clerestory's face to the nave roof's foot, 17m: three pairs of flights
# turning on a landing, each pair arriving on a landing over both (its middle on the flight by the wall: a third of it in
# the wall), from which the next
# pair starts -- all in one bay, between its flyers' feet, the flight by the wall coming down, the outer one going up
RF_N, RF_RUN, RF_W = 16, 0.27, 1.3
RF_Z = round(LINE(BAYS - 1) - 2.5, 4)          # (its foot's west end: the flights rise east from it, and come back)
# (each pair a part of its own: the railings ask whether stone stands beside a landing's edge, and a stair is no stone
#  to itself -- one part repeated up, its landing's edge over the next pair's foot was railed shut)
for sx, nm in ((1, "right"), (-1, "left")):
    for k in range(3):
        add(f"roof stair {nm} {k + 1}", {"type": "staircase", "flight": RF_N, "width": RF_W, "run": RF_RUN, "rise": "(naveTop - innerWallH) / 96", "soffit": 0.3,
            "landing": {"depth": RF_W, "width": 2 * RF_W, "shift": -sx * RF_W / 2,
                        "then": [{"flight": RF_N, "width": RF_W, "from": "back", "at": -sx * RF_W / 2, "landing": {"depth": RF_W, "width": 3 * RF_W}}]},
            "place": [[f"{sx} * (naveW / 2 + pierT + 0.1 + {RF_W * 1.5})", f"innerWallH + (naveTop - innerWallH) * {k} / 3", RF_Z, 1.5707963]],
            **({"_about": "up from the inner terrace to the nave roof: three pairs of flights against the clerestory"} if (sx, k) == (1, 0) else {})})
for k, (z0, z1) in enumerate(((-NAVE_L / 2, TZ0), (TZ1, FL_Z), (FL_Z + FL_W, NAVE_L / 2))):
    add(f"arcade parapets {k + 1}", {"type": "box", "width": 0.5, "length": round(z1 - z0, 4), "height": 1.1,
        "at": [[f"{sx} * (innerX + aisleT - 0.25)", "innerWallH", round((z0 + z1) / 2, 4), 0] for sx in (-1, 1)],
        **({"_about": "along the inner arcade's head, over the drop to the outer terrace: open where the stair arrives"} if k == 0 else {})})
# BUTTRESSES AND PINNACLES down both flanks, on every bay line but the crossing's three (its walls are its buttresses):
# a flying buttress from a pier against the outer wall (its back 10cm in: one mass with it) over the outer terrace to the
# inner arcade -- springing high enough off its pier to be walked under along the terrace -- and a second tier from a pier on
# the inner arcade over the inner terrace to the clerestory, where the nave vault pushes out. The pinnacles are no one
# kind (`pinnacle` parts, pinnacle.js): by turns down each flank a tall octagonal one with a statue and a square one with
# corner spirelets; the upper tier's, lighter, by turns the same, the other way about; the clerestory's plain.
FLANK_LINES = [k for k in range(BAYS) if k not in (3, 4, 5)]
PIN_A = {"type": "pinnacle", "w": 1.7, "sides": 8, "h": 3.4, "s": 7.5, "gablets": 1.1, "crockets": 3, "figure": 2.1}
PIN_B = {"type": "pinnacle", "w": 1.6, "sides": 4, "h": 4.4, "s": 6.0, "gablets": 0.9, "crockets": 2, "attendants": 0.42}
PIN_C = {"type": "pinnacle", "w": 1.2, "sides": 8, "h": 2.6, "s": 5.5, "gablets": 0.8, "crockets": 2, "figure": 1.7}
PIN_D = {"type": "pinnacle", "w": 1.2, "sides": 4, "h": 3.2, "s": 4.2, "gablets": 0.7, "attendants": 0.3}
def by_turns(name, kinds, spots, about=None):
    # spots [(k, x, y, z)]: each kind of pinnacle on every len(kinds)th bay line
    for i, kd in enumerate(kinds):
        add(f"{name} {i + 1}", {**kd, "at": [[x, y, z, 0] for k, x, y, z in spots if k % len(kinds) == i], **({"_about": about} if about and i == 0 else {})})
X0 = "wallX - 0.1"
# (a flyer's soffit is a quarter ellipse rising straight up off its pier, its back a straight line: the back must clear the
#  ellipse's bulge -- some 0.41 of its rise over the chord -- or the arch breaks up through it and the top goes round.
#  Each set here leaves 0.7-0.8m at the thinnest: the flat-backed strut every flyer of Milan's is)
fb = {"pierH": "outerWallH + 3.8", "pierD": 2.4, "span": f"{X0} - innerX - aisleT", "low": "outerWallH - 0.3", "high": "outerWallH + 7.7",
      "top0": "outerWallH + 3.7", "top1": "outerWallH + 11.7"}   # (its soffit 7.3m over the terrace by the arcade: the terrace stair's landing passes under)
add("flank buttresses", {"type": "component", "use": "components/flying-buttress", "params": fb, "build": ["pier", "flyer"],
                         "at": [[f"{sx} * ({X0})", 0, round(LINE(k), 4), 3.14159265 if sx > 0 else 0]
                                for sx in (1, -1) for k in FLANK_LINES],
                         "_about": "the lower tier: a pier against the outer wall, its flyer over the outer terrace to the inner arcade"})
by_turns("flank pinnacles", [PIN_A, PIN_B], [(k, f"{sx} * ({X0} + 1.2)", "outerWallH + 3.8", round(LINE(k), 4)) for sx in (1, -1) for k in FLANK_LINES],
         "on the lower piers, by turns: octagonal with its statue; square with four spirelets")
up = {"pierH": 8.0, "pierD": "aisleT", "pierW": 1.6, "span": "innerX - naveW / 2 - pierT", "low": 4.6, "high": 10.4, "top0": 7.8, "top1": 13.6}
add("clerestory flyers", {"type": "component", "use": "components/flying-buttress", "params": up, "build": ["pier", "flyer"],
                          "at": [[f"{sx} * innerX", "innerWallH", round(LINE(k), 4), 3.14159265 if sx > 0 else 0]
                                 for sx in (1, -1) for k in FLANK_LINES],
                          "_about": "the upper flyers: their piers on the inner arcade, over the inner terrace to the clerestory"})
by_turns("upper pinnacles", [PIN_D, PIN_C], [(k, f"{sx} * (innerX + aisleT / 2)", "innerWallH + 8", round(LINE(k), 4)) for sx in (1, -1) for k in FLANK_LINES])
add("clerestory pinnacles", {"type": "pinnacle", "w": 1.0, "h": 2.6, "s": 4.6, "crockets": 2,
                             "at": [[f"{sx} * (naveW / 2 + pierT / 2)", "naveTop", round(LINE(k), 4), 0] for sx in (1, -1) for k in FLANK_LINES]})
# THE LACE: an openwork cresting over each bay of the outer walls and the inner arcade, between the piers
cresting("outer cresting", "wallX", "outerWallH", [zc(i) for i in range(BAYS) if i not in (3, 4)], _about="the outer walls' lace, bay by bay between the buttresses")
cresting("inner cresting", "innerX + aisleT", "innerWallH", [zc(i) for i in range(BAYS) if i not in (2, 3, 4, 5, FL_BAY, FL_BAY + 1)])
# THE FRONT. Six great buttresses, five bays, and no two pairs of anything alike. A bay is its own wall with its own
# tiers: a portal under a pediment, a square-headed window under another (Pellegrini's, c.1600), and over them a great pointed
# window (19th c.) as high as its bay inside allows -- the nave's far the tallest, an inner aisle's under its vault, an outer
# aisle's under its terrace. Over the walls the top is a broken gable: a rake of its own for each bay, a step down at each
# buttress, to 56.5m at the middle, lace along the whole of it (`screen`, `cresting`). The buttresses set back twice on their way
# up, statues under canopies on their faces. Their pinnacles differ: by the nave a DOUBLED pair side by side, octagonal, the tallest; between the aisles one, ringed by spirelets; at the
# corners three, a heavy one in front and two lighter ones side by side behind it.
FRONT = NAVE_L / 2 + 2.4
BX = [P["naveW"] / 2 + P["pierT"] / 2, INNER_X + P["aisleT"] / 2, WALL_X - 1]   # the buttresses' lines from the axis: by the nave, between the aisles, at the corner
EDGE = [0, BX[0], BX[1], WALL_X]                                                # (the bays' walls meet behind them)
MID = [0, HALF_B + P["aisleW"] / 2, INNER_X + P["aisleT"] + P["aisleW"] / 2]    # the aisles' middles: where each bay's portal stands
RAKE = [(56.5, 49.0), (46.5, 39.0), (37.0, 30.5)]                               # the top line of each bay: at its inner end and its outer
WALL_TOP = ["naveTop", 30.0, 30.0]
pedi = lambda kind: {"head": "pediment", "pediment": kind, "band": 0.32, "depth": 0.3}
BAYS_F = [  # width, height of portal; tier heights; the square window (width, sill, springing); the pointed window (width, sill, springing)
    {"door": (4.4, 10.5), "low": 15.0, "win": (4.0, 2.2, 6.0), "mid": 8.0, "up": (6.0, 1.5, 14.0), "ped": ("segmental", "triangular")},
    {"door": (3.4, 8.0), "low": 13.0, "win": (2.8, 1.2, 4.4), "mid": 6.5, "up": (3.6, 0.8, 3.0), "ped": ("triangular", "segmental")},
    {"door": (3.0, 7.2), "low": 11.0, "win": (2.2, 0.9, 3.4), "mid": 5.5, "up": (2.4, 0.7, 1.7), "ped": ("segmental", "triangular")}]
def front_bay(b, sx, at):
    F, nm = BAYS_F[b], ["nave", "inner", "outer"][b]
    w = EDGE[b + 1] * 2 if b == 0 else EDGE[b + 1] - EDGE[b]
    c = 0 if b == 0 else sx * (EDGE[b] + EDGE[b + 1]) / 2
    off = round(sx * MID[b] - c, 4)
    add(f"front {nm}" + ("" if b == 0 else " right" if sx > 0 else " left"), {"type": "wall", "width": round(w, 4), "height": WALL_TOP[b], "thickness": 2.4, "at": [[round(c, 4), 0, round(FRONT, 4), 0]], "tiers": [
        {"h": F["low"], "openings": [{"at": off, "width": F["door"][0], "sill": 0, "springing": F["door"][1], "head": {"profile": "flat"}, "surround": pedi(F["ped"][0])}]},
        {"h": F["mid"], "openings": [{"at": off, "width": F["win"][0], "sill": F["win"][1], "springing": F["win"][2], "head": {"profile": "flat"}, "surround": pedi(F["ped"][1])}]},
        {"openings": [{"at": off, "width": F["up"][0], "sill": F["up"][1], "springing": F["up"][2], "head": {"profile": "pointed", "spread": 1.4}, "tracery": True}]}],
        **({"_about": "the bay's wall: portal, square window, pointed window"} if b == 0 else {})})
front_bay(0, 1, 0)
for b in (1, 2):
    for sx in (1, -1): front_bay(b, sx, 0)
# the gable: a screen on the walls, each bay's own rake; lace along it, a spirelet every third post
add("gable nave", {"type": "screen", "outline": [[-BX[0], "naveTop - 0.05"], [BX[0], "naveTop - 0.05"], [BX[0], RAKE[0][1]], [0, RAKE[0][0]], [-BX[0], RAKE[0][1]]], "t": 2.4,
                   "at": [[0, 0, round(FRONT, 4), 0]], "_about": "the broken gable: over the nave's bay to 56.5m, and over each aisle's a rake of its own, a step down at each buttress"})
for b, sx, nm in ((1, 1, "inner right"), (1, -1, "inner left"), (2, 1, "outer right"), (2, -1, "outer left")):
    a, e = EDGE[b], EDGE[b + 1]
    add(f"gable {nm}", {"type": "screen", "outline": [[sx * a, WALL_TOP[b] - 0.05], [sx * e, WALL_TOP[b] - 0.05], [sx * e, RAKE[b][1]], [sx * a, RAKE[b][0]]], "t": 2.4, "at": [[0, 0, round(FRONT, 4), 0]]})
LACE = {"h": 1.5, "panel": 1.3, "t": 0.3, "every": 3, "spirelet": {"w": 0.3, "s": 1.3}, "at": [[0, 0, round(FRONT, 4), 0]]}
add("gable lace nave", {"type": "cresting", "run": [[-BX[0], RAKE[0][1]], [0, RAKE[0][0]], [BX[0], RAKE[0][1]]], **LACE})
for b, sx, nm in ((1, 1, "inner right"), (1, -1, "inner left"), (2, 1, "outer right"), (2, -1, "outer left")):
    add(f"gable lace {nm}", {"type": "cresting", "run": [[sx * EDGE[b], RAKE[b][0]], [sx * EDGE[b + 1], RAKE[b][1]]], **LACE})
# the buttresses, three stages each, setting back; their heads level with the rakes' steps
TOPS = [50.5, 41.0, 33.5]
def stages(b):
    W = [(3.4, 3.8), (2.8, 3.0), (2.2, 2.2)] if b < 2 else [(4.2, 4.2), (3.6, 3.4), (3.0, 2.6)]   # (the corner's heavier: the stair goes up behind it)
    H = [0, 14.0, 26.0, TOPS[b]]
    return [(H[i], H[i + 1], *W[i]) for i in range(3)]
for b in range(3):
    for i, (y0, y1, w, dp) in enumerate(stages(b)):
        add(f"front buttress {b + 1} stage {i + 1}", {"type": "box", "width": w, "length": round(dp + 0.8, 3), "height": y1 - y0,
            "at": [[sx * BX[b], y0, round(FRONT + dp / 2 - 0.4, 3), 0] for sx in (1, -1)],
            **({"_about": "the front's buttresses: by the nave, between the aisles, at the corners, each setting back twice"} if (b, i) == (0, 0) else {})})
face = lambda b, i: FRONT + stages(b)[i][3] - 0.2      # (a stage's front face, less a little: a thing on it stands in it)
TOP_Z = lambda b: round(FRONT + stages(b)[2][3] / 2 - 0.4, 3)
add("front pinnacles nave", {"type": "pinnacle", "w": 1.05, "sides": 8, "h": 4.0, "s": 9.5, "gablets": 0.8, "crockets": 4, "figure": 2.6, "pair": {"d": 1.15, "axis": "x", "scale": 1},
                             "at": [[sx * BX[0], TOPS[0], TOP_Z(0), 0] for sx in (1, -1)],
                             "_about": "by the nave: the tallest, on the highest heads, DOUBLED -- two octagonal spires side by side on one head, a statue on each point"})
add("front pinnacles middle", {"type": "pinnacle", "w": 1.9, "sides": 8, "h": 3.6, "s": 8.0, "gablets": 1.2, "crockets": 3, "figure": 2.4, "attendants": 0.45,
                               "at": [[sx * BX[1], TOPS[1], TOP_Z(1), 0] for sx in (1, -1)],
                               "_about": "between the aisles: one, octagonal, ringed by four spirelets, a statue on the point"})
CZ = stages(2)[2][3]                                   # (the corner head's depth: the great one at its front, the two behind)
add("front pinnacles corner", {"type": "pinnacle", "w": 1.7, "sides": 8, "h": 4.2, "s": 7.0, "gablets": 1.1, "crockets": 3, "figure": 2.4,
                               "at": [[sx * BX[2], TOPS[2], round(TOP_Z(2) + CZ / 2 - 1.0, 3), 0] for sx in (1, -1)],
                               "_about": "at the corners, THREE: a heavy octagonal one at the head's front..."})
add("front pinnacles corner back", {"type": "pinnacle", "w": 1.15, "sides": 8, "h": 3.2, "s": 5.2, "gablets": 0.7, "crockets": 2, "figure": 1.8, "pair": {"d": 1.6, "axis": "x", "scale": 1},
                                    "at": [[sx * BX[2], TOPS[2], round(TOP_Z(2) - CZ / 2 + 0.2, 3), 0] for sx in (1, -1)],
                                    "_about": "...and two lighter ones side by side behind it"})
add("gable apex", {"type": "pinnacle", "w": 0.9, "h": 1.6, "s": 2.0, "gablets": 0.5, "figure": 2.6, "at": [[0, 56.9, round(FRONT - 0.3, 3), 0]],
                   "_about": "on the gable's point"})
# statues on the buttresses' faces, each on a corbel under its canopy (no markers: there are 2,300 on the real one -- a turned figure at this size)
rows = [(0, 0, 6.4), (0, 0, 10.5), (0, 1, 15.5), (0, 1, 20.5), (0, 2, 28.0), (0, 2, 34.0), (0, 2, 40.0), (1, 0, 6.4), (1, 0, 10.5), (1, 1, 15.5), (1, 1, 20.5), (1, 2, 28.0), (1, 2, 33.5), (2, 0, 6.4), (2, 1, 15.5), (2, 1, 20.5), (2, 2, 27.5)]
figs = [[sx * BX[b], y, round(face(b, i), 3), 0] for b, i, y in rows for sx in (1, -1)]
add("front statues", {"type": "pinnacle", "w": 0.8, "h": 0.25, "s": 0.02, "figure": 2.2, "at": figs,
                      "_about": "a statue on a corbel, on each stage of each front buttress"})
add("front canopies", {"type": "pinnacle", "w": 0.95, "h": 0.2, "s": 1.5, "gablets": 0.4, "at": [[x, y + 2.65, z, 0] for x, y, z, _ in figs],
                       "_about": "the canopy over each"})
# THE TRANSEPT: an arm each side as high as the nave, from the clerestory out past the outer wall -- its walls on the
# bay lines either side of the crossing's two bays, the aisles running on through them by an arch each, its windows
# over the aisles' roofs; a portal and a great window in each end; four rib vaults down each arm, as high as the nave's.
# And each arm has its AISLES, the bays either side of it (2 and 5) carried out past the outer wall at the outer aisles' height,
# which makes the arm's mass 39m broad, as the church's plan has it; a window in their walls and ends, a terrace over them
TR_BAY = (ARM_X - 2 - HALF_B) / 4
TR_BAYS = [HALF_B + (j + .5) * TR_BAY for j in range(4)]
tc = (HALF_B + ARM_X) / 2
AA_X0, AA_X1 = WALL_X, ARM_X - 2                  # (an arm's aisle, inside)
AA_C = (AA_X0 + AA_X1) / 2
SIDE = [{"h": 31.0, "openings": [{"x": INNER_X - P["aisleW"] / 2, "width": 7.0, "sill": 0, "springing": 17.0, "head": POINTED, "glass": False},
                                 {"x": INNER_X + P["aisleT"] + P["aisleW"] / 2, "width": 7.0, "sill": 0, "springing": 10.0, "head": POINTED, "glass": False},
                                 {"x": AA_C, "width": 7.0, "sill": 0, "springing": 10.0, "head": POINTED, "glass": False}]},
        {"openings": [{"x": x, "width": 2.6, "sill": 1.5, "springing": 8.0, "head": POINTED, "tracery": True} for x in TR_BAYS]}]
for sx, nm in ((1, "right"), (-1, "left")):
    add(f"transept walls {nm}", {"type": "wall", "width": round(ARM_X - HALF_B, 4), "height": "naveTop", "thickness": 2.0,
        "tiers": [{**t, "openings": [{**{k: v for k, v in o.items() if k != "x"}, "at": round(sx * (o["x"] - tc), 4)} for o in t["openings"]]} for t in SIDE],
        "at": [[round(sx * tc, 4), 0, TZ0 + 2, 0], [round(sx * tc, 4), 0, TZ1, 0]],
        **({"_about": "the arm's two side walls (on the bay lines: a wall's thickness is behind its line), an arch through each for each aisle"} if sx > 0 else {})})
    add(f"transept end {nm}", {"type": "wall", "width": TZ1 - TZ0, "height": "naveTop", "thickness": 2.0,
        "tiers": [{"h": 12.0, "openings": [{"at": 0, "width": 5.0, "sill": 0, "springing": 7.0, "head": POINTED, "wimperg": {"pitch": 58}}]},
                  {"openings": [{"at": 0, "width": 6.0, "sill": 3.0, "springing": 23.0, "head": {"profile": "pointed", "spread": 1.2}, "tracery": True}]}],
        "at": [[round(sx * ARM_X, 4), 0, CROSS_Z, round(sx * 1.5707963, 7)]]})
add("transept vaults", {"type": "groin", "width": round(TR_BAY, 4), "length": TR_IN, "springing": "clearH", "top": "naveTop",
                        "across": {"profile": "pointed", "spread": round(((TR_IN / TR_BAY) ** 2 * 3 - 1) / 2, 4)}, "along": POINTED,
                        "at": [[round(sx * x, 4), 0, CROSS_Z, 0] for sx in (1, -1) for x in TR_BAYS],
                        "_about": "four bays down each arm, their crowns the nave's"})
add("transept ribs", {"type": "ribs", "on": "transept vaults", "width": 0.45, "depth": 0.3, "wall": {"width": 0.6, "depth": 0.35}})
# (an arm's aisle: its side wall on the far bay line, its end wall in line with the arm's, one rib vault, a terrace)
AA_Z = [round(LINE(2) + (BAY - 1) / 2, 4), round(LINE(5) + 1 + (BAY - 1) / 2, 4)]     # their middles
AA_L, AA_W = round(BAY - 1, 4), round(AA_X1 - AA_X0, 4)
AA_WIN = {"width": 3.4, "sill": 3.5, "springing": 11.0, "head": {"profile": "pointed", "spread": 1.2}, "tracery": True}
add("arm aisle walls", {"type": "wall", "width": round(ARM_X - WALL_X, 4), "height": "outerWallH", "thickness": 2.0, "tiers": [{"openings": [{"at": 0, **AA_WIN, "width": 4.4}]}],
                        "at": [[round(sx * (WALL_X + ARM_X) / 2, 4), 0, round(z, 4), 0] for sx in (1, -1) for z in (LINE(2), LINE(6) + 2)],
                        "_about": "the arm's aisles' long walls, on the bay lines beyond them"})
add("arm aisle ends", {"type": "wall", "width": round(AA_L + 2, 4), "height": "outerWallH", "thickness": 2.0, "tiers": [{"openings": [{"at": 0, **AA_WIN}]}],
                       "at": [[round(sx * ARM_X, 4), 0, round(z, 4), round(sx * 1.5707963, 7)] for sx in (1, -1) for z in (AA_Z[0] - 1, AA_Z[1] + 1)]})
add("arm aisle vaults", {"type": "groin", "width": AA_W, "length": AA_L, "springing": "outerSpring", "top": "outerTop",
                         "across": {"profile": "pointed", "spread": round(((AA_L / AA_W) ** 2 * 3 - 1) / 2, 4)}, "along": POINTED,
                         "at": [[round(sx * AA_C, 4), 0, z, 0] for sx in (1, -1) for z in AA_Z]})
add("arm aisle ribs", {"type": "ribs", "on": "arm aisle vaults", "width": 0.35, "depth": 0.25, "wall": {"width": 0.45, "depth": 0.3}})
add("arm aisle terraces", {"type": "box", "width": round(ARM_X - WALL_X, 4), "length": round(AA_L + 2, 4), "height": 0.4,
                           "at": [[round(sx * (WALL_X + ARM_X) / 2, 4), "outerWallH - 0.4", round(z, 4), 0] for sx in (1, -1) for z in (AA_Z[0] - 1, AA_Z[1] + 1)],
                           "_about": "over an arm's aisle, at the outer terrace's height"})
parts["arm aisles interior"] = {"type": "interior", "plan": {"rect": [round(AA_W + 2, 4), round(AA_L + 1, 4)]}, "height": "outerWallH - 0.4",
                                "at": [[round(sx * (AA_C + 1 - 1), 4), 0, z, 0] for sx in (1, -1) for z in AA_Z]}
# THE ARMS BUTTRESSED: they stand out past the outer aisles the nave's height, carrying its vaults -- two buttresses on each
# end wall either side of the portal, and from piers on the aisles' long walls a flyer over each aisle's terrace to the arm's
# side wall -- each one carrying a pinnacle clear of the eaves: the forest of spires carried round the arms
TB_H = "naveTop - 1"
tb_end = [[round(sx * (ARM_X + 1.5), 4), 0, round(CROSS_Z + dz, 4), 0] for sx in (1, -1) for dz in (-6.0, 6.0)]
add("transept end buttresses", {"type": "box", "width": 4.0, "length": 2.4, "height": TB_H, "at": tb_end})
add("transept pinnacles", {"type": "pinnacle", "w": 1.6, "sides": 8, "h": 3.6, "s": 8.0, "gablets": 1.1, "crockets": 3, "figure": 2.2,
                           "at": [[round(x + (0.4 if x > 0 else -0.4), 4), TB_H, z, 0] for x, _, z, _ in tb_end]})
arm_fb = {"pierH": "outerWallH + 3.8", "pierD": 2.4, "span": round(BAY - 1, 4), "low": "outerWallH - 0.3", "high": "outerWallH + 7.7", "top0": "outerWallH + 3.7", "top1": "outerWallH + 11.7"}
ARM_PIERS = [(sx * x, z, yaw) for sx in (1, -1) for x in (TR_BAYS[2] + TR_BAY / 2, ARM_X - 1.0) for z, yaw in ((LINE(6), 1.5707963), (LINE(2), -1.5707963))]
add("arm flyers", {"type": "component", "use": "components/flying-buttress", "params": arm_fb, "build": ["pier", "flyer"],
                   "at": [[round(x, 4), 0, round(z, 4), yaw] for x, z, yaw in ARM_PIERS],
                   "_about": "over each arm's aisle from a pier on its long wall to the arm's side wall, where the arm's vault pushes out"})
by_turns("arm pinnacles", [PIN_A, PIN_B], [(i, round(x, 4), "outerWallH + 3.8", round(z + (1.2 if z > CROSS_Z else -1.2), 4)) for i, (x, z, _) in enumerate(ARM_PIERS)])
TR_ROOF = ARM_X + 0.2 - HALF_B
add("transept roofs", {"type": "roof", "form": "gable", "width": TZ1 - TZ0 + 0.4, "length": round(TR_ROOF, 4), "pitch": ROOF_PITCH,
                       "at": [[round(sx * (HALF_B + TR_ROOF / 2), 4), "naveTop", CROSS_Z, 1.5707963] for sx in (1, -1)]})
# THE APSE: half a decagon of five faces, one of them square to the axis (a corner on the axis would have been wrong: the
# middle one of the three great windows looks straight down the nave), round the choir and a single ambulatory -- the
# inner aisles carried round; the outer aisles stop at the sacristies' ends. The three windows are the largest of any
# Gothic church (some 20m by 7m), the two faces either side of them lit as well.
apse = [[0, 0, "0 - naveL / 2", 0]]
APSE = dict(count=10, at=[3, 4, 5, 6, 7])
RING_R = "innerX + aisleT"
add("chevet", {"type": "ring", **APSE, "rOuter": RING_R, "rInner": "innerX", "height": "innerWallH",
               "opening": {"width": 7.0, "sill": 4.0, "springing": 17.0, "head": {"profile": "pointed", "spread": 1.2}, "tracery": True}, "place": apse,
               "_about": "the apse's walls and great windows (their heads, 24m, under the ambulatory's vault, which springs at the aisles' 25.7m)"})
# the chevet's BUTTRESSES on its corners, and from each a flyer to the choir's clerestory, each with its pinnacle (the
# corners at the flanks' ends are the flank's)
R_OUT = P["naveW"] / 2 + P["pierT"] + P["aisleW"] + P["aisleT"]
chev = [math.radians(a) for a in (126, 162, 198, 234)]
sp = lambda r, t: (round(r * math.sin(t), 4), round(-NAVE_L / 2 + r * math.cos(t), 4))
apse_fb = {"pierH": "innerWallH + 8", "pierD": 3.0, "pierW": 2.2, "span": round(R_OUT - .1 - (P["naveW"] / 2 + P["pierT"]) * math.cos(math.pi / 10), 4), "low": "innerWallH + 4.6", "high": "innerWallH + 10.4", "top0": "innerWallH + 7.8", "top1": "innerWallH + 13.6"}
add("apse flyers", {"type": "component", "use": "components/flying-buttress", "params": apse_fb, "build": ["pier", "flyer"],
                    "at": [[*sp(R_OUT - .1, t)[:1], 0, sp(R_OUT - .1, t)[1], round(math.atan2(math.cos(t), -math.sin(t)), 6)] for t in chev],
                    "_about": "a buttress on each corner of the apse, its flyer over the ambulatory's roof to the choir"})
by_turns("apse pinnacles", [PIN_A, PIN_B], [(i, sp(R_OUT + 1.4, t)[0], "innerWallH + 8", sp(R_OUT + 1.4, t)[1]) for i, t in enumerate(chev)])
# THE CHOIR opens to the ambulatory as the nave does to its aisles: an ARCADE round the half ring below the arcade's
# height, the clerestory over it; the ambulatory vaulted round the apse's centre, at its aisle's height, so the aisles' vaults run on
add("choir arcade", {"type": "ring", **APSE, "rOuter": "naveW / 2 + pierT", "rInner": "naveW / 2", "height": "arcadeH",
                     "opening": {"width": 4.6, "sill": 0, "springing": "spring", "head": {"profile": "pointed", "spread": 1}}, "place": apse,
                     "_about": "the choir's piers and their arches into the ambulatory: the nave arcade's springing and pointed head"})
add("choir", {"type": "ring", **APSE, "rOuter": "naveW / 2 + pierT", "rInner": "naveW / 2", "y": "arcadeH", "height": "naveTop - arcadeH",
              "opening": {"width": 3.0, "sill": 5.0, "springing": "clearH + 5 - arcadeH", "head": {"profile": "pointed", "spread": 1}, "tracery": True}, "place": apse,
              "_about": "the choir's clerestory, over its arcade"})
add("inner ambulatory vault", {"type": "vault", "count": 20, "turn": 0.5, "at": list(range(5, 15)), "rInner": "naveW / 2 + pierT", "rOuter": "innerX",
                               "springing": "crown", "top": "aisleTop", "clears": "spring + 3 * 1.7321", "head": {"profile": "segmental", "rise": "aisleRise"}, "place": apse,
                               "_about": "the inner aisles' vault carried round: their springing, rise and top"})
# (the CHOIR VAULT springs over its windows' heads, at 40.5m -- sprung at the nave's springing it buried them, the
#  half dome's shell standing across their upper lights -- and rises a shallow segment, under the choir's roof; over
#  the arch between it and the nave a DIAPHRAGM closes the nave's attic off from the choir)
CHOIR_SPRING = 40.5
add("choir vault", {"type": "dome", "sweep": 0.5, "sides": 10, "radius": "naveW / 2 + pierT", "thickness": "pierT", "head": {"profile": "segmental", "rise": 5.5},
                    "at": [[0, CHOIR_SPRING, "0 - naveL / 2", 3.14159265]]})
add("choir diaphragm", {"type": "wall", "width": "naveW + 2 * pierT", "height": f"naveTop - clearH", "thickness": 2.0, "glass": False,
                        "openings": [{"at": "naveW / 2 + pierT", "width": "naveW", "sill": 0, "springing": 0, "head": POINTED}],
                        "at": [[0, "clearH", "0 - naveL / 2", 0]],
                        "_about": "the wall over the choir's arch, from the nave vault's springing to the roof: the nave's last cell ends against it"})
add("choir roof", {"type": "dome", "sweep": 0.5, "sides": 10, "radius": "naveW / 2 + pierT + 0.3", "thickness": 0, "head": {"profile": "trigonal", "rise": 4.5},
                   "at": [[0, "naveTop", "0 - naveL / 2", 3.14159265]]})
add("ambulatory roof", {"type": "dome", "sweep": 0.5, "sides": 10, "radius": f"{RING_R} + 0.3", "thickness": 0, "head": {"profile": "trigonal", "rise": 6},
                        "oculus": "naveW / 2 + pierT", "cap": False,
                        "at": [[0, "innerWallH", "0 - naveL / 2", 3.14159265]],
                        "_about": "the lean-to round the choir: a half cone cut off at the choir's wall (`oculus`) and left open there"})
# THE CROSSING carries the tiburio: its octagon stands on the clerestory walls either side, and across the nave on a
# DIAPHRAGM at each end of the crossing -- a wall over the transverse arch, pierced by the arch itself, from the vault's
# springing up to the roof's foot, as the four great arches of a crossing are -- and over the four corners between them
# on SQUINCHES, a triangle of masonry across each corner under the octagon's diagonal face. Inside, the crossing is open
# up into the tiburio: its octagonal DOME springs from the octagon's foot.
TIB = 10.25                                   # (its octagon's outer faces: over the clerestory walls, and over the diaphragms)
add("crossing diaphragms", {"type": "wall", "width": "naveW + 2 * pierT", "height": "naveTop - clearH", "thickness": 2.0, "glass": False,
                            "openings": [{"at": "naveW / 2 + pierT", "width": "naveW", "sill": 0, "springing": 0, "head": POINTED}],
                            "at": [[0, "clearH", TZ0 + 2, 0], [0, "clearH", TZ1, 0]],
                            "_about": "the walls over the crossing's two end arches, on which the tiburio's end faces stand"})
ap = (TIB - 1.0) * math.sqrt(2)               # (the octagon's inner diagonal faces: x + z = ap from the crossing's middle)
hx, hz = P["naveW"] / 2, TR_IN / 2
for n, (sx, sz) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
    tri = [[round(sx * x, 4), round(CROSS_Z + sz * z, 4)] for x, z in ((hx, hz), (hx, ap - hx), (ap - hz, hz))]
    add(f"crossing squinch {n + 1}", {"type": "prism", "plan": {"points": tri if sx * sz > 0 else tri[::-1]}, "height": "naveTop - 42", "at": [[0, 42.0, 0, 0]],
        **({"_about": "the squinches: a triangle across each of the crossing's corners, carrying the tiburio's diagonal faces"} if n == 0 else {})})
add("crossing dome", {"type": "dome", "sides": 8, "radius": round(TIB / math.cos(math.pi / 8) - 0.5, 3), "thickness": 0.6,
                      "head": {"profile": "pointed", "spread": 0.6}, "at": [[0, "naveTop", CROSS_Z, 0]],
                      "_about": "the crossing's own dome inside the tiburio, struck from the octagon's foot"})
# THE TIBURIO over the crossing: the octagon with its gables and a gallery ring (`domed-tower`, without its cap), on that a
# slender crocketed octagonal SPIRE (a `pinnacle` at this size: the real one is open tracery on a stair), to the gilded
# MADONNINA at 108.5m. At the crossing's four corners, on the piers where the walls cross, the four GUGLIE, each tied to the
# octagon by a little flyer (the north-east one, Carelli's, the oldest of the forest).
add("tiburio", {"type": "component", "use": "components/domed-tower",
                "params": {"sides": 8, "R": round(TIB / math.cos(math.pi / 8), 3), "H": 16, "t": 1.0, "cap": "trigonal", "capRise": 8, "capR": 4.2, "drumR": 5.0, "drumH": 7.5,
                           "kok": 1.5, "finial": 2, "winW": 2.2},
                "build": ["tower", "kokoshniki", "head", "neck", "drum"], "at": [[0, "naveTop", "crossZ", 0]],
                "_about": "the tiburio: the octagon over the crossing with a gable on each face, and the gallery storey on it"})
TIB_TOP = P["clearH"] + P["naveW"] / 2 * 1.7321 + 1.2 + 16 + 1.5 + 7.5   # (naveTop, the octagon, the neck, the gallery)
add("tiburio gallery floor", {"type": "prism", "plan": {"sides": 8, "radius": 5.0}, "height": 0.4, "at": [[0, round(TIB_TOP - 0.4, 3), "crossZ", 0]], "_about": "closing the gallery's head: the spire stands on it"})
# (OPENWORK, as the real one is: an octagonal foot with its gablets, the net of ribs and tracery round a slender core the stair climbs in)
add("tiburio spire foot", {"type": "pinnacle", "w": 6.6, "sides": 8, "h": 2.2, "s": 0.02, "gablets": 2.0, "at": [[0, round(TIB_TOP, 3), "crossZ", 0]], "_about": "the great spire's foot"})
add("tiburio spire", {"type": "open-spire", "R": 3.5, "rise": 30.2, "rows": 9, "rib": 0.32, "bar": 0.12, "topR": 0.5, "finial": 0, "at": [[0, round(TIB_TOP + 3.65, 3), "crossZ", 0]],
                      "_about": "the great spire, the sky through it"})
add("tiburio spire core", {"type": "column", "radius": 0.85, "height": 28.8, "sides": 8, "at": [[0, round(TIB_TOP + 3.6, 3), "crossZ", 0]], "_about": "the core in the spire's middle, with the stair up it"})
SPIRE_TIP = TIB_TOP + 2.2 + 6.6 * .22 + 29.0
add("madonnina", {"type": "pinnacle", "w": 0.7, "h": 0.5, "s": 0.02, "figure": 4.16, "at": [[0, round(TIB_TOP + 32.3, 3), "crossZ", 0]],
                  "_about": "the Madonnina, 4.16m of gilded copper, on the spire's point"})
gug = [(sx * BX[0], CROSS_Z + sz * BAY) for sx in (1, -1) for sz in (1, -1)]
add("guglie", {"type": "pinnacle", "w": 2.2, "sides": 8, "h": 11.0, "s": 13.0, "gablets": 1.5, "crockets": 5, "figure": 2.6, "attendants": 0.6, "at": [[round(x, 4), "naveTop", round(z, 4), 0] for x, z in gug],
               "_about": "the four guglie, on the crossing's corners"})
fy = []
for x, z in gug:
    d = math.hypot(x, z - CROSS_Z); ux, uz = -x / d, -(z - CROSS_Z) / d
    fy.append([round(x + ux * 1.0, 4), "naveTop", round(z + uz * 1.0, 4), round(math.atan2(-uz, ux), 6)])
add("guglie flyers", {"type": "flyer", "span": round(d - 1.0 - TIB + 0.3, 3), "low": 7.4, "high": 11.5, "top0": 10.0, "top1": 13.4, "width": 0.7, "at": fy,
                      "_about": "from each guglia in to the octagon's diagonal face"})
# spiral turrets up to the roofs, in the westernmost bay of each outer aisle: the stair climbs from the aisle floor to
# a flat terrace over that bay, round the turret, and out through a door in the turret's head onto it; from there the aisle roofs are walked.
# The turret stands at the bay's EAST end against the outer wall, clear of the side portal and its window, the bay
# behind the portal a vestibule
tR = 2.4
a, h8 = round(tR * 0.92388, 4), round(tR * 0.38268, 4)            # the octagon's apothem, and half a face
off = round(a + 0.8, 4)                                          # (clear of the bay line's wall rib, and its flyer over the head)
tz = f"naveL / 2 - bayLen + {off}"
for sx, nm in ((1, "right"), (-1, "left")):
    tx = f"{sx} * (wallX - aisleT - {a})"                            # (its outer face against the outer wall)
    # the turret, its door (bay 4 of 8: -z, into the aisle -- the turret stands at the component's middle, so say it) and the
    # spiral from the door up through its open head onto the terrace -- `tower-stair`, less the floor it would lay
    add(f"stair {nm}", {"type": "component", "use": "components/tower-stair", "params": {"W": 6.0, "H": "outerWallH", "tR": tR, "tx": 0, "tz": 0, "doorBay": 4, "hand": "right" if sx > 0 else "left"},
                        "build": ["turret", "turret door", "stair"], "at": [[tx, 0, tz, 0]]})
    # the terrace over the turret's bay: the bay less the turret's octagon (faces a = tR cos 22.5 from its middle), so
    # there is no crack round the stair's head -- slabs in the turret's own frame (u out toward the outer wall, v west):
    # inside it, west of it, the strips east of it and outside it, and the four corners of its square the octagon
    # leaves open
    u0, u1 = f"innerX + aisleT - (wallX - aisleT - {a})", a      # (the arcade, the outer wall)
    v0, v1 = -off, f"bayLen - {off}"                  # (the bay's east and west ends)
    def slab(u, v):   # a rectangle u x v, mirrored to the turret's side
        return [[f"{sx} * ({x})", z] for x, z in ((u[0], v[0]), (u[1], v[0]), (u[1], v[1]), (u[0], v[1]))]
    pieces = [slab((u0, -a), (v0, v1)), slab((-a, u1), (a, v1)), slab((-a, u1), (v0, -a))]
    pieces += [[[sx * su * a, sv * a], [sx * su * h8, sv * a], [sx * su * a, sv * h8]] for su in (1, -1) for sv in (1, -1)]
    for k, pts in enumerate(pieces):
        add(f"stair terrace {nm} {k + 1}", {"walked": True, "type": "prism", "plan": {"points": pts}, "height": 0.4,
            "at": [[tx, "outerWallH - 0.4", tz, 0]], **({"_about": "the flat roof over the turret's bay, round the turret's head"} if k == 0 else {})})
    # the turret's HEAD over the terrace: its octagon on up, a door in the bay the spiral arrives in (bay 0: west, onto
    # the terrace beside it -- the last tread ends some 20 degrees round from there, either hand), a stone lid and a
    # pinnacle on it
    head = {"type": "ring", "count": 8, "rOuter": tR, "rInner": tR - 0.4, "height": 3.0, "y": "outerWallH", "place": [[tx, 0, tz, 0]]}
    add(f"turret head {nm}", {**head, "skip": [0], "solid": True, **({"_about": "the stair turret's head over the terrace, the spiral arriving inside it"} if sx > 0 else {})})
    add(f"turret head door {nm}", {**head, "at": [0], "opening": {"width": 1.2, "sill": 0, "springing": 1.8, "head": {"profile": "pointed", "spread": 1}}})
    add(f"turret lid {nm}", {"type": "prism", "plan": {"sides": 8, "radius": tR + 0.05}, "height": 0.35, "at": [[tx, "outerWallH + 3.0", tz, 0]]})
    add(f"turret pinnacle {nm}", {"type": "component", "use": "components/pinnacle", "params": {"w": 1.5, "h": 4.0, "s": 6.0},
                                  "at": [[tx, "outerWallH + 3.35", tz, 0]]})
    parts[f"turret head {nm} interior"] = {"type": "interior", "plan": {"sides": 8, "radius": tR - 0.2}, "height": 3.0, "at": [[tx, "outerWallH", tz, 0]],
                                           **({"_about": "inside the turret's head, where the spiral arrives"} if sx > 0 else {})}
# ---- THE INTERIORS (for the finishes: the inlaid floor is the church's, the pavement outside and the terraces are not):
# the church in three stepped boxes on the middle lines of its walls, from the facade's middle -- the whole width up to
# the outer terraces, the nave and inner aisles up to the inner ones, the nave up to its roof's foot (the crossing goes on
# up into the tiburio, its own) -- the transept across them as high as the nave, and round the apse the same three on
# the chevet's, the ambulatory arcade's and the choir's half rings
for nm, x, h in (("body", "wallX - aisleT / 2", "outerWallH - 0.4"), ("inner aisles", "innerX + aisleT / 2", "innerWallH - 0.4"), ("nave", "naveW / 2 + pierT / 2", "naveTop")):
    parts[f"{nm} interior"] = {"type": "interior", "plan": {"rect": [f"2 * ({x})", "naveL + 1.2"]}, "height": h, "at": [[0, 0, 0.6, 0]]}
parts["body interior"]["_about"] = "the nave and its four aisles from the facade's middle to the apse, up to the outer aisles' terraces; over the nave and the inner aisles, two more boxes stepping up as their roofs do"
parts["transept interior"] = {"type": "interior", "plan": {"rect": [round(2 * (ARM_X - 1), 4), round(TZ1 - TZ0 - 2, 4)]}, "height": "naveTop", "at": [[0, 0, CROSS_Z, 0]]}
for nm, n, r, h in (("inner ambulatory", 20, "innerX + aisleT / 2", "innerWallH - 0.4"), ("choir", 10, "naveW / 2 + pierT / 2", "naveTop")):
    parts[f"{nm} interior"] = {"type": "interior", "plan": {"sides": n, "radius": r}, "arc": [90, 270], "height": h, "at": [[0, 0, "0 - naveL / 2", 0]]}
parts["inner ambulatory interior"]["_about"] = "round the apse: the ambulatory's half ring up to the roof's foot, the choir's to the nave's"
# ---- INSIDE (as notre_dame.py gothic): seating up to the crossing (crossZ), the altar east of it, the organ in the north transept
add("seating", {"type": "zone", "zone": "seating", "w": "naveW - 1.6", "d": "(naveL / 2 - bayLen - 1.5) - (crossZ + bayLen + 1.5)", "h": "arcadeH",
                "at": [[0, 0, "((crossZ + bayLen + 1.5) + (naveL / 2 - bayLen - 1.5)) / 2", 1.5707963]]})
add("altar", {"type": "zone", "zone": "altar", "w": "naveW - 2", "d": 3.2, "h": "arcadeH", "at": [[0, 0, "crossZ - bayLen - 3.5", 1.5707963]]})
add("organ", {"type": "zone", "zone": "organ", "w": 5, "d": 4.0, "h": 12, "at": [[round(-(ARM_X - 4.1), 3), 0, f"crossZ + {dz}", 0] for dz in (-5.5, 5.5)],
              "_about": "the organ in two cases, against the north transept arm's end wall either side of its portal (Milan has no west gallery: its organs face each other across the choir)"})
doc = {"name": "Milan Cathedral",
  "_about": "THE DUOMO OF MILAN: 158m long, the front 68m and 56.5m high, the transept 93m across, the spire 108.5m. Five aisles west of the crossing stepping down in three levels, every bay rib-vaulted, three east of it round a five-faced apse (the sacristies where the outer aisles would be); a transept with aisles of its own; two tiers of flying buttresses on every bay line, and no one kind of pinnacle (`pinnacle` parts, by turns); openwork cresting over every bay; the front a bay at a time -- portal, square window, pointed window, each under its own head -- and a broken gable, between six buttresses that set back twice, the pairs carrying three different pinnacles, the middle pair doubled; the tiburio, its four guglie, its spire and the Madonnina. Spiral turrets in the westernmost bays climb to the outer aisles' flat terraces, a stair from there to the inner ones: the aisle roofs are walked on, under the flyers.",
  "params": P, "base": {"height": 1.2, "steps": 4, "stepOut": 0.8, "margin": 3}, "railing": {"type": "stone"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/milan.json"), "w").write(json.dumps(doc, indent=2) + "\n")
