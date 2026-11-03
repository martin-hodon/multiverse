# MAINZ CATHEDRAL (Hoher Dom St. Martin, 975-1239; the Gothic chapels 1278-1319, the cloister 1390-1410, the west
# tower's stone crown by Franz Ignaz Michael Neumann 1769-74), in red Main sandstone: a DOUBLE-CHOIR basilica.
# THE FRAME: +z is WEST (the west choir, the main choir), +x is SOUTH (the cloister); the nave's axis runs 12.7 degrees
# north of east, so the frame is OpenStreetMap's turned by that, its origin the nave's middle (49.99891 N, 8.27406 E, then
# 3.5 m east along the axis). THE PLAN IS OSM's (way 155551498 and its building:parts 207808988/89/91, 616585329,
# 616847752, 475948611; the cloister 100003216, the Gotthardkapelle 146459809, the Dom-Cafe 146459812 and the
# Dominformation 146459813) checked against the Commons ground plan (File:MZ_Dom_Grundriss.png), whose interior --
# piers, chapels, trefoil, crypt -- it gives where OSM has only outlines. Heights from OSM's parts (the nave and the
# transepts 42 m to the ridge, their walls 30.5, the chapels 14, the west tower's stages 56 / 62 / 66 / 72 / 75 and the
# spire to 82.5 under the 0.95 m cock, the Memorie 19, the sacristy 8) and Wikipedia (the nave 13.6 m wide, its vault
# 28 m; the trefoil 24.25 m across inside; the domes 38 and 44 m clear), the rest from photographs (Commons: the aerial
# "Mainz Luftbild - Dom & Leichhof 2008", "Cathedral (Mainz) 2"). The plan is drawn symmetric about the axis (OSM's
# north and south flanks differ by up to a metre; the mean is taken).
#   East to west: the EAST TRANSEPT (a block across the whole width) with the crossing under the octagonal EAST TOWER, its
# apse with the dwarf gallery (`gallery-apse`) and the two ROUND STAIR TOWERS (`round-stair-tower`) on its outer corners;
# the east choir raised over the five-bay hall CRYPT, two flights up from the nave either side of the crypt's door; the
# NAVE, ten round arches a side on square piers under five rib vaults (the bound system), the clerestory, the AISLES
# and beyond them the GOTHIC CHAPELS between buttresses under one copper lean-to -- in the north row the vestibule of
# the MARKTPORTAL (Willigis's bronze doors), between the two DOMHAEUSER built against it; the WEST TRANSEPT and its
# crossing under the WESTTURM -- the Romanesque octagon with its dwarf gallery, the Gothic belfry and clock, Neumann's
# balustrade, two stone stages and the stone helm, 83.5 m; the TREFOIL WEST CHOIR, a square bay raised nine steps, with
# the stalls, and three polygonal conchs, each with its dwarf gallery and a gable over it, two slender octagonal towers
# in the angles, the sacristy round its foot. South: the MEMORIE (the chapter house, one rib vault) and the CLOISTER, three
# vaulted walks round the garth, the Dommuseum's storey over them, the stair up to it; north: the GOTTHARDKAPELLE, the
# archbishop's double chapel, joined to the north transept by a passage.
import os, json, math
from historicism import block, comp, flight, r4, ROOT
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n); return n
Q = math.pi / 2
C8 = math.cos(math.pi / 8)                    # an octagon's in-radius over its circumradius
SEMI = {"profile": "semicircular"}
PTD = lambda s=1.0: {"profile": "pointed", "spread": s}
ROM = lambda n=1: {"style": "romanesque", "orders": n}
LOMBARD = {"arch": 0.8, "bay": 5.0, "lesene": 0.6}
arch = lambda z, w, spring, sill=0, head=SEMI, **kw: {"z": z, "width": w, "sill": sill, "springing": spring, "head": head, **kw}
def gspread(rise, half):                      # (a pointed arch over `half` rising `rise`: the spread that does it -- milan.py's)
    return r4(max(0.0, (rise * rise - half * half) / (2 * half * half)))

def seg(name, a, b, t, height, tiers, y=0.0, about=None, **kw):
    """a wall from a to b (x, z), its thickness straddling the line; tiers' openings `at` from the middle toward b, or by
    `z` / `x` (where along the wall). Its FRONT (lesenes, Lombard bands, surrounds) faces (-dz, dx): walking a -> b, on the left."""
    L = math.dist(a, b); dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    def at(o):
        if "z" in o: return r4((o["z"] - mz) / dz)
        if "x" in o: return r4((o["x"] - mx) / dx)
        return o.get("at", 0)
    tt = [{**t, "openings": [{**{k: v for k, v in o.items() if k not in ("z", "x")}, "at": at(o)} for o in t["openings"]]} for t in tiers]
    d = {"type": "wall", "width": r4(L), "height": height, "thickness": t, "tiers": tt,
         "at": [[r4(mx - t / 2 * dz), y, r4(mz + t / 2 * dx), r4(math.atan2(-dz, dx))]], **kw}
    if about: d["_about"] = about
    return add(name, d)
def interior(name, x0, x1, z0, z1, h, y=0.0, about=None):
    parts[name] = {"type": "interior", "plan": {"rect": [r4(x1 - x0), r4(z1 - z0)]}, "height": h, "at": [[r4((x0 + x1) / 2), y, r4((z0 + z1) / 2), 0]],
                   **({"_about": about} if about else {})}
def slab(name, x0, x1, z0, z1, top, h=0.4, walked=True, about=None, **kw):
    return add(name, {"type": "prism", "plan": {"rect": [r4(x1 - x0), r4(z1 - z0)]}, "height": h, "flatRoof": True, **({"walked": True} if walked else {}),
                      "at": [[r4((x0 + x1) / 2), r4(top - h), r4((z0 + z1) / 2), 0]], **({"_about": about} if about else {}), **kw})
def groins(name, xs, zs, w, l, spring, rise, top, along_half=None, about=None, **kw):
    """groin vaults w (x) by l (z) at every (x, z): round across, pointed along to the same crown (or round along and
    pointed across where the bay is longer than it is wide)"""
    if rise: across = along = {"profile": "segmental", "rise": rise}
    elif l <= w: across, along = SEMI, PTD(gspread(w / 2, l / 2))
    else: across, along = PTD(gspread(l / 2, w / 2)), SEMI
    return add(name, {"type": "groin", "width": r4(w), "length": r4(l), "springing": spring, "top": top, "across": across, "along": along,
                      "at": [[r4(x), 0, r4(z), 0] for x in xs for z in zs], **({"_about": about} if about else {}), **kw})

# ================================================================ THE NAVE
NX, PT = 6.8, 2.0                             # the nave's half width (13.6 m), the arcade walls
HB = NX + PT                                  # 8.8: the arcade walls' outer faces
AX = 15.3                                     # the aisles' outer walls' inner face (aisles 6.5 m)
AWX = 16.3                                    # ...and their outer face: the chapels beyond
CHX = 21.4                                    # the chapels' outer face (0.8 m walls)
ZE, ZW = -26.6, 24.8                          # the nave from the east transept's west face to the west transept's east face
BAY = 4.84                                    # the arcade's bays (OSM / the plan: piers at -20.0 ... 18.7)
Z0 = -24.84                                   # the first bay's east end (the crossing pier's respond)
zc = lambda i: Z0 + (i + 0.5) * BAY           # bay i's middle, i 0..9
SPRING_N, TOP_N, EAVE = 21.2, 28.0, 30.5      # the nave vault's springing, its crown (28 m), the walls' top
LEAN_HI, LEAN_LO = 22.5, 14.0                 # the lean-to over aisles and chapels: against the clerestory, on the chapels' wall
def fl(name, sx, x, z0, z1, tiers, height, t, y=0.0, about=None, **kw):
    """a wall down the north (sx -1) or south (sx 1) flank, its outer face on the line |x| = x, z0..z1; openings by z"""
    xm = sx * (x - t / 2)
    a, b = ((xm, z1), (xm, z0)) if sx > 0 else ((xm, z0), (xm, z1))      # (its front outward)
    return seg(name, a, b, t, height, tiers, y=y, about=about, **kw)
for sx, nm in ((-1, "north"), (1, "south")):
    fl(f"nave arcade {nm}", sx, HB, ZE, ZW, [
        {"h": 12.0, "openings": [arch(zc(i), 3.0, 7.6) for i in range(10)]},
        {"h": 10.4, "openings": []},
        {"openings": [arch(zc(i), 1.4, 2.8, sill=0.8, surround=ROM(1)) for i in range(10)], "lombard": LOMBARD}],
       EAVE, PT, about="the nave's walls: ten round arches a side on square piers, a blind storey over them (the aisles' attic), the clerestory, a small round-arched window to each arch over the lean-to, a Lombard band under the eaves" if sx < 0 else None)
NV_L = 2 * BAY
add("nave vaults", {"type": "groin", "width": 2 * NX, "length": NV_L, "springing": SPRING_N, "top": TOP_N + 0.6,
                    "across": SEMI, "along": PTD(gspread(NX, NV_L / 2)),
                    "at": [[0, 0, r4(Z0 + NV_L * (j + 0.5)), 0] for j in range(5)],
                    "_about": "the nave's five rib vaults, each over two arches (the bound system): round across, a little pointed along, 28 m at the crown"})
add("nave ribs", {"type": "ribs", "on": "nave vaults", "width": 0.5, "depth": 0.3, "wall": {"width": 0.7, "depth": 0.35}})
NR_P = round(math.degrees(math.atan2(42.0 - EAVE, HB + 0.3)), 2)
add("nave roof", {"type": "roof", "form": "gable", "width": 2 * HB + 0.6, "length": ZW - ZE, "pitch": NR_P, "at": [[0, EAVE, r4((ZE + ZW) / 2), 0]],
                  "_about": "the nave's slate roof, its ridge at 42 m"})
# the aisles: a groin vault to each arch
AW = AX - HB
add("aisle vaults", {"type": "groin", "width": r4(AW), "length": BAY, "springing": 8.0, "top": 11.8, "across": SEMI, "along": PTD(gspread(AW / 2, BAY / 2)),
                     "at": [[r4(sx * (HB + AW / 2)), 0, r4(zc(i)), 0] for sx in (-1, 1) for i in range(10)],
                     "_about": "the aisles' groin vaults, one to each arch of the arcade"})
add("aisle ribs", {"type": "ribs", "on": "aisle vaults", "width": 0.35, "depth": 0.25})

