# THE HUNGARIAN PARLIAMENT (Orszaghaz), Budapest -- Imre Steindl, 1885-1904, Gothic Revival -- rebuilt (2026-11-03) on
# its OSM plan with the Gothic Revival library (neogothic.py): long RANGES of three storeys, a buttress-pier at every bay
# line rising through the openwork cresting to a pinnacle, a stone dormer gable over every bay (the "forest of
# pinnacles"); the RIVER ARCADE along the Danube front; in the middle the sixteen-sided DOME with its flying buttresses
# and pinnacles, the traceried drum, the ribbed pointed dome and the lantern spire to 96m; either side the two CHAMBERS
# rising over the ranges under steep roofs, a turret with a copper spire on each corner; the two END PAVILIONS with their
# turrets and great gables; the river centre's seven gables between its two openwork TOWERS; and on the land side the
# stair hall's wing with its towers, the LAND FRONT on Kossuth Square with the frontispiece, its three-arched porch under
# the great gable, and the broad stair.
#   Axes: +z is the RIVER (west), -z the land front (Kossuth Square, east); +x south, -x north; the dome on the origin.
#   SOURCED: length 268m, width 123m, dome 96m high, 16-sided drum, the plan (OpenStreetMap: way outlines and the
#   building:part heights -- dome 75m to the dome's crown, lantern 80, spire 96; chamber cornice ~38.5 and roof 48.5;
#   end-pavilion turrets 44; river towers 66.2; range roofs 31-37; the courts: 10 by the sources, 8 open ones mapped,
#   the other two light wells under glass). The chamber turrets' spires to ~65m are from photographs (OSM: 56.2).
#   ESTIMATED (from photographs): the storey heights, the cornice at 24.6m, the bay of 5.5m, windows, piers, pinnacles,
#   dormer gables, the arcade's depth, the drum's and the dome's detail, the porch and the stair.
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from neogothic import (Rect, facade_block, turret, gothic_tower, flyer_ring, gothic_dome, arcade, great_gable, risalit, STOREYS,
                       POINTED, ROUND, r4, Q, MIRROR)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}

H = 24.6                                   # the ranges' cornice
BAY = 5.5
PIERS = {"w": 0.8, "d": 0.55, "up": 1.6}
PIN = {"w": 0.62, "h": 1.4, "s": 2.6}
CREST = {"h": 0.9, "panel": 3.4, "every": 0}
DORM = {"w": 2.9, "h": 4.6, "reach": 4.8, "t": 0.45}
HIP = {"form": "hip", "pitch": 52, "overhang": 0.25}
COURT = 3 * BAY                            # (the court walls: a lancet every third bay)
# the river front's storeys: the ARCADE storey (round arches behind the loggia), the principal storey's two-light lancets
# under small gables, the upper storey's paired lancets
MAIN = dict(STOREYS["main"], wimperg={"pitch": 60, "coping": 0.25, "depth": 0.2})
RMAIN = dict(MAIN, tracery=0)              # (the long ranges' lancets under their gables, glazed without tracery: triangles)
LMAIN = dict(STOREYS["main"], tracery=0)                  # (the land side's: the same lancets, glazed plain)
SIDES = (("south", 1), ("north", -1))


half = lambda sx, r: r if sx > 0 else r.mirrored()                       # (the north half: the south's mirrored)
faces = lambda sx, fs: tuple(fs) if sx > 0 else tuple(MIRROR[f] for f in fs)
ZR = 14.7                                  # the ranges' court faces (OSM: the courts reach z 5.8..14.7)


# ==== THE DOME HALL: the sixteen-sided hall, its flat roof round the drum, the flying buttresses, the dome =================
N = 16
HALL_R, HALL_H = 21.0, 26.0
add("dome hall", {"type": "enclosure", "plan": {"sides": N, "radius": HALL_R}, "thickness": 1.5, "height": HALL_H, "openings": [],
                  "courses": True, "at": [[0, 0, 0, 0]], "_about": "the dome hall: sixteen-sided, under the ranges' roofs all round"})
