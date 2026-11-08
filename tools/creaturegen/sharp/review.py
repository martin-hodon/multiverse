# review.py NAME... | all : fixes after the review of the second sharp pass (2026-11-08), each a function below that
# rewrites only the shapes concerned (re-reading the file right before it writes) and notes it in the species' `_about`.
# Run from tools/creaturegen/sharp AFTER claws.py / teeth.py / spikes.py / antlers.py / bills.py (it edits their horns).
#   gull       the bill: a straight deep bill whose upper mandible bends down only at the very tip (it had curled back
#              into a "C" round a hole), the lower with its gonys angle; the red gonys spot the lower's own `tip`
#              colour (a field ell it was, left floating under the new horn)
#   duck       the field `culmen` ell (bill-yellow, under the horn's root) removed: it showed as a yellow smear on the face
#   crocodile  the teeth rebuilt on the jaw MARGIN: the uppers out of the upper jaw's lower edge, down and a little out
#              over the outside of the lower jaw; the lowers between them, up over the upper jaw; the enlarged 4th lower in
#              the notch; conical, round, curved slightly back, the roots sunk in the gum and stained toward it
#   claws      (bear and the other claws.py species) the root FAIRED into the toe (horn `fair`: a fillet grown out of the
#              skin in the toe's paint -- the claw comes out from under the fur instead of cutting it in a jagged line)
#   reindeer   the palms (crown, bez, shovel) as flat `fin` sheets with the tines' points along their edges (they were
#              flattened horns: round discs) -- now caribou.py's (it runs that)
#   cockatoo, cockatiel  the hooked bills re-made from one profile (the lower mandible deep and rounded, not a block)
#   pelican    the upper mandible long and flat with only a short nail hooked at its tip (it curled into a "C")
#   dilophosaurus, allosaurus, tyrannosaur  the HANDS: each finger one smooth horn (the field cones' ends and the
#              six-sided finger tubes came out as pale shards round the claws on the coarse grid), the claws out of the
#              rounded fingertips (run after `claws`)
#   pachycephalosaurus  the squamosal knobs short blunt horns (field spheres of 1.5 cells came out as faceted knots)
#   flamingo   the bill's root faired into the face (a hard collar)
import sys, re, math, json
from sharp2 import *
from shp import note

TAG = "(2026-11-08, review.py)"

def edit(sp, fn, about=None, what=None):
    """fn(shapes) -> shapes, on the file as it is now; `about`: a sentence for the species' _about, tagged by `what`
    (a later note of the same tag replaces it)"""
    txt, d = load(sp)
    out = fn([dict(s) for s in d["sculpt"]["shape"]])
    save(sp, out, txt)
    if about: note(sp, TAG[:-1] + (": " + what if what else "") + ")", about)

def put(sh, new):
    """shapes `new` (by id) replacing those of the same id in place (or appended)"""
    by = {s["id"]: s for s in new}; seen = set(); out = []
    for s in sh:
        if s.get("id") in by: out.append(by[s["id"]]); seen.add(s["id"])
        else: out.append(s)
    return out + [s for s in new if s["id"] not in seen]

# ------------------------------------------------------------------------------------------------------------------
def gull():
    sp = "birds/gull"
    # (the commissure runs straight from the gape to the tip; the upper's dome above it, the lower's below: flat=1 each)
    U = [[0.1953, 0.2633, 0, 0.0150, 1.557], [0.2028, 0.2628, 0, 0.0150, 1.557], [0.2254, 0.2615, 0, 0.0118, 1.62],
         [0.2460, 0.2605, 0, 0.0084, 1.6], [0.2590, 0.2599, 0, 0.0066, 1.5], [0.2660, 0.2590, 0, 0.0052, 1.35],
         [0.2700, 0.2568, 0, 0.0034, 1.15], [0.2716, 0.2534, 0, 0.0, 1.0]]
    # (the lower: shallow, deepest again at the gonys angle two thirds along, its tip tucked behind the upper's hook)
    L = [[0.1984, 0.2627, 0, 0.0105, 1.382], [0.2037, 0.2624, 0, 0.0105, 1.382], [0.2297, 0.2609, 0, 0.0070, 1.45],
         [0.2480, 0.2601, 0, 0.0056, 1.85], [0.2585, 0.2596, 0, 0.0040, 1.55], [0.2652, 0.2593, 0, 0.0, 1.4]]
    def fn(sh):
        by = {s["id"]: s for s in sh}
        u = dict(by["upperBill"]); u["pts"] = U
        l = dict(by["lowerBill"]); l["pts"] = L; l["tip"] = "@red"; l["tipAt"] = 0.62
        return [s for s in put(sh, [u, l]) if s.get("id") != "gonys"]
    edit(sp, fn, "The bill: straight and deep, the upper mandible bent down only at its very tip, over the lower's; the "
         "red gonys spot is the lower mandible's own tip colour (`tip`), on it near its end.")

def duck():
    sp = "birds/duck"
    edit(sp, lambda sh: [s for s in sh if s.get("id") != "culmen"],
         "The bill-yellow `culmen` ell under the bill's root removed (it smeared yellow over the face round the horn bill).")

