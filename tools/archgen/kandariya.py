# KANDARIYA MAHADEVA, KHAJURAHO (c. 1030, the Chandella kings), in buff sandstone: the NAGARA temple at its fullest. On a
# high terrace (jagati) the temple stands on its own moulded plinth (adhishthana), its halls in a line from the entrance to
# the sanctum, each roofed higher than the last -- the porch (ardhamandapa), the hall (mandapa), the great hall
# (mahamandapa) with its balconied transepts, the vestibule (antarala) -- and over the sanctum (garbhagriha), within its
# ambulatory, the TOWER (shikhara.js): a pancharatha body bending in along the rekha to the amalaka and kalasha, built up of
# copies of itself, the urushringas, tier on tier. The halls' roofs are SAMVARANA (shikhara.js): stepped pyramids of slabs
# with bells on every course. So the whole rises as a range of peaks to the summit over the god -- Kailasa, Shiva's mountain.
#   Built as a mason raises it: terrace, stairs, plinths, the sanctum's walls and cell, the halls' parapets and pillars,
# the beams on them, the roofs on the beams, the tower on the sanctum's cornice. The entrance faces +z (east, on site).
#   Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
r4 = lambda v: round(v, 4)
flat = {"profile": "flat"}

# the RATHA PLAN, as shikhara.js rathaPlan draws it: a square `a` from its middle to a karna's face, each side in
# `rathas` offsets, the bhadra `bhadra` of the side, each offset `step` further out toward the middle -- the sanctum's
# walls are the tower's plan carried down to the plinth, as on site
def ratha_plan(a, rathas=5, step=0.3, bhadra=0.3):
    k = (rathas - 1) // 2; side = 2 * a
    bw = side * bhadra if k else side; rest = (side - bw) / (2 * k) if k else 0
    b = [-a]
    for j in range(2 * k + 1): b.append(b[j] + (bw if j == k else rest))
    p = lambda j: (k - abs(j - k)) * step
    one = [(-a, -a)]
    for j in range(1, 2 * k + 1): one += [(b[j], -(a + p(j - 1))), (b[j], -(a + p(j)))]
    out = []
    for q in range(4):
        for x, z in one:
            X, Z = x, z
            for _ in range(q): X, Z = -Z, X
            out.append([r4(X), r4(Z)])
    return out

# ---------------------------------------------------------------- the measures
JH = 3.0                    # the terrace
AH = 2.2                    # the temple's plinth over it
FL = JH + AH                # 5.2: the floor of the halls and the sanctum
HW = 6.0                    # walls and pillars, the floor to the roofs' foot
TOPW = FL + HW              # 11.2
PAR = 1.0                   # the balconies' and halls' parapet (asana), its seat-back
BEAM = 0.5                  # the beams on the pillars
# along the axis, from the entrance (+z) to the sanctum: [front, back] of each unit, its width
PORCH = (18.0, 13.5, 6.0)
MANDAPA = (13.5, 7.5, 8.4)
HALL = (7.5, -3.3, 10.8)
ANTARALA = (-3.3, -5.7, 6.4)
SANCTUM = (-5.7, -18.1, 12.4)
TRANSEPT = 19.0             # the balconied transepts across, at the great hall and the sanctum
mid = lambda u: r4((u[0] + u[1]) / 2)
dep = lambda u: r4(u[0] - u[1])
ZS = mid(SANCTUM)           # -11.9: the sanctum's and the tower's middle
SA = SANCTUM[2] / 2         # 6.2: the sanctum's karna faces from its middle
STEP = 0.3

# ---------------------------------------------------------------- the terrace and its stairs
JZ = (-22.0, 26.0)          # the terrace's back and front: room to walk round, and a landing before the temple stair
JM = mid(JZ); JL = r4(JZ[1] - JZ[0])
add("jagati", {"type": "box", "width": 30, "length": JL, "height": JH, "at": [[0, 0, JM, 0]],
               "courses": {"list": [{"y": 0, "h": 0.45, "out": 0.25, "profile": "khura"},
                                    {"y": r4(JH - 0.35), "h": 0.35, "out": 0.2, "profile": "kapota"}],
                           "clear": {"0": [[13.0, 17.0]]}},
               "_about": "the terrace the temple stands on, high over the ground, walked round (the pradakshina outside): a foot moulding and an eave at its edge, broken by the stair"})
# (a flight runs from its placement along local +x -- turned a quarter, toward -z -- and is `width` across toward -x)
add("terrace stair", {"type": "flight", "run": 0.3, "rise": 0.2, "width": 4.0, "base": 0, "top": JH, "landing": 0,
                      "at": [[2.0, 0, r4(JZ[1] + 15 * 0.3), Q := math.pi / 2]], "_about": "the steep stair up the terrace's front"})