# ================================================================ THE GOTHIC CHAPELS (1278-1319) between the aisles and the buttresses
# the bay lines (the buttresses' middles, OSM): the north row from the west transept to the east one, the Marktportal's
# vestibule in its fifth bay from the west (between the two Domhaeuser); the south row from the Memorie to the east transept
LINES = {-1: [ZW, 20.1, 15.05, 5.0, -0.2, -5.05, -10.2, -15.3, -20.4, ZE], 1: [11.6, 5.15, 0.1, -4.9, -10.0, -15.25, -20.2, ZE]}
PORTAL_BAY = (15.05, 5.0)
MARKT_Z = 11.9                                # the Marktportal's middle (between the Dom-Cafe and the Dominformation)
CH_H, CH_SP, CH_TOP = LEAN_LO, 8.5, 12.6
CW = CHX - 0.8 - AWX                          # the chapels' depth inside, 4.3
for sx, nm in ((-1, "north"), (1, "south")):
    L = LINES[sx]; bays = list(zip(L[:-1], L[1:]))
    arches = []
    for a, b in bays:
        if (a, b) == PORTAL_BAY: arches += [arch((a + b) / 2 + d, 3.4, 6.5, head=PTD()) for d in (-2.5, 2.5)]
        else: arches.append(arch((a + b) / 2, min(3.6, a - b - 1.4), 6.5, head=PTD()))
    if sx > 0: arches.append(arch(18.2, 1.6, 3.0, glass=False))    # (the door into the Memorie)
    fl(f"aisle wall {nm}", sx, AWX, ZE, ZW, [{"openings": arches}], 17.2, AWX - AX,
       about="the aisles' outer walls, broken through into the Gothic chapels -- a pointed arch to each (two into the Marktportal's vestibule; on the south, west of the chapels, the door into the Memorie)" if sx < 0 else None)
    win = lambda a, b: arch((a + b) / 2, min(3.0, a - b - 1.9), 9.0, sill=3.2, head=PTD(), tracery=2)
    ABOUT_W = "the chapels' outer wall: a tall traceried window in every bay"
    if sx > 0: fl(f"chapel wall {nm}", sx, CHX, L[-1], L[0], [{"openings": [win(a, b) for a, b in bays]}], CH_H, 0.8)
    else:
        pa, pb = PORTAL_BAY
        fl("chapel wall north east", sx, CHX, L[-1], pb, [{"openings": [win(a, b) for a, b in bays if a <= pb]}], CH_H, 0.8, about=ABOUT_W)
        fl("chapel wall north west", sx, CHX, pa, L[0], [{"openings": [win(a, b) for a, b in bays if b >= pa]}], CH_H, 0.8)
        fl("chapel wall north portal", sx, CHX, pb, pa, [{"h": 7.2, "openings": [arch(MARKT_Z, 3.4, 4.6, surround=ROM(3), glass=False)]},
                                                         {"openings": [arch(MARKT_Z, 2.2, 3.0, sill=0.4, head=PTD(), tracery=2)]}], CH_H, 0.8,
           about="the MARKTPORTAL in its stepped Romanesque surround (Willigis's bronze doors, c. 1000), a window over it")
    inner = [z for z in L[1:-1]]
    for k, z in enumerate(inner):
        seg(f"chapel partitions {nm} {k + 1}", (sx * AWX, z), (sx * (CHX - 0.8), z), 0.9, CH_TOP, [{"openings": []}],
            about="the walls between the chapels (the old buttresses of the aisle, carried in)" if (sx, k) == (-1, 0) else None)
    vb = []
    for a, b in bays:
        if (a, b) == PORTAL_BAY: vb += [((a + b) / 2 + d, (a - b) / 2 - 0.45) for d in (-2.5, 2.5)]
        else: vb.append(((a + b) / 2, a - b - 0.9))
    for k, (z, l) in enumerate(vb):
        groins(f"chapel vaults {nm} {k + 1}", [sx * (AWX + CW / 2)], [z], CW, l, CH_SP, 0, CH_TOP,
               about="the chapels' rib vaults, one to a bay" if (sx, k) == (-1, 0) else None)
    for k in range(len(vb)): add(f"chapel ribs {nm} {k + 1}", {"type": "ribs", "on": f"chapel vaults {nm} {k + 1}", "width": 0.3, "depth": 0.22})
    BUT = [z for z in L if z not in (ZW, ZE, 11.6)]
    add(f"chapel buttresses {nm}", {"type": "box", "width": 1.5, "length": 1.0, "height": 12.4, "at": [[r4(sx * (CHX + 0.75)), 0, r4(z), 0] for z in BUT],
                                    **({"_about": "the chapels' buttresses on the bay lines, each under a pinnacle"} if sx < 0 else {})})
    add(f"chapel pinnacles {nm}", {"type": "pinnacle", "w": 0.9, "h": 1.4, "s": 2.6, "crockets": 1, "at": [[r4(sx * (CHX + 0.75)), 12.4, r4(z), 0] for z in BUT]})
    # (the lean-to over aisle and chapels, from the chapels' wall head up to under the clerestory's sills)
    z0 = L[-1]; z1 = L[0]
    run = CHX + 0.3 - HB
    add(f"lean-to {nm}", {"type": "roof", "form": "shed", "width": r4(run), "length": r4(z1 - z0), "pitch": round(math.degrees(math.atan2(LEAN_HI - LEAN_LO, run)), 2),
                          "at": [[r4(sx * (HB + run / 2)), LEAN_LO, r4((z0 + z1) / 2), 0 if sx < 0 else math.pi]],
                          **({"_about": "one copper lean-to over each aisle and its chapels, from the chapels' wall head to the clerestory"} if sx < 0 else {})})
# the south aisle west of the chapels (the Memorie against it): its lean-to over the aisle alone
run = AWX + 0.2 - HB
add("lean-to south west", {"type": "roof", "form": "shed", "width": r4(run), "length": r4(ZW - 11.6), "pitch": round(math.degrees(math.atan2(LEAN_HI - LEAN_LO, CHX + 0.3 - HB)), 2),
                           "at": [[r4(HB + run / 2), r4(LEAN_HI - run * (LEAN_HI - LEAN_LO) / (CHX + 0.3 - HB)), r4((11.6 + ZW) / 2), math.pi]]})
interior("body interior", -(CHX - 0.8), CHX - 0.8, ZE, ZW, CH_TOP, about="the nave, the aisles and the chapels up to the chapels' vaults; the nave on up to its vault, the aisles to under the lean-to")
interior("nave interior", -NX - 1.0, NX + 1.0, ZE, ZW, TOP_N + 0.6)
interior("aisles interior north", -(AWX - 0.5), -(HB - 0.5), ZE, ZW, 17.0)
interior("aisles interior south", HB - 0.5, AWX - 0.5, ZE, ZW, 17.0)

# ================================================================ THE EAST TRANSEPT, its crossing, the crypt and the raised choir
EZ0, EZ1 = -42.4, -26.6                       # the block's east and west faces (OSM)
EX = 21.35                                    # its ends
EC = -34.6                                    # the crossing's middle
EW_IN, EE_IN = EZ1 - 2.0, EZ0 + 1.8           # the walls' inner faces: -28.6, -40.6
TWR = (20.7, -37.8, 3.9)                      # the round stair towers on the block's outer east corners (OSM): x, z, R
TWR_TAN = TWR[1] + TWR[2]                     # (-33.9: where the end wall meets the tower)
CHOIR_Y = 3.8                                 # the east choir's floor over the crypt
seg("east transept west wall", (EX, EZ1 - 1.0), (-EX, EZ1 - 1.0), 2.0, EAVE, [
    {"openings": [{"x": sx * (HB + AW / 2), "width": 5.0, "sill": 0, "springing": 8.0, "head": SEMI, "glass": False} for sx in (-1, 1)]
                         + [{"x": sx * (AWX + CW / 2), "width": 2.6, "sill": 0, "springing": 6.0, "head": PTD(), "glass": False} for sx in (-1, 1)]
                         + [{"x": 0, "width": 12.4, "sill": 0, "springing": 21.0, "head": SEMI, "glass": False}]
                         + [{"x": sx * 15.85, "width": 1.8, "sill": 19.0, "springing": 22.5, "head": SEMI, "surround": ROM(1)} for sx in (-1, 1)]}],
    about="the east transept's west wall: the triumphal arch to the nave, the arches from the aisles and the last chapels, windows over the lean-tos")
seg("east transept east wall", (-EX, EZ0 + 0.9), (EX, EZ0 + 0.9), 1.8, EAVE, [
    {"openings": [{"x": 0, "width": 11.6, "sill": 0, "springing": 15.5, "head": SEMI, "glass": False}]
                 + [{"x": sx * 12.6, "width": 2.2, "sill": 9.0, "springing": 17.0, "head": SEMI, "surround": ROM(1)} for sx in (-1, 1)], "lombard": LOMBARD}],
    about="its east wall: the arch into the apse (the crypt runs on under it), a tall window in each arm")
for sx, nm in ((-1, "north"), (1, "south")):
    door = [arch(-30.6, 1.6, 2.8, glass=False)] if sx > 0 else []
    fl(f"east transept {nm} end", sx, EX, TWR_TAN, EZ1, [
        {"h": 10.0, "openings": door}, {"openings": [arch(-30.25, 2.2, 9.0, sill=4.0, surround=ROM(1))], "lombard": LOMBARD}], EAVE, 2.0,
       about="the arms' ends, as far as the round towers on the corners (the south one with the door into the cloister's east walk)" if sx < 0 else None)
    fl(f"east crossing {nm} arch", sx, HB, EE_IN, EW_IN, [{"openings": [arch(EC, 10.0, 17.0, glass=False)]}], EAVE, PT,
       about="the crossing's side walls: a great arch into each arm" if sx < 0 else None)
groins("east arm vaults", [-(HB + (EX - 2.0 - HB) / 2), HB + (EX - 2.0 - HB) / 2], [EC], EX - 2.0 - HB, EE_IN - EW_IN if False else EW_IN - EE_IN, 21.0, 0, 27.6,
       about="the arms' vaults")
add("east arm ribs", {"type": "ribs", "on": "east arm vaults", "width": 0.45, "depth": 0.3})
# THE CRYPT: a hall of three aisles under the crossing, five bays to the apse; the choir floor on its vaults
CRY_Z = [EW_IN - 2.0 - 4.0 * k for k in range(3)]               # the crossing's three bays (12 m)
CW3 = 2 * NX / 3
groins("crypt vaults", [-CW3, 0, CW3], CRY_Z, CW3, 4.0, 2.2, 1.0, CHOIR_Y - 0.4, about="the east CRYPT: a hall of three aisles under the crossing, groin vaults on columns")
add("crypt vaults apse", {"type": "groin", "width": r4(CW3), "length": 4.0, "springing": 2.2, "top": CHOIR_Y - 0.4, "across": {"profile": "segmental", "rise": 1.0}, "along": {"profile": "segmental", "rise": 1.0},
                          "at": [[0, 0, r4(EE_IN - 2.0 - 4.0 * k), 0] for k in range(2)], "_about": "...and its middle aisle on into the apse, its fourth and fifth bays"})
