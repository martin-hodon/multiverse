"""THE ACROPOLIS OF ATHENS (2026-10-30): its buildings of the fifth century BC, each a building of its own -- the
Erechtheion with its maidens, the Propylaia, the temple of Athena Nike (the temple generator's, amphiprostyle) -- and the
site: the rock, its circuit walls, the stair up to the Propylaia, and on the summit the Parthenon (temples.py), the
bronze Athena Promachos, the old temple's foundations and the great altar, every building PAINTED as it was (each its
own finish, the site's using them: arch/finish.js withUses).
Every frame here is a temple's: +z its east, +x its north, the ground (or its floor) at 0."""
import math
from temples import temple, save, common
from statuary import statue, pedestal, capped, FACE_E, FACE_W, FACE_PX, FACE_NX

HALF_PI = 1.5707963


def acroteria(name, y, z_east, z_west, h, x=0, yaw=0):
    """the floral acroterion on each apex of a gable, standing on the raking cornice's meeting"""
    return {"type": "item", "item": "items/ornaments/acroterion", "params": {"h": h}, "solid": False,
            "at": [[x, y, z_east, yaw], [x, y, z_west, yaw]], "_about": f"the floral acroteria on the apexes of the {name}"}


def door(at, w, h):
    return {"at": at, "width": w, "sill": 0, "springing": h, "head": {"profile": "flat"}, "glass": False}


def window(at, w, sill, h):
    return {"at": at, "width": w, "sill": sill, "springing": sill + h, "head": {"profile": "flat"}, "glass": False}


