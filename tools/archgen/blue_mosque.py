# THE BLUE MOSQUE (Sultan Ahmed Mosque), Istanbul (Sedefkar Mehmed Agha, 1609-16), from components -- and the
# components themselves, each written once here:
#   components/dome-cascade.json    the classical Ottoman hall: a dome on four piers and pendentives, a SEMIDOME on
#                                   each side on its half ring of arcades and windows, two EXEDRAE cut into each
#                                   semidome, a small dome over each corner bay, the roofs between, turrets on the piers
#   components/domed-arcade.json    a straight row of square bays, each under a small dome on pendentives: pointed
#                                   arcade in front, arched cross walls between, a back wall with windows and a gate
#   components/riwaq.json           the arcaded portico round a courtyard: four `domed-arcade` rows, corners in the
#                                   rows along x, any side left out (`sF` `sB` `sL` `sR`), any back wall left out
#   components/ottoman-minaret.json the `minaret`'s shaft and balconies (its balconies set by `tier`, the first high up
#                                   on a tall plinth), a stretch of shaft over the last, and the lead pencil cap on it
# and assets/architecture/blue-mosque.json: the hall (`dome-cascade`, its dome 23.5m across and 43m high inside), its
# walls, the forecourt as large as the hall inside a `riwaq` of 32 domed bays, the ablution fountain, the monumental
# gateway, and six `ottoman-minaret`s (four of three balconies at the hall's corners, two of two at the court's).
#   The qibla is +z; the forecourt lies -z of the hall. Everything is metres. Run: python3 tools/archgen/blue_mosque.py
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = lambda rel, doc: open(os.path.join(ROOT, "assets/architecture", rel), "w").write(json.dumps(doc, indent=2) + "\n")
Q = math.pi / 2
f = lambda v: f"{v:.6f}".rstrip("0").rstrip(".")                     # a number inside an expression
POINTED = {"profile": "pointed", "spread": 0.4}                       # the Ottoman arch: two centres, a low point


def rot(a, x, z):
    """(x, z) expressions turned by a quarter-turn multiple a about the origin (yaw: x cos a + z sin a, -x sin a + z cos a)"""
    k = round(a / Q) % 4
    neg = lambda e: f"0 - ({e})" if e not in ("0", 0) else 0
    return [(x, z), (z, neg(x)), (neg(x), neg(z)), (neg(z), x)][k]


YAWS = [0, Q, math.pi, -Q]                                            # the four sides: +z, +x, -z, -x


