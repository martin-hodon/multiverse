# cervid.py deer|reindeer|cervicapra|oryx -- the deer frame's sculpts, written from the rig's joints
import sys
from lib import *
from lib import _cr
name = "impala"; IMP = True
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
HB = {"deer": 0.1, "reindeer": 0.1, "cervicapra": 0.07, "impala": 0.07, "oryx": 0.09}[name]
PI = {"deer": 0.04, "reindeer": 0.06, "cervicapra": 0.05, "impala": 0.05, "oryx": 0.06}[name]
FRM = json.load(open(ROOT + "assets/creatures/frames/deer.json"))
pre = json.load(open(ROOT + f"assets/creatures/mammals/{name}.json"))
BASE = {"deer": -0.62, "reindeer": -0.42, "cervicapra": -0.42, "impala": -0.42, "oryx": -0.477}[name]
TB = float(FRM["tail"]["c"][0].split("*")[0]) - (0.2 if name == "deer" else 0)
lg = pre["legs"]; lg["hind"] = [f"{BASE - HB:.3f}*s"] + lg["hind"][1:]
tl = {**FRM["tail"], "c": [f"{TB + PI:.3f}*s", FRM["tail"]["c"][1]]}
if pre["legs"] != lg or pre.get("tail") != tl:
    pre["legs"] = lg; pre["tail"] = tl; json.dump(pre, open(ROOT + f"assets/creatures/mammals/{name}.json", "w"), indent=2, ensure_ascii=False)
