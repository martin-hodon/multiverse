# NOTRE-DAME DE PARIS (1163-1345), the Gothic cathedral: its body is the `basilica` PART (arch/gothic.js) -- the
# vaulted skeleton of nave, crossing, transept, apse and ambulatory, with its piers, rib vaults, flying buttresses and
# roofs all worked out from the plan -- and round it the west front in three tiers with its two towers and a
# `domed-tower` flèche on the crossing.
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def gothic(file, name, about, P, spire=None, fleche=True, frontTiers=None, kings=False, more=None):
  """`more(add, P, A)`: a church's own parts besides (Regensburg's porch and Eselsturm), added before the file is written;
  A: the anchors of the layout, as expressions (side, towerZ, towerTop, front, bodyW, zCross, crossW)"""
  parts = {}; build = []
  def add(n, d): parts[n] = d; build.append(n)
  return _gothic(file, name, about, P, spire, fleche, parts, build, add, kings, more)

NOTRE_DAME = {"detail": 4, "bays": 9, "bayLen": 6.6, "naveW": 12.5, "aisleW": 10.5, "pierT": 1.4, "aisleT": 1.4,
     "naveL": "bays * bayLen", "bodyW": "naveW + 2 * pierT + 2 * aisleW + 2 * aisleT",
     "_naveW": "the nave's and the aisles' clear widths, between the walls' faces", "spring": 7.0,
     "arcadeH": 18.0, "clearH": 26.0, "_arcadeH": "the heights the furnishing is laid out to (the organ, the gallery)",
     "frontH": 43.0, "towerW": 13.4, "towerH": 26.0, "roofPitch": 50, "towerBays": 2,
     "_towerBays": "the aisles' last bays at the west end, which the towers stand over: they have no aisle vault or roof of their own",
     "towerD": "towerBays * bayLen + 3", "_towerD": "a tower's depth: over the aisle bays it stands on and the west front's 3m -- its back is the next bay's transverse arch",
     "crossA": 4, "_crossA": "the first of the two bays the crossing spans, from the west (the crossing square: two bays by the nave's width)",
     "zCross": "naveL / 2 - (crossA + 1) * bayLen", "arm": 3.0, "apse": 5, "pierR": 0.85, "shaft": 0.25, "clerSpring": 5.0, "flyerStages": 1,
     "_flyerStages": "Notre-Dame's flyers clear both aisles in one leap (rebuilt so in the 1220s); Cologne's in two, from intermediate piers",
     "_clerSpring": "the high vault springs this far over the clerestory sill: Notre-Dame's tall clerestory",
     # THE FRONT IS ITS OWN (2026-11-02): how it is stacked was fixed here for every church, and so Notre-Dame had Cologne's
     # wall -- narrow portals, a blank stage. `front` says it: the tiers' heights, the portals (width, springing), what stands
     # in the middle tier of the wall between the towers and of the towers, and an open gallery under the towers' free stage
     "pinnacleKinds": [{"h": 2.2, "s": 3.2, "gablets": 0.5, "crockets": 2}, {"sides": 8, "h": 1.7, "s": 3.6, "gablets": 0.45, "crockets": 3, "attendants": 0.22}],
     "front": {"h": [24, 12], "portal": [8.2, 8.6], "sidePortal": [7.0, 8.0], "towerOut": 0,
               "mid": {"at": 0, "width": 9.6, "sill": 6.0, "springing": 6.0, "head": {"profile": "semicircular"}, "foot": {"profile": "semicircular"}, "tracery": True},
               "towerMid": {"at": 0, "width": 5.8, "sill": 1.8, "springing": 6.4, "head": {"profile": "pointed", "spread": 0.8}, "tracery": 2},
               "gallery": {"pattern": "5", "width": 1.15, "gap": 0.8, "pier": 0.8, "sill": 1.2, "springing": 4.4, "head": {"profile": "pointed", "spread": 1.0}},
               "towerGallery": {"pattern": "6", "width": 1.15, "gap": 0.8, "pier": 0.8, "sill": 1.2, "springing": 4.4, "head": {"profile": "pointed", "spread": 1.0}},
               "belfry": {"width": 3.3, "gap": 1.4, "pier": 1.3},
               "courses": [20.0, 24.0, 36.0], "buttress": [[0, 20, 1.7], [20, 36, 1.0]], "kingsY": 20.3, "doors": {"below": 2.6}}}
