#!/usr/bin/env python3
# PTERANODON LONGICEPS generator (2026-11-06, round 2) -> assets/creatures/dinosaurs/pteranodon.json
# A rig of parts (kind "parts") with a sculpt overlay. The REST pose stands on all fours on the folded wings (the
# metacarpal the front leg, the hand's three fingers on the ground ahead, the wing finger folded back tight along the
# metacarpal and the forearm); FLIGHT (skeleton.js flightPose) is each part's flyRot: the body levelled, the neck reached
# forward, the legs spread out behind, the wing spread. The wing's skin is one MEMBRANE (bodymesh.js membraneMesh) a side:
#  - a grid of streamwise CHORDS from the leading edge (arm, metacarpal, wing finger) back to the trailing edge;
#  - a FREE chord (its trailing end loose) FURLS: it has one bone T of its own, a child of its leading bone, hinged above
#    the chord's middle, folded at rest and in line with the leading bone aloft; each point of the chord is skinned
#    [lead, T, w] with w = u (1 - W / l) (u: how far along the chord) and placed at rest where that blend carries it
#    exactly onto its flight position -- so aloft the skin is exact, and at rest the chord closes up to W beside its bone;
#  - a chord whose trailing end is on the LEG (the inner wing: humerus to thigh and shin, the membrane ending at the
#    ankle) is skinned [arm, leg, u], its rest points solved the same exact way.
# All of the wing beats on ONE bone (wRoot*) about the body's long axis through the shoulder: the skin's root runs along
# that axis (shoulder to hip), so it never leaves the flank however the wing beats.
import sys, json, math
import numpy as np
SP = "/home/martin/store/apps/multiverse/tools/creaturegen/"
sys.path.insert(0, SP + "sc/carn/gen")
from lib import dumps, rnd
REPO = "/home/martin/store/apps/multiverse/"
OUT = REPO + "assets/creatures/dinosaurs/pteranodon.json"
import os; OUT = os.environ.get("PTERO_OUT", OUT)   # (a trial build elsewhere)
D = math.pi / 180
V = lambda *a: np.array(a, float)

# ---------------------------------------------------------------- rotation helpers (three.js Euler XYZ: R = Rx Ry Rz)
def Rx(a): c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def Ry(a): c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def Rz(a): c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def e2m(e): return Rx(e[0] * D) @ Ry(e[1] * D) @ Rz(e[2] * D)
def m2e(m):
    y = math.asin(max(-1, min(1, m[0, 2])))
    if abs(m[0, 2]) < 0.9999999: x = math.atan2(-m[1, 2], m[2, 2]); z = math.atan2(-m[0, 1], m[0, 0])
    else: x = math.atan2(m[2, 1], m[1, 1]); z = 0.0
    return np.array([x, y, z]) / D
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v) or 1)
def frame(y, zh):   # columns x, y, z: y along the bone, z as near the hint as it can be
    y = unit(y); zh = np.asarray(zh, float); z = unit(zh - (zh @ y) * y); return np.column_stack([np.cross(y, z), y, z])
def frame_x(y, xh):   # y along the bone, x (the wing's TRAILING side) as near the hint as it can be
    y = unit(y); xh = np.asarray(xh, float); x = unit(xh - (xh @ y) * y); return np.column_stack([x, y, np.cross(x, y)])
def rot_between(a, b):   # the least rotation taking direction a to b
    a, b = unit(a), unit(b); v = np.cross(a, b); c = float(a @ b)
    if c > 1 - 1e-9: return np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]); return np.eye(3) + K + K @ K / (1 + c)
def wrap(a): return (a + 180) % 360 - 180
def lerp(a, b, t): return np.asarray(a, float) + (np.asarray(b, float) - np.asarray(a, float)) * t
def hx(c): return int(c[1:], 16)
def dirn(dx, dy, dz): return unit(V(dx, dy, dz))

# ---------------------------------------------------------------- the rig: parts with REST and FLIGHT world frames
class Rig:
    def __init__(s): s.P = {}; s.order = []
    def add(s, id, parent, pos, Rr, Rf, **kw):
        """pos in the parent's frame (the same in both poses); Rr, Rf: world rotations at rest and aloft"""
        pos = np.asarray(pos, float)
        if parent: pp = s.P[parent]; Or = pp["Or"] + pp["Rr"] @ pos; Of = pp["Of"] + pp["Rf"] @ pos
        else: Or = Of = pos
        s.P[id] = dict(id=id, parent=parent, pos=pos, Rr=Rr, Rf=Rf, Or=Or, Of=Of, kw=kw); s.order.append(id); return s.P[id]
    def local(s, id, which):
        p = s.P[id]; R = p["R" + which]
        return R if not p["parent"] else s.P[p["parent"]]["R" + which].T @ R
    def to_rest(s, id, pf):   # a point aloft, carried rigidly by bone id back to where the rest pose puts it
        p = s.P[id]; return p["Or"] + p["Rr"] @ (p["Rf"].T @ (np.asarray(pf, float) - p["Of"]))
    def rest_pt(s, id, loc): p = s.P[id]; return p["Or"] + p["Rr"] @ np.asarray(loc, float)
    def fl_local(s, id, pf): p = s.P[id]; return p["Rf"].T @ (np.asarray(pf, float) - p["Of"])
    def skin_map(s, id):   # rest -> flight, as (linear, translation): what skinning does to a point on this bone aloft
        p = s.P[id]; M = p["Rf"] @ p["Rr"].T; return M, p["Of"] - M @ p["Or"]
    def parts(s):
        out = []
        for id in s.order:
            p = s.P[id]; kw = dict(p["kw"]); er = m2e(s.local(id, "r")); ef = m2e(s.local(id, "f"))
            anim = kw.pop("anim", None); fly = np.array([wrap(a) for a in (ef - er)])
            if anim and anim.get("wing"): fly[0] = ef[0]   # (a wing part's x aloft is its flight rx outright: FLIGHT.arm 0)
            q = {"id": id, "parent": p["parent"], "shape": kw.pop("shape", "sphere"), "size": kw.pop("size", {"r": .01}), "pos": [float(v) for v in p["pos"]]}
            for k in ("geomRot", "pivot"):
                if k in kw: q[k] = kw.pop(k)
            q["rot"] = [float(v) for v in er]
            q["color"] = kw.pop("color", 0x808080)
            if anim: q["anim"] = anim; q["fold"] = [0, 0, 0]
            if np.abs(fly).max() > 1e-3: q["flyRot"] = [float(v) for v in fly]
            q.update(kw)
            out.append(rnd(q, 4))
        return out

