# THAI (Rattanakosin, 1782 on): the royal and temple architecture of Bangkok -- the Grand Palace, Wat Phra Kaew, Wat Pho,
# Wat Arun -- as rules and the components they are built of. Run it to (re)write them:
#
#   components/thai-gable   the GABLE END of a Thai roof tier (na ban): the gilded pediment triangle `W` wide and `H` high, the
#                           BAI RAKA along its rakes (the naga's body as a bargeboard, its fins standing up it in a row), the
#                           HANG HONG curling up at its feet (the naga's heads), the CHOFA on its apex (the bird's-beak horn,
#                           a blade in the ridge's plane). Its origin is the triangle's foot, in its plane; it faces +z.
#   components/thai-hall    the HALL (ubosot, wihan, sala, throne hall): a platform, a peristyle of indented square pillars
#                           with lotus capitals (`peri`), the walls with doors at the ends and windows down the sides (or none:
#                           an open sala), and the ROOF: steep gabled layers TELESCOPED along the ridge (`lots` 1-3: each pair
#                           of end pieces dropped `ld` under the one within, so the eaves step down at the ends) and LAYERED
#                           down the slope (`chans` 1-2: the upper layer on the walls, the lower over the colonnade, the
#                           upper one's eave lapping it), every piece edged in a band of green tiles at its eaves, every
#                           upper piece's end a thai-gable. Ridge along z, the front +z.
#   components/thai-cross   the CRUCIFORM PRASAT: two thai roofs crossing over a cross of walls (`A` long along z, `B` across,
#                           `W` the arms' width), a door at each arm's end, telescoped ends, and the SPIRE over the crossing
#                           (`spire` prasat: a thai-spire -- Dusit Maha Prasat, Phra Wihan Yot; prang: components/prang --
#                           Prasat Phra Thep Bidon). `walls` open: pillars at the arms' corners instead (Aphorn Phimok).
#   components/thai-roof    a THAI ROOF alone, to set on walls of another style (the Chakri Maha Prasat's European body):
#                           the telescoped gabled roof, with a second across it and the spire over the crossing if wanted.
#   components/thai-spire   the YOT PRASAT / MONDOP SPIRE: the little house it stands on (ruean that), `tiers` (three, five,
#                           seven) redented storeys each flaring out at its foot like a roof skirt and smaller than the one
#                           below, the redented BELL (ong rakhang), the ringed spire (plong chanai), the lotus bud (pli) and
#                           its point -- `w` across its foot, `H` to its tip.
#   components/chedi        the BELL CHEDI (Sri Lankan type, Phra Si Rattana Chedi): three round steps (or redented square
#                           ones: `plan` square -- the golden chedis), three lotus rings, the bell `r` in radius, the square
#                           harmika (balang), the column ring (sao harn), the ringed spire `sh` high, the bud and its point.
#   components/prang        the KHMER TOWER (prang, Prasat Phra Thep Bidon's, Wat Arun's): three redented terraces, the body
#                           with a porch on each side, the corn-cob tower bending in through its storeys -- a small copy on
#                           every corner of every storey (shikhara.js) -- the bud and the spike (naphasun). `w`, `H`.
#   components/thai-wall    a stretch of PALACE WALL `L` long: whitewashed brick `H` high and `t` thick, its coping, the leaf-
#                           shaped BAI SEMA merlons in a row on its outer edge (+z).
#   components/thai-gate    a GATE in a wall (pratu): two piers and the lintel over the passage, a cornice, an attic and the
#                           crown -- a thai-spire (`crown` spire) or a prang (`crown` prang; `lean` yes: a lean one). The way through runs along z.
#   components/yaksha       a YAKSHA, the giant guarding a temple gate (Wat Phra Kaew's twelve, 1830s): standing with his
#                           feet apart, both hands on the club planted before him, in a jewelled collar, a skirt and the tall
#                           tiered crown (chada) -- carved in lofts (as the lion is), `S` metres high, facing +z.
#   components/seated-buddha a BUDDHA seated cross-legged in meditation on his lap, the ushnisha's flame on his head (the
#                           Emerald Buddha's pose), carved in lofts, `S` high, facing +z.
#
# And the helpers a palace's generator uses to set them out: hall(), cross(), spire(), chedi(), prang(), gate() give a
# component's params from the few numbers that size it (the rest by the proportions of the type); wall_run() sets
# thai-wall stretches along a line. y 0 on the ground (or the platform's foot), front +z.
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from javanese import outline, plan, X, rot, BASE, TIER

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMP = os.path.join(ROOT, "assets", "architecture", "components")
r4 = lambda v: round(v, 4)
Q = math.pi / 2
FLAT = {"profile": "flat"}