def _gothic(file, name, about, P, spire, fleche, parts, build, add, kings=False, more=None):
  # ---- THE CHURCH AS ITS STRUCTURE (arch/gothic.js `basilica`): the arcade and the aisle wall as two lines running down
  # the bays and on round the apse, a compound pier at every node, every bay rib-vaulted -- nave, crossing, transept,
  # aisles, ambulatory, the apse's fan -- a flying buttress at every node of the aisle wall, round the chevet as down
  # the flanks, and the roofs on the same lines. Its heights are worked out from the springing and the aisle roof.
  add("church", {"type": "basilica", "bays": "bays", "bayLen": "bayLen", "naveW": "naveW + pierT", "aisleW": "(aisleW + (pierT + aisleT) / 2) / 2", "aisles": 2, "flyerStages": "flyerStages",
                 "t": "pierT", "aisleT": "aisleT", "apse": "apse", "spring": "spring", "pierR": "pierR", "shaft": "shaft",
                 "clerSpring": "clerSpring", "pitch": "roofPitch", "aislePitch": 18, "aisleWin": 3.0, "aisleSill": 4.0,
                 "skipAisle": [[0, "towerBays - 1"]], "transept": ["crossA", "crossA + 1"], "arm": "arm", "transeptT": 2.0,
                 "pinnacleKinds": P.pop("pinnacleKinds", []),
                 # (the staggered chevet, no ambulatory: `ambulatory` false, `chancelBays`, `sideApse` -- gothic.js; Regensburg's)
                 **{k: P.pop(k) for k in ("ambulatory", "chancelBays", "sideApse", "transeptRose", "choirWin", "choirButtress", "sideApsePitch") if k in P},
                 "at": [[0, 0, 0, 0]],
                 "_about": "nave, crossing, transept, apse and ambulatory as one vaulted skeleton: piers, arches, rib vaults, buttresses, flyers, roofs"})
  # ---- the west front, in three tiers, and its two towers
  F = P.pop("front", {}); OUT = F.get("towerOut", 0)
  side = f"bodyW / 2 - towerW / 2 - 0.5 + {OUT}"
  # THE TOWERS STAND ON THE GROUND. Each is a hollow square from the base up, in stages: a portal in its front, a
  # window over it, a blind stage to the top of the west front, and the belfry with its lancet pairs. Its back is an
  # arch across the aisle, which runs on through the tower's foot. (They used to stand ON the west front -- a 3m
  # wall -- and reach 12m back over nothing.) The west front is only what stands BETWEEN them.
  # (`portalGables`: a WIMPERG over each portal -- Cologne's, not Notre-Dame's, whose west portals stand under the
  # gallery of kings with none)
  gab = {"wimperg": True} if P.pop("portalGables", False) else {}
  pa = lambda w, sill, spring, spread=1, g=False: {"at": 0, "width": w, "sill": sill, "springing": spring, "head": {"profile": "pointed", "spread": spread}, **(gab if g else {})}
  BF = F.get("belfry", {})
  belfry = {"openings": {"pattern": "2", "width": BF.get("width", 1.8), "gap": BF.get("gap", 0.9), "pier": BF.get("pier", 0.9), "sill": 3.5, "springing": "towerH - 9", "head": {"profile": "pointed", "spread": 1.6}, **({"wimperg": BF["wimperg"]} if "wimperg" in BF else {})}, "glass": False}
  H0, H1 = F.get("h", [15, 12]); pw, ps = F.get("portal", [6.0, 7.5]); sw, ss = F.get("sidePortal", [5.0, 6.8])
  MID = F.get("mid", {"at": 0, "width": 9.6, "sill": 5.9, "springing": 5.9, "head": {"profile": "semicircular"}, "foot": {"profile": "semicircular"}, "tracery": True})
  add("west front", {"type": "wall", "width": f"2 * ({side}) - towerW", "height": "frontH", "thickness": 3.0, "at": [[0, 0, "naveL / 2 + 3", 0]],
                     "tiers": [{"h": H0, "openings": [pa(pw, 0, ps, g=True)]}, {"h": H1, "openings": [MID]},
                               {"openings": F.get("gallery", {"pattern": "4", "width": 1.3, "gap": 1.25, "pier": 1.25, "sill": 3.0, "springing": 10.5, "head": {"profile": "pointed", "spread": 1.4}}), "glass": False}],
                     "_about": "the west front between the towers, in three tiers: the central portal; the great rose; the open gallery"})
  # (inside behind it, up to the rose's tier: the nave's last stretch, from the west bay's piers to the middle of the
  #  front -- a wall stands back from its placement, its face there)
  add("west interior", {"type": "interior", "plan": {"rect": [f"2 * ({side}) - towerW", 3]}, "height": H0 + H1, "at": [[0, 0, "naveL / 2", 0]]})
  twr = lambda sx: [f"{sx} * ({side})", 0, "naveL / 2 + 3 - towerD / 2", 0]
  add("towers", {"type": "enclosure", "plan": {"rect": ["towerW", "towerD"]}, "thickness": 1.6, "height": "frontH + towerH",
                 "tiers": [{"h": H0, "openings": []}, {"h": H1, "openings": []}, {"h": f"frontH - {H0 + H1}", **({"openings": F["towerSide"]} if "towerSide" in F else {"openings": []})}, belfry],
                 "faces": {"0": [{"h": H0, "openings": [pa(sw, 0, ss, g=True)]}, {"h": H1, "openings": [F.get("towerMid", pa(2.6, 2.5, 8.0))]},
                                 {"h": f"frontH - {H0 + H1}", **({"openings": F["towerGallery"], "glass": False} if "towerGallery" in F else {"openings": []})}, belfry],
                           "2": [{"h": H0, "openings": [pa("towerW - 5.2", 0, f"{H0} - 1.1 - (towerW - 5.2) / 2 * 1.7321")]}, {"h": H1, "openings": []}, {"h": f"frontH - {H0 + H1}", "openings": []}, belfry]},
                 "at": [twr(-1), twr(1)], "interior": "frontH + towerH - 1",
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
  # ---- THE FRONT'S RELIEF: four great buttresses going up the towers' faces in stages (they are what divides it into three
  # bays; without them it was a sheet of stone), and the string courses that run across it all, towers and all
  half = f"({side}) + towerW / 2"
  bx = lambda sx, i: f"{sx} * ({side}) + {i} * (towerW / 2 - 1.1)"
  FZ_ = "naveL / 2 + 3"
  for k, (y0, y1, d) in enumerate(F.get("buttress", [])):
    add(f"front buttresses {k + 1}", {"type": "box", "width": max(2.2 - .3 * k, 1.2), "length": d, "height": y1 - y0, "at": [[bx(sx, i), y0, f"{FZ_} + {d / 2 - 0.05}", 0] for sx in (-1, 1) for i in (-1, 1)]})
    add(f"front buttresses side {k + 1}", {"type": "box", "width": d, "length": max(2.2 - .3 * k, 1.2), "height": y1 - y0, "at": [[f"{sx} * ({half} + {d / 2 - 0.05})", y0, f"{FZ_} - 1.1", 0] for sx in (-1, 1)]})
  if F.get("courses"):
    add("front courses", {"type": "box", "width": f"2 * ({half}) + 0.4", "length": 0.5, "height": 0.35, "at": [[0, y, f"{FZ_} + 0.2", 0] for y in F["courses"]],
                          "_about": "the string courses across the whole front"})
  if F.get("gable"):                                   # (a gable between the towers, on the wall's head, a pierced gallery up its rakes)
    gw, gh = f"({side}) - towerW / 2 - 0.1", F["gable"]
    add("west gable", {"type": "screen", "outline": [[f"0 - ({gw})", "frontH - 0.05"], [gw, "frontH - 0.05"], [0, f"frontH + {gh}"]], "t": 1.2, "at": [[0, 0, FZ_, 0]], "_about": "the gable over the great window, between the towers"})
    add("west gable lace", {"type": "cresting", "run": [[f"0 - ({gw})", "frontH"], [0, f"frontH + {gh}"], [gw, "frontH"]], "h": 1.2, "panel": 1.6, "t": 0.25, "every": 3, "spirelet": {"w": 0.2, "s": 0.9}, "at": [[0, 0, f"{FZ_} - 0.4", 0]]})
    add("west gable apex", {"type": "pinnacle", "w": 1.2, "h": 1.6, "s": 3.2, "gablets": 0.5, "crockets": 2, "at": [[0, f"frontH + {gh} - 0.4", f"{FZ_} - 0.6", 0]]})
  # ---- the flèche over the crossing
  if fleche: add("fleche", {"type": "component", "use": "components/domed-tower",
                 "params": {"sides": 8, "R": 2.6, "H": 9.0, "t": 0.3, "cap": "trigonal", "capRise": 34, "capR": 2.9, "drumR": 2.1, "drumH": 2.5,
                            "kok": 0.3, "finial": 2.5, "glazed": 0},
                 "build": ["tower", "drum", "cap", "finial"], "atop": "church", "atopLevel": "ridge", "at": [[0, -2.5, "zCross", 0]],
                 "_about": "the flèche: a slender octagonal lantern and spire over the crossing -- the domed-tower component with a very tall tent"})
  
  if spire:
    # SPIRES on the towers (Cologne's): an octagonal stage and an openwork spire on each tower's middle, the
    # terrace round it walked on -- the domed-tower component with a very tall tent
    op = spire.pop("open", None)
    if "octagon" in spire:
      # ...or (`octagon`: Regensburg's, Ulm's) an open OCTAGON STAGE (`gothic-octagon-stage`, its params) on each
      # tower, `feet` the gables and pinnacles round the spire's foot (`gothic-spire`'s), and the openwork spire on it
      oc, ft = spire["octagon"], spire.get("feet")
      tz, y2 = "naveL / 2 + 3 - towerD / 2", f"frontH + towerH + {oc['H']}"
      add("tower octagons", {"type": "component", "use": "components/gothic-octagon-stage", "params": oc, "build": spire.get("octagonBuild", ["walls"]),
                             "at": [[f"{sx} * ({side})", "frontH + towerH", tz, 0] for sx in (-1, 1)],
                             "_about": "the open octagon on each tower, a tall traceried lancet in every face (`gothic-octagon-stage`)"})
      if ft: add("tower spire feet", {"type": "component", "use": "components/gothic-spire", "params": ft, "build": ["gables", "pinnacles"],
                                      "at": [[f"{sx} * ({side})", y2, tz, 0] for sx in (-1, 1)], "_about": "the gables and pinnacles round each spire's foot (`gothic-spire`)"})
      if op: add("tower spires", {"type": "open-spire", **op, "at": [[f"{sx} * ({side})", y2, tz, 0] for sx in (-1, 1)], "_about": "the OPENWORK spires"})
    else:
     add("spires", {"type": "component", "use": "components/domed-tower", "params": spire,
                   "build": ["tower", "kokoshniki", "neck", "drum"] + ([] if op else ["cap", "finial"]),
                   "at": [[f"{sx} * ({side})", "frontH + towerH", "naveL / 2 + 3 - towerD / 2", 0] for sx in (-1, 1)],
                   "_about": "the spires: an octagonal lantern stage on each tower and its spire"})
     if op:
       add("open spires", {"type": "open-spire", **op, "at": [[f"{sx} * ({side})", f"frontH + towerH + {spire['H'] + spire['drumH']} - 0.1", "naveL / 2 + 3 - towerD / 2", 0] for sx in (-1, 1)],
                           "_about": "the openwork spires, the sky showing through them"})
    # ...and a pinnacle on each corner of the square tower's head, carrying the eye from the square to the octagon
    # (`pinnacles` among the spire's keys: their params)
    add("tower pinnacles", {"type": "component", "use": "components/pinnacle", "params": spire.get("pinnacles", {"w": 1.8, "h": 5.0, "s": 8.0}),
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
    half = bodyW / 2 - 0.5 + OUT                                    # the front's half width, towers included
    z0, yK = naveL / 2 + 3, F.get("kingsY", 11.2)                   # its face; the gallery's floor: over the portals' heads, under the rose
    add("gallery of kings ledge", {"type": "box", "width": round(2 * half, 3), "length": 1.0, "height": 0.4, "at": [[0, yK - 0.4, round(z0 + 0.5, 3), 0]],
                                   "_about": "the ledge the kings stand on, across the whole west front"})
    add("gallery of kings canopy", {"type": "box", "width": round(2 * half, 3), "length": 1.0, "height": 0.35, "at": [[0, yK + 3.4, round(z0 + 0.5, 3), 0]],
                                    "_about": "the canopy over the kings"})
    # (28 kings, in the front's three stretches between its buttresses, shared by width -- spread evenly over the whole width, some had stood inside a buttress with a hand showing;
    #  a pointed arcade over them, a colonnette between each two: the row is an arcade, not a shelf)
    towerW = P["towerW"]; sideN = half - towerW / 2; inner = sideN - towerW / 2; clear = 1.3
    runs = [(-half + clear, -inner - clear), (-inner + clear, inner - clear), (inner + clear, half - clear)]
    tot = sum(b - a for a, b in runs); counts = [round(28 * (runs[0][1] - runs[0][0]) / tot), 0, 0]; counts[2] = counts[0]; counts[1] = 28 - 2 * counts[0]
    pts = []; cols = []; hK = 3.2
    for run_i, ((a, b), c) in enumerate(zip(runs, counts)):
      w = (b - a) / c; pts += [(a + (i + 0.5) * w, yK, z0 + 0.5) for i in range(c)]
      cols += [[round(a + i * w, 3), yK, round(z0 + 0.82, 3), 0] for i in range(c + 1)]
      out = [(a, hK + 0.8), (b, hK + 0.8), (b, hK - 0.1)]
      for i in range(c): x1 = b - i * w; out += [(x1 - w / 2, hK + 0.32), (x1 - w, hK - 0.1)]
      add(f"gallery of kings arcade {run_i + 1}", {"type": "screen", "outline": [[round(x, 3), round(y, 3)] for x, y in out], "t": 0.75, "at": [[0, yK, round(z0 + 1.0, 3), 0]], "_about": "the pointed arcade over the kings"})
    add("gallery of kings colonnettes", {"type": "column", "radius": 0.11, "height": hK - 0.1, "sides": 6, "at": cols})
    parts.pop("gallery of kings canopy"); build.remove("gallery of kings canopy")
    for k, v in capped(row("king", pts, kind="man", style="gothic", stone="limestone", scale=1.75, face=FACE_PZ)).items(): add(k, v)
  if F.get("doors"):
    # THE PORTALS CLOSED: each a pointed arch with its archivolts (rings of stone stepped back into the wall), a tympanum over a lintel, and under it the door
    # (assets/doors/notre-dame.json: the leaves, as the game hangs them)
    fz = float(P["bays"]) * P["bayLen"] / 2 + 3; L = F["doors"]
    def arc(w, spring, n=8):          # (a pointed arch, equilateral: its right half from the springing to the crown)
      return [(w / 2 - w * (1 - math.cos(t)), spring + w * math.sin(t)) for t in [math.radians(60) * k / n for k in range(n + 1)]]
    bodyW = P["naveW"] + 2 * P["pierT"] + 2 * P["aisleW"] + 2 * P["aisleT"]; sx_ = bodyW / 2 - P["towerW"] / 2 - 0.5 + OUT
    for nm, x, (w, sp), dep, shut in (("central", 0.0, (pw, ps), 1.5, False), ("north", -sx_, (sw, ss), 1.0, True), ("south", sx_, (sw, ss), 1.0, True)):
      top = arc(w, sp); inner_w = w - 0.1; lint = sp - L["below"]; tz = fz - dep
      half_outline = [(x_, y_) for x_, y_ in arc(inner_w, sp)]
      tym = [(inner_w / 2, lint)] + half_outline[0:] + [(-a, b) for a, b in reversed(half_outline[:-1])] + [(-inner_w / 2, lint)]
      add(f"{nm} tympanum", {"type": "screen", "outline": [[round(a, 3), round(b, 3)] for a, b in tym], "t": 0.4, "at": [[round(x, 3), 0, round(tz, 3), 0]], "_about": "the tympanum filling the arch's head, carved in the real one, over its lintel"})
      add(f"{nm} lintel", {"type": "box", "width": round(inner_w, 3), "length": 0.5, "height": 0.7, "at": [[round(x, 3), round(lint - 0.5, 3), round(tz + 0.05, 3), 0]]})
      add(f"{nm} trumeau", {"type": "column", "radius": 0.34, "height": round(lint - 0.5, 3), "sides": 8, "at": [[round(x, 3), 0, round(tz + 0.12, 3), 0]], "_about": "the pier parting the doorway"}) if shut else None
      # (three archivolt rings: each a band following the arch, stepped forward of the last)
      for k in range(3):
        wa, wb = w + 0.02 - k * 0.5, w + 0.02 - (k + 1) * 0.5
        oa, ob = arc(wa, sp), arc(wb, sp)
        ring = [(a, b) for a, b in oa] + [(-a, b) for a, b in reversed(oa[:-1])] + [(-a, b) for a, b in ob[:-1]] + [(a, b) for a, b in reversed(ob)]
        add(f"{nm} archivolt {k + 1}", {"type": "screen", "outline": [[round(a, 3), round(b, 3)] for a, b in ring], "t": 0.35, "at": [[round(x, 3), 0, round(fz - dep + 0.4 + (2 - k) * 0.35, 3), 0]], "_about": "a ring of the arch's mouldings"})
      # (the door under the lintel is not a part: its leaves hang in the doorway and open -- assets/doors/notre-dame.json)
  # (`more` gets the anchors of what gothic() laid out, as expressions: a tower's x is `sx * side`)
  if more: more(add, P, {"side": f"({side})", "towerZ": "naveL / 2 + 3 - towerD / 2", "towerTop": "frontH + towerH", "front": "naveL / 2 + 3",
                         "bodyW": "bodyW", "zCross": "zCross", "crossW": "naveL / 2 - crossA * bayLen"})
  doc = {"name": name, "_about": about, "params": P, "base": {"height": 0.9, "steps": 3, "stepOut": 0.6, "margin": 4}, "railing": {"type": "stone"}, "build": build, "parts": parts}
  open(os.path.join(ROOT, f"assets/architecture/{file}.json"), "w").write(json.dumps(doc, indent=2) + "\n")

if __name__ == "__main__": gothic("notre-dame", "Notre-Dame de Paris", "NOTRE-DAME DE PARIS, the Gothic cathedral as its structure: the `basilica` part lays out the arcade and the aisle wall as two lines down the nave and round the five-sided apse, stands a compound pier at every node, vaults every bay -- nave, crossing, transept arms, aisles, the trapezoids of the ambulatory and the apse's fan -- on ribs springing from vaulting shafts, and props the high vault with a flying buttress and pinnacle at every node of the aisle wall, round the chevet as down the flanks; the west front in three TIERS (three portals, the great rose between lancets, the gallery) under its two flat-topped towers; the transept's ends with their roses over portals; and on the crossing the flèche, the `domed-tower` component with a 28m tent; across the west front above the portals, the Gallery of Kings: twenty-eight limestone kings of Judah on their ledge under a canopy.", NOTRE_DAME, kings=True)
