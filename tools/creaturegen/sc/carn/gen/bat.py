import math
from lib import *

# A BAT (a big-eared microbat at the size the world flies it: 15 cm head-body, 55 cm span): a furry body, a short
# face, small eyes, big ears; the WING as a bat's is made -- the arm to the wrist, three long fingers fanned from the
# hand and the skin stretched between them and back to the flank (mammals.js batWing's anatomy, here at rest SPREAD,
# as it flies: the world's bats are always aloft), flapping on the flier's clock
def hx(c): return int(c[1:], 16)
C = {"body": "#5b4433", "front": "#7a5c44", "belly": "#6c523e", "head": "#4e3a2c", "muzzle": "#5e4434", "ear": "#3a2a24", "earIn": "#6e4c42",
     "nose": "#33231f", "mem": "#5e463e", "bone": "#2a201c", "eye": "#3c2a1e", "lid": "#1a120e", "foot": "#2e221e"}

def wing(s, k, at, deg=40, speed=5, scallop=0.3):
    S = "L" if s > 0 else "R"
    E, LD = 1.08 * k, 1.0 * k
    F = [(a, L * k) for a, L in ((3, 1.1), (20, 1.16), (44, 1.0), (70, 0.88))]
    T = [[-math.sin(math.radians(a)) * L, math.cos(math.radians(a)) * L, 0] for a, L in F]
    mem, bone = hx(C["mem"]), hx(C["bone"])
    tri = lambda id, par, a, b, c: {"id": id, "parent": par, "shape": "tri", "size": {"a": a, "b": b, "c": c, "r": 0.006 * k}, "pos": [0, 0, 0], "color": mem, "edge": 0}
    # THE TRAILING EDGE of the arm's skin: from the fifth finger's tip back to the ankle, CONCAVE (bowed in toward the arm);
    # the seam where the hand's panel meets the arm's a quarter of the way along it
    Hh = [0, E, 0]
    T3a = [Hh[0] + T[3][0], Hh[1] + T[3][1], 0]
    A = [-1.05 * k, -0.2 * k, 0]
    def edge(t): return [T3a[0] + (A[0] - T3a[0]) * t + 0.3 * k * math.sin(math.pi * t), T3a[1] + (A[1] - T3a[1]) * t, 0.06 * k * math.sin(math.pi * t)]
    ts = [0.25, 0.42, 0.58, 0.74, 0.88, 1.0]
    Sm = edge(ts[0])
    out = [
        {"id": f"wArm{S}", "parent": "body", "shape": "capsule", "size": {"r": 0.02 * k, "len": 1.1 * k}, "pos": [at[0], at[1], s * at[2]], "rot": [s * 84, 0, -10],
         "pivot": [0, 0.55 * k, 0], "color": bone, "edge": 0, "anim": {"axis": "x", "deg": s * deg, "speed": speed, "phase": 0, "wing": True}, "fold": [s * 118, 0, 70]},
        {"id": f"wHand{S}", "parent": f"wArm{S}", "shape": "sphere", "size": {"r": 0.026 * k}, "pos": [0, E, 0], "rot": [s * 4, 0, 0], "color": bone, "edge": 0,
         "anim": {"axis": "x", "deg": s * deg * 0.55, "speed": speed, "phase": 0.6, "wing": True}, "fold": [-s * 4, 0, 0]},
    ]
    # the arm's skin: a fan of quads from the arm to the bowed edge (arm points from the wrist down to the shoulder) in TWO
    # rows, the skin BILLOWED: its camber peaking inside the panel, falling to the taut edge and to nothing at the bone
    CA = 0.16 * k
    def mid(R, P, t, c): return [R[0] + (P[0] - R[0]) * 0.55, R[1] + (P[1] - R[1]) * 0.55, c * math.sin(math.pi * t)]
    for i in range(len(ts) - 1):
        y0, y1 = E * (1 - i / (len(ts) - 1)), E * (1 - (i + 1) / (len(ts) - 1))
        R0, R1 = [0, y0, 0], [0, y1, 0]
        P0, P1 = edge(ts[i]), edge(ts[i + 1])
        P0[2], P1[2] = 0.4 * CA * math.sin(math.pi * ts[i]), 0.4 * CA * math.sin(math.pi * ts[i + 1])
        u0, u1 = i / (len(ts) - 1), (i + 1) / (len(ts) - 1)
        M0, M1 = mid(R0, P0, 0.15 + 0.85 * u0, CA), mid(R1, P1, 0.15 + 0.85 * u1, CA)
        out += [tri(f"wMemA{i}{S}", f"wArm{S}", R0, M0, M1), tri(f"wMemA{i}b{S}", f"wArm{S}", R0, M1, R1),
                tri(f"wMemA{i}c{S}", f"wArm{S}", M0, P0, P1), tri(f"wMemA{i}d{S}", f"wArm{S}", M0, P1, M1)]
    for i, (a, L) in enumerate(F):
        out.append({"id": f"wFinger{i}{S}", "parent": f"wHand{S}", "shape": "capsule", "size": {"r": 0.011 * k, "r2": 0.006 * k, "len": L}, "pos": [0, 0, 0],
                    "rot": [0, 0, a], "pivot": [0, L / 2, 0], "color": bone, "edge": 0})
    # each panel between two digits a FAN from the hand to its trailing edge, the edge a CONCAVE scallop (a smooth bow in
    # toward the hand between the fingertips, not a V notch), the skin billowed a little out of the plane (camber)
    def panel(nm, P, Q, sc, n=5, cam=0.12):
        E2, M2 = [], []
        for j in range(n + 1):
            t = j / n; f = 1 - sc * math.sin(math.pi * t); b = math.sin(math.pi * t)
            e = [(P[q] + (Q[q] - P[q]) * t) * f for q in range(2)]
            E2.append(e + [0.35 * cam * k * b])
            M2.append([e[0] * 0.55, e[1] * 0.55, cam * k * b])   # (the billow's crest, inside the skin)
        out = []
        for j in range(n):
            out += [tri(f"{nm}{j}{S}", f"wHand{S}", [0, 0, 0], M2[j], M2[j + 1]),
                    tri(f"{nm}{j}m{S}", f"wHand{S}", M2[j], E2[j], E2[j + 1]), tri(f"{nm}{j}n{S}", f"wHand{S}", M2[j], E2[j + 1], M2[j + 1])]
        return out
    for i, (P, Q) in enumerate(((T[0], T[1]), (T[1], T[2]), (T[2], T[3]))):
        out += panel(f"wMemB{i}_", P, Q, 0.04 if i == 0 else scallop, cam=0.05 if i == 0 else 0.12)   # (the leading edge's skin, digits 2-3, taut)
    # the fifth finger's panel: its tip to the seam on the bowed edge, scalloped between
    Sh = [Sm[0] - Hh[0], Sm[1] - Hh[1], Sm[2]]
    out += panel("wMemB3_", T[3], Sh, scallop * 0.6)
    out.append({"id": f"wClaw{S}", "parent": f"wHand{S}", "shape": "cone", "size": {"r": 0.03 * k, "h": 0.16 * k}, "pos": [0.03 * k, 0.05 * k, 0], "rot": [0, 0, -50], "color": bone, "edge": 0})
    return out

