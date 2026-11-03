# SACRE-COEUR, Montmartre (Paul Abadie, 1875-1914), Romano-Byzantine, in white Chateau-Landon travertine -- rebuilt
# (2026-11-03) on its real plan: the footprint and the heights of the OpenStreetMap building parts (way 23762981 and its
# building:parts, turned 4.2 degrees onto the church's axis), the dimensions of the French and English Wikipedia and the
# roof plan on Wikimedia Commons (Sacre-Coeur-de-Montmartre_plan_roofs.png).
#   THE PLAN: a Greek cross round the crossing -- the dome's square, 16 m (the cupola 16 m across inside) -- whose four
# arms are barrel-vaulted and gabled; the four angles between them filled by the CORNER BAYS, each a square tower over a
# sail vault inside and an octagonal drum, egg dome and lantern outside (the four small domes); round all of it the
# AISLES, low and flat-roofed (the 16 m block of the OSM outline); behind, the long choir ending in the APSE (the great
# mosaic of Christ in Majesty in its half dome), the AMBULATORY round it and seven radiating chapels -- six half-domed,
# the axial one the foot of the square CAMPANILE (the Savoyarde in its belfry, an upper stage, a small dome, lantern and
# cross). In front the PORCH of three arches with the bronze equestrian statues of Saint Louis (west) and Joan of Arc
# (east) on its corners, the gable with the Sacred Heart in its niche, the parvis terrace and its great flight.
#   Under the church the CRYPT, the same plan one storey down (lit through small windows low in the walls, entered
# from the west). THE CLIMB: a stair turret from the ground in the back west angle (as the visitors' entrance is on the
# west side) to the high roof terraces over the choir aisles, the gutter walk along the choir's wall head to the roof
# round the drum's foot, and a second turret against the drum up to the GALLERIES at the dome's foot -- the outer one
# behind its arcade, open to Paris, and through a door the inner one round the drum, looking down into the church.
#   The front faces +z; the origin is the dome's middle. Numbers are worked here and written as numbers.
#   (A `wall`'s thickness lies on the -z side of its placement -- the -x side, turned a quarter.)
#   python3 tools/archgen/sacre_coeur.py  ->  assets/architecture/sacre-coeur.json, assets/finishes/sacre-coeur.json
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n); return n
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
Q, PI = math.pi / 2, math.pi
r3 = lambda v: round(v, 3)
SIDES = ((1, "east"), (-1, "west"))

# ---- the levels (y up; the ground round the church 0; OSM heights stand on the parvis, 4.5 m up)
G = 5.5            # the church's floor (the crypt under it, from the ground)
L1 = 20.5          # the aisles' flat roofs (OSM 16 m)
L2 = 28.5          # the arms' wall heads, the corner towers', the choir aisles' and the ambulatory's roofs, the deck round the drum (24 m)
SPR = 19.7         # the barrels' and the great arches' springing: their crowns 27.7, their backs L2
A, W = 8.0, 10.85  # the arms' inner faces (the crossing 16 m) and outer faces: the walls and piers 2.85 m
WT = W - A
ZF = 27.6          # the front wall's inner face (its outer 28.9)
XT = 23.7          # the transept end walls' inner faces (their outer 25.0)
ZA = -31.6         # the apse's middle, where the choir's straight part ends
CQ = 20.1          # the corner towers' outer faces (their inner, the arms' outer: W)
CT = 1.2           # their walls
OT = 1.3           # the outer walls'
ROUND = {"profile": "semicircular"}

def arch(at, w, sill, spring, glass=None, **kw):
    o = {"at": r3(at), "width": r3(w), "sill": r3(sill), "springing": r3(spring), "head": ROUND, **kw}
    if glass is not None: o["glass"] = glass
    return o

def wall_z(name, xa, xb, z0, z1, tiers, y=0, about=None, **kw):
    """a wall along z, from xa to xb thick, z0..z1 long; its tiers' openings `at` given as world z (turned to its own)"""
    zc = (z0 + z1) / 2
    tt = [{**t, "openings": [{**o, "at": r3(zc - o["at"])} for o in t["openings"]]} for t in tiers]
    d = {"type": "wall", "width": r3(z1 - z0), "thickness": r3(xb - xa), "height": r3(sum(t.get("h", 0) for t in tiers) if "height" not in kw else kw.pop("height")),
         "tiers": tt, "at": [[r3(xb), y, r3(zc), Q]], **kw}
    if about: d["_about"] = about
    return add(name, d)

def wall_x(name, za, zb, x0, x1, tiers, y=0, about=None, **kw):
    """a wall along x, from za to zb thick, x0..x1 long; its tiers' openings `at` given as world x"""
    xc = (x0 + x1) / 2
    tt = [{**t, "openings": [{**o, "at": r3(o["at"] - xc)} for o in t["openings"]]} for t in tiers]
    d = {"type": "wall", "width": r3(x1 - x0), "thickness": r3(zb - za), "height": r3(sum(t.get("h", 0) for t in tiers) if "height" not in kw else kw.pop("height")),
         "tiers": tt, "at": [[r3(xc), y, r3(zb), 0]], **kw}
    if about: d["_about"] = about
    return add(name, d)

def box(name, x0, x1, z0, z1, y0, y1, about=None, **kw):
    d = {"type": "box", "width": r3(x1 - x0), "length": r3(z1 - z0), "height": r3(y1 - y0), "at": [[r3((x0 + x1) / 2), r3(y0), r3((z0 + z1) / 2), 0]], **kw}
    if about: d["_about"] = about
    return add(name, d)

def mirror_x(pts):
    """a half outline (x >= 0, from the front axis round to the back axis) made whole"""
    return pts + [[-x, z] for x, z in reversed(pts) if abs(x) > 1e-9]

def arc(cx, cz, r, a0, a1, n):
    """points on a circle, the angle from +z toward +x (degrees)"""
    return [[r3(cx + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))), r3(cz + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)))] for i in range(n + 1)]

CRYPT = lambda *ops: {"h": G, "openings": list(ops)}           # (the crypt's storey of a wall standing from the ground)
cwin = lambda at: arch(at, 1.2, 1.6, 3.4)                         # (a crypt window: low, as the saut-de-loup lights it)

