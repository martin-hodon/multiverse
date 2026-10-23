# NOTRE-DAME DE PARIS (1163-1345), the Gothic cathedral from components: the `basilica` definition for its nave --
# arcades, clerestory, aisle walls and RIB VAULTS -- and `flying-buttress`es down both flanks and round the chevet,
# the west front in three tiers with its two towers, the transept's rose windows, the apse and a `domed-tower` flèche.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def gothic(file, name, about, P, spire=None, fleche=True, frontTiers=None, kings=False):
  parts = {}; build = []
  def add(n, d): parts[n] = d; build.append(n)
  return _gothic(file, name, about, P, spire, fleche, parts, build, add, kings)

NOTRE_DAME = {"detail": 4, "bays": 9, "bayLen": 6.6, "naveW": 12.5, "aisleW": 10.5, "pierT": 1.4, "aisleT": 1.4,
     "naveL": "bays * bayLen", "bodyW": "naveW + 2 * pierT + 2 * aisleW + 2 * aisleT",
     "spring": 7.0, "arcadeH": 18.0, "clearH": 26.0, "aisleRise": 3.5, "clearSill": 2.2,
     "crown": "spring + (bayLen - pierT) / 2 * 1.7321", "aisleTop": "crown + aisleRise + 0.6", "naveTop": "clearH + naveW / 2 * 1.7321 + 1.2",
     "aisleWallH": "aisleTop + 1.2", "frontH": 43.0, "towerW": 12.0, "towerH": 26.0, "roofPitch": 50,
     "ridge": "(naveW / 2 + pierT + 0.3) * 1.1918", "towerBays": 2,
     "_towerBays": "the aisles' last bays at the west end, which the towers stand over: they have no aisle vault or roof of their own", "flyerX": "bodyW / 2 + 1.2", "flyerSpan": "flyerX - naveW / 2 - pierT",
     "_crown": "the arcade's crown: a pointed (equilateral) head over the gap between two piers",
     "_ridge": "the nave roof's height over its eaves: half its width times tan(roofPitch)",
     "_flyerX": "where a flying buttress's pier stands: 1.2m clear of the aisle wall"}
