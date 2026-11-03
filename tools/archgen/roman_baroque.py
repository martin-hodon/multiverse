# THE ROMAN BAROQUE PIAZZA (a style library, L2): what a papal square is built from, written once here and used by any
# generator that imports it (st_peters.py first). The church fronts themselves are neoclassical.block (the engine's
# giant order, order.js); this module is the square's: Front +z.
#   components/curved-colonnade.json  BERNINI'S COLONNADE: rows of free-standing columns on concentric arcs, radially in line
#                                     (all rows the same count), under ONE entablature swept along the arc across all of
#                                     them, a low lead roof and a parapet on both edges for the saints; by name pediments at
#                                     the arc's two ends and on the middle of its inner and outer faces (the temple fronts).
#                                     Any curved portico -- an exedra, a crescent -- is this with other numbers.
#   arc_points(...)                   points on an arc (statues along a curved balustrade)
#   obelisk(...)                      an Egyptian obelisk re-erected: pedestal, bronze lions, granite shaft, the bronze crown and cross
#   fountain(...)                     a Roman piazza fountain: a round basin, a stem, two mushroom bowls, the water
#   giant_front(...)                  a church front in the giant order through two storeys and an attic, free columns before
#                                     its middle, the entablature (swept profile, inscription band) breaking forward over
#                                     them, a pediment over the middle ones, the balustrade (Maderno's at St Peter's)
# Every number of a component is a param or an expression over its params; the `_x` keys say what x is.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = lambda rel, doc: open(os.path.join(ROOT, "assets/architecture", rel), "w").write(json.dumps(doc, indent=2) + "\n")
DEG = 0.0174533
r3 = lambda v: round(v, 3)


