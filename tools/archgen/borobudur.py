# BOROBUDUR, Central Java (c. 780-830, the Shailendra kings), in grey andesite: the greatest Buddhist monument, a
# mountain of stone climbed as a path to awakening. On a broad foot (the hidden foot, its reliefs of the world of desire
# buried under the encasement) rise FIVE SQUARE TERRACES, each redented in ever more offsets toward its middle -- the
# world of forms -- their galleries walled in by balustrades of niches, each niche with a Buddha in it and a little
# stupa over it, the gallery's inner side the next terrace's wall, so the pilgrim walking round sees only stone and
# sky. Over them THREE ROUND TERRACES -- the formless world -- open, ringed by 72 PERFORATED STUPAS (32, 24, 16), a
# Buddha seated in each behind the lattice, and in the middle the GREAT STUPA, closed, the summit.
#   The plan is the site's (the survey's outlines, made symmetric): the terraces' redents, the stair projections in
# the middle of every side; the stairs climb straight up the four axes, each flight cut into the terrace it climbs
# (a notch in that terrace's outline: the flight stands in the notch, the balustrade broken over it), steep as on site,
# with a gallery's width to stand on between one flight's head and the next one's foot.
#   Every terrace is a prism from the ground up (their overlaps one stone); each balustrade an enclosure on its
# terrace's edge, its niches openings in it; the stupas a lotus cushion, a BELL (dome.js bell profile: a skirt
# flaring out to the cushion, a level crown), the square harmika on it and the spire.
#   East is +x, south is +z; the main stair is the east one. Numbers are worked here and written as numbers.
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from statuary import statue, FACE_PZ, FACE_NZ, FACE_PX, FACE_NX
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
r4 = lambda v: round(v, 4)

# ---- the measures -----------------------------------------------------------------------------------------------
# each square terrace from its middle line out: [(t, d), ...] -- `d` the face's distance out while the side runs to `t`
# (along it, from the axis), the last step the corner (t = d). The first step is the stair projection.
RUN, RISE = 0.22, 0.28                     # the stairs: steep, as the pilgrims find them
W = 2.4                                    # a square terrace's stair across
WR = 1.6                                   # a round terrace's
TERRACES = [                               # (name, top, profile)
    ("foot",      4.0, [(24.5, 60.0), (42.0, 57.0), (54.5, 54.5)]),
    ("terrace 1", 7.0, [(13.3, 52.8), (30.0, 45.7), (43.0, 43.0)]),
    ("terrace 2", 11.0, [(9.5, 48.1), (26.0, 42.2), (39.3, 39.3)]),
    ("terrace 3", 14.0, [(5.6, 42.7), (22.1, 38.4), (35.3, 35.3)]),
    ("terrace 4", 17.0, [(2.5, 38.0), (18.0, 34.5), (31.6, 31.6)]),
    ("terrace 5", 20.0, [(14.6, 30.4), (27.2, 27.2)]),
]
ROUND = [("round terrace 1", 22.0, 26.0), ("round terrace 2", 24.0, 20.0), ("round terrace 3", 26.0, 13.3)]
BH, BT = 2.0, 0.7                          # the balustrades: high and thick
SIDES = [0, math.pi / 2, math.pi, 3 * math.pi / 2]   # the four sides, by the angle of their axis from +z toward +x

def frame(phi, lat, rad):
    """a point `lat` along a side (increasing in planPoints' winding) and `rad` out from the middle, on the side whose axis
    is `phi` from +z"""
    return [r4(rad * math.sin(phi) + lat * math.cos(phi)), r4(rad * math.cos(phi) - lat * math.sin(phi))]

def flight_steps(h): return max(1, round(h / RISE))

