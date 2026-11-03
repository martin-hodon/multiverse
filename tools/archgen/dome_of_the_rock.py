# THE DOME OF THE ROCK (Qubbat al-Sakhra), Jerusalem (691-92, Abd al-Malik; the outer tiles Suleiman's of the 1540s, copied in 1960-62; the
# dome gilded again in 1993-94): the great octagon on the Haram's upper platform, its side 20.6m, its walls some 11.5m to the
# parapet -- marble to sill height, blue and white tile above -- under a low sloping roof, and rising through that the tiled DRUM of
# sixteen windows on its ring of 4 piers and 12 columns, and the DOME over it, gold, 20.4m across inside, its crown 35.5m over the floor.
#   Within: the outer ambulatory, the octagonal arcade (8 piers and 16 columns between the piers: drawn as arches in an octagonal wall),
#   the inner ambulatory, the circular arcade, the Rock itself. Four doors on the axes, each behind its porch; the south's is the great one.
#   Round it: a piece of the upper platform with its stairs and the free-standing arcades (qanatir, mawazin) at their heads, and to the
#   east the small Dome of the Chain. North is -z, east +x, the dome's axis at the origin. Numbers are worked here.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q, PI = math.pi / 2, math.pi
r3 = lambda v: round(v, 3)
POINTED = {"profile": "pointed", "spread": .3}

PH = 4.2                                         # the upper platform, over the esplanade
SIDE = 20.6                                      # the octagon's side
RC = SIDE / (2 * math.sin(PI / 8))               # ...its corner radius, 26.9m; 49.7m across the flats
AP = RC * math.cos(PI / 8)
WH, MARBLE, FRIEZE = 11.6, 5.2, 1.5              # the wall's height over the floor, the marble dado, the parapet's tiled band
T = 1.3                                          # its thickness
EAVE = WH - FRIEZE - .3                          # the roof's foot, inside the parapet
DR, DDT, DH = 10.2, 1.2, 9.6                     # the drum: the inner radius (the dome's 20.4m), its wall, its height
DY = 13.0                                        # its foot
Y = PH                                           # everything below is set on the platform's top

# ---- the octagon ------------------------------------------------------------------------------------------------------
BAY = {"pattern": "7", "width": 1.9, "gap": 1.0, "sill": .9, "springing": 3.0, "head": POINTED, "glass": True}
door = {"at": 0, "width": 3.2, "sill": 0, "springing": 4.0, "head": {"profile": "flat"}}
TIERS = [{"h": MARBLE, "openings": []}, {"h": WH - MARBLE - FRIEZE, "openings": BAY}, {"openings": []}]
DOOR_TIERS = [{"h": MARBLE, "openings": [door]}, {"h": WH - MARBLE - FRIEZE, "openings": BAY}, {"openings": []}]
add("octagon", {"type": "enclosure", "plan": {"sides": 8, "radius": r3(RC)}, "thickness": T, "height": WH, "tiers": TIERS,
                "faces": {str(k): DOOR_TIERS for k in (0, 2, 4, 6)}, "at": [[0, Y, 0, 0]],
                "_about": "the octagon, side 20.6m: a door on each axis, seven arched lights to a face over a marble dado, the parapet's tiled band"})
parts["ambulatory"] = {"type": "interior", "plan": {"sides": 8, "radius": r3(RC - T / 2 / math.cos(PI / 8))}, "height": r3(EAVE + 1.5), "at": [[0, Y, 0, 0]],
                       "_about": "the ambulatories and the space under the drum: within the octagon, up under its roof"}
# the low roof: a cone from the parapet's inside to the drum, its slope hidden from below by the parapet
RR = RC - T / math.cos(PI / 8)                   # (its foot: the wall's inner corners)
Rise = (DY - EAVE) / (1 - (DR + DDT) / RR)
add("roof", {"type": "dome", "sides": 8, "radius": r3(RR + .15), "thickness": .3, "oculus": r3(DR + DDT), "head": {"profile": "trigonal", "rise": r3(Rise)},
             "at": [[0, r3(Y + EAVE), 0, 0]], "_about": "the lead roof of the ambulatories, a low octagonal cone from the parapet to the drum"})

