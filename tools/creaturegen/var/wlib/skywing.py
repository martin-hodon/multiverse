# skywing.py: a monster's great wing (the pegasus's, the griffin's) -- the birds agent's flier.wing (copied here,
# read only: scratchpad birds/flier.py) at a monster's size: the golden eagle's own wing call (birds/eagle.py) scaled F
# about its shoulder and moved to the monster's withers W0, its dihedral `dih` (rise per metre out), the covert tracts
# denser (n per tract scaled with the span, three tracts over the arm: lesser, median, greater) so they close into one
# shingled surface at this size
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flier import wing as _wing
def big_wing(W0, F, dih, nk=1.0, under=("@wingIn", "@wingIn"), bars=None, sec_lens=(.25, .3, .33, .315, .27), sec_n=14,
             prim_lens=(.3, .37, .41, .42, .39), prim_a=(6, 40), prim_n=10, prim_w=.05, cov_n=(16, 15, 14, 8), htaper=.62, hsweep=.11,
             tips=("@wingTip", "@wingTip"), quills=0.012):
    # (round 3: the outline is the caller's -- secondaries' and primaries' lengths (fractions of F, root to tip), the
    #  primaries' fan and count, the coverts' counts (lesser, median, greater, primary coverts), the hand's taper and sweep)
    x0, y0, z0 = W0
    zW, zT = z0 + (.48 - .07) * F, z0 + (.74 - .07) * F
    f = lambda v: round(v * F, 4)
    covN = lambda n: int(round(n * nk))
    sec = {"n": int(sec_n * nk), "len": f(.3), "lens": [f(v) for v in sec_lens], "w": f(.05), "outline": "round", "color": "@wing", "tip": tips[0]}
    prim = {"n": int(prim_n * nk), "a": prim_a, "lens": [f(v) for v in prim_lens], "w": f(prim_w), "color": "@wing", "tip": tips[1], "curve": .04}
    if bars: sec["bars"] = bars; prim["bars"] = bars
    sh = _wing(y0, x0, z0, zW, zT, dih, f(.22), sec=sec, prim=prim,
               covs=[{"id": "lesser", "s": .42, "len": f(.075), "w": f(.04), "n": covN(cov_n[0]), "h": .75, "color": "@covert", "tip": "@covert"},
                     {"id": "median", "s": .32, "len": f(.1), "w": f(.045), "n": covN(cov_n[1]), "h": .8, "color": "@covert", "tip": "@covert"},
                     {"id": "greater", "s": .19, "len": f(.15), "w": f(.05), "n": covN(cov_n[2]), "color": "@covert", "tip": "@wing"}],
               pcov={"s": .16, "len": f(.14), "w": f(.048), "n": covN(cov_n[3]), "color": "@covert", "tip": "@wing"},
               kink=f(.1), hsweep=f(hsweep), htaper=htaper, under=[{"s": .22, "w": .36, "color": under[0]}, {"s": .58, "w": .22, "color": under[1]}],
               ucov=[{"id": "ulesser", "s": .34, "len": f(.1), "w": f(.045), "n": covN(14), "color": "@wingIn", "tip": "@wingIn"},
                     {"id": "ugreater", "s": .16, "len": f(.15), "w": f(.05), "n": covN(14), "color": "@wingIn", "tip": "@wing"}],
               colors={"arm": "@covert"})
    # (the wing RISES dih per metre: flier's slab pieces and feathers are laid flat for the eagle's near-level wing --
    #  here each slab piece is turned to the wing's slope and every feather tract's `up` is the wing's own normal, or the
    #  pieces step up the span like a stair and the coverts stand off the slope as loose leaves)
    import math
    a = math.atan(dih); n = [0, round(math.cos(a), 4), round(-math.sin(a), 4)]
    for s in sh:
        if s.get("type") == "feathers":
            s["up"] = n if s.get("up", [0, 1, 0])[1] > 0 else [0, -n[1], -n[2]]
            for r in s["rows"]: r.pop("up", None)
            if s["id"] not in ("sec", "prim"): s["camber"] = .05; s["curve"] = 0   # (flatter coverts: the eagle's camber, scaled, curled them up off the arm)
        elif s.get("type") == "ell": s["rot"] = [round(-math.degrees(a), 2), 0, 0]
        elif s.get("id") == "edgeH": s["pts"] = [p[:3] + [round(p[3] * 1.8, 4)] for p in s["pts"]]
        s["id"] = "w" + s["id"][0].upper() + s["id"][1:]
    # (round 4: every feather ROOTED -- a quill-base tube along each tract's root line, through the rows' `at`, so no
    #  feather's root lies in a notch between the arm's slab pieces, off the skin: the island test's floating feathers)
    if quills:
        for s in [q for q in sh if q.get("type") == "feathers"]:
            sh.append({"id": s["id"] + "Q", "type": "tube", "bone": s["rows"][0].get("bone", s.get("bone")),
                       "pts": [[round(v, 4) for v in r["at"]] + [quills] for r in s["rows"]], "k": round(quills * .8, 4),
                       "color": "@covert", "mirror": True})
    wrist = [x0, round(y0 + dih * (zW - z0), 4), round(zW, 4)]
    return sh, wrist, (zT - z0)
