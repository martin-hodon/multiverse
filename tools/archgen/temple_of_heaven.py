# THE TEMPLE OF HEAVEN, Beijing (1420, the hall rebuilt 1889): the Hall of Prayer for Good Harvests (Qinian Dian) on the
# Altar of Prayer for Good Harvests, in its walled court with the Qinian Gate and the two annex halls.
#   The ALTAR is the building's `base`: three round tiers of white marble (91, 80 and 68m across, 1.8m each), a
#   balustrade of posts and carved panels round every tier's edge, stairs up all four sides -- to the south and north two
#   flights either side of the carved imperial way, to the east and west one flight.
#   The HALL is round and in three tiers, each roofed with blue tiles: twelve bays of lattice doors and windows between
#   the twelve outer (eave) columns, then a drum of windows on the twelve middle (gold) columns, a smaller drum on the
#   four inner (dragon-well) columns, and the gilded finial on the top roof's point. Every roof is the jujia section
#   turned (profiles.js), its eave carried on a ring of dougong bracket sets; the two lower roofs are rings, cut short by
#   an oculus where the drum above stands on them (`atop`, `atopR`: the drum stands where the roof has narrowed to it).
#   Inside, the caisson ceiling -- a coffered saucer -- under the top roof.
#   The COURT: a red wall with a tiled coping (components/palace-wall), the Qinian Gate in its south side
#   (components/chinese-hall, walked through), the east and west annex halls facing the altar.
#   South is +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q, PI = math.pi / 2, math.pi
r4 = lambda v: round(v, 4)

# the jujia section: height above the eave of a point d metres in from it, on a roof of radius a (profiles.js jujia)
def J(a, lo, hi, d): return lo * d + (hi - lo) * d * d / (2 * a)

# ---- the altar: three tiers, the base ------------------------------------------------------------------------
NB = 96                                  # bays round every tier (the balustrade's panels, the base's polygon)
TIER, RT, OUT = 1.8, 34.0, 5.75          # a tier's height, the top tier's radius, how far each tier below reaches out
HB = 3 * TIER
cosb = math.cos(PI / NB)
corner = [RT + k * OUT / cosb for k in range(3)]      # each tier's corner radius (top, middle, bottom): the base insets mitred
apo = [c * cosb for c in corner]                    # ...and its apothem, the flat on each axis
base = {"height": HB, "steps": 3, "stepOut": OUT, "plan": {"sides": NB, "radius": RT}}

