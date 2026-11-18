"""THE GENERATORS' COMMON KIT: what every tools/archgen script used to write out for itself.

A generator builds one definition (assets/architecture/*.json): a dict of named parts and the order they are built
in. `Doc` holds the two and refuses a name given twice (two parts silently merged were a bug more than once); its
helpers make the parts every building has -- a component placed, a run of floor slabs, an opening. The geometry
helpers are the arithmetic the scripts kept copying: cutting a rectangle round holes (`tiles`), cutting long pieces
short (`split`), which `side` of a range faces away from a court (`side_away`), the muqarnas cells under an iwan's
hood. Numbers are rounded to 0.1 mm (`r4`) as they are written, so a definition reads cleanly and diffs quietly.

    from kit import Doc, r4, Q, op, door, POINTED
    D = Doc()
    D.add("hall", {...}, about="...")
    D.write("assets/architecture/x.json", name="X", about="...")
"""
import os, json, math

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
Q = math.pi / 2
r4 = lambda v: round(v, 4)

# ---- arch heads --------------------------------------------------------------------------------------------------
POINTED = {"profile": "pointed", "spread": .5}         # the Persian / Ottoman four-centred proportion
FLAT = {"profile": "flat"}
ROUND = {"profile": "semicircular"}
def horseshoe(over=.3): return {"profile": "horseshoe", "over": over}
def lobed(lobes=5, over=0.0, **kw): return {"profile": "lobed", "lobes": lobes, "over": over, **kw}


def op(at, w, sill, spr, head=POINTED, glass=None, **kw):
    """an opening along a face: centred `at`, `w` wide, from `sill` to its `spr`inging, under `head`"""
    d = {"at": r4(at), "width": r4(w), "sill": r4(sill), "springing": r4(spr), "head": head, **kw}
    if glass is not None: d["glass"] = glass
    return d


def door(at=0, w=1.6, h=2.6, head=POINTED):
    return op(at, w, 0, h, head, glass=False)


def comp(use, params, at, **kw):
    """a `component` part: the definition `use` (a path under assets/architecture) placed at each of `at`"""
    return {"type": "component", "use": use, "params": params, "at": at, **kw}


def at(x, y, z, yaw=0.0):
    return [r4(x), r4(y), r4(z), r4(yaw)]


def wall_at(x, y, z, yaw, t):
    """the placement of a `wall` t thick CENTRED on the line through (x, z): a wall stands behind its face -- its local
    z runs from -t to 0 (build.js straightAt) -- unlike a box or an arch, which straddle theirs"""
    return at(x + t / 2 * math.sin(yaw), y, z + t / 2 * math.cos(yaw), yaw)


class Doc:
    """one definition being built: its parts by name, and the order they are built in"""

    def __init__(self):
        self.parts, self.build = {}, []

    def add(self, name, d, about=None):
        if name in self.parts: raise KeyError(f"part {name!r} given twice")
        if about: d = {**d, "_about": about}
        self.parts[name] = d
        self.build.append(name)
        return name

    def comp(self, name, use, params, places, about=None, **kw):
        return self.add(name, comp(use, params, places, **kw), about)

    def first(self, names):
        """build these before everything else (a platform, the ground: what the rest stands on)"""
        for n in names: self.build.remove(n)
        self.build[:0] = list(names)

    def slabs(self, name, rects, y, h=.3, about=None, place=None, **kw):
        """floor (or roof) slabs over rectangles (x0, z0, x1, z1), one instanced box part per size; `place(x, y, z)` the
        placement of a slab's middle when the rectangles are in a frame of their own (a building turned off the axes)"""
        place = place or at
        groups = {}
        for a, b, c, e in rects:
            groups.setdefault((r4(c - a), r4(e - b)), []).append(place((a + c) / 2, y, (b + e) / 2))
        out = []
        for k, ((w, l), places) in enumerate(sorted(groups.items())):
            out.append(self.add(name if k == 0 else f"{name} {k + 1}", {"type": "box", "width": w, "length": l, "height": h, "at": places, **kw},
                                about if k == 0 else None))
        return out

    def write(self, rel, name, about, params=None, **extra):
        doc = {"name": name, "_about": about, "params": params or {"detail": 4}, **extra, "build": self.build, "parts": self.parts}
        write_json(rel, doc)
        print(f"{rel}: {len(self.parts)} parts")
        return doc


