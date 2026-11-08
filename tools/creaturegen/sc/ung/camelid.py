# camelid.py camel|bactrian -- the camels, written from their rigs' joints
import sys
from lib import *
name = sys.argv[1]
BA = name == "bactrian"
# (round 4: the hind legs moved BACK 10 cm under the rump -- it stood out behind the thigh as a shelf over a thin shank --
#  and the rump drawn in 4 cm, the tail with it; the pristine rig so altered, a bactrian's re-made shorter below from it)
HB, PI = 0.1, 0.04
O0 = json.load(open(HERE + f"/orig_{name}.json")); O0["legs"]["hind"][0] = round(O0["legs"]["hind"][0] - HB, 4)
O0["tail"]["c"][0] = round(O0["tail"]["c"][0] + PI, 4)
json.dump(O0, open(HERE + f"/_mod_{name}.json", "w"))
J = joints(name, HERE + f"/_mod_{name}.json")
WB = 1.15 if BA else 1.0   # (a bactrian's barrel: broader)
S = Sculpt()
B = "@body"
# ---- trunk: narrow, shallower than the rig's (long legs under it), the sternal pad under the chest
S.ell("chest", [0.36, 1.47, 0], [0.4, 0.3, 0.25 * WB], k=0.1, color=B)
S.ell("keel", [0.42, 1.24, 0], [0.22, 0.12, 0.1], rot=[0, 0, -8], k=0.08, color=B)
S.ell("withers", [0.4, 1.66, 0], [0.32, 0.12, 0.14], rot=[0, 0, -8], k=0.08, color=B)
S.ell("barrel", [-0.1, 1.46, 0], [0.62, 0.27, 0.32 * WB], k=0.1, color=B)
S.ell("belly", [-0.15, 1.3, 0], [0.45, 0.1, 0.27 * WB], rot=[0, 0, -6], k=0.08, color=B)
S.ell("rump", [-0.6 + PI, 1.5, 0], [0.32, 0.2, 0.23 * WB], rot=[0, 0, -18], k=0.09, color=B)
S.ell("haunch", [-0.67 + PI, 1.38, 0.11 * WB], [0.27, 0.25, 0.11], k=0.06, color=B, mirror=True)
S.ell("pad", [0.43, 1.12, 0], [0.12, 0.055, 0.09], k=0.04, kc=0.015, color="@pad")   # (the sternal pad: it kneels on it)
S.ell("scapula", [0.5, 1.5, 0.17], [0.09, 0.26, 0.08], rot=[0, 0, 22], k=0.06, color=B, mirror=True)
if BA:
    # (round 7) two humps, soft fatty cone-domes broader at the base than tall: each a broad base swell sunk in the back and
    # a smaller dome on it, the front one leaning a little forward, the rear one a little back (and flopping to one side);
    # a saddle between them raised to ~40% of their height (the dip 60% of it deep), where the rider sits (`saddle`). The
    # coat goes on up them, a shade darker and shaggier over the crowns: a paint layer inside each dome, out over the top
    for nm, x, lean, fz, rz in (("humpB", 0.48, 0.06, 0.0, -12), ("humpA", -0.42, -0.06, 0.03, 12)):
        S.ell(nm + "Base", [x, 1.76, 0], [0.3, 0.22, 0.23 * WB], k=0.16, color=B)
        S.ell(nm, [x + lean * 0.6, 1.93, fz * 0.5], [0.19, 0.16, 0.16], rot=[0, 0, rz], k=0.14, color=B)
        S.ell(nm + "Shag", [x + lean * 0.8, 1.955, fz * 0.6], [0.165, 0.15, 0.145], rot=[0, 0, rz], k=0.03, kc=0.05, color="@humpc", fleece=True, hair=0.7)
    S.ell("saddleFill", [0.03, 1.775, 0], [0.32, 0.13, 0.22 * WB], k=0.14, color=B)
    # (the neck's root filled out into the shoulder: no crease where the neck wool meets it)
    S.ell("neckFill", [0.64, 1.6, 0], [0.26, 0.24, 0.21], rot=[0, 0, 30], k=0.14, color=B)
