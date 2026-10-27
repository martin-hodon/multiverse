#!/usr/bin/env python3
"""THE PALACE OF VERSAILLES (2026-10-02, was architecture.js baroquePalace + its `versailles` plan): the garden front
and the court as an arch-engine definition (assets/architecture/versailles.json) and its finish -- the plan set out by
the same rules the code laid it by, written out once as parts.

A plan of rectangular BLOCKS, each a hollow three-storey shell (ground, piano nobile, attic) with the endlessly repeated
baroque bay -- a ground window, a tall piano-nobile window between pilasters, a square attic window -- and its orders:
each block ONE enclosure, its courses mitred round its corners, Ionic pilasters through the piano nobile and a Tuscan
attic order over them (arch/order.js: each sized from its storey, its entablature the cornice), a flat roof behind a
balustrade. Where two blocks stand face to face the shared plane is a PARTY WALL: no windows, no
trim, and a passage through it is ONE doorway (the later block's snaps onto the earlier one's and leaves the door panel
to it). The ramp blocks have a real stair to each storey through a stairwell in the slab, railed round its drop. Rooms
along each block's long axis open into each other through an enfilade of aligned doorways; the corps central's piano
nobile keeps its garden half one long hall -- the HALL OF MIRRORS: tall mirrors in gilt frames on the partition's gallery
face (`mirror` markers: the game makes them reflect, within their `room`), and behind each, on the salon side, a framed
canvas (`painting` markers: a view of the world, taken at the start). Chandeliers and salon groups in the corps, beds
and wardrobes in the outer wings (the plain furniture items). Every window an openable GLASS pane (`site.glazed`).

    python3 tools/archgen/versailles.py
"""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PI, PI2 = 3.14159265, 1.5707963
R = lambda v: round(v, 4)


def write(base, path, doc):
    full = os.path.join(ROOT, "assets", base, path + ".json")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(json.dumps(doc, indent=1) + "\n")


def jround(v): return math.floor(v + 0.5)   # (JavaScript's Math.round: the plan was laid by it)
def linspace(a, b, k): return [a + (b - a) * i / (k - 1) for i in range(k)]


STOREYS = [5.2, 7.8, 5.5]
LV = [0.0, 5.2, 13.0, 18.5]
H = LV[3]
BAY, T, ROOM = 5.5, 1.0, 11
DOOR_W, DOOR_H, RAMP_W = 3.4, 4.2, 2.0
BLOCKS = [
    {"name": "corps", "x": 0, "z": -21, "w": 100, "d": 24, "ramp": True, "gallery": True, "gilt": True,
     "door": [["s", 0], ["s", -41], ["s", 41], ["n", 0], ["w", 6], ["e", 6]]},   # (the end doors 6 m toward the court: clear of the stairs)
    {"name": "north court wing", "x": -41, "z": 12, "w": 18, "d": 42, "brick": True, "gilt": True, "door": [["e", 0], ["n", 0]], "plain": ["n"]},
    {"name": "south court wing", "x": 41, "z": 12, "w": 18, "d": 42, "brick": True, "gilt": True, "door": [["w", 0], ["n", 0]], "plain": ["n"]},
    {"name": "north wing", "x": -107.5, "z": -22.5, "w": 115, "d": 21, "ramp": True, "door": [["s", 0], ["e", 7.5]], "plain": ["e"]},
    {"name": "south wing", "x": 107.5, "z": -22.5, "w": 115, "d": 21, "ramp": True, "door": [["s", 0], ["w", 7.5]], "plain": ["w"]},
]
FACES = {"n": (0, -1), "s": (0, 1), "e": (1, 0), "w": (-1, 0)}
OPP = {"n": "s", "s": "n", "e": "w", "w": "e"}
YAW = {"s": 0, "n": PI, "e": PI2, "w": -PI2}          # a wall's outer face looks out of its block
PANE_YAW = {"s": 0, "n": 0, "e": -PI2, "w": -PI2}     # (a pane or a door turns with its wall's line, not its side)


def face_len(b, f): return b["w"] if f in "ns" else b["d"]


def at_(b, f, u, out):   # u along face f, `out` from the wall's middle line (outward)
    nx, nz = FACES[f]
    if f in "ns": return b["x"] + u, b["z"] + nz * (b["d"] / 2 - T / 2 + out)
    return b["x"] + nx * (b["w"] / 2 - T / 2 + out), b["z"] + u


