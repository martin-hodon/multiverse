# suid.py pig|boar -- the pigs, written from their rigs' joints
import sys
from lib import *
name = sys.argv[1]
# (round 4: the hind legs moved BACK under the hams -- they stood out behind the thigh as a shelf over a thin shank -- and
#  the rump drawn in, the tail with it; absolute values, so a re-run never shifts them twice)
PI = 0.05 if name == "pig" else 0.03
pre = json.load(open(ROOT + f"assets/creatures/mammals/{name}.json"))
lg = dict(pre["legs"]); lg["hind"] = [-0.46 if name == "pig" else -0.4] + list(lg["hind"][1:])
tl = dict(pre["tail"]); tl["c"] = [-0.71 + PI if name == "pig" else -0.94 + PI, tl["c"][1]]
if pre["legs"] != lg or pre["tail"] != tl:
    pre["legs"] = lg; pre["tail"] = tl; json.dump(pre, open(ROOT + f"assets/creatures/mammals/{name}.json", "w"), indent=2, ensure_ascii=False)
J = joints(name)
BO = name == "boar"
HX = J["head"]["o"][0] - 0.82
S = Sculpt()
B = "@body"
P = {}
if not BO:
    # ---- the pig: a long deep barrel on short legs, a level back arched a little over the loin, big hams, the jowl under a short neck
    S.ell("barrel", [-0.02, 0.6, 0], [0.48, 0.245, 0.28], k=0.1, color=B)
    S.ell("back", [-0.06, 0.72, 0], [0.46, 0.095, 0.22], rot=[0, 0, 2], k=0.1, color="@back", hair=0.5)
    S.ell("loin", [-0.2, 0.81, 0], [0.26, 0.125, 0.21], rot=[0, 0, 2], k=0.1, color="@back", hair=0.5)   # (the loin arched up behind a slight dip)
    S.ell("shoulderTop", [0.28, 0.8, 0], [0.18, 0.105, 0.2], rot=[0, 0, -6], k=0.1, color="@back", hair=0.5)   # (the shoulder rising)
    S.ell("rump", [-0.43 + PI, 0.6, 0], [0.25, 0.25, 0.26], rot=[0, 0, 10], k=0.1, color=B)
    S.ell("ham", [-0.53 + PI, 0.47, 0.13], [0.2, 0.21, 0.13], rot=[0, 0, 18], k=0.07, color=B, mirror=True)   # (the big round hams, bulging behind and below the rump)
    S.ell("shoulder", [0.3, 0.58, 0], [0.26, 0.26, 0.28], k=0.1, color=B)
    S.ell("belly", [0.0, 0.43, 0], [0.42, 0.12, 0.25], k=0.09, color=B)
    S.ell("teats", [0.0, 0.335, 0], [0.3, 0.03, 0.08], k=0.04, color=B)
    S.ell("neck", [0.56, 0.6, 0], [0.17, 0.2, 0.2], bone="neck", k=0.1, color=B)
    S.ell("jowl", [0.68, 0.48, 0], [0.15, 0.1, 0.15], bone="neck", k=0.08, color=B)
    S.ell("jowlFold", [0.8 + HX, 0.45, 0], [0.11, 0.055, 0.12], rot=[0, 0, -8], bone="head", k=0.05, color=B)   # (the fold under the jaw)
    S.ell("dock", [-0.64 + PI, 0.68, 0], [0.06, 0.05, 0.05], k=0.06, color=B)
    hx, nx = 0.79 + HX, J["nose"]["o"][0] - 0.08   # (the face short: a cylinder, the disc big)
    hy, ny = 0.6, J["nose"]["o"][1]
    S.ell("cranium", [hx, hy, 0], [0.16, 0.15, 0.14], bone="head", k=0.06, color=B)
    S.ell("cheek", [0.82 + HX, 0.51, 0.07], [0.12, 0.08, 0.06], bone="head", k=0.05, color=B, mirror=True)
    S.cone("face", [0.84 + HX, 0.585, 0], [nx - 0.03, ny + 0.005, 0], 0.1, 0.075, bone="head", k=0.05, color="@muzzle")
    S.ell("snout", [nx - 0.02, ny, 0], [0.035, 0.074, 0.078], rot=[0, 0, -8], bone="head", k=0.015, color="@snout")
    S.ell("disc", [nx + 0.005, ny, 0], [0.014, 0.071, 0.075], rot=[0, 0, -8], bone="head", k=0.006, kc=0.003, color="@nose")
    S.sph("nostril", [nx + 0.02, ny + 0.002, 0.026], 0.014, bone="head", k=0.004, op="sub", color="@nostril", mirror=True)
    S.ell("lip", [nx - 0.06, ny - 0.05, 0], [0.07, 0.025, 0.05], rot=[0, 0, -5], bone="head", k=0.02, color="@muzzle")
    # the lop ears, broad and thin, falling forward over the eyes
    e0 = J["earL"]["o"]
    S.ell("ear", [e0[0] + 0.075, e0[1] - 0.005, e0[2] + 0.035], [0.11, 0.022, 0.08], rot=[18, 0, -28], bone="earL", k=0.015, kc=0.006, color="@ear", mirror=True)
    eye = [0.93 + HX, 0.605, 0.07]
    lz = 0.18; LG = "@leg"
    fx, hx2 = J["legFLu"]["o"][0], J["legHLu"]["o"][0]
    S.ell("arm", [fx - 0.02, 0.39, lz * 0.85], [0.1, 0.13, 0.08], bone="legFLu", k=0.06, color=B, mirror=True)
    S.cone("forearm", [fx, 0.34, lz], [fx, 0.18, lz], 0.06, 0.038, bone="legFLu", k=0.03, color=LG, mirror=True)
    S.sph("knee", [fx + 0.005, 0.18, lz], 0.036, bone="legFLl", k=0.015, kc=0.012, color="@joint", mirror=True)
    S.cone("cannon", [fx, 0.17, lz], [fx + 0.01, 0.07, lz], 0.034, 0.03, bone="legFLl", k=0.015, color=LG, mirror=True)
    S.ell("thigh", [hx2 + 0.02, 0.4, lz * 0.85], [0.13, 0.14, 0.09], bone="legHLu", k=0.06, color=B, mirror=True)
    S.cone("gaskin", [hx2, 0.33, lz], [hx2 - 0.02, 0.19, lz], 0.06, 0.035, bone="legHLu", k=0.03, color=LG, mirror=True)
    ham(S, J, [0.5, 1.15], [0.16, 0.25], 0.1, 0.04, B, 0.05, zf=0.85)
    S.sph("hock", [hx2 - 0.03, 0.19, lz], 0.032, bone="legHLl", k=0.015, kc=0.012, color="@joint", mirror=True)
    S.cone("hcannon", [hx2 - 0.02, 0.17, lz], [hx2 + 0.01, 0.07, lz], 0.034, 0.03, bone="legHLl", k=0.015, color=LG, mirror=True)
    TW = 1.1
    keep = ["tail\\d*"]
    cols = {"nose": "#d88a90", "nostril": "#6a3a3a", "foot": "#4a3430", "snout": "#e09a94", "muzzle": "#d89a8c", "ear": "#d8908a", "joint": "#d8968a", "back": "#d0a092"}
    about = "THE PIG (2026-11-05, 2nd pass: the face short and round to a big disc, the belly up, big hams, a jowl fold, pinker snout, ears and joints, dark trotters): a long deep barrel on short legs, the back level and a little arched over the loin, big round hams and a heavy shoulder, the jowl under a short neck; a conical head out to the flat snout disc with its two nostrils, the lop ears falling forward over the eyes; short legs on small cloven trotters with dewclaws; the curly tail kept"
