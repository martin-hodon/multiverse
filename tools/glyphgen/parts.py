# the hieroglyph PARTS (assets/glyphs/parts.json): authoring source -- dumped compact by jdump
import sys; sys.path.insert(0, ".")
from jdump import write
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "glyphs") + os.sep
def S(points, fill=None, **k):            # a smooth closed outline
    d = {"shape": "spline", "points": points}
    if fill: d["fill"] = fill
    d.update(k); return d
def L(points, fill, w, **k):              # a limb: a thick stroke with its outline
    d = {"shape": "limb", "points": points, "w": w, "fill": fill}; d.update(k); return d
def line(a, b, stroke="line", w=1.0, **k):
    d = {"shape": "line", "from": a, "to": b, "stroke": stroke, "line": w}; d.update(k); return d
def P(name, **k):                          # a part used
    d = {"part": name}; d.update(k); return d
C = 1   # (a corner, as a point's third number)

parts = {}
# ---- people (facing left: the face toward -x) ------------------------------------------------------------------------
parts["eye"] = {"_about": "a painted eye in profile: the almond, its pupil to the front, the cosmetic line drawn out behind; origin its middle, 6 across",
  "colors": {"pupil": "black"},
  "layers": [{"shape": "lens", "r": 3, "w": 2.3, "fill": "eye", "line": .6},
             {"shape": "circle", "r": .95, "at": [-.7, 0], "fill": "pupil", "outline": False},
             line([2.8, .1], [5.4, .7], w=.8)]}
parts["face"] = {"_about": "a man's face in profile, the neck under it: brow, nose, lips, chin, the skull's back; origin the neck's base, 25 tall",
  "layers": [S([[3.5, 0, C], [-3, 0, C], [-3.4, 4], [-6.8, 5.4], [-8.6, 7.4], [-8.9, 9.1], [-9.7, 10.1], [-9.2, 11.2], [-11.3, 13.3, C], [-9.3, 15.3], [-8.8, 17.6], [-8.2, 20.6], [-5, 23.6], [0, 24.6], [5, 23.2], [8, 19], [8.6, 14], [6.6, 8], [4.6, 5]], "skin"),
             line([-9.4, 10.1], [-7.7, 10.4], w=.55),
             P("eye", at=[-5, 16.3], scale=.85)]}
parts["wig-short"] = {"_about": "the short round wig, over the skull to the nape, the ear left out of it; origin as the face's",
  "colors": {"wig": "black"},
  "layers": [S([[-8, 21], [-5, 24.4], [.5, 25.8], [6.4, 24.2], [9.8, 19.2], [10.2, 12.6], [8.8, 7.4, C], [4.6, 7.6], [1.6, 9.6], [.2, 13], [-.2, 17.4], [-2.4, 19.6], [-6.8, 20.2, C]], "wig"),
             {"shape": "ellipse", "rx": 1.5, "ry": 2.4, "at": [3.4, 13.2], "fill": "skin", "line": .6}]}
parts["wig-long"] = {"_about": "the long tripartite wig: over the skull, a lappet falling before the shoulder to the chest, the mass behind to the shoulder blades; origin as the face's",
  "colors": {"wig": "black"},
  "layers": [S([[-7.8, 20.8], [-5, 24.6], [.5, 26.2], [6.8, 24.4], [10.4, 19], [11, 9], [10.4, -6], [9, -13, C], [-3.2, -13, C], [-3.8, -4], [-2.8, 5.4], [-1.6, 11.6], [-1.6, 16], [-4, 18.8, C], [-6.8, 19.6, C]], "wig"),
             line([3.8, -12.4], [4.4, 4], w=.6)]}
parts["beard-god"] = {"_about": "a god's plaited beard, curling forward at its end; origin under the chin",
  "colors": {"beard": "wig"},
  "layers": [L([[0, 0], [.4, -4], [-.6, -7.4], [-3, -8.6]], "beard", 2.2)]}
NECK = {"shape": "rect", "w": 6.2, "h": 3.4, "at": [.25, -.4], "fill": "skin", "outline": False, "_about": "(where the neck runs into the shoulders: no seam)"}
parts["head"] = {"_about": "a man's head: face, short wig, ear; origin the neck's base", "layers": [P("face"), P("wig-short"), NECK]}
parts["head-god"] = {"_about": "a god's head: face, the long wig, the beard", "layers": [P("face"), P("wig-long"), P("beard-god", at=[-7.6, 5.2]), NECK]}
parts["head-woman"] = {"_about": "a woman's head: face, the long wig, a fillet", "colors": {"skin": "skin-woman"},
  "layers": [P("face"), P("wig-long"), NECK, {"shape": "rect", "w": 17.4, "h": 1.6, "at": [1.6, 21.4], "rot": -8, "fill": "fillet", "outline": False}],}
