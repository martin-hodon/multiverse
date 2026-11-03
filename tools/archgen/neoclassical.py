# NEOCLASSICAL: the vocabulary of the classical public building of the 18th and 19th centuries -- capitols, palaces of
# justice, museums, the domed state houses copied from Washington's -- as helpers that compose the engine's parts (an L2
# style library: tools/archgen/README.md). Import it from a landmark's generator:
#
#   Balusters()        a balustrade collector: straight runs and rings of balusters under a rail on a plinth, drawn as three
#                      `bars` parts for the whole building (8 triangles a baluster, a fifth of a pierced wall's)
#   block()            a wing: one `enclosure` of storeys -- a rusticated ground storey, a giant order through the upper ones
#                      (order.js), windows set out on a bay rhythm and dressed (surround.js), doors where asked, none where
#                      another block stands against it --, its floors and its roof slab, the balustrade on its free heads
#   grand_stair()      a straight stair up to a front or a terrace between sloping cheek walls
#   temple_front()     a pedimented portico of `ped` columns between colonnades of `flank` columns, on a podium arcade the
#                      ground storey's height, the grand stair up to it between sloping cheek walls (components/portico)
#   dome_on_drum()     the skirt over the roofs, `drum-dome` with its peristyle, attic, the plinth a narrower dome stands back
#                      on, the ribbed dome and the `tholos` lantern; balustrade rings round the skirt, the peristyle and the
#                      lantern's foot; returns the heights it set (where a statue on top stands)
#   write_tholos()     writes components/tholos, the round temple a dome's lantern is (drum-dome builds it by name)
#
# Conventions: a FACING is "+z", "-z", "+x" or "-x" (the way a front looks out); a front's local frame is u along it (to the
# right, seen from outside... as the engine's yaw turns it) and v out from the wall. Sizes in metres; every function adds
# parts with `add(name, def)` and returns what a caller needs to set further parts against it.
import os, json, math

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R3 = lambda v: round(v, 3)
YAW = {"+z": 0.0, "-z": math.pi, "+x": math.pi / 2, "-x": -math.pi / 2}   # (turns a front's local +z -- its v -- to face that way)


def frame(x, z, facing):
    """the front's local (u, v) to world (x, z): v out of the wall, u along it"""
    t = YAW[facing]
    return lambda u, v: (R3(x + u * math.cos(t) + v * math.sin(t)), R3(z - u * math.sin(t) + v * math.cos(t)))


