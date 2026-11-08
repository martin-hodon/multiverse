from sealib import *

# COMMON OCTOPUS (Octopus vulgaris): the mantle 16 cm, the arms 38 cm, spread about 0.9 m across
HZ = 0.6
R = Rig()
R.add("body", None, [0, 0, 0], shape={"shape": "sphere", "size": {"r": 0.05}})
R.add("mantle", "body", [-0.03, 0.03, 0], shape={"shape": "sphere", "size": {"r": 0.06}},
      anim={"axis": "z", "deg": 3, "speed": HZ * 0.5, "phase": 0})          # (the mantle swells and settles as it breathes)
C0 = [0.01, -0.04, 0]                        # (the arms' crown, under the head round the mouth)
SEG = [0.09, 0.085, 0.075, 0.068, 0.062]
RAD = [0.022, 0.017, 0.0128, 0.0094, 0.0066, 0.0042]
CURL = [-13, 5, 7, 8, 9]                     # (round 3b: the rise kept low -- the curl is sideways, below)
# (each bone's bend in the rest pose: out and down, then curling up -- 2026-11-07: gentler, an even spiral, not a hook)
NA = 8
arms, wigs = [], []
for i in range(NA):
    phi = 22.5 + 45 * i
    # (2026-11-07: each arm's sideways bend one way and growing toward the tip -- a spiral; alternating bends zig-zagged it)
    wig = [x * (1 if i % 2 else -1) * (1.0 + 0.25 * math.sin(2.3 * i)) for x in (0, 4, 9, 18, 30)]   # (round 3b: the tip's SPIRAL in the ground plane, the turn growing smoothly toward it)
    # (2026-11-07: the two arms trailing straight back run under the swept-up mantle -- curled like the rest, their
    # tips stood up behind it like a spike on the mantle; they trail low instead, only their tips turning)
    curl = CURL if math.cos(math.radians(phi)) > -0.6 else [-13, 5, 4, 5, 9]
    if math.cos(math.radians(phi)) < -0.6: wig = [-x for x in wig]   # (round 3b: the two trailing arms curl OUT, away from each other -- toward each other their tips crossed behind the mantle)
    pr = "body"
    ids = []
    for j in range(5):
        id = f"arm{i}{'abcde'[j]}"
        if j == 0:
            off = [C0[0] + 0.022 * math.cos(math.radians(phi)), C0[1], C0[2] - 0.022 * math.sin(math.radians(phi))]
            R.add(id, pr, off, rot=[0, phi, curl[0]], anim={"axis": "z", "deg": 4, "speed": HZ, "phase": -0.8 * i})
        else:
            R.add(id, pr, [SEG[j - 1], 0, 0], rot=[0, wig[j], curl[j]],
                  anim={"axis": "z" if j % 2 else "y", "deg": (6 + 2 * j) if j % 2 else (8 + 4 * j), "speed": HZ, "phase": -0.8 * i - 0.75 * j})
        ids.append(id); pr = id
    arms.append(ids); wigs.append(wig)

sh = [
    # the head (the eyes' bulges either side) and the MANTLE, a bulb swept up and back over it
    S("ell", id="head", c=[0.0, 0.0, 0], r=[0.05, 0.042, 0.052], k=0.012, color="@body", pat="mottle"),
    S("ell", id="mantle", bone="mantle", c=[-0.085, 0.07, 0], r=[0.098, 0.068, 0.072], rot=[0, 0, -37], k=0.02, color="@body", pat="mottle"),
    S("ell", id="neck", c=[-0.03, 0.03, 0], r=[0.05, 0.04, 0.05], k=0.015, color="@body", pat="mottle"),
    S("ell", id="eyebulge", c=[0.018, 0.028, 0.034], r=[0.022, 0.02, 0.018], k=0.01, color="@body", pat="mottle", mirror=True),
    S("ell", id="brow", c=[0.02, 0.046, 0.034], r=[0.009, 0.005, 0.006], k=0.004, color="@body", pat="mottle", mirror=True),   # (a papilla over each eye)
    # the siphon (the funnel), on the left under the mantle's rim
    S("tube", id="siphon", pts=[[-0.025, -0.012, 0.042, 0.011], [0.0, -0.022, 0.058, 0.008], [0.016, -0.03, 0.064, 0.006]], k=0.006, color="@body", pat="mottle"),
    S("ell", id="siphonmouth", c=[0.019, -0.031, 0.066], r=[0.004, 0.004, 0.004], k=0.002, color="@dark", op="sub"),
    S("ell", id="crown", c=[C0[0], C0[1] + 0.006, 0], r=[0.04, 0.02, 0.04], k=0.012, color="@body", pat="mottle"),
    S("ell", id="beak", c=[C0[0], C0[1] - 0.022, 0], r=[0.009, 0.009, 0.009], k=0.002, color="@dark", op="sub"),
]
# the EIGHT ARMS, tapering, each a chain of five bones, the SUCKERS in two staggered rows down the oral side of each
# (the coat pattern `suckers`, coatpat.js 30, laid along each bone)
def cr(p0, p1, p2, p3, t):
    return [.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in range(3)]
