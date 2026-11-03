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
    if after and name in build: build.remove(name)     # (`after` places it again: built once what it stands on is)
    if name not in build:
        build.insert(build.index(after) + 1 if after else len(build), name)
# A WALL STANDS ON ITS LINE, ITS THICKNESS BEHIND IT: so the lines the arcades and the flanks are set on are their
# OUTER faces -- the arcade's at the nave's half width and a pier's thickness, the flank's at the body's half width. (Set
# on the piers' and the aisle walls' centre lines, both stood half a thickness in: the arcade ran 1.5m into the nave
# vault and left a slot open from the floor to the roof between it and the aisle vaults; the flanks stood 90cm inside
# the facade's ends.)
P.update({"halfB": "naveW / 2 + pierT", "halfA": "naveW / 2 + pierT + aisleW + aisleT"})
P.update({"roofZ0": "zc + naveL / 2 + pierT", "roofZ1": "octZ + octR * 0.92388", "roofL": "roofZ0 - roofZ1",
          "aisleRoofIn": "naveW / 2 + pierT", "aisleRoofOut": "bodyW / 2 - 0.05",
          "_roofZ0": "the nave's roof runs from the facade to the crossing's own wall"})
# the drum's EIGHT OCULI: round windows are openings with a foot as well as a head
parts["drum"]["opening"] = {"width": 5.8, "sill": 7.4, "springing": 7.4, "head": {"profile": "semicircular"}, "foot": {"profile": "semicircular"}}
parts["drum"]["_about"] = "the drum, an eight-sided ring with a great round window -- an oculus -- in every face"
# THE OCTAGON IS AN OCTAGON: its walls, its piers, the drum, the tribunes and the cornices on them are POLYGONAL rings
# (flat faces between corners at their radii -- the dome's own octagon, whose webs spring from them), not cylinders
# cut into eight arcs, which bulged past the flat face walls and the dome's corners
for k in ["octagon", "drum", "octagon pier", "tribune", "tribune roof"]:
    parts[k]["polygon"] = True
# THE CLERESTORY RISES TO THE ROOF: the wall does not stop where the vault springs -- its cells' lunettes meet it along
# their wall ribs, and it carries on up to the wall plate the roof sits on (stopped at the springing, the lunettes stood
# open to the sky the whole length of the nave)
parts["clerestory"]["height"] = "naveTop - arcadeH"
# THE TRIBUNES ARE CHAPELS: closed walls round the altars, lit by a tall lancet high in each face -- between the
# marble courses at half height and under the cornice -- glazed (with a sill well over the floor, by default). (They had
# been rings of six-metre arches standing open from the pavement, a portico round each apse, the green course running
# across every one of them in mid air.)
parts["tribune"]["opening"] = {"width": 2.4, "sill": "tribH * 0.5 + 1.0", "springing": "tribH * 0.77", "head": {"profile": "pointed", "spread": 1.0}, "tracery": True}
parts["tribune"]["_about"] = "the three tribunes round the octagon, chapels lit by a tall traceried lancet in each outer face"
parts["tribune roof"]["rInner"] = "tribR"     # (the cornice ring on the wall's head: the half dome springs inside it)
# ROOFS
add("nave roof", {"type": "roof", "form": "gable", "width": "naveW + 2 * pierT + 0.6", "length": "roofL", "pitch": 23.2,
                  "at": [[0, "naveTop", "(roofZ0 + roofZ1) / 2", 0]],
                  "_about": "the nave's roof, facade to crossing; its west gable closes the nave over the rose"}, after="aisle vault")
add("aisle roofs", {"type": "roof", "form": "shed", "width": "aisleRoofOut - aisleRoofIn", "length": "roofL", "pitch": 5.5,
                    "at": [["0 - (aisleRoofIn + aisleRoofOut) / 2", "aisleTop - 0.4", "(roofZ0 + roofZ1) / 2", 0],
                           ["(aisleRoofIn + aisleRoofOut) / 2", "aisleTop - 0.4", "(roofZ0 + roofZ1) / 2", 3.14159265]],
                    "_about": "a lean-to over each aisle, rising to just under the clerestory's sills"}, after="nave roof")
tp = parts["tribune"]["place"]
add("tribune roofs", {"type": "dome", "sweep": 0.5, "sides": 10, "radius": "tribR + tribT + 0.4", "thickness": 0, "cap": False,
                      "head": {"profile": "trigonal", "rise": 8.5},
                      "at": [[a[0], "tribH + 1.6", a[2], f"({a[3]}) + 3.14159265"] for a in tp],
                      "_about": "a half pyramid over each tribune, on its five faces: a dome skin of sweep 0.5, its cut against the octagon"}, after="tribune roof")
