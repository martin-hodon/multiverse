"""THE WESTERN ISLAMIC KIT: the components al-Andalus built with, from Cordoba's caliphate (10th c.) to the Nasrids (14th c.).

Run: python3 tools/archgen/andalusi.py -- writes assets/architecture/components/<name>.json for each below. The
buildings (cordoba.py, alhambra.py) only place them; a third Andalusi building should need nothing new here.

  cordoban-arcade   the Mezquita's two-tier arcade, one line of N bays: columns, their impost blocks, the lower
                    horseshoe arch braced between them, and the pier wall above carrying the upper arches and the roof
                    gutter. Both arches are `arch` parts (voussoir bands: the red-and-white striping is their finish,
                    mapped round their own centre), their heads words -- so the same line is the plain hall's
                    (horseshoe over semicircle) or al-Hakam II's maqsura's (polylobed, interlaced: `interlace` yes)
  alminar           the square minaret of Abd al-Rahman III: a shaft with paired horseshoe windows and a band of
                    blind arches, the stepped-merlon terrace, the muezzin's lantern with its dome and the yamur
                    (the golden balls on their rod)
  bab               a portal: the doorway's horseshoe arch of red-and-white voussoirs in its ALFIZ (the rectangular
                    frame), blind polylobed arches over it, a carved eave on corbels and stepped merlons -- Cordoba's
                    gates; Nasrid gates use it unmerloned under a deep eave
  nasrid-portico    a Nasrid portico: slender columns with cubic capitals, stilted round arches, the pierced SEBKA
                    (the lattice of lozenges) over them, a carved wooden eave and a tiled roof: the Court of the Myrtles'
                    ends, the Court of the Lions' galleries, the Partal
  qubba             a square domed room raised as a tower over its neighbours: walls with windows in the drum, a
                    muqarnas dome inside (cells in rings, set by kit.muqarnas_dome), a tiled pyramid roof -- the Two
                    Sisters', the Abencerrajes', the Lions' pavilions
  torre             a Nasrid wall tower: a solid foot, a hall storey with its windows, a terrace with merlons
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import Doc, r4, Q, muqarnas_dome

COMP = "assets/architecture/components/"


def ball_sections(r, n=6):
    """a loft's sections for a ball of radius r, its foot at s 0"""
    return [{"s": r4(r - r * math.cos(math.pi * k / n)), "a": r4(max(.01, r * math.sin(math.pi * k / n))), "b": r4(max(.01, r * math.sin(math.pi * k / n)))}
            for k in range(n + 1)]


# (RELIEF -- a frame, a blind arcade -- stands on the face it decorates with its back exactly in that face: the support check
#  holds a part fixed where a corner of it touches another's surface, and a relief sunk into the wall touches none)