# ==== THE CROSS ======================================================================================================
# ---- the crossing's four piers, from the crypt to the wall heads
add("crossing piers", {"type": "box", "width": WT, "length": WT, "height": L2, "at": [[sx * (A + WT / 2), 0, sz * (A + WT / 2), 0] for sx in (-1, 1) for sz in (-1, 1)],
                       "_about": "the four piers of the crossing, 2.85 m square, from the crypt to the roofs: the great arches and the pendentives stand on them"})

# ---- the arms' side walls: arcades into the corner bays and the aisles beyond, the crypt's arches under them; over the
# aisles' roofs blind (the barrels' haunches are behind them)
CB = (W + CQ) / 2                          # the corner bays' middles (along the arm)
def arm_side(name, lo, hi, about=None):
    """the arm's side wall's openings from the crossing (|lo| = W) out to `hi`: the corner bay's arch, the aisle's beyond"""
    s = 1 if hi > 0 else -1
    a1 = s * (W + CQ - CT) / 2             # (the corner bay, between the arm's wall and its own outer wall)
    a2 = s * (CQ + abs(hi)) / 2
    w2 = min(5.6, abs(hi) - CQ - 1.6)
    return [CRYPT(arch(a1, 4.0, 0, 2.4, False), *( [arch(a2, min(3.4, w2), 0, 2.4, False)] if w2 > 1.2 else [])),
            {"h": L1 - G, "openings": [arch(a1, 6.4, 0, 8.5, False)] + ([arch(a2, w2, 0, 8.0, False)] if w2 > 1.2 else [])},
            {"h": L2 - L1, "openings": []}]
for sx, nm in SIDES:
    xa, xb = (A, W) if sx > 0 else (-W, -A)
    wall_z(f"nave {nm} wall", xa, xb, W, ZF, arm_side("n", W, ZF), about="the nave arm's side walls, 2.85 m: an arch into the corner bay under its small dome and one into the aisle beyond; the crypt's arches under them" if sx > 0 else None)
    wall_z(f"choir {nm} wall", xa, xb, ZA, -W, arm_side("c", -W, ZA - 0.0))
    za, zb = (A, W) if sx > 0 else (-W, -A)
    wall_x(f"transept {'south' if sx > 0 else 'north'} walls", za, zb, W, XT, arm_side("t", W, XT))
    wall_x(f"transept {'south' if sx > 0 else 'north'} walls west", za, zb, -XT, -W, arm_side("t", -W, -XT))

# ---- the arms' end walls: the front (three doors behind the porch, the great window, the gable over it); the transepts'
# (a pair of tall windows, the rose in the lunette under the vault)
wall_x("front wall", ZF, ZF + 1.3, -W, W,
       [{"h": G, "openings": []},
        {"h": 9.5, "openings": [arch(0, 3.0, 0, 4.4, False), arch(-5.3, 2.2, 0, 3.6, False), arch(5.3, 2.2, 0, 3.6, False)]},
        {"h": L2 - G - 9.5, "openings": [arch(0, 6.0, 2.0, 8.6)]}],
       about="the front: three doors from the porch into the nave, the great window over the porch's roof, the gable over it all")
for sx, nm in SIDES:
    xa, xb = (XT, XT + 1.3) if sx > 0 else (-XT - 1.3, -XT)
    wall_z(f"{nm} transept front", xa, xb, -W, W,
           [CRYPT(cwin(-4.5), cwin(4.5)),
            {"h": L1 - G, "openings": [arch(-4.5, 2.6, 3.5, 10.6), arch(4.5, 2.6, 3.5, 10.6)]},
            {"h": L2 - L1, "openings": [{"at": 0, "width": 5.6, "sill": 3.9, "springing": 3.9, "head": ROUND, "foot": ROUND, "tracery": True}]}],
           about="the transepts' fronts: two tall windows, and the rose in the lunette under the barrel" if sx > 0 else None)

# ---- the vaults: the arms' barrels (their first bays the crossing's great arches), the pendentives and the deck round the drum
add("arm barrels", {"type": "barrel", "width": 2 * A, "length": ZF - A, "springing": SPR, "top": L2, "head": ROUND, "at": [[0, 0, ZF, 0]],
                    "_about": "the barrel vault over each arm, from the crossing (its first bay the great arch) to the arm's end"})
add("choir barrel", {"type": "barrel", "width": 2 * A, "length": -ZA - A, "springing": SPR, "top": L2, "head": ROUND, "at": [[0, 0, -A, 0]]})
add("transept barrels", {"type": "barrel", "width": 2 * A, "length": XT - A, "springing": SPR, "top": L2, "head": ROUND, "at": [[XT, 0, 0, Q], [-A, 0, 0, Q]]})
add("pendentives", {"walked": True, "type": "pendentives", "span": 2 * A, "springing": SPR, "sides": 16, "at": [[0, 0, 0, 0]], "deck": {"thickness": 0.8, "out": WT},
                    "_about": "the pendentives turning the crossing's square into the drum's circle, and the deck round the drum's foot: the roof walk between the four arms' gables"})
# the arms' gabled roofs: their eaves on the walls' inner halves, the outer halves (1.2 m) the gutter walk along each wall head
EAVE = A + 1.65
PITCH = round(math.degrees(math.atan(9.0 / EAVE)), 2)       # (eaves 24 m, ridges 33 m: OSM)
add("nave roof", {"type": "roof", "form": "gable", "width": 2 * EAVE, "length": ZF + 1.3 - W, "pitch": PITCH, "overhang": 0, "at": [[0, L2, (ZF + 1.3 + W) / 2, 0]],
                  "_about": "the arms' gabled roofs in stone, from the drum's deck out to the gables; between their eaves and the wall heads' outer edges the gutter walk"})
add("choir roof", {"type": "roof", "form": "gable", "width": 2 * EAVE, "length": -ZA - W, "pitch": PITCH, "overhang": 0, "at": [[0, L2, (ZA - W) / 2, 0]]})
add("transept roofs", {"type": "roof", "form": "gable", "width": 2 * EAVE, "length": XT + 1.3 - W, "pitch": PITCH, "overhang": 0,
                       "at": [[sx * (XT + 1.3 + W) / 2, L2, 0, Q] for sx in (-1, 1)]})

