# cervid.py deer|reindeer|cervicapra|oryx -- the deer frame's sculpts, written from the rig's joints
import sys
from lib import *
from lib import _cr
name = "chamois"; IMP = True
# THE RED DEER's rig, stretched (round 2): the trunk 0.2 m longer behind (the rear, the hind legs, the tail back) and the
# head cluster forward and down (the neck carried at ~40 degrees, not 55) -- from the frame's values, so a re-run never
# shifts it twice
DH = (0.14, -0.1) if name == "deer" else (0.0, 0.0)
if name == "deer":
    FRM = json.load(open(ROOT + "assets/creatures/frames/deer.json"))
    pre = json.load(open(ROOT + "assets/creatures/mammals/deer.json"))
    def sh(v, ix, d): return f"{float(v.split('*')[0]) + d:.3f}*s" if isinstance(v, str) else v
    def mv(arr, pairs):
        out = list(arr)
        for i in pairs: out[i] = sh(out[i], i, DH[0]); out[i + 1] = sh(out[i + 1], i + 1, DH[1])
        return out
    rig = {"rear": [sh(FRM["rear"][0], 0, -0.2)] + FRM["rear"][1:],
           "tail": {**FRM["tail"], "c": [sh(FRM["tail"]["c"][0], 0, -0.2), FRM["tail"]["c"][1]]},
           "neck": mv(FRM["neck"], [3]), "head": mv(FRM["head"], [0]), "muzzle": mv(FRM["muzzle"], [0, 3]),
           "nose": mv(FRM["nose"], [0]), "ears": mv(FRM["ears"], [0, 3]), "eyes": mv(FRM["eyes"], [0])}
    lg = pre.get("legs", {}); lg["hind"] = [sh(FRM["legs"]["hind"][0], 0, -0.2)] + list(lg.get("hind", FRM["legs"]["hind"])[1:]); rig["legs"] = lg
    if any(pre.get(k) != v for k, v in rig.items()):
        pre.update(rig); json.dump(pre, open(ROOT + "assets/creatures/mammals/deer.json", "w"), indent=2, ensure_ascii=False)
# (round 4: the hind legs moved BACK under the buttocks -- the rump stood out behind the thigh as a shelf over a thin
#  shank -- and the rump drawn in a little, the tail with it; from the frame's values, so a re-run never shifts it twice)
HB = {"deer": 0.1, "reindeer": 0.1, "cervicapra": 0.07, "impala": 0.07, "chamois": 0.07, "oryx": 0.09}[name]
PI = {"deer": 0.04, "reindeer": 0.06, "cervicapra": 0.05, "impala": 0.05, "chamois": 0.05, "oryx": 0.06}[name]
FRM = json.load(open(ROOT + "assets/creatures/frames/deer.json"))
pre = json.load(open(ROOT + f"assets/creatures/mammals/{name}.json"))
BASE = {"deer": -0.62, "reindeer": -0.42, "cervicapra": -0.42, "impala": -0.42, "chamois": -0.42, "oryx": -0.477}[name]
TB = float(FRM["tail"]["c"][0].split("*")[0]) - (0.2 if name == "deer" else 0)
# (round 2, 2026-11-06: a STOCKY goat-antelope, not an impala -- the head cluster drawn back and down (a short thick
#  neck), the face shortened (a short goat head); the rig built each run from its first values (chamois_rig0.json) so a
#  re-run never shifts it twice; the whole animal LOWERED on shorter legs at the end -- see DROP)
R0 = json.load(open(HERE + "/chamois_rig0.json"))
HX, HY, SN = -0.06, -0.07, -0.065   # (the head cluster's shift; the face's shortening -- x s)
def cs(v, d): return f"{float(v.split('*')[0]) + d:.3f}*{v.split('*', 1)[1]}" if isinstance(v, str) and d else v
def mvp(arr, idx, dx, dy): return [cs(v, dx if i in idx else dy if i - 1 in idx else 0) for i, v in enumerate(arr)]
RG = {"neck": mvp(R0["neck"], (3,), HX, HY), "head": mvp(R0["head"], (0,), HX, HY),
      "muzzle": mvp(mvp(R0["muzzle"], (0, 3), HX, HY), (3,), SN, 0), "nose": mvp(mvp(R0["nose"], (0,), HX, HY), (0,), SN, 0),
      "ears": mvp(R0["ears"], (0, 3), HX, HY), "eyes": mvp(R0["eyes"], (0,), HX, HY), "rear": FRM["rear"], "front": FRM["front"]}