# ---------------------------------------------------------------- proportions (metres; a 6 m male)
TH = 30.0                     # the body's rest pitch, nose up
HC = 0.585                    # the body's centre, rest height
S_b = V(0.10, 0.0, 0.07)      # the shoulder (and the skin's root: the axis the wing beats about runs back from it along x)
H_b = V(-0.20, -0.01, 0.052)  # the hip joint
Hm_b = V(-0.215, 0.0, 0.05)   # the skin's root at the hip: on the beat axis
N_b = V(0.17, 0.05, 0.0)      # the neck's root
N0_b = V(0.205, 0.0, 0.035)   # the propatagium's root, in the neck's side (2026-11-07: z .07 -> .035 -- at .07 it stood ~17 mm
                             #  proud of the raised neck at rest and the folded propatagium showed as a dark sliver on the chest)
LH, LF, LM = 0.30, 0.47, 0.68 # humerus, forearm, metacarpal IV
PH = [0.64, 0.46, 0.31, 0.18] # the wing finger's phalanges (span ~5.95 m)
LFE, LTI, LMT = 0.21, 0.29, 0.085   # femur, tibia, metatarsus
NK = [0.13, 0.12, 0.12]       # the neck: three short links, 0.37 m
UP = V(0, 1, 0); ZL = V(0, 0, 1)

Rb_r = Rz(TH * D); Rb_f = np.eye(3)
OB = V(0, HC, 0)
def body_rest(p): return OB + Rb_r @ np.asarray(p, float)
def body_fl(p): return OB + np.asarray(p, float)

# ---- FLIGHT planform (body frame, left wing): the leading edge's joints
Sf = body_fl(S_b)
Ef = Sf + LH * dirn(-0.20, 0.10, 1)
Wf = Ef + LF * dirn(0.42, 0.06, 1)
Kf = Wf + LM * dirn(-0.05, 0.07, 1)
fing = [Kf]
for L, a, dy in zip(PH, (12, 18, 25, 33), (0.04, 0.0, -0.04, -0.07)):
    fing.append(fing[-1] + L * unit(V(-math.sin(a * D), dy, math.cos(a * D))))
Tipf = fing[-1]

# ---- REST stance (world): the knuckle on the ground ahead, the metacarpal near upright (the front leg), the forearm run
# back from the wrist to the elbow at the shoulder's side, the wing finger folded back up along them
def two_bone(A, B, l1, l2, hint):   # the joint between A and B, l1 from A and l2 from B, bent toward hint
    d = np.linalg.norm(B - A); u = unit(B - A); d = min(d, l1 + l2 - 1e-6)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d); h = math.sqrt(max(0, l1 * l1 - a * a))
    n = unit(hint - (hint @ u) * u); return A + u * a + n * h
Sr = body_rest(S_b)
Kr = V(0.40, 0.06, 0.25)
Wr = Kr + LM * dirn(-0.10, 1, 0.02)
Er = two_bone(Sr, Wr, LH, LF, dirn(-0.6, -0.35, 0.72))   # (the elbow back and down at the flank, below the shoulder)
Jr = Kr + PH[0] * unit(unit(Wr - Kr) + V(-0.25, 0, 0.31))   # the finger's first joint: up behind the metacarpal and outside it, at the wrist
FIN2r = dirn(-0.77, 0.60, -0.13)                           # the rest of the finger: back along the forearm, outside it and a little up

# ---------------------------------------------------------------- the skeleton
R = Rig()
C = {"body": "#d6d1c6", "back": "#b9b3a7", "belly": "#e6e2d8", "neck": "#d3cec3", "head": "#d4cdbd", "face": "#d6ccb4", "beak": "#cfbf98", "jaw": "#c2b088",
     "beakTip": "#9c8a64", "crest": "#9b4a2c", "crestBase": "#b0603a", "crestEdge": "#6a2c1c", "mem": "#57473c", "arm": "#a59a8b", "bone": "#7a6a59", "limb": "#85786a",
     "leg": "#9a9184", "foot": "#6f665c", "claw": "#2a2420", "eye": "#1c130c", "lid": "#5e554a", "mouth": "#3e3224"}
R.add("body", None, OB, Rb_r, Rb_f, shape="capsule", size={"r": 0.1, "len": 0.3}, geomRot=[0, 0, 90], color=hx(C["body"]))

# the wing (left; the right one mirrored after). Aloft every wing bone's z is the wing's top (UP), its x the trailing side.
R.add("wRootL", "body", S_b, Rb_r, Rb_f, anim={"axis": "x", "deg": 2.2, "speed": 0.62, "phase": 0, "wing": True, "side": 1})
R.add("wArmL", "wRootL", [0, 0, 0], frame_x(Er - Sr, V(-1, -0.3, 0)), frame(Ef - Sf, UP))
R.add("wForeL", "wArmL", [0, LH, 0], frame_x(Wr - Er, V(0, 0.6, 0.8)), frame(Wf - Ef, UP))
# (the UPSTROKE: the hand swept back and let droop at the wrist, the outer finger more -- flyUp, signs found below)
R.add("wMcL", "wForeL", [0, LF, 0], frame_x(Kr - Wr, V(-0.5, 0, 0.85)), frame(Kf - Wf, UP))
R.add("wFingL", "wMcL", [0, LM, 0], frame_x(Jr - Kr, V(0.5, 0, -0.85)), frame(fing[1] - Kf, UP))
R.add("wFing2L", "wFingL", [0, PH[0], 0], frame_x(FIN2r, V(0, -0.7, -0.7)), frame(fing[2] - fing[1], UP))
# the pteroid (at the wrist): folded back along the forearm at rest, forward and in aloft (the propatagium's spar)
PTL = 0.16
Pdir_f = dirn(0.62, -0.02, -0.78)
R.add("wPterL", "wForeL", [0, LF, 0], frame_x(Er - Wr, V(0, 1, 0)), frame(Pdir_f, UP))
Ptip_f = Wf + PTL * Pdir_f
# the three free fingers, at the knuckle: on the ground pointing forward at rest, laid forward along the leading edge aloft
DIG = []
for i, (a_r, L) in enumerate(((-12, 0.075), (6, 0.085), (24, 0.08))):
    rest_d = dirn(math.cos(a_r * D), -0.12, math.sin(a_r * D) + 0.1)
    fl_d = unit(unit(Wf - Kf) * 0.8 + V(0.35, 0, 0) + V(0, 0.02 * (i - 1), 0))
    nm = "wDig" + "ABC"[i] + "L"
    R.add(nm, "wMcL", [0, LM, 0], frame(rest_d, UP), frame(fl_d, UP))
    DIG.append((nm, L))