# ------------------------------------------------------------------------------------------------------------------
def dark(sp, col, k=0.55):
    """a colour ("@ref" resolved in the species' palette, or hex) darkened: the claw's base"""
    if isinstance(col, str) and col.startswith("@"):
        txt, d = load(sp); C = d.get("c") or d.get("colors") or {}
        col = C.get(col[1:])
    if not (isinstance(col, str) and col.startswith("#")): return None
    n = int(col[1:], 16); r, g, b = (n >> 16) & 255, (n >> 8) & 255, n & 255
    return "#%02x%02x%02x" % tuple(int(v * k) for v in (r, g, b))

def reroot_claws(sp, rx, fair=0.35, skin=0.15, darken=True):
    """each claw horn `rx` of sp RE-ROOTED where its centreline leaves the toe (found on the body's field): the part
    outside kept, the part inside replaced by a straight sheath as wide as the claw is where it comes out (not wider: a
    wider root showed as a pale bulb), sunk ~2.4 of that radius; the join FAIRED (horn `fair`: a fillet grown out of the
    skin in its paint -- `skin` the share at which it is all skin); and the claw darker at its base (`color` the claw's
    darkened, fading to the claw's own colour, `tip`, from where it comes out) -- the pale cut edge on dark fur gone"""
    txt, d = load(sp)
    H = [s for s in d["sculpt"]["shape"] if s.get("type") == "horn" and re.fullmatch(rx, s.get("id", ""))]
    S = []   # (dense samples along each claw: [x, y, z, r, segment, t])
    for h in H:
        P = h["pts"]; smp = []
        for i in range(len(P) - 1):
            for t in [j / 8 for j in range(8)]: smp.append(lerp(P[i][:4], P[i + 1][:4], t) + [i, t])
        smp.append(list(P[-1][:4]) + [len(P) - 2, 1.0]); S.append(smp)
    D = fd(sp, {"points": [q[:3] for smp in S for q in smp], "exclude": [h["id"] for h in H]})["d"]
    new = {}; k = 0
    for h, smp in zip(H, S):
        dd = D[k:k + len(smp)]; k += len(smp)
        # (where it COMES OUT: its centreline half its radius under the skin -- its surface is out beyond that)
        ex = [v + 0.5 * q[3] for v, q in zip(dd, smp)]
        j = 1 if ex[0] > 0 else next((i for i in range(1, len(smp)) if ex[i] > 0 and ex[i - 1] <= 0), None)
        if j is None: print("  ", h["id"], "no exit found: left"); continue
        a, b = smp[j - 1], smp[j]; t = 0.0 if ex[0] > 0 else ex[j - 1] / (ex[j - 1] - ex[j])   # (a root out already: from it)
        E = lerp(a[:4], b[:4], t); rE = E[3]
        if rE < 0.45 * max(q[3] for q in smp):   # (a claw lying along the skin, only its end out: left as it is)
            print("  ", h["id"], "grazes the skin (out at r %.4f): left" % rE); continue
        P = h["pts"]; seg = b[4] if b[5] > 0 else b[4] - 1
        T = nrm(sub(b[:3], a[:3]))
        rest = [list(p) for p in P[seg + 1:] if ln(sub(p[:3], E[:3])) > 0.5 * rE]
        if not rest: print("  ", h["id"], "nothing outside?"); continue
        ex = [E[4]] if len(P[0]) > 4 else []
        Q = [add(E, T, -2.4 * rE) + [rE * 0.85] + ex, add(E, T, -1.0 * rE) + [rE * 0.97] + ex, E[:3] + [rE] + ex] + rest
        Q = sink(sp, [q for q in Q], [x["id"] for x in H], need=0.7)
        L = sum(ln(sub(Q[i + 1][:3], Q[i][:3])) for i in range(len(Q) - 1)); Lin = sum(ln(sub(Q[i + 1][:3], Q[i][:3])) for i in range(len(Q) - len(rest) - 1))
        g = dict(h); g["pts"] = r5([list(q) for q in Q]); g["fair"] = {"r": round(fair * rE, 4), "skin": skin}
        if darken:
            base = h.get("tip") and h.get("color") or h.get("color")
            dk = dark(sp, base)
            if dk: g["color"] = dk; g["tip"] = base; g["tipAt"] = round(Lin / L, 3)
        new[h["id"]] = g
        print("  ", h["id"], "exit r %.4f at %.0f%% of its length" % (rE, 100 * Lin / L))
    edit(sp, lambda sh: put(sh, list(new.values())),
         "The claws RE-ROOTED (review.py): each a sheath as wide as the claw where it leaves the toe, sunk in it, the join "
         "faired (horn `fair`: grown out of the skin in its paint), darker at the base fading to its own colour at the "
         "point -- no pale cut edge where it leaves the fur.", "claws")