lg = json.loads(json.dumps(R0["legs"])); lg["hind"] = [f"{BASE - HB:.3f}*s"] + lg["hind"][1:]; lg["front"][2], lg["hind"][2] = "0.14*s", "0.15*s"   # (= CFG lz, hz below)
tl = {**FRM["tail"], "c": [f"{TB + PI:.3f}*s", FRM["tail"]["c"][1]]}
pre.update(RG); pre["params"] = {"s": 0.7, "bulk": 1.2}; pre["legs"] = lg; pre["tail"] = tl; pre.pop("sculpt", None)
json.dump(pre, open(HERE + "/_chamois_base.json", "w"), indent=1, ensure_ascii=False)
J = joints(name, HERE + "/_chamois_base.json")
CFG = {
    "deer":       dict(s=1.0, bulk=1.0, by=1.0, lz=0.13, hz=0.14, up=0.0, T=1.0),
    "reindeer":   dict(s=0.95, bulk=1.25, by=1.08, lz=0.15, hz=0.16, up=0.0, T=1.3),
    "cervicapra": dict(s=0.7, bulk=0.9, by=0.88, lz=0.13, hz=0.14, up=0.04, T=0.95),
    "impala": dict(s=0.74, bulk=0.88, by=0.9, lz=0.13, hz=0.14, up=0.04, T=0.92),
    "chamois": dict(s=0.7, bulk=1.2, by=1.14, lz=0.14, hz=0.15, up=0.03, T=1.55),
    "oryx":       dict(s=0.95, bulk=1.2, by=1.0, lz=0.14, hz=0.15, up=0.02, T=1.15),
}[name]
s, bk, by, UP = CFG["s"], CFG["bulk"], CFG["by"], CFG["up"]
RD, BB, BL, CV, OX = name == "reindeer", name == "deer", None, name in ("cervicapra", "impala", "chamois"), name == "oryx"
S = Sculpt()
B = "@body"
Y0 = 0.98   # the trunk's mid line (deer units): depth scales with bulk about it
def P(x, y, z=0): return [x * s, (Y0 + (y - Y0) * by) * s, z * s * bk]
def r3(a, b, c): return [a * s, b * s * by, c * s * bk]
XS = 0.9 if CV else 1.0   # (a blackbuck is compact: its trunk drawn in toward the middle)
def STR(x): return x if name != "deer" else x - 0.2 * min(1, max(0, (0.1 - x) / 0.6))   # (the red deer's trunk stretched behind the chest)
def PX(x, y, z=0): return P(STR(-0.12 + (x + 0.12) * XS), y, z)
K = lambda k: k * s * bk
def conform(id, base, sx, sz, drop, color, k=0.02, kc=0.006):
    """a paint layer that hugs a trunk shape: a copy a little narrower, dropped a little -- it breaks the skin only
    below where the two cross, so the colour edge runs along the flank without a slab standing proud"""
    d = next(q for q in S.shapes if q["id"] == base)
    c = [d["c"][0], d["c"][1] - drop * s, d["c"][2]]
    S.ell(id, c, [d["r"][0] * sx, d["r"][1], d["r"][2] * sz], rot=d.get("rot"), k=K(k), kc=K(kc), color=color, mirror=d.get("mirror"))
