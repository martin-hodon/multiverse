#!/usr/bin/env python3
"""FACES (2026-09-30): the parametric low-poly head (face.js, item part type `face`) as definitions -- the canon and
the kinds of people drawn from it (assets/items/faces/*.json), the skin, eye, lip and hair materials, and the
catalogue's "Items: faces" category. Edit this for the numbers, then run it:

    python3 tools/facegen.py

A face's params are the skull's (face.js FACE_PARAMS: faceW, forehead, occiput, crown -- factors, 1 the canon; hairline,
neckR, earS) and the face's ATTRIBUTES (face.js FACE_ATTRS, docs/face.md: anthropometric measurements in metres, angles
in degrees, roundness factors, expressions). Ranges draw a stranger from each kind by the seed. Run tools/hairgen.py
after this one: it gives the faces their hairstyles."""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ITEMS = os.path.join(ROOT, "assets", "items")


def write(path, doc):
    full = os.path.join(ITEMS, path + ".json")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")


SKINS = {"pick": ["skin-pale", "skin-fair", "skin-fair", "skin-olive", "skin-tan", "skin-brown", "skin-dark"]}
IRISES = {"pick": ["iris-brown", "iris-brown", "iris-hazel", "iris-blue", "iris-blue", "iris-green", "iris-grey", "iris-amber"]}
HAIRS = {"pick": ["hair-black", "hair-black", "hair-brown", "hair-brown", "hair-chestnut", "hair-blond", "hair-red"]}

FACES = {}
# the head's own parameters a thing worn on it takes from the face (as a hairstyle does: hairgen.py PASS)
HEAD_PASS = ["scale", "faceW", "forehead", "occiput", "crown", "hairline", "earS", "foreheadHeight", "foreheadAngle", "browRidge"]
# THE CANON (2026-10-05, docs/face.md): the skull's own numbers (the loft the hair grows on: faceW, forehead, occiput,
# crown -- factors) and the face's ATTRIBUTES (face.js FACE_ATTRS: Farkas's measurements in metres, the profile's
# angles in degrees, the roundness factors) -- face.js reads every attribute from the item's params by its name, so
# the part maps only the skull's
CANON = {"scale": 1, "faceW": 1, "forehead": 1, "occiput": 1, "crown": 1, "earS": 1, "hairline": 0.06, "bare": 1, "hair": "hair",
         "faceHeight": 0.123, "foreheadHeight": 0.062, "foreheadAngle": 12, "upperWidth": 0.136, "foreheadWidth": 0.112, "lowerWidth": 0.098, "chinWidth": 0.042,
         "jawAngle": 122, "eyeDistance": 0.033, "eyeWidth": 0.030, "eyeHeight": 0.010, "eyeTilt": 4, "eyeDepth": 0.016,
         "browHeight": 0.016, "browArch": 0.003, "browThickness": 0.006, "browRidge": 0.003,
         "noseHeight": 0.052, "noseWidth": 0.034, "noseProjection": 0.020, "nasolabialAngle": 102, "noseBridge": 0.003, "noseHump": 0,
         "mouthWidth": 0.052, "upperLipHeight": 0.021, "upperVermilion": 0.008, "lowerVermilion": 0.009, "lowerLipHeight": 0.019,
         "chinProjection": 0, "chinHeight": 0.013, "chubby": 1,
         "expression": "neutral", "viseme": "none", "flower": 0, "hairFlower": "items/flowers/blooms/rose", "flowerScale": 0.75,
         "headwear": 0, "earrings": 0, "hairCap": None, "fringe": 0}
