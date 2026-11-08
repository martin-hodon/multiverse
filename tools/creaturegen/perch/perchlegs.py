#!/usr/bin/env python3
"""PERCH LEGS (2026-11-06): legs for the birds drawn ALOFT (assets/creatures/birds owl, eagle, parrot, buzzard, falcon),
so that sat on a perch (perchers.js, skeleton.js PERCH) they STAND on it -- the feathered thighs ("trousers") down out of
the belly, the tarsus, the toes curled round the bough (two forward and two back: the owl's, the macaw's; three and the
hallux: the raptors'), the talons at their tips.

  apply(d, name) -> d     idempotent: drops the old tucked thigh/foot/talon prims and every part/prim this pass made
                          before (ids in LEG_IDS / prims tagged "perchleg"), then adds them afresh. Touches nothing else
                          (not coats, colors, params, wings, face) -- except the owl's tail fan (TAIL), which it rebuilds.
  python3 perchlegs.py [names]   applies it to the asset files in place.

The REST pose (what the mesh is built in) is the PERCHED leg: the body tipped up `pitch` degrees (the figure's own,
on footL: `perchPitch`, which perchers.js takes in place of its table's), the tarsus plumb under the body's centre, the
toes' undersides at the foot bone's origin -- the point that rests on the perch top. Aloft, skeleton.js turns each leg
bone by its `tuck` (degrees about z) times (1 - an.perch): the leg swung back under the tail, the toes clenched.
Each toe its own bone with `curl` { len, r0, dir }: drawn curved round a bough of radius r0; on a perch of radius
an.perchR it turns about its root by the difference (dir 1 forward, -1 back).
"""
import json, math, os, sys

R = "/home/martin/store/apps/multiverse/assets/creatures/birds/"
TAG = "perchleg"

# per species. pitch: degrees tipped up sat; hip: [x, y, z] body frame (inside the belly); gap: belly's lowest to the
# perch top (m); tars: the tarsus (m) and its radius; thighR: the trousers' girth; toes: [(len, splay deg, forward?)],
# toeR, claw: talon length; r0: the bough radius the toes are drawn round; col: colours (keys the asset already has)
SPEC = {
    "owl": dict(pitch=62, hip=[-.035, .315, .045], gap=.025, dx=-.005, tars=.06, tarsR=.019, thighR=.042, toeR=.013, claw=.03, r0=.06,
                toes=[(.068, 14, 1), (.062, -16, 1), (.058, 28, -1), (.05, -10, -1)],
                col=dict(thigh="@buff", tars="@buff", toe="@buff", claw="@talon"), feathered=True, footAloft=45),
    "eagle": dict(pitch=55, hip=[-.05, .345, .055], gap=.05, dx=-.01, tars=.085, tarsR=.019, thighR=.05, toeR=.013, claw=.038, r0=.08,
                  toes=[(.082, 0, 1), (.074, 22, 1), (.07, -20, 1), (.062, 4, -1)],
                  col=dict(thigh="@warm", tars="@warm", toe="@foot", claw="@talon"), feathered=True, hallux=1.35, footAloft=40),
    "parrot": dict(pitch=50, hip=[-.035, .275, .028], gap=.014, dx=-.004, tars=.026, tarsR=.0085, thighR=.024, toeR=.0065, claw=.012, r0=.035,
                   toes=[(.036, 14, 1), (.03, -14, 1), (.034, 22, -1), (.026, -12, -1)],
                   col=dict(thigh="@breast", tars="@foot", toe="@foot", claw="@black"), feathered=False),
    "buzzard": dict(pitch=45, hip=[-.03, .215, .032], gap=.03, dx=-.006, tars=.06, tarsR=.0085, thighR=.03, toeR=.0065, claw=.018, r0=.05,
                    toes=[(.04, 0, 1), (.036, 22, 1), (.034, -20, 1), (.03, 4, -1)],
                    col=dict(thigh="@thigh", tars="@foot", toe="@foot", claw="@talon"), feathered=False, hallux=1.3),
    "falcon": dict(pitch=50, hip=[-.025, .168, .025], gap=.022, dx=-.005, tars=.042, tarsR=.0065, thighR=.022, toeR=.005, claw=.013, r0=.04,
                   toes=[(.036, 0, 1), (.03, 22, 1), (.028, -20, 1), (.024, 4, -1)],
                   col=dict(thigh="@thigh", tars="@foot", toe="@foot", claw="@talon"), feathered=False, hallux=1.3),
    # (the great hornbill -- birds/hornbill.py: short stout grey legs, three toes forward and one back, the thighs white)
    "hornbill": dict(pitch=30, hip=[-.05, .355, .042], gap=.02, dx=-.008, tars=.05, tarsR=.0105, thighR=.03, toeR=.0075, claw=.014, r0=.05,
                     toes=[(.05, 0, 1), (.045, 20, 1), (.042, -18, 1), (.036, 4, -1)],
                     col=dict(thigh="@white", tars="@foot", toe="@foot", claw="@black"), feathered=False, hallux=1.2),
}
LEG_IDS = {"legL", "legR", "shinL", "shinR", "footL", "footR"} | {f"toe{s}{i}" for s in "LR" for i in range(4)}
OLD = {"thigh", "foot", "talon"}
r4 = lambda v: [round(x, 4) for x in v]


