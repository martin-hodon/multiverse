# LATE-GOTHIC SECULAR BUILDING (Saxony and the Empire, c. 1470-1530: the Albrechtsburg in Meissen, Torgau's Hartenfels,
# the town halls and the Residenzen after them) -- the L2 pieces a palace-castle of the time is made of, written once:
#   * components/wendelstein  (L1) -- THE OPEN STAIR TOWER: an n-gon standing out from a wing's wall, a spiral inside round
#     an open eye, its fronts almost all opening -- an open arcade at the foot, great arches on slender piers storey over
#     storey, each storey's parapet a balustrade band -- and at its head the loggia the stair arrives in, a gable and
#     pinnacles over every front face and a slender needle. `climb` steps the storeys up face by face with the stair
#     (Torgau's way); 0 keeps them level (Meissen's). wendelstein-n{n}-r{rows}: the same for other counts.
#   * components/lucarne     (L1) -- THE ZWERCHHAUS: a dormer standing on the eave flush with the front, one or two
#     storeys of windows under its own gable with little pinnacles, and its own roof running back into the great one.
#   * the CURTAIN-ARCH window (`curtain` head, arch/profiles.js, L0): `curtain_window()` one opening or a fitted row;
#     `castle_window()` the Residenz's great window, a curtain head over lights parted by mullion and transom.
#   * a WING: `wing()` -- walls of storeys (`storeys()`) on a rect, its hipped roof, a substructure down the slope;
#     `rect_faces()` its faces as Frames; `along()`/`clear_span()` points on a face as the openings' `at`/`clear` measure it.
#   * Frame -- a face's frame from two plan points (outside on the right of p -> q), to place things along a front.
#   * lucarne_row() -- lucarnes along a front at the eave, as one component part.
# A landmark imports what it needs (tools/archgen/albrechtsburg.py) and calls write_components() once.
import os, json, math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapes import plan_edges
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMP = os.path.join(ROOT, "assets/architecture/components")
r4 = lambda v: round(v, 4)


def curtain_window(width=1.5, sill=1.0, springing=3.6, every=None, rise=0.42, lobes=1, sag=0.5, surround=True, seg=6, **kw):
    """a CURTAIN-ARCH window (Vorhangbogenfenster): its head the `curtain` profile -- quarter-round shoulders and `lobes`
    hanging swags, `rise` the cusps over the springing, `seg` its segments (6: two per shoulder and swag); with `every` a row that fits any face (assemble.js laidOut),
    `surround` a dressed stone frame round it. Extra keys (with, clear, end, at) pass through."""
    o = {"width": width, "sill": sill, "springing": springing, "head": {"profile": "curtain", "rise": rise, "lobes": lobes, "sag": sag, **({"seg": seg} if seg else {})}}
    if every is not None: o["every"] = every
    else: o["at"] = 0
    if surround: o["surround"] = {"band": 0.16, "depth": 0.07, "head": False, "sill": True}
    return {**o, **kw}


class Frame:
    """a straight front from plan point p to q (x, z): `along` from its middle, `off` out of it (the outside is on the right
    of p -> q, as an enclosure's faces are), `yaw` turns a part's +z to face out"""
    def __init__(s, p, q):
        ed = plan_edges([p, q])[0]                    # (shapes.py: its middle, direction, inward normal, length)
        s.p, s.q, s.L, s.e, s.m = p, q, ed["L"], ed["e"], ed["mid"]
        s.n = (-ed["n_in"][0], -ed["n_in"][1]); s.yaw = math.atan2(s.n[0], s.n[1])
    def at(s, along=0.0, off=0.0): return (s.m[0] + s.e[0] * along + s.n[0] * off, s.m[1] + s.e[1] * along + s.n[1] * off)
    def place(s, along=0.0, off=0.0, y=0.0, turn=0.0): a, b = s.at(along, off); return [r4(a), r4(y), r4(b), r4(s.yaw + turn)]
    def spread(s, every, end=2.5):
        """the `along`s of a row fitted to the front: as many as fit `every` apart, centred, the outer ones `end` in from the ends"""
        k = max(0, int((s.L - 2 * end) / every + 1e-9) + 1)
        return [(j - (k - 1) / 2) * every for j in range(k)]


def lucarne_row(add, name, frame, alongs, eave, params, off=0.05, build=None, about=None):
    """lucarnes (components/lucarne) standing on the eave of a front at each `along`, their faces `off` proud of the wall"""
    if not alongs: return None
    d = {"type": "component", "use": "components/lucarne", "params": params, "at": [frame.place(a, off, eave) for a in alongs],
         "_about": about or "a row of lucarnes (Zwerchhauser) on the eave, flush with the front"}
    if build: d["build"] = build
    return add(name, d)