# =====================================================================================================================
# CORDOBAN ARCADE
# =====================================================================================================================
def cordoban_arcade():
    D = Doc()
    head = lambda w: {"profile": w, "over": w + "Over", "lobes": w + "Lobes"}
    D.add("columns", {"type": "colonnade", "plan": "straight", "count": "N + 2 * ends - 1", "spacing": "bay", "order": "order", "columnR": "colR", "height": "colH",
                      "at": [[0, 0, 0, 0]]}, "the columns, one under every pier: reused Roman and Visigothic shafts, new caliphal capitals")
    D.add("imposts", {"type": "box", "width": "impW", "length": "t + 0.08", "height": "impH", "at": [["-(N + 2 * ends - 2) * bay / 2", "colH", 0, 0]],
                      "repeat": {"count": "N + 2 * ends - 1", "step": ["bay", 0, 0, 0]}},
          "the impost block on every capital, long along the arcade: the lower arches spring from its ends, the pier stands in its middle")
    D.add("piers", {"type": "wall", "width": "N * bay + pierW * (2 * ends - 1)", "height": "top - colH - impH", "thickness": "t", "glass": False,
                    "openings": {"pattern": "N", "width": "bay - pierW", "gap": "pierW", "end": "pierW * ends", "sill": 0,
                                 "springing": "upSpr - colH - impH", "head": head("up")},
                    "at": [[0, "colH + impH", "t / 2", 0]]},   # (a wall stands behind its face: t/2 centres it on the columns)
          "the wall over the columns: a pier on every impost, the upper arches between them, the gutter on its top")
    D.add("lower arches", {"type": "arch", "width": "bay - pierW", "depth": "lowD", "thickness": "lowT", "head": head("low"),
                           "at": [["-N * bay / 2 + bay / 2", "colH + impH", 0, 0]], "repeat": {"count": "N", "step": ["bay", 0, 0, 0]}},
          "the lower arches, braced from impost to impost -- horseshoes in the hall, polylobed in the maqsura")
    D.add("upper arches", {"type": "arch", "width": "bay - pierW", "depth": "upD", "thickness": "t + 0.04", "head": head("up"),
                           "at": [["-N * bay / 2 + bay / 2", "upSpr", 0, 0]], "repeat": {"count": "N", "step": ["bay", 0, 0, 0]}},
          "the upper arches, from pier to pier: the ones that carry")
    D.add("interlaced arches", {"type": "arch", "width": "2 * bay - pierW", "depth": "ilD", "thickness": "t + 0.1", "head": head("up"),
                                "at": [["-N * bay / 2 + bay", "upSpr", 0, 0]], "repeat": {"count": "N - 1", "step": ["bay", 0, 0, 0]}, "when": {"interlace": "yes"}},
          "al-Hakam II's interlacing: an arch from every pier to the next but one, so that each crosses its neighbours")
    return D.write(COMP + "cordoban-arcade.json", "Cordoban arcade",
                   "A CORDOBAN ARCADE (the Great Mosque of Cordoba, 785-988): one line of N bays `bay` apart along x, centred, `t` thick "
                   "along z, standing on the floor. Columns (`order` caliphal) `colH` to the top of the capital, an impost block `impH` on "
                   "each, the LOWER arch (head `low`: horseshoe in the hall) braced between the imposts, and over the imposts a wall of "
                   "PIERS `pierW` wide carrying the UPPER arches (head `up`: semicircular) and the gutter at `top`. The heads are words, "
                   "`low`/`up` + Over and Lobes their numbers: horseshoe, semicircular or lobed. `interlace` yes adds al-Hakam II's "
                   "interlaced arches, each from a pier to the next but one. The two tiers are what let the hall stand 9.8 m on "
                   "columns 3 m tall: the lower arch braces, the upper carries (Hernandez Gimenez; Ewert). `ends` 0 leaves out the end "
                   "columns and piers: a run between two others that already stand on them (or a screen between two arcades).",
                   params={"detail": 4, "N": 12, "bay": 3.15, "ends": 1, "order": "caliphal", "colR": .22, "colH": 3.6, "impH": .35, "impW": "pierW + 2 * lowD",
                           "pierW": .8, "t": 1.07, "top": 9.805,
                           "low": "horseshoe", "lowOver": .3, "lowLobes": 5, "lowD": .42, "lowT": "t * 0.78",
                           "up": "semicircular", "upOver": 0, "upLobes": 5, "upSpr": 6.335, "upD": .45,
                           "interlace": "no", "ilD": .32})


