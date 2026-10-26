#!/usr/bin/env python3
"""BIRDS (2026-09-30): birds as items (assets/items/birds/*.json) with FEATHERED WINGS AND TAILS -- every primary,
secondary and tail feather its own vane (items.js part type `feathers`, feathers.js), the coverts over their roots one
plate, the body a spindle, the neck a sweep, the head a sphere, the beak a cone, the legs rods. One wing component
(assets/items/components/wing.json) takes the span, the chord, the counts and the wing's SHAPE (rounded fingers of a
crow, pointed of a swallow, broad of an eagle) and the bird's `pose` ("spread": flying, wings out; "folded": perched,
wings along the flanks, the primaries' tips crossed over the tail). Edit this for the numbers, then run it:

    python3 tools/birdgen.py

The bird's frame: +x forward, +y up, +z its left; the origin under its belly at the feet.
"""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ITEMS = os.path.join(ROOT, "assets", "items")


def write(path, doc):
    full = os.path.join(ITEMS, path + ".json")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")


# ---- THE WING: one component, its shape by numbers ------------------------------------------------------------------
# In the wing's own frame: the shoulder at the origin, +z out along the span, +x forward, +y up; the definition mirrors
# it for the right wing. `spread` 1: flying; 0: folded along the flank (the whole fan swept back to lie along -x, the
# hand folded onto the arm). Shapes: pointed (swallow, falcon, gull: the last primary longest, the fan narrow),
# rounded (crow, hawk, pheasant: fingered primaries splayed), broad (eagle, stork, heron: deep and wide).
WING = {
    "kind": "item", "name": "Wing", "category": "components", "era": "everywhere", "region": "everywhere",
    "_about": "a bird's wing: the arm and hand under one plate of coverts, the secondaries fanned off the forearm, the primaries off the hand -- each feather its own vane (a component for the birds; params span, chord, pri, sec, shape, spread)",
    "params": {"span": 0.3, "chord": 0.1, "pri": 10, "sec": 9, "spread": 1, "sweep": 0, "band": 0, "lift": 0.0006},
    "materials": {"coverts": "wing-brown", "feather": "wing-brown", "tips": "wing-dark"},
    "parts": [
        # the hand: the primaries fan from the wrist out to the tip
        {"id": "primaries", "type": "feathers", "material": "feather", "tips": "tips", "n": "pri", "shape": "pointed", "band": "band", "lift": "lift",
         "roots": [["-chord * 0.05 - (1 - spread) * span * 0.4", "span * 0.48 * spread + (1 - spread) * span * 0.12"], ["-chord * 0.05 - (1 - spread) * span * 0.45", "span * 0.66 * spread + (1 - spread) * span * 0.14"]],
         "dir": ["50 + sweep + (1 - spread) * (90 - 50 - sweep)", "8 + sweep + (1 - spread) * (90 - 8 - sweep)"],
         "length": ["chord * 0.9", "span * 0.36 + chord * 0.1"], "width": ["chord * 0.24", "chord * 0.16"], "droop": "0.3 * spread", "lead": 1},
        # the arm: the secondaries along the trailing edge of the forearm
        {"id": "secondaries", "type": "feathers", "material": "feather", "tips": "tips", "n": "sec", "shape": "rounded", "band": "band", "lift": "lift",
         "roots": [["-chord * 0.15", "span * 0.06"], ["-chord * 0.12 - (1 - spread) * span * 0.4", "span * 0.48 * spread + (1 - spread) * span * 0.12"]],
         "dir": ["82 + (1 - spread) * 8", "62 + sweep * 0.5 + (1 - spread) * (28 - sweep * 0.5)"],
         "length": ["chord * 0.85", "chord * 0.9"], "width": ["chord * 0.28", "chord * 0.24"], "droop": "0.15 * spread", "lead": 1},
        # the coverts: one plate over the arm and the hand's roots (the outline in x and span; laid flat by the pitch)
        {"id": "coverts", "type": "plate", "material": "coverts", "thick": 0.002, "at": [0, "lift * (pri + sec) + 0.002", 0, 0, 90, 0],
         "outline": [["chord * 0.5", 0], ["chord * 0.42 - (1 - spread) * span * 0.3", "span * 0.5 * spread + (1 - spread) * span * 0.12"], ["chord * 0.28 - (1 - spread) * span * 0.45", "span * 0.68 * spread + (1 - spread) * span * 0.14"],
                     ["-chord * 0.05 - (1 - spread) * span * 0.45", "span * 0.66 * spread + (1 - spread) * span * 0.14"], ["-chord * 0.15 - (1 - spread) * span * 0.4", "span * 0.48 * spread + (1 - spread) * span * 0.12"], ["-chord * 0.2", 0]]},
    ],
}

SHAPES = {   # sweep (degrees the whole fan is swept back), the primaries' shape, the counts
    "pointed": {"sweep": 12, "pri": 10, "sec": 8},
    "rounded": {"sweep": -6, "pri": 10, "sec": 10},
    "broad": {"sweep": -10, "pri": 11, "sec": 14},
}


