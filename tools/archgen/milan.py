# MILAN CATHEDRAL (Duomo di Milano, 1386-1965; the fabric and its forest of spires): five aisles stepping down --
# the `basilica` for the nave and inner aisles, rib-vaulted outer aisles of its own -- buttresses and pinnacles
# down both flanks, the five-portal facade, the transept, the polygonal apse, the tiburio and its spire with the
# Madonnina; spiral turrets up to the roofs, which are walked on.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
P = {"detail": 4, "bays": 10, "bayLen": 9.5, "naveW": 16.4, "aisleW": 9.6, "pierT": 2.8, "aisleT": 2.0,
     "naveL": "bays * bayLen", "spring": 13.0, "arcadeH": 27.0, "clearH": 32.0, "aisleRise": 3.5,
     "crown": "spring + (bayLen - pierT) / 2 * 1.7321", "aisleTop": "crown + aisleRise + 0.6", "naveTop": "clearH + naveW / 2 * 1.7321 + 1.2",
     "innerX": "naveW / 2 + pierT + aisleW", "outerX": "innerX + aisleT + aisleW", "wallX": "outerX + aisleT",
     "outerSpring": 11.0, "outerTop": "outerSpring + aisleW / 2 * 1.7321 + 0.8", "outerWallH": "outerTop + 1.2",
     "innerWallH": "aisleTop + 1.8", "crossZ": "0 - naveL / 2 + 2 * bayLen", "facadeH": 50.0, "facadeEave": 30.0, "facadePitch": "facadeH - facadeEave",
     "_innerX": "the inner aisles' outer edge: the arcade between the two aisles on each side stands there",
     "_crossZ": "the crossing, two bays from the east end of the nave"}
add("nave", {"type": "component", "use": "basilica",
             "params": {"bays": "bays", "bayLen": "bayLen", "naveW": "naveW", "aisleW": "aisleW", "pierT": "pierT", "aisleT": "aisleT",
                        "openW": "bayLen - pierT", "spring": "spring", "crown": "crown", "arcadeH": "arcadeH", "clearH": "clearH",
                        "naveTop": "naveTop", "aisleSpring": "crown", "aisleTop": "aisleTop",
                        "arch": "pointed", "arcSpread": 1, "naveSpread": 1, "clearSpread": 1,
                        "aisleArch": "segmental", "aisleRise": "aisleRise", "aisleAlongArch": "segmental", "aisleAlongRise": "aisleRise",
                        "naveAlongArch": "pointed", "naveAlongSpread": "((naveW / bayLen) * (naveW / bayLen) * 3 - 1) / 2",
                        "clearWinW": 2.2, "clearSill": 1.2, "clearSpring": "clearH - arcadeH - 2.2"},
             "build": ["arcade", "clerestory", "nave vault", "nave ribs", "aisle vault", "aisle ribs"], "at": [[0, 0, 0, 0]],
             "_about": "the nave and the inner aisles: the `basilica` definition"})
# the arcade between inner and outer aisles, the outer aisles' vaults and ribs, the outer walls
for sx, nm in ((1, "right"), (-1, "left")):
    add(f"aisle arcade {nm}", {"type": "wall", "width": "naveL", "height": "innerWallH", "thickness": "aisleT",
        "openings": {"pattern": "bays", "width": "bayLen - aisleT", "gap": "aisleT", "sill": 0, "springing": "outerSpring - 1",
                     "head": {"profile": "pointed", "spread": 1}},
        "at": [[f"{sx} * (innerX + aisleT)", 0, 0, f"{sx} * 1.5707963"]]})
    add(f"outer wall {nm}", {"type": "wall", "width": "naveL", "height": "outerWallH", "thickness": "aisleT",
        "openings": {"pattern": "bays", "width": 3.4, "gap": "bayLen - 3.4", "sill": 4.0, "springing": 13.0,
                     "head": {"profile": "pointed", "spread": 1.2}},
        "at": [[f"{sx} * wallX", 0, 0, f"{sx} * 1.5707963"]],
        "_about": "(a wall turned a quarter reaches from its line inward: set on wallX, it stands between wallX - aisleT and wallX)"})
