#!/usr/bin/env python3
"""THE TEMPLE OF HATHOR, DENDERA (Ptolemaic, 54 BC - AD 20), at its real size, as an arch-engine definition, set out by
the rules an Egyptian temple is built by rather than as a stack of blocks:

  THE AXIS. The temple is a sequence of rooms on one line, from the open forecourt to the dark sanctuary: the
    pronaos (the Roman hypostyle built against the old facade), the Hall of Appearances with its six columns and the
    store rooms either side, the Hall of Offerings, the Hall of the Ennead, and the sanctuary standing free in its
    corridor at the back. Going in, every FLOOR RISES a few steps and every ROOF COMES DOWN -- the light falls away
    and the ground climbs toward the god, the primeval mound the sanctuary stands for. Each step up is a short
    flight before a door and a threshold through it; each roof is lower than the last, so the roof terraces step down.
  THE WALL. Every outer face is BATTERED (it leans back about 1 in 12, a mud-brick habit kept in stone), a TORUS roll
    runs round its top, and the CAVETTO -- the gorge cornice, the palm fronds bending out over a reed wall -- crowns
    it, all sized from the wall's own height (crown()). The roof lies inside the parapet the gorge crowns.
  THE HYPOSTYLE. The columns stand in files with the middle intercolumniation wider (the processional way); the
    ARCHITRAVES run over the files from front to back and the roof slabs span across between them -- the roof is
    carried, slab on beam on column, never laid on air. The pronaos's front row stands in the open facade, joined by
    the half-height SCREEN WALLS with their own little gorges, the middle bay a door whose lintel is broken in two.
    Pronaos columns are HATHORIC (the four-faced goddess under her sistrum), the inner hall's CAMPANIFORM.
  THE ROOFS rest on the cross walls: each hall's slabs on the wall behind it, which is built up to that hall's ceiling,
    the lower hall behind abutting its face -- so the roof falls in steps exactly where the walls are.

    python3 tools/archgen/dendera.py      # -> assets/architecture/dendera.json, assets/finishes/dendera.json
"""
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
r4 = lambda v: round(v, 4)
QUARTER = r4(math.pi / 2)

# ---- the measures (metres) --------------------------------------------------------------------------------------
B = 0.6                                       # the platform's top: the temple's ground
L = 81                                        # the whole length, front of the pronaos to the back wall
Wp, Dp, tP = 42, 25, 2.6                      # the pronaos: width, depth, wall thickness
Wi, ti = 35, 2.4                              # the temple proper: width, outer wall thickness
RISE = 0.15                                   # every step up toward the sanctuary
slab = 0.9                                    # a roof slab

zF = L / 2                                    # the pronaos's front face
zJ = zF - Dp                                  # where the pronaos stands against the old facade
zB = -L / 2                                   # the back wall's outer face


def crown(H, gorge=None):
    """THE EGYPTIAN WALL'S MOULDINGS from its height: the gorge (a ninth of it, within reason) standing out three quarters
    of its height, the torus a quarter of the gorge under it, and the BATTER from the ground up to the torus, leaning
    back 1 in 12 -- a list of courses (courses.js profiles batter, torus, gorge)."""
    g = gorge if gorge is not None else max(0.5, min(2.2, H * 0.11))
    th = g * 0.25
    bh = H - g - th
    out = [{"y": r4(bh), "h": r4(th), "out": r4(th / 2), "profile": "torus"},
           {"y": r4(H - g), "h": r4(g), "out": r4(g * 0.75), "profile": "gorge"}]
    return ([{"y": 0, "h": r4(bh), "out": r4(bh / 12), "profile": "batter"}] if bh > 2 else []) + out


def door(width, height, at=0):
    return {"at": r4(at), "width": r4(width), "sill": 0, "springing": r4(height), "head": {"profile": "flat"}, "glass": False}


parts, build = {}, []
def add(name, d):
    parts[name] = d
    build.append(name)