# ==== THE CORNER BAYS: a tower in each angle of the cross, open below to the arms and the aisles, a sail vault inside, its
# head a terrace with the octagonal drum, the egg dome and the lantern on it (OSM: the 24 m squares, the 33 m drums, the domes 46 m)
CI = CQ - CT
for sz, zn in ((1, "front"), (-1, "back")):
    for sx, xn in SIDES:
        nm = f"{zn} {xn} corner"
        xa, xb = (CI, CQ) if sx > 0 else (-CQ, -CI)
        za, zb = (CI, CQ) if sz > 0 else (-CQ, -CI)
        mid = (W + CI) / 2
        tiers = [CRYPT(arch(0, 3.2, 0, 2.4, False)), {"h": L1 - G, "openings": [arch(0, 6.0, 0, 8.4, False)]}, {"h": L2 - L1, "openings": []}]
        wall_z(f"{nm} side", xa, xb, min(sz * W, sz * CQ), max(sz * W, sz * CQ), [{**t, "openings": [{**o, "at": sz * mid} for o in t["openings"]]} for t in tiers],
               about="each corner tower's two outer walls: a great arch into the aisle beyond, blind over the aisles' roofs" if sx > 0 and sz > 0 else None)
        wall_x(f"{nm} end", za, zb, min(sx * W, sx * CI), max(sx * W, sx * CI), [{**t, "openings": [{**o, "at": sx * mid} for o in t["openings"]]} for t in tiers])
add("corner vaults", {"type": "pendentives", "sail": True, "span": r3(CI - W), "springing": 14.0, "sides": 16,
                      "at": [[sx * (W + CI) / 2, 0, sz * (W + CI) / 2, 0] for sx in (-1, 1) for sz in (-1, 1)],
                      "_about": "the sail vault over each corner bay"})
add("corner towers", {"flatRoof": True, "type": "box", "width": r3(CQ - W), "length": r3(CQ - W), "height": L2 - 20.0,
                      "at": [[r3(sx * (W + CQ) / 2), 20.0, r3(sz * (W + CQ) / 2), 0] for sx in (-1, 1) for sz in (-1, 1)],
                      "_about": "the corner towers' masonry over their vaults, up to the terrace the small domes stand on"})
CD = (W + CQ) / 2
add("small domes", comp("components/drum-dome", {"R": 3.9, "dt": 0.6, "H": 9.0, "n": 8, "every": 1, "winW": 1.1, "winSill": 2.6, "winH": 3.8,
                                                  "profile": "pointed", "spread": 2.3, "domeT": 0.4, "ribsN": 8, "ribW": 0.3, "lanternR": 1.0, "lanternH": 4.2, "lanternSides": 8},
                        [[r3(sx * CD), L2, r3(sz * CD), 0] for sx in (-1, 1) for sz in (-1, 1)],
                        build=["drum", "dome", "ribs", "ribbed lantern", "lantern columns", "lantern spire", "lantern ball", "lantern cross", "lantern cross arm"],
                        _about="the four small domes over the corner towers: an octagonal drum with an arch in every face, the ribbed egg dome, the lantern and its cross (OSM: drums to 33 m, domes to 46 m, lanterns to 53 m)"))

# ==== THE GREAT DOME ===============================================================================================
DR, DT = A, 1.6                              # the drum's inside (the pendentives' circle) and its wall
DY = SPR + A                                 # the pendentives' crown: the drum's foot
GAL = 48.5                                   # the galleries' floor at the drum's head
ATT = 5.8                                    # the gallery storey, up to the dome's springing (54.3)
add("dome", comp("components/drum-dome", {"R": DR, "dt": DT, "H": r3(GAL - DY), "n": 16, "every": 1, "winW": 1.6, "winSill": 10.6, "winH": 6.4,
                                          "profile": "pointed", "spread": 2.1, "domeT": 0.9, "ribsN": 16, "ribW": 0.55, "atticH": ATT,
                                          "lanternR": 1.9, "lanternH": 7.2, "lanternSides": 8},
                 [[0, DY, 0, 0]], build=["drum", "dome", "ribs", "ribbed lantern", "lantern columns", "lantern spire", "lantern ball", "lantern cross", "lantern cross arm"],
                 _about="the great drum, sixteen tall windows over the roofs, the egg dome on its gallery storey with sixteen ribs, the colonnaded lantern, ball and cross (OSM: the dome 50-73 m, the lantern to 83 m)"))
# the drum's last storey, the galleries: inside a ring walked round the drum, outside a ring walked behind an open arcade,
# a door between them; the second stair turret against the drum's south-west comes up into the outer one
TB = 225.0                                   # (the turret's bearing from the dome's middle: back west, over a crossing pier)
TR, TRAD = 1.9, 11.3                         # its radius, its middle's distance from the dome's
DOOR_BAY = 9                                 # (the gallery storey's door: the bay of 16 next to the turret's door out)
add("gallery storey", {"type": "ring", "count": 16, "rOuter": DR + DT, "rInner": DR, "height": ATT, "y": GAL, "turn": 0.5, "skip": [DOOR_BAY],
                       "opening": {"width": 1.3, "sill": 1.1, "springing": 3.6, "head": ROUND}, "place": [[0, 0, 0, 0]],
                       "_about": "the drum's gallery storey under the dome: a window in every bay but one"})
add("gallery storey door", {"type": "ring", "count": 16, "rOuter": DR + DT, "rInner": DR, "height": ATT, "y": GAL, "turn": 0.5, "at": [DOOR_BAY], "glass": False,
                            "opening": {"width": 1.2, "sill": 0, "springing": 2.6, "head": ROUND}, "place": [[0, 0, 0, 0]],
                            "_about": "...and the door from the outer gallery to the inner one"})
add("inner gallery", {"walked": True, "type": "ring", "count": 16, "rOuter": DR, "rInner": DR - 1.4, "height": 0.6, "y": GAL - 0.6, "turn": 0.5, "solid": True, "place": [[0, 0, 0, 0]],
                      "_about": "the inner gallery round the drum's foot of the dome, 54 m over the church's floor"})
