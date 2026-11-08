#!/usr/bin/env python3
# mantwing.py IN.json OUT.json -- the manticore's wings as ONE continuous skin a side (bodyspec.js "membrane": shared
# vertices, each on its own bone or a blend of two), in place of the patchwork it was: 22 loose triangle plates a wing,
# each on a bone of its own (wMemA* fanned from the shoulder, wMemB* on the fingers), the arm's cover plates and the
# hand's cover membrane over them. Plates on different bones posed apart, so every shared edge opened into a sliver
# aloft (and at the wrist, between the arm's panel and the hand's).
#
# THE OUTLINE is the plates' own, read where they lie SPREAD (the flight pose without its beat: skeleton.js flyRot +
# FLIGHT.arm, wing anim deg 0): the leading edge shoulder S -> wrist W, finger 0 to its tip, the scalloped trailing edge
# tip to tip (each scallop's three points; the middle one, where two plates met, their mean), behind finger 3 the strip
# back to the arm panel's outer corner, and the arm panel's trailing edge to its root on the flank.
# THE MESH: two fans sharing their seam -- the HAND from W (a spoke down each finger and each trailing point, NRH
# rings out) and the ARM from S (spokes to W, along the seam W -> outer corner -- the hand fan's last spoke, its very
# vertices -- and the trailing edge to the root, NRA rings out); long rim segments split so no spoke is far from the next.
# THE SKIN (two bones a point at most): in the hand, a point between finger i and i + 1 rides both by its angle between
# them; behind finger 3 the strip rides finger 3 alone (as its plates did: it folds with it). The arm's fan rides
# [wRootL, finger 3] by u, how far the point lies from the root line (shoulder -> the root's rear end on the flank)
# toward the seam (wrist -> outer corner): u = d_root / (d_root + d_seam) -- the root on the flank stays on the body,
# the seam on the finger, the leading edge between them. wRootL is a bone added here: on the body at the shoulder,
# turned FOLD degrees about the root line at rest (and back by flyRot aloft, where it IS the body's frame), so that at
# rest the skin's inner part stands up against the flank instead of sticking straight out of it as a shelf.
# Each point's REST position is solved from where it lies spread: the blend of its bones' skinning maps inverted (as
# the pteranodon's wing, sc/ptero/gen.py solve_rest) -- aloft (beat-free) the skin is exactly the outline above, and at
# rest it folds wherever its bones take it (checked: no face crosses another at rest or at any phase of the beat).
# Normals worked out spread, carried back the same way.
# COLOUR: @mem, the arm panel's middle lighter toward @memIn (`tone`), as the arm's cover plates were.
# The plates' bones (wMemA*, wMemB* in extras) go: nothing rides them now. Run once, on the plated manticore (the JSON
# before 2026-11-08's wing skin: it reads the outline from the plates, so it cannot run on its own output).
import json, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/martin/store/apps/multiverse/"
NRH, NRA, SEG = 10, 10, .07   # (rings in the hand's fan and the arm's; the longest rim segment, metres)
TH = .002                     # (the skin's half-thickness)
inp, outp = sys.argv[1], sys.argv[2]
d = json.load(open(inp))
REG = next(p for p in (HERE + "/../../reg.mjs", HERE + "/../reg.mjs") if os.path.exists(p))
M4 = lambda e: np.array(e, float).reshape(4, 4).T
def load(path):
    global probe, bones, bi, Ri, SP, RS
    probe = json.loads(subprocess.check_output(["node", "--import", REG, HERE + "/mantwing_probe.mjs", os.path.abspath(path)], cwd=REPO))
    bones = probe["bones"]; bi = {b: i for i, b in enumerate(bones)}
    Ri = [M4(m) for m in probe["restInv"]]; SP = [M4(m) for m in probe["spread"]]; RS = [M4(m) for m in probe["rest"]]
