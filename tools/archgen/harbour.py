#!/usr/bin/env python3
"""THE HARBOUR (2026-11-03): an L2 library of port architecture, written out as L1 components
(assets/architecture/components/*.json) and one finish per tradition (assets/finishes/<tradition>-port.json).

    python3 tools/archgen/harbour.py

port.js lays a port out of these pieces along a shore stretch (docs/world.md "Ports"); assets/world/ports.json says which
pieces, params and finish each culture builds with. EVERY PIECE SHARES ONE FRAME: y 0 is the quay top (the town's ground
at the shore), +z is SEAWARD (out over the water), x runs along the shore; the water stands at y -F (F, the freeboard,
1.6 m by default) over a bed D deeper. Placed in the world with yaw = atan2(nx, nz) for the seaward normal (nx, nz).
Parts are named by their piece ("quay wall", "store roof", "pier piles") so one finish per tradition can dress them all.

The pieces (sizes are working figures, not one surveyed harbour; the sources each follows are in its `_about`):
    quay            a straight run of quay: stone (ashlar wall, coping, timber fenders, bronze rings, bollards, a water
                    stair inside the wall line), timber (a plank bulkhead on piles, cap beam, ladder) or steps (a stepped
                    quay down to the water the whole length: Japanese gangi, Indian ghats)
    pier            a timber jetty on piles out over the water, cross-braced bents, bollards, a ladder at its head
    mole            a rubble breakwater, battered, paved on top, a parapet on its sea side, a round head for a light
    pharos          the antique lighthouse in three stages, square, octagonal, round, and its lantern (after Alexandria
                    as the coins and Ibn al-Shaykh show it; scaled to a harbour light, 30 m, like Portus' or Leptis')
    light-tower     the medieval harbour light: a round stone tower, machicolated parapet, the fire in a capped turret
    lighthouse      the later lighthouse (1700-1900): a tapering round tower, gallery and rail, the glazed lantern, dome
    stone-lantern   the Japanese harbour lantern (joyato, Tomo-no-ura's 5.5 m): base, stem, table, fire box, roof, hoju
    beacon-pagoda   the Chinese river-mouth pagoda that served as a light (Liuhe Pagoda's role): octagonal, seven eaves
    horreum         the antique warehouse as a stoa: a colonnade before a row of store rooms under a tiled roof
    speicher        the Hanseatic gabled warehouse: four storeys of loading doors under the gable to the quay, the hoist
                    beam in the apex, a stepped gable (Luebeck, Stralsund, Danzig)
    kura            the Japanese / Chinese storehouse: thick plastered walls on a dark tiled skirt, heavy roof; `firewalls`
                    raises the stepped gable walls of south China (matouqiang)
    treadwheel-crane the medieval harbour crane: a round stone tower, its conical cap carrying the jib (Trier 1413,
                    Andernach 1561, Bingen); the treadwheel inside
    polyspastos     the Roman crane (Vitruvius X.2): two legs leaning out over the quay, stays, pulley block, and the
                    treadwheel at their foot
    jib-crane       the 19th-century iron crane: a curved box jib on a pillar (Fairbairn's), the driver's cab
    ship-shed       Greek neosoikoi (Zea, Munychia): slipways sloping into the water between column rows, a roof per slip
    boat-slip       a hard sloping into the water with its curbs and a capstan at the top
    fish-market     an open market hall on posts, stone tables, the catch on them
    customs-house   the harbour office: two storeys, an arcade on the quay, a hipped roof
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
COMP = os.path.join(ROOT, "assets", "architecture", "components")
FIN = os.path.join(ROOT, "assets", "finishes")
PI2 = "1.5707963"


def write(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")


def r4(v): return round(v, 4)
def at(*pts): return [list(p) if len(p) == 4 else [*p, 0] for p in pts]
def box(w, l, h, *pts, **k): return {"type": "box", "width": w, "length": l, "height": h, "at": at(*pts), **k}
def col(r, h, *pts, sides=8, **k): return {"type": "column", "radius": r, "height": h, "sides": sides, "at": at(*pts), **k}
def prism(plan, h, *pts, **k): return {"type": "prism", "plan": plan, "height": h, "at": at(*pts), **k}
def bars(w, lines=None, paths=None, pos=None, closed=False, **k):
    pts = [] if pos is None else ([pos] if not isinstance(pos[0], (list, tuple)) else pos)
    d = {"type": "bars", "w": w, **({"lines": lines} if lines else {}), **({"paths": paths} if paths else {}), "at": at(*pts) if pts else [[0, 0, 0, 0]], **k}
    if closed: d["closed"] = True
    return d
def marker(role, *pts, repeat=None, **data): return {"type": "marker", "role": role, "at": at(*pts), "data": data, **({"repeat": repeat} if repeat else {})}
def item(path, *pts, **k): return {"type": "item", "item": path, "at": at(*pts), **k}
def comp(use, *pts, params=None, **k): return {"type": "component", "use": use, "at": at(*pts), **({"params": params} if params else {}), **k}
def roof(form, w, l, pitch, *pts, over=0.3, **k): return {"type": "roof", "form": form, "width": w, "length": l, "pitch": pitch, "overhang": over, "at": at(*pts), **k}
def cone(r, rise, *pts, sides=16, profile="trigonal", **k):
    head = {"profile": profile, "rise": rise, **({} if profile == "trigonal" else {"seg": 6})}
    return {"type": "dome", "sides": sides, "radius": r, "thickness": 0, "head": head, "cap": False, "at": at(*pts), **k}
def opening(x, w, sill, top, head="flat", **k): return {"at": x, "width": w, "sill": sill, "springing": top, "head": {"profile": head}, **k}
def every(step, w, sill, top, end=1.0, head="flat", **k): return {"every": step, "width": w, "end": end, "sill": sill, "springing": top, "head": {"profile": head}, **k}
def rep(count, dx=0, dy=0, dz=0): return {"count": count, "step": [dx, dy, dz, 0]}
def when(d, **w):
    d["when"] = {k: v for k, v in w.items() if not k.startswith("_")}
    d.update({k: v for k, v in w.items() if k.startswith("_")})
    return d
def ring_path(r, n, y=0.0, plane="xz", cx=0.0, cy=0.0, cz=0.0):
    """a closed polygon of n points, radius r (a number or an expression), in the xz plane at height y or the xy plane"""
    out = []
    for k in range(n):
        c, s = r4(math.cos(2 * math.pi * k / n)), r4(math.sin(2 * math.pi * k / n))
        X = f"{cx} + ({r}) * {c}" if isinstance(r, str) else r4(cx + r * c)
        S = f"{cz if plane == 'xz' else cy} + ({r}) * {s}" if isinstance(r, str) else r4((cz if plane == "xz" else cy) + r * s)
        out.append([X, y, S] if plane == "xz" else [X, S, cz])
    return out


def component(key, name, about, params, parts, build=None):
    doc = {"name": name, "_about": about + " GENERATED by tools/archgen/harbour.py: change it there.",
           "params": {"detail": 4, **params}, "build": build or [k for k, v in parts.items() if v.get("type") != "interior"], "parts": parts}
    write(os.path.join(COMP, key + ".json"), doc)
    return doc


FRAME = "y 0 the quay top, +z seaward, the water at y -F."
N_BAYS = "max(1, round(L / bay))"


# ---- QUAY ------------------------------------------------------------------------------------------------------------
def quay():
    """a straight run of quay L long centred on x 0, its face on z 0 (the water before it, +z), the apron B deep behind"""
    P = {"L": 24, "F": 1.6, "D": 3.0, "T": 1.6, "B": 6.0, "bay": 6.0, "style": "stone", "stairs": "yes",
         "_style": "stone: an ashlar wall with its coping, fenders and rings; timber: a plank bulkhead on piles under a cap beam; steps: a stepped quay down to the water the whole length (gangi, ghat)",
         "_stairs": "yes: a water stair inside the stone wall's line (sw wide, at sx), climbing +x from a landing at the water to the coping",
         "nb": N_BAYS, "st": "L / nb", "sw": 1.3, "sx": "0 - L / 2 + st * max(1, floor(nb / 4))", "_sx": "between two bollards, a quarter of the way along", "run": 0.3, "ns": "ceil(F / 0.2)", "sr": "ns * run",
         "_sr": "the stair's (or the stepped quay's) run: ns steps of a fifth of a metre", "x0": "sx - sr / 2", "x1": "sx + sr / 2", "xl": "x0 - 1.4"}
    S = {"style": "stone"}
    parts = {
        # stone: the wall (split round the stair when it has one), the coping, the fenders, the rings
        "quay wall": when(box("L", "T", "F + D - 0.3", (0, "0 - F - D", "0 - T / 2")), style="stone", stairs="no"),
        "quay wall 1": when(box("xl + L / 2", "T", "F + D - 0.3", ("(xl - L / 2) / 2", "0 - F - D", "0 - T / 2")), style="stone", stairs="yes"),
        "quay wall 2": when(box("L / 2 - x1", "T", "F + D - 0.3", ("(x1 + L / 2) / 2", "0 - F - D", "0 - T / 2")), style="stone", stairs="yes"),
        "quay wall 3": when(box("x1 - xl", "T - sw", "F + D - 0.3", ("(xl + x1) / 2", "0 - F - D", "0 - T + (T - sw) / 2")), style="stone", stairs="yes"),
        "quay coping": when(box("L", "T + 0.1", 0.3, (0, -0.3, "0.05 - T / 2")), style="stone", stairs="no", _about="the coping, standing 10 cm out over the face"),
        "quay coping 1": when(box("xl + L / 2", "T + 0.1", 0.3, ("(xl - L / 2) / 2", -0.3, "0.05 - T / 2")), style="stone", stairs="yes"),
        "quay coping 2": when(box("L / 2 - x1", "T + 0.1", 0.3, ("(x1 + L / 2) / 2", -0.3, "0.05 - T / 2")), style="stone", stairs="yes"),
        "quay coping 3": when(box("x1 - xl", "T - sw", 0.3, ("(xl + x1) / 2", -0.3, "0 - T + (T - sw) / 2")), style="stone", stairs="yes"),
        "water stair landing": when(box(1.4, "sw", "D", ("x0 - 0.7", "0 - F - D", "0 - sw / 2"), walked=True), style="stone", stairs="yes",
                                    _about="the landing at the water's edge the stair starts from"),
        "water stair": when({"type": "flight", "run": "run", "rise": "F / ns", "width": "sw", "base": 0, "top": "F", "landing": 0, "railing": False,
                             "ground": "0 - D", "at": [["x0", "0 - F", 0, 0]], "_about": "climbing +x inside the wall's line, open to the water on its seaward side"},
                            style="stone", stairs="yes"),
        "fenders": when(box(0.26, 0.24, "F + 0.5", ("0 - L / 2 + st", "0 - F - 0.5", 0.12), repeat=rep("nb - 1", "st")), style="stone",
                        _about="oak rubbing posts on the face between the bollards' bays"),
        "mooring rings": when(bars(0.045, None, [ring_path(0.16, 8, plane="xy", cy=-0.16)], ("0 - L / 2 + st / 2", -0.45, 0.04),
                                   closed=True, repeat=rep("nb", "st"), kind="iron"), style="stone",
                              _about="bronze rings let into the face under the coping, one a bay (Ostia's travertine blocks, the Hanse quays' iron)"),
        # timber: the bulkhead, its piles, the cap beam and the plank deck behind; a ladder for the stair
        "bulkhead": when(box("L", 0.22, "F + D - 0.35", (0, "0 - F - D", -0.11)), style="timber", _about="horizontal planks spiked to the piles' land side"),
        "quay piles": when(col(0.17, "F + D - 0.35", ("0 - L / 2 + 0.5", "0 - F - D", 0.17), sides=6, repeat=rep("round((L - 1) / 2) + 1", "(L - 1) / round((L - 1) / 2)")), style="timber"),
        "cap beam": when(box("L", 0.55, 0.35, (0, -0.35, 0.05)), style="timber", walked=True),
        "quay deck": when(box("L", "T - 0.22", 0.12, (0, -0.12, "0 - 0.22 - (T - 0.22) / 2"), walked=True), style="timber"),
        "quay ladder": when(bars(0.06, [[-0.25, "0 - F - 0.6", 0.42, -0.25, 0.5, 0.42], [0.25, "0 - F - 0.6", 0.42, 0.25, 0.5, 0.42]]
                                 + [[-0.25, r4(-0.3 * k), 0.42, 0.25, r4(-0.3 * k), 0.42] for k in range(0, 8)], None, ("sx", 0, 0), kind="iron"), style="timber"),
        # steps: the stepped quay, the full length, with the ledge at the water
        "quay steps": when({"type": "flight", "run": "run", "rise": "F / ns", "width": "L", "base": 0, "top": "F", "landing": 0, "railing": False,
                            "ground": "0 - D", "at": [["L / 2", "0 - F", "sr", PI2]], "_about": "the stepped face, climbing landward from the water"}, style="steps"),
        "quay steps ledge": when(box("L", 2.2, "D", (0, "0 - F - D", "sr + 1.1"), walked=True), style="steps", _about="the ledge at the water the boats lie against"),
        "quay steps wall": when(box("L", "T", "F + D", (0, "0 - F - D", "0 - T / 2")), style="steps"),
        # every style: the apron behind, the bollards
        "quay paving": box("L", "B", 0.12, (0, -0.12, "0 - T - B / 2"), walked=True, _about="the apron the goods are set down on"),
        "bollards": col(0.2, 0.5, ("0 - L / 2 + st / 2", 0, -0.75), sides=10, taper=0.82, repeat=rep("nb", "st")),
        "bollard heads": col(0.25, 0.14, ("0 - L / 2 + st / 2", 0.5, -0.75), sides=10, repeat=rep("nb", "st")),
        "slots": marker("slot", ("0 - L / 2 + 2", 0, "0 - T - 1.8"), repeat=rep("max(1, round((L - 4) / 3))", 3)),
    }
    return component("quay", "Quay", f"A QUAY, a straight run of it L long along x, its face on z 0: {FRAME} `style` stone (an ashlar wall T thick from the bed, its coping standing out over the face, oak fenders and bronze mooring rings a bay apart, a water stair `stairs` inside the wall's line climbing from a landing at the water), timber (a plank bulkhead on a row of piles under a cap beam, a ladder at sx: the Hanseatic Bollwerk, Bryggen) or steps (the whole face a flight down to a ledge at the water: the Japanese gangi of Tomo-no-ura and Takehara, the ghats); behind it the paved apron B deep; bollards every `bay`. `slot` markers on the apron for the goods.", P, parts)


# ---- PIER ------------------------------------------------------------------------------------------------------------
def pier():
    P = {"L": 24, "W": 3.4, "F": 1.6, "D": 3.0, "bay": 3.0, "z0": 0, "nb": "max(2, round((L - z0) / bay))", "st": "(L - z0) / nb",
         "_z0": "where the bents begin: on a stepped quay (gangi, ghat) the deck spans the steps from the top and its piles stand past the ledge"}
    lad = [[-0.25, "0 - F - 0.6", 0, -0.25, 0.6, 0], [0.25, "0 - F - 0.6", 0, 0.25, 0.6, 0]] + [[-0.25, r4(0.3 - 0.3 * k), 0, 0.25, r4(0.3 - 0.3 * k), 0] for k in range(8)]
    parts = {
        "pier deck": box("W", "L", 0.12, (0, -0.12, "L / 2"), walked=True),
        "pier stringers": box(0.22, "L - min(z0, 0.8)", 0.3, ("0 - W / 2 + 0.35", -0.42, "(L + min(z0, 0.8)) / 2"), ("W / 2 - 0.35", -0.42, "(L + min(z0, 0.8)) / 2"),
                              _about="the two stringers; over a stepped quay they start clear of its top steps"),
        "pier caps": box("W + 0.5", 0.32, 0.32, (0, -0.74, "z0 + st / 2"), repeat=rep("nb", 0, 0, "st")),
        "pier piles": col(0.17, "F + D - 0.74", ("0 - W / 2", "0 - F - D", "z0 + st / 2"), ("W / 2", "0 - F - D", "z0 + st / 2"), sides=6, repeat=rep("nb", 0, 0, "st")),
        "pier braces": bars(0.12, [["0 - W / 2", -0.8, 0, "W / 2", "0 - F + 0.2", 0], ["W / 2", -0.8, 0, "0 - W / 2", "0 - F + 0.2", 0]], None, (0, 0, "z0 + st / 2"),
                            repeat=rep("nb", 0, 0, "st"), kind="beam", _about="the bents' cross braces, down to the water"),
        "pier bollards": col(0.17, 0.5, ("0 - W / 2 + 0.3", 0, "L - 0.4"), ("W / 2 - 0.3", 0, "L - 0.4"), ("0 - W / 2 + 0.3", 0, "L / 2"), ("W / 2 - 0.3", 0, "L / 2"), sides=8, taper=0.85),
        "pier ladder": bars(0.06, lad, None, ("W / 2 - 0.7", 0, "L + 0.08"), kind="iron"),
    }
    return component("pier", "Pier", f"A PIER (jetty) of timber running out over the water from z 0 to L: {FRAME} The plank deck W wide on two stringers over cross-heads on bents of two piles every `bay`, each bent cross-braced down to the water; bollards at its head and half way; a ladder down to the water at its head. Ships lie along both sides.", P, parts)


# ---- MOLE ------------------------------------------------------------------------------------------------------------
def mole():
    P = {"L": 40, "W": 7.0, "F": 1.6, "D": 4.0, "top": 0.4, "side": 1, "out": "(F + D) * 0.9",
         "_side": "1: the open sea on +x (the parapet there), -1 on -x", "_out": "how far the rubble spreads past the top at the bed (each side)",
         "nb": "max(1, round(L / 10))"}
    parts = {
        "mole mound": prism({"rect": ["W", "L"]}, "F + D + top", (0, "0 - F - D", "L / 2"), batter={"out": "out", "power": 1}, walked=True,
                            _about="the rubble mound, battered both sides, its top walked"),
        "mole head": prism({"sides": 14, "radius": "W / 2 + 1.0"}, "F + D + top", (0, "0 - F - D", "L"), batter={"out": "out", "power": 1}, walked=True,
                           _about="the round head the light stands on"),
        "mole parapet": box(0.9, "L", 1.3, ("side * (W / 2 - 0.45)", "top", "L / 2"), _about="the breastwork on the sea side"),
        "mole bollards": col(0.2, 0.5, ("0 - side * (W / 2 - 0.7)", "top", 5), sides=10, taper=0.82, repeat=rep("nb", 0, 0, 10)),
    }
    return component("mole", "Mole", f"A MOLE (breakwater) of rubble running out from the shore along +z, L long, W wide on top: {FRAME} The mound battered out to the bed (`out`), its top `top` over the quay, a parapet along the open sea's side (`side`), bollards on the harbour side, a round head at L for a light (the moles of the Piraeus, Caesarea, Portus).", P, parts)


# ---- LIGHTS ----------------------------------------------------------------------------------------------------------
def pharos():
    P = {"H": 30, "A": "H * 0.26", "h1": "H * 0.48", "h2": "H * 0.24", "h3": "H * 0.1", "y1": 1.2, "y2": "y1 + h1 + 0.6", "y3": "y2 + h2 + 0.5", "y4": "y3 + h3",
         "_H": "about its whole height (Alexandria's was over 100 m; the harbour lights after it, at Portus, Leptis, Dover, 20-35 m)"}
    lc = [[f"A * {r4(0.2 * math.cos(2 * math.pi * k / 8))}", "y4", f"A * {r4(0.2 * math.sin(2 * math.pi * k / 8))}", 0] for k in range(8)]
    parts = {
        "pharos base": prism({"rect": ["A + 3", "A + 3"]}, 1.2, (0, 0, 0), walked=True),
        "pharos square": prism({"rect": ["A", "A"]}, "h1", (0, "y1", 0), batter={"out": "A * 0.05", "power": 1}),
        "pharos cornice": prism({"rect": ["A * 1.14", "A * 1.14"]}, 0.6, (0, "y1 + h1", 0), walked=True),
        "pharos octagon": prism({"sides": 8, "radius": "A * 0.36"}, "h2", (0, "y2", 0)),
        "pharos cornice 2": prism({"sides": 8, "radius": "A * 0.42"}, 0.5, (0, "y2 + h2", 0), walked=True),
        "pharos drum": prism({"sides": 16, "radius": "A * 0.24"}, "h3", (0, "y3", 0)),
        "pharos floor": prism({"sides": 16, "radius": "A * 0.27"}, 0.3, (0, "y4 - 0.3", 0), walked=True),
        "pharos lantern columns": {"type": "column", "radius": "A * 0.022", "height": "H * 0.07", "sides": 8, "at": lc},
        "pharos lantern slab": prism({"sides": 16, "radius": "A * 0.25"}, 0.25, (0, "y4 + H * 0.07 - 0.25", 0)),
        "pharos lantern roof": cone("A * 0.25", "A * 0.22", (0, "y4 + H * 0.07", 0)),
        "fire": marker("fire", (0, "y4", 0), r=1.0, h=1.6),
    }
    return component("pharos", "Pharos", f"THE PHAROS, the antique lighthouse in three stages: a square tower battered in toward its cornice, an octagon, a round drum, and on it the lantern of columns under a cone where the fire burns (Alexandria, c. 280 BC, as its coins and Ibn al-Shaykh's description show it: 56/28/7 parts of the height; the harbour lights after it at Ostia-Portus and Leptis Magna). H about its whole height; it stands on a base on the ground or a mole's head. {FRAME}", P, parts)


def light_tower():
    P = {"R": 3.2, "H": 16, "_H": "the tower's height to its parapet walk"}
    parts = {
        "light tower": prism({"sides": 16, "radius": "R * 0.86"}, "H", (0, 0, 0), batter={"out": "R * 0.14", "power": 1}),
        "light tower door": box(1.2, 0.2, 2.2, (0, 0, "0 - R + 0.05"), _about="the door on the land side (dark timber, a slab proud of the batter)"),
        "light tower corbels": prism({"sides": 16, "radius": "R * 0.86 + 0.45"}, 0.7, (0, "H", 0), walked=True, _about="the machicolated walk round the top"),
        "light tower parapet": {"type": "enclosure", "plan": {"sides": 16, "radius": "R * 0.86 + 0.25"}, "thickness": 0.4, "height": 1.1, "openings": [], "at": [[0, "H + 0.7", 0, 0]]},
        "light turret": {"type": "enclosure", "plan": {"sides": 8, "radius": 1.4}, "thickness": 0.3, "height": 2.4, "openings": {"pattern": "1", "width": 0.8, "sill": 0.6, "springing": 1.7, "head": {"profile": "semicircular"}},
                         "at": [[0, "H + 0.7", 0, 0]], "_about": "the turret the fire burns in, open on every side"},
        "light turret cap": cone(1.7, 2.2, (0, 0, 0), sides=8, seat="light turret"),
        "fire": marker("fire", (0, "H + 0.75", 0), r=0.6, h=1.0),
    }
    return component("light-tower", "Harbour light tower", f"THE MEDIEVAL HARBOUR LIGHT: a round stone tower battered toward its top, a machicolated walk round the parapet, and on it the turret the fire burns in, open on all eight sides under a pointed cap (the Lanterna's forerunners, Hook Head, the Hanseatic towers with a fire basket). {FRAME}", P, parts)


def lighthouse():
    P = {"R": 2.8, "H": 22, "_H": "the tower's height to its gallery"}
    posts = [[f"(R * 0.62 + 0.75) * {r4(math.cos(2 * math.pi * k / 16))}", "H + 0.3", f"(R * 0.62 + 0.75) * {r4(math.sin(2 * math.pi * k / 16))}", 0] for k in range(16)]
    parts = {
        "lighthouse plinth": prism({"sides": 16, "radius": "R + 0.6"}, 0.8, (0, 0, 0), walked=True),
        "lighthouse tower": prism({"sides": 16, "radius": "R * 0.62"}, "H - 0.8", (0, 0.8, 0), batter={"out": "R * 0.38", "power": 1}),
        "lighthouse door": box(1.1, 0.2, 2.2, (0, 0.8, "0 - R + 0.1")),
        "lighthouse gallery": prism({"sides": 16, "radius": "R * 0.62 + 0.9"}, 0.3, (0, "H", 0), walked=True),
        "lighthouse rail posts": {"type": "column", "radius": 0.035, "height": 1.0, "sides": 4, "at": posts},
        "lighthouse rail": bars(0.05, None, [[[f"(R * 0.62 + 0.75) * {r4(math.cos(2 * math.pi * k / 16))}", "H + 1.3", f"(R * 0.62 + 0.75) * {r4(math.sin(2 * math.pi * k / 16))}"] for k in range(16)]], closed=True, kind="iron"),
        "lighthouse watch room": prism({"sides": 16, "radius": "R * 0.62 - 0.1"}, 1.4, (0, "H + 0.3", 0)),
        "lantern": {"type": "enclosure", "plan": {"sides": 10, "radius": 1.25}, "thickness": 0.1, "height": 2.4, "glass": True,
                    "openings": {"pattern": "1", "width": 0.62, "sill": 0.3, "springing": 2.15, "head": {"profile": "flat"}}, "at": [[0, "H + 1.7", 0, 0]],
                    "_about": "the glazed lantern: ten panes round the lamp"},
        "lantern dome": cone(1.45, 1.0, (0, 0, 0), sides=10, profile="semicircular", seat="lantern"),
        "lantern vent": col(0.22, 0.5, (0, "H + 4.75", 0), sides=8, taper=0.6),
        "fire": marker("fire", (0, "H + 2.1", 0), r=0.35, h=0.7),
    }
    return component("lighthouse", "Lighthouse", f"THE LIGHTHOUSE of 1700-1900: a round masonry tower tapering to its gallery, an iron rail round it, the watch room, the glazed lantern under its domed roof and vent (Smeaton's Eddystone, Bell Rock, the Roter Sand's kin). {FRAME}", P, parts)


def stone_lantern():
    P = {"s": 1.0, "_s": "its size: 1 is Tomo-no-ura's joyato, 5.5 m to the jewel's tip on its stone base"}
    S = lambda v: f"s * {v}"
    parts = {
        "lantern base": prism({"rect": [S(3.4), S(3.4)]}, S(0.9), (0, 0, 0), batter={"out": S(0.3), "power": 1}, walked=True, _about="the stone platform (ishigaki)"),
        "lantern base 2": prism({"rect": [S(1.9), S(1.9)]}, S(0.35), (0, S(0.9), 0)),
        "lantern stem": prism({"rect": [S(0.85), S(0.85)]}, S(1.9), (0, S(1.25), 0)),
        "lantern table": prism({"rect": [S(1.7), S(1.7)]}, S(0.32), (0, S(3.15), 0)),
        "lantern firebox": {"type": "enclosure", "plan": {"rect": [S(1.2), S(1.2)]}, "thickness": S(0.12), "height": S(0.95), "glass": False,
                            "openings": {"pattern": "1", "width": S(0.6), "sill": S(0.15), "springing": S(0.8), "head": {"profile": "flat"}}, "at": [[0, S(3.47), 0, 0]],
                            "_about": "the fire box (hibukuro), its windows papered"},
        "lantern roof": roof("pyramid", S(2.5), S(2.5), 32, (0, S(4.42), 0), over=0, thickness=S(0.25)),
        "lantern jewel": comp("components/hoju", (0, S(4.95), 0), params={"s": S(0.55)}),
        "fire": marker("fire", (0, S(3.5), 0), r=0.25, h=0.5),
    }
    return component("stone-lantern", "Harbour lantern (joyato)", f"THE JAPANESE HARBOUR LANTERN (joyato, the night lamp the Edo ports kept lit for the boats): a stone platform, a square stem, the table, the fire box with papered windows, a pyramid roof and the jewel (Tomo-no-ura's of 1859, 5.5 m). {FRAME}", P, parts)


def beacon_pagoda():
    n = 7
    P = {"R": 3.2, "H": 24, "hs": f"(H - 2.5) / {n}", "_H": "to the top of the finial; seven eaves, the shaft tapering by the batter"}
    parts = {
        "pagoda plinth": prism({"sides": 8, "radius": "R + 1.4"}, 1.2, (0, 0, 0), walked=True),
        "pagoda shaft": prism({"sides": 8, "radius": "R * 0.62"}, f"hs * {n}", (0, 1.2, 0), batter={"out": "R * 0.38", "power": 1}),
        "pagoda door": box(1.0, 0.3, 2.1, (0, 1.2, "0 - R * 0.95"), _about="the arched door's leaves, on the land side"),
    }
    for k in range(n):
        f = r4(1 - (k + 1) / n)
        parts[f"pagoda eaves {k + 1}"] = prism({"sides": 8, "radius": f"R * 0.62 + R * 0.38 * {f} + 0.75"}, 0.32, (0, f"1.2 + hs * {k + 1} - 0.32", 0),
                                               batter={"out": 0.25, "power": 1}, _about="a brick eave corbelled out, its tiles")
    parts["pagoda spire"] = cone("R * 0.62 + 0.4", 1.2, (0, f"1.2 + hs * {n}", 0), sides=8)
    parts["pagoda finial"] = col(0.12, 1.4, (0, f"1.2 + hs * {n} + 0.9", 0), sides=6, taper=0.4)
    parts["fire"] = marker("fire", (0, f"1.2 + hs * {n - 1}", 0), r=0.3, h=0.6)
    return component("beacon-pagoda", "Beacon pagoda", f"THE CHINESE BEACON PAGODA: an octagonal brick pagoda of seven corbelled eaves on its plinth, the shaft tapering, a light kept in its top storey for the boats (the Liuhe Pagoda over the Qiantang mouth, 970, rebuilt 1165; the Zhenhai and Quanzhou beacon towers). {FRAME}", P, parts)


# ---- WAREHOUSES ------------------------------------------------------------------------------------------------------
def horreum():
    P = {"L": 32, "Dp": 13, "H": 5.6, "porch": 4.2, "order": "doric", "r": 0.36, "nc": "round(L / 4) + 1", "sp": "(L - 1) / (nc - 1)",
         "_order": "the colonnade's order: doric (a Greek stoa), tuscan (Roman), square (piers: Egypt, the Islamic and Indian ports)", "eh": "H * 0.16",
         "_porch": "the depth of the colonnade's walk before the store rooms"}
    flat = "flat"
    parts = {
        "store platform": prism({"rect": ["L + 1.2", "Dp + 1.2"]}, 0.45, (0, 0, 0), walked=True, _about="the stylobate on its step"),
        "store colonnade": {"type": "colonnade", "order": "order", "count": "nc", "spacing": "sp", "columnR": "r", "height": "H - eh",
                            "entablature": {"h": "eh", "cornice": {"h": "eh * 0.35", "out": 0.3}}, "at": [[0, 0.45, "Dp / 2 - 0.5", 0]], "when": {"order": ["doric", "tuscan", "ionic"]}},
        "store piers": when(col("r * 1.2", "H - eh", ("0 - (nc - 1) * sp / 2", 0.45, "Dp / 2 - 0.5"), sides=4, repeat=rep("nc", "sp")), order="square"),
        "store architrave": when(box("L - 0.4", "r * 2.6", "eh", (0, "0.45 + H - eh", "Dp / 2 - 0.5")), order="square"),
        "store walls": {"type": "enclosure", "plan": {"rect": ["L - 1", "Dp - porch - 0.5"]}, "thickness": 0.6, "height": "H", "glass": False, "openings": [],
                        "faces": {"0": every(4.0, 1.8, 0, 2.7, end=1.6), "2": every(8.0, 0.6, 2.6, 3.4, end=3.0)},
                        "at": [[0, 0.45, "0 - (porch + 0.5) / 2 + 0.25", 0]], "_about": "the row of store rooms behind the colonnade, a door into each, slits high in the back wall"},
        "store ceiling": box("L - 0.4", "porch + 0.3", 0.22, (0, "0.45 + H - 0.22", "Dp / 2 - porch / 2 - 0.45"), _about="the colonnade's ceiling, beams on the architrave and the wall"),
        "store roof": roof("gable", "Dp + 0.4", "L + 0.4", 18, (0, "0.45 + H", 0, PI2), over=0.5),
        "slots": marker("slot", ("0 - L / 2 + 3", 0.45, "Dp / 2 - porch / 2 - 0.4"), repeat=rep("max(1, round((L - 6) / 3))", 3)),
    }
    return component("horreum", "Harbour warehouse (stoa)", f"THE ANTIQUE HARBOUR WAREHOUSE as a stoa: a colonnade (`order`: doric for the Greek emporion stoas of the Piraeus, tuscan for the Roman horrea of Ostia, square piers elsewhere) before a row of store rooms, a door into each, slits high in the back wall, one gabled tiled roof over all; L along the quay, its front (+z) to the water. `slot` markers under the colonnade for the goods. {FRAME}", P, parts)


def stepped(w, h, steps=4):
    """a stepped gable's outline (historicism.stepped_gable's, feet at y 0) with its x in units of the expression w and its
    y in units of h: one outline for any width and rise"""
    pts = [(-0.5, 0.0)]
    for k in range(steps):
        x0 = -0.5 * (1 - k / steps); y1 = (k + 1) / (steps + 0.6)
        x1 = -0.5 * (1 - (k + 1) / steps) if k + 1 < steps else -0.5 / steps * 0.75
        pts += [(x0 + 0.02 if k else x0, y1), (x1, y1)]
    pts += [(pts[-1][0], 1.0), (-pts[-1][0], 1.0)]
    out = pts + [(-x, y) for x, y in reversed(pts[1:-2])] + [(0.5, 0.0)]
    return [[f"{w} * {r4(x)}", f"{h} * {r4(y)}"] for x, y in out]


def speicher():
    n = 4
    P = {"W": 9, "Dp": 16, "hs": 2.9, "H": f"hs * {n}", "pitch": 56, "rise": "W / 2 * sin(pitch * 0.0174533) / cos(pitch * 0.0174533)", "gableForm": "stepped",
         "_gableForm": "stepped: a brick stepped gable before the roof's end (Luebeck, Stralsund); plain: the gable is the roof's own end",
         "_hs": "the storeys' height; four of them to the eaves"}
    door = lambda j: opening(0, 1.4, 0 if j == 0 else 0.25, 2.3 if j == 0 else 2.2, glass=False)
    wins = lambda j: [opening("0 - W / 4 - 0.4", 0.8, 0.9, 2.1), opening("W / 4 + 0.4", 0.8, 0.9, 2.1)]
    front = [{"h": "hs", "openings": [door(j)] + wins(j)} for j in range(n - 1)] + [{"openings": [door(n - 1)] + wins(n - 1)}]
    side = [{"h": "hs", "openings": every(3.2, 0.7, 1.0, 2.0, end=1.5)} for j in range(n - 1)] + [{"openings": every(3.2, 0.7, 1.0, 2.0, end=1.5)}]
    hatch = [[0, f"H + {r4(0.35 + 2.0 * k)}", "Dp / 2 + 0.11", 0] for k in range(2)]
    parts = {
        "speicher walls": {"type": "enclosure", "plan": {"rect": ["W", "Dp"]}, "thickness": 0.6, "height": "H", "glass": False, "openings": [],
                           "faces": {"0": front, "1": side, "3": side}, "at": [[0, 0, 0, 0]], "interior": True,
                           "_about": "four storeys, the loading doors one over another in the gable's axis, a window either side; small windows down the flanks"},
        "speicher floors": box("W - 1.2", "Dp - 1.2", 0.25, (0, "hs - 0.25", 0), repeat=rep(n - 1, 0, "hs"), _about="the lofts on their beams"),
        "speicher roof": roof("gable", "W", "Dp", "pitch", (0, "H", 0), over=0),
        "speicher gable": when({"type": "screen", "outline": stepped("(W + 0.5)", "(rise + 0.9)"), "t": 0.6, "at": [[0, "H", "Dp / 2 + 0.05", 0]],
                                "_about": "the stepped brick gable standing before the roof's end"}, gableForm="stepped"),
        "speicher gable 2": when({"type": "screen", "outline": [["0 - W / 2", 0], [0, "rise"], ["W / 2", 0]], "t": 0.6, "at": [[0, "H", "Dp / 2 + 0.05", 0]],
                                  "_about": "the plain gable, flush under the roof's end (the hatches are set in it)"}, gableForm="plain"),
        "gable hatches": box(1.2, 0.12, 1.6, *[tuple(h) for h in hatch], _about="the loft hatches in the gable, one over the other"),
        "hoist beam": box(0.35, 1.6, 0.4, (0, "H + rise * 0.78", "Dp / 2 + 0.6"), _about="the hoist beam (Windenbalken) out of the apex"),
        "hoist hood": roof("gable", 0.9, 1.3, 40, (0, "H + rise * 0.78 + 0.4", "Dp / 2 + 0.75"), over=0),
        "hoist rope": bars(0.03, [[0, "H + rise * 0.78", "Dp / 2 + 1.25", 0, 1.4, "Dp / 2 + 1.25"]], kind="iron"),
        "hoist hook": box(0.12, 0.12, 0.3, (0, 1.1, "Dp / 2 + 1.25")),
        "door": marker("door", (0, 0, "Dp / 2 - 0.3", 0), w=1.4, h=2.3),
        "slots": marker("slot", ("0 - W / 2 + 1.5", 0, "Dp / 2 + 2.5"), repeat=rep(3, "(W - 3) / 2")),
    }
    return component("speicher", "Gabled warehouse (Speicher)", f"THE HANSEATIC WAREHOUSE (Speicher): a brick house W wide, its gable to the quay (+z), Dp deep, four storeys of lofts; the loading doors one over another in the gable's axis with a window either side, hatches up into the gable, the hoist beam out of the apex under its little hood with the rope and hook; `gableForm` stepped (the brick Staffelgiebel standing before the roof's end) or plain. Luebeck's salt warehouses, Stralsund, Danzig's granaries. {FRAME}", P, parts)


def kura():
    P = {"W": 9, "Dp": 6.5, "H": 5.4, "pitch": 26, "rise": "Dp / 2 * sin(pitch * 0.0174533) / cos(pitch * 0.0174533)", "firewalls": "no",
         "_firewalls": "yes: the gable walls carried up past the roof in steps under their own tiles (the matouqiang of Huizhou and Jiangnan): a Chinese storehouse"}
    side = lambda: [{"h": 2.7, "openings": [opening("0 - W / 4", 1.5, 0, 2.2, glass=False)]}, {"openings": [opening("W / 5", 0.8, 0.8, 1.6, glass=False)]}]
    parts = {
        "kura base": prism({"rect": ["W + 0.5", "Dp + 0.5"]}, 0.45, (0, 0, 0), walked=True),
        "kura walls": {"type": "enclosure", "plan": {"rect": ["W", "Dp"]}, "thickness": 0.5, "height": "H", "glass": False, "openings": [],
                       "faces": {"0": side(), "2": [{"h": 2.7, "openings": []}, {"openings": [opening(0, 0.8, 0.8, 1.6, glass=False)]}]},
                       "at": [[0, 0.45, 0, 0]], "interior": True, "_about": "earth walls half a metre thick plastered white, the door and a high window to the water"},
        "kura skirt": None,
        "kura door": box(1.7, 0.24, 2.4, ("0 - W / 4", 0.45, "Dp / 2 + 0.12"), _about="the heavy plastered door, standing open beside its doorway"),
        "kura roof": roof("gable", "Dp + 0.2", "W + 0.2", "pitch", (0, "0.45 + H", 0, PI2), over=0.55),
        "kura ridge": box("W + 1.2", 0.4, 0.45, (0, "0.45 + H + rise - 0.05", 0)),
        "kura firewalls": when({"type": "screen", "outline": stepped("(Dp + 0.6)", "(rise + 1.6)", 2), "t": 0.45,
                                "at": [["W / 2 + 0.6", "0.45 + H", 0, PI2], ["0 - W / 2 - 0.15", "0.45 + H", 0, PI2]],
                                "_about": "the stepped gable walls rising past the roof"}, firewalls="yes"),
        "door": marker("door", ("0 - W / 4", 0.45, "Dp / 2 - 0.25", 0), w=1.5, h=2.2),
        "slots": marker("slot", ("0 - W / 2 + 1.2", 0, "Dp / 2 + 2.0"), repeat=rep(3, "(W - 2.4) / 2")),
    }
    parts["kura skirt"] = {"type": "enclosure", "plan": {"rect": ["W + 0.12", "Dp + 0.12"]}, "thickness": 0.06, "height": 1.3, "openings": [],
                           "faces": {"0": [opening("0 - W / 4", 1.5, 0, 1.3, glass=False)]}, "at": [[0, 0.45, 0, 0]],
                           "_about": "the dark skirt of tiles (namako-kabe) round the wall's foot, a skin on the wall"}
    return component("kura", "Storehouse (kura)", f"THE JAPANESE STOREHOUSE (kura, dozo), the godown of the Edo ports and canals: earth walls half a metre thick, plastered white over a dark skirt of tiles, a heavy door and a small high window to the water, a tiled gable roof on a deep ridge. `firewalls` yes raises the stepped gable walls of the south Chinese warehouses (Huizhou, Suzhou, the Canton godowns) past the roof. W along the quay, its front (+z) to the water. {FRAME}", P, parts)


# ---- CRANES ----------------------------------------------------------------------------------------------------------
def swung(*p, a="ja"):
    """a point (0, y, z) of what turns with a crane's cap, swung `a` (radians, an expression) about the y axis: [x, y, z, yaw]"""
    x, y, z = p
    return (f"({z}) * sin({a})", y, f"({z}) * cos({a})", a)


