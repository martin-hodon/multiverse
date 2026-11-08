# gen.py (2026-11-08): the big NORTHERN UNGULATES -- moose, American bison, Alpine ibex -- written from scratch as
# sculpted rig animals (the moose and the ibex on the deer frame, creatures/frames/deer; the bison a cattle rig of its
# own, the ox's plan). Each species' whole sculpt: trunk, neck and head by hand, the LEGS mapped off the chamois'
# (ulib.legs_from: one cloven-hoofed leg modelled once), the EARS mapped off another species' `fin` ear (ulib.ear_onto),
# the eye put on the skin by a ray; then the SHARP parts -- the moose's palmate antlers (two `fin` palms a side rooted
# along a flattened `horn` beam, every tine a `horn` on a palm's rim: sharp/caribou.py's way), the bison's and the
# ibex's horns (`horn`s, the ibex's with its knobs in the centreline: radius and aspect raised every 5 cm), the moose's
# bell and the ibex's beard (`fin` sheets on the midline) -- their roots sunk in the field (plib.sink_horns).
#   python3 tools/creaturegen/ungulates/gen.py [moose bison ibex]
# It writes assets/creatures/mammals/<name>.json whole (nothing else made them: re-running is safe) and lists the
# species in assets/index.json (Mammals) if it is not there yet.
import sys, math, copy, os
from ulib import *   # noqa

os.environ.setdefault("PREHIST_TMP", "/tmp")


def eye_on(d, S, x, y, r, zin=0.3, **kw):
    """the sculpt's eye on the skin at (x, y): a ray in from the side; the rig's eyes moved there too"""
    hit = ray_hit(d, S, [x, y, zin + 1.0], [x, y, 0.0])
    z = round(hit[2], 4)
    d["sculpt"]["eyes"] = {"at": [round(x, 4), round(y, 4), z], "from": [round(x - 0.15, 4), round(y, 4), 0], "r": r, **kw}
    return z


def midfin(id, root, edge, color, bone, thick, **kw):
    """a sheet on the midline (z = 0, its faces to either side): a bell, a beard"""
    f = {"id": id, "type": "fin", "bone": bone, "root": [R4(list(p[:2]) + [0.0]) for p in root],
         "edge": [R4(list(p[:2]) + [0.0]) + list(p[2:]) for p in edge], "thick": thick, "face": [0, 0, 1], "color": color}
    f.update(kw)
    return f