# THE TRIBUNES ARE VAULTED: a half dome over each, inside its roof -- springing from the wall's head under the cornice
# ring, its outer face struck under the roof's cone everywhere (a segmental dome of 6.5m rise: a deeper one came
# through the roof near its foot), its inner edge on the wall's inner face, the soffit plastered and frescoed as the
# inner dome is. The octagon's great arches into them spring at 16m, not 18: their crowns (28.5m) under the half dome's
# soffit where it meets the octagon's face (29.3m) -- higher, the roof's tiles showed between the two
parts["octagon"]["opening"]["springing"] = "crossH * 0.4"
add("tribune vaults", {"type": "dome", "sweep": 0.5, "sides": 10, "radius": "tribR + 1.2", "thickness": 1.2,
                       "head": {"profile": "segmental", "rise": 6.5},
                       "at": [[a[0], "tribH", a[2], f"({a[3]}) + 3.14159265"] for a in tp],
                       "_about": "the half dome over each tribune, under its roof"}, after="tribune roof")
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
parts["tribune vaults"]["at"] = [[a[0], "tribH", a[2], f"({a[3]}) + 3.14159265"] for a in seats]
half = "(octR + octT) * 0.38268"                      # half an octagon face
for sx, nm in ((1, "right"), (-1, "left")):
    # (its top falls as the tribune's roof does along the cut -- 8.5 m over the roof's radius from the apex over the
    #  tribune's centre -- so the roof's cut is closed by masonry where it runs past the octagon's face)
    add(f"tribune spandrels {nm}", {"type": "prism", "height": "tribH + 1.6 + 8.5", "slope": [f"{-sx} * 8.5 / (tribR + tribT + 0.4)", 0],
        "plan": {"points": [[f"{sx} * {half}", 0], [f"{sx} * (tribR + tribT)", 0], [f"{sx} * (tribR + tribT)", f"tribR + tribT - {half}"]]},
        "place": seats,
        "_about": "the wedge between a tribune's end and the octagon's diagonal face, built up to the tribune roof's line: the roof's cut, past the octagon's face, rests against it"}, after="tribune roof")
# ---- THE CLIMBS, rebuilt: continuous stairs that stand on something and arrive somewhere (they were rings of
# separate short flights placed round a circle, and hung in the air with gaps between them)
for k in ["campanile stair", "gallery stair", "drum stair", "cupola stair"]:
    parts.pop(k, None)
    if k in build: build.remove(k)
# THE CAMPANILE: four flights to a storey round the well, on corner landings, twenty in all, the first up the east
# wall so the door (in the south wall) stays clear; the last arrives on the terrace at the top, which is cut away
# only over that corner.
P["campIn"] = "campW - 2 * campT"; P["campStairW"] = 1.2
P["_campIn"] = "the campanile's inside, between the inner faces of its walls"
FLOOR = 0.3   # the pavements' height over the ground
# (it starts on the tower's pavement, FLOOR up, and climbs the rest: 420 risers from there to the terrace)
add("campanile stair", {"type": "staircase", "rise": f"(campH - {FLOOR}) / 420", "run": "(campIn - 2 * campStairW) / 21", "soffit": 0.3,
                        "flight": 21, "width": "campStairW", "landing": {"depth": "campStairW", "width": "campStairW"},
                        "times": 20, "from": "right", "at": "campStairW / 2",
                        "place": [["campX + campIn / 2 - campStairW / 2", FLOOR, "campZ - campIn / 2 + campStairW", -1.5707963]],
                        "_about": "four flights a storey round the well on corner landings, five storeys, 420 steps to the terrace"}, after="campanile")