def square_outline(prof, notch=None):
    """the terrace's outline in planPoints' kept winding (south side going +x first), its corners where the profile
    says; `notch` (width, depth): the slot in the middle of every side a flight stands in"""
    half = []
    if notch:
        w, n = notch
        half += [(w / 2, prof[0][1] - n), (w / 2, prof[0][1])]
    for i, (t, d) in enumerate(prof[:-1]):
        half += [(t, d), (t, prof[i + 1][1])]
    side = [(-t, d) for t, d in reversed(half)] + half              # (the corner point ends the side: the next one starts there)
    side = side[:-1]
    out = []
    for phi in SIDES:
        out += [frame(phi, t, d) for t, d in side]
    return out

def round_outline(r, notch, segs=64):
    """a round terrace's outline, a notch in it on every axis"""
    w, n = notch
    a = math.asin(w / 2 / r); s = math.sqrt(r * r - w * w / 4)
    out = []
    for q, phi in enumerate(SIDES):
        out += [frame(phi, -w / 2, s), frame(phi, -w / 2, r - n), frame(phi, w / 2, r - n), frame(phi, w / 2, s)]
        k0 = phi + a; k1 = phi + math.pi / 2 - a
        m = max(1, round((k1 - k0) / (2 * math.pi / segs)))
        for j in range(1, m):
            th = k0 + (k1 - k0) * j / m
            out.append([r4(r * math.sin(th)), r4(r * math.cos(th))])
    return out

def flights(name, base, top, D, w, about):
    """four flights up the axes from `base` to `top`, each standing in the notch of the terrace it climbs (that terrace's
    face `D` out): its foot at the face, its head inside. (A flight climbs its local +x, `width` across local -z..0.)"""
    n = flight_steps(top - base); q = math.pi / 2
    at = [[r4(w / 2), 0, D, q], [D, 0, r4(-w / 2), math.pi], [r4(-w / 2), 0, -D, -q], [-D, 0, r4(w / 2), 0]]
    add(name, {"type": "flight", "width": w, "run": RUN, "rise": r4((top - base) / n), "base": base, "top": top, "landing": 0,
               "steep": True, "at": at, "_about": about})
    return n * RUN

# ---- the terraces and the stairs up them -----------------------------------------------------------------------
prev = 0.0
for i, (name, top, prof) in enumerate(TERRACES):
    L = flight_steps(top - prev) * RUN
    add(name, {"type": "prism", "plan": {"points": square_outline(prof, (W, L))}, "height": top, "walked": True, "at": [[0, 0, 0, 0]],
               "_about": ["the foot: the broad base the monument stands on (its reliefs of the world of desire hidden by the encasement), the first walk round it open" if i == 0
                          else f"the {['first', 'second', 'third', 'fourth', 'fifth'][i - 1]} square terrace, redented toward its middle, a gallery round it"][0]})
    flights(f"{name} stairs", prev, top, prof[0][1], W,
            "the four stairs up the foot from the ground, the main one on the east" if i == 0 else f"the stairs up to {name}, cut into its stair projections")
    prev = top
for name, top, r in ROUND:
    L = flight_steps(top - prev) * RUN
    add(name, {"type": "prism", "plan": {"points": round_outline(r, (WR, L))}, "height": top, "walked": True, "at": [[0, 0, 0, 0]],
               "_about": f"the {name.split()[-1] == '1' and 'first' or name.split()[-1] == '2' and 'second' or 'third'} round terrace, open to the sky"})
    flights(f"{name} stairs", prev, top, r, WR, f"the stairs up to {name}")
    prev = top

