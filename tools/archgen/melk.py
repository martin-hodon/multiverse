# STIFT MELK (1702-36), the Benedictine abbey over the Danube, from components: the Prälatenhof -- a courtyard
# closed by four `palace-wing`s -- the church at its west side with its twin towers (`domed-tower`, square, under
# bell caps) and the dome over the crossing on its drum, and in front of the church the terrace between the
# library wing and the marble-hall wing, closed at its west end by the curved `curved-gallery` (the Altane).
#   x runs along the abbey (east +x), z across it. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2

N, H, D = 4, 5.0, 14.0                 # storeys, storey height, wing depth
CX0, CX1, CZ = 0.0, 100.0, 36.0        # the courtyard block: x from CX0 to CX1, z within +-CZ
wing = lambda L, n=N, **kw: {"L": L, "D": D, "n": n, "H": H, "roofForm": "hip", "pitch": 38, **kw}

# ---- the Prälatenhof: ONE `court` -- a ring of rooms round the courtyard, its floors and stairs continuous all the
# way round, a gate through its east side into the court, doors from the court into the rooms
add("prelates court", {"type": "court", "plan": {"rect": [CX1 - CX0, 2 * CZ]}, "depth": D, "storeys": N, "storeyH": H, "axis": 3.8,
                       "gate": {"face": 1, "width": 4.2, "height": 5.5}, "roof": {"form": "hip", "pitch": 38}, "courses": True,
                       # (its windows DRESSED -- surround.js: an architrave and a sill each, a cornice over those of the two main floors)
                       "surround": [{"head": False}, {"head": "cornice"}, {"head": "cornice"}, {"head": False}],
                       # (the church's crossing stands against the west wing: no windows into its wall there, and a
                       #  door through from the wing's rooms into the crossing -- the church and the abbey one plan)
                       "joins": [{"face": 3, "at": 0, "width": 18.0 + 2 * 1.6, "door": {"width": 3.0, "height": 4.2}}],
                       "at": [[(CX0 + CX1) / 2, 0, 0, 0]],
                       "_about": "the Prälatenhof: the monastery's four wings round their courtyard, one ring of rooms, entered by the gate in the east wing"})

# ---- the church: nave, crossing with its dome, the west front between two towers
NW, NL, NH = 18.0, 26.0, 24.0          # nave width, length, height
XS = 18.0                              # the crossing square
xc = CX0 - XS / 2                      # the crossing's middle, against the west wing
xn = xc - XS / 2 - NL / 2              # the nave's middle
add("nave", {"type": "enclosure", "plan": {"rect": [NL, NW]}, "thickness": 1.4, "height": NH,
             "tiers": [{"h": 12, "openings": {"pattern": "3", "width": 2.4, "gap": 5.8, "sill": 4, "springing": 9, "head": {"profile": "semicircular"}}},
                       {"openings": {"pattern": "3", "width": 2.2, "gap": 6.0, "sill": 2, "springing": 8, "head": {"profile": "semicircular"}}}],
             "faces": {"1": [{"at": 0, "width": 14.0, "sill": 0, "springing": 14, "head": {"profile": "semicircular"}}],
                       "3": [{"h": 12, "openings": [{"at": 0, "width": 4.0, "sill": 0, "springing": 7.5, "head": {"profile": "semicircular"}}]},
                             {"openings": [{"at": 0, "width": 3.6, "sill": 2.0, "springing": 8.5, "head": {"profile": "semicircular"}}]}]},
             "at": [[xn, 0, 0, 0]],
             "_about": "the nave, two tiers of round-headed windows down each side; its west end the front -- the portal, the great window over it -- and its east end a great arch into the crossing"})
