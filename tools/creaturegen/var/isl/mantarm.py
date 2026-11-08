#!/usr/bin/env python3
# mantarm.py IN.json OUT.json -- the manticore's wing ARM drawn (2026-11-08), after mantwing.py made its skin one membrane.
# Aloft the skin's leading edge runs straight from the shoulder S to the wrist W, but the arm under it was not there:
# the elbow (wForeL's origin) sat 16 cm behind that edge inside the skin, and the arm's three shapes (humerus,
# forearmW, wrist) were FIELD shapes on wArmL -- the forearm folded into the chest aloft, and on wForeL it dragged the
# body's own surface out to the wrist as a web. So:
#  - THE ELBOW onto the leading edge: wForeL's origin moved along wArmL's axis (aloft the wrist lies on that axis) to the
#    one point E that is as far from the wrist at rest as aloft (the forearm a rigid bone: E = t W, t solved), the
#    forearm turned the least to run E -> W in both poses, and wHandL turned back so that the hand -- and with it the
#    fingers and the whole skin -- stands exactly where it stood, at rest and spread;
#  - THE BONES as sharp `horn`s (sharp.js: details, never in the field, so the body's skin is not pulled after them):
#    the humerus on wArmL from inside the shoulder to just past the elbow, the forearm on wForeL from inside the
#    humerus's end to the wrist, tapering into finger 0 -- on the leading edge, the skin's rim along their middle;
#  - THE THUMB at the wrist a small hooked claw (a horn on wHandL, the bone's colour darkening to the claw's tip) in
#    place of the short fat dark cone that read as a knot at the wing's corner.
# The skin (wingSkin) rides wHandL, the fingers and wRootL only: with the hand's frames unchanged it is untouched.
import json, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/martin/store/apps/multiverse/"
REG = next(p for p in (HERE + "/../../reg.mjs", HERE + "/../reg.mjs") if os.path.exists(p))
inp, outp = sys.argv[1], sys.argv[2]
d = json.load(open(inp))
M4 = lambda e: np.array(e, float).reshape(4, 4).T
def probe(path):
    # (the wing beat stilled at rest too: at t = 0 the hand's own beat, phase .6, already has it turned 2.8 degrees)
    import tempfile
    q = json.load(open(path))
    for e in q["extras"]:
        r = e.get("raw", e)
        if isinstance(r, dict) and r.get("anim", {}).get("wing"): r["anim"] = {**r["anim"], "deg": 0}
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); json.dump(q, tmp); tmp.close()
    p = json.loads(subprocess.check_output(["node", "--import", REG, HERE + "/mantwing_probe.mjs", tmp.name], cwd=REPO)); os.unlink(tmp.name)
    bi = {b: i for i, b in enumerate(p["bones"])}
    return p, bi, [M4(m) for m in p["rest"]], [M4(m) for m in p["spread"]], [[M4(m) for m in f["M"]] for f in p["fly"]]
P0, bi, RS, SP, FL = probe(inp)
D = math.pi / 180
def Rx(a): c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def Ry(a): c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def Rz(a): c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def e2m(e): return Rx(e[0] * D) @ Ry(e[1] * D) @ Rz(e[2] * D)
def m2e(m):
    y = math.asin(max(-1, min(1, m[0, 2])))
    if abs(m[0, 2]) < 0.9999999: x = math.atan2(-m[1, 2], m[2, 2]); z = math.atan2(-m[0, 1], m[0, 0])
    else: x = math.atan2(m[2, 1], m[1, 1]); z = 0.0
    return np.array([x, y, z]) / D
def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v)
def rot_between(a, b):
    a, b = unit(a), unit(b); v = np.cross(a, b); c = float(a @ b)
    if c > 1 - 1e-12: return np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]); return np.eye(3) + K + K @ K / (1 + c)
