# named.py SPECIES... : the user's named exemplars converted to the sharp types (sharp.js). Run once per species (it
# reads the shapes it replaces from the file: a second run finds them gone and stops)
import sys
from conv import *

def replace(sp, ids, make):
    txt, d = load(sp); sh = d["sculpt"]["shape"]
    idx = [i for i, s in enumerate(sh) if s.get("id") in ids]
    if not idx: print(sp, "nothing to convert:", ids); return
    old = {s["id"]: s for s in sh if s.get("id") in ids}
    new = make(old)
    out = sh[:idx[0]] + new + [s for i, s in enumerate(sh) if i > idx[0] and s.get("id") not in ids]
    save(sp, out, txt); print(sp, "converted", sorted(old), "->", [s["id"] + ":" + s["type"] for s in new])

def boar():
    replace("mammals/boar", ["tusk", "tuskd"], lambda o: [horn_of(
        [[1.078, 0.418, 0.024, 0.0135], [1.1, 0.43, 0.05, 0.0135], [1.1198, 0.4483, 0.0627, 0.013], [1.1329, 0.4784, 0.0791, 0.0122],
         [1.128, 0.51, 0.09, 0.0105], [1.1117, 0.5364, 0.0949, 0.0065], [1.1, 0.549, 0.0962, 0.0]],
        {**o["tuskd"], "id": "tusk"}, up=[1, 0, 0], aspect=0.85, flat=0.25, keel=0.12, twist=-25, tip="#f6f2e8", tipAt=0.55)])
    ears("mammals/boar", ["ear", "earTuft", "earIn"], tip="@crest", tipAt=0.72, point=0.85, inner=None, cup=0.35)

def walrus():
    replace("sea/walrus", ["tusk0", "tusk1", "tusk2", "tusk3"], lambda o: [horn_of(
        [o["tusk0"]["a"] + [0.038], o["tusk1"]["a"] + [0.0291], o["tusk2"]["a"] + [0.0214], o["tusk3"]["a"] + [0.0141],
         lerp(o["tusk3"]["a"], o["tusk3"]["b"], 0.6) + [0.0075], o["tusk3"]["b"] + [0.0]],
        {**o["tusk0"], "id": "tusk"}, up=[1, 0, 0], aspect=1.25, tip="#f2ead6", tipAt=0.6)])

def elephant():
    replace("mammals/elephant", ["tusk"], lambda o: [horn_of(
        [[2.34, 1.99, 0.21, 0.09], [2.62, 1.72, 0.28, 0.08], [2.92, 1.56, 0.33, 0.066], [3.12, 1.585, 0.333, 0.05], [3.26, 1.64, 0.33, 0.026], [3.31, 1.67, 0.328, 0.0]],
        o["tusk"], up=[0, 1, 0], aspect=0.95, tip="#e4d9bc", tipAt=0.7)])

def crane(sp, root, mid1, mid2, tip, wu, hu, wl, hl, ltip, fair=None):
    """a crane's bill: two horns either side of the line its mandibles close on (root -> tip, x y), each flat there"""
    FAIR = {"fair": {"r": fair}} if fair else {}   # (the root faired into the face)
    line = lambda pts, dy: [[p[0], p[1] + dy, 0.0, p[2]] for p in pts]
    up = line([root + [wu], mid1 + [wu * 0.8], mid2 + [wu * 0.5], tip + [0.0]], 0.0005)
    lo = line([root + [wl], mid1 + [wl * 0.78], mid2 + [wl * 0.48], ltip + [0.0]], -0.0005)
    replace(sp, ["upperBill", "lowerBill"], lambda o: [
        horn_of(up, o["upperBill"], up=[0, 1, 0], aspect=hu / wu, flat=1, keel=0.06, sides=14, **FAIR),
        horn_of(lo, o["lowerBill"], up=[0, -1, 0], aspect=hl / wl, flat=1, sides=14, **FAIR)])

def stork():
    """(2026-11-08 evening) the white stork's LOWER mandible re-pointed as the crane's was: it stopped 5 cm short of the
    upper's tip, its radius dropping from 7 mm to 0 in 5 mm (a cut-off, blunt end). Now it runs on along the commissure
    -- the upper's own centreline, 0.6 mm under it -- tapering steadily like the upper, its point 5 mm behind and just
    under the upper's. The upper is kept as bills.py made it."""
    lo = [[0.3393, 0.9424, 0.0, 0.0182, 1.315], [0.3478, 0.939, 0.0, 0.0182, 1.315], [0.4368, 0.9037, 0.0, 0.0128, 1.45],
          [0.5068, 0.8783, 0.0, 0.0075, 1.6], [0.545, 0.8685, 0.0, 0.004, 1.5], [0.564, 0.8637, 0.0, 0.0, 1.5]]
    replace("birds/stork", ["lowerBill"], lambda o: [{**o["lowerBill"], "pts": lo}])

def ears(sp, ids, **kw):
    replace(sp, ids, lambda o: ear_fin(sp, o[ids[0]], ids + kw.pop("also", []), **kw))

SP = {
    "boar": boar, "walrus": walrus, "elephant": elephant,
    "crane": lambda: crane("birds/crane", [0.335, 1.1045], [0.41, 1.0917], [0.47, 1.0814], [0.525, 1.072], 0.0145, 0.0215, 0.013, 0.0155, [0.52, 1.072], fair=0.005),   # (2026-11-08: longer, slimmer -- the tip was .4913, wu/hu .019/.031)
    "crowned-crane": lambda: crane("birds/crowned-crane", [0.298, 0.9435], [0.3373, 0.9395], [0.3621, 0.9365], [0.3834, 0.9345], 0.0145, 0.0225, 0.0115, 0.015, [0.379, 0.9345]),
    "stork": stork,   # (re-runnable: it replaces the lower mandible in place)
    "zebra": lambda: ears("mammals/zebra", ["ear", "earIn"], inner="@earIn", tip="@mane", tipAt=0.8, point=0.75, cup=0.45),
    "kangaroo": lambda: ears("mammals/kangaroo", ["ear", "earIn"], inner="@earIn", point=0.9, cup=0.5, fillet=False),
    "giraffe": lambda: ears("mammals/giraffe", ["ear"], inner="@body", point=0.9, cup=0.4),
}
for a in sys.argv[1:]: SP[a]()