else:
    # (round 4) one soft mound: a single broad fatty swell blended wide into the back, rising behind the seat (species.js
    # saddle(): the withers, x ~0.19, y ~1.79), highest just behind the middle of the back, falling longer over the loin
    S.ell("hump", [-0.23, 1.64, 0], [0.4, 0.38, 0.24], k=0.17, color=B)
    S.ell("humpFall", [-0.48, 1.72, 0], [0.32, 0.1, 0.2], rot=[0, 0, 22], k=0.15, color=B)
S.ell("dock", [-0.9, 1.53, 0], [0.12, 0.06, 0.06], rot=[0, 0, 25], k=0.07, color=B)
# ---- the neck: low out of the chest, forward and down, then up in a long curve to a head held level
npts = [[0.62, 1.52, 0, 0.21], [0.92, 1.48, 0, 0.16], [1.14, 1.56, 0, 0.13], [1.3, 1.78, 0, 0.11], [1.4, 2.04, 0, 0.1], [1.46, 2.28, 0, 0.095]]
if BA: npts = [[0.62, 1.5, 0, 0.22], [0.9, 1.46, 0, 0.17], [1.1, 1.54, 0, 0.14], [1.25, 1.75, 0, 0.12], [1.35, 1.98, 0, 0.11], [1.41, 2.2, 0, 0.1]]
S.ell("neckBase", [0.6, 1.5, 0], [0.25, 0.27, 0.2], rot=[0, 0, -10], k=0.1, color=B)
chain(S, "neck", npts, bone="neck", depth=1.25, k=0.08, color="@wool" if BA else B)
if BA:
    # the beard: dark wool hanging a hand's breadth and more under the throat, down the neck to the chest
    S.ell("beard", [0.84, 1.25, 0], [0.22, 0.17, 0.12], rot=[0, 0, 4], bone="neck", k=0.08, kc=0.05, color="@wool", fleece=True, hair=0.8)
    S.ell("beard2", [1.07, 1.33, 0.0], [0.15, 0.16, 0.1], rot=[0, 0, 20], bone="neck", k=0.08, kc=0.05, color="@wool", fleece=True, hair=0.8)
    S.ell("beard3", [1.22, 1.52, 0.0], [0.1, 0.13, 0.09], rot=[0, 0, 40], bone="neck", k=0.07, kc=0.05, color="@shag", fleece=True, hair=0.8)
    S.ell("poll", [1.43, 2.37, 0], [0.14, 0.09, 0.11], rot=[0, 0, 20], bone="head", k=0.04, kc=0.03, color="@shag", fleece=True, hair=0.8)
    S.ell("mane", [1.36, 2.18, 0], [0.12, 0.1, 0.08], rot=[0, 0, 70], bone="neck", k=0.05, kc=0.04, color="@shag", fleece=True, hair=0.8)