# the flex of the upstroke: find the signs that sweep the hand BACK and let it droop DOWN (in flight, about the bone)
def flex_for(id, sweep, droop):
    p = R.P[id]; par = R.P[p["parent"]]; loc = par["Rf"].T @ p["Rf"]; e = m2e(loc)
    best = None
    for sx in (1, -1):
        for sz in (1, -1):
            d = np.array([sx * droop, 0, sz * sweep]); Rn = par["Rf"] @ e2m(e + d); y = Rn[:, 1]; y0 = p["Rf"][:, 1]
            score = -(y - y0)[0] * sweep - (y - y0)[1] * droop   # back (-x) and down (-y)
            if best is None or score > best[0]: best = (score, d)
    return [float(v) for v in best[1]]
R.P["wMcL"]["kw"]["flyUp"] = flex_for("wMcL", 14, 9)
R.P["wFing2L"]["kw"]["flyUp"] = flex_for("wFing2L", 9, 8)

# the legs: standing at rest, spread out and back aloft (they hold the skin's inner trailing edge out to the ankle)
Hr = body_rest(H_b); Hf = body_fl(H_b)
Ar = V(Hr[0] + 0.0, 0.048, 0.11)
Knr = two_bone(Hr, Ar, LFE, LTI, dirn(1, 0, 0.15))
Knf = Hf + LFE * dirn(-0.55, -0.06, 0.83)
Af = Knf + LTI * dirn(-0.78, 0.0, 0.62)
FOOTr = dirn(1, -0.06, 0.12); FOOTf = dirn(-0.9, 0.08, 0.3)
R.add("thighL", "body", H_b, frame(Knr - Hr, dirn(0, 0, 1)), frame(Knf - Hf, UP))
R.add("shinL", "thighL", [0, LFE, 0], frame(Ar - Knr, dirn(0, 0, 1)), frame(Af - Knf, UP))
R.add("footL", "shinL", [0, LTI, 0], frame(FOOTr, UP), frame(FOOTf, UP))

# the neck and head: a gentle S at rest, the head carried high; reached forward aloft
Nr = body_rest(N_b); Nf = body_fl(N_b)
def ang(a): return dirn(math.cos(a * D), math.sin(a * D), 0)
nkr = [ang(52), ang(80), ang(50)]
nkf = [ang(12), ang(5), ang(-2)]
R.add("nkA", "body", N_b, frame(nkr[0], ZL), frame(nkf[0], ZL))
R.add("nkB", "nkA", [0, NK[0], 0], frame(nkr[1], ZL), frame(nkf[1], ZL))
R.add("nkC", "nkB", [0, NK[1], 0], frame(nkr[2], ZL), frame(nkf[2], ZL))
HEADr, HEADf = -7.0, -5.0   # the jaw line's pitch (degrees, + up)
R.add("head", "nkC", [0, NK[2], 0], Rz(HEADr * D), Rz(HEADf * D))

# ---------------------------------------------------------------- the membranes (flight geometry, body frame)
def cr(P, n=12):   # a Catmull-Rom polyline through P
    P = [np.asarray(p, float) for p in P]; out = []
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(0, i - 1)], P[i], P[i + 1], P[min(len(P) - 1, i + 2)]
        for j in range(n):
            t = j / n
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1]); return np.array(out)
def at_z(line, z):   # the point of a polyline (monotonic in z) at that z
    zs = line[:, 2]
    if z <= zs[0]: return line[0].copy()
    if z >= zs[-1]: return line[-1].copy()
    i = int(np.searchsorted(zs, z)) - 1; t = (z - zs[i]) / (zs[i + 1] - zs[i]); return line[i] + (line[i + 1] - line[i]) * t
def polyline_pts(pts, n):   # n+1 points evenly by arc length along a polyline
    pts = np.array(pts, float); seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); L = np.concatenate([[0], np.cumsum(seg)])
    out = []
    for k in range(n + 1):
        s = L[-1] * k / n; i = min(len(seg) - 1, int(np.searchsorted(L, s, side="right")) - 1); t = (s - L[i]) / (seg[i] or 1)
        out.append(pts[i] + (pts[i + 1] - pts[i]) * t)
    return out

Hmf = body_fl(Hm_b)
# the leading edge aloft, bone by bone: [(bone, point)]; the humerus's chords end on the leg (hip -> knee -> ankle)
lead = [("body", Sf)]
lead += [("wArmL", lerp(Sf, Ef, k / 3)) for k in (1, 2, 3)]
lead += [("wForeL", lerp(Ef, Wf, t)) for t in (0.2, 0.47, 0.74)]
lead += [("wMcL", lerp(Wf, Kf, t)) for t in (0.0, 0.26, 0.52, 0.77)]
lead += [("wFingL", lerp(fing[0], fing[1], t)) for t in (0.0, 0.25, 0.5, 0.75)]
f2 = polyline_pts(fing[1:], 8)
lead += [("wFing2L", p) for p in f2[:-1]] + [("wFing2L", Tipf)]
leg_path = [Hf, Knf, Af]
def leg_pt(s):   # a point along the leg aloft (s: of its length, hip to ankle) and its bone
    l = s * (LFE + LTI)
    if l <= LFE: return "thighL", lerp(Hf, Knf, l / LFE)
    return "shinL", lerp(Knf, Af, (l - LFE) / LTI)
# the trailing edge aloft: from the ankle out to the tip -- gently concave, the chord narrowing steadily outward
lez = np.array([p for _, p in lead])
def le_y(z): return float(at_z(lez, z)[1])
TEc = [Af] + [V(x, le_y(z) - 0.012, z) for x, z in ((-0.42, 0.58), (-0.335, 0.80), (-0.285, 1.10), (-0.245, 1.47), (-0.24, 1.85), (-0.25, 2.15), (-0.27, 2.50), (-0.295, 2.78))] + [Tipf]
trail = cr(TEc, 14)