def rot(p, deg):   # about z, (x, y) -> turned `deg` (+ nose up)
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return [p[0] * c - p[1] * s, p[0] * s + p[1] * c] + list(p[2:])


def body_low(d, P, near=.08):
    """the lowest point of the body's big ellipsoids within `near` of the centre of their volume (fore and aft: the rump
    and the tail hang lower behind the perch), and that centre, tipped up P degrees"""
    cx, cy, vol, pts = 0, 0, 0, []
    for q in d["sculpt"]["shape"]:
        if q.get("type") != "ell" or q.get("bone") or q.get("tag") == TAG or q["id"] in OLD or min(q["r"]) < .025: continue
        v = q["r"][0] * q["r"][1] * q["r"][2]; c = rot(q["c"], P); cx += c[0] * v; cy += c[1] * v; vol += v
        rz = math.radians((q.get("rot") or [0, 0, 0])[2])
        for i in range(48):
            a = i / 48 * 2 * math.pi; x, y = q["r"][0] * math.cos(a), q["r"][1] * math.sin(a)
            x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
            pts.append(rot([q["c"][0] + x, q["c"][1] + y], P))
    com = [cx / vol, cy / vol]
    return min(p[1] for p in pts if abs(p[0] - com[0]) < near), com


def ell(id, c, r, color, k, bone, rotz=0, kc=None):
    q = {"id": id, "type": "ell", "bone": bone, "c": r4(c), "r": r4(r), "k": round(k, 4), "color": color, "mirror": True, "tag": TAG}
    if rotz: q["rot"] = [0, 0, round(rotz, 2)]
    if kc: q["kc"] = round(kc, 4)
    return q


def tube(id, pts, color, k, bone, kc=None):
    q = {"id": id, "type": "tube", "bone": bone, "pts": [r4(p) for p in pts], "k": round(k, 4), "color": color, "mirror": True, "tag": TAG}
    if kc: q["kc"] = round(kc, 4)
    return q


