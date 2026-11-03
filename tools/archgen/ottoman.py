# THE OTTOMAN PALACE'S VOCABULARY (a style library, L2): the components a palace of the Sultans is built from, written
# here once as parametric definitions and used by any generator that imports this module (topkapi.py first):
#   components/conical-tower.json   a tower of stone -- octagonal or square -- under a tall pointed lead cap (külah) on its
#                                   cornice, an alem on the tip; on a square shaft, by name, a windowed upper stage (a
#                                   cihannüma, the Tower of Justice's kiosk) between the shaft and the cap
#   components/ottoman-portico.json a row of marble columns with faceted capitals carrying pointed arches, under a lead
#                                   shed roof whose deep eave (saçak) runs out over them, its soffit a painted ceiling; a
#                                   back wall of its own with windows (and a door in the middle), or none against a
#                                   building; a small dome over the middle bay by name (the Gate of Felicity's canopy)
#   components/ottoman-kiosk.json   the köşk: a room on a low platform inside a colonnade on all four sides, the whole under
#                                   one low hipped lead roof with deep eaves; by name a dome on a drum over the room (the
#                                   Baghdad Kiosk's) -- the Audience Chamber is the kiosk without the dome
#   (and the domed rows -- the kitchens, the treasury, the Divan's chambers -- are blue_mosque.py's `domed-arcade`, closed
#    by its `front` wall|door|doors, a chimney on every dome by `chimney` yes, two rows back to back by `backWin` arches)
# Every number of a component is a param or an expression over its params; the `_x` keys say what x is. Front +z.
import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = lambda rel, doc: open(os.path.join(ROOT, "assets/architecture", rel), "w").write(json.dumps(doc, indent=2) + "\n")
Q = 1.5707963
POINTED = {"profile": "pointed", "spread": 0.4}            # the Ottoman arch: two centres, a low point
TAN = lambda deg: f"(sin({deg} * 0.0174533) / cos({deg} * 0.0174533))"


