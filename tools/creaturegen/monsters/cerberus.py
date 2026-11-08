# cerberus.py (2026-11-08): CERBERUS, the three-headed hound of the underworld's gate (assets/creatures/monsters/cerberus.json),
# written whole from the grey wolf (wolf_base.json: mammals/wolf.json as it stood that day, kept here so a later change to
# the wolf does not move this one). Run from anywhere: python3 tools/creaturegen/monsters/cerberus.py
#
# THE PLAN
# - the wolf's rig and sculpt scaled 1.5x about the ground, the trunk made a mastiff's: the withers, shoulders and chest
#   broader and deeper, heavier legs and paws; `kind: mammal` (mammals.js) as the wolf, `monster: true` (the monster pen)
# - THREE HEADS. The centre one is the rig's own `head` (its idle turn, `look`), on the rig's `neck`. The side ones are the
#   centre's head-and-neck group turned about the neck's root by YAW degrees out and set SHIFT out along z, on bones of their
#   own (`extras` raw parts): neckL (on the body, turned YAW about y and SIDE_RAISE up: its frame faces the way its head does) -> headL ->
#   headJawL; the right side is every left shape's mirror (`mirror: true`, bodyspec.js twin: headL -> headR), so the rest
#   mesh is mirror-symmetric (sculpt.js THE MIRROR) and is meshed as a half.
# - EVERY HEAD MOVES on the idle clock (skeleton.js: ids starting head/neck/tail are `idle`), each on its own speed and
#   phase: the head's look-around (about y), the side necks raised and lowered (about z: a howl's lift), and a JAW bone
#   on each head (headJaw, headJawL, headJawR) snapping wider now and then (`flick`: a sine's crest only).
# - THE MOUTHS are open: the lower jaw's shapes turned JAW degrees down about the hinge, a dark mouth and a tongue in the
#   gap, `horn` teeth -- canines, incisors and premolars, upper on the head, lower on the jaw -- rooted by rays through the
#   lips (probe.mjs) and sunk (plib.sink_horns)
# - THE MANE: dark bristling quills (`coat`) on the necks and the shoulders
# - THE SERPENT TAIL: one `sweep` along tail..tail5 (raw parts, each swaying on its own phase behind the last -- a wave down
#   the snake), ending in a snake's head on tail5 (cranium, snout, jaw, scales, amber eyes, two small `horn` fangs, a
#   forked tongue)
# - heavy paws with sharp `horn` claws, one a toe
import json, math, os, sys, copy
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "prehistoric"))
os.environ.setdefault("PREHIST_TMP", "/tmp")
import plib                      # noqa: E402  probe (joints, field, rays), sink_horns, xshape
from plib import save            # noqa: E402

S = 1.5          # the wolf -> cerberus
YAW = 32.0       # the side heads turned out (degrees)
SIDE_RAISE = 10.0   # ...and their necks turned up that much more than the centre's (more upright: three columns, not one mass)
SHIFT = 0.26     # ...and set out along z (metres) at the neck's root
HS = 1.18       # the heads (not the necks) against the wolf's at 1.5x: big heads on the three necks
RAISE = 14.0     # every head and neck carried higher than the wolf's, turned up about the neck's root (degrees)
LIFT = 0.0       # ...and up
JAW = 20.0       # the jaws open (degrees)
W = json.load(open(os.path.join(HERE, "wolf_base.json")))

# ---------------------------------------------------------------- small vector / rotation helpers
def add(a, b, s=1.0): return [a[i] + b[i] * s for i in range(3)]
def sub(a, b): return [a[i] - b[i] for i in range(3)]
def mul(a, s): return [v * s for v in a]
def ln(a): return math.sqrt(sum(v * v for v in a))
def nrm(a): L = ln(a) or 1.0; return [v / L for v in a]
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def mz(p): return [p[0], p[1], -p[2]] + list(p[3:])
def r4(v): return [round(x, 4) for x in v]

def rotM(deg):   # Euler XYZ, row-major (sculpt.js rotM)
    x, y, z = [d * math.pi / 180 for d in (deg or [0, 0, 0])]
    a, b, c, d, e, f = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    ae, af, be, bf = a * e, a * f, b * e, b * f
    return [[c * e, -c * f, d], [af + be * d, ae - bf * d, -b * c], [bf - ae * d, be + af * d, a * c]]
def mm(A, B): return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def mv(A, v): return [sum(A[i][k] * v[k] for k in range(3)) for i in range(3)]
def euler(m):    # XYZ Euler (degrees) of a rotation matrix (three.js setFromRotationMatrix)
    y = math.asin(max(-1, min(1, m[0][2])))
    if abs(m[0][2]) < 0.9999999: x = math.atan2(-m[1][2], m[2][2]); z = math.atan2(-m[0][1], m[0][0])
    else: x = math.atan2(m[2][1], m[1][1]); z = 0
    return [round(v * 180 / math.pi, 3) for v in (x, y, z)]
