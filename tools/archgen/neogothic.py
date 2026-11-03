# THE GOTHIC REVIVAL (L2 style library): the vocabulary of a 19th-century Neo-Gothic public building -- a parliament, a
# town hall, a university, a railway hotel -- composed from the engine's parts and components. First written for the
# Hungarian Parliament (parliament.py); any Gothic Revival range can use it (Westminster, Vienna's Rathaus, Glasgow, ...).
#
#   Rect(x0, x1, z0, z1)        a block's plan; its faces "pz" "px" "nz" "nx" (+z, +x, -z, -x: the enclosure's faces 0..3),
#                               `place(face, a, o, y)` a point `a` along a face (from its middle, the way the enclosure runs
#                               it) and `o` out from it, with the yaw that turns a part's +z outward and its +x along it
#   facade_block(...)           A RANGE: an enclosure of storeys (`storeys`: STOREYS presets or your own), its fronts in
#                               bays `bay` apart -- a BUTTRESS-PIER at every bay line rising `piers.up` over the cornice to
#                               a PINNACLE, an openwork CRESTING along the cornice, a stone DORMER GABLE over every bay with
#                               its own little roof running back into the main roof (hip or mansard) -- the "forest of
#                               pinnacles" of a Gothic Revival front. Openings are laid out per bay, so the storeys align
#                               and the piers fall between them; doors replace the ground storey's window in their bay.
#   turret(...)                 a square or polygonal turret shaft with small lancets and a spire (an 8-sided pinnacle --
#                               cheap -- or the `gothic-spire` component)
#   gothic_tower(...)           `gothic-tower-stage`s stacked, an optional `gothic-octagon-stage`, a `gothic-spire`
#   flyer_ring(...)             `flying-buttress`es round a drum, radial, their piers and pinnacles outside
#   gothic_dome(...)            a Gothic Revival DOME: an n-sided drum of tall traceried lancets under gables (wimpergs),
#                               a pinnacle on every corner, a band of small windows (the attic), the ribbed pointed dome and
#                               the lantern with its needle spire
# Numbers are metres; every function takes `add(name, part)` (and `comp` for components) from the generator.
import math

r4 = lambda v: round(v, 4)
Q = math.pi / 2
YAW = {"pz": 0.0, "px": Q, "nz": math.pi, "nx": -Q}
FACE_NO = {"pz": "0", "px": "1", "nz": "2", "nx": "3"}
MIRROR = {"px": "nx", "nx": "px", "pz": "pz", "nz": "nz"}
POINTED = {"profile": "pointed", "spread": 1.0}
ROUND = {"profile": "semicircular"}


class Rect:
    def __init__(self, x0, x1, z0, z1):
        self.x0, self.x1, self.z0, self.z1 = min(x0, x1), max(x0, x1), min(z0, z1), max(z0, z1)
        self.cx, self.cz = (self.x0 + self.x1) / 2, (self.z0 + self.z1) / 2
        self.W, self.D = self.x1 - self.x0, self.z1 - self.z0

    def mirrored(self):
        return Rect(-self.x1, -self.x0, self.z0, self.z1)

    def length(self, f):
        return self.W if f in ("pz", "nz") else self.D

    def place(self, f, a, o=0.0, y=0.0):
        """[x, y, z, yaw] of the point `a` along face f (from its middle, as the enclosure runs it) and `o` out from it"""
        x, z = {"pz": (self.cx + a, self.z1 + o), "px": (self.x1 + o, self.cz - a),
                "nz": (self.cx - a, self.z0 - o), "nx": (self.x0 - o, self.cz + a)}[f]
        return [r4(x), r4(y), r4(z), r4(YAW[f])]

    def along(self, f, w):
        """the world x (faces pz/nz) or z (px/nx) `w` as a distance along face f"""
        return {"pz": w - self.cx, "nz": self.cx - w, "px": self.cz - w, "nx": w - self.cz}[f]


def _world(rect, f, a):
    """the world x (faces pz/nz) or z (px/nx) of the point `a` along face f"""
    return {"pz": rect.cx + a, "nz": rect.cx - a, "px": rect.cz - a, "nx": rect.cz + a}[f]