# ---- the arcades within --------------------------------------------------------------------------------------------------
RA = 18.6                                        # the octagonal arcade's corner radius
AH = 9.4
add("octagonal arcade", {"type": "enclosure", "plan": {"sides": 8, "radius": RA}, "thickness": .9, "height": AH,
                         "openings": {"pattern": "3", "width": 3.1, "gap": 1.1, "sill": 0, "springing": 5.4, "head": {"profile": "semicircular"}}, "glass": False, "at": [[0, Y, 0, 0]],
                         "_about": "the octagonal arcade between the two ambulatories: eight piers, two columns' arches between each (three arches to a side)"})
add("circular arcade", {"type": "ring", "count": 16, "rOuter": DR + DDT, "rInner": DR, "height": DY, "glass": False,
                        "opening": {"width": 2.9, "sill": 0, "springing": 7.0, "head": {"profile": "semicircular"}}, "place": [[0, Y, 0, 0]],
                        "_about": "the circular arcade under the drum: 4 piers and 12 columns in the real one, sixteen arches here"})
add("circular columns", {"type": "column", "radius": .42, "height": 7.0, "sides": 12, "at": [[r3((DR + DDT / 2) * math.sin(2 * PI * (k + .5) / 16)), Y, r3((DR + DDT / 2) * math.cos(2 * PI * (k + .5) / 16)), 0] for k in range(16)],
                         "_about": "the marble shafts between its arches"})
parts["under drum"] = {"type": "interior", "plan": {"sides": 16, "radius": DR + .1}, "height": r3(DY + DH), "at": [[0, Y, 0, 0]], "_about": "the space over the Rock, up the drum to the dome"}
add("rock", {"type": "prism", "plan": {"points": [[-7.5, -4.0], [-3.0, -7.0], [3.0, -7.4], [7.0, -5.0], [8.0, .5], [5.5, 5.5], [0, 7.2], [-5.0, 6.0], [-8.0, 1.5]]}, "height": 1.5,
             "batter": {"out": 1.2, "power": 1}, "at": [[0, Y, 0, 0]], "_about": "the Rock itself, under the dome"})

# ---- the drum and the dome --------------------------------------------------------------------------------------------------
PS = .08                                         # how far the dome's two arcs are spread: a gentle point
ah = DR + DDT                                    # its radius at the springing
h_dome = ah * math.sqrt(1 + 2 * PS)
add("great dome", comp("components/drum-dome", {"R": DR, "dt": DDT, "H": DH, "n": 16, "every": 1, "winW": 1.5, "winSill": 3.2, "winH": 3.4,
                                                "profile": "pointed", "spread": PS, "domeT": .6},
                       [[0, r3(Y + DY), 0, 0]], build=["drum", "dome"],
                       _about="the drum of sixteen windows, tiled, and the gold dome on it, slightly pointed: its crown 35.5m over the floor"))
TIPY = Y + DY + DH + h_dome
add("finial", {"type": "column", "radius": .22, "taper": .3, "height": 4.0, "sides": 8, "at": [[0, r3(TIPY - .3), 0, 0]], "_about": "the finial: a spike, two balls, the crescent"})
add("finial ball", {"type": "column", "radius": .5, "taper": .4, "height": .7, "sides": 10, "at": [[0, r3(TIPY + .5), 0, 0], [0, r3(TIPY + 1.5), 0, 0]]})
cy = TIPY + 3.6
add("crescent", {"type": "bars", "w": .16, "h": .22, "paths": [[[r3(.95 * math.cos(a)), r3(cy + .95 * math.sin(a)), 0] for a in [(-40 + 26 * k) * PI / 180 - PI * 0.0 + PI * 0.0 for k in range(0)]]
                                                              + [[r3(.95 * math.sin(a * PI / 180)), r3(cy + .95 * math.cos(a * PI / 180) + .95), 0] for a in range(150, 211 + 300 - 300, 12)]]})
