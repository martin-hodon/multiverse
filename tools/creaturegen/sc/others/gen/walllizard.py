# walllizard.py -- writes assets/creatures/others/wall-lizard.json: a common wall lizard (Podarcis muralis), 20 cm long.
# Run from anywhere: python3 tools/creaturegen/sc/others/gen/walllizard.py
# Two passes, like snake.py: the body is written without its markings, the skin is probed along rays (lizprobe.mjs, node)
# and the markings -- paints, colour only -- are laid ON it and the file written again.
# Rig: body (the rear trunk, the root) -> chest (the front trunk) -> nape -> head; body -> caud1..4 (the tail, NOT named
# tail*: skeleton.js turns head|neck|tail parts on the world clock; these swing on the gait clock and fade standing, amp);
# sprawled legs (crocodile plan: the upper bone out sideways swinging fore and aft, the lower down, a lift on the swing).
# Toes and fingers are DETAILS (bodyspec: thinner than .8 cells -> smooth lathes with a dark claw), rooted in the palms.
import sys, os, json, subprocess, random
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import *
import common
def _rnd6(v):   # (a 20 cm lizard: written to the micrometre, not common.rnd's tenth of a millimetre -- its toes are 0.2 mm thick)
    if isinstance(v, float): return round(v, 6)
    if isinstance(v, list): return [_rnd6(x) for x in v]
    if isinstance(v, dict): return {k: _rnd6(x) for k, x in v.items()}
    return v
common.rnd = _rnd6
PI = math.pi
HERE = __file__.rsplit("/", 1)[0]
REPO = "/home/martin/store/apps/multiverse"
OUT = "others/wall-lizard.json"

def sub(a, b): return [a[i] - b[i] for i in range(3)]
def nrm(v):
    l = math.sqrt(sum(x * x for x in v)) or 1
    return [x / l for x in v]
def roty(v, deg):   # turn a vector about y (+: from +x toward +z)
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return [v[0] * c - v[2] * s, v[1], v[0] * s + v[2] * c]
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]

Y0 = .0080                       # the trunk's axis above the ground
B = [.012, Y0, 0]                # body (root): the rear trunk
C = [.022, Y0, 0]                # chest: the front trunk, turning about the middle of the back
N = [.0445, Y0 + .0004, 0]       # nape
HD = [.0525, Y0 + .0013, 0]      # head: its pivot behind the skull
TX = [0.0, -.030, -.062, -.096]  # caud1..4 roots; the tip at -.1325
TIP = -.1325
# the tail's radius and axis height along x
RT = [(.004, .0036), (0.0, .0033), (-.01, .0029), (-.02, .0025), (-.03, .0021), (-.045, .0017), (-.06, .0014), (-.075, .00115),
      (-.09, .00092), (-.105, .0007), (-.118, .00048), (-.127, .0003), (TIP, .00008)]
YT = [(.004, Y0 - .0002), (0.0, Y0 - .0004), (-.01, .0062), (-.02, .0046), (-.03, .0031), (-.045, .00205)]
def interp(T, x):
    if x >= T[0][0]: return T[0][1]
    for (x0, v0), (x1, v1) in zip(T, T[1:]):
        if x1 <= x <= x0: return v0 + (v1 - v0) * (x - x0) / (x1 - x0)
    return T[-1][1]
def tr(x): return interp(RT, x)
def ty(x): return interp(YT, x) if x >= -.045 else tr(x) + .00025

# ---- the legs' joints (left; the right mirrored)
FS, FE, FW = [.0385, .0078, .0040], [.0362, .0058, .0122], [.0394, .0016, .0138]     # shoulder, elbow, wrist
HH, HK, HA = [.0058, .0077, .0040], [.0084, .0066, .0136], [.0030, .0018, .0162]     # hip, knee, ankle
HAND = nrm([math.cos(math.radians(30)), 0, math.sin(math.radians(30))])               # the hand points forward-out
FOOT = nrm([math.cos(math.radians(48)), 0, math.sin(math.radians(48))])               # the foot out to the side and forward