def treadwheel_crane():
    P = {"R": 3.6, "Ht": 6.5, "reach": 4.5, "F": 1.6, "jib": 0,
         "_reach": "how far the jib's tip stands out past the tower's face over the water", "jy": "Ht + 1.4",
         "_jib": "the cap's turn (degrees) from straight out over the water (+z), toward +x: port.js swings it over its berth's hold",
         "ja": "jib * 0.0174533"}
    parts = {
        "crane tower": {"type": "enclosure", "plan": {"sides": 16, "radius": "R"}, "thickness": 0.9, "height": "Ht", "glass": False, "openings": [],
                        "faces": {"8": [opening(0, 1.3, 0, 2.4, "semicircular", glass=False)], "0": [opening(0, 0.9, 3.4, 4.6, "semicircular", glass=False)]},
                        "at": [[0, 0, 0, 0]], "interior": True, "_about": "the round stone tower, its door to the land, a window to the water"},
        "crane floor": prism({"sides": 16, "radius": "R - 0.85"}, 0.2, (0, "Ht - 0.2", 0)),
        "crane eaves": prism({"sides": 16, "radius": "R + 0.3"}, 0.35, (0, "Ht", 0)),
        "crane roof": cone("R + 0.55", "R * 1.25", (0, 0, 0), seat="crane tower"),
        "crane jib strut": bars(0.26, [[0, "Ht + 0.4", "R + 0.2", 0, "jy", "R + reach * 0.75"]], None, (0, 0, 0, "ja"), kind="beam"),
        "crane jib": box(0.42, "R + reach + 1.0", 0.5, swung(0, "jy", "(R + reach + 1.0) / 2 - 0.5"), _about="the jib (the Ausleger) out of the turning cap over the water"),
        "crane jib hood": roof("gable", 0.9, 1.6, 40, swung(0, "jy + 0.5", "R + reach - 0.2"), over=0),
        "crane rope": bars(0.035, [[0, "jy", "R + reach", 0, "0 - F + 1.2", "R + reach"]], None, (0, 0, 0, "ja"), kind="iron"),
        "crane hook": box(0.18, 0.18, 0.4, swung(0, "0 - F + 0.8", "R + reach")),
        "crane wheel stand": box(0.3, 2.0, 2.45, (0, 0, 0)),
        "crane wheel treads": bars(0.1, [[r4(2.25 * math.cos(2 * math.pi * k / 16)), r4(2.6 + 2.25 * math.sin(2 * math.pi * k / 16)), -0.6,
                                          r4(2.25 * math.cos(2 * math.pi * k / 16)), r4(2.6 + 2.25 * math.sin(2 * math.pi * k / 16)), 0.6] for k in range(16)]
                                  + [[0, 2.6, -0.9, 0, 2.6, 0.9], [-2.3, 2.6, -0.6, 2.3, 2.6, -0.6], [0, 0.3, -0.6, 0, 4.9, -0.6], [-2.3, 2.6, 0.6, 2.3, 2.6, 0.6], [0, 0.3, 0.6, 0, 4.9, 0.6]], kind="beam"),
        "crane wheel": bars(0.12, None, [ring_path(2.3, 16, plane="xy", cy=2.6, cz=-0.6), ring_path(2.3, 16, plane="xy", cy=2.6, cz=0.6)], closed=True, kind="beam",
                            _about="the treadwheel inside, its two rims (seen through the door)"),
    }
    return component("treadwheel-crane", "Treadwheel crane", f"THE MEDIEVAL HARBOUR CRANE: a round stone tower R across, its conical cap turning on it and carrying the jib out over the water, the rope down to the hook at the hold; inside, the treadwheel the men walk to wind it (Trier's Alter Krahnen 1413, Andernach 1561, Bingen, Wuerzburg; Danzig's and Lueneburg's are timber). {FRAME}", P, parts)