def curved_colonnade():
    """components/curved-colonnade: R the inner row's axis radius (round the component's origin), arc its angle (degrees,
    centred on +z), count columns in every row; d2..d4 the other rows' radii past R. The swept parts follow the arc at R,
    their profile across all four rows (u outward), from colR * 1.6 inside the first to as far past the last"""
    N = 16                                              # points on the arc for the swept parts (a Catmull-Rom curve through them)
    path = lambda: [[f"R * sin(({i} / {N} - 0.5) * arc * {DEG})", f"R * cos(({i} / {N} - 0.5) * arc * {DEG})"] for i in range(N + 1)]
    parts, build = {}, []
    def add(n, d, built=True):
        parts[n] = d
        if built: build.append(n)
    for k, d in enumerate(["0", "d2", "d3", "d4"]):
        add(f"row {k + 1}", {"type": "colonnade", "plan": "round", "arc": "arc", "count": "count", "radius": f"R + {d}", "order": "order",
                              "columnR": f"colR * (1 + colGrow * {k} / 3)", "height": "colH", "taper": "taper", "sides": "colSides", "at": [[0, 0, 0, 0]],
                              **({"_about": "the rows of columns, one arc each, the same count in every row: radially in line, so from the arc's centre the four read as one"} if k == 0 else {})})
    e, o, T = "colR * 1.6", "cornOut", "colH + entH"
    add("entablature", {"type": "sweep", "path": path(), "step": "step", "kind": "moulding",
                        "profile": [[f"0 - {e}", "colH"], [f"d4 + {e}", "colH"], [f"d4 + {e}", f"{T} - cornH"], [f"d4 + {e} + {o}", f"{T} - cornH"],
                                    [f"d4 + {e} + {o}", T], [f"0 - {e} - {o}", T], [f"0 - {e} - {o}", f"{T} - cornH"], [f"0 - {e}", f"{T} - cornH"]],
                        "standsOn": ["row 1"],
                        "_about": "ONE entablature over all the rows, swept along the arc: architrave and frieze, the cornice standing out on both faces"})
    add("roof", {"type": "sweep", "path": path(), "step": "step", "kind": "roof",
                 "profile": [[f"0 - {e} + balT", T], [f"d4 + {e} - balT", T], ["d4 / 2", f"{T} + roofRise"]], "standsOn": ["entablature"],
                 "_about": "the low lead roof between the parapets"})
    for nm, u0, u1 in (("inner balustrade", f"0 - {e} - {o} + 0.1", f"0 - {e} - {o} + 0.1 + balT"),
                       ("outer balustrade", f"d4 + {e} + {o} - 0.1 - balT", f"d4 + {e} + {o} - 0.1")):
        add(nm, {"type": "sweep", "path": path(), "step": "step", "kind": "moulding", "standsOn": ["entablature"],
                 "profile": [[u0, T], [u1, T], [u1, f"{T} + balH"], [u0, f"{T} + balH"]],
                 **({"_about": "the balustrades along both edges of the roof (the saints stand on the inner one: the building's statues)"} if nm.startswith("inner") else {})})
    # THE TEMPLE FRONTS (by name): a pediment over each end of the arc, turned along it, on the entablature; and over the middle
    # of the inner face and of the outer, facing out of each. Each is components/portico's pediment alone.
    ped = lambda w, d: {"count": 2, "spacing": w, "colR": "colR", "colH": "colH", "entH": "entH", "order": "tuscan", "depth": d, "steps": 0, "pitch": "pitch", "W": w}
    rm = "(R + d4 / 2)"
    end = lambda s: [f"{rm} * sin({s} * (arc / 2 * {DEG} + colR * 1.6 / {rm} - endD / {rm}))", 0,
                     f"{rm} * cos({s} * (arc / 2 * {DEG} + colR * 1.6 / {rm} - endD / {rm}))",
                     f"{s} * (arc / 2 * {DEG} + colR * 1.6 / {rm} - endD / {rm}) + {s} * 1.5707963"]
    add("end fronts", {"type": "component", "use": "components/portico", "params": ped(f"d4 + {e} * 2 + {o} * 2", "endD * 2"), "build": ["pediment"],
                       "at": [end(1), end(-1)], "standsOn": ["entablature"], "_about": "a pediment over each end of the arc, turned along it (by name)"}, built=False)
    add("middle fronts", {"type": "component", "use": "components/portico", "params": ped("midW", "midD"), "build": ["pediment"],
                          "at": [[0, 0, f"R - {e} - {o} + midD / 2", 3.1415927], [0, 0, f"R + d4 + {e} + {o} - midD / 2", 0]], "standsOn": ["entablature"],
                          "_about": "...and over the middle of the inner face and of the outer, facing out of each (by name)"}, built=False)
    # the PIERS the temple fronts stand on (by name): square pillars in place of the inner and outer rows' end columns, and
    # either side of the middle fronts
    pier = lambda rr, a: [f"{rr} * sin({a})", 0, f"{rr} * cos({a})", a]
    A = f"(arc / 2 * {DEG})"
    add("end piers", {"type": "box", "width": "colR * 2.6", "length": "colR * 2.6", "height": "colH", "courses": True,
                      "at": [pier(rr, f"{s} * {A}") for rr in ("R", "(R + d4)") for s in (1, -1)],
                      "_about": "square pillars at the arc's ends, in place of the inner and outer rows' last columns, under the end fronts (by name)"}, built=False)
    add("middle piers", {"type": "box", "width": "colR * 2.6", "length": "colR * 2.6", "height": "colH", "courses": True,
                         "at": [pier(rr, f"{s} * (midW / 2 - colR * 1.3) / {rr}") for rr in ("R", "(R + d4)") for s in (1, -1)],
                         "_about": "...and either side of the middle fronts, on the inner and the outer row (by name)"}, built=False)
    params = {"detail": 4, "R": 68.5, "arc": 145.0, "count": 33, "d2": 4.4, "d3": 10.6, "d4": 15.0, "order": "tuscan", "colR": 0.8, "colH": 13.0,
              "taper": 0.86, "colSides": 10, "colGrow": 0, "entH": 2.8, "cornH": 0.8, "cornOut": 0.7, "roofRise": 2.0, "balH": 1.6, "balT": 0.5, "step": 2.5,
              "pitch": 22, "endD": 2.0, "midW": 16.0, "midD": 3.0,
              "_R": "the inner row's axis radius round the component's origin; arc its angle in degrees, centred on +z; count the columns in EVERY row (so the rows are radially in line)",
              "_d2": "rows 2, 3 and 4 at R + d2, R + d3, R + d4 (Bernini's: the middle gap wider, a carriage way)",
              "_order": "the columns' order (ORDERS), colR their radius, colH base to abacus, colSides their facets, taper the shaft's top; colGrow: the outer rows' columns thicker, row 4's by that share (Bernini's, so the rows line up as one)",
              "_entH": "the swept entablature over all rows (cornH its cornice, cornOut how far it stands out); roofRise the low roof's ridge; balH, balT the parapets",
              "_step": "metres between the rings of the swept parts along the arc (their cost)",
              "_endD": "end fronts / middle fronts (by name): pediments of `pitch` -- each end's endD * 2 deep, its front at the arc's end; the middle ones midW wide, midD deep; end piers / middle piers (by name): the square pillars under them"}
    OUT("components/curved-colonnade.json", {"name": "Curved colonnade",
        "_about": "BERNINI'S COLONNADE, St Peter's Square: rows of free-standing columns on concentric arcs, radially in line, under one entablature swept along the arc over all of them, a low lead roof and a parapet on either edge for the saints; pediments over the arc's ends and the middle of its faces by name. Written by tools/archgen/roman_baroque.py.",
        "params": params, "build": build, "parts": parts})