def tube(a, b, r1, r2):
    return {"a": a, "c": lerp(a, b, .5), "b": b, "r1": r1, "r2": r2}
SW = 9          # the walk: the body's swing (deg), the legs' sweep, the tail's wave
parts = [
    {"id": "body", "parent": None, "shape": "tube", "size": tube([-.008, 0, 0], [.01, 0, 0], .0055, .0055), "pos": B, "color": "@back"},
    {"id": "chest", "parent": "body", "shape": "tube", "size": tube([0, 0, 0], [.018, 0, 0], .0055, .005), "pos": sub(C, B), "color": "@back",
     "anim": {"axis": "y", "deg": SW, "speed": .9, "phase": 0, "amp": True}},
    {"id": "nape", "parent": "chest", "shape": "tube", "size": tube([0, 0, 0], [.008, 0, 0], .004, .004), "pos": sub(N, C), "color": "@back",
     "anim": {"axis": "y", "deg": SW * .8, "speed": .9, "phase": PI, "amp": True}},   # (the head held on its line while the chest swings)
    {"id": "head", "parent": "nape", "shape": "tube", "size": tube([0, 0, 0], [.015, -.001, 0], .0035, .001), "pos": sub(HD, N), "color": "@back"},
]
prev = "body"; at = B
for i, x in enumerate(TX):
    xe = TX[i + 1] if i + 1 < len(TX) else TIP
    p = [x, ty(x), 0]
    parts.append({"id": f"caud{i + 1}", "parent": prev, "shape": "tube", "size": tube([0, 0, 0], [xe - x, ty(xe) - ty(x), 0], tr(x), tr(xe)),
                  "pos": sub(p, at), "color": "@back",
                  "anim": {"axis": "y", "deg": [11, 13, 15, 17][i], "speed": .9, "phase": round(PI + .75 * (i + 1), 3), "amp": True}})
    prev = f"caud{i + 1}"; at = p
for S_, sz in (("L", 1), ("R", -1)):
    z = lambda v: [v[0], v[1], v[2] * sz]
    # (upper bones: a y swing, mirrored geometry makes it alternate: FL with HR. The lower bone lifts the foot outward
    #  on the forward swing only -- flick 1: the positive half of the sine -- its sign and phase per side)
    parts += [
        {"id": f"legF{S_}u", "parent": "chest", "shape": "tube", "size": tube([0, 0, 0], z(sub(FE, FS)), .001, .0008), "pos": z(sub(FS, C)), "color": "@back",
         "anim": {"axis": "y", "deg": 30, "speed": .9, "phase": 0, "amp": True}},
        {"id": f"legF{S_}l", "parent": f"legF{S_}u", "shape": "tube", "size": tube([0, 0, 0], z(sub(FW, FE)), .0008, .0006), "pos": z(sub(FE, FS)), "color": "@back",
         "anim": {"axis": "x", "deg": -14 * sz, "speed": .9, "phase": PI / 2 if sz > 0 else -PI / 2, "flick": 1, "amp": True}},
        {"id": f"legH{S_}u", "parent": "body", "shape": "tube", "size": tube([0, 0, 0], z(sub(HK, HH)), .0014, .001), "pos": z(sub(HH, B)), "color": "@back",
         "anim": {"axis": "y", "deg": 30, "speed": .9, "phase": PI, "amp": True}},
        {"id": f"legH{S_}l", "parent": f"legH{S_}u", "shape": "tube", "size": tube([0, 0, 0], z(sub(HA, HK)), .0009, .0006), "pos": z(sub(HK, HH)), "color": "@back",
         "anim": {"axis": "x", "deg": -14 * sz, "speed": .9, "phase": 3 * PI / 2 if sz > 0 else PI / 2, "flick": 1, "amp": True}},
    ]

sh = []
def S(id, **k):
    d = {"id": id}; d.update(k); sh.append(d); return d
