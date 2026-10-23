#!/usr/bin/env python3
"""MURALS (2026-10-05, docs/murals.md): the parts of Egyptian tomb paintings -- heads, animal heads, wigs, crowns,
beards, hands, feet, held things, the throne, the offering table, the frieze -- the named figures (gods, kings, the
dead) and the paintings, as definitions (assets/murals/*.json) in the hieroglyphs' language (glyphs.js: shapes,
roles, the painter's colours). Units: FIGURE UNITS, a square of the canon is 10; a head and what it wears is drawn
at the neck's base (0, 0), facing left (-x); a hand at its wrist, pointing along -x; a held thing at its grip.

    python3 tools/muralgen.py
"""
import json, math, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "assets", "murals")
C = 1   # a corner (a point's third number)

def S(points, fill=None, **k):
    d = {"shape": "spline", "points": points}
    if fill: d["fill"] = fill
    d.update(k); return d
def L(points, fill, w, **k): d = {"shape": "limb", "points": points, "w": w, "fill": fill}; d.update(k); return d
def line(a, b, stroke="line", w=1.0, **k): d = {"shape": "line", "from": a, "to": b, "stroke": stroke, "line": w}; d.update(k); return d
def ell(x, y, rx, ry, fill, **k): d = {"shape": "ellipse", "rx": rx, "ry": ry, "at": [x, y], "fill": fill}; d.update(k); return d
def circ(x, y, r, fill, **k): d = {"shape": "circle", "r": r, "at": [x, y], "fill": fill}; d.update(k); return d
def rect(x, y, w, h, fill, **k): d = {"shape": "rect", "w": w, "h": h, "at": [x, y], "fill": fill}; d.update(k); return d
def poly(pts, fill, **k): d = {"shape": "points", "points": pts, "fill": fill}; d.update(k); return d
def P(name, **k): d = {"part": name}; d.update(k); return d
def part(about, layers, colors=None): d = {"_about": about}; d.update({"colors": colors} if colors else {}); d["layers"] = layers; return d

parts = {}
# ---- the human head (at the neck's base; the hairline at y 20 = the canon's 18 squares) ----------------------------
HEAD = [[-7, 0, C], [6, 0, C], [6.5, 8], [10, 13], [12, 20], [10.5, 26], [5, 30], [-3, 30.5], [-10, 27.5], [-13.5, 24], [-15, 21.4], [-15.2, 19.5],
        [-17.2, 15.6], [-18.6, 14.3], [-16.6, 13.2], [-15.4, 12.8], [-16.2, 11.6], [-15.2, 10.9], [-14.2, 10.6], [-15.6, 9.6], [-14.6, 7.8], [-13.6, 5.8], [-11.6, 4.6], [-7.2, 5.4]]
parts["m-eye"] = part("the painted eye seen from the front in a profile face: the almond, the iris, the kohl line drawn out behind, the brow", [
    {"shape": "lens", "r": 3.6, "w": 2.6, "at": [0, 0], "fill": "eye", "line": .5},
    circ(-.9, .1, 1.25, "pupil", outline=False),
    S([[-3.6, .2], [-1, 1.25], [2, 1.15], [3.6, .1], [7.2, .5, C], [7.2, 1.1, C], [3.6, .9], [1, 1.9], [-2, 1.7]], "line", outline=False),
    S([[-4.6, 3.4], [-1, 4.7], [3, 4.4], [6.6, 3.4], [6.6, 2.7], [3, 3.6], [-1, 3.8], [-4.6, 2.7]], "brow", outline=False)],
    {"pupil": "black", "brow": "line"})
parts["m-head"] = part("a human head in profile on its neck: brow, nose, lips, chin, the jaw, the ear; the eye frontal", [
    S(HEAD, "skin"),
    S([[-15.2, 11.6], [-13.2, 11.2], [-15, 10.9]], None, stroke="lips", line=.6, closed=False),
    ell(3.4, 15.4, 2.2, 3.4, "skin", line=.5), S([[3.6, 17], [2.4, 15.4], [3.6, 13.8]], None, stroke="line", line=.4, closed=False),
    P("m-eye", at=[-9.4, 19.2])], {"lips": "red-dark"})
parts["m-head-woman"] = part("a woman's head: the face finer, the lips fuller, an earring", [
    S([[-6.4, 0, C], [5.6, 0, C], [6, 8], [9.4, 13], [11.2, 20], [10, 26], [4.6, 29.6], [-3, 30], [-9.6, 27.2], [-13, 24], [-14.4, 21.4], [-14.6, 19.6],
       [-16.4, 15.8], [-17.6, 14.6], [-15.8, 13.4], [-14.8, 13], [-15.8, 11.8], [-14.8, 11.0], [-13.8, 10.7], [-15.2, 9.6], [-14, 7.8], [-12.6, 6], [-10.8, 5], [-6.6, 5.6]], "skin"),
    ell(3, 15.2, 2, 3.1, "skin", line=.5), circ(3, 11, 1.6, "gold"),
    P("m-eye", at=[-8.8, 19.4], scale=.95)])
