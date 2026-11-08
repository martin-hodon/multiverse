import copy
from lib import *

# a BROWN BEAR: a barrel on four pillars -- the shoulder hump of digging muscle higher than the rump, thick short legs,
# plantigrade hind feet with long soles, long pale fore claws; a big broad head with a DISHED face (the forehead's bulge
# over a dip at the bridge, the muzzle running on to a black nose), small round ears high on the sides, small dark eyes;
# grizzled paler over the hump and nape, darker on the legs, a tan muzzle
def build():
    d = copy.deepcopy(orig("bear"))
    d.pop("sculpt", None)
    d["c"] = {**d["c"], "hump": "#82623f", "belly": "#5a3d24", "head": "#6a482c", "muzzle": "#86643f", "nose": "#16100c", "earIn": "#3a2616",
              "foot": "#3a2716", "claw": "#8c7a5c", "lid": "#1a120c", "eye": "#2a1a10", "cheek": "#74512f", "body": "#674629", "leg": "#4b331f"}
    d["tail"] = {**d["tail"], "c": [-1.06, 0.78], "R": 0.12, "a0": -0.5, "a1": -1.6, "r1": 0.055, "r2": 0.035}
    save("bear", d)
    J = joints("bear")
    Hd, No, Er = J["head"], J["nose"], J["earL"]
    h = lambda dx, dy, dz=0.0: [Hd[0] + dx, Hd[1] + dy, dz]
    SN = 0.045   # the snout 4.5 cm longer than the rig's
    n = lambda dx, dy, dz=0.0: [No[0] + dx + SN, No[1] + dy, dz]
    GR = {}   # (the leaf-mottle grizzle read as polka dots: dropped; the coat's tone is the sculpt's countershading -- shade -- instead)   # GRIZZLE: the leaf mottle, a patch a few cm across a shade darker
    F, E, P = J["legFLu"], J["legFLl"], J["footFL"]
    Hh, K, Q = J["legHLu"], J["legHLl"], J["footHL"]
    zF, zH = F[2], Hh[2]
    S = []
    def sh(**k): S.append(k)
    # the trunk
    sh(id="chest", **GR, type="ell", c=[0.42, 0.78, 0], r=[0.5, 0.34, 0.35], k=0.14, color="@body")
    sh(id="barrel", **GR, type="ell", c=[-0.05, 0.77, 0], r=[0.55, 0.33, 0.37], k=0.14, color="@body")
    sh(id="hump", type="ell", c=[0.5, 1.02, 0], r=[0.34, 0.17, 0.26], rot=[0, 0, -6], k=0.16, kc=0.3, color="@hump", hair=1, **GR)
    sh(id="belly", type="ell", c=[0.0, 0.54, 0], r=[0.45, 0.12, 0.29], k=0.1, color="@belly")
    sh(id="rump", **GR, type="ell", c=[-0.56, 0.79, 0], r=[0.36, 0.3, 0.33], k=0.12, color="@body")
    sh(id="scapula", type="ell", c=[0.56, 0.86, 0.22], r=[0.13, 0.22, 0.1], rot=[0, 0, 15], k=0.1, color="@body", mirror=True)
    # forelegs: columns on broad paws, long claws
    sh(id="arm", type="tube", bone="legFLu", pts=[[F[0] + 0.05, 0.7, zF - 0.02, 0.165], [F[0] + 0.02, 0.48, zF - 0.01, 0.15], [E[0], E[1] + 0.02, zF, 0.13]], k=0.08, color="@body", mirror=True)
    sh(id="forearm", type="cone", bone="legFLl", a=[E[0], E[1] + 0.01, zF], b=[P[0] - 0.035, 0.11, zF], ra=0.128, rb=0.1, k=0.05, color="@leg", mirror=True)
    sh(id="paw", type="ell", bone="footFL", c=[P[0] + 0.035, 0.055, zF], r=[0.145, 0.055, 0.115], k=0.04, color="@foot", mirror=True)
    for i, dz in enumerate((-0.06, -0.02, 0.02, 0.06)):
        # (one tube from inside the paw out and down to the point: a single piece, no gap between root and tip)
        sh(id=f"claw{i}", type="tube", bone="footFL", pts=[[P[0] + 0.11, 0.062, zF + dz * 0.96, 0.0175], [P[0] + 0.19, 0.045, zF + dz * 1.08, 0.011], [P[0] + 0.228, 0.01, zF + dz * 1.12, 0.003]],
           k=0.003, kc=0.001, color="@claw", mirror=True)
    # hind legs: a heavy thigh, a short shin, the long flat sole
    sh(id="thigh", type="ell", bone="legHLu", c=[Hh[0] - 0.02, 0.6, zH + 0.01], r=[0.23, 0.29, 0.16], rot=[0, 0, 10], k=0.08, color="@body", mirror=True)
    sh(id="gaskin", type="cone", bone="legHLu", a=[Hh[0], 0.46, zH], b=[K[0] - 0.01, K[1] + 0.01, zH], ra=0.145, rb=0.115, k=0.06, color="@leg", mirror=True)
    sh(id="shin", type="cone", bone="legHLl", a=[K[0] - 0.01, K[1], zH], b=[Q[0] - 0.04, 0.09, zH], ra=0.113, rb=0.095, k=0.05, color="@leg", mirror=True)
    sh(id="hpaw", type="ell", bone="footHL", c=[Q[0] + 0.04, 0.05, zH], r=[0.18, 0.05, 0.105], k=0.04, color="@foot", mirror=True)
    for i, dz in enumerate((-0.05, 0.0, 0.05)):
        sh(id=f"hclaw{i}", type="cone", bone="footHL", a=[Q[0] + 0.19, 0.04, zH + dz], b=[Q[0] + 0.235, 0.014, zH + dz], ra=0.011, rb=0.003, k=0.003, kc=0.001, color="@claw", mirror=True)
    # the neck: short and thick, its nape grizzled
    sh(id="neck", type="ell", bone="neck", c=[0.86, 0.92, 0], r=[0.3, 0.25, 0.25], rot=[0, 0, 22], k=0.12, color="@body")
    sh(id="nape", type="ell", bone="neck", c=[0.8, 1.05, 0], r=[0.22, 0.12, 0.2], rot=[0, 0, 12], k=0.1, kc=0.25, color="@hump", hair=1, **GR)
    # the head: broad, the dish of its profile between the forehead's bulge and the nose
    sh(id="cranium", type="ell", bone="head", c=h(-0.02, 0.02), r=[0.165, 0.135, 0.18], k=0.06, color="@head", **GR)
    sh(id="forehead", type="ell", bone="head", c=h(0.07, 0.09), r=[0.095, 0.072, 0.125], k=0.04, color="@head")
    sh(id="cheek", type="ell", bone="head", c=h(-0.01, -0.035, 0.11), r=[0.12, 0.11, 0.09], k=0.05, color="@cheek", mirror=True, **GR)
    sh(id="ruffC", type="ell", bone="head", c=h(-0.08, -0.05, 0.12), r=[0.08, 0.13, 0.08], rot=[-15, 0, 10], k=0.05, kc=0.04, color="@cheek", mirror=True, hair=1)
    sh(id="bridge", type="cone", bone="head", a=h(0.15, 0.012), b=n(-0.035, 0.022), ra=0.05, rb=0.044, k=0.025, color="@muzzle")
    sh(id="muzzle", type="cone", bone="head", a=h(0.08, -0.008), b=n(-0.04, -0.012), ra=0.092, rb=0.064, k=0.04, color="@muzzle")
    sh(id="jaw", type="cone", bone="head", a=h(0.03, -0.08), b=n(-0.06, -0.058), ra=0.07, rb=0.045, k=0.035, color="@muzzle")
    sh(id="nose", type="ell", bone="head", c=n(-0.003, 0.0), r=[0.034, 0.03, 0.044], k=0.008, kc=0.003, color="@nose", wet=0.3)
    sh(id="ear", type="ell", bone="earL", c=[Er[0] - 0.015, Er[1] + 0.045, Er[2] + 0.035], r=[0.032, 0.05, 0.052], rot=[-25, 0, 0], k=0.02, kc=0.006, color="@ear", mirror=True)
    sh(id="earIn", type="ell", bone="earL", c=[Er[0] + 0.004, Er[1] + 0.045, Er[2] + 0.037], r=[0.012, 0.033, 0.034], rot=[-25, 0, 0], k=0.006, kc=0.002, color="@earIn", mirror=True)
    eyes = {"at": h(0.115, 0.05, 0.068), "from": h(0.0, 0.03, 0), "r": 0.0135, "iris": "@eye", "pupil": "round", "lid": "@lid", "sink": 0.35}
    # the HEAD bigger (a fifth of the body's length): its shapes scaled about the head joint, the eyes with them
    HS = 1.14
    def big(p): return [Hd[0] + (p[0] - Hd[0]) * HS + 0.03, Hd[1] + (p[1] - Hd[1]) * HS, p[2] * HS]
    for q in S:
        if q.get("bone") not in ("head", "earL"): continue
        if q["bone"] == "earL":   # (the ears ride out with the bigger skull, their own size kept)
            q["c"] = big(q["c"]); continue
        for kk in ("c", "a", "b"):
            if kk in q: q[kk] = big(q[kk])
        for kk in ("ra", "rb", "k", "kc"):
            if kk in q: q[kk] = q[kk] * HS
        if "r" in q: q["r"] = [x * HS for x in q["r"]] if isinstance(q["r"], list) else q["r"] * HS
    eyes["at"] = big(eyes["at"]); eyes["from"] = big(eyes["from"]); eyes["r"] *= 1.08
    # (audit 2026-11-07: the coat read as smooth plastic -- TICKED fur, coatpat.js agouti, on every furred shape)
    for q in S:
        if q.get("color") in ("@body", "@hump", "@belly", "@leg", "@head", "@cheek", "@muzzle", "@foot"): q["pat"] = "agouti"
        # (round 2: still plastic -- the long guard hairs: coatpat's COARSE strands over the body, hump, head and legs)
        if q.get("color") in ("@body", "@hump", "@leg", "@head", "@cheek"): q["pat"] = "coarse"
    out = {"name": "bear",
           "_about": "a brown bear SCULPTED on its rig (2026-11-05, gen: scratchpad sc/carn/gen/bear.py): a barrel on four pillars, the shoulder hump higher than the rump, plantigrade hind feet on long soles, long pale fore claws; a broad head with a dished face, small round ears high on its sides, small dark eyes; grizzled over the hump and nape, darker legs, a tan muzzle"}
    out.update({k: v for k, v in d.items() if k not in ("name", "_about")})
    out["sculpt"] = {"keep": ["tail\\d*"], "mesh": {"tris": [8000, 2500]}, "shape": S, "eyes": eyes,
                      "shade": {"back": 1.12, "belly": 0.86, "low": 0.82, "on": "@body"}}
    # (audit 2026-11-07) COATS, picked by seed: the Eurasian brown (as written), the silver-tipped GRIZZLY, the dark-brown
    # Syrian-to-Kamchatka "black-brown"; and VARIANTS by name: the American BLACK BEAR (smaller, black with a tan muzzle) and
    # the POLAR BEAR (larger, cream-white, a black nose)
    out["coats"] = [{"name": "brown"},
                    {"name": "grizzly", "body": "#6a4c32", "hump": "#b0946a", "head": "#8c6e4c", "cheek": "#9c7e58", "belly": "#4e3824",
                     "leg": "#3e2a1a", "foot": "#2e2014", "muzzle": "#a88a62"},
                    {"name": "dark brown", "body": "#3e2a1a", "hump": "#4e3622", "head": "#422c1c", "cheek": "#4a3220", "belly": "#33231a",
                     "leg": "#2a1c12", "foot": "#22170f", "muzzle": "#6e5236", "ear": "#33231a"}]
    out["variants"] = {
        "black": {"scale": 0.72, "colors": {"body": "#1d1a18", "hump": "#24201c", "head": "#201c1a", "cheek": "#25201c", "belly": "#191614",
                                            "leg": "#141210", "foot": "#121010", "muzzle": "#9c7650", "ear": "#191614", "earIn": "#141210", "tail": "#191614"}},
        "polar": {"scale": 1.1, "colors": {"body": "#e6e0d0", "hump": "#ebe5d6", "head": "#ece6d8", "cheek": "#e8e2d2", "belly": "#d6cfbe",
                                           "leg": "#dcd5c3", "foot": "#d2cab8", "muzzle": "#e9e3d4", "ear": "#e0d9c8", "earIn": "#c4bba8",
                                           "tail": "#e0d9c8", "nose": "#0e0c0c", "claw": "#3a342e"}}}
    save("bear", out)

build()