add("outer vaults", {"type": "groin", "width": "aisleW", "length": "bayLen", "springing": "outerSpring", "top": "outerTop",
                     "across": {"profile": "pointed", "spread": 1}, "along": {"profile": "pointed", "spread": "((aisleW / bayLen) * (aisleW / bayLen) * 3 - 1) / 2"},
                     "at": [["innerX + aisleT + aisleW / 2", 0, "0 - naveL / 2 + bayLen / 2", 0], ["0 - innerX - aisleT - aisleW / 2", 0, "0 - naveL / 2 + bayLen / 2", 0]],
                     "repeat": {"count": "bays - 1", "step": [0, 0, "bayLen", 0]},
                     "_about": "the outer aisles' vaults, all but the westernmost bay's: that one is the stair turret's, under a flat terrace"})
add("outer ribs", {"type": "ribs", "on": "outer vaults", "width": 0.35, "depth": 0.25, "wall": {"width": 0.45, "depth": 0.3}})
# roofs: low, walked on
add("nave roof", {"type": "roof", "form": "gable", "width": "naveW + 2 * pierT + 0.4", "length": "naveL", "pitch": 22, "at": [[0, "naveTop", 0, 0]]})
add("inner aisle roofs", {"type": "roof", "form": "shed", "width": "aisleW + 0.3", "length": "naveL", "pitch": 8,
                          "at": [["0 - (naveW / 2 + pierT + aisleW / 2)", "innerWallH", 0, 0], ["naveW / 2 + pierT + aisleW / 2", "innerWallH", 0, 3.14159265]]})
add("outer aisle roofs", {"type": "roof", "form": "shed", "width": "aisleW + aisleT", "length": "naveL - bayLen", "pitch": 8,
                          "at": [["0 - (innerX + aisleT / 2 + aisleW / 2 + aisleT / 2)", "outerWallH", "0 - bayLen / 2", 0], ["innerX + aisleT / 2 + aisleW / 2 + aisleT / 2", "outerWallH", "0 - bayLen / 2", 3.14159265]]})
# buttresses and pinnacles down both flanks: a flying buttress from every outer pier to the inner arcade, a pinnacle
# on every pier of the inner arcade too
fb = {"pierH": "outerWallH + 3", "pierD": 2.4, "span": "wallX + 1.2 - innerX - aisleT", "low": "outerWallH + 0.5", "high": "innerWallH - 0.8",
      "top0": "outerWallH + 2.6", "top1": "innerWallH + 1.4", "pin": 1.5, "pinH": 5.0, "pinS": 7.0}
add("flank buttresses", {"type": "component", "use": "components/flying-buttress", "params": fb,
                         "at": [["wallX + 1.2", 0, "0 - naveL / 2", 3.14159265], ["0 - wallX - 1.2", 0, "0 - naveL / 2", 0]],
                         "repeat": {"count": "bays", "step": [0, 0, "bayLen", 0]}})
add("arcade pinnacles", {"type": "component", "use": "components/pinnacle", "params": {"w": 1.2, "h": 4.0, "s": 6.0},
                         "at": [["innerX + aisleT / 2", "innerWallH", "0 - naveL / 2", 0], ["0 - innerX - aisleT / 2", "innerWallH", "0 - naveL / 2", 0]],
                         "repeat": {"count": "bays", "step": [0, 0, "bayLen", 0]}})
add("clerestory pinnacles", {"type": "component", "use": "components/pinnacle", "params": {"w": 1.0, "h": 3.0, "s": 5.0},
                             "at": [["naveW / 2 + pierT", "naveTop", "0 - naveL / 2", 0], ["0 - naveW / 2 - pierT", "naveTop", "0 - naveL / 2", 0]],
                             "repeat": {"count": "bays", "step": [0, 0, "bayLen", 0]}})
