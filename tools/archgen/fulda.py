# FULDA CATHEDRAL (Dom St. Salvator), Johann Dientzenhofer, 1704-12: a cruciform three-aisled pillar basilica turned
# to the WEST like St Peter's, its front the east one on the Domplatz. From components (baroque.py): the
# `twin-tower-front` -- the two towers close together (65 m) flanking the centre in a Doric storey and a Corinthian one,
# the portal between engaged columns, the great window, the pediment, and over the towers the clock stage, the belfry and
# each tower's `baroque-helm` (a Schweifkuppel, an open lantern, a second Schweifkuppel with a smaller lantern, the
# spike, the pineapple and the cross) -- the two domed chapels (Andreas- and Johanneskapelle) either side of the towers,
# low blocks under slate domes on short drums, the two sandstone obelisks beside them; behind, the nave and aisles (the
# clerestory on its arcade over the aisles' lean-to roofs), the short transept and over the crossing the DOME on a drum
# (pendentives, `drum-dome`), the choir in its aisles, the cross range of the Lady Chapel and sacristy (meeting the old
# monastery), and the high choir over the crypt to the west.
#   SOURCED (Wikipedia de/en "Fuldaer Dom"): 99 m long; dome 39 m high; towers 65 m, four storeys parted by cornices,
#   their helms (Schweifkuppel, open lantern, Schweifkuppel, smaller lantern, spike, pineapple, cross); portal with four
#   three-quarter columns, entablature with triglyphs (Doric); upper storey of columns, round-headed great window,
#   pediment with an oculus and the Salvator on it; the two domed chapels; obelisks about 11 m; sandstone throughout.
#   The PLAN is OpenStreetMap's (way 90756726, the outline turned so the axis is z): the front block 51.7 m wide and
#   about 15 m deep, nave and aisles 34.5 m wide, the transept arms reaching 22 m out, the cross range 77 m long, the
#   high choir 16.5 m wide, 93.5 m in all. ESTIMATED (read off the Wikipedia photographs at the towers' scale): the
#   storey heights of the front (13 m, 15.4 m, 9.4 m, 6 m), the centre 13 m and towers 8.2 m wide, the helms' sizes; the
#   nave's heights (aisles 14 m, clerestory 25 m), the bays, the drum and dome over the crossing, the cross range's 15 m.
#   The front (east) is +z; north +x.
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import baroque, roman_baroque
from statuary import statue, pedestal, FACE_PZ, capped
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q = math.pi / 2
r2 = lambda v: round(v, 3)
semi = {"profile": "semicircular"}
baroque.helm(); baroque.twin_tower_front()           # (the components this building is made of: written fresh)
import clocks; clocks.dial()

# ---- the plan (OSM, metres; z = the axis toward the front)
FZ, D = 46.3, 14.9                         # the front line; the front block's depth
BZ = FZ - D                                # its back: 31.4, where the nave begins
CW, TW = 13.0, 8.2                         # the centre between the towers; the towers
X1 = CW / 2 + TW                           # the towers' outer faces: 14.7
H1, H2, H3, H4 = 13.0, 15.4, 9.4, 6.0      # the front's storeys: Doric, Corinthian; the clock stage, the belfry
HF = H1 + H2
AW, NW = 34.5, 16.0                        # the aisles' outside width, the nave's (the clerestory's)
AH, NH = 14.0, 25.0                        # the aisles' walls, the clerestory's head
Z5, ZT = 5.0, -11.7                        # the transept's east and west faces
ZR, ZW, ZE = -26.0, -37.0, -46.7           # the cross range's east and west faces; the high choir's end
TA = 22.0                                  # the transept arms reach this far out
T = 1.2                                    # the walls
TV = 1.5                                   # ...the vaulted transept's and high choir's (a tenth of the vault's span, and more)