# ---- trunk: a deep narrow chest, the barrel tucked up to the flank, a round rump
S.ell("chest", PX(0.28, 1.0), r3(0.36 * XS, 0.22, 0.19), k=K(0.08), color=B)
S.ell("withers", PX(0.24, 1.15), r3(0.3 * XS, 0.1, 0.1), rot=[0, 0, -12], k=K(0.07), color="@back")
PB = CV or OX   # (pied: the white underparts ARE the belly shapes, the lowest skin, cut clean along the low flank)
S.ell("barrel", PX(-0.1, 1.04 if PB else 1.02), r3(0.6 if BB else 0.48 * XS, 0.18, 0.21), rot=[0, 0, -4], k=K(0.08), color=B)
S.ell("loin", PX(-0.42, 1.08), r3(0.3 * XS, 0.13, 0.17), k=K(0.08), color="@back")
DR = name == "deer"   # (the stretched deer: a slimmer croup tapering to the tail, the haunch down onto the thigh)
S.ell("rump", PX((-0.57 if CV else -0.62) + PI, 1.07 if DR else 1.05), r3(0.22, 0.135, 0.155) if DR else r3(0.22 if CV else 0.28 * XS, 0.17, 0.19), rot=[0, 0, -10 if DR else 0], k=K(0.1 if DR else 0.08), color=B)
S.ell("haunch", PX(-0.6 + PI, 0.93, 0.085) if DR else PX(-0.64 + PI, 0.97, 0.09), r3(0.2, 0.17, 0.095) if DR else r3(0.23 * XS, 0.19, 0.11), rot=[0, 0, -8 if DR else 0], k=K(0.07 if DR else 0.06), color=B, mirror=True)
S.ell("scapula", PX(0.38, 1.04, 0.11), r3(0.07, 0.19, 0.06), rot=[0, 0, 30], k=K(0.05), color=B, mirror=True)
S.ell("breast", PX(0.55, 0.92, 0.06), r3(0.1, 0.13, 0.085), rot=[0, 0, 12], k=K(0.05), color=B, mirror=True)
belly = B if CV else "@belly"   # (the blackbuck's white underside: the shade below, cut level along the flank)
S.ell("belly", PX(-0.06 if CV else -0.04, (0.95 if CV else 0.865) + UP if PB else 0.9), (r3(0.56 * XS, 0.13, 0.215) if CV else r3(0.44 * XS, 0.055, 0.2)) if PB else r3(0.48 if BB else 0.38 * XS, 0.08, 0.16), rot=[0, 0, -6], k=K(0.07), kc=K(0.015 if PB else 0.05), color=belly)
S.ell("girth", PX(0.3, (0.88 if CV else 0.84) + UP), (r3(0.26 * XS, 0.12, 0.17) if CV else r3(0.24 * XS, 0.085, 0.15)) if PB else r3(0.22 * XS, 0.07, 0.14), k=K(0.06), kc=K(0.015 if PB else 0.05), color=belly)
S.ell("rumpPatch", PX((-0.74 if CV else -0.79) + PI, 1.01), r3(0.06, 0.17, 0.14) if BB else r3(0.05, 0.14, 0.11), k=K(0.01), kc=K(0.025), color="@patch")
S.cone("dock", PX(-0.84 + PI, 1.1), PX(-0.92 + PI, 1.07), 0.04 * s, 0.035 * s, k=K(0.03), color=B)
# ---- neck: thick at the chest, carried high to the poll; a throat a shade paler
poll = [J["head"]["o"][0] - 0.035 * s, J["head"]["o"][1] + 0.09 * s, 0]
nb = P(0.55, 1.1)
NW = {"deer": 1.0, "reindeer": 1.1, "cervicapra": 1.4, "impala": 1.4, "chamois": 1.32, "oryx": 1.4}[name]
S.ell("neckBase", nb, r3(0.24, 0.25, 0.17) if name == "impala" else r3(0.2, 0.2, 0.135) if name == "chamois" else r3(0.22, 0.19 * min(NW, 1.2), 0.14 * min(NW, 1.25)), rot=[0, 0, 45 if name in ("impala", "chamois") else 50], k=K(0.08), color="@neckc" if RD else "@back")
nm = lerp(nb, poll, 0.5)
nd = sub(poll, nb)
S.ell("neck", add(nm, [0.0, -0.02 * s, 0]), [length(nd) * 0.55, 0.115 * s * bk * NW, 0.085 * s * bk * NW], rot=[0, 0, ang(nd)], bone="neck", k=K(0.07), color="@neckc" if RD else B)
S.ell("throat", add(lerp(nb, poll, 0.72), [0.02 * s * (NW - 1), -0.04 * s * (NW - 1), 0]), [0.12 * s, 0.07 * s * bk * NW, 0.065 * s * bk * NW], rot=[0, 0, ang(nd) + 15], bone="neck", k=K(0.05), color="@throat")
# ---- head: a slim wedge from the poll to a dark wet nose; big ears
tip = [J["nose"]["o"][0] + 0.03 * s, J["nose"]["o"][1] - 0.03 * s, 0] if "nose" in J else None
hf = Frame(poll, sub(tip, poll)); L = length(sub(tip, poll))
def H(t, h=0, z=0): return hf(t * L, h * L, z * L)
hr = hf.rot()
S.ell("cranium", H(0.2, -0.05), [0.22 * L, 0.2 * L, 0.19 * L], rot=hr, bone="head", k=K(0.03), color="@head")
S.ell("jaw", H(0.45, -0.17, 0.07), [0.25 * L, 0.12 * L, 0.06 * L], rot=hf.rot(-6), bone="head", k=K(0.03), color="@head", mirror=True)
S.cone("face", H(0.28, -0.01), H(0.86, -0.04), 0.15 * L, 0.085 * L, bone="head", k=K(0.03), color="@head")
S.ell("muzzle", H(0.9, -0.08), [0.11 * L, 0.11 * L, 0.09 * L], rot=hr, bone="head", k=K(0.025), color="@muzzle")
S.ell("nose", H(0.98, -0.03), [0.035 * L, 0.06 * L, 0.07 * L], rot=hr, bone="head", k=K(0.008), kc=0.003, color="@nose", wet=0.4)
S.ell("chin", H(0.83, -0.18), [0.09 * L, 0.04 * L, 0.06 * L], rot=hr, bone="head", k=K(0.02), kc=K(0.008), color="@chin")
S.ell("gland", H(0.47, 0.0, 0.135), [0.08 * L, 0.018 * L, 0.02 * L], rot=hf.rot(-28), bone="head", k=K(0.006), kc=0.002, color="@gland", mirror=True)
eye = H(0.34, 0.08, 0.17)
# ears: big, oval, out to the side and up
EAR = {"deer": (0.24, 0.045, [-0.15, 0.75, 0.65]), "reindeer": (0.15, 0.04, [-0.2, 0.7, 0.7]), "cervicapra": (0.17, 0.034, [-0.1, 0.65, 0.75]), "impala": (0.21, 0.042, [-0.2, 0.5, 0.85]), "chamois": (0.17, 0.036, [-0.16, 0.86, 0.48]), "oryx": (0.17, 0.05, [-0.2, 0.8, 0.55])}[name]
el, ew, edir = EAR
# (the ear fix, 2026-11-06: the impala's ear sat 4 cm in front of its own bone, its inner edge standing in the horn's
#  base as the horn swept back over it -- now ON its bone's root, at the skull's back corner behind the horn, and held
#  more out to the side, so the horn rises clear of it through the whole flick)
eb = list(J["earL"]["o"]) if IMP else H(0.1, 0.1, 0.13)
ed = norm(edir)
ec = add(eb, ed, el * s * 0.42)
EK = 0.02 if OX else 0.012   # (an oryx's broad ears: smoother)
S.ell("ear", ec, [0.018 * s, el * s * 0.42, ew * s], rot=orient(ed), bone="earL", k=K(EK), kc=0.004, color="@ear", mirror=True)
S.ell("earTip", add(eb, ed, el * s * 0.8), [0.014 * s, el * s * 0.2, ew * s * (0.7 if OX else 0.5)], rot=orient(ed), bone="earL", k=K(0.015), kc=0.004, color="@ear", mirror=True)
S.ell("earIn", add(ec, [0.013 * s, 0, 0]), [0.007 * s, el * s * 0.36, ew * s * 0.62], rot=orient(ed), bone="earL", k=K(0.004), kc=0.002, color="@earIn", mirror=True)
# ---- legs: slender; forearm and gaskin the only muscle, then bone and tendon to the cloven hooves
fx, fz = J["legFLu"]["o"][0], J["legFLu"]["o"][2]
kn = J["legFLu"]["o"][1] - 0.45 * s   # (the knee: the deer frame's fore upper bone below the hip -- the rig's joint is the elbow now)
EL = 0.72   # (the fore legs' IK joint, at the ELBOW (x s): a knee folding forward under the IK read as buck-kneed in the stride)
hx, hz = J["legHLu"]["o"][0], J["legHLu"]["o"][2]
hk = J["legHLl"]["o"][1]
LG = "@leg"
T = CFG["T"]    # (bulk thickens the legs too)
fl = 0.13 * s               # (fetlock height)
CT = 1.4 if RD else 1.3 if name == "chamois" else 1.0     # (a reindeer's cannons: stout)
TS = 1.4 if RD else 1.22 if name == "chamois" else 1.0     # (...and its crescent hooves: huge, splayed)
S.ell("arm", [fx + 0.0 * s, 0.77 * s, fz * 0.8], [0.09 * s * T, 0.13 * s, 0.065 * s * T], rot=[0, 0, -22], bone="legFLu", k=K(0.05), color=B, mirror=True)
S.cone("forearm", [fx - 0.02 * s, 0.7 * s, fz], [fx, kn + 0.02 * s, fz], 0.05 * s * T, 0.028 * s * T, bone="legFLl", k=K(0.03), color="@upleg", mirror=True)
S.ell("knee", [fx + 0.003 * s, kn - 0.01 * s, fz], [0.03 * s * T, 0.033 * s, 0.027 * s * T], bone="legFLl", k=K(0.015), color=LG, mirror=True)
S.cone("cannon", [fx, kn - 0.03 * s, fz], [fx + 0.004 * s, fl + 0.01 * s, fz], 0.02 * s * T * CT, 0.018 * s * T * CT, bone="legFLl", k=K(0.012), color=LG, mirror=True)
S.cone("tendon", [fx - 0.016 * s, kn - 0.05 * s, fz], [fx - 0.012 * s, fl + 0.02 * s, fz], 0.012 * s * T, 0.013 * s * T, bone="legFLl", k=K(0.01), color=LG, mirror=True)
S.ell("fetlock", [fx, fl, fz], [0.027 * s * T * CT, 0.027 * s * CT, 0.024 * s * T * CT], bone="legFLl", k=K(0.012), color=LG, mirror=True)
S.cone("pastern", [fx, fl - 0.01 * s, fz], [fx + 0.022 * s, 0.055 * s, fz], 0.02 * s * T * CT, 0.02 * s * T * CT, bone="legFLl", k=K(0.01), color=LG, mirror=True)
HW = 1.9 if RD else 1.25 if name == "chamois" else 1.0     # (a reindeer's hooves are broad: snowshoes)
for side, dz in (("o", 1), ("i", -1)):
    S.ell("toe" + side, [fx + 0.035 * s * TS, 0.022 * s * TS, fz + dz * 0.013 * s * HW * TS], [0.032 * s * (1 + (HW - 1) * 0.4) * TS, 0.022 * s * TS, 0.013 * s * HW * TS], rot=[0, -10 * dz * (TS > 1), -18], bone="footFL", k=K(0.004), kc=0.002, color="@foot", mirror=True)
    S.ell("htoe" + side, [hx + 0.035 * s * TS, 0.022 * s * TS, hz + dz * 0.013 * s * HW * TS], [0.031 * s * (1 + (HW - 1) * 0.4) * TS, 0.021 * s * TS, 0.013 * s * HW * TS], rot=[0, -10 * dz * (TS > 1), -18], bone="footHL", k=K(0.004), kc=0.002, color="@foot", mirror=True)
