# REGENSBURG CATHEDRAL (Dom St. Peter, 1275-1520; the spires 1859-69): the Gothic cathedral of notre_dame.py `gothic`
# with Regensburg's own numbers and the things that make it Regensburg --
#   * the STAGGERED CHEVET: no ambulatory, three polygonal choirs side by side, the main one a bay further east and
#     nearly all glass between deep buttresses (the `basilica` part's `ambulatory: false`, `chancelBays`, `sideApse`,
#     `choirWin`, `choirButtress`, `sideApsePitch` -- arch/gothic.js);
#   * the TRIANGULAR PORCH (Dreieckportal, c. 1410) before the main portal: a porch on a triangular plan, its tip on
#     one pillar, open in two arches under free-standing crocketed gables, a pierced parapet, a tall pinnacle over the
#     pillar (`components/triangle-porch`, written here: a parametric porch any Gothic front can take);
#   * the west towers' 19th-century crowns: an open octagon with gables and pinnacles and an OPENWORK spire on each,
#     105 m (gothic()'s `spire` with an `octagon`); the copper-green Dachreiter on the crossing; and on the north side,
#     west of the north transept front, the Romanesque ESELSTURM left from the old cathedral.
# The building is pale Kelheim limestone with greensand blocks among it (`stone/ashlar two stones`, palette
# `regensburg`), the steep roofs red-brown plain tile. This file writes the finish too (assets/finishes/regensburg.json).
#
# Axes as notre_dame.py: +z is WEST (the front), -z the liturgical east (the choirs), -x NORTH (the Eselsturm), +x south.
# SOURCED (de.wikipedia, Dom St. Peter): inside 85.40 m long, 34.80 m wide, the nave 31.85 m to the vault, the towers
#   105 m; five nave bays (the first under the towers); a transept that does not project; three staggered choirs, no
#   ambulatory; the porch on a triangular plan on a central pillar; the Eselsturm on the north side, part of the north
#   transept front. FROM THE PHOTOGRAPH (en.wikipedia lead, from the Danube): red-brown tiled roofs, the green Dachreiter,
#   the Eselsturm west of the north transept front.
# ESTIMATED (from photographs, not measured): bay length 8.5 (so 9 bays + the apse make the 85 m), the widths' split
#   (nave 14.0, aisles 8.8 -- they sum to the sourced 34.8), the springings (tuned so the vault's crown is ~32),
#   roof pitch 58, the towers' square stages to 52 m, the octagon 15 m, the spire 35 m; the porch 11.2 m wide,
#   6 m deep, its arches' wall 9.3 m, its gables to ~14 m; the Eselsturm 8.5 m square, 33 m.
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notre_dame import gothic, NOTRE_DAME, ROOT
COMP = os.path.join(ROOT, "assets/architecture/components")