def Ry(deg):     # three.js makeRotationY
    t = deg * math.pi / 180; c, s = math.cos(t), math.sin(t)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
def Rz(deg):
    t = deg * math.pi / 180; c, s = math.cos(t), math.sin(t)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]

class Rigid:
    """a rigid motion p -> O2 + M (p - O): points, vectors (M only), ellipsoid frames"""
    def __init__(self, M, O, O2): self.M, self.O, self.O2 = M, O, O2
    def p(self, q): return r4(add(self.O2, mv(self.M, sub(q[:3], self.O)))) + list(q[3:])
    def v(self, q): return r4(mv(self.M, q[:3]))
    def rot(self, deg): return euler(mm(self.M, rotM(deg)))

def move(sh, T, bone=None):
    """a shape (field or sharp) carried by the rigid motion T; its bone renamed"""
    sh = copy.deepcopy(sh)
    for k in ("c", "a", "b"):
        if k in sh: sh[k] = T.p(sh[k])
    if "pts" in sh: sh["pts"] = [T.p(q) for q in sh["pts"]]
    if "root" in sh: sh["root"] = [T.p(q)[:3] for q in sh["root"]]
    if "edge" in sh: sh["edge"] = [T.p(q[:3]) + list(q[3:]) for q in sh["edge"]]
    for k in ("up", "face", "dir", "normal", "along"):
        if k in sh: sh[k] = T.v(sh[k])
    if sh.get("type") == "whiskers": sh["at"] = T.p(sh["at"])
    if sh.get("type") in ("ell", "box") and (sh.get("rot") or T.M != [[1, 0, 0], [0, 1, 0], [0, 0, 1]]): sh["rot"] = T.rot(sh.get("rot"))
    if bone: sh["bone"] = bone
    return sh

def whisk_f(w):
    """a whiskers shape's own forward (bodyspec.js whiskerStrands: cross(up square to dir, dir)) -- or its `along`"""
    d = nrm(w["dir"])
    if w.get("along"):
        a = w["along"]; return nrm(sub(a, mul(d, dot(a, d))))
    u = nrm(sub([0, 1, 0], mul(d, d[1]))); return cross(u, d)

def twin(sh):
    """the shape's mirror across z = 0, written out (bodyspec.js twin, by hand: a side head needs both its own sides)"""
    q = copy.deepcopy(sh); q.pop("mirror", None)
    for k in ("c", "a", "b"):
        if k in q: q[k] = mz(q[k])
    if "pts" in q: q["pts"] = [mz(p) for p in q["pts"]]
    if "root" in q: q["root"] = [mz(p) for p in q["root"]]
    if "edge" in q: q["edge"] = [mz(p) for p in q["edge"]]
    for k in ("up", "face", "normal"):
        if k in q: q[k] = mz(q[k])
    if "rot" in q: q["rot"] = [-q["rot"][0], -q["rot"][1], q["rot"][2]]
    if "twist" in q: q["twist"] = -q["twist"]
    if q.get("type") == "whiskers":
        # (the pad on the other side, strand for strand: the fan's forward kept forward -- `along` the mirror of the
        #  forward, the sweep and the curl reversed, the rows' order along kept by a negative gap)
        f = whisk_f(sh)
        q["at"] = mz(sh["at"]); q["dir"] = mz(sh["dir"]); q["along"] = r4(mul(mz(f), -1))
        q["sweep"] = [-v for v in sh.get("sweep", [-10, 25])]
        q["gap"] = [-sh.get("gap", [0.003, 0.003])[0], sh.get("gap", [0.003, 0.003])[1]]
        q["curl"] = -sh.get("curl", 0)
        q["jitter"] = 0
        if "seed" in q: q["seed"] = q["seed"] + 101
    return q

def scaled(sh, s=S, O=(0, 0, 0)):
    q = plib.xshape(sh, list(O), s, [0, 0, 0])
    if q.get("type") == "whiskers":
        q["at"] = r4(add(O, sub(sh["at"], O), s)); q["gap"] = r4(mul(sh["gap"], s)); q["len"] = r4(mul(sh["len"], s)); q["r"] = round(sh["r"] * s, 5)
    if q.get("type") == "fin":
        for k in ("rim", "innerRim"):
            if k in sh: q[k] = round(sh[k] * s, 4)
    return q

def scale_params(d):
    for k in ("rear", "front"): d[k] = r4([v * S for v in d[k]])
    for k in ("neck", "head", "muzzle", "nose", "ears", "eyes"): d[k] = r4([v * S for v in d[k]])
    L = d["legs"]
    for k in ("front", "hind", "radii", "foot"): L[k] = r4([v * S for v in L[k]])