# =====================================================================================================================
# ALMINAR
# =====================================================================================================================
def alminar():
    D = Doc()
    hs = {"profile": "horseshoe", "over": .35}
    pair = [{"at": f"{sg} * pw * 0.75", "width": "pw", "sill": "ts * 0.3", "springing": "ts * 0.6167", "head": hs} for sg in (-1, 1)]
    blind = {"pattern": "bn", "width": "bw", "gap": "bw * 0.4286", "sill": "bh * 0.3", "springing": "bh * 0.55", "head": {"profile": "lobed", "lobes": 3, "over": .25}}
    D.add("shaft", {"type": "enclosure", "plan": {"rect": ["W", "W"]}, "thickness": "tw", "height": "H", "glass": False,
                    "tiers": [{"h": "H - 2 * ts - bh - th", "openings": []}, {"h": "ts", "openings": pair}, {"h": "ts", "openings": pair},
                              {"h": "bh", "openings": blind}, {"h": "th", "openings": []}]},
          "the shaft, 8.5 m square: blind below, two storeys of paired horseshoe windows, the band of nine blind arches under the top")
    D.add("core", {"type": "prism", "plan": {"rect": ["W - 2 * tw + 0.02", "W - 2 * tw + 0.02"]}, "height": "H", "flatRoof": True},
          "its masonry core between the two stairs (the windows are the stairs' lights: niches here)")
    for k, (x, z, yaw, L) in enumerate([(0, "W / 2 - 0.225", 0, "W"), (0, "0.225 - W / 2", math.pi, "W"),
                                         ("W / 2 - 0.225", 0, -Q, "W - 0.9"), ("0.225 - W / 2", 0, Q, "W - 0.9")]):
        D.add(f"merlons {k + 1}", {"type": "component", "use": "components/crenellation",
                                   "params": {"L": L, "t": .45, "h": .7, "step": 1.05, "mh": .85, "merlon": "stepped"}, "at": [[x, "H", z, r4(yaw)]]},
              "the terrace's parapet of stepped merlons" if k == 0 else None)
    D.add("lantern", {"type": "enclosure", "plan": {"rect": ["lw", "lw"]}, "thickness": .55, "height": "lh", "glass": False, "interior": True,
                      "openings": [{"at": 0, "width": "lw * 0.3864", "sill": 0, "springing": "lh * 0.5357", "head": hs}], "at": [[0, "H", 0, 0]]},
          "the muezzin's lantern: one horseshoe arch in every face")
    D.add("lantern cornice", {"type": "box", "width": "lw + 0.4", "length": "lw + 0.4", "height": .3, "at": [[0, "H + lh", 0, 0]]})
    D.add("lantern dome", {"type": "dome", "radius": "lw / 2", "thickness": 0, "sides": 8, "head": {"profile": "semicircular"},
                           "at": [[0, "H + lh + 0.3", 0, 0]]}, "its little ribbed dome")
    D.add("yamur", {"type": "column", "radius": .05, "height": "yam", "sides": 6, "taper": .6, "at": [[0, "H + lh + 0.3 + lw / 2 - 0.05", 0, 0]]},
          "the YAMUR: an iron rod through three gilt balls, the largest lowest")
    for k, (r, f) in enumerate(((.55, .18), (.42, .42), (.3, .64))):
        D.add(f"yamur ball {k + 1}", {"type": "loft", "axis": "y", "sides": 12, "sections": ball_sections(r),
                                      "at": [[0, f"H + lh + 0.3 + lw / 2 + yam * {f}", 0, 0]]})
    return D.write(COMP + "alminar.json", "Alminar",
                   "AN ALMINAR, the square minaret of al-Andalus -- Abd al-Rahman III's at Cordoba (951-958): a shaft `W` square and `H` "
                   "to its terrace (walls `tw` round a solid core: the two stairs ran in them), blind below, two storeys `ts` tall of paired "
                   "horseshoe windows `pw` wide, a band `bh` tall of `bn` blind lobed arches `bw` wide, and `th` of plain wall to the top; a parapet of stepped merlons; the muezzin's "
                   "lantern `lw` square and `lh` tall with a horseshoe arch in each face and a small dome; the yamur on it, a rod "
                   "through three gilt balls. Centred on its placement, standing on it.",
                   params={"detail": 4, "W": 8.5, "H": 34.0, "tw": 1.5, "lw": 4.4, "lh": 5.6, "yam": 4.0,
                           "ts": 6.0, "pw": 1.0, "bh": 4.0, "bn": 9, "bw": .42, "th": 3.0})