# ================================================================ L1: the triangle porch (reusable)
TRIANGLE_PORCH = {
  "name": "Triangle porch",
  "_about": ("A PORCH ON A TRIANGULAR PLAN before a portal (Regensburg's Dreieckportal, c. 1410): its back is the wall it "
             "stands against (from x = -half to half on z = 0), its tip `depth` out on +z, where ONE PILLAR carries the two "
             "front faces. Each face is a wall `w` long, open in a pointed arch (`pier` of wall either side, springing at "
             "`spring`) and only `h` high -- just over the arch's crown; over it a crocketed GABLE (wimperg) stands FREE, its "
             "tracery open to the sky, up to `gableTop` at most (steeper or flatter by `pitch`). A slab closes the porch at "
             "`h`, a pierced parapet runs along the faces' heads behind the gables, pinnacles stand on its back corners and "
             "a tall one over the pillar. `w` and `yaw` (the faces' length and turn) follow from half and depth. Place it "
             "with its back on the wall's face, facing +z."),
  "params": {"detail": 4, "half": 5.6, "depth": 6.0, "w": "sqrt(half * half + depth * depth)", "yaw": "atan2(depth, half)",
             "t": 0.9, "pier": 1.4, "spring": 3.5, "h": "spring + (w - 2 * pier) * 0.866 + 1.1", "gableTop": "h + 5.5",
             "pitch": 66, "pierR": 0.9, "slab": 0.6, "crest": 1.1,
             "pinW": 1.1, "pinH": 2.6, "pinS": 4.2, "tipW": 1.4, "tipH": 5.5, "tipS": 6.5,
             "_yaw": "the right face's turn (a yaw turns +x towards -z); the left one's is its negative",
             "_h": "the faces' walls: just over the arches' crowns (an equilateral arch rises 0.866 of its width)",
             "_gableTop": "the most the gables may rise to: wimperg.js flattens a gable that would rise higher, and drops one it cannot fit",
             "_tipW": "the pinnacle over the pillar (tipW, tipH, tipS); pinW, pinH, pinS the back corners'"},
  "build": ["faces", "pillar", "slab", "parapet", "corner pinnacles", "tip pinnacle"],
  "parts": {
    "faces": {"type": "wall", "width": "w", "height": "h", "thickness": "t", "glass": False,
              "openings": [{"at": "w / 2", "width": "w - 2 * pier", "sill": 0, "springing": "spring", "head": {"profile": "pointed", "spread": 1.0},
                            "wimperg": {"pitch": "pitch", "coping": 0.4, "depth": 0.3, "top": "gableTop"}}],
              "at": [["0 - half / 2", 0, "depth / 2", "0 - yaw"], ["half / 2", 0, "depth / 2", "yaw"]],
              "_about": "the two front faces, each open in a pointed arch under its free-standing gable (their outer faces on the triangle's sides)"},
    "pillar": {"type": "column", "radius": "pierR", "height": "h", "sides": 8, "at": [[0, 0, "depth - pierR * 0.7", 0]],
               "_about": "the one pillar at the tip, which both arches spring from"},
    "slab": {"type": "prism", "plan": {"points": [["0 - half", 0], ["half", 0], [0, "depth"]]}, "height": "slab", "at": [[0, "h - slab", 0, 0]],
             "_about": "the porch's head: a slab over its vault, the faces' tops"},
    "parapet": {"type": "cresting", "run": [["0 - w / 2", 0], ["w / 2", 0]], "h": "crest", "panel": 1.2, "t": 0.25, "every": 2, "spirelet": {"w": 0.18, "s": 0.8},
                "at": [["0 - half / 2 + sin(yaw) * t / 2", "h", "depth / 2 - cos(yaw) * t / 2", "0 - yaw"], ["half / 2 - sin(yaw) * t / 2", "h", "depth / 2 - cos(yaw) * t / 2", "yaw"]],
                "_about": "a pierced parapet along each face's head, on the wall behind its gable"},
    "corner pinnacles": {"type": "component", "use": "components/pinnacle", "params": {"w": "pinW", "h": "pinH", "s": "pinS"},
                         "at": [["0 - half + pinW / 2", "h", "pinW / 2", 0], ["half - pinW / 2", "h", "pinW / 2", 0]]},
    "tip pinnacle": {"type": "component", "use": "components/pinnacle", "params": {"w": "tipW", "h": "tipH", "s": "tipS"},
                     "at": [[0, "h", "depth - tipW * 0.6", 0]], "_about": "the tall pinnacle over the pillar"}}}
open(os.path.join(COMP, "triangle-porch.json"), "w").write(json.dumps(TRIANGLE_PORCH, indent=2) + "\n")

# ================================================================ L3: Regensburg's numbers
tall = lambda w, sill, spring, lights, **k: {"at": 0, "width": w, "sill": sill, "springing": spring, "head": {"profile": "pointed", "spread": 0.9}, "tracery": lights, **k}
P = {**NOTRE_DAME, "bays": 9, "bayLen": 8.5, "naveW": 14.0, "aisleW": 8.8, "pierT": 1.6, "aisleT": 1.6,
     "spring": 7.0, "arcadeH": 17.0, "clearH": 31.85, "frontH": 38.0, "towerW": 12.4, "towerH": 14.0, "roofPitch": 58,
     "towerBays": 1, "crossA": 5, "arm": 0.0, "clerSpring": 3.7, "flyerStages": 1, "portalGables": True,
     # THE THREE CHOIRS: the main choir one bay past the side choirs and closed in five sides of an octagon, its windows
     # 0.95 of each bay's clear width between buttresses 3.2 m deep; each side choir (the aisle run on east of the
     # crossing) closed in three under a 50-degree roof; the transept fronts with tall windows, no roses
     "ambulatory": False, "chancelBays": 1, "sideApse": 3, "transeptRose": False, "choirWin": 0.95, "choirButtress": 3.2, "sideApsePitch": 50,
     "front": {"h": [16, 14], "portal": [6.0, 5.5], "sidePortal": [4.4, 5.0], "towerOut": 0.5,
               "mid": tall(7.6, 1.5, 7.0, 4),
               # (the towers' upper stages: tall traceried windows, under gables in the first)
               "towerMid": tall(5.6, 1.2, 6.8, 3, wimperg={"pitch": 62, "coping": 0.35, "depth": 0.3}),
               "gallery": {"pattern": "5", "width": 1.2, "gap": 0.7, "pier": 0.7, "sill": 1.6, "springing": 4.2, "head": {"profile": "pointed", "spread": 1.0}},
               "towerGallery": [tall(4.6, 0.8, 3.6, 2)], "towerSide": [tall(4.6, 0.8, 3.6, 2)],
               "belfry": {"width": 3.0, "gap": 1.5, "pier": 1.6, "wimperg": {"pitch": 62, "coping": 0.3, "depth": 0.3}},
               "buttress": [[0, 16, 2.4], [16, 38, 1.6], [38, 52, 1.0]], "courses": [16.0, 30.0, 38.0], "gable": 10.0,
               "doors": {"below": 1.0}}}
