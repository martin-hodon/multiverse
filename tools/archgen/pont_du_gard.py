# THE PONT DU GARD (c. AD 40-60), the aqueduct of Nimes carried over the Gardon on three tiers of arches, 48.8m high and 275m long, built dry in big blocks of
# Vers limestone without mortar save in the channel.
#   THE LOWER TIER, six arches, 142m long, 6m thick, 22m high. The arches differ, each built on its own centring: the great one over the river spans 24.4m, the
#   others 15.5 to 21m -- and all crown at one level, so each springs from its own height. Each pier stands on the riverbed, the two in the water with cutwaters upstream.
#   THE MIDDLE TIER, eleven arches, 242m, 4m thick, 20m high: its piers stand over the lower tier's and it runs on past them to the slopes.
#   THE UPPER TIER, thirty-five little arches, 275m, 3m thick, and on them the conduit: the channel (specus) 1.2m wide and 1.8m high between two walls, roofed with slabs one walks on.
#   Stones were left standing proud of the faces on the piers (bosses: what the scaffolds and centring sat on) and they are the bridge's own texture at close range.
#   THE VALLEY. Each tier runs into its hillside: the ground stands at the lower tier's feet at the bridge's middle and at the conduit's roof at either end, and a stair climbs one
#   slope so that the water's road can be walked. The Gardon runs under the great arch: a `pool` moat, 34m wide, through the site.
#   The bridge runs along x; the river along z. The great arch's middle is the origin. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
r4 = lambda v: round(v, 4)
Q = math.pi / 2
semi = {"profile": "semicircular"}
DEEP = 4.0                                 # the piers' feet under the ground, down to the riverbed

# ---- the lower tier: spans from west to east, the river's arch the fourth, its middle at x = 0
S1 = [15.5, 19.2, 21.0, 24.4, 19.5, 16.0]
P1 = 3.8                                   # the pier between two arches
H1 = 22.0
C1 = 20.7                                  # where every arch crowns
x = -S1[3] / 2 - P1 - S1[2] - P1 - S1[1] - P1 - S1[0] - P1   # the tier's west end, an end pier wide
X1 = [x]
ops1, centres = [], []
for s in S1:
    c = x + P1 + s / 2
    centres.append(c); x = c + s / 2
X1E = x + P1                               # the east end
L1 = X1E - X1[0]
XM1 = (X1E + X1[0]) / 2                    # the wall's own middle
ops1 = [{"at": r4(c - X1[0]), "width": s, "sill": 0.6, "springing": r4(C1 + DEEP - s / 2), "head": semi} for c, s in zip(centres, S1)]
add("lower tier", {"type": "wall", "width": r4(L1), "height": H1 + DEEP, "thickness": 6.0, "glass": False, "openings": ops1, "at": [[r4(XM1), -DEEP, 3.0, 0]],
                   "courses": [{"y": H1 + DEEP - 0.9, "h": 0.5, "out": 0.25, "profile": "string"}],
                   "_about": "the lower tier: six arches crowning at one level, so each springs from its own height, on piers that stand on the riverbed"})
# (the two river piers' cutwaters, upstream, in the water)
piers = [centres[i] + S1[i] / 2 + P1 / 2 for i in range(5)]
for i in (2, 3):
    add(f"cutwater {i - 1}", {"type": "prism", "plan": {"points": [[-P1 / 2, 0], [P1 / 2, 0], [0, 3.6]]}, "height": 9.0 + DEEP, "at": [[r4(piers[i]), -DEEP, 3.0, 0]],
                              **({"_about": "a cutwater on the upstream face of each pier in the river"} if i == 2 else {})})

