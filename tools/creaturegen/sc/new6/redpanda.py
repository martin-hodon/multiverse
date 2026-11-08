# redpanda.py -- the red panda (Ailurus fulgens) SCULPTED on its own rig (2nd pass, 2026-11-06: a short stocky round-
# backed body in fluffy fur, a big broad round head with a short pointed muzzle, big round-tipped white-rimmed ears out to
# the sides, dark eyes, the face's red-brown TEARS and white brows / cheeks / muzzle as separate PAINTS, a thick bushy tail)
import json
from g6 import *
from lib import Sculpt
N = "redpanda"
rig = {
    "name": N, "kind": "mammal", "headForm": "canid", "shy": 7, "graze": 0.35, "rest": 0.65, "print": "paw", "headTurn": 22,
    "rear": [-0.09, 0.215, 0, 0.12, 0.1, 0.1], "front": [0.05, 0.195, 0, 0.12, 0.09, 0.09],
    "neck": [0.1, 0.21, 0, 0.165, 0.24, 0, 0.06, 0.055],
    "head": [0.205, 0.255, 0, 0.06], "muzzle": [0.24, 0.24, 0, 0.275, 0.229, 0, 0.025, 0.011], "nose": [0.279, 0.231, 0, 0.007],
    "ears": [0.194, 0.295, 0.04, 0.1888, 0.3294, 0.0658, 0.02, 0.006], "eyes": [0.249, 0.26, 0.033, 0.0068],
    "legs": {"front": [0.055, 0.15, 0.05, 0.07], "hind": [-0.112, 0.16, 0.055, 0.08], "radii": [0.032, 0.025, 0.019], "foot": [0.027, 0.011, 0.02], "kneeH": -1},
    "tail": {**arc_through([-0.168, 0.242], [-0.57, 0.1], 0.07), "r1": 0.045, "r2": 0.04, "n": 6, "sway": 12, "speed": 0.5},
    "c": {"body": "#ad4a26", "muzzle": "#eee8de", "ear": "#6e2814", "leg": "#24140f", "tail": "#ad4a26", "eye": "#0e0806", "nose": "#141010",
          "white": "#f0ebe2", "black": "#24140f", "head": "#b8582e", "back": "#a2421f", "ring": "#d8a46a", "tear": "#4a1608", "earMid": "#8a3418", "earIn": "#f0ebe2",
          "paw": "#140c0a", "lid": "#1a0c08", "claw": "#3a3029", "tip": "#5a2414"},
    "_about": ("a red panda SCULPTED on its rig (2026-11-06, 2nd pass; gen: scratchpad sc/new6/redpanda.py): 55 cm of soft, "
               "fluffy, rusty-red tree-dweller -- a short stocky round-backed body, the rump a little high, on short black legs, "
               "the belly and chest black too; a big broad ROUND head with a short pointed muzzle; big round-tipped triangular ears out to the "
               "sides, white-rimmed; dark eyes; a red-brown 'tear' from each eye down to the mouth's corner, white brows, cheeks "
               "and muzzle (paints, each its own patch) to a black nose; a thick bushy tail ringed red and buff to a dark tip. "
               "Woodland; shy"),
    "coats": [{}, {"name": "pale", "colors": {"body": "#b8603a", "head": "#c06a3e", "back": "#ae5634", "ring": "#e0b884"}},
              {"name": "dark", "colors": {"body": "#9a3a1c", "head": "#a8461f", "back": "#8a3216", "ring": "#cc9458", "black": "#1a0e0a", "leg": "#1a0e0a"}}],
    "variants": {"cub": {"scale": 0.6}},
}
write_rig(N, rig)   # (first as drawn: the joints below are read from it; rewritten with the bigger head at the end)
J = joints_of(N)
S = Sculpt()
B, W, K_ = "@body", "@white", "@black"
o = lambda b: J[b]["o"]
FL, FK, FF = o("legFLu"), o("legFLl"), o("footFL")
HL, HK, HF = o("legHLu"), o("legHLl"), o("footHL")
H0, PAT = 0.15, "agouti"
FUZ = {"amp": 0.0042, "size": 0.016}   # (the coat heaped in soft tufts: no rubber)
# ---- trunk: SHORT and stocky, round-backed, the rump a little higher than the shoulder; black below
S.ell("chest", [0.045, 0.192, 0], [0.085, 0.078, 0.072], rot=[0, 0, 4], k=0.03, color=B, hair=H0, pat=PAT, fleece=FUZ)
S.ell("barrel", [-0.025, 0.2, 0], [0.1, 0.09, 0.092], k=0.035, color=B, hair=H0, pat=PAT, fleece=FUZ)
S.ell("rump", [-0.1, 0.216, 0], [0.082, 0.088, 0.088], rot=[0, 0, -6], k=0.032, color=B, hair=H0, pat=PAT, fleece=FUZ)
S.ell("saddle", [-0.04, 0.264, 0], [0.11, 0.036, 0.052], rot=[0, 0, -4], k=0.03, kc=0.025, color="@back", hair=H0, pat=PAT, fleece=FUZ)
S.ell("belly", [-0.015, 0.138, 0], [0.1, 0.04, 0.058], k=0.03, kc=0.008, color=K_, hair=H0, pat=PAT)
S.ell("breast", [0.075, 0.152, 0], [0.045, 0.048, 0.046], k=0.025, kc=0.008, color=K_, hair=H0, pat=PAT)
# ---- neck: short and thick; the throat black
S.ell("neck", [0.135, 0.226, 0], [0.055, 0.058, 0.056], rot=[0, 0, 25], bone="neck", k=0.025, color=B, hair=H0, pat=PAT, fleece=FUZ)
S.ell("throat", [0.145, 0.19, 0], [0.045, 0.034, 0.04], rot=[0, 0, 20], bone="neck", k=0.02, kc=0.008, color=K_, hair=H0, pat=PAT)
# ---- head: BIG, broad and ROUND -- a wide cranium, a broad forehead, full cheek ruffs out to the sides, a short pointed
#      muzzle; all red here, the white and the tears painted on below
S.ell("cranium", [0.2, 0.258, 0], [0.05, 0.048, 0.054], bone="head", k=0.02, color="@head", hair=H0, pat=PAT)
S.ell("nape", [0.178, 0.25, 0], [0.042, 0.046, 0.05], bone="head", k=0.02, color="@head", hair=H0, pat=PAT)
S.ell("forehead", [0.226, 0.27, 0], [0.03, 0.026, 0.042], bone="head", k=0.016, color="@head", hair=H0, pat=PAT)
S.ell("cheek", [0.214, 0.234, 0.036], [0.034, 0.03, 0.03], rot=[0, 0, -10], bone="head", k=0.018, color="@head", mirror=True, hair=H0, pat=PAT, fleece={"amp": 0.002, "size": 0.009})
S.cone("snout", [0.238, 0.24, 0], [0.274, 0.229, 0], 0.024, 0.011, bone="head", k=0.012, color="@head", hair=H0)
S.ell("chin", [0.252, 0.219, 0], [0.02, 0.0095, 0.015], bone="head", k=0.01, kc=0.004, color="@head", hair=H0)
# (round 3: the NOSE black and proud of the snout's tip -- inside it, the snout's red showed there)
S.ell("nose", [0.2835, 0.2325, 0], [0.0075, 0.0072, 0.0102], bone="head", k=0.004, kc=0.002, color="@nose", wet=0.5)
# ears: big TRIANGLES on the top corners of the head, out to the sides and up -- the white front (a little larger: the rim
# shows round the dark back from behind), the back dark red-brown
EA, EB, ET = [0.197, 0.298, 0.018], [0.19, 0.262, 0.062], [0.184, 0.332, 0.088]
# (round 3: a little smaller -- 86% about the base -- and the TIP ROUNDED: each layer a fan of slabs round an arc in
#  place of the point, not a fox's sharp triangle)
EM = [(EA[i] + EB[i]) / 2 for i in range(3)]
EA, EB, ET = [[EM[i] + (p[i] - EM[i]) * 0.86 for i in range(3)] for p in (EA, EB, ET)]
def ear_fan(id, A, B, T, r, **kw):
    L = lambda p, q, u: [p[i] + (q[i] - p[i]) * u for i in range(3)]
    P1, P2 = L(T, A, 0.34), L(T, B, 0.34)
    Tc = L(T, [(A[i] + B[i]) / 2 for i in range(3)], 0.06)
    arc = [[(1 - s) ** 2 * P1[i] + 2 * s * (1 - s) * Tc[i] + s * s * P2[i] for i in range(3)] for s in (0, 0.25, 0.5, 0.75, 1)]
    poly = arc + [B]
    for j in range(len(poly) - 1):
        S.tri(id if j == 0 else f"{id}{j}", [round(x, 4) for x in A], [round(x, 4) for x in poly[j]], [round(x, 4) for x in poly[j + 1]], r, **kw)
