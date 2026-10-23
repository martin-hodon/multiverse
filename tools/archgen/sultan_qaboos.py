# THE SULTAN QABOOS GRAND MOSQUE, Muscat (2001), from components -- simplest first:
#   crenellation   a parapet with its row of stepped Omani merlons
#   arcade-walk    a riwaq: a row of pointed arches on piers, a back wall (or a second row), a flat roof, crenellations
#                  on both edges (a `crenellation` each)
#   portal         a monumental iwan-like entrance: a deep frame whose reveal is the recess, the `iwan` back closing
#                  it with the door through, crenellated on top, slender octagonal shafts at its front corners
#   omani-minaret  a square shaft turning octagonal, balconies on corbelling, an open lantern and a small pointed dome
# and the mosque from them: on its platform, the sahn enclosed by four `arcade-walk`s, gated through `portal`s; the
# prayer hall -- a square of lower flat-roofed bays round the crossing, whose four piers and arches carry pendentives
# and the tall drum (`drum-dome`) and the gilded dome; its entrance `portal`s; the women's prayer hall with its own
# small dome and portal; the great minaret and four smaller ones on the complex's corners.
#   The courtyard front faces +z; the hall stands at the -z end. This script writes the components too.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMP = os.path.join(ROOT, "assets/architecture/components")
Q = math.pi / 2
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}

def write(path, doc):
    open(path, "w").write(json.dumps(doc, indent=2) + "\n")

# ================================================================= components
write(os.path.join(COMP, "crenellation.json"), {
  "name": "Crenellation",
  "_about": "A CRENELLATED PARAPET: a low wall `L` long, `t` thick and `h` tall, centred on its placement along x, and on it a row of MERLONS every `step` metres, each stepped (a smaller block on a larger -- the Omani and Persian kind); build it without \"merlon tops\" for plain square merlons, or without \"parapet\" to set the merlons straight on a wall's head.",
  "params": {"detail": 4, "L": 20, "t": 0.5, "h": 0.9, "step": 2.0, "mw": "step * 0.45", "mh": 0.8, "n": "max(1, floor(L / step))",
             "_n": "how many merlons: as many whole steps as the parapet holds, the row centred on it"},
  "build": ["parapet", "merlons", "merlon tops"],
  "parts": {
    "parapet": {"type": "box", "width": "L", "length": "t", "height": "h", "at": [[0, 0, 0, 0]]},
    "merlons": {"type": "box", "width": "mw", "length": "t", "height": "mh", "at": [["0 - (n - 1) * step / 2", "h", 0, 0]],
                "repeat": {"count": "n", "step": ["step", 0, 0, 0]}, "_about": "the merlons, centred on the parapet"},
    "merlon tops": {"type": "box", "width": "mw * 0.5", "length": "t", "height": "mh * 0.6", "at": [["0 - (n - 1) * step / 2", "h + mh", 0, 0]],
                    "repeat": {"count": "n", "step": ["step", 0, 0, 0]}, "standsOn": ["merlons"], "_about": "the step on each merlon"}}})

