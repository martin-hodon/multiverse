# TOPKAPI PALACE, Istanbul (from 1459; the Second Court's buildings mostly Süleyman's, 1520s, and Sinan's after the fire of
# 1574), its ceremonial core as a site, from the Ottoman palace components (tools/archgen/ottoman.py):
#   the MIDDLE GATE (Bâbüsselâm): a crenellated wall between two octagonal towers under pointed lead caps, a porch on
#     columns before the passage, the gate hall behind it and the guard rooms either side;
#   the SECOND COURT (Divan Meydanı) with porticoes round it: on the Middle Gate's side, on the west (the Carriage Gate to
#     the Harem in its back wall), before the kitchens all down the east, either side of the Gate of Felicity;
#   the IMPERIAL COUNCIL (Kubbealtı): three domed chambers behind a portico under a deep eave, and behind them the TOWER
#     OF JUSTICE (Adalet Kulesi) -- a square stone shaft, its windowed upper stage (Mahmud II), a tall pointed lead cap;
#   the OUTER TREASURY: two rows of four domes, stone and brick;
#   the KITCHENS: the range along the court with its three gates, the kitchen street, and Sinan's two rows of ten domed
#     kitchens, a broad chimney on every dome (twenty);
#   the GATE OF FELICITY (Bâbüssaâde): the range closing the court, the gate's canopy on marble columns under its eave,
#     a small dome over its middle bay;
#   the AUDIENCE CHAMBER (Arz Odası) behind it in the Third Court: the kiosk in its colonnade of 22 columns under one
#     deep-eaved roof.
# Not built: the First Court, the Third Court's other buildings, the Harem, the Fourth Court and the Baghdad Kiosk (it
# stands 250m away on the Fourth Court's terrace; the `ottoman-kiosk` with `dome` yes is its form).
#
# THE PLAN (sourced): the footprints are OpenStreetMap's ways (2026), turned into the court's own frame -- the court's
# long axis from the Middle Gate to the Gate of Felicity is -z, the kitchens' side +x, the Divan's side -x. From them:
# the court 84 x 144m; the Middle Gate block 44.6 x 27m, its towers 18.2m apart, the passage off the court's axis (x
# -20.8); the Divan 26.5 x 11.7m with a 5m portico, the Tower of Justice 8.7 x 8.4m behind its west end; the Outer
# Treasury 32.3 x 17.6m; the kitchens' court range 11.5m deep, the street 5.2m, the domed kitchens 106 x 21m; the Gate
# of Felicity's canopy 16.4m wide and 6.8m deep, the range 14.3m deep; the Audience Chamber 31.6 x 29m with its eaves.
# Sourced from the texts (Wikipedia en/tr): two octagonal towers with pointed caps on the Middle Gate, its
# crenellations; three domed chambers in the Divan; the Tower of Justice square, the palace's tallest, its upper stage
# with round-arched windows, a lead cap; the treasury of eight domes; ten domed kitchens with two rows of twenty
# chimneys (taken here as one chimney per dome: twenty in two rows of ten); the Audience Chamber's 22 columns.
# ESTIMATED (no source gives them): every height -- the Tower of Justice 41m to its tip (shaft 24, stage 7, cap 9.5),
# the Middle Gate towers 24m (shaft 14, cap 9.5) and 6.4m across, its wall 10.5m; the porticoes' columns 4.5m; the
# kitchens' springing 6m; the treasury taken as 2 x 4 square bays; the kiosk's room 21 x 18m.
#   Front is +z: the Middle Gate. Everything is metres. Run: python3 tools/archgen/topkapi.py
import os, json, math
from ottoman import write_components, comp, POINTED, ROOT

Q = math.pi / 2
OUT = lambda rel, doc: open(os.path.join(ROOT, rel), "w").write(json.dumps(doc, indent=2) + "\n")
r2 = lambda v: round(v, 3)

parts, build = {}, []
def add(n, d): parts[n] = d; build.append(n)