SKIP_DECK = round(TB / 15) % 24
add("outer gallery", {"walked": True, "type": "ring", "count": 24, "rOuter": 12.4, "rInner": DR + DT, "height": 0.6, "y": GAL - 0.6, "turn": 0, "solid": True, "skip": [SKIP_DECK],
                      "place": [[0, 0, 0, 0]], "_about": "the outer gallery round the drum, walked behind its arcade (the stair turret stands in one bay of it)"})
ARC_SKIP = [k for k in range(48) if abs(((k + 0.5) * 7.5 - TB + 180) % 360 - 180) < 9.0]
add("gallery arcade", {"type": "ring", "count": 48, "rOuter": 12.4, "rInner": 12.0, "height": 5.4, "y": GAL, "turn": 0.5, "glass": False, "skip": ARC_SKIP,
                       "opening": {"width": 1.0, "sill": 1.0, "springing": 3.6, "head": ROUND}, "place": [[0, 0, 0, 0]],
                       "_about": "the open arcade round the outer gallery, its sills the parapet"})
add("gallery roof", {"type": "ring", "count": 24, "rOuter": 13.3, "rInner": DR + DT, "height": 0.4, "y": GAL + 5.4, "turn": 0, "solid": True, "flatRoof": True,
                     "place": [[0, 0, 0, 0]], "_about": "the cornice over the arcade, the gallery's ceiling: the dome stands behind it"})
add("gallery interior", {"type": "interior", "plan": {"sides": 16, "radius": DR + DT / 2}, "height": ATT, "at": [[0, GAL, 0, 0]],
                         "_about": "the gallery storey's space, up to the dome's springing"})
tx, tz = TRAD * math.sin(math.radians(TB)), TRAD * math.cos(math.radians(TB))
# (eight bays: the door out onto the deck in bay 5, facing away from the drum; 99 steps of 20 cm bring its landing round to
#  bay 3, the door into the outer gallery beside the gallery storey's door)
add("dome stair", comp("components/round-stair-tower", {"R": TR, "wall": 0.35, "H": r3(GAL - L2), "n": 8, "steps": 99, "doorBay": 5, "stageH": 5.4,
                                                        "doorW": 1.2, "archW": 1.0, "newel": 0.2},
                       [[r3(tx), L2, r3(tz), 0]], build=["shaft", "shaft door", "stair", "belvedere", "belvedere door"],
                       _about="the stair turret against the drum, over the south-west crossing pier: from the deck round the drum's foot up to the outer gallery"))

# ==== THE AISLES: the low storey round the cross (OSM's 16 m outline), its outer walls from the ground (the crypt's lights low
# in them), the flat roofs over them; behind the back corner towers the choir aisles' higher masonry, a terrace on top
def owin(n, w, gap, sill, spring):
    return {"pattern": str(n), "width": w, "gap": gap, "sill": sill, "springing": spring, "head": ROUND}
def outer(name, kind, a, b, lo, hi, n=1, about=None, door=False):
    """an outer wall of the aisles from the ground to their roof: n windows, the crypt's lights under them"""
    L = hi - lo; mid = (lo + hi) / 2
    pos = [mid + (i - (n - 1) / 2) * L / n for i in range(n)]
    crypt = [cwin(p) for p in pos]
    if door: crypt = [arch(mid, 1.6, 0, 2.6, False)] + [cwin(p) for p in pos if abs(p - mid) > 2.0]
    tiers = [CRYPT(*crypt), {"h": L1 - G, "openings": [arch(p, 2.4 if L / n > 4 else 1.8, 3.2, 10.4) for p in pos]}]
    return (wall_x if kind == "x" else wall_z)(name, a, b, lo, hi, tiers, about=about)
for sx, nm in SIDES:
    s = sx
    def span(a, b): return (min(s * a, s * b), max(s * a, s * b))
    outer(f"{nm} front aisle front", "x", 25.2 - OT, 25.2, *span(W, 20.3), n=2,
          about="the aisles' outer walls, from the ground to their flat roofs: tall round-headed windows, the crypt's small lights under them" if sx > 0 else None)
    outer(f"{nm} front aisle side", "z", *span(20.3 - OT, 20.3), 20.5, 25.2)
    outer(f"{nm} transept aisle front", "x", 20.5 - OT, 20.5, *span(20.3, 25.0))
    outer(f"{nm} transept aisle south", "z", *span(25.0 - OT, 25.0), W, 20.5, n=2)
    outer(f"{nm} transept aisle north", "z", *span(25.0 - OT, 25.0), -20.5, -W, n=2)
    outer(f"{nm} transept aisle back", "x", -20.5, -20.5 + OT, *span(21.7, 25.0))
    outer(f"{nm} choir aisle side", "z", *span(21.7 - OT, 21.7), -28.3, -20.5, n=2, door=sx < 0)
    outer(f"{nm} choir aisle back", "x", -28.3 - OT, -28.3, *span(18.2, 21.7))
    outer(f"{nm} choir aisle end", "z", *span(18.2 - 1.2, 18.2), ZA, -28.3 - OT)
    # the aisles' flat roofs (seen from the terraces, not walked) and the choir aisles' masonry over them, its top walked
    for k, (x0, x1, z0, z1) in enumerate([(W, 20.3, CQ, 25.2), (CQ, 25.0, W, 20.5), (CQ, 25.0, -20.5, -W), (W, 21.7, -28.3, -CQ), (W, 18.2, ZA, -28.3)]):
        a, b = span(x0, x1)
        box(f"{nm} aisle roof {k + 1}", a, b, z0, z1, L1 - 0.6, L1, flatRoof=True,
            about="the aisles' flat roofs, over their ceilings" if sx > 0 and k == 0 else None)
    a, b = span(W, 18.2)
    box(f"{nm} choir aisle terrace", a, b, ZA, -CQ, L1, L2, walked=True,
        about="the choir aisles' upper masonry behind the back corner towers (OSM's 24 m block), its top a terrace walked from the stair turret to the gutter walks and round the apse" if sx > 0 else None)