# the facade: five portals, five great windows, a gable zone; six buttresses with their pinnacles
bx = ["0 - wallX + 1", "0 - innerX - aisleT / 2", "0 - naveW / 2 - pierT / 2", "naveW / 2 + pierT / 2", "innerX + aisleT / 2", "wallX - 1"]
mid = ["0 - (innerX + aisleT + aisleW / 2)", "0 - (naveW / 2 + pierT + aisleW / 2)", "0", "naveW / 2 + pierT + aisleW / 2", "innerX + aisleT + aisleW / 2"]
# THE FACADE IS ONE GABLE: a wall to `facadeEave` across the whole width, and on it a single triangle of stone up
# to `facadeH` at the middle -- no square shoulders. The buttresses climb with its slope, the outer ones lowest,
# each carrying its pinnacle at the gable's edge.
add("facade", {"type": "wall", "width": "2 * wallX", "height": "facadeEave", "thickness": 2.4, "at": [[0, 0, "naveL / 2 + 2.4", 0]],
               "tiers": [{"h": 15, "openings": [{"at": m, "width": 6.0 if m == "0" else 4.2, "sill": 0, "springing": 9.0 if m == "0" else 7.5,
                                                "head": {"profile": "pointed", "spread": 1}} for m in mid]},
                         {"openings": [{"at": m, "width": 4.0 if m == "0" else 3.0, "sill": 1.5, "springing": 9.0,
                                        "head": {"profile": "pointed", "spread": 1.4}} for m in mid]}],
               "_about": "the facade below the gable, in two tiers: five portals, and five great pointed windows over them"})
add("facade gable", {"type": "roof", "form": "gable", "width": "2 * wallX", "length": 2.4, "pitch": 30.32, "at": [[0, "facadeEave", "naveL / 2 + 1.2", 0]],
                     "_about": "the gable: one triangle across the whole front, its apex over the nave (pitch: facadeH - facadeEave over wallX)"})
slope = "(facadePitch) / wallX"
heights = {x: f"facadeEave + (wallX - {ax}) * {slope} + 2" for x, ax in zip(bx, ["(wallX - 1)", "(innerX + aisleT / 2)", "(naveW / 2 + pierT / 2)",
                                                                                  "(naveW / 2 + pierT / 2)", "(innerX + aisleT / 2)", "(wallX - 1)"])}
add("facade buttresses", {"type": "box", "width": 2.2, "length": 3.2, "height": "facadeEave", "at": [[x, 0, "naveL / 2 + 3.6", 0] for x in bx]})
for k, x in enumerate(bx):
    add(f"facade buttress {k + 1}", {"type": "box", "width": 2.2, "length": 3.2, "height": f"{heights[x]} - facadeEave",
                                      "at": [[x, "facadeEave", "naveL / 2 + 3.6", 0]],
                                      **({"_about": "each buttress on up with the gable's slope: the outer ones lowest, the two by the nave highest"} if k == 0 else {})})
add("facade pinnacles", {"type": "component", "use": "components/pinnacle", "params": {"w": 2.0, "h": 6.0, "s": 10.0},
                         "at": [[x, heights[x], "naveL / 2 + 3.6", 0] for x in bx]})
# the transept
add("transept", {"type": "enclosure", "plan": {"rect": [14, "2 * bayLen"]}, "thickness": 2.0, "height": "innerWallH",
                 "openings": [{"at": 0, "width": 3.4, "sill": 4.0, "springing": 15.0, "head": {"profile": "pointed", "spread": 1.2}}],
                 "faces": {"3": [], "1": []},
                 "at": [["wallX + 7", 0, "crossZ", 0], ["0 - wallX - 7", 0, "crossZ", 0]]})