# ---- the Middle Gate ---------------------------------------------------------------------------------------------
GX, WZ, WT, WH = -20.8, 95.5, 3.0, 10.5                    # the passage's axis; the gate wall's line, thickness, height
W0, W1 = -62.0, 60.0                                        # the gate wall's ends
add("gate wall", {"type": "wall", "width": W1 - W0, "height": WH, "thickness": WT, "glass": False, "at": [[r2((W0 + W1) / 2), 0, WZ, 0]],
                  "openings": [{"at": r2(GX - W0), "width": 4.4, "sill": 0, "springing": 4.6, "head": POINTED}],
                  "_about": "the Middle Gate's crenellated wall, the passage through it off the court's axis"})
add("gate towers", comp("conical-tower", {"sides": 8, "w": 6.4, "H": 14.0, "beltY": WH, "corH": 0.7, "corOut": 0.3, "capH": 12.0, "capR": 3.95},
                        [[GX - 9.1, 0, 98.0, 0], [GX + 9.1, 0, 98.0, 0]],
                        _about="the two octagonal towers either side of the passage, under their pointed lead caps"))
add("gate crenellation", comp("crenellation", {"L": W1 - W0, "t": 0.7, "h": 0.5, "step": 1.6, "mh": 0.9, "merlon": "square"},
                              [[r2((W0 + W1) / 2), WH, r2(WZ + WT / 2 - 0.35), 0]], standsOn=["gate wall"],
                              _about="its battlements, along the outer face"))
add("gate porch", comp("ottoman-portico", {"n": 3, "B": 3.6, "colH": 4.6, "colR": 0.26, "D": 3.0, "eave": 1.6, "back": 0, "arches": "no", "archH": 0.6},
                       [[GX, 0, WZ + WT / 2 + 3.0, 0]], _about="the porch before the passage, its eave widened in the 19th century"))
HZ0, HZ1 = 73.6, WZ - WT / 2                                # the gate hall and the guard rooms, from the court wall to the gate wall
pas = [{"at": 0, "width": 4.4, "sill": 0, "springing": 4.6, "head": POINTED}]
add("gate hall", {"type": "enclosure", "plan": {"rect": [12, r2(HZ1 - HZ0)]}, "thickness": 1.4, "height": 9.0, "glass": False, "interior": True,
                  "openings": [], "faces": {"0": pas, "2": pas}, "at": [[GX, 0, r2((HZ0 + HZ1) / 2), 0]],
                  "_about": "the hall the passage runs through, from the gate wall to the court"})
add("gate hall roof", {"type": "roof", "form": "hip", "width": 13, "length": r2(HZ1 - HZ0 + 0.6), "pitch": 22, "overhang": 0.4,
                       "at": [[GX, 9.0, r2((HZ0 + HZ1) / 2 - 0.3), 0]], "standsOn": ["gate hall"]})
wings = [(-40.0, GX - 6), (GX + 6, 4.6)]
add("guard rooms", {"type": "enclosure", "plan": {"rect": [13.2, r2(HZ1 - HZ0)]}, "thickness": 1.2, "height": 7.0, "glass": True, "openings": [],
                    "faces": {"2": {"every": 3.2, "width": 1.0, "end": 1.5, "sill": 1.6, "springing": 2.8, "head": POINTED}},
                    "at": [[r2((a + b) / 2), 0, r2((HZ0 + HZ1) / 2), 0] for a, b in [wings[0]]],
                    "_about": "the guard rooms west of the gate hall"})
add("guard rooms east", {"type": "enclosure", "plan": {"rect": [r2(wings[1][1] - wings[1][0]), r2(HZ1 - HZ0)]}, "thickness": 1.2, "height": 7.0, "glass": True,
                         "openings": [], "faces": {"2": {"every": 3.2, "width": 1.0, "end": 1.5, "sill": 1.6, "springing": 2.8, "head": POINTED}},
                         "at": [[r2(sum(wings[1]) / 2), 0, r2((HZ0 + HZ1) / 2), 0]], "_about": "the guard rooms east of it"})