parts["crescent"]["paths"] = [[[r3(1.0 * math.sin(math.radians(a))), r3(cy + .95 + 1.0 * math.cos(math.radians(a))), 0] for a in range(50, 311, 26)]]
parts["crescent"]["_about"] = "the crescent on its spike, open to the sky"

# ---- the four porches: one on each door, the south's the great one -------------------------------------------------------
def porch(nm, W, n, gapw, yaw):
    D, Hp = 3.2, 5.0
    sn, cs = math.sin(yaw), math.cos(yaw)
    fx, fz = AP + D, 0.0
    place = lambda d, a: [r3((AP + d) * sn), Y, r3((AP + d) * cs), r3(yaw)]
    add(f"{nm} porch front", {"type": "wall", "width": W, "height": Hp, "thickness": .5, "at": [place(D, 0)],
                              "openings": {"pattern": str(n), "width": gapw, "gap": r3((W - n * gapw) / (n + 1)), "sill": 0, "springing": 3.0, "head": POINTED},
                              **({"_about": "the porches: a vaulted bay in front of each door, an arcade to its front"} if nm == "south" else {})})
    ends = [[r3((AP + D / 2) * sn + s * (W / 2 - .25) * cs), Y, r3((AP + D / 2) * cs - s * (W / 2 - .25) * sn), r3(yaw + Q)] for s in (-1, 1)]
    add(f"{nm} porch ends", {"type": "box", "width": D, "length": .5, "height": Hp, "at": ends})
    add(f"{nm} porch roof", {"type": "box", "width": W + .4, "length": D + .3, "height": .5, "flatRoof": True, "at": [[r3((AP + D / 2) * sn), Y + Hp, r3((AP + D / 2) * cs), r3(yaw)]]})
porch("south", 15.0, 7, 1.4, 0.0)
porch("east", 8.0, 3, 1.5, Q)
porch("north", 8.0, 3, 1.5, PI)
porch("west", 8.0, 3, 1.5, -Q)

# ---- the upper platform ---------------------------------------------------------------------------------------------------
PX0, PX1, PZ0, PZ1 = -66.0, 74.0, -62.0, 62.0    # (cut to the buildings: the real one is some 160m by 130m)
NX, NZ = 7, 6
TW, TL = (PX1 - PX0) / NX, (PZ1 - PZ0) / NZ
add("platform", {"type": "box", "width": r3(TW), "length": r3(TL), "height": PH, "walked": True,
                 "at": [[r3(PX0 + TW * (i + .5)), 0, r3(PZ0 + TL * (j + .5)), 0] for i in range(NX) for j in range(NZ)],
                 "_about": "the Haram's upper platform: a stone terrace 4m over the esplanade, paved, laid in tiles so that no triangle of it is vast"})
build.remove("platform"); build.insert(0, "platform")
STEPS, RUN = 22, .34
FL = STEPS * RUN
def stair(nm, cx, cz, yaw, W):
    """a flight up to the platform's edge at (cx, cz), climbing the way yaw says"""
    sn, cs = math.sin(yaw), math.cos(yaw)        # (a flight climbs its local +x, across local -z of its placement: temple_of_heaven.py)
    add(f"{nm} stair", {"type": "flight", "width": W, "run": RUN, "steps": STEPS, "top": PH, "landing": 0,
                        "at": [[r3(cx + sn * W / 2 - cs * FL), 0, r3(cz + cs * W / 2 + sn * FL), r3(yaw)]]})