# the balustrade round each tier: panels (a ring of NB bays, the stair gaps left out) and posts at the joints, in four
# arcs between the gaps. Gaps: five bays to the south and north, three to the east and west.
GS, GE = 2, 1
gaps = [((b % NB) + NB) % NB for c, g in ((0, GS), (NB // 4, GE), (NB // 2, GS), (3 * NB // 4, GE)) for b in range(c - g, c + g + 1)]
arcs = []                                # (centre bay, bays spanned) of each run of posts
for c0, g0, c1, g1 in ((0, GS, NB // 4, GE), (NB // 4, GE, NB // 2, GS), (NB // 2, GS, 3 * NB // 4, GE), (3 * NB // 4, GE, NB, GS)):
    a, b = c0 + g0 + .5, c1 - g1 - .5
    arcs.append(((a + b) / 2, b - a))
for k, nm in enumerate(("upper", "middle", "lower")):
    y = -k * TIER
    rO = corner[k] - .15
    add(f"{nm} balustrade panels", {"type": "ring", "count": NB, "rOuter": r4(rO), "rInner": r4(rO - .14), "height": .85, "solid": True,
                                    "skip": gaps, "place": [[0, y, 0, 0]],
                                    **({"_about": "each tier's balustrade: carved panels between the posts, open where the stairs come up"} if k == 0 else {})})
    add(f"{nm} balustrade posts", {"type": "colonnade", "plan": "round", "count": 21, "arc": 75, "radius": r4(rO - .07), "shaft": "square",
                                   "columnR": .12, "height": 1.3, "base": {"h": .12, "r": .15}, "capital": {"h": .34, "r": .15},
                                   "at": [[0, y, 0, r4(c * 2 * PI / NB)] for c, _ in arcs]})

# the stairs: 11 steps a tier. South and north: the carved IMPERIAL WAY (a slab sloping from tier to tier -- the
# `shed` roof form is that wedge) with a flight either side; east and west, one flight.
STEPS, RUN = 11, .3
FL = STEPS * RUN                         # a flight's length on the ground
SW, FW, EW = 2.4, 2.6, 3.0               # the imperial way's width, the flights' beside it, the east and west flights'
pitch = math.degrees(math.atan(TIER / FL))
for k, nm in enumerate(("upper", "middle", "lower")):
    y0, A = -(k + 1) * TIER, apo[k]
    foot = A + FL - .03                  # (its top tread reaches 3cm into the tier above)
    flights = []
    for side, yaw in ((1, Q), (-1, -Q)):            # south (climbing -z), north (climbing +z)
        for xc in (-(SW / 2 + FW / 2), SW / 2 + FW / 2):
            flights.append([r4(xc + side * FW / 2), y0, r4(side * foot), yaw])
    add(f"{nm} stairs", {"type": "flight", "width": FW, "run": RUN, "steps": STEPS, "top": TIER, "landing": 0,
                         "at": [[x, y, z, r4(a)] for x, y, z, a in flights],
                         **({"_about": "a flight either side of the imperial way, to the south and to the north"} if k == 0 else {})})
    add(f"{nm} side stairs", {"type": "flight", "width": EW, "run": RUN, "steps": STEPS, "top": TIER, "landing": 0,
                              "at": [[r4(foot), y0, -EW / 2, r4(PI)], [r4(-foot), y0, EW / 2, 0]]})
    add(f"{nm} imperial way", {"type": "roof", "form": "shed", "width": FL, "length": SW, "pitch": r4(pitch),
                               "at": [[0, y0, r4(A + FL / 2 - .03), Q], [0, y0, r4(-(A + FL / 2 - .03)), -Q]],
                               **({"_about": "the carved slab up the middle of the south and north stairs: a wedge from tier to tier"} if k == 0 else {})})

# ---- the hall ----------------------------------------------------------------------------------------------------
# ground storey: twelve bays between the twelve eave columns -- doors on the four axes, lattice windows between
R1, WT, H1, AH1 = 12.0, .4, 6.2, .8
add("hall doors", {"type": "ring", "count": 12, "rOuter": R1, "rInner": R1 - WT, "height": H1, "at": [0, 3, 6, 9], "glass": False,
                   "opening": {"width": 4.2, "sill": 0, "springing": 5.0, "head": {"profile": "flat"}}, "place": [[0, 0, 0, 0]],
                   "_about": "twelve bays of lattice between the eave columns: doors on the four axes..."})
add("hall windows", {"type": "ring", "count": 12, "rOuter": R1, "rInner": R1 - WT, "height": H1, "skip": [0, 3, 6, 9], "glass": True,
                     "opening": {"width": 4.6, "sill": .9, "springing": 5.6, "head": {"profile": "flat"}}, "place": [[0, 0, 0, 0]],
                     "_about": "...and lattice windows over a low wall between"})
add("eave columns", {"type": "column", "radius": .45, "height": H1 + AH1, "spiral": {"count": 12, "radius": R1 - WT / 2, "turn": r4(PI / 12)},
                     "_about": "the twelve eave columns (the hours), red, at the bays' joints"})
add("architrave 1", {"type": "ring", "count": 12, "rOuter": R1, "rInner": R1 - WT, "height": AH1, "y": H1, "solid": True, "place": [[0, 0, 0, 0]]})
S1, S2, S3 = 1.0, .85, .75               # the bracket sets' scale, tier by tier
BT = 1.06                                # a set's height at scale 1 (components/dougong)
TIP = 1.12                               # ...and its reach to the outer beam
add("brackets 1", comp("components/dougong", {"s": S1}, None, spiral={"count": 48, "radius": R1 - .2, "y": H1 + AH1, "turn": r4(PI / 12)},
                       _about="a ring of dougong bracket sets on the architrave, one on every column and three between"))
parts["brackets 1"].pop("at")

# first roof: the jujia ring from its eave in to the drum above; its soffit comes down on the brackets' outer beams
RE1, T1, LO1, HI1 = 15.6, .7, .25, 1.1
RD2 = 8.6                                # the second drum's (outer) radius: the first roof's oculus
yE1 = H1 + AH1 + BT * S1 - J(RE1, LO1, HI1, RE1 - (R1 - .2 + TIP * S1) - T1)
add("roof 1", {"type": "dome", "radius": RE1, "thickness": T1, "oculus": RD2, "head": {"profile": "jujia", "lo": LO1, "hi": HI1},
               "at": [[0, r4(yE1), 0, 0]], "_about": "the lowest roof: blue tiles on the jujia section, from the eave in to the drum of the tier above"})
# second tier: the drum of windows, standing on the first roof
H2, AH2 = 3.6, .7
add("drum 2", {"type": "ring", "count": 24, "rOuter": RD2, "rInner": RD2 - .35, "height": H2, "glass": True, "atop": "roof 1", "atopR": RD2,
               "opening": {"width": 1.5, "sill": .5, "springing": 3.0, "head": {"profile": "flat"}}, "place": [[0, 0, 0, 0]],
               "_about": "the second tier's drum of lattice windows, standing on the first roof where it has narrowed to it"})
add("architrave 2", {"type": "ring", "count": 24, "rOuter": RD2, "rInner": RD2 - .35, "height": AH2, "solid": True, "atop": "drum 2", "place": [[0, 0, 0, 0]]})
add("brackets 2", {"type": "component", "use": "components/dougong", "params": {"s": S2}, "atop": "architrave 2",
                   "spiral": {"count": 48, "radius": RD2 - .2, "turn": r4(PI / 24)}})
RE2, T2, LO2, HI2 = 12.3, .6, .25, 1.15
RD3 = 5.4
add("roof 2", {"type": "dome", "radius": RE2, "thickness": T2, "oculus": RD3, "head": {"profile": "jujia", "lo": LO2, "hi": HI2}, "atop": "architrave 2",
               "at": [[0, r4(BT * S2 - J(RE2, LO2, HI2, RE2 - (RD2 - .2 + TIP * S2) - T2)), 0, 0]], "_about": "the middle roof"})
# third tier
H3, AH3 = 3.3, .6
add("drum 3", {"type": "ring", "count": 16, "rOuter": RD3, "rInner": RD3 - .35, "height": H3, "glass": True, "atop": "roof 2", "atopR": RD3,
               "opening": {"width": 1.2, "sill": .5, "springing": 2.7, "head": {"profile": "flat"}}, "place": [[0, 0, 0, 0]]})
add("architrave 3", {"type": "ring", "count": 16, "rOuter": RD3, "rInner": RD3 - .35, "height": AH3, "solid": True, "atop": "drum 3", "place": [[0, 0, 0, 0]]})
add("brackets 3", {"type": "component", "use": "components/dougong", "params": {"s": S3}, "atop": "architrave 3",
                   "spiral": {"count": 32, "radius": RD3 - .2, "turn": r4(PI / 32)}})
RE3, T3, LO3, HI3 = 8.4, .5, .3, 1.7
add("roof 3", {"type": "dome", "radius": RE3, "thickness": T3, "head": {"profile": "jujia", "lo": LO3, "hi": HI3}, "atop": "architrave 3",
               "at": [[0, r4(BT * S3 - J(RE3, LO3, HI3, RE3 - (RD3 - .2 + TIP * S3) - T3)), 0, 0]], "_about": "the top roof, to its point"})
add("finial base", {"type": "column", "radius": .55, "height": .8, "sides": 12, "atop": "roof 3", "atopR": .55, "at": [[0, -.25, 0, 0]],
                    "_about": "the gilded finial (baoding): a drum, a ball, a spike"})
add("finial ball", {"type": "dome", "radius": .75, "thickness": 0, "head": {"profile": "onion", "bulge": 1.3, "neck": .5}, "atop": "finial base", "at": [[0, 0, 0, 0]]})

# the columns inside: the middle ring to the second drum's top, the four dragon-well columns to the third's
R2, R3 = 7.75, 4.55
y_d2 = yE1 + J(RE1, LO1, HI1, RE1 - RD2)                      # the second drum's foot (the first roof's height at its radius)
y_d3 = y_d2 + H2 + AH2 + BT * S2 - J(RE2, LO2, HI2, RE2 - (RD2 - .2 + TIP * S2) - T2) + J(RE2, LO2, HI2, RE2 - RD3)
add("gold columns", {"type": "column", "radius": .45, "height": r4(y_d2 + H2 + .05), "spiral": {"count": 12, "radius": R2, "turn": r4(PI / 12)},
                     "_about": "the twelve middle columns (the months), rising inside to the second drum's head"})
add("dragon columns", {"type": "column", "radius": .55, "height": r4(y_d3 + H3 + .05), "spiral": {"count": 4, "radius": R3, "turn": r4(PI / 4)},
                       "_about": "the four dragon-well columns (the seasons), to the third drum's head"})
add("caisson", {"type": "dome", "radius": 4.95, "thickness": .3, "head": {"profile": "segmental", "rise": 1.1}, "atop": "drum 3", "at": [[0, 0, 0, 0]],
                "coffers": {"count": 16, "rows": 2, "from": .12, "to": .8, "depth": .12}, "_about": "the caisson ceiling (zaojing) under the top roof: a coffered saucer"})

# ---- the court --------------------------------------------------------------------------------------------------
G = -HB                                  # the ground, under the altar's lift
CX, CN, CS = 70.0, -80.0, 95.0           # the court: its half width, its north and south walls
WT2, WH = 1.2, 3.8
gate = {"nx": 5, "bw": 5.2, "nz": 2, "bd": 5.6, "H": 5.4, "plat": 1.2, "platOut": 2.4, "backSill": 0, "s": .85, "over": 2.4, "pitch": 38}
gHalf = gate["nx"] * gate["bw"] / 2 + gate["platOut"]
add("qinian gate", comp("components/chinese-hall", gate, [[0, G, CS, 0]],
                        _about="the Qinian Gate: a five-bay hall in the south wall, its middle bay a passage walked through"))
segL = CX - gHalf
add("south wall", comp("components/palace-wall", {"L": r4(segL), "T": WT2, "H": WH},
                       [[r4(sx * (gHalf + segL / 2)), G, CS, Q] for sx in (-1, 1)], _about="the court's red walls, their copings tiled"))
add("side walls", comp("components/palace-wall", {"L": r4(CS - CN + WT2), "T": WT2, "H": WH},
                       [[r4(sx * (CX + WT2 / 2)), G, (CS + CN) / 2, 0] for sx in (-1, 1)]))
add("north wall", comp("components/palace-wall", {"L": r4(2 * CX + 2 * WT2), "T": WT2, "H": WH}, [[0, G, CN - WT2 / 2, Q]]))
annex = {"nx": 7, "bw": 5.0, "nz": 2, "bd": 5.4, "H": 5.2, "plat": .9, "platOut": 2.0, "backSill": .9, "backSteps": 0, "s": .8, "over": 2.2, "pitch": 36}
add("annex halls", comp("components/chinese-hall", annex, [[58.0, G, 30.0, -Q], [-58.0, G, 30.0, Q]],
                        _about="the east and west annex halls, facing the altar across the court"))

doc = {
    "name": "Temple of Heaven",
    "_about": "The Hall of Prayer for Good Harvests on its three-tiered marble altar, in its walled court with the Qinian Gate and the "
              "annex halls (Beijing, 1420; the hall rebuilt 1889). Generated by tools/archgen/temple_of_heaven.py -- edit the script "
              "for arithmetic changes. South is +z.",
    "params": {"detail": 4, "maxDetail": 16},
    "base": base,
    "railing": {"type": "stone", "height": .9},
    "build": build,
    "parts": parts,
}
out = os.path.join(ROOT, "assets", "architecture", "temple-of-heaven.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts; drum 2 at", round(y_d2, 2), "drum 3 at", round(y_d3, 2))
