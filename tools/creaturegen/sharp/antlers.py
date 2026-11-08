# antlers.py deer | reindeer : ANTLERS made the engine's sharp parts (sharp.js) -- the beam a `horn` (its root sunk
# into the skull's pedicle, carried on through the crown tine it ends in), every tine its own `horn` ROOTED IN THE BEAM
# (its first point on the beam's centreline, its base widened to most of the beam's girth there so it grows out of it
# instead of being stuck on, the tip a point); the reindeer's palms (the crown, the bez palm, the shovel's leaf) flat
# `fin` sheets rooted along the beam / tine they spread from. The field keeps the skull and the pedicle; nothing of the
# antler is in it any more (it blended, blunted and lumped them). Run once per species. RE-RUN after cervid.py /
# var/rnd.py (README "Reproducibility").
import sys, math
from sharp2 import *

def near_on(P, q):
    """the point of polyline P ([x,y,z,r]) nearest q: (point, radius there, index of its segment, t)"""
    best = None
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]; ab = sub(b, a); L2 = dot(ab, ab) or 1e-12
        t = max(0.0, min(1.0, dot(sub(q, a), ab) / L2)); p = add(a, ab, t)
        dd = ln(sub(q, p))
        if best is None or dd < best[0]: best = (dd, p, a[3] + (b[3] - a[3]) * t, i, t)
    return best[1], best[2], best[3], best[4]

def tine(P, beam, base=0.7, tipr=None):
    """a tine's points (from where it leaves the beam) rooted in the beam: its first point moved onto the beam's
    centreline (r: base x the beam's radius there), the points within ~1.6 beam radii of it dropped, the radius eased
    from the root's to the tine's own, the tip a point"""
    c, rb, _, _ = near_on(beam, P[0][:3])
    R0 = rb * base
    out = [c + [R0]]
    for p in P[1:]:
        dd = ln(sub(p, c))
        if dd < rb * 1.6 and p is not P[-1]: continue
        out.append(list(p[:4]))
    # (a knot just outside the beam's surface, between the root's girth and the tine's)
    d = nrm(sub(out[1], c))
    out.insert(1, add(c, d, rb * 1.15) + [max(out[1][3], R0 * 0.8)])
    out[-1] = out[-1][:3] + [0.0]
    return out

def beam_horn(P, cont=None, sinkd=0.8):
    """the beam's points, its root carried back into the skull by sinkd x its radius, continued by a crown tine `cont`
    (its points past the beam's end, radii no larger than the beam's last)"""
    d = nrm(sub(P[1], P[0]))
    Q = [add(P[0], d, -sinkd * P[0][3]) + [P[0][3]]] + [list(p[:4]) for p in P]
    if cont:
        e = Q[-1]
        for p in cont[1:]:
            if ln(sub(p, e)) < e[3] * 0.5: continue
            Q.append(p[:3] + [min(p[3], Q[-1][3])])
    Q[-1] = Q[-1][:3] + [0.0]
    return Q

def copy_keys(src, h, keys=("when", "mirror", "pat", "frame")):
    for k in keys:
        if k in src: h[k] = src[k]
    return h

def deer():
    sp = "mammals/deer"
    tines = ["crownAd", "crownCd", "browd", "bezd", "trezd"]
    ids = ["beam", "crownBd"] + tines
    def make(o):
        B = o["beam"]["pts"]
        beam = beam_horn(B, o["crownBd"]["pts"])
        hb = horn_of(r5(beam), o["beam"], up=[0, 1, 0], aspect=0.92, tip=o["crownBd"].get("tip"), tipAt=0.86)
        out = [hb]
        for t in tines:
            s = o[t]
            h = horn_of(r5(tine(s["pts"], B)), s, up=[0, 1, 0], aspect=0.9)
            h["id"] = t[:-1]   # (no longer a "detail" tube: crownA, browd -> brow ...)
            out.append(h)
        P = sink_many(sp, [hb["pts"]], ids, need=0.5)
        hb["pts"] = r5(P[0])
        return out
    replace(sp, ids, make)

def palm(s, root_end=0.95):
    """a PALM (a flat ell: the reindeer's crown, bez palm, shovel) as a flat horn -- along its long axis, its width the
    ell's in-plane half-axis, its thickness the thin one (up: the palm's normal, aspect thin / wide), both ends
    rounded: a leaf-shaped plate that the beam runs into and the tines grow out of"""
    ax = axes_of(s.get("rot")); ex, ey, ez = nrm(ax[0]), nrm(ax[1]), nrm(ax[2]); a, b, c = s["r"]
    P = []
    for f in (-root_end, -0.75, -0.35, 0.0, 0.4, 0.75, 0.92):
        k = (1 - f * f) ** .5
        P.append(add(s["c"], ex, a * f) + [b * k])
    P.append(add(s["c"], ex, a) + [0.0])
    return P, ez, round(c / b, 3)