write(os.path.join(COMP, "arcade-walk.json"), {
  "name": "Arcade walk",
  "_about": "A COVERED WALK -- a riwaq, a cloister walk, a stoa: `L` long along x and `D` deep, its FRONT (+z) a row of arches on piers (`bay` apart, the piers `pw` wide, `n` of them centred on the length, their head any profile: `arch`, with `spread` for a pointed one), its back a blind wall (\"back wall\"), a wall with a gate in its middle (\"back gate\", `gw` wide) or a second row of arches (\"back arcade\": open on both sides). Over it a flat roof slab `slab` thick on walls `H` tall, and a `crenellation` along each long edge. Its ends are open, to run on into whatever it meets. Placed by the middle of its floor, facing +z.",
  "params": {"detail": 4, "L": 40, "D": 7, "H": 8, "t": 0.9, "bay": 4.5, "pw": 1.2, "arch": "pointed", "spread": 0.5, "slab": 0.6,
             "n": "max(1, floor(L / bay))", "w": "bay - pw", "s": "H - 1.0 - w / 2 * sqrt(1 + 2 * spread)",
             "gw": 3.6, "gs": "H - 1.4 - gw / 2 * sqrt(1 + 2 * spread)", "ph": 0.8, "mstep": 2.4, "pt": 0.5,
             "_s": "the arches' springing: a metre of wall over the crown of a pointed arch of `spread` (the crown of any other head is lower)",
             "_gw": "the back gate's width, `gs` its springing", "_ph": "the parapets' height, `mstep` their merlons' spacing, `pt` their thickness"},
  "build": ["front", "back wall", "roof", "front parapet", "back parapet"],
  "parts": {
    "front": {"type": "wall", "width": "L", "height": "H", "thickness": "t", "glass": False,
              "openings": {"pattern": "n", "width": "w", "gap": "pw", "pier": "pw", "sill": 0, "springing": "s", "head": {"profile": "arch", "spread": "spread"}},
              "at": [[0, 0, "D / 2", 0]], "_about": "the row of arches on its piers, open to the court"},
    "back wall": {"type": "wall", "width": "L", "height": "H", "thickness": "t", "openings": [], "at": [[0, 0, "t - D / 2", 0]],
                  "_about": "the blind back wall (the outer wall of a court)"},
    "back gate": {"type": "wall", "width": "L", "height": "H", "thickness": "t", "glass": False,
                  "openings": [{"at": "L / 2", "width": "gw", "sill": 0, "springing": "gs", "head": {"profile": "arch", "spread": "spread"}}],
                  "at": [[0, 0, "t - D / 2", 0]], "_about": "the back wall with a gate through its middle"},
    "back arcade": {"type": "wall", "width": "L", "height": "H", "thickness": "t", "glass": False,
                    "openings": {"pattern": "n", "width": "w", "gap": "pw", "pier": "pw", "sill": 0, "springing": "s", "head": {"profile": "arch", "spread": "spread"}},
                    "at": [[0, 0, "t - D / 2", 0]], "_about": "a second row of arches for a walk open on both sides"},
    "roof": {"type": "box", "width": "L", "length": "D", "height": "slab", "at": [[0, "H", 0, 0]], "flatRoof": True, "_about": "the flat roof"},
    "front parapet": comp("components/crenellation", {"L": "L", "t": "pt", "h": "ph", "step": "mstep"}, [[0, "H + slab", "D / 2 - pt / 2", 0]],
                          standsOn=["roof"], _about="the crenellated parapet along the front edge"),
    "back parapet": comp("components/crenellation", {"L": "L", "t": "pt", "h": "ph", "step": "mstep"}, [[0, "H + slab", "pt / 2 - D / 2", 0]],
                         standsOn=["roof"])}})

write(os.path.join(COMP, "portal.json"), {
  "name": "Portal",
  "_about": "A MONUMENTAL PORTAL, iwan-like (a pishtaq): a frame `W` wide and `Hh` tall, `D` deep, standing out from a building's face -- its back on the placement's plane (z = 0), its front at z = D, facing +z. Its opening (`w` wide, springing at `s`, pointed by `spread`) goes right through, so the reveal is the recess and the arch head its vault; the `iwan` component closes it at the back with its half cylinder and semidome, `door` wide through its middle bay (by default as wide as the iwan's middle bay allows) (the building behind wants its own door there). A `crenellation` along the top, and a slender octagonal shaft with a small cap at each front corner. `D` must exceed w / 2 + it (the iwan's radius).",
  "params": {"detail": 4, "W": 16, "Hh": 18, "D": 7, "w": 8, "s": 8, "spread": 0.5, "it": 0.6, "door": "min(3.2, (w / 2 + it) * 0.5 - 0.25)",
             "sr": "W * 0.03 + 0.25", "sh": "Hh + 2.5", "_sr": "the corner shafts' radius and height"},
  "build": ["frame", "iwan", "crenellation", "shafts", "shaft caps"],
  "parts": {
    "frame": {"type": "wall", "width": "W", "height": "Hh", "thickness": "D", "glass": False,
              "openings": [{"at": "W / 2", "width": "w", "sill": 0, "springing": "s", "head": {"profile": "pointed", "spread": "spread"}}],
              "at": [[0, 0, "D", 0]], "_about": "the frame: its reveal is the recess, its pointed head the recess's vault"},
    "iwan": comp("components/iwan", {"w": "w", "s": "s", "spread": "spread", "t": "it", "door": "door"}, [[0, 0, "w / 2 + it", 0]],
                 build=["back", "back door", "hood"], _about="the recess's back: half cylinder and semidome, the door in its middle bay"),
    "crenellation": comp("components/crenellation", {"L": "W", "t": 0.6, "h": 0.6, "step": 2.0}, [[0, "Hh", "D - 0.3", 0]], standsOn=["frame"]),
    "shafts": {"type": "column", "radius": "sr", "height": "sh", "sides": 8, "at": [["0 - W / 2 + sr", 0, "D + sr * 0.5", 0], ["W / 2 - sr", 0, "D + sr * 0.5", 0]],
               "_about": "the slender shafts at the frame's front corners, rising over it"},
    "shaft caps": {"type": "dome", "radius": "sr * 1.3", "sides": 8, "thickness": 0, "head": {"profile": "pointed", "spread": 0.6},
                   "at": [["0 - W / 2 + sr", "sh", "D + sr * 0.5", 0], ["W / 2 - sr", "sh", "D + sr * 0.5", 0]], "standsOn": ["shafts"]}}})