def castle_window(width=2.5, sill=1.0, springing=4.4, every=None, lights=2, rows=2, rise=0.5, **kw):
    """the Residenz's GREAT WINDOW: a curtain head over `lights` lights in `rows`, parted by mullion and transom (tracery
    bars), no dressed frame (the cusps of a frame's band would spike)"""
    return curtain_window(width, sill, springing, every=every, rise=rise, surround=False,
                          tracery={"style": "bars", "cols": lights, "rows": rows, "bar": 0.11}, **kw)


def storeys(heights, clear=(), doors=(), every=3.8, great=2.5, small=1.15):
    """a face's storeys, `heights` [ground, main..., the last taking the rest]: the ground floor's small curtain-arch windows,
    the main floors' great ones (castle_window), each row fitted to the face `every` apart; `clear` stretches kept blind
    (another wing against it, a stair tower before it), `doors` among the ground floor's windows"""
    kw = {"clear": [list(c) for c in clear]} if clear else {}
    tiers = [{"h": heights[0], "openings": curtain_window(small, 1.3, heights[0] - 1.6, every=every, end=1.4, rise=0.34, surround=False,
                                                         **kw, **({"with": list(doors)} if doors else {}))}]
    for k, h in enumerate(heights[1:]):
        o = castle_window(great, 1.0, h - 2.0, every=every, end=1.6, **kw)
        tiers.append({"openings": o} if k == len(heights) - 2 else {"h": h, "openings": o})
    return tiers


def plain_storeys(heights, every=4.2, width=0.9):
    """the substructure's storeys under a wing, down the slope: plain walls, a small window to each bay"""
    o = curtain_window(width, 1.2, 0, every=every, end=1.6, rise=0.26, surround=False)
    tiers = [{"h": h, "openings": {**o, "springing": r4(h - 1.4)}} for h in heights]
    tiers[-1] = {"openings": tiers[-1]["openings"]}
    return tiers


def rot(px, pz, yaw): return (px * math.cos(yaw) + pz * math.sin(yaw), -px * math.sin(yaw) + pz * math.cos(yaw))
def rect_faces(c, w, l, yaw):
    """an enclosure's four faces on a rect plan [w, l] centred at c, yawed: in the engine's order (planPoints) +z, +x, -z, -x"""
    q = [(-w / 2, l / 2), (w / 2, l / 2), (w / 2, -l / 2), (-w / 2, -l / 2)]
    pts = [(c[0] + rot(x, z, yaw)[0], c[1] + rot(x, z, yaw)[1]) for x, z in q]
    return [Frame(pts[i], pts[(i + 1) % 4]) for i in range(4)]
def along(f, p): return r4((p[0] - f.m[0]) * f.e[0] + (p[1] - f.m[1]) * f.e[1])
def clear_span(f, p, q): return sorted([along(f, p), along(f, q)])


def wing(add, name, c, w, l, yaw, faces, about, y0, heights, pitch=52, overhang=0.3, ridge_along_l=True, thickness=1.3,
         sub=None, sub_open=()):
    """A WING of the Residenz: walls on a rect [w, l] (yawed: its +z along l) standing at height y0, its storeys `heights`
    (storeys()), and its hipped roof; `faces` {i: None (blind: another wing stands against it) | {clear, doors}} by
    rect_faces' numbering, the faces not named windowed all along. `sub`: the substructure under it, that many metres down
    the slope to the rock, its storeys plain, windowed on the faces `sub_open`. Returns its faces (Frames)."""
    H = sum(heights)
    spec = {str(i): (storeys(heights, **v) if v is not None else []) for i, v in faces.items()}
    add(name, {"type": "enclosure", "plan": {"rect": [r4(w), r4(l)]}, "thickness": thickness, "height": r4(H), "glass": True,
               "tiers": storeys(heights), "faces": spec, "courses": {"plinth": 0.8 if not sub else False, "strings": [heights[0]], "cornice": 0.45},
               "at": [[r4(c[0]), r4(y0), r4(c[1]), r4(yaw)]], "_about": about})
    add(name + " roof", {"type": "roof", "form": "hip", "width": r4(w if ridge_along_l else l), "length": r4(l if ridge_along_l else w),
                         "pitch": pitch, "overhang": overhang,
                         "at": [[r4(c[0]), r4(y0 + H), r4(c[1]), r4(yaw if ridge_along_l else yaw + math.pi / 2)]]})
    if sub:
        hs = [sub / 2, sub / 2] if sub > 7 else [sub]
        add(name + " substructure", {"type": "enclosure", "plan": {"rect": [r4(w), r4(l)]}, "thickness": thickness + 0.4, "height": r4(sub),
                                     "glass": True, "tiers": [{"openings": []}] if len(hs) == 1 else [{"h": r4(hs[0]), "openings": []}, {"openings": []}],
                                     "faces": {str(i): plain_storeys([r4(h) for h in hs]) for i in sub_open},
                                     "courses": {"plinth": 1.2, "strings": [], "cornice": False},
                                     "at": [[r4(c[0]), r4(y0 - sub), r4(c[1]), r4(yaw)]],
                                     "_about": "its substructure down the slope to the rock: plain walls, small windows"})
    return rect_faces(c, w, l, yaw)