# =================================================================================================================
# dome-cascade
# =================================================================================================================
def dome_cascade():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    RN = 18                                           # the half rings' polygon: a bay on the axis, edges at 90
    HALF = [0, 1, 2, 3, 4, 14, 15, 16, 17]            # the bays facing away from the middle (bay k centred at 20k deg)
    EX = [2, 16]                                      # the bays the exedrae open from (+-40 deg)
    side = lambda y: [[rot(a, 0, "z0")[0], y, rot(a, 0, "z0")[1], round(a, 6)] for a in YAWS]

    add("piers", {"type": "box", "width": "P", "length": "P", "height": "RING",
                  "at": [[f"{sx} * (R + P / 2)", 0, f"{sz} * (R + P / 2)", 0] for sx in (-1, 1) for sz in (-1, 1)],
                  "_about": "the four great piers -- the 'elephant feet' -- up to the pendentives' top"})
    add("great arches", {"type": "barrel", "width": "2 * R", "length": "P", "springing": "SPR", "top": "RING + dk2", "head": {"profile": "semicircular"},
                         "at": [[0, 0, "0 - R", 0], [0, 0, "R + P", 0], ["0 - R", 0, 0, Q], ["R + P", 0, 0, Q]],
                         "_about": "the four arches from pier to pier: the dome's ring on their crowns, a semidome under each"})
    add("pendentives", {"type": "pendentives", "span": "2 * R", "springing": "SPR", "sides": "n", "deck": {"thickness": "dk2", "out": "P"},
                        "at": [[0, 0, 0, 0]], "_about": "the pendentives, and the roof over the piers round the drum's foot"})
    add("dome", {"type": "component", "use": "components/drum-dome",
                 "params": {"R": "R", "dt": "dt", "H": "dH", "n": "n", "every": 1, "winW": "winW", "winSill": "winSill", "winH": "winH",
                            "profile": "semicircular", "domeT": "domeT"},
                 "build": ["drum", "dome"], "at": [[0, "RING + dk2", 0, 0]], "standsOn": ["pendentives"],
                 "_about": "the drum, a window in every bay, and the dome on it"})
    add("alem", {"type": "column", "radius": 0.35, "height": 4.5, "sides": 8, "taper": 0.2,
                 "at": [[0, "RING + dk2 + dH + R + dt", 0, 0]], "standsOn": ["dome"], "_about": "the gilded finial on the dome's crown"})
    add("turrets", {"type": "prism", "plan": {"sides": 8, "radius": "tR"}, "height": "tH",
                    "at": [[f"{sx} * (R + P / 2)", "RING + dk2", f"{sz} * (R + P / 2)", 0] for sx in (-1, 1) for sz in (-1, 1)],
                    "flatRoof": True, "standsOn": ["pendentives"], "_about": "the octagonal weight turrets over the piers"})
    add("turret caps", {"type": "dome", "radius": "tR * 1.05", "thickness": 0, "head": {"profile": "semicircular"}, "sides": 8, "turn": 0.5,
                        "at": [[f"{sx} * (R + P / 2)", "RING + dk2 + tH", f"{sz} * (R + P / 2)", 0] for sx in (-1, 1) for sz in (-1, 1)],
                        "standsOn": ["turrets"]})
    add("turret finials", {"type": "column", "radius": 0.12, "height": 1.6, "sides": 6, "taper": 0.3,
                           "at": [[f"{sx} * (R + P / 2)", "RING + dk2 + tH + tR * 1.05", f"{sz} * (R + P / 2)", 0] for sx in (-1, 1) for sz in (-1, 1)],
                           "standsOn": ["turret caps"]})

    # ---- the four semidomes on their half rings: an arcade below the roofs, a ring of windows over them
    add("half rings", {"type": "ring", "count": RN, "rOuter": "R", "rInner": "R - ringT", "height": "ROOFt", "at": HALF, "place": side(0),
                       "opening": {"width": "aW", "sill": 0, "springing": "aS", "head": POINTED}, "glass": False,
                       "_about": "the ground storey of each half ring: pointed arches out into the space behind -- and, 40 degrees either side of the axis, into the exedrae"})
    add("half ring windows", {"type": "ring", "count": RN, "rOuter": "R", "rInner": "R - ringT", "height": "SPR - ROOFt", "y": "ROOFt",
                              "at": [b for b in HALF if b not in EX], "place": side(0), "standsOn": ["half rings"],
                              "opening": {"width": "wW", "sill": "wSill", "springing": "wSill + wH", "head": POINTED},
                              "_about": "the windows round each semidome's foot, over the roofs"})
    add("half ring blind", {"type": "ring", "count": RN, "rOuter": "R", "rInner": "R - ringT", "height": "SPR - ROOFt", "y": "ROOFt",
                            "at": EX, "place": side(0), "solid": True, "standsOn": ["half rings"],
                            "_about": "the bays behind which the exedrae rise: blind, closing their half domes"})
    add("semidomes", {"type": "dome", "sweep": 0.5, "sides": RN, "radius": "R", "thickness": "ringT", "head": {"profile": "semicircular"},
                      "at": side("SPR"), "standsOn": ["half ring windows"],
                      "_about": "the four semidomes, their crowns under the great arches' -- the cascade round the dome"})
    # the exedrae: half domes on half rings, their chords on the half ring's inside face at +-40 deg
    ex = []
    for a in YAWS:
        for s in (-1, 1):
            th = s * math.radians(40)
            x, z = rot(a, f"Ce * {f(math.sin(th))}", f"z0 + Ce * {f(math.cos(th))}")
            ex.append([x, 0, z, round(a + th, 6)])
    add("exedrae", {"type": "component", "use": "components/apse",
                    "params": {"R": "exR", "T": "exT", "H": "exH", "n": 12, "winW": "exWinW", "winSill": "exWinSill", "winH": "exWinH", "domeT": "exT"},
                    "at": ex, "_about": "two exedrae cut into each semidome's foot (`apse`): a half ring of windows over the roofs and a half dome"})

    # ---- the side arches from each pier to the outer wall, the corner bays' pendentives and domes
    sa = []
    for a in YAWS:
        for sx in (-1, 1):
            x, z = rot(a, "R + P" if sx > 0 else "0 - R", "(z0 + W) / 2")
            sa.append([x, 0, z, round(a + Q, 6)])
    add("side arches", {"type": "barrel", "width": "C", "length": "P", "springing": "SA", "top": "ROOFt", "head": {"profile": "semicircular"},
                        "at": sa, "_about": "the arches from each pier out to the wall, between a semidome's bay and the corner bays"})
    corners = [[f"{sx} * (z0 + W) / 2", 0, f"{sz} * (z0 + W) / 2", 0] for sx in (-1, 1) for sz in (-1, 1)]
    add("corner pendentives", {"type": "pendentives", "span": "C", "springing": "SA", "sides": "cn", "deck": {"thickness": "dk", "out": 0.02},
                               "at": corners, "_about": "the corner bays' pendentives, on the side arches and the outer walls"})
    add("corner drums", {"type": "ring", "count": "cn", "rOuter": "C / 2 + cdt", "rInner": "C / 2", "height": "cdH", "turn": 0.5, "y": "ROOFt",
                         "opening": {"width": "cWinW", "sill": 0.3, "springing": "cdH - 0.3 - cWinW / 2", "head": {"profile": "semicircular"}},
                         "place": corners, "standsOn": ["corner pendentives"]})
    add("corner domes", {"type": "dome", "sides": "cn", "turn": -0.5, "radius": "C / 2 + cdt", "thickness": "cdt", "head": {"profile": "semicircular"},
                         "at": [[x, "ROOFt + cdH", z, 0] for x, _, z, _ in corners], "standsOn": ["corner drums"],
                         "_about": "a small dome over each corner bay"})
    add("corner finials", {"type": "column", "radius": 0.15, "height": 2.0, "sides": 6, "taper": 0.25,
                           "at": [[x, "ROOFt + cdH + C / 2 + cdt", z, 0] for x, _, z, _ in corners], "standsOn": ["corner domes"]})

    # ---- the roofs over the spaces behind the half rings, round the exedrae (+z's plan, turned to each side)
    def ring_pt(deg):
        r = math.radians(deg)
        return [f"R * {f(math.sin(r))}", f"z0 + R * {f(math.cos(r))}"]
    def ex_pt(s, xl, yl):                           # a point in the exedra's own frame (x' across, y' out) -> hall
        th = s * math.radians(40); c, sn = math.cos(th), math.sin(th)
        return [f"Ce * {f(sn)} + ({xl}) * {f(c)} + ({yl}) * {f(sn)}", f"z0 + Ce * {f(c)} - ({xl}) * {f(sn)} + ({yl}) * {f(c)}"]
    def exedra(s):
        pts = [ex_pt(s, "0 - qx", "qy")]
        for b in (-60, -30, 0, 30, 60):
            r = math.radians(b)
            pts.append(ex_pt(s, f"Ro * {f(math.sin(r))}", f"Ro * {f(math.cos(r))}"))
        return pts + [ex_pt(s, "qx", "qy")]
    plan = [["R", "z0"], ["R", "W"], ["0 - R", "W"], ["0 - R", "z0"], ring_pt(-70)] + exedra(-1) + [ring_pt(-10), ring_pt(10)] + exedra(1) + [ring_pt(70)]
    add("roofs", {"type": "prism", "plan": {"points": plan}, "height": "dk", "flatRoof": True,
                  "at": [[0, "ROOF", 0, round(a, 6)] for a in YAWS],
                  "_about": "the flat roofs over the spaces behind each half ring, cut round it and round its exedrae"})

    # ---- the walls round the whole (a building may leave them out and write its own)
    win = lambda sill, spr: {"pattern": "3-5-3", "width": "oW", "gap": "oGap", "pier": "oPier", "sill": sill, "springing": spr, "head": POINTED}
    low, up = win(1.5, 4.2), win(1.0, 3.6)
    door = {"width": "doorW", "sill": 0, "springing": "doorS", "glass": False}
    add("walls", {"type": "enclosure", "plan": {"rect": ["2 * (W + T)", "2 * (W + T)"]}, "thickness": "T", "height": "ROOFt + par", "interior": "ROOFt",
                  "tiers": [{"h": "tierH", "openings": low}, {"openings": up}],
                  "faces": {"1": [{"h": "tierH", "openings": {**low, "middle": door}}, {"openings": up}],
                            "3": [{"h": "tierH", "openings": {**low, "middle": door}}, {"openings": up}],
                            "2": [{"h": "tierH", "openings": [{"at": 0, "head": POINTED, **door}, {"at": "doorX", "head": POINTED, **door},
                                                              {"at": "0 - doorX", "head": POINTED, **door}]}, {"openings": up}]},
                  "at": [[0, 0, 0, 0]],
                  "_about": "the outer walls, two rows of windows clear of the side arches; a door in the middle of +x and -x, three in -z; +z (the qibla) blind below"})

    # ---- the spaces over the roofs (the walls' interior stops at their top): the crossing between the piers and under
    # the great arches up to the drum's foot, each half ring's up to its semidome, the corner drums -- the domes' and the
    # semidomes' insides are their own (not in `build`: interiors come with the whole)
    parts["crossing"] = {"type": "interior", "of": ["piers"], "height": "RING + dk2 - ROOFt", "at": [[0, "ROOFt", 0, 0]],
                         "plan": {"points": [["R", "R"], ["R", "z0"], ["0 - R", "z0"], ["0 - R", "R"], ["0 - z0", "R"], ["0 - z0", "0 - R"],
                                             ["0 - R", "0 - R"], ["0 - R", "0 - z0"], ["R", "0 - z0"], ["R", "0 - R"], ["z0", "0 - R"], ["z0", "R"]]},
                         "_about": "the crossing over the roofs: the square between the piers and the great arches' spans, up to the drum's foot"}
    parts["semidome bays"] = {"type": "interior", "of": ["half rings"], "plan": {"sides": RN, "radius": "R - ringT / 2"}, "arc": [-90, 90],
                              "height": "SPR - ROOFt", "at": side("ROOFt"), "_about": "inside each half ring's windows, over the roofs, up to its semidome"}
    parts["corner drum spaces"] = {"type": "interior", "of": ["corner drums"], "plan": {"sides": "cn", "radius": "C / 2 + cdt / 2"}, "height": "cdH",
                                   "at": [[x, "ROOFt", z, 0] for x, _, z, _ in corners], "_about": "inside the corner domes' drums"}

    params = {
        "detail": 4,
        "R": 11.75, "_R": "half the square under the dome (the dome's inside radius); P the piers; G the passage between each half ring's crown and the wall",
        "P": 5.0, "G": 2.0, "T": 2.5,
        "SPR": 16.0, "_SPR": "where the great arches, the pendentives and the semidomes spring",
        "RING": "SPR + R", "dk2": 1.0, "_dk2": "the deck round the drum's foot",
        "dH": 3.2, "n": 28, "dt": 0.8, "domeT": 0.8, "winW": 1.1, "winSill": 0.4, "winH": 1.8,
        "_n": "the dome's drum: n windows (a multiple of four: the pendentives meet it corner for corner)",
        "ROOFt": 12.0, "_ROOFt": "the top of the roofs round the half rings, and of the walls; the corner bays' pendentives reach up to its underside",
        "dk": 0.6, "ROOF": "ROOFt - dk", "C": "R + G", "W": "2 * R + P + G", "z0": "R + P", "SA": "ROOF - C / 2",
        "_W": "the walls' inside, from the middle; C the corner bays; z0 where each semidome's half ring stands; SA the side arches' springing",
        "ringT": 1.0, "aW": 2.6, "aS": 7.0, "wW": 1.4, "wSill": 0.5, "wH": 2.1,
        "_aW": "the half rings' arcade (aW wide, springing aS) and the windows over the roofs (wW, wSill, wH)",
        "exR": 3.3, "exT": 0.6, "exH": "SPR - 1.5", "exWinW": 0.9, "exWinSill": "ROOFt + 0.3", "exWinH": 1.3,
        "_exR": "the exedrae: exR inside, exT walls, exH where their half domes spring; their windows over the roofs. Their outline must cross the half ring's between 60 and 90 degrees off their axis (the roofs are cut round it): (exR + exT) about a third of R",
        "Ce": "R - ringT", "Ro": "exR + exT",
        "ia": "0.267949 * Ro * Ro", "ib": "2 * Ro * (0 - 0.133975 * Ro - 0.5 * Ce)", "ic": "0.75 * Ro * Ro + (0.5 * Ro + Ce) * (0.5 * Ro + Ce) - R * R",
        "it": "(0 - ib - sqrt(ib * ib - 4 * ia * ic)) / (2 * ia)", "qx": "Ro * (0.866025 + 0.133975 * it)", "qy": "Ro * (0.5 - 0.5 * it)",
        "_qx": "where an exedra's outer face (its last bay, 60 to 90 degrees off its axis) crosses the half ring's outside, in the exedra's frame: the roofs' plan turns there",
        "cn": 16, "cdH": 1.6, "cdt": 0.5, "cWinW": 0.7, "_cn": "the corner domes: cn sides, a drum cdH high with a window in every bay",
        "tR": 1.7, "tH": 4.5,
        "tierH": 6.0, "par": 0.9, "_par": "the walls' parapet over the roofs", "oW": 1.6, "oGap": 2.6, "oPier": 7.6, "doorW": 3.0, "doorS": 3.8, "doorX": 21.0,
        "_oPier": "the walls' windows: blocks of 3, 5, 3 with the side arches' ends (P wide) between them; doorX the -z face's side doors",
    }
    return {"name": "Dome cascade",
            "_about": "THE CLASSICAL OTTOMAN HALL (the Sehzade, the Blue Mosque, the Yeni Cami): a dome on a drum of windows over four great piers, arches and pendentives; on each side a SEMIDOME on its half ring -- an arcade below the roofs, windows above -- with two EXEDRAE (`apse`) cut into its foot 40 degrees either side; a small dome on pendentives over each corner bay, carried by the side arches from the piers to the walls; flat roofs round the half rings, turrets on the piers, and the walls round it all. Centred on the dome; +z is the qibla (its wall has no door). The whole plan is 2 * (W + T) square.",
            "params": params, "build": build, "parts": parts}