add("transept roofs", {"type": "roof", "form": "gable", "width": "2 * bayLen", "length": 14.4, "pitch": 22,
                       "at": [["wallX + 7", "innerWallH", "crossZ", 1.5707963], ["0 - wallX - 7", "innerWallH", "crossZ", 1.5707963]]})
# the apse: a polygonal chevet (half an octagon) round the ambulatory, the choir's inner half ring, its vault and roofs
apse = [[0, 0, "0 - naveL / 2", 0]]
add("chevet", {"type": "ring", "count": 8, "turn": 0.5, "at": [2, 3, 4, 5], "rOuter": "wallX", "rInner": "wallX - aisleT", "height": "outerWallH",
               "opening": {"width": 4.0, "sill": 4.0, "springing": 14.0, "head": {"profile": "pointed", "spread": 1.2}}, "place": apse})
add("choir", {"type": "ring", "count": 8, "turn": 0.5, "at": [2, 3, 4, 5], "rOuter": "naveW / 2 + pierT", "rInner": "naveW / 2", "height": "naveTop",
              "opening": {"width": 3.2, "sill": "arcadeH + 1", "springing": "clearH + 5", "head": {"profile": "pointed", "spread": 1}}, "place": apse})
add("choir vault", {"type": "dome", "sweep": 0.5, "sides": 8, "radius": "naveW / 2 + pierT", "thickness": "pierT", "head": {"profile": "pointed", "spread": 1},
                    "at": [[0, "clearH", "0 - naveL / 2", 3.14159265]]})
add("choir roof", {"type": "dome", "sweep": 0.5, "sides": 8, "radius": "naveW / 2 + pierT + 0.3", "thickness": 0, "head": {"profile": "trigonal", "rise": 4.5},
                   "at": [[0, "naveTop", "0 - naveL / 2", 3.14159265]]})
add("ambulatory roof", {"type": "dome", "sweep": 0.5, "sides": 8, "radius": "wallX + 0.3", "thickness": 0, "head": {"profile": "trigonal", "rise": 6},
                        "oculus": "naveW / 2 + pierT", "cap": False,
                        "at": [[0, "outerWallH", "0 - naveL / 2", 3.14159265]],
                        "_about": "the lean-to round the choir: a half cone cut off at the choir's wall (`oculus`) and left open there"})
# the tiburio over the crossing, its spire, the Madonnina
add("tiburio", {"type": "component", "use": "components/domed-tower",
                "params": {"sides": 8, "R": 7.5, "H": 12, "t": 1.0, "cap": "trigonal", "capRise": 28, "capR": 4.2, "drumR": 3.6, "drumH": 6,
                           "kok": 1.5, "finial": 4.2, "winW": 1.8},
                "build": ["tower", "kokoshniki", "neck", "drum", "cap", "finial"], "at": [[0, "naveTop + 2", "crossZ", 0]],
                "_about": "the tiburio: the octagonal lantern over the crossing, its spire and the Madonnina at the top -- the domed-tower component, gabled, with a tall tent"})