ear_fan("earIn", EA, EB, ET, 0.0042, bone="earL", k=0.004, kc=0.002, color=W, mirror=True, hair=H0)
cen = [(EA[i] + EB[i] + ET[i]) / 3 for i in range(3)]
shr = lambda p: [cen[0] + (p[0] - cen[0]) * 0.8 - 0.0045, cen[1] + (p[1] - cen[1]) * 0.8 - 0.002, cen[2] + (p[2] - cen[2]) * 0.8]
ear_fan("ear", shr(EA), shr(EB), shr(ET), 0.0045, bone="earL", k=0.004, kc=0.002, color="@ear", mirror=True, hair=H0)
# (the front's middle red-brown too, inside its white rim: a third slab a little proud of the white one, smaller)
mid = lambda p: [cen[0] + (p[0] - cen[0]) * 0.62 + 0.0032, cen[1] + (p[1] - cen[1]) * 0.62 - 0.003, cen[2] + (p[2] - cen[2]) * 0.62]
ear_fan("earMid", mid(EA), mid(EB), mid(ET), 0.003, bone="earL", k=0.002, kc=0.0015, color="@earMid", mirror=True, hair=H0)
# ---- legs: short, thick, black; the paws furred, small curved claws
S.cone("arm", [FL[0] - 0.005, FL[1] + 0.01, FL[2]], FK, 0.034, 0.025, bone="legFLu", k=0.018, kc=0.014, color=K_, mirror=True, hair=H0, pat=PAT)
S.cone("forearm", FK, [FF[0] - 0.003, 0.02, FF[2]], 0.024, 0.019, bone="legFLl", k=0.012, color=K_, mirror=True, hair=H0, pat=PAT)
S.ell("paw", [FF[0] + 0.007, 0.011, FF[2]], [0.024, 0.011, 0.019], bone="footFL", k=0.008, color="@paw", mirror=True)
for j, dz in enumerate((-0.009, 0.0, 0.009)):
    S.cone(f"claw{j}", [FF[0] + 0.024, 0.011, FF[2] + dz], [FF[0] + 0.034, 0.003, FF[2] + dz], 0.0028, 0.0011, bone="footFL", k=0, color="@claw", mirror=True)