NJ = 8
mem_pts, mem_skin, mem_tone, mem_tris, mem_fl, mem_nrmf, mem_M = [], [], [], [], [], [], []
bones_list = []
def bidx(b):
    if b not in bones_list: bones_list.append(b)
    return bones_list.index(b)
def solve_rest(skins, pf):
    """skins: [(bone, weight)]; the rest point that the blend of their skinning maps onto pf aloft, and the blend's linear part"""
    M = np.zeros((3, 3)); t = np.zeros(3)
    for b, w in skins: Mb, tb = R.skin_map(b); M += w * Mb; t += w * tb
    return np.linalg.solve(M, pf - t), M
furl_info = []
LEGW = 0.06
def Rax(ax, a):   # rotation about a unit axis by a degrees
    ax = unit(ax); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]]); a *= D
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K
AXES = [unit(V(math.cos(2.39996 * k) * math.sqrt(1 - (1 - (2 * k + 1) / 80) ** 2), 1 - (2 * k + 1) / 80, math.sin(2.39996 * k) * math.sqrt(1 - (1 - (2 * k + 1) / 80) ** 2))) for k in range(80)]
def add_chord_row(i, bone, L, T, kind, NJ, cam, Wf_, prefix, tone_fn):
    """one chord of the grid: its points' rest positions, skins, flight positions; returns their indices"""
    if kind == "leg":   # (its trailing end on the leg aloft; at rest, swung up on a bone X of its own to lie beside the arm)
        lb, T = T
        B = R.P[lb]; MA, tA = R.skin_map(bone)
        Tl = R.fl_local(lb, T); Lr = R.to_rest(bone, L)
        tgt = Lr + LEGW * unit(body_rest(Hm_b) - Lr)
        best = None
        for ax in AXES:   # (X's turn rest -> flight: the arm's own, give or take up to 60 degrees -- whichever lays the chord shortest)
            for an in (0, 20, 40, 60):
                if an == 0 and best is not None: continue
                RXr = Rax(ax, an) @ MA.T @ B["Rf"]; Qx = B["Rr"].T @ RXr
                Gl = np.linalg.lstsq(np.eye(3) - Qx, B["Rr"].T @ (tgt - B["Or"]) - Qx @ Tl, rcond=None)[0]
                OXr = B["Or"] + B["Rr"] @ Gl; OXf = B["Of"] + B["Rf"] @ Gl
                MX = B["Rf"] @ RXr.T; tX = OXf - MX @ OXr
                reach = 0
                for u in np.linspace(0, 1, 9):
                    pf = L + (T - L) * u
                    q = np.linalg.solve((1 - u) * MA + u * MX, pf - (1 - u) * tA - u * tX); reach = max(reach, float(np.linalg.norm(q - Lr)))
                if best is None or reach < best[0]: best = (reach, RXr, Gl)
        xb = f"{prefix}{i}xL"
        R.add(xb, lb, best[2], best[1], B["Rf"])
        lb = xb
    ch = T - L; ln = float(np.linalg.norm(ch)); row = []
    nrm = UP if bone == "body" or kind == "leg" else R.P[bone]["Rf"][:, 2]
    if kind == "free" and ln > 1e-6:
        A = R.P[bone]
        n_f = nrm
        G = (L + T) / 2 + n_f * ln * 1.0
        Ll, Tl, Gl = R.fl_local(bone, L), R.fl_local(bone, T), R.fl_local(bone, G)
        Q = rot_between(Ll - Gl, Tl - Gl)
        tb = f"{prefix}{i}L"
        R.add(tb, bone, Gl, A["Rr"] @ Q.T, A["Rf"])
        furl_info.append((tb, ln))
    for j in range(NJ + 1):
        u = j / NJ
        pf = L + ch * u + nrm * cam * ln * math.sin(math.pi * u) * (0 if bone == "body" else 1)
        if kind == "free" and ln > 1e-6:
            w = round(max(0.0, u * (1 - Wf_ / ln)), 4) if ln > 1.5 * Wf_ else 0.0
            pl = R.fl_local(bone, pf); Mw = (1 - w) * np.eye(3) + w * Q
            ql = Gl + np.linalg.solve(Mw, pl - Gl); pr = A["Or"] + A["Rr"] @ ql
            Mlin = A["Rf"] @ Mw @ A["Rr"].T
            sk = [bidx(bone), bidx(tb), round(w, 4)] if w > 0 else bidx(bone)
            if w > 0: bidx(tb)
        elif kind == "leg":
            u = round(u, 4); pr, Mlin = solve_rest([(bone, 1 - u), (lb, u)], pf)
            sk = [bidx(bone), bidx(lb), round(u, 4)] if 0 < u < 1 else bidx(bone if u == 0 else lb)
        else:   # rigid on the bone (the root on the body, the tip, the pteroid's own chord)
            pr = R.to_rest(bone, pf) if bone != "body" else body_rest(pf - OB); Mlin = R.skin_map(bone)[0] if bone != "body" else Rb_r.T
            sk = bidx(bone)
        mem_pts.append(pr); mem_fl.append(pf); mem_skin.append(sk); mem_M.append(Mlin); mem_tone.append(tone_fn(i, j, u, L))
        row.append(len(mem_pts) - 1)
    return row
def grid_tris(grid):
    for i in range(len(grid) - 1):
        for j in range(len(grid[i]) - 1):
            a, b, c, d = grid[i][j], grid[i][j + 1], grid[i + 1][j], grid[i + 1][j + 1]
            mem_tris.extend([a, c, b, b, c, d])

# the BRACHIOPATAGIUM: darker toward the trailing edge and the tip, the fibres' lines running along the span
TIPZ = float(Tipf[2])
def main_tone(i, j, u, L):
    s = max(0.0, (float(L[2]) - Sf[2]) / (TIPZ - Sf[2]))
    t = (1 - 0.30 * u ** 1.4) * (1 - 0.24 * s ** 2) * (1.06 - 0.06 * u)
    if 0 < j < NJ and j % 2: t *= 0.9   # (every other line of the grid: the actinofibrils' grain)
    return t