# ==== THE CHOIR'S END: the apse (its half dome the great mosaic), the ambulatory round it, the seven chapels
NA = 14
HALF = list(range(4, 11))                   # (the bays of 14 facing back: 90 to 270 degrees)
APL = [[0, 0, ZA, 0]]
RA0, RA1 = A, W - 0.25                      # the apse's wall: its inside the choir's, its outside under the arms' wall heads
RM0, RM1 = 17.0, 18.2                       # the ambulatory's outer wall (OSM's 24 m ring, ~18 m round the apse's middle)
ring = lambda name, ro, ri, h, y, **kw: add(name, {"type": "ring", "count": NA, "rOuter": ro, "rInner": ri, "height": r3(h), "y": r3(y), "turn": 0, "at": HALF, "place": APL, **kw})
ring("apse crypt", RA1, RA0, G, 0, glass=False, opening={"width": 2.4, "sill": 0, "springing": 2.4, "head": ROUND},
     _about="the apse's wall in the crypt, arched into the crypt's ambulatory")
ring("apse arcade", RA1, RA0, 10.0, G, glass=False, opening={"width": 2.8, "sill": 0, "springing": 7.4, "head": ROUND},
     _about="the apse's arcade into the ambulatory, an arch a bay")
ring("apse upper wall", RA1, RA0, SPR - G - 10.0, G + 10.0, solid=True, _about="the apse's wall over the arcade, up to the half dome")
add("apse half dome", {"type": "dome", "sweep": 0.5, "sides": NA, "radius": RA1, "thickness": r3(RA1 - RA0), "head": ROUND, "at": [[0, SPR, ZA, PI]],
                       "_about": "the apse's half dome, its crown the choir barrel's: inside, the great mosaic of Christ in Majesty"})
add("apse roof", {"type": "dome", "sweep": 0.5, "sides": NA, "radius": W + 0.15, "thickness": 0, "head": {"profile": "trigonal", "rise": 9.0}, "at": [[0, L2, ZA, PI]],
                  "_about": "the half-cone stone roof over the apse, to the choir roof's ridge"})
add("ambulatory vault", {"type": "vault", "count": NA, "rOuter": RM0, "rInner": RA1, "springing": 13.0, "top": 17.0, "head": ROUND, "at": HALF, "place": APL,
                         "_about": "the ambulatory's barrel vault, round the apse"})
ring("ambulatory upper", RM0, RA1, L2 - 0.4 - 17.0, 17.0, solid=True, _about="the masonry over the ambulatory's vault (the gallery storey of OSM's 24 m ring)")
ring("ambulatory roof", RM1, RA1, 0.4, L2 - 0.4, solid=True, walked=True, _about="the ambulatory's flat roof, walked round the apse")
ring("ambulatory wall", RM1, RM0, L2 - 0.4, 0, glass=False, opening={"width": 4.0, "sill": 0, "springing": G + 8.0, "head": ROUND},
     _about="the ambulatory's outer wall: an arch into each chapel (and in the crypt, into the crypt's chapels under them)")
add("ambulatory crypt floor", {"type": "ring", "count": NA, "rOuter": RM1, "rInner": RA0, "height": 0.6, "y": G - 0.6, "turn": 0, "at": HALF, "place": APL, "solid": True,
                               "walked": True, "_about": "the floor of the ambulatory and the apse over the crypt"})
CH_R, CH_T, CH_C = 3.2, 0.8, RM1 - 0.6
chapels = [b for b in HALF if b != 7]
CHAT = [[r3(CH_C * math.sin(b * 2 * PI / NA)), 0, r3(ZA + CH_C * math.cos(b * 2 * PI / NA)), r3(b * 2 * PI / NA)] for b in chapels]
add("crypt chapels", comp("components/apse", {"R": CH_R, "T": CH_T, "H": G - 0.6, "n": 12, "winW": 0.8, "winSill": 1.6, "winH": 1.6}, CHAT, build=["walls"],
                          _about="the crypt's six chapels under the church's"))
add("chapels", comp("components/apse", {"R": CH_R, "T": CH_T, "H": 11.2, "n": 12, "winW": 1.1, "winSill": 3.8, "winH": 4.4, "domeT": CH_T},
                    [[x, G, z, a] for x, _, z, a in CHAT], build=["walls", "half dome"],
                    _about="the six radiating chapels round the ambulatory, each a half round of windows under its stone half dome (the seventh, the axial one, is the campanile's foot)"))
add("chapel floors", {"type": "prism", "walked": True, "plan": {"points": arc(0, 0, CH_R + CH_T / 2, -90, 90, 12)},
                      "height": 0.6, "at": [[x, G - 0.6, z, a] for x, _, z, a in CHAT], "_about": "the chapels' floors over the crypt's"})

# ==== THE CAMPANILE (84 m, 91 with its cross): behind the apse, its foot the axial chapel; a long shaft of narrow lights,
# the belfry of the Savoyarde (three open arches a face), a smaller arcaded stage, a little drum and egg dome, lantern, cross
CW, CL = 13.2, 12.7
CZ = ZA - RM0 - CL / 2 + 0.6                # (its front wall the ambulatory's, in the axial bay)
CB_Y, CS_Y = 44.0, 57.5                     # the belfry's floor, the shaft's head
cface = lambda front: [{"h": G, "openings": [arch(0, 2.2, 0, 2.4, False)] if front else [cwin(0)]},
                       {"h": 12.0, "openings": [arch(0, 4.0, 0, 8.0, False)] if front else [arch(0, 2.4, 3.0, 8.6)]},
                       {"h": CB_Y - G - 12.0, "openings": owin(2, 1.0, 2.8, 8.0, 19.0)},
                       {"openings": owin(3, 2.3, 1.0, 1.4, 9.6), "glass": False}]
add("campanile", {"type": "enclosure", "plan": {"rect": [CW, CL]}, "thickness": 1.2, "height": CS_Y, "at": [[0, 0, r3(CZ), 0]],
                  "tiers": cface(False), "faces": {"0": cface(True)}, "glass": True, "courses": {"strings": [G + 12.0, CB_Y]},
                  "_about": "the campanile's square shaft: the axial chapel at its foot (the arch from the ambulatory), the long shaft of paired lights, the open belfry"})