# ---------------------------------------------------------------------------------------------------------------------
class Balusters:
    """A BALUSTRADE as bars: a plinth, a rail and the balusters between, every run and ring of the building in three
    parts -- the preferred balustrade for a long classical building (a pierced `wall` costs five times the triangles,
    a `railing` is iron). `h` its height, `every` a baluster's spacing, `post` its thickness, `rail` and `plinth` (width, height)."""

    def __init__(self, h=1.1, every=0.5, post=0.16, rail=(0.36, 0.16), plinth=(0.38, 0.22)):
        self.h, self.every, self.post, self.rail, self.plinth = h, every, post, rail, plinth
        self.rails, self.plinths, self.posts = [], [], []

    def run(self, a, b, y):
        """a straight run, its middle line from a (x, z) to b at the height y it stands on"""
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 0.3: return
        yp, yr = y + self.plinth[1] / 2, y + self.h - self.rail[1] / 2
        self.plinths.append([R3(a[0]), R3(yp), R3(a[1]), R3(b[0]), R3(yp), R3(b[1])])
        self.rails.append([R3(a[0]), R3(yr), R3(a[1]), R3(b[0]), R3(yr), R3(b[1])])
        n = max(1, int(L / self.every))
        for i in range(n):
            t = (i + 0.5) / n
            x, z = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            self.posts.append([R3(x), R3(y + self.plinth[1]), R3(z), R3(x), R3(y + self.h - self.rail[1]), R3(z)])

    def ring(self, cx, cz, r, y, n=32):
        """a ring of n straight runs round (cx, cz), r to their middle line"""
        p = [(cx + r * math.cos(2 * math.pi * k / n), cz + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
        for k in range(n): self.run(p[k], p[(k + 1) % n], y)

    def parts(self, name="balustrade"):
        if not self.rails: return {}
        return {f"{name} plinths": {"type": "bars", "lines": self.plinths, "w": self.plinth[0], "h": self.plinth[1], "kind": "moulding",
                                    "_about": "the balustrades' plinths, every run on the building (neoclassical.Balusters: the preferred L2 balustrade)"},
                f"{name} balusters": {"type": "bars", "lines": self.posts, "w": self.post, "h": self.post, "caps": False, "kind": "moulding",
                                      "_about": f"the balusters, one every {self.every} m"},
                f"{name} rails": {"type": "bars", "lines": self.rails, "w": self.rail[0], "h": self.rail[1], "kind": "moulding",
                                  "_about": "and the rails over them"}}


# ---------------------------------------------------------------------------------------------------------------------
# a block's faces: a rect enclosure's 0 +z, 1 +x, 2 -z, 3 -x; `at` along a face from its middle, as its first corner runs
FACE_OF = {"+z": 0, "+x": 1, "-z": 2, "-x": 3}
def face_at(f, u):
    """a face's `at` for a point `u` along it (x on the z faces, z on the x faces, from the block's middle)"""
    return R3(u if f in (0, 3) else -u)

# a storey's windows: (sill, width, height, arched, surround) -- None for none
WINDOWS = [(1.4, 1.7, 3.0, True, None),                                   # the ground storey: round-headed, plain in the rustication
           (0.9, 1.8, 4.2, False, {"head": "alternate", "sill": True}),   # the principal storey: pediments by turns
           (0.8, 1.5, 1.9, False, None)]                                  # the upper storey within the order: plain


def block(add, name, w, d, x, z, y=0.0, storeys=(6.0, 7.0, 5.0), bay=4.2, windows=WINDOWS, doors=(), against=None, blind=None,
          order="corinthian", T=1.2, roof=0.4, well=None, floors=True, bal=None, about=None):
    """A WING of a classical building, w (x) by d (z) centred at (x, z), standing at y.
    storeys: their heights (the first rusticated, the rest under one giant order of `order`; "" for none).
    bay: the window rhythm. windows: per storey (sill, width, height, arched, surround) or None.
    doors: [(facing, u, storey, width, height, arched)] -- u along that face from the block's middle (world axis).
    against: {facing: [(u0, u1), ...]}: where another block stands against a face -- no window, moulding or balustrade there.
    blind: {facing: [storey, ...]}: storeys of a face left without windows (a terrace stands against them).
    well: a round hole in the roof slab (radius): a rotunda rises through it.
    bal: a Balusters to add the wall heads' runs to. Returns the block's anchors."""
    against, blind = against or {}, blind or {}
    H = sum(storeys)
    levels = [y + sum(storeys[:k]) for k in range(len(storeys))]
    faces, clear = {}, {}
    for facing, f in FACE_OF.items():
        L = w if f in (0, 2) else d
        spans = sorted(against.get(facing, []))
        hit = lambda u, half: any(u + half > a - 0.4 and u - half < b + 0.4 for a, b in spans)
        nb = max(1, int(L // bay))
        us = [-L / 2 + L / nb * (i + 0.5) for i in range(nb)]
        tiers = []
        for k, sh in enumerate(storeys):
            ops = []
            for (df, du, ds, dw, dh, darch) in doors:
                if df == facing and ds == k:
                    ops.append({"at": face_at(f, du), "width": dw, "sill": 0, "springing": R3(dh - (dw / 2 if darch else 0)),
                                "head": {"profile": "semicircular" if darch else "flat"}, "surround": {"head": "cornice" if k else False}})
            win = windows[k] if k < len(windows) else None
            if win and k not in blind.get(facing, []):
                sill, ww, wh, arched, sur = win
                for u in us:
                    if hit(u, ww / 2): continue
                    if any(df == facing and abs(du - u) < (dw + ww) / 2 + 0.5 for (df, du, ds, dw, dh, _) in doors if ds in (k, k - 1)): continue
                    op = {"at": face_at(f, u), "width": ww, "sill": sill, "springing": R3(sill + wh - (ww / 2 if arched else 0)),
                          "head": {"profile": "semicircular" if arched else "flat"}}
                    if sur: op["surround"] = sur
                    ops.append(op)
            tiers.append({"h": sh, "openings": ops} if k < len(storeys) - 1 else {"openings": ops})
        faces[str(f)] = tiers
        if spans:
            clear[str(f)] = [[R3(L / 2 + min(face_at(f, a), face_at(f, b))), R3(L / 2 + max(face_at(f, a), face_at(f, b)))] for a, b in spans]
        # the balustrade on the wall head, less where another block stands
        if bal is not None:
            free, at0 = [], -L / 2
            for a, b in spans:
                if a - at0 > 0.8: free.append((at0, a))
                at0 = max(at0, b)
            if L / 2 - at0 > 0.8: free.append((at0, L / 2))
            inset = bal.plinth[0] / 2
            for a, b in free:
                if f in (0, 2):
                    zz = z + (d / 2 - inset) * (1 if f == 0 else -1)
                    bal.run((x + a, zz), (x + b, zz), y + H + roof)
                else:
                    xx = x + (w / 2 - inset) * (1 if f == 1 else -1)
                    bal.run((xx, z + a), (xx, z + b), y + H + roof)
    part = {"type": "enclosure", "plan": {"rect": [R3(w), R3(d)]}, "thickness": T, "height": R3(H), "glass": True, "faces": faces,
            "interior": True, "courses": {"clear": clear} if clear else {},
            **({"orders": [{"tier": 1, "kind": order, "span": len(storeys) - 1}]} if order and len(storeys) > 1 else {}),
            "at": [[R3(x), R3(y), R3(z), 0]]}
    if about: part["_about"] = about
    add(name, part)
    # the roof slab on the wall heads (a round well cut through it where a rotunda rises), the floors
    plan = {"rect": [R3(w), R3(d)]}
    if well: plan["well"] = {"radius": R3(well), "sides": 36}
    add(f"{name} roof", {"type": "prism", "plan": plan, "height": roof, "at": [[R3(x), R3(y + H), R3(z), 0]], "flatRoof": True,
                         **({"railing": False} if well else {})})   # (no railing round the well: what rises through it closes it)
    if floors:
        add(f"{name} floor", {"type": "box", "width": R3(w - 0.04), "length": R3(d - 0.04), "height": 0.1, "at": [[R3(x), R3(y), R3(z), 0]]})
        add(f"{name} principal floor", {"type": "box", "width": R3(w - 2 * T), "length": R3(d - 2 * T), "height": 0.4,
                                        "at": [[R3(x), R3(levels[1] - 0.4), R3(z), 0]]})
    return {"x": x, "z": z, "w": w, "d": d, "y": y, "H": H, "top": y + H + roof, "levels": levels,
            "face": {"+z": z + d / 2, "-z": z - d / 2, "+x": x + w / 2, "-x": x - w / 2}}


# ---------------------------------------------------------------------------------------------------------------------
def temple_front(add, name, x, z, facing, y0, y1, ped=8, flank=4, spacing=3.2, colR=0.48, colH=9.6, entH=2.4, depth=6.0,
                 pitch=17.5, sideCount=1, stair=None, podium=True, bal=None, order="corinthian", pedOut=0.0, cornice=(0.6, 0.5)):
    """A FRONT of columns before the wall at (x, z) facing `facing`: `ped` columns under a pediment between two colonnades of
    `flank` columns (0: a portico alone; ped 0: a colonnade alone, flat-roofed), all on one rhythm `spacing`, `depth` out
    from the wall, standing at the principal floor y1 -- on a PODIUM down to y0 (an arcade under the flanks, solid under
    the pediment) and climbed by a grand STAIR `stair` wide (None: none) between sloping cheek walls. The portico stands
    `pedOut` further out than the colonnades (its podium with it), its pediment framed by a horizontal and two raking
    cornices (`cornice`: their projection and height, as bars; None: none).
    Returns the anchors (the floor's outer edge, the stair's foot, the top)."""
    W = frame(x, z, facing)
    t = YAW[facing]
    N = ped + 2 * flank
    top = y1 + colH + entH
    Wall = (N - 1) * spacing + 4 * colR + 1.0
    Wp = (ped - 1) * spacing + 4 * colR + 1.0 if ped else 0     # (the portico's width, as components/portico's W)
    dp = depth + (pedOut if ped else 0)
    # the podium first (what is raised on it is listed after it): a front wall arcaded between the columns' feet, its
    # two ends, the floor on it
    if podium and y1 - y0 > 0.5:
        ph = y1 - y0
        cx, cz = W(0, depth)
        arches = []
        for k in range(N - 1):
            u = (k - (N - 2) / 2) * spacing
            if ped and stair and abs(u) < stair / 2 + spacing * 0.5: continue
            if ped and pedOut and abs(u) < Wp / 2 + spacing * 0.3: continue      # (behind the portico's own podium)
            arches.append({"at": R3(u + Wall / 2),   # (a plain wall's openings from its left end)
                            "width": R3(spacing * 0.55), "sill": 0,
                           "springing": R3(min(ph - 1.2, ph * 0.62)), "head": {"profile": "semicircular"}})
        add(f"{name} podium", {"type": "wall", "width": R3(Wall), "height": R3(ph), "thickness": 1.0, "openings": arches, "glass": False,
                               "at": [[cx, R3(y0), cz, R3(t)]], "_about": "the podium: the ground storey's arcade under the colonnades"})
        for i, s in enumerate((-1, 1)):
            ex, ez = W(s * Wall / 2, depth / 2)
            add(f"{name} podium end {i + 1}", {"type": "box", "width": R3(1.0 if facing in ("+z", "-z") else depth), "length": R3(depth if facing in ("+z", "-z") else 1.0),
                                               "height": R3(ph), "at": [[R3(ex - s * 0.5 * math.cos(t)), R3(y0), R3(ez + s * 0.5 * math.sin(t)), 0]]})
        fx, fz = W(0, depth / 2)
        wid, ln = (Wall, depth) if facing in ("+z", "-z") else (depth, Wall)
        add(f"{name} floor", {"type": "box", "width": R3(wid), "length": R3(ln), "height": 0.4, "walked": True,
                              "at": [[fx, R3(y1 - 0.4), fz, 0]], "_about": "the colonnade's floor on the podium"})
        if ped and pedOut:
            fx, fz = W(0, depth + pedOut / 2)
            wid, ln = (Wp, pedOut) if facing in ("+z", "-z") else (pedOut, Wp)
            add(f"{name} portico podium", {"type": "box", "width": R3(wid), "length": R3(ln), "height": R3(ph), "walked": True,
                                           "at": [[fx, R3(y0), fz, 0]], "_about": "the portico's podium, standing out before the arcade"})
    # the pedimented portico (components/portico: its columns at depth - colR * 1.8)
    if ped:
        px, pz = W(0, 0)
        add(f"{name} portico", {"type": "component", "use": "components/portico",
                                "params": {"count": ped, "spacing": spacing, "colR": colR, "colH": colH, "entH": entH, "depth": R3(dp),
                                           "pitch": pitch, "steps": 0, "sideCount": sideCount, "order": order},
                                "build": ["columns", "side columns", "pediment"] if sideCount else ["columns", "pediment"],
                                "at": [[px, R3(y1), pz, R3(t)]], "_about": f"the portico: {ped} columns under the pediment"})
        if cornice:
            cw, ch = cornice
            v = dp + 0.4 + 0.1                                   # (the gable's face: the roof's 0.4 overhang; the bars stand forward of it)
            yb, ya = top + ch / 2, top + Wp / 2 * math.tan(math.radians(pitch)) + ch * 0.3
            ends = [W(-Wp / 2 - 0.3, v), W(0, v), W(Wp / 2 + 0.3, v)]
            L = lambda a, ay, b, by: [a[0], R3(ay), a[1], b[0], R3(by), b[1]]
            add(f"{name} pediment cornice", {"type": "bars", "lines": [L(ends[0], yb, ends[2], yb), L(ends[0], yb, ends[1], ya), L(ends[1], ya, ends[2], yb)],
                                             "w": cw, "h": ch, "kind": "moulding",
                                             "_about": "the pediment's frame: its horizontal cornice and the two raking ones over the tympanum"})
    # the colonnades either side, under a flat roof with its balustrade
    if flank:
        uf = spacing * (ped + flank) / 2 if ped else 0
        sides = (-1, 1) if ped else (0,)
        at = [[*[W(s * uf, 0)[0]], R3(y1), W(s * uf, 0)[1], R3(t)] for s in sides]
        add(f"{name} colonnade", {"type": "component", "use": "components/portico",
                                  "params": {"count": flank, "spacing": spacing, "colR": colR, "colH": colH, "entH": entH, "depth": depth,
                                             "steps": 0, "sideCount": 0, "order": order},
                                  "build": ["columns"], "at": at, "_about": f"the colonnades: {flank} columns, flat-roofed"})
        fw = (flank - 1) * spacing + 4 * colR + 1.0
        for i, s in enumerate(sides):
            cx, cz = W(s * uf, depth / 2)
            wid, ln = (fw, depth) if facing in ("+z", "-z") else (depth, fw)
            add(f"{name} colonnade roof {i + 1}", {"type": "box", "width": R3(wid), "length": R3(ln), "height": 0.5,
                                                    "at": [[cx, R3(top), cz, 0]], "flatRoof": True})
            if bal is not None:
                a, b = W(s * uf - fw / 2, depth - 0.3), W(s * uf + fw / 2, depth - 0.3)
                bal.run(a, b, top + 0.5)
                for e in ((s * uf + s * fw / 2 - s * 0.3,) if ped else (-fw / 2 + 0.3, fw / 2 - 0.3)):   # (the free ends, back to the wall)
                    bal.run(W(e, depth - 0.3), W(e, 0.2), top + 0.5)
    out = {"top": top, "W": Wall, "depth": depth}
    if stair and y1 - y0 > 0.5:
        out["foot"] = grand_stair(add, f"{name} stair", x, z, facing, y0, y1, stair, out=dp)
    return out


# ---------------------------------------------------------------------------------------------------------------------
def grand_stair(add, name, x, z, facing, y0, y1, width, out=0.0, run=0.4, cheek=1.4):
    """A GRAND STAIR up to a front facing `facing` at (x, z): it arrives at y1 `out` before the wall (a portico's floor's
    edge, a terrace's rim) from the ground y0, straight on, between two cheek walls whose tops fall with it a metre over
    the nosings. Returns the foot's middle (x, z)."""
    W = frame(x, z, facing)
    t = YAW[facing]
    n = max(2, round((y1 - y0) / 0.17)); L = n * run
    sx, sz = W(width / 2, out + L)
    add(name, {"type": "flight", "width": R3(width), "run": run, "rise": R3((y1 - y0) / n), "base": R3(y0), "top": R3(y1),
               "landing": 0, "railing": False, "at": [[sx, 0, sz, R3(t + math.pi / 2)]], "_about": f"a grand stair: {n} steps up"})
    if cheek:
        k = (y1 - y0) / L
        dv = (math.sin(t), math.cos(t))
        for i, s in enumerate((-1, 1)):
            u0 = s * (width / 2 + cheek / 2)
            pts = [W(u0 - cheek / 2, out), W(u0 + cheek / 2, out), W(u0 + cheek / 2, out + L), W(u0 - cheek / 2, out + L)]
            ox, oz = W(u0, out)
            add(f"{name} cheek {i + 1}", {"type": "prism", "plan": {"points": [[R3(px - ox), R3(pz - oz)] for px, pz in pts]},
                                          "height": R3(y1 - y0 + 1.0), "slope": [R3(-k * dv[0]), R3(-k * dv[1])], "at": [[ox, R3(y0), oz, 0]]})
    return W(0, out + L)


# ---------------------------------------------------------------------------------------------------------------------
def seg_height(a, rise, r):
    """a segmental dome's height over its springing where it has narrowed to radius r"""
    rho = (a * a + rise * rise) / (2 * rise)
    return math.sqrt(max(0.0, rho * rho - r * r)) - (rho - rise)


def dome_height(a, r, rise=None, spread=None):
    """a dome's height over its springing where it has narrowed to radius r: pointed (spread: each side's arc centred
    spread * a beyond the axis -- its crown a * sqrt(1 + 2 spread)) or segmental (rise; none: a hemisphere)"""
    if spread is not None:
        return math.sqrt(max(0.0, (a * (1 + spread)) ** 2 - (r + spread * a) ** 2))
    return seg_height(a, rise or a, r)


# components/tholos's proportions (of R and H): write_tholos() writes them, tholos_heights() reads them -- one table
THOLOS = {"plinthR": 1.25, "plinthH": 0.15, "colH": 0.52, "entH": 0.11, "capRise": 0.22, "crownR": 0.3, "crownH": 0.15, "globeR": 0.18, "collarH": 0.3}


def dome_radius(a, y, rise=None, spread=None):
    """the inverse of dome_height: the dome's radius at the height y over its springing"""
    if spread is not None:
        return math.sqrt(max(0.0, (a * (1 + spread)) ** 2 - y * y)) - spread * a
    rise = rise or a
    rho = (a * a + rise * rise) / (2 * rise)
    return math.sqrt(max(0.0, rho * rho - (y + rho - rise) ** 2))


def dome_windows(add, name, x, z, spring, domeR, n, rows, rise=None, spread=None, t=0.12, frame=0.3):
    """WINDOWS IN A DOME'S SHELL, n round in each row between the ribs (the bays' middles): rows [(f, w, h)] -- f the
    window's middle as a share of the dome's crown height, w its width, h its length up the shell. Each a dark light
    lying on the shell (a `bars` plate down the meridian, t thick, just proud of the shell) in a frame `frame`
    wider all round. Two parts a row: `<name> <k>` the lights, `<name> frames <k>` their frames."""
    crown = dome_height(domeR, 0, rise, spread)
    for k, (f, ww, wh) in enumerate(rows):
        ym = crown * f
        r0, r1 = dome_radius(domeR, ym - 0.5, rise, spread), dome_radius(domeR, ym + 0.5, rise, spread)
        c, sn = (r0 - r1), 1.0                                   # (the meridian's direction at the middle: out c, up 1)
        L = math.hypot(c, sn); dr, dy = -c / L, sn / L           # (up the shell)
        nr, ny = dy, -dr                                         # (out of it)
        rm = dome_radius(domeR, ym, rise, spread)
        for part, ext, off in ((f"{name} frames {k + 1}", frame, 0.0), (f"{name} {k + 1}", 0.0, t * 0.6)):   # (the frame half sunk in the shell -- a polygon, its faces' middles inside the circle -- the light just proud of it)
            half = wh / 2 + ext
            lines = []
            for i in range(n):
                ph = 2 * math.pi * (i + 0.5) / n
                cs, sn_ = math.cos(ph), math.sin(ph)
                pt = lambda s_: (rm + dr * s_ + nr * off, spring + ym + dy * s_ + ny * off)
                (ra, ya), (rb, yb) = pt(-half), pt(half)
                lines.append([R3(x + ra * cs), R3(ya), R3(z + ra * sn_), R3(x + rb * cs), R3(yb), R3(z + rb * sn_)])
            add(part, {"type": "bars", "lines": lines, "w": R3(ww + 2 * ext), "h": t, "kind": "moulding",
                       **({"_about": "the dome's windows: dark lights lying on the shell between its ribs, each in its frame"} if k == 0 and not ext else {})})


def dome_on_drum(add, name, x, z, y, R, dt=1.8, skirt=None, H=11.4, colH=9.0, n=36, colR=0.45, pw=3.4, win=(1.6, 1.0, 6.0),
                 atticH=11.0, atticWin=(1.4, 3.6, 4.0), atticHead="semicircular", domeR=None, plinth=1.5, rise=None, spread=None, ribW=0.45,
                 lanternR=3.8, lanternH=11.6, tholosN=12, globe=False, globeR=None, windows=(), bal=None):
    """A DOME ON A DRUM WITH A PERISTYLE, as the Capitol's and its many children: over the roofs at y a SKIRT (r_outer,
    height) round the rotunda R; on it `drum-dome` -- the drum (dt thick, H high, n bays, a window `win` (width, sill,
    height) in each), its peristyle of n columns pw out, the attic (atticH, windows (width, sill, height)), the dome plinth
    and the ribbed dome (domeR; segmental to `rise`, or pointed by `spread`: the Capitol's, taller than a half sphere), the `tholos` lantern of tholosN columns. Balustrade rings round the
    skirt's rim, the peristyle's deck and the lantern's foot. The SKIRT in two stages: a broader base ring under a cornice,
    the ring the peristyle stands on set back over it, a band under its rim. `windows`: rows in the dome's shell
    (dome_windows). `globe`: a globe on the tholos's crown (a statue's foot), `globeR` m (default THOLOS's share of
    lanternR). Returns the heights (top: where the
    lantern -- or its globe -- ends, a statue's foot)."""
    domeR = domeR or R + dt
    rise = rise or domeR
    head = {"profile": "pointed", "spread": spread} if spread is not None else {"profile": "segmental", "rise": R3(rise)}
    yd = y
    if skirt:
        so, sh = skirt
        hb = sh * 0.45
        ring = lambda nm, ro, h, y_, **kw: add(f"{name} {nm}", {"type": "ring", "count": n, "rOuter": R3(ro), "rInner": R3(R), "height": R3(h), "y": R3(y_),
                                                                 "turn": 0.5, "solid": True, "place": [[R3(x), 0, R3(z), 0]], **kw})
        ring("skirt base", so + 1.6, hb, y, _about="the skirt's base over the roofs, broader, under its cornice")
        ring("skirt base cornice", so + 2.0, 0.5, y + hb - 0.3, flatRoof=True)
        ring("skirt", so, sh - hb - 0.2, y + hb + 0.2, flatRoof=True, walked=True,
             _about="the skirt the peristyle stands on, set back on its base: walked round between the columns and its balustrade")
        ring("skirt band", so + 0.35, 0.6, y + sh - 0.95)
        yd = y + sh
        if bal is not None: bal.ring(x, z, so - bal.plinth[0] / 2, yd, n)
    winW, winSill, winH = win
    aW, aSill, aH = atticWin
    add(name, {"type": "component", "use": "components/drum-dome",
               "params": {"R": R, "dt": dt, "H": H, "n": n, "every": 1, "winW": winW, "winSill": winSill, "winH": winH,
                          **head, "domeT": 0.6, "colN": n, "colR": colR, "colH": colH, "pw": pw,
                          "attic": "yes", "atticH": atticH, "atticWin": aW, "atticSill": aSill, "atticWinH": aH, "atticHead": atticHead,
                          "domeR": R3(domeR), "domePlinth": plinth, "plinth": "yes" if plinth else "no", "ribsN": n, "ribW": ribW, "lanternR": lanternR, "lanternH": lanternH,
                          "tholosN": tholosN, "tholosGlobe": "yes" if globe else "no", **({"tholosGlobeR": R3(globeR)} if globeR else {})},
               "build": ["drum", "peristyle", "peristyle deck", "attic", "dome plinth", "dome", "ribs", "tholos", "interior", "attic interior"],
               "at": [[R3(x), R3(yd), R3(z), 0]],
               "_about": "the drum and its peristyle, the attic, the plinth, the ribbed dome and the tholos (drum-dome)"})
    deck = yd + H
    if bal is not None:
        bal.ring(x, z, R + dt + pw + colR * 0.6, deck, n)          # (on the peristyle's entablature, round the attic's foot)
    spring = deck + atticH + plinth
    pr = lanternR * THOLOS["plinthR"]
    tb = spring + dome_height(domeR, pr, rise, spread) - lanternR * 0.1  # (drum-dome's tholos: on the dome where it narrows to its plinth)
    th = tholos_heights(lanternR, lanternH, globe, globeR)
    if windows: dome_windows(add, f"{name} windows", x, z, spring, domeR, n, windows, rise=rise if spread is None else None, spread=spread)
    if bal is not None: bal.ring(x, z, pr - bal.plinth[0] / 2 - 0.05, tb + th["plinth"], 24)
    return {"skirtTop": yd, "deck": deck, "spring": spring, "crown": spring + dome_height(domeR, 0, rise, spread), "tholos": tb, "top": tb + th["top"]}


GLOBE_SINK = 0.165   # (the sphere sits down into its collar until it is the collar's width, 0.55 of its radius: 1 - sqrt(1 - 0.55^2))


def tholos_heights(R, H, globe=False, globeR=None):
    """the tholos's heights over its foot, as components/tholos sets them (from THOLOS: check_tholos() holds the file to it);
    with a globe, its top: the collar, the sphere sunk GLOBE_SINK into it"""
    k = THOLOS
    p, c, e = H * k["plinthH"], H * k["colH"], H * k["entH"]
    cap = seg_height(R * 1.08, H * k["capRise"], R * k["crownR"])
    top = p + c + e + cap - 0.1 + H * k["crownH"]
    g = globeR or R * k["globeR"]
    return {"plinth": p, "cap": p + c + e, "crown": top, "top": top + (g * (k["collarH"] + 2 - GLOBE_SINK) if globe else 0)}


def write_tholos():
    """components/tholos: a ROUND TEMPLE -- a plinth, a windowed core, n columns round it under their entablature, the deck,
    a shallow cap and a crown on it (a statue's or a cross's foot). R to the columns' line, H to the cap's crown."""
    k = THOLOS
    doc = {"name": "Tholos",
           "_about": "A THOLOS, the round temple a dome's lantern often is: a plinth, a windowed core, a ring of `n` columns round it under their entablature, the deck over them, a shallow cap and a crown on it for a statue or a cross to stand on -- the Capitol's, St Peter's, the Pantheon in Paris. R is the columns' line, H the height to the cap's crown; drum-dome builds it by name (`tholos`) on its dome. GENERATED by tools/archgen/neoclassical.py write_tholos() from its THOLOS table, which tholos_heights() reads to stand a statue on top: change the table there, not this file.",
           "params": {"detail": 4, "R": 3.0, "H": 10.0, "n": 12, "order": "corinthian",
                      "plinthR": f"R * {k['plinthR']}", "plinthH": f"H * {k['plinthH']}", "colR": "R * 0.08", "colH": f"H * {k['colH']}",
                      "entH": f"H * {k['entH']}", "coreR": "R * 0.66", "coreT": "R * 0.1", "capR": "R * 1.08", "capRise": f"H * {k['capRise']}",
                      "crownR": f"R * {k['crownR']}", "crownH": f"H * {k['crownH']}", "winW": "coreR * 0.3", "globe": "no", "globeR": f"R * {k['globeR']}", "collarH": f"globeR * {k['collarH']}",
                      "_globe": "globe: yes -- a GLOBE on the crown (globeR: on a collar collarH high, a whole sphere sunk into it, a band round its equator), a statue standing on its top: the Capitol's Freedom on her cast-iron globe with its motto band",
                      "_R": "R: the columns' line; H: from its foot to the cap's crown; n: its columns, and a narrow window in the core between each two",
                      "_crownR": "the crown on the cap (crownR, crownH): a drum where a statue or a cross stands, its top crownH over the cap where the cap has narrowed to it"},
           "build": ["plinth", "core", "colonnade", "deck", "cap", "crown", "globe collar", "globe", "globe band"],
           "parts": {
               "plinth": {"type": "prism", "plan": {"sides": "n * 2", "radius": "plinthR"}, "height": "plinthH", "at": [[0, 0, 0, 0]], "walked": True,
                          "_about": "the plinth it stands on, wider than the colonnade: walked round"},
               "core": {"type": "ring", "count": "n", "rOuter": "coreR", "rInner": "coreR - coreT", "height": "colH + entH", "y": "plinthH", "turn": 0.5,
                        "every": 1, "only": 1, "opening": {"width": "winW", "sill": "colH * 0.22", "springing": "colH * 0.8", "head": {"profile": "semicircular"}},
                        "place": [[0, 0, 0, 0]], "_about": "the core, a narrow window between each two columns"},
               "colonnade": {"type": "colonnade", "plan": "round", "count": "n", "radius": "R", "order": "order", "columnR": "colR", "height": "colH",
                             "taper": 0.86, "entablature": {"h": "entH", "depth": "colR * 2.6"}, "at": [[0, "plinthH", 0, 0]], "_about": "the ring of columns"},
               "deck": {"type": "ring", "count": "n", "rOuter": "R", "rInner": "coreR - coreT", "height": "entH", "y": "plinthH + colH", "turn": 0.5,
                        "solid": True, "place": [[0, 0, 0, 0]], "standsOn": ["core"], "_about": "the deck from the core out to the columns' line"},
               "cap": {"type": "dome", "sides": "n * 2", "radius": "capR", "thickness": 0.3, "head": {"profile": "segmental", "rise": "capRise"},
                       "at": [[0, "plinthH + colH + entH", 0, 0]], "standsOn": ["deck"], "_about": "the shallow cap over the colonnade"},
               "crown": {"type": "prism", "plan": {"sides": 16, "radius": "crownR"}, "height": "crownH", "at": [[0, -0.1, 0, 0]], "atop": "cap", "atopR": "crownR",
                         "standsOn": ["cap"], "_about": "the crown on the cap, where a statue or a cross stands"},
               "globe collar": {"type": "prism", "plan": {"sides": 16, "radius": "globeR * 0.55"}, "height": "collarH", "at": [[0, 0, 0, 0]], "atop": "crown",
                                "standsOn": ["crown"], "when": {"globe": "yes"}, "_about": "(globe: yes) the globe's collar on the crown..."},
               "globe": {"type": "loft", "axis": "y", "sides": 20, "smooth": 2, "at": [[0, "0 - globeR * 0.165", 0, 0]], "atop": "globe collar", "standsOn": ["globe collar"],
                         "when": {"globe": "yes"}, "sections": [{"s": "globeR * 0", "u": 0, "v": 0, "a": "globeR * 0.0", "b": "globeR * 0.0", "n": 2}, {"s": "globeR * 0.06", "u": 0, "v": 0, "a": "globeR * 0.3412", "b": "globeR * 0.3412", "n": 2}, {"s": "globeR * 0.2", "u": 0, "v": 0, "a": "globeR * 0.6", "b": "globeR * 0.6", "n": 2}, {"s": "globeR * 0.4", "u": 0, "v": 0, "a": "globeR * 0.8", "b": "globeR * 0.8", "n": 2}, {"s": "globeR * 0.64", "u": 0, "v": 0, "a": "globeR * 0.933", "b": "globeR * 0.933", "n": 2}, {"s": "globeR * 1.0", "u": 0, "v": 0, "a": "globeR * 1.0", "b": "globeR * 1.0", "n": 2}, {"s": "globeR * 1.36", "u": 0, "v": 0, "a": "globeR * 0.933", "b": "globeR * 0.933", "n": 2}, {"s": "globeR * 1.6", "u": 0, "v": 0, "a": "globeR * 0.8", "b": "globeR * 0.8", "n": 2}, {"s": "globeR * 1.8", "u": 0, "v": 0, "a": "globeR * 0.6", "b": "globeR * 0.6", "n": 2}, {"s": "globeR * 1.94", "u": 0, "v": 0, "a": "globeR * 0.3412", "b": "globeR * 0.3412", "n": 2}, {"s": "globeR * 2", "u": 0, "v": 0, "a": "globeR * 0.0", "b": "globeR * 0.0", "n": 2}], "_about": "...the globe on it, a whole sphere sunk into the collar to the collar's width"},
               "globe band": {"type": "prism", "plan": {"sides": 20, "radius": "globeR * 1.07"}, "height": "globeR * 0.24", "at": [[0, "globeR * 0.715", 0, 0]], "atop": "globe collar",
                              "standsOn": ["globe"], "when": {"globe": "yes"}, "_about": "...and the band round its equator (the Capitol's: E PLURIBUS UNUM)"}}}
    p = os.path.join(ROOT, "assets/architecture/components/tholos.json")
    open(p, "w").write(json.dumps(doc, indent=2) + "\n")
    return p


def check_tholos():
    """components/tholos as THOLOS says (a hand edit there would leave a statue placed by tholos_heights in the air)"""
    got = json.load(open(os.path.join(ROOT, "assets/architecture/components/tholos.json")))["params"]
    for k, v in THOLOS.items():
        assert got.get(k, "").endswith(f"* {v}"), f"components/tholos {k} = {got.get(k)} is not THOLOS's {v}: run neoclassical.py"


if __name__ == "__main__":
    print(write_tholos())