parts.pop("campanile cornice", None)
if "campanile cornice" in build: build.remove("campanile cornice")
parts.pop("campanile terrace corner", None)
if "campanile terrace corner" in build: build.remove("campanile terrace corner")
add("campanile terrace", {"walked": True, "type": "box", "width": "campIn", "length": "campIn - campStairW", "height": 0.3,
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
add("inner dome back", {"type": "dome", "sides": 8, "radius": "octR + octT - outerT - shellGap + 0.02", "thickness": 0.02, "oculus": "lanternR",
                        "head": {"profile": "pointed", "spread": "domeSpread"}, "at": [[0, "drumTop", "octZ", 0]],
                        "_about": "the inner shell's BACK, a skin over it: bare brick and plaster where the stair climbs, not the fresco of its soffit"}, after="inner dome")
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
for nm in ("shaft floor east", "shaft floor west"):
    parts.pop(nm, None)
    if nm in build: build.remove(nm)
add("shaft floor", {"walked": True, "type": "prism", "plan": {"rect": [19.7, "octT - 1.0"], "well": {"radius": 1.4}}, "height": 0.3, "at": [[cx, "drumTop - 2.5", cz, round(a, 6)]],
                    "_about": "the floor at the top of the shaft, the spiral coming up through its well"}, after="pier stair")
# (its foot 2.45m along from the shaft's middle: its 0.9m approach clear of the railing round the pier stair's well)
SHELL_OFF = 2.75
fx, fz = C(SHELL_OFF, "((octR + octT - outerT) + (octR + octT - outerT - shellGap)) / 2 * 0.92388 + 0.5")
add("shell flight", {"type": "flight", "width": 1.2, "run": 0.28, "rise": 0.18, "base": "drumTop - 2.2", "top": "drumTop", "landing": 0.8,
                     "at": [[fx, 0, fz, round(a, 6)]],
                     "_about": "up from the shaft's floor into the gap between the two shells"}, after="shaft floor")
end_ang = a + (SHELL_OFF + 12 * 0.28 + 0.5) / 25.0
add("dome stair", {"type": "spiral-stair", "follow": {"head": {"profile": "pointed", "spread": "domeSpread"}, "radius": "octR + octT", "inset": "outerT + 0.35", "insetTop": "outerT + 1.85", "width": 1.15, "sides": 8},
                   "top": "domeRise * 0.8", "run": 0.3, "rise": 0.19, "soffit": 0.2, "landing": 8.0, "at": [[0, "drumTop", "octZ", round(end_ang, 6)]],
                   "_about": "between the shells, on the inner one's back: its outer edge follows the outer shell's inner face a handspan off, so it draws in as the dome does; it arrives on a landing that runs on to the octagon's corner, where the gallery begins"},
    after="shell flight")
# THE GALLERY between the shells where the stair arrives: a slab across the whole gap -- from the inner shell's back to
# the outer one's inner face, both struck from the pointed head's centres (a shell's inner face is its curve less its
# thickness) -- on the four sides the stair does not climb under (it rises from the 60th degree to the 177th; its landing
# runs on to the corner at the 202nd, where these sides begin)
yG = "domeRise * 0.8"
sq = lambda e: f"({e}) * ({e})"
add("dome gallery", {"walked": True, "type": "ring", "count": 8, "solid": True, "height": 0.3, "y": f"{yG} - 0.3",
                     "rOuter": f"sqrt({sq('(octR + octT) * (1 + domeSpread) - outerT')} - {sq(yG)}) - (octR + octT) * domeSpread",
                     "rInner": f"sqrt({sq('(octR + octT - outerT - shellGap) * (1 + domeSpread)')} - {sq(yG)}) - (octR + octT - outerT - shellGap) * domeSpread",
                     "at": [5, 6, 7, 0], "place": [[0, "drumTop", "octZ", 0]],
                     "_about": "the walk between the shells the dome stair arrives on"}, after="inner dome")
# the platform it stands on (the game draws its own pavement and asks for the church without it: `base: false`)
d["base"] = {"height": 0.6, "steps": 3, "stepOut": 0.6, "margin": 4}
# ---- THE PAVEMENT, THE MARBLE BANDS, THE CONGREGATION (2026-10-02: were architecture.js florenceCathedral's own parts).
# The pavement: marble over the body (inside the walls only: laid to the body's full width it showed as a chequered apron
# round the church's foot), the crossing's octagon, the three tribunes and the tower's floor -- walked. The bands: Florence
# is white Carrara banded with green Prato and red Maremma, courses of thin slabs standing just off its face -- on the
# flanks, the facade, the tower, round the octagon and drum, and on the tribunes (the half of each that stands clear of
# the crossing: the tribune ring's own bays). The congregation: pews down the nave, facing the crossing (a zone).
add("pavement", {"type": "box", "width": "bodyW - 2 * aisleT - 0.2", "length": "naveL + 2 * pierT - 0.4", "height": FLOOR, "at": [[0, 0, "zc", 0]], "walked": True})
# (a column's corners are at its yaw and every eighth turn on: turned an eighth of a half so its faces lie on the
#  octagon's -- corners on the faces' middles poked 1.5m into the hollow pier, over the stair's first treads)
add("pavement crossing", {"type": "column", "radius": "octR - 0.2", "height": FLOOR, "sides": 8, "at": [[0, 0, "octZ", round(math.pi / 8, 6)]], "walked": True})
add("pavement tribunes", {"type": "column", "radius": "tribR - 0.2", "height": FLOOR, "sides": 10, "at": [[a[0], 0, a[2], 0] for a in parts["tribune"]["place"]], "walked": True})
add("pavement tower", {"type": "box", "width": "campW - 2 * campT - 0.1", "length": "campW - 2 * campT - 0.1", "height": FLOOR, "at": [["campX", 0, "campZ", 0]], "walked": True})
def bandbox(name, rows, w, l, x, z):   # rows: (y centre, height); boxes w across x, l along z
    for i, (y, h) in enumerate(rows):
        add(f"{name} {i + 1}", {"type": "box", "width": w, "length": l, "height": h, "at": [[x, f"({y}) - {h / 2}", z, 0]] if not isinstance(x, list) else [[xx, f"({y}) - {h / 2}", z, 0] for xx in x]})
G, R = "green band", "red band"
# THE MARBLE COURSES are a veneer on the walls' OUTER faces, 10cm deep -- 4cm into the wall, 6cm proud. (A wall's
# front face stands on its placement line, its thickness behind: the flanks' outer faces are at +-halfA, the front's on
# its line, the campanile's half a thickness in from campW.) They had been boxes the wall's thickness wide set on
# bodyW / 2, a ledge nearly two metres deep along the flanks; and the campanile's were solid blocks the tower's size, a
# slab through its inside at every storey that the stair ran into.
FRONT = "zc + naveL / 2 + pierT + 0.01"
bandbox(G + " flank", [("winSill - 1.2", 0.5), ("aisleTop + 0.6", 0.55)], 0.1, "roofL", ["halfA + 0.01", "0 - halfA - 0.01"], "(roofZ0 + roofZ1) / 2")
bandbox(R + " flank", [("winSill - 0.5", 0.22)], 0.1, "roofL", ["halfA + 0.01", "0 - halfA - 0.01"], "(roofZ0 + roofZ1) / 2")
# (on the FACADE the courses stop either side of the portals and their gables -- run across them they cut the doorways
#  in two at a man's height; the upper green course runs along the aisles' fronts only, under the wings' windows, the
#  nave's front carrying the rose there)
for nm in [k for k in parts if k.startswith((G + " facade", R + " facade", G + " front", R + " front"))]:
    parts.pop(nm); build.remove(nm)
def facade_band(name, y, h, segs):
    """a course across the front in pieces: segs [(x0, x1)], one part per width (copies of it at each place)"""
    widths = {}
    for x0, x1 in segs:
        widths.setdefault(round(x1 - x0, 3), []).append(round((x0 + x1) / 2, 3))
    for k, (w, xs) in enumerate(sorted(widths.items())):
        add(f"{name} {k + 1}" if len(widths) > 1 else name, {"type": "box", "width": w, "length": 0.1, "height": h,
                                                            "at": [[x, f"({y}) - {h / 2}", FRONT, 0] for x in xs]})
# (the front's numbers: bodyW 48.1, the nave's front 25.5 wide, the wing doors at +-18.4 with gables 5.3 wide, the
#  portal's gable 10.4)
EDGE, PORT, WING, WHALF = 24.11, 5.4, 18.4, 2.8
low = [(-EDGE, -WING - WHALF), (-WING + WHALF, -PORT), (PORT, WING - WHALF), (WING + WHALF, EDGE)]
facade_band(G + " facade 1", "winSill - 1.2", 0.5, low)
facade_band(R + " facade 1", "winSill - 0.5", 0.22, low)
facade_band(G + " facade 2", "aisleTop + 1.4", 0.5, [(-EDGE, -12.75), (12.75, EDGE)])
facade_band(G + " front 1", "roseY - 0.8", 0.5, [(-12.81, 12.81)])
facade_band(R + " front 1", "naveTop - 1.2", 0.45, [(-12.81, 12.81)])
# the courses on the octagon and the tribunes: polygonal rings on their faces, set 4 cm into the wall and 8 cm proud
# (radii are corner radii: a face offset over cos(pi / n)); the octagon's lowest runs over the tribunes' roofs, not
# through the tribunes under them, and the two lowest not on the face toward the nave (bay 0): under the nave's roof
# there, they ran through its vault and its attic
band = lambda r, n, d: f"{r} + {d / math.cos(math.pi / n):.4f}"
for i, (y, h, c) in enumerate([("tribH + 11", 0.7, G), ("crossH - 1.6", 0.45, R), ("crossH + 1.0", 0.6, G), ("drumTop - 1.4", 0.7, R)]):
    add(f"{c} octagon {i + 1}", {"type": "ring", "count": 8, "polygon": True, "rOuter": band("octR + octT", 8, 0.08), "rInner": band("octR + octT", 8, -0.04),
                                 "height": h, "y": f"({y}) - {h / 2}", "solid": True, "place": [[0, 0, "octZ", 0]], **({"skip": [0]} if i < 2 else {})})
for i, (y, h, c) in enumerate([("tribH * 0.5", 0.55, G), ("tribH - 1.2", 0.4, R)]):
    add(f"{c} tribunes {i + 1}", {"type": "ring", "count": 10, "polygon": True, "rOuter": band("tribR + tribT", 10, 0.08), "rInner": band("tribR + tribT", 10, -0.04),
                                   "height": h, "y": f"({y}) - {h / 2}", "solid": True, "skip": parts["tribune"]["skip"], "place": parts["tribune"]["place"]})
# ---- THE FACADE (2026-10-27): the rose a full circle, high under the gable, with its tracery; a GABLE over the nave's
# front standing above the roof as a screen (the nave's roof stops behind it); a WIMPERG over each portal, as the
# Florentine portals carry -- the front had been a blank box with a round-headed window low in it
parts["west rose"]["openings"] = [{"at": "frontC / 2", "width": "roseW", "sill": 8.5, "springing": 8.5,
                                   "head": {"profile": "semicircular"}, "foot": {"profile": "semicircular"}, "tracery": True}]
P["roseW"] = 8.0
parts["west front"]["openings"][0]["wimperg"] = {"pitch": 55, "coping": 0.6, "depth": 0.45}
parts["west wing"]["openings"][0]["wimperg"] = {"pitch": 55, "coping": 0.45, "depth": 0.4}
# parts["nave roof"].update({"length": "roofL - pierT", "at": [[0, "naveTop", "(roofZ0 - pierT + roofZ1) / 2", 0]]})
add("west gable", {"type": "roof", "form": "gable", "width": "frontC + 1.0", "length": "pierT", "pitch": 32,
                   "at": [[0, "naveTop", "zc + naveL / 2 + pierT / 2", 0]],
                   "_about": "the nave front's gable, on the facade's own thickness: steeper and higher than the roof behind it, a screen"}, after="nave roof")
# ---- THE TRIBUNES' CHAPELS: five round each, between spur walls from the corners of its five outer faces (the
# chapels are in the tribune's own ring, as built), an altar on a step against each face under its lancet
spurs, altars, steps = [], [], []
fin = "tribR * 0.95106"                            # (a face's distance from the tribune's centre: corner radius x cos 18)
for sx, sz, syaw in [(0, "octZ - tribD", 0.0), ("tribD", "octZ", -math.pi / 2), ("0 - tribD", "octZ", math.pi / 2)]:
    def W(r, ang, sx=sx, sz=sz, syaw=syaw):        # (a point r out from the tribune's centre at `ang` in its own frame)
        c, s_ = math.cos(syaw), math.sin(syaw)
        lx, lz = f"({r}) * {math.sin(ang):.6f}", f"({r}) * {math.cos(ang):.6f}"
        return [f"{sx} + {lx} * {c:.6f} + {lz} * {s_:.6f}", f"{sz} - {lx} * {s_:.6f} + {lz} * {c:.6f}"]
    for k in (3.5, 4.5, 5.5, 6.5):                 # the corners between the five faces
        ang = k * 2 * math.pi / 10
        x, z = W("tribR - 1.9", ang); spurs.append([x, 0, z, round(ang + syaw, 6)])
    for k in (4, 5, 6, 7, 3):                      # the faces' middles
        ang = k * 2 * math.pi / 10
        x, z = W(f"{fin} - 0.6", ang); altars.append([x, 0.45, z, round(ang + syaw, 6)])
        x, z = W(f"{fin} - 1.15", ang); steps.append([x, FLOOR, z, round(ang + syaw, 6)])
add("tribune chapels", {"type": "box", "width": 0.9, "length": 4.0, "height": 11.5, "at": spurs,
                        "_about": "the spur walls between a tribune's five chapels, from its corners in"}, after="tribune")
add("chapel steps", {"type": "box", "width": 4.0, "length": 2.3, "height": 0.15, "at": steps, "walked": True}, after="tribune chapels")
add("chapel altars", {"type": "box", "width": 2.4, "length": 1.0, "height": 1.0, "at": altars,
                      "_about": "an altar in each chapel, against the face under its window"}, after="chapel steps")
# THE FLANKS CLOSED TO THE OCTAGON: the aisle walls stopped with the nave (z -6), but the octagon's diagonal face only
# reaches their line 9m further east -- a wedge of open air into the end of each aisle. Each flank runs on to it.
add("aisle wall east", {"type": "wall", "width": 9.1, "height": "aisleTop + 1.5", "thickness": "aisleT", "openings": [],
                        "at": [["halfA", 0, "zc - naveL / 2 - 4.55", "quarter"], ["0 - halfA", 0, "zc - naveL / 2 - 4.55", "0 - quarter"]],
                        "_about": "the flank walls' last stretch, from the nave's end to the octagon's diagonal face (buried in it at their inner corner)"}, after="aisle wall")
# THE AISLES' LAST STRETCH ROOFED: the aisle vaults and their lean-tos stop with the nave (z -6), the aisle's end wall
# stands 1.75m further east under the octagon's tribunes -- a slot open to the sky, the octagon's marbled faces seen up
# through it from the aisle floor. The lean-to runs on over it.
add("aisle end roofs", {"type": "roof", "form": "shed", "width": "aisleRoofOut - aisleRoofIn", "length": 1.85, "pitch": 5.5,
                        "at": [["0 - (aisleRoofIn + aisleRoofOut) / 2", "aisleTop - 0.4", "zc - naveL / 2 - 0.9", 0], ["(aisleRoofIn + aisleRoofOut) / 2", "aisleTop - 0.4", "zc - naveL / 2 - 0.9", 3.14159265]],
                        "_about": "each aisle's lean-to carried on past the nave's end to the aisle's east wall, closing the slot between them"}, after="aisle roofs")
add("seating", {"type": "zone", "zone": "seating", "w": "naveW - 2.8", "d": 27, "h": "arcadeH", "at": [[0, FLOOR, "zc + naveL / 2 - 6 - 13.5", 1.5707963]],
                "_about": "the congregation: pews down the nave on a middle aisle, facing the crossing (-z) -- clear of the arcade's piers, which stand 0.6 m into the nave"})
# ---- THE INTERIORS: the church's spaces, each on the middle of the walls round it (finish.js reads inside and out
# from them). The octagon's walls' middle (`dm`, on its flats) is where the crossing ends and the nave, the aisles'
# last stretch and the tribunes begin; the hollow pier's shaft is a space of its own in the middle of its wall.
dm = "(octR + octT / 2) * 0.92388"
mA = "halfA - aisleT / 2"                         # (the aisle walls' middle, and the facade's)
zW = "roofZ0 - pierT / 2"
add("body", {"type": "interior", "height": "aisleTop - 0.4",
             "plan": {"points": [[mA, zW], [mA, f"octZ + {dm} * 1.41421 - ({mA})"], [f"{dm} * 0.41421", f"octZ + {dm}"],
                                 [f"0 - {dm} * 0.41421", f"octZ + {dm}"], [f"0 - ({mA})", f"octZ + {dm} * 1.41421 - ({mA})"], [f"0 - ({mA})", zW]]},
             "at": [[0, 0, 0, 0]],
             "_about": "the nave and both aisles up to the aisles' roofs (no higher: the clerestory's outer face stands over them), from the facade to the octagon's west face and its diagonal faces the aisles end on"})
add("nave", {"type": "interior", "height": "naveTop", "plan": {"rect": ["2 * halfB - pierT", f"{zW} - octZ - {dm}"]},
             "at": [[0, 0, f"({zW} + octZ + {dm}) / 2", 0]],
             "_about": "the nave between the arcades' middles, up to its vault's back under the roof"})
add("crossing", {"type": "interior", "height": "drumTop", "plan": {"sides": 8, "radius": "octR + octT / 2"}, "at": [[0, 0, "octZ", 0]],
                 "_about": "the octagon and its drum, on their walls' middle, up to the dome's springing (the shells inside by their own shape)"})
# (a tribune: its half ring of five faces on their middle, its chord on the octagon's outer face -- the spandrels
#  stand beyond it either side -- and, the octagon's face wide, on across it to the octagon's middle, through the arch
#  it opens by)
trib = [[round(20.0 * math.sin(math.radians(a)), 4), round(20.0 * math.cos(math.radians(a)), 4)] for a in range(90, 271, 36)]
assert (P["tribR"], P["tribT"]) == (19.0, 2.0)
fl = "(octR + octT) * 0.38268"                     # (the octagon's outer face, half its width)
add("tribunes", {"type": "interior", "height": "tribH",
                 "plan": {"points": trib + [[f"0 - {fl}", 0], [f"0 - {fl}", "octT / 2 * 0.92388"], [fl, "octT / 2 * 0.92388"], [fl, 0]]},
                 "at": [list(q) for q in parts["tribune"]["place"]],
                 "_about": "the three tribunes, each up to its half dome, and across its chord into the octagon's arch"})
add("pier shaft", {"type": "interior", "height": "drumTop",
                   "plan": {"points": [[f"0 - (octR * 0.92388 + 0.25) * 0.41421", "octR * 0.92388 + 0.25"], [f"(octR * 0.92388 + 0.25) * 0.41421", "octR * 0.92388 + 0.25"],
                                       [f"((octR + octT) * 0.92388 - 0.25) * 0.41421", "(octR + octT) * 0.92388 - 0.25"], [f"0 - ((octR + octT) * 0.92388 - 0.25) * 0.41421", "(octR + octT) * 0.92388 - 0.25"]]},
                   "at": [[0, 0, "octZ", 0.785398]],
                   "_about": "the hollow pier's shaft, its stair's space, from the floor up to the shells: on its own walls' middle"})
add("lantern space", {"type": "interior", "height": "lanternH", "plan": {"sides": 32, "radius": "lanternR + 0.5"}, "at": [[0, 0, "octZ", 0]],
                      "atop": "dome", "atopR": "lanternR", "_about": "the lantern, inside its ring"})
add("campanile space", {"type": "interior", "height": "campH - 0.3", "plan": {"rect": ["campW - 3 * campT + campT", "campW - 3 * campT + campT"]},
                        "at": [["campX", 0, "campZ", 0]],
                        "_about": "the campanile's shaft round its stair, on its walls' middle, up to the terrace"})
# ---- GIOTTO'S CAMPANILE (2026-11-01): it was five equal storeys with one and the same window, a tower 12m wide with
# fins at its corners (walls set half a thickness in, and as wide as the whole tower), 13m from the church. It is five
# DIFFERENT zones on a square of 14.45m -- two of relief panels, hexagons under lozenges (0-15m), the niches with their
# sixteen statues (15-24), two storeys with a pair of two-light windows on each face (24-53), and the great three-light
# window of the last (53-81) -- under a cornice that juts out on corbels, an octagonal buttress at every corner the whole
# way up, and it stands 6m off the aisle wall, level with the facade. One wall a face, with the zones as its `tiers`.
FZ = "zc + naveL / 2 + pierT"
P.update({"campT": 3.3, "campIn": "campW - 2 * campT", "campX": "bodyW / 2 + 6 + campW / 2 + 1.2", "campZ": f"{FZ} - campW / 2 - 0.6"})
P["_campT"] = "the tower's walls are 4m thick at the foot on the real one"
for k in ("campanile base", "campanile base wall", "campanile", "campanile cornice"):
    parts.pop(k, None)
    if k in build: build.remove(k)
PT = {"profile": "pointed", "spread": 0.5}
BIFORA = lambda at: {"at": at, "width": 2.7, "sill": 2.2, "springing": 8.2, "head": PT, "tracery": 2, "glass": False, "wimperg": {"pitch": 60, "coping": 0.3, "depth": 0.25}}
NICHE = lambda at: {"at": at, "width": 1.5, "sill": 2.0, "springing": 4.8, "head": PT, "glass": False}
UP = [{"h": 9.0, "openings": [NICHE(u) for u in (-4.05, -1.35, 1.35, 4.05)]},
      {"h": 14.5, "openings": [BIFORA(-2.75), BIFORA(2.75)]},
      {"h": 14.5, "openings": [BIFORA(-2.75), BIFORA(2.75)]},
      {"openings": [{"at": 0, "width": 5.4, "sill": 3.2, "springing": 19.0, "head": {"profile": "pointed", "spread": 0.6}, "tracery": 3, "glass": False, "wimperg": {"pitch": 60, "coping": 0.4, "depth": 0.3}}]}]
FACES = [(0.0, "campZ + campW / 2", "campX"), (math.pi, "campZ - campW / 2", "campX"), (math.pi / 2, "campZ", "campX + campW / 2"), (-math.pi / 2, "campZ", "campX - campW / 2")]
def on_face(k, u, d):
    # a point on face k: u along it, d out from its line
    yaw = FACES[k][0]
    return f"campX + {u * math.cos(yaw) + (P['campW'] / 2 + d) * math.sin(yaw):.4f}", f"campZ + {-u * math.sin(yaw) + (P['campW'] / 2 + d) * math.cos(yaw):.4f}", round(yaw, 6)
wall_at = lambda k: [FACES[k][2], 0, FACES[k][1], round(FACES[k][0], 6)]
add("campanile", {"type": "wall", "width": "campW", "height": "campH", "thickness": "campT", "tiers": [{"h": 15.0, "openings": []}] + UP, "at": [wall_at(k) for k in (0, 2, 3)],
                  "_about": "a face of the tower, its zones as tiers: reliefs, niches, two storeys of pairs of two-light windows, the great three-light one"}, after="west wing upper")
add("campanile door face", {"type": "wall", "width": "campW", "height": "campH", "thickness": "campT",
                            "tiers": [{"h": 15.0, "openings": [{"at": 0, "width": "campDoorW", "sill": 0, "springing": "campDoorSpring", "head": {"profile": "arch", "spread": "arcSpread"}}]}] + UP,
                            "at": [wall_at(1)], "_about": "the same face with the door in its foot, so the stair can be reached from the ground"}, after="campanile")
cc = "campW / 2 - 0.1"
add("campanile buttresses", {"type": "column", "radius": 1.2, "height": "campH - 3.2", "sides": 8,
                             "at": [[f"campX {a} ({cc})", 0, f"campZ {b} ({cc})", round(math.pi / 8, 6)] for a in "+-" for b in "+-"],
                             "_about": "the octagonal buttress at each corner, from the ground to the corbels"}, after="campanile door face")
# the niches closed behind (an opening goes through the wall, and these are 90cm deep), a prophet standing in each
backs, saints, hexes, lozes = [], [], [], []
for k in range(4):
    for u in (-4.05, -1.35, 1.35, 4.05):
        x, z, yaw = on_face(k, u, -2.1)
        backs.append([x, 15 + 1.8, z, yaw])
        x, z, yaw = on_face(k, u, -0.5)
        saints.append([x, 17.0, z, yaw])
    for i in range(7):
        u = (i - 3) * 1.6
        x, z, yaw = on_face(k, u, 0.12)   # (its back on the wall's face: at the corners two walls overlap, and a point set inside both counts as inside neither)
        lozes.append([x, 11.3, z, yaw])
        if k != 1 or abs(u) > 2.5: hexes.append([x, 4.6, z, yaw])
add("campanile niche backs", {"type": "box", "width": 2.1, "length": 2.4, "height": 6.0, "at": backs, "_about": "what closes the niches: masonry, in the wall's thickness"}, after="campanile buttresses")
add("campanile statues", {"type": "pinnacle", "w": 0.7, "h": 0.2, "s": 0.02, "figure": 2.7, "at": saints, "_about": "the sixteen prophets and sibyls of the niche storey"}, after="campanile niche backs")
hx = lambda r: [[round(r * math.cos(i * math.pi / 3), 3), round(r * math.sin(i * math.pi / 3), 3)] for i in range(6)]
add("campanile hexagons", {"type": "screen", "outline": hx(0.72), "t": 0.12, "at": hexes, "_about": "Andrea Pisano's hexagonal reliefs, the lowest zone"}, after="campanile statues")
add("campanile lozenges", {"type": "screen", "outline": [[0.62, 0], [0, 0.95], [-0.62, 0], [0, -0.95]], "t": 0.12, "at": lozes, "_about": "the lozenges of the zone above, on their blue ground"}, after="campanile hexagons")
JOINTS = [15.0, 24.0, 38.5, 53.0]   # (the zones' joints: green and red in turn, a white moulding on each, and one between the two relief rows)
for k, y in enumerate(JOINTS, 1):
    add(f"{G if k % 2 else R} tower {k}", {"type": "enclosure", "plan": {"rect": ["campW + 0.12", "campW + 0.12"]}, "thickness": 0.1, "height": 0.45, "openings": [],
                                           "at": [["campX", y - 0.45, "campZ", 0]]})
add("campanile strings", {"type": "enclosure", "plan": {"rect": ["campW + 0.5", "campW + 0.5"]}, "thickness": 0.35, "height": 0.3, "openings": [],
                          "at": [["campX", y, "campZ", 0] for y in [8.1] + JOINTS], "_about": "a moulding at each joint between the zones"})
add("campanile corbels", {"type": "enclosure", "plan": {"rect": ["campW + 2.0", "campW + 2.0"]}, "thickness": 2.0, "height": 1.6, "openings": [], "at": [["campX", "campH - 3.2", "campZ", 0]],
                          "_about": "the corbel table the cornice juts out on"}, after="campanile terrace")
add("campanile cornice", {"type": "enclosure", "plan": {"rect": ["campW + 2.8", "campW + 2.8"]}, "thickness": 2.9, "height": 2.6, "openings": [], "at": [["campX", "campH - 1.6", "campZ", 0]],
                          "_about": "the cornice and the parapet round the terrace on its top"}, after="campanile corbels")
parts["pavement tower"].update({"width": "campW - campT", "length": "campW - campT"})
parts["campanile space"]["plan"] = {"rect": ["campW - campT", "campW - campT"]}
# ---- THE FACADE's outline (2026-11-01): De Fabris's front is three bays between four great piers carrying tabernacles;
# the wings rake up to the middle bay rather than stopping level, a pierced gallery along every rake; a row of the
# Madonna and apostles in niches runs the whole width over the portals; the gable carries the tondo. It had been two flat
# wings and a plain gable, a box with holes in it.
WTOP, RK, INNER = "aisleTop + 8.0", 36.8, "frontC / 2"
EDGE_X = "frontC / 2 + frontWing"
for sx, nm in ((1, "right"), (-1, "left")):
    add(f"west rake {nm}", {"type": "screen", "outline": [[f"{sx} * ({EDGE_X})", f"{WTOP} - 0.05"], [f"{sx} * ({INNER})", f"{WTOP} - 0.05"], [f"{sx} * ({INNER})", RK], [f"{sx} * ({EDGE_X})", WTOP]], "t": 1.0,
                            "at": [[0, 0, FZ, 0]], "_about": "the wing's top, raking up to the middle bay"}, after="west wing upper")
    add(f"west rake lace {nm}", {"type": "cresting", "run": [[f"{sx} * ({EDGE_X})", WTOP], [f"{sx} * ({INNER})", RK]], "h": 1.1, "panel": 1.5, "t": 0.2, "every": 3,
                                 "spirelet": {"w": 0.18, "s": 0.8}, "at": [[0, 0, f"{FZ} - 0.4", 0]]}, after=f"west rake {nm}")
# (the gable's apex: its half width at 32 degrees over naveTop)
add("west gable lace", {"type": "cresting", "run": [[-13.25, "naveTop"], [0, "naveTop + 8.28"], [13.25, "naveTop"]], "h": 1.0, "panel": 1.5, "t": 0.2, "every": 3,
                        "spirelet": {"w": 0.18, "s": 0.8}, "at": [[0, 0, f"{FZ} - 0.5", 0]], "_about": "the pierced gallery up the gable's rakes"}, after="west gable")
tondo = [[round(2.5 * math.cos(i * math.pi / 8), 3), round(2.5 * math.sin(i * math.pi / 8), 3)] for i in range(16)]
add("west tondo", {"type": "screen", "outline": tondo, "t": 0.2, "at": [[0, "naveTop + 2.7", f"{FZ} + 0.1", 0]], "_about": "the tondo in the gable"}, after="west gable lace")
add("west gable apex", {"type": "pinnacle", "w": 1.3, "h": 2.0, "s": 3.0, "gablets": 0.8, "at": [[0, "naveTop + 8.0", f"{FZ} - 0.5", 0]], "_about": "the tabernacle at the gable's peak"}, after="west tondo")
# the four piers: proud of the front in two stages, each with its tabernacle -- not all alike (the inner pair the taller,
# octagonal, a figure on each; the outer pair square)
PX = ["frontC / 2", EDGE_X]
add("west piers", {"type": "box", "width": 3.0, "length": 1.8, "height": 28.0, "at": [[f"{sx} * ({x})", 0, f"{FZ} - 0.2", 0] for sx in (1, -1) for x in PX], "_about": "the front's four piers, their lower stage"}, after="west wing upper")
add("west piers inner", {"type": "box", "width": 2.4, "length": 1.5, "height": "naveTop + 2.2 - 28", "at": [[f"{sx} * ({PX[0]})", 28, f"{FZ} - 0.2", 0] for sx in (1, -1)]}, after="west piers")
add("west piers outer", {"type": "box", "width": 2.4, "length": 1.5, "height": f"{WTOP} + 1.2 - 28", "at": [[f"{sx} * ({PX[1]})", 28, f"{FZ} - 0.2", 0] for sx in (1, -1)]}, after="west piers")
add("west pinnacles inner", {"type": "pinnacle", "w": 2.2, "h": 4.2, "s": 5.2, "sides": 8, "gablets": 1.2, "crockets": 3, "figure": 2.2, "at": [[f"{sx} * ({PX[0]})", "naveTop + 2.15", f"{FZ} - 0.2", 0] for sx in (1, -1)]}, after="west piers inner")
add("west pinnacles outer", {"type": "pinnacle", "w": 2.1, "h": 3.0, "s": 4.2, "gablets": 1.0, "crockets": 2, "at": [[f"{sx} * ({PX[1]})", f"{WTOP} + 1.15", f"{FZ} - 0.2", 0] for sx in (1, -1)]}, after="west piers outer")
# the row of the Madonna and the apostles over the portals, on a course the whole width, under canopies
APOS = [round(i * 2.45 - 8 * 2.45 / 2, 3) for i in range(9)] + [round(s * (15.6 + i * 2.2), 3) for s in (1, -1) for i in range(3)]
Y0 = 20.7
add("apostles course", {"type": "box", "width": "bodyW - 0.2", "length": 0.8, "height": 0.45, "at": [[0, Y0 - 0.45, f"{FZ} + 0.1", 0]], "_about": "the course the apostles stand on"}, after="west rose")
add("apostles", {"type": "pinnacle", "w": 0.8, "h": 0.2, "s": 0.02, "figure": 2.6, "at": [[x, Y0, f"{FZ} + 0.2", 0] for x in APOS], "_about": "the Madonna among the apostles, in a row across the front"}, after="apostles course")
add("apostles canopies", {"type": "pinnacle", "w": 1.05, "h": 0.25, "s": 1.5, "gablets": 0.45, "at": [[x, Y0 + 3.0, f"{FZ} + 0.2", 0] for x in APOS]}, after="apostles")
# ---- THE LANTERN (2026-11-01) was 21m to its eaves and 4.5 of cone -- the real one is 21m with its cone, ball and cross:
# 13 of octagon with tall lights, 7.5 of cone, a ball over two metres wide and the cross on it
P["lanternH"] = 13.0
parts["lantern"]["opening"].update({"springing": 7.5}); parts["lantern"]["polygon"] = True
parts["lantern roof"].update({"radius": "lanternR + 1.4", "head": {"profile": "trigonal", "rise": 7.5}})
parts["lantern buttresses"].update({"low": -0.25, "high": 7.5, "top1": 10.5, "width": 1.15})
add("lantern cross", {"type": "box", "width": 0.22, "length": 0.22, "height": 3.6, "atop": "lantern ball", "at": [[0, -0.2, "octZ", 0]], "_about": "the cross on the ball"}, after="lantern ball")
add("lantern cross arm", {"type": "box", "width": 1.5, "length": 0.2, "height": 0.2, "atop": "lantern ball", "at": [[0, 2.0, "octZ", 0]]}, after="lantern cross")
open(p, "w").write(json.dumps(d, indent=2) + "\n")
