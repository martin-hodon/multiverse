#!/usr/bin/env python3
"""THE CRAFTS (2026-11-21; docs/items.md "Crafts and trades"): the things the village's people play, eat from and work
with that were still missing, or stood in as bare boxes in the workshops (tools/archgen/village.py furniture) and the
mine (mine.js) -- written as items the way tools/propgen.py writes its props:

- the BARD'S INSTRUMENTS beside the lute and the lyre (index.html BARD_INSTRUMENTS, the fire's musician): the fiddle
  with its bow (a violin, or a medieval vielle: `style`), the recorder, the transverse flute, the Gothic harp
- TABLEWARE: the plate (a turned wooden trencher, pewter or glazed ware: `style`; tableware.js lays the food on one)
  and the iron cauldron (on its own legs, on a tripod or hung by a chain: `mount`; the hearth's, over its fire)
- the WORKSHOPS' gear: the anvil on its stump (smithy), the great bellows (smithy, its top board on a `hinge`), the
  floor loom (weaver), the joiner's workbench with its leg vice and the sawhorse (carpenter), the potter's kick wheel
  (pottery), the butcher's block, the dress form and the tailor's shears (tailor), the baker's oven peel (bakery)
- the MINE's: the miner's frog lamp (its flame a `fire` marker, as the candlestick's), the windlass and the kibble

    python3 tools/craftgen.py       # -> assets/items/{tools,tableware,furniture}/*.json, listed in assets/index.json

THE FRAME is the period items': the origin on the floor (or the table) under the thing's middle, y up; furniture's
front toward +z; an instrument's neck up +y with its face toward +z, as the lute's. Lengths in metres; `at` is
[x, y, z, yaw, pitch, roll] in degrees (items.js: R = Ry Rx Rz). Each item's materials are ROLES (wood, iron, string,
cloth...), most of them a pick drawn by the seed, so no two looms in a village are the same wood.
"""
import fcntl, json, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "modern"))
from kit import box, rod, sphere, lathe, sweep, plate, use, hinge, euler, arc, r3, runs


def ring(id_, mat, r, tube, at, sides=10, sec=6, **k):
    """a hoop, a link, an ear: a torus in the xz plane as an open LATHE of a hexagonal tube section -- 120 triangles
    where items.js `ring` (a closed sweep, its path smoothed to ~26 stations) makes 312 for the smallest ear
    (`sec` 4: a diamond section, for links in a chain: 64 triangles at 8 sides)"""
    prof = []
    for i in range(sec + 1):
        a = math.pi * 2 * i / sec
        dx, dy = round(tube * math.cos(a), 5), round(tube * math.sin(a), 5)
        prof.append([f"{r} + {dx}" if isinstance(r, str) else round(r + dx, 5), dy])
    return lathe(id_, mat, prof, at, sides=sides, caps=False, **k)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ITEMS = os.path.join(ROOT, "assets", "items")
CRAFTS = {}
D2R = "0.0174533"


def item(name, category, about, params, materials, parts, markers=None, hold=None, era="1200-1900", region="Europe"):
    d = {"kind": "item", "name": name, "category": category, "era": era, "region": region, "_about": about,
         "params": params, "materials": materials, "parts": [p for p in parts if p]}
    if markers: d["markers"] = markers
    if hold: d["hold"] = hold
    return d


# ---- helpers ----------------------------------------------------------------------------------------------------
def beam(id_, mat, a, b, w, d, **k):
    """a square-sawn member from point a to point b (its length along its own y), w across and d deep: a splayed leg,
    a brace -- turned so its width lies as near the x-z plane as it can"""
    v = [b[i] - a[i] for i in range(3)]
    L = math.sqrt(sum(c * c for c in v))
    ya = [c / L for c in v]
    hint = [0, 0, 1] if abs(ya[2]) < 0.9 else [1, 0, 0]
    xa = [ya[1] * hint[2] - ya[2] * hint[1], ya[2] * hint[0] - ya[0] * hint[2], ya[0] * hint[1] - ya[1] * hint[0]]
    lx = math.sqrt(sum(c * c for c in xa)); xa = [c / lx for c in xa]
    za = [xa[1] * ya[2] - xa[2] * ya[1], xa[2] * ya[0] - xa[0] * ya[2], xa[0] * ya[1] - xa[1] * ya[0]]
    m = [(a[i] + b[i]) / 2 for i in range(3)]
    return box(id_, mat, [w, L, d], [*m, *euler(xa, ya, za)], **k)


def band(id_, mat, r, h, t, at, sides=16, **k):
    """an iron hoop round a turned thing: a short open lathe r out, h high, t proud -- far cheaper than a torus"""
    out = (lambda d: f"{r} + {d}") if isinstance(r, str) else (lambda d: r + d)
    return lathe(id_, mat, [[out(0), -h / 2], [out(t), -h / 2 + t], [out(t), h / 2 - t], [out(0), h / 2]], at, sides=sides, caps=False, **k)


def spread(part, xs):
    """one part laid again at each x offset (its own turn kept): four treadles side by side"""
    a = part["at"]
    part["at"] = [[a[0] + x, *a[1:]] for x in xs]
    return part


def smooth(ctrl, n=6):
    """Catmull-Rom through control points [(y, hw)], n samples a span -- an outline's half"""
    out = []
    P = [ctrl[0]] + ctrl + [ctrl[-1]]
    for i in range(1, len(P) - 2):
        for s in range(n):
            t = s / n
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(2)))
    out.append(ctrl[-1])
    return out


def body_outline(ctrl, k=1.0):
    """a symmetric outline in the x-y plane from its right half's (y, half-width) controls, bottom to top; k scales
    the width (a rib's inset)"""
    half = smooth(ctrl)
    right = [[hw * k, y] for y, hw in half if hw > 1e-6]
    return [[0, ctrl[0][0]]] + right + [[0, ctrl[-1][0]]] + [[-x, y] for x, y in reversed(right)]


def lean_pt(x, y, z=0):
    """a point of an upright thing leaned `lean` degrees toward -x about its foot (an expression the item resolves)"""
    c, s = f"cos(lean * {D2R})", f"sin(lean * {D2R})"
    return [f"({x}) * {c} - ({y}) * {s}", f"({x}) * {s} + ({y}) * {c}", z]


# ==== THE BARD'S INSTRUMENTS =======================================================================================
# Held as the lute is (tools/lute.json): the body against the player, the neck up its own +y, the face +z; `rest`
# "body" -- it rests against the body where the hand holds it, the hand playing over it (tools.js BODY_REST).
LUTE_HOLD = {"axis": [0, 1, 0], "face": [0, 0, 1], "carry": {"axis": [0.1, 0.5, 1], "face": [1, 0, 0]}, "follow": 0, "rest": "body"}

# ---- THE FIDDLE: a violin's waisted body (1550 on: Cremona's pattern, 356 mm) or a medieval VIELLE's (the oval
# fiddle of the 13th-15th centuries, a leaf-shaped peg head with five frontal pegs) by `style`, each with its bow laid
# across the strings between the bridge and the fingerboard. Back, ribs and belly are three plates of the outline
# (the ribs inset, so the edges overhang); the f-holes (C-holes on the vielle) dark sweeps on the belly.
VIOLIN = [(-0.178, 0), (-0.176, 0.045), (-0.165, 0.082), (-0.135, 0.101), (-0.095, 0.103), (-0.062, 0.092), (-0.045, 0.07),
          (-0.02, 0.056), (0.012, 0.057), (0.035, 0.068), (0.052, 0.082), (0.085, 0.084), (0.125, 0.077), (0.158, 0.058),
          (0.174, 0.032), (0.178, 0)]
VIELLE = [(-0.215, 0), (-0.21, 0.055), (-0.185, 0.095), (-0.13, 0.112), (-0.06, 0.104), (0.0, 0.094), (0.06, 0.1),
          (0.12, 0.096), (0.165, 0.074), (0.192, 0.042), (0.2, 0)]


