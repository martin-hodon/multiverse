"""THE STREET'S FURNITURE (2026-11-20; docs/modern.md): what stands on a modern pavement -- traffic lights, road signs,
street lamps, a bus stop and its shelter, bollards, a crash barrier, a guard rail, a hydrant, a post box, a litter bin,
a bench, a telephone box, a parking meter. Each in the frame of a thing that stands (kit.py): the origin on the ground
under its middle, +x its FRONT (the face a sign shows the traffic, a bench's seat), y up, z across -- so a bench, a
shelter, a barrier run along z and face +x.

Four shared components are written here (modern/components/):
  - `pole`: a round steel pole on its flange or straight out of the ground, capped -- every sign's, a signal's, a
    meter's;
  - `sign-face`: a road sign's face by its `sign` param (stop, give-way, speed, no-entry, crossing, parking, direction,
    bus-stop), each a stack of thin coloured plates over an aluminium back -- its own frame: the face in the xy plane,
    looking along +z, centred at the origin (turned by yaw 90 it looks along +x, its x running to the viewer's right);
  - `signal-head`: a traffic signal's head, three aspects for the traffic or two for the pedestrian, lit by `phase`;
  - `kiosk-sign`: the telephone box's fascia with TELEPHONE on it, one side's, placed on all four.

LETTERING: the signs' words and numbers are written in STROKES (`text3`): each letter a few straight or curved
centre-lines (GLYPHS, in em units), each drawn as a flat ribbon (a sweep with a rectangular section) laid on any plane
-- a sign's face, a phone box's fascia, a shelter's roof edge."""
import math
from kit import item, box, rod, lathe, sphere, ring, sweep, plate, use, write, hinge, each, merge, fill, panes, bars

C = "modern/components/"

# ---- LETTERING -------------------------------------------------------------------------------------------------------
def _ell(cx, cy, rx, ry, n=14):
    return [[cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)] for i in range(n)]

_P = [[0.06, 1], [0.34, 1], [0.5, 0.88], [0.5, 0.64], [0.34, 0.5], [0.06, 0.5]]
_C = [[0.53, 0.86], [0.4, 0.98], [0.22, 0.98], [0.07, 0.8], [0.04, 0.5], [0.07, 0.2], [0.22, 0.02], [0.4, 0.02], [0.53, 0.14]]
_6 = [[0.5, 0.9], [0.32, 1.0], [0.12, 0.85], [0.05, 0.5], [0.08, 0.18], [0.28, 0.0], [0.47, 0.1], [0.52, 0.32], [0.4, 0.55], [0.2, 0.56], [0.06, 0.42]]
# (each glyph: its advance in em and its strokes -- a list of points, or ("loop", points) for a closed one)
GLYPHS = {
    " ": (0.3, []),
    "A": (0.62, [[[0.02, 0], [0.31, 1]], [[0.31, 1], [0.6, 0]], [[0.13, 0.33], [0.49, 0.33]]]),
    "B": (0.56, [[[0.06, 0], [0.06, 1]], [[0.06, 1], [0.36, 1], [0.5, 0.9], [0.5, 0.64], [0.36, 0.53], [0.06, 0.53]],
                 [[0.06, 0.53], [0.38, 0.53], [0.53, 0.4], [0.53, 0.13], [0.38, 0.0], [0.06, 0]]]),
    "C": (0.56, [_C]),
    "D": (0.58, [[[0.06, 0], [0.06, 1]], [[0.06, 1], [0.3, 1], [0.5, 0.85], [0.55, 0.5], [0.5, 0.15], [0.3, 0], [0.06, 0]]]),
    "E": (0.5, [[[0.06, 0], [0.06, 1]], [[0.06, 1], [0.48, 1]], [[0.06, 0.52], [0.42, 0.52]], [[0.06, 0], [0.48, 0]]]),
    "F": (0.48, [[[0.06, 0], [0.06, 1]], [[0.06, 1], [0.48, 1]], [[0.06, 0.52], [0.42, 0.52]]]),
    "G": (0.6, [_C[:-1] + [[0.56, 0.15], [0.56, 0.45]], [[0.56, 0.45], [0.34, 0.45]]]),
    "H": (0.58, [[[0.06, 0], [0.06, 1]], [[0.52, 0], [0.52, 1]], [[0.06, 0.52], [0.52, 0.52]]]),
    "I": (0.2, [[[0.1, 0], [0.1, 1]]]),
    "K": (0.56, [[[0.06, 0], [0.06, 1]], [[0.54, 1], [0.06, 0.4]], [[0.22, 0.58], [0.54, 0]]]),
    "L": (0.48, [[[0.06, 1], [0.06, 0]], [[0.06, 0], [0.46, 0]]]),
    "M": (0.72, [[[0.06, 0], [0.06, 1]], [[0.06, 1], [0.36, 0.35]], [[0.36, 0.35], [0.66, 1]], [[0.66, 1], [0.66, 0]]]),
    "N": (0.6, [[[0.06, 0], [0.06, 1]], [[0.06, 1], [0.54, 0]], [[0.54, 0], [0.54, 1]]]),
    "O": (0.66, [("loop", _ell(0.33, 0.5, 0.28, 0.49))]),
    "P": (0.54, [[[0.06, 0], [0.06, 1]], _P]),
    "R": (0.56, [[[0.06, 0], [0.06, 1]], _P, [[0.3, 0.5], [0.54, 0]]]),
    "S": (0.54, [[[0.5, 0.86], [0.38, 0.98], [0.17, 0.98], [0.05, 0.84], [0.08, 0.64], [0.27, 0.53], [0.46, 0.42], [0.5, 0.2], [0.38, 0.03], [0.16, 0.02], [0.03, 0.14]]]),
    "T": (0.56, [[[0.0, 1], [0.56, 1]], [[0.28, 1], [0.28, 0]]]),
    "U": (0.58, [[[0.06, 1], [0.06, 0.3], [0.13, 0.07], [0.29, 0.0], [0.45, 0.07], [0.52, 0.3], [0.52, 1]]]),
    "V": (0.6, [[[0.02, 1], [0.3, 0]], [[0.3, 0], [0.58, 1]]]),
    "W": (0.82, [[[0.02, 1], [0.21, 0]], [[0.21, 0], [0.41, 0.7]], [[0.41, 0.7], [0.61, 0]], [[0.61, 0], [0.8, 1]]]),
    "X": (0.58, [[[0.03, 0], [0.55, 1]], [[0.03, 1], [0.55, 0]]]),
    "Y": (0.6, [[[0.02, 1], [0.3, 0.5]], [[0.58, 1], [0.3, 0.5]], [[0.3, 0.5], [0.3, 0]]]),
    "0": (0.56, [("loop", _ell(0.28, 0.5, 0.23, 0.49))]),
    "1": (0.4, [[[0.08, 0.8], [0.27, 1]], [[0.27, 1], [0.27, 0]]]),
    "2": (0.56, [[[0.05, 0.8], [0.18, 0.97], [0.38, 0.98], [0.52, 0.8], [0.45, 0.55], [0.05, 0.0]], [[0.05, 0], [0.54, 0]]]),
    "3": (0.56, [[[0.05, 0.88], [0.28, 1], [0.5, 0.86], [0.45, 0.62], [0.24, 0.54]], [[0.24, 0.54], [0.5, 0.44], [0.53, 0.18], [0.3, 0], [0.04, 0.12]]]),
    "4": (0.58, [[[0.44, 0], [0.44, 1]], [[0.44, 1], [0.02, 0.3]], [[0.02, 0.3], [0.58, 0.3]]]),
    "5": (0.56, [[[0.52, 1], [0.1, 1]], [[0.1, 1], [0.07, 0.55]], [[0.07, 0.55], [0.3, 0.63], [0.52, 0.42], [0.48, 0.12], [0.27, 0], [0.04, 0.1]]]),
    "6": (0.56, [_6]),
    "7": (0.56, [[[0.03, 1], [0.55, 1]], [[0.55, 1], [0.18, 0]]]),
    "8": (0.56, [("loop", _ell(0.28, 0.76, 0.19, 0.23)), ("loop", _ell(0.28, 0.27, 0.24, 0.27))]),
    "9": (0.56, [[[0.56 - x, 1 - y] for x, y in _6]]),
}


def text_width(s, gap=0.14):
    return sum(GLYPHS[c][0] for c in s) + gap * (len(s) - 1)


