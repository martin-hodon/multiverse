# KARLSKIRCHE, Vienna (1716-37), from components: the church round in plan (an enclosure of sixteen faces for its
# oval), on it a drum of windows and the tall dome with its lantern; before it a Corinthian PORTICO, a temple front
# of six columns under a pediment; either side of the portico one of the two GIANT COLUMNS (Trajan's column, twice)
# on its pedestal with a lantern on its capital; and the facade running out from the portico on both sides to a
# gate PAVILION at each end, its arch walked through, under a curved roof.
#   The front faces +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2

R, T, BH = 16.0, 1.6, 26.0                 # the church: radius, walls, height
DR, DT, DH = 12.0, 1.0, 9.0                # the drum
# ---- the church, its roof ring, the drum, the dome, the lantern
add("church", {"type": "enclosure", "plan": {"sides": 16, "radius": R}, "thickness": T, "height": BH,
               "tiers": [{"h": 13, "openings": [{"at": 0, "width": 2.4, "sill": 4.0, "springing": 9.0, "head": {"profile": "semicircular"}}]},
                         {"openings": [{"at": 0, "width": 2.2, "sill": 2.0, "springing": 7.5, "head": {"profile": "segmental", "seg": 0.4}}]}],
               "faces": {k: [{"h": 13, "openings": [{"at": 0, "width": 4.0 if k == "0" else 2.4, "sill": 0, "springing": 8.0 if k == "0" else 3.6,
                                                    "head": {"profile": "semicircular"}}]},
                             {"openings": [{"at": 0, "width": 2.2, "sill": 2.0, "springing": 7.5, "head": {"profile": "segmental", "seg": 0.4}}]}]
                         for k in ("0", "2", "14")},
               "at": [[0, 0, 0, 0]], "_about": "the church, round (the real one is an oval): two tiers of windows, the door behind the portico, and doors into the side halls"})
apo = R * math.cos(math.pi / 16) - T        # its walls' inner face
add("roof ring", {"type": "ring", "count": 16, "rOuter": round(apo / math.cos(math.pi / 16), 4), "rInner": DR, "height": 0.6, "y": BH - 0.6, "turn": 0.5,
                  "solid": True, "place": [[0, 0, 0, 0]], "_about": "the flat roof round the drum, from the church's walls in to it"})
add("dome", comp("components/drum-dome", {"R": DR, "dt": DT, "H": DH, "n": 16, "every": 2, "winW": 2.0, "winSill": 2.0, "winH": 4.4,
                                          "profile": "pointed", "spread": 0.8, "domeT": DT, "lanternR": 2.2, "lanternH": 5.0},
                 [[0, BH, 0, 0]], _about="the drum with eight windows, the dome -- taller than a hemisphere, a steep pointed section -- and its lantern"))

# ---- the portico
PW, PD, CH, PZ = 22.0, 10.0, 13.0, R - 1.0     # portico width, depth, column height, where it meets the church
add("portico steps", {"type": "crepidoma", "width": PW, "length": PD, "steps": 4, "stepH": 0.2, "stepOut": 0.5,
                      "at": [[0, 0, PZ + PD / 2, 0]], "_about": "the portico's steps"})
add("portico columns", {"type": "colonnade", "order": "corinthian", "count": 6, "spacing": 4.0, "columnR": 0.7, "height": CH, "taper": 0.86,
                        "entablature": {"h": 2.2, "depth": 1.8}, "at": [[0, 0.8, PZ + PD - 1.2, 0]],
                        "_about": "six Corinthian columns and their entablature: a Greek temple's front"})
add("portico side columns", {"type": "colonnade", "order": "corinthian", "count": 2, "spacing": 4.0, "columnR": 0.7, "height": CH, "taper": 0.86,
                             "entablature": {"h": 2.2, "depth": 1.8}, "at": [[sx * 10.0, 0.8, PZ + PD / 2 - 1.2, Q] for sx in (-1, 1)]})
add("pediment", {"type": "roof", "form": "gable", "width": PW, "length": PD + 1.0, "pitch": 20, "overhang": 0.4,
                 "at": [[0, 0.8 + CH + 2.2, PZ + PD / 2 - 0.5, 0]], "_about": "the pediment over it"})

# ---- the giant columns
for sx, nm in ((-1, "west"), (1, "east")):
    X, Z = sx * 20.0, PZ + PD - 2.0
    add(f"{nm} column pedestal", {"type": "box", "width": 6.0, "length": 6.0, "height": 6.0, "at": [[X, 0, Z, 0]],
                                   **({"_about": "the two giant columns, each on its pedestal: a shaft wound with reliefs (a spiral band), a capital, a lantern with an eagle's cage of a cap"} if sx < 0 else {})})
    add(f"{nm} column", {"type": "column", "radius": 2.0, "height": 30.0, "sides": 16, "taper": 0.92, "at": [[X, 6.0, Z, 0]]})
    add(f"{nm} column band", {"type": "box", "width": 0.5, "length": 0.9, "height": 0.35,
                              "spiral": {"count": 160, "turns": 6, "radius": 2.0, "x": X, "z": Z, "y": 7.0, "dy": 0.17, "dr": -0.001},
                              "_about": "the relief band wound round the shaft"})
    add(f"{nm} column capital", {"type": "box", "width": 5.0, "length": 5.0, "height": 1.2, "at": [[X, 36.0, Z, 0]]})
    add(f"{nm} column lantern", comp("components/domed-tower", {"sides": 8, "R": 1.7, "H": 3.0, "t": 0.3, "drumR": 1.1, "drumH": 0.8, "cap": "bell",
                                                                "capR": 1.4, "waist": 0.75, "lift": 1.0, "kok": 0.2, "finial": 1.5, "doorH": 1.0},
                                     [[X, 37.2, Z, 0]], build=["tower", "cap", "finial"]))

