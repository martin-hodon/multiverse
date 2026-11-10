# dlib.py (2026-11-09): helpers for THE DOZEN -- twelve species derived from the ones already in assets/creatures/
# (donkey from the horse, goat from the ibex, otter and meerkat from the weasel, mammoth from the elephant, velociraptor
# from the dilophosaurus, llama from the camel, koala from the giant panda, tapir from the pig, warthog from the boar,
# water buffalo from the ox, sea turtle from the turtle). Each species' script loads its base, SCALES it as a whole
# (every length in metres: the rig's fields and the sculpt's shapes), reshapes and recolours by shape id, and writes the
# new file whole (giants/lib.py save: one shape a line); nothing patches it after, so re-running reproduces it.
#
#   from dlib import *
#   d = load("mammals/horse"); scale_def(d, .82); d["name"] = "donkey"; ...; save("mammals/donkey", d); index_add("creatures/mammals/donkey", "Mammals")
#
# Rendering a species to look at it: render("creatures/mammals/donkey", "donkey", views=("side", "front", "q", "rear", "head")) --
# cshot.py (this folder) opens assets.html headless (one browser at a time on this PC: a lock), waits for the sculpted
# body, frames each view from the asset's box, and writes <out>/<name>_<view>.png.
import json, os, sys, copy, math, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "giants"))
from lib import save as _save, rnd   # noqa: E402
REPO = "/home/martin/store/apps/multiverse/"
R = REPO + "assets/creatures/"

def load(path):
    """a species as it is now (path under assets/creatures, no extension)"""
    return json.load(open(R + path + ".json"))

def save(path, d):
    d = copy.deepcopy(d)
    for k in list(d):
        if k.startswith("_") and k not in ("_about", "_coats", "_variants", "_params"): del d[k]
    _save(path, d)
    print("wrote", R + path + ".json")

# ---- scaling: every length in the file multiplied by f (angles, shares, counts, colours left) -----------------------
def _mul(v, f):
    if isinstance(v, (int, float)) and not isinstance(v, bool): return v * f
    if isinstance(v, list): return [_mul(x, f) for x in v]
    return v   # (an expression string over the params: the frame scales it by `s`)
def _pts(pts, f, n=4):
    """points [x, y, z, r, (aspect...)]: the first n entries lengths"""
    return [[(p[i] * f if i < n and isinstance(p[i], (int, float)) else p[i]) for i in range(len(p))] for p in pts]
RIG_LISTS = ("rear", "front", "neck", "head", "muzzle", "nose", "ears", "eyes")
def scale_rig(d, f):
    for k in RIG_LISTS:
        v = d.get(k)
        if isinstance(v, dict) and "v" in v: v["v"] = _mul(v["v"], f)
        elif v is not None: d[k] = _mul(v, f)
    L = d.get("legs")
    if isinstance(L, dict):
        for k in ("front", "hind", "radii", "foot", "toe", "ankle"):
            if k in L: L[k] = _mul(L[k], f)
        if isinstance(L.get("toes"), dict):
            for k in ("len", "r"):
                if k in L["toes"]: L["toes"][k] = _mul(L["toes"][k], f)
    T = d.get("tail")
    if isinstance(T, dict):
        for k in ("c", "R", "r1", "r2", "tuft", "z", "zEnd"):
            if k in T: T[k] = _mul(T[k], f)
    for e in d.get("extras", []) or []:
        for k in ("from", "to", "r1", "r2", "ell", "at", "r"):
            if k in e: e[k] = _mul(e[k], f)
        if isinstance(e.get("arc"), dict):
            for k in ("c", "R", "r1", "r2", "z", "zEnd"):
                if k in e["arc"]: e["arc"][k] = _mul(e["arc"][k], f)
    if isinstance(d.get("gaits"), dict):
        for g in d["gaits"].values():
            if isinstance(g, dict):
                for k in ("stride", "lift", "bob"):
                    if k in g: g[k] = _mul(g[k], f)
    if isinstance(d.get("k"), dict): d["k"] = {k: _mul(v, f) for k, v in d["k"].items()}
    if isinstance(d.get("mount"), dict) and "h" in d["mount"]: d["mount"]["h"] = _mul(d["mount"]["h"], f)
    if isinstance(d.get("saddle"), dict): d["saddle"] = {k: _mul(v, f) for k, v in d["saddle"].items()}
    if "waist" in d: d["waist"] = _mul(d["waist"], f)
    # a "parts" rig (the turtle): pos, size, pivot, len
    for p in d.get("parts", []) or []:
        for k in ("pos", "pivot"):
            if k in p: p[k] = _mul(p[k], f)
        if isinstance(p.get("size"), dict): p["size"] = {k: _mul(v, f) for k, v in p["size"].items()}
        if isinstance(p.get("anim"), dict):
            for k in ("dy", "amp"):
                if k in p["anim"]: p["anim"][k] = _mul(p["anim"][k], f)