# (scale textures: ROW SCALES (coatpat.js 32) in frames of their own -- pitch r x .05 metres: the back's granules .45 mm, the
#  ventral plates 1.6 mm; the tail's whorls finer toward the tip. (scales 17 floors its size at 3 mm: no use at this size))
# (the markings are a PATTERN of their own, coatpat.js 70-74 "lacerta": laid by the angle round the axis of the frame,
#  so the trunk's, the belly's, the head's, the legs' and the tail's shapes share one origin and axis)
TRUNKP = [{"when": "spotted", "v": 74}, {"when": "male", "v": 70}, {"when": "female", "v": 71}]
BODYPAT = {"pat": TRUNKP, "frame": {"o": [.022, Y0, 0], "u": [1, 0, 0], "r": .009}}
VENT = {"pat": TRUNKP, "frame": {"o": [.022, Y0, 0], "u": [1, 0, 0], "r": .03}}
# (the head, the legs and the tail in the TRUNK's frame too -- one pattern group, so no seam where they join it (a vertex
#  takes its pattern group flat: where two meet, a sawtooth): the shader tells them apart by where they lie -- past x .0485
#  the head, far from the axis a leg, behind the pelvis the tail, its axis lowered as the tail falls to the ground)

# ---- trunk: flattened, a flat belly, widest in the middle; the shoulders and the pelvis
S("trunkM", type="ell", c=[.0225, Y0 + .0001, 0], r=[.0150, .0036, .0059], k=.0018, color="@back", **BODYPAT)
S("trunkF", type="ell", bone="chest", c=[.0330, Y0 + .0002, 0], r=[.0100, .0035, .0053], k=.0018, color="@back", **BODYPAT)
S("trunkR", type="ell", c=[.0110, Y0, 0], r=[.0105, .0034, .0055], k=.0018, color="@back", **BODYPAT)
S("shoulders", type="ell", bone="chest", c=[.0378, Y0 + .0003, 0], r=[.0060, .0032, .0047], k=.0015, color="@back", **BODYPAT)
S("pelvis", type="ell", c=[.0050, Y0 - .0001, 0], r=[.0070, .0031, .0048], k=.0015, color="@back", **BODYPAT)
S("plastronF", type="ell", bone="chest", c=[.0305, Y0 - .0015, 0], r=[.0110, .0022, .0052], k=.0012, color="@back", **VENT)
S("plastronR", type="ell", c=[.0140, Y0 - .0015, 0], r=[.0120, .0022, .0053], k=.0012, color="@back", **VENT)
# ---- neck: narrower than the head and the trunk; the collar of big scales across the throat (a fold, its free edge back)
S("neck", type="ell", bone="nape", c=[.0465, Y0 + .0007, 0], r=[.0075, .0030, .0036], k=.0015, color="@back", **BODYPAT)
S("throat", type="ell", bone="nape", c=[.0478, Y0 - .0006, 0], r=[.0068, .0019, .0033], k=.0012, color="@back", **VENT)
S("collar", type="ell", bone="nape", c=[.0441, Y0 - .0019, 0], r=[.0011, .0006, .0033], rot=[0, 0, 12], k=.0005, color="@back", **VENT)
# ---- tail: round, a broad root behind the vent, lying on the ground for most of its length, whip-thin to its point
S("tailRoot", type="ell", c=[.0005, Y0 - .0006, 0], r=[.0065, .0029, .0038], k=.0015, color="@back", **BODYPAT)
CUTS = [(.004, -.038), (-.026, -.066), (-.058, -.100), (-.092, TIP)]
for i, (x0, x1) in enumerate(CUTS):
    xs = [x0 + (x1 - x0) * t / 6 for t in range(7)]
    S(f"tail{i + 1}", type="tube", bone=f"caud{i + 1}", pts=[[x, ty(x), 0, tr(x)] for x in xs], k=.0002, color="@back" if i == 0 else "@tail", **BODYPAT)