# each free chord furls to about half the way to the folded bone beside it (the forearm's and the finger's skins meeting
# between them, the metacarpal's and the first phalanx's), alternate chords a quarter short of that: the skin pleated
Tipr = R.to_rest("wFing2L", Tipf)
PARTNER = {"wForeL": (Jr, Tipr), "wFing2L": (Er, Wr), "wMcL": (Kr, Jr), "wFingL": (Wr, Kr)}
def ptseg(p, a, b): t = max(0.0, min(1.0, float((p - a) @ (b - a) / ((b - a) @ (b - a))))); return float(np.linalg.norm(p - (a + (b - a) * t)))
WRISTW = float(os.environ.get("PT_WRISTW", .09))
PROW = float(os.environ.get("PT_PROW", .012))   # (the propatagium furls tight inside the forearm at rest: at .025 its edge lay on the skin, a dark line)
def wfurl(i, bone, L):
    # (the chord AT the wrist: the fat joint swallowed its furled end and left a 10 mm fin of skin -- a dark crack at the
    #  wrist at rest; furled further out it folds beside the joint like its neighbours either side)
    if bone == "wMcL" and np.linalg.norm(L - Wf) < 1e-6: return WRISTW
    a, b = PARTNER[bone]; g = ptseg(R.to_rest(bone, L), a, b)
    return max(0.036, min(0.05, 0.5 * g)) * (1 if i % 2 else 0.75)
g_main = []
nlead = len(lead)
for i, (bone, L) in enumerate(lead):
    if i == 0: g_main.append(add_chord_row(i, "body", L, Hmf, "rigid", NJ, 0, 0, "wT", main_tone)); continue
    if bone == "wArmL":
        k = i   # 1..3 -> a third of the leg each
        lb, T = leg_pt(k / 3)
        g_main.append(add_chord_row(i, bone, L, (lb, T), "leg", NJ, 0.02, 0, "wT", main_tone)); continue
    if i == nlead - 1: g_main.append(add_chord_row(i, bone, L, Tipf, "rigid", NJ, 0, 0, "wT", main_tone)); continue
    T = at_z(trail, L[2])
    g_main.append(add_chord_row(i, bone, L, T, "free", NJ, 0.035, wfurl(i, bone, L), "wT", main_tone))
grid_tris(g_main)

# the PROPATAGIUM: ahead of the humerus and forearm, from the neck's side to the pteroid's tip
N0f = body_fl(N0_b)
front = cr([N0f, body_fl(V(0.215, 0.02, 0.30)), body_fl(V(0.255, 0.035, 0.52)), Ptip_f], 12)
pro_back = [("body", Sf), ("wArmL", lerp(Sf, Ef, 0.5)), ("wForeL", Ef), ("wForeL", lerp(Ef, Wf, 1 / 3)), ("wForeL", lerp(Ef, Wf, 2 / 3)), ("wPterL", Wf)]
NJP = 3
g_pro = []
for i, (bone, L) in enumerate(pro_back):
    tone = lambda i_, j, u, L_: 1.0 - 0.1 * u
    if i == 0: g_pro.append(add_chord_row(i, "body", L, N0f, "rigid", NJP, 0, 0, "wP", tone)); continue
    if i == len(pro_back) - 1: g_pro.append(add_chord_row(i, bone, L, Ptip_f, "rigid", NJP, 0, 0, "wP", tone)); continue
    g_pro.append(add_chord_row(i, bone, L, at_z(front, L[2]), "free", NJP, 0.02, PROW, "wP", tone))
grid_tris(g_pro)

# the skin's normals: worked out spread (aloft), carried back to the rest pose through each point's own skinning
FL = np.array(mem_fl); NV = np.zeros_like(FL)
for f in range(0, len(mem_tris), 3):
    a_, b_, c_ = mem_tris[f:f + 3]; fn = np.cross(FL[b_] - FL[a_], FL[c_] - FL[a_])
    for v in (a_, b_, c_): NV[v] += fn
mem_nrm = [unit(np.linalg.solve(mem_M[v], unit(NV[v]))) for v in range(len(FL))]

# ---------------------------------------------------------------- mirror the wing and the leg to the right
def mirror_id(id): return id[:-1] + "R" if id.endswith("L") else id
for id in list(R.order):
    if not id.endswith("L"): continue
    p = R.P[id]; Mz = np.diag([1, 1, -1])
    par = mirror_id(p["parent"]) if p["parent"] else None
    kw = dict(p["kw"])
    if "anim" in kw: kw["anim"] = {**kw["anim"], "deg": -kw["anim"]["deg"], "side": -1}
    if "flyUp" in kw: kw["flyUp"] = [-kw["flyUp"][0], -kw["flyUp"][1], kw["flyUp"][2]]
    pos = p["pos"].copy(); pos[2] = -pos[2]
    R.add(mirror_id(id), par, pos, Mz @ p["Rr"] @ Mz, Mz @ p["Rf"] @ Mz, **kw)