def polyspastos():
    P = {"Hc": 10, "lean": 3.0, "F": 1.6, "_lean": "how far the apex stands out over the water past the legs' feet (at z -1)"}
    ax, ay, az = 0, "Hc", "lean"
    rim = lambda x: ring_path(2.4, 16, plane="xy", cy=2.6, cz=x)
    wheel_x = -5.5
    # (the wheel's axis runs along x; its rims in planes x = +-0.7 -- written in the z-y plane and placed turned)
    lines = [[-1.8, 0, -1.0, 0, "Hc", "lean"], [1.8, 0, -1.0, 0, "Hc", "lean"],
             [-1.2, "Hc * 0.33", "-1 + (lean + 1) * 0.33", 1.2, "Hc * 0.33", "-1 + (lean + 1) * 0.33"],
             [-0.6, "Hc * 0.66", "-1 + (lean + 1) * 0.66", 0.6, "Hc * 0.66", "-1 + (lean + 1) * 0.66"],
             [-2.2, 0.15, -1.0, 2.2, 0.15, -1.0]]
    ropes = [[0, "Hc", "lean", -3.2, 0.1, -9.0], [0, "Hc", "lean", 3.2, 0.1, -9.0], [0, "Hc", "lean", 0, 0.1, -10.5],
             [0, "Hc - 0.3", "lean", 0, "0 - F + 1.4", "lean"], [0, "Hc - 0.3", "lean", 0, 2.6, wheel_x]]
    wheel = []
    for k in range(16):
        a = 2 * math.pi * k / 16
        y, z = r4(2.6 + 2.4 * math.sin(a)), r4(wheel_x + 2.4 * math.cos(a))
        wheel.append([-0.7, y, z, 0.7, y, z])
    for k in range(8):
        a = 2 * math.pi * k / 8
        for x in (-0.7, 0.7):
            wheel.append([x, 2.6, wheel_x, x, r4(2.6 + 2.4 * math.sin(a)), r4(wheel_x + 2.4 * math.cos(a))])
    wheel += [[-1.3, 2.6, wheel_x, 1.3, 2.6, wheel_x]]
    for x in (-1.15, 1.15):
        wheel += [[x, 0, wheel_x - 1.4, x, 2.7, wheel_x], [x, 0, wheel_x + 1.4, x, 2.7, wheel_x], [x, 0.1, wheel_x - 1.6, x, 0.1, wheel_x + 1.6]]
    parts = {
        "crane legs": bars(0.32, lines, kind="beam", _about="the two legs, their braces and the sill they stand on"),
        "crane ropes": bars(0.04, ropes, kind="iron", _about="the stays back to their stakes, the fall to the hook, the rope back to the wheel"),
        "crane block": box(0.5, 0.5, 0.8, (0, "Hc - 0.9", "lean"), _about="the pulley block (polyspastos: five sheaves) under the apex"),
        "crane hook": box(0.2, 0.2, 0.4, (0, "0 - F + 1.0", "lean")),
        "crane wheel": {**bars(0.14, wheel, kind="beam"), "_about": "the treadwheel (magna rota) on its trestles, its axis along x"},
        "crane stakes": box(0.3, 0.3, 0.5, (-3.2, -0.4, -9.0), (3.2, -0.4, -9.0), (0, -0.4, -10.5)),
    }
    return component("polyspastos", "Roman crane (polyspastos)", f"THE ROMAN CRANE (Vitruvius X.2): two timber legs leaning out over the quay to an apex Hc high and `lean` past the edge, braced, stayed back by ropes to stakes, the pulley block under the apex, the fall to the hook, and the rope back to the treadwheel at the foot (the Haterii relief; the reconstructions at Bonn and Xanten). {FRAME}", P, parts)


