# THE HISTORICIST CASTLE'S VOCABULARY (a style library, L2): the pieces a 19th-century "castle" villa is put together from
# -- Gothic Revival and Neo-Renaissance as the Rhineland built it (Drachenburg first; Neuschwanstein, Hohenzollern, Stolzenfels,
# Lichtenstein would take the same) -- written once as parametric components and Python helpers for any generator to import:
#   components/cone-turret.json   a round turret ("pepperpot") standing on its own foot: a polygonal shaft of storeys under
#                                 belt courses, a window in every third face, a door by name, a corbelled cornice, a
#                                 tall pointed slate cone (or a squat one) and a finial
#   components/oriel.json         an Erker: a three-sided bay standing `d` out of a wall `w` wide, on a stepped corbel under
#                                 it, a window in each of its three faces, a cornice and -- by name -- a slate helm
#                                 (`cap` helm) or a flat top behind a parapet (`cap` flat)
#   components/castle-tower.json  a SQUARE tower of storeys -- a window pair in each face of each storey, a door, a clock by
#                                 name -- and its head by `top`: "spire" (a belfry stage of lancets, a gable on every
#                                 face, an octagonal turret with a stone cap at every corner, a steep four-sided slate
#                                 spire with lucarnes: the Rhenish Gothic Revival tower) or "battlement" (a machicolated
#                                 corbel course, crenellations, a watch turret on one corner by name: the keep)
# and the helpers (python, for the generator): pointed and stepped GABLE outlines with their pinnacles (`gable`), a gabled
# ROOF and the stone gable closing its end, sized to hide it (`gabled`), a storeyed block with its windows face by face
# (`block`, its storeys by `storey_row`), a ridge's iron CRESTING round a flat roof top (`crest_rect`), crenellated
# PARAPETS along a terrace's outline or a bastion's arc (`parapets`), a straight FLIGHT set out by its foot and direction (`flight`).
# Every number of a component is a param or an expression over its params; the `_x` keys say what x is. Front +z.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = lambda rel, doc: open(os.path.join(ROOT, "assets/architecture", rel), "w").write(json.dumps(doc, indent=2) + "\n")
r4 = lambda v: round(v, 4)
POINTED = {"profile": "pointed", "spread": 0.55}
comp = lambda use, params, at, **kw: {"type": "component", "use": f"components/{use}", "params": params, "at": at, **kw}


# ---------------------------------------------------------------------------------------------------------------- L1
def cone_turret():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    # (a window in every third face of every storey above the first; the door in face 0 of the first by `door` yes --
    #  the faces are counted round the polygon from +z, so for sides 12 the windows look out every 90 degrees; faces
    #  past `sides` are ignored, so any polygon up to 32 sides takes them. The shaft is written once for each count of
    #  storeys (1 to 4) and drawn by `when`: "shaft" is the four-storey one, "shaft 3" the three-storey one...)
    def faces(door, n):
        F = {}
        for k in range(32):
            win = [{"at": 0, "width": "winW", "sill": "H / storeys * 0.3", "springing": "H / storeys * 0.62", "head": POINTED}] if k % 3 == 0 else []
            low = [{"at": 0, "width": "doorW", "sill": 0, "springing": "doorH", "head": POINTED, "glass": False}] if (door and k == 0) else []
            F[str(k)] = [{"openings": low}] if n == 1 else [{"h": "H / storeys", "openings": low}] + [{"h": "H / storeys", "openings": win}] * (n - 2) + [{"openings": win}]
        return F
    shaft = {"type": "enclosure", "plan": {"sides": "sides", "radius": "R"}, "thickness": "t", "height": "H", "glass": True, "interior": True, "at": [[0, 0, 0, 0]]}
    for n in (4, 3, 2, 1):
        sfx = "" if n == 4 else f" {n}"
        add(f"shaft{sfx}", {**shaft, "faces": faces(True, n), "when": {"door": "yes", "storeys": n},
                            "_about": f"the shaft of {n} storeys (each H / storeys tall, the top one what is left), the door in face 0"})
        add(f"shaft blind{sfx}", {**shaft, "faces": faces(False, n), "when": {"door": "no", "storeys": n},
                                  "_about": f"the shaft of {n} storeys without a door (a turret reached from the building it stands against)"})
    add("belts", {"type": "prism", "plan": {"sides": "sides", "radius": "R + 0.08"}, "height": 0.2, "flatRoof": True, "at": [[0, "H / storeys - 0.1", 0, 0]],
                  "repeat": {"count": "storeys - 1", "step": [0, "H / storeys", 0, 0]}, "when": {"storeys": [2, 3, 4]}, "_about": "a belt course at every floor"})
    add("corbels", {"type": "prism", "plan": {"sides": "sides", "radius": "R + corOut * 0.5"}, "height": "corH * 0.55", "flatRoof": True, "at": [[0, "H - corH * 0.55", 0, 0]],
                    "_about": "the corbel course under the cornice"})
    add("cornice", {"type": "prism", "plan": {"sides": "sides", "radius": "R + corOut"}, "height": "corH * 0.45", "flatRoof": True, "at": [[0, "H", 0, 0]], "standsOn": ["corbels"],
                    "_about": "the cornice the cone sits on, corOut proud"})
    add("cap", {"type": "dome", "radius": "capR", "thickness": 0, "sides": "capSides", "head": {"profile": "trigonal", "rise": "capRise"},
                "at": [[0, "H + corH * 0.45", 0, 0]], "standsOn": ["cornice"], "_about": "the slate cone, its eave overhanging the cornice"})
    add("finial", {"type": "column", "radius": "max(0.05, capR * 0.05)", "height": "finial", "sides": 6, "taper": 0.4, "at": [[0, 0, 0, 0]], "atop": "cap", "standsOn": ["cap"],
                   "_about": "the iron finial (a vane's rod) on the tip"})
    return {"name": "Cone turret",
            "_about": "A ROUND TURRET UNDER A CONE -- the historicist castle's \"pepperpot\" (Drachenburg's terrace and corner turrets): a polygonal shaft (`sides`, R to its corners, H tall, `t` walls) "
                      "in `storeys` under belt courses, a pointed window in every third face of every storey but the first, a door in face 0 (+z) of the first by `door` yes, a corbel course and a "
                      "cornice corOut proud and corH deep, a cone `capRise` tall from capR at its eave (the Rhenish slate spike: capR = R + corOut, capRise 3.5 capR; squat: capRise R), "
                      "an iron finial on the tip. (Its kin: components/stage-tower -- Schwerin's round tower of stages under a tent and lantern -- for a turret that steps back "
                      "and carries more on top; components/castle-tower for the square tower.)",
            "params": {"detail": 4, "sides": 12, "R": 2.2, "H": 12.0, "t": "max(0.3, R * 0.2)", "storeys": 4, "door": "yes", "doorW": "min(1.1, R * 0.45)", "doorH": "min(2.3, H / storeys * 0.6)",
                       "winW": "R * 0.24", "corOut": "R * 0.12", "corH": 0.7, "capR": "R + corOut + 0.2", "capRise": "R * 3", "capSides": 16, "finial": "capRise * 0.18",
                       "_door": "yes: a pointed door in face 0 (+z) of the first storey; no: blind (reached from the building behind)",
                       "_storeys": "how many storeys the shaft shows, 1 to 4 (belt courses between, a window in every third face of each but the first)",
                       "_capRise": "the cone's height above its eave: about 3 R for the tall slate spike, R for a squat cap"},
            "build": build, "parts": parts}


