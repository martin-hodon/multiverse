# COLOGNE CATHEDRAL (1248-1880): the same Gothic cathedral as Notre-Dame (notre_dame.py `gothic`), with Cologne's
# numbers -- a taller, wider nave with double aisles, 14.4m towers rising over the aisles to a hundred metres,
# and on each an octagonal stage and an openwork spire to 157m; the stair in the tower climbs to the terrace
# the spire stands on, as the real one does.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notre_dame import gothic, NOTRE_DAME
P = {**NOTRE_DAME, "bays": 11, "bayLen": 7.6, "naveW": 14.0, "aisleW": 12.0, "pierT": 1.6, "aisleT": 1.6,
     "spring": 9.0, "arcadeH": 21.0, "clearH": 31.0, "frontH": 55.0, "towerW": 19.5, "towerH": 45.0, "roofPitch": 55,
     "towerBays": 2, "crossA": 5, "clerSpring": 6.0, "flyerStages": 2, "portalGables": True,
     "pinnacleKinds": [{"sides": 8, "h": 2.6, "s": 4.6, "gablets": 0.55, "crockets": 3, "attendants": 0.25}, {"h": 2.2, "s": 4.0, "gablets": 0.5, "crockets": 2}, {"h": 2.5, "s": 3.4, "gablets": 0.6, "crockets": 3, "attendants": 0.3}],
     # (the real front is 61.5m wide on a body of 45: the towers, 20m square, stand well out past the aisle walls; no rose --
     #  a great traceried window over the middle portal, three more stages of tall traceried windows under gables on each tower)
     "front": {"h": [22, 20], "portal": [8.0, 9.5], "sidePortal": [6.0, 8.5], "towerOut": 8.5,
               "mid": {"at": 0, "width": 12.0, "sill": 1.0, "springing": 9.5, "head": {"profile": "pointed", "spread": 0.8}, "tracery": 4},
               "towerMid": {"at": 0, "width": 8.0, "sill": 2.0, "springing": 12.0, "head": {"profile": "pointed", "spread": 0.8}, "tracery": 3, "wimperg": {"pitch": 62, "coping": 0.4, "depth": 0.35}},
               "gallery": {"pattern": "6", "width": 1.3, "gap": 1.2, "pier": 1.0, "sill": 2.0, "springing": 8.0, "head": {"profile": "pointed", "spread": 1.2}},
               "towerGallery": {"pattern": "2", "width": 3.4, "gap": 2.6, "pier": 2.0, "sill": 1.5, "springing": 7.5, "head": {"profile": "pointed", "spread": 1.0}},
               "towerSide": {"pattern": "2", "width": 3.4, "gap": 3.0, "pier": 2.0, "sill": 1.5, "springing": 7.5, "head": {"profile": "pointed", "spread": 1.0}},
               "belfry": {"width": 4.6, "gap": 2.4, "pier": 2.0, "wimperg": {"pitch": 62, "coping": 0.35, "depth": 0.3}},
               "buttress": [[0, 22, 2.4], [22, 55, 1.8], [55, 88, 1.2]], "courses": [22.0, 42.0, 55.0], "gable": 11.0}}
# the octagon nearly the tower's width (the stair turret stands inside it), its spire as wide: 100m of square
# tower, 15m of octagon, a 40m OPENWORK spire (pinnacle.js), the sky through it -- 157m
spire = {"sides": 8, "R": 9.0, "H": 15, "t": 0.9, "drumR": 8.7, "drumH": 3.0, "kok": 1.8, "winW": 3.4, "doorH": 3.2, "glazed": 0,
         "cap": "trigonal", "capRise": 40, "capR": 8.7, "finial": 4.0,
         "open": {"R": 8.7, "rise": 35.4, "rows": 10, "rib": 0.55, "bar": 0.22, "topR": 0.5, "finial": 3.6}}
gothic("cologne", "Cologne Cathedral",
       "COLOGNE CATHEDRAL from the same components as Notre-Dame (the `gothic` generator): the `basilica` nave, 43m to the vault, with wide double aisles, rib-vaulted; flying buttresses down both flanks and round the chevet; the west front under two 16m towers rising to a hundred metres, each crowned by an octagonal stage and an openwork spire to 157m (the `domed-tower`); a spiral stair in each tower up to the terrace the spire stands on.",
       P, spire=spire, fleche=False)