if RD:   # dewclaws behind the fetlock; a pale ring above the hooves
    for f, (xx, zz) in (("F", (fx, fz)), ("H", (hx, hz))):
        S.ell("dew" + f, [xx - 0.035 * s, 0.075 * s, zz], [0.018 * s, 0.014 * s, 0.03 * s], rot=[0, 0, 30], bone="legFLl" if f == "F" else "legHLl", k=K(0.006), kc=0.002, color="@foot", mirror=True)
        S.ell("sock" + f, [xx + 0.008 * s, 0.085 * s, zz], [0.024 * s * T, 0.025 * s, 0.022 * s * T], bone="legFLl" if f == "F" else "legHLl", k=K(0.006), kc=0.01, color="@sock", mirror=True)
S.ell("thigh", [hx + 0.01 * s, 0.83 * s, hz * 0.9], [0.14 * s * T, 0.19 * s, 0.085 * s * T], rot=[0, 0, -12], bone="legHLu", k=K(0.05), color=B, mirror=True)
S.ell("stifle", [hx + 0.12 * s, 0.8 * s, hz * 0.9], [0.06 * s * T, 0.075 * s, 0.055 * s * T], rot=[0, 0, -15], bone="legHLu", k=K(0.04), color=B, mirror=True)
S.cone("gaskin", [hx + 0.05 * s, 0.7 * s, hz], [hx - 0.03 * s, hk + 0.035 * s, hz], (0.075 if CV else 0.065) * s * T, (0.034 if CV else 0.03) * s * T, bone="legHLu", k=K(0.03), color="@upleg", mirror=True)
# (the hamstrings: the back of the thigh straight from the point of the buttock down to the point of the hock)
ham(S, J, [0.3, 1.0], [0.09, 0.25], 0.085 * s * T, 0.03 * s * T, B, K(0.05), zf=0.85)
S.ell("hock", [hx - 0.02 * s, hk - 0.005 * s, hz], [0.035 * s * T, 0.036 * s, 0.026 * s * T], bone="legHLl", k=K(0.015), color=LG, mirror=True)
S.sph("hockPt", [hx - 0.055 * s, hk + 0.025 * s, hz], 0.022 * s * T, bone="legHLl", k=K(0.015), color=LG, mirror=True)
S.cone("hcannon", [hx - 0.018 * s, hk - 0.03 * s, hz], [hx, fl + 0.01 * s, hz], 0.022 * s * T * CT, 0.019 * s * T * CT, bone="legHLl", k=K(0.012), color=LG, mirror=True)
S.cone("htendon", [hx - 0.04 * s, hk - 0.05 * s, hz], [hx - 0.014 * s, fl + 0.02 * s, hz], 0.012 * s * T, 0.013 * s * T, bone="legHLl", k=K(0.01), color=LG, mirror=True)
S.ell("hfetlock", [hx, fl, hz], [0.027 * s * T * CT, 0.027 * s * CT, 0.024 * s * T * CT], bone="legHLl", k=K(0.012), color=LG, mirror=True)
S.cone("hpastern", [hx, fl - 0.01 * s, hz], [hx + 0.022 * s, 0.055 * s, hz], 0.02 * s * T * CT, 0.02 * s * T * CT, bone="legHLl", k=K(0.01), color=LG, mirror=True)
# ---- each one's own
keep = []
cols = {}
extras = None
t0 = J["tail"]["o"]
a = math.radians(ang(nd)); nn = [math.sin(a), -math.cos(a), 0]; nu = mul(nn, -1)   # (below / above the neck's line)
HS, HJ = 0.7, [(0.92 + DH[0]) * s, (1.55 + DH[1]) * s, 0]   # (the frame's headScale and its neck joint, the centre it shrinks about: mammals.js pulls a head extra's ROOT onto the shrunk skull, hP)
def pill(id, a, b, r1, r2, color, mirror=True):   # a, b where the pill should END UP: its root un-shrunk so hP puts it back at a
    f = [HJ[i] + (a[i] - HJ[i]) / HS for i in range(3)]; t = add(f, sub(b, a))
    return {"id": id if id.startswith("ant") else "ant" + id, "parent": "head", "from": R3(f), "to": R3(t), "r1": round(r1, 4), "r2": round(r2, 4), "color": color, **({"mirror": True} if mirror else {})}