add("campanile chapel ceiling", {"type": "box", "width": CW - 2.4, "length": CL - 2.4, "height": 0.8, "at": [[0, G + 12.0, r3(CZ), 0]], "_about": "the axial chapel's ceiling"})
add("campanile floor", {"type": "box", "walked": True, "width": CW - 2.4, "length": CL - 2.4, "height": 0.6, "at": [[0, G - 0.6, r3(CZ), 0]]})
add("belfry floor", {"type": "box", "flatRoof": True, "width": CW - 2.4, "length": CL - 2.4, "height": 0.6, "at": [[0, CB_Y - 0.6, r3(CZ), 0]], "_about": "the belfry's floor"})
add("savoyarde", {"type": "dome", "sides": 24, "radius": 1.55, "thickness": 0, "head": {"profile": "bell", "waist": 0.62, "lift": 1.0}, "at": [[0, CB_Y + 2.2, r3(CZ), 0]],
                  "_about": "La Savoyarde, the great bell (18.8 t, 3 m across), hung in the belfry"})
add("bell frame", {"type": "box", "width": 5.0, "length": 0.6, "height": 0.6, "at": [[0, CB_Y + 5.6, r3(CZ), 0]]})
add("bell posts", {"type": "box", "width": 0.5, "length": 0.6, "height": 5.6, "at": [[sx * 2.3, CB_Y, r3(CZ), 0] for sx in (-1, 1)]})
add("campanile buttresses", {"type": "column", "radius": 1.0, "height": CS_Y, "sides": 8, "at": [[sx * (CW / 2 - 0.15), 0, r3(CZ + sz * (CL / 2 - 0.15)), r3(PI / 8)] for sx in (-1, 1) for sz in (-1, 1)],
                             "_about": "the buttresses at its corners, running up into pinnacles"})
add("campanile cornice", {"type": "box", "width": CW + 1.6, "length": CL + 1.6, "height": 1.0, "flatRoof": True, "at": [[0, CS_Y, r3(CZ), 0]], "_about": "the belfry's cornice"})
add("campanile pinnacles", {"type": "pinnacle", "w": 1.4, "h": 2.0, "s": 4.0, "sides": 8, "at": [[sx * (CW / 2 - 0.15), CS_Y + 1.0, r3(CZ + sz * (CL / 2 - 0.15)), 0] for sx in (-1, 1) for sz in (-1, 1)]})
CU = 9.0
add("campanile stage", {"type": "enclosure", "plan": {"rect": [CU, CU]}, "thickness": 0.9, "height": 9.0, "at": [[0, CS_Y + 1.0, r3(CZ), 0]], "glass": False,
                        "openings": owin(3, 1.4, 0.9, 1.2, 5.6), "_about": "the arcaded stage over the belfry"})
add("campanile stage cornice", {"type": "box", "width": CU + 1.0, "length": CU + 1.0, "height": 0.7, "flatRoof": True, "at": [[0, CS_Y + 10.0, r3(CZ), 0]]})
add("campanile dome", comp("components/drum-dome", {"R": 3.2, "dt": 0.5, "H": 3.4, "n": 8, "every": 1, "winW": 0.9, "winSill": 0.6, "winH": 1.8,
                                                    "profile": "pointed", "spread": 1.4, "domeT": 0.3, "ribsN": 8, "ribW": 0.25, "lanternR": 0.85, "lanternH": 3.4, "lanternSides": 8},
                           [[0, CS_Y + 10.7, r3(CZ), 0]], build=["drum", "dome", "ribs", "ribbed lantern", "lantern columns", "lantern spire", "lantern ball", "lantern cross", "lantern cross arm"],
                           _about="its little drum and egg dome, the lantern and the cross"))
add("campanile interior", {"type": "interior", "plan": {"rect": [CW - 1.2, CL - 1.2]}, "height": 12.0, "at": [[0, G, r3(CZ), 0]], "_about": "the axial chapel in the campanile's foot"})

# ==== THE FRONT: the porch of three arches on the parvis, the equestrian saints on its corners; the turrets beside the gable,
# the Sacred Heart in his niche on it; the terrace and its flight
ZP = 33.3                                   # the porch's front (OSM)
PH = 9.0                                    # the arcade's height over the floor
box("porch floor", -9.6, 9.6, ZF + 1.3, ZP, 0, G, walked=True, about="the porch's floor, a step over the parvis")
wall_x("porch arcade", ZP - 1.5, ZP, -9.6, 9.6, [{"h": PH, "openings": [arch(0, 3.8, 0, 5.0, False), arch(-5.75, 3.8, 0, 5.0, False), arch(5.75, 3.8, 0, 5.0, False)]}], y=G,
       about="the porch: three round arches on the parvis (after Saint-Front at Perigueux)")
for sx, nm in SIDES:
    xa, xb = (8.1, 9.6) if sx > 0 else (-9.6, -8.1)
    wall_z(f"porch {nm} side", xa, xb, ZF + 1.3, ZP - 1.5, [{"h": PH, "openings": [arch((ZF + 1.3 + ZP - 1.5) / 2, 1.6, 0, 3.4, False)]}], y=G)
box("porch roof", -9.6, 9.6, ZF + 1.3, ZP, G + PH, G + PH + 0.8, flatRoof=True, about="the porch's roof, a terrace behind its balustrade")
add("porch balustrade", {"type": "wall", "width": 19.2, "thickness": 0.4, "height": 1.1, "at": [[0, G + PH + 0.8, ZP, 0]],
                         "openings": {"pattern": "15", "width": 0.7, "gap": 0.5, "sill": 0.25, "springing": 0.85, "head": {"profile": "flat"}}, "glass": False,
                         "_about": "the balustrade along the porch's roof"})
