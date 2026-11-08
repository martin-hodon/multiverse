from cetlib import *
import os

# NARWHAL (Monodon monoceros), an adult MALE, 4.5 m from the front of the melon to the fluke notch (the tusk not
# counted): the melon's front at x = +1.9, the notch at -2.6. Rest frame: x forward, y up, z LEFT, metres; the body's
# axis about y = 0. Writes assets/creatures/sea/narwhal.json and narwhal_wgsl.json (wgsl_narwhal.py: its coat).
#
# What is gridded and what is not (2026-11-07, the lessons of the shark and the smilodon): the trunk, the head and the
# low dorsal RIDGE are in the sculpt grid (all of them thick, so nothing samples into steps); the FLIPPERS, the FLUKES
# and the TUSK are explicit closed meshes (`membrane` details: drawn as they are, never gridded or decimated) -- the
# blades lofted from airfoil sections, thin at their edges and thick at their roots, the tusk a helically fluted lathe
# tapering to a true point. Only smooth fillets at the blades' roots and a collar of lip round the tusk are in the grid.
# Build: python3 narwhal.py && node narwhal_stock.mjs && python3 narwhal.py (the second pass lays the flukes' root over
# the stock's sculpted surface, which the first wrote), then wgsl_narwhal.py and install_pat.py (see its last lines).
L, XS = 4.5, 1.9
X = lambda s: XS - s * L          # (s: the share of the length back from the front of the melon)
HZ = 0.75                         # (a cruising tail beat)

# THE RIG: body (root) -> head; the flippers; four tail bones PITCHING (the flukes beat up and down, each a beat behind)
XT = [X(0.54), X(0.70), X(0.85), X(0.935)]
R = Rig()
R.add("body", None, [0, 0, 0], shape=tube_part([1.2, 0, 0], [-0.6, 0, 0], 0.48, 0.42), color="@skin",
      anim={"axis": "z", "deg": 0.8, "speed": HZ, "phase": 2.6})
R.add("head", "body", [1.3, 0, 0], shape={"shape": "sphere", "size": {"r": 0.3}}, color="@skin",
      anim={"axis": "y", "deg": 1.2, "speed": HZ * 0.5, "phase": 1.0})
PECT = [X(0.205), -0.27, 0.36]
for side, s in (("L", 1), ("R", -1)):
    R.add(f"pect{side}", "body", [PECT[0], PECT[1], s * PECT[2]], shape={"shape": "sphere", "size": {"r": 0.06}}, color="@skin",
          anim={"axis": "x", "deg": s * 5, "speed": HZ * 0.5, "phase": 0.4})
degs, ph = [3.0, 6.5, 9.5, 15.0], [0.0, -0.55, -1.1, -1.75]
par, x0 = "body", 0.0
for j, x in enumerate(XT):
    nm = f"tail{j + 1}" if j < 3 else "fluke"
    R.add(nm, par, [x - x0, 0.0, 0], shape={"shape": "sphere", "size": {"r": 0.22 - 0.05 * j}}, color="@skin",
          anim={"axis": "z", "deg": degs[j], "speed": HZ, "phase": ph[j]})
    par, x0 = nm, x
def bone_x(x):
    if x > 1.3: return "head"
    if x > XT[0]: return "body"
    if x > XT[1]: return "tail1"
    if x > XT[2]: return "tail2"
    if x > XT[3]: return "tail3"
    return "fluke"