add("dome hall roof", {"type": "prism", "plan": {"sides": N, "radius": HALL_R}, "height": 0.6, "flatRoof": True, "at": [[0, HALL_H - 0.6, 0, 0]],
                       "_about": "the flat roof round the drum's foot"})
DR = 12.9                                  # the drum to its corners (OSM: 25.7 across)
flyer_ring(add, comp, "dome buttresses", N, 18.2, DR, {"pierW": 1.5, "pierD": 2.6, "pierH": 15.0, "low": 9.5, "high": 12.5, "top0": 13.5,
                                                       "top1": 15.5, "flyW": 0.9, "pin": 1.3, "pinH": 3.0, "pinS": 4.5},
           y=HALL_H, turn=0.5, about="the sixteen flying buttresses round the drum, a pinnacle on every pier (OSM: the ring of masses to 44.2m)")
TOP = gothic_dome(add, comp, "dome", n=N, R=DR, y0=HALL_H, drumH=26.0, T=1.4, winW=2.6, winSill=10.5, lights=2, oculus=2.6,
                  wimperg={"pitch": 62, "coping": 0.3, "depth": 0.25, "crockets": 3, "finial": 1.0},
                  cornerPin={"w": 0.9, "h": 1.6, "s": 4.2}, atticH=3.2, atticWin=1.7, atticRound=True,
                  footPin={"w": 0.7, "h": 1.2, "s": 3.0}, rise=18.0, domeT=0.9, ribW=0.45,
                  lantern={"R": 3.0, "H": 4.5, "rise": 17.5, "spireR": 2.2, "finial": 1.6},
                  about="THE DOME (96m): the sixteen-sided drum, a tall two-light lancet in every face under its gable and a round window over it")

# ==== THE RANGES: river (+z) and land (-z) fronts, from the middle out to the end pavilions =============================
RIS = (42.29, 74.86)                       # the risalits before the chambers: on the river range's bay lines (14 bays of 5.43)
for nm, sx in SIDES:
    # the river range: its loggia before the ground storey, the risalit before the chamber
    rr = half(sx, Rect(26.0, 102.0, ZR, 23.1))
    facade_block(add, f"{nm} river range", rr, H, fronts=("pz",), plain=("nz",), bay=BAY, plain_bay=COURT, piers=PIERS, pinnacle=PIN, cresting=CREST,
                 storeys=("arcade", RMAIN, "upper"), dormers=DORM, roof=HIP, skip=[("pz", sx * RIS[0], sx * RIS[1])],
                 about=f"the {nm} half of the RIVER FRONT: three storeys in bays between buttress-piers, each rising to a pinnacle over the cresting; a stone gable over every bay")
    risalit(add, f"{nm} river risalit", rr, "pz", sx * RIS[0], sx * RIS[1], 1.5, H, bay=5.43, piers=PIERS, pinnacle=PIN, cresting=CREST,
            storeys=("arcade", RMAIN, "upper"), dormers=DORM, roof=HIP, gables=(sx * 45.0, sx * 72.14),
            gable={"w": 6.4, "h": 10.5, "t": 0.6, "pinnacle": {"w": 0.9, "h": 1.6, "s": 3.6, "crockets": 2}, "roof": {"reach": 9.8}},
            about="the RISALIT before the chamber: brought forward, its corner piers rising to great pinnacles, a great gable at each end")
    arcade(add, f"{nm} river range", rr, "pz", 4.2, 7.0, bay=BAY, about="the arcade along the Danube: a round arch in every bay, the balcony over it")
    # the land range
    lr = half(sx, Rect(31.0, 102.0, -23.1, -ZR))
    facade_block(add, f"{nm} land range", lr, H, fronts=("nz",), plain=("pz",), bay=BAY, plain_bay=COURT, piers=PIERS, pinnacle=PIN,
                 storeys=("arcade", LMAIN, "upper1"), dormers=DORM, roof=HIP,
                 about=f"the {nm} half of the land front's long ranges")
    # the spine between the courts, from the dome hall to the chamber, and the cross range beyond the chamber
    sp = half(sx, Rect(19.0, 45.6, -6.0, 6.0))
    facade_block(add, f"{nm} spine", sp, 27.0, fronts=(), plain=("pz", "nz"), bay=BAY, plain_bay=COURT, roof={"form": "gable", "pitch": 59, "overhang": 0.2},
                 storeys=({"kind": "plain", "h": 9.0, "w": 1.4, "sill": 1.4, "clear": 1.4, "head": POINTED}, {"kind": "plain", "h": 9.0, "w": 1.4, "sill": 1.4, "clear": 1.4, "head": POINTED}, "plain"),
                 about="the range between the courts, from the dome hall to the chamber: gabled to 37m")
    cr = half(sx, Rect(74.4, 81.0, -ZR, ZR))
    facade_block(add, f"{nm} cross range", cr, H, fronts=(), plain=faces(sx, ("px",)), bay=BAY, plain_bay=COURT, roof=HIP,
                 about="the range beyond the chamber, between its courts")