# ---------------------------------------------------------------- L1: the open stair tower
def wendelstein(n=8, rows=3, open_faces=None):
    """THE WENDELSTEIN as a component: `n` faces (an n-gon `R` to its corners), of which `open_faces` (default: those turned
    no more than 90 degrees from +z, the front) are opened up; the others are blind (they stand in the wing's wall). Over
    the foot's open arcade (the door on the face toward +z) `rows` storeys of great arches `winW` wide on piers `pier`
    wide, a parapet band (`parapet` high, a string at its foot and its head: the balustrade) under each; then the
    loggia the stair arrives in (`stageH`), a gable over every open face, pinnacles at their corners, and the needle
    (`capRise`). `arch` names the arches' head (pointed, curtain...), `spread` a pointed head's sharpness, `archRise` its
    rise. `climb` (0..1) lifts each face's storeys by its share of a storey round the tower -- the stair's climb drawn on
    the outside; `turns` how many turns the spiral makes to H. The face count and `rows` are the drawing's structure,
    fixed here (wendelstein-n{n}-r{rows} for others); everything else is a param."""
    open_faces = open_faces if open_faces is not None else [i for i in range(n) if math.cos(2 * math.pi * (i + 1) / n) > -1e-9]
    # face i's middle is at bearing (i + 1) * 360 / n from +z toward +x (build.js planPoints); vertex k at (k + 0.5) * 360 / n
    f = {i: r4(((i + 1) % n) / n) for i in range(n)}
    door_face = n - 1
    head = {"profile": "arch", "spread": "spread", "rise": "rise", "lobes": 1, "sag": 0.55, "seg": 6}
    def arch(sill, spring): return {"at": 0, "width": "winW", "sill": sill, "springing": spring, "head": head, "glass": False}
    faces = {}
    for i in range(n):
        if i not in open_faces: faces[str(i)] = []; continue
        tiers = [{"h": f"footH + climb * {f[i]} * rowH", "openings": [arch(0 if i == door_face else "footSill", "footH - band - archRise")]}]
        tiers += [{"h": "rowH", "openings": [arch("parapet", "rowH - band - archRise")]} for _ in range(rows)]
        tiers.append({"openings": []})
        faces[str(i)] = tiers
    crown = {str(i): ([arch("parapet", "stageH - band - archRise")] if i in open_faces else []) for i in range(n)}
    corners = sorted({k % n for i in open_faces for k in (i, i + 1)})
    bear = lambda i: 2 * math.pi * (i + 1) / n
    strings = [x for k in range(rows) for x in (f"footH + {k} * rowH", f"footH + {k} * rowH + parapet")]
    T = {
      "name": "Wendelstein",
      "_about": (f"THE WENDELSTEIN, the open stair tower of the late-Gothic Residenz (the Albrechtsburg's Grosser Wendelstein, 1471-1524; "
                 f"Torgau's after it): a {n}-sided tower `R` to its corners standing out from a wing's front, a SPIRAL inside round an open "
                 f"eye (`eye`) from the door at its foot (the face toward +z) up to `H`, the floor it arrives at, in `turns` turns. Its fronts "
                 f"are nearly all opening: the foot an open arcade (`footH`), then {rows} storeys of great `arch`-headed arches `winW` wide "
                 f"on piers `pier` wide, a balustrade band (`parapet`) under each; over `H` the loggia (`stageH`), a cornice, a GABLE "
                 f"(`gableH`) over every open face with PINNACLES at its corners, and the slate NEEDLE (`capRise`) with a finial. `climb` "
                 f"lifts each face's storeys by its share of a storey round the tower, so the openings climb with the stair (0: level, "
                 f"as at Meissen). The back faces are blind: set the tower so they stand in the wing's wall (its middle `a` = R cos(180/n) "
                 f"out from the wall's face, less `t`). Place it at its middle, yawed so +z faces out. Written by tools/archgen/late_gothic.py."),
      "params": {
        "detail": 4, "R": 3.9, "t": 0.45, "H": 17.0, "footH": 3.6, "stageH": 3.8, "capRise": 13.0, "finial": 1.4,
        "eye": 0.6, "pier": 0.35, "arch": "pointed", "spread": 0.5, "rise": 0.42, "parapet": 1.0, "band": 0.45, "footSill": 0.5,
        "climb": 0, "turns": 4, "stepRise": 0.18, "gableH": 2.8, "pinW": 0.36, "pinS": 1.2,
        "_R": "the tower's corner radius; `t` its shell (thin: the piers between the arches are the structure); H the floor the stair arrives at",
        "_arch": "the arches' head (a profile word: pointed, curtain, ...); `spread` a pointed head's sharpness, `rise` a curtain head's",
        "_climb": "0: the storeys level all round; 1: each face's a share of a storey higher than the last, round the tower with the stair",
        "_parapet": "the balustrade under each storey's arches; `band` the solid over them; `footSill` the arcade's parapet (the door's face has none)",
        "_stepRise": "the steps' rise wanted (12-22cm); their number follows from H",
        "a": f"R * {r4(math.cos(math.pi / n))}", "side": f"R * {r4(2 * math.sin(math.pi / n))}", "winW": "side - 2 * pier",
        "archRise": "winW / 2 * sqrt(1 + 2 * spread)", "rowH": f"(H - footH - band) / ({rows} + climb)",
        "sr": "a - t - 0.08", "steps": "round(H / stepRise)", "turn": "360 * turns / steps",
        "_a": "the faces' distance from the middle; `side` a face's width", "_archRise": "the arches' rise (a pointed head's; give `rise` for a curtain head)",
        "_rowH": "a storey of arches", "_turn": "the spiral's turn per step: `turns` whole turns from the door to the floor at H",
      },
      "build": ["shaft", "stair", "crown", "cornice", "gables", "pinnacles", "cap", "finial"],
      "parts": {
        "shaft": {"type": "enclosure", "plan": {"sides": n, "radius": "R"}, "thickness": "t", "height": "H", "glass": False, "faces": faces,
                  "courses": {"plinth": 0.5, "strings": strings, "cornice": False},
                  "at": [[0, 0, 0, 0]], "_about": "the shell: the open arcade at the foot, storeys of great arches over balustrade bands; the back faces blind"},
        "stair": {"type": "spiral-stair", "radius": "sr", "newel": "eye", "post": False, "turn": "turn", "top": "H", "steps": "steps", "soffit": 0.22,
                  "at": [[0, 0, 0, 0]], "_about": "the spiral round its open eye, from the door to the floor at H"},
        "crown": {"type": "enclosure", "plan": {"sides": n, "radius": "R"}, "thickness": "t", "height": "stageH", "glass": False, "faces": crown,
                  "courses": {"plinth": False, "strings": ["parapet"], "cornice": False},
                  "at": [[0, "H", 0, 0]], "_about": "the loggia the stair arrives in, an arch in every front face"},
        "cornice": {"type": "prism", "plan": {"sides": n, "radius": "R + 0.18"}, "height": 0.3, "flatRoof": True, "at": [[0, "H + stageH", 0, 0]],
                    "standsOn": ["crown"], "_about": "the cornice and the ceiling under the needle"},
        "gables": {"type": "screen", "outline": [["0 - side / 2", 0], ["side / 2", 0], [0, "gableH"]], "t": 0.3,
                   "at": [[f"a * {r4(math.sin(bear(i)))}", "H + stageH + 0.3", f"a * {r4(math.cos(bear(i)))}", r4(bear(i))] for i in open_faces],
                   "standsOn": ["cornice"], "_about": "a gable over every open face"},
        "pinnacles": {"type": "pinnacle", "w": "pinW", "h": "gableH + 1.0", "s": "pinS",
                      "at": [[f"R * {r4(math.sin((k + 0.5) * 2 * math.pi / n))}", "H + stageH + 0.3", f"R * {r4(math.cos((k + 0.5) * 2 * math.pi / n))}", 0] for k in corners],
                      "standsOn": ["cornice"], "_about": "a pinnacle at every corner between the gables"},
        "cap": {"type": "dome", "sides": n, "radius": "R - 0.35", "thickness": 0, "head": {"profile": "trigonal", "rise": "capRise"},
                "at": [[0, "H + stageH + 0.3", 0, 0]], "standsOn": ["cornice"], "_about": "the slender slate needle"},
        "finial": {"type": "column", "radius": 0.1, "height": "finial", "sides": 6, "at": [[0, 0, 0, 0]], "atop": "cap", "standsOn": ["cap"]},
        "interior": {"type": "interior", "of": ["shaft"], "plan": {"sides": n, "radius": "a - t"}, "height": "H",
                     "_about": "the stair's well (open: the air's)"}
      }
    }
    return T


