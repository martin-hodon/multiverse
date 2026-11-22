"""THE MODERN AGE'S KIT (2026-11-20; docs/modern.md): what every modern generator (tools/modern/*.py, run by
tools/moderngen.py) writes its items with -- the item's frame and its parts as small functions, so a car, a bus and a
fridge say only what they are. Items are written to assets/items/modern/<group>/<name>.json and listed in the
catalogue (assets/index.json) under "Modern: <group>".

THE FRAME of a vehicle (and of anything that stands): the origin on the ground under its middle, +x its front, y up,
z across (+z its right, as a ship's starboard). Lengths in metres, angles in degrees (items.js `at`: x y z yaw pitch roll).
"""
import fcntl, json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
ITEMS = os.path.join(ROOT, "assets", "items")
WRITTEN = {}   # (group -> [paths]: what the catalogue lists)
ERA, REGION = "1880-2030", "everywhere"


def r3(v):   # (numbers rounded to the millimetre: the json stays readable)
    if isinstance(v, float): return round(v, 4)
    if isinstance(v, list): return [r3(x) for x in v]
    if isinstance(v, dict): return {k: r3(x) for k, x in v.items()}
    return v


def write(path, doc, group=None):
    """path under assets/items (no extension): "modern/vehicles/car" -- listed under its group in the catalogue."""
    full = os.path.join(ITEMS, path + ".json")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        json.dump(r3(doc), f, indent=1, ensure_ascii=False)
        f.write("\n")
    WRITTEN.setdefault(group or path.split("/")[1], []).append("items/" + path)


def item(name, category, about, materials, parts, params=None, markers=None, hold=None, era=ERA, region=REGION):
    d = {"kind": "item", "name": name, "category": category, "era": era, "region": region, "_about": about,
         "params": params or {}, "materials": materials, "parts": [p for p in parts if p]}
    if markers: d["markers"] = markers
    if hold: d["hold"] = hold
    return d


# ---- PARTS ---------------------------------------------------------------------------------------------------------
def box(id_, mat, size, at, **k):
    return {"id": id_, "type": "box", "material": mat, "size": list(size), "at": at, **k}


def rod(id_, mat, r, a, b, sides=8, **k):
    return {"id": id_, "type": "rod", "material": mat, "r": r, "from": list(a), "to": list(b), "sides": sides, **k}


def sphere(id_, mat, r, at, **k):
    return {"id": id_, "type": "sphere", "material": mat, "r": r, "at": at, **k}


def lathe(id_, mat, profile, at=None, **k):
    d = {"id": id_, "type": "lathe", "material": mat, "profile": [list(q) for q in profile], **k}
    if at is not None: d["at"] = at
    return d


def sweep(id_, mat, path, r=None, section=None, **k):
    d = {"id": id_, "type": "sweep", "material": mat, "path": [list(q) for q in path], **k}
    if r is not None: d["r"] = r
    if section is not None: d["section"] = list(section)
    return d


def plate(id_, mat, outline, thick, at=None, **k):
    d = {"id": id_, "type": "plate", "material": mat, "outline": [list(q) for q in outline], "thick": thick, **k}
    if at is not None: d["at"] = at
    return d


def ring(id_, mat, r, tube, at, **k):
    return {"id": id_, "type": "ring", "material": mat, "r": r, "tube": tube, "at": at, **k}


def loft(id_, mat, stations, round_=0.05, holes=None, caps=True, **k):
    """rounded sections along +x (items.js loft): stations [x, hw, y0, y1, tw?]; holes [{x: [a, b], y: [a, b], side}]"""
    d = {"id": id_, "type": "loft", "material": mat, "stations": [list(s) for s in stations], "round": round_, **k}
    if holes: d["holes"] = holes
    if caps is not True: d["caps"] = caps
    return d


def use(id_, path, at, params=None, materials=None, **k):
    d = {"id": id_, "use": "items/" + path, "at": at, **k}
    if params: d["params"] = params
    if materials: d["materials"] = materials
    return d


def hinge(id_, pivot, parts, axis=(0, 1, 0), max_=65, **k):
    """a HINGED piece (items.js hinge): its parts written in the parent's own frame, swung `max_` degrees about the axis
    through `pivot` when the item's `open` param says (0 shut .. 1 wide) -- a door, a bonnet, a lid; the viewer swings it"""
    return {"id": id_, "type": "hinge", "pivot": list(pivot), "axis": list(axis), "max": max_, "parts": [p for p in parts if p], **k}


def slide(id_, move, parts, **k):
    """a SLIDING piece (items.js slide): its parts in the parent's frame, moved by `move` [x, y, z] metres when open --
    a van's side door on its rail, a drawer"""
    return {"id": id_, "type": "slide", "move": list(move), "parts": [p for p in parts if p], **k}


def plug_slide(id_, move, parts, out=0.25, **k):
    """a PLUG SLIDING door (a van's side door, a helicopter's cabin door): first out of its opening by move's sideways
    part, over the first `out` of the share, then back along its rail by the rest -- so it never passes through the skin.
    Two nested slides (items.js `range`): `<id>Out` carries `<id>`"""
    side, run = [0, 0, move[2]], [move[0], move[1], 0]
    return slide(id_ + "Out", side, [slide(id_, run, parts, range=[out, 1])], range=[0, out], **k)