def text3(idp, mat, s, h, origin, right=(1, 0, 0), up=(0, 1, 0), normal=(0, 0, 1), weight=0.15, depth=0.003, align="center", gap=0.14, **k):
    """`s` written `h` high on any plane: `origin` the line's middle (align center) or its start (left), at mid-height;
    `right` and `up` the plane's directions, `normal` out of it (the strokes stand `depth` off it). Each stroke a flat
    ribbon -- a sweep of a rectangular section `weight` em wide"""
    x = -text_width(s, gap) / 2 if align == "center" else 0
    out = []
    P = lambda u, v: [origin[i] + right[i] * u * h + up[i] * (v - 0.5) * h + normal[i] * depth / 2 for i in range(3)]
    for ci, c in enumerate(s):
        w, strokes = GLYPHS[c]
        for si, st in enumerate(strokes):
            closed = isinstance(st, tuple)
            pts = st[1] if closed else st
            if len(pts) == 2:   # (a straight stroke runs on half its width at both ends, so its corners meet square)
                (ax, ay), (bx, by) = pts
                L = math.hypot(bx - ax, by - ay) or 1
                ex, ey = (bx - ax) / L * weight / 2, (by - ay) / L * weight / 2
                pts = [[ax - ex, ay - ey], [bx + ex, by + ey]]
            out.append(sweep(f"{idp}{ci}_{si}", mat, [P(x + px, py) for px, py in pts], None, section=[weight * h, depth],
                             up=list(normal), closed=closed, seg=3 if len(pts) > 2 else 2, **k))
        x += w + gap
    return out


# (a person in strokes, `h` tall, its feet at `origin`: standing, or walking toward the plane's right)
FIGURES = {
    "stand": ((0, 0.9, 0.1), [[[0, 0.77], [0, 0.42]], [[0, 0.44], [-0.09, 0]], [[0, 0.44], [0.09, 0]], [[0, 0.74], [-0.14, 0.42]], [[0, 0.74], [0.14, 0.42]]]),
    "walk": ((0.06, 0.9, 0.1), [[[0.04, 0.77], [-0.02, 0.44]], [[-0.02, 0.44], [0.13, 0.22], [0.23, 0.0]], [[-0.02, 0.44], [-0.12, 0.22], [-0.26, 0.06]],
                                [[0.03, 0.73], [0.16, 0.55], [0.22, 0.42]], [[0.03, 0.73], [-0.12, 0.57], [-0.2, 0.44]]]),
}


def figure3(idp, mat, kind, h, origin, right=(1, 0, 0), up=(0, 1, 0), normal=(0, 0, 1), weight=0.11, depth=0.003, **k):
    (hx, hy, hr), strokes = FIGURES[kind]
    P = lambda u, v, d=depth / 2: [origin[i] + right[i] * u * h + up[i] * v * h + normal[i] * d for i in range(3)]
    out = [rod(idp + "head", mat, hr * h, P(hx, hy, 0), P(hx, hy, depth), 12, **k)]
    for si, st in enumerate(strokes):
        out.append(sweep(f"{idp}{si}", mat, [P(u, v) for u, v in st], None, section=[weight * h, depth], up=list(normal), seg=3, **k))
    return out


# ---- SHAPES ----------------------------------------------------------------------------------------------------------
def ngon(R, n, rot=0):
    return [[R * math.cos(math.radians(rot + 360 * i / n)), R * math.sin(math.radians(rot + 360 * i / n))] for i in range(n)]


def rrect(w, h, r, n=4, cx=0, cy=0):
    """a rounded rectangle's outline, w x h, corners of radius r"""
    out = []
    for qx, qy, a0 in [(1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)]:
        ox, oy = cx + qx * (w / 2 - r), cy + qy * (h / 2 - r)
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            out.append([ox + r * math.cos(a), oy + r * math.sin(a)])
    return out


def scaled(pts, s, dx=0, dy=0):
    return [[x * s + dx, y * s + dy] for x, y in pts]


L0 = 0.003   # (one layer of a sign's face: each plate this thick, stacked in front of the last)


def layer(id_, mat, pts, k, **kw):
    """the k-th coloured layer of a sign's face (0 on the aluminium back), its front at L0 * (k + 1)"""
    return plate(id_, mat, pts, L0, [0, 0, L0 * (k + 0.5)], **kw)


def words(idp, mat, s, h, x, y, k, **kw):
    """lettering on a sign's face, on top of layer k-1, centred at (x, y)"""
    return text3(idp, mat, s, h, [x, y, L0 * k], depth=L0, **kw)


# ---- THE COMPONENTS --------------------------------------------------------------------------------------------------
def pole():
    # A STREET POLE: a steel tube `h` tall and `r` round, standing on a bolted flange (`base` flange) or straight out of
    # the pavement (`base` none), capped -- a sign's, a signal's, a meter's, a bus stop's
    return item("Pole", "components", "a round steel pole standing on the pavement: the tube, its cap, a bolted base flange if asked -- h tall, r round, its foot at the origin",
        {"pole": "steel", "cap": "plastic-black"}, [
            lathe("tube", "pole", [["r", 0], ["r", "h"]], [0, 0, 0], caps=False, sides=14),
            lathe("cap", "cap", [["r * 1.08", "h - 0.01"], ["r * 1.08", "h + 0.01"], ["r * 0.6", "h + r * 0.45"], [0, "h + r * 0.5"]], [0, 0, 0], sides=14, when="cap"),
            lathe("flange", "pole", [["r * 2.6", 0], ["r * 2.6", 0.014], ["r * 1.1", 0.03], ["r", 0.06]], [0, 0, 0], sides=16, when={"base": "flange"}),
            sphere("bolt", "pole", 0.01, [0, 0.016, 0], around={"n": 4, "r": "r * 2.1", "plane": "xz", "start": 45}, sides=6, when={"base": "flange"}),
            lathe("collar", "pole", [["r * 1.25", 0], ["r * 1.25", 0.012], ["r", 0.02]], [0, 0, 0], sides=14, when={"base": "none"}),
        ], params={"h": 2.9, "r": 0.038, "base": "none", "cap": 1})


SIGN_COLOURS = {"white": "#f2f2ee", "red": "#c4161c", "blue": "#1b4e9b", "green": "#0b6b3a", "black": "#16171a",
                "yellow": "#f2c200", "back": "aluminium"}


