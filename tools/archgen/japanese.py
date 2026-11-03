# THE JAPANESE TEMPLE'S PIECES, shared by the generators that build Japanese halls (kinkakuji.py, byodo_in.py):
#   phoenix_component()  writes components/phoenix: the gilt bronze phoenix (hoo) on a ridge or a finial, as bars
#   hoju_component()     writes components/hoju: the jewel on a pyramid roof's apex -- a round base, a waist, the bulb to a point
#   rail(), rail_path()  a railing (koran) round a rectangle or along a line: top rail, mid rail, posts -- `bars`
#   offset_line()        a polyline moved sideways, mitred at its folds (a balcony's edge along a folding corridor)
#   deck()               a veranda or balcony floor round a rectangle, the wall's footprint left out
#   corridor_wing()      a covered corridor of two storeys along a folding line (a Phoenix Hall's yokuro): the ground
#                        storey open between its posts, the upper storey low under a gabled roof, a railed balcony round it
# Each takes the generator's own `add(name, part)`, so the parts land in the building that calls it. Numbers are metres.
import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
r4 = lambda v: round(v, 4)


def phoenix_component():
    """components/phoenix: the bird as straight bars -- body, breast, neck, crest, two legs, the raised wing either side,
    the fan of the tail -- standing on a square base, facing +z. Params: `s` the bird's size (1: about a metre to the
    crest), `bw` `bh` the base's width and height, `pedestal` "square" (the default), "disc" (a round one bw across: the
    Phoenix Hall's) or "none" with bh 0 (the bird on whatever it is set on) -- not `base`, which a caller cannot pass, the
    engine keeping that word for a building's own base -- `tail_rise` how far (x s) the tail's feathers sweep UP behind (0: the
    low fan of Kinkaku-ji's bird)."""
    S = lambda v: f"{r4(v)} * s"
    def P(x, y, z): return [S(x), f"bh + {r4(y)} * s", S(z)]
    def bar(a, b): return P(*a) + P(*b)
    parts = {
        "base": {"type": "box", "width": "bw", "length": "bw", "height": "bh", "at": [[0, 0, 0, 0]], "when": {"pedestal": "square"},
                 "_about": "the square base the bird stands on"},
        "disc": {"type": "prism", "plan": {"sides": 12, "radius": "bw / 2"}, "height": "bh", "at": [[0, 0, 0, 0]], "when": {"pedestal": "disc"},
                 "_about": "the round pedestal the bird stands on (pedestal \"disc\")"},
        "legs": {"type": "bars", "lines": [bar((-.07, 0, 0), (-.03, .33, 0)), bar((.07, 0, 0), (.03, .33, 0))],
                 "w": "0.035 * s", "h": "0.035 * s", "caps": False, "kind": "moulding"},
        "body": {"type": "bars", "paths": [[P(0, .34, -.28), P(0, .42, 0), P(0, .52, .16), P(0, .74, .22), P(0, .9, .2)]],
                 "w": "0.16 * s", "h": "0.17 * s", "kind": "moulding", "_about": "the body from the tail's root up the breast to the neck"},
        "head": {"type": "bars", "lines": [bar((0, .9, .2), (0, .86, .34)), bar((0, .92, .2), (0, 1.05, .1)), bar((0, .88, .17), (0, .98, .04))],
                 "w": "0.05 * s", "h": "0.08 * s", "caps": False, "kind": "moulding", "_about": "the beak, the crest and the wattle"},
    }
    L = []
    for sg in (-1, 1):
        for j, (dy, dz) in enumerate(((.62, -.02), (.54, -.14), (.44, -.22), (.32, -.28))):
            L.append(bar((sg * .07, .46, -.02), (sg * (.12 + .05 * j), .46 + dy, dz)))
    for dx, dy, dz, ky in ((0, .28, -.72, 1), (.11, .22, -.7, .85), (-.11, .22, -.7, .85), (.22, .12, -.62, .65), (-.22, .12, -.62, .65), (.3, .0, -.5, .45), (-.3, .0, -.5, .45)):
        # (the tail's tip raised tail_rise x ky and drawn in a little as it rises)
        L.append(P(0, .36, -.26) + [S(dx), f"bh + ({r4(.36 + dy)} + {ky} * tail_rise) * s", f"({r4(-.26 + dz)} + {r4(.3 * ky)} * tail_rise) * s"])
    parts["feathers"] = {"type": "bars", "lines": L, "w": "0.03 * s", "h": "0.06 * s", "caps": False, "kind": "moulding",
                         "_about": "the raised wings, four flight feathers a side, and the fan of the tail"}
    doc = {"name": "Phoenix",
           "_about": "THE PHOENIX (hoo), the gilt bronze bird on a Japanese hall's ridge or finial -- Kinkaku-ji's on its pyramid, the pair on the "
                     "Phoenix Hall's ridge ends: straight `bars` read as a silhouette (body, breast, neck and crest, two legs, the wings raised, the "
                     "tail's fan), facing +z, on a square base. `s` its size (1: about a metre to the crest), `bw` `bh` the base, `pedestal` \"disc\" a round "
                     "one, \"none\" none (set bh 0 with it), `tail_rise` the tail swept up. Written by tools/archgen/japanese.py.",
           "params": {"detail": 4, "s": 1.0, "bw": .62, "bh": .2, "pedestal": "square", "tail_rise": 0},
           "build": list(parts), "parts": parts}
    out = os.path.join(ROOT, "assets", "architecture", "components", "phoenix.json")
    with open(out, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")


def hoju_component():
    """components/hoju: THE JEWEL (hoju) on a pyramid roof's apex (a corner tower's, a hexagonal hall's) -- a round base, a
    waist, the bulb swelling and drawn up to a point: a `loft` about y. Param `s` its size (1: about 1.1m tall, the bulb
    .55 across); y 0 its foot, on the apex (tiered's `top.ridgeEnds` sets it there)."""
    prof = ((0, .3), (.12, .3), (.16, .17), (.24, .14), (.3, .2), (.48, .27), (.66, .24), (.84, .13), (.98, .03), (1.1, 0))
    parts = {"jewel": {"type": "loft", "axis": "y", "sides": 12, "at": [[0, 0, 0, 0]],
                       "sections": [{"s": f"{r4(y)} * s", "u": 0, "v": 0, "a": f"{r4(r)} * s", "b": f"{r4(r)} * s", "n": 2} for y, r in prof],
                       "_about": "the base, the waist, the bulb drawn up to its point"}}
    doc = {"name": "Hoju",
           "_about": "THE JEWEL (hoju), the bulb drawn up to a point on a round base and waist, on the apex of a Japanese pyramid roof (hogyo) -- "
                     "the Phoenix Hall's corner towers', Yumedono's. `s` its size (1: about 1.1m tall). Written by tools/archgen/japanese.py.",
           "params": {"detail": 4, "s": 1.0}, "build": list(parts), "parts": parts}
    with open(os.path.join(ROOT, "assets", "architecture", "components", "hoju.json"), "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")


def offset_line(pts, d):
    """the open polyline pts [(x, z), ...] moved `d` to its left (walking from the first point: + is left, - right), each
    fold mitred -- the two runs' offset lines meeting -- so the rails along a folding corridor meet at its corners"""
    def nrm(a, b):
        L = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** .5
        return (-(b[1] - a[1]) / L, (b[0] - a[0]) / L)
    out = []
    for i, p in enumerate(pts):
        n0 = nrm(pts[i - 1], p) if i > 0 else None
        n1 = nrm(p, pts[i + 1]) if i + 1 < len(pts) else None
        if n0 and n1:
            mx, mz = n0[0] + n1[0], n0[1] + n1[1]
            k = d / max(1e-6, mx * n1[0] + mz * n1[1])      # (the mitre: along the bisector, as far as both runs' offsets meet)
            out.append((r4(p[0] + mx * k), r4(p[1] + mz * k)))
        else:
            n = n0 or n1
            out.append((r4(p[0] + n[0] * d), r4(p[1] + n[1] * d)))
    return out


def rail(add, name, hw, hd, y, h, gap=0.0, posts=1.6, w=.07):
    """a railing round a rectangle hw x hd (half sizes) at height y: top rail, mid rail and posts; `gap` leaves the -z side's
    middle open that far either side of the axis (only that side: Kinkaku-ji's balconies open toward the pond there --
    turn the result with `at` for another)"""
    y1, y2 = r4(y + h), r4(y + h * .5); L = []
    for yr in (y1, y2):
        cs = [(-hw, -hd), (-hw, hd), (hw, hd), (hw, -hd)]
        for a, b in zip(cs, cs[1:]): L.append([a[0], yr, a[1], b[0], yr, b[1]])
        if gap: L += [[hw, yr, -hd, gap, yr, -hd], [-gap, yr, -hd, -hw, yr, -hd]]
        else: L.append([hw, yr, -hd, -hw, yr, -hd])
    for sx in (-1, 1):
        n = max(1, round(2 * hd / posts))
        L += [[sx * hw, y, r4(-hd + 2 * hd * j / n), sx * hw, y1, r4(-hd + 2 * hd * j / n)] for j in range(n + 1)]
    n = max(1, round(2 * hw / posts))
    for j in range(1, n):
        x = r4(-hw + 2 * hw * j / n)
        L.append([x, y, hd, x, y1, hd])
        if abs(x) > gap: L.append([x, y, -hd, x, y1, -hd])
    add(name, {"type": "bars", "lines": [[r4(v) for v in l] for l in L], "w": w, "h": w, "caps": False, "kind": "moulding"})


def rail_path(add, name, pts, y, h, posts=1.6, w=.07, closed=False, **kw):
    """a railing along the polyline pts [(x, z), ...] at height y: top and mid rails, a post every `posts` along each run"""
    y1, y2 = r4(y + h), r4(y + h * .5); L = []
    runs = list(zip(pts, pts[1:])) + ([(pts[-1], pts[0])] if closed else [])
    for (ax, az), (bx, bz) in runs:
        for yr in (y1, y2): L.append([ax, yr, az, bx, yr, bz])
        n = max(1, round(((bx - ax) ** 2 + (bz - az) ** 2) ** .5 / posts))
        L += [[ax + (bx - ax) * j / n, y, az + (bz - az) * j / n, ax + (bx - ax) * j / n, y1, az + (bz - az) * j / n] for j in range(n + (0 if closed else 1))]
    add(name, {"type": "bars", "lines": [[r4(v) for v in l] for l in L], "w": w, "h": w, "caps": False, "kind": "moulding", **kw})


def deck(add, name, hw, hd, ihw, ihd, y, t=.16, x=0.0, z=0.0, **kw):
    """a floor round a rectangle: outer half sizes hw hd, the hole ihw ihd (the wall's footprint) left out, its top at y"""
    add(name, {"type": "prism", "plan": {"rect": [r4(2 * hw), r4(2 * hd)], "well": {"rect": [r4(2 * ihw), r4(2 * ihd)]}}, "height": t,
               "at": [[r4(x), r4(y - t), r4(z), 0]], **kw})


def corridor_wing(add, name, path, width, h1, h2, bay, post=.3, floor=.25, balcony=.55, rail_h=.75, roof=None, upper=None, ends=None, side="right", about=None, y=0.0):
    """A COVERED CORRIDOR OF TWO STOREYS along a folding line (a Phoenix Hall's yokuro, a temple's two-storey kairo):
       the ground storey `h1` high, open between its posts (`post` square, one every `bay`), ceiled by the upper floor
       (`floor` thick), which runs out `balcony` past the posts under a railing `rail_h` high; the upper storey `h2`
       high (`upper`: its openings spec, every face -- lattice windows, say), under a gabled roof (`roof`: range roof spec)
       that hips round the outside of every fold and valleys inside it. `path` [[x, z], ...] the middle line, folding
       as it likes; `side` ("right" or "left", walking from its first point) the side that looks OUT -- the `range`'s; `y`
       the ground it stands on. `ends` the openings of the lower storey's two ends (a passage on into the next building:
       the upper's are blank). Parts: <name> lower (its walk the balcony floor), <name> upper, <name> rail 1 and 2 (the
       balcony's rails, out and in, mitred at the folds). Returns the height of the upper storey's wall head."""
    gap = bay - post
    open_ = {"every": bay, "width": r4(gap), "end": r4(post / 2), "sill": 0, "springing": r4(h1 - .35), "head": {"profile": "flat"}}
    E = ends if ends is not None else []
    add(f"{name} lower", {"type": "range", "path": path, "width": width, "height": h1, "thickness": post, "interior": False, "side": side,
                          "faces": {"out": open_, "in": open_, "end": E}, "walk": {"t": floor, "over": balcony}, "parapet": False,
                          "at": [[0, r4(y), 0, 0]], **({"_about": about} if about else {})})
    y2 = y + h1 + floor
    up = upper if upper is not None else {"every": bay, "width": r4(gap * .6), "end": r4(post), "sill": .5, "springing": r4(h2 - .3), "head": {"profile": "flat"}}
    add(f"{name} upper", {"type": "range", "path": path, "width": width, "height": h2, "thickness": .18, "interior": False, "side": side,
                          "faces": {"out": up, "in": up, "end": []}, "walk": False,
                          "roof": roof or {"pitch": 26, "overhang": 1.2, "shell": .3, "ends": "gable"}, "at": [[0, r4(y2), 0, 0]]})
    # the balcony's railing, both sides, at the walk's outer edge -- one line each, mitred at the folds
    off = width / 2 + balcony - .06
    for i, sg in enumerate((-1, 1)):
        rail_path(add, f"{name} rail {i + 1}", offset_line(path, sg * off), r4(y2), rail_h, posts=bay / 2, w=.06)
    return y2 + h2