# ---- the Erechtheion -----------------------------------------------------------------------------------------------
def erechtheion():
    """THE ERECHTHEION (421-406 BC): the main block 11.63 x 22.76m, its east front a porch of six Ionic columns, its
    west wall with four engaged columns and windows between them, the NORTH PORCH at its west end (six columns, its own
    gable and the great door under it) and on the south the PORCH OF THE MAIDENS -- six caryatids on a high podium
    carrying its flat roof on their heads, PAINTED (statues.js "painted"); inside, the olivewood Athena Polias. One
    floor throughout (the north porch stood three metres lower on the falling rock: here its columns are shorter, so
    its roof stays under the main one's eaves)."""
    parts = {}; build = []
    def add(n, d): parts[n] = d; build.append(n)
    P = {"detail": 4, "W": 11.63, "L": 22.76, "base": 0.6, "D": 0.69, "colH": 6.58, "entH": 1.55, "cornH": 0.45, "cornOut": 0.35,
         "wallT": 0.6, "porchZ": 13.4, "npD": 0.76, "npH": 5.2, "npX": 12.2, "npZ": -7.2, "npSpan": 3.1,
         "cpX": -7.45, "cpZ": -7.7, "cpH": 1.8, "kore": 1.15, "_kore": "a maiden's scale (statues.js: 1.78m a unit)"}
    W, L, base, D, colH, entH, cornH, cornOut = P["W"], P["L"], P["base"], P["D"], P["colH"], P["entH"], P["cornH"], P["cornOut"]
    top = colH + entH + cornH                                  # the walls' top over the floor: the roof's foot
    add("crepidoma", {"type": "crepidoma", "width": W + 1.0, "length": "porchZ + D + 13.0", "steps": 3, "stepH": 0.2, "stepOut": 0.3,
                      "at": [[0, 0, "(porchZ + D - 13.0) / 2 + 0.5", 0]], "_about": "the stepped platform under the main block and its east porch"})
    # the walls: doors east (into Athena's cella) and north (under the porch), a small one south to the maidens' stair,
    # windows high in the west wall between its engaged columns; the entablature round them as courses -- the moulding
    # over the architrave, the frieze of dark Eleusinian stone above it (the finish's), the cornice crowning it
    add("cella", {"type": "enclosure", "plan": {"rect": ["W", "L"]}, "thickness": "wallT", "height": top, "glass": False,
                  "faces": {"0": [door(0, 2.0, 4.6)], "1": [door("0 - npZ", 2.4, 4.9)], "2": [window(-2.6, 0.9, 4.0, 1.7), window(0, 0.9, 4.0, 1.7), window(2.6, 0.9, 4.0, 1.7)],
                            "3": [door("cpZ + 1.3", 0.9, 2.0)]},
                  "courses": [{"y": 0, "h": 0.35, "out": 0.08, "profile": "band"}, {"y": colH + 0.62, "h": 0.12, "out": 0.06, "profile": "band"},
                              {"y": colH + entH, "h": cornH, "out": cornOut, "profile": "cornice"}],
                  "at": [[0, "base", 0, 0]], "_about": "the main block's walls, the entablature run round them as mouldings"})
    add("cross wall", {"type": "wall", "width": "W - 2 * wallT", "height": colH, "thickness": 0.5, "openings": [door("(W - 2 * wallT) / 2", 1.6, 3.6)],
                       "at": [[0, "base", 1.2, 0]], "_about": "the wall between Athena's cella in the east and the rooms of Erechtheus and Poseidon in the west"})
    # the east porch: six Ionic columns before the east wall, the entablature returning to it at the sides
    add("east porch", {"type": "colonnade", "order": "ionic", "count": 6, "spacing": "(W - D * 1.2) / 5", "columnR": "D / 2", "height": colH,
                       "entablature": {"h": entH, "depth": "D * 1.1", "cornice": {"h": cornH, "out": cornOut}}, "at": [[0, "base", "porchZ", 0]],
                       "_about": "the six Ionic columns of the east porch"})
    add("east porch returns", {"type": "box", "width": "D * 1.1", "length": "porchZ - L / 2", "height": entH + cornH,
                               "at": [["W / 2 - D * 0.55", f"base + {colH}", "(porchZ + L / 2) / 2", 0], ["0 - W / 2 + D * 0.55", f"base + {colH}", "(porchZ + L / 2) / 2", 0]],
                               "_about": "the entablature's returns from the porch to the walls"})
    add("east porch ceiling", {"type": "coffered-ceiling", "width": "W - D * 2.2", "length": "porchZ - L / 2", "thickness": entH + cornH, "nx": 5, "nz": 1,
                               "depth": 0.15, "steps": 1, "at": [[0, f"base + {colH}", "(porchZ + L / 2) / 2", 0]], "_about": "the porch's coffered ceiling"})
    # the west front: four Ionic columns half in the wall, the windows between them
    add("west columns", {"type": "colonnade", "order": "ionic", "count": 4, "spacing": "(W - 1.6) / 3", "columnR": 0.3, "height": colH,
                         "at": [[0, "base", "0 - L / 2", 0]], "_about": "the four engaged Ionic columns of the west wall"})
    ridge = round((W + 2 * cornOut) / 2 * math.tan(math.radians(13)), 3)
    roof_z0, roof_z1 = -L / 2 - cornOut, P["porchZ"] + D * 0.55 + cornOut
    add("roof", {"type": "roof", "form": "gable", "width": W + 2 * cornOut, "length": round(roof_z1 - roof_z0, 3), "pitch": 13, "rake": {"h": cornH, "out": 0.15},
                 "at": [[0, f"base + {top}", round((roof_z0 + roof_z1) / 2, 3), 0]], "_about": "the main gable, its pediments east and west"})
    add("acroteria", acroteria("main gable", f"base + {top + ridge}", round(roof_z1 - 0.2, 3), round(roof_z0 + 0.2, 3), "D * 1.6"))
    # THE NORTH PORCH: four columns across its front and one behind each corner, its own gable running north from the
    # wall, its ceiling coffered; the great north door behind
    npH, npD, npX, npZ, sp = P["npH"], P["npD"], P["npX"], P["npZ"], P["npSpan"]
    add("north porch", {"type": "colonnade", "order": "ionic", "count": 4, "spacing": "npSpan", "columnR": "npD / 2", "height": "npH",
                        "entablature": {"h": entH, "depth": "npD * 1.1", "cornice": {"h": cornH, "out": cornOut}}, "at": [["npX", "base", "npZ", HALF_PI]],
                        "_about": "the north porch's front: four Ionic columns"})
    add("north porch flanks", {"type": "colonnade", "order": "ionic", "count": 2, "spacing": "npSpan * 3", "columnR": "npD / 2", "height": "npH",
                               "at": [["npX - npSpan", "base", "npZ", HALF_PI]], "_about": "a column behind each front corner"})
    np_len = npX - W / 2 + npD * 0.55
    add("north porch sides", {"type": "box", "width": round(np_len, 3), "length": "npD * 1.1", "height": entH + cornH,
                              "at": [[round(W / 2 + np_len / 2, 3), f"base + {npH}", f"npZ + {1.5 * sp}", 0], [round(W / 2 + np_len / 2, 3), f"base + {npH}", f"npZ - {1.5 * sp}", 0]],
                              "_about": "the porch's side entablatures back to the wall"})
    add("north porch ceiling", {"type": "coffered-ceiling", "width": round(np_len - npD * 1.1, 3), "length": f"npSpan * 3 - npD * 1.1", "thickness": entH + cornH, "nx": 4, "nz": 5,
                                "depth": 0.2, "steps": 1, "at": [[round(W / 2 + (np_len - npD * 1.1) / 2, 3), f"base + {npH}", "npZ", 0]], "_about": "its coffered ceiling"})
    np_w = 3 * sp + npD * 1.1 + 2 * cornOut
    np_ridge = round(np_w / 2 * math.tan(math.radians(13)), 3)
    np_x1 = npX + npD * 0.55 + cornOut
    add("north porch roof", {"type": "roof", "form": "gable", "width": round(np_w, 3), "length": round(np_x1 - W / 2 + 0.3, 3), "pitch": 13, "rake": {"h": cornH, "out": 0.15},
                             "at": [[round((np_x1 + W / 2 - 0.3) / 2, 3), f"base + {npH + entH + cornH}", "npZ", HALF_PI]], "_about": "the north porch's gable, its pediment to the north"})
    add("north porch acroterion", {"type": "item", "item": "items/ornaments/acroterion", "params": {"h": "npD * 1.4"}, "solid": False,
                                   "at": [[round(np_x1 - 0.2, 3), f"base + {round(npH + entH + cornH + np_ridge, 3)}", "npZ", HALF_PI]], "_about": "the floral acroterion on its apex"})
    # THE PORCH OF THE MAIDENS: the podium, six korai -- four in front, one behind each end -- the capitals on their
    # heads (echinus and abacus), the entablature and the flat roof over them
    cpX, cpZ, cpH, kore = P["cpX"], P["cpZ"], P["cpH"], P["kore"]
    add("maidens' podium", {"type": "box", "width": 3.6, "length": 5.2, "height": "cpH", "at": [["cpX", "base", "cpZ", 0]],
                            "_about": "the high podium the maidens stand on"})
    spots = [(cpX - 1.3, cpZ + dz) for dz in (-1.95, -0.65, 0.65, 1.95)] + [(cpX + 0.55, cpZ - 1.95), (cpX + 0.55, cpZ + 1.95)]
    head = cpH + 1.78 * kore
    korai = {}
    for i, (x, z) in enumerate(spots):
        # (each her own seed, her weight on the leg away from the middle: the three on the east mirrored, as they stand)
        korai[f"kore {i}"] = statue((x, base + cpH, z), kind="woman", style="greek", stone="painted", scale=kore,
                                    pose="contrapposto left" if z > cpZ else "contrapposto", seed=40 + i, face=FACE_NX)
    add("maidens' capitals", {"type": "column", "radius": 0.21, "height": 0.16, "taper": 1.5, "sides": 12,
                              "at": [[round(x, 3), f"base + {round(head - 0.04, 3)}", round(z, 3), 0] for x, z in spots], "_about": "the echinus on each maiden's head"})
    add("maidens' abaci", {"type": "box", "width": 0.62, "length": 0.62, "height": 0.1,
                           "at": [[round(x, 3), f"base + {round(head + 0.12, 3)}", round(z, 3), 0] for x, z in spots], "_about": "the abacus over it"})
    add("maidens' entablature", {"type": "box", "width": 3.3, "length": 4.9, "height": 0.62, "at": [["cpX - 0.2", f"base + {round(head + 0.22, 3)}", "cpZ", 0]],
                                 "_about": "the architrave with its rosettes and the dentils over the maidens"})
    add("maidens' roof", {"type": "box", "width": 3.7, "length": 5.3, "height": 0.3, "at": [["cpX - 0.25", f"base + {round(head + 0.84, 3)}", "cpZ", 0]],
                          "_about": "the porch's flat marble roof"})
    for k, v in korai.items(): add(k, v)
    # ATHENA POLIAS: the old olivewood image in the east cella, painted and dressed, on her base before the door
    add("Polias base", pedestal((0, base, 7.5), 1.4, 1.2, 0.6, "the base of the Athena Polias"))
    add("Athena Polias", statue((0, base + 0.6, 7.5), kind="woman", style="greek", stone="painted", scale=1.2, pose="offering",
                                hold={"R": "items/food/pomegranate"}, wear=["clothes/crested-helmet"], seed=21, face=FACE_E))
    save("erechtheion.json", {"name": "Erechtheion", "era": "-421--406", "region": "Greece", "_about": erechtheion.__doc__.strip(),
                              "params": P, "build": build, "parts": capped(parts)})