# ---------------------------------------------------------------- colours and coats
C = {"body": "#221e1c", "saddle": "#141211", "head": "#201c1a", "ear": "#171413", "earIn": "#6a2614", "leg": "#1e1a19",
     "tail": "#1c1d1a", "eye": "#ff5a12", "lid": "#7a1c06", "belly": "#33291f", "chestc": "#2c2420", "throat": "#2e2622",
     "mask": "#2a2522", "muzzle": "#26211f", "muzzleC": "#1f1b19", "lip": "#140d0b", "nose": "#090707", "foot": "#1a1716",
     "tip": "#0d0b0a", "mane": "#100e0d", "maneTip": "#4a2c1e", "maneDark": "#060505", "mouth": "#3c0b08",
     "tongue": "#7a2420", "tooth": "#dccfb2", "claw": "#120f0e", "clawTip": "#4a443a",
     "scale": "#24211d", "scaleB": "#3a3626", "sHead": "#252720", "sEye": "#e0a818", "fang": "#ece4d0", "sTongue": "#8a1a14"}
COATS = [
    {"name": "black"},
    {"name": "bronze", "body": "#4a3524", "saddle": "#2c1f15", "head": "#4a3626", "ear": "#2e2016", "earIn": "#7a3a1c", "leg": "#3e2d20",
     "belly": "#6a5038", "chestc": "#5a4430", "throat": "#5e4834", "mask": "#584230", "muzzle": "#4e3a28", "muzzleC": "#3e2e20",
     "lip": "#1e140e", "foot": "#33261b", "tip": "#1a120c", "mane": "#24180f", "maneTip": "#7a5232", "maneDark": "#120c08",
     "scale": "#3a2e1c", "scaleB": "#6a5a34", "sHead": "#44361f", "eye": "#ff7a1a", "lid": "#6a2a08"},
    {"name": "ashen", "body": "#55514d", "saddle": "#3a3734", "head": "#57534f", "ear": "#3a3734", "earIn": "#6a3a2c", "leg": "#4c4845",
     "belly": "#7a756f", "chestc": "#6c6762", "throat": "#716c66", "mask": "#6a6560", "muzzle": "#5c5853", "muzzleC": "#4a4643",
     "lip": "#1e1b1a", "foot": "#403d3a", "tip": "#22201e", "mane": "#2a2826", "maneTip": "#8a847c", "maneDark": "#141312",
     "scale": "#3c3e3a", "scaleB": "#6e6a5e", "sHead": "#464842", "eye": "#ff4a10", "lid": "#5a1a08"},
]

# ---------------------------------------------------------------- the base: the wolf, scaled
d = {"name": "cerberus"}
for k in ("waist", "headForm", "kind", "headScale", "rear", "front", "neck", "head", "muzzle", "nose", "ears", "eyes", "legs"):
    d[k] = copy.deepcopy(W[k])
scale_params(d)
d["headTurn"] = 16
d["monster"] = True
d["call"] = "wolf"
d["print"] = "paw"

d["legs"]["radii"] = r4([v * 1.15 for v in d["legs"]["radii"]])
d["legs"]["foot"] = r4([v * 1.15 for v in d["legs"]["foot"]])
shapes = [scaled(s) for s in W["sculpt"]["shape"] if s["id"] != "tail"]
by = {s["id"]: s for s in shapes}

# a MASTIFF'S TRUNK: broader and deeper at the withers, shoulders and chest
def bulk(i, f, dc=None):
    s = by[i]; s["r"] = r4([s["r"][j] * f[j] for j in range(3)])
    if dc: s["c"] = r4(add(s["c"], dc))
bulk("chest", [1.06, 1.12, 1.32]); bulk("brisket", [1.15, 1.15, 1.4], [0.02, -0.01, 0]); bulk("withers", [1.12, 1.25, 1.5], [0.0, 0.02, 0])
bulk("loin", [1.0, 1.05, 1.18]); bulk("rump", [1.0, 1.06, 1.18]); bulk("belly", [1, 1, 1.25]); bulk("saddle", [1.0, 1.0, 1.2])
bulk("scapula", [1.25, 1.12, 1.35]); by["scapula"]["c"] = r4([by["scapula"]["c"][0], by["scapula"]["c"][1] + 0.02, by["scapula"]["c"][2] * 1.35])
bulk("thigh", [1.2, 1.08, 1.25])
by["arm"]["pts"] = [r4(p[:3]) + [round(p[3] * 1.35, 4)] for p in by["arm"]["pts"]]
for i in ("forearm", "gaskin", "hock", "pastern"): by[i]["ra"] = round(by[i]["ra"] * 1.32, 4); by[i]["rb"] = round(by[i]["rb"] * 1.3, 4)
for i in ("paw", "hpaw", "carpal", "calc"): bulk(i, [1.22, 1.15, 1.25])
for i in [s["id"] for s in shapes if s["id"].startswith(("toe", "htoe"))]:   # (the toes bigger, spread over the broader paw)
    pz = by["paw" if i.startswith("toe") else "hpaw"]["c"][2]
    bulk(i, [1.25, 1.15, 1.22]); by[i]["c"][2] = round(pz + (by[i]["c"][2] - pz) * 1.2, 4)
