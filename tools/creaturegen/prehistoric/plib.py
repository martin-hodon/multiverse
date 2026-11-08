# plib.py: helpers for the prehistoric mammals' generator (gen.py, 2026-11-08): the rig's joints and the body field read
# back through probe.mjs (the species JSON given as a file, so it need not be in the catalogue yet), sharp horns with a
# rounded or pointed end, five- / four- / three-toed nails, ears cut from the rhinoceros' tubular ear fin.
import json, math, os, subprocess, sys, copy
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "giants"))
from lib import Shapes, rnd, save   # noqa: E402  (giants/lib.py: the shape list and the writer every giant uses)

CG = os.path.join(HERE, "..")
REPO = "/home/martin/store/apps/multiverse/"
TMP = os.environ.get("PREHIST_TMP", "/tmp")


def add(a, b, s=1.0): return [a[i] + b[i] * s for i in range(3)]
def sub(a, b): return [a[i] - b[i] for i in range(3)]
def mul(a, s): return [v * s for v in a]
def ln(a): return math.sqrt(sum(v * v for v in a))
def nrm(a): L = ln(a) or 1.0; return [v / L for v in a]
def lerp(a, b, t): return [a[i] + (b[i] - a[i]) * t for i in range(3)]
def mz(p): return [p[0], p[1], -p[2]] + list(p[3:])