def bays(L, bay, end=0.0):
    """the bay lines and middles of a face L long: n bays near `bay` wide, `end` left at each end"""
    n = max(1, round((L - 2 * end) / bay)); p = (L - 2 * end) / n; a0 = -L / 2 + end
    return [r4(a0 + p * i) for i in range(n + 1)], [r4(a0 + p * (i + .5)) for i in range(n)], p


def apex(w, head):
    """how high a head of width w rises over its springing"""
    a = w / 2
    if head.get("profile") == "pointed": return a * math.sqrt(1 + 2 * head.get("spread", 1.0))
    if head.get("profile") == "semicircular": return a
    return head.get("rise", a * 0.5)


# STOREY PRESETS: what one storey of a front has in each bay. `kind`: "window" one opening, "pair" two (`gap` between),
# "blind" none. Sills over the storey's foot; the head's apex is kept `clear` under the storey's top.
STOREYS = {
    "arcade":  {"kind": "window", "h": 7.5, "w": 2.2, "sill": 0.9, "clear": 1.0, "head": ROUND, "_about": "the ground storey: round arches"},
    "main":    {"kind": "window", "h": 9.0, "w": 2.0, "sill": 1.2, "clear": 1.0, "head": POINTED, "tracery": 2, "_about": "the principal storey: tall two-light lancets"},
    "upper":   {"kind": "pair", "h": 8.1, "w": 0.95, "gap": 0.45, "sill": 1.4, "clear": 1.4, "head": POINTED, "_about": "the upper storey: paired lancets"},
    "upper1":  {"kind": "window", "h": 8.1, "w": 1.7, "sill": 1.4, "clear": 1.4, "head": POINTED, "_about": "the upper storey, plainer: a lancet a bay"},
    "plain":   {"kind": "window", "w": 1.4, "sill": 1.4, "clear": 1.4, "head": POINTED, "_about": "a court or back wall: one lancet a bay"},
    "loggia":  {"kind": "window", "h": 9.0, "w": 3.4, "sill": 1.0, "clear": 1.0, "head": ROUND, "glass": False, "_about": "an open loggia storey: big round arches, unglazed"},
}


def storey_openings(st, h, mids, doors=()):
    """the openings of one storey of height h in bays at `mids`; doors [(a, width, height)] take the bay they stand in"""
    out = []
    for a in mids:
        d = next((d for d in doors if abs(d[0] - a) < 1e-6), None)
        if d:
            _, w, dh = d
            out.append({"at": r4(a), "width": w, "sill": 0, "springing": r4(dh - apex(w, POINTED)), "head": POINTED, "glass": False})
            continue
        if st["kind"] == "blind": continue
        w, head = st["w"], st["head"]
        spr = r4(h - st["clear"] - apex(w, head))
        base = {"width": w, "sill": st["sill"], "springing": spr, "head": head}
        if st.get("tracery"): base["tracery"] = st["tracery"]
        if "glass" in st: base["glass"] = st["glass"]
        if st.get("wimperg"): base["wimperg"] = st["wimperg"]
        if st["kind"] == "pair":
            off = (w + st.get("gap", .5)) / 2
            out += [{"at": r4(a - off), **base}, {"at": r4(a + off), **base}]
        else:
            out.append({"at": r4(a), **base})
    return out