def jib_crane():
    P = {"Hj": 9, "reach": 7, "F": 1.6, "jib": 0, "ja": "jib * 0.0174533",
         "_reach": "the hook's distance from the post", "_jib": "the crane's turn on its post (degrees) from straight out over the water (+z), toward +x"}
    jib = [[0, 1.8, -0.6], [0, "Hj * 0.55", 0.5], [0, "Hj * 0.88", "reach * 0.45"], [0, "Hj", "reach * 0.8"], [0, "Hj * 0.97", "reach"]]
    turn = (0, 0, 0, "ja")
    parts = {
        "crane pillar": col(1.0, 1.2, (0, 0, 0), sides=12, _about="the granite pillar the crane turns on"),
        "crane post": col(0.42, 1.0, (0, 1.2, 0), sides=12, kind="iron"),
        "crane jib": bars(0.55, None, [jib], turn, kind="iron", _about="Fairbairn's curved box jib of riveted plate"),
        "crane tie": bars(0.18, [[0, 2.2, -1.2, 0, "Hj * 0.88", "reach * 0.45"], [0, 2.0, -1.6, 0, 2.2, -1.2]], None, turn, kind="iron"),
        "crane cab": box(2.2, 2.4, 2.4, swung(0, 2.0, -1.9), _about="the driver's cab and the winding gear in it"),
        "crane cab roof": roof("gable", 2.6, 2.8, 25, swung(0, 4.4, -1.9), over=0),
        "crane rope": bars(0.035, [[0, "Hj * 0.97", "reach", 0, "0 - F + 1.2", "reach"]], None, turn, kind="iron"),
        "crane hook": box(0.2, 0.2, 0.4, swung(0, "0 - F + 0.8", "reach")),
    }
    return component("jib-crane", "Iron jib crane", f"THE IRON HARBOUR CRANE of the 19th century: a curved box jib of riveted plate (Fairbairn's patent, 1850) on its post on a granite pillar, the driver's cab with the winding gear behind, the rope and hook out over the water. {FRAME}", P, parts)