parts["head-woman"]["colors"]["fillet"] = "red"
parts["torso"] = {"_about": "a man's upper body as the painters drew it: the shoulders seen from in front, the chest in profile, down to the waist; origin the neck's base, 27 deep",
  "layers": [S([[-3.4, 1.4, C], [3.4, 1.4, C], [10, -1.2], [11.4, -5], [7.6, -14], [5.6, -27, C], [-4.6, -27, C], [-6.6, -15], [-9.6, -9], [-11.4, -4.4], [-10, -1.2]], "skin")]}
parts["torso-woman"] = {"_about": "a woman's upper body in her sheath dress, the breast in profile; origin the neck's base", "colors": {"skin": "skin-woman"},
  "layers": [S([[-3, 1.4, C], [3, 1.4, C], [8.4, -1.2], [9.6, -5], [6.6, -14], [5, -27, C], [-4.4, -27, C], [-5.6, -15], [-9.8, -10.6], [-10.2, -6.4], [-9.4, -1.2]], "skin")]}
parts["kilt"] = {"_about": "the kilt (shendyt): from the waist to above the knee, its front flap a little forward; origin the waist's middle", "colors": {"cloth": "cloth"},
  "layers": [S([[-5.2, 0, C], [5.8, 0, C], [8.2, -10], [8.4, -19, C], [-10.6, -19, C], [-8.6, -9]], "cloth"),
             {"shape": "rect", "w": 11.8, "h": 2.2, "at": [.3, -1.1], "fill": "belt", "outline": False}],}
parts["kilt"]["colors"]["belt"] = "red"

# ---- the seated figure's legs, and the standing one's ---------------------------------------------------------------------
parts["legs-seated"] = {"_about": "sitting on the ground, one knee raised: the raised leg (thigh, shin, foot flat before him), the buttock, the other foot folded under; origin the waist's middle, 27 over the ground",
  "layers": [S([[4, -24.4, C], [24, -24.4, C], [22, -21], [12, -20], [5, -21]], "skin"),
             S([[8, 0], [-17, 18], [-24, 14], [-28, -16], [-27, -20], [-39, -24.6, C], [-20, -25.4, C], [-17, -16], [-12, 6], [4, -14], [15, -22.6], [21, -17], [19, -4]], "skin")]}
parts["kilt-seated"] = {"_about": "the kilt over a seated man's hip and thigh; origin the waist's middle", "colors": {"cloth": "cloth", "belt": "red"},
  "layers": [S([[15, 1.4, C], [-7.6, 1.4, C], [-17.6, 13.6], [-13, 16.8], [-3, 8], [7, -10], [14, -15], [20, -12], [19, -2]], "cloth"),
             {"shape": "rect", "w": 22, "h": 2.4, "at": [3.6, .2], "fill": "belt", "outline": False}]}
parts["legs-standing"] = {"_about": "standing, the near leg striding forward, the far one back -- the feet flat; origin the waist's middle, 50 over the ground",
  "layers": [L([[3, -18], [6, -33], [9, -47]], "skin", 6.4),
             S([[4.6, -49.6, C], [15, -49.6, C], [14.4, -47.6], [10, -46], [6.6, -45]], "skin"),
             L([[-2, -18], [-8, -33], [-14, -47]], "skin", 6.6),
             S([[-11, -49.6, C], [-24, -49.6, C], [-23, -47.6], [-16, -46], [-11.6, -45]], "skin")]}
parts["legs-together"] = {"_about": "standing, feet together; origin the waist's middle, 50 over the ground",
  "layers": [L([[1, -18], [1, -33], [1.6, -47]], "skin", 7.4),
             S([[4.6, -49.6, C], [-9.4, -49.6, C], [-8.6, -47.6], [-3, -46], [3.4, -45]], "skin")]}
parts["dress"] = {"_about": "a woman's sheath dress, from under the breast to the ankles; origin the waist's middle", "colors": {"cloth": "cloth"},
  "layers": [S([[-5, 6, C], [5.6, 6, C], [6.6, -6], [8.6, -30], [8, -46, C], [-6.4, -46, C], [-6.6, -30], [-7.4, -8]], "cloth")]}
parts["hand"] = {"_about": "a hand, open, the fingers together, the thumb up; origin the wrist, pointing along -x", "layers": [
  S([[-2, 2], [-4.6, 5.4], [-6.8, 6], [-6.4, 4.2], [-5.2, 2.2]], "skin"),
  S([[1.4, 3], [-4, 3.4], [-9.6, 2.4], [-11.4, .4], [-9.6, -1.8], [-4, -2.8], [1.4, -3]], "skin")]}