# ---- the front: towers, centre, pediment, helms (components/twin-tower-front)
add("front", comp("components/twin-tower-front",
                  {"cW": CW, "tW": TW, "D": D, "tD": D, "pedD": D - 1.0, "t": 1.4, "H1": H1, "H2": H2, "H3": H3, "H4": H4, "s": 0.45, "co": 1.0, "colA": 4.2, "colB": 7.8,
                   "chamf": 0.9, "pitch": 34, "order1": "doric", "order2": "corinthian", "doorW": 3.6, "doorH": 7.2, "winW": 3.4, "winSill": 3.0,
                   "winH": 8.2, "tWin": 1.2, "backW": 9.0, "backH": 11.0, "pcR": 0.62,
                   "hR": 3.8, "hLR": 1.75, "hLH": 3.9, "hR2": 2.05, "hL2R": 0.8, "hL2H": 1.9, "hSpikeH": 2.6, "hBallR": 0.55, "hCrossH": 2.4,
                   "clock": "yes", "clockR": 1.15, "clockY": 1.9, "clockWinW": 2.6, "belfryWinW": 2.5,
                   "hWaist": 0.8, "hLift": 0.6, "hWaist2": 0.8, "hLift2": 0.62},
                  [[0, 0, FZ, 0]],
                  _about="the east front: the towers 8.2 m square close round the 13 m centre, a Doric ground storey and a Corinthian upper one, the portal between engaged columns, the great window, the pediment; the clock stage, the belfry and the helms, 65 m"))

# ---- the two domed chapels either side of the towers (St Andrew's north, St John's south), the front's ground storey
CH_W, CH_Z0, CH_Z1 = 11.15, BZ, 44.3
cx = X1 + CH_W / 2
cz = (CH_Z0 + CH_Z1) / 2
ch_front = [{"h": 6.0, "openings": [{"at": 0, "width": 1.9, "sill": 0, "springing": 3.6, "head": semi, "surround": {"head": "cornice"}}]},
            {"openings": [{"at": 0, "width": 2.2, "sill": 0.8, "springing": 4.6, "head": semi, "surround": True}]}]
ch_side = [{"h": 6.0, "openings": [{"at": 0, "width": 2.2, "sill": 2.0, "springing": 4.6, "head": semi, "surround": True}]},
           {"openings": [{"at": 0, "width": 1.6, "sill": 2.2, "springing": 2.2, "head": semi, "foot": semi}]}]
for sx, nm in ((1, "north"), (-1, "south")):
    outer, inner = ("1", "3") if sx > 0 else ("3", "1")
    add(f"{nm} chapel", {"type": "enclosure", "plan": {"rect": [CH_W, r2(CH_Z1 - CH_Z0)]}, "thickness": T, "height": H1, "interior": True,
                         "faces": {"0": ch_front, outer: ch_side, inner: [], "2": []}, "orders": [{"tier": 0, "span": 2, "kind": "doric"}],
                         "courses": {"skip": [int(inner)]}, "at": [[r2(sx * cx), 0, r2(cz), 0]],
                         **({"_about": "the domed chapels either side of the towers (St Andrew's, St John's), as tall as the front's Doric storey and dressed in its order: a door and a window on the square, a window and an oculus at the side"} if sx > 0 else {})})
add("chapel decks", {"type": "box", "width": r2(CH_W - 2 * T + 0.6), "length": r2(CH_Z1 - CH_Z0 - 2 * T + 0.6), "height": 0.5, "flatRoof": True,
                     "at": [[r2(sx * cx), H1 - 0.5, r2(cz), 0] for sx in (1, -1)], "standsOn": ["north chapel"], "_about": "the chapels' ceilings and the roofs round their domes"})
add("chapel domes", comp("components/drum-dome", {"R": 4.6, "dt": 0.5, "H": 1.0, "n": 16, "every": 4, "winW": 0.6, "winSill": 0.2, "winH": 0.35,
                                                  "profile": "semicircular", "domeT": 0.4, "lanternR": 0.85, "lanternH": 3.0},
                         [[r2(sx * cx), H1, r2(cz), 0] for sx in (1, -1)], build=["drum", "dome", "lantern"], standsOn=["chapel decks"],
                         _about="the chapels' slate domes on short drums, a lantern on each"))

# ---- the nave: the aisles' outer walls, the arcade, the clerestory over it, the roofs
nave_arch = {"at": 0, "width": 9.0, "sill": 0, "springing": 6.5, "head": semi}   # (the front's arch backW x backH, through from its hall)
cross = lambda: [{"at": 0, "width": 12.0, "sill": 0, "springing": AH, "head": {"profile": "flat"}},        # (a notch: the arch is the transept's)
                 {"at": 12.4, "width": 4.4, "sill": 0, "springing": 8.0, "head": semi}, {"at": -12.4, "width": 4.4, "sill": 0, "springing": 8.0, "head": semi}]
