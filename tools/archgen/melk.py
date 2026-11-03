#!/usr/bin/env python3
"""STIFT MELK (2026-11-03, rebuilt; was a court block, a church and a terrace): Jakob Prandtauer's Benedictine abbey on
its rock over the Danube, 1702-36, as an arch-engine definition (assets/architecture/melk.json) and its finish.

THE PLAN is OpenStreetMap's (ways 41656763 the abbey, 303398928 the church, building:parts 827142334..827142370, the courts
29763625 Praelatenhof, 41656760 Kolomanihof, 41656759 Torwartlhof, 29753403 Konventhof), turned so the abbey's axis --
the church's, 7.1 degrees off east -- is x: x EAST along the axis, z SOUTH across it (the town is south, the Danube north
and west), the dome's centre the origin, y 0 the courts' and the church's floor. West to east (about 320 m):
  the ALTANE: the curved terrace range closing the Kolomanihof to the west, banded ochre and white, a great arch in its
    middle opening on the view (columns and a balustrade in it), its roof the terrace walk at the principal floor;
  the two PAVILIONS it joins, splayed nine degrees like the arms of a U: the MARBLE HALL's to the south (it runs on into
    the Kaisertrakt), the LIBRARY's to the north -- each a tall hall through two storeys of windows and oculi on the
    principal floor, under a steep roof with a pedimented Zwerchhaus to the view and to the court; their arms run on
    east to the church's towers;
  the KOLOMANIHOF between them and the CHURCH (Stiftskirche St. Peter und Paul): the TWIN-TOWER FRONT (components/
    twin-tower-front: two storeys of a Tuscan and a Corinthian order (Composite in the original), the portal, the round window of the upper storey,
    Peter and Paul, Michael and the guardian angel, the risen Christ between two angels on the attic; the towers' belfry
    stage, the clock stage and their onion helms with lanterns, 64 m); the wall-pillar nave of three bays with its side
    chapels and the EMPOREN (galleries) over them, the barrel vault with lunettes; the shallow transept and the DOME on its
    drum over the crossing (pendentives, components/drum-dome), the presbytery with the gilt high altar, the monks' choir
    behind under its pyramid and lantern;
  the PRAELATENHOF (84 x 42 m) with the Kolomanibrunnen in its middle, its west, north and east wings, the KAISERSTIEGE in
    its south-west corner climbing to every storey, the KAISERTRAKT along the whole south side (196 m, the KAISERGANG
    its corridor on the principal floor, the imperial rooms off it) from the Marble Hall to the east wing;
  the TORWARTLHOF east of it, the gate building of 1718 between the two BASTIONS (St Leopold and St Koloman beside the
    gateway), the round tower to the north-east; north of the church the Konvent's ranges round the Konventhof.
SOURCED: de.wikipedia "Stift Melk" (axis 320 m; Kaisertrakt and its 196 m Kaisergang on the first floor; Praelatenhof
  84 x 42 m with the Kolomanibrunnen; the Kaiserstiege in its south-west corner; the Marble Hall joined to the Kaisertrakt,
  the Library opposite, the Altane between them; the church a barrel-vaulted hall with chapel niches and Emporen, three
  chapels a side, the dome on its drum, the facade statues; the east portal of 1718 between the bastions, Leopold and
  Koloman); austria-forum.org (the dome 64 m; the towers 64 m). The Commons photographs (Benediktinerstift Melk Luftbild;
  Stiftskirche Melk Fassade; Stift Melk Altane; Stift Melk Westseite; the Kolomanihof, the Praelatenhof, the library, the
  Marble Hall) for the storeys, the bands, the roofs and the colours. ESTIMATED: the storey heights (6.0, 4.6, 4.4, 4.0 to
  the eaves at 19 m), the facade's storeys (17 m, 12.5 m, the belfry 9.5 m, the clock stage 5.5 m), the nave's (chapels
  and Emporen 20 m, vault 29.5 m), the rooms' partitions (no published plan was found on Commons).

    python3 tools/archgen/melk.py      (writes assets/architecture/melk.json and assets/finishes/melk.json)
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import baroque, roman_baroque
from neoclassical import Balusters
from statuary import statue, pedestal, capped, FACE_PX, FACE_NX, FACE_PZ, FACE_NZ
ROOT = os.path.dirname(os.path.dirname(HERE))
parts, build, late = {}, [], []
Q = math.pi / 2
r3 = lambda v: round(v, 3)
SEMI, FLAT = {"profile": "semicircular"}, {"profile": "flat"}
comp = lambda use, params, at, **kw: {"type": "component", "use": "components/" + use, "params": params, "at": at, **kw}


def add(n, d, last=False):
    parts[n] = d
    (late if last else build).append(n)
    return n


# ================================================================ the storeys, the windows, the walls
S = [6.0, 4.6, 4.4, 4.0]                    # ground, principal floor (the Kaisergang, the halls), second, third
LV = [0.0, 6.0, 10.6, 15.0]
EAVE = 19.0
T, SLAB, BAY = 1.0, 0.3, 3.9
win = lambda sill, w, h, sur=None, head=FLAT: (sill, w, h, head, sur)
WINGWIN = [win(1.7, 1.45, 2.7, {"head": False}), win(1.0, 1.6, 3.0, {"head": "cornice", "sill": True}),
           win(0.9, 1.5, 2.6, {"head": False}), win(0.8, 1.4, 2.0)]
PAVWIN = [win(1.7, 1.6, 2.9, {"head": False}), win(0.8, 1.9, 3.4, {"head": "cornice", "keystone": True}, SEMI),
          ("oculus", 1.7), None]          # (the halls: tall arched windows, oculi over them; the third storey is the hall's too)


def opening(u, w, sill, h, head=FLAT, sur=None, glass=None):
    o = {"at": r3(u), "width": w, "sill": r3(sill), "springing": r3(sill + h - (w / 2 if head is SEMI else 0)), "head": head}
    if sur: o["surround"] = sur
    if glass is not None: o["glass"] = glass
    return o


def door(u, w=1.8, h=3.2, head=SEMI):
    return opening(u, w, 0, h, head, glass=False)


def face_tiers(L, storeys, wins, doors=(), skip=(), blind=False, bay=BAY):
    """a face's tiers, a storey each: its windows on the bay rhythm (centred, so the face's direction does not matter),
    none within `skip` spans (another block against it) nor beside a door; doors (u, storey, w, h, head)"""
    nb = max(1, int(L / bay))
    us = [-L / 2 + L / nb * (i + 0.5) for i in range(nb)]
    tiers = []
    for k, sh in enumerate(storeys):
        ops = [door(u, w, h, hd) for (u, dk, w, h, hd) in doors if dk == k]
        wk = wins[k] if k < len(wins) else None
        if wk and not blind:
            for u in us:
                if any(a - 1.2 < u < b + 1.2 for a, b in skip): continue
                if any(abs(u - du) < (dw + 1.6) / 2 + 0.5 for (du, dk, dw, _, _) in doors if dk in (k, k - 1)): continue
                if u < -L / 2 + 1.2 or u > L / 2 - 1.2: continue
                if wk[0] == "oculus":
                    d = wk[1]; ops.append({"at": r3(u), "width": d, "sill": r3((sh - d) / 2 - 0.3), "springing": r3((sh - d) / 2 - 0.3 + d / 2),
                                           "head": SEMI, "foot": SEMI, "surround": {"head": False}})
                else:
                    sill, w, h, head, sur = wk
                    ops.append(opening(u, w, sill, h, head, sur))
        tiers.append({"h": sh, "openings": ops} if k < len(storeys) - 1 else {"openings": ops})
    return tiers


def rect_pts(x0, x1, z0, z1):   # (a rect enclosure's own order: its faces 0 south (+z), 1 east, 2 north, 3 west)
    return [[x0, z1], [x1, z1], [x1, z0], [x0, z0]]


def area(p):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(p, p[1:] + p[:1])) / 2


WINGS = {}


def wing(name, pts, storeys=S, wins=WINGWIN, orders=None, about=None, slabs=(), glass=True, H=None, plain=()):
    """a wing: ONE enclosure on its outline (faces numbered round it as a rect's: start at the south-west corner, east
    along the south face), its storeys; doors and party spans are added before it is written (doorway / party)"""
    assert area(pts) < 0, f"{name}: outline turned the wrong way"
    WINGS[name] = {"pts": [[r3(x), r3(z)] for x, z in pts], "storeys": storeys, "wins": wins, "orders": orders, "about": about,
                   "doors": {}, "party": {}, "slabs": slabs, "glass": glass, "H": H or sum(storeys), "plain": plain}
    return WINGS[name]


def edge(w, i):
    p, q = w["pts"][i], w["pts"][(i + 1) % len(w["pts"])]
    L = math.dist(p, q)
    return p, q, L, ((q[0] - p[0]) / L, (q[1] - p[1]) / L)


def u_on(w, i, x, z):
    p, q, L, e = edge(w, i)
    return (x - (p[0] + q[0]) / 2) * e[0] + (z - (p[1] + q[1]) / 2) * e[1]


def doorway(name, i, x, z, storeys=(0,), w=1.8, h=3.2, head=SEMI):
    W = WINGS[name]
    for k in storeys:
        hh = min(h, W["storeys"][k] - 0.6)
        W["doors"].setdefault(i, []).append((u_on(W, i, x, z), k, w, hh, head if k == 0 else FLAT))


PARTY = []


def party(a, ia, b, ib, p0, p1, doors=(), storeys=(0, 1, 2, 3), w=1.8, h=3.2):
    """two wings face to face along p0-p1 (each its own wall): no windows there, the courses stopped, and a doorway
    through both walls at each of `doors` (world points) on each storey; the strip between the walls' middles theirs"""
    for nm, i in ((a, ia), (b, ib)):
        W = WINGS[nm]
        u0, u1 = sorted((u_on(W, i, *p0), u_on(W, i, *p1)))
        W["party"].setdefault(i, []).append((u0, u1))
        for d in doors: doorway(nm, i, d[0], d[1], storeys, w, h)
    PARTY.append((a, b, p0, p1))