# =====================================================================================================================
# BAB
# =====================================================================================================================
def bab():
    D = Doc()
    hs = {"profile": "horseshoe", "over": "over"}
    D.add("front", {"type": "wall", "width": "W", "height": "H", "thickness": "D", "glass": False,
                    "openings": [{"at": "W / 2", "width": "dw", "sill": 0, "springing": "ds", "head": hs}], "at": [[0, 0, "D", 0]]},   # (its back on z 0, its face on z D)
          "the frontispiece, standing proud of the wall it is set in, the doorway through it")
    D.add("voussoirs", {"type": "arch", "width": "dw", "depth": "vd", "thickness": "D + 0.06", "head": hs, "at": [[0, "ds", "D / 2", 0]]},
          "the doorway's arch: red and white voussoirs radiating from its centre, not from the springing")
    D.add("alfiz head", {"type": "box", "width": "2 * ax + 0.3", "length": .12, "height": .3, "at": [[0, "ay", "D + 0.06", 0]]},
          "the ALFIZ: the moulded frame round the arch, from the imposts to over its crown")
    D.add("alfiz sides", {"type": "box", "width": .3, "length": .12, "height": "ay + 0.3 - ds + 0.4", "at": [["-ax", "ds - 0.4", "D + 0.06", 0], ["ax", "ds - 0.4", "D + 0.06", 0]]})
    D.add("blind arcade", {"type": "arch", "width": "bw", "depth": .16, "thickness": .1, "head": {"profile": "lobed", "lobes": 5, "over": .3},
                           "at": [["-(bn - 1) / 2 * (bw + 0.5)", "ay + 0.9", "D + 0.05", 0]], "repeat": {"count": "bn", "step": ["bw + 0.5", 0, 0, 0]}},
          "over the alfiz a row of blind polylobed arches")
    D.add("blind colonnettes", {"type": "box", "width": .14, "length": .1, "height": .9, "at": [["-(bn - 1) / 2 * (bw + 0.5) - bw / 2 - 0.16", "ay", "D + 0.05", 0]],
                                "repeat": {"count": "bn + 1", "step": ["bw + 0.5", 0, 0, 0]}})
    D.add("eave", {"type": "box", "width": "W + 0.5", "length": "D + 0.45", "height": .32, "at": [[0, "H", "(D + 0.45) / 2 - 0.02", 0]]},
          "the eave on its carved corbels (modillones de rollos)")
    D.add("corbels", {"type": "box", "width": .22, "length": .55, "height": .28, "at": [["-(W - 0.6) / 2", "H - 0.28", "D + 0.2", 0]],
                      "repeat": {"count": "round((W - 0.6) / 0.55) + 1", "step": ["(W - 0.6) / round((W - 0.6) / 0.55)", 0, 0, 0]}})
    D.add("merlons", {"type": "component", "use": "components/crenellation", "params": {"L": "W", "t": .4, "h": .25, "step": .95, "mh": .8, "merlon": "stepped"},
                      "at": [[0, "H + 0.32", "D / 2", 0]], "when": {"crest": "merlons"}},
          "Cordoba's stepped merlons on top")
    return D.write(COMP + "bab.json", "Bab",
                   "A BAB, the gate of al-Andalus: a frontispiece `W` wide, `H` tall and `D` proud of the wall behind it (its back at z 0, "
                   "its face toward +z), with a doorway `dw` wide springing at `ds` under a horseshoe (`over`) of voussoirs `vd` deep; "
                   "round the arch the ALFIZ, a rectangular frame from the imposts to over the crown; above it `bn` blind polylobed "
                   "arches on colonnettes; a carved eave on corbels; and (`crest` merlons) stepped merlons on top. The wall it stands "
                   "on needs its own doorway behind it.",
                   params={"detail": 4, "W": 5.8, "H": 8.4, "D": .45, "dw": 2.3, "ds": 3.2, "over": .32, "vd": "dw * 0.27",
                           "ax": "dw / 2 + vd + 0.35", "ay": "ds + dw / 2 * over + sqrt(dw * dw / 4 * (1 + over * over)) + vd + 0.3",
                           "bn": 5, "bw": "min(0.75, (W - 1.2) / bn - 0.5)", "crest": "merlons"})