# ---- the middle tier: eleven arches, the six over the lower tier's and five more to the slopes
P2, H2, C2 = 4.2, 20.0, 18.9
Y2 = H1
XW, XE = -123.0, 119.0                     # its 242m
inner = list(zip(centres, S1))
n_w, n_e = 2, 3
w_len = (centres[0] - S1[0] / 2 - P2 / 2) - (XW + P2 / 2 + 0)
e_len = (XE - P2 / 2) - (centres[-1] + S1[-1] / 2 + P2 / 2 + 0)
bw, be = w_len / n_w, e_len / n_e          # each extra bay, arch and pier
A2 = [(XW + P2 / 2 + bw * (k + 0.5) + 0, bw - P2) for k in range(n_w)] + inner + [(centres[-1] + S1[-1] / 2 + P2 / 2 + be * (k + 0.5), be - P2) for k in range(n_e)]
add("middle tier", {"type": "wall", "width": XE - XW, "height": H2, "thickness": 4.0, "glass": False,
                    "openings": [{"at": r4(c - XW), "width": r4(s), "sill": 0, "springing": r4(C2 - s / 2), "head": semi} for c, s in A2],
                    "at": [[(XE + XW) / 2, Y2, 2.0, 0]], "courses": [{"y": H2 - 0.8, "h": 0.5, "out": 0.25, "profile": "string"}, {"y": 0, "h": 0.4, "out": 0.12, "profile": "band"}],
                    "_about": "the middle tier: eleven arches, 242m, its piers over the lower tier's and past them to the hillsides"})

# ---- the upper tier: thirty-five small arches, and the conduit on them
N3, L3, Y3 = 35, 275.0, 42.0
BAY3 = L3 / N3
add("upper tier", {"type": "wall", "width": L3, "height": 4.15, "thickness": 3.0, "glass": False,
                   "openings": [{"at": r4(BAY3 * (k + 0.5)), "width": 4.8, "sill": 0, "springing": 1.1, "head": semi} for k in range(N3)],
                   "at": [[0, Y3, 1.5, 0]], "_about": "thirty-five arches, 4.8m each"})
YS = Y3 + 4.15                             # the channel's floor
SPECUS, SH = 1.2, 1.8
add("channel floor", {"type": "box", "width": L3, "length": 3.0, "height": 0.02, "walked": True, "at": [[0, r4(YS - 0.02), 1.5, 0]]})
add("channel walls", {"type": "wall", "width": L3, "height": SH, "thickness": 0.9, "glass": False, "at": [[0, r4(YS), 0.45, 0], [0, r4(YS), 2.55, 0]],
                      "_about": "the conduit: two walls 1.2m apart and 1.8m high, the channel that carried Nimes's water"})
add("channel slabs", {"type": "box", "width": L3, "length": 3.0, "height": 0.85, "walked": True, "at": [[0, r4(YS + SH), 1.5, 0]], "_about": "the great slabs that roof the channel: 48.8m over the river, walked on"})
TOPY = YS + SH + 0.85

# ---- bosses: stones left proud on the piers' faces (one box, many places)
boss, boss2 = [], []
for x0 in piers + [X1[0] + P1 / 2, X1E - P1 / 2]:
    for y in (6.0, 11.0, 16.0):
        for k in (-1, 1):
            boss.append([r4(x0 + k * 0.9), y, 3.0, 0])
for c, s in A2[:-1]:
    x0 = c + s / 2 + P2 / 2
    for y in (Y2 + 4.0, Y2 + 10.0):
        boss2.append([r4(x0), y, 2.0, 0])
add("bosses", {"type": "box", "width": 0.7, "length": 6.3, "height": 0.45, "at": boss, "_about": "the stones left standing proud where the scaffolds and centring sat: through the pier, proud on both faces"})
add("bosses 2", {"type": "box", "width": 0.7, "length": 4.3, "height": 0.45, "at": boss2})