load(inp)
def A(b): i = bi[b]; return SP[i] @ Ri[i]                       # (a bone's skinning map: rest -> spread)
def sk(b, p): return (A(b) @ np.append(np.asarray(p, float), 1))[:3]
def joint(b, loc=(0, 0, 0)): return (SP[bi[b]] @ np.append(np.asarray(loc, float), 1))[:3]
plates = {q["id"]: q for q in probe["det"] if q["type"] == "tri"}
P = lambda pid, k: sk(plates[pid]["bone"], plates[pid][k])     # (a plate's corner, spread)
S, W = joint("wArmL"), joint("wHandL")
flen = {i: next(e["raw"]["size"]["len"] for e in d["extras"] if e.get("raw", e).get("id") == f"wFinger{i}L") for i in range(4)}
T = [joint(f"wFinger{i}L", (0, flen[i], 0)) for i in range(4)]
mid = lambda a, b: (a + b) / 2
# the hand's rim, finger 0's tip round to the arm panel's outer corner: (point, finger index it lies on or None)
nm = ["", "1", "2", "3"]
rimH = []
for i in range(3):
    a = f"wMemB{i}LM"
    rimH += [(T[i], i), (P(a, "c"), None), (mid(P(f"wMemB{i}aLM", "c"), P(f"wMemB{i}bLM", "b")), None), (P(f"wMemB{i}bLM", "c"), None)]
rimH += [(T[3], 3), (P("wMemB3LM", "c"), None), (P("wMemB3aLM", "c"), None), (P("wMemB3bLM", "c"), None)]
C = mid(P("wMemB3cLM", "c"), P("wMemA1LM", "c"))   # (the outer corner: the strip's last point, the arm panel's)
rimH.append((C, "seam"))
rimA = [P(f"wMemA{j}LM", "c") for j in (2, 3, 4, 5)]          # (the arm panel's trailing edge, the outer corner to the root)
print("spread: S", S.round(3), "W", W.round(3), "corner", C.round(3), "A1.c-B3c.c gap", np.linalg.norm(P("wMemB3cLM", "c") - P("wMemA1LM", "c")).round(4),
      "seam A.c off line", np.linalg.norm(np.cross(P("wMemALM", "c") - W, C - W)) / np.linalg.norm(C - W), file=sys.stderr)
def split(pts, seg=SEG):   # a polyline with each long piece split evenly
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        n = max(1, math.ceil(np.linalg.norm(b - a) / seg))
        out += [a + (b - a) * k / n for k in range(1, n + 1)]
    return out
# ---- the vertices
V, SKIN, KEY = [], [], {}
def vid(p, skin):
    k = tuple(np.round(p, 6))
    if k in KEY: return KEY[k]
    KEY[k] = len(V); V.append(np.asarray(p, float)); SKIN.append(skin); return KEY[k]
TRI = []
def fan(O, oskin, rim, nr, skin_of):
    """rings out from O to each rim point; skin_of(j, s) the skin of spoke j's point s of the way out"""
    o = vid(O, oskin); G = []
    for j, Q in enumerate(rim):
        G.append([o] + [vid(O + (Q - O) * r / nr, skin_of(j, r / nr)) for r in range(1, nr + 1)])
    for j in range(len(rim) - 1):
        a, b = G[j], G[j + 1]
        TRI.append([o, a[1], b[1]])
        for r in range(1, nr):
            TRI.extend([[a[r], a[r + 1], b[r + 1]], [a[r], b[r + 1], b[r]]])
    return G
# the hand's fan: its rim (split), each point's angle about W between the fingers either side
hpts, hfin = [], []
for (p, f), (q, g) in zip(rimH, rimH[1:]):
    seg = split([p, q]); hpts += seg[:-1]; hfin += [f] + [None] * (len(seg) - 2)
hpts.append(rimH[-1][0]); hfin.append("seam")
nH = np.cross(T[0] - W, T[3] - W); nH /= np.linalg.norm(nH)      # (the hand's plane, for angles)
def ang(p, ref):
    a, b = ref - W, p - W; return math.atan2(np.cross(a, b) @ nH, a @ b)