def mixhex(a, b, t): return "#" + "".join(f"{round(int(a[1 + 2 * i:3 + 2 * i], 16) * (1 - t) + int(b[1 + 2 * i:3 + 2 * i], 16) * t):02x}" for i in range(3))
def tine(out, id, a, b, r1, r2, c, tipc, mirror=True):   # a tine: brown, paling over its last third to a polished point
    m1, m2 = lerp(a, b, 0.66), lerp(a, b, 0.86); r_1, r_2 = r1 + (r2 - r1) * 0.66, r1 + (r2 - r1) * 0.86
    out += [pill(id, a, m1, r1, r_1, c, mirror), pill(id + "m", m1, m2, r_1, r_2, mixhex(c, tipc, 0.5), mirror), pill(id + "t", m2, b, r_2, r2 * 0.6, tipc, mirror)]
def fan(out, id, a, tips, r1, r2, c, tipc, mirror=True):   # a palm: tines fanned close in one plane, read as a plate
    for k, b in enumerate(tips): tine(out, f"{id}{k}", a, b, r1, r2, c, tipc, mirror)
CELL = {"deer": 0.0175, "reindeer": 0.0199, "cervicapra": 0.0118, "impala": 0.0122, "chamois": 0.0112, "oryx": 0.0199}[name]   # (the body's grid, t_all: what the field can draw)
def TINE(id, a, b, r1, r2, c, tipc, par="beam", mirror=True, mid=None):   # a tine: ONE path out of its parent, paling over its last third
    horn(S, id, [list(a) + [r1], list(lerp(a, b, 0.5)) + [(r1 + r2) / 2], list(b) + [r2]], c, CELL, k=K(0.004),
         fade=(0.45, tipc), mirror=mirror, parent=par)   # (round 7: the point pales in one smooth fade, no banded sheaths)
def FAN(id, a, tips, r1, r2, c, tipc, par, mirror=True):
    for k, b in enumerate(tips): TINE(f"{id}{k}", a, b, r1, r2, c, tipc, par, mirror)
def BEAM(id, pts, c, mirror=True): horn(S, id, [A(*p[:3]) + [p[3] * s] for p in pts], c, CELL, k=K(0.006), mirror=mirror)
AB = [HJ[i] + ([(0.9 + DH[0]) * s, (1.74 + DH[1]) * s, 0.06 * s][i] - HJ[i]) * HS for i in range(3)]   # (the antler's root, on the skull)
def A(x, y, z): return add(AB, [x * s, y * s, z * s])
def tailEll(id, d, r, col, **kw): S.ell(id, add(t0, [d[0] * s, d[1] * s, 0]), [r[0] * s, r[1] * s, r[2] * s], rot=[0, 0, kw.pop("rot", -15)], bone="tail", k=K(kw.pop("k", 0.02)), color=col, **kw)
if BB:
    cols = {"belly": "#cfae84", "throat": "#8a5a32", "patch": "#e6dcc8", "head": "#9a6a3a", "muzzle": "#7a5230", "nose": "#1c1612", "chin": "#e6dcc8", "gland": "#241a12", "earIn": "#a88878", "upleg": "#96643a", "ear": "#946234", "back": "#86562e", "tailc": "#5a3c24"}
    about = "THE RED DEER (2026-11-05, 2nd pass): a narrow chest under the withers, the barrel tucked up high on long legs, a round rump with its flat pale patch and the short dark tail on it; countershaded, the back and neck darker, the flank paler to the belly; a slim wedge of a head to a dark wet nose, a pale chin, the dark gland line before the lateral eye; long tapering ears; slender legs on cloven hooves; the antlers built here as tapered beams -- back, then up and forward -- with brow, bez and trez tines, a crown, ivory points"
    tailEll("tail", (-0.03, -0.06), (0.03, 0.075, 0.035), "@tailc", rot=-20)
    C, I = "#7e6c56", "#cfc2a8"
    # (the antlers: sculpted, one continuous path each -- beam, brow, bez, trez, crown -- every tine rooted INSIDE its beam)
    BEAM("beam", [(0, -0.02, -0.01, 0.038), (-0.1, 0.14, 0.09, 0.033), (-0.16, 0.3, 0.17, 0.028), (-0.14, 0.46, 0.235, 0.024), (-0.08, 0.6, 0.265, 0.02)], C)
    TINE("crownB", A(-0.08, 0.59, 0.265), A(0.0, 0.74, 0.25), 0.017 * s, 0.004 * s, C, I)
    TINE("crownA", A(-0.09, 0.57, 0.262), A(-0.16, 0.73, 0.32), 0.014 * s, 0.004 * s, C, I)
    TINE("crownC", A(-0.12, 0.51, 0.25), A(-0.05, 0.69, 0.36), 0.014 * s, 0.004 * s, C, I)
    TINE("brow", A(-0.02, 0.05, 0.03), A(0.2, 0.19, 0.07), 0.018 * s, 0.005 * s, C, I)
    TINE("bez", A(-0.06, 0.1, 0.065), A(0.15, 0.22, 0.11), 0.016 * s, 0.005 * s, C, I)
    TINE("trez", A(-0.155, 0.29, 0.165), A(0.03, 0.42, 0.19), 0.015 * s, 0.004 * s, C, I)
    X = []
    extras = X