def oriel():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    # the plan: three faces of a half-octagon standing d out of the wall line z 0, w wide there; c is how far the
    # slanted faces come in (the front is w - 2c); face 3 is the back, on the wall, blind
    pts = lambda s, g=0: [[f"0 - (w / 2 + {g}) * {s}", 0], [f"0 - (w / 2 + {g} - c) * {s}", f"(d + {g}) * {s}"], [f"(w / 2 + {g} - c) * {s}", f"(d + {g}) * {s}"], [f"(w / 2 + {g}) * {s}", 0]]
    for k, s in enumerate((0.3, 0.6, 0.85)):
        add(f"corbel {k + 1}", {"type": "prism", "plan": {"points": pts(s)}, "height": "foot / 3", "flatRoof": True, "at": [[0, f"0 - foot + foot / 3 * {k}", 0, 0]],
                                "_about": "the stepped corbel the bay is carried on, widening upward in three courses"})
    win = {"at": 0, "width": "winW", "sill": "sill", "springing": "spring", "head": {"profile": "pointed", "spread": 0.6}}
    add("body", {"type": "enclosure", "plan": {"points": pts(1)}, "thickness": "t", "height": "H", "glass": True, "interior": True,
                 "faces": {"0": [{"openings": [{**win, "width": "winW * 0.7"}]}], "1": [{"openings": [win]}], "2": [{"openings": [{**win, "width": "winW * 0.7"}]}], "3": [{"openings": []}]},
                 "at": [[0, 0, 0, 0]], "_about": "the bay: its three faces each with a pointed window (the slanted ones narrower), the back on the wall"})
    add("sill course", {"type": "prism", "plan": {"points": pts(1, 0.08)}, "height": 0.2, "flatRoof": True, "at": [[0, "sill - 0.2", 0, 0]], "standsOn": ["body"]})
    add("cornice", {"type": "prism", "plan": {"points": pts(1, 0.18)}, "height": 0.35, "flatRoof": True, "at": [[0, "H", 0, 0]], "standsOn": ["body"], "_about": "the cornice round its head"})
    add("parapet", {"type": "enclosure", "plan": {"points": pts(1, 0.05)}, "thickness": 0.18, "height": "parH", "glass": False, "openings": [], "faces": {"3": [{"openings": []}]},
                    "at": [[0, "H + 0.35", 0, 0]], "when": {"cap": "flat"}, "standsOn": ["cornice"], "_about": "cap flat: a low parapet round its flat top (a balcony for the window over it)"})
    add("helm", {"type": "dome", "radius": "w / 2 + 0.2", "thickness": 0, "sides": 8, "turn": 0.5, "head": {"profile": "trigonal", "rise": "capRise"},
                 "at": [[0, "H + 0.35", 0, 0]], "when": {"cap": "helm"}, "standsOn": ["cornice"], "_about": "cap helm: a slate helm over it, its back half in the wall"})
    add("helm finial", {"type": "column", "radius": 0.05, "height": "capRise * 0.25", "sides": 6, "taper": 0.4, "at": [[0, 0, 0, 0]], "atop": "helm", "when": {"cap": "helm"}, "standsOn": ["helm"]})
    return {"name": "Oriel",
            "_about": "AN ORIEL (Erker): a three-sided bay `w` wide at the wall and `d` deep, its slanted faces coming in `c`, `H` tall from its floor (the placement, on the wall's face, +z out), "
                      "carried on a stepped corbel `foot` deep below it; a pointed window in each face (winW, from sill to spring), a sill course and a cornice; `cap` helm puts a slate "
                      "helm `capRise` tall over it, `cap` flat a parapet parH high round a flat top.",
            "params": {"detail": 4, "w": 3.0, "d": 1.3, "c": "d * 0.8", "H": 4.0, "t": 0.3, "foot": 1.5, "winW": "(w - 2 * c) * 0.6", "sill": "H * 0.22", "spring": "H * 0.75",
                       "cap": "flat", "capRise": "w * 0.9", "parH": 0.9,
                       "_c": "how far each slanted face comes in toward the middle (c = d: 45 degrees)",
                       "_cap": "helm: a slate helm capRise tall; flat: a parapet parH high round its top"},
            "build": build, "parts": parts}