add("nave roof", {"type": "roof", "form": "gable", "width": NW, "length": NL, "pitch": 42, "overhang": 0.5, "at": [[xn, NH, 0, Q]]})
add("crossing", {"type": "enclosure", "plan": {"rect": [XS, XS]}, "thickness": 1.6, "height": NH,
                 "openings": [{"at": 0, "width": 7.0, "sill": 8, "springing": 13, "head": {"profile": "semicircular"}}],
                 "faces": {"3": [{"at": 0, "width": 14.0, "sill": 0, "springing": 14, "head": {"profile": "semicircular"}}],
                           "1": [{"at": 0, "width": 3.0, "sill": 0, "springing": 2.7, "head": {"profile": "semicircular"}}]},   # (the door into the abbey's west wing: its own door, through both walls)
                 "at": [[xc, 0, 0, 0]], "_about": "the crossing: the nave opens into it by a great arch, the transept ends lit by tall windows"})
add("crossing pendentives", {"type": "pendentives", "span": XS - 3.2, "springing": NH - (XS - 3.2) / 2, "sides": 24, "at": [[xc, 0, 0, 0]],
                             "deck": {"thickness": 0.5, "out": 1.2},
                             "_about": "the pendentives inside the crossing, turning its square into the drum's circle, and the roof over its corners round the drum"})
DR = (XS - 3.2) / 2
add("dome", comp("components/drum-dome", {"R": DR, "dt": 0.8, "H": 9.0, "n": 24, "every": 3, "winW": 1.8, "winSill": 2.0, "winH": 4.2,
                                          "profile": "bell", "waist": 0.75, "lift": 0.9, "domeT": 0.8, "lanternR": 1.9, "lanternH": 4.0},
                 [[xc, NH, 0, 0]], _about="the drum with its eight windows, the dome, a Baroque bell, and the lantern"))
# the towers, either side of the front, a little proud of it
TW, TX = 9.0, xn - NL / 2 + 4.5 - 0.3
add("towers", comp("components/domed-tower", {"sides": 4, "R": TW / 2 * 1.4142, "H": 44.0, "t": 1.2, "drumR": 3.4, "drumH": 5.0, "cap": "bell",
                                              "capR": 4.4, "waist": 0.8, "lift": 1.1, "winW": 1.6, "kok": 0.5, "finial": 3.5, "doorH": 5.5, "glazed": 0},
                   [[TX, 0, sz * (NW / 2 + TW / 2 - 2.0), math.pi] for sz in (-1, 1)], build=["tower", "drum", "cap", "finial"],  # (doors to -x, the terrace)
                   _about="the twin towers, square, each under an open lantern stage and a bell cap"))

# ---- the terrace: the library and marble-hall wings, and the curved gallery closing it to the west
TL = 34.0
tx = TX - TW / 2 - TL / 2                  # the terrace wings' middles
tz = NW / 2 + TW - 2.0 + D / 2             # beside the towers
add("library wing", comp("components/palace-wing", wing(TL, n=3), [[tx, 0, -tz, 0]], _about="the library wing, south of the terrace"))
add("marble hall wing", comp("components/palace-wing", wing(TL, n=3), [[tx, 0, tz, math.pi]], _about="the marble-hall wing, north of it"))
GR = tz                                    # the gallery's radius: its ends meet the wings' west ends
add("altane", comp("components/curved-gallery", {"R": GR, "D": 6.0, "H": 7.0, "count": 48, "from": -24, "to": -1, "winW": 2.2, "sill": 0, "terrace": 0},
                   [[tx - TL / 2, 0, 0, 0]], _about="the Altane: the curved gallery closing the terrace, an open arcade toward the river and the valley -- the way onto the terrace"))

doc = {"name": "Stift Melk",
       "_about": "STIFT MELK, the Benedictine abbey over the Danube (1702-36), from components: the Prälatenhof, one `court` -- a ring of rooms round the courtyard, walked all the way round on every storey, entered by its gate; the church at its west side, its nave opening through a great arch into the crossing, where PENDENTIVES carry the drum and the bell-shaped dome with its lantern; its west front between twin square towers (`domed-tower`s, under open lantern stages and bell caps); and in front the terrace between the library wing and the marble-hall wing, closed by the curved gallery (a `curved-gallery`, the Altane).",
       "params": {"detail": 4}, "base": {"height": 0.8, "steps": 3, "stepOut": 0.5, "margin": 4}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/melk.json"), "w").write(json.dumps(doc, indent=2) + "\n")
