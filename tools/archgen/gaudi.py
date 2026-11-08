# GAUDI'S PARTS (2026-11-02): the L2 library of Catalan modernisme as Gaudi built it at Park Guell -- run it to write the
# L1 components, import it for the helpers a landmark lays its pieces out with.
#   components/gaudi-cross       the four-armed cross that points to the four quarters and up (Park Guell, Casa Batllo)
#   components/gaudi-mushroom    a stem and a cap: the cupolas and chimneys of the entrance pavilions (an amanita, a stinkhorn)
#   components/hyperboloid-tower a tower drawn in at a waist and flaring again, the cross on it (the administration pavilion)
#   components/gaudi-pavilion    the gingerbread house: rubble walls round an oval-ish plan, a wavy trencadis roof, a mirador
#                                tower with a mushroom on it, mushroom chimneys and (asked for) the hyperboloid tower beside it
# Helpers, all plain numbers for the generator to place:
#   oval(cx, cz, a, b, t0, t1, n)            points on an ellipse's arc
#   bench_profile(h, d)                      the serpentine bench's section (the sweep's profile, outward to the right)
#   leaning_portico(add, name, path, ...)    a portico of rubble columns along a curve, its inner file leaning against a
#                                            battered wall, its outer file upright or leaning in, a walked deck on top
#                                            (the washerwoman's portico, the viaducts)
#   hypostyle(add, outline=..., ...)         the market hall: a Doric grid set into a convex plan, the open fronts' columns
#                                            leaning, cupolas over the bays
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
C = os.path.join(ROOT, "assets/architecture/components/")


def save(p, d):
    open(C + p, "w").write(json.dumps(d, indent=1) + "\n")


def r3(v): return round(v, 3)


# ---------------------------------------------------------------- the cross
def cross():
    parts = {
        "shaft": {"type": "box", "width": "t", "length": "t", "height": "h", "at": [[0, 0, 0, 0]],
                  "_about": "the upright, the arm that points to the sky"},
        "arms": {"type": "box", "width": "2 * arm + t", "length": "t", "height": "t", "at": [[0, "h - arm - t", 0, 0], [0, "h - arm - t", 0, 1.5707963]],
                 "_about": "the four arms, to the four quarters: two bars crossing at the height of the top arm's length under the top"},
        "tips": {"type": "box", "width": "t * 1.25", "length": "t * 1.25", "height": "t * 1.25",
                 "at": [["arm + t / 2", "h - arm - t * 1.125", 0, 0], ["0 - arm - t / 2", "h - arm - t * 1.125", 0, 0],
                        [0, "h - arm - t * 1.125", "arm + t / 2", 0], [0, "h - arm - t * 1.125", "0 - arm - t / 2", 0], [0, "h - t * 0.25", 0, 0]],
                 "_about": "a knob at every arm's end, the cross's ends thickened as Gaudi's are"},
    }
    save("gaudi-cross.json", {"name": "Gaudi's cross", "_about": "GAUDI'S FOUR-ARMED CROSS: an upright and two bars through it at right angles, so that it points to the four quarters and up -- on the administration pavilion's tower at Park Guell (3.8m), on Casa Batllo's turret, on the Bellesguard. Stand it on whatever carries it; h is its height from there.",
                              "params": {"h": 3.8, "arm": 0.9, "t": 0.32, "_h": "its height; arm: each arm's reach from the upright; t: the bars' thickness"},
                              "build": list(parts), "parts": parts})