def castle_tower():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    # THE SHAFT: five tiers -- the ground storey with the door in face 0, three storeys of window pairs, the clock storey
    # (blind: the dial is on it) -- each `H * share` tall
    SH = [0.24, 0.2, 0.2, 0.18]
    pair = lambda k: {"pattern": "2", "width": "winW", "gap": "winW * 0.45", "sill": f"H * {SH[k]} * 0.28", "springing": f"H * {SH[k]} * 0.78", "head": POINTED}
    tiers = [{"h": f"H * {SH[0]}", "openings": {**pair(0), "pattern": "1"}}] + [{"h": f"H * {SH[k]}", "openings": pair(k)} for k in (1, 2, 3)] + [{"openings": []}]
    front = [{"h": f"H * {SH[0]}", "openings": [{"at": 0, "width": "doorW", "sill": 0, "springing": "doorH", "head": POINTED, "glass": False}]}] + tiers[1:]
    add("shaft", {"type": "enclosure", "plan": {"rect": ["w", "w"]}, "thickness": "t", "height": "H", "glass": True, "interior": True, "tiers": tiers, "faces": {"0": front},
                  "courses": True, "at": [[0, 0, 0, 0]], "_about": "the square shaft, w on a side and H tall: the door storey, three storeys of paired pointed windows, the clock storey; plinth, strings and cornice its own"})
    # THE CLOCK (clock yes): the shared dial (components/clock-dial: plate, chapter ring, marks, hands at ten past ten)
    # on every face of the top storey, its middle at clockY
    add("clock", comp("clock-dial", {"R": "clockR", "t": 0.12}, [], spiral={"count": 4, "radius": "w / 2", "y": "clockY"}, when={"clock": "yes"}, standsOn=["shaft"],
                      _about="the dial, clockR, on each face at clockY (its middle): components/clock-dial"))
    # ---- top: "spire" -- the belfry stage, gables, corner turrets, the spire and its lucarnes
    add("belfry", {"type": "enclosure", "plan": {"rect": ["w", "w"]}, "thickness": "t * 0.8", "height": "Hb", "glass": False, "interior": True,
                   "openings": {"pattern": "lights", "width": "bW", "gap": "bW * 0.4", "sill": "Hb * 0.16", "springing": "Hb * 0.7", "head": POINTED},
                   "at": [[0, "H", 0, 0]], "when": {"top": "spire"}, "standsOn": ["shaft"], "_about": "the belfry stage: `lights` lancets in every face, open"})
    add("belfry cornice", {"type": "prism", "plan": {"rect": ["w + 0.4", "w + 0.4"]}, "height": 0.4, "flatRoof": True, "at": [[0, "H + Hb", 0, 0]], "when": {"top": "spire"}, "standsOn": ["belfry"]})
    gable = [["0 - gW / 2", 0], ["gW / 2", 0], ["gW / 2", 0.5], [0, "gH"], ["0 - gW / 2", 0.5]]
    add("gables", {"type": "screen", "outline": gable, "t": 0.45, "spiral": {"count": 4, "radius": "w / 2 + 0.15", "y": "H + Hb + 0.4"}, "when": {"top": "spire"}, "standsOn": ["belfry cornice"],
                   "_about": "a gable gW wide and gH tall on every face, standing before the spire's foot"})
    add("gable finials", {"type": "pinnacle", "w": 0.35, "h": 0.5, "s": 1.1, "sides": 4, "spiral": {"count": 4, "radius": "w / 2 - 0.1", "y": "H + Hb + 0.4 + gH - 0.35"},
                          "when": {"top": "spire"}, "standsOn": ["gables"], "_about": "the finial on each gable's apex"})
    add("turrets", {"type": "pinnacle", "w": "tW", "h": "tH", "s": "tS", "sides": 8, "spiral": {"count": 4, "radius": "w * 0.7071 - tW * 0.2", "y": "H - tDrop", "turn": 0.7853982},
                    "when": {"top": "spire"}, "standsOn": ["shaft"], "_about": "an octagonal turret tW across at every corner, from tDrop under the belfry, tH of shaft and a stone cap tS tall"})
    add("spire", comp("gothic-spire", {"sides": 4, "R": "w * 0.66", "rise": "rise", "topR": "w * 0.03", "finial": "vane", "shellT": 0.25},
                      [[0, "H + Hb + 0.4", 0, 0]], build=["spire", "finial"], when={"top": "spire"}, standsOn=["belfry cornice"],
                      _about="the steep four-sided slate spire, its corners over the shaft's, `rise` to its tip, a vane's rod `vane` tall"))
    lf = "w * 0.66 * 0.7071 * (1 - lY / rise)"     # (how far the spire's face stands from the axis at the lucarnes' height)
    add("lucarnes", {"type": "box", "width": "lW", "length": "lW * 1.4", "height": "lW * 0.9", "spiral": {"count": 4, "radius": f"{lf} - lW * 0.1", "y": "H + Hb + 0.4 + lY"},
                     "when": {"top": "spire"}, "standsOn": ["spire"], "_about": "a lucarne on every face of the spire, lY up it"})
    add("lucarne roofs", {"type": "roof", "form": "gable", "width": "lW * 1.15", "length": "lW * 1.5", "pitch": 60, "overhang": 0.05,
                          "spiral": {"count": 4, "radius": f"{lf} - lW * 0.1", "y": "H + Hb + 0.4 + lY + lW * 0.9"}, "when": {"top": "spire"}, "standsOn": ["lucarnes"]})
    # ---- top: "battlement" -- the corbel course, the parapet with its merlons, the deck, a watch turret
    add("machicolation", {"type": "prism", "plan": {"rect": ["w + 2 * mOut", "w + 2 * mOut"]}, "height": "mH", "flatRoof": True, "at": [[0, "H", 0, 0]],
                          "when": {"top": "battlement"}, "standsOn": ["shaft"], "_about": "the corbelled course standing mOut out over the shaft"})
    add("machicolation corbels", {"type": "prism", "plan": {"rect": ["w + mOut", "w + mOut"]}, "height": "mH * 0.6", "flatRoof": True, "at": [[0, "H - mH * 0.6", 0, 0]],
                                  "when": {"top": "battlement"}, "standsOn": ["shaft"], "_about": "the step of corbels under it"})
    add("battlements", comp("crenellation", {"L": "w + 2 * mOut", "t": 0.45, "h": "pH", "step": "mStep", "mh": "pH * 0.7", "merlon": "square"},
                            [], spiral={"count": 4, "radius": "w / 2 + mOut - 0.225", "y": "H + mH"}, when={"top": "battlement"}, standsOn=["machicolation"],
                            _about="the crenellated parapet round its head"))
    add("watch", {"type": "prism", "plan": {"rect": ["wS", "wS"]}, "height": "wH", "flatRoof": True, "at": [["w / 2 - wS / 2", "H + mH", "0 - (w / 2 - wS / 2)", 0]],
                  "when": {"top": "battlement", "watch": "yes"}, "standsOn": ["machicolation"], "_about": "watch yes: the stair's square turret rising wH over the deck at the back corner"})
    add("watch battlements", comp("crenellation", {"L": "wS + 0.3", "t": 0.3, "h": 0.5, "step": 0.9, "mh": 0.55, "merlon": "square"},
                                  [], spiral={"count": 4, "radius": "wS / 2", "y": "H + mH + wH", "x": "w / 2 - wS / 2", "z": "0 - (w / 2 - wS / 2)"},
                                  when={"top": "battlement", "watch": "yes"}, standsOn=["watch"]))
    return {"name": "Castle tower",
            "_about": "A SQUARE TOWER OF A HISTORICIST CASTLE, w on a side and H to its head: a door storey (door in face 0, +z), three storeys of paired pointed windows, a top storey that carries a "
                      "CLOCK on every face by `clock` yes (dial clockR at clockY). Its head by `top`: \"spire\" -- a belfry stage Hb tall with `lights` open lancets (bW) in every face, a GABLE "
                      "gW by gH on every face with a finial, an octagonal TURRET at every corner (tW across, its shaft tH from tDrop under the belfry, a stone cap tS), the steep four-sided "
                      "slate SPIRE `rise` tall with a vane's rod `vane`, a LUCARNE (lW) on every face lY up it -- Drachenburg's Hauptturm; or \"battlement\" -- a machicolated course (mOut, mH), "
                      "crenellations pH high every mStep, and by `watch` yes a square stair turret wS wide rising wH from the deck's back corner -- a keep, Drachenburg's Nordturm. "
                      "(Round towers: components/cone-turret, components/stage-tower.)",
            "params": {"detail": 4, "w": 7.8, "H": 22.0, "t": "max(0.5, w * 0.1)", "winW": "w * 0.11", "doorW": "w * 0.22", "doorH": "H * 0.16", "top": "spire",
                       "clock": "no", "clockR": "w * 0.15", "clockY": "H * 0.91",
                       "Hb": "w * 0.72", "lights": 2, "bW": "w * 0.13", "gW": "w * 0.62", "gH": "w * 0.5", "tW": "w * 0.17", "tH": "Hb + tDrop + 0.6", "tS": "w * 0.36", "tDrop": 1.6,
                       "rise": "w * 1.75", "vane": "w * 0.3", "lW": "w * 0.15", "lY": "rise * 0.22",
                       "mOut": 0.5, "mH": 1.0, "pH": 1.1, "mStep": 1.4, "watch": "no", "wS": "w * 0.3", "wH": 2.6,
                       "_top": "spire: belfry, gables, corner turrets and the slate spire; battlement: machicolations and crenellations",
                       "_clock": "yes: a dial and hands on every face of the top storey",
                       "_lights": "how many open lancets each belfry face has",
                       "_watch": "with top battlement: yes raises a square stair turret on the deck's -z, +x corner"},
            "build": build, "parts": parts}