else:
    # ---- the wild boar: high, heavy shoulders and a back falling to narrow hindquarters, the body pressed flat from the sides,
    #      a crest of long bristles along the spine; a long wedge of a head, small erect ears, the tusks; longer slim legs
    S.ell("shoulder", [0.26, 0.73, 0], [0.28, 0.25, 0.23], k=0.1, color=B, hair=0.35, pat="coarse")
    S.ell("withers", [0.2, 0.87, 0], [0.32, 0.12, 0.17], rot=[0, 0, -8], k=0.1, color="@back", hair=0.35, pat="coarse")
    S.ell("barrel", [-0.05, 0.7, 0], [0.43, 0.2, 0.2], rot=[0, 0, -3], k=0.1, color=B, hair=0.35, pat="coarse")
    S.ell("rump", [-0.45 + PI, 0.66, 0], [0.24, 0.2, 0.19], rot=[0, 0, -14], k=0.09, color=B, hair=0.35, pat="coarse")
    S.ell("ham", [-0.43 + PI, 0.6, 0.09], [0.2, 0.2, 0.12], rot=[0, 0, 10], k=0.07, color=B, mirror=True, hair=0.35)
    S.ell("belly", [0.02, 0.57, 0], [0.32, 0.06, 0.16], rot=[0, 0, 3], k=0.08, kc=0.05, color="@belly", hair=0.5, pat="coarse")
    S.ell("neck", [0.55, 0.68, 0], [0.18, 0.2, 0.18], rot=[0, 0, -20], bone="neck", k=0.1, color=B, hair=0.35, pat="coarse")
    S.ell("jowl", [0.66, 0.53, 0], [0.16, 0.11, 0.15], bone="neck", k=0.08, color="@cheek", hair=0.3, pat="coarse")
    S.ell("dock", [-0.67 + PI, 0.7, 0], [0.06, 0.045, 0.045], k=0.06, color=B)
    # the bristle crest: ONE continuous mane along the measured spine, standing highest over the withers, tapering to the rump
    cx = [0.62 - 0.05 * i for i in range(25)]
    tops = surf(S, [{"x": x, "y": 0.7, "dir": [1, 0]} for x in cx])
    def cr(x): return 0.05 + 0.03 * max(0, 1 - abs(x - 0.25) / 0.45)   # (radius 5-8 cm, fullest over the shoulders)
    def ch(x): return 0.045 + 0.1 * max(0, 1 - abs(x - 0.25) / 0.55) ** 1.1   # (how far it stands out: ~14 cm at the withers -- round 3: it must read)
    mane = [[x, 0.7 + t["t"] + ch(x) - cr(x), 0, cr(x)] for x, t in zip(cx, tops) if t["t"] is not None]
    # (audit 2026-11-07: no lumps -- they rendered as shiny rubber wrinkles; the bristles are the coarse hair pattern)
    S.tube("crestN", [p for p in mane if p[0] > 0.4], bone="neck", k=0.04, kc=0.02, color="@crest", hair=0.3, pat="coarse", when="adult")
    S.tube("crest", [p for p in mane if p[0] <= 0.47], k=0.04, kc=0.02, color="@crest", hair=0.3, pat="coarse", when="adult")
    # (audit 2026-11-07) the PIGLET's pale stripes along each flank (its `piglet` variant): paints on the skin, the points
    # probed by sc/au/boar_stripes.py
    for i, pts in enumerate(json.load(open(HERE + "/../au/boar_stripes.json"))):
        S.tube(f"stripe{i}", pts, op="paint", kc=0.006, color="@stripe", mirror=True, when="piglet")
    hx, nx = 0.8 + HX, J["nose"]["o"][0] - 0.02   # (a wedge: shortened)
    hy, ny = 0.63, J["nose"]["o"][1]
    # (audit 2026-11-07: the head a LONG STRAIGHT WEDGE from the crest to the snout -- the old cranium stood up as a round
    #  dome over a thin snout; the forehead line runs on from the neck's crest; a broad flat snout DISC)
    # (round 3, the coordinator's notes: a MASSIVE WEDGE -- deep forehead and cheeks, the profile from crown to disc near-straight
    #  and steep; the disc a flat pink-grey oval facing forward)
    S.ell("cranium", [hx - 0.01, hy + 0.035, 0], [0.17, 0.155, 0.125], rot=[0, 0, -26], bone="head", k=0.06, color=B, hair=0.3, pat="coarse")
    S.ell("cheek", [0.85 + HX, 0.545, 0.07], [0.15, 0.1, 0.064], rot=[0, 0, -20], bone="head", k=0.055, color="@cheek", mirror=True, hair=0.3, pat="coarse")
    S.cone("face", [0.85 + HX, 0.62, 0], [nx - 0.035, ny + 0.01, 0], 0.135, 0.06, bone="head", k=0.06, color="@muzzle", hair=0.3, pat="coarse")
    S.cone("brow", [0.8 + HX, 0.765, 0], [nx - 0.065, ny + 0.058, 0], 0.07, 0.034, bone="head", k=0.05, color="@muzzle", hair=0.3, pat="coarse")
    S.ell("snout", [nx - 0.022, ny + 0.004, 0], [0.034, 0.062, 0.066], rot=[0, 0, -8], bone="head", k=0.018, color="@muzzle")
    S.ell("disc", [nx + 0.007, ny + 0.004, 0], [0.012, 0.058, 0.064], rot=[0, 0, -6], bone="head", k=0.005, kc=0.003, color="@nose", wet=0.35)
    S.sph("nostril", [nx + 0.019, ny + 0.004, 0.021], 0.012, bone="head", k=0.004, op="sub", color="@nostril", mirror=True)
    S.ell("lip", [nx - 0.09, ny - 0.045, 0], [0.11, 0.03, 0.045], rot=[0, 0, -12], bone="head", k=0.02, color="@muzzle")
    S.ell("flange", [nx - 0.1, ny - 0.015, 0.045], [0.045, 0.03, 0.02], rot=[0, 0, -12], bone="head", k=0.015, color="@muzzle", mirror=True)
    e0 = J["earL"]["o"]
    ed = norm([-0.35, 0.85, 0.4])
    S.ell("ear", add(e0, ed, 0.055), [0.042, 0.078, 0.013], rot=orient(ed), bone="earL", k=0.01, kc=0.004, color="@ear", mirror=True, pat="coarse", hair=0.3)
    S.ell("earTuft", add(e0, ed, 0.12), [0.016, 0.03, 0.01], rot=orient(ed), bone="earL", k=0.006, kc=0.003, color="@crest", mirror=True)
    eye = [0.93 + HX, 0.6, 0.068]
    lz = 0.17; LG = "@leg"
    fx, hx2 = J["legFLu"]["o"][0], J["legHLu"]["o"][0]
    S.ell("arm", [fx - 0.02, 0.42, lz * 0.85], [0.085, 0.13, 0.065], bone="legFLu", k=0.06, color=B, mirror=True)
    S.cone("forearm", [fx, 0.36, lz], [fx, 0.19, lz], 0.05, 0.03, bone="legFLu", k=0.03, color=LG, mirror=True)
    S.sph("knee", [fx + 0.006, 0.205, lz], 0.031, bone="legFLl", k=0.014, color=LG, mirror=True)   # (round 3: a knee, the leg jointed)
    S.cone("cannon", [fx, 0.19, lz], [fx + 0.008, 0.08, lz], 0.027, 0.021, bone="legFLl", k=0.012, color=LG, mirror=True)
    S.sph("fetlock", [fx + 0.01, 0.078, lz], 0.024, bone="legFLl", k=0.01, color=LG, mirror=True)
    S.ell("thigh", [hx2 + 0.02, 0.42, lz * 0.8], [0.1, 0.14, 0.07], bone="legHLu", k=0.06, color=B, mirror=True)
    S.cone("gaskin", [hx2, 0.37, lz], [hx2 - 0.02, 0.21, lz], 0.055, 0.03, bone="legHLu", k=0.03, color=LG, mirror=True)
    ham(S, J, [0.36, 1.1], [0.13, 0.25], 0.08, 0.032, B, 0.05, zf=0.8, hair=0.35)
    S.sph("hock", [hx2 - 0.03, 0.21, lz], 0.026, bone="legHLl", k=0.015, color=LG, mirror=True)
    S.cone("hcannon", [hx2 - 0.02, 0.19, lz], [hx2 + 0.008, 0.08, lz], 0.027, 0.021, bone="legHLl", k=0.012, color=LG, mirror=True)
    S.sph("hfetlock", [hx2 + 0.01, 0.078, lz], 0.024, bone="legHLl", k=0.01, color=LG, mirror=True)
    TW = 0.85
    keep = ["tail"]
    # (audit 2026-11-07) the tusks: one smooth path each, its thin end lathed (two cones under the 1.6 cm grid broke to shards)
    if BO:
        n0 = len(S.shapes)
        horn(S, "tusk", [[nx - 0.095, ny - 0.05, 0.045, 0.019], [nx - 0.06, ny - 0.012, 0.072, 0.016], [nx - 0.062, ny + 0.035, 0.09, 0.012], [nx - 0.085, ny + 0.07, 0.096, 0.0065]], "@tusk", 0.0158, k=0.004)
        for p in S.shapes[n0:]: p["when"] = "adult"
    else:
        for nm, a, b in (("tusk", [nx - 0.1, ny - 0.035, 0.05], [nx - 0.075, ny + 0.02, 0.068]), ("tuskTip", [nx - 0.075, ny + 0.02, 0.068], [nx - 0.095, ny + 0.055, 0.075])):
            S.cone(nm, a, b, 0.014 if nm == "tusk" else 0.009, 0.009 if nm == "tusk" else 0.003, bone="head", k=0.004, kc=0.001, color="@tusk", mirror=True, when="adult")
    cols = {"nose": "#86706a", "nostril": "#2a1e1a", "foot": "#141010", "crest": "#211a15", "tusk": "#e8e0cc", "body": "#5a4a3a", "back": "#4a3e30", "belly": "#4a3c30", "cheek": "#72685a", "muzzle": "#3a2e24", "leg": "#3a2e24", "crestTip": "#8a7a66"}
    about = "THE WILD BOAR (2026-11-05, 2nd pass: the belly up on longer legs, a grizzled coat -- grey-brown with a darker back, a paler cheek, a dark snout and legs, bristle sheen -- a deeper shorter wedge of a head, an upright brush of a crest): high heavy shoulders and a back falling to narrow hindquarters, the body pressed flat from the sides under its bark-grizzled coat, a crest of long bristles along the spine highest over the withers; a long wedge of a head out to the snout disc, small erect tufted ears, the kept tusks curling up from the lip flanges; slimmer longer legs on small dark trotters; the tail kept"