add("crypt columns", {"type": "column", "radius": 0.32, "height": 2.2, "sides": 12,
                      "at": [[r4(sx * CW3 / 2), 0, r4(z), 0] for sx in (-1, 1) for z in (EW_IN - 4.0, EW_IN - 8.0, EE_IN)], "_about": "the crypt's columns"})
add("crypt capitals", {"type": "prism", "plan": {"rect": [0.85, 0.85]}, "height": 0.35, "at": [[r4(sx * CW3 / 2), 1.85, r4(z), 0] for sx in (-1, 1) for z in (EW_IN - 4.0, EW_IN - 8.0, EE_IN)]})
seg("crypt front", (-NX, EW_IN + 0.3), (NX, EW_IN + 0.3), 0.6, CHOIR_Y - 0.4, [{"openings": [{"x": 0, "width": 1.8, "sill": 0, "springing": 2.2, "head": SEMI, "glass": False}]}],
    about="the crypt's front under the choir's edge: its door from the nave, between the two flights up")
for sx, nm in ((-1, "north"), (1, "south")):
    fl(f"crypt side {nm}", sx, NX + 0.6, EE_IN, EW_IN, [{"h": CHOIR_Y, "openings": [arch(z, 0.9, 2.0, sill=0.9) for z in CRY_Z]}, {"openings": []}], CHOIR_Y + 1.0, 0.6,
       about="the crypt's side walls under the crossing's arches, carried up as the choir's parapet" if sx < 0 else None)
slab("east choir floor", -NX, NX, EE_IN, EW_IN, CHOIR_Y, about="the EAST CHOIR's floor over the crypt's vaults, up under the crossing tower")
add("east choir floor apse", {"type": "prism", "plan": {"sides": 16, "radius": 6.3}, "height": 0.4, "flatRoof": True, "walked": True, "at": [[0, CHOIR_Y - 0.4, EZ0, 0]]})
add("east choir floor arch", {"type": "prism", "plan": {"rect": [11.6, 1.9]}, "height": 0.4, "flatRoof": True, "walked": True, "at": [[0, CHOIR_Y - 0.4, r4(EZ0 + 0.9), 0]]})
interior("crypt interior", -NX, NX, EE_IN - 8.6, EW_IN, CHOIR_Y - 0.4, about="the crypt")
N_UP = 20
for sx in (-1, 1):
    add(f"east choir stair {'north' if sx < 0 else 'south'}", flight((sx * 4.9, EW_IN + N_UP * 0.3), (0, -1), 2.6, 0, CHOIR_Y, run=0.3, rise=CHOIR_Y / N_UP,
        **({"_about": "the two flights up from the nave to the east choir, either side of the crypt's door"} if sx < 0 else {})))
# the crossing tower: the octagon on the crossing's walls, gables round its head, the slate tent; the dome inside
ER = 8.0 / C8
add("east tower", {"type": "enclosure", "plan": {"sides": 8, "radius": r4(ER)}, "thickness": 1.4, "height": 16.5, "glass": False,
                   "tiers": [{"h": 5.5, "openings": []},
                             {"openings": {"pattern": "2", "width": 1.3, "gap": 0.9, "pier": 0.9, "sill": 1.5, "springing": 5.8, "head": SEMI, "surround": ROM(1)}, "lombard": LOMBARD}],
                   "at": [[0, EAVE, EC, 0]], "_about": "the EAST TOWER over the crossing (its octagon 14th c., its head Cuypers's of the 1870s): paired round-arched openings in every face, a Lombard band"})
add("east tower head", {"type": "prism", "plan": {"sides": 8, "radius": r4(ER - 0.8)}, "height": 0.3, "at": [[0, EAVE + 16.2, EC, 0]], "standsOn": ["east tower"]})
face8 = lambda R: 2 * R * math.sin(math.pi / 8)
add("east tower gables", {"type": "roof", "form": "gable", "width": r4(face8(ER) - 0.3), "length": 0.6, "pitch": 52,
                          "spiral": {"count": 8, "radius": r4(8.0 - 0.3), "y": EAVE + 16.5, "z": EC}, "standsOn": ["east tower"],
                          "_about": "a gable over every face of the octagon"})
add("east tower roof", {"type": "dome", "sides": 8, "radius": r4(ER + 0.3), "thickness": 0, "head": {"profile": "trigonal", "rise": 27.0},
                        "at": [[0, EAVE + 16.5, EC, 0]], "_about": "its slate tent between the gables, to 75 m"})
add("east tower finial", {"type": "column", "radius": 0.18, "height": 2.4, "sides": 6, "at": [[0, EAVE + 43.4, EC, 0]], "_about": "the cross on it"})
add("east crossing dome", {"type": "dome", "sides": 8, "radius": r4(6.0 / C8), "thickness": 0.6, "head": {"profile": "pointed", "spread": 0.35},
                           "at": [[0, 31.0, EC, 0]], "_about": "the octagonal dome inside, 38 m clear"})
apz = (6.6 * math.sqrt(2))
for n, (sx, sz) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
    hx, hz = NX, 6.0
    tri = [[r4(sx * x), r4(EC + sz * z)] for x, z in ((hx, hz), (hx, apz - hx), (apz - hz, hz))]
    add(f"east squinch {n + 1}", {"type": "prism", "plan": {"points": tri if sx * sz > 0 else tri[::-1]}, "height": 3.5, "at": [[0, 27.5, 0, 0]],
                                  **({"_about": "the squinches across the crossing's corners under the dome's diagonal faces"} if n == 0 else {})})
ARM_RUN = EX + 0.3 - 8.0
add("east transept roofs", {"type": "roof", "form": "gable", "width": r4(EZ1 - EZ0 + 0.6), "length": r4(ARM_RUN), "pitch": round(math.degrees(math.atan2(11.5, (EZ1 - EZ0) / 2 + 0.3)), 2),
                            "frieze": {"arch": 0.8}, "at": [[r4(sx * (8.0 + ARM_RUN / 2)), EAVE, r4((EZ0 + EZ1) / 2), Q] for sx in (-1, 1)],
                            "_about": "the arms' slate roofs, gabled north and south (ridge 42 m), a Lombard frieze up the gables"})
interior("east transept interior", -(EX - 2.0), EX - 2.0, EE_IN, EW_IN, 27.6, about="the east transept and its crossing")
interior("east crossing interior", -NX, NX, EE_IN, EW_IN, 38.0)
# the apse, with its dwarf gallery
add("east apse", comp("gallery-apse", {"R": 8.6, "T": 2.4, "spring": 18.4, "conchT": 1.0, "arcT": 0.5, "pass": 0.8, "galH": 3.5, "roofRise": 7.6,
                                       "winW": 2.0, "winSill": 6.5, "winSpring": 13.0, "galW": 0.9, "galSill": 1.1},
                      [[0, 0, EZ0, math.pi]], _about="the east apse: round-arched windows over the crypt, the dwarf gallery under the eaves, the stone conch inside, a half cone of slate"))
# the round stair towers, each a spiral from the arm up to its belvedere over the roofs (`round-stair-tower`)
H_UP = 38.0
steps = round(H_UP / 0.19)
while 15 < (steps * 24 + 49.5) % 360 < 345: steps -= 1           # (arriving facing the way it set off: toward the crossing tower)
for sx, nm in ((1, "south"), (-1, "north")):
    add(f"{nm} stair tower", comp("round-stair-tower", {"R": TWR[2], "wall": 0.9, "H": H_UP, "steps": steps, "doorBay": 9 if sx > 0 else 3, "stageH": 4.5, "capRise": 12.5,
                                                         "doorW": 1.1, "archW": 1.0},
                                  [[sx * TWR[0], 0, TWR[1], 0]],
                                  **({"_about": "the two ROUND STAIR TOWERS on the east transept's outer corners: a spiral from the arm up to the belvedere at 38 m, its arcade and stone cone (55.5 m)"} if sx > 0 else {})))

# ================================================================ THE WEST TRANSEPT and its crossing
WZ0, WZ1 = ZW, 42.7                           # its east and west faces
WC = 33.75                                    # the crossing's middle
WIN0, WIN1 = WZ0 + 2.0, WZ1 - 2.0             # the inner faces: 26.8, 40.7
TX = 25.6                                     # the arms' ends (OSM: 26.3 north, 24.9 south)
TT = 2.4
seg("west transept east wall", (TX, WZ0 + 1.0), (-TX, WZ0 + 1.0), 2.0, EAVE, [
    {"openings": [{"x": sx * (HB + AW / 2), "width": 5.0, "sill": 0, "springing": 8.0, "head": SEMI, "glass": False} for sx in (-1, 1)]
                         + [{"x": 0, "width": 12.4, "sill": 0, "springing": 21.2, "head": SEMI, "glass": False}]
                         + [{"x": sx * 19.5, "width": 2.0, "sill": 11.5, "springing": 15.0, "head": SEMI, "surround": ROM(1)} for sx in (-1, 1)], "lombard": LOMBARD}],
    about="the west transept's east wall: the arch from the nave, the aisles' arches, a window high in each arm")
seg("west transept west wall", (-TX, WZ1 - 1.0), (TX, WZ1 - 1.0), 2.0, EAVE, [
    {"openings": [{"x": 0, "width": 11.0, "sill": 0, "springing": 19.5, "head": SEMI, "glass": False}]
                 + [{"x": sx * 17.0, "width": 2.4, "sill": 7.0, "springing": 13.5, "head": SEMI, "surround": ROM(2)} for sx in (-1, 1)], "lombard": LOMBARD}],
    about="its west wall: the arch into the west choir, a tall window in each arm over the sacristy")
END_LOW = lambda door: [arch(WC + 0.6, 3.6, 5.6, surround=ROM(3), glass=False)] if door == "portal" else [arch(29.0, 1.6, 2.8, glass=False)]
for sx, nm, door in ((-1, "north", "link"), (1, "south", "portal")):
    fl(f"west transept {nm} end", sx, TX, WZ0, WZ1, [
        {"h": 15.0, "openings": END_LOW(door) + [arch(38.9, 3.0, 9.0, sill=6.0, foot=SEMI) if False else arch(38.9, 2.2, 11.0, sill=5.0, surround=ROM(1))]},
        {"openings": [arch(z, 2.4, 9.0, sill=2.5, surround=ROM(2)) for z in (29.0, WC + 0.6, 38.9)], "lombard": LOMBARD}], EAVE, TT,
       about="the arms' end fronts: in two storeys under Lombard bands -- the south one the Leichhof portal in its stepped orders, the north one the door to the Gotthardkapelle's passage -- three tall round-arched windows over them" if sx < 0 else None)
    fl(f"west crossing {nm} arch", sx, HB, WIN0, WIN1, [{"openings": [arch(WC, 11.4, 19.5, glass=False)]}], EAVE, PT,
       about="the crossing's side walls: a great arch into each arm" if sx < 0 else None)
    add(f"west transept {nm} buttresses", {"type": "box", "width": 1.8, "length": 1.4, "height": 26.0,
                                         "at": [[r4(sx * (TX + 0.9)), 0, z, 0] for z in (31.9, 36.8, 42.0)],
                                         **({"_about": "the buttresses on the arms' ends (OSM)"} if sx < 0 else {})})
