# PRAMBANAN (Rara Jonggrang), Central Java, c. 850, Shaivite: the inner court of sixteen temples on its raised square, the
# second court of 224 perwara in four rows on terraces rising toward it, both walled and gated on the axes.
#
# East is +x, south +z; the Trimurti face east. Every temple is components/candi (javanese.py: the type's rules), sized by
# javanese.candi() from its width and height. Run it: writes assets/architecture/prambanan.json and assets/finishes/prambanan.json.
#
# SOURCED (Wikipedia id/en/de): Shiva 47 m high, 34 m wide, four stairs, the main one east, a central cella reached from
#   the east porch and three side chambers entered from their own stairs (Agastya south, Ganesha west, Durga north),
#   Shiva Mahadeva 3 m; the balustraded gallery with the Ramayana on its inner face and ratnas along it; Vishnu (north)
#   and Brahma (south) 33 m high, 20 m wide, one chamber, one stair east; the three vahana temples opposite (Nandi, Garuda,
#   Hamsa) facing west; two apit 14 m on 6 x 6 m between the rows at the north and south; four kelir behind the inner
#   gates and four patok at the corners, about 2 m; the inner court raised, square, gated on the axes; the second court
#   225 m a side holding 224 perwara in four rows of 44, 52, 60, 68, each 14 m on 6 x 6 m, the rows on terraces rising
#   toward the centre, facing outward. The roofs' ratnas in the vajra form.
# ESTIMATED: the inner court 110 m and its height, the terraces' heights and widths, the rows' spacing, the vahana
#   temples' sizes (Nandi 15 m wide x 25 m, Garuda and Hamsa 13 x 22), the positions within the inner court, all the
#   proportions candi() derives (base, body, roof tiers), the gates' sizes, the walls' heights. The outer (third) wall,
#   390 m and mostly lost, is left out.
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from javanese import candi, rot, finish_rules
from statuary import statue, pedestal, FACE_PZ, FACE_NZ, FACE_PX, FACE_NX
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
r4 = lambda v: round(v, 4)
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
E, S, W, N = math.pi / 2, 0.0, 3 * math.pi / 2, math.pi        # a candi's yaw to face east, south, west, north (its front is +z)

# ---- the courts ------------------------------------------------------------------------------------------------------
INNER = 110.0; Y0 = 2.4                       # the inner court: its side, its floor's height
OUTER = 225.0                                 # the second court's wall
TERR = [(72.5, 1.6), (82.5, 1.2), (92.5, 0.8), (102.5, 0.4)]    # the second court's terraces (half-side, top), inner first
ROWS = [(66.0, 12), (76.0, 14), (86.0, 16), (96.0, 18)]         # the perwara rows: half-side, temples a side (corners shared)

for i, (h, y) in reversed(list(enumerate(TERR))):
    add(f"terrace {i + 1}", {"type": "box", "width": 2 * h, "length": 2 * h, "height": y, "walked": True, "at": [[0, 0, 0, 0]],
                             "_about": f"the second court's {['first', 'second', 'third', 'fourth'][i]} terrace, the perwara's row on it" if i else "the second court's first terrace, the innermost row on it"})
add("inner court", {"type": "box", "width": INNER, "length": INNER, "height": Y0, "walked": True, "at": [[0, 0, 0, 0]],
                    "_about": "the inner court: raised over the second, its floor sand"})

# the flights up the terraces and onto the inner court, on the four axes
def axis_flights(name, half, base, top, width):
    rise = top - base; n = max(1, round(rise / 0.2)); run = 0.32; L = n * run
    ats = [[r4(v) for v in rot([width / 2, 0, half + L, math.pi / 2], q)] for q in range(4)]   # (foot outside the edge, climbing in; y its base's)
    add(name, {"type": "flight", "width": width, "run": run, "rise": r4(rise / n), "base": base, "top": top, "landing": 0, "at": ats,
               "_about": "the steps up on the axis"})
prev = 0.0
for i, (h, y) in reversed(list(enumerate(TERR))):
    axis_flights(f"terrace {i + 1} steps", h, prev, y, 5.0); prev = y
axis_flights("inner court steps", INNER / 2, TERR[0][1], Y0, 4.0)

