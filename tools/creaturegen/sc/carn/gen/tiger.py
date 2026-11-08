# NOTE (2026-11-07, sky-steeds/mammal agent): assets/creatures/mammals/tiger.json is FINISHED DOWNSTREAM of this script --
# scratchpad var/tgr.py takes its output (kept as var/tiger_r1.json) and transplants the lion's skull and face, the white
# cheek ruffs, body-frame stripes and lion toe lobes. Regenerating here alone reverts those: run var/tgr.py on the output after.
import copy, math
from lib import *

# THE TIGER, retouched (2026-11-05, review pass): the face's markings (black forehead bars, the white spot over each eye),
# the bridge and upper muzzle orange with the white kept to the whisker pads, chin and cheek ruff, a smaller jowl and
# throat (they stood out face-on as a white ball), broader stripes, black ear backs with their white spot, black rings
# over the tail's last third. MARKS are DECALS: small shapes SEATED on the surface the others make (bodyspec seat) and
# sunk in so only a cap a few mm proud shows -- paint that goes where the surface is, whatever the blend made of it.
def decal(id, bone, at, frm, r, color, out=None, rot=None, mirror=True, k=0.003, sink=0.55):
    # (seat's offset is x the shape's LARGEST radius: sunk by `sink` of its smallest, so a cap of it stays proud)
    if out is None: out = -sink * (min(r) / max(r) if isinstance(r, list) else 1.0)
    s = {"id": id, "type": "ell" if isinstance(r, list) else "sphere", "bone": bone, "c": at, "r": r, "k": k, "kc": 0.0015, "color": color,
         "seat": {"from": frm, "out": out}}
    if rot: s["rot"] = rot
    if mirror: s["mirror"] = True
    return s

def bez(A, C, B, t):
    return [(1 - t) ** 2 * A[i] + 2 * t * (1 - t) * C[i] + t * t * B[i] for i in range(2)]
def bezd(A, C, B, t):
    return [2 * (1 - t) * (C[i] - A[i]) + 2 * t * (B[i] - C[i]) for i in range(2)]

def tail_rings(J, tube_pts, rings, color="@black", grow=0.005):
    """rings round a kept tail tube: ell bands centred on its curve, thin along it"""
    A, C, B, r1, r2, bone = tube_pts
    out = []
    for i, (t, w) in enumerate(rings):
        P = bez(A, C, B, t); d = bezd(A, C, B, t); ang = math.degrees(math.atan2(d[1], d[0]))
        R = r1 + (r2 - r1) * t + grow
        out.append({"id": f"tailRing{i}", "type": "ell", "bone": bone, "c": [P[0], P[1], 0], "r": [w, R, R], "rot": [0, 0, ang], "k": 0.004, "kc": 0.002, "color": color})
    return out

def sculpt_tail(tubes, n=10):
    out = []
    for (A, B, C, r1, r2, bone, black) in tubes:
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            P0, P1 = bez(A, C, B, t0), bez(A, C, B, t1)
            tm = (t0 + t1) / 2
            dark = any(a <= tm < b for a, b in black)
            # (the black bands cut by their own small segments, so a ring's edges fall where the band says)
            out.append(dict({"id": f"{bone}Seg{i}", "type": "cone", "bone": bone, "a": [P0[0], P0[1], 0], "b": [P1[0], P1[1], 0],
                             "ra": r1 + (r2 - r1) * t0, "rb": r1 + (r2 - r1) * t1, "k": 0.012, "kc": 0.003},
                            **({"color": "@black"} if dark else {"color": "@tail", "pat": "stripes", "frame": {"o": [P0[0], P0[1], 0], "u": [P1[0] - P0[0], P1[1] - P0[1], 0], "r": 0.05}})))
    return out

def tube_ctrl(A, B, cl):
    """a rig tube's control point in root space (its local frame: y along the chord, x the chord turned +90 deg)"""
    d = [B[0] - A[0], B[1] - A[1]]; L = math.hypot(*d); y = [d[0] / L, d[1] / L]; x = [y[1], -y[0]]
    if x[1] < 0 and cl[0] > 0: pass
    return [A[0] + cl[1] * y[0] + cl[0] * x[0], A[1] + cl[1] * y[1] + cl[0] * x[1]]