# (its last few millimetres too thin for the grid: a fine lathe on to the point, from inside the tail's own end)
S("tailTip", type="tube", bone="caud4", pts=[[x, ty(x), 0, r] for x, r in ((-.1272, .00025), (-.1300, .00016), (-.1320, .00008), (-.1338, .000015))], color="@tail")
# ---- head: pointed, a little flattened -- from above a long wedge, widest at the jaws' muscles and narrowing straight to
# a blunt point; in profile its top a gentle slope to the snout, the jaw line straight; the ear opening, the nostrils
H = "head"
# (a WEDGE: one flattened ellipsoid, then CUT -- a flat crown sloping down to the snout, a flat chin, and each side
#  sliced back from the snout at 18 deg: face-on wider than tall and flat-topped, from above a long pointed triangle
#  widest at the jaws' muscles behind the eyes, in profile low with the top falling gently to the snout. The head's
#  shapes go FIRST in the list, so the cuts carve only them -- the neck and the throat are laid on after. (The cuts carry
#  the pattern too: a smooth cut lends the face it leaves its own attributes)
h0 = len(sh)
S("headM", type="ell", bone=H, c=[.0556, .0091, 0], r=[.0098, .0037, .0048], k=.0012, color="@head", **BODYPAT)
S("temple", type="ell", bone=H, c=[.0516, .0083, .0026], r=[.0032, .0024, .0024], k=.0012, color="@head", mirror=True, **BODYPAT)
S("cutTop", type="box", bone=H, op="sub", c=[.0588, .0144, 0], r=[.0100, .0040, .0080], rot=[0, 0, -12], k=.0006, color="@head", **BODYPAT)
S("cutChin", type="box", bone=H, op="sub", c=[.0589, .0029, 0], r=[.0100, .0040, .0080], rot=[0, 0, 6], k=.0005, color="@head", **BODYPAT)
S("cutSide", type="box", bone=H, op="sub", c=[.0621, .0090, .0067], r=[.0090, .0060, .0040], rot=[0, 19.5, 0], k=.0006, color="@head", mirror=True, **BODYPAT)
# (and the crown's edges bevelled back over the temples: face-on the flat top narrower than the jaws, the sides sloping)
S("cutBevel", type="box", bone=H, op="sub", c=[.0560, .0124, .0062], r=[.0100, .0030, .0060], rot=[49.7, 0, 0], k=.0007, color="@head", mirror=True, **BODYPAT)
sh[:] = sh[h0:] + sh[:h0]
S("naris", type="sphere", bone=H, op="sub", c=[.0641, .0091, .0011], r=.00026, k=.0001, color="@mouth", mirror=True)

# ---- legs: sprawled -- the upper bone out to the side, the lower down to a flat palm; slender round toes (details)
def limb(u, l, s0, e, w, r0, r1, r2, r3):
    S(u, type="tube", bone=u, pts=[s0 + [r0], lerp(s0, e, .3) + [r0 * .9], lerp(s0, e, .65) + [(r0 + r1) / 2], e + [r1]], k=.0012, color="@limb", mirror=True, **BODYPAT)
    S(l, type="tube", bone=l, pts=[e + [r1 * .95], lerp(e, w, .5) + [r2], w + [r3]], k=.0006, color="@limb", mirror=True, **BODYPAT)
limb("legFLu", "legFLl", [.0372, .0077, .0030], FE, FW, .00145, .00098, .00076, .00060)
limb("legHLu", "legHLl", [.0060, .0076, .0030], HK, HA, .00215, .00112, .00084, .00058)
PALM = [FW[0] + HAND[0] * .0006, .0006, FW[2] + HAND[2] * .0006]
S("palm", type="ell", bone="legFLl", c=PALM, r=[.0013, .00040, .00080], rot=[0, -30, 0], k=.0007, color="@limb", mirror=True, **BODYPAT)
SOLE = [HA[0] + FOOT[0] * .0017, .0006, HA[2] + FOOT[2] * .0017]
S("sole", type="ell", bone="legHLl", c=SOLE, r=[.0025, .00046, .0010], rot=[0, -48, 0], k=.0006, color="@limb", mirror=True, **BODYPAT)
S("heel", type="ell", bone="legHLl", c=[HA[0], .0008, HA[2]], r=[.0008, .0006, .0008], k=.0005, color="@limb", mirror=True)