# ======================================================================================================================
def moose():
    d = {
        "name": "moose", "shy": 10, "graze": 0.9, "rest": 0.7, "use": "creatures/frames/deer", "print": "cloven",
        "params": {"s": 1.75, "bulk": 1.1, "bull": True, "cow": False},
        "headScale": 1, "headTurn": 12,
        "colors": {"body": "#3a2a1f", "back": "#2a1f18", "belly": "#2c221b", "front": "#3a2a1f", "neck": "#35271d",
                   "head": "#4a392b", "face": "#4f3e2f", "muzzle": "#5c4a3a", "lip": "#4e3e31", "chin": "#5a4a3c",
                   "nose": "#1d1714", "ear": "#45352a", "earIn": "#4e4034", "limb": "#3a2a1f", "upleg": "#4a3a2e",
                   "leg": "#6e6052", "foot": "#2a2420", "tail": "#2a1f18", "tailc": "#2a1f18", "bell": "#2e231b",
                   "eye": "#1a120c", "lid": "#2a1f18", "antler": "#b39a72", "antlerTip": "#e4d8c0", "mane": "#2a1f18"},
        "legs": {"front": [0.46, 1.27, 0.2, 0.18], "hind": [-0.64, 1.3, 0.2, 0.62]},
        "rear": [-0.55, 1.42, 0, 0.6, 0.4, 0.34], "front": [0.3, 1.47, 0, 0.7, 0.45, 0.36],
        "neck": [0.62, 1.62, 0, 0.98, 1.8, 0, 0.3, 0.22],
        "head": [1.02, 1.84, 0, 0.17],
        "muzzle": [1.08, 1.78, 0, 1.55, 1.38, 0, 0.13, 0.11],
        "nose": [1.6, 1.38, 0, 0.07],
        "ears": [1.0, 1.93, 0.09, 0.93, 2.03, 0.33, 0.08, 0.025],
        "eyes": [1.17, 1.79, 0.12, 0.025],
        "tail": {"c": [-1.0, 1.6], "R": 0.12, "a0": 0, "a1": -1.0, "r1": 0.045, "r2": 0.03, "n": 3, "sway": 10, "speed": 0.7},
    }
    d["sculpt"] = {"keep": [], "mesh": {"tris": [8500, 2600], "focus": {"head": 4}, "symmetric": True},
                   "shade": {"on": "@body", "back": 0.82, "belly": 1.04}, "shape": []}
    J = joints(d)
    S = Shapes(); C = {"pat": "coarse", "hair": 0.15}
    # ---- the trunk: deep and short, the HUMP over the shoulders (the long spines of the withers), the back falling to
    #      a lower, narrower rump; a deep chest on very long legs
    S.ell("chest", [0.36, 1.44, 0], [0.42, 0.4, 0.32], "@body", k=0.12, **C)
    S.ell("withers", [0.24, 1.74, 0], [0.42, 0.2, 0.22], "@back", k=0.12, rot=[0, 0, -8], **C)
    S.ell("hump", [0.28, 1.88, 0], [0.32, 0.15, 0.15], "@back", k=0.14, rot=[0, 0, -6], **C)
    S.ell("barrel", [-0.16, 1.45, 0], [0.56, 0.33, 0.36], "@body", k=0.12, rot=[0, 0, -4], **C)
    S.ell("loin", [-0.46, 1.56, 0], [0.3, 0.16, 0.27], "@back", k=0.12, rot=[0, 0, 4], **C)
    S.ell("rump", [-0.64, 1.5, 0], [0.26, 0.22, 0.26], "@body", k=0.1, rot=[0, 0, 12], **C)
    S.ell("haunch", [-0.66, 1.4, 0.13], [0.21, 0.25, 0.14], "@body", k=0.08, mirror=True, **C)
    S.ell("belly", [-0.1, 1.26, 0], [0.48, 0.15, 0.3], "@belly", k=0.1, **C)
    S.ell("girth", [0.4, 1.18, 0], [0.25, 0.14, 0.23], "@belly", k=0.1, **C)
    S.ell("scapula", [0.42, 1.52, 0.19], [0.09, 0.26, 0.1], "@body", k=0.08, rot=[0, 0, 25], mirror=True, **C)
    S.ell("breast", [0.62, 1.34, 0.09], [0.13, 0.18, 0.12], "@body", k=0.08, rot=[0, 0, 12], mirror=True, **C)
    # ---- the neck: short and thick, carried forward, a dark crest of longer hair along the top
    S.ell("neckBase", [0.62, 1.62, 0], [0.27, 0.3, 0.25], "@neck", k=0.12, rot=[0, 0, 40], **C)
    S.ell("neck", [0.82, 1.74, 0], [0.27, 0.21, 0.18], "@neck", bone="neck", k=0.1, rot=[0, 0, 18], **C)
    S.ell("crest", [0.66, 1.92, 0], [0.24, 0.075, 0.09], "@mane", bone="neck", k=0.08, rot=[0, 0, -12], pat="shag", hair=0.3)
    S.ell("throat", [0.95, 1.62, 0], [0.14, 0.13, 0.12], "@neck", bone="neck", k=0.08, **C)
    # ---- the legs (the chamois' stretched: long, slender, pale below the knee)
    for s in legs_from(J, (2.15, 2.0), fx=(2.4, 2.3), cols={"@limb": "@body"}, pat="coarse", hair=0.15):
        if s["color"] != "@foot": s["kc"] = 0.075     # (the pale lower leg fading into the brown over ~15 cm)
        S.append(s)
    # ---- the head: long and heavy, hung forward and down, the Roman-nosed bridge and the great overhanging MUZZLE --
    #      a broad pendulous upper lip past the short lower jaw, the nostrils slanting slits on its front
    H = "head"
    S.ell("cranium", [1.03, 1.86, 0], [0.14, 0.13, 0.12], "@head", bone=H, k=0.05, rot=[0, 0, -30])
    S.ell("pedicle", [1.05, 1.96, 0.08], [0.055, 0.045, 0.05], "@head", bone=H, k=0.03, mirror=True, when="bull")
    S.ell("face", [1.27, 1.66, 0], [0.3, 0.115, 0.095], "@face", bone=H, k=0.05, rot=[0, 0, -42])
    S.ell("bridge", [1.44, 1.53, 0], [0.15, 0.065, 0.085], "@face", bone=H, k=0.04, rot=[0, 0, -38])
    S.ell("bulb", [1.52, 1.42, 0], [0.15, 0.13, 0.115], "@muzzle", bone=H, k=0.05, rot=[0, 0, -40])
    S.ell("upLip", [1.57, 1.31, 0], [0.11, 0.085, 0.11], "@lip", bone=H, k=0.04, rot=[0, 0, -20])
    S.ell("cheek", [1.08, 1.69, 0.075], [0.13, 0.11, 0.07], "@head", bone=H, k=0.05, mirror=True)
    S.ell("jaw", [1.23, 1.56, 0.055], [0.23, 0.06, 0.045], "@head", bone=H, k=0.04, rot=[0, 0, -40], mirror=True)
    S.ell("chin", [1.43, 1.33, 0], [0.075, 0.04, 0.055], "@chin", bone=H, k=0.03, rot=[0, 0, -40])
    S.ell("nostril", [1.62, 1.41, 0.065], [0.055, 0.018, 0.024], "@nose", bone=H, k=0.01, op="sub", rot=[0, 20, -55], mirror=True)
    S.ell("mouth", [1.54, 1.29, 0], [0.1, 0.007, 0.085], "@nose", bone=H, k=0.008, op="sub", rot=[0, 0, -20])
    # ---- the tail: a short stump
    S.ell("tailDock", [-0.86, 1.6, 0], [0.06, 0.05, 0.05], "@back", k=0.04, rot=[0, 0, 30], **C)
    S.tube("tail", [[-0.87, 1.62, 0, 0.045], [-0.93, 1.58, 0, 0.042], [-0.97, 1.51, 0, 0.034], [-0.98, 1.45, 0, 0.016]],
           "@tailc", bone="tail", k=0.02, **C)
    # ---- the eye, the ears, the bell
    eye_on(d, S, 1.17, 1.79, 0.022, iris="@eye", pupil="bar", lid="@lid", sink=0.45)
    ears = load_species("mammals/deer")
    e0 = next(p for p in ears["sculpt"]["shape"] if p["id"] == "ear")
    T = ray_hit(d, S, [0.99, 1.9, 0.0], [0.99, 2.05, 0.3]); T = add(T, nrm([0, 0.5, 1.0]), -0.015)
    ear = ear_onto(e0, T, [-0.3, 0.4, 1.0], [1.0, 0.15, 0.3], 1.25, 1.2)
    hy = ray_hit(d, S, [1.04, 1.68, 0], [1.04, 1.0, 0])[1]
    bell = midfin("bell", [[0.97, hy + 0.05], [1.03, hy + 0.04], [1.09, hy + 0.03]],
                  [[0.955, hy - 0.02, 1.2], [0.96, hy - 0.1, 1.2], [0.975, hy - 0.2], [0.99, hy - 0.28], [1.005, hy - 0.32],
                   [1.02, hy - 0.3], [1.035, hy - 0.22], [1.06, hy - 0.12], [1.085, hy - 0.04, 1.4]],
                  "@bell", "neck", 0.035, slope=0.6, corners=[4], fair={"r": 0.02, "sink": 3}, pat="shag")
    # ---- the ANTLERS (the bull's): a short beam out from each pedicle, flattened, and on it two PALMS sharing it as
    #      their root -- the broad main palm rising back and up (its plane through the beam tipped 38 degrees back), the
    #      brow palm reaching forward nearly level (its own plane through the beam), the two at an angle with a cleft
    #      between them, dished, short tines along their outer rims
    B = [1.06, 1.99, 0.09]
    L = nrm([0, math.sin(math.radians(12)), math.cos(math.radians(12))])
    def plane(e1):
        n = nrm(crs(L, e1)); n = n if n[1] > 0 else mul(n, -1)
        return Plane(B, n, e1)
    pm = plane([math.cos(math.radians(38)), -math.sin(math.radians(38)), 0])
    pf = plane([1, 0.06, 0])
    BV = [(-0.05, 0.044, 1.0), (0.0, 0.048, 1.0), (0.05, 0.042, 0.95), (0.1, 0.039, 0.85), (0.16, 0.035, 0.7),
          (0.22, 0.03, 0.6), (0.26, 0.022, 0.55), (0.29, 0.012, 0.55), (0.31, 0.0, 0.55)]
    beam = curve_horn("beam", [R4(pm.p3(0, v)) + [r, a] for v, r, a in BV], "@antler", mirror=True, up=R4(pm.n),
                      tip="@antlerTip", tipAt=0.95, when="bull")
    root = [pm.p3(0, v) for v in (0.07, 0.13, 0.19, 0.25)]
    A = {"mirror": True, "when": "bull"}
    front, ft = palm_fin(pf, "browPalm", root, [
        ("p", 0.05, 0.08, 1.0), ("p", 0.11, 0.1, 1.0),
        ("t", "browT0", 0.17, 0.125, 10, 0.016, 0.11, 10, 0.2),
        ("p", 0.21, 0.17, 1.0),
        ("t", "browT1", 0.23, 0.215, 30, 0.016, 0.12, 8, 0.2),
        ("p", 0.22, 0.265, 1.0),
        ("t", "browT2", 0.19, 0.31, 56, 0.015, 0.11, 0, 0.2),
        ("p", 0.14, 0.345, 1.0),
        ("t", "browT3", 0.1, 0.37, 78, 0.013, 0.08, -6, 0.2),
        ("p", 0.06, 0.34, 1.0), ("p", 0.03, 0.29, 1.0)],
        "@antler", thick=0.026, slope=1.2, swell=(0.036, 0.09, 1.2), bt=1.3, n=80, across=6, extra=dict(A))
    rear, rt = palm_fin(pm, "palm", root, [
        ("p", -0.07, 0.085, 1.0), ("p", -0.16, 0.12, 1.0), ("p", -0.25, 0.17, 1.0), ("p", -0.32, 0.24, 1.0),
        ("t", "palmT0", -0.36, 0.31, 168, 0.017, 0.11, -12, 0.15),
        ("p", -0.37, 0.38, 1.0),
        ("t", "palmT1", -0.35, 0.45, 142, 0.017, 0.13, -10, 0.2),
        ("p", -0.315, 0.51, 1.0),
        ("t", "palmT2", -0.265, 0.56, 120, 0.017, 0.14, -8, 0.25),
        ("p", -0.21, 0.6, 1.0),
        ("t", "palmT3", -0.155, 0.63, 102, 0.016, 0.14, -6, 0.25),
        ("p", -0.1, 0.64, 1.0),
        ("t", "palmT4", -0.045, 0.63, 86, 0.016, 0.13, -4, 0.25),
        ("p", -0.005, 0.6, 1.0),
        ("t", "palmT5", 0.02, 0.545, 68, 0.014, 0.1, -4, 0.2),
        ("p", -0.02, 0.47, 1.0), ("p", -0.045, 0.38, 1.0), ("p", -0.05, 0.31, 1.0)],
        "@antler", thick=0.028, slope=1.2, swell=(0.036, 0.09, 1.2), bt=1.3, n=110, across=7, extra=dict(A))
    front["face"] = R4(pf.n); front["cup"] = 0.1
    rear["face"] = R4(pm.n); rear["cup"] = 0.16
    tines = [curve_horn(t, P, "@antler", mirror=True, up=R4(pf.n), tip="@antlerTip", tipAt=0.55, when="bull") for t, P in ft]
    tines += [curve_horn(t, P, "@antler", mirror=True, up=R4(pm.n), tip="@antlerTip", tipAt=0.55, when="bull") for t, P in rt]
    sink_horns(d, [beam])
    sharp = [beam, front, rear] + tines + [ear, bell]
    d["sculpt"]["shape"] = list(S) + sharp
    d["variants"] = {
        "cow": {"params": {"bull": False, "cow": True}, "scale": 0.86,
                "colors": {"head": "#5a4634", "face": "#5e4a38", "muzzle": "#6a5644", "back": "#30241b"}},
        "calf": {"params": {"bull": False, "cow": False}, "scale": 0.5,
                 "colors": {"body": "#8a5232", "back": "#76442a", "belly": "#7e4c30", "front": "#8a5232", "neck": "#844e30",
                            "head": "#7a4a2e", "face": "#7e4e32", "muzzle": "#6e4a34", "lip": "#6a4630", "chin": "#80583c",
                            "ear": "#7a4a2e", "limb": "#8a5232", "upleg": "#8a5a3c", "leg": "#9a6e4c", "tail": "#76442a",
                            "tailc": "#76442a", "bell": "#7a4a2e", "mane": "#6e3e26"}}}
    d["_variants"] = ("VARIANTS (species.js variantDef): `cow`, the female -- .86 the bull's size, no antlers, a browner face; "
                      "`calf`, half the size, the reddish-brown coat of its first summer, no antlers")
    d["sculpt"]["_about"] = (
        "THE MOOSE (Alces alces; 2026-11-08, generator tools/creaturegen/ungulates/gen.py, on the deer frame): a bull of "
        "about 2 m at the shoulder -- very long slender legs, pale grey-brown below the knee, under a short deep trunk; "
        "the high HUMP over the shoulders, the back falling to a lower rump; a short thick neck with a dark crest; the "
        "long heavy head hung forward and down, a Roman-nosed bridge ending in the great overhanging MUZZLE (a broad "
        "pendulous upper lip past the short lower jaw, slit nostrils on its front); large ears (the deer's `fin` ear "
        "mapped larger); the BELL, a hairy `fin` flap hanging from the throat; a short stump of a tail; dark brown, near "
        "black on the hump. The ANTLERS (bull only, `when: bull`), exactly mirrored: from each pedicle a short beam (a "
        "`horn`, flattened in the antler's plane) out and a little up, and on it two PALMS -- dished `fin` sheets rooted "
        "along the beam, each in its own plane: the brow palm reaching forward nearly level with four tines, the broad "
        "main palm rising back and up (its plane tipped 38 degrees back) with six, a cleft between them -- every tine a short `horn` on the palm's rim, turning a "
        "little up, its tip pale. Legs: the chamois' (ulib.legs_from), stretched. Variants `cow` (no antlers; shares the bull's shape build) and `calf`.")
    return d


