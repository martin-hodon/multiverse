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

W, L, T, WH = 36.0, 76.0, 1.8, 28.0        # the hall: width, length, walls, their height
BAYS = 8
IN = L - 2 * T
BAY = IN / BAYS
NW = 11.0                                  # the nave, between the pier rows
AW = (W - 2 * T - NW) / 2                  # each aisle
SPR, TOP = 17.0, 25.5                      # the vaults' springing and crown
lancets = {"pattern": "7", "width": 2.4, "gap": BAY - 2.4, "sill": 5.0, "springing": 16.0, "head": {"profile": "pointed", "spread": 1.0}}
add("hall", {"type": "enclosure", "plan": {"rect": [W, L]}, "thickness": T, "height": WH, "openings": lancets,
             "faces": {"0": [{"h": 17, "openings": [{"at": 0, "width": 6.0, "sill": 0, "springing": 9.0, "head": {"profile": "semicircular"}}]},
                             {"openings": [{"at": 0, "width": 6.0, "sill": 1.0, "springing": 4.6, "head": {"profile": "pointed", "spread": 1.0}}]}],
                       "2": [{"at": 0, "width": 18.0, "sill": 0, "springing": 12.0, "head": {"profile": "pointed", "spread": 0.6}}]},
             "at": [[0, 0, 0, 0]],
             "_about": "the hall: tall lancets down both flanks, the Giant's Door and the great window over it in the west front, and the east end open by a great arch into the choir"})
add("piers", {"type": "column", "radius": 0.9, "height": SPR, "sides": 12,
              "at": [[sx * NW / 2, 0, L / 2 - T - BAY * k, 0] for sx in (-1, 1) for k in range(1, BAYS)],
              "_about": "two rows of piers down the hall"})
for nm, cx, w in (("nave vaults", 0.0, NW), ("aisle vaults", NW / 2 + AW / 2, AW)):
    add(nm, {"type": "groin", "width": w, "length": BAY, "springing": SPR, "top": TOP, "head": {"profile": "pointed", "spread": 0.6},
             "at": [[sx * cx, 0, L / 2 - T - BAY / 2 - BAY * k, 0] for sx in ((1,) if cx == 0 else (-1, 1)) for k in range(BAYS)],
             **({"_about": "groin vaults over nave and aisles, all at one height: a hall church"} if cx == 0 else {})})
add("hall ceiling", {"type": "box", "width": W - 2 * T, "length": IN, "height": 0.4, "at": [[0, WH - 0.4, 0, 0]],
                     "_about": "the floor of the roof space, over the vaults"})
add("roof", {"type": "roof", "form": "gable", "width": W + 1.0, "length": L, "pitch": 58, "overhang": 0.6, "at": [[0, WH, 0, 0]],
             "_about": "the great roof, 38m of steep patterned tiles"})

# ---- the choir and its apse
CW, CL = 30.0, 22.0
add("choir", {"type": "enclosure", "plan": {"rect": [CW, CL]}, "thickness": T, "height": WH - 2.0,
              "openings": {"pattern": "3", "width": 2.4, "gap": 4.0, "sill": 5.0, "springing": 15.0, "head": {"profile": "pointed", "spread": 1.0}},
              "faces": {"0": [{"at": 0, "width": 18.0, "sill": 0, "springing": 12.0, "head": {"profile": "pointed", "spread": 0.6}}],
                        "2": [{"at": 0, "width": CW - 2 * T - 1.0, "sill": 0, "springing": 8.0, "head": {"profile": "pointed", "spread": 0.3}}]},
              "at": [[0, 0, -L / 2 - CL / 2, 0]], "_about": "the Albertine choir, a hall of its own, open to the nave and to its apse"})
AR = CW / 2 - T
add("apse", {"type": "component", "use": "components/apse",
             "params": {"R": AR, "T": T, "H": WH - 2.0, "n": 16, "winW": 2.2, "winSill": 5.0, "winH": 10.0, "winHead": "pointed",
                        "profile": "trigonal", "rise": 24.0, "domeT": 0, "over": 0.5},
             "at": [[0, 0, -L / 2 - CL, math.pi]], "_about": "the apse, a tall lancet in each bay, under the half cone of its roof (`apse`)"})
add("choir roof", {"type": "roof", "form": "gable", "width": CW + 1.0, "length": CL, "pitch": 58, "overhang": 0.5, "at": [[0, WH - 2.0, -L / 2 - CL / 2, 0]]})

# ---- the towers beside the hall, where the transept would be: the south one (+x) and the north one (-x)
TW, TT = 14.0, 2.0
tz = -L / 2 + 20.0
stage = lambda w, h, y, x, **kw: {"type": "enclosure", "plan": {"rect": [w, w]}, "thickness": TT, "height": h, "at": [[x, y, tz, 0]], **kw}
SX = W / 2 + TW / 2
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
                           [[sx * (W / 2 - 2.6), 0, L / 2 - 1.6, 0] for sx in (-1, 1)], build=["tower", "kokoshniki", "drum", "cap", "finial"],
                           _about="the two Heathen Towers either side of the Giant's Door, octagons under stone spires"))

doc = {"name": "Stephansdom",
       "_about": "THE STEPHANSDOM, Vienna, from components: a HALL CHURCH -- nave and aisles one height, groin-vaulted on two rows of piers -- under the great steep roof of patterned tiles; the choir and its polygonal apse under a half cone; the SOUTH TOWER, square in two stages, then the gabled octagon and the spire to 136m (`domed-tower`), a `tower-stair` up its square foot; the unfinished NORTH TOWER under its Renaissance cap, climbed the same way; and the west front with the Giant's Door and the great window between the two octagonal HEATHEN TOWERS.",
       "params": {"detail": 4}, "base": {"height": 0.6, "steps": 2, "stepOut": 0.5, "margin": 3}, "railing": {"type": "stone"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/stephansdom.json"), "w").write(json.dumps(doc, indent=2) + "\n")