def conical_tower():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    poly = {"sides": "sides", "radius": "w / 2 / cos(3.14159265 / sides)"}
    add("shaft", {"type": "prism", "plan": poly, "height": "H", "at": [[0, 0, 0, 0]], "when": {"plan": "polygon"},
                  "courses": [{"y": "beltY", "h": "beltH", "out": "beltOut", "profile": "band"}],
                  "_about": "the stone shaft on its polygon (w across the flats), a belt course at beltY"})
    add("shaft square", {"type": "prism", "plan": {"rect": ["w", "w"]}, "height": "H", "at": [[0, 0, 0, 0]], "when": {"plan": "square"},
                         "courses": [{"y": "beltY", "h": "beltH", "out": "beltOut", "profile": "band"}]})
    add("cornice", {"type": "prism", "plan": {"sides": "sides", "radius": "(w / 2 + corOut) / cos(3.14159265 / sides)"}, "height": "corH",
                    "flatRoof": True, "at": [[0, "H", 0, 0]], "when": {"plan": "polygon"}, "standsOn": ["shaft"],
                    "_about": "the cornice the cap sits on, standing out corOut"})
    add("cornice square", {"type": "prism", "plan": {"rect": ["w + 2 * corOut", "w + 2 * corOut"]}, "height": "corH", "flatRoof": True,
                           "at": [[0, "H", 0, 0]], "when": {"plan": "square"}, "standsOn": ["shaft square"]})
    win = {"at": 0, "width": "uw", "sill": "uSill", "springing": "uSpr", "head": {"profile": "semicircular"}}
    add("upper", {"type": "enclosure", "plan": {"rect": ["wu", "wu"]}, "thickness": "ut", "height": "Hu", "openings": [win], "glass": True,
                  "at": [[0, "H + corH", 0, 0]], "when": {"upper": "yes"}, "standsOn": ["cornice square"],
                  "_about": "the upper stage (upper: yes, a square shaft): a room with a tall round-arched window in every face"})
    add("upper piers", {"type": "box", "width": "uw * 0.22", "length": "uw * 0.22", "height": "Hu",
                        "at": [[f"{a} * (wu / 2)", "H + corH", f"{b} * (wu / 2)", 0] for a, b in ((-1, -1), (-1, 1), (1, -1), (1, 1))],
                        "when": {"upper": "yes", "upperCols": "no"}, "standsOn": ["cornice square"], "_about": "engaged piers at the upper stage's corners"})
    # PAIRED ENGAGED COLUMNS either side of every face's window (upperCols yes: the Tower of Justice's Empire stage): a pair
    # at each end of each face, standing ucR * 0.5 proud of it -- eight pairs, each turned to its face
    ends = []
    for k in range(4):
        for e in (-1, 1):
            x, z = f"{e} * (wu / 2 - ucR * 2.4)", "wu / 2 + ucR * 0.5"
            X, Z = [(x, z), (z, f"0 - ({x})"), (f"0 - ({x})", f"0 - ({z})"), (f"0 - ({z})", x)][k]
            ends.append([X, "H + corH", Z, round(k * Q, 7)])
    add("upper columns", {"type": "colonnade", "order": "corinthian", "count": 2, "spacing": "ucR * 2.6", "columnR": "ucR", "height": "Hu",
                          "at": ends, "when": {"upper": "yes", "upperCols": "yes"}, "standsOn": ["cornice square"],
                          "_about": "upperCols yes: paired engaged columns flanking every face's window"})
    add("upper cornice", {"type": "prism", "plan": {"rect": ["wu + 2 * corOut", "wu + 2 * corOut"]}, "height": "ucH", "flatRoof": True,
                          "at": [[0, "H + corH + Hu", 0, 0]], "when": {"upper": "yes"}, "standsOn": ["upper"]})
    # A SEGMENTAL PEDIMENT over every face (upperPed yes): a slab whose outline is a flat arch pedH high, the cornice's width,
    # standing on the cornice's face -- the cap rising behind the four of them
    add("upper pediments", {"type": "loft", "axis": "z", "half": True, "sides": 16,
                            "sections": [{"s": "wu / 2 + corOut - 0.45", "a": "wu / 2 + corOut", "b": "pedH", "n": 2.6},
                                         {"s": "wu / 2 + corOut", "a": "wu / 2 + corOut", "b": "pedH", "n": 2.6}],
                            "at": [[0, "H + corH + Hu + ucH", 0, round(k * Q, 7)] for k in range(4)], "when": {"upper": "yes", "upperPed": "yes"},
                            "standsOn": ["upper cornice"], "_about": "upperPed yes: a segmental pediment over every face"})
    add("cap", {"type": "dome", "radius": "capR", "thickness": 0, "sides": "capSides", "head": {"profile": "trigonal", "rise": "capH"},
                "at": [[0, "H + corH + Hu + ucH", 0, 0]], "_about": "the külah: a tall pointed lead cap on the cornice"})
    add("alem", {"type": "column", "radius": "capR * 0.05", "height": "capH * 0.22", "sides": 6, "taper": 0.35, "at": [[0, 0, 0, 0]], "atop": "cap",
                 "standsOn": ["cap"], "_about": "the gilt alem on the tip"})
    return {"name": "Conical tower",
            "_about": "A TOWER UNDER A KÜLAH -- the Ottoman palace's: a stone shaft, octagonal (`plan` polygon, `sides`) or square (`plan` square), "
                      "w across its flats and H tall with a belt course at beltY; a cornice standing out corOut, corH deep; on a square shaft an "
                      "upper stage by `upper` yes (Hu tall, wu wide, a tall round-arched window uw wide in each face from uSill to uSpr, corner "
                      "piers or by `upperCols` yes paired engaged columns (ucR) flanking every window, its own cornice ucH, by `upperPed` yes a "
                      "segmental pediment pedH high over every face -- the Tower of Justice's Empire lantern); then the tall pointed lead cap (capR, capH, capSides facets: 16 reads round) and its "
                      "alem. The Middle Gate's two towers, the Tower of Justice. y 0 on the ground. (tools/archgen/ottoman.py)",
            "params": {"detail": 4, "plan": "polygon", "sides": 8, "w": 6.0, "H": 14.0, "beltY": "H * 0.55", "beltH": 0.3, "beltOut": 0.12,
                       "corH": 0.6, "corOut": 0.35, "upper": "no", "Hu": 0, "wu": "w * 0.86", "ut": 0.5, "uw": "wu * 0.4", "ucH": 0,
                       "uSill": "Hu * 0.08", "uSpr": "Hu * 0.75", "upperCols": "no", "ucR": "wu * 0.035", "upperPed": "no", "pedH": "wu * 0.2",
                       "_upperCols": "yes: paired engaged corinthian columns (ucR) either side of every window; no: plain corner piers",
                       "_upperPed": "yes: a segmental pediment pedH high over every face of the upper stage",
                       "capR": "w / 2 + corOut + 0.25", "capH": "w * 1.5", "capSides": 16,
                       "_plan": "polygon (sides) or square", "_Hu": "the upper stage's height: 0 with upper no; with upper yes give Hu and ucH (its cornice)",
                       "_capR": "the cap's radius at its eave: past the cornice, so it overhangs"},
            "build": build, "parts": parts}