J = joints(name)
CFG = {
    "deer":       dict(s=1.0, bulk=1.0, by=1.0, lz=0.13, hz=0.14, up=0.0, T=1.0),
    "reindeer":   dict(s=0.95, bulk=1.25, by=1.08, lz=0.15, hz=0.16, up=0.0, T=1.3),
    "cervicapra": dict(s=0.7, bulk=0.9, by=0.88, lz=0.13, hz=0.14, up=0.04, T=0.95),
    "impala": dict(s=0.74, bulk=0.88, by=0.9, lz=0.13, hz=0.14, up=0.04, T=0.92),
    "oryx":       dict(s=0.95, bulk=1.2, by=1.0, lz=0.14, hz=0.15, up=0.02, T=1.15),
}[name]
s, bk, by, UP = CFG["s"], CFG["bulk"], CFG["by"], CFG["up"]
RD, BB, BL, CV, OX = name == "reindeer", name == "deer", None, name in ("cervicapra", "impala"), name == "oryx"
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
NW = {"deer": 1.0, "reindeer": 1.1, "cervicapra": 1.4, "impala": 1.4, "oryx": 1.4}[name]
S.ell("neckBase", nb, r3(0.24, 0.25, 0.17) if name == "impala" else r3(0.22, 0.19 * min(NW, 1.2), 0.14 * min(NW, 1.25)), rot=[0, 0, 45 if name == "impala" else 50], k=K(0.08), color="@neckc" if RD else "@back")
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
EAR = {"deer": (0.24, 0.045, [-0.15, 0.75, 0.65]), "reindeer": (0.15, 0.04, [-0.2, 0.7, 0.7]), "cervicapra": (0.17, 0.034, [-0.1, 0.65, 0.75]), "impala": (0.21, 0.042, [-0.2, 0.5, 0.85]), "oryx": (0.17, 0.05, [-0.2, 0.8, 0.55])}[name]
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
CT = 1.4 if RD else 1.0     # (a reindeer's cannons: stout)
TS = 1.4 if RD else 1.0     # (...and its crescent hooves: huge, splayed)
S.ell("arm", [fx + 0.0 * s, 0.77 * s, fz * 0.8], [0.09 * s * T, 0.13 * s, 0.065 * s * T], rot=[0, 0, -22], bone="legFLu", k=K(0.05), color=B, mirror=True)
S.cone("forearm", [fx - 0.02 * s, 0.7 * s, fz], [fx, kn + 0.02 * s, fz], 0.05 * s * T, 0.028 * s * T, bone="legFLl", k=K(0.03), color="@upleg", mirror=True)
S.ell("knee", [fx + 0.003 * s, kn - 0.01 * s, fz], [0.03 * s * T, 0.033 * s, 0.027 * s * T], bone="legFLl", k=K(0.015), color=LG, mirror=True)
S.cone("cannon", [fx, kn - 0.03 * s, fz], [fx + 0.004 * s, fl + 0.01 * s, fz], 0.02 * s * T * CT, 0.018 * s * T * CT, bone="legFLl", k=K(0.012), color=LG, mirror=True)
S.cone("tendon", [fx - 0.016 * s, kn - 0.05 * s, fz], [fx - 0.012 * s, fl + 0.02 * s, fz], 0.012 * s * T, 0.013 * s * T, bone="legFLl", k=K(0.01), color=LG, mirror=True)
S.ell("fetlock", [fx, fl, fz], [0.027 * s * T * CT, 0.027 * s * CT, 0.024 * s * T * CT], bone="legFLl", k=K(0.012), color=LG, mirror=True)
S.cone("pastern", [fx, fl - 0.01 * s, fz], [fx + 0.022 * s, 0.055 * s, fz], 0.02 * s * T * CT, 0.02 * s * T * CT, bone="legFLl", k=K(0.01), color=LG, mirror=True)
HW = 1.9 if RD else 1.0     # (a reindeer's hooves are broad: snowshoes)
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
CELL = {"deer": 0.0175, "reindeer": 0.0199, "cervicapra": 0.0118, "impala": 0.0122, "oryx": 0.0199}[name]   # (the body's grid, t_all: what the field can draw)
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
elif IMP:
    keep += []
    cols = {"body": "#c99a68", "front": "#c99a68", "neck": "#b47a48", "back": "#8a4a28", "belly": "#f2ede4", "throat": "#b8784a", "throatW": "#f2ede4", "patch": "#f2ede4",
            "head": "#9a5a34", "muzzle": "#8a5232", "nose": "#1e1614", "chin": "#f2ede4", "gland": "#9a5a34", "earIn": "#ece2d4", "ear": "#a8683e",
            "earTip": "#141010", "upleg": "#b47c4c", "leg": "#b98552", "foot": "#1e1a18", "tail": "#f2ede4", "tailc": "#f2ede4", "black": "#141110",
            "hornc": "#3a3430", "brow": "#efe6d8", "eye": "#241812", "limb": "#c2915e"}
    about = ("THE IMPALA (2026-11-05, gen: scratchpad sc/new6/impala_base.py, the deer frame's cervid sculpt): a slender, leggy antelope "
             "of 0.9 m at the withers, the neck of moderate length carried at ~45 degrees -- three tones in level bands: a red-brown "
             "saddle over the back and upper flank, a fawn band along the lower flank, the belly white (the countershade's three "
             "levels); a white chin, lips and throat patch, a white brow over each eye; black-tipped ears; from behind a white rump "
             "between two black vertical stripes down the buttocks, a white tail with a black line along its top; black tufts on the "
             "back of the hind fetlocks; the ram's lyre-shaped horns -- up and back from the brow, out, then up and the points forward "
             "-- thick at the base and tapering hard, irregularly ringed for two thirds of their length (the `ridges` coat), smooth "
             "to the points, rooted on the skull above and behind the eyes")
    # tail: white and bushy, a bold black line along its top (its REAR face as it hangs)
    tailEll("tail", (-0.03, -0.08), (0.032, 0.1, 0.03), "@tailc", rot=-20, k=0.02, hair=0.6)
    tailEll("tailStripe", (-0.05, -0.07), (0.014, 0.1, 0.019), "@black", rot=-20, k=0.004, kc=0.002)
    # (the white belly: the countershade's lowest band -- the coat's colour under lowAt -- not a strip of paint shapes)
    # the face: a white chin and lips, a white patch on the throat behind the jaw
    S.ell("lip", H(0.92, -0.12), [0.1 * L, 0.06 * L, 0.085 * L], rot=hr, bone="head", k=K(0.015), kc=K(0.006), color="@chin")
    S.ell("chinW", H(0.72, -0.19), [0.16 * L, 0.05 * L, 0.07 * L], rot=hr, bone="head", k=K(0.015), kc=K(0.006), color="@chin")
    S.ell("throatW", add(lerp(nb, poll, 0.84), nn, 0.115 * s * bk * NW * 0.62), [0.06 * s, 0.045 * s, 0.06 * s], rot=[0, 0, ang(nd)], bone="neck", k=K(0.006), kc=0.004, color="@throatW")
    S.ell("throatW2", H(0.3, -0.24), [0.1 * L, 0.05 * L, 0.08 * L], rot=hf.rot(30), bone="head", k=K(0.01), kc=0.004, color="@throatW")
    # the white brow: a crescent over the eye -- a flat ell just under the skin above it, so only a thin cap breaks through
    eo = norm(sub(eye, H(0.34, 0.0, 0)))
    S.ell("browW", add(add(eye, eo, -0.006), hf.n, 0.011), [0.019, 0.007, 0.012], rot=hf.rot(-8), bone="head", k=0.004, kc=0.002, color="@brow", mirror=True)
    for q in S.shapes:
        if q["id"] in ("withers", "loin", "neckBase"): q["color"] = B   # (one coat: the shade alone draws the bands)
        if q["id"] in ("arm", "thigh", "stifle"): q["color"] = "@limb"   # (fawn, but outside the shade's tolerance: no white band across the legs)
        if q["id"] == "earTip":   # (the black tip: the last quarter of the ear, inside its own outline)
            ear = next(e for e in S.shapes if e["id"] == "ear")
            q["color"] = "@earTip"; q["kc"] = 0.005; q["r"] = [ear["r"][0] * 1.02, q["r"][1] * 0.95, q["r"][2] * 0.95]
        if q["id"] == "rumpPatch": q["color"] = B   # (no pale disc on the croup: the impala's white is under the tail)
    # black tufts on the back of the hind fetlocks (the metatarsal glands)
    S.ell("tuft", [hx - 0.03 * s, fl + 0.07 * s, hz], [0.02 * s, 0.045 * s, 0.017 * s], rot=[0, 0, 8], bone="legHLl", k=K(0.008), kc=0.003, color="@black", hair=1, mirror=True)
    # the rump from behind: a white patch under the tail between two black vertical stripes down the buttocks
    hq = next(q for q in S.shapes if q["id"] == "haunch")
    def hcopy(id, dx, dy, dz, fy, fz, col, k=0.01):
        c, r = hq["c"], hq["r"]
        S.ell(id, [c[0] + dx, c[1] + dy, c[2] + dz], [r[0], r[1] * fy, r[2] * fz], rot=hq.get("rot"), k=k, kc=0.002, color=col, mirror=True)
    # (laid ON the rear skin, measured: a ray back from inside the rump at each height finds it -- a black stripe down
    #  each buttock, the white between them under the tail; the backs of the thighs the fawn limb colour, no white)
    for q in S.shapes:
        if q["id"].startswith("ham"): q["color"] = "@limb"
    def rear(id, z, ys, r, proud, col, mirror):
        hs = surf(S, [{"x": -0.45, "y": y, "z0": z, "dir": [-1, 0, 0]} for y in ys])
        pts = [[-0.45 - h["t"] + r - proud, y, z, r] for y, h in zip(ys, hs) if h["t"]]
        S.tube(id, pts, k=0.006, kc=0.003, color=col, mirror=mirror)
    ys = [0.79 - 0.03 * i for i in range(7)]
    rear("rumpW", 0.024, ys[1:-1], 0.022, 0.006, "@patch", True)
    rear("rumpB", 0.05, ys, 0.012, 0.0045, "@black", True)
    # the horns: a LYRE -- from the skull just above and behind the eyes up and back, swinging out, then up, the points
    # turning forward and a little in; thick at the base and tapering hard; ringed (34 ridges -- irregular -- one frame
    # per stretch, its origin set back by the length before it so the rings run on) for two thirds, smooth to the points
    root = H(0.25, 0.115, 0.065)
    HP = [[0, 0, 0, 0.0235], [-0.06, 0.075, 0.032, 0.0215], [-0.105, 0.16, 0.088, 0.0185], [-0.118, 0.25, 0.132, 0.0155],
          [-0.095, 0.33, 0.14, 0.0118], [-0.045, 0.39, 0.118, 0.008], [0.005, 0.425, 0.095, 0.0045]]
    HP = [add(root, p[:3]) + [p[3]] for p in HP]
    D = _cr(HP, per=3)
    cut = next(i for i, q in enumerate(D) if math.dist(q[:3], HP[4][:3]) < 1e-6)   # (ringed to the fifth knot: two thirds of its length)
    cum = 0.0
    for i in range(cut):
        a, b = D[i], D[i + 1]; u = norm(sub(b[:3], a[:3]))
        S.cone(f"horn{i}", a[:3], b[:3], a[3], b[3], bone="head", k=K(0.004), kc=0.003, color="@hornc", pat="ridges",
               frame={"o": R3(sub(a[:3], mul(u, cum))), "u": R3(u), "r": 0.0105}, mirror=True)
        cum += math.dist(a[:3], b[:3])
    horn(S, "hornTip", D[cut:], "@hornc", CELL, k=K(0.004))
    extras = []