TA = TX - TT - HB
groins("west arm vaults", [-(HB + TA / 2), HB + TA / 2], [WC], TA, WIN1 - WIN0, SPRING_N, 0, 29.0, about="the arms' vaults, one square bay each")
add("west arm ribs", {"type": "ribs", "on": "west arm vaults", "width": 0.45, "depth": 0.3})
TR_RUN = TX + 0.3 - 8.35
add("west transept roofs", {"type": "roof", "form": "gable", "width": r4(WZ1 - WZ0 + 0.6), "length": r4(TR_RUN), "pitch": round(math.degrees(math.atan2(11.5, (WZ1 - WZ0) / 2 + 0.3)), 2),
                            "frieze": {"arch": 0.8}, "at": [[r4(sx * (8.35 + TR_RUN / 2)), EAVE, WC, Q] for sx in (-1, 1)],
                            "_about": "the arms' slate roofs, ridge 42 m, a Lombard frieze up their gables"})
interior("west transept interior", -(TX - TT), TX - TT, WIN0, WIN1, 29.0, about="the west transept and its crossing")
interior("west crossing interior", -NX, NX, WIN0, WIN1, 44.0)

# ================================================================ THE WESTTURM over the crossing, 83.5 m
WR = 8.35 / C8
add("west crossing dome", {"type": "dome", "sides": 8, "radius": r4(6.35 / C8), "thickness": 0.6, "head": SEMI, "at": [[0, 37.0, WC, 0]],
                           "_about": "the octagonal dome inside, 44 m clear"})
apw = 6.35 * math.sqrt(2)
for n, (sx, sz) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
    hx, hz = NX, (WIN1 - WIN0) / 2
    tri = [[r4(sx * x), r4(WC + sz * z)] for x, z in ((hx, hz), (hx, apw - hx), (apw - hz, hz))]
    add(f"west squinch {n + 1}", {"type": "prism", "plan": {"points": tri if sx * sz > 0 else tri[::-1]}, "height": 6.5, "at": [[0, 30.5, 0, 0]]})
add("west tower 1", {"type": "enclosure", "plan": {"sides": 8, "radius": r4(WR)}, "thickness": 2.0, "height": 16.5, "glass": False,
                     "tiers": [{"h": 10.0, "openings": []},
                               {"h": 3.0, "openings": {"pattern": "3", "width": 0.7, "gap": 0.45, "pier": 0.9, "sill": 0.6, "springing": 2.2, "head": SEMI}, "lombard": LOMBARD},
                               {"openings": {"pattern": "2", "width": 1.0, "gap": 1.1, "pier": 0.9, "sill": 0.6, "springing": 2.4, "head": SEMI, "surround": ROM(1)}, "lombard": LOMBARD}],
                     "at": [[0, EAVE, WC, 0]], "_about": "the WESTTURM's Romanesque octagon (c. 1200): out of the roofs, a dwarf gallery of little arches and a row of paired windows, each under its Lombard band"})
add("west tower 2", {"type": "enclosure", "plan": {"sides": 8, "radius": r4(8.1 / C8)}, "thickness": 1.4, "height": 10.0, "glass": False,
                     "tiers": [{"h": 1.2, "openings": []},
                               {"openings": {"pattern": "2", "width": 1.5, "gap": 0.7, "pier": 0.8, "sill": 0.6, "springing": 6.2, "head": PTD(), "tracery": 2}}],
                     "at": [[0, 47.0, WC, 0]], "_about": "the Gothic belfry (1482): two tall traceried lancets in every face"})
add("west tower clock", comp("clock-dial", {"R": 1.1, "hour": 10, "minute": 9}, [], spiral={"count": 4, "radius": 8.12, "y": 55.0, "z": WC},
                             _about="the clock on the belfry's four main faces"))
del parts["west tower clock"]["at"]
add("west tower 2 cornice", {"type": "prism", "plan": {"sides": 8, "radius": r4(8.1 / C8 + 0.35)}, "height": 0.45, "flatRoof": True, "at": [[0, 57.0, WC, 0]]})
add("west tower balustrade", {"type": "ring", "count": 8, "polygon": True, "rOuter": r4(8.1 / C8 + 0.3), "rInner": r4(8.1 / C8), "height": 1.0, "y": 57.45,
                              "place": [[0, 0, WC, 0]], "solid": True,
                              "_about": "NEUMANN's crown (1769-74): the balustrade round the belfry's head..."})
add("west tower pinnacles", {"type": "pinnacle", "w": 0.8, "sides": 4, "h": 1.6, "s": 3.0, "crockets": 2,
                             "at": [[r4((8.1 / C8 + 0.05) * math.sin((k + .5) * math.pi / 4)), 57.45, r4(WC + (8.1 / C8 + 0.05) * math.cos((k + .5) * math.pi / 4)), 0] for k in range(8)],
                             "_about": "...the pinnacles on its corners..."})
R3 = 6.05 / C8
add("west tower 2 roof", {"type": "dome", "sides": 8, "radius": r4(8.1 / C8), "thickness": 0, "head": {"profile": "trigonal", "rise": r4(4.0 * (8.1 / C8) / (8.1 / C8 - R3))},
                          "oculus": r4(R3), "cap": False, "at": [[0, 57.45, WC, 0]], "_about": "...the stone roof sloping up from it to the next stage..."})
add("west tower 3", {"type": "enclosure", "plan": {"sides": 8, "radius": r4(R3)}, "thickness": 1.0, "height": 9.55, "glass": False,
                     "tiers": [{"h": 4.6, "openings": []}, {"openings": {"pattern": "1", "width": 1.6, "sill": 0.4, "springing": 3.2, "head": SEMI}}],
                     "at": [[0, 57.45, WC, 0]], "_about": "...the octagonal stage over it, an arched window in every face..."})
add("west tower 3 cornice", {"type": "prism", "plan": {"sides": 8, "radius": r4(R3 + 0.3)}, "height": 0.4, "flatRoof": True, "at": [[0, 67.0, WC, 0]]})
add("west tower 3 pinnacles", {"type": "pinnacle", "w": 0.6, "sides": 4, "h": 1.2, "s": 2.4, "crockets": 1,
                               "at": [[r4((R3 + 0.05) * math.sin((k + .5) * math.pi / 4)), 67.4, r4(WC + (R3 + 0.05) * math.cos((k + .5) * math.pi / 4)), 0] for k in range(8)]})
R4 = 4.15 / C8
add("west tower 3 roof", {"type": "dome", "sides": 8, "radius": r4(R3), "thickness": 0, "head": {"profile": "trigonal", "rise": r4(3.6 * R3 / (R3 - R4))},
                          "oculus": r4(R4), "cap": False, "at": [[0, 67.4, WC, 0]], "_about": "...its own stone roof..."})
add("west tower 4", {"type": "enclosure", "plan": {"sides": 8, "radius": r4(R4)}, "thickness": 0.7, "height": 7.6, "glass": False,
                     "tiers": [{"h": 3.8, "openings": []}, {"openings": {"pattern": "1", "width": 0.9, "sill": 0.5, "springing": 2.0, "head": SEMI}}],
                     "at": [[0, 67.4, WC, 0]], "_about": "...the little top stage..."})
add("west tower 4 cornice", {"type": "prism", "plan": {"sides": 8, "radius": r4(R4 + 0.25)}, "height": 0.35, "flatRoof": True, "at": [[0, 75.0, WC, 0]]})
add("west tower helm", {"type": "dome", "sides": 8, "radius": r4(R4 + 0.1), "thickness": 0, "head": {"profile": "bell", "waist": 0.7, "lift": 1.0, "rise": 2.6},
                        "at": [[0, 75.35, WC, 0]], "_about": "...and the stone helm: a bell..."})
add("west tower lantern", {"type": "column", "radius": 1.0, "height": 1.6, "sides": 8, "at": [[0, 77.9, WC, 0]], "_about": "...a lantern..."})
add("west tower spire", {"type": "dome", "sides": 8, "radius": 1.15, "thickness": 0, "head": {"profile": "trigonal", "rise": 3.0}, "at": [[0, 79.5, WC, 0]],
                         "_about": "...and the spire, to 82.5 m"})
add("west tower ball", {"type": "column", "radius": 0.28, "height": 0.5, "sides": 8, "at": [[0, 82.3, WC, 0]]})
add("domsgickel", {"type": "pinnacle", "w": 0.5, "h": 0.15, "s": 0.95, "sides": 4, "at": [[0, 82.6, WC, 0]], "_about": "the gilt weathercock (the Domsgickel), 0.95 m, at 83.5 m"})

# ================================================================ THE TREFOIL WEST CHOIR (1200-39), raised nine steps
CB = 6.6                                      # the square bay's half width inside (13.2 m)
CZ0, CZ1 = WZ1, WZ1 + 2 * CB                  # its east and west inner faces: 42.7, 55.9
CC = (CZ0 + CZ1) / 2                          # 49.3
BT = 2.4                                      # its walls
WCH_Y = 9 * 0.19                              # the choir's floor: nine steps up from the crossing
CA, CT = 5.5, 2.2                             # a conch's apothem inside (the trefoil 24.25 m across), its walls
CH1, GAL = 18.0, 3.2                          # a conch's walls to the dwarf gallery's floor, the gallery
CONCHES = [("west", (0, CZ1), 0.0), ("north", (-CB, CC), -Q), ("south", (CB, CC), Q)]
W_TOP = 31.0
for nm, a, b, ops in (("north", (-CB - BT / 2, CZ1 + BT), (-CB - BT / 2, CZ0), "z"), ("south", (CB + BT / 2, CZ0), (CB + BT / 2, CZ1 + BT), "z"),
                      ("west", (CB, CZ1 + BT / 2), (-CB, CZ1 + BT / 2), "x")):
    c = {"z": CC} if ops == "z" else {"x": 0}
    seg(f"west choir {nm} wall", a, b, BT, W_TOP, [
        {"h": 25.0, "openings": [{**c, "width": 2 * CA, "sill": 0, "springing": 12.0, "head": SEMI, "glass": False}]},
        {"openings": [{**c, "width": 3.0, "sill": 1.6, "springing": 3.1, "head": SEMI, "foot": SEMI}], "lombard": LOMBARD}],
        about="the west choir's square bay: a great arch on each of its three free sides into a conch, a rose over each in the gable storey" if nm == "north" else None)