# =====================================================================================================================
# CORDOBAN LANTERN
# =====================================================================================================================
def cordoban_lantern():
    D = Doc()
    D.add("walls", {"type": "enclosure", "plan": {"rect": ["W", "L"]}, "thickness": "t", "height": "h", "glass": False, "interior": "h + 0.35 + R * 0.9",
                    "openings": {"pattern": "2", "width": .8, "gap": 1.3, "sill": "h - 2.4", "springing": "h - 1.2",
                                 "head": {"profile": "lobed", "lobes": 3, "over": .3}}},
          "the lantern's walls, standing on the arcades round the bay: two lobed windows in every face, the light falling on the mosaics")
    D.add("deck", {"type": "prism", "plan": {"rect": ["W", "L"], "well": {"radius": "R", "sides": 8}}, "height": .35, "flatRoof": True, "at": [[0, "h", 0, 0]]},
          "the square's corners closed up to the dome's octagon (Cordoba's squinches, as a deck)")
    D.add("dome", {"type": "dome", "radius": "R", "sides": 8, "thickness": .3, "head": {"profile": "semicircular"}, "at": [[0, "h + 0.35", 0, 0]]},
          "the ribbed dome: eight ribs crossing in an eight-pointed star, a little scalloped cupola in the middle (the finish draws them)")
    return D.write(COMP + "cordoban-lantern.json", "Cordoban lantern",
                   "A CORDOBAN LANTERN (al-Hakam II's maqsura and the Villaviciosa bay, 961-965): a skylit dome raised over one bay of the "
                   "hall -- walls `W` by `L` (`t` thick) standing on the arcades round the bay to `h` over them, two lobed windows in "
                   "every face; a deck closing the square's corners to the octagon; the ribbed dome of radius `R` on it. Placed on the "
                   "arcades' top, centred on the bay.",
                   params={"detail": 4, "W": 7.85, "L": 9.45, "t": .7, "h": 3.4, "R": "min(W, L) / 2 - 0.7"})


# =====================================================================================================================
# NASRID PORTICO
# =====================================================================================================================
def nasrid_portico():
    D = Doc()
    D.add("columns", {"type": "colonnade", "plan": "straight", "count": "N + 1", "spacing": "bay", "order": "nasrid", "columnR": "colR", "height": "colH",
                      "at": [[0, 0, 0, 0]], "when": {"pairs": "no"}},
          "the slender marble columns, ringed at the neck, under their cubic capitals")
    for k, sgn in enumerate((-1, 1)):
        D.add(f"columns {'ab'[k]}", {"type": "colonnade", "plan": "straight", "count": "N + 1", "spacing": "bay", "order": "nasrid", "columnR": "colR", "height": "colH",
                                     "at": [[f"{sgn} * pairGap / 2", 0, 0, 0]], "when": {"pairs": "yes"}},
              "or a pair on every pier (the Court of the Lions' corners and pavilions)" if k == 0 else None)
    D.add("arcade", {"type": "wall", "width": "N * bay + pierW", "height": "H - colH", "thickness": "t", "glass": False,
                     "openings": {"pattern": "N", "width": "bay - pierW", "gap": "pierW", "end": "pierW", "sill": 0, "springing": "spr",
                                  "head": {"profile": "head", "over": "over", "lobes": "lobes"}},
                     "at": [[0, "colH", "t / 2", 0]]},
          "the wall the columns carry, the arches cut in it -- stilted, their jambs running straight up from the capitals -- "
          "and over them the SEBKA, the net of lozenges in plaster (the finish's)")
    D.add("ceiling", {"type": "box", "width": "N * bay + pierW", "length": "d + t / 2", "height": .25, "at": [[0, "H - 0.25", "(t / 2 - d) / 2", 0]]},
          "the gallery's wooden ceiling, from the arcade back to the wall behind")
    D.add("eave", {"type": "box", "width": "N * bay + pierW + 0.6", "length": "eave + t", "height": .22, "at": [[0, "H", "eave / 2", 0]]},
          "the carved wooden eave on its brackets, far out over the arcade")
    D.add("roof", {"type": "roof", "form": "shed", "width": "d + eave + t / 2", "length": "N * bay + pierW + 0.6", "pitch": "pitch",
                   "at": [[0, "H + 0.22", "(t / 2 + eave - d) / 2", Q]], "when": {"roof": "yes"}},
          "a roof of tiles falling to the eave (`roof` no: the building roofs it)")
    return D.write(COMP + "nasrid-portico.json", "Nasrid portico",
                   "A NASRID PORTICO (the Alhambra, 14th c.): N arches `bay` apart along x, centred, the arcade's middle on z 0 and the gallery "
                   "behind it, `d` deep toward -z (the wall at -d is the building's). Columns of the `nasrid` order `colH` to the top of their "
                   "cubic capitals -- `pairs` yes sets two on every pier, `pairGap` apart -- carrying a wall `t` thick and up to `H` in which "
                   "the arches are cut, stilted: their jambs `spr` straight up from the capitals, `pierW` apart, under heads of any profile "
                   "(`head` semicircular, or lobed with `lobes`; `over` a horseshoe's). A wooden ceiling, the eave `eave` out on the court "
                   "side, and (`roof` yes) a shed roof of tiles `pitch` degrees over it all, high against the back wall.",
                   params={"detail": 4, "N": 7, "bay": 2.6, "colR": .14, "colH": 2.9, "pairs": "no", "pairGap": "colR * 2.6", "H": 5.8, "t": .55,
                           "d": 3.4, "pierW": .5, "spr": 1.2, "head": "semicircular", "over": 0, "lobes": 5, "eave": .9, "pitch": 24, "roof": "yes"})