def step_up(name, z_face, lo, hi, width, depth):
    """A STEP UP AT A DOOR: a short flight on the lower side climbing to the wall's face (toward -z), and the threshold
    through the doorway at the higher floor -- `z_face` the face it climbs to, the wall(s) `depth` thick behind it."""
    n = max(1, round((hi - lo) / RISE))
    add(f"{name} steps", {"type": "flight", "width": width, "run": 0.32, "rise": r4((hi - lo) / n), "base": r4(B + lo), "top": r4(B + hi), "landing": 0,
                          "at": [[r4(width / 2), 0, r4(z_face + n * 0.32), QUARTER]]})
    add(f"{name} threshold", {"type": "box", "width": width, "length": r4(depth), "height": r4(B + hi), "walked": True,
                              "at": [[0, 0, r4(z_face - depth / 2), 0]]})


# ---- the PRONAOS ------------------------------------------------------------------------------------------------
# six Hathor columns across, four rows deep; the front row in the open facade, the end ones against its piers
rP, nP, rowsP = 1.15, 6, 4
pier = tP + 0.8                               # the facade's end piers, a little wider than the side walls
Wo = Wp - 2 * pier                            # the open facade between them
s = (Wo - 2 * rP) / (nP - 2 + 1.3)            # the intercolumniation; the middle one 1.3 times it
naveP = 1.3 * s
zRow0 = zF - tP / 2                           # the front row stands in the middle of the facade's thickness
zFrontIn, zBackIn = zF - tP, zJ + tP          # the facade's and the back wall's inner faces
rsP = (zRow0 - zBackIn) / (rowsP - 1 + 0.55)  # the rows, the last a little over half a bay from the back wall
Hc, archP = 14.6, 1.5                         # a column (its disc to its abacus), the architraves on it
roofP = Hc + archP                            # the slabs' soffit
Hp = roofP + slab + 1.4                       # the walls: up past the roof into the parapet the gorge crowns
gP = 2.1                                      # its gorge, the great cornice of the facade

add("platform", {"type": "box", "width": Wp + 6, "length": L + 6, "height": B, "walked": True, "at": [[0, 0, 0, 0]],
                 "_about": "the temple's low platform, the ground every floor inside rises from"})
nS, wS = round(B / RISE), r4(naveP - 2 * rP)
add("platform steps", {"type": "flight", "width": wS, "run": 0.32, "rise": r4(B / nS), "base": 0, "top": B, "landing": 0,
                       "at": [[r4(wS / 2), 0, r4(zF + 3 + nS * 0.32), QUARTER]],
                       "_about": "up onto the platform on the axis, before the open middle bay"})
add("pronaos", {"type": "enclosure", "plan": {"rect": [Wp, Dp]}, "thickness": tP, "height": r4(Hp), "glass": False,
                # (its open facade's architraves: the processional way between the middle columns is spanned by
                #  sandstone beams of six metres -- the Egyptian quarries gave what no other builders set)
                "beam": 6.5,
                "faces": {"0": [door(Wo, Hc)], "2": [door(3.2, 6.5)], "1": [], "3": []},
                "courses": {"list": crown(Hp, gP),
                            # (its back face stands against the old facade up to that one's height: the batter stops
                            #  there, its torus and gorge running on above the lower roof)
                            "clear": {"2": [[r4((Wp - Wi) / 2), r4((Wp + Wi) / 2), -1, r4(Hp - gP * 1.25 - 0.01)]]}},
                "at": [[0, B, r4(zF - Dp / 2), 0]],
                "_about": "the Roman hypostyle's walls: the facade open between its end piers over the front row of columns, the wall over them the great architrave and gorge; the door at the back into the old temple"})
add("pronaos columns", {"type": "colonnade", "order": "hathoric", "plan": "grid", "count": nP, "spacing": r4(s), "nave": r4(naveP),
                        "rows": rowsP, "rowSpacing": r4(rsP), "columnR": rP, "height": Hc, "sides": 16,
                        "entablature": {"h": archP, "depth": r4(rP * 1.6), "reach": [r4(zFrontIn - zRow0), r4(zRow0 - (rowsP - 1) * rsP - zBackIn)]},
                        "at": [[0, B, r4(zRow0 - (rowsP - 1) * rsP / 2), 0]],
                        "_about": "24 Hathor columns, the middle aisle wider; the architraves over the files from the facade to the back wall"})
