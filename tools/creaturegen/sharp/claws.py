# claws.py SPECIES... | all : the CLAW family (claws, talons, the anteater's and pangolin's nails, the hoof-nails of
# camels, hippos, rhinos, capybaras and the armoured dinosaurs) made the engine's `horn` (sharp.js) -- one horn per field
# cone / tube / ell, the same id, bone, colour and mirror: its root sunk into the toe (found on the body's field), its
# middle arched (a claw is convex on top), laterally compressed (aspect > 1), the tip a true point carried on past a
# blunt cone's end; a hoof-nail a short broad flat-bottomed shell with a ROUNDED end (its last two points close).
# Run once per species (a second run finds the shapes gone). The originals: git. RE-RUN after the species' generator.
import sys, re, math
from sharp2 import *

def claw_pts(s, bend=0.1, ext=2.0, ref=(0, 1, 0), rk=1.0, pw=0.8):
    """a cone or tube claw as an arched centreline ending in a point"""
    P = pts_of(s)
    if len(P) == 2:
        a, b = P[0][:3], P[1][:3]; L = ln(sub(b, a)); ra, rb = P[0][3], P[1][3]
        e = (rb * ext / L) if rb > 0.25 * ra else 0.0
        u = perp_up(nrm(sub(b, a)), ref)
        Q = bent(a, b, ra * rk, bend=bend, ext=e, n=4, up=u, pw=pw)
        return Q, u
    # a tube: its own curve, the tip carried on in the direction it turns
    d1 = nrm(sub(P[-1], P[-2])); d0 = nrm(sub(P[-2], P[-3])) if len(P) > 2 else d1
    turn = sub(d1, d0)
    chord = nrm(sub(P[-1], P[0]))
    mid = P[len(P) // 2]
    off = sub(mid[:3], add(P[0], chord, dot(sub(mid, P[0]), chord)))
    u = nrm(off) if ln(off) > 1e-4 else perp_up(chord, ref)
    if P[-1][3] > 0.25 * P[0][3]:
        L = P[-1][3] * ext
        dn = nrm(add(d1, turn, 0.6)) if ln(turn) > 1e-6 else d1
        P = P + [add(P[-1], dn, L) + [0.0]]
    P[-1] = P[-1][:3] + [0.0]
    P = [p[:3] + [p[3] * rk] for p in P]
    return P, u

def hoofnail_pts(s):
    """an ell hoof-nail: a short shell along its longest horizontal axis, forward, its end rounded"""
    P = pts_of(s)   # (along the longest axis: two ends, the middle)
    a, b = P[0][:3], P[-1][:3]
    if b[0] < a[0]: a, b = b, a   # (toward the toe's front: +x on a forefoot... the far end from the foot's centre)
    return a, b

def run(sp, spec):
    txt, d = load(sp); S = d["sculpt"]["shape"]
    for rx, kw in spec:
        ids = [s["id"] for s in S if re.fullmatch(rx, s.get("id", "")) and s["type"] in ("cone", "tube", "ell", "sphere")]
        if not ids: print(sp, "none for", rx); continue
        kind = kw.pop("kind", "claw")
        def make(old):
            if kind == "hoof":
                # (each foot's middle: the mean of its nails, by bone)
                byb = {}
                for i in ids: byb.setdefault(old[i].get("bone"), []).append(old[i]["c"])
                cen = {b: [sum(c[0] for c in C) / len(C), sum(c[2] for c in C) / len(C)] for b, C in byb.items()}
                return [hoof(sp, old[i], ids, centre=cen[old[i].get("bone")], **kw) for i in ids]
            if kind == "finger": return finger_claws(sp, old, ids, **kw)
            PU = [claw_pts(old[i], kw.get("bend", 0.1), kw.get("ext", 2.0), kw.get("ref", (0, 1, 0)), kw.get("rk", 0.8), kw.get("pw", 0.8)) for i in ids]
            Ps = sink_many(sp, [p for p, u in PU], ids, need=kw.get("need", 0.4))
            return [horn_of(r5(lift(P)), old[i], up=r5(u), aspect=kw.get("aspect", 1.3), **kw.get("extra", {})) for i, P, (_, u) in zip(ids, Ps, PU)]
        replace(sp, ids, make)

def lift(P, floor=0.003):
    """a claw whose carried-on tip went under the ground (y < floor: the rest pose stands on y 0) turned up about its
    root, in its own vertical plane, just enough"""
    if min(p[1] for p in P) >= floor or P[0][1] < floor: return P
    a = P[0][:3]; ch = sub(P[-1][:3], a); h = nrm([ch[0], 0, ch[2]])
    ax = nrm(crs(h, [0, 1, 0])) if ln([ch[0], 0, ch[2]]) > 1e-6 else [0, 0, 1]
    def rot(v, th):   # (Rodrigues about ax)
        c, s = math.cos(th), math.sin(th); k = ax
        return add(add(mul(v, c), crs(k, v), s), k, dot(k, v) * (1 - c))
    for sg in (1, -1):
        for n in range(1, 60):
            th = sg * n * 0.01
            Q = [P[0]] + [add(a, rot(sub(p[:3], a), th)) + p[3:] for p in P[1:]]
            if min(q[1] for q in Q) >= floor: return Q
    return P

def finger_claws(sp, old, ids, split=1, rk=0.75, ext=3.0, aspect=1.4, finger=None, bend=0.16, **kw):
    """a tube that drew a whole FINGER in the claw's colour (a theropod's hand) split at its point `split`: the part
    before it a field tube in the hand's colour (`finger`: {color, pat, frame, k}), the rest a hooked claw horn -- its
    root back inside that finger's end (on the finger's axis: the field the fd tool sees has no finger tube yet), its
    girth rk of the finger's there, tapering along an arc (convex on the back of the hand) to a point"""
    out = []
    for i in ids:
        s = old[i]; P = [list(p) for p in s["pts"]]
        f = {"id": i.replace("claw", "finger"), "type": "tube", "bone": s.get("bone", "body"), "pts": [p[:4] for p in P[:split + 1]],
             "k": (finger or {}).get("k", s.get("k", 0.006) * 2), "color": (finger or {}).get("color", "@body")}
        for kk in ("pat", "frame"):
            if finger and kk in finger: f[kk] = finger[kk]
        if s.get("mirror"): f["mirror"] = True
        out.append(r5(f))
        e = P[split]; fd_ = nrm(sub(e, P[split - 1])); r0 = e[3] * rk
        a = add(e, fd_, -1.2 * e[3])                      # (the sheath's mouth: a little back inside the finger's end)
        tip = P[-1][:3]; d = nrm(sub(tip, e))
        L = ln(sub(tip, e)) * 0.8 + P[-1][3] * ext * 0.5   # (a little shorter than the old tube's claw part, to a point)
        b = add(e, d, L)
        u = perp_up(d, fd_)                               # (convex toward where the finger points: a hook)
        Q = bent(e[:3], b, r0, bend=bend, up=u, n=5, pw=0.75)
        # the hidden part: the sheath a touch wider than the finger's end (round, so the finger's end cap stays inside
        # it -- no two surfaces running together); a thin finger tube is drawn as it is, not in the field, so the root is
        # carried back to the finger's start, in the field, thin and low there inside the finger
        Q = [P[split - 1][:3] + [e[3] * 0.4, 1.0], a + [e[3] * 1.06, 1.0]] + Q
        out.append(horn_of(r5(Q), s, up=r5(u), aspect=aspect))
    return out

def hoof(sp, s, ids, fwd=(1, 0, 0), flat=0.7, aspect=0.6, splay=0.6, length=1.0, centre=None, **kw):
    """a hoof-nail (an ell): a short shell from inside the toe out over its front, broad (aspect < 1), flat underneath,
    its end ROUNDED (the radius held almost to the end) -- pointing forward, splayed out by where it sits on its foot
    (`centre`: the foot's middle, x z)"""
    c, r = s["c"], s["r"]
    f = list(fwd)
    if centre is not None:
        o = [c[0] - centre[0], 0, c[2] - centre[1]]
        if ln(o) > 1e-6: f = add(f, nrm(o), splay)
    f = nrm([f[0], f[1] - 0.25, f[2]])   # (a little down: the nail follows the toe's curve to the ground)
    L = max(r) * 2.0 * length
    rr = (sorted(r)[1] * sorted(r)[2]) ** .5 * 0.9
    a = add(c, f, -L * 0.5)
    pts = [a + [rr * .85], add(a, f, L * 0.45) + [rr], add(a, f, L * 0.78) + [rr * .92], add(a, f, L * 0.94) + [rr * .6], add(a, f, L * 1.0) + [0.0]]
    pts = sink(sp, pts, ids, need=0.3)
    return horn_of(r5(pts), s, up=[0, 1, 0], aspect=aspect, flat=flat)

# per species: (id regex, options)   bend: the arch (a share of its length), ext: a blunt cone's tip carried on (radii)
SPEC = {
    "mammals/badger": [(r"h?claw\d", dict(bend=0.14, ext=2.0, aspect=1.35))],
    "mammals/bear": [(r"h?claw\d", dict(bend=0.1, ext=1.5, aspect=1.3))],
    "mammals/hyena": [(r"[fh]claw\d", dict(bend=0.16, ext=1.4, aspect=1.25))],
    "mammals/giantpanda": [(r"claw\d", dict(bend=0.14, ext=2.0, aspect=1.3))],
    "mammals/redpanda": [(r"claw\d", dict(bend=0.16, ext=2.0, aspect=1.3))],
    "mammals/skunk": [(r"claw\d", dict(bend=0.12, ext=2.0, aspect=1.3))],
    "mammals/porcupine": [(r"h?claw\d", dict(bend=0.14, ext=2.0, aspect=1.3))],
    "mammals/anteater": [(r"claw\d", dict(bend=0.0, ext=2.0, aspect=1.4)), (r"nail\d", dict(bend=0.12, ext=1.6, aspect=1.25))],
    "mammals/pangolin": [(r"claw\d", dict(bend=0.0, ext=2.0, aspect=1.4)), (r"nail\d", dict(bend=0.12, ext=1.6, aspect=1.25))],
    "others/turtle": [(r"claw[FH]\d", dict(bend=0.12, ext=2.0, aspect=1.2))],
    "sea/seal": [(r"[fh]claw\d", dict(bend=0.1, ext=2.0, aspect=1.2))],
    "monsters/hydra": [(r"claw[FH]\d", dict(bend=0.14, ext=1.5, aspect=1.3))],
    "dinosaurs/allosaurus": [(r"fclaw\d", dict(kind="finger", split=1, rk=0.9, ext=3.0, aspect=1.35)), (r"claw\d", dict(bend=0.12, ext=2.0, aspect=1.25))],
    "dinosaurs/dilophosaurus": [(r"fclaw\d", dict(kind="finger", split=1, rk=0.9, ext=3.0, aspect=1.35)), (r"claw\d", dict(bend=0.12, ext=2.0, aspect=1.25))],
    "dinosaurs/carnotaurus": [(r"claw\d", dict(bend=0.12, ext=2.0, aspect=1.25))],
    "dinosaurs/tyrannosaur": [(r"fclaw\d", dict(bend=0.16, ext=2.0, aspect=1.35)), (r"claw\d", dict(bend=0.12, ext=2.0, aspect=1.25))],
    "dinosaurs/diplodocus": [(r"claw\d", dict(bend=0.12, ext=2.0, aspect=1.3))],
    "dinosaurs/pteranodon": [(r"toeClaw\d", dict(bend=0.14, ext=1.6, aspect=1.3)), (r"wDig[ABC]Claw", dict(bend=0.16, ext=2.0, aspect=1.35))],
    "birds/eagle": [(r"claw\d", dict(bend=0.0, ext=2.0, aspect=1.3))],
    "birds/hornbill": [(r"claw\d", dict(bend=0.0, ext=2.0, aspect=1.3))],
    "birds/parrot": [(r"claw\d", dict(bend=0.0, ext=2.0, aspect=1.3))],
    "birds/buzzard": [(r"talon", dict(bend=0.18, ext=2.0, aspect=1.3))],
    "birds/falcon": [(r"talon", dict(bend=0.18, ext=2.0, aspect=1.3))],
    "birds/owl": [(r"talon", dict(bend=0.18, ext=2.0, aspect=1.3))],
    # hoof-nails: broad, flat-bottomed, rounded at the end
    "mammals/camel": [(r"h?naili|h?nailo", dict(kind="hoof", aspect=0.55, splay=0.5))],
    "mammals/bactrian": [(r"h?naili|h?nailo", dict(kind="hoof", aspect=0.55, splay=0.5))],
    "mammals/hippo": [(r"h?nail\d", dict(kind="hoof", aspect=0.6, splay=0.7))],
    "mammals/rhinoceros": [(r"h?nail\d", dict(kind="hoof", aspect=0.6, splay=0.8))],
    "mammals/capybara": [(r"h?nail\d", dict(kind="hoof", aspect=0.75, splay=0.5, flat=0.5, length=1.2))],
    "dinosaurs/ankylosaurus": [(r"nail\d", dict(kind="hoof", aspect=0.6, splay=0.8))],
    "dinosaurs/stegosaurus": [(r"nail\d", dict(kind="hoof", aspect=0.6, splay=0.8))],
}

if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["all"]: args = list(SPEC)
    for a in args:
        sp = a if "/" in a else next(k for k in SPEC if k.endswith("/" + a))
        run(sp, [(rx, dict(kw)) for rx, kw in SPEC[sp]])
