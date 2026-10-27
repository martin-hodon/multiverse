# SCHLOSS MORITZBURG (Saxony, rebuilt 1723-33 for Augustus the Strong), the hunting lodge on its island in the lake,
# from components: a `court` -- one ring of rooms round a small courtyard, three storeys under tall hipped roofs
# with dormers -- a round `domed-tower` standing out from every corner under a Baroque bell cap and a lantern, the
# whole on a raised terrace with balustrades on the island, a flight up to it from the causeway, and the `bridge`
# over the water to the island on the entrance (south, +z) side. The lake is the ground's: the game carves a moat
# round the island (architecture.js archBuilding `moat`).
#   Everything is centred on the origin (the island is), the entrance to +z. Numbers are worked here and written
# as numbers.
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapes import bell_y_at
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}
r4 = lambda v: round(v, 4)
Q = math.pi / 2

CW, CL = 52.0, 46.0                        # the main block: along x, along z
D, N, H = 12.0, 3, 5.2                     # the ring's depth, storeys, storey height
TH = 1.5                                   # the terrace the castle stands on, over the island
PITCH = 58                                 # the tall roofs
TR, TOFF = 7.0, 2.5                        # the corner towers' radius, and how far each stands out past its corner
TOW_H = N * H + 3.5                        # the towers rise a little over the eaves
TM, IM = 3.6, 5.0                          # the terrace past the towers; the island past the terrace
TX, TZ = CW / 2 + TOFF + TR + TM, CL / 2 + TOFF + TR + TM      # the terrace's half extents
HX, HZ = TX + IM, TZ + IM                                      # the island's
MOAT_W = 16.0

# ---- the island's terrace, walked on, and its balustrade -- open at the front where the flight comes up
add("terrace", {"type": "box", "width": 2 * TX, "length": 2 * TZ, "height": TH, "at": [[0, 0, 0, 0]], "walked": True,
                "_about": "the terrace round the castle, raised over the island, walked all the way round"})