def fiddle():
    v, m = {"when": {"style": "violin"}}, {"when": {"style": "vielle"}}
    parts = [
        # the violin: back, ribs, belly; its neck, fingerboard, nut, pegbox and scroll; four pegs; tailpiece and button
        plate("back", "body", body_outline(VIOLIN), 0.004, [0, 0, -0.018], **v),
        plate("ribs", "body", body_outline(VIOLIN, 0.96), 0.034, [0, 0, 0], **v),
        plate("belly", "top", body_outline(VIOLIN), 0.004, [0, 0, 0.018], **v),
        sweep("fhole", "dark", [[0.03, -0.06, 0.0205], [0.036, -0.04, 0.0205], [0.03, -0.015, 0.0205], [0.034, 0.012, 0.0205]], r=0.0022, mirror="x", **v),
        box("neck", "body", [0.026, 0.135, 0.022], [0, 0.245, 0.015], **v),
        plate("fingerboard", "fittings", [[-0.012, 0.312], [0.012, 0.312], [0.021, 0.05], [-0.021, 0.05]], 0.006, [0, 0, 0.031], **v),
        box("nut", "fittings", [0.025, 0.005, 0.008], [0, 0.312, 0.036], **v),
        box("pegbox", "body", [0.024, 0.075, 0.026], [0, 0.35, 0.013], **v),
        sweep("scroll", "body", [[0, 0.385, 0.026], [0, 0.405, 0.03], [0, 0.42, 0.016], [0, 0.415, 0.0], [0, 0.4, 0.002], [0, 0.398, 0.014], [0, 0.408, 0.016]],
              radii=[0.012, 0.012, 0.011, 0.01, 0.009, 0.008, 0.006], **v),
        rod("pegs", "fittings", 0.0035, [-0.026, 0, 0], [0.026, 0, 0], 6, at=[[0, 0.326, 0.013], [0, 0.341, 0.013], [0, 0.356, 0.013], [0, 0.371, 0.013]], **v),
        sphere("pegHeads", "fittings", 0.009, [[-0.03, 0.326, 0.013], [0.03, 0.341, 0.013], [-0.03, 0.356, 0.013], [0.03, 0.371, 0.013]], sides=6, stretch=[0.5, 1, 1.3], **v),
        plate("tailpiece", "fittings", [[-0.008, -0.155], [0.008, -0.155], [0.019, -0.085], [0, -0.08], [-0.019, -0.085]], 0.006, [0, 0, 0.026], **v),
        rod("button", "fittings", 0.005, [0, -0.177, 0], [0, -0.186, 0], 8, **v),
        # the vielle: its oval body, C-holes, a short neck into a flat leaf-shaped peg head with five frontal pegs
        plate("vBack", "body", body_outline(VIELLE), 0.004, [0, 0, -0.022], **m),
        plate("vRibs", "body", body_outline(VIELLE, 0.96), 0.042, [0, 0, 0], **m),
        plate("vBelly", "top", body_outline(VIELLE), 0.004, [0, 0, 0.022], **m),
        sweep("chole", "dark", [[0.05, -0.07, 0.0245], [0.06, -0.045, 0.0245], [0.058, -0.015, 0.0245], [0.048, 0.005, 0.0245]], r=0.0025, mirror="x", **m),
        box("vNeck", "body", [0.032, 0.11, 0.024], [0, 0.255, 0.016], **m),
        plate("vFingerboard", "fittings", [[-0.015, 0.31], [0.015, 0.31], [0.022, 0.1], [-0.022, 0.1]], 0.006, [0, 0, 0.034], **m),
        plate("leaf", "body", [[0, 0.3], [0.03, 0.315], [0.042, 0.35], [0.038, 0.39], [0.02, 0.42], [0, 0.43], [-0.02, 0.42], [-0.038, 0.39], [-0.042, 0.35], [-0.03, 0.315]], 0.018, [0, 0, 0.018], **m),
        rod("vPegs", "fittings", 0.0035, [0, 0, -0.012], [0, 0, 0.04], 6, at=[[-0.018, 0.34, 0], [0.018, 0.34, 0], [-0.016, 0.375, 0], [0.016, 0.375, 0], [0, 0.405, 0]], **m),
        box("vPegHeads", "fittings", [0.022, 0.008, 0.008], [[-0.018, 0.34, -0.012], [0.018, 0.34, -0.012], [-0.016, 0.375, -0.012], [0.016, 0.375, -0.012], [0, 0.405, -0.012]], **m),
        plate("vTailpiece", "fittings", [[-0.01, -0.2], [0.01, -0.2], [0.024, -0.12], [-0.024, -0.12]], 0.006, [0, 0, 0.03], **m),
        # the bridge (an arched plate stood across the belly) and the strings over it, tailpiece to nut
        plate("bridge", "bridgeWood", [[-0.02, 0], [0.02, 0], [0.018, 0.009], [0.013, 0.026], [0, 0.03], [-0.013, 0.026], [-0.018, 0.009]], 0.004, [0, -0.035, 0.02, 0, 90, 0], **v),
        rod("stringsLow", "string", 0.0008, [0, -0.083, 0.03], [0, -0.035, 0.0495], 3, along={"n": 4, "from": [-0.012, 0, 0], "to": [0.012, 0, 0]}, **v),
        rod("strings", "string", 0.0008, [0, -0.035, 0.0495], [0, 0.312, 0.0405], 3, along={"n": 4, "from": [-0.01, 0, 0], "to": [0.01, 0, 0]}, **v),
        plate("vBridge", "bridgeWood", [[-0.028, 0], [0.028, 0], [0.026, 0.012], [0.02, 0.022], [-0.02, 0.022], [-0.026, 0.012]], 0.005, [0, -0.08, 0.024, 0, 90, 0], **m),
        rod("vStringsLow", "string", 0.0009, [0, -0.122, 0.034], [0, -0.08, 0.0465], 3, along={"n": 5, "from": [-0.018, 0, 0], "to": [0.018, 0, 0]}, **m),
        rod("vStrings", "string", 0.0009, [0, -0.08, 0.0465], [0, 0.31, 0.0425], 3, along={"n": 5, "from": [-0.016, 0, 0], "to": [0.016, 0, 0]}, **m),
        # THE BOW across the strings, near the bridge: the stick over its hair, the frog at the hand's end, the tip
        rod("bowHair", "hair", 0.0022, [-0.42, "bowY", 0.052], [0.19, "bowY", 0.052], 4),
        sweep("bowStick", "fittings", [[0.24, "bowY", 0.068], [0.1, "bowY", "0.066 + arch"], [-0.15, "bowY", "0.064 + arch"], [-0.38, "bowY", "0.06 + arch * 0.5"], [-0.44, "bowY", 0.055]],
              radii=[0.0045, 0.0042, 0.0036, 0.003, 0.003]),
        box("frog", "fittings", [0.04, 0.012, 0.018], [0.205, "bowY", 0.061]),
        rod("bowButton", "bridgeWood", 0.004, [0.24, "bowY", 0.068], [0.255, "bowY", 0.068], 6),
        box("bowTip", "bridgeWood", [0.012, 0.008, 0.012], [-0.43, "bowY", 0.055]),
    ]
    return item("Fiddle", "tool", "the fiddle and its bow: a violin's waisted body (style violin: belly, back and overhanging ribs, f-holes, a scroll and four side pegs) or a medieval vielle's oval one (style vielle: C-holes, five frontal pegs in a flat leaf of a peg head), its strings over an arched bridge, the bow laid across them -- held against the body as the lute is",
        {"style": {"pick": ["violin", "violin", "vielle"]}, "bowY": [-0.02, 0.0], "arch": {"pick": [0.0, 0.0, 0.03]}},
        {"body": {"pick": ["cherry", "walnut", "mahogany"]}, "top": {"pick": ["cherry", "walnut"]}, "fittings": "ebony", "bridgeWood": "ivory",
         "string": "gut", "hair": "hair-white", "dark": "mouth-dark"},
        parts, hold={"grip": [0, -0.1, 0.06], **LUTE_HOLD}, era="1200-1900")


# ---- THE RECORDER: a turned boxwood pipe in three joints (head, body, foot), the beak and window at the head, seven
# finger holes before and the thumb's behind; `L` from a descant's 0.32 to an alto's 0.46 m, so every recorder in a
# village is a little its own; ivory rings at the joints on a good one
def recorder():
    Y = lambda f: f"L * {f}"
    prof = [[0, 0], [0.012, 0], [0.0158, Y(0.02)], [0.0162, Y(0.05)], [0.0138, Y(0.09)], [0.0118, Y(0.125)], [0.0136, Y(0.135)],
            [0.0136, Y(0.15)], [0.0115, Y(0.16)], [0.0122, Y(0.4)], [0.0132, Y(0.68)], [0.0152, Y(0.7)], [0.0168, Y(0.73)],
            [0.0168, Y(0.94)], [0.015, Y(0.975)], [0.0095, "L"], [0, "L"]]
    holes = [0.62, 0.555, 0.49, 0.415, 0.35, 0.285, 0.21]
    return item("Recorder", "tool", "the recorder: a turned pipe in three joints -- the head with its beak and window, the body with seven finger holes before and the thumb hole behind, the bell-flared foot -- from a descant to an alto (`L`), ivory rings at the joints on some",
        {"L": [0.31, 0.46], "rings": {"pick": [0, 0, 1]}},
        {"wood": {"pick": ["ash", "cherry", "walnut", "ebony"]}, "dark": "mouth-dark", "ring": "ivory"}, [
            lathe("pipe", "wood", prof, sides=14),
            box("window", "dark", [0.009, 0.007, 0.004], [0, Y(0.885), 0.0155]),
            box("beak", "wood", [0.02, Y(0.05), 0.012], [0, Y(0.97), -0.006], round=0.004),
            rod("holes", "dark", 0.0026, [0, 0, 0.0112], [0, 0, 0.0142], 8, at=[[0, Y(f), 0] for f in holes]),
            rod("thumb", "dark", 0.0028, [0, 0, -0.0118], [0, 0, -0.0145], 8, at=[0, Y(0.655), 0]),
            ring("rings", "ring", 0.0158, 0.0018, [[0, Y(0.7), 0], [0, Y(0.142), 0]], when="rings"),
        ], hold={"grip": [0, 0.12, 0], "axis": [0, 1, 0], "face": [0, 0, 1], "carry": {"axis": [-0.35, 1, 0], "face": [1, 0.35, 0]}, "follow": 0, "rest": "body"},
        era="1300-1900")