for i, f in (("neck", [1.05, 1.02, 0.8]), ("nape", [1.05, 1.0, 0.85]), ("throat", [1.0, 1.0, 0.9])): bulk(i, f)
for s in shapes:   # (the wolf's agouti ticking off: a black hound)
    if s.get("pat") == "agouti": s.pop("pat")

# ---------------------------------------------------------------- the centre head: the wolf's, the mouth opened
HEAD_BONES = {"head", "earL", "neck"}
head0 = [s for s in shapes if s.get("bone") in HEAD_BONES or s["type"] == "whiskers"]
body0 = [s for s in shapes if s not in head0]
by["ruffP0"]["ra"] *= 0.7; by["ruffP1"]["ra"] *= 0.7; by["ruffC"]["r"] = r4(mul(by["ruffC"]["r"], 0.75))
HINGE = r4(mul([0.66, 0.777, 0], S))
TJ = Rigid(Rz(-JAW), HINGE, HINGE)
jaw = by["jaw"]; jaw["ra"] = round(0.032 * S, 4); jaw["rb"] = round(0.018 * S, 4); jaw["k"] = round(0.012 * S, 4)
jaw2 = move(jaw, TJ, "headJaw")
head0 = [jaw2 if s is jaw else s for s in head0]
# (the dark of the mouth between the jaws, and the tongue lying in the lower one)
head0.append({"id": "mouthIn", "type": "ell", "bone": "head", "c": r4(mul([0.7, 0.758, 0], S)), "r": r4(mul([0.062, 0.02, 0.022], S)), "k": round(0.006 * S, 4), "color": "@mouth"})
head0.append(move({"id": "tongue", "type": "ell", "bone": "headJaw", "c": r4(mul([0.752, 0.783, 0], S)), "r": r4(mul([0.06, 0.007, 0.019], S)), "k": round(0.004 * S, 4), "color": "@tongue", "wet": 0.5}, TJ))
head0.append(move({"id": "chin", "type": "ell", "bone": "headJaw", "c": r4(mul([0.79, 0.758, 0], S)), "r": r4(mul([0.03, 0.017, 0.02], S)), "k": round(0.008 * S, 4), "color": "@lip"}, TJ))
by["lip"]["color"] = "@lip"
# (a snarl: the muzzle's top wrinkled up toward the eyes -- two low ridges a side)
for j, (x, y) in enumerate([(0.765, 0.822), (0.735, 0.83)]):
    head0.append({"id": "snarl%d" % j, "type": "ell", "bone": "head", "c": r4(mul([x, y, 0.022], S)), "r": r4(mul([0.008, 0.006, 0.018], S)),
                  "rot": [30, 0, 0], "k": round(0.006 * S, 4), "color": "@muzzleC", "mirror": True})

# ---------------------------------------------------------------- probes
TMP = os.environ["PREHIST_TMP"]

def assemble(extra_shapes=(), eyes=None):
    dd = copy.deepcopy(d)
    # (a provisional jaw bone: the field does not depend on where the bones are, only the skin does)
    dd["extras"] = [{"raw": {"id": "headJaw", "parent": "head", "shape": "sphere", "size": {"r": 0.02}, "pos": [0, 0, 0], "color": "#000000"}}]
    dd["sculpt"] = {"keep": [], "mesh": {"tris": [16000, 4800], "cell": 0.011}, "shape": copy.deepcopy(list(body0) + list(head0) + list(extra_shapes))}
    if eyes: dd["sculpt"]["eyes"] = eyes
    return dd

base = assemble()
J = plib.joints(base)
print("joints: neck", J["neck"], "head", J["head"])

# the teeth: roots found by rays through the lips (in the closed head's frame for the lower ones, then opened with the jaw)
def teeth_rays():
    up, lo = [], []
    # upper: [x along the muzzle (wolf metres), length, root radius, name]
    U = [(0.836, 0.022, 0.0042, "inc"), (0.822, 0.034, 0.0062, "can"), (0.80, 0.014, 0.0042, "pm1"), (0.775, 0.018, 0.005, "pm2"), (0.745, 0.016, 0.0055, "car")]
    L = [(0.818, 0.016, 0.0036, "linc"), (0.805, 0.03, 0.0056, "lcan"), (0.78, 0.013, 0.0042, "lpm1"), (0.752, 0.015, 0.0048, "lpm2")]
    return U, L
U, L = teeth_rays()
dd = assemble()
rays = []
for x, ln_, r, n in U: rays.append([r4(mul([x, 0.785, 0], S)), r4(mul([x, 0.745, 0.04], S))])
probe_closed = copy.deepcopy(dd)   # (the lower teeth found on the jaw as it was, closed: its shapes put back)
probe_closed["sculpt"]["shape"] = [s for s in probe_closed["sculpt"]["shape"] if s.get("bone") != "headJaw"] + [jaw, {"id": "chinC", "type": "ell", "c": r4(mul([0.79, 0.758, 0], S)), "r": r4(mul([0.03, 0.017, 0.02], S)), "k": 0.012, "color": "@lip"}]
H1 = plib.probe(dd, {"rays": rays, "exclude": ["mouthIn", "tongue"]})["hits"]
rays2 = [[r4(mul([x, 0.762, 0], S)), r4(mul([x, 0.80, 0.035], S))] for x, ln_, r, n in L]
H2 = plib.probe(probe_closed, {"rays": rays2, "exclude": ["mouthIn", "lip", "snoutU", "muzzle", "nose", "bridge"]})["hits"]

