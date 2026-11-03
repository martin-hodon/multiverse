# BYODO-IN, the PHOENIX HALL (Hoo-do, the Amida Hall of 1053), Uji: the hall on its island in the Aji pond, facing EAST across the water
# to where the Western Paradise is seen from -- the central hall, the two wing corridors spread either side, the tail corridor behind:
# a bird with outstretched wings and a tail, the pair of phoenixes on the ridge.
#   THE CENTRAL HALL (chudo): a core (moya) of 3 x 2 bays under a hip-and-gable roof, ringed by a one-bay pent skirt (mokoshi) on every
#   side, so that it looks two-storeyed though it is one; no aisle (hisashi) between them. The mokoshi is open on the east, north and
#   south (posts, no walls), walled behind with a double door in its middle bay; the moya's front three bays and its sides' front bays
#   are double plank doors, its sides' back bays slat windows (renji-mado), its back middle bay a solid wall behind the Amida and the
#   back side bays open. A railing (koran) runs round the moya on top of the skirt -- not for use. The main roof reaches out past the
#   skirt's eave and past the platform. On its stone platform (dan-jo-zumi kidan).
#   Here: a `tiered` part of two storeys -- the first the mokoshi line, its faces' own bays (`faces`: the wide middle bay), a railing on
#   its skirt (`rail`); the second the moya over the skirt -- and the moya's own walls below, inside, with its doors and windows (`chudo
#   moya`). The front's middle bay of the skirt is lifted (kiri-age, tiered's `lift`: the skirt cut open, a roof of its own higher up)
#   so the Amida's face is seen from across the pond through the fan-shaped window in the moya's middle bay.
#   THE WING CORRIDORS (yokuro), north and south alike: L-shaped, 8 bays folded (counted round the outside), one bay deep, two storeys
#   under a gable roof -- the ground storey open between its posts, no floor; the upper one too low to stand in, a railed balcony round
#   it -- running out from the hall's sides and turning EAST, toward the pond, at a CORNER TOWER (sumi-ro): a third storey there, 3 x 3
#   bays under a pyramid roof (hogyo) with a tile jewel, a door in the middle bay of each side, slat windows either side.
#   (japanese.corridor_wing, one folded line a wing; the towers' third storeys `tiered` on the corridor's roof at the fold.)
#   THE TAIL CORRIDOR (biro): one storey, gabled, 7 bays by 1, straight back west from the hall's back skirt: a sliding door in the first
#   bay, bell-headed windows (katomado) in the second, third, sixth and seventh, lattice in the fourth and fifth -- crossing the pond on
#   its fifth and sixth bays, a post in the water between them, to the land behind.
#   THE POND (Aji-ike): a `pool` with a `shore` and the island one of its `islands` -- the water all round, a channel behind; the island
#   barely more than the buildings, its edge a beach of pebbles (suhama) sloping in (a battered prism); a plank bridge from the north bank
#   (the real island has two).
#   THE PHOENIXES: components/phoenix (japanese.py), gilt (as regilded in 2014), on round pedestals, their tails swept up, one on each
#   end of the ridge facing outward -- tiered's `top.ridgeEnds`; the towers' jewels the same way (components/hoju).
# SOURCED (Japanese Wikipedia, 平等院): the bay counts -- moya 3 x 2, mokoshi one bay all round, yokuro 8 bays folded x 1, towers'
#   third storey 3 x 3, biro 7 x 1; which bays are doors, windows, open; the moya's columns 2 shaku (60 cm), the mokoshi's 8.5 sun (27 cm);
#   the front middle bay of the skirt lifted; the main roof's eave past the skirt's and the platform's; the phoenixes ~2.3 m overall,
#   the birds ~1 m. ESTIMATED (no published metres found): every length and height -- the hall about 14 x 11.6 m, the whole about
#   41 m north to south, the ridge about 12.5 m over the platform; the bay widths; the pond's size and shape (far smaller than the real).
#   East is +x (the front), south is +z. Numbers are worked here and written as numbers.
import os, json, math
import japanese as J
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
r4 = lambda v: round(v, 4)
Q = math.pi / 2

