# SCHLOSS SCHWERIN (rebuilt 1845-57), the castle on its island in the lake, from components: a `court` -- one ring of
# rooms -- round a five-sided courtyard, a round `domed-tower` over every corner (where two wings meet at the pentagon's angle, the
# tower covers the joint, as the real castle's towers do), the great gate tower in the middle of the town front
# under its gilded dome, the bridge over the water to its gate. The lake is the ground's: the game carves a moat
# round the island (architecture.js archBuilding `moat`).
#   The court's pentagon has its town front to -z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
comp = lambda use, params, at, **kw: {"type": "component", "use": use, "params": params, "at": at, **kw}

RP = 38.0                                  # the pentagon's corners, from its middle
WD, N, H = 12.0, 4, 4.6                    # the wings: depth, storeys, storey height
CT = 7.4                                   # the corner towers' radius (an octagon: it must reach past a wing's corner)
GT = 8.0                                   # the gate tower's
angles = [math.radians(a) for a in (234, 306, 18, 90, 162)]       # counter-clockwise from the town front's west end
V = [(RP * math.cos(a), RP * math.sin(a)) for a in angles]
zmin = min(z for _, z in V) - CT - 4; zmax = max(z for _, z in V) + CT
DZ = -(zmin + zmax) / 2                    # shift the court so the island is centred on the origin
V = [(round(x, 4), round(z + DZ, 4)) for x, z in V]

