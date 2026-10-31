"""Greek pots' shapes, shared by propgen.py (the lathe) and greekgen.py (the painting on it). A painting wraps a pot once
round and along its whole profile (items.js `wrap`), so its zones are said here in HEIGHTS on the pot and turned into shares
of the painting: a picture goes where the body is near its full width, where it isn't pinched at the feet."""
import math

def rounded(profile, n=3):                        # a thrown pot has no corners: each step of its profile cut by a Catmull-Rom
    P, out = profile, []
    for i in range(len(P) - 1):
        a, b, c, d = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)]
        for k in range(n):
            t = k / n
            out.append([round(max(0, .5 * (2 * b[j] + (c[j] - a[j]) * t + (2 * a[j] - 5 * b[j] + 4 * c[j] - d[j]) * t * t + (3 * b[j] - a[j] - 3 * c[j] + d[j]) * t ** 3)), 4) for j in (0, 1)])
    return out + [P[-1]]

# profile [[r, y], ...] from the foot up (m); zones from the lip down, each (the height it ends at, a zone of greekgen's PAINTINGS)
# with `picture` on the one that sets the painting's proportions. Handles at +-x; a one-sided pot's front is +z, its `at` .25.
POTS = {
    "amphora": {"profile": [[.07, 0], [.075, .012], [.05, .025], [.065, .06], [.13, .17], [.155, .26], [.145, .33], [.09, .385], [.055, .405], [.05, .46], [.075, .49], [.08, .5], [.05, .495]],
                "zones": [(.46, {"solid": 1}), (.405, {"band": "palmette"}), (.375, {"band": "tongues"}), (.35, {"solid": 1}),
                          (.135, {"picture": 1, "panels": 2, "width": .6}), (.075, {"solid": 1}), (.02, {"band": "rays"}), (0, {"solid": 1})]},
    "krater": {"profile": [[.085, 0], [.09, .015], [.05, .03], [.06, .06], [.13, .13], [.17, .23], [.185, .32], [.2, .37], [.215, .395], [.19, .39]],
               "zones": [(.372, {"band": "ivy"}), (.35, {"band": "meander"}), (.165, {"picture": 1, "panels": 4, "width": .92}), (.145, {"band": "meander-saltire"}), (.055, {"solid": 1}), (.022, {"band": "egg"}), (0, {"solid": 1})]},
    "lekythos": {"profile": [[.04, 0], [.042, .008], [.02, .02], [.05, .06], [.052, .2], [.048, .225], [.02, .24], [.012, .275], [.026, .29], [.018, .3]],
                 "zones": [(.235, {"solid": 1}), (.203, {"band": "tongues"}), (.19, {"band": "meander"}), (.068, {"picture": 1, "panels": 1, "at": [.25], "width": .66}), (0, {"solid": 1})]},
    "hydria": {"profile": [[.08, 0], [.085, .012], [.06, .025], [.09, .07], [.145, .17], [.16, .25], [.14, .31], [.08, .355], [.05, .37], [.05, .41], [.08, .43], [.06, .435]],
               "zones": [(.345, {"solid": 1}), (.315, {"band": "tongues"}), (.16, {"picture": 1, "panels": 1, "at": [.25], "width": .56}), (.14, {"band": "meander"}), (0, {"solid": 1})]},
    "kylix": {"profile": [[.055, 0], [.058, .006], [.012, .03], [.012, .055], [.05, .07], [.105, .092], [.132, .124], [.138, .138], [.134, .141]],
              "zones": [(.13, {"solid": 1}), (.086, {"picture": 1, "panels": 2, "width": .84}), (.08, {"band": "meander"}), (0, {"solid": 1})],
              "well": [[.134, .141], [.122, .118], [.07, .09], [0, .082]], "tondo": .135},   # (a shallow bowl, its inside a disc of its own)
}

def fit(key):
    """a pot's painting: its aspect [W, 1] (round the picture's middle : along the whole profile) and its zones as shares"""
    P = rounded(POTS[key]["profile"])
    along, at = [0], 0
    for a, b in zip(P, P[1:]):
        at += math.dist(a, b); along.append(at)
    total = along[-1]
    def on(y):                                    # how far along, and the radius, where the profile first reaches a height
        for i in range(len(P) - 1):
            if P[i + 1][1] >= y:
                t = (y - P[i][1]) / max(P[i + 1][1] - P[i][1], 1e-9)
                return along[i] + (along[i + 1] - along[i]) * t, P[i][0] + (P[i + 1][0] - P[i][0]) * t
        return total, P[-1][0]
    def radius(s):                                # the radius so far along
        for i in range(len(P) - 1):
            if along[i + 1] >= s:
                return P[i][0] + (P[i + 1][0] - P[i][0]) * (s - along[i]) / max(along[i + 1] - along[i], 1e-9)
        return P[-1][0]
    spans, top = [], total
    for y, zone in POTS[key]["zones"]:
        s = on(y)[0]
        spans.append((zone, (top - s) / total, sum(radius(s + (top - s) * (k + .5) / 12) for k in range(12)) / 12)); top = s
    wide = next(r for z, h, r in spans if z.get("picture"))
    W = round(2 * math.pi * wide / total, 3)
    return [W, 1], [{**{k: v for k, v in z.items() if k != "picture"}, "h": round(h, 4), **({"squeeze": round(r / wide, 3)} if z.get("band") else {})} for z, h, r in spans]