def toe(id_, bone, base, d, L, r0, y0):
    # a toe: from inside the palm out along d, sloping down, tapering a little, then the claw (dark, curved down to the ground)
    pts = []
    for t, rr, yy in ((0, r0, y0), (.35, r0 * .9, y0 - .00012), (.65, r0 * .78, y0 - .00022), (.84, r0 * .62, y0 - .00032), (.94, r0 * .4, y0 - .00046), (1.0, .000018, .00004)):
        p = add(base, d, L * t); pts.append([p[0], yy, p[2], rr])
    S(id_, type="tube", bone=bone, pts=pts, color="@toe", tip="@claw", tipAt=.82, mirror=True)
for i, (ang, L) in enumerate([(-58, .0018), (-26, .0028), (0, .0034), (23, .0036), (55, .0024)]):
    d = roty(HAND, ang); base = add(PALM, roty(HAND, ang * .6), .00055)
    toe(f"finger{i + 1}", "legFLl", base, d, L, .00022, .00060)
for i, (bang, m, ang, L) in enumerate([(-30, .0023, -38, .0024), (-13, .0030, -20, .0037), (0, .0034, -5, .0050), (10, .0033, 11, .0068), (58, .0010, 64, .0036)]):
    d = roty(FOOT, ang); base = add([HA[0], .0006, HA[2]], roty(FOOT, bang), m)
    toe(f"toe{i + 1}", "legHLl", base, d, L, .00023, .00060)

# ==== the MARKINGS: paints (colour only), each an ellipsoid laid ON the probed skin -- a patch (x0..x1 along the body,
# phi0..phi1 round it from the dorsal midline toward the animal's left; the right side mirrored with its own dice).
# Zones round the trunk: the back (vertebral, paravertebral) to ~48 deg, the pale dorsolateral stripe ~48-60, the dark
# flank band ~60-106, the pale lower stripe ~106-117, the belly beyond ~124 (the outer ventral row ~124-136: a male's blue)
def axis_y(x, reg):
    if reg == "h": return .0092
    if x > .040: return Y0 + .0006
    return Y0 if x >= .004 else ty(x)
def bone_at(x, reg):
    if reg == "h": return "head"
    if x > .0415: return "nape"
    if x > .022: return "chest"
    if x > 0: return "body"
    return "caud" + str(1 + sum(1 for t in TX[1:] if x < t))
def ray(x, phi, reg):
    a = math.radians(phi); return [x, axis_y(x, reg), 0, 0, math.cos(a), math.sin(a)]
MK = []   # (id, reg, x0, x1, phi0, phi1, colour, when, extra)
def mk(id_, reg, x0, x1, p0, p1, col, when=None, **kw):
    MK.append(dict(id=id_, reg=reg, x0=x0, x1=x1, p0=p0, p1=p1, col=col, when=when, **kw))
def strip(id_, reg, x0, x1, p0, p1, col, rng, when=None, step=.0034, gap=0, jit=3, grow=None):
    # a stripe of overlapping patches, its edges a little ragged; `gap`: the chance of a break; grow(x) -> (p0, p1) along it
    x = x0; j = 0
    while x > x1:
        L = step * rng.uniform(.9, 1.25); q0, q1 = grow(x) if grow else (p0, p1)
        if rng.random() >= gap:
            mk(f"{id_}{j}", reg, x, x - L, q0 + rng.uniform(-jit, jit), q1 + rng.uniform(-jit, jit), col, when)
        x -= step * rng.uniform(.6, .85); j += 1