S.ell("thigh", [HL[0] + 0.005, HL[1] + 0.012, HL[2] + 0.004], [0.052, 0.062, 0.036], rot=[0, 0, 10], bone="legHLu", k=0.02, kc=0.012, color=B, mirror=True, hair=H0, pat=PAT, fleece=FUZ)
S.cone("shank", [HK[0] + 0.004, HK[1] + 0.01, HK[2]], [HF[0] - 0.006, 0.018, HF[2]], 0.025, 0.018, bone="legHLl", k=0.012, color=K_, mirror=True, hair=H0, pat=PAT)
S.ell("foot", [HF[0] + 0.011, 0.01, HF[2]], [0.031, 0.01, 0.019], bone="footHL", k=0.008, color="@paw", mirror=True)
# ---- the tail: long, THICK and BUSHY -- as thick as a leg at its root, fattest past it -- ringed red and buff to a dark
#      tip; tube segments, each its ring's colour, heaped in tufts (fleece)
T = rig["tail"]; NT = 24; P = arc_pts(T, NT); tb = tail_bones(T)
def smooth(a, b, x): x = min(1, max(0, (x - a) / (b - a))); return x * x * (3 - 2 * x)
TP = [[q[0], q[1], 0, 0.034 + 0.026 * smooth(0, 0.22, i / NT) - 0.022 * smooth(0.78, 1.0, i / NT)] for i, q in enumerate(P)]
FUR = {"amp": 0.0038, "size": 0.014}
RINGS = ["@tail", "@ring"] * 5 + ["@tail", "@tip"]
for j, col in enumerate(RINGS):
    a, b = j * 2, min(NT, j * 2 + 2)
    S.tube(f"tailR{j}", TP[a:b + 1], bone=tb((a + b) / 2 / NT), k=0.02, kc=0.004, color=col, hair=H0, pat=PAT, fleece=FUR)
