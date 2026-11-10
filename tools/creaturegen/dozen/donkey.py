# THE DONKEY (2026-11-09): the horse's frame at .78 (1.05 m at the withers) with the horse's own sculpt scaled the same --
# then a donkey's: EARS twice the length, upright and a little splayed; a heavier head (cranium, jowl and muzzle grown); the
# horse's fall of a lock mane and its forelock gone, a short UPRIGHT BRUSH of a mane down the crest in its place (bristle
# tubes a few cm high, as the zebra's); a THIN TAIL ending in a tuft (a cow's, not a horse's fall of hair); a grey-dun coat
# with the DARK DORSAL STRIPE and SHOULDER CROSS (paint shapes), a pale muzzle, pale eye rings and belly, dark legs. Coats:
# grey (the base), brown, black, pale. A slow mount, a draft animal (the horse's `draft`: yoke and shafts).
import sys, os, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dlib import *

S = 0.78
d = load("mammals/horse")
d["params"]["s"] = S
scale_sculpt(d["sculpt"], S)
d["name"] = "donkey"
d["mount"] = {"h": 1.75, "speed": 1.3}
d["young"] = {**d["young"], "name": "foal"}
d["tail"] = {"r1": "0.028*s", "r2": "0.02*s", "tuft": "0.1*s"}   # (the frame's arc, thin, a tuft at its end)
d["_about"] = ("THE DONKEY (2026-11-09, tools/creaturegen/dozen/donkey.py -- written whole by it): the horse's frame and sculpt at .78; "
               "ears twice the horse's, upright; a heavier head; a short upright brush mane and no forelock; a thin tail with a tuft; "
               "grey-dun with the dark dorsal stripe and shoulder cross (paints), pale muzzle, eye rings and belly, dark legs. "
               "Coats: grey, brown, black, pale -- each with the cross. A slow mount; a draft animal (the horse's yoke and shafts).")

# ---- the head: heavier -- a bigger cranium and jowl, a longer deeper muzzle
grow(d, "cranium", 1.12); grow(d, "jowl", 1.15); grow(d, "forehead", 1.08)
grow(d, "face", 1.08); grow(d, "muzzle", 1.12, 1.1, 1.12); grow(d, "chin", 1.1)
move(d, "muzzle", dx=.012, dy=-.006); move(d, "nostril", dx=.012, dy=-.006); move(d, "chin", dx=.01, dy=-.006)

# ---- the ears: the horse's fin, its edge stretched to twice the length along the ear's axis (root to tip), a little
# wider, and splayed outward (z) and back; the inner colour pale
ear = shape(d, "ear")
root = ear["root"]; r0 = [(root[0][i] + root[1][i]) / 2 for i in range(3)]
tip = ear["edge"][ear["corners"][0]]
ax = [tip[i] - r0[i] for i in range(3)]; L = math.sqrt(sum(v * v for v in ax)); ax = [v / L for v in ax]
def stretch_pt(p, f_len=1.95, f_wide=1.25, splay=.22):
    v = [p[i] - r0[i] for i in range(3)]
    along = sum(v[i] * ax[i] for i in range(3)); perp = [v[i] - along * ax[i] for i in range(3)]
    q = [r0[i] + along * f_len * ax[i] + perp[i] * f_wide for i in range(3)]
    t = max(0.0, along / L)   # (0 at the root, 1 at the tip)
    q[2] += splay * along * f_len * .45 * t   # (the tip leaning outward)
    q[0] -= .06 * along * f_len * t           # (...and a little back)
    return [round(x, 4) for x in q] + list(p[3:])
ear["edge"] = [stretch_pt(p) for p in ear["edge"]]
ear["thick"] = round(ear["thick"] * 1.3, 4); ear["cup"] = .5
ear["rim"] = round(ear["rim"] * 1.4, 4); ear["innerRim"] = round(ear["innerRim"] * 1.6, 4)
ear["fair"] = {"r": round(ear["fair"]["r"] * 1.25, 4), "sink": 3}
ear["rimColor"] = "@earTip"

# ---- the mane: the lock fall and the forelock gone, a brush of upright bristles along the crest (maneRidge's line) --
# every 1.6 cm a bristle 6-7 cm high, leaning a little back, in the mane colour; the ridge itself kept, a little fuller
drop(d, "^lk[ABC]\\d+$", "^fl\\d$")
ridge = shape(d, "maneRidge"); ridge["pts"] = [[p[0], p[1], 0, round(p[3] * 1.1, 4)] for p in ridge["pts"]]
pts = ridge["pts"]
def ridge_at(t):   # (a point along the ridge polyline by its share of the length)
    segs = [math.dist(pts[i][:3], pts[i + 1][:3]) for i in range(len(pts) - 1)]; tot = sum(segs); s = t * tot
    for i, L_ in enumerate(segs):
        if s <= L_ or i == len(segs) - 1:
            u = min(1, s / L_) if L_ else 0
            return [pts[i][j] + (pts[i + 1][j] - pts[i][j]) * u for j in range(4)], [pts[i + 1][j] - pts[i][j] for j in range(3)]
        s -= L_