# ==== THE CHAMBERS: the two houses' halls, rising over the ranges, a turret on every corner ============================
CH = 38.5
for nm, sx in SIDES:
    c = half(sx, Rect(45.25, 74.75, -14.75, 14.75))
    clere = {"kind": "window", "h": 13.9, "w": 2.6, "sill": 2.0, "clear": 1.6, "head": POINTED, "tracery": 2,
             "wimperg": {"pitch": 60, "coping": 0.3, "depth": 0.25, "crockets": 2, "finial": 0.8}}
    facade_block(add, f"{nm} chamber", c, CH, fronts=("pz", "nz"), plain=(), bay=5.9, piers={"w": 1.0, "d": 0.7, "up": 2.0},
                 pinnacle={"w": 0.8, "h": 1.8, "s": 3.4, "crockets": 2}, cresting={"h": 1.1, "panel": 1.5}, interior=False,
                 storeys=({"kind": "blind", "h": H}, clere), roof={"form": "mansard", "pitch": 18, "lowerPitch": 70, "breakH": 6.5, "overhang": 0.3},
                 about=f"the {'Upper' if sx > 0 else 'Lower'} House's CHAMBER, rising over the ranges: tall three-light windows under gables, its steep roof to 48.5m")
    # its four turrets, flush with its corners (OSM: 7.3m square, 44.2m, spire to 56.2m)
    TW = 7.3
    at = [[r4(x - s * (TW / 2 - 0.4)), 0, r4(z - t * (TW / 2 - 0.4))] for (x, s) in ((c.x0, -1), (c.x1, 1)) for (z, t) in ((c.z0, -1), (c.z1, 1))]
    turret(add, f"{nm} chamber towers", at, W=TW, H=44.2, sides=4, t=0.6, win=0.9, blind=24.6,
           spire={"kind": "pinnacle", "w": 3.6, "collar": 0.8, "rise": 20.0, "sides": 8, "crockets": 3},
           corners={"w": 0.9, "h": 1.6, "s": 3.2}, tip={"w": 0.6, "s": 2.6},
           about="the chamber's corner turrets: pinnacles round the foot of a slender dark spire, its tip copper")