# =====================================================================================================================
# QUBBA
# =====================================================================================================================
MUQ = muqarnas_dome()


def qubba():
    D = Doc()
    D.add("walls", {"type": "enclosure", "plan": {"rect": ["W", "W"]}, "thickness": "t", "height": "h", "glass": False, "interior": "h - dr + R * 0.95",
                    "tiers": [{"h": "h - dr - wh", "openings": [{"at": 0, "width": "dw", "sill": 0, "springing": "ds", "head": {"profile": "semicircular"}}]},
                              {"h": "wh", "openings": {"pattern": "win", "width": .7, "gap": .9, "sill": .5, "springing": "wh - 0.7",
                                                       "head": {"profile": "semicircular"}}},
                              {"h": "dr", "openings": []}]},
          "the room's walls: a great arch in every face below (its alcoves, its doorway), the drum of little windows over them, "
          "the walls carried on up round the dome's foot to the roof")
    D.add("squinches", {"type": "prism", "plan": {"rect": ["W - 2 * t + 0.02", "W - 2 * t + 0.02"], "well": {"radius": "R - 0.15", "sides": 16}},
                        "height": .5, "flatRoof": True, "at": [[0, "h - dr - 0.5", 0, 0]]},
          "the square's corners closed to the dome's ring (muqarnas squinches, here a plain deck: the finish carves it)")
    D.add("dome", {"type": "dome", "radius": "R", "thickness": .3, "sides": 16, "head": {"profile": "semicircular"}, "at": [[0, "h - dr", 0, 0]]},
          "the dome, springing from the drum's top")
    D.add("muqarnas", {"type": "box", "width": "R * 0.2", "length": "R * 0.16", "height": "R * 0.13",
                       "at": [[f"R * {r4(x * .9)}", f"h - dr + R * {r4(y * .93 - .1)}", f"R * {r4(z * .9)}", r4(yaw)] for x, y, z, yaw in MUQ]},
          "the MUQARNAS: thousands of prisms in plaster (here a cell for every few), hung in rings under the dome, the rings "
          "climbing to the star at its crown -- the Two Sisters', the Abencerrajes'")
    D.add("roof", {"type": "roof", "form": "pyramid", "width": "W + 0.6", "length": "W + 0.6", "pitch": "pitch", "at": [[0, "h", 0, 0]]},
          "a pyramid of tiles over it, rising over the roofs round it: the qubba seen from outside")
    return D.write(COMP + "qubba.json", "Qubba",
                   "A QUBBA, the Nasrid domed hall (the Alhambra's Two Sisters, Abencerrajes, the Lions' pavilions): a square room `W` across "
                   "(walls `t`) and `h` tall to its eaves, centred, standing on its placement. A great arch `dw` wide springing at `ds` in "
                   "every face below; over them a drum `wh` tall with `win` windows in every face; and from `dr` under the eaves the "
                   "dome of radius `R`, lined with MUQARNAS (cells in rings, from kit.muqarnas_dome), under a pyramid roof of tiles "
                   "`pitch` degrees. A face the building closes (it backs on another room) the building walls up.",
                   params={"detail": 4, "W": 9.0, "t": .9, "h": 13.0, "R": "W / 2 - t", "dr": "R * 0.55", "wh": 2.4, "win": 2,
                           "dw": "W * 0.36", "ds": "h * 0.32", "pitch": 26})