fidx = [i for i, f in enumerate(hfin) if f in (0, 1, 2, 3)]
def hskin(j, s):
    f = hfin[j]
    if f in (0, 1, 2, 3): return f"wFinger{f}L"
    k = max(i for i in fidx if i < j)
    if hfin[k] == 3: return "wFinger3L"                          # (behind the last finger: it rides that finger)
    k2 = min(i for i in fidx if i > j)
    t = ang(hpts[j], T[hfin[k]]) / ang(T[hfin[k2]], T[hfin[k]])
    return [f"wFinger{hfin[k]}L", f"wFinger{hfin[k2]}L", round(float(min(1, max(0, t))), 4)]
GH = fan(W, "wHandL", hpts, NRH, hskin)
seam = [V[v] for v in GH[-1]]                                     # (W ... C: the arm's fan runs its rim along these)
# the arm's fan: rim W -> seam -> C -> trailing edge -> root
tr = split([C] + rimA)
apts = seam + tr[1:]
nseam = len(seam)
def smooth(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
R0 = rimA[-1]
# THE ROOT'S FOLD: a bone of its own for the skin's inner edge, wRootL -- on the body at the shoulder, its rest turned
# FOLD degrees about the root line (shoulder -> the root's rear end) so that at rest the skin's inner part stands up
# against the flank (on the body it stuck straight out of it, a shelf), and turned back by flyRot aloft, where it is
# the body's frame exactly
FOLD = 80.0
Sr = (RS[bi["body"]] @ np.linalg.inv(SP[bi["body"]]) @ np.append(S, 1))[:3]; R0r = (RS[bi["body"]] @ np.linalg.inv(SP[bi["body"]]) @ np.append(R0, 1))[:3]
ax = (R0r - Sr) / np.linalg.norm(R0r - Sr)
def rot_axis(a, deg):
    t = math.radians(deg); K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]]); return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K
Rf = rot_axis(ax, FOLD)
if (Rf @ np.array([0, 0, 1.0]))[1] < 0: Rf = rot_axis(ax, -FOLD)   # (the outer side turned UP)
def m2e(m):   # three.js Euler XYZ (Rx Ry Rz), degrees
    b = math.asin(max(-1, min(1, m[0, 2])))
    return [round(math.degrees(v), 4) for v in (math.atan2(-m[1, 2], m[2, 2]), b, math.atan2(-m[0, 1], m[0, 0]))]
e = m2e(Rf)
d["extras"] = [x for x in d["extras"] if x.get("raw", x).get("id") not in ("wRootL", "wRootR")]
for S_, sg in (("L", 1), ("R", -1)):
    er = [e[0] * sg, e[1] * sg, e[2]]
    d["extras"].append({"raw": {"id": "wRoot" + S_, "parent": "body", "shape": "sphere", "size": {"r": 0.01}, "pos": [0, 0, 0], "rot": er, "flyRot": [-v for v in er], "color": "#3a1812", "edge": 0},
                        "at": [round(float(Sr[0]), 4), round(float(Sr[1]), 4), round(float(Sr[2]) * sg, 4)]})
import tempfile
tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); json.dump(d, tmp); tmp.close()
load(tmp.name); os.unlink(tmp.name)
def dseg(p, a, b):
    t = max(0.0, min(1.0, float((p - a) @ (b - a) / ((b - a) @ (b - a))))); return float(np.linalg.norm(p - (a + (b - a) * t)))
def askin(j, s):
    if j < nseam and s == 1: return "wFinger3L"   # (the seam's own points: already made by the hand's fan, on finger 3)
    p = S + (apts[j] - S) * s
    dr, do = dseg(p, S, R0), dseg(p, W, C)
    u = dr / (dr + do) if dr + do > 1e-9 else 0.0
    return ["wRootL", "wFinger3L", round(u, 4)] if u > 1e-4 else "wRootL"
GA = fan(S, "wRootL", apts, NRA, askin)
# ---- orientation: every face's normal up (+y spread)
for t in TRI:
    a, b, c = (V[i] for i in t)
    if np.cross(b - a, c - a)[1] < 0: t[1], t[2] = t[2], t[1]
