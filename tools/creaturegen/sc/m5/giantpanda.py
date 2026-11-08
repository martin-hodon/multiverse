# giantpanda.py -- THE GIANT PANDA on the bear's rig, scaled to 1.5 m (shapes written in bear units, then scaled by F)
# round 2 (the coordinator's review): the head ROUND and broad, big cheek mass, the forehead rising steeply from a SHORT
# muzzle; large black oval eye patches slanting down and out (PAINT: op "paint", a clean edge on the finished surface);
# big round ears on top; the shoulder band a paint too (no shards where a black skin crossed the white); thick rounded
# legs on visible paws with toe lobes; a bulkier body, the rump round and high
import json, subprocess, os
from lib import *
F = 0.62
bear = load("bear")
J = joints("bear")
Hd, Er = J["head"], J["earL"]
FL, E, P = J["legFLu"], J["legFLl"], J["footFL"]
Hh, K, Q = J["legHLu"], J["legHLl"], J["footHL"]
zF, zH = FL[2], Hh[2]
S = []
def sh(**k): S.append(k); return k
W, BK = "@body", "@black"
# the trunk: a heavy barrel, the rump round and high, no hump
sh(id="chest", type="ell", c=[0.4, 0.78, 0], r=[0.48, 0.36, 0.4], k=0.14, color=W)
sh(id="barrel", type="ell", c=[-0.05, 0.78, 0], r=[0.56, 0.37, 0.42], k=0.14, color=W)
sh(id="belly", type="ell", c=[0.0, 0.55, 0], r=[0.46, 0.14, 0.32], k=0.1, color=W)
sh(id="rump", type="ell", c=[-0.5, 0.84, 0], r=[0.4, 0.36, 0.4], k=0.14, color=W)
sh(id="scapula", type="ell", c=[0.55, 0.86, 0.24], r=[0.15, 0.22, 0.11], rot=[0, 0, 15], k=0.1, color=W, mirror=True)
# forelegs: thick, rounded, a wrist, a broad paw with toe lobes and dark claws
sh(id="arm", type="tube", bone="legFLu", pts=[[FL[0] + 0.05, 0.74, zF - 0.03, 0.18], [FL[0] + 0.02, 0.48, zF - 0.01, 0.15], [E[0], E[1] + 0.02, zF, 0.13]], k=0.1, color=BK, mirror=True)
sh(id="forearm", type="cone", bone="legFLl", a=[E[0], E[1] + 0.01, zF], b=[P[0] - 0.02, 0.15, zF], ra=0.125, rb=0.09, k=0.07, color=BK, mirror=True)
sh(id="paw", type="ell", bone="footFL", c=[P[0] + 0.05, 0.065, zF], r=[0.16, 0.068, 0.125], k=0.06, color=BK, mirror=True)
for i, dz in enumerate((-0.075, -0.025, 0.025, 0.075)):
    sh(id=f"toe{i}", type="sphere", bone="footFL", c=[P[0] + 0.18, 0.045, zF + dz], r=0.04, k=0.03, color=BK, mirror=True)
    sh(id=f"claw{i}", type="cone", bone="footFL", a=[P[0] + 0.2, 0.04, zF + dz], b=[P[0] + 0.24, 0.012, zF + dz * 1.05], ra=0.012, rb=0.004, k=0.003, kc=0.001, color="@claw", mirror=True)
# hind legs: black from the hip down, thick, the long flat sole
sh(id="thigh", type="ell", bone="legHLu", c=[Hh[0] - 0.01, 0.62, zH + 0.02], r=[0.24, 0.29, 0.17], rot=[0, 0, 10], k=0.1, kc=0.06, color=BK, mirror=True)
sh(id="gaskin", type="cone", bone="legHLu", a=[Hh[0], 0.46, zH], b=[K[0] - 0.01, K[1] + 0.01, zH], ra=0.15, rb=0.12, k=0.08, color=BK, mirror=True)
sh(id="shin", type="cone", bone="legHLl", a=[K[0] - 0.01, K[1], zH], b=[Q[0] - 0.03, 0.12, zH], ra=0.118, rb=0.09, k=0.07, color=BK, mirror=True)
sh(id="hpaw", type="ell", bone="footHL", c=[Q[0] + 0.05, 0.06, zH], r=[0.19, 0.06, 0.115], k=0.06, color=BK, mirror=True)
for i, dz in enumerate((-0.06, 0.0, 0.06)):
    sh(id=f"htoe{i}", type="sphere", bone="footHL", c=[Q[0] + 0.21, 0.042, zH + dz], r=0.036, k=0.03, color=BK, mirror=True)