def apply(d, name):
    S = SPEC[name]; P = S["pitch"]
    parts = [p for p in d["parts"] if p["id"] not in LEG_IDS]
    shape = [q for q in d["sculpt"]["shape"] if q.get("tag") != TAG and q["id"] not in OLD]
    d = {**d, "parts": parts, "sculpt": {**d["sculpt"], "shape": shape}}
    body = next(p for p in parts if p["id"] == "body"); B = body["pos"]
    low, com = body_low(d, P, S["r0"] + .03)
    # THE PERCHED LEG, in the tipped frame (x forward level, y up): G the toes' root on the perch top, A the ankle, H the hip
    G = [com[0] + S["dx"], low - S["gap"]]
    A = [G[0] - S["tars"] * .12, G[1] + S["tars"]]
    Hb = S["hip"]; H = rot(Hb, P); z = Hb[2]
    back = lambda p, zz=z: rot(p[:2], -P) + [zz]   # (to the body's own frame)
    Gb, Ab = back(G), back(A)
    # bones: leg (the hip: the thigh, the trousers), shin (the ankle: the tarsus), foot (the toes' root), a bone a toe
    # ALOFT (each bone's `tuck`, degrees about z, scaled by 1 - an.legs): the thigh swung back along the body under the
    # tail, the tarsus trailing straight on behind it (both rotations turn a back-pointing bone DOWN when +), and the
    # foot turned back level, so the clenched toes lie under the vent rather than hanging
    wrap = lambda a: (a + 180) % 360 - 180
    ang = lambda v: math.degrees(math.atan2(v[1], v[0]))
    aTuck, aTrail = ang([-1, -.16]), ang([-1, -.08])
    tuck = round(wrap(aTuck - ang([Ab[0] - Hb[0], Ab[1] - Hb[1]])), 1)
    tuckS = round(wrap(aTrail - ang([Gb[0] - Ab[0], Gb[1] - Ab[1]]) - tuck), 1)
    # (footAloft: degrees more, + toes up -- the owl's, drawn tipped 62 deg, would otherwise point down below the belly)
    tuckF = round(wrap(-(tuck + tuckS) + S.get("footAloft", 0)), 1)
    # the leg's own frame: ids L (z +); the definition's mirror makes R
    for s, sz in (("L", 1), ("R", -1)):
        parts += [
            {"id": "leg" + s, "parent": "body", "shape": "sphere", "size": {"r": S["thighR"] * .5}, "color": S["col"]["thigh"],
             "pos": r4([Hb[0] - B[0], Hb[1] - B[1], sz * z - B[2]]), "tuck": tuck},
            {"id": "shin" + s, "parent": "leg" + s, "shape": "sphere", "size": {"r": S["tarsR"]}, "color": S["col"]["tars"],
             "pos": r4([Ab[0] - Hb[0], Ab[1] - Hb[1], 0]), "tuck": tuckS},
            {"id": "foot" + s, "parent": "shin" + s, "shape": "sphere", "size": {"r": S["toeR"]}, "color": S["col"]["toe"],
             "pos": r4([Gb[0] - Ab[0], Gb[1] - Ab[1], 0]), "tuck": tuckF, "perchPitch": P},
        ]
    sh = []
    col = S["col"]
    # the trousers: from inside the belly down to the ankle, feathered; the thigh's top lost in the belly
    mid = [(H[0] + A[0]) / 2, (H[1] + A[1]) / 2]; L = math.hypot(A[0] - H[0], A[1] - H[1])
    ang = math.degrees(math.atan2(A[1] - H[1], A[0] - H[0]))
    sh.append(ell("trouser", back(mid), [L * .62, S["thighR"], S["thighR"] * .85], col["thigh"], S["thighR"] * .9, "legL", ang - P))
    lowT = [A[0] + .004, A[1] + S["tars"] * .25]   # (the feathering's lower end, fuller: the "trousers'" cuff)
    sh.append(ell("cuff", back(lowT), [S["thighR"] * .75, S["thighR"] * .9, S["thighR"] * .8], col["thigh"], S["thighR"] * .6, "legL"))
    # the tarsus: plumb from the ankle to the toes' root (feathered: thick and the thigh's colour)
    tA, tG = back([A[0], A[1]]), back([G[0] + .002, G[1] + S["toeR"] * 1.3])
    sh.append(tube("tarsus", [tA + [S["tarsR"]], tG + [S["tarsR"] * (.95 if S["feathered"] else .8)]], col["tars"], S["tarsR"] * .8, "shinL"))
    # the toes: each round a bough of radius r0 (its axis along z, r0 under the root), its claw hooking on round it
    r0 = S["r0"]
    for i, (Lt, spl, fw) in enumerate(S["toes"]):
        tr = S["toeR"] * (S.get("hallux", 1) if fw < 0 and len([t for t in S["toes"] if t[2] < 0]) == 1 else 1)
        Rr = r0 + tr * .9; ca, sa = math.cos(math.radians(spl)), math.sin(math.radians(spl))
        z0 = z + sa * .006
        def at(s, extra=0.0):
            ph = s / Rr; x = fw * Rr * math.sin(ph) * ca; y = Rr * math.cos(ph) - r0
            return [G[0] + x, G[1] + y, z0 + s * sa * fw]
        n = 4; pts = []
        for j in range(n + 1):
            s = Lt * j / n; p = at(s); bp = back(p[:2], p[2])
            pts.append(bp + [tr * (1 - .25 * j / n)])
        bone = "toeL%d" % i
        sh.append(tube("toe%d" % i, pts, col["toe"], tr * .6, bone))
        # the claw: on from the tip, curving in harder (a third of the bough's radius), tapering to a point
        cl = S["claw"] * (S.get("hallux", 1) if fw < 0 and S.get("hallux") else 1)
        tip = at(Lt); ph0 = Lt / Rr; Rc = max(cl * .9, r0 * .35)
        # (the claw's arc: tangent to the toe at its tip, round a tighter centre)
        tx, ty = fw * math.cos(ph0) * ca, -math.sin(ph0)
        nx, ny = -fw * math.sin(ph0) * ca, -math.cos(ph0)   # (toward the bough's axis)
        cpts = []
        for j in range(4):
            s = cl * j / 3; a = s / Rc
            px = tip[0] + tx * Rc * math.sin(a) + nx * Rc * (1 - math.cos(a)); py = tip[1] + ty * Rc * math.sin(a) + ny * Rc * (1 - math.cos(a))
            cpts.append(back([px, py], tip[2] + s * sa * fw) + [max(.0007, tr * .78 * (1 - j / 3.4))])
        sh.append(tube("claw%d" % i, cpts, col["claw"], tr * .2, bone, kc=tr * .1))
        for s, sz in (("L", 1), ("R", -1)):
            parts.append({"id": "toe%s%d" % (s, i), "parent": "foot" + s, "shape": "sphere", "size": {"r": tr * .8}, "color": col["toe"],
                          "pos": [0, 0, round(sz * (z0 - z), 4)], "curl": {"len": round(Lt, 4), "r0": r0, "dir": fw}})
    if S["feathered"]:   # (feathers down over the toes' roots: an owl's, an eagle's)
        sh.append(ell("spat", back([G[0] + .003, G[1] + S["toeR"] * 1.6]), [S["tarsR"] * 1.15, S["toeR"] * 1.3, S["tarsR"] * 1.1], col["tars"], S["toeR"] * .8, "footL"))
    if name == "owl": shape = owl_tail(shape)
    d["sculpt"]["shape"] = shape + sh
    d["parts"] = parts
    return d