n = 30
for i in range(n):
    t = (i + .5) / n
    p, dirv = ridge_at(t)
    dl = math.hypot(dirv[0], dirv[1]); ux, uy = dirv[0] / dl, dirv[1] / dl
    nx, ny = -uy, ux   # (up, square to the crest)
    if ny < 0: nx, ny = -nx, -ny
    h = .07 * (1 - .35 * abs(t - .55) * 2)   # (tallest over the middle of the neck, shorter at the withers and the poll)
    lean = -.35   # (leaning back toward the withers)
    base = [p[0], p[1] - .01, 0]
    top = [base[0] + (nx + lean * ux) * h, base[1] + (ny + lean * uy) * h, 0]
    mid = [(base[0] + top[0]) / 2, (base[1] + top[1]) / 2 + .004, 0]
    for side, z in ((0, 0.0), (1, .011), (2, -.011)):
        add(d, {"id": f"brush{i}{'abc'[side]}", "type": "tube", "bone": "neck",
                "pts": [[round(base[0], 4), round(base[1], 4), z, .0105], [round(mid[0], 4), round(mid[1], 4), z * 1.2, .0085], [round(top[0], 4), round(top[1], 4), z * 1.4, .0045]],
                "k": 0.004, "color": "@mane", "hair": .6})

# ---- the tail: the horse's hanging falls gone; a thin tube from the dock to above the hocks on the tail bone, a tuft at its end
drop(d, "tailFall", "tailFall2")
dock = shape(d, "tailDock"); dock["ra"] = round(dock["ra"] * .8, 4); dock["rb"] = round(dock["rb"] * .6, 4); dock["hair"] = .2; dock["color"] = "@body"
b = dock["b"]
add(d, {"id": "tailCord", "type": "tube", "bone": "tail", "pts": [[b[0], b[1], 0, .028], [b[0] - .035, b[1] - .22, 0, .022], [b[0] - .05, b[1] - .42, 0, .018]],
        "k": .02, "color": "@body", "hair": .3})
add(d, {"id": "tailTuft", "type": "ell", "bone": "tail", "c": [b[0] - .06, b[1] - .52, 0], "r": [.045, .11, .038], "rot": [0, 0, -6], "k": .02, "kc": .008, "color": "@tail", "hair": .9})

# ---- the cross: a dorsal stripe from the withers to the dock and a stripe down over each shoulder -- paints on the skin
sp = [s for s in shapes(d) if s["id"] == "withers"][0]["c"]; cr = shape(d, "croup")["c"]
add(d, {"id": "dorsal", "type": "tube", "pts": [[sp[0] + .1, sp[1] + .09, 0, .022], [sp[0] - .25, sp[1] + .045, 0, .022], [cr[0] + .1, cr[1] + .2, 0, .02], [cr[0] - .28, cr[1] + .12, 0, .016]],
        "k": .004, "kc": .006, "op": "paint", "color": "@stripe"}, after="dock")
add(d, {"id": "cross", "type": "tube", "pts": [[sp[0] - .02, sp[1] + .07, .02, .02], [sp[0] + .01, sp[1] - .09, .13, .02], [sp[0] + .05, sp[1] - .25, .185, .017]],
        "k": .004, "kc": .006, "op": "paint", "color": "@stripe", "mirror": True}, after="dorsal")
# pale rings round the eyes, a pale muzzle (the muzzle shape's colour) and a pale belly (the belly's)
ey = d["sculpt"]["eyes"]["at"]
add(d, {"id": "eyeRing", "type": "ell", "bone": "head", "c": [ey[0], ey[1], ey[2] - .004], "r": [.036, .03, .012], "rot": [0, 0, -50], "k": .003, "kc": .005, "op": "paint", "color": "@pale", "mirror": True}, after="cross")
shape(d, "belly")["color"] = "@belly"

# ---- colours: grey-dun with the cross; coats over it
d["colors"] = {"body": "#8c8378", "back": "#7a7268", "flank": "#968d82", "belly": "#d6cfc2", "muzzle": "#e2dacb", "pale": "#ddd6c8", "ear": "#7e766c", "earIn": "#d8d0c2", "earTip": "#3b352f",
               "leg": "#5c544c", "sock": "#5c544c", "foot": "#3a3430", "tail": "#3b352f", "mane": "#3b352f", "stripe": "#3e3832", "eye": "#2a1a10", "nose": "#2a2522"}
d["coats"] = [
  {"name": "grey"},
  {"name": "brown", "body": "#6e5a48", "back": "#5e4c3c", "flank": "#7a6654", "ear": "#64503f", "leg": "#4a3c30", "sock": "#4a3c30", "mane": "#2e2620", "tail": "#2e2620", "stripe": "#2e2620", "earTip": "#2e2620"},
  {"name": "black", "body": "#3a3532", "back": "#302c29", "flank": "#443e3a", "belly": "#b8b0a4", "muzzle": "#cfc6b8", "pale": "#cfc6b8", "ear": "#363230", "earIn": "#b8b0a4", "leg": "#2a2624", "sock": "#2a2624", "mane": "#1e1b19", "tail": "#1e1b19", "stripe": "#1e1b19", "earTip": "#1e1b19"},
  {"name": "pale", "body": "#c4bcb0", "back": "#b4aca0", "flank": "#ccc4b8", "ear": "#b8b0a4", "leg": "#8a8278", "sock": "#8a8278", "mane": "#5a524a", "tail": "#5a524a", "stripe": "#5a524a", "earTip": "#5a524a"},
  {"name": "grey"},
]
d["_coats"] = "COATS (species.js coatDef, by seed): grey (twice: the commonest), brown, black, pale -- each keeps the dorsal stripe and shoulder cross (`stripe`), the pale muzzle, eye rings (`pale`) and belly, the ear tips dark"
save("mammals/donkey", d)
index_add("creatures/mammals/donkey", "Mammals")
if "--shot" in sys.argv: render("creatures/mammals/donkey", "donkey", views=("side", "q", "head", "rear"))
