# desmatosuchus.py -- writes assets/creatures/dinosaurs/desmatosuchus.json (2026-11-08): DESMATOSUCHUS SPURENSIS, a late
# Triassic AETOSAUR (a pseudosuchian archosaur, on the crocodiles' side -- not a dinosaur), 4.5 m long, about a metre at
# the hips, a heavily armoured herbivore.
# Run: python3 tools/creaturegen/prehistoric/desmatosuchus.py   (two passes, like dimetrodon.py: the body bare, its skin
# probed through sharp/fd.mjs, then the armour rooted on it). The species must be listed in assets/index.json.
# Rig ("parts", the wall lizard's plan): body (the trunk, rigid under its armour) -> head (pivot at the neck's root: the
# neck rides it); body -> caud1..4 (the tail, a small swing: an armoured tail is stiff); semi-erect legs (the upper bone
# down and out, the lower down; a lift on the forward swing).
# THE ARMOUR: rows of rectangular OSTEODERMS, each a `fin` PLATE laid on the skin -- its root along its front edge just
# under the skin, its rim the exact rectangle (the two rear corners `corners`), the rear edge standing proud so each row
# overlaps the next like tiles; a slab (thick 16 mm, steep `slope`: flat with a crisp edge), a dark band round its rim so
# the rows read. Each row one sheet a side (MERGE: paramedian -- the flat top of the back -- and lateral -- down the flank's
# shoulder, bent over it with the skin -- as one plate, half the details; MERGE False writes them as two) -- from behind the skull down the neck, over the trunk and
# round the tail to near its tip, narrower and shorter toward it. Probed on the field (rays out from the body's axis at
# angles round it) so each lies on the skin.
# SPIKES (`horn`s, faired into the skin, rising through their lateral plates): along the neck growing back, from a knob
# to 20 cm; the great SHOULDER SPIKE (45 cm, broad and flattened at its root) out from the last cervical row, rising
# out (~60 deg from the midline) and up (~35 deg), then sweeping back -- above the back's line in profile; short keels on every other lateral of the trunk and the tail's root.
# The HEAD small and low: a SHORT deep snout, its blunt tip UPTURNED into a spade (a pig's), the nostrils on it, small
# leaf-shaped teeth (horns, compressed); the eye small. Dull grey-brown and ochre, the plates' rims dark.
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rept import *

SP = "dinosaurs/desmatosuchus"
OUT = SP + ".json"

B = [0.0, 0.64, 0]
HD = [0.74, 0.66, 0]
TX = [-0.62, -1.15, -1.70, -2.25]
TIP = -2.95
YT = [(-0.50, 0.68), (-0.90, 0.63), (-1.30, 0.55), (-1.70, 0.45), (-2.10, 0.36), (-2.50, 0.28), (TIP, 0.2)]
RT = [(-0.50, 0.28), (-0.90, 0.225), (-1.30, 0.175), (-1.70, 0.13), (-2.10, 0.09), (-2.50, 0.056), (-2.80, 0.03), (TIP, 0.008)]
ty = lambda x: interp(YT, x)
tr = lambda x: interp(RT, x)
# the neck's axis (on the head bone), x -> (y, r)
NK = [(0.60, 0.68, 0.24), (0.80, 0.665, 0.19), (1.00, 0.635, 0.15), (1.17, 0.61, 0.125)]
ny = lambda x: interp([(a, b) for a, b, c in NK], x)
FS, FE, FW = [0.52, 0.52, 0.22], [0.45, 0.26, 0.42], [0.52, 0.07, 0.4]
HH, HK, HA = [-0.42, 0.56, 0.22], [-0.31, 0.27, 0.44], [-0.44, 0.08, 0.42]
HAND = nrm([math.cos(math.radians(15)), 0, math.sin(math.radians(15))])
FOOT = nrm([math.cos(math.radians(20)), 0, math.sin(math.radians(20))])