def facade_block(add, name, rect, H, *, fronts=("pz",), plain=None, storeys=("arcade", "main", "upper"), bay=5.5, end=0.0, T=1.0,
                 piers=None, pinnacle=None, cresting=None, dormers=None, roof=None, doors=None, interior=False,
                 courses=True, about=None, door_tier=0, plain_bay=None, skip=(), corner_up=None, bay_roofs=None):
    """A GOTHIC REVIVAL RANGE on `rect`, its walls H to the cornice in `storeys` (STOREYS names or dicts, the last taking
    the rest of H). Fronts (faces in `fronts`) get the bays, the buttress-piers and pinnacles, the cresting and the dormer
    gables; the faces in `plain` (default: the others) a lancet every `plain_bay` (STOREYS["plain"]) in every storey; faces in
    neither are blind. piers {w, d, up}: a pier at every bay line and each front's corners, rising `up` over the cornice;
    pinnacle {w, h, s, sides, crockets, gablets} on each (None: none); cresting {h, panel, every} along the cornice;
    dormers {w, h, reach, t, every}: a stone gable over a bay and its gabled roof (pitch from its height) into the main
    roof; roof {form hip|mansard|gable, pitch, lowerPitch, breakH, overhang}; doors [(face, world x|z, width, height)]
    in the ground storey (`door_tier`), as wide as their bay allows; interior: True or a height. skip [(face, w0, w1)]: world
    stretches (x or z) of a front where a risalit stands -- no piers, pinnacles or dormers there; corner_up: the corner piers'
    rise over the cornice (default piers.up); bay_roofs {w, h, t}: instead of a main roof, every bay of the (one) front under
    its own steep roof running the block's whole depth, its stone gable on the front (the river centre's seven). Returns the
    names added."""
    names = []
    def skipped(f, a):
        return any(ff == f and min(w0, w1) - 1e-6 <= _world(rect, f, a) <= max(w0, w1) + 1e-6 for ff, w0, w1 in skip)
    if bay_roofs:
        dormers = {"w": bay_roofs.get("w", bay * 0.92), "h": bay_roofs["h"], "t": bay_roofs.get("t", 0.6), "back": 0.4,
                   "reach": rect.length("px" if fronts[0] in ("pz", "nz") else "pz") - 1.0}
        roof = None
    plain_bay = plain_bay or bay * 2                      # (a court's wall: a lancet every other bay)
    def put(n, d):
        add(n, d); names.append(n)
    plain = [f for f in ("pz", "px", "nz", "nx") if f not in fronts] if plain is None else list(plain)
    sts = [dict(STOREYS[s]) if isinstance(s, str) else dict(s) for s in storeys]
    hs = [s.get("h") for s in sts[:-1]]; sts[-1]["h"] = H - sum(hs)
    piers = piers or {}; pw, pd, up = piers.get("w", 0.9), piers.get("d", 0.6), piers.get("up", 2.0)
    faces, lines = {}, {}
    for f in ("pz", "px", "nz", "nx"):
        L = rect.length(f)
        if f in fronts: st_list = sts
        elif f in plain: st_list = [dict(STOREYS["plain"], h=s["h"]) for s in sts]
        else: faces[FACE_NO[f]] = []; continue
        bl, mids, p = bays(L, bay if f in fronts else plain_bay, end)
        lines[f] = (bl, mids, p)
        fd = [(r4(rect.along(f, w)), dw, dh) for (ff, w, dw, dh) in (doors or []) if ff == f]
        # (a door goes to the bay it stands in)
        fd = [(min(mids, key=lambda m: abs(m - a)), dw, dh) for (a, dw, dh) in fd]
        tl = []
        for k, s in enumerate(st_list):
            ops = storey_openings(s, s["h"], mids, fd if k == door_tier else ())
            tl.append({"h": r4(s["h"]), "openings": ops} if k < len(st_list) - 1 else {"openings": ops})
        faces[FACE_NO[f]] = tl
    enc = {"type": "enclosure", "plan": {"rect": [r4(rect.W), r4(rect.D)]}, "thickness": T, "height": r4(H),
           "tiers": [{"openings": []}], "faces": faces, "courses": courses, "at": [[r4(rect.cx), 0, r4(rect.cz), 0]]}
    if interior: enc["interior"] = r4(H - 0.6) if interior is True else interior
    if about: enc["_about"] = about
    put(f"{name} walls", enc)
    # the buttress-piers: at the bay lines of every front, and a stouter one on each corner a front meets
    pier_at, pin_at = [], []
    for f in fronts:
        bl, mids, p = lines[f]
        for a in bl[1:-1]:
            if skipped(f, a): continue
            pier_at.append(rect.place(f, a, pd / 2 - 0.15, 0)); pin_at.append(rect.place(f, a, pd / 2 - 0.15, H + up))
    corners = set()
    for f in fronts:
        L = rect.length(f)
        for a in (-L / 2, L / 2):
            x, _, z, _ = rect.place(f, a, 0, 0); corners.add((x, z))
    cw = pw * 1.5; cup = up if corner_up is None else corner_up
    cor_at, cpin_at = [], []
    for (x, z) in sorted(corners):
        sx = 1 if x > rect.cx else -1; sz = 1 if z > rect.cz else -1
        cx, cz = x + sx * (cw / 2 - 0.25), z + sz * (cw / 2 - 0.25)
        cor_at.append([r4(cx), 0, r4(cz), 0]); cpin_at.append([r4(cx), r4(H + cup), r4(cz), 0])
    if pier_at:
        put(f"{name} piers", {"type": "box", "width": pw, "length": pd, "height": r4(H + up), "at": pier_at,
                              "_about": "the buttress-piers between the bays, up through the cornice"})
    if cor_at:
        put(f"{name} corner piers", {"type": "box", "width": r4(cw), "length": r4(cw), "height": r4(H + cup), "at": cor_at})
    if pinnacle:
        pin = {"type": "pinnacle", **{k: v for k, v in pinnacle.items() if k in ("w", "h", "s", "sides", "gablets", "crockets", "figure")}}
        if pin_at: put(f"{name} pinnacles", {**pin, "at": pin_at, "_about": "a pinnacle on every pier"})
        k = 1.3 if corner_up is None else 1.8
        if cpin_at: put(f"{name} corner pinnacles", {**pin, "w": r4(pin["w"] * k), "s": r4(pin["s"] * k), "at": cpin_at})
    # the cresting along each front's cornice, between the corner piers
    if cresting:
        for f in cresting.get("faces", fronts):
            L = rect.length(f)
            put(f"{name} cresting {f}", {"type": "cresting", "run": [[r4(-L / 2 + cw - 0.3), 0], [r4(L / 2 - cw + 0.3), 0]], "h": cresting.get("h", 1.0),
                                         "panel": cresting.get("panel", 1.8), "t": 0.28, "every": cresting.get("every", 0), "at": [rect.place(f, 0, 0, H)]})
    # the dormer gables, one over every `every`th bay, and their roofs
    if dormers:
        gw, gh, t = dormers.get("w", 3.0), dormers.get("h", 4.2), dormers.get("t", 0.45)
        sh = gh * 0.32; pitch = math.degrees(math.atan2(gh - sh - 0.35, gw / 2 * 0.95))
        reach = dormers.get("reach", 5.0); ev = dormers.get("every", 1); so = dormers.get("back", 0.45)
        g_at, r_at = [], []
        for f in fronts:
            bl, mids, p = lines[f]
            for i, a in enumerate(mids):
                if i % ev or skipped(f, a): continue
                g_at.append(rect.place(f, a, -so, H)); r_at.append(rect.place(f, a, -so - t / 2 - reach / 2 + 0.05, H + sh))
        outline = [[-gw / 2, 0], [gw / 2, 0], [gw / 2, sh], [0, gh], [-gw / 2, sh]]
        put(f"{name} dormer gables", {"type": "screen", "outline": [[r4(a), r4(b)] for a, b in outline], "t": t, "at": g_at,
                                      "_about": "a stone gable over every bay, rising from the cornice through the roof"})
        put(f"{name} dormer roofs", {"type": "roof", "form": "gable", "width": r4(gw * 0.95), "length": r4(reach), "pitch": r4(pitch),
                                     "overhang": 0.05, "at": r_at, "_about": "each gable's own roof, running back into the main roof"})
        if bay_roofs:                                     # (the flat under the bays' roofs, up to their shoulders)
            f = fronts[0]; L = rect.length(f); D = rect.length("px" if f in ("pz", "nz") else "pz")
            put(f"{name} bay roofs flat", {"type": "box", "width": r4(L - 0.8), "length": r4(D - 0.8), "height": r4(sh),
                                           "at": [rect.place(f, 0, -D / 2, H)], "_about": "the flat between the bays' roofs"})
    if roof:
        form = roof.get("form", "hip"); along_x = rect.W >= rect.D
        r = {"type": "roof", "form": form, "width": r4(rect.D if along_x else rect.W), "length": r4(rect.W if along_x else rect.D),
             "pitch": roof.get("pitch", 50), "overhang": roof.get("overhang", 0.2),
             "at": [[r4(rect.cx), r4(H), r4(rect.cz), r4(Q if along_x else 0)]]}
        for k in ("lowerPitch", "breakH"):
            if k in roof: r[k] = roof[k]
        put(f"{name} roof", r)
    return names