# ---- THE BIRDS ---------------------------------------------------------------------------------------------------------
def bird(key, name, era, region, about, *, L, r, head, beak, neck=None, legs, tail, wing, colours, band=0, pose_pick=("spread", "folded"),
         crest=None, eye="#1a1208", size=(0.92, 1.08), beak_shape="cone"):
    """L: body length (m); r: [breast, belly, rump] radii; head: [r, x_forward, y_up] from the body's front;
    beak: [length, root radius, pitch degrees (down)]; neck: [length, rise angle, radius] or None (the head on the body);
    legs: [thigh, tarsus, radius]; tail: {n, length, spread (degrees whole fan), shape, width, up (pitch)};
    wing: {span, chord, shape}; colours: back, breast, head, wing, primaries, tips, tail, beak, legs."""
    s = "s"
    shape = SHAPES[wing["shape"]]
    hip_y = legs[0] + legs[1]
    body_y = f"s * {hip_y + r[1] * 0.9:.4f}"
    front = f"s * {L * 0.5:.4f}"
    parts = [
        {"id": "body", "type": "sweep", "material": "back", "sides": 9, "seg": 1, "radii": [f"s * {r[0] * 0.25:.4f}", f"s * {r[0]:.4f}", f"s * {r[1]:.4f}", f"s * {r[2]:.4f}", f"s * {r[2] * 0.35:.4f}"],
         "path": [[front, body_y, 0], [f"s * {L * 0.25:.4f}", body_y, 0], [0, f"s * {hip_y + r[1] * 0.85:.4f}", 0], [f"s * {-L * 0.3:.4f}", f"s * {hip_y + r[1] * 0.95:.4f}", 0], [f"s * {-L * 0.5:.4f}", f"s * {hip_y + r[1] * 1.05:.4f}", 0]]},
        {"id": "breast", "type": "sphere", "material": "breast", "r": f"s * {r[0] * 0.8:.4f}", "sides": 8, "at": [f"s * {L * 0.2:.4f}", f"s * {hip_y + r[1] * 0.72:.4f}", 0], "stretch": [1.7, 1.02, 1.1]},
    ]
    hx, hy = L * 0.5 + head[1], hip_y + r[1] * 0.9 + head[2]
    if neck:
        nl, na, nr = neck
        import math
        hx = L * 0.5 + nl * math.cos(math.radians(na)) * 0.9
        hy = hip_y + r[1] * 0.9 + nl * math.sin(math.radians(na))
        parts.append({"id": "neck", "type": "sweep", "material": "head", "sides": 7, "seg": 2, "radii": [f"s * {nr * 1.2:.4f}", f"s * {nr:.4f}", f"s * {nr * 0.9:.4f}"],
                      "path": [[f"s * {L * 0.4:.4f}", f"s * {hip_y + r[1] * 0.9:.4f}", 0], [f"s * {L * 0.5 + nl * 0.55 * math.cos(math.radians(na)):.4f}", f"s * {hip_y + r[1] * 0.9 + nl * 0.45 * math.sin(math.radians(na)):.4f}", 0], [f"s * {hx:.4f}", f"s * {hy:.4f}", 0]]})
    hr = head[0]
    parts += [
        {"id": "head", "type": "sphere", "material": "head", "r": f"s * {hr:.4f}", "sides": 8, "at": [f"s * {hx:.4f}", f"s * {hy:.4f}", 0]},
        {"id": "eye", "type": "sphere", "material": "eye", "r": f"s * {hr * 0.18:.4f}", "sides": 5, "at": [f"s * {hx + hr * 0.45:.4f}", f"s * {hy + hr * 0.25:.4f}", f"s * {hr * 0.8:.4f}"], "mirror": "z"},
        {"id": "beak", "type": "rod", "material": "beak", "sides": 4 if beak_shape == "cone" else 6, "r0": f"s * {beak[1]:.4f}", "r1": f"s * {beak[1] * (0.35 if beak_shape == 'flat' else 0.08):.4f}",
         "at": [f"s * {hx + hr * 0.75:.4f}", f"s * {hy - hr * 0.05:.4f}", 0], "from": [0, 0, 0], "to": [f"s * {beak[0]:.4f}", f"s * {-beak[0] * beak[2] / 60:.4f}", 0],
         **({"stretch": [1, 0.45, 1.6]} if beak_shape == "flat" else {})},
        {"id": "thigh", "type": "rod", "material": "legs", "sides": 4, "r": f"s * {legs[2] * 1.3:.4f}", "from": [f"s * {-L * 0.05:.4f}", f"s * {hip_y:.4f}", f"s * {r[1] * 0.35:.4f}"], "to": [f"s * {L * 0.02:.4f}", f"s * {legs[1]:.4f}", f"s * {r[1] * 0.4:.4f}"], "mirror": "z", "when": {"pose": "folded"}},
        {"id": "tarsus", "type": "rod", "material": "legs", "sides": 4, "r": f"s * {legs[2]:.4f}", "from": [f"s * {L * 0.02:.4f}", f"s * {legs[1]:.4f}", f"s * {r[1] * 0.4:.4f}"], "to": [f"s * {L * 0.04:.4f}", 0, f"s * {r[1] * 0.4:.4f}"], "mirror": "z", "when": {"pose": "folded"}},
        {"id": "toes", "type": "rod", "material": "legs", "sides": 3, "r0": f"s * {legs[2] * 0.8:.4f}", "r1": f"s * {legs[2] * 0.3:.4f}", "from": [0, 0, 0], "to": [f"s * {legs[1] * 0.45:.4f}", 0, 0],
         "at": [f"s * {L * 0.04:.4f}", 0, f"s * {r[1] * 0.4:.4f}"], "around": {"n": 3, "r": 0, "plane": "xz", "start": -35, "span": 70}, "mirror": "z", "when": {"pose": "folded"}},
        {"id": "hind toe", "type": "rod", "material": "legs", "sides": 3, "r0": f"s * {legs[2] * 0.7:.4f}", "r1": f"s * {legs[2] * 0.3:.4f}", "from": [f"s * {L * 0.04:.4f}", 0, f"s * {r[1] * 0.4:.4f}"], "to": [f"s * {L * 0.04 - legs[1] * 0.25:.4f}", 0, f"s * {r[1] * 0.4:.4f}"], "mirror": "z", "when": {"pose": "folded"}},
        # IN FLIGHT (the spread pose) the legs trail back under the tail, the feet together behind -- not hanging as if
        # it stood on the air
        *(lambda kx, ky, fx, fy, z: [
            {"id": "thigh flying", "type": "rod", "material": "legs", "sides": 4, "r": f"s * {legs[2] * 1.3:.4f}", "from": [f"s * {-L * 0.05:.4f}", f"s * {hip_y:.4f}", f"s * {z:.4f}"], "to": [f"s * {kx:.4f}", f"s * {ky:.4f}", f"s * {z:.4f}"], "mirror": "z", "when": {"pose": "spread"}},
            {"id": "tarsus flying", "type": "rod", "material": "legs", "sides": 4, "r": f"s * {legs[2]:.4f}", "from": [f"s * {kx:.4f}", f"s * {ky:.4f}", f"s * {z:.4f}"], "to": [f"s * {fx:.4f}", f"s * {fy:.4f}", f"s * {z * 0.6:.4f}"], "mirror": "z", "when": {"pose": "spread"}},
            {"id": "toes flying", "type": "rod", "material": "legs", "sides": 3, "r0": f"s * {legs[2] * 0.8:.4f}", "r1": f"s * {legs[2] * 0.3:.4f}", "from": [f"s * {fx:.4f}", f"s * {fy:.4f}", f"s * {z * 0.6:.4f}"], "to": [f"s * {fx - legs[1] * 0.3:.4f}", f"s * {fy - legs[1] * 0.02:.4f}", f"s * {z * 0.5:.4f}"], "mirror": "z", "when": {"pose": "spread"}},
        ])(-L * 0.18, hip_y - (hip_y - legs[1]) * 0.35, -L * 0.18 - legs[1] * 0.95, hip_y - (hip_y - legs[1]) * 0.35 - legs[1] * 0.1, r[1] * 0.3),
        # the tail: a fan of feathers from the rump, laid back along -x (its frame yawed so +z points back)
        {"id": "tail", "type": "feathers", "material": "tail", "tips": "tips", "n": tail["n"], "shape": tail.get("shape", "rounded"), "band": tail.get("band", band), "lift": 0.0008,
         "roots": [[0, 0], [0, 0]], "dir": [f"-{tail['spread'] / 2}", f"{tail['spread'] / 2}"], "length": [f"s * {tail['length']:.4f}", f"s * {tail['length']:.4f}"],
         "width": [f"s * {tail['width']:.4f}", f"s * {tail['width']:.4f}"], "droop": tail.get("droop", 0.2), "lead": 1,
         "at": [f"s * {-L * 0.45:.4f}", f"s * {hip_y + r[1] * 1.0:.4f}", 0, -90, -tail.get("up", 10), 0]},
    ]
    if tail.get("centre"):   # a peacock's train, a pheasant's long middle pair: longer feathers in the middle of the fan
        c = tail["centre"]
        parts.append({"id": "tail centre", "type": "feathers", "material": "train", "tips": "tips", "n": c["n"], "shape": c.get("shape", "pointed"), "band": c.get("band", 0), "lift": 0.0008,
                      "roots": [[0, 0], [0, 0]], "dir": [f"-{c['spread'] / 2}", f"{c['spread'] / 2}"], "length": [f"s * {c['length']:.4f}", f"s * {c['length']:.4f}"],
                      "width": [f"s * {c['width']:.4f}", f"s * {c['width']:.4f}"], "droop": c.get("droop", 0.3), "lead": 1,
                      "at": [f"s * {-L * 0.45:.4f}", f"s * {hip_y + r[1] * 1.0 + 0.003:.4f}", 0, -90, -c.get("up", 10), 0]})
    if crest:
        parts.append({"id": "crest", "type": "feathers", "material": "crest", "n": crest["n"], "shape": "pointed", "band": 0, "lift": 0.0005,
                      "roots": [[0, 0], [0, 0]], "dir": [f"-{crest['spread'] / 2}", f"{crest['spread'] / 2}"], "length": [f"s * {crest['length']:.4f}", f"s * {crest['length']:.4f}"],
                      "width": [f"s * {crest['width']:.4f}", f"s * {crest['width']:.4f}"], "droop": 0, "lead": 1,
                      "at": [f"s * {hx - hr * 0.3:.4f}", f"s * {hy + hr * 0.8:.4f}", 0, -90, -crest.get("up", 60), 0]})
    # the wings: the component, once a side, at the shoulders; spread out flat or folded along the flanks
    for pose in ("spread", "folded"):
        sp = 1 if pose == "spread" else 0
        parts.append({"id": f"wing {pose}", "use": "items/components/wing", "when": {"pose": pose}, "mirror": "z",
                      "params": {"span": f"s * {wing['span']:.4f}", "chord": f"s * {wing['chord']:.4f}", "pri": shape["pri"], "sec": shape["sec"], "spread": sp, "sweep": shape["sweep"], "band": band},
                      "materials": {"coverts": "wing", "feather": "primaries", "tips": "tips"},
                      "at": [f"s * {L * 0.15:.4f}", f"s * {hip_y + r[1] * (1.4 if sp else 1.7):.4f}", f"s * {r[1] * (0.8 if sp else 0.5):.4f}", 0, -8 if sp else 70, 0]})
    mats = {"back": colours["back"], "breast": colours.get("breast", colours["back"]), "head": colours.get("head", colours["back"]), "wing": colours.get("wing", colours["back"]),
            "primaries": colours.get("primaries", colours.get("wing", colours["back"])), "tips": colours.get("tips", "wing-dark"), "tail": colours.get("tail", colours.get("wing", colours["back"])),
            "beak": colours.get("beak", "beak-horn"), "legs": colours.get("legs", "leg-grey"), "eye": eye}
    if tail.get("centre"): mats["train"] = colours.get("train", mats["tail"])
    if crest: mats["crest"] = colours.get("crest", mats["head"])
    doc = {"kind": "item", "name": name, "category": "birds", "era": era, "region": region, "_about": about,
           "params": {"s": list(size), "pose": {"pick": list(pose_pick)}}, "materials": mats, "parts": parts,
           "hold": {"grip": [0, f"s * {hip_y + r[1] * 0.8:.4f}", 0], "axis": [1, 0, 0], "face": [0, 1, 0]}}
    return key, doc


