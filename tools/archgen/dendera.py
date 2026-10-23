#!/usr/bin/env python3
"""THE TEMPLE OF HATHOR, DENDERA (Ptolemaic, 54 BC - AD 20), at its real size, as an arch-engine definition (was
architecture.js egyptianTemple): a flat-roofed sandstone mass -- the pronaos facade of six columns linked by half-height
screen walls under a fat cavetto cornice, the hypostyle forest behind it, then the lower inner temple with its naos.
Walked: in through the open central bay, between the columns, through the inner door, round the sanctuary.

    python3 tools/archgen/dendera.py      # -> assets/architecture/dendera.json, assets/finishes/dendera.json
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

W, L, hallH, colH, colsFront, hypoRows, innerH = 34, 81, 17, 15, 6, 4, 12
D, T, B = 2.2, 1.2, 0.5                       # column diameter, wall thickness, the platform's top
hallDepth, screenH, L2 = L * 0.32, hallH * 0.4, L / 2
xs = [-(W / 2 - D) + i * (W - 2 * D) / (colsFront - 1) for i in range(colsFront)]
zF = L2 - D
rowGap = (hallDepth - 5) / hypoRows
rows = [zF - k * rowGap for k in range(hypoRows)]
at = lambda pts: [[round(x, 4), round(y, 4), round(z, 4), 0] for x, y, z in pts]
innerDepth = L - hallDepth; ziC = -L2 + innerDepth / 2; zin = L2 - hallDepth + T / 2
parts = {
    "platform": {"type": "box", "width": W + 2, "length": L + 2, "height": B, "at": [[0, 0, 0, 0]]},
    "columns": {"type": "column", "radius": D / 2, "height": colH - 2.4, "taper": 0.88, "sides": 12, "at": at([(x, B, z) for z in rows for x in xs])},
    "capitals": {"type": "box", "width": D * 1.15, "length": D * 1.15, "height": 1.6, "at": at([(x, B + colH - 2.4, z) for z in rows for x in xs]), "_about": "the Hathor block capitals"},
    "abaci": {"type": "box", "width": D * 0.9, "length": D * 0.9, "height": 0.8, "at": at([(x, B + colH - 0.8, z) for z in rows for x in xs])},
    "screen walls": {"type": "box", "width": round(xs[1] - xs[0] - D * 0.8, 4), "length": 1, "height": screenH,
                     "at": at([((xs[i] + xs[i + 1]) / 2, B, zF) for i in range(colsFront - 1) if i != colsFront // 2 - 1]), "_about": "half-height screens between the front columns, the central bay open"},
    "hall walls": {"type": "box", "width": T, "length": round(hallDepth, 4), "height": hallH, "at": at([(sx * (W - T) / 2, B, L2 - hallDepth / 2) for sx in (-1, 1)])},
    "hall roof": {"type": "box", "width": W, "length": round(hallDepth, 4), "height": 0.8, "at": at([(0, B + hallH, L2 - hallDepth / 2)]), "walked": True},
    "cornice": {"type": "box", "width": W + 1.6, "length": 2, "height": 1.7, "at": at([(0, B + hallH, L2 - 1)]), "_about": "the cavetto cornice over the facade"},
    "inner walls": {"type": "box", "width": T, "length": round(innerDepth, 4), "height": innerH, "at": at([(sx * (W - T) / 2, B, ziC) for sx in (-1, 1)])},
    "inner back": {"type": "box", "width": W, "length": T, "height": innerH, "at": at([(0, B, -L2 + T / 2)])},
    "inner front": {"type": "wall", "width": W - 2 * T, "height": innerH, "thickness": T, "glass": False,
                    "openings": [{"at": (W - 2 * T) / 2, "width": 3.4, "sill": 0, "springing": min(6, innerH - 2), "head": {"profile": "flat"}}],
                    "at": [[0, B, round(zin + T / 2, 4), 0]], "_about": "the inner temple's front, its axial door"},
    "inner roof": {"type": "box", "width": W, "length": round(innerDepth, 4), "height": 0.8, "at": at([(0, B + innerH, ziC)]), "walked": True},
    "naos": {"type": "box", "width": 6, "length": 8, "height": 6, "at": at([(0, B, -L2 + 7)])},
    "naos door": {"type": "box", "width": 2.2, "length": 0.5, "height": 3.6, "at": at([(0, B, -L2 + 11.2)]), "_about": "its dark doorway"},
}
doc = {"name": "Temple of Hathor, Dendera", "_about": "THE TEMPLE OF HATHOR AT DENDERA (Ptolemaic, 54 BC - AD 20) at its real size, 34 x 81 m: a flat-roofed sandstone mass, the pronaos facade of six columns joined by half-height screen walls under a fat cavetto cornice, a hypostyle of four rows behind it (the central file clear), then the lower inner temple entered by its axial door, the naos at the rear.",
       "params": {"detail": 4}, "parts": parts, "build": list(parts)}
open(os.path.join(ROOT, "assets/architecture/dendera.json"), "w").write(json.dumps(doc, indent=1) + "\n")
fin = {"name": "Temple of Hathor, Dendera", "building": "architecture/dendera", "_about": "Dendera: Nubian sandstone throughout, the Hathor capitals and the cornice a shade darker, the naos's doorway dark.",
       "stone": {"color": "#c9b283", "accent": "#b09a6d", "pat": "ashlar"},
       "rules": [{"parts": "naos door", "color": "#2e2a22", "accent": "#2e2a22"},
                 {"parts": ["capitals", "abaci", "cornice", "hall roof", "inner roof", "platform"], "pattern": "stone/ashlar", "palette": "sandstone"},
                 {"surface": "floor", "pattern": "floors/flagstones", "palette": "sandstone"},
                 {"pattern": "stone/ashlar fine", "palette": "sandstone"}]}
open(os.path.join(ROOT, "assets/finishes/dendera.json"), "w").write(json.dumps(fin, indent=1) + "\n")
print("dendera:", len(parts), "parts")