# THE BODY (x, top, bottom, half width): STOUT and cigar-shaped, deepest ~0.38 back; the small rounded head with the
# hint of a neck behind it; the stock laterally flattened (the keels) and narrowing hard to the flukes
ST = [(X(0.0), -0.02, -0.1, 0.05), (X(0.012), 0.07, -0.17, 0.13), (X(0.03), 0.15, -0.23, 0.2), (X(0.055), 0.22, -0.28, 0.255),
      (X(0.085), 0.27, -0.315, 0.29), (X(0.12), 0.3, -0.34, 0.31), (X(0.155), 0.325, -0.37, 0.33), (X(0.2), 0.37, -0.42, 0.375),
      (X(0.26), 0.43, -0.47, 0.43), (X(0.32), 0.475, -0.5, 0.47), (X(0.39), 0.495, -0.505, 0.48), (X(0.46), 0.485, -0.48, 0.46),
      (X(0.54), 0.44, -0.42, 0.405), (X(0.62), 0.37, -0.34, 0.33), (X(0.70), 0.29, -0.255, 0.24), (X(0.78), 0.21, -0.17, 0.15),
      (X(0.85), 0.145, -0.105, 0.095), (X(0.9), 0.105, -0.07, 0.07), (X(0.925), 0.07, -0.047, 0.052), (X(0.945), 0.04, -0.022, 0.034)]
PAT = 68   # (coatpat.js 68 `narwhal`, laid in the rest pose's own space: a frame that IS that space, so no seam between shapes)
FRAME = {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 1}
RF = lambda t, b, w: w + 0.4 * ((t - b) / 2 - w)
sh = trunk_tubes(ST, [ST[0][0] + 0.02, 1.3, XT[0], XT[1], XT[2], XT[3], ST[-1][0]], ["head", "body", "tail1", "tail2", "tail3", "fluke"], "@skin",
                 step=0.1, ov=0.08, k=0.08, rfun=RF)
def tube_r(x):   # (the trunk tube at x: its middle and radius)
    t, b, w = smooth(ST, x); return (t + b) / 2, RF(t, b, w)
back = lambda x: sum(tube_r(x))
belly = lambda x: tube_r(x)[0] - tube_r(x)[1]

# the stock's KEELS, above and below: broad (3+ cells), blended in -- they flatten the stock from the side (ending short
# of the flukes' joint: a rigid keel past it would stand proud of the flukes as they beat)
sh += [S("tube", id=f"keelD{i}", bone=bone_x(x), pts=[[x + 0.16, back(x + 0.16) - 0.05, 0, 0.05], [max(x - 0.16, XT[3] + 0.03), back(max(x - 0.16, XT[3] + 0.03)) - 0.04, 0, 0.04]],
         k=0.05, color="@skin") for i, x in enumerate([X(0.74), X(0.8), X(0.86), X(0.91)])]
sh += [S("tube", id=f"keelV{i}", bone=bone_x(x), pts=[[x + 0.16, belly(x + 0.16) + 0.045, 0, 0.045], [max(x - 0.16, XT[3] + 0.03), belly(max(x - 0.16, XT[3] + 0.03)) + 0.035, 0, 0.037]],
         k=0.05, color="@skin") for i, x in enumerate([X(0.78), X(0.84), X(0.9)])]

# THE DORSAL RIDGE: no fin -- a low ridge along the rear half of the back, ~4-5 cm high, of irregular BUMPS (nodules)
# on a low continuous crest; all of them 3+ cells thick, blended in
RX = [X(0.5) - 0.0, X(0.78)]
rpts = []
for i in range(8):
    t = i / 7; x = lerpf(RX[0], RX[1], t)
    rpts.append([x, back(x) - 0.03 + 0.012 * math.sin(math.pi * t), 0, 0.036 + 0.006 * math.sin(math.pi * t)])
sh += [S("tube", id="ridge", bone="tail1", pts=rpts, k=0.04, color="@skin")]
BUMPS = [(0.53, 0.012, 0.045), (0.565, 0.02, 0.05), (0.595, 0.014, 0.04), (0.625, 0.024, 0.055), (0.655, 0.018, 0.045), (0.685, 0.022, 0.05),
         (0.715, 0.014, 0.04), (0.745, 0.01, 0.035)]
for i, (s, up, rx) in enumerate(BUMPS):
    x = X(s)
    sh.append(S("ell", id=f"bump{i}", bone=bone_x(x), c=[x, back(x) + up - 0.012, 0.004 * (1 if i % 2 else -1)], r=[rx, 0.032, 0.032], k=0.03, color="@skin"))