def write_wings():
    for name, W in WINGS.items():
        pts, faces, clear = W["pts"], {}, {}
        for i in range(len(pts)):
            p, q, L, e = edge(W, i)
            ds = W["doors"].get(i, [])
            sk = W["party"].get(i, [])
            faces[str(i)] = face_tiers(L, W["storeys"], W["wins"], ds, sk, blind=i in W["plain"])
            if sk: clear[str(i)] = [[r3(L / 2 + a), r3(L / 2 + b)] for a, b in sk]
        d = {"type": "enclosure", "plan": {"points": pts}, "thickness": T, "height": r3(W["H"]), "glass": W["glass"], "interior": True,
             "faces": faces, "courses": {"clear": clear} if clear else {}, "at": [[0, 0, 0, 0]]}
        if W["orders"]: d["orders"] = W["orders"]
        if W["about"]: d["_about"] = W["about"]
        add(name, d)
    for k, (a, b, p0, p1) in enumerate(PARTY):   # (versailles' party walls: the strip from one wall's middle to the other's)
        L = math.dist(p0, p1); ex, ez = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
        nx, nz = -ez, ex
        pts = [[r3(p0[0] + nx * T / 2), r3(p0[1] + nz * T / 2)], [r3(p1[0] + nx * T / 2), r3(p1[1] + nz * T / 2)],
               [r3(p1[0] - nx * T / 2), r3(p1[1] - nz * T / 2)], [r3(p0[0] - nx * T / 2), r3(p0[1] - nz * T / 2)]]
        if area(pts) > 0: pts = pts[::-1]
        add(f"party interior {k + 1}", {"type": "interior", "plan": {"points": pts}, "height": r3(min(WINGS[a]["H"], WINGS[b]["H"])), "at": [[0, 0, 0, 0]],
                                        **({"_about": "where two wings stand face to face: the strip from one wall's middle to the other's is the rooms' (the doorways' reveals inside)"} if k == 0 else {})})


def iwall(name, a, b, doors, storeys=(0, 1, 2, 3), y0=0.0, t=0.3, about=None, dw=1.3, dh=2.7, H=EAVE, levels=None):
    """an inner wall from a to b (x, z), centred on that line, up the storeys: a doorway at each distance from a in
    `doors` on every storey (a list of lists: the storey's own)"""
    levels = levels or S
    L = math.dist(a, b); dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    tiers = []
    for k, sh in enumerate(levels):
        dd = doors[k] if doors and isinstance(doors[0], (list, tuple)) else doors
        ops = [opening(d - L / 2, dw, 0.0 if k == 0 else 0.0, min(dh, sh - 0.7), FLAT, glass=False) for d in dd] if k in storeys else []
        tiers.append({"h": sh, "openings": ops} if k < len(levels) - 1 else {"openings": ops})
    mx, mz = (a[0] + b[0]) / 2 - t / 2 * dz, (a[1] + b[1]) / 2 + t / 2 * dx
    d = {"type": "wall", "width": r3(L), "height": r3(H - y0), "thickness": t, "tiers": tiers, "glass": False,
         "at": [[r3(mx), y0, r3(mz), r3(math.atan2(-dz, dx))]]}
    if about: d["_about"] = about
    return add(name, d)


def slab(name, x0, x1, z0, z1, ks=(1, 2, 3), about=None, yaw=0.0, cx=None, cz=None):
    d = {"type": "box", "width": r3(x1 - x0), "length": r3(z1 - z0), "height": SLAB,
         "at": [[r3((x0 + x1) / 2 if cx is None else cx), r3(LV[k] - SLAB), r3((z0 + z1) / 2 if cz is None else cz), r3(yaw)] for k in ks]}
    if about: d["_about"] = about
    return add(name, d)


def hip(name, path, width, pitch=40, y=EAVE, overhang=0.6, ends="hip", about=None, **kw):
    d = {"type": "roof", "path": [[r3(x), r3(z)] for x, z in path], "width": r3(width), "pitch": pitch, "overhang": overhang, "ends": ends,
         "at": [[0, r3(y), 0, 0]], **kw}
    if about: d["_about"] = about
    return add(name, d, last=False)


# ================================================================ THE PLAN (OSM, in the abbey's frame)
# the two splayed arms of the U round the Kolomanihof: each one enclosure from the pavilion at the Altane to the wing it
# meets; the pavilion's east end where OSM parts it (the hall within it)
LIB = wing("library wing", [[-70.0, -13.0], [-31.6, -19.0], [-31.6, -32.3], [-72.0, -26.0]], wins=PAVWIN,
           orders=[{"tier": 1, "kind": "tuscan", "span": 3}],
           about="the library wing: the north arm of the U, splayed 9 degrees -- the LIBRARY's pavilion at its west end over the Altane, the small library and the spiral stair in its arm, east to the north wing")
MAR = wing("marble wing", [[-72.0, 27.4], [-34.0, 33.0], [-34.0, 19.0], [-70.0, 13.6]], wins=PAVWIN,
           orders=[{"tier": 1, "kind": "tuscan", "span": 3}],
           about="the marble wing: the south arm -- the MARBLE HALL's pavilion at its west end, its arm running on into the Kaisertrakt")
KT = wing("kaisertrakt", rect_pts(-34.0, 161.8, 19.0, 33.0),
          about="the KAISERTRAKT: the long south range, 196 m from the marble wing to the east wing, the KAISERGANG its corridor on the principal floor along the court side, the imperial rooms off it toward the town")
PW = wing("praelatenhof west wing", rect_pts(49.8, 63.1, -49.9, 19.0), about="the Praelatenhof's west wing, the KAISERSTIEGE in its south end; running north as the Konventhof's east side")
PN = wing("praelatenhof north wing", rect_pts(63.1, 148.4, -32.5, -19.5), about="the Praelatenhof's north wing")
PE = wing("praelatenhof east wing", rect_pts(148.4, 161.8, -32.5, 19.0), about="the Praelatenhof's east wing, the gate passage through it from the Torwartlhof")
# (the outer ranges: shells of their storeys, a door each, no floors)
NW_ = wing("north wing", rect_pts(-31.6, -5.6, -32.3, -19.0), about="the wing north of the nave, past its little court")
KW = wing("konvent west range", rect_pts(-15.6, -5.6, -47.8, -32.3), about="the Konvent's ranges round the Konventhof north of the church")
KN = wing("konvent north range", [[-5.7, -47.8], [77.6, -50.6], [72.8, -66.2], [-15.8, -60.0]])
KD = wing("konvent east range", [[83.1, -32.5], [105.8, -32.5], [91.5, -80.3], [69.3, -78.4]])
CN = wing("north choir wing", [[-5.6, -15.0], [10.5, -15.0], [10.5, -8.6], [49.8, -8.6], [49.8, -19.5], [-5.6, -19.5]], about="the ranges either side of the choir (sacristy, the abbot's chapel), round the little east court", plain=(0,))
CS = wing("south choir wing", rect_pts(29.5, 49.8, 5.0, 14.5))
TN = wing("torwartlhof north range", [[161.8, -35.0], [168.0, -35.0], [168.0, -27.5], [190.0, -27.5], [190.0, -35.0], [203.0, -35.0], [203.0, -44.0], [161.8, -44.0]],
          storeys=[5.5, 4.5], wins=WINGWIN[:2], about="the Torwartlhof's north range")
TS = wing("torwartlhof south range", rect_pts(166.0, 192.0, 24.5, 33.0), storeys=[5.5, 4.5], wins=WINGWIN[:2], about="the Torwartlhof's south range")
GB = wing("gate building", rect_pts(203.0, 209.0, -20.0, 5.0), storeys=[7.0, 4.5], wins=[None, win(1.0, 1.5, 2.6, {"head": "cornice"})],
          orders=[{"tier": 0, "kind": "tuscan", "span": 2}], about="the gate building of 1718 between the bastions: the gateway through it, St Leopold and St Koloman either side")