def scale_shape(s, f):
    t = s.get("type", "ell")
    for k in ("c", "r", "k", "kc", "round", "a", "b", "ra", "rb", "thick", "rim", "innerRim", "len", "gap", "bury", "at"):   # (not rowLen: a share)
        if k in s and k != "at" or (k == "at" and t == "whiskers"): s[k] = _mul(s[k], f)
    if t in ("tube", "sweep", "horn", "membrane") and "pts" in s: s["pts"] = _pts(s["pts"], f)
    if t == "fin":
        if "root" in s: s["root"] = _pts(s["root"], f, 3)
        if "edge" in s: s["edge"] = _pts(s["edge"], f, 3)
        if "swell" in s and isinstance(s["swell"], list): s["swell"] = [s["swell"][0] * f, s["swell"][1] * f] + s["swell"][2:]
    if "fair" in s: s["fair"] = _mul(s["fair"], f) if not isinstance(s["fair"], dict) else {k: (_mul(v, f) if k == "r" else v) for k, v in s["fair"].items()}
    if isinstance(s.get("lumps"), dict) and "size" in s["lumps"]: s["lumps"]["size"] = _mul(s["lumps"]["size"], f)
    if isinstance(s.get("frame"), dict):
        for k in ("o", "r"):
            if k in s["frame"]: s["frame"][k] = _mul(s["frame"][k], f)
    if t == "membrane" and "r" in s: s["r"] = _mul(s["r"], f)

def scale_sculpt(sc, f):
    for s in sc.get("shape", []): scale_shape(s, f)
    e = sc.get("eyes")
    if isinstance(e, dict):
        for k in ("at", "from", "r"):
            if k in e: e[k] = _mul(e[k], f)
    if isinstance(sc.get("mesh"), dict) and "cell" in sc["mesh"]: sc["mesh"]["cell"] = sc["mesh"]["cell"] * f
    sh = sc.get("shade")
    if isinstance(sh, dict):
        for k in ("at", "lowAt"):
            if k in sh: sh[k] = sh[k] * f

def scale_def(d, f):
    """the whole definition at f of its size (uniform). A frame-based species (`use` + params.s): set params.s yourself
    for the rig and call scale_sculpt(d["sculpt"], f) -- scale_rig would double it"""
    if f == 1: return d
    if d.get("use"): scale_sculpt(d["sculpt"], f)
    else:
        scale_rig(d, f)
        if "sculpt" in d: scale_sculpt(d["sculpt"], f)
    for v in (d.get("variants") or {}).values():
        if isinstance(v.get("sculpt"), dict): scale_sculpt(v["sculpt"], f)
    return d