# ---- wigs and headcloths (over the skull: drawn after the head) ------------------------------------------------------
parts["m-wig-short"] = part("the short round wig over the skull, down to the nape, the ear left showing", [
    S([[-14, 21.6], [-13.2, 25.6], [-8, 30.4], [0, 32.2], [8, 30.6], [13.2, 24], [13.8, 15], [12, 9.4, C], [6.8, 9.6], [6.2, 13.2], [5.6, 18.4], [1, 20.6], [-6, 21.6], [-11, 22.2, C]], "wig")],
    {"wig": "black"})
parts["m-wig-long"] = part("the long tripartite wig: a lappet falling before the shoulder, the mass behind to the shoulder blade", [
    S([[-14, 21.6], [-13.4, 26], [-8, 30.8], [0, 32.6], [8.4, 31], [13.8, 24.6], [15, 12], [14.4, -8], [12.6, -18, C], [-.6, -18, C], [-1.6, -6], [-1.2, 6], [-.6, 14], [-2.6, 19.4], [-8, 21.2], [-11, 22.2, C]], "wig"),
    *[line([x, -17], [x + .8, 6], "wig-line", w=.45) for x in (2.5, 5.5, 8.5, 11.5)]], {"wig": "black", "wig-line": "blue-dark"})
parts["m-nemes"] = part("the king's NEMES: the striped headcloth over the brow, its lappets before the shoulders, its tail behind; the uraeus at the brow", [
    S([[-13.4, 21.6], [-12.4, 26.4], [-6, 31.4], [2, 32.6], [10, 30], [15, 22], [17.4, 10], [20, 0], [21, -6, C], [14, -4], [12.8, 4], [9.6, 4, C], [9.4, -14], [8, -22, C], [-1, -22, C], [-1, -4], [-.4, 8], [-1.2, 14], [-4, 19.8], [-9, 21.4]], "cloth"),
    *[line([-12 + i * 2.6, 22.4 - i * .3], [-10 + i * 2.6, 30.8 - abs(i - 4) * .8], "stripes", w=1.1) for i in range(9)],
    *[line([.5, y], [8.2, y], "stripes", w=1.1) for y in (-18, -14, -10, -6, -2, 2, 6, 10)],
    rect(-1.6, 21.4, 25, 1.8, "band", rot=8, outline=False),
    P("m-uraeus", at=[-12.6, 23])], {"cloth": "gold", "stripes": "blue", "band": "gold"})
parts["m-skullcap"] = part("Ptah's close blue cap", [S([[-14.2, 21], [-13, 26.4], [-7, 31], [1, 32], [8.6, 30], [12.6, 24], [12, 18], [6, 20.4], [-4, 21.6]], "cap")], {"cap": "blue"})
parts["m-uraeus"] = part("the rearing cobra at the brow", [
    S([[0, 0], [-1.6, 2.4], [-3, 5.6], [-2.4, 7.6], [-.6, 7.8], [.4, 6], [-.6, 3.6], [1, 1.2]], "cobra"),
    S([[-2.6, 7.4], [-4, 8.8], [-2.8, 9.4], [-1.6, 8.2]], "cobra")], {"cobra": "gold"})
# ---- crowns (on the wig / headcloth) ---------------------------------------------------------------------------------
parts["m-hedjet"] = part("the WHITE CROWN of Upper Egypt: tall, bulbous, a knob at its top", [
    S([[-13.2, 22, C], [11.6, 22, C], [10.8, 34], [8, 46], [5.6, 58], [6, 62], [2.6, 66], [-1, 62.6], [-1.6, 58], [-5, 46], [-10.6, 34]], "white"), P("m-uraeus", at=[-12.4, 23.6])])
parts["m-deshret"] = part("the RED CROWN of Lower Egypt: a flat cap with a tall back and the curling wire", [
    S([[-13.2, 22, C], [11.6, 22, C], [11.6, 50, C], [6.4, 50, C], [6.4, 34, C], [-12.4, 33, C]], "red"),
    L([[-6, 33], [-10, 40], [-12.6, 46], [-9.6, 49.4], [-7.4, 46.6]], "gold", 1.4), P("m-uraeus", at=[-12.6, 23.6])])
parts["m-pschent"] = part("the DOUBLE CROWN: the white within the red -- the Two Lands", [
    S([[-13.2, 22, C], [11.6, 22, C], [11.6, 50, C], [6.4, 50, C], [6.4, 34, C], [-12.4, 33, C]], "red"),
    S([[-9.4, 33.4, C], [5.6, 33.6, C], [5, 42], [3.6, 54], [3.8, 58], [1.4, 61.4], [-1.4, 58], [-3.4, 50], [-6.6, 41]], "white"),
    L([[-6, 33], [-10, 40], [-12.6, 46], [-9.6, 49.4], [-7.4, 46.6]], "gold", 1.4), P("m-uraeus", at=[-12.6, 23.6])])
