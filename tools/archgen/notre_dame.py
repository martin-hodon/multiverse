# NOTRE-DAME DE PARIS (1163-1345), the Gothic cathedral: its body is the `basilica` PART (arch/gothic.js) -- the
# vaulted skeleton of nave, crossing, transept, apse and ambulatory, with its piers, rib vaults, flying buttresses and
# roofs all worked out from the plan -- and round it the west front in three tiers with its two towers and a
# `domed-tower` flèche on the crossing.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def gothic(file, name, about, P, spire=None, fleche=True, frontTiers=None, kings=False):
  parts = {}; build = []
  def add(n, d): parts[n] = d; build.append(n)
  return _gothic(file, name, about, P, spire, fleche, parts, build, add, kings)

NOTRE_DAME = {"detail": 4, "bays": 9, "bayLen": 6.6, "naveW": 12.5, "aisleW": 10.5, "pierT": 1.4, "aisleT": 1.4,
     "naveL": "bays * bayLen", "bodyW": "naveW + 2 * pierT + 2 * aisleW + 2 * aisleT",
     "_naveW": "the nave's and the aisles' clear widths, between the walls' faces", "spring": 7.0,
     "arcadeH": 18.0, "clearH": 26.0, "_arcadeH": "the heights the furnishing is laid out to (the organ, the gallery)",
     "frontH": 43.0, "towerW": 12.0, "towerH": 26.0, "roofPitch": 50, "towerBays": 2,
     "_towerBays": "the aisles' last bays at the west end, which the towers stand over: they have no aisle vault or roof of their own",
     "towerD": "towerBays * bayLen + 3", "_towerD": "a tower's depth: over the aisle bays it stands on and the west front's 3m -- its back is the next bay's transverse arch",
     "crossA": 4, "_crossA": "the first of the two bays the crossing spans, from the west (the crossing square: two bays by the nave's width)",
     "zCross": "naveL / 2 - (crossA + 1) * bayLen", "arm": 3.0, "apse": 5, "pierR": 0.85, "shaft": 0.25, "clerSpring": 5.0, "flyerStages": 1,
     "_flyerStages": "Notre-Dame's flyers clear both aisles in one leap (rebuilt so in the 1220s); Cologne's in two, from intermediate piers",
     "_clerSpring": "the high vault springs this far over the clerestory sill: Notre-Dame's tall clerestory"}
