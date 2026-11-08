# shp.py: edit a species' sculpt.shape list in place (one shape a line, the rest of the file untouched), and the
# geometry for converting field shapes to the engine's sharp types (horn, fin)
import json, math, re, subprocess
REPO = "/home/martin/store/apps/multiverse/"
import os
SH = os.path.dirname(os.path.abspath(__file__)) + "/"   # (fd.mjs beside it; run from tools/creaturegen/sharp)

def path_of(sp): return REPO + "assets/creatures/" + sp + ".json"

def load(sp):
    txt = open(path_of(sp)).read(); d = json.loads(txt)
    return txt, d

def block(txt, n):
    """the line range of the sculpt shape list: (first shape line, end line exclusive, indent)"""
    L = txt.split("\n")
    for i, l in enumerate(L):
        if re.match(r'^\s*"shape": \[\s*$', l):
            j = i + 1
            while j < len(L) and not re.match(r'^\s*\],?\s*$', L[j]): j += 1
            if j - i - 1 == n: return L, i + 1, j
    raise RuntimeError("no one-line-a-shape block of %d" % n)

def save(sp, shapes, txt=None):
    if txt is None: txt = open(path_of(sp)).read()
    d = json.loads(txt); n = len(d["sculpt"]["shape"])
    L, a, b = block(txt, n)
    ind = re.match(r'^(\s*)', L[a]).group(1)
    new = [ind + json.dumps(s) + ("," if k < len(shapes) - 1 else "") for k, s in enumerate(shapes)]
    out = "\n".join(L[:a] + new + L[b:])
    json.loads(out)
    open(path_of(sp), "w").write(out)

def r5(v):
    if isinstance(v, float): return round(v, 4)
    if isinstance(v, list): return [r5(x) for x in v]
    if isinstance(v, dict): return {k: r5(x) for k, x in v.items()}
    return v

# vectors
def sub(a, b): return [a[i] - b[i] for i in range(3)]
def add(a, b, t=1.0): return [a[i] + b[i] * t for i in range(3)]
def mul(a, t): return [x * t for x in a[:3]]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def crs(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def ln(a): return math.sqrt(dot(a, a))
def nrm(a): l = ln(a) or 1; return [x / l for x in a[:3]]
def lerp(a, b, t): return [a[i] + (b[i] - a[i]) * t for i in range(len(a))]

def axes_of(rot):
    """three's Euler XYZ (degrees) -> the three local axes (columns)"""
    x, y, z = [math.radians(v) for v in (rot or [0, 0, 0])]
    a, b, c, d, E, f = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    ae, af, be, bf = a * E, a * f, b * E, b * f
    return [[c * E, af + be * d, bf - ae * d], [-c * f, ae - bf * d, be + af * d], [d, -b * c, a * c]]

def fd(sp, req):
    """the body field (fd.mjs): distances at points, ray exits, joints"""
    r = subprocess.run(["node", "--import", "../reg.mjs", "fd.mjs", "creatures/" + sp], input=json.dumps(req), capture_output=True, text=True, cwd=SH)
    if r.returncode: raise RuntimeError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().split("\n")[-1])

def zv(p): return [p[0], p[1], -p[2]] + list(p[3:])

def note(sp, tag, text):
    """append (or replace, by its tag) a dated sentence to a species' `_about`, the rest of the file untouched"""
    path = path_of(sp); txt = open(path).read(); d = json.loads(txt)
    if "_about" not in d: return False
    old = d["_about"]; base = old.split(" " + tag)[0] if (" " + tag) in old else old
    new = base + " " + tag + " " + text
    for enc in (False, True):
        o = json.dumps(old, ensure_ascii=enc)
        if o in txt:
            open(path, "w").write(txt.replace(o, json.dumps(new, ensure_ascii=enc), 1)); json.loads(open(path).read()); return True
    raise RuntimeError(sp + ": _about not found verbatim")