# THE HEAD: small and rounded, the MELON bulging forward over a short mouth; the lower jaw small, set back under it
def surf_z(x, y, out=0.0):
    yc, r = tube_r(x)
    return math.sqrt(max(0.0, r * r - (y - yc) ** 2)) + out
sh += [
    S("ell", id="melon", bone="head", c=[X(0.05), 0.005, 0], r=[0.22, 0.23, 0.245], k=0.1, color="@skin"),
    S("ell", id="jaw", bone="head", c=[X(0.06), -0.2, 0], r=[0.19, 0.085, 0.17], k=0.07, color="@skin"),
    S("ell", id="cheek", bone="head", c=[X(0.105), -0.12, 0.0], r=[0.2, 0.2, 0.29], k=0.1, color="@skin"),
    S("ell", id="throat", c=[X(0.17), -0.3, 0], r=[0.32, 0.12, 0.27], k=0.12, color="@skin"),
]
# the MOUTH: a short line from the front of the lower jaw back to its corner (below and well ahead of the eye), turned up
# a little at the corner -- drawn by the coat (wgsl_narwhal.py: a dark line at this height along x; a groove or a
# paint tube finer than the mesh speckles)
LIP = [(X(0.0) + 0.01, -0.168), (X(0.018), -0.18), (X(0.038), -0.186), (X(0.055), -0.18), (X(0.068), -0.166)]
# the BLOWHOLE: a crescent on top of the head, its open side forward
BX = X(0.135)
sh += [S("ell", id="blow", bone="head", c=[BX, back(BX) + 0.004, 0], r=[0.014, 0.02, 0.05], k=0.01, color="@skin", op="sub"),
       S("ell", id="blowLip", bone="head", c=[BX + 0.024, back(BX) - 0.004, 0], r=[0.026, 0.02, 0.05], k=0.02, color="@skin")]

# ---- EXPLICIT MESHES -------------------------------------------------------------------------------------------------
def loft_closed(rings, tip_a=None, tip_b=None):
    """faces of a closed loft: rings (each the same number of points, in the same order round), and optional end points
    the first / last ring is fanned to; returns (pts, tris) with the faces wound outward"""
    n = len(rings[0]); pts = [p for r in rings for p in r]; tris = []
    for i in range(len(rings) - 1):
        for m in range(n):
            a, b = i * n + m, i * n + (m + 1) % n
            tris += [a, b, a + n, b, b + n, a + n]
    if tip_a is not None:
        ia = len(pts); pts.append(tip_a)
        for m in range(n): tris += [ia, (m + 1) % n, m]
    if tip_b is not None:
        ib = len(pts); pts.append(tip_b); o = (len(rings) - 1) * n
        for m in range(n): tris += [o + m, o + (m + 1) % n, ib]
    # (outward: the signed volume positive)
    vol = 0.0
    for f in range(0, len(tris), 3):
        A, B, C = pts[tris[f]], pts[tris[f + 1]], pts[tris[f + 2]]
        vol += dot(A, cross(B, C))
    if vol < 0:
        for f in range(0, len(tris), 3): tris[f + 1], tris[f + 2] = tris[f + 2], tris[f + 1]
    return pts, tris

def membrane(id, pts, tris, bone, color, tone=None, mirror=False, when=None):
    return S("membrane", id=id, bones=[bone], skin=[0] * len(pts), pts=[[round(v, 5) for v in p] for p in pts], tris=tris,
             tone=tone, r=0.0003, color=color, mirror=True if mirror else None, when=when)

def airfoil(c):   # (a section's thickness at chord share c from the leading edge: 1 at its thickest, ~0.3 back)
    return min(1.0, 1.95 * math.sqrt(max(c, 0.0)) * (1 - c) ** 1.1) if c < 1 else 0.0

