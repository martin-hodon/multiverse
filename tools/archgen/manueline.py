"""MANUELINE (L2, 2026-11-02): the Portuguese late Gothic of King Manuel I (Belem, Batalha, Tomar, Setubal, Lisbon's
19th-century revival of it) as components and set-out rules, for any generator that builds in it.

    write_components(root)      writes components/manueline-portal.json and components/mitre-tower.json (L1)
    portal_doors(spec, at0)     the wall's two doorways under a `manueline-portal` of params `spec`, as openings
    front_buttresses(...)       buttresses (with pinnacles) standing out from one edge of an outline, at offsets along it
    crest(...)                  an openwork crest (`cresting`) along the top of edges of an outline (spire=None: a balustrade)
    seg_edge(a, b)              one edge a -> b in plan_edges' frame, for a crest or buttresses along part of a face

An outline's edges are shapes.plan_edges'. A part's frame: x along, y up, z out of the wall."""
import os, json, math
from shapes import plan_edges

r4 = lambda v: round(v, 4)
semi = {"profile": "semicircular"}
seg = lambda rise: {"profile": "segmental", "rise": rise}
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
ROPE_FRAME = {"style": "romanesque", "orders": 2}      # a window's carved frame: two orders, a shaft in each (surround.js)
ROPE_FRAME1 = {"style": "romanesque", "orders": 1}


def portal_doors(spec, at0, sign=1):
    """the two doorways in the wall behind a `manueline-portal` (its params `spec`: doorW, doorH, gap), centred at `at0`
    along the face (`sign` -1 where the face's `at` runs against the portal's x); their crowns at doorH"""
    a, rise = spec["gap"] / 2 + spec["doorW"] / 2, 0.6
    return [{"at": r4(at0 + sign * s * a), "width": spec["doorW"], "sill": 0, "springing": r4(spec["doorH"] - rise), "head": seg(rise), "glass": False} for s in (-1, 1)]


def front_buttresses(add, name, edge, offs, w, d, h, pin=None, about=None):
    """buttresses `w` wide standing `d` out from an outline's `edge` (plan_edges), `h` tall, at `offs` along it from its
    middle -- each run 0.3 into the wall so it stands on it -- and a `components/pinnacle` { w, h, s } on each"""
    (mx, mz), (ex, ez), (nx, nz) = edge["mid"], edge["e"], edge["n_in"]
    at = [[r4(mx + ex * o - nx * (d / 2 - 0.3)), 0, r4(mz + ez * o - nz * (d / 2 - 0.3)), r4(edge["yaw"])] for o in offs]
    add(name, {"type": "box", "width": w, "length": d + 0.3, "height": h, "at": at, **({"_about": about} if about else {})})
    if pin:
        add(name + " pinnacles", comp("components/pinnacle", pin, [[a[0], h, a[2], a[3]] for a in at], standsOn=[name]))


def crest(add, name, edges, y, h=1.3, inset=0.5, every=3, spire=(0.35, 1.2), panel=1.2, t=0.3, end=0.6, about=None, **kw):
    """an openwork crest along the top (`y`) of each of `edges`, `inset` in from the face (`n_in`), `end` clear of each
    end: one part per length; `spire` None a plain pierced balustrade, without spirelets"""
    rows = {}
    for e in edges:
        (mx, mz), (nx, nz) = e["mid"], e["n_in"]
        rows.setdefault(round(e["L"], 2), []).append([r4(mx + nx * inset), y, r4(mz + nz * inset), r4(e["yaw"])])
    for L, at in sorted(rows.items()):
        sp = {"every": every, "spirelet": {"w": spire[0], "s": spire[1]}} if spire else {}
        add(f"{name} {round(L)}", {"type": "cresting", "run": [[r4(-L / 2 + end), 0], [r4(L / 2 - end), 0]], "h": h, "panel": panel, "t": t,
                                   **sp, "at": at, **kw, **({"_about": about} if about else {})})


def seg_edge(a, b):
    """the edge from a to b (plan_edges' frame: its inward normal on the right of a -> b, as an outline's)"""
    return plan_edges([a, b])[0]


