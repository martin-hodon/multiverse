# THE PLATEAU'S PLAN, THE GREAT SPHINX AND KHAFRE'S VALLEY COMPLEX, written into assets/architecture/giza.json and
# assets/finishes/giza.json (the pyramids and their chambers were written by hand: this replaces only what it sets, so it
# can be run again).
#   THE PLAN, at the pyramids' own quarter scale, on the engine's compass (+x east, +z south, so north is -z): Khafre's
#   centre about 339m south and 322m west of Khufu's, Menkaure's about 740m south and 563m west, the Sphinx about 434m south
#   and 329m east (from the coordinates Wikipedia's four pages give, whole seconds of arc or so, so good to some tens of metres). Each pyramid is turned a half-circle (yaw pi): its entrance, its local +z, faces real north. That turns
#   the chamber, its sarcophagus and passage with it; `dig` and the murals' offsets follow here. (A chamber wall's name is
#   the builder's local one: "north" and "south" are true, "east" and "west" trade places.)
#   THE SPHINX, in lofts (assemble.js `loft`), at the same scale (real 73m long, 19m wide, 20m high): a lion's body lying
#   with its haunches and shoulders, forepaws run out in front with the Dream Stele between them, the nemes spreading at
#   the sides of a head small for the body, as it really is, and the face with its broken nose. Before it the Sphinx
#   Temple; south of that the Valley Temple, Khafre's causeway up to his mortuary temple at the pyramid's east face.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "assets", "architecture", "giza.json")
PF = os.path.join(ROOT, "assets", "finishes", "giza.json")
doc = json.load(open(P)); fin = json.load(open(PF))
Q = math.pi / 2
r3 = lambda v: round(v, 3)
# ---- the plan
PY = {"khufu": (0.0, 0.0, -3.6, 22.572, 28.837), "khafre": (-80.5, 85.0, -5.5, 20.697, 26.963), "menkaure": (-141.0, 185.0, -1.7, 6.559, 12.825)}   # x, z, the sarcophagus's local x, the dig's local z
for k, (x, z, sx, d0, d1) in PY.items():
    doc["parts"][k]["at"] = [[x, 0, z, r3(math.pi)]]
    s = doc["parts"][k + " sarcophagus"]["at"][0]
    doc["parts"][k + " sarcophagus"]["at"] = [[r3(x - sx), s[1], z, s[3]]]     # (the turn takes local -x to +x)
doc["site"]["dig"] = [[r3(x - .95), r3(z - d1), r3(x + .95), r3(z - d0)] for (x, z, _, d0, d1) in PY.values()]
# (a wall's mural runs along it, the way it faces into the room, and its offset centres it: as the turned wall now looks)
OFF = {"south": lambda x, z: x, "north": lambda x, z: -x, "east": lambda x, z: z, "west": lambda x, z: -z}
for r in fin["rules"]:
    if r.get("offset") and isinstance(r.get("parts"), str):
        w = r["parts"].split()
        if w[0] in PY: r["offset"] = [OFF[w[2]](PY[w[0]][0], PY[w[0]][1]), 0]
# ---- the Sphinx
NEW = "sphinx "
for n in [n for n in doc["parts"] if n.startswith(NEW) or n in ("khafre causeway", "khafre mortuary temple", "khafre valley temple")]: del doc["parts"][n]
doc["build"] = [n for n in doc["build"] if n in doc["parts"]]
CX, CZ = 82.0, 108.5                # the Sphinx's middle: it looks east, along +x
def add(n, d): doc["parts"][n] = d; doc["build"].append(n)
AT = [[CX, 0, CZ, r3(Q)]]            # (local: x across, z along it, the head's end +z; yaw pi/2 turns +z to east, +x to north)
def sec(s, a, b, v=0.0, u=0.0, n=2.0): return {"s": s, "u": u, "v": v, "a": a, "b": b, "n": n}
def loft(n, axis, secs, sides=16, smooth=3, about=None):
    add(NEW + n, {"type": "loft", "axis": axis, "sides": sides, "smooth": smooth, "sections": secs, "at": AT, **({"_about": about} if about else {})})
def box(n, x, y0, z, w, l, h, about=None):
    add(NEW + n, {"type": "box", "width": w, "length": l, "height": h, "at": [[r3(CX + z), y0, r3(CZ - x), r3(Q)]], **({"_about": about} if about else {})})