def ottoman_portico():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    add("columns", {"type": "colonnade", "order": "ottoman", "count": "n - 1 + endL + endR", "spacing": "B", "columnR": "colR", "height": "colH", "sides": 8,
                    "at": [["(endL - endR) * B / 2 * (0 - 1)", 0, 0, 0]],
                    "_about": "marble columns on the front line (z 0), faceted capitals; an end's column left out (endL, endR 0) where the neighbouring portico's corner column carries it"})
    add("arcade", {"type": "wall", "width": "L + t", "height": "archH", "thickness": "t", "glass": False, "at": [[0, "colH", 0, 0]],
                   "openings": {"pattern": "n", "width": "B - t", "gap": "t", "end": "t", "sill": 0, "springing": "spr", "head": POINTED},
                   "standsOn": ["columns"], "when": {"arches": "yes"}, "_about": "pointed arches from capital to capital, the spandrels between"})
    add("beam", {"type": "box", "width": "L + t", "length": "t", "height": "archH", "at": [[0, "colH", 0, 0]], "standsOn": ["columns"], "when": {"arches": "no"},
                 "_about": "arches no: a beam from capital to capital, the eave straight on it (a canopy's, the Gate of Felicity's)"})
    back = lambda door: {"type": "wall", "width": "L + t", "height": f"colH + archH + (D + eave) * {TAN('pitch')}", "thickness": "bt", "glass": True,
                         "at": [[0, 0, "0 - D - bt / 2", 0]],
                         "tiers": [{"openings": {"every": "B", "width": "wW", "end": "B * 0.7", "sill": "wSill", "springing": "wSpr", "head": POINTED,
                                      **({"with": [{"at": 0, "width": "gW", "sill": 0, "springing": "gS", "head": POINTED, "glass": False}]} if door else {})}}],
                         "repeat": {"count": "back", "step": [0, 0, 0, 0]}, "when": {"door": "yes" if door else "no"}}
    add("back wall", {**back(False), "_about": "the back wall: a pointed window in every bay"})
    add("back wall door", {**back(True), "_about": "the back wall with a door in its middle (door yes)"})
    add("roof", {"type": "roof", "form": "shed", "width": "D + eave + back * bt", "length": "L + t + eaveL + eaveR", "pitch": "pitch",
                 "at": [["(eaveR - eaveL) / 2", "colH + archH", "(eave - D - back * bt) / 2", Q]], "standsOn": ["arcade", "beam"], "when": {"roofForm": "shed"},
                 "_about": "the lead shed roof, from the back wall out over the columns to the deep eave (saçak); its flat soffit the painted ceiling"})
    add("roof hipped", {"type": "roof", "form": "hip", "width": "2 * (D + eave + back * bt)", "length": "L + t + eaveL + eaveR", "pitch": "pitch",
                        "at": [["(eaveR - eaveL) / 2", "colH + archH", "0 - D - back * bt", Q]], "standsOn": ["arcade", "beam"], "when": {"roofForm": "hip"},
                        "_about": "roofForm hip: the eave hipped round its ends too -- a canopy standing free of its neighbours (its back half runs into the building behind)"})
    add("fascia", {"type": "box", "width": "L + t + eaveL + eaveR", "length": 0.18, "height": "fascia", "at": [["(eaveR - eaveL) / 2", "colH + archH - fascia", "eave - 0.09", 0]],
                   "standsOn": ["roof", "roof hipped"], "_about": "the eave's front board"})
    add("drum", {"type": "ring", "count": 16, "rOuter": "domeR + 0.3", "rInner": "domeR", "height": f"(D + eave) * {TAN('pitch')} * 0.6 + 0.9", "solid": True,
                 "place": [[0, "colH + archH", "0 - D * 0.45", 0]], "when": {"dome": "yes"}, "standsOn": ["roof", "roof hipped"],
                 "_about": "the drum of the dome over the middle bay, up through the roof"})
    add("dome", {"type": "dome", "radius": "domeR + 0.3", "thickness": 0.3, "sides": 16, "head": {"profile": "semicircular"},
                 "at": [[0, f"colH + archH + (D + eave) * {TAN('pitch')} * 0.6 + 0.9", "0 - D * 0.45", 0]], "when": {"dome": "yes"}, "standsOn": ["drum"],
                 "_about": "a small lead dome over the middle bay (dome yes)"})
    add("dome alem", {"type": "column", "radius": 0.08, "height": 1.4, "sides": 6, "taper": 0.3, "at": [[0, 0, "0 - D * 0.45", 0]], "atop": "dome", "when": {"dome": "yes"},
                      "standsOn": ["dome"]})
    return {"name": "Ottoman portico",
            "_about": "AN OTTOMAN PORTICO (revak) with its deep eave: n bays B apart along x, centred; marble columns (`ottoman` order, colR, colH) on "
                      "the front line z 0 carrying pointed arches (archH of arcade wall, t thick, springing spr over the capitals) -- or with `arches` no a beam archH deep; a lead shed roof "
                      "from the back (z -D) out past the columns by `eave` (eaveS at the ends), pitch `pitch`, its flat soffit the painted saçak; a "
                      "fascia board on its edge. `back` 1 builds a back wall (bt thick, a pointed window every bay: wW, wSill, wSpr) and `door` yes "
                      "a door in it (gW, gS); `back` 0 stands the roof against another building; with a back wall the roof reaches over it. `dome` yes sets a small dome (domeR) on a drum over "
                      "the middle bay, up through the roof -- the Gate of Felicity's canopy. `endL`/`endR` 0 leave out the column at the -x/+x end: two "
                      "porticoes meeting at a court's corner share one corner column. (The vaulted, arcaded walk is `arcade-walk`; this is the "
                      "timber-roofed Ottoman kind, its eave reaching past the columns.) (tools/archgen/ottoman.py)",
            "params": {"detail": 4, "n": 5, "B": 4.0, "L": "n * B", "colR": 0.28, "colH": 4.2, "t": "colR * 2.6", "spr": 0.25,
                       "archH": "spr + (B - t) * 0.75 + 0.7", "arches": "yes", "D": 5.0, "eave": 2.0, "eaveS": 0.6, "pitch": 10, "fascia": 0.35,
                       "back": 1, "door": "no", "bt": 0.9, "wW": 1.3, "wSill": 1.0, "wSpr": 2.6, "gW": 2.6, "gS": 3.2,
                       "dome": "no", "domeR": "B * 0.42", "endL": 1, "endR": 1, "eaveL": "eaveS", "eaveR": "eaveS", "roofForm": "shed",
                       "_eaveL": "how far the roof runs past the -x end (eaveR the +x): a portico's roof carried on over a court's corner",
                       "_roofForm": "shed (against the building behind) or hip (hipped round its ends: a free-standing canopy)",
                       "_endL": "1: a column at the row's -x end (endR: the +x end); 0: none -- the corner column is the neighbouring portico's",
                       "_D": "from the column line back to the back wall's face; the roof covers D + eave",
                       "_archH": "the arcade wall's height over the capitals: the arches' crown (pointed, about 0.67 of their span over spr) and a band over it; with arches no the beam's",
                       "_arches": "yes: pointed arches between the columns; no: a plain beam on them"},
            "build": build, "parts": parts}