def write_components():
    OUT("components/cone-turret.json", cone_turret())
    OUT("components/oriel.json", oriel())
    OUT("components/castle-tower.json", castle_tower())


# ---------------------------------------------------------------------------------------------------------------- helpers
def pointed_gable(w, h, kneel=0.6):
    """a steep gable's outline, feet at y 0, w wide: short upright kneelers at the feet (where the pinnacles stand), then the rakes"""
    return [[-w / 2, 0.0], [w / 2, 0.0], [w / 2, kneel], [0.0, h], [-w / 2, kneel]]


def stepped_gable(w, h, steps=4):
    """a stepped gable's outline (Staffelgiebel), feet at y 0 -- schwerin.py's `stepped`, copied: schwerin.py writes its
    building when imported (no __main__ guard), so it cannot be imported from here"""
    pts = [(-w / 2, 0.0)]
    for k in range(steps):
        x0 = -w / 2 * (1 - k / steps); y1 = h * (k + 1) / (steps + 0.6)
        x1 = -w / 2 * (1 - (k + 1) / steps) if k + 1 < steps else -w / 2 / steps * 0.75
        pts += [(x0 + w * 0.02, y1), (x1, y1)]
    pts += [(pts[-1][0], h), (-pts[-1][0], h)]
    return [[r4(x), r4(y)] for x, y in pts + [(-x, y) for x, y in reversed(pts[1:-2])] + [(w / 2, 0.0)]]