def side(sg, rng):
    # (the back's, the flanks' and the tail's markings are the lacerta pattern; these are the colours it is laid over
    #  and the head's, which the pattern does not reach)
    S_ = "L" if sg > 0 else "R"; P = lambda a: a * sg
    # the belly and the underside of the tail, pale; the throat its own colour; the collar
    x = .0405
    while x > -.004:
        mk(f"belly{S_}{int(x * 1e4)}", "t", x + .0025, x - .0025, P(124), P(181), "@belly"); x -= .0036
    x = -.003
    while x > -.100:
        L = .006 if x > -.04 else .009
        mk(f"tailU{S_}{int(-x * 1e4)}", "t", x + L * .55, x - L * .55, P(128 if x > -.03 else 120), P(181), "@tailU"); x -= L * .7
    for x in (.0475, .0457, .0441):
        mk(f"throat{S_}{int(x * 1e4)}", "t", x + .0012, x - .0012, P(120), P(181), "@throat")
    mk(f"collar{S_}", "t", .0451, .0433, P(112), P(181), "@collar")
side(1, random.Random(5)); side(-1, random.Random(9))

def marks():
    # probe each patch's middle and its four edges, and lay an ellipsoid over it
    rays = [[.0512, .0090, 0, 0, 0, 1], EYE_FROM + sub(EYE_AT, EYE_FROM)]
    for m in MK:
        xm, pm = (m["x0"] + m["x1"]) / 2, (m["p0"] + m["p1"]) / 2
        m["_r"] = len(rays); rays += [ray(xm, pm, m["reg"]), ray(m["x0"], pm, m["reg"]), ray(m["x1"], pm, m["reg"]), ray(xm, m["p0"], m["reg"]), ray(xm, m["p1"], m["reg"])]
    import tempfile; tmp = tempfile.mkdtemp(); T = tmp + "/rays.json"; O = tmp + "/hits.json"
    json.dump(rays, open(T, "w"))
    subprocess.run(["node", "--import", REPO + "/tools/creaturegen/reg.mjs", HERE + "/lizprobe.mjs", "wall lizard", T, O], check=True, cwd=REPO + "/tools/creaturegen")
    hits = json.load(open(O)); e = hits[0]
    out = lids(hits[1])
    out += [{"id": "ear", "type": "sphere", "bone": "head", "op": "sub", "c": add(e[:3], e[3:], -.00008), "r": .00078, "k": .00015, "color": "@tymp", "mirror": True}]
    for m in MK:
        h = hits[m["_r"]:m["_r"] + 5]
        if any(q is None for q in h): print("missed", m["id"]); continue
        c, n = h[0][:3], nrm(h[0][3:])
        o = [ (m["x0"] + m["x1"]) / 2, axis_y((m["x0"] + m["x1"]) / 2, m["reg"]), 0]
        rl = math.dist(c, o)
        al = nrm(sub(h[1][:3], h[2][:3])); ar = nrm(cross(n, al)); al = cross(ar, n)
        La = max(math.dist(h[1][:3], h[2][:3]) / 2, .00025); Lr = max(math.dist(h[3][:3], h[4][:3]) / 2, .00018)
        if m.get("thin"): Lr = .00014
        dep = min(.5 * rl, .0012)
        q = {"id": m["id"], "type": "ell", "bone": bone_at(c[0], m["reg"]), "op": "paint", "c": c, "r": [La * 1.08, Lr * 1.08, dep],
             "axes": [al, ar, n], "k": .00015, "kc": .0003 if m.get("soft") else .00015, "color": m["col"]}
        if m["when"]: q = {"when": m["when"], **q}
        out.append(q)
    return out

def lids(hit):
    # the EYELIDS: a fold over the eye and a softer one under it, laid on the probed skin at the eye (ellipsoids in the
    # head's own colour and pattern; the socket, hardly wider than the eyeball, leaves them over its rim -- only an almond
    # of the dark eye showing between them; after gen_theropods.eyelids)
    c, n = hit[:3], nrm(hit[3:])
    t1 = nrm(add([1, 0, 0], n, -n[0])); t2 = cross(n, t1)
    if t2[1] < 0: t2 = [-v for v in t2]
    r = EYE_R
    up = {"id": "lidUp", "type": "ell", "bone": "head", "c": add(add(c, t2, .82 * r), n, -.06 * r), "r": [1.55 * r, .52 * r, .8 * r], "axes": [t1, t2, n],
          "k": .3 * r, "kc": .1 * r, "color": "@head", "mirror": True, **BODYPAT}
    lo = {"id": "lidLo", "type": "ell", "bone": "head", "c": add(add(c, t2, -.88 * r), n, -.1 * r), "r": [1.35 * r, .44 * r, .7 * r], "axes": [t1, t2, n],
          "k": .3 * r, "kc": .1 * r, "color": "@head", "mirror": True, **BODYPAT}
    return [up, lo]