add("pronaos roof", {"type": "box", "width": r4(Wp - 2 * tP), "length": r4(zFrontIn - zBackIn), "height": slab, "walked": True, "flatRoof": True,
                     "at": [[0, r4(B + roofP), r4((zFrontIn + zBackIn) / 2), 0]], "_about": "the slabs, across between the architraves"})
# the screen walls between the front row: under half the column's height, a gorge of their own; the middle bay a door
xsP = [k * s + (1 if k > 0 else -1) * (naveP - s) / 2 for k in [i - (nP - 1) / 2 for i in range(nP)]]
Hs, ts = 6.4, 1.0
for i in range(nP - 1):
    x0, x1 = xsP[i] + rP * 0.8, xsP[i + 1] - rP * 0.8
    mid = i == nP // 2 - 1
    add(f"screen {i + 1}", {"type": "wall", "width": r4(x1 - x0), "height": Hs, "thickness": ts, "glass": False,
                            "openings": [door(3.2, Hs, (x1 - x0) / 2)] if mid else [],
                            "courses": crown(Hs, 0.75),
                            "at": [[r4((x0 + x1) / 2), B, r4(zRow0 + ts / 2), 0]],
                            **({"_about": "the middle bay: a door through the screen, its lintel broken -- the jambs rise to the screen's cornice and stop"} if mid else {})})

# ---- THE TEMPLE PROPER: the halls on the axis, floors rising, roofs falling ----------------------------------
xIn = Wi / 2 - ti                             # the inner faces of its side walls
zI = zJ - ti                                  # the old facade's inner face
# each hall: its depth along the axis, how far its floor has risen, the soffit of its roof (both from the platform),
# and the cross wall behind it
halls = [
    {"name": "hall of appearances", "depth": 13.0, "floor": 3 * RISE, "soffit": 11.35, "wall": 1.6},
    {"name": "hall of offerings",   "depth": 6.5,  "floor": 5 * RISE, "soffit": 10.6,  "wall": 1.6},
    {"name": "hall of the ennead",  "depth": 6.0,  "floor": 7 * RISE, "soffit": 9.9,   "wall": 1.6},
]
z = zI
for h in halls:
    h["z1"], h["z0"] = z, z - h["depth"]
    z = h["z0"] - h["wall"]
sanct = {"name": "sanctuary court", "z1": z, "z0": zB + ti, "floor": 10 * RISE, "soffit": 9.2}
Hi = halls[0]["soffit"] + slab + 2.4          # the outer walls: past the highest roof into the parapet, the spouts under its torus
add("temple", {"type": "enclosure", "plan": {"rect": [Wi, zJ - zB]}, "thickness": ti, "height": r4(Hi), "glass": False,
               "faces": {"0": [door(3.2, 6.5)], "1": [], "2": [], "3": []},
               "courses": {"list": crown(Hi), "skip": ["0"]},
               "at": [[0, B, r4((zJ + zB) / 2), 0]],
               "_about": "the temple's outer walls, battered, torus and gorge round the top; its front (the old facade) hidden behind the pronaos"})

step_up("temple door", zBackIn, 0, halls[0]["floor"], 3.2, tP + ti)
for k, h in enumerate(halls):
    nm, nxt = h["name"], (halls[k + 1] if k + 1 < len(halls) else sanct)
    add(f"{nm} floor", {"type": "box", "width": r4(2 * xIn), "length": r4(h["depth"]), "height": r4(B + h["floor"]), "walked": True,
                        "at": [[0, 0, r4((h["z0"] + h["z1"]) / 2), 0]]})
    # the cross wall behind it, built up to this hall's soffit: its roof is laid on it, the lower roof behind abuts it
    add(f"{nm} back wall", {"type": "wall", "width": r4(2 * xIn), "height": r4(h["soffit"]), "thickness": h["wall"], "glass": False,
                            "openings": [door(2.8, 5.6 if k == 0 else 5.0, xIn)], "at": [[0, B, r4(h["z0"]), 0]]})
    step_up(nm, h["z0"], h["floor"], nxt["floor"], 2.8, h["wall"])