# ---- the Propylaia --------------------------------------------------------------------------------------------------
def propylaia():
    """THE PROPYLAIA (437-432 BC, Mnesikles), the gateway: the central building's west and east fronts six Doric columns
    each under their triglyph friezes and pediments, the deep west hall between them, its coffered ceiling -- blue, with
    gold stars -- carried on two rows of tall Ionic columns either side of the road, the gate wall with its five doors
    (the middle one for the procession, the rest smaller the further out); the PINAKOTHEKE, the picture gallery, in the
    north-west wing behind its portico of three columns facing the approach, and its shallower twin in the south-west.
    Its origin the middle of the gate wall, +z east (into the sanctuary)."""
    parts = {}; build = []
    def add(n, d): parts[n] = d; build.append(n)
    P = {"detail": 4, "D": 1.56, "colH": 8.81, "entH": 2.05, "cornH": 0.55, "cornOut": 0.45, "base": 0.9, "W": 18.2, "wallT": 1.0,
         "westZ": -15.5, "eastZ": 7.5, "wingX": 11.5, "wingZ": -22.5, "wD": 1.0, "wH": 5.85}
    D, colH, entH, cornH, cornOut, base, W = P["D"], P["colH"], P["entH"], P["cornH"], P["cornOut"], P["base"], P["W"]
    westZ, eastZ = P["westZ"], P["eastZ"]
    top = colH + entH + cornH
    sp = round((W - D * 1.3) / 5, 3)
    add("crepidoma", {"type": "crepidoma", "width": W + 2.0, "length": round(eastZ - westZ + D + 2.0, 3), "steps": 3, "stepH": 0.3, "stepOut": 0.4,
                      "at": [[0, 0, round((eastZ + westZ) / 2, 3), 0]], "_about": "the stepped platform of the central building"})
    tri = {"triglyphs": {"w": "D * 0.55", "d": 0.14}}
    for nm, z in (("west portico", westZ), ("east portico", eastZ)):
        add(nm, {"type": "colonnade", "order": "doric", "count": 6, "spacing": sp, "columnR": "D / 2", "height": "colH",
                 "entablature": {"h": "entH", "depth": "D * 1.1", "cornice": {"h": "cornH", "out": "cornOut"}, **tri}, "at": [[0, "base", z, 0]],
                 "_about": f"the six Doric columns of the {nm.split()[0]} front"})
    half = 2.5 * sp + D * 0.55
    add("side walls", {"type": "box", "width": "wallT", "length": round(eastZ - westZ, 3), "height": round(colH + entH, 3),
                       "at": [[round(half - 0.5, 3), "base", round((eastZ + westZ) / 2, 3), 0], [round(-half + 0.5, 3), "base", round((eastZ + westZ) / 2, 3), 0]],
                       "_about": "the walls of the halls, from the west front to the east"})
    gw = round(2 * half - 2.0, 3)
    add("gate wall", {"type": "wall", "width": gw, "height": round(colH + entH, 3), "thickness": 1.2, "beam": 6.0,
                      "openings": [door(round(gw / 2 + dx, 3), w, h) for dx, w, h in ((-6.3, 1.4, 3.1), (-3.6, 2.9, 5.3), (0, 4.2, 7.4), (3.6, 2.9, 5.3), (6.3, 1.4, 3.1))],
                      "at": [[0, "base", 0, 0]], "_about": "the gate wall and its five doors, the middle one the procession's"})
    # the west hall: two rows of three Ionic columns either side of the road, tall enough to carry the ceiling beams
    # over the hall at the height of the fronts' entablature tops
    ion_h = round(colH + entH - 0.65, 3)
    add("hall columns", {"type": "colonnade", "order": "ionic", "count": 3, "spacing": 4.0, "columnR": 0.52, "height": ion_h,
                         "entablature": {"h": 0.65, "depth": 1.1}, "at": [[2.9, "base", round(westZ / 2, 3), HALF_PI], [-2.9, "base", round(westZ / 2, 3), HALF_PI]],
                         "_about": "the Ionic columns of the west hall either side of the road, and the beams they carry"})
    add("west ceiling", {"type": "coffered-ceiling", "width": round(2 * half - 2.0, 3), "length": round(-westZ - D * 0.55 - 0.6, 3), "thickness": "cornH",
                         "nx": 6, "nz": 5, "depth": 0.25, "steps": 1, "at": [[0, f"base + {colH + entH}", round((westZ + D * 0.55) / 2 - 0.3, 3), 0]],
                         "_about": "the coffered marble ceiling of the west hall -- blue, with gold stars"})
    add("east ceiling", {"type": "coffered-ceiling", "width": round(2 * half - 2.0, 3), "length": round(eastZ - D * 0.55 - 0.6, 3), "thickness": round(entH + cornH, 3),
                         "nx": 6, "nz": 2, "depth": 0.25, "steps": 1, "at": [[0, f"base + {colH}", round((eastZ - D * 0.55) / 2 + 0.3, 3), 0]],
                         "_about": "the east portico's coffered ceiling"})
    rw = 2 * half + 2 * cornOut
    ridge = round(rw / 2 * math.tan(math.radians(14)), 3)
    z0, z1 = westZ - D * 0.55 - cornOut, eastZ + D * 0.55 + cornOut
    add("roof", {"type": "roof", "form": "gable", "width": round(rw, 3), "length": round(z1 - z0, 3), "pitch": 14, "rake": {"h": "cornH", "out": 0.15},
                 "at": [[0, f"base + {top}", round((z0 + z1) / 2, 3), 0]], "_about": "the central building's gable, a pediment over each front"})
    add("acroteria", acroteria("gable", f"base + {round(top + ridge, 3)}", round(z1 - 0.25, 3), round(z0 + 0.25, 3), "D * 1.3"))
    # THE WINGS, west of the fronts either side of the approach: a portico of three Doric columns facing the road
    # between two antae; behind the north one the picture gallery, behind the south one a shallow hall
    wX, wZ, wD, wH = P["wingX"], P["wingZ"], P["wD"], P["wH"]
    went = 1.35
    for side, nm in ((1, "north wing"), (-1, "south wing")):
        x = side * wX
        add(f"{nm} portico", {"type": "colonnade", "order": "doric", "count": 3, "spacing": 3.0, "columnR": "wD / 2", "height": "wH",
                              "entablature": {"h": went, "depth": "wD * 1.1", "cornice": {"h": 0.4, "out": 0.3}, "triglyphs": {"w": "wD * 0.55", "d": 0.12}},
                              "at": [[x, "base", "wingZ", HALF_PI]], "_about": f"the {nm}'s portico of three Doric columns facing the approach"})
        add(f"{nm} antae", {"type": "box", "width": 2.6 if side > 0 else 2.0, "length": 0.8, "height": wH + went,
                            "at": [[round(x + side * (1.3 if side > 0 else 1.0), 3), "base", round(wZ + 5.6, 3), 0], [round(x + side * (1.3 if side > 0 else 1.0), 3), "base", round(wZ - 5.6, 3), 0]],
                            "_about": "the side walls ending in antae either end of the portico"})
    room_w, room_x = 9.0, wX + 2.6 + 4.5
    add("pinakotheke", {"type": "enclosure", "plan": {"rect": [room_w, 10.76]}, "thickness": 0.8, "height": wH + went + 0.4, "glass": False,
                        "faces": {"3": [door(0, 1.8, 3.6), window(-3.0, 1.1, 1.5, 1.9), window(3.0, 1.1, 1.5, 1.9)], "0": [], "1": [], "2": []},
                        "courses": [{"y": wH, "h": 0.12, "out": 0.06, "profile": "band"}, {"y": wH + went, "h": 0.4, "out": 0.3, "profile": "cornice"}],
                        "at": [[round(room_x, 3), "base", "wingZ", 0]], "_about": "THE PINAKOTHEKE, the picture gallery: its door between two windows off the portico"})
    add("pinakotheke hall", {"type": "interior", "plan": {"rect": [room_w - 1.6, 10.76 - 1.6]}, "height": wH + went,
                             "at": [[round(room_x, 3), "base", "wingZ", 0]], "_about": "the gallery's room: its walls' inner faces are inside (the finish paints them)"})
    add("pinakotheke ceiling", {"type": "box", "width": room_w - 1.6 + 2.6, "length": 10.76 - 1.6, "height": 0.4,
                                "at": [[round(room_x - 1.3, 3), f"base + {wH + went}", "wingZ", 0]], "_about": "the gallery's and its portico's ceiling"})
    wing_len = 2.6 + room_w + 0.6
    add("north wing roof", {"type": "roof", "form": "hip", "width": round(wing_len, 3), "length": 12.2, "pitch": 14,
                            "at": [[round(wX - 0.6 + wing_len / 2, 3), f"base + {wH + went + 0.4}", "wingZ", 0]], "_about": "the north wing's hipped roof"})
    add("south wing hall", {"type": "box", "width": 0.8, "length": 11.2, "height": wH + went, "at": [[round(-wX - 2.4, 3), "base", "wingZ", 0]],
                            "_about": "the back wall of the south wing's shallow hall"})
    add("south wing ceiling", {"type": "box", "width": 3.2, "length": 11.2, "height": 0.4, "at": [[round(-wX - 1.2, 3), f"base + {wH + went}", "wingZ", 0]],
                               "_about": "its ceiling"})
    add("south wing roof", {"type": "roof", "form": "hip", "width": 4.4, "length": 12.2, "pitch": 14,
                            "at": [[round(-wX - 1.3, 3), f"base + {wH + went + 0.4}", "wingZ", 0]], "_about": "its hipped roof"})
    add("north wing platform", {"type": "box", "width": 15.0, "length": 13.6, "height": "base", "at": [[round(wX - 1.0 + 7.5, 3), 0, "wingZ", 0]],
                                "_about": "the floor the north wing stands on, level with the central building's"})
    add("south wing platform", {"type": "box", "width": 5.6, "length": 13.6, "height": "base", "at": [[round(-wX - 1.6, 3), 0, "wingZ", 0]],
                                "_about": "the south wing's floor"})
    save("propylaia.json", {"name": "Propylaia", "era": "-437--432", "region": "Greece", "_about": propylaia.__doc__.strip(),
                            "params": P, "build": build, "parts": parts})