# ==== THE END PAVILIONS: mansard-roofed, a turret at every corner, the great gable on the end ============================
for nm, sx in SIDES:
    ep = half(sx, Rect(102.0, 125.5, -32.0, 32.7))
    facade_block(add, f"{nm} end pavilion", ep, H, fronts=faces(sx, ("pz", "px", "nz")), plain=(), bay=BAY, piers=PIERS, pinnacle=PIN, cresting=dict(CREST, faces=("pz",)),
                 storeys=("arcade", LMAIN, "upper1"), dormers=DORM, roof={"form": "mansard", "pitch": 25, "lowerPitch": 70, "breakH": 6.0, "overhang": 0.25},
                 doors=[(faces(sx, ("px",))[0], 0.0, 3.2, 5.6)],
                 about=f"the {nm} END PAVILION, its corner turrets and the great gable over its end")
    TW = 5.5
    at = [[r4(x - s * (TW / 2 - 0.4)), 0, r4(z - t * (TW / 2 - 0.4))] for (x, s) in ((ep.x0, -1), (ep.x1, 1)) for (z, t) in ((ep.z0, -1), (ep.z1, 1))]
    turret(add, f"{nm} end turrets", at, W=TW, H=32.0, sides=4, t=0.5, win=0.8, every=16.0,
           spire={"kind": "pinnacle", "w": 2.8, "collar": 0.6, "rise": 16.0, "sides": 8, "crockets": 3},
           tip={"w": 0.5, "s": 2.2},
           about="the end pavilions' corner turrets (OSM: 5.5m square to 44m; the spires to ~50m from photographs)")
    # the projection on the end and its great gable (OSM: gabled to 37m, 18.6 x 14.8)
    pj = half(sx, Rect(125.5, 131.6, -7.5, 7.5))
    facade_block(add, f"{nm} end projection", pj, H, fronts=faces(sx, ("px",)), plain=(), bay=5.0, piers=PIERS, pinnacle=PIN,
                 storeys=("arcade", RMAIN, "upper"), roof=None)
    great_gable(add, f"{nm} end gable", [[r4(sx * (131.6 - 0.05)), H, 0, r4(sx * Q)]], w=15.0, h=12.4, t=0.8,
                pinnacle={"w": 1.0, "h": 2.0, "s": 4.0, "crockets": 2}, roof={"reach": 18.6})

# ==== THE RIVER CENTRE: the seven gables between the two towers, the link to the dome hall ===============================
cc = Rect(-17.0, 17.0, 23.6, 37.5)
facade_block(add, "river centre", cc, H, fronts=("pz",), plain=(), bay=4.86, T=1.4, piers=PIERS, pinnacle=PIN, cresting=CREST,
             storeys=("arcade", "loggia", "upper"), bay_roofs={"w": 4.6, "h": 6.6}, doors=[("pz", 0.0, 3.4, 6.0)],
             about="the RIVER CENTRE between the towers: seven bays, the principal storey's seven great open round arches, each bay under its own steep gable and roof (OSM: seven roofs to 31m)")
add("river centre loggia back", {"type": "box", "width": 31.0, "length": 0.5, "height": 16.5, "at": [[0, 0, r4(cc.z1 - 1.4 - 3.0), 0]],
                                  "_about": "the loggia's back wall, in shadow behind the great arches"})
lk = Rect(-26.0, 26.0, 13.5, 23.6)
facade_block(add, "river link", lk, H, fronts=(), plain=(), roof=HIP, about="the range from the river centre to the dome hall")
lk2 = Rect(-31.0, 31.0, -24.5, -13.5)
facade_block(add, "land link", lk2, H, fronts=(), plain=(), roof=HIP, about="the range from the dome hall to the land wing")
# the two openwork towers (OSM: 9.4m square to 27m, 8.2 to 38.5, 6.5 to 44.2, the spire to 66.2)
for nm, sx in SIDES:
    gothic_tower(add, comp, f"{nm} river tower", sx * 21.7, 33.1, 0.0, [
        ({"W": 9.4, "H": 27.0, "t": 1.2, "low": 9.0, "wins": 1, "winW": 2.2, "lights": 0, "bw": 1.3, "bd": 1.2}, ["walls", "buttresses", "slab"]),
        ({"W": 8.2, "H": 11.5, "t": 0.8, "low": 2.0, "wins": 1, "winW": 2.6, "glazed": 0, "lights": 2, "bw": 1.0, "bd": 0.9, "pinH": 2.4, "pinS": 3.6},
         ["walls", "corner pinnacles", "parapet", "slab"]),
    ], octagon={"R": 2.6, "H": 5.7, "t": 0.4, "low": 1.0, "glazed": 0},
        about="the river centre's two towers: a square shaft, an open belfry, an octagon and an openwork spire to 66m")
    add(f"{nm} river tower spire", {"type": "open-spire", "R": 2.0, "rise": 20.5, "rows": 4, "rib": 0.18, "bar": 0.08, "topR": 0.3, "finial": 1.5,
                                    "at": [[r4(sx * 21.7), 44.2, 33.1, 0]], "_about": "the openwork spire, the sky through its tracery"})