# per species: (horn ids, options)
CLAWS = {
    "mammals/bear": (r"h?claw\d", {}), "mammals/badger": (r"h?claw\d", {}), "mammals/hyena": (r"[fh]claw\d", {}),
    "mammals/giantpanda": (r"claw\d", {}), "mammals/redpanda": (r"claw\d", {}), "mammals/skunk": (r"claw\d", {}),
    "mammals/porcupine": (r"h?claw\d", {}), "mammals/anteater": (r"claw\d|nail\d", {}), "mammals/pangolin": (r"claw\d|nail\d", {}),
    "others/turtle": (r"claw[FH]\d", {}), "sea/seal": (r"[fh]claw\d", {}), "monsters/hydra": (r"claw[FH]\d", {}),
    "dinosaurs/allosaurus": (r"claw\d", {}), "dinosaurs/dilophosaurus": (r"claw\d", {}), "dinosaurs/carnotaurus": (r"claw\d", {}),
    "dinosaurs/tyrannosaur": (r"f?claw\d", {}), "dinosaurs/diplodocus": (r"claw\d", {}),
    "dinosaurs/pteranodon": (r"toeClaw\d|wDig[ABC]Claw", {}),
    # (birds: the talons stay their own colour -- black on a yellow foot is right)
    "birds/eagle": (r"claw\d", {"darken": False}), "birds/hornbill": (r"claw\d", {"darken": False}), "birds/parrot": (r"claw\d", {"darken": False}),
    "birds/buzzard": (r"talon", {"darken": False}), "birds/falcon": (r"talon", {"darken": False}), "birds/owl": (r"talon", {"darken": False}),
}

# ------------------------------------------------------------------------------------------------------------------
def crocodile():
    """the teeth on the jaw margin (the slit at y .241 where the jaws shut, flush outside): each a cone out of its jaw
    just by the slit, standing a radius off the other jaw's outer face, a slight backward curve, stained toward the gum"""
    sp = "others/crocodile"; Y0 = 0.241
    UP = [(1.00, .022, .0060), (1.065, .024, .0064), (1.13, .025, .0066), (1.19, .024, .0064), (1.24, .022, .0060),
          (1.295, .028, .0074), (1.34, .020, .0056)]
    LO = [(1.033, .021, .0058), (1.098, .022, .0060), (1.16, .022, .0060), (1.265, .040, .0090), (1.318, .020, .0056)]
    # (each tooth's points as (dy from the slit, dz from the face there, dx, r share), the sign of dy flipped for a lower)
    # (the root up and in through the jaw's face just above the slit at ~45 degrees -- a gum faired round it -- the
    #  crown down and a little out, standing clear of the other jaw's face, its tip just touching it)
    PROF = [(.012, -.012, 0, .9), (.004, -.002, 0, 1.0), (-.003, None, 0, .95), (-.45, None, .002, .68), (-.8, None, .0005, .32), (-1.0, .003, -.002, 0.0)]
    jobs = [("toothU%d" % i, "head", x, L, r, 1) for i, (x, L, r) in enumerate(UP)] + [("toothL%d" % i, "jaw", x, L, r, -1) for i, (x, L, r) in enumerate(LO)]
    # (the first three dy in metres -- the root in the jaw, out at the slit -- the rest shares of the tooth's length)
    def ys(L, sg): return [Y0 + sg * (dy if k < 3 else dy * L) for k, (dy, dz, dx, rs) in enumerate(PROF)]
    rays = []
    for _, _, x, L, r, sg in jobs:
        for y in ys(L, sg) + [Y0 + .005, Y0 - .005]: rays.append([[x, y, 0.25], [x, y, 0.0]])
    H = fd(sp, {"rays": rays, "exclude": [j[0] for j in jobs]})["hits"]
    new = []; k = 0; n = len(PROF) + 2
    for tid, bone, x, L, r0, sg in jobs:
        P = []; hz = [h[2] for h in H[k:k + n]]; k += n
        hz[2] = max(hz[-2:])   # (out at the slit: the jaws' face either side of it, not the slit's floor)
        for j, ((dy, dz, dx, rs), y) in enumerate(zip(PROF, ys(L, sg))):
            s = hz[j]
            r = r0 * rs
            z = s + (dz if dz is not None else r0 * (0.9 if rs > .9 else 1.4 if rs > .5 else 1.1))
            P.append([round(x + dx, 4), round(y, 4), round(z, 4), round(r, 4)])
        new.append({"id": tid, "type": "horn", "bone": bone, "pts": P, "color": "#a08c66", "tip": "@tooth", "tipAt": 0.35,
                    "mirror": True, "up": [1, 0, 0], "sides": 12, "fair": {"r": 0.0025, "skin": 0.2}})
    def fn(sh):
        idx = [i for i, s in enumerate(sh) if re.fullmatch(r"tooth[UL]\d+", s.get("id", ""))]
        return sh[:idx[0]] + new + [s for i, s in enumerate(sh) if i > idx[0] and i not in idx]
    edit(sp, fn, "The TEETH stand on the jaw margin (the slit where the jaws shut): each upper a cone out of the upper jaw by "
         "the slit, standing a little out from the lower jaw's outer face; the lowers between them, up over the upper jaw; the "
         "enlarged 4th lower in the notch behind the rosette; round, curved slightly back, the root faired into a gum "
         "(horn `fair`), stained toward it.", "teeth")

