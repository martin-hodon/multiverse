# plates.py stegosaurus | dilophosaurus : PLATES and CRESTS as `fin` sheets (2026-11-08).
# STEGOSAURUS: the dorsal plates as `fin` SHEETS (2026-11-08). They were field shapes -- a flat ell and a cone
# on top of it each -- which came out as orange CONES, and the front ones (placed for an older body) were buried in the
# back. Now 19 plates, two staggered rows (alternating left / right of the midline, each leaning out 10 degrees) from
# the neck to the middle of the tail, each rooted along the back's surface (measured on the field: fd.mjs rays), sized
# by position -- small and rounded on the neck, largest over the hips and the base of the tail, smaller and more
# pointed down the tail. Each is a thin sheet on an exact outline (roughly pentagonal: a narrower base, broad
# shoulders, the apex a pointed corner a little behind the middle), thickest at its base (`swell`) and FAIRED into the
# back (`fair`: the body swells out into it), its surface grooved by the `finrays` pattern (rays fanning from a
# point under the middle of its base -- near-parallel grooves, not a scallop's fan -- lighter toward the rim) in a frame of its own, `color` -> `tip` a little darker toward the rim.
# Each rides the spine / tail bone over it. The thagomizer's four spikes stay the horns spikes.py made.
# Re-running it gives the same plates (it replaces every shape whose id is plate*/plateTip*). Run from
# tools/creaturegen/sharp; RE-RUN after the stegosaurus' generator.
# DILOPHOSAURUS: the twin head crests -- field ells (a flat one and a rim one over it, which came out as a lumpy block
# on the skull) -- as two thin `fin` sheets (mirrored), rooted along the skull top a little either side of the midline,
# leaning out 7 degrees: low at the nostril, rising in a convex arc to its highest over the eye's front, ending behind
# in a small backward point (a corner); faired into the skull, its top edge banded in the rim colour.
import math, json
from sharp2 import *

SP = "dinosaurs/stegosaurus"
N = 19; X0, DX = 2.0, 0.28
# the plates' height above the back (metres) along the body, x -> H
HCTL = [(2.1, 0.12), (1.4, 0.25), (0.8, 0.42), (0.2, 0.58), (-0.4, 0.70), (-1.0, 0.78), (-1.5, 0.74), (-2.0, 0.56),
        (-2.5, 0.38), (-3.1, 0.18)]
LEAN, Z0, DEPTH = 10.0, 0.07, 0.07
# the rig's spine and tail joints (x): a plate rides the bone whose stretch it stands on
BONES = [(1.3, "neck"), (0.965, "front"), (0.602, "body3"), (0.238, "body2"), (-1.3, "body"), (-1.765, "tail"),
         (-2.227, "tail1"), (-2.684, "tail2"), (-3.132, "tail3"), (-9, "tail4")]

def interp(T, x):
    T = sorted(T)
    if x <= T[0][0]: return T[0][1]
    for (a, fa), (b, fb) in zip(T, T[1:]):
        if x <= b: return fa + (fb - fa) * (x - a) / (b - a)
    return T[-1][1]

def bone_at(x):
    return next(b for x0, b in BONES if x >= x0)