# the Hall of Appearances: six campaniform columns, a file either side of the axis, three deep; the store rooms
# either side behind partition walls, three a side, each with its door off the hall
ha = halls[0]
zcA, rA, archA, rowsA, rsA = (ha["z0"] + ha["z1"]) / 2, 0.9, 0.9, 3, 3.9
add("appearance columns", {"type": "colonnade", "order": "campaniform", "plan": "grid", "count": 2, "spacing": 7.6, "nave": 7.6,
                           "rows": rowsA, "rowSpacing": rsA, "columnR": rA, "height": r4(ha["soffit"] - archA - ha["floor"]), "sides": 14,
                           "entablature": {"h": archA, "depth": 1.4, "reach": [r4(ha["z1"] - zcA - rsA), r4(zcA - rsA - ha["z0"])]},
                           "at": [[0, r4(B + ha["floor"]), r4(zcA), 0]]})
roomD, tPart = 5.0, 1.2
xPart = xIn - roomD - tPart / 2               # the partitions' middle lines
cellL, hA = ha["depth"] / 3, ha["soffit"] - ha["floor"]
for sx in (-1, 1):
    side = "west" if sx < 0 else "east"
    # (turned a quarter so its length runs along the axis -- its front face on its line, its back toward the hall)
    add(f"{side} store partition", {"type": "wall", "width": r4(ha["depth"]), "height": r4(hA), "thickness": tPart, "glass": False,
                                    "openings": [door(1.4, 3.2, cellL * (j + 0.5)) for j in range(3)],
                                    "at": [[r4(sx * (xPart + tPart / 2)), r4(B + ha["floor"]), r4(zcA), r4(QUARTER * sx)]]})
    for j in (1, 2):
        add(f"{side} store wall {j}", {"type": "wall", "width": r4(roomD), "height": r4(hA), "thickness": 0.8, "glass": False,
                                       "at": [[r4(sx * (xIn - roomD / 2)), r4(B + ha["floor"]), r4(ha["z1"] - j * cellL + 0.4), 0]]})

# THE WAY TO THE ROOF (the New Year procession carried the goddess up to the sun): a newel stair in its own walled
# room off the Hall of Offerings, west of the axis, winding up through a well in that hall's roof onto its terrace
ho = halls[1]
zcO, room, tRoom, sR = (ho["z0"] + ho["z1"]) / 2, 3.6, 0.4, 1.3
xSt = -xIn + room / 2
hSt = ho["soffit"] - ho["floor"]
add("west stair room", {"type": "enclosure", "plan": {"rect": [room, room]}, "thickness": tRoom, "height": r4(hSt), "glass": False,
                        "faces": {"1": [door(1.0, 2.3)], "0": [], "2": [], "3": []},
                        "at": [[r4(xSt), r4(B + ho["floor"]), r4(zcO), 0]],
                        "_about": "the west stair's room, its door to the hall; the roof slab is laid on its walls"})
rise = hSt + slab
add("west stair", {"type": "spiral-stair", "radius": sR, "newel": 0.15, "turn": 28, "top": r4(rise), "steps": round(rise / 0.19), "soffit": 0.2,
                   "at": [[r4(xSt), r4(B + ho["floor"]), r4(zcO), QUARTER]],
                   "_about": "the spiral, from the hall's floor to its roof terrace, arriving on the slab round its well"})

# the roofs: each hall's slabs from the face of the wall before it over the wall behind it (the offerings hall's
# pierced by the stair's well)
for h in halls:
    zf, zb = h["z1"], h["z0"] - h["wall"]
    well = {"well": {"radius": sR + 0.1, "sides": 12, "at": [r4(xSt), r4(zcO - (zf + zb) / 2)]}} if h is ho else {}
    add(f"{h['name']} roof", {"type": "prism", "plan": {"rect": [r4(2 * xIn), r4(zf - zb)], **well}, "height": slab, "walked": True, "flatRoof": True,
                              "at": [[0, r4(B + h["soffit"]), r4((zf + zb) / 2), 0]]})