carch = [{"at": 0, "width": 12.0, "sill": 0, "springing": 4.0, "head": semi}]      # (the clerestory's share of the crossing's arch: 14 + 4 = 18)
SEC = dict(AW=AW, NW=NW, AH=AH, NH=NH, T=T, CT=1.4)    # (the clerestory 1.4 thick: the vault's abutment)           # (the body's section: baroque.basilica_body, its barrel vault with lunettes)
baroque.basilica_body(add, "nave", BZ, Z5, 5, front=[nave_arch], back=cross(), cback=carch, **SEC,
                      about="the nave and its aisles: five bays from the front to the crossing")
baroque.basilica_body(add, "choir", ZT, ZR, 3, front=cross(), back=[{"at": 0, "width": 12.0, "sill": 0, "springing": AH, "head": {"profile": "flat"}}],
                      cfront=carch, cback=carch, **SEC, about="the choir's three bays between the crossing and the cross range, the aisles running on beside it")
add("nave roof", {"type": "roof", "form": "gable", "width": NW, "length": r2(BZ - Z5), "pitch": 45, "overhang": 0.4, "at": [[0, NH, r2((BZ + Z5) / 2), 0]],
                  "standsOn": ["nave clerestory"], "_about": "the steep slate roofs over the nave, the choir and the high choir"})
add("choir roof", {"type": "roof", "form": "gable", "width": NW, "length": r2(ZT - ZE), "pitch": 45, "overhang": 0.4, "at": [[0, NH, r2((ZT + ZE) / 2), 0]],
                   "standsOn": ["choir clerestory"]})

# ---- the transept and the crossing: the arms barely past the aisles; piers and arches, pendentives, the dome
TL = Z5 - ZT
tz = (Z5 + ZT) / 2
xarch = {"at": 0, "width": 12.0, "sill": 0, "springing": 18.0, "head": semi}
aarch = lambda a: {"at": a, "width": 4.4, "sill": 0, "springing": 8.0, "head": semi}
tend = [{"h": 9.0, "openings": [{"at": 0, "width": 2.6, "sill": 0, "springing": 4.6, "head": semi, "surround": {"head": "pediment", "pediment": "segmental"}}]},
        {"openings": [{"at": 0, "width": 3.6, "sill": 2.0, "springing": 10.0, "head": semi, "surround": True}]}]
tside = {"pattern": "1", "width": 2.4, "gap": 1.0, "sill": 9.0, "springing": 14.6, "head": semi, "surround": True}
add("transept", {"type": "enclosure", "plan": {"rect": [2 * TA, r2(TL)]}, "thickness": TV, "height": NH, "interior": True,
                 "faces": {"0": [xarch, aarch(12.4), aarch(-12.4)], "2": [xarch, aarch(12.4), aarch(-12.4)], "1": tend, "3": tend},
                 "orders": [{"tier": 0, "kind": "tuscan", "span": 2}], "courses": True, "at": [[0, 0, r2(tz), 0]],
                 "_about": "the transept: the crossing and its two short arms, the great arches into the nave and the choir, a door and a window in each end"})
add("crossing piers", {"type": "box", "width": 2.0, "length": 2.0, "height": 18.0,
                       "at": [[r2(sx * 7.0), 0, r2(z), 0] for sx in (1, -1) for z in (Z5 - T - 1.0, ZT + T + 1.0)],
                       "_about": "the four piers of the crossing"})
SP = TL - 2 * T - 4.0
add("crossing arches", {"type": "barrel", "width": r2(SP), "length": 2.0, "springing": 18.0, "top": NH, "head": semi,
                        "at": [[r2(sx * 7.0 + 1.0), 0, r2(tz), Q] for sx in (1, -1)], "standsOn": ["crossing piers"],
                        "_about": "the arches from pier to pier into the transept's arms"})
DR = 6.6
add("pendentives", {"type": "pendentives", "span": 2 * DR, "springing": NH - DR, "sides": 16, "deck": {"thickness": 0.6, "out": 2.2},
                    "at": [[0, 0, r2(tz), 0]], "_about": "the pendentives over the crossing, and the deck round the drum's foot"})