BIRDS = dict([
    bird("sparrow", "House sparrow", "everywhere", "everywhere", "a sparrow: brown streaked back, grey breast, a stubby seed-eater's beak",
         L=0.09, r=[0.022, 0.024, 0.016], head=[0.017, 0.012, 0.012], beak=[0.008, 0.004, 15], legs=[0.02, 0.022, 0.0015],
         tail={"n": 6, "length": 0.045, "spread": 30, "width": 0.008, "up": 5}, wing={"span": 0.11, "chord": 0.04, "shape": "rounded"},
         colours={"back": "plumage-brown", "breast": "plumage-grey", "head": "plumage-brown", "wing": "plumage-brown", "primaries": "wing-dark", "tail": "wing-dark", "beak": "beak-dark", "legs": "leg-pink"}),
    bird("robin", "Robin", "everywhere", "Europe", "a robin: olive-brown above, the red breast and face",
         L=0.09, r=[0.023, 0.025, 0.016], head=[0.017, 0.012, 0.013], beak=[0.009, 0.003, 10], legs=[0.022, 0.026, 0.0014],
         tail={"n": 6, "length": 0.045, "spread": 28, "width": 0.008}, wing={"span": 0.11, "chord": 0.04, "shape": "rounded"},
         colours={"back": "plumage-olive", "breast": "robin-red", "head": "plumage-olive", "wing": "plumage-olive", "primaries": "plumage-olive", "beak": "beak-dark", "legs": "leg-pink"}),
    bird("swallow", "Barn swallow", "everywhere", "everywhere", "a swallow: blue-black above, a red throat, long pointed wings and the forked tail",
         L=0.1, r=[0.02, 0.021, 0.013], head=[0.016, 0.01, 0.008], beak=[0.006, 0.003, 5], legs=[0.012, 0.012, 0.001],
         tail={"n": 6, "length": 0.08, "spread": 50, "width": 0.007, "shape": "pointed", "up": 0, "centre": {"n": 2, "length": 0.05, "spread": 12, "width": 0.007}},
         wing={"span": 0.16, "chord": 0.04, "shape": "pointed"},
         colours={"back": "plumage-blue-black", "breast": "plumage-cream", "head": "plumage-blue-black", "wing": "plumage-blue-black", "primaries": "wing-dark", "tail": "wing-dark", "train": "wing-dark", "beak": "beak-dark", "legs": "leg-grey"}),
    bird("blackbird", "Blackbird", "everywhere", "Europe", "a blackbird: all black, the yellow beak and eye-ring",
         L=0.13, r=[0.03, 0.032, 0.02], head=[0.022, 0.015, 0.015], beak=[0.014, 0.004, 10], legs=[0.03, 0.035, 0.002],
         tail={"n": 8, "length": 0.09, "spread": 32, "width": 0.012}, wing={"span": 0.17, "chord": 0.06, "shape": "rounded"},
         colours={"back": "plumage-black", "breast": "plumage-black", "head": "plumage-black", "wing": "plumage-black", "primaries": "plumage-black", "tail": "plumage-black", "beak": "beak-yellow", "legs": "leg-dark"}),
    bird("magpie", "Magpie", "everywhere", "Europe, Asia", "a magpie: black and white, the long graduated tail with a green sheen",
         L=0.18, r=[0.035, 0.037, 0.024], head=[0.026, 0.018, 0.016], beak=[0.02, 0.006, 8], legs=[0.035, 0.045, 0.0025],
         tail={"n": 8, "length": 0.22, "spread": 26, "width": 0.014, "shape": "pointed", "up": 6}, wing={"span": 0.26, "chord": 0.09, "shape": "rounded"}, band=0.4,
         colours={"back": "plumage-black", "breast": "plumage-white", "head": "plumage-black", "wing": "plumage-black", "primaries": "plumage-white", "tips": "plumage-black", "tail": "plumage-green-black", "beak": "beak-dark", "legs": "leg-dark"}),
    bird("crow", "Carrion crow", "everywhere", "everywhere", "a crow: all black, a heavy beak, fingered wingtips",
         L=0.22, r=[0.05, 0.052, 0.032], head=[0.035, 0.02, 0.02], beak=[0.035, 0.009, 10], legs=[0.045, 0.06, 0.003],
         tail={"n": 10, "length": 0.15, "spread": 36, "width": 0.02, "shape": "square"}, wing={"span": 0.42, "chord": 0.14, "shape": "rounded"},
         colours={"back": "plumage-black", "breast": "plumage-black", "head": "plumage-black", "wing": "plumage-black", "primaries": "plumage-black", "tail": "plumage-black", "beak": "beak-dark", "legs": "leg-dark"}),
    bird("raven", "Raven", "everywhere", "everywhere", "a raven: the great black crow, a wedge tail and a shaggy throat",
         L=0.3, r=[0.065, 0.068, 0.04], head=[0.045, 0.025, 0.025], beak=[0.055, 0.013, 8], legs=[0.06, 0.075, 0.004],
         tail={"n": 10, "length": 0.2, "spread": 40, "width": 0.026, "shape": "pointed"}, wing={"span": 0.58, "chord": 0.19, "shape": "rounded"},
         colours={"back": "plumage-black", "breast": "plumage-black", "head": "plumage-black", "wing": "plumage-black", "primaries": "plumage-black", "tail": "plumage-black", "beak": "beak-dark", "legs": "leg-dark"}),
    bird("pigeon", "Rock dove", "everywhere", "everywhere", "a pigeon: blue-grey, the two black wing bars, the iridescent neck",
         L=0.16, r=[0.04, 0.042, 0.026], head=[0.024, 0.015, 0.012], beak=[0.014, 0.005, 12], legs=[0.03, 0.03, 0.0025],
         tail={"n": 8, "length": 0.1, "spread": 34, "width": 0.014, "band": 0.25}, wing={"span": 0.3, "chord": 0.1, "shape": "pointed"}, band=0.15,
         colours={"back": "plumage-blue-grey", "breast": "plumage-grey", "head": "plumage-blue-grey", "wing": "plumage-blue-grey", "primaries": "plumage-grey", "tips": "plumage-black", "tail": "plumage-blue-grey", "beak": "beak-dark", "legs": "leg-pink"}),
    bird("kingfisher", "Kingfisher", "everywhere", "Europe, Asia", "a kingfisher: electric blue above, orange below, a dagger of a beak, a stump of a tail",
         L=0.09, r=[0.024, 0.026, 0.016], head=[0.02, 0.012, 0.008], beak=[0.035, 0.004, 3], legs=[0.012, 0.012, 0.0012],
         tail={"n": 5, "length": 0.03, "spread": 26, "width": 0.008}, wing={"span": 0.12, "chord": 0.045, "shape": "rounded"},
         colours={"back": "plumage-kingfisher", "breast": "plumage-orange", "head": "plumage-kingfisher", "wing": "plumage-kingfisher", "primaries": "plumage-blue-black", "tail": "plumage-kingfisher", "beak": "beak-dark", "legs": "leg-orange"}),
    bird("gull", "Herring gull", "everywhere", "the coasts", "a gull: white with a grey mantle, black wingtips, a yellow beak",
         L=0.3, r=[0.06, 0.062, 0.038], head=[0.038, 0.03, 0.02], beak=[0.045, 0.01, 6], legs=[0.05, 0.07, 0.004], neck=[0.06, 40, 0.03],
         tail={"n": 10, "length": 0.14, "spread": 36, "width": 0.024, "shape": "square"}, wing={"span": 0.68, "chord": 0.17, "shape": "pointed"}, band=0.2,
         colours={"back": "plumage-gull-grey", "breast": "plumage-white", "head": "plumage-white", "wing": "plumage-gull-grey", "primaries": "plumage-gull-grey", "tips": "plumage-black", "tail": "plumage-white", "beak": "beak-yellow", "legs": "leg-pink"}),
    bird("mallard", "Mallard drake", "everywhere", "everywhere", "a mallard drake: the bottle-green head, white collar, chestnut breast, grey flanks, the blue speculum",
         L=0.32, r=[0.065, 0.07, 0.045], head=[0.04, 0.03, 0.03], beak=[0.05, 0.014, 4], legs=[0.03, 0.04, 0.005], neck=[0.07, 55, 0.03], beak_shape="flat",
         tail={"n": 8, "length": 0.08, "spread": 34, "width": 0.018, "up": 10}, wing={"span": 0.42, "chord": 0.14, "shape": "pointed"}, band=0.3,
         colours={"back": "plumage-grey", "breast": "plumage-chestnut", "head": "plumage-bottle-green", "wing": "plumage-grey", "primaries": "plumage-grey", "tips": "plumage-speculum", "tail": "plumage-black", "beak": "beak-yellow", "legs": "leg-orange"}),
    bird("goose", "Greylag goose", "everywhere", "everywhere", "a goose: grey-brown, a long neck held high, the orange beak and pink legs",
         L=0.5, r=[0.1, 0.11, 0.07], head=[0.05, 0.03, 0.03], beak=[0.06, 0.018, 6], legs=[0.06, 0.09, 0.008], neck=[0.22, 70, 0.04], beak_shape="flat",
         tail={"n": 10, "length": 0.1, "spread": 36, "width": 0.024, "up": 5}, wing={"span": 0.75, "chord": 0.24, "shape": "broad"},
         colours={"back": "plumage-brown-grey", "breast": "plumage-grey", "head": "plumage-brown-grey", "wing": "plumage-brown-grey", "primaries": "wing-dark", "tail": "plumage-white", "beak": "beak-orange", "legs": "leg-pink"}),
    bird("swan", "Mute swan", "everywhere", "Europe, Asia", "a swan: all white, the long curved neck, the orange beak with its black knob",
         L=0.7, r=[0.14, 0.15, 0.09], head=[0.06, 0.03, 0.02], beak=[0.08, 0.02, 8], legs=[0.07, 0.1, 0.01], neck=[0.45, 75, 0.05], beak_shape="flat",
         tail={"n": 10, "length": 0.12, "spread": 36, "width": 0.03, "up": 12}, wing={"span": 1.0, "chord": 0.32, "shape": "broad"},
         colours={"back": "plumage-white", "breast": "plumage-white", "head": "plumage-white", "wing": "plumage-white", "primaries": "plumage-white", "tail": "plumage-white", "beak": "beak-orange", "legs": "leg-dark"}),
    bird("heron", "Grey heron", "everywhere", "everywhere", "a heron: grey, a white neck with black streaks, long legs, the dagger beak",
         L=0.45, r=[0.09, 0.095, 0.06], head=[0.045, 0.03, 0.02], beak=[0.12, 0.015, 3], legs=[0.25, 0.3, 0.008], neck=[0.35, 65, 0.035],
         tail={"n": 8, "length": 0.1, "spread": 30, "width": 0.022}, wing={"span": 0.9, "chord": 0.3, "shape": "broad"},
         crest={"n": 2, "length": 0.09, "spread": 8, "width": 0.01, "up": 5},
         colours={"back": "plumage-gull-grey", "breast": "plumage-white", "head": "plumage-white", "wing": "plumage-gull-grey", "primaries": "wing-dark", "tail": "plumage-gull-grey", "beak": "beak-yellow", "legs": "leg-dark", "crest": "plumage-black"}),
    bird("stork", "White stork", "everywhere", "Europe, Africa", "a stork: white, black flight feathers, the long red beak and red legs",
         L=0.5, r=[0.1, 0.105, 0.065], head=[0.05, 0.035, 0.02], beak=[0.17, 0.018, 4], legs=[0.3, 0.4, 0.009], neck=[0.32, 60, 0.04],
         tail={"n": 10, "length": 0.12, "spread": 34, "width": 0.026}, wing={"span": 1.0, "chord": 0.32, "shape": "broad"},
         colours={"back": "plumage-white", "breast": "plumage-white", "head": "plumage-white", "wing": "plumage-white", "primaries": "plumage-black", "tail": "plumage-white", "beak": "beak-red", "legs": "leg-red"}),
    bird("hen", "Hen", "-3000-1900", "everywhere", "a hen: plump, brown, the small red comb, a short tail",
         L=0.3, r=[0.08, 0.09, 0.055], head=[0.035, 0.03, 0.03], beak=[0.025, 0.008, 12], legs=[0.07, 0.08, 0.006], neck=[0.1, 60, 0.03],
         tail={"n": 8, "length": 0.12, "spread": 40, "width": 0.022, "up": 25}, wing={"span": 0.3, "chord": 0.16, "shape": "rounded"},
         crest={"n": 3, "length": 0.02, "spread": 30, "width": 0.012, "up": 70},
         colours={"back": "plumage-chestnut", "breast": "plumage-brown", "head": "plumage-chestnut", "wing": "plumage-chestnut", "primaries": "plumage-brown", "tail": "wing-dark", "beak": "beak-horn", "legs": "leg-yellow", "crest": "comb-red"}),
    bird("rooster", "Rooster", "-3000-1900", "everywhere", "a rooster: the red comb and wattles, a golden neck, green-black sickle tail feathers arching",
         L=0.34, r=[0.085, 0.09, 0.055], head=[0.038, 0.035, 0.04], beak=[0.028, 0.009, 12], legs=[0.09, 0.1, 0.007], neck=[0.14, 65, 0.032],
         tail={"n": 8, "length": 0.14, "spread": 40, "width": 0.024, "up": 35, "centre": {"n": 4, "length": 0.3, "spread": 16, "width": 0.02, "up": 70, "droop": 1.6}},
         wing={"span": 0.34, "chord": 0.18, "shape": "rounded"},
         crest={"n": 5, "length": 0.045, "spread": 50, "width": 0.014, "up": 70},
         colours={"back": "plumage-chestnut", "breast": "plumage-black", "head": "plumage-gold", "wing": "plumage-chestnut", "primaries": "plumage-black", "tail": "plumage-green-black", "train": "plumage-green-black", "beak": "beak-horn", "legs": "leg-yellow", "crest": "comb-red"}),
    bird("pheasant", "Pheasant cock", "everywhere", "Asia, Europe", "a pheasant: copper and gold, the green head, red wattles, the long barred tail",
         L=0.35, r=[0.075, 0.08, 0.05], head=[0.035, 0.03, 0.03], beak=[0.025, 0.008, 12], legs=[0.07, 0.08, 0.006], neck=[0.1, 55, 0.028],
         tail={"n": 6, "length": 0.2, "spread": 24, "width": 0.02, "shape": "pointed", "up": 15, "centre": {"n": 2, "length": 0.45, "spread": 6, "width": 0.02, "up": 15, "droop": 0.3}},
         wing={"span": 0.34, "chord": 0.16, "shape": "rounded"},
         colours={"back": "plumage-copper", "breast": "plumage-copper", "head": "plumage-bottle-green", "wing": "plumage-brown", "primaries": "plumage-brown", "tail": "plumage-pheasant-tail", "train": "plumage-pheasant-tail", "beak": "beak-horn", "legs": "leg-grey"}),
    bird("peacock", "Peacock", "everywhere", "India, then every palace garden", "a peacock: the blue neck and breast, the crest, the great green train of eyed feathers",
         L=0.4, r=[0.085, 0.09, 0.055], head=[0.035, 0.03, 0.04], beak=[0.025, 0.008, 10], legs=[0.12, 0.14, 0.007], neck=[0.22, 70, 0.03],
         tail={"n": 8, "length": 0.14, "spread": 40, "width": 0.024, "up": 10, "centre": {"n": 12, "length": 1.2, "spread": 30, "width": 0.05, "up": -8, "droop": 0.12, "band": 0.12}},
         wing={"span": 0.44, "chord": 0.2, "shape": "rounded"},
         crest={"n": 5, "length": 0.05, "spread": 30, "width": 0.006, "up": 100},
         colours={"back": "plumage-green", "breast": "plumage-peacock-blue", "head": "plumage-peacock-blue", "wing": "plumage-barred", "primaries": "plumage-chestnut", "tail": "plumage-brown", "train": "plumage-green", "tips": "plumage-eye", "beak": "beak-horn", "legs": "leg-grey", "crest": "plumage-peacock-blue"}),
    bird("owl", "Tawny owl", "everywhere", "everywhere", "an owl: round-headed, mottled brown, broad soft wings, a short tail",
         L=0.28, r=[0.075, 0.08, 0.05], head=[0.06, 0.02, 0.03], beak=[0.02, 0.008, 40], legs=[0.05, 0.05, 0.006],
         tail={"n": 8, "length": 0.1, "spread": 34, "width": 0.024, "shape": "square"}, wing={"span": 0.5, "chord": 0.2, "shape": "broad"},
         colours={"back": "plumage-mottled", "breast": "plumage-cream", "head": "plumage-mottled", "wing": "plumage-mottled", "primaries": "plumage-brown", "tail": "plumage-brown", "beak": "beak-horn", "legs": "leg-feathered"}, eye="#1a1208"),
    bird("buzzard", "Buzzard", "everywhere", "everywhere", "a buzzard: brown above, a pale barred breast, broad rounded wings, a fanned tail when soaring",
         L=0.32, r=[0.075, 0.08, 0.05], head=[0.04, 0.025, 0.02], beak=[0.03, 0.01, 30], legs=[0.06, 0.07, 0.006],
         tail={"n": 12, "length": 0.18, "spread": 60, "width": 0.028, "shape": "square", "band": 0.15}, wing={"span": 0.62, "chord": 0.24, "shape": "rounded"}, band=0.2,
         colours={"back": "plumage-brown", "breast": "plumage-cream", "head": "plumage-brown", "wing": "plumage-brown", "primaries": "plumage-cream", "tips": "wing-dark", "tail": "plumage-brown", "beak": "beak-dark", "legs": "leg-yellow"}),
    bird("eagle", "Golden eagle", "everywhere", "the mountains", "an eagle: dark brown, the golden nape, huge fingered wings, the hooked beak",
         L=0.5, r=[0.11, 0.115, 0.07], head=[0.055, 0.035, 0.03], beak=[0.05, 0.015, 35], legs=[0.09, 0.1, 0.009],
         tail={"n": 12, "length": 0.3, "spread": 50, "width": 0.04, "shape": "square"}, wing={"span": 1.05, "chord": 0.36, "shape": "broad"},
         colours={"back": "plumage-dark-brown", "breast": "plumage-dark-brown", "head": "plumage-gold", "wing": "plumage-dark-brown", "primaries": "plumage-dark-brown", "tail": "plumage-brown", "beak": "beak-dark", "legs": "leg-yellow"}),
    bird("falcon", "Peregrine falcon", "everywhere", "everywhere", "a falcon: slate above, barred white below, the black moustache, long pointed wings",
         L=0.28, r=[0.06, 0.065, 0.04], head=[0.035, 0.022, 0.02], beak=[0.025, 0.009, 35], legs=[0.05, 0.05, 0.005],
         tail={"n": 10, "length": 0.16, "spread": 34, "width": 0.024, "band": 0.15}, wing={"span": 0.58, "chord": 0.17, "shape": "pointed"}, band=0.1,
         colours={"back": "plumage-slate", "breast": "plumage-barred", "head": "plumage-slate", "wing": "plumage-slate", "primaries": "plumage-slate", "tips": "plumage-black", "tail": "plumage-slate", "beak": "beak-dark", "legs": "leg-yellow"}),
    bird("parrot", "Macaw", "everywhere", "the Americas (and a captain's shoulder)", "a macaw: scarlet, the blue and yellow wings, the long pointed tail, the great hooked beak",
         L=0.3, r=[0.06, 0.065, 0.04], head=[0.04, 0.025, 0.02], beak=[0.04, 0.016, 40], legs=[0.04, 0.04, 0.005],
         tail={"n": 8, "length": 0.4, "spread": 24, "width": 0.024, "shape": "pointed", "up": -15}, wing={"span": 0.5, "chord": 0.16, "shape": "pointed"}, band=0.5,
         colours={"back": "plumage-scarlet", "breast": "plumage-scarlet", "head": "plumage-scarlet", "wing": "plumage-yellow", "primaries": "plumage-yellow", "tips": "plumage-cobalt", "tail": "plumage-scarlet", "beak": "beak-horn", "legs": "leg-grey"}),
    bird("flamingo", "Flamingo", "everywhere", "the salt lakes", "a flamingo: pink, the long legs and the S-neck, the bent black-tipped beak",
         L=0.45, r=[0.085, 0.09, 0.06], head=[0.04, 0.03, 0.02], beak=[0.09, 0.016, 45], legs=[0.35, 0.5, 0.006], neck=[0.5, 80, 0.028],
         tail={"n": 8, "length": 0.1, "spread": 30, "width": 0.022}, wing={"span": 0.7, "chord": 0.24, "shape": "broad"},
         colours={"back": "plumage-pink", "breast": "plumage-pink", "head": "plumage-pink", "wing": "plumage-crimson", "primaries": "plumage-black", "tail": "plumage-pink", "beak": "beak-pink", "legs": "leg-pink"}),
    bird("crane", "Common crane", "everywhere", "Europe, Asia", "a crane: tall and grey, the red crown, the bustle of drooping tertials over the tail",
         L=0.55, r=[0.1, 0.105, 0.065], head=[0.045, 0.03, 0.02], beak=[0.1, 0.014, 5], legs=[0.35, 0.45, 0.009], neck=[0.5, 78, 0.035],
         tail={"n": 10, "length": 0.22, "spread": 34, "width": 0.03, "droop": 1.2, "up": 20}, wing={"span": 1.1, "chord": 0.34, "shape": "broad"},
         colours={"back": "plumage-gull-grey", "breast": "plumage-gull-grey", "head": "plumage-black", "wing": "plumage-gull-grey", "primaries": "plumage-black", "tail": "plumage-black", "beak": "beak-horn", "legs": "leg-dark"}),
    bird("dove", "Turtle dove", "everywhere", "Europe, Asia", "a turtle dove: pinkish, the scaled chestnut wings, a black and white neck patch",
         L=0.14, r=[0.034, 0.036, 0.022], head=[0.022, 0.014, 0.012], beak=[0.012, 0.004, 12], legs=[0.025, 0.028, 0.002],
         tail={"n": 8, "length": 0.1, "spread": 34, "width": 0.014, "band": 0.25}, wing={"span": 0.26, "chord": 0.09, "shape": "pointed"},
         colours={"back": "plumage-chestnut", "breast": "plumage-pink-grey", "head": "plumage-pink-grey", "wing": "plumage-chestnut", "primaries": "wing-dark", "tips": "plumage-white", "tail": "plumage-slate", "beak": "beak-dark", "legs": "leg-pink"}),
])