def stretch(d, fx=1.0, fy=1.0, fz=1.0, about=None):
    """an ANISOTROPIC stretch of the sculpt only (small amounts: rotated shapes keep their rotation, so only their
    centres and the aligned radii move truly) -- the rig fields are not touched: do those by hand"""
    o = about or [0, 0, 0]
    def P(p, n=3):
        q = list(p); 
        for i, f in enumerate((fx, fy, fz)):
            if i < n and isinstance(q[i], (int, float)): q[i] = o[i] + (q[i] - o[i]) * f
        return q
    def RR(r):
        if isinstance(r, list): return [r[0] * fx, r[1] * fy, r[2] * fz]
        return r * (fx * fy * fz) ** (1 / 3)
    for s in d["sculpt"].get("shape", []):
        for k in ("c", "a", "b"):
            if k in s and isinstance(s[k], list) and len(s[k]) >= 3 and isinstance(s[k][0], (int, float)): s[k] = P(s[k])
        if "r" in s and s.get("type") in ("ell", "box") and isinstance(s["r"], list) and not s.get("rot") and not s.get("axes"): s["r"] = RR(s["r"])
        if "pts" in s: s["pts"] = [P(p, 3) for p in s["pts"]]
        if "root" in s: s["root"] = [P(p) for p in s["root"]]
        if "edge" in s: s["edge"] = [P(p) for p in s["edge"]]
        if s.get("type") == "whiskers" and "at" in s: s["at"] = P(s["at"])
    e = d["sculpt"].get("eyes")
    if e:
        for k in ("at", "from"): e[k] = P(e[k])
    return d

# ---- shapes by id -------------------------------------------------------------------------------------------------
def shapes(d): return d["sculpt"]["shape"]
def shape(d, id):
    for s in shapes(d):
        if s.get("id") == id: return s
    raise KeyError(id)
def has(d, id): return any(s.get("id") == id for s in shapes(d))
def ids(d, pat=None):
    import re
    return [s.get("id") for s in shapes(d) if pat is None or re.search(pat, s.get("id", ""))]
def drop(d, *ids_):
    import re
    gone = set()
    for pat in ids_:
        for s in shapes(d):
            if s.get("id") == pat or (pat.startswith("^") and re.search(pat, s.get("id", ""))): gone.add(s.get("id"))
    d["sculpt"]["shape"] = [s for s in shapes(d) if s.get("id") not in gone]
    return sorted(gone)
def over(d, id, **fields):
    """fields written over shape `id` (a value None removes the key)"""
    s = shape(d, id)
    for k, v in fields.items():
        if v is None: s.pop(k, None)
        else: s[k] = v
    return s
def add(d, s, after=None):
    """a new shape, at the end or right after shape `after`"""
    sh = shapes(d)
    if after is None: sh.append(s); return s
    i = next(i for i, x in enumerate(sh) if x.get("id") == after)
    sh.insert(i + 1, s); return s
def move(d, id, dx=0, dy=0, dz=0):
    s = shape(d, id); v = [dx, dy, dz]
    for k in ("c", "a", "b"):
        if k in s and isinstance(s[k], list) and isinstance(s[k][0], (int, float)): s[k] = [s[k][i] + v[i] for i in range(3)]
    if "pts" in s: s["pts"] = [[p[i] + v[i] if i < 3 else p[i] for i in range(len(p))] for p in s["pts"]]
    for k in ("root", "edge"):
        if k in s: s[k] = [[p[i] + v[i] if i < 3 else p[i] for i in range(len(p))] for p in s[k]]
    if s.get("type") == "whiskers" and "at" in s: s["at"] = [s["at"][i] + v[i] for i in range(3)]
    return s
def move_all(d, pat, dx=0, dy=0, dz=0):
    import re
    for i in ids(d, pat): move(d, i, dx, dy, dz)
def grow(d, id, fx=1.0, fy=None, fz=None):
    """an ell's/box's radii scaled (fy, fz default fx); a sphere's/tube's/cone's radii by fx"""
    s = shape(d, id); fy = fx if fy is None else fy; fz = fx if fz is None else fz
    if isinstance(s.get("r"), list): s["r"] = [s["r"][0] * fx, s["r"][1] * fy, s["r"][2] * fz]
    elif isinstance(s.get("r"), (int, float)): s["r"] *= fx
    if "pts" in s: s["pts"] = [[p[i] * fx if i == 3 else p[i] for i in range(len(p))] for p in s["pts"]]
    for k in ("ra", "rb"):
        if k in s: s[k] *= fx
    return s