groins("west choir vault", [0], [CC], 2 * CB, 2 * CB, 21.0, 0, 28.2, about="the bay's rib vault")
add("west choir ribs", {"type": "ribs", "on": "west choir vault", "width": 0.5, "depth": 0.3, "wall": {"width": 0.6, "depth": 0.3}})
for nm, (x, z), yaw in CONCHES:
    ri, ro = CA / C8, (CA + CT) / C8
    place = [[x, 0, z, yaw]]
    add(f"{nm} conch", {"type": "ring", "count": 8, "polygon": True, "at": [6, 7, 0, 1, 2], "rOuter": r4(ro), "rInner": r4(ri), "height": CH1, "place": place,
                        "opening": {"width": 1.9, "sill": 7.0, "springing": 13.0, "head": SEMI, "surround": ROM(1)}, "lombard": LOMBARD,
                        **({"_about": "the TREFOIL's three polygonal conchs (half octagons, 5.5 m deep inside): a tall round-arched window in each face"} if nm == "west" else {})})
    add(f"{nm} conch gallery", {"type": "ring", "count": 8, "polygon": True, "at": [7, 0, 1], "rOuter": r4(ro), "rInner": r4(ro - 0.5 / C8), "height": GAL, "y": CH1,
                                "place": place, "glass": False, "outside": True, "opening": {"width": 2.4, "sill": 0.8, "springing": 1.7, "head": SEMI},
                                **({"_about": "the dwarf gallery under each conch's eaves, open in arcades..."} if nm == "west" else {})})
    add(f"{nm} conch gallery wall", {"type": "ring", "count": 8, "polygon": True, "at": [6, 7, 0, 1, 2], "rOuter": r4(ro - 1.3 / C8), "rInner": r4(ri), "height": GAL, "y": CH1,
                                     "place": place, "outside": True, **({"_about": "...the wall behind its passage"} if nm == "west" else {})})
    add(f"{nm} conch gallery ends", {"type": "ring", "count": 8, "polygon": True, "at": [6, 2], "rOuter": r4(ro), "rInner": r4(ro - 1.3 / C8), "height": GAL, "y": CH1, "place": place, "solid": True})
    add(f"{nm} conch vault", {"type": "dome", "sweep": 0.5, "sides": 8, "radius": r4(ri + 0.8), "thickness": 0.8, "head": SEMI, "at": [[x, 11.0, z, yaw]],
                              **({"_about": "the conchs' half domes inside"} if nm == "west" else {})})
    add(f"{nm} conch roof", {"type": "dome", "sweep": 0.5, "sides": 8, "radius": r4(ro + 0.3), "thickness": 0, "head": {"profile": "trigonal", "rise": 5.0},
                             "at": [[r4(x + 0.4 * math.sin(yaw)), CH1 + GAL, r4(z + 0.4 * math.cos(yaw)), yaw]], **({"_about": "and their slate half-pyramids, up against the bay's gables"} if nm == "west" else {})})
    parts[f"{nm} conch interior"] = {"type": "interior", "plan": {"sides": 8, "radius": r4(ri)}, "height": CH1, "at": [[x, 0, z, 0]]}
    add(f"{nm} conch floor", {"type": "prism", "plan": {"sides": 8, "radius": r4(ri + 0.2)}, "height": WCH_Y, "flatRoof": True, "walked": True, "at": [[x, 0, z, 0]],
                              **({"_about": "the conchs' floors, the choir's"} if nm == "west" else {})})
slab("west choir floor", -CB - BT, CB + BT, WIN1, CZ1, WCH_Y, h=WCH_Y, about="the WEST CHOIR's floor, nine steps over the crossing's, through the arch")
add("west choir steps", flight((0, WIN1 - 9 * 0.32), (0, 1), 9.0, 0, WCH_Y, run=0.32, rise=0.19, _about="the nine steps up from the crossing into the west choir"))
interior("west choir interior", -CB, CB, WIN1, CZ1, 28.2, about="the west choir's bay")
# its roofs: two gables crossing over the bay, a rose in each gable; St Martin on the west one
WG_P = 42
add("west choir roofs", {"type": "roof", "form": "gable", "width": r4(2 * (CB + BT) + 0.6), "length": r4(CZ1 + BT + 0.3 - WZ1), "pitch": WG_P, "frieze": {"arch": 0.7},
                         "at": [[0, W_TOP, r4((WZ1 + CZ1 + BT + 0.3) / 2), 0]],
                         "_about": "two slate gables crossing over the bay, over the west conch and over the north and south"})
add("west choir cross roof", {"type": "roof", "form": "gable", "width": r4(CZ1 + BT - CZ0 + 0.6), "length": r4(2 * (CB + BT) + 0.6), "pitch": WG_P, "frieze": {"arch": 0.7},
                              "at": [[0, W_TOP, CC + BT / 2, Q]]})
RIDGE_W = W_TOP + (CB + BT + 0.3) * math.tan(math.radians(WG_P))
add("st martin", comp("equestrian", {"S": 1.6, "kind": "man", "style": "gothic", "stone": "sandstone", "pose": "enthroned", "holdR": "items/weapons/sword"},
                      [[0, r4(RIDGE_W - 0.3), r4(CZ1 + BT - 0.4), 0]], _about="St Martin on horseback on the west gable, dividing his cloak"))
# the two slender octagonal towers in the angles between the conchs
for sx in (-1, 1):
    add(f"west choir tower {'north' if sx < 0 else 'south'}", {"type": "enclosure", "plan": {"sides": 8, "radius": 2.4}, "thickness": 0.7, "height": 41.0, "glass": True,
        "tiers": [{"h": 8.0, "openings": []}, {"h": 6.5, "openings": [], "lombard": LOMBARD}, {"h": 6.5, "openings": {"pattern": "1", "width": 0.6, "sill": 2.8, "springing": 5.0, "head": SEMI}, "lombard": LOMBARD},
                  {"h": 6.5, "openings": {"pattern": "1", "width": 0.7, "sill": 2.6, "springing": 5.0, "head": SEMI}, "lombard": LOMBARD},
                  {"h": 6.5, "openings": {"pattern": "2", "width": 0.5, "gap": 0.3, "pier": 0.3, "sill": 2.4, "springing": 5.0, "head": SEMI}, "lombard": LOMBARD},
                  {"openings": {"pattern": "2", "width": 0.55, "gap": 0.3, "pier": 0.25, "sill": 0.9, "springing": 4.6, "head": SEMI}, "lombard": LOMBARD}],
        "at": [[r4(sx * 8.6), 0, 59.6, 0]], **({"_about": "the two slender octagonal STAIR TOWERS in the trefoil's outer angles, storey on storey under Lombard bands, open at the top"} if sx < 0 else {})})
add("west choir tower cornices", {"type": "prism", "plan": {"sides": 8, "radius": 2.7}, "height": 0.4, "flatRoof": True, "at": [[r4(sx * 8.6), 41.0, 59.6, 0] for sx in (-1, 1)]})
add("west choir tower caps", {"type": "dome", "sides": 8, "radius": 2.6, "thickness": 0, "head": {"profile": "bell", "waist": 0.7, "lift": 1.0, "rise": 2.8},
                              "at": [[r4(sx * 8.6), 41.4, 59.6, 0] for sx in (-1, 1)], "_about": "their stone caps (Neumann's), each with a little lantern and spike"})
add("west choir tower lanterns", {"type": "column", "radius": 0.7, "height": 1.2, "sides": 8, "at": [[r4(sx * 8.6), 44.1, 59.6, 0] for sx in (-1, 1)]})
add("west choir tower spikes", {"type": "dome", "sides": 8, "radius": 0.8, "thickness": 0, "head": {"profile": "trigonal", "rise": 2.0}, "at": [[r4(sx * 8.6), 45.3, 59.6, 0] for sx in (-1, 1)]})
# the sacristy round the trefoil's foot (OSM 475948611): low, flat-roofed in copper
SAC = [(17.8, 71.7), (-3.5, 71.7), (-14.6, 68.4), (-24.8, 48.0), (-24.7, 45.9), (-13.6, 45.3), (-13.6, 57.0), (-3.2, 66.1), (5.7, 65.8), (11.4, 56.2),
       (13.1, 54.2), (14.3, 53.9), (15.6, 59.3), (16.2, 62.1), (18.2, 71.5)]
add("sacristy", {"type": "prism", "plan": {"points": [[x, z] for x, z in SAC]}, "height": 5.6, "flatRoof": True, "at": [[0, 0, 0, 0]],
                 "_about": "the sacristies wrapped round the trefoil's foot (OSM), 8 m, flat copper roofs"})
add("sacristy roof", {"type": "prism", "plan": {"points": [[x, z] for x, z in SAC]}, "height": 0.4, "flatRoof": True, "at": [[0, 5.6, 0, 0]]})

# ================================================================ THE MEMORIE (the chapter house) and THE CLOISTER (1390-1410)
MX0, MX1, MZ0, MZ1 = AWX, 31.2, 11.6, ZW      # the Memorie, against the south aisle west of the chapels
MCX, MCZ = (MX0 + MX1) / 2, (MZ0 + MZ1) / 2
WW0, WW1 = 12.4, 17.8                         # the west walk's clear width (z), its arcade from 11.6
add("memorie", {"type": "enclosure", "plan": {"rect": [r4(MX1 - MX0), r4(MZ1 - MZ0)]}, "thickness": 1.2, "height": 11.0, "glass": True, "interior": True,
                "faces": {"3": [{"openings": [{"at": 0, "width": 1.6, "sill": 0, "springing": 3.0, "head": SEMI, "glass": False}]}],
                          "1": [{"openings": [{"at": r4(MCZ - (WW0 + WW1) / 2), "width": 1.6, "sill": 0, "springing": 3.0, "head": PTD(), "glass": False},
                                              {"at": r4(MCZ - 21.0), "width": 2.2, "sill": 3.5, "springing": 7.0, "head": PTD(), "tracery": 2}]}],
                          "2": [{"openings": [{"at": r4(d), "width": 2.4, "sill": 3.5, "springing": 7.5, "head": PTD(), "tracery": 2} for d in (-3.5, 3.5)]}],
                          "0": [{"openings": []}]},
                "at": [[r4(MCX), 0, r4(MCZ), 0]],
                "_about": "the MEMORIE, the chapter house (c. 1240): a square hall off the south aisle under one rib vault, its door to the cloister's west walk, traceried windows to the garth"})
groins("memorie vault", [MCX], [MCZ], MX1 - MX0 - 2.4, MZ1 - MZ0 - 2.4, 4.0, 0, 10.6)
add("memorie ribs", {"type": "ribs", "on": "memorie vault", "width": 0.4, "depth": 0.28})
add("memorie roof", {"type": "roof", "form": "hip", "width": r4(MX1 - MX0 + 0.6), "length": r4(MZ1 - MZ0 + 0.6), "pitch": 42, "at": [[r4(MCX), 11.0, r4(MCZ), 0]],
                     "_about": "its slate roof"})