def probe(d, req):
    """probe.mjs on the definition d (written to a scratch file): joints, field distances, ray hits"""
    f = os.path.join(TMP, "_prehist_%s.json" % d["name"])
    json.dump(d, open(f, "w"))
    r = subprocess.run(["node", "--import", "./reg.mjs", "prehistoric/probe.mjs", f], cwd=CG, input=json.dumps(req),
                       capture_output=True, text=True, timeout=300)
    if r.returncode: raise RuntimeError(r.stderr[-3000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def joints(d):
    import copy
    d = copy.deepcopy(d)
    if not d["sculpt"].get("shape"): d["sculpt"]["shape"] = [{"type": "sphere", "c": d["rear"][:3], "r": 0.3}]
    return probe(d, {"joints": True})["joints"]


def knob(id, base, tip, r, bone="head", bend=None, bendAmt=0.0, blunt=0.55, color="@knob", tipc=None, fair=None,
         aspect=None, up=None, mirror=True, n=4, rootBack=0.0, caps=(40,), sides=10, **kw):
    """a horn from `base` (on or in the skin) to `tip`, radius r at its base, its middle bowed `bendAmt` of its length
    toward `bend`; `blunt` > 0 ends it in a rounded cap of that share of r (a knob, a blunt horn), 0 a point.
    `rootBack` puts the first point that far back inside (along the axis), so the root is buried. `caps`: the latitudes
    (degrees) of the dome's rings; sharp.js adds a ring wherever the radius' slope bends, so each steep one costs many
    rings (35/60/78 cost ~200 rings a knob; one at 40 about 30). `sides` round it (10: the knobs are small)."""
    dvec = nrm(sub(tip, base)); L = ln(sub(tip, base))
    u = nrm(bend) if bend else [0, 0, 0]
    pts = []
    if rootBack > 0: pts.append(add(base, dvec, -rootBack) + [r])
    for i in range(n):
        t = i / (n - 1)
        if blunt > 0:
            tt = t * (1 - blunt * r * 0.9 / L)    # (the last ring short of the tip: the cap after it)
            rr = r * (1 - tt * (1 - blunt * 0.95))
        else:
            tt = t; rr = r * (1 - t) ** 0.85 if i < n - 1 else 0.0
        p = add(add(base, dvec, L * tt), u, bendAmt * L * 4 * tt * (1 - tt))
        pts.append(p + [rr])
    if blunt > 0:
        # (the rounded end: a ring of .7 the cap's radius a little further on, then the apex)
        last = pts[-1]; rc = last[3]
        dd = nrm(sub(last[:3], pts[-2][:3]))
        for th in caps:   # (a dome: rings at its latitudes, then the apex; each steep ring costs sharp.js many rings)
            t = math.radians(th)
            pts.append(add(last[:3], dd, rc * math.sin(t)) + [rc * math.cos(t)])
        pts.append(add(last[:3], dd, rc) + [0.0])
    h = {"id": id, "type": "horn", "bone": bone, "pts": [[round(v, 4) for v in p] for p in pts], "color": color}
    if mirror: h["mirror"] = True
    if up: h["up"] = up
    if aspect: h["aspect"] = aspect
    if tipc: h["tip"] = tipc; h["tipAt"] = kw.pop("tipAt", 0.6)
    if fair: h["fair"] = fair
    if sides: h["sides"] = sides
    h.update(kw)
    return h


def curve_horn(id, P, color, bone="head", mirror=False, fair=None, **kw):
    """a horn through explicit centreline points [x, y, z, r]; the last r forced 0 by the engine"""
    h = {"id": id, "type": "horn", "bone": bone, "pts": [[round(v, 4) for v in p] for p in P], "color": color}
    if mirror: h["mirror"] = True
    if fair: h["fair"] = fair
    h.update(kw)
    return h


def nails(prefix, bone, c, rx, rz, angles, r=0.034, color="@nail", y=None, reach=1.11, drop=0.035):
    """hoof-nails round the front of a pad foot centred c (half length rx, half width rz): one per angle (degrees,
    0 straight ahead, + toward +z), as the rhinoceros' (a short flat shell, the last two points close: a rounded end)"""
    out = []
    y0 = c[1] if y is None else y
    for i, a in enumerate(angles):
        t = math.radians(a); ca, sa = math.cos(t), math.sin(t)
        def at(f, dy): return [c[0] + rx * f * ca, y0 + dy, c[2] + rz * f * sa]
        # (a broad shell with a blunt end in four points: sharp.js puts a ring wherever the radius' slope bends, so the
        # old swelling, rounded five-point shell cost ~190 rings a nail; this one about 30)
        # (`reach`: how far past the foot's rim the tip comes, a share of rx; `drop`: how far below the foot's centre)
        e = reach - 1.11
        P = [at(0.55, -drop * 0.4) + [r * 1.3], at(0.82 + e * 0.5, -drop * 0.7) + [r * 1.08], at(1.03 + e, -drop * 0.92) + [r * 0.62],
             at(1.11 + e, -drop) + [0.0]]
        out.append({"id": "%s%d" % (prefix, i), "type": "horn", "bone": bone, "pts": [[round(v, 4) for v in p] for p in P],
                    "color": color, "mirror": True, "up": [0, 1, 0], "aspect": 0.6, "flat": 0.7, "sides": 8})
    return out


# the rhinoceros' left ear (ears2.py's tubular cupped sheet), relative to its earL joint [1.54, 1.344, 0.112]
RHINO_EAR_J = [1.54, 1.344, 0.112]
RHINO_EAR = json.load(open(REPO + "assets/creatures/mammals/rhinoceros.json"))
RHINO_EAR = next(p for p in RHINO_EAR["sculpt"]["shape"] if p["id"] == "ear")


def ear_from_rhino(J, s=1.0, sy=None, tilt=0.0, out=0.0, shift=(0, 0, 0), color="@ear", inner="@earIn", fair=None, yaw=0.0, **kw):
    """the rhinoceros' ear moved onto joint J, scaled s (sy: its height scaled apart), tipped `tilt` degrees back (about
    z, through the joint) and `out` degrees outward (about x), then `yaw` degrees about the vertical (+: its hollow,
    which faces forward on the rhinoceros, turned outward -- so from the side the cupped ear shows its back, not its edge)"""
    sy = s if sy is None else sy
    ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    co, so = math.cos(math.radians(out)), math.sin(math.radians(out))
    cy, syw = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    def rot(v):
        v = [v[0] * ct - v[1] * st, v[0] * st + v[1] * ct, v[2]]                 # (back: +tilt turns the tip toward -x)
        v = [v[0], v[1] * co - v[2] * so, v[1] * so + v[2] * co]                  # (out: the tip toward +z)
        return [v[0] * cy - v[2] * syw, v[1], v[0] * syw + v[2] * cy]           # (yaw: +x toward +z)
    def tr(p):
        v = sub(p, RHINO_EAR_J); v = rot([v[0] * s, v[1] * sy, v[2] * s])
        return [round(x, 4) for x in add(add(J, v), list(shift))]
    def trd(v):
        return [round(x, 4) for x in nrm(rot(v))]
    e = dict(RHINO_EAR)
    e["root"] = [tr(p) for p in RHINO_EAR["root"]]
    e["edge"] = [tr(p[:3]) + list(p[3:]) for p in RHINO_EAR["edge"]]
    e["face"] = trd(RHINO_EAR["face"])
    e["thick"] = round(RHINO_EAR["thick"] * s, 4); e["innerRim"] = round(RHINO_EAR["innerRim"] * s, 4)
    e["fair"] = fair or {"r": round(0.021 * s, 4), "sink": 3}
    e["color"] = color; e["inner"] = inner
    e.update(kw)
    return e


def sink_horns(d, horns, need=0.45, exclude=()):
    """each horn's root made sure to be inside the body: a point prepended back along its first segment (up to 4 radii)
    until the field's distance there is below -need x its radius"""
    qs = []
    ks = [0.5 * i for i in range(9)]
    for h in horns:
        P = h["pts"]; dv = nrm(sub(P[0][:3], P[1][:3])); r = max(P[0][3], 1e-3)
        qs += [add(P[0][:3], dv, k * r) for k in ks]
    D = probe(d, {"points": qs, "exclude": list(exclude)})["d"]
    for j, h in enumerate(horns):
        P = h["pts"]; r = max(P[0][3], 1e-3); row = D[j * len(ks):(j + 1) * len(ks)]
        k = next((i for i, v in enumerate(row) if v < -need * r), None)
        if k is None:
            print("  (warning: %s root not inside: %s)" % (h["id"], row)); continue
        if k: h["pts"] = [[round(v, 4) for v in qs[j * len(ks) + k]] + [P[0][3]]] + P
    return horns


def ear_depth(d, e):
    """the field's distance at an ear's root points (they must be inside)"""
    return probe(d, {"points": [p[:3] for p in e["root"]]})["d"]


def xpt(p, O, s, dO):
    """a point of the head's design frame moved: scaled s about O, then shifted dO (a radius, if any, scaled)"""
    q = [O[i] + (p[i] - O[i]) * s + dO[i] for i in range(3)]
    return [round(v, 4) for v in q] + [round(v * s, 4) for v in p[3:]]


def xshape(sh, O, s, dO):
    """a whole shape (field or sharp) moved as xpt: centres, ends, centrelines, root and rim; sizes scaled"""
    sh = copy.deepcopy(sh)
    for k in ("c", "a", "b"):
        if k in sh: sh[k] = xpt(sh[k], O, s, dO)
    if "pts" in sh: sh["pts"] = [xpt(p, O, s, dO) for p in sh["pts"]]
    if "root" in sh: sh["root"] = [xpt(p, O, s, dO)[:3] for p in sh["root"]]
    if "edge" in sh: sh["edge"] = [xpt(p[:3], O, s, dO) + list(p[3:]) for p in sh["edge"]]
    if "r" in sh: sh["r"] = [round(v * s, 4) for v in sh["r"]] if isinstance(sh["r"], list) else round(sh["r"] * s, 4)
    for k in ("ra", "rb", "k", "kc", "thick", "innerRim"):
        if k in sh: sh[k] = round(sh[k] * s, 4)
    if isinstance(sh.get("fair"), dict): sh["fair"] = {**sh["fair"], "r": round(sh["fair"]["r"] * s, 4)}
    elif isinstance(sh.get("fair"), (int, float)): sh["fair"] = round(sh["fair"] * s, 4)
    return sh


def xrig(d, O, s, dO):
    """the rig's head params moved with the head's shapes: head, muzzle, ears, eyes and the sculpt's eyes"""
    h = d["head"]; d["head"] = xpt(h[:3], O, s, dO) + [round(h[3] * s, 4)]
    for k in ("muzzle", "ears"):
        v = d[k]; d[k] = xpt(v[0:3], O, s, dO) + xpt(v[3:6], O, s, dO) + [round(x * s, 4) for x in v[6:]]
    e = d["eyes"]; d["eyes"] = xpt(e[:3], O, s, dO) + [round(e[3] * s, 4)]
    E = d["sculpt"]["eyes"]; E["at"] = xpt(E["at"], O, s, dO); E["from"] = xpt(E["from"], O, s, dO); E["r"] = round(E["r"] * s, 4)


def gate(sh, when):
    """a shape only some of the species have: creatures.js `when` -- kept while every named param holds"""
    sh = dict(sh); sh["when"] = when; return sh