# ------------------------------------------------------------------------------------------------------------------
def palm_fin(s, tines, fc=0.8, reach=2.3, notch=0.62, flank=1.25, thick=0.012, b=1.6):
    """a reindeer's PALM (a flat horn: its plane the one square to its `up`) as a `fin` SHEET spanning the tines that
    grow out of it: its rim runs out along each tine to a CORNER fc of the way along it (the tine, a round horn, carries
    the point on), dips to a rounded NOTCH between neighbouring tines (notch x the nearer corner's reach from the palm's
    middle), swells over the flanks where no tine is, and is rooted across the beam / tine it grows from"""
    P = s["pts"]; O = P[0][:3]; Ct = P[-1][:3]
    a = nrm(sub(Ct, O)); Lh = ln(sub(Ct, O))
    up = s.get("up", [0, 1, 0]); n = nrm(sub(up, mul(a, dot(up, a)))); e2 = nrm(crs(n, a))
    C = add(O, a, 0.5 * Lh)
    to2 = lambda p: (dot(sub(p, C), a), dot(sub(p, C), e2))
    to3 = lambda u, v: add(add(C, a, u), e2, v)
    rmax = max(p[3] for p in P)
    cs = []
    Rc = reach * rmax
    for t in tines:
        # (the corner: where the tine first gets `reach` palm radii from the palm's middle -- else fc of the way out)
        T = t["pts"]; dense = [lerp(T[i][:3], T[i + 1][:3], k / 10) for i in range(len(T) - 1) for k in range(10)] + [T[-1][:3]]
        p = next((q for q in dense if ln(sub(q, C)) >= Rc), dense[int(fc * (len(dense) - 1))])
        u, v = to2(p)
        cs.append((math.atan2(v, u), math.hypot(u, v)))
    cs.sort()
    rr = 1.1 * max(P[0][3], P[1][3])
    r0, r1 = add(O, e2, -rr), add(O, e2, rr)
    edge, corners = [], []
    th0 = math.atan2(*reversed(to2(r0))); th1 = math.atan2(*reversed(to2(r1)))
    R = rmax * flank
    if cs[0][0] - th0 > 1.6: edge.append(to3(R * math.cos(-math.pi / 2), R * math.sin(-math.pi / 2)) + [b])
    for k, (th, rad) in enumerate(cs):
        if k:
            tm = (cs[k - 1][0] + th) / 2; rm = notch * min(cs[k - 1][1], rad)
            edge.append(to3(rm * math.cos(tm), rm * math.sin(tm)) + [b * 0.9])
        corners.append(len(edge)); edge.append(to3(rad * math.cos(th), rad * math.sin(th)) + [1.0])
    if th1 - cs[-1][0] > 1.6: edge.append(to3(R * math.cos(math.pi / 2), R * math.sin(math.pi / 2)) + [b])
    f = {"id": s["id"], "type": "fin", "bone": s.get("bone", "head"), "root": [r0, O, r1], "edge": edge, "corners": corners,
         "thick": thick, "slope": 0.3, "color": s.get("color"), "n": 44, "across": 6}
    for kk in ("mirror", "when"):
        if kk in s: f[kk] = s[kk]
    return r5(f)

# (the palms as antlers.py made them: flat horns -- kept here so this runs again on a file it has already changed)
PALM_HORNS = {"crown": {"id": "crown", "type": "horn", "bone": "head", "pts": [[0.9068, 2.5023, 0.4631, 0.0112], [0.9117, 2.5113, 0.4612, 0.0238], [0.9215, 2.5293, 0.4573, 0.0337], [0.93, 2.545, 0.454, 0.036], [0.9398, 2.563, 0.4502, 0.033], [0.9483, 2.5787, 0.4468, 0.0238], [0.9525, 2.5863, 0.4452, 0.0141], [0.9544, 2.5899, 0.4445, 0.0]], "color": "#a89474", "up": [0.0, 0.2079, 0.9781], "when": "bull", "mirror": True}, "bezPalm": {"id": "bezPalm", "type": "horn", "bone": "head", "pts": [[0.9311, 1.8151, 0.1858, 0.0116], [0.9403, 1.8176, 0.1871, 0.0245], [0.9586, 1.8226, 0.1896, 0.0347], [0.9747, 1.8269, 0.1919, 0.037], [0.9931, 1.8319, 0.1945, 0.0339], [1.0091, 1.8362, 0.1967, 0.0245], [1.0169, 1.8383, 0.1978, 0.0145], [1.0206, 1.8393, 0.1984, 0.0]], "color": "#a89474", "up": [-0.1392, -0.0, 0.9903], "when": "bull", "mirror": True}, "shovelLeaf": {"id": "shovelLeaf", "type": "horn", "bone": "head", "pts": [[0.963, 1.6455, -0.0124, 0.0133], [0.9815, 1.6357, -0.0124, 0.0282], [1.0184, 1.6161, -0.0124, 0.04], [1.0507, 1.5989, -0.0124, 0.0427], [1.0876, 1.5793, -0.0124, 0.0391], [1.1199, 1.5621, -0.0124, 0.0282], [1.1356, 1.5538, -0.0124, 0.0167], [1.143, 1.5498, -0.0124, 0.0]], "color": "#a89474", "up": [0.0, -0.0, 1.0], "when": "bull"}}