TRI = [t for t in TRI if len(set(t)) == 3]
# normals spread (by area), tone
nv = np.zeros((len(V), 3))
for t in TRI:
    a, b, c = (V[i] for i in t); n = np.cross(b - a, c - a)
    for i in t: nv[i] += n
nv /= np.linalg.norm(nv, axis=1)[:, None]
col = d["colors"]; lin = lambda h: np.array([(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5)]) ** 2.2
LIGHT = float(np.mean(lin(col["memIn"]) / lin(col["mem"])))
tone = [1.0] * len(V)
for j, sp in enumerate(GA):   # (the arm panel's middle lighter: in from its edges, out from the shoulder)
    if j == 0: continue
    for r, v in enumerate(sp):
        s = r / NRA; m = smooth((s - .15) / .3) * smooth((1 - s) / .35) * smooth(min(j, len(GA) - 1 - j) / 6)
        tone[v] = round(1 + (LIGHT - 1) * .8 * m, 3)
# ---- the rest pose: each point's blended skinning map inverted
blist = sorted({b for s in SKIN for b in ([s] if isinstance(s, str) else s[:2])}, key=lambda b: bi[b])
def blend(s):
    if isinstance(s, str): return A(s), [(s, 1)]
    return (1 - s[2]) * A(s[0]) + s[2] * A(s[1]), [(s[0], 1 - s[2]), (s[1], s[2])]
pts, nrm = [], []
for p, s, n in zip(V, SKIN, nv):
    M, _ = blend(s); Mi = np.linalg.inv(M)
    pts.append((Mi @ np.append(p, 1))[:3]); m = Mi[:3, :3] @ n; nrm.append(m / np.linalg.norm(m))
skin = [blist.index(s) if isinstance(s, str) else [blist.index(s[0]), blist.index(s[1]), s[2]] for s in SKIN]
R5 = lambda v: [round(float(x), 5) for x in v]
mem = {"id": "wingSkin", "type": "membrane", "bone": "wArmL", "pts": [R5(p) for p in pts], "tris": [i for t in TRI for i in t], "bones": blist, "skin": skin,
       "nrm": [R5(n) for n in nrm], "tone": tone, "r": TH, "color": "@mem", "mirror": True}
print("wing skin:", len(V), "points", len(TRI), "faces, bones", blist, file=sys.stderr)
sh = d["sculpt"]["shape"]
drop = lambda q: q.get("type") == "tri" and q["id"].startswith("wMem") or q["id"].startswith("wHandCover") or q["id"] == "wingSkin"
sh = [q for q in sh if not drop(q)]
d["sculpt"]["shape"] = sh + [mem]
OLD = "the membranes authored: each wedge of skin a plate on its own bone, darker at its edge)"
assert OLD in d["_about"]
d["_about"] = d["_about"].replace(OLD, "the skin ONE membrane a wing (2026-11-08, tools/creaturegen/var/isl/mantwing.py): a single sheet, every vertex "
    "shared -- on a finger or between two by its angle, the arm's panel between the root line on the flank (bone wRootL, "
    "the body's frame aloft, folded up against the flank at rest) and the last finger -- so no seam can open; its outline "
    "the old plates', the scalloped trailing edge; @mem, lighter toward @memIn in the arm panel's middle)")
d["extras"] = [e for e in d["extras"] if not e.get("raw", e).get("id", "").startswith("wMem")]
def fmt(v, ind=0):   # (the file's own layout: a list of objects one a line, a big object opened up, the rest inline)
    c = lambda x: json.dumps(x, separators=(", ", ": "))
    pad = "  " * (ind + 1)
    if isinstance(v, list) and any(isinstance(x, dict) for x in v):
        return "[\n" + ",\n".join(pad + c(x) for x in v) + "\n" + "  " * ind + "]"
    if isinstance(v, dict) and (len(c(v)) > 100 or any(isinstance(x, list) and any(isinstance(y, dict) for y in x) for x in v.values())):
        return "{\n" + ",\n".join(pad + json.dumps(k) + ": " + fmt(x, ind + 1) for k, x in v.items()) + "\n" + "  " * ind + "}"
    return c(v)
open(outp, "w").write(fmt(d) + "\n")