EYE_AT, EYE_FROM, EYE_R, EYE_SINK = [.0584, .0099, .0040], [.0584, .0097, 0], .00072, .76
COLORS = {"back": "#7a6248", "head": "#76604a", "dark": "#2a2018", "pale": "#cfc29c", "pale2": "#b4a07a", "belly": "#de8c4c",
          "throat": "#ead2b4", "tailU": "#d8c6a4",
          "blue": "#2f78c4", "limb": "#6a5640", "toe": "#86705a", "claw": "#2a221c", "mouth": "#3a2c22", "lip": "#c8b894", "tymp": "#4e4234",
          "tail": "#6e5c48", "collar": "#e8b888", "lid": "#3a2e24", "eye": "#3a2414", "eyeDark": "#140e0a"}
FEMALE = {"collar": "#e6dcc4", "back": "#7e6a52", "head": "#7a6650", "dark": "#3a2c20", "pale": "#d4c8a4", "belly": "#ece4cc", "throat": "#efe8d6", "tailU": "#e0d6bc"}
GREEN = {"back": "#5c6a34", "head": "#5e6638", "tail": "#6a5c48", "pale": "#a0a46c", "pale2": "#868e56", "belly": "#e8b080", "throat": "#efe0c4"}
d = {
    "name": "wall lizard",
    "_about": "SCULPTED (2026-11-07, tools/creaturegen/sc/others/gen/walllizard.py): a common wall lizard (Podarcis muralis), 20 cm long, the tail two thirds of it -- a slender flattened trunk on four sprawled legs (the upper bones out to the side, the hind longer), five long thin clawed toes on each foot (the hind 4th the longest), a pointed, slightly flattened head on a distinct neck with the ear opening behind the jaw and small dark eyes, the collar of big scales across the throat, a whip tail tapering to a point; brown with dark markings, pale below. It walks with its body and tail swinging side to side (the chest, the nape held against it, the tail's four links a beat apart -- all faded out standing) and stands still with its head lifted (graze < 0: the head raised about nodPivot)",
    "kind": "parts",
    "flags": {"print": "none", "legLen": .03, "shy": 3, "graze": -.25, "nodPivot": sub(HD, N)},
    "colors": COLORS,
    "params": {"male": True, "female": False, "spotted": False},
    "coats": [{"name": "male"}, {"name": "male"},
              {"name": "female", "params": {"male": False, "female": True}, "colors": FEMALE},
              {"name": "female", "params": {"male": False, "female": True}, "colors": FEMALE},
              {"name": "green-backed male", "params": {"spotted": True}, "colors": GREEN}],
    "variants": {"male": {"params": {}, "colors": {}},
                 "female": {"params": {"male": False, "female": True}, "colors": FEMALE},
                 "green-backed": {"params": {"spotted": True}, "colors": GREEN}},
    "parts": parts,
    "sculpt": {
        "keep": [],
        "patScale": .055,
        "mesh": {"cell": .00034, "tris": [8400, 2600], "anchor": 0, "focus": {"head": 4, "legFLl": 2, "legHLl": 2}},
        "shape": sh,
        "eyes": {"at": EYE_AT, "from": EYE_FROM, "r": EYE_R, "color": "@eyeDark", "iris": "@eye", "pupil": "round", "lid": "@head", "sink": EYE_SINK, "socket": 1.02},
    },
}

if __name__ == "__main__":
    dump(OUT, d)                 # (pass 1: the body bare, to be probed)
    P = marks(); sh += P
    dump(OUT, d)
    print(len(sh), "shapes,", len(P), "paints")
