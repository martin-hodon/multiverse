# SACRE-COEUR, Montmartre (1875-1914), Romano-Byzantine, from components: a Greek cross of four arms round a square
# crossing, PENDENTIVES in the crossing carrying a colonnaded drum and the tall dome with its lantern; a small domed
# tower in each of the four angles between the arms; the apse; the three-arched porch with its two statues; the
# square campanile behind the apse; the whole on a raised terrace. The roofs are flat and walked on, all the way
# round the drum -- a stair turret climbs to them, as visitors do.
#   The front faces +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2

C, T, AH = 22.0, 1.6, 24.0                 # the crossing square, the walls, the arms' height (and the roof walk's)
A = C / 2
arch = lambda w, spring: {"at": 0, "width": w, "sill": 0, "springing": spring, "head": {"profile": "semicircular"}}
win2 = [{"h": 12, "openings": {"pattern": "2", "width": 2.4, "gap": 5.0, "sill": 3.5, "springing": 9.0, "head": {"profile": "semicircular"}}},
        {"openings": {"pattern": "3", "width": 1.8, "gap": 3.2, "sill": 2.5, "springing": 8.0, "head": {"profile": "semicircular"}}}]

# ---- the crossing and its four arms (faces: 0 +z, 1 +x, 2 -z, 3 -x); each arm opens into the crossing by a great arch
add("crossing", {"type": "enclosure", "plan": {"rect": [C, C]}, "thickness": T, "height": AH, "openings": [arch(14.0, 10.0)],
                 "at": [[0, 0, 0, 0]], "_about": "the crossing: a great arch into each arm"})
NL, TL, CL = 26.0, 16.0, 12.0              # the nave arm, the transept arms, the choir arm
add("nave arm", {"type": "enclosure", "plan": {"rect": [C, NL]}, "thickness": T, "height": AH, "tiers": win2,
                 "faces": {"2": [arch(14.0, 10.0)], "0": [{"h": 12, "openings": [arch(5.0, 7.0)]},
                                                          {"openings": [{"at": 0, "width": 7.0, "sill": 4.5, "springing": 4.5, "head": {"profile": "semicircular"}, "foot": {"profile": "semicircular"}}]}]},
                 "at": [[0, 0, A + NL / 2, 0]], "_about": "the nave arm: the portal and a rose in its front"})
for sx, nm, inner in ((1, "east", "3"), (-1, "west", "1")):
    add(f"{nm} transept", {"type": "enclosure", "plan": {"rect": [TL, C]}, "thickness": T, "height": AH, "tiers": win2, "faces": {inner: [arch(14.0, 10.0)]},
                           "at": [[sx * (A + TL / 2), 0, 0, 0]], **({"_about": "the transept arms"} if sx > 0 else {})})
win1 = [{"h": 12, "openings": [{"at": 0, "width": 2.4, "sill": 3.5, "springing": 9.0, "head": {"profile": "semicircular"}}]},
        {"openings": [{"at": 0, "width": 1.8, "sill": 2.5, "springing": 8.0, "head": {"profile": "semicircular"}}]}]
add("choir arm", {"type": "enclosure", "plan": {"rect": [C, CL]}, "thickness": T, "height": AH, "tiers": win1,
                  "faces": {"0": [arch(14.0, 10.0)], "2": [arch(C - 2 * T - 1.0, 12.0)]}, "at": [[0, 0, -A - CL / 2, 0]],
                  "_about": "the choir arm, open at its end into the apse"})
AR = C / 2 - T                             # the apse: a half ring off the choir's end, and its half dome
APH = AH - AR - T - 0.6                    # the apse lower than the choir: its half dome's face is closed by the choir's end wall
add("apse", {"type": "component", "use": "components/apse",
             "params": {"R": AR, "T": T, "H": APH, "n": 16, "winW": 2.0, "winSill": 2.5, "winH": 4.5, "domeT": T},
             "at": [[0, 0, -A - CL, math.pi]], "_about": "the apse, lower than the choir: its half dome rises into the choir's end wall, not above it"})

# ---- the flat roofs, walked on (over the arms, on their walls' tops)
S = 0.4
add("nave roof", {"walked": True, "type": "box", "width": C, "length": NL, "height": S, "at": [[0, AH, A + NL / 2, 0]],
                  "_about": "the flat roofs over the arms: a walk round the drum"})
add("transept roofs", {"walked": True, "type": "box", "width": TL, "length": C, "height": S, "at": [[sx * (A + TL / 2), AH, 0, 0] for sx in (-1, 1)]})
add("choir roof", {"walked": True, "type": "box", "width": C, "length": CL, "height": S, "at": [[0, AH, -A - CL / 2, 0]]})

# ---- the dome: pendentives, the roof round the drum, the colonnaded drum, the dome and its lantern
DR = C / 2 - T                             # the pendentives' circle: the drum's inside
add("pendentives", {"walked": True, "type": "pendentives", "span": C - 2 * T, "springing": AH - DR, "sides": 24, "at": [[0, 0, 0, 0]], "deck": {"thickness": S, "out": T},
                    "_about": "the pendentives inside the crossing, turning its square into the drum's circle, and the roof round the drum's foot"})