stair("south", 0.0, PZ1, Q, 16.0)
stair("north", 0.0, PZ0, -Q, 16.0)
stair("west", PX0, 0.0, 0.0, 16.0)
stair("east", PX1, 0.0, PI, 16.0)
def qanatir(nm, x, z, yaw, n, W):
    add(f"{nm} arcade", {"type": "wall", "width": W, "height": 7.2, "thickness": .9, "at": [[r3(x), PH, r3(z), r3(yaw)]],
                         "openings": {"pattern": str(n), "width": r3(W / n * .68), "gap": r3(W / n * .32), "sill": 0, "springing": 4.2, "head": POINTED},
                         **({"_about": "the qanatir (mawazin), free-standing arcades at the head of each stair, the scales on which they say souls will be weighed"} if nm == "south" else {})})
    add(f"{nm} arcade columns", {"type": "column", "radius": .3, "height": 4.2, "sides": 8,
                                 "at": [[r3(x + (W / 2 - (i + 0) * W / n) * math.cos(yaw)), PH, r3(z - (W / 2 - i * W / n) * math.sin(yaw)), 0] for i in range(1, n)]})
qanatir("south", 0.0, PZ1 - 4.0, 0.0, 4, 18.0)
qanatir("north", 0.0, PZ0 + 4.9, 0.0, 4, 18.0)
qanatir("west", PX0 + 4.45, 0.0, Q, 4, 18.0)
qanatir("east", PX1 - 4.45, 0.0, Q, 4, 18.0)

# ---- the Dome of the Chain, to the east -------------------------------------------------------------------------------------
CX, CR = 44.0, 7.5
add("chain outer columns", {"type": "colonnade", "plan": "round", "count": 11, "radius": CR, "columnR": .3, "height": 4.2, "at": [[CX, Y, 0, 0]],
                            "base": {"h": .2, "r": .36}, "capital": {"h": .35, "r": .36}, "_about": "the Dome of the Chain: eleven columns round six, under a low roof"})
add("chain outer lintel", {"type": "ring", "count": 11, "rOuter": CR + .4, "rInner": CR - .4, "height": .8, "solid": True, "polygon": True, "place": [[CX, r3(Y + 4.2), 0, 0]]})
add("chain drum", {"type": "ring", "count": 6, "rOuter": 3.4, "rInner": 3.0, "height": 8.5, "polygon": True, "glass": False,
                   "opening": {"width": 2.2, "sill": 0, "springing": 3.4, "head": POINTED}, "place": [[CX, Y, 0, 0]], "_about": "its hexagonal core, arches below, tiled above"})
add("chain roof", {"type": "dome", "sides": 11, "radius": CR + .8, "thickness": .25, "oculus": 3.4, "head": {"profile": "trigonal", "rise": 2.6}, "at": [[CX, r3(Y + 5.0), 0, 0]]})
add("chain dome", {"type": "dome", "radius": 3.4, "thickness": .25, "head": {"profile": "pointed", "spread": .15}, "sides": 16, "at": [[CX, r3(Y + 8.5), 0, 0]], "_about": "its small lead dome"})

doc = {"name": "Dome of the Rock",
       "_about": "THE DOME OF THE ROCK, Jerusalem (691-92; Suleiman's tiles, the gilding of 1993-94): the octagon of side 20.6m, marble under blue tile, four porched doors, the low lead roof; the tiled drum of sixteen "
                 "windows on its circular arcade; the gold dome, its crown 35.5m over the floor; within, the octagonal arcade and the Rock; round it the upper platform, its stairs and the free-standing qanatir, "
                 "and the Dome of the Chain. Generated by tools/archgen/dome_of_the_rock.py -- edit the script for arithmetic changes. North is -z, east +x.",
       "params": {"detail": 4}, "railing": {"type": "stone"}, "build": build, "parts": parts}
out = os.path.join(ROOT, "assets", "architecture", "dome-of-the-rock.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts; dome crown", round(Y + DY + DH + h_dome - Y, 2), "over the floor")