parts["m-khepresh"] = part("the BLUE CROWN (khepresh): helmet-shaped, studded with gold discs, the uraeus at the front", [
    S([[-13.6, 21.6, C], [12, 21.6, C], [14, 28], [12.4, 40], [6, 48], [-4, 47], [-11, 40], [-14.6, 30]], "blue"),
    *[circ(x, y, .9, "gold", outline=False) for x in range(-10, 11, 4) for y in (27, 32, 37, 42) if (x + 2) ** 2 / 180 + (y - 33) ** 2 / 300 < 1],
    P("m-uraeus", at=[-12.8, 23.6])])
parts["m-atef"] = part("the ATEF of Osiris: the white crown between two ostrich plumes, on ram's horns", [
    L([[-14, 26], [-20, 25], [-24, 28], [-21, 30]], "gold", 2.2), L([[11, 26], [17, 25], [21, 28], [18, 30]], "gold", 2.2),
    S([[-13.2, 22, C], [11.6, 22, C], [10.8, 34], [8, 46], [5.6, 58], [6, 62], [2.6, 66], [-1, 62.6], [-1.6, 58], [-5, 46], [-10.6, 34]], "white"),
    S([[-12, 26, C], [-10, 26, C], [-9, 46], [-11.4, 62], [-15, 66], [-14.6, 48]], "plume"), S([[9, 26, C], [11, 26, C], [13.6, 48], [12, 66], [8.6, 62], [8, 46]], "plume"),
    P("m-uraeus", at=[-12.4, 23.6])], {"plume": "white"})
parts["m-plumes"] = part("Amun's crown: a low cap and two tall plumes, banded", [
    S([[-13.6, 22, C], [11, 22, C], [11, 30, C], [-13, 30, C]], "red"),
    S([[-6, 30, C], [0, 30, C], [1, 52], [-2, 76], [-5, 80], [-7, 76], [-7.6, 52]], "plume"), S([[0, 30, C], [6, 30, C], [6.6, 52], [5, 76], [2, 80], [0, 76], [-.4, 52]], "plume"),
    *[line([-7.4, y], [6.4, y + .4], "band", w=1.1) for y in (40, 50, 60, 70)]], {"plume": "red", "band": "blue"})
parts["m-sun-disc"] = part("the SUN DISC with the uraeus coiled round it (Ra, Sekhmet)", [
    circ(0, 40, 12, "sun"), S([[-10, 30], [-12.6, 34], [-12, 38], [-10.4, 36], [-9.8, 32]], "gold")], {"sun": "red"})
parts["m-horns-disc"] = part("Hathor's (and Isis') COW HORNS cradling the sun disc", [
    S([[-1, 26], [-10, 28], [-16, 36], [-16, 46], [-13, 52], [-13, 44], [-10, 36], [-2, 30]], "horn"),
    S([[1, 26], [10, 28], [16, 36], [16, 46], [13, 52], [13, 44], [10, 36], [2, 30]], "horn"),
    circ(0, 40, 10, "sun"), rect(0, 25, 18, 4, "gold")], {"horn": "black", "sun": "red"})
parts["m-throne-sign"] = part("the THRONE sign Isis wears", [poly([[-8, 24], [6, 24], [6, 34], [0, 34], [0, 44], [-8, 44]], "blue"), rect(-4, 39, 6, 6, "white")])
parts["m-maat-feather"] = part("Maat's ostrich feather, on a fillet", [
    rect(-1, 21.6, 25, 2.2, "red", rot=8),
    S([[1, 22, C], [3, 22, C], [4, 34], [3, 46], [0, 50], [-2.6, 48], [0, 42], [.6, 32]], "plume")], {"plume": "white"})
parts["m-vulture-cap"] = part("the queen's VULTURE headdress: the bird's wings down over the wig, its head at the brow, tall plumes", [
    S([[-13, 22], [-6, 31], [4, 32], [12, 26], [14, 14], [12, 6], [8, 14], [2, 22], [-6, 23]], "plumage"),
    *[line([0 + i * 2.6, 26 - i], [6 + i * 2, 12 - i * .6], "feather", w=.7) for i in range(4)],
    S([[-13, 22], [-16, 24.6], [-14.6, 26.6], [-11.4, 25]], "plumage"),
    rect(-1, 33, 22, 3.4, "blue"),
    S([[-6, 34, C], [0, 34, C], [1, 54], [-2, 74], [-5, 78], [-7, 74], [-7.6, 54]], "plume"), S([[0, 34, C], [6, 34, C], [6.6, 54], [5, 74], [2, 78], [0, 74], [-.4, 54]], "plume")],
    {"plumage": "gold", "feather": "blue", "plume": "white"})