write(os.path.join(COMP, "omani-minaret.json"), {
  "name": "Omani minaret",
  "_about": "AN OMANI MINARET: a SQUARE shaft `a` wide rising `hs`, a chamfered step, then an OCTAGONAL shaft to `h`, `balconies` balconies spaced evenly up it (the last at its top) -- each on a flared octagonal corbelling, with its parapet -- and on the top an open octagonal LANTERN of arches under a small pointed dome and a finial. (The `minaret` component is round from its plinth up and crowned with a chhatri or a pencil cap: the square-to-octagon shaft and the domed lantern are this one's.) The Sultan Qaboos Grand Mosque has five: one great and four small.",
  "params": {"detail": 4, "h": 40, "a": 5, "hs": "h * 0.35", "r": "a * 0.42", "tr": "a * 0.5", "th": 1.2, "ch": 0.5, "balconies": 2, "bw": "r * 0.35",
             "tier": "(h - hs - ch - th) / balconies", "lr": "r * 0.8", "lh": "r * 2.2", "cr": "lr * 1.12", "fin": "r * 1.4",
             "_h": "the height of the octagonal shaft's top, where the lantern stands; `a` the square shaft's width, `hs` its height",
             "_tr": "the octagonal step between the two shafts (`th` tall), over the square's cornice (`ch`)", "_lr": "the lantern's radius and height, `cr` its dome's"},
  "build": ["square shaft", "cornice", "step", "shaft", "corbelling", "balcony", "parapet", "lantern", "cap", "finial"],
  "parts": {
    "square shaft": {"type": "prism", "plan": {"rect": ["a", "a"]}, "height": "hs", "at": [[0, 0, 0, 0]], "flatRoof": True},
    "cornice": {"type": "box", "width": "a + 0.5", "length": "a + 0.5", "height": 0.5, "at": [[0, "hs", 0, 0]], "flatRoof": True,
                "_about": "the band on the square shaft's head"},
    "step": {"type": "column", "radius": "tr", "height": "th", "sides": 8, "taper": "r / tr", "at": [[0, "hs + ch", 0, 0]], "flatRoof": True,
             "_about": "the square turning octagonal: a chamfered step"},
    "shaft": {"type": "column", "radius": "r", "height": "tier - 0.9", "sides": 8, "at": [[0, "hs + ch + th", 0, 0]], "flatRoof": True,
              "repeat": {"count": "balconies", "step": [0, "tier", 0, 0]}, "standsOn": ["step"],
              "_about": "the octagonal shaft, in lengths from each balcony to the corbelling of the next"},
    "corbelling": {"type": "column", "radius": "r", "height": 0.9, "sides": 8, "taper": "(r + bw) / r", "at": [[0, "hs + ch + th + tier - 0.9", 0, 0]], "flatRoof": True,
                   "repeat": {"count": "balconies", "step": [0, "tier", 0, 0]}, "_about": "the flare under each balcony"},
    "balcony": {"type": "ring", "count": 8, "rOuter": "r + bw", "rInner": "r", "height": 0.3, "solid": True, "turn": 0.5,
                "place": [[0, "hs + ch + th + tier", 0, 0]], "repeat": {"count": "balconies", "step": [0, "tier", 0, 0]}},
    "parapet": {"type": "ring", "count": 8, "rOuter": "r + bw", "rInner": "r + bw - 0.18", "height": 1.0, "solid": True, "turn": 0.5,
                "place": [[0, "hs + ch + th + tier + 0.3", 0, 0]], "repeat": {"count": "balconies", "step": [0, "tier", 0, 0]}},
    "lantern": {"type": "ring", "count": 8, "rOuter": "lr", "rInner": "lr - 0.3", "height": "lh", "turn": 0.5, "glass": False,
                "opening": {"width": "lr * 0.45", "sill": 0, "springing": "lh * 0.55", "head": {"profile": "pointed", "spread": 0.5}},
                "place": [[0, "h", 0, 0]], "_about": "the open lantern of eight arches on the shaft's top"},
    "cap": {"type": "dome", "radius": "cr", "sides": 8, "turn": -0.5, "thickness": 0, "head": {"profile": "pointed", "spread": 0.6},
            "at": [[0, "h + lh", 0, 0]], "standsOn": ["lantern"], "_about": "the small pointed dome"},
    "finial": {"type": "column", "radius": "r * 0.05 + 0.06", "height": "fin", "sides": 6, "taper": 0.4, "at": [[0, -0.05, 0, 0]], "atop": "cap", "standsOn": ["cap"]}}})

