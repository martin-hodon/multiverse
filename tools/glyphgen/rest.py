from common import *
import math
Z = lambda pts: pts
def zig(x0, x1, y, amp, n, w=4):   # a zigzag line of water
    pts = [[x0 + (x1 - x0) * i / (2 * n), y + (amp if i % 2 else -amp)] for i in range(2 * n + 1)]
    return {"shape": "spline", "points": [p + [1] for p in pts], "closed": False, "stroke": "water", "line": w, "cap": "round"}
def rect(x, y, w, h, fill, **k): d = {"shape": "rect", "w": w, "h": h, "at": [x, y], "fill": fill}; d.update(k); return d
def circ(x, y, r, fill, **k): d = {"shape": "circle", "r": r, "at": [x, y], "fill": fill}; d.update(k); return d
def ell(x, y, rx, ry, fill, **k): d = {"shape": "ellipse", "rx": rx, "ry": ry, "at": [x, y], "fill": fill}; d.update(k); return d
def poly(pts, fill, **k): d = {"shape": "points", "points": pts, "fill": fill}; d.update(k); return d
cats = {}
# ---- H parts of birds --------------------------------------------------------------------------------------------------
cats["H"] = {
 "H6": sign("feather", reading="Sw: feather; mAat: truth", freq=3, colors={"plume": "white", "vane": "green"}, layers=[P("feather", at=[52, 4], scale=1.55)]),
 "H8": sign("egg", reading="sA: son (determinative), egg", freq=1, colors={"egg": "white"}, layers=[ell(50, 30, 20, 26, "egg", rot=-20)]),
}
# ---- I reptiles ----------------------------------------------------------------------------------------------------------
cats["I"] = {
 "I3": sign("crocodile", reading="msH: crocodile", freq=1, colors={"body": "green-dark", "belly": "green-light"}, layers=[
   L([[34, 22], [30, 10], [24, 8]], "body", 4), L([[70, 22], [72, 10], [66, 8]], "body", 4),
   S([[2, 26], [10, 30], [26, 32], [46, 34], [66, 33], [84, 30], [98, 24], [98, 20, C], [84, 20], [64, 20], [40, 20], [20, 22], [4, 22]], "body"),
   *[poly([[x, 33.4], [x + 3, 38], [x + 6, 33.6]], "body", line=.6) for x in range(30, 72, 7)],
   L([[38, 22], [36, 10], [30, 8]], "body", 4), L([[76, 22], [80, 10], [74, 8]], "body", 4),
   circ(14, 30, 1.4, "black", outline=False)]),
 "I9": sign("horned viper", reading="f", freq=8, colors={"body": "yellow", "spots": "brown"}, layers=[
   S([[6, 26], [10, 32], [20, 33], [28, 28], [40, 24], [60, 22], [80, 20], [96, 14], [98, 10, C], [80, 12], [58, 14], [38, 16], [26, 18], [14, 20], [8, 20]], "body"),
   *[ell(x, y, 2.2, 1.2, "spots", outline=False) for x, y in ((36, 20), (48, 18.4), (60, 17.6), (72, 16.4), (84, 14.4))],
   L([[15, 32], [13, 38]], "body", 2), L([[21, 32], [23, 38]], "body", 2), circ(12, 27, 1.3, "black", outline=False)]),
 "I10": sign("cobra", reading="D (dj)", freq=8, colors={"body": "green", "belly": "yellow"}, layers=[
   S([[24, 18], [36, 14], [56, 12], [74, 16], [90, 14], [98, 8, C], [84, 6], [64, 4], [40, 4], [22, 6], [16, 12]], "body"),
   L([[20, 12], [16, 30], [18, 50]], "body", 7.4),
   S([[14, 48], [8, 54], [10, 60], [20, 60], [24, 54], [22, 48]], "body"), circ(13, 55, 1.2, "black", outline=False)]),
 "I12": sign("erect cobra (uraeus)", reading="iart: uraeus", freq=1, colors={"body": "green", "hood": "yellow"}, layers=[
   S([[40, 4], [70, 4], [86, 10], [80, 16], [60, 14], [46, 14], [40, 10]], "body"),
   S([[42, 12], [34, 30], [30, 56], [34, 76], [40, 84], [48, 82], [50, 70], [48, 44], [52, 22], [56, 12]], "hood"),
   S([[34, 74], [32, 86], [38, 92], [46, 90], [48, 82]], "body"), circ(37, 86, 1.2, "black", outline=False)]),
}
# ---- K fish, L insects --------------------------------------------------------------------------------------------------
cats["K"] = {"K1": sign("bulti fish (tilapia)", reading="in", freq=3, colors={"body": "blue-light", "fins": "red", "stripes": "blue-dark"}, layers=[
   S([[76, 34], [86, 48], [96, 52], [94, 30], [96, 12], [86, 18]], "fins"),
   S([[30, 48, C], [42, 56], [60, 54], [70, 50], [64, 46]], "fins"),
   S([[8, 30], [16, 40], [34, 46], [56, 46], [76, 38], [80, 30], [76, 22], [56, 14], [34, 14], [16, 20]], "body"),
   *[line([x, 18], [x - 2, 42], "stripes", w=1.4) for x in (36, 48, 60)], S([[30, 14, C], [44, 6], [52, 12]], "fins"),
   circ(16, 32, 1.8, "black", outline=False)])}