# ---------------------------------------------------------------- L1: the lucarne (Zwerchhaus)
def lucarne():
    return {
      "name": "Lucarne",
      "_about": ("A LUCARNE (Zwerchhaus): the dormer of the late-Gothic Residenz, standing ON THE EAVE flush with the front -- the wall "
                 "carried up `H` over the eave, `W` wide and `D` deep back into the great roof, with a window in each of its two storeys "
                 "(the lower `low` of H), and over it its own GABLE, `GH` high on the front with a little pinnacle at each foot and one on "
                 "the apex, its own gabled roof running back into the great one. The Albrechtsburg's ring of them makes its skyline. "
                 "Place it at the middle of its front, on the eave, yawed so +z faces out; `head` its windows' heads (a profile name: "
                 "curtain, pointed, flat...)."),
      "params": {
        "detail": 4, "W": 4.2, "D": 6.0, "H": 5.6, "GH": 3.6, "t": 0.45, "low": 0.55, "winW": 1.3, "rise": 0.38,
        "pinW": 0.32, "pinH": 0.9, "pinS": 1.3, "head": "curtain",
        "h0": "H * low", "pitch": "atan2(GH * 0.92, W / 2) * 57.29578",
        "_W": "its width; D how far its own roof runs back into the great roof (its back is hidden in it)",
        "_low": "the share of H the lower window's storey takes; the upper window has the rest",
        "_pitch": "its roof's pitch, from the gable",
      },
      "build": ["body", "gable", "roof", "pinnacles"],
      "parts": {
        "body": {"type": "enclosure", "plan": {"rect": ["W", "D"]}, "thickness": "t", "height": "H", "glass": True,
                 "faces": {"0": [{"h": "h0", "openings": [{"at": 0, "width": "winW", "sill": 0.6, "springing": "h0 - 0.45 - rise", "head": {"profile": "head", "rise": "rise", "sag": 0.55, "seg": 6},
                                                             "surround": {"band": 0.14, "depth": 0.06, "head": False, "sill": True}}]},
                                 {"openings": [{"at": 0, "width": "winW * 0.85", "sill": 0.5, "springing": "H - h0 - 0.4 - rise", "head": {"profile": "head", "rise": "rise", "sag": 0.55, "seg": 6},
                                                "surround": {"band": 0.14, "depth": 0.06, "head": False, "sill": True}}]}],
                           "1": [], "2": [], "3": []},
                 "at": [[0, 0, "0 - D / 2", 0]], "_about": "the wall carried up over the eave, two windows in its front"},
        "gable": {"type": "screen", "outline": [["0 - W / 2", 0], ["W / 2", 0], [0, "GH"]], "t": "t", "at": [[0, "H", 0, 0]],
                  "_about": "its gable, in the plane of the front"},
        "roof": {"type": "roof", "form": "gable", "width": "W - 0.05", "length": "D - 0.1", "pitch": "pitch", "overhang": 0.12,
                 "at": [[0, "H", "0 - D / 2 - 0.1", 0]], "_about": "its own roof, its ridge running back into the great roof"},
        "pinnacles": {"type": "pinnacle", "w": "pinW", "h": "pinH", "s": "pinS",
                      "at": [["pinW / 2 - W / 2", "H", "0 - t / 2", 0], ["W / 2 - pinW / 2", "H", "0 - t / 2", 0], [0, "H + GH - 0.25", "0 - t / 2", 0]],
                      "_about": "a little pinnacle at each foot of the gable and on its apex"}
      }
    }


def write_components(variants=()):
    """components/wendelstein (8 faces, 3 storeys) and components/lucarne; `variants` [(n, rows)] also writes
    components/wendelstein-n{n}-r{rows} for a tower of other counts"""
    docs = [("wendelstein", wendelstein()), ("lucarne", lucarne())] + [(f"wendelstein-n{n}-r{r}", wendelstein(n, r)) for n, r in variants]
    for nm, d in docs:
        open(os.path.join(COMP, f"{nm}.json"), "w").write(json.dumps(d, indent=2) + "\n")
