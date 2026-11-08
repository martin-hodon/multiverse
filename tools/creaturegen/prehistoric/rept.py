# rept.py -- helpers for the sprawling Permian / Triassic reptiles written by dimetrodon.py and desmatosuchus.py
# (2026-11-08). A "parts" rig like the wall lizard's and the crocodile's (walllizard.py: the upper leg bone out to the
# side swinging fore and aft, the lower down, a lift on the forward swing; the tail's links NOT named tail*, they swing
# on the gait clock), the sculpt overlay written one shape a line (sc/others/gen/common.py dump), and the body field
# probed through sharp/fd.mjs (sharp/shp.py fd: distances at points, where rays leave the surface) to root the SHARP
# parts -- sails, scutes, spikes, teeth, claws -- on the skin.
import sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "sharp"))
sys.path.insert(0, os.path.join(HERE, "..", "sc", "others", "gen"))
import shp
from common import dump as _dump
import common

PI = math.pi
def sub(a, b): return [a[i] - b[i] for i in range(3)]
def add(a, b, t=1.0): return [a[i] + b[i] * t for i in range(3)]
def mul(a, t): return [x * t for x in a[:3]]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def crs(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def ln(a): return math.sqrt(dot(a, a))
def nrm(a): l = ln(a) or 1; return [x / l for x in a[:3]]
def lerp(a, b, t): return [a[i] + (b[i] - a[i]) * t for i in range(len(a))]
def roty(v, deg):   # turn a vector about y (+: from +x toward +z)
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return [v[0] * c - v[2] * s, v[1], v[0] * s + v[2] * c]
def rotz(v, deg):   # about z (+: from +x toward +y)
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2]]
def mz(v): return [v[0], v[1], -v[2]] + list(v[3:])

def interp(T, x):
    """piecewise linear through [(x, v)...] (any order), held at the ends"""
    T = sorted(T)
    if x <= T[0][0]: return T[0][1]
    for (a, fa), (b, fb) in zip(T, T[1:]):
        if x <= b: return fa + (fb - fa) * (x - a) / (b - a)
    return T[-1][1]

def tube(a, b, r1, r2):
    return {"a": a, "c": lerp(a, b, .5), "b": b, "r1": r1, "r2": r2}

def rnd(v, n=4):
    if isinstance(v, float): return round(v, n)
    if isinstance(v, list): return [rnd(x, n) for x in v]
    if isinstance(v, dict): return {k: rnd(x, n) for k, x in v.items()}
    return v

def dump(path, d):
    """write assets/creatures/<path> one part / shape a line (common.dump)"""
    _dump(path, d)

def fd(sp, req):
    """the body field of assets/creatures/<sp>.json (listed in assets/index.json): {d: distances at points, hits: ray exits}"""
    return shp.fd(sp, req)

class Shapes(list):
    def S(self, id, **k):
        d = {"id": id}; d.update(k); self.append(d); return d

def bent(a, b, ra, bend=0.12, up=None, ext=0.0, n=4, pw=0.8):
    """a claw / tooth / spike a -> b (radius ra at a), its middle lifted `bend` of its length toward `up` -- [x, y, z, r]"""
    d = nrm(sub(b, a)); L = ln(sub(b, a)) * (1 + ext)
    u = nrm(up) if up else nrm(sub([0, 1, 0], mul(d, d[1])))
    out = []
    for i in range(n + 1):
        t = i / n
        p = add(add(a, d, L * t), u, bend * L * 4 * t * (1 - t))
        out.append(p + [ra * (1 - t) ** pw if i < n else 0.0])
    return out

def limb_parts(S_, sz, parent_f, parent_h, FS, FE, FW, HH, HK, HA, BF, BH, rf, rh, swing=22, lift=12, speed=.8):
    """the four leg bones of one side (sz +1 left, -1 right): upper bones swing about y (mirrored geometry makes FL go
    with HR), the lower lift the foot on the forward swing (flick 1: the positive half of the sine) -- walllizard.py"""
    z = lambda v: [v[0], v[1], v[2] * sz]
    return [
        {"id": f"legF{S_}u", "parent": parent_f, "shape": "tube", "size": tube([0, 0, 0], z(sub(FE, FS)), rf[0], rf[1]), "pos": z(sub(FS, BF)), "color": "@back",
         "anim": {"axis": "y", "deg": swing, "speed": speed, "phase": 0, "amp": True}},
        {"id": f"legF{S_}l", "parent": f"legF{S_}u", "shape": "tube", "size": tube([0, 0, 0], z(sub(FW, FE)), rf[1], rf[2]), "pos": z(sub(FE, FS)), "color": "@back",
         "anim": {"axis": "x", "deg": -lift * sz, "speed": speed, "phase": PI / 2 if sz > 0 else -PI / 2, "flick": 1, "amp": True}},
        {"id": f"legH{S_}u", "parent": parent_h, "shape": "tube", "size": tube([0, 0, 0], z(sub(HK, HH)), rh[0], rh[1]), "pos": z(sub(HH, BH)), "color": "@back",
         "anim": {"axis": "y", "deg": swing, "speed": speed, "phase": PI, "amp": True}},
        {"id": f"legH{S_}l", "parent": f"legH{S_}u", "shape": "tube", "size": tube([0, 0, 0], z(sub(HA, HK)), rh[1], rh[2]), "pos": z(sub(HK, HH)), "color": "@back",
         "anim": {"axis": "x", "deg": -lift * sz, "speed": speed, "phase": 3 * PI / 2 if sz > 0 else PI / 2, "flick": 1, "amp": True}},
    ]

def index_add(paths, after_prefix="creatures/dinosaurs/"):
    """put `paths` into assets/index.json's list that holds `after_prefix` paths, sorted in, nothing else touched
    (re-read right before writing: other agents edit the file too)"""
    P = "/home/martin/store/apps/multiverse/assets/index.json"
    txt = open(P).read(); L = txt.split("\n")
    for p in paths:
        if f'"{p}"' in txt: continue
        idx = [i for i, l in enumerate(L) if l.strip().startswith(f'"{after_prefix}')]
        at = next((i for i in idx if json.loads(L[i].strip().rstrip(",")) > p), None)
        if at is None:   # (last in the list: the old last line takes a comma)
            at = idx[-1] + 1
            if not L[idx[-1]].rstrip().endswith(","): L[idx[-1]] = L[idx[-1]].rstrip() + ","
            ind = L[idx[-1]][:len(L[idx[-1]]) - len(L[idx[-1]].lstrip())]
            L.insert(at, ind + json.dumps(p))
        else:
            ind = L[at][:len(L[at]) - len(L[at].lstrip())]
            L.insert(at, ind + json.dumps(p) + ",")
        txt = "\n".join(L)
    json.loads(txt)
    open(P, "w").write(txt)