# ================================================================= the mosque
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)

# ---- the sahn and its riwaq: four arcade walks round the complex, their backs its outer wall
CX, CZ = 160.0, 200.0                       # the complex, outside
AD, AH = 8.0, 8.0                           # the riwaq: deep, tall
arc = {"D": AD, "H": AH, "t": 0.9, "bay": 5.0, "pw": 1.3, "spread": 0.5, "slab": 0.6, "gw": 4.4}
LS = CZ - 2 * AD                            # the long sides run between the ends
add("south riwaq", comp("components/arcade-walk", {**arc, "L": CX}, [[0, 0, CZ / 2 - AD / 2, math.pi]],
                        build=["front", "back gate", "roof", "front parapet", "back parapet"],
                        _about="the riwaq along the front, the main gate through its back wall"))
add("north riwaq", comp("components/arcade-walk", {**arc, "L": CX}, [[0, 0, -CZ / 2 + AD / 2, 0]],
                        _about="the riwaq behind the prayer hall"))
add("side riwaqs", comp("components/arcade-walk", {**arc, "L": LS}, [[CX / 2 - AD / 2, 0, 0, -Q], [-CX / 2 + AD / 2, 0, 0, Q]],
                        build=["front", "back gate", "roof", "front parapet", "back parapet"],
                        _about="the riwaqs along the sides, a gate through the middle of each"))
# the gates' portals, standing out from the outer wall
gate = {"W": 20.0, "Hh": 17.0, "D": 8.0, "w": 9.0, "s": 7.5, "spread": 0.5, "it": 0.6}
add("main gate", comp("components/portal", gate, [[0, 0, CZ / 2, 0]], _about="the main gate's portal on the front"))
add("side gates", comp("components/portal", {**gate, "W": 14.0, "Hh": 14.0, "D": 6.5, "w": 7.0, "s": 6.0}, [[CX / 2, 0, 0, Q], [-CX / 2, 0, 0, -Q]],
                       _about="the side gates' portals"))

# ---- the prayer hall: a square of flat-roofed bays round the crossing
HW, HH, HT = 64.0, 14.0, 2.0                # square, walls' height, thickness
HZ = -CZ / 2 + AD + 10.0 + HW / 2           # its middle (10m behind it to the north riwaq)
A = HW / 2
win = lambda n, g, sp=8.0, ww=2.4: {"pattern": str(n), "width": ww, "gap": g, "sill": 2.5, "springing": sp, "head": {"profile": "pointed", "spread": 0.5}}
withdoor = lambda n, g, dw, ds: {**win(n, g), "middle": {"width": dw, "sill": 0, "springing": ds}}
add("prayer hall", {"type": "enclosure", "plan": {"rect": [HW, HW]}, "thickness": HT, "height": HH,
                    "faces": {"0": withdoor(3, 14.3, 5.0, 6.0), "1": withdoor(3, 14.3, 3.2, 4.4), "3": withdoor(3, 14.3, 3.2, 4.4), "2": win(5, 9.0)},
                    "at": [[0, 0, HZ, 0]], "_about": "the prayer hall's walls: the great door toward the court, a door on each side, pointed windows"})