def build():
    d = copy.deepcopy(orig("tiger"))
    S = d["sculpt"]["shape"]
    by = {s["id"]: s for s in S}
    # the white kept to the pads, chin and the cheek ruff: a smaller, tighter-edged pad; the jowl and throat drawn in
    by["pad"].update(r=[0.044, 0.035, 0.04], kc=0.006)
    by["chin"].update(kc=0.006)
    by["jowl"].update(c=[0.955, 0.94, 0.0], r=[0.11, 0.052, 0.085], kc=0.012)
    by["throat"].update(c=[0.77, 0.84, 0.0], r=[0.16, 0.085, 0.105], kc=0.03)
    by["muzzle"].update(kc=0.006)
    # the white spot over the eye: a spot, not a brow
    S.remove(by["brow"])
    # the ears: black behind, the white spot on the back (below)
    by["ear"].update(color="@black")
    J = joints("tiger")
    H = J["head"]
    hb = [0.95, 1.06, 0.0]
    add = [
        # the FOREHEAD, striped: a cone over the upper half of the bridge, in the skull's own frame -- the bars per pixel
        {"id": "forehead", "type": "cone", "bone": "head", "a": [1.0, 1.094, 0.0], "b": [1.093, 1.064, 0.0], "ra": 0.07, "rb": 0.057, "k": 0.02, "kc": 0.008,
         "color": "@body", "pat": "stripes", "frame": {"o": "$head", "u": [0, 1, 0], "v": [1, 0, 0], "r": 0.11}},
        # the white spot over each eye
        decal("eyeSpot", "head", [1.05, 1.135, 0.055], hb, [0.028, 0.018, 0.026], "@white", rot=[0, 0, 20], sink=0.6),
        # the white spot on the back of each ear
        decal("earSpot", "earL", [0.87, 1.185, 0.094], [0.9, 1.18, 0.094], 0.014, "@white"),
    ]
    # THE TAIL sculpted (the rig's tubes were drawn as shells beside the body: nothing could be laid on them): cones down
    # its two links' curves (the control on the arc's OUTER side, as the rig's own tubes bow: a smooth U, no V at the joint), striped (rings, on a part this thin), the last third ringed black, the tip black
    A0, B0, A1, B1 = J["tail"], J["tail1"], J["tail1"], J["tailTuft"]
    add += sculpt_tail([(A0, B0, tube_ctrl(A0, B0, [-0.1275, 0.2623]), 0.068, 0.059, "tail", []),
                        (A1, B1, tube_ctrl(A1, B1, [-0.1275, 0.2623]), 0.059, 0.05, "tail1", [(0.3, 0.4), (0.52, 0.62), (0.73, 0.83), (0.91, 1.0)])])
    # THE TAIL ROOT as thick as the sacrum's base: a croup cone on the body tapering into the tail, and the tail's first
    # 20 cm on its own bone tapering from that girth to the tail's (no pinch, no elbow where it leaves the rump)
    add += [{"id": "croup", "type": "cone", "a": [-0.84, 0.84, 0.0], "b": [-0.98, 0.83, 0.0], "ra": 0.12, "rb": 0.095, "k": 0.06, "kc": 0.03,
             "color": "@body", "pat": "stripes", "frame": "body"},
            {"id": "tailRoot", "type": "cone", "bone": "tail", "a": [-0.95, 0.835, 0.0], "b": [-1.125, 0.69, 0.0], "ra": 0.09, "rb": 0.066, "k": 0.05, "kc": 0.02,
             "color": "@body", "pat": "stripes", "frame": {"o": [-0.95, 0.835, 0.0], "u": [-0.175, -0.145, 0.0], "r": 0.05}}]
    add.append({"id": "tailTip", "type": "sphere", "bone": "tail1", "c": [B1[0] - 0.01, B1[1], 0], "r": 0.05, "k": 0.02, "kc": 0.003, "color": "@black"})
    d["sculpt"]["keep"] = []
    S += add
    # THE HEAD PASS (felid.py head_pass): eyes set in under a brow ridge, almond corners, a faint tear line, a flatter muzzle
    from felid import head_pass
    d["sculpt"]["shape"] = S = head_pass(S, d["sculpt"]["eyes"], lambda p: list(p), 1.0,
                                         {"tear": "@tear", "tearW": 0.006, "ears": 0.88, "earZ": 0.016, "earY": -0.01, "nose": 0.82, "eyeBall": "#6e4e14", "snout": 0.008})
    tbl = "colors" if "colors" in d else "c"
    d[tbl] = {**d[tbl], "tear": "#6a3a16"}
    d["sculpt"]["mesh"] = {"tris": [10000, 3000]}
    d["patScale"] = 1.28
    d["_about"] = d["_about"] + " (2026-11-05 review pass, gen: scratchpad sc/carn/gen/tiger.py: the face's markings as seated decals, broader stripes -- patScale 1.28 -- black ear backs with their white spot, ringed tail end, a smaller white jowl and throat)"
    save("tiger", d)
build()