# ---- the balustrades: niches all along, a Buddha in each of the first's, a small stupa over every one ---------------
# (an enclosure on the terrace's own edge -- its walls inward from it -- the outline without its notch, broken by an
#  opening as wide as the stair over it; its edges walked in planPoints' winding, so face i is edge i)
NICHE = {"width": 1.1, "sill": 0.45, "springing": 1.2, "head": {"profile": "semicircular"}}
PITCH, END = 2.6, BT + 0.5                 # a niche every PITCH along a face, none nearer its ends than END
small = []; buddhas = []
FACES = {0: FACE_PZ, 1: FACE_PX, 2: FACE_NZ, 3: FACE_NX}
for i, (name, top, prof) in enumerate(TERRACES[1:5], start=1):
    pts = square_outline(prof)
    faces = {}
    for e in range(len(pts)):
        p0, p1 = pts[e], pts[(e + 1) % len(pts)]
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        mx, mz = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        ux, uz = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
        ox, oz = -uz, ux                                   # (outward: the outside is on the left of every edge, this winding)
        axis = abs(mx * ux + mz * uz) < 1e-6 and abs(abs(mx * ox + mz * oz) - prof[0][1]) < 1e-6
        ops, ats = [], []
        if axis:
            ops.append({"at": 0, "width": W, "sill": 0, "springing": BH, "head": {"profile": "flat"}})
            k = 1
            while k * PITCH + NICHE["width"] / 2 <= L / 2 - END:
                if k * PITCH - NICHE["width"] / 2 > W / 2 + 0.6: ats += [k * PITCH, -k * PITCH]
                k += 1
        elif L >= 2 * END + NICHE["width"]:
            m = int((L - 2 * END - NICHE["width"]) / PITCH) + 1
            ats = [(j - (m - 1) / 2) * PITCH for j in range(m)]
        for a in sorted(ats):
            ops.append({"at": r4(a), **NICHE})
            cx, cz = mx + ux * a - ox * BT / 2, mz + uz * a - oz * BT / 2
            small.append([r4(cx), r4(top + BH), r4(cz), 0])
            if i == 1 and axis:
                side = 0 if oz > .5 else 1 if ox > .5 else 2 if oz < -.5 else 3
                buddhas.append(((cx, top + NICHE["sill"], cz), FACES[side]))
        ops.sort(key=lambda o: o["at"])
        if ops: faces[str(e)] = ops
    add(f"balustrade {i}", {"type": "enclosure", "plan": {"points": pts}, "thickness": BT, "height": BH, "glass": False,
                             "openings": [], "faces": faces, "at": [[0, top, 0, 0]],
                             "_about": f"the balustrade round the {['first', 'second', 'third', 'fourth'][i - 1]} gallery: a niche in it every few paces, broken where the stairs come up"})
add("niche stupa cushions", {"type": "column", "radius": 0.36, "height": 0.22, "sides": 8, "at": small,
                             "_about": "the little stupas along the balustrades' tops, one over every niche: the cushion"})
add("niche stupas", {"type": "dome", "radius": 0.3, "thickness": 0.08, "sides": 8, "head": {"profile": "bell", "waist": 0.8, "lift": 0.7},
                     "at": [[x, r4(y + 0.22), z, 0] for x, y, z, _ in small], "_about": "and its bell"})
add("niche stupa spires", {"type": "column", "radius": 0.07, "taper": 0.3, "height": 0.4, "sides": 6,
                           "at": [[x, r4(y + 0.22 + 0.45), z, 0] for x, y, z, _ in small], "_about": "and its spire"})

