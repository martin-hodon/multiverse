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
                   "foot": "#4a4434", "horn": "#7c6c52" if not styr else "#76664a", "hornBase": "#5e5242" if not styr else "#5e4e38", "beak": "#3a3228", "nail": "#4e4536",
                   "frill": "#8a5a3a" if not styr else "#9a4a2a", "frillIn": "#b08a58" if not styr else "#c0804a",
                   "rim": "#4e3a28", "frillWin": "#5a3424", "head": "#78714f" if not styr else "#86704e", "eye": "#3a2a14", "lid": "#3a3426"})
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
    E("snout", [3.42 + fx * 0.6, 1.25, 0], [0.62 + fx, 0.36 + (0.05 if dia else 0), 0.24], "@head", bone="head", k=0.1, rot=[0, 0, -18], **sc)
    E("jaw", [3.25 + fx * 0.5, 0.98, 0], [0.55 + fx * 0.5, 0.18 + (0.03 if dia else 0), 0.25], "@head", bone="head", k=0.08, rot=[0, 0, -10], **sc)
    # the rostral: a narrow, laterally compressed upper beak arching down to a hooked point
    T("rostral", [[3.74 + fx, 1.24, 0, 0.11], [3.96 + fx, 1.16, 0, 0.09], [4.1 + fx, 1.0, 0, 0.068], [4.13 + fx, 0.86, 0, 0.048], [4.08 + fx, 0.76, 0, 0.034]],
      "@beak", bone="head", k=0.03, kc=0.008)
    E("rostralKeel", [3.97 + fx, 1.04, 0], [0.15, 0.16, 0.075], "@beak", bone="head", k=0.03, kc=0.008, rot=[0, 0, -38])
    # the predentary: the lower beak, a blade with a crisp edge closing under the hook
    S.tri("predentary", m([3.58 + fx, 0.9, 0]), m([3.62 + fx, 0.72, 0]), m([4.02 + fx, 0.78, 0]), 0.062 * s, "@beak", bone="head", k=0.03 * s, kc=0.008 * s)
    T("predentaryRoot", [[3.5 + fx, 0.86, 0, 0.12], [3.7 + fx, 0.82, 0, 0.08]], "@beak", bone="head", k=0.04, kc=0.01)
    # ======== pass 8: the horns and the frill as the fossil skull has them ========
    CELL = {"trike": 0.05, "styr": 0.036, "diablo": 0.032}[kind]
    RT = 0.72 * CELL / s           # (a radius, in this file's units, under which a horn is drawn as a smooth DETAIL lathe)
    HC = {"trike": ("#5a4c3a", "#2a221a"), "styr": ("#5e5040", "#241c14"), "diablo": ("#4a3e30", "#1e1812")}[kind]
    def lerp(a, b, t): return [a[i] + (b[i] - a[i]) * t for i in range(len(a))]
    def horn(id, pts, col="@horn", mirror=True, k=0.04):
        """a horn: its thick base in the field (blended into the bone it grows from), its thin outer part a smooth detail
        lathe (no grid aliasing, a real point) whose keratin darkens to the tip; the detail starts inside the base"""
        i = next((j for j, p in enumerate(pts) if p[3] < RT), len(pts))
        if i >= len(pts):   # (thick all the way: all field)
            T(id, pts, col, bone="head", k=k, kc=0.01, mirror=mirror); return
        a, b = pts[i - 1], pts[i]
        t = (a[3] - RT * 0.98) / max(a[3] - b[3], 1e-6); cut = lerp(a, b, min(max(t, 0), 1))
        T(id, pts[:i] + [cut[:3] + [RT * 0.98]], col, bone="head", k=k, kc=0.01, mirror=mirror)
        start = lerp(a, cut, 0.45)[:3] + [RT * 0.95]   # (inside the field part)
        S.tube("kTip" + id[0].upper() + id[1:], [m(start)] + [m(p[:3] + [min(p[3], RT * 0.95)]) for p in [cut] + pts[i:]], "@horn",
               bone="head", k=0.0, tip=HC[1], tipAt=0.25, **({"mirror": True} if mirror else {}))
    def bend(p0, d1, d2, ln, r0, r1, n=5, wob=0.0):
        """points along a curve from p0: leaving along d1, arriving along d2 (unit-ish), radius r0 -> r1; `wob` a small twist"""
        out = []
        for j in range(n):
            t = j / (n - 1)
            dd = [d1[q] * (1 - t) + d2[q] * t for q in range(3)]
            if j == 0: P_ = list(p0)
            else:
                L_ = math.sqrt(sum(v * v for v in dd)) or 1
                P_ = [out[-1][q] + dd[q] / L_ * ln / (n - 1) for q in range(3)]
                P_[2] += wob * math.sin(math.pi * t) * ln / (n - 1)
            out.append(P_ + [r0 + (r1 - r0) * t ** 0.85])
        return out
    # -- the jugal (cheek) horn: the epijugal, down and out (trike: back too, on a flared jugal; diablo: prominent)
    ej = {"trike": (0.3, 0.1), "styr": (0.2, 0.075), "diablo": (0.3, 0.1)}[kind]
    if kind == "trike":
        E("jugalFlare", [2.95, 1.05, 0.42], [0.26, 0.2, 0.12], "@head", bone="head", k=0.07, rot=[0, -25, 0], mirror=True, **sc)
        E("squamStep", [2.62, 1.55, 0.5], [0.3, 0.1, 0.08], "@head", bone="head", k=0.07, rot=[0, -30, 30], mirror=True, **sc)
    horn("epijugal", bend([2.98, 1.02, 0.44], [0.1, -0.6, 0.8], [-0.3, -0.7, 0.65], ej[0], ej[1], 0.012, n=4), col="@hornBase", k=0.03)
    # -- the postorbital (brow) horns
    E("hornRoot", [3.0, 1.8, 0.27], [0.22, 0.14, 0.16] if kind == "trike" else [0.16, 0.12, 0.14], "@head", bone="head", k=0.06, mirror=True, **sc)
    if kind == "trike":   # ~1 m, a broad oval base, curving forward and a little up, a slight inward twist to a blunt-sharp tip
        horn("browHorn", bend([3.0, 1.82, 0.27], [0.55, 0.85, 0.14], [1.0, 0.05, -0.12], 1.15, 0.17, 0.016, n=6, wob=0.05))
    elif kind == "styr":  # short stubs on bosses
        E("browBoss", [3.04, 1.88, 0.27], [0.12, 0.1, 0.11], "@hornBase", bone="head", k=0.05, kc=0.01, mirror=True)
    else:                 # diablo: short, up and out over the eyes
        horn("browHorn", bend([3.02, 1.82, 0.27], [0.1, 0.9, 0.45], [-0.1, 0.8, 0.6], 0.5, 0.12, 0.014, n=5))
    # -- the nasal horn
    if kind == "styr":    # tall (~57 cm), straight, leaning a little back, off a deep nasal boss
        E("noseRoot", [3.56, 1.42, 0], [0.24, 0.16, 0.17], "@head", bone="head", k=0.07, **sc)
        horn("noseHorn", bend([3.6, 1.42, 0], [-0.12, 1, 0], [-0.14, 1, 0], 0.88, 0.12, 0.014, n=5), mirror=False)
    elif kind == "trike": # short and thick
        horn("noseHorn", bend([3.66, 1.4, 0], [0.3, 1, 0], [0.45, 1, 0], 0.4, 0.14, 0.02, n=4), mirror=False)
    else:                 # diablo: a low boss with a small point
        E("noseRoot", [3.5, 1.42, 0], [0.2, 0.13, 0.15], "@head", bone="head", k=0.07, **sc)
        horn("noseHorn", bend([3.52, 1.48, 0], [0.2, 1, 0], [0.35, 1, 0], 0.2, 0.1, 0.02, n=3), mirror=False)
    # ---- the frill: the parietal (a midline bar and two side sheets) and the squamosals along its sides; rising from
    #      the skull roof behind the orbits, swept back, its top a little dished; centrosaurs with two parietal windows
    tilt = {"trike": 62, "styr": 60, "diablo": 52}[kind]
    th = math.radians(tilt)
    Y = [-math.sin(th), math.cos(th)]; N = [math.cos(th), math.sin(th)]
    base = [2.85, 1.75]
    H, W = {"trike": (0.78, 1.08), "styr": (0.78, 0.95), "diablo": (0.86, 0.72)}[kind]   # (diablo's tall and narrow)
    ctr = [base[0] + Y[0] * 0.93 * H, base[1] + Y[1] * 0.93 * H]
    RIM, TH = 0.06, (0.06 if kind == "trike" else 0.065)
    def at(yv, z, nv=0.0):
        return [ctr[0] + Y[0] * yv + N[0] * nv, ctr[1] + Y[1] * yv + N[1] * nv, z]
    def rimPt(ang, f=1.0, nv=0.012):
        a_ = math.radians(ang)
        tri_ = 1.0 - (0.18 * abs(math.sin(a_)) * max(0, math.cos(a_)) if kind == "diablo" else 0)   # (a triangular frill)
        return at((H - RIM) * f * math.cos(a_), (W - RIM) * f * math.sin(a_) * tri_, nv)
    def radial(ang):
        a_ = math.radians(ang); return [Y[0] * math.cos(a_), Y[1] * math.cos(a_), math.sin(a_)]
    E("frill", [*ctr, 0], [TH, H - RIM * 0.8, (W - RIM * 0.8) * (0.93 if kind == "diablo" else 1)], "@frill", bone="head", k=0.06, kc=0.02, rot=[0, 0, tilt])
    E("frillBase", [base[0] + Y[0] * 0.3, base[1] + Y[1] * 0.3, 0], [0.24, 0.46, 0.6], "@head", bone="head", k=0.22, kc=0.08, rot=[0, 0, tilt], **sc)
    E("frillRoot", [base[0] - math.sin(math.radians(tilt - 18)) * 0.42 * H, base[1] + math.cos(math.radians(tilt - 18)) * 0.42 * H, 0],
      [0.1, 0.45 * H, 0.66 * W], "@frill", bone="head", k=0.16, kc=0.06, rot=[0, 0, tilt - 18])
    E("frillIn", [*at(0.05 * H, 0, TH * 0.2)][:3], [TH * 0.7, H * 0.6, W * 0.62], "@frillIn", bone="head", k=0.02, kc=0.03, rot=[0, 0, tilt])
    T("frillRim", [[*rimPt(g), RIM] for g in range(-126, 127, 12)], "@frill", bone="head", k=0.04, kc=0.015)
    # the parietal's midline bar: a low ridge up the middle of the shield
    T("parietalBar", [[*at(yv * H, 0, TH * 0.45), TH * (1.05 if kind != "trike" else 0.8)] for yv in (-0.45, 0.0, 0.45, 0.86)], "@frill", bone="head", k=0.05, kc=0.02)
    if kind != "trike":   # the two parietal fenestrae: skin-covered windows, darker, either side of the bar
        E("fenestra", [*at(0.22 * H, 0.4 * W, TH * 0.25)][:3], [TH * 0.62, 0.3 * H, 0.22 * W], "@frillWin", bone="head", k=0.02, kc=0.035, rot=[0, 0, tilt], mirror=True)
    # the epoccipitals: discrete low triangles along the margin (epiparietals on the parietal, episquamosals along the sides)
    def epo(id, ang, L, wdeg, rr):
        a0, a1 = rimPt(ang - wdeg / 2, 1.0, 0.0), rimPt(ang + wdeg / 2, 1.0, 0.0)
        rd = radial(ang); tipp = rimPt(ang, 1.0, 0.0); tipp = [tipp[0] + rd[0] * (RIM + L), tipp[1] + rd[1] * (RIM + L), tipp[2] + rd[2] * (RIM + L)]
        S.tri(id, m(a0), m(a1), m(tipp), max(rr * s, 0.62 * CELL), "@rim", bone="head", k=0.02 * s, kc=0.008 * s, **({"mirror": True} if ang > 0.5 else {}))
    if kind == "trike":   # 7 per side and one on the midline, low, merging into the edge
        for i, g in enumerate([0] + [16 * j for j in range(1, 8)]):
            epo(f"epo{i}", g, 0.12 if g < 90 else 0.09, 14, 0.04)
    elif kind == "styr":  # the squamosal's small points down the sides
        for i, g in enumerate([84, 98, 112]):
            epo(f"epo{i}", g, 0.07, 11, 0.04)
    else:                 # diablo: small curved hooks along the rim
        for i, g in enumerate([36, 52, 68, 84, 100]):
            p0 = rimPt(g, 1.0, 0.0); rd = radial(g)
            horn(f"hook{i}", bend(p0, rd, [rd[0] * 0.3 + N[0] * 0.8, rd[1] * 0.3 + N[1] * 0.8, rd[2] * 0.3], 0.16, 0.075, 0.012, n=4), col="@rim", k=0.03)
    # the parietal processes, grown out of the margin (each from inside the plate, through the rim)
    def proc(id, ang, ln, r0, d1, d2, n=5, col="@horn"):
        p0 = rimPt(ang, 0.8, 0.0); p1 = rimPt(ang, 1.0, 0.0)
        pts = [p0 + [r0 * 1.05]] + bend(p1, d1, d2, ln, r0, 0.012, n=n)
        horn(id, pts, col=col)
    UP = [0, 1, 0]
    def mix(*ws):
        v = [0, 0, 0]
        for w, d_ in ws: v = [v[q] + w * d_[q] for q in range(3)]
        return v
    if kind == "styr":
        Nn = [N[0], N[1], 0]
        for i, (g, ln, r0) in enumerate([(-5, 0.1, 0.06), (-13, 0.12, 0.065)]):        # P1, P2: little hooks by the midline, curling forward
            rd = radial(g); proc(f"hookP{i + 1}", g, ln, r0, rd, mix((0.3, rd), (0.9, Nn)), n=4, col="@rim")
        rd = radial(-22); proc("spikeP3", -22, 0.3, 0.085, mix((1, rd), (0.3, UP)), mix((0.9, rd), (0.5, UP)), n=4)
        # P4-P6: the long spikes off the rear margin -- each a SEPARATE horn: its own boss sunk into the rim, a shaft
        # blended by a tiny k only (no smooth-min bridging its neighbours: no web), its outer part a detail lathe;
        # spaced along the rim and fanning so there is clear air between them along their whole free length
        LS = []
        for i, (g, ln, fan) in enumerate([(-30, 0.84, 0.1), (-48, 0.86, 0.24), (-66, 0.76, 0.4)]):
            rd = radial(g * 0.45); p1 = rimPt(g, 1.0, 0.0)
            d1 = mix((0.85, rd), (0.32, UP), (-0.08, Nn), (-fan * 0.5, [0, 0, 1]))
            d2 = mix((0.7, rd), (0.5, UP), (-0.15, Nn), (-fan, [0, 0, 1]))
            E(f"spikeBoss{i + 4}", p1, [0.1, 0.1, 0.1], "@hornBase", bone="head", k=0.012, kc=0.01, mirror=True)
            pts = bend(p1, d1, d2, ln, 0.085, 0.012, n=6)
            horn(f"spikeP{i + 4}", pts, k=0.008)
            LS.append(pts)
        def clear(A, B):   # the least air between two spikes' surfaces beyond their bosses (metres)
            best = 9
            for pa in A[1:]:
                for pb in B[1:]:
                    dd = math.dist(pa[:3], pb[:3]) - pa[3] - pb[3]; best = min(best, dd)
            return best * s
        print("  styraco spikes: clearance", [round(clear(LS[j], LS[j + 1]), 3) for j in range(2)],
              "tip spread", [round(math.dist(LS[j][-1][:3], LS[j + 1][-1][:3]) * s, 3) for j in range(2)],
              "boss gap", [round((math.dist(LS[j][0][:3], LS[j + 1][0][:3]) - 0.2) * s, 3) for j in range(2)])
    if dia:               # two long, slightly curved spikes rising off the top of the frill
        Nn = [N[0], N[1], 0]; rd = radial(-12)
        proc("spikeP1", -12, 0.9, 0.14, mix((0.5, rd), (0.8, UP), (-0.25, [0, 0, 1])), mix((0.1, rd), (1.0, UP), (-0.5, [0, 0, 1]), (0.15, Nn)), n=6)
    for p in S:   # (the head carried higher: its shapes lifted with its bone)
        if p.get("bone") == "head":
            dy = HY * s
            for key in ("c", "a", "b"):
                if key in p: p[key][1] += dy
            if "pts" in p:
                for q in p["pts"]: q[1] += dy
    pass   # (horn tips are details now: no floor)
    keep = []
    d["sculpt"] = {
        "_about": "x forward, y up, z left, metres; each shape rides the bone it names; `mirror` makes the right one from the left",
        "keep": keep,
        "mesh": {"tris": [9000, 2800], "focus": {"head": 6}, "cell": CELL},
        "shape": [fix_order(p) for p in S],
        "eyes": {"at": m([3.06, 1.68 + HY, 0.3]), "from": m([2.85, 1.62 + HY, 0]), "r": 0.048 * s, "iris": "@eye", "pupil": "round", "lid": "@lid"},
    }
    d["sculpt"]["shade"] = {"back": 0.8, "belly": 1.12, "low": 0.96, "on": "@body"}
    save(P, d)
    print(P, len(S), "shapes")

build("dinosaurs/triceratops", 1.0, "trike")
build("dinosaurs/styracosaurus", 0.65, "styr")
build("dinosaurs/diabloceratops", 0.55, "diablo", src="dinosaurs/styracosaurus")