def tooth(id, hit, down, length, r, bone, color="@tooth", lean=0.12):
    """a pointed tooth: root a little inside the hit along its axis, tip `length` out along `down`, a slight hook back"""
    dv = nrm(down)
    base = add(hit, dv, -0.5 * r)
    back = [-1, 0, 0]
    pts = [add(base, dv, -1.6 * r) + [r], base + [r]]
    for t in (0.35, 0.7, 1.0):
        p = add(add(hit, dv, length * t), back, lean * length * t * t)
        pts.append(r4(p) + [round(r * (1 - t) ** 0.9 * 0.95, 5) if t < 1 else 0.0])
    return {"id": id, "type": "horn", "bone": bone, "pts": [r4(p[:3]) + [p[3]] for p in pts], "color": color, "tip": "#f4eedc", "tipAt": 0.6,
            "mirror": True, "sides": 8, "aspect": 1.15}

teeth = []
for (x, length, r, n), h in zip(U, H1):
    if not h: print("  upper tooth %s: no hit" % n); continue
    teeth.append(tooth("t" + n, h, [0.08, -1, 0.06], length * S, r * S, "head"))
for (x, length, r, n), h in zip(L, H2):
    if not h: print("  lower tooth %s: no hit" % n); continue
    t = tooth("t" + n, h, [-0.06, 1, 0.05], length * S, r * S, "headJaw", lean=0.1)
    teeth.append(move(t, TJ))
head0 += teeth

# ---------------------------------------------------------------- the heads bigger (about the head's joint), then the whole group turned up about the neck's root
HJ0 = J["head"]
head0 = [scaled(s, HS, HJ0) if s.get("bone", "body") != "neck" else s for s in head0]
HINGE = plib.xpt(HINGE, HJ0, HS, [0, 0, 0])
NJ = J["neck"]
TR = Rigid(Rz(RAISE), NJ, NJ)
head0 = [move(s, TR) for s in head0]
HINGE = TR.p(HINGE)
for k in ("head", "nose", "eyes"): d[k] = TR.p(d[k][:3]) + d[k][3:]
for k in ("muzzle", "ears"): d[k] = TR.p(d[k][0:3]) + TR.p(d[k][3:6]) + d[k][6:]
d["neck"] = d["neck"][0:3] + TR.p(d["neck"][3:6]) + d["neck"][6:]
J = plib.joints(assemble())
print("raised: head", J["head"])

# ---------------------------------------------------------------- the side heads
SIDE_PIV = r4(add(NJ, [-0.06, 0, 0]))
ML = mm(Ry(-YAW), Rz(SIDE_RAISE)); MR = mm(Ry(YAW), Rz(SIDE_RAISE))   # (the left neck's frame, and its mirror's)
TL = Rigid(ML, SIDE_PIV, add(SIDE_PIV, [-0.02, LIFT, SHIFT]))
SLIM = {"neckL": [1.0, 0.78, 0.85], "throatL": [0.9, 0.75, 0.8], "napeL": [1.0, 0.9, 0.9]}   # (the side necks leaner: no throat bag where no chest is under them)
BONE_L = {"head": "headL", "earL": "headL", "neck": "neckL", "headJaw": "headJawL"}
side = []
for s in head0:
    both = [s, twin(s)] if s.get("mirror") else [s]
    for k, q in enumerate(both):
        q = copy.deepcopy(q); q.pop("mirror", None)
        if k: q["id"] = q["id"] + "_o"
        m = move(q, TL, BONE_L.get(q.get("bone", "body"), q.get("bone")))
        m["id"] = m["id"] + "L"; m["mirror"] = True
        if m["id"] in SLIM: m["r"] = r4([m["r"][j] * SLIM[m["id"]][j] for j in range(3)])
        side.append(m)
# (broad shoulders the side necks rise from: a mass bridging each neck's root to the withers)
side.append({"id": "shoulderL", "type": "ell", "c": r4(add(SIDE_PIV, [-0.1, -0.1, SHIFT * 0.62])), "r": [0.24, 0.19, 0.15],
             "rot": euler(mm(Ry(-YAW * 0.5), Rz(30))), "k": 0.07, "color": "@body", "mirror": True})