FACES["face"] = {
    "kind": "item", "name": "Face", "category": "face", "era": "everywhere", "region": "everywhere",
    "_about": "the canon head on GUIDE LINES (face.js, docs/face.md): Farkas's adult means as attributes -- face height, upper and lower width, the eyes' distance and width, the nose's height, width and projection, the nasolabial and forehead angles, the mouth's width, the lips' heights -- placing the landmarks, the landmarks the lattice of guide lines (brow, lids, lip borders, jawline...), the skin the lattice subdivided with each region's roundness. expression / viseme (or the actions: smile, jawOpen, blink...) move the lines. The origin is the cranium's centre; +x is where it looks",
    "params": CANON,
    "materials": {"skin": SKINS, "lip": {"pick": ["lip-rose", "lip-rose", "lip-pink", "lip-brown", "lip-pale", "lip-dark"]}, "mouth": "mouth-dark", "teeth": "teeth-ivory", "eye": "eye-white", "limbus": "iris-limbus", "glint": "eye-glint", "lash": "lash-dark", "iris": IRISES, "pupil": "pupil", "brow": "hairColour", "hair": "hairColour", "hairColour": HAIRS, "tie": "leather-dark"},
    "parts": [{"id": "head", "type": "face", "headScale": "scale", "faceW": "faceW", "forehead": "forehead", "occiput": "occiput", "crown": "crown",
               "earS": "earS", "hairline": "hairline", "bare": "bare", "hair": "hair"},
              # A FLOWER IN THE HAIR (`flower` 1): a bloom (items/flowers/blooms) worn over the left ear, its face turned out
              # from the head, sitting on the hair (the head's half-breadth there and the hair's cap over it)
              {"id": "hair flower", "use": "hairFlower", "when": "flower", "scale": "scale * flowerScale",
               "at": ["0.006 * scale", "0.016 * scale", "-0.09 * scale", 15, -90, 0]},
              # JEWELRY on the head (items/jewelry: a diadem, a wreath, a circlet) and at the ears, laid on this head's own
              # skull and its hairstyle's cap (jewelry.js headFit, earFit) -- the head's params handed on by their names
              {"id": "headwear", "use": "headwear", "when": "headwear", "params": {**{k: k for k in HEAD_PASS}, "hairCap": "hairCap", "fringe": "fringe"}},
              {"id": "earrings", "use": "earrings", "when": "earrings", "params": {k: k for k in HEAD_PASS}}],
}


def kind(key, name, about, params, materials=None):
    FACES[key] = {"kind": "item", "use": "items/faces/face", "name": name, "category": "face", "_about": about, "params": params, "materials": materials or {}}


# (ranges: a stranger of each kind drawn by the seed; men and women from Farkas's means and spreads)
kind("man", "Man", "a man's head: the face longer and the jaw wider and squarer (a lower jaw angle), the brow ridge heavier and the brows lower and straighter, the forehead sloping, the nose longer, wider and more projecting with a more acute nasolabial angle, the lips thinner, the hairline drawn by the seed (some receding)",
     {"faceHeight": [0.118, 0.13], "upperWidth": [0.134, 0.142], "lowerWidth": [0.096, 0.108], "chinWidth": [0.042, 0.05], "jawAngle": [114, 124], "foreheadAngle": [10, 18],
      "browRidge": [0.004, 0.007], "browHeight": [0.012, 0.016], "browArch": [0.0, 0.002], "browThickness": [0.006, 0.0085],
      "noseHeight": [0.052, 0.058], "noseWidth": [0.034, 0.039], "noseProjection": [0.019, 0.024], "nasolabialAngle": [90, 102], "noseHump": [0, 0.004], "noseBridge": [0.003, 0.006],
      "mouthWidth": [0.05, 0.056], "upperVermilion": [0.006, 0.008], "lowerVermilion": [0.008, 0.01], "upperLipHeight": [0.02, 0.024], "lowerLipHeight": [0.018, 0.021],
      "eyeDistance": [0.031, 0.035], "eyeWidth": [0.029, 0.032], "eyeHeight": [0.009, 0.011], "eyeTilt": [0, 4], "chinProjection": [0.0, 0.004], "chinHeight": [0.013, 0.017],
      "chubCheek": [0.7, 1.0], "chubby": [0.8, 1.0], "chubJaw": [0.6, 1.0], "earS": [1.0, 1.12], "hairline": {"pick": [0.055, 0.06, 0.065, 0.085, 0.11]}})