# THE FLIPPERS: short ROUNDED paddles (0.38 m), set low behind the head, out, down and back; the tips CURLED UP (an
# adult's). Each a closed blade: airfoil sections along the span (5 cm thick at the root, its edges thin), the chord
# broadest a quarter out and rounding to the tip; its root run 9 cm into the flank, a smooth pad in the grid there
FL_LEN = 0.38
f_s = norm([-0.42, -0.5, 0.76]); fcd = [1.0, -0.12, 0.1]
froot = [PECT[0] + 0.06, PECT[1] + 0.02, surf_z(PECT[0] + 0.06, PECT[1] + 0.02) - 0.07]
f_c = norm(sub(fcd, mul(f_s, dot(fcd, f_s)))); f_n = cross(f_c, f_s)
if f_n[1] < 0: f_n = mul(f_n, -1)          # (the blade's upper side)
def fchord(t):
    t = min(1.0, max(0.0, t))
    return 0.19 * (1 + 0.22 * math.sin(math.pi * min(1.0, t * 1.6))) * max(0.0, 1 - t ** 2.6) ** 0.55
fthick = lambda t: lerpf(0.05, 0.014, max(0.0, t) ** 0.8)
fmid = lambda t: -0.07 * max(0.0, t) ** 1.6 - fchord(t) * 0.45   # (the chord's middle along f_c: swept back toward the tip)
fcurl = lambda t, c: 0.045 * max(0.0, (t - 0.4) / 0.6) ** 2 + 0.006 * max(0.0, t) * ((c - 0.45) / 0.55) ** 2   # (the tip up; the blade a shade cupped)
CH = [0.0, 0.07, 0.22, 0.45, 0.72, 1.0]
def frow(t):
    ch = fchord(t)
    base = add(froot, mul(f_s, t * FL_LEN))
    top, bot = [], []
    for c in CH:
        p = add(add(base, mul(f_c, fmid(t) + ch * (0.5 - c) * 1.0 + 0.45 * ch - 0.45 * ch)), mul(f_n, fcurl(t, c)))
        h = fthick(t) * airfoil(c) / 2
        top.append(add(p, mul(f_n, h))); bot.append(add(p, mul(f_n, -h)))
    return top + bot[-2:0:-1]
TS = [-0.24] + [math.sin(math.pi / 2 * i / 14) * 0.988 for i in range(15)]   # (closer toward the tip; the first row 9 cm in)
rings = [frow(t) for t in TS]
f_tip = add(add(add(froot, mul(f_s, FL_LEN)), mul(f_c, fmid(1.0))), mul(f_n, fcurl(1.0, 0.45)))
fp, ft = loft_closed(rings, tip_b=f_tip)
sh.append(membrane("flipper", fp, ft, "pectL", "@fin", mirror=True))
sh += root_pad("flipperC", add(froot, mul(f_s, 0.06)), f_s, f_c, fchord(0), 0.04, "pectL", "@skin", k=0.05, along=0.055, mirror=True)

# THE FLUKES: 1.15 m across. An adult MALE's are "put on backwards": the LEADING edges CONCAVE (dipping back toward
# the middle of each lobe, the rounded tips forward of it), the TRAILING edge CONVEX -- a fan bulging back each side of
# a shallow median NOTCH (`fan`). A female's and a calf's (`swept`): the tips swept back, the trailing edge CONCAVE.
# One closed blade across both lobes, thickest at the root -- and its root is the stock's END: the middle of the blade
# runs forward over the last ~25 cm of the sculpted stock as a FAIRING that follows the stock's own surface (sampled
# from the field: narwhal_stock.mjs -> narwhal_stock.json), first just under it (hidden), then just over it, and
# flattens out sideways into the lobes (a smooth max of the stock and the blade), so the stock spreads into the flukes
# with no shoulder and no ring. The stock's sculpt ends inside it. Patterned like the skin (the coat darkens the stock
# into the flukes' colour there), so the two meet in one colour.
ZT = 0.575
_le_fan = lambda u: X(0.925) - 0.1 * math.sin(math.pi * u * 0.8) + 0.02 * u
_te_fan = lambda u: X(0.982) - 0.13 * math.sin(math.pi * min(1, u) * 0.95) ** 0.75 + 0.07 * u * u
_le_sw = lambda u: X(0.925) - 0.05 * math.sin(math.pi * u * 0.8) - 0.17 * u ** 1.5
_te_sw = lambda u: X(0.975) + 0.035 * math.sin(math.pi * min(1, u)) - 0.1 * u ** 1.6
XF0 = -2.13                                   # (the fairing's front, inside the stock)
XW = -2.15                                    # (the wedge's front, at the stock's sides)
XC = (-2.185, -2.235)                         # (where it comes out through the stock's surface)
def planform(le0, te0):
    def f(z):
        u = min(1.0, abs(z) / ZT); m = (le0(u) + te0(u)) / 2; h = (le0(u) - te0(u)) / 2; u0 = 0.7
        env = max(0.0, 1 - ((u - u0) / (1 - u0)) ** 2) ** 0.6 if u > u0 else 1.0   # (the tip rounded, a little pointed)
        le, te = m + h * env, m - h * env
        # (the root's leading edge swept forward along the stock's sides: the WEDGE the flukes spread out of it by)
        return le + (XW - le) * (1 - sstep(0.06, 0.32, abs(z))), te
    return f