# ---- the central hall ------------------------------------------------------------------------------------------------
G = .3                                   # the island's top: everything stands on it
MW, ML = 7.4, 9.9                        # the moya: 2 bays deep (x) 3.7 + 3.7, 3 bays across the front (z) 3.0 + 3.9 + 3.0
MOK = 2.1                                # the mokoshi's one bay
SW, SL = MW + 2 * MOK, ML + 2 * MOK      # the skirt's line: 11.6 x 14.1
KH = .75                                 # the stone platform
KW, KL = SW + 2.2, SL + 2.2              # (it runs out past the skirt's posts, under the cut-plank veranda)
YH = G + KH                              # the hall's floor
H1, H2 = 4.0, 4.1                        # the skirt storey to its wall head; the moya over it
SKIRT = {"pitch": 24, "overhang": 1.5, "lo": .35, "hi": 1.0, "upturn": .25, "flare": .2}
BRK = {"s": .5, "every": 1.4}
J.phoenix_component(); J.hoju_component()
TOPR = {"form": "gablet", "pitch": 31, "overhang": 3.1, "hipH": .5,
        "ridgeEnds": {"use": "components/phoenix", "params": {"s": 1.15, "bw": .5, "bh": .45, "pedestal": "disc", "tail_rise": .45}, "inset": .3}}

add("platform", {"type": "prism", "plan": {"rect": [KW, KL]}, "height": KH, "walked": True, "at": [[0, G, 0, 0]],
                 "courses": [{"y": r4(KH - .14), "h": .14, "out": .06, "profile": "band"}],
                 "_about": "the stone platform (dan-jo-zumi kidan): kerb, panels, posts and coping stone"})
n = 4
add("platform steps", {"type": "flight", "width": 3.0, "run": .3, "rise": r4(KH / n), "top": KH, "base": 0, "landing": 0,
                       "at": [[r4(SW / 2 + 1.1 + n * .3), G, -1.5, Q * 2]], "_about": "the steps up the front, at the middle bay"})

# the skirt's bays: the front 2.1 | 3.0 | 3.9 | 3.0 | 2.1 (the moya's three and a skirt bay each side), the sides 2.1 | 3.7 | 3.7 | 2.1;
# open between the posts on the front and sides; the back walled, a double door in its middle bay into the tail corridor
POST = .3
def bays(widths, sill=0, springing=2.8, **kw):
    x, out = -sum(widths) / 2, []
    for w in widths:
        out.append({"at": r4(x + w / 2), "width": r4(w - POST), "sill": sill, "springing": springing, "head": {"profile": "flat"}, "glass": False, **kw})
        x += w
    return out
FRONT, SIDE = [MOK, 3.0, 3.9, 3.0, MOK], [MOK, 3.7, 3.7, MOK]
skirt_faces = {"1": bays(FRONT), "0": bays(SIDE), "2": bays(SIDE),
               "3": [{"at": 0, "width": 2.4, "sill": 0, "springing": 2.6, "head": {"profile": "flat"}, "glass": False}]}
# the moya's front middle bay over the skirt: a lattice either side of the fan-shaped window (gunbai) the Amida's face is seen through
gunbai = [{"at": -1.3, "width": .9, "sill": .25, "springing": 1.25, "head": {"profile": "flat"}, "glass": True},
          {"at": 0, "width": 1.0, "sill": .3, "springing": .9, "head": {"profile": "horseshoe"}, "glass": False},
          {"at": 1.3, "width": .9, "sill": .25, "springing": 1.25, "head": {"profile": "flat"}, "glass": True}]
add("chudo", {"type": "tiered", "storeys": [{"w": SW, "l": SL, "h": H1, "windows": False, "faces": skirt_faces,
                                             "lift": {"side": "e", "at": 0, "width": 3.9 + .24, "dy": 1.5, "pitch": 14},
                                             "rail": {"out": .6, "h": .7, "every": 1.25, "w": .08}},
                                            {"w": MW, "l": ML, "h": H2, "windows": False, "faces": {"1": gunbai}}],
              "wall": {"t": POST}, "roof": SKIRT, "top": TOPR, "floors": False, "brackets": BRK,
              "at": [[0, YH, 0, 0]],
              "_about": "the central hall: the skirt (mokoshi) a bay round the core, open between its posts on the front and sides, walled behind, its pent roof up to "
                        "the core's walls, a railing (koran) round the core on it, its front middle bay lifted (kiri-age); the core (moya) under the hip-and-gable "
                        "roof that reaches out past the skirt, the fan-shaped window in its front middle bay, the phoenixes on the ridge's ends (top.ridgeEnds)"})