# ---- the hillsides: each tier runs into its slope. Layers of rock, each one set back as it rises, all as deep as each other
HALF = 24.0                                # the slopes' half-depth along the river
XEND = 158.0
LAYERS = [(0.0, 3.0, 69.0), (3.0, 9.0, 80.0), (9.0, 15.0, 88.0), (15.0, 21.0, 96.0), (21.0, 27.0, 104.0), (27.0, 33.0, 113.0), (33.0, 39.0, 121.0), (39.0, 45.0, 130.0), (45.0, TOPY, 137.5)]
for s, nm in ((-1, "west"), (1, "east")):
    for i, (y0, y1, xi) in enumerate(LAYERS):
        x0 = xi
        ww = XEND - x0
        add(f"{nm} slope {i + 1}", {"type": "prism", "plan": {"rect": [r4(ww), HALF * 2]}, "height": r4(y1 - y0), "batter": {"out": 1.6}, "at": [[r4(s * (x0 + ww / 2)), r4(y0), 1.5, 0]],
                                    **({"walked": True} if i == len(LAYERS) - 1 else {}),
                                    **({"_about": "the valley's side, rising in beds of rock to the conduit's roof at the bridge's end"} if i == 0 else {})})
# the water's road, on foot: short steep flights up the east slope's beds, one between each bed and the next, to the conduit's roof
STAIR_Z, FW = 17.0, 2.6
for i in range(len(LAYERS) - 1):
    y0, y1, xn = LAYERS[i][1], LAYERS[i + 1][1], LAYERS[i + 1][2]
    n = max(2, round((y1 - y0) / 0.26)); run = 0.22
    add(f"slope stair {i + 1}", {"type": "flight", "width": FW, "steep": True, "run": run, "rise": r4((y1 - y0) / n), "base": r4(y0), "top": r4(y1), "landing": 0,
                                 "at": [[r4(xn - n * run - 0.02), 0, r4(STAIR_Z + FW / 2), 0]],
                                 **({"_about": "the stair up the valley's side, one flight to each bed of rock"} if i == 0 else {})})
# rocks along the river's banks
add("bank rocks", {"type": "prism", "plan": {"points": [[-3, -1.6], [2.4, -2.2], [3.6, 0.2], [1.2, 1.8], [-2.4, 1.2]]}, "height": 1.2, "batter": {"out": 0.7},
                   "at": [[-19.5, 0, 22, 0.4], [20.5, 0, 26, 1.7], [-21, 0, -18, 2.6], [19.5, 0, -24, 0.9], [-20, 0, 42, 1.1], [21, 0, -46, 2.2]], "_about": "limestone ledges along the Gardon's banks"})

doc = {"name": "Pont du Gard",
       "_about": "THE PONT DU GARD: three tiers of arches, 48.8m high and 275m long -- six arches (142m), eleven (242m), thirty-five (275m) and the conduit -- over the Gardon, into its hillsides (tools/archgen/pont_du_gard.py).",
       "params": {"detail": 4, "footW": 2 * XEND + 8, "footD": 112},
       "site": {"origin": True, "moat": {"pool": True, "hw": 17.0, "hd": 54.0, "w": 0, "depth": 3.4}},
       "railing": False, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/pont-du-gard.json"), "w").write(json.dumps(doc, indent=1) + "\n")
fin = {"name": "Pont du Gard", "building": "architecture/pont-du-gard",
       "_about": "Honey Vers limestone in big dry-laid blocks; the slopes bare rock.",
       "stone": {"color": "#d8c79d", "accent": "#b9a678", "pat": "ashlar"},
       "rules": [{"parts": ["west slope", "east slope", "bank rocks", "stair head"], "pattern": "stone/rock face", "palette": "limestone"},
                 {"parts": ["cutwater"], "pattern": "stone/rusticated", "palette": "travertine"},
                 {"surface": "floor", "pattern": "stone/ashlar", "palette": "limestone"},
                 {"surface": "wall", "pattern": "stone/rusticated", "palette": "travertine"}]}
open(os.path.join(ROOT, "assets/finishes/pont-du-gard.json"), "w").write(json.dumps(fin, indent=1) + "\n")
print("pont du gard:", len(parts), "parts; top", round(TOPY, 2), "lower tier", round(X1[0], 1), round(X1E, 1), "L", round(L1, 1), "extra bays", round(bw, 1), round(be, 1))
