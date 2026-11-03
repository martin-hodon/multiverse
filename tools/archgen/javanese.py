# THE CENTRAL JAVANESE TEMPLE (candi), 8th-10th century -- Prambanan, Sewu, Plaosan, Kalasan, Sambisari -- as rules, and the
# components they are built of. Run it to (re)write them:
#
#   components/ratna      the RATNA, the jewel finial a Javanese roof bristles with, `h` high to its tip and `r` across its
#                         foot's half, `n` sides: `form` "vajra" (Prambanan's Hindu form: a swelling drum and a long point --
#                         slender and cheap), "bell" (the Buddhist form: a square foot, a bell, a point -- Sewu, Plaosan) or
#                         "spike" (a four-sided point alone, for temples seen by the hundred)
#   components/candi      the TEMPLE: the base (kaki, the world of men) with its mouldings, a balustraded gallery round it
#                         (`gallery` "yes": the walk the reliefs are read from, crowned with ratnas, a gate where each stair
#                         arrives); its stairs (`stairs` "four" | "two" | "one" | "none": "one" on the front, +z, "two" the
#                         front and the right, +x -- a corner perwara's); the body (tubuh, the world of the holy) -- the
#                         cella's walls with the door at the back of the front porch (`cella` "open"), or a solid with false
#                         doors (`cella` "solid"); a porch on every stair's side (on a four-stair temple the side porches are
#                         chambers of their own, entered only from outside, as Shiva's at Prambanan); and the roof (atap, the
#                         world of the gods): `tiers` "three" | "four" | "five" storeys, each a smaller copy of the redented
#                         square by `k`, every ledge ringed with ratnas (`ratnas` "corners" | "three" | "five" | "seven" a
#                         side), the crowning ratna on top. `mould` "yes" | "no": moulded, or plain blocks (the cheap one).
#                         Every size is a param; `candi()` below works them out from the temple's width and height by the
#                         proportions of the type, and `finish_rules()` gives a temple's reliefs at its own scale.
#   components/paduraksa  a roofed GATE in a court wall: two piers, the lintel over the passage, a stepped roof bristling with
#                         ratnas, its crowning one.
#
# The plans are REDENTED squares: each side a projection in its middle and steps back toward the corners, written as a
# profile (t, d) from the axis to the corner in fractions of the half-width (t along the side, d out from the middle, the
# last step the corner, t = d). Front +z; y 0 on the ground.
import os, sys, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMP = os.path.join(ROOT, "assets", "architecture", "components")
r4 = lambda v: round(v, 4)
SIDES = [0, math.pi / 2, math.pi, 3 * math.pi / 2]   # the four sides by the angle of their axis from +z toward +x
Q = {0: ["one", "two", "four"], 1: ["two", "four"], 2: ["four"], 3: ["four"]}   # which `stairs` give a stair (a porch) on each side
TIERS = {1: None, 2: None, 3: None, 4: ["four", "five"], 5: ["five"]}           # which `tiers` have the i-th

# the profiles (fractions of the half-width)
BASE = [(0.40, 1.0), (0.70, 0.94), (0.86, 0.86)]    # the base: the stair projection, a step, the corner
TIER = [(0.48, 1.0), (0.78, 0.93), (0.88, 0.88)]    # a roof tier: the bhadra, a step, the corner


def X(k, var):
    """the expression k * var (k a number, var a param or an expression)"""
    k = r4(k)
    if k == 0: return 0
    if k == 1: return var
    if k == -1: return f"-({var})"
    return f"{k} * ({var})" if any(c in var for c in "+-") else f"{k} * {var}"


def frame(phi, lat, rad):
    """a point `lat` along the side whose axis is `phi` from +z (in planPoints' winding) and `rad` out from the middle"""
    return (lat * math.cos(phi) + rad * math.sin(phi), -lat * math.sin(phi) + rad * math.cos(phi))


def outline(prof):
    """the redented square as unit points (half-width 1) in planPoints' kept winding, every corner of it"""
    half = []
    for i, (t, d) in enumerate(prof[:-1]):
        half += [(t, d), (t, prof[i + 1][1])]
    half.append(prof[-1])                                  # (the corner: it ends this side, the next begins after it)
    side = [(-t, d) for t, d in reversed(half)][1:] + half
    pts = []
    for phi in SIDES:
        pts += [tuple(round(v, 9) + 0.0 for v in frame(phi, t, d)) for t, d in side]
    return pts