def write_json(rel, obj):
    with open(os.path.join(ROOT, rel), "w") as f:
        json.dump(obj, f, indent=1)
        f.write("\n")


# ---- rectangles --------------------------------------------------------------------------------------------------
def tiles(x0, z0, x1, z1, holes):
    """the rectangle (x0, z0, x1, z1) less the rectangular holes, as rectangles: cut on every hole's edges, the free
    cells of each row run together"""
    xs = sorted({x0, x1, *[c for h in holes for c in (h[0], h[2]) if x0 < c < x1]})
    zs = sorted({z0, z1, *[c for h in holes for c in (h[1], h[3]) if z0 < c < z1]})
    out = []
    for j in range(len(zs) - 1):
        run = None
        for i in range(len(xs) - 1):
            mx, mz = (xs[i] + xs[i + 1]) / 2, (zs[j] + zs[j + 1]) / 2
            free = not any(h[0] < mx < h[2] and h[1] < mz < h[3] for h in holes)
            if free and run is None: run = xs[i]
            if (not free or i == len(xs) - 2) and run is not None:
                out.append((run, zs[j], xs[i + 1] if free else xs[i], zs[j + 1])); run = None
    return out


def split(rects, m=16.0):
    """cut every rectangle into pieces no longer than m (no one triangle of a floor vast)"""
    out = []
    for a, b, c, d in rects:
        nx, nz = max(1, math.ceil((c - a) / m - 1e-6)), max(1, math.ceil((d - b) / m - 1e-6))
        for i in range(nx):
            for j in range(nz):
                out.append((a + (c - a) * i / nx, b + (d - b) * j / nz, a + (c - a) * (i + 1) / nx, b + (d - b) * (j + 1) / nz))
    return out


def side_away(path, c):
    """the `side` of a range whose OUT looks away from the point c (range.js: the right of a segment is (-e.z, e.x))"""
    (x0, z0), (x1, z1) = path[0], path[1]
    ex, ez = x1 - x0, z1 - z0
    return "right" if (-ez) * (c[0] - (x0 + x1) / 2) + ex * (c[1] - (z0 + z1) / 2) < 0 else "left"


# ---- profiles' arithmetic (as profiles.js strikes them) ----------------------------------------------------------
def onion_h(a, bulge, neck):
    """how tall an onion of half-width a stands over its springing"""
    R1, R2 = a * bulge, a * neck
    return math.sqrt(R1 * R1 - a * a) + math.sqrt(R1 * R1 + 2 * R1 * R2)


def pointed_h(a, spread):
    return a * math.sqrt(1 + 2 * spread)


def horseshoe_h(a, over):
    """the crown of a horseshoe of half-width a over its springing: its centre `over` half-widths up, through the springing"""
    return a * over + math.hypot(a, a * over)


# ---- muqarnas ----------------------------------------------------------------------------------------------------
def muqarnas(X, Z, yaw, w, s, it, tiers=None, rise=1.35):
    """the stalactite hood of an iwan: tiers of little cells hung under its half dome, each a block turned to the
    middle, drawing in and climbing as the vault does -- ending in the small crown. (X, Z, yaw): the `portal`'s
    placement; w s it its opening's width, springing and inset. Returns the cells' placements."""
    tiers = tiers or ((7, 9, 11, 13, 15, 17) if w >= 9 else (5, 7, 9, 11, 13))
    r = w / 2 + .05; zc = w / 2 + it; out = []; n = len(tiers); c, sn = math.cos(yaw), math.sin(yaw)
    for k, m in enumerate(tiers[::-1]):
        f = (k + .35) / (n + .4); phi = f * math.pi / 2 * .94
        rr, y = r * math.cos(phi), s + r * rise * math.sin(phi)
        for j in range(m):
            th = -math.pi / 2 * .96 + math.pi * .96 * (j + (.5 if k % 2 else .0) + (0 if k % 2 else .5)) / m
            lx, lz = (rr - .2) * math.sin(th), zc - (rr - .2) * math.cos(th)
            out.append([r4(X + c * lx + sn * lz), r4(y), r4(Z - sn * lx + c * lz), r4(yaw + th)])
    return out