# ---------------------------------------------------------------- the sculpt
def br(p): return [float(v) for v in body_rest(p)]
def bones_rest(id, loc): return [float(v) for v in R.rest_pt(id, loc)]
Rh = R.P["head"]["Rr"]
def hd(x, y, z=0.0): return bones_rest("head", V(x, y, z))
def L_(v): return [float(x) for x in v]
SH = []
add = SH.append
FUR = {"pat": "agouti"}
# the trunk: a compact deep chest, broad over the flight muscles and the shoulders, narrowing back to slim hips; a stub of a tail
add({"id": "torso", "type": "ell", "c": br([-0.01, 0.0, 0]), "r": [0.165, 0.10, 0.095], "rot": [0, 0, TH], "k": 0.03, "color": "@body", **FUR})
add({"id": "chest", "type": "ell", "c": br([0.07, -0.035, 0]), "r": [0.12, 0.10, 0.10], "rot": [0, 0, TH], "k": 0.03, "color": "@belly", **FUR})
add({"id": "keel", "type": "ell", "c": br([0.075, -0.10, 0]), "r": [0.095, 0.05, 0.042], "rot": [0, 0, TH], "k": 0.03, "color": "@belly", **FUR})
add({"id": "pectoral", "type": "ell", "c": br([0.065, -0.035, 0.06]), "r": [0.105, 0.078, 0.06], "rot": [0, 0, TH - 8], "k": 0.03, "color": "@body", "mirror": True, **FUR})
add({"id": "notarium", "type": "ell", "c": br([0.10, 0.065, 0]), "r": [0.07, 0.04, 0.055], "rot": [0, 0, TH], "k": 0.025, "color": "@back", **FUR})
add({"id": "shoulder", "type": "ell", "c": br([0.10, 0.015, 0.07]), "r": [0.062, 0.058, 0.05], "rot": [0, 0, TH], "k": 0.025, "color": "@body", "mirror": True, **FUR})
add({"id": "pelvis", "type": "ell", "c": br([-0.15, 0.0, 0]), "r": [0.10, 0.058, 0.055], "rot": [0, 0, TH], "k": 0.03, "color": "@body", **FUR})
add({"id": "hip", "type": "ell", "c": br([-0.205, -0.005, 0.044]), "r": [0.048, 0.043, 0.033], "rot": [0, 0, TH], "k": 0.02, "color": "@body", "mirror": True, **FUR})
add({"id": "tail", "type": "cone", "a": br([-0.24, 0.0, 0]), "b": br([-0.32, -0.005, 0]), "ra": 0.022, "rb": 0.007, "k": 0.02, "color": "@back", **FUR})
add({"id": "neckRoot", "type": "cone", "a": br([0.09, 0.03, 0]), "b": L_(Nr), "ra": 0.08, "rb": 0.076, "k": 0.03, "color": "@neck", **FUR})
# the neck: stout, a gentle S -- thick at its root and only a little narrower under the skull
NA, NB, NC, NH = (R.P[b]["Or"] for b in ("nkA", "nkB", "nkC", "head"))
add({"id": "neck1", "type": "cone", "bone": "nkA", "a": L_(NA), "b": L_(NB), "ra": 0.076, "rb": 0.067, "k": 0.03, "color": "@neck", **FUR})
add({"id": "neck2", "type": "cone", "bone": "nkB", "a": L_(NB), "b": L_(NC), "ra": 0.067, "rb": 0.06, "k": 0.03, "color": "@neck", **FUR})
add({"id": "neck3", "type": "cone", "bone": "nkC", "a": L_(NC), "b": L_(NH), "ra": 0.06, "rb": 0.053, "k": 0.03, "color": "@neck", **FUR})

# THE HEAD (its own frame: x along the jaw line from the neck's end, y up, z left): ONE laterally flattened wedge, beak,
# skull and crest in a piece. Two long boxes (the skull's paint and the beak's, blended) cut down by planes -- the
# culmen above, the jaw's keel below, and each side two flat cheeks meeting at the mouth's line (the upper narrowing to
# the culmen, the lower to the keel), every one leaning in toward the tip -- so the beak's base is the skull's depth at
# the eye and it all tapers to a needle; the crest a flat blade rising from the back of the skull, in line with the culmen.
X0, YC0, SCm = 0.04, -0.032, -0.015 / 0.915              # the mouth's line (the commissure): y = yc(x)
W0, SW = 0.044, (0.0078 - 0.044) / 0.94                   # the half-width at the mouth's line: w(x), from x = 0.02
TU, TL = 0.18, 0.24                                       # the cheeks' lean in above and below it (width lost a metre of height)
YT0, ST = 0.080, (-0.040 - 0.080) / 0.868                 # the culmen: y = 0.080 at x = 0.10, -0.040 at the tip
YV0, SV = -0.088, (-0.054 + 0.088) / 0.932                # the jaw's keel: y = -0.088 at x = 0.03, -0.054 at the tip
yc = lambda x: YC0 + SCm * (x - X0)
wd = lambda x: W0 + SW * (x - 0.02)
yt = lambda x: YT0 + ST * (x - 0.10)
yv = lambda x: YV0 + SV * (x - 0.03)
def plane_sub(id, P0, n, segs, ylo, yhi, k=0.006, Dp=0.05, rd=0.035):
    """a half-space carved off the head: the plane through P0 (head frame) with outward normal n, over the head's x from
    x0 to x1 for each (x0, x1, paint) of segs (the face's paint grading into the beak's, the tip's: boxes overlapping, their
    ends rounded off), and ylo..yhi across it; Dp deep. (Every carving paints what it opens: a bare one would be grey.)"""
    n = unit(n); ex = unit(V(1, 0, 0) - n[0] * n); ey = np.cross(n, ex)
    if ey[1] < 0: ex, ey = -ex, -ey                        # ylo..yhi runs up on both sides (a right-handed frame still)
    M = Rh @ np.column_stack([ex, ey, n]); rot = [float(v) for v in m2e(M)]
    for m, (x0, x1, col) in enumerate(segs):
        a0, a1 = (x0 - P0[0]) / ex[0], (x1 - P0[0]) / ex[0]
        Cc = P0 + ex * (a0 + a1) / 2 + ey * (ylo + yhi) / 2 + n * Dp
        add({"id": f"{id}{m}", "type": "box", "bone": "head", "op": "sub", "c": bones_rest("head", Cc), "r": [abs(float(a1 - a0)) / 2, float(yhi - ylo) / 2, Dp],
             "rot": rot, "round": rd, "k": k, "kc": k, "color": col})
FACE, BEAK, TIP = (-0.08, 0.27, "@face"), (0.17, 0.90, "@beak"), (0.80, 1.03, "@beakTip")
JAW = (0.0, 0.90, "@jaw")
add({"id": "skull", "type": "box", "bone": "head", "c": hd(0.12, -0.004), "r": [0.18, 0.088, 0.047], "rot": [0, 0, HEADr], "round": 0.03, "k": 0.045, "color": "@face"})
add({"id": "rostrum", "type": "box", "bone": "head", "c": hd(0.575, -0.004), "r": [0.395, 0.088, 0.047], "rot": [0, 0, HEADr], "round": 0.004, "k": 0.045, "kc": 0.045, "color": "@beak"})
# the crest: a flat blade, deep at its root behind the eyes, its upper edge the culmen's line carried on to a point
add({"id": "crestCore", "type": "tri", "bone": "head", "a": hd(0.07, 0.068), "b": hd(-0.30, 0.12), "c": hd(-0.035, 0.022), "r": 0.0125, "k": 0.03, "kc": 0.02, "color": "@crestBase"})
add({"id": "crest", "type": "tri", "bone": "head", "a": hd(0.11, 0.071), "b": hd(-0.74, 0.192), "c": hd(-0.05, 0.03), "r": 0.0072, "k": 0.02, "kc": 0.012, "color": "@crest"})
for s in (1, -1):
    S_ = "L" if s > 0 else "R"
    # the upper cheek: z = w(x) - TU (y - yc(x))
    nu = V(-SW - TU * SCm, TU, s * 1.0); P0 = V(0.5, yc(0.5), s * wd(0.5))
    plane_sub("cheek" + S_, P0, nu, [FACE, BEAK, TIP], -0.09, 0.13)
    # the lower jaw's side: z = w(x) - TL (yc(x) - y), its own paint
    nl = V(-SW + TL * SCm, -TL, s * 1.0)
    plane_sub("jawSide" + S_, P0, nl, [JAW, TIP], -0.12, 0.045, k=0.005)
    # the mouth's line: a fine dark groove from the tip back to below the eye (on the surface: it hardly cuts, it paints)
    a, b = V(0.958, yc(0.958), s * (wd(0.958) + 0.0008)), V(0.05, yc(0.05), s * (wd(0.05) + 0.0018))
    add({"id": "mouth" + S_, "type": "cone", "bone": "head", "op": "sub", "a": hd(*a), "b": hd(*b), "ra": 0.0022, "rb": 0.0045, "k": 0.006, "kc": 0.006, "color": "@mouth"})
