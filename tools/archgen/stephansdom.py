# THE STEPHANSDOM, Vienna (Gothic, 1304-1511), from components: a HALL CHURCH -- nave and aisles of one height under
# groin vaults on two rows of piers -- under the great steep roof of patterned tiles; the choir beyond it with its
# polygonal apse; the SOUTH TOWER (the Steffl) beside the nave, square in two stages and then an octagon and its
# spire to 136m, climbed by a `tower-stair` to its first floor; the unfinished NORTH TOWER under its Renaissance cap,
# climbed the same way; the west front between the two octagonal HEATHEN TOWERS, the Giant's Door in it.
#   The west front faces +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2

# ---- THE CHURCH AS ITS STRUCTURE: the `basilica` part as a HALL (arch/gothic.js): nave and aisles vaulted from the
# same capitals -- the aisles' keystones 3m under the nave's (a stepped hall) -- one line of piers a side running on
# round the choir's polygon into an ambulatory, tall windows in the outer wall under the aisle vaults, a deep stepped
# buttress with its pinnacle at every bay and every corner of the apse, and ONE roof over all three vessels
BAYS, BAY = 10, 9.2                        # nave and Albertine choir, west front to the apse
NW, AW, T, TA = 12.0, 10.0, 1.4, 1.6       # the arcade's centre lines apart, pier line to wall line, the walls
SPR, PITCH, OV = 20.0, 62, 0.6
L = BAYS * BAY                             # the straight bays: z from +L/2 (west) to -L/2, the apse beyond
OUT = NW / 2 + AW + TA / 2                 # the outer wall's face
CROWN = SPR + (NW / 2 - T / 2) * 1.7321 * 0.9
WALLTOP = CROWN + 0.5 + 0.3
RIDGE = WALLTOP + (OUT + OV) * math.tan(math.radians(PITCH))
add("church", {"type": "basilica", "hall": True, "bays": BAYS, "bayLen": BAY, "naveW": NW, "aisleW": AW, "t": T, "aisleT": TA,
               "apse": 5, "spring": SPR, "aisleDrop": 3.0, "pierR": 0.95, "shaft": 0.3, "pitch": PITCH, "overhang": OV,
               "aisleSill": 6.0, "aisleWin": 3.2, "buttressW": 1.8, "buttressD": 3.4, "skipButtress": [[6, 6]], "wimpergs": True, "at": [[0, 0, 0, 0]],
               "_about": "nave and choir as one HALL: piers, arcades, rib vaults over nave, aisles and ambulatory at nearly one height, the outer walls with their tall windows, a stepped buttress and pinnacle at every bay and round the apse, one steep roof over all"})
# THE WEST FRONT across the hall's open west end, its back on it: the Giant's Door, the great window over it, and the
# GABLE over the eave, cut to the roof's own pitch (two halves, each a mass whose top falls with the roof)
FW = 2 * OUT
add("west front", {"type": "wall", "width": FW, "height": round(WALLTOP, 4), "thickness": 3.0, "at": [[0, 0, L / 2 + 3.0, 0]],
                   "tiers": [{"h": 17, "openings": [{"at": 0, "width": 6.0, "sill": 0, "springing": 9.0, "head": {"profile": "semicircular"}}]},
                             {"openings": [{"at": 0, "width": 6.0, "sill": 1.0, "springing": round(WALLTOP - 17 - 4.5 - 3 * 1.7321, 4), "head": {"profile": "pointed", "spread": 1.0}, "tracery": True}]}],
                   "_about": "the west front: the Romanesque Giant's Door, and the great window over it"})
GH = RIDGE - WALLTOP                       # the gable's height over the eave, at its middle
add("west gable", {"type": "prism", "plan": {"rect": [OUT, 3.0]}, "height": round(GH - OUT / 2 * math.tan(math.radians(PITCH)), 4),
                   "slope": [round(-math.tan(math.radians(PITCH)), 5), 0], "at": [[OUT / 2, round(WALLTOP, 4), L / 2 + 1.5, 0], [-OUT / 2, round(WALLTOP, 4), L / 2 + 1.5, round(math.pi, 6)]],
                   "_about": "the west gable over the front, its two halves falling with the roof"})

# ---- the towers beside the hall, where the transept would be: the south one (+x) and the north one (-x)
TW, TT = 14.0, 2.0
tz = L / 2 - 6 * BAY                       # on the sixth node from the west, where the choir begins (no buttress there)
stage = lambda w, h, y, x, **kw: {"type": "enclosure", "plan": {"rect": [w, w]}, "thickness": TT, "height": h, "at": [[x, y, tz, 0]], **kw}
SX = OUT + TW / 2
add("south tower", stage(TW, 40.0, 0, SX, tiers=[{"h": 16, "openings": []}, {"openings": {"pattern": "1", "width": 2.4, "sill": 8.0, "springing": 17.0,
                                                                                       "head": {"profile": "pointed", "spread": 1.0}}}],
                          faces={"2": [{"h": 16, "openings": [{"at": 0, "width": 3.0, "sill": 0, "springing": 5.0, "head": {"profile": "pointed", "spread": 1.0}}]},
                                       {"openings": {"pattern": "1", "width": 2.4, "sill": 8.0, "springing": 17.0, "head": {"profile": "pointed", "spread": 1.0}}}]},
                          _about="the south tower, the Steffl: its square foot, a door in it..."))