def muqarnas_dome(rings=(28, 24, 20, 16, 12, 8), top=.86):
    """the cells of a MUQARNAS DOME (the Nasrid qubba's: the Two Sisters', the Abencerrajes') in a unit hemisphere --
    radius 1, springing at 0: ring k of `rings` cells at elevation k/len * `top` of a quarter turn, every other ring
    turned half a cell, each cell facing the middle. Returns (x, y, z, yaw) in units of the radius: a component scales
    them by its own (as expressions), so one list serves every size."""
    out, n = [], len(rings)
    for k, m in enumerate(rings):
        phi = (k + .5) / n * top * math.pi / 2
        rr, y = math.cos(phi), math.sin(phi)
        for j in range(m):
            th = 2 * math.pi * (j + (.5 if k % 2 else 0)) / m
            out.append((rr * math.sin(th), y, rr * math.cos(th), th))
    return out


def muqarnas_box(w, places, about="the stalactite cells under its half dome"):
    """the part the cells of a hood `w` wide are drawn as"""
    return {"type": "box", "width": r4(w * .1), "length": r4(w * .06), "height": r4(w * .085), "at": places, "_about": about}


# ---- planting ----------------------------------------------------------------------------------------------------
# KINDS of tree a court is planted with, as parts: (trunk radius, trunk height to the crown, crown radius). Each kind is
# a pair of instanced parts -- trunks and crowns -- so a court of two hundred trees costs four draws.
TREES = {"palm": (.28, 8.0, 2.7), "orange": (.12, 1.4, 1.5), "cypress": (.18, 1.2, .85)}


def plant(D, kind, pts, name=None, about=None):
    """trees of one `kind` at the points (x, y, z), each turned its own way (the golden angle: no two alike). The parts
    are "<name> trunks" and "<name> crowns" ("fronds" on a palm, "foliage" and "spires" on a cypress), `name` the kind's
    own by default: what a finish's rules name them by"""
    name = name or kind
    turn = lambda k: r4((k * 2.39996) % (2 * math.pi))
    at_ = lambda dy=0.0: [[r4(x), r4(y + dy), r4(z), turn(k)] for k, (x, y, z) in enumerate(pts)]
    tr, th, cr = TREES[kind]
    if kind == "palm":
        D.add(f"{name} trunks", {"type": "column", "radius": tr, "height": th + .4, "sides": 6, "taper": .8, "at": at_()}, about or "date palms' trunks")
        D.add(f"{name} fronds", {"type": "loft", "axis": "y", "sides": 16, "at": at_(th),
                                 "sections": [{"s": -.9, "a": .25, "b": .25, "n": .6}, {"s": .3, "a": r4(cr * .7), "b": r4(cr * .7), "n": .55},
                                              {"s": .8, "a": cr, "b": cr, "n": .45}, {"s": 1.2, "a": r4(cr * .6), "b": r4(cr * .6), "n": .5}, {"s": 1.5, "a": .2, "b": .2}]},
              "their crowns of fronds, arching out and down")
    elif kind == "orange":
        D.add(f"{name} trunks", {"type": "column", "radius": tr, "height": th + .3, "sides": 6, "taper": .75, "at": at_()}, about or "orange trees' trunks")
        D.add(f"{name} crowns", {"type": "dome", "sides": 16, "radius": cr, "thickness": 0, "head": {"profile": "bell", "waist": .98, "lift": .5}, "at": at_(th)},
              "their round dark crowns")
    elif kind == "cypress":
        D.add(f"{name} trunks", {"type": "column", "radius": tr, "height": th, "sides": 6, "taper": .8, "at": at_()}, about or "cypresses' trunks")
        D.add(f"{name} foliage", {"type": "column", "radius": cr, "height": 3.0, "sides": 14, "taper": 1.25, "at": at_(th - .2)}, "a dark flame, swelling from its foot ...")
        D.add(f"{name} spires", {"type": "column", "radius": r4(cr * 1.25), "height": 7.5, "sides": 14, "taper": .06, "at": at_(th + 2.8)}, "... drawn up to its tip")
    else:
        raise KeyError(kind)


def hedges(D, name, rects, y, h=1.1, about=None):
    """clipped hedges (myrtle, box) along rectangles (x0, z0, x1, z1): the Court of the Myrtles' two beds"""
    return D.slabs(name, rects, y, h=h, about=about)