def place(cx, cz, yaw, along=0.0, out=0.0, y=0.0, turn=0.0):
    """a point `along` a face (its own +x) and `out` from it, the face's middle (cx, cz) and its outward yaw: [x, y, z, yaw]"""
    c, s = math.cos(yaw), math.sin(yaw)
    return [r4(cx + along * c + out * s), r4(y), r4(cz - along * s + out * c), r4(yaw + turn)]


def gable(add, name, cx, cz, yaw, w, h, y, kind="pointed", t=0.6, pins=(0.7, 2.2, 2.0), finial=(0.45, 0.6, 1.6), overhang=0.15, about=""):
    """a stone gable standing in a face at (cx, cz) looking out along `yaw`, its feet at y: the screen, a pinnacle on each
    kneeler and one on the apex (pins / finial: w, shaft h, spire s; None for none). The screen's face stands 5 cm before
    the end of the roof behind it (`overhang`: how far that roof's end runs out past the face), so the stone hides the
    roof's end; w and h must cover the roof's end triangle (`gabled` sizes them so)"""
    out = pointed_gable(w, h) if kind == "pointed" else stepped_gable(w, h)
    pr = overhang + 0.05
    add(name, {"type": "screen", "outline": out, "t": t, "at": [place(cx, cz, yaw, 0, pr, y)], "_about": about or "a gable"})
    if pins:
        add(f"{name} pinnacles", {"type": "pinnacle", "w": pins[0], "h": pins[1], "s": pins[2], "sides": 4,
                                  "at": [place(cx, cz, yaw, d * (w / 2 - pins[0] / 2), pr - t / 2, y + (0.6 if kind == "pointed" else 0)) for d in (-1, 1)]})
    if finial:
        add(f"{name} finial", {"type": "pinnacle", "w": finial[0], "h": finial[1], "s": finial[2], "sides": 4, "at": [place(cx, cz, yaw, 0, pr - t / 2, y + h - finial[0] * 0.8)]})


def gabled(add, name, cx, cz, yaw, W, L, pitch, y, overhang=0.15, w=None, h=None, **kw):
    """a gabled roof W wide and L long running back from a face at (cx, cz) (looking out along `yaw`), its eaves at y,
    and the stone gable that closes its front end: "{name} roof" and "{name} gable" (with its pinnacles and finial); the
    gable is sized to cover the roof's end (w: W + 2 overhang + 0.4; h: the ridge's height + 0.6) unless w / h say
    otherwise. Returns the ridge's height over y."""
    rise = W / 2 * math.tan(math.radians(pitch))
    add(f"{name} roof", {"type": "roof", "form": "gable", "width": r4(W), "length": r4(L), "pitch": pitch, "overhang": overhang, "at": [place(cx, cz, yaw, 0, -L / 2, y)]})
    gable(add, f"{name} gable", cx, cz, yaw, w or r4(W + 2 * overhang + 0.4), h or r4(rise + 0.6), y, overhang=overhang, **kw)
    return rise