def near(a, ref): return a + 360 * round((ref - a) / 360)   # (the turn a multiple of 360 from a nearest ref: the same way round)
raw = {e.get("raw", e)["id"]: e.get("raw", e) for e in d["extras"] if isinstance(e.get("raw", e), dict) and "id" in e.get("raw", e)}
A, F, H = bi["wArmL"], bi["wForeL"], bi["wHandL"]
loc = lambda M, a, b: np.linalg.inv(M[a]) @ M[b]                # (bone b in bone a's frame)
# ---- the elbow: E = t W in the arm's frame (aloft W is on its y axis), |W_rest - E| = |W_spread - E|
Wf, Wr = loc(SP, A, H)[:3, 3], loc(RS, A, H)[:3, 3]
assert np.linalg.norm(Wf[[0, 2]]) < 1e-3, f"the wrist aloft is off the arm's axis: {Wf}"
t = (Wf @ Wf - Wr @ Wr) / (2 * (Wf @ Wf - Wr @ Wf)); E = t * Wf
LF = float(np.linalg.norm(Wf - E))
print(f"elbow: t {t:.4f}, humerus {np.linalg.norm(E):.4f}, forearm {LF:.4f} (rest {np.linalg.norm(Wr - E):.4f})", file=sys.stderr)
# ---- the forearm's local turns (in the arm's frame), the least change from its old ones; the hand's to keep its frames
Ofr, Off = loc(RS, A, F)[:3, :3], loc(SP, A, F)[:3, :3]
Nfr = rot_between(Ofr[:, 1], Wr - E) @ Ofr; Nff = rot_between(Off[:, 1], Wf - E) @ Off
Hr, Hf = loc(RS, A, H)[:3, :3], loc(SP, A, H)[:3, :3]
Nhr, Nhf = Nfr.T @ Hr, Nff.T @ Hf
fo, ha = raw["wForeL"], raw["wHandL"]
er_f, ef_f = m2e(Nfr), m2e(Nff)
er_h, ef_h = m2e(Nhr), m2e(Nhf)
# (aloft: a plain part turns to rot + flyRot; a wing part's x is sg * FLIGHT.hand + flyRot[0] outright -- skeleton.js)
FH = {**{"hand": 8}, **(d.get("flight") or {})}["hand"]
new_fo = {"rot": [round(float(v), 4) for v in er_f]}
new_fo["flyRot"] = [round(float(near(ef_f[k] - er_f[k], fo["flyRot"][k])), 4) for k in range(3)]
new_ha = {"rot": [round(float(v), 4) for v in er_h]}
fx = ef_h[0] - FH
new_ha["flyRot"] = [round(float(near(fx, ha["flyRot"][0])), 4)] + [round(float(near(ef_h[k] - er_h[k], ha["flyRot"][k])), 4) for k in (1, 2)]
print("forearm", fo["rot"], fo["flyRot"], "->", new_fo, "\nhand", ha["rot"], ha["flyRot"], "->", new_ha, file=sys.stderr)
for e in d["extras"]:
    r = e.get("raw", e)
    if not isinstance(r, dict): continue
    sg = 1 if r.get("id", "").endswith("L") else -1
    mir = lambda v: [v[0] * sg, v[1] * sg, v[2]]
    if r.get("id") in ("wForeL", "wForeR"):
        r["pos"] = [0, round(float(E[1]), 4), 0]; r["size"] = {**r["size"], "len": round(LF, 4)}; r["pivot"] = [0, round(LF / 2, 4), 0]
        r["rot"] = mir(new_fo["rot"]); r["flyRot"] = mir(new_fo["flyRot"])
    if r.get("id") in ("wHandL", "wHandR"):
        r["pos"] = [0, round(LF, 4), 0]; r["rot"] = mir(new_ha["rot"]); r["flyRot"] = mir(new_ha["flyRot"])
# ---- the bones' shapes, in the rest pose's space (the shapes' own): E at rest, S, W
Sr = RS[A][:3, 3]; Er = (RS[A] @ np.append(E, 1))[:3]; Wr_w = RS[H][:3, 3]
up = RS[A][:3, 0]   # (the arm's x: forward, the leading side)
L3 = lambda v: [round(float(x), 4) for x in v]
hu = unit(Er - Sr); fa = unit(Wr_w - Er)
HUM = {"id": "humerus", "type": "horn", "bone": "wArmL", "color": "@wbone", "mirror": True, "sides": 10,
       "pts": [L3(Sr - .06 * hu) + [.05], L3(Sr + .02 * hu) + [.042], L3(Sr + .5 * (Er - Sr)) + [.03], L3(Er - .02 * hu) + [.033], L3(Er + .012 * hu) + [.03], L3(Er + .04 * hu) + [0]]}