def plan(prof, half):
    """the outline's points as expressions of `half` (the half-width's expression)"""
    return [[X(x, half), X(z, half)] for x, z in outline(prof)]


def axis_faces(prof):
    """the index of the face crossing each axis (+z, +x, -z, -x: sides 0-3) and that face's length in half-widths"""
    pts = outline(prof); out = {}
    for e in range(len(pts)):
        (x0, z0), (x1, z1) = pts[e], pts[(e + 1) % len(pts)]
        mx, mz = (x0 + x1) / 2, (z0 + z1) / 2
        if abs(mx) < 1e-9 and z0 == z1 and mz > 0: out[0] = (e, abs(x1 - x0))
        if abs(mz) < 1e-9 and x0 == x1 and mx > 0: out[1] = (e, abs(z1 - z0))
        if abs(mx) < 1e-9 and z0 == z1 and mz < 0: out[2] = (e, abs(x1 - x0))
        if abs(mz) < 1e-9 and x0 == x1 and mx < 0: out[3] = (e, abs(z1 - z0))
    return out


def rot(at, q):
    """a placement [x, y, z, yaw] (numbers or expressions) turned a quarter q times about the origin (yaw as three.js: +z goes
    to +x)"""
    x, y, z, yaw = at
    neg = lambda e: 0 if e == 0 else (-e if isinstance(e, (int, float)) else f"-({e})")
    for _ in range(q):
        x, z = z, neg(x)
    return [x, y, z, r4(yaw + q * math.pi / 2)]


