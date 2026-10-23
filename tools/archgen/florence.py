# SANTA MARIA DEL FIORE: what the definition lacked -- the roofs the game used to draw as prisms of its own, the
# drum's round windows, the tribune morte, the lantern's roof, ball and radiating buttresses, the campanile's
# cornice. Updates florence.json in place (safe to run again: every part it adds it replaces).
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, "assets/architecture/florence.json")
d = json.load(open(p))
P, parts, build = d["params"], d["parts"], d["build"]
def add(name, part, after=None):
    parts[name] = part
    if name not in build:
        build.insert(build.index(after) + 1 if after else len(build), name)
P.update({"roofZ0": "zc + naveL / 2 + pierT", "roofZ1": "octZ + octR * 0.92388", "roofL": "roofZ0 - roofZ1",
          "aisleRoofIn": "naveW / 2 + pierT + 0.35", "aisleRoofOut": "bodyW / 2 + 0.3",
          "_roofZ0": "the nave's roof runs from the facade to the crossing's own wall"})
# the drum's EIGHT OCULI: round windows are openings with a foot as well as a head
parts["drum"]["opening"] = {"width": 5.8, "sill": 7.4, "springing": 7.4, "head": {"profile": "semicircular"}, "foot": {"profile": "semicircular"}}
parts["drum"]["_about"] = "the drum, an eight-sided ring with a great round window -- an oculus -- in every face"
# ROOFS
add("nave roof", {"type": "roof", "form": "gable", "width": "naveW + 2 * pierT + 0.6", "length": "roofL", "pitch": 23.2,
                  "at": [[0, "naveTop", "(roofZ0 + roofZ1) / 2", 0]],
                  "_about": "the nave's roof, facade to crossing; its west gable closes the nave over the rose"}, after="aisle vault")
add("aisle roofs", {"type": "roof", "form": "shed", "width": "aisleRoofOut - aisleRoofIn", "length": "roofL", "pitch": 5.5,
                    "at": [["0 - (aisleRoofIn + aisleRoofOut) / 2", "aisleTop - 0.4", "(roofZ0 + roofZ1) / 2", 0],
                           ["(aisleRoofIn + aisleRoofOut) / 2", "aisleTop - 0.4", "(roofZ0 + roofZ1) / 2", 3.14159265]],
                    "_about": "a lean-to over each aisle, rising to just under the clerestory's sills"}, after="nave roof")
tp = parts["tribune"]["place"]
add("tribune roofs", {"type": "dome", "sweep": 0.5, "sides": 20, "radius": "tribR + tribT + 0.4", "thickness": 0,
                      "head": {"profile": "trigonal", "rise": 8.5},
                      "at": [[a[0], "tribH + 1.6", a[2], f"({a[3]}) + 3.14159265"] for a in tp],
                      "_about": "a half cone over each tribune: a dome skin of sweep 0.5, its open side against the octagon"}, after="tribune roof")
# the TRIBUNE MORTE: four exedrae against the octagon's diagonal faces, at the foot of the drum
fd = "(octR + octT) * 0.92388"
morte = []
for k in (1, 3, 5, 7):
    th = k * math.pi / 4
    morte.append([f"{fd} * {math.sin(th):.6f}", "tribH + 1.6", f"octZ + {fd} * {math.cos(th):.6f}", round(th + math.pi, 6)])
add("tribune morte", {"type": "component", "use": "components/iwan", "params": {"w": 9.0, "s": 7.0, "spread": 0, "t": 0.8},
                      "at": morte, "_about": "Brunelleschi's four 'dead tribunes': exedrae against the octagon's diagonal faces, a half ring under a half dome -- the `iwan` component with a round hood"}, after="drum")
# the LANTERN stands ON THE DOME, where the dome has narrowed to its oculus (a height worked out by hand held only at
# one detail: a finer meridian crosses the oculus a little higher); its conical roof, the ball, and eight buttresses leaning in to it off the dome's top ring
parts["lantern"].update({"atop": "dome", "atopR": "lanternR", "y": 0})
P.pop("lanternTop", None)
add("lantern roof", {"type": "dome", "sides": 8, "radius": "lanternR + 1.6", "thickness": 0, "head": {"profile": "trigonal", "rise": 4.5},
                     "atop": "lantern", "at": [[0, 0, "octZ", 0]]}, after="lantern")