# ---- animal heads (the whole head on its neck; the gods wear the lappet wig under them) -------------------------------
parts["m-head-falcon"] = part("a FALCON's head: round, the hooked beak, the dark 'tear' marking below the eye", [
    S([[-6, 0, C], [6, 0, C], [8, 10], [11, 20], [9, 27], [2, 31], [-6, 30], [-12, 25], [-14, 20], [-15, 17]], "plumage"),
    S([[-14, 22], [-22, 20.4], [-24.4, 15.6, C], [-21, 16.8], [-16.4, 16.4]], "beak"), S([[-15, 21.6], [-12.4, 22.8], [-12.2, 19.6]], "cere"),
    L([[-8, 17], [-9, 8]], "mark", 3.2), circ(-8.4, 20.6, 2.6, "eye", line=.5), circ(-8.8, 20.6, 1.4, "black", outline=False),
    S([[-5.6, 21], [-.6, 20.4], [2, 21.6]], None, stroke="mark", line=1.4, closed=False)],
    {"plumage": "blue", "beak": "blue-dark", "cere": "yellow", "mark": "blue-dark", "eye": "yellow"})
parts["m-head-jackal"] = part("a JACKAL's head (Anubis): the long muzzle, the tall pointed ears", [
    S([[-6, 0, C], [6, 0, C], [8, 10], [10, 20], [8, 24], [4, 40], [2, 41, C], [0, 27], [-4, 27], [-9, 26], [-16, 23.6], [-26, 21], [-27.6, 18.4], [-25, 16], [-18, 15], [-12, 14], [-7, 10]], "fur"),
    S([[8, 24], [8.6, 38], [6.4, 41, C], [4, 40]], "fur"),
    S([[-26.4, 20.6], [-28, 19.8], [-27.6, 18.4]], "nose"), L([[-25, 16.4], [-16, 15.6]], "line", .6),
    {"shape": "lens", "r": 2.6, "w": 1.6, "at": [-10, 22], "fill": "eye", "line": .5}, circ(-10.4, 22, .9, "black", outline=False),
    ell(3.6, 33, 1.4, 5, "ear-in", outline=False)],
    {"fur": "black", "nose": "black", "eye": "white", "ear-in": "gold"})
parts["m-head-ibis"] = part("an IBIS's head (Thoth): small, the long beak curving down", [
    L([[0, 0], [-2, 12], [-3, 18]], "plumage", 11),
    S([[-8, 18], [-6, 26], [0, 28], [6, 25], [7, 18], [4, 12], [-4, 13]], "plumage"),
    S([[-7, 22], [-16, 20.6], [-26, 14], [-32, 4], [-30, 3.4], [-24, 11], [-15, 17.4], [-7, 18.6]], "beak"),
    circ(-3, 22, 1.8, "eye", line=.5), circ(-3.3, 22, .9, "black", outline=False)], {"plumage": "black", "beak": "black", "eye": "white"})
parts["m-head-ram"] = part("a RAM's head (Khnum): the long face, the horizontal twisted horns", [
    S([[-6, 0, C], [6, 0, C], [8, 10], [10, 20], [6, 27], [-2, 28], [-8, 25], [-14, 20], [-18, 14], [-18.6, 10], [-15, 8], [-10, 8]], "fur"),
    L([[-6, 25], [-18, 28], [-30, 26], [-34, 24]], "horn", 3.4), L([[2, 26], [14, 29], [26, 27], [32, 24]], "horn", 3.4),
    *[line([x, 23.4], [x + 1.4, 29.4], "horn-line", w=.6) for x in (-30, -25, -20, -15, 6, 11, 16, 21, 26)],
    circ(-8, 19, 1.8, "eye", line=.5), circ(-8.3, 19, .9, "black", outline=False)], {"fur": "white", "horn": "yellow-dark", "horn-line": "brown", "eye": "yellow"})
parts["m-head-lion"] = part("a LIONESS's head (Sekhmet): the blunt muzzle, the round ear, the ruff", [
    S([[-6, 0, C], [8, 0, C], [12, 10], [14, 22], [10, 30], [2, 32], [-6, 30], [-11, 25], [-17, 20], [-19, 15], [-17, 11], [-11, 10], [-8, 6]], "mane"),
    S([[-8, 26], [-13, 23], [-18, 19], [-19.4, 15], [-17, 11.6], [-11, 11], [-6, 16], [-4, 22]], "fur"),
    circ(2, 28, 3, "fur"), S([[-19.4, 16.6], [-20, 15], [-18.6, 14]], "nose"),
    {"shape": "lens", "r": 2.4, "w": 1.6, "at": [-9, 21], "fill": "eye", "line": .5}, circ(-9.4, 21, .9, "black", outline=False)],
    {"mane": "yellow-dark", "fur": "yellow", "nose": "black", "eye": "green"})
# ---- beards ----------------------------------------------------------------------------------------------------------
parts["m-beard-royal"] = part("the king's false beard: straight, its end squared", [S([[-12.6, 6, C], [-9.4, 6, C], [-9.4, -6, C], [-12.6, -6, C]], "beard"),
    *[line([-12.6, y], [-9.4, y], "line", w=.4) for y in (-3, 0, 3)]], {"beard": "blue-dark"})