# ==== THE LAND WING: the stair hall, its side ranges and towers, the land front and the frontispiece ===================
sh = Rect(-8.4, 8.4, -60.0, -24.5)
facade_block(add, "stair hall", sh, 27.0, fronts=(), plain=("px", "nx"), bay=BAY, plain_bay=COURT, roof={"form": "gable", "pitch": 50, "overhang": 0.2},
             storeys=({"kind": "plain", "h": 9.0, "w": 1.6, "sill": 1.4, "clear": 1.4, "head": POINTED}, {"kind": "window", "w": 2.4, "sill": 3.0, "clear": 1.6, "head": POINTED, "tracery": 2}),
             about="the grand STAIR HALL, from the land front to the dome hall, gabled to 37m")
for nm, sx in SIDES:
    sr = half(sx, Rect(20.0, 31.0, -60.0, -24.5))
    facade_block(add, f"{nm} land wing", sr, H, fronts=faces(sx, ("px",)), plain=faces(sx, ("nx",)), bay=BAY, plain_bay=COURT, piers=PIERS, pinnacle=PIN,
                 storeys=("arcade", LMAIN, "upper1"), dormers=DORM, roof=HIP, about="the side ranges of the land wing")
    turret(add, f"{nm} land towers", [[sx * 33.0, 0, -24.0]], W=5.5, H=32.0, sides=4, t=0.5, win=0.8,
           spire={"kind": "pinnacle", "w": 2.8, "collar": 0.6, "rise": 18.0, "sides": 8, "crockets": 3},
           tip={"w": 0.5, "s": 2.2},
           about="the towers at the land wing's corners (OSM: 5.5m square to 50m)")
lf = Rect(-38.5, 38.5, -75.4, -60.0)
facade_block(add, "land front", lf, H, fronts=("nz", "px", "nx"), plain=("pz",), bay=BAY, piers=PIERS, pinnacle=PIN, cresting=CREST,
             storeys=("arcade", LMAIN, "upper1"), dormers=DORM, roof={"form": "mansard", "pitch": 30, "lowerPitch": 70, "breakH": 4.5, "overhang": 0.25},
             about="the LAND FRONT on Kossuth Square")
fp = Rect(-14.35, 14.35, -81.0, -66.0)
PORCH = {"kind": "window", "h": 10.0, "w": 2.4, "sill": 1.2, "clear": 1.2, "head": POINTED}
facade_block(add, "frontispiece", fp, 28.0, fronts=("nz", "px", "nx"), plain=(), bay=5.74, piers={"w": 1.0, "d": 0.7, "up": 2.0},
             pinnacle={"w": 0.8, "h": 1.8, "s": 3.4, "crockets": 2}, cresting=CREST, interior=True,
             storeys=(PORCH, dict(MAIN, h=10.0, tracery=0), "upper"), roof={"form": "mansard", "pitch": 30, "lowerPitch": 70, "breakH": 4.0, "overhang": 0.25},
             doors=[("nz", -5.74, 3.6, 8.2), ("nz", 0.0, 3.6, 8.2), ("nz", 5.74, 3.6, 8.2)],
             about="the FRONTISPIECE: the porch of three arches into the stair hall, under the great gable")