def _gothic(file, name, about, P, spire, fleche, parts, build, add, kings=False):
  # ---- THE CHURCH AS ITS STRUCTURE (arch/gothic.js `basilica`): the arcade and the aisle wall as two lines running down
  # the bays and on round the apse, a compound pier at every node, every bay rib-vaulted -- nave, crossing, transept,
  # aisles, ambulatory, the apse's fan -- a flying buttress at every node of the aisle wall, round the chevet as down
  # the flanks, and the roofs on the same lines. Its heights are worked out from the springing and the aisle roof.
  add("church", {"type": "basilica", "bays": "bays", "bayLen": "bayLen", "naveW": "naveW + pierT", "aisleW": "(aisleW + (pierT + aisleT) / 2) / 2", "aisles": 2, "flyerStages": "flyerStages",
                 "t": "pierT", "aisleT": "aisleT", "apse": "apse", "spring": "spring", "pierR": "pierR", "shaft": "shaft",
                 "clerSpring": "clerSpring", "pitch": "roofPitch", "aislePitch": 18, "aisleWin": 3.0, "aisleSill": 4.0,
                 "skipAisle": [[0, "towerBays - 1"]], "transept": ["crossA", "crossA + 1"], "arm": "arm", "transeptT": 2.0,
                 "at": [[0, 0, 0, 0]],
                 "_about": "nave, crossing, transept, apse and ambulatory as one vaulted skeleton: piers, arches, rib vaults, buttresses, flyers, roofs"})
  # ---- the west front, in three tiers, and its two towers
  side = "bodyW / 2 - towerW / 2 - 0.5"
  # THE TOWERS STAND ON THE GROUND. Each is a hollow square from the base up, in stages: a portal in its front, a
  # window over it, a blind stage to the top of the west front, and the belfry with its lancet pairs. Its back is an
  # arch across the aisle, which runs on through the tower's foot. (They used to stand ON the west front -- a 3m
  # wall -- and reach 12m back over nothing.) The west front is only what stands BETWEEN them.
  # (`portalGables`: a WIMPERG over each portal -- Cologne's, not Notre-Dame's, whose west portals stand under the
  # gallery of kings with none)
  gab = {"wimperg": True} if P.pop("portalGables", False) else {}
  pa = lambda w, sill, spring, spread=1, g=False: {"at": 0, "width": w, "sill": sill, "springing": spring, "head": {"profile": "pointed", "spread": spread}, **(gab if g else {})}
  belfry = {"openings": {"pattern": "2", "width": 1.8, "gap": 0.9, "pier": 0.9, "sill": 3.5, "springing": "towerH - 9", "head": {"profile": "pointed", "spread": 1.6}}, "glass": False}
  add("west front", {"type": "wall", "width": f"2 * ({side}) - towerW", "height": "frontH", "thickness": 3.0, "at": [[0, 0, "naveL / 2 + 3", 0]],
                     "tiers": [{"h": 15, "openings": [pa(6.0, 0, 7.5, g=True)]},
                               {"h": 12, "openings": [{"at": 0, "width": 9.6, "sill": 5.9, "springing": 5.9, "head": {"profile": "semicircular"}, "foot": {"profile": "semicircular"}, "tracery": True}]},
                               {"openings": {"pattern": "4", "width": 1.3, "gap": 1.25, "pier": 1.25, "sill": 3.0, "springing": 10.5, "head": {"profile": "pointed", "spread": 1.4}}, "glass": False}],
                     "_about": "the west front between the towers, in three tiers: the central portal; the great rose; the open gallery"})
  twr = lambda sx: [f"{sx} * ({side})", 0, "naveL / 2 + 3 - towerD / 2", 0]
  add("towers", {"type": "enclosure", "plan": {"rect": ["towerW", "towerD"]}, "thickness": 1.6, "height": "frontH + towerH",
                 "tiers": [{"h": 15, "openings": []}, {"h": 12, "openings": []}, {"h": "frontH - 27", "openings": []}, belfry],
                 "faces": {"0": [{"h": 15, "openings": [pa(5.0, 0, 6.8, g=True)]}, {"h": 12, "openings": [pa(2.6, 2.5, 8.0)]}, {"h": "frontH - 27", "openings": []}, belfry],
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
                       "at": [[f"{sx} * ({side})", 0, "naveL / 2 + 3 - towerD / 2", 0 if sx > 0 else 3.14159265] for sx in (-1, 1)],
                       "_about": "the stair up each tower (`tower-stair`): the spiral turret against the outer flank, from the aisle to the terrace on top, which is the floor round its head"})
  add("tower parapets", {"type": "enclosure", "plan": {"rect": ["towerW + 0.4", "towerD + 0.4"]}, "thickness": 0.4, "height": 1.4, "openings": [],
                         "at": [[a[0], "frontH + towerH", a[2], 0] for a in (twr(-1), twr(1))]})
  # ---- the flèche over the crossing
  if fleche: add("fleche", {"type": "component", "use": "components/domed-tower",
                 "params": {"sides": 8, "R": 1.8, "H": 5.0, "t": 0.3, "cap": "trigonal", "capRise": 28, "capR": 2.0, "drumR": 1.4, "drumH": 2.5,
                            "kok": 0.3, "finial": 2.5, "glazed": 0},
                 "build": ["tower", "drum", "cap", "finial"], "atop": "church", "atopLevel": "ridge", "at": [[0, -2.5, "zCross", 0]],
                 "_about": "the flèche: a slender octagonal lantern and spire over the crossing -- the domed-tower component with a very tall tent"})
  
  if spire:
    # SPIRES on the towers (Cologne's): an octagonal stage and an openwork spire on each tower's middle, the
    # terrace round it walked on -- the domed-tower component with a very tall tent
    add("spires", {"type": "component", "use": "components/domed-tower", "params": spire,
                   "build": ["tower", "kokoshniki", "neck", "drum", "cap", "finial"],
                   "at": [[f"{sx} * ({side})", "frontH + towerH", "naveL / 2 + 3 - towerD / 2", 0] for sx in (-1, 1)],
                   "_about": "the spires: an octagonal lantern stage on each tower and its spire"})
    # ...and a pinnacle on each corner of the square tower's head, carrying the eye from the square to the octagon
    add("tower pinnacles", {"type": "component", "use": "components/pinnacle", "params": {"w": 1.8, "h": 5.0, "s": 8.0},
                            "at": [[f"{sx} * ({side}) + {cx} * (towerW / 2 - 1.1)", "frontH + towerH", f"naveL / 2 + 3 - towerD / 2 + {cz} * (towerD / 2 - 1.1)", 0]
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
  add("seating", {"type": "zone", "zone": "seating", "w": "naveW - 1.6", "d": "(naveL / 2 - bayLen - 1.5) - (zCross + bayLen + 1.5)", "h": "arcadeH",
                  "at": [[0, 0, "((zCross + bayLen + 1.5) + (naveL / 2 - bayLen - 1.5)) / 2", 1.5707963]],
                  "_about": "the nave's seating between the arcades, from under the gallery up to the crossing, on a middle aisle"})
  add("altar", {"type": "zone", "zone": "altar", "w": "naveW - 2", "d": 3.2, "h": "arcadeH", "at": [[0, 0, "zCross - bayLen - 2.5", 1.5707963]], "_about": "the high altar just east of the crossing"})
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

if __name__ == "__main__": gothic("notre-dame", "Notre-Dame de Paris", "NOTRE-DAME DE PARIS, the Gothic cathedral as its structure: the `basilica` part lays out the arcade and the aisle wall as two lines down the nave and round the five-sided apse, stands a compound pier at every node, vaults every bay -- nave, crossing, transept arms, aisles, the trapezoids of the ambulatory and the apse's fan -- on ribs springing from vaulting shafts, and props the high vault with a flying buttress and pinnacle at every node of the aisle wall, round the chevet as down the flanks; the west front in three TIERS (three portals, the great rose between lancets, the gallery) under its two flat-topped towers; the transept's ends with their roses over portals; and on the crossing the flèche, the `domed-tower` component with a 28m tent; across the west front above the portals, the Gallery of Kings: twenty-eight limestone kings of Judah on their ledge under a canopy.", NOTRE_DAME, kings=True)