add("temple stair", {"type": "flight", "run": 0.3, "rise": 0.2, "width": 3.0, "base": JH, "top": FL, "landing": 0,
                     "at": [[1.5, 0, r4(PORCH[0] + 11 * 0.3), Q]], "_about": "and up the plinth to the porch"})

# ---------------------------------------------------------------- the plinth (adhishthana): ONE moulding round the plan
# The units' plinths are one plinth: its outline the union of theirs -- in and out along the halls, the transepts and
# the sanctum, all symmetric about the axis, so its half-width a function of z -- and its mouldings, khura to kapota
# (courses.js), run round all of it, stopping at the stair.
UNITS = [(PORCH[2] / 2, PORCH[1], PORCH[0]), (MANDAPA[2] / 2, MANDAPA[1], MANDAPA[0]), (HALL[2] / 2, HALL[1], HALL[0]),
         (TRANSEPT / 2, mid(HALL) - 3.0, mid(HALL) + 3.0), (ANTARALA[2] / 2, ANTARALA[1], ANTARALA[0]),
         (SANCTUM[2] / 2 + STEP + 0.2, SANCTUM[1], SANCTUM[0]), (TRANSEPT / 2, ZS - SANCTUM[2] * 0.15 - 0.5, ZS + SANCTUM[2] * 0.15 + 0.5)]
zs = sorted({z for _, z0, z1 in UNITS for z in (z0, z1)})
half = [(max([h for h, z0, z1 in UNITS if z0 <= (za + zb) / 2 <= z1] or [0]), za, zb) for za, zb in zip(zs, zs[1:])]
# (walked in planPoints' winding, so it keeps its face numbers: down the right side from the front, back up the left --
#  the last face the front, from the left)
right = []
for h, za, zb in reversed(half):
    for q in ((h, zb), (h, za)):
        if right and right[-1] == q: continue
        if len(right) >= 2 and right[-1][0] == right[-2][0] == q[0]: right[-1] = q; continue
        right.append(q)
right = [[r4(x), r4(z)] for x, z in right]
OUTLINE = right + [[-x, z] for x, z in reversed(right)]
MOULD = [{"y": 0, "h": 0.4, "out": 0.24, "profile": "khura"},
         {"y": 0.45, "h": 0.7, "out": 0.3, "profile": "kumbha"},
         {"y": 1.2, "h": 0.3, "out": 0.18, "profile": "kalasha"},
         {"y": 1.55, "h": 0.2, "out": 0.08, "profile": "band"},
         {"y": 1.8, "h": 0.4, "out": 0.34, "profile": "kapota"}]
add("adhishthana", {"type": "prism", "plan": {"points": OUTLINE}, "height": AH, "at": [[0, JH, 0, 0]],
                    "courses": {"list": MOULD, "clear": {str(len(OUTLINE) - 1): [[r4(PORCH[2] / 2 - 1.5), r4(PORCH[2] / 2 + 1.5)]]}},
                    "_about": "the temple's own plinth: one mass on the whole plan, its mouldings -- the hoof (khura), the pot (kumbha), the roll (kalasha), a band, the dovecote eave (kapota) -- running in and out round every projection, stopped where the stair comes up"})

# ---------------------------------------------------------------- the sanctum: its walls on the tower's plan, the cell
# the walls are a square on the karna line, the offsets of the plan (the pratirathas a step out, the bhadras two) laid
# against them -- a wall a step deep can't be a metre thick; on site too the rathas are the facing, the core is square.
# The bhadras on three sides are the openings themselves: to the balconies across and to the vestibule
BW = r4(2 * SA * 0.3); REST = r4((2 * SA - BW) / 4)
add("sanctum walls", {"type": "enclosure", "plan": {"rect": [SANCTUM[2], SANCTUM[2]]}, "thickness": 1.2, "height": HW, "glass": False,
                      "openings": [],
                      "faces": {"1": [{"at": 0, "width": 3.0, "sill": 0, "springing": 4.2, "head": flat}],
                                "3": [{"at": 0, "width": 3.0, "sill": 0, "springing": 4.2, "head": flat}],
                                "0": [{"at": 0, "width": 2.8, "sill": 0, "springing": 4.6, "head": flat}]},
                      "at": [[0, FL, ZS, 0]],
                      "_about": "the walls round the ambulatory (the jangha), square on the karna line; open to the balconies and to the vestibule"})
add("sanctum pratirathas", {"type": "box", "width": REST, "length": STEP, "height": HW,
                            "at": [[r4(c * (BW / 2 + REST / 2)), FL, r4(ZS - SA - STEP / 2), 0] for c in (1, -1)] +
                                  [[r4(c * (BW / 2 + REST / 2)), FL, r4(ZS + SA + STEP / 2), 0] for c in (1, -1)],
                            "_about": "the offsets a step proud of the walls on the front and the back, either side of the bhadra"})