# ---- the head: a rounded brow over heavy-lidded eyes, a long muzzle, the split upper lip overhanging, the lower lip slack
hb = J["head"]["o"]
poll = [hb[0] - 0.08, hb[1] + 0.07, 0]
tip = [hb[0] + 0.52, hb[1] - 0.18, 0]   # (long: a camel's head is half a metre)
hf = Frame(poll, sub(tip, poll)); L = length(sub(tip, poll))
def H(t, h=0, z=0): return hf(t * L, h * L, z * L)
hr = hf.rot()
S.ell("cranium", H(0.18, -0.06), [0.2 * L, 0.21 * L, 0.2 * L], rot=hr, bone="head", k=0.04, color=B)
S.ell("brow", H(0.3, 0.05, 0.11), [0.1 * L, 0.06 * L, 0.06 * L], rot=hr, bone="head", k=0.025, color=B, mirror=True)
S.cone("face", H(0.3, -0.04), H(0.8, -0.06), 0.15 * L, 0.11 * L, bone="head", k=0.04, color=B)
S.ell("jaw", H(0.4, -0.18, 0.06), [0.24 * L, 0.11 * L, 0.06 * L], rot=hf.rot(-5), bone="head", k=0.03, color=B, mirror=True)
S.ell("lipU", H(0.9, -0.11, 0.035), [0.12 * L, 0.11 * L, 0.06 * L], rot=hf.rot(-12), bone="head", k=0.02, kc=0.008, color="@muzzle", mirror=True)
S.ell("lipL", H(0.8, -0.25), [0.13 * L, 0.06 * L, 0.075 * L], rot=hf.rot(-16), bone="head", k=0.025, color="@muzzle")
S.ell("nostril", H(0.92, -0.01, 0.06), [0.06 * L, 0.012 * L, 0.02 * L], rot=hf.rot(35), bone="head", k=0.004, kc=0.002, color="@nose", mirror=True)
eye = H(0.3, 0.02, 0.15)
eb = H(0.08, 0.04, 0.12)
ed = norm([-0.35, 0.8, 0.5])
S.ell("ear", add(eb, ed, 0.05), [0.018, 0.05, 0.035], rot=orient(ed), bone="earL", k=0.01, kc=0.004, color="@ear", mirror=True)
# ---- legs: long; the thighs held in to the body (a camel's stifle is free of the flank), knee and elbow pads, two toes on a broad pad
fx, fz = J["legFLu"]["o"][0], J["legFLu"]["o"][2]
kn = J["legFLl"]["o"][1]
hx, hz = J["legHLu"]["o"][0], J["legHLu"]["o"][2]
hk = J["legHLl"]["o"][1]
LG = "@leg"
CT = 1.25 if BA else 1.0   # (a bactrian's cannons: a quarter thicker)
# (audit 2026-11-07, user bug: the hind leg had a HOLE at the stifle -- the thigh's bottom, the gaskin's top and the ham's
#  foot met only at their rims, so the field opened right through the leg there -- and the legs read as bony slabs. Now
#  every leg is one continuous limb: round sections, each piece reaching well into the next, soft blends at the joints)
S.ell("arm", [fx - 0.04, 1.2, fz * 0.88], [0.12, 0.17, 0.1], rot=[0, 0, -15], bone="legFLu", k=0.08, color=B, mirror=True)
S.tube("forearm", [[fx - 0.03, 1.1, fz, 0.085], [fx - 0.015, 0.92, fz, 0.068], [fx, kn + 0.06, fz, 0.05], [fx, kn + 0.01, fz, 0.047]], bone="legFLu", k=0.05, color=LG, mirror=True)
S.ell("knee", [fx + 0.005, kn - 0.01, fz], [0.057, 0.06, 0.052], bone="legFLl", k=0.035, kc=0.012, color="@pad", mirror=True)
S.cone("cannon", [fx, kn - 0.02, fz], [fx + 0.01, 0.16, fz], 0.044 * CT, 0.037 * CT, bone="legFLl", k=0.03, color=LG, mirror=True)
S.ell("fetlock", [fx + 0.01, 0.15, fz], [0.047, 0.042, 0.042], bone="legFLl", k=0.03, color=LG, mirror=True)
S.cone("pastern", [fx + 0.01, 0.145, fz], [fx + 0.06, 0.06, fz], 0.037, 0.04, bone="legFLl", k=0.025, color=LG, mirror=True)
if BA:
    S.ell("sleeve", [fx - 0.01, 0.97, fz], [0.1, 0.18, 0.095], bone="legFLu", k=0.03, kc=0.03, color="@shag", fleece=True, hair=0.8, mirror=True)