elif CV:
    keep += ["horn.*"]
    cols = {"belly": "#f2ede4", "throat": "#3a2a22", "patch": "#f0ebe2", "head": "#3e2e24", "muzzle": "#f0ebe2", "nose": "#2a2220", "chin": "#f2ede4", "gland": "#120c0a", "earIn": "#8a7468", "upleg": "#2e221c", "ear": "#3a2a22", "ring": "#f4efe6", "back": "#241a16", "leg": "#3a2a22", "tailc": "#2a1e18"}
    about = "THE BLACKBUCK (2026-11-05, 2nd pass): a compact, leggy antelope on the deer frame -- the back and flanks near black, the white underparts wrapping from between the forelegs along the belly and up the inside of the legs, a clean edge low on the flank; a thick short neck; a bold white ring round the eye, a white lip and chin; narrow ears; the spiralled horns kept"
    tailEll("tail", (-0.03, -0.06), (0.03, 0.07, 0.03), "@tailc", rot=-20)
    # inside of the legs: white strips just proud of the inner skin
    S.ell("innerF", [fx - 0.005 * s, (kn + 0.7 * s) / 2, fz - 0.038 * s * T], [0.04 * s, (0.7 * s - kn) / 2, 0.016 * s], bone="legFLl", k=K(0.006), kc=0.003, color="@belly", mirror=True)
    S.ell("innerH", [hx + 0.0 * s, (hk + 0.72 * s) / 2, hz - 0.045 * s * T], [0.055 * s, (0.72 * s - hk) / 2, 0.016 * s], rot=[0, 0, 12], bone="legHLu", k=K(0.006), kc=0.003, color="@belly", mirror=True)
    S.ell("innerFl", [fx, (kn + fl) / 2, fz - 0.015 * s * T], [0.012 * s, (kn - fl) / 2, 0.007 * s], bone="legFLl", k=K(0.004), kc=0.002, color="@belly", mirror=True)
    S.ell("innerHl", [hx - 0.01 * s, (hk + fl) / 2, hz - 0.016 * s * T], [0.012 * s, (hk - fl) / 2, 0.007 * s], bone="legHLl", k=K(0.004), kc=0.002, color="@belly", mirror=True)
    S.ell("eyeRing", add(eye, mul(norm(sub(eye, H(0.34, 0.0, 0))), -0.004)), [0.02, 0.016, 0.012], rot=hr, bone="head", k=0.004, kc=0.002, color="@ring", mirror=True)
    S.ell("lip", H(0.9, -0.1), [0.12 * L, 0.08 * L, 0.095 * L], rot=hr, bone="head", k=K(0.015), kc=K(0.006), color="@belly")
    S.ell("chinW", H(0.72, -0.19), [0.16 * L, 0.05 * L, 0.07 * L], rot=hr, bone="head", k=K(0.015), kc=K(0.006), color="@belly")