add(NEW + "rock bed", {"type": "prism", "plan": {"rect": [5.6, 19.0], "chamfer": .3}, "height": .4, "at": [[r3(CX - 1.3), 0, CZ, r3(Q)]],
                       "_about": "the rock floor it was cut from: at the pyramids' quarter scale, 18m of the real 73"})
loft("body", "z", [sec(-10.3, .3, .3, 1.0, n=2.4), sec(-9.9, 1.5, 1.2, 1.2, n=2.4), sec(-8.4, 2.1, 1.75, 1.6, n=2.4), sec(-6.0, 2.0, 1.4, 1.55, n=2.4), sec(-2.5, 2.05, 1.55, 1.7, n=2.4),
                  sec(1.0, 2.25, 1.85, 1.85, n=2.4), sec(2.8, 2.2, 1.85, 1.85, n=2.4), sec(3.6, 1.6, 1.6, 1.8, n=2.4), sec(4.1, .5, .8, 1.7, n=2.4)], sides=20,
     about="the lion's body, lying: the rump, the long loin, the shoulders standing higher, the chest's prow")
for sx, nm in ((1, "right"), (-1, "left")):
    loft(f"haunch {nm}", "z", [sec(-9.7, .3, .4, 1.3, sx * 1.85), sec(-8.8, .7, 1.05, 1.45, sx * 2.0), sec(-7.2, .75, 1.15, 1.45, sx * 2.05), sec(-5.6, .45, .7, 1.05, sx * 1.95), sec(-3.2, .4, .4, .75, sx * 1.95), sec(-2.8, .1, .1, .7, sx * 1.95)], sides=12, smooth=2,
         about="the haunch and the hind leg drawn along the flank")
    loft(f"shoulder {nm}", "z", [sec(-.4, .2, .4, 2.0, sx * 2.1), sec(.8, .45, 1.2, 1.8, sx * 2.2), sec(2.5, .45, 1.2, 1.5, sx * 2.05), sec(3.5, .2, .6, 1.0, sx * 1.6)], sides=12, smooth=2)
    loft(f"forepaw {nm}", "z", [sec(2.2, .6, .6, 1.0, sx * 1.3), sec(4.5, .6, .52, .9, sx * 1.3), sec(7.0, .62, .48, .85, sx * 1.3), sec(7.6, .5, .36, .75, sx * 1.3), sec(7.85, .12, .1, .65, sx * 1.3)], sides=12, smooth=2)
    loft(f"lappet {nm}", "y", [sec(2.75, .28, .12, 3.05, sx * .85, n=5), sec(3.95, .3, .14, 3.05, sx * .82, n=5), sec(4.1, .1, .05, 3.05, sx * .8, n=5)], sides=12, smooth=1)
loft("neck", "y", [sec(2.9, 1.05, .95, 2.25, n=2.4), sec(4.1, .72, .72, 2.3)], sides=14, smooth=1)
loft("nemes", "y", [sec(3.1, 1.25, .8, 2.35, n=2.8), sec(3.65, 1.25, .85, 2.35, n=2.8), sec(4.2, 1.0, .85, 2.35, n=2.6), sec(4.7, .74, .82, 2.35, n=2.6), sec(5.02, .58, .7, 2.35, n=2.4), sec(5.14, .15, .2, 2.35)], sides=20,
     about="the nemes, the king's headcloth: flat over the crown, spreading in wings beside the face to the lappets")
loft("face", "y", [sec(3.58, .14, .22, 3.03), sec(3.75, .37, .48, 3.03), sec(4.1, .5, .62, 3.03), sec(4.5, .53, .62, 3.03), sec(4.85, .47, .56, 3.03), sec(5.0, .3, .35, 3.03)], sides=18,
     about="the face, about a quarter of its real 4m wide")
loft("nose", "y", [sec(4.12, .13, .1, 3.64), sec(4.4, .09, .1, 3.64), sec(4.5, .03, .03, 3.62)], sides=10, smooth=1, about="what is left of the nose: long gone, its root and its breadth")
for sx, nm in ((1, "right"), (-1, "left")):
    box(f"brow {nm}", sx * .25, 4.48, 3.58, .28, .1, .05)
    box(f"eye {nm}", sx * .25, 4.4, 3.595, .16, .05, .05)