MATERIALS = {
    "wing-brown": "#6a4e30", "wing-dark": "#2a2420", "plumage-brown": "#7a5a38", "plumage-dark-brown": "#4a3420", "plumage-grey": "#9a9a98", "plumage-gull-grey": "#a8adb2",
    "plumage-blue-grey": "#7a8494", "plumage-slate": "#4a5260", "plumage-black": "#1e1c1c", "plumage-blue-black": "#22283e", "plumage-green-black": "#1e3a2e", "plumage-white": "#f0eee8",
    "plumage-cream": "#e4d8c0", "plumage-olive": "#7a7048", "robin-red": "#d8602a", "plumage-orange": "#e08a3a", "plumage-kingfisher": "#1a8ac0", "plumage-chestnut": "#8a4a2a",
    "plumage-bottle-green": "#1a5a3a", "plumage-speculum": "#2a4ab0", "plumage-brown-grey": "#8a7a68", "plumage-gold": "#c89a3a", "plumage-copper": "#b8602a", "plumage-pheasant-tail": "#a87a40",
    "plumage-green": "#2a8a4a", "plumage-peacock-blue": "#1a4aa8", "plumage-barred": "#c8b890", "plumage-eye": "#1a6a8a", "plumage-mottled": "#8a6a48", "plumage-scarlet": "#d02a22",
    "plumage-yellow": "#e8c030", "plumage-cobalt": "#2a5ad0", "plumage-pink": "#e8a0b0", "plumage-crimson": "#c02a48", "plumage-pink-grey": "#c8a8a0", "comb-red": "#d02020",
    "beak-horn": "#c8b088", "beak-dark": "#3a3028", "beak-yellow": "#e0b020", "beak-orange": "#e07820", "beak-red": "#c83020", "beak-pink": "#e8a8a8",
    "leg-grey": "#6a6a68", "leg-dark": "#2a2828", "leg-pink": "#d89a90", "leg-orange": "#e08830", "leg-yellow": "#d8b040", "leg-red": "#c83020", "leg-feathered": "#c8b898",
}