YF = 0.012
fth = lambda z: 0.012 + 0.1 * (1 - min(abs(z), ZT) / ZT) ** 1.4 + 0.016 * math.exp(-(z / 0.09) ** 2)
# (the stock's surface: its top and bottom at x and z, sampled; beyond its side it runs on down steeply)
SXR = {"x0": -2.04, "x1": -2.52, "dx": 0.01, "zs": [round(0.01 * i, 2) for i in range(21)]}
json.dump(SXR, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "narwhal_stock_req.json"), "w"))
try:
    STK = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "narwhal_stock.json")))
    if STK["zs"] != SXR["zs"] or abs(STK["rows"][0]["x"] - SXR["x0"]) > 1e-6: STK = None
except Exception:
    STK = None
if STK is None: print("NOTE: no stock samples yet -- run node narwhal_stock.mjs and this again")
def stock_at(x, z):
    """(top, bottom) of the sculpted stock at (x, |z|), or None ahead of / behind the samples"""
    if STK is None: return None
    R = STK["rows"]; i = (SXR["x0"] - x) / SXR["dx"]
    if i < 0 or i > len(R) - 1: return None
    i0 = min(int(i), len(R) - 2); f = i - i0
    def row(r):
        t, bt, zs = r["top"], r["bot"], STK["zs"]
        if t[0] is None: return None
        yc = (t[0] + bt[0]) / 2
        n = 0
        while n + 1 < len(zs) and t[n + 1] is not None: n += 1
        hw = zs[n] + 0.006                     # (its half width: just past the last sample inside)
        az = abs(z)
        if az <= zs[n]:
            j = min(int(az / 0.01), n - 1) if n > 0 else 0; g = (az - zs[j]) / 0.01 if n > 0 else 0
            tt = t[j] + (t[j + 1] - t[j]) * g if n > 0 else t[0]; bb = bt[j] + (bt[j + 1] - bt[j]) * g if n > 0 else bt[0]
            return tt, bb
        tn, bn = t[n], bt[n]; fr = (az - zs[n]) / max(1e-4, hw - zs[n])   # (closing to the side, then on down)
        if fr <= 1: return yc + (tn - yc) * math.sqrt(max(0.0, 1 - fr * fr)), yc + (bn - yc) * math.sqrt(max(0.0, 1 - fr * fr))
        return yc - 2.0 * (az - hw), yc + 2.0 * (az - hw)
    A, B = row(R[i0]), row(R[i0 + 1])
    if A is None or B is None: return A if B is None else B
    return A[0] + (B[0] - A[0]) * f, A[1] + (B[1] - A[1]) * f
def smaxk(a, b, k):
    h = max(k - abs(a - b), 0.0) / k; return max(a, b) + h * h * k * 0.25