def turret(add, name, at, *, W, H, sides=4, t=0.45, win=0.7, every=10.0, blind=0.0, spire=None, corners=None, tip=None, about=None, comp=None):
    """TURRETS at `at` ([[x, y, z], ...]: their feet): a shaft W across (`sides` 4 square, else a polygon W across the
    corners) H high, a small lancet in each face every `every` metres up, and a spire {kind: "pinnacle" (an n-sided
    pinnacle: cheap) | "gothic" (components/gothic-spire), rise, sides, crockets, collar}; the lowest `blind` metres (where it stands in a range) windowless;
    corners {w, h, s}: a pinnacle on each corner of a square turret's head, round the spire's foot; tip {w, s}: a small
    spire of its own over the spire's top (`<name> tips`: the copper tips of the Parliament's turrets)"""
    plan = {"rect": [W, W]} if sides == 4 else {"sides": sides, "radius": r4(W / 2)}
    n = max(1, int((H - blind) // every)); hh = (H - blind) / n
    spr = r4(hh - 1.2 - apex(win, POINTED))
    tiers = [{"h": r4(blind), "openings": []}] if blind else []
    tiers += [{"h": r4(hh), "openings": [{"at": 0, "width": win, "sill": r4(hh * 0.45), "springing": spr, "head": POINTED}]} for _ in range(n - 1)]
    tiers.append({"openings": [{"at": 0, "width": win, "sill": r4(hh * 0.45), "springing": spr, "head": POINTED}]})
    d = {"type": "enclosure", "plan": plan, "thickness": t, "height": r4(H), "tiers": tiers, "at": [[r4(x), r4(y), r4(z), 0] for x, y, z in at]}
    if about: d["_about"] = about
    add(f"{name} shafts", d)
    cap = {"rect": [r4(W - 0.1), r4(W - 0.1)]} if sides == 4 else {"sides": sides, "radius": r4(W / 2 - 0.05)}
    add(f"{name} caps", {"type": "prism", "plan": cap, "height": 0.4, "flatRoof": True, "at": [[r4(x), r4(y + H - 0.4), r4(z), 0] for x, y, z in at],
                         "_about": "the stone roof over the shaft, the spire's footing"})
    if corners and sides == 4:
        c = W / 2 - corners.get("w", 0.8) / 2
        add(f"{name} corner pinnacles", {"type": "pinnacle", "w": corners.get("w", 0.8), "h": corners.get("h", 1.4), "s": corners.get("s", 2.6),
                                         "at": [[r4(x + i * c), r4(y + H), r4(z + j * c), 0] for x, y, z in at for i in (-1, 1) for j in (-1, 1)]})
    if not spire: return
    sp = dict(spire); rise = sp.get("rise", W * 3)
    if sp.get("kind", "pinnacle") == "pinnacle":
        add(f"{name} spires", {"type": "pinnacle", "w": r4(sp.get("w", W * 1.04)), "h": sp.get("collar", 0.6), "s": r4(rise), "sides": sp.get("sides", 8 if sides != 4 else 4),
                               "crockets": sp.get("crockets", 0), "gablets": sp.get("gablets", 0),
                               "at": [[r4(x), r4(y + H), r4(z), 0] for x, y, z in at]})
        if tip:
            add(f"{name} tips", {"type": "pinnacle", "w": tip.get("w", 0.6), "h": 0.2, "s": tip.get("s", 2.5), "sides": 6,
                                 "at": [[r4(x), r4(y + H + sp.get("collar", 0.6) + rise * 0.82), r4(z), 0] for x, y, z in at]})
    else:                                                 # (components/gothic-spire: pass `comp`)
        add(f"{name} spires", comp("components/gothic-spire", {"sides": sp.get("sides", 8), "R": r4(sp.get("w", W) / 2), "rise": r4(rise)},
                                   [[r4(x), r4(y + H), r4(z), 0] for x, y, z in at], build=sp.get("build", ["spire", "ribs", "finial"])))


def gothic_tower(add, comp, name, x, z, y0, stages, *, octagon=None, spire=None, yaw=0.0, about=None):
    """A GOTHIC TOWER at (x, z) from y0: `stages` [(params of gothic-tower-stage, build list), ...] stacked, then an
    optional octagon (gothic-octagon-stage params) and a spire (gothic-spire params, + build list under "build")"""
    y = y0
    for i, (p, bl) in enumerate(stages):
        kw = {"_about": about} if (about and i == 0) else {}
        add(f"{name} stage {i + 1}", comp("components/gothic-tower-stage", p, [[r4(x), r4(y), r4(z), r4(yaw)]], build=bl, **kw))
        y += p["H"]
    if octagon:
        o = dict(octagon); bl = o.pop("build", ["walls", "slab"])
        add(f"{name} octagon", comp("components/gothic-octagon-stage", o, [[r4(x), r4(y), r4(z), 0]], build=bl))
        y += o["H"]
    if spire:
        sp = dict(spire); bl = sp.pop("build", ["spire", "ribs", "finial"])
        add(f"{name} spire", comp("components/gothic-spire", sp, [[r4(x), r4(y), r4(z), 0]], build=bl))
    return y


def flyer_ring(add, comp, name, n, r_pier, r_wall, params, *, y=0.0, turn=0.0, about=None):
    """`n` FLYING BUTTRESSES round a drum (`r_wall` its outside, at its faces' middles): the piers `r_pier` out (their
    inner face), each flyer reaching in to the drum (components/flying-buttress, its span from the radii)"""
    at = []
    for k in range(n):
        t = (k + turn) * 2 * math.pi / n
        at.append([r4(r_pier * math.sin(t)), r4(y), r4(r_pier * math.cos(t)), r4(math.atan2(math.cos(t), -math.sin(t)))])
    p = {**params, "span": r4(r_pier - r_wall + 0.15)}
    add(name, comp("components/flying-buttress", p, at, **({"_about": about} if about else {})))


def gothic_dome(add, comp, name, *, n=16, R, y0, drumH, T=1.2, winW=2.2, winSill=2.0, lights=2, wimperg=None, oculus=0.0,
                cornerPin=None, atticH=3.0, atticWin=0.9, atticRound=False, footPin=None, rise, profile="pointed", domeT=0.8, ribW=0.5,
                lantern=None, about=None):
    """A GOTHIC REVIVAL DOME (the Hungarian Parliament's, 1904): an n-sided DRUM, R to its corners, drumH high from y0, a
    tall traceried lancet (`lights`) in every face under its gable (`wimperg`) and over it -- `oculus` > 0 -- a band of
    round windows that wide; a pinnacle (`cornerPin` {w, h, s}) on every corner over the cornice; the ATTIC, a band of small
    arched windows atticH high (`atticRound`: round ones, oculi), a second ring of pinnacles (`footPin`) on its corners at the
    dome's foot; the ribbed DOME rising `rise` over the attic -- `profile` "pointed" (its spread worked from the rise) or
    any head profile the engine has with its `rise`; and the LANTERN {R, H, rise, spireR}: an open octagonal stage and a
    needle spire on the dome's crown"""
    head = {"profile": "pointed", "spread": 1.0}
    band = r4(oculus + 1.8) if oculus else 0.0
    spr = r4(drumH - band - 2.2 - apex(winW, head))
    op = {"at": 0, "width": winW, "sill": winSill, "springing": spr, "head": head, "tracery": lights}
    if wimperg: op["wimperg"] = wimperg
    tiers = [{"h": r4(drumH - band), "openings": [op]}]
    if oculus:
        tiers.append({"openings": [{"at": 0, "width": oculus, "sill": r4(band / 2), "springing": r4(band / 2), "head": ROUND, "foot": ROUND}]})
    add(f"{name} drum", {"type": "enclosure", "plan": {"sides": n, "radius": r4(R)}, "thickness": T, "height": r4(drumH),
                         "tiers": tiers if oculus else [{"openings": [op]}], "courses": True, "at": [[0, r4(y0), 0, 0]],
                         **({"_about": about} if about else {})})
    ring = lambda r, y: [[r4(r * math.sin((k + .5) * 2 * math.pi / n)), r4(y), r4(r * math.cos((k + .5) * 2 * math.pi / n)), 0] for k in range(n)]
    if cornerPin:
        add(f"{name} drum pinnacles", {"type": "pinnacle", **cornerPin, "at": ring(R, y0 + drumH), "_about": "a pinnacle on every corner of the drum"})
    ya = y0 + drumH
    aspr = r4(atticH - 0.5 - atticWin / 2)
    aops = [{"at": 0, "width": atticWin, "sill": r4(atticH / 2), "springing": r4(atticH / 2), "head": ROUND, "foot": ROUND} if atticRound
            else {"at": 0, "width": atticWin, "sill": 0.5, "springing": aspr, "head": ROUND}]
    add(f"{name} attic", {"type": "enclosure", "plan": {"sides": n, "radius": r4(R - 0.4)}, "thickness": T, "height": r4(atticH),
                          "openings": aops, "at": [[0, r4(ya), 0, 0]], "_about": "the attic: a band of small arched windows at the dome's foot"})
    yd = ya + atticH
    if footPin:
        add(f"{name} foot pinnacles", {"type": "pinnacle", **footPin, "at": ring(R - 0.4, yd), "_about": "the second ring of pinnacles, round the dome's foot"})
    # the dome: its (corner) radius R - 0.4 as the attic's; a pointed one's spread from the rise wanted: rise = a sqrt(1 + 2 spread)
    a = (R - 0.4) * math.cos(math.pi / n)
    if profile == "pointed":
        spread = max(0.05, ((rise / a) ** 2 - 1) / 2); dhead = {"profile": "pointed", "spread": r4(spread)}
    else:
        spread = None; dhead = {"profile": profile, "rise": r4(rise)}
    add(f"{name} dome", {"type": "dome", "sides": n, "radius": r4(R - 0.4), "thickness": domeT, "head": dhead,
                         "at": [[0, r4(yd), 0, 0]], "standsOn": [f"{name} attic"], "_about": "the ribbed dome"})
    add(f"{name} ribs", {"type": "ribs", "on": f"{name} dome", "count": n, "width": ribW, "depth": r4(ribW * 0.7), "standsOn": [f"{name} dome"],
                         "_about": "a rib up every corner of the dome"})
    if lantern:
        L = lantern
        if spread is not None:   # (it stands where the dome has narrowed to its radius: on the pointed arc x = -c + sqrt(r^2 - y^2))
            c, rr = a * spread, a * (1 + spread)
            y_l = yd + math.sqrt(max(0.0, rr * rr - (L["R"] + c) ** 2)) - 0.1
        else:
            y_l = yd + L.get("at", rise * 0.95)
        add(f"{name} lantern", comp("components/gothic-octagon-stage", {"R": L["R"], "H": L["H"], "t": r4(L["R"] * 0.14), "low": r4(L["H"] * 0.2), "glazed": 0},
                                    [[0, r4(y_l), 0, 0]], build=["walls", "slab"], _about="the lantern on the dome's crown: an open octagon"))
        add(f"{name} spire", comp("components/gothic-spire", {"R": L.get("spireR", L["R"]), "rise": L["rise"], "finial": L.get("finial", 2.0), "pinR": L["R"]},
                                  [[0, r4(y_l + L["H"]), 0, 0]], build=["spire", "ribs", "gables", "pinnacles", "finial"],
                                  _about="the needle spire over the lantern"))
        return y_l + L["H"] + L["rise"]
    return yd + rise


def arcade(add, name, rect, face, depth, h, *, bay=5.5, pier=1.3, head=ROUND, t=0.9, crest=True, about=None):
    """AN ARCADED LOGGIA before a range's ground storey: a wall `depth` out from the face, an arch (`head`) in every bay
    (`bay`, laid out as the range's, so the arches fall between its piers: `pier` the solid between two), its deck the
    loggia's ceiling and the balcony over it, an openwork cresting on the balcony's edge"""
    L = rect.length(face); bl, mids, p = bays(L, bay)
    w = r4(p - pier); spr = r4(h - 1.0 - apex(w, head))
    ops = [{"at": a, "width": w, "sill": 0, "springing": spr, "head": head, "glass": False} for a in mids]
    add(f"{name} arcade", {"type": "wall", "width": r4(L), "height": h, "thickness": t, "tiers": [{"openings": ops}], "glass": False,
                           "at": [rect.place(face, 0, depth - t / 2, 0)], **({"_about": about} if about else {})})
    add(f"{name} arcade deck", {"type": "box", "width": r4(L), "length": r4(depth), "height": 0.5,
                                "at": [rect.place(face, 0, depth / 2, h - 0.4)], "walked": True})
    if crest:
        add(f"{name} arcade cresting", {"type": "cresting", "run": [[r4(-L / 2 + 0.5), 0], [r4(L / 2 - 0.5), 0]], "h": 1.0, "panel": 3.2, "t": 0.25, "every": 0,
                                        "at": [rect.place(face, 0, depth - 0.1, h + 0.1)]})


def great_gable(add, name, at, *, w, h, t=0.8, pinnacle=None, rose=0.0, roof=None):
    """GREAT GABLES at `at` ([x, y, z, yaw]: the middle of the gable's foot on the wall's face, yaw turning it outward):
    a stone gable w wide and h high, a pinnacle (`pinnacle` {w, h, s}) at its apex and its feet, `rose` > 0 a ROSE window
    that wide in it (a wall standing in the gable's face with a round traceried opening, tracery.js roseLines), and
    roof {reach, pitch}: its gabled roof running back into the roof behind"""
    outline = [[r4(-w / 2), 0], [r4(w / 2), 0], [0, r4(h)]]
    if rose:   # (the gable open where the rose's wall stands in it: else its face runs through the rose's glass, and the two flicker)
        hw = r4((rose + 1.2) / 2); top = r4(h * (1 - 2 * hw / w) - 0.1)
        outline = [[r4(-w / 2), 0], [-hw, 0], [-hw, top], [hw, top], [hw, 0], [r4(w / 2), 0], [0, r4(h)]]
    add(f"{name}", {"type": "screen", "outline": outline, "t": t, "at": at})
    rot =lambda p, dx, dz: [r4(p[0] + dx * math.cos(p[3]) + dz * math.sin(p[3])), p[1], r4(p[2] - dx * math.sin(p[3]) + dz * math.cos(p[3])), p[3]]
    if pinnacle:
        pts = []
        for p in at:
            pts += [rot([p[0], r4(p[1] + h - 0.4), p[2], p[3]], 0, 0.15), rot(p, -w / 2, 0.15), rot(p, w / 2, 0.15)]
        add(f"{name} pinnacles", {"type": "pinnacle", **pinnacle, "at": [[q[0], q[1], q[2], 0] for q in pts]})
    if rose:
        d = rose; ww = r4(d + 1.2); y_c = r4(h * (1 - ww / w) - d / 2 - 0.6)   # (its wall's corners under the gable's slopes)
        add(f"{name} rose", {"type": "wall", "width": ww, "height": r4(y_c + d / 2 + 0.6), "thickness": 0.4, "glass": True,
                             "tiers": [{"openings": [{"at": 0, "width": d, "sill": y_c, "springing": y_c, "head": ROUND, "foot": ROUND, "tracery": True}]}],
                             "at": [rot([p[0], p[1], p[2], p[3]], 0, 0.2) for p in at], "_about": "the rose window in the gable"})
    if roof:
        reach = roof["reach"]; pitch = roof.get("pitch", math.degrees(math.atan2(h - 0.3, w / 2)))
        add(f"{name} roof", {"type": "roof", "form": "gable", "width": r4(w * 0.98), "length": r4(reach), "pitch": r4(pitch), "overhang": 0.1,
                             "at": [rot(p, 0, -t - reach / 2 + 0.05) for p in at]})


def risalit(add, name, main, face, w0, w1, out, H, *, gables=(), gable=None, back=1.0, corner_up=5.0, **kw):
    """A RISALIT: the stretch w0..w1 (world x or z) of `main`'s front `face` brought forward `out`, a block of its own
    (facade_block's keywords in **kw: storeys, piers, pinnacle, dormers ...), its corner piers rising `corner_up` over the
    cornice to great pinnacles, and over it GREAT GABLES at the world positions `gables` (great_gable's keywords in
    `gable`: w, h, pinnacle, rose, roof); the main block should `skip` this stretch. Returns its Rect."""
    a0, a1 = sorted((w0, w1))
    if face == "pz": r = Rect(a0, a1, main.z1 - back, main.z1 + out)
    elif face == "nz": r = Rect(a0, a1, main.z0 - out, main.z0 + back)
    elif face == "px": r = Rect(main.x1 - back, main.x1 + out, a0, a1)
    else: r = Rect(main.x0 - out, main.x0 + back, a0, a1)
    dkw = dict(kw)
    if gables and dkw.get("dormers"):
        gw = (gable or {}).get("w", 8.0)
        dkw["skip"] = [(face, g - gw / 2 - 1.0, g + gw / 2 + 1.0) for g in gables]
    facade_block(add, name, r, H, fronts=(face,), plain=(), corner_up=corner_up, **dkw)   # (its short returns blind)
    if gables:
        g = dict(gable or {})
        at = [r.place(face, r.along(face, x), 0.05 - 0.0, H) for x in gables]
        great_gable(add, f"{name} gables", at, **g)
    return r