# ---- where they meet: party walls, the doorways through them on every storey the floors are walked
party("kaisertrakt", 2, "praelatenhof west wing", 0, (49.8, 19.0), (63.1, 19.0), doors=[(60.6, 19.0)])
party("kaisertrakt", 2, "praelatenhof east wing", 0, (148.4, 19.0), (161.8, 19.0), doors=[(149.9, 19.0)])
party("praelatenhof west wing", 1, "praelatenhof north wing", 3, (63.1, -32.5), (63.1, -19.5), doors=[(63.1, -22.0)])
party("praelatenhof north wing", 1, "praelatenhof east wing", 3, (148.4, -32.5), (148.4, -19.5), doors=[(148.4, -22.0)])
party("marble wing", 1, "kaisertrakt", 3, (-34.0, 19.0), (-34.0, 33.0), doors=[(-34.0, 21.5)], storeys=(0, 1))
party("library wing", 1, "north wing", 3, (-31.6, -19.0), (-31.6, -32.3), doors=[(-31.6, -22.0)], storeys=(0,))
party("north wing", 1, "konvent west range", 2, (-15.6, -32.3), (-5.6, -32.3))
party("konvent west range", 2, "konvent north range", 0, (-15.6, -47.8), (-5.6, -47.8))
party("north choir wing", 3, "praelatenhof west wing", 3, (49.8, -19.5), (49.8, -8.6), doors=[(49.8, -13.0)], storeys=(0,))
party("south choir wing", 1, "praelatenhof west wing", 3, (49.8, 5.0), (49.8, 14.5))
party("praelatenhof north wing", 2, "konvent east range", 0, (83.1, -32.5), (105.8, -32.5))
for nm, i, x, z in (("north wing", 0, -20.0, -19.0), ("konvent west range", 1, -5.6, -40.0), ("konvent north range", 0, 30.0, -48.9),
                    ("konvent east range", 3, 80.0, -50.0), ("north choir wing", 2, 36.0, -8.6), ("south choir wing", 2, 40.0, 5.0),
                    ("torwartlhof north range", 2, 179.0, -27.5), ("torwartlhof south range", 2, 179.0, 24.5)):
    doorway(nm, i, x, z, (0,), 2.0, 3.6)

# ---- the doors from the courts (ground storey) and the halls' doors onto the Altane (principal floor)
for x in (2.0, 26.0, 81.0, 129.0):
    doorway("kaisertrakt", 2, x, 19.0, (0,), 2.2, 3.8)
doorway("praelatenhof west wing", 1, 63.1, 12.0, (0,), 3.0, 4.6)   # THE KAISERSTIEGE's door from the court
doorway("praelatenhof west wing", 1, 63.1, -6.0, (0,), 2.2, 3.8)
doorway("praelatenhof west wing", 3, 49.8, -33.0, (0,), 2.2, 3.8)   # (out to the Konventhof...)
doorway("praelatenhof west wing", 1, 63.1, -43.0, (0,), 2.2, 3.8)   # (...and to the little court behind the north wing)
doorway("praelatenhof north wing", 0, 92.0, -19.5, (0,), 2.2, 3.8)
doorway("praelatenhof north wing", 0, 119.0, -19.5, (0,), 2.2, 3.8)
doorway("praelatenhof east wing", 3, 148.4, 0.0, (0,), 4.2, 5.0)   # the gate passage: from the Praelatenhof...
doorway("praelatenhof east wing", 1, 161.8, 0.0, (0,), 4.2, 5.0)   # ...through the east wing into the Torwartlhof
doorway("gate building", 1, 209.0, -7.5, (0,), 4.4, 6.0)           # the gateway
doorway("gate building", 3, 203.0, -7.5, (0,), 4.4, 6.0)
# (the Altane's walk meets each hall's west face at the principal floor)
ALT_N, ALT_S = (-70.85, -18.5), (-70.71, 18.5)
doorway("library wing", 3, *ALT_N, (1,), 2.2, 4.2)
doorway("marble wing", 3, *ALT_S, (1,), 2.2, 4.2)

# ---- the floors: every storey of the Kaisertrakt and the Praelatenhof's wings (reached by the Kaiserstiege); the
# principal floor of the arms (the halls, the Kaisergang's west end, the small library)
KWELL = (50.8, 56.6, 7.3, 14.9)          # the Kaiserstiege's well in the west wing (x0, x1, z0, z1)
slab("kaisertrakt floors", -33.0, 160.8, 20.0, 32.0, about="the Kaisertrakt's floors, storey over storey")
slab("praelatenhof north floors", 64.1, 147.4, -31.5, -20.5)
slab("praelatenhof east floors", 149.4, 160.8, -31.5, 18.0)
slab("praelatenhof west floors", 50.8, 62.1, -48.9, KWELL[2])
slab("praelatenhof west floors south", 50.8, 62.1, KWELL[3], 18.0)
slab("kaiserstiege landing", KWELL[1], 62.1, KWELL[2], KWELL[3], about="the Kaiserstiege's hall: the floors beside its well")


def inset(pts, d):
    """the outline moved in by d on every side, mitred (assemble.js insetPoints, for this winding)"""
    n, out = len(pts), []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        e0 = (p1[0] - p0[0], p1[1] - p0[1]); e1 = (p2[0] - p1[0], p2[1] - p1[1])
        l0, l1 = math.hypot(*e0), math.hypot(*e1)
        n0, n1 = (e0[1] / l0, -e0[0] / l0), (e1[1] / l1, -e1[0] / l1)      # (inward, for this winding)
        k = d / (1 + n0[0] * n1[0] + n0[1] * n1[1])
        out.append([r3(p1[0] + (n0[0] + n1[0]) * k), r3(p1[1] + (n0[1] + n1[1]) * k)])
    return out


class Frame:
    """a splayed arm's own frame: u along its face 0 from that face's first corner, v square to it into the wing"""
    def __init__(self, w):
        p, q, L, e = edge(w, 0)
        self.p, self.e = p, e
        c = (sum(a[0] for a in w["pts"]) / len(w["pts"]), sum(a[1] for a in w["pts"]) / len(w["pts"]))
        n = (-e[1], e[0])
        if (c[0] - p[0]) * n[0] + (c[1] - p[1]) * n[1] < 0: n = (e[1], -e[0])
        self.n = n
        self.yaw = math.atan2(-e[1], e[0])          # (a part turned so its local +x runs along u)
    def __call__(self, u, v):
        return (self.p[0] + self.e[0] * u + self.n[0] * v, self.p[1] + self.e[1] * u + self.n[1] * v)
    def box(self, u0, u1, v0, v1, y, h):
        """a box's placement and size between u0..u1, v0..v1 (its local x along u)"""
        x, z = self((u0 + u1) / 2, (v0 + v1) / 2)
        return {"width": r3(u1 - u0), "length": r3(v1 - v0), "height": r3(h), "at": [r3(x), r3(y), r3(z), r3(self.yaw)]}


def depth_of(w):
    p, q, L, e = edge(w, 0)
    p3 = w["pts"][3]
    return abs((p3[0] - p[0]) * -e[1] + (p3[1] - p[1]) * e[0])


# ================================================================ THE ARMS: the Library and the Marble Hall
FL, FM = Frame(LIB), Frame(MAR)
DL, DM = depth_of(LIB), depth_of(MAR)
PAV = 23.5                                  # the pavilions' halls: from the west wall to the cross wall at u 23.5
SPIRAL = FL(35.2, DL / 2)                   # the Wendeltreppe in the library wing's arm
doorway("library wing", 0, *FL(33.0, 0), (0,), 2.2, 3.8)    # (the arm's door from the Kolomanihof, by the spiral's foot)
doorway("marble wing", 2, *FM(31.0, DM), (0,), 2.2, 3.8)
add("library wing floor", {"type": "prism", "plan": {"points": inset(LIB["pts"], T), "well": {"radius": 2.2, "sides": 24, "at": [r3(SPIRAL[0]), r3(SPIRAL[1])]}},
                           "height": SLAB, "railing": False, "at": [[0, r3(LV[1] - SLAB), 0, 0]],
                           "_about": "the library wing's principal floor: the Library, the small library, the spiral stair's well"})
add("marble wing floor", {"type": "prism", "plan": {"points": inset(MAR["pts"], T)}, "height": SLAB, "at": [[0, r3(LV[1] - SLAB), 0, 0]],
                          "_about": "the marble wing's principal floor: the Marble Hall and the rooms on to the Kaisergang"})
for F, D, nm, cuts, about in ((FL, DL, "library", (PAV, 31.5), "the library wing's cross walls: the Library's east wall (a door to the small library), the small library's (a door to the spiral stair)"),
                              (FM, DM, "marble", (PAV,), "the Marble Hall's east wall, a door through to the arm and the Kaisergang")):
    for k, u in enumerate(cuts):
        a, b = F(u, 1.0), F(u, D - 1.0)
        iwall(f"{nm} cross wall {k + 1}", a, b, [D / 2 - 1.0], storeys=(0, 1), dw=1.8, dh=3.6, about=about if k == 0 else None)
# THE MARBLE HALL's painted ceiling (Troger's fresco under the roof) and THE LIBRARY's: two storeys of shelves, the
# wooden GALLERY round three sides at the second storey's floor, its flight up along the east wall, the ceiling
add("marble hall ceiling", {"type": "box", **{k: v for k, v in FM.box(1.0, PAV - 0.15, 1.0, DM - 1.0, EAVE - 0.26, 0.25).items() if k != "at"},
                            "at": [FM.box(1.0, PAV - 0.15, 1.0, DM - 1.0, EAVE - 0.26, 0.25)["at"]],
                            "_about": "the Marble Hall's flat ceiling, Troger's fresco on it"})
add("library ceiling", {"type": "box", **{k: v for k, v in FL.box(1.0, PAV - 0.15, 1.0, DL - 1.0, EAVE - 0.26, 0.25).items() if k != "at"},
                        "at": [FL.box(1.0, PAV - 0.15, 1.0, DL - 1.0, EAVE - 0.26, 0.25)["at"]], "_about": "the Library's ceiling, Troger's fresco"})
GW = 1.25
gal = [FL.box(1.0, PAV - 1.4, 1.0, 1.0 + GW, LV[2] - SLAB, SLAB), FL.box(1.0, PAV - 0.15, DL - 1.0 - GW, DL - 1.0, LV[2] - SLAB, SLAB),
       FL.box(1.0, 1.0 + GW, 1.0 + GW, DL - 1.0 - GW, LV[2] - SLAB, SLAB)]