# ---- the temple of Athena Nike -----------------------------------------------------------------------------------------
def athena_nike():
    temple("athena-nike.json", ("Temple of Athena Nike",
      "THE TEMPLE OF ATHENA NIKE (c. 420 BC, Kallikrates), on the bastion before the Propylaia: AMPHIPROSTYLE -- four monolithic Ionic columns before each end and none down the sides -- on a three-step crepidoma 5.38 x 8.16m, its cella nearly square, its continuous frieze and its pediments painted, the wooden image of Athena Nike inside with a pomegranate in her hand."),
      {**common, "W": 5.38, "L": 8.16, "steps": 3, "stepH": 0.26, "stepOut": 0.3, "base": 0.78, "front": 4, "side": 2, "D": 0.53, "inset": 0.545,
       "colH": 4.07, "entH": 0.95, "cornH": 0.3, "cornOut": 0.25, "pitch": 14, "ridge": 0.68,
       "cellaW": 4.6, "cellaL": 3.9, "cellaZ": -0.45, "cellaH": 4.0, "wallT": 0.45, "doorW": 2.0, "doorH": 3.2, "porch": 0, "porchD": 0},
      order="ionic", porches=False, recess=0.2,
      statues={"cult base": pedestal((0, 0.78, -1.2), 1.0, 0.9, 0.5, "the base of the cult image"),
               "Athena Nike": statue((0, 1.28, -1.2), kind="woman", style="greek", stone="painted", scale=1.0, pose="offering",
                                     hold={"R": "items/food/pomegranate"}, wear=["clothes/crested-helmet"], seed=13, face=FACE_E)})