S, PR = 28.0, 3.0                           # the crossing under the dome, and its piers
SPR = 11.0
CT = SPR + S / 2                            # the pendentives' top: the drum's foot
add("piers", {"type": "box", "width": PR, "length": PR, "height": CT + 0.5,
              "at": [[sx * (S / 2 + PR / 2), 0, HZ + sz * (S / 2 + PR / 2), 0] for sx in (-1, 1) for sz in (-1, 1)],
              "_about": "the four great piers under the dome, rising over the roofs"})
add("great arches", {"type": "barrel", "width": S, "length": PR, "springing": SPR, "top": CT + 0.5, "head": {"profile": "semicircular"},
                     "at": [[0, 0, HZ - S / 2, 0], [0, 0, HZ + S / 2 + PR, 0], [-S / 2, 0, HZ, Q], [S / 2 + PR, 0, HZ, Q]],
                     "_about": "the arches from pier to pier; above the roofs their backs are the crossing's square walls"})
add("pendentives", {"type": "pendentives", "span": S, "springing": SPR, "sides": 16, "at": [[0, 0, HZ, 0]], "deck": {"thickness": 0.5, "out": PR},
                    "_about": "the pendentives, and the roof round the drum's foot"})
RO = S / 2 + PR                             # the crossing reaches this far from the middle
RS = 0.8
add("hall roof", {"flatRoof": True, "type": "box", "width": HW, "length": A - RO, "height": RS,
                  "at": [[0, HH, HZ + sz * (A + RO) / 2, 0] for sz in (-1, 1)], "_about": "the flat roofs of the bays round the crossing"})
add("hall roof sides", {"flatRoof": True, "type": "box", "width": A - RO, "length": 2 * RO, "height": RS,
                        "at": [[sx * (A + RO) / 2, HH, HZ, 0] for sx in (-1, 1)]})
TY = HH + RS                                # the tympana: the great arches rise over the roofs, and are closed there
add("tympana", {"type": "wall", "width": S, "height": CT + 0.5 - TY, "thickness": 1.0,
                "openings": {"pattern": "3", "width": 2.4, "gap": 5.0, "sill": 1.5, "springing": 5.0, "head": {"profile": "pointed", "spread": 0.5}},
                "at": [[0, TY, HZ - RO + 1.0, 0], [0, TY, HZ + RO - 1.0, math.pi], [-RO, TY, HZ, -Q], [RO, TY, HZ, Q]],
                "_about": "the tympana closing the great arches over the roofs, each with three pointed windows: the crossing's clerestory"})
add("hall parapet", comp("components/crenellation", {"L": HW, "t": 0.6, "h": 0.9, "step": 2.4},
                         [[0, HH + RS, HZ + A - 0.3, 0], [0, HH + RS, HZ - A + 0.3, 0], [A - 0.3, HH + RS, HZ, Q], [-A + 0.3, HH + RS, HZ, Q]],
                         standsOn=["hall roof", "hall roof sides"], _about="the crenellated parapet round the hall's roofs"))
add("crossing parapet", comp("components/crenellation", {"L": 2 * RO, "t": 0.6, "h": 0.9, "step": 2.4},
                             [[0, CT + 0.5, HZ + RO - 0.3, 0], [0, CT + 0.5, HZ - RO + 0.3, 0], [RO - 0.3, CT + 0.5, HZ, Q], [-RO + 0.3, CT + 0.5, HZ, Q]],
                             standsOn=["pendentives"], _about="and round the crossing's square head, at the drum's foot"))