add("lantern ball", {"type": "dome", "sides": 12, "radius": 0.36, "thickness": 0, "head": {"profile": "onion", "bulge": 3.0, "neck": 0.4},
                     "atop": "lantern roof", "at": [[0, -0.05, "octZ", 0]], "_about": "the gilt ball on the lantern's cone (an onion of a very narrow foot)"}, after="lantern roof")
fly = []
for k in range(8):
    a = (k + 0.5) * math.pi / 4                       # between the lantern's windows: on its corners
    fly.append([f"(lanternR + 4.2) * {math.sin(a):.6f}", 0, f"octZ + (lanternR + 4.2) * {math.cos(a):.6f}", round(a + math.pi / 2, 6)])
add("lantern buttresses", {"type": "flyer", "span": 3.2, "low": -0.1, "high": 9.5,
                           "top0": 2.1, "top1": 13.0, "width": 0.9, "at": fly, "atop": "dome", "atopR": "lanternR + 4.2",
                           "_about": "the lantern's eight buttresses, each a strut on a rampant arch leaning in to one of its corners: its foot on the dome where it stands (`atopR`), its head 2.5m higher up the lantern, which stands on the oculus"}, after="lantern ball")
add("campanile cornice", {"type": "box", "width": "campW + 1.4", "length": "campW + 1.4", "height": 0.9, "at": [["campX", "campH", "campZ", 0]],
                          "_about": "the cornice and terrace the campanile ends in"}, after="campanile")
# THE TRIBUNES STAND ON THE OCTAGON'S FACES: their centre `tribD` out from the crossing's, so each one's
# diameter lies in the face it opens off (it used to stand 1.85m short, and the sky showed between). A tribune is
# wider than the face, so beside each end, between it and the octagon's diagonal face, a SPANDREL fills the
# wedge up to the terrace -- one prism on a plan worked out from the two rings.
P["tribD"] = "(octR + octT) * 0.92388"
P["_tribD"] = "a tribune's centre, out from the crossing's: on the octagon's outer face (the game reads it too)"
seats = [[0, 0, "octZ - tribD", 0], ["tribD", 0, "octZ", "0 - quarter"], ["0 - tribD", 0, "octZ", "quarter"]]
parts["tribune"]["place"] = seats
parts["tribune roof"]["place"] = seats
parts["tribune roofs"]["at"] = [[a[0], "tribH + 1.6", a[2], f"({a[3]}) + 3.14159265"] for a in seats]
half = "(octR + octT) * 0.38268"                      # half an octagon face
for sx, nm in ((1, "right"), (-1, "left")):
    add(f"tribune spandrels {nm}", {"flatRoof": True, "type": "prism", "height": "tribH + 1.6",
        "plan": {"points": [[f"{sx} * {half}", 0], [f"{sx} * (tribR + tribT)", 0], [f"{sx} * (tribR + tribT)", f"tribR + tribT - {half}"]]},
        "place": seats,
        "_about": "the wedge between a tribune's end and the octagon's diagonal face, filled to the terrace"}, after="tribune roof")
# ---- THE CLIMBS, rebuilt: continuous stairs that stand on something and arrive somewhere (they were rings of
# separate short flights placed round a circle, and hung in the air with gaps between them)
for k in ["campanile stair", "gallery stair", "drum stair", "cupola stair"]:
    parts.pop(k, None)
    if k in build: build.remove(k)
# THE CAMPANILE: four flights to a storey round the well, on corner landings, twenty in all, the first up the east
# wall so the door (in the south wall) stays clear; the last arrives on the terrace at the top, which is cut away
# only over that corner. (The walls stand half a thickness in from campW: the inside is campW - 3 campT square.)
P["campIn"] = "campW - 3 * campT"; P["campStairW"] = 1.2
P["_campIn"] = "the campanile's inside, between the inner faces of its walls"
add("campanile stair", {"type": "staircase", "rise": "campStorey / 84", "run": "(campIn - 2 * campStairW) / 21", "soffit": 0.3,
                        "flight": 21, "width": "campStairW", "landing": {"depth": "campStairW", "width": "campStairW"},
                        "times": 20, "from": "right", "at": "campStairW / 2",
                        "place": [["campX + campIn / 2 - campStairW / 2", 0, "campZ - campIn / 2 + campStairW", -1.5707963]],
                        "_about": "four flights a storey round the well on corner landings, five storeys, 420 steps to the terrace"}, after="campanile")