add("sanctum pratirathas across", {"type": "box", "width": STEP, "length": REST, "height": HW,
                                   "at": [[r4(c * (SA + STEP / 2)), FL, r4(ZS + d * (BW / 2 + REST / 2)), 0] for c in (1, -1) for d in (1, -1)],
                                   "_about": "and on the two sides, flanking the balconies"})
add("sanctum bhadra", {"type": "box", "width": BW, "length": 2 * STEP, "height": HW, "at": [[0, FL, r4(ZS - SA - STEP), 0]],
                       "_about": "the bhadra at the back, two steps proud: the one the balconies and the vestibule don't take"})
add("garbhagriha", {"type": "enclosure", "plan": {"rect": [5.6, 5.6]}, "thickness": 0.9, "height": HW, "glass": False,
                    "openings": [], "faces": {"0": [{"at": 0, "width": 1.4, "sill": 0, "springing": 2.8, "head": flat}]},
                    "at": [[0, FL, ZS, 0]], "_about": "the womb-house: the dark cell of the god, its one door toward the entrance"})
# the balconies off the ambulatory and the great hall: a parapet round the open side, pillars on it, beams, the eaves
def balconies(name, z, x0, length):
    x1 = TRANSEPT / 2; d = r4(x1 - x0)
    for sx, nm in ((1, "right"), (-1, "left")):
        xm = r4(sx * (x0 + x1) / 2)
        add(f"{name} parapet {nm}", {"type": "box", "width": 0.5, "length": length, "height": PAR, "at": [[r4(sx * (x1 - 0.25)), FL, z, 0]],
                                    "_about": "the seat-back (kakshasana) along the balcony's open side"})
        add(f"{name} pillars {nm}", {"type": "column", "radius": 0.24, "sides": 8, "height": r4(HW - PAR - BEAM),
                                    "at": [[r4(sx * (x1 - 0.25)), FL + PAR, r4(z + f * (length / 2 - 0.3)), 0] for f in (-1, -1 / 3, 1 / 3, 1)]})
        add(f"{name} beam {nm}", {"type": "box", "width": 0.5, "length": length, "height": BEAM, "at": [[r4(sx * (x1 - 0.25)), r4(TOPW - BEAM), z, 0]]})
        add(f"{name} eaves {nm}", {"type": "box", "width": r4(d + 0.6), "length": r4(length + 0.6), "height": 0.4, "at": [[r4(sx * (x0 + d / 2 + 0.3)), TOPW, z, 0]],
                                  "_about": "the balcony's roof, a slab projecting as an eave (chhajja)"})
balconies("sanctum balcony", ZS, SA, r4(BW - 0.1))
add("sanctum cornice", {"type": "prism", "plan": {"points": ratha_plan(r4(SA + 0.3), 5, STEP, 0.3)}, "height": 0.6, "at": [[0, TOPW, ZS, 0]],
                        "_about": "the cornice (varandika) over the sanctum's walls, the tower's foot"})
TA = 5.4                    # the tower's karna from its middle, a little in from the cornice's
add("shikhara", {"type": "shikhara", "width": 2 * TA, "height": 19.0, "rathas": 5, "step": 0.4, "bhumis": 11, "top": 0.48, "bend": 1.8, "nest": 1,
                 "tiers": [{"scale": 0.6, "lift": 0, "out": 0.45}, {"scale": 0.46, "lift": 0.2, "out": 0.45},
                           {"scale": 0.34, "lift": 0.4, "out": 0.45}, {"scale": 0.24, "lift": 0.58, "out": 0.45}],
                 "corners": {"scale": 0.3, "at": [0, 0.2]}, "at": [[0, r4(TOPW + 0.6), ZS, 0]],
                 "_about": "the tower over the god: the latina and its urushringas, four tiers on each face, and spires on the corners -- the mountain made of mountains"})

# ---------------------------------------------------------------- the vestibule
add("antarala walls", {"type": "box", "width": 1.0, "length": dep(ANTARALA), "height": HW,
                       "at": [[r4(s * (ANTARALA[2] / 2 - 0.5)), FL, mid(ANTARALA), 0] for s in (1, -1)]})
add("antarala roof", {"type": "box", "width": r4(ANTARALA[2] + 0.4), "length": r4(dep(ANTARALA) + 0.6), "height": 1.2, "at": [[0, TOPW, mid(ANTARALA), 0]],
                      "_about": "the vestibule's roof, where the hall's roof meets the tower"})