# ---------------------------------------------------------------- the mane: dark bristling quills on the necks and the shoulders
mane = [
    {"id": "maneNeck", "type": "ell", "bone": "neck", "c": TR.p(r4(mul([0.5, 0.78, 0], S))), "r": r4(mul([0.13, 0.07, 0.075], S)), "rot": [0, 0, 28 + RAISE], "k": round(0.03 * S, 4), "color": "@mane", "coat": True},
    {"id": "maneWith", "type": "ell", "c": r4(mul([0.3, 0.765, 0], S)), "r": r4(mul([0.17, 0.06, 0.12], S)), "rot": [0, 0, 8], "k": round(0.035 * S, 4), "color": "@mane", "coat": True},
    {"id": "maneSh", "type": "ell", "c": r4(mul([0.33, 0.72, 0.09], S)), "r": r4(mul([0.11, 0.07, 0.06], S)), "rot": [0, 0, 18], "k": round(0.03 * S, 4), "color": "@mane", "coat": True, "mirror": True},
]
mane_side = [move(mane[0], TL, "neckL") | {"id": "maneNeckL", "mirror": True}]

# ---------------------------------------------------------------- the serpent tail: tail..tail5 and one sweep
TP = [[-0.70, 0.86, 0, 0.1], [-0.84, 0.83, 0, 0.093], [-0.99, 0.72, 0, 0.084], [-1.14, 0.58, 0, 0.075], [-1.32, 0.50, 0, 0.067],
      [-1.50, 0.53, 0, 0.06], [-1.64, 0.64, 0, 0.055], [-1.72, 0.79, 0, 0.051], [-1.76, 0.93, 0, 0.049], [-1.80, 1.02, 0, 0.048]]
SS = 1.6   # the snake's head against the sizes written below
TB = ["tail", "tail1", "tail2", "tail3", "tail4", "tail5"]
TJT = [TP[0][:3], TP[2][:3], TP[4][:3], TP[5][:3], TP[7][:3], TP[9][:3]]   # their joints
sweep = {"id": "serpent", "type": "sweep", "bones": TB, "pts": TP, "k": round(0.02 * S, 4), "kc": 0.01, "color": "@scale", "pat": "scales", "thin": 1.5}
# the snake's head on tail5: looking back and a little up from the end of the tail
F = nrm([-1.0, 0.32, 0]); Uv = nrm(cross([0, 0, 1], F)); Z = [0, 0, 1]
SH = TP[9][:3]
def sp(f, u, z=0.0): return r4(add(add(add(SH, F, f * SS), Uv, u * SS), Z, z * SS))
FR = euler([[F[0], Uv[0], 0], [F[1], Uv[1], 0], [F[2], Uv[2], 1]])
snake = [
    {"id": "sCran", "type": "ell", "bone": "tail5", "c": sp(0.06, 0.004), "r": [0.075, 0.042, 0.055], "rot": FR, "k": 0.03, "color": "@sHead", "pat": "scales"},
    {"id": "sSnout", "type": "ell", "bone": "tail5", "c": sp(0.125, 0.0), "r": [0.05, 0.03, 0.04], "rot": FR, "k": 0.02, "color": "@sHead", "pat": "scales"},
    {"id": "sJaw", "type": "ell", "bone": "tail5", "c": sp(0.09, -0.028), "r": [0.07, 0.016, 0.04], "rot": FR, "k": 0.014, "color": "@scaleB"},
    {"id": "sBrow", "type": "ell", "bone": "tail5", "c": sp(0.08, 0.026, 0.03), "r": [0.035, 0.012, 0.016], "rot": FR, "k": 0.01, "color": "@sHead", "mirror": True},
    {"id": "sMouth", "type": "tube", "bone": "tail5", "pts": [sp(0.168, -0.016) + [0.004], sp(0.12, -0.016, 0.035) + [0.004], sp(0.06, -0.012, 0.045) + [0.004]], "k": 0.003, "color": "#0a0807", "op": "paint", "kc": 0.004, "mirror": True},
]
def fang(id, at, r, length):
    dv = nrm(add(mul(Uv, -1), F, -0.25)); base = add(at, dv, -0.012)
    return {"id": id, "type": "horn", "bone": "tail5", "pts": [r4(base) + [r], r4(at) + [r * 0.9], r4(add(at, dv, length * 0.5)) + [r * 0.5], r4(add(add(at, dv, length), F, -0.004)) + [0.0]],
            "color": "@fang", "mirror": True, "sides": 8}
for q in snake:   # (the sizes written for a smaller head: scaled with it)
    if q["type"] == "ell": q["r"] = r4(mul(q["r"], SS)); q["k"] = round(q["k"] * SS, 4)
snake.append(fang("sFang", sp(0.15, -0.022, 0.017), 0.0045 * SS, 0.03 * SS))
# (a forked tongue flicking out of the front of the mouth)
tq = sp(0.17, -0.02)
snake.append({"id": "sTongue", "type": "horn", "bone": "tail5", "pts": [r4(add(tq, F, -0.03 * SS)) + [0.0035 * SS], r4(tq) + [0.003 * SS], r4(add(tq, F, 0.03 * SS)) + [0.0026 * SS],
              r4(add(add(tq, F, 0.055 * SS), Z, 0.009 * SS)) + [0.0]], "color": "@sTongue", "mirror": True, "sides": 6})