kind("woman", "Woman", "a woman's head: the face shorter, the jaw narrower with a more open angle, the chin small, the forehead upright and smooth, the brows higher and arched over the orbit, the eyes a little larger and lifted at the outer corner, the nose shorter and finer with a more obtuse nasolabial angle, the lips fuller, the cheeks rounder",
     {"faceHeight": [0.108, 0.118], "upperWidth": [0.126, 0.134], "lowerWidth": [0.086, 0.095], "chinWidth": [0.036, 0.042], "jawAngle": [123, 130], "foreheadAngle": [4, 10],
      "browRidge": [0.0, 0.002], "browHeight": [0.016, 0.02], "browArch": [0.003, 0.006], "browThickness": [0.004, 0.0055],
      "noseHeight": [0.046, 0.051], "noseWidth": [0.029, 0.033], "noseProjection": [0.017, 0.02], "nasolabialAngle": [100, 112], "noseBridge": [0.002, 0.004],
      "mouthWidth": [0.047, 0.052], "upperVermilion": [0.008, 0.01], "lowerVermilion": [0.009, 0.011], "upperLipHeight": [0.018, 0.021], "lowerLipHeight": [0.017, 0.019],
      "eyeDistance": [0.031, 0.034], "eyeWidth": [0.029, 0.032], "eyeHeight": [0.01, 0.012], "eyeTilt": [3, 7], "chinHeight": [0.011, 0.014],
      "chubCheek": [1.1, 1.4], "chubby": [1.0, 1.15], "chubLips": [1.2, 1.5], "earS": [0.9, 1.0], "hairline": [0.05, 0.06],
      "flower": {"pick": [0, 0, 0, 1]}, "hairFlower": {"pick": ["items/flowers/blooms/rose", "items/flowers/blooms/daisy", "items/flowers/blooms/hibiscus", "items/flowers/blooms/frangipani",
                                                               "items/flowers/blooms/poppy", "items/flowers/blooms/cornflower", "items/flowers/blooms/lily"]}})
kind("child", "Child", "a child's head: the cranium large for the face (the face short and small within it), the forehead high, upright and round, the eyes large and set wide, the nose small, short and turned up, the mouth small, the jaw and chin small with an open angle, everything rounder",
     {"scale": [0.82, 0.9], "faceHeight": [0.096, 0.104], "foreheadHeight": [0.064, 0.07], "foreheadAngle": [-2, 4], "upperWidth": [0.122, 0.13], "lowerWidth": [0.082, 0.088], "chinWidth": [0.034, 0.038], "jawAngle": [126, 132],
      "browRidge": 0, "browHeight": [0.015, 0.018], "browArch": [0.002, 0.004], "browThickness": [0.0035, 0.0045],
      "noseHeight": [0.038, 0.042], "noseWidth": [0.027, 0.03], "noseProjection": [0.012, 0.015], "nasolabialAngle": [105, 115], "noseBridge": 0,
      "mouthWidth": [0.04, 0.044], "upperLipHeight": [0.015, 0.017], "lowerLipHeight": [0.014, 0.016], "upperVermilion": [0.007, 0.008], "lowerVermilion": [0.008, 0.009], "chinHeight": [0.008, 0.01],
      "eyeDistance": [0.031, 0.034], "eyeWidth": [0.027, 0.029], "eyeHeight": [0.011, 0.012], "eyeDepth": [0.013, 0.015],
      "forehead": [1.03, 1.08], "crown": [1.06, 1.12], "chubCheek": [1.6, 2.0], "chubby": [1.2, 1.4], "chubJaw": [1.2, 1.5], "earS": [0.85, 0.95], "hairline": [0.06, 0.07], "neckR": 0.042})
kind("elder", "Elder", "an old head: the cheeks hollow under prominent cheekbones (the cheek pads gone: chubCheek below 0), jowls, the eyes deep-set under a heavier brow, the lids lower, the nose and ears grown and the nasal hump plain, the lips thinned, the hairline high or the crown bald, grey or white",
     {"faceHeight": [0.118, 0.128], "upperWidth": [0.13, 0.138], "lowerWidth": [0.094, 0.104], "jawAngle": [122, 130], "browRidge": [0.004, 0.007], "browHeight": [0.012, 0.015], "browThickness": [0.006, 0.009],
      "eyeDepth": [0.018, 0.021], "eyeHeight": [0.007, 0.009], "eyeTilt": [-2, 2], "noseHeight": [0.054, 0.06], "noseWidth": [0.036, 0.041], "noseProjection": [0.022, 0.026], "noseHump": [0.002, 0.006],
      "upperVermilion": [0.004, 0.006], "lowerVermilion": [0.005, 0.007], "mouthWidth": [0.05, 0.055], "chubCheek": [-0.6, 0.0], "chubby": [0.8, 1.0], "chubJaw": [1.0, 1.4],
      "earS": [1.1, 1.25], "hairline": {"pick": [0.085, 0.11, 0.2, 0.2]}},
     {"hairColour": {"pick": ["hair-grey", "hair-grey", "hair-white", "hair-brown"]}})