for nm, (a, b) in (("guard roof", wings[0]), ("guard roof east", wings[1])):
    add(nm, {"type": "roof", "form": "hip", "width": r2(b - a + 0.6), "length": r2(HZ1 - HZ0 + 0.6), "pitch": 22, "overhang": 0.3,
             "at": [[r2((a + b) / 2), 7.0, r2((HZ0 + HZ1) / 2 - 0.3), 0]], "standsOn": ["guard rooms" + (" east" if "east" in nm else "")]})

# ---- the court's walls and porticoes -----------------------------------------------------------------------------
NW0, NW1 = -46.6, 42.0                                      # the court's north wall, the Divan side's back to the kitchens'
add("court wall", {"type": "wall", "width": NW1 - NW0, "height": 10.0, "thickness": 1.6, "glass": False, "at": [[r2((NW0 + NW1) / 2), 0, 72.8, 0]],
                   "openings": [{"at": r2(GX - NW0), "width": 4.4, "sill": 0, "springing": 4.6, "head": POINTED}],
                   "_about": "the court's wall on the Middle Gate's side, the passage coming through it"})
# THE PORTICOES, SET OUT FROM THE COURT'S CORNERS: the column lines (the court's edge in OSM) meet at four corner columns, each
# owned by one portico (the other leaves its end column out: endL/endR 0); a corner's square behind them is roofed by
# carrying one portico's roof on past it (eaveL/eaveR). Every court portico has the same columns, arcade and eave, so
# their roofs meet level. The north row's bays put the passage in the middle of its fifth bay.
CW, CE, CN, CS = -41.6, 37.0, 67.0, -66.7                   # the column lines: west, east (kitchens), north (gate), south (Felicity)
DIVZ = (-18.6, -46.6)                                       # the Divan portico's run, on the west line
PC = {"colH": 4.6, "archH": 3.9, "D": 4.9, "eave": 2.4}     # every court portico's columns, arcade, depth and eave
def row(a, b, n, about, **kw):
    """an ottoman-portico of n bays between the column axes a and b along its line (its bay worked out from them)"""
    return comp("ottoman-portico", {**PC, "n": n, "B": r2(abs(b - a) / n), **kw}, None, _about=about)
def place(d, x, z, yaw):
    d["at"] = [[r2(x), 0, r2(z), yaw]]
    return d
CORNER = PC["D"] + 0.1                                      # how far a roof runs on over a corner's square
add("gate portico", place(row(CE, CW, 17, "the portico along the Middle Gate side, owning both its corner columns, its roof "
                              "carried over both corners; the passage in its fifth bay", back=0, eaveL=CORNER, eaveR=CORNER), (CW + CE) / 2, CN, math.pi))
add("west portico", place(row(CN, DIVZ[0], 19, "the west portico from the north-west corner to the Divan's, the Carriage Gate to the "
                              "Harem in its back wall", back=1, door="yes", bt=1.2, gW=3.4, gS=4.0, endL=0, eaveL=0, eaveR=0),
                          CW, (CN + DIVZ[0]) / 2, Q))
add("kitchen portico", place(row(CS, CN, 30, "the portico all down the kitchens' side, owning the south-east corner and roofing it",
                                 back=0, endR=0, eaveR=0, eaveL=CORNER), CE, (CS + CN) / 2, -Q))
add("felicity portico", place(row(CW, 1.0, 10, "the portico west of the Gate of Felicity, from the treasury's front", back=0, endL=0, eaveL=0),
                              (CW + 1.0) / 2, CS, 0))
add("felicity portico east", place(row(19.0, CE, 4, "the portico east of it, to the kitchens' corner", back=0, endR=0, eaveR=0),
                                   (19.0 + CE) / 2, CS, 0))