def fluke_mesh(id, le0, te0, when):
    pf = planform(le0, te0)
    def tb(x, z):   # (the blade's top and bottom at (x, z): the fairing over the stock and the blade, smoothly maxed)
        le, te = pf(z); T = Bt = None
        if te <= x <= le:
            c = (le - x) / max(1e-6, le - te); az = abs(z)
            h = fth(az) * airfoil(c) ** (1 - 0.6 * max(0.0, 1 - az / ZT) ** 4) / 2
            y = YF - 0.03 * (az / ZT) ** 2
            T, Bt = y + h, y - h
        st = stock_at(x, z)
        if st is not None:
            yc = (st[0] + st[1]) / 2
            g = sstep(XF0, XF0 - 0.05, x)                                    # (the fairing's nose, closing inside)
            e = -0.006 + 0.012 * sstep(XC[0], XC[1], x)                     # (under the surface, then over it)
            ht, hb = yc + (st[0] - yc) * g + e, yc + (st[1] - yc) * g - e
            T = ht if T is None else smaxk(T, ht, 0.03)
            Bt = hb if Bt is None else -smaxk(-Bt, -hb, 0.03)
        return T, Bt
    CHM = [0, .02, .055, .1, .16, .24, .33, .44, .57, .71, .86, 1.0]
    def ring(z):
        le, te = pf(z)
        # (its front: where it first has thickness, searched from the fairing's nose back)
        x = max(le, XF0) if abs(z) < 0.2 else le; front = None
        while x > te:
            T, Bt = tb(x, z)
            if T is not None and T - Bt > 1e-4: front = x; break
            x -= 0.002
        if front is None: front = le
        if front < le: front = le                                           # (never behind the blade's own edge)
        top, bot = [], []
        for c in CHM:
            xx = front + (te - front) * c
            T, Bt = tb(xx, z)
            if T is None or T < Bt: T = Bt = ((T or 0) + (Bt or 0)) / 2 if T is not None else YF
            if c == 0 or c == 1.0: T = Bt = (T + Bt) / 2
            top.append([xx, T, z]); bot.append([xx, Bt, z])
        return top + bot[-2:0:-1]
    zc = [0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.125]
    zb = [0.15 + (ZT - 0.15) * math.sin(math.pi / 2 * i / 8) for i in range(1, 9)]
    zh = zc[1:] + [z for z in zb if z < ZT - 1e-6]
    zs_ = [-z for z in zh[::-1]] + [0.0] + zh
    rings = [ring(z) for z in zs_]
    le_t, _ = pf(ZT)
    tipL = [le_t, YF - 0.03, -ZT - 0.004]; tipR = [le_t, YF - 0.03, ZT + 0.004]
    P, T = loft_closed(rings, tip_a=tipL, tip_b=tipR)
    # (its skin: over the stock it follows the stock's own surface -- the grid there rides the last tail bone and the
    #  flukes' bone about 60:40 from the fairing's front to the stock's end; the lobes ride the flukes' bone alone)
    wc = lambda x: 0.4 * sstep(-2.11, -2.2, x) + 0.6 * sstep(-2.42, -2.52, x)
    skin = [[0, 1, round(max(wc(q[0]), sstep(0.1, 0.22, abs(q[2]))), 4)] for q in P]
    m = membrane(id, P, T, "fluke", "@skin", when=when)
    m["bones"] = ["tail3", "fluke"]; m["skin"] = skin
    m["pat"] = PAT; m["patFrame"] = FRAME
    return m, P, T
fk, FP, FT = fluke_mesh("flukes", _le_fan, _te_fan, "fan")
sh.append(fk)
fk2, _, _ = fluke_mesh("flukesSwept", _le_sw, _te_sw, "swept")
sh.append(fk2)