# ---- THE SANCTUARY, standing free in its corridor at the back, the goddess's shrine in it ---------------------
zcS = (sanct["z0"] + sanct["z1"]) / 2
add("sanctuary court floor", {"type": "box", "width": r4(2 * xIn), "length": r4(sanct["z1"] - sanct["z0"]), "height": r4(B + sanct["floor"]), "walked": True,
                              "at": [[0, 0, r4(zcS), 0]]})
sW, sD, sT, corridor = 6.0, 10.0, 1.2, 2.4
sz1 = sanct["z1"] - corridor                  # the sanctuary's front face
naosFloor = sanct["floor"] + 3 * RISE
add("sanctuary", {"type": "enclosure", "plan": {"rect": [sW + 2 * sT, sD + 2 * sT]}, "thickness": sT, "height": r4(sanct["soffit"] - sanct["floor"]), "glass": False, "interior": True,
                  "faces": {"0": [door(2.0, 4.4)], "1": [], "2": [], "3": []},
                  "at": [[0, r4(B + sanct["floor"]), r4(sz1 - (sD + 2 * sT) / 2), 0]],
                  "_about": "the Per-wer, the great seat: a room standing free, the corridor of the mysteries round it, its roof the lowest of all"})
step_up("sanctuary", sz1, sanct["floor"], naosFloor, 2.0, sT)
add("sanctuary inner floor", {"type": "box", "width": sW, "length": sD, "height": r4(B + naosFloor), "walked": True,
                              "at": [[0, 0, r4(sz1 - sT - sD / 2), 0]]})
add("sanctuary court roof", {"type": "box", "width": r4(2 * xIn), "length": r4(sanct["z1"] - sanct["z0"]), "height": slab, "walked": True, "flatRoof": True,
                             "at": [[0, r4(B + sanct["soffit"]), r4(zcS), 0]]})
# THE TERRACES joined: on each lower roof a short flight on the axis up to the next roof's edge, so the roof is one
# walk from the stair's head back down the steps to the kiosk -- each the step down its roofs make
terraces = [(h["name"], h["soffit"] + slab, h["z1"]) for h in halls] + [("sanctuary court", sanct["soffit"] + slab, sanct["z1"])]
for (upper, yU, _), (lower, yL, zL) in zip(terraces, terraces[1:]):
    n = max(1, round((yU - yL) / RISE))
    add(f"{lower} roof steps", {"type": "flight", "width": 2.0, "run": 0.32, "rise": r4((yU - yL) / n), "base": r4(B + yL), "top": r4(B + yU), "landing": 0,
                                "at": [[-1.0, 0, r4(zL - n * 0.32), r4(-QUARTER)]]})
# THE SPOUTS: every terrace drains through the side walls, a lion-headed spout either side for each twelve metres of
# its length, its channel at the roof's surface, under the torus
spans = [(h["name"], h["soffit"] + slab, h["z1"], h["z0"] - h["wall"]) for h in halls] + [("sanctuary court", sanct["soffit"] + slab, sanct["z1"], sanct["z0"])]
spouts = []
for nm, yT, z1, z0 in spans:
    k = max(1, round((z1 - z0) / 12))
    for j in range(k):
        zs = z1 - (z1 - z0) * (j + 0.5) / k
        for sx in (-1, 1):
            spouts.append([r4(sx * (Wi / 2 + 0.6)), r4(B + yT - 0.45), r4(zs), 0])
add("lion spouts", {"type": "box", "width": 1.2, "length": 0.5, "height": 0.45, "at": spouts,
                    "_about": "the roof's waterspouts, one per twelve metres of each terrace either side, at its surface"})

# THE ROOF KIOSK at the south-west corner of the lowest terrace: twelve Hathor columns in a square, screen walls
# between them, open on the side toward the axis -- where the goddess's image met the sun at the New Year
yK = B + sanct["soffit"] + slab
kA, kR, kH = 6.0, 0.32, 3.6
xK, zK = -xIn + kA / 2 + 1.2, sanct["z0"] + kA / 2 + 1.2
add("kiosk", {"type": "colonnade", "order": "hathoric", "plan": "peristyle", "front": 4, "side": 4, "width": kA, "length": kA,
              "columnR": kR, "height": kH, "sides": 10, "entablature": {"h": 0.6, "depth": 0.6, "cornice": {"h": 0.45, "out": 0.25}},
              "at": [[r4(xK), r4(yK), r4(zK), 0]]})