# =================================================================================================================
# domed-arcade: a straight row of domed bays
# =================================================================================================================
def domed_arcade():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    rep = lambda count, dx="B": {"count": count, "step": [dx, 0, 0, 0]}
    add("arcade", {"type": "wall", "width": "arcL", "height": "crown", "thickness": "p", "at": [[0, 0, "p / 2", 0]], "glass": False,
                   "openings": {"pattern": "n", "width": "ow", "gap": "B - ow", "end": "(arcL - n * B + B - ow) / 2", "sill": 0, "springing": "os", "head": POINTED},
                   "_about": "the arcade to the court: a pointed arch in every bay, on the row's front line (z = 0)"})
    add("cross walls", {"type": "wall", "width": "s", "height": "crown", "thickness": "p", "glass": False,
                        "openings": [{"at": "s / 2", "width": "cw", "sill": 0, "springing": "cs", "head": POINTED}],
                        "at": [["B - L / 2 + p / 2", 0, "0 - B / 2", Q]], "repeat": rep("n - 1"),
                        "_about": "the arched walls between the bays"})
    add("end walls", {"type": "wall", "width": "B - p + p * back", "height": "crown", "thickness": "p", "openings": [],
                      "at": [["p / 2 - L / 2", 0, "0 - (B + p * back) / 2", Q]], "repeat": rep("2 * ends", "L"),
                      "_about": "the walls closing the row's two ends (`ends` 1), round the corner of the back wall"})
    add("back wall", {"type": "wall", "width": "L - p", "height": "crown + dk + 0.6", "thickness": "p", "at": [[0, 0, "0 - B - p / 2", math.pi]],
                      "repeat": {"count": "back", "step": [0, 0, 0, 0]},
                      "openings": {"pattern": "half-1-half", "width": "wW", "gap": "B - wW", "pier": "B - (wW + gW) / 2", "end": "(B - p - wW) / 2", "sill": "wSill", "springing": "wSpr",
                                   "head": POINTED, "middle": {"width": "gW", "sill": 0, "springing": "gS", "glass": False}},
                      "_about": "the back wall: a window in every bay, and in the middle of an odd row a gate"})
    bay = lambda y: [["B / 2 - L / 2", y, "0 - B / 2", 0]]
    add("pendentives", {"type": "pendentives", "span": "s", "springing": "SP", "sides": "cn", "deck": {"thickness": "dk", "out": "p / 2"},
                        "at": bay(0), "repeat": rep("n"), "_about": "every bay's pendentives, and the roof round its drum"})
    add("drums", {"type": "ring", "count": "cn", "rOuter": "s / 2 + dt", "rInner": "s / 2", "height": "dh", "turn": 0.5, "solid": True,
                  "place": bay("crown + dk"), "repeat": rep("n"), "standsOn": ["pendentives"]})
    add("domes", {"type": "dome", "sides": "cn", "turn": -0.5, "radius": "s / 2 + dt", "thickness": "dt", "head": {"profile": "semicircular"},
                  "at": bay("crown + dk + dh"), "repeat": rep("n"), "standsOn": ["drums"], "_about": "a small lead dome over every bay"})
    add("finials", {"type": "column", "radius": 0.08, "height": 1.0, "sides": 6, "taper": 0.3,
                    "at": bay("crown + dk + dh + s / 2 + dt"), "repeat": rep("n"), "standsOn": ["domes"]})
    # the row's space, from the arcade's middle to the back wall's -- a row with no back of its own (`back` 0) reaching
    # past the middle of the wall it stands against -- up to the pendentives' top; and each drum's, up to its dome
    parts["bays space"] = {"type": "interior", "plan": {"rect": ["L", "B + (1 - back) * p"]}, "height": "crown",
                           "at": [[0, 0, "0 - (B + (1 - back) * p) / 2", 0]],
                           "_about": "the walk under the domes, closed but for its arcade: finished as a room, its floor and its back wall's inside"}
    parts["drum spaces"] = {"type": "interior", "plan": {"sides": "cn", "radius": "s / 2 + dt / 2"}, "height": "dk + dh",
                            "at": bay("crown"), "repeat": rep("n")}
    params = {"detail": 4, "n": 5, "B": 7.0, "p": 1.3, "_B": "the bays' pitch, pier axis to pier axis; p the piers and every wall; n the bays",
              "L": "n * B", "s": "B - p", "arcL": "L + p", "_arcL": "the arcade's length: L + p from the outer faces of its end piers, L - p between two other rows' arcades",
              "SP": 4.2, "crown": "SP + s / 2", "_SP": "where the pendentives spring; crown their top, the walls' height",
              "ow": 3.8, "os": 4.0, "cw": 3.2, "cs": 3.6, "_ow": "the arcade's arches (ow wide, springing os) and the cross walls' (cw, cs)",
              "wW": 1.4, "wSill": 1.2, "wSpr": 3.2, "gW": 3.6, "gS": 4.0, "_gW": "the gate in the middle of the back wall (an odd n)",
              "dk": 0.4, "dh": 0.8, "dt": 0.3, "cn": 12, "_cn": "the domes: cn sides (a multiple of four), a drum dh high, dt thick",
              "half": "(n - 1) / 2", "_half": "the back wall's windows either side of the gate: n is odd, 3 or more (a gate gW = wW is one more window)",
              "back": 1, "ends": 1, "_back": "1: a back wall of its own; 0: the row stands against another building's wall. ends 1: walls closing both ends"}
    return {"name": "Domed arcade",
            "_about": "A ROW OF DOMED BAYS -- the portico of an Ottoman mosque, a medrese's cells' gallery, a caravanserai's arcade: n square bays B apart along x, centred on x = 0; a pointed ARCADE along the front (z = 0, facing +z), arched CROSS WALLS between the bays, a BACK WALL (at z = -B) with a window in every bay and a gate in the middle, and over every bay PENDENTIVES, a low drum and a small dome. The bays' clear square is B - p; the piers and walls are p thick.",
            "params": params, "build": build, "parts": parts}