def steer(id_, pivot, parts, max_=35, by="steer"):
    """a STEERED front wheel, both sides (items.js hinge `by`, 2026-11-22): `parts` written for the RIGHT side
    (+z, unmirrored), turned about the upright through `pivot` (its centre on the right) by the item's `steer` param,
    -1..1 (+1 full lock to the left, `max_` degrees). Two hinges, `<id>` and `<id>L`: the left is the right reflected
    across z by a `stretch` [1, 1, -1] (built exactly as a `mirror` "z" copy), its angle negated, since a reflected
    leaf turns the other way -- both wheels then turn the same way. Straight (steer 0) the build is the unsteered one"""
    return [hinge(id_, pivot, parts, max_=max_, by=by),
            hinge(id_ + "L", pivot, parts, max_=-max_, by=by, stretch=[1, 1, -1])]


def region(x0, x1, y0=None, y1=None, side="right", **k):
    """a stretch of a loft's surface -- a loft's `only` (a door cut out of the body it closes) or its `holes`; no y:
    the whole height"""
    return {"x": [x0, x1], **({"y": [y0, 9 if y1 is None else y1]} if y0 is not None else {}), "side": side, **k}


def piece(src, regions, id_=None, gap=0.006, **over):
    """the PIECE of a loft that closes some of its holes -- a door's skin, a tailgate, a pane: the same loft (its
    stations, rounding, arches) keeping only `regions`, each drawn in by `gap` (the shut line; not at the open ends:
    a y running on to 9, an x past the loft's end), its own holes and `bare` dropped. `over`: anything else (holes
    of its own: a door's window)"""
    xs = [s[0] for s in src["stations"]]
    def shrink(r):
        r = dict(r); x0, x1 = r["x"]
        r["x"] = [x0 + gap if x0 > xs[0] else x0, x1 - gap if x1 < xs[-1] else x1]
        if "y" in r: y0, y1 = r["y"]; r["y"] = [y0 + gap if y0 > -1e8 else y0, y1 - gap if y1 < 9 else y1]
        return r
    d = {k: v for k, v in src.items() if k not in ("holes", "bare", "id", "only")}
    return {**d, "id": id_ or src["id"], "only": [shrink(r) for r in regions], **over}


def cut(src, regions, **over):
    """a loft with `regions` cut out as holes besides its own -- the body with its doors' openings"""
    return {**src, "holes": [*src.get("holes", []), *regions], **over}


def hole(x0, x1, y0, y1, side="both"):
    return {"x": [x0, x1], "y": [y0, y1], "side": side}


# ---- REPEATS (items.js `each`) ---------------------------------------------------------------------------------------
def _num(x, d=6):   # (no exponent: expr.js reads 0.00004, not 4e-05)
    x = round(x, d)
    return str(int(x)) if x == int(x) else format(x, f".{d + 3}f").rstrip("0")


def _lin(vals, as_):
    """the numbers vals (one a copy) as one expression in `as_` -- "b + s * i" -- that gives each copy's stored
    number back exactly (the json keeps 4 decimals: kit.r3), or None"""
    v = [r3(x) for x in vals]
    if all(x == v[0] for x in v): return v[0]
    b, s = v[0], round(v[1] - v[0], 6)
    if any(abs(b + s * i - x) > 1e-9 for i, x in enumerate(v)):
        # (a step that is no round number -- a wall's 16 m in seven bays: each copy's number was rounded to 4
        #  decimals on its own; the expression rounds it the same way, round() in items.js's expressions)
        b, s = round(vals[0], 9), round((vals[-1] - vals[0]) / (len(v) - 1), 9)
        if any(abs(math.floor((b + s * i) * 10000 + 0.5) / 10000 - x) > 1e-12 for i, x in enumerate(v)): return None
        return f"round(({_num(b, 9)} {'+' if s > 0 else '-'} {_num(abs(s), 9)} * {as_}) * 10000) / 10000"
    term = as_ if s in (1, -1) else f"{_num(abs(s))} * {as_}"
    if b == 0: return term if s > 0 else f"-{term}"
    return f"{_num(b)} {'+' if s > 0 else '-'} {term}"