# ---- SHIP SHEDS, SLIP, MARKET, OFFICE --------------------------------------------------------------------------------
def ship_shed():
    P = {"n": 4, "bw": 6.5, "Ls": 40, "F": 1.6, "D": 3.0, "Hc": 4.6, "dip": "atan2(F + 1.0, Ls + 6) * 57.29578",
         "_n": "slipways side by side, bw apart (Zea: 6.25-6.5 m between the column rows, 37-40 m long under the roof)",
         "_dip": "the slipways' slope: from the quay top at the back to a metre under the water 6 m out"}
    nzc = 10
    cz = [[0, 0, f"0 - Ls + Ls / {nzc} * {r4(k + 0.5)}", 0] for k in range(nzc)]
    for c in cz: c[0] = "0 - n * bw / 2"
    parts = {
        "shed dividers": box(1.3, "Ls + 2", "F + D", ("0 - n * bw / 2", "0 - F - D", "0 - Ls / 2 + 1"), repeat=rep("n + 1", "bw"), walked=True,
                             _about="the stylobates between the slips, quays at the top, the columns on them"),
        "shed back wall": box("n * bw + 1.3", 0.7, "Hc + 0.6", (0, 0, "0 - Ls - 0.35")),
        "shed slips": {**box("bw - 1.3", "Ls + 6", 0.5, ("0 - (n - 1) * bw / 2", -0.5, "0 - Ls / 2 + 3"), repeat=rep("n", "bw")),
                       "lean": {"deg": "dip", "toward": [0, 1], "at": [0, 0, "0 - Ls"]}, "_about": "the slipways, sloping into the water"},
        "shed columns": {"type": "column", "radius": 0.32, "height": "Hc", "sides": 8, "at": cz, "repeat": rep("n + 1", "bw")},
        "shed beams": box(0.6, "Ls + 0.6", 0.55, ("0 - n * bw / 2", "Hc", "0 - Ls / 2 + 0.3"), repeat=rep("n + 1", "bw")),
        "shed roofs": roof("gable", "bw", "Ls + 0.6", 20, ("0 - (n - 1) * bw / 2", "Hc + 0.55", "0 - Ls / 2 + 0.3"), over=0.25, repeat=rep("n", "bw")),
    }
    return component("ship-shed", "Ship sheds (neosoikoi)", f"GREEK SHIP SHEDS (neosoikoi): `n` slipways side by side sloping from the back wall down into the water, between them the stylobates carrying the column rows, the beams on the columns, a gabled roof over each slip, open to the sea; a trireme hauled up each (Zea and Munychia at the Piraeus, 196 sheds; Oiniadai). {FRAME}", P, parts)