# ---------------------------------------------------------------- the halls: walls or parapets, pillars, beams, roofs
# the great hall: walls at its corners, open to the balconies, the hall before it and the vestibule
add("hall walls", {"type": "enclosure", "plan": {"rect": [HALL[2], dep(HALL)]}, "thickness": 1.0, "height": HW, "glass": False,
                   "openings": [],
                   "faces": {"2": [{"at": 0, "width": 4.0, "sill": 0, "springing": 4.6, "head": flat}],
                             "1": [{"at": 0, "width": 5.6, "sill": 0, "springing": 4.6, "head": flat}],
                             "0": [{"at": 0, "width": 6.0, "sill": 0, "springing": 4.6, "head": flat}],
                             "3": [{"at": 0, "width": 5.6, "sill": 0, "springing": 4.6, "head": flat}]},
                   "at": [[0, FL, mid(HALL), 0]], "_about": "the great hall's walls, piers at its corners between its four openings"})
add("hall pillars", {"type": "column", "radius": 0.36, "sides": 8, "height": HW,
                     "at": [[sx * 2.4, FL, r4(mid(HALL) + sz * 2.4), 0] for sx in (1, -1) for sz in (1, -1)],
                     "_about": "the four pillars round the middle of the great hall, under the roof's crown"})
# (no stone beam spans its openings whole -- five and six metres: two pillars stand in each, under the lintel, as
#  the balconies' pillars do on their parapets)
add("hall opening pillars", {"type": "column", "radius": 0.3, "sides": 8, "height": 4.6,
                             "at": [[f, FL, r4(HALL[0] - 0.5), 0] for f in (-1.0, 1.0)] +
                                   [[r4(sx * (HALL[2] / 2 - 0.5)), FL, r4(mid(HALL) + f), 0] for sx in (1, -1) for f in (-0.95, 0.95)],
                             "_about": "the pillars in the great hall's openings, carrying their lintels in three"})
balconies("hall balcony", mid(HALL), HALL[2] / 2, 6.0)
# the open halls before it: a parapet down each side, pillars on it, a ring of beams on them
def open_hall(name, u):
    w, l, z = u[2], dep(u), mid(u)
    for sx, nm in ((1, "right"), (-1, "left")):
        add(f"{name} parapet {nm}", {"type": "box", "width": 0.5, "length": l, "height": PAR, "at": [[r4(sx * (w / 2 - 0.25)), FL, z, 0]]})
    add(f"{name} pillars", {"type": "column", "radius": 0.28, "sides": 8, "height": r4(HW - PAR - BEAM),
                            "at": [[r4(sx * (w / 2 - 0.25)), FL + PAR, r4(z + f * (l / 2 - 0.3)), 0] for sx in (1, -1) for f in (-1, 0, 1)]})
    add(f"{name} beams", {"type": "enclosure", "plan": {"rect": [w, l]}, "thickness": 0.5, "height": BEAM, "glass": False, "openings": [],
                          "at": [[0, r4(TOPW - BEAM), z, 0]], "_about": "the ring of beams the roof is laid on"})
open_hall("mandapa", MANDAPA)
open_hall("porch", PORCH)
# the roofs, rising toward the tower
add("porch roof", {"type": "samvarana", "width": r4(PORCH[2] + 0.8), "length": r4(dep(PORCH) + 0.8), "rise": 4.2, "tiers": 4, "top": 0.32, "bells": False,
                   "at": [[0, TOPW, mid(PORCH), 0]], "_about": "the porch's roof, a plain stepped pyramid (phamsana)"})
add("mandapa roof", {"type": "samvarana", "width": r4(MANDAPA[2] + 0.8), "length": r4(dep(MANDAPA) + 0.8), "rise": 6.5, "tiers": 5, "top": 0.3,
                     "at": [[0, TOPW, mid(MANDAPA), 0]], "_about": "the hall's roof: a samvarana, a bell on every course"})
add("hall roof", {"type": "samvarana", "width": r4(HALL[2] + 0.8), "length": r4(dep(HALL) + 0.8), "rise": 10.0, "tiers": 7, "top": 0.26,
                  "at": [[0, TOPW, mid(HALL), 0]], "_about": "the great hall's roof, the highest before the tower"})

doc = {"name": "Kandariya Mahadeva Temple",
       "_about": "KANDARIYA MAHADEVA, KHAJURAHO (c. 1030): the Nagara temple at its fullest, on its high terrace. The halls in a line from the entrance to the sanctum, each roofed higher than the last under stepped bell-crowned roofs (samvarana), and over the sanctum the TOWER -- a pancharatha shikhara bending in along the rekha to the amalaka and the kalasha, built up of copies of itself (urushringas) tier on tier and spires on its corners: a range of peaks rising to the summit over the god, as Kailasa. Every piece follows the rules it was set out by: the sanctum's walls on the tower's own ratha plan, the copies from the tower's measures, the roofs from their courses.",
       "params": {"detail": 4}, "base": {"height": 0.3, "steps": 1, "stepOut": 0.5, "margin": 2}, "railing": {"type": "stone"},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/kandariya.json"), "w").write(json.dumps(doc, indent=2) + "\n")
print(len(build), "parts")