elif OX:
    keep += ["horn.*"]
    cols = {"belly": "#f2eee6", "throat": "#2a2420", "patch": "#c8b8a0", "head": "#f0ebe2", "muzzle": "#f0ebe2", "nose": "#1e1a18", "chin": "#f0ebe2", "gland": "#1e1a18", "earIn": "#e8e0d4", "upleg": "#ece6dc", "ear": "#c8b8a0", "black": "#1e1916", "white": "#f2eee6", "back": "#beae96", "leg": "#ece6dc"}
    about = "THE GEMSBOK (2026-11-05, 2nd pass): a stocky antelope on the deer frame, a gemsbok's height (1.2 m) -- grey-fawn on a thick neck; the black: a broad band from the elbow along the lower flank over the white belly to the stifle and down the front of the thigh, a patch atop each foreleg, a line down the spine from the nape, a line down the throat, a patch on the thigh, garters high on the legs, white below with black knee patches; the white face boldly masked (a blaze from the horns to the nose, a stripe down through each eye to the cheek, a strap under the chin); broad rounded ears; the long straight horns and a long black tail to the hocks"
    BK = "@black"
    tailEll("tailDock", (-0.04, -0.08), (0.035, 0.1, 0.035), BK, rot=-30)
    tailEll("tailHair", (-0.09, -0.36), (0.05, 0.26, 0.035), BK, rot=-10, k=0.03, hair=0.9)
    # the flank band: a broad black band (~9 cm) from the elbow to the stifle, then down the front of the thigh -- sharp decals
    #   laid on the measured skin (both sides alike: mirrored)
    # (one tube on the measured skin, tapering and rounding off at both ends -- it stands less proud there, so it narrows --
    #  its edge soft)
    xb = [0.37 - 0.04 * i for i in range(20)]; yb = [0.858 + 0.03 * i / 19 for i in range(20)]
    hb = surf(S, [{"x": x, "y": y, "dir": [0, 1]} for x, y in zip(xb, yb)])
    def tp(i): u = min(i, 19 - i) / 4.5; return min(1, u) ** 0.6 if u < 1 else 1
    bp = []
    for i, (x, y, h) in enumerate(zip(xb, yb, hb)):
        if h["t"] is None: continue
        f = tp(i); hy = 0.12 * (0.5 + 0.5 * f); pr = 0.03 * (0.08 + 0.92 * f)
        bp.append([x, y, h["t"] - hy + pr, hy])
    S.tube("flankBand", bp, k=0.02, kc=0.012, color=BK, mirror=True)
    dl = [(f"thighF{i}", x, y, 0.12, [0, 1], 0.04, 0.05, BK, sp) for i, (x, y, sp) in enumerate(((-0.37, 0.87, 80), (-0.35, 0.81, 80), (-0.34, 0.75, 85), (-0.355, 0.69, 100)))]
    decals(S, dl, proud=0.02, k=0.022, kc=0.004, c=0.016, mirror=True)
    xd = [0.36 - 0.06 * i for i in range(18)]   # the dorsal stripe: ON the measured topline, withers to tail, ~4 cm wide
    hs = surf(S, [{"x": x, "y": 1.0, "z0": 0, "dir": [1, 0]} for x in xd])
    S.tube("dorsal", [[x, 1.0 + h["t"] - 0.045 + 0.012, 0, 0.045] for x, h in zip(xd, hs) if h["t"] is not None], k=K(0.012), kc=0.004, color=BK)
    nr = 0.115 * s * bk * NW
    S.ell("dorsalN", add(nm, nu, nr * 0.86), [length(nd) * 0.5, 0.03 * s, 0.03 * s], rot=[0, 0, ang(nd)], bone="neck", k=K(0.01), kc=K(0.004), color=BK)
    S.ell("throatStripe", add(lerp(nb, poll, 0.55), nn, nr * 0.95), [length(nd) * 0.42, 0.035 * s, 0.045 * s], rot=[0, 0, ang(nd)], bone="neck", k=K(0.01), kc=K(0.004), color=BK)
    S.ell("throatLow", add(lerp(nb, poll, 0.12), nn, nr * 1.15), [length(nd) * 0.25, 0.04 * s, 0.05 * s], rot=[0, 0, ang(nd) + 10], bone="neck", k=K(0.01), kc=K(0.004), color=BK)   # (down the throat to the brisket)
    S.cone("garterF", [fx - 0.012 * s, 0.73 * s, fz], [fx, 0.6 * s, fz], 0.052 * s * T, 0.045 * s * T, bone="legFLl", k=K(0.006), kc=0.003, color=BK, mirror=True)
    S.cone("garterH", [hx + 0.05 * s, 0.72 * s, hz], [hx + 0.0 * s, 0.58 * s, hz], 0.064 * s * T, 0.054 * s * T, bone="legHLu", k=K(0.006), kc=0.003, color=BK, mirror=True)
    S.tube("blaze", [H(0.1, 0.11) + [0.09 * L], H(0.45, 0.07) + [0.078 * L], H(0.75, 0.03) + [0.064 * L], H(0.97, -0.015) + [0.056 * L]], bone="head", k=K(0.006), kc=0.002, color=BK)
    S.ell("eyeStripe", H(0.4, -0.07, 0.15), [0.26 * L, 0.078 * L, 0.06 * L], rot=hf.rot(-58), bone="head", k=K(0.006), kc=0.002, color=BK, mirror=True)
    S.ell("strap", H(0.56, -0.2), [0.09 * L, 0.07 * L, 0.13 * L], rot=hf.rot(-55), bone="head", k=K(0.006), kc=0.002, color=BK)
    for p in S.shapes:   # the black patch at the top of the foreleg (meets the band), black knee patches on white legs
        if p["id"] == "arm": p["color"] = BK; p["kc"] = round(K(0.012), 4)
        if p["id"] == "knee": p["color"] = BK; p["kc"] = 0.004
    # the horns: long, straight, ringed at the base -- sculpted, one path each (the rig's pill lost its thin end to the grid)
    hf0 = [HJ[i] + ([0.93 * s, 1.76 * s, 0.046 * s][i] - HJ[i]) * HS for i in range(3)]; ht = add(hf0, [-0.38 * s, 0.86 * s, 0.074 * s])
    horn(S, "horn", [hf0 + [0.03 * s], lerp(hf0, ht, 0.35) + [0.024 * s], lerp(hf0, ht, 0.7) + [0.016 * s], ht + [0.004 * s]], "@hornc", CELL, k=K(0.006))
    for i in range(5): S.sph(f"hornRing{i}", lerp(hf0, ht, 0.06 + 0.06 * i) + [0], (0.031 - 0.0015 * i) * s, bone="head", k=0.004, kc=0.002, color="@hornc", mirror=True) if False else None
    cols["hornc"] = "#2a2420"
    extras = []