# THE TUSK (`tusk`, a male's): the LEFT upper canine, straight, 2.3 m out of the lip, a LEFT-HANDED spiral (four
# grooves winding round it), tapering evenly to a point; erupting through the upper lip a little left of the middle,
# pointing forward and a shade down. A closed lathe, drawn as it is (never gridded), its root buried 0.22 m in the jaw;
# the lip a smooth collar round it (in the grid)
def tusk(id, E, length, r0, pitch, when, nring):
    d = norm([math.cos(math.radians(4.0)), -math.sin(math.radians(4.0)), math.sin(math.radians(1.2))])
    e1 = norm(sub([0, 1, 0], mul(d, dot([0, 1, 0], d)))); e2 = cross(d, e1)   # (e1 x e2 = d)
    NA, K, G = 16, 4, 0.08
    bur = 0.22
    tot = bur + length
    rings_, tones = [], []
    for i in range(nring):
        u = i / nring                                  # (the last ring short of the point: the point its own vertex)
        s = 1 - (1 - u) ** 1.12                       # (a little closer toward the tip)
        a = s * tot                                    # (metres from the buried end)
        v = min(1.0, max(0.0, (a - bur) / length))               # (share of the visible length)
        r = r0 * (1.04 if a < bur else 1.0) * (1 - v) ** 0.92 * (1 + 0.035 * math.exp(-v / 0.04))
        g = G * (1 - sstep(0.7, 0.97, v)) * sstep(0.004, 0.05, v)   # (the grooves: worn smooth toward the point; round at the gum)
        th = 2 * math.pi * a / pitch * (1 + 0.25 * v)  # (LEFT-HANDED: the phase turns back as the tusk goes out)
        c = add(E, mul(d, a - bur))
        ring = []
        for m in range(NA):
            phi = 2 * math.pi * m / NA - th
            f = 1 - g * (0.5 - 0.5 * math.cos(K * (2 * math.pi * m / NA))) ** 1.6
            ring.append(add(c, add(mul(e1, r * f * math.cos(phi)), mul(e2, r * f * math.sin(phi)))))
            gv = (0.5 - 0.5 * math.cos(K * (2 * math.pi * m / NA))) ** 1.6
            tones.append(round((0.9 + 0.1 * v) * (1 - 0.1 * gv * g / G) * (0.93 if v < 0.06 else 1.0), 3))
        rings_.append(ring)
    tipP = add(E, mul(d, length))
    pts, tris = loft_closed(rings_, tip_b=tipP)
    tones.append(1.0)
    return membrane(id, pts, tris, "head", "@ivory", tone=tones, when=when), d
TE_ = [X(0.004), -0.135, 0.065]       # (where it leaves the lip)
tsk, TD = tusk("tusk", TE_, 2.3, 0.04, 0.46, "tusk", 56)
sh.append(tsk)
# (a FEMALE's rare small tusk: `tusklet`, 0.9 m, thinner)
tsk2, _ = tusk("tusklet", TE_, 0.9, 0.022, 0.3, "tusklet", 30)
sh.append(tsk2)
# the LIP's collar round it: a short round cone along the tusk, from inside the jaw to just past the lip
sh.append(S("cone", id="collar", bone="head", a=add(TE_, mul(TD, -0.14)), b=add(TE_, mul(TD, -0.005)), ra=0.07, rb=0.052, k=0.05, color="@skin", when="tusk"))
sh.append(S("cone", id="collar2", bone="head", a=add(TE_, mul(TD, -0.12)), b=add(TE_, mul(TD, -0.005)), ra=0.05, rb=0.033, k=0.04, color="@skin", when="tusklet"))

# the coat pattern on every gridded skin shape, in the rest pose's own space
for p in sh:
    if p.get("type") != "membrane" and p.get("op") not in ("sub", "paint") and p.get("color") != "@fin":
        p["pat"] = PAT; p["frame"] = FRAME
        p["wet"] = 0.0 if p.get("bone") in ("tail3", "fluke") else 0.12   # (the stock's end as matte as the flukes: meshes are not wet)