parts = [
    {"id": "body", "parent": None, "shape": "tube", "size": tube([-0.6, 0, 0], [0.6, 0, 0], 0.3, 0.3), "pos": B, "color": "@back"},
    {"id": "head", "parent": "body", "shape": "tube", "size": tube([0, 0, 0], [0.8, -0.1, 0], 0.18, 0.04), "pos": sub(HD, B), "color": "@back",
     "anim": {"axis": "y", "deg": 5, "speed": 0.2, "phase": 0}},
]
prev, at = "body", B
for i, x in enumerate(TX):
    xe = TX[i + 1] if i + 1 < len(TX) else TIP
    p = [x, ty(x), 0]
    parts.append({"id": f"caud{i + 1}", "parent": prev, "shape": "tube", "size": tube([0, 0, 0], [xe - x, ty(xe) - ty(x), 0], tr(x), tr(xe)),
                  "pos": sub(p, at), "color": "@back",
                  "anim": {"axis": "y", "deg": [3, 4, 5, 6][i], "speed": 0.7, "phase": round(PI + 0.7 * (i + 1), 3), "amp": True}})
    prev, at = f"caud{i + 1}", p
for S_, sz in (("L", 1), ("R", -1)):
    parts += limb_parts(S_, sz, "body", "body", FS, FE, FW, HH, HK, HA, B, B, (0.13, 0.08, 0.055), (0.16, 0.09, 0.06), swing=20, lift=10, speed=0.7)

