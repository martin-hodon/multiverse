"""THE ALHAMBRA at its height under Muhammad V (c. 1370-1391): the walled palace-city on the Sabika hill over Granada,
and across the ravine to the east the GENERALIFE, the sultans' country palace and its orchards.

Run: python3 tools/archgen/alhambra.py -- writes assets/architecture/alhambra.json, assets/finishes/alhambra.json and
assets/doors/alhambra.json. Built from the components of tools/archgen/andalusi.py (nasrid-portico, qubba, torre, bab,
alminar) and couchant-lion; nothing else is drawn here but what is the Alhambra's alone -- its plan, its ground.

FRAME. x east, z south, metres from 37.1767 N 3.5895 W (the Court of the Myrtles' north end lies near x -16, z -76);
y 0 is 745 m above sea level, the foot of the Sabika's slopes: the palaces' courts stand at 772 m (y 27), the
Alcazaba's parade ground at 781 m, the Generalife's court at 798 m. The hill is let down to y 0 over the frame's last
20 m (the world round it is flat). The Generalife is laid out in a frame of its own (`Frame`), turned 38 degrees along
its court; the Sabika's palaces lie on the compass.

SOURCED.
  Ground: the IGN's MDT05 (5 m digital terrain model, servicios.idee.es WCS, coverage Elevacion4258_5), in
    alhambra_dtm.txt (decimetres over 772.0 m), carved level under every building's floor here.
  Plan (OpenStreetMap, 2026-11): the outer wall's ring (way 92528618, simplified to 1.5 m), the Alcazaba's (26935518),
    every named tower's footprint as its least rectangle, the Nasrid palaces' rooms (Mexuar 197859965, Cuarto Dorado
    197859964, Sala de la Barca 197859971, the Myrtles' court 92528790, the baths 197859963, the Lions' halls
    197859972-74 / 197861085, Daraxa 197859966, Lindaraja 92528755), the Partal (51683602, its pond 51683603, the
    Damas tower 196500564, the oratory 117357969), the mosque's site (117369758), its baths (196485675), the Yusuf III
    palace's (1070349177), the Abencerrajes palace's (196500578); the Generalife (the palace 51683601, the Court of the
    Water Channel 268563933 and its channel, the Sala Regia 1079185009, the Sultana's court 268563942, the upper
    gardens 1079185019, the entrance courts, the orchards 1083149402 / 1293589086), the Albercon Arabe (437956399),
    the Silla del Moro (223074706).
  Measures (Lopez Lopez; Fernandez-Puertas, The Alhambra I, 1997; the Patronato's plans): the Myrtles' court 36.6 x
    23 m, its pool 34 x 7.1 m; the Hall of the Ambassadors 11.3 m square and 18.2 m high in the Comares tower, some 45 m
    over the slope outside; the Lions' court 28.5 x 15.7 m, 124 columns, its pavilions and the fountain of twelve lions;
    the Two Sisters' dome some 8 m across; the Torre de la Vela 26.8 m, the Homenaje 26 m; the Partal's portico of
    five arches before the Damas tower and its pond; the mosque of Muhammad III (1305) of three naves, its minaret;
    the Generalife's court 48.7 x 12.8 m, the porticoes of five arches at its ends, the west gallery of eighteen with
    its mirador, the tower of Ismail I behind the Sala Regia, the water stair's three flights.
ESTIMATED.
  Heights where none is published (the walls 9 m over their ground, most towers 12-16 m, the ranges round the courts
    8-10 m); the porticoes' bays from the courts' widths; the medina's houses -- a grid of courtyard houses with lanes,
    standing where the city's houses stood (its ruins are excavated in places, not mapped); the palaces in the medina
    (Yusuf III's, the Abencerrajes', the one under the convent of San Francisco) as courts with a pool, porticoes at
    their ends and ranges round, on their sites' rectangles; the mosque's hall 30 x 20 m with its court to the north
    and the minaret at the court's corner (excavated under Santa Maria, not mapped); a muqarnas cell for every few;
    in the Generalife the east range's rooms, the entrance courts' walls and stair, the oratory at the water stair's
    head (a small qubba), the Silla del Moro as its outline walled with one tower, the orchards' trees on a 9 m grid.
LEFT OUT (what came after the Nasrid peak, or is no part of the medieval Alhambra):
  the palace of Charles V (1527) -- the ground it took is the medina's again here, houses and the Rawda's court; Santa
    Maria (1581) -- the mosque stands in its place; the convent of San Francisco -- a Nasrid palace in its place; the
    Torre del Cubo (16th c.), the artillery bastions on the Siete Suelos and Cabezas towers, the Puerta de las Granadas
    and the Puerta de los Carros; the Peinador de la Reina's gallery (1537) on the Abu-l-Hayyay tower; the rooms of
    Charles V round the Lindaraja garden (here open to the valley again); the Mocarabes hall's vault of 1714 (its
    muqarnas is the finish's); in the GENERALIFE, the gallery of 1494 over the north pavilion, the Sultana court's
    galleries (1584) and its U-shaped pool, the Mirador Romantico (1836), the cypress walk, the 20th-century gardens
    and theatre, the Albercones beside the Arab one; beyond the frame, the Dar al-Arusa and the Alijares.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import Doc, r4, Q, at, wall_at, split, tiles, plant, hedges, write_json, horseshoe

NAME = "alhambra"
HERE = os.path.dirname(os.path.abspath(__file__))
D = Doc()

# =====================================================================================================================
# 1. THE FRAME AND THE GROUND
# =====================================================================================================================
Y0 = 745.0                                     # metres above the sea at y 0
def lv(m): return round(m - Y0, 2)             # a height above the sea, in the frame
PAL = lv(772.0)                                # the Nasrid palaces' courts
PARTAL = lv(769.6)                             # the Partal's pond and portico
_rows = [ln for ln in open(os.path.join(HERE, "alhambra_dtm.txt")) if not ln.startswith("#")]
GX0, GZ0, CELL = -340.0, -240.0, 5.0
RAW = [[772.0 + int(v) / 10 - Y0 for v in row.split()] for row in _rows]
NX, NZ = len(RAW[0]), len(RAW)
GX1, GZ1 = GX0 + (NX - 1) * CELL, GZ0 + (NZ - 1) * CELL
rng = random.Random(1391)                      # (the medina's houses, the orchards: the same every run)
FADE = 20.0                                    # the hill let down to the world's ground over the frame's last metres


def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def bilin(G, x, z):
    fx, fz = (x - GX0) / CELL, (z - GZ0) / CELL
    i, j = max(0, min(NX - 2, int(math.floor(fx)))), max(0, min(NZ - 2, int(math.floor(fz))))
    u, v = fx - i, fz - j
    return G[j][i] * (1 - u) * (1 - v) + G[j][i + 1] * u * (1 - v) + G[j + 1][i] * (1 - u) * v + G[j + 1][i + 1] * u * v


def node_xz(i, j): return GX0 + i * CELL, GZ0 + j * CELL


GH = [[max(0.0, RAW[j][i] * smooth(min(node_xz(i, j)[0] - GX0, GX1 - node_xz(i, j)[0], node_xz(i, j)[1] - GZ0, GZ1 - node_xz(i, j)[1]) / FADE))
       for i in range(NX)] for j in range(NZ)]
def ground(x, z): return bilin(GH, x, z)


def poly_in(P, x, z):
    c = False
    for i in range(len(P)):
        (x0, z0), (x1, z1) = P[i], P[i - 1]
        if (z0 > z) != (z1 > z) and x < (x1 - x0) * (z - z0) / (z1 - z0) + x0: c = not c
    return c


def seg_d(x, z, a, b):
    ex, ez = b[0] - a[0], b[1] - a[1]; L2 = ex * ex + ez * ez or 1e-9
    t = max(0, min(1, ((x - a[0]) * ex + (z - a[1]) * ez) / L2))
    return math.hypot(x - a[0] - t * ex, z - a[1] - t * ez)


def poly_d(P, x, z): return min(seg_d(x, z, P[i - 1], P[i]) for i in range(len(P)))
def in_rect(r, x, z, m=0.0): return r[0] - m <= x <= r[2] + m and r[1] - m <= z <= r[3] + m


class Frame:
    """a plan's own axes: its origin (x, z) and its turn `deg` (local +z points along (sin, cos) of it -- the engine's
    yaw). The palaces of the Sabika are laid out on the compass and use WORLD; the Generalife is turned 38 degrees."""
    def __init__(self, x=0.0, z=0.0, deg=0.0):
        self.x, self.z, self.yaw = x, z, math.radians(deg)
        self.c, self.s = math.cos(self.yaw), math.sin(self.yaw)

    def w(self, u, v): return self.x + u * self.c + v * self.s, self.z - u * self.s + v * self.c       # local -> world
    def l(self, x, z): dx, dz = x - self.x, z - self.z; return dx * self.c - dz * self.s, dx * self.s + dz * self.c
    def at(self, u, y, v, yaw=0.0): X, Z = self.w(u, v); return at(X, y, Z, yaw + self.yaw)


WORLD = Frame()

# SITES: the level ground every building stands on -- (name, [rects in its frame], level, frame, platform). The hill is
# cut down under each (and a cell round it, so no slope stands up through a wall), and unless `platform` is off (a
# flight of stairs, carried on its own masonry) a platform stands up from the lowest ground under it to its level: the
# floor, walked.
SITES = []
def site(name, rects, y, F=WORLD, platform=True):
    SITES.append((name, rects, y, F, platform)); return y


def on_site(S, x, z, m=0.0):
    u, v = S[3].l(x, z); return any(in_rect(r, u, v, m) for r in S[1])


# =====================================================================================================================
# 2. THE PLAN (OpenStreetMap; see the docstring)
# =====================================================================================================================
RING = [[-79.9, 54.9], [-85.4, 68.1], [-72.6, 73.4], [-65.8, 57.1], [-38.6, 69.2], [-40.1, 72.3], [-30.0, 77.2], [-28.4, 74.1], [12.4, 88.2], [48.0, 102.9],
        [60.4, 111.0], [76.0, 124.9], [77.7, 122.9], [111.8, 149.4], [95.7, 168.6], [99.7, 174.6], [105.8, 177.8], [123.0, 157.7], [158.2, 184.5], [154.6, 190.3],
        [160.1, 193.6], [163.6, 187.9], [195.5, 201.9], [192.8, 208.5], [199.0, 211.2], [202.2, 204.6], [235.4, 212.4], [234.4, 240.6], [235.0, 244.1], [240.5, 248.2],
        [248.7, 248.5], [253.3, 244.5], [254.0, 213.5], [307.5, 217.1], [307.1, 225.3], [312.4, 225.6], [312.9, 217.4], [340.5, 220.1], [343.9, 228.6], [349.7, 226.3],
        [346.3, 217.7], [365.6, 208.5], [387.3, 210.3], [387.8, 199.7], [384.3, 199.5], [383.6, 197.5], [385.6, 176.3], [388.0, 175.0], [389.8, 158.0], [398.0, 156.6],
        [397.6, 151.9], [393.8, 149.6], [386.5, 151.2], [341.5, 121.3], [328.6, 115.1], [333.9, 106.2], [325.3, 101.2], [320.5, 109.4], [303.2, 95.0], [289.1, 76.7],
        [280.2, 60.3], [292.3, 53.7], [288.4, 46.6], [276.3, 53.2], [257.0, 35.9], [240.1, 9.9], [246.7, 3.7], [243.0, -0.2], [236.4, 6.0], [200.4, -18.9],
        [209.4, -26.2], [209.7, -30.0], [204.7, -35.9], [212.2, -41.1], [208.3, -46.2], [214.2, -50.7], [209.0, -57.4], [191.5, -46.0], [180.4, -58.6], [172.2, -51.6],
        [140.9, -47.6], [114.3, -62.4], [96.9, -75.5], [96.8, -80.4], [90.5, -80.2], [90.4, -86.1], [83.7, -86.0], [83.8, -80.1], [59.6, -81.8], [55.8, -79.4],
        [26.9, -101.3], [25.8, -106.1], [20.7, -104.9], [21.9, -100.0], [-8.3, -94.6], [-8.2, -103.1], [-23.9, -103.3], [-24.1, -87.7], [-58.2, -90.2], [-58.1, -93.7],
        [-62.4, -93.8], [-62.4, -90.4], [-92.0, -89.6], [-91.8, -93.8], [-103.6, -95.1], [-103.6, -92.1], [-121.8, -91.7], [-137.9, -97.2], [-143.0, -95.4], [-164.9, -98.2],
        [-164.6, -95.2], [-208.7, -68.8], [-210.8, -71.3], [-218.5, -67.5], [-220.0, -76.6], [-229.7, -75.1], [-228.2, -65.5], [-267.7, -59.2], [-267.4, -56.5], [-306.4, -46.2],
        [-307.9, -49.4], [-316.4, -40.9], [-315.9, -32.6], [-305.2, -23.9], [-306.9, -21.7], [-293.3, -11.3], [-289.3, -9.7], [-288.5, -14.2], [-271.9, -14.9], [-251.1, -13.0],
        [-250.2, -4.5], [-232.6, -2.9], [-231.9, -13.6], [-151.9, -8.8], [-129.1, 11.9], [-133.5, 19.2], [-126.3, 30.5], [-125.4, 36.1]]
ALCAZABA = [[-220.0, -76.6], [-229.7, -75.1], [-224.3, -49.2], [-236.4, -46.2], [-237.3, -50.2], [-260.1, -48.1], [-258.2, -26.7], [-253.2, -26.6], [-252.1, -16.1],
            [-246.2, -15.9], [-246.7, -8.1], [-238.8, -7.7], [-237.8, -21.0], [-225.2, -21.7], [-225.2, -19.6], [-216.4, -19.6], [-216.5, -22.0], [-165.1, -22.2],
            [-165.5, -17.6], [-156.4, -16.8], [-156.2, -41.9], [-152.1, -41.6], [-151.0, -57.5], [-155.4, -57.8], [-155.7, -70.2], [-149.3, -70.2], [-149.3, -82.0],
            [-160.2, -82.0], [-160.2, -73.5], [-162.8, -73.8], [-168.1, -70.4], [-170.4, -74.0], [-175.0, -71.1], [-173.0, -67.6], [-194.6, -55.2], [-197.0, -58.2],
            [-203.2, -54.5], [-201.3, -52.1], [-213.6, -46.4], [-217.2, -50.4]]

# THE TOWERS: (name, x, z, W, L, the W side's bearing in degrees from +x toward +z, options). `tall`: its terrace over the
# ground at its middle (default 13 m, and 3 m over the wall at least); `top`: the terrace's height in the frame instead;
# `hw` its hall storey, `win`/`ww`/`wsill`/`wspr` the hall's windows, `crest` merlons or roof; `gate`: a bab on its
# outer face ("out"), on both ("both").
TOWERS = [
    ("Torre de los Hidalgos", -261.9, -53.9, 11.8, 10.3, 83.6, {"tall": 14}),
    ("Torre de la Vela", -248.9, -36.9, 14.4, 15.2, 86.2, {"top": lv(781.0) + 26.8, "hw": 6.5, "win": 2}),
    ("Torre de la Polvora", -242.5, -11.8, 8.0, 7.8, 3.5, {"tall": 10}),
    ("Torre de las Armas", -222.7, -62.8, 12.0, 9.8, 80.7, {"tall": 15, "gate": "out"}),
    ("Torre de la Sultana", -220.8, -21.8, 8.8, 4.3, 0.1, {"tall": 9}),
    ("Torre de Alquiza", -198.4, -54.3, 7.9, 5.2, 148.7, {"tall": 12}),
    ("Torre del Criado del Doctor Ortiz", -171.2, -70.0, 5.7, 5.9, 149.1, {"tall": 12}),
    ("Torre Hueca", -160.5, -22.1, 9.9, 9.1, 95.1, {"tall": 15}),
    ("Torre Quebrada", -156.1, -49.8, 16.0, 9.1, 94.0, {"tall": 16}),
    ("Torre del Homenaje", -154.7, -76.1, 10.9, 11.8, 0.0, {"tall": 26, "hw": 6.5}),
    ("Torre de las Rocas", -130.5, 36.7, 7.5, 8.4, 18.2, {"tall": 12}),
    ("Puerta del Vino", -110.1, 6.2, 8.3, 7.5, 103.5, {"tall": 13, "gate": "both", "free": True}),
    ("Torre de Mohamed", -97.8, -90.2, 9.8, 11.9, 90.7, {"tall": 13}),
    ("Torre de la Justicia", -76.2, 64.1, 14.4, 13.9, 112.8, {"tall": 17, "gate": "out"}),
    ("Torre de Machuca", -60.3, -91.1, 5.1, 4.3, 91.4, {"top": PAL + 8}),
    ("Torre de Barba", -34.3, 73.2, 11.3, 3.5, 25.7, {"tall": 11}),
    ("Torre de Comares", -16.1, -95.35, 15.9, 15.9, 0.0, {"top": PAL + 23.0, "hw": 23.0, "win": 3, "ww": 1.6, "wsill": .3, "wspr": 4.2}),
    ("Torre de los Carros", 17.4, 88.1, 9.1, 4.1, 23.0, {"tall": 12}),
    ("Torre de Abu-l-Hayyay", 24.2, -101.6, 7.9, 5.2, 76.7, {"top": PAL + 12.0, "hw": 9.0, "win": 1, "ww": 1.4}),
    ("Torre de los Abencerrajes", 74.2, 118.7, 10.9, 7.0, 40.9, {"tall": 13}),
    ("Torre de las Damas", 87.1, -83.1, 5.9, 6.7, 89.2, {"top": PARTAL + 11.0, "hw": 11.0, "win": 1, "ww": 2.0, "wsill": .3, "wspr": 3.6, "crest": "roof"}),
    ("Torre de las Cabezas", 108.7, 163.9, 12.0, 12.0, 129.9, {"tall": 14}),
    ("Torre de la Bruja", 159.1, 189.1, 6.8, 6.4, 121.8, {"tall": 12}),
    ("Torre de los Picos", 179.4, -47.0, 8.5, 7.5, 141.5, {"tall": 15, "win": 1}),
    ("Torre del Capitan", 197.7, 206.0, 7.4, 8.5, 22.5, {"tall": 13}),
    ("Torre del Cadi", 241.5, 4.9, 9.1, 5.3, 136.9, {"tall": 12}),
    ("Torre de los Siete Suelos", 244.4, 230.6, 14.0, 12.0, 91.9, {"tall": 16, "gate": "out"}),
    ("Torre de la Cautiva", 284.3, 53.5, 13.8, 8.1, 151.4, {"tall": 15, "hw": 8.0, "win": 2}),
    ("Torre de Baltasar de la Cruz", 310.0, 220.7, 5.4, 9.5, 3.0, {"tall": 12}),
    ("Torre de las Infantas", 326.2, 109.5, 13.5, 9.9, 120.6, {"tall": 15, "hw": 8.0, "win": 2}),
    ("Torre de Juan de Arce", 344.9, 222.7, 10.3, 6.3, 68.1, {"tall": 12}),
    ("Torre del Agua", 381.9, 204.7, 11.2, 10.6, 2.4, {"tall": 13}),
    ("Torre del Cabo de la Carrera", 392.7, 154.4, 10.7, 8.9, 167.1, {"tall": 13}),
]

# =====================================================================================================================
# 3. THE NASRID PALACES: rectangles (x0, z0, x1, z1) from OSM, squared to the courts' axes
# =====================================================================================================================
site("palaces", [(-75.0, -88.5, 46.5, -19.0), (12.0, -92.0, 38.0, -67.0)], PAL)

PORTICO = "components/nasrid-portico"
HALLS = []                                                               # (every room built by hall(): the finish plasters them)
QUBBA = "components/qubba"


def hall(name, r, y, h, roof="hip", pitch=28, t=.8, faces=None, openings=None, about=None, roof_about=None, F=WORLD):
    """a room or a range of rooms on the rectangle r (in the frame F): walls t thick and h tall round it (doors and
    windows by face -- 0 +z (south), 1 +x (east), 2 -z, 3 -x, each measured from the face's middle), its roof of tiles"""
    w, l = r[2] - r[0], r[3] - r[1]
    at = F.at
    d = {"type": "enclosure", "plan": {"rect": [r4(w), r4(l)]}, "thickness": t, "height": h, "glass": False, "interior": True,
         "at": [at((r[0] + r[2]) / 2, y, (r[1] + r[3]) / 2)]}
    if faces: d["faces"] = {str(k): v for k, v in faces.items()}
    d["openings"] = openings or []
    D.add(name, d, about); HALLS.append(name)
    if roof == "flat":
        D.add(f"{name} roof", {"type": "box", "width": r4(w + .3), "length": r4(l + .3), "height": .35, "at": [at((r[0] + r[2]) / 2, y + h, (r[1] + r[3]) / 2)],
                               "flatRoof": True}, roof_about)
    elif roof:
        a, b, yaw = (w, l, 0.0) if w <= l else (l, w, Q)        # (the ridge along the longer side)
        D.add(f"{name} roof", {"type": "roof", "form": roof, "width": r4(a + .5), "length": r4(b + .5), "pitch": pitch,
                               "at": [at((r[0] + r[2]) / 2, y + h, (r[1] + r[3]) / 2, yaw)]}, roof_about)


def door(x, w=1.5, s=2.6, head=None):
    return {"at": r4(x), "width": w, "sill": 0, "springing": s, "head": head or {"profile": "semicircular"}, "glass": False}


def storeys(h, h0, lower, upper):
    """a face in two storeys (a face's openings may not stand over one another in one band): the ground storey h0 tall
    with `lower`, the upper one to the eaves with `upper`, their sills measured from its own floor"""
    return [{"h": r4(h0), "openings": lower}, {"h": r4(h - h0), "openings": upper}]


def window(x, w=.9, sill=1.2, s=2.6):
    return {"at": r4(x), "width": w, "sill": sill, "springing": s, "head": horseshoe(.2), "glass": False}


def portico(name, x, z, yaw, n, bay, about=None, y=PAL, F=WORLD, **p):
    """a Nasrid portico of n arches `bay` apart, centred at (x, z) on the floor at y, its arcade facing along yaw's +z"""
    D.comp(name, PORTICO, {"N": n, "bay": r4(bay), **p}, [F.at(x, y, z, yaw)], about=about)


def court(name, r, y, holes=(), about=None, F=WORLD):
    """a court's paving (the site's platform under it): its marble slabs, cut round the pools"""
    D.slabs(f"{name} paving", split(tiles(*r, list(holes)), 12), y, h=.06, about=about, walked=True, place=F.at)


def pool(name, r, y, about=None, F=WORLD):
    """a pool in the paving, brim-full: its water on the platform, 3 cm under the slabs' top (the basin under it is the
    platform's own -- not drawn)"""
    w, l = r[2] - r[0], r[3] - r[1]
    D.add(f"{name} water", {"type": "box", "width": r4(w), "length": r4(l), "height": .05, "at": [F.at((r[0] + r[2]) / 2, y - .02, (r[1] + r[3]) / 2)]}, about)


# ---- the Mexuar, the Cuarto Dorado ------------------------------------------------------------------------------------
hall("mexuar", (-51.75, -84.15, -40.25, -50.45), PAL, 8.5, faces={1: [door(-6.0, 1.6, 2.9), door(6.0, 1.6, 2.9)], 3: [window(k * 5.0) for k in range(-2, 3)]},
     about="the MEXUAR, the council hall (Ismail I, 1317; remade by Muhammad V), its lantern on four columns inside, and the rooms down to the Machuca court")
hall("mexuar oratory", (-49.4, -90.8, -40.4, -84.15), PAL, 6.0, faces={0: [door(0, 1.2, 2.3)], 2: [window(-2.4, .8), window(0, .8), window(2.4, .8)]},
     about="its oratory, out over the wall toward the Albaicin, the windows north")
court("machuca", (-74.0, -82.0, -52.0, -62.0), PAL, holes=[(-69.0, -73.5, -57.0, -70.5)], about="the Machuca court, before the Mexuar")
pool("machuca pool", (-69.0, -73.5, -57.0, -70.5), PAL)
portico("machuca portico", -63.0, -82.0, 0.0, 5, 2.6, about="its north portico", colH=2.6, H=5.4, spr=1.1, d=3.0)
hall("machuca range", (-70.0, -88.5, -56.0, -85.0), PAL, 6.0, faces={0: [door(0, 1.4, 2.5)]})
CD = (-40.25, -81.3, -33.0, -71.7)                                       # the Cuarto Dorado's court
court("cuarto dorado", CD, PAL, holes=[(-37.4, -77.2, -35.85, -75.6)], about="the Cuarto Dorado's court")
pool("cuarto dorado basin", (-37.4, -77.2, -35.85, -75.6), PAL)
portico("cuarto dorado portico", -36.6, -81.3, 0.0, 3, 2.2, about="the Cuarto Dorado's portico of three arches", colH=2.6, H=5.6, spr=1.0, d=2.4)
hall("cuarto dorado", (-40.25, -88.5, -33.0, -83.7), PAL, 7.0, faces={0: [door(0, 1.4, 2.6)], 2: [window(-1.8, .8), window(1.8, .8)]},
     about="the Cuarto Dorado, its ceiling gilded under the Catholic Monarchs -- here as Muhammad V left it")
hall("comares facade", (-40.25, -71.7, -33.95, -46.0), PAL, 9.5,
     faces={2: storeys(9.5, 4.0, [door(-1.4, 1.2, 2.4, {"profile": "flat"}), door(1.4, 1.2, 2.4, {"profile": "flat"})],
                       [window(-1.4, .7, .4, 1.3), window(0, .7, .4, 1.3), window(1.4, .7, .4, 1.3)])},
     about="the COMARES FACADE (1370): Muhammad V's throne front, two doors under a band of windows, the court of the Cuarto Dorado before it")
D.add("comares facade eave", {"type": "box", "width": 7.4, "length": 1.6, "height": .35, "at": [at(-37.1, PAL + 9.5, -72.1)]},
      "its great carved eave of cedar")

# ---- Comares: the Myrtles' court, the Sala de la Barca, the Hall of the Ambassadors in its tower ----------------------
MY = (-27.1, -76.3, -5.3, -41.1)                                         # the court (36.6 x 23 m measured; OSM 35.2 x 21.8)
MYP = (-20.65, -75.85, -13.15, -41.75)                                   # its pool
court("myrtles", MY, PAL, holes=[MYP], about="the COURT OF THE MYRTLES (Comares, Yusuf I and Muhammad V): white marble round the pool")
pool("myrtles pool", MYP, PAL, about="the pool, 34 m long, brim-full: the porticoes and the tower stand in it")
hedges(D, "myrtle hedges", [(-23.5, -73.0, -22.1, -44.6), (-11.7, -73.0, -10.3, -44.6)], PAL, h=1.1, about="the clipped myrtles along the pool's sides")
portico("myrtles north portico", -16.2, -76.3, 0.0, 7, 3.04, about="the north portico: seven arches before the Sala de la Barca",
        colH=2.9, H=7.2, spr=1.7, d=4.2, eave=1.0)
portico("myrtles south portico", -16.2, -41.1, math.pi, 7, 3.04, about="the south portico, with the gallery over it", colH=2.9, H=7.2, spr=1.7, d=3.6, eave=1.0)
hall("sala de la barca", (-32.0, -87.9, -1.5, -80.5), PAL, 9.0, faces={0: [door(0, 3.2, 3.6)]}, about="the SALA DE LA BARCA, the antechamber, its wooden vault an upturned hull")
hall("myrtles west range", (-33.95, -76.3, -27.1, -41.1), PAL, 9.5, faces={1: storeys(9.5, 4.6, [door(-8.0), door(8.0)], [window(x, .9, 1.0, 2.2) for x in (-12.0, -8.0, 8.0, 12.0)])},
     about="the ranges along the court: the women's rooms, two storeys, doors and windows on the court")
hall("myrtles east range", (-5.3, -76.3, 1.35, -41.1), PAL, 9.5,
     faces={3: storeys(9.5, 4.6, [door(-8.0), door(8.0)], [window(x, .9, 1.0, 2.2) for x in (-12.0, -8.0, 8.0, 12.0)])})
hall("myrtles south range", (-35.3, -37.5, -1.5, -30.9), PAL, 11.0, faces={2: [door(0, 2.0, 3.0)]}, about="the south range (pulled down for Charles V's palace; rebuilt)")
hall("royal baths", (1.35, -72.6, 10.25, -55.8), PAL, 4.4, roof="flat", faces={3: [door(4.0, 1.1, 2.2)]},
     about="the ROYAL BATHS of Comares (Ismail I): the Sala de las Camas, then the vaulted warm and hot rooms, half sunk in the hill")
D.add("bath vaults", {"type": "dome", "radius": 1.5, "thickness": .25, "sides": 12, "head": {"profile": "semicircular"},
                      "at": [at(5.8, PAL + 4.75, z) for z in (-69.8, -66.0, -61.6, -58.0)]},
      "the baths' vaults over the roof, pierced with star-shaped skylights (the finish's)")

# ---- the Palace of the Lions (Muhammad V, 1362-1391) -----------------------------------------------------------------
LC = (21.25, -41.45)                                                     # the fountain
court("lions", (7.0, -49.3, 35.5, -33.6), PAL, about="the COURT OF THE LIONS: 28.5 x 15.7 m, marble")
portico("lions north portico", LC[0], -49.3, 0.0, 14, 2.0, about="its galleries: 124 columns, the arches stilted, the walls over them lace of plaster",
        colH=2.55, H=5.2, spr=1.0, d=2.6, pierW=.45, colR=.12)
portico("lions south portico", LC[0], -33.6, math.pi, 14, 2.0, colH=2.55, H=5.2, spr=1.0, d=2.6, pierW=.45, colR=.12)
portico("lions west portico", 7.0, LC[1], Q, 7, 2.17, colH=2.55, H=5.2, spr=1.0, d=2.7, pierW=.45, colR=.12)
portico("lions east portico", 35.5, LC[1], -Q, 7, 2.17, colH=2.55, H=5.2, spr=1.0, d=2.5, pierW=.45, colR=.12)
for k, x in enumerate((9.6, 32.9)):
    D.comp(f"lions {'west' if k == 0 else 'east'} pavilion", QUBBA, {"W": 5.4, "t": .45, "h": 9.6, "wh": 1.6, "win": 1, "dw": 3.4, "ds": 3.0, "pitch": 28},
           [at(x, PAL, LC[1])], about="the two pavilions standing out into the court at its ends, each a small qubba on clustered columns" if k == 0 else None)
D.comp("lions fountain lions", "components/couchant-lion", {"S": 1.05, "plinthH": .05},
       [at(LC[0] + 1.3 * math.sin(2 * math.pi * k / 12), PAL + .06, LC[1] + 1.3 * math.cos(2 * math.pi * k / 12), 2 * math.pi * k / 12) for k in range(12)],
       about="the FOUNTAIN OF THE LIONS: twelve lions of marble, the water from their mouths")
LION_TOP = .7                                                            # (their backs: the basin rests on them, their manes inside it)
D.add("fountain basin", {"type": "prism", "plan": {"sides": 12, "radius": 1.5}, "height": .32, "flatRoof": True, "at": [at(LC[0], PAL + LION_TOP - .1, LC[1])]},
      "the twelve-sided basin on their backs, Ibn Zamrak's verses round its rim")
D.add("fountain water", {"type": "prism", "plan": {"sides": 12, "radius": 1.32}, "height": .04, "at": [at(LC[0], PAL + LION_TOP + .22, LC[1])]})
D.add("fountain stem", {"type": "column", "radius": .16, "height": .55, "sides": 12, "at": [at(LC[0], PAL + LION_TOP + .22, LC[1])]})
D.add("fountain bowl", {"type": "prism", "plan": {"sides": 12, "radius": .5}, "height": .14, "at": [at(LC[0], PAL + LION_TOP + .77, LC[1])]})
D.add("channels", {"type": "box", "width": .28, "length": 1.0, "height": .05,
                   "at": [at(LC[0] + dx * s, PAL + .06, LC[1] + dz * s, 0.0 if dz else Q) for dx, dz, n in ((1, 0, 9), (-1, 0, 9), (0, 1, 6), (0, -1, 6))
                          for s in [2.1 + k for k in range(n)]]},
      "the channels from the fountain to the pavilions and the halls, the water flowing into the rooms")
# (the two great halls are qubbas standing IN their ranges: the ranges are built round them, not over them)
DH = (22.3, -56.6, 9.4)                                                  # the Two Sisters: its middle, its width (its front on the court's range face)
hall("lions north range", (4.3, -63.2, DH[0] - DH[2] / 2, -51.9), PAL, 8.5, faces={1: [door(0, 1.4, 2.6)]},
     about="the north range, the Two Sisters' hall rising in its middle")
hall("lions north range east", (DH[0] + DH[2] / 2, -63.2, 38.0, -51.9), PAL, 8.5, faces={3: [door(0, 1.4, 2.6)]})
hall("dos hermanas back", (DH[0] - DH[2] / 2, -63.2, DH[0] + DH[2] / 2, DH[1] - DH[2] / 2), PAL, 8.5, roof="flat", faces={0: [door(0, 1.6, 2.6)]})
D.comp("dos hermanas", QUBBA, {"W": DH[2], "t": .7, "h": 15.5, "win": 2, "dw": 3.0, "ds": 4.2},
       [at(DH[0], PAL, DH[1])], about="the HALL OF THE TWO SISTERS: the muqarnas dome of some five thousand cells over its drum of windows")
hall("ajimeces", (14.0, -66.9, 30.6, -63.2), PAL, 7.0, faces={2: [window(-3.5, 1.2, .9, 2.4), window(3.5, 1.2, .9, 2.4)]},
     about="the Ajimeces hall behind it")
hall("daraxa mirador", (18.6, -70.2, 22.4, -66.9), PAL, 7.0, faces={2: [window(0, 1.6, .8, 2.6)], 1: [window(0, .9, .8, 2.4)], 3: [window(0, .9, .8, 2.4)]},
     about="the MIRADOR OF DARAXA, the lady's window on the garden and the city below")
AB = (19.8, -25.5, 11.0)                                                 # the Abencerrajes: the range's whole depth
hall("lions south range", (4.3, -31.0, AB[0] - AB[2] / 2, -20.0), PAL, 8.5, faces={1: [door(0, 1.4, 2.6)]}, about="the south range")
hall("lions south range east", (AB[0] + AB[2] / 2, -31.0, 38.0, -20.0), PAL, 8.5, faces={3: [door(0, 1.4, 2.6)]})
D.comp("abencerrajes", QUBBA, {"W": AB[2], "t": .9, "h": 15.5, "win": 2, "dw": 3.4, "ds": 4.2}, [at(AB[0], PAL, AB[1])],
       about="the HALL OF THE ABENCERRAJES: its star of muqarnas over the fountain")
hall("mocarabes", (-1.7, -53.5, 4.3, -32.9), PAL, 9.0, faces={1: [door(0, 3.0, 3.4)]}, about="the Hall of the Mocarabes, the court's vestibule")
hall("sala de los reyes", (38.0, -55.2, 45.8, -28.2), PAL, 9.0, faces={3: [door(-9.0, 2.4, 3.2), door(0, 2.4, 3.2), door(9.0, 2.4, 3.2)]},
     about="the HALL OF THE KINGS: three domed alcoves behind triple arches, the painted leather vaults")
LIND = (14.0, -89.4, 35.5, -70.2)                                        # the garden, open to the valley in Nasrid times
D.add("lindaraja fountain", {"type": "prism", "plan": {"sides": 12, "radius": 1.0}, "height": .5, "flatRoof": True, "at": [at(27.0, PAL, -79.8)]},
      "the garden's fountain basin")
plant(D, "orange", [(x, PAL, z) for x in (17.0, 21.0, 31.5) for z in (-87.0, -83.0, -76.0, -72.5)], about="the LINDARAJA garden's orange trees")
plant(D, "cypress", [(x, PAL, z) for x, z in ((16.0, -79.8), (34.0, -79.8), (27.0, -87.5), (27.0, -72.0))])

# =====================================================================================================================
# 4. THE PARTAL (Yusuf III's portico and the Damas tower, 1302-1325), its pond; the oratory
# =====================================================================================================================
site("partal", [(74.0, -80.0, 100.0, -44.0), (97.0, -67.5, 111.0, -55.0)], PARTAL)
PP = (82.6, -74.2, 95.8, -47.4)
court("partal", (76.0, -77.0, 98.0, -44.5), PARTAL, holes=[PP], about="the Partal's terrace")
pool("partal pond", PP, PARTAL, about="the pond before the portico")
portico("partal portico", 87.1, -77.0, 0.0, 5, 2.5, about="THE PARTAL: a portico of five arches on the pond, the Damas tower behind it",
        colH=2.7, H=6.0, spr=1.2, d=2.75, y=PARTAL)
for k, (x0, x1) in enumerate(((80.6, 84.15), (90.05, 93.6))):
    D.add(f"partal back wall {k + 1}", {"type": "wall", "width": r4(x1 - x0), "height": 6.0, "thickness": .6, "glass": False, "openings": [],
                                        "at": [wall_at((x0 + x1) / 2, PARTAL, -79.75, 0.0, .6)]}, "the walls beside the tower" if k == 0 else None)
hall("partal oratory", (104.2, -66.6, 108.4, -63.6), PARTAL, 5.5, faces={0: [door(0, 1.0, 2.2)], 1: [window(0, .7, 1.4, 2.6)]},
     about="the Partal's ORATORY (Yusuf I), its mihrab in a niche to the south-east, the windows out over the wall")
hall("partal house", (98.0, -63.0, 104.0, -56.0), PARTAL, 6.0, faces={3: [door(0, 1.2, 2.4)]}, about="the house beside it (Astasio de Bracamonte's)")

# =====================================================================================================================
# 5. THE GENERALIFE (Jannat al-'Arif): the sultans' country palace across the ravine, as Ismail I remade it (1319)
# =====================================================================================================================
# Its own frame, turned along the Court of the Water Channel: u across the court (+u east-north-east), v along it (+v
# toward the south pavilion), the court's middle at its origin (OSM: the palace 51683601, the court 268563933, the Sala
# Regia 1079185009, the Sultana's court 268563942, the upper gardens 1079185019 -- in this frame all square to it).
GF = Frame(348.2, -146.9, 38.0)
GY = site("generalife", [(-9.5, -34.0, 10.3, 31.0), (-11.4, -5.7, -9.5, .8), (-1.2, -38.5, 4.1, -34.0), (10.3, 4.5, 12.2, 31.0)], lv(798.0), GF)
GS = site("sultana", [(10.3, -27.0, 26.1, -4.3)], lv(800.0), GF)
GE = site("generalife entrance", [(-31.3, 18.6, -9.5, 39.1)], lv(792.5), GF)


def fwall(name, F, u0, v0, u1, v1, y, h, t=.7, openings=(), about=None):
    """a free wall in the frame F from (u0, v0) to (u1, v1), centred on that line (along u or along v); its openings'
    `at` given as the u (or v) of their middle -- a wall measures them from its own start, which this works out"""
    L, yaw = (abs(u1 - u0), 0.0) if v0 == v1 else (abs(v1 - v0), Q)
    cu, cv = (u0 + u1) / 2, (v0 + v1) / 2
    # (a wall's local +x runs along +u at yaw 0, along -v at a quarter turn: its start is at the least u, the greatest v)
    ops = [{**o, "at": r4(o["at"] - (cu - L / 2) if yaw == 0.0 else (cv + L / 2) - o["at"])} for o in openings]
    D.add(name, {"type": "wall", "width": r4(L), "height": h, "thickness": t, "glass": False, "openings": ops,
                 "at": [F.at(cu + t / 2 * math.sin(yaw), y, cv + t / 2 * math.cos(yaw), yaw)]}, about)
    HALLS.append(name)                                                     # (whitewashed, as the rooms are)


# ---- the Court of the Water Channel -----------------------------------------------------------------------------------
ACQ = [(-.45, -24.6, .45, -1.3), (-.45, 1.3, .45, 24.6)]                 # the channel, in two runs either side of the basin
BEDS = [(-4.7, -24.0, -1.1, -1.6), (1.1, -24.0, 4.7, -1.6), (-4.7, 1.6, -1.1, 24.0), (1.1, 1.6, 4.7, 24.0)]
court("acequia", (-5.3, -25.2, 5.3, 25.2), GY, holes=ACQ + BEDS + [(-1.1, -1.3, 1.1, 1.3)], F=GF,
      about="THE GENERALIFE: the COURT OF THE WATER CHANNEL, 50 m long, the acequia down its middle between sunk beds")
pool("acequia channel", ACQ[0], GY, F=GF, about="the channel, the Acequia Real's water running through the court")
pool("acequia channel 2", ACQ[1], GY, F=GF)
pool("acequia basin", (-1.1, -1.3, 1.1, 1.3), GY, F=GF)
D.add("acequia beds", {"type": "box", "width": 3.6, "length": 22.4, "height": .4,
                       "at": [GF.at((b[0] + b[2]) / 2, GY - .4, (b[1] + b[3]) / 2) for b in BEDS]},
      "the beds, sunk under the walks: myrtle, roses, orange trees")
portico("generalife north portico", 0, -25.2, 0.0, 5, 2.0, F=GF, y=GY, colH=2.6, H=5.8, spr=1.0, d=3.0, pierW=.5,
        about="the NORTH PAVILION: its portico of five arches on the court (the gallery over it is of 1494: left out)")
hall("sala regia", (-10.9, -34.0, 10.3, -28.2), GY, 7.5, F=GF, faces={0: [door(-3.0, 1.3, 2.6), door(0, 2.0, 3.0), door(3.0, 1.3, 2.6)],
                                                                   2: [window(-7.0, .9, 1.0), window(7.0, .9, 1.0)]},
     about="the SALA REGIA behind it, its triple arch, the windows over the city")
hall("generalife north room west", (-9.5, -28.2, -5.3, -25.2), GY, 6.0, F=GF, faces={1: [door(0, 1.0, 2.2)]})
hall("generalife north room east", (5.3, -28.2, 10.3, -25.2), GY, 6.0, F=GF, faces={3: [door(0, 1.0, 2.2)]})
portico("generalife south portico", 0, 25.2, math.pi, 5, 2.0, F=GF, y=GY, colH=2.6, H=5.4, spr=1.0, d=2.6, pierW=.5,
        about="the SOUTH PAVILION's portico")
hall("generalife south pavilion", (-6.0, 27.8, 12.2, 31.0), GY, 6.5, F=GF, faces={2: [door(3.1, 2.0, 2.8)]})
portico("generalife west gallery", -5.3, -3.25, Q, 18, 2.4, F=GF, y=GY, colH=2.4, H=5.0, spr=1.0, d=3.6, pierW=.5,
        about="the WEST GALLERY: eighteen arches on the court, windows in its back wall over the Alhambra")
fwall("generalife west gallery wall", GF, -9.2, -25.1, -9.2, 18.6, GY, 5.0, t=.6,
      openings=[window(v, .8, 1.0, 2.2) for v in (-21.0, -16.0, -11.0, 6.0, 11.0, 16.0)] + [door(-2.45, 2.6, 2.8)])
hall("generalife mirador", (-11.4, -5.7, -9.5, .8), GY, 5.0, F=GF, roof="flat", t=.5,
     faces={3: [window(-1.6, .8, .9, 2.2), window(0, .8, .9, 2.2), window(1.6, .8, .9, 2.2)]},
     about="its MIRADOR, standing out over the slope in the gallery's middle")
hall("generalife east range", (5.3, -25.2, 10.3, 25.2), GY, 8.5, F=GF,
     faces={3: storeys(8.5, 4.2, [door(-12.0), door(0, 1.8, 2.8), door(12.0)], [window(v, .9, 1.0, 2.2) for v in (-18.0, -6.0, 6.0, 18.0)])},
     about="the east range, rooms on two floors")

# ---- the Sultana's garden; the entrance courts ------------------------------------------------------------------------
SP = (16.2, -19.5, 20.2, -11.8)
court("sultana", (10.3, -27.0, 26.1, -4.3), GS, holes=[SP], F=GF, about="the garden court beside it (the Sultana's: its galleries of 1584 left out)")
pool("sultana pool", SP, GS, F=GF)
fwall("sultana wall north", GF, 10.3, -26.65, 26.1, -26.65, GS, 3.5)
fwall("sultana wall east", GF, 25.75, -27.0, 25.75, -4.3, GS, 3.5, openings=[door(-10.0, 1.4, 2.4)])
court("generalife entrance", (-31.3, 18.6, -9.5, 39.1), GE, F=GF, about="the ENTRANCE COURTS below the palace (the Polo and the Descabalgamiento)")
fwall("generalife entrance wall north", GF, -31.3, 18.95, -9.5, 18.95, GE, 5.0)
fwall("generalife entrance wall south", GF, -31.3, 38.75, -9.5, 38.75, GE, 5.0)
fwall("generalife entrance wall west", GF, -30.95, 18.6, -30.95, 39.1, GE, 5.0, openings=[door(28.85, 2.4, 3.2, horseshoe(.3))])
fwall("generalife entrance cross wall", GF, -20.7, 19.3, -20.7, 38.4, GE, 4.5, openings=[door(28.85, 2.0, 2.8, horseshoe(.3))])
D.comp("generalife gate", "components/bab", {"W": 5.0, "H": 8.4, "dw": 2.4, "ds": 3.2, "over": .3, "crest": "none", "bn": 3},
       [GF.at(-31.3, GE, 28.85, -Q)], about="its gate, before the wall's outer face")
# the WATER STAIR up the hill behind the Sultana's garden to the oratory at the top: three flights (u0, base, top) and
# their landings, cut into the slope (carved, not platformed: each flight is carried on its own masonry)
WSTAIR, WRUN, WRISE, WLAND = [(26.1, GS, GS + 3.4), (35.3, GS + 3.4, GS + 6.8), (44.5, GS + 6.8, GS + 10.2)], .34, .17, 2.4
WS_LEN = [round((t - b) / WRISE) * WRUN + (WLAND if k < 2 else 0) for k, (u0, b, t) in enumerate(WSTAIR)]
for k, (u0, b, t) in enumerate(WSTAIR):
    site(f"water stair {k + 1}", [(u0, -11.6, u0 + WS_LEN[k], -8.4)], b, GF, platform=False)
GO = site("generalife oratory", [(51.3, -14.0, 58.5, -6.0)], WSTAIR[-1][2], GF)
D.add("generalife entrance stair", {"type": "flight", "width": 2.4, "run": .31, "rise": .17, "base": GE, "top": GY, "landing": 0,
                                    "at": [GF.at(-9.5 - round((GY - GE) / .17) * .31, 0, 22.0 + 1.2)]},
      "the stair up to the court")

# =====================================================================================================================
# 6. THE MEDINA: the mosque and its baths, the palaces along the Calle Real, the houses
# =====================================================================================================================
MOS = site("mosque", [(0.0, 2.0, 42.0, 50.0)], lv(780.0))
hall("mosque", (6.0, 24.0, 36.0, 44.0), MOS, 6.8, roof=None, t=.7,
     faces={0: [{"at": 0, "width": 1.6, "sill": 0, "springing": 2.6, "head": horseshoe(.3), "glass": False}],
            2: [door(-10.0, 1.8, 3.0, horseshoe(.3)), door(0, 2.2, 3.4, horseshoe(.3)), door(10.0, 1.8, 3.0, horseshoe(.3))]},
     about="THE GREAT MOSQUE of the Alhambra (Muhammad III, 1305): a hall of three naves, the qibla wall to the south")
for k, x in enumerate((16.0, 26.0)):
    portico(f"mosque arcade {k + 1}", x, 34.0, Q, 5, 3.6, about="its arcades, the naves' arches on marble columns" if k == 0 else None,
            colH=3.0, H=6.8, spr=1.0, d=9.3, eave=0, roof="no", head="horseshoe", over=.25, y=MOS)
D.add("mosque east ceiling", {"type": "box", "width": 9.3, "length": 18.6, "height": .25, "at": [at(31.0, MOS + 6.55, 34.0)]}, "the east nave's ceiling")
D.add("mosque roofs", {"type": "roof", "form": "gable", "width": 10.4, "length": 20.6, "pitch": 24, "at": [at(x, MOS + 6.8, 34.0) for x in (11.0, 21.0, 31.0)]},
      "a gable roof of tiles over each nave")
D.add("mihrab", {"type": "enclosure", "plan": {"sides": 8, "radius": 1.9}, "thickness": .5, "height": 4.6, "glass": False,
                 "faces": {"3": [{"at": 0, "width": 1.2, "sill": 0, "springing": 2.4, "head": horseshoe(.3), "glass": False}]}, "openings": [],
                 "at": [at(21.0, MOS, 43.85 + 1.9 * math.cos(math.pi / 8))]}, "the octagonal mihrab, out from the qibla wall")
D.add("mihrab dome", {"type": "dome", "radius": 1.9 * math.cos(math.pi / 8), "thickness": .2, "sides": 8, "head": {"profile": "semicircular"},
                      "at": [at(21.0, MOS + 4.6, 43.85 + 1.9 * math.cos(math.pi / 8))]}, "its dome")
court("mosque court", (6.0, 4.0, 36.0, 24.0), MOS, about="the court, orange trees in rows on the naves' axes")
for k, (x, z, L, yaw) in enumerate(((21.0, 4.0, 30.0, 0.0), (6.0, 14.0, 20.0, Q), (36.0, 14.0, 20.0, Q))):
    D.add(f"mosque court wall {k + 1}", {"type": "wall", "width": L + (.7 if yaw == 0 else -.7), "height": 5.0, "thickness": .7, "glass": False,
                                         "openings": [door(L / 2, 2.0, 3.0, horseshoe(.3))] if k == 0 else [],
                                         "at": [wall_at(x, MOS, z, yaw, .7)]}, "the court's walls" if k == 0 else None)
D.comp("mosque minaret", "components/alminar", {"W": 4.6, "H": 19.0, "tw": .9, "lw": 2.6, "lh": 3.4, "yam": 2.2, "ts": 3.6, "pw": .6, "bh": 2.4, "bn": 5, "bw": .32, "th": 1.8}, [at(9.0, MOS, 7.0)],
       about="the minaret at the court's corner")
plant(D, "orange", [(x, MOS, z) for x in (11.0, 16.0, 21.0, 26.0, 31.0) for z in (12.0, 18.0)], name="mosque orange",
      about="the court's orange trees")
BM = site("mosque baths", [(47.0, 45.0, 66.0, 61.0)], round(ground(56.5, 53.0), 1))
hall("mosque baths", (49.0, 47.0, 64.0, 59.0), BM, 4.4, roof="flat", faces={3: [door(0, 1.2, 2.2)]},
     about="the MOSQUE'S BATHS (1305): the dressing hall, the cold, warm and hot rooms")
D.add("mosque baths vaults", {"type": "dome", "radius": 1.6, "thickness": .25, "sides": 12, "head": {"profile": "semicircular"},
                              "at": [at(x, BM + 4.75, z) for x, z in ((53.0, 50.5), (53.0, 55.5), (59.5, 50.5), (59.5, 55.5))]}, "their vaults, starred with skylights")


def riad(name, r, y, about):
    """a palace of the medina: a court with a long pool, a portico at either end, ranges of rooms round it"""
    x0, z0, x1, z1 = r; dd = 5.0
    cx = (x0 + x1) / 2; c = (x0 + dd, z0 + dd + 3.0, x1 - dd, z1 - dd - 3.0)          # the court (its porticoes' galleries 3 m deep at the ends)
    pw = min(4.0, (c[2] - c[0]) * .3); pl = (cx - pw / 2, c[1] + 2.0, cx + pw / 2, c[3] - 2.0)
    court(name, c, y, holes=[pl], about=about)
    pool(f"{name} pool", pl, y)
    n = max(3, int((c[2] - c[0] - .5) / 2.8)); bay = (c[2] - c[0] - .5) / n
    portico(f"{name} north portico", cx, c[1], 0.0, n, bay, colH=2.6, H=5.6, spr=1.1, d=3.0, y=y)
    portico(f"{name} south portico", cx, c[3], math.pi, n, bay, colH=2.6, H=5.6, spr=1.1, d=3.0, y=y)
    hall(f"{name} north range", (x0, z0, x1, c[1] - 3.0), y, 7.5, faces={0: [door(0, 1.8, 2.8)]})
    hall(f"{name} south range", (x0, c[3] + 3.0, x1, z1), y, 7.5, faces={2: [door(0, 1.8, 2.8)]})
    hall(f"{name} west range", (x0, c[1] - 3.0, c[0], c[3] + 3.0), y, 7.0, faces={1: [door(0, 1.4, 2.6)]})
    hall(f"{name} east range", (c[2], c[1] - 3.0, x1, c[3] + 3.0), y, 7.0, faces={3: [door(0, 1.4, 2.6)]})
    return c


PALACES = [("yusuf III palace", (124.0, -17.0, 150.0, 15.0), "the PALACE OF YUSUF III (1408-17's rebuilding of an older one): its court and pool, rebuilt from the excavated plan"),
           ("abencerrajes palace", (88.0, 98.0, 118.0, 128.0), "the palace of the Abencerrajes, blown up in 1812: rebuilt"),
           ("san francisco palace", (200.0, 12.0, 230.0, 40.0), "the Nasrid palace under the convent of San Francisco (Yusuf I's), its court and pool")]
PAL_COURTS = []
for nm, r, about in PALACES:
    y = site(nm, [r], round(sum(ground(x, z) for x in (r[0], r[2]) for z in (r[1], r[3])) / 4, 1))
    PAL_COURTS.append(riad(nm, r, y, about))
    cc = PAL_COURTS[-1]
    plant(D, "cypress", [((cc[0] + cc[2]) / 2 + sx * ((cc[2] - cc[0]) / 2 - 1.0), y, (cc[1] + cc[3]) / 2 + sz * 3.0) for sx in (-1, 1) for sz in (-1, 1)],
          name=f"{nm} cypress")

# =====================================================================================================================
# 7. THE WALLS AND THE TOWERS
# =====================================================================================================================
# (every site declared: the hill cut down under them now -- and a cell round them -- before anything reads the ground
#  to stand on it: a tower's foot, a house's, the wall's walk)
M = 5.5
for j in range(NZ):
    for i in range(NX):
        x, z = node_xz(i, j)
        for S in SITES:
            if on_site(S, x, z, M): GH[j][i] = min(GH[j][i], max(0.0, S[2] - .05))

WT, WH, PH = 2.4, 9.0, 1.0                     # the curtain wall's thickness, its walk over the ground, the breastwork


def site_at(x, z, m=0.0):
    for S in SITES:
        if on_site(S, x, z, m): return S[2]
    return None


def dense(P, step=2.0, closed=True):
    out = []
    for i in range(len(P) if closed else len(P) - 1):
        a, b = P[i], P[(i + 1) % len(P)]; n = max(1, math.ceil(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out


def ma(v, n=2): return [sum(v[(i + k) % len(v)] for k in range(-n, n + 1)) / (2 * n + 1) for i in range(len(v))]


def wall_loop(name, P, H, about):
    """a curtain wall round the closed outline P: its walk H over the ground (smoothed), let down to just under the floor
    where a building stands on it (the palaces' own walls are the defence there); a breastwork and merlons on its
    outer edge elsewhere. One sweep for the body, one for each run of breastwork, the merlons as one part."""
    pts = dense(P)
    tops = ma([site_at(x, z, 1.0) - .1 if site_at(x, z, 1.0) is not None else ground(x, z) + H for x, z in pts], 2)
    lowest = min(ground(x, z) for x, z in pts)
    depth = max(t - ground(x, z) for t, (x, z) in zip(tops, pts)) + 2.0
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(P, P[1:] + P[:1])) / 2
    out = 1 if area < 0 else -1                # (the right of the way the path runs is the outside on a loop that turns so)
    u0, u1 = -WT / 2, WT / 2
    D.add(name, {"type": "sweep", "closed": True, "step": 2.0, "path": [[r4(x), r4(t), r4(z)] for (x, z), t in zip(pts, tops)],
                 "profile": [[u0, r4(-depth)], [u1, r4(-depth)], [u1, 0], [u0, 0]]}, about)
    runs, cur = [], []
    for k, ((x, z), t) in enumerate(zip(pts, tops)):
        if site_at(x, z, 3.0) is None: cur.append(k)
        elif cur: runs.append(cur); cur = []
    if cur:
        if runs and runs[0][0] == 0: runs[0] = cur + runs[0]
        else: runs.append(cur)
    bw = [[r4(out * (WT / 2 - .55)), 0], [r4(out * WT / 2), 0], [r4(out * WT / 2), PH], [r4(out * (WT / 2 - .55)), PH]]
    if out < 0: bw = bw[::-1]
    merl = []
    for k, run in enumerate(r for r in runs if len(r) >= 3):
        D.add(f"{name} breastwork {k + 1}", {"type": "sweep", "step": 2.0, "path": [[r4(pts[i][0]), r4(tops[i] - .02), r4(pts[i][1])] for i in run], "profile": bw},
              "the breastwork along the walk's outer edge" if k == 0 else None)
        for i in run[1:-1]:
            (xa, za), (xb, zb) = pts[i - 1], pts[(i + 1) % len(pts)]
            (xc, zc) = pts[i]
            turn = abs(math.remainder(math.atan2(zb - zc, xb - xc) - math.atan2(zc - za, xc - xa), math.tau))
            if turn > .6: continue                 # (not on a sharp corner: the merlon would stand off the turning walk)
            L = math.hypot(xb - xa, zb - za) or 1.0; tx, tz = (xb - xa) / L, (zb - za) / L
            rx, rz = -tz, tx                   # (range.js: the right of a segment is (-e.z, e.x))
            merl.append(at(pts[i][0] + out * rx * (WT / 2 - .275), tops[i] - .02 + PH, pts[i][1] + out * rz * (WT / 2 - .275), -math.atan2(tz, tx)))
    D.add(f"{name} merlons", {"type": "box", "width": 1.0, "length": .55, "height": 1.2, "at": merl}, "the square merlons, one every two metres")
    return lowest


wall_loop("city wall", RING, WH, "THE WALL round the palace-city, some two kilometres of rammed earth and lime on the Sabika's edge, its walk 9 m over the ground")
wall_loop("alcazaba wall", ALCAZABA, 11.0, "the ALCAZABA's own walls, the citadel at the hill's western point (9th-13th c.)")


def tower(name, x, z, W, L, deg, o, about=None):
    yaw = -math.radians(deg)
    c, s = math.cos(yaw), math.sin(yaw)
    corners = [(x + c * u + s * v, z - s * u + c * v) for u in (-W / 2, W / 2) for v in (-L / 2, L / 2)]
    foot = min(ground(px, pz) for px, pz in corners + [(x, z)]) - 1.0
    if "top" in o: top = o["top"]
    else: top = max(ground(x, z) + o.get("tall", 13.0), ground(x, z) + WH + 3.0)
    hw = min(o.get("hw", 5.5), top - foot - 1.0)
    p = {"W": r4(W), "L": r4(L), "H": r4(top - foot), "hw": r4(hw), "tw": r4(min(1.4, min(W, L) * .2)), "win": o.get("win", 1), "ww": o.get("ww", 1.1),
         "crest": o.get("crest", "merlons")}
    for k in ("wsill", "wspr"):
        if k in o: p[k] = o[k]
    D.comp(name, "components/torre", p, [at(x, foot, z, yaw)], about=about)
    gate = o.get("gate")
    if gate:
        n = (s, c)                             # (the tower's local +z, out of its L side)
        sides = [1, -1] if gate == "both" else [1 if not poly_in(RING, x + n[0] * (L / 2 + 4), z + n[1] * (L / 2 + 4)) else -1]
        for k, sg in enumerate(sides):
            gy = ground(x + sg * n[0] * (L / 2 + 1), z + sg * n[1] * (L / 2 + 1))
            D.comp(f"{name} gate {k + 1}" if len(sides) > 1 else f"{name} gate", "components/bab",
                   {"W": r4(min(W - 1.0, 7.0)), "H": r4(min(top - gy - 2.0, 11.0)), "dw": 3.0, "ds": 4.2, "over": .3, "crest": "none", "bn": 3 if W < 9 else 5},
                   [at(x + sg * n[0] * L / 2, gy, z + sg * n[1] * L / 2, yaw if sg > 0 else yaw + math.pi)],
                   about="its gate: a great horseshoe arch in its alfiz, the passage turning inside")


for nm, x, z, W, L, deg, o in TOWERS:
    tower(nm.lower().replace("torre de los ", "").replace("torre de las ", "").replace("torre de la ", "").replace("torre del ", "").replace("torre de ", "")
          .replace("torre ", "").replace("puerta del ", "").replace("puerta de la ", "") + (" gate" if nm.startswith("Puerta") else " tower"), x, z, W, L, deg, o)

# =====================================================================================================================
# 8. THE GENERALIFE's tower, its water stair and oratory; the Silla del Moro; the Albercon; the orchards
# =====================================================================================================================
tx, tz = GF.w(1.45, -36.25)
tower("ismail tower", tx, tz, 5.3, 4.5, -38.0, {"top": GY + 14.0, "hw": 5.0, "win": 1, "ww": 1.4},
      about="the TOWER OF ISMAIL I behind the Sala Regia, its hall a mirador over the Darro")
plant(D, "orange", [(GF.w(u, v)[0], GY, GF.w(u, v)[1]) for u in (-2.9, 2.9) for v in (-20.0, -13.0, -6.0, 6.0, 13.0, 20.0)], name="generalife orange",
      about="the court's orange trees")
plant(D, "cypress", [(GF.w(u, v)[0], GS, GF.w(u, v)[1]) for u, v in ((14.0, -23.0), (22.5, -23.0), (14.0, -8.5), (22.5, -8.5))], name="generalife cypress",
      about="the Sultana's cypresses")
for k, (u0, b, t) in enumerate(WSTAIR):
    L = WS_LEN[k]
    low = min(ground(*GF.w(u0 + L * i / 6, v)) for i in range(7) for v in (-11.2, -10.0, -8.8))
    D.add(f"water stair {k + 1}", {"type": "flight", "width": 2.4, "run": WRUN, "rise": WRISE, "base": r4(b), "top": r4(t),
                                   "landing": 0, "ground": r4(min(low, b) - .3), "at": [GF.at(u0, 0, -10.0 + 1.2)]},
          "the WATER STAIR (Escalera del Agua): three flights and their landings up to the oratory" if k == 0 else None)
    if k < 2:                                                              # (its landing: a floor of its own, walked, the next flight's foot)
        run = round((t - b) / WRISE) * WRUN
        D.add(f"water stair landing {k + 1}", {"type": "box", "width": WLAND, "length": 2.4, "height": r4(t - (min(low, b) - .3)),
                                               "at": [GF.at(u0 + run + WLAND / 2, r4(min(low, b) - .3), -10.0)], "walked": True, "flatRoof": True})
WPATH = []                                                               # (the parapets' top line: up each flight, along its landing)
for k, (u0, b, t) in enumerate(WSTAIR):
    run = round((t - b) / WRISE) * WRUN
    WPATH += [(u0 + run * i / 6, b + (t - b) * i / 6) for i in range(7)]
    if k < 2: WPATH.append((u0 + WS_LEN[k], t))
for side, vv in (("north", -11.4), ("south", -8.6)):
    path = [[r4(GF.w(u, vv)[0]), r4(y + .9), r4(GF.w(u, vv)[1])] for u, y in WPATH]
    D.add(f"water stair parapet {side}", {"type": "sweep", "path": path, "profile": [[-.2, -3.4], [.2, -3.4], [.2, 0], [-.2, 0]]},
          "its parapets, the water running down a channel cut in their tops" if side == "north" else None)
    D.add(f"water stair channel {side}", {"type": "sweep", "path": path, "profile": [[-.08, 0], [.08, 0], [.08, .04], [-.08, .04]]})
D.comp("generalife oratory", QUBBA, {"W": 5.0, "t": .5, "h": 7.0, "wh": 1.4, "win": 1, "dw": 2.2, "ds": 2.8, "pitch": 28}, [GF.at(54.9, GO, -10.0)],
       about="the small ORATORY at the stair's head (the Romantic mirador of 1836 stands near it now)")

SILLA = [[474.8, -177.2], [506.3, -157.9], [512.0, -166.9], [515.9, -164.5], [531.7, -176.4], [516.7, -188.1], [491.1, -203.7]]
wall_loop("silla del moro", SILLA, 6.0, "the SILLA DEL MORO (the castle of Santa Elena) on the hill over the Generalife, guarding the Acequia Real")
tower("silla del moro tower", 503.0, -181.0, 8.0, 8.0, 31.0, {"tall": 11})

ALB = (517.25, -10.95, 20.75, 14.25, -math.radians(48.3))              # the Albercon Arabe: middle, sides, turn
gs = [ground(ALB[0] + du * math.cos(ALB[4]) + dv * math.sin(ALB[4]), ALB[1] - du * math.sin(ALB[4]) + dv * math.cos(ALB[4]))
      for du in (-ALB[2] / 2, ALB[2] / 2) for dv in (-ALB[3] / 2, ALB[3] / 2)]
D.add("albercon", {"type": "box", "width": ALB[2], "length": ALB[3], "height": r4(max(gs) + .9 - (min(gs) - 1.0)), "at": [at(ALB[0], r4(min(gs) - 1.0), ALB[1], ALB[4])]},
      "the ALBERCON ARABE: the tank the Acequia Real filled, the orchards' water")
D.add("albercon water", {"type": "box", "width": ALB[2] - 1.2, "length": ALB[3] - 1.2, "height": .05, "at": [at(ALB[0], r4(max(gs) + .88), ALB[1], ALB[4])]})

HUERTAS = [[[409.3, 165.7], [417.4, 147.8], [332.8, -74.4], [319.2, -77.8], [312.4, -92.0], [287.8, -75.6], [292.9, -66.7], [277.9, -35.2], [260.7, -11.3],
            [258.5, -1.3], [293.8, 36.9], [317.1, 76.0], [339.6, 98.8], [371.3, 125.5], [396.4, 144.4], [399.9, 168.7]],
           [[399.4, -138.8], [415.8, -135.7], [426.3, -88.2], [446.5, -48.8], [483.8, -23.9], [475.4, -6.8], [420.6, -44.0], [397.5, -103.6], [394.8, -121.9]]]
trees = []
for H in HUERTAS:
    xs, zs = [p[0] for p in H], [p[1] for p in H]
    for gx in range(int(min(xs)), int(max(xs)), 9):
        for gz in range(int(min(zs)), int(max(zs)), 9):
            x, z = gx + rng.uniform(-2, 2), gz + rng.uniform(-2, 2)
            if not poly_in(H, x, z) or poly_in(RING, x, z) or poly_d(RING, x, z) < 10 or site_at(x, z, 6.0) is not None: continue
            trees.append((x, ground(x, z) - .3, z))                         # (a little sunk: the terrain's triangles dip between the posts)
plant(D, "orange", trees, name="huerta orange", about="the ORCHARDS of the Generalife (the Huerta Grande, the Merceria): fruit trees on the terraces")

# =====================================================================================================================
# 9. THE HOUSES of the medina and of the Alcazaba's soldiers' quarter: a grid of courtyard houses with lanes
# =====================================================================================================================
SIZES = [(8.0, 9.0), (9.5, 8.0), (11.0, 10.0)]
KEEP_OFF = [(-75.0, -105.0, 47.0, -15.0), (60.0, -95.0, 115.0, -40.0)]          # (the palaces' gardens and the Partal's, besides the sites)
TOWER_PTS = [(x, z, max(W, L)) for _, x, z, W, L, _, _ in TOWERS]
houses = {k: [] for k in range(len(SIZES))}


def free(x, z, w, l, inside, wall):
    if not all(poly_in(inside, x + dx, z + dz) for dx in (-w / 2 - 4, w / 2 + 4) for dz in (-l / 2 - 4, l / 2 + 4)): return False
    if poly_d(wall, x, z) < max(w, l) / 2 + 6.0: return False
    if site_at(x, z, max(w, l) / 2 + 7.0) is not None or any(in_rect(r, x, z, max(w, l) / 2 + 7.0) for r in KEEP_OFF):
        return False                                                       # (clear of the ground cut round the sites)
    if any(math.hypot(x - tx, z - tz) < tr / 2 + max(w, l) / 2 + 5 for tx, tz, tr in TOWER_PTS): return False
    return True


def place_houses(inside, wall, x0, z0, x1, z1, exclude=None, pitch=13.0):
    for gx in range(int((x1 - x0) / pitch) + 1):
        for gz in range(int((z1 - z0) / pitch) + 1):
            if gz % 4 == 3 or gx % 5 == 4: continue                       # (the lanes)
            if rng.random() < .22: continue                                # (gardens, a few empty plots)
            k = rng.randrange(len(SIZES)); w, l = SIZES[k]
            x, z = x0 + gx * pitch + rng.uniform(-1, 1), z0 + gz * pitch + rng.uniform(-1, 1)
            if exclude and poly_in(exclude, x, z): continue
            if not free(x, z, w, l, inside, wall): continue
            hs = [ground(x + dx, z + dz) for dx in (-w / 2, 0, w / 2) for dz in (-l / 2, 0, l / 2)]
            if max(hs) - min(hs) > 3.5: continue                           # (too steep for a house: a terrace garden)
            houses[k].append((x, max(hs), z))


place_houses(RING, RING, -110.0, -10.0, 400.0, 245.0, exclude=ALCAZABA)
place_houses(ALCAZABA, ALCAZABA, -245.0, -70.0, -160.0, -20.0)
for k, (w, l) in enumerate(SIZES):
    pts = houses[k]
    D.add(f"houses {k + 1}", {"type": "box", "width": w, "length": l, "height": 9.0, "at": [at(x, top - 4.5, z) for x, top, z in pts]},
          "the medina's houses: whitewashed walls round a court, blind to the lane" if k == 0 else None)
    D.add(f"house roofs {k + 1}", {"type": "roof", "form": "hip", "width": w + .4, "length": l + .4, "pitch": 24, "at": [at(x, top + 4.5, z) for x, top, z in pts]},
          "their roofs of tiles" if k == 0 else None)

# =====================================================================================================================
# 10. THE SITES' PLATFORMS; THE GROUND
# =====================================================================================================================
for nm, rects, y, F, platform in SITES:
    if not platform: continue
    low = min([ground(*F.w(u, v)) for r in rects for u in (r[0], (r[0] + r[2]) / 2, r[2]) for v in (r[1], (r[1] + r[3]) / 2, r[3])] + [y]) - .5
    D.slabs(f"{nm} floor", split(rects, 16), r4(low), h=r4(y - low), walked=True, flatRoof=True, place=F.at,
            about="the platforms the buildings stand on: walls of rubble up from the hill, filled, paved" if nm == "palaces" else None)
D.add("hill", {"type": "terrain", "origin": [GX0, GZ0], "cell": CELL, "scale": 0.1, "base": -0.3, "bottom": False, "walked": True,
               "heights": [" ".join("-2" if h <= 0.05 else str(round(h * 10)) for h in row) for row in GH],
               "_about": "the Sabika hill as the IGN's 5 m terrain model has it, 745 m at y 0: cut level under the palaces and the medina's buildings, let down to the world's ground at the frame's edge"})
D.first(["hill"] + [n for n in D.build if n.endswith(" floor") or " floor " in n])

D.write(f"assets/architecture/{NAME}.json", "Alhambra",
        "THE ALHAMBRA as Muhammad V left it (c. 1370-1391), before any Christian work: the red walls round the Sabika hill with their "
        "towers and gates (the Justicia, the Vino, the Armas, the Siete Suelos); the Alcazaba and its soldiers' quarter; the Nasrid "
        "palaces -- the Mexuar and the Cuarto Dorado, Comares with the Court of the Myrtles and the Hall of the Ambassadors in its "
        "tower, the royal baths, the Palace of the Lions with its 124 columns, its pavilions, the Two Sisters and the Abencerrajes "
        "under their muqarnas domes, the Lindaraja garden open to the valley; the Partal and its pond; the medina with its great "
        "mosque where Santa Maria stands, the baths, the palaces of the Calle Real and its houses; across the ravine the GENERALIFE "
        "-- the Court of the Water Channel between its pavilions, the west gallery, the Sala Regia and Ismail I's tower, the Sultana's "
        "garden, the water stair, the orchards -- with the Albercon and the Silla del Moro above. Built by tools/archgen/alhambra.py "
        "from the components of tools/archgen/andalusi.py (its docstring: what is sourced, what is estimated, what is left out). "
        "x east, z south.",
        railing={"type": "stone"})

# =====================================================================================================================
# THE FINISH: the red earth of the walls outside (al-qal'a al-hamra'); inside, carved plaster over tiled dadoes, marble,
# cedar ceilings; tiled roofs; whitewashed houses
# =====================================================================================================================
rules = [
    {"parts": [f"{n} water" for n in ("myrtles pool", "machuca pool", "cuarto dorado basin", "partal pond")] + [f"{p} pool water" for p, _, _ in PALACES]
     + ["fountain water", "channels", "acequia channel water", "acequia channel 2 water", "acequia basin water", "sultana pool water", "albercon water",
        "water stair channel north", "water stair channel south"], "color": "#3f8fa6", "accent": "#347c91", "_about": "the water"},
    {"parts": ["orange crowns", "mosque orange crowns", "generalife orange crowns", "huerta orange crowns"], "color": "#3e5f2a", "accent": "#2f4d20"},
    {"parts": ["cypress foliage", "cypress spires", "generalife cypress foliage", "generalife cypress spires"] + [f"{p} cypress {s}" for p, _, _ in PALACES for s in ("foliage", "spires")], "color": "#2c4425", "accent": "#22361c"},
    {"parts": ["myrtle hedges", "acequia beds"], "color": "#3d5a2a", "accent": "#2e4a20", "_about": "the myrtles"},
    {"parts": ["orange trunks", "mosque orange trunks", "generalife orange trunks", "huerta orange trunks", "cypress trunks", "generalife cypress trunks"] + [f"{p} cypress trunks" for p, _, _ in PALACES], "pattern": "timber/bark", "palette": "oak-grey"},
    {"parts": ["hill"], "pattern": "stone/sand", "palette": "earth", "_about": "the hill's red earth"},
    {"parts": ["columns shafts", "columns a shafts", "columns b shafts", "fountain stem"], "pattern": "stone/marble", "palette": "carrara",
     "_about": "the columns: white marble of Macael"},
    {"parts": ["columns capitals", "columns abaci", "columns bases", "columns a capitals", "columns b capitals", "columns a abaci", "columns b abaci",
               "columns a bases", "columns b bases", "fountain basin", "fountain bowl", "lindaraja fountain"], "color": "#ece6da", "accent": "#d2c9b8"},
    {"parts": ["plinth", "body", "haunch right", "haunch left", "foreleg right", "foreleg left", "mane", "head", "tail"], "color": "#e3ddd0", "accent": "#c9c0ae",
     "_about": "the lions: marble (couchant-lion's parts)"},
    {"parts": ["arcade"], "pattern": "ornament/arabesque", "palette": "nasrid-stucco",
     "_about": "the porticoes' walls over the arches: plaster carved in a lace of lozenges and palmettes (the sebka)"},
    {"parts": ["muqarnas", "squinches"], "color": "#efe4cf", "accent": "#b79f78", "_about": "the muqarnas: painted plaster"},
    {"parts": ["dome"], "surface": "ceiling", "pattern": "ornament/rosette 16", "palette": "nasrid-stucco", "map": "conformal",
     "_about": "the domes' soffits between the cells"},
    {"parts": ["ceiling", "eave", "comares facade eave", "mosque east ceiling"], "pattern": "ornament/star8 strap", "palette": "walnut",
     "_about": "the ceilings and eaves: carved cedar, the star patterns of the Ambassadors' dome"},
    {"parts": ["kind:enclosure"], "side": "in", "pattern": "ornament/arabesque", "palette": "nasrid-stucco",
     "_about": "the rooms inside: carved and painted plaster (the tiled dadoes below it the finish cannot yet tell apart)"},
    {"parts": ["houses 1", "houses 2", "houses 3"] + HALLS + ["walls"], "pattern": "stone/plaster", "palette": "nasrid-stucco",
     "_about": "the houses, the palaces' rooms and halls (qubbas' `walls`): lime plaster, whitewashed -- the red is the walls' and towers' alone"},
    {"parts": ["kind:roof"], "pattern": "roofs/coppi", "palette": "terracotta"},
    {"parts": ["kind:dome"], "surface": "roof", "pattern": "stone/plaster", "palette": "nasrid-stucco", "_about": "the baths' vaults: lime"},
    {"surface": "floor", "within": [7.0, -49.3, 35.5, -33.6], "pattern": "stone/marble", "palette": "carrara", "_about": "the courts: white marble"},
    {"surface": "floor", "within": [-27.1, -76.3, -5.3, -41.1], "pattern": "stone/marble", "palette": "carrara"},
    {"surface": "floor", "pattern": "floors/terracotta", "_about": "the rooms and the other courts: brick, glazed tiles in the halls"},
    {"pattern": "stone/plaster", "palette": "alhambra-earth", "_about": "the walls, the towers and the palaces outside: rammed earth and lime, red"},
]
write_json(f"assets/finishes/{NAME}.json", {"name": "Alhambra", "building": f"architecture/{NAME}",
                                            "stone": {"color": "#b9704c", "accent": "#a8603f", "pat": "ashlar"}, "rules": rules})
write_json(f"assets/doors/{NAME}.json", {
    "name": "Alhambra: doors", "building": NAME,
    "_about": "the palaces' doors: two leaves of carved cedar, star-patterned, on bronze pins",
    "doors": [{"_about": "the halls' doors", "part": ["sala regia", "mexuar", "cuarto dorado", "sala de la barca", "lions north range", "lions south range", "mocarabes",
                                                      "sala de los reyes", "partal oratory", "mosque"], "style": "andalusi"}]})
print("finish and doors written;", sum(len(v) for v in houses.values()), "houses")