# ---- THE TRANSVERSE FLUTE: the Renaissance's one-piece cylinder of boxwood (or a baroque one in joints with ivory
# ferrules: `ferrules`), stopped above the embouchure hole, six finger holes down its length; held out to the right
def flute():
    Y = lambda f: round(0.6 * f, 4)
    return item("Flute", "tool", "the transverse flute: a turned cylinder, stopped at its head, the embouchure hole near it and six finger holes down its length; a Renaissance flute plain, a baroque one in joints with ivory ferrules -- held out across the player's right",
        {"ferrules": {"pick": [0, 1]}},
        {"wood": {"pick": ["ash", "cherry", "walnut"]}, "dark": "mouth-dark", "ring": "ivory"}, [
            lathe("tube", "wood", [[0, 0], [0.0118, 0], [0.0118, Y(0.3)], [0.0125, Y(0.31)], [0.0125, Y(0.97)], [0.013, Y(0.985)], [0.0105, Y(1.0)], [0, Y(1.0)]], sides=14),
            lathe("bore", "dark", [[0.0075, -0.0005], [0, -0.0005]], sides=10),
            rod("embouchure", "dark", 0.0042, [0, 0, 0.0115], [0, 0, 0.0136], 10, at=[0, Y(0.905), 0], stretch=[1, 1.25, 1]),
            rod("holes", "dark", 0.0032, [0, 0, 0.011], [0, 0, 0.013], 8, at=[[0, Y(f), 0] for f in (0.62, 0.575, 0.53, 0.43, 0.385, 0.34)]),
            lathe("ferrules", "ring", [[0.0136, -0.012], [0.0138, 0], [0.0136, 0.012]], sides=14, caps=False, at=[[0, Y(0.31), 0], [0, Y(0.68), 0], [0, Y(0.96), 0]], when="ferrules"),
            lathe("cap", "ring", [[0.0128, 0], [0.0128, 0.008], [0.006, 0.012], [0, 0.012]], at=[0, Y(1.0), 0], when="ferrules"),
        ], hold={"grip": [0, 0.17, 0], "axis": [0, 1, 0], "face": [0, 0, 1], "carry": {"axis": [0.15, 0.3, -1], "face": [0.2, 1, 0]}, "follow": 0, "rest": "body"},
        era="1400-1900")


# ---- THE HARP: a Gothic harp of the 15th century (Memling's angels', the Brian Boru's cousins), 0.82 m, played on the
# lap: the soundbox rising as the triangle's long side from the foot to the neck (its belly in pine, a string rib down
# it), the neck curving over in its S, the pillar standing up in front; sixteen gut strings, upright, from the rib up
# to the tuning pins in the neck -- the harp's plane the x-y plane, its pillar toward +x (away from the player)
def harp():
    B, T = (0.0, 0.06), (-0.28, 0.68)
    ang = math.degrees(math.atan2(T[1] - B[1], T[0] - B[0]))
    L = math.hypot(T[0] - B[0], T[1] - B[1])
    nx, ny = -math.sin(math.radians(ang)), math.cos(math.radians(ang))   # (the loft's +y in the harp's plane: the back)
    neck = [(-0.305, 0.69), (-0.2, 0.728), (-0.08, 0.716), (0.03, 0.75), (0.125, 0.81)]
    def neck_y(x):
        for (x0, y0), (x1, y1) in zip(neck, neck[1:]):
            if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return neck[-1][1]
    strings, pins = [], []
    n = 16
    for i in range(n):
        t = 0.08 + 0.86 * i / (n - 1)
        bx, by = B[0] + (T[0] - B[0]) * t - nx * 0.008, B[1] + (T[1] - B[1]) * t - ny * 0.008
        top = neck_y(bx) - 0.02
        strings.append(rod(f"string{i}", "string", 0.0011 + 0.0007 * (1 - t), [bx, by, 0], [bx, top, 0], 4))   # (unrounded: write() rounds; `runs` folds the rounding)
        pins.append([r3(bx), r3(top + 0.012), 0])
    at = [B[0], B[1], 0, 0, 0, round(ang, 2)]
    return item("Harp", "tool", "a Gothic harp played on the lap: the soundbox rising from the foot as the triangle's long side (its pine belly, a string rib down it), the neck curving over in its S, the pillar standing in front, sixteen gut strings upright from the rib to the tuning pins -- its plane the x-y plane, the pillar toward +x",
        {}, {"frame": {"pick": ["walnut", "cherry", "oak"]}, "board": "pine", "rib": "ebony", "string": "gut", "pin": {"pick": ["iron", "brass"]}}, [
            {"id": "soundbox", "type": "loft", "material": "frame", "stations": [[0, 0.055, 0.004, 0.085], [L * 0.5, 0.042, 0.004, 0.062], [L, 0.024, 0.004, 0.034]], "round": 0.012, "at": at},
            {"id": "belly", "type": "loft", "material": "board", "stations": [[0.01, 0.05, 0.0, 0.006], [L * 0.5, 0.038, 0.0, 0.006], [L - 0.01, 0.021, 0.0, 0.006]], "round": 0.002, "at": at},
            {"id": "stringRib", "type": "loft", "material": "rib", "stations": [[0.02, 0.008, -0.008, 0.002], [L - 0.02, 0.006, -0.008, 0.002]], "round": 0.003, "at": at},
            sweep("neck", "frame", [list(p) + [0] for p in neck], section=[0.034, 0.046], radii=[1.15, 1, 0.9, 1, 1.15]),
            sweep("pillar", "frame", [[0.13, 0.03, 0], [0.175, 0.25, 0], [0.172, 0.5, 0], [0.135, 0.79, 0]], radii=[0.021, 0.017, 0.016, 0.02]),
            box("foot", "frame", [0.2, 0.05, 0.06], [0.06, 0.03, 0]),
            lathe("finial", "frame", [[0.02, 0], [0.026, 0.015], [0.018, 0.03], [0.008, 0.045], [0, 0.05]], at=[0.13, 0.8, 0]),
            rod("pins", "pin", 0.0025, [0, 0, -0.026], [0, 0, 0.026], 5, at=pins),
            *runs("strings", strings),   # (2026-11-22: `each` runs, one a straight stretch of the neck)
        ], hold={"grip": [-0.1, 0.3, 0], "axis": [0, 1, 0], "face": [1, 0, 0], "carry": {"axis": [0, 1, 0], "face": [1, 0, 0]}, "follow": 0, "rest": "body"},
        era="1100-1700")


# ==== TABLEWARE ====================================================================================================
# ---- THE PLATE (`style`): a medieval TRENCHER turned from a wood (a deep well, a broad rim), a PEWTER plate (flat, a
# wide rim with a cast bead at its edge -- the 16th-18th centuries'), or GLAZED WARE (a tin-glazed or slipware dish,
# a painted band round its well); `R` its radius, a little its own. Its foot at the origin, the food's place `well`
# over it (tableware.js lays the food there)
def plate_item():
    R = lambda f: f"R * {f}"
    return item("Plate", "tableware", "a plate to eat from: a turned wooden trencher (style trencher), a pewter plate with a cast bead round its rim (pewter), or glazed ware with a band painted round its well (ceramic) -- on its foot at the origin, the food's place in its well",
        {"style": "trencher", "R": [0.11, 0.13], "well": 0.009},
        {"wood": {"pick": ["oak", "ash", "birch", "walnut"]}, "pewter": "pewter", "glaze": {"pick": ["paint-cream", "faience-white", "terracotta"]},
         "band": {"pick": ["enamel-blue", "faience-green", "enamel-red"]}}, [
            lathe("trencher", "wood", [[0, 0], [R(0.68), 0], [R(0.78), 0.006], [R(0.98), 0.016], [R(1.0), 0.02], [R(0.95), 0.022], [R(0.82), 0.013], [R(0.62), 0.009], [0, 0.009]],
                  sides=28, when={"style": "trencher"}),
            lathe("pewter", "pewter", [[0, 0], [R(0.55), 0], [R(0.58), 0.004], [R(0.63), 0.012], [R(0.985), 0.016], [R(1.0), 0.0185], [R(0.985), 0.02], [R(0.66), 0.017], [R(0.6), 0.007], [0, 0.006]],
                  sides=24, when={"style": "pewter"}),
            ring("bead", "pewter", R(0.985), 0.0018, [0, 0.019, 0], when={"style": "pewter"}),
            lathe("dish", "glaze", [[0, 0], [R(0.45), 0], [R(0.46), 0.006], [R(0.52), 0.006], [R(0.72), 0.013], [R(0.96), 0.024], [R(1.0), 0.027], [R(0.965), 0.028], [R(0.72), 0.0168], [R(0.5), 0.0108], [0, 0.0098]],
                  sides=24, when={"style": "ceramic"}),
            lathe("band", "band", [[R(0.74), 0.0181], [R(0.84), 0.0229]], sides=24, caps=False, double=True, when={"style": "ceramic"}),
        ], hold={"grip": [0, 0.01, 0], "axis": [0, 0, 1], "face": [0, 1, 0], "carry": {"axis": [1, 0, 0], "face": [0, 1, 0]}, "follow": 0.7},
        era="800-1900")