def owl_tail(shape):
    """the eagle-owl's tail: short, broad and rounded (edge-on it read as a spike) -- eleven feathers fanned 40 degrees
    each way from a wider root, the outer ones a little shorter: a round edge"""
    out = []
    for q in shape:
        if q.get("type") == "feathers" and q["id"] == "tail" and not q.get("bone") and len(q["rows"]) >= 2:
            q = json.loads(json.dumps(q)); mid = q["rows"][len(q["rows"]) // 2]
            root, L0 = mid["at"], math.hypot(mid["to"][0] - mid["at"][0], mid["to"][2] - mid["at"][2])
            rows = []
            for i in range(5):
                u = i / 4; a = math.radians(40 * (1 - 2 * u)); Lr = L0 * (1 - .1 * abs(1 - 2 * u) ** 2)
                at = [root[0], root[1], root[2] + (1 - 2 * u) * .05]
                rows.append({**mid, "at": r4(at), "to": r4([at[0] - math.cos(a) * Lr, at[1], at[2] + math.sin(a) * Lr]), "w": .047})
            q["rows"] = rows; q["n"] = 11
        out.append(q)
    return out


if __name__ == "__main__":
    names = sys.argv[1].split(",") if len(sys.argv) > 1 else ["owl", "eagle"]
    for n in names:
        f = R + n + ".json"; d = json.load(open(f))
        d = apply(d, n)
        sys.path.insert(0, "/home/martin/store/apps/multiverse/tools/creaturegen/birds")
        from bg import fmt   # (the birds' own layout: the files diff as they always have)
        open(f, "w").write(fmt(d) + "\n")
        print(n, "legs:", [p["id"] for p in d["parts"] if p["id"] in LEG_IDS][:6], "prims +", sum(1 for q in d["sculpt"]["shape"] if q.get("tag") == TAG))