# the trotters: two cloven toes and the dewclaws behind
for tag, x0 in (("", J["legFLu"]["o"][0]), ("h", J["legHLu"]["o"][0])):
    bn = "footFL" if not tag else "footHL"
    for side, dz in (("o", 1), ("i", -1)):
        if BO:   # (round 3: two clear hooves with the cleft between them, under a slimmer pastern -- not one dark stump)
            S.cone(tag + "toe" + side, [x0 + 0.008, 0.06, lz + dz * 0.016], [x0 + 0.05, 0.012, lz + dz * 0.021], 0.018, 0.012, bone=bn, k=0.003, kc=0.002, color="@foot", mirror=True)
        else:
            S.cone(tag + "toe" + side, [x0 + 0.005, 0.075, lz + dz * 0.012 * TW], [x0 + 0.045, 0.014, lz + dz * 0.016 * TW], 0.024 * TW, 0.015 * TW, bone=bn, k=0.006, kc=0.003, color="@foot", mirror=True)
        S.sph(tag + "dew" + side, [x0 - 0.022, 0.055, lz + dz * 0.016], 0.01, bone=bn, k=0.008, kc=0.002, color="@foot", mirror=True)
sc = {"_about": about, "keep": keep, "mesh": {"tris": [7500, 2600]}, "shape": S.shapes,
      **({"shade": {"on": "@body", "back": 0.93, "belly": 1.06, "k": 0.15, "at": 0.0, "low": 0.8, "lowAt": -0.4}} if not BO else {}),
      "eyes": {"at": R3(eye), "from": R3([0.86 + HX, 0.6, 0]), "r": 0.016 if BO else 0.018, "iris": "@eye", "lid": "#3a2420" if BO else "#c08878", "sink": 0.5}}
upd = {"colors": cols}
if BO:   # (audit 2026-11-07) VARIANTS: the striped PIGLET, a third his size -- no tusks, no crest, rufous with pale stripes
    cols["stripe"] = "#3e3226"
    upd["params"] = {"adult": True}
    upd["variants"] = {"piglet": {"params": {"adult": False, "piglet": True}, "scale": 0.32,
                                  "colors": {"body": "#8a5a36", "back": "#6e4428", "belly": "#9a6c46", "cheek": "#946440", "muzzle": "#4a3020",
                                             "leg": "#4a3020", "stripe": "#d2ae7c", "crest": "#6e4428"}}}
print(write(name, sc, upd), len(S.shapes), "shapes")