def fringe(id, root, tips, color, bone, thick, back=None, z=0.0, face=(0, 0, 1), notch=0.45, **kw):
    """a ragged sheet of long hair: rooted along `root` ((x, y) points, its edge leaving root[0] and coming back to
    root[-1]), hanging in LOCKS -- each tip (x, y) a sharp corner, a notch between neighbours `notch` of the way back
    up toward the root; in the plane z (its faces to either side)"""
    def P(q, b=None): return R4([q[0], q[1], z]) + ([b] if b else [])
    edge, corners = [P(root[0], 1.2)], []
    prev = root[0]
    for i, t in enumerate(tips):
        if i:
            m = lerp([prev[0], prev[1], 0], [t[0], t[1], 0], 0.5)
            r = root[min(len(root) - 1, round(i * (len(root) - 1) / len(tips)))]
            edge.append(P([m[0] + (r[0] - m[0]) * notch, m[1] + (r[1] - m[1]) * notch], 1.2))
        corners.append(len(edge)); edge.append(P(t)); prev = t
    edge.append(P(root[-1], 1.2))
    f = {"id": id, "type": "fin", "bone": bone, "root": [P(q) for q in root], "edge": edge, "corners": corners,
         "thick": thick, "face": list(face), "color": color}
    f.update(kw)
    return f


# ======================================================================================================================
def jit(i, a=0):
    """a fixed pseudo-random share 0..1 (the lumps' sizes vary, the same every run)"""
    return ((i * 7919 + a * 104729 + 13) % 997) / 997.0