# ================================================================ components/manueline-portal
def _portal():
    pp = {}
    PX = "W / 2 - pw / 2"                      # the piers' middles
    HP = "H * 0.72"                            # the piers' tops
    ARCH_Y = "doorH + 0.6"                     # the archivolt's springing
    Y0 = "doorH + 0.6 + archR + band + 0.3"    # the tabernacle's foot
    CROSS = "H * 0.08"
    HS = f"(H - {CROSS} - ({Y0})) / tiers"     # one niche of the tabernacle
    pp["piers"] = {"type": "box", "width": "pw", "length": "D + wallIn", "height": HP, "at": [[f"0 - ({PX})", 0, "(D - wallIn) / 2", 0], [PX, 0, "(D - wallIn) / 2", 0]],
                   "_about": "the two buttress piers either side, carved all over"}
    PSX = [f"0 - ({PX}) - pw * 0.32", f"0 - ({PX}) + pw * 0.32", f"{PX} - pw * 0.32", f"{PX} + pw * 0.32"]
    pp["pier shafts"] = {"type": "column", "radius": "pw * 0.2", "height": HP, "sides": 12, "twist": {"lobes": 3, "depth": 0.24, "turns": f"max(1, {HP} / 2.0)", "rows": 4},
                         "at": [[x, 0, "D + pw * 0.05", 0] for x in PSX], "_about": "the twisted rope shafts wound up the piers' fronts"}
    pp["pier pinnacles"] = comp("components/pinnacle", {"w": "pw", "h": "H * 0.05", "s": "H * 0.17"},
                                [[f"0 - ({PX})", HP, "(D - wallIn) / 2", 0], [PX, HP, "(D - wallIn) / 2", 0]], standsOn=["piers"])
    PIER_Y = ["H * 0.28", "H * 0.48"]
    pp["pier ledges"] = {"type": "box", "width": "pw * 0.6", "length": 0.45, "height": 0.25,
                         "at": [[sx, y, "D + 0.2", 0] for y in PIER_Y for sx in (f"0 - ({PX})", PX)], "_about": "brackets on the piers' fronts, a statue on each"}
    pp["pier canopies"] = comp("components/pinnacle", {"w": "pw * 0.55", "h": 0.4, "s": 1.3},
                               [[sx, f"{y} + 2.3", "D + 0.2", 0] for y in PIER_Y for sx in (f"0 - ({PX})", PX)])
    pp["field"] = {"type": "box", "width": "W - 2 * pw", "length": "fieldD + wallIn", "height": f"{HP} - doorH - 0.2", "at": [[0, "doorH + 0.2", "(fieldD - wallIn) / 2", 0]],
                   "_about": "the relief field between the piers, over the doors' heads"}
    # the ARCHIVOLT: a deep band round a basket (half-ellipse) arch over both doors, from pier to pier, well out of the field
    K = 12
    inner = [[f"(W / 2 - pw) * {r4(math.cos(math.pi * k / K))}", f"{ARCH_Y} + archR * {r4(math.sin(math.pi * k / K))}"] for k in range(K + 1)]
    outer = [[f"(W / 2 - pw + band) * {r4(math.cos(math.pi * k / K))}", f"{ARCH_Y} + (archR + band) * {r4(math.sin(math.pi * k / K))}"] for k in range(K, -1, -1)]
    pp["archivolt"] = {"type": "screen", "outline": inner + outer, "t": "0.9 + fieldD * 0", "at": [[0, 0, "fieldD + 0.85", 0]],
                       "_about": "the archivolt: a deep carved band round the basket arch that gathers both doors under it"}
    # the EMBRASURE: `orders` stepped jambs either side of the doors, each further out than the last, a twisted shaft on each
    for k in range(3):
        on = f"min(1, max(0, orders - {k}))"
        x = f"gap / 2 + doorW + 0.21 + {0.42 * k}"; zf = f"{0.15 + 0.35 * k}"
        pp[f"jamb order {k + 1}"] = {"type": "box", "width": 0.42, "length": f"{zf} + wallIn", "height": ARCH_Y,
                                     "at": [[f"0 - ({x})", 0, f"({zf} - wallIn) / 2", 0], [x, 0, f"({zf} - wallIn) / 2", 0]], "repeat": {"count": on, "step": [0, 0, 0, 0]},
                                     **({"_about": "the splayed embrasure: the jambs stepping out in orders"} if k == 0 else {})}
        pp[f"jamb shafts {k + 1}"] = {"type": "column", "radius": 0.17, "height": ARCH_Y, "sides": 12, "twist": {"lobes": 3, "depth": 0.25, "turns": "max(1, doorH / 1.2)", "rows": 4},
                                      "at": [[f"0 - ({x})", 0, zf, 0], [x, 0, zf, 0]], "repeat": {"count": on, "step": [0, 0, 0, 0]}}
    TR = "doorH * 0.45"
    pp["trumeau"] = {"type": "column", "radius": "gap * 0.38", "height": TR, "sides": 12, "twist": {"lobes": 4, "depth": 0.2, "turns": "max(1, doorH * 0.45 / 1.0)", "rows": 4},
                     "at": [[0, 0, "gap * 0.3", 0]], "_about": "the trumeau between the doors: a twisted column"}
    pp["trumeau bracket"] = {"type": "box", "width": "gap * 1.1", "length": "gap * 0.9 + wallIn", "height": 0.25, "at": [[0, TR, "(gap * 0.9 - wallIn) / 2", 0]]}
    pp["trumeau canopy"] = {"type": "box", "width": "gap * 1.1", "length": "gap * 0.9 + wallIn", "height": 0.3, "at": [[0, f"{TR} + 2.25", "(gap * 0.9 - wallIn) / 2", 0]]}
    pp["trumeau spire"] = comp("components/pinnacle", {"w": "gap * 0.7", "h": 0.2, "s": f"max(0.4, doorH + 0.2 - ({TR} + 2.55) - 0.25)"},
                               [[0, f"{TR} + 2.55", "gap * 0.3", 0]], standsOn=["trumeau canopy"])
    # the TABERNACLE up the middle: up to four NICHES stacked, each narrower and shallower than the one under it (`taper`):
    # a back panel, a post either side, a canopy over, a statue on its ledge inside, pinnacles on the canopy's corners
    build_tab = []
    for k in range(4):
        on = f"min(1, max(0, tiers - {k}))"
        tk = " * ".join(["taper"] * k) or "1"            # (taper to the k: expr.js has no power)
        wk, dk, y = f"tabW * {tk}", f"D * 0.85 * {tk}", f"{Y0} + {HS} * {k}"
        rep = {"repeat": {"count": on, "step": [0, 0, 0, 0]}}
        n = f"niche {k + 1}"
        pp[f"{n} back"] = {"type": "box", "width": wk, "length": f"{dk} * 0.45 + wallIn", "height": HS, "at": [[0, y, f"({dk} * 0.45 - wallIn) / 2", 0]], **rep,
                           **({"_about": "the tabernacle: niches one over the next up the middle, each narrower than the one under it"} if k == 0 else {})}
        pp[f"{n} posts"] = {"type": "box", "width": 0.3, "length": f"{dk} + wallIn", "height": f"{HS} - 0.45", "at": [[f"{s} * ({wk} / 2 - 0.15)", y, f"({dk} - wallIn) / 2", 0] for s in (-1, 1)], **rep}
        pp[f"{n} canopy"] = {"type": "box", "width": wk, "length": f"{dk} + wallIn", "height": 0.45, "at": [[0, f"{y} + {HS} - 0.45", f"({dk} - wallIn) / 2", 0]], **rep}
        pp[f"{n} ledge"] = {"type": "box", "width": f"{wk} * 0.45", "length": 0.45, "height": 0.25, "at": [[0, y, f"{dk} * 0.45 + 0.2", 0]], **rep}
        pp[f"{n} pinnacles"] = comp("components/pinnacle", {"w": 0.3, "h": 0.25, "s": 1.1}, [[f"{s} * ({wk} / 2 - 0.15)", f"{y} + {HS}", f"{dk} - 0.15", 0] for s in (-1, 1)],
                                    standsOn=[f"{n} canopy"], **rep)
        pp[f"{n} statue"] = _mark([[0, f"{y} + 0.25", f"{dk} * 0.45 + 0.2", 0]], kind="woman" if k == 0 else "man", pose="stand", scale=0.85, seed=3 + k, **rep)
        build_tab += [f"{n} back", f"{n} posts", f"{n} canopy", f"{n} ledge", f"{n} pinnacles", f"{n} statue"]
    FY = ["H * 0.42", "H * 0.58"]
    FX = "(W / 2 - pw + tabW / 2) / 2"
    pp["field ledges"] = {"type": "box", "width": 0.9, "length": 0.5, "height": 0.25, "at": [[f"{sx} * {FX}", y, "fieldD + 0.2", 0] for y in FY for sx in (-1, 1)]}
    pp["field canopies"] = comp("components/pinnacle", {"w": 0.8, "h": 0.4, "s": 1.4}, [[f"{sx} * {FX}", f"{y} + 2.3", "fieldD + 0.2", 0] for y in FY for sx in (-1, 1)])
    pp["cross shaft"] = {"type": "box", "width": f"{CROSS} * 0.16", "length": f"{CROSS} * 0.16", "height": CROSS, "at": [[0, f"H - {CROSS}", "D * 0.3", 0]],
                         "_about": "the cross of the Order of Christ, crowning the tabernacle"}
    pp["cross arms"] = {"type": "box", "width": f"{CROSS} * 0.62", "length": f"{CROSS} * 0.16", "height": f"{CROSS} * 0.16",
                        "at": [[0, f"H - {CROSS} * 0.62", "D * 0.3", 0]], "standsOn": ["cross shaft"]}
    pp["trumeau statue"] = _mark([[0, f"{TR} + 0.25", "gap * 0.45", 0]], kind="man", pose="guard", scale=0.95, seed=11)
    pp["pier statues"] = _mark([[sx, f"{y} + 0.25", "D + 0.2", 0] for y in PIER_Y for sx in (f"0 - ({PX})", PX)], kind="man", pose="stand", scale=0.85, seed=5)
    pp["field statues"] = _mark([[f"{sx} * {FX}", f"{y} + 0.25", "fieldD + 0.2", 0] for y in FY for sx in (-1, 1)], kind="man", pose="stand", scale=0.85, seed=7)
    build = ["piers", "pier shafts", "pier pinnacles", "pier ledges", "pier canopies", "pier statues", "field", "archivolt",
             *[f"jamb {w} {k}" for k in (1, 2, 3) for w in ("order", "shafts")],
             "trumeau", "trumeau bracket", "trumeau statue", "trumeau canopy", "trumeau spire", *build_tab,
             "field ledges", "field statues", "field canopies", "cross shaft", "cross arms"]
    return {"name": "Manueline portal",
            "_about": "A MANUELINE PORTAL (Belem, Batalha, Tomar): a carved screen standing out from a wall round TWIN DOORS -- two buttress PIERS wound with twisted rope shafts and crowned with pinnacles, a splayed EMBRASURE of `orders` (0-3) stepped jambs with a twisted shaft on each, the TRUMEAU between the doors a twisted column carrying a statue under a canopy, the doors' heads under a deep basket ARCHIVOLT, the relief FIELD over them, and up the middle the TABERNACLE: `tiers` (1-4) NICHES one over the next, each `taper` times narrower and shallower than the one under it, a statue in each under its canopy and pinnacles, the cross of the Order of Christ on top. `W` wide, `H` high (the cross's top), the piers `pw` wide and `D` out from the wall, the doors `doorW` wide each with their crowns at `doorH`, `gap` between them. The wall's own doorways are the building's (manueline.py portal_doors): two openings `doorW` wide, crowns at `doorH`, centred `gap / 2 + doorW / 2` either side of the middle. Its frame: z out of the wall (the wall's face at z 0); every piece runs `wallIn` back into the wall.",
            "params": {"detail": 4, "W": 12.0, "H": 32.0, "D": 2.0, "pw": 1.6, "doorW": 2.6, "doorH": 6.2, "gap": 1.0, "tiers": 4, "taper": 0.85, "orders": 3, "wallIn": 0.4,
                       "fieldD": 0.6, "archR": "min(3.2, (W / 2 - pw) * 0.75)", "band": 0.9, "tabW": "min(2.8, W * 0.24)",
                       "_tiers": "the tabernacle's niches (1-4), one over the next, from over the archivolt to under the cross", "_orders": "the embrasure's stepped jambs each side (0-3)"},
            "build": build, "parts": pp}