# ---- the round terraces' stupas: 72, a Buddha behind each one's lattice ----------------------------------------------
# rings of 32, 24 and 16, none on the axes (the stairs come up between two), each a lotus cushion, the bell, the harmika
# (square on the first two rings, octagonal on the last, as on site), the spire
CR, BR = 1.5, 1.35                         # the cushion's radius and the bell's
BELL = {"profile": "bell", "waist": 0.8, "lift": 0.9}
RINGS = [(32, 23.4, 22.0), (24, 17.4, 24.0), (16, 10.8, 26.0)]
for k, (n, rr, y) in enumerate(RINGS, start=1):
    at = [[r4(rr * math.sin((j + .5) * 2 * math.pi / n)), y, r4(rr * math.cos((j + .5) * 2 * math.pi / n)), 0] for j in range(n)]
    add(f"stupas {k} cushions", {"type": "column", "radius": CR, "height": 0.45, "sides": 16, "at": at,
                                 "_about": f"the {n} perforated stupas of the {['first', 'second', 'third'][k - 1]} round terrace: the double lotus cushion"})
    add(f"stupas {k}", {"type": "dome", "radius": BR, "thickness": 0.15, "sides": 16, "head": BELL,
                        "at": [[x, r4(y + 0.45), z, 0] for x, y, z, _ in at],
                        "_about": "the bell, latticed (diamond openings on the lower rings, square ones on the top) over a seated Buddha"})
    if k < 3:
        add(f"stupas {k} harmikas", {"type": "box", "width": 0.7, "length": 0.7, "height": 0.45, "atop": f"stupas {k}", "atopR": 0.42,
                                     "at": [[x, 0, z, 0] for x, _, z, _ in at], "_about": "the square harmika on the bell's crown"})
    else:
        add(f"stupas {k} harmikas", {"type": "column", "radius": 0.38, "height": 0.45, "sides": 8, "atop": f"stupas {k}", "atopR": 0.38,
                                     "at": [[x, 0, z, 0] for x, _, z, _ in at], "_about": "the octagonal harmika on the bell's crown"})
    add(f"stupas {k} spires", {"type": "column", "radius": 0.17, "taper": 0.35, "height": 0.9, "sides": 8, "atop": f"stupas {k} harmikas",
                               "at": [[x, 0, z, 0] for x, _, z, _ in at], "_about": "the spire (yasti)"})

# ---- the great stupa ---------------------------------------------------------------------------------------------
Y3 = ROUND[-1][1]
add("great stupa cushion", {"type": "prism", "plan": {"sides": 32, "radius": 8.4}, "height": 1.2, "at": [[0, Y3, 0, 0]],
                            "_about": "the great stupa's double lotus cushion"})
add("great stupa", {"type": "dome", "radius": 7.6, "thickness": 0.6, "sides": 32, "head": {"profile": "bell", "waist": 0.85, "lift": 0.45},
                    "at": [[0, r4(Y3 + 1.2), 0, 0]], "_about": "the great stupa at the summit: closed, its two chambers empty, a bell rising from the cushion to a level crown"})
add("great stupa harmika", {"type": "box", "width": 3.4, "length": 3.4, "height": 1.4, "atop": "great stupa", "atopR": 2.0, "at": [[0, 0, 0, 0]],
                            "_about": "the harmika: the railed square on its crown"})
add("great stupa spire", {"type": "column", "radius": 0.75, "taper": 0.25, "height": 3.2, "sides": 8, "atop": "great stupa harmika", "at": [[0, 0, 0, 0]],
                          "_about": "the spire (yasti), its parasols worn to an octagonal shaft"})

# ---- the Buddhas in the first balustrade's niches ---------------------------------------------------------------
for j, (p, face) in enumerate(buddhas):
    parts[f"buddha {j + 1}"] = statue(p, kind="man", pose="sit", style="chinese", stone="limestone", scale=0.75, seed=j + 1, face=face)
    build.append(f"buddha {j + 1}")

doc = {
    "name": "Borobudur",
    "_about": "BOROBUDUR (c. 800): the foot, five square terraces redented toward their middles, their galleries walled in by "
              "balustrades of niches (a Buddha in each of the first's, a little stupa over every one), three round terraces "
              "ringed by 72 perforated bell stupas, and the great stupa at the summit; the stairs straight up the four axes, cut "
              "into the terraces they climb. The plan the survey's, made symmetric. Generated by tools/archgen/borobudur.py -- "
              "edit the script for arithmetic changes. East is +x, south +z.",
    "params": {"detail": 4},
    "base": {"height": 0.3, "steps": 1, "stepOut": 0.5, "margin": 6},
    "railing": {"type": "stone", "height": 0.9},
    "build": build,
    "parts": parts,
}
out = os.path.join(ROOT, "assets", "architecture", "borobudur.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts,", len(small), "niches,", len(buddhas), "buddhas")