# ---------------------------------------------------------------- the mushroom
def mushroom():
    parts = {
        "stem": {"type": "loft", "axis": "y", "sides": "sides", "smooth": 3, "at": [[0, 0, 0, 0]],
                 "sections": [{"s": 0, "a": "stemR * foot", "b": "stemR * foot"}, {"s": "stemH * 0.35", "a": "stemR", "b": "stemR"},
                              {"s": "stemH * 0.8", "a": "stemR * 0.92", "b": "stemR * 0.92"}, {"s": "stemH + capH * 0.08", "a": "stemR", "b": "stemR"}],
                 "_about": "the stem, a little swollen at its foot"},
        "cap": {"type": "loft", "axis": "y", "sides": "sides", "smooth": 3, "at": [[0, 0, 0, 0]],
                "sections": [{"s": "stemH", "a": "stemR * 1.05", "b": "stemR * 1.05"},
                             {"s": "stemH + capH * 0.06", "a": "capR * lip", "b": "capR * lip"},
                             {"s": "stemH + capH * 0.22", "a": "capR", "b": "capR"},
                             {"s": "stemH + capH * 0.55", "a": "capR * (0.55 + bell * 0.3)", "b": "capR * (0.55 + bell * 0.3)"},
                             {"s": "stemH + capH * 0.85", "a": "capR * 0.42 * (1 - bell * 0.4)", "b": "capR * 0.42 * (1 - bell * 0.4)"},
                             {"s": "stemH + capH", "a": "capR * 0.04", "b": "capR * 0.04"}],
                "_about": "the cap: its underside a lip out from the stem, its rim, then a dome (bell 1: the amanita's bell; 0: a flatter cap)"},
    }
    save("gaudi-mushroom.json", {"name": "Gaudi mushroom", "_about": "A MUSHROOM, as Gaudi crowned the Park Guell pavilions and turned their chimneys: a stem and a cap, each its own finish -- the porter's lodge's bell-shaped amanita (red, white-spotted) on its mirador, the administration pavilion's cupola, the chimneys on both roofs. Place it on what carries it.",
                                 "params": {"stemR": 0.5, "stemH": 1.2, "capR": 1.1, "capH": 1.4, "lip": 0.92, "bell": 1.0, "foot": 1.15, "sides": 20,
                                            "_stemR": "the stem's radius and height; foot: how much wider it is where it stands",
                                            "_capR": "the cap's radius at its rim, its height over the stem's top; lip: the underside's reach at the rim; bell 1 a bell, 0 a flatter dome"},
                                 "build": list(parts), "parts": parts})


# ---------------------------------------------------------------- the hyperboloid tower
def hyperboloid():
    parts = {
        "shaft": {"type": "loft", "axis": "y", "sides": "sides", "smooth": 4, "at": [[0, 0, 0, 0]],
                  "sections": [{"s": 0, "a": "r0", "b": "r0"}, {"s": "h * waistAt * 0.5", "a": "(r0 + rw) / 2 + (r0 - rw) * 0.1", "b": "(r0 + rw) / 2 + (r0 - rw) * 0.1"},
                               {"s": "h * waistAt", "a": "rw", "b": "rw"}, {"s": "h * (waistAt + (1 - waistAt) * 0.6)", "a": "(rw + r1) / 2", "b": "(rw + r1) / 2"},
                               {"s": "h", "a": "r1", "b": "r1"}],
                  "_about": "the shaft: a hyperboloid of one sheet, drawn in to rw at waistAt of its height, flaring to r1 at the top"},
        "crown": {"type": "loft", "axis": "y", "sides": "sides", "smooth": 3, "at": [[0, "h", 0, 0]],
                  "sections": [{"s": 0, "a": "r1 * 1.08", "b": "r1 * 1.08"}, {"s": "r1 * 0.5", "a": "r1 * 0.85", "b": "r1 * 0.85"}, {"s": "r1 * 1.1", "a": "r1 * 0.35", "b": "r1 * 0.35"}, {"s": "r1 * 1.4", "a": "t", "b": "t"}],
                  "_about": "the domed crown the cross stands on"},
        "cross": {"type": "component", "use": "components/gaudi-cross", "when": {"cross": "yes"}, "params": {"h": "crossH", "arm": "crossH * 0.24", "t": "crossH * 0.085"},
                  "at": [[0, "h + r1 * 1.4 - 0.1", 0, 0]], "_about": "Gaudi's cross on the crown (cross: no leaves it off)"},
    }
    save("hyperboloid-tower.json", {"name": "Hyperboloid tower", "_about": "A TOWER DRAWN IN AT A WAIST: a ruled surface Gaudi built in brick and dressed in trencadis -- the administration pavilion's at Park Guell, white and blue in a chequer, 'the typical cross of four arms' on its domed crown. r0 at the foot, rw at the waist, r1 at the top; the shaft and crown take their own finishes.",
                                    "params": {"h": 14.0, "r0": 1.6, "rw": 0.9, "r1": 1.2, "waistAt": 0.6, "t": 0.12, "sides": 24, "cross": "yes", "crossH": 3.8,
                                               "_h": "the shaft's height from where it stands (the crown and cross go on top); r0, rw, r1: radii at foot, waist (at waistAt of h) and top",
                                               "_cross": "yes: Gaudi's cross on the crown, crossH tall", "_t": "the crown's tip, where the cross stands", "_sides": "facets round"},
                                    "build": list(parts), "parts": parts})