elif RD:
    cols = {"belly": "#ddd5c5", "throat": "#e4dccc", "patch": "#e0d8c8", "head": "#7a6854", "muzzle": "#a89884", "nose": "#4a3c30", "chin": "#d8d0c0", "gland": "#3a2e24", "earIn": "#8a7a68", "upleg": "#665646", "ear": "#6a5a48", "ruff": "#ece6d8", "neckc": "#b4a690", "back": "#6a5a48", "band": "#4a3c30", "sock": "#a89c88", "tailc": "#e8e2d4"}
    about = "THE REINDEER (2026-11-05, 2nd pass): the deer's plan at half again its mass -- broader, on sturdier legs and broad splayed hooves with dewclaws, a pale ring above them; grey-brown, a dark band along the lower flank over the pale belly, the neck pale with a cream mane hanging from the throat; a blunt furry muzzle, short pointed ears; the antlers built here: beams swept BACK and then forward in a C, palmate at the top, one shovel (the palmate brow tine) forward over the face, bez tines with their own small palms"
    tailEll("tail", (-0.03, -0.05), (0.035, 0.06, 0.04), "@tailc", rot=-20)
    for i, (t, d, r) in enumerate(((0.12, 0.1, (0.11, 0.11, 0.09)), (0.38, 0.12, (0.1, 0.12, 0.08)), (0.62, 0.09, (0.08, 0.09, 0.065)))):
        S.ell(f"ruff{i}", add(add(lerp(nb, poll, t), nn, 0.115 * s * bk * NW * 0.95), [0, -d * s * 0.9, 0]), [r[0] * s * 0.7, r[1] * s * 1.35, r[2] * s * bk * 0.75], rot=[0, 0, -12], bone="neck", k=K(0.05), kc=K(0.03), color="@ruff", hair=0.8)
    S.ell("band", P(-0.08, 0.95), r3(0.5, 0.06, 0.2), rot=[0, 0, -4], k=K(0.025), kc=K(0.03), color="@band")
    C, I = "#a89474", "#d2c6ac"
    # (round 7b) the beam: ONE smooth field tube -- from the pedicle back and OUT, up, and over its top third forward; from
    # the front a wide lyre (tops ~1 m apart, leaning a little in). At its top a FLAT blade in the beam's plane (two thin
    # flattened ells, 3.4 cm thick, smooth-unioned into the beam: a ragged hand, no slab) with 5 tines of varied length off
    # its edge; one short back tine mid-beam; the bez forward over the face with its own small palm; ONE brow shovel, a
    # thin narrow vertical leaf over the nose; every point a smooth taper to a rounded ~0.8 cm end, paling at the tip
    BEAM("beam", [(0, -0.02, -0.01, 0.037), (-0.14, 0.1, 0.16, 0.034), (-0.3, 0.28, 0.32, 0.031), (-0.36, 0.48, 0.42, 0.029), (-0.3, 0.66, 0.48, 0.027), (-0.17, 0.8, 0.49, 0.026), (-0.02, 0.88, 0.46, 0.025)], C)
    PT = 0.0085 / s   # (a point's rounded end)
    def lean(x, y, z0=0.455, y0=0.92): return A(x, y, z0 - 0.25 * (y - y0))   # (the palm's plane: leaning in ~14 deg)
    S.ell("palm", lean(0.03, 0.95), [0.14 * s, 0.075 * s, 0.017], rot=[-14, 0, 24], bone="head", k=K(0.03), color=C, mirror=True)
    S.ell("palm2", lean(-0.05, 0.97), [0.08 * s, 0.07 * s, 0.017], rot=[-14, 0, -10], bone="head", k=K(0.03), color=C, mirror=True)
    for k2, (x0, y0, x1, y1) in enumerate(((0.13, 0.98, 0.31, 1.02), (0.09, 1.0, 0.2, 1.16), (0.0, 1.0, 0.03, 1.24), (-0.08, 1.0, -0.15, 1.12), (-0.11, 0.95, -0.2, 0.99))):
        m = lean((x0 + x1) / 2 + 0.01, (y0 + y1) / 2)
        horn(S, f"palmPt{k2}", [lean(x0, y0) + [0.024 * s], m + [0.016 * s], lean(x1, y1) + [PT * s]], C, CELL, k=K(0.006), fade=(0.5, I))
    TINE("back", A(-0.36, 0.46, 0.42), A(-0.48, 0.52, 0.44), 0.02 * s, PT * s, C, I)
    horn(S, "bez", [A(-0.1, 0.08, 0.12) + [0.026 * s], A(-0.01, 0.16, 0.15) + [0.025 * s], A(0.08, 0.22, 0.16) + [0.024 * s]], C, CELL, k=K(0.004), parent="beam")
    S.ell("bezPalm", A(0.12, 0.24, 0.16), [0.065 * s, 0.04 * s, 0.017], rot=[0, -8, 15], bone="head", k=K(0.02), color=C, mirror=True)
    for k2, (a1, b1) in enumerate(((0.24, 0.31), (0.23, 0.2))):
        horn(S, f"bezP{k2}", [A(0.15, (0.26 + b1) / 2 + 0.0, 0.16) + [0.022 * s], A((0.15 + a1) / 2, (0.25 + b1) / 2, 0.162) + [0.015 * s], A(a1, b1, 0.164) + [PT * s]], C, CELL, k=K(0.006), fade=(0.5, I))
    # the shovel (one side only): a stem off the beam's root, in to the midline and forward, then a thin narrow leaf down over the nose
    horn(S, "shovel", [A(0.0, 0.0, -0.005) + [0.025 * s], A(0.06, 0.04, -0.025) + [0.024 * s], A(0.12, 0.04, -0.045) + [0.023 * s]], C, CELL, k=K(0.006), mirror=False)
    S.ell("shovelLeaf", A(0.2, 0.0, -0.055), [0.11 * s, 0.045 * s, 0.017], rot=[0, 0, -28], bone="head", k=K(0.025), color=C)
    for k2, (x0, y0, x1, y1) in enumerate(((0.27, 0.0, 0.33, 0.0), (0.26, -0.05, 0.3, -0.1))):
        horn(S, f"shovelPt{k2}", [A(x0, y0, -0.055) + [0.022 * s], A((x0 + x1) / 2, (y0 + y1) / 2, -0.055) + [0.015 * s], A(x1, y1, -0.055) + [PT * s]], C, CELL, k=K(0.006), fade=(0.5, I), mirror=False)
    TINE("browR", A(0.0, 0.03, -2 * AB[2] / s + 0.005), A(0.13, 0.08, -2 * AB[2] / s - 0.01), 0.016 * s, PT * s, C, I, par=None, mirror=False)
    X = []
    extras = X