# ---- THE CAULDRON: a cast-iron pot, round-bellied, its rim lipped, two ears and an iron bail, the stew in it to `fill`;
# `mount` how it stands over the fire -- on its own three LEGS (the posnet's), hung by a CHAIN from a hook above (`top`
# the chain's top over the origin: the hearth's, from its hood), or from a TRIPOD of iron legs with the chain down
# from its crown. `lift` raises the pot's foot over the origin (the legs' height: 0.11). Origin on the ground (the
# hearth) under the pot
def cauldron():
    r = lambda f: f"r * {f}"
    y = lambda f: f"lift + r * {f}"
    hang = {"mount": ["chain", "tripod"]}
    prof = [[0, y(0)], [r(0.5), y(0)], [r(0.82), y(0.06)], [r(0.98), y(0.3)], [r(1.0), y(0.62)], [r(0.94), y(0.95)], [r(0.86), y(1.18)],
            [r(0.86), y(1.27)], [r(0.95), y(1.33)], [r(0.95), y(1.38)], [r(0.83), y(1.38)], [r(0.79), y(1.22)], [r(0.88), y(0.95)],
            [r(0.9), y(0.62)], [r(0.75), y(0.15)], [0, y(0.08)]]
    bailTop = "lift + r * 2.25"
    # (2026-11-22, the in-game budget: a link a diamond section round 8 sides, 64 triangles -- it was 120, and a hearth's
    #  chain of 18 links was 2160 of the cauldron's 3774, in every house)
    link = lambda id_, off, yaw: ring(id_, "iron", 0.017, 0.0042, [0, 0, 0, yaw, 90, 0], sides=8, sec=4, stretch=[1, 1.55, 1],
                                      along={"n": "max(1, round((top - lift - r * 2.25) / 0.07))", "from": [0, f"top - 0.025 - {off}", 0], "to": [0, f"lift + r * 2.25 + 0.03 + {off}", 0]}, when=hang)
    return item("Cauldron", "tableware", "an iron cauldron: a round-bellied cast pot, its rim lipped, two ears and a bail, the stew in it -- on its own three legs (mount legs), hung by a chain from a hook above (chain: the hearth's, from its hood), or from an iron tripod's crown (tripod)",
        {"r": [0.17, 0.21], "mount": "legs", "lift": 0.11, "top": 1.2, "fill": 0.8},
        {"iron": "iron", "stew": {"pick": ["crust-dark", "bean", "carrot"]}}, [
            lathe("pot", "iron", prof, sides=18),
            lathe("stew", "stew", [[r(0.86), f"lift + r * (0.3 + 0.85 * fill)"], [0, f"lift + r * (0.3 + 0.85 * fill)"]], sides=14, when="fill"),
            ring("ears", "iron", 0.022, 0.007, [[r(0.97), y(1.3), 0, 0, 90, 0], [r(-0.97), y(1.3), 0, 0, 90, 0]], sides=8),
            sweep("bail", "iron", [[r(-0.97), y(1.36), 0], [r(-0.75), y(1.95), 0], [0, bailTop, 0], [r(0.75), y(1.95), 0], [r(0.97), y(1.36), 0]], r=0.0065, sides=6),
            rod("legs", "iron", 0.02, [r(0.62), "lift + 0.03", 0], [r(0.7), 0, 0], 6, r1=0.012, around={"n": 3, "r": 0}, when={"mount": "legs"}),
            # the chain, of links alternately across and along, from `top` down to the bail
            link("linksA", 0, 0), link("linksB", 0.035, 90),
            sweep("hook", "iron", [[0, bailTop, 0], [0.012, f"{bailTop} + 0.03", 0], [0, f"{bailTop} + 0.05", 0], [-0.01, f"{bailTop} + 0.035", 0]], r=0.005, when=hang),
            rod("crane", "iron", 0.012, [0, "top", -0.15], [0, "top", 0.15], 6, when={"mount": "chain"}),
            ring("crown", "iron", 0.03, 0.01, [0, "top", 0], when={"mount": "tripod"}),
            rod("tripod", "iron", 0.014, [0.02, "top", 0], ["top * 0.42", 0, 0], 6, r1=0.011, around={"n": 3, "r": 0}, when={"mount": "tripod"}),
        ], hold={"grip": [0, "lift + r * 2.25", 0], "axis": [1, 0, 0], "face": [0, 0, 1], "carry": {"axis": [0, 0, 1], "face": [1, 0, 0]}},
        era="-500-1900")


# ==== THE WORKSHOPS ================================================================================================
# ---- THE ANVIL ON ITS STUMP (the smithy): a wrought anvil of the London pattern -- its feet, waist, body, steel face,
# the heel with the hardy and pritchel holes, the step and the horn -- dogged onto an elm stump bound with an iron
# band; `stump` 0 the anvil alone on the floor. Its horn toward +x
def anvil():
    b = lambda v: f"base + {v}"
    return item("Anvil", "furniture", "a smith's anvil of the London pattern on its stump: splayed feet, the waist, the body with its steel face, the heel with the hardy and pritchel holes, the step and the conical horn (+x) -- dogged onto an iron-bound stump (stump 0: on the floor)",
        {"stump": 1, "sh": [0.5, 0.56], "base": "stump * sh"},
        {"stump": {"pick": ["oak-grey", "oak"]}, "endgrain": "pine", "iron": "iron", "steel": "steel", "dark": "mouth-dark"}, [
            lathe("stump", "stump", [[0, 0], [0.31, 0], [0.3, 0.05], [0.27, 0.18], [0.265, "sh - 0.03"], [0.26, "sh"], [0, "sh"]], sides=11, faceted=True, when="stump"),
            lathe("endgrain", "endgrain", [[0.248, "sh"], [0.248, "sh + 0.003"], [0, "sh + 0.003"]], sides=11, when="stump"),
            band("band", "iron", 0.262, 0.04, 0.006, [0, "sh - 0.07", 0], sides=11, when="stump"),
            plate("feet", "iron", [[-0.2, 0], [-0.07, 0], [-0.055, 0.026], [0.055, 0.026], [0.07, 0], [0.2, 0], [0.18, 0.03], [0.08, 0.09], [-0.08, 0.09], [-0.18, 0.03]], 0.2, [0, "base", 0]),
            plate("feetAcross", "iron", [[-0.12, 0], [-0.04, 0], [-0.03, 0.02], [0.03, 0.02], [0.04, 0], [0.12, 0], [0.1, 0.03], [0.05, 0.09], [-0.05, 0.09], [-0.1, 0.03]], 0.3, [0, "base", 0, 90, 0, 0]),
            rod("waist", "iron", 0.11, [0, b(0.085), 0], [0, b(0.175), 0], 4, r1=0.08, at=[0, 0, 0, 45, 0, 0], stretch=[1.25, 1, 0.75]),
            plate("body", "iron", [[-0.17, 0.17], [0.08, 0.17], [0.12, 0.195], [0.132, 0.24], [0.132, 0.272], [0.06, 0.272], [0.06, 0.291], [-0.27, 0.291], [-0.27, 0.252], [-0.21, 0.225]], 0.11, [0, "base", 0]),
            box("face", "steel", [0.33, 0.008, 0.112], [-0.105, b(0.2945), 0]),
            lathe("horn", "iron", [[0.046, 0], [0.042, 0.04], [0.03, 0.1], [0.014, 0.16], [0.004, 0.185], [0, 0.19]], [0.125, b(0.228), 0, 0, 0, -90], sides=12),
            box("hardy", "dark", [0.024, 0.003, 0.024], [-0.225, b(0.2995), 0]),
            box("pritchel", "dark", [0.013, 0.003, 0.013], [-0.17, b(0.2995), 0.028]),
            box("hardyTool", "iron", [0.022, 0.05, 0.03], [-0.225, b(0.32), 0], when="stump"),
            rod("dogs", "iron", 0.008, [0, b(0.045), 0], [0, b(-0.05), 0], 4, at=[[0.22, 0, 0.06], [-0.22, 0, -0.06], [0.05, 0, 0.16], [-0.05, 0, -0.16]], when="stump"),
        ], era="1600-1950")