def boat_slip():
    P = {"w": 5, "Ls": 16, "F": 1.6, "D": 2.0, "dip": "atan2(F + 1.0, Ls) * 57.29578"}
    parts = {
        "slip ramp": {**box("w", "Ls", 0.6, (0, -0.6, "Ls / 2 - 2")), "lean": {"deg": "dip", "toward": [0, 1], "at": [0, 0, -2]}, "walked": True, "_about": "the hard, sloping into the water"},
        "slip curbs": {**box(0.5, "Ls", 0.9, ("0 - w / 2 - 0.25", -0.6, "Ls / 2 - 2"), ("w / 2 + 0.25", -0.6, "Ls / 2 - 2")),
                       "lean": {"deg": "dip", "toward": [0, 1], "at": [0, 0, -2]}},
        "slip apron": box("w + 4", 4, 0.12, (0, -0.12, -4), walked=True),
        "capstan": col(0.35, 1.0, (0, 0, -4.6), sides=10),
        "capstan bars": bars(0.08, [[-1.1, 0.85, -4.6, 1.1, 0.85, -4.6], [0, 0.85, -5.7, 0, 0.85, -3.5]], kind="beam"),
        "boat": item("items/ships/fisher-boat", (0.3, "0 - (F + 1.0) * 2.5 / Ls + 0.05", 0.5, 0), solid=False),
    }
    return component("boat-slip", "Boat slip", f"A BOAT SLIP: a hard of stone sloping from the quay into the water between its curbs, the apron at its head with the capstan the boats are wound up by, a fishing boat drawn up. {FRAME}", P, parts)