# the moya's own walls, inside the skirt, from the platform up to the core storey: its doors and windows
DOOR = lambda at, w: {"at": at, "width": w, "sill": 0, "springing": 3.1, "head": {"profile": "flat"}, "glass": False}
WIN = lambda at: {"at": at, "width": 2.6, "sill": 1.1, "springing": 3.0, "head": {"profile": "flat"}, "glass": True}
add("chudo moya", {"type": "enclosure", "plan": {"rect": [MW, ML]}, "thickness": .3, "height": H1, "glass": False,
                   "faces": {"1": [DOOR(-3.45, 2.4), DOOR(0, 3.1), DOOR(3.45, 2.4)],
                             "0": [DOOR(1.85, 2.4), WIN(-1.85)], "2": [DOOR(-1.85, 2.4), WIN(1.85)],
                             "3": [DOOR(-3.45, 2.6), DOOR(3.45, 2.6)]},
                   "at": [[0, YH, 0, 0]],
                   "_about": "the core's walls below the skirt roof: three double plank doors on the front, a door and a slat window on each side; "
                             "behind, the middle bay a solid wall (butsugo-heki, behind the Amida) and the two side bays open"})
add("chudo floor", {"type": "box", "width": r4(SW - .3), "length": r4(SL - .3), "height": .12, "walked": True, "at": [[0, YH, 0, 0]],
                    "_about": "the board floor inside and the cut-plank veranda (kirime-en) under the open skirt"})

# ---- the wing corridors and their corner towers ------------------------------------------------------------------------
B, D = 3.3, 3.3                          # a bay along the wing, its depth (one bay)
XL = 2.0                                 # the wings' cross legs' middle line: forward of the hall's middle
ZT = SL / 2 + 3 * B + D / 2              # the corner towers' middle: 3 bays out from the skirt's side, then the tower's bay
XF = XL + D / 2 + 3 * B                  # the forward legs' east ends: 3 bays on from the tower toward the pond
WH1, WH2, WF = 3.3, 1.8, .25             # the wing's open ground storey, its low upper storey, the floor between
WROOF = {"pitch": 27, "overhang": 1.1, "shell": .28, "ends": "gable"}
renji = {"every": B, "width": 2.0, "end": .6, "sill": .4, "springing": 1.25,   # (its lintel kept under the roof's eave, which starts at the wall head)
         "head": {"profile": "flat"}, "glass": True}
passage = {"at": 0, "width": r4(D - .5), "sill": 0, "springing": r4(WH1 - .35), "head": {"profile": "flat"}, "glass": False}
TW, TH = 2.7, 3.4                        # the tower's third storey: 3 x 3 bays of .9, on the corridor's roof at the fold
tbay = [{"at": -.9, "width": .55, "sill": 1.3, "springing": 2.6, "head": {"profile": "flat"}, "glass": True},
        {"at": 0, "width": .66, "sill": .95, "springing": 2.6, "head": {"profile": "flat"}, "glass": False},
        {"at": .9, "width": .55, "sill": 1.3, "springing": 2.6, "head": {"profile": "flat"}, "glass": True}]
for s, side in ((-1, "north"), (1, "south")):
    yW = J.corridor_wing(add, f"{side} wing", [[XL, r4(s * SL / 2)], [XL, r4(s * ZT)], [r4(XF), r4(s * ZT)]], D, WH1, WH2, B,
                         floor=WF, upper=renji, roof=WROOF, ends=[passage], side="right" if s < 0 else "left", y=G,
                         about=f"the {side} wing corridor (yokuro): out from the hall's side, then turned east toward the pond at the corner tower -- "
                               "open below between its posts, the low upper storey with its slat windows behind a railed balcony, under a gable roof")
    add(f"{side} tower", {"type": "tiered", "storeys": [{"w": TW, "l": TW, "h": TH, "windows": False, "faces": {str(f): tbay for f in range(4)}}],
                          "wall": {"t": .18}, "roof": {"pitch": 26, "overhang": 1.25, "lo": .35, "hi": 1.0, "upturn": .3, "flare": .2},
                          "top": {"form": "hip", "pitch": 30, "overhang": 1.25, "ridgeEnds": {"use": "components/hoju", "params": {"s": .7}}}, "floors": False,
                          "at": [[XL, r4(yW - .05), r4(s * ZT), 0]],
                          "_about": f"the {side} corner tower (sumi-ro): its third storey of 3 x 3 bays on the corridor's roof at the fold -- a plank door in the "
                                    "middle bay of each side, slat windows either side -- under a pyramid roof (hogyo) and its jewel (components/hoju)"})

