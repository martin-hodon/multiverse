# THE UNITED STATES CAPITOL, Washington (Thornton, Latrobe, Bulfinch 1793-1829; Walter's extensions and the iron dome
# 1851-68; the east front moved out 1958-62), from the NEOCLASSICAL library (neoclassical.py): the CENTRAL BLOCK with the
# rotunda through it, its east front a temple front -- eight columns under the pediment between colonnades of four -- on
# a podium arcade, the grand stair up to the Columbus doors; the west projection; the two CONNECTORS; the SENATE (north)
# and HOUSE (south) extensions, each with its own pedimented east front and stair, colonnades on their west fronts and
# their far ends; every wing a rusticated ground storey under a giant Corinthian order, balustrades on every head.
# Over the roofs the skirt, and on it the DOME (`drum-dome`): the drum behind its peristyle of 36 columns, the attic, the
# plinth the narrower iron dome stands back on, its 36 ribs and three tiers of windows, the THOLOS (12 columns), the
# Statue of Freedom on the globe on its crown 88 m over the east plaza. On the hill: the east plaza, the lawns, Olmsted's
# west terrace and its three stairs down to the Mall's lawn.
#
#   +z is EAST (the main front, the plaza), +x NORTH (the Senate). The building stands on the hill's top at Y0.
#   SOURCED (Wikipedia, Architect of the Capitol, $X/ref/cap_*): the dome 288 ft = 87.8 m to the statue's crest, the
#   rotunda 96 ft = 29.3 m across; 36 peristyle columns, 12 in the tholos; the Statue of Freedom 19.5 ft = 5.94 m (on a
#   cast-iron globe about a third of that across, its motto band round it -- read off photographs, 2 m); the
#   building 751 ft = 229 m long; the east front's 8 + 2 x 4 columns, extended 32.5 ft in 1958.
#   ESTIMATED (from the east-front photograph scaled by the 229 m and the 88 m): the wings' depths, the storeys (6.5,
#   7.5, 5.5; the balustrade's top 21 m), the porticoes 3 m (2 m on the wings) before their colonnades, the peristyle
#   40 m across, its base 30.5 m up, the attic 9.5 m, the dome's own radius 13.4 m and its pointed crown 17 m up, the
#   tholos 3.8 m to its columns, the hill 6 m, the terrace 36 m deep. DERIVED: the tholos's height, solved so that
#   Freedom's crest is 87.8 m up.
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from neoclassical import Balusters, block, temple_front, grand_stair, dome_on_drum, check_tholos, R3, ROOT
from statuary import statue, FACE_PZ, capped

parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)

Y0 = 6.0                                  # the hill's top: the plaza and the building's ground floor
ST = (6.5, 7.5, 5.5)                      # ground (rusticated), principal, upper storeys
COLH, ENTH, COLR = 10.4, 2.6, 0.52        # the giant order through the upper two (10.4 + 2.6 = 7.5 + 5.5)
Y1 = Y0 + ST[0]                           # the principal floor: the porticoes stand on it
bal = Balusters(every=0.9)

# ---- the hill: its top the plaza and the building's ground; grass slopes round it; Olmsted's west terrace a walled
# platform at the same height, its wall in panels between piers, three stairs down to the lawn west -- the broad one
# in the middle, a pair either side -- each in two flights by a landing halfway
add("hill", {"type": "prism", "plan": {"rect": [290, 165]}, "height": Y0, "batter": {"out": 24}, "walked": True, "at": [[0, 0, 40.5, 0]],
             "_about": "Capitol Hill's top: the plaza east, the lawns round, grass slopes down on every side"})
TW, TZ0, TZ1 = 240.0, -76.0, -40.0
add("west terrace", {"type": "prism", "plan": {"rect": [TW, TZ1 - TZ0]}, "height": Y0, "walked": True, "at": [[0, 0, (TZ0 + TZ1) / 2, 0]],
                     "_about": "Olmsted's west terrace (1884-92): a platform walled round the west front, at the floor's level"})
STAIRS = [(0, 14.0, 24.0, 30.0, ""), (-52, 8.0, 11.0, 15.0, " south"), (52, 8.0, 11.0, 15.0, " north")]   # x, upper, lower, landing width
heads = sorted((sx - up / 2 - 1.2, sx + up / 2 + 1.2) for sx, up, _, _, _ in STAIRS)
x0 = -TW / 2 + 0.3
for a, b in heads + [(TW / 2 - 0.3, None)]:                    # (the parapet along the rim, broken at each stair's head)
    bal.run((x0, TZ0 + 0.3), (a, TZ0 + 0.3), Y0); x0 = b