# the neck: short and thick
sh(id="neck", type="ell", bone="neck", c=[0.86, 0.95, 0], r=[0.3, 0.28, 0.29], rot=[0, 0, 22], k=0.12, color=W)
# THE HEAD: big and ROUND -- a round skull, big cheek masses (the chewing muscles of a bamboo eater) making the face
#  near-round from the front, the forehead rising steeply from a SHORT muzzle, a black nose
C = [Hd[0] + 0.1, Hd[1] + 0.02, 0]
c = lambda dx, dy, dz=0.0: [C[0] + dx, C[1] + dy, dz]
sh(id="cranium", type="ell", bone="head", c=c(0, 0.01), r=[0.2, 0.19, 0.21], k=0.08, color=W)
sh(id="forehead", type="ell", bone="head", c=c(0.09, 0.07), r=[0.12, 0.12, 0.16], k=0.07, color=W)
sh(id="cheek", type="ell", bone="head", c=c(0.04, -0.07, 0.12), r=[0.15, 0.14, 0.13], k=0.08, color=W, mirror=True)
sh(id="jowl", type="ell", bone="head", c=c(-0.03, -0.1, 0.13), r=[0.13, 0.11, 0.11], k=0.07, color=W, mirror=True)
sh(id="muzzle", type="ell", bone="head", c=c(0.2, -0.065), r=[0.1, 0.08, 0.09], k=0.05, color=W)
sh(id="chin", type="ell", bone="head", c=c(0.14, -0.13), r=[0.09, 0.055, 0.08], k=0.04, color=W)
sh(id="nose", type="ell", bone="head", c=c(0.288, -0.035), r=[0.032, 0.03, 0.048], k=0.01, kc=0.003, color="@nose", wet=0.3)
sh(id="lipLine", type="cone", bone="head", a=c(0.29, -0.06), b=c(0.275, -0.095), ra=0.006, rb=0.005, k=0.004, kc=0.002, color="@nose")
# ears: big, ROUND, black, on top of the head toward the sides
sh(id="ear", type="ell", bone="earL", c=c(-0.07, 0.2, 0.15), r=[0.05, 0.085, 0.085], rot=[-35, 0, 0], k=0.03, kc=0.006, color=BK, mirror=True)
# the eyes: small, IN the patches, set on the front of the face
eyes = {"at": c(0.17, 0.035, 0.09), "from": c(0.0, 0.03, 0), "r": 0.0135, "iris": "@eye", "pupil": "round", "color": "#3a2c22", "lid": "@lid", "sink": 0.35}   # (a dark eyeball: no white ring in the patch)
# THE EYE PATCHES: big black ovals round each eye, slanting down and outward (paint: the surface inside takes the black)
sh(id="patch", type="ell", op="paint", bone="head", c=c(0.178, 0.004, 0.106), r=[0.09, 0.112, 0.06], rot=[-34, 18, 0], kc=0.012, color=BK, mirror=True)
# THE SHOULDER BAND: black right round the trunk over the shoulders and down into the forelegs (paint: a clean edge)
sh(id="band", type="ell", op="paint", c=[0.5, 0.82, 0], r=[0.2, 0.6, 0.6], rot=[0, 0, -8], kc=0.045, color=BK)
# ---- scale to the panda
def sc(q):
    q = dict(q)
    for kk in ("c", "a", "b"):
        if kk in q: q[kk] = [x * F for x in q[kk]]
    if "pts" in q: q["pts"] = [[x * F for x in p] for p in q["pts"]]
    for kk in ("ra", "rb", "k", "kc"):
        if kk in q: q[kk] = q[kk] * F
    if "r" in q: q["r"] = [x * F for x in q["r"]] if isinstance(q["r"], list) else q["r"] * F
    return q