# ---- the Imperial Council and the Tower of Justice ----------------------------------------------------------------
# The domed rows are blue_mosque.py's `domed-arcade`, closed: its front (local z 0..p) to the court, its bays behind
DZ = -32.6
add("divan", comp("domed-arcade", {"n": 3, "B": 9.0, "p": 1.3, "SP": 6.0, "cn": 16, "front": "door", "gW": 2.2, "gS": 3.0, "wSill": 1.6, "wSpr": 3.6},
                  [[-46.5 - 1.3, 0, DZ, Q]], _about="the Kubbealtı: the council chamber, the chancery and the Defterhane, three domed rooms"))
add("divan portico", place(row(DIVZ[0], DIVZ[1], 5, "the Divan's portico under its deep painted eave", back=0, endL=0, eaveL=0),
                           CW, sum(DIVZ) / 2, Q))
add("tower of justice", comp("conical-tower", {"plan": "square", "w": 8.5, "H": 21.0, "beltY": 11.0, "corH": 0.8, "corOut": 0.35,
                                               "upper": "yes", "Hu": 7.5, "wu": 7.6, "ucH": 0.7, "upperCols": "yes", "upperPed": "yes", "pedH": 1.5,
                                               "capR": 3.9, "capH": 15.5},
                              [[-62.4, 0, -24.1, Q]], _about="the Tower of Justice: the palace's tallest -- the stone shaft, Mahmud II's white "
                                                             "marble stage (a tall arched window between paired columns in every face, segmental "
                                                             "pediments) and the slender lead cone"))

# ---- the Outer Treasury -------------------------------------------------------------------------------------------
# two rows of four domes back to back: the court row's back wall a spine of arches into the rear row
TZ, TB, TP = -63.4, 8.0, 1.3
tre = {"n": 4, "B": TB, "p": TP, "SP": 6.5, "cn": 12, "wSill": 2.4, "wSpr": 4.4}
add("treasury", comp("domed-arcade", {**tre, "front": "door", "dOff": 4.0, "back": 1, "backWin": "arches"},
                     [[-41.4 - TP, 0, TZ, Q]], _about="the Outer Treasury's court-side row of four domes, stone and brick"))
add("treasury rear", comp("domed-arcade", {**tre, "front": "wall", "back": 0, "backWin": "arches"},
                          [[-41.4 - TP - TB - TP - TB, 0, TZ, -Q]], _about="its back row, opening into the first through the spine's arches"))

# ---- the kitchens -------------------------------------------------------------------------------------------------
KX0, KX1, KZ0, KZ1 = 42.0, 53.5, 72.8, -69.0
gate3 = [{"at": a, "width": 3.0, "sill": 0, "springing": 3.6, "head": POINTED, "glass": False} for a in (-40, 0, 40)]
rowK = {"every": 6.0, "width": 1.2, "end": 2.0, "sill": 2.0, "springing": 3.6, "head": POINTED, "with": gate3}
add("kitchen range", {"type": "enclosure", "plan": {"rect": [KX1 - KX0, KZ0 - KZ1]}, "thickness": 1.3, "height": 10.0, "glass": True, "interior": True,
                      "openings": [], "faces": {"1": rowK, "3": rowK}, "at": [[r2((KX0 + KX1) / 2), 0, r2((KZ0 + KZ1) / 2), 0]],
                      "_about": "the range between the court and the kitchen street, its three gates from the portico"})
add("kitchen range roof", {"type": "roof", "form": "hip", "width": KX1 - KX0 + 0.8, "length": KZ0 - KZ1 + 0.8, "pitch": 20, "overhang": 0.4,
                           "at": [[r2((KX0 + KX1) / 2), 10.0, r2((KZ0 + KZ1) / 2), 0]], "standsOn": ["kitchen range"]})