for i, g in enumerate(gal):
    add(f"library gallery {i + 1}", {"type": "box", "width": g["width"], "length": g["length"], "height": g["height"], "at": [g["at"]],
                                     **({"_about": "the Library's gallery round three sides, on consoles at the second storey's floor"} if i == 0 else {})})
fx, fz = FL(PAV - 0.2, 1.0 + GW + 0.1)
n_ = FL.n
add("library gallery stair", {"type": "flight", "run": 0.27, "width": 1.1, "base": 0, "top": r3(S[1]), "steps": 24, "landing": r3(DL - 2.0 - GW - 0.1 - 24 * 0.27),
                              "at": [[r3(fx), LV[1], r3(fz), r3(math.atan2(-n_[1], n_[0]))]],
                              "_about": "the flight up the Library's east wall to its gallery"}, last=True)
add("library spiral", {"type": "spiral-stair", "radius": 2.05, "newel": 0.35, "turn": 24, "top": LV[1], "soffit": 0.25,
                       "at": [[r3(SPIRAL[0]), 0, r3(SPIRAL[1]), 0]],
                       "_about": "the WENDELTREPPE: the spiral stair from the small library down to the ground floor and out to the Kolomanihof and the church"}, last=True)
BAL = Balusters(h=1.0, every=0.32, post=0.11, rail=(0.16, 0.1), plinth=(0.18, 0.1))
LBAL = Balusters(h=1.0, every=0.22, post=0.07, rail=(0.12, 0.08), plinth=(0.14, 0.08))     # (the Library gallery's: wood)
for a, b in (((2.2, 1.0 + GW), (PAV - 1.5, 1.0 + GW)), ((2.2, DL - 1.0 - GW), (PAV - 1.5, DL - 1.0 - GW)), ((1.0 + GW, 1.0 + GW), (1.0 + GW, DL - 1.0 - GW))):
    LBAL.run(FL(*a), FL(*b), LV[2])

# ================================================================ THE ALTANE: the curved terrace between the pavilions
ALT = [ALT_N, (-75.5, -16.6), (-79.8, -13.0), (-82.6, -8.2), (-83.6, -4.0), (-83.6, 4.0), (-82.6, 8.2), (-79.8, 13.0), (-75.5, 16.6), ALT_S]
AW_, AH_ = 5.0, LV[1] - 0.5
arch_ = {"at": 0, "width": 5.0, "sill": 0, "springing": 2.5, "head": SEMI, "glass": False}
awin = {"every": 3.6, "width": 1.4, "sill": 1.6, "springing": 3.6, "head": SEMI, "surround": {"head": False}}
add("altane", {"type": "range", "path": [[r3(x), r3(z)] for x, z in ALT], "width": AW_, "height": AH_, "thickness": 0.9, "side": "right",
               "faces": {"out": awin, "in": awin, "in:4": [arch_], "out:4": [arch_], "end": []},
               "walk": {"t": 0.5, "over": 0.3}, "parapet": False, "courses": True,
               "_about": "the ALTANE: the curved range closing the Kolomanihof to the west, its walls banded, its roof the terrace walk from the Marble Hall to the Library at the principal floor; the great arch in its middle opening on the view"})
# the terrace's balustrades along both edges (the inner and the outer line of the walk), and across the great arch's outer side
def offset(path, d):
    out = []
    for i, p in enumerate(path):
        a = path[max(0, i - 1)]; b = path[min(len(path) - 1, i + 1)]
        ex, ez = b[0] - a[0], b[1] - a[1]; L = math.hypot(ex, ez); ex, ez = ex / L, ez / L
        out.append((p[0] - ez * d, p[1] + ex * d))
    return out
for d in (AW_ / 2 + 0.05, -AW_ / 2 - 0.05):
    line = offset(ALT, d)
    for a, b in zip(line, line[1:]): BAL.run(a, b, LV[1])
BAL.run((-85.95, -2.3), (-85.95, 2.3), 0.0)
add("altane arch columns", {"type": "column", "radius": 0.28, "height": 2.5, "sides": 12, "at": [[-84.1, 0, -1.6, 0], [-84.1, 0, 1.6, 0], [-81.1, 0, -1.6, 0], [-81.1, 0, 1.6, 0]],
                            "_about": "the columns standing in the great arch, as in the photographs"})

# ================================================================ THE PAVILIONS' ROOFS AND GABLES, THE WINGS' ROOFS
def gable_front(name, x, z, yaw, w=7.0, h=3.4, d=4.0, about=None):
    """a pedimented Zwerchhaus on the eaves: a wall `w` wide carried up h over the eaves with an oculus, its own roof back into the great one"""
    add(name, {"type": "enclosure", "plan": {"rect": [w, d]}, "thickness": 0.6, "height": h, "interior": False, "glass": True,
               "faces": {"0": [{"at": 0, "width": 1.5, "sill": r3(h / 2 - 0.75), "springing": r3(h / 2), "head": SEMI, "foot": SEMI, "surround": {"head": False}}], "1": [], "2": [], "3": []},
               "courses": True, "at": [[r3(x), EAVE, r3(z), r3(yaw)]], **({"_about": about} if about else {})})
    add(name + " roof", {"type": "roof", "form": "gable", "width": w + 0.4, "length": d, "pitch": 32, "overhang": 0.35, "at": [[r3(x), EAVE + h, r3(z), r3(yaw)]]})


def arm_roofs(nm, F, D, w):
    u_end = edge(w, 0)[2]
    hip(f"{nm} pavilion roof", [F(0.0, D / 2), F(PAV + 0.5, D / 2)], D, pitch=52, overhang=0.7, about=f"the {nm} pavilion's steep roof")
    hip(f"{nm} arm roof", [F(PAV + 0.5, D / 2), F(u_end + 0.6, D / 2)], D, pitch=42, overhang=0.7, ends="gable")


arm_roofs("library", FL, DL, LIB)
arm_roofs("marble", FM, DM, MAR)
for nm, F, D in (("library", FL, DL), ("marble", FM, DM)):
    wx, wz = F(-0.0, D / 2)
    x0, z0 = F(1.6, D / 2)
    gable_front(f"{nm} west gable", x0, z0, F.yaw + Q, about=f"the {nm} pavilion's pedimented Zwerchhaus over the Altane")
    gx, gz = F(PAV / 2, 1.6 if nm == "library" else D - 1.6)
    gable_front(f"{nm} court gable", gx, gz, F.yaw + (0 if nm == "library" else math.pi))
# the ranges' roofs: hipped, red tile, over each wing's middle line
hip("kaisertrakt roof", [(-34.0, 26.0), (161.8, 26.0)], 14.0, about="the long roofs of red tile over the wings")
hip("praelatenhof west roof", [(56.45, -49.9), (56.45, 19.0)], 13.3)
hip("praelatenhof north roof", [(63.1, -26.0), (148.4, -26.0)], 13.0)
hip("praelatenhof east roof", [(155.1, -32.5), (155.1, 19.0)], 13.4)
hip("north wing roof", [(-31.6, -25.65), (-5.6, -25.65)], 13.3)
hip("konvent west roof", [(-10.6, -47.8), (-10.6, -32.3)], 10.0)
hip("konvent north roof", [(-10.75, -53.9), (75.2, -58.4)], 13.5)
hip("konvent east roof", [(94.45, -32.5), (80.4, -79.35)], 22.0, pitch=32)
hip("north choir roof", [(-5.6, -17.25), (10.5, -17.25)], 4.5, pitch=35, y=EAVE)
hip("north choir roof 2", [(10.5, -14.05), (49.8, -14.05)], 10.9)
hip("south choir roof", [(29.5, 9.75), (49.8, 9.75)], 9.5)
hip("torwartlhof north roof", [(161.8, -39.5), (203.0, -39.5)], 9.0, y=10.0)
hip("torwartlhof north roof 2", [(168.0, -31.0), (190.0, -31.0)], 8.0, y=10.0, ends="gable")
hip("torwartlhof south roof", [(166.0, 28.75), (192.0, 28.75)], 8.5, y=10.0)
hip("gate building roof", [(206.0, -20.0), (206.0, 5.0)], 6.0, y=11.5, pitch=45)
for nm, x, z, yaw in (("kaisertrakt gable", 105.75, 33.0, math.pi), ("praelatenhof north gable", 105.75, -19.5, math.pi), ("praelatenhof west gable", 63.1, -0.25, -Q),
                      ("praelatenhof east gable", 148.4, -0.25, Q), ("kaisertrakt court gable", 105.75, 19.0, 0.0)):
    gable_front(nm, x, z - (1.4 if yaw == math.pi else -1.4 if yaw == 0.0 else 0) * 0 + 0, yaw + math.pi, w=12.0, h=3.6, d=5.0,
                about="a frontispiece's pediment over the middle of a front" if nm == "kaisertrakt gable" else None)

# ================================================================ THE PRAELATENHOF'S ROOMS, THE KAISERGANG, THE KAISERSTIEGE
ALLK = (0, 1, 2, 3)
PX_KT = [-23.0, -12.0, -1.0, 10.0, 21.0, 32.0, 43.0, 54.0, 65.0, 76.0, 87.0, 98.0, 109.0, 120.0, 131.0, 142.0, 153.0]
def room_doors(xs, x0, x1):   # a door from the corridor into each room, a little off its middle
    edges = [x0] + xs + [x1]
    return [r3((a + b) / 2 + 1.0 - x0) for a, b in zip(edges, edges[1:]) if b - a > 3]