def bison():
    d = {
        "name": "bison", "kind": "mammal", "headForm": "cattle", "shy": 4, "graze": 1.0, "rest": 0.75, "print": "cloven",
        "headScale": 1, "headTurn": 8, "pupil": "bar",
        "params": {"bull": True, "cow": False, "adult": True},
        "rear": [-0.5, 1.02, 0, 0.5, 0.42, 0.36], "front": [0.45, 1.15, 0, 0.65, 0.6, 0.45],
        "neck": [0.86, 1.25, 0, 1.08, 1.05, 0, 0.38, 0.3],
        "head": [1.18, 0.98, 0, 0.3],
        "muzzle": [1.24, 0.9, 0, 1.46, 0.64, 0, 0.2, 0.15],
        "ears": [1.12, 1.05, 0.2, 1.1, 1.04, 0.32, 0.05, 0.03],
        "eyes": [1.3, 0.98, 0.19, 0.025],
        "legs": {"front": [0.64, 1.02, 0.32, 0.32], "hind": [-0.76, 0.72, 0.32, 0.34], "radii": [0.17, 0.115, 0.085],
                 "foot": [0.1, 0.055, 0.09], "thigh": 1.5},
        "tail": {"path": [[-0.96, 1.3], [-1.03, 1.22], [-1.04, 1.05], [-1.02, 0.88]], "r1": 0.04, "r2": 0.025, "tuft": 0,
                 "sway": 12, "speed": 0.7},
        "extras": [],
        "c": {"body": "#4a3522", "cape": "#2a1e16", "fore": "#2a1e16", "head": "#251a13", "muzzle": "#1f1915",
              "nose": "#141110", "ear": "#2a1e16", "earIn": "#2a201a", "leg": "#2a1f18", "foot": "#1a1512",
              "tail": "#46321f", "tuft": "#211812", "eye": "#120c08", "horn": "#1d1916", "hornTip": "#0e0c0b",
              "beard": "#1e1610", "mat": "#33251b", "belly": "#3a2a1c"},
    }
    d["sculpt"] = {"keep": [], "mesh": {"tris": [9000, 2700], "focus": {"head": 4, "tail": 4}, "symmetric": True},
                   "shade": {"on": "@body", "back": 0.88, "belly": 1.06}, "shape": []}
    J = joints(d)
    S = Shapes()
    W = {"pat": "coarse", "hair": 0.06}         # (the cape: MATTE coarse wool -- `hair` is the sheen: kept low)
    Cs = {"pat": "coarse", "hair": 0.1}         # (the hindquarters' short hair)
    KC = 0.2                                    # (the cape's colour fading into the body's over ~20 cm)
    # ---- ONE MASS: the huge low head rising through the crest into the HUMP, which peaks over the forelegs, then the
    #      back sloping down evenly to the small, low, round hindquarters -- big blends, no step
    S.ell("chest", [0.45, 1.12, 0], [0.5, 0.47, 0.44], "@cape", k=0.15, kc=KC, **W)
    S.ell("hump", [0.42, 1.48, 0], [0.52, 0.37, 0.33], "@cape", k=0.18, kc=KC, rot=[0, 0, -16], **W)
    S.ell("humpTop", [0.5, 1.7, 0], [0.34, 0.18, 0.21], "@cape", k=0.16, kc=KC, rot=[0, 0, -22], **W)
    S.ell("slope", [-0.12, 1.39, 0], [0.62, 0.17, 0.31], "@body", k=0.2, kc=KC, rot=[0, 0, 13], **Cs)
    S.ell("barrel", [-0.3, 1.04, 0], [0.52, 0.3, 0.36], "@body", k=0.16, kc=KC, **Cs)
    S.ell("rump", [-0.76, 1.2, 0], [0.27, 0.19, 0.26], "@body", k=0.16, **Cs)
    S.ell("hook", [-0.6, 1.27, 0.2], [0.08, 0.05, 0.06], "@body", k=0.1, mirror=True, **Cs)
    S.ell("tailhead", [-0.94, 1.29, 0], [0.08, 0.06, 0.07], "@body", k=0.06, **Cs)
    S.ell("quarter", [-0.78, 0.98, 0.18], [0.2, 0.27, 0.15], "@body", k=0.13, rot=[0, 0, -12], mirror=True, **Cs)
    S.ell("belly", [-0.22, 0.9, 0], [0.5, 0.16, 0.36], "@belly", k=0.12, **Cs)
    S.ell("scapula", [0.5, 1.22, 0.32], [0.14, 0.3, 0.13], "@cape", k=0.1, rot=[0, 0, 24], mirror=True, **W)
    S.ell("brisket", [0.7, 0.86, 0], [0.2, 0.17, 0.21], "@cape", k=0.1, **W)
    S.ell("neckBase", [0.8, 1.22, 0], [0.36, 0.44, 0.37], "@cape", k=0.16, rot=[0, 0, -30], **W)
    S.ell("neck", [1.0, 1.1, 0], [0.3, 0.34, 0.31], "@cape", bone="neck", k=0.14, rot=[0, 0, -40], **W)
    S.ell("crest", [0.82, 1.5, 0], [0.36, 0.18, 0.24], "@cape", bone="neck", k=0.15, rot=[0, 0, -38], **W)
    # ---- the head: huge, the forehead almost UPRIGHT, a short face to a dark broad muzzle near the ground
    H = "head"
    S.ell("skull", [1.16, 1.03, 0], [0.24, 0.23, 0.23], "@head", bone=H, k=0.06, **W)
    S.ell("poll", [1.1, 1.18, 0], [0.14, 0.1, 0.18], "@cape", bone=H, k=0.06, **W)
    S.ell("forehead", [1.3, 0.98, 0], [0.1, 0.22, 0.2], "@cape", bone=H, k=0.06, rot=[0, 0, -8], **W)
    S.cone("face", [1.3, 0.9, 0], [1.42, 0.67, 0], 0.13, 0.105, "@head", bone=H, k=0.05, **W)
    S.ell("muzzle", [1.43, 0.64, 0], [0.085, 0.095, 0.11], "@muzzle", bone=H, k=0.04, rot=[0, 0, -65])
    S.ell("nose", [1.495, 0.625, 0], [0.018, 0.07, 0.09], "@nose", bone=H, k=0.013, rot=[0, 0, -65], wet=0.45)
    S.ell("lip", [1.38, 0.58, 0], [0.06, 0.035, 0.075], "@muzzle", bone=H, k=0.03, rot=[0, 0, -65])
    S.ell("nostril", [1.505, 0.635, 0.045], [0.012, 0.024, 0.015], "@nose", bone=H, k=0.006, op="sub", rot=[0, 0, -90], mirror=True)
    S.ell("jaw", [1.22, 0.86, 0.09], [0.18, 0.13, 0.07], "@head", bone=H, k=0.05, rot=[0, 0, -60], mirror=True, **W)
    S.ell("cheek", [1.17, 0.97, 0.17], [0.11, 0.15, 0.09], "@cape", bone=H, k=0.05, mirror=True, **W)
    # ---- the legs: the ox's, thicker -- the forelegs in the cape's wool to the knees, sturdy hind legs
    ox = load_species("mammals/ox")
    for s in ox["sculpt"]["shape"]:
        if not (s.get("bone", "").startswith(("legF", "legH", "foot")) or s["id"] in ("toeo", "toei", "htoeo", "htoei")):
            continue
        s = copy.deepcopy(s); fore = s.get("bone", "").startswith(("legF", "footF"))
        g = 1.0 if s["color"] == "@foot" else (1.22 if fore else 1.15)
        if s["id"] == "arm": g = 1.22
        if s["id"] == "forearm": s["ra"] = round(s["ra"] * 1.6, 4); s["rb"] = round(s["rb"] * 1.45, 4)
        if "r" in s: s["r"] = [round(v * g, 4) for v in s["r"]] if isinstance(s["r"], list) else round(s["r"] * g, 4)
        if s["id"] != "forearm":
            for k in ("ra", "rb"):
                if k in s: s[k] = round(s[k] * g, 4)
        if "pts" in s: s["pts"] = [p[:3] + [round(p[3] * g, 4)] for p in s["pts"]]
        if s["id"] in ("arm", "forearm"): s["color"] = "@cape"; s.update(W); s["kc"] = 0.06
        elif s["color"] != "@foot": s.update(Cs)
        S.append(s)
    # ---- the tail: short and thin (a `sweep`), a dark tuft
    S.append({"id": "tail", "type": "sweep", "bones": ["tail", "tail1"], "color": "@tail", "k": 0.02,
              "pts": [[-0.955, 1.3, 0, 0.05], [-0.99, 1.28, 0, 0.044], [-1.025, 1.24, 0, 0.038], [-1.04, 1.18, 0, 0.034],
                      [-1.045, 1.11, 0, 0.031], [-1.042, 1.04, 0, 0.029], [-1.036, 0.97, 0, 0.027], [-1.03, 0.91, 0, 0.026]], **Cs})
    S.tube("tailTuft", [[-1.035, 0.97, 0, 0.032], [-1.03, 0.89, 0, 0.05], [-1.025, 0.81, 0, 0.042], [-1.02, 0.73, 0, 0.012]],
           "@tuft", bone="tail1", k=0.02, **Cs)
    d["sculpt"]["shape"] = list(S)
    base = list(S)
    def hit(a, b):
        h = probe(dict(d, sculpt=dict(d["sculpt"], shape=base)), {"rays": [[a, b]]})["hits"][0]
        return h
    def lump(id, c, r, bone=None, when=None, color="@cape", k=0.06):
        sh = {"id": id, "type": "ell", "c": R4(c), "r": [round(v, 4) for v in r], "k": k, "color": color, **W}
        if bone: sh["bone"] = bone
        if c[2] > 0.01: sh["mirror"] = True
        if when: sh["when"] = when
        return sh
    lumps = []
    # ---- the hump's and the crest's wool: soft lumps along the top line (their own for the cow's lower hump, below)
    TOP = [(-0.02, 0, 0.08), (0.12, 0, 0.1), (0.26, 0, 0.11), (0.4, 0, 0.11), (0.54, 0, 0.11), (0.67, 0, 0.1),
           (0.2, 0.2, 0.1), (0.4, 0.22, 0.11), (0.6, 0.21, 0.1)]
    def top_locks(shapes):
        out = []
        for i, (x, z, r) in enumerate(TOP):
            h = probe(dict(d, sculpt=dict(d["sculpt"], shape=shapes)), {"rays": [[[x, 2.6, z], [x, 0.6, z]]]})["hits"][0]
            out.append(("lock%d" % i, [x, h[1] - r * 0.6, z], [r * 1.3, r, r]))
        return out
    for id, c, r in top_locks(base): lumps.append(lump(id, c, r, k=0.09))
    # ---- the SKIRT: overlapping lumps of many sizes hanging along the cape's lower edge -- under the throat, the
    #      chest and the elbows
    n = 0
    for xi in range(14):
        x = 0.24 + xi * 0.065
        for zi, z in enumerate((0.0, 0.13, 0.25)):
            if z > 0.2 and x > 0.85: continue
            h = hit([x, 0.15, z], [x, 1.6, z])
            if not h: continue
            j = jit(n, 1); rx = 0.055 + 0.035 * j; ry = 0.08 + 0.06 * jit(n, 2); rz = 0.05 + 0.03 * jit(n, 3)
            bone = "neck" if x > 0.86 else None
            lumps.append(lump("skirt%d" % n, [x + 0.02 * (jit(n, 4) - 0.5), h[1] - 0.1 * ry, z], [rx, ry, rz], bone, "adult", k=0.05))
            n += 1
    # ---- the cape's rear edge: lumps thinning out over the ribs (fewer and smaller further back), and patches of its
    #      colour (paints) scattered past it -- an irregular, gradual edge
    n = 0
    for xi, x in enumerate((0.3, 0.2, 0.1, 0.02, -0.06)):
        for yi, y in enumerate((0.98, 1.12, 1.26, 1.4)):
            if jit(xi * 4 + yi, 5) < 0.25 + 0.15 * xi: continue
            h = hit([x, y, 1.2], [x, y, 0.0])
            if not h: continue
            r = (0.07 + 0.03 * jit(n, 6)) * (1 - 0.12 * xi)
            lumps.append(lump("flank%d" % n, [x, y, h[2] - r * 0.55], [r * 1.2, r, r * 0.8], None, "adult", k=0.06))
            n += 1
    for i, (x, y) in enumerate(((0.05, 1.05), (-0.08, 1.2), (-0.02, 1.4), (-0.14, 1.33), (0.08, 0.95), (-0.12, 1.1))):
        h = hit([x, y, 1.2], [x, y, 0.0])
        if h: lumps.append({"id": "capeEdge%d" % i, "type": "ell", "op": "paint", "c": R4([x, y, h[2]]),
                            "r": [0.09 + 0.05 * jit(i, 7), 0.07 + 0.05 * jit(i, 8), 0.08], "kc": 0.07, "color": "@cape", "mirror": True})
    # ---- the forelegs' CHAPS: wool lumps round the forearm, down to the knee
    n = 0
    for yi, y in enumerate((0.7, 0.6, 0.5, 0.42)):
        for ai, ang in enumerate((180, 130, 230, 90, 280)):
            if yi == 3 and ai > 2: continue
            a = math.radians(ang); x0 = 0.62 + 0.004 * (0.7 - y) / 0.1
            rr = 0.105 - 0.015 * yi
            c = [x0 + math.cos(a) * rr, y, 0.292 + math.sin(a) * rr * 0.9]
            r = 0.065 + 0.025 * jit(n, 9)
            lumps.append(lump("chap%d" % n, c, [r, r * 1.35, r], "legFLl", "adult", k=0.04))
            lumps[-1]["mirror"] = True
            n += 1
    # ---- the BEARD: thick, rounded locks hanging from the chin and the jaws (the bull's longer)
    n = 0
    for i, x in enumerate((1.12, 1.19, 1.26, 1.33)):
        h = hit([x, 0.1, 0], [x, 1.2, 0])
        if not h: continue
        for z in (0.0, 0.07):
            r = 0.06 + 0.02 * jit(n, 10)
            lumps.append(lump("beard%d" % n, [x, h[1] - 0.03, z], [r, r * 1.6, r * 0.9], "head", "adult", "@beard", k=0.04))
            n += 1
            if i < 3:
                lumps.append(lump("beard%d" % n, [x - 0.02, h[1] - 0.15, z * 0.7], [r * 0.85, r * 1.5, r * 0.75], "head", "bull", "@beard", k=0.04))
                n += 1
    # ---- the FORELOCK: a big curly mat over the brow and between the horns -- round curls of many sizes, staggered
    #      and jittered (rows would read as rolls)
    n = 0
    for yi, y in enumerate((0.9, 0.97, 1.04, 1.11, 1.18, 1.25)):
        for zi in range(3):
            z = zi * 0.085 + (0.04 if yi % 2 else 0.0) + 0.02 * (jit(n, 13) - 0.5)
            yy = y + 0.03 * (jit(n, 14) - 0.5)
            h = hit([2.0, yy, z], [0.9, yy, z])
            if not h or z > 0.2: continue
            r = 0.035 + 0.03 * jit(n, 11)
            lumps.append(lump("mat%d" % n, [h[0] - r * 0.4, yy, max(0.0, z)], [r, r, r], "head", None, "@mat", k=0.015))
            n += 1
    for xi, x in enumerate((1.0, 1.07, 1.14, 1.21)):
        for zi in range(2):
            z = zi * 0.09 + (0.045 if xi % 2 else 0.0)
            h = hit([x, 2.2, z], [x, 0.8, z])
            if not h: continue
            r = 0.04 + 0.03 * jit(n, 12)
            lumps.append(lump("mat%d" % n, [x + 0.02 * (jit(n, 15) - 0.5), h[1] - r * 0.4, z], [r, r, r], "head", None, "@mat", k=0.015))
            n += 1
    S = Shapes(base + lumps)
    # ---- the eye small in the wool, the ears (the ox's leaf, small, mostly hidden)
    eye_on(d, S, 1.3, 0.98, 0.022, iris="@eye", pupil="bar", lid="#1a120c", sink=0.5)
    e0 = next(p for p in ox["sculpt"]["shape"] if p["id"] == "ear")
    T = ray_hit(d, S, [1.11, 1.04, 0.0], [1.11, 1.04, 0.6]); T = add(T, [0, 0, 1], -0.05)
    ear = ear_onto(e0, T, [-0.2, -0.4, 1.0], [1.0, 0.1, 0.25], 0.6, 0.65)
    # ---- the HORNS: short, sharp, black -- from the sides of the head just under the mat, out, then up and IN
    hB = curve_horn("hornB", [[1.14, 1.12, 0.14, 0.06], [1.14, 1.13, 0.24, 0.054], [1.14, 1.16, 0.31, 0.046],
                              [1.13, 1.22, 0.35, 0.036], [1.11, 1.29, 0.35, 0.025], [1.09, 1.34, 0.32, 0.013],
                              [1.075, 1.365, 0.29, 0.0]], "@horn", mirror=True, tip="@hornTip", tipAt=0.6, when="bull")
    hC = curve_horn("hornC", [[1.14, 1.12, 0.14, 0.045], [1.14, 1.13, 0.23, 0.04], [1.14, 1.16, 0.29, 0.033],
                              [1.13, 1.21, 0.32, 0.025], [1.11, 1.27, 0.31, 0.015], [1.09, 1.3, 0.28, 0.0]],
                    "@horn", mirror=True, tip="@hornTip", tipAt=0.6, when="cow")
    sink_horns(d, [hB, hC])
    d["sculpt"]["shape"] = list(S) + [hB, hC, ear]
    # (the cow's and the calf's lower hump, with its own wool lumps placed on it)
    HUMP_LOW = {"humpTop": {"c": [0.5, 1.6, 0], "r": [0.32, 0.13, 0.19]}, "hump": {"c": [0.42, 1.43, 0], "r": [0.5, 0.31, 0.31]}}
    low = [dict(s, **HUMP_LOW.get(s["id"], {})) for s in base]
    small = {"shape": [dict(id=k, **v) for k, v in HUMP_LOW.items()] +
                      [{"id": id, "c": R4(c)} for id, c, r in top_locks(low)]}
    d["variants"] = {
        "cow": {"params": {"bull": False, "cow": True, "adult": True}, "scale": 0.82, "sculpt": small},
        "calf": {"params": {"bull": False, "cow": False, "adult": False}, "scale": 0.45, "sculpt": small,
                 "colors": {"body": "#b2642e", "cape": "#a85a28", "fore": "#a85a28", "head": "#9a5226", "muzzle": "#4a3020",
                            "ear": "#a85a28", "leg": "#8a4a22", "tail": "#a85a28", "tuft": "#6a3a1c", "mat": "#a05426",
                            "belly": "#a05a2c", "beard": "#8a4a22"}}}
    d["_variants"] = ("VARIANTS (species.js variantDef): `cow` -- .82 the bull's size, a lower hump, thinner horns curving "
                      "in more, a short beard; `calf` -- .45, the orange-red 'red dog' coat of its first months, no horns, "
                      "no beard, skirt or chaps, a low hump")
    d["sculpt"]["_about"] = (
        "THE AMERICAN BISON (Bison bison; 2026-11-08, generator tools/creaturegen/ungulates/gen.py, a cattle rig): a "
        "bull of about 1.9 m at the hump, ONE MASS -- the huge head carried low, its forehead almost upright, rising "
        "through the crest into the HUMP that peaks over the forelegs, the back sloping evenly down to small, low, round "
        "hindquarters in short paler hair (big blends, no step). The dark CAPE is matte coarse wool (`coarse`, `hair`), "
        "its colour fading into the body's over ~20 cm (`kc`) with scattered patches of it (paints) past an irregular "
        "edge of thinning lumps over the ribs; its SHAGGY OUTLINE is field lumps of many sizes -- along the hump, the "
        "SKIRT hanging under the throat, chest and elbows, the CHAPS round the forearms down to the knees, a thick BEARD "
        "of rounded locks (longer on the bull), a big curly FORELOCK mat over the brow. Thick forelegs, sturdy hind legs "
        "(the ox's, thickened). The HORNS short, sharp and black (`horn`s) from the sides of the head under the mat, out, "
        "up and curving in; small ears (the ox's leaf) mostly hidden; small eyes in the wool; a short `sweep` tail with "
        "a dark tuft.")
    return d