add("dome", comp("components/drum-dome", {"R": DR, "dt": 1.0, "H": 11.0, "n": 16, "every": 2, "winW": 1.5, "winSill": 8.2, "winH": 1.9,
                                          "profile": "semicircular", "domeT": 0.8, "ribW": 0.3, "lanternR": 1.7, "lanternH": 8.0},
                 [[0, NH + 0.6, r2(tz), 0]], build=["drum", "drum piers", "dome", "lantern"], standsOn=["pendentives"],
                 _about="the dome over the crossing: a tall drum, its windows in every other one of its sixteen bays clear over the ridges round it, the slate dome, the lantern to about 54 m"))
add("transept roofs", {"type": "roof", "form": "gable", "width": r2(TL), "length": r2(TA - NW / 2), "pitch": 45, "overhang": 0.4,
                       "at": [[r2(sx * (NW / 2 + (TA - NW / 2) / 2)), NH, r2(tz), Q] for sx in (1, -1)], "standsOn": ["transept"],
                       "_about": "the arms' roofs, their gables on the ends"})

# ---- the cross range west of the choir (St Mary's Chapel north, the sacristy south, meeting the monastery) and the high choir
RW = ZR - ZW
rwin = [{"h": 7.0, "openings": {"pattern": "3", "width": 2.0, "gap": 6.0, "sill": 2.6, "springing": 5.4, "head": semi, "surround": True}},
        {"openings": {"pattern": "3", "width": 2.0, "gap": 6.0, "sill": 1.8, "springing": 4.8, "head": semi, "surround": True}}]
rfront = [{"h": 7.0, "openings": [{"at": a, "width": 2.0, "sill": 2.6, "springing": 5.4, "head": semi, "surround": True} for a in (-4.0, 4.0)]},
          {"openings": [{"at": a, "width": 2.0, "sill": 1.8, "springing": 4.8, "head": semi, "surround": True} for a in (-4.0, 4.0)]}]   # (clear of the choir's aisles behind)
rend = [{"h": 7.0, "openings": [{"at": 0, "width": 2.0, "sill": 2.6, "springing": 5.4, "head": semi, "surround": True}]},
        {"openings": [{"at": 0, "width": 2.0, "sill": 1.8, "springing": 4.8, "head": semi, "surround": True}]}]
for sx, nm, x0, x1 in ((1, "north", NW / 2, 39.9), (-1, "south", -NW / 2, -36.8)):
    w, xm = abs(x1 - x0), (x0 + x1) / 2
    inner = "3" if sx > 0 else "1"
    add(f"{nm} range", {"type": "enclosure", "plan": {"rect": [r2(w), r2(RW)]}, "thickness": T, "height": 15.0, "tiers": rwin, "interior": True,
                        "faces": {inner: [], "0": rfront, ("1" if sx > 0 else "3"): rend}, "courses": {"skip": [int(inner)]}, "at": [[r2(xm), 0, r2((ZR + ZW) / 2), 0]],
                        **({"_about": "the cross range west of the choir: St Mary's Chapel (north) and the sacristy (south), running on to the old monastery's wings"} if sx > 0 else {})})
    add(f"{nm} range roof", {"type": "roof", "form": "hip", "width": r2(RW), "length": r2(w), "pitch": 45, "overhang": 0.4,
                             "at": [[r2(xm), 15.0, r2((ZR + ZW) / 2), Q]], "standsOn": [f"{nm} range"]})
HL = ZR - ZE
hwin = {"at": 0, "width": 2.6, "sill": 9.0, "springing": 17.0, "head": semi, "surround": True}
add("high choir", {"type": "enclosure", "plan": {"rect": [NW, r2(HL)]}, "thickness": TV, "height": NH, "interior": True,
                   "faces": {"0": [{"at": 0, "width": 12.0, "sill": 0, "springing": 18.0, "head": semi}], "2": [hwin],
                             "1": [{**hwin, "at": r2(HL / 2 - (ZW - ZE) / 2)}], "3": [{**hwin, "at": r2(-(HL / 2 - (ZW - ZE) / 2))}]},
                   "orders": [{"tier": 0, "kind": "tuscan"}], "courses": True, "at": [[0, 0, r2((ZR + ZE) / 2), 0]],
                   "_about": "the high choir over St Boniface's crypt, through the cross range to the west end"})