def main():
    write("components/wing", WING)
    for k, v in BIRDS.items():
        write("birds/" + k, v)
    mpath = os.path.join(ITEMS, "materials.json")
    lib = json.load(open(mpath))
    added = 0
    for k, v in MATERIALS.items():
        if k not in lib["materials"]:
            lib["materials"][k] = {"pattern": "materials/paint", "palette": [v, v, v, v]}; added += 1
    json.dump(lib, open(mpath, "w"), indent=1, ensure_ascii=False)
    ipath = os.path.join(ROOT, "assets", "index.json")
    index = json.load(open(ipath))
    cats = {c["name"]: c for c in index["categories"]}
    if "Items: birds" not in cats:
        pos = index["categories"].index(cats["Items: food"]) + 1
        index["categories"].insert(pos, {"name": "Items: birds", "kind": "item", "paths": []})
        cats = {c["name"]: c for c in index["categories"]}
    cats["Items: birds"]["paths"] = ["items/birds/" + k for k in BIRDS]
    comps = cats["Items: components"]["paths"]
    if "items/components/wing" not in comps: comps.append("items/components/wing")
    json.dump(index, open(ipath, "w"), indent=2, ensure_ascii=False)
    print(len(BIRDS), "birds,", added, "materials added")


if __name__ == "__main__":
    main()