# the walls and their gates
def court_wall(name, side, y, h, t, gate, about):
    add(name, {"type": "enclosure", "plan": {"rect": [side, side]}, "thickness": t, "height": h, "glass": False, "openings": [],
               "faces": {str(f): [{"at": 0, "width": gate, "sill": 0, "springing": h, "head": {"profile": "flat"}}] for f in range(4)},
               "at": [[0, y, 0, 0]], "courses": {"list": [{"y": h - 0.35, "h": 0.35, "out": 0.12, "profile": "cornice"}]}, "_about": about})
court_wall("inner wall", INNER, Y0, 2.4, 1.0, 3.6, "the inner court's wall, a gate on each axis")
court_wall("outer wall", OUTER, 0.0, 2.2, 1.0, 4.2, "the second court's wall, a gate on each axis")
def gates(name, half, y, p, about):
    add(name, {"type": "component", "use": "components/paduraksa", "params": p,
               "at": [[0, y, half, 0], [0, y, -half, 0], [half, y, 0, math.pi / 2], [-half, y, 0, math.pi / 2]], "_about": about})
gates("inner gates", INNER / 2 - 1.7, Y0, {"w": 7.0, "d": 3.4, "pw": 2.6, "ph": 3.4, "h": 10.5}, "the inner court's gates (paduraksa)")
gates("outer gates", OUTER / 2 - 1.5, 0.0, {"w": 6.5, "d": 3.0, "pw": 2.8, "ph": 3.4, "h": 8.5}, "the second court's gates (paduraksa)")

# ---- the inner court's sixteen ---------------------------------------------------------------------------------------
XT, XV, ZS = -10.0, 27.0, 35.0               # the Trimurti's row, the vahanas' row, the side temples off the axis
def temple(name, x, z, yaw, p, about):
    add(name, {"type": "component", "use": "components/candi", "params": p, "at": [[x, Y0, z, yaw]], "_about": about})
    TEMPLES[name] = p

SHIVA = candi(34, 47, stairs="four", gallery=True, cella="open", tiers=5, ratnas="seven")
VISHNU = candi(20, 33, stairs="one", gallery=True, cella="open", tiers=4, ratnas="five")
NANDI = candi(15, 25, stairs="one", gallery=True, cella="open", tiers=4, ratnas="five")
VAHANA = candi(13, 22, stairs="one", gallery=True, cella="open", tiers=4, ratnas="five")
APIT = candi(6, 14, stairs="one", gallery=False, cella="open", tiers=3, ratnas="three")
SMALL = candi(1.6, 2.0, stairs="none", gallery=False, cella="solid", tiers=3, ratnas="corners", far=True, crownform="vajra")
SHRINE = candi(1.8, 4.0, stairs="none", gallery=False, cella="solid", tiers=3, ratnas="corners", far=True, ratna="vajra", crownform="vajra")
TEMPLES = {}
temple("shiva", XT, 0.0, E, SHIVA, "Candi Shiva: 47 m, the main stair east to the porch before Shiva Mahadeva's cella, the side stairs to Agastya's (south), Ganesha's (west) and Durga's (north) chambers")
temple("vishnu", XT, -ZS, E, VISHNU, "Candi Vishnu, north of Shiva: 33 m, one chamber, its stair east")
temple("brahma", XT, ZS, E, VISHNU, "Candi Brahma, south of Shiva: Vishnu's twin")
temple("nandi", XV, 0.0, W, NANDI, "Candi Nandi, facing Shiva: the bull, with Chandra and Surya")
temple("garuda", XV, -ZS, W, VAHANA, "Candi Garuda, facing Vishnu")
temple("hamsa", XV, ZS, W, VAHANA, "Candi Hamsa (Angsa), facing Brahma")
temple("apit north", 8.5, -47.0, S, APIT, "the north apit ('flanking') temple, between the rows")
temple("apit south", 8.5, 47.0, N, APIT, "the south apit temple")

# the two shrines of the guardians Mahakala and Nandhisvara, on Shiva's gallery either side of the east porch, against the body
def world(x0, z0, yaw, lx, lz):              # a temple's local point into the site (yaw as three.js: +z goes to +x at E)
    c, s = math.cos(yaw), math.sin(yaw)
    return x0 + lx * c + lz * s, z0 - lx * s + lz * c