parts.pop("campanile cornice", None)
if "campanile cornice" in build: build.remove("campanile cornice")
parts.pop("campanile terrace corner", None)
if "campanile terrace corner" in build: build.remove("campanile terrace corner")
add("campanile terrace", {"type": "box", "width": "campIn", "length": "campIn - campStairW", "height": 0.3,
                          "at": [["campX", "campH - 0.3", "campZ + campStairW / 2", 0]],
                          "_about": "the terrace on top: all of the inside but the band along the south wall the last flight climbs in (its landing, in the corner, is the terrace there)"}, after="campanile stair")
add("campanile cornice", {"type": "enclosure", "plan": {"rect": ["campW + 1.4", "campW + 1.4"]}, "thickness": 2.6, "height": 0.9, "openings": [],
                          "at": [["campX", "campH", "campZ", 0]], "_about": "the cornice and parapet round the terrace"}, after="campanile terrace")
# THE DOME IN TWO SHELLS, as Brunelleschi built it: an outer one carrying the ribs and an inner one struck over the
# drum's own radius, a gap of 1.8m between them where the stair climbs
P["outerT"] = 0.9; P["shellGap"] = 2.2
parts["dome"]["thickness"] = "outerT"
parts["dome"]["_about"] = "the OUTER shell, carrying the ribs and the tiles"
add("inner dome", {"type": "dome", "sides": 8, "radius": "octR + octT - outerT - shellGap", "thickness": "octT - outerT - shellGap", "oculus": "lanternR",
                   "head": {"profile": "pointed", "spread": "domeSpread"}, "at": [[0, "drumTop", "octZ", 0]],
                   "_about": "the INNER shell: its soffit is the drum's inner face carried up; the stair climbs on its back"}, after="dome")
# THE PIER STAIR: one of the four solid piers of the octagon (bay 1) is hollow -- two skins, walls closing its ends --
# with a door from the crossing, and a spiral inside it climbs through the octagon and the drum to 2.2m under the
# dome's springing, where a floor in the shaft leads along it to a short flight up into the gap between the shells
parts["octagon pier"]["at"] = [3, 5, 7]
a = math.pi / 4
skin = lambda h, y, r0, r1, **kw: {"type": "ring", "count": 8, "rOuter": r1, "rInner": r0, "height": h, "y": y, "at": [1], "place": [[0, 0, "octZ", 0]], **kw}
# the skins are FLAT walls on the octagon's faces (a ring bay with a door in it is a polyline on the circle, and bulged
# into the void): the inner one at the face of the crossing with the door in it, the outer one at the outside face
dIn, dOut = "octR * 0.92388", "(octR + octT) * 0.92388"
def face_wall(name, d, h, y, inward, openings, after):
    yaw = a + math.pi if inward else a
    add(name, {"type": "wall", "width": f"2 * {d} * 0.41421", "height": h, "thickness": 0.5, "openings": openings,
               "at": [[f"{d} * {math.sin(a):.6f}", y, f"octZ + {d} * {math.cos(a):.6f}", round(yaw, 6)]]}, after=after)
face_wall("pier shaft inner", dIn, "crossH", 0, True, [{"at": "octR * 0.92388 * 0.41421", "width": 1.1, "sill": 0, "springing": 2.3, "head": {"profile": "semicircular"}}], "octagon pier")
face_wall("pier shaft outer", dOut, "crossH", 0, False, [], "pier shaft inner")
face_wall("drum shaft inner", dIn, "drumH", "crossH", True, [], "drum")
face_wall("drum shaft outer", dOut, "drumH", "crossH", False, [], "drum shaft inner")
parts["drum"]["skip"] = [1]
ends = []
for e in (-1, 1):
    ang = a + e * math.pi / 8
    ends.append([f"(octR + octT / 2) * {math.sin(ang):.6f}", 0, f"octZ + (octR + octT / 2) * {math.cos(ang):.6f}", round(ang, 6)])   # (on the corners' radial lines)
