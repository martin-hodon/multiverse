# sabres.py IN OUT -- (USER BUG 2026-11-07) the smilodon's sabres as explicit meshes instead of two overlapping SDF tubes.
# The tubes (r .017 -> .003 on a 1.8 cm grid) came out as ragged, flattened slabs with blunt tips that the decimator
# cut differently left and right. Now each sabre is a closed lathe (a `membrane` detail on the head bone -- drawn as
# it is, never gridded or decimated, mirrored exactly): an egg-shaped section, laterally flattened (the fore-aft
# depth twice the thickness, the front edge fuller than the rear blade), along a gently curved centre line from
# inside the gum to a true point, tapering evenly. Its root is buried in the muzzle, so it leaves the lip cleanly.
import json, math, sys

src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src))
sc = d["sculpt"]

# the centre line (x forward, y up; z constant), from inside the gum to the tip
CTRL = [(1.044, 0.905), (1.0465, 0.875), (1.048, 0.84), (1.048, 0.807), (1.045, 0.774), (1.04, 0.743), (1.033, 0.713),
        (1.0235, 0.684), (1.0115, 0.657), (1.0045, 0.645)]
Z = 0.06
NA, NS = 14, 14            # around, along
DEPTH, THICK = 0.0245, 0.012   # half fore-aft depth, half lateral thickness at the root

def cr(p0, p1, p2, p3, t):   # Catmull-Rom
    return tuple(0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - e) * t * t + (-a + 3 * b - 3 * c + e) * t ** 3)
                 for a, b, c, e in zip(p0, p1, p2, p3))

def curve(u):   # u in [0, 1] along the control polygon
    n = len(CTRL) - 1
    x = min(u * n, n - 1e-9); i = int(x); t = x - i
    P = [CTRL[max(0, i - 1)], CTRL[i], CTRL[i + 1], CTRL[min(n, i + 2)]]
    return cr(*P, t)

# sample by arc length
fine = [curve(i / 400) for i in range(401)]
L = [0.0]
for a, b in zip(fine, fine[1:]): L.append(L[-1] + math.dist(a, b))
tot = L[-1]
def at(s):   # point and tangent at arc-length fraction s
    tgt = s * tot
    j = next(k for k in range(1, len(L)) if L[k] >= tgt - 1e-12)
    f = (tgt - L[j - 1]) / ((L[j] - L[j - 1]) or 1)
    p = [fine[j - 1][k] + (fine[j][k] - fine[j - 1][k]) * f for k in range(2)]
    t = [fine[j][k] - fine[j - 1][k] for k in range(2)]; tl = math.hypot(*t)
    return p, [t[0] / tl, t[1] / tl]

def taper(s):   # even taper to a point; a little fuller just out of the gum
    return (1 - s) ** 0.82 * (1 + 0.12 * math.sin(math.pi * min(1, s * 1.4)))

pts, tone = [], []
for i in range(NS):
    s = i / NS * (1 - 1e-3)
    s = 1 - (1 - s) ** 1.25 if i else 0          # (rings closer together toward the tip)
    (px, py), (tx, ty) = at(s)
    nx, ny = ty, -tx                              # in-plane normal (forward when the tooth points down)
    if nx < 0: nx, ny = -nx, -ny
    f = taper(s)
    for m in range(NA):
        a = 2 * math.pi * m / NA
        ca, sa = math.cos(a), math.sin(a)
        dep = DEPTH * f * (1.12 if ca > 0 else 0.88)   # fuller front edge, finer rear blade
        pts.append([round(px + nx * dep * ca, 5), round(py + ny * dep * ca, 5), round(Z + THICK * f * sa, 5)])
        tone.append(round(0.86 + 0.2 * s, 3))      # (yellower at the gum, paler toward the tip)
(px, py), _ = at(1.0)
tip = len(pts); pts.append([round(px, 5), round(py, 5), Z]); tone.append(1.06)
tris = []
for i in range(NS - 1):
    for m in range(NA):
        a, b = i * NA + m, i * NA + (m + 1) % NA
        c, e = a + NA, b + NA
        tris += [a, b, c, b, e, c]
for m in range(NA):   # the point
    a, b = (NS - 1) * NA + m, (NS - 1) * NA + (m + 1) % NA
    tris += [a, b, tip]
# (outward winding: check one face's normal against the direction from the centre line)
def sub(u, v): return [u[k] - v[k] for k in range(3)]
def crs(u, v): return [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
A, B, C = (pts[tris[k]] for k in range(3))
n = crs(sub(B, A), sub(C, A)); cen = [at(0)[0][0], at(0)[0][1], Z]
if sum(n[k] * (A[k] - cen[k]) for k in range(3)) < 0:
    tris = [tris[i - i % 3 + (3 - i % 3) % 3] for i in range(len(tris))]

shape = {"id": "sabre", "type": "membrane", "bones": ["head"], "skin": [0] * len(pts), "pts": pts, "tris": tris, "tone": tone,
         "r": 0.0002, "color": "@ivory", "mirror": True,
         "_about": "(2026-11-07, user bug: ragged, blunt, uneven sabres) a closed lathe drawn as it is -- see sc/carn/gen/sabres.py"}
out = []
for q in sc["shape"]:
    if q["id"] in ("sabre", "sabreF"):
        if q["id"] == "sabre": out.append(shape)
        continue
    out.append(q)
sc["shape"] = out
# (written as the audit wrote it: two-space indent, each sculpt shape on one line)
shapes = sc["shape"]; sc["shape"] = [f"@@{i}@@" for i in range(len(shapes))]
s = json.dumps(d, indent=2, ensure_ascii=False)
for i, q in enumerate(shapes): s = s.replace(f'"@@{i}@@"', json.dumps(q, ensure_ascii=False))
import re   # (short numeric arrays on one line)
s = re.sub(r"\[\s+([-0-9.e\",*a-z\s]+?)\s+\]", lambda m: "[" + ", ".join(x.strip() for x in m.group(1).split(",")) + "]", s)
open(dst, "w").write(s + "\n")
print(len(pts), "points", len(tris) // 3, "faces, length", round(tot, 3))