sx = SHIVA["pw"] / 2 + 0.6 + SHRINE["w"] / 2; sz = SHIVA["bw"] / 2 + SHRINE["w"] / 2 + 0.2
add("guardian shrines", {"type": "component", "use": "components/candi", "params": SHRINE,
                         "at": [[r4(x), r4(Y0 + SHIVA["bh"]), r4(z), E] for x, z in (world(XT, 0.0, E, -sx, sz), world(XT, 0.0, E, sx, sz))],
                         "_about": "the shrines of Mahakala and Nandhisvara, the gate's guardians, on the gallery either side of Shiva's east porch"})
TEMPLES["guardian shrines"] = SHRINE

# the kelir (just inside each inner gate, so no one walks straight in) and the patok (at the court's corners): miniature
# candi, two metres, no stairs
KH = INNER / 2 - 6.0; PH = INNER / 2 - 4.0
add("kelir", {"type": "component", "use": "components/candi", "params": SMALL,
              "at": [[0, Y0, KH, N], [0, Y0, -KH, S], [KH, Y0, 0, W], [-KH, Y0, 0, E]], "_about": "the kelir, inside each inner gate, facing in"})
add("patok", {"type": "component", "use": "components/candi", "params": SMALL,
              "at": [[sx_ * PH, Y0, sz_ * PH, 0] for sx_ in (1, -1) for sz_ in (1, -1)], "_about": "the patok, one at each corner of the inner court"})
TEMPLES["kelir"] = TEMPLES["patok"] = SMALL

# ---- the 224 perwara: one part, every row on its terrace, facing out (the corner ones north or south) -------------------
# (a corner one has two stairs and two porches, out both ways: its front and its right, +x -- turned so both face out)
PERWARA = candi(6, 14, stairs="one", gallery=False, cella="solid", tiers=3, ratnas="corners", far=True)
CORNER = {**PERWARA, "stairs": "two"}
at = []; corners = []; counts = []
for (half, n), (_, y) in zip(ROWS, TERR):
    step = 2 * half / (n - 1); c = 0
    for i in range(1, n - 1):
        u = -half + i * step
        at += [[r4(u), y, half, S], [r4(u), y, -half, N], [half, y, r4(u), E], [-half, y, r4(u), W]]; c += 4
    corners += [[half, y, half, S], [-half, y, half, W], [-half, y, -half, N], [half, y, -half, E]]; c += 4
    counts.append(c)
add("perwara", {"type": "component", "use": "components/candi", "params": PERWARA, "at": at,
                "_about": f"the perwara ('guardian') temples along the rows' sides, {len(at)}, each facing out"})
add("perwara corners", {"type": "component", "use": "components/candi", "params": CORNER, "at": corners,
                        "_about": "the perwara at the rows' corners, 16: two stairs and two porches each, out both ways"})

# ---- the gods in their cellas ----------------------------------------------------------------------------------------
def floor_y(p): return r4(Y0 + p["bh"] + 0.15)
def chamber(p, q):
    """the centre of the porch-chamber q quarter-turns from the front, in the temple's own frame (+z the front)"""
    d = p["bw"] / 2 + p["pd"] / 2
    return [(0, d), (d, 0), (0, -d), (-d, 0)][q]
def seen(rects): return [[r4(v) for v in r] for r in rects]
def god(name, x, z, y, face, kind, pose, scale, ped, seed, look):
    add(f"{name} pedestal", pedestal((x, y, z), ped, ped, 0.8, "the pedestal: a yoni, or a lotus throne"))
    parts[f"{name}"] = statue((x, y + 0.8, z), kind=kind, pose=pose, style="indian", stone="limestone", scale=scale, seed=seed, face=face, seen=seen(look))
    build.append(name)

yS = floor_y(SHIVA); cin = SHIVA["bw"] / 2 - SHIVA["wt"]
god("shiva mahadeva", XT, 0.0, yS, FACE_PX, "man", "stand", 1.7, 1.6, 1, [[-cin, cin, -cin, cin], [0, 60, -2.5, 2.5]])
for nm, q, kind, pose, face, seed in (("agastya", 3, "man", "stand", FACE_PZ, 2), ("ganesha", 2, "man", "sit", FACE_NX, 3), ("durga", 1, "woman", "stand", FACE_NZ, 4)):
    lx, lz = chamber(SHIVA, q); x, z = world(XT, 0.0, E, lx, lz)
    ph = SHIVA["pd"] / 2
    look = {FACE_PZ: [[-ph, ph, -ph, 40]], FACE_NZ: [[-ph, ph, -40, ph]], FACE_NX: [[-40, ph, -ph, ph]]}[face]
    god(nm, r4(x), r4(z), yS, face, kind, pose, 1.05, 1.0, seed, look)