def build(surf):
    """surf(x, z) -> the back's height there (a table measured on the field)"""
    out = []
    for i in range(N):
        x = X0 - i * DX; sg = 1 if i % 2 == 0 else -1; z0 = Z0 * sg
        H = interp(HCTL, x); L = 0.92 * H + 0.06
        tail = max(0.0, min(1.0, (-1.4 - x) / 1.4))   # (0 over the body, 1 at the tail's middle: more pointed, leaning back)
        y0 = surf(x, z0); slope = (surf(x + 0.1, z0) - surf(x - 0.1, z0)) / 0.2
        F = nrm([1, slope, 0]); U0 = nrm([-slope, 1, 0]); N0 = [0, 0, sg]; th = math.radians(LEAN)
        U = add(mul(U0, math.cos(th)), N0, math.sin(th))
        B = [x, y0, z0]
        p3 = lambda s, t: add(add(B, F, s), U, t)
        def under(s, d):   # (a point s along the base, d below the back's surface there)
            q = p3(s, 0); return p3(s, surf(q[0], z0) - q[1] - d)
        sb = 0.32 * L   # (the base's half-length: narrower than the shoulders)
        root = [under(s, DEPTH) for s in (-sb, -sb / 2, 0, sb / 2, sb)]
        ap = -(0.10 + 0.12 * tail) * L   # (the apex a little behind the middle; further back down the tail)
        sh = 0.38 - 0.10 * tail          # (the shoulders' height, a share of H: lower on the tail -- more triangular)
        S0, S1, A = (0.50 * L, sh * H), (-0.50 * L, (sh - 0.04) * H), (ap, H)
        def edge_line(P, Q, fs=(1 / 3, 2 / 3), bulge=0.035):   # (points along a nearly straight edge, bowed out a little)
            dx, dy = Q[0] - P[0], Q[1] - P[1]; l = math.hypot(dx, dy); nx, ny = dy / l, -dx / l
            if nx * (P[0] + Q[0]) / 2 + ny * ((P[1] + Q[1]) / 2 - 0.45 * H) < 0: nx, ny = -nx, -ny
            return [(P[0] + dx * f + nx * bulge * l * 4 * f * (1 - f), P[1] + dy * f + ny * bulge * l * 4 * f * (1 - f)) for f in fs]
        pts2 = [S0] + edge_line(S0, A) + [A] + edge_line(A, S1) + [S1]
        rim = [under(0.97 * sb, -0.01) + [1.0]] + [p3(*q) + [1.0] for q in pts2] + [under(-0.97 * sb, -0.01) + [1.0]]
        apex = 1 + pts2.index(A)
        # (the rim from root[0] (rear) round: rear base, rear shoulder, ..., apex, ..., front base -- reversed so)
        rim = rim[::-1]; apex = len(rim) - 1 - apex
        k = H / 0.78
        f = {"id": "plate%d" % i, "type": "fin", "bone": bone_at(x), "root": root, "edge": rim, "corners": [apex],
             "thick": round(0.03 + 0.03 * k, 4), "slope": 0.35, "swell": [round(0.04 + 0.05 * k, 4), round(0.3 * H, 4), 1.2],
             "fair": {"r": round(0.03 + 0.04 * k, 4), "rows": 3}, "color": "@plate", "tip": "@plateRim", "tipAt": 0.45,
             "pat": "finrays", "frame": {"o": add(B, U, -0.4 * H), "u": U, "v": F, "r": round(0.9 * H, 4)},
             "n": int(round(20 + 20 * k)), "across": 4}   # (sized by the plate: 19 of them -- n 72 / across 8 had been 106k tris)
        out.append(r5(f))
    return out

def surface_table():
    xs = [round(X0 + 0.3 - k * 0.05, 3) for k in range(int((X0 + 0.3 + 3.5) / 0.05) + 1)]
    txt, d = load(SP)
    ex = [s["id"] for s in d["sculpt"]["shape"] if s.get("id", "").startswith("plate")]
    rays = [[[x, 4.5, z], [x, 0.5, z]] for z in (Z0, -Z0) for x in xs]
    hits = fd(SP, {"exclude": ex, "rays": rays})["hits"]
    T = {Z0: [(x, h[1]) for x, h in zip(xs, hits[:len(xs)])], -Z0: [(x, h[1]) for x, h in zip(xs, hits[len(xs):])]}
    return lambda x, z: interp(T[Z0 if z > 0 else -Z0], x)