def storey_row(L, xs, j, hs, w=1.3, head=None, door=None, tracery=None, doorW=1.6, doorH=2.7):
    """for `block`: windows at `xs` (along the face) in storey j, tall on the ground floor, a pointed door at `door` there
    (doorW by doorH) in place of the window at that spot"""
    out = []
    for a in xs:
        if j == 0 and door is not None and abs(a - door) < 0.05: continue
        out.append({"at": r4(a), "width": w, "sill": r4(hs * (0.3 if j else 0.25)), "springing": r4(hs * 0.78), "head": head or {"profile": "flat"}, **({"tracery": tracery} if tracery else {})})
    if j == 0 and door is not None:
        out.append({"at": r4(door), "width": doorW, "sill": 0, "springing": doorH, "head": POINTED, "glass": False})
    return out


def row(L, n, w, sill, spring, head, edge=1.2, glass=True, **kw):
    """n openings w wide spread evenly along a face L long (at, from the face's middle); [] when n is 0"""
    if n <= 0: return []
    step = (L - 2 * edge) / n
    return [{"at": r4(-L / 2 + edge + step * (k + 0.5)), "width": w, "sill": sill, "springing": spring, "head": head, **({"glass": False} if not glass else {}), **kw} for k in range(n)]


def block(add, name, x0, x1, z0, z1, y0, H, storeys, faces, t=0.7, skip=(), about="", interior=True):
    """a storeyed block on the rect x0..x1, z0..z1 standing at y0, H tall: `faces` {0: +z, 1: +x, 2: -z, 3: -x} each a function
    (L, storey, hs) -> that storey's openings (a list), or None for blind; (the face's `at` runs: 0 toward +x, 1 toward -z,
    2 toward -x, 3 toward +z, from its middle); `skip`: faces against a neighbour, without courses (blind, unless `faces`
    gives one a doorway through to it); `interior` False: an open porch or loggia -- no room inside, so the walls it
    shows the open air are dressed as the outside"""
    W, D = x1 - x0, z1 - z0; hs = H / storeys
    F = {}
    for k in range(4):
        L = W if k % 2 == 0 else D; f = faces.get(k)
        tiers = [{"h": r4(hs), "openings": (f(L, j, hs) if f else [])} for j in range(storeys - 1)] + [{"openings": (f(L, storeys - 1, hs) if f else [])}]
        F[str(k)] = tiers
    add(name, {"type": "enclosure", "plan": {"rect": [r4(W), r4(D)]}, "thickness": t, "height": H, "glass": True, "interior": interior, "faces": F, "courses": {"skip": [str(k) for k in skip]} if skip else True,
               "at": [[r4((x0 + x1) / 2), y0, r4((z0 + z1) / 2), 0]], "_about": about})


def crest_rect(add, name, cx, y, cz, W, D, h=0.7, panel=0.55):
    """iron cresting round a flat roof top W (x) by D (z) at height y: two placements of a run W long, two of D"""
    add(f"{name} ends", {"type": "cresting", "run": [[-D / 2, 0], [D / 2, 0]], "h": h, "panel": panel, "t": 0.06, "bar": 0.04,
                         "at": [[r4(cx + W / 2), r4(y), r4(cz), r4(math.pi / 2)], [r4(cx - W / 2), r4(y), r4(cz), r4(-math.pi / 2)]]})
    add(name, {"type": "cresting", "run": [[-W / 2, 0], [W / 2, 0]], "h": h, "panel": panel, "t": 0.06, "bar": 0.04,
               "at": [[r4(cx), r4(y), r4(cz + D / 2), 0], [r4(cx), r4(y), r4(cz - D / 2), r4(math.pi)]], "_about": "iron cresting along the roof's flat top"})


def parapets(add, name, pts, y, h=1.0, step=2.2, t=0.5, merlon="square", skip=0.9, gaps=(), holes=(), closed=True):
    """a crenellated parapet (components/crenellation) on every edge of the outline `pts` at height y, its outer face on
    the outline: one part per run (each its own length), broken where a `gaps` entry ((x, z), width) falls on an edge (a
    stair arriving) and left out within a `holes` circle ((x, z), r) (where a bastion's own parapet takes over); runs
    shorter than `skip` are left out. `closed` False: an open line (an arc round a bastion), the side the closing chord
    lies on being inside. Returns the parts' names (for the finish)."""
    n = len(pts); area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n)); names = []
    for i in range(n if closed else n - 1):
        p, q = pts[i], pts[(i + 1) % n]; L = math.dist(p, q)
        ex, ez = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        nx, nz = (ez, -ex) if area > 0 else (-ez, ex)          # (the outward normal: right of p->q for a counter-clockwise outline in x, z)
        yaw = math.atan2(nx, nz)
        runs = [(0.0, L)]
        for (gx, gz), gw in gaps:                              # (a gap on this edge: within a metre of its line, between its ends)
            u = (gx - p[0]) * ex + (gz - p[1]) * ez; v = (gx - p[0]) * nx + (gz - p[1]) * nz
            if abs(v) < 1.0 and 0 < u < L:
                runs = [r for a, b in runs for r in ((a, min(b, u - gw / 2)), (max(a, u + gw / 2), b))]
        for (hx, hz), hr in holes:                             # (the stretch of this edge's line inside the circle)
            u = (hx - p[0]) * ex + (hz - p[1]) * ez; v = (hx - p[0]) * nx + (hz - p[1]) * nz
            if abs(v) < hr:
                e = math.sqrt(hr * hr - v * v)
                runs = [r for a, b in runs for r in ((a, min(b, u - e)), (max(a, u + e), b))]
        runs = [r for r in runs if r[1] - r[0] >= skip]
        for k, (a, b) in enumerate(runs):
            m = (a + b) / 2; Lr = b - a
            mx, mz = p[0] + ex * m - nx * t / 2, p[1] + ez * m - nz * t / 2
            nm = f"{name} {i}" + (f".{k}" if len(runs) > 1 else "")
            add(nm, comp("crenellation", {"L": r4(Lr + (t * 0.5 if Lr == L else 0)), "t": t, "h": h, "step": step, "mh": 0.7, "merlon": merlon}, [[r4(mx), y, r4(mz), r4(yaw)]]))
            names.append(nm)
    return names