cats["L"] = {
 "L1": sign("scarab beetle", reading="xpr: become", freq=3, colors={"body": "blue", "legs": "black", "head": "green"}, layers=[
   *[L(p, "legs", 2.4) for p in ([[38, 40], [24, 34], [18, 22]], [[62, 40], [76, 34], [82, 22]], [[36, 56], [20, 58], [14, 66]], [[64, 56], [80, 58], [86, 66]], [[40, 70], [28, 80], [26, 92]], [[60, 70], [72, 80], [74, 92]])],
   S([[50, 76], [64, 72], [70, 56], [66, 32], [50, 18], [34, 32], [30, 56], [36, 72]], "body"), line([50, 70], [50, 22], w=1.2),
   S([[42, 74], [44, 86], [50, 90], [56, 86], [58, 74]], "head")]),
 "L2": sign("bee", reading="bit: bee, honey", freq=1, colors={"body": "yellow", "bands": "black", "wings": "white"}, layers=[
   S([[56, 52], [62, 76], [76, 92], [84, 88], [78, 70], [64, 52]], "wings"),
   S([[30, 46], [44, 54], [70, 52], [90, 40], [92, 30], [78, 26], [52, 30], [36, 36]], "body"),
   *[line([x, 28], [x + 2, 52], "bands", w=3) for x in (62, 72, 82)],
   S([[18, 40], [24, 52], [34, 50], [36, 40], [28, 34]], "bands"),
   L([[20, 50], [12, 62]], "bands", 1.2), L([[24, 52], [20, 66]], "bands", 1.2),
   L([[46, 32], [40, 18]], "bands", 1.6), L([[56, 30], [56, 14]], "bands", 1.6), L([[66, 28], [72, 14]], "bands", 1.6)]),
}
# ---- M plants ------------------------------------------------------------------------------------------------------------
cats["M"] = {
 "M1": sign("tree", reading="iAm: tree", freq=1, colors={"leaves": "green", "wood": "brown"}, layers=[
   L([[50, 2], [50, 40]], "wood", 7), S([[50, 98], [64, 86], [70, 64], [66, 44], [56, 36], [44, 36], [34, 44], [30, 64], [36, 86]], "leaves")]),
 "M3": sign("branch", reading="xt: wood", freq=2, colors={"wood": "yellow-dark"}, layers=[
   S([[2, 12], [36, 16], [60, 22], [72, 30], [74, 26], [64, 18], [80, 18], [98, 22], [98, 16], [70, 12], [40, 8], [4, 6]], "wood")]),
 "M8": sign("pool with lotus flowers", reading="SA", freq=3, colors={"water": "blue", "lotus": "green", "bloom": "white"}, layers=[
   *[L([[x, 24], [x, 44]], "lotus", 3) for x in (16, 34, 50, 66, 84)],
   *[poly([[x - 7, 44], [x + 7, 44], [x + 9, 58], [x, 50], [x - 9, 58]], "bloom") if i % 2 == 0 else poly([[x - 3, 44], [x + 3, 44], [x, 54]], "lotus") for i, x in enumerate((16, 34, 50, 66, 84))],
   rect(50, 16, 94, 18, "water", r=8), zig(10, 90, 16, 2.4, 7, w=1.2)]),
 "M12": sign("lotus plant", reading="xA: thousand", freq=2, colors={"stem": "green", "bloom": "green-light", "pod": "blue"}, layers=[
   L([[50, 4], [50, 70]], "stem", 4), L([[50, 4], [38, 4]], "stem", 3), L([[50, 4], [62, 4]], "stem", 3),
   S([[40, 70], [36, 88], [44, 84], [50, 96], [56, 84], [64, 88], [60, 70]], "bloom")]),
 "M16": sign("clump of papyrus", reading="HA", freq=2, colors={"stem": "green", "umbel": "green-light"}, layers=[
   *[L([[50, 6], [x, 66]], "stem", 3) for x in (24, 38, 50, 62, 76)],
   *[poly([[x - 7, 80], [x + 7, 80], [x, 64]], "umbel") for x in (24, 38, 50, 62, 76)],
   rect(50, 6, 40, 6, "stem")]),
 "M17": sign("flowering reed", reading="i", freq=9, colors={"leaf": "green", "flower": "yellow"}, layers=[
   S([[44, 4, C], [56, 4, C], [58, 40], [60, 72], [56, 92], [50, 98, C], [46, 86], [48, 76], [42, 72], [44, 66], [42, 36]], "leaf"),
   S([[50, 98, C], [56, 92], [58, 84], [52, 86], [48, 90]], "flower")]),
 "M23": sign("sedge", reading="sw: he; nsw: king", freq=4, colors={"stem": "green", "flower": "yellow"}, layers=[
   L([[50, 4], [50, 80], [56, 92], [62, 92]], "stem", 3.4),
   *[L(p, "stem", 3) for p in ([[50, 30], [34, 40], [28, 52]], [[50, 30], [66, 40], [72, 52]], [[50, 12], [32, 18], [24, 30]], [[50, 12], [68, 18], [76, 30]])]]),
}
# ---- N sky, earth, water -----------------------------------------------------------------------------------------------
cats["N"] = {
 "N1": sign("sky", reading="pt: sky", freq=3, colors={"sky": "sky"}, layers=[poly([[2, 70], [98, 70], [98, 54], [92, 54], [92, 60], [8, 60], [8, 54], [2, 54]], "sky")]),
 "N5": sign("sun", reading="ra: sun, day", freq=5, colors={"sun": "red"}, layers=[circ(50, 50, 30, "sun"), circ(50, 50, 6, "yellow")]),
 "N14": sign("star", reading="sbA: star", freq=2, colors={"star": "yellow"}, layers=[
   {"shape": "star", "n": 5, "r": 40, "inner": .22, "at": [50, 46], "fill": "star"}]),
 "N16": sign("flat land with grains of sand", reading="tA: land", freq=3, colors={"earth": "black", "sand": "red"}, layers=[
   rect(50, 34, 90, 10, "earth", r=2), *[circ(x, 21, 3.4, "sand") for x in (28, 50, 72)]]),
 "N25": sign("hill country", reading="xAst: desert, foreign land", freq=2, colors={"desert": "pink", "sand": "red"}, layers=[
   S([[4, 6, C], [96, 6, C], [96, 22], [84, 34], [72, 22, C], [62, 46], [50, 52], [38, 46], [28, 22, C], [16, 34], [4, 22]], "desert"),
   *[circ(x, y, 1.6, "sand", outline=False) for x, y in ((16, 20), (36, 32), (50, 40), (64, 32), (84, 20), (50, 18), (30, 14), (70, 14))]]),
 "N29": sign("sandy hill slope", reading="q", freq=7, colors={"sand": "yellow", "grain": "red"}, layers=[
   S([[22, 10, C], [86, 10, C], [84, 30], [72, 60], [60, 72], [48, 70], [36, 52], [28, 30]], "sand"),
   *[circ(x, y, 1.8, "grain", outline=False) for x, y in ((40, 24), (54, 30), (66, 22), (50, 48), (62, 52), (46, 16), (72, 38))]]),
 "N31": sign("road with shrubs", reading="wAt: road", freq=2, colors={"road": "yellow-dark", "shrub": "green"}, layers=[
   rect(50, 30, 92, 14, "road"), *[poly([[x - 5, 37], [x + 5, 37], [x, 47]], "shrub") for x in (14, 34, 54, 74, 90)],
   *[poly([[x - 5, 23], [x + 5, 23], [x, 13]], "shrub") for x in (24, 44, 64, 84)]]),
 "N35": sign("ripple of water", reading="n", freq=9, colors={"water": "water"}, layers=[
   {**zig(4, 96, 30, 5, 8, w=5), "_about": "the zigzag of a wave"}]),
 "N37": sign("pool", reading="S", freq=7, colors={"water": "water"}, layers=[
   rect(50, 30, 90, 22, "water"), zig(10, 90, 30, 3, 8, w=1.4)]),
}
cats["N"]["N37"]["layers"][1]["stroke"] = "blue-dark"
# ---- O buildings ---------------------------------------------------------------------------------------------------------
cats["O"] = {
 "O1": sign("house (plan)", reading="pr: house", freq=6, colors={"wall": "red"}, layers=[
   {"shape": "spline", "points": [[42, 14, C], [12, 14, C], [12, 50, C], [88, 50, C], [88, 14, C], [58, 14, C]], "closed": False, "stroke": "wall", "line": 8, "cap": "butt"}]),
 "O4": sign("reed shelter", reading="h", freq=7, colors={"wall": "yellow-dark"}, layers=[
   {"shape": "spline", "points": [[30, 6, C], [30, 34, C], [16, 34], [14, 70, C], [86, 70, C], [86, 6, C]], "closed": False, "stroke": "wall", "line": 7, "cap": "butt"}]),
 "O24": sign("pyramid", reading="mr: pyramid", freq=1, colors={"stone": "white", "face": "yellow"}, layers=[
   poly([[14, 10], [86, 10], [50, 84]], "stone"), poly([[50, 84], [86, 10], [62, 10]], "face"), rect(50, 7, 84, 6, "yellow-dark")]),
 "O28": sign("column", reading="iwn: pillar", freq=2, colors={"stone": "white", "band": "red"}, layers=[
   rect(50, 46, 22, 74, "stone"), rect(50, 86, 14, 8, "stone"), *[rect(50, y, 22, 4, "band") for y in (72, 66, 22)],
   S([[40, 82], [44, 92], [50, 96], [56, 92], [60, 82]], "stone")]),
 "O34": sign("door bolt", reading="z (s)", freq=7, colors={"bolt": "red", "wood": "yellow-dark"}, layers=[
   rect(52, 30, 72, 8, "wood"), ell(24, 30, 9, 9, "bolt"), ell(42, 30, 7, 7, "bolt"), rect(92, 30, 6, 14, "bolt")]),
 "O49": sign("village with crossroads", reading="niwt: town (determinative)", freq=3, colors={"town": "red", "street": "plaster"}, layers=[
   circ(50, 50, 32, "town"), rect(50, 50, 52, 7, "street", rot=45, outline=False), rect(50, 50, 52, 7, "street", rot=-45, outline=False)]),
}
# ---- P ships, Q furniture -------------------------------------------------------------------------------------------------
cats["P"] = {
 "P1": sign("boat", reading="boat (determinative)", freq=2, colors={"hull": "yellow-dark", "cabin": "red", "oar": "brown"}, layers=[
   L([[74, 20], [86, 60]], "oar", 2.6),
   S([[4, 40], [18, 24], [40, 18], [70, 18], [88, 26], [98, 42], [92, 38], [72, 30], [40, 30], [16, 32]], "hull"),
   rect(52, 37, 22, 12, "cabin"), poly([[44, 43], [60, 43], [52, 54]], "cabin")]),
 "P8": sign("oar", reading="xrw: voice", freq=2, colors={"wood": "yellow-dark"}, layers=[
   L([[50, 96], [50, 30]], "wood", 3.6), S([[50, 34], [58, 20], [56, 6], [50, 2, C], [44, 6], [42, 20]], "wood")]),
}
cats["Q"] = {
 "Q1": sign("seat (throne)", reading="st: seat; Isis", freq=4, colors={"wood": "red", "back": "white"}, layers=[
   poly([[20, 6], [70, 6], [70, 38], [52, 38], [52, 52], [20, 52]], "wood"), rect(30, 46, 20, 9, "back"), rect(62, 44, 6, 10, "wood")]),
 "Q3": sign("stool of reed matting", reading="p", freq=8, colors={"mat": "blue"}, layers=[
   rect(50, 22, 44, 36, "mat"), *[line([30, y], [70, y], "line", w=1) for y in (12, 22, 32)]]),
 "Q7": sign("brazier with flame", reading="fire (determinative)", freq=1, colors={"bowl": "yellow-dark", "flame": "red"}, layers=[
   S([[36, 50], [30, 70], [40, 82], [48, 96], [54, 84], [64, 76], [64, 56]], "flame"),
   S([[24, 48, C], [76, 48, C], [70, 36], [58, 30], [42, 30], [30, 36]], "bowl"), rect(50, 16, 12, 28, "bowl")]),
}
# ---- R sacred, S crowns and staves -----------------------------------------------------------------------------------------
cats["R"] = {
 "R4": sign("loaf on a reed mat", reading="Htp: offering, peace", freq=4, colors={"mat": "green", "bread": "bread"}, layers=[
   rect(50, 12, 92, 8, "mat"), poly([[40, 16], [60, 16], [58, 32], [50, 40], [42, 32]], "bread")]),
 "R8": sign("cloth on a pole", reading="nTr: god", freq=5, colors={"pole": "yellow", "cloth": "red", "band": "white"}, layers=[
   L([[56, 4], [56, 96]], "pole", 5),
   S([[56, 92, C], [30, 90], [24, 82], [32, 74], [42, 76], [52, 72], [56, 70, C]], "cloth"), line([30, 84], [54, 82], "band", w=3)]),
 "R11": sign("djed pillar", reading="Dd: stable, endure", freq=3, colors={"pillar": "blue", "band": "red", "cap": "green"}, layers=[
   S([[40, 4, C], [60, 4, C], [58, 40], [58, 62, C], [42, 62, C], [42, 40]], "pillar"),
   *[rect(50, y, 36, 5, "cap") for y in (64, 72, 80, 88)], rect(50, 95, 24, 4, "band"), rect(50, 36, 18, 4, "band")]),
}
cats["S"] = {
 "S3": sign("red crown", reading="dSrt: red crown", freq=1, colors={"crown": "red"}, layers=[
   S([[22, 4, C], [70, 4, C], [70, 54, C], [78, 54], [78, 96, C], [66, 96, C], [66, 64, C], [24, 60], [20, 30]], "crown"),
   L([[24, 40], [16, 56], [12, 70], [20, 74], [24, 66], [20, 62]], "gold", 2.4)]),
 "S12": sign("collar of beads", reading="nbw: gold", freq=2, colors={"gold": "gold", "bead": "blue"}, layers=[
   S([[8, 70, C], [92, 70, C], [92, 58], [80, 32], [60, 22], [40, 22], [20, 32], [8, 58]], "gold"),
   rect(50, 70, 84, 6, "gold"), *[circ(50 + 30 * math.cos(a), 52 - 26 * math.sin(a), 3, "bead") for a in [math.pi * (i + .5) / 9 for i in range(9)]]]),
 "S29": sign("folded cloth", reading="s", freq=9, colors={"cloth": "red"}, layers=[
   {"shape": "spline", "points": [[40, 4, C], [40, 78], [44, 90], [50, 94], [56, 90], [60, 78], [60, 4, C]], "closed": True, "fill": "cloth"},
   line([50, 86], [50, 6], w=1.2)]),
 "S34": sign("sandal strap (ankh)", reading="anx: life", freq=5, colors={"ankh": "blue"}, layers=[
   {"shape": "ring", "r": 16, "w": 7, "at": [50, 74], "fill": "ankh"}, rect(50, 56, 50, 8, "ankh", r=2),
   poly([[46, 54], [54, 54], [57, 4], [43, 4]], "ankh")]),
 "S38": sign("crook", reading="HqA: rule", freq=2, colors={"stripe": "blue", "gold": "gold"}, layers=[
   L([[44, 4], [44, 74], [46, 88], [54, 92], [62, 88], [62, 78], [56, 76]], "gold", 7),
   *[L([[44, y], [44, y + 4]], "stripe", 7, outline=False, cap="butt") for y in (14, 30, 46, 62)]]),
 "S40": sign("was sceptre", reading="wAs: dominion", freq=3, colors={"wood": "green"}, layers=[
   L([[50, 10], [50, 80]], "wood", 5), L([[50, 10], [44, 2]], "wood", 4), L([[50, 10], [56, 2]], "wood", 4),
   S([[48, 76], [38, 84], [36, 92], [44, 90], [58, 82], [54, 76]], "wood")]),
}
# ---- T weapons, U tools ------------------------------------------------------------------------------------------------------
cats["T"] = {
 "T3": sign("mace with pear-shaped head", reading="HD: white, bright", freq=2, colors={"head": "white", "wood": "yellow-dark"}, layers=[
   L([[50, 4], [50, 70]], "wood", 4), S([[50, 92], [60, 84], [62, 74], [56, 66], [44, 66], [38, 74], [40, 84]], "head")]),
 "T14": sign("throw stick", reading="foreign (determinative)", freq=2, colors={"wood": "yellow-dark"}, layers=[
   L([[30, 90], [44, 70], [44, 6]], "wood", 5)]),
 "T22": sign("arrowhead", reading="sn: brother", freq=2, colors={"flint": "yellow-dark"}, layers=[
   poly([[40, 96], [60, 96], [56, 30], [64, 30], [50, 4], [36, 30], [44, 30]], "flint")]),
}
cats["U"] = {
 "U1": sign("sickle", reading="mA", freq=2, colors={"wood": "yellow-dark", "flint": "white"}, layers=[
   S([[14, 8], [40, 28], [64, 50], [78, 66], [84, 82], [92, 84], [88, 66], [76, 50], [56, 30], [24, 6]], "wood"),
   S([[78, 66], [70, 76], [62, 84], [72, 86], [84, 80]], "flint")]),
 "U7": sign("hoe", reading="mr", freq=3, colors={"wood": "yellow-dark", "rope": "red"}, layers=[
   L([[10, 54], [96, 54]], "wood", 4.4), L([[18, 56], [52, 30], [86, 12]], "wood", 4.4), L([[54, 54], [62, 26]], "rope", 2)]),
}
# ---- V rope and baskets ------------------------------------------------------------------------------------------------------
cats["V"] = {
 "V4": sign("lasso", reading="wA", freq=3, colors={"rope": "yellow-dark"}, layers=[
   L([[60, 8], [62, 50], [56, 76], [44, 80], [34, 70], [36, 50], [50, 40], [40, 24], [26, 22], [26, 34], [36, 38]], "rope", 3.2)]),
 "V13": sign("tethering rope", reading="T", freq=7, colors={"rope": "yellow-dark"}, layers=[
   L([[94, 30], [26, 30]], "rope", 5), {"shape": "ring", "r": 8, "w": 4, "at": [18, 38], "fill": "rope"}, {"shape": "ring", "r": 8, "w": 4, "at": [18, 22], "fill": "rope"}]),
 "V20": sign("hobble for cattle", reading="mD: ten", freq=3, colors={"rope": "yellow-dark"}, layers=[
   {"shape": "spline", "points": [[34, 6, C], [34, 36], [40, 46], [50, 50], [60, 46], [66, 36], [66, 6, C]], "closed": False, "stroke": "rope", "line": 6, "cap": "butt"}]),
 "V28": sign("twisted wick", reading="H", freq=8, colors={"flax": "green"}, layers=[
   L([[50, 4], [50, 14]], "flax", 4),
   *[{"shape": "ring", "r": 9, "w": 4.6, "at": [50, y], "fill": "flax"} for y in (26, 46, 66)], L([[50, 76], [50, 94]], "flax", 4),
   L([[50, 94], [44, 98]], "flax", 3), L([[50, 94], [56, 98]], "flax", 3)]),
 "V30": sign("wicker basket", reading="nb: lord, all", freq=6, colors={"basket": "green", "weave": "green-dark"}, layers=[
   S([[6, 38, C], [94, 38, C], [86, 22], [66, 12], [34, 12], [14, 22]], "basket"),
   *[line([x, 36], [x + 4, 14], "weave", w=1) for x in range(18, 82, 10)]]),
 "V31": sign("basket with handle", reading="k", freq=8, colors={"basket": "green", "weave": "green-dark"}, layers=[
   L([[90, 34], [96, 28], [92, 20], [84, 22]], "basket", 3.4),
   S([[6, 38, C], [90, 38, C], [82, 22], [64, 12], [34, 12], [14, 22]], "basket"),
   *[line([x, 36], [x + 4, 14], "weave", w=1) for x in range(18, 80, 10)]]),
}
# ---- W vessels, X bread, Y writing, Z strokes, Aa -------------------------------------------------------------------------------
cats["W"] = {
 "W11": sign("jar stand", reading="g", freq=7, colors={"stand": "red"}, layers=[
   S([[30, 56, C], [70, 56, C], [64, 46], [62, 30], [68, 16, C], [32, 16, C], [38, 30], [36, 46]], "stand"),
   rect(50, 58, 46, 6, "stand", r=2), rect(50, 14, 42, 5, "stand", r=2)]),
 "W24": sign("bowl (pot)", reading="nw, in", freq=4, colors={"pot": "red"}, layers=[
   S([[34, 50], [28, 36], [32, 18], [50, 10], [68, 18], [72, 36], [66, 50]], "pot"), rect(50, 52, 34, 6, "pot", r=2)]),
}
cats["X"] = {
 "X1": sign("bread loaf", reading="t", freq=10, colors={"bread": "bread"}, layers=[
   {"shape": "spline", "points": [[24, 14, C], [76, 14, C], [72, 26], [62, 34], [50, 36], [38, 34], [28, 26]], "fill": "bread"}]),
 "X8": sign("conical loaf", reading="di, rdi: give", freq=4, colors={"bread": "bread"}, layers=[
   poly([[40, 6], [60, 6], [50, 64]], "bread")]),
}
cats["Y"] = {
 "Y1": sign("papyrus roll, tied", reading="abstract (determinative)", freq=4, colors={"papyrus": "papyrus", "tie": "red"}, layers=[
   rect(52, 24, 76, 16, "papyrus", r=3), rect(46, 24, 6, 18, "tie", outline=False), L([[44, 32], [38, 40]], "tie", 2), L([[48, 32], [54, 40]], "tie", 2)]),
 "Y5": sign("senet board", reading="mn", freq=5, colors={"board": "yellow-dark", "piece": "black"}, layers=[
   rect(50, 20, 88, 18, "board"), *[rect(x, 33, 5, 8, "piece", r=2) for x in (14, 26, 38, 50, 62, 74, 86)]]),
}
cats["Z"] = {
 "Z1": sign("single stroke", reading="(the sign means what it shows; one)", freq=6, colors={"ink": "black"}, layers=[rect(50, 22, 7, 36, "ink")]),
 "Z4": sign("two diagonal strokes", reading="y", freq=6, colors={"ink": "black"}, layers=[rect(38, 22, 7, 36, "ink", rot=-16), rect(60, 22, 7, 36, "ink", rot=-16)]),
 "Z7": sign("coil (hieratic quail chick)", reading="w", freq=5, colors={"ink": "yellow-dark"}, layers=[
   L([[40, 8], [54, 16], [62, 30], [56, 44], [44, 46], [38, 38], [42, 30], [50, 32]], "ink", 4.4)]),
}
cats["Aa"] = {
 "Aa1": sign("placenta (or sieve)", reading="x (kh)", freq=8, colors={"disc": "red", "stripe": "black"}, layers=[
   circ(50, 34, 24, "disc"), *[{"shape": "rect", "w": 46, "h": 2.6, "at": [50, y], "fill": "stripe", "outline": False, "clip": {"shape": "circle", "r": 23, "at": [0, 34 - y]}} for y in (24, 34, 44)]]),
 "Aa11": sign("platform (of Maat)", reading="mAa: true", freq=2, colors={"wood": "yellow-dark"}, layers=[
   poly([[4, 8], [84, 8], [96, 18], [12, 18]], "wood")]),
}
for k, v in cats.items(): category(k, v)