def build():
    d = orig("bat")
    B = [0, 0.334, 0]
    hp = [0.064, 0.01, 0]
    H = [B[i] + hp[i] for i in range(3)]
    parts = []
    for p in d["parts"]:
        if p["id"] in ("wingL", "wingR"): continue
        p = dict(p)
        if p["id"] == "body": p["color"] = hx(C["body"])
        if p["id"] == "head": p.update(pos=hp, size={"r": 0.024}, color=hx(C["head"]))
        if p["id"] in ("earL", "earR"):
            s = 1 if p["id"] == "earL" else -1
            p.update(pos=[-0.004, 0.014, s * 0.01], size={"r": 0.011, "h": 0.036}, rot=[s * 20, 0, 8], color=hx(C["ear"]))
        if p["id"] in ("eyeL", "eyeR"): continue
        parts.append(p)
    k = 0.115
    for s in (1, -1): parts += wing(s, k, [0.025, 0.012, 0.02])
    h = lambda dx, dy, dz=0.0: [H[0] + dx, H[1] + dy, H[2] + dz]
    b = lambda dx, dy, dz=0.0: [B[0] + dx, B[1] + dy, B[2] + dz]
    S = [
        # the body: a furry barrel, the chest broad where the wings work, paler before
        {"id": "torso", "type": "ell", "c": b(0.004, 0.002), "r": [0.05, 0.028, 0.03], "k": 0.012, "color": "@body"},
        {"id": "chest", "type": "ell", "c": b(0.028, -0.006), "r": [0.03, 0.022, 0.03], "k": 0.012, "color": "@front"},
        {"id": "belly", "type": "ell", "c": b(-0.015, -0.01), "r": [0.035, 0.016, 0.022], "k": 0.01, "color": "@belly"},
        {"id": "ruff", "type": "ell", "c": b(0.046, 0.0), "r": [0.02, 0.02, 0.024], "k": 0.01, "color": "@body"},
        # the hind legs, the knees turned out, and the tail-skin between them
        {"id": "hleg", "type": "cone", "a": b(-0.04, -0.008, 0.016), "b": b(-0.07, -0.016, 0.03), "ra": 0.0065, "rb": 0.004, "k": 0.004, "color": "@bone", "mirror": True},
        {"id": "hfoot", "type": "ell", "c": b(-0.075, -0.017, 0.032), "r": [0.007, 0.003, 0.004], "k": 0.002, "color": "@foot", "mirror": True},
        {"id": "uropat", "type": "tri", "a": b(-0.068, -0.014, 0.028), "b": b(-0.068, -0.014, -0.028), "c": b(-0.1, -0.012, 0), "r": 0.003, "color": "@mem"},
        # the head: a round skull, a short pug snout, a black nose; big ears
        {"id": "skull", "type": "ell", "bone": "head", "c": h(-0.002, 0.003), "r": [0.021, 0.018, 0.019], "k": 0.008, "color": "@head"},
        {"id": "snout", "type": "cone", "bone": "head", "a": h(0.008, -0.002), "b": h(0.027, -0.006), "ra": 0.012, "rb": 0.008, "k": 0.005, "color": "@muzzle"},
        {"id": "cheek", "type": "ell", "bone": "head", "c": h(0.01, -0.006, 0.01), "r": [0.012, 0.01, 0.008], "k": 0.004, "color": "@muzzle", "mirror": True},
        {"id": "nose", "type": "ell", "bone": "head", "c": h(0.029, -0.005), "r": [0.0035, 0.005, 0.0075], "k": 0.002, "kc": 0.001, "color": "@nose", "wet": 0.12},
        {"id": "jaw", "type": "ell", "bone": "head", "c": h(0.014, -0.013), "r": [0.012, 0.005, 0.008], "k": 0.003, "color": "@muzzle"},
        {"id": "ear", "type": "cone", "bone": "earL", "a": h(-0.004, 0.012, 0.011), "b": h(-0.009, 0.05, 0.026), "ra": 0.012, "rb": 0.0025, "k": 0.004, "kc": 0.001, "color": "@ear", "mirror": True},
        {"id": "earIn", "type": "ell", "bone": "earL", "c": h(0.0, 0.03, 0.0185), "r": [0.0025, 0.014, 0.007], "rot": [-22, -20, 6], "k": 0.0015, "kc": 0.0008, "color": "@earIn", "mirror": True},
    ]
    eyes = {"at": h(0.017, 0.006, 0.012), "from": h(0.0, 0.004, 0.0), "r": 0.003, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.6, "socket": 1.06, "color": "#0e0a08"}
    out = {"name": "bat",
           "_about": "a bat SCULPTED on its parts (2026-11-05, gen: scratchpad sc/carn/gen/bat.py): a big-eared microbat, 15 cm head-body, 55 cm across the wings -- a furry barrel paler before, a short pug face, small eyes, big ears; each wing as a bat's is made (mammals.js batWing): the arm to the wrist, three long fingers fanned from the hand, the skin stretched between them and back to the flank and the hind legs, spread as it flies and beating on the flier's clock",
           "kind": "parts", "flags": d["flags"], "c": C, "parts": parts,
           "sculpt": {"keep": ["w[A-Z].*"], "mesh": {"tris": [5000, 1300], "focus": {"head": 5}}, "shape": S, "eyes": eyes}}
    save("bat", out)

build()