# ---- THE GREAT BELLOWS (the smithy): two boards of a pear's outline with the leather between them in folds, the
# nozzle block at the narrow end and its iron tuyere (+x) -- bent toward -z by `pipe` metres into the forge's side --
# on a stand of four legs; the top board a HINGE at the nozzle end (`open` lifts its broad end: the blow), with its
# strap, the weight stone and the handle the smith works it by
def bellows():
    out = arc(-0.22, 0, 0.27, 90, 270, 10) + [[0.4, -0.065], [0.4, 0.065]]
    inner = arc(-0.22, 0, 0.25, 90, 270, 10) + [[0.38, -0.055], [0.38, 0.055]]
    big = arc(-0.22, 0, 0.285, 90, 270, 10) + [[0.38, -0.075], [0.38, 0.075]]
    flat = lambda yy: [0, yy, 0, 0, -90, 0]
    y0, gap = 0.72, 0.13
    piv = [0.4, y0 + 0.035 + gap, 0]
    return item("Bellows", "furniture", "a smithy's great bellows: two pear-shaped boards with the leather between them in folds, the nozzle block and iron tuyere at the narrow end (+x, bent aside by `pipe` into the forge), on a four-legged stand; the top board hinged at the nozzle (`open`: its broad end lifted), weighted with a stone, worked by its handle",
        {"pipe": 0, "open": 0},
        {"wood": {"pick": ["oak", "ash", "pine"]}, "leather": {"pick": ["leather", "leather-dark"]}, "fold": "leather-dark", "iron": "iron", "stone": "stone"}, [
            use("legs", "components/square-leg", [[0.28, 0, 0.17], [0.28, 0, -0.17], [-0.38, 0, 0.17], [-0.38, 0, -0.17]], {"h": y0, "w": 0.07, "taper": 0.85}),
            box("sideRails", "wood", [0.78, 0.08, 0.05], [[-0.05, y0 - 0.06, 0.17], [-0.05, y0 - 0.06, -0.17]]),
            box("endRails", "wood", [0.05, 0.08, 0.36], [[0.28, y0 - 0.06, 0], [-0.38, y0 - 0.06, 0]]),
            box("stretchers", "wood", [0.04, 0.04, 0.36], [[0.28, 0.15, 0], [-0.38, 0.15, 0]]),
            box("stretcher", "wood", [0.66, 0.04, 0.04], [-0.05, 0.15, 0]),
            plate("bottomBoard", "wood", out, 0.035, flat(y0 + 0.0175)),
            plate("leather", "leather", inner, gap, flat(y0 + 0.035 + gap / 2)),
            plate("fold", "fold", big, 0.014, flat(y0 + 0.035 + gap * 0.3)),
            box("nozzleBlock", "wood", [0.09, gap + 0.07, 0.15], [0.4, y0 + 0.035 + gap / 2, 0]),
            rod("tuyere", "iron", 0.042, [0.44, y0 + 0.09, 0], [0.68, y0 + 0.08, 0], 10, r1=0.02),
            sweep("pipe", "iron", [[0.67, y0 + 0.08, 0], [0.76, y0 + 0.08, 0], [0.8, y0 + 0.08, "0 - pipe * 0.45"], [0.81, y0 + 0.08, "0 - pipe"]], r=0.019, when="pipe"),
            hinge("blow", piv, [
                plate("topBoard", "wood", out, 0.035, flat(y0 + 0.035 + gap + 0.0175)),
                plate("upperFold", "fold", big, 0.014, flat(y0 + 0.035 + gap * 0.75)),
                box("strap", "iron", [0.7, 0.006, 0.05], [-0.1, y0 + 0.035 + gap + 0.038, 0]),
                sphere("stone", "stone", 0.09, [-0.24, y0 + gap + 0.12, 0.05], sides=7, stretch=[1.2, 0.6, 1]),
                rod("handle", "wood", 0.022, [-0.47, y0 + gap + 0.07, 0], [-0.62, y0 + gap + 0.55, 0], 8),
                rod("grip", "wood", 0.02, [-0.62, y0 + gap + 0.55, -0.15], [-0.62, y0 + gap + 0.55, 0.15], 8),
                ring("eye", "iron", 0.025, 0.006, [-0.47, y0 + gap + 0.06, 0, 0, 0, 90]),
            ], axis=(0, 0, -1), max_=14),
        ], era="1200-1900")


# ---- THE FLOOR LOOM (the weaver): a horizontal treadle loom -- its two side frames, the castle rising over the middle
# with the pulley roller the two heddle shafts hang from, the batten swinging from it with its reed, the warp from the
# warp beam at the back over the back beam through the heddles (the shed open: half the threads up, half down) to the
# fell of the cloth, the woven cloth over the breast beam and down onto the cloth beam, four treadles under it, the
# shuttle in the shed. The weaver sits at +z. 1.9 m wide, 1.3 deep, 1.75 high
def floor_loom():
    W, zf, zb = 0.9, 0.6, -0.6
    th = {"n": 36, "from": [-0.6, 0, 0], "to": [0.6, 0, 0]}
    return item("Floor loom", "furniture", "a treadle floor loom: side frames and the castle over the middle, two heddle shafts hung from its pulley roller, the batten and reed swinging from its top, the warp from the warp beam at the back over the back beam through the heddles -- the shed open, half the threads up and half down -- to the fell of the cloth, the woven cloth over the breast beam and wound onto the cloth beam, four treadles, the shuttle in the shed; the weaver sits at +z",
        {}, {"wood": {"pick": ["oak", "ash", "pine"]}, "warp": {"pick": ["linen", "wool"]}, "cloth": {"pick": ["wool", "linen", "damask-red", "velvet-green", "damask-blue"]},
             "cord": "hemp", "iron": "iron"}, [
            box("posts", "wood", [0.09, 0.95, 0.09], [[x, 0.475, z] for x in (-W, W) for z in (zf, zb)]),
            box("castlePosts", "wood", [0.09, 1.75, 0.09], [[-W, 0.875, -0.05], [W, 0.875, -0.05]]),
            box("castleTop", "wood", [2 * W + 0.12, 0.1, 0.12], [0, 1.75, -0.05]),
            box("lowRails", "wood", [0.08, 0.08, zf - zb + 0.09], [[-W, 0.12, 0], [W, 0.12, 0]]),
            box("topRails", "wood", [0.08, 0.09, zf - zb + 0.09], [[-W, 0.92, 0], [W, 0.92, 0]]),
            box("breastBeam", "wood", [2 * W, 0.1, 0.1], [0, 0.85, zf]),
            box("backBeam", "wood", [2 * W, 0.09, 0.09], [0, 0.87, zb]),
            rod("warpBeam", "wood", 0.045, [-W, 0.45, zb + 0.05], [W, 0.45, zb + 0.05], 10, at=[0, 0, 0]),
            rod("warpRoll", "warp", 0.1, [-0.65, 0.45, zb + 0.05], [0.65, 0.45, zb + 0.05], 14),
            rod("clothBeam", "wood", 0.045, [-W, 0.4, zf - 0.08], [W, 0.4, zf - 0.08], 10),
            rod("clothRoll", "cloth", 0.075, [-0.65, 0.4, zf - 0.08], [0.65, 0.4, zf - 0.08], 14),
            sweep("ratchet", "iron", [[W + 0.05, 0.45, zb + 0.05], [W + 0.05, 0.45, zb + 0.05 + 0.0001]], r=0.08, sides=10),
            # the warp: back roll up over the back beam, on to the heddles, the shed opening to the fell
            rod("warpBack", "warp", 0.0012, [0, 0.55, zb + 0.06], [0, 0.915, zb], 3, along=th),
            rod("warpRun", "warp", 0.0012, [0, 0.915, zb], [0, 0.85, -0.05], 3, along=th),
            rod("shedUp", "warp", 0.0012, [0, 0.88, -0.05], [0, 0.885, 0.3], 3, along={"n": 18, "from": [-0.6, 0, 0], "to": [0.57, 0, 0]}),
            rod("shedDown", "warp", 0.0012, [0, 0.82, -0.05], [0, 0.885, 0.3], 3, along={"n": 18, "from": [-0.57, 0, 0], "to": [0.6, 0, 0]}),
            box("web", "cloth", [1.2, 0.006, zf - 0.3 + 0.05], [0, 0.89, (zf + 0.3) / 2 + 0.02]),
            box("webDown", "cloth", [1.2, 0.42, 0.006], [0, 0.69, zf + 0.055]),
            # two heddle shafts: their bars, the string heddles, hung by cords from the roller
            box("shaftBars", "wood", [1.36, 0.025, 0.02], [[0, y, z] for y in (0.62, 1.08) for z in (-0.08, -0.02)]),
            rod("heddles", "cord", 0.0009, [0, 0.62, 0], [0, 1.08, 0], 3, at=[[0, 0, -0.08], [0, 0, -0.02]], along={"n": 30, "from": [-0.62, 0, 0], "to": [0.62, 0, 0]}),
            rod("roller", "wood", 0.04, [-0.75, 1.6, -0.05], [0.75, 1.6, -0.05], 10),
            rod("shaftCords", "cord", 0.003, [0, 1.6, -0.05], [0, 1.08, 0], 4, at=[[-0.5, 0, -0.03], [0.5, 0, -0.03], [-0.5, 0, 0.03], [0.5, 0, 0.03]]),
            # the batten from the castle's top: its swords, the lower bar the reed stands in, the cap over it
            beam("swordL", "wood", [-W + 0.08, 1.72, 0.0], [-W + 0.08, 0.8, 0.28], 0.06, 0.04),
            beam("swordR", "wood", [W - 0.08, 1.72, 0.0], [W - 0.08, 0.8, 0.28], 0.06, 0.04),
            box("battenBar", "wood", [2 * W - 0.1, 0.07, 0.07], [0, 0.8, 0.28]),
            box("battenCap", "wood", [2 * W - 0.1, 0.04, 0.05], [0, 0.99, 0.23]),
            rod("reed", "cord", 0.0012, [0, 0.835, 0.27], [0, 0.97, 0.235], 3, along={"n": 40, "from": [-0.68, 0, 0], "to": [0.68, 0, 0]}),
            # four treadles from their pivot bar at the back, their cords up to the shafts
            rod("treadleBar", "wood", 0.025, [-0.4, 0.05, -0.45], [0.4, 0.05, -0.45], 8),
            spread(beam("treadles", "wood", [0, 0.05, -0.45], [0, 0.11, 0.42], 0.06, 0.03), [-0.3, -0.1, 0.1, 0.3]),
            rod("treadleCords", "cord", 0.003, [0, 0.1, -0.05], [0, 0.62, -0.05], 4, at=[[-0.3, 0, 0], [-0.1, 0, 0], [0.1, 0, 0], [0.3, 0, 0]]),
            # the boat shuttle in the shed, its bobbin of weft
            sphere("shuttle", "wood", 0.04, [0.15, 0.865, 0.2], sides=8, stretch=[3.2, 0.45, 0.5]),
        ], era="1100-1900")