S.ell("thigh", [hx + 0.03, 1.17, hz * 0.88], [0.17, 0.26, 0.125], rot=[0, 0, -10], bone="legHLu", k=0.1, color=B, mirror=True)
S.tube("gaskin", [[hx + 0.05, 1.08, hz * 0.95, 0.1], [hx + 0.01, 0.9, hz, 0.08], [hx - 0.03, hk + 0.14, hz, 0.058], [hx - 0.03, hk + 0.02, hz, 0.05]], bone="legHLu", k=0.06, color=LG, mirror=True)
ham(S, J, [0.24, 1.0], [0.06, 0.2], 0.095, 0.05, B, 0.07, zf=0.95)
S.ell("hock", [hx - 0.025, hk, hz], [0.056, 0.06, 0.05], bone="legHLl", k=0.035, color=LG, mirror=True)
S.sph("hockPt", [hx - 0.06, hk + 0.025, hz], 0.032, bone="legHLl", k=0.035, color=LG, mirror=True)
S.cone("hcannon", [hx - 0.022, hk - 0.02, hz], [hx + 0.01, 0.16, hz], 0.044 * CT, 0.037 * CT, bone="legHLl", k=0.03, color=LG, mirror=True)
S.ell("hfetlock", [hx + 0.01, 0.15, hz], [0.047, 0.042, 0.042], bone="legHLl", k=0.03, color=LG, mirror=True)
S.cone("hpastern", [hx + 0.01, 0.145, hz], [hx + 0.06, 0.06, hz], 0.037, 0.04, bone="legHLl", k=0.025, color=LG, mirror=True)
for tag, x0, z0 in (("", fx, fz), ("h", hx, hz)):
    bn = "footFL" if not tag else "footHL"
    # the pad: a thick round cushion (~0.18 m across), two short toes on its front with their nails
    S.ell(tag + "sole", [x0 + 0.06, 0.045, z0], [0.095, 0.045, 0.09], bone=bn, k=0.02, kc=0.006, color="@foot", mirror=True)
    for side, dz in (("o", 1), ("i", -1)):
        S.ell(tag + "toe" + side, [x0 + 0.12, 0.05, z0 + dz * 0.042], [0.05, 0.038, 0.04], bone=bn, k=0.012, kc=0.004, color="@foot", mirror=True)
        S.ell(tag + "nail" + side, [x0 + 0.165, 0.045, z0 + dz * 0.042], [0.016, 0.014, 0.016], bone=bn, k=0.003, kc=0.001, color="@nail", mirror=True)
# ---- the tail: thin, hanging to the hock, a tuft of dark hair at its end
t0 = J["tail"]["o"]
S.cone("tailDock", t0, add(t0, [-0.07, -0.16, 0]), 0.045, 0.032, bone="tail", k=0.04, color=B)
S.cone("tailStem", add(t0, [-0.07, -0.16, 0]), add(t0, [-0.1, -0.5, 0]), 0.03, 0.022, bone="tail", k=0.02, color=B)
S.ell("tailTuft", add(t0, [-0.11, -0.6, 0]), [0.04, 0.12, 0.035], rot=[0, 0, -4], bone="tail", k=0.025, color="@tuft", hair=0.9)
# (audit 2026-11-07) ticked fur on the coat, coarse wool on a bactrian's wool, shag and hump crowns
for q in S.shapes:
    if q.get("op") or "pat" in q: continue
    if q.get("color") in ("@body", "@leg", "@muzzle"): q["pat"] = "agouti"
    elif BA and q.get("color") in ("@wool", "@shag", "@humpc"): q["pat"] = "coarse"
keep = []
if BA:
    cols = {"pad": "#4e3624", "nose": "#2a1e16", "shag": "#4a321e", "humpc": "#82603e", "nail": "#2a2018", "tuft": "#2e2016", "body": "#9a7450", "leg": "#6a4a2e", "wool": "#5e4228"}
    about = "THE BACTRIAN CAMEL (2026-11-05, 2nd pass): heavier and lower than the dromedary -- legs 15% shorter (the rig re-made so: the body lowered, the legs shortened), the cannons a quarter thicker, the barrel broader; two conical, floppy humps, each leaning its own way under a lopsided mop of dark wool, the saddle dip between them where the rider sits; dark wool on the neck, a beard hanging under the throat to the chest, sleeves on the forearms, a mane on the poll, against a paler body; a long head, the split upper lip drooping; thick round pads; the tail hanging to the hock with its tuft"