def scaled_rig(d, k, s, bulk):
    """a deer-frame species' rig params (expressions in s and bulk) evaluated at the source's s and the new bulk, then all
    scaled k about the origin (lengths; the tail's angles and timing kept)"""
    def ev(x): return eval(x, {}, {"s": s, "bulk": bulk}) if isinstance(x, str) else x
    def sc(v): return [round(ev(x) * k, 4) for x in v]
    for key in ("rear", "front", "neck", "head", "muzzle", "nose", "ears", "eyes"):
        if key in d: d[key] = sc(d[key])
    d["legs"] = {kk: sc(v) for kk, v in d["legs"].items()}
    t = d["tail"]
    if "c" in t: t["c"] = sc(t["c"])
    if "path" in t: t["path"] = [sc(p) for p in t["path"]]
    for kk in ("R", "r1", "r2"):
        if kk in t: t[kk] = round(ev(t[kk]) * k, 4)


def knob_horn(id, B, a0, turn, L, z0, z1, r0, r1, knobs=True, n=None, **kw):
    """an IBEX horn: a scimitar arc of length L from base B (x, y), its direction a0 degrees at the root (90 up, 180
    back) turning `turn` degrees by the tip, spreading out from z0 to z1; the radius tapering r0 to r1 by 90% of its
    length, then to a point -- and on the front of it the KNOBS: every 5 cm a ridge (the radius 20% up, the aspect
    lower: wider across the front), between them a shallow trough"""
    n = n or max(8, int(round(L / 0.025)))
    P, x, y = [], B[0], B[1]
    for i in range(n + 1):
        s = L * i / n; f = s / L
        th = math.radians(a0 + turn * f)
        if i: x += math.cos(th) * L / n; y += math.sin(th) * L / n
        z = z0 + (z1 - z0) * f ** 1.3
        r = r0 + (r1 - r0) * min(1.0, f / 0.9) if f < 0.9 else r1 * (1 - f) / 0.1
        asp = 0.82
        if knobs and 0.04 < s < 0.8 * L:
            if i % 2 == 0: r *= 1.2; asp = 0.7
            else: r *= 0.95
        P.append([round(x, 4), round(y, 4), round(z, 4), round(max(r, 0.0), 4), asp])
    P[-1][3] = 0.0
    h = {"id": id, "type": "horn", "bone": "head", "pts": P}
    h.update(kw)
    return h