iwall("kaisergang wall", (-33.0, 23.15), (160.8, 23.15), room_doors(PX_KT, -33.0, 160.8), about="the KAISERGANG's wall: the corridor 196 m along the court side, a door into each of the imperial rooms (and the same on every storey)")
add("kaisertrakt partitions", {"type": "wall", "width": 8.7, "height": EAVE, "thickness": 0.3, "glass": False,
                               "tiers": [{"h": S[k], "openings": [opening(2.6, 1.3, 0, min(2.7, S[k] - 0.7), FLAT, glass=False)]} for k in range(3)] + [{"openings": [opening(2.6, 1.3, 0, 2.7, FLAT, glass=False)]}],
                               "at": [[x, 0, 27.65, Q] for x in PX_KT], "_about": "the imperial rooms' walls, the doors of their enfilade by the windows"})
PX_PN = [74.0, 85.0, 96.0, 107.0, 118.0, 129.0, 140.0]
iwall("praelatenhof north corridor wall", (64.1, -23.65), (147.4, -23.65), room_doors(PX_PN, 64.1, 147.4))
add("praelatenhof north partitions", {"type": "wall", "width": 7.7, "height": EAVE, "thickness": 0.3, "glass": False,
                                      "tiers": [{"h": S[k], "openings": [opening(-2.0, 1.3, 0, min(2.7, S[k] - 0.7), FLAT, glass=False)]} for k in range(3)] + [{"openings": [opening(-2.0, 1.3, 0, 2.7, FLAT, glass=False)]}],
                                      "at": [[x, 0, -27.65, Q] for x in PX_PN]})
PZ_W = [-38.0, -27.0, -16.0, -5.0]
iwall("praelatenhof west corridor wall", (58.95, -48.9), (58.95, 5.5), room_doors(PZ_W, -48.9, 5.5))
add("praelatenhof west partitions", {"type": "wall", "width": 8.0, "height": EAVE, "thickness": 0.3, "glass": False,
                                     "tiers": [{"h": S[k], "openings": [opening(-2.0, 1.3, 0, min(2.7, S[k] - 0.7), FLAT, glass=False)]} for k in range(3)] + [{"openings": [opening(-2.0, 1.3, 0, 2.7, FLAT, glass=False)]}],
                                     "at": [[54.8, 0, z, 0] for z in PZ_W + [5.5]]})
PZ_E = [-24.0, -13.0, -2.6, 2.6, 13.0]
ewall = room_doors(PZ_E, -31.5, 18.0)
iwall("praelatenhof east corridor wall", (152.55, -31.5), (152.55, 18.0), [[31.5] + [d for d in ewall if abs(d - 31.5) > 2.5]] + [ewall] * 3,
      about="the east wing's corridor wall: the gate passage (the Benediktihalle) open to it on the ground floor")
add("praelatenhof east partitions", {"type": "wall", "width": 8.1, "height": EAVE, "thickness": 0.3, "glass": False,
                                     "tiers": [{"h": S[k], "openings": [opening(2.0, 1.3, 0, min(2.7, S[k] - 0.7), FLAT, glass=False)] if (k > 0) else []} for k in range(3)] + [{"openings": [opening(2.0, 1.3, 0, 2.7, FLAT, glass=False)]}],
                                     "at": [[156.75, 0, z, 0] for z in PZ_E]})
# THE KAISERSTIEGE: a dog-leg up each storey round its well in the west wing's south end, a pair of flights a storey
# (each its own part: a repeated stair's landings would be railed over the next flight)
for k in range(3):
    n = 16 if k == 0 else 12
    add(f"kaiserstiege {k + 1}", {"type": "staircase", "rise": r3(S[k] / (2 * n)), "run": 0.3, "soffit": 0.3, "flight": n, "width": 2.0,
                                  "landing": {"depth": 2.3, "width": 4.4, "shift": -1.2,
                                              "then": [{"from": "back", "at": -1.2, "flight": n, "width": 2.0, "landing": {"depth": 1.0, "width": 2.0}}]},
                                  "at": [[52.0, LV[k], KWELL[2], -Q]],
                                  **({"_about": "THE KAISERSTIEGE: up the stair hall in the Praelatenhof's south-west corner, a dog-leg to every storey -- the principal floor's Kaisergang, the rooms over it"} if k == 0 else {})}, last=True)
    BAL.run((KWELL[1] - 0.15, KWELL[2] + 0.2), (KWELL[1] - 0.15, KWELL[3]), LV[k + 1])
    BAL.run((KWELL[0], KWELL[3] - 0.15), (KWELL[1], KWELL[3] - 0.15), LV[k + 1])

# ================================================================ THE CHURCH (Stiftskirche St. Peter und Paul)
# built in the church's own frame, fulda.py's (front +z, +x to the south), and turned into the abbey's as it is added:
# the front faces west (-x), so a church point (xl, zl) is the abbey's (-zl, xl), and every yaw a quarter less
def W(xl, zl): return (-zl, xl)


def to_abbey(d):
    d = dict(d)
    if "at" in d and isinstance(d["at"], list):
        d["at"] = [[r3(-a[2]) if not isinstance(a[2], str) else f"0 - ({a[2]})", a[1], a[0], (r3(a[3] - Q) if not isinstance(a[3], str) else f"({a[3]}) - 1.5707963")]
                   for a in d["at"]]
    if "lines" in d:
        d["lines"] = [[r3(-l[2]), l[1], l[0], r3(-l[5]), l[4], l[3]] for l in d["lines"]]
    # (a plan's points stay the church's: the part's own turn carries them round)
    return d


def cadd(n, d, last=False):
    return add(n, to_abbey(d), last)


FZ, DF, CW, TW = 41.8, 8.8, 9.4, 8.75       # the front line (x -41.8), the front's depth, its centre's and towers' widths
BZ = FZ - DF                                # the nave's west end
H1, H2, H3, H4 = 17.0, 12.5, 10.5, 5.5      # the front's storeys, the towers' clock stage and belfry
HF = H1 + H2
AWc, NWc, AHc, NHc = CW + 2 * TW, 19.2, 20.0, 29.5     # the body: the chapels' outer walls, the nave's; their heights
TC, CTc, TV = 1.2, 1.4, 1.5
Z5, ZT, ZC, ZM = 9.5, -10.5, -23.4, -29.5  # the transept's west and east faces, the presbytery's end, the monks' choir's
TA = 14.7                                   # the transept's arms reach this far out
EMP = 11.2                                  # the Emporen over the side chapels
semi = SEMI

cadd("church front", comp("twin-tower-front",
     {"cW": CW, "tW": TW, "D": DF, "tD": DF, "pedD": DF, "t": 1.4, "H1": H1, "H2": H2, "H3": H3, "H4": H4, "s": 0.5, "co": 0.7, "chamf": 0.9,
      "pitch": 30, "pediment": "none", "order1": "tuscan", "order2": "corinthian", "doorW": 3.0, "doorH": 6.2, "winW": 3.0, "winSill": 2.4, "winH": 6.6,
      "tWin": 1.4, "backW": 6.0, "backH": 10.0, "pcR": 0.55, "portals": "three", "tDoorW": 1.6, "tDoorH": 3.8,
      "clockStage": "yes", "clock": "yes", "clockR": 1.15, "clockY": 1.8, "clockWinW": 2.3, "belfryWinW": 1.6,
      "hR": 3.0, "hProfile": "onion", "hBulge": 1.3, "hNeck": 0.8, "hRise": 4.0, "hLR": 1.35, "hLH": 2.8, "hR2": 1.55, "hProfile2": "onion",
      "hBulge2": 1.3, "hNeck2": 0.8, "hRise2": 1.9, "hL2R": 0.55, "hL2H": 1.3, "hSpikeH": 1.6, "hBallR": 0.38, "hCrossH": 2.2, "hLanterns": "two"},
     [[0, 0, FZ, 0]],
     _about="THE TWIN-TOWER FRONT (components/twin-tower-front) on the Kolomanihof: a Tuscan and a Corinthian storey (the Composite drawn as Corinthian), the portal and the side portals, the great window, no pediment but the attic with the risen Christ; over the towers the clock stage with its dials and tall arch, the chamfered belfry, the onion helms with their two lanterns, 65 m"))
cadd("front attic", {"type": "box", "width": CW + 1.0, "length": 2.2, "height": 1.6, "at": [[0, HF, FZ - 1.1, 0]],
                     "_about": "the attic over the centre between the towers, the statues on it"})
# THE BODY: a wall-pillar hall read as baroque.basilica_body -- its arcade the wall pillars, its aisles the side chapels --
# its outer walls in two tiers (the chapels' windows, the Emporen's over them), three bays
nave_arch = {"at": 0, "width": 6.0, "sill": 0, "springing": 7.0, "head": semi}
cross = [{"at": 0, "width": 16.4, "sill": 0, "springing": AHc, "head": FLAT}, {"at": 10.9, "width": 2.2, "sill": 0, "springing": 6.0, "head": semi},
         {"at": -10.9, "width": 2.2, "sill": 0, "springing": 6.0, "head": semi}]
carch = [{"at": 0, "width": 16.4, "sill": 0, "springing": 0.5, "head": semi}]
baroque.basilica_body(cadd, "nave", BZ, Z5, 3, front=[nave_arch], back=cross, cback=carch, AW=AWc, NW=NWc, AH=AHc, NH=NHc, T=TC, CT=CTc,
                      order="tuscan", clerWin=(2.2, 1.6, 6.4), vault=6.0, aislePitch=22,
                      about="the nave: three bays of wall pillars, the side chapels between them and the EMPOREN over the chapels, the barrel vault with lunettes")