# THE TOWERS' CROWNS (Denzinger, 1859-69): an open octagon on each square tower, gables and pinnacles at the spire's
# foot, the spire itself OPENWORK to 105 m, and a pinnacle on each corner of the square tower's head
SPIRE = {"octagon": {"R": 5.8, "H": 15.0, "t": 0.8, "low": 3.0, "lights": 2},
         "feet": {"R": 5.5, "rise": 35.0, "pinR": 5.9, "pinW": 0.9, "pinH": 2.6, "pinS": 4.6},
         "open": {"R": 5.5, "rise": 34.5, "topR": 0.4, "rows": 9, "rib": 0.4, "bar": 0.15, "finial": 3.0},
         "pinnacles": {"w": 1.5, "h": 4.0, "s": 6.5}}

def more(add, P_, A):
  # ---- THE TRIANGLE PORCH before the main portal, its back on the west front's face
  add("porch", {"type": "component", "use": "components/triangle-porch", "params": {"half": 5.6, "depth": 6.0}, "at": [[0, 0, A["front"], 0]],
                "_about": "the TRIANGULAR PORCH (Dreieckportal, c. 1410) before the main portal: its tip on one pillar, open in two arches under free-standing gables (`triangle-porch`)"})
  # ---- THE ESELSTURM: the Romanesque tower of the old cathedral, on the north side just west of the north transept
  # front, against the aisle -- plain ashlar, small round-headed openings, paired ones at the top, a steep tiled pyramid
  EW, EH = 8.5, 33.0
  at = [[f"0 - ({A['bodyW']} / 2 + {EW / 2 - 0.6})", 0, f"{A['crossW']} - 0.25", 0]]
  lights = lambda pat, w, gap, sill, spring: {"pattern": pat, "width": w, "gap": gap, "pier": 1.2, "sill": sill, "springing": spring, "head": {"profile": "semicircular"}}
  add("eselsturm", {"type": "enclosure", "plan": {"rect": [EW, EW]}, "thickness": 1.4, "height": EH, "glass": False,
                    "tiers": [{"h": 13.0, "openings": []}, {"h": 7.0, "openings": lights("1", 0.8, 0, 3.0, 4.6)},
                              {"h": 6.5, "openings": lights("1", 0.9, 0, 2.6, 4.4)}, {"h": 6.5, "openings": lights("2", 1.0, 0.45, 2.2, 4.4)}],
                    "courses": True, "at": at,
                    "_about": "the ESELSTURM, the Romanesque tower left from the old cathedral, west of the north transept front: small round-headed openings, paired at the top"})
  add("eselsturm roof", {"type": "dome", "sides": 4, "radius": round((EW + 0.6) * 0.7071, 4), "thickness": 0, "head": {"profile": "trigonal", "rise": 7.0},
                         "at": [[at[0][0], EH, at[0][2], 0]], "_about": "its steep tiled pyramid roof"})
  # ---- THE DACHREITER (1872, instead of the crossing tower never built): a slender lantern and spire on the ridge
  # over the crossing, copper-clad -- the `domed-tower` as Notre-Dame's fleche, far smaller, sunk into the ridge as far
  # as its lantern's corners reach down the roof's slope (1.6 * tan 58 = 2.6 m)
  add("dachreiter", {"type": "component", "use": "components/domed-tower",
                     "params": {"sides": 8, "R": 1.6, "H": 5.0, "t": 0.25, "cap": "trigonal", "capRise": 13, "capR": 1.8, "drumR": 1.3, "drumH": 1.6,
                                "kok": 0.2, "finial": 1.6, "glazed": 0},
                     "build": ["tower", "drum", "cap", "finial"], "atop": "church", "atopLevel": "ridge", "at": [[0, -3.2, A["zCross"], 0]],
                     "_about": "the Dachreiter over the crossing: a small open lantern and its spire, copper (`domed-tower`)"})