VAULT = {"type": "barrel", "springing": 18.4, "top": NH, "head": {"profile": "segmental", "rise": 6.0}}   # (a flattened barrel over the windows' heads)
add("high choir vault", {**VAULT, "width": NW - 2 * TV, "length": r2(HL - 2 * TV), "at": [[0, 0, ZR - TV, 0]], "standsOn": ["high choir"],
                         "_about": "the high choir's barrel vault and the transept arms'"})
add("transept vaults", {**VAULT, "width": r2(TL - 2 * TV), "length": r2(TA - TV - NW / 2), "at": [[TA - TV, 0, r2(tz), Q], [-NW / 2, 0, r2(tz), Q]],
                        "standsOn": ["transept"]})

# ---- the obelisks on the square's front line beside the chapels (11 m, sandstone; roman_baroque.obelisk, plain)
OX = X1 + CH_W + 3.2
for sx, nm in ((1, "north"), (-1, "south")):
    roman_baroque.obelisk(add, sx * OX, 45.0, shaft=7.0, foot=0.55, top=0.36, pedH=3.4, pedW=2.0, crown=0, lions=False, name=f"{nm} obelisk")

# ---- the statues (statuary.py), sandstone: the Salvator blessing on the pediment's point; Simplicius and Faustinus
# either side of the great window; St Boniface (south) and St Sturmius (north) on the towers' upper storey
apex = HF + (CW / 2 + 1.0) * math.tan(math.radians(34))
stat = {"statue Salvator": statue((0, apex - 0.3, FZ - 0.6), kind="man", style="roman", stone="sandstone", scale=1.7, seed=3, face=FACE_PZ)}
for sx, nm, s in ((-1, "Simplicius", 5), (1, "Faustinus", 7)):          # (martyrs: the palm; between each pair of columns)
    add(f"pedestal {nm}", pedestal((sx * 6.0, H1 + 0.3, FZ + 0.45), 1.2, 0.9, 0.9))
    stat[f"statue {nm}"] = statue((sx * 6.0, H1 + 1.2, FZ + 0.45), kind="man", style="roman", stone="sandstone", scale=1.35, seed=s, face=FACE_PZ,
                                  hold={"R": "items/tools/palm-frond"})
for sx, nm, s, h in ((-1, "Boniface", 9, "items/tools/book"), (1, "Sturmius", 11, "items/tools/staff")):   # (the gospel book he died under; the abbot's staff)
    tx = sx * (CW / 2 + TW / 2)
    add(f"pedestal {nm}", pedestal((tx, H1 + 0.3, FZ + 0.45), 1.3, 0.9, 0.9))
    stat[f"statue {nm}"] = statue((tx, H1 + 1.2, FZ + 0.45), kind="man", style="roman", stone="sandstone", scale=1.45, seed=s, face=FACE_PZ,
                                  hold={"R": h})
for k, v in capped(stat).items(): add(k, v)

