# horns.py SPECIES... : the HORN family made the engine's `horn` (sharp.js): each chain of field shapes and thin detail
# tubes that drew one horn (a stout part in the grid, its slender end a tube, `hornd`) merged into ONE centreline --
# the first point sunk a radius into the skull, the tip a true point. Run once per species (a second run finds the
# shapes gone and stops). The originals: git.
import sys, json
from conv import *

CHAINS = {
    "mammals/ox": [["horn", "hornd"]],
    "mammals/oryx": [["horn", "hornd"]],
    "mammals/rhinoceros": [["horn", "hornTip"], ["horn2"]],
    "dinosaurs/carnotaurus": [["horn", "hornTip"]],
    "mammals/impala": [["horn%d" % i for i in range(12)] + ["hornTipd"]],
    "mammals/chamois": [["hornd"]],
    "mammals/cow": [["hornd"]],
    # (not the ram: its coiled horn lies against the fleece -- unblended, the two z-fight in patches)
}

def pts_of(s):
    if s["type"] == "cone": return [list(s["a"][:3]) + [s["ra"]], list(s["b"][:3]) + [s["rb"]]]
    return [list(p[:4]) for p in s["pts"]]

def merge(shapes):
    P = []
    for s in shapes:
        for p in pts_of(s):
            if len(P) >= 2:   # (a later shape that starts back inside the last: only its points on past the end, the taper never growing)
                d = nrm(sub(P[-1], P[-2]))
                if dot(sub(p, P[-1]), d) <= 0.25 * P[-1][3]: continue
                p = p[:3] + [min(p[3], P[-1][3])]
            elif P and ln(sub(p, P[-1])) < 0.25 * max(p[3], P[-1][3]): continue
            P.append(p)
    # (thin the points of a long chain of short cones: a knot every ~1.5 radii is plenty for the spline)
    Q = [P[0]]
    for p in P[1:-1]:
        if ln(sub(p, Q[-1])) > 1.5 * Q[-1][3]: Q.append(p)
    Q.append(P[-1])
    if len(Q) < 2: Q = P
    if Q[-1][3] > 0.004: Q = extend_tip(Q, 0.7)
    Q[-1][3] = 0.0
    d = nrm(sub(Q[1], Q[0]))
    return [add(Q[0], d, -0.8 * Q[0][3]) + [Q[0][3]]] + Q   # (the root sunk into the skull)

def run(sp):
    txt, d = load(sp)
    S = d["sculpt"]["shape"]; ids = {s.get("id"): i for i, s in enumerate(S)}
    out = list(S); drop = set()
    for chain in CHAINS[sp]:
        if any(c not in ids for c in chain): print(sp, "missing", [c for c in chain if c not in ids]); return
        src = [S[ids[c]] for c in chain]
        tipc = src[-1].get("color") if src[-1].get("color") != src[0].get("color") else None
        kw = {"up": [0, 1, 0]}
        if tipc: kw.update(tip=tipc, tipAt=0.6)
        h = horn_of(r5(merge(src)), src[0], **kw)
        for kk in ("tip", "tipAt"):
            if kk in src[-1] and kk not in h: h[kk] = src[-1][kk]
        out[ids[chain[0]]] = h; drop |= {ids[c] for c in chain[1:]}
    save(sp, [s for i, s in enumerate(out) if i not in drop], txt)
    print(sp, "ok")

if __name__ == "__main__":
    for a in sys.argv[1:]: run(a)