# =====================================================================================================================
# TORRE
# =====================================================================================================================
def torre():
    D = Doc()
    D.add("shaft", {"type": "enclosure", "plan": {"rect": ["W", "L"]}, "thickness": "tw", "height": "H", "glass": False,
                    "tiers": [{"h": "H - hw", "openings": []},
                              {"h": "hw", "openings": {"pattern": "win", "width": "ww", "gap": "ww * 0.9", "sill": "wsill", "springing": "wspr",
                                                       "head": {"profile": "horseshoe", "over": .2}}}]},
          "the tower: a blind mass of rammed earth and rubble below, the hall storey over it lit by its windows (a tower-palace's: "
          "the Ladies', the Captive's)")
    D.add("core", {"type": "prism", "plan": {"rect": ["W - 2 * tw + 0.02", "L - 2 * tw + 0.02"]}, "height": "H - hw", "flatRoof": True},
          "its solid foot, the hall's floor on it")
    D.add("deck", {"type": "box", "width": "W - 2 * tw + 0.02", "length": "L - 2 * tw + 0.02", "height": .4, "at": [[0, "H - 0.4", 0, 0]],
                   "when": {"crest": "merlons"}}, "the hall's ceiling, the terrace on it")
    for k, (x, z, yaw, Ln) in enumerate([(0, "L / 2 - 0.25", 0, "W"), (0, "0.25 - L / 2", math.pi, "W"),
                                          ("W / 2 - 0.25", 0, -Q, "L - 1.0"), ("0.25 - W / 2", 0, Q, "L - 1.0")]):
        D.add(f"merlons {k + 1}", {"type": "component", "use": "components/crenellation",
                                   "params": {"L": Ln, "t": .5, "h": 1.0, "step": 2.0, "mw": 1.0, "mh": 1.1, "merlon": "square"},
                                   "at": [[x, "H", z, r4(yaw)]], "when": {"crest": "merlons"}},
              "the terrace's breastwork and square merlons" if k == 0 else None)
    D.add("roof", {"type": "roof", "form": "hip", "width": "W + 0.5", "length": "L + 0.5", "pitch": 27, "at": [[0, "H", 0, 0]], "when": {"crest": "roof"}},
          "or (`crest` roof) a hipped roof of tiles, as a tower-palace has")
    return D.write(COMP + "torre.json", "Torre",
                   "A NASRID WALL TOWER: `W` along the wall's line (x) by `L` out from it (z), centred, `H` from its foot to the terrace, walls "
                   "`tw` thick round a solid core; its top storey `hw` tall a hall with `win` horseshoe windows `ww` wide in every face (from `wsill` over its floor, springing "
                   "at `wspr`), and on "
                   "top (`crest`) a terrace behind square merlons, or a hipped roof.",
                   params={"detail": 4, "W": 9.0, "L": 8.0, "H": 18.0, "tw": 1.4, "hw": 5.5, "win": 1, "ww": 1.1, "wsill": 1.0,
                           "wspr": "hw - 1.3 - ww / 2", "crest": "merlons"})


if __name__ == "__main__":
    cordoban_lantern()
    cordoban_arcade()
    alminar()
    bab()
    nasrid_portico()
    qubba()
    torre()