yV = floor_y(VISHNU); vin = VISHNU["bw"] / 2 - VISHNU["wt"]
for nm, z, seed in (("vishnu god", -ZS, 5), ("brahma god", ZS, 6)):
    god(nm, XT, z, yV, FACE_PX, "man", "stand", 1.6, 1.3, seed, [[-vin, vin, -vin, vin], [0, 50, -2, 2]])

# ---- write --------------------------------------------------------------------------------------------------------------
doc = {
    "name": "Prambanan",
    "_about": "PRAMBANAN (Rara Jonggrang), Central Java, c. 850: Shiva's temple 47 m high between Vishnu's and Brahma's, the "
              "vahana temples facing them, the apit, kelir and patok, all on the raised inner court; round it the second "
              "court's 224 perwara in four rows on terraces rising toward the centre, every one facing out. Every temple is "
              "components/candi (base and gallery, body and porches, a roof of tiers ringed with ratnas). Generated by "
              "tools/archgen/prambanan.py (sizes it does not source are estimated there) -- edit the script. East is +x, south +z.",
    "params": {"detail": 4},
    "base": {"height": 0.2, "steps": 1, "stepOut": 0.5, "margin": 8},
    "railing": {"type": "stone", "height": 0.9},
    "build": build,
    "parts": parts,
}
out = os.path.join(ROOT, "assets", "architecture", "prambanan.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")

# ---- the finish ---------------------------------------------------------------------------------------------------------
A = "andesite"
fin = {
    "name": "Prambanan",
    "building": "architecture/prambanan",
    "_about": "Prambanan's surfaces: grey andesite throughout, darkened by lichen; the base wrapped in the 'Prambanan motif' "
              "(lions in niches between wishing trees), the balustrade's inner face in the Ramayana's panels, the body's walls "
              "in deities in niches between pilasters, the roof tiers and ratnas in fine courses; the inner court's floor sand, "
              "the second court's terraces grass, its perwara plain blocks (most of them still rubble today).",
    "stone": {"color": "#5d5c58", "accent": "#4a4946", "pat": "ashlar"},
    "rules": [
        {"parts": ["inner court"], "surface": "floor", "pattern": "stone/sand", "palette": "marble-grey", "_about": "the inner court's light grey gravel"},
        {"parts": ["terrace 1", "terrace 2", "terrace 3", "terrace 4"], "surface": "floor", "color": "#5c7a3f", "accent": "#4e6a35", "pat": "marble",
         "_about": "the second court's terraces: grass"},
        *[r for name, p in TEMPLES.items() for r in finish_rules(name, p, A)],
        *finish_rules("perwara", PERWARA, A), *finish_rules("perwara corners", CORNER, A),
        {"parts": ["inner gates", "outer gates", "kind:column"], "pattern": "stone/ashlar fine", "palette": A},
        {"surface": "floor", "pattern": "floors/flagstones", "palette": A},
        {"surface": "wall", "pattern": "stone/ashlar", "palette": A},
        {"pattern": "stone/ashlar", "palette": A},
    ],
}
fout = os.path.join(ROOT, "assets", "finishes", "prambanan.json")
with open(fout, "w") as f:
    json.dump(fin, f, indent=1)
    f.write("\n")
print("wrote", os.path.relpath(out, ROOT), len(parts), "parts,", len(at) + len(corners), "perwara", counts, "and", os.path.relpath(fout, ROOT))
for nm, p in (("shiva", SHIVA), ("vishnu", VISHNU), ("nandi", NANDI), ("vahana", VAHANA), ("apit", APIT), ("small", SMALL), ("shrine", SHRINE), ("perwara", PERWARA)):
    print(nm, {k: p[k] for k in ("bh", "bw", "wt", "bH", "cs", "pw", "pd", "t1", "ch", "sw", "dw", "dh")})
