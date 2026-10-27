# EL CASTILLO, Chichen Itza (the Temple of Kukulcan, 9th-12th c.), set out by the rules its builders counted by:
#   THE CALENDAR. Four staircases of 91 steps and the temple's own step make the 365 days of the year; the nine
#   terraces, cut in two by the stairs, make the 18 months of the Haab on each face; and each face carries 52 PANELS,
#   the years of the Calendar Round -- 26 a side of its stair, shared out among the terraces by their length (the
#   largest remainders taking the odd ones), the same on either side, so every face is symmetrical.
#   THE TERRACE is TALUD AND TABLERO: a leaning foot and a vertical panel band over it (the crepidoma's `tablero`), the
#   panels recessed in the band -- a skin laid on it with the panels cut through, the core showing behind.
#   THE SERPENT. Only the north stair -- the one the equinox shadow runs down -- ends in the feathered serpent's heads
#   (components/serpent-head), one at the foot of each balustrade, jaws open toward the approach; and the temple's
#   north door is divided in three by serpent columns (components/serpent-column), heads on the floor, tails up as
#   the capitals.
#   THE CORBEL VAULT. A Maya roof is closed by corbelling (profiles.js `corbel`), so no room is wider than a corbel can
#   span: the temple is narrow galleries -- a corridor round three sides, entered by a door in each, and on the north
#   the portico and, behind it, the sanctuary, its vault cut into three by two pillars and the lintels over them. The
#   temple's HEIGHT follows: the walls to the springing, the widest span's corbel rise and its capstone, the flat roof
#   over that, the medial moulding at the springing, the cornice and the crest of merlons along the roof's edge.
#   North is +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
Q = math.pi / 2
r4 = lambda v: round(v, 4)

TOP, N, H = 19.5, 9, 24.0 / 9                  # the top platform, the terraces, each one's height
OUT = (55.3 - TOP) / 2 / N                     # how far each terrace stands out from the one above
TABLERO = 0.55                                 # the vertical panel band's share of a terrace
add("pyramid", {"type": "crepidoma", "width": TOP, "length": TOP, "steps": N, "stepH": r4(H), "stepOut": r4(OUT), "batter": 0.8, "tablero": TABLERO,
                "at": [[0, 0, 0, 0]], "_about": "nine terraces, each a leaning talud and a vertical tablero over it, each set back from the one below"})

# the four staircases: each from the ground straight up the middle of a face to the top platform
STEPS, W = 91, 8.9
RISE = 24.0 / STEPS
reach = TOP / 2 + STEPS * RISE                 # a 45-degree flight: it projects from the pyramid's foot
def rot(x, z, d):                              # a placement turned by d about the middle, as the engine turns a part
    c, s = math.cos(d), math.sin(d)
    return x * c + z * s, -x * s + z * c
names = ["north", "west", "south", "east"]
for k, nm in enumerate(names):
    d = k * Q
    x, z = rot(W / 2, reach, d)
    add(f"{nm} stair", {"type": "flight", "steep": True, "width": W, "run": r4(RISE), "rise": r4(RISE), "base": 0, "top": 24.0, "landing": 0,
                        "at": [[r4(x), 0, r4(z), round(Q + d, 6)]],
                        **({"_about": "a staircase up each face: 91 steps of 26cm on 26cm -- steep, as the real ones are -- arriving on the top platform"} if k == 0 else {})})

# THE PANELS: 26 a side of the stair on every face, shared by the terraces' lengths
D_SKIN = 0.22
band = H * TABLERO
segs = []                                      # per terrace (from the foot): the tablero's half-width, the run beside the stair
for i in range(N):
    A = TOP / 2 + OUT * (N - 1 - i)
    segs.append((A, A - W / 2))
total = sum(S for _, S in segs)
share = [26 * S / total for _, S in segs]
count = [math.floor(v) for v in share]
for i in sorted(range(N), key=lambda i: share[i] - count[i], reverse=True)[:26 - sum(count)]:
    count[i] += 1