FOR = {"id": "forearmW", "type": "horn", "bone": "wForeL", "color": "@wbone", "mirror": True, "sides": 10,
       "pts": [L3(Er - .015 * fa) + [.012], L3(Er + .01 * fa) + [.027], L3(Er + .06 * fa) + [.025], L3(Er + .5 * (Wr_w - Er)) + [.02], L3(Wr_w - .03 * fa) + [.022], L3(Wr_w) + [.021], L3(Wr_w + .03 * fa) + [0]]}
# the thumb: laid out aloft -- from inside the wrist forward (the arm's leading side), a little out along the span and
# down, hooked down at its point -- and carried back to the rest pose on the hand (its skinning map inverted)
fwd, dn = SP[A][:3, 0], SP[A][:3, 2]                              # (aloft: the arm's x forward, its z down)
dn = dn if dn[1] < 0 else -dn
Ws, span = SP[H][:3, 3], unit(SP[H][:3, 3] - SP[A][:3, 3])
ax = unit(fwd + .45 * span + .3 * dn); Lt = .1
Mh = RS[H] @ np.linalg.inv(SP[H]); toR = lambda p: (Mh @ np.append(p, 1))[:3]
TH = {"id": "thumb", "type": "horn", "bone": "wHandL", "color": "@wbone", "tip": "@stingTip", "tipAt": .35, "mirror": True, "sides": 8, "aspect": 1.3,
      "up": L3(Mh[:3, :3] @ -dn),
      "pts": [L3(toR(Ws - .012 * ax)) + [.017], L3(toR(Ws + .3 * Lt * ax)) + [.014], L3(toR(Ws + .65 * Lt * ax + .012 * dn)) + [.009], L3(toR(Ws + Lt * ax + .035 * dn)) + [0]]}
rep = {"humerus": HUM, "forearmW": FOR, "thumb": TH}
sh = [rep.get(q["id"], q) for q in d["sculpt"]["shape"] if q["id"] != "wrist"]
d["sculpt"]["shape"] = sh
OLD = "folded up and back over the rump at rest and spread aloft by flyRot"
NOTE = ("; THE ARM drawn (2026-11-08, tools/creaturegen/var/isl/mantarm.py): the elbow moved onto the skin's leading edge (it sat "
        "16 cm inside the skin, behind it), the hand's frames kept, and the humerus, the forearm and the thumb's hooked claw sharp "
        "`horn`s on their own bones -- details, never in the body's field -- so the arm runs visibly along the leading edge aloft, "
        "shoulder to elbow to wrist, without pulling the body's skin after it")
assert OLD in d["_about"] and "mantarm.py" not in d["_about"]
d["_about"] = d["_about"].replace(OLD, OLD + NOTE)
def fmt(v, ind=0):   # (mantwing.py's layout)
    c = lambda x: json.dumps(x, separators=(", ", ": "))
    pad = "  " * (ind + 1)
    if isinstance(v, list) and any(isinstance(x, dict) for x in v):
        return "[\n" + ",\n".join(pad + c(x) for x in v) + "\n" + "  " * ind + "]"
    if isinstance(v, dict) and (len(c(v)) > 100 or any(isinstance(x, list) and any(isinstance(y, dict) for y in x) for x in v.values())):
        return "{\n" + ",\n".join(pad + json.dumps(k) + ": " + fmt(x, ind + 1) for k, x in v.items()) + "\n" + "  " * ind + "}"
    return c(v)
open(outp, "w").write(fmt(d) + "\n")
# ---- checked: the hand and the fingers where they were, at rest, spread and every phase of the beat; the elbow on the edge
P1, bi1, RS1, SP1, FL1 = probe(outp)
dev = lambda X, Y: max(float(np.linalg.norm(X[bi[b]][:3, 3] - Y[bi1[b]][:3, 3]) + np.abs(X[bi[b]][:3, :3] - Y[bi1[b]][:3, :3]).max())
                       for b in ("wHandL", "wFinger0L", "wFinger3L", "wHandR", "wFinger0R"))
print("hand frames moved: rest %.2g spread %.2g" % (dev(RS, RS1), dev(SP, SP1)), file=sys.stderr)
S1, E1, W1 = SP1[bi1["wArmL"]][:3, 3], SP1[bi1["wForeL"]][:3, 3], SP1[bi1["wHandL"]][:3, 3]
u = unit(W1 - S1); print("elbow off the leading edge aloft: %.4f m" % np.linalg.norm((E1 - S1) - ((E1 - S1) @ u) * u), file=sys.stderr)