def arc_points(cx, cz, r, a0, a1, n, y, yaw=0.0):
    """n points evenly on an arc of radius r round (cx, cz) from angle a0 to a1 (degrees, 0 toward local +z, before `yaw`
    turns it as the engine turns a placement), at height y: statues along a curved balustrade"""
    out = []
    for k in range(n):
        a = math.radians(a0 + (a1 - a0) * (k + .5) / n)
        lx, lz = r * math.sin(a), r * math.cos(a)
        c, s = math.cos(yaw), math.sin(yaw)
        out.append((r3(cx + lx * c + lz * s), r3(y), r3(cz - lx * s + lz * c)))
    return out


def obelisk(add, x, z, *, shaft=25.5, foot=1.35, top=0.9, pedH=8.3, pedW=6.0, crown=4.2, name="obelisk", lions=True):
    """an Egyptian obelisk re-erected: the stepped pedestal, four bronze lions under the shaft's corners, the granite shaft
    `shaft` high from `foot` to `top` half-width, its pyramidion, the bronze mounts and star (a cage of bars) and the cross
    `crown` over it. Returns the height of the cross's top. (lions=False: no lions; crown=0: no bronze crown -- a plain
    Baroque obelisk, Fulda's)"""
    add(f"{name} steps", {"type": "crepidoma", "width": r3(pedW + 1.2), "length": r3(pedW + 1.2), "steps": 3, "stepH": 0.3, "stepOut": 0.6,
                          "at": [[r3(x), 0, r3(z), 0]], "_about": "the obelisk's steps..."})
    add(f"{name} pedestal", {"type": "box", "width": r3(pedW), "length": r3(pedW), "height": r3(pedH - 0.9 - (1.4 if lions else 0)), "at": [[r3(x), 0.9, r3(z), 0]],
                             "courses": True, "_about": "...its pedestal..."})
    if lions: add(f"{name} lions", {"type": "box", "width": 1.0, "length": 1.4, "height": 1.4,
                          "at": [[r3(x + sx * (foot - .3)), r3(pedH - 1.4), r3(z + sz * (foot - .3)), 0] for sx in (-1, 1) for sz in (-1, 1)],
                          "_about": "...the four bronze lions it stands on"})
    add(f"{name}", {"type": "column", "radius": r3(foot * 1.4142), "height": r3(shaft), "sides": 4, "taper": r3(top / foot),
                    "at": [[r3(x), r3(pedH), r3(z), 0.785398]], "_about": "the granite shaft, uninscribed"})
    add(f"{name} pyramidion", {"type": "column", "radius": r3(top * 1.4142), "height": r3(top * 1.3), "sides": 4, "taper": 0.02,
                               "at": [[r3(x), r3(pedH + shaft), r3(z), 0.785398]], "_about": "its pyramidion"})
    yC = pedH + shaft + top * 1.3 - 0.2
    L = lambda a, b: [r3(a[0]), r3(a[1]), r3(a[2]), r3(b[0]), r3(b[1]), r3(b[2])]
    if crown <= 0: return yC + 0.2
    add(f"{name} crown", {"type": "bars", "w": 0.2, "h": 0.2, "kind": "bronze",
                          "lines": [L((x, yC, z), (x, yC + crown, z)), L((x - .8, yC + crown - 1.0, z), (x + .8, yC + crown - 1.0, z)),
                                    L((x - .7, yC + .9, z - .7), (x + .7, yC + .9, z + .7)), L((x - .7, yC + .9, z + .7), (x + .7, yC + .9, z - .7)),
                                    L((x - .8, yC + 1.9, z), (x + .8, yC + 1.9, z)), L((x, yC + 1.9, z - .8), (x, yC + 1.9, z + .8))],
                          "_about": "the bronze over it: the Chigi mounts and star (a cage of bars), the cross"})
    return yC + crown