def main():
    new = build(surface_table())
    # (every root point inside the body, every rim point but the base's outside it)
    txt, d = load(SP)
    ex = [s["id"] for s in d["sculpt"]["shape"] if s.get("id", "").startswith("plate")]
    q = [p for f in new for p in f["root"]]
    dr = fd(SP, {"exclude": ex, "points": q})["d"]
    if max(dr) > -0.02: print("WARNING: a plate's root is not well inside the back:", max(dr))
    txt, d = load(SP)
    sh = d["sculpt"]["shape"]
    idx = [i for i, s in enumerate(sh) if s.get("id", "").startswith("plate")]
    out = sh[:idx[0]] + new + [s for i, s in enumerate(sh) if i > idx[0] and i not in idx]
    save(SP, out, txt)
    note(SP, "(2026-11-08, plates.py)", "The PLATES are `fin` sheets (they were a flat ell and a cone each: orange cones, "
         "the front ones buried in the back): 19 in two staggered rows from the neck to the middle of the tail, each "
         "leaning out 10 degrees, rooted along the back's surface, small and rounded on the neck, largest over the hips "
         "and the base of the tail, more pointed down the tail; thin with a sharp rim on an exact pentagonal outline, "
         "thickened and faired into the back at the base, grooved (`finrays` fanning from the base) and darker toward "
         "the rim; each rides the spine or tail bone it stands on. The thagomizer's spikes stay horns.")
    print(SP, "plates", len(idx), "->", len(new))

def dilophosaurus():
    sp = "dinosaurs/dilophosaurus"; ids = ["crest", "crestTop"]
    z0, lean = 0.05, math.radians(7)
    xs = [round(2.1 + 0.02 * k, 2) for k in range(30)]
    hits = fd(sp, {"exclude": ids, "rays": [[[x, 2.7, z0], [x, 2.0, z0]] for x in xs]})["hits"]
    T = [(x, h[1]) for x, h in zip(xs, hits) if h]
    U = [0, math.cos(lean), math.sin(lean)]
    P = lambda x, h: add([x, interp(T, x), z0], U, h)   # (h: up the leaning plane from the skull's surface there)
    root = [P(x, -0.025) for x in (2.22, 2.32, 2.42, 2.52, 2.6)]
    prof = [(2.61, 0.0), (2.585, 0.03), (2.53, 0.066), (2.45, 0.094), (2.37, 0.108), (2.3, 0.106), (2.245, 0.094),
            (2.16, 0.098), (2.205, 0.05), (2.215, 0.0)]   # (front base -> the arc -> the rear point -> the rear base)
    edge = [P(x, h) + [1.0] for x, h in prof]
    edge = edge[::-1]   # (from root[0], the rear)
    f = {"id": "crest", "type": "fin", "bone": "head", "root": root, "edge": edge, "corners": [len(prof) - 1 - 7],
         "thick": 0.012, "slope": 0.3, "swell": [0.02, 0.04, 1.2], "fair": {"r": 0.015}, "color": "@crest",
         "rim": 0.012, "rimColor": "@crestRim", "n": 56, "across": 7, "mirror": True}
    txt, d = load(sp); sh = d["sculpt"]["shape"]
    idx = [i for i, s in enumerate(sh) if s.get("id") in ids]
    if not idx: raise SystemExit("no crest shapes")
    out = sh[:idx[0]] + [r5(f)] + [s for i, s in enumerate(sh) if i > idx[0] and i not in idx]
    save(sp, out, txt)
    note(sp, "(2026-11-08, plates.py)", "The twin CRESTS are thin `fin` sheets (they were two flat field ells each: a lumpy "
         "block on the skull), rooted along the skull top either side of the midline and leaning out 7 degrees: low at "
         "the nostril, rising in a convex arc to their highest over the front of the eye, ending behind in a small "
         "backward point; faired into the skull, the top edge banded in the rim colour.")
    print(sp, "crests", len(idx), "-> 1 (mirrored)")

if __name__ == "__main__":
    import sys
    for a in sys.argv[1:]: {"stegosaurus": main, "dilophosaurus": dilophosaurus}[a]()