# ---- THE JOINER'S WORKBENCH (the carpenter): a heavy top on four square legs with stretchers and a shelf under, the
# LEG VICE at its front left (the chop, its wooden screw and tommy bar, the parallel guide at its foot), dog holes along
# the front, a planing stop at the right end, a holdfast, a drawer and a jack plane. 2.2 m by 0.6, its front +z
def workbench():
    H, hw, hd = 0.88, 1.1, 0.3
    return item("Workbench", "furniture", "a joiner's workbench: a thick top on four square legs with stretchers and a shelf under it, a leg vice at the front left (the chop, its wooden screw and tommy bar, the parallel guide), dog holes along the front, a planing stop at the right end, a holdfast, a drawer, a jack plane on the top -- 2.2 m long, its front +z",
        {}, {"wood": {"pick": ["oak", "ash", "pine"]}, "top": {"pick": ["oak", "planks"]}, "iron": "iron", "dark": "mouth-dark", "steel": "steel"}, [
            box("top", "top", [2 * hw, 0.1, 2 * hd], [0, H - 0.05, 0]),
            use("legs", "components/square-leg", [[x, 0, z] for x in (-0.95, 0.95) for z in (-0.22, 0.22)], {"h": H - 0.1, "w": 0.1, "taper": 1}),
            box("stretchers", "wood", [1.8, 0.08, 0.06], [[0, 0.2, -0.22], [0, 0.2, 0.22]]),
            box("endRails", "wood", [0.06, 0.08, 0.44], [[x, y, 0] for x in (-0.95, 0.95) for y in (0.2, H - 0.14)]),
            box("shelf", "wood", [1.84, 0.025, 0.44], [0, 0.255, 0]),
            box("shelfBoards", "wood", [1.2, 0.03, 0.15], [[0.1, 0.283, -0.08], [0.05, 0.313, -0.07]]),
            # the leg vice
            box("chop", "wood", [0.2, 0.78, 0.07], [-0.95, 0.47, hd + 0.04]),
            rod("screw", "wood", 0.03, [-0.95, 0.72, 0.15], [-0.95, 0.72, hd + 0.16], 10),
            lathe("boss", "wood", [[0.05, 0], [0.05, 0.05], [0.032, 0.07], [0, 0.07]], [-0.95, 0.72, hd + 0.075, 0, 90, 0], sides=12),
            rod("tommyBar", "wood", 0.013, [-1.15, 0.72, hd + 0.13], [-0.75, 0.72, hd + 0.13], 8),
            box("guide", "wood", [0.06, 0.04, 0.35], [-0.95, 0.12, hd - 0.1]),
            rod("guidePeg", "wood", 0.012, [-0.95, 0.1, hd - 0.2], [-0.95, 0.17, hd - 0.2], 6),
            # the top's furniture: dog holes along the front, the planing stop, a holdfast
            box("dogHoles", "dark", [0.022, 0.002, 0.022], [0, H + 0.0005, hd - 0.07], along={"n": 7, "from": [-0.55, 0, 0], "to": [0.95, 0, 0]}),
            box("stop", "wood", [0.06, 0.035, 0.06], [hw - 0.08, H + 0.017, 0.05]),
            sweep("holdfast", "iron", [[0.3, H - 0.12, -0.12], [0.3, H + 0.11, -0.12], [0.34, H + 0.135, -0.12], [0.46, H + 0.06, -0.12], [0.5, H + 0.01, -0.12]], r=0.01),
            # a drawer under the top at the front right, a jack plane lying on the top
            use("drawer", "components/drawer", [0.45, H - 0.17, hd - 0.02], {"w": 0.55, "h": 0.12, "knobs": 1}),
            box("drawerCase", "wood", [0.62, 0.15, 0.04], [0.45, H - 0.17, hd - 0.05]),
            box("planeBody", "wood", [0.36, 0.07, 0.065], [-0.35, H + 0.035, -0.1, 15, 0, 0]),
            sweep("planeTote", "wood", [[-0.43, H + 0.07, -0.08], [-0.46, H + 0.13, -0.075], [-0.41, H + 0.13, -0.065], [-0.39, H + 0.07, -0.06]], r=0.012),
            box("planeIron", "steel", [0.008, 0.06, 0.05], [-0.33, H + 0.09, -0.105, 15, 0, -50]),
        ], era="1600-1950")


# ---- THE SAWHORSE: a squared beam on two pairs of splayed legs, braced across; a V-notch sawn into one end
def sawhorse():
    legs = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            legs.append(beam(f"leg{'L' if sx < 0 else 'R'}{'b' if sz < 0 else 'f'}", "wood", [sx * 0.38, 0.62, sz * 0.03], [sx * 0.45, 0, sz * 0.3], 0.07, 0.045))
    return item("Sawhorse", "furniture", "a sawhorse: a squared beam on two pairs of legs splayed out under it, a brace across each pair, a V notched into one end for holding a pole",
        {}, {"wood": {"pick": ["oak", "ash", "pine", "oak-grey"]}, "iron": "iron"}, [
            box("beam", "wood", [1.0, 0.1, 0.1], [0, 0.65, 0]),
            *legs,
            box("braces", "wood", [0.04, 0.08, 0.46], [[-0.42, 0.25, 0], [0.42, 0.25, 0]]),
            box("cheeks", "wood", [0.16, 0.12, 0.025], [[-0.38, 0.6, 0.064], [-0.38, 0.6, -0.064], [0.38, 0.6, 0.064], [0.38, 0.6, -0.064]]),
            box("notch", "mouth-dark", [0.06, 0.004, 0.06], [0.47, 0.701, 0, 0, 0, 0]),
            rod("nails", "iron", 0.004, [0, 0, -0.08], [0, 0, 0.08], 4, at=[[-0.38, 0.6, 0], [0.38, 0.6, 0]]),
        ], era="any")


# ---- THE POTTER'S KICK WHEEL (the pottery): the heavy flywheel near the floor, kicked by the potter's foot, its iron
# shaft up through a bearing bar to the wheel head, a pot thrown on the head (a bowl, a jar or a beaker: `pr`, `ph`), the
# frame round it -- four posts, a tray round the head, the bearing bar -- a bowl of slip water and a rib on the tray.
# The potter sits at -x
def kick_wheel():
    return item("Kick wheel", "furniture", "a potter's kick wheel: the heavy flywheel near the floor, its iron shaft up through the bearing bar to the wheel head, a pot thrown on it, the frame round it with a tray about the head, a bowl of slip water and a rib on the tray; the potter sits at -x",
        {"pr": [0.06, 0.1], "ph": [0.1, 0.2], "neck": [0.55, 1.0]},
        {"wood": {"pick": ["oak", "ash", "oak-grey"]}, "fly": {"pick": ["oak", "stone"]}, "iron": "iron", "clay": {"pick": ["terracotta", "paint-cream"]}, "wet": "terracotta"}, [
            lathe("flywheel", "fly", [[0, 0.06], [0.36, 0.06], [0.36, 0.15], [0.12, 0.15], [0.08, 0.17], [0, 0.17]], sides=20),
            band("tyre", "iron", 0.36, 0.06, 0.006, [0, 0.105, 0], sides=20),
            box("footBlock", "wood", [0.16, 0.06, 0.16], [0, 0.03, 0]),
            rod("shaft", "iron", 0.02, [0, 0.03, 0], [0, 0.5, 0], 8),
            lathe("head", "wood", [[0, 0.47], [0.05, 0.47], [0.15, 0.495], [0.15, 0.52], [0, 0.52]], sides=18),
            lathe("pot", "clay", [[0, 0.52], ["pr * 0.7", 0.52], ["pr", "0.52 + ph * 0.45"], ["pr * neck", "0.52 + ph"], ["pr * neck + 0.008", "0.52 + ph + 0.006"],
                                  ["pr * neck - 0.006", "0.52 + ph"], ["pr - 0.007", "0.52 + ph * 0.45"], [0, 0.53]], sides=16),
            box("posts", "wood", [0.07, 0.6, 0.07], [[x, 0.3, z] for x in (-0.42, 0.42) for z in (-0.4, 0.4)]),
            box("rails", "wood", [0.06, 0.06, 0.8], [[x, y, 0] for x in (-0.42, 0.42) for y in (0.2, 0.42)]),
            box("bearingBar", "wood", [0.9, 0.07, 0.08], [0, 0.42, 0]),
            box("trayFront", "wood", [0.9, 0.03, 0.22], [[0, 0.6, 0.29], [0, 0.6, -0.29]]),
            box("traySides", "wood", [0.22, 0.03, 0.36], [[0.31, 0.6, 0], [-0.31, 0.6, 0]]),
            box("trayLips", "wood", [0.9, 0.06, 0.025], [[0, 0.63, 0.4], [0, 0.63, -0.4]]),
            lathe("slipBowl", "wet", [[0, 0.615], [0.05, 0.615], [0.075, 0.655], [0.07, 0.658], [0.045, 0.625], [0, 0.623]], [0.3, 0, 0.27], sides=12),
            box("rib", "wood", [0.09, 0.008, 0.05], [0.32, 0.619, -0.25, 30, 0, 0]),
        ], era="any")


