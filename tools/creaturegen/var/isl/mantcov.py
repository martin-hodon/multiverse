#!/usr/bin/env python3
# (SUPERSEDED 2026-11-08 by mantwing.py: the wing is one membrane a side now, the hand cover gone with the plates.)
# mantcov.py IN.json OUT.json -- the manticore's HAND COVER (the smooth plate over each folded hand bundle, manticore.py
# membranes(): fifteen loose triangle plates on the leading finger, lifted ~1 cm off the bundle) made ONE membrane a side
# and ROOTED: the same centre, rings and faces (lighter middle, darker rim: `tone` on a second copy of the inner ring, so
# the colours still change at the ring, not in a blend), a thinner sheet with its outer face where the plates' was, and
# drawn down onto two of the finger bones under it where it passes nearest them -- skin lying on the bones, not a plate
# hovering over them (t_isl2: it was 10 floating pieces, 13-19 cm off the body). On the leading finger as before.
import json, re, sys
import numpy as np
ROOTS = ("finger1", "finger3")
TH = 0.005
d = json.load(open(sys.argv[1]))
C = d['colors']
rgb = lambda h: [int(h[i:i + 2], 16) for i in (1, 3, 5)]
mem, memIn = rgb(C['mem']), rgb(C['memIn'])
TONE = round(sum(mem) / sum(memIn), 3)   # (the rim's darkness against the middle's)
sh = d['sculpt']['shape']
out_shapes, done = [], set()
for s in sh:
    m = re.match(r'wMemBCov([LR])(\d+)([cef])$', s['id'])
    if not m: out_shapes.append(s); continue
    S = m.group(1)
    if S in done: continue
    done.add(S)
    cov = {}
    for q in sh:
        mm = re.match(r'wMemBCov' + S + r'(\d+)([cef])$', q['id'])
        if mm: cov[(int(mm.group(1)), mm.group(2))] = q
    n = max(i for i, _ in cov) + 1
    cen = cov[(0, 'c')]['a']
    inn = [cov[(i, 'c')]['b'] for i in range(n)]
    out = [cov[(i, 'e')]['b'] for i in range(n)]
    for i in range(n):   # (the plates as manticore.py wrote them: c = cen, inn i, inn j; e = inn i, out i, out j; f = inn i, out j, inn j)
        j = (i + 1) % n
        assert cov[(i, 'c')]['c'] == inn[j] and cov[(i, 'e')]['c'] == out[j] and cov[(i, 'f')]['b'] == out[j], (S, i)
    th, bone = cov[(0, 'c')]['r'], cov[(0, 'c')]['bone']
    # points: 0 cen, 1..n inner ring (middle's colour), n+1..2n inner ring again (rim's), 2n+1..3n outer ring
    I1, I2, O = (lambda i: 1 + i), (lambda i: 1 + n + i), (lambda i: 1 + 2 * n + i)
    pts = [cen] + inn + inn + out
    tone = [1.0] * (1 + n) + [TONE] * (2 * n)
    tris = []
    for i in range(n):
        j = (i + 1) % n
        tris += [0, I1(i), I1(j), I2(i), O(i), O(j), I2(i), O(j), I2(j)]
    # THE ROOTS: the cover hovered ~1 cm over the bundle, touching nothing. Where it passes nearest two of the finger
    # bones under it, a point of its face is drawn down onto the bone (the face split about it, flat -- every point keeps
    # the cover's own normal, so it is lit exactly as before): a shallow pucker where the skin lies on the bone.
    cn = np.cross(np.subtract(inn[0], cen), np.subtract(inn[1], cen)); cn = cn / np.linalg.norm(cn)   # (the faces' own side)
    fingers = {q['id']: q for q in sh if re.match(r'finger\d$', q['id'])}
    sg = 1 if S == 'L' else -1
    def tri_of(pt):
        P = np.array(pts)
        for f in range(0, len(tris), 3):
            A, B, Cc = P[tris[f]], P[tris[f + 1]], P[tris[f + 2]]
            v0, v1, v2 = Cc - A, B - A, pt - A
            d00, d01, d11, d20, d21 = v0 @ v0, v0 @ v1, v1 @ v1, v2 @ v0, v2 @ v1
            den = d00 * d11 - d01 * d01; u = (d11 * d20 - d01 * d21) / den; v = (d00 * d21 - d01 * d20) / den
            if u >= .02 and v >= .02 and u + v <= .98: return f
        return None
    # (the sheet thinner -- 5 mm a side, not 11 -- its OUTER face kept where the plates' was, away from the bundle: the
    #  bones then reach both its faces where it is drawn down onto them)
    P0 = np.array(pts, float); hs = []
    for F in fingers.values():
        fa = np.array(F['a'], float); fa[2] *= sg; fb = np.array(F['b'], float); fb[2] *= sg
        hs.append(((fa + fb) / 2 - np.array(cen)) @ cn)
    out_side = -1.0 if np.mean(hs) > 0 else 1.0   # (the bundle on one side; the cover's outside the other)
    pts = (P0 + cn * out_side * (th - TH)).round(5).tolist(); cen = pts[0]
    roots = []
    for fid in ROOTS:
        F = fingers[fid]; fa = np.array(F['a'], float); fb = np.array(F['b'], float); fa[2] *= sg; fb[2] *= sg
        best = None
        for t in np.linspace(0, 1, 401):
            x = fa + (fb - fa) * t; r = F['ra'] + (F['rb'] - F['ra']) * t
            hgt = (x - np.array(cen)) @ cn; q = x - cn * hgt
            f = tri_of(q)
            if f is None: continue
            top = hgt + r if hgt < 0 else hgt - r   # (the bone's near side, toward the cover)
            if best is None or abs(top) < abs(best[0]): best = (top, q, f, t)
        top, q, f, t = best
        # (its outer face 2 mm into the bone's near side -- the inner face then within the bone too)
        p_ = q + cn * (top + (TH - .002 if top > 0 else .002 - TH))
        k = len(pts); pts.append([round(float(v), 5) for v in p_]); tone.append(tone[tris[f]] if tris[f] != 0 else 1.0)
        a_, b_, c_ = tris[f:f + 3]
        tone[k] = tone[b_]   # (the face's colour: its ring's)
        tris[f:f + 3] = [a_, b_, k]; tris += [b_, c_, k, c_, a_, k]
        roots.append((fid, round(float(t), 2), round(float(np.dot(p_ - q, cn)), 4)))
    nrm = [[round(float(v), 5) for v in cn]] * len(pts)
    print(S, 'ring', n, 'tone', TONE, 'roots (finger, along it, pucker m)', roots, file=sys.stderr)
    out_shapes.append({"id": "wHandCover" + S, "type": "membrane", "pts": pts, "tris": tris, "bones": [bone], "skin": [0] * len(pts),
                       "tone": tone, "nrm": nrm, "r": TH, "color": "@memIn"})
d['sculpt']['shape'] = out_shapes
json.dump(d, open(sys.argv[2], 'w'), indent=1)