def write(name, doc):
    p = os.path.join(COMP, name + ".json")
    with open(p, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print("wrote", os.path.relpath(p, ROOT), len(doc["parts"]), "parts")


# ---- the ratna -------------------------------------------------------------------------------------------------------
def ratna_component():
    V, B, S = {"form": "vajra"}, {"form": "bell"}, {"form": "spike"}
    parts = {
        "swell": {"type": "column", "radius": "r", "taper": 0.55, "height": "h * 0.45", "sides": "n", "at": [[0, 0, 0, 0]], "when": V,
                  "_about": "the vajra's body: a drum swelling to its shoulder"},
        "point": {"type": "column", "radius": "r * 0.55", "taper": 0, "height": "h * 0.55", "sides": "n", "at": [[0, "h * 0.45", 0, 0]], "when": V,
                  "_about": "the long point"},
        "foot": {"type": "box", "width": "r * 2", "length": "r * 2", "height": "h * 0.2", "at": [[0, 0, 0, 0]], "when": B,
                 "_about": "the square stepped foot (padma)"},
        "bell": {"type": "dome", "radius": "rb", "sides": "n", "head": {"profile": "bell", "waist": 0.78, "lift": 0.85},
                 "at": [[0, "h * 0.2", 0, 0]], "when": B, "_about": "the bell, as a little stupa's (its height 1.63 of its radius)"},
        "tip": {"type": "column", "radius": "rb * 0.3", "taper": 0.12, "height": "h * 0.8 - rb * 1.55", "sides": "n", "at": [[0, "h * 0.2 + rb * 1.55", 0, 0]],
                "when": B, "_about": "the bell's pointed top, to the ratna's height"},
        "spike": {"type": "pyramid", "base": "r * 2", "height": "h", "at": [[0, 0, 0, 0]], "when": S,
                  "_about": "the far form: a four-sided point, square with its temple"},
    }
    write("ratna", {
        "name": "Ratna",
        "_about": "A RATNA, the jewel finial a Central Javanese roof bristles with, `h` high to its tip, `r` its foot's half-width, "
                  "`n` its sides. `form` \"vajra\": Prambanan's Hindu form -- a swelling drum and a long point; \"bell\": the "
                  "Buddhist form (a square foot, a bell like a small stupa's -- as wide as `r` allows within the height -- and its "
                  "point); \"spike\": a four-sided point alone, for temples seen by the hundred. y 0 on the ledge it stands on. "
                  "Written by tools/archgen/javanese.py.",
        "params": {"detail": 4, "r": 0.4, "h": 1.6, "n": 6, "form": "vajra", "rb": "min(r, h * 0.28)"},
        "build": list(parts), "parts": parts})


# ---- the temple ------------------------------------------------------------------------------------------------------
def candi_component():
    parts = {}
    def add(n, d): parts[n] = d
    bf = axis_faces(BASE)
    W2 = "w / 2"
    ST = ["one", "two", "four"]
    STAIRS = {"four": [0, 1, 2, 3], "two": [0, 1], "one": [0], "none": []}

    # THE BASE: a redented prism from the ground, its top the gallery's floor; moulded round its outline (stopping where a
    # stair stands against it) -- or a plain block
    MOULD = [{"y": 0, "h": "min(0.5, bh * 0.2)", "out": "min(0.3, bh * 0.12)", "profile": "torus"},
             {"y": "min(0.5, bh * 0.2)", "h": "min(0.3, bh * 0.1)", "out": "min(0.15, bh * 0.06)", "profile": "band"},
             {"y": "bh - min(0.7, bh * 0.25)", "h": "min(0.7, bh * 0.25)", "out": "min(0.35, bh * 0.14)", "profile": "cornice"}]
    def clear(sides):
        out = {}
        for s in sides:
            e, L = bf[s]; m = X(L / 2, W2)
            out[str(e)] = [[f"{m} - sw / 2 - 0.2", f"{m} + sw / 2 + 0.2"]]
        return out
    base = {"type": "prism", "plan": {"points": plan(BASE, W2)}, "height": "bh", "walked": True, "at": [[0, 0, 0, 0]],
            "_about": "the base (kaki): a redented square, its top the gallery's floor"}
    for word, sides in STAIRS.items():
        add("base" if word == "four" else f"base {word}", {**base, "courses": {"list": MOULD, "clear": clear(sides)} if sides else MOULD,
                                                            "when": {"stairs": word, "mould": "yes"}})
    add("base plain", {"type": "box", "width": "w", "length": "w", "height": "bh", "walked": True, "at": [[0, 0, 0, 0]], "when": {"mould": "no"},
                       "_about": "the base as a plain block: the cheap one"})

    # THE GALLERY: a balustrade on the base's edge (its wall inward from it), the reliefs on its inner face, broken where a
    # stair comes up; ratnas on its outer corners and either side of each axis; a gate over each stair's head
    balu = {"type": "enclosure", "plan": {"points": plan(BASE, W2)}, "thickness": "bt", "height": "bah", "glass": False, "openings": [],
            "at": [[0, "bh", 0, 0]], "courses": {"list": [{"y": "bah - 0.25", "h": 0.25, "out": 0.08, "profile": "band"}]},
            "_about": "the balustrade round the gallery: the reliefs on its inner face, broken where the stairs come up"}
    for word, sides in STAIRS.items():
        add("balustrade" if word == "four" else f"balustrade {word}",
            {**balu, "faces": {str(bf[s][0]): [{"at": 0, "width": "sw + 0.2", "sill": 0, "springing": "bah", "head": {"profile": "flat"}}] for s in sides},
             "when": {"gallery": "yes", "stairs": word}})
    pts = outline(BASE); at = []; seen = set()
    for e in range(len(pts)):
        (x0, z0), (x1, z1) = pts[e], pts[(e + 1) % len(pts)]
        L = math.hypot(x1 - x0, z1 - z0); ux, uz = (x1 - x0) / L, (z1 - z0) / L; ox, oz = -uz, ux
        mx, mz = (x0 + x1) / 2, (z0 + z1) / 2
        onaxis = abs(mx * ux + mz * uz) < 1e-9 and (abs(mx) < 1e-9 or abs(mz) < 1e-9)
        cand = [-L * 0.36, L * 0.36] if onaxis else []
        (x2, z2) = pts[(e + 2) % len(pts)]
        if ux * (z2 - z1) - uz * (x2 - x1) < 0: cand.append(L / 2)      # (and its end, where that is an outer corner)
        for a in cand:
            px, pz = mx + ux * a, mz + uz * a
            if (round(px, 4), round(pz, 4)) in seen: continue
            seen.add((round(px, 4), round(pz, 4)))
            inset = lambda p, o: X(p, W2) if not o else f"{X(p, W2)} {'-' if o > 0 else '+'} {r4(abs(o))} * bt / 2"
            at.append([inset(px, ox), "bh + bah", inset(pz, oz), 0])
    add("balustrade ratnas", {"type": "component", "use": "components/ratna", "params": {"r": "rb * 0.22", "h": "rb", "n": 6, "form": "ratna", "detail": 2},
                              "at": at, "when": {"gallery": "yes"}, "_about": "the ratnas crowning the balustrade"})

    # each side's stair, makaras, gate and porch: drawn on the sides `stairs` gives one (Q)
    fl = {"type": "flight", "width": "sw", "run": "run", "rise": "bh / stairN", "base": 0, "top": "bh", "landing": 0, "steep": True}
    mk = {"type": "box", "width": "0.5 + bh * 0.08", "length": "0.9 + bh * 0.1", "height": "0.9 + bh * 0.08",
          "_about": "the makara at the stair's foot, either side: the sea monster whose jaws the balustrade comes out of"}
    gz = f"{W2} - bt / 2"
    gate = {"piers": ({"type": "box", "width": 0.9, "length": "bt + 0.4", "height": "gH + 0.6", "_about": "the gate's piers"},
                      [[f"sw / 2 + 0.55", "bh", gz, 0], [f"-(sw / 2 + 0.55)", "bh", gz, 0]]),
            "lintel": ({"type": "box", "width": "sw + 2", "length": "bt + 0.4", "height": 0.6, "_about": "the lintel over the stair's head, a kala's face on it"},
                       [[0, "bh + gH", gz, 0]]),
            "cap": ({"type": "box", "width": "sw + 1.2", "length": "bt + 0.1", "height": 0.7}, [[0, "bh + gH + 0.6", gz, 0]]),
            "ratna": ({"type": "component", "use": "components/ratna", "params": {"r": "rb * 0.35", "h": "rb * 1.6", "n": 6, "form": "ratna", "detail": 2}},
                      [[0, "bh + gH + 1.3", gz, 0]])}
    pz = "bw / 2 + pd / 2"
    door = [{"at": 0, "width": "dw", "sill": 0, "springing": "dh", "head": {"profile": "flat"}}]
    proof = {"porch roof": ({"type": "box", "width": "pw + 0.4", "length": "pd + 0.2", "height": "min(0.4, pH * 0.08)"}, "bh + pH", "bw / 2 + pd / 2 + 0.1"),
             "porch step": ({"type": "box", "width": "pw * 0.74", "length": "pd * 0.76", "height": "pH * 0.16"}, "bh + pH + min(0.4, pH * 0.08)", pz),
             "porch top": ({"type": "box", "width": "pw * 0.46", "length": "pd * 0.5", "height": "pH * 0.12"}, "bh + pH * 1.16 + min(0.4, pH * 0.08)", pz)}
    for q in range(4):
        n = "" if q == 0 else f" {q + 1}"
        on = {"stairs": Q[q]}
        front = rot(["sw / 2", 0, f"{W2} + stairL", math.pi / 2], q)
        add(f"stair{n}", {**fl, "at": [front], "when": {**on, "mould": "yes"}, "_about": "the stair up the base, steep, its cheeks the building's stone railing"})
        add(f"stair plain{n}", {**fl, "at": [front], "railing": False, "when": {**on, "mould": "no"}, "_about": "the stair, no cheeks: the cheap one"})
        mz_ = f"{W2} + stairL - 0.45 - bh * 0.05"
        add(f"makaras{n}", {**mk, "at": [rot([f"sw / 2 + 0.25 + bh * 0.04", 0, mz_, 0], q), rot([f"-(sw / 2 + 0.25 + bh * 0.04)", 0, mz_, 0], q)],
                            "when": {**on, "mould": "yes"}})
        for k, (d, ats) in gate.items():
            add(f"gate {k}{n}", {**d, "at": [rot(a, q) for a in ats], "when": {**on, "gallery": "yes"}})
        # the porch: open (a vestibule through to the cella on the front; a chamber of its own on a side), or solid
        pa = rot([0, "bh", pz, 0], q)
        if q == 0:
            add("porch", {"type": "enclosure", "plan": {"rect": ["pw", "pd"]}, "thickness": "pt", "height": "pH", "glass": False, "openings": [],
                          "faces": {"0": door, "2": door}, "at": [pa], "when": {**on, "cella": "open"},
                          "_about": "the porch: the vestibule before the cella, its gate the kala-makara arch"})
        else:
            add(f"side porch{n}", {"type": "enclosure", "plan": {"rect": ["pw", "pd"]}, "thickness": "pt", "height": "pH", "glass": False, "openings": [],
                                   "faces": {"0": door}, "at": [pa], "when": {**on, "cella": "open"},
                                   "_about": "a side chamber, entered from its own stair only (Agastya's, Ganesha's, Durga's at Prambanan)"})
        add(f"porch floor{n}", {"type": "box", "width": "pw - 2 * pt", "length": "pd - 2 * pt", "height": 0.15, "walked": True, "at": [pa],
                                "when": {**on, "cella": "open"}})
        add(f"porch block{n}", {"type": "box", "width": "pw", "length": "pd", "height": "pH", "at": [pa], "when": {**on, "cella": "solid"},
                                "_about": "the porch, solid: its false door on its face"})
        if q == 0:
            add("false door", {"type": "box", "width": "dw", "length": 0.12, "height": "dh", "at": [[0, "bh", "bw / 2 + pd", 0]],
                               "when": {**on, "cella": "solid", "mould": "yes"}, "_about": "the false door, a dark panel (left off the cheap one)"})
        for k, (d, y, z) in proof.items():
            add(f"{k}{n}", {**d, "at": [rot([0, y, z, 0], q)], "when": {**on, "mould": "yes"} if k == "porch top" else on})   # (the cheap one: two steps)
        for m, y in (("yes", "bh + pH * 1.28 + min(0.4, pH * 0.08)"), ("no", "bh + pH * 1.16 + min(0.4, pH * 0.08)")):
            add(f"porch ratna{n}" + ("" if m == "yes" else " low"), {"type": "component", "use": "components/ratna", "at": [rot([0, y, pz, 0], q)],
                                "params": {"r": "min(pw, pd) * 0.12", "h": "pH * 0.5", "n": 6, "form": "ratna", "detail": 2},
                                "when": {**on, "mould": m}})   # (on the porch top; on the step where the cheap one has no top)
    add("blind false door", {"type": "box", "width": "dw", "length": 0.12, "height": "dh", "at": [[0, "bh", "bw / 2", 0]], "when": {"stairs": "none"}})

    # THE BODY: the cella's walls (a square: its thick walls can't follow the redents), its door at the front; or a solid
    BMOULD = [{"y": 0, "h": "min(0.6, bH * 0.06)", "out": "min(0.25, bH * 0.03)", "profile": "torus"},
              {"y": "bH - min(0.8, bH * 0.08)", "h": "min(0.8, bH * 0.08)", "out": "min(0.45, bH * 0.045)", "profile": "cornice"}]
    cella = {"type": "enclosure", "plan": {"rect": ["bw", "bw"]}, "thickness": "wt", "height": "bH", "glass": False, "openings": [],
             "faces": {"0": door}, "at": [[0, "bh", 0, 0]], "_about": "the body (tubuh): the cella's thick walls, its door at the back of the front porch"}
    add("cella", {**cella, "courses": {"list": BMOULD}, "when": {"cella": "open", "mould": "yes"}})
    add("cella plain", {**cella, "when": {"cella": "open", "mould": "no"}})
    body = {"type": "prism", "plan": {"rect": ["bw", "bw"]}, "height": "bH", "at": [[0, "bh", 0, 0]], "_about": "the body: solid, its doors false ones"}
    add("body", {**body, "courses": {"list": BMOULD}, "when": {"cella": "solid", "mould": "yes"}})
    add("body plain", {"type": "box", "width": "bw", "length": "bw", "height": "bH + cs", "at": [[0, "bh", 0, 0]], "when": {"cella": "solid", "mould": "no"},
                       "_about": "the body as a plain block, up to the roof (no slab)"})
    add("cella floor", {"type": "box", "width": "bw - 2 * wt", "length": "bw - 2 * wt", "height": 0.15, "walked": True, "at": [[0, "bh", 0, 0]],
                        "when": {"cella": "open"}, "_about": "the cella's floor"})
    add("ceiling", {"type": "box", "width": "bw + 0.6", "length": "bw + 0.6", "height": "cs", "at": [[0, "bh + bH", 0, 0]], "when": {"mould": "yes"},
                    "_about": "the slab over the body, its cornice's top: the roof stands on it"})
    add("ceiling open", {"type": "box", "width": "bw", "length": "bw", "height": "cs", "at": [[0, "bh + bH", 0, 0]], "when": {"cella": "open", "mould": "no"},
                         "_about": "the slab over a plain cella"})

    # THE ROOF: tiers, each a smaller copy of the redented square by `k` (width and height), its cornice moulded, its ledge
    # ringed with ratnas -- `ratnas` a side, the corners always; the crowning ratna on the last
    TCOR = [{"y": "th * 0.82", "h": "th * 0.18", "out": "tw * 0.02", "profile": "cornice"}]
    sets = {"corners": ([0.8], None), "mid": ([0.0], ["three", "five", "seven"]), "quarter": ([0.4], ["five"]), "sixth": ([0.2667, 0.5333], ["seven"])}
    for i in range(1, 6):
        hw = f"tw{i} / 2"
        when = {"tiers": TIERS[i]} if TIERS[i] else {}
        tat = [[0, f"y{i - 1}", 0, 0]]
        add(f"roof {i}", {"type": "prism", "height": f"t{i}", "at": tat, "plan": {"points": plan(TIER, hw)},
                          "courses": {"list": [{k: (v.replace("th", f"t{i}").replace("tw", f"tw{i}") if isinstance(v, str) else v) for k, v in c.items()}
                                               | ({} if i == 1 else {"profile": "plinth"}) for c in TCOR]},   # (above the first: a weathered ledge, half the faces)
                          "when": {**when, "mould": "yes"}, "_about": f"the roof's {['first', 'second', 'third', 'fourth', 'fifth'][i - 1]} tier: the body again, smaller"})
        add(f"roof {i} plain", {"type": "box", "width": f"tw{i} * 0.9", "length": f"tw{i} * 0.9", "height": f"t{i}", "at": tat, "when": {**when, "mould": "no"},
                                "_about": "the tier as a plain block: the cheap one"})
        rp = {"r": f"tw{i} * 0.035", "h": f"rr * {r4(0.8 ** (i - 1))}", "n": 6, "form": "ratna", "detail": 2}
        for nm, (ts, words) in sets.items():
            spots = []
            for t in ts:
                for s in ((1, -1) if t and nm != "corners" else (1,)):
                    for q in range(4):
                        d = 0.8 if nm == "corners" else 0.86
                        spots.append(rot([X(s * t, hw), f"y{i}", X(d, hw), 0], q))
            add(f"roof {i} ratnas {nm}", {"type": "component", "use": "components/ratna", "params": rp, "at": [[a[0], a[1], a[2], 0] for a in spots],
                                          "when": {**when, **({"ratnas": words} if words else {})}})
    for T, word in ((3, "three"), (4, "four"), (5, "five")):
        add(f"crown {word}", {"type": "component", "use": "components/ratna", "params": {"r": f"tw{T} * 0.14", "h": "ch", "n": 6, "form": "crownform"},
                              "at": [[0, f"y{T}", 0, 0]], "when": {"tiers": word}, "_about": "the crowning ratna: the vajra"})

    params = {"detail": 4,
              "w": 20, "bh": 3.0, "bt": 0.7, "bah": 1.5, "rb": 1.0, "gH": 2.6,
              "sw": 2.6, "rise": 0.28, "run": 0.26, "stairN": "max(1, round(bh / rise))", "stairL": "stairN * run",
              "bw": 10.0, "bH": 8.0, "wt": 1.4, "dw": 1.6, "dh": 2.9, "cs": 0.5,
              "pw": 5.0, "pd": 2.6, "pH": 5.0, "pt": 0.7,
              "tw": "bw * 0.92", "t1": 3.6, "k": 0.7, "rr": 1.5, "ch": 4.5,
              "tw1": "tw", "tw2": "tw * k", "tw3": "tw2 * k", "tw4": "tw3 * k", "tw5": "tw4 * k",
              "t2": "t1 * k", "t3": "t2 * k", "t4": "t3 * k", "t5": "t4 * k",
              "y0": "bh + bH + cs", "y1": "y0 + t1", "y2": "y1 + t2", "y3": "y2 + t3", "y4": "y3 + t4", "y5": "y4 + t5",
              "stairs": "one", "gallery": "yes", "cella": "open", "tiers": "three", "ratnas": "five", "ratna": "vajra", "crownform": "vajra", "mould": "yes"}
    write("candi", {
        "name": "Candi",
        "_about": "A CENTRAL JAVANESE TEMPLE (candi), 8th-10th century, Prambanan's type: three worlds stacked. The BASE (kaki) a "
                  "redented square `w` across and `bh` high, moulded; a GALLERY on it (`gallery` yes|no) inside a balustrade `bah` high "
                  "and `bt` thick, ratnas `rb` high on its top, a gate (`gH` clear) where each stair arrives; STAIRS `sw` wide and steep "
                  "(`stairs` four|two|one|none: one on the front, +z, two the front and +x), a makara either side of each foot. The "
                  "BODY (tubuh) a square `bw` across and `bH` high under a slab `cs` thick: the cella's walls `wt` thick with its "
                  "door (`dw` x `dh`) at the back of the front porch (`cella` open), or a solid with false doors (`cella` solid); a "
                  "PORCH `pw` x `pd`, `pH` high, on every stair's side, each under a stepped roof and a ratna. The ROOF (atap): `tiers` "
                  "three|four|five, the first `tw` across and `t1` high, each next one `k` of the last, every ledge ringed with "
                  "ratnas (`ratnas` corners|three|five|seven a side, `rr` high on the first), the crowning ratna `ch` high on top. "
                  "`ratna`/`crownform` vajra|bell|spike pick the ratnas' form, `mould` yes|no the mouldings (no: plain blocks, "
                  "the cheap one for a temple seen by the hundred). y 0 on the ground. Written by tools/archgen/javanese.py; its "
                  "candi() works the sizes out from a temple's width and height, finish_rules() its reliefs.",
        "params": params, "build": list(parts), "parts": parts})


# ---- the gate --------------------------------------------------------------------------------------------------------
def paduraksa_component():
    R = "(h - ph - 0.9)"                                   # the roof's height, crown included
    L = [("roof 1", 0.86, 0.22, 0), ("roof 2", 0.64, 0.17, 0.22), ("roof 3", 0.44, 0.13, 0.39)]
    parts = {
        "piers": {"type": "box", "width": "(w - pw) / 2", "length": "d", "height": "ph + 0.9", "at": [["(w + pw) / 4", 0, 0, 0], ["-(w + pw) / 4", 0, 0, 0]],
                  "_about": "the two piers, the passage between"},
        "lintel": {"type": "box", "width": "w", "length": "d", "height": 0.9, "at": [[0, "ph", 0, 0]], "_about": "the lintel, its kala"},
    }
    for nm, s, hh, y in L:
        parts[nm] = {"type": "box", "width": f"w * {s}", "length": f"d * {s}", "height": f"{R} * {hh}", "at": [[0, f"ph + 0.9 + {R} * {y}", 0, 0]]}
    for j, (nm, s, hh, y) in enumerate(L[:2]):
        yy = f"ph + 0.9 + {R} * {r4(y + hh)}"; e = r4(L[j + 1][1] / 2 + (s - L[j + 1][1]) / 4)
        parts[f"{nm} ratnas"] = {"type": "component", "use": "components/ratna", "params": {"r": "w * 0.035", "h": f"{R} * 0.16", "n": 6, "detail": 2},
                                 "at": [[f"w * {sx * e}", yy, f"d * {sz * e}", 0] for sx in (1, -1) for sz in (1, -1)] + [[0, yy, f"d * {sz * e}", 0] for sz in (1, -1)]}
    parts["crown"] = {"type": "component", "use": "components/ratna", "params": {"r": "w * 0.07", "h": f"{R} * 0.48", "n": 6},
                      "at": [[0, f"ph + 0.9 + {R} * 0.52", 0, 0]], "_about": "the crowning ratna"}
    write("paduraksa", {
        "name": "Paduraksa",
        "_about": "A PADURAKSA, the roofed gate in a Javanese court wall: two piers `w` across all told and `d` deep, the passage `pw` "
                  "wide and `ph` high under the lintel (a kala's face on it), a roof of three steps narrowing to a point, ratnas on "
                  "its ledges and the crowning one, `h` high in all. The way through runs along z. Written by tools/archgen/javanese.py.",
        "params": {"detail": 4, "w": 6.0, "d": 3.0, "pw": 2.6, "ph": 3.2, "h": 9.0},
        "build": list(parts), "parts": parts})


# ---- the rules: a temple's sizes from its width and height -------------------------------------------------------------
def candi(w, h, stairs="one", gallery=True, cella="open", tiers=3, ratnas="five", far=False, **over):
    """the params of components/candi for a temple `w` across its base and `h` high to the crown's tip, by the proportions of
    Prambanan's temples (read off their elevations: base about a tenth of the height, body about a quarter, roof and crown the
    rest; the gallery a fourteenth of the width; the body what the base leaves after gallery and porches). Small temples
    (kelir, patok: two metres) are clamped so every part keeps a size. `far`: the cheap one (no mouldings, plain blocks,
    spikes for ratnas). Anything in `over` is passed as it stands; `k` there changes the tiers too."""
    k = over.pop("k", 0.7)
    bh = r4(max(0.2, h * (0.09 if gallery else 0.085)))
    bt = r4(max(0.5, w * 0.025)) if gallery else 0.5
    gal = r4(max(1.6, w * 0.07)) if gallery else 0
    pd = 0 if stairs == "none" else r4(max(min(0.9, w * 0.15), w * (0.1 if stairs == "four" else 0.12)))
    land = 0 if gallery else max(min(0.6, w * 0.08), w * 0.06)       # (no gallery: a landing before the porch)
    extent = w * 0.5 - (bt + gal if gallery else land)                # from the axis to the porch's face
    bw = r4(max(w * 0.35, 2 * (extent - pd)))
    bH = r4(h * 0.25)
    cs = r4(min(0.5, bH * 0.06))
    pw = r4(bw * (0.46 if stairs == "four" else 0.52))
    T = {3: "three", 4: "four", 5: "five"}[tiers]
    roofH = h - bh - bH - cs
    ch = r4(roofH * 0.24)
    t1 = r4((roofH - ch) / sum(k ** i for i in range(tiers)))
    p = {"w": r4(w), "bh": bh, "bt": bt, "bah": r4(min(1.7, max(1.0, h * 0.04))), "rb": r4(min(1.2, max(0.6, w * 0.035))), "gH": r4(min(2.8, max(2.1, bh * 0.7))),
         "sw": r4(min(3.4, max(1.1, w * 0.1))), "bw": bw, "bH": bH, "cs": cs, "wt": r4(max(0.6, min(6.0, bw * 0.22))),
         "dw": r4(min(1.8, max(0.7, bw * 0.13), bw * 0.4)), "dh": r4(min(3.2, max(1.5, bH * 0.36), bH * 0.8)),
         "pw": pw, "pd": pd, "pH": r4(bH * 0.72), "pt": r4(max(0.4, min(0.9, pd * 0.28))),
         "t1": t1, "k": k, "rr": r4(t1 * 0.42), "ch": ch,
         "stairs": stairs, "gallery": "yes" if gallery else "no", "cella": cella, "tiers": T, "ratnas": ratnas,
         "ratna": "spike" if far else "vajra", "crownform": "spike" if far else "vajra", "mould": "no" if far else "yes"}
    p.update(over)
    return p


def finish_rules(name, p, palette):
    """the rules that dress the candi part `name` (params `p`) at its own scale: the Prambanan motif round the base, one
    register of niches up the body and the porches (a deity in each, between pilasters -- never stacked), the reliefs along
    the balustrade, the tiers and ratnas in fine courses. Put them before the building's general rules."""
    if p.get("mould") == "no": return [{"in": name, "pattern": "stone/ashlar", "palette": palette, "_about": f"{name}: plain blocks"}]
    out = [{"in": name, "parts": ["base", "base one", "base two", "base none"], "surface": "wall", "pattern": "stone/prambanan motif", "palette": palette,
            "scale": r4(p["bh"] * 0.8 / 1.4), "align": "part", "_about": f"{name}'s base: the Prambanan motif, one register"},
           {"in": name, "parts": ["cella", "body"], "surface": "wall", "side": "out", "pattern": "stone/candi niches", "palette": palette,
            "scale": r4(p["bH"] / 3.2), "align": "part", "whole": True, "_about": f"{name}'s body: one register of niches"},
           {"in": name, "parts": ["porch", "side porch", "porch block"], "surface": "wall", "side": "out", "pattern": "stone/candi niches", "palette": palette,
            "scale": r4(p["pH"] / 3.2), "align": "part", "whole": True, "_about": f"{name}'s porches: one register of niches"}]
    if p.get("gallery") == "yes":
        out.append({"in": name, "parts": ["balustrade", "balustrade one", "balustrade two", "balustrade none"], "surface": "wall",
                    "pattern": "stone/candi reliefs", "palette": palette, "scale": r4(p["bah"] / 1.2), "align": "part",
                    "_about": f"{name}'s balustrade: the reliefs in one register"})
    out.append({"in": name, "parts": ["roof 1", "roof 2", "roof 3", "roof 4", "roof 5", "kind:dome", "kind:column"], "pattern": "stone/ashlar fine", "palette": palette})
    return out


if __name__ == "__main__":
    ratna_component()
    candi_component()
    paduraksa_component()