SP = G + 12.0                                # (OSM: the statues' piers 13 m)
box("statue piers", -9.6, -7.65, ZF + 1.3, ZP, G, SP, about="the porch's corner piers, rising over its roof to carry the two equestrian statues")
box("statue piers east", 7.65, 9.6, ZF + 1.3, ZP, G, SP)
add("statue plinths", {"type": "box", "width": 2.4, "length": 3.6, "height": 0.6, "at": [[sx * 8.625, SP, 32.1, 0] for sx in (-1, 1)],
                          "_about": "the statues' plinths, run forward of the piers clear of the turrets behind"})
for sx, saint, kind, seed in ((-1, "saint louis", "man", 31), (1, "joan of arc", "woman", 12)):
    add(f"{saint}", comp("components/equestrian", {"S": 1.5, "kind": kind, "seed": seed, "pose": "enthroned", "stone": "bronze", "style": "gothic", "holdR": "items/weapons/sword"},
                         [[sx * 8.625, SP + 0.6, 32.0, 0]],
                         _about=("the bronze equestrian statues by Hippolyte Lefebvre on the porch's corners: Saint Louis to the west (left as one faces the front), sword raised"
                                 if sx < 0 else "Joan of Arc to the east, sword raised")))
add("facade turrets", {"type": "column", "radius": 1.15, "height": 33.0, "sides": 8, "at": [[sx * 9.0, 0, 29.1, r3(PI / 8)] for sx in (-1, 1)],
                       "_about": "the slender turrets either side of the gable, their small domes over the roof's eaves (OSM: 33 m)"})
add("facade turret domes", {"type": "dome", "sides": 8, "radius": 1.35, "thickness": 0, "head": {"profile": "pointed", "spread": 1.2}, "at": [[sx * 9.0, 33.0, 29.1, 0] for sx in (-1, 1)]})
add("facade turret finials", {"type": "pinnacle", "w": 0.35, "h": 0.4, "s": 1.6, "sides": 8, "at": [[sx * 9.0, 36.2, 29.1, 0] for sx in (-1, 1)]})
box("sacred heart niche", -2.9, 2.9, ZF + 1.3, ZF + 2.6, L2 + 0.4, L2 + 8.4, about="the aedicule on the gable, the Sacred Heart standing before it (OSM: 35.5 m)")
add("sacred heart niche roof", {"type": "roof", "form": "gable", "width": 6.4, "length": 1.8, "pitch": 32, "overhang": 0.1, "at": [[0, L2 + 8.4, ZF + 1.95, 0]]})
box("sacred heart ledge", -1.6, 1.6, ZF + 2.6, ZF + 3.5, L2 + 0.4, L2 + 0.9)
add("sacred heart", {"type": "marker", "role": "statue", "at": [[0, L2 + 0.9, r3(ZF + 3.05), 0]],
                     "data": {"kind": "man", "pose": "blessing", "style": "roman", "stone": "limestone", "scale": 2.4, "seed": 7, "face": -1.5707963},
                     "_about": "Christ of the Sacred Heart blessing, over the front"})
# the parvis terrace on its arches, and the flights
ZT = 48.0
box("parvis", -24.0, 24.0, ZP, ZT, 0, G - 1.0, walked=True, about="the parvis before the porch, a terrace over the hill on blind arches")
add("porch steps", {"type": "flight", "width": 19.2, "run": 0.34, "rise": 0.17, "base": G - 1.0, "top": G, "landing": 0, "at": [[9.6, 0, r3(ZP + 6 * 0.34), Q]],
                    "_about": "the steps from the parvis up to the porch"})
add("great flight", {"type": "flight", "width": 14.0, "run": 0.36, "rise": 0.167, "base": 0, "top": G - 1.0, "landing": 0, "at": [[7.0, 0, r3(ZT + 27 * 0.36), Q]],
                     "_about": "the broad flight from the hill up to the parvis"})

# ==== THE CLIMB: the stair turret in the back west angle, its bridge to the choir aisle terrace
TAx, TAz = -24.75, -24.4
add("roof stair", comp("components/round-stair-tower", {"R": 2.4, "wall": 0.5, "H": L2, "n": 12, "steps": 156, "doorBay": 9, "stageH": 3.2, "capRise": 3.6},
                       [[TAx, 0, TAz, 0]],
                       _about="the stair turret in the back west angle, its door to the west at the ground: 156 steps up to the high terraces, its belvedere and cone over them"))
box("roof stair bridge", TAx + 2.4 - 0.2, -18.2, TAz - 0.9, TAz + 0.9, L1, L2, walked=True, about="the bridge from the turret's door over the aisle's roof to the choir aisle terrace")

# ==== THE FLOORS, THE CRYPT, THE INSIDE
LOW = mirror_x([[0, ZF + 0.65], [W, ZF + 0.65], [W, 25.2 - OT / 2], [20.3 - OT / 2, 25.2 - OT / 2], [20.3 - OT / 2, 20.5 - OT / 2], [25.0 - OT / 2, 20.5 - OT / 2],
                [25.0 - OT / 2, -20.5 + OT / 2], [21.7 - OT / 2, -20.5 + OT / 2], [21.7 - OT / 2, -28.3 - OT / 2], [18.2 - 0.6, -28.3 - OT / 2]]
               + arc(0, ZA, (RM0 + RM1) / 2, 90, 180, 8))
LOW = [[r3(x), r3(z)] for x, z in LOW]
add("church floor", {"type": "prism", "walked": True, "plan": {"points": LOW}, "height": 0.6, "at": [[0, G - 0.6, 0, 0]],
                     "_about": "the church's floor over the crypt"})
add("crypt floor", {"type": "prism", "walked": True, "plan": {"points": LOW}, "height": 0.05, "at": [[0, 0, 0, 0]], "_about": "the crypt's floor"})
cp = [[x, z] for x in (-4.0, 4.0) for z in (12.5, 18.0, 23.0, -13.0, -19.0, -25.0)] + [[x, z] for x in (13.0, 18.0, -13.0, -18.0) for z in (-4.0, 4.0)] + \
     [[x, z] for x in (-4.0, 4.0) for z in (-4.0, 4.0)] + [[sx * 15.0, sz * 15.0] for sx in (-1, 1) for sz in (-1, 1)]