add("dome", comp("components/drum-dome", {"R": S / 2, "dt": 1.2, "H": 13.0, "n": 16, "every": 1, "winW": 2.4, "winSill": 3.0, "winH": 6.0,
                                          "profile": "pointed", "spread": 0.25, "domeT": 0.8, "ribsN": 32, "ribW": 0.35,
                                          },
                 [[0, CT, HZ, 0]], build=["drum", "dome", "ribs"],
                 _about="the tall drum, a pointed window in every bay, the gilded dome with its ribs and the gold finial"))
# the gold finials on the domes' crowns: a spike with a knop (the crown is the pointed profile's apex, sqrt(1 + 2 spread)
# of the dome's radius over its drum -- a component's dome is not a part of this document to stand `atop`)
def finial(name, x, y, z, R, spread, h, about):
    crown = y + R * math.sqrt(1 + 2 * spread) - 0.1
    add(name, {"type": "column", "radius": h * 0.05, "height": h, "sides": 8, "taper": 0.25, "at": [[x, crown, z, 0]], "_about": about})
    add(name + " knop", {"type": "column", "radius": h * 0.09, "height": h * 0.15, "sides": 8, "taper": 0.6, "at": [[x, crown + h * 0.35, z, 0]]})
finial("dome finial", 0, CT + 13.0, HZ, S / 2 + 1.2, 0.25, 8.0, "the gilded finial on the great dome")
# its portals: the great one toward the court, one on each side
add("hall portal", comp("components/portal", {"W": 24.0, "Hh": 22.0, "D": 9.0, "w": 12.0, "s": 10.0, "spread": 0.5, "it": 0.7},
                        [[0, 0, HZ + A, 0]], _about="the prayer hall's great portal, toward the court"))
add("hall side portals", comp("components/portal", {"W": 13.0, "Hh": 16.0, "D": 6.0, "w": 6.5, "s": 6.5, "spread": 0.5, "it": 0.5},
                              [[A, 0, HZ, Q], [-A, 0, HZ, -Q]], _about="the side portals"))

# the arcades along the hall's front and sides, either side of its portals: the walk's back is the hall's own wall
ha = {"D": 7.0, "H": 10.5, "t": 0.9, "bay": 4.4, "pw": 1.1, "spread": 0.5, "slab": 0.6}
walk = ["front", "roof", "front parapet"]
add("hall front arcades", comp("components/arcade-walk", {**ha, "L": 20.0}, [[sx * 22.0, 0, HZ + A + 3.5, 0] for sx in (-1, 1)], build=walk,
                               _about="the arcaded walks along the hall's front, either side of its great portal"))
add("hall side arcades", comp("components/arcade-walk", {**ha, "L": 25.5},
                              [[sx * (A + 3.5), 0, HZ + sz * 19.25, sx * Q] for sx in (-1, 1) for sz in (-1, 1)], build=walk,
                              _about="and along its sides"))

# ---- the women's prayer hall, east of the main one
WX, WZ, WW, WL, WH = 54.0, HZ - 6.0, 18.0, 22.0, 9.0
add("women's hall", {"type": "enclosure", "plan": {"rect": [WW, WL]}, "thickness": 1.2, "height": WH,
                     "faces": {"0": [{"at": 0, "width": 3.2, "sill": 0, "springing": 3.8, "head": {"profile": "pointed", "spread": 0.5}}], "1": win(3, 3.6, 5.5, 1.8), "2": win(3, 3.6, 5.5, 1.8), "3": win(3, 3.6, 5.5, 1.8)},
                     "at": [[WX, 0, WZ, 0]], "_about": "the women's prayer hall: its door toward the court, pointed windows"})
add("women's roof", {"flatRoof": True, "type": "box", "width": WW, "length": WL, "height": 0.6, "at": [[WX, WH, WZ, 0]]})
add("women's parapet", comp("components/crenellation", {"L": WW, "t": 0.5, "h": 0.8, "step": 2.2},
                            [[WX, WH + 0.6, WZ + WL / 2 - 0.25, 0], [WX, WH + 0.6, WZ - WL / 2 + 0.25, 0]], standsOn=["women's roof"]))
add("women's parapet sides", comp("components/crenellation", {"L": WL, "t": 0.5, "h": 0.8, "step": 2.2},
                                  [[WX + WW / 2 - 0.25, WH + 0.6, WZ, Q], [WX - WW / 2 + 0.25, WH + 0.6, WZ, Q]], standsOn=["women's roof"]))