def sign_face():
    # A ROAD SIGN'S FACE by `sign` -- each the sizes of the British and Continental standards (the Vienna convention):
    # stop (an octagon 750 across, white STOP on red), give-way (a triangle point down, 900 a side), speed (a red ring
    # 600 across round black numbers: `limit` 20/30/50/70), no-entry (a red disc, a white bar), crossing (a blue square,
    # the walking figure on a zebra in a white triangle), parking (a blue square, a white P), direction (a green board
    # 1.4 x 0.7, an arrow and two places), bus-stop (a yellow disc ringed green, a green H). The face looks along +z.
    W = lambda k: "w"   # (role names: the colours are roles, so a parent may repaint)
    oct8 = ngon(0.406, 8, 22.5)
    tri = [[-0.45, 0.26], [0.45, 0.26], [0, -0.52]]
    sq = rrect(0.6, 0.6, 0.04)
    d = rrect(1.4, 0.7, 0.05)
    tri_up = [[-0.25, -0.19], [0.25, -0.19], [0, 0.243]]
    arrow = [[-0.025, -0.22], [0.025, -0.22], [0.025, 0.05], [0.08, 0.05], [0, 0.2], [-0.08, 0.05], [-0.025, 0.05]]
    parts = []
    S = lambda name: {"sign": name}
    # stop
    parts += [plate("backStop", "back", oct8, L0, [0, 0, -L0 / 2], when=S("stop")),
              layer("wStop", "white", oct8, 0, when=S("stop")), layer("rStop", "red", ngon(0.384, 8, 22.5), 1, when=S("stop")),
              *words("stop", "white", "STOP", 0.16, 0, 0, 2, weight=0.17, when=S("stop"))]
    # give way
    parts += [plate("backGive", "back", tri, L0, [0, 0, -L0 / 2], when=S("give-way")),
              layer("wGive", "white", tri, 0, when=S("give-way")), layer("rGive", "red", scaled(tri, 0.95), 1, when=S("give-way")),
              layer("iGive", "white", scaled(tri, 0.62), 2, when=S("give-way"))]
    # speed limit
    sp = S("speed")
    parts += [plate("backSpeed", "back", ngon(0.3, 40), L0, [0, 0, -L0 / 2], when=sp),
              layer("wSpeed", "white", ngon(0.3, 40), 0, when=sp), layer("rSpeed", "red", ngon(0.29, 40), 1, when=sp),
              layer("iSpeed", "white", ngon(0.22, 40), 2, when=sp)]
    for lim in (20, 30, 50, 70):
        parts += words(f"lim{lim}_", "black", str(lim), 0.2, 0, 0, 3, weight=0.16, when={"sign": "speed", "limit": lim})
    # no entry
    ne = S("no-entry")
    parts += [plate("backNo", "back", ngon(0.3, 40), L0, [0, 0, -L0 / 2], when=ne),
              layer("wNo", "white", ngon(0.3, 40), 0, when=ne), layer("rNo", "red", ngon(0.29, 40), 1, when=ne),
              layer("barNo", "white", rrect(0.42, 0.09, 0.01), 2, when=ne)]
    # pedestrian crossing
    cr = S("crossing")
    parts += [plate("backCross", "back", sq, L0, [0, 0, -L0 / 2], when=cr),
              layer("wCross", "white", sq, 0, when=cr), layer("bCross", "blue", rrect(0.57, 0.57, 0.03), 1, when=cr),
              layer("tCross", "white", tri_up, 2, when=cr),
              *[layer(f"zebra{i}", "black", rrect(0.05, 0.022, 0.003, 1, -0.12 + 0.08 * i, -0.165), 3, when=cr) for i in range(4)],
              *figure3("walker", "black", "walk", 0.24, [0, -0.15, L0 * 3], depth=L0, when=cr)]
    # parking
    pk = S("parking")
    parts += [plate("backPark", "back", sq, L0, [0, 0, -L0 / 2], when=pk),
              layer("wPark", "white", sq, 0, when=pk), layer("bPark", "blue", rrect(0.57, 0.57, 0.03), 1, when=pk),
              *words("park", "white", "P", 0.4, 0, 0, 2, weight=0.18, when=pk)]
    # direction
    dr = S("direction")
    parts += [plate("backDir", "back", d, L0, [0, 0, -L0 / 2], when=dr),
              layer("wDir", "white", d, 0, when=dr), layer("gDir", "green", rrect(1.36, 0.66, 0.035), 1, when=dr),
              layer("arrow", "white", scaled(arrow, 1.1, -0.5, 0), 2, when=dr),
              *words("dirA", "white", "CENTRE", 0.11, -0.3, 0.13, 2, weight=0.15, align="left", when=dr),
              *words("dirB", "white", "STATION", 0.11, -0.3, -0.13, 2, weight=0.15, align="left", when=dr)]
    # bus stop (a flag on its pole, read from both ways: the parent hangs two back to back)
    bs = S("bus-stop")
    parts += [plate("backBus", "back", ngon(0.225, 36), L0, [0, 0, -L0 / 2], when=bs),
              layer("gBus", "green", ngon(0.225, 36), 0, when=bs), layer("yBus", "yellow", ngon(0.19, 36), 1, when=bs),
              *words("bus", "green", "H", 0.2, 0, 0, 2, weight=0.18, when=bs)]
    return item("Sign face", "components",
        "a road sign's face, picked by `sign`: stop, give-way, speed (`limit`), no-entry, crossing, parking, direction, bus-stop -- thin coloured plates stacked on an aluminium back, the lettering in strokes; the face looks along +z, centred at the origin",
        dict(SIGN_COLOURS), parts, params={"sign": "stop", "limit": 30})


def signal_head():
    # A TRAFFIC SIGNAL'S HEAD, looking along +x, its back's middle at the origin: `kind` vehicle (three aspects of
    # 200 mm in a housing 0.3 x 0.9, hooded, on a black backboard with a white border) or ped (two 200 mm squares:
    # the red man standing, the green man walking). `phase`: red, redamber, green, amber -- which lamps are lit (the
    # pedestrian's green man shows while the traffic has red).
    V, Pd = {"kind": "vehicle"}, {"kind": "ped"}
    parts = [box("housing", "body", [0.22, 0.9, 0.3], [0.11, 0, 0], round=0.02, when=V)]
    plate_yz = lambda id_, mat, pts, x, t, **k: plate(id_, mat, pts, t, [x, 0, 0, 90, 0, 0], **k)
    parts += [plate_yz("board", "board", rrect(0.56, 1.18, 0.06), -0.005, 0.01, when=V),
              plate_yz("border", "border", rrect(0.6, 1.22, 0.07), -0.012, 0.006, when=V)]
    for name, y, lit, dim, on in [("red", 0.3, "lamp-red", "#4a1714", ["red", "redamber"]), ("amber", 0, "lamp-amber", "#4d3a12", ["amber", "redamber"]),
                                   ("green", -0.3, "lamp-green", "#133d26", ["green"])]:
        off = [p for p in ["red", "redamber", "green", "amber"] if p not in on]
        parts += [rod(name + "On", lit, 0.1, [0.215, y, 0], [0.226, y, 0], 20, when={"kind": "vehicle", "phase": on}),
                  rod(name + "Off", dim, 0.1, [0.215, y, 0], [0.226, y, 0], 20, when={"kind": "vehicle", "phase": off}),
                  ring(name + "Rim", "body", 0.105, 0.008, [0.222, y, 0, 0, 0, 90], when=V),
                  sweep(name + "Hood", "body", [[0.31, y + 0.118 * math.sin(math.radians(a)), 0.118 * math.cos(math.radians(a))] for a in range(-15, 196, 15)],
                        None, section=[0.006, 0.18], up=[1, 0, 0], seg=2, when=V)]
    # (the pedestrian's: a squarer housing, two black lenses, the red man above, the green man below)
    parts += [box("pedBody", "body", [0.2, 0.56, 0.3], [0.1, 0, 0], round=0.02, when=Pd),
              box("pedLens", "lens", [0.01, 0.24, 0.24], [[0.202, 0.135, 0], [0.202, -0.135, 0]], when=Pd),
              box("pedHood", "body", [0.12, 0.012, 0.3], [[0.25, 0.27, 0], [0.25, 0.0, 0]], when=Pd)]
    R, F, N = (0, 0, -1), (0, 1, 0), (1, 0, 0)   # (the plane of the lenses: right is -z seen from the front)
    parts += figure3("man", "lamp-red", "stand", 0.19, [0.207, 0.04, 0], R, F, N, weight=0.13, depth=0.004, when={"kind": "ped", "phase": ["green", "amber", "redamber"]})
    parts += figure3("manOff", "#3a1512", "stand", 0.19, [0.207, 0.04, 0], R, F, N, weight=0.13, depth=0.004, when={"kind": "ped", "phase": ["red"]})
    parts += figure3("walk", "lamp-green", "walk", 0.19, [0.207, -0.23, 0], R, F, N, weight=0.13, depth=0.004, when={"kind": "ped", "phase": ["red"]})
    parts += figure3("walkOff", "#11331f", "walk", 0.19, [0.207, -0.23, 0], R, F, N, weight=0.13, depth=0.004, when={"kind": "ped", "phase": ["green", "amber", "redamber"]})
    return item("Signal head", "components",
        "a traffic signal's head looking along +x: three hooded 200 mm aspects on a black backboard with a white border (`kind` vehicle), or the pedestrian's two squares, the red man and the green man (ped); `phase` red, redamber, green or amber lights them",
        {"body": "plastic-black", "board": "#141414", "border": "#efefef", "lens": "#0c0c0c"}, parts, params={"kind": "vehicle", "phase": "red"})


# ---- TRAFFIC LIGHTS ----------------------------------------------------------------------------------------------------
def push_button(at_y, face_z=1):
    # (the pedestrian's push-button box, yellow, a WAIT lamp, on the pole looking along +z)
    z = 0.07 * face_z
    return [box("pushBox", "push", [0.11, 0.24, 0.07], [0, at_y, z], round=0.012),
            box("pushStrap", "pole", [0.12, 0.03, 0.12], [[0, at_y + 0.08, 0.02], [0, at_y - 0.08, 0.02]]),
            box("waitLamp", "#2a2a2a", [0.07, 0.04, 0.004], [0, at_y + 0.06, z + 0.036]),
            *text3("wait", "lamp-amber", "WAIT", 0.022, [0, at_y + 0.06, z + 0.038], weight=0.16, depth=0.002),
            rod("button", "#d8d8d8", 0.017, [0, at_y - 0.03, z + 0.034], [0, at_y - 0.03, z + 0.042], 12)]