def reindeer():
    # (superseded 2026-11-08 by caribou.py, which rebuilds the whole antler -- beam, palms, tines -- from its own
    #  frozen courses; what follows is the earlier palm pass, kept for the record)
    import caribou; return caribou.main()
    sp = "mammals/reindeer"
    # (each palm: its tines, how far out its points reach and how far its flanks swell, in palm radii)
    PALMS = {"crown": (["topT0", "topT1", "topT2"], 3.2, 1.6), "bezPalm": (["bezP0", "bezP1"], 2.6, 1.35),
             "shovelLeaf": (["shovelPt0", "shovelPt1"], 2.3, 1.25)}
    def fn(sh):
        by = {s["id"]: s for s in sh}
        return put(sh, [palm_fin(PALM_HORNS[pid], [by[t] for t in ts], reach=rc, flank=fl) for pid, (ts, rc, fl) in PALMS.items()])
    edit(sp, fn, "The PALMS (the crown, the bez palm, the shovel) are flat `fin` sheets spanning the tines that grow out "
         "of them: broad, irregular, the rim running out along each tine to a point and dipping between them (they were "
         "flat horns, round discs).", "palms")
# ------------------------------------------------------------------------------------------------------------------
# HOOKED BILLS whose converted upper curled back into a "C" round a hole (the old tube's knob turned back under the
# needle). The PARROT's came out right (its hook ends a little below and before the lower's tip, the lower fitting into
# its curve): the cockatoo's and cockatiel's are the parrot's two mandibles scaled onto their own roots; the pelican's
# a long flat upper with a short nail bent down at its very end, the lower run on to just behind it.
PARROT_U = [(0, 0, .02, 1.87), (.0098, -.0019, .02, 1.87), (.0242, -.0048, .018, 2.0), (.0365, -.0108, .013, 2.14),
            (.0444, -.0231, .008, 2.17), (.0461, -.037, .003, 1.6), (.0464, -.0404, 0, 1.5)]
PARROT_L = [(0, 0, .015, 1.6), (.0071, -.0025, .015, 1.6), (.0245, -.0085, .011, 1.8), (.033, -.0164, .006, 1.9),
            (.0369, -.0246, 0, 1.9)]

def scaled(prof, o, sx, sy, sr, asp=1.0):
    return [[round(o[0] + x * sx, 5), round(o[1] + y * sy, 5), 0, round(r * sr, 5), round(a * asp, 3)] for x, y, r, a in prof]

def parrotbill(sp, sx, sy, sru, srl, aspu=1.0, aspl=1.0, what="bill"):
    def fn(sh):
        by = {s["id"]: s for s in sh}
        u = dict(by["upperBill"]); l = dict(by["lowerBill"])
        u["pts"] = scaled(PARROT_U, u["pts"][0], sx, sy, sru, aspu); u["up"] = [0.214, 0.977, 0]
        l["pts"] = scaled(PARROT_L, l["pts"][0], sx, sy, srl, aspl); l["up"] = [-0.38, -0.925, 0]
        return put(sh, [u, l])
    edit(sp, fn, "The bill: the parrot's two mandibles scaled onto this one's roots -- the upper's hook bent down to end "
         "a little below and before the lower's tip (it curled back into a C round a hole), the lower a deep scoop "
         "fitting into its curve (it was a block).", what)

def cockatoo(): parrotbill("birds/cockatoo", .65, .75, .525, .7, 1.2, 0.9)
def cockatiel(): parrotbill("birds/cockatiel", .183, .235, .18, .227, 1.1, 0.9)

def pelican():
    sp = "birds/pelican"
    U = [[0.4619, 0.9184, 0, 0.033, 1.0], [0.4793, 0.916, 0, 0.033, 1.0], [0.6339, 0.8947, 0, 0.026, 0.75],
         [0.789, 0.8751, 0, 0.019, 0.7], [0.88, 0.864, 0, 0.016, 0.75], [0.915, 0.8595, 0, 0.012, 0.9],
         [0.932, 0.853, 0, 0.0075, 1.1], [0.9395, 0.845, 0, 0.0035, 1.2], [0.9415, 0.8385, 0, 0.0, 1.2]]
    L = [[0.4694, 0.9169, 0, 0.0246, 1.186], [0.4815, 0.9152, 0, 0.0246, 1.186], [0.659, 0.891, 0, 0.0168, 1.0],
         [0.80, 0.873, 0, 0.0125, 0.8], [0.89, 0.8622, 0, 0.0095, 0.8], [0.922, 0.8578, 0, 0.0, 0.8]]
    def fn(sh):
        by = {s["id"]: s for s in sh}
        u = dict(by["upperBill"]); u["pts"] = U
        l = dict(by["lowerBill"]); l["pts"] = L
        return put(sh, [u, l])
    edit(sp, fn, "The bill: a long flat upper mandible ending in a short nail bent down at its very tip (it curled back "
         "into a C), the lower run on to just behind the nail.", "bill")