def fish_market():
    P = {"L": 14, "Dp": 8, "Hp": 3.4, "pitch": 28}
    posts = [[f"0 - L / 2 + L / 4 * {k}", 0.2, z, 0] for k in range(5) for z in ("0 - Dp / 2", "Dp / 2")]
    parts = {
        "market floor": prism({"rect": ["L + 1", "Dp + 1"]}, 0.2, (0, 0, 0), walked=True),
        "market posts": {"type": "column", "radius": 0.24, "height": "Hp", "sides": 8, "at": posts},
        "market beams": box("L + 0.4", 0.35, 0.4, (0, "0.2 + Hp", "0 - Dp / 2"), (0, "0.2 + Hp", "Dp / 2")),
        "market roof": roof("hip", "Dp + 0.4", "L + 0.4", "pitch", (0, "0.6 + Hp", 0, PI2), over=0.8),
        "fish tables": box(3.0, 1.0, 0.85, *[(f"0 - L / 2 + L / 4 * {k + 0.5}", 0.2, z) for k in range(4) for z in ("0 - 1.0", 1.0)], _about="stone tables, the catch laid out on them"),
        "catch": item("items/food/fish", *[(f"0 - L / 2 + L / 4 * {k + 0.5} + {dx}", 1.05, z + dz, a) for k in range(4) for z in (-1.0, 1.0) for dx, dz, a in ((-0.7, 0.1, 0.4), (0.2, -0.15, -0.3), (0.9, 0.12, 1.2))], solid=False),
        "baskets": item("items/tools/basket", *[(f"0 - L / 2 + L / 4 * {k + 0.5} - 1.1", 0.2, 2.0) for k in range(4)], solid=False),
        "sellers": marker("spot", *[(f"0 - L / 2 + L / 4 * {k + 0.5}", 0.2, 0, 0) for k in range(4)], pose="stand", work=1, gesture="lift"),
    }
    return component("fish-market", "Fish market", f"A FISH MARKET: an open hall on two rows of posts under a hipped roof, stone tables down the middle with the catch on them, baskets, the sellers' places (the fish halls of the Hanse towns, Venice's Pescheria, the Edo uoichi). {FRAME}", P, parts)


def customs_house():
    P = {"L": 16, "Dp": 10, "h0": 4.6, "h1": 3.8, "pitch": 30, "arch": "semicircular",
         "_arch": "the arcade's head: semicircular, pointed (the Mediterranean and Islamic ports), segmental"}
    arcade = {"every": 3.4, "width": 2.3, "end": 1.2, "sill": 0, "springing": 2.4, "head": {"profile": "arch"}, "glass": False,
              "_springing": "low enough for a pointed head to close under the floor"}
    win = every(3.4, 1.1, 1.0, 2.6, end=1.4)
    parts = {
        "office platform": prism({"rect": ["L + 0.8", "Dp + 0.8"]}, 0.3, (0, 0, 0), walked=True),
        "office walls": {"type": "enclosure", "plan": {"rect": ["L", "Dp"]}, "thickness": 0.6, "height": "h0 + h1", "glass": True, "openings": [],
                         "faces": {"0": [{"h": "h0", "openings": arcade}, {"openings": win}],
                                   "1": [{"h": "h0", "openings": [opening(0, 1.4, 0, 2.6, "semicircular", glass=False)]}, {"openings": win}],
                                   "2": [{"h": "h0", "openings": every(3.4, 1.0, 1.2, 2.8, end=1.4)}, {"openings": win}],
                                   "3": [{"h": "h0", "openings": every(3.4, 1.0, 1.2, 2.8, end=1.4)}, {"openings": win}]},
                         "at": [[0, 0.3, 0, 0]], "interior": True, "_about": "the arcade on the quay (the merchants' loggia, the weigh house), the clerks' rooms over it"},
        "office floor": box("L - 1.2", "Dp - 1.2", 0.3, (0, "0.3 + h0 - 0.3", 0)),
        "office cornice": prism({"rect": ["L + 0.5", "Dp + 0.5"]}, 0.35, (0, "0.3 + h0 + h1", 0)),
        "office roof": roof("hip", "Dp + 0.5", "L + 0.5", "pitch", (0, "0.65 + h0 + h1", 0, PI2), over=0.4),
        "door": marker("door", ("L / 2 - 0.3", 0.3, 0, PI2), w=1.4, h=2.6),
    }
    return component("customs-house", "Customs house", f"THE HARBOUR OFFICE (customs house, weigh house, the Hanse's Zollhaus, the Dogana): two storeys, an open arcade on the quay below (`arch` its head), the clerks' rooms above, a hipped roof; a door at the east end. {FRAME}", P, parts)


# ---- FINISHES, one per tradition: every piece's part names ----------------------------------------------------------
def R(parts, pattern, palette, **k): return {"parts": parts, "pattern": pattern, "palette": palette, **k}
TIMBER = ["fenders", "bulkhead", "quay piles", "cap beam", "quay deck", "pier deck", "pier stringers", "pier caps", "pier piles", "pier braces", "pier bollards",
          "crane jib", "crane jib strut", "crane wheel", "crane wheel treads", "crane wheel stand", "crane legs", "crane stakes", "crane block", "capstan", "capstan bars",
          "shed beams", "market posts", "market beams", "hoist beam", "gable hatches", "kura door", "speicher floors"]
IRON = ["mooring rings", "quay ladder", "pier ladder", "crane rope", "crane ropes", "crane hook", "hoist rope", "hoist hook", "lighthouse rail", "lighthouse rail posts", "crane tie", "crane post"]


def finish(key, name, about, stone, rules, borrow=()):
    """`borrow`: dwellings the layout sets on the quay (ports.json `land`) keep their own finish's rules, before the default"""
    for b in borrow:
        with open(os.path.join(FIN, b + ".json")) as f:
            rules = rules[:-1] + [r for r in json.load(f)["rules"] if r.get("parts")] + rules[-1:]
    write(os.path.join(FIN, key + ".json"), {"name": name, "building": "architecture/harbour/" + key, "_about": about, "stone": stone, "rules": rules})