# =================================================================================================================
# riwaq: four rows of domed bays round a court
# =================================================================================================================
def riwaq():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    common = {k: k for k in ("B", "p", "SP", "ow", "os", "cw", "cs", "wW", "wSill", "wSpr", "gW", "gS", "dk", "dh", "dt", "cn")}
    row = lambda n, arcL, ends, back, at, flag, about: {
        "type": "component", "use": "components/domed-arcade", "params": {**common, "n": n, "arcL": arcL, "ends": ends, "back": back},
        "at": [at], "repeat": {"count": flag, "step": [0, 0, 0, 0]}, "_about": about}
    add("front", row("nx + 2", "(nx + 2) * B + p", 1, "bF", [0, 0, "0 - hz", 0], "sF", "the row along -z, its corner bays at both ends"))
    add("back", row("nx + 2", "(nx + 2) * B + p", 1, "bB", [0, 0, "hz", math.pi], "sB", "the row along +z, its corner bays at both ends"))
    add("left", row("nz", "nz * B - p", 0, "bL", ["0 - hx", 0, 0, Q], "sL", "the row along -x, between the corner bays"))
    add("right", row("nz", "nz * B - p", 0, "bR", ["hx", 0, 0, -Q], "sR", "the row along +x, between the corner bays"))
    params = {"detail": 4, "nx": 7, "nz": 7, "B": 7.0, "p": 1.3,
              "_nx": "the court: nx by nz bays between the arcades' pier axes (odd, for a gate in the middle of each back wall); B the bays, p the piers and walls",
              "hx": "nx * B / 2", "hz": "nz * B / 2",
              "sF": 1, "sB": 1, "sL": 1, "sR": 1, "_sF": "which sides have a row (1) -- front -z, back +z, left -x, right +x",
              "bF": 1, "bB": 1, "bL": 1, "bR": 1, "_bF": "which rows have a back wall of their own (0: they stand against a building -- a mosque's hall)",
              "SP": 4.2, "ow": 3.8, "os": 4.0, "cw": 3.2, "cs": 3.6, "wW": 1.4, "wSill": 1.2, "wSpr": 3.2, "gW": 3.6, "gS": 4.0,
              "dk": 0.4, "dh": 0.8, "dt": 0.3, "cn": 12}
    return {"name": "Riwaq",
            "_about": "A RIWAQ: the arcaded portico round a mosque's courtyard -- a pointed arcade under a row of small domes on every side (`domed-arcade`), the corner bays in the rows along x, the gates in the middle of the back walls. Centred on the court; its arcades' pier axes are nx * B by nz * B, and the portico reaches B - p / 2 beyond them to the back walls' inside (p more to their outside). A side is left out with its flag (sF sB sL sR); a row standing against a hall has no back wall of its own (bF bB bL bR).",
            "params": params, "build": build, "parts": parts}