# ------------------------------------------------------------------------------------------------------------------
def horn_fingers(sp, n, claw="fclaw%d", finger="finger%d", tube="ffinger%d"):
    """a theropod's HAND: each finger (a field cone out of the hand, and on the smaller ones a thin tube on to the
    claw) re-made as one smooth HORN -- on the coarse grid (3-4 cm cells for fingers 2-5 cm thick) the cone's end was a
    blocky knot and the tube a six-sided lathe, whose pale facets stuck out round the claw's root as ragged shards (and
    a claw sheathed over them came out bulky). The finger: from inside the hand (faired into it) through the cone's and
    the tube's ends to a ROUNDED fingertip, its point buried in the claw. The claw: rooted inside that fingertip, 0.72
    of its girth where it comes out, along its old hook to the point, no `fair` (the fingertip is not the field)"""
    def fn(sh):
        by = {s["id"]: s for s in sh}; new = []; drop = set()
        for i in range(n):
            f = by[finger % i]; c = dict(by[claw % i]); t = by.get(tube % i)
            if f["type"] == "horn":   # (run before: the finger horn's own points give back its cone and tube ends)
                P = f["pts"]; a, b, ra, rb = P[1][:3], P[2][:3], P[1][3], P[2][3]
                C = [(a, ra), (b, rb)] + ([(P[3][:3], P[3][3])] if len(P) == 6 else [])
                d0 = nrm(sub(b, a)); E, rE = C[-1]; dE = nrm(sub(E, C[-2][0]))
            else:
                a, b, ra, rb = f["a"], f["b"], f["ra"], f["rb"]
                C = [(a, ra), (b, rb)] + ([(t["pts"][-1][:3], t["pts"][-1][3])] if t else [])
                if t: drop.add(t["id"])
                d0 = nrm(sub(b, a)); E, rE = C[-1]; dE = nrm(sub(E, C[-2][0]))
                pts = [add(a, d0, -0.6 * ra) + [0.9 * ra]] + [p + [r] for p, r in C] + [add(E, dE, 0.5 * rE) + [0.8 * rE], add(E, dE, 0.9 * rE) + [0.0]]
                g = {"id": f["id"], "type": "horn", "bone": f.get("bone", "body"), "pts": r5(pts), "color": f.get("color", "@body"),
                     "up": r5(nrm(crs(d0, [0, 0, 1]))), "fair": {"r": round(0.25 * ra, 4), "skin": 0.3}}
                for k in ("mirror", "pat"):
                    if k in f: g[k] = f[k]
                new.append(g)
            hook = [p[:3] for p in c["pts"] if dot(sub(p[:3], E), dE) > 0.3 * rE]   # (the claw's own course past the fingertip)
            L = ln(sub(hook[0], E)) + sum(ln(sub(hook[k + 1], hook[k])) for k in range(len(hook) - 1))
            s, Q = 0.0, []
            for k, p in enumerate(hook):
                s += ln(sub(p, hook[k - 1] if k else E))
                Q.append(p + [0.0 if k == len(hook) - 1 else 0.72 * rE * (1 - s / L) ** 0.8])
            # (its root carried back inside the finger to the hand, thin, hidden -- so it is held by the body, not only by the finger)
            back = [a + [0.4 * ra]] + ([b + [0.45 * rb]] if len(C) == 3 else [])
            c["pts"] = r5(back + [add(E, dE, -rE) + [0.55 * rE], E + [0.72 * rE]] + Q); c.pop("fair", None)
            new.append(c)
        return [s for s in put(sh, new) if s.get("id") not in drop]
    edit(sp, fn, "The HAND: each finger one smooth horn (faired into the hand, a rounded fingertip) instead of a field cone "
         "and a six-sided tube that came out as blocky shards on the coarse grid round the claws' roots; the claws come out "
         "of the fingertips, 0.72 of their girth, along their old hooks (no fillet).", "hand claws")

def knuckle_fingers(sp, n, claw="fclaw%d", finger="finger%d", grow=1.08):
    """(2026-11-08, after horn_fingers) the theropod fingers read as SAUSAGES: a fat smooth plain-coloured tube from the
    hand to a round end, a claw thinner than it poking out. Now each finger (its horn's own points give back the hand
    end `a` and the fingertip E) is slimmer at the hand (at most 1.45 of its tip), swells at two KNUCKLES (30% and 72%
    of the way) and narrows between them, wears the arm's scales (`pat` scales: a horn with a pattern takes the nearest
    field shape's frame -- bodymesh.js), and ends IN its claw: the claw's base `grow` of the fingertip's girth (it was
    .72), a sheath over the finger's end, the hook tapering from there to the point (at .92 the claw's base and the
    finger's rounded end crossed at a grazing angle: a ragged line; a little wider than the finger it is a clean rim)"""
    def fn(sh):
        by = {s["id"]: s for s in sh}; new = []
        for i in range(n):
            f = dict(by[finger % i]); c = dict(by[claw % i])
            P = f["pts"]
            done = bool(f.get("pat"))   # (done already: a patterned finger -- only its claw's base is (re)set below)
            # (the hand end, then the cone's end and the tube's end: E the last; a knuckled finger's E is 3rd from its end)
            C = [P[1], P[len(P) - 3]] if done else [P[1]] + P[2:len(P) - 2]
            E, rE = C[-1][:3], C[-1][3]; a = C[0][:3]
            ra = min(C[0][3], 1.45 * rE)
            seg = [ln(sub(C[k + 1][:3], C[k][:3])) for k in range(len(C) - 1)]; L = sum(seg)
            def at(s):   # (a point s of the way along the finger's polyline)
                t = s * L
                for k, l in enumerate(seg):
                    if t <= l or k == len(seg) - 1: return lerp(C[k][:3], C[k + 1][:3], min(1.0, t / (l or 1)))
                    t -= l
            prof = [(0.0, 1.0), (0.3, 1.1), (0.5, 0.94), (0.72, 1.09), (0.88, 0.97), (1.0, 1.0)]
            Q = [list(P[0][:3]) + [min(P[0][3], 0.95 * ra)]]
            for s, k in prof:
                Q.append(at(s) + [(ra + (rE - ra) * s) * k])
            dE = nrm(sub(E, C[-2][:3]))
            Q += [add(E, dE, 0.5 * rE) + [0.8 * rE], add(E, dE, 0.9 * rE) + [0.0]]
            if not done: f["pts"] = r5(Q); f["pat"] = "scales"
            # (the claw: from E on, its radii scaled to start at `grow` of the fingertip, ROUND there (aspect 1 at E, 1.15
            # the station after, the claw's own beyond); its old long root inside the finger replaced: a little behind E
            # it has that girth, a clean RIM round the finger -- the claw's base crossing the finger's rounded end at a
            # grazing angle drew a ragged, sawtoothed line)
            cp = c["pts"]; j = min(range(len(cp)), key=lambda k: ln(sub(cp[k][:3], E)))
            g = grow * rE / (cp[j][3] or 1e-6)
            asp = {j: 1.0, j + 1: min(1.15, c.get("aspect", 1))}
            tail = [list(p[:3]) + [p[3] * g] + ([asp[k]] if k in asp else list(p[4:])) for k, p in enumerate(cp) if k >= j]
            dE = nrm(sub(E, C[-2][:3]))
            # (and its ROOT a thin rod (half the tip's girth) up the finger's own centreline from the hand, inside the
            #  body, as the old claw's was -- rooted in the body, not a cap stuck on the finger; rising steeply (in a third of
            #  the tip's radius) to the rim's girth it crosses the finger's surface cleanly, just behind E)
            FP = f["pts"] if done else r5(Q)
            c["pts"] = r5([FP[1][:3] + [0.5 * rE, 1.0], FP[3][:3] + [0.5 * rE, 1.0], add(E, dE, -0.65 * rE) + [0.5 * rE, 1.0],
                           add(E, dE, -0.3 * rE) + [grow * rE, 1.0]] + tail)
            new += [f, c]
        return put(sh, new)
    edit(sp, fn, "The FINGERS (review.py knuckle_fingers): slimmer, two knuckles swelling along each, the arm's scales on "
         "them, each running into its claw -- the claw's base nearly the fingertip's girth and round, a sheath the finger "
         "ends in (they read as smooth sausages with a thin claw poking out).", "fingers")