def finishes():
    wood = lambda pal="oak-grey": R(TIMBER, "timber/bark", pal)
    iron = R(IRON, "stone/plaster", "iron")
    fire = R(["kind:glass"], "stone/plaster", "plaster-white")
    finish("greek-port", "Greek harbour", "limestone quays and moles, the stoa in marble and limestone under terracotta, timber cranes",
           {"color": "#d8cdb4", "accent": "#c4b79a", "pat": "ashlar"},
           [R(["store roof", "shed roofs", "market roof", "office roof"], "roofs/coppi", "terracotta", surface="roof"),
            R(["quay paving", "store platform", "office platform", "market floor", "slip apron"], "floors/flagstones", "limestone"),
            R(["mole mound", "mole head", "slip ramp", "slip curbs"], "stone/field rubble", "stone"),
            R(["store colonnade", "pharos lantern columns"], "stone/marble", "carrara"),
            R(["store walls", "office walls"], "stone/plaster", "plaster-white"),
            wood(), iron, R(["shed slips"], "timber/planks", "oak-grey"),
            R(["fish tables"], "stone/marble", "carrara"),
            {"pattern": "stone/ashlar", "palette": "limestone"}], borrow=["greek-house"])
    finish("roman-port", "Roman harbour", "travertine quays and rings, brick-faced concrete horrea and offices under red tiles, the pharos in stone",
           {"color": "#cfc2a8", "accent": "#b8a98c", "pat": "ashlar"},
           [R(["store roof", "office roof", "market roof", "shed roofs"], "roofs/coppi", "terracotta", surface="roof"),
            R(["quay paving", "store platform", "office platform", "market floor", "slip apron", "mole mound", "mole head"], "floors/flagstones", "travertine"),
            R(["store walls", "office walls", "store architrave"], "stone/brick", "roman-brick"),
            R(["store colonnade", "store piers"], "stone/travertine", "travertine"),
            R(["pharos square", "pharos octagon", "pharos drum", "pharos base"], "stone/ashlar", "limestone"),
            wood(), iron, R(["slip ramp", "slip curbs"], "stone/rubble", "stone"), R(["fish tables"], "stone/marble", "carrara"),
            {"pattern": "stone/travertine", "palette": "travertine"}])
    finish("hanse-port", "Hanseatic harbour", "timber bulwarks and piers, red brick warehouses and offices under red tile, the crane in stone",
           {"color": "#8b3122", "accent": "#6e2719", "pat": "brick"},
           [R(["speicher roof", "office roof", "market roof", "kura roof", "hoist hood", "crane jib hood"], "roofs/beaver tail", "tile-red", surface="roof"),
            R(["crane roof", "light turret cap"], "roofs/slate", "slate", surface="roof"),
            R(["quay paving", "office platform", "market floor", "slip apron"], "floors/sampietrini", "sampietrini"),
            R(["mole mound", "mole head", "slip ramp", "slip curbs", "quay wall", "quay coping", "water stair", "water stair landing"], "stone/rubble", "stone"),
            R(["speicher walls", "speicher gable", "office walls", "office cornice"], "stone/brick monk bond", "hanse-brick",
              _about="Luebeck's brick: deep red stretchers, the headers burnt near black, grey lime joints"),
            R(["crane tower", "light tower", "light tower corbels", "light tower parapet", "light turret", "crane eaves"], "stone/rubble long", "sandstone-grey"),
            wood("oak"), iron, R(["fish tables"], "stone/granite", "granite"),
            {"pattern": "stone/brick", "palette": "hanse-brick"}])
    finish("chinese-port", "Chinese harbour", "granite quays and steps, grey brick godowns with white walls under grey tube tiles, the beacon pagoda in brick",
           {"color": "#b9b4aa", "accent": "#9c978d", "pat": "ashlar"},
           [R(["kura roof", "kura ridge", "market roof", "lantern roof", "hoist hood"], "roofs/tube tiles", "slate", surface="roof"),
            R(["pagoda eaves 1", "pagoda eaves 2", "pagoda eaves 3", "pagoda eaves 4", "pagoda eaves 5", "pagoda eaves 6", "pagoda eaves 7", "pagoda spire"], "roofs/tube tiles", "slate"),
            R(["kura walls", "kura firewalls"], "stone/plaster", "plaster-white"),
            R(["kura skirt", "kura base", "pagoda shaft", "pagoda plinth"], "stone/brick", "stone"),
            R(["kura door", "pagoda door"], "timber/planks", "lacquer-black"),
            # the merchants' hall (components/chinese-hall, the office): grey tube tiles, red-lacquered timber, white plaster, painted beams
            R(["roof"], "roofs/tube tiles", "slate", surface="roof"),
            R(["roof"], "painted/caisson", "caihua", scale=0.5, _about="the eaves' soffits"),
            {"parts": ["ridge", "ridge beasts"], "color": "#5d6266", "accent": "#4b5054"},
            {"parts": "columns", "color": "#a3261e", "accent": "#861e17"},
            R(["walls"], "stone/plaster", "plaster-white"),
            R(["kind:glass"], "painted/lattice", "chinese-red"),
            R(["architrave"], "painted/caihua", "caihua", align="part"),
            {"parts": ["dou", "tongue 1", "tongue 2", "blocks 1", "blocks 2"], "color": "#3a7d68"},
            {"parts": ["arm 1", "arm 2", "arm 3", "beams"], "color": "#2f5f8f"},
            R(["platform", "front steps", "back steps"], "stone/granite", "granite"),
            R(["quay paving", "market floor", "slip apron"], "floors/flagstones", "granite"),
            R(["mole mound", "mole head", "slip ramp", "slip curbs"], "stone/field rubble", "stone"),
            wood("chestnut"), iron, R(["fish tables"], "stone/granite", "granite"),
            {"pattern": "stone/granite", "palette": "granite"}])
    finish("japanese-port", "Japanese harbour", "granite gangi steps and walls, white kura on namako skirts under kawara, the stone lantern",
           {"color": "#b8b2a6", "accent": "#9a948a", "pat": "ashlar"},
           [R(["kura roof", "kura ridge", "market roof"], "roofs/tube tiles", "kawara", surface="roof"),
            R(["kura walls"], "stone/plaster", "plaster-white"),
            R(["kura skirt"], "timber/shinkabe", "lacquer-black"),
            R(["kura door"], "stone/plaster", "plaster-white"),
            R(["kura base", "lantern base", "lantern base 2", "lantern stem", "lantern table", "lantern roof", "lantern jewel", "lantern firebox"], "stone/granite", "granite"),
            R(["quay paving", "market floor", "slip apron"], "floors/flagstones", "granite"),
            R(["mole mound", "mole head", "slip ramp", "slip curbs"], "stone/field rubble", "stone"),
            wood("pine"), iron, R(["fish tables"], "timber/planks", "pine"),
            {"pattern": "stone/granite", "palette": "granite"}], borrow=["minka"])
    finish("industrial-port", "Industrial harbour", "granite quays, brick warehouses under slate, iron cranes, the white lighthouse",
           {"color": "#8e4632", "accent": "#743828", "pat": "brick"},
           [R(["speicher roof", "office roof", "market roof", "hoist hood", "crane cab roof"], "roofs/slate", "slate", surface="roof"),
            R(["lantern dome", "lantern vent"], "roofs/sheet metal", "copper"),
            R(["lighthouse tower", "lighthouse watch room", "lighthouse door"], "stone/plaster", "plaster-white"),
            R(["lighthouse plinth", "lighthouse gallery", "crane pillar"], "stone/granite", "granite"),
            R(["speicher walls", "speicher gable", "office walls", "office cornice"], "stone/brick flemish", "munich-brick"),
            R(["quay paving", "office platform", "market floor", "slip apron"], "floors/sampietrini", "sampietrini"),
            R(["quay wall", "quay coping", "water stair", "water stair landing", "mole mound", "mole head", "mole parapet", "slip ramp", "slip curbs"], "stone/granite", "granite"),
            R(["crane jib", "crane cab"], "stone/plaster", "iron"),
            wood("oak"), iron, R(["fish tables"], "stone/marble", "marble-grey"),
            {"pattern": "stone/granite", "palette": "granite"}])
    finish("rustic-port", "Shore landing", "timber and thatch: the piers and slips of the Maya coast, the river ports of India and the villages",
           {"color": "#a08868", "accent": "#806a50", "pat": "wood"},
           [R(["market roof", "kura roof", "store roof", "office roof"], "roofs/thatch", "thatch", surface="roof"),
            R(["quay paving", "market floor", "slip apron", "store platform"], "stone/sand", "earth"),
            R(["quay steps", "quay steps ledge", "quay steps wall", "mole mound", "mole head", "slip ramp", "slip curbs"], "stone/ashlar", "sandstone"),
            R(["store walls", "kura walls", "office walls", "store piers", "store architrave"], "stone/plaster", "plaster-ochre"),
            wood("oak"), iron, R(["fish tables"], "timber/planks", "oak"),
            {"pattern": "stone/plaster", "palette": "plaster-ochre"}], borrow=["maya-house"])
    finish("mediterranean-port", "Mediterranean harbour", "the ports of Byzantium, the Ottomans and the Islamic world: ashlar quays, plastered offices and stores under pantiles, the light tower",
           {"color": "#d6c8a8", "accent": "#bfae8a", "pat": "ashlar"},
           [R(["store roof", "office roof", "market roof", "kura roof"], "roofs/coppi", "tile-red", surface="roof"),
            R(["crane roof", "light turret cap"], "roofs/sheet metal", "lead", surface="roof"),
            R(["store walls", "office walls", "store piers", "store architrave"], "stone/plaster", "plaster-white"),
            R(["quay paving", "office platform", "market floor", "slip apron", "store platform"], "floors/flagstones", "limestone"),
            R(["mole mound", "mole head", "slip ramp", "slip curbs"], "stone/rubble", "stone"),
            wood(), iron, R(["fish tables"], "stone/marble", "carrara"),
            {"pattern": "stone/ashlar", "palette": "sandstone"}])
    finish("nile-port", "Nile harbour", "Egypt's quays: sandstone walls and steps, ochre-plastered mud-brick stores and offices under flat plaster roofs",
           {"color": "#d2b98a", "accent": "#b89c6c", "pat": "ashlar"},
           [R(["store roof", "office roof", "market roof", "kura roof", "shed roofs"], "stone/plaster", "plaster-ochre", surface="roof"),
            R(["store walls", "office walls", "store piers", "store architrave", "kura walls", "office cornice"], "stone/plaster", "plaster-ochre"),
            R(["store colonnade"], "stone/ashlar", "sandstone"),
            R(["quay paving", "office platform", "market floor", "slip apron", "store platform"], "floors/flagstones", "sandstone"),
            R(["quay wall", "quay coping", "quay steps", "quay steps ledge", "quay steps wall", "water stair", "water stair landing",
               "mole mound", "mole head", "slip ramp", "slip curbs"], "stone/ashlar", "sandstone"),
            wood("oak"), iron, R(["fish tables"], "stone/ashlar", "sandstone"),
            {"pattern": "stone/ashlar", "palette": "sandstone"}], borrow=["egyptian-house"])


if __name__ == "__main__":
    for f in (quay, pier, mole, pharos, light_tower, lighthouse, stone_lantern, beacon_pagoda, horreum, speicher, kura,
              treadwheel_crane, polyspastos, jib_crane, ship_shed, boat_slip, fish_market, customs_house):
        f()
    finishes()
    print("harbour: 18 components, 9 finishes")