DH, DT = 14.0, 1.0
add("dome", comp("components/drum-dome", {"R": DR, "dt": DT, "H": DH, "n": 24, "every": 1, "winW": 1.4, "winSill": 3.5, "winH": 7.0,
                                          "profile": "pointed", "spread": 0.55, "domeT": DT, "lanternR": 2.8, "lanternH": 6.0},
                 [[0, AH, 0, 0]], build=["drum", "dome", "lantern"],
                 _about="the drum, a window in every bay -- a colonnade of light -- the tall pointed dome and its lantern"))

# ---- a small domed tower in each angle between the arms
SR = 3.6
add("small domes", comp("components/domed-tower", {"sides": 8, "R": SR, "H": AH + 6.0, "t": 0.8, "drumR": 2.6, "drumH": 3.0, "cap": "onion",
                                                    "bulge": 1.05, "neck": 0.9, "capR": 2.8, "kok": 0.5, "finial": 2.0, "doorH": 3.0, "winW": 0.9},
                        [[sx * (A + SR * 0.92), 0, sz * (A + SR * 0.92), 0] for sx in (-1, 1) for sz in (-1, 1) if not (sx < 0 and sz < 0)],
                        build=["tower", "drum", "cap", "finial"],
                        _about="three small domed towers in the angles between the arms (the fourth angle holds the stair turret)"))
# ---- the stair tower to the roofs, in the fourth angle (`round-stair-tower`): its door to the south-west, outside,
# and 126 steps chosen so its spiral arrives facing the crossing's corner (exit bay 1 of 12), out onto a small terrace in
# the angle that joins the choir's roof and the transept's
TR = 3.0
tx = tz = -(A + TR - 0.05)
add("stair tower", comp("components/round-stair-tower", {"R": TR, "H": AH + S, "steps": 126, "doorBay": 7, "stageH": 3.2, "capRise": 4.0},
                        [[tx, 0, tz, 0]], _about="the stair tower in the fourth angle: a spiral from the ground up to the roofs, under its belvedere and cone"))
add("angle terrace", {"walked": True, "type": "box", "width": 1.9, "length": 1.0, "height": 0.6, "at": [[-(A + 0.95), AH - 0.2, -(A + 0.5), 0]],
                      "_about": "the little terrace in the angle, level with the roofs, from the stair tower's door to the choir's roof and the transept's"})

# ---- the porch and the campanile
PZ, PD, PH = A + NL, 7.0, 13.0
add("porch front", {"type": "wall", "width": C, "height": PH, "thickness": 1.4, "at": [[0, 0, PZ + PD, 0]],
                    "openings": {"pattern": "3", "width": 4.4, "gap": 2.6, "sill": 0, "springing": 7.5, "head": {"profile": "semicircular"}},
                    "_about": "the porch: three arches under the rose"})
add("porch sides", {"type": "wall", "width": PD - 1.4, "height": PH, "thickness": 1.4,
                    "openings": [{"at": (PD - 1.4) / 2, "width": 2.4, "sill": 0, "springing": 6.0, "head": {"profile": "semicircular"}}],
                    "at": [[sx * A + (1.4 if sx < 0 else 0), 0, PZ + (PD - 1.4) / 2, Q] for sx in (-1, 1)]})
add("porch roof", {"type": "box", "width": C, "length": PD, "height": 0.6, "at": [[0, PH, PZ + PD / 2, 0]]})
for sx, saint in ((-1, {"kind": "woman", "seed": 12}), (1, {"kind": "man", "seed": 31})):
    add("statue " + ("Joan" if sx < 0 else "Louis"), comp("components/pedestal", {"W": 1.6, "L": 2.0, "H": 2.2, "scale": 2.0, "stone": "bronze", "style": "gothic",
                                                                          "holdR": "items/weapons/sword", **saint},
                                                    [[sx * (A - 1.6), PH + 0.6, PZ + PD - 2.0, 0]],
                                                    **({"_about": "the two saints over the porch, Joan of Arc and Saint Louis, in bronze on their pedestals"} if sx < 0 else {})))
add("campanile", comp("components/domed-tower", {"sides": 4, "R": 5.5 * 1.4142, "H": 54.0, "t": 1.2, "drumR": 3.6, "drumH": 5.0, "cap": "onion",
                                                 "bulge": 1.05, "neck": 0.9, "capR": 4.0, "kok": 0.8, "finial": 4.0, "doorH": 4.0, "winW": 1.4, "glazed": 0},
                      [[0, 0, -A - CL - AR - T - 5.4, Q]], build=["tower", "drum", "cap", "finial"],
                      _about="the campanile behind the apse, the great bell (the Savoyarde) in its open belfry"))

doc = {"name": "Sacre-Coeur",
       "_about": "THE BASILICA OF SACRE-COEUR, Montmartre (1875-1914), Romano-Byzantine, in white travertine: a Greek cross of four arms round a square crossing where PENDENTIVES carry a drum windowed in every bay and the tall pointed dome with its lantern; a small domed tower in three of the angles between the arms, and in the fourth the stair turret up to the flat roofs, which are walked all the way round the drum; the apse and its half dome; the three-arched porch with its two statues; the square campanile behind the apse; the whole on a terrace up a flight of steps.",
       "params": {"detail": 4}, "base": {"height": 2.4, "steps": 8, "stepOut": 0.5, "margin": 4}, "railing": {"type": "iron"}, "build": build, "parts": parts}
path = os.path.join(ROOT, "assets/architecture/sacre-coeur.json")
open(path, "w").write(json.dumps(doc, indent=2) + "\n")
