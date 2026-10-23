# EL CASTILLO, Chichen Itza (the Temple of Kukulcan, 9th-12th c.): a stepped pyramid of nine battered terraces, 55m
# square and 24m to its top platform; up the middle of each face a staircase of 91 steps (four times 91, and the
# temple's step, make the 365 days of the year), projecting from the pyramid, with serpent heads at the foot of its
# balustrades; on top the temple, its main door to the north between serpent columns.
#   North is +z. Numbers are worked here and written as numbers.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
Q = math.pi / 2

TOP, N, H = 19.5, 9, 24.0 / 9                  # the top platform, the terraces, each one's height
OUT = (55.3 - TOP) / 2 / N                     # how far each terrace stands out from the one above
add("pyramid", {"type": "crepidoma", "width": TOP, "length": TOP, "steps": N, "stepH": round(H, 4), "stepOut": round(OUT, 4), "batter": 0.8,
                "at": [[0, 0, 0, 0]], "_about": "nine terraces, each face leaning in (the talud) and each set back from the one below"})

# the four staircases: each from the ground straight up the middle of a face to the top platform
STEPS, W = 91, 8.9
RISE = 24.0 / STEPS
reach = TOP / 2 + STEPS * RISE                 # a 45-degree flight: it projects from the pyramid's foot
def rot(x, z, d):                              # a placement turned by d about the middle, as the engine turns a part
    c, s = math.cos(d), math.sin(d)
    return x * c + z * s, -x * s + z * c
names = ["north", "west", "south", "east"]
for k, nm in enumerate(names):
    d = k * Q
    x, z = rot(W / 2, reach, d)
    add(f"{nm} stair", {"type": "flight", "steep": True, "width": W, "run": round(RISE, 5), "rise": round(RISE, 5), "base": 0, "top": 24.0, "landing": 0,
                        "at": [[round(x, 4), 0, round(z, 4), round(Q + d, 6)]],
                        **({"_about": "a staircase up each face: 91 steps of 26cm on 26cm -- steep, as the real ones are -- arriving on the top platform"} if k == 0 else {})})
    for side in (-1, 1):
        hx, hz = rot(side * (W / 2 + 0.35), reach + 1.2, d)          # (in front of the balustrade's foot)
        add(f"{nm} serpent head {'left' if side < 0 else 'right'}", {"type": "box", "width": 1.2, "length": 2.2, "height": 1.3,
                                                                    "at": [[round(hx, 4), 0, round(hz, 4), round(d, 6)]],
                                                                    **({"_about": "the serpent heads at the foot of each balustrade (Kukulcan's shadow runs down to them at the equinox)"} if k == 0 and side < 0 else {})})

# the temple on top
TW, TH = 12.5, 6.5
door3 = [{"at": a, "width": 1.9, "sill": 0, "springing": 2.6, "head": {"profile": "flat"}} for a in (-3.2, 0, 3.2)]
door1 = [{"at": 0, "width": 1.9, "sill": 0, "springing": 2.6, "head": {"profile": "flat"}}]
add("temple", {"type": "enclosure", "plan": {"rect": [TW, TW]}, "thickness": 1.3, "height": TH, "openings": door1, "faces": {"0": door3},
               "at": [[0, 24.0, 0, 0]], "_about": "the temple: three doors to the north between its serpent columns, one on each other side"})
add("temple roof", {"type": "box", "width": TW + 0.6, "length": TW + 0.6, "height": 0.7, "at": [[0, 24.0 + TH, 0, 0]]})
add("roof crest", {"type": "box", "width": 0.8, "length": 0.8, "height": 0.8, "spiral": {"count": 24, "radius": TW / 2 - 0.2, "y": 24.0 + TH + 0.7},
                   "_about": "the merlons along the roof's edge"})

doc = {"name": "Chichen Itza",
       "_about": "EL CASTILLO, CHICHEN ITZA (the Temple of Kukulcan): a stepped pyramid of nine battered terraces (a `crepidoma` whose steps lean in), 55m square and 24m to its top; up the middle of each face a staircase of 91 steep steps, projecting from the pyramid's foot, its stone balustrades (the stairs' railings, `railing` stone) and the serpent heads at their foot; and on top the temple, three doors to the north, one to each other side, under its flat roof and crest.",
       "params": {"detail": 4}, "base": {"height": 0.3, "steps": 1, "stepOut": 0.5, "margin": 3},
       "railing": {"type": "stone", "height": 1.0}, "_railing": "the stairs' balustrades: stone, a metre high, sloping with the flights", "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/chichen-itza.json"), "w").write(json.dumps(doc, indent=2) + "\n")