def flight(foot, d, w, base, top, run=0.3, rise=0.17, **kw):
    """a straight flight whose foot's middle is `foot` (x, z), climbing along the unit (x, z) direction `d` from base to top"""
    n = max(1, round((top - base) / rise)); yaw = math.atan2(-d[1], d[0])
    s, c = math.sin(yaw), math.cos(yaw)
    px, pz = foot[0] + w / 2 * s, foot[1] + w / 2 * c          # (a flight's width lies to its right, -z of its own frame)
    return {"type": "flight", "width": w, "run": run, "rise": r4((top - base) / n), "base": base, "top": top, "landing": 0, "at": [[r4(px), 0, r4(pz), r4(yaw)]], **kw}



# ---------------------------------------------------------------------------------------------------------------- L1 (2026-11-04)
def round_keep():
    """components/round-keep.json -- Burg Hohenzollern's round towers (Stüler's Markgrafen- and Kaiserturm) and their kin"""
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    # (the shaft's storeys as cone_turret's: a window in every `every`-th face of each storey above the first, the
    #  door by name in face 0; one shaft per count of storeys, 2 to 5, drawn by `when`)
    shaft = {"type": "enclosure", "plan": {"sides": "sides", "radius": "R"}, "thickness": "t", "height": "H", "glass": True, "interior": True, "courses": True, "at": [[0, 0, 0, 0]]}
    def storeys_faces(door, n, every):
        F = {}
        for k in range(32):
            win = [{"at": 0, "width": "winW", "sill": "H / storeys * 0.3", "springing": "H / storeys * 0.72", "head": {"profile": "semicircular"},
                    "surround": {"band": "winW * 0.16", "depth": 0.1}}] if k % every == 0 else []
            low = [{"at": 0, "width": "doorW", "sill": 0, "springing": "doorH", "head": POINTED, "glass": False}] if (door and k == 0) else []
            F[str(k)] = [{"h": "H / storeys", "openings": low}] + [{"h": "H / storeys", "openings": win}] * (n - 2) + [{"openings": win}]
        return F
    for n in (5, 4, 3, 2):
        for every in (2, 4):
            sfx = f" {n}" + ("" if every == 4 else " dense")
            add(f"shaft{sfx}", {**shaft, "faces": storeys_faces(True, n, every), "when": {"door": "yes", "storeys": n, "windows": "dense" if every == 2 else "sparse"},
                                "_about": f"the shaft of {n} storeys, a round-headed window in every {every}th face above the first, the door in face 0"})
            add(f"shaft blind{sfx}", {**shaft, "faces": storeys_faces(False, n, every), "when": {"door": "no", "storeys": n, "windows": "dense" if every == 2 else "sparse"},
                                      "_about": f"the same without a door (a tower reached from the building it stands in)"})
    add("belts", {"type": "prism", "plan": {"sides": "sides", "radius": "R + 0.1"}, "height": 0.25, "flatRoof": True, "at": [[0, "H / storeys - 0.12", 0, 0]],
                  "repeat": {"count": "storeys - 1", "step": [0, "H / storeys", 0, 0]}, "_about": "a string course at every floor"})
    # THE GALLERY STOREY: corbelled out gOut on three courses of corbels, a ring of small round-arched windows (an arcade
    # under the eaves) -- the Kaiserturm's and the Markgrafenturm's top band
    for k, f in enumerate((0.35, 0.7, 1.0)):
        add(f"corbel {k + 1}", {"type": "prism", "plan": {"sides": "sides", "radius": f"R + gOut * {f}"}, "height": "corH / 3", "flatRoof": True,
                                "at": [[0, f"H - corH + corH / 3 * {k}", 0, 0]], "_about": "the corbel table the gallery storey is carried out on, in three steps"})
    add("gallery", {"type": "enclosure", "plan": {"sides": "sides", "radius": "R + gOut"}, "thickness": "t * 0.7", "height": "Hg", "glass": True, "interior": True,
                    "openings": [{"at": 0, "width": "gW", "sill": "Hg * 0.28", "springing": "Hg * 0.72", "head": {"profile": "semicircular"}}],
                    "at": [[0, "H", 0, 0]], "standsOn": ["corbel 3"], "_about": "the gallery storey, gOut proud: a small round-arched window in every face"})
    add("cornice", {"type": "prism", "plan": {"sides": "sides", "radius": "R + gOut + 0.25"}, "height": 0.45, "flatRoof": True, "at": [[0, "H + Hg", 0, 0]], "standsOn": ["gallery"],
                    "_about": "the cornice the roof stands on"})
    # THE HEAD by `crown`: "cone" -- a tall slate cone from the cornice; "battlement" -- crenellations round the cornice
    # and a drum set back behind them under a smaller cone (a keep's lookout)
    add("cone", {"type": "dome", "radius": "capR", "thickness": 0, "sides": "capSides", "head": {"profile": "trigonal", "rise": "capRise"},
                 "at": [[0, "H + Hg + 0.45", 0, 0]], "when": {"crown": "cone"}, "standsOn": ["cornice"], "_about": "crown cone: the tall slate cone, capRise high from capR at its eave"})
    add("battlements", comp("crenellation", {"L": "2 * (R + gOut + 0.2) * sin(3.14159265 / sides) + 0.25", "t": 0.4, "h": "pH", "step": 1.1, "mh": "pH * 0.6", "merlon": "square"},
                            [], spiral={"count": "sides", "radius": "(R + gOut + 0.2) * cos(3.14159265 / sides) - 0.2", "y": "H + Hg + 0.45"}, when={"crown": ["battlement", "platform"]},
                            standsOn=["cornice"], _about="crown battlement or platform: a crenellated parapet round the cornice (whose top is the deck)"))
    add("drum", {"type": "enclosure", "plan": {"sides": "sides", "radius": "dR"}, "thickness": 0.4, "height": "dH", "glass": True, "interior": True,
                 "openings": [{"at": 0, "width": 0.5, "sill": "dH * 0.3", "springing": "dH * 0.7", "head": {"profile": "semicircular"}}],
                 "at": [[0, "H + Hg + 0.45", 0, 0]], "when": {"crown": "battlement"}, "standsOn": ["cornice"], "_about": "the drum set back behind the battlements"})
    add("drum cone", {"type": "dome", "radius": "dR + 0.3", "thickness": 0, "sides": "capSides", "head": {"profile": "trigonal", "rise": "dRise"},
                      "at": [[0, "H + Hg + 0.45 + dH", 0, 0]], "when": {"crown": "battlement"}, "standsOn": ["drum"]})
    add("finial", {"type": "column", "radius": "max(0.06, capR * 0.03)", "height": "finial", "sides": 6, "taper": 0.4, "at": [[0, "H + Hg + 0.45 + capRise - 0.05", 0, 0]],
                   "when": {"crown": "cone"}, "standsOn": ["cone"], "_about": "the vane's rod on the cone's tip"})
    add("drum finial", {"type": "column", "radius": 0.06, "height": "finial", "sides": 6, "taper": 0.4, "at": [[0, "H + Hg + 0.45 + dH + dRise - 0.05", 0, 0]],
                        "when": {"crown": "battlement"}, "standsOn": ["drum cone"]})
    add("flagpole", {"type": "column", "radius": 0.07, "height": "R * 2.2", "sides": 6, "taper": 0.6, "at": [[0, "H + Hg + 0.45", 0, 0]], "when": {"crown": "platform", "flag": "yes"},
                     "standsOn": ["cornice"], "_about": "crown platform, flag yes: a flagpole in the middle of the deck"})
    return {"name": "Round keep",
            "_about": "A ROUND TOWER OF THE GOTHIC REVIVAL CASTLE -- Burg Hohenzollern's Markgrafenturm and Kaiserturm (Stüler, 1850-67): a polygonal (`sides`) shaft R to its corners and "
                      "H tall in `storeys` under string courses, a round-headed window in a sandstone surround in every 4th face (`windows` dense: every 2nd) of each storey but the first, "
                      "a door in face 0 (+z) by `door` yes; at its head a GALLERY STOREY Hg tall carried gOut out on a three-stepped corbel table corH deep, a small round-arched window "
                      "(gW) in every face; a cornice; and by `crown`: \"cone\" -- a tall slate cone capRise high from capR at the eave, a vane's rod `finial`; \"battlement\" -- crenellations "
                      "pH high round the cornice and a drum dR, dH tall set back behind them under a cone dRise; \"platform\" -- the crenellations alone round the flat deck (a flagpole by `flag` yes), for a stage to stand on or a lookout. (Smaller and corbelled: components/cone-turret; square: castle-tower.)",
            "params": {"detail": 4, "sides": 16, "R": 4.5, "H": 24.0, "t": "max(0.5, R * 0.18)", "storeys": 4, "windows": "sparse", "door": "no", "doorW": "min(1.4, R * 0.35)",
                       "doorH": "min(2.8, H / storeys * 0.6)", "winW": "R * 0.2", "Hg": 3.2, "gOut": "R * 0.12", "corH": 1.2, "gW": "R * 0.13",
                       "crown": "cone", "capR": "R + gOut + 0.35", "capRise": "R * 3", "capSides": 24, "finial": "R * 0.5",
                       "pH": 1.1, "dR": "R * 0.62", "dH": 3.0, "dRise": "dR * 2.2", "flag": "no",
                       "_storeys": "2 to 5: the shaft's storeys under string courses",
                       "_windows": "sparse: a window in every 4th face above the first storey; dense: every 2nd",
                       "_crown": "cone: the tall slate cone; battlement: crenellations, a set-back drum and a smaller cone; platform: crenellations round the flat deck"},
            "build": build, "parts": parts}


def write_castle_components():
    OUT("components/round-keep.json", round_keep())


if __name__ == "__main__":
    write_components()
    print("historicism: cone-turret, oriel, castle-tower")
