#!/usr/bin/env python3
"""THE BELVEDERE, VIENNA (2026-11-04): Prince Eugene of Savoy's summer palace by Johann Lukas von Hildebrandt -- the UPPER
BELVEDERE (1717-23) over its garden, the Ehrenhof and its pool to the south -- as an arch-engine definition
(assets/architecture/belvedere.json), its finish and its doors.

THE PLAN is OpenStreetMap's (way 5887599 the palace; building:parts 807860307 the Marmorsaal's chamfered block, 807860302
and 807860311 the link and the south entrance projection, 807860309/310 the three-storey blocks, 807860305/306 the
two-storey wings, 807860298-301 the octagonal corner pavilions, 807860303/304 the low links between them; way 5887597 the
pool; the garden's ways round the parterre and the cascade 98116794), turned so the palace's long axis (8.2 degrees off
east) is x, z SOUTH toward the pool (the garden north, -z), the centre line x 0, y 0 the forecourt's and the parterre's
ground. Its blocks step down from the middle, each under ITS OWN curved copper roof -- the tent silhouette:
  the CENTRE: the Marmorsaal's block, a chamfered octagon standing forward into the garden, three storeys of windows (the
    Sala Terrena's doors, the hall's tall arched windows and its oculi), under the tallest roof, a bell-curved tent;
  the SOUTH PROJECTION before it on the Ehrenhof: the three glazed arches of the carriage entrance up a flight between two
    curved ramps, oval windows over them, the BROKEN CURVED PEDIMENT with the Savoy cartouche on top;
  the THREE-STOREY BLOCKS either side (ground storey, bel etage, top storey with its pilasters), each under a curved tent roof;
  the TWO-STOREY WINGS, lower, under low curved roofs;
  the OCTAGONAL CORNER PAVILIONS, four, two storeys and an attic under their copper bell domes with a lantern finial; the
    low LINKS between each pair, their roofs terraces at the bel etage;
  balustrades with statues and urns along every roofline; pale stucco with white trim, the ground storey banded.
INSIDE (walkable): the SALA TERRENA under the Marmorsaal, its groin vaults carried on four ATLAS figures; the PRUNKSTIEGE
in the south projection -- from the vestibule a flight DOWN to the Sala Terrena's level and two flights UP along the side
walls, turning at the corners to meet before the Marmorsaal's door; the MARMORSAAL through two storeys, red-brown marble
pilasters, Carlone's painted ceiling, three chandeliers; the state rooms of the bel etage in enfilade either side of it
(furnished), the wings' rooms, the corner pavilions' cabinets and the CHAPEL in the south-east pavilion; the top storeys of
the three-storey blocks up a spiral stair in each.
THE GARDEN: the TERRACE along the garden front, its flights down to the UPPER PARTERRE -- gravel, lawn panels edged in box
with clipped yew cones, the side allees between tall hedges, the two round fountains -- the SPHINXES on the stair cheeks and
at the cascade, the UPPER CASCADE falling in five steps into the sunken lower basin's court, its balustraded rim the garden's
end and its lookout. The forecourt: the curved ramps and the horse groups at their feet, the gravel and lawns round the
POOL (real water: site.moat).
SOURCED: OSM (the footprint, the parts' heights: 25 m the centre and the three-storey blocks with their roofs, 19 the
projection, 16 the wings, 19 + 5 the pavilions' domes); de.wikipedia "Schloss Belvedere" and en.wikipedia "Belvedere,
Vienna" (Hildebrandt, 1717-23; the Sala Terrena's four Atlantes; the Prunkstiege down to the Sala Terrena and up to the
Marmorsaal; Carlone's ceiling with Chiarini's quadratura, the red Adnet marble; the chapel with Solimena's altarpiece; the
garden's cascades and sphinxes; the Upper Belvedere about 23 m over the Lower); Wikimedia Commons photographs (the garden
front from the north, the south front with the pool, the bird's-eye view from the south-east, the Sala Terrena, the
Marmorsaal, the cascade, the sphinxes). ESTIMATED: the storey heights (ground 6.0 over a 0.9 m platform, bel etage 7.6, top
5.4; the Marmorsaal 15 m inside), the roofs' curves, the rooms' partitions. COMPRESSED to keep the site about 250 m: the
parterre (about 90 m instead of 160), the pool (62 m instead of 112), the slope to the Lower Belvedere (the cascade court
is 3.6 m deep; the Lower Belvedere is left out).

    python3 tools/archgen/belvedere.py   (writes assets/architecture/belvedere.json, assets/finishes/belvedere.json,
                                          assets/doors/belvedere.json; the sphinxes are components/sphinx -- sphinx.py)
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from neoclassical import Balusters
from statuary import statue, pedestal, capped, FACE_PX, FACE_NX, FACE_PZ, FACE_NZ
ROOT = os.path.dirname(os.path.dirname(HERE))
parts, build, late = {}, [], []
Q, PI = math.pi / 2, math.pi
r3 = lambda v: round(v, 3)
SEMI, FLAT = {"profile": "semicircular"}, {"profile": "flat"}
comp = lambda use, params, at, **kw: {"type": "component", "use": "components/" + use, "params": params, "at": at, **kw}


def add(n, d, last=False):
    assert n not in parts, n
    parts[n] = d
    (late if last else build).append(n)
    return n


def area(p):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(p, p[1:] + p[:1])) / 2


def inset(pts, d):
    """the outline moved in by d on every side, mitred (melk.py's, for this winding)"""
    n, out = len(pts), []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        e0 = (p1[0] - p0[0], p1[1] - p0[1]); e1 = (p2[0] - p1[0], p2[1] - p1[1])
        l0, l1 = math.hypot(*e0), math.hypot(*e1)
        n0, n1 = (e0[1] / l0, -e0[0] / l0), (e1[1] / l1, -e1[0] / l1)
        k = d / (1 + n0[0] * n1[0] + n0[1] * n1[1])
        out.append([r3(p1[0] + (n0[0] + n1[0]) * k), r3(p1[1] + (n0[1] + n1[1]) * k)])
    return out


def rect_pts(x0, x1, z0, z1):   # (faces 0 south (+z), 1 east, 2 north, 3 west)
    return [[x0, z1], [x1, z1], [x1, z0], [x0, z0]]


def octagon(x0, x1, z0, z1, c):
    return [[x0 + c, z1], [x1 - c, z1], [x1, z1 - c], [x1, z0 + c], [x1 - c, z0], [x0 + c, z0], [x0, z0 + c], [x0, z1 - c]]


def mirror(pts):
    """the outline mirrored across x 0, kept turning the same way, starting again at its south-west corner"""
    m = [[-x, z] for x, z in pts][::-1]
    k = min(range(len(m)), key=lambda i: (-m[i][1], m[i][0]))       # (the south-west-most corner)
    return m[k:] + m[:k]


# ================================================================ THE STOREYS, THE WINDOWS
T, SLAB, BAY = 1.0, 0.3, 4.1
FG, FV, FB, L2 = 0.9, 1.8, 6.9, 14.5         # the ground floor (on the platform), the vestibule, the bel etage, the top storey
S3 = [6.9, 7.6, 5.4]                         # the three-storey blocks: to 19.9
S2 = [6.9, 7.6]                              # the wings: to 14.5
SPV = [6.9, 7.6, 1.5]                        # the corner pavilions: the attic under the dome, to 16.0
SC = [6.9, 9.6, 6.0]                         # the centre: the Sala Terrena, the Marmorsaal's two tiers of windows, to 22.5
SSP = [9.3, 5.3]                             # the south projection: the arches, the oval windows, to 14.6
SLK = [6.9]                                  # the links
win = lambda sill, w, h, head=FLAT, sur=None: (sill, w, h, head, sur)
G_GARDEN = win(1.9, 1.5, 3.4, SEMI, {"head": False, "keystone": True})                   # the ground storey to the garden: arched
G_COURT = win(1.9, 1.4, 2.5, FLAT, {"head": "cornice", "sill": True})                    # ...to the court: square, lower
BEL = win(1.0, 1.7, 3.6, FLAT, {"head": "pediment", "pediment": "segmental", "sill": True})   # the bel etage
TOP = win(0.9, 1.4, 2.3, FLAT, {"head": "cornice"})                                     # the top storey
SALA = win(0.8, 2.4, 6.6, SEMI, {"head": False, "keystone": True})                     # the Marmorsaal's tall arched windows
OCUL = ("oculus", 1.9)


def opening(u, w, sill, h, head=FLAT, sur=None, glass=None):
    o = {"at": r3(u), "width": r3(w), "sill": r3(sill), "springing": r3(sill + h - (w / 2 if head is SEMI else 0)), "head": head}
    if sur: o["surround"] = sur
    if glass is not None: o["glass"] = glass
    return o


BLOCKS = {}


def block(name, pts, storeys, wins, orders=None, about=None, plain=(), glass=True, bay=BAY):
    """a block: ONE enclosure on its outline (faces counted round it from its south-west corner), its storeys; `wins`
    (face's outward normal, storey) -> a window or None; doors and party spans are added before it is written"""
    assert area(pts) < 0, f"{name}: outline turned the wrong way"
    BLOCKS[name] = {"pts": [[r3(x), r3(z)] for x, z in pts], "storeys": storeys, "wins": wins, "orders": orders, "about": about,
                    "doors": {}, "party": {}, "plain": set(plain), "glass": glass, "H": sum(storeys), "bay": bay}
    return BLOCKS[name]


def edge(B, i):
    p, q = B["pts"][i], B["pts"][(i + 1) % len(B["pts"])]
    L = math.dist(p, q)
    return p, q, L, ((q[0] - p[0]) / L, (q[1] - p[1]) / L)


def face_of(name, x, z):
    """the face of the block nearest the point"""
    B = BLOCKS[name]
    def d(i):
        p, q, L, e = edge(B, i)
        t = max(0, min(L, (x - p[0]) * e[0] + (z - p[1]) * e[1]))
        return math.hypot(p[0] + e[0] * t - x, p[1] + e[1] * t - z)
    return min(range(len(B["pts"])), key=d)


def u_on(B, i, x, z):
    p, q, L, e = edge(B, i)
    return (x - (p[0] + q[0]) / 2) * e[0] + (z - (p[1] + q[1]) / 2) * e[1]


def doorway(name, x, z, storeys=(0,), w=1.8, h=3.4, head=SEMI, sill=None, glass=False, sur=None):
    B = BLOCKS[name]
    i = face_of(name, x, z)
    for k in storeys:
        s = (FG if k == 0 else 0.0) if sill is None else sill
        hh = min(h, B["storeys"][k] - s - 0.6) if k < len(B["storeys"]) - 1 else h
        B["doors"].setdefault(i, []).append((u_on(B, i, x, z), k, w, hh, head, s, glass) + ((sur,) if sur else ()))


PARTY = []


def party(a, b, p0, p1, doors=(), storeys=(0, 1, 2), w=2.0, h=4.0, head=SEMI):
    """two blocks face to face along p0-p1 (each its own wall): no windows there on the storeys they share, the courses
    stopped as high as the lower one; a doorway through both walls at each of `doors` on each of `storeys`"""
    ha = min(BLOCKS[a]["H"], BLOCKS[b]["H"])
    for nm in (a, b):
        B = BLOCKS[nm]
        i = face_of(nm, (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        u0, u1 = sorted((u_on(B, i, *p0), u_on(B, i, *p1)))
        ks = {k for k in range(len(B["storeys"])) if sum(B["storeys"][:k]) < ha - 0.5}
        B["party"].setdefault(i, []).append((u0, u1, ks, ha))
        for d in doors:
            doorway(nm, d[0], d[1], [k for k in storeys if k < len(B["storeys"])], w, h, head)
    PARTY.append((a, b, p0, p1, ha))


def face_tiers(B, i):
    p, q, L, e = edge(B, i)
    nrm = (-e[1], e[0])                                          # (outward)
    storeys, bay = B.get("ftiers", {}).get(i, B["storeys"]), B["bay"]
    nb = max(1, round(L / bay))
    us = [-L / 2 + L / nb * (j + 0.5) for j in range(nb)]
    doors = B["doors"].get(i, [])
    skips = B["party"].get(i, [])
    tiers = []
    for k, sh in enumerate(storeys):
        ops = [opening(u, w, s, h, hd, (d[7:] or [None])[0], glass=gl) for d in doors for (u, dk, w, h, hd, s, gl) in [d[:7]] if dk == k] + B.get("extra", {}).get((i, k), [])
        wk = None if i in B["plain"] or (i, k) in B.get("blind", ()) else B["wins"](nrm, k)
        if wk:
            for u in us:
                if any(a - 1.4 < u < b + 1.4 for a, b, ks, _ in skips if k in ks): continue
                if any(abs(d[0] - u) < (d[2] + 1.7) / 2 + 0.4 for d in doors if d[1] == k): continue
                if u < -L / 2 + 1.1 or u > L / 2 - 1.1: continue
                if wk[0] == "oculus":
                    d = wk[1]; s0 = sh / 2 - 0.1
                    ops.append({"at": r3(u), "width": d, "sill": r3(s0), "springing": r3(s0), "head": SEMI, "foot": SEMI, "surround": {"head": False}})
                else:
                    sill, w, h, head, sur = wk
                    ops.append(opening(u, w, sill, h, head, sur))
        tiers.append({"h": sh, "openings": ops} if k < len(storeys) - 1 else {"openings": ops})
    return tiers


def write_blocks():
    for name, B in BLOCKS.items():
        pts, faces, clear = B["pts"], {}, {}
        for i in range(len(pts)):
            p, q, L, e = edge(B, i)
            faces[str(i)] = face_tiers(B, i)
            sk = B["party"].get(i, [])
            if sk: clear[str(i)] = [[r3(L / 2 + a), r3(L / 2 + b), -1, r3(ha + 0.05)] for a, b, ks, ha in sk]
        d = {"type": "enclosure", "plan": {"points": pts}, "thickness": T, "height": r3(B["H"]), "glass": B["glass"], "interior": True,
             "faces": faces, "courses": {"clear": clear} if clear else True, "at": [[0, 0, 0, 0]]}
        if B["orders"]: d["orders"] = B["orders"]
        if B["about"]: d["_about"] = B["about"]
        add(name, d)
    for k, (a, b, p0, p1, ha) in enumerate(PARTY):   # (the strip from one wall's middle to the other's is the rooms')
        L = math.dist(p0, p1); ex, ez = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
        nx, nz = -ez, ex
        pts = [[r3(p0[0] + nx * T), r3(p0[1] + nz * T)], [r3(p1[0] + nx * T), r3(p1[1] + nz * T)],
               [r3(p1[0] - nx * T), r3(p1[1] - nz * T)], [r3(p0[0] - nx * T), r3(p0[1] - nz * T)]]
        if area(pts) > 0: pts = pts[::-1]
        add(f"party interior {k + 1}", {"type": "interior", "plan": {"points": pts}, "height": r3(ha), "at": [[0, 0, 0, 0]],
                                        **({"_about": "where two blocks stand face to face: the strip between their walls is the rooms' (the doorways' reveals inside)"} if k == 0 else {})})


def wins_std(court_ground=G_COURT, top=TOP):
    def f(n, k):
        if k == 0: return G_GARDEN if n[1] < -0.5 else court_ground
        if k == 1: return BEL
        if k == 2: return top
    return f


# ================================================================ THE PLAN (OSM, in the palace's frame)
CPTS = [[-8.2, 1.55], [8.2, 1.55], [11.15, -3.6], [11.15, -9.9], [8.1, -15.45], [-8.1, -15.45], [-11.15, -9.9], [-11.15, -3.6]]
FPTS = [[8.2, 12.53], [33.1, 12.53], [33.1, -9.9], [11.15, -9.9], [11.15, -3.6], [8.2, 1.55]]
CEN = block("centre block", CPTS, SC, lambda n, k: [G_GARDEN, SALA, OCUL][k] if n[1] < -0.3 else None,
            orders=[{"tier": 1, "kind": "corinthian", "span": 1}], bay=5.4,
            about="THE CENTRE: the Marmorsaal's block, a chamfered octagon standing forward into the garden (OSM 807860307) -- the Sala Terrena's three doors to the garden, the Marmorsaal's tall arched windows and its oculi over them through two storeys")
SP = block("south projection", rect_pts(-8.2, 8.2, 1.55, 18.44), SSP, lambda n, k: None, orders=[{"tier": 0, "kind": "ionic", "span": 1}],
           about="THE SOUTH PROJECTION on the Ehrenhof (OSM 807860302, 807860311): the carriage entrance's three glazed arches up their flight, the oval windows over them, the broken curved pediment on top; inside the vestibule and the Prunkstiege")
BLOCKS["south projection"]["plain"] = set()
for sx, side in ((1, "east"), (-1, "west")):
    M = (lambda p: p) if sx > 0 else mirror
    m = (lambda x: x) if sx > 0 else (lambda x: -x)
    block(f"{side} block", M(FPTS), S3, wins_std(),
          orders=[{"tier": 1, "kind": "ionic", "span": 1}, {"tier": 2, "kind": "corinthian", "span": 1}],
          about=f"the {side} three-storey block (OSM {'807860310' if sx > 0 else '807860309'}): the ground storey banded, the bel etage's pedimented windows between Ionic pilasters, the top storey's between Corinthian ones (Hildebrandt's herm pilasters)")
    block(f"{side} wing", M(rect_pts(33.1, 49.85, -8.56, 12.5)), S2, wins_std(),
          orders=[{"tier": 1, "kind": "ionic", "span": 1}],
          about=f"the {side} two-storey wing (OSM {'807860305' if sx > 0 else '807860306'})")
    for ns, z0, z1 in (("north", -14.0, -4.4), ("south", 8.4, 18.0)):
        pts = octagon(49.85, 60.9, z0, z1, 2.2) if sx > 0 else octagon(-60.9, -49.85, z0, z1, 2.2)
        block(f"{ns}-{side} pavilion", pts, SPV, lambda n, k: [G_GARDEN if n[1] < 0.5 else G_COURT, BEL, OCUL][k] if k < 2 else ("oculus", 1.0),
              orders=[{"tier": 1, "kind": "ionic", "span": 1}], bay=3.6,
              about=f"the {ns}-{side} corner pavilion: an octagon of two storeys and an attic under its copper bell dome")
    block(f"{side} link", M(rect_pts(49.85, 58.2, -4.4, 8.4)), SLK, lambda n, k: G_GARDEN if abs(n[0]) > 0.5 else None, bay=4.3,
          about=f"the {side} link between the corner pavilions: one storey, its roof a balustraded terrace at the bel etage")

BLOCKS["south-east pavilion"]["blind"] = {(face_of("south-east pavilion", 60.9, 13.2), 1)}     # (the chapel's altar wall)

# ---- where they meet: party walls, the doorways through them
party("centre block", "south projection", (-8.2, 1.55), (8.2, 1.55), doors=[], storeys=())
doorway("centre block", 0, 1.55, (0,), 2.8, 4.2)                       # (from the Prunkstiege's lower hall into the Sala Terrena)
doorway("centre block", 0, 1.55, (1,), 2.4, 4.6, sill=0.0)             # (from its landing into the Marmorsaal)
SPN = face_of("south projection", 0, 1.55)                             # (the projection's back wall: tiers at the bel etage)
BLOCKS["south projection"]["ftiers"] = {SPN: [FB, 14.6 - FB]}
BLOCKS["south projection"]["doors"].setdefault(SPN, []).extend([(0.0, 0, 2.8, 4.2, SEMI, FG, False), (0.0, 1, 2.4, 4.6, SEMI, 0.0, False)])
for sx, side in ((1, "east"), (-1, "west")):
    X = lambda x: sx * x
    B, W = f"{side} block", f"{side} wing"
    party("centre block", B, (X(11.15), -3.6), (X(11.15), -9.9), doors=[(X(11.15), -6.75)], storeys=(0, 1), w=2.0, h=4.2)
    party("centre block", B, (X(8.2), 1.55), (X(11.15), -3.6))
    party("south projection", B, (X(8.2), 1.55), (X(8.2), 12.53))
    party(B, W, (X(33.1), -8.56), (X(33.1), 12.5), doors=[(X(33.1), -3.6)], storeys=(0, 1), w=2.0, h=4.0)
    party(W, f"{side} link", (X(49.85), -4.4), (X(49.85), 8.4), doors=[(X(49.85), 2.0)], storeys=(0,), w=1.8, h=3.6)
    party(W, f"north-{side} pavilion", (X(49.85), -8.56), (X(49.85), -6.6))
    party(W, f"south-{side} pavilion", (X(49.85), 10.6), (X(49.85), 12.5))
    party(f"{side} link", f"north-{side} pavilion", (X(52.05), -4.4), (X(58.2), -4.4), doors=[(X(55.1), -4.4)], storeys=(0,), w=1.8, h=3.6)
    party(f"{side} link", f"south-{side} pavilion", (X(52.05), 8.4), (X(58.2), 8.4), doors=[(X(55.1), 8.4)], storeys=(0,), w=1.8, h=3.6)
    # the bel etage's doors out onto the link's terrace, from the wing and into the two pavilions: French doors, the
    # bel etage's windows let down to the floor (the same width, head and segmental pediment)
    for nm, x, z in ((W, X(49.85), 2.0), (f"north-{side} pavilion", X(55.1), -4.4), (f"south-{side} pavilion", X(55.1), 8.4)):
        doorway(nm, x, z, (1,), BEL[1], BEL[0] + BEL[2], FLAT, 0.0, sur={"head": "pediment", "pediment": "segmental"})
    # the doors from outside: the garden terrace, the court, the pavilions' ends
    doorway(B, X(22.1), -9.9, (0,), 2.0, 3.9)
    doorway(B, X(20.6), 12.53, (0,), 1.8, 3.4)
    doorway(W, X(41.5), -8.56, (0,), 2.0, 3.9)
    doorway(f"north-{side} pavilion", X(60.9), -9.2, (0,), 1.8, 3.6)
    doorway(f"south-{side} pavilion", X(60.9), 13.2, (0,), 1.8, 3.6)
    doorway(f"{side} link", X(58.2), 2.0, (0,), 2.0, 3.8)
# the garden doors of the Sala Terrena: three arches in the centre's north face
for u in (-5.4, 0.0, 5.4):
    doorway("centre block", u, -15.45, (0,), 2.3, 4.8)
# the south projection's front: the three arches of the carriage entrance (the middle one the door) and the oval windows
SPF = face_of("south projection", 0, 18.44)
BLOCKS["south projection"]["doors"].setdefault(SPF, []).extend(
    [(u, 0, 3.4, 7.0, SEMI, FV, None if u else False) for u in (-4.6, 0.0, 4.6)])
BLOCKS["south projection"]["extra"] = {(SPF, 1): [{"at": r3(u), "width": 1.7, "sill": 2.6, "springing": 2.6, "head": SEMI, "foot": SEMI, "surround": {"head": False}} for u in (-4.6, 0.0, 4.6)]}
for xs in (1, -1):
    i = face_of("south projection", xs * 8.2, 15.5)
    BLOCKS["south projection"]["doors"].setdefault(i, []).append((u_on(BLOCKS["south projection"], i, xs * 8.2, 15.6), 0, 1.6, 4.4, SEMI, 3.0, True))

# ================================================================ THE PLATFORM, THE TERRACE, THE FLOORS
# the palace stands on a platform 0.9 m high (its ground floor), reaching out 0.5 m round its walls and north as the
# GARDEN TERRACE along the whole garden front to z -24
PLAT_E = [(0, -24.0), (61.4, -24.0), (61.4, -6.4), (59.0, -4.0), (58.7, -4.0), (58.7, 8.0), (59.0, 8.0), (61.4, 10.4), (61.4, 16.0),
          (58.9, 18.5), (51.85, 18.5), (49.35, 16.0), (49.35, 13.0), (8.7, 13.0), (8.7, 18.94), (0, 18.94)]
PLAT = [(x, z) for x, z in PLAT_E[1:-1]] + [(-x, z) for x, z in PLAT_E[-1:0:-1]][:-1]
PLAT = [[r3(x), r3(z)] for x, z in [PLAT_E[0]] + PLAT_E[1:] + [(-x, z) for x, z in PLAT_E[-2:0:-1]]]
add("platform", {"type": "prism", "plan": {"points": PLAT}, "height": FG, "courses": True, "railing": False, "at": [[0, 0, 0, 0]],
                 "_about": "the palace's platform, 0.9 m: its ground floor everywhere inside, and the GARDEN TERRACE along the garden front"})
# the floors: the bel etage's in every block but the projection, the top storey's in the three-storey blocks (a spiral
# stair's well in each), the ceilings under the roofs (their tops the roofs' decks); the Sala Terrena's ceiling the
# Marmorsaal's floor
SPIRAL = {}
for sx, side in ((1, "east"), (-1, "west")):
    SPIRAL[side] = (sx * 29.3, 8.6)


def slab_of(name, y, well=None, about=None, nm=None):
    pl = {"points": inset(BLOCKS[name]["pts"], T - 0.02)}
    if well: pl["well"] = {"radius": 2.0, "sides": 20, "at": [r3(well[0]), r3(well[1])]}
    d = {"type": "prism", "plan": pl, "height": SLAB, "railing": False, "at": [[0, r3(y - SLAB), 0, 0]]}
    if about: d["_about"] = about
    return add(nm or f"{name} floor {y}", d)


slab_of("centre block", FB, about="the Marmorsaal's floor over the Sala Terrena's vaults", nm="marmorsaal floor")
slab_of("centre block", 22.5, about="the Marmorsaal's ceiling (Carlone's fresco), its top the deck under the roof", nm="marmorsaal ceiling")
slab_of("south projection", 14.6, about="the vestibule's and the stair hall's ceiling", nm="stair hall ceiling")
for side in ("east", "west"):
    slab_of(f"{side} block", FB, nm=f"{side} block bel etage floor", about="the bel etage's floor" if side == "east" else None)
    slab_of(f"{side} block", L2, well=SPIRAL[side], nm=f"{side} block top floor", about="the top storey's floor, the spiral's well in it" if side == "east" else None)
    slab_of(f"{side} block", 19.9, nm=f"{side} block ceiling")
    slab_of(f"{side} wing", FB, nm=f"{side} wing bel etage floor")
    slab_of(f"{side} wing", 14.5, nm=f"{side} wing ceiling")
    slab_of(f"{side} link", FB, nm=f"{side} link terrace", about="the link's roof: the terrace at the bel etage between the pavilions" if side == "east" else None)
    for ns in ("north", "south"):
        slab_of(f"{ns}-{side} pavilion", FB, nm=f"{ns}-{side} pavilion floor")
        slab_of(f"{ns}-{side} pavilion", 16.0, nm=f"{ns}-{side} pavilion ceiling")

# ================================================================ INNER WALLS AND THE ROOMS
def iwall(name, a, b, doors, levels, y0=0.0, t=0.35, dw=1.6, dh=3.6, about=None):
    """an inner wall from a to b (x, z), centred on that line, through the storeys `levels` [(foot, height), ...] with a
    doorway at each distance from a in doors[k]"""
    L = math.dist(a, b); dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    tiers = []
    for k, (f, sh) in enumerate(levels):
        dd = doors[k] if k < len(doors) else []
        ops = [opening(d - L / 2, dw, f, min(dh, sh - 0.8), FLAT, glass=False) for d in dd]
        tiers.append({"h": r3(sh + (f if k == 0 else 0)), "openings": ops} if k < len(levels) - 1 else {"openings": ops})
    H = sum(sh for _, sh in levels) + levels[0][0]
    mx, mz = (a[0] + b[0]) / 2 - t / 2 * dz, (a[1] + b[1]) / 2 + t / 2 * dx
    d = {"type": "wall", "width": r3(L), "height": r3(H - y0), "thickness": t, "tiers": tiers, "glass": False,
         "at": [[r3(mx), y0, r3(mz), r3(math.atan2(-dz, dx))]]}
    if about: d["_about"] = about
    return add(name, d)


LV3 = [(0.0, 6.9), (0.0, 7.6), (0.0, 5.4)]      # (the first tier from the wall's foot: the platform's top is its floor)
LV2W = [(0.0, 6.9), (0.0, 7.6)]
for sx, side in ((1, "east"), (-1, "west")):
    X = lambda x: sx * x
    # the three-storey block: a spine wall along it (the garden rooms and the court rooms), a cross wall in the garden row
    a, b = (X(9.0), 1.3), (X(33.6), 1.3)
    iwall(f"{side} block spine", a, b, [[abs(X(17.0) - a[0]), abs(X(27.0) - a[0])]] * 3, [(FG, 6.0), (0.0, 7.6), (0.0, 5.4)],
          about="the spine wall: the garden rooms and the court rooms, a door between them on every storey" if side == "east" else None)
    a, b = (X(22.4), -10.4), (X(22.4), 1.3)
    iwall(f"{side} block cross wall", a, b, [[5.6]] * 3, [(FG, 6.0), (0.0, 7.6), (0.0, 5.4)],
          about="the cross wall between the two garden rooms, their doors in enfilade" if side == "east" else None)
    a, b = (X(33.6), 2.2), (X(50.35), 2.2)
    iwall(f"{side} wing spine", a, b, [[abs(X(38.0) - a[0]), abs(X(46.0) - a[0])]] * 2, [(FG, 6.0), (0.0, 7.6)])

# ================================================================ THE PRUNKSTIEGE (the south projection)
# from the vestibule at FV a flight DOWN north to the lower hall (the Sala Terrena's level) and two flights UP along the
# side walls, landing in the corners and turning in along the north wall to meet before the Marmorsaal's door at FB
ZV = 12.0                                    # the vestibule's edge over the stair hall
add("vestibule floor", {"type": "box", "width": 14.6, "length": r3(17.6 - ZV), "height": r3(FV - FG), "at": [[0, FG, r3((17.6 + ZV) / 2), 0]],
                        "_about": "the VESTIBULE behind the three arches, up the flight from the Ehrenhof"})
NDOWN = 5
add("prunkstiege down", {"type": "flight", "run": 0.32, "width": 4.0, "base": FG, "top": FV, "steps": NDOWN, "landing": 0,
                         "at": [[-2.0, 0, r3(ZV - NDOWN * 0.32), -Q]],
                         "_about": "the Prunkstiege's middle flight DOWN from the vestibule to the lower hall and the Sala Terrena's door"}, last=True)
N1, N2 = 25, 13
R1 = (FB - FV) / (N1 + N2)
RUN1 = (ZV - 2.55 - 2.0) / N1
for sx, side in ((1, "east"), (-1, "west")):
    xo = sx * 7.2
    # the first flight north along the side wall: its foot's corner on the wall at the vestibule's edge, its own landing
    # the corner's
    if sx > 0: at1 = [xo, 0, ZV, Q]                           # (rising -z: its width from x - w to x)
    else: at1 = [xo + 2.0, 0, ZV, Q]
    add(f"prunkstiege {side} flight", {"type": "flight", "run": r3(RUN1), "width": 2.0, "base": FV, "top": r3(FV + N1 * R1), "steps": N1, "landing": 2.0,
                                       "ground": FG, "at": [[r3(at1[0]), FV if False else 0, r3(at1[2]), at1[3]]],
                                       **({"_about": "the Prunkstiege's flights UP along the side walls to the corner landings..."} if sx > 0 else {})}, last=True)
    # the second flight in along the north wall to the middle landing before the Marmorsaal's door
    y1 = FV + N1 * R1
    if sx > 0: at2 = [5.2, 0, 2.55, PI]                       # (rising -x: its width from z to z + w)
    else: at2 = [-5.2, 0, 4.55, 0.0]                          # (rising +x: its width from z - w to z)
    add(f"prunkstiege {side} upper flight", {"type": "flight", "run": r3((5.2 - 0.0) / (N2 + 4.6)), "width": 2.0, "base": r3(y1), "top": FB, "steps": N2,
                                             "landing": r3(5.2 - N2 * (5.2 / (N2 + 4.6))), "soffit": 0.35, "at": [[r3(at2[0]), 0, r3(at2[2]), at2[3]]],
                                             **({"_about": "...and in along the north wall, meeting on the landing before the Marmorsaal's door"} if sx > 0 else {})}, last=True)

# ================================================================ THE SALA TERRENA: the groin vaults on four Atlantes
VX, VZ, VC = 3.4, 3.3, -6.95                 # the middle bay's half-width, half-depth, its middle
SPR, VT = 4.5, FB - SLAB - 0.02
xs_ = [-10.15, -VX, VX, 10.15]; zs_ = [-14.45, VC - VZ, VC + VZ, 0.55]
vb = []
for i in range(3):
    for j in range(3):
        w, l = xs_[i + 1] - xs_[i], zs_[j + 1] - zs_[j]
        vb.append((r3((xs_[i] + xs_[i + 1]) / 2), r3((zs_[j] + zs_[j + 1]) / 2), r3(w), r3(l)))
for k, (x, z, w, l) in enumerate(vb):
    rx, rz = min(1.9, w / 2 - 0.05), min(1.9, l / 2 - 0.05)
    add(f"sala terrena vault {k + 1}", {"type": "groin", "width": w, "length": l, "springing": SPR, "top": r3(VT),
                                        "across": {"profile": "segmental", "rise": r3(rx)}, "along": {"profile": "segmental", "rise": r3(rz)},
                                        "at": [[x, 0, z, 0]], **({"_about": "the SALA TERRENA's groin vaults, nine bays, the middle one carried on the four Atlantes"} if k == 0 else {})})
ATL = [(sx * VX, VC + sz * VZ) for sx in (1, -1) for sz in (1, -1)]
# the four ATLANTES: bearded giants carved bare, each on his own pedestal, bowed under the vault -- the impost block on
# his nape and shoulders, his hands up at it -- the four middle bays' groins springing from those blocks. No pier: the
# figure is the support (as in Hildebrandt's hall), so nothing stands before him from any side
APED, AIMP, ASC = 1.05, 3.8, 1.42             # the pedestal's height; the impost's foot (its top the springing); the figure's scale
AFWD = -0.32                                 # the block BEHIND his feet's middle: on his shoulders and nape, his head bowed before it
ATB = [(x - AFWD * x / math.hypot(x, VC - z), z + AFWD * (VC - z) / math.hypot(x, VC - z)) for x, z in ATL]
add("atlas pedestals", {"type": "box", "width": 1.25, "length": 1.25, "height": APED, "at": [[r3(x), FG, r3(z), 0] for x, z in ATL],
                        "_about": "the Atlantes' pedestals"})
add("atlas pedestal caps", {"type": "box", "width": 1.45, "length": 1.45, "height": 0.14, "at": [[r3(x), r3(FG + APED - 0.14), r3(z), 0] for x, z in ATL]})
add("atlas pedestal bases", {"type": "box", "width": 1.45, "length": 1.45, "height": 0.16, "at": [[r3(x), FG, r3(z), 0] for x, z in ATL]})
add("atlas imposts", {"type": "box", "width": 0.85, "length": 0.85, "height": r3(SPR - 0.2 - AIMP), "at": [[r3(x), AIMP, r3(z), 0] for x, z in ATB],
                      "_about": "the impost blocks the Atlantes carry on their napes, shoulders and hands, the vaults springing from them"})
add("atlas abaci", {"type": "box", "width": 1.45, "length": 1.45, "height": 0.2, "at": [[r3(x), r3(SPR - 0.2), r3(z), 0] for x, z in ATB]})
stat = {}
for k, (x, z) in enumerate(ATL):
    face = math.atan2(-(VC - z), -x)                          # (each turned to the middle bay's centre, on its diagonal)
    stat[f"atlas {k + 1}"] = statue((x, r3(FG + APED), z), kind="man", pose="atlas", style="greek", stone="limestone", scale=ASC, seed=11 + k, face=face,
                                    outfit={"beard": "full", "hair": "short"}, wear=["loincloth"])

# ================================================================ THE MARMORSAAL: its pilasters, chandeliers
MP = []
for x in (-7.4, -2.7, 2.7, 7.4):
    MP.append((x, -14.3, 0.0))               # (the north wall, between its windows)
for x in (-7.4, -2.7, 2.7, 7.4):
    MP.append((x, 0.4, PI))                  # (the south wall, either side of the door)
for z in (-4.6, -8.9):
    MP += [(10.0, z, Q), (-10.0, z, -Q)]
add("marmorsaal pilasters", {"type": "box", "width": 1.0, "length": 0.32, "height": r3(21.0 - FB), "at": [[r3(x), FB, r3(z), r3(y)] for x, z, y in MP],
                             "_about": "the Marmorsaal's pilasters of red-brown Adnet marble through both its storeys"})
add("marmorsaal capitals", {"type": "box", "width": 1.25, "length": 0.5, "height": 0.6, "at": [[r3(x), 21.0, r3(z), r3(y)] for x, z, y in MP]})
add("marmorsaal cornice", {"type": "bars", "w": 0.7, "h": 0.5, "closed": True, "kind": "moulding",
                           "paths": [[[x, 21.85, z] for x, z in inset(CPTS, T + 0.3)]], "_about": "the cornice round the hall under the painted ceiling"})
add("marmorsaal gallery band", {"type": "bars", "w": 0.4, "h": 0.35, "closed": True, "kind": "moulding",
                                "paths": [[[x, 16.6, z] for x, z in inset(CPTS, T + 0.15)]], "_about": "the band between the hall's two storeys of windows"})
add("marmorsaal chandeliers", {"type": "item", "item": "items/furniture/chandelier", "solid": False,
                               "at": [[0.0, 19.4, -6.95, 0], [-5.6, 19.4, -6.95, 0], [5.6, 19.4, -6.95, 0], [0.0, 12.3, 8.0, 0]], "_about": "the hall's three chandeliers (and the stair hall's)"})

# ================================================================ THE CHAPEL (the south-east pavilion's bel etage)
CHX, CHZ = 55.375, 13.2
add("chapel altar", {"type": "box", "width": 0.9, "length": 2.6, "height": 1.05, "at": [[59.2, FB, CHZ, 0]], "_about": "the chapel's altar against the east wall"})
add("chapel retable", {"type": "box", "width": 0.45, "length": 3.4, "height": 5.6, "at": [[59.65, r3(FB + 1.05), CHZ, 0]],
                       "_about": "the retable round Solimena's altarpiece (the Resurrection)"})
add("chapel retable columns", {"type": "column", "radius": 0.2, "height": 5.0, "sides": 12, "at": [[59.25, r3(FB + 1.05), r3(CHZ + s), 0] for s in (-1.9, 1.9)]})
add("chapel pews", {"type": "item", "item": "items/furniture/bench", "at": [[r3(x), FB, r3(CHZ + s * 1.4), Q] for x in (52.6, 54.0, 55.4) for s in (-1, 1)],
                    "_about": "the chapel's benches"})
add("chapel cupola", {"type": "dome", "radius": 3.6, "sides": 16, "thickness": 0.25, "oculus": 0.8, "head": {"profile": "segmental", "rise": 1.6},
                      "at": [[CHX, 14.0, CHZ, 0]], "_about": "the chapel's shallow painted cupola under the pavilion's dome (Carlone's fresco)"})
add("chapel cupola ring", {"type": "prism", "plan": {"points": inset(BLOCKS["south-east pavilion"]["pts"], T - 0.02), "well": {"radius": 3.6, "sides": 16, "at": [CHX, CHZ]}},
                           "height": 0.3, "railing": False, "at": [[0, 13.7, 0, 0]],
                           "_about": "the ring the cupola springs from"})

# ================================================================ FURNITURE, PAINTINGS (the state rooms)
items = {}
def item(kind, places):
    items.setdefault(kind, []).extend([[r3(a) for a in p] for p in places])
paintings, mirrors = [], []
for sx, side in ((1, "east"), (-1, "west")):
    X = lambda x: sx * x
    Y = FB
    # the garden rooms of the bel etage, in enfilade from the Marmorsaal: an audience room, a conference room
    item("chandelier", [(X(17.0), Y + 5.5, -4.3, 0), (X(27.6), Y + 5.5, -4.3, 0), (X(21.0), Y + 5.5, 6.5, 0), (X(41.5), Y + 5.5, -3.0, 0), (X(41.5), Y + 5.5, 7.5, 0)])
    item("console-table", [(X(17.0), Y, -8.55, 0), (X(27.6), Y, -8.55, 0)])
    item("wall-mirror", [(X(17.0), Y + 1.0, -8.75, 0), (X(27.6), Y + 1.0, -8.75, 0)])
    item("fauteuil", [(X(15.5), Y, -3.0, Q * sx), (X(18.5), Y, -3.0, -Q * sx), (X(26.0), Y, -1.5, 0), (X(29.0), Y, -1.5, 0)])
    item("sofa", [(X(17.0), Y, 0.3, PI)])
    item("gate-leg-table", [(X(27.5), Y, -4.0, 0)])
    item("baroque-armchair", [(X(26.2), Y, -4.0, Q), (X(28.8), Y, -4.0, -Q)])
    # the court rooms: a bedchamber (east), a cabinet with the bureau (west)
    if sx > 0:
        item("four-poster", [(X(16.0), Y, 8.8, PI)])
        item("chest-of-drawers", [(X(21.0), Y, 10.9, PI)])
    else:
        item("bureau", [(X(16.0), Y, 10.8, PI)])
        item("longcase-clock", [(X(13.6), Y, 10.9, PI)])
        item("harpsichord", [(X(20.0), Y, 6.0, 0)])
    # the wings: the picture gallery rooms
    item("bench", [(X(41.5), Y, -3.2, 0), (X(41.5), Y, 7.5, 0)])
    for x in (36.2, 40.0, 43.8, 47.4):
        paintings.append(([r3(X(x)), r3(Y + 2.6), -7.52, 0], 2.2, 1.7))
        paintings.append(([r3(X(x)), r3(Y + 2.6), 11.46, PI], 2.0, 1.6))
    for z in (-6.0, 0.0, 6.0):
        if abs(z - 2.2) > 1.5: paintings.append(([r3(X(34.12)), r3(Y + 2.6), z, r3(Q * sx)], 1.8, 1.4))
    # the pavilions' cabinets
    for ns, z in (("north", -9.2), ("south", 13.2)):
        if sx > 0 and ns == "south": continue          # (the chapel)
        item("chandelier", [(X(55.4), Y + 5.6, z, 0)])
        item("console-table", [(X(59.85), Y, z, -Q * sx)])
        item("fauteuil", [(X(54.0), Y, z - 1.0, 0), (X(56.6), Y, z - 1.0, 0)])
    # the Sala Terrena's level: the ground floors' halls (the garden rooms) keep a few benches
    item("bench", [(X(17.0), FG, -6.0, 0), (X(27.6), FG, -6.0, 0)])
# the Marmorsaal's paintings: the battle pieces of the prince's campaigns between its pilasters (the south wall)
for x in (-5.05, 5.05):
    paintings.append(([x, 10.8, 0.6, PI], 2.8, 3.6))
paintings.append(([59.4, r3(FB + 4.1), CHZ, r3(-Q)], 2.0, 3.2))       # (the chapel's altarpiece in its retable)
for k, v in items.items():
    add(f"furniture {k}", {"type": "item", "item": "items/furniture/" + k, "at": v, **({"solid": False} if k == "chandelier" else {})})
add("paintings", {"type": "marker", "role": "painting", "at": [p[0] for p in paintings], "data": {"w": [p[1] for p in paintings], "h": [p[2] for p in paintings]},
                  "_about": "the paintings: the gallery's in the wings, the battle pieces in the Marmorsaal"})

# ================================================================ THE SPIRAL STAIRS (bel etage to the top storey)
for sx, side in ((1, "east"), (-1, "west")):
    x, z = SPIRAL[side]
    add(f"{side} spiral", {"type": "spiral-stair", "radius": 1.85, "newel": 0.3, "turn": 26, "top": r3(L2 - FB), "soffit": 0.25,
                           **({} if sx > 0 else {"hand": "left"}), "at": [[r3(x), FB, z, 0]],
                           **({"_about": "the spiral stairs from the bel etage's court rooms to the top storey"} if sx > 0 else {})}, last=True)

# ================================================================ THE ROOFS: each block its own curved copper tent
def mansard(name, x0, x1, z0, z1, y, along="x", pitch=22, lower=72, brk=3.0, chamfer=0.0, about=None):
    """a mansard over x0..x1 by z0..z1 from the wall top y: the steep swept lower slope all round (its dormers), the low
    hip over it with its ridge `along` x or z -- the Belvedere's copper roofs, each block its own"""
    w, l = (z1 - z0, x1 - x0) if along == "x" else (x1 - x0, z1 - z0)
    d = {"type": "roof", "form": "mansard", "width": r3(w), "length": r3(l), "pitch": pitch, "lowerPitch": lower, "breakH": brk, "overhang": 0,
         "at": [[r3((x0 + x1) / 2), r3(y), r3((z0 + z1) / 2), Q if along == "x" else 0]]}
    if chamfer: d["chamfer"] = chamfer
    if about: d["_about"] = about
    return add(name, d)


RI = 0.9                                     # (the roofs stand in that far from the walls' outer faces, on their tops)
mansard("centre roof", -11.15 + RI, 11.15 - RI, -15.45 + RI, 1.55 - RI, 22.5, pitch=36, lower=72, brk=3.2, chamfer=3.6,
        about="the centre's roof: the tallest, a chamfered mansard over the Marmorsaal's block rising to a short ridge, green copper")
DORM = []
for sx, side in ((1, "east"), (-1, "west")):
    xa, xb = sorted((sx * (11.15 + RI), sx * (33.1 - RI)))
    mansard(f"{side} block roof", xa, xb, -9.9 + RI, 12.53 - RI, 19.9, about="the three-storey blocks' mansard roofs: the steep lower slope with its oval dormers, the low hip over it" if sx > 0 else None)
    xa, xb = sorted((sx * (33.1 + RI), sx * (49.85 - RI)))
    mansard(f"{side} wing roof", xa, xb, -8.56 + RI, 12.5 - RI, 14.5, along="z", pitch=22, brk=2.4, about="the wings' lower roofs" if sx > 0 else None)
    DORM += [[r3(sx * x), 19.9, 11.68, 0] for x in (14.5, 18.6, 22.7, 26.9, 31.0)] + [[r3(sx * x), 19.9, -8.95, PI] for x in (13.6, 17.75, 22.1, 26.5, 30.6)]
    DORM += [[r3(sx * x), 14.5, 11.65, 0] for x in (37.2, 41.5, 45.8)] + [[r3(sx * x), 14.5, -7.61, PI] for x in (37.2, 41.5, 45.8)]
    for ns, zc in (("north", -9.2), ("south", 13.2)):
        add(f"{ns}-{side} dome", comp("baroque-helm", {"sides": 8, "R": 4.45, "footH": 0.5, "profile": "bell", "waist": 0.8, "lift": 0.5, "lanterns": "one",
                                                        "LR": 0.85, "LH": 1.6, "spikeH": 1.5},
                                      [[r3(sx * 55.375), 16.0, zc, 0]],
                                      _about="the corner pavilion's copper bell dome, its little lantern and finial" if (sx > 0 and ns == "north") else None))
add("roof dormers", comp("oculus-dormer", {"W": 1.7, "H": 1.7, "GH": 0.8, "D": 2.6, "t": 0.25, "r": 0.42}, DORM,
                         _about="the oval dormers in the mansards' lower slopes, behind the balustrades"))
# the south projection's roof behind its pediment, ridged back into the centre
add("projection roof", {"type": "roof", "form": "gable", "width": 16.4, "length": 16.89, "pitch": 30, "overhang": 0.4, "at": [[0, 14.6, 9.995, 0]],
                        "_about": "the south projection's roof behind the pediment, its ridge running back into the centre's wall"})
add("chimneys", {"type": "box", "width": 0.9, "length": 1.8, "height": 4.6,
                 "at": [[r3(sx * x), 22.6, r3(z), 0] for sx in (1, -1) for x, z in ((17.0, -2.6), (27.0, 4.2))] +
                       [[r3(sx * 41.5), 16.6, r3(z), 0] for sx in (1, -1) for z in (-1.0, 6.0)],
                 "_about": "the chimney stacks through the roofs"})

# ================================================================ THE PEDIMENTS
def seg_arc(half, y0, rise, n=10):
    R = (half * half + rise * rise) / (2 * rise)
    yc = y0 + rise - R
    return lambda x: yc + math.sqrt(max(0.0, R * R - x * x))


# the south front's BROKEN CURVED PEDIMENT: two segmental halves, the cartouche between them
PH, PY0, PB = 8.8, 14.6, 0.75
arc = seg_arc(PH, PY0 + PB, 5.0)
for sx, side in ((1, "east"), (-1, "west")):
    xs = [1.6 + (PH - 1.6) * k / 9 for k in range(10)]
    out = [(sx * PH, PY0), (sx * PH, PY0 + PB)] + [(sx * x, arc(x)) for x in reversed(xs)] + [(sx * 1.6, PY0)]
    add(f"pediment {side}", {"type": "screen", "outline": [[r3(x), r3(y)] for x, y in out], "t": 1.0, "at": [[0, 0, 18.74, 0]],
                             **({"_about": "THE BROKEN CURVED PEDIMENT over the south front: two segmental halves rising toward the middle, broken for the cartouche"} if sx > 0 else {})})
    add(f"pediment {side} cornice", {"type": "bars", "w": 0.9, "h": 0.5, "kind": "moulding",
                                     "paths": [[[r3(sx * x), r3(arc(x) - 0.1), 18.6] for x in reversed(xs)]] if sx > 0 else [[[r3(sx * x), r3(arc(x) - 0.1), 18.6] for x in xs]]})
add("pediment base cornice", {"type": "box", "width": 18.4, "length": 1.6, "height": 0.6, "at": [[0, PY0, 18.3, 0]], "_about": "the cornice the pediment stands on"})
add("cartouche", {"type": "box", "width": 2.6, "length": 1.2, "height": 1.7, "at": [[0, PY0, 18.3, 0]], "_about": "the cartouche between the pediment's halves, the Savoy arms on it: its scrolled foot..."})
add("cartouche frame", {"type": "loft", "axis": "z", "sides": 20, "smooth": 2,
                        "sections": [{"s": -0.6, "a": 1.55, "b": 2.2}, {"s": 0.1, "a": 1.75, "b": 2.45}, {"s": 0.3, "a": 1.6, "b": 2.3}, {"s": 0.4, "a": 1.3, "b": 1.85}],
                        "at": [[0, r3(PY0 + 3.6), 18.6, 0]], "_about": "...and its scrolled oval frame"})
add("cartouche arms", {"type": "loft", "axis": "z", "sides": 18, "smooth": 2,
                       "sections": [{"s": 0, "a": 1.15, "b": 1.6}, {"s": 0.2, "a": 1.25, "b": 1.7}, {"s": 0.35, "a": 0.9, "b": 1.25}, {"s": 0.4, "a": 0.0, "b": 0.0}],
                       "at": [[0, r3(PY0 + 3.6), 18.85, 0]], "_about": "the gilt oval of the arms"})
add("cartouche crown", {"type": "loft", "axis": "y", "sides": 12, "smooth": 2,
                        "sections": [{"s": 0, "a": 0.6, "b": 0.4}, {"s": 0.4, "a": 0.9, "b": 0.55}, {"s": 0.9, "a": 0.55, "b": 0.35}, {"s": 1.2, "a": 0.0, "b": 0.0}],
                        "at": [[0, r3(PY0 + 5.95), 18.7, 0]], "_about": "the prince's crown over it"})
# the garden front's centre: a segmental pediment over the Marmorsaal block's north face
GPH = 6.2
garc = seg_arc(GPH, 22.5, 2.3)
gx = [-GPH + 2 * GPH * k / 14 for k in range(15)]
add("garden pediment", {"type": "screen", "outline": [[r3(x), r3(garc(x))] for x in gx][::-1] + [[-8.1, 22.5], [8.1, 22.5]][::-1][::-1] if False else
                        [[-GPH, 22.5]] + [[r3(x), r3(garc(x))] for x in gx] + [[GPH, 22.5]], "t": 0.9, "at": [[0, 0, -15.75, PI]],
                        "_about": "the segmental pediment over the garden front's middle, the Marmorsaal's oculus windows under it"})
add("garden pediment cornice", {"type": "bars", "w": 0.9, "h": 0.45, "kind": "moulding", "paths": [[[r3(x), r3(garc(x)), -15.55] for x in gx]]})

# ================================================================ THE BALUSTRADES, THE ROOFLINE'S STATUES AND URNS
BAL = Balusters(h=1.1, every=0.38, post=0.14, rail=(0.4, 0.16), plinth=(0.42, 0.2))
PIERS, URNS, RSTAT = [], [], []


def roofline(name, faces=None, y=None, statues_on=(), every=None):
    """a balustrade along the block's top on the faces given (outward faces only), piers at its corners and over its
    pilasters, urns on them -- and statues on the faces in `statues_on`"""
    B = BLOCKS[name]; y = B["H"] if y is None else y
    ip = inset(B["pts"], 0.4)
    n = len(ip)
    for i in faces if faces is not None else range(n):
        a, b = ip[i], ip[(i + 1) % n]
        p, q, L, e = edge(B, i)
        nb = max(1, round(L / B["bay"]))
        ts = [k / nb for k in range(nb + 1)]
        pts = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for t in ts]
        for c, d in zip(pts, pts[1:]):
            l = math.dist(c, d); ux, uz = (d[0] - c[0]) / l, (d[1] - c[1]) / l
            BAL.run((c[0] + ux * 0.35, c[1] + uz * 0.35), (d[0] - ux * 0.35, d[1] - uz * 0.35), y)
        nrm = (-e[1], e[0])
        face = FACE_PZ if nrm[1] > 0.5 else FACE_NZ if nrm[1] < -0.5 else FACE_PX if nrm[0] > 0 else FACE_NX
        for k, c in enumerate(pts):
            PIERS.append((c[0], y, c[1]))
            if i in statues_on and 0 < k < len(pts) - 1:
                RSTAT.append(((c[0], y + 1.25, c[1]), face))
            else:
                URNS.append((c[0], y + 1.25, c[1]))


def faces_out(name, skip_pts):
    """the faces of a block not against another (their midpoints far from every point in skip_pts)"""
    B = BLOCKS[name]; out = []
    for i in range(len(B["pts"])):
        p, q, L, e = edge(B, i)
        m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        if all(math.dist(m, s) > 0.6 for s in skip_pts): out.append(i)
    return out


for sx, side in ((1, "east"), (-1, "west")):
    X = lambda x: sx * x
    B = f"{side} block"
    fo = faces_out(B, [(X(11.15), -6.75), (X(9.675), -1.025)])
    roofline(B, fo, statues_on=[face_of(B, X(22.0), 12.53), face_of(B, X(22.0), -9.9)])
    W = f"{side} wing"
    roofline(W, faces_out(W, [(X(33.1), 1.97)]), statues_on=[face_of(W, X(41.5), 12.5), face_of(W, X(41.5), -8.56)])
    for ns in ("north", "south"):
        P = f"{ns}-{side} pavilion"
        roofline(P, faces_out(P, [(X(49.85), -7.58 if ns == "north" else 11.55)]))
    Lk = f"{side} link"
    roofline(Lk, [face_of(Lk, X(58.2), 2.0)])
roofline("centre block", [face_of("centre block", 9.6, -12.7), face_of("centre block", -9.6, -12.7)], statues_on=[face_of("centre block", 9.6, -12.7), face_of("centre block", -9.6, -12.7)])
add("roofline piers", {"type": "box", "width": 0.62, "length": 0.62, "height": 1.25, "kind": "moulding",
                       "at": [[r3(x), r3(y), r3(z), 0] for x, y, z in PIERS], "_about": "the balustrades' piers, the statues and urns standing on them"})
URN = {"type": "loft", "axis": "y", "sides": 12, "smooth": 2,
       "sections": [{"s": 0, "a": 0.2, "b": 0.2}, {"s": 0.1, "a": 0.1, "b": 0.1}, {"s": 0.24, "a": 0.24, "b": 0.24}, {"s": 0.48, "a": 0.25, "b": 0.25},
                    {"s": 0.64, "a": 0.13, "b": 0.13}, {"s": 0.72, "a": 0.18, "b": 0.18}, {"s": 0.82, "a": 0.06, "b": 0.06}, {"s": 0.98, "a": 0.0, "b": 0.0}]}
add("roofline urns", {**URN, "at": [[r3(x), r3(y), r3(z), 0] for x, y, z in URNS], "_about": "the urns and flaming vases on the piers"})
for k, ((x, y, z), face) in enumerate(RSTAT):
    stat[f"roof statue {k + 1}"] = statue((x, y, z), kind="woman" if k % 3 == 1 else "man", style="roman", stone="limestone", scale=1.15, seed=40 + k, face=face,
                                          **({"hold": {"R": "items/weapons/spear"}} if k % 4 == 0 else {"hold": {"L": "items/shields/round"}} if k % 4 == 2 else {}))
# the pediment's figures: Fame and a warrior seated on its broken ends
for sx in (1, -1):
    x = sx * 3.2
    stat[f"pediment figure {'east' if sx > 0 else 'west'}"] = statue((x, arc(3.2) + 0.1, 18.2), kind="woman" if sx > 0 else "man", pose="seated",
                                                                    style="roman", stone="limestone", scale=1.25, seed=7 + sx, face=FACE_PZ)

for sx in (1, -1):
    stat[f"garden pediment figure {'east' if sx > 0 else 'west'}"] = statue((sx * 3.0, garc(3.0) - 0.05, -15.3), kind="man" if sx > 0 else "woman", pose="seated",
                                                                           style="roman", stone="limestone", scale=1.2, seed=31 + sx, face=FACE_NZ)

# ================================================================ THE EHRENHOF: the perron, the ramps, the pool
PZ0, PZ1 = 18.44, 22.0
add("perron", {"type": "box", "width": 17.4, "length": r3(PZ1 - PZ0 + 0.5), "height": FV, "at": [[0, 0, r3((PZ0 - 0.5 + PZ1) / 2), 0]],
               "_about": "the PERRON before the three arches, at the vestibule's floor"})
NP = 10
add("perron flight", {"type": "flight", "run": 0.34, "width": 9.0, "base": 0, "top": FV, "steps": NP, "landing": 0, "at": [[4.5, 0, r3(PZ1 + NP * 0.34), Q]],
                      "_about": "the flight up from the Ehrenhof to the arches"}, last=True)
RAMP = [(8.7, 20.22), (12.5, 20.5), (16.5, 21.7), (19.8, 24.0), (22.0, 27.3), (23.0, 31.0)]
RW = PZ1 - PZ0
cum = [0.0]
for a, b in zip(RAMP, RAMP[1:]): cum.append(cum[-1] + math.dist(a, b))
hgt = [FV * (1 - c / cum[-1]) for c in cum]


def normals(P):
    out = []
    for i in range(len(P)):
        a, b = P[max(0, i - 1)], P[min(len(P) - 1, i + 1)]
        l = math.dist(a, b); out.append(((b[1] - a[1]) / l * -1, (b[0] - a[0]) / l))
    return out


NR = normals(RAMP)
redges = {}
for sx, side in ((1, "east"), (-1, "west")):
    for i in range(len(RAMP) - 1):
        a, b = RAMP[i], RAMP[i + 1]
        na, nb = NR[i], NR[i + 1]
        c = [(a[0] + na[0] * RW / 2, a[1] + na[1] * RW / 2), (b[0] + nb[0] * RW / 2, b[1] + nb[1] * RW / 2),
             (b[0] - nb[0] * RW / 2, b[1] - nb[1] * RW / 2), (a[0] - na[0] * RW / 2, a[1] - na[1] * RW / 2)]
        mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        L = math.dist(a, b); dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        g = (hgt[i + 1] - hgt[i]) / L
        pts = [[r3(sx * (x - mx)), r3(z - mz)] for x, z in c]
        if area(pts) > 0: pts = pts[::-1]
        add(f"{side} ramp {i + 1}", {"type": "prism", "plan": {"points": pts}, "height": r3((hgt[i] + hgt[i + 1]) / 2), "slope": [r3(g * dx * sx), r3(g * dz)],
                                     "railing": False, "at": [[r3(sx * mx), 0, r3(mz), 0]],
                                     **({"_about": "the CURVED RAMPS the carriages drove up to the arches, either side of the flight"} if i == 0 and sx > 0 else {})})
    for s in (1, -1):
        line = [(sx * (p[0] + s * n[0] * (RW / 2 - 0.2)), h + 0.45, p[1] + s * n[1] * (RW / 2 - 0.2)) for p, n, h in zip(RAMP, NR, hgt)]
        redges.setdefault("p", []).extend([[r3(a[0]), r3(a[1]), r3(a[2]), r3(b[0]), r3(b[1]), r3(b[2])] for a, b in zip(line, line[1:])])
add("ramp parapets", {"type": "bars", "w": 0.4, "h": 0.9, "kind": "moulding", "lines": redges["p"], "_about": "the ramps' low parapets"})
# the horse groups at the ramps' feet, the figures at the flight's
for sx in (1, -1):
    add(f"{'east' if sx > 0 else 'west'} horse pedestal", pedestal((sx * 25.2, 0, 33.4), 2.0, 3.8, 2.3, about="the pedestals of the horse groups at the ramps' feet"))
    add(f"{'east' if sx > 0 else 'west'} horse group", comp("equestrian", {"S": 1.6, "kind": "man", "style": "greek", "stone": "limestone", "pose": "aloft", "holdR": ""},
                                                            [[r3(sx * 25.2), 2.3, 33.4, 0]], _about="a horse group (a horse and its tamer) at the ramp's foot"))
    add(f"{'east' if sx > 0 else 'west'} flight pedestal", pedestal((sx * 5.4, 0, 24.6), 1.1, 1.6, 1.4))
    stat[f"flight figure {sx}"] = statue((sx * 5.4, 1.4, 24.6), kind="man" if sx > 0 else "woman", style="roman", stone="limestone", scale=1.2, seed=60 + sx, face=FACE_PZ)
# the forecourt's gravel, the lawns beside the pool, the pool's stone kerb
PX0, PX1, PZA, PZB = -28.0, 28.0, 46.0, 108.0
FCX = 45.0
add("forecourt", {"type": "box", "width": r3(2 * FCX), "length": r3(PZA - 0.8 - 13.0), "height": 0.08, "at": [[0, 0, r3((PZA - 0.8 + 13.0) / 2), 0]],
                  "_about": "the Ehrenhof's gravel between the palace and the pool"})
for sx, side in ((1, "east"), (-1, "west")):
    add(f"pool walk {side}", {"type": "box", "width": 4.4, "length": r3(PZB - PZA + 1.6), "height": 0.08, "at": [[r3(sx * (PX1 + 0.8 + 2.2)), 0, r3((PZA + PZB) / 2), 0]]})
    add(f"pool lawn {side}", {"type": "box", "width": r3(FCX - PX1 - 0.8 - 4.4), "length": r3(PZB - PZA + 1.6), "height": 0.14,
                              "at": [[r3(sx * (PX1 + 0.8 + 4.4 + (FCX - PX1 - 5.2) / 2)), 0, r3((PZA + PZB) / 2), 0]],
                              **({"_about": "the lawns either side of the pool"} if sx > 0 else {})})
add("pool walk south", {"type": "box", "width": r3(2 * FCX), "length": 3.0, "height": 0.08, "at": [[0, 0, r3(PZB + 0.8 + 1.5), 0]]})
KO = 0.4
add("pool kerb", {"type": "bars", "w": 0.8, "h": 0.5, "closed": True, "caps": False, "kind": "moulding",
                  "paths": [[[r3(x), 0.25, r3(z)] for x, z in [(PX0 - KO, PZA - KO), (PX1 + KO, PZA - KO), (PX1 + KO, PZB + KO), (PX0 - KO, PZB + KO)]]],
                  "_about": "the pool's stone kerb"})
SHORE = [[PX0, PZA], [PX1, PZA], [PX1, PZB], [PX0, PZB]]
PCX, PCZ = (PX0 + PX1) / 2, (PZA + PZB) / 2
MOAT = {"pool": True, "hw": r3((PX1 - PX0) / 2), "hd": r3((PZB - PZA) / 2), "w": 0, "depth": 1.8, "surface": -0.4, "x": r3(PCX), "z": r3(PCZ),
        "shore": [[r3(x - PCX), r3(z - PCZ)] for x, z in SHORE]}

# ================================================================ THE GARDEN: the terrace's flights, the upper parterre
GZ0 = -24.0                                  # the terrace's edge
GZ1 = -118.5                                 # the parterre's north end: the cascade
NG = 5
for nm, xc, w in (("middle", 0.0, 14.0), ("east", 45.0, 6.0), ("west", -45.0, 6.0)):
    add(f"terrace flight {nm}", {"type": "flight", "run": 0.36, "width": w, "base": 0, "top": FG, "steps": NG, "landing": 0,
                                 "at": [[r3(xc - w / 2), 0, r3(GZ0 - NG * 0.36), -Q]],
                                 **({"_about": "the flights from the garden terrace down to the parterre"} if nm == "middle" else {})}, last=True)
# the terrace's balustrade along its edge, open at the flights; its ends
gaps = [(-8.8, 8.8), (40.3, 49.7), (-49.7, -40.3)]                     # (the flights and their cheeks)
xs = sorted([-61.4, 61.4] + [a for g in gaps for a in g])
for a, b in zip(xs[0::2], xs[1::2]):
    BAL.run((a + 0.3, GZ0 + 0.25), (b - 0.3, GZ0 + 0.25), FG)
for sx in (1, -1):
    BAL.run((sx * 61.15, GZ0 + 0.3), (sx * 61.15, -6.8), FG)
    BAL.run((sx * 61.15, 10.8), (sx * 61.15, 15.8), FG)
# the stair cheeks and their SPHINXES
SPH = []
CHEEK = []
for xc, w in ((0.0, 14.0), (45.0, 6.0), (-45.0, 6.0)):
    for s in (1, -1):
        x = xc + s * (w / 2 + 0.85)
        CHEEK.append((x, GZ0 - 0.95))
        SPH.append((x, FG, GZ0 - 0.95, PI))
add("stair cheeks", {"type": "box", "width": 1.7, "length": 2.9, "height": FG, "at": [[r3(x), 0, r3(z), 0] for x, z in CHEEK],
                     "_about": "the cheeks of the terrace's flights, the sphinxes on them"})
# the parterre: gravel over it, the lawn panels edged in box, yew cones, the side allees between tall hedges
add("parterre gravel", {"type": "box", "width": 108.0, "length": r3(GZ0 - GZ1 - 0.2), "height": 0.08, "at": [[0, 0, r3((GZ0 - 0.2 + GZ1) / 2), 0]],
                        "_about": "the UPPER PARTERRE's gravel"})
PAN = [(9.5, 44.0, -29.0, -61.0), (9.5, 44.0, -77.0, -109.0)]
LAWNS, HEDGE, YEWS = [], [], []
k = 0
for sx in (1, -1):
    for x0, x1, z0, z1 in PAN:
        k += 1
        xa, xb = sorted((sx * x0, sx * x1)); za, zb = sorted((z0, z1))
        cx, cz, w, l = (xa + xb) / 2, (za + zb) / 2, xb - xa, zb - za
        add(f"lawn {k}", {"type": "box", "width": r3(w), "length": r3(l), "height": 0.16, "at": [[r3(cx), 0, r3(cz), 0]],
                          **({"_about": "the parterre's lawn panels"} if k == 1 else {})})
        LAWNS.append(f"lawn {k}")
        e = 0.35
        HEDGE.append([[r3(xa + e), 0.42, r3(za + e)], [r3(xb - e), 0.42, r3(za + e)], [r3(xb - e), 0.42, r3(zb - e)], [r3(xa + e), 0.42, r3(zb - e)]])
        # the broderie: an inner frame with its corners cut, a ring in the middle
        f = 5.0; c = 3.0
        HEDGE.append([[r3(x), 0.42, r3(z)] for x, z in [(xa + f + c, za + f), (xb - f - c, za + f), (xb - f, za + f + c), (xb - f, zb - f - c), (xb - f - c, zb - f),
                                                          (xa + f + c, zb - f), (xa + f, zb - f - c), (xa + f, za + f + c)]])
        HEDGE.append([[r3(cx + 4.2 * math.cos(t * PI / 8)), 0.42, r3(cz + 4.2 * math.sin(t * PI / 8))] for t in range(16)])
        YEWS += [(xa + 1.2, za + 1.2), (xb - 1.2, za + 1.2), (xa + 1.2, zb - 1.2), (xb - 1.2, zb - 1.2), (cx, za + 1.2), (cx, zb - 1.2), (cx, cz)]
add("box hedges", {"type": "bars", "w": 0.5, "h": 0.55, "closed": True, "caps": False, "paths": HEDGE, "_about": "the box hedges edging the lawns and drawing the broderie"})
add("yew cones", {"type": "column", "radius": 0.75, "height": 3.4, "sides": 10, "taper": 0.06, "at": [[r3(x), 0.16, r3(z), 0] for x, z in YEWS],
                  "_about": "the clipped yew cones at the panels' corners and middles"})
for sx, side in ((1, "east"), (-1, "west")):
    add(f"{side} allee hedge", {"type": "box", "width": 1.4, "length": r3(GZ0 - GZ1 - 2.0), "height": 3.4, "at": [[r3(sx * 54.0), 0, r3((GZ0 - 2.0 + GZ1) / 2), 0]],
                                **({"_about": "the tall clipped hedges walling the side allees"} if sx > 0 else {})})
PV = [(sx * 8.4, z) for sx in (1, -1) for z in (-33.0, -45.0, -57.0, -81.0, -93.0, -105.0)]
add("parterre vase pedestals", {"type": "box", "width": 0.9, "length": 0.9, "height": 1.3, "kind": "moulding", "at": [[r3(x), 0, r3(z), 0] for x, z in PV],
                                "_about": "the stone vases along the parterre's middle walk, on their pedestals"})
add("parterre vases", {**URN, "at": [[r3(x), 1.3, r3(z), 0] for x, z in PV]})
add("allee yews", {"type": "column", "radius": 0.7, "height": 3.0, "sides": 10, "taper": 0.06,
                   "at": [[r3(sx * 48.0), 0.08, r3(z), 0] for sx in (1, -1) for z in [GZ0 - 8.0 - 10.0 * k for k in range(9)]],
                   "_about": "the yew cones along the side allees"})
# the two round fountains
FT = [(26.75, -69.0), (-26.75, -69.0)]
for k, (x, z) in enumerate(FT):
    nm = f"fountain {k + 1}"
    add(f"{nm} basin", {"type": "enclosure", "plan": {"sides": 24, "radius": 6.8}, "thickness": 0.5, "height": 0.62, "glass": False, "interior": False, "openings": [],
                        "at": [[x, 0, z, 0]], **({"_about": "the parterre's two round fountains: a basin, a figure in the middle, its jet"} if k == 0 else {})})
    add(f"{nm} water", {"type": "prism", "plan": {"sides": 24, "radius": 6.3}, "height": 0.42, "flatRoof": True, "at": [[x, 0, z, 0]]})
    add(f"{nm} pedestal", pedestal((x, 0.42, z), 1.4, 1.4, 1.6, about="the figure's rock in the middle"))
    add(f"{nm} jet", {"type": "marker", "role": "flow", "at": [[x, 3.2, z, 0]], "data": {"kind": "jet", "r": 0.12, "h": 4.5}})
    add(f"{nm} ripple", {"type": "marker", "role": "flow", "at": [[x, 0.43, z, 0]], "data": {"kind": "pool", "r": 6.0, "seg": 24}})
    stat[f"fountain figure {k + 1}"] = statue((x, 2.02, z), kind="man", pose="aloft", style="greek", stone="limestone", scale=1.1, seed=90 + k, face=FACE_PZ)

# ================================================================ THE CASCADE AND THE LOWER BASIN'S COURT
CD = -3.6                                    # the court's floor
CX = 22.0                                    # its half-width
CZ1 = -140.0                                 # its north wall's inner face
add("upper basin", {"type": "enclosure", "plan": {"rect": [20.0, 6.0]}, "thickness": 0.45, "height": 0.62, "glass": False, "interior": False, "openings": [],
                    "at": [[0, 0, -115.5, 0]], "_about": "the UPPER CASCADE's basin at the parterre's end, its water spilling over its north rim"})
add("upper basin water", {"type": "box", "width": 19.1, "length": 5.1, "height": 0.48, "at": [[0, 0, -115.5, 0]]})
add("upper basin group pedestal", pedestal((0, 0.48, -115.2), 3.4, 1.8, 1.2, about="the rock of the cascade's sculpture group"))
for k, x in enumerate((-0.9, 0.9)):
    stat[f"cascade figure {k + 1}"] = statue((x, 1.68, -115.2), kind="man" if k == 0 else "woman", pose="aloft" if k == 0 else "contrapposto",
                                             style="greek", stone="limestone", scale=1.15, seed=95 + k, face=FACE_NZ)
STEPS = [(0.0, -118.5), (-0.9, -120.3), (-1.8, -122.1), (-2.7, -123.9)]
for k in range(1, 4):
    y, zf = STEPS[k]; zb = STEPS[k - 1][1]
    add(f"cascade step {k}", {"type": "box", "width": 16.0, "length": 1.8, "height": r3(y - CD), "at": [[0, CD, r3((zf + zb) / 2), 0]],
                              **({"_about": "the cascade's steps, the water running over each"} if k == 1 else {})})
    add(f"cascade water {k}", {"type": "box", "width": 15.2, "length": 1.7, "height": 0.06, "at": [[0, r3(y), r3((zf + zb) / 2 - 0.05), 0]]})
JETS = []
for k in range(4):
    y, z = STEPS[k]
    yb = STEPS[k + 1][0] if k < 3 else CD + 0.45
    for j in range(7):
        JETS.append([r3(-6.6 + 2.2 * j), r3(yb), r3(z - 0.15), 0, r3(y - yb)])
add("cascade falls", {"type": "marker", "role": "flow", "at": [j[:4] for j in JETS], "data": {"kind": "jet", "r": 0.32, "h": [j[4] for j in JETS]},
                      "_about": "the water falling over each step's lip"})
for sx in (1, -1):
    add(f"cascade cheek {'east' if sx > 0 else 'west'}", {"type": "box", "width": 1.8, "length": r3(-STEPS[0][1] + STEPS[3][1] + 1.8), "height": r3(-CD),
                                                          "at": [[r3(sx * 8.9), CD, r3((STEPS[0][1] + STEPS[3][1] - 1.8) / 2), 0]],
                                                          **({"_about": "the cascade's cheek walls, the sphinxes on them"} if sx > 0 else {})})
    SPH.append((sx * 8.9, 0.0, -119.6, PI))
add("lower basin", {"type": "enclosure", "plan": {"rect": [26.0, 8.0]}, "thickness": 0.5, "height": 0.7, "glass": False, "interior": False, "openings": [],
                    "at": [[0, CD, -128.5, 0]], "_about": "the lower basin at the cascade's foot"})
add("lower basin water", {"type": "box", "width": 25.0, "length": 7.0, "height": 0.5, "at": [[0, CD, -128.5, 0]]})
add("lower basin jets", {"type": "marker", "role": "flow", "at": [[x, r3(CD + 0.5), -128.5, 0] for x in (-7.0, 0.0, 7.0)], "data": {"kind": "jet", "r": 0.1, "h": 3.8}})
add("lower basin rocks", {"type": "box", "width": 1.6, "length": 1.6, "height": 1.0, "at": [[x, r3(CD + 0.5), -128.5, 0] for x in (-3.5, 3.5)]})
for k, x in enumerate((-3.5, 3.5)):
    stat[f"lower basin figure {k + 1}"] = statue((x, CD + 1.5, -128.5), kind="woman" if k == 0 else "man", pose="reclining" if False else "contrapposto",
                                                 style="greek", stone="limestone", scale=1.1, seed=97 + k, face=FACE_NZ)
add("court floor", {"type": "box", "width": r3(2 * CX), "length": r3(STEPS[0][1] - CZ1), "height": 0.3, "at": [[0, r3(CD - 0.3), r3((STEPS[0][1] + CZ1) / 2), 0]],
                    "_about": "the sunken court of the lower basin, 3.6 m under the parterre (the garden falling toward the Lower Belvedere)"})
RWALL = [("court south wall", 2 * CX + 2.0, 1.0, (0, STEPS[0][1] + 0.5)), ("court north wall", 2 * CX + 2.0, 1.0, (0, CZ1 - 0.5)),
         ("court east wall", 1.0, STEPS[0][1] - CZ1, (CX + 0.5, (STEPS[0][1] + CZ1) / 2)), ("court west wall", 1.0, STEPS[0][1] - CZ1, (-CX - 0.5, (STEPS[0][1] + CZ1) / 2))]
for nm, w, l, (x, z) in RWALL:
    add(nm, {"type": "box", "width": r3(w), "length": r3(l), "height": r3(-CD + 0.3), "at": [[r3(x), r3(CD - 0.3), r3(z), 0]],
             **({"_about": "the court's retaining walls, their tops the parterre's level"} if nm == "court south wall" else {})})
NC = 20
for sx in (1, -1):
    add(f"court flight {'east' if sx > 0 else 'west'}", {"type": "flight", "run": 0.32, "width": 3.6, "base": CD, "top": 0.0, "steps": NC, "landing": 0,
                                                         "at": [[r3(sx * 15.0 - 1.8), CD, r3(STEPS[0][1] - NC * 0.32), -Q]],
                                                         **({"_about": "the flights down into the court beside the cascade"} if sx > 0 else {})}, last=True)
# the court's rim: the balustrade the garden ends at, looking out over the lower basin and the cascade
for sx in (1, -1):
    BAL.run((sx * 9.9, STEPS[0][1] - 0.3), (sx * 13.0, STEPS[0][1] - 0.3), 0.0)
    BAL.run((sx * 17.0, STEPS[0][1] - 0.3), (sx * (CX + 0.4), STEPS[0][1] - 0.3), 0.0)
    BAL.run((sx * (CX + 0.4), STEPS[0][1] - 0.3), (sx * (CX + 0.4), CZ1 - 0.4), 0.0)
    BAL.run((sx * 13.0, STEPS[0][1] - 0.4), (sx * 13.0, STEPS[0][1] - NC * 0.32 - 0.2), CD + 0.0) if False else None
BAL.run((-CX - 0.4, CZ1 - 0.4), (CX + 0.4, CZ1 - 0.4), 0.0)
add("court urns", {**URN, "at": [[r3(sx * (CX + 0.4)), 1.1, r3(z), 0] for sx in (1, -1) for z in (STEPS[0][1] - 0.3, -129.0, CZ1 - 0.4)] +
                   [[r3(x), 1.1, r3(CZ1 - 0.4), 0] for x in (-11.0, 0.0, 11.0)], "_about": "urns on the court's rim"})
add("court urn piers", {"type": "box", "width": 0.62, "length": 0.62, "height": 1.1, "kind": "moulding",
                        "at": [[r3(sx * (CX + 0.4)), 0, r3(z), 0] for sx in (1, -1) for z in (STEPS[0][1] - 0.3, -129.0, CZ1 - 0.4)] + [[r3(x), 0, r3(CZ1 - 0.4), 0] for x in (-11.0, 0.0, 11.0)]})
# the sphinxes
add("sphinxes", comp("sphinx", {"S": 2.4, "plinthH": 0.55}, [[r3(x), r3(y), r3(z), r3(yaw)] for x, y, z, yaw in SPH],
                     _about="THE SPHINXES on the terrace's stair cheeks and at the cascade (components/sphinx: a lion's body, a woman's bust)"))
# the outside flights up to the pavilions', the links' and the blocks' doors from the court
for sx, side in ((1, "east"), (-1, "west")):
    X = lambda x: sx * x
    for nm, (x, z) in (("north pavilion", (61.4, -9.2)), ("south pavilion", (61.4, 13.2)), ("link", (58.7, 2.0))):
        foot = X(x + 5 * 0.3)
        yaw = PI if sx > 0 else 0.0
        zc = z - 1.0 if sx > 0 else z + 1.0
        add(f"{side} {nm} steps", {"type": "flight", "run": 0.3, "width": 2.0, "base": 0, "top": FG, "steps": 5, "landing": 0, "at": [[r3(foot), 0, r3(zc), yaw]]}, last=True)
    add(f"{side} court door steps", {"type": "flight", "run": 0.3, "width": 2.0, "base": 0, "top": FG, "steps": 5, "landing": 0,
                                     "at": [[r3(X(20.6) + 1.0), 0, r3(13.0 + 5 * 0.3), Q]]}, last=True)

for k, v in capped(stat).items(): add(k, v)
write_blocks()
for k, v in BAL.parts("balustrade").items(): add(k, v)

doc = {"name": "Belvedere",
       "_about": "THE UPPER BELVEDERE, Vienna (Johann Lukas von Hildebrandt for Prince Eugene of Savoy, 1717-23), on OpenStreetMap's plan: the palace 122 m long stepping down from the middle -- the Marmorsaal's chamfered centre under the tallest tent roof, the three-storey blocks, the two-storey wings, the four octagonal corner pavilions under their copper bell domes -- each block under its own curved green copper roof; the south projection's three arches, ramps and broken curved pediment over the Ehrenhof and its pool; the garden terrace, the upper parterre with its box and yews, fountains and sphinxes, the cascade into the lower basin's sunken court. Inside: the Sala Terrena on its four Atlantes, the Prunkstiege, the Marmorsaal, the state rooms, the chapel. x along the palace (east), z south to the pool, y 0 the court's and the garden's ground. Generated by tools/archgen/belvedere.py.",
       "params": {"detail": 4}, "railing": {"type": "balusters"},
       "site": {"moat": MOAT, "dig": [[-CX, CZ1, CX, STEPS[0][1]]], "glazed": True},
       "build": build + late, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/belvedere.json"), "w").write(json.dumps(doc, indent=1) + "\n")

# ================================================================ THE FINISH
CEN_BOX = [-11.2, -15.5, 11.2, 1.6]
SP_BOX = [-8.3, 1.5, 8.3, 18.5]
CHAPEL_BOX = [49.8, 8.3, 61.0, 18.1]
GARDEN_BOX = [-56.0, -119.0, 56.0, -24.3]
FINISH = {
    "name": "Belvedere", "building": "architecture/belvedere",
    "_about": "The Belvedere (written by tools/archgen/belvedere.py): pale cream stucco with every order, cornice, window surround and balustrade in white, the ground storey banded; the roofs, domes and lanterns green copper with gilt finials and the gilt arms in the pediment; inside, the Sala Terrena's white stucco, the Prunkstiege's white walls under a painted ceiling, the Marmorsaal's marbled walls and red-brown marble pilasters under Carlone's fresco, the chapel's rose marbling, the state rooms' damask and parquet; outside, the pale gravel, the lawns, the box and yew, the water.",
    "stone": {"color": "#e9e0c8", "accent": "#d8cdb0", "pat": "ashlar"},
    "rules": [
        {"parts": "kind:glass", "pattern": "glass/quarries", "palette": "grisaille", "_about": "clear glass in small panes"},
        {"parts": ["north-east dome/finial", "south-east dome/finial", "north-west dome/finial", "south-west dome/finial", "cartouche arms", "cartouche crown"],
         "pattern": "roofs/gold leaf", "palette": "gold", "_about": "the finials and the Savoy arms gilt"},
        {"parts": ["roof dormers/roof"], "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the dormers' hoods"},
        {"parts": ["roof dormers"], "pattern": "stone/plaster", "palette": "plaster-white", "_about": "...their white fronts"},
        {"parts": ["centre roof", "east block roof", "west block roof", "east wing roof", "west wing roof"], "pattern": "roofs/sheet metal", "palette": "copper",
         "_about": "the mansards: green copper"},
        {"parts": ["north-east dome", "south-east dome", "north-west dome", "south-west dome"], "side": "out", "pattern": "roofs/sheet metal", "palette": "copper",
         "_about": "the pavilions' domes and lanterns: green copper"},
        {"parts": ["projection roof"], "surface": "roof", "pattern": "roofs/sheet metal", "palette": "copper"},
        {"parts": ["chimneys"], "pattern": "stone/plaster", "palette": "ivory"},
        # the garden and the court
        {"parts": ["box hedges", "yew cones", "allee yews", "east allee hedge", "west allee hedge"], "color": "#33502b", "accent": "#294322", "_about": "clipped box and yew"},
        {"parts": LAWNS + ["pool lawn east", "pool lawn west"], "surface": "floor", "pattern": "materials/grass", "palette": "lawn", "_about": "the lawns"},
        {"parts": LAWNS + ["pool lawn east", "pool lawn west"], "pattern": "stone/ashlar fine", "palette": "limestone", "_about": "their stone edging"},
        {"parts": ["parterre gravel", "forecourt", "pool walk east", "pool walk west", "pool walk south", "court floor"], "surface": "floor", "pattern": "stone/sand",
         "palette": "loire-gravel", "_about": "the pale gravel of the walks and the court"},
        {"parts": ["fountain 1 water", "fountain 2 water", "upper basin water", "lower basin water", "cascade water 1", "cascade water 2", "cascade water 3"],
         "color": "#5b7f88", "accent": "#4b6d76", "_about": "the basins' water"},
        {"parts": ["fountain 1 basin", "fountain 2 basin", "upper basin", "lower basin", "cascade step 1", "cascade step 2", "cascade step 3", "cascade cheek east",
                   "cascade cheek west", "court south wall", "court north wall", "court east wall", "court west wall", "pool kerb", "stair cheeks", "lower basin rocks",
                   "fountain 1 pedestal", "fountain 2 pedestal", "upper basin group pedestal"], "pattern": "stone/ashlar", "palette": "limestone",
         "_about": "the basins, the cascade, the court's walls and the kerbs: grey-white stone"},
        {"parts": ["sphinxes"], "pattern": "stone/ashlar fine", "palette": "limestone", "_about": "the sphinxes"},
        {"parts": ["east horse group", "west horse group"], "pattern": "stone/ashlar fine", "palette": "limestone"},
        # inside: the Marmorsaal
        {"parts": ["marmorsaal pilasters"], "pattern": "stone/marble", "palette": "granite-red", "_about": "the Marmorsaal's pilasters: red-brown Adnet marble"},
        {"parts": ["marmorsaal capitals", "marmorsaal cornice", "marmorsaal gallery band", "furniture chandelier"], "pattern": "roofs/gold leaf", "palette": "gold",
         "_about": "their gilt capitals, the gilt cornice and band"},
        {"within": CEN_BOX, "side": "in", "surface": "ceiling", "above": FB + 1.0, "pattern": "stone/plaster", "palette": "pilar-fresco", "_about": "Carlone's ceiling"},
        {"within": CEN_BOX, "side": "in", "surface": "wall", "above": 16.55, "pattern": "stone/plaster", "palette": "alabaster",
         "_about": "the Marmorsaal's upper storey: white stucco round the oculi, Chiarini's painted architecture"},
        {"within": CEN_BOX, "side": "in", "surface": "wall", "above": FB - 0.1, "pattern": "painted/faux marble", "palette": "marble-rose",
         "_about": "...its lower storey: red marble"},
        {"within": CEN_BOX, "side": "in", "surface": "floor", "above": FB - 0.5, "pattern": "floors/checker diagonal", "palette": "marble-rose", "_about": "...its marble floor"},
        # the Sala Terrena
        {"parts": ["atlas pedestals", "atlas pedestal caps", "atlas pedestal bases", "atlas imposts", "atlas abaci"], "pattern": "stone/ashlar fine", "palette": "limestone"},
        {"parts": [f"sala terrena vault {k + 1}" for k in range(9)], "pattern": "stone/plaster", "palette": "plaster-white", "_about": "the Sala Terrena's white stucco vaults"},
        {"within": CEN_BOX, "side": "in", "surface": "floor", "pattern": "floors/checker", "palette": "marble-grey", "_about": "...its stone floor"},
        {"within": CEN_BOX, "side": "in", "surface": "wall", "pattern": "stone/plaster", "palette": "plaster-white"},
        # the Prunkstiege
        {"parts": ["prunkstiege down", "prunkstiege east flight", "prunkstiege west flight", "prunkstiege east upper flight", "prunkstiege west upper flight", "vestibule floor"],
         "pattern": "floors/flagstones", "palette": "limestone", "_about": "the stairs and the vestibule: stone"},
        {"within": SP_BOX, "side": "in", "surface": "ceiling", "above": 13.0, "pattern": "stone/plaster", "palette": "pilar-fresco", "_about": "the stair hall's painted ceiling"},
        {"within": SP_BOX, "side": "in", "surface": "wall", "pattern": "stone/plaster", "palette": "plaster-white", "_about": "its white stucco walls"},
        # the chapel
        {"parts": ["chapel retable", "chapel retable columns", "chapel altar"], "pattern": "painted/faux marble", "palette": "marble-grey"},
        {"within": CHAPEL_BOX, "side": "in", "surface": "wall", "above": FB - 0.1, "pattern": "painted/faux marble", "palette": "baroque-rose", "_about": "the chapel's marbling"},
        {"parts": ["chapel cupola"], "pattern": "stone/plaster", "palette": "pilar-fresco", "_about": "its painted cupola"},
        # the state rooms and the rest inside
        {"surface": "wall", "side": "in", "above": FB - 0.1, "below": L2 - 0.2, "pattern": "fabrics/damask", "palette": "damask-red", "_about": "the state rooms' damask"},
        {"surface": "floor", "side": "in", "above": FB - 0.5, "pattern": "timber/herringbone", "palette": "oak", "_about": "the upper floors' parquet"},
        {"surface": "floor", "side": "in", "pattern": "floors/checker", "palette": "marble-grey", "_about": "the ground floor's stone"},
        {"surface": "ceiling", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
        {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
        {"side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
        # outside: the terraces' paving, the stucco and its white trim
        {"parts": ["platform", "perron", "link"], "surface": "floor", "pattern": "floors/flagstones", "palette": "limestone", "_about": "the terrace's and the perron's flags"},
        {"parts": ["east link terrace", "west link terrace"], "surface": "floor", "pattern": "floors/flagstones", "palette": "limestone"},
        {"surface": "floor", "pattern": "floors/flagstones", "palette": "limestone", "_about": "the ramps, the flights and the roofs' decks"},
        {"parts": ["kind:moulding", "kind:column", "kind:colonnade", "kind:bars", "pediment east", "pediment west", "garden pediment", "cartouche", "cartouche frame",
                   "pediment base cornice", "roofline piers"], "pattern": "stone/plaster", "palette": "plaster-white",
         "_about": "every order, cornice, band, window surround, balustrade and the pediments: white"},
        {"parts": ["platform", "perron", "stair cheeks"], "surface": "wall", "pattern": "stone/rusticated", "palette": "limestone", "_about": "the platform's rusticated stone"},
        {"surface": "wall", "below": FB, "pattern": "stone/stucco lines", "palette": "ivory", "_about": "the ground storey: banded stucco"},
        {"pattern": "stone/plaster", "palette": "ivory", "_about": "the facades: pale cream stucco"},
    ]}
open(os.path.join(ROOT, "assets/finishes/belvedere.json"), "w").write(json.dumps(FINISH, indent=2) + "\n")

# ================================================================ THE DOORS
DOORS = {"name": "Belvedere: doors", "building": "belvedere",
         "_about": "The Belvedere: oak doors in raised baroque panels -- the carriage entrance's middle arch, the Sala Terrena's garden doors, the blocks', wings' and pavilions' doors outside, the Marmorsaal's door from the Prunkstiege",
         "doors": [
             {"_about": "the carriage entrance's middle arch", "part": "south projection", "near": [[0.0, 18.44]], "style": "baroque", "leafH": 5.8},
             {"_about": "the Sala Terrena's three doors to the garden", "part": "centre block", "near": [[-5.4, -15.45], [0.0, -15.45], [5.4, -15.45]], "style": "baroque", "below": 6.0},
             {"_about": "the Marmorsaal's door from the Prunkstiege", "part": "centre block", "near": [[0.0, 1.55]], "style": "baroque", "below": 30.0},
             {"_about": "the blocks' doors to the garden and the court", "part": ["east block", "west block"],
              "near": [[22.1, -9.9], [20.6, 12.53], [-22.1, -9.9], [-20.6, 12.53]], "style": "baroque", "below": 6.0},
             {"_about": "the wings' garden doors", "part": ["east wing", "west wing"], "near": [[41.5, -8.56], [-41.5, -8.56]], "style": "baroque", "below": 6.0},
             {"_about": "the pavilions' doors", "part": ["north-east pavilion", "south-east pavilion", "north-west pavilion", "south-west pavilion"],
              "near": [[60.9, -9.2], [60.9, 13.2], [-60.9, -9.2], [-60.9, 13.2]], "style": "baroque", "below": 6.0},
             {"_about": "the links' doors", "part": ["east link", "west link"], "near": [[58.2, 2.0], [-58.2, 2.0]], "style": "baroque"},
             {"_about": "the bel etage's French doors out onto the links' terraces, glazed like the windows beside them",
              "part": ["east wing", "west wing", "north-east pavilion", "south-east pavilion", "north-west pavilion", "south-west pavilion"],
              "near": [[49.85, 2.0], [-49.85, 2.0], [55.1, -4.4], [55.1, 8.4], [-55.1, -4.4], [-55.1, 8.4]], "style": "french", "above": 6.0},
         ]}
open(os.path.join(ROOT, "assets/doors/belvedere.json"), "w").write(json.dumps(DOORS, indent=2) + "\n")
print(len(parts), "parts")