FW = 7.1                                   # the terrace flight's width (and the gap in the balustrade): within the bridge's parapets, room before it
def piercing(L):
    k = int((L - 0.6) // 0.6)
    return {"pattern": str(k), "width": 0.25, "gap": 0.35, "sill": 0.22, "springing": 0.82, "head": {"profile": "flat"}, "glass": False}
BH, BT = 1.0, 0.35
KW, KH = BT + 0.55, 0.15                   # the plinth the balustrade stands on, a low step proud of it
fl = TX - FW / 2
add("terrace plinth", {"type": "box", "width": fl, "length": KW, "height": KH,
                       "at": [[-(FW / 2 + fl / 2), TH, TZ - KW / 2, 0], [FW / 2 + fl / 2, TH, TZ - KW / 2, 0]],
                       "_about": "the plinth under the balustrade (not a floor: its top is the balustrade's footing)"})
add("terrace plinth back", {"type": "box", "width": 2 * TX, "length": KW, "height": KH, "at": [[0, TH, -(TZ - KW / 2), 0]]})
add("terrace plinth sides", {"type": "box", "width": KW, "length": 2 * TZ - 2 * KW, "height": KH, "at": [[TX - KW / 2, TH, 0, 0], [-(TX - KW / 2), TH, 0, 0]]})
add("terrace balustrade front", {"type": "wall", "width": fl, "height": BH, "thickness": BT, "openings": piercing(fl),
                                 "at": [[-(FW / 2 + fl / 2), TH + KH, TZ, 0], [FW / 2 + fl / 2, TH + KH, TZ, 0]],
                                 "_about": "the balustrade along the terrace's edge, parted for the flight up from the bridge"})
add("terrace balustrade back", {"type": "wall", "width": 2 * TX, "height": BH, "thickness": BT, "openings": piercing(2 * TX),
                                "at": [[0, TH + KH, -TZ, math.pi]]})
add("terrace balustrade sides", {"type": "wall", "width": 2 * TZ - 2 * BT, "height": BH, "thickness": BT, "openings": piercing(2 * TZ - 2 * BT),
                                 "at": [[TX, TH + KH, 0, Q], [-TX, TH + KH, 0, -Q]]})
FS = int(round(TH / 0.15))
add("terrace flight", {"type": "flight", "width": FW, "run": 0.32, "rise": 0.15, "top": TH, "base": 0, "landing": 0,
                       "at": [[FW / 2, 0, r4(TZ + FS * 0.32), Q]], "_about": "up from the island to the terrace, before the gate"})

# ---- the main block: ONE ring of rooms round the courtyard, the gate through its south front (face 0, +z)
add("castle", {"type": "court", "plan": {"rect": [CW, CL]}, "depth": D, "storeys": N, "storeyH": H, "axis": 3.4,
               "gate": {"face": 0, "width": 4.0, "height": 4.8}, "roof": {"form": "hip", "pitch": PITCH, "overhang": 0.5}, "courses": True, "surround": {"head": False},
               "tracery": {"style": "bars"},
               "at": [[0, TH, 0, 0]],
               "_about": "the lodge's four wings round the small courtyard, one ring of rooms walked all the way round on every storey, entered by the gate in the south front"})

# the dormers in the outer slopes of the roofs: a small white front under a gable, sunk into the slope
EAVE = TH + N * H
tp = math.tan(math.radians(PITCH))
s0, s1 = 1.2, 3.2                          # the dormer's front and back, in from the outer wall
dW, dH = 1.8, 2.0
yb = EAVE + s0 * tp - 0.25
dormers, gables, panes = [], [], []
for nx, nz, L, off in ((0, 1, CW, CL / 2), (0, -1, CW, CL / 2), (1, 0, CL, CW / 2), (-1, 0, CL, CW / 2)):
    ex, ez = nz, -nx                       # along the face
    yaw = math.atan2(nx, nz)               # local z out of the face
    us = [u for u in (-17.0, -10.2, -3.4, 3.4, 10.2, 17.0) if abs(u) <= L / 2 - 8]
    for u in us:
        sm = (s0 + s1) / 2
        cx, cz = ex * u + nx * (off - sm), ez * u + nz * (off - sm)
        dormers.append([r4(cx), r4(yb), r4(cz), r4(yaw)])
        gables.append([r4(cx), r4(yb + dH), r4(cz), r4(yaw)])
        px, pz = ex * u + nx * (off - s0 + 0.02), ez * u + nz * (off - s0 + 0.02)
        panes.append([r4(px), r4(yb + 0.45), r4(pz), r4(yaw)])
add("dormers", {"type": "box", "width": dW, "length": s1 - s0, "height": dH, "at": dormers,
                "_about": "the dormers in the tall roofs' outer slopes, their backs sunk in the slope"})
add("dormer roofs", {"type": "roof", "form": "gable", "width": dW, "length": s1 - s0, "pitch": 45, "overhang": 0.15, "at": gables})
add("dormer windows", {"type": "box", "width": 0.9, "length": 0.06, "height": 1.2, "at": panes})

# ---- the four round corner towers under bell caps, standing out from the corners; a door onto the terrace
CAPR, WAIST, LIFT = 5.3, 0.8, 1.1
tw = {"sides": 16, "R": TR, "H": TOW_H, "t": 1.0, "drumR": TR * 0.66, "drumH": 2.6, "cap": "bell", "capR": CAPR,
      "waist": WAIST, "lift": LIFT, "kok": 0.6, "doorH": 3.4, "winW": 1.3, "capRibs": 16}
corners = [(sx, sz) for sx, sz in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
tpos = [(sx * (CW / 2 + TOFF), sz * (CL / 2 + TOFF)) for sx, sz in corners]
tat = [[r4(x), TH, r4(z), r4(math.atan2(sx, sz) - math.pi / 16)] for (x, z), (sx, sz) in zip(tpos, corners)]
add("corner towers", comp("components/domed-tower", tw, tat, build=["tower", "drum", "cap"],
                          _about="the four round towers at the corners, standing out from them, each under a Baroque bell cap; a door at the foot onto the terrace"))
LR = 1.5
capY = TH + TOW_H + 0.6 + 2.6
ly = capY + bell_y_at(CAPR, LR, WAIST, LIFT) - 0.15
add("tower lanterns", comp("components/domed-tower", {"sides": 8, "R": LR, "H": 2.6, "t": 0.3, "drumR": 1.0, "drumH": 0.7, "cap": "bell",
                                                      "capR": 1.25, "waist": 0.8, "lift": 1.2, "kok": 0.2, "finial": 1.8, "doorH": 0.9,
                                                      "winW": 0.4, "glazed": 0},
                           [[r4(x), r4(ly), r4(z), 0] for x, z in tpos], build=["tower", "cap", "finial"],
                           _about="the open lantern on every cap, a small bell and a finial over it"))

# ---- the bridge from the island over the lake, and the steps down from its end to the shore
BZ0 = HZ - 1.0
BL = 1.0 + 0.5 + MOAT_W + 1.5
add("bridge", comp("components/bridge", {"L": BL, "W": 8, "depth": 5.0, "n": 3}, [[0, 0, BZ0, 0]],
                   _about="the causeway bridge over the lake to the island, on the axis of the gate"))
add("bridge steps", {"type": "flight", "width": 7.1, "run": 0.32, "rise": 0.15, "top": 0, "base": -0.6, "landing": 0,
                     "at": [[3.55, 0, r4(BZ0 + BL + 4 * 0.32), Q]], "_about": "down from the deck to the shore"})

doc = {"name": "Schloss Moritzburg",
       "_about": "SCHLOSS MORITZBURG, Augustus the Strong's hunting lodge on its island (rebuilt 1723-33), from components: a `court` -- four wings round a small courtyard, one ring of rooms on three storeys walked all the way round, entered by the gate in the south front -- under tall hipped roofs with dormers; a round `domed-tower` standing out from every corner under a Baroque bell cap with an open lantern; the terrace round it on the island behind its balustrade, a flight up to it; and the `bridge` over the lake to the island. The lake is carved round the island by the game.",
       "params": {"detail": 4}, "railing": {"type": "balusters"},
       "base": {"height": 0.6, "steps": 2, "stepOut": 0.5, "plan": {"rect": [2 * HX, 2 * HZ]}},
       "_moat": {"hw": round(HX + 0.5, 2), "hd": round(HZ + 0.5, 2), "w": MOAT_W},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/moritzburg.json"), "w").write(json.dumps(doc, indent=2) + "\n")
print("moat", doc["_moat"])