box("mouth", 0, 3.97, 3.61, .3, .05, .03)
box("stele", 0, .4, 5.6, 1.1, .16, .95, about="the Dream Stele of Thutmose IV between the paws")
# the temples and the causeway, low and square: Old Kingdom masonry
add(NEW + "temple", {"type": "box", "width": 9.0, "length": 8.5, "height": 2.2, "at": [[r3(CX + 9.0 + .6 + 4.25), 0, CZ, r3(Q)]], "_about": "the Sphinx Temple before its paws"})
VX, VZ = CX + 3, CZ + 11.5
add("khafre valley temple", {"type": "box", "width": 11.0, "length": 11.0, "height": 3.2, "at": [[r3(VX), 0, r3(VZ), 0]], "_about": "Khafre's Valley Temple beside the Sphinx, to its south, in pink granite"})
KX, KZ = PY["khafre"][:2]
MX, MZ = KX + 53.825 / 2 + 3.5, KZ   # his mortuary temple, against the pyramid's east face
add("khafre mortuary temple", {"type": "box", "width": 8.0, "length": 11.0, "height": 2.6, "at": [[MX, 0, MZ, 0]], "_about": "Khafre's mortuary temple against the pyramid's east face"})
ax, az, bx, bz = MX + 4, MZ, VX - 5.5, VZ
add("khafre causeway", {"type": "prism", "plan": {"rect": [1.6, r3(math.hypot(bx - ax, bz - az))]}, "height": .55, "walked": True,
                        "at": [[r3((ax + bx) / 2), 0, r3((az + bz) / 2), r3(math.atan2(bx - ax, bz - az))]],
                        "_about": "the causeway down from the mortuary temple to the Valley Temple"})
# the three queens' pyramids south of Menkaure's, in a line east to west, as the photographs have them in front of his
QX, QZ = PY["menkaure"][0], PY["menkaure"][1] + 33.0
for n in [n for n in doc["parts"] if n.startswith("queen ")]: del doc["parts"][n]
doc["build"] = [n for n in doc["build"] if n in doc["parts"]]
for i, (dx, b, h) in enumerate(((13.0, 11.0, 6.7), (0.0, 7.8, 4.8), (-11.0, 7.8, 4.8))):
    add(f"queen {i + 1}", {"type": "pyramid", "base": b, "height": h, "at": [[r3(QX + dx), 0, QZ, 0]],
                           **({"_about": "the queens' small pyramids"} if i == 0 else {})})
DARK = [NEW + n for n in ("eye right", "eye left", "mouth")]
BODY = [n for n in doc["parts"] if n.startswith(NEW) and n not in DARK and n not in (NEW + "temple", NEW + "stele", NEW + "nemes", NEW + "lappet right", NEW + "lappet left", NEW + "rock bed")]
rules = [r for r in fin["rules"] if not (r.get("_sphinx") or (isinstance(r.get("parts"), list) and "sphinx rock bed" in r["parts"]))]
rules[:0] = [
  {"_sphinx": True, "parts": DARK, "color": "#7d6642", "accent": "#6a5636", "_about": "the eyes and the mouth: their shadow, cut into the stone"},
  {"_sphinx": True, "parts": [NEW + "nemes", NEW + "lappet right", NEW + "lappet left"], "pattern": "stone/ashlar", "palette": "sandstone", "scale": .5, "_about": "the nemes: its stripes, in the beds it was cut through"},
  {"_sphinx": True, "parts": BODY, "pattern": "stone/ashlar", "palette": "sandstone", "scale": .6, "_about": "the Sphinx: the plateau's own yellow limestone, in its beds"},
  {"_sphinx": True, "parts": ["queen 1 core", "queen 2 core", "queen 3 core"], "pattern": "stone/plaster", "palette": "limestone", "_about": "the queens' pyramids"},
  {"_sphinx": True, "parts": [NEW + "rock bed", NEW + "stele"], "pattern": "stone/ashlar fine", "palette": "limestone"},
]
fin["rules"] = rules
doc["_about"] = "Khufu's, Khafre's and Menkaure's pyramids at a quarter of their size, on the plateau's real plan, each entrance facing north: the stepped core, the white Tura casing near the top, a gilded pyramidion; in each a passage from the north face to a burial chamber painted with tomb scenes; the Great Sphinx, the queens' pyramids, Khafre's causeway and temples (Egypt, -2560 -- -2510)"
with open(P, "w") as f: json.dump(doc, f, indent=1); f.write("\n")
with open(PF, "w") as f: json.dump(fin, f, indent=1, ensure_ascii=False); f.write("\n")
print("giza:", len(doc["parts"]), "parts")