parts["m-beard-god"] = part("a god's false beard: plaited, curling forward at its tip", [L([[-11, 6], [-11, -4], [-12, -8], [-15, -9]], "beard", 3)], {"beard": "blue-dark"})
# ---- the collar: drawn on the shoulders (at the neck's base), its rows round the neck --------------------------------
parts["m-collar"] = part("the BROAD COLLAR (wesekh): rows of beads round the neck over the shoulders and chest", [
    *[{"shape": "arc", "r": r, "a0": 185, "a1": 355, "stroke": c, "line": 3.2, "at": [-1, 2]} for r, c in ((7, "row1"), (10, "row2"), (13, "row3"), (16, "row4"))],
    *[{"shape": "arc", "r": r, "a0": 185, "a1": 355, "stroke": "line", "line": .4, "at": [-1, 2]} for r in (5.4, 8.6, 11.6, 14.6, 17.6)]],
    {"row1": "blue", "row2": "red", "row3": "green", "row4": "gold"})
# ---- hands and feet ---------------------------------------------------------------------------------------------------
parts["m-hand-open"] = part("an open hand, the fingers together, the thumb up: at the wrist, along -x", [
    S([[1, 2.6], [-4, 3.2], [-9, 2.6], [-12.4, 1.6], [-13.4, .2], [-12, -1.4], [-6, -2.4], [1, -2.6]], "skin"),
    S([[-2, 2.4], [-5, 6.4], [-7.6, 7], [-7.2, 5], [-5.4, 2.6]], "skin"), line([-6, .2], [-12.6, .4], "line", w=.35)])
parts["m-fist"] = part("a closed fist, gripping: at the wrist, along -x (the grip at (-6, 0))", [
    S([[1, 3], [-4, 3.6], [-8.4, 2.8], [-9.2, -.4], [-8, -3], [-3, -3.4], [1, -2.8]], "skin"), line([-8.6, 1], [-5, 1.6], "line", w=.35), line([-8.8, -1], [-5, -.8], "line", w=.35)])
parts["m-foot"] = part("a foot in profile seen from the inside (the big toe): the ankle at (0, 9), toes to -x", [
    S([[7, 0, C], [-24, 0, C], [-25, 1.6], [-22, 3.4], [-12, 4.8], [-4, 7.6], [-1, 10], [5, 10], [7, 6]], "skin"), line([-20, 2.6], [-24, 2.4], "line", w=.35)])
# ---- held things (at the grip; up is +y) ------------------------------------------------------------------------------
parts["m-ankh"] = part("the ANKH, held by its loop (grip at the loop's top)", [
    {"shape": "ring", "r": 5, "w": 2.2, "at": [0, -5], "fill": "ankh"}, rect(0, -10.8, 13, 2.6, "ankh"), poly([[-1.2, -11.6], [1.2, -11.6], [1.8, -26], [-1.8, -26]], "ankh")], {"ankh": "blue"})
parts["m-was-head"] = part("the WAS sceptre's head: an animal's (the Seth beast's) head bent forward", [S([[1.2, 0, C], [-1.2, 0, C], [-2, 4], [-8, 6], [-9, 8], [-3, 8.6], [1.2, 6]], "staff")], {"staff": "gold"})
parts["m-was-fork"] = part("the WAS sceptre's forked foot", [poly([[-1.2, 0], [1.2, 0], [3, -6], [1.4, -6], [0, -2.6], [-1.4, -6], [-3, -6]], "staff")], {"staff": "gold"})
parts["m-crook"] = part("the CROOK (heqa), held at the chest", [L([[0, -14], [0, 18], [-1.6, 22], [-5.4, 23], [-7.4, 20], [-6.6, 17.6]], "gold", 2.2),
    *[line([-1.1, y], [1.1, y], "blue", w=1.2) for y in range(-12, 17, 4)]])