# ---------------------------------------------------------------- the pavilion
def _op(at, width, sill, spring, surround=True):
    """a parabolic opening (a lancet: two centres a half-width apart), its trencadis surround"""
    o = {"at": at, "width": width, "sill": sill, "springing": spring, "head": {"profile": "pointed", "spread": 1.0}}
    return {**o, "surround": {"band": "surBand", "depth": 0.07}} if surround else o


def pavilion():
    # faces of a chamfered rect plan (build.js planPoints): 0 -x, 2 +z (the street), 4 +x, 6 -z; the odd ones the chamfers
    T1, T2 = "(h / storeys)", "(h - h / storeys)"
    win1 = lambda at: _op(at, "winW", f"{T1} * 0.3", f"{T1} * 0.62")
    win2 = lambda at: _op(at, "winW", f"{T2} * 0.25", f"{T2} * 0.58")
    end = [{"h": T1, "openings": [win1(0)]}, {"h": T2, "openings": [win2(0)]}]
    # the merlons of the roof terraces: along the long faces and across the ends, on the eave
    tz = "(l / 2 + eave * 0.2)"; tx = "(w / 2 + eave * 0.2)"
    merl = [[f"(w / 2 - ch) * {k / 2}", "h + eaveH", f"{sg}{tz}", 0] for k in (-2, -1, 0, 1, 2) for sg in ("", "0 - ")] + [[f"{sg}{tx}", "h + eaveH", z, 0] for sg in ("", "0 - ") for z in ("0 - l / 6", "l / 6")]
    lobe = [{"s": "0 - l / 2 + terr", "a": "w * 0.07", "b": "roofH * 0.25", "n": 2.2},
            {"s": "0 - l / 4", "a": "w * 0.11", "b": "roofH * 0.85", "n": 2.2},
            {"s": "l / 4", "a": "w * 0.11", "b": "roofH * 0.85", "n": 2.2},
            {"s": "l / 2 - terr", "a": "w * 0.07", "b": "roofH * 0.25", "n": 2.2}]
    parts = {
        "plinth": {"type": "prism", "plan": {"rect": ["w + 0.3", "l + 0.3"], "chamfer": "ch + 0.15"}, "height": 0.6, "at": [[0, -0.4, 0, 0]],
                   "_about": "a footing a little wider than the walls, sunk into the ground"},
        "walls": {"type": "enclosure", "plan": {"rect": ["w", "l"], "chamfer": "ch"}, "thickness": "t", "height": "h", "glass": True,
                  "tiers": [{"h": T1, "openings": [win1("0 - winGap"), win1("winGap")]}, {"h": T2, "openings": [win2(0)]}],
                  "faces": {"1": [], "3": [], "5": [], "7": [], "0": end, "4": end,
                            "6": [{"h": T1, "openings": [{**_op("doorAt", "doorW", 0, "doorH"), "glass": False}]}, {"h": T2, "openings": [win2(0)]}]},
                  "_about": "the walls of the place's own stone, laid rough, round a plan whose corners are cut so far it reads oval; parabolic windows and door framed in trencadis (the door on the back, face 6, away from the street)"},
        "plaques": {"type": "box", "width": "plaqueW", "length": 0.1, "height": "plaqueW * 0.3", "at": [[0, f"{T1} * 0.42", "l / 2 + 0.03", 0]],
                    "_about": "the plaque with 'Park Guell' in trencadis on the street face, between the windows"},
        "floors": {"type": "prism", "plan": {"rect": ["w - 2 * t", "l - 2 * t"], "chamfer": "max(0.1, ch - t * 0.6)",
                                             "well": {"rect": ["stairN * 0.25 + 0.15", "stairW + 0.05"], "at": ["stairX - stairN * 0.125 + 0.075", "0 - (l / 2 - t) + stairW / 2 + 0.1"]}},
                   "height": 0.25, "railing": False, "at": [[0, f"{T1} - 0.25", 0, 0]], "_about": "the upper floor, its stairwell along the back wall"},
        "stair": {"type": "flight", "width": "stairW", "run": 0.25, "steps": "stairN", "base": 0.2, "top": T1, "landing": 0, "railing": False,
                  "at": [["stairX", 0, "0 - (l / 2 - t)", 3.14159]],
                  "_about": "the stair up to the upper floor, along the back wall beside the door (rising toward -x from stairX)"},
        "ceiling": {"type": "prism", "plan": {"rect": ["w - 2 * t + 0.02", "l - 2 * t + 0.02"], "chamfer": "max(0.1, ch - t * 0.6)"}, "height": 0.3,
                    "at": [[0, "h - 0.3", 0, 0]], "_about": "the vault over the top floor, the roof's bed"},
        "cornice": {"type": "prism", "plan": {"rect": ["w + 2 * eave", "l + 2 * eave"], "chamfer": "ch + eave"}, "height": "eaveH", "at": [[0, "h", 0, 0]],
                    "_about": "the eave: a thick rolled lip all round, its top the terraces round the roof, dressed in trencadis"},
        "merlons": {"type": "prism", "plan": {"sides": 8, "radius": "merlonR"}, "height": "merlonR * 2.6", "at": merl,
                    "_about": "the almenas: rounded merlons on the eave round the attic terraces, white trencadis"},
        "roof": {"type": "loft", "axis": "x", "sides": 16, "smooth": 3, "half": True, "shell": True, "at": [[0, "h + eaveH * 0.5", 0, 0]],
                 "sections": [{"s": "0 - w / 2 + terr * 0.5", "a": "l / 2 - ch * 0.6", "b": "roofH * 0.3", "n": 2.2},
                              {"s": "0 - w / 2 + ch * 0.5", "a": "l / 2 - terr", "b": "roofH * (1 - wave)", "n": 2.2},
                              {"s": "0 - w / 4", "a": "l / 2 - terr", "b": "roofH", "n": 2.2},
                              {"s": 0, "a": "l / 2 - terr", "b": "roofH * (1 - wave)", "n": 2.2},
                              {"s": "w / 4", "a": "l / 2 - terr", "b": "roofH", "n": 2.2},
                              {"s": "w / 2 - ch * 0.5", "a": "l / 2 - terr", "b": "roofH * (1 - wave)", "n": 2.2},
                              {"s": "w / 2 - terr * 0.5", "a": "l / 2 - ch * 0.6", "b": "roofH * 0.3", "n": 2.2}],
                 "_about": "the roof: no plane in it -- the hyperbolic vaults of the attic as a mound rising and falling along the house in lobes (wave: how deep the troughs are), the 'sugar icing' of the gingerbread house, in trencadis; terr in from the eave, the terrace"},
        "roof lobes": {"type": "loft", "axis": "z", "sides": 12, "smooth": 3, "half": True, "shell": True, "at": [["0 - w / 4", "h + eaveH * 0.5", 0, 0], ["w / 4", "h + eaveH * 0.5", 0, 0]],
                       "sections": lobe, "_about": "a lobe across the roof over each crest, so it swells both ways like a mushroom's gills"},
        "tower": {"type": "prism", "plan": {"sides": 10, "radius": "towerR"}, "height": "towerH - lookH - (h + eaveH)", "at": [["towerX", "h + eaveH", "towerZ", 0]],
                  "batter": {"out": "towerR * 0.18", "power": 1.6},
                  "_about": "the tower out of the roof, of rubble, swelling a little toward its foot"},
        "lookout": {"type": "enclosure", "plan": {"sides": 10, "radius": "towerR * 0.92"}, "thickness": 0.3, "height": "lookH", "glass": False,
                    "openings": [_op(0, "towerR * 0.42", "lookH * 0.3", "lookH * 0.58", surround=False)],
                    "at": [["towerX", "towerH - lookH", "towerZ", 0]], "_about": "the mirador: the tower's top storey opened all round"},
        "lookout floor": {"type": "prism", "plan": {"sides": 10, "radius": "towerR * 0.92"}, "height": 0.2, "at": [["towerX", "towerH - lookH - 0.2", "towerZ", 0]]},
        "cupola": {"type": "component", "use": "components/gaudi-mushroom", "params": {"stemR": "towerR * 0.8", "stemH": "towerR * 0.25", "capR": "capR", "capH": "capH", "bell": "bell", "lip": 0.9, "foot": 1.0},
                   "at": [["towerX", "towerH", "towerZ", 0]], "_about": "the mushroom on the mirador -- the porter's lodge's bell-shaped amanita"},
        "chimneys": {"type": "component", "use": "components/gaudi-mushroom", "when": {"chimneys": "yes"},
                     "params": {"stemR": "chimR", "stemH": "chimH", "capR": "chimR * 1.9", "capH": "chimR * 1.6", "bell": 0.4, "sides": 12},
                     "at": [["chimX", "chimY", "0 - l * 0.1", 0], ["0 - chimX", "chimY", "l * 0.1", 0]],
                     "_about": "two chimneys, little mushrooms of their own, standing on the roof's crests (chimneys: no leaves them off)"},
        "spire": {"type": "component", "use": "components/hyperboloid-tower", "when": {"spire": "yes"},
                  "params": {"h": "spireH", "r0": "spireR", "rw": "spireR * 0.58", "r1": "spireR * 0.72", "waistAt": 0.62, "crossH": "crossH"},
                  "at": [["spireX", "spireY", "spireZ", 0]], "_about": "the hyperboloid tower at one end, standing out of the wall (spire: yes), Gaudi's cross on it"},
    }
    save("gaudi-pavilion.json", {"name": "Gaudi pavilion", "_about": "THE PARK GUELL PAVILION, a gingerbread house of 1901: low walls of the hill's own rubble round a plan whose corners are cut so far it reads as an oval, parabolic windows and door framed in trencadis, a 'Park Guell' plaque, a thick eave carrying the attic's terraces behind rounded merlons, a tall roof of lobes rising and falling both ways dressed in trencadis, a rubble tower out of it with a mirador and a mushroom on top, mushroom chimneys on the crests -- and, asked for, a hyperboloid tower at one end carrying Gaudi's cross. The door is on the back face (away from the street, +z the front).",
                                  "params": {"w": 14.8, "l": 7.66, "ch": 2.2, "t": 0.6, "h": 7.0, "storeys": 2, "winW": 1.0, "winGap": 2.6, "surBand": 0.2,
                                             "doorW": 1.4, "doorH": 2.0, "doorAt": 2.0, "plaqueW": 2.4, "stairN": 15, "stairX": 2.8, "stairW": 1.5,
                                             "eave": 0.35, "eaveH": 0.55, "terr": 0.8, "merlonR": 0.24, "roofH": 5.5, "wave": 0.4,
                                             "towerR": 1.8, "towerX": 2.0, "towerZ": 0.4, "towerH": 17.5, "lookH": 2.4, "capR": 2.3, "capH": 3.4, "bell": 1.0,
                                             "chimneys": "yes", "chimR": 0.32, "chimH": 2.2, "chimX": "w / 4", "chimY": "h + eaveH * 0.5 + roofH * 0.9",
                                             "spire": "no", "spireX": 5.5, "spireY": 0, "spireZ": 0, "spireH": 18.0, "spireR": 1.6, "crossH": 3.8,
                                             "_w": "the plan: w along the street (x), l deep, ch the corners cut; t the walls, h to the eave in `storeys` floors (the attic is in the roof)",
                                             "_winW": "the windows: winW wide, the street face's lower pair winGap either side of the middle; surBand their trencadis frames",
                                             "_doorW": "the door on the back face: doorW wide, springing at doorH, doorAt along the face (which runs toward -x: 2 puts it at x -2, clear of the stair); plaqueW the street plaque",
                                             "_stairN": "the stair inside: stairN steps on 25 cm treads rising from the ground floor's +0.2 to the upper floor, along the back wall toward -x from x = stairX, stairW wide (1.5: the walker, 0.3 m round, clears its sides on any grid)",
                                             "_eave": "the eave: eave out from the wall, eaveH thick; terr the terrace between it and the roof; merlonR the merlons on it",
                                             "_roofH": "the roof's crest over the eave; wave: how deep its troughs fall (0 a plain mound)",
                                             "_towerH": "the tower's top (from the ground) where the mushroom sits; lookH its mirador; capR/capH/bell the mushroom",
                                             "_chimneys": "yes: two mushroom chimneys chimR wide and chimH tall, at x = +-chimX, their feet at chimY (on the roof's crests)",
                                             "_spire": "yes: the hyperboloid tower at [spireX, spireY, spireZ], spireH its shaft, spireR its foot's radius, crossH its cross"},
                                  "build": list(parts), "parts": parts})


