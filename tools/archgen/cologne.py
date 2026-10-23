# COLOGNE CATHEDRAL (1248-1880): the same Gothic cathedral as Notre-Dame (notre_dame.py `gothic`), with Cologne's
# numbers -- a taller, wider nave with double aisles, 14.4m towers rising over the aisles to a hundred metres,
# and on each an octagonal stage and an openwork spire to 157m; the stair in the tower climbs to the terrace
# the spire stands on, as the real one does.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notre_dame import gothic, NOTRE_DAME
P = {**NOTRE_DAME, "bays": 11, "bayLen": 7.6, "naveW": 14.0, "aisleW": 12.0, "pierT": 1.6, "aisleT": 1.6,
     "spring": 9.0, "arcadeH": 21.0, "clearH": 31.0, "aisleRise": 4.0, "frontH": 55.0, "towerW": 14.4, "towerH": 45.0, "roofPitch": 55,
     "ridge": "(naveW / 2 + pierT + 0.3) * 1.4281", "towerBays": 3}
# the octagon nearly the tower's width (the stair turret stands inside it), its spire as wide: 100m of square
# tower, 15m of octagon, a 40m spire -- 157m
spire = {"sides": 8, "R": 6.8, "H": 15, "t": 0.7, "cap": "trigonal", "capRise": 40, "capR": 6.9, "drumR": 6.4, "drumH": 2.4,
         "kok": 1.8, "finial": 4.0, "winW": 2.6, "doorH": 3.2}
gothic("cologne", "Cologne Cathedral",
       "COLOGNE CATHEDRAL from the same components as Notre-Dame (the `gothic` generator): the `basilica` nave, 43m to the vault, with wide double aisles, rib-vaulted; flying buttresses down both flanks and round the chevet; the west front under two 16m towers rising to a hundred metres, each crowned by an octagonal stage and an openwork spire to 157m (the `domed-tower`); a spiral stair in each tower up to the terrace the spire stands on.",
       P, spire=spire, fleche=False)