assert sum(count) == 26
for i, ((A, S), c) in enumerate(zip(segs, count)):
    y0 = (i + 1 - TABLERO) * H
    slot = S / c
    # (the run east of the stair reaches the corner and the next face's run abuts its back; turned round the pyramid
    #  the four faces close the corners without overlapping)
    for tag, x0, x1 in (("long", W / 2, A + D_SKIN), ("short", -A, -W / 2)):
        L = x1 - x0
        # (each run's panels laid from the stair's side out, so the two runs mirror each other)
        ops = [{"at": r4(slot * (j + 0.5) if tag == "long" else L - slot * (j + 0.5)), "width": r4(slot * 0.62),
                "sill": r4(band * 0.18), "springing": r4(band * 0.8), "head": {"profile": "flat"}, "glass": False} for j in range(c)]
        at = []
        for k in range(4):
            px, pz = rot((x0 + x1) / 2, A + D_SKIN, k * Q)
            at.append([r4(px), r4(y0), r4(pz), r4(k * Q)])
        add(f"tablero {tag} {i + 1}", {"type": "wall", "width": r4(L), "height": r4(band), "thickness": D_SKIN, "glass": False, "openings": ops, "at": at,
                                       **({"_about": "the panel band of a terrace: a skin on the tablero with its panels cut through it, the core behind them"} if i == 0 and tag == "long" else {})})

# the serpent heads at the foot of the north stair's balustrades (their plume collars against its corners, clear of the
# treads' approach)
HW = 1.4
add("serpent heads", {"type": "component", "use": "components/serpent-head", "params": {"W": HW},
                      "at": [[r4(sx * (W / 2 + 0.7 * HW)), 0, r4(reach + 0.9 * HW), 0] for sx in (-1, 1)],
                      "_about": "Kukulcan's heads at the foot of the north stair's balustrades (the equinox shadow runs down to them)"})

# ---- THE TEMPLE on the top platform, its rooms as wide as a corbel closes ----------------------------------------
Y0 = 24.0
TW, tw = 14.0, 1.0                             # its outer walls
a = TW / 2 - tw                                # their inner faces
cw, tin = 2.0, 0.9                             # the gallery round three sides, the inner walls
b = a - cw                                     # the inner walls' outer faces
c = b - tin                                    # their inner faces: the portico and the sanctuary between
zP = a - 2.4                                   # the portico's back (its depth 2.4), the cross wall behind it
zS = zP - tin                                  # the sanctuary's front
hs = 3.5                                       # the springing: the walls' height to where the corbels start
CAP, CAPT, SLOPE = 0.15, 0.45, 70              # the capstone's half-width and thickness, the soffits' lean
spans = {"gallery": cw, "portico": a - zP, "sanctuary side": c - 1.4, "sanctuary middle": 1.4}
rise = lambda span: (span / 2 - CAP) * math.tan(math.radians(SLOPE))
TH = hs + max(rise(v) for v in spans.values()) + CAPT        # the vaults filled flat to the roof over the widest one
corbel = {"profile": "corbel", "cap": CAP, "slope": SLOPE}
hd, wd = 2.6, 1.6                              # the doors
door = [{"at": 0, "width": wd, "sill": 0, "springing": hd, "head": {"profile": "flat"}, "glass": False}]
CW = 0.9                                       # the serpent columns' heads
bay = (2 * c - 2 * CW * 0.8) / 3
add("temple", {"type": "enclosure", "plan": {"rect": [TW, TW]}, "thickness": tw, "height": r4(TH), "glass": False,
               "openings": door, "faces": {"0": [{"at": 0, "width": r4(2 * c), "sill": 0, "springing": 3.0, "head": {"profile": "flat"}, "glass": False}]},
               "courses": [{"y": 0, "h": 0.3, "out": 0.1, "profile": "band"},
                           {"y": hs - 0.1, "h": 0.55, "out": 0.22, "profile": "string"},
                           {"y": r4(TH - 0.5), "h": 0.5, "out": 0.3, "profile": "band"}],
               "at": [[0, Y0, 0, 0]],
               "_about": "the temple's walls: the north front open between serpent columns into the portico, a door on each other side into the gallery; the medial moulding at the vaults' springing, the cornice at the roof"})
add("serpent columns", {"type": "component", "use": "components/serpent-column", "params": {"W": CW, "H": 3.0},
                        "at": [[r4(sx * (bay / 2 + CW * 0.4)), Y0, r4(TW / 2 - tw / 2 + 0.3 * CW), 0] for sx in (-1, 1)],
                        "_about": "the feathered serpent standing on its head either side of the middle bay, its tail carrying the lintel"})
