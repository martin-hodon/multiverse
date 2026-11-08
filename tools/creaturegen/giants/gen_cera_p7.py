import math, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import *

def V(*a): return list(a)

def build(P, s, kind, src=None):
    styr = kind != "trike"
    d = load(src or P)
    m = lambda v: [x * s for x in v]            # a point at this size
    mr = lambda v: [x * s for x in v]
    if styr:
        d["_about"] = ("STYRACOSAURUS ALBERTENSIS (sculpt overlay, 2026-11-05): a 5.5 m centrosaurine -- the ceratopsian build of "
                       "the triceratops at .65, its own head: a long upright nose horn, brow knobs, a short frill with two holes "
                       "(the parietal fenestrae) and six long spikes radiating back from its rim, small epoccipital points, a deep "
                       "narrow snout to a parrot beak. Countershaded, scaled; the frill flushed red.")
    else:
        d["_about"] = ("TRICERATOPS HORRIDUS (sculpt overlay, 2026-11-05, after Hartman's skeletal): 8.7 m, the hips 1.8 m "
                       "up -- a broad barrel highest at the hips, sloping to the shoulders; columnar hind legs, shorter fore legs "
                       "with the elbows out; a 2.3 m head: a solid frill swept up and back, rimmed with epoccipitals, two metre-long "
                       "brow horns curving forward, a short nose horn, a deep narrow snout to a parrot beak, epijugal points on the "
                       "cheeks; a short tail held off the ground. Countershaded, scaled; the frill two-toned.")
    d["rear"] = m([-0.9, 2.1, 0, 1.0, 0.6, 0.95])
    d["front"] = m([1.0, 1.45, 0, 0.9, 0.55, 0.95])
    HY = 0.38
    d["neck"] = m([1.7, 1.6, 0, 2.5, 1.55 + HY, 0, 0.6, 0.5])
    d["head"] = m([2.65, 1.55 + HY, 0, 0.55])
    d["eyes"] = m([3.05, 1.68 + HY, 0.33, 0.05])
    d["legs"] = {"front": m([1.25, 1.15, 0.7, 0.55]), "hind": m([-1.15, 1.8, 0.66, 0.95]), "radii": mr([0.36, 0.28, 0.23]),
                 "foot": mr([0.28, 0.13, 0.28]), "kneeH": 1, "kneeF": -1}
    # tail: its root on the rump, drooping a little to the tip (an arc of R 6 from its top)
    R = 6 * s
    d["tail"] = {"c": m([-1.75, 2.2 - 6]), "R": R, "a0": 1.5708, "a1": 1.5708 + 0.3754, "r1": 0.55 * s, "r2": 0.04 * s,
                 "n": 6, "sway": 9, "speed": 0.35}
    d.pop("pat", None); d.pop("patOn", None)
    d["c"].update({"back": "#5d5a3e" if not styr else "#66553a", "body": "#736d4e" if not styr else "#7d6848",
                   "belly": "#aa9e7a" if not styr else "#b09a76", "leg": "#666046" if not styr else "#6d5c42",
                   "foot": "#4a4434", "horn": "#b3a586" if not styr else "#76664a", "hornBase": "#7a6c54" if not styr else "#5e4e38", "beak": "#3a3228", "nail": "#4e4536",
                   "frill": "#8a5a3a" if not styr else "#9a4a2a", "frillIn": "#b08a58" if not styr else "#c0804a",
                   "rim": "#4e3a28", "head": "#78714f" if not styr else "#86704e", "eye": "#3a2a14", "lid": "#3a3426"})
    if kind == "diablo":
        d["name"] = "diabloceratops"
        d["_about"] = ("DIABLOCERATOPS EATONI (sculpt overlay, 2026-11-05): a 5.5 m early centrosaurine of the Late Cretaceous of "
                       "Utah (Wahweap Formation) -- the ceratopsian build at .65; its devil's horns: two long spikes curving up and out "
                       "from the top of the frill, small curved hooks along the rim; big brow horns pointing up and out over the eyes, "
                       "a low nose horn, a deep short face to a parrot beak. Countershaded slate-brown, the frill deep maroon with an "
                       "ochre flush, the horns dark.")
        d["c"].update({"back": "#4a4638", "body": "#68624e", "belly": "#b2a688", "leg": "#5a5442", "foot": "#3e3a2e",
                       "horn": "#4e4434", "hornBase": "#3a3226", "beak": "#3e362c", "frill": "#6a2a22", "frillIn": "#b07a34",
                       "rim": "#2e221a", "head": "#70684f"})
    FR = {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.45 * s}
    sc = {"pat": "scales", "frame": FR}
    S = Shapes()
    E = lambda id, c, r, col, **kw: S.ell(id, m(c), mr(r), col, **{**kw, **({"k": kw["k"] * s} if "k" in kw else {}), **({"kc": kw["kc"] * s} if "kc" in kw else {})})
    C = lambda id, a, b, ra, rb, col, **kw: S.cone(id, m(a), m(b), ra * s, rb * s, col, **{**kw, **({"k": kw["k"] * s} if "k" in kw else {})})
    T = lambda id, pts, col, **kw: S.tube(id, [m(p) for p in pts], col, **{**kw, **({"k": kw["k"] * s} if "k" in kw else {}), **({"kc": kw["kc"] * s} if "kc" in kw else {})})
    # ---- trunk: a broad barrel, the hips its highest point
    E("barrel", [-0.1, 1.76, 0], [1.75, 0.72, 0.85], "@body", k=0.2, rot=[0, 0, -8], **sc)
    E("hips", [-0.9, 2.15, 0], [0.95, 0.52, 0.72], "@back", k=0.18, kc=0.14, **sc)
    E("spine", [-0.2, 2.28, 0], [1.6, 0.25, 0.5], "@back", k=0.18, kc=0.14, rot=[0, 0, -9], **sc)
    E("chest", [1.05, 1.45, 0], [0.8, 0.6, 0.74], "@body", k=0.16, **sc)
    E("belly", [0.0, 1.2, 0], [1.3, 0.3, 0.76], "@belly", k=0.16, kc=0.12, rot=[0, 0, -5], **sc)
    # ---- tail
    T("tail", [[-1.7, 2.12, 0, 0.38], [-2.35, 1.98, 0, 0.26], [-3.0, 1.76, 0, 0.15], [-3.6, 1.52, 0, 0.07], [-3.9, 1.42, 0, 0.03]],
      "@body", bone="tail", k=0.14, **sc)
    T("tailTop", [[-1.6, 2.3, 0, 0.2], [-2.35, 2.1, 0, 0.12], [-2.95, 1.84, 0, 0.06]], "@back", bone="tail", k=0.12, kc=0.1, **sc)
    T("tailBelly", [[-1.7, 1.95, 0, 0.24], [-2.4, 1.86, 0, 0.14], [-2.95, 1.68, 0, 0.07]], "@belly", bone="tail", k=0.12, kc=0.1, **sc)
    # ---- fore legs: the elbow out and back, a short hand
    E("scapula", [1.15, 1.58, 0.62], [0.36, 0.52, 0.22], "@body", bone="legFLu", k=0.12, rot=[0, 0, 25], mirror=True, **sc)
    C("humerus", [1.25, 1.17, 0.7], [1.12, 0.62, 0.86], 0.27, 0.2, "@body", bone="legFLu", k=0.09, mirror=True, **sc)
    E("triceps", [1.05, 0.9, 0.8], [0.22, 0.28, 0.18], "@body", bone="legFLu", k=0.07, mirror=True, **sc)
    E("elbow", [1.1, 0.64, 0.88], [0.17, 0.15, 0.16], "@leg", bone="legFLu", k=0.06, mirror=True, **sc)
    C("forearm", [1.12, 0.62, 0.86], [1.27, 0.2, 0.74], 0.19, 0.14, "@leg", bone="legFLl", k=0.07, mirror=True, **sc)
    E("hand", [1.3, 0.1, 0.72], [0.22, 0.1, 0.2], "@foot", bone="footFL", k=0.05, mirror=True, **sc)
    # ---- hind legs: a column, knee forward
    E("thigh", [-1.1, 1.52, 0.6], [0.46, 0.62, 0.3], "@body", bone="legHLu", k=0.14, rot=[0, 0, 10], mirror=True, **sc)
    E("knee", [-1.06, 0.92, 0.66], [0.25, 0.22, 0.24], "@leg", bone="legHLu", k=0.08, mirror=True, **sc)
    C("shank", [-1.1, 0.9, 0.66], [-1.17, 0.22, 0.66], 0.24, 0.16, "@leg", bone="legHLl", k=0.07, mirror=True, **sc)
    E("foot", [-1.08, 0.11, 0.66], [0.3, 0.11, 0.24], "@foot", bone="footHL", k=0.05, mirror=True, **sc)
    for i, a in enumerate([-42, -14, 14, 42]):      # (four hind digits, three hoofed fore ones: short toes, blunt hooves)
        t = math.radians(a); ux, uz = math.cos(t), math.sin(t)
        E(f"toe{i}", [-1.08 + 0.24 * ux, 0.08, 0.66 + 0.2 * uz], [0.12, 0.075, 0.08], "@foot", bone="footHL", k=0.03, rot=[0, -a, 0], mirror=True, **sc)
        E(f"hoof{i}", [-1.08 + 0.34 * ux, 0.05, 0.66 + 0.27 * uz], [0.07, 0.05, 0.075], "@nail", bone="footHL", k=0.015, kc=0.005, rot=[0, -a, 0], mirror=True)
        if i < 3:
            t = math.radians([-38, 0, 38][i]); ux, uz = math.cos(t), math.sin(t)
            E(f"ftoe{i}", [1.3 + 0.17 * ux, 0.08, 0.72 + 0.16 * uz], [0.1, 0.07, 0.07], "@foot", bone="footFL", k=0.03, rot=[0, -[-38, 0, 38][i], 0], mirror=True, **sc)
            E(f"fhoof{i}", [1.3 + 0.26 * ux, 0.05, 0.72 + 0.23 * uz], [0.065, 0.045, 0.065], "@nail", bone="footFL", k=0.015, kc=0.005, rot=[0, -[-38, 0, 38][i], 0], mirror=True)
    # ---- neck, short, under the frill
    T("neck", [[1.45, 1.58, 0, 0.62], [2.05, 1.74, 0, 0.52], [2.5, 1.86, 0, 0.45]], "@body", bone="neck", k=0.14, **sc)
    E("dewlap", [2.05, 1.35, 0], [0.5, 0.3, 0.42], "@belly", bone="neck", k=0.12, kc=0.1, **sc)
    # ---- the head
    dia = kind == "diablo"
    fx = -0.14 if dia else 0.0     # (diabloceratops: a deep, short face)
    E("cranium", [2.85, 1.48, 0], [0.5, 0.42, 0.42], "@head", bone="head", k=0.12, **sc)
    E("jugal", [2.95, 1.15, 0.36], [0.3, 0.25, 0.12], "@head", bone="head", k=0.08, mirror=True, **sc)
    C("epijugal", [3.0, 1.02, 0.44], [3.05, 0.86, 0.56], 0.09, 0.035, "@hornBase", bone="head", k=0.03, mirror=True)
    E("snout", [3.42 + fx * 0.6, 1.25, 0], [0.62 + fx, 0.36 + (0.05 if dia else 0), 0.24], "@head", bone="head", k=0.1, rot=[0, 0, -18], **sc)
    E("jaw", [3.25 + fx * 0.5, 0.98, 0], [0.55 + fx * 0.5, 0.18 + (0.03 if dia else 0), 0.25], "@head", bone="head", k=0.08, rot=[0, 0, -10], **sc)
    # the rostral: a narrow, laterally compressed upper beak arching down to a hooked point
    T("rostral", [[3.74 + fx, 1.24, 0, 0.11], [3.96 + fx, 1.16, 0, 0.09], [4.1 + fx, 1.0, 0, 0.068], [4.13 + fx, 0.86, 0, 0.048], [4.08 + fx, 0.76, 0, 0.034]],
      "@beak", bone="head", k=0.03, kc=0.008)
    E("rostralKeel", [3.97 + fx, 1.04, 0], [0.15, 0.16, 0.075], "@beak", bone="head", k=0.03, kc=0.008, rot=[0, 0, -38])
    # the predentary: the lower beak, a blade with a crisp edge closing under the hook
    S.tri("predentary", m([3.58 + fx, 0.9, 0]), m([3.62 + fx, 0.72, 0]), m([4.02 + fx, 0.78, 0]), 0.062 * s, "@beak", bone="head", k=0.03 * s, kc=0.008 * s)
    T("predentaryRoot", [[3.5 + fx, 0.86, 0, 0.12], [3.7 + fx, 0.82, 0, 0.08]], "@beak", bone="head", k=0.04, kc=0.01)
    E("hornRoot", [3.02, 1.8, 0.27], [0.17, 0.13, 0.15], "@head", bone="head", k=0.06, mirror=True, **sc)
    if kind == "styr":     # a long straight nose horn, thick at the base; small brow knobs
        T("noseHorn", [[3.6 + 0.24 * t, 1.4 + 0.98 * t, 0, r] for t, r in [(0, 0.17), (0.4, 0.115), (0.75, 0.07), (1.0, 0.035)]], "@horn", bone="head", k=0.04, kc=0.008)
        E("noseRoot", [3.58, 1.42, 0], [0.2, 0.12, 0.16], "@head", bone="head", k=0.06, **sc)
        E("browKnob", [3.05, 1.86, 0.27], [0.11, 0.1, 0.1], "@hornBase", bone="head", k=0.05, kc=0.01, mirror=True)
    elif dia:              # a low nose horn; big brow horns up and out over the eyes
        C("noseHorn", [3.56, 1.42, 0], [3.64, 1.64, 0], 0.12, 0.05, "@horn", bone="head", k=0.04, kc=0.008)
        T("browHorn", [[3.02, 1.8, 0.27, 0.14], [3.08, 2.1, 0.36, 0.105], [3.1, 2.38, 0.46, 0.07], [3.05, 2.6, 0.53, 0.035]],
          "@horn", bone="head", k=0.04, kc=0.01, mirror=True)
    else:                  # a short nose horn; two metre-long brow horns curving forward and a little up
        C("noseHorn", [3.68, 1.42, 0], [3.8, 1.8, 0], 0.13, 0.035, "@horn", bone="head", k=0.04, kc=0.008)
        T("browHorn", [[3.02, 1.8, 0.27, 0.165], [3.33, 2.13, 0.33, 0.115], [3.63, 2.38, 0.38, 0.072], [3.95, 2.48, 0.4, 0.035]],
          "@horn", bone="head", k=0.04, kc=0.01, mirror=True)
    # ---- the frill: the parietal-squamosal shield, ONE solid plate grown out of the skull roof (thick at its base), a
    #      rolled rim round it (thicker than the plate: the top reads dished, the edge a smooth curve, not a thin aliased
    #      slab), the epoccipitals bumps ON that rim, the spikes grown out of it (each tube starting inside the plate)
    tilt = 62 if kind == "trike" else 60
    th = math.radians(tilt)
    Y = [-math.sin(th), math.cos(th)]; N = [math.cos(th), math.sin(th)]
    base = [2.85, 1.75]
    H, W = {"trike": (0.8, 1.1), "styr": (0.78, 0.95), "diablo": (0.74, 0.92)}[kind]
    ctr = [base[0] + Y[0] * 0.93 * H, base[1] + Y[1] * 0.93 * H]
    RIM, TH = 0.06, (0.06 if kind == "trike" else 0.065)   # (plate 12 / 8.5 cm thick; the rim 12 / 8 cm round)
    def at(yv, z, nv=0.0):   # a point on the shield: yv along it, z across, nv off its top face
        return [ctr[0] + Y[0] * yv + N[0] * nv, ctr[1] + Y[1] * yv + N[1] * nv, z]
    def rimPt(ang, f=1.0, nv=0.012):   # on the rim's centre line (ang 0: the top of the shield; +-90: its sides)
        a_ = math.radians(ang); return at((H - RIM) * f * math.cos(a_), (W - RIM) * f * math.sin(a_), nv)
    E("frill", [*ctr, 0], [TH, H - RIM * 0.8, W - RIM * 0.8], "@frill", bone="head", k=0.06, kc=0.02, rot=[0, 0, tilt])
    E("frillBase", [base[0] + Y[0] * 0.3, base[1] + Y[1] * 0.3, 0], [0.24, 0.46, 0.6], "@head", bone="head", k=0.22, kc=0.08, rot=[0, 0, tilt], **sc)
    # (it rises from the skull roof in a curve: a steeper, thicker root blended into the swept-back plate)
    E("frillRoot", [base[0] - math.sin(math.radians(tilt - 18)) * 0.42 * H, base[1] + math.cos(math.radians(tilt - 18)) * 0.42 * H, 0],
      [0.1, 0.45 * H, 0.66 * W], "@frill", bone="head", k=0.16, kc=0.06, rot=[0, 0, tilt - 18])
    E("frillIn", [*at(0.05 * H, 0, TH * 0.2)][:3], [TH * 0.7, H * 0.6, W * 0.62], "@frillIn", bone="head", k=0.02, kc=0.03, rot=[0, 0, tilt])
    T("frillRim", [[*rimPt(g), RIM] for g in range(-126, 127, 12)], "@frill", bone="head", k=0.04, kc=0.015)   # (frill-coloured: edge-on it is no dark log)
    # epoccipitals: a scalloped edge of bumps sitting on the rim
    if kind == "trike": epos = list(range(-120, 121, 12))
    elif kind == "styr": epos = [g for g in range(-120, 121, 12) if abs(g) >= 60]
    else: epos = []
    for i, g in enumerate(epos):
        if g < 0: continue
        p = rimPt(g, 1.0 + 0.6 * RIM / H, 0.0)
        E(f"epo{i}", p, [0.06, 0.085, 0.085], "@rim", bone="head", k=0.025, kc=0.01, rot=[0, 0, tilt], **({"mirror": True} if g > 0 else {}))
    def spike(id, ang, ln, up, out, r0, curl=0.0):
        """a spike grown out of the margin: from inside the plate, through the rim, tapering out and curving"""
        a_ = math.radians(ang)
        rad = [Y[0] * math.cos(a_), Y[1] * math.cos(a_), math.sin(a_)]
        dvec = [rad[0] * (1 - up) + up * 0.0 - N[0] * 0.15, rad[1] * (1 - up) + up * 1.0 - N[1] * 0.15, rad[2] + out]
        L = math.sqrt(sum(v * v for v in dvec)); dvec = [v / L for v in dvec]
        r0p, r1p = rimPt(ang, 0.78, 0.0), rimPt(ang, 1.0, 0.0)
        pts = [[*r0p, r0 * 1.05], [*r1p, r0]]
        for t, rr in [(0.35, 0.72), (0.7, 0.45), (1.0, 0.24)]:
            c_ = curl * t * t
            pts.append([r1p[0] + dvec[0] * ln * t, r1p[1] + dvec[1] * ln * t + c_, r1p[2] + dvec[2] * ln * t + abs(c_) * math.copysign(0.6, ang), r0 * rr])
        T(id, pts, "@horn", bone="head", k=0.04, kc=0.012, mirror=True)
    if kind == "styr":   # six long parietal spikes, the middle pair longest, sweeping up and back and a little out; short side ones
        for j, (g, ln, out) in enumerate([(-12, 0.82, 0.02), (-30, 0.78, 0.08), (-48, 0.62, 0.15)]):
            spike(f"spike{j}", g, ln, 0.3, -out, 0.13)
        for j, g in enumerate([-66, -84]):
            spike(f"sideSpike{j}", g, 0.22, 0.0, -0.05, 0.085)
    if dia:              # the devil's horns: two long spikes off the top curving up and out; small curved hooks along the rim
        spike("spike0", -14, 0.86, 0.75, -0.55, 0.14, curl=0.12)
        for j, g in enumerate([-38, -56, -74, -92, -110]):
            spike(f"hook{j}", g, 0.17, 0.0, 0.0, 0.08, curl=0.06)
    for p in S:   # (the head carried higher: its shapes lifted with its bone)
        if p.get("bone") == "head":
            dy = HY * s
            for key in ("c", "a", "b"):
                if key in p: p[key][1] += dy
            if "pts" in p:
                for q in p["pts"]: q[1] += dy
    floorR(S, ("browHorn", "noseHorn", "spike", "sideSpike", "hook", "epijugal"), 0.032 * s)
    keep = []
    d["sculpt"] = {
        "_about": "x forward, y up, z left, metres; each shape rides the bone it names; `mirror` makes the right one from the left",
        "keep": keep,
        "mesh": {"tris": [9000, 2800], "focus": {"head": 6}, **({"cell": 0.05} if kind == "trike" else {})},
        "shape": [fix_order(p) for p in S],
        "eyes": {"at": m([3.06, 1.68 + HY, 0.3]), "from": m([2.85, 1.62 + HY, 0]), "r": 0.048 * s, "iris": "@eye", "pupil": "round", "lid": "@lid"},
    }
    d["sculpt"]["shade"] = {"back": 0.8, "belly": 1.12, "low": 0.96, "on": "@body"}
    save(P, d)
    print(P, len(S), "shapes")

build("dinosaurs/triceratops", 1.0, "trike")
build("dinosaurs/styracosaurus", 0.65, "styr")
build("dinosaurs/diabloceratops", 0.65, "diablo", src="dinosaurs/styracosaurus")