# =================================================================================================================
# ottoman-minaret
# =================================================================================================================
def ottoman_minaret():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    add("pedestal", {"type": "prism", "plan": {"sides": 8, "radius": "r * 1.55"}, "height": "foot", "at": [[0, 0, 0, 0]], "flatRoof": True,
                     "_about": "the tall polygonal base, up to the roofs"})
    add("minaret", {"type": "component", "use": "components/minaret",
                    "params": {"h": "h", "r": "r", "balconies": "balconies", "bw": "bw", "tier": "tier"},
                    "build": ["plinth", "shaft", "corbelling", "balcony", "parapet"], "at": [[0, "foot", 0, 0]], "standsOn": ["pedestal"],
                    "_about": "the `minaret` on it: its plinth (1.2m), the shaft and its balconies, one every `tier` from the plinth's top"})
    add("cap", {"type": "dome", "radius": "r * 1.08", "thickness": 0, "sides": 16, "head": {"profile": "trigonal", "rise": "capRise"},
                "at": [[0, "foot + 1.2 + h", 0, 0]], "standsOn": ["minaret"], "_about": "the lead pencil cap on the shaft's head"})
    add("finial", {"type": "column", "radius": "r * 0.07", "height": "r * 1.3", "sides": 6, "taper": 0.3, "at": [[0, 0, 0, 0]], "atop": "cap", "standsOn": ["cap"]})
    params = {"detail": 4, "foot": 11.0, "h": 42.0, "r": 2.0, "balconies": 3, "tier": 10.0, "bw": 1.0, "capRise": "r * 4",
              "_foot": "the pedestal; on it the `minaret`'s own plinth (1.2m, its default) and the shaft, h tall",
              "_tier": "a balcony every `tier` from the plinth's top -- fewer than h / tier, so the shaft runs on over the last; the cap `capRise` tall"}
    return {"name": "Ottoman minaret",
            "_about": "AN OTTOMAN MINARET: slender, on a tall polygonal pedestal, `balconies` balconies high up the shaft (the `minaret` component on the pedestal, its balconies spaced by `tier` rather than filling the shaft), the shaft running on above the last, and the pencil cap -- a tall lead cone -- with its finial.",
            "params": params, "build": build, "parts": parts}