add("women's dome", comp("components/drum-dome", {"R": 4.5, "dt": 0.6, "H": 3.5, "n": 12, "every": 1, "winW": 1.2, "winSill": 0.8, "winH": 1.6,
                                                  "profile": "pointed", "spread": 0.3, "domeT": 0.4},
                         [[WX, WH + 0.6, WZ, 0]], build=["drum", "dome"], _about="its small dome on a drum over the roof"))
finial("women's finial", WX, WH + 0.6 + 3.5, WZ, 4.5 + 0.6, 0.3, 3.0, "and on the women's hall's dome")
add("women's portal", comp("components/portal", {"W": 9.0, "Hh": 12.0, "D": 4.2, "w": 5.4, "s": 5.0, "spread": 0.5, "it": 0.4},
                           [[WX, 0, WZ + WL / 2, 0]], _about="its portal toward the court"))

# ---- the minarets: the great one by the hall's front corner, four small on the complex's corners
add("great minaret", comp("components/omani-minaret", {"h": 76.0, "a": 8.0, "hs": 26.0, "balconies": 3},
                          [[-A - 18.0, 0, HZ + A - 4.0, 0]], _about="the great minaret, 90m: the square shaft, the octagon with three balconies, the lantern and dome"))
add("corner minarets", comp("components/omani-minaret", {"h": 38.0, "a": 5.0, "hs": 12.0, "balconies": 2},
                            [[sx * CX / 2, 0, sz * CZ / 2, 0] for sx in (-1, 1) for sz in (-1, 1)],
                            _about="the four smaller minarets on the complex's corners, 45m"))

# ---- the platform everything stands on, and the flights up to it before the gates
PH = 1.2
for d in parts.values():                    # (everything above was set out from the platform's top)
    for a in d.get("at", []): a[1] = round(a[1] + PH, 4)
PX0, PX1, PZ0, PZ1 = -90.0, 90.0, -106.0, 118.0
NX, NZ = 6, 8                               # in tiles, so that no one triangle of its top is vast (the checks index by cells)
TW, TL = (PX1 - PX0) / NX, (PZ1 - PZ0) / NZ
add("platform", {"type": "box", "width": TW, "length": TL, "height": PH, "walked": True,
                 "at": [[round(PX0 + TW * (i + 0.5), 4), 0, round(PZ0 + TL * (j + 0.5), 4), 0] for i in range(NX) for j in range(NZ)],
                 "_about": "the raised platform of the whole complex, its top the sahn's white marble"})
RISE, RUN = 0.15, 0.35
FL = round(PH / RISE) * RUN
add("main flight", {"type": "flight", "width": 16.0, "run": RUN, "rise": RISE, "top": PH, "landing": 0, "at": [[8.0, 0, PZ1 + FL, Q]],
                    "_about": "the broad flight up to the platform before the main gate"})
add("side flights", {"type": "flight", "width": 10.0, "run": RUN, "rise": RISE, "top": PH, "landing": 0,
                     "at": [[PX1 + FL, 0, -5.0, math.pi], [PX0 - FL, 0, 5.0, 0]], "_about": "and before the side gates"})

doc = {"name": "Sultan Qaboos Grand Mosque",
       "_about": "THE SULTAN QABOOS GRAND MOSQUE, Muscat (2001), from components on its platform: the marble sahn enclosed by four riwaqs (`arcade-walk`: pointed arches on piers, a flat roof, `crenellation`s along both edges), gated through three `portal`s -- iwan-like frames whose reveal is the recess, the `iwan` back closing it round the door; the prayer hall, a square of lower flat-roofed bays round the crossing, whose four piers and pointed arches carry pendentives and the tall drum of sixteen windows with the ribbed, gilded dome (`drum-dome`), entered through its great portal from the court and a portal on each side; the women's prayer hall with its small dome and portal; the great `omani-minaret` (square shaft, octagon, three balconies, lantern and dome) and four smaller ones on the complex's corners.",
       "params": {"detail": 4}, "railing": {"type": "stone"},
       "build": build, "parts": parts}
write(os.path.join(ROOT, "assets/architecture/sultan-qaboos.json"), doc)