parts["m-flail"] = part("the FLAIL (nekhakha), held at the chest, its strands falling back", [L([[0, -10], [2, 16]], "gold", 2), *[L([[2, 16], [7 + i * 1.5, 12 - i * 2.2], [8 + i * 1.6, 2 - i * 2.4]], "blue", 1.2) for i in range(3)]])
parts["m-lotus"] = part("a LOTUS flower on its stem, held up", [L([[0, 0], [-1, 14]], "green", 1.2), S([[-1, 14], [-6, 22], [-3, 21], [-1, 26], [1, 21], [4, 22]], "white"), S([[-1, 14], [-4, 20], [-1, 18], [2, 20]], "blue")])
parts["m-jar"] = part("a libation jar (hes), offered on the palm", [S([[-3, 0, C], [3, 0, C], [4.4, 6], [3, 14], [4.4, 17, C], [-4.4, 17, C], [-3, 14], [-4.4, 6]], "jar"), L([[-4, 15], [-9, 18], [-11, 20]], "jar", 1.4)], {"jar": "gold"})
parts["m-loaves"] = part("loaves on a tray, offered", [rect(0, .8, 16, 1.6, "tray"), poly([[-6, 1.6], [-2, 1.6], [-4, 11]], "bread"), ell(1.6, 4.4, 3.4, 2.8, "bread"), poly([[3, 1.6], [7, 1.6], [5, 10]], "bread")], {"tray": "red-dark", "bread": "yellow-dark"})
parts["m-sistrum"] = part("a SISTRUM, Hathor's rattle", [L([[0, 0], [0, 10]], "gold", 1.6), circ(0, 13, 3, "skin-woman"), {"shape": "arc", "r": 5, "a0": 0, "a1": 180, "at": [0, 18], "stroke": "gold", "line": 1.6}, line([-5, 18], [-5, 14], "gold", w=1.6), line([5, 18], [5, 14], "gold", w=1.6)])
# ---- furniture and the wall -------------------------------------------------------------------------------------------
parts["m-throne"] = part("the BLOCK THRONE on its dais: a cube with a low back, the feather pattern on its side, the sema-tawy panel", [
    rect(-4, 3, 96, 6, "dais"), rect(16, 28, 34, 44, "seat"), rect(31, 37, 4, 22, "seat"),
    *[poly([[x, 8], [x + 4, 8], [x + 2, 14]], "feather") for x in range(2, 30, 5)],
    *[line([0, y], [32, y], "feather", w=.8) for y in (16, 18)],
    rect(16, 33, 22, 18, "panel"), circ(16, 33, 4.4, "seat")], {"dais": "green", "seat": "red", "feather": "blue", "panel": "gold"})
parts["m-offering-table"] = part("the OFFERING TABLE heaped high: a stand, loaves, vegetables, a duck, a lotus over all", [
    poly([[-3, 0], [3, 0], [2, 24], [-2, 24]], "stand"), rect(0, 25, 34, 3, "stand"),
    *[poly([[x - 2, 27], [x + 2, 27], [x, 44]], "bread") for x in (-13, -6, 1, 8)],
    ell(-9, 31, 5, 3.2, "bread"), ell(6, 31, 5, 3.2, "bread"),
    S([[-12, 44], [-4, 50], [6, 48], [10, 44], [4, 41], [-6, 41]], "duck"), L([[-12, 44], [-16, 50], [-14, 53]], "duck", 2.2),
    ell(10, 52, 4, 2.4, "green"), S([[0, 48], [-2, 58], [2, 56], [4, 62], [6, 56], [10, 58], [8, 48]], "white"), S([[4, 48], [0, 55], [4, 53], [8, 55]], "blue")],
    {"stand": "yellow-dark", "bread": "yellow", "duck": "white"})
parts["m-kheker"] = part("one KHEKER of the frieze: a bundle of reeds knotted at its top", [
    S([[-3, 0, C], [3, 0, C], [3.4, 12], [1.6, 15], [2.6, 18.6], [0, 21], [-2.6, 18.6], [-1.6, 15], [-3.4, 12]], "reed"), rect(0, 13.4, 7, 2, "band"), circ(0, 18, 1.4, "band")],
    {"reed": "green", "band": "red"})