parts["fist"] = {"_about": "a closed hand; origin the wrist", "layers": [S([[1, 2], [-3, 2.8], [-5.4, 1.4], [-5.4, -1.6], [-2.4, -2.6], [1, -2]], "skin")]}
parts["feather"] = {"_about": "an ostrich feather, upright, its tip curling forward; origin its quill's foot, 60 tall", "colors": {"plume": "white", "vane": "green"},
  "layers": [S([[1, 0, C], [-1, 0, C], [-3, 14], [-5, 34], [-6, 50], [-8, 58], [-10, 60], [-9, 56], [-4, 48], [0, 36], [3, 14]], "plume"),
             line([0, 2], [-5, 50], w=1)]}

parts["arm"] = {"_about": "an arm held out, the palm down, the hand open: the upper arm, the forearm, the hand; origin the shoulder, reaching along -x, 46 long",
  "layers": [L([[0, 0], [-34, 0]], "skin", 8), P("hand", at=[-34, 0], scale=1.15)]}
parts["leg"] = {"_about": "a leg in profile from the knee down, the foot flat, toes to -x; origin the knee", "layers": [
  L([[0, 0], [0, -30]], "skin", 7.6), S([[3.4, -34.6, C], [-14.6, -34.6, C], [-13.6, -32.2], [-5, -30.4], [3, -29.4]], "skin")]}
parts["quadruped-leg"] = {"_about": "a beast's leg: thigh, the joint, the cannon, the hoof or paw; origin the hip, 34 long", "colors": {"hoof": "black"},
  "layers": [L([[0, 0], [1, -16], [0, -30]], "body", 5.4), {"shape": "rect", "w": 6.4, "h": 4, "at": [-.6, -32], "fill": "hoof"}]}
parts["lion-leg"] = {"_about": "a lion's leg: the paw broad, claws forward; origin the shoulder or the hip", "layers": [
  L([[0, 0], [0, -14], [0, -26]], "body", 6.4), S([[3, -26, C], [-7.4, -27, C], [-8, -29.6, C], [3.4, -29.6, C]], "body")]}
# ---- birds (standing in profile, facing left; drawn at the size of a bird filling the quadrat) --------------------------
parts["bird-body"] = {"_about": "a standing bird's body: breast to the tail's tip, in quadrat units (a bird filling the quadrat); its neck at [32, 64]", "colors": {"plumage": "yellow", "breast": "plumage"},
  "layers": [S([[30, 66], [23, 56], [25, 44], [35, 33], [52, 28], [68, 29], [82, 24], [97, 13, C], [95, 21], [85, 36], [70, 52], [56, 62], [43, 69]], "plumage"),
             S([[25, 54], [27, 42], [36, 34], [46, 31], [40, 40], [32, 50]], "breast", outline=False)]}
parts["bird-wing"] = {"_about": "a bird's wing folded along its back, its long feathers to the tail; laid over bird-body", "colors": {"wing": "plumage", "tips": "wing"},
  "layers": [S([[39, 63], [55, 66], [71, 54], [87, 33], [99, 17, C], [86, 23], [68, 32], [50, 40], [38, 51]], "wing"),
             S([[70, 50], [87, 33], [99, 17, C], [86, 23], [74, 30], [64, 40]], "tips", outline=False),
             S([[70, 50], [87, 33], [99, 17, C], [86, 23], [74, 30], [64, 40]], None, stroke="line", line=.8, closed=True),
             line([52, 52], [80, 32], w=.7), line([46, 48], [74, 30], w=.7)]}
parts["bird-legs"] = {"_about": "a standing bird's two legs and feet", "colors": {"legs": "yellow"},
  "layers": [L([[60, 30], [63, 6]], "legs", 3.2), L([[63, 6], [53, 4]], "legs", 2.4), L([[63, 6], [70, 3.6]], "legs", 2),
             L([[50, 30], [48, 6]], "legs", 3.2), L([[48, 6], [37, 4]], "legs", 2.4), L([[48, 6], [55, 3.6]], "legs", 2)]}
def HEAD(name, about, layers, colors=None):
    parts[name] = {"_about": about + "; origin the neck's base (bird-body's [32, 64]), facing left", **({"colors": colors} if colors else {}), "layers": layers}