def traffic_light():
    # A TRAFFIC LIGHT on its pole at a crossing: the three-aspect head for the traffic (+x) at 2.5-3.4 m, the
    # pedestrian's head lower on the same pole looking across the road (+z), the push-button box at hand height.
    # A 114 mm grey pole, 4 m. `phase` drawn by the seed.
    return item("Traffic light", "street",
        "a traffic light at a pedestrian crossing: a 4 m grey pole, the three-aspect head (red, amber, green, 200 mm lenses, hooded, on a black backboard with a white border) facing the traffic at +x, the pedestrian's red and green man facing across the road (+z) at 2.2 m, a yellow push-button box with its WAIT lamp at 1.1 m. `phase` red, redamber, green or amber -- the green man shows on red.",
        {"pole": "paint-grey", "push": "paint-yellow", "cap": "plastic-black"}, [
            use("pole", C + "pole", [0, 0, 0], {"h": 3.55, "r": 0.057, "base": "none"}),
            use("head", C + "signal-head", [0.075, 2.98, 0], {"kind": "vehicle", "phase": "phase"}),
            box("bracket", "pole", [0.09, 0.05, 0.08], [[0.03, 3.3, 0], [0.03, 2.66, 0]]),
            use("ped", C + "signal-head", [0, 2.22, 0.075, -90, 0, 0], {"kind": "ped", "phase": "phase"}),
            box("pedBracket", "pole", [0.08, 0.05, 0.09], [[0, 2.42, 0.03], [0, 2.02, 0.03]]),
            *push_button(1.1),
        ], params={"phase": {"pick": ["red", "green", "amber", "redamber", "red", "green"]}})


def pedestrian_light():
    # A PEDESTRIAN SIGNAL on its own pole (the far side of a crossing): the red man and the green man facing +x at
    # 2.2 m, a push button below. A 3 m pole.
    return item("Pedestrian light", "street",
        "a pedestrian signal on its own 3 m pole at the far side of a crossing: the red man standing and the green man walking, 200 mm squares, hooded, facing +x at 2.2 m; a yellow push-button box at 1.1 m. `phase` as the traffic's: the green man shows on red.",
        {"pole": "paint-grey", "push": "paint-yellow", "cap": "plastic-black"}, [
            use("pole", C + "pole", [0, 0, 0], {"h": 2.85, "r": 0.057, "base": "none"}),
            use("ped", C + "signal-head", [0.075, 2.25, 0], {"kind": "ped", "phase": "phase"}),
            box("bracket", "pole", [0.09, 0.05, 0.08], [[0.03, 2.45, 0], [0.03, 2.05, 0]]),
            *push_button(1.1),
        ], params={"phase": {"pick": ["red", "green"]}})


# ---- ROAD SIGNS --------------------------------------------------------------------------------------------------------
SIGNS = ["stop", "give-way", "speed", "no-entry", "crossing", "parking"]


def road_sign(sign=None, limit=None):
    # A ROAD SIGN ON ITS POST: a 76 mm galvanised post 2.9 m tall, the face (sign-face) clamped to its front by two
    # bands, its middle at 2.45 m (its foot about 2.1 m up, the clear height over a footway). `sign` picks the face.
    params = {"sign": sign or {"pick": SIGNS}, "limit": limit or {"pick": [20, 30, 30, 50, 50, 70]}}
    return item("Road sign" if not sign else "Road sign: " + sign.replace("-", " ") + (f" {limit}" if limit else ""), "street",
        "a road sign on its galvanised post (76 mm, 2.9 m): the face clamped by two bands to the post's front, its middle at 2.45 m -- `sign` stop (an octagon 750 across), give-way (a triangle 900 a side), speed (a 600 red ring, `limit`), no-entry, crossing (the walking figure in a white triangle on blue), parking (a blue square, a white P). The face looks along +x.",
        {"pole": "steel", "cap": "plastic-black"}, [
            use("post", C + "pole", [0, 0, 0], {"h": 2.9, "r": 0.038, "base": "none"}),
            use("face", C + "sign-face", [0.055, 2.45, 0, 90, 0, 0], {"sign": "sign", "limit": "limit"}),
            ring("band", "pole", 0.04, 0.006, [[0, 2.27, 0], [0, 2.63, 0]], sides=6),
            box("clip", "pole", [0.03, 0.035, 0.05], [[0.04, 2.27, 0], [0.04, 2.63, 0]]),
        ], params=params)


def direction_sign():
    # A DIRECTION SIGN on two posts: a green board 1.4 x 0.7 with a white border, an arrow ahead and two places
    # (CENTRE, STATION), clamped to two 76 mm posts 0.9 apart, its middle at 2.5 m.
    return item("Direction sign", "street",
        "a direction sign on two galvanised posts: a green board 1.4 x 0.7 m with a white border, a white arrow ahead and two destinations in white capitals, clamped by rails to two 76 mm posts 0.9 m apart, its middle 2.5 m up. It looks along +x.",
        {"pole": "steel", "cap": "plastic-black"}, [
            use("post", C + "pole", [[0, 0, -0.45], [0, 0, 0.45]], {"h": 2.88, "r": 0.038, "base": "none"}),
            use("face", C + "sign-face", [0.06, 2.5, 0, 90, 0, 0], {"sign": "direction"}),
            box("rail", "pole", [0.025, 0.04, 1.2], [[0.037, 2.3, 0], [0.037, 2.7, 0]]),
        ])


# ---- STREET LAMPS ------------------------------------------------------------------------------------------------------
def street_lamp():
    # A STREET LIGHT of the LED age: a tapered octagonal steel column 8 m tall, its base shroud and door, a curved
    # outreach arm 1.5 m over the road (+x), a flat luminaire tilted up 5 degrees, its lens underneath.
    H, O = 8.0, 1.5
    return item("Street lamp", "street",
        "a modern street light: a tapered octagonal galvanised column 8 m tall (168 mm at the foot, 90 at the top), its base shroud and inspection door, a curved outreach arm reaching 1.5 m over the road (+x), a flat LED luminaire 0.7 m long tilted up 5 degrees, its lens beneath.",
        {"column": "steel", "head": "paint-grey", "lens": "lamp", "door": "steel"}, [
            lathe("column", "column", [[0.084, 0], [0.045, H]], [0, 0, 0], caps=False, sides=8, faceted=True),
            lathe("shroud", "column", [[0.13, 0], [0.13, 0.05], [0.11, 0.08], [0.105, 0.6], [0.09, 0.66]], [0, 0, 0], sides=8, faceted=True),
            box("door", "door", [0.02, 0.32, 0.09], [0.1, 0.36, 0]),
            sweep("arm", "column", [[0, H - 0.4, 0], [0.02, H - 0.05, 0], [0.3, H + 0.22, 0], [0.9, H + 0.3, 0], [O, H + 0.32, 0]], 0.035, seg=5),
            box("luminaire", "head", [0.72, 0.09, 0.3], [O + 0.3, H + 0.34, 0, 0, 0, 5], round=0.035),
            box("lensBed", "lens", [0.5, 0.012, 0.22], [O + 0.33, H + 0.3, 0, 0, 0, 5], round=0.004),
        ])


def heritage_lamp():
    # A HERITAGE LANTERN COLUMN (the cast-iron Victorian pattern, still put up in old streets): a fluted base, a slim
    # shaft with its ladder bar, a four-sided lantern with a glowing lamp, a pyramid roof and a finial. 4.5 m.
    return item("Heritage street lamp", "street",
        "a cast-iron heritage lamp column of the Victorian pattern (still made for old streets): a broad moulded base, a slim shaft with the lamplighter's ladder bar, a four-sided lantern (its glass alight) under a pyramid roof and a finial; painted black, 4.5 m.",
        {"iron": {"pick": ["paint-black", "paint-black", "paint-green"]}, "glass": "lamp", "gilt": "gilt"}, [
            lathe("base", "iron", [[0.2, 0], [0.2, 0.06], [0.17, 0.09], [0.16, 0.5], [0.13, 0.62], [0.11, 0.7], [0.1, 0.9], [0.075, 1.02], [0.065, 1.1]], [0, 0, 0], sides=16),
            lathe("flutes", "iron", [[0.17, 0.12], [0.17, 0.48]], [0, 0, 0], sides=12, faceted=True),
            lathe("shaft", "iron", [[0.065, 1.1], [0.05, 3.6], [0.06, 3.65], [0.06, 3.7], [0.045, 3.75]], [0, 0, 0], sides=12),
            ring("collar", "gilt", 0.068, 0.012, [0, 1.15, 0]),
            rod("ladderBar", "iron", 0.014, [0, 3.45, -0.32], [0, 3.45, 0.32], 8),
            sphere("barEnd", "iron", 0.025, [0, 3.45, 0.32], mirror="z"),
            lathe("lanternBase", "iron", [[0.03, 3.74], [0.13, 3.8], [0.13, 3.83], [0.04, 3.83]], [0, 0, 0, 45, 0, 0], sides=4),
            lathe("glass", "glass", [[0.13, 3.83], [0.19, 4.22]], [0, 0, 0, 45, 0, 0], sides=4, faceted=True),
            rod("corner", "iron", 0.009, [0, 3.83, 0.13], [0, 4.22, 0.19], 5, around={"n": 4, "r": 0, "plane": "xz"}),
            lathe("roof", "iron", [[0.23, 4.22], [0.23, 4.25], [0.06, 4.42], [0.03, 4.44]], [0, 0, 0, 45, 0, 0], sides=4, faceted=True),
            lathe("finial", "iron", [[0.03, 4.44], [0.04, 4.47], [0.012, 4.52], [0.03, 4.56], [0, 4.62]], [0, 0, 0], sides=8),
        ])