def crocodile_lip():
    """(2026-11-08) the JAW LINE made visible where the teeth are: the `lipCut` groove and the dark `lip` along the slit
    lay 2-4 cm INSIDE the snout (z .04-.07, written for an older, narrower jaw), so no line showed and the teeth, set on
    the jaw's real margin (crocodile() above, by rays), seemed to stand on the side of the face. Each of their points is
    moved out onto the face at the slit (a ray in from the side, the teeth and the two tubes excluded): the groove's
    centre just under the skin, the lip a thin dark ridge over it"""
    sp = "others/crocodile"
    txt, d = load(sp); by = {s["id"]: s for s in d["sculpt"]["shape"]}
    ex = ["lip", "lipCut"] + [s["id"] for s in d["sculpt"]["shape"] if re.fullmatch(r"tooth[UL]\d+", s.get("id", ""))]
    # (the face either side of the slit -- the slit's own floor lies deeper: the jaws' outer faces, as the teeth were set)
    rays = [[[p[0], p[1] + dy, 0.25], [p[0], p[1] + dy, 0.0]] for k in ("lipCut", "lip") for p in by[k]["pts"] for dy in (0.006, -0.006)]
    H0 = fd(sp, {"rays": rays, "exclude": ex})["hits"]
    H = [max(H0[2 * i], H0[2 * i + 1], key=lambda h: h[2]) for i in range(len(H0) // 2)]
    def fn(sh):
        out = []; k = 0
        for s in sh:
            if s.get("id") in ("lipCut", "lip"):
                s = dict(s); P = []
                for p in s["pts"]:
                    hz = H[k][2]; k += 1
                    P.append([p[0], p[1], round(hz - (0.002 if s["id"] == "lipCut" else 0.0065), 4), p[3]])
                s["pts"] = P
            out.append(s)
        return out
    edit(sp, fn, "The JAW LINE shows where the teeth stand: the groove (`lipCut`) and the dark lip along the slit moved out "
         "onto the face (they lay inside the snout, written for a narrower jaw, so no line showed and the teeth seemed to "
         "stand up the side of the face).", "jaw line")

def anteater_claws():
    """the giant anteater's FORE CLAWS: the 2nd and 3rd digits' long curved digging claws -- out of the top of the fist's
    front, arching forward and down round it and curling back under it toward the ground (it walks on its knuckles, the
    claws folded); laterally compressed (aspect 2: deep, narrow), the 3rd ~11 cm, the 2nd three quarters of it; the root
    faired into the fist, dark at the base. They were short flat 4 cm hooks pointing at the ground"""
    sp = "mammals/anteater"
    # (the 3rd digit's curve in (x, y), the fist's front at x ~.387, its top y ~.07, the ground y 0; z per claw)
    # (hugging the fist: at most ~1.5 cm proud of its front -- reaching 3.6 cm out they stood off it like ram's horns)
    CUR = [(0.352, 0.052, 0.0066), (0.372, 0.062, 0.0070), (0.389, 0.062, 0.0068), (0.399, 0.054, 0.0062), (0.404, 0.040, 0.0054),
           (0.403, 0.025, 0.0044), (0.397, 0.012, 0.0031), (0.390, 0.005, 0.0017), (0.383, 0.003, 0.0)]
    def claw(id, z, sc, base):
        x0, y0 = CUR[1][0], CUR[1][1]
        pts = [[round(x0 + (x - x0) * sc, 4), round(y0 + (y - y0) * sc if k else y, 4), z, round(r * (0.85 + 0.15 * sc), 4)] for k, (x, y, r) in enumerate(CUR)]
        pts[-1][1] = max(pts[-1][1], 0.003)
        return dict(base, id=id, pts=pts, up=[-0.3, 0.95, 0.0], aspect=2.0, fair={"r": 0.003, "skin": 0.15}, tipAt=0.25)
    def fn(sh):
        by = {s["id"]: s for s in sh}
        return put(sh, [claw("claw1", 0.095, 1.0, by["claw1"]), claw("claw0", 0.076, 0.75, by["claw0"])])
    edit(sp, fn, "The FORE CLAWS (review.py anteater_claws): the 2nd and 3rd digits' long curved digging claws, ~11 cm and "
         "three quarters of that, arching out of the top of the fist's front, down round it close to it and curling back under it "
         "toward the ground (folded, as it walks on its knuckles); deep and narrow (aspect 2), dark at the base.", "fore claws")

def dilophosaurus(): horn_fingers("dinosaurs/dilophosaurus", 3)
def allosaurus(): horn_fingers("dinosaurs/allosaurus", 3)
def tyrannosaur(): horn_fingers("dinosaurs/tyrannosaur", 2)

def pachycephalosaurus():
    """the squamosal KNOBS (field spheres of 1.3-1.6 cells: on the 2.8 cm grid each came out a knot of flat facets, and
    the spikes among them looked faceted with them) re-made as short blunt horns: their axis the head's own normal there
    (the field without them), rising about their radius out of the skin, faired into it"""
    sp = "dinosaurs/pachycephalosaurus"
    txt, d = load(sp); K = [s for s in d["sculpt"]["shape"] if re.fullmatch(r"knob\d", s.get("id", ""))]
    if not K: return
    e = 0.004; req = []
    for s in K:
        c = s["c"]; req += [c] + [[c[0] + e * (k == 0) * g, c[1] + e * (k == 1) * g, c[2] + e * (k == 2) * g] for k in range(3) for g in (1, -1)]
    D = fd(sp, {"points": req, "exclude": [s["id"] for s in K]})["d"]
    new = []
    for i, s in enumerate(K):
        q = D[7 * i:7 * i + 7]; n = nrm([(q[1 + 2 * k] - q[2 + 2 * k]) / (2 * e) for k in range(3)])
        r = s["r"]; S = add(s["c"], n, -q[0])                      # (the skin under the knob's centre)
        P = [(-0.8, 0.85), (0.0, 0.9), (0.45, 0.72), (0.8, 0.4), (0.97, 0.0)]
        h = {"id": s["id"], "type": "horn", "bone": s.get("bone", "head"), "pts": r5([add(S, n, a * r) + [b * r] for a, b in P]),
             "color": s.get("color", "@knob"), "up": r5(nrm(crs(n, [0, 0, 1]) if abs(n[2]) < .9 else crs(n, [1, 0, 0]))),
             "sides": 16, "fair": {"r": round(0.3 * r, 4), "skin": 0.3}}
        if s.get("mirror"): h["mirror"] = True
        new.append(h)
    edit(sp, lambda sh: put(sh, new), "The squamosal KNOBS are short blunt horns (sides 16) out of the skin along its normal, "
         "faired into it -- as field spheres only 1.5 grid cells across they came out as knots of flat facets.", "knobs")

def flamingo():
    """the bill's ROOT faired into the face (its root end stood as a hard-edged collar round the skull's front)"""
    def fn(sh):
        out = []
        for s in sh:
            if s.get("id") in ("billA", "lowerBill"): s = dict(s); s["fair"] = {"r": 0.007, "skin": 0.3}
            out.append(s)
        return out
    edit("birds/flamingo", fn, "The bill's root is faired into the face (horn `fair`): no hard collar where it leaves the skull.", "bill root")

NAMES = {"knuckles": lambda: [knuckle_fingers("dinosaurs/tyrannosaur", 2), knuckle_fingers("dinosaurs/allosaurus", 3), knuckle_fingers("dinosaurs/dilophosaurus", 3)],
         "anteater_claws": anteater_claws, "crocodile_lip": crocodile_lip, "gull": gull, "duck": duck, "crocodile": crocodile, "reindeer": reindeer, "cockatoo": cockatoo, "cockatiel": cockatiel, "pelican": pelican, "dilophosaurus": dilophosaurus, "allosaurus": allosaurus, "tyrannosaur": tyrannosaur, "pachycephalosaurus": pachycephalosaurus, "flamingo": flamingo}

if __name__ == "__main__":
    for a in sys.argv[1:]:
        if a in NAMES: NAMES[a]()
        elif a == "claws":
            for sp, (rx, kw) in CLAWS.items(): print(sp); reroot_claws(sp, rx, **kw)
        elif a.startswith("claws:"):
            sp = a.split(":", 1)[1]; reroot_claws(sp, CLAWS[sp][0], **CLAWS[sp][1])
        else: raise SystemExit("unknown " + a)