def recolor(d, **colours):
    """the species' colour table (`c` or `colors`): names set (a value None removes one)"""
    key = "colors" if "colors" in d else "c"
    for k, v in colours.items():
        if v is None: d[key].pop(k, None)
        else: d[key][k] = v
    return d[key]
def colours(d): return d.get("colors") if "colors" in d else d.get("c")
def set_bone(d, pat, bone):
    for i in ids(d, pat): shape(d, i)["bone"] = bone

# ---- the catalogue ------------------------------------------------------------------------------------------------
def index_add(path, category):
    """the species listed in assets/index.json under `category` (Mammals, Dinosaurs, Others, Sea life), sorted in"""
    f = REPO + "assets/index.json"; txt = open(f).read()
    if '"%s"' % path in txt: return False
    d = json.loads(txt)
    cat = next(c for c in d["categories"] if c["name"] == category)
    names = sorted(cat["paths"] + [path])
    i = names.index(path)
    if i + 1 < len(names):
        a = '"%s"' % names[i + 1]
        assert txt.count(a) == 1, a
        txt = txt.replace(a, '"%s", %s' % (path, a) if "\n" not in txt[txt.index(a) - 12:txt.index(a)] else '"%s",\n        %s' % (path, a), 1)
    else:
        last = '"%s"' % cat["paths"][-1]
        assert txt.count(last) == 1, last
        txt = txt.replace(last, '%s, "%s"' % (last, path) if "\n" not in txt[txt.index(last) - 12:txt.index(last)] else '%s,\n        "%s"' % (last, path), 1)
    json.loads(txt)
    open(f, "w").write(txt)
    print("indexed", path, "under", category)
    return True

# ---- a look at it -------------------------------------------------------------------------------------------------
def render(path, name, views=("side", "front", "q", "rear", "head"), out=None, dress=None, extra=None):
    """screenshots of the species in assets.html (cshot.py: real GPU headless, one at a time): <out>/<name>_<view>.png.
    dress: {"coat": i} or {"variant": "nanny"}; extra: a list of {"js", "wait", "shot"} steps of your own after the views"""
    out = out or os.environ.get("DOZEN_SHOTS", os.path.join(HERE, "_shots"))
    os.makedirs(out, exist_ok=True)
    args = [sys.executable, os.path.join(HERE, "cshot.py"), path, name, out, ",".join(views)]
    if dress: args += ["--dress", json.dumps(dress)]
    if extra: args += ["--extra", json.dumps(extra)]
    r = subprocess.run(args, capture_output=True, text=True, timeout=3600)   # (the lock: other renders ahead)
    print(r.stdout[-4000:]); 
    if r.returncode: print(r.stderr[-3000:])
    return [os.path.join(out, f"{name}_{v}.png") for v in views]

# ---- a blade: a fin (an ear, a small fin) as a rounded leaf -- root centre rm, u along the root, v the blade's axis
# (unit vectors, root space), L its reach along v, W its half-width along u; the outline a rounded point or round
def fin_blade(rm, u, v, L, W, n=13, tipness=0.9, root_half=0.8):
    import math
    def nz(a): l = math.sqrt(sum(x * x for x in a)) or 1; return [x / l for x in a]
    u, v = nz(u), nz(v)
    P = lambda a, b: [round(rm[i] + u[i] * a + v[i] * b, 4) for i in range(3)]
    edge = []
    for k in range(n):
        t = math.pi * k / (n - 1)
        a = W * math.cos(t) * (1 - (1 - tipness) * math.sin(t)); b = L * math.sin(t)
        edge.append(P(a, b))
    root = [P(W * root_half, 0), P(0, 0), P(-W * root_half, 0)]
    return {"root": root, "edge": edge, "corners": [n // 2]}