bay = kA / 3
for side, (cx, cz, yaw) in {"n": (0, kA / 2, 0), "s": (0, -kA / 2, math.pi), "w": (-kA / 2, 0, -math.pi / 2), "e": (kA / 2, 0, math.pi / 2)}.items():
    for j in range(3):
        if side == "e" and j == 1:
            continue                              # (the open bay, toward the axis)
        u = (j - 1) * bay                         # along the side, from its middle
        ux, uz = math.cos(yaw), -math.sin(yaw)    # (a wall's length runs along its own x)
        nx, nz = math.sin(yaw), math.cos(yaw)     # (its front face looks out along its own z)
        add(f"kiosk screen {side}{j + 1}", {"type": "wall", "width": r4(bay - 2 * kR * 0.8), "height": 1.6, "thickness": 0.3, "glass": False,
                                            "courses": crown(1.6, 0.3),
                                            "at": [[r4(xK + cx + ux * u + nx * 0.15), r4(yK), r4(zK + cz + uz * u + nz * 0.15), r4(yaw)]]})

nH, zN = 3.6, sz1 - sT - sD + 2.2
add("naos", {"type": "enclosure", "plan": {"rect": [2.2, 3.0]}, "thickness": 0.35, "height": nH, "glass": False, "interior": True,
             "faces": {"0": [door(1.0, 2.3)], "1": [], "2": [], "3": []}, "courses": {"list": crown(nH, 0.45)},
             "at": [[0, r4(B + naosFloor), r4(zN), 0]],
             "_about": "the shrine of the goddess's image: one block of stone hollowed, its door at the front, its own torus and gorge"})
add("naos roof", {"type": "box", "width": 2.2, "length": 3.0, "height": 0.3, "at": [[0, r4(B + naosFloor + nH), r4(zN), 0]]})

walls = ["pronaos", "temple", "screen", "west stair room", "west store partition", "east store partition", "west store wall", "east store wall", "sanctuary"] + [f"{h['name']} back wall" for h in halls]
doc = {"name": "Temple of Hathor, Dendera",
       "_about": "THE TEMPLE OF HATHOR AT DENDERA (Ptolemaic, 54 BC - AD 20) at its real size, 42 x 81 m, set out by the Egyptian temple's rules: one axis from the open pronaos to the free-standing sanctuary, the floors rising and the roofs falling at every door; battered walls crowned by torus and gorge; hypostyles whose architraves run over the files of columns, the middle aisle wider; the pronaos's Hathor columns joined by screen walls, the inner hall's campaniform, its store rooms either side (tools/archgen/dendera.py).",
       "params": {"detail": 4}, "parts": parts, "build": build}
open(os.path.join(ROOT, "assets/architecture/dendera.json"), "w").write(json.dumps(doc, indent=1) + "\n")
fin = {"name": "Temple of Hathor, Dendera", "building": "architecture/dendera",
       "_about": "Dendera: Nubian sandstone throughout; the walls carved with columns of hieroglyphs in sunk relief inside and out, the columns' shafts painted with them; the mouldings plain ashlar; the naos dark inside.",
       "stone": {"color": "#c9b283", "accent": "#b09a6d", "pat": "ashlar"},
       "rules": [{"parts": "naos", "side": "in", "color": "#2e2a22", "accent": "#2e2a22"},
                 {"parts": "kind:moulding", "pattern": "stone/ashlar", "palette": "sandstone"},
                 {"parts": ["pronaos columns shafts", "appearance columns shafts"], "pattern": "hieroglyphs/painted columns", "palette": "sandstone"},
                 {"surface": "floor", "pattern": "floors/flagstones", "palette": "sandstone"},
                 {"parts": walls, "surface": "wall", "pattern": "hieroglyphs/sunk relief", "palette": "sandstone"},
                 {"pattern": "stone/ashlar fine", "palette": "sandstone"}]}
open(os.path.join(ROOT, "assets/finishes/dendera.json"), "w").write(json.dumps(fin, indent=1) + "\n")
print("dendera:", len(parts), "parts")