def along(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
# ---- the court: ONE ring of rooms on the pentagon -- floors and stairs continuous all the way round, the gate
# through the town front (edge 0: the points are given clockwise from the town front's east end)
add("court", {"type": "court", "plan": {"points": [list(V[1]), list(V[0]), list(V[4]), list(V[3]), list(V[2])]},
              "depth": WD, "storeys": N, "storeyH": H, "axis": 3.4, "gate": {"face": 0, "width": 4.0, "height": 5.5},
              "roof": {"form": "hip", "pitch": 52}, "courses": True,
              # (Renaissance dress -- surround.js: pediments over the first floor's windows, triangular and segmental in turn)
              "surround": [{"head": False}, {"pediment": "alternate"}, {"head": "cornice"}, {"head": False}],
              "_about": "the castle's five wings round its court, one ring of rooms walked all the way round, entered through the gate tower"})

gold = {"cap": "bell", "waist": 0.78, "lift": 1.05}
add("corner towers", comp("components/domed-tower", {"sides": 8, "R": CT, "H": N * H + 7, "t": 0.9, "drumR": CT * 0.62, "drumH": 3.2,
                                                     "capR": CT * 0.66, "kok": 0.6, "finial": 2.4, "doorH": 3.2, **gold},
                          [[x, 0, z, 0] for x, z in V], build=["tower", "drum", "cap", "finial"],
                          _about="a round tower over every corner of the court, taller than the wings, under a gilded bell cupola"))
gx, gz = along(V[0], V[1], 0.5)
GS, GH = 2 * GT, N * H + 4.0                 # the gate storey: square, over the wings' eaves
arch = lambda w, h: [{"h": 10.0, "openings": [{"at": 0, "width": w, "sill": 0, "springing": h - w / 2, "head": {"profile": "semicircular"}}]},
                     {"openings": {"pattern": "2", "width": 1.6, "gap": 3.0, "sill": 2.0, "springing": 5.0, "head": {"profile": "semicircular"}}}]
add("gate storey", {"type": "enclosure", "plan": {"rect": [GS, GS]}, "thickness": 1.4, "height": GH, "glass": False,
                    "tiers": [{"h": 10.0, "openings": []}, {"openings": {"pattern": "2", "width": 1.6, "gap": 3.0, "sill": 2.0, "springing": 5.0,
                                                                        "head": {"profile": "semicircular"}}}],
                    # (its sides stand across the court's ring of rooms: a door through them on every storey)
                    "faces": {"0": arch(4.4, 7.0), "2": arch(4.4, 7.0),
                              # (in the middle of the ring's depth, toward the court: an enclosure face's `at` runs clockwise round
                              #  the plan, so that is -z on the +x face, +z on the -x face)
                              **{k: [{"h": H, "openings": [{"at": sgn * (WD / 2 - 0.9), "width": 1.6, "sill": 0, "springing": 2.4,
                                                            "head": {"profile": "semicircular"}}]} for _ in range(N)] + [{"openings": []}]
                                 for k, sgn in (("1", -1), ("3", 1))}},
                    "at": [[round(gx, 4), 0, round(gz, 4), 0]],
                    "_about": "the gate tower's square storey on the town front: the gateway straight through it, from the bridge to the court's gate"})
add("gate storey floor", {"flatRoof": True, "type": "box", "width": GS - 2.8, "length": GS - 2.8, "height": 0.5, "at": [[round(gx, 4), N * H + 1.9, round(gz, 4), 0]],
                          "_about": "the floor closing the gate storey under its octagon, low over the attic (a void, not a room)"})
add("gate tower", comp("components/domed-tower", {"sides": 8, "R": GT * 0.95, "H": 12.0, "t": 1.2, "drumR": GT * 0.72, "drumH": 6.0,
                                                  "cap": "semicircular", "capR": GT * 0.78, "kok": 0.8, "finial": 5.0, "doorH": 3.0, "winW": 2.0},
                        [[round(gx, 4), GH, round(gz, 4), 0]], build=["tower", "kokoshniki", "drum", "cap", "finial"],
                        _about="over it the octagon, the drum and the gilded dome"))
add("gate lantern", comp("components/domed-tower", {"sides": 8, "R": 1.6, "H": 3.0, "t": 0.3, "drumR": 1.1, "drumH": 0.8, "capR": 1.2,
                                                    "kok": 0.2, "finial": 2.0, "doorH": 1.0, **gold},
                         [[round(gx, 4), GH + 12.0 + 0.8 + 6.0 + GT * 0.78 - 0.6, round(gz, 4), 0]], build=["tower", "cap", "finial"],
                         _about="the lantern on the dome"))

# ---- the island's platform and the bridge from the gate over the water
HX = max(abs(x) for x, _ in V) + CT + 4; HZ = (zmax - zmin) / 2
MOAT_W = 16.0
gate_z = gz - GT                           # the gate storey's front face
BL = (gate_z - (-HZ - MOAT_W - 1.5))
add("bridge", comp("components/bridge", {"L": round(BL, 4), "W": 7, "depth": 5.0, "n": 4}, [[round(gx, 4), 0, round(gate_z, 4), math.pi]],
                   _about="the bridge over the lake to the gate"))
add("bridge steps", {"type": "flight", "width": 6, "run": 0.32, "rise": 0.15, "top": 0, "base": -0.6, "landing": 0,
                     "at": [[round(gx - 3, 4), 0, round(gate_z - BL - 4 * 0.32, 4), -1.5707963]], "_about": "down from the deck to the shore"})

doc = {"name": "Schloss Schwerin",
       "_about": "SCHLOSS SCHWERIN, the castle on its island (rebuilt 1845-57), from components: a `court` round its five-sided courtyard, one ring of rooms walked all the way round on every storey; a round `domed-tower` over every corner of the court, covering the joint where two wings meet, under a gilded bell cupola; the great gate tower in the middle of the town front, its gate at the foot and a gilded dome with a lantern over its drum; and the `bridge` over the lake to the gate. The lake is carved round the island by the game.",
       "params": {"detail": 4}, "base": {"height": 0.6, "steps": 2, "stepOut": 0.5, "plan": {"rect": [round(2 * HX, 4), round(2 * HZ, 4)]}},
       "_moat": {"hw": round(HX + 0.5, 2), "hd": round(HZ + 0.5, 2), "w": MOAT_W},
       "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/schwerin.json"), "w").write(json.dumps(doc, indent=2) + "\n")
print("moat", doc["_moat"])