else:
    cols = {"pad": "#8a6a44", "nose": "#4a3626", "nail": "#3a2a1a", "tuft": "#5a3e24"}
    about = "THE DROMEDARY (2026-11-05, 2nd pass): one long mound of a hump, rising behind the withers (the rider's seat, species.js saddle(), is on the withers before it: a Tuareg saddle's), peaking past the middle of the back and falling over the loin; the body narrow and shallow on long legs, the sternal pad under the chest; the neck low out of the chest, forward and down, then up in a long curve to a head carried level; a rounded brow over heavy-lidded eyes, small round ears, a long muzzle, the split upper lip overhanging the slack lower one, slit nostrils; knee pads, thighs held in close, two toes on broad flat pads; the tail kept"
upd = {"colors": cols, "!legs": O0["legs"], "!tail": O0["tail"]}
if BA:   # shorter legs: the body down 0.15, everything below 1.1 m pressed into 0.95 -- the shapes, and the rig with them
    FY = lambda y: y - 0.15 if y >= 1.1 else y * 0.95 / 1.1
    def mp(v): return [v[0], FY(v[1])] + list(v[2:])
    for q in S.shapes:
        for key in ("c", "a", "b"):
            if key in q: q[key] = R3(mp(q[key]))
        if "pts" in q: q["pts"] = [R3(mp(p[:3])) + [p[3]] for p in q["pts"]]
    eye = mp(eye); H0 = mp(H(0.3, -0.04, 0))
    O = O0
    for key, idx in (("rear", (1,)), ("front", (1,)), ("neck", (1, 4)), ("head", (1,)), ("muzzle", (1, 4)), ("ears", (1, 4)), ("eyes", (1,))):
        v = list(O[key])
        for i in idx: v[i] = round(FY(v[i]), 4)
        upd[key] = v
    lg = json.loads(json.dumps(O["legs"]))
    for k2 in ("front", "hind"): lg[k2][1] = round(FY(lg[k2][1]), 4); lg[k2][3] = round(lg[k2][3] * 0.95 / 1.1, 4)
    upd["!legs"] = lg
    tl = dict(O["tail"]); tl["c"] = [tl["c"][0], round(FY(tl["c"][1]), 4)]; upd["!tail"] = tl
    ex = json.loads(json.dumps(O["extras"]))
    for x in ex:
        for key in ("from", "to"):
            if key in x: x[key][1] = round(FY(x[key][1]), 4)
        if "ell" in x: x["ell"][1] = round(FY(x["ell"][1]), 4)
    upd["!extras"] = ex
    upd["mount"] = {**O["mount"], "h": round(O["mount"]["h"] - 0.15, 3)}
    upd["saddle"] = {"x": 0.18, "y": 1.725}   # (round 7: the saddle between the humps raised: the rider on its skin)
else:
    H0 = H(0.3, -0.04, 0)
sc = {"_about": about, "keep": keep, "mesh": {"tris": [8000, 2400], "cell": 0.016, "focus": {"head": 2, "legFLu": 1.6, "legFRu": 1.6, "legHLu": 1.6, "legHRu": 1.6}}, "shape": S.shapes,
      # (the bactrian's dark neck wool fading into the paler body over ~0.2 m at the shoulder, not stopping at a line:
      #  the engine's shade, run along x and only on the wool colour)
      **({"shade": {"on": "@wool", "up": [1, 0, 0], "at": 0.93 - J["body"]["o"][0], "k": 0.18, "back": "@wool", "belly": "@body", "mode": "mix", "tol": 0.05}} if BA else {}),
      "eyes": {"at": R3(eye), "from": R3(H0), "r": 0.024, "iris": "@eye", "pupil": "bar", "lid": "#3a2a1c", "sink": 0.45}}
print(write(name, sc, upd), len(S.shapes), "shapes")