shapes = [sc(q) for q in S]
# (round 3) THE MARKINGS PER PIXEL: the eye patches and the shoulder band are no longer paints -- the paint went to the
# vertices, and where the near mesh is coarse a black-to-white edge showed as grey shards. They are coatpat.js's PANDA
# pattern (64; QINLING 65, the brown coat) on every white shape, its ellipsoids these two shapes' -- printed here as the
# rows of each one's inverse frame (local unit coords u = M (p - c)) for coatpat.js pandaOf, written in by hand
def euler(rx, ry, rz):   # three's 'XYZ': R = Rx Ry Rz
    a, b, g = (math.radians(v) for v in (rx, ry, rz))
    Rx = [[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]]
    Ry = [[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]]
    Rz = [[math.cos(g), -math.sin(g), 0], [math.sin(g), math.cos(g), 0], [0, 0, 1]]
    mm = lambda A, B: [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return mm(mm(Rx, Ry), Rz)
MARKS = {}
for q in shapes:
    if q["id"] in ("patch", "band"):
        R = euler(*(q.get("rot") or [0, 0, 0]))
        M = [[R[k][i] / q["r"][i] for k in range(3)] for i in range(3)]   # (row i: R's column i over r_i)
        MARKS[q["id"]] = (q["c"], M)
        print(q["id"], "c", [round(x, 4) for x in q["c"]], "rows", [[round(x, 3) for x in row] for row in M])
# (the patch's CORE stays a paint, 70% of it, so the eye's socket -- which the pattern does not reach -- sits in black;
#  its soft edge is well inside the pattern's black, so no shard shows)
for q in shapes:
    if q["id"] == "patch": q["id"] = "patchCore"; q["r"] = [x * 0.7 for x in q["r"]]; q["kc"] = 0.004
shapes = [q for q in shapes if q["id"] != "band"]
for q in shapes:   # (the black shapes too: inside the band the pattern's black, so the trunk's white fades into no grey there)
    if q.get("color") in (W, BK) and q.get("op") != "paint": q["pat"] = [{"when": "qinling", "v": "qinling"}, {"when": "panda", "v": "panda"}]
eyes = {**eyes, "at": [x * F for x in eyes["at"]], "from": [x * F for x in eyes["from"]], "r": eyes["r"] * F}
def scl(v): return [x * F if isinstance(x, (int, float)) else x for x in v]
d = {"name": "giantpanda",
     "_about": ("the GIANT PANDA sculpted on the bear's rig scaled to 1.5 m (2026-11-06, round 2; gen: scratchpad sc/m5/giantpanda.py): a "
                "heavy white barrel, the rump round and high, on thick rounded black legs with broad paws; a broad black band over "
                "the shoulders and round the chest into the forelegs; a big ROUND white head -- big cheek masses, the forehead "
                "rising steeply from a short muzzle -- large black oval patches round the small eyes slanting down and out, big "
                "round black ears on top, a black nose; a short white tail. Slow and placid; lies down at its stops"),
     "headForm": "bear", "graze": 0.55, "rest": 0.7, "kind": "mammal", "headScale": 0.62, "headTurn": 14, "print": "paw",
     "rear": scl(bear["rear"]), "front": scl(bear["front"]), "neck": scl(bear["neck"]), "head": scl(bear["head"]), "muzzle": scl(bear["muzzle"]),
     "nose": scl(bear["nose"]), "ears": scl(bear["ears"]), "eyes": scl(bear["eyes"]),
     "legs": {k: scl(v) for k, v in bear["legs"].items()},
     "tail": {**bear["tail"], "c": [-1.0 * F, 0.9 * F], "R": 0.09 * F, "a0": -0.6, "a1": -1.7, "r1": 0.06 * F, "r2": 0.04 * F, "n": 2, "sway": 6},
     "c": {"body": "#ece8dd", "muzzle": "#ece8dd", "ear": "#16130f", "leg": "#16130f", "tail": "#e6e1d4", "eye": "#1a120c", "black": "#17130f",
           "head": "#ece8dd", "nose": "#100c0a", "foot": "#16130f", "claw": "#3a3430", "lid": "#100c0a"},
     "params": {"panda": True},
     "coats": [{}, {"name": "qinling", "params": {"qinling": True}, "colors": {"black": "#4a3426", "leg": "#4a3426", "ear": "#4a3426", "foot": "#4a3426", "body": "#e6dccb"}}],
     "variants": {"cub": {"scale": 0.45}},
     "sculpt": {"keep": ["tail\\d*"], "mesh": {"tris": [9600, 2900], "cell": 0.0075, "anchor": 260, "focus": {"head": 4}}, "shape": shapes, "eyes": eyes,
                "shade": {"back": 1.03, "belly": 0.93, "low": 0.92, "on": "@body"}}}
save("giantpanda", d)
print(len(shapes), "shapes")