for sx in (-1, 1): bal.run((sx * (TW / 2 - 0.3), TZ1 + 2), (sx * (TW / 2 - 0.3), TZ0 + 0.3), Y0)
for sx, up, lo, lw, nm in STAIRS:
    add(f"terrace landing{nm}", {"type": "prism", "plan": {"rect": [lw, 10]}, "height": 3.0, "walked": True, "at": [[sx, 0, TZ0 - 5, 0]]})
    grand_stair(add, f"terrace stair{nm}", sx, TZ0, "-z", 3.0, Y0, up, cheek=1.2)
    grand_stair(add, f"lawn stair{nm}", sx, TZ0 - 10, "-z", 0.0, 3.0, lo, cheek=1.2)
piers = [x for x in [-TW / 2 + 6 + 12 * i for i in range(20)] if all(not (a - 1.5 < x < b + 1.5) for a, b in heads)]
add("terrace piers", {"type": "box", "width": 1.4, "length": 0.6, "height": Y0, "at": [[R3(x), 0, R3(TZ0 - 0.3), 0] for x in piers],
                      "_about": "the terrace wall's piers, every 12 m: panels between them"})

# ---- the wings: one block each, against each other where they meet
CW, CD, CZ = 84.0, 46.0, 1.0              # the central block (Bulfinch's, the east front moved out 1958)
KX0, KX1, KZ0, KZ1 = 42.0, 61.0, -16.0, 20.0   # the connectors
EX0, EX1, EZ0, EZ1 = 61.0, 114.5, -42.5, 29.5  # the extensions: 2 x 114.5 = 229 m
WPW, WZ0 = 50.0, -46.0                    # the west projection
kw = dict(y=Y0, storeys=ST, bay=4.9, bal=bal)
central = block(add, "central block", CW, CD, 0, CZ, well=14.6, about="the central block, the rotunda in its middle",
                doors=[("+z", 0, 1, 3.0, 5.6, True), ("-z", 0, 1, 2.4, 4.4, True)],
                against={"+x": [(KZ0 - CZ, KZ1 - CZ)], "-x": [(KZ0 - CZ, KZ1 - CZ)], "-z": [(-WPW / 2, WPW / 2)]}, **kw)
block(add, "west projection", WPW, CZ - CD / 2 - WZ0, 0, (WZ0 + CZ - CD / 2) / 2, about="the west front's centre (Latrobe's and Bulfinch's)",
      doors=[("-z", 0, 0, 2.6, 4.2, True)], against={"+z": [(-WPW / 2, WPW / 2)]}, **kw)
for sx, nm in ((1, "senate"), (-1, "house")):
    kx, ex = sx * (KX0 + KX1) / 2, sx * (EX0 + EX1) / 2
    near, far = ("-x", "+x") if sx > 0 else ("+x", "-x")
    block(add, f"{nm} connector", KX1 - KX0, KZ1 - KZ0, kx, (KZ0 + KZ1) / 2, about="the connector to the extension",
          against={near: [(-(KZ1 - KZ0) / 2, (KZ1 - KZ0) / 2)], far: [(-(KZ1 - KZ0) / 2, (KZ1 - KZ0) / 2)]}, **kw)
    ezc = (EZ0 + EZ1) / 2
    block(add, f"{nm} extension", EX1 - EX0, EZ1 - EZ0, ex, ezc, about=f"the {nm.title()} extension (Walter, 1851-59)",
          doors=[("+z", 0, 1, 2.8, 5.2, True), (far, 0, 0, 2.4, 4.0, True)],
          against={near: [(KZ0 - ezc, KZ1 - ezc)]}, **kw)

# ---- the fronts: the east fronts' temple fronts on their podiums with the grand stairs, the colonnades elsewhere
tf = dict(y0=Y0, y1=Y1, colR=COLR, colH=COLH, entH=ENTH, bal=bal)
temple_front(add, "east front", 0, CZ + CD / 2, "+z", ped=8, flank=4, spacing=3.2, depth=7.0, stair=15.0, pedOut=3.0, **tf)
temple_front(add, "west front", 0, WZ0, "-z", ped=0, flank=10, spacing=3.2, depth=4.0, **tf)
for sx, nm in ((1, "senate"), (-1, "house")):
    ex, ezc = sx * (EX0 + EX1) / 2, (EZ0 + EZ1) / 2
    temple_front(add, f"{nm} east front", ex, EZ1, "+z", ped=8, flank=4, spacing=3.0, depth=6.0, stair=12.0, pedOut=2.0, **tf)
    temple_front(add, f"{nm} west front", ex, EZ0, "-z", ped=0, flank=10, spacing=3.0, depth=4.0, **tf)
    temple_front(add, f"{nm} end front", sx * EX1, ezc, "+x" if sx > 0 else "-x", ped=0, flank=10, spacing=3.0, depth=4.0, **tf)
    temple_front(add, f"{nm} connector front", sx * (KX0 + KX1) / 2, KZ1, "+z", ped=0, flank=6, spacing=2.9, depth=3.6, **tf)