def mz(P):   # (the other side's: z mirrored)
    return [[p[0], p[1], -p[2]] + list(p[3:]) for p in P]

def reindeer():
    sp = "mammals/reindeer"
    bull_t = ["back2d", "backd"]
    ids = ["beam", "crown", "topT0d", "topT1d", "topT2d", "bez", "bezPalm", "bezP0d", "bezP1d", "shovel", "shoveld",
           "shovelLeaf", "shovelPt0d", "shovelPt1d", "browRd"] + bull_t + ["beamCow", "backdCow", "palmPt1dCow", "palmPt2dCow", "bezCow"]
    def make(o):
        out = []
        B = o["beam"]["pts"]
        hb = horn_of(r5(beam_horn(B)), o["beam"], up=[0, 1, 0], aspect=0.92); out.append(hb)
        for t in bull_t:   # (tines on the beam)
            h = horn_of(r5(tine(o[t]["pts"], B)), o[t], up=[0, 1, 0], aspect=0.9); h["id"] = t[:-1]; out.append(h)
        # the branches: the bez off the beam, the shovel off its base (the right side's: on the mirrored beam)
        def branch(sid, cont=None, host=B, into=None):
            s = o[sid]; P = tine(s["pts"], host, base=0.8)
            if cont: P = P[:-1] + [p[:3] + [min(p[3], P[-2][3])] for p in cont[1:]]
            if into is not None:   # (carried on into its palm's middle, tapering there)
                P = P[:-1] + [P[-1][:3] + [P[-2][3] * 0.8], list(into[:3]) + [0.0]]
            P[-1] = P[-1][:3] + [0.0]
            return horn_of(r5(P), s, up=[0, 1, 0], aspect=0.9)
        out.append(branch("bez", into=o["bezPalm"]["c"]))
        sh = o["shovel"]; host = B if sh["pts"][0][2] > 0 else mz(B)
        out.append(branch("shovel", cont=o["shoveld"]["pts"], host=host, into=o["shovelLeaf"]["c"]))
        # the palms, and the tines out of them (flat in the palm's plane, rooted toward its middle)
        for pid, tines in (("crown", ["topT0d", "topT1d", "topT2d"]), ("bezPalm", ["bezP0d", "bezP1d"]), ("shovelLeaf", ["shovelPt0d", "shovelPt1d"])):
            s = o[pid]; P, ez, asp = palm(s)
            out.append(horn_of(r5(P), s, up=r5(ez), aspect=asp, sides=16))
            for t in tines:
                q = o[t]; T = tine(q["pts"], P, base=0.55)
                h = horn_of(r5(T), q, up=r5(ez), aspect=max(asp * 1.4, 0.5)); h["id"] = t[:-1]; out.append(h)
        # the right brow tine (on the right side's beam: this one is not mirrored)
        q = o["browRd"]; h = horn_of(r5(tine(q["pts"], mz(B) if q["pts"][0][2] < 0 else B)), q, up=[0, 1, 0], aspect=0.9); h["id"] = "browR"; out.append(h)
        # the cow's: her beam carried on through the longer fork tine, the other tines rooted in it
        C = o["beamCow"]["pts"]
        hc = horn_of(r5(beam_horn(C, o["palmPt2dCow"]["pts"])), o["beamCow"], up=[0, 1, 0], aspect=0.92); out.append(hc)
        for t in ["backdCow", "palmPt1dCow"]:
            h = horn_of(r5(tine(o[t]["pts"], C)), o[t], up=[0, 1, 0], aspect=0.9); h["id"] = t.replace("dCow", "Cow"); out.append(h)
        out.append(branch("bezCow", host=C))
        out[-1]["id"] = "bezCow"
        # the beams' roots sunk into the pedicles
        Ps = sink_many(sp, [hb["pts"], hc["pts"]], ids, need=0.5)
        hb["pts"], hc["pts"] = r5(Ps[0]), r5(Ps[1])
        return out
    replace(sp, ids, make)

SP = {"deer": deer, "reindeer": reindeer}
if __name__ == "__main__":
    for a in sys.argv[1:]: SP[a]()