# ======================================================================================================================
def ibex():
    K = 1.18      # the chamois' 0.8 m at the withers to the billy's 0.94
    KH = 1.1      # the head heavier again (about its cranium)
    ch = load_species("mammals/chamois")
    d = {k: copy.deepcopy(ch[k]) for k in ("use", "legs", "tail", "neck", "head", "muzzle", "nose", "ears", "eyes",
                                           "rear", "front", "print", "extras")}
    d.update({"name": "ibex", "shy": 12, "graze": 1.0, "params": {"s": round(0.7 * K, 4), "bulk": 1.37, "billy": True,
                                                                     "nanny": False, "kid": False}})
    scaled_rig(d, K, 0.7, 1.2 * 1.14)
    d["colors"] = {"body": "#8a7862", "front": "#5e4c3a", "neck": "#82705c", "head": "#857360", "muzzle": "#a4937c",
                   "ear": "#7a6854", "leg": "#3c3128", "foot": "#1e1a16", "tail": "#3a2e24", "eye": "#3a2a14",
                   "belly": "#c2b49c", "throat": "#7a6854", "patch": "#c8bba4", "nose": "#2a2420", "chin": "#b4a68e",
                   "gland": "#857360", "earIn": "#8c7a62", "upleg": "#5a4a3a", "ring": "#d8ccb8", "back": "#76644f",
                   "tailc": "#3a2e24", "earTip": "#55463a", "black": "#2a221c", "hornc": "#6e604e", "hornTip": "#4a4036",
                   "brow": "#8a7862", "throatW": "#b4a68e", "limb": "#655341", "stripe": "#4a3c2e", "mask": "#857360",
                   "beard": "#3a2e24"}
    sc = ch["sculpt"]
    d["sculpt"] = {"keep": [], "mesh": {"tris": [7600, 2400], "focus": {"head": 4}, "symmetric": True},
                   "shade": {"on": "@body", "back": 0.86, "belly": 1.06}, "shape": []}
    STOCKY = {"chest": (1.12, 1.1, -0.03), "girth": (1.18, 1.15, -0.02), "breast": (1.15, 1.15, 0.0),
              "neckBase": (1.18, 1.18, 0.0), "neck": (1.15, 1.2, 0.0), "throat": (1.1, 1.15, 0.0), "scapula": (1.1, 1.18, 0.0)}
    TRUNK = {"chest", "withers", "barrel", "loin", "rump", "haunch", "scapula", "breast", "belly", "girth", "neckBase",
             "neck", "throat"}
    Hc = [0.6585 * K, 0.8756 * K, 0.0]   # (the cranium's centre, scaled)
    S = Shapes(); horn0 = ear0 = None
    for s in sc["shape"]:
        if s["id"] in ("dorsal", "mask"): continue
        s = xshape(s, [0, 0, 0], K, [0, 0, 0])
        if s["id"] == "hornd": horn0 = s; continue
        if s.get("bone") == "head" or s["id"] == "ear":
            s = xshape(s, Hc, KH, [0, 0, 0])
            if s["id"] == "ear": ear0 = s; continue
        if s["id"] in TRUNK and "r" in s:     # (a stocky goat: the trunk and neck deeper and broader)
            s["r"] = [s["r"][0], round(s["r"][1] * 1.12, 4), round(s["r"][2] * 1.16, 4)]
            if s["id"] in ("haunch", "scapula", "breast"): s["c"][2] = round(s["c"][2] * 1.12, 4)
            g = STOCKY.get(s["id"])
            if g:   # (deeper chest, thicker neck and shoulders)
                s["r"] = [s["r"][0], round(s["r"][1] * g[0], 4), round(s["r"][2] * g[1], 4)]
                s["c"][1] = round(s["c"][1] + g[2], 4)
            if s["id"] in ("belly", "girth", "barrel", "chest"):   # (smooth flanks: the belly blended in, no crease)
                s["k"] = max(s["k"], 0.12); s["kc"] = 0.03
        if s["id"] in ("arm", "thigh", "stifle", "forearm", "gaskin"): s["kc"] = 0.06   # (the darker legs fade in)
        S.append(s)
    d["head"] = xpt(d["head"][:3], Hc, KH, [0, 0, 0]) + [round(d["head"][3] * KH, 4)]
    for key in ("muzzle", "ears"):
        v = d[key]; d[key] = xpt(v[0:3], Hc, KH, [0, 0, 0]) + xpt(v[3:6], Hc, KH, [0, 0, 0]) + [round(x * KH, 4) for x in v[6:]]
    d["nose"] = xpt(d["nose"][:3], Hc, KH, [0, 0, 0]) + [round(d["nose"][3] * KH, 4)]
    d["eyes"] = xpt(d["eyes"][:3], Hc, KH, [0, 0, 0]) + [round(d["eyes"][3] * KH, 4)]
    E = sc["eyes"]
    d["sculpt"]["shape"] = list(S)
    ea = xpt(xpt(E["at"], [0, 0, 0], K, [0, 0, 0]), Hc, KH, [0, 0, 0])
    eye_on(d, S, ea[0], ea[1], round(E["r"] * K * KH, 4), zin=0.1, iris="@eye", pupil="bar", lid="@nose", sink=0.45)
    # ---- the COAT (no flank stripe: an Alpine ibex is a fairly even grey-brown) -- paints with wide, gradual edges:
    #      a slightly darker line down the back, a darker brown chest front, a paler belly
    bk = []
    for x in (0.46, 0.3, 0.15, 0.0, -0.15, -0.3, -0.44):
        h = ray_hit(d, S, [x, 1.5, 0.0], [x, 0.4, 0.0])
        bk.append(R4(add(h, [0, 1, 0], -0.01)) + [0.05 if -0.4 < x < 0.42 else 0.03])
    S.tube("backLine", bk, "@back", k=0.0, op="paint", kc=0.07)
    yb = ray_hit(d, S, [0.0, 0.0, 0], [0.0, 1.2, 0])[1]
    S.ell("bellyPale", R4([-0.04, yb - 0.02, 0.0]), [0.36, 0.1, 0.32], "@belly", rot=[0, 0, -4], op="paint", kc=0.08)
    cf = ray_hit(d, S, [1.2, 0.64, 0.0], [0.0, 0.64, 0.0])    # (the chest's front surface, between the forelegs)
    S.ell("chestFront", R4(add(cf, [1, 0, 0], -0.03)), [0.09, 0.2, 0.17], "@front", rot=[0, 0, 15], op="paint", kc=0.08)
    # ---- the BEARD (the billy's): a short pointed tuft under the chin
    def under(x): return ray_hit(d, S, [x, 0.4, 0], [x, 1.3, 0])[1]
    bx = [0.82, 0.85, 0.88]
    broot = [(x, under(x) + 0.012) for x in bx]
    beard = fringe("beard", broot, [(0.815, broot[0][1] - 0.06), (0.835, broot[1][1] - 0.1), (0.86, broot[1][1] - 0.075),
                                    (0.885, broot[2][1] - 0.03)],
                   "@beard", "head", 0.016, notch=0.35, slope=0.6, fair={"r": 0.008, "sink": 3}, pat="shag", when="billy")
    # ---- the HORNS: the billy's great scimitars -- from the brow, close together, up and sweeping back in one arc (about
    #      0.95 m along the curve), spreading a little, the KNOBS across their fronts; the nanny's short thin ones; the
    #      kid's buds
    B = horn0["pts"][1][:3]
    hornB = knob_horn("hornB", B, 98, 128, 0.95, B[2] + 0.012, 0.17, 0.04, 0.012, color="@hornc", mirror=True,
                      tip="@hornTip", tipAt=0.7, when="billy")
    hornN = knob_horn("hornN", B, 96, 70, 0.26, B[2], 0.06, 0.013, 0.006, knobs=False, n=9, color="@hornc",
                      mirror=True, tip="@hornTip", tipAt=0.7, when="nanny")
    hornK = knob_horn("hornK", B, 100, 30, 0.05, B[2], B[2] + 0.004, 0.012, 0.008, knobs=False, n=4, color="@hornc",
                      mirror=True, when="kid")
    sink_horns(d, [hornB, hornN, hornK])
    # (the ear: the chamois' cupped `fin` leaf, set out SIDEWAYS from the side of the head behind the horns, its
    #  hollow forward, body-coloured with a paler inside)
    #  (rooted HIGH on the back of the skull, behind the horn bases, so it stands clear of the thick neck)
    T = ray_hit(d, S, [0.735, 1.075, 0.0], [0.735, 1.075, 0.4]); T = add(T, [0, 0, 1], -0.008)
    ear0 = ear_onto(ear0, T, [-0.45, 0.55, 0.7], [0.7, -0.2, 0.5], 0.74, 1.2, color="@ear", inner="@earIn")
    tp = ear0["edge"][ear0.get("corners", [9])[0]]
    d["sculpt"]["shape"] = list(S) + [hornB, hornN, hornK, ear0, beard]
    d["variants"] = {
        "nanny": {"params": {"billy": False, "nanny": True, "kid": False}, "scale": 0.78,
                  "colors": {"body": "#9a8466", "ear": "#8a7458", "front": "#6e5a44", "neck": "#947e62", "back": "#86705a"}},
        "kid": {"params": {"billy": False, "nanny": False, "kid": True}, "scale": 0.45,
                "colors": {"body": "#a08a6c", "ear": "#907a5e", "front": "#7c6850", "neck": "#9a8468", "back": "#8e7a62"}}}
    d["_variants"] = ("VARIANTS (species.js variantDef): `nanny` -- .78 the billy's size, short thin horns, no beard, a "
                      "paler browner coat; `kid` -- .45, horn buds")
    d["sculpt"]["_about"] = (
        "THE ALPINE IBEX (Capra ibex; 2026-11-08, generator tools/creaturegen/ungulates/gen.py, on the deer frame): a "
        "billy of about 0.94 m at the shoulder -- a stocky wild goat: the chamois' sculpt (its sure-footed cloven legs, "
        "its body and its head) scaled 1.18, the trunk and neck deeper and broader (a deeper chest, a thicker neck and shoulders, the belly blended in smooth), the head 1.1 again, its face mask "
        "taken off. The HORNS (`horn`s, mirrored): great scimitars from the brow, close together, rising and sweeping "
        "back in one arc of about 0.95 m, spreading a little, with the KNOBS across their fronts -- a ridge every 5 cm (the "
        "radius up 20%, the section wider), shallow troughs between. A short pointed BEARD (a `fin` tuft under the chin). "
        "A fairly even grey-brown with no flank stripe: a slightly darker line down the back, a darker brown chest front and legs, a paler belly, every edge gradual (paints and `kc` ~7 cm); a goat "
        "ear about 12 cm long (the chamois' cupped `fin` leaf), set out sideways and back, a little up, its hollow forward and down, so its body-coloured outside reads in profile, body-coloured with a paler inside. Lives on the crags (index.html cragRange, as the chamois).")
    return d


ALL = {"moose": moose, "bison": bison, "ibex": ibex}

if __name__ == "__main__":
    for nm in (sys.argv[1:] or list(ALL)):
        d = ALL[nm]()
        save("mammals/" + nm, d)
        print("wrote", nm, len(d["sculpt"]["shape"]), "shapes", "(indexed)" if index_add("creatures/mammals/" + nm) else "")