def _mark(at, **d):
    """a statue marker, inline (a component's numbers are expressions; statuary.py's are numbers): it faces out (+z)"""
    rep = {"repeat": d.pop("repeat")} if "repeat" in d else {}
    return {"type": "marker", "role": "statue", "at": at, "data": {"style": "gothic", "stone": "limestone", "face": -1.5707963, **d}, **rep}


# ================================================================ components/mitre-tower
def _tower():
    SH = "(H - belfryH) / 3"                   # one of the three stages under the belfry
    win = {"pattern": "wins", "width": "winW", "gap": "(W - 2 * t) / wins - winW", "sill": f"{SH} * 0.3", "springing": f"{SH} * 0.3 + winW * 1.8", "head": semi}
    bell = {"pattern": "bells", "width": "(W - 2 * t) / bells * 0.62", "gap": "(W - 2 * t) / bells * 0.38", "sill": 1.0, "springing": "belfryH * 0.68", "head": semi}
    door = {"at": "doorAt", "width": "doorW", "sill": 0, "springing": "doorW * 1.5", "head": semi, "glass": False}
    P4 = lambda y: [[f"{sx} * (W / 2 - pin * 0.6)", y, f"{sz} * (W / 2 - pin * 0.6)", 0] for sx in (-1, 1) for sz in (-1, 1)]
    return {
        "name": "Mitre tower",
        "_about": "A MANUELINE TOWER: a square shaft `W` wide and `H` tall in `t`-thick walls, in three STAGES under a BELFRY -- `wins` windows `winW` wide in each face of each stage, `bells` round arches a face in the belfry (`belfryH` tall), a door `doorW` wide in face 0 (+z) at `doorAt` -- a string course and a PINNACLE at each corner over every stage (`pin`), a pierced balustrade round the flat top, and on it EITHER (build \"drum\", \"drum head\", \"dome\", \"finial\") an octagonal DRUM (`drumR`, `drumH`) under a POINTED stone dome -- Belem's bell tower and its mitre (1867-68) -- its two arcs' centres `spread` half-widths apart (1 equilateral, more a lancet, rising half-width * sqrt(1 + 2 spread)), OR (build \"spire\") a crocketed octagonal SPIRE `spireH` tall -- the 19th-century tower at the west end of the range; and (build \"turret\", \"turret cap\") a stair TURRET `turretR` at the +x +z corner, rising past the top.",
        "params": {"detail": 4, "W": 10.0, "H": 30.0, "t": 1.2, "belfryH": 7.0, "bells": 2, "wins": 1, "winW": "W * 0.12", "doorW": 1.6, "doorAt": 0,
                   "drumR": "W * 0.36", "drumH": "W * 0.4", "spread": 1.6, "pin": "W * 0.1", "spireH": "W * 1.2", "turretR": "W * 0.14"},
        "build": ["shaft", "stage floors", "courses", "stage pinnacles", "head", "balustrade", "pinnacles", "drum", "drum head", "dome", "finial"],
        "parts": {
            "shaft": {"type": "enclosure", "plan": {"rect": ["W", "W"]}, "thickness": "t", "height": "H", "interior": True, "at": [[0, 0, 0, 0]],
                      "tiers": [{"h": SH, "openings": win}, {"h": SH, "openings": win}, {"h": SH, "openings": win}, {"openings": {**bell, "glass": False}}],
                      "faces": {"0": [{"h": SH, "openings": [door]}, {"h": SH, "openings": win}, {"h": SH, "openings": win}, {"openings": {**bell, "glass": False}}]},
                      "_about": "the square shaft: three stages of windows, the belfry's arches at its head, the door in its foot"},
            "stage floors": {"type": "prism", "plan": {"rect": ["W - t", "W - t"]}, "height": 0.3, "at": [[0, f"{SH} - 0.3", 0, 0]], "repeat": {"count": 3, "step": [0, SH, 0, 0]},
                             "standsOn": ["shaft"], "walked": True},
            "courses": {"type": "box", "width": "W + 0.5", "length": "W + 0.5", "height": 0.35, "at": [[0, SH, 0, 0]], "repeat": {"count": 3, "step": [0, SH, 0, 0]},
                        "_about": "the string courses between the stages"},
            "stage pinnacles": comp("components/pinnacle", {"w": "pin * 1.2", "h": "pin", "s": "pin * 3"}, P4(f"{SH} + 0.35"),
                                    repeat={"count": 3, "step": [0, SH, 0, 0]}, standsOn=["courses"]),
            "head": {"type": "prism", "plan": {"rect": ["W - t", "W - t"]}, "height": 0.4, "at": [[0, "H - 0.4", 0, 0]], "standsOn": ["shaft"], "walked": True,
                     "_about": "the tower's flat top, a terrace round the drum or the spire"},
            "balustrade": {"type": "cresting", "run": [["0 - W / 2 + 0.3", 0], ["W / 2 - 0.3", 0]], "h": 1.1, "panel": 1.0, "t": 0.25,
                           "at": [[0, "H", "W / 2 - 0.3", 0], [0, "H", "0 - (W / 2 - 0.3)", 3.1415927], ["W / 2 - 0.3", "H", 0, 1.5707963], ["0 - (W / 2 - 0.3)", "H", 0, -1.5707963]],
                           "standsOn": ["head"], "_about": "the pierced balustrade round the top"},
            "pinnacles": comp("components/pinnacle", {"w": "pin * 1.6", "h": "pin * 2", "s": "pin * 5"}, P4("H"), standsOn=["head"]),
            "drum": {"type": "enclosure", "plan": {"sides": 8, "radius": "drumR"}, "thickness": "t * 0.7", "height": "drumH", "glass": False, "at": [[0, "H", 0, 0]],
                     "openings": [{"at": 0, "width": "drumR * 0.3", "sill": "drumH * 0.25", "springing": "drumH * 0.62", "head": semi}], "standsOn": ["head"]},
            "drum head": {"type": "prism", "plan": {"sides": 8, "radius": "drumR + 0.25"}, "height": 0.35, "at": [[0, "H + drumH - 0.35", 0, 0]], "flatRoof": True, "standsOn": ["drum"]},
            "dome": {"type": "dome", "sides": 8, "radius": "drumR + 0.25", "thickness": 0, "head": {"profile": "pointed", "spread": "spread"},
                     "at": [[0, "H + drumH", 0, 0]], "standsOn": ["drum head"], "_about": "the pointed stone dome, the mitre"},
            "finial": {"type": "column", "radius": "W * 0.03", "height": "W * 0.2", "sides": 6, "at": [[0, 0, 0, 0]], "atop": "dome", "standsOn": ["dome"]},
            "spire": {"type": "pinnacle", "w": "W * 0.62", "h": "W * 0.12", "s": "spireH", "sides": 8, "crockets": 1, "at": [[0, "H", 0, 0]], "standsOn": ["head"],
                      "_about": "the crocketed octagonal spire"},
            "turret": {"type": "prism", "plan": {"sides": 8, "radius": "turretR"}, "height": "H + pin * 2", "at": [["W / 2", 0, "W / 2", 0]],
                       "_about": "the stair turret at a corner, rising past the top"},
            "turret cap": {"type": "pinnacle", "w": "turretR * 2.2", "h": "pin", "s": "turretR * 5", "sides": 8, "crockets": 1, "at": [["W / 2", "H + pin * 2", "W / 2", 0]],
                           "standsOn": ["turret"]},
        }}


def write_components(root):
    for nm, doc in (("manueline-portal", _portal()), ("mitre-tower", _tower())):
        open(os.path.join(root, f"assets/architecture/components/{nm}.json"), "w").write(json.dumps(doc, indent=1) + "\n")
