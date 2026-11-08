# THE CANID TEMPLATE: shapes laid on a dog-family rig's own joints (wolf, dog, fox), written in a grey wolf's metres and
# scaled by the species' girth (kb: its chest against the wolf's) and head (kx along it, kh across)
import math
from lib import *

def lerp(a, b, t): return [a[i] + (b[i] - a[i]) * t for i in range(3)]
def add(a, d): return [a[i] + (d[i] if i < len(d) else 0) for i in range(3)]

def canid(name, rig, o):
    J = joints(name)
    Rc, Rr = rig["rear"][:3], rig["rear"][3:6]
    Fc, Fr = rig["front"][:3], rig["front"][3:6]
    kb = Fr[1] / 0.24 * o.get("kb", 1.0)
    rH, rK, rA = rig["legs"]["radii"]
    Fh, El, Fp = J["legFLu"], J["legFLl"], J["footFL"]
    Hh, Kn, Hp = J["legHLu"], J["legHLl"], J["footHL"]
    Hd, No, Nk = J["head"], J["nose"], J["neck"]
    Er = J["earL"]
    L = No[0] - Hd[0]
    kx = L / 0.196 * o.get("kx", 1.0); kh = rig["head"][3] / 0.15 * o.get("kh", 1.0)
    h = lambda dx, dy, dz=0.0: [Hd[0] + dx * kx, Hd[1] + dy * kh, dz * kh]
    n = lambda dx, dy, dz=0.0: [No[0] + dx * kx, No[1] + dy * kh, dz * kh]
    b = lambda v: v * kb
    backY = max(Rc[1] + Rr[1], Fc[1] + Fr[1])
    zF, zH = Fh[2], Hh[2]
    lg = o.get("leg", 1.0)
    S = []
    def sh(**k): S.append(k)
    # ---- the trunk: a deep narrow chest over a pale brisket, a tucked loin, a sloping croup; a darker saddle along the back
    dp = o.get("deep", 1.0); ry = Fr[1] * 0.97; up = 2 * ry * (1 - dp)
    sh(id="chest", type="ell", c=[Fc[0] + b(0.02), Fc[1] - b(0.01) + ry * (1 - dp), 0], r=[Fr[1] * 1.18, ry * dp, Fr[2] * 0.86], k=b(0.08), color="@body")
    bk = o.get("brisket", 1.0)
    sh(id="brisket", type="ell", c=[Fc[0] + b(0.1) * bk, Fc[1] - Fr[1] * 0.5 + up, 0], r=[b(0.13) * bk, b(0.1) * bk, b(0.085) * bk], k=b(0.06), color="@chestc")
    sh(id="withers", type="ell", c=[Fh[0] + b(0.0), Fc[1] + Fr[1] * 0.6, 0], r=[b(0.17), b(0.08), b(0.1)], k=b(0.06), color="@body")
    sh(id="loin", type="ell", c=[(Rc[0] + Fc[0]) / 2, (Rc[1] + Fc[1]) / 2 + b(0.045), 0], r=[(Fc[0] - Rc[0]) * 0.62, Rr[1] * 0.62, Rr[2] * 0.82], k=b(0.08), color="@body")
    sh(id="belly", type="ell", c=[(Rc[0] + Fc[0]) / 2 + b(0.04), Rc[1] - Rr[1] * 0.42 + up * o.get("tuck", 1.0), 0], r=[b(0.21), b(0.05), b(0.09)], k=b(0.06), color="@belly")
    sh(id="rump", type="ell", c=[Rc[0] - b(0.04), Rc[1] + b(0.015), 0], r=[Rr[1] * 1.0, Rr[1] * 0.86, Rr[2] * 0.95], rot=[0, 0, -8], k=b(0.07), color="@body")
    sh(id="saddle", type="ell", c=[(Rc[0] + Fh[0]) / 2 + b(0.02), backY - b(0.068), 0], r=[(Fh[0] - Rc[0]) * 0.66 * o.get("saddle", 1), b(0.06) * o.get("saddle", 1), b(0.1) * o.get("saddle", 1) ** 1.5], k=b(0.03), kc=b(0.05), color="@saddle")
    # ---- forelegs: shoulder blade, upper arm, a straight forearm, the pastern sprung forward, a compact paw
    sh(id="scapula", type="ell", c=[Fh[0] + b(0.03), Fh[1] + b(0.16), zF * 0.85], r=[b(0.07), b(0.15), b(0.05)], rot=[0, 0, 25], k=b(0.05), color="@body", mirror=True)
    sh(id="arm", type="tube", bone="legFLu", pts=[[Fh[0] + b(0.035), Fh[1] + b(0.07), zF, rH * 1.05 * lg], [Fh[0] + b(0.005), Fh[1] - b(0.05), zF, rH * 0.92 * lg], [El[0] - b(0.012), El[1] + b(0.02), zF, rK * 1.02 * lg]], k=b(0.04), color="@body", mirror=True)
    sh(id="forearm", type="cone", bone="legFLl", a=[El[0] - b(0.008), El[1] + b(0.005), zF], b=[Fp[0] - b(0.012), Fp[1] + b(0.075), zF], ra=rK * 0.95 * lg, rb=rA * 0.72 * lg, k=b(0.03), kc=b(0.05), color="@leg", mirror=True)
    sh(id="pastern", type="cone", bone="footFL", a=[Fp[0] - b(0.012), Fp[1] + b(0.075), zF], b=[Fp[0] + b(0.012), Fp[1] + b(0.012), zF], ra=rA * 0.72 * lg, rb=rA * 0.8 * lg, k=b(0.015), color="@foot", mirror=True)
    sh(id="paw", type="ell", bone="footFL", c=[Fp[0] + b(0.03), b(0.025), zF], r=[b(0.05), b(0.025), b(0.036)], k=b(0.015), color="@foot", mirror=True)
    # ---- hind legs: a broad thigh, the gaskin back to a high hock, the long metatarsus down to the paw
    sh(id="thigh", type="ell", bone="legHLu", c=[Hh[0] + b(0.005), Hh[1] - b(0.035), zH * 1.05], r=[b(0.12), b(0.165), b(0.075)], rot=[0, 0, 18], k=b(0.05), color="@body", mirror=True)
    sh(id="gaskin", type="cone", bone="legHLu", a=[Hh[0] + b(0.03), Hh[1] - b(0.12), zH], b=[Kn[0] - b(0.045), Kn[1] + b(0.005), zH], ra=b(0.058) * lg, rb=rK * 0.62 * lg, k=b(0.03), kc=b(0.05), color="@leg", mirror=True)
    sh(id="hock", type="cone", bone="legHLl", a=[Kn[0] - b(0.045), Kn[1], zH], b=[Hp[0] + b(0.002), Hp[1] + b(0.035), zH], ra=rK * 0.56 * lg, rb=rA * 0.7 * lg, k=b(0.02), color="@foot", mirror=True)
    sh(id="hpaw", type="ell", bone="footHL", c=[Hp[0] + b(0.028), b(0.023), zH], r=[b(0.046), b(0.023), b(0.033)], k=b(0.014), color="@foot", mirror=True)
    # ---- the neck, thick with fur: a darker nape, a pale throat ruff
    ang = math.degrees(math.atan2(Hd[1] - Nk[1], Hd[0] - Nk[0]))
    sh(id="neck", type="ell", bone="neck", c=add(lerp(Nk, Hd, 0.42), [0, -b(0.01)]), r=[b(0.17), b(0.125), b(0.1) * o.get("gneck", 1)], rot=[0, 0, ang], k=b(0.07), color="@body")
    if not o.get("noNape"): sh(id="nape", type="ell", bone="neck", c=add(lerp(Nk, Hd, 0.38), [-b(0.02), b(0.075)]), r=[b(0.14), b(0.06), b(0.08)], rot=[0, 0, ang * 0.6], k=b(0.03), kc=b(0.04), color="@saddle")
    if o.get("topline"):
        tl = o["topline"]
        Oc = [Hd[0] - tl.get("occX", 0.055) * kx, Hd[1] + tl.get("occY", 0.0) * kh, 0]
        Wt = [Fh[0] - b(0.03), Fc[1] + Fr[1] * tl.get("wY", 0.4), 0]
        Lb = [(Rc[0] + Fc[0]) / 2, (Rc[1] + Fc[1]) / 2 + b(0.045), 0]
        sh(id="crest", type="cone", bone="neck", a=Oc, b=Wt, ra=tl.get("ra", 0.06) * kh, rb=Fr[1] * tl.get("rb", 0.55), k=b(0.05), color="@body")
        sh(id="back", type="cone", a=Wt, b=Lb, ra=Fr[1] * tl.get("rb", 0.55), rb=Rr[1] * 0.6, k=b(0.05), color="@body")
    th = o.get("throat", 1) * 0.78
    sh(id="throat", type="ell", bone="neck", c=add(lerp(Nk, Hd, 0.6), [b(0.015), -b(0.055)]), r=[b(0.11) * th, b(0.085) * th, b(0.08) * o.get("gneck", 1) * th], rot=[0, 0, ang], k=b(0.05), kc=b(0.035), color="@throat")
    if o.get("bib"):   # an unbroken BIB, chin to chest: a band down the neck's underside
        sh(id="bib", type="cone", bone="neck", a=h(0.005, -0.058), b=[Fc[0] + b(0.17), Fc[1] - b(0.06) + ry * (1 - dp), 0], ra=0.036 * kh, rb=b(0.075), k=b(0.03), kc=b(0.01), color="@throat")
    # ---- the head: a broad cranium, flared pale cheeks, a long muzzle under a gentle stop, a black wet nose
    dm = o.get("dome", 0.0)
    sh(id="cranium", type="ell", bone="head", c=h(-0.015 + dm * 0.01, 0.02 + dm * 0.022), r=[0.085 * kx, 0.068 * kh * (1 + dm * 0.22), 0.07 * kh * (1 + dm * 0.1) * o.get("skullW", 1)], k=0.03 * kh, color="@head")
    sh(id="cheek", type="ell", bone="head", c=h(-0.0, -0.022, 0.048 * o.get("skullW", 1)), r=[0.06 * kx, 0.05 * kh, 0.038 * kh * o.get("skullW", 1)], k=0.025 * kh, color="@mask", mirror=True)
    sh(id="ruffC", type="ell", bone="head", c=h(-0.05, -0.035, 0.053), r=[0.044 * kx, 0.068 * kh, 0.033 * kh], rot=[-12, 0, 12], k=0.035 * kh, kc=0.03 * kh, color=o.get("ruffC", "@mask"), mirror=True)
    sh(id="brow", type="ell", bone="head", c=h(0.045, 0.045, 0.032), r=[0.022 * kx, 0.014 * kh, 0.019 * kh], k=0.012 * kh, kc=0.006 * kh, color="@mask", mirror=True)
    st = o.get("stop", 0.0)
    if o.get("stepStop"):
        # a STOP: the forehead a step above the bridge (a dog's): the bridge's root dropped, a brow ridge over it
        sh(id="bridge", type="cone", bone="head", a=h(0.055, 0.03), b=n(-0.022, 0.012), ra=0.03 * kh, rb=0.019 * kh * o.get("blunt", 1), k=0.012 * kh, color="@head")
        sh(id="forehead", type="ell", bone="head", c=h(0.02, 0.05 + st), r=[0.045 * kx, 0.036 * kh, 0.05 * kh], k=0.02 * kh, color="@head")
    else:
        sh(id="bridge", type="cone", bone="head", a=h(0.035, 0.04 + st), b=n(-0.022, 0.012), ra=0.033 * kh, rb=0.019 * kh * o.get("blunt", 1), k=0.02 * kh, color="@head")
    sh(id="muzzle", type="cone", bone="head", a=h(0.05, -0.004), b=n(-0.026, -0.008), ra=0.047 * kh, rb=0.025 * kh * o.get("blunt", 1), k=0.02 * kh, color="@muzzleC")
    sh(id="lip", type="ell", bone="head", c=n(-0.07, -0.024, 0.022 * o.get("blunt", 1)), r=[0.058 * kx, 0.019 * kh * o.get("flews", 1), 0.015 * kh], k=0.012 * kh, kc=0.006 * kh, color="@lip", mirror=True)
    sh(id="jaw", type="cone", bone="head", a=h(0.0, -0.048), b=n(-0.035, -0.036), ra=0.03 * kh, rb=0.017 * kh * o.get("blunt", 1), k=0.016 * kh, color="@lip")
    if o.get("lab"):   # (audit 2026-11-07, round 3) A FARM DOG'S HEAD (a Labrador's): the muzzle DEEP at its root and tapering to the
        # nose; the upper lip's FLEWS hanging a little over the lower jaw; the cheek muscle over the zygomatic arch; BROWS above the eyes
        sw = o.get("skullW", 1)
        sh(id="muzzleBase", type="ell", bone="head", c=h(0.072, -0.02), r=[0.052 * kx, 0.044 * kh, 0.046 * kh * sw], k=0.022 * kh, color="@muzzleC")
        sh(id="flew", type="ell", bone="head", c=n(-0.048, -0.035, 0.025), r=[0.054 * kx, 0.026 * kh, 0.011 * kh], rot=[0, 0, -6], k=0.01 * kh, kc=0.004 * kh, color="@lip", mirror=True)
        sh(id="zyg", type="ell", bone="head", c=h(0.008, -0.012, 0.056 * sw), r=[0.046 * kx, 0.034 * kh, 0.026 * kh], rot=[0, 0, -8], k=0.018 * kh, color="@head", mirror=True)
        sh(id="browL", type="ell", bone="head", c=h(0.05, 0.054, 0.036), r=[0.028 * kx, 0.016 * kh, 0.021 * kh], rot=[0, 0, -12], k=0.01 * kh, kc=0.004 * kh, color="@head", mirror=True)
    nb = o.get("noseBig", 1.0)
    sh(id="nose", type="ell", bone="head", c=n(-0.006 + 0.008 * (nb - 1) + o.get("noseX", 0), 0.003 * (nb - 1)), r=[0.016 * kx * nb * o.get("noseFlat", 1), 0.015 * kh * nb, 0.019 * kh * o.get("noseZ", o.get("blunt", 1)) * nb], k=0.006 * kh, kc=0.002 * kh, color="@nose", wet=o.get("noseWet", 0.55))
    if o.get("mouth"):
        # NOSTRILS (two dark commas on the leather's front) and the MOUTH LINE (a dark seam along the lip, back to the corner)
        nc = n(-0.006 + 0.008 * (nb - 1) + o.get("noseX", 0), 0.003 * (nb - 1))
        sh(id="nostril", type="ell", bone="head", c=[nc[0] + 0.012 * kx * nb, nc[1] - 0.001 * kh, 0.0075 * kh * nb], r=[0.004 * kx, 0.0035 * kh, 0.0048 * kh], rot=[0, 30, -20],
           k=0.001, kc=0.0005, color="@black", mirror=True, seat={"from": nc, "out": -0.45})
        for i, (dx, dz, yaw) in enumerate([] if not o.get("mouthLine") else [(-0.02, 0.012, -15), (-0.05, 0.022, -25), (-0.08, 0.027, -12)]):
            sh(id=f"mouth{i}", type="ell", bone="head", c=n(dx, -0.036, dz), r=[o.get("seamL", 0.018) * kx, 0.0032 * kh, 0.006 * kh], rot=[0, yaw, 0], k=0.001, kc=0.0006,
               color="@black", mirror=True, seat={"from": n(dx, -0.03, 0), "out": -0.2})
    # ---- the ears (on their own bones: they flick)
    ear = o.get("ear", {})
    el, eo = ear.get("len", 1), ear.get("out", 0)   # (a soft drop ear's length; how far out from the cheek it lies)
    if ear.get("drop"):
        if ear.get("soft"):   # (audit 2026-11-07, a dog's: the leather a soft TAPERING flap lying against the cheek -- thicker at
            # the fold, narrowing to a rounded tip below the eye line -- not a flat paddle standing off the skull)
            sh(id="ear", type="ell", bone="earL", c=[Er[0] + 0.01 * kx, Er[1] - 0.05 * el * kh, Er[2] + (0.012 + eo) * kh], r=[0.034 * kx, 0.05 * el * kh, 0.015 * kh], rot=[-10, 0, -10], k=0.014 * kh, kc=0.003 * kh, color="@ear", mirror=True)
            sh(id="earLow", type="ell", bone="earL", c=[Er[0] + 0.016 * kx, Er[1] - 0.094 * el * kh, Er[2] + (0.016 + eo * 1.2) * kh], r=[0.024 * kx, 0.03 * kh, 0.013 * kh], rot=[-6, 0, -14], k=0.014 * kh, kc=0.003 * kh, color="@ear", mirror=True)
        else:
            sh(id="ear", type="ell", bone="earL", c=[Er[0] + 0.006 * kx, Er[1] - 0.05 * kh, Er[2] + 0.034 * kh], r=[0.042 * kx, 0.062 * kh, 0.011 * kh], rot=[-7, 0, -12], k=0.006 * kh, kc=0.003 * kh, color="@ear", mirror=True)
        # the FOLD: a thick roll at the root, over the skull's side and out to the flap
        sh(id="earRoot", type="ell", bone="earL", c=[Er[0] + 0.004 * kx, Er[1] - (0.008 if ear.get("soft") else -0.002) * kh, Er[2] + (0.016 if ear.get("soft") else 0.026) * kh], r=[0.036 * kx * (0.8 if eo else 1), 0.02 * kh * (0.8 if eo else 1), 0.024 * kh], rot=[-30, 0, 0], k=0.012 * kh, kc=0.004 * kh, color="@ear", mirror=True)
    elif ear.get("cup"):
        # THE CUPPED EAR: two thick triangles (field slabs, rounded at every edge and the tip) folded along the midline, the
        # fold set back so the front is an open hollow; broad at the base; its inside a pale plate laid in each half
        c = ear["cup"]; E = lambda d: [Er[0] + d[0] * kx, Er[1] + d[1] * kh, Er[2] + (d[2] + c.get("apart", 0)) * kh]
        Bi, Bo, M0, T = E(c["bi"]), E(c["bo"]), E(c["mid"]), E(c["tip"]); r = c["r"] * kh
        sub3 = lambda u, v: [u[i] - v[i] for i in range(3)]
        cr3 = lambda u, v: [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
        lerp3 = lambda u, v, t: [u[i] + (v[i] - u[i]) * t for i in range(3)]
        # round 7 (review: a red fox's ear is broad at the base, its OUTER EDGE CONVEX, the black only on the back and the
        # upper third): the outer half bulges through Q; the slab is the front colour, a black slab set just behind it
        # makes the back, and a black cap covers the top third on both faces
        halves = [[Bi, M0, T]]
        if c.get("bulge"):
            Q = E(c["bulge"]); halves += [[M0, Bo, Q], [M0, Q, T]]
        else:
            halves += [[M0, Bo, T]]
        col = c.get("col", "@ear"); back = c.get("back"); tipc = c.get("tipCol"); ft = c.get("tipFrac", 0.34)
        for j, (A, B, C) in enumerate(halves):
            sh(id=f"ear{j}", type="tri", bone="earL", a=A, b=B, c=C, r=r, k=c.get("k", 0.006) * kh, kc=0.002 * kh, color=col, mirror=True)
            nv = cr3(sub3(B, A), sub3(C, A)); ln = math.sqrt(sum(v * v for v in nv)); nv = [v / ln for v in nv]
            if nv[0] < 0: nv = [-v for v in nv]
            g = [(A[i] + B[i] + C[i]) / 3 for i in range(3)]
            if back:
                bk = lambda P: [g[i] + (P[i] - g[i]) * 0.97 - nv[i] * r * 0.55 for i in range(3)]
                sh(id=f"earBack{j}", type="tri", bone="earL", a=bk(A), b=bk(B), c=bk(C), r=r * 0.9, k=0.002 * kh, kc=0.001 * kh, color=back, mirror=True)
            fin = c.get("inTip", 0.62); fb = c.get("inBase", 0.7)
            sh_ = lambda P, f: [g[i] + (P[i] - g[i]) * f + nv[i] * (r * c.get("inLift", 1.0) + 0.0012 * kh) for i in range(3)]
            sh(id=f"earIn{j}", type="tri", bone="earL", a=sh_(A, fb), b=sh_(B, fb), c=sh_(C, fin if C is T else fb), r=0.0008 * kh, color="@earIn", mirror=True)
        if tipc:
            # the black cap: the top `ft` of the ear, a slab a shade thicker than the ear so it wins both faces
            L = [lerp3(T, P, ft) for P in ([Bi, M0, Q] if c.get("bulge") else [Bi, M0, Bo])]
            for j, (A, B) in enumerate(((L[0], L[1]), (L[1], L[2]))):
                sh(id=f"earTip{j}", type="tri", bone="earL", a=A, b=B, c=T, r=r * 1.12, k=0.002 * kh, kc=0.001 * kh, color=tipc, mirror=True)
    else:
        tip = ear.get("tip", [-0.015, 0.1, 0.028]); ra = ear.get("ra", 0.034)
        sh(id="ear", type="cone", bone="earL", a=[Er[0], Er[1] - 0.005 * kh, Er[2]], b=[Er[0] + tip[0] * kx, Er[1] + tip[1] * kh, Er[2] + tip[2] * kh], ra=ra * kh, rb=0.004 * kh, k=0.012 * kh, kc=0.003 * kh, color="@ear", mirror=True)
        if ear.get("front"):
            sh(id="earFront", type="ell", bone="earL", c=[Er[0] + 0.011 * kx, Er[1] + tip[1] * 0.3 * kh, Er[2] + tip[2] * 0.3 * kh], r=[0.008 * kx, tip[1] * 0.34 * kh, ra * 0.82 * kh], rot=[-15, -25, 0], k=0.006 * kh, kc=0.002 * kh, color=ear["front"], mirror=True)
        sh(id="earIn", type="ell", bone="earL", c=[Er[0] + 0.012 * kx, Er[1] + tip[1] * 0.42 * kh, Er[2] + tip[2] * 0.4 * kh], r=[0.006 * kx, tip[1] * 0.3 * kh, ra * 0.5 * kh], rot=[-15, -25, 0], k=0.004 * kh, kc=0.002 * kh, color="@earIn", mirror=True)
    ey = o.get("eyeY", 0.0)
    eyes = {"at": h(o.get("eyeX", 0.058), 0.034 + ey, 0.04), "from": h(-0.01, 0.02 + ey, 0), "r": 0.0125 * kh * o.get("eye", 1), "iris": "@eye", "pupil": o.get("pupil", "round"), "lid": "@lid", "sink": o.get("sink", 0.5), "socket": 1.1}
    return S, eyes