SH = Shapes(); S = SH.S
FR = {"o": [0, 0, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.16}
SC = {"pat": "scales", "frame": FR}
HF = {"pat": "scales", "frame": {"o": [1.35, 0.65, 0], "u": [1, 0, 0], "v": [0, 1, 0], "r": 0.1}}

# ---- the HEAD (first: its cuts carve only it): small, low, the snout tapering to an upturned spade
H = "head"
S("skull", type="ell", bone=H, c=[1.27, 0.595, 0], r=[0.115, 0.07, 0.072], k=0.03, color="@head", **HF)
S("snout", type="ell", bone=H, c=[1.36, 0.57, 0], r=[0.1, 0.055, 0.05], rot=[0, 0, -3], k=0.03, color="@head", **HF)
S("snoutTip", type="ell", bone=H, c=[1.42, 0.588, 0], r=[0.045, 0.054, 0.052], k=0.025, color="@head", **HF)
S("spade", type="ell", bone=H, c=[1.456, 0.618, 0], r=[0.024, 0.056, 0.06], rot=[0, 0, 24], k=0.016, color="@snout", **HF)
S("jaw", type="ell", bone=H, c=[1.3, 0.525, 0], r=[0.135, 0.032, 0.055], rot=[0, 0, 4], k=0.025, color="@jaw", **HF)
S("jawAngle", type="ell", bone=H, c=[1.2, 0.535, 0], r=[0.07, 0.045, 0.065], k=0.025, color="@jaw", **HF)
S("cheek", type="ell", bone=H, c=[1.22, 0.58, 0.035], r=[0.07, 0.05, 0.04], k=0.02, color="@head", mirror=True, **HF)
S("brow", type="ell", bone=H, c=[1.25, 0.648, 0.05], r=[0.04, 0.012, 0.02], k=0.01, color="@head", mirror=True, **HF)
S("mouth", type="box", bone=H, op="sub", c=[1.335, 0.543, 0.06], r=[0.1, 0.0035, 0.03], rot=[0, 0, -4], round=0.0025, k=0.003, color="@mouth", mirror=True)
S("naris", type="sphere", bone=H, op="sub", c=[1.466, 0.645, 0.02], r=0.009, k=0.003, color="@mouth", mirror=True)
# ---- neck and trunk: broad, the back wide and flat-topped (the armour's carapace), the belly deep
S("neck", type="tube", bone=H, pts=[[x, y, 0, r] for x, y, r in NK], k=0.05, color="@back", **SC)
S("throat", type="ell", bone=H, c=[0.98, 0.55, 0], r=[0.24, 0.07, 0.11], k=0.04, color="@belly", **SC)
S("neckRoot", type="ell", c=[0.62, 0.66, 0], r=[0.2, 0.22, 0.26], k=0.06, color="@back", **SC)
S("trunk", type="ell", c=[0.03, 0.63, 0], r=[0.72, 0.24, 0.36], k=0.08, color="@back", **SC)
S("carapace", type="ell", c=[0.0, 0.76, 0], r=[0.72, 0.11, 0.33], k=0.07, color="@back", **SC)
S("chest", type="ell", c=[0.48, 0.61, 0], r=[0.28, 0.22, 0.29], k=0.07, color="@back", **SC)
S("hips", type="ell", c=[-0.45, 0.67, 0], r=[0.3, 0.2, 0.28], k=0.07, color="@back", **SC)
S("belly", type="ell", c=[0.05, 0.46, 0], r=[0.6, 0.09, 0.29], k=0.08, color="@belly", **SC)
S("shoulder", type="ell", c=[0.5, 0.56, 0.2], r=[0.16, 0.15, 0.11], k=0.06, color="@back", mirror=True, **SC)
S("pelvis", type="ell", c=[-0.42, 0.6, 0.2], r=[0.17, 0.15, 0.11], k=0.06, color="@back", mirror=True, **SC)
# ---- the tail: deep and broad at its root, tapering, held off the ground
CUTS = [(-0.45, -1.22), (-1.08, -1.78), (-1.62, -2.33), (-2.18, TIP)]
for i, (x0, x1) in enumerate(CUTS):
    xs = [x0 + (x1 - x0) * t / 5 for t in range(6)]
    S(f"tail{i + 1}", type="tube", bone=f"caud{i + 1}", pts=[[x, ty(x), 0, tr(x)] for x in xs], k=0.02, color="@back", **SC)
S("tailBelly", type="tube", bone="caud1", pts=[[x, ty(x) - 0.45 * tr(x), 0, 0.6 * tr(x)] for x in (-0.5, -0.75, -1.0)], k=0.04, color="@belly", **SC)
# ---- legs: semi-erect, stout
def limb(u, l, s0, e, w, r0, r1, r2, r3):
    S(u, type="tube", bone=u, pts=[s0 + [r0], lerp(s0, e, 0.45) + [(r0 + r1) / 2 * 1.1], e + [r1]], k=0.06, color="@limb", mirror=True, **SC)
    S(l, type="tube", bone=l, pts=[e + [r1 * 0.95], lerp(e, w, 0.5) + [r2], w + [r3]], k=0.03, color="@limb", mirror=True, **SC)
limb("legFLu", "legFLl", [0.53, 0.53, 0.13], FE, FW, 0.16, 0.085, 0.07, 0.056)
limb("legHLu", "legHLl", [-0.42, 0.57, 0.13], HK, HA, 0.19, 0.095, 0.076, 0.062)
S("elbow", type="ell", bone="legFLl", c=add(FE, [-0.01, 0, 0.0]), r=[0.07, 0.07, 0.065], k=0.03, color="@limb", mirror=True, **SC)
S("knee", type="ell", bone="legHLl", c=add(HK, [0.01, 0, 0.0]), r=[0.08, 0.075, 0.075], k=0.03, color="@limb", mirror=True, **SC)
PALM = [FW[0] + HAND[0] * 0.04, 0.03, FW[2] + HAND[2] * 0.04]
S("palm", type="ell", bone="legFLl", c=PALM, r=[0.085, 0.03, 0.085], rot=[0, -15, 0], k=0.025, color="@limb", mirror=True, **SC)
SOLE = [HA[0] + FOOT[0] * 0.06, 0.03, HA[2] + FOOT[2] * 0.06]
S("sole", type="ell", bone="legHLl", c=SOLE, r=[0.11, 0.03, 0.09], rot=[0, -20, 0], k=0.025, color="@limb", mirror=True, **SC)
S("heel", type="ell", bone="legHLl", c=[HA[0] - 0.01, 0.05, HA[2]], r=[0.06, 0.05, 0.055], k=0.025, color="@limb", mirror=True)
TOES = []
def digits(pre, bone, palm, axis, spec, r0, y0):
    for i, (ang, bang, m, L) in enumerate(spec):
        d = roty(axis, ang); base = add([palm[0], y0, palm[2]], roty(axis, bang), m)
        tip = add(base, d, L); tip[1] = 0.02
        S(f"{pre}{i + 1}", type="tube", bone=bone, pts=[base + [r0], lerp(base, tip, 0.5) + [r0 * 0.88], tip + [r0 * 0.75]], k=0.01, color="@limb", mirror=True)
        TOES.append((f"{pre}{i + 1}", bone, tip, d, r0 * 0.75))
digits("finger", "legFLl", PALM, HAND, [(-48, -60, 0.06, 0.035), (-22, -28, 0.072, 0.045), (0, 0, 0.076, 0.05), (22, 28, 0.072, 0.045), (46, 60, 0.06, 0.035)], 0.02, 0.028)
digits("toe", "legHLl", SOLE, FOOT, [(-44, -55, 0.065, 0.04), (-20, -24, 0.085, 0.055), (-2, -4, 0.1, 0.065), (16, 18, 0.09, 0.06), (40, 55, 0.065, 0.045)], 0.022, 0.028)

EYE = {"at": [1.255, 0.62, 0.062], "from": [1.255, 0.62, 0], "r": 0.016, "color": "@eyeDark", "iris": "@eye", "pupil": "round", "lid": "@head", "sink": 0.6}
COLORS = {"back": "#6a5c46", "head": "#6e604a", "limb": "#5e5240", "jaw": "#94846a", "belly": "#a89676", "snout": "#5a4c3a",
          "plate": "#86745a", "plateRim": "#3e3428", "lateral": "#7a6a50", "spike": "#c2ae8a", "spikeTip": "#4e4232",
          "claw": "#2e2820", "tooth": "#e2d8bc", "mouth": "#3a2c22", "eye": "#8a6a2a", "eyeDark": "#140e0a"}
OCHRE = {"back": "#7a6440", "head": "#7c6644", "limb": "#6a5638", "jaw": "#a88e64", "belly": "#bca47a", "snout": "#5e4a32",
         "plate": "#a08050", "plateRim": "#4a3824", "lateral": "#8e7048", "spike": "#d2b888", "spikeTip": "#5a4630"}
GREY = {"back": "#5c5a52", "head": "#5e5c54", "limb": "#52504a", "jaw": "#8c887a", "belly": "#9e9a8a", "snout": "#4a4842",
        "plate": "#78746a", "plateRim": "#34322c", "lateral": "#6a675e", "spike": "#bab4a2", "spikeTip": "#3e3c36"}
d = {
    "name": "desmatosuchus",
    "_about": "SCULPTED (2026-11-08, tools/creaturegen/prehistoric/desmatosuchus.py): DESMATOSUCHUS SPURENSIS, a late "
              "Triassic AETOSAUR (a pseudosuchian archosaur on the crocodiles' side, not a dinosaur), 4.5 m long and about "
              "a metre at the hips: a heavily armoured herbivore. The ARMOUR is rows of rectangular OSTEODERMS, each a `fin` "
              "plate laid on the probed skin -- rooted along its front edge just under it, its rim the exact rectangle, the "
              "rear edge standing proud so each row overlaps the next like tiles, a slab with a crisp edge and a dark rim "
              "band: one sheet a side a row, over the flat top of the back and down the flank's shoulder, from "
              "behind the skull down the neck, over the trunk and round the tail to near its tip, narrowing toward it. "
              "SPIKES (horns, faired, rising through their laterals): along the neck growing back to 20 cm, the great "
              "SHOULDER SPIKES (45 cm, broad and flattened at the root) out from the last cervical row rising out and up, "
              "then sweeping back (above the back in profile); short keels on every other lateral of the trunk and the tail's root. A small low head, the "
              "SHORT deep snout ending in a blunt UPTURNED spade (a pig's) with the nostrils on it, small leaf-shaped teeth "
              "(horns), a small eye; semi-erect legs (elbows and knees out, thick upper bones, short shins) on broad feet, "
              "five short clawed toes splayed forward; a long tapering tail held off the "
              "ground. Dull grey-brown, the plates paler with dark rims. Coats: grey-brown, ochre, slate; variant "
              "`juvenile` (.35).",
    "kind": "parts",
    "flags": {"dinosaur": True, "print": "paw", "legLen": 0.55},
    "colors": COLORS,
    "coats": [{"name": "grey-brown"}, {"name": "ochre", "colors": OCHRE}, {"name": "slate", "colors": GREY}],
    "variants": {"grey-brown": {"colors": {}}, "ochre": {"colors": OCHRE}, "slate": {"colors": GREY}, "juvenile": {"scale": 0.35, "colors": {}}},
    "parts": parts,
    "sculpt": {
        "keep": [],
        "mesh": {"cell": 0.016, "tris": [10000, 3000], "focus": {"head": 3, "legFLl": 1.5, "legHLl": 1.5}},
        "shade": {"back": 0.85, "belly": 1.1, "on": "@back"},
        "shape": SH,
        "eyes": EYE,
    },
}

# ================= pass 2: the armour, rooted on the probed skin
def rows():
    """the transverse rows, front to back: (x front, x back, bone, axis y, paramedian angle, lateral angle, region)"""
    R = []
    x = 1.165
    while x > 0.70:   # (the neck: on the head bone)
        L = 0.08; R.append((x, x - L, "head", ny(x - L / 2), 48, 112, "neck")); x -= L - 0.014
    x += 0.02   # (the first trunk row well under the last cervical one: no seam where the neck meets the trunk)
    while x > -0.62:  # (the trunk)
        L = 0.088; R.append((x, x - L, "body", 0.64, 58, 102, "trunk")); x -= L - 0.014
    while x > -2.72:  # (the tail: rows shortening toward the tip)
        L = 0.088 - 0.03 * min(1, (-0.62 - x) / 2.0)
        xm = x - L / 2
        bone = "body" if xm > TX[0] else "caud" + str(1 + sum(1 for t in TX[1:] if xm < t))
        R.append((x, x - L, bone, ty(xm), 52, 118, "tail")); x -= L - 0.012
    return R

NPL = 8
MERGE = True   # (one plate a side a row: paramedian and lateral as one sheet -- half the details; False: two)
def plates():
    R = rows()
    ex = [s["id"] for s in SH if s.get("type") in ("horn", "fin")]
    TH = lambda a0, a1, k: [a0 + (a1 - a0) * j / (k - 1) for j in range(k)]
    rays, keys = [], []
    for i, (xa, xb, bone, yc, ap, al, reg) in enumerate(R):
        for x in (xa, (xa + xb) / 2, xb):
            for a in TH(0.6, ap, 6) + TH(ap - 2, al, 6) + TH(0.6, al, 6) + TH(0.6, al, 9):
                t = math.radians(a); o = [x, yc, 0]
                rays.append([o, [x, yc + math.cos(t), math.sin(t)]]); keys.append((i, round(x, 5), round(a, 3)))
    hits = fd(SP, {"exclude": ex, "rays": rays})["hits"]
    HIT = {k: h for k, h in zip(keys, hits)}
    out, spk = [], []
    for i, (xa, xb, bone, yc, ap, al, reg) in enumerate(R):
        xm = (xa + xb) / 2
        def P(x, a, lift):
            h = HIT[(i, round(x, 5), round(a, 3))]
            t = math.radians(a); dvec = [0, math.cos(t), math.sin(t)]
            return add(h, dvec, lift)
        # (two plates a side, a paramedian and a lateral; down the slender end of the tail one, wrapping round)
        PL = (("pl", 0.6, al, "@plate"),) if MERGE else (("pm", 0.6, ap, "@plate"), ("lt", ap - 2, al, "@lateral")) if reg != "tail" or tr(xm) > 0.12 else (("tl", 0.6, al, "@plate"),)
        for kind, a0, a1, col in PL:
            A = TH(a0, a1, 9 if MERGE else 6)
            th = 0.016 if reg != "tail" else max(0.009, 0.016 * (0.4 + 0.6 * tr(xm) / 0.28))
            lf, lb = 0.004, 0.006 + 0.9 * th          # (the front's and the rear edge's lift: the rear stands proud)
            root = [P(xa, a, -0.009) for a in A]
            edge = [P(xa, A[0], lf) + [1.0], P(xm, A[0], (lf + lb) / 2) + [1.0], P(xb, A[0], lb) + [1.0]]
            c0 = len(edge) - 1
            edge += [P(xb, a, lb) + [1.0] for a in A[1:-1]]
            edge += [P(xb, A[-1], lb) + [1.0]]; c1 = len(edge) - 1
            edge += [P(xm, A[-1], (lf + lb) / 2) + [1.0], P(xa, A[-1], lf) + [1.0]]
            # (the rim runs from root[0] round to root[last]: root[0] is at A[0], so the rim goes back down the A[0] side,
            #  across the rear edge, and forward up the A[-1] side)
            out.append({"id": f"{kind}{i}", "type": "fin", "bone": bone, "root": root, "edge": edge, "corners": [0, c0, c1, len(edge) - 1],
                        "thick": round(th, 4), "slope": 1.6, "color": col, "rim": 0.012, "rimColor": "@plateRim",
                        "n": NPL, "across": 1, "mirror": True})
        # spikes on the laterals: out of the plate's middle
        a = (ap + al) / 2
        if reg == "neck":
            k = sum(1 for r in R[:i] if r[6] == "neck"); nN = sum(1 for r in R if r[6] == "neck")
            if 0 < k < nN - 1:   # (the last cervical row carries the great shoulder spike: shoulder_spike)
                L = 0.06 + 0.16 * (k - 1) / max(1, nN - 3)
                spk.append((f"cspike{i}", bone, i, xm, a - 6, L, 0.02 + 0.09 * L, 0.3, reg))
        elif reg == "trunk" and i % 2 == 0:
            spk.append((f"kspike{i}", bone, i, xm, a, 0.075, 0.028, 0.45, reg))
        elif reg == "tail" and xm > -1.4 and i % 2 == 0:
            spk.append((f"tspike{i}", bone, i, xm, a - 8, 0.05, 0.022, 0.5, reg))
    return R, out, spk, HIT

def spikes(R, spk, HIT):
    from sharp2 import sink_many
    ex = [s["id"] for s in SH if s.get("type") in ("horn", "fin")]
    P, M, rays = [], [], []
    for nm, bone, i, xm, a, L, r0, back, reg in spk:
        t = math.radians(a); n = [0, math.cos(t), math.sin(t)]; o = [xm, R[i][3], 0]
        rays.append([o, add(o, n, 1.0)])
    hits = fd(SP, {"exclude": ex, "rays": rays})["hits"]
    for (nm, bone, i, xm, a, L, r0, back, reg), h in zip(spk, hits):
        t = math.radians(a); n = [0, math.cos(t), math.sin(t)]
        dirv = nrm(add(n, [-back, 0.25, 0]))
        base = add(h, n, -0.03)
        tip = add(h, dirv, L)
        P.append(bent(base, tip, r0, bend=0.06, up=[-1, 0, 0], n=4, pw=0.9)); M.append((nm, bone, L))
    P = sink_many(SP, P, ex, need=0.4)
    return [{"id": nm, "type": "horn", "bone": bone, "pts": pts, "up": [0, 1, 0], "aspect": 0.85, "sides": 7,
             "color": "@spike", "tip": "@spikeTip", "tipAt": 0.5, "fair": {"r": 0.012}, "mirror": True} for (nm, bone, L), pts in zip(M, P)]

def shoulder_spike(R):
    """the great spike: out of the last cervical lateral, curving out, a little up and back (45 cm)"""
    from sharp2 import sink_many
    ex = [s["id"] for s in SH if s.get("type") in ("horn", "fin")]
    i = max(j for j, r in enumerate(R) if r[6] == "neck")
    xa, xb, bone, yc, ap, al, _ = R[i]
    xm = (xa + xb) / 2 - 0.02
    t = math.radians(66); n = [0, math.cos(t), math.sin(t)]
    h = fd(SP, {"exclude": ex, "rays": [[[xm, yc, 0], add([xm, yc, 0], n, 1.0)]]})["hits"][0]
    # (out ~60 deg from the midline and up ~35 deg at the root, then sweeping back: above the back's line in profile)
    c = [add(h, n, -0.06), add(h, [0.0, 0.05, 0.075], 1.0), add(h, [-0.02, 0.13, 0.175], 1.0), add(h, [-0.08, 0.2, 0.26], 1.0),
         add(h, [-0.18, 0.245, 0.315], 1.0), add(h, [-0.3, 0.26, 0.34], 1.0)]
    r = [0.095, 0.08, 0.06, 0.04, 0.02, 0.0]
    pts = [p + [rr] for p, rr in zip(c, r)]
    pts = sink_many(SP, [pts], ex, need=0.4)[0]
    return [{"id": "shoulderSpike", "type": "horn", "bone": "body", "pts": pts, "up": [0, 1, 0], "aspect": 0.62, "sides": 14,
             "color": "@spike", "tip": "@spikeTip", "tipAt": 0.55, "fair": {"r": 0.03}, "mirror": True}]

def teeth():
    from sharp2 import sink_many
    ex = [s["id"] for s in SH if s.get("type") in ("horn", "fin")]
    P, N = [], []
    for k, x in enumerate([1.4, 1.38, 1.36, 1.34, 1.32, 1.30, 1.28]):
        z = 0.04 + 0.004 * (1.4 - x) / 0.12
        a = [x, 0.554, z]; b = [x + 0.002, 0.536, z + 0.002]
        P.append(bent(a, b, 0.0055, bend=0.0, up=[1, 0, 0], n=3, pw=0.6)); N.append(f"tooth{k}")
    P = sink_many(SP, P, ex, need=0.5)
    return [{"id": nm, "type": "horn", "bone": "head", "pts": pts, "up": [1, 0, 0], "aspect": 1.7, "sides": 5, "color": "@tooth",
             "mirror": True} for nm, pts in zip(N, P)]

def claws():
    from sharp2 import sink_many
    P, M = [], []
    for nm, bone, tip, dvec, r in TOES:
        a = add(tip, dvec, -0.012); a[1] = 0.024
        b = add(tip, dvec, 0.02); b[1] = 0.004
        P.append(bent(a, b, r * 0.9, bend=0.1, up=[0, 1, 0], n=4, pw=0.7)); M.append((nm, bone))
    ex = [s["id"] for s in SH if s.get("type") in ("horn", "fin")]
    P = sink_many(SP, P, ex, need=0.5)
    return [{"id": "claw" + nm[0].upper() + nm[1:], "type": "horn", "bone": bone, "pts": pts, "up": [0, 1, 0], "aspect": 0.8,
             "flat": 0.4, "sides": 6, "color": "@claw", "fair": {"r": 0.007}, "mirror": True} for (nm, bone), pts in zip(M, P)]

if __name__ == "__main__":
    dump(OUT, d)
    index_add(["creatures/" + SP])
    R, pl, spk, HIT = plates()
    sh2 = pl + spikes(R, spk, HIT) + shoulder_spike(R) + teeth() + claws()
    SH += sh2
    dump(OUT, d)
    print(len(SH), "shapes,", len(pl), "plates,", len(sh2) - len(pl), "other sharp;", len(R), "rows")