def _gothic(file, name, about, P, spire, fleche, parts, build, add, kings=False):
  # ---- the nave: the basilica, as a component
  add("nave", {"type": "component", "use": "basilica",
               "params": {"bays": "bays", "bayLen": "bayLen", "naveW": "naveW", "aisleW": "aisleW", "pierT": "pierT", "aisleT": "aisleT",
                          "openW": "bayLen - pierT", "spring": "spring", "crown": "crown", "arcadeH": "arcadeH", "clearH": "clearH",
                          "naveTop": "naveTop", "aisleSpring": "crown", "aisleTop": "aisleTop",
                          "arch": "pointed", "arcSpread": 1, "naveSpread": 1, "clearSpread": 1,
                          "aisleArch": "segmental", "aisleRise": "aisleRise", "aisleAlongArch": "segmental", "aisleAlongRise": "aisleRise",
                          "aisleBays": "bays - towerBays",
                        "naveAlongArch": "pointed", "naveAlongSpread": "((naveW / bayLen) * (naveW / bayLen) * 3 - 1) / 2",
                          "winW": 3.0, "winSill": 4.0, "clearWinW": 2.4, "clearSill": "clearSill", "clearSpring": "clearH - arcadeH - 2.2",
                          "_naveAlongSpread": "the vault's arch ALONG a bay is a lancet: steep enough over the short span to reach the crown of the wide one"},
               "build": ["arcade", "clerestory", "aisle wall", "nave vault", "nave ribs", "aisle vault", "aisle ribs"],
               "at": [[0, 0, 0, 0]],
               "_about": "the nave from the `basilica` definition: arcades, clerestory, aisle walls, and rib vaults over nave and aisles"})
  # ---- roofs
  add("nave roof", {"type": "roof", "form": "gable", "width": "naveW + 2 * pierT + 0.6", "length": "naveL", "pitch": "roofPitch",
                    "at": [[0, "naveTop", 0, 0]]})
  add("aisle roofs", {"type": "roof", "form": "shed", "width": "bodyW / 2 - naveW / 2 - pierT", "length": "naveL + 3 - towerW", "pitch": 15,
                      "at": [["0 - (bodyW / 2 + naveW / 2 + pierT) / 2", "aisleWallH", "(3 - towerW) / 2", 0], ["(bodyW / 2 + naveW / 2 + pierT) / 2", "aisleWallH", "(3 - towerW) / 2", 3.14159265]],
                      "_about": "a lean-to over each aisle, up to the towers' back faces"})
  # ---- flying buttresses, one at every bay's end down each flank
  fb = {"pierH": 24, "span": "flyerSpan", "low": 20.5, "high": "clearH - 1", "top0": 23.5, "top1": "clearH + 2.2"}
  add("flank buttresses", {"type": "component", "use": "components/flying-buttress", "params": fb,
                           "at": [["flyerX", 0, "0 - naveL / 2 + bayLen", 3.14159265], ["0 - flyerX", 0, "0 - naveL / 2 + bayLen", 0]],
                           "repeat": {"count": "bays - 1 - towerBays", "step": [0, 0, "bayLen", 0]},
                           "_about": "a flying buttress at every bay's end, both sides: pier, pinnacle, and the flyer to the clerestory"})
  # ---- the west front, in three tiers, and its two towers
  side = "bodyW / 2 - towerW / 2 - 0.5"
  # THE TOWERS STAND ON THE GROUND. Each is a hollow square from the base up, in stages: a portal in its front, a
  # window over it, a blind stage to the top of the west front, and the belfry with its lancet pairs. Its back is an
  # arch across the aisle, which runs on through the tower's foot. (They used to stand ON the west front -- a 3m
  # wall -- and reach 12m back over nothing.) The west front is only what stands BETWEEN them.
  pa = lambda w, sill, spring, spread=1: {"at": 0, "width": w, "sill": sill, "springing": spring, "head": {"profile": "pointed", "spread": spread}}
  belfry = {"openings": {"pattern": "2", "width": 1.8, "gap": 0.9, "pier": 0.9, "sill": 3.5, "springing": "towerH - 9", "head": {"profile": "pointed", "spread": 1.6}}, "glass": False}
  add("west front", {"type": "wall", "width": f"2 * ({side}) - towerW", "height": "frontH", "thickness": 3.0, "at": [[0, 0, "naveL / 2 + 3", 0]],
                     "tiers": [{"h": 15, "openings": [pa(6.0, 0, 7.5)]},
                               {"h": 12, "openings": [{"at": 0, "width": 9.6, "sill": 5.9, "springing": 5.9, "head": {"profile": "semicircular"}, "foot": {"profile": "semicircular"}}]},
                               {"openings": {"pattern": "4", "width": 1.3, "gap": 1.25, "pier": 1.25, "sill": 3.0, "springing": 10.5, "head": {"profile": "pointed", "spread": 1.4}}, "glass": False}],
                     "_about": "the west front between the towers, in three tiers: the central portal; the great rose; the open gallery"})
  twr = lambda sx: [f"{sx} * ({side})", 0, "naveL / 2 + 3 - towerW / 2", 0]
  add("towers", {"type": "enclosure", "plan": {"rect": ["towerW", "towerW"]}, "thickness": 1.6, "height": "frontH + towerH",
                 "tiers": [{"h": 15, "openings": []}, {"h": 12, "openings": []}, {"h": "frontH - 27", "openings": []}, belfry],
                 "faces": {"0": [{"h": 15, "openings": [pa(5.0, 0, 6.8)]}, {"h": 12, "openings": [pa(2.6, 2.5, 8.0)]}, {"h": "frontH - 27", "openings": []}, belfry],
                           "2": [{"h": 15, "openings": [pa("towerW - 5.2", 0, "15 - 1.1 - (towerW - 5.2) / 2 * 1.7321")]}, {"h": 12, "openings": []}, {"h": "frontH - 27", "openings": []}, belfry]},
                 "at": [twr(-1), twr(1)],
                 "_about": "the two towers, from the ground: a portal in the front, a window, a blind stage, then the belfry's lancet pairs; the back an arch across the aisle"})
  # the towers' TOPS: a terrace slab in each, round the hatch the stair turret comes up through, and a spiral turret
  # from the aisle floor all the way up (387 steps on the real ones). It stands against the middle of the tower's
  # OUTER flank, clear of the portal and of the arch across the aisle, and inside the plan of an octagon of up to
  # nearly the tower's width -- so a spire stage on the tower (Cologne's) stands over the stair's head, not on it.
  turretR = 2.1                                    # (treads 1.4m clear: a walker passes on either side of the grid)
  off = P["towerW"] / 2 - 2.6 - turretR           # its shaft a metre clear of the flank wall (the aisle wall runs on inside it)
  add("tower stairs", {"type": "component", "use": "components/tower-stair",
                       "params": {"W": "towerW - 3.2", "H": "frontH + towerH", "tR": turretR, "tx": round(off, 4), "tz": 0, "hand": "left"},
                       "at": [[f"{sx} * ({side})", 0, "naveL / 2 + 3 - towerW / 2", 0 if sx > 0 else 3.14159265] for sx in (-1, 1)],
                       "_about": "the stair up each tower (`tower-stair`): the spiral turret against the outer flank, from the aisle to the terrace on top, which is the floor round its head"})
  add("tower parapets", {"type": "enclosure", "plan": {"rect": ["towerW + 0.4", "towerW + 0.4"]}, "thickness": 0.4, "height": 1.4, "openings": [],
                         "at": [[a[0], "frontH + towerH", a[2], 0] for a in (twr(-1), twr(1))]})
  # ---- the transept: its two gable ends, each with a rose over a portal, and its roof across the nave's
  add("transept ends", {"type": "wall", "width": "bayLen * 2", "height": "naveTop", "thickness": 2.0,
                        "tiers": [{"h": 14, "openings": [{"at": 0, "width": 4.4, "sill": 0, "springing": 7.0, "head": {"profile": "pointed", "spread": 1}}]},
                                  {"openings": [{"at": 0, "width": 11.0, "sill": 6.6, "springing": 6.6, "head": {"profile": "semicircular"}, "foot": {"profile": "semicircular"}}]}],
                        "at": [["bodyW / 2 + 3", 0, 0, 1.5707963], ["0 - bodyW / 2 - 3", 0, 0, -1.5707963]],
                        "_about": "the transept's two ends, each a portal and over it a rose window 11m across"})
  add("transept sides", {"type": "box", "width": 4.4, "length": 1.6, "height": "naveTop",
                         "at": [[f"{sx} * (bodyW / 2 + 1)", 0, f"{sz} * (bayLen - 0.8)", 0] for sx in (1, -1) for sz in (1, -1)]})
  add("transept roof", {"type": "roof", "form": "gable", "width": "bayLen * 2 + 0.6", "length": "bodyW + 7", "pitch": "roofPitch",
                        "at": [[0, "naveTop", 0, 1.5707963]], "_about": "the transept's roof, crossing the nave's at the same eaves"})
  # ---- the chevet: the apse, its vault, its roofs, the ambulatory, and flying buttresses all round it
  apse = [0, 0, "0 - naveL / 2", 0]
  half = {"count": 12, "turn": 0.5, "at": [3, 4, 5, 6, 7, 8], "place": [apse]}
  add("apse arcade", {"type": "ring", **half, "rOuter": "naveW / 2 + pierT", "rInner": "naveW / 2", "height": "arcadeH",
                      "opening": {"width": 3.0, "sill": 0, "springing": "spring", "head": {"profile": "pointed", "spread": 1}}})
  add("apse clerestory", {"type": "ring", **half, "rOuter": "naveW / 2 + pierT", "rInner": "naveW / 2", "height": "naveTop - arcadeH", "y": "arcadeH",
                          "_about": "the apse's upper wall, up to the roof's eaves: it encloses the half vault as the nave's spandrels do its bays",
                          "opening": {"width": 1.8, "sill": "clearSill", "springing": "clearH - arcadeH - 2.0", "head": {"profile": "pointed", "spread": 1}}})
  add("apse vault", {"type": "dome", "sweep": 0.5, "sides": 24, "radius": "naveW / 2 + pierT", "thickness": "pierT", "head": {"profile": "pointed", "spread": 1},
                     "at": [[0, "clearH", "0 - naveL / 2", 3.14159265]], "_about": "the apse's half vault: the nave vault's own pointed section turned round"})
  add("apse roof", {"type": "dome", "sweep": 0.5, "sides": 24, "radius": "naveW / 2 + pierT + 0.3", "thickness": 0, "head": {"profile": "trigonal", "rise": "ridge"},
                    "at": [[0, "naveTop", "0 - naveL / 2", 3.14159265]]})
  add("ambulatory wall", {"type": "ring", **half, "rOuter": "bodyW / 2", "rInner": "bodyW / 2 - aisleT", "height": "aisleWallH",
                          "opening": {"width": 3.0, "sill": 4.0, "springing": 6.4, "head": {"profile": "pointed", "spread": 1}}})
  add("ambulatory roof", {"type": "dome", "sweep": 0.5, "sides": 24, "radius": "bodyW / 2 + 0.3", "thickness": 0, "head": {"profile": "trigonal", "rise": 6.5},
                          "oculus": "naveW / 2 + pierT", "cap": False,
                          "at": [[0, "aisleWallH", "0 - naveL / 2", 3.14159265]],
                          "_about": "the lean-to round the apse: a half cone cut off at the apse's wall (`oculus`) and left open there"})
  rad = []
  for deg in (112.5, 146.25, 180, 213.75, 247.5):
      th = math.radians(deg)
      rad.append([f"(flyerX) * {math.sin(th):.6f}", 0, f"0 - naveL / 2 + (flyerX) * {math.cos(th):.6f}", round(th + math.pi / 2, 6)])
  add("chevet buttresses", {"type": "component", "use": "components/flying-buttress", "params": fb, "at": rad,
                            "_about": "the flying buttresses standing round the chevet, radiating"})
  # ---- the flèche over the crossing
  if fleche: add("fleche", {"type": "component", "use": "components/domed-tower",
                 "params": {"sides": 8, "R": 1.8, "H": 5.0, "t": 0.3, "cap": "trigonal", "capRise": 28, "capR": 2.0, "drumR": 1.4, "drumH": 2.5,
                            "kok": 0.3, "finial": 2.5, "glazed": 0},
                 "build": ["tower", "drum", "cap", "finial"], "at": [[0, "naveTop + ridge - 2.5", 0, 0]],
                 "_about": "the flèche: a slender octagonal lantern and spire over the crossing -- the domed-tower component with a very tall tent"})
  
  if spire:
    # SPIRES on the towers (Cologne's): an octagonal stage and an openwork spire on each tower's middle, the
    # terrace round it walked on -- the domed-tower component with a very tall tent
    add("spires", {"type": "component", "use": "components/domed-tower", "params": spire,
                   "build": ["tower", "kokoshniki", "neck", "drum", "cap", "finial"],
                   "at": [[f"{sx} * ({side})", "frontH + towerH", "naveL / 2 + 3 - towerW / 2", 0] for sx in (-1, 1)],
                   "_about": "the spires: an octagonal lantern stage on each tower and its spire"})
    # ...and a pinnacle on each corner of the square tower's head, carrying the eye from the square to the octagon
    add("tower pinnacles", {"type": "component", "use": "components/pinnacle", "params": {"w": 1.8, "h": 5.0, "s": 8.0},
                            "at": [[f"{sx} * ({side}) + {cx} * (towerW / 2 - 1.1)", "frontH + towerH", f"naveL / 2 + 3 - towerW / 2 + {cz} * (towerW / 2 - 1.1)", 0]
                                   for sx in (-1, 1) for cx in (-1, 1) for cz in (-1, 1)],
                            "_about": "a pinnacle on every corner of the towers' heads, where the octagon stage begins"})
  # ---- INSIDE: the floor marked by use (zones, assets/architecture/furnishing.json): the nave's seating up to the
  # crossing, the high altar east of it, and the organ on a WEST GALLERY -- a loft over the first bay, so the west
  # doors below it stay clear (an organ on the floor would block them). The liturgical east is -z here: zones yaw pi/2.
  gal = "arcadeH * 0.45"   # the gallery's floor height
  add("west gallery", {"walked": True, "type": "box", "width": "naveW", "length": "bayLen - 0.4", "height": 0.5,
                       "at": [[0, f"{gal} - 0.5", "naveL / 2 - bayLen / 2 + 0.2", 0]],
                       "_about": "the organ loft: a gallery across the nave's west bay, the doors passing under it"})
  add("gallery parapet", {"type": "box", "width": "naveW", "length": 0.25, "height": 1.0, "at": [[0, gal, "naveL / 2 - bayLen + 0.4", 0]]})
  add("seating", {"type": "zone", "zone": "seating", "w": "naveW - 1.6", "d": "(naveL / 2 - bayLen - 1.5) - (bayLen + 1.5)", "h": "arcadeH",
                  "at": [[0, 0, "((bayLen + 1.5) + (naveL / 2 - bayLen - 1.5)) / 2", 1.5707963]],
                  "_about": "the nave's seating between the arcades, from under the gallery up to the crossing, on a middle aisle"})
  add("altar", {"type": "zone", "zone": "altar", "w": "naveW - 2", "d": 3.2, "h": "arcadeH", "at": [[0, 0, "0 - bayLen - 2.5", 1.5707963]], "_about": "the high altar just east of the crossing"})
  add("organ", {"type": "zone", "zone": "organ", "w": "min(naveW - 2, 10)", "d": "bayLen * 0.6", "h": f"(clearH - {gal}) * 0.6",
                "at": [[0, gal, "naveL / 2 - bayLen / 2 + 0.6", 1.5707963]], "_about": "the great organ on the west gallery, its pipes facing east down the nave"})
  if kings:
    # THE GALLERY OF KINGS (c. 1220): twenty-eight kings of Judah standing in a row across the whole west front -- towers
    # and all -- above the portals, on their ledge under a canopy: limestone, crowned and robed, looking out over the square
    import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from statuary import row, FACE_PZ, capped
    naveL = P["bays"] * P["bayLen"]; bodyW = P["naveW"] + 2 * P["pierT"] + 2 * P["aisleW"] + 2 * P["aisleT"]
    half = bodyW / 2 - P["towerW"] / 2 - 0.5 + P["towerW"] / 2      # the front's half width, towers included
    z0, yK = naveL / 2 + 3, 11.2                                    # its face; the gallery's floor: over the portals' heads, under the rose
    add("gallery of kings ledge", {"type": "box", "width": round(2 * half, 3), "length": 1.0, "height": 0.4, "at": [[0, yK - 0.4, round(z0 + 0.5, 3), 0]],
                                   "_about": "the ledge the kings stand on, across the whole west front"})
    add("gallery of kings canopy", {"type": "box", "width": round(2 * half, 3), "length": 1.0, "height": 0.35, "at": [[0, yK + 3.4, round(z0 + 0.5, 3), 0]],
                                    "_about": "the canopy over the kings"})
    n = 28
    for k, v in capped(row("king", [(-half + (i + 0.5) * 2 * half / n, yK, z0 + 0.5) for i in range(n)],
                           kind="man", style="gothic", stone="limestone", scale=1.75, face=FACE_PZ)).items(): add(k, v)
  doc = {"name": name, "_about": about, "params": P, "base": {"height": 0.9, "steps": 3, "stepOut": 0.6, "margin": 4}, "railing": {"type": "stone"}, "build": build, "parts": parts}
  open(os.path.join(ROOT, f"assets/architecture/{file}.json"), "w").write(json.dumps(doc, indent=2) + "\n")

if __name__ == "__main__": gothic("notre-dame", "Notre-Dame de Paris", "NOTRE-DAME DE PARIS, the Gothic cathedral from components: its nave is the `basilica` definition (pointed arcades, clerestory, aisle walls and rib vaults over nave and aisles -- the vault's arch along a bay a lancet steep enough to meet the crown of the wide one); `flying-buttress`es -- pier, pinnacle, flyer -- at every bay down both flanks and in a ring round the chevet; the west front in three TIERS (three portals, the great rose between lancets, the gallery) under its two flat-topped towers; the transept's ends with their 11m roses; the apse with its half vault and half-cone roof over the ambulatory; and the flèche, the `domed-tower` component with a 28m tent; across the west front above the portals, the Gallery of Kings: twenty-eight limestone kings of Judah on their ledge under a canopy.", NOTRE_DAME, kings=True)