# ---- THE BUTCHER'S BLOCK: a round of a great trunk on three splayed legs, end grain up and worn hollow in the middle,
# two iron bands round it, a scraper lying on it
def chopping_block():
    return item("Chopping block", "furniture", "a butcher's block: a round of a great trunk on three splayed legs, end grain up and worn hollow in the middle, bound with two iron bands, the scraper lying on it",
        {"R": [0.36, 0.4]},
        {"wood": {"pick": ["oak", "oak-grey"]}, "endgrain": {"pick": ["pine", "ash"]}, "iron": "iron", "steel": "steel"}, [
            lathe("block", "wood", [[0, 0.34], ["R", 0.34], ["R + 0.01", 0.5], ["R", 0.79], [0, 0.79]], sides=16, faceted=True),
            lathe("top", "endgrain", [["R - 0.01", 0.79], ["R - 0.01", 0.802], ["R * 0.6", 0.797], ["R * 0.25", 0.788], [0, 0.786]], sides=16),
            band("bands", "iron", "R + 0.003", 0.035, 0.005, [[0, 0.42, 0], [0, 0.74, 0]]),
            rod("legs", "wood", 0.05, ["R * 0.5", 0.36, 0], ["R * 0.85", 0, 0], 8, r1=0.04, around={"n": 3, "r": 0}),
            box("scraper", "steel", [0.12, 0.004, 0.09], [0.12, 0.8, 0.1, 20, 0, 0]),
            box("scraperGrip", "wood", [0.13, 0.025, 0.03], [0.13, 0.815, 0.155, 20, 0, 0]),
        ], era="any")


# ---- THE DRESS FORM (the tailor): a padded torso on a turned pole over a three-legged foot, a garment in the making
# on it -- a bodice and a skirt -- and the tape measure hung round its neck
def dress_form():
    torso = [[0, 0.95], [0.165, 0.95], [0.176, 1.0], [0.14, 1.11], [0.132, 1.14], [0.158, 1.24], [0.17, 1.3], [0.158, 1.38], [0.11, 1.43], [0.05, 1.46], [0.045, 1.5], [0, 1.5]]
    bodice = [[0.14, 1.08], [0.139, 1.11], [0.138, 1.14], [0.164, 1.24], [0.176, 1.3], [0.165, 1.37], [0.12, 1.415]]
    return item("Dress form", "furniture", "a tailor's dress form: a padded torso on a turned pole over a three-legged foot, a garment in the making on it -- the bodice pinned over the torso, the skirt flaring from the waist -- and a tape measure hung round its neck",
        {"skirt": {"pick": [0, 1, 1]}},
        {"wood": {"pick": ["walnut", "oak", "mahogany"]}, "pad": {"pick": ["linen", "canvas"]}, "garment": {"pick": ["velvet-red", "damask-blue", "wool", "velvet-green", "damask-red"]},
         "tape": "paint-yellow", "brass": "brass", "pin": "velvet-red"}, [
            rod("feet", "wood", 0.022, [0.02, 0.12, 0], [0.28, 0.01, 0], 6, r1=0.016, around={"n": 3, "r": 0}),
            lathe("hub", "wood", [[0.045, 0.08], [0.045, 0.16], [0.03, 0.2], [0, 0.2]], sides=10),
            rod("pole", "wood", 0.016, [0, 0.16, 0], [0, 0.98, 0], 8),
            lathe("collar", "brass", [[0.03, 0.8], [0.03, 0.83], [0, 0.83]], sides=10),
            lathe("torso", "pad", torso, sides=18, stretch=[1, 1, 0.72]),
            lathe("neckCap", "wood", [[0.05, 1.5], [0.05, 1.515], [0.03, 1.535], [0, 1.54]], sides=12, stretch=[1, 1, 0.8]),
            lathe("bodice", "garment", [[x + 0.006, y] for x, y in bodice], sides=18, caps=False, stretch=[1, 1, 0.72]),
            lathe("skirt", "garment", [[0.15, 1.1], [0.2, 0.95], [0.27, 0.75], [0.31, 0.6]], sides=18, caps=False, double=True, stretch=[1, 1, 0.8], when="skirt"),
            sweep("tape", "tape", [[-0.06, 1.16, 0.115], [-0.068, 1.32, 0.115], [-0.055, 1.43, 0.06], [0, 1.455, -0.045], [0.055, 1.43, 0.06], [0.068, 1.32, 0.115], [0.06, 1.2, 0.115]], section=[0.014, 0.0012]),
            sphere("pincushion", "pin", 0.03, [0.13, 1.4, 0.0], sides=8, stretch=[1, 0.6, 1]),
        ], era="1700-1950")


# ---- THE TAILOR'S SHEARS: two blades on a pivot screw, each running back into its shank and handle bow -- the thumb's
# round, the fingers' long -- lying open (`open` degrees) on the table, flat
def shears():
    blade = [[-0.012, 0.009], [0.03, 0.012], [0.17, 0.002], [0.17, 0.0], [0.03, -0.003], [-0.012, -0.007]]
    half = lambda k, yy, yaw, bow_r, bow_s: [
        plate(f"blade{k}", "steel", blade, 0.003, [0, yy, 0, yaw, -90, 0]),
        sweep(f"shank{k}", "iron", [[-0.01, 0, 0], [-0.05, 0, -0.008], [-0.085, 0, -0.016]], r=0.0045, at=[0, yy, 0, yaw, 0, 0]),
        ring(f"bow{k}", "iron", bow_r, 0.0045, [-0.085 - bow_r, yy, -0.016, yaw, 0, 0], stretch=[bow_s, 1, 1]),
    ]
    return item("Shears", "tool", "a tailor's shears: two long blades crossing on a pivot screw, each running back into its shank and handle bow -- the thumb's round, the fingers' long -- lying open on the table",
        {"gape": [6, 16]},
        {"steel": "steel", "iron": "iron", "brass": "brass"}, [
            *half("A", 0.0015, "gape * 0.5", 0.018, 1.0),
            *half("B", 0.0045, "0 - gape * 0.5", 0.024, 1.4),
            lathe("pivot", "brass", [[0.008, 0], [0.008, 0.008], [0.005, 0.0095], [0, 0.0095]], sides=10),
        ], hold={"grip": [-0.11, 0.004, 0], "axis": [1, 0, 0], "face": [0, 1, 0], "carry": {"axis": [1, -0.3, 0], "face": [0, 1, 0]}, "follow": 0.7},
        era="1500-1950")


# ---- THE OVEN PEEL (the bakery): a long ash handle into a broad thin blade, its edge scorched; `lean` degrees off
# upright toward -x about its foot (stood against the oven or the wall: an arch item turns only about y)
def oven_peel():
    pts = lambda x, y, z=0: lean_pt(x, y, z)
    return item("Oven peel", "tool", "a baker's oven peel: a long ash handle into a broad thin blade, scorched along its edge -- stood on the blade's edge, leaned `lean` degrees toward -x (against the oven or the wall)",
        {"lean": 0, "L": [1.6, 1.85]},
        {"wood": {"pick": ["ash", "pine", "oak"]}, "scorch": "crust-dark"}, [
            plate("blade", "wood", [[-0.15, 0.0], [0.15, 0.0], [0.165, 0.02], [0.16, 0.26], [0.13, 0.31], [0.04, 0.35], [-0.04, 0.35], [-0.13, 0.31], [-0.16, 0.26], [-0.165, 0.02]], 0.01,
                  [0, 0, 0, 0, 0, "lean"]),
            plate("scorch", "scorch", [[-0.15, 0.0], [0.15, 0.0], [0.165, 0.02], [-0.165, 0.02]], 0.012, [0, 0, 0, 0, 0, "lean"]),
            plate("shoulder", "wood", [[-0.04, 0.3], [0.04, 0.3], [0.02, 0.42], [-0.02, 0.42]], 0.026, [0, 0, 0, 0, 0, "lean"]),
            rod("handle", "wood", 0.017, pts(0, 0.38), pts(0, "L"), 8),
            rod("end", "wood", 0.02, pts(0, "L - 0.015"), pts(0, "L + 0.01"), 8),
        ], hold={"grip": [0, 1.2, 0], "axis": [0, 1, 0], "face": [0, 0, 1], "carry": {"axis": [0, 1, 0], "face": [1, 0, 0]}, "follow": 0.35, "rest": "ground"},
        era="any")