add("south tower stair", comp("components/tower-stair", {"W": TW - 2 * TT, "H": 40.0}, [[SX, 0, tz, 0]],
                              _about="...climbed by its stair to the floor at the top of the square foot..."))
add("south tower stage", {**stage(12.0, 22.0, 40.0, SX, glass=False, openings={"pattern": "1", "width": 2.2, "sill": 4.0, "springing": 15.0,
                                                                         "head": {"profile": "pointed", "spread": 1.0}},
                               _about="...the second, narrower stage, with the room the stair arrives in (its walls thin, clear of the stair's head)..."), "thickness": 1.0})
add("south tower spire", comp("components/domed-tower", {"sides": 8, "R": 6.0, "H": 16.0, "t": 1.0, "drumR": 4.6, "drumH": 3.0, "cap": "trigonal",
                                                         "capRise": 50.0, "capR": 5.0, "kok": 1.4, "finial": 4.0, "winW": 1.6, "glazed": 0},
                              [[SX, 62.0, tz, 0]], build=["tower", "kokoshniki", "neck", "drum", "cap", "finial"],
                              _about="...and the octagon with its gables, and the spire to 136m"))
add("north tower", stage(TW, 50.0, 0, -SX, tiers=[{"h": 16, "openings": []}, {"openings": {"pattern": "1", "width": 2.4, "sill": 8.0, "springing": 20.0,
                                                                                         "head": {"profile": "pointed", "spread": 1.0}}}],
                          faces={"2": [{"h": 16, "openings": [{"at": 0, "width": 3.0, "sill": 0, "springing": 5.0, "head": {"profile": "pointed", "spread": 1.0}}]},
                                       {"openings": {"pattern": "1", "width": 2.4, "sill": 8.0, "springing": 20.0, "head": {"profile": "pointed", "spread": 1.0}}}]},
                          _about="the north tower, left unfinished at 68m..."))
add("north tower stair", comp("components/tower-stair", {"W": TW - 2 * TT, "H": 50.0}, [[-SX, 0, tz, Q]],
                              _about="...climbed the same way, to the Pummerin's floor..."))
add("north tower cap", comp("components/domed-tower", {"sides": 4, "R": TW / 2 * 1.4142, "H": 5.0, "t": 1.0, "drumR": 3.6, "drumH": 3.0, "cap": "bell",
                                                       "capR": 4.4, "waist": 0.75, "lift": 1.0, "kok": 0.8, "finial": 2.5, "winW": 1.2, "glazed": 0},
                            [[-SX, 50.0, tz, 0]], build=["tower", "drum", "cap", "finial"],
                            _about="...its belfry room, where the stair arrives, under its Renaissance cap"))

# ---- the west front's two Heathen Towers
add("heathen towers", comp("components/domed-tower", {"sides": 8, "R": 3.4, "H": 40.0, "t": 0.8, "drumR": 2.6, "drumH": 3.0, "cap": "trigonal",
                                                      "capRise": 16.0, "capR": 3.0, "kok": 0.8, "finial": 2.0, "winW": 1.0, "glazed": 0, "doorH": 3.0},
                           [[sx * 6.6, 0, L / 2 + 3.0 + 3.2, 0] for sx in (-1, 1)], build=["tower", "kokoshniki", "drum", "cap", "finial"],
                           _about="the two Heathen Towers either side of the Giant's Door, octagons under stone spires"))

doc = {"name": "Stephansdom",
       "_about": "THE STEPHANSDOM, Vienna, from components: a HALL CHURCH -- nave and aisles one height, groin-vaulted on two rows of piers -- under the great steep roof of patterned tiles; the choir and its polygonal apse under a half cone; the SOUTH TOWER, square in two stages, then the gabled octagon and the spire to 136m (`domed-tower`), a `tower-stair` up its square foot; the unfinished NORTH TOWER under its Renaissance cap, climbed the same way; and the west front with the Giant's Door and the great window between the two octagonal HEATHEN TOWERS.",
       "params": {"detail": 4}, "base": {"height": 0.6, "steps": 2, "stepOut": 0.5, "margin": 3}, "railing": {"type": "stone"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/stephansdom.json"), "w").write(json.dumps(doc, indent=2) + "\n")