if True:   # THE CHAMOIS
    cols = {"body": "#94683e", "front": "#94683e", "neck": "#8a5e36", "back": "#6a4628", "belly": "#cdb08a", "throat": "#9a6c40", "throatW": "#efe8d8", "patch": "#dccbac",
            "head": "#ebe2cf", "muzzle": "#e6dcc8", "nose": "#1e1614", "chin": "#efe8d8", "gland": "#ebe2cf", "earIn": "#ece2d0", "ear": "#7e5634",
            "earTip": "#2a1e16", "upleg": "#3a281a", "leg": "#2a1e16", "foot": "#1a1614", "tail": "#2a1e16", "tailc": "#2a1e16", "black": "#18120e",
            "hornc": "#16120f", "eye": "#2a1a10", "limb": "#5a3c24", "stripe": "#2e2016", "mask": "#1c1410"}
    about = ("THE CHAMOIS (Rupicapra rupicapra; 2026-11-06, gen: scratchpad sc/new6/chamois.py, the deer frame's cervid sculpt): a stocky, "
             "agile goat-antelope of 0.75 m at the shoulder on sturdy legs; a short face, white-cream, a black stripe from the base of "
             "the ear through the eye down to the corner of the mouth on each side; short black horns rising straight from the brow "
             "and hooking sharply back at the tips; brown (summer) to near black (winter), a dark stripe along the spine, the legs dark, "
             "a pale rump; a short dark tail; pale-lined pointed ears")
    tailEll("tail", (-0.024, -0.056), (0.024, 0.055, 0.024), "@tailc", rot=-20, k=0.02)   # (2026-11-08: onto the dock, blended softer)
    S.tube("tailDock", [add(t0, [dx * s, dy * s, 0]) + [r * s] for dx, dy, r in ((0.1643, 0.0186, 0.0429), (0.0571, -0.0071, 0.0343), (-0.0043, -0.0343, 0.0257))], bone="tail", k=K(0.02), color="@body", pat="coarse", hair=0.3)   # (2026-11-08: the DOCK, from inside the rump to the tail -- the tail stood off the rump by a ~1 cm gap)
    for q in S.shapes:
        if q["id"] in ("cranium", "jaw"): q["r"] = [x * (1.06 if i else 1.0) for i, x in enumerate(q["r"])]   # (a deeper, broader skull: the short goat face)
        if q["id"] == "face": q["ra"] *= 1.12; q["rb"] *= 1.18   # (round 2: a broader, blunter goat face)
        if q["id"] == "muzzle": q["r"] = [q["r"][0], q["r"][1] * 1.08, q["r"][2] * 1.15]
    # the face: cream chin and lips, a pale throat patch
    S.ell("lip", H(0.92, -0.12), [0.1 * L, 0.065 * L, 0.09 * L], rot=hr, bone="head", k=K(0.015), kc=K(0.006), color="@chin")
    S.ell("chinW", H(0.72, -0.19), [0.16 * L, 0.05 * L, 0.07 * L], rot=hr, bone="head", k=K(0.015), kc=K(0.006), color="@chin")
    # (no pale patch on the neck: the throat is pale only under the jaw)
    S.ell("throatW2", H(0.3, -0.24), [0.1 * L, 0.05 * L, 0.08 * L], rot=hf.rot(30), bone="head", k=K(0.01), kc=0.004, color="@throatW")
    # THE MASK: a black band each side from below the ear, through the eye, down the side of the face to the mouth's corner
    #  (laid ON the measured skin of the head, a tube a little proud, its edge soft)
    mq = [(0.12, 0.085, 0.012), (0.22, 0.085, 0.018), (0.34, 0.075, 0.021), (0.48, 0.03, 0.019), (0.62, -0.01, 0.017), (0.76, -0.05, 0.015), (0.86, -0.08, 0.013)]
    hs = surf(S, [{"x": H(t, h)[0], "y": H(t, h)[1], "z0": 0, "dir": [0, 1]} for t, h, r in mq])
    mk = [H(t, h)[:2] + [q["t"] - r + 0.0035, r] for (t, h, r), q in zip(mq, hs) if q["t"] is not None]
    S.tube("mask", mk, bone="head", k=K(0.004), kc=0.002, color="@mask", mirror=True)
    for q in S.shapes:
        if q["id"] in ("withers", "loin", "neckBase"): q["color"] = B
        if q["id"] in ("arm", "thigh", "stifle"): q["color"] = "@limb"
        if q["id"] == "earTip":
            ear = next(e for e in S.shapes if e["id"] == "ear")
            q["color"] = "@earTip"; q["kc"] = 0.005; q["r"] = [ear["r"][0] * 1.02, q["r"][1] * 0.8, q["r"][2] * 0.8]
    # the dark DORSAL STRIPE: on the measured topline, withers to tail
    xd = [0.36 - 0.06 * i for i in range(18)]
    hs = surf(S, [{"x": x, "y": 1.0, "z0": 0, "dir": [1, 0]} for x in xd])
    S.tube("dorsal", [[x, 1.0 + h["t"] - 0.03 + 0.008, 0, 0.03] for x, h in zip(xd, hs) if h["t"] is not None], k=K(0.012), kc=0.006, color="@stripe")
    # THE HORNS: from the brow just above and in front of the eyes, rising straight and nearly parallel, then hooking
    #  sharply BACK at the tips; black, slim (2.4 cm at the base), ~17 cm along the curve
    root = H(0.3, 0.11, 0.045)
    HP = [[0, -0.01, 0, 0.0125], [0.004, 0.05, 0.004, 0.0115], [0.004, 0.095, 0.007, 0.0098], [-0.006, 0.13, 0.009, 0.0082],
          [-0.03, 0.148, 0.009, 0.0064], [-0.055, 0.138, 0.008, 0.0048], [-0.066, 0.115, 0.007, 0.0032]]
    horn(S, "horn", [add(root, p[:3]) + [p[3]] for p in HP], "@hornc", CELL, k=K(0.004))
    # GOAT HOOVES: blocky, the two toes splayed a little (TS, HW above); a dewclaw pair behind each fetlock
    for f, (xx, zz) in (("F", (fx, fz)), ("H", (hx, hz))):
        S.ell("dew" + f, [xx - 0.03 * s, 0.07 * s, zz], [0.016 * s, 0.013 * s, 0.026 * s], rot=[0, 0, 30], bone="legFLl" if f == "F" else "legHLl", k=K(0.006), kc=0.002, color="@foot", mirror=True)
    # FUR: coarse hair over the coat (no smooth hide)
    for q in S.shapes:
        if q.get("color") in (B, "@back", "@limb", "@upleg", "@leg", "@throat", "@belly", "@stripe", "@patch") and q.get("op") is None: q["pat"] = "coarse"; q["hair"] = 0.3
    extras = []