# ---- THE BUS STOP ------------------------------------------------------------------------------------------------------
def bus_stop():
    # A BUS STOP: a glazed shelter 3.2 m long (along z) and 1.4 deep, its open front to the road (+x) -- a frame of
    # aluminium posts, three glass panels at the back, glass at one end and an advertising light box at the other, a
    # flat roof sloping back with a fascia, a perch bench along the back; and the stop's own pole beyond the shelter's
    # end with its flag (a yellow disc ringed green, H, both ways) and a timetable case.
    L, D, Hh = 3.2, 1.4, 2.45
    xb, xf = -D / 2, D / 2 - 0.1
    back = fill(-L / 2 + 0.035, L / 2 - 0.035, post=0.07, n=3)   # (the back's three panels between its four posts)
    parts = [
        *bars("post", "frame", "x", xb, back, 0, Hh, t=0.07, w=0.07, ends=True),
        box("postFront", "frame", [0.07, Hh, 0.07], [[xf, Hh / 2, -L / 2], [xf, Hh / 2, L / 2]]),
        *panes("backGlass", "glass", "x", xb, back, (0.15, 2.2), t=0.012),
        box("rail", "frame", [0.05, 0.05, L], [[xb, 0.13, 0], [xb, 2.22, 0]]),
        box("endGlass", "glass", [xf - xb - 0.07, 2.05, 0.012], [(xb + xf) / 2, 1.175, -L / 2]),
        box("endRail", "frame", [xf - xb, 0.05, 0.05], [[(xb + xf) / 2, 0.13, -L / 2], [(xb + xf) / 2, 2.22, -L / 2], [(xb + xf) / 2, 2.22, L / 2]]),
        # (the advertising light box at the right-hand end: its frame and its lit poster both sides)
        box("adBox", "frame", [1.25, 1.85, 0.14], [(xb + xf) / 2, 1.18, L / 2]),
        box("poster", "poster", [1.13, 1.73, 0.146], [(xb + xf) / 2, 1.18, L / 2]),
        # (the roof: a slab sloping back, its fascia at the front with the stop's name)
        box("roof", "frame", [D + 0.25, 0.06, L + 0.25], [0.0, Hh + 0.05, 0, 0, 0, -2]),
        box("fascia", "frame", [0.05, 0.2, L + 0.25], [D / 2 + 0.1, Hh, 0]),
        box("fasciaBand", "band", [0.006, 0.12, 1.4], [D / 2 + 0.127, Hh, 0]),
        *text3("fasciaT", "white", "BUS STOP", 0.08, [D / 2 + 0.13, Hh, 0], (0, 0, -1), (0, 1, 0), (1, 0, 0), weight=0.16, depth=0.003),
        # (the perch bench along the back on its brackets)
        box("bench", "bench", [0.32, 0.05, 2.0], [xb + 0.2, 0.5, 0], round=0.01),
        box("benchArm", "frame", [0.3, 0.04, 0.04], [[xb + 0.18, 0.46, z] for z in (-0.8, 0, 0.8)]),
        # (the stop's pole beyond the left end, its flag both ways, the timetable)
        use("stopPole", C + "pole", [xf + 0.15, 0, -L / 2 - 0.6], {"h": 2.95, "r": 0.045, "base": "none"}, {"pole": "frame", "cap": "frame"}),
        use("flag", C + "sign-face", [xf + 0.15, 2.65, -L / 2 - 0.6 + 0.05, 0, 0, 0], {"sign": "bus-stop"}),
        use("flagB", C + "sign-face", [xf + 0.15, 2.65, -L / 2 - 0.6 - 0.05, 180, 0, 0], {"sign": "bus-stop"}),
        box("flagClip", "frame", [0.05, 0.3, 0.1], [xf + 0.15, 2.65, -L / 2 - 0.6]),
        box("timetable", "frame", [0.06, 0.55, 0.4], [xf + 0.15 - 0.075, 1.5, -L / 2 - 0.6]),
        box("timetableSheet", "paper", [0.004, 0.47, 0.32], [xf + 0.15 - 0.106, 1.5, -L / 2 - 0.6]),
    ]
    return item("Bus stop", "street",
        "a bus stop: a glazed aluminium shelter 3.2 m long, 1.4 deep and 2.5 high, open to the road at +x -- three glass panels at the back, glass at one end, a lit advertising box at the other, a flat roof sloping back with its BUS STOP fascia, a perch bench along the back; beyond its end the stop's pole with its flag (a yellow disc ringed green, an H, read both ways) and a timetable case.",
        {"frame": "aluminium", "glass": "glass-light", "poster": "lamp", "band": "#1b4e9b", "white": "#f2f2ee", "bench": "steel", "paper": "plastic-white",
         **{k: v for k, v in SIGN_COLOURS.items() if k != "white"}, "pole": "aluminium", "cap": "aluminium"}, parts)


# ---- BOLLARDS, BARRIERS, RAILS -----------------------------------------------------------------------------------------
def bollard():
    # A BOLLARD by `style`: steel (a stainless tube 0.9 m, 140 mm, a domed top, two reflective bands), cast (the black
    # cast-iron heritage bollard, a collar and a gilt band, 1 m) or concrete (a squat cylinder 0.7 m, 400 mm round).
    return item("Bollard", "street",
        "a bollard, `style`: steel (a stainless tube 0.9 m tall and 140 mm round, a domed cap, two white reflective bands), cast (a black cast-iron heritage bollard, 1 m, a moulded collar and a gilt band, a ball on top), or concrete (a squat chamfered cylinder 0.7 m, 400 mm round).",
        {"steel": "chrome", "band": "#e8e8e8", "iron": "paint-black", "gilt": "gilt", "concrete": "concrete"}, [
            lathe("tube", "steel", [[0.07, 0], [0.07, 0.86], [0.055, 0.89], [0.03, 0.905], [0, 0.91]], [0, 0, 0], sides=18, when={"style": "steel"}),
            lathe("band", "band", [[0.0715, 0.7], [0.0715, 0.74]], [[0, 0, 0], [0, -0.1, 0]], caps=False, sides=18, when={"style": "steel"}),
            lathe("cast", "iron", [[0.15, 0], [0.15, 0.04], [0.12, 0.08], [0.1, 0.12], [0.085, 0.7], [0.11, 0.74], [0.11, 0.8], [0.09, 0.84], [0.08, 0.88],
                                   [0.075, 0.92], [0.06, 0.95]], [0, 0, 0], sides=16, when={"style": "cast"}),
            sphere("ball", "iron", 0.07, [0, 0.99, 0], sides=14, when={"style": "cast"}),
            lathe("castBand", "gilt", [[0.112, 0.755], [0.112, 0.785]], [0, 0, 0], caps=False, sides=16, when={"style": "cast"}),
            lathe("block", "concrete", [[0.2, 0], [0.2, 0.62], [0.17, 0.68], [0, 0.69]], [0, 0, 0], sides=20, when={"style": "concrete"}),
        ], params={"style": {"pick": ["steel", "cast", "concrete"]}})