# ---- the side wings: hallways from the church out to the gate pavilions
# Each is a building of its own, a storey of halls: its inner end is set into the church's wall (a door through the
# church's diagonal face opens into it), its outer end opens into the pavilion by an arch the pavilion's own size.
HZ0, HZ1, HH = 10.5, PZ + 2.6, 12.0          # the wings' depth (clear of the church's inside at their inner end) and height
HX0 = PW / 2 - 1.0                            # beside the portico
PV, PX = 9.0, 38.0                            # the pavilions
HX1 = PX - PV / 2
hz = (HZ0 + HZ1) / 2
wing_win = {"pattern": "4", "width": 2.0, "gap": 3.2, "sill": 1.2, "springing": 6.0, "head": {"profile": "semicircular"}}
passage = [{"at": 0, "width": 4.2, "sill": 0, "springing": 6.0, "head": {"profile": "semicircular"}}]
for sx, nm in ((-1, "west"), (1, "east")):
    # (faces: 0 the front (+z), 1 the +x end, 2 the back, 3 the -x end)
    outer, inner = ("1", "3") if sx > 0 else ("3", "1")
    add(f"{nm} hall", {"type": "enclosure", "plan": {"rect": [HX1 - HX0, HZ1 - HZ0]}, "thickness": 0.9, "height": HH,
                       "openings": wing_win, "faces": {outer: passage, inner: []},
                       "at": [[sx * (HX0 + HX1) / 2, 0, hz, 0]],
                       **({"_about": "the side wings: halls from the church to the gate pavilions, windows front and back, a door from the church at one end and an arch into the pavilion at the other"} if sx < 0 else {})})
    add(f"{nm} hall roof", {"type": "roof", "form": "hip", "width": HZ1 - HZ0, "length": HX1 - HX0, "pitch": 24, "overhang": 0.3,
                            "at": [[sx * (HX0 + HX1) / 2, HH, hz, Q]]})
    add(f"{nm} pavilion", {"type": "enclosure", "plan": {"rect": [PV, PV]}, "thickness": 1.4, "height": 20.0, "glass": False,
                           "tiers": [{"h": 9.0, "openings": passage}, {"openings": [{"at": 0, "width": 2.0, "sill": 3.0, "springing": 7.5, "head": {"profile": "semicircular"}}]}],
                           "at": [[sx * PX, 0, hz, 0]],
                           **({"_about": "a gate pavilion at each end of the front, an arch through it every way, its belfry over"} if sx < 0 else {})})
    add(f"{nm} pavilion floor", {"flatRoof": True, "type": "box", "width": PV - 2.8, "length": PV - 2.8, "height": 0.4, "at": [[sx * PX, 9.0 - 0.4, hz, 0]],
                                 **({"_about": "the belfry floor over the passage, and under the roof"} if sx < 0 else {})})
    add(f"{nm} pavilion ceiling", {"type": "box", "width": PV - 2.8, "length": PV - 2.8, "height": 0.4, "at": [[sx * PX, 20.0 - 0.4, hz, 0]]})
    add(f"{nm} pavilion roof", {"type": "dome", "sides": 4, "radius": PV / 2 * 1.4142, "thickness": 0, "head": {"profile": "bell", "waist": 0.7, "lift": 0.6},
                                "at": [[sx * PX, 20.0, hz, 0]]})

# ---- the statues (statuary.py): on the pediment, the figure crowning its apex and an angel at each of its lower corners;
# before the steps, on their pedestals, the two angels of the Old and the New Covenant -- limestone, looking out
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from statuary import statue, pedestal, FACE_PZ, capped
yP, zG, rise = 0.8 + CH + 2.2, PZ + PD + 0.4, (PW / 2) * math.tan(math.radians(20))   # the pediment's foot, its gable's face, its height
stat = {"statue pediment apex": statue((0, yP + rise - 0.3, zG - 0.6), kind="man", style="roman", stone="limestone", scale=1.7, seed=3, face=FACE_PZ),
        "statue pediment left": statue((-(PW / 2 - 0.8), yP, zG - 0.5), kind="woman", style="roman", stone="limestone", scale=1.4, seed=5, face=FACE_PZ),
        "statue pediment right": statue((PW / 2 - 0.8, yP, zG - 0.5), kind="woman", style="roman", stone="limestone", scale=1.4, seed=7, face=FACE_PZ)}
for sx, nm, sd in ((-1, "old covenant", 11), (1, "new covenant", 13)):
    x, z = sx * (PW / 2 - 1.4), PZ + PD + 2.6
    stat[f"pedestal {nm}"] = pedestal((x, 0, z), 1.6, 1.6, 2.2, f"the pedestal of the angel of the {nm}")
    stat[f"statue {nm}"] = statue((x, 2.2, z), kind="woman", style="roman", stone="limestone", scale=1.5, seed=sd, face=FACE_PZ, hold={"R": "items/tools/book"})
for k, v in capped(stat).items(): add(k, v)

doc = {"name": "Karlskirche",
       "_about": "THE KARLSKIRCHE, Vienna (1716-37), from components: the church round in plan (an `enclosure` of sixteen faces standing for its oval), a drum of eight windows and the tall dome with its lantern (`domed-tower`); before it a Corinthian PORTICO, six columns under a pediment, on its steps; either side of the portico a GIANT COLUMN after Trajan's, a relief band wound up its shaft, a lantern on its capital; and the front running out to a gate PAVILION at each end, arches through it, under a bell roof.",
       "params": {"detail": 4},
       "base": {"height": 0.6, "steps": 2, "stepOut": 0.5, "margin": 3}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/karlskirche.json"), "w").write(json.dumps(doc, indent=2) + "\n")
