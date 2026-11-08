from sealib import *
import json as _json, math

# THE DRAGONFLY's sculpt overlay (2026-11-07), at k = 1 (scaled by k through `sculptScale`): the rig (body, thorax, head,
# eyes, tail, the four wings' bones) and its coats stay as they are. The game's dragonflies are an instanced herd that
# draws the parts (instanced.js): this overlay is what the asset manager and a sculpted build show
P = REPO + "assets/creatures/others/dragonfly.json"
d = _json.load(open(P))
bone = lambda x: "body" if x > -0.022 else "tail"
sh = []
# the ABDOMEN: ten slim segments, the second swollen a little, the end a touch clubbed; a dark ring at each joint
AB = [(0.024, 0.0036), (0.016, 0.0035), (0.008, 0.0036), (0.0, 0.0031), (-0.012, 0.0027), (-0.024, 0.0025), (-0.036, 0.0024),
      (-0.048, 0.0024), (-0.058, 0.0025), (-0.064, 0.0024), (-0.068, 0.0017)]
for i in range(len(AB) - 1):
    (x0, r0), (x1, r1) = AB[i], AB[i + 1]
    sh.append(S("tube", id="abd%d" % i, bone=bone((x0 + x1) / 2), pts=[[x0, 0.0, 0, r0], [x1, 0.0, 0, r1]], k=0.002, color="@body"))
for i, x in enumerate([0.012, 0.003, -0.006, -0.016, -0.027, -0.038, -0.048, -0.056, -0.062]):
    r = 0.0035 if x > 0 else 0.0029
    sh.append(S("tube", id="seg%d" % i, bone=bone(x), pts=[[x + 0.0007, 0.0, 0, r], [x - 0.0007, 0.0, 0, r]], k=0.0003, kc=0.0003, color="@thorax", op="paint"))
# the paired claspers at the tip
sh.append(S("tube", id="clasp", bone="tail", pts=[[-0.067, 0.0004, 0.0008, 0.0006], [-0.072, 0.0002, 0.0012, 0.0004]], k=0.0003, color="@thorax", mirror=True))
# the THORAX: deep, slanted back (the wings set behind the legs), two pale stripes on its front
sh += [S("ell", id="thorax", bone="thorax", c=[0.031, 0.0025, 0], r=[0.0105, 0.0072, 0.0058], k=0.0015, color="@thorax"),
       S("ell", id="thoraxTop", bone="thorax", c=[0.028, 0.0058, 0], r=[0.0075, 0.0035, 0.0048], k=0.0015, color="@thorax"),
       S("tube", id="humeral", bone="thorax", pts=[[0.038, 0.005, 0.0035, 0.0008], [0.033, -0.001, 0.0055, 0.0008]], k=0.0003, kc=0.0003, color="@body", op="paint", mirror=True),
       # the HEAD: small, all eyes -- two great compound eyes meeting on top, the face below them
       S("ell", id="head", bone="head", c=[0.0445, 0.002, 0], r=[0.0038, 0.0042, 0.0058], k=0.001, color="@thorax"),
       S("ell", id="face", bone="head", c=[0.0478, 0.0, 0], r=[0.0018, 0.0028, 0.0032], k=0.0008, color="@body"),
       S("sphere", id="eye", bone="head", c=[0.0458, 0.0042, 0.0036], r=0.0044, k=0.0008, color="@eye", mirror=True)]
# six thin legs, folded forward under the thorax (a basket for catching prey)
for i, (x, fx) in enumerate([(0.036, 0.046), (0.031, 0.04), (0.026, 0.033)]):
    sh.append(S("tube", id="leg%dL" % i, bone="thorax", pts=[[x, -0.003, 0.0018, 0.001], [x + 0.002, -0.0072, 0.0042, 0.0008], [fx, -0.0092, 0.0034, 0.0006]],
                k=0.0004, color="@leg", mirror=True))
# the WINGS: four long glassy plates on their own bones, a dark pterostigma near each tip, veins fanning from the root
def wing(id, root, tipz, chord, sweep, b):
    x0 = root
    pts = [[x0 + 0.003, 0.0068, 0.003], [x0 + 0.0045 + sweep * 0.4, 0.0074, tipz * 0.45], [x0 + 0.0035 + sweep, 0.008, tipz * 0.92], [x0 + 0.0015 + sweep, 0.008, tipz],
           [x0 - 0.0025 + sweep, 0.0078, tipz * 0.96], [x0 - chord + 0.004 + sweep * 0.5, 0.0072, tipz * 0.55], [x0 - chord, 0.0068, tipz * 0.18], [x0 - 0.002, 0.0066, 0.003]]
    out = fin(pts, 0.00022, "@wing", bone=b, id=id, mirror=True, smooth=2, rays=True)
    st = [x0 + 0.0026 + sweep * 0.95, 0.0081, tipz * 0.87]
    out.append(S("ell", id=id + "Stig", bone=b, c=st, r=[0.0007, 0.0003, 0.0022], k=0.0002, color="@stig", mirror=True))
    return out
sh += wing("foreW", 0.035, 0.052, 0.0062, 0.004, "foreWL")
sh += wing("hindW", 0.025, 0.048, 0.0105, 0.0, "hindWL")

d["_about"] = ("A dragonfly, 7-8 cm long with a 10 cm span: a long thin abdomen of ten segments (a dark ring at each joint, "
    "the claspers at its tip), a deep slanted thorax with pale shoulder stripes, a small head that is nearly all eye (the two great compound "
    "eyes meeting on top), six thin legs folded forward under the thorax, and four long glassy wings, veins fanning from each root and a dark "
    "pterostigma near each tip, beating fast (the hind pair half a beat behind the fore). It darts low and only over water (index.html keeps "
    "it to the lake shore and the river, `fly`: its height above the water, its speed, its wingbeat). SCULPTED (2026-11-07: generator "
    "scratchpad sc/sea2/gen/dragonfly.py; the overlay written at k = 1, scaled by k through `sculptScale`) for the asset manager; the game draws "
    "it as its parts, in the instanced herd (instanced.js) -- at its size the parts read the same.")
d["flags"]["sculptScale"] = "k"
if not any(c.get("name") == "banded demoiselle" for c in d["coats"]):
    d["coats"].append({"name": "banded demoiselle", "body": "#1c58c8", "thorax": "#1440a0", "wing": "#8a9cc4", "eye": "#1a2a50"})
d["_coats"] = ("COATS (species.js makeDragonfly): blue emperor (its own), green darner, ruddy darter, brown hawker, banded demoiselle (metallic blue, "
               "its wings tinted) -- the abdomen's colour and the thorax's (the head's and the tail's).")
d.pop("sculpt", None)
d["colors"].setdefault("leg", "#141416")
d["colors"]["eye"] = "#24506a"   # (a blue emperor's eyes: blue-green)
for c_, e_ in (("green darner", "#2e5a48"), ("ruddy darter", "#6a2418"), ("brown hawker", "#4a3e22")):
    for cc in d["coats"]:
        if cc.get("name") == c_: cc.setdefault("eye", e_)
d["colors"].setdefault("stig", "#2a2420")
d["sculpt"] = {
    "keep": [],
    "mesh": {"cell": 0.00028, "tris": [3000, 900]},
    "shape": sh,
}
# (the key order as it was: `sculpt` after `facet`)
o = {}
for k_, v in d.items():
    o[k_] = v
open(P, "w").write(dumps_def(o))
print("wrote", P, "shapes", len(sh))