plane_sub("culmen", V(0.56, yt(0.56), 0), V(-ST, 1, 0), [(0.105, 0.27, "@face"), BEAK, TIP], -0.07, 0.07, k=0.007, Dp=0.09)
plane_sub("keel", V(0.5, yv(0.5), 0), V(SV, -1, 0), [(0.03, 0.90, "@jaw"), TIP], -0.07, 0.07, k=0.007)

# the legs: a muscled thigh, a slender shin, a long plantigrade foot of four clawed toes
def leg_shapes():
    H, K_, A = R.P["thighL"]["Or"], R.P["shinL"]["Or"], R.P["footL"]["Or"]
    return [{"id": "thigh", "type": "cone", "bone": "thighL", "a": L_(H), "b": L_(K_), "ra": 0.038, "rb": 0.02, "k": 0.03, "color": "@body", **FUR},
            {"id": "shin", "type": "cone", "bone": "shinL", "a": L_(K_), "b": L_(A), "ra": 0.02, "rb": 0.0125, "k": 0.012, "color": "@leg"},
            {"id": "meta", "type": "cone", "bone": "footL", "a": L_(A), "b": L_(R.rest_pt("footL", V(0, LMT, 0))), "ra": 0.0125, "rb": 0.0095, "k": 0.008, "color": "@foot"}]
SH += [dict(q, mirror=True) for q in leg_shapes()]
for i, (a, L) in enumerate(((-14, 0.055), (-4, 0.062), (6, 0.06), (16, 0.05))):
    d = R.P["footL"]["Rr"] @ unit(V(0, 1, math.sin(a * D)))
    b0 = R.rest_pt("footL", V(0, LMT, 0)); tip = b0 + d * L
    add({"id": f"toe{i}", "type": "cone", "bone": "footL", "a": L_(b0), "b": L_(tip), "ra": 0.0062, "rb": 0.004, "k": 0.004, "color": "@foot", "mirror": True})
    add({"id": f"toeClaw{i}", "type": "cone", "bone": "footL", "a": L_(tip), "b": L_(tip + d * 0.018 + V(0, -0.006, 0)), "ra": 0.0042, "rb": 0.0008, "k": 0.002, "color": "@claw", "mirror": True})
# the arm: the humerus's deltopectoral crest, the forearm, the long metacarpal, the knuckle, the wing finger to its tip
# (limbs, not boards: a short stout humerus muscled into the shoulder, a round forearm tapering to the wrist, a long slim
# round metacarpal with a knob of a joint at each end -- skin-coloured, a warm grey-brown a shade lighter than the wing's skin)
add({"id": "humerus", "type": "cone", "bone": "wArmL", "a": L_(Sr), "b": L_(Er), "ra": 0.046, "rb": 0.027, "k": 0.03, "color": "@arm", "mirror": True, **FUR})
add({"id": "delto", "type": "ell", "bone": "wArmL", "c": bones_rest("wArmL", V(-0.01, 0.09, 0.0)), "r": [0.042, 0.085, 0.036], "rot": [float(v) for v in m2e(R.P["wArmL"]["Rr"])], "k": 0.025, "color": "@arm", "mirror": True, **FUR})
add({"id": "elbow", "type": "sphere", "bone": "wForeL", "c": L_(Er), "r": 0.03, "k": 0.015, "color": "@limb", "mirror": True})
add({"id": "forearm", "type": "cone", "bone": "wForeL", "a": L_(Er), "b": L_(Wr), "ra": 0.03, "rb": 0.018, "k": 0.012, "color": "@limb", "mirror": True})
add({"id": "foreMuscle", "type": "ell", "bone": "wForeL", "c": bones_rest("wForeL", V(0, 0.13, 0)), "r": [0.028, 0.13, 0.03], "rot": [float(v) for v in m2e(R.P["wForeL"]["Rr"])], "k": 0.015, "color": "@limb", "mirror": True})
add({"id": "wrist", "type": "sphere", "bone": "wMcL", "c": L_(Wr), "r": 0.025, "k": 0.012, "color": "@limb", "mirror": True})
add({"id": "metacarpal", "type": "cone", "bone": "wMcL", "a": L_(Wr), "b": L_(Kr), "ra": 0.0155, "rb": 0.013, "k": 0.01, "color": "@limb", "mirror": True})
add({"id": "knuckle", "type": "sphere", "bone": "wMcL", "c": L_(Kr), "r": 0.023, "k": 0.01, "color": "@limb", "mirror": True})
F1 = [R.to_rest("wFingL", p) for p in fing[:2]]
F2 = [R.to_rest("wFing2L", p) for p in fing[1:]]
add({"id": "finger", "type": "cone", "bone": "wFingL", "a": L_(F1[0]), "b": L_(F1[1]), "ra": 0.015, "rb": 0.0125, "k": 0.04, "kc": 0.006, "color": "@limb", "mirror": True})
add({"id": "finger2", "type": "tube", "bone": "wFing2L", "pts": [L_(F2[0]) + [0.012], L_(F2[1]) + [0.0095], L_(F2[2]) + [0.0072]], "k": 0.006, "color": "@limb", "mirror": True})
add({"id": "fingerTip", "type": "tube", "bone": "wFing2L", "pts": [L_(F2[2]) + [0.006], L_((F2[2] + F2[3]) / 2) + [0.0042], L_(F2[3]) + [0.0018]], "k": 0.003, "color": "@limb", "mirror": True})
# the pteroid, the propatagium's spar
add({"id": "pteroid", "type": "cone", "bone": "wPterL", "a": L_(Wr), "b": L_(R.to_rest("wPterL", Ptip_f)), "ra": 0.0075, "rb": 0.003, "k": 0.004, "color": "@limb", "mirror": True})
# the three free fingers and their claws
for nm, L in DIG:
    b0 = R.P[nm]["Or"]; d = R.P[nm]["Rr"][:, 1]; tip = b0 + d * L
    add({"id": nm[:-1], "type": "cone", "bone": nm, "a": L_(b0 + d * 0.01), "b": L_(tip), "ra": 0.0075, "rb": 0.005, "k": 0.004, "color": "@limb", "mirror": True})
    add({"id": nm[:-1] + "Claw", "type": "cone", "bone": nm, "a": L_(tip), "b": L_(tip + d * 0.022 + V(0, -0.012, 0)), "ra": 0.0048, "rb": 0.0008, "k": 0.002, "color": "@claw", "mirror": True})