def ottoman_kiosk():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    add("platform", {"type": "box", "width": "W + 2 * G + 1.0", "length": "L + 2 * G + 1.0", "height": "plat", "walked": True, "at": [[0, 0, 0, 0]],
                     "_about": "the low marble platform the kiosk and its colonnade stand on"})
    add("steps", {"type": "flight", "width": "dW + 0.6", "run": 0.34, "rise": "plat / 3", "top": "plat", "base": 0, "landing": 0,
                  "at": [[f"{e} * dX + (dW + 0.6) / 2", 0, "L / 2 + G + 0.5 + plat / (plat / 3) * 0.34", Q] for e in (-1, 1)],
                  "_about": "three steps up the front before each of the two doors"})
    add("colonnade", {"type": "colonnade", "plan": "peristyle", "order": "ottoman", "front": "nf", "side": "ns", "width": "W + 2 * G - 1.0",
                      "length": "L + 2 * G - 1.0", "columnR": "colR", "height": "H", "sides": 8,
                      "entablature": {"h": "beam", "depth": "colR * 2.4"}, "at": [[0, "plat", 0, 0]], "standsOn": ["platform"],
                      "_about": "the colonnade round all four sides, nf columns across the front, ns along the sides (corners in both), carrying a beam"})
    add("room", {"type": "enclosure", "plan": {"rect": ["W", "L"]}, "thickness": "t", "height": "H + beam", "interior": True, "glass": True,
                 "openings": {"every": "wB", "width": "wW", "end": 1.2, "sill": "wSill", "springing": "wSpr", "head": POINTED},
                 "faces": {"0": {"every": "wB", "width": "wW", "end": 1.2, "sill": "wSill", "springing": "wSpr", "head": POINTED,
                                 "with": [{"at": "0 - dX", "width": "dW", "sill": 0, "springing": "dS", "head": POINTED, "glass": False},
                                          {"at": "dX", "width": "dW", "sill": 0, "springing": "dS", "head": POINTED, "glass": False}]}},
                 "at": [[0, "plat", 0, 0]], "standsOn": ["platform"],
                 "_about": "the room: windows all round, two doors in the front (dX either side of the middle) with the gift window between"})
    add("ceiling", {"type": "box", "width": "W - 2 * t", "length": "L - 2 * t", "height": 0.3, "at": [[0, "plat + H + beam - 0.3", 0, 0]], "standsOn": ["room"]})
    add("roof", {"type": "roof", "form": "hip", "width": "W + 2 * G + 2 * eave", "length": "L + 2 * G + 2 * eave", "pitch": "pitch",
                 "at": [[0, "plat + H + beam", 0, 0]], "standsOn": ["room", "colonnade"],
                 "_about": "one low hipped lead roof over room and colonnade, its deep eave out past the columns"})
    add("drum", {"type": "ring", "count": 16, "rOuter": "domeR + 0.4", "rInner": "domeR", "height": f"min(W, L) / 2 * {TAN('pitch')} + 1.2", "solid": True,
                 "place": [[0, "plat + H + beam", 0, 0]], "when": {"dome": "yes"}, "standsOn": ["room"]})
    add("dome", {"type": "dome", "radius": "domeR + 0.4", "thickness": 0.4, "sides": 16, "head": {"profile": "semicircular"},
                 "at": [[0, f"plat + H + beam + min(W, L) / 2 * {TAN('pitch')} + 1.2", 0, 0]], "when": {"dome": "yes"}, "standsOn": ["drum"],
                 "_about": "the dome over the room on its drum, up through the roof (dome yes: the Baghdad Kiosk's)"})
    add("alem", {"type": "column", "radius": 0.1, "height": 1.8, "sides": 6, "taper": 0.3, "at": [[0, 0, 0, 0]], "atop": "dome", "when": {"dome": "yes"},
                 "standsOn": ["dome"]})
    return {"name": "Ottoman kiosk",
            "_about": "THE KÖŞK: a room W x L, H tall to the beam, on a platform `plat` high (steps up the front before each door), inside a colonnade G deep on all "
                      "four sides (`ottoman` columns, nf across the front and ns along the sides, corners counted in both, a `beam` on them), the whole "
                      "under one low hipped lead roof (pitch) whose deep eave reaches `eave` past the columns; windows all round every wB (wW wide), "
                      "two doors in the front dX either side of the middle. `dome` yes sets a dome (domeR) on a drum over the room, up through the roof. "
                      "The Audience Chamber (Arz Odası) is this with 22 columns; the Baghdad and Yerevan kiosks with the dome. (tools/archgen/ottoman.py)",
            "params": {"detail": 4, "W": 16.0, "L": 18.0, "H": 6.0, "t": 1.0, "G": 3.2, "plat": 0.45, "colR": 0.3, "nf": 7, "ns": 6, "beam": 0.5,
                       "eave": 2.4, "pitch": 16, "wB": 3.2, "wW": 1.2, "wSill": 0.9, "wSpr": 3.0, "dW": 1.8, "dS": 3.0, "dX": 3.0, "dome": "no", "domeR": "min(W, L) * 0.32",
                       "_G": "the colonnade's depth: the column axes stand G - 0.5 out from the room's walls"},
            "build": build, "parts": parts}


def write_components():
    OUT("components/conical-tower.json", conical_tower())
    OUT("components/ottoman-portico.json", ottoman_portico())
    OUT("components/ottoman-kiosk.json", ottoman_kiosk())


comp = lambda use, params, at, **kw: {"type": "component", "use": f"components/{use}", "params": params, "at": at, **kw}

if __name__ == "__main__":
    write_components()
    print("ottoman: conical-tower, ottoman-portico, ottoman-kiosk")