sc = {"_about": about, "keep": keep, "mesh": {"tris": [6800, 2200], "cell": 0.009}, "shape": S.shapes,
      # (a blackbuck's white: chest to groin and up the lower flank to one crisp level edge, the legs dark again below it)
      **({"shade": {"on": B, "back": "@back", "belly": B, "low": "@belly", "mode": "mix", "tol": 0.05, "k": 0.008,
                    "at": round(0.74 - J["body"]["o"][1], 3), "lowAt": round(0.655 - J["body"]["o"][1], 3)}} if IMP else
         {"shade": {"on": B, "back": B, "belly": "@belly", "low": B, "mode": "mix", "tol": 0.04, "k": 0.012,
                    "at": round(0.67 - J["body"]["o"][1], 3), "lowAt": round(0.585 - J["body"]["o"][1], 3)}} if CV else {}),
      "eyes": {"at": R3(eye), "from": R3(H(0.42, 0.02, 0)), "r": round(0.012 * s, 4), "iris": "@eye", "pupil": "bar", "lid": "@nose", "sink": 0.45}}
legs = {"front": [f"{J['legFLu']['o'][0] / s:.3f}*s", f"{J['legFLu']['o'][1] / s:.3f}*s", f"{CFG['lz']}*s", None], "hind": [f"{J['legHLu']['o'][0] / s:.3f}*s", f"{J['legHLu']['o'][1] / s:.3f}*s", f"{CFG['hz']}*s", None]}
FR = json.load(open(ROOT + "assets/creatures/frames/deer.json"))["legs"]
legs["front"][3] = f"{J['legFLu']['o'][1] / s - EL:.3f}*s"; legs["hind"][3] = "0.400*s" if name == "impala" else FR["hind"][3]   # (the impala: its hock higher, the cannon long -- 0.48 put it at 29% of the withers, a crouch)
upd = {"colors": cols, "legs": legs}
if extras is not None: upd["!extras"] = extras
if OX: upd["params"] = {"s": 0.95, "bulk": 1.15}; upd["mount"] = {"h": 1.76, "speed": 1.6}
print("horn paths ok:", check_horns())
print(write(name, sc, upd), len(S.shapes), "shapes")