NB = (BZ - Z5) / 3
row = lambda w, sill, spr: {"pattern": "3", "width": w, "gap": r3(NB - w), "end": 1.0, "sill": sill, "springing": spr, "head": semi, "surround": True}
ais = parts["nave aisles"]
ais.pop("openings", None)
ais["faces"].update({k: [{"h": EMP, "openings": row(2.0, 2.6, 7.6)}, {"openings": row(2.2, 1.0, 5.4)}] for k in ("1", "3")})
ais["orders"] = [{"tier": 0, "kind": "tuscan", "span": 2}]
PXo, PXi = 8.6, AWc / 2 - TC                  # the Emporen: from in the wall pillars' line (a balcony in each arch) to the outer walls
SPZ = BZ - TC - 1.6                          # their spiral stairs' middles, in the westmost chapel each side
for sx, nm in ((1, "south"), (-1, "north")):
    xm = sx * (PXi - 1.55)
    pts = [[sx * PXo, BZ - TC], [sx * PXi, BZ - TC], [sx * PXi, Z5 + TC], [sx * PXo, Z5 + TC]]
    cadd(f"{nm} emporen", {"type": "prism", "plan": {"points": pts, "well": {"radius": 1.55, "sides": 20, "at": [r3(xm), r3(SPZ)]}}, "height": 0.35,
                           "railing": False, "at": [[0, EMP - 0.35, 0, 0]],
                           **({"_about": "the EMPOREN: the galleries over the side chapels, the length of the nave each side"} if sx > 0 else {})})
    cadd(f"{nm} emporen stair", {"type": "spiral-stair", "radius": 1.45, "newel": 0.25, "turn": 27, "top": EMP, "soffit": 0.2, **({} if sx > 0 else {"hand": "left"}),
                                 "at": [[r3(xm), 0, r3(SPZ), 0]], **({"_about": "the spiral stairs up to the Emporen in the westmost chapels"} if sx > 0 else {})}, last=True)
    zs = [BZ - TC] + [z for k in (1, 2) for z in (BZ - k * NB + 0.9, BZ - k * NB - 0.9)] + [Z5 + TC]
    for a, b in zip(zs[0::2], zs[1::2]):
        BAL.run(W(sx * (PXo + 0.15), a - 0.2), W(sx * (PXo + 0.15), b + 0.2), EMP)
# THE TRANSEPT AND THE CROSSING: the shallow arms, the piers, the pendentives, the DOME on its drum
TL, tz = Z5 - ZT, (Z5 + ZT) / 2
xarch = lambda w: {"at": 0, "width": w, "sill": 0, "springing": 20.5, "head": semi}
aarch = lambda a: {"at": a, "width": 2.2, "sill": 0, "springing": 6.0, "head": semi}
tend = [{"h": 20.0, "openings": []}, {"openings": [{"at": 0, "width": 3.0, "sill": 1.2, "springing": 6.4, "head": semi, "surround": True}]}]
cadd("transept", {"type": "enclosure", "plan": {"rect": [2 * TA, r3(TL)]}, "thickness": TV, "height": NHc, "interior": True,
                  "faces": {"0": [xarch(16.4), aarch(10.9), aarch(-10.9)], "2": [xarch(13.2)], "1": tend, "3": tend},
                  "orders": [{"tier": 0, "kind": "tuscan", "span": 2}], "courses": True, "at": [[0, 0, r3(tz), 0]],
                  "_about": "the transept: the crossing and its two short arms, the great arches into the nave and the presbytery, a window high in each end"})
cadd("crossing piers", {"type": "box", "width": 2.0, "length": 2.0, "height": 20.5,
                        "at": [[r3(sx * 9.2), 0, r3(z), 0] for sx in (1, -1) for z in (Z5 - TV - 1.0, ZT + TV + 1.0)], "_about": "the four piers of the crossing"})
SP = TL - 2 * TV - 4.0
cadd("crossing arches", {"type": "barrel", "width": r3(SP), "length": 2.0, "springing": 20.5, "top": NHc, "head": semi,
                         "at": [[r3(sx * 9.2 + 1.0), 0, r3(tz), Q] for sx in (1, -1)], "standsOn": ["crossing piers"],
                         "_about": "the arches from pier to pier into the transept's arms"})
DR = 8.0
cadd("pendentives", {"type": "pendentives", "span": 2 * DR, "springing": NHc - DR, "sides": 16, "deck": {"thickness": 0.6, "out": 2.2},
                     "at": [[0, 0, r3(tz), 0]], "_about": "the pendentives over the crossing (Rottmayr's evangelists), the deck round the drum's foot"})
cadd("dome", comp("drum-dome", {"R": DR, "dt": 1.0, "H": 10.0, "n": 16, "every": 2, "winW": 1.6, "winSill": 4.6, "winH": 3.4,
                                "profile": "semicircular", "domeT": 0.8, "ribW": 0.3, "lanternR": 2.0, "lanternH": 7.5},
                  [[0, NHc + 0.6, r3(tz), 0]], build=["drum", "drum piers", "dome", "lantern", "interior"], standsOn=["pendentives"],
                  _about="the DOME over the crossing: the drum with its eight windows, the copper dome, the lantern, 64 m; inside, Rottmayr's painted cupola"))
cadd("transept roofs", {"type": "roof", "form": "gable", "width": r3(TL), "length": r3(TA - NWc / 2), "pitch": 35, "overhang": 0.4,
                        "at": [[r3(sx * (NWc / 2 + (TA - NWc / 2) / 2)), NHc, r3(tz), Q] for sx in (1, -1)], "standsOn": ["transept"]})
TVv = {"type": "barrel", "springing": 21.5, "top": NHc, "head": {"profile": "segmental", "rise": 6.0}}
cadd("transept vaults", {**TVv, "width": r3(TL - 2 * TV), "length": r3(TA - TV - NWc / 2), "at": [[TA - TV, 0, r3(tz), Q], [-NWc / 2, 0, r3(tz), Q]],
                         "standsOn": ["transept"], "_about": "the arms' vaults"})
# THE PRESBYTERY with the gilt high altar, the monks' choir behind under its own roof and turret
PW_, PL_ = 16.2, ZT - ZC
pwin = [{"h": 20.0, "openings": []}, {"openings": {"pattern": "2", "width": 2.2, "gap": 3.6, "sill": 1.4, "springing": 6.0, "head": semi, "surround": True}}]
cadd("presbytery", {"type": "enclosure", "plan": {"rect": [PW_, r3(PL_)]}, "thickness": 1.4, "height": NHc, "interior": True,
                    "faces": {"0": [xarch(13.2)], "2": [{"at": 0, "width": 4.0, "sill": 0, "springing": 6.0, "head": semi}], "1": pwin, "3": pwin},
                    "orders": [{"tier": 0, "kind": "tuscan", "span": 2}], "courses": True, "at": [[0, 0, r3((ZT + ZC) / 2), 0]],
                    "_about": "the presbytery: its high windows over the side ranges, the high altar at its east end"})
cadd("presbytery vault", {**TVv, "width": PW_ - 2.8, "length": r3(PL_ - 2.8), "at": [[0, 0, ZT - 1.4, 0]], "standsOn": ["presbytery"]})
cadd("presbytery roof", {"type": "roof", "form": "gable", "width": PW_, "length": r3(PL_), "pitch": 35, "overhang": 0.4, "at": [[0, NHc, r3((ZT + ZC) / 2), 0]],
                         "standsOn": ["presbytery"]})
cadd("monks choir", {"type": "enclosure", "plan": {"rect": [PW_, r3(ZC - ZM)]}, "thickness": 1.2, "height": 22.0, "interior": True,
                     "faces": {"0": [{"at": 0, "width": 4.0, "sill": 0, "springing": 6.0, "head": semi}],
                               "1": [{"h": 19.5, "openings": []}, {"openings": []}], "3": [{"h": 19.5, "openings": []}, {"openings": []}],
                               "2": [{"h": 19.5, "openings": []}, {"openings": []}]},
                     "courses": True, "at": [[0, 0, r3((ZC + ZM) / 2), 0]], "_about": "the monks' choir behind the high altar"})
cadd("monks choir roof", {"type": "roof", "form": "hip", "width": PW_, "length": r3(ZC - ZM), "pitch": 35, "overhang": 0.4, "at": [[0, 22.0, r3((ZC + ZM) / 2), 0]],
                          "standsOn": ["monks choir"]})
cadd("choir turret", comp("baroque-helm", {"R": 1.3, "profile": "onion", "rise": 1.6, "lanterns": "one", "LR": 0.7, "LH": 1.6, "spikeH": 0.8, "crossH": 1.2},
                          [[0, 22.0 + 2.1, r3((ZC + ZM) / 2), 0]], standsOn=["monks choir roof"], _about="the little turret on the monks' choir's roof"))