kind("beast-man", "Beast man", "a brute's head for a monster: the face long and wide, the jaw massive (a low, square angle) and the chin thrust out, the brow ridge heavy over a sloping forehead, the nose broad and flat with an acute nasolabial angle, the eyes small and close, the mouth wide, the ears large",
     {"scale": [1.05, 1.15], "faceHeight": [0.13, 0.14], "upperWidth": [0.148, 0.16], "lowerWidth": [0.118, 0.13], "chinWidth": [0.054, 0.06], "jawAngle": [108, 116], "foreheadAngle": [20, 28],
      "browRidge": [0.009, 0.013], "browHeight": [0.011, 0.013], "browThickness": [0.009, 0.012], "noseWidth": [0.045, 0.05], "noseProjection": [0.015, 0.019], "nasolabialAngle": [84, 94],
      "mouthWidth": [0.058, 0.064], "eyeDistance": [0.028, 0.031], "eyeWidth": [0.026, 0.028], "eyeHeight": [0.008, 0.009], "eyeDepth": [0.018, 0.021], "chinProjection": [0.004, 0.008],
      "chubby": [0.85, 0.95], "earS": [1.2, 1.4], "hairline": [0.04, 0.05], "forehead": [0.9, 0.96]},
     {"skin": {"pick": ["skin-tan", "skin-brown", "skin-olive", "#7a8a5a"]}})

MATERIALS = {
    "skin-pale": "#efd6c2", "skin-fair": "#e2b998", "skin-olive": "#cfa47e", "skin-tan": "#b8865e", "skin-brown": "#8e5f3e", "skin-dark": "#5c3b27",
    "lip-rose": "#b26b62", "lip-dark": "#7d443c", "lip-pink": "#c47c76", "lip-red": "#a8423f", "lip-brown": "#8a5348", "lip-pale": "#c99088", "mouth-dark": "#3a1c1a", "teeth-ivory": "#e6dfcc", "eye-white": "#efe9e0", "iris-limbus": "#24180f", "eye-glint": "#ffffff", "lash-dark": "#1c1512",
    "iris-brown": "#6b3d1e", "iris-hazel": "#8a6a2a", "iris-blue": "#4f86c4", "iris-green": "#5f9a48", "iris-grey": "#8a98a8", "iris-amber": "#b8742a", "pupil": "#0e0a08",
    "hair-black": "#1f1a17", "hair-brown": "#4a3222", "hair-chestnut": "#6b3f24", "hair-blond": "#c9a565", "hair-red": "#8c3d1f", "hair-grey": "#9a9a95", "hair-white": "#e2ddd3",
}


def main():
    for k, v in FACES.items():
        write("faces/" + k, v)
    mpath = os.path.join(ITEMS, "materials.json")
    lib = json.load(open(mpath))
    added = 0
    for k, v in MATERIALS.items():
        if k not in lib["materials"] or k.startswith("iris-"):
            lib["materials"][k] = {"pattern": "materials/paint", "palette": [v, v, v, v]}; added += 1
    json.dump(lib, open(mpath, "w"), indent=1, ensure_ascii=False)
    ipath = os.path.join(ROOT, "assets", "index.json")
    index = json.load(open(ipath))
    cats = {c["name"]: c for c in index["categories"]}
    if "Items: faces" not in cats:
        pos = index["categories"].index(cats["Items: ships"]) + 1
        index["categories"].insert(pos, {"name": "Items: faces", "kind": "item", "paths": []})
        cats = {c["name"]: c for c in index["categories"]}
    cats["Items: faces"]["paths"] = ["items/faces/" + k for k in FACES]
    json.dump(index, open(ipath, "w"), indent=2, ensure_ascii=False)
    print(len(FACES), "faces,", added, "materials added")


if __name__ == "__main__":
    main()