# ---- the rotunda: its wall from the principal floor up through the roof, where the skirt and the drum go on with it
RR, DT = 14.6, 1.8
add("rotunda", {"type": "ring", "count": 16, "rOuter": RR + DT, "rInner": RR, "height": R3(ST[1] + ST[2] + 0.4), "y": R3(Y1), "turn": 0.5,
                "every": 4, "only": 4, "opening": {"width": 3.0, "sill": 0, "springing": 4.6, "head": {"profile": "semicircular"}},
                "place": [[0, 0, 0, 0]], "_about": "the rotunda's wall, 96 ft across, four doors into it"})
add("rotunda interior", {"type": "interior", "of": ["rotunda"], "plan": {"sides": 36, "radius": RR + DT / 2}, "height": R3(ST[1] + ST[2] + 0.4),
                         "at": [[0, R3(Y1), 0, 0]], "_about": "the rotunda's space up to the drum"})

# ---- the dome. The tholos's height is the one number left free: it is what sets Freedom's crest 87.8 m over the plaza
ROOF = central["top"]
DR, SPREAD = 13.4, 0.3                    # the iron dome: taller than a half sphere (pointed, its crown 13.4 x 1.26 = 17 m up)
FREEDOM = 5.94                            # the statue, 19.5 ft
check_tholos()
dd = dict(dt=DT, skirt=(21.0, R3(Y0 + 30.5 - ROOF)), H=11.4, colH=9.0, n=36, colR=0.45, pw=3.4, win=(1.9, 0.8, 6.8), atticH=9.5,
          atticWin=(1.4, 2.8, 3.8), atticHead="flat", domeR=DR, plinth=1.5, spread=SPREAD, ribW=0.45, lanternR=3.8, tholosN=12, globe=True, globeR=1.0,
          windows=((0.38, 0.8, 1.3), (0.6, 0.9, 1.6), (0.8, 0.6, 0.8)))   # (the dome's three tiers of lights between its ribs)
lo, hi = 6.0, 16.0
for _ in range(40):
    LH = (lo + hi) / 2
    (lo, hi) = (LH, hi) if dome_on_drum(lambda n, d: None, "dome", 0, 0, ROOF, RR, lanternH=LH, **dd)["top"] < Y0 + 87.8 - FREEDOM else (lo, LH)
D = dome_on_drum(add, "dome", 0, 0, ROOF, RR, lanternH=R3(LH), bal=bal, **dd)
# the Statue of Freedom (Crawford, 1863): bronze, on the globe on the tholos's crown, looking east -- her crest 88 m over the plaza
# (the engine seats the tholos's crown on the cap's faceted curve, ~0.08 under the true arc dome_on_drum reckons with: so
#  her foot goes 0.1 under the reckoned top, into the globe, not over it -- measured on the assembled mesh: globe top 87.78)
FOOT = D["top"] - 0.1
scale = (Y0 + 87.8 - FOOT) / 1.78
stat = {"statue of freedom": statue((0, R3(FOOT), 0), kind="woman", style="roman", stone="bronze", scale=R3(scale), seed=17, face=FACE_PZ,
                                    hold={"R": "items/weapons/sword"})}
for k, v in capped(stat).items(): add(k, v)
for k, v in bal.parts().items(): add(k, v)

doc = {"name": "United States Capitol",
       "_about": "THE UNITED STATES CAPITOL, Washington (1793-1868): the central block with its east front -- a pedimented portico of eight Corinthian columns between colonnades of four on an arcaded podium, the grand stair -- and the rotunda; the connectors and the Senate and House extensions with their own temple fronts; the rusticated ground storey and the giant order round every wing, balustrades on every head; over it the cast-iron dome: the skirt, the drum behind its peristyle of 36 columns, the attic, the ribbed dome and its windows, the tholos and the Statue of Freedom on her globe, 88 m over the east plaza; on the hill, Olmsted's west terrace and its three stairs. Built by tools/archgen/us_capitol.py from neoclassical.py.",
       "params": {"detail": 4}, "base": False, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/us-capitol.json"), "w").write(json.dumps(doc, indent=2) + "\n")
print("statue at", R3(FOOT), "scale", R3(scale), "| deck", R3(D["deck"]), "spring", R3(D["spring"]), "crown", R3(D["crown"]),
      "tholos", R3(D["tholos"]), "lanternH", R3(LH), "| parts", len(parts))