def tipw(b, w, L=0.03, pitch=10):
    """(round 3b) the point past the last bone's end, turned on by 1.2x the last joint's sideways turn: the spiral closes"""
    a, p = math.radians(1.2 * w), math.radians(pitch)
    return R.to_world(b, [SEG[-1] + L * math.cos(p) * math.cos(a), L * math.sin(p), -L * math.cos(p) * math.sin(a)])
for i, ids in enumerate(arms):
    # (the centreline: a smooth curve through the joints, so the arm bends evenly, not at elbows)
    P = [R.joint(id) for id in ids] + [R.to_world(ids[-1], [SEG[-1], 0, 0]), tipw(ids[-1], wigs[i][-1])]   # (the tip: on along the same spiral)
    P = [lerp(P[0], P[1], -0.3)] + P + [lerp(P[-2], P[-1], 1.5)]
    for j, id in enumerate(ids):
        q = [cr(P[j], P[j + 1], P[j + 2], P[j + 3], t) for t in (0, 1 / 3, 2 / 3, 1)]
        if j == 0: q[0] = lerp(q[0], q[1], -0.25)
        rr = [RAD[j] + (RAD[j + 1] - RAD[j]) * t for t in (0, 1 / 3, 2 / 3, 1)]
        u = norm(sub(q[-1], q[0])); v = norm(R.axis(id, [0, 1, 0]))
        fr = {"o": q[0], "u": u, "v": v, "r": (RAD[j] + RAD[j + 1]) / 2}
        sh.append(S("tube", id=f"arm{i}{j}", bone=id, pts=[qq + [r] for qq, r in zip(q, rr)], k=0.004 if j else 0.008, color="@body", pat="suckers", frame=fr))
    q = [cr(P[5], P[6], P[7], P[8], t) for t in (0, 0.5, 1)]
    sh.append(S("tube", id=f"tip{i}", bone=ids[-1], pts=[q[0] + [RAD[-1]], q[1] + [0.0038], q[2] + [0.0034]], k=0.002, color="@body"))
# THE WEB between the arms' bases: a fleshy slab from arm to arm, on the arms' first bones
for i in range(NA):
    A, B = arms[i][0], arms[(i + 1) % NA][0]
    pa = R.to_world(A, [0.0, 0, 0]); pb = R.to_world(B, [0.0, 0, 0])
    qa = R.to_world(A, [0.085, 0, 0]); qb = R.to_world(B, [0.085, 0, 0])
    mid = mul(add(qa, qb), 0.5)
    mid = add(mul(mid, 0.82), mul(C0, 0.18))
    sh.append(S("tri", id=f"web{i}a", bone=A, a=pa, b=qa, c=mid, r=0.0036, k=0.004, color="@body", pat="mottle"))
    sh.append(S("tri", id=f"web{i}b", bone=B, a=pb, b=mid, c=qb, r=0.0036, k=0.004, color="@body", pat="mottle"))
    sh.append(S("tri", id=f"web{i}c", a=pa, b=mid, c=pb, r=0.0036, k=0.004, color="@body", pat="mottle"))

d = {
    "name": "octopus",
    "_about": "SCULPTED (2026-11-05, docs/engines.md 'the sculpt overlay'): a common octopus, the mantle 16 cm and the arms 38 cm, spread 0.9 m -- the soft MANTLE a bulb swept up and back over the head, the eyes in bulges either side under a papilla each, the siphon on the left under the mantle's rim; EIGHT TAPERING ARMS round the mouth, each a chain of five bones (arm0a-e .. arm7a-e) bent out and down and curling up to fine tips, the SUCKERS in two staggered rows down each arm's pale oral side (the coat pattern `suckers`, coatpat.js 30, laid along each bone); the fleshy WEB slung between the arms' bases; red-brown and MOTTLED (the coat pattern `mottle`, coatpat.js 29). A SWIMMER (the fish's plumbing: `fly`, `alt` its depth; not put in the lake -- an animal of the sea). Each arm's bones bend a beat behind the one before (about z and y in turn), the arms out of step with each other: the arms WAVE and curl; the mantle breathes.",
    "kind": "parts",
    "facet": False,
    "flags": {"fly": {"alt": [0.2, 0.7], "speed": [0.1, 0.3], "hz": HZ}},
    "colors": {"body": "#a2603e", "dark": "#1a0c08"},
    "parts": R.parts,
    "sculpt": {
        "keep": [],
        "mesh": {"cell": 0.0024, "tris": [8400, 2600]},
        "shape": sh,
        "eyes": {"at": [0.03, 0.03, 0.05], "from": [0.012, 0.026, 0.02], "r": 0.0085, "color": "#0a0806", "iris": "#c8a868", "pupil": "bar", "lid": "@body", "sink": 0.45, "bone": "body"},
    },
}
write("octopus", keep_coats("octopus", d))