s_eyes = {"at": sp(0.085, 0.022, 0.04), "from": sp(0.07, 0.0), "r": round(0.0105 * SS, 4), "iris": "@sEye", "pupil": "slit", "lid": "#0a0a08", "sink": 0.45, "socket": 1.08, "bone": "tail5"}

# ---------------------------------------------------------------- claws: one a toe, hooked down
def claws():
    out = []
    for s in shapes:
        if not s["id"].startswith(("toe", "htoe")): continue
        c, r = s["c"], s["r"]
        base = [c[0] + r[0] * 0.55, c[1] + r[1] * 0.15, c[2]]
        Lc = 0.042 if s["id"].startswith("toe") else 0.036
        tip = [base[0] + Lc * 0.85, 0.004, base[2]]
        mid = [base[0] + Lc * 0.55, base[1] - 0.003, base[2]]
        rr = 0.0072 if s["id"].startswith("toe") else 0.0064
        out.append({"id": "claw" + s["id"], "type": "horn", "bone": s["bone"], "pts": [r4(add(base, [-1, 0.1, 0], 0.014)) + [rr], r4(base) + [rr],
                    r4(mid) + [rr * 0.62], r4(tip) + [0.0]], "color": "@claw", "tip": "@clawTip", "tipAt": 0.75, "mirror": True,
                    "up": [0.35, 0.94, 0], "aspect": 1.35, "fair": {"r": 0.005, "skin": 0.15}})
    return out
claw = claws()

# ---------------------------------------------------------------- the eyes: ember, one pair a head
E0 = [TR.p(plib.xpt(scaled({"type": "x", "c": W["sculpt"]["eyes"][k]})["c"], HJ0, HS, [0, 0, 0])) for k in ("at", "from")]
eye = {"r": round(W["sculpt"]["eyes"]["r"] * S * HS, 4), "iris": "@eye", "pupil": "slit", "lid": "@lid", "sink": 0.5, "socket": 1.12}
eyes = [dict(eye, at=E0[0], **{"from": E0[1]}),
        dict(eye, at=TL.p(E0[0]), bone="headL", **{"from": TL.p(E0[1])}),
        dict(eye, at=TL.p(mz(E0[0])), bone="headL", **{"from": TL.p(mz(E0[1]))}),
        s_eyes]

# ---------------------------------------------------------------- the rig's own bones for the side heads, the jaws and the tail
HJ = J["head"]
def local(child, parent, M=None):   # (a child's place in its parent's frame: M the parent's rotation, its transpose applied)
    v = sub(child, parent)
    return r4(v if M is None else [sum(M[k][i] * v[k] for k in range(3)) for i in range(3)])
NL, HL, JL = TL.p(NJ), TL.p(HJ), TL.p(HINGE)
ball = lambda r: {"shape": "sphere", "size": {"r": r}}
extras = [
    {"raw": {"id": "headJaw", "parent": "head", **ball(0.02), "pos": local(HINGE, HJ), "color": C["lip"],
             "anim": {"axis": "z", "deg": -13, "speed": 0.19, "phase": 0.4, "flick": 5}}},
    {"raw": {"id": "neckL", "parent": "body", **ball(0.05), "pos": local(NL, d["rear"][:3]), "rot": euler(ML), "color": C["body"],
             "anim": {"axis": "z", "deg": 7, "speed": 0.13, "phase": 1.1}}},
    {"raw": {"id": "headL", "parent": "neckL", **ball(0.05), "pos": local(HL, NL, ML), "color": C["head"],
             "anim": {"axis": "y", "deg": 20, "speed": 0.24, "phase": 1.9}}},
    {"raw": {"id": "headJawL", "parent": "headL", **ball(0.02), "pos": local(JL, HL, ML), "color": C["lip"],
             "anim": {"axis": "z", "deg": -13, "speed": 0.23, "phase": 2.3, "flick": 5}}},
    {"raw": {"id": "neckR", "parent": "body", **ball(0.05), "pos": local(mz(NL), d["rear"][:3]), "rot": euler(MR), "color": C["body"],
             "anim": {"axis": "z", "deg": 7, "speed": 0.11, "phase": 3.4}}},
    {"raw": {"id": "headR", "parent": "neckR", **ball(0.05), "pos": local(mz(HL), mz(NL), MR), "color": C["head"],
             "anim": {"axis": "y", "deg": -20, "speed": 0.29, "phase": 4.4}}},
    {"raw": {"id": "headJawR", "parent": "headR", **ball(0.02), "pos": local(mz(JL), mz(HL), MR), "color": C["lip"],
             "anim": {"axis": "z", "deg": -13, "speed": 0.27, "phase": 0.9, "flick": 5}}},
]
TA = [{"axis": "y", "deg": 7, "speed": 0.32, "phase": 0.0}, {"axis": "y", "deg": 10, "speed": 0.32, "phase": -1.0},
      {"axis": "y", "deg": 12, "speed": 0.32, "phase": -2.0}, {"axis": "y", "deg": 12, "speed": 0.32, "phase": -3.0},
      {"axis": "z", "deg": 9, "speed": 0.21, "phase": 0.6}, {"axis": "y", "deg": 22, "speed": 0.17, "phase": 1.3}]