# ---- the tail corridor -----------------------------------------------------------------------------------------------
# seven bays straight back west, CROSSING the pond on its fifth and sixth (a post in the water between them) to the land behind
TB = 2.4
TX0 = -SW / 2
XS, XW = -15.6, -20.0                    # the island's west tip, the far bank
def tail_face(sg):
    # bay 1 (by the hall) a sliding door, 2, 3, 6, 7 bell-headed windows (katomado), 4, 5 lattice; `at` from the face's middle
    out = []
    for j in range(1, 8):
        at = r4(sg * (1.2 + (j - 1) * TB - 3.5 * TB))
        if j == 1: out.append({"at": at, "width": 1.4, "sill": 0, "springing": 2.3, "head": {"profile": "flat"}, "glass": False})
        elif j in (4, 5): out.append({"at": at, "width": 1.7, "sill": .75, "springing": 2.2, "head": {"profile": "flat"}, "glass": True})
        else: out.append({"at": at, "width": 1.0, "sill": .85, "springing": 1.75, "head": {"profile": "bell"}, "glass": True})
    return out
add("tail corridor", {"type": "range", "path": [[r4(TX0), 0], [r4(TX0 - 7 * TB), 0]], "width": 2.7, "height": 3.1, "thickness": .22, "interior": False,
                      "faces": {"out": tail_face(1), "in": tail_face(-1), "end:0": [{"at": 0, "width": 2.2, "sill": 0, "springing": 2.4, "head": {"profile": "flat"}, "glass": False}], "end:1": []},
                      "walk": False, "roof": {"pitch": 26, "overhang": .9, "shell": .25, "ends": "gable"}, "at": [[0, YH, 0, 0]],
                      "_about": "the tail corridor (biro): one storey, gabled, seven bays straight back west from the hall's back skirt -- a sliding door, bell-headed "
                                "windows (katomado), lattice -- over the water on its fifth and sixth bays"})
add("tail floor", {"type": "box", "width": r4(7 * TB), "length": 2.5, "height": .12, "walked": True, "at": [[r4(TX0 - 3.5 * TB), YH, 0, 0]]})
add("tail platform", {"type": "prism", "plan": {"rect": [r4(TX0 - XS), 3.4]}, "height": KH, "at": [[r4((TX0 + XS) / 2), G, 0, 0]],
                      "_about": "the corridor's stone platform on the island"})
add("tail landing", {"type": "prism", "plan": {"rect": [r4(XW - (TX0 - 7 * TB) + .3), 3.4]}, "height": YH, "at": [[r4((XW + TX0 - 7 * TB - .3) / 2), 0, 0, 0]],
                     "_about": "its stone platform on the far bank"})
add("tail piles", {"type": "box", "width": .32, "length": .32, "height": r4(YH + 2.6),
                   "at": [[x, -2.6, z, 0] for x in (r4(TX0 - 5 * TB),) for z in (-1.1, 1.1)],
                   "_about": "the posts standing in the water under the corridor, between its fifth and sixth bays"})
add("tail beams", {"type": "box", "width": r4(XS - XW + 1.0), "length": .3, "height": .3, "at": [[r4((XS + XW) / 2), r4(YH - .3), z, 0] for z in (-1.1, 1.1)],
                   "_about": "the beams carrying the floor over the water, from bank to bank on the posts"})