add("shaft ends", {"type": "box", "width": 0.5, "length": "octT - 0.5", "height": "drumTop", "at": ends,
                   "_about": "the walls closing the hollow pier at its two ends, up through the drum"}, after="drum shaft outer")
# (an octagon's walls are FLAT: positions here are distances from the centre to a face, not radii to a corner --
#  the hollow pier's void lies between its skins' faces, (octR + .5) and (octR + octT - .5) times cos 22.5)
rc = "(octR + octT / 2) * 0.92388"
C = lambda t, r=rc: [f"({r}) * {math.sin(a):.6f} + ({t}) * {math.cos(a):.6f}", f"octZ + ({r}) * {math.cos(a):.6f} - ({t}) * {math.sin(a):.6f}"]
cx, cz = C(0)
add("pier stair", {"type": "spiral-stair", "radius": 1.35, "newel": 0.2, "turn": 24, "top": "drumTop - 2.2", "rise": 0.19, "soffit": 0.2,
                   "at": [[cx, 0, cz, round(a + math.pi, 6)]],
                   "_about": "the spiral inside the hollow pier, from the crossing's floor to the shaft's upper floor"}, after="shaft ends")
for side, nm in ((1, "east"), (-1, "west")):
    bx, bz = C(f"{side} * 5.75")
    add(f"shaft floor {nm}", {"type": "box", "width": 8.2, "length": "octT - 1.0", "height": 0.3, "at": [[bx, "drumTop - 2.5", bz, round(a, 6)]],
                              "_about": "the floor at the top of the shaft, beside the spiral"}, after="pier stair")
fx, fz = C(2.3, "((octR + octT - outerT) + (octR + octT - outerT - shellGap)) / 2 * 0.92388 + 0.5")
add("shell flight", {"type": "flight", "width": 0.9, "run": 0.28, "rise": 0.18, "base": "drumTop - 2.2", "top": "drumTop", "landing": 0.8,
                     "at": [[fx, 0, fz, round(a, 6)]],
                     "_about": "up from the shaft's floor into the gap between the two shells"}, after="shaft floor west")
end_ang = a + (2.3 + 12 * 0.28 + 0.5) / 25.0
add("dome stair", {"type": "spiral-stair", "follow": {"head": {"profile": "pointed", "spread": "domeSpread"}, "radius": "octR + octT", "inset": "outerT + 0.35", "insetTop": "outerT + 1.9", "width": 0.9, "sides": 8},
                   "top": "domeRise * 0.8", "run": 0.3, "rise": 0.19, "soffit": 0.2, "at": [[0, "drumTop", "octZ", round(end_ang, 6)]],
                   "_about": "between the shells, on the inner one's back: its outer edge follows the outer shell's inner face a handspan off, so it draws in as the dome does"},
    after="shell flight")
# the platform it stands on (the game draws its own pavement and asks for the church without it: `base: false`)
d["base"] = {"height": 0.6, "steps": 3, "stepOut": 0.6, "margin": 4}
# ---- THE PAVEMENT, THE MARBLE BANDS, THE CONGREGATION (2026-10-02: were architecture.js florenceCathedral's own parts).
# The pavement: marble over the body (inside the walls only: laid to the body's full width it showed as a chequered apron
# round the church's foot), the crossing's octagon, the three tribunes and the tower's floor -- walked. The bands: Florence
# is white Carrara banded with green Prato and red Maremma, courses of thin slabs standing just off its face -- on the
# flanks, the facade, the tower, round the octagon and drum, and on the tribunes (the half of each that stands clear of
# the crossing: the tribune ring's own bays). The congregation: pews down the nave, facing the crossing (a zone).
FLOOR = 0.3
add("pavement", {"type": "box", "width": "bodyW - 2 * aisleT - 0.2", "length": "naveL + 2 * pierT - 0.4", "height": FLOOR, "at": [[0, 0, "zc", 0]], "walked": True})
add("pavement crossing", {"type": "column", "radius": "octR - 0.2", "height": FLOOR, "sides": 8, "at": [[0, 0, "octZ", 0]], "walked": True})
add("pavement tribunes", {"type": "column", "radius": "tribR - 0.2", "height": FLOOR, "sides": 10, "at": [[a[0], 0, a[2], 0] for a in parts["tribune"]["place"]], "walked": True})
add("pavement tower", {"type": "box", "width": "campW - 2 * campT - 0.1", "length": "campW - 2 * campT - 0.1", "height": FLOOR, "at": [["campX", 0, "campZ", 0]], "walked": True})
def bandbox(name, rows, w, l, x, z):   # rows: (y centre, height); boxes w across x, l along z
    for i, (y, h) in enumerate(rows):
        add(f"{name} {i + 1}", {"type": "box", "width": w, "length": l, "height": h, "at": [[x, f"({y}) - {h / 2}", z, 0]] if not isinstance(x, list) else [[xx, f"({y}) - {h / 2}", z, 0] for xx in x]})