for i, b in enumerate(TB):
    par = "body" if i == 0 else TB[i - 1]
    pos = local(TJT[i], d["rear"][:3]) if i == 0 else local(TJT[i], TJT[i - 1])
    extras.append({"raw": {"id": b, "parent": par, **ball(0.03), "pos": pos, "color": C["scale"], "anim": TA[i]}})
d["extras"] = extras

# ---------------------------------------------------------------- assemble, sink the sharp roots, save
d["c"] = C
d["coats"] = COATS
d["_coats"] = ("COATS (species.js coatDef): BLACK with ember eyes (the base: charcoal and soot, the inner ears, eyelids and mouth "
               "ember-red), dark BRONZE (a burnt umber hound, its snake tail bronze-scaled) and ASHEN grey (pale ash over charcoal, the "
               "eyes a hotter red). No young.")
allshapes = body0 + head0 + side + mane + mane_side + [sweep] + snake + claw
dd = copy.deepcopy(d)
dd["sculpt"] = {"keep": [], "mesh": {"tris": [18000, 5400], "cell": 0.011, "focus": {"head": 1.6, "headL": 1.6, "headR": 1.6, "tail5": 1.6}, "symmetric": True},
                "shape": allshapes, "eyes": eyes,
                "coat": {"gap": 0.034, "len": 0.1, "r": 0.011, "sides": 3, "lean": 1.0, "vary": 0.35, "skirt": -1.2, "drop": 0, "face": 0.5, "rise": 0.45,
                         "tip": "@maneTip", "base": "@mane", "dark": 0.45, "darkTip": "@maneDark", "hold": 0.55},
                "shade": {"back": 0.78, "belly": 1.3, "k": round(0.12 * S, 4), "low": 1.15, "on": "@body"}}
horns = [s for s in allshapes if s["type"] == "horn" and s["id"].startswith(("claw", "t", "sF")) and not s["id"].startswith("tail") and not s["id"].startswith("sT")]
plib.sink_horns(dd, horns, need=0.4)
d = dd
d["_about"] = ("CERBERUS (2026-11-08, tools/creaturegen/monsters/cerberus.py, written whole from the grey wolf: wolf_base.json there): the "
    "three-headed hound that guards the underworld's gate -- a black mastiff-built wolf 1.5x a grey wolf's size (withers ~1.1 m), the "
    "withers, shoulders and chest broadened and deepened, heavy legs and paws with hooked `horn` claws, one a toe. THREE HEADS on three "
    "thick necks from the shoulders: the centre one the rig's own `head` and `neck` (its idle look-around, an.look); the side ones the "
    "centre's head-and-neck group turned %d degrees out and %d more up about the neck's root and set out %.2f m (broad shoulder masses under them), on bones of their own (extras: "
    "neckL -> headL -> headJawL, mirrored R) -- the right head every left shape's mirror, so the rest mesh is mirror-symmetric "
    "(mesh.symmetric). Each head a wolf's: erect cupped `fin` ears, dark whiskers, EMBER eyes (slit pupils, ember-red lids), the "
    "MOUTH OPEN in a snarl -- the lower jaw turned %d degrees down on its own JAW bone, a dark mouth and a tongue between, the muzzle "
    "wrinkled, `horn` teeth (canines, incisors, premolars and the carnassial, upper on the head, lower on the jaw, rooted by rays "
    "through the lips). EVERY HEAD MOVES on the idle clock, each on its own speed and phase: the heads look about (y), the side "
    "necks rise and fall (z: a howl's lift), each jaw snaps wider now and then (a flick). A MANE of dark bristling quills (`coat`) "
    "on the necks and the shoulders. The TAIL a SERPENT: one scaled `sweep` along tail..tail5 (raw parts, each swaying a beat behind "
    "the last: a wave runs down it), rising at its end into a snake's head (tail5: scaled cranium and snout, amber slit eyes, two "
    "small `horn` fangs, a red forked tongue) that looks about. It howls as the wolf does (call). In the monster pen (MFENCE: "
    "`monster`; the world has no cave, ruin or underworld gate to set it at)." % (YAW, SIDE_RAISE, SHIFT, JAW))
order = ["name", "_about", "kind", "monster", "call", "waist", "headForm", "shy", "headScale", "headTurn", "rear", "front", "neck", "head", "muzzle",
         "nose", "ears", "eyes", "legs", "extras", "c", "coats", "_coats", "print", "sculpt"]
out = {k: d[k] for k in order if k in d}
save("monsters/cerberus", out)
print("saved: %d shapes (%d horns), %d eyes" % (len(allshapes), sum(1 for s in allshapes if s["type"] == "horn"), len(eyes)))