# ---------------------------------------------------------------- helpers for a landmark
def oval(cx, cz, a, b, t0, t1, n):
    """n+1 points [x, z] on the ellipse (a along x, b along z) from angle t0 to t1 (0 = +x, pi/2 = +z)"""
    return [[r3(cx + a * math.cos(t0 + (t1 - t0) * k / n)), r3(cz + b * math.sin(t0 + (t1 - t0) * k / n))] for k in range(n + 1)]


def bench_profile(h=1.0, d=0.8):
    """the serpentine bench's section [u, v], u outward (to the sweep's right): the seat inside, the parapet-back outside,
    rolling over at its top; h the back's top, d the whole depth"""
    s = d / 0.8
    return [[r3(-0.38 * s), 0], [r3(0.42 * s), 0], [r3(0.44 * s), r3(0.62 * h)], [r3(0.38 * s), r3(0.9 * h)], [r3(0.26 * s), h], [r3(0.14 * s), r3(0.93 * h)],
            [r3(0.1 * s), r3(0.46 * h)], [r3(-0.32 * s), r3(0.43 * h)], [r3(-0.38 * s), r3(0.36 * h)]]


def resample(path, step):
    """a polyline [[x, y, z]] cut into equal steps (in plan) of about `step`: [[x, y, z, heading]]"""
    L = [0]
    for i in range(1, len(path)):
        L.append(L[-1] + math.hypot(path[i][0] - path[i - 1][0], path[i][2] - path[i - 1][2]))
    n = max(1, round(L[-1] / step)); out = []
    for k in range(n + 1):
        s = L[-1] * k / n; i = 1
        while i < len(L) - 1 and L[i] < s: i += 1
        f = (s - L[i - 1]) / ((L[i] - L[i - 1]) or 1)
        p = [path[i - 1][c] + (path[i][c] - path[i - 1][c]) * f for c in range(3)]
        out.append(p + [math.atan2(path[i][0] - path[i - 1][0], path[i][2] - path[i - 1][2])])
    return out