# ---- the site ---------------------------------------------------------------------------------------------------------
# the summit's edge, (x north, z east) metres from the Parthenon's middle -- the notch in the west where the stair
# comes up between the wings, the Nike bastion south of it
ROCK = [(21, -122), (21, -137), (37, -137), (50, -110), (62, -75), (69, -40), (70, -5), (66, 30), (58, 65), (44, 95), (26, 118),
        (6, 128), (-12, 124), (-28, 108), (-38, 75), (-41, 40), (-40, 5), (-38, -35), (-35, -75), (-31, -105), (-26, -122),
        (-26, -146), (-1, -146), (-1, -122)]
OPEN = {(21, -122), (-1, -146), (-1, -122)}   # the edges FROM these are open: the notch's -- the stair's head, the wings' fronts
LOW = {(-26, -122), (-26, -146), (-1, -146)}   # the bastion's edges: the Nike parapet, low


def acropolis():
    parts = {}; build = []
    def add(n, d): parts[n] = d; build.append(n)
    rockH = 14.0
    P = {"detail": 4, "rockH": rockH, "_rockH": "the summit over the plain round it (the real rises some seventy metres over the city: here its upper cliff)"}
    add("rock", {"type": "prism", "plan": {"points": [[x, z] for x, z in ROCK]}, "height": "rockH", "batter": {"out": 9, "power": 1.6},
                 "at": [[0, 0, 0, 0]], "_about": "the rock, its cliffs falling steeply from the summit's edge"})
    # the circuit walls along the edge, each run a parapet, its outer face on the cliff; the bastion's the Nike parapet
    area = sum(ROCK[i][0] * ROCK[(i + 1) % len(ROCK)][1] - ROCK[(i + 1) % len(ROCK)][0] * ROCK[i][1] for i in range(len(ROCK)))
    walls, low = [], []
    for i, p in enumerate(ROCK):
        q = ROCK[(i + 1) % len(ROCK)]
        if p in OPEN: continue
        dx, dz = q[0] - p[0], q[1] - p[1]; ln = math.hypot(dx, dz)
        t, h = (0.5, 1.05) if p in LOW else (1.8, 1.6)
        nx, nz = (-dz / ln, dx / ln) if area > 0 else (dz / ln, -dx / ln)      # (inward)
        mx, mz = (p[0] + q[0]) / 2 + nx * t / 2, (p[1] + q[1]) / 2 + nz * t / 2
        (low if p in LOW else walls).append([round(mx, 3), "rockH", round(mz, 3), round(math.atan2(-dz, dx), 5), round(ln + t, 3), t, h])
    for nm, rows, about in (("circuit wall", walls, "the circuit walls round the summit, a parapet over the cliffs"),
                            ("nike parapet", low, "the parapet round the Nike bastion, carved with Victories")):
        for k, (x, y, z, a, ln, t, h) in enumerate(rows):
            add(f"{nm} {k}", {"type": "box", "width": ln, "length": t, "height": h, "at": [[x, y, z, a]], "_about": about})
    # the buildings, each its own and painted as it is (the finish uses theirs)
    add("parthenon", {"type": "component", "use": "parthenon", "at": [[0, "rockH", 0, 0]], "_about": "the Parthenon (temples.py), on the summit's south side"})
    add("erechtheion", {"type": "component", "use": "erechtheion", "at": [[46, "rockH", -14, 0]], "_about": "the Erechtheion, on the north side over the old temple's site"})
    add("propylaia", {"type": "component", "use": "propylaia", "at": [[10, "rockH", -105, 0]], "_about": "the Propylaia, the gateway at the west end"})
    add("athena nike", {"type": "component", "use": "athena-nike", "at": [[-13.5, "rockH", -134, 0]], "_about": "the temple of Athena Nike on its bastion"})
    add("old temple", {"type": "box", "width": 21.3, "length": 43.4, "height": 0.4, "at": [[29, "rockH", -8, 0]],
                       "_about": "the foundations of the old temple of Athena, burnt by the Persians, between the two"})
    add("altar", {"type": "box", "width": 5.0, "length": 9.0, "height": 1.3, "at": [[30, "rockH", 26, 0]], "_about": "the great altar of Athena, east of the old temple"})
    # ATHENA PROMACHOS (Phidias, c. 456 BC): the bronze champion, nine metres tall, her spear's gilt point seen from the
    # sea, facing the gate
    add("Promachos base", pedestal((16, rockH, -72), 5.5, 5.5, 1.6, "the Promachos's base"))
    add("Athena Promachos", statue((16, rockH + 1.6, -72), kind="woman", style="greek", stone="bronze", scale=5.0, pose="spear bearer",
                                   hold={"L": "items/weapons/dory", "R": "items/shields/aspis"}, grip={"R": "shield rest"}, wear=["clothes/crested-helmet"], seed=9, face=FACE_W))
    # the stair up the west slope to the Propylaia's floor, between the wings
    add("stair", {"type": "flight", "width": 16, "run": 0.4, "rise": 0.2, "top": "rockH + 0.9", "landing": 0,
                  "at": [[10, 0, f"-122 - (rockH + 0.9) / 0.2 * 0.4", -HALF_PI]], "_about": "the stair up the west slope to the Propylaia, between its wings"})
    save("acropolis.json", {"name": "Acropolis of Athens", "era": "-447--406", "region": "Greece",
      "_about": "THE ACROPOLIS OF ATHENS as Pericles' builders left it (c. 400 BC), every building at its real size and PAINTED as it was: the rock, its circuit walls and the stair up the west slope; the PROPYLAIA, the gateway, its wings either side of the approach; on the bastion south of it the little temple of ATHENA NIKE; inside, the bronze ATHENA PROMACHOS facing the gate; the PARTHENON on the summit's south side, the ERECHTHEION with its porch of maidens on the north, between them the old temple's foundations and the great altar. (Each building is a building of its own -- erechtheion, propylaia, athena-nike, parthenon -- and the site's finish uses each one's.)",
      "params": P, "build": build, "parts": parts})


if __name__ == "__main__":
    erechtheion(); propylaia(); athena_nike(); acropolis()