EYE = lambda x, y, r=1.6: [{"shape": "circle", "r": r * 1.6, "at": [x, y], "fill": "white", "line": .5}, {"shape": "circle", "r": r, "at": [x - .3, y], "fill": "black", "outline": False}]
HEAD("head-falcon", "a falcon's head: round, the hooked beak, the dark 'tear' under the eye", [
  S([[-1, 0], [-7, 8], [-10, 15], [-8, 23], [0, 27], [9, 24], [11, 14], [8, 3]], "plumage"),
  S([[-8, 19], [-15.6, 17.6], [-17, 12.4, C], [-13.6, 13.6], [-9, 13.6]], "beak"),
  L([[-2, 16], [-3, 7]], "tear", 2.4), *EYE(-2.4, 18.6)], {"beak": "black", "tear": "black"})
HEAD("head-vulture", "a vulture's head: the bare neck rising, the heavy hooked beak", [
  L([[2, 0], [-2, 12], [-4, 22]], "neck", 6.4),
  S([[-1, 20], [-9, 24], [-10, 30], [-4, 33], [3, 30], [4, 24]], "neck"),
  S([[-8, 30], [-18, 28], [-19.6, 22, C], [-15, 24], [-9, 25]], "beak"), *EYE(-3.4, 28.6, 1.3)], {"neck": "plumage", "beak": "yellow-dark"})
HEAD("head-owl", "an owl's head, turned to face us: round, the two great eyes, the little hooked beak, the ear tufts", [
  S([[-14, 0], [-17, 12], [-14, 26], [-11, 30, C], [-6, 26], [6, 26], [11, 30, C], [14, 26], [17, 12], [14, 0]], "face"),
  {"shape": "circle", "r": 5.2, "at": [-6.6, 14], "fill": "white", "line": .7}, {"shape": "circle", "r": 2.4, "at": [-6.6, 14], "fill": "black", "outline": False},
  {"shape": "circle", "r": 5.2, "at": [6.6, 14], "fill": "white", "line": .7}, {"shape": "circle", "r": 2.4, "at": [6.6, 14], "fill": "black", "outline": False},
  {"shape": "points", "points": [[-2, 10], [2, 10], [0, 3]], "fill": "beak"}], {"face": "plumage", "beak": "black"})
HEAD("head-duck", "a duck's head: round on a long neck, the flat bill", [
  L([[0, 0], [-3, 14], [-6, 24]], "neck", 6.4),
  S([[-1, 20], [-10, 23], [-12, 30], [-6, 35], [2, 32], [3, 25]], "neck"),
  S([[-11, 28], [-20, 25.6], [-21, 23, C], [-11, 24]], "bill"), *EYE(-5, 29, 1.2)], {"neck": "plumage", "bill": "black"})
HEAD("head-small", "a small bird's head: the short pointed beak (sparrow, swallow, chick)", [
  S([[-1, 0], [-7, 6], [-9, 13], [-6, 19], [1, 21], [8, 18], [10, 10], [7, 2]], "plumage"),
  {"shape": "points", "points": [[-8, 15], [-16, 12], [-8, 10]], "fill": "beak"}, *EYE(-2.4, 14, 1.3)], {"beak": "black"})
HEAD("head-ibis", "an ibis's head: small, the long beak curving down, the crest behind", [
  L([[0, 0], [-3, 12], [-4, 20]], "neck", 5.2),
  S([[-1, 17], [-8, 20], [-9, 26], [-3, 29], [3, 27], [4, 21]], "neck"),
  S([[-8, 25], [-16, 24], [-24, 18], [-28, 8], [-25, 9], [-20, 16], [-12, 20], [-8, 21]], "beak"),
  S([[2, 28], [8, 32], [10, 26], [5, 24]], "crest"), *EYE(-3.4, 24.4, 1.1)], {"neck": "plumage", "beak": "black", "crest": "plumage"})
HEAD("head-cormorant", "a cormorant's head: flat, the long hooked beak", [
  L([[0, 0], [-6, 10], [-8, 20]], "neck", 5.6),
  S([[-4, 18], [-12, 21], [-12, 26], [-4, 28], [2, 24]], "neck"),
  S([[-11, 25], [-25, 24], [-27, 20, C], [-24, 21.6], [-11, 21]], "beak"), *EYE(-6, 24, 1.1)], {"neck": "plumage", "beak": "black"})
# ---- (more parts above this line) ----
write(OUT + "parts.json", {"name": "Hieroglyphs: parts", "_about": "THE PARTS hieroglyphs are made of (glyphs.js): an eye, a face, a wig, a body, a bird's wing -- each a few shapes of the pattern language (patterns.js: spline, ellipse, rect, line...) in its own frame, its colours ROLES (skin, wig, cloth, plumage) with defaults the sign using it may override. A sign places a part with { part, at, rot, scale, flip, colors }.", "parts": parts})
print(len(parts), "parts")