# =================================================================================================================
# the Blue Mosque
# =================================================================================================================
def blue_mosque():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
    R, P, G, T = 11.75, 5.0, 2.0, 2.5
    W = 2 * R + P + G
    HO = W + T                                         # the hall's outside, from its middle (65m square)
    add("hall", comp("components/dome-cascade", {"R": R, "P": P, "G": G, "T": T}, [[0, 0, 0, 0]],
                     _about="the prayer hall (`dome-cascade`): the dome 23.5m across on four elephant-foot piers and pendentives, 43m high inside; four semidomes, each with two exedrae; four corner domes; turrets on the piers; the walls, three doors from the court"))

    # ---- the forecourt: a riwaq of 7 by 7 bays between the arcades, as large as the hall
    B, p, nx, nz = 7.0, 1.3, 7, 7
    hz = nz * B / 2
    ZC = -HO - (hz + B - p / 2)                       # the court's middle: its +z row stands against the hall's wall
    add("riwaq", comp("components/riwaq", {"nx": nx, "nz": nz, "B": B, "p": p, "bB": 0}, [[0, 0, ZC, 0]],
                      _about="the forecourt's portico (`riwaq`): 32 domed bays on pointed arcades round the court, the gates in the middle of three sides; its fourth row the hall's own portico, against its wall"))
    far = ZC - hz - B - p / 2                          # the court's outside, -z
    add("gateway", {"type": "wall", "width": 12.0, "height": 15.0, "thickness": 3.0, "at": [[0, 0, far, 0]], "glass": False,
                    "openings": [{"at": 6.0, "width": 5.0, "sill": 0, "springing": 8.5, "head": POINTED}],
                    "_about": "the monumental gateway: a tall portal block before the court's main gate, its pointed arch the passage"})
    add("gateway crest", {"type": "box", "width": 12.6, "length": 3.6, "height": 0.8, "at": [[0, 15.0, far - 1.5, 0]], "flatRoof": True, "standsOn": ["gateway"]})
    add("gateway dome", {"type": "dome", "radius": 1.5, "thickness": 0, "sides": 12, "head": {"profile": "semicircular"},
                         "at": [[0, 15.8, far - 1.5, 0]], "standsOn": ["gateway crest"], "_about": "the little dome on the gateway"})
    # ---- the ablution fountain in the court's middle
    add("fountain basin", {"type": "prism", "plan": {"sides": 6, "radius": 1.9}, "height": 0.9, "at": [[0, 0, ZC, 0]], "flatRoof": True,
                           "_about": "the sadirvan: a hexagonal fountain under a canopy on six columns"})
    add("fountain columns", {"type": "colonnade", "plan": "round", "order": "tuscan", "count": 6, "radius": 3.0, "columnR": 0.22, "height": 3.6,
                             "sides": 8, "at": [[0, 0, ZC, 0]]})
    add("fountain eave", {"type": "prism", "plan": {"sides": 6, "radius": 3.9}, "height": 0.35, "at": [[0, 3.6, ZC, 0]], "flatRoof": True,
                          "standsOn": ["fountain columns"]})
    add("fountain dome", {"type": "dome", "radius": 3.1, "thickness": 0, "sides": 12, "head": {"profile": "semicircular"},
                          "at": [[0, 3.95, ZC, 0]], "standsOn": ["fountain eave"]})

    # ---- six minarets
    M = HO + 2.6
    add("minarets", comp("components/ottoman-minaret", {"h": 42.0, "r": 2.0, "foot": 11.0, "balconies": 3, "tier": 12.0},
                         [[sx * M, 0, sz * M, 0] for sx in (-1, 1) for sz in (-1, 1)],
                         _about="the four minarets at the hall's corners, three balconies each"))
    cx = (nx + 2) * B / 2 + p / 2 + 2.6
    add("court minarets", comp("components/ottoman-minaret", {"h": 32.0, "r": 1.8, "foot": 7.0, "balconies": 2, "tier": 12.0},
                               [[sx * cx, 0, far - 2.0, 0] for sx in (-1, 1)],
                               _about="the two at the forecourt's far corners, two balconies each"))

    return {"name": "Blue Mosque",
            "_about": "THE BLUE MOSQUE (Sultan Ahmed Mosque), Istanbul, 1609-16, from components: the prayer hall is a `dome-cascade` -- the dome 23.5m across and 43m high inside on four elephant-foot piers and pendentives, a semidome on every side with two exedrae cut into it, the four corner domes, turrets on the piers, the walls with their rows of windows; the forecourt, as large as the hall, inside a `riwaq` of small domes on pointed arcades, its hall-side row the hall's portico; the hexagonal ablution fountain; the monumental gateway; six `ottoman-minaret`s with pencil caps -- four of three balconies at the hall's corners, two of two at the court's far corners.",
            "params": {"detail": 4}, "base": {"height": 0.6, "steps": 3, "stepOut": 0.5, "margin": 3}, "railing": {"type": "stone"},
            "build": build, "parts": parts}


OUT("components/dome-cascade.json", dome_cascade())
OUT("components/domed-arcade.json", domed_arcade())
OUT("components/riwaq.json", riwaq())
OUT("components/ottoman-minaret.json", ottoman_minaret())
OUT("blue-mosque.json", blue_mosque())