def fountain(add, x, z, *, R=4.6, name="fountain"):
    """a Roman piazza fountain (Maderno's, and Bernini's copy of it): a round basin on a step, a stem, a great MUSHROOM bowl
    turned up, a smaller one over it, the jet: lofts for the bowls, `flow` markers for the water"""
    add(f"{name} step", {"type": "column", "radius": r3(R + 0.6), "height": 0.3, "sides": 24, "at": [[r3(x), 0, r3(z), 0]], "_about": "the fountain's step..."})
    add(f"{name} basin", {"type": "ring", "count": 24, "rOuter": r3(R), "rInner": r3(R - 0.45), "height": 0.75, "y": 0.3, "solid": True, "polygon": True,
                          "place": [[r3(x), 0, r3(z), 0]], "standsOn": [f"{name} step"], "_about": "...its round basin"})
    add(f"{name} stem", {"type": "column", "radius": 0.75, "height": 2.4, "sides": 12, "taper": 0.7, "at": [[r3(x), 0.3, r3(z), 0]], "standsOn": [f"{name} step"]})
    bowl = lambda r, y0, h: {"type": "loft", "axis": "y", "sides": 20, "smooth": 3, "at": [[r3(x), r3(y0), r3(z), 0]],
                             "sections": [{"s": 0, "a": r3(r * .18), "b": r3(r * .18)}, {"s": r3(h * .35), "a": r3(r * .55), "b": r3(r * .55)},
                                          {"s": r3(h * .8), "a": r3(r * .97), "b": r3(r * .97)}, {"s": r3(h), "a": r3(r), "b": r3(r)}]}
    add(f"{name} lower bowl", {**bowl(2.9, 2.6, 1.3), "standsOn": [f"{name} stem"], "_about": "the great bowl turned up like a mushroom's cap, the water spilling over its rim..."})
    add(f"{name} upper stem", {"type": "column", "radius": 0.35, "height": 1.0, "sides": 10, "taper": 0.8, "at": [[r3(x), 3.85, r3(z), 0]], "standsOn": [f"{name} lower bowl"]})
    add(f"{name} upper bowl", {**bowl(1.5, 4.8, 0.8), "standsOn": [f"{name} upper stem"], "_about": "...and the small one over it"})
    add(f"{name} water", {"type": "marker", "role": "flow", "at": [[r3(x), 0.95, r3(z), 0]],
                          "data": {"kind": "pool", "r": r3(R - 0.5), "seg": 24}, "_about": "the water in the basin"})
    add(f"{name} jet", {"type": "marker", "role": "flow", "at": [[r3(x), 5.6, r3(z), 0]], "data": {"kind": "jet", "r": 0.12, "h": 2.2}})


def opening(at, w, sill, h, arched, **kw):
    """an opening `w` wide from `sill`, `h` to its crown (a semicircular head if `arched`, else flat)"""
    return {"at": at, "width": w, "sill": sill, "springing": r3(sill + h - (w / 2 if arched else 0)),
            "head": {"profile": "semicircular" if arched else "flat"}, **kw}