def leaning_portico(add, name, path, H, width, step=3.2, lean=12, colR=0.42, deckT=0.6, bank=6.0, ground=12.0, middle=False, outer_lean=0.0,
                    about=None):
    """THE WASHERWOMAN'S PORTICO / A VIADUCT: along `path` ([x, y, z], y its floor, climbing as the hill does; the wall on
    its LEFT, the open side on its right): a battered rubble wall `H` high holding back an earth `bank` (metres wide) behind
    it, a file of columns on the open side (upright, or leaning `outer_lean` deg in toward the wall: a viaduct's outer
    file, its thrust line a parabola), a file leaning in (lean deg) toward the wall between, and (`middle`) a third file
    upright between those -- the upper viaducts' three rows; a deck `width` wide over all, walked, a parapet; under the
    floor its own terrace `ground` deep. Sweeps and columns only. `about`: what it is, for the parts' notes."""
    pts = resample(path, step); P = [[r3(x), r3(y), r3(z)] for x, y, z in path]
    sw = lambda prof, **k: {"type": "sweep", "path": P, "step": 0.6, "profile": [[r3(u), r3(v)] for u, v in prof], **k}
    add(f"{name} ground", sw([[-bank - 0.6, -ground], [width + 0.3, -ground], [width + 0.3, 0], [-0.6, 0], [-bank - 0.6, 0]], walked=True,
                             _about=f"{about or name}: the terrace it stands on, faced in the hill's rubble where the slope falls away"))
    add(f"{name} wall", sw([[-0.6, 0], [0.9, 0], [0.25, H], [-0.6, H]], _about="the retaining wall, its open face battered back as it rises, rubble"))
    add(f"{name} bank", sw([[-bank - 0.6, 0], [-0.6, 0], [-0.6, H + 0.4], [-bank * 0.5, H + 1.2], [-bank - 0.6, H + 2.0]],
                           _about="the hillside the wall holds back"))
    outer, inner, mid = [], [], []
    ho = H - deckT + 0.15; so = ho * math.sin(math.radians(outer_lean))
    for x, y, z, hd in pts[1:-1]:
        rx, rz = -math.cos(hd), math.sin(hd)     # right of travel, (-tz, tx) with t = (sin hd, cos hd)
        uo = width - colR - 0.2 + so             # (a leaning outer column's foot set out so its head stays under the deck's edge)
        y -= 0.1                                 # (set into the floor a little: the path's curve and the columns' points differ on a bend)
        outer.append([r3(x + rx * uo), r3(y), r3(z + rz * uo), r3(hd)])
        inner.append([r3(x + rx * (width * 0.45)), r3(y), r3(z + rz * (width * 0.45)), r3(hd)])
        if middle: mid.append([r3(x + rx * (width * 0.72)), r3(y), r3(z + rz * (width * 0.72)), r3(hd)])
    add(f"{name} outer columns", {"type": "column", "radius": colR, "height": r3(ho / math.cos(math.radians(outer_lean))), "sides": 9, "at": outer,
                                  **({"lean": {"deg": outer_lean, "toward": [1, 0], "each": True, "local": True}} if outer_lean else {}),
                                  "_about": "the outer file, rough-hewn, swelling at the foot like palms" + (": leaning in, so the thrust runs down it to the ground" if outer_lean else ": upright")})
    if middle:
        add(f"{name} middle columns", {"type": "column", "radius": colR * 0.9, "height": r3(ho), "sides": 9, "at": mid,
                                       "_about": "the middle file, upright under the deck's crown"})
    add(f"{name} inner columns", {"type": "column", "radius": colR * 0.9, "height": r3(ho / math.cos(math.radians(lean))), "sides": 9, "at": inner,
                                  "lean": {"deg": lean, "toward": [1, 0], "each": True, "local": True},
                                  "_about": "the inner file, leaning back toward the wall: Gaudi's columns take the push of the earth on their slant"})
    add(f"{name} deck", sw([[-0.6, H - deckT], [width, H - deckT], [width, H], [-0.6, H]], walked=True, _about="the path over the portico"))
    add(f"{name} parapet", sw([[width - 0.45, H], [width, H], [width - 0.05, H + 0.75], [width - 0.4, H + 0.75]], _about="a low parapet along the open edge"))
    return pts