gothic("regensburg", "Regensburg Cathedral",
       "REGENSBURG CATHEDRAL (Dom St. Peter) from the same components as Notre-Dame (the `gothic` generator): the `basilica` nave of five bays, 31.85 m to the vault, rib-vaulted on compound piers, flyers down the flanks; a transept that does not project; and no ambulatory but THREE STAGGERED CHOIRS, the main one a bay further east, nearly all glass between deep buttresses, each closed in a polygon; the west front between two towers, the great traceried window over the main portal and before it the TRIANGULAR PORCH on its one pillar under free-standing gables (`triangle-porch`); the towers' open octagons and openwork spires to 105 m; the copper Dachreiter over the crossing; and west of the north transept front the Romanesque Eselsturm. Pale limestone patched with greensand under red-brown tiled roofs.",
       P, spire=SPIRE, fleche=False, more=more)

# ================================================================ the finish
GLASS = [("tall", 6, ["saint peter", "medallion stack", "saint bishop", "medallion story", "saint virgin", "saint martyr"]),
         ("short", 2, ["medallion annunciation", "medallion majesty"])]
FINISH = {
  "name": "Regensburg Cathedral", "building": "architecture/regensburg",
  "_about": "Regensburg Cathedral (written by tools/archgen/regensburg.py): pale Kelheim limestone with greensand blocks scattered through it (stone/ashlar two stones, palette regensburg), as cleaned of its black crust after 1985; the steep roofs in red-brown plain tile (fish scale, the nearest to beaver-tails), the Eselsturm's pyramid too; the Dachreiter in copper gone green; the Romanesque Eselsturm in plain ashlar of the same limestone; the medieval stained glass; inside, the limestone and a flagstone floor.",
  "stone": {"color": "#d3cbb5", "accent": "#bbbaa2", "pat": "ashlar"},
  "rules": [{"parts": "kind:glass", "opening": "head", "map": "opening", "pattern": "glass/tracery diaper", "palette": "cologne"}]
         + [{"parts": "kind:glass", "opening": op, "nth": [n, i], "map": "opening", **({"turn": 90} if op == "tall" else {}), "pattern": f"glass/{g}", "palette": "cologne"}
            for op, n, gs in GLASS for i, g in enumerate(gs)]
         + [{"parts": "kind:glass", "pattern": "painted/stained glass", "palette": "stained", "_about": "the windows' stained glass"},
            {"parts": ["dachreiter"], "pattern": "roofs/sheet metal", "palette": "copper", "_about": "the Dachreiter: copper, gone green"},
            {"parts": ["eselsturm roof"], "pattern": "roofs/fish scale", "palette": "tile-brown", "_about": "the Eselsturm's pyramid: plain tile"},
            {"parts": "kind:roof", "surface": "roof", "pattern": "roofs/fish scale", "palette": "tile-red", "_about": "the steep roofs and the side choirs' half cones: red-brown plain tile"},
            {"parts": ["eselsturm"], "pattern": "stone/ashlar", "palette": "regensburg", "_about": "the Romanesque Eselsturm: plain ashlar of the same limestone, without the Gothic builders' greensand"},
            {"parts": "kind:dome", "surface": "roof", "pattern": "stone/ashlar fine", "palette": "regensburg", "_about": "the pinnacles' and spirelets' stone caps"},
            {"surface": "floor", "side": "in", "pattern": "floors/flagstones", "palette": "limestone"},
            {"surface": "floor", "pattern": "floors/flagstones", "palette": "granite"},
            {"surface": "wall", "side": "in", "pattern": "stone/ashlar", "palette": "limestone", "_about": "inside: the limestone (whitewashed in the Middle Ages, ochre and olive-grey since)"},
            {"surface": "wall", "pattern": "stone/ashlar two stones", "palette": "regensburg", "_about": "outside: limestone patched with greensand"},
            {"side": "in", "pattern": "stone/ashlar", "palette": "limestone", "_about": "the vaults' webs and ribs inside"},
            {"pattern": "stone/ashlar two stones", "palette": "regensburg", "_about": "the rest -- pinnacles, mouldings, spires -- in the same two stones"}]}
open(os.path.join(ROOT, "assets/finishes/regensburg.json"), "w").write(json.dumps(FINISH, indent=2) + "\n")