for sx, nm in ((1, "south"),):
    cadd(f"{nm} sacristy", {"type": "enclosure", "plan": {"rect": [r3(14.5 - PW_ / 2), r3(ZT - ZM)]}, "thickness": 1.0, "height": 13.0, "interior": True,
                            "faces": {"3": [], "0": [], "2": [], "1": [{"h": 6.0, "openings": [{"at": 0, "width": 1.6, "sill": 0, "springing": 2.8, "head": semi, "glass": False}] +
                                                                       [{"at": a, "width": 1.5, "sill": 2.0, "springing": 4.2, "head": semi} for a in (-7.0, -3.5, 3.5, 7.0)]},
                                                                     {"openings": {"pattern": "4", "width": 1.5, "gap": 3.0, "sill": 1.2, "springing": 3.8, "head": semi}}]},
                            "courses": {"skip": [3]}, "at": [[r3(sx * (PW_ / 2 + (14.5 - PW_ / 2) / 2)), 0, r3((ZT + ZM) / 2), 0]],
                            "_about": "the sacristy range south of the presbytery"})
    cadd(f"{nm} sacristy roof", {"type": "roof", "form": "shed", "width": r3(14.5 - PW_ / 2), "length": r3(ZT - ZM), "pitch": 25, "overhang": 0.4,
                                 "at": [[r3(sx * (PW_ / 2 + (14.5 - PW_ / 2) / 2)), 13.0, r3((ZT + ZM) / 2), 0]], "standsOn": [f"{nm} sacristy"]})
cadd("nave roof", {"type": "roof", "form": "gable", "width": NWc, "length": r3(BZ - Z5), "pitch": 32, "overhang": 0.4, "at": [[0, NHc, r3((BZ + Z5) / 2), 0]],
                   "standsOn": ["nave clerestory"], "_about": "the church's roofs: grey slate"})
# THE HIGH ALTAR (Beduzzi's: a gilt retable of columns round the painting, the crown over it) and the pews
ALX = -ZC - 1.4
add("high altar columns", {"type": "column", "radius": 0.38, "height": 9.0, "sides": 12, "at": [[r3(ALX - 0.9), 0.6, z, 0] for z in (-3.6, -2.2, 2.2, 3.6)],
                           "_about": "the HIGH ALTAR's retable: its columns, the entablature and the crown over them (gilt)"})
add("high altar", {"type": "box", "width": 1.6, "length": 9.4, "height": 0.6, "at": [[r3(ALX - 0.9), 0, 0, 0], [r3(ALX - 0.6), 9.6, 0, 0]]})
add("high altar crown", {"type": "box", "width": 0.8, "length": 5.0, "height": 3.6, "at": [[r3(ALX - 0.6), 10.2, 0, 0]]})
add("altar", {"type": "zone", "zone": "altar", "w": 4.0, "d": 2.4, "h": 8.0, "at": [[r3(ALX - 3.6), 0, 0, 0]]})
add("seating", {"type": "zone", "zone": "seating", "w": 13.0, "d": 17.0, "h": 15.0, "at": [[-22.0, 0, 0, 0]]})
# THE FRONT's STATUES: the risen Christ between two angels on the attic, Peter and Paul in the upper storey, Michael and
# the guardian angel on the towers' (sandstone, white-washed as the building's trim)
stat = {}
for nm, xl, y, kind, extra in (("Christ", 0.0, HF + 1.6, "man", {"scale": 1.8}), ("angel north", -3.6, HF + 1.6, "woman", {"scale": 1.5, "wings": "raised"}),
                               ("angel south", 3.6, HF + 1.6, "woman", {"scale": 1.5, "wings": "raised"})):
    x, z = W(xl, FZ - 1.1)
    stat[f"statue {nm}"] = statue((x, y, z), kind=kind, style="roman", stone="limestone", seed=len(stat) * 3 + 1, face=FACE_NX, **extra)
for nm, xl, hold in (("Peter", -4.3, "items/tools/book"), ("Paul", 4.3, "items/tools/book"), ("Michael", -(CW / 2 + TW / 2), None), ("guardian angel", CW / 2 + TW / 2, None)):
    x, z = W(xl, FZ + 0.45)
    add(f"pedestal {nm}", pedestal((x, H1 + 0.3, z), 0.9, 1.2, 0.9))
    stat[f"statue {nm}"] = statue((x, H1 + 1.2, z), kind="man", style="roman", stone="limestone", scale=1.45, seed=len(stat) * 3 + 2, face=FACE_NX,
                                  **({"hold": {"R": hold}} if hold else {}), **({"wings": "raised"} if "angel" in nm or nm == "Michael" else {}))

# ================================================================ THE TORWARTLHOF: the bastions, the gate, the round tower
BH = 6.0
BAST = {"north bastion": [(203.0, -20.0), (218.0, -20.0), (224.0, -25.0), (228.0, -32.0), (226.0, -40.0), (218.0, -46.0), (208.0, -49.0), (203.0, -48.0)],
        "south bastion": [(203.0, 5.0), (217.0, 5.0), (226.0, 12.0), (233.0, 25.0), (232.0, 33.0), (240.0, 37.0), (232.0, 44.0), (222.0, 41.0), (203.0, 41.0)]}
for nm, pts in BAST.items():
    add(nm, {"type": "prism", "plan": {"points": [[r3(x), r3(z)] for x, z in pts]}, "height": BH, "railing": False, "courses": True, "at": [[0, 0, 0, 0]],
             **({"_about": "the two BASTIONS either side of the gate building (1718), their tops terraces over the Danube and the town, a flight up to each from the Torwartlhof"} if nm.startswith("north") else {})})
    for a, b in zip(pts[:-1], pts[1:]):
        if abs(a[0] - 203.0) < 0.01 and abs(b[0] - 203.0) < 0.01: continue
        L = math.dist(a, b); ex, ez = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        cx, cz = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
        nx, nz = -ez, ex
        if (cx - a[0]) * nx + (cz - a[1]) * nz < 0: nx, nz = -nx, -nz          # (inward)
        BAL.run((a[0] + nx * 0.25 + ex * 0.3, a[1] + nz * 0.25 + ez * 0.3), (b[0] + nx * 0.25 - ex * 0.3, b[1] + nz * 0.25 - ez * 0.3), BH)
add("north bastion flight", {"type": "flight", "run": 0.3, "width": 2.4, "base": 0, "top": BH, "steps": 32, "landing": 1.4, "at": [[203.0, 0, -23.8, Q]],
                             "_about": "the flights up from the Torwartlhof to the bastions' terraces, against their inner walls"}, last=True)
add("south bastion flight", {"type": "flight", "run": 0.3, "width": 2.4, "base": 0, "top": BH, "steps": 32, "landing": 1.4, "at": [[200.6, 0, 10.0, -Q]]}, last=True)
add("torwartlhof walls", {"type": "box", "width": 11.0, "length": 0.7, "height": 6.5, "at": [[197.5, 0, 33.6, 0], [163.9, 0, 33.6, 0]],
                          "_about": "the court's walls between the ranges"})
add("round tower", {"type": "prism", "plan": {"sides": 16, "radius": 4.65}, "height": 17.0, "courses": True, "at": [[163.85, 0, -51.25, 0]],
                    "_about": "the round tower at the abbey's north-east corner (a relic of the old fortifications)"})
add("round tower helm", comp("baroque-helm", {"R": 4.0, "profile": "onion", "rise": 3.2, "lanterns": "one", "LR": 1.4, "LH": 2.4, "spikeH": 1.2, "crossH": 1.6},
                             [[163.85, 17.0, -51.25, 0]], standsOn=["round tower"]))
for nm, z, hold in (("Leopold", -11.6, "items/tools/staff"), ("Koloman", -3.4, "items/tools/staff")):
    add(f"pedestal {nm}", pedestal((209.9, 0, z), 1.2, 1.2, 2.2, about="the gate's statues of St Leopold and St Koloman on their pedestals"))
    stat[f"statue {nm}"] = statue((209.9, 2.2, z), kind="man", style="roman", stone="limestone", scale=1.5, seed=len(stat) * 3 + 5, face=FACE_PX, hold={"R": hold})

# ================================================================ THE PRAELATENHOF'S FOUNTAIN, THE STATUES, THE WINGS
roman_baroque.fountain(add, 105.75, 0.0, R=4.6, name="kolomanibrunnen")
parts["kolomanibrunnen step"]["_about"] = "the KOLOMANIBRUNNEN in the middle of the Praelatenhof (its basin and bowls; the Kolomani fountain of 1687 drawn with the Roman fountain's bowls)"
for k, v in capped(stat).items(): add(k, v)
write_wings()
for k, v in {**BAL.parts("balustrade"), **LBAL.parts("library balustrade")}.items(): add(k, v)