# the cloister: three walks round the garth -- west, south, east -- each vaulted bay by bay, open to the garth in traceried
# arches (a door through the middle one), the rooms behind them; over walks and rooms the Dommuseum's storey under slate
GX0, GX1, GZ0, GZ1 = CHX, 50.8, ZE, 11.6      # the garth, inside the arcades
K_H, K_SP, K_TOP = 7.0, 3.6, 6.6              # the ground storey, the walks' springing and vault tops
UP_H = 5.5                                    # the Dommuseum's storey
SX0, SX1 = 51.6, 56.8                         # the south walk (x)
EZ_0, EZ_1 = -27.4, -32.8                     # the east walk (z)
TRAC = lambda w=2.6: {"width": w, "sill": 0.8, "springing": 3.0, "head": PTD(), "tracery": 2, "glass": False}
GATE = {"width": 1.8, "sill": 0, "springing": 3.0, "head": PTD(), "glass": False}
def arcade(name, a, b, n, about=None):
    L = math.dist(a, b); ops = [{"at": r4(-L / 2 + L * (k + 0.5) / n), **(GATE if k == n // 2 else TRAC())} for k in range(n)]
    return seg(name, a, b, 0.8, K_H, [{"openings": ops}], about=about)
arcade("cloister west arcade", (31.2, GZ1 + 0.4), (SX0, GZ1 + 0.4), 5, about="the cloister's arcades to the garth: Gothic tracery in every bay, a door through the middle one")
arcade("cloister south arcade", (SX0 - 0.4, GZ1 + 0.8), (SX0 - 0.4, EZ_0), 10)
arcade("cloister east arcade", (SX0, EZ_0 + 0.4), (CHX, EZ_0 + 0.4), 8)
groins("west walk vaults", [31.2 + (SX0 - 31.2) * (k + 0.5) / 5 for k in range(5)], [(WW0 + WW1) / 2], (SX0 - 31.2) / 5, WW1 - WW0, K_SP, 0, K_TOP,
       about="the walks' rib vaults, bay by bay")
SW_N = 12
groins("south walk vaults", [(SX0 + SX1) / 2], [EZ_1 + (WW1 - EZ_1) * (k + 0.5) / SW_N for k in range(SW_N)], SX1 - SX0, (WW1 - EZ_1) / SW_N, K_SP, 0, K_TOP)
groins("east walk vaults", [CHX + (SX0 - CHX) * (k + 0.5) / 7 for k in range(7)], [(EZ_0 + EZ_1) / 2], (SX0 - CHX) / 7, EZ_0 - EZ_1, K_SP, 0, K_TOP)
for w in ("west", "south", "east"): add(f"{w} walk ribs", {"type": "ribs", "on": f"{w} walk vaults", "width": 0.25, "depth": 0.2})
interior("west walk interior", 31.2, SX0, WW0, WW1, K_TOP, about="the cloister's walks")
interior("south walk interior", SX0, SX1, EZ_1, WW1, K_TOP)
interior("east walk interior", CHX, SX0, EZ_1, EZ_0, K_TOP)
# the rooms behind the walks, the walks' back walls their faces; the stair to the Dommuseum in the south range
DOOR = lambda at: {"at": r4(at), "width": 1.6, "sill": 0, "springing": 2.8, "head": PTD(), "glass": False}
WIN = lambda at: {"at": r4(at), "width": 1.5, "sill": 1.4, "springing": 3.9, "head": PTD(), "tracery": 2}
block(add, "cloister west range", 31.2, SX1, WW1, ZW, 0, K_H, 1,
      {2: lambda L, j, hs: [DOOR(-(43.0 - (31.2 + SX1) / 2))], 0: lambda L, j, hs: [WIN(a) for a in (-8, 0, 8)]}, t=0.8, skip=(3,),
      about="the rooms behind the west walk (OSM: the range to the Memorie's west face)")
KS_X1 = 66.0
KMID = (EZ_1 - 11.2 + ZW) / 2
block(add, "cloister south range", SX1, KS_X1, EZ_1 - 11.2, ZW, 0, K_H, 1,
      {3: lambda L, j, hs: [DOOR(z - KMID) for z in (-14.0, 4.0)], 1: lambda L, j, hs: [WIN(-(z - KMID)) for z in (-36, -24, -12, 8, 18)]}, t=0.8,
      about="the south range: its hall, the stair up to the Dommuseum")
block(add, "cloister east range", 24.8, SX1, EZ_1 - 11.2, EZ_1, 0, K_H, 1,
      {0: lambda L, j, hs: [DOOR(36.0 - (24.8 + SX1) / 2)], 2: lambda L, j, hs: [WIN(-(x - (24.8 + SX1) / 2)) for x in (30, 40, 50)]}, t=0.8, skip=(1,),
      about="the east range")
seg("east walk end", (CHX, EZ_1 + 0.4), (24.8, EZ_1 + 0.4), 0.8, K_H, [{"openings": []}])
# the Dommuseum's storey over walks and ranges: three halls, a door through each joint, windows to the garth and out
UY = K_H
for nm, (x0, x1, z0, z1) in (("west", (31.2, GX1, GZ1, ZW)), ("east", (24.8, GX1, EZ_1 - 11.2, GZ0))):
    slab(f"dommuseum floor {nm}", x0, x1, z0, z1, UY)
slab("dommuseum floor east walk", CHX, 24.8, EZ_1, GZ0, UY, walked=False)
SH = (58.0, 61.2, -14.0, -6.8)                # the stair's well (x0, x1, z0, z1)
for k, (x0, x1, z0, z1) in enumerate(((GX1, KS_X1, EZ_1 - 11.2, SH[2]), (GX1, KS_X1, SH[3], ZW), (GX1, SH[0], SH[2], SH[3]), (SH[1], KS_X1, SH[2], SH[3]))):
    slab(f"dommuseum floor south {k + 1}", x0, x1, z0, z1, UY, about="the south range's upper floor, round the stair's well" if k == 0 else None)
add("dommuseum stair", {"type": "staircase", "flight": 20, "width": 1.6, "run": 0.28, "rise": r4(UY / 40), "soffit": 0.3,
                        "landing": {"depth": 1.6, "width": 3.2, "shift": -0.8, "then": [{"flight": 20, "width": 1.6, "from": "back", "at": -0.8}]},
                        "at": [[58.8, 0, SH[2], -Q]], "_about": "the stair up to the Dommuseum: two flights turning on a landing"})
um = lambda a, b: (a + b) / 2
block(add, "dommuseum west", 31.2, GX1, GZ1, ZW, UY, UP_H, 1,
      {2: lambda L, j, hs: [WIN(a) for a in (-6, 0, 6)], 1: lambda L, j, hs: [DOOR(-(um(WW0, ZW) - um(GZ1, ZW)))], 0: lambda L, j, hs: [WIN(a) for a in (-6, 6)]}, t=0.7, skip=(3,),
      about="the Dommuseum's storey over the walks and ranges")
block(add, "dommuseum south", GX1, KS_X1, EZ_1 - 11.2, ZW, UY, UP_H, 1,
      {3: lambda L, j, hs: [DOOR(z - KMID) for z in (um(WW0, ZW), -38.0)] + [WIN(z - KMID) for z in (-20, -10, 0)],
       1: lambda L, j, hs: [WIN(-(z - KMID)) for z in (-36, -24, -12, 0, 12)]}, t=0.7)
block(add, "dommuseum east", 24.8, GX1, EZ_1 - 11.2, GZ0, UY, UP_H, 1,
      {1: lambda L, j, hs: [DOOR(-(-38.0 - um(EZ_1 - 11.2, GZ0)))], 0: lambda L, j, hs: [WIN(-(x - um(24.8, GX1))) for x in (32, 40, 47)],
       2: lambda L, j, hs: [WIN(-(x - um(24.8, GX1))) for x in (30, 40)]}, t=0.7)
RY = UY + UP_H
add("cloister roofs", {"type": "roof", "form": "gable", "width": r4(ZW - GZ1 + 0.6), "length": r4(GX1 - 31.2), "pitch": 45, "at": [[um(31.2, GX1), RY, um(GZ1, ZW), Q]],
                       "_about": "the cloister ranges' slate roofs"})
add("cloister south roof", {"type": "roof", "form": "gable", "width": r4(KS_X1 - GX1 + 0.6), "length": r4(ZW - EZ_1 + 11.2 + 0.6), "pitch": 45, "at": [[um(GX1, KS_X1), RY, um(EZ_1 - 11.2, ZW), 0]]})
add("cloister east roof", {"type": "roof", "form": "gable", "width": r4(GZ0 - EZ_1 + 11.2 + 0.6), "length": r4(GX1 - 24.8), "pitch": 45, "at": [[um(24.8, GX1), RY, um(EZ_1 - 11.2, GZ0), Q]]})
add("cloister walk roof", {"type": "roof", "form": "shed", "width": 3.6, "length": r4(GZ0 - EZ_1 + 0.6), "pitch": 30, "at": [[r4(CHX + 1.8), UY, um(EZ_1, GZ0), 0]]})
add("garth", {"type": "prism", "plan": {"rect": [r4(GX1 - GX0 - 0.4), r4(GZ1 - GZ0 - 0.4)]}, "height": 0.05, "flatRoof": True, "walked": True, "at": [[um(GX0, GX1), 0, um(GZ0, GZ1), 0]],
                 "_about": "the garth's lawn"})

# ================================================================ NORTH: THE GOTTHARDKAPELLE (1137) and the Domhaeuser against the chapels
GX_0, GX_1, GZ_0, GZ_1 = -43.1, -29.1, 23.9, 39.0      # OSM 146459809
GOT_H = 16.0
gcx, gcz = (GX_0 + GX_1) / 2, (GZ_0 + GZ_1) / 2
win = lambda a, sill, sp, w=1.2: {"at": r4(a), "width": w, "sill": sill, "springing": sp, "head": SEMI, "surround": ROM(1)}
add("gotthardkapelle", {"type": "enclosure", "plan": {"rect": [r4(GX_1 - GX_0), r4(GZ_1 - GZ_0)]}, "thickness": 1.3, "height": GOT_H, "glass": True, "interior": True,
    "faces": {"1": [{"h": 7.0, "openings": [{"at": r4(gcz - 29.0), "width": 1.6, "sill": 0, "springing": 2.8, "head": SEMI, "glass": False}]},
                    {"openings": [win(a, 2.0, 6.0) for a in (-4.5, 4.5)], "lombard": LOMBARD}],
              "2": [{"h": 7.0, "openings": [{"at": r4(-(gcx - (-36.15))), "width": 3.6, "sill": 0, "springing": 4.6, "head": SEMI, "glass": False}]},
                    {"openings": [{"at": r4(-(gcx - (-36.15))), "width": 5.0, "sill": 0, "springing": 3.0, "head": SEMI, "glass": False}], "lombard": LOMBARD}],
              "0": [{"h": 7.0, "openings": [win(a, 2.4, 5.4, 1.0) for a in (-4.0, 0, 4.0)]}, {"openings": [win(a, 2.0, 6.0) for a in (-4.0, 4.0)], "lombard": LOMBARD}],
              "3": [{"h": 7.0, "openings": [win(a, 2.4, 5.4, 1.0) for a in (-4.0, 0, 4.0)]}, {"openings": [win(a, 2.0, 6.0) for a in (-4.5, 4.5)], "lombard": LOMBARD}]},
    "at": [[r4(gcx), 0, r4(gcz), 0]],
    "_about": "the GOTTHARDKAPELLE, the archbishop's double chapel (1137): two storeys of nine bays, the lower vaults open in the middle to the upper chapel, its apse to the east, joined to the north transept by a passage"})
gx = [gcx + (GX_1 - GX_0 - 2.6) / 3 * k for k in (-1, 0, 1)]
gz = [gcz + (GZ_1 - GZ_0 - 2.6) / 3 * k for k in (-1, 0, 1)]
gw, gl = (GX_1 - GX_0 - 2.6) / 3, (GZ_1 - GZ_0 - 2.6) / 3
GOT_YAW = 0.0
add("gotthard lower vaults", {"type": "groin", "width": r4(gw), "length": r4(gl), "springing": 4.0, "top": 6.8, "across": PTD(gspread(gl / 2, gw / 2)), "along": SEMI,
                              "at": [[r4(x), 0, r4(z), 0] for x in gx for z in gz if (x, z) not in ((gx[1], gz[1]), (gx[0], gz[2]))],
                              "_about": "the lower chapel's vaults on four columns, the middle bay open to the upper chapel, the north-west one the stair's"})
add("gotthard stair", {"type": "spiral-stair", "radius": 1.75, "newel": 0.2, "turn": 24, "top": 6.85, "steps": 36, "soffit": 0.2,
                       "at": [[r4(gx[0]), 0, r4(gz[2]), GOT_YAW]], "_about": "the winding stair up to the upper chapel in the lower chapel's north-west bay"})
add("gotthard upper vaults", {"type": "groin", "width": r4(gw), "length": r4(gl), "springing": 11.5, "top": 15.6, "across": PTD(gspread(gl / 2, gw / 2)), "along": SEMI,
                              "at": [[r4(x), 0, r4(z), 0] for x in gx for z in gz]})
for w in ("lower", "upper"): add(f"gotthard {w} ribs", {"type": "ribs", "on": f"gotthard {w} vaults", "width": 0.3, "depth": 0.22})
add("gotthard columns", {"type": "column", "radius": 0.35, "height": 4.0, "sides": 12, "at": [[r4(x), 0, r4(z), 0] for x in (gx[0] + gw / 2, gx[1] + gw / 2) for z in (gz[0] + gl / 2, gz[1] + gl / 2)]})
add("gotthard upper columns", {"type": "column", "radius": 0.3, "height": 4.7, "sides": 12, "at": [[r4(x), 6.8, r4(z), 0] for x in (gx[0] + gw / 2, gx[1] + gw / 2) for z in (gz[0] + gl / 2, gz[1] + gl / 2)]})
add("gotthard roof", {"type": "roof", "form": "hip", "width": r4(GX_1 - GX_0 + 0.6), "length": r4(GZ_1 - GZ_0 + 0.6), "pitch": 38, "at": [[r4(gcx), GOT_H, r4(gcz), 0]]})
add("gotthard apse", comp("gallery-apse", {"R": 3.75, "T": 1.0, "spring": 8.0, "conchT": 0.6, "arcT": 0.4, "pass": 0.6, "galH": 2.6, "roofRise": 3.0,
                                           "winW": 0.9, "winSill": 3.0, "winSpring": 6.0, "galW": 0.6, "galSill": 0.8},
                          [[-36.15, 0, GZ_0, math.pi]], _about="its apse, with a dwarf gallery of its own"))
seg("gotthard passage north", (-29.1, 30.5), (-TX, 30.5), 0.6, 4.5, [{"openings": []}], about="the passage between the north transept and the Gotthardkapelle")
seg("gotthard passage south", (-TX, 27.5), (-29.1, 27.5), 0.6, 4.5, [{"openings": []}])
add("gotthard passage roof", {"type": "roof", "form": "gable", "width": 3.6, "length": r4(29.1 - TX), "pitch": 35, "at": [[r4(-(29.1 + TX) / 2), 4.5, 29.0, Q]]})
interior("gotthard passage interior", -29.1, -TX, 27.8, 30.2, 4.5)
# the Domhaeuser built against the north chapels (OSM): the Dom-Cafe, two storeys under a mansard; the Dominformation
PLAIN = lambda n: (lambda L, j, hs: [{"at": r4(-L / 2 + L * (k + 0.5) / n), "width": 1.2, "sill": 0.9, "springing": 2.6, "head": {"profile": "flat"}} for k in range(n)])
block(add, "dom-cafe", -45.5, -CHX - 1.6, -6.2, 9.0, 0, 8.4, 2, {0: PLAIN(5), 2: PLAIN(5), 3: PLAIN(4)}, t=0.6, skip=(1,), interior=False,
      about="the Dom-Cafe, one of the Domhaeuser built against the north chapels (OSM 146459812): plastered, two storeys under a slate mansard")
add("dom-cafe roof", {"type": "roof", "form": "mansard", "width": r4(45.5 - CHX - 1.6 + 0.4), "length": 15.6, "pitch": 30, "lowerPitch": 70, "breakH": 3.0,
                      "at": [[r4(-(45.5 + CHX + 1.6) / 2), 8.4, 1.4, 0]]})
block(add, "dominformation", -47.0, -CHX - 1.6, 14.8, 24.7, 0, 7.0, 2, {0: PLAIN(5), 2: PLAIN(5), 3: PLAIN(3)}, t=0.6, skip=(1,), interior=False,
      about="the Dominformation, the other (OSM 146459813)")
add("dominformation roof", {"type": "roof", "form": "mansard", "width": r4(47.0 - CHX - 1.6 + 0.4), "length": 10.3, "pitch": 30, "lowerPitch": 70, "breakH": 2.6,
                            "at": [[r4(-(47.0 + CHX + 1.6) / 2), 7.0, 19.75, 0]]})

# ================================================================ THE PAVEMENT: sandstone flags at the ground's level wherever there is a floor under a roof
def pave(name, x0, x1, z0, z1, about=None):
    slab(name, x0, x1, z0, z1, 0.05, h=0.05, about=about)
pave("pavement body", -(CHX - 0.8), CHX - 0.8, EE_IN, ZW, about="the pavement: the nave, aisles, chapels, the east transept and the crypt")
pave("pavement west transept", -(TX - TT), TX - TT, ZW, WIN1 + 0.4)
add("pavement apse", {"type": "prism", "plan": {"sides": 16, "radius": 6.4}, "height": 0.05, "flatRoof": True, "walked": True, "at": [[0, 0, EZ0, 0]]})
pave("pavement apse arch", -5.9, 5.9, EZ0 - 0.2, EE_IN)
pave("pavement memorie", MX0, MX1, MZ0, MZ1)
pave("pavement cloister west", 31.2, SX0 + 0.4, GZ1, ZW)
pave("pavement cloister south", SX0 - 0.4, KS_X1, EZ_1 - 11.2, ZW)
pave("pavement cloister east", CHX, SX0 - 0.4, EZ_1 - 11.2, GZ0)
pave("pavement gotthard", GX_0, GX_1, GZ_0, GZ_1)
pave("pavement gotthard passage", -29.1 - 0.3, -TX + 0.2, 27.5, 30.5)
add("pavement gotthard apse", {"type": "prism", "plan": {"sides": 12, "radius": 2.8}, "height": 0.05, "flatRoof": True, "walked": True, "at": [[-36.15, 0, GZ_0, 0]]})

# ================================================================ INSIDE: pews in the nave toward the east choir, the altars, the west choir's stalls
add("seating", {"type": "zone", "zone": "seating", "w": 2 * NX - 1.6, "d": r4(ZW - 2.0 - (EW_IN + N_UP * 0.3 + 2.0)), "h": 12,
                "at": [[0, 0, r4((ZW - 2.0 + EW_IN + N_UP * 0.3 + 2.0) / 2), Q]]})
add("east altar", {"type": "zone", "zone": "altar", "w": 6, "d": 2.4, "h": 10, "at": [[0, CHOIR_Y, -37.0, Q]], "_about": "the altar in the east choir"})
add("west altar", {"type": "zone", "zone": "altar", "w": 6, "d": 2.4, "h": 10, "at": [[0, r4(WCH_Y), 53.0, -Q]], "_about": "the high altar in the west choir"})
for sx in (-1, 1):
    add(f"choir stalls {'north' if sx < 0 else 'south'}", {"type": "zone", "zone": "choir", "w": 9.0, "d": 2.6, "h": 8, "at": [[r4(sx * 4.9), r4(WCH_Y), CC, 0 if sx < 0 else math.pi]],
        **({"_about": "the late-Baroque choir stalls (1767) down both sides of the west choir"} if sx < 0 else {})})

doc = {"name": "Mainz Cathedral",
       "_about": "MAINZ CATHEDRAL (Hoher Dom St. Martin, 975-1239), red Main sandstone, a DOUBLE-CHOIR basilica on OpenStreetMap's plan: the east transept and crossing under the octagonal east tower, its apse with the dwarf gallery and the two round stair towers on its corners, the east choir raised over the hall crypt; the nave of ten round arches a side under five rib vaults, the aisles, the Gothic chapels between buttresses under copper lean-tos, the Marktportal's vestibule between the Domhaeuser; the west transept and the Westturm (Romanesque octagon, Gothic belfry and clock, Neumann's balustrade, stone stages and helm, 83.5 m); the trefoil west choir raised nine steps with its stalls, three polygonal conchs with dwarf galleries, their crossing gables and roses, St Martin on horseback, two slender towers in its angles, the sacristy round its foot; on the south the Memorie and the cloister's three vaulted walks round the garth, the Dommuseum over them; on the north the Gotthardkapelle. (tools/archgen/mainz.py)",
       "params": {"detail": 4}, "railing": {"type": "stone"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/mainz.json"), "w").write(json.dumps(doc, indent=2) + "\n")

# ================================================================ THE FINISH
VAULTS = [n for n in parts if parts[n]["type"] in ("groin", "dome") and ("vault" in n or "dome" in n) and "roof" not in n]
SLATE = ["nave roof", "east transept roofs", "east tower roof", "east tower gables", "west transept roofs", "west choir roofs", "west choir cross roof",
         "memorie roof", "cloister roofs", "cloister south roof", "cloister east roof", "gotthard roof", "gotthard passage roof", "dom-cafe roof", "dominformation roof",
         "east apse/roof", "gotthard apse/roof", "south stair tower/cap", "north stair tower/cap", "cloister walk roof"] + [f"{c} conch roof" for c, _, _ in CONCHES]
COPPER = ["lean-to north", "lean-to south", "lean-to south west", "sacristy roof"]
STONE_TOP = ["west tower 2 roof", "west tower 3 roof", "west tower helm", "west tower spire", "west tower lantern", "west tower balustrade", "west tower pinnacles", "west tower 3 pinnacles",
             "west choir tower caps", "west choir tower spikes", "west choir tower lanterns"]
HOUSES = ["dom-cafe", "dominformation"]
fin = {"name": "Mainz Cathedral", "building": "architecture/mainz",
       "_about": "Mainz Cathedral: red Main sandstone in courses, a paler band now and then, the dressings -- lesenes, Lombard friezes, the openings' orders, cornices -- paler still; slate on the nave, the transepts, the towers' tents and cones, the choirs and conchs, the Memorie, the cloister and the Gotthardkapelle; green copper on the lean-tos over the aisles and chapels and on the sacristy; Neumann's crown all stone, the cock gilt. Inside the walls in the red-ochre paint of the 1970s restoration with white joints drawn on it, the vaults pale with their joints, the ribs red stone; sandstone flags underfoot; the Domhaeuser plastered white.",
       "stone": {"color": "#a4513b", "accent": "#c99a7a", "pat": "ashlar"},
       "rules": [
           {"parts": ["domsgickel", "east tower finial"], "pattern": "roofs/gold leaf", "_about": "the gilt cock and cross"},
           {"parts": ["west tower clock/ring", "west tower clock/hands", "west tower clock/marks"], "pattern": "roofs/gold leaf", "_about": "the clock's gilt ring, marks and hands on a dark dial"},
           {"parts": ["west tower clock/dial", "west tower clock/hub"], "pattern": "roofs/sheet metal", "palette": "iron"},
           {"parts": "kind:glass", "opening": "round", "map": "opening", "pattern": "glass/rose wheel", "palette": "chartres", "_about": "the roses in colour"},
           {"parts": "kind:glass", "opening": "head", "map": "opening", "pattern": "glass/tracery white", "palette": "grisaille"},
           {"parts": "kind:glass", "opening": "tall", "nth": [3, 1], "map": "opening", "turn": 90, "pattern": "glass/saint bishop", "palette": "chartres"},
           {"parts": "kind:glass", "opening": "tall", "map": "opening", "pattern": "glass/grisaille lattice", "palette": "grisaille"},
           {"parts": "kind:glass", "map": "opening", "pattern": "glass/quarries", "palette": "grisaille", "_about": "leaded quarries elsewhere"},
           {"parts": COPPER, "pattern": "roofs/sheet metal", "palette": "copper", "_about": "green copper on the lean-tos and the sacristy"},
           {"parts": STONE_TOP, "pattern": "stone/ashlar", "palette": "red-sandstone", "_about": "Neumann's stone crown: the roofs of its stages, the helm, the spire, the balustrade; the side towers' caps"},
           {"parts": [p for p in SLATE if "/" not in p] + [p for p in SLATE if "/" in p], "surface": "roof", "pattern": "roofs/slate", "palette": "slate", "_about": "slate"},
           {"parts": ["kind:roof"], "surface": "wall", "pattern": "stone/banded ashlar", "palette": "mainz", "_about": "the gables' faces in the walls' stone"},
           {"parts": HOUSES, "side": "out", "surface": "wall", "pattern": "stone/plaster", "palette": "plaster-white", "_about": "the Domhaeuser plastered white"},
           {"parts": ["st martin"], "pattern": "stone/ashlar fine", "palette": "rose-sandstone"},
           {"parts": ["garth"], "pattern": "materials/grass", "palette": "lawn"},
           {"parts": ["kind:ribs", "kind:column", "crypt capitals"], "pattern": "stone/ashlar fine", "palette": "red-sandstone", "_about": "the ribs and columns red stone"},
           {"parts": VAULTS, "side": "in", "pattern": "stone/stucco lines", "palette": "mainz-vault", "_about": "the vaults' webs pale, their joints drawn on"},
           {"parts": "kind:moulding", "pattern": "stone/ashlar fine", "palette": "rose-sandstone", "_about": "the dressings paler: lesenes, Lombard friezes, orders, cornices"},
           {"surface": "floor", "side": "in", "pattern": "floors/flagstones", "palette": "sandstone-grey", "_about": "sandstone flags inside"},
           {"surface": "floor", "pattern": "floors/flagstones", "palette": "red-sandstone"},
           {"surface": "wall", "side": "in", "pattern": "stone/stucco lines", "palette": "mainz-paint", "_about": "inside, the red-ochre paint with white joints drawn on"},
           {"surface": "wall", "pattern": "stone/banded ashlar", "palette": "mainz", "_about": "red sandstone in courses, a paler band now and then"},
           {"pattern": "stone/ashlar", "palette": "red-sandstone", "_about": "whatever else is stone"}]}
open(os.path.join(ROOT, "assets/finishes/mainz.json"), "w").write(json.dumps(fin, indent=2) + "\n")

doors = {"name": "Mainz Cathedral: doors", "building": "mainz",
         "_about": "Mainz's doors: on the north the MARKTPORTAL with the bronze doors Archbishop Willigis had cast about 1000 (Master Berenger), lion-headed rings on their leaves; the Leichhof portal in the south transept's end in oak; the small doors to the cloister, the Memorie, the crypt and the round stair towers. (+z is west, +x south.)",
         "doors": [
             {"_about": "the Marktportal: Willigis's bronze doors", "part": "chapel wall north portal", "near": [-CHX, MARKT_Z], "style": "bronze", "color": "#5a4a30"},
             {"_about": "the Leichhof portal in the south transept's end", "part": "west transept south end", "near": [TX, r4(WC + 0.6)], "style": "romanesque"},
             {"_about": "the door from the east transept into the cloister", "part": "east transept south end", "near": [EX, -30.6], "style": "tower"},
             {"_about": "the crypt's door", "part": "crypt front", "style": "tower"},
             {"_about": "the stair towers' doors", "part": "south stair tower/shaft door", "style": "tower"},
             {"part": "north stair tower/shaft door", "style": "tower"}]}
open(os.path.join(ROOT, "assets/doors/mainz.json"), "w").write(json.dumps(doors, indent=2) + "\n")

# ---------------------------------------------------------------- the component: a round stair tower (also Maria Laach's, Ulm's, Sacre-Coeur's)
TOWER = {
  "name": "Round stair tower",
  "_about": "A ROUND STAIR TOWER standing on its own (against a wall, in the angle of a choir): a ring of `n` bays, a door at its foot in bay `doorBay`, a spiral inside from the ground up to `H`, where it arrives on its landing at a door out (bay `exitBay`, worked out from where the spiral ends) -- onto a terrace or a gallery the caller builds there; above that an open belvedere of arches over a parapet, a cornice and a cone. Place it at its middle. `steps` may be chosen (12-22cm each) so the stair arrives facing the way the caller wants. Mainz's east towers.",
  "params": {
    "detail": 4, "R": 3.6, "wall": 0.8, "H": 20.0, "n": 12, "newel": 0.2, "turn": 24,
    "steps": "round(H / 0.19)", "doorBay": 0, "stageH": 4.0, "capRise": 6.0, "finial": 1.6, "doorW": 1.2, "archW": 1.1,
    "_doorW": "its doors' width (and `archW` the belvedere's arches'): a narrower tower has narrower bays",
    "_R": "the tower's outside radius; `wall` its thickness; H the level the stair arrives at (the terrace's)",
    "_steps": "the spiral's steps: the landing's bearing follows from their number, so a caller picks it to arrive facing the door it wants",
    "sr": "R - wall - 0.05", "rA": "(sr + newel) / 2", "land": "max(1.2, sr - newel)",
    "exitBay": "round(doorBay + steps * turn * n / 360 + land / rA / 2 * n / 6.2831853)",
    "_exitBay": "the bay the landing reaches: the first step's bearing, the steps' turns, and half the landing's arc"
  },
  "build": ["shaft", "shaft door", "stair", "belvedere", "belvedere door", "cornice", "cap", "finial"],
  "parts": {
    "shaft": {"type": "ring", "count": "n", "rOuter": "R", "rInner": "R - wall", "height": "H", "place": [[0, 0, 0, 0]], "skip": ["doorBay"], "solid": True,
              "_about": "the round shaft, from the ground to the stair's head"},
    "shaft door": {"type": "ring", "count": "n", "rOuter": "R", "rInner": "R - wall", "height": "H", "place": [[0, 0, 0, 0]], "at": ["doorBay"],
                   "opening": {"width": "doorW", "sill": 0, "springing": 2.0, "head": {"profile": "semicircular"}}},
    "stair": {"type": "spiral-stair", "radius": "sr", "newel": "newel", "turn": "turn", "top": "H", "steps": "steps", "soffit": 0.2,
              "at": [[0, 0, 0, "doorBay * 6.2831853 / n"]], "_about": "the spiral, its first step at the door, its landing at the door out"},
    "belvedere": {"type": "ring", "count": "n", "rOuter": "R", "rInner": "R - wall", "height": "stageH", "y": "H", "place": [[0, 0, 0, 0]],
                  "skip": ["exitBay"], "glass": False,
                  "opening": {"width": "archW", "sill": 1.0, "springing": "stageH - 0.6 - archW / 2", "head": {"profile": "semicircular"}},
                  "_about": "the belvedere at the stair's head: an arch in every bay over a parapet..."},
    "belvedere door": {"type": "ring", "count": "n", "rOuter": "R", "rInner": "R - wall", "height": "stageH", "y": "H", "place": [[0, 0, 0, 0]],
                       "at": ["exitBay"], "glass": False,
                       "opening": {"width": "doorW", "sill": 0, "springing": "stageH - 0.6 - doorW / 2", "head": {"profile": "semicircular"}},
                       "_about": "...and the door out, where the landing arrives"},
    "cornice": {"type": "prism", "plan": {"sides": "n", "radius": "R + 0.2"}, "height": 0.35, "at": [[0, "H + stageH", 0, 0]], "flatRoof": True,
                "standsOn": ["belvedere"], "_about": "the ceiling over the belvedere and the cornice the cone stands on"},
    "cap": {"type": "dome", "sides": "n", "radius": "R + 0.2", "thickness": 0, "head": {"profile": "trigonal", "rise": "capRise"},
            "at": [[0, "H + stageH + 0.35", 0, 0]], "standsOn": ["cornice"]},
    "finial": {"type": "column", "radius": 0.12, "height": "finial", "sides": 6, "at": [[0, 0, 0, 0]], "atop": "cap", "standsOn": ["cap"]},
    "interior": {"type": "interior", "of": ["shaft", "shaft door"], "plan": {"sides": "n", "radius": "R - wall / 2"}, "height": "H",
                 "_about": "the shaft's well, up to the belvedere (open: the air's)"}
  }
}
open(os.path.join(ROOT, "assets/architecture/components/round-stair-tower.json"), "w").write(json.dumps(TOWER, indent=2) + "\n")
print("mainz:", len(parts), "parts")