d = {
    "name": "narwhal",
    "_about": "SCULPTED (2026-11-07; generator tools/creaturegen/sc/sea3/gen/narwhal.py, its coat wgsl_narwhal.py): a NARWHAL, an adult MALE, 4.5 m without the tusk -- stout and cigar-shaped, deepest ~0.38 back; the small rounded head, the MELON bulging forward over a short mouth, the hint of a neck; NO dorsal fin but a low RIDGE of bumps along the rear half of the back; the stock flattened by its keels; short ROUNDED FLIPPERS curled up at the tips; the FLUKES' leading edges concave, their trailing edge convex, fanned (a male's: `fan`; a female's and a calf's `swept`, the tips swept back, the trailing edge concave), each side of a median notch, their root a wedge spreading out of the stock's sides (the blade runs forward over the stock's end, following its surface, so the stock flows into the flukes). The male's TUSK (`tusk`): the left upper canine, straight, 2.3 m, a LEFT-HANDED spiral of four grooves, tapering evenly to a point, leaving the upper lip a little left of the middle in a collar of lip. The flippers, flukes and tusk are explicit closed meshes (membranes: exact, smooth, never gridded). COAT (coatpat.js 68 `narwhal`, the rest pose's space): MOTTLED -- dark grey-brown blotches on a pale grey-cream ground, merging near solid along the back, sparse on the flanks, the belly paler and near clean; the ground's own brightness sets the age: a pale ground (an OLD male) fewer, smaller blotches; a dark grey one (a CALF) plain grey, the belly a shade paler. The flippers (a mesh, unpatterned) are a matching dark grey-brown; the flukes carry the coat, which darkens the stock's end into their colour, so the two meet in one colour. VARIANTS: female (no tusk, 0.9, swept flukes), tusked female (a rare small tusk), old male (near white), calf (1.6 m, uniform grey, swept flukes). A SWIMMER of a cold sea (sealife.js: a pod). Its tail PITCHES (axis z, four bones a beat apart).",
    "kind": "parts",
    "facet": False,
    "params": {"tusk": True, "tusklet": False, "fan": True, "swept": False},
    "flags": {"fly": {"alt": [1.2, 3.5], "speed": [1.4, 2.4], "hz": HZ}},
    "colors": {"skin": "#cdc6b8", "fin": "#4a423b", "dark": "#2e2925", "ivory": "#e6dcc4"},
    "coats": [{"name": "male"}, {"name": "male"}, {"name": "female", "scale": 0.9, "params": {"tusk": False, "fan": False, "swept": True}},
              {"name": "female", "scale": 0.9, "params": {"tusk": False, "fan": False, "swept": True}, "skin": "#c4bdb0"}],
    "variants": {
        "female": {"scale": 0.9, "params": {"tusk": False, "fan": False, "swept": True}},
        "tusked female": {"scale": 0.9, "params": {"tusk": False, "tusklet": True, "fan": False, "swept": True}},
        "old male": {"colors": {"skin": "#ece8e0", "fin": "#7b7268"}},
        "calf": {"scale": 0.36, "params": {"tusk": False, "fan": False, "swept": True}, "colors": {"skin": "#7f8486", "fin": "#6b7072"}},
    },
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mottle": {"amount": 0},
        "mesh": {"cell": 0.016, "tris": [5600, 1800], "focus": {"head": 3}, "far": 16},
        "shape": sh,
        "eyes": {"at": [X(0.098), -0.115, 0.27], "from": [X(0.098), -0.115, 0], "r": 0.016, "color": "#060606", "iris": "#2a1c12", "pupil": "round", "lid": False, "sink": 0.4, "socket": 1.05, "bone": "head"},
    },
}
write_to("sea/narwhal", d)

# ---- for wgsl_narwhal.py: the body's axis and half girths along x, and the landmarks ----------------------------------
AX = []
for s in ST:
    yc, r = tube_r(s[0]); t, b, w = s[1], s[2], s[3]
    AX.append((round(s[0], 3), round(yc, 4), round(max(r, (t - b) / 2), 4), round(max(r, w), 4)))
json.dump({"AX": AX, "XS": XS, "L": L, "XF": X(0.9), "PX": [X(0.15), X(0.3)], "LIP": LIP},open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "narwhal_wgsl.json"), "w"), indent=1)
print("tusk dir", [round(v, 3) for v in TD], "flipper pts", len(fp), "faces", len(ft) // 3, "flukes pts", len(FP), "faces", len(FT) // 3, "tusk pts", len(tsk["pts"]), "faces", len(tsk["tris"]) // 3)