# ---- the island, the bridge and the pond ------------------------------------------------------------------------------------
# the island: barely more than the buildings and their eaves -- the wings' gable ends on the water's edge -- the tail corridor's
# strip running back to its west tip; its edge a pebble beach (suhama) sloping into the pond, the water all round it
ISLAND = [(14.5, -23.6), (14.5, -14.8), (11.0, -12.2), (10.4, -6.0), (10.6, 0.0), (10.4, 6.0), (11.0, 12.2), (14.5, 14.8), (14.5, 23.6),
          (-3.8, 23.6), (-3.8, 11.2), (-9.8, 10.2), (-9.8, 3.0), (XS, 3.0), (XS, -3.0), (-9.8, -3.0), (-9.8, -10.2), (-3.8, -11.2), (-3.8, -23.6)]
add("island", {"type": "prism", "plan": {"points": [[x, z] for x, z in ISLAND]}, "height": 1.1, "batter": {"out": 2.5}, "walked": True,
               "at": [[0, r4(G - 1.1), 0, 0]], "_about": "the island under the hall: its edge the pebble beach (suhama) sloping into the pond"})
# the pond: in front, round the sides and behind, the far bank west of the island a channel's width away
OUTER = [(XW, -31.0), (-6.0, -31.8), (8.0, -31.5), (20.0, -33.0), (31.0, -37.5), (43.0, -36.5), (50.0, -26.0), (51.5, -8.0), (51.0, 10.0),
         (49.0, 27.0), (41.0, 37.0), (29.0, 37.8), (19.0, 32.5), (8.0, 31.5), (-6.0, 31.8), (XW, 31.0), (XW - .6, 16.0), (XW, 0.0), (XW - .6, -16.0)]
PX, PHW, PHD = 15.5, 36.5, 38.5          # the pond's rectangle: its middle east of the hall, its half sizes
# the bridge from the north bank to the island, by the north wing (the real island is reached by two from the north)
BX, BZ0, BZ1 = 6.0, -23.2, -32.2
add("north bridge", {"type": "box", "width": 2.0, "length": r4(BZ0 - BZ1), "height": .2, "walked": True, "at": [[BX, r4(G + .05), r4((BZ0 + BZ1) / 2), 0]],
                     "_about": "a plank bridge from the north bank to the island"})
add("north bridge piles", {"type": "box", "width": .25, "length": .25, "height": r4(G + .05 + 2.6),
                           "at": [[r4(BX + e), -2.6, z, 0] for e in (-.85, .85) for z in (-25.8, -28.4, -30.6)]})
J.rail_path(add, "north bridge rail 1", [(BX - .92, BZ0), (BX - .92, BZ1)], r4(G + .25), .75, posts=1.5, w=.07)
J.rail_path(add, "north bridge rail 2", [(BX + .92, BZ0), (BX + .92, BZ1)], r4(G + .25), .75, posts=1.5, w=.07)

# (what carries comes first: the island, the posts in the water)
FIRST = ["island", "tail landing", "tail piles", "tail beams", "north bridge piles"]
build = FIRST + [n for n in build if n not in FIRST]
doc = {
    "name": "Byodo-in",
    "_about": "BYODO-IN, the Phoenix Hall (1053), Uji: the central hall (a `tiered` core and its pent skirt -- the skirt's front middle bay lifted, a railing "
              "round the core on it -- the hip-and-gable roof reaching out past it, the two phoenixes on the ridge's ends), the two L-shaped two-storey wing "
              "corridors folding east at their corner towers (japanese.corridor_wing; the towers' third storeys `tiered` on the folds), the tail corridor "
              "crossing the water to the far bank, on its island in the Aji pond (a `pool` with a `shore` and the island one of its `islands`). "
              "Generated by tools/archgen/byodo_in.py -- edit the script for arithmetic changes. East (+x) is the front, south +z.",
    "params": {"detail": 4, "footW": 2 * (PX + PHW) + 4, "footD": 2 * PHD + 6},
    "site": {"origin": True, "moat": {"pool": True, "hw": PHW, "hd": PHD, "w": 0, "depth": 3.0, "surface": -.5, "x": PX,
                                      "shore": [[r4(x - PX), r4(z)] for x, z in OUTER], "islands": [[[r4(x - PX), r4(z)] for x, z in ISLAND]]}},
    "railing": {"type": "balusters"},
    "build": build,
    "parts": parts,
}
out = os.path.join(ROOT, "assets", "architecture", "byodo-in.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")