def wall_at(b, f):   # a wall part's placement: its outer face on the block's edge
    nx, nz = FACES[f]
    return [R(b["x"] + nx * b["w"] / 2), 0, R(b["z"] + nz * b["d"] / 2), YAW[f]]


# the long walls (n, s) run the block's whole width and hold its corners; the ends (e, w) stand between them, 2T shorter
# (one wall's end in the plane of the other's face would flicker)
def wall_len(b, f): return b["w"] if f in "ns" else b["d"] - 2 * T

def contacts(b, f):
    nx, nz = FACES[f]; along = f in "ns"; out = []
    for o in BLOCKS:
        if o is b: continue
        mine = b["z"] + nz * b["d"] / 2 if along else b["x"] + nx * b["w"] / 2
        theirs = o["z"] - nz * o["d"] / 2 if along else o["x"] - nx * o["w"] / 2
        if abs(mine - theirs) > 0.05: continue
        if along: u0, u1 = max(b["x"] - b["w"] / 2, o["x"] - o["w"] / 2) - b["x"], min(b["x"] + b["w"] / 2, o["x"] + o["w"] / 2) - b["x"]
        else: u0, u1 = max(b["z"] - b["d"] / 2, o["z"] - o["d"] / 2) - b["z"], min(b["z"] + b["d"] / 2, o["z"] + o["d"] / 2) - b["z"]
        if u1 - u0 > 0.5: out.append((u0, u1, o))
    return out


parts = {}
ROOF_STATUES = []   # (block, face, u): where the statues stand on the roofline's balustrade
BOXES = {}   # (name, w, l, h) -> placements: boxes of a size are one part
def box(name, w, l, h, x, y, z, yaw=0):   # (y: its bottom)
    BOXES.setdefault((name, R(w), R(l), R(h)), []).append([R(x), R(y), R(z), yaw])
# a facade trim box along face f: `along` the face, `thick` across it, its middle `y` (as the code had it), `out` from the wall's line
def fbox(name, b, f, u, out, along, h, y, thick):
    x, z = at_(b, f, u, out)
    box(name, along, thick, h, x, y - h / 2, z, 0 if f in "ns" else PI2)