def crash_barrier():
    # A CRASH BARRIER segment (the W-beam guardrail of motorways and country roads): a 4 m steel W-beam (310 mm high,
    # 85 deep) its middle 0.6 m up, bolted through spacer blocks to two sigma posts 2 m apart. It runs along z and
    # faces the traffic at +x.
    import math as m
    ys = [-0.155 + 0.31 * i / 24 for i in range(25)]
    d = lambda y: 0.045 - 0.04 * m.cos(2 * m.pi * y / 0.16)
    t = 0.0035
    prof = [[d(y) + t, y] for y in ys] + [[d(y) - t, y] for y in reversed(ys)]
    return item("Crash barrier", "street",
        "a 4 m segment of W-beam crash barrier (motorways, country roads): the galvanised beam 310 mm high and 85 deep, its middle 0.6 m up, bolted through spacer blocks to two sigma posts 2 m apart; it runs along z, facing the traffic at +x. Lay them end to end every 4 m.",
        {"steel": "steel", "bolt": "steel"}, [
            plate("beam", "steel", prof, 4.0, [0.0, 0.6, 0]),
            box("spacer", "steel", [0.15, 0.3, 0.06], [[-0.075, 0.58, -1.0], [-0.075, 0.58, 1.0]]),
            box("post", "steel", [0.1, 0.75, 0.055], [[-0.2, 0.375, -1.0], [-0.2, 0.375, 1.0]]),
            box("postFlange", "steel", [0.012, 0.75, 0.1], [[-0.15, 0.375, -1.0], [-0.25, 0.375, -1.0], [-0.15, 0.375, 1.0], [-0.25, 0.375, 1.0]]),
            sphere("bolt", "bolt", 0.012, [[0.012, 0.6, -1.0], [0.012, 0.6, 1.0]], stretch=[0.5, 1, 1], sides=8),
            sphere("splice", "bolt", 0.01, [[0.09, y, z] for y in (0.52, 0.68) for z in (-1.98, -1.88, 1.88, 1.98)], stretch=[0.5, 1, 1], sides=6),
        ])


def guard_rail():
    # A PEDESTRIAN GUARD RAIL panel (the kerbside railing at a crossing): 2 m of steel, 1 m high, a top and a bottom
    # rail, vertical bars, posts at each end set in the pavement. Runs along z, its road side at +x.
    return item("Pedestrian guard rail", "street",
        "a pedestrian guard rail panel at the kerb: 2 m long and 1 m high, a top rail and a bottom rail with 22 vertical bars between, a square post at each end set in the pavement; galvanised or painted. It runs along z; lay them end to end every 2 m.",
        {"rail": {"pick": ["steel", "steel", "paint-green", "paint-black"]}}, [
            box("post", "rail", [0.06, 1.05, 0.06], [[0, 0.525, -1.0], [0, 0.525, 1.0]]),
            sphere("postCap", "rail", 0.035, [[0, 1.05, -1.0], [0, 1.05, 1.0]], stretch=[1, 0.5, 1], sides=8),
            box("top", "rail", [0.05, 0.05, 2.0], [0, 0.98, 0]),
            box("bottom", "rail", [0.04, 0.04, 2.0], [0, 0.18, 0]),
            rod("bar", "rail", 0.009, [0, 0.18, 0], [0, 0.98, 0], 6, along={"n": 22, "from": [0, 0, -0.92], "to": [0, 0, 0.92]}),
        ])


# ---- HYDRANT, POST BOX, BIN, BENCH, PHONE BOX, METER -----------------------------------------------------------------
def hydrant():
    # A FIRE HYDRANT (the American pillar hydrant): a cast barrel 0.75 m tall on its flange, a bonnet with the
    # pentagonal operating nut, two hose outlets at the sides and the big pumper outlet at the front (+x), their caps
    # chained on.
    pent = lambda id_, at: lathe(id_, "cap", [[0.022, 0], [0.022, 0.03], [0, 0.03]], at, sides=5, faceted=True)
    return item("Fire hydrant", "street",
        "a pillar fire hydrant of the American pattern: a cast-iron barrel 0.75 m tall on its ground flange, a domed bonnet with the pentagonal operating nut, two 2.5-inch hose outlets at the sides and the 4.5-inch pumper outlet at the front (+x), each capped with its own pentagon nut, the caps chained to the barrel.",
        {"body": {"pick": ["paint-red", "paint-red", "paint-yellow"]}, "cap": {"pick": ["paint-silver", "paint-white", "paint-red"]}, "chain": "steel"}, [
            lathe("barrel", "body", [[0.15, 0], [0.15, 0.035], [0.12, 0.05], [0.11, 0.07], [0.11, 0.47], [0.135, 0.48], [0.135, 0.52], [0.11, 0.53],
                                     [0.105, 0.6], [0.075, 0.66], [0.04, 0.68]], [0, 0, 0], sides=20),
            sphere("bolts", "body", 0.012, [0, 0.5, 0], around={"n": 8, "r": 0.125, "plane": "xz"}, sides=6),
            pent("nut", [0, 0.68, 0]),
            lathe("bonnetCap", "cap", [[0.11, 0.53], [0.105, 0.6], [0.075, 0.66], [0.04, 0.68], [0.0, 0.68]], [0, 0, 0], sides=20),
            rod("hose", "body", 0.035, [0, 0.38, 0], [0, 0.38, 0.16], 14, mirror="z"),
            lathe("hoseCap", "cap", [[0.043, 0], [0.043, 0.035], [0.03, 0.04], [0, 0.04]], [0, 0.38, 0.155, 0, 90, 0], sides=14, mirror="z"),
            lathe("hoseNut", "cap", [[0.018, 0], [0.018, 0.022], [0, 0.022]], [0, 0.38, 0.193, 0, 90, 0], sides=5, faceted=True, mirror="z"),
            rod("pumper", "body", 0.058, [0, 0.33, 0], [0.17, 0.33, 0], 18),
            lathe("pumperCap", "cap", [[0.068, 0], [0.068, 0.04], [0.05, 0.048], [0, 0.048]], [0.165, 0.33, 0, 0, 0, -90], sides=18),
            lathe("pumperNut", "cap", [[0.024, 0], [0.024, 0.026], [0, 0.026]], [0.21, 0.33, 0, 0, 0, -90], sides=5, faceted=True),
            sweep("chain", "chain", [[0.08, 0.36, 0.06], [0.12, 0.29, 0.06], [0.17, 0.3, 0.04]], 0.004, seg=3),
            sweep("chainS", "chain", [[0.06, 0.34, 0.1], [0.05, 0.3, 0.14], [0.03, 0.34, 0.17]], 0.004, seg=3, mirror="z"),
        ])


def post_box():
    # A PILLAR BOX (the British round post box): a red cast-iron pillar 1.6 m tall, 0.55 round, on a black plinth,
    # its cap overhanging, the posting aperture under its hood, the door's outline, the collection plate. HOLLOW behind
    # its door: the pillar's wall is a lathe all round but the door's 60 degrees, lined inside; the door (its stretch
    # of the wall, its edges, the plate) hinged at its left edge, swung 110 degrees out by `open` onto the letters
    # lying on the floor inside.
    R, T = 0.27, 0.012
    door = lambda a: [R * math.cos(math.radians(a)), R * math.sin(math.radians(a))]
    seam = []
    for a, y in [(-30, 0.28), (-30, 1.06), (30, 1.06), (30, 0.28)]:
        c, s = door(a)
        seam.append([c + 0.002, y, s])
    piv = door(30)
    rnd = __import__("random").Random(7)
    letters = [[rnd.uniform(-0.05, 0.08), 0.29 + 0.012 * i, rnd.uniform(-0.08, 0.08), rnd.uniform(0, 180), rnd.uniform(-6, 6), 0] for i in range(9)]
    return item("Post box", "street",
        "a British pillar post box: a red cast-iron pillar 1.6 m tall and 0.55 m round on a black plinth, its domed cap overhanging, the posting aperture under its hood at 1.2 m, the outline of its door and a white collection plate on the front (+x); hollow, its door hinged at the left edge and swung out by `open` onto the letters and a parcel lying inside.",
        {"body": "paint-red", "base": "paint-black", "slot": "#121212", "plate": "plastic-white", "inner": "#5a1414", "paper": "#ece6d6", "paper2": "#d8cfb4", "parcel": "#a88458"}, [
            lathe("plinth", "base", [[0.3, 0], [0.3, 0.06], [0.28, 0.09]], [0, 0, 0], sides=28),
            lathe("pillarFoot", "body", [[0.28, 0.09], [R, 0.12], [R, 0.28]], [0, 0, 0], sides=32),
            lathe("pillar", "body", [[R, 0.28], [R, 1.06]], [0, 0, 0], sides=27, arc=[30, 330]),
            lathe("pillarTop", "body", [[R, 1.06], [R, 1.3], [0.29, 1.33], [0.33, 1.37], [0.33, 1.41], [0.3, 1.43], [0.25, 1.5], [0.15, 1.57], [0, 1.6]], [0, 0, 0], sides=32),
            lathe("lining", "inner", [[R - T, 1.06], [R - T, 0.28]], [0, 0, 0], sides=27, arc=[30, 330], inside=True),
            lathe("band", "body", [[R + 0.008, 1.24], [R + 0.008, 1.27]], [0, 0, 0], caps=False, sides=32),
            box("slot", "slot", [0.03, 0.025, 0.26], [R - 0.008, 1.18, 0]),
            box("hood", "body", [0.045, 0.018, 0.3], [R + 0.012, 1.203, 0, 0, 0, -10]),
            rod("doorSide2", "slot", 0.0035, seam[3], seam[2], 4),
            # (the door: hinged at +30 degrees round (its left seen from the front), the plate and the lower seams on it)
            hinge("door", [piv[0], 0.67, piv[1]], [
                lathe("face", "body", [[R, 0.282], [R, 1.058]], [0, 0, 0], sides=5, arc=[-29.5, 29.5]),
                lathe("back", "inner", [[R - T, 1.058], [R - T, 0.282]], [0, 0, 0], sides=5, arc=[-29.5, 29.5], inside=True),
                box("edge", "body", [T, 0.776, 0.004], [[(R - T / 2) * math.cos(math.radians(a)), 0.67, (R - T / 2) * math.sin(math.radians(a)), -a, 0, 0] for a in (-29.5, 29.5)], inside=True),
                rod("doorSide", "slot", 0.0035, seam[0], seam[1], 4),
                *[sweep(f"doorArc{i}", "slot", [[(R + 0.002) * math.cos(math.radians(a)), y, (R + 0.002) * math.sin(math.radians(a))] for a in range(-30, 31, 10)], 0.0035, seg=2)
                  for i, y in enumerate((0.28, 1.06))],
                box("plate", "plate", [0.006, 0.11, 0.15], [R + 0.0, 0.92, 0]),
                box("lock", "slot", [0.004, 0.03, 0.02], [R + 0.002, 0.8, -0.1]),
            ], max_=-110),
            # (inside, seen only open: the letters fallen from the aperture, a small parcel)
            box("letters", "paper", [0.16, 0.004, 0.11], letters[::2], inside=True),
            box("letters2", "paper2", [0.22, 0.004, 0.11], letters[1::2], inside=True),
            box("parcel", "parcel", [0.16, 0.08, 0.11], [-0.08, 0.32, 0.05, 25, 0, 0], inside=True),
        ], params={"open": 0})