# ---- the FACE, painted on the finished head (clean edges): white cheeks low on each side, a white muzzle (the nose kept
#      black), small white brows over the eyes, and the red-brown TEAR from under each eye down to the mouth's corner
S.ell("pCheek", [0.236, 0.228, 0.042], [0.024, 0.02, 0.024], rot=[0, 0, -15], bone="head", op="paint", kc=0.004, color=W, mirror=True)
S.ell("pMuzzle", [0.262, 0.229, 0], [0.019, 0.019, 0.026], bone="head", op="paint", kc=0.003, color=W)
S.ell("pBrow", [0.246, 0.279, 0.021], [0.01, 0.0065, 0.012], rot=[0, 0, -20], bone="head", op="paint", kc=0.002, color=W, mirror=True)
S.tube("pTear", [[0.249, 0.252, 0.034, 0.0075], [0.253, 0.24, 0.033, 0.0095], [0.257, 0.229, 0.027, 0.009], [0.258, 0.221, 0.018, 0.0065]], bone="head", op="paint", kc=0.0015, color="@tear", mirror=True)
S.ell("pNose", [0.284, 0.2325, 0], [0.0095, 0.0092, 0.0122], bone="head", op="paint", kc=0.001, color="@nose")
# ---- the head 15% bigger than drawn (a red panda's round head is big for its body): its shapes, the face's paints and
#      the eyes scaled about the neck's top
PV, HSC = [0.165, 0.24, 0.0], 1.15
def bigp(p): return [round(PV[i] + (p[i] - PV[i]) * HSC, 4) for i in range(3)] + list(p[3:])
for q in S.shapes:
    if q.get("bone") not in ("head", "earL"): continue
    for kk in ("c", "a", "b"):
        if kk in q: q[kk] = bigp(q[kk])
    if "pts" in q: q["pts"] = [bigp(p[:3]) + [round(p[3] * HSC, 4)] for p in q["pts"]]
    for kk in ("ra", "rb", "k", "kc"):
        if kk in q: q[kk] = round(q[kk] * HSC, 4)
    if "r" in q: q["r"] = [round(x * HSC, 4) for x in q["r"]] if isinstance(q["r"], list) else round(q["r"] * HSC, 4)
for k in ("head", "muzzle", "nose", "ears", "eyes"):   # (the rig's head cluster with them)
    v = rig[k]; n3 = len(v) // 3 if k in ("muzzle", "ears") else 1
    for j in range(n3): v[3 * j:3 * j + 3] = bigp(v[3 * j:3 * j + 3])
write_rig(N, rig)
eye = rig["eyes"]
sc = {"keep": [], "mesh": {"tris": [7600, 2600], "cell": 0.0042, "focus": {"head": 6}}, "shape": S.shapes,
      "eyes": {"at": eye[:3], "from": bigp([0.2, 0.258, 0]), "r": 0.0078, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.45, "socket": 1.35}}
finish(N, rig, sc)