# ==== THE MINE =====================================================================================================
# ---- THE FROG LAMP (Froschlampe): the miner's open iron oil lamp of the 16th-19th centuries -- a shallow bowl drawn
# out into a spout where the wick burns, a hinged half lid over its back, the hanger rising from its back into a hook
# with the spike driven into the rock or a set's post at -x. Its ORIGIN is the flame (at the spout's tip), and the
# flame a `fire` marker there (a candle's: one small flickering cone, as the candlestick's)
def frog_lamp():
    return item("Frog lamp", "tool", "a miner's frog lamp: a shallow iron bowl drawn out into a spout where the wick burns (+x), a half lid over its back, the hanger rising from its back into a hook and the spike driven into the rock at -x -- its origin the flame, a `fire` marker",
        {}, {"iron": {"pick": ["iron", "iron", "brass"]}, "oil": "leather-dark", "wick": "hemp"}, [
            lathe("bowl", "iron", [[0, -0.028], [0.028, -0.028], [0.045, -0.018], [0.05, -0.004], [0.047, -0.002], [0.042, -0.015], [0, -0.022]], [-0.055, 0, 0], sides=10, stretch=[1.15, 1, 1]),
            lathe("oil", "oil", [[0.043, -0.012], [0, -0.012]], [-0.055, 0, 0], sides=12, stretch=[1.15, 1, 1]),
            rod("spout", "iron", 0.013, [-0.03, -0.012, 0], [0.002, -0.006, 0], 8, r1=0.006, stretch=[1, 0.6, 1]),
            rod("wick", "wick", 0.0035, [-0.012, -0.01, 0], [0.003, 0.0, 0], 5),
            lathe("lid", "iron", [[0.05, -0.002], [0.04, 0.012], [0.02, 0.02], [0, 0.022]], [-0.07, 0, 0], sides=10, caps=False, double=True, stretch=[0.8, 1, 1]),
            sweep("hanger", "iron", [[-0.11, -0.004, 0], [-0.12, 0.05, 0], [-0.1, 0.11, 0], [-0.06, 0.135, 0], [-0.035, 0.12, 0], [-0.05, 0.1, 0]], r=0.0042, sides=5, seg=3),
            ring("swivel", "iron", 0.012, 0.003, [-0.1, 0.11, 0, 0, 90, 0], sides=8),
            rod("spike", "iron", 0.006, [-0.06, 0.13, 0], [-0.185, 0.13, 0], 6, r1=0.0015),
        ], markers=[{"role": "fire", "at": [0, 0.004, 0], "data": {"r": 0.035, "h": 0.09, "candle": 1}}],
        hold={"grip": [-0.08, 0.13, 0], "axis": [0, 1, 0], "face": [1, 0, 0], "carry": {"axis": [0, 1, 0], "face": [1, 0, 0]}, "follow": 0},
        era="1500-1900")


# ---- THE WINDLASS (Haspel): over the hauling shaft -- two posts on their sills, braced, the octagonal drum between
# them on its iron axle with the rope wound round it, an iron crank at each end (one hanging, one standing: the two
# men's strokes half a turn apart) with its wooden handle. The axle along z, 2.9 m between the handles; the ropes
# leave the drum at x +-0.16
def windlass():
    yA = 1.06
    braces = []
    for sz in (-1, 1):
        for sx in (-1, 1):
            braces.append(beam(f"brace{'n' if sz < 0 else 's'}{'w' if sx < 0 else 'e'}", "wood", [sx * 0.6, 0.16, sz * 1.25], [sx * 0.09, 0.75, sz * 1.25], 0.08, 0.1))
    return item("Windlass", "furniture", "a mine's windlass (Haspel) over the hauling shaft: two posts on their sills, braced, the octagonal drum between them on its iron axle with the rope wound round it, an iron crank at each end -- one hanging, one standing, half a turn apart -- with its handle; the axle along z",
        {}, {"wood": {"pick": ["oak", "oak-grey"]}, "drum": {"pick": ["oak", "pine"]}, "iron": "iron", "rope": "hemp"}, [
            box("sills", "wood", [1.4, 0.16, 0.22], [[0, 0.08, -1.25], [0, 0.08, 1.25]]),
            box("posts", "wood", [0.18, 1.2, 0.18], [[0, 0.76, -1.25], [0, 0.76, 1.25]]),
            box("caps", "wood", [0.26, 0.08, 0.22], [[0, 1.4, -1.25], [0, 1.4, 1.25]]),
            *braces,
            box("bearings", "iron", [0.22, 0.03, 0.2], [[0, yA - 0.045, -1.25], [0, yA - 0.045, 1.25]]),
            lathe("drum", "drum", [[0, -1.12], [0.14, -1.12], [0.15, -1.08], [0.15, 1.08], [0.14, 1.12], [0, 1.12]], [0, yA, 0, 0, 90, 0], sides=8, faceted=True),
            band("drumHoops", "iron", 0.15, 0.04, 0.006, [[0, yA, z, 0, 90, 0] for z in (-1.0, 1.0)], sides=8),
            lathe("rope", "rope", [[0.15, -0.33]] + [[0.163 + (0.011 if k % 2 else 0.0), round(-0.33 + 0.0125 * k, 4)] for k in range(1, 27)] + [[0.15, 0.0]], [0, yA, 0, 0, 90, 0], sides=12, caps=False),
            rod("axle", "iron", 0.03, [0, yA, -1.45], [0, yA, 1.45], 8),
            box("crankN", "iron", [0.05, 0.4, 0.03], [0, yA - 0.17, -1.42]),
            rod("handleN", "wood", 0.024, [0, yA - 0.34, -1.42], [0, yA - 0.34, -1.68], 8),
            box("crankS", "iron", [0.05, 0.4, 0.03], [0, yA + 0.17, 1.42]),
            rod("handleS", "wood", 0.024, [0, yA + 0.34, 1.42], [0, yA + 0.34, 1.68], 8),
            ring("collars", "iron", 0.04, 0.01, [[0, yA, z, 0, 90, 0] for z in (-1.38, 1.38)]),
        ], era="1300-1900")


# ---- THE KIBBLE (Kübel): the mine's hauling bucket -- coopered staves swelling a little at the belly, three iron
# hoops, iron straps up its sides to the ears, the bail with its eye for the rope's hook; `full` heaped with ore
def kibble():
    return item("Kibble", "tool", "a mine's kibble: a coopered bucket swelling at the belly, three iron hoops, iron straps up its sides to the ears, the bail with its eye for the rope's hook -- heaped with ore when `full`",
        {"full": 0},
        {"wood": {"pick": ["oak", "oak-grey"]}, "iron": "iron", "ore": {"pick": ["stone", "granite-black", "granite-red"]}}, [
            lathe("staves", "wood", [[0, 0], [0.2, 0], [0.222, 0.02], [0.25, 0.2], [0.246, 0.34], [0.232, 0.46], [0.214, 0.46], [0.226, 0.34], [0.23, 0.2], [0.2, 0.04], [0, 0.04]], sides=16, faceted=True),
            band("hoops", "iron", 0.225, 0.035, 0.006, [[0, 0.04, 0], [0, 0.425, 0]]),
            band("belly", "iron", 0.25, 0.04, 0.006, [0, 0.22, 0]),
            box("straps", "iron", [0.04, 0.24, 0.012], [[0, 0.36, 0.244, 0, -4, 0], [0, 0.36, -0.244, 0, 4, 0]]),
            ring("ears", "iron", 0.022, 0.008, [[0, 0.48, 0.24, 90, 90, 0], [0, 0.48, -0.24, 90, 90, 0]]),
            sweep("bail", "iron", [[0, 0.49, -0.24], [0, 0.66, -0.2], [0, 0.76, -0.06], [0, 0.77, 0], [0, 0.76, 0.06], [0, 0.66, 0.2], [0, 0.49, 0.24]], r=0.012, sides=6),
            ring("eye", "iron", 0.03, 0.009, [0, 0.8, 0, 90, 90, 0]),
            lathe("ore", "ore", [[0.222, 0.42], [0.17, 0.47], [0.09, 0.51], [0, 0.52]], sides=9, faceted=True, when="full"),
        ], era="1300-1900")


CRAFTS.update({
    "tools/fiddle": fiddle(), "tools/recorder": recorder(), "tools/flute": flute(), "tools/harp": harp(),
    "tableware/plate": plate_item(), "tableware/cauldron": cauldron(),
    "furniture/anvil": anvil(), "furniture/bellows": bellows(), "furniture/floor-loom": floor_loom(),
    "furniture/workbench": workbench(), "furniture/sawhorse": sawhorse(), "furniture/kick-wheel": kick_wheel(),
    "furniture/chopping-block": chopping_block(), "furniture/dress-form": dress_form(),
    "tools/shears": shears(), "tools/oven-peel": oven_peel(),
    "tools/frog-lamp": frog_lamp(), "furniture/windlass": windlass(), "tools/kibble": kibble(),
})


def write(path, doc):
    full = os.path.join(ITEMS, path + ".json")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        json.dump(r3(doc), f, indent=1, ensure_ascii=False)
        f.write("\n")


def main():
    for k, v in CRAFTS.items(): write(k, v)
    ipath = os.path.join(ROOT, "assets", "index.json")
    lock = open(ipath + ".lock", "w"); fcntl.flock(lock, fcntl.LOCK_EX)   # (other generators write the catalogue too)
    index = json.load(open(ipath))
    cats = {c["name"]: c for c in index["categories"]}
    where = {"tools": "Items: tools", "furniture": "Items: furniture", "tableware": "Items: tools"}
    added = []
    for k in CRAFTS:
        c = cats[where[k.split("/")[0]]]["paths"]
        if "items/" + k not in c: c.append("items/" + k); added.append(k)
    if added:
        with open(ipath, "w") as f: f.write(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
        print("registered", added)
    fcntl.flock(lock, fcntl.LOCK_UN)
    print(len(CRAFTS), "crafts:", ", ".join(f"{k} {len(v['parts'])}" for k, v in CRAFTS.items()))


if __name__ == "__main__":
    main()