def _inside(poly, x, z, m):
    """(x, z) at least m inside every edge of the convex outline `poly` (either winding)"""
    n = len(poly); area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sg = 1 if area < 0 else -1
    for i in range(n):
        (ax, az), (bx, bz) = poly[i], poly[(i + 1) % n]; L = math.hypot(bx - ax, bz - az)
        if sg * ((x - ax) * (bz - az) - (z - az) * (bx - ax)) / L < m: return False
    return True


def _inward(poly, i):
    """edge i's inward unit normal [nx, nz]"""
    n = len(poly); area = sum(poly[k][0] * poly[(k + 1) % n][1] - poly[(k + 1) % n][0] * poly[k][1] for k in range(n))
    (ax, az), (bx, bz) = poly[i], poly[(i + 1) % n]; L = math.hypot(bx - ax, bz - az); tx, tz = (bx - ax) / L, (bz - az) / L
    return [-tz, tx] if area > 0 else [tz, -tx]


def hypostyle(add, *, outline, x0, z0, dx, dz, margin, floor, colH, colR, omit=(), rosettes=(), open_edges=None, lean=5.0, rise=0.7,
              vaultT=0.15, medallions=14):
    """A GAUDI HYPOSTYLE (Park Guell's market hall, 2026-11-04 as built: a square grid set into the plan it has). Doric
    columns on a grid x0 + k dx (files k), z0 - j dz (rows j >= 0) wherever a column stands `margin` inside every edge of
    the convex `outline` [[x, z]] (the hall's own plan); `omit` [(k, j)] left out and nothing put there (the stair's
    head), `rosettes` [(k, j)] left out for a ceiling rosette each; `open_edges` {edge index: name} the outline's edges
    the hall is open along -- every column within a grid step of one leans `lean` deg, feet out across it, its capital
    on the grid. Over every bay with all four corners standing (a column or a rosette) a shallow cupola (rise), its crown
    the ceiling's level; elsewhere the ceiling is flat at the crowns (the slab the caller lays). Returns the levels and
    the grid: {"spring", "crown", "pos": {(k, j): (x, z)}, "count"}."""
    spring = floor + colH; crown = spring + rise
    pos = {}
    for j in range(0, 40):
        for k in range(-20, 21):
            x, z = x0 + k * dx, z0 - j * dz
            if (k, j) not in omit and _inside(outline, x, z, margin): pos[(k, j)] = (r3(x), r3(z))
    groups = {"columns": []}; toward = {"columns": None}
    off = colH * math.sin(math.radians(lean)); n = len(outline)
    for kj, (x, z) in sorted(pos.items(), key=lambda q: (q[0][1], q[0][0])):
        if kj in rosettes: continue
        g = "columns"
        for e, nm in (open_edges or {}).items():
            (ax, az), (bx, bz) = outline[e], outline[(e + 1) % n]; L = math.hypot(bx - ax, bz - az)
            d = abs((x - ax) * (bz - az) - (z - az) * (bx - ax)) / L
            if d < margin + min(dx, dz) * 0.95: g = f"{nm} columns"; toward[g] = _inward(outline, e); break
        nx, nz = toward.get(g) or (0, 0)
        groups.setdefault(g, []).append([r3(x - nx * off), r3(floor), r3(z - nz * off), 0])
    col = {"type": "colonnade", "order": "doric", "count": 1, "spacing": 1, "columnR": colR, "height": colH, "sides": 20}
    for g, at in groups.items():
        add(g, {**col, "at": at, **({"lean": {"deg": lean, "toward": [r3(v) for v in toward[g]], "each": True}} if toward[g] else {}),
                "_about": "the hypostyle's Doric columns, 6.16 m, the plaza's rain running down inside them to a cistern" if g == "columns"
                          else f"the {g.split(' columns')[0]} front: the outer columns inclined, feet out, along the line of the vaults' push"})
    full = set(pos)
    bays = [[r3(x0 + (k + 0.5) * dx), r3(spring), r3(z0 - (j + 0.5) * dz), 0] for (k, j) in sorted(full)
            if {(k + 1, j), (k, j + 1), (k + 1, j + 1)} <= full]
    add("vaults", {"type": "dome", "sides": 4, "turn": 0, "radius": r3(dz / math.sqrt(2)), "stretch": [r3(dx / dz), 1, 1], "thickness": vaultT,
                   "head": {"profile": "segmental", "rise": rise, "seg": 6}, "at": bays,
                   "_about": "the ceiling: a shallow cupola over every bay, column to column, in white trencadis"})
    add("rosettes", {"type": "column", "radius": 1.5, "height": 0.1, "sides": 20, "at": [[pos[kj][0], r3(spring - 0.1), pos[kj][1], 0] for kj in sorted(rosettes)],
                     "_about": "Jujol's four rosettes, 3 m across, where four columns were left out: suns of many points, the seasons"})
    step = max(1, len(bays) // medallions)
    add("medallions in the vaults", {"type": "column", "radius": 0.5, "height": 0.12, "sides": 16, "at": [[b[0], r3(crown - vaultT - 0.08), b[2], 0] for b in bays[step // 2::step][:medallions]],
                                     "_about": "smaller medallions, 1 m across, at the vaults' crowns: the moon's cycle"})
    return {"spring": spring, "crown": crown, "pos": pos, "count": sum(len(v) for v in groups.values()), "groups": list(groups)}


if __name__ == "__main__":
    cross(); mushroom(); hyperboloid(); pavilion()
    print("gaudi: 4 components written")