great_gable(add, "frontispiece gable", [[0, 28.0, r4(fp.z0 + 0.05), math.pi]], w=17.0, h=13.0, t=0.9,
            pinnacle={"w": 1.1, "h": 2.2, "s": 4.4, "crockets": 2}, rose=5.6)
# the PORCH before it: three great open pointed arches between buttresses, a statue on each buttress's pinnacle
po = Rect(-11.0, 11.0, -88.0, -81.0)
facade_block(add, "porch", po, 12.0, fronts=("nz", "px", "nx"), plain=(), bay=7.33, T=1.2, piers={"w": 1.2, "d": 1.0, "up": 2.0},
             pinnacle={"w": 1.0, "h": 1.8, "s": 3.2, "crockets": 2, "figure": 1.9}, cresting=CREST, corner_up=2.0,
             storeys=({"kind": "window", "w": 4.4, "sill": 0, "clear": 1.4, "head": POINTED, "glass": False},), roof=None,
             about="the PORCH on Kossuth Square: three great open pointed arches between buttresses, a statue on every buttress")
add("porch deck", {"type": "box", "width": 22.0, "length": 7.0, "height": 0.5, "at": [[0, 11.5, -84.5, 0]], "walked": True,
                   "_about": "the porch's vault, the balcony over it"})
for nm, sx in SIDES:
    turret(add, f"{nm} frontispiece tower", [[sx * 11.0, 0, -78.2]], W=4.2, H=31.0, sides=8, t=0.45, win=0.7, every=15.0,
           spire={"kind": "pinnacle", "w": 2.6, "collar": 0.5, "rise": 13.0, "sides": 8, "crockets": 3}, tip={"w": 0.45, "s": 2.0},
           about="the slender towers either side of the great gable")
# the broad stair up to the porch from the square (its foot outside the plinth)
SW, BASE_H = 22.0, 3.0                     # (the terrace: estimated from the river photographs)
n = 16; run = 0.36; L = n * run
add("main stair", {"type": "flight", "width": SW, "run": run, "rise": r4(BASE_H / n), "base": -BASE_H, "top": 0.0, "landing": 0,
                   "at": [[r4(-SW / 2), 0, r4(-88.5 - L), -Q]], "_about": "the broad stair up from Kossuth Square to the porch"})
# the two stone LIONS lying on their plinths either side of its foot, facing the square (Béla Markup, 1902)
LION_S = 2.6
add("stair lions", {"type": "component", "use": "components/couchant-lion", "params": {"S": LION_S, "plinthH": 1.6},
                    "at": [[r4(sx * (SW / 2 + 0.62 * LION_S / 2 + 0.3)), -BASE_H, r4(-88.5 - L + 0.56 * LION_S), math.pi] for _, sx in SIDES],
                    "_about": "the guardian lions either side of the stair's foot (components/couchant-lion)"})

# ==== THE RIVER TERRACE: the plinth along the Danube and its two flights =================================================
for nm, sx in SIDES:
    add(f"{nm} river flight", {"type": "flight", "width": 18.0, "run": run, "rise": r4(BASE_H / n), "base": -BASE_H, "top": 0.0, "landing": 0,
                               "at": [[r4(sx * 60.0 + 9.0), 0, r4(47.0 + L), Q]], "_about": "the flights from the embankment up to the terrace before the chambers"})