doc = {"name": "Stift Melk",
       "_about": "STIFT MELK, Jakob Prandtauer's Benedictine abbey on its rock over the Danube (1702-36), about 320 m from the Altane to the gate: the curved ALTANE and its great arch between the two pavilions -- the LIBRARY (north, its gallery, the small library, the spiral stair) and the MARBLE HALL (south) -- the Kolomanihof, the CHURCH (the twin-tower front with its onion helms, the wall-pillar nave with its chapels and Emporen, the crossing dome on its drum, the presbytery with the gilt high altar), the PRAELATENHOF with the Kolomanibrunnen, the KAISERSTIEGE and the 196 m KAISERTRAKT with its Kaisergang on the principal floor, the Torwartlhof between the BASTIONS and the gate building. On OpenStreetMap's plan, turned so the axis is x (east), z south; the dome's centre the origin. Generated by tools/archgen/melk.py.",
       "params": {"detail": 4}, "base": {"height": 0.8, "steps": 3, "stepOut": 0.5, "margin": 4},
       "build": build + late, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/melk.json"), "w").write(json.dumps(doc, indent=1) + "\n")

# ================================================================ THE FINISH
LIB_BOX = [-73.0, -33.5, -38.6, -12.0]
MAR_BOX = [-73.0, 12.0, -46.0, 34.5]
CH_BOX = [-42.6, -14.8, 30.5, 14.8]
G = 0.8                                     # (the base: the building's heights from the ground)
FINISH = {
    "name": "Stift Melk", "building": "architecture/melk",
    "_about": "Stift Melk (written by tools/archgen/melk.py): the facades' ochre-yellow stucco with every order, cornice, band and window surround white, the ground storey and the Altane in banded stucco; the wings' roofs red tile, the church's grey slate, the helms, the dome and the lanterns green copper with gilt balls and crosses; inside, the church's warm marbled stucco and gold under painted vaults, the Marble Hall's marbled walls on a rose marble floor under Troger's ceiling, the Library's walnut and its parquet, the Kaisergang's and the rooms' white walls, stone flags below and parquet above.",
    "stone": {"color": "#e3b75a", "accent": "#d4a64a", "pat": "ashlar"},
    "rules": [
        {"parts": "kind:glass", "pattern": "glass/quarries", "palette": "grisaille", "_about": "clear leaded glass"},
        {"parts": ["church front/helms/ball", "church front/helms/cross", "church front/helms/finial", "choir turret/ball", "choir turret/cross", "choir turret/finial",
                   "round tower helm/ball", "round tower helm/cross", "round tower helm/finial", "dome/lantern/finial", "dome/lantern/cross", "dome/lantern/ball",
                   "high altar columns", "high altar", "high altar crown"], "pattern": "roofs/gold leaf", "palette": "gold",
         "_about": "the balls and crosses gilt; the high altar's gilt retable"},
        {"parts": ["church front/clocks/ring", "church front/clocks/marks", "church front/clocks/hub", "church front/clocks/hands"], "pattern": "roofs/gold leaf", "palette": "gold",
         "_about": "the clocks: gilt ring, marks and hands..."},
        {"parts": "church front/clocks/dial", "pattern": "stone/plaster", "palette": "plaster-white", "_about": "...on white dials"},
        {"parts": ["church front/helms", "choir turret", "round tower helm", "dome/lantern"], "side": "out", "pattern": "roofs/sheet metal", "palette": "copper",
         "_about": "the helms, their lanterns and the dome's lantern: green copper"},
        {"parts": "kind:dome", "surface": "roof", "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the dome: green copper"},
        {"parts": "kind:pendentives", "surface": "roof", "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the deck round the drum's foot"},
        {"parts": ["nave roof", "transept roofs", "presbytery roof", "monks choir roof", "nave aisle roofs", "south sacristy roof"], "surface": "roof",
         "pattern": "roofs/slate", "palette": "slate", "_about": "the church's roofs: grey slate"},
        {"parts": "kind:roof", "surface": "roof", "pattern": "roofs/beaver tail", "palette": "tile-red", "_about": "the wings' and pavilions' roofs: red tile"},
        {"parts": ["altane", "altane/walk"], "surface": "floor", "side": "out", "pattern": "floors/flagstones", "palette": "marble-grey", "_about": "the Altane's terrace walk"},
        {"parts": ["north bastion", "south bastion"], "surface": "floor", "pattern": "stone/sand", "palette": "gravel", "_about": "the bastions' gravel terraces"},
        # inside: the Library, the Marble Hall, the church
        {"parts": ["library gallery", "library gallery stair", "library balustrade plinths", "library balustrade balusters", "library balustrade rails"],
         "pattern": "timber/wood", "palette": "walnut", "_about": "the Library's gallery, its stair and rail: walnut"},
        {"within": LIB_BOX, "side": "in", "surface": "wall", "pattern": "timber/panelling", "palette": "walnut", "_about": "the Library's walls: walnut shelving and panelling"},
        {"within": LIB_BOX, "side": "in", "surface": "floor", "pattern": "timber/basket parquet", "palette": "oak", "_about": "...its parquet"},
        {"within": LIB_BOX, "side": "in", "surface": "ceiling", "pattern": "stone/plaster", "palette": "fresco", "_about": "...Troger's ceiling"},
        {"within": MAR_BOX, "side": "in", "surface": "wall", "above": LV[1] + G, "pattern": "painted/faux marble", "palette": "verona", "_about": "the Marble Hall's marbled stucco walls"},
        {"within": MAR_BOX, "side": "in", "surface": "floor", "above": LV[1] + G - 0.5, "pattern": "floors/checker diagonal", "palette": "marble-rose", "_about": "...its marble floor"},
        {"within": MAR_BOX, "side": "in", "surface": "ceiling", "above": LV[1] + G, "pattern": "stone/plaster", "palette": "fresco", "_about": "...Troger's ceiling"},
        {"parts": ["kind:barrel", "kind:groin", "kind:pendentives", "dome/dome", "dome/drum", "dome/interior"], "side": "in", "surface": "ceiling", "pattern": "stone/plaster", "palette": "fresco",
         "_about": "the church's painted vaults, pendentives and cupola (Rottmayr)"},
        {"parts": ["kind:barrel", "kind:groin"], "pattern": "stone/plaster", "palette": "baroque", "_about": "the arches' and vaults' sides: gilt-edged stucco"},
        {"within": [-35.0, -4.0, -31.0, 4.0], "reveal": True, "pattern": "painted/faux marble", "palette": "baroque-rose", "_about": "the arch from the front's hall into the nave"},
        {"within": CH_BOX, "side": "in", "surface": "wall", "pattern": "painted/faux marble", "palette": "baroque-rose", "_about": "the church: marbled stucco in ochre, rose and grey, gold"},
        {"within": CH_BOX, "side": "in", "surface": "floor", "pattern": "floors/checker", "palette": "marble-grey", "_about": "...its marble floor"},
        {"within": CH_BOX, "side": "in", "surface": "ceiling", "pattern": "stone/plaster", "palette": "fresco"},
        {"parts": ["north emporen", "south emporen", "church front"], "side": "in", "surface": "ceiling", "pattern": "stone/plaster", "palette": "fresco"},
        # the rest inside: white walls, stone flags below, parquet above
        {"surface": "floor", "side": "in", "below": LV[1] + G - 0.5, "pattern": "floors/flagstones", "palette": "marble-grey", "_about": "the ground floor's stone flags"},
        {"surface": "floor", "side": "in", "pattern": "timber/herringbone", "palette": "oak", "_about": "the upper floors' parquet (the Kaisergang, the imperial rooms)"},
        {"surface": "ceiling", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
        {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white", "_about": "the corridors and rooms: white walls"},
        {"side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
        # outside: the courts' paving, the stucco, its white trim
        {"surface": "floor", "pattern": "floors/flagstones", "palette": "sandstone-grey", "_about": "the courts' paving"},
        {"parts": ["kind:moulding", "kind:column", "kind:colonnade", "kind:bars"], "pattern": "stone/plaster", "palette": "plaster-white",
         "_about": "every order, cornice, band, window surround and balustrade: white"},
        {"parts": ["altane", "altane/walls", "north bastion", "south bastion", "round tower"], "surface": "wall", "pattern": "stone/stucco lines", "palette": "plaster-ochre",
         "_about": "the Altane and the bastions: banded ochre stucco"},
        {"surface": "wall", "below": LV[1] + G, "pattern": "stone/stucco lines", "palette": "plaster-ochre", "_about": "the ground storey: banded stucco"},
        {"pattern": "stone/plaster", "palette": "plaster-ochre", "_about": "the facades: ochre-yellow stucco"},
    ]}
open(os.path.join(ROOT, "assets/finishes/melk.json"), "w").write(json.dumps(FINISH, indent=2) + "\n")

# ================================================================ THE DOORS
DOORS = {"name": "Stift Melk: doors", "building": "melk",
         "_about": "Stift Melk: oak doors in raised Baroque panels -- the church's portal and side portals, the gateway in the gate building, the gate passage through the east wing, the Kaiserstiege's door and the doors from the Praelatenhof and the Kolomanihof",
         "doors": [
             {"_about": "the church's portal", "part": "church front/centre", "near": [-41.8, 0.0], "style": "baroque", "leafH": 6.0},
             {"_about": "the side portals in the towers", "part": ["church front/tower left", "church front/tower right"], "near": [[-41.8, -9.075], [-41.8, 9.075]], "style": "baroque", "leaves": 2},
             {"_about": "the gateway between the bastions", "part": "gate building", "near": [[209.0, -7.5]], "style": "baroque", "leafH": 5.6},
             {"_about": "the gate passage into the Praelatenhof", "part": "praelatenhof east wing", "near": [[161.8, 0.0]], "style": "baroque", "leafH": 4.8},
             {"_about": "the Kaiserstiege's door", "part": "praelatenhof west wing", "near": [[63.1, 12.0]], "style": "baroque", "leafH": 4.4},
             {"_about": "the Kaisertrakt's doors on the court", "part": "kaisertrakt", "near": [[2.0, 19.0], [26.0, 19.0], [81.0, 19.0], [129.0, 19.0]], "style": "baroque", "below": 5.0},
             {"_about": "the arms' doors on the Kolomanihof", "part": ["library wing", "marble wing"], "near": [list(map(r3, FL(33.0, 0))), list(map(r3, FM(31.0, DM)))], "style": "baroque", "below": 5.0},
         ]}
open(os.path.join(ROOT, "assets/doors/melk.json"), "w").write(json.dumps(DOORS, indent=2) + "\n")
print(len(parts), "parts")