# the inner walls: the U round the portico and the sanctuary (east, west, south), and the cross wall between them
for sx, side in ((1, "east"), (-1, "west")):
    add(f"{side} inner wall", {"type": "wall", "width": r4(a - (-c)), "height": r4(TH), "thickness": tin, "glass": False,
                               "at": [[r4(sx * b), Y0, r4((a - c) / 2), r4(sx * Q)]]})
add("south inner wall", {"type": "wall", "width": r4(2 * b), "height": r4(TH), "thickness": tin, "glass": False, "at": [[0, Y0, r4(-b), r4(math.pi)]]})
add("cross wall", {"type": "wall", "width": r4(2 * c), "height": r4(TH), "thickness": tin, "glass": False, "openings": [{**door[0], "at": r4(c)}],
                   "at": [[0, Y0, r4(zP), 0]], "_about": "between the portico and the sanctuary, its door on the axis"})
# the sanctuary's two pillars: each the middle pier of a wall along the axis, the lintels over its two openings the
# beams the vaults spring from
pw = 0.7
L_s = zS - (-c)
add("sanctuary pillars", {"type": "wall", "width": r4(L_s), "height": r4(TH), "thickness": pw, "glass": False,
                          "openings": [{"at": r4(v), "width": r4((L_s - pw) / 2), "sill": 0, "springing": r4(hs - 0.5), "head": {"profile": "flat"}, "glass": False}
                                       for v in ((L_s - pw) / 4, L_s - (L_s - pw) / 4)],
                          "at": [[r4(sx * (1.4 / 2 + pw)), Y0, r4((zS - c) / 2), r4(sx * Q)] for sx in (-1, 1)],
                          "_about": "two pillars down the sanctuary, the lintels over them, the wall over those up to the roof between the vaults"})
# the CORBEL VAULTS (barrels on the `corbel` head), each over the run it closes
vault = lambda width, length, x, z, yaw: {"type": "barrel", "width": r4(width), "length": r4(length), "springing": hs, "top": r4(TH), "head": corbel,
                                          "at": [[r4(x), Y0, r4(z), r4(yaw)]]}
add("east gallery vault", vault(cw, 2 * a, a - cw / 2, a, 0))
add("west gallery vault", vault(cw, 2 * a, -(a - cw / 2), a, 0))
add("south gallery vault", vault(cw, 2 * b, b, -(a - cw / 2), Q))
add("portico vault", vault(a - zP, 2 * c, c, (a + zP) / 2, Q))
xm = 1.4 / 2
for nm, x0, x1 in (("west", -c, -xm - pw), ("middle", -xm, xm), ("east", xm + pw, c)):
    add(f"sanctuary {nm} vault", vault(x1 - x0, L_s, (x0 + x1) / 2, zS, 0))
add("roof", {"type": "box", "width": TW, "length": TW, "height": 0.35, "walked": True, "flatRoof": True, "at": [[0, r4(Y0 + TH), 0, 0]]})
crest = []
for k in range(4):
    px, pz = rot(0, TW / 2 - 0.2, k * Q)
    crest.append([r4(px), r4(Y0 + TH + 0.35), r4(pz), r4(k * Q)])
add("roof crest", {"type": "component", "use": "components/crenellation", "params": {"L": TW - 0.8, "t": 0.4, "h": 0.3, "step": 1.1, "mh": 0.75}, "at": crest,
                   "_about": "the crest of stepped merlons along the roof's edge"})

doc = {"name": "Chichen Itza",
       "_about": "EL CASTILLO, CHICHEN ITZA (the Temple of Kukulcan), counted out by the calendar: nine talud-and-tablero terraces (55m square, 24m to the top), 52 recessed panels on every face (the Calendar Round), four stairs of 91 steep steps (with the temple's step, the 365 days), the feathered serpent's heads at the foot of the north stair; on top the temple, its rooms as narrow as a corbel vault closes -- the gallery round three sides, the portico behind the serpent columns of the north door, the sanctuary with its two pillars -- its height worked from the springing and the widest corbel, the crest of merlons on its roof (tools/archgen/chichen_itza.py).",
       "params": {"detail": 4}, "base": {"height": 0.3, "steps": 1, "stepOut": 0.5, "margin": 3},
       "railing": {"type": "stone", "height": 1.0}, "_railing": "the stairs' balustrades: stone, a metre high, sloping with the flights", "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/chichen-itza.json"), "w").write(json.dumps(doc, indent=2) + "\n")
print("chichen-itza:", len(parts), "parts; panels per terrace", count)