def litter_bin():
    # A LITTER BIN (the round street bin): a black steel drum 0.95 m tall on a plinth, its domed hood over the opening
    # all round, a gilt band, LITTER on the front.
    return item("Litter bin", "street",
        "a round street litter bin: a black steel drum 0.95 m tall and 0.5 m round on a plinth, a domed hood standing over the opening on four ribs, a gilt band and LITTER in gilt capitals on the front (+x).",
        {"body": {"pick": ["paint-black", "paint-black", "paint-green"]}, "gilt": "gilt", "dark": "#101010"}, [
            lathe("plinth", "body", [[0.2, 0], [0.2, 0.05], [0.22, 0.08]], [0, 0, 0], sides=24),
            lathe("drum", "body", [[0.22, 0.08], [0.25, 0.12], [0.25, 0.75], [0.26, 0.77]], [0, 0, 0], sides=24),
            lathe("mouth", "dark", [[0.235, 0.77], [0.235, 0.86]], [0, 0, 0], sides=24, caps=False),
            box("rib", "body", [0.03, 0.1, 0.03], [[0.245 * math.cos(math.radians(a)), 0.815, 0.245 * math.sin(math.radians(a))] for a in (45, 135, 225, 315)]),
            lathe("hood", "body", [[0.27, 0.86], [0.27, 0.88], [0.22, 0.95], [0.1, 0.99], [0, 1.0]], [0, 0, 0], sides=24),
            lathe("band", "gilt", [[0.252, 0.66], [0.252, 0.69]], [0, 0, 0], caps=False, sides=24),
            *text3("litter", "gilt", "LITTER", 0.055, [0.251, 0.5, 0], (0, 0, -1), (0, 1, 0), (1, 0, 0), weight=0.15, depth=0.004),
        ])


def bench():
    # A PARK BENCH: two cast-iron ends (each one plate: the front leg, the seat rail, the back leg rising into the back's
    # support; an arm on top), five seat slats and three back slats of hardwood, 1.8 m long. It runs along z, its seat
    # facing +x.
    end = [[0.3, 0], [0.22, 0], [0.19, 0.37], [-0.17, 0.35], [-0.26, 0], [-0.34, 0], [-0.245, 0.43], [-0.33, 0.86], [-0.27, 0.87], [-0.175, 0.46], [0.22, 0.44]]
    arm = [[0.24, 0.44], [0.2, 0.44], [0.205, 0.6], [-0.26, 0.62], [-0.26, 0.67], [0.27, 0.66], [0.29, 0.62]]
    seat = [[0.175 - 0.088 * i, 0.47 - 0.006 * i] for i in range(5)]
    back = [[-0.2 - 0.13 * t + 0.03, 0.5 + 0.41 * t] for t in (0.2, 0.5, 0.8)]
    return item("Bench", "street",
        "a park bench: two cast-iron ends (front leg, seat rail, back leg rising into the back's support, an arm on top), five hardwood seat slats at 0.45 m and three back slats leaning 17 degrees, 1.8 m long; it runs along z, its seat facing +x.",
        {"iron": {"pick": ["paint-black", "paint-green", "#1d1f1e"]}, "wood": {"pick": ["oak", "#8a5a35", "planks-grey"]}}, [
            plate("end", "iron", end, 0.04, [0, 0, 0.85], mirror="z"),
            plate("arm", "iron", arm, 0.05, [0, 0, 0.85], mirror="z"),
            box("seat", "wood", [0.075, 0.03, 1.84], [[x, y, 0] for x, y in seat]),
            box("back", "wood", [0.03, 0.1, 1.84], [[x, y, 0, 0, 0, 17.6] for x, y in back]),
            rod("tie", "iron", 0.008, [-0.05, 0.38, -0.85], [-0.05, 0.38, 0.85], 6),
        ])


def kiosk_sign():
    # THE TELEPHONE BOX'S FASCIA, one side's: the white glazed sign and TELEPHONE in black strokes on it, facing +x
    # in the kiosk's own frame (the box turns it to its four sides)
    c = 0.91 / 2 - 0.004
    return item("Kiosk sign", "components", "a telephone kiosk's fascia: the white glazed sign with TELEPHONE in black, facing +x at the kiosk's side (x 0.451, y 2.2): the phone box places it on its four sides",
        {"fascia": "plastic-white", "letter": "#121212"},
        [box("fascia", "fascia", [0.01, 0.11, 0.66], [c + 0.006, 2.2, 0.0, 0, 0, 0]),
         *text3("tel_", "letter", "TELEPHONE", 0.055, [c + 0.012, 2.2, 0.0], (0, 0, -1), (0, 1, 0), (1, 0, 0), weight=0.15, depth=0.003)])