def write(name, doc):
    p = os.path.join(COMP, name + ".json")
    with open(p, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print("wrote", os.path.relpath(p, ROOT), len(doc["parts"]), "parts")


def lin(**k):
    """a linear expression: lin(W=0.5, b=1.2) -> '0.5 * W + 1.2 * b' (zero terms dropped)"""
    terms = [(r4(v), n) for n, v in k.items() if abs(v) > 1e-9]
    if not terms: return 0
    out = ""
    for i, (v, n) in enumerate(terms):
        s = "-" if v < 0 else "+"
        a = abs(v)
        t = n if a == 1 else f"{a} * {n}"
        out += (("- " if s == "-" else "") + t) if i == 0 else f" {s} {t}"
    return out


# ---- the gable --------------------------------------------------------------------------------------------------------
def gable_component():
    # the bai raka: the rake's band (b deep, measured plumb), the fins standing up it, the hang hong curling up at its feet
    NT = 4                                                 # fins a side
    def outer(f, side):                                    # a point on the band's top edge, f from the foot (0) to the apex (1)
        return (lin(W=side * (1 - f) / 2), lin(H=f, b=1))
    right = [(0, lin(H=1, b=1.15))]
    f0, f1 = 0.93, 0.07
    st = (f0 - f1) / NT
    for i in range(NT):
        fa = f0 - i * st
        right.append(outer(fa, 1))
        right.append((lin(W=(1 - (fa - 0.15 * st)) / 2, b=0.42), lin(H=fa - 0.15 * st, b=1.8)))   # (the fin, leaning up the rake)
        right.append(outer(fa - 0.55 * st, 1))
    right.append(outer(0.03, 1))
    # the hang hong: the band's foot turned out and up into the naga's head
    right += [(lin(W=0.5, b=0.55), lin(b=1.25)), (lin(W=0.5, b=1.1), lin(b=2.3)), (lin(W=0.5, b=1.55), lin(b=2.85)),
              (lin(W=0.5, b=1.75), lin(b=2.1)), (lin(W=0.5, b=1.6), lin(b=0.6)), (lin(W=0.5, b=0.9), lin(b=-0.35)),
              (lin(W=0.5, b=-0.1), lin(b=-0.12))]
    inner_r = [(lin(W=0.5), 0)]
    mirror = lambda p: (f"-({p[0]})" if p[0] != 0 else 0, p[1])
    band = right + inner_r + [(0, "H")] + [mirror(p) for p in reversed(inner_r)] + [mirror(p) for p in reversed(right[1:])]
    # the chofa, a blade in the ridge's plane: its foot on the apex, the horn sweeping up and its beak out over the gable
    # (local -x is the gable's out, +z, once turned a quarter)
    C = [(0.3, 0), (0.18, 0.35), (0.06, 0.62), (-0.06, 0.82), (-0.2, 0.96), (-0.42, 1.0), (-0.3, 0.9), (-0.2, 0.84),
         (-0.14, 0.66), (-0.12, 0.4), (-0.18, 0.12), (-0.3, 0)]
    parts = {
        "na ban": {"type": "screen", "outline": [[lin(W=-0.5), 0], [lin(W=0.5), 0], [0, "H"]], "t": 0.08, "at": [[0, 0, 0, 0]],
                   "_about": "the pediment: the gable's triangle, carved and gilded on red, set with coloured glass"},
        "bai raka": {"type": "screen", "outline": [list(p) for p in band], "t": "t", "at": [[0, 0, "t * 0.5", 0]],
                     "_about": "the bai raka: the naga's body down both rakes, its fins standing up them, its heads (hang hong) curling up at the feet"},
        "chofa": {"type": "screen", "outline": [[f"{r4(x)} * cs", f"{r4(y)} * cs"] for x, y in C], "t": "t * 0.8",
                  "at": [["t * 0.4", lin(H=1, b=0.9), "-t * 0.2", Q]], "when": {"chofa": "yes"},
                  "_about": "the chofa: the bird's-beak horn on the apex, its beak out over the gable"},
    }
    write("thai-gable", {
        "name": "Thai gable",
        "_about": "THE GABLE END of a Thai roof tier: the pediment triangle (na ban) `W` wide at its foot and `H` high, gilded; the "
                  "bai raka down its rakes -- the naga's body as a bargeboard `b` deep with a row of fins standing up it -- its "
                  "hang hong curling up at the feet; the chofa, the bird's-beak horn `cs` high, on the apex (`chofa` yes|no). "
                  "Origin at the triangle's foot in its plane, facing +z; set it on the roof's gable face. Written by "
                  "tools/archgen/thai.py.",
        "params": {"detail": 4, "W": 10.0, "H": 6.5, "b": "max(0.16, H * 0.06)", "t": "max(0.14, b * 0.55)", "cs": "max(0.6, H * 0.26)",
                   "chofa": "yes"},
        "build": list(parts), "parts": parts})


# ---- the roof ----------------------------------------------------------------------------------------------------------
def roof_layers(add, pre, W, L, y, o, pitch, T, when, gable=True, yaw=0.0, lots=(1, 2, 3), strip="0.9"):
    """a Thai roof layer over a `W` (x) by `L` (z) plan from height `y` (expressions), telescoped by `lots` (each value a
    `when` on the param `lots`): the middle piece, then each end piece `lf` long and `ld` lower; every piece's eaves edged
    with a green band (`strip` deep); with `gable`, a thai-gable on every piece's ends. `yaw`: the ridge along x (pi / 2)."""
    def place(lx, ly, lz, ya=0.0):            # (a point in the layer's frame -- ridge along its z -- turned by `yaw`)
        if abs(yaw) < 1e-9: return [lx, ly, lz, r4(ya)]
        return [lz, ly, f"-({lx})" if lx not in (0, "0") else 0, r4(ya + yaw)]
    for v in lots:
        Lc = f"{L} - {2 * (v - 1)} * lf" if v > 1 else L
        for k in range(v):
            nm = f"{pre} {v}" + ("" if k == 0 else f" end {k}")
            yk = f"{y} - {k} * ld" if k else y
            plen = Lc if k == 0 else "lf"
            zs = [0] if k == 0 else [f"({Lc}) / 2 + {r4(k - 0.5)} * lf", f"-(({Lc}) / 2 + {r4(k - 0.5)} * lf)"]
            w = {**when, "lots": v}
            add(nm, {"type": "roof", "form": "gable", "width": W, "length": plen, "pitch": pitch, "overhang": o,
                     "at": [place(0, yk, z) for z in zs], "when": w,
                     **({"_about": "the roof layer's middle piece" if k == 0 else "the telescoped end pieces, dropped under the one within"} if v == 2 else {})})
            # the green band along both eaves of the piece: a single slope as steep as the roof, on its eave
            ey = f"{yk} - {o} * {T} + 0.05"
            ex = f"({W}) / 2 + {o} - {strip} / 2"
            sl = f"{plen} + 2 * {o}"
            add(nm + " eaves", {"type": "roof", "form": "shed", "width": strip, "length": sl, "pitch": pitch, "overhang": 0,
                                "at": [place(f"-({ex})", ey, z, 0) for z in zs] + [place(ex, ey, z, math.pi) for z in zs], "when": w})
            if gable:
                # (its gable on each end of the piece: the face is the verge, `o` past the piece's end)
                outer_end = f"({Lc}) / 2" if k == 0 else f"({Lc}) / 2 + {k} * lf"
                gz = f"{outer_end} + {o} + 0.04"
                gy = f"{yk} - {o} * {T}"
                add(nm + " gables", {"type": "component", "use": "components/thai-gable",
                                     "params": {"W": f"{W} + 2 * {o}", "H": f"(({W}) / 2 + {o}) * {T}"},
                                     "at": [place(0, gy, gz, 0), place(0, gy, f"-({gz})", math.pi)], "when": w})


INDENT = lambda a: [[a, f"-({a}) * 0.72"], [a, f"{a} * 0.72"], [f"{a} * 0.72", f"{a} * 0.72"], [f"{a} * 0.72", a], [f"-({a}) * 0.72", a],
                    [f"-({a}) * 0.72", f"{a} * 0.72"], [f"-({a})", f"{a} * 0.72"], [f"-({a})", f"-({a}) * 0.72"], [f"-({a}) * 0.72", f"-({a}) * 0.72"],
                    [f"-({a}) * 0.72", f"-({a})"], [f"{a} * 0.72", f"-({a})"], [f"{a} * 0.72", f"-({a}) * 0.72"]]   # (a square with its corners indented)


def flights(add, name, ends, when=None, x=0):
    """a flight up the platform (`ph`) at each of `ends` ("+z", "-z", "+x", "-x"), its foot `run` per step out from the
    platform's edge (`PW` x `PL`), `sw` wide"""
    n = "ceil(ph / 0.17)"
    common = {"type": "flight", "width": "sw", "run": 0.3, "rise": f"ph / {n}", "base": 0, "top": "ph", "landing": 0}
    at = {"+z": ["sw / 2", 0, f"PL / 2 + {n} * 0.3", Q], "-z": ["-sw / 2", 0, f"-(PL / 2 + {n} * 0.3)", -Q],
          "+x": [f"PW / 2 + {n} * 0.3", 0, "-sw / 2", math.pi], "-x": [f"-(PW / 2 + {n} * 0.3)", 0, "sw / 2", 0]}
    add(name, {**common, "at": [at[e] for e in ends], **({"when": when} if when else {})})


def hall_component():
    parts = {}
    def add(n, d): parts[n] = d
    # THE PLATFORM, its stairs
    add("platform", {"type": "prism", "plan": {"rect": ["PW", "PL"]}, "height": "ph", "walked": True, "at": [[0, 0, 0, 0]],
                     "courses": [{"y": 0, "h": "min(0.35, ph * 0.25)", "out": 0.12, "profile": "torus"},
                                 {"y": "ph - min(0.3, ph * 0.2)", "h": "min(0.3, ph * 0.2)", "out": 0.15, "profile": "cornice"}],
                     "_about": "the platform (than): the hall's base, its mouldings round its foot and its edge"})
    flights(add, "stairs ends", ["+z", "-z"], {"stairs": ["ends", "all"]})
    flights(add, "stairs front", ["+z"], {"stairs": "front"})
    add("stairs sides", {"type": "flight", "width": "sw", "run": 0.3, "rise": "ph / ceil(ph / 0.17)", "base": 0, "top": "ph", "landing": 0,
                         "at": [["PW / 2 + ceil(ph / 0.17) * 0.3", 0, f"{z} - sw / 2", math.pi] for z in ("L * 0.3", "-L * 0.3")]
                               + [["-(PW / 2 + ceil(ph / 0.17) * 0.3)", 0, f"{z} + sw / 2", 0] for z in ("L * 0.3", "-L * 0.3")],
                         "when": {"stairs": "all"}, "_about": "two flights up each long side (the ubosot's)"})
    # THE PERISTYLE: indented square pillars, a lotus capital on each
    col = {"type": "prism", "plan": {"points": INDENT("cs / 2")}, "height": "ch - cs * 0.5"}
    cap = {"type": "prism", "plan": {"points": INDENT("cs * 0.66")}, "height": "cs * 0.5"}
    xs, zs = "W / 2 + cm", "L / 2 + ce"
    sides = {"at": [[xs, "ph", f"-({zs})", 0], [f"-({xs})", "ph", f"-({zs})", 0]], "repeat": {"count": "nz + 1", "step": [0, 0, f"2 * ({zs}) / nz", 0]}}
    ends = {"at": [[f"-({xs}) + 2 * ({xs}) / nx", "ph", zs, 0], [f"-({xs}) + 2 * ({xs}) / nx", "ph", f"-({zs})", 0]],
            "repeat": {"count": "nx - 1", "step": [f"2 * ({xs}) / nx", 0, 0, 0]}}
    add("pillars", {**col, **sides, "when": {"peri": "all"}, "_about": "the peristyle: square pillars with indented corners (sao yo mum), glass mosaic on them"})
    add("pillars ends", {**col, **ends, "when": {"peri": "all"}})
    lift = lambda d: {**d, "at": [[a[0], "ph + ch - cs * 0.5", a[2], 0] for a in d["at"]]}
    add("capitals", {**cap, **lift(sides), "when": {"peri": "all"}, "_about": "the lotus capitals (bua chong)"})
    add("capitals ends", {**cap, **lift(ends), "when": {"peri": "all"}})
    add("architrave", {"type": "enclosure", "plan": {"rect": [f"2 * ({xs}) + cs", f"2 * ({zs}) + cs"]}, "thickness": "cs", "height": 0.5,
                       "glass": False, "openings": [], "interior": False, "at": [[0, "ph + ch - 0.5", 0, 0]], "when": {"peri": "all"},
                       "_about": "the beam round the pillars' heads the lower roof layer rests on"})
    # THE WALLS: doors at the ends (one or three), windows down the sides
    win = {"every": "wsp", "width": "ww", "end": 2.4, "sill": "wsill", "springing": "wsill + wh", "head": FLAT}
    door = lambda a: {"at": a, "width": "dw", "sill": 0, "springing": "dh", "head": FLAT}
    for n, ats in ((1, [0]), (3, [0, "W * 0.29", "-W * 0.29"])):
        d3 = [door(a) for a in ats]
        add("walls" if n == 1 else "walls three", {"type": "enclosure", "plan": {"rect": ["W", "L"]}, "thickness": "t", "height": "H", "glass": False,
                                                   "interior": True, "openings": [], "faces": {"0": d3, "2": d3, "1": win, "3": win},
                                                   "courses": {"list": [{"y": 0, "h": 0.5, "out": 0.15, "profile": "torus"}, {"y": 0.5, "h": 0.2, "out": 0.08, "profile": "band"}]},
                                                   "at": [[0, "ph", 0, 0]], "when": {"walls": "closed", "doors": n},
                                                   **({"_about": "the walls: the doors at the ends (the main ones on the front), windows down the sides"} if n == 1 else {})})
    # THE ROOF: the layers
    roof_layers(add, "roof", "W", "L + 2 * ce", "ph + H", "o0", "p0", "T0", {"chans": 2})
    roof_layers(add, "roof lower", "W + 2 * cm", "L + 2 * ce - 1.0 - 2 * max(0, o1 - o0)", "ph + ch", "o1", "p1", "T1", {"chans": 2}, gable=False)
    roof_layers(add, "roof single", "W + 2 * cm", "L + 2 * ce", "ph + ch", "o0", "p0", "T0", {"chans": 1})
    params = {"detail": 4,
              "W": 14.0, "L": 30.0, "t": 0.9, "H": 9.0, "ph": 1.4, "pm": 1.6, "cm": 3.0, "ce": 3.0, "ch": 5.6, "cs": 0.7, "sp": 3.6,
              "nz": "max(1, round((L + 2 * ce) / sp))", "nx": "max(1, round((W + 2 * cm) / sp))",
              "PW": "W + 2 * cm + 2 * pm", "PL": "L + 2 * ce + 2 * pm", "sw": 3.0,
              "dw": 1.8, "dh": 4.2, "ww": 1.3, "wsill": 1.2, "wh": 3.0, "wsp": 4.0,
              "lf": 3.2, "ld": 1.8, "p0": 52, "T0": 1.2799, "o0": 0.8, "p1": 45, "T1": 1.0, "o1": 1.0,
              "peri": "all", "walls": "closed", "doors": 1, "lots": 2, "chans": 2, "stairs": "ends"}
    write("thai-hall", {
        "name": "Thai hall",
        "_about": "A THAI HALL (ubosot, wihan, sala, throne hall): a platform `ph` high and `pm` past the pillars, its stairs (`stairs` "
                  "ends|front|all|none); a peristyle of indented square pillars `cs` thick and `ch` high, `cm` out from the walls "
                  "down the sides and `ce` at the ends (`peri` all|none); the walls `W` x `L`, `H` high and `t` thick (`walls` "
                  "closed|open), `doors` 1|3 at each end (`dw` x `dh`), windows down the sides; THE ROOF steep and gabled: the upper "
                  "layer on the walls (pitch `p0`, `T0` its tangent, eaves `o0` out), the lower over the colonnade (`p1`, `T1`, "
                  "`o1`) -- `chans` 2; or one layer over all (`chans` 1) -- each telescoped (`lots` 1-3: end pieces `lf` long, "
                  "each `ld` under the one within), its eaves edged in green tiles, a thai-gable on every upper piece's end. Ridge "
                  "along z, the front +z, y 0 the platform's foot. Written by tools/archgen/thai.py; its hall() works out the "
                  "params from a hall's plan and height.",
        "params": params, "build": list(parts), "parts": parts})


def hall(W, L, H=None, ph=1.4, peri=True, cm=None, ce=None, walls=True, doors=1, lots=2, chans=None, pitch=52, pitch1=None,
         stairs="ends", ch=None, **over):
    """the params of components/thai-hall for walls `W` x `L` (or the pillars' span, for an open sala), `H` high: the rest by
    the proportions of the type (the colonnade a fifth of the width out, the lower layer's eave on its pillars, the upper's
    walls high enough to lap it)"""
    cm = r4(cm if cm is not None else (max(1.8, min(4.2, W * 0.2)) if peri else 0.0))
    ce = r4(ce if ce is not None else cm)
    chans = chans if chans is not None else (2 if peri and walls else 1)
    pitch1 = pitch1 if pitch1 is not None else pitch - 8
    T0, T1 = math.tan(math.radians(pitch)), math.tan(math.radians(pitch1))
    if H is None: H = W * 0.55
    if ch is None: ch = H if chans == 1 else max(3.2, H - cm * T1 - 1.2)
    o1 = r4(min(1.4, max(0.7, cm * 0.3)))
    o0 = r4(0.7 if chans == 2 else o1)
    p = {"W": r4(W), "L": r4(L), "H": r4(H), "ph": r4(ph), "cm": cm, "ce": ce, "ch": r4(ch),
         "peri": "all" if peri else "none", "walls": "closed" if walls else "open", "doors": doors, "lots": lots, "chans": chans,
         "p0": pitch, "T0": r4(T0), "p1": pitch1, "T1": r4(T1), "o0": o0, "o1": o1, "stairs": stairs,
         "lf": r4(max(1.6, min(4.0, (L + 2 * ce) * 0.1))), "ld": r4(max(0.8, min(2.2, W * 0.13))),
         "dh": r4(min(4.6, max(2.4, (ch if chans == 1 else H - o0 * T0) * 0.62))), "wh": r4(min(3.2, max(1.4, H * 0.3))),
         "cs": r4(min(0.9, max(0.4, ch * 0.11)))}
    p.update(over)
    return p


def ridge_of(p):
    """the height of a hall's ridge over its platform's foot"""
    if p["chans"] == 2: return p["ph"] + p["H"] + p["W"] / 2 * p["T0"]
    return p["ph"] + p["ch"] + (p["W"] / 2 + p["cm"]) * p["T0"]


# ---- the cruciform prasat --------------------------------------------------------------------------------------------
def cross_component():
    parts = {}
    def add(n, d): parts[n] = d
    cross = [["-W / 2", "A / 2"], ["W / 2", "A / 2"], ["W / 2", "W / 2"], ["B / 2", "W / 2"], ["B / 2", "-W / 2"], ["W / 2", "-W / 2"],
             ["W / 2", "-A / 2"], ["-W / 2", "-A / 2"], ["-W / 2", "-W / 2"], ["-B / 2", "-W / 2"], ["-B / 2", "W / 2"], ["-W / 2", "W / 2"]]
    m = lambda e: [["-W / 2 - pm", f"A / 2 + pm"], ["W / 2 + pm", "A / 2 + pm"], ["W / 2 + pm", "W / 2 + pm"], ["B / 2 + pm", "W / 2 + pm"],
                   ["B / 2 + pm", "-W / 2 - pm"], ["W / 2 + pm", "-W / 2 - pm"], ["W / 2 + pm", "-A / 2 - pm"], ["-W / 2 - pm", "-A / 2 - pm"],
                   ["-W / 2 - pm", "-W / 2 - pm"], ["-B / 2 - pm", "-W / 2 - pm"], ["-B / 2 - pm", "W / 2 + pm"], ["-W / 2 - pm", "W / 2 + pm"]]
    add("platform", {"type": "prism", "plan": {"points": m(0)}, "height": "ph", "walked": True, "at": [[0, 0, 0, 0]],
                     "courses": [{"y": 0, "h": "min(0.4, ph * 0.2)", "out": 0.14, "profile": "torus"},
                                 {"y": "ph - min(0.35, ph * 0.15)", "h": "min(0.35, ph * 0.15)", "out": 0.16, "profile": "cornice"}],
                     "_about": "the cruciform platform, moulded (on the Dusit Maha Prasat a high base, garudas carrying it)"})
    n = "ceil(ph / 0.17)"
    fl = {"type": "flight", "width": "sw", "run": 0.3, "rise": f"ph / {n}", "base": 0, "top": "ph", "landing": 0}
    add("stairs", {**fl, "at": [["sw / 2", 0, f"A / 2 + pm + {n} * 0.3", Q], ["-sw / 2", 0, f"-(A / 2 + pm + {n} * 0.3)", -Q],
                                [f"B / 2 + pm + {n} * 0.3", 0, "-sw / 2", math.pi], [f"-(B / 2 + pm + {n} * 0.3)", 0, "sw / 2", 0]],
                   "when": {"stairs": "four"}, "_about": "a flight up to each arm's door"})
    add("stairs front", {**fl, "at": [["sw / 2", 0, f"A / 2 + pm + {n} * 0.3", Q]], "when": {"stairs": "front"}})
    door = [{"at": 0, "width": "dw", "sill": 0, "springing": "dh", "head": FLAT}]
    win = {"every": "wsp", "width": "ww", "end": 1.6, "sill": "wsill", "springing": "wsill + wh", "head": FLAT}
    faces = {str(i): door if i in (0, 3, 6, 9) else win for i in range(12)}
    add("walls", {"type": "enclosure", "plan": {"points": cross}, "thickness": "t", "height": "H", "glass": False, "interior": True, "openings": [],
                  "faces": faces, "at": [[0, "ph", 0, 0]], "when": {"walls": "closed"},
                  "_about": "the walls on the cross: a door at each arm's end, windows between"})
    corners = [[x, "ph", z, 0] for x, z in cross]
    add("pillars", {"type": "prism", "plan": {"points": INDENT("cs / 2")}, "height": "H", "at": corners, "when": {"walls": "open"},
                    "_about": "an open pavilion: a pillar on each corner of the cross"})
    add("beams", {"type": "enclosure", "plan": {"points": cross}, "thickness": "cs", "height": 0.6, "glass": False, "interior": False, "openings": [],
                  "at": [[0, "ph + H - 0.6", 0, 0]], "when": {"walls": "open"}})
    roof_layers(add, "roof", "W", "A", "ph + H", "o0", "p0", "T0", {})
    roof_layers(add, "roof across", "W", "B", "ph + H", "o0", "p0", "T0", {}, yaw=Q)
    ridge = "ph + H + W / 2 * T0"
    add("spire", {"type": "component", "use": "components/thai-spire", "params": {"w": "sw0", "H": "sH", "tiers": "tiers"},
                  "at": [[0, f"{ridge} - W / 2 * T0 * 0.45", 0, 0]], "when": {"spire": "prasat"},
                  "_about": "the spire over the crossing (yot prasat)"})
    add("prang", {"type": "component", "use": "components/prang", "params": {"w": "sw0", "H": "sH", "base": "no", "by": 0},
                  "at": [[0, f"{ridge} - W / 2 * T0 * 0.45", 0, 0]], "when": {"spire": "prang"},
                  "_about": "the prang over the crossing (Prasat Phra Thep Bidon's)"})
    params = {"detail": 4, "A": 36.0, "B": 36.0, "W": 12.0, "t": 0.9, "H": 9.0, "ph": 2.0, "pm": 1.6, "cs": 0.8, "sw": 3.0,
              "dw": 2.0, "dh": 4.4, "ww": 1.2, "wsill": 1.4, "wh": 2.8, "wsp": 3.6,
              "lf": 3.0, "ld": 1.6, "p0": 52, "T0": 1.2799, "o0": 1.0, "sw0": 7.0, "sH": 24.0, "tiers": "seven",
              "lots": 3, "walls": "closed", "stairs": "four", "spire": "prasat"}
    write("thai-cross", {
        "name": "Thai cruciform prasat",
        "_about": "A CRUCIFORM PRASAT (Dusit Maha Prasat, Phra Wihan Yot, Prasat Phra Thep Bidon): a cross of walls -- `A` along z, `B` "
                  "across, the arms `W` wide, `H` high (`walls` closed|open: pillars on the corners) -- on a cruciform platform `ph` "
                  "high and `pm` past them, a stair to each arm's door (`stairs` four|front|none), two steep Thai roofs crossing "
                  "(pitch `p0`, `T0` its tangent, eaves `o0`), telescoped at every end (`lots` 1-3, `lf`, `ld`), a thai-gable on each "
                  "piece's end, and over the crossing the SPIRE `sw0` across its foot and `sH` high: a thai-spire of `tiers` (`spire` "
                  "prasat) or a prang (`spire` prang) or none. y 0 the platform's foot. Written by tools/archgen/thai.py.",
        "params": params, "build": list(parts), "parts": parts})


def cross(A, B, W, H, ph=2.0, pitch=52, spireW=None, spireH=None, spire="prasat", tiers="seven", walls=True, lots=3, stairs="four", **over):
    T0 = math.tan(math.radians(pitch))
    p = {"A": r4(A), "B": r4(B), "W": r4(W), "H": r4(H), "ph": r4(ph), "p0": pitch, "T0": r4(T0), "o0": r4(min(1.4, max(0.6, W * 0.08))),
         "sw0": r4(spireW if spireW else W * 0.6), "sH": r4(spireH if spireH else W * 2.2), "spire": spire, "tiers": tiers,
         "walls": "closed" if walls else "open", "lots": lots, "stairs": stairs,
         "lf": r4(max(1.4, min(3.6, (min(A, B) - W) / 2 / lots * 0.8))), "ld": r4(max(0.8, min(2.2, W * 0.13))),
         "dh": r4(min(5.0, max(2.4, (H - 1.0) * 0.62))), "wh": r4(min(3.2, max(1.4, H * 0.32))), "cs": r4(min(0.9, max(0.45, H * 0.08)))}
    p.update(over)
    return p


def cross_top(p):
    """where a cruciform prasat's spire stands, and its tip"""
    y = p["ph"] + p["H"] + p["W"] / 2 * p["T0"] * 0.55
    return y, y + p["sH"]


# ---- a Thai roof alone (on another style's walls: the Chakri Maha Prasat's) --------------------------------------------
def roof_component():
    parts = {}
    def add(n, d): parts[n] = d
    roof_layers(add, "roof", "W", "A", 0, "o0", "p0", "T0", {})
    roof_layers(add, "roof across", "W", "B", 0, "o0", "p0", "T0", {"cross": "yes"}, yaw=Q)
    ridge = "W / 2 * T0"
    add("spire", {"type": "component", "use": "components/thai-spire", "params": {"w": "sw0", "H": "sH", "tiers": "tiers"},
                  "at": [[0, f"{ridge} * 0.55", 0, 0]], "when": {"spire": "prasat"}, "_about": "the spire over the crossing"})
    add("prang", {"type": "component", "use": "components/prang", "params": {"w": "sw0", "H": "sH", "base": "no", "by": 0},
                  "at": [[0, f"{ridge} * 0.55", 0, 0]], "when": {"spire": "prang"}})
    write("thai-roof", {
        "name": "Thai roof",
        "_about": "A THAI ROOF set on walls of another style (the Chakri Maha Prasat's: a European body under Thai roofs): the steep "
                  "gabled roof `W` across and `A` long along z, telescoped at its ends (`lots` 1-3, `lf`, `ld`), green-edged, a "
                  "thai-gable on every end; with `cross` yes a second one `B` long across it, and over the crossing a SPIRE (`spire` "
                  "prasat: a thai-spire of `tiers`; prang; none) `sw0` across and `sH` high. y 0 its eaves' foot (the wall head). "
                  "Written by tools/archgen/thai.py.",
        "params": {"detail": 4, "W": 12.0, "A": 24.0, "B": 24.0, "lf": 2.4, "ld": 1.4, "p0": 52, "T0": 1.2799, "o0": 1.0,
                   "lots": 2, "cross": "yes", "spire": "prasat", "sw0": 6.0, "sH": 24.0, "tiers": "seven"},
        "build": list(parts), "parts": parts})


def roof(W, A, B=0.0, pitch=52, lots=2, spire="none", spireW=None, spireH=None, tiers="seven", o=None, **over):
    """components/thai-roof's params: a roof `W` x `A` (and `B` across, when given) on a wall head"""
    T0 = math.tan(math.radians(pitch))
    p = {"W": r4(W), "A": r4(A), "B": r4(B if B else W), "cross": "yes" if B else "no", "p0": pitch, "T0": r4(T0),
         "o0": r4(o if o is not None else min(1.4, max(0.6, W * 0.08))), "lots": lots, "spire": spire,
         "sw0": r4(spireW if spireW else W * 0.55), "sH": r4(spireH if spireH else W * 2.0), "tiers": tiers,
         "lf": r4(max(1.4, min(3.6, ((min(A, B) if B else A) - (W if B else 0)) / 2 / lots * 0.8))), "ld": r4(max(0.8, min(2.2, W * 0.13)))}
    p.update(over)
    return p


# ---- the spire -------------------------------------------------------------------------------------------------------
SPIRE_TIERS = {"three": 3, "five": 5, "seven": 7}


def spire_component():
    parts = {}
    def add(n, d): parts[n] = d
    add("house", {"type": "prism", "plan": {"points": plan(TIER, "w / 2")}, "height": "H * 0.1", "at": [[0, 0, 0, 0]],
                  "courses": [{"y": "H * 0.085", "h": "H * 0.015", "out": "w * 0.03", "profile": "band"}],
                  "_about": "the little house the spire stands on (ruean that), redented"})
    for word, n in SPIRE_TIERS.items():
        Ht = {3: 0.26, 5: 0.33, 7: 0.38}[n]
        ht = Ht / n                                         # (each tier's height, of H)
        foot = 0.98                                         # (tier 1: its foot as wide as the house)
        k = (0.4 / foot) ** (1 / (n - 1))                   # (each tier's foot this share of the last's)
        y = 0.1
        for i in range(n):
            w = f"tier {word} {i + 1}"
            add(w, {"type": "prism", "plan": {"points": plan(TIER, f"w * {r4(foot * 0.78 / 2)}")}, "height": f"H * {r4(ht * 0.55)}",
                    "batter": {"out": f"w * {r4(foot * 0.11)}", "power": 1.4, "steps": 2}, "at": [[0, f"H * {r4(y)}", 0, 0]], "when": {"tiers": word},
                    **({"_about": "the tiers (chan): each a redented skirt flaring out at its foot, a little gable on each face, and the "
                                  "storey's band over it -- smaller tier by tier"} if i == 0 else {})})
            add(w + " band", {"type": "prism", "plan": {"points": plan(TIER, f"w * {r4(foot * 0.72 / 2)}")}, "height": f"H * {r4(ht * 0.45)}",
                              "at": [[0, f"H * {r4(y + ht * 0.55)}", 0, 0]], "when": {"tiers": word}})
            gw, gh = foot * 0.34, ht * 0.62
            add(w + " gables", {"type": "screen", "outline": [[f"-w * {r4(gw / 2)}", 0], [f"w * {r4(gw / 2)}", 0], [0, f"H * {r4(gh)}"]], "t": f"w * {r4(foot * 0.1)}",
                                "at": [rot([0, f"H * {r4(y + ht * 0.08)}", f"w * {r4(foot * 0.47)}", 0], q) for q in range(4)], "when": {"tiers": word}})
            foot *= k
            y += ht
        yb = y
        add(f"bell {word}", {"type": "dome", "radius": f"w * {r4(foot * 0.46)}", "sides": 12, "thickness": 0.1,
                             "head": {"profile": "bell", "waist": 0.74, "lift": 0.9}, "at": [[0, f"H * {r4(yb)}", 0, 0]], "when": {"tiers": word},
                             **({"_about": "the bell (ong rakhang), redented"} if n == 7 else {})})
        # (the bell is 1.64 of its radius high: the ringed spire from its crown to 0.9 of the height, its rings narrowing)
        rb = foot * 0.46
        add(f"spire {word}", {"type": "column", "radius": f"w * {r4(rb * 0.36)}", "taper": 0.18, "sides": 12,
                              "height": f"H * {r4(0.9 - yb)} - w * {r4(rb * 1.6)}", "at": [[0, f"H * {r4(yb)} + w * {r4(rb * 1.6)}", 0, 0]],
                              "when": {"tiers": word}, **({"_about": "the ringed spire (plong chanai)"} if n == 7 else {})})
        for j in range(6):
            f = j / 6 * 0.62
            add(f"ring {word} {j + 1}", {"type": "column", "radius": f"w * {r4(rb * 0.36 * (1 - 0.82 * f) + rb * 0.07)}", "sides": 12, "height": f"H * {r4((0.9 - yb) * 0.03)}",
                                         "at": [[0, f"H * {r4(yb + (0.9 - yb) * f)} + w * {r4(rb * 1.6 * (1 - f))}", 0, 0]], "when": {"tiers": word}})
    add("bud", {"type": "dome", "radius": "w * 0.035", "sides": 8, "thickness": 0.05, "head": {"profile": "onion", "bulge": 1.2, "neck": 0.6},
                "at": [[0, "H * 0.895", 0, 0]], "_about": "the lotus bud (pli)"})
    add("point", {"type": "column", "radius": "w * 0.012", "taper": 0.1, "sides": 6, "height": "H * 0.07", "at": [[0, "H * 0.93", 0, 0]],
                  "_about": "its point"})
    write("thai-spire", {
        "name": "Thai spire (yot prasat)",
        "_about": "A THAI SPIRE (yot prasat, the mondop's and the throne hall's): the redented house it stands on, `tiers` "
                  "three|five|seven redented storeys each flaring at its foot like a roof skirt and narrowing upward, the redented "
                  "bell, the ringed spire (plong chanai), the lotus bud and its point; `w` across its foot, `H` to its tip. y 0 its "
                  "foot. Written by tools/archgen/thai.py.",
        "params": {"detail": 4, "w": 6.0, "H": 18.0, "tiers": "seven"}, "build": list(parts), "parts": parts})


# ---- the bell chedi --------------------------------------------------------------------------------------------------
def chedi_component():
    parts = {}
    def add(n, d): parts[n] = d
    y = 0.0
    RND, SQ = {"plan": "round"}, {"plan": "square"}
    for i, (rr, hh) in enumerate([(1.55, 0.2), (1.43, 0.2), (1.31, 0.2)]):
        add(f"step {i + 1}", {"type": "column", "radius": f"r * {rr}", "height": f"r * {hh}", "sides": "n", "at": [[0, f"r * {r4(y)}", 0, 0]], "when": RND,
                              **({"_about": "the three round steps (thaen)"} if i == 0 else {})})
        add(f"step {i + 1} square", {"type": "prism", "plan": {"points": plan(BASE, f"r * {rr}")}, "height": f"r * {hh}", "at": [[0, f"r * {r4(y)}", 0, 0]], "when": SQ,
                                     **({"_about": "the redented square steps (the golden chedis')"} if i == 0 else {})})
        y += hh
    for i, (rr, hh) in enumerate([(1.2, 0.13), (1.12, 0.13), (1.05, 0.13)]):
        add(f"lotus {i + 1}", {"type": "column", "radius": f"r * {rr}", "taper": 0.93, "height": f"r * {hh}", "sides": "n", "at": [[0, f"r * {r4(y)}", 0, 0]], "when": RND,
                               **({"_about": "the three lotus rings (bua thalaeng)"} if i == 0 else {})})
        add(f"lotus {i + 1} square", {"type": "prism", "plan": {"points": plan(TIER, f"r * {rr}")}, "height": f"r * {hh}", "at": [[0, f"r * {r4(y)}", 0, 0]], "when": SQ})
        y += hh
    add("bell", {"type": "dome", "radius": "r", "sides": "n", "thickness": 0.2, "head": {"profile": "bell", "waist": 0.8, "lift": 0.92},
                 "at": [[0, f"r * {r4(y)}", 0, 0]], "_about": "the bell (ong rakhang)"})
    y += 1.72
    add("harmika", {"type": "box", "width": "r * 0.72", "length": "r * 0.72", "height": "r * 0.32", "at": [[0, f"r * {r4(y - 0.04)}", 0, 0]],
                    "_about": "the square harmika (balang) on the bell's crown"})
    add("harmika cornice", {"type": "box", "width": "r * 0.84", "length": "r * 0.84", "height": "r * 0.07", "at": [[0, f"r * {r4(y + 0.28)}", 0, 0]]})
    y += 0.35
    add("columns", {"type": "column", "radius": "r * 0.2", "sides": "n", "height": "r * 0.24", "at": [[0, f"r * {r4(y)}", 0, 0]],
                    "_about": "the ring of little columns (sao harn) under the spire"})
    y += 0.24
    add("spire", {"type": "column", "radius": "r * 0.19", "taper": 0.1, "sides": "n", "height": "sh * 0.86", "at": [[0, f"r * {r4(y)}", 0, 0]],
                  "_about": "the ringed spire (plong chanai)"})
    for j in range(8):
        f = j / 8 * 0.66
        add(f"ring {j + 1}", {"type": "column", "radius": f"r * {r4(0.19 * (1 - 0.9 * f) + 0.035)}", "sides": "n", "height": "sh * 0.018",
                              "at": [[0, f"r * {r4(y)} + sh * {r4(0.86 * f)}", 0, 0]]})
    add("bud", {"type": "dome", "radius": "r * 0.05", "sides": 8, "thickness": 0.05, "head": {"profile": "onion", "bulge": 1.2, "neck": 0.6},
                "at": [[0, f"r * {r4(y)} + sh * 0.84", 0, 0]], "_about": "the bud (pli)"})
    add("point", {"type": "column", "radius": "r * 0.016", "taper": 0.1, "sides": 6, "height": "sh * 0.1", "at": [[0, f"r * {r4(y)} + sh * 0.9", 0, 0]]})
    write("chedi", {
        "name": "Bell chedi",
        "_about": "A BELL CHEDI (Sri Lankan type, Phra Si Rattana Chedi): three steps (thaen) -- round, or redented square (`plan` "
                  "round|square: the golden chedis) -- three lotus rings, the bell `r` in radius, the square harmika (balang) on its "
                  "crown, the ring of columns, the ringed spire `sh` high, its bud and point. `n` sides round. y 0 its foot; its "
                  f"height {r4(y)} r + sh. Written by tools/archgen/thai.py.",
        "params": {"detail": 4, "r": 5.0, "sh": 20.0, "n": 32, "plan": "round"}, "build": list(parts), "parts": parts})
    return y


CHEDI_Y = 3.3   # (the chedi's height below its spire, in bell radii: chedi_component's y)


def chedi(H, r=None, plan_="round", n=32):
    """components/chedi's params for a chedi `H` high (its bell r: H / 7.5 by default, as Phra Si Rattana Chedi's)"""
    r = r if r else H / 7.5
    return {"r": r4(r), "sh": r4(H - CHEDI_Y * r), "plan": plan_, "n": n}


# ---- the prang -------------------------------------------------------------------------------------------------------
def prang_component():
    parts = {}
    def add(n, d): parts[n] = d
    y = 0.0
    for i, (ww, hh) in enumerate([(1.0, 0.07), (0.86, 0.06), (0.73, 0.05)]):
        add(f"terrace {i + 1}", {"type": "prism", "plan": {"points": plan(BASE, f"w * {r4(ww / 2)}")}, "height": f"H * {hh}", "at": [[0, f"H * {r4(y)}", 0, 0]],
                                 "when": {"base": "yes"}, **({"_about": "the three redented terraces"} if i == 0 else {})})
        y += hh
    add("body", {"type": "prism", "plan": {"points": plan(TIER, "w * 0.29")}, "height": "H * 0.17", "at": [["0", "H * 0.18 * by", 0, 0]],
                 "courses": [{"y": "H * 0.15", "h": "H * 0.02", "out": "w * 0.02", "profile": "cornice"}],
                 "_about": "the body (ruean that): the sanctum, redented"})
    add("porches", {"type": "box", "width": "w * 0.26", "length": "w * 0.64", "height": "H * 0.14", "at": [[0, "H * 0.18 * by", 0, 0], [0, "H * 0.18 * by", 0, Q]],
                    "_about": "a porch on each side, its false door"})
    add("porch roofs", {"type": "roof", "form": "gable", "width": "w * 0.3", "length": "w * 0.68", "pitch": 58, "overhang": 0.1,
                        "at": [[0, "H * (0.18 * by + 0.14)", 0, 0], [0, "H * (0.18 * by + 0.14)", 0, Q]]})
    tower = {"type": "shikhara", "width": "w * 0.58", "height": "H * 0.5", "rathas": "rathas", "step": "w * 0.022", "bhadra": 0.34, "top": 0.24,
             "bend": 1.5, "bhumis": "bhumis", "band": 0.06, "bandH": 0.3, "crown": False, "corners": {"scale": 0.17, "at": [0, 0.2, 0.4]},
             "at": [[0, "H * (0.18 * by + 0.17)", 0, 0]]}
    bud = {"type": "dome", "radius": "w * 0.07", "thickness": 0.08, "sides": 12, "head": {"profile": "onion", "bulge": 1.15, "neck": 0.55}, "at": [[0, 0, 0, 0]]}
    add("tower", {**tower, "when": {"lean": "no"}, "_about": "the corn-cob tower: its storeys bending in, a small copy on every corner of three of them"})
    add("tower lean", {**tower, "corners": {"scale": 0.2, "at": [0.12]}, "when": {"lean": "yes"}, "_about": "(lean: the corner copies on one storey)"})
    add("bud", {**bud, "atop": "tower", "when": {"lean": "no"}, "_about": "the lotus bud on the tower's top"})
    add("bud lean", {**bud, "atop": "tower lean", "when": {"lean": "yes"}})
    add("spike", {"type": "column", "radius": "w * 0.018", "taper": 0.1, "sides": 6, "height": "H * 0.12", "at": [[0, "H * (0.18 * by + 0.67 + 0.035)", 0, 0]],
                  "_about": "the spike (naphasun): Shiva's trident"})
    write("prang", {
        "name": "Prang",
        "_about": "A PRANG, the Khmer tower as Bangkok built it (Prasat Phra Thep Bidon's, Wat Arun's, the eight Phra Atthamaha "
                  "Chedi): three redented terraces (`base` yes|no -- no: on a building's crossing), the body with a porch on each side, "
                  "the corn-cob tower bending in through `bhumis` storeys (7) on its `rathas` (5) plan, a small copy on every corner (`lean` yes: on one storey only), the bud and the spike. "
                  "`w` across its foot, `H` to its tip; y 0 its foot. Written by tools/archgen/thai.py.",
        "params": {"detail": 4, "w": 9.0, "H": 20.0, "base": "yes", "by": "1", "rathas": 5, "bhumis": 7, "lean": "no"}, "build": list(parts), "parts": parts})


def prang(w, H, base=True, lean=False):
    """components/prang's params; `lean`: fewer rathas and storeys on the tower (a distant or a little one)"""
    return {"w": r4(w), "H": r4(H), "base": "yes" if base else "no", "by": 1 if base else 0, **({"rathas": 3, "bhumis": 5, "lean": "yes"} if lean else {})}


# ---- the wall and the gate -------------------------------------------------------------------------------------------
SEMA = [(-0.5, 0), (0.5, 0), (0.5, 0.3), (0.34, 0.64), (0, 1.0), (-0.34, 0.64), (-0.5, 0.3)]   # (the leaf, in few points: there are thousands)


def wall_component():
    parts = {
        "wall": {"type": "box", "width": "L", "length": "t", "height": "H", "at": [[0, 0, 0, 0]], "_about": "the wall: whitewashed brick"},
        "coping": {"type": "box", "width": "L", "length": "t + 0.24", "height": "cap", "at": [[0, "H", 0, 0]], "_about": "its coping, moulded"},
        "plinth": {"type": "box", "width": "L", "length": "t + 0.3", "height": 0.5, "at": [[0, 0, 0, 0]]},
        "merlons": {"type": "screen", "outline": [[f"{x} * mw", f"{y} * mh"] for x, y in SEMA], "t": "mt",
                    "at": [["-(nm - 1) * ms / 2", "H + cap", "t / 2 + 0.06", 0]], "repeat": {"count": "nm", "step": ["ms", 0, 0, 0]},
                    "_about": "the merlons, each a bai sema -- the boundary stone's leaf -- in a row on the outer edge"},
        "walk merlons": {"type": "screen", "outline": [[f"{x} * mw * 0.8", f"{y} * mh * 0.8"] for x, y in SEMA], "t": "mt",
                         "at": [["-(nm - 1) * ms / 2", "H + cap", "-t / 2 + mt - 0.06", 0]], "repeat": {"count": "nm", "step": ["ms", 0, 0, 0]},
                         "when": {"inner": "yes"}, "_about": "and on the inner edge, smaller"},
    }
    write("thai-wall", {
        "name": "Thai palace wall",
        "_about": "A STRETCH OF THAI PALACE WALL `L` long: whitewashed brick `H` high and `t` thick on its plinth, the coping `cap` deep, "
                  "and the merlons in a row on its outer (+z) edge -- each a BAI SEMA, the leaf-shaped boundary stone, `mw` x `mh`, "
                  "`ms` apart (`inner` yes: a row on the inner edge too). Centred on its middle, along x. Written by tools/archgen/thai.py.",
        "params": {"detail": 4, "L": 20.0, "H": 4.6, "t": 1.4, "cap": 0.3, "mw": 0.75, "mh": 1.05, "ms": 1.5, "mt": 0.32,
                   "nm": "max(1, floor((L - 0.8) / ms) + 1)", "inner": "no"},
        "build": list(parts), "parts": parts})


def wall_run(add, name, pts, H=4.6, t=1.4, out=1, closed=False, gaps=(), inner=False, about=None, first_about=True):
    """thai-wall stretches along `pts` [(x, z)], the merlons on the side `out` (+1: the right walking along the line, -1 the left),
    broken by `gaps` [((x, z), width)] (a gate: its piers stand there). Returns the part names."""
    names = []
    segs = list(zip(pts, pts[1:] + ([pts[0]] if closed else [])))
    for i, (p, q) in enumerate(segs):
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        if L < 0.6: continue
        ex, ez = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        # cut the stretch where a gate stands on it
        spans = [(0.0, L)]
        for (gx, gz), gw in gaps:
            a = (gx - p[0]) * ex + (gz - p[1]) * ez
            d = abs(-(gx - p[0]) * ez + (gz - p[1]) * ex)
            if d > 3.0 or a < -gw / 2 or a > L + gw / 2: continue
            nsp = []
            for s0, s1 in spans:
                if a + gw / 2 <= s0 or a - gw / 2 >= s1: nsp.append((s0, s1)); continue
                if a - gw / 2 - s0 > 0.6: nsp.append((s0, a - gw / 2))
                if s1 - (a + gw / 2) > 0.6: nsp.append((a + gw / 2, s1))
            spans = nsp
        for j, (s0, s1) in enumerate(spans):
            ln = s1 - s0
            # (the merlons' side -- the wall's +z -- to the right of the line, out = +1: right = (-ez, ex); local +z goes
            #  to (sin yaw, cos yaw) and local +x to (cos yaw, -sin yaw) -- so +x along the line: yaw = atan2(-ez, ex))
            yaw = math.atan2(-ez, ex) if out > 0 else math.atan2(ez, -ex)
            mx, mz = p[0] + ex * (s0 + s1) / 2, p[1] + ez * (s0 + s1) / 2
            nm = f"{name} {i + 1}" + (f"-{j + 1}" if len(spans) > 1 else "")
            add(nm, {"type": "component", "use": "components/thai-wall",
                     "params": {"L": r4(ln + t * 0.5), "H": H, "t": t, **({"inner": "yes"} if inner else {})},
                     "at": [[r4(mx), 0, r4(mz), r4(yaw)]], **({"_about": about} if about and not names else {})})
            names.append(nm)
    return names


def gate_component():
    parts = {
        "piers": {"type": "box", "width": "(w - pw) / 2", "length": "d", "height": "bh", "at": [["(w + pw) / 4", 0, 0, 0], ["-(w + pw) / 4", 0, 0, 0]],
                  "_about": "the piers, the passage between"},
        "lintel": {"type": "box", "width": "pw", "length": "d", "height": "bh - ph", "at": [[0, "ph", 0, 0]], "_about": "the lintel over the passage"},
        "cornice": {"type": "box", "width": "w + 0.5", "length": "d + 0.5", "height": 0.45, "at": [[0, "bh", 0, 0]], "_about": "the cornice"},
        "attic": {"type": "prism", "plan": {"points": plan(TIER, "min(w, d) * 0.42")}, "height": "(H - bh) * 0.1", "at": [[0, "bh + 0.45", 0, 0]],
                  "_about": "the attic the crown stands on"},
        "spire": {"type": "component", "use": "components/thai-spire", "params": {"w": "min(w, d) * 0.62", "H": "(H - bh) * 0.9 - 0.45", "tiers": "tiers"},
                  "at": [[0, "bh + 0.45 + (H - bh) * 0.1", 0, 0]], "when": {"crown": "spire"}, "_about": "the crown: a spire of tiers"},
        "prang": {"type": "component", "use": "components/prang", "params": {"w": "min(w, d) * 0.7", "H": "(H - bh) * 0.9 - 0.45", "base": "no", "by": 0, "lean": "lean"},
                  "at": [[0, "bh + 0.45 + (H - bh) * 0.1", 0, 0]], "when": {"crown": "prang"}, "_about": "the crown: a prang"},
    }
    write("thai-gate", {
        "name": "Thai gate",
        "_about": "A GATE in a Thai wall (pratu): two piers `w` across all told and `d` deep, the passage `pw` wide and `ph` high under "
                  "the lintel, the body `bh` high, its cornice and attic, and the crown to `H`: a thai-spire of `tiers` (`crown` spire) "
                  "or a prang (`crown` prang; `lean` yes: a lean one). The way through runs along z. Written by tools/archgen/thai.py.",
        "params": {"detail": 4, "w": 7.0, "d": 4.0, "pw": 3.0, "ph": 4.2, "bh": 6.0, "H": 16.0, "crown": "spire", "tiers": "five", "lean": "no"},
        "build": list(parts), "parts": parts})


# ---- the figures -------------------------------------------------------------------------------------------------------
def _sec(s, u, v, a, b, n=2.2, b2=None, a2=None, k="S"):
    q = {"s": f"{r4(s)} * {k}" if s else 0, "u": f"{r4(u)} * {k}" if u else 0, "v": f"{r4(v)} * {k}" if v else 0,
         "a": f"{r4(a)} * {k}", "b": f"{r4(b)} * {k}", "n": n}
    if b2 is not None: q["b2"] = f"{r4(b2)} * {k}"
    if a2 is not None: q["a2"] = f"{r4(a2)} * {k}"
    return q


def _loft(axis, secs, sides=12, smooth=2, about=None, y="plinthH"):
    d = {"type": "loft", "axis": axis, "sides": sides, "smooth": smooth, "sections": secs, "at": [[0, y, 0, 0]]}
    if about: d["_about"] = about
    return d


def yaksha_component():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    add("plinth", {"type": "box", "width": "S * 0.5", "length": "S * 0.36", "height": "plinthH", "at": [[0, 0, "S * 0.04", 0]],
                   "_about": "the pedestal he stands on"})
    for side, sx in (("right", -1), ("left", 1)):     # (his right on -x: he faces +z)
        add(f"leg {side}", _loft("y", [_sec(0.02, sx * 0.11, 0.0, 0.034, 0.036), _sec(0.12, sx * 0.112, 0.0, 0.042, 0.046),
                                       _sec(0.23, sx * 0.108, 0.012, 0.043, 0.046), _sec(0.34, sx * 0.1, 0.0, 0.064, 0.066),
                                       _sec(0.45, sx * 0.085, 0.0, 0.076, 0.072)], sides=10,
                                 about="the legs set apart, the knees a little bent" if side == "right" else None))
        add(f"foot {side}", _loft("z", [_sec(-0.04, sx * 0.112, 0.016, 0.03, 0.016), _sec(0.02, sx * 0.115, 0.02, 0.04, 0.022),
                                        _sec(0.09, sx * 0.12, 0.012, 0.035, 0.012)], sides=8))
        add(f"upper arm {side}", _loft("y", [_sec(0.555, sx * 0.205, 0.085, 0.043, 0.043), _sec(0.63, sx * 0.21, 0.04, 0.05, 0.05),
                                             _sec(0.7, sx * 0.19, 0.0, 0.056, 0.056)], sides=10,
                                       about="the arms: down from the shoulders, the forearms in to the club's head" if side == "right" else None))
        add(f"forearm {side}", _loft("z", [_sec(0.07, sx * 0.2, 0.56, 0.044, 0.044), _sec(0.13, sx * 0.13, 0.53, 0.04, 0.04),
                                           _sec(0.185, sx * 0.065, 0.52, 0.042, 0.04), _sec(0.215, sx * 0.032, 0.52, 0.03, 0.035)], sides=10))
        add(f"bracelet {side}", _loft("y", [_sec(0.555, sx * 0.205, 0.085, 0.05, 0.05), _sec(0.585, sx * 0.207, 0.07, 0.052, 0.052)], sides=10, smooth=1))
    add("skirt", _loft("y", [_sec(0.36, 0, 0.0, 0.2, 0.125, 2.4), _sec(0.42, 0, 0.0, 0.185, 0.115, 2.4), _sec(0.5, 0, 0.0, 0.16, 0.1, 2.4)],
                       sides=14, about="the skirt (chong kraben) and its flaps"))
    add("torso", _loft("y", [_sec(0.48, 0, 0.0, 0.14, 0.092), _sec(0.56, 0, 0.012, 0.136, 0.09), _sec(0.64, 0, 0.0, 0.165, 0.09),
                             _sec(0.705, 0, -0.005, 0.195, 0.085), _sec(0.745, 0, 0.0, 0.07, 0.055)], sides=14, smooth=3,
                       about="the torso: the belly, the deep chest, the broad shoulders"))
    add("belt", _loft("y", [_sec(0.48, 0, 0.0, 0.15, 0.1), _sec(0.51, 0, 0.0, 0.148, 0.098)], sides=14, smooth=1))
    add("collar", _loft("y", [_sec(0.655, 0, 0.0, 0.18, 0.1, 2.4), _sec(0.7, 0, 0.0, 0.21, 0.098, 2.4), _sec(0.735, 0, 0.0, 0.12, 0.07)],
                        sides=14, smooth=1, about="the jewelled collar over the shoulders"))
    add("head", _loft("y", [_sec(0.735, 0, 0.0, 0.05, 0.05), _sec(0.765, 0, 0.012, 0.064, 0.07), _sec(0.8, 0, 0.012, 0.066, 0.07),
                            _sec(0.835, 0, 0.0, 0.055, 0.056)], sides=12, smooth=2, about="the head: the glaring eyes, the tusks"))
    add("ears", _loft("x", [_sec(-0.09, 0.0, 0.79, 0.022, 0.05), _sec(0.0, 0.0, 0.79, 0.022, 0.05), _sec(0.09, 0.0, 0.79, 0.022, 0.05)], sides=8, smooth=1))
    add("crown", _loft("y", [_sec(0.82, 0, 0.0, 0.066, 0.066), _sec(0.85, 0, 0.0, 0.058, 0.058), _sec(0.87, 0, 0.0, 0.046, 0.046),
                             _sec(0.885, 0, 0.0, 0.052, 0.052), _sec(0.905, 0, 0.0, 0.036, 0.036), _sec(0.92, 0, 0.0, 0.041, 0.041),
                             _sec(0.94, 0, 0.0, 0.025, 0.025), _sec(0.955, 0, 0.0, 0.029, 0.029), _sec(0.975, 0, 0.0, 0.012, 0.012),
                             _sec(1.0, 0, 0.0, 0.002, 0.002)], sides=10, smooth=1, about="the tall tiered crown (chada), its tiers stepping in to a point"))
    add("club", {"type": "column", "radius": "S * 0.024", "taper": 0.75, "sides": 8, "height": "S * 0.52", "at": [[0, "plinthH", "S * 0.205", 0]],
                 "_about": "the club (krabong) planted before him, his hands on its head"})
    add("club head", {"type": "column", "radius": "S * 0.03", "taper": 0.8, "sides": 8, "height": "S * 0.06", "at": [[0, "plinthH + S * 0.47", "S * 0.205", 0]]})
    write("yaksha", {"name": "Yaksha",
                     "_about": "A YAKSHA, the giant guarding a Thai temple's gate (Wat Phra Kaew's twelve, after the Ramakien): standing on his "
                               "pedestal `plinthH` high, feet apart, both hands on the head of the club planted before him; the skirt, the belt, "
                               "the jewelled collar, the bracelets, the glaring head and the tall tiered crown (chada). Carved in lofts; `S` his "
                               "height to the crown's tip, facing +z. The skin parts (legs, feet, arms, torso, head, ears) take his colour, the "
                               "rest is his costume. Written by tools/archgen/thai.py.",
                     "params": {"detail": 4, "S": 6.0, "plinthH": 1.2}, "build": build, "parts": parts})


def buddha_component():
    parts, build = {}, []
    def add(n, d): parts[n] = d; build.append(n)
    add("legs", _loft("x", [_sec(-0.42, 0.05, 0.08, 0.1, 0.06), _sec(-0.32, 0.06, 0.1, 0.2, 0.09), _sec(0.0, 0.05, 0.11, 0.24, 0.1),
                            _sec(0.32, 0.06, 0.1, 0.2, 0.09), _sec(0.42, 0.05, 0.08, 0.1, 0.06)], sides=12, smooth=2, y=0,
                      about="the legs crossed in the lotus seat, the soles up"))
    add("torso", _loft("y", [_sec(0.12, 0, -0.02, 0.22, 0.15), _sec(0.32, 0, -0.03, 0.19, 0.12), _sec(0.52, 0, -0.03, 0.225, 0.12),
                             _sec(0.6, 0, -0.03, 0.09, 0.08)], sides=12, smooth=2, y=0, about="the torso, upright"))
    add("head", _loft("y", [_sec(0.59, 0, -0.02, 0.07, 0.075), _sec(0.66, 0, -0.01, 0.1, 0.105), _sec(0.74, 0, -0.02, 0.1, 0.1),
                            _sec(0.79, 0, -0.03, 0.07, 0.07)], sides=12, smooth=2, y=0, about="the head, the long ears"))
    add("ushnisha", _loft("y", [_sec(0.775, 0, -0.03, 0.06, 0.06), _sec(0.82, 0, -0.03, 0.045, 0.045), _sec(0.86, 0, -0.03, 0.02, 0.02),
                                _sec(1.0, 0, -0.03, 0.004, 0.004)], sides=8, smooth=1, y=0, about="the ushnisha and its flame"))
    for side, sx in (("right", -1), ("left", 1)):
        add(f"upper arm {side}", _loft("y", [_sec(0.26, sx * 0.24, 0.02, 0.055, 0.055), _sec(0.42, sx * 0.25, -0.02, 0.06, 0.06),
                                             _sec(0.53, sx * 0.21, -0.03, 0.065, 0.065)], sides=8, smooth=1, y=0))
        add(f"forearm {side}", _loft("z", [_sec(0.0, sx * 0.235, 0.24, 0.05, 0.05), _sec(0.1, sx * 0.14, 0.2, 0.045, 0.04),
                                           _sec(0.16, sx * 0.05, 0.19, 0.05, 0.03)], sides=8, smooth=1, y=0))
    write("seated-buddha", {"name": "Seated Buddha",
                            "_about": "A BUDDHA seated cross-legged in meditation, his hands in his lap, the ushnisha's flame on his head (the "
                                      "Emerald Buddha's pose): carved in lofts, `S` high to the flame's tip, facing +z, y 0 his seat. Written by "
                                      "tools/archgen/thai.py.",
                            "params": {"detail": 4, "S": 1.0}, "build": build, "parts": parts})


def gate(w, d, pw, ph, H, crown="spire", tiers="five", bh=None, lean=False):
    return {"w": r4(w), "d": r4(d), "pw": r4(pw), "ph": r4(ph), "bh": r4(bh if bh else ph + max(1.2, w * 0.25)), "H": r4(H), "crown": crown, "tiers": tiers,
            **({"lean": "yes"} if lean else {})}


def write_components():
    gable_component()
    hall_component()
    cross_component()
    roof_component()
    spire_component()
    y = chedi_component()
    assert abs(y - CHEDI_Y) < 1e-6, y
    prang_component()
    wall_component()
    gate_component()
    yaksha_component()
    buddha_component()


if __name__ == "__main__":
    write_components()