# spiral turrets up to the roofs, in the westernmost bay of each outer aisle: the stair climbs from the aisle floor to
# a flat terrace over that bay, round the turret, and out through a door onto it; from there the aisle roofs are walked
tR, tz = 2.4, "naveL / 2 - 2.6"
for sx, nm in ((1, "right"), (-1, "left")):
    tx = f"{sx} * (wallX - aisleT - {tR + 0.25})"
    # the turret, its door (bay 4 of 8: -z, into the aisle -- the turret stands at the component's middle, so say it) and the
    # spiral from the door up through its open head onto the terrace -- `tower-stair`, less the floor it would lay
    add(f"stair {nm}", {"type": "component", "use": "components/tower-stair", "params": {"W": 6.0, "H": "outerWallH", "tR": tR, "tx": 0, "tz": 0, "doorBay": 4, "hand": "right" if sx > 0 else "left"},
                        "build": ["turret", "turret door", "stair"], "at": [[tx, 0, tz, 0]]})
    # the terrace over the turret's bay: the bay less the turret -- cut to the turret's octagon (its faces a = tR cos 22.5
    # from its middle), so there is no crack round the stair's head -- as two slabs: beside it, and east of it
    a = round(tR * 0.92388, 4)
    tcx = f"(wallX - aisleT - {tR + 0.25})"                          # the turret's middle, from the axis
    wa = f"({tcx} - {a} - innerX - aisleT)"                          # from the arcade to the turret's inner face
    add(f"stair terrace {nm}", {"walked": True, "type": "box", "width": wa, "length": "bayLen", "height": 0.4,
        "at": [[f"{sx} * (innerX + aisleT + {wa} / 2)", "outerWallH - 0.4", "naveL / 2 - bayLen / 2", 0]],
        "_about": "the flat roof over the turret's bay, beside the turret"})
    le = f"(bayLen - 2.6 - {a})"                                     # from the bay's east end to the turret's east face
    add(f"stair terrace east {nm}", {"walked": True, "type": "box", "width": f"wallX - aisleT - {tcx} + {a}", "length": le, "height": 0.4,
        "at": [[f"{sx} * (({tcx} - {a} + wallX - aisleT) / 2)", "outerWallH - 0.4", f"naveL / 2 - bayLen + {le} / 2", 0]],
        "_about": "...and east of it"})
# ---- INSIDE (as notre_dame.py gothic): seating up to the crossing (crossZ), the altar east of it, the organ on a west gallery over the first bay
gal = "arcadeH * 0.45"
add("west gallery", {"walked": True, "type": "box", "width": "naveW", "length": "bayLen - 0.4", "height": 0.5, "at": [[0, f"{gal} - 0.5", "naveL / 2 - bayLen / 2 + 0.2", 0]],
                     "_about": "the organ loft: a gallery across the nave's west bay, the doors passing under it"})
add("gallery parapet", {"type": "box", "width": "naveW", "length": 0.25, "height": 1.0, "at": [[0, gal, "naveL / 2 - bayLen + 0.4", 0]]})
add("seating", {"type": "zone", "zone": "seating", "w": "naveW - 1.6", "d": "(naveL / 2 - bayLen - 1.5) - (crossZ + bayLen + 1.5)", "h": "arcadeH",
                "at": [[0, 0, "((crossZ + bayLen + 1.5) + (naveL / 2 - bayLen - 1.5)) / 2", 1.5707963]]})
add("altar", {"type": "zone", "zone": "altar", "w": "naveW - 2", "d": 3.2, "h": "arcadeH", "at": [[0, 0, "crossZ - bayLen - 2.5", 1.5707963]]})
add("organ", {"type": "zone", "zone": "organ", "w": "min(naveW - 2, 10)", "d": "bayLen * 0.6", "h": f"(clearH - {gal}) * 0.6", "at": [[0, gal, "naveL / 2 - bayLen / 2 + 0.6", 1.5707963]]})
doc = {"name": "Milan Cathedral",
  "_about": "THE DUOMO OF MILAN, from components: the nave and inner aisles are the `basilica`, and outer aisles of its own step down beside them, every bay rib-vaulted; down both flanks a `flying-buttress` at every bay with its pinnacle and a `pinnacle` on every pier of the inner arcade and the clerestory -- the forest of spires; the facade in three tiers (five portals, five windows, a rose) between six buttresses with their pinnacles; the transept arms; the polygonal chevet round the choir with its half vault; the tiburio over the crossing with its spire and the Madonnina (the `domed-tower`). Spiral turrets inside the facade climb to the aisle roofs, and flights from there to the nave roof: the roofs are walked on.",
  "params": P, "base": {"height": 1.2, "steps": 4, "stepOut": 0.8, "margin": 3}, "railing": {"type": "stone"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/milan.json"), "w").write(json.dumps(doc, indent=2) + "\n")