# ---- THE FIGURES: who each is, in the engine's words (murals.js figureLayers) ---------------------------------------------
GOD_KILT = {"garment": "kilt", "kiltColor": "white", "collar": True, "belt": "gold"}
FIG = {
 "ra": {"name": "Ra-Horakhty", "kind": "man", "pose": "stride", "arms": ["sceptre", "ankh"], "head": "falcon", "wig": "m-wig-long", "crown": "m-sun-disc", **GOD_KILT, "skin": "red", "wigColor": "blue"},
 "horus": {"name": "Horus", "kind": "man", "pose": "stride", "arms": ["sceptre", "ankh"], "head": "falcon", "wig": "m-wig-long", "crown": "m-pschent", **GOD_KILT, "skin": "red", "wigColor": "blue"},
 "anubis": {"name": "Anubis", "kind": "man", "pose": "stride", "arms": ["sceptre", "ankh"], "head": "jackal", "wig": "m-wig-long", **GOD_KILT, "skin": "red", "wigColor": "blue"},
 "thoth": {"name": "Thoth", "kind": "man", "pose": "stride", "arms": ["sceptre", "ankh"], "head": "ibis", "wig": "m-wig-long", **GOD_KILT, "skin": "red", "wigColor": "blue"},
 "khnum": {"name": "Khnum", "kind": "man", "pose": "stride", "arms": ["sceptre", "ankh"], "head": "ram", "wig": "m-wig-long", **GOD_KILT, "skin": "red", "wigColor": "blue"},
 "amun": {"name": "Amun", "kind": "man", "pose": "stride", "arms": ["sceptre", "ankh"], "head": "human", "beard": "god", "crown": "m-plumes", **GOD_KILT, "skin": "blue"},
 "ptah": {"name": "Ptah", "kind": "man", "pose": "mummy", "arms": ["sceptre-chest", None], "head": "human", "wig": "m-skullcap", "beard": "god", "collar": True, "skin": "green", "shroud": "white"},
 "osiris": {"name": "Osiris", "kind": "man", "pose": "mummy-seated", "arms": ["crook", "flail"], "head": "human", "crown": "m-atef", "beard": "god", "collar": True, "skin": "green", "shroud": "white"},
 "isis": {"name": "Isis", "kind": "woman", "pose": "stand", "arms": ["sceptre", "ankh"], "head": "woman", "wig": "m-wig-long", "crown": "m-throne-sign", "garment": "dress", "dressColor": "red", "collar": True, "skin": "skin-woman", "wigColor": "blue"},
 "hathor": {"name": "Hathor", "kind": "woman", "pose": "stand", "arms": ["sceptre", "ankh"], "head": "woman", "wig": "m-wig-long", "crown": "m-horns-disc", "garment": "dress", "dressColor": "red", "collar": True, "skin": "skin-woman", "wigColor": "blue"},
 "maat": {"name": "Maat", "kind": "woman", "pose": "stand", "arms": ["hang", "ankh"], "head": "woman", "wig": "m-wig-long", "crown": "m-maat-feather", "garment": "dress", "dressColor": "white", "collar": True, "skin": "skin-woman", "wigColor": "blue"},
 "sekhmet": {"name": "Sekhmet", "kind": "woman", "pose": "stand", "arms": ["sceptre", "ankh"], "head": "lion", "wig": "m-wig-long", "crown": "m-sun-disc", "garment": "dress", "dressColor": "green", "collar": True, "skin": "skin-woman", "wigColor": "blue"},
 "king": {"name": "The king (offering)", "kind": "man", "pose": "stride", "arms": ["offer", "offer"], "holds": {"front": "m-jar"}, "head": "human", "wig": "m-nemes", "beard": "royal", "garment": "royal-kilt", "kiltColor": "white", "collar": True, "belt": "gold", "tail": True, "skin": "red"},
 "king-crowned": {"name": "The king (double crown)", "kind": "man", "pose": "stride", "arms": ["staff", "hang"], "head": "human", "wig": "m-wig-short", "crown": "m-pschent", "beard": "royal", "garment": "royal-kilt", "kiltColor": "white", "collar": True, "belt": "gold", "tail": True, "skin": "red"},
 "king-khepresh": {"name": "The king (blue crown, adoring)", "kind": "man", "pose": "stride", "arms": ["adore", "adore"], "head": "human", "crown": "m-khepresh", "garment": "royal-kilt", "kiltColor": "white", "collar": True, "belt": "gold", "tail": True, "skin": "red"},
 "queen": {"name": "The queen", "kind": "woman", "pose": "stand", "arms": ["offer", "hang"], "holds": {"front": "m-sistrum"}, "head": "woman", "wig": "m-wig-long", "crown": "m-vulture-cap", "garment": "dress", "dressColor": "white", "collar": True, "skin": "skin-woman"},
 "noble": {"name": "A noble (adoring)", "kind": "man", "pose": "stride", "arms": ["adore", "adore"], "head": "human", "wig": "m-wig-long", "garment": "kilt", "kiltColor": "white", "collar": True, "skin": "red"},
 "wife": {"name": "His wife", "kind": "woman", "pose": "stand", "arms": ["lotus", "hang"], "holds": {"front": "m-lotus"}, "head": "woman", "wig": "m-wig-long", "garment": "dress", "dressColor": "white", "collar": True, "skin": "skin-woman"},
 "bearer": {"name": "An offering bearer", "kind": "man", "pose": "stride", "arms": ["offer", "hang"], "holds": {"front": "m-loaves"}, "head": "human", "wig": "m-wig-short", "garment": "kilt", "kiltColor": "white", "skin": "red"},
}