def phone_box():
    # A TELEPHONE BOX (the red British kiosk of 1935): 0.91 m square and 2.5 high on a plinth, its door at +x, glazed in
    # small panes on three sides, the backlit TELEPHONE fascias under a shallow domed roof with a crown.
    # HOLLOW (2026-11-21): each side is a frame of cast-iron panels (the kick panel, the stiles, the head) round its
    # see-through glazing, the four corner posts and the roof over a ceiling; inside, the telephone on its back wall
    # with the coin box and handset, the directory shelf, the lamp. The door is the whole +x side below the fascia,
    # HINGED at its -z edge (open: 100 degrees out), the handle by its free edge.
    W, H = 0.91, 2.42
    gy0, gy1, gw = 0.41, 1.83, 0.52                    # (the glazing: bottom, top, width)
    o = W / 2 - 0.02                                   # (the side panels' middle, out from the centre; 4 cm thick)
    dt = 2.12                                          # (the door's top: the fascia's panel over it stays)
    parts = [
        box("plinth", "base", [W + 0.08, 0.12, W + 0.08], [0, 0.06, 0]),
        box("ceiling", "body", [W - 0.02, 0.06, W - 0.02], [0, H - 0.03, 0]),
        box("corner", "body", [0.1, H - 0.12, 0.1], [[x, 0.12 + (H - 0.12) / 2, z] for x in (-W / 2 + 0.05, W / 2 - 0.05) for z in (-W / 2 + 0.05, W / 2 - 0.05)]),
        box("cornice", "body", [W + 0.04, 0.06, W + 0.04], [0, H + 0.03, 0]),
        lathe("roof", "body", [[0.66, 0], [0.66, 0.03], [0.6, 0.1], [0.4, 0.17], [0, 0.2]], [0, H + 0.06, 0, 45, 0, 0], sides=4, faceted=True),
        sphere("crown", "gilt", 0.04, [0, H + 0.27, 0], sides=8, stretch=[1.3, 0.8, 1.3]),
        # (inside: the telephone on the back wall -- its case, the coin box, the dial, the handset on its rest -- the
        #  directory shelf under it with two books, the lamp under the ceiling)
        box("backboard", "board", [0.012, 0.62, 0.36], [-o + 0.026, 1.3, 0.0]),
        box("phone", "phone", [0.09, 0.3, 0.2], [-o + 0.077, 1.42, 0.05]),
        box("coinBox", "phone", [0.1, 0.16, 0.16], [-o + 0.082, 1.16, 0.05]),
        lathe("dial", "steel", [[0, 0.006], [0.035, 0.006], [0.038, 0]], [-o + 0.122, 1.46, 0.05, 0, 0, -90], sides=12),
        rod("handset", "phone", 0.018, [-o + 0.14, 1.52, -0.075], [-o + 0.14, 1.32, -0.075], 8),
        sphere("earpiece", "phone", 0.032, [[-o + 0.14, 1.53, -0.075], [-o + 0.14, 1.31, -0.075]], sides=8, stretch=[0.8, 0.6, 1.0]),
        sweep("cord", "steel", [[-o + 0.12, 1.3, -0.04], [-o + 0.1, 1.2, -0.03], [-o + 0.07, 1.16, 0.0]], 0.005, seg=2),
        box("shelf", "body", [0.24, 0.025, 0.6], [-o + 0.14, 0.92, 0]),
        box("directory", "book", [0.2, 0.045, 0.14], [[-o + 0.14, 0.955, -0.17], [-o + 0.15, 1.0, -0.17]]),
        box("lamp", "fascia", [0.12, 0.03, 0.12], [0, H - 0.075, 0]),
    ]
    # (the four sides: each a frame of panels round its glazing of 3 x 8 panes -- the glass, then the bars over it;
    #  the side at +x is the door)
    door = []
    for k, (yaw, nx, nz) in enumerate([(0, 1, 0), (90, 0, -1), (180, -1, 0), (-90, 0, 1)]):
        cx, cz = nx * (W / 2 - 0.004), nz * (W / 2 - 0.004)
        px, pz = nx * o, nz * o
        rx, rz = nz, -nx   # (the panel's right, seen from outside: -n x up)
        y0, pw = (0.13, W - 0.21) if k == 0 else (0.12, W - 0.2)   # (the door clears the plinth and the posts by 5 mm)
        sw = (pw - gw) / 2
        side = [box(f"kick{k}", "body", [0.04, gy0 - y0, pw], [px, (gy0 + y0) / 2, pz, yaw, 0, 0]),
                box(f"stile{k}", "body", [0.04, gy1 - gy0, sw], [[px + rx * u, (gy0 + gy1) / 2, pz + rz * u, yaw, 0, 0] for u in (-(gw + sw) / 2, (gw + sw) / 2)]),
                box(f"glass{k}", "glass", [0.006, 1.42, 0.52], [cx + nx * 0.004, 1.12, cz + nz * 0.004, yaw, 0, 0]),
                *each(f"hbar{k}", [box(f"hbar{k}", "body", [0.012, 0.025, 0.54], [cx + nx * 0.008, 0.42 + 1.42 / 8 * j, cz + nz * 0.008, yaw, 0, 0]) for j in range(9)]),
                *each(f"vbar{k}", [box(f"vbar{k}", "body", [0.012, 1.44, 0.025], [cx + nx * 0.008 + rx * u, 1.12, cz + nz * 0.008 + rz * u, yaw, 0, 0]) for u in (-0.27, -0.09, 0.09, 0.27)])]
        if k == 0:
            door += side + [box("doorHead", "body", [0.04, dt - gy1, pw], [px, (dt + gy1) / 2, pz])]
            parts += [box("head0", "body", [0.04, H - 0.06 - dt, W - 0.2], [px, (H - 0.06 + dt) / 2, pz])]
        else:
            parts += side + [box(f"head{k}", "body", [0.04, H - 0.06 - gy1, W - 0.2], [px, (H - 0.06 + gy1) / 2, pz, yaw, 0, 0])]
    # (the fascias: a white glazed sign over each side, TELEPHONE in black -- the component kiosk-sign, turned to each)
    parts.append(use("fascia", C + "kiosk-sign", [[0, 0, 0, yaw, 0, 0] for yaw in (0, 90, 180, -90)]))
    door += [box("handle", "steel", [0.02, 0.18, 0.03], [W / 2 + 0.01, 1.1, W / 2 - 0.12])]
    parts += [hinge("door", [W / 2, 0, -W / 2 + 0.1], door, max_=100)]
    return item("Telephone box", "street",
        "the red British telephone kiosk of 1935: 0.91 m square and 2.5 m tall on a plinth, cast iron, glazed in small panes on all four sides (the door at +x with its handle, hinged at its -z edge), the TELEPHONE fascias lit white under a shallow domed roof with the crown at the top; inside, the telephone with its coin box on the back wall over the directory shelf, and a lamp.",
        {"body": "paint-red", "base": "concrete", "glass": "window-glass", "fascia": "plastic-white", "letter": "#121212", "gilt": "gilt", "steel": "steel",
         "phone": "#1d1e20", "board": "#3b2a1e", "book": {"pick": ["#d8c25a", "#c9c3b0"]}}, merge(parts), params={"open": 0})


def parking_meter():
    # A PARKING METER (the classic single-space meter): a grey head on a 1.1 m post -- its housing, the domed window
    # over the dial at the front (+x), the coin slot and the turning handle on the side.
    return item("Parking meter", "street",
        "a single-space parking meter of the classic pattern: a cast head (0.16 wide, 0.3 tall) on a 1.1 m steel post, a domed window over the dial and its red expired flag at the front (+x), the coin slot and the handle to turn on the right.",
        {"head": {"pick": ["paint-grey", "paint-silver", "paint-black"]}, "pole": "steel", "cap": "plastic-black", "glass": "glass-light", "flag": "lamp-red", "dark": "#121212", "dial": "plastic-white"}, [
            use("post", C + "pole", [0, 0, 0], {"h": 1.12, "r": 0.03, "base": "none", "cap": 0}),
            box("housing", "head", [0.13, 0.2, 0.16], [0, 1.22, 0], round=0.015),
            rod("top", "head", 0.08, [-0.065, 1.32, 0], [0.065, 1.32, 0], 18),
            box("base", "head", [0.11, 0.05, 0.12], [0, 1.115, 0], round=0.01),
            box("dial", "dial", [0.006, 0.09, 0.11], [0.066, 1.33, 0]),
            box("flag", "flag", [0.004, 0.035, 0.05], [0.07, 1.31, 0.02]),
            sphere("window", "glass", 0.08, [0.06, 1.33, 0], stretch=[0.35, 0.8, 0.8], sides=16),
            box("slot", "dark", [0.004, 0.008, 0.04], [0.066, 1.2, 0]),
            rod("handleHub", "head", 0.02, [0, 1.2, 0.08], [0, 1.2, 0.095], 10),
            box("handle", "pole", [0.06, 0.015, 0.012], [0, 1.2, 0.1]),
        ])


# (the catalogue: one item per sign too, so each can be placed by name)
def write_all():
    for name, f in [("pole", pole), ("sign-face", sign_face), ("signal-head", signal_head), ("kiosk-sign", kiosk_sign)]:
        write("modern/components/" + name, f(), "components")
    for name, f in [("traffic-light", traffic_light), ("pedestrian-light", pedestrian_light), ("road-sign", road_sign), ("direction-sign", direction_sign),
                    ("street-lamp", street_lamp), ("heritage-lamp", heritage_lamp), ("bus-stop", bus_stop), ("bollard", bollard),
                    ("crash-barrier", crash_barrier), ("guard-rail", guard_rail), ("hydrant", hydrant), ("post-box", post_box),
                    ("litter-bin", litter_bin), ("bench", bench), ("phone-box", phone_box), ("parking-meter", parking_meter)]:
        write("modern/street/" + name, f(), "street")
    for sign, lim in [("stop", None), ("give-way", None), ("speed", 30), ("speed", 50), ("no-entry", None), ("crossing", None), ("parking", None)]:
        write("modern/street/sign-" + sign + (f"-{lim}" if lim else ""), road_sign(sign, lim), "street")

GROUPS = {"street": "street", "components": "components"}