sc = {"_about": about, "keep": keep, "mesh": {"tris": [7400, 2300], "cell": 0.009, "focus": {"head": 4}}, "shape": S.shapes,
      "shade": {"on": B, "back": "@back", "belly": B, "low": "@belly", "mode": "mix", "tol": 0.05, "k": 0.02,
                "at": round(0.64 - J["body"]["o"][1], 3), "lowAt": round(0.5 - J["body"]["o"][1], 3)},
      "eyes": {"at": R3(eye), "from": R3(H(0.42, 0.02, 0)), "r": round(0.013 * s, 4), "iris": "@eye", "pupil": "bar", "lid": "@nose", "sink": 0.45}}
legs = {"front": [f"{J['legFLu']['o'][0] / s:.3f}*s", f"{J['legFLu']['o'][1] / s:.3f}*s", f"{CFG['lz']}*s", None], "hind": [f"{J['legHLu']['o'][0] / s:.3f}*s", f"{J['legHLu']['o'][1] / s:.3f}*s", f"{CFG['hz']}*s", None]}
legs["front"][3] = f"{J['legFLu']['o'][1] / s - EL:.3f}*s"; legs["hind"][3] = "0.400*s"
upd = {"colors": cols, "legs": legs, "!extras": extras, "print": "cloven", "shy": 16,
       "coats": [{}, {"name": "winter", "colors": {"body": "#3e2e22", "front": "#3e2e22", "neck": "#3a2a1e", "back": "#2a1e16", "belly": "#5e4c3a",
                                                   "limb": "#30241a", "upleg": "#2a1e16", "leg": "#221a14", "ear": "#3a2a1e", "patch": "#c8b89c", "stripe": "#18120e"}}],
       "variants": {"winter": {"colors": {"body": "#3e2e22", "front": "#3e2e22", "neck": "#3a2a1e", "back": "#2a1e16", "belly": "#5e4c3a",
                                          "limb": "#30241a", "upleg": "#2a1e16", "leg": "#221a14", "ear": "#3a2a1e", "patch": "#c8b89c", "stripe": "#18120e"}},
                    "kid": {"scale": 0.6}}}
print("horn paths ok:", check_horns())
# ---- LOWERED on shorter legs (round 2): everything above the elbow (YT) down by DROP, the legs between the fetlock (YB)
#      and the elbow drawn in to fit -- the hooves untouched on the ground; the rig dropped to match
DROP, YT, YB = 0.12 * s, 0.72 * s, 0.15 * s
def ym(y): return y - DROP if y >= YT else (y if y <= YB else YB + (y - YB) * (YT - DROP - YB) / (YT - YB))
def mp(p): return [p[0], ym(p[1])] + list(p[2:])
for q in S.shapes:
    for kk in ("c", "a", "b"):
        if isinstance(q.get(kk), list) and len(q[kk]) >= 3: q[kk] = R3(mp(q[kk]))
    if "pts" in q: q["pts"] = [R3(mp(p[:3])) + list(p[3:]) for p in q["pts"]]
sc["eyes"]["at"] = R3(mp(sc["eyes"]["at"])); sc["eyes"]["from"] = R3(mp(sc["eyes"]["from"]))
dy = -DROP / s
RGd = {"neck": mvp(RG["neck"], (0, 3), 0, dy), "head": mvp(RG["head"], (0,), 0, dy), "muzzle": mvp(RG["muzzle"], (0, 3), 0, dy),
       "nose": mvp(RG["nose"], (0,), 0, dy), "ears": mvp(RG["ears"], (0, 3), 0, dy), "eyes": mvp(RG["eyes"], (0,), 0, dy),
       "rear": mvp(RG["rear"], (0,), 0, dy), "front": mvp(RG["front"], (0,), 0, dy)}
hip, hk = J["legHLu"]["o"][1], J["legHLl"]["o"][1]
legs["front"][1] = cs(legs["front"][1], dy); legs["hind"][1] = cs(legs["hind"][1], dy)
legs["hind"][3] = f"{0.4 * (hip - DROP - ym(hk)) / (hip - hk):.3f}*s"
upd.update(RGd); upd["params"] = {"s": s, "bulk": bk}; upd["tail"] = {**tl, "c": [tl["c"][0], cs(tl["c"][1], dy)]}
print(write(name, sc, upd), len(S.shapes), "shapes")