G, R = "green band", "red band"
bandbox(G + " flank", [("winSill - 1.2", 0.5), ("aisleTop + 0.6", 0.55)], "aisleT + 0.12", "roofL", ["bodyW / 2 + 0.06", "0 - bodyW / 2 - 0.06"], "(roofZ0 + roofZ1) / 2")
bandbox(R + " flank", [("winSill - 0.5", 0.22)], "aisleT + 0.12", "roofL", ["bodyW / 2 + 0.06", "0 - bodyW / 2 - 0.06"], "(roofZ0 + roofZ1) / 2")
bandbox(G + " facade", [("winSill - 1.2", 0.5), ("aisleTop + 1.4", 0.5)], "bodyW + 0.12", "pierT + 0.12", 0, "zc + naveL / 2 + pierT")
bandbox(G + " front", [("roseY - 0.8", 0.5)], "frontC + 0.12", "pierT + 0.12", 0, "zc + naveL / 2 + pierT")
bandbox(R + " facade", [("winSill - 0.5", 0.22)], "bodyW + 0.12", "pierT + 0.12", 0, "zc + naveL / 2 + pierT")
bandbox(R + " front", [("roseY + roseW + 2.4", 0.45)], "frontC + 0.12", "pierT + 0.12", 0, "zc + naveL / 2 + pierT")
for k in range(1, 5):   # the campanile's courses, one to a storey, green and red in turn
    add(f"{G if k % 2 else R} tower {k}", {"type": "box", "width": "campW + 0.12", "length": "campW + 0.12", "height": 0.45, "at": [["campX", f"{k} * campStorey - 0.525", "campZ", 0]]})
for i, (y, h, c) in enumerate([("crossH * 0.55", 0.7, G), ("crossH - 1.6", 0.45, R), ("crossH + 1.0", 0.6, G), ("drumTop - 1.4", 0.7, R)]):
    add(f"{c} octagon {i + 1}", {"type": "ring", "count": 24, "rOuter": "octR + octT + 0.14", "rInner": "octR + octT + 0.06", "height": h, "y": f"({y}) - {h / 2}", "solid": True, "place": [[0, 0, "octZ", 0]]})
for i, (y, h, c) in enumerate([("tribH * 0.5", 0.55, G), ("tribH - 1.2", 0.4, R)]):
    add(f"{c} tribunes {i + 1}", {"type": "ring", "count": 10, "rOuter": "tribR + tribT + 0.14", "rInner": "tribR + tribT + 0.06", "height": h, "y": f"({y}) - {h / 2}", "solid": True,
                                   "skip": parts["tribune"]["skip"], "place": parts["tribune"]["place"]})
add("seating", {"type": "zone", "zone": "seating", "w": "naveW - 2.8", "d": 27, "h": "arcadeH", "at": [[0, FLOOR, "zc + naveL / 2 - 6 - 13.5", 1.5707963]],
                "_about": "the congregation: pews down the nave on a middle aisle, facing the crossing (-z) -- clear of the arcade's piers, which stand 0.6 m into the nave"})
open(p, "w").write(json.dumps(d, indent=2) + "\n")