fin = {
    "name": "Byodo-in",
    "building": "architecture/byodo-in",
    "_about": "The Phoenix Hall's surfaces as repainted in 2014: the timber in the orange-red earth pigment (ni), the plaster white between it, the slat "
              "windows red over the dark rooms, grey fired clay tiles (hongawara) on every roof, the bracket sets red, the phoenixes gilt, the tower's "
              "jewel tile-grey; the platforms granite, the island a beach of pebbles.",
    "stone": {"color": "#a39e94", "accent": "#857f75", "pat": "ashlar"},
    "rules": [
        {"parts": ["chudo/storey 2 glass"], "pattern": "painted/lattice", "_about": "the lattice either side of the fan-shaped window"},
        {"parts": "kind:glass", "pattern": "timber/renji", "palette": "byodo-ni", "_about": "the slat windows (renji-mado)"},
        {"parts": "kind:roof", "surface": "roof", "pattern": "roofs/tube tiles", "palette": "kawara"},
        {"parts": "kind:roof", "color": "#b14a2b", "accent": "#8d3a21", "pat": "wood", "_about": "the eaves' rafters and boards underneath, red"},
        {"parts": [f"chudo/ridge ends/{q}" for q in ("disc", "legs", "body", "head", "feathers")], "pattern": "roofs/gold leaf", "_about": "the phoenixes, gilt"},
        {"parts": ["north tower/ridge ends/jewel", "south tower/ridge ends/jewel"], "color": "#5b6066", "accent": "#484c52", "_about": "the towers' tile jewels (hoju)"},
        {"parts": ["dou", "arm 1", "tongue 1", "blocks 1", "arm 2", "tongue 2", "blocks 2", "arm 3", "beams"], "color": "#c4522f", "accent": "#9e3f22",
         "_about": "the bracket sets, red"},
        {"parts": ["platform", "platform steps", "tail platform", "tail landing"], "pattern": "stone/ashlar fine", "palette": "granite", "_about": "the stone platforms"},
        {"parts": ["island"], "surface": "floor", "pattern": "stone/sand", "palette": "gravel", "_about": "the island's gravel"},
        {"parts": ["island"], "pattern": "stone/pebbles", "palette": "suhama", "_about": "the pebble beach (suhama) sloping into the water"},
        {"parts": ["north bridge", "north bridge piles", "tail piles", "tail beams"], "pattern": "timber/planks", "palette": "walnut", "_about": "the bridge and the posts in the water, dark timber"},
        {"surface": "floor", "pattern": "timber/planks", "palette": "walnut", "_about": "the board floors and the wings' upper floors, dark"},
        {"parts": ["chudo/rail 1", "chudo/lift 1 posts", "chudo/lift 1 beam", "north wing rail 1", "north wing rail 2", "south wing rail 1", "south wing rail 2",
                   "north bridge rail 1", "north bridge rail 2"], "color": "#c4522f", "accent": "#9e3f22", "_about": "the railings and the lifted bay's posts, red"},
        {"parts": "kind:railing", "color": "#c4522f", "accent": "#9e3f22"},
        {"parts": ["chudo moya"], "surface": "wall", "pattern": "timber/shinkabe", "palette": "byodo-ni",
         "_about": "the core's walls: red columns and plank doors, white plaster over them (it stands under the skirt, so the inside rule would catch it)"},
        {"parts": ["chudo/storey 1"], "surface": "wall", "color": "#c4522f", "accent": "#9e3f22", "_about": "the open skirt's posts, red"},
        {"parts": ["north wing lower", "south wing lower"], "surface": "wall", "color": "#c4522f", "accent": "#9e3f22", "_about": "the wings' open ground storey: posts, red"},
        {"surface": "wall", "side": "in", "pattern": "timber/planks", "palette": "walnut", "_about": "inside: dark boards"},
        {"surface": "wall", "pattern": "timber/shinkabe", "palette": "byodo-ni", "_about": "red timber standing proud of white plaster"},
    ],
}
with open(os.path.join(ROOT, "assets", "finishes", "byodo-in.json"), "w") as f:
    json.dump(fin, f, indent=1)
    f.write("\n")
print("byodo-in:", len(parts), "parts; towers at z", r4(ZT), "wing ends x", r4(XF))