add("crypt piers", {"type": "column", "radius": 0.6, "height": G - 0.6, "sides": 8, "at": [[x, 0, z, r3(PI / 8)] for x, z in cp],
                    "_about": "the crypt's piers under the church's floor"})
add("crypt interior", {"type": "interior", "plan": {"points": LOW}, "height": G - 0.6, "at": [[0, 0, 0, 0]], "_about": "the crypt: the church's plan a storey down"})
add("church interior", {"type": "interior", "plan": {"points": LOW}, "height": L1 - G, "at": [[0, G, 0, 0]],
                        "_about": "the church up to the aisles' roofs: the cross, the corner bays, the aisles, the choir aisles and the ambulatory (the chapels' and the apse's own above)"})
M = W - WT / 2
CROSS = [[M, ZF + 0.65], [-M, ZF + 0.65], [-M, M], [-(XT + 0.65), M], [-(XT + 0.65), -M], [-M, -M], [-M, ZA], [M, ZA], [M, -M], [XT + 0.65, -M], [XT + 0.65, M], [M, M]]
add("nave interior", {"type": "interior", "plan": {"points": [[r3(x), r3(z)] for x, z in CROSS]}, "height": r3(DY - L1), "at": [[0, L1, 0, 0]],
                      "_about": "the arms over the aisles' roofs, under their barrels, to the pendentives' ring"})

doc = {"name": "Sacre-Coeur",
       "_about": "THE BASILICA OF SACRE-COEUR, Montmartre (Abadie, 1875-1914), Romano-Byzantine in white travertine, on its real plan (OSM building parts, Wikipedia): the Greek cross of four barrel-vaulted, gabled arms round the 16 m crossing, PENDENTIVES carrying the great drum of sixteen windows, the gallery storey with its open arcade and the tall ribbed egg dome with its colonnaded lantern and cross (~87 m); the four corner towers over sail-vaulted bays, each with its octagonal drum, small egg dome and lantern; the low aisles round it under flat roofs; the long choir, the APSE with its half dome (the mosaic of Christ in Majesty), the ambulatory and six half-domed radiating chapels; the square CAMPANILE behind (the axial chapel at its foot, the Savoyarde in its belfry, a small dome and cross); the three-arched PORCH with the bronze equestrian statues of Saint Louis and Joan of Arc, the Sacred Heart on the gable, the parvis and its flight; the CRYPT under all of it. A stair turret in the back west angle climbs to the high terraces, the gutter walks lead to the deck round the drum, and a second turret against the drum to the outer and inner GALLERIES at the dome's foot.",
       "params": {"detail": 4}, "railing": {"type": "balusters"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/sacre-coeur.json"), "w").write(json.dumps(doc, indent=2) + "\n")

# ==== THE FINISH
fin = {"name": "Sacre-Coeur", "building": "architecture/sacre-coeur",
       "_about": "Sacre-Coeur: white Chateau-Landon travertine everywhere outside, the domes and the stone roofs too (it whitens in the rain); the two saints in bronze; inside, pale stone, marble floors, the apse's half dome the great gold and blue mosaic of Christ in Majesty, gold mosaic in the choir's barrel; the windows stained glass, the roses wheels.",
       "stone": {"color": "#f1eee6", "accent": "#dedad0", "pat": "ashlar"},
       "rules": [
           {"parts": "kind:railing", "pattern": "stone/ashlar fine", "palette": "carrara", "_about": "the balustrades in the same white stone"},
           {"parts": ["saint louis", "joan of arc", "savoyarde", "bell frame", "bell posts"], "pattern": "materials/metal", "palette": "bronze", "_about": "the bronzes: the saints on their horses, the great bell"},
           {"parts": ["dome/lantern cross", "dome/lantern cross arm", "dome/lantern ball"], "pattern": "roofs/gold leaf", "_about": "the gilt cross over the lantern"},
           {"parts": "apse half dome", "side": "in", "map": "meridian", "count": 2, "scale": 9.67, "offset": [0, -6.28], "pattern": "mosaic/wall deesis",
            "_about": "the apse's mosaic, Christ in Majesty with the Virgin and Saint Michael at his sides (Luc-Olivier Merson, 475 m2): the library's Deesis, one picture over the whole half dome (its inner radius 8 m: half round 25.1 m, up the meridian 12.6 m)"},
           {"parts": ["apse upper wall", "choir barrel"], "side": "in", "pattern": "mosaic/gold ground", "scale": 3.0, "_about": "gold mosaic round it"},
           {"parts": "kind:glass", "opening": "round", "map": "opening", "pattern": "glass/rose wheel", "palette": "chartres", "_about": "the transepts' roses"},
           {"parts": "kind:glass", "below": 22, "map": "opening", "pattern": "glass/saint any", "palette": "chartres", "_about": "stained glass, a saint in each light"},
           {"parts": "kind:glass", "map": "opening", "pattern": "glass/medallion stack", "palette": "chartres"},
           {"parts": ["kind:dome", "kind:roof", "kind:ribs"], "pattern": "stone/ashlar fine", "palette": "carrara", "_about": "the domes and the roofs in the white stone"},
           {"surface": ["floor", "top", "roof"], "side": "out", "pattern": "stone/ashlar fine", "palette": "carrara", "_about": "the terraces, the roofs and the parvis: the same white stone"},
           {"surface": "floor", "side": "in", "below": 1.0, "pattern": "floors/flagstones", "palette": "limestone", "_about": "the crypt's floor"},
           {"surface": "floor", "side": "in", "pattern": "floors/opus sectile", "palette": "marble-grey", "_about": "the church's floors in coloured marble"},
           {"surface": "ceiling", "side": "in", "pattern": "stone/ashlar fine", "palette": "limestone"},
           {"surface": "wall", "side": "in", "pattern": "stone/ashlar fine", "palette": "limestone", "_about": "inside, pale dressed stone"},
           {"surface": "wall", "pattern": "stone/ashlar fine", "palette": "carrara", "_about": "Chateau-Landon travertine: it whitens as it weathers"}]}
open(os.path.join(ROOT, "assets/finishes/sacre-coeur.json"), "w").write(json.dumps(fin, indent=2) + "\n")
print("sacre-coeur:", len(parts), "parts")