doc = {"name": "Fulda Cathedral",
       "_about": "FULDA CATHEDRAL (Dom St. Salvator), Johann Dientzenhofer 1704-12: a cruciform three-aisled pillar basilica turned west like St Peter's, its front the east one on the Domplatz -- the `twin-tower-front` (two 65 m towers close round the centre, a Doric and a Corinthian storey, the portal between engaged columns, the great window, the pediment and the Salvator; the clock stage, the belfry and each tower's `baroque-helm`: Schweifkuppel, open lantern, a second Schweifkuppel and lantern, spike, pineapple, cross), the two domed chapels and the obelisks either side; the nave and aisles, the short transept and the crossing DOME on its drum (pendentives, `drum-dome`), the choir, the cross range of St Mary's Chapel and the sacristy, the high choir over St Boniface's crypt. On OpenStreetMap's plan. Generated by tools/archgen/fulda.py. The front (east) is +z.",
       "params": {"detail": 4}, "base": {"height": 0.5, "steps": 3, "stepOut": 0.4, "margin": 5}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/fulda.json"), "w").write(json.dumps(doc, indent=2) + "\n")

# ================================================================ the finish
FINISH = {
    "name": "Fulda Cathedral", "building": "architecture/fulda",
    "_about": "Fulda Cathedral (written by tools/archgen/fulda.py): the whole outside in sandstone ashlar of mixed beds -- buff and grey blocks with rose-red ones among them (stone/ashlar two stones, palette fulda), as the front shows; the helms, the chapels' domes, the crossing dome and every roof in slate; the helms' lanterns slated too; the balls and crosses gilt, the clocks gilt on copper; inside, the white walls, vaults and stucco (plaster) over a light grey stone floor, as the church's white interior with its black and gold.",
    "stone": {"color": "#bfae94", "accent": "#a2876e", "pat": "ashlar"},
    "rules": [
        {"parts": "kind:glass", "pattern": "glass/quarries", "palette": "grisaille", "_about": "clear leaded glass in small quarries"},
        {"parts": ["front/helms/ball", "front/helms/cross", "chapel domes/lantern/finial", "dome/lantern/finial"], "pattern": "roofs/gold leaf", "palette": "gold", "_about": "the gilt balls (pineapples), crosses and finials"},
        {"parts": ["front/helms/lantern", "front/helms/lantern head", "front/helms/lantern 2", "front/helms/lantern 2 head", "front/helms/foot",
                   "chapel domes/lantern/tower", "chapel domes/lantern/drum"], "side": "out", "pattern": "roofs/slate", "palette": "slate",
         "_about": "the helms' lanterns and the chapels' lanterns hung with slate like their bulbs"},
        {"parts": ["chapel domes/drum"], "pattern": "stone/ashlar fine", "palette": "fulda", "_about": "the chapels' low drums: sandstone"},
        {"parts": "chapel decks", "surface": "floor", "pattern": "roofs/sheet metal", "palette": "lead", "_about": "the flat roofs round the chapels' domes: lead"},
        {"parts": ["front/clocks/ring", "front/clocks/marks", "front/clocks/hub", "front/clocks/hands"], "pattern": "roofs/gold leaf", "palette": "gold", "_about": "the clocks: gilt ring, marks and hands..."},
        {"parts": "front/clocks/dial", "pattern": "roofs/sheet metal", "palette": "copper", "_about": "...on a copper plate"},
        {"parts": "kind:pendentives", "surface": "roof", "pattern": "roofs/sheet metal", "palette": "lead", "_about": "the deck round the drum's foot: lead"},
        {"parts": ["kind:barrel", "kind:groin", "kind:pendentives"], "pattern": "stone/plaster", "palette": "plaster-white", "_about": "the vaults, arches and pendentives: white stucco"},
        {"parts": ["front/centre", "transept", "nave aisles", "choir aisles", "high choir", "nave clerestory", "choir clerestory"], "surface": "ceiling",
         "pattern": "stone/plaster", "palette": "plaster-white", "_about": "the arches' soffits inside"},
        {"parts": "kind:column", "pattern": "stone/ashlar fine", "palette": "fulda", "_about": "the engaged columns and the obelisks: finer dressed"},
        {"parts": "kind:dome", "surface": "roof", "pattern": "roofs/slate", "palette": "slate", "_about": "the helms, the chapels' domes and the crossing dome: slate"},
        {"parts": "kind:roof", "surface": "roof", "pattern": "roofs/slate", "palette": "slate", "_about": "the roofs: slate"},
        {"surface": "floor", "side": "in", "pattern": "floors/flagstones", "palette": "marble-grey", "_about": "inside: light grey stone flags"},
        {"surface": "floor", "pattern": "floors/flagstones", "palette": "sandstone-grey", "_about": "the Domplatz: sandstone flags"},
        {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white", "_about": "inside: the white walls and stucco"},
        {"side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
        {"parts": "kind:moulding", "pattern": "stone/ashlar fine", "palette": "fulda", "_about": "the orders, cornices and surrounds: the same sandstone, finer dressed"},
        {"pattern": "stone/ashlar two stones", "palette": "fulda", "_about": "outside: sandstone ashlar, buff and grey with rose-red blocks among them"},
    ]}
open(os.path.join(ROOT, "assets/finishes/fulda.json"), "w").write(json.dumps(FINISH, indent=2) + "\n")
print(len(parts), "parts")