# the plinth: the building's outline and the river terrace before it
BP = [[-135.0, -36.0], [-42.0, -36.0], [-42.0, -88.5], [42.0, -88.5], [42.0, -36.0], [135.0, -36.0], [135.0, 47.0], [-135.0, 47.0]]
doc = {"name": "Hungarian Parliament",
       "_about": "THE HUNGARIAN PARLIAMENT, Budapest (Imre Steindl, 1885-1904, Gothic Revival), 268m along the Danube, on its OSM plan, from the Gothic Revival library (tools/archgen/neogothic.py): the long RANGES of three storeys in bays between buttress-piers, each pier rising through the openwork cresting to a pinnacle and every bay crowned by a stone dormer gable under its own red roof; the ARCADE along the river; the sixteen-sided DOME (96m) ringed by flying buttresses and pinnacles -- the traceried drum under its gables, the band of small windows, the ribbed pointed dome, the lantern and its spire; the two CHAMBERS rising over the ranges under steep roofs, copper-spired turrets on their corners; the END PAVILIONS with their turrets and great gables; the river centre's seven gables between its two openwork towers; the land wing with the stair hall and its towers; the LAND FRONT on Kossuth Square with the frontispiece, the porch of three arches under the great gable and the broad stair; all on the plinth of the river terrace. +z is the river.",
       "params": {"detail": 4}, "base": {"height": BASE_H, "steps": 5, "stepOut": 0.4, "margin": 3, "plan": {"points": BP}}, "railing": {"type": "stone"},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/parliament.json"), "w").write(json.dumps(doc, indent=2) + "\n")

# ---- the finish (by the photographs): white limestone; the roofs and the dome in dark maroon patterned tile (roofs/patterned
# tile: the lozenges of Budapest's glazed roofs), the dome's ribs, its lantern and spire and the turrets' spires dark lead,
# the turrets' tips copper
STONE = ["dome drum pinnacles", "dome foot pinnacles", "dome buttresses"] + [f"{nm} river tower {w}" for nm, _ in SIDES for w in ("spire", "stage 2", "octagon")]
SPIRES = ["dome spire", "dome lantern"] + [f"{nm} {w} spires" for nm, _ in SIDES for w in ("chamber towers", "end turrets", "land towers", "frontispiece tower")]
TIPS = [f"{nm} {w} tips" for nm, _ in SIDES for w in ("chamber towers", "end turrets", "land towers", "frontispiece tower")]
fin = {"name": "Hungarian Parliament", "building": "architecture/parliament",
       "_about": "The Hungarian Parliament: white limestone (Sóskút), the roofs in dark maroon patterned tile -- a lattice of darker glazed lozenges -- the dome the same between dark lead ribs, the lantern, its spire and the turrets' spires dark, their tips copper; inside, Zsolnay-tiled floors and faux marble.",
       "stone": {"color": "#ece5d3", "accent": "#d6cdb8", "pat": "ashlar"},
       "rules": [
           {"parts": "kind:moulding", "pattern": "stone/ashlar fine", "palette": "limestone", "_about": "the courses in the walls' own limestone: relief, not colour"},
           {"parts": "kind:ribs", "color": "#3f4640", "_about": "the dome's ribs: lead"},
           {"parts": "river centre loggia back", "color": "#6b645a", "_about": "the loggia's back wall, in its shadow"},
           {"parts": TIPS, "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the copper tips of the turrets' spires"},
           {"parts": SPIRES, "pattern": "roofs/fish scale", "palette": "slate", "_about": "the dark spires: the turrets', the lantern's"},
           {"parts": STONE, "pattern": "stone/ashlar fine", "palette": "limestone", "_about": "the stone spires and pinnacles: the river towers', the dome's rings"},
           {"parts": ["kind:roof", "kind:dome"], "surface": "roof", "pattern": "roofs/patterned tile", "palette": "parliament-tile"},
           {"parts": "kind:dome", "pattern": "roofs/patterned tile", "palette": "parliament-tile"},
           {"surface": "floor", "side": "in", "pattern": "floors/octagon and dot", "palette": "marble-rose"},
           {"surface": "floor", "pattern": "floors/flagstones", "palette": "limestone"},
           {"surface": "wall", "side": "in", "pattern": "painted/faux marble", "palette": "baroque"},
           {"surface": "wall", "pattern": "stone/ashlar fine", "palette": "limestone"}]}
open(os.path.join(ROOT, "assets/finishes/parliament.json"), "w").write(json.dumps(fin, indent=2) + "\n")
print(len(parts), "parts")