# Sinan's kitchens: two rows of ten domed bays back to back, a chimney on every dome; the street row's front a door into
# every kitchen, its back wall the spine of arches into the seaward row
KB, KP, KS = 10.5, 1.3, 58.7                                # the bays, the walls, the street side's face
kit = {"n": 10, "B": KB, "p": KP, "SP": 6.0, "cn": 16, "dh": 0.4, "chimney": "yes", "chH": "s * 0.8", "chCap": "cone", "wSill": 3.0, "wSpr": 4.6}
add("kitchens", comp("domed-arcade", {**kit, "front": "doors", "gW": 2.4, "gS": 3.4, "back": 1, "backWin": "arches"}, [[KS + KP, 0, -16.0, -Q]],
                     _about="Sinan's kitchens, the street side: ten domed bays, a door into each, a chimney on every dome"))
add("kitchens rear", comp("domed-arcade", {**kit, "front": "wall", "back": 0, "backWin": "arches"}, [[KS + KP + KB + KP + KB, 0, -16.0, Q]],
                          _about="the seaward row: ten more domes and chimneys"))

# ---- the Gate of Felicity and the Audience Chamber ----------------------------------------------------------------
FX, FZ0, FZ1 = 10.0, -71.7, -86.0
FC = (-41.0 + 55.0) / 2
fg = lambda a: [{"at": a, "width": 3.8, "sill": 0, "springing": 4.4, "head": POINTED, "glass": False}]
add("felicity range", {"type": "enclosure", "plan": {"rect": [96.0, r2(FZ0 - FZ1)]}, "thickness": 1.3, "height": 11.0, "glass": True, "interior": True,
                       "openings": [], "faces": {"0": {"every": 4.4, "width": 1.1, "end": 2.0, "sill": 1.8, "springing": 3.4, "head": POINTED, "with": fg(FX - FC)},
                                                 "2": {"every": 4.4, "width": 1.1, "end": 2.0, "sill": 1.8, "springing": 3.4, "head": POINTED, "with": fg(FC - FX)}},
                       "at": [[FC, 0, r2((FZ0 + FZ1) / 2), 0]], "_about": "the range closing the court, the Gate of Felicity through it"})
add("felicity range roof", {"type": "roof", "form": "hip", "width": 96.8, "length": r2(FZ0 - FZ1 + 0.8), "pitch": 20, "overhang": 0.4,
                            "at": [[FC, 11.0, r2((FZ0 + FZ1) / 2), 0]], "standsOn": ["felicity range"]})
add("felicity gate", comp("ottoman-portico", {"n": 3, "B": 5.4, "colH": 8.0, "colR": 0.32, "D": 6.8, "eave": 3.2, "back": 0, "dome": "yes",
                                              "domeR": 3.2, "arches": "no", "archH": 0.8, "pitch": 10, "roofForm": "hip"},
                          [[FX, 0, FZ0 + 6.8, 0]], _about="the Gate of Felicity's canopy: marble columns, the deep eave, the dome over the passage"))
add("audience chamber", comp("ottoman-kiosk", {"W": 21.0, "L": 18.0, "H": 6.0, "G": 3.5, "nf": 7, "ns": 6, "eave": 2.4},
                             [[FX, 0, -102.5, 0]], _about="the Arz Odası: the throne room in its colonnade of 22 columns under the deep roof"))

doc = {"name": "Topkapı Palace",
       "_about": "TOPKAPI PALACE's ceremonial core, Istanbul (15th-16th c.): the Middle Gate between its two capped towers, the Second Court "
                 "with its porticoes, the Imperial Council's three domes under the Tower of Justice, the Outer Treasury, Sinan's kitchens with "
                 "twenty chimneys, the Gate of Felicity's canopy and the Audience Chamber in its colonnade -- from the components "
                 "conical-tower, ottoman-portico, ottoman-kiosk and domed-arcade. Generated by tools/archgen/topkapi.py. The Middle Gate is +z.",
       "params": {"detail": 4}, "build": build, "parts": parts}

if __name__ == "__main__":
    write_components()
    OUT("assets/architecture/topkapi.json", doc)
    print(len(build), "parts")