def giant_front(add, bal, *, z, y, W, D, G0, G1, GA, doors, arches, ends, cols, pedCols, x=0.0, thick=2.4, pitch=19, name="front"):
    """A ROMAN CHURCH FRONT IN THE GIANT ORDER (Maderno's at St Peter's): a block W wide and D deep, its face on z
    facing +z, the floor at y. The order (order.js: Corinthian pilasters on the piers, its entablature round the block)
    through the portals' storey G0 and the loggia's G1, the attic GA over it. `doors` (x) the portals under alternate
    pediments with the loggia's windows over them, `arches` the great arches (passages), `ends` the end bays' windows;
    free-standing giant COLUMNS at `cols` (either side of the middle), the entablature breaking forward over them --
    architrave, frieze with its inscription band, cornice (a swept profile) -- the pediment over the `pedCols` middle
    ones, the flat roof and its balustrade (`bal`, neoclassical.Balusters). Returns the height of the walls' head."""
    xs = lambda v: r3(x + v)
    big = lambda v: v == 0
    face0 = [{"h": G0, "openings": [opening(xs(v), 4.2 if big(v) else 3.8, 0, 8.6 if big(v) else 7.6, False, glass=False,
                                            surround={"head": "pediment", "pediment": "alternate"}) for v in doors]
                                   + [opening(xs(v), 6.6, 0, min(15.5, G0 - 1.5), True, glass=False) for v in arches]
                                   + [opening(xs(v), 3.2, 7.0, 6.0, False, surround={"head": "pediment", "pediment": "segmental"}) for v in ends]},
             {"h": G1, "openings": [opening(xs(v), 5.6 if big(v) else 4.6, 2.0, min(10.5 if big(v) else 9.0, G1 - 3.0), True, glass=not big(v),
                                            surround={"head": "pediment", "pediment": "alternate"}) for v in doors]
                                   + [opening(xs(v), 3.6, 3.0, min(7.5, G1 - 5.0), False, surround={"head": "pediment", "pediment": "triangular"}) for v in arches + ends]},
             {"openings": [opening(xs(v), 3.0, 3.2, min(4.4, GA - 4.5), False) for v in doors + arches + ends]}]
    back = [{"h": G0, "openings": [opening(xs(0.0), 12.0, 0, min(16.0, G0 - 1.0), True, glass=False)]
                                  + [opening(xs(s * v), 6.0, 0, 12.0, True, glass=False) for v in doors[-1:] for s in (-1, 1) if v]},
            {"h": G1, "openings": []}, {"openings": []}]
    add(name, {"type": "enclosure", "plan": {"rect": [W, D]}, "thickness": thick, "height": G0 + G1 + GA,
               "tiers": [{"h": G0, "openings": []}, {"h": G1, "openings": []}, {"openings": []}],
               "faces": {"0": face0, "2": back}, "orders": [{"tier": 0, "kind": "corinthian", "span": 2, "proj": 0.8}], "courses": True,
               "interior": True, "glass": True, "at": [[r3(x), r3(y), r3(z - D / 2), 0]],
               "_about": "the front in the giant Corinthian order through the portals' storey and the loggia's, the Benediction loggia in "
                         "the middle, the attic over the entablature; the narthex behind it"})
    m = (G0 + G1) / 25.0                                 # the order's module (Corinthian: 20 for the column, 5 for the entablature)
    R, CH, E = m, 20 * m, 5 * m
    zc = z + 0.8 * m + R * 0.55                          # the columns' axis, before the pilasters
    add(f"{name} columns", {"type": "colonnade", "plan": "straight", "count": 1, "spacing": 1.0, "order": "corinthian", "columnR": r3(R), "height": r3(CH),
                            "taper": 0.88, "sides": 16, "at": [[xs(s * v), r3(y), r3(zc), 0] for v in cols for s in (-1, 1)],
                            "_about": f"the {2 * len(cols)} giant columns standing out of the order's pilasters"})
    EW, h0 = 2 * cols[-1] + 2 * R + 2.0, R + 0.5         # the entablature's run, its half depth
    prof = [(-h0, 0), (h0, 0), (h0, .3), (h0 - .12, .3), (h0 - .12, .63), (h0 + .25, .63), (h0 + .25, .75), (h0 + .75, .75), (h0 + .75, 1.0),
            (-h0 - .75, 1.0), (-h0 - .75, .75), (-h0 - .25, .75), (-h0 - .25, .63), (-h0 + .12, .63), (-h0 + .12, .3), (-h0, .3)]
    add(f"{name} entablature", {"type": "sweep", "kind": "moulding", "step": 4.0, "path": [[r3(-EW / 2), 0], [r3(EW / 2), 0]],
                                "profile": [[r3(u), r3(v * E)] for u, v in prof], "at": [[r3(x), r3(y + CH), r3(zc), 0]], "standsOn": [f"{name} columns"],
                                "_about": "the entablature breaking forward over the columns: architrave, frieze, the cornice standing out"})
    add(f"{name} inscription", {"type": "box", "width": r3(2 * cols[-2] + 2 * R), "length": 0.12, "height": r3(E * 0.33 * 0.7),
                                "at": [[r3(x), r3(y + CH + E * (0.3 + 0.33 * 0.15)), r3(zc + h0 - 0.12 + 0.03), 0]], "standsOn": [f"{name} entablature"],
                                "_about": "the dedication's band along the frieze"})
    PW = 2 * pedCols[-1] + 2 * R + 2.4
    add(f"{name} pediment", {"type": "roof", "form": "gable", "width": r3(PW), "length": r3(2 * h0 + 1.5), "pitch": pitch, "overhang": 0.5,
                             "at": [[r3(x), r3(y + CH + E), r3(zc), 0]], "standsOn": [f"{name} entablature"],
                             "_about": f"the pediment over the middle {2 * len(pedCols)} columns, before the attic"})
    top = y + G0 + G1 + GA
    add(f"{name} roof", {"type": "prism", "plan": {"rect": [W, D]}, "height": 0.4, "flatRoof": True, "at": [[r3(x), r3(top), r3(z - D / 2), 0]]})
    bal.run((x - W / 2 + 0.4, z - 0.3), (x + W / 2 - 0.4, z - 0.3), top + 0.4)
    for s in (-1, 1):
        bal.run((x + s * (W / 2 - 0.3), z - 0.5), (x + s * (W / 2 - 0.3), z - D + 0.5), top + 0.4)
    return top


def write_components():
    curved_colonnade()


if __name__ == "__main__":
    write_components()