doors, wins, mirrors, paintings, cobwebs = [], {0: [], 1: [], 2: []}, [], [], []
WIN = [(1.15, 1.7, 3.6), (LV[1] + 1, 1.9, 4.8), (LV[2] + 0.9, 1.4, 2.1)]   # sill, width, height, storey by storey
FACE_NO = {"s": 0, "e": 1, "n": 2, "w": 3}   # (a rect enclosure's faces: +z, +x, -z, -x; each runs from its first corner, `at` from its middle)
BAL_H, BAL_T = 1.0, 0.3                      # the balustrade on the wall heads, round the roof's 0.4m slab (its top BAL_H over the slab)
walls, balustrades = [], []
for bi, b in enumerate(BLOCKS):
    door_list, plain = b.get("door", []), b.get("plain", [])
    faces, clear = {}, {}
    for f in "nsew":
        L, along, cts = face_len(b, f), f in "ns", contacts(b, f)
        in_contact = lambda u, half: next((c for c in cts if u + half > c[0] - 0.3 and u - half < c[1] + 0.3), None)
        fdoors = []
        for df, u in door_list:
            if df != f: continue
            c = in_contact(u, DOOR_W / 2)
            if not c or BLOCKS.index(c[2]) > bi: fdoors.append((u, True)); continue
            o = c[2]
            theirs = [(o["x"] + ou - b["x"]) if along else (o["z"] + ou - b["z"]) for odf, ou in o.get("door", []) if odf == OPP[f]]
            near = next((ou for ou in theirs if abs(ou - u) < 3.5), None)
            if near is not None: fdoors.append((near, False))   # (no doorway opposite: the passage would end in their wall)
        is_plain = f in plain
        nb = max(1, jround(L / BAY) - 1)
        us = [] if is_plain else ([0] if nb == 1 else linspace(-(L / 2 - BAY * 0.8), L / 2 - BAY * 0.8, nb))
        us = [u for u in us if not in_contact(u, 1.3)]
        fw = []
        for u in us:
            for k, (wy, ww, wh) in enumerate(WIN):
                if wy < LV[1] and any(abs(u - du) < DOOR_W / 2 + 1.2 for du, _ in fdoors): continue
                fw.append((u, k, wy, ww, wh))
        # the face in three tiers, a storey each (a window may stand over a door), its openings from the face's middle
        mid = lambda u: R(u if f in ("s", "w") else -u)
        tiers = [{"h": STOREYS[0], "openings": [{"at": mid(du), "width": DOOR_W, "sill": 0, "springing": DOOR_H, "head": {"profile": "flat"}} for du, _ in fdoors]},
                 {"h": STOREYS[1], "openings": []}, {"openings": []}]
        # (the ground storey's and the piano nobile's windows round-headed, the attic's square; each DRESSED -- surround.js:
        #  an architrave round it and a sill, a keystone in an arch, and on the brick wings' piano nobile a cornice over)
        for u, k, wy, ww, wh in fw:
            arched = k < 2
            dress = {"head": "cornice" if (k == 1 and b.get("brick")) else False, **({"keystone": True} if arched else {})}
            tiers[k]["openings"].append({"at": mid(u), "width": ww, "sill": R(wy - LV[k]), "springing": R(wy + wh - LV[k] - (ww / 2 if arched else 0)),
                                         "head": {"profile": "semicircular" if arched else "flat"}, "surround": dress})
        faces[str(FACE_NO[f])] = tiers
        # where another block stands against it: no moulding, no pilaster (a party wall), and no balustrade over it
        spans = sorted((R(L / 2 + min(mid(c[0]), mid(c[1]))), R(L / 2 + max(mid(c[0]), mid(c[1])))) for c in cts)
        if spans: clear[str(FACE_NO[f])] = [list(sp) for sp in spans]
        for du, panel in fdoors:
            if panel: x, z = at_(b, f, du, 0); doors.append([R(x), 0.2, R(z), PANE_YAW[f]])
        for u, k, wy, ww, wh in fw:   # every window an openable glass pane
            x, z = at_(b, f, u, 0); wins[k].append([R(x), R(wy - 0.075), R(z), PANE_YAW[f]])
        # THE BALUSTRADE along the face's head, less what stands against another block: a parapet pierced between its
        # balusters (the long faces full length, the ends between them)
        lo, hi = (-L / 2, L / 2) if along else (-L / 2 + BAL_T, L / 2 - BAL_T)
        free, at0 = [], lo
        for c0, c1, _ in sorted(cts, key=lambda c: c[0]):
            if c0 - at0 > 1.0: free.append((at0, c0))
            at0 = max(at0, c1)
        if hi - at0 > 1.0: free.append((at0, hi))
        for a0, a1 in free:
            w = a1 - a0
            nx, nz, uc = *FACES[f], (a0 + a1) / 2
            x, z = (b["x"] + uc, b["z"] + nz * b["d"] / 2) if along else (b["x"] + nx * b["w"] / 2, b["z"] + uc)   # (its outer face on the block's edge)
            balustrades.append({"type": "wall", "width": R(w), "height": 0.4 + BAL_H, "thickness": BAL_T, "glass": False,
                                "openings": {"pattern": str(max(1, int((w - 0.6) // 0.5))), "width": 0.32, "gap": 0.18, "sill": 0.62, "springing": 1.2, "head": {"profile": "flat"}, "glass": False},
                                "at": [[R(x), R(H), R(z), YAW[f]]]})
        if is_plain: continue
        for i, u in enumerate(us):
            if i < len(us) - 1 and b["name"] == "corps" and f in "sn" and i % 2 == 0: ROOF_STATUES.append((b, f, u + BAY / 2))   # (a statue over every other pier)
    # ONE ENCLOSURE a block: its courses mitred round its corners -- the plinth, the string course over the ground storey
    # -- and the stone blocks' two ORDERS (order.js): Ionic pilasters through the piano nobile, a Tuscan attic order over
    # them, each sized from its storey, their entablatures the floor line and the crowning cornice; the old chateau's
    # brick wings only their courses
    walls.append((b["name"], {"type": "enclosure", "plan": {"rect": [b["w"], b["d"]]}, "thickness": T, "height": H, "glass": False, "faces": faces,
                              "courses": {**({"clear": clear} if clear else {})},
                              **({} if b.get("brick") else {"orders": [{"tier": 1, "kind": "ionic"}, {"tier": 2, "kind": "tuscan"}]}),
                              "at": [[b["x"], 0, b["z"], 0]]}))

    # the roof and the floors: the attic's boarded ceiling, marble flags downstairs, parquet above (a stairwell through it)
    box("roof", b["w"] - 2 * BAL_T, b["d"] - 2 * BAL_T, 0.4, b["x"], H, b["z"])   # (within the balustrade, on the wall heads)
    box("attic ceiling", b["w"] - 2 * T, b["d"] - 2 * T, 0.12, b["x"], H - 0.13, b["z"])
    box("ground floor", b["w"] - 0.02, b["d"] - 0.02, 0.2, b["x"], 0, b["z"])   # (under the walls too: a doorway has its floor; 1cm in from the faces)
    zR0, zR1 = b["z"] + b["d"] / 2 - 2.6, b["z"] - b["d"] / 2 + 2.6
    run = zR0 - zR1
    rampX = [b["x"] - b["w"] / 2 + T + 1.3, b["x"] + b["w"] / 2 - T - 1.3]
    for s in (1, 2):
        y = LV[s]
        if not b.get("ramp"): box("upper floor", b["w"] - 2 * T, b["d"] - 2 * T, 0.3, b["x"], y, b["z"]); continue
        side = s - 1; hx = rampX[side]
        hz0, hz1 = (zR1, zR1 + run * 0.5) if side == 0 else (zR0 - run * 0.5, zR0)   # headroom for a 2m walker
        x0, x1 = hx - RAMP_W / 2 - 0.2, hx + RAMP_W / 2 + 0.2
        iw0, iw1, id0, id1 = b["x"] - b["w"] / 2 + T, b["x"] + b["w"] / 2 - T, b["z"] - b["d"] / 2 + T, b["z"] + b["d"] / 2 - T
        box("upper floor", x0 - iw0, id1 - id0, 0.3, (x0 + iw0) / 2, y, b["z"])
        box("upper floor", iw1 - x1, id1 - id0, 0.3, (x1 + iw1) / 2, y, b["z"])
        box("upper floor", x1 - x0, hz0 - id0, 0.3, (x0 + x1) / 2, y, (hz0 + id0) / 2)
        box("upper floor", x1 - x0, id1 - hz1, 0.3, (x0 + x1) / 2, y, (hz1 + id1) / 2)
        # the stairwell's balustrade: along its open side (less the landing's stretch, where one steps off) and across the
        # end that drops onto the flight below (wellRail, as it was)
        top, rail_side, land_z0 = y + 0.3, (1 if side == 0 else -1), side == 0
        xo = x1 if rail_side > 0 else x0
        za, zb = (hz0 + 1.05, hz1) if land_z0 else (hz0, hz1 - 1.05)
        n = max(1, jround((zb - za) / 0.45))
        for i in range(n + 1): box("well rails", 0.08, 0.08, 0.95, xo, top, za + (zb - za) * i / n)
        box("well rails", 0.07, zb - za + 0.08, 0.07, xo, top + 0.915, (za + zb) / 2)
        zd = hz1 if land_z0 else hz0
        n2 = max(1, jround((x1 - x0) / 0.45))
        for i in range(1, n2): box("well rails", 0.08, 0.08, 0.95, x0 + (x1 - x0) * i / n2, top, zd)
        box("well rails", x1 - x0 + 0.08, 0.07, 0.07, (x0 + x1) / 2, top + 0.915, zd)
        # the flight up to it: a real staircase (a stair of 19cm on 32cm, arriving on a landing metre at the well's end)
        base, rise = (0.2, LV[1] + 0.1) if s == 1 else (LV[1] + 0.3, STOREYS[1])
        steps = math.ceil(rise / 0.19); tread = 0.32; length = steps * tread + 1.0
        if side == 0: place = [R(hx + RAMP_W / 2), R(base), R(zR1 + length), PI2]   # climbing toward -z, its width toward -x
        else: place = [R(hx - RAMP_W / 2), R(base), R(zR0 - length), -PI2]          # climbing toward +z, its width toward +x
        parts[f"{b['name']} stair {s}"] = {"type": "flight", "run": tread, "width": RAMP_W, "base": 0, "top": R(rise), "steps": steps, "landing": 1.0, "at": [place]}

    # the rooms: partitions across the long axis with an enfilade of aligned doorways, marble-lined downstairs and panelled
    # on the piano nobile; `gallery` keeps the piano nobile's garden half one long hall behind a doored longitudinal wall
    longX = b["w"] >= b["d"]
    pT, pdW = 0.4, 2.4
    axis_len = b["w"] if longX else b["d"]
    p0 = (b["x"] if longX else b["z"]) - axis_len / 2
    n_rooms = math.floor(axis_len / ROOM)
    def pwall(name, pos, y0p, hgt, s0, s1, door_u):
        def mk(a2, b2):
            if b2 - a2 <= 0.25: return
            if longX: box(name, pT, b2 - a2, hgt, pos, y0p, (a2 + b2) / 2)
            else: box(name, b2 - a2, pT, hgt, (a2 + b2) / 2, y0p, pos)
        mk(s0, door_u - pdW / 2); mk(door_u + pdW / 2, s1)
        lh = hgt - 3.2
        if lh > 0.1:
            if longX: box(name, pT, pdW, lh, pos, y0p + 3.2, door_u)
            else: box(name, pdW, pT, lh, door_u, y0p + 3.2, pos)
    s0 = (b["z"] - b["d"] / 2 if longX else b["x"] - b["w"] / 2) + T
    s1 = (b["z"] + b["d"] / 2 if longX else b["x"] + b["w"] / 2) - T
    for i in range(1, n_rooms):
        pos = p0 + i * ROOM
        if b.get("ramp") and any(abs(pos - rx) < 2.8 for rx in rampX): continue
        pwall("partition ground", pos, 0.2, LV[1] - 0.2, s0, s1, s0 + 2)
        if b.get("gallery"): pwall("partition piano", pos, LV[1] + 0.3, STOREYS[1] - 0.3, b["z"] + 1.7, s1, b["z"] + 3.2)
        else: pwall("partition piano", pos, LV[1] + 0.3, STOREYS[1] - 0.3, s0, s1, s0 + 2)
    if b.get("gallery"):
        gz, gy, gh = b["z"] + 1.5, LV[1] + 0.3, STOREYS[1] - 0.3
        room = [R(b["x"] - b["w"] / 2 + T), R(b["x"] + b["w"] / 2 - T), R(LV[1] - 0.5), LV[2], R(b["z"] - b["d"] / 2 + T - 0.5), R(gz)]
        def mirror_span(xa_, xb_):
            span = xb_ - xa_
            if span < 3: return
            k = 2 if span > 7 else 1
            w, h = min(2.4, span / k - 1.2), min(gh - 1.6, 5.2)
            zf, yc = gz - pT / 2 - 0.04, gy + 0.7 + h / 2
            for i in range(k):
                xc = xa_ + span * (i + 0.5) / k
                mirrors.append(([R(xc), R(yc), R(zf - 0.01), PI], R(w), R(h)))
                pz, py, pw, ph = gz + pT / 2 + 0.04, gy + 2.1, 2.0, 1.5   # behind it, on the salon side: a framed canvas at eye height
                paintings.append(([R(xc), R(py), R(pz + 0.01), 0], pw, ph))
                for dx, dy, sw, sh in ((0, ph / 2 + 0.07, pw + 0.28, 0.14), (0, -ph / 2 - 0.07, pw + 0.28, 0.14), (-pw / 2 - 0.07, 0, 0.14, ph), (pw / 2 + 0.07, 0, 0.14, ph)):
                    box("frames", sw, 0.08, sh, xc + dx, py + dy - sh / 2, pz)
                for dx, dy, sw, sh in ((0, h / 2 + 0.06, w + 0.24, 0.12), (0, -h / 2 - 0.06, w + 0.24, 0.12), (-w / 2 - 0.06, 0, 0.12, h), (w / 2 + 0.06, 0, 0.12, h)):
                    box("frames", sw, 0.08, sh, xc + dx, yc + dy - sh / 2, zf)
            return room
        xa = b["x"] - b["w"] / 2 + T + 3.2
        xb_end = b["x"] + b["w"] / 2 - T - 3.2
        for i in range(n_rooms):
            dx2 = p0 + (i + 0.5) * ROOM
            if dx2 - 1.2 - xa > 0.3: box("gallery wall", dx2 - 1.2 - xa, pT, gh, (xa + dx2 - 1.2) / 2, gy, gz)
            mirror_span(xa, dx2 - 1.2)
            box("gallery wall", 2.4, pT, gh - 3.2, dx2, gy + 3.2, gz)
            xa = dx2 + 1.2
        if xb_end - xa > 0.3: box("gallery wall", xb_end - xa, pT, gh, (xa + xb_end) / 2, gy, gz)
        mirror_span(xa, xb_end)
        mirror_room = room

# the furnishings: chandeliers and salon groups in the corps' piano nobile, beds and wardrobes along the outer wings'
# ground floors
items = {"chandeliers": [], "tables": [], "chairs": [], "sofas": [], "beds": [], "wardrobes": []}
b0 = BLOCKS[0]
for i in range(math.floor(b0["w"] / ROOM)):
    rc = b0["x"] - b0["w"] / 2 + (i + 0.5) * ROOM          # room centres, clear of the partitions
    items["chandeliers"] += [[R(rc), R(LV[2] - 0.05), b0["z"] - 4, 0], [R(rc), R(LV[1] - 0.05), b0["z"], 0]]   # (the gallery lane on the garden side; the hall below)
    if i % 2 == 0:
        items["tables"].append([R(rc), R(LV[1] + 0.3), b0["z"] - 4, 0])
        items["chairs"] += [[R(rc - 1.5), R(LV[1] + 0.3), b0["z"] - 4, PI2], [R(rc + 1.5), R(LV[1] + 0.3), b0["z"] - 4, R(3 * PI2)]]
        items["sofas"].append([R(rc), R(LV[1] + 0.3), b0["z"] - 7, PI])
for bw in BLOCKS[3:]:
    for i in range(0, math.floor(bw["w"] / ROOM), 2):
        rc = bw["x"] - bw["w"] / 2 + (i + 0.5) * ROOM
        items["beds"].append([R(rc), 0.2, R(bw["z"] + 1.5), 0])
        items["wardrobes"].append([R(rc + 3), 0.2, R(bw["z"] - bw["d"] / 2 + T + 0.45), 0])
    cobwebs += [([R(bw["x"] - bw["w"] / 2 + T), LV[1], R(bw["z"] - bw["d"] / 2 + T), 0], 1, 1, 0.8), ([R(bw["x"] + bw["w"] / 2 - T), LV[1], R(bw["z"] + bw["d"] / 2 - T), 0], -1, -1, 0.7)]

# ---- the definition
for name, w in walls: parts[name] = w
for i, w in enumerate(balustrades): parts[f"balustrade {i + 1}"] = w
counts = {}
for (name, w, l, h), places in BOXES.items():
    counts[name] = counts.get(name, 0) + 1
    parts[f"{name} {counts[name]}"] = {"type": "box", "width": w, "length": l, "height": h, "at": places,
                                       **({"flatRoof": True} if name == "roof" else {})}
ITEM = {"chandeliers": "chandelier", "tables": "plain-table", "chairs": "plain-chair", "sofas": "sofa", "beds": "plain-bed", "wardrobes": "plain-wardrobe"}
for k, places in items.items():
    parts[k] = {"type": "item", "item": "items/furniture/" + ITEM[k], "at": places, **({"solid": False} if k == "chandeliers" else {})}
parts["doors"] = {"type": "marker", "role": "door", "at": doors, "data": {"w": DOOR_W, "h": DOOR_H}}
for k, (wy, ww, wh) in enumerate(WIN):
    parts[f"windows {['ground', 'piano nobile', 'attic'][k]}"] = {"type": "marker", "role": "window", "at": wins[k], "data": {"w": R(ww + 0.15), "h": R(wh + 0.15)}}
parts["mirrors"] = {"type": "marker", "role": "mirror", "at": [m[0] for m in mirrors], "data": {"w": [m[1] for m in mirrors], "h": [m[2] for m in mirrors], "room": [mirror_room for m in mirrors]}}
parts["paintings"] = {"type": "marker", "role": "painting", "at": [p[0] for p in paintings], "data": {"w": 2.0, "h": 1.5}}
parts["cobwebs"] = {"type": "marker", "role": "cobweb", "at": [c[0] for c in cobwebs], "data": {"sx": [c[1] for c in cobwebs], "sz": [c[2] for c in cobwebs], "d": [c[3] for c in cobwebs]}}
# THE ROOFLINE'S STATUES (statuary.py): over every other pier of the corps's two long fronts, standing on the
# balustrade's rail -- the garden front's first (the more prominent), then the court's -- limestone, looking out
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from statuary import statue, capped, FACE_PZ, FACE_NZ
OUTWARD = {"s": FACE_NZ, "n": FACE_PZ}
stat = {}
for i, (b, f, u) in enumerate(sorted(ROOF_STATUES, key=lambda q: q[1] != "s")):
    x, z = at_(b, f, u, T / 2 - BAL_T / 2)   # (on the balustrade's rail, over a pier)
    stat[f"roof statue {f} {i}"] = statue((x, H + 0.4 + BAL_H, z), kind="woman" if i % 3 == 1 else "man", style="roman", stone="limestone", scale=1.35, seed=40 + i, face=OUTWARD[f],
                                          **({"hold": {"R": "items/weapons/spear"}} if i % 4 == 0 else {"hold": {"L": "items/shields/round"}} if i % 4 == 2 else {}))
parts.update(capped(stat))
xs = [v for b in BLOCKS for v in (b["x"] - b["w"] / 2, b["x"] + b["w"] / 2)]
zs = [v for b in BLOCKS for v in (b["z"] - b["d"] / 2, b["z"] + b["d"] / 2)]
write("architecture", "versailles", {"name": "Palace of Versailles",
      "_about": "THE PALACE OF VERSAILLES, garden front and court (a simplified plan at its real scale): the 100 m corps central between 115 m wings on a ~330 m garden front, the court wings in the old chateau's brick embracing the Cour Royale, three storeys (ground, piano nobile, attic) to a balustraded flat roofline at 18.5 m; stairs to every storey in the corps and the wings; rooms in enfilade; the Hall of Mirrors with its mirrors and the canvases behind them; chandeliers, salons, bedrooms. The court opens toward +z. (tools/archgen/versailles.py: the plan's rules, party walls and all.)",
      "site": {"origin": True, "glazed": True},
      "params": {"detail": 4, "footW": max(xs) - min(xs) + 2, "footD": max(zs) - min(zs) + 2}, "parts": parts,
      "build": [k for k in parts if " stair " not in k] + [k for k in parts if " stair " in k]})   # (the stairs once the floors they start on and reach are laid)
write("finishes", "versailles", {"name": "Palace of Versailles", "building": "architecture/versailles",
      "_about": "cream limestone and the old chateau's red brick, gilt trim, a leaded roof, marble flags below and parquet above, marble-lined and gilt-panelled rooms",
      "stone": {"color": "#dfcda4", "accent": "#c3b28c", "pat": "ashlar"},
      "rules": [{"parts": ["gilt trim", "frames"], "pattern": "stone/plaster", "palette": "gold"},
                {"parts": "roof", "pattern": "roofs/sheet metal", "palette": "lead"},
                {"parts": "attic ceiling", "pattern": "timber/boards", "palette": "oak"},
                {"parts": "ground floor", "pattern": "floors/checker", "palette": "marble-grey"},
                {"parts": ["upper floor", "attic ceiling"], "surface": "ceiling", "pattern": "stone/plaster", "palette": "plaster-white"},
                {"parts": "upper floor", "pattern": "floors/basketweave", "palette": "oak"},
                {"parts": "well rails", "pattern": "timber/bark", "palette": "walnut"},
                {"parts": "partition ground", "pattern": "stone/marble", "palette": "carrara"},
                {"parts": ["partition piano", "gallery wall"], "pattern": "panels/wainscot", "palette": "baroque"},
                {"parts": "kind:moulding", "pattern": "stone/ashlar fine", "palette": "limestone"},
                {"parts": ["north court wing", "south court wing"], "side": "out", "pattern": "stone/brick", "palette": "brick"},
                {"parts": ["corps", "north wing", "south wing"], "surface": "wall", "side": "out", "below": 5.2, "pattern": "stone/rusticated", "palette": "limestone"},
                {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
                {"pattern": "stone/ashlar fine", "palette": "limestone"}]})
print("versailles:", len(parts), "parts;", len(doors), "doors,", sum(len(v) for v in wins.values()), "windows,", len(mirrors), "mirrors")