def _grid(vals, as_, m):
    """the numbers vals as a GRID in `as_`, m copies a row -- "b + R * floor(i / m) + C * (i - m * floor(i / m))": a
    row's step C, the next row's R (a keg grid's columns, a course laid in the last one's hollows, toes to alternate
    sides with m = 2); a partial last row too. Exact at the json's 4 decimals, or None"""
    v = [r3(x) for x in vals]
    b, C, R = v[0], round(v[1] - v[0], 6), round(v[m] - v[0], 6)
    if any(abs(b + R * (i // m) + C * (i % m) - x) > 1e-9 for i, x in enumerate(v)): return None
    row, col = f"floor({as_} / {m})", f"({as_} - {m} * floor({as_} / {m}))"
    out = _num(b) if b != 0 else ""
    for s, t in ((R, row), (C, col)):
        if s == 0: continue
        term = t if abs(s) == 1 else f"{_num(abs(s))} * {t}"
        out = (f"{out} {'+' if s > 0 else '-'} {term}" if out else (term if s > 0 else f"-{term}"))
    return out or 0


def _fold(vals, as_, key=None, m=None, top=False):
    a = vals[0]
    if all(isinstance(x, bool) or x is None for x in vals) or isinstance(a, bool):
        return a if all(x == a for x in vals) else None
    if all(isinstance(x, (int, float)) for x in vals):
        f = _lin(vals, as_)
        return _grid(vals, as_, m) if f is None and m else f
    if isinstance(a, str):
        if all(x == a for x in vals): return a
        if key == "when":   # (each copy gated by its own param: "w0", "w1", .. -> "w{i}", items.js)
            t = a.replace(str(0), "{" + as_ + "}", 1) if "0" in a else None
            return t if t and all(x == t.replace("{" + as_ + "}", str(i)) for i, x in enumerate(vals)) else None
        return None
    if isinstance(a, list):
        if not all(isinstance(x, list) and len(x) == len(a) for x in vals): return None
        out = [_fold([x[j] for x in vals], as_, None, m) for j in range(len(a))]
        return None if any(o is None and any(x[j] is not None for x in vals) for j, o in enumerate(out)) else out
    if isinstance(a, dict):
        if not all(isinstance(x, dict) and x.keys() == a.keys() for x in vals): return None
        out = {}
        for k in a:
            if k == "id":   # (the run's own id is set by each/runs; a part inside keeps its id where every copy's is the same
                if top: continue   # -- a slide inside the run, so its joint is `<run>#i`'s; one whose ids differ does not fold)
                if all(x[k] == a[k] for x in vals): out[k] = a[k]
                elif a.get("type") in ("hinge", "slide"): return None
                continue
            o = _fold([x[k] for x in vals], as_, k, m)
            if o is None and a[k] is not None: return None
            out[k] = o
        return out
    return None


_JS = {"min": min, "max": max, "floor": math.floor, "ceil": math.ceil, "round": lambda x: math.floor(x + 0.5), "abs": abs,
       "atan2": math.atan2, "sin": math.sin, "cos": math.cos, "sqrt": math.sqrt}   # (expr.js's functions, as items.js reckons them)


def _same(t, c, env):
    """does the template leaf t (an expression in the copy's index, or a value) give the copy's leaf c?"""
    if isinstance(t, dict): return isinstance(c, dict) and t.keys() - {"id"} == c.keys() - {"id"} and all(_same(t[k], c[k], env) for k in t if k != "id")
    if isinstance(t, list): return isinstance(c, list) and len(t) == len(c) and all(_same(a, b, env) for a, b in zip(t, c))
    if isinstance(t, str) and isinstance(c, (int, float)) and not isinstance(c, bool):
        try: v = eval(t, {"__builtins__": {}}, {**_JS, **env})
        except Exception: return False
        return abs(v - r3(c)) <= 1e-12
    if isinstance(t, (int, float)) and isinstance(c, (int, float)): return r3(t) == r3(c)
    return t == c


def each(id_, copies, as_="i", like=None):
    """a RUN of parts that differ only by steps (posts, panes, books, seats) as ONE part laid `len(copies)` times
    (items.js `each`): every number that changes from copy to copy becomes an expression in `as_` -- if each steps
    evenly, so every copy comes out as written. Copies that do not fold are returned as they are (a list)."""
    copies = [c for c in copies if c]
    if len(copies) < 2: return copies
    if like is not None:   # (the run written as one part by hand -- a curve's numbers: checked against every copy)
        bad = [i for i, c in enumerate(copies) if not _same(like, c, {as_: i, as_ + "_t": i / (len(copies) - 1)})]
        if bad: print(f"  each {id_}: copies {bad[:5]} differ from the expression; written out"); return copies
        return [{"id": id_, "each": len(copies) if as_ == "i" else {"n": len(copies), "as": as_}, **{k: v for k, v in like.items() if k != "id"}}]
    f = _fold(copies, as_, top=True)
    if f is None: return copies
    return [{"id": id_, "each": len(copies) if as_ == "i" else {"n": len(copies), "as": as_}, **f}]


def runs(id_, copies, key=None, as_="i", grid=True, least=3):
    """a list of parts as the fewest `each` runs, in order: cut where it gives the fewest parts, each stretch of at
    least `least` that folds (`each`) one part -- or, with `grid`, folds as rows of m (`_grid`: kegs in a 3 x 3 block, a
    second course in the first's hollows, toes to alternate sides with m = 2). `key(part)` keeps apart what must not
    share a run (a big cask's from a keg's); by default the parts' shape with their numbers left out. What folds with
    nothing stays the part it was. Every fold is checked against its copies. The runs are named `id_`, then `id_ 2`,
    `id_ 3`, .. (ids become `id#i`)"""
    def shape(p):
        def s(v):
            if isinstance(v, bool) or v is None or isinstance(v, str): return v
            if isinstance(v, (int, float)): return 0
            if isinstance(v, list): return [s(x) for x in v]
            return {k: s(x) for k, x in v.items() if k != "id"}
        return json.dumps(s(p), sort_keys=True)
    key = key or shape
    cs = [c for c in copies if c]
    K = [key(c) for c in cs]
    def fold(a, b):
        run = cs[a:b]
        if len(run) < max(2, least) or any(k != K[a] for k in K[a:b]): return None
        env = lambda i: {as_: i, as_ + "_t": i / (len(run) - 1)}
        f = _fold(run, as_, top=True)
        if f is not None and all(_same(f, c, env(i)) for i, c in enumerate(run)): return f
        if not grid or len(run) < 4: return None
        for m in range(2, len(run) - 1):
            f = _fold(run, as_, None, m, top=True)
            if f is not None and all(_same(f, c, env(i)) for i, c in enumerate(run)): return f
        return None
    n = len(cs)
    best = [(0, None)] * (n + 1)   # (from copy a on: the fewest parts, and where the first piece ends with its fold)
    for a in range(n - 1, -1, -1):
        best[a] = (best[a + 1][0] + 1, (a + 1, None))
        for b in range(n, a + 1, -1):   # (the longest first, so a tie keeps the longer run)
            if best[b][0] + 1 < best[a][0]:
                f = fold(a, b)
                if f is not None: best[a] = (best[b][0] + 1, (b, f))
    out, a, k = [], 0, 0
    while a < n:
        b, f = best[a][1]
        if f is None: out.append(cs[a])
        else:
            k += 1
            out.append({"id": id_ if k == 1 else f"{id_} {k}", "each": b - a if as_ == "i" else {"n": b - a, "as": as_}, **f})
        a = b
    return out


def merge(parts):
    """parts the same but for where they stand (`at`) as ONE part with a list of placements -- a wall's piers at its
    front and its back, a wing and its mirror twin's runs. Each keeps the first one's id and place in the list."""
    out, seen = [], {}
    for p in parts:
        if not p: continue
        if "at" not in p or any(k in p for k in ("along", "around", "parts")): out.append(p); continue
        key = json.dumps(r3({k: v for k, v in p.items() if k not in ("id", "at")}), sort_keys=True)
        at = p["at"] if p["at"] and isinstance(p["at"][0], list) else [p["at"]]
        if key in seen: seen[key]["at"] += at; continue
        q = {**p, "at": list(at)}; seen[key] = q; out.append(q)
    for q in out:
        if "at" in q and isinstance(q["at"], list) and len(q["at"]) == 1 and isinstance(q["at"][0], list): q["at"] = q["at"][0]
    return out


# (an axle along z: a part turned so its y runs across -- a wheel's lathe, a drum)
def across(x, y, z=0, roll=0):
    return [x, y, z, 0, 90, roll]


def arc(cx, cy, r, a0, a1, n=12):
    """points of a circle's arc in the xy plane, degrees -- a wheel arch's outline, a door's top"""
    return [[cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))] for i in range(n + 1)]



# ==== SHARED HELPERS (promoted 2026-11-20 from the group generators, where each was first written: see docs/modern.md
# "Reusable parts") ==================================================================================================
# ---- THE LOFT, EVALUATED IN PYTHON (the same sums as items.js `loft`) --------------------------------------------
def _st(s):
    return [s[0], s[1], s[2], s[3], s[4] if len(s) > 4 else s[1]]


def station_at(stations, x):
    """the loft's section values at x: [x, hw, y0, y1, tw], Catmull-Rom through the stations in the span's own t"""
    St = [_st(s) for s in stations]
    i = 0
    while i < len(St) - 2 and x > St[i + 1][0]: i += 1
    t = (x - St[i][0]) / max(1e-9, St[i + 1][0] - St[i][0])
    g = lambda j: St[max(0, min(len(St) - 1, j))]
    a, b, c, d = g(i - 1), g(i), g(i + 1), g(i + 2)
    cr = lambda k: b[k] + .5 * t * (c[k] - a[k] + t * (2 * a[k] - 5 * b[k] + 4 * c[k] - d[k] + t * (3 * (b[k] - c[k]) + d[k] - a[k])))
    return [x, max(.002, cr(1)), cr(2), cr(3), max(.002, cr(4))]


def section_half(s, rnd, m=24):
    """the right half of a section, [(y, z)], from the bottom's middle round to the top's middle (m samples a corner)"""
    _, hw, y0, y1, tw = s
    R = rnd if isinstance(rnd, (list, tuple)) else [rnd, rnd]
    hgt = y1 - y0
    rb, rt = min(R[0], hw * .98, hgt * .49), min(R[1], tw * .98, hgt * .49)
    out = [(y0, 0.0)]
    for k in range(m + 1):
        a = -math.pi / 2 + k / m * math.pi / 2
        out.append((y0 + rb + math.sin(a) * rb, hw - rb + math.cos(a) * rb))
    for k in range(m + 1):
        a = k / m * math.pi / 2
        out.append((y1 - rt + math.sin(a) * rt, tw - rt + math.cos(a) * rt))
    out.append((y1, 0.0))
    return out


def section_poly(s, rnd, m=6):
    """the whole section as an outline [(z, y)] for a plate (an end wall, a bulkhead): round from the bottom's middle"""
    h = section_half(s, rnd, m)
    right = [(z, y) for y, z in h]
    left = [(-z, y) for y, z in reversed(h[1:-1])]
    return right + left


def _half_point(s, rnd, u):
    """the point a share u (0 bottom middle .. 1 top middle) of the way round the right half, by length"""
    h = section_half(s, rnd)
    L = [0.0]
    for k in range(1, len(h)): L.append(L[-1] + math.hypot(h[k][0] - h[k - 1][0], h[k][1] - h[k - 1][1]))
    want = u * L[-1]
    for k in range(1, len(h)):
        if L[k] >= want:
            f = (want - L[k - 1]) / max(1e-9, L[k] - L[k - 1])
            return h[k - 1][0] + (h[k][0] - h[k - 1][0]) * f, h[k - 1][1] + (h[k][1] - h[k - 1][1]) * f
    return h[-1]


def _u_for(stations, rnd, x, y=None, z=None):
    """the share round the half at which the side reaches height y (going up), or the top comes in to z"""
    s = station_at(stations, x)
    lo, hi = 0.0, 1.0
    if y is not None:
        for _ in range(40):
            mid = (lo + hi) / 2
            if _half_point(s, rnd, mid)[0] < y: lo = mid
            else: hi = mid
        return lo
    lo = 0.5
    for _ in range(40):   # (over the top: z falls from the side to the middle)
        mid = (lo + hi) / 2
        py, pz = _half_point(s, rnd, mid)
        if pz > z and py > (s[2] + s[3]) / 2: lo = mid
        else: hi = mid
    return lo


def loft_eval(stations, rnd, x, u):
    """a point of the loft's surface: x along, u round the right half (0 the bottom's middle, 1 the top's)"""
    py, pz = _half_point(station_at(stations, x), rnd, u)
    return [x, py, pz]


def _sub(a, b): return [a[i] - b[i] for i in range(3)]
def _cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def _dot(a, b): return sum(a[i] * b[i] for i in range(3))
def _norm(a):
    l = math.sqrt(_dot(a, a)) or 1
    return [v / l for v in a]


def euler(xa, ya, za):
    """the yaw, pitch, roll (degrees, items.js: R = Ry Rx Rz) that turn a part's x, y, z axes onto xa, ya, za"""
    R = [[xa[r], ya[r], za[r]] for r in range(3)]
    b = math.asin(max(-1, min(1, -R[1][2])))
    c = math.atan2(R[1][0], R[1][1])
    a = math.atan2(R[0][2], R[2][2])
    return [math.degrees(a), math.degrees(b), math.degrees(c)]


def on_loft(stations, rnd, x, y=None, z=None, off=0.012, left=False):
    """the `at` that lays a thin box flat on a loft's surface: its x the surface's outward normal, its y up the surface
    (round the section), its z along the body (-x). Give the side's height `y`, or `z` on the top (a windscreen).
    The box is then [thickness, height round the body, length along it]. `left`: the -z side's (mirror it instead)."""
    u = _u_for(stations, rnd, x, y=y, z=z)
    P = loft_eval(stations, rnd, x, u)
    du, dx = 0.002, 0.01
    Tu = _norm(_sub(loft_eval(stations, rnd, x, min(1, u + du)), loft_eval(stations, rnd, x, max(0, u - du))))
    Tx = _sub(loft_eval(stations, rnd, x + dx, u), loft_eval(stations, rnd, x - dx, u))
    n = _norm(_cross(Tx, Tu))
    s = station_at(stations, x)
    if _dot(n, _sub(P, [x, (s[2] + s[3]) / 2, 0])) < 0: n = [-v for v in n]
    ya = _norm(_sub(Tu, [n[i] * _dot(Tu, n) for i in range(3)]))
    za = _cross(n, ya)
    yaw, pitch, roll = euler(n, ya, za)
    p = [P[i] + n[i] * off for i in range(3)]
    if left: return [p[0], p[1], -p[2], *euler([n[0], n[1], -n[2]], [ya[0], ya[1], -ya[2]], [-za[0], -za[1], za[2]])]
    return [p[0], p[1], p[2], yaw, pitch, roll]


def cr_at(st, x):
    """a loft's section at x as (hw, y0, y1, tw) -- station_at without its x"""
    return tuple(station_at(st, x)[1:])


def shell_over(st, xs, grow=0.012):
    """stations for a loft lying just OUTSIDE another (`st`) between the xs given: the roof over the glasshouse"""
    out = []
    for x in xs:
        hw, y0, y1, tw = cr_at(st, x)
        out.append([x, hw + grow, y0, y1 + grow, tw + grow])
    return out


def loft_z(st, round_, x, y):
    """z of a loft's right side at (x, y) -- on its flat side, or round its corners: where to set a handle, a seam,
    a lamp on the body's surface"""
    hw, y0, y1, tw = cr_at(st, x)
    R = round_ if isinstance(round_, (list, tuple)) else [round_, round_]
    rb, rt = min(R[0], hw * .98, (y1 - y0) * .49), min(R[1], tw * .98, (y1 - y0) * .49)
    ya, yb = y0 + rb, y1 - rt
    if y < ya: return hw - rb + math.sqrt(max(0, rb * rb - (ya - y) ** 2))
    if y > yb: return tw - rt + math.sqrt(max(0, rt * rt - (y - yb) ** 2))
    return hw + (tw - hw) * (y - ya) / max(1e-9, yb - ya)


# ---- small assemblies ----------------------------------------------------------------------------------------------
def tube(id_, mat, prof, x0, y=0, z=0, sides=16, **k):
    """a round thing along +x: a lathe profile [[r, dx], ...] from x0 forward (roll -90 turns the lathe's y onto +x)"""
    return lathe(id_, mat, prof, [x0, y, z, 0, 0, -90], sides=sides, **k)



def ram(id_, a, b, r, frac=0.56, barrel="paint", piston="chrome", **k):
    """A HYDRAULIC CYLINDER from a to b: the barrel (r) from a, its piston rod (r * 0.5, chrome) out of it to b, an eye
    at each end -- a boom's, a blade's, a tipper's, a fork's tilt"""
    m = [a[i] + (b[i] - a[i]) * frac for i in range(3)]
    m2 = [a[i] + (b[i] - a[i]) * (frac - 0.06) for i in range(3)]
    return [rod(id_ + "Barrel", barrel, r, a, m, 10, **k), rod(id_ + "Rod", piston, r * 0.5, m2, b, 8, **k),
            rod(id_ + "Gland", barrel, r * 1.15, m2, m, 10, **k)]



def handrail(id_, mat, x0, x1, y, z, posts=4, post_h=1.0, r=0.02, **k):
    """a rail along x at height y over z on its posts (a walkway's, a gangway's), both sides if mirror='z'"""
    return [rod(id_, mat, r, [x0, y, z], [x1, y, z], 6, **k),
            rod(id_ + "Post", mat, r, [0, y - post_h, z], [0, y, z], 6, along={"n": posts, "from": [x0, 0, 0], "to": [x1, 0, 0]}, **k)]



def catalogue(groups_named):
    """the catalogue's "Modern: ..." categories, rewritten from what was written this run (others left as they are)"""
    p = os.path.join(ROOT, "assets", "index.json")
    lock = open(p + ".lock", "w"); fcntl.flock(lock, fcntl.LOCK_EX)   # (generators run side by side: one writer at a time)
    idx = json.load(open(p))
    cats = idx["categories"]
    for group, title in groups_named.items():
        paths = sorted(set(WRITTEN.get(group, [])))
        if not paths: continue
        name = "Modern: " + title
        old = next((c for c in cats if c["name"] == name), None)
        if old:   # (what other modules wrote to the same group stays, as long as its file does)
            keep = [q for q in old["paths"] if os.path.exists(os.path.join(ROOT, "assets", q + ".json"))]
            old["paths"] = sorted(set(keep) | set(paths))
        else:
            at = max(i for i, c in enumerate(cats) if c["name"].startswith(("Items:", "Modern:"))) + 1
            cats.insert(at, {"name": name, "kind": "item", "paths": paths})
    with open(p, "w") as f:
        json.dump(idx, f, indent=2, ensure_ascii=False)
        f.write("\n")
    fcntl.flock(lock, fcntl.LOCK_UN)


# ---- WHEEL ARCHES AND FLOOR PANS (2026-11-22, the road vehicles' undersides) ------------------------------------------
def body_arches(xs, r, gap=0.06):
    """a loft's `arches` for road wheels of radius r at each x: notches gap clear of the tyre"""
    return [[x, r, r + gap] for x in xs]


def arches(xs, r, z, track, mat="trim", inner=None, lip=0.13, gap=0.03, cup=False, skin=None, low=None, floor=None, notch=None, deep=0.05):
    """the wheel arches: a dark lip round each notch the body's loft cuts (its `arches`), and the wheelhouse behind it,
    the wheel turning in it; `inner` where the house stops (a bus's: before its aisle; a car's runs across); `cup`: a
    closed tub, its inner wall a disc.
    - `skin` (z of the body's side at x, y) lays the lip ON the body, following its tumblehome, as a band `deep` thick
      reaching in (an arch liner's edge: no gap between it and the house to look into the body through); `low` (the
      body's bottom at x) runs it down to where the notch (`notch`, r + .06) meets the bottom at both ends. Without them
      the lip is a flat plate at z, to a little below the axle.
    - `floor` (a height, or one at x: the floor pan's underside) keeps the house above it: an arc, open below as a real
      wheelhouse is, not a drum round the whole tyre hanging to the ground."""
    out = []
    Rn, Rt = notch or r + 0.06, r + 0.05
    for i, x in enumerate(xs):
        inner_i = inner[i] if isinstance(inner, (list, tuple)) else inner   # (one per x: a steered axle's tubs reach further in)
        zin = -0.02 if inner_i is None else inner_i
        if skin is None:   # (the lip runs only a little below the axle's height: lower, its ends hung below the sill as black tabs)
            A = [-6 + 192 * k / 16 for k in range(17)]
            outer = [[x + (r + lip) * math.cos(math.radians(a)), r + (r + lip) * math.sin(math.radians(a))] for a in A]
            inner_ = [[x + (r + gap) * math.cos(math.radians(a)), r + (r + gap) * math.sin(math.radians(a))] for a in reversed(A)]
            out.append(plate(f"arch{i}", mat, outer + inner_, 0.03, [0, 0, z], mirror="z"))
        else:
            end = lambda xe: math.degrees(math.asin(max(-1.0, min(1.0, ((low(xe) if low else r) - r) / Rn))))
            a0, a1 = end(x + Rn), 180 - end(x - Rn)
            rm = r + (gap + lip) / 2
            pts = []
            for k in range(17):
                a = math.radians(a0 + (a1 - a0) * k / 16)
                px, py = x + rm * math.cos(a), r + rm * math.sin(a)
                pts.append([round(px, 4), round(py, 4), round(skin(px, py) + 0.012 - deep / 2, 4)])
            out.append(sweep(f"arch{i}", mat, pts, section=[lip - gap, deep], up=[0, 0, 1], seg=2, mirror="z"))
        prof = [[Rt, zin], [Rt, track / 2 - 0.25 if inner_i is None else z - 0.03]]
        if inner_i is not None and cup: prof = [[0, zin]] + prof   # (stopping short of the middle: a closed tub, its inner wall a disc)
        k = {}
        if floor is not None:   # (the lathe's angle a lies at -a in the vehicle's x-y plane: keep -a in [t0, 180 - t0])
            fy = floor(x) if callable(floor) else floor
            t0 = math.degrees(math.asin(max(-1.0, min(1.0, (fy - r) / Rt))))
            k["arc"] = [round(t0 - 180, 3), round(-t0, 3)]
        if floor is not None and prof[0][0] == 0:   # (an arc's cup: its wall only the circle's segment above the floor --
            prof = prof[1:]                           #  a lathe's disc would be a pie reaching down to the hub, a dark
            T = [math.radians(t0 + (180 - 2 * t0) * j / 16) for j in range(17)]   # wedge seen through the wheel)
            out.append(plate(f"tub{i}", "well", [[round(x + Rt * math.cos(a), 4), round(r + Rt * math.sin(a), 4)] for a in T], 0.006, [0, 0, zin], mirror="z"))
        out.append(lathe(f"house{i}", "well", prof, [x, r, 0, 0, 90, 0], caps=False, double=True, sides=20, mirror="z", **k))
    return out


def steer_in(track, r, w, lock=35, gap=0.03):
    """the z of a STEERED wheel's tub's inner wall (arches `inner`, pan `zin`): at full lock the tyre's leading or
    trailing edge, r out from the upright through its centre, swings in by r sin(lock), its inner face by w/2 cos(lock)
    -- `gap` clear of both"""
    a = math.radians(lock)
    return track / 2 - (w / 2 * math.cos(a) + r * math.sin(a)) - gap


def arch_gap(x, r, floor):
    """the stretch [a, b] of x a floor pan leaves open round a wheel's house (arches(..., floor)): as long as the house
    is at the floor, a centimetre under its edge"""
    Rt = r + 0.05
    h = Rt * math.cos(math.asin(max(-1.0, min(1.0, (floor - r) / Rt)))) - 0.01
    return (x - h, x + h)


def pan(id_, mat, st, rnd, x0, x1, gaps=(), zin=None, lift=0.004, t=0.02, inset=0.004):
    """a FLOOR PAN under a loft that is open below (`bare` bottom), following the body's bottom `lift` above it, its
    sides `inset` inside the skin at its own underside (so it closes the opening the bottom's rounded corners leave,
    no strip of the body's inside showing past it), from x0 to x1. Round the wheels it is open: a loft's flat face is
    one quad from the middle out, so a hole cannot take only its outer part -- the pan is a middle strip to `zin` (the
    tubs' inner walls) all the way, 3 mm up, and full-width pieces between the `gaps` (arch_gap)."""
    def strip(i, a, b, half=None, up=0.0):
        n = max(2, round((b - a) / 0.25))
        S = []
        for k in range(n + 1):
            x = a + (b - a) * k / n
            y0 = cr_at(st, x)[1] + lift + up
            zz = loft_z(st, rnd, x, y0 - up) - inset
            if half is not None: zz = min(zz, half)
            S.append([round(x, 4), round(zz, 4), round(y0, 4), round(y0 + t, 4), round(zz, 4)])
        return loft(i, mat, S, 0.006, seg=1)
    if not gaps: return [strip(id_, x0, x1)]
    if isinstance(zin, (list, tuple)):   # (one per gap, as `gaps` are given: a steered axle's tubs reach further in --
        zs = dict(zip(gaps, zin))          #  the middle strip in pieces, each gap's its own, between them the narrowest)
        cuts = sorted(gaps); edges = sorted({x0, x1, *[v for g in cuts for v in g if x0 < v < x1]})
        out = [strip(f"{id_}m{k}" if k else id_, a, b, next((zs[g] for g in cuts if g[0] <= a and b <= g[1]), min(zin)) - 0.005, 0.003)
               for k, (a, b) in enumerate(zip(edges, edges[1:]))]
    else:
        cuts, out = sorted(gaps), [strip(id_, x0, x1, zin - 0.005, 0.003)]
    a = x0
    for k, (ga, gb) in enumerate(cuts + [(x1, x1)]):
        if ga - a > 0.02: out.append(strip(f"{id_}{k}", a, ga))
        a = gb
    return out


# ==== WINDOWS (2026-11-22): one family for every row of panes, the posts or mullions between them, and the walls and
# lofts they are cut into (were infra.win_wall, sea.windows, vehicles.panes / window_posts and inline loops).
# A row's LAYOUT is a list of spans [(a, b)] along a face (`fill`, `spaced`); the FACE is a plane: axis "x" (the plane
# x = c, the row running along z) or "z" (z = c, the row along x). What is laid on it is boxes, folded into `each` runs.
def fill(u0, u1, pane=1.35, post=0.12, n=None):
    """panes FILLING u0..u1 with a `post` between each two (none at the ends): `n` of them, or as many about `pane`
    long as fit -- a bus's side, a shelter's back, a curtain wall's bays (post 0) -> [(a, b)]"""
    n = n or max(1, round((u1 - u0 + post) / (pane + post)))
    p = (u1 - u0 - post * (n - 1)) / n
    return [(u0 + k * (p + post), u0 + k * (p + post) + p) for k in range(n)]


def spaced(u0, u1, n, w, ends=False):
    """n openings `w` wide SPACED evenly: each in the middle of one of n equal cells of u0..u1 (a carriage's windows,
    a facade's bays), or, `ends`, their middles running from u0 to u1 (a ship's rows of windows) -> [(a, b)]"""
    cs = [u0 + (u1 - u0) * ((k / (n - 1) if n > 1 else 0.5) if ends else (k + 0.5) / n) for k in range(n)]
    return [(c - w / 2, c + w / 2) for c in cs]


def window_holes(sp, y0, y1, side="both"):
    """a loft's `holes` for a row of windows: each span from y0 to y1 (on both sides, or "left" / "right")"""
    return [hole(a, b, y0, y1, side) for a, b in sp]


def face_box(id_, mat, axis, c, ur, yr, t, off=0.0, **k):
    """a box on a face by its extents there: ur (u0, u1) along the face, yr (y0, y1) up it, `t` thick about c + off"""
    um, ym, du, dy = (ur[0] + ur[1]) / 2, (yr[0] + yr[1]) / 2, abs(ur[1] - ur[0]), abs(yr[1] - yr[0])
    if axis == "x": return box(id_, mat, [t, dy, du], [c + off, ym, um], **k)
    return box(id_, mat, [du, dy, t], [um, ym, c + off], **k)


def panes(id_, mat, axis, c, sp, rows, t=0.02, over=0.0, off=0.0, **k):
    """PANES: a box on the face over every span of `sp` in every row of `rows` ([(y0, y1), ..] or one (y0, y1)), each
    `over` wider than its span at both ends -- a row of panes, a deckhouse's grid of windows, the sills and heads over
    a carriage's windows, a curtain wall's transoms (one span, a row a transom). `k`: mirror, when.. Row by row, folded
    into `each` runs (a grid folds whole)."""
    if rows and not isinstance(rows[0], (list, tuple)): rows = [rows]
    cs = [face_box(f"{id_}{j}", mat, axis, c, (a - over, b + over), yr, t, off, **k) for j, (yr, (a, b)) in enumerate((yr, s) for yr in rows for s in sp)]
    if len(cs) == 1: cs[0]["id"] = id_
    return runs(id_, cs)


def bars(id_, mat, axis, c, sp, y0, y1, t=0.012, w=None, over=0.0, gap=None, ends=False, off=0.0, **k):
    """the POSTS (mullions) between a row's spans, y0 to y1: over each gap between neighbours, `over` wider at both
    sides (a bus's black panels over its window posts) -- or, `w` given, a bar that wide on the gap's middle (a
    shelter's posts, a curtain wall's mullions). `gap`: only gaps narrower (not a bus's door); `ends`: one more beyond
    each end of the row, as if it went on (its gap as wide as the next one in). Folded into `each` runs."""
    xs = sorted(sp)
    gs = [(xs[j][1], xs[j + 1][0]) for j in range(len(xs) - 1)]
    if ends:
        g0, g1 = (gs[0][1] - gs[0][0], gs[-1][1] - gs[-1][0]) if gs else (0.0, 0.0)
        gs = [(xs[0][0] - g0, xs[0][0])] + gs + [(xs[-1][1], xs[-1][1] + g1)]
    if gap is not None: gs = [g for g in gs if g[1] - g[0] < gap]
    ur = (lambda a, b: ((a + b - w) / 2, (a + b + w) / 2)) if w is not None else (lambda a, b: (a - over, b + over))
    cs = [face_box(f"{id_}{j}", mat, axis, c, ur(a, b), (y0, y1), t, off, **k) for j, (a, b) in enumerate(gs)]
    if len(cs) == 1: cs[0]["id"] = id_
    return runs(id_, cs)


def window_wall(id_, axis, c, t, u0, u1, y0, y1, rows, ncol, frac=0.6, mat="wall", glaze="glazing", mull=None):
    """a WALL WITH WINDOWS on the face (axis, c), u0..u1 along it, y0..y1 up, `t` thick: `rows` [(sill, head, glazed,
    open_cols or None)] each cut by `ncol` windows `frac` of a cell wide (open_cols: only those columns -- a door's
    column stays solid); solid courses between the rows, piers round each window (each kind a run along the wall,
    split where a solid column breaks it), a `mull` (material) bar half the wall thick up each window's middle, and
    one `glaze` pane a row, 3 cm thick in the wall's middle (hidden in the piers, seen in the openings)"""
    B = lambda nm, m, ur, yr, tt=t: face_box(nm, m, axis, c, ur, yr, tt)
    out, y, cell = [], y0, (u1 - u0) / ncol
    for r, (s, h, gl, cols) in enumerate(rows):
        if s > y + 1e-6: out.append(B(f"{id_}B{r}", mat, [u0, u1], [y, s]))
        m = cell * (1 - frac) / 2
        run = {"S": [], "Pa": [], "Pb": [], "M": []}   # (each kind a run along the wall: one part laid by `each`)
        for i in range(ncol):
            a, b = u0 + cell * i, u0 + cell * (i + 1)
            if cols is not None and i not in cols: run["S"].append((i, B(f"{id_}S{r}_{i}", mat, [a, b], [s, h]))); continue
            if m > 0.01: run["Pa"].append((i, B(f"{id_}P{r}_{i}a", mat, [a, a + m], [s, h]))); run["Pb"].append((i, B(f"{id_}P{r}_{i}b", mat, [b - m, b], [s, h])))
            if mull: run["M"].append((i, B(f"{id_}M{r}_{i}", mull, [(a + b) / 2 - 0.04, (a + b) / 2 + 0.04], [s, h], tt=t * 0.5)))
        for kd, ps in run.items():   # (split where a door's column breaks the run -- unless the rest still step evenly)
            whole = each(f"{id_}{kd}{r}", [q for _, q in ps])
            if len(whole) == 1: out += whole; continue
            while ps:
                n = next((j for j in range(1, len(ps)) if ps[j][0] != ps[j - 1][0] + 1), len(ps))
                out += each(f"{id_}{kd}{r}" + (f"_{ps[0][0]}" if n < ncol else ""), [q for _, q in ps[:n]]); ps = ps[n:]
        if gl: out.append(B(f"{id_}G{r}", glaze, [u0, u1], [s, h], tt=0.03))
        y = h
    if y1 > y + 1e-6: out.append(B(f"{id_}T", mat, [u0, u1], [y, y1]))
    return out