# ---- THE PAINTINGS ------------------------------------------------------------------------------------------------------
TEXT = lambda seed, cols=6, rows=5: {"cols": cols, "rows": rows, "lines": "columns", "face": "right", "pool": {"*": 1}, "ground": "limestone", "divider": {"color": "line", "width": .03}, "seed": seed}
PAINT = {
 "offering-to-osiris": {"name": "The king offers to Osiris", "size": [640, 340], "ground": "limestone", "frieze": "kheker", "dado": True, "border": True,
   "registers": [{"h": 260, "items": [
      {"figure": "osiris", "x": 470, "face": "left", "scale": 1.1},
      {"table": True, "x": 365},
      {"figure": "king", "x": 250, "face": "right"},
      {"figure": "isis", "x": 120, "face": "right", "scale": .95},
      {"text": TEXT(3, 4, 5), "x": 290, "y": 150, "w": 100, "h": 100},
      {"text": TEXT(5, 3, 3), "x": 510, "y": 220, "w": 66, "h": 36}]}]},
 "gods-procession": {"name": "A procession of the gods", "size": [720, 300], "ground": "limestone", "frieze": "sky", "dado": True, "border": True,
   "registers": [{"h": 230, "items": [{"figure": f, "x": 70 + i * 120, "face": "left", "scale": .85} for i, f in enumerate(["anubis", "horus", "thoth", "khnum", "hathor", "sekhmet"])] +
                  [{"text": TEXT(10 + i, 2, 3), "x": 22 + i * 120, "y": 190, "w": 36, "h": 36} for i in range(6)]}]},
 "adoration-of-ra": {"name": "The king adores Ra", "size": [560, 320], "ground": "limestone", "frieze": "kheker", "dado": True, "border": True,
   "registers": [{"h": 245, "items": [{"figure": "ra", "x": 400, "face": "left", "scale": 1.05}, {"figure": "maat", "x": 470, "face": "left", "scale": .9},
                  {"figure": "king-khepresh", "x": 220, "face": "right"}, {"table": True, "x": 315, "scale": .8},
                  {"text": TEXT(21, 4, 4), "x": 285, "y": 150, "w": 88, "h": 88}]}]},
 "the-dead-and-their-offerings": {"name": "The deceased and his wife, the offerings brought", "size": [620, 420], "ground": "plaster", "frieze": "kheker", "dado": True, "border": True,
   "registers": [{"h": 200, "items": [{"figure": "noble", "x": 380, "face": "left"}, {"figure": "wife", "x": 455, "face": "left", "scale": .92}, {"table": True, "x": 270, "scale": .9},
                  {"figure": "anubis", "x": 150, "face": "right", "scale": .95}, {"text": TEXT(31, 4, 4), "x": 225, "y": 108, "w": 80, "h": 80}]},
                 {"h": 140, "items": [{"figure": "bearer", "x": 120 + i * 110, "face": "left", "scale": .6} for i in range(5)]}]},
 "anubis-guardian": {"name": "Anubis guards the dead (an upright panel)", "size": [300, 330], "ground": "limestone", "frieze": "kheker", "dado": True, "border": True,
   "registers": [{"h": 255, "items": [{"figure": "anubis", "x": 190, "face": "left", "scale": 1.05}, {"table": True, "x": 85, "scale": .9},
                  {"text": TEXT(51, 3, 3), "x": 40, "y": 140, "w": 72, "h": 72}]}]},
 "isis-and-hathor": {"name": "Isis and Hathor (an upright panel)", "size": [300, 330], "ground": "limestone", "frieze": "sky", "dado": True, "border": True,
   "registers": [{"h": 262, "items": [{"figure": "isis", "x": 100, "face": "right", "scale": .95}, {"figure": "hathor", "x": 205, "face": "left", "scale": .95},
                  {"text": TEXT(61, 2, 3), "x": 128, "y": 160, "w": 44, "h": 66}]}]},
 "pyramid-texts": {"name": "The Pyramid Texts (a wall of columns)", "size": [600, 300], "ground": "limestone", "frieze": "sky", "border": True,
   "registers": [{"h": 270, "items": [{"text": {**TEXT(41, 18, 9), "mode": "blue", "ground": "limestone"}, "x": 20, "y": 10, "w": 560, "h": 250}]}]},
}

def main():
    os.makedirs(OUT, exist_ok=True)
    json.dump({"kind": "mural-parts", "name": "Mural parts", "_about": "the parts of tomb paintings in the hieroglyphs' language (glyphs.js): figure units (a square of the canon is 10), a head and its headdress at the neck's base facing left, a hand at its wrist along -x, a held thing at its grip", "parts": parts},
              open(os.path.join(OUT, "parts.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"kind": "mural-figures", "name": "Mural figures", "_about": "the named figures (murals.js figureLayers): kind (man, woman), pose (stand, stride, mummy, mummy-seated, sit), arms [front, back] (hang, staff, sceptre, ankh, offer, adore, lotus, crook, flail, sceptre-chest), head (human, woman, falcon, jackal, ibis, ram, lion), wig, crown (parts), beard (royal, god), garment (kilt, royal-kilt, dress), collar, belt, tail, holds { front, back } (parts), skin and the other colours (the painter's names)", "figures": FIG},
              open(os.path.join(OUT, "figures.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({"kind": "mural", "name": "Murals", "_about": "the paintings (murals.js renderPainting): size [w, h] in figure units, ground, frieze (kheker | sky), dado, border, registers top to bottom -- each a height and its items: a figure (a named one or written out; x its feet's middle, face left or right, scale), the offering table, text columns (a hieroglyph text, glyphs.js: x, y from the register's top, w, h)", "paintings": PAINT},
              open(os.path.join(OUT, "paintings.json"), "w"), indent=1, ensure_ascii=False)
    ip = os.path.join(ROOT, "assets", "index.json"); idx = json.load(open(ip))
    idx["categories"] = [c for c in idx["categories"] if c["name"] != "Murals"] + [{"name": "Murals", "kind": "mural", "paths": ["murals/parts", "murals/figures", "murals/paintings"]}]
    json.dump(idx, open(ip, "w"), indent=2, ensure_ascii=False); open(ip, "a").write("\n")
    print(len(parts), "parts,", len(FIG), "figures,", len(PAINT), "paintings")

if __name__ == "__main__": main()