# the skin of the wings: one membrane each side (lighter from below: the light through it)
tris = [int(v) for v in mem_tris]
SH.append({"id": "wings", "type": "membrane", "mirror": True, "color": "@mem", "r": 0.0016, "under": 1.3, "bones": bones_list,
           "pts": [[round(float(v), 4) for v in p] for p in mem_pts], "skin": mem_skin, "nrm": [[round(float(x), 3) for x in n] for n in mem_nrm],
           "tone": [round(t, 3) for t in mem_tone], "tris": tris})

eyes = {"at": hd(0.078, 0.03, 0.045), "from": hd(0.078, 0.03, 0.0), "r": 0.0105, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.5, "socket": 1.4, "color": "#0e0906"}

parts = R.parts()
out = {
    "name": "pteranodon",
    "_about": "PTERANODON LONGICEPS (2026-11-06, gen: scratchpad sc/ptero/gen.py): a male, 5.95 m across the wings, a turkey's body under them -- "
              "a compact deep furred trunk (pycnofibres: pale grey-cream, darker over the back) broad over the flight muscles, a short stout neck "
              "held in a gentle S, and a head longer than the trunk: one laterally flattened wedge, the long straight toothless beak running back "
              "into the skull and on into the flat crest, as long again. STANDING (the rest pose) on all fours on the folded wings: the metacarpal "
              "the front leg, the three free clawed fingers on the ground ahead, the wing finger folded back tight up the metacarpal and along the "
              "forearm, its skin furled beside the bones; IN FLIGHT (flyRot) long narrow wings, the trailing edge from the pointed tip in to the "
              "ankles, the legs spread behind; on the upstroke the hand flexes back at the wrist (flyUp). Its skin is one membrane each side "
              "(bodymesh.js membraneMesh), every free chord furled on a bone of its own",
    "kind": "parts",
    "flags": {"flight": {"arm": 0, "hand": 0, "beat": 11, "handK": 1, "bob": 0.025, "ease": 1.0}, "soar": {"alt": [14, 40], "speed": [7, 11]}},
    "c": C,
    "parts": parts,
    "sculpt": {"keep": [], "mesh": {"cell": 0.0085, "tris": [12000, 3400], "focus": {"head": 4}},
               "shade": {"back": 0.86, "belly": 1.07, "on": "@body"},
               "shape": SH, "eyes": eyes},
}
open(OUT, "w").write(dumps(out))
json.dump([[float(v) for v in p] for p in mem_fl], open(SP + "sc/ptero/mem_fl.json", "w"))
def segd(a, b, c, d):   # the least distance between segments ab and cd (sampled)
    return min(np.linalg.norm(lerp(a, b, s) - lerp(c, d, t)) for s in np.linspace(0, 1, 21) for t in np.linspace(0, 1, 21))
CAPS = [("humerus", Sr, Er, 0.036), ("forearm", Er, Wr, 0.022), ("mc", Wr, Kr, 0.017), ("ph1", F1[0], F1[1], 0.016), ("ph2", F2[0], F2[3], 0.012)]
for i in range(len(CAPS)):
    for j in range(i + 1, len(CAPS)):
        g = segd(CAPS[i][1], CAPS[i][2], CAPS[j][1], CAPS[j][2]) - CAPS[i][3] - CAPS[j][3]
        print("clearance", CAPS[i][0], CAPS[j][0], round(float(g), 3))
P = np.array(mem_pts)
print("parts", len(parts), "membrane pts", len(mem_pts), "tris", len(tris) // 3, "skin bones", len(bones_list), "flyUp mc", R.P["wMcL"]["kw"]["flyUp"], "f2", R.P["wFing2L"]["kw"]["flyUp"])
print("rest: K", np.round(Kr, 3), "W", np.round(Wr, 3), "E", np.round(Er, 3), "S", np.round(Sr, 3), "J", np.round(Jr, 3), "tip", np.round(R.to_rest('wFing2L', Tipf), 3))
print("flight: tip", np.round(Tipf - OB, 3), "K", np.round(Kf - OB, 3), "W", np.round(Wf - OB, 3), "ankle", np.round(Af - OB, 3))
print("head rest", np.round(R.P['head']['Or'], 3), "beak tip", np.round(hd(0.97, -0.047), 3), "crest tip", np.round(hd(-0.74, 0.192), 3))
print("rest membrane bounds", np.round(P.min(0), 3), np.round(P.max(0), 3))
if "--dbg" in sys.argv:
    for i, row in enumerate(g_main):
        r0, r1 = np.array(mem_pts[row[0]]), np.array(mem_pts[row[-1]])
        wmax = max(np.linalg.norm(np.array(mem_pts[v]) - r0) for v in row)
        print("main", i, lead[i][0], "L", np.round(r0, 3), "T", np.round(r1, 3), "reach", round(float(wmax), 3), "ln", round(float(np.linalg.norm(np.array(mem_fl[row[-1]]) - mem_fl[row[0]])), 3))
    for i, row in enumerate(g_pro):
        r0 = np.array(mem_pts[row[0]]); print("pro", i, np.round(r0, 3), "reach", round(float(max(np.linalg.norm(np.array(mem_pts[v]) - r0) for v in row)), 3))
