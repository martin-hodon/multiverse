# TOPKAPI PALACE, Istanbul (from 1459; the Second Court mostly Süleyman's, 1520s, the kitchens Sinan's after the fire of
# 1574, the Fourth Court's kiosks 17th-19th c.): the whole palace along its promontory, from the Imperial Gate to the
# Fourth Court, from the Ottoman palace components (tools/archgen/ottoman.py) and blue_mosque.py's `domed-arcade`.
#
# THE FRAME (2026-11-04 rework): +x runs along the palace's axis, azimuth 27.3 degrees (NNE: from the Imperial Gate toward
# Sarayburnu, the Second Court's long walls, the kitchens' street); +z is azimuth 117.3 (ESE: the Sea of Marmara side,
# the kitchens); -z the Golden Horn side (the Harem). The origin is the Gate of Salutation's outer face on its passage
# (41.011320 N, 28.983128 E). Front +z: the kitchens' long side faces the meadow; the Imperial Gate is the -x end.
# THE PLAN IS OSM's (Overpass, 2026-11-04), every way turned into this frame (`OSM` below, metres, way ids beside them):
# the palace's own outline (way 335415778) is the plateau the Second, Third and Fourth Courts stand on; the Gate of
# Salutation (335402649), the kitchens (32396096: the court range, the kitchen street, the two rows of domed kitchens,
# the confectionery), the Divan (103907772) and its portico roof (335402671), the Tower of Justice (335402653), the
# Outer Treasury (335402652), the court's NW portico roof (1396051571), the halberdiers' dormitory (32396154), the Gate
# of Felicity's range and canopy (32396111), the Harem (relation 4743322: its outer way and three courts), the Third
# Court (the Audience Chamber 103907818, the Library of Ahmed III 32396231, the Mosque of the Agas 32396236, the
# dormitories 103907804, 103907794, 32396266, 969865285, 969865284, the Conqueror's Pavilion / Treasury 335402654, the
# Pavilion of the Holy Mantle 32396205), the Fourth Court (the Baghdad Kiosk 32396296, the Revan Kiosk 969327995, the
# Circumcision Room 335415776, the Iftariye canopy 1272157518, the pool 335415775 and the smaller ones, the Sofa Kiosk
# 194486642, the Mecidiye Kiosk 32396254, the Sofa Mosque 261824325, the wardrobe 261824324), the First Court (the
# Imperial Gate 335364925, Hagia Irene relation 4742554, the Kimyahane 103907803 and Firincilar mescidi 1456476427, the
# mint precinct's wall 335364924, the Sur-i Sultani 103339336).
# THE GROUND (SRTM 30 m via opentopodata: the Imperial Gate 44 m, the Gate of Salutation 52, the courts 53-55, the
# Fourth Court's lower garden and the Mecidiye 40-44, Gülhane below 27, the shore 8-14): y 0 is the Imperial Gate's
# ground, the game's; the First Court rises along x to the plateau at PT 8 m (the courts' level) at the Gate of
# Salutation; the palace's outline stands PT above the ground round it (its faces the terrace walls over the slopes to
# the Golden Horn and the Marmara); the Fourth Court's lower garden (the tulip garden, the Sofa Kiosk, the Mecidiye) is a
# terrace PL 3 m, under the marble terrace of the Baghdad and Revan kiosks (PT), stairs between them.
# Sourced (Wikipedia en/tr "Topkapı Sarayı", "Adalet Kulesi", "Bağdat Köşkü"): the Gate of Salutation's two octagonal
# towers with pointed caps and crenellations; the Divan's three domed rooms; the Tower of Justice square, the palace's
# tallest, its upper stage (1825) with tall round-arched windows, engaged columns and pediments, a lead cone; the Outer
# Treasury's eight domes; the kitchens' ten domed halls with twenty chimneys; the Audience Chamber's 22 columns under
# one deep-eaved roof; the Library of Ahmed III a Greek cross with a dome, on a basement, its porch reached by stairs
# both sides; the Conqueror's Pavilion two floors on a terrace with a loggia of double arches; the Baghdad Kiosk an
# octagon widened by four iwans under a dome in a colonnade; the Iftariye a gilt bronze canopy; Hagia Irene's two domes.
# ESTIMATED (from Commons photographs against OSM's widths; no source gives them): the Tower of Justice 44 m to its tip
# (shaft 25, stage 7.5, cap 10), the Gate of Salutation's towers 25.5 (shaft 14.5, cap 10.5) and its wall 10.5, the
# Imperial Gate 16.5, the porticoes' columns 4.6, the kitchens' springing 6, the ranges 8-11, the Harem 12, the
# Mecidiye 11, Hagia Irene's main dome 15 m across and 35 m up; every kiosk's room inside its OSM outline (the outline
# taken as the eaves).
#   Everything is metres. Run: python3 tools/archgen/topkapi.py
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ottoman import write_components, comp, POINTED, ROOT

Q, PI = math.pi / 2, math.pi
r3 = lambda v: round(v, 3)
parts, build = {}, []
def add(n, d):
    assert n not in parts, n
    parts[n] = d; build.append(n); return n

# ---- THE OSM PLAN in the frame (metres; collinear points dropped) ---------------------------------------------------
OSM = {
    'palace': [[6.5, -111.2], [4.9, -97.9], [4.0, -93.6], [6.1, -86.0], [5.7, -75.2], [3.3, -73.3], [2.9, -62.8], [2.9, -17.0], [0.0, -17.0], [0.0, 25.0], [-8.1, 25.1], [-7.6, 58.0], [1.6, 57.9], [1.8, 70.2], [1.0, 100.5], [196.6, 100.2], [307.5, 100.2], [321.9, 107.2], [346.2, 89.9], [363.9, 87.9], [367.3, 32.6], [371.4, -32.1], [372.0, -56.7], [374.8, -91.0], [270.5, -107.9], [230.2, -116.7], [219.7, -117.9], [220.3, -123.3], [209.8, -124.5], [209.2, -119.5], [166.8, -124.4], [113.2, -133.5], [110.6, -106.2], [110.8, -98.2], [60.2, -104.3]],   # way 335415778 (the Gate of Salutation's tower bumps left out)
    'kitchens': [[8.9, 63.1], [169.4, 62.8], [169.3, 69.5], [173.1, 69.6], [173.3, 100.2], [1.0, 100.5], [0.9, 87.2], [59.4, 87.1], [59.4, 79.3], [165.0, 79.1], [164.9, 75.4], [74.6, 75.5], [74.6, 74.1], [9.0, 74.2]],   # way 32396096
    'nw portico': [[106.9, -47.8], [107.5, -53.8], [36.6, -60.8], [36.1, -54.7]],   # way 1396051571 (a roof)
    'halberdiers': [[106.9, -47.8], [106.9, -44.2], [115.7, -44.1], [116.8, -68.5], [108.8, -69.4], [110.8, -98.2], [6.5, -111.2], [4.9, -97.9], [93.3, -87.1], [92.9, -79.4], [86.4, -80.0], [85.3, -56.0], [107.5, -53.8]],   # way 32396154
    'harem': [[226.9, -85.0], [232.6, -84.1], [231.0, -73.7], [236.8, -71.6], [234.6, -47.1], [254.6, -46.0], [255.2, -58.0], [267.2, -57.2], [266.9, -52.2], [264.7, -42.9], [262.6, -43.0], [262.3, -34.4], [174.8, -33.9], [158.4, -33.5], [157.0, -47.0], [138.0, -47.7], [137.9, -37.8], [124.5, -37.7], [124.4, -46.0], [115.7, -45.9], [116.8, -68.5], [108.8, -69.4], [110.6, -106.2], [113.2, -133.5], [166.8, -124.4], [162.7, -94.6], [171.3, -93.7], [172.2, -99.8], [188.3, -98.3], [189.7, -108.8], [198.1, -108.0], [199.5, -120.6], [209.2, -119.5], [209.8, -124.5], [220.3, -123.3], [219.7, -117.9], [230.2, -116.7]],   # relation 4743322, outer way 32396162
    'harem court a': [[196.7, -47.5], [180.9, -48.2], [181.4, -62.3], [197.2, -61.6]],   # way 335402648
    'harem court b': [[150.4, -88.7], [117.5, -94.0], [118.0, -101.4], [151.5, -96.1]],   # way 335402645
    'harem court c': [[153.0, -108.9], [128.3, -112.0], [129.3, -119.8], [153.9, -116.6]],   # way 335402686
    'agas mosque': [[202.0, -28.5], [196.7, -16.1], [221.6, -5.2], [227.0, -17.7]],   # way 32396236
    'library': [[218.0, 15.5], [215.0, 15.4], [214.8, 24.4], [217.8, 24.5], [217.6, 29.1], [227.8, 29.5], [227.9, 24.8], [230.9, 24.9], [231.1, 15.9], [228.1, 15.8], [228.3, 10.4], [218.1, 10.1]],   # way 32396231
    'baghdad': [[322.2, -49.5], [318.8, -29.8], [344.7, -25.1], [348.1, -44.8], [343.6, -45.6], [344.5, -50.7], [327.4, -53.8], [326.6, -48.7]],   # way 32396296
    'iftariye': [[314.1, -50.7], [314.4, -52.3], [310.5, -53.0], [310.2, -51.4]],   # way 1272157518
    'imperial gate': [[-332.2, -6.0], [-318.1, -2.0], [-329.4, 37.3], [-343.5, 33.3]],   # way 335364925
    'irene': [[-212.6, -92.2], [-202.4, -90.1], [-204.5, -80.8], [-200.4, -79.9], [-202.8, -71.1], [-206.4, -72.0], [-208.6, -64.8], [-218.7, -67.3], [-226.5, -35.9], [-236.8, -38.4], [-240.2, -36.5], [-248.9, -41.4], [-258.8, -44.0], [-236.2, -137.4], [-203.7, -133.4]],   # relation 4742554
    'kimyahane': [[-167.0, 32.5], [-166.8, 45.8], [-125.7, 45.5], [-126.0, 17.1], [-139.9, 17.2], [-139.8, 27.3], [-143.7, 32.3]],   # way 103907803
    'firincilar': [[-167.0, 32.5], [-187.1, 33.1], [-187.1, 45.1], [-166.8, 45.8]],   # way 1456476427
    'mint wall': [[-8.1, 25.1], [-30.2, 19.4], [-52.2, 14.3], [-66.1, 11.5], [-95.0, 5.3], [-121.2, -1.4], [-182.5, 4.0], [-193.7, 3.9], [-250.7, 8.0], [-258.1, 44.5]],   # way 335364924 (a line)
    'sur nw': [[-332.2, -6.0], [-326.6, -30.7], [-324.6, -38.4], [-308.3, -105.3], [-305.0, -122.7]],   # way 103339336 (its outer line)
    'fourth wall': [[267.2, -57.2], [268.7, -80.3], [270.5, -107.9]],   # way 335415774
}
# the rectangles in OSM's outlines (x0, x1, z0, z1), read off the same ways
R_ = {
    'gate block': (3.0, 23.6, -19.2, 25.2),          # 335402649 behind the gate wall
    'gate wall north': (2.9, 8.9, -62.8, -17.0),     # 103907788, the rooms along the wall north of the gate
    'gate wall south': (-8.1, 9.0, 25.1, 70.0),      # 335402670, the building south of it
    'divan': (115.9, 142.5, -37.8, -26.0),           # 103907772
    'divan portico': (103.7, 142.6, -44.2, -21.1),   # 335402671
    'tower': (115.7, 124.5, -46.0, -37.6),           # 335402653
    'treasury': (142.5, 174.8, -38.7, -21.0),        # 335402652
    'felicity canopy': (161.0, 167.7, 22.3, 38.7),   # 32396111
    'felicity range': (167.7, 182.4, 3.2, 62.8), 'felicity north': (170.0, 182.4, -21.0, 3.2), 'felicity south': (169.4, 182.4, 62.8, 75.6),
    'arz': (182.3, 211.3, 15.4, 46.8),               # 103907818
    'has oda dorm': (227.0, 262.3, -34.6, -8.0),     # 103907804 (its part along the court; the rest under the mosque's corner)
    'holy mantle': (262.3, 298.0, -42.6, -7.0), 'holy mantle porch': (268.7, 288.5, -7.0, 6.7),   # 32396205
    'dorm ne1': (268.5, 291.8, 9.1, 42.7),           # 103907794
    'dorm ne2': (268.3, 291.3, 45.7, 71.4),          # 32396266
    'treasury pavilion': (229.7, 284.6, 71.3, 100.7),  # 335402654 the Conqueror's Pavilion
    'seferli': (195.7, 229.7, 74.1, 100.5),          # 969865285
    'dorm se': (173.2, 196.5, 75.6, 100.2),          # 969865284
    'revan': (297.3, 309.6, -26.7, -6.5),            # 969327995
    'circumcision': (283.2, 299.2, -54.3, -41.0),    # 335415776
    'pool': (300.5, 309.9, -40.3, -28.1),            # 335415775
    'sofa kiosk': (318.6, 337.0, -13.7, 7.6),        # 194486642
    'mecidiye': (318.5, 358.2, 62.7, 77.6),          # 32396254
    'sofa mosque': (294.2, 302.2, 74.0, 85.9),       # 261824325
    'wardrobe': (306.0, 312.5, 54.5, 61.5),          # 261824324
}
POOLS = [(320.0, -20.0, 6.0, 5.0), (358.5, -35.5, 18.0, 6.0), (329.0, 15.5, 5.5, 12.5), (253.5, 25.0, 4.5, 5.0), (311.5, -62.0, 8.5, 3.6)]   # 1272157517, 1272160891, 1272160895, 1396250561, 1272157519: (x, z, w, l)

# ---- THE LEVELS ---------------------------------------------------------------------------------------------------
PT, PL = 8.0, 3.0                 # the courts' plateau; the Fourth Court's lower garden
X_IG = -330.0                     # where the First Court's slope meets the ground (the Imperial Gate)
SLOPE = PT / -X_IG
yR = lambda x: max(0.0, PT + SLOPE * x)   # the First Court's ground at x

# ---- GEOMETRY HELPERS ----------------------------------------------------------------------------------------------
def clip(poly, a, b, c):
    """the polygon's part where a x + b z <= c (Sutherland-Hodgman against one half-plane)"""
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if fp <= 0: out.append(p)
        if (fp < 0 < fq) or (fq < 0 < fp):
            t = fp / (fp - fq); out.append([p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t])
    res = []
    for p in out:
        p = [r3(p[0]), r3(p[1])]
        if not res or math.dist(res[-1], p) > 0.05: res.append(p)
    if len(res) > 2 and math.dist(res[0], res[-1]) < 0.05: res.pop()
    return res
def clips(poly, *planes):
    for pl in planes: poly = clip(poly, *pl)
    return poly
def area(p): return sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p))) / 2
def edges(pts):
    """each edge of the outline: (p, q, L, ex, ez, nx, nz), n outward"""
    A, out = area(pts), []
    for i in range(len(pts)):
        p, q = pts[i], pts[(i + 1) % len(pts)]; L = math.dist(p, q)
        ex, ez = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        nx, nz = (ez, -ex) if A > 0 else (-ez, ex)
        out.append((p, q, L, ex, ez, nx, nz))
    return out
def outset(pts, d):
    """the outline moved OUT by d, its corners mitred"""
    E = edges(pts); n = len(E); lines = [(p[0] + nx * d, p[1] + nz * d, ex, ez) for (p, q, L, ex, ez, nx, nz) in E]; out = []
    for i in range(n):
        xa, za, ea, fa = lines[i - 1]; xb, zb, eb, fb = lines[i]
        den = ea * fb - fa * eb
        if abs(den) < 1e-6: out.append([r3(xb), r3(zb)]); continue
        u = ((xb - xa) * fb - (zb - za) * eb) / den
        out.append([r3(xa + ea * u), r3(za + fa * u)])
    return out
def marks(pts, every, y, w, h, out=0.05, end=2.0, skip=()):
    """window (or door) panes along every face of the outline: [x, y, z, yaw] for a box w wide facing out"""
    res = []
    for k, (p, q, L, ex, ez, nx, nz) in enumerate(edges(pts)):
        if L < w + 2 * end or k in skip: continue
        n = max(1, int((L - 2 * end) // every) + 1); step = (L - 2 * end) / max(1, n - 1) if n > 1 else 0
        for i in range(n):
            u = end + i * step if n > 1 else L / 2
            res.append([r3(p[0] + ex * u + nx * out), r3(y), r3(p[1] + ez * u + nz * out), r3(math.atan2(nx, nz))])
    return res
def rect_pts(x0, x1, z0, z1): return [[x0, z0], [x1, z0], [x1, z1], [x0, z1]]
def ctr(r): return ((r[0] + r[1]) / 2, (r[2] + r[3]) / 2)

WIN = lambda e, sill=1.6, spr=3.0, w=1.1, end=1.8: {"every": e, "width": w, "end": end, "sill": sill, "springing": spr, "head": POINTED}
DOOR = lambda a, w=2.2, h=3.0: {"at": r3(a), "width": w, "sill": 0, "springing": h, "head": POINTED, "glass": False}

def at_on(face, r, w):
    """a world coordinate along a rect's face -> that face's `at` (from its middle: face 0 (+z) runs +x, 1 (+x) -z, 2 (-z) -x, 3 (-x) +z)"""
    xm, zm = ctr(r)
    return r3([w - xm, zm - w, xm - w, w - zm][face])

def block(name, r, y0, H, faces=None, every=4.0, roof="hip", pitch=17, eave=0.9, t=1.0, interior=False, about="", tiers=None, sill=1.6, spr=3.0, **kw):
    """a range on the rect r (x0, x1, z0, z1): walls with pointed windows, `faces` {k: [openings] or a face dict} over them,
    under a low hipped lead roof with its eave (roof None: a flat lead top behind a parapet's coping)"""
    x0, x1, z0, z1 = r; W, L = x1 - x0, z1 - z0
    win = WIN(every, sill, spr)
    F = {}
    for k in range(4):
        f = (faces or {}).get(k)
        if isinstance(f, list): F[str(k)] = [{**tiers[0], "openings": {**tiers[0]["openings"], "with": f}}] + tiers[1:] if tiers else {**win, "with": f}
        elif isinstance(f, dict) or f == []: F[str(k)] = f
    d = {"type": "enclosure", "plan": {"rect": [r3(W), r3(L)]}, "thickness": t, "height": H, "glass": True, "interior": interior,
         "openings": tiers if tiers else win, "faces": F, "at": [[r3((x0 + x1) / 2), r3(y0), r3((z0 + z1) / 2), 0]], "_about": about, **kw}
    if tiers: d.pop("openings"); d["tiers"] = tiers
    add(name, d)
    if roof == "hip":
        add(name + " roof", {"type": "roof", "form": "hip", "width": r3(W + 2 * eave), "length": r3(L + 2 * eave), "pitch": pitch, "overhang": 0.3,
                             "at": [[r3((x0 + x1) / 2), r3(y0 + H), r3((z0 + z1) / 2), 0]], "standsOn": [name]})
    elif roof == "flat":
        add(name + " roof", {"type": "prism", "plan": {"rect": [r3(W + 2 * eave), r3(L + 2 * eave)]}, "height": 0.45, "flatRoof": True,
                             "at": [[r3((x0 + x1) / 2), r3(y0 + H), r3((z0 + z1) / 2), 0]], "standsOn": [name]})
    return name

def solid(name, pts, y0, H, every=4.2, about="", eave=0.7, roof=True, sill=1.6, wh=1.6, storeys=1):
    """a mass on an OSM outline that is not walked into: the walls a prism, windows as panes on its faces, a flat lead roof
    with its eave (the Harem's ranges, the halberdiers', the First Court's)"""
    add(name, {"type": "prism", "plan": {"points": pts}, "height": r3(H), "at": [[0, r3(y0), 0, 0]], "flatRoof": True,
               "courses": [{"y": 0, "h": 0.5, "out": 0.1, "profile": "plinth"}], "_about": about})
    sto = H / storeys
    add(name + " windows", {"type": "box", "width": 1.1, "length": 0.08, "height": wh,
                            "at": [m for s in range(storeys) for m in marks(pts, every, y0 + s * sto + sill, 1.1, wh)], "_about": "its windows"})
    if roof:
        add(name + " roof", {"type": "prism", "plan": {"points": outset(pts, eave)}, "height": 0.5, "flatRoof": True, "at": [[0, r3(y0 + H), 0, 0]],
                             "standsOn": [name], "_about": "its lead roof, the eave out past the walls"})

def domes(name, pts, y, r, drum=0.9, cn=16, about=""):
    """lead domes of radius r on low drums, their crowns' alems -- on a roof at y (or each point's own: (x, z, y))"""
    pts = [(q[0], q[1], q[2] if len(q) > 2 else y) for q in pts]; y = 0
    add(name + " drums", {"type": "ring", "count": cn, "rOuter": r3(r), "rInner": r3(r - 0.35), "height": drum, "solid": True,
                          "place": [[r3(x), r3(y + yy), r3(z), 0] for x, z, yy in pts]})
    add(name, {"type": "dome", "radius": r3(r), "thickness": 0.3, "sides": cn, "head": {"profile": "semicircular"},
               "at": [[r3(x), r3(yy + drum), r3(z), 0] for x, z, yy in pts], "standsOn": [name + " drums"], "_about": about})
    add(name + " alems", {"type": "column", "radius": 0.07, "height": r3(max(0.8, r * 0.3)), "sides": 6, "taper": 0.3,
                          "at": [[r3(x), r3(yy + drum + r), r3(z), 0] for x, z, yy in pts], "standsOn": [name]})

def chimneys(name, pts, y, h, r=0.55):
    pts = [(q[0], q[1], q[2] if len(q) > 2 else y) for q in pts]
    add(name, {"type": "prism", "plan": {"sides": 8, "radius": r}, "height": h, "at": [[r3(x), r3(yy), r3(z), 0] for x, z, yy in pts],
               "courses": [{"y": r3(h - 0.5), "h": 0.3, "out": 0.15, "profile": "band"}]})
    add(name + " caps", {"type": "dome", "radius": r + 0.15, "thickness": 0, "sides": 8, "head": {"profile": "trigonal", "rise": r * 0.9},
                         "at": [[r3(x), r3(yy + h), r3(z), 0] for x, z, yy in pts], "standsOn": [name]})

# =====================================================================================================================
# THE GROUND: the First Court's slope, the plateau, the marble terrace and the lower garden
# =====================================================================================================================
PAL = OSM['palace']
# HAGIA IRENE's frame (OSM relation 4742554): the First Court's ground stops at a retaining wall round it -- the church
# stands in its own yard at the old ground, below the court (y 0)
IRW, IRE = ((-236.2 + -203.7) / 2, (-137.4 + -133.4) / 2), ((-258.8 + -226.5) / 2, (-44.0 + -35.9) / 2)
ir_len = math.dist(IRW, IRE); ird = ((IRE[0] - IRW[0]) / ir_len, (IRE[1] - IRW[1]) / ir_len)
IRY = math.atan2(ird[0], ird[1]); irc = ((IRW[0] + IRE[0]) / 2, (IRW[1] + IRE[1]) / 2)
def ir_at(u, s, y=0.0):
    """Hagia Irene's local frame: s along the church from its middle (east +), u across (right of east)"""
    return [r3(irc[0] + ird[0] * s + ird[1] * u), r3(y), r3(irc[1] + ird[1] * s - ird[0] * u), r3(IRY)]
IRW_ = 32.0
IRC = [ir_at(u, s_)[0:3:2] for u, s_ in ((-20.0, ir_len / 2 + 4.0), (20.0, ir_len / 2 + 4.0), (20.0, -ir_len / 2 - 4.0), (-20.0, -ir_len / 2 - 4.0))]
def on_line(p, q, z):
    t = (z - p[1]) / (q[1] - p[1]); return [r3(p[0] + (q[0] - p[0]) * t), r3(z)]
# THE FIRST COURT's outline from OSM's lines round it (no way draws the court itself): the Imperial Gate's inner face, the
# Sur-i Sultani's inner face (way 103339336, 1.5 m in) to its corner tower, Hagia Irene's yard (notched round the church),
# the precinct wall north of the court (335402638), the Archaeology Museum's south front (319020883), the palace's own
# west wall (335415778) to the Gate of Salutation, the mint's wall (335364924) back to the gate
RAMP = ([[-318.1, -2.0], [-324.9, -30.5], [-323.0, -38.4], [-306.8, -105.3], [-303.6, -121.4], on_line(IRC[0], IRC[3], -125.0)] + IRC[0:2] + [on_line(IRC[1], IRC[2], -74.0)]
        + [[-183.3, -73.9], [-134.2, -71.5], [-131.5, -106.8], [-125.7, -108.3], [-122.5, -107.9], [-115.2, -107.4], [-54.6, -99.8], [-53.9, -105.9], [-13.9, -100.9]]
        + [[4.9, -97.9], [4.0, -93.6], [6.1, -86.0], [5.7, -75.2], [3.3, -73.3], [2.9, -62.8], [2.9, -17.0], [0.0, -17.0], [0.0, 25.0], [-8.1, 25.1]]
        + OSM['mint wall'][1:] + [[-329.4, 37.3]])
# the Imperial Mint's precinct south of its wall (the Darphane: OSM's wall, then its outermost buildings, 103907779 and
# 103907800, to the palace's wall at the Gate of Salutation -- OSM draws no line there)
MINT = list(reversed(OSM['mint wall'])) + [[-193.5, 45.0], [-125.7, 45.8], [-60.5, 62.3], [-33.1, 69.6], [-8.0, 70.4], [1.8, 70.2], [1.6, 57.9], [-7.6, 58.0]]
add("first court", {"type": "prism", "plan": {"points": RAMP}, "height": PT, "slope": [r3(SLOPE), 0], "walked": True, "at": [[0, 0, 0, 0]],
                    "_about": "THE FIRST COURT (Alay Meydanı): the ground rising 8 m along the 330 m from the Imperial Gate to the Gate of Salutation, inside OSM's walls and fronts"})
add("mint yard", {"type": "prism", "plan": {"points": MINT}, "height": PT, "slope": [r3(SLOPE), 0], "walked": True, "at": [[0, 0, 0, 0]],
                  "_about": "the Imperial Mint's precinct (the Darphane) behind its wall, on the same slope"})
add("irene yard", {"type": "prism", "plan": {"points": IRC}, "height": 0.05, "walked": True, "at": [[0, 0, 0, 0]],
                   "_about": "Hagia Irene's sunken yard at the old ground, the court's retaining wall round it"})
WK = (1, r3(3.3 / 50.7), r3(267.2 - 57.2 * 3.3 / 50.7))              # the Fourth Court's wall's line (OSM way 335415774): x + k z <= c west of it
WKo = tuple(-v for v in WK)
ZT = -54.6                                                          # the marble terrace's edge over the Golden Horn garden
UP = clips(PAL, WK, (0, 1, 72.0))            # the courts' plateau; north of z 72 its edge steps back to x 293 (the Sofa Mosque below it)
UPE = clips(PAL, WKo, (1, 0, 298.0), (0, 1, 72.0), (0, -1, -ZT))   # past the Fourth Court's wall, the strip to the terrace (the Circumcision Room)
UPN = clips(PAL, (1, 0, 293.0), (0, -1, -72.0))
# THE MARBLE TERRACE: OSM draws no outline, so it is the line its buildings stand on -- the Golden Horn edge just behind
# the Circumcision Room (335415776) and the Iftariye (1272157518), round the Baghdad Kiosk's iwans and colonnade on its
# corner (32396296, its 10 deg turn), down to the Sofa Kiosk's front (194486642), round the Revan Kiosk's platform
# (969327995) to the Holy Mantle's east wall -- an L about the pool
TER = [[298.0, ZT], [327.4, -53.8], [344.5, -50.7], [343.6, -45.6], [348.1, -44.8], [344.7, -25.1], [337.0, -14.0], [318.0, -14.0], [318.0, -3.0], [298.0, -3.0]]
add("plateau", {"type": "prism", "plan": {"points": UP}, "height": PT, "walked": True, "at": [[0, 0, 0, 0]],
                "courses": [{"y": r3(PT - 0.6), "h": 0.6, "out": 0.15, "profile": "band"}],
                "_about": "the palace's plateau (OSM's outline of the palace, way 335415778): the Second and Third Courts and the Harem, its faces the terrace walls over the slopes"})
add("plateau east", {"type": "prism", "plan": {"points": UPE}, "height": PT, "walked": True, "at": [[0, 0, 0, 0]],
                     "courses": [{"y": r3(PT - 0.6), "h": 0.6, "out": 0.15, "profile": "band"}], "_about": "the plateau's stretch from the Fourth Court's wall to the marble terrace"})
add("plateau north", {"type": "prism", "plan": {"points": UPN}, "height": PT, "walked": True, "at": [[0, 0, 0, 0]],
                      "courses": [{"y": r3(PT - 0.6), "h": 0.6, "out": 0.15, "profile": "band"}], "_about": "the plateau's stretch along the Conqueror's Pavilion"})
LOW = [clip(PAL, -1, 0, -298.0), clips(PAL, WKo, (1, 0, 298.0), (0, 1, ZT)), clips(PAL, (-1, 0, -293.0), (1, 0, 298.0), (0, -1, -72.0))]
for i, p in enumerate(LOW):
    add(f"lower garden {i + 1}", {"type": "prism", "plan": {"points": p}, "height": PL, "walked": True, "at": [[0, 0, 0, 0]],
                                  "_about": "the Fourth Court's lower garden (the tulip garden, the Sofa Kiosk, the Mecidiye), 5 m under the marble terrace" if i == 0 else "its next stretch"})
add("marble terrace", {"type": "prism", "plan": {"points": TER}, "height": PT, "walked": True, "at": [[0, 0, 0, 0]],
                       "courses": [{"y": r3(PT - 0.6), "h": 0.6, "out": 0.15, "profile": "band"}],
                       "_about": "the Fourth Court's marble terrace: the Baghdad Kiosk on its corner, the Revan Kiosk, the Circumcision Room, the Iftariye on its edge and the pool, over the gardens"})
def pip(p, poly):
    x, z = p; inside = False
    for i in range(len(poly)):
        (xa, za), (xb, zb) = poly[i], poly[(i + 1) % len(poly)]
        if (za > z) != (zb > z) and x < xa + (xb - xa) * (z - za) / (zb - za): inside = not inside
    return inside
def level(x, z):
    """the ground's height at (x, z) inside the palace's outline"""
    if pip((x, z), TER): return PT
    if x >= 298 or (WK[0] * x + WK[1] * z > WK[2] and z < ZT) or (x >= 293 and z >= 72): return PL
    return PT
# THE HILLSIDE (a `terrain` height map, 5 m cells): the promontory's fall round the walls -- from 1.6 m under the plateau's
# edge (its terrace walls stand that high over the slope) and 0.8 m under the First Court's, down to the game's ground
# over HD metres: toward the Golden Horn and Gülhane, toward the Marmara, round Sarayburnu. (The real fall is 40 m to
# the shore; the game's ground is one level, so the slope ends there.) Hagia Irene's yard stays at the old ground.
HD, HC = 20.0, 5.0
def poly_near(p, poly):
    best = (1e9, None)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]; dx, dz = b[0] - a[0], b[1] - a[1]
        t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dz) / (dx * dx + dz * dz or 1)))
        q = (a[0] + dx * t, a[1] + dz * t); d = math.hypot(p[0] - q[0], p[1] - q[1])
        if d < best[0]: best = (d, q)
    return best
HILL_R = [(PAL, lambda q: level(*q) - 1.6), (RAMP, lambda q: yR(q[0]) - 0.8), (MINT, lambda q: yR(q[0]) - 0.8)]
def hill_h(x, z):
    if pip((x, z), IRC): return 0.0
    h = 0.0
    for poly, top in HILL_R:
        d, q = poly_near((x, z), poly)
        if pip((x, z), poly):
            if d > 1.6 * HC: return None
            return max(0.0, top((x, z)))
        u = (q[0] - x, q[1] - z); n = math.hypot(*u) or 1
        e = top((q[0] + u[0] / n * 0.6, q[1] + u[1] / n * 0.6))
        h = max(h, e * max(0.0, 1 - d / HD))
    return h
HX0, HZ0 = -340.0, -160.0
HG = [[hill_h(HX0 + i * HC, HZ0 + j * HC) for i in range(int((395 - HX0) / HC) + 1)] for j in range(int((130 - HZ0) / HC) + 1)]
for j, row in enumerate(HG):   # (ground only where the slope is, or next to it: the rest is the game's own)
    HG[j] = [v if v is None or v > 0.02 or any((HG[j + dj][i + di] or 0) > 0.02 for dj in (-1, 0, 1) for di in (-1, 0, 1)
                                              if 0 <= j + dj < len(HG) and 0 <= i + di < len(row)) else None for i, v in enumerate(row)]
add("hillside", {"type": "terrain", "cell": HC, "origin": [HX0, HZ0], "scale": 0.1, "walked": True, "bottom": False,
                 "heights": [" ".join("-" if v is None else str(round(v * 10)) for v in row) for row in HG],
                 "_about": "THE HILLSIDE round the palace's walls, falling to the shore and to Gülhane (a height map from the walls' lines)"})
HILL_TREES = []
for j in range(2, len(HG) - 2, 3):
    for i in range(1, len(HG[0]) - 1, 4):
        v = HG[j][i]; x, z = HX0 + i * HC + 1.2, HZ0 + j * HC - 0.8
        if v is not None and 0.8 < v < 4.5 and all(not pip((x, z), P_) for P_ in (PAL, RAMP, MINT)) and (z < -100 or z > 104 or x > 360):
            HILL_TREES.append((x, z, round(v - 0.3, 2)))
# the stairs down from the marble terrace and from the Third Court into the lower garden
def flight(name, foot, d, w, base, top, about=""):
    n = max(1, round((top - base) / 0.17)); yaw = math.atan2(-d[1], d[0]); s, c = math.sin(yaw), math.cos(yaw)
    px, pz = foot[0] + w / 2 * s, foot[1] + w / 2 * c
    add(name, {"type": "flight", "width": w, "run": 0.32, "rise": r3((top - base) / n), "base": base, "top": top, "landing": 0,
               "at": [[r3(px), 0, r3(pz), r3(yaw)]], "_about": about})
    return n * 0.32
RUN = round((PT - PL) / 0.17) * 0.32
flight("terrace stair", (312.6, -3.0 + RUN), (0, -1), 3.0, PL, PT, "the stair from the marble terrace down into the tulip garden, beside the Sofa Kiosk")
flight("garden stair", (298.0 + RUN, 44.2), (-1, 0), 2.6, PL, PT, "the stair from the Third Court's north-east corner down into the lower garden")
# the marble terrace's parapets along its edges (not toward the Holy Mantle's level ground; a gap at the stair)
for k in range(len(TER) - 1):
    a, b = TER[k], TER[k + 1]
    segs = [(a, b)] if k != 8 else [((318.0, -3.0), (314.3, -3.0)), ((310.9, -3.0), (298.0, -3.0))]
    for j, (a, b) in enumerate(segs):
        L = math.dist(a, b); yaw = math.atan2(b[1] - a[1], b[0] - a[0])
        add(f"terrace parapet {k + 1}" + ("b" if j else ""), {"type": "wall", "width": r3(L), "height": 1.0, "thickness": 0.35, "glass": False, "openings": [],
                                                          "at": [[r3((a[0] + b[0]) / 2), PT, r3((a[1] + b[1]) / 2), r3(-yaw)]], "_about": "the marble terrace's parapet" if k == 0 else "its next stretch"})

# =====================================================================================================================
# THE FIRST COURT: the Imperial Gate in the Sur-ı Sultani, the road, the mint's wall, Hagia Irene, the plane trees
# =====================================================================================================================
IG = OSM['imperial gate']
igx, igz = sum(p[0] for p in IG) / 4, sum(p[1] for p in IG) / 4
ig_long = math.dist(IG[0], IG[3]); ig_deep = math.dist(IG[0], IG[1])
ig_out = ((IG[0][0] - IG[1][0]) / ig_deep, (IG[0][1] - IG[1][1]) / ig_deep)        # out of the palace (toward -x)
IGY = math.atan2(ig_out[0], ig_out[1])
pas = lambda: [{"at": 0, "width": 5.2, "sill": 0, "springing": 7.6, "head": POINTED, "glass": False}]
add("imperial gate", {"type": "enclosure", "plan": {"rect": [r3(ig_long), r3(ig_deep)]}, "thickness": 2.6, "height": 16.5, "glass": True, "interior": True,
                      "openings": [], "faces": {"0": pas(), "2": pas(),
                                               "1": {"every": 3.4, "width": 1.0, "end": 2.6, "sill": 4.0, "springing": 5.6, "head": POINTED},
                                               "3": {"every": 3.4, "width": 1.0, "end": 2.6, "sill": 4.0, "springing": 5.6, "head": POINTED}},
                      "courses": [{"y": 15.4, "h": 1.1, "out": 0.35, "profile": "cornice"}],
                      "at": [[r3(igx), 0, r3(igz), r3(IGY)]],
                      "_about": "the IMPERIAL GATE (Bâb-ı Hümâyûn, 1478): the marble block in the Sur-ı Sultani, OSM's 41 x 15 m, the passage through its middle (its upper storey of timber, gone since 1866, not built)"})
add("imperial gate niche", {"type": "wall", "width": 12.0, "height": 15.2, "thickness": 0.9, "glass": False,
                            "openings": [{"at": 6.0, "width": 8.6, "sill": 0, "springing": 8.8, "head": POINTED, "glass": False}],
                            "at": [[r3(igx + ig_out[0] * (ig_deep / 2 + 0.45)), 0, r3(igz + ig_out[1] * (ig_deep / 2 + 0.45)), r3(IGY)]],
                            "_about": "the deep pointed arch framing the passage on the outer face, its marble frame standing proud"})
for nm, side in (("imperial gate passage walls", 0),):
    add(nm, {"type": "wall", "width": r3(ig_deep - 5.2), "height": 9.4, "thickness": 0.8, "glass": False, "openings": [],
             "at": [[r3(igx + e * 3.0 * math.cos(IGY)), 0, r3(igz - e * 3.0 * math.sin(IGY)), r3(IGY + Q)] for e in (-1, 1)],
             "_about": "the passage's side walls, the guard rooms behind them"})
add("imperial gate roof", {"type": "prism", "plan": {"rect": [r3(ig_long - 0.4), r3(ig_deep - 0.4)]}, "height": 0.5, "flatRoof": True,
                           "at": [[r3(igx), 16.5, r3(igz), r3(IGY)]], "standsOn": ["imperial gate"]})
# the Sur-ı Sultani, Mehmed II's land wall round the palace: north from the gate down toward the Golden Horn (OSM), south
# toward the Marmara along the gate's line
def wall_line(name, pts, y_of, H, t=2.4, crenel=True, about=""):
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; L = math.dist(a, b); yaw = math.atan2(b[1] - a[1], b[0] - a[0])
        y0 = min(y_of(a[0]), y_of(b[0])); dh = abs(y_of(a[0]) - y_of(b[0]))
        add(f"{name} {i + 1}", {"type": "wall", "width": r3(L + t * 0.5), "height": r3(H + dh), "thickness": t, "glass": False, "openings": [],
                                "at": [[r3((a[0] + b[0]) / 2), r3(y0 - 0.05), r3((a[1] + b[1]) / 2), r3(-yaw)]], "_about": about if i == 0 else "its next stretch"})
        if crenel:
            n = max(1, int(L // 1.9))
            add(f"{name} {i + 1} merlons", {"type": "box", "width": 0.95, "length": r3(t * 0.6), "height": 0.9,
                                            "at": [[r3(a[0] + (b[0] - a[0]) * (k + 0.5) / n), r3(y0 - 0.05 + H + dh), r3(a[1] + (b[1] - a[1]) * (k + 0.5) / n), r3(-yaw)] for k in range(n)],
                                            "standsOn": [f"{name} {i + 1}"]})
SUR_S = [IG[3], [r3(IG[3][0] + (IG[3][0] - IG[0][0]) * 1.0), r3(IG[3][1] + (IG[3][1] - IG[0][1]) * 1.0)]]
wall_line("sur-i sultani north", OSM['sur nw'], lambda x: 0.0, 10.0, about="the Sur-ı Sultani, the palace's land wall, north from the Imperial Gate (OSM way 103339336)")
wall_line("sur-i sultani south", SUR_S, lambda x: 0.0, 10.0, about="the Sur-ı Sultani south of the gate, toward the Marmara")
wall_line("mint wall", OSM['mint wall'], yR, 4.8, t=1.0, crenel=False, about="the wall along the road's south side, round the Imperial Mint's precinct (OSM way 335364924)")
# the road: the paved way from the Imperial Gate to the Gate of Salutation, up the slope
ROADC = [(-326.0, 15.6), (-250.0, 0.0), (-121.0, -8.0), (-3.5, 0.0)]   # its line: north of the mint's wall (which runs to -1.4 at x -121)
def road_z(x):
    for (xa, za), (xb, zb) in zip(ROADC, ROADC[1:]):
        if x <= xb: return za + (zb - za) * (x - xa) / (xb - xa)
    return ROADC[-1][1]
def ribbon(c, w):
    L, R = [], []
    for k, (x, z) in enumerate(c):
        a, b = c[max(0, k - 1)], c[min(len(c) - 1, k + 1)]; dx, dz = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dz)
        L.append([r3(x + dz / n * w / 2), r3(z - dx / n * w / 2)]); R.append([r3(x - dz / n * w / 2), r3(z + dx / n * w / 2)])
    return L + R[::-1]
ROAD = ribbon(ROADC, 10.0)
add("first court road", {"type": "prism", "plan": {"points": ROAD}, "height": r3(PT + 0.06), "slope": [r3(SLOPE), 0], "walked": True, "at": [[0, 0, 0, 0]],
                         "_about": "the road through the First Court, paved"})
# HAGIA IRENE (6th c., the palace's armoury): the domed basilica, its atrium to the west (OSM relation 4742554) -- a
# massing in brick: the aisles' block, the apse, the main dome on its windowed drum (15 m, 35 m up), the lower west dome
add("irene atrium", {"type": "enclosure", "plan": {"rect": [IRW_, 38.0]}, "thickness": 1.4, "height": 8.0, "glass": False, "interior": False,
                     "openings": {"every": 4.2, "width": 2.4, "end": 3.0, "sill": 0, "springing": 4.2, "head": {"profile": "semicircular"}},
                     "faces": {"0": [], "2": [{"at": 0, "width": 3.0, "sill": 0, "springing": 4.6, "head": {"profile": "semicircular"}, "glass": False}]},
                     "at": [ir_at(0, -ir_len / 2 + 19.0)], "_about": "HAGIA IRENE's atrium, the arcaded court before the church"})
add("irene atrium roofs", {"type": "prism", "plan": {"rect": [IRW_ + 0.8, 38.8], "well": {"rect": [20.0, 24.0], "at": [0, 0]}}, "height": 0.5, "flatRoof": True, "railing": False,
                           "at": [ir_at(0, -ir_len / 2 + 19.0, 8.0)], "standsOn": ["irene atrium"]})
add("irene", {"type": "enclosure", "plan": {"rect": [IRW_, 50.0]}, "thickness": 1.8, "height": 16.0, "glass": True, "interior": True,
              "tiers": [{"h": 8.0, "openings": {"every": 4.6, "width": 1.6, "end": 3.0, "sill": 2.0, "springing": 5.6, "head": {"profile": "semicircular"}}},
                        {"openings": {"every": 4.6, "width": 1.6, "end": 3.0, "sill": 2.0, "springing": 5.6, "head": {"profile": "semicircular"}}}],
              "faces": {"2": [{"h": 8.0, "openings": [{"at": 0, "width": 3.2, "sill": 0, "springing": 5.0, "head": {"profile": "semicircular"}, "glass": False}]},
                              {"openings": [{"at": 0, "width": 4.0, "sill": 1.6, "springing": 5.0, "head": {"profile": "semicircular"}}]}]},
              "at": [ir_at(0, -ir_len / 2 + 38.0 + 25.0)], "_about": "the church: the aisles and galleries' block, round-headed windows in two rows"})
add("irene roof", {"type": "prism", "plan": {"rect": [IRW_ + 0.6, 50.6]}, "height": 0.5, "flatRoof": True, "at": [ir_at(0, -ir_len / 2 + 63.0, 16.0)], "standsOn": ["irene"]})
add("irene apse", {"type": "prism", "plan": {"points": [[r3(7.6 * math.cos(PI * k / 10)), r3(7.6 * math.sin(PI * k / 10))] for k in range(11)]}, "height": 13.0, "flatRoof": True,
                   "at": [ir_at(0, -ir_len / 2 + 88.0)], "_about": "the apse to the east"})
add("irene apse dome", {"type": "dome", "radius": 7.6, "thickness": 0.4, "sides": 20, "head": {"profile": "semicircular"}, "at": [ir_at(0, -ir_len / 2 + 88.0, 13.0)],
                        "standsOn": ["irene apse"]})
for nm, s, w, h, R_d, dh in (("irene main", -ir_len / 2 + 72.0, 17.0, 20.0, 7.6, 4.4), ("irene west", -ir_len / 2 + 51.0, 15.0, 18.0, 6.6, 1.6)):
    add(nm + " tower", {"type": "prism", "plan": {"rect": [w, w]}, "height": h, "flatRoof": True, "at": [ir_at(0, s)], "courses": [{"y": r3(h - 0.5), "h": 0.5, "out": 0.25, "profile": "cornice"}],
                        "_about": "the square the dome stands on, over the church's roofs"})
    add(nm + " drum", {"type": "enclosure", "plan": {"sides": 20, "radius": R_d + 0.6}, "thickness": 0.6, "height": dh, "glass": True,
                       "openings": [{"at": 0, "width": 1.0, "sill": 0.6, "springing": r3(dh - 0.9), "head": {"profile": "semicircular"}}] if dh > 2 else [],
                       "at": [ir_at(0, s, h)], "standsOn": [nm + " tower"]})
    add(nm + " dome", {"type": "dome", "radius": r3(R_d + 0.6), "thickness": 0.5, "sides": 20, "head": {"profile": "semicircular"}, "at": [ir_at(0, s, h + dh)],
                       "standsOn": [nm + " drum"], "_about": "the main dome, 15 m across, 35 m up" if nm == "irene main" else "the lower dome over the west bay"})
# the Imperial Mint's old buildings on the court (Kimyahane, the bakers' mescid)
for nm in ("kimyahane", "firincilar"):
    pts = OSM[nm]; y0 = yR(min(p[0] for p in pts)) - 0.1
    solid(nm, pts, r3(y0), 8.0 if nm == "kimyahane" else 6.0, about="the Kimyahane on the First Court (OSM way 103907803)" if nm == "kimyahane" else "the Fırıncılar mescidi (OSM way 1456476427)")

# =====================================================================================================================
# THE GATE OF SALUTATION (Bâbüsselâm): the crenellated wall between two octagonal towers under pointed lead caps
# =====================================================================================================================
GW_T, GW_H = 3.0, 10.5
add("gate wall", {"type": "wall", "width": 125.8, "height": GW_H, "thickness": GW_T, "glass": False,
                  "openings": [{"at": 63.0, "width": 4.2, "sill": 0, "springing": 4.6, "head": POINTED}],
                  "at": [[r3(GW_T / 2), PT, r3((-62.8 + 63.0) / 2), Q]],
                  "_about": "the Middle Gate's crenellated wall, the court's wall on the First Court's side, the passage through it at the origin"})
add("gate crenellation", {"type": "box", "width": 1.0, "length": 0.7, "height": 0.9,
                          "at": [[0.35, PT + GW_H, r3(-62.3 + 1.9 * k), Q] for k in range(66)], "standsOn": ["gate wall"], "_about": "its merlons"})
TW = 5.0
add("gate towers", comp("conical-tower", {"sides": 8, "w": TW, "H": 14.5, "beltY": GW_H, "corH": 0.7, "corOut": 0.3, "capH": 10.5, "capR": 3.2},
                        [[r3(-3.2 + TW / 2), PT - 0.1, -9.1, 0], [r3(-3.2 + TW / 2), PT - 0.1, 9.25, 0]],
                        _about="the two octagonal towers either side of the passage (OSM's bumps: 5 m across, 18.35 m apart), under their pointed lead caps"))
add("gate porch", comp("ottoman-portico", {"n": 3, "B": 3.6, "colH": 4.6, "colR": 0.26, "D": 3.0, "eave": 1.6, "back": 0, "arches": "no", "archH": 0.6},
                       [[-3.0, r3(yR(-3.0) - 0.02), 0, -Q]], _about="the porch before the passage on the First Court's side"))
GB = R_['gate block']
add("gate hall", {"type": "enclosure", "plan": {"rect": [r3(GB[1] - GB[0] - 6.0), 12.0]}, "thickness": 1.4, "height": 9.0, "glass": False, "interior": True,
                  "openings": [], "faces": {"1": [DOOR(0, 4.2, 4.6)], "3": [DOOR(0, 4.2, 4.6)]}, "at": [[r3((GB[0] + GB[1] - 6.0) / 2), PT, 0, 0]],
                  "_about": "the hall the passage runs through, from the gate wall to the court"})
add("gate hall roof", {"type": "roof", "form": "hip", "width": r3(GB[1] - GB[0] - 5.4), "length": 12.6, "pitch": 20, "overhang": 0.3,
                       "at": [[r3((GB[0] + GB[1] - 6.0) / 2), PT + 9.0, 0, 0]], "standsOn": ["gate hall"]})
for nm, z0, z1 in (("guard rooms north", GB[2], -6.0), ("guard rooms south", 6.0, GB[3])):
    block(nm, (GB[0], GB[1] - 6.0, z0, z1), PT, 7.5, faces={0: [], 2: [], 3: []}, every=3.4, about="the guard rooms either side of the gate hall")
add("gate inner portico", comp("ottoman-portico", {"n": 9, "B": r3((GB[3] - GB[2]) / 9), "colH": 4.6, "colR": 0.28, "archH": 3.9, "D": 6.0, "eave": 2.4, "back": 0},
                               [[GB[1], PT, r3((GB[2] + GB[3]) / 2), Q]], _about="the portico on the gate's court side, its broad eave over the passage's mouth"))
for nm in ("gate wall north", "gate wall south"):
    block(nm, R_[nm], PT, 8.0, faces={3: []}, every=3.6, about="the rooms along the court's wall")

# =====================================================================================================================
# THE SECOND COURT (Divan Meydanı): the porticoes round it, the paths, the trees
# =====================================================================================================================
PC = {"colH": 4.6, "archH": 3.9, "D": 5.0, "eave": 2.4}
def row(a, b, n, about, **kw):
    return comp("ottoman-portico", {**PC, "n": n, "B": r3(abs(b - a) / n), **kw}, None, _about=about)
def place(d, x, z, yaw, y=PT):
    d["at"] = [[r3(x), y, r3(z), r3(yaw)]]; return d
CK = 63.0                                                   # the kitchen portico's column line (the court's edge in OSM)
XF = 162.4                                                  # the Felicity side's column line, 5.3 m before the range
add("kitchen portico", place(row(GB[1] + 0.3, XF, 30, "the portico all down the kitchens' side, the three kitchen gates in the range behind it",
                                 back=0, eaveL=0.3, eaveR=5.1), (GB[1] + 0.3 + XF) / 2, CK, PI))
add("felicity portico south", place(row(CK, 38.7, 5, "the portico south of the Gate of Felicity", back=0, endL=0, eaveL=0, eaveR=0), XF, (CK + 38.7) / 2, -Q))
add("felicity portico north", place(row(22.3, 3.2, 4, "the portico north of it, to the range's corner", back=0, eaveL=0, eaveR=0.6), XF, (22.3 + 3.2) / 2, -Q))
NWP = OSM['nw portico']                                     # front edge (36.1,-54.7)-(106.9,-47.8), 6 m deep
nwa, nwb = NWP[3], NWP[0]; nwL = math.dist(nwa, nwb); nwy = math.atan2(nwb[1] - nwa[1], nwb[0] - nwa[0])
add("nw portico", place(row(0, nwL, 15, "the portico along the court's north-west side (OSM's roof, way 1396051571), its back wall over the stables' yard",
                            D=5.4, back=1, door="yes", gW=3.0, gS=3.8), (nwa[0] + nwb[0]) / 2, (nwa[1] + nwb[1]) / 2, r3(-nwy) + 0.0))
DP = R_['divan portico']
add("divan portico", place(row(DP[0], DP[1], 8, "the Divan's portico under its deep painted eave (OSM's roof, way 335402671)", D=4.9, back=0, eaveL=0, eaveR=0.6),
                           (DP[0] + DP[1]) / 2, DP[3], 0))
add("divan portico west", place(row(DP[3], DP[2], 5, "its wing before the Tower of Justice and the Carriage Gate to the Harem", D=11.9, back=0, endL=0, eaveL=0, eaveR=0.4, pitch=8),
                                DP[0], (DP[2] + DP[3]) / 2, -Q))
# the paths: from the Gate of Salutation to the Gate of Felicity and to the Divan; the trees in the court's lawns
def path(name, a, b, w, y):
    L = math.dist(a, b); yaw = math.atan2(b[1] - a[1], b[0] - a[0])
    add(name, {"type": "box", "width": r3(L), "length": w, "height": 0.06, "walked": True, "at": [[r3((a[0] + b[0]) / 2), y, r3((a[1] + b[1]) / 2), r3(-yaw)]]})
path("court path felicity", (GB[1] + 6.0, 0.0), (XF - 0.3, 30.5), 5.0, PT)
path("court path divan", (GB[1] + 6.0, 0.0), (122.0, -20.8), 4.0, PT)
path("court path kitchens", (70.0, 9.0), (85.0, CK - 0.3), 3.0, PT)

# =====================================================================================================================
# THE KITCHENS: the court range with its gates, the kitchen street, Sinan's two rows of ten domed kitchens with a
# chimney on every dome, the confectionery's row at the south-west end, the larders at the north-east end
# =====================================================================================================================
KR = (GB[1] + 0.3, 165.0, 68.0, 74.2)
block("kitchen range", KR, PT, 8.5, faces={0: [DOOR(at_on(0, KR, x), 2.8, 3.6) for x in (40.0, 85.0, 130.0)],
                                           2: [DOOR(at_on(2, KR, x), 2.8, 3.6) for x in (40.0, 85.0, 130.0)], 3: []}, every=6.0, sill=2.2, spr=3.6, interior=True,
      about="the range between the portico and the kitchen street (OSM's strip, 6 m), its three gates")
KB, KP, KZ = 9.85, 0.75, 79.1
kx = (59.4 + 165.0) / 2
kit = {"n": 10, "B": KB, "p": KP, "SP": 6.0, "cn": 16, "dh": 0.4, "chimney": "yes", "chH": "s * 0.75", "chCap": "cone", "wSill": 3.0, "wSpr": 4.6}
add("kitchens", comp("domed-arcade", {**kit, "front": "doors", "gW": 2.4, "gS": 3.4, "back": 1, "backWin": "arches"}, [[r3(kx), PT, r3(KZ + KP), PI]],
                     _about="Sinan's kitchens on the street: ten domed halls (OSM: 21.4 m deep in two rows, 105 m long), a door into each, a chimney on every dome"))
add("kitchens rear", comp("domed-arcade", {**kit, "front": "wall", "back": 0, "backWin": "arches"}, [[r3(kx), PT, r3(KZ + KP + 2 * KB + KP), 0]],
                          _about="the seaward row: ten more domes and chimneys"))
HB = 11.4
add("confectionery", comp("domed-arcade", {"n": 5, "B": HB, "p": 0.75, "SP": 5.0, "cn": 16, "dh": 0.4, "chimney": "yes", "chH": "s * 0.6", "chCap": "cone",
                                           "front": "door", "gW": 2.4, "gS": 3.4, "back": 1, "backWin": "gate", "wSill": 3.0, "wSpr": 4.4},
                          [[r3((0.9 + 59.4) / 2), PT, r3(87.2 + 0.75), PI]], _about="the confectionery (helvahane) and its row at the street's south-west end: five domes"))
block("larders", (165.0, 173.2, 74.2, 100.2), PT, 9.0, every=4.0, about="the range closing the kitchens' north-east end")

# =====================================================================================================================
# THE IMPERIAL COUNCIL (Kubbealtı), THE TOWER OF JUSTICE, THE OUTER TREASURY
# =====================================================================================================================
DV = R_['divan']
DB, DPp = 8.9, 1.2
add("divan", comp("domed-arcade", {"n": 3, "B": DB, "p": DPp, "SP": 6.0, "cn": 16, "front": "door", "gW": 2.2, "gS": 3.0, "wSill": 1.6, "wSpr": 3.6},
                  [[r3((DV[0] + DV[1]) / 2), PT, r3(DV[3] - DPp), 0]], _about="the Kubbealtı: the council chamber, the chancery and the Defterhane, three domed rooms (OSM 26.6 x 11.8 m)"))
TJ = R_['tower']
add("tower of justice", comp("conical-tower", {"plan": "square", "w": 8.5, "H": 25.0, "beltY": 12.0, "corH": 0.8, "corOut": 0.35,
                                               "upper": "yes", "Hu": 7.5, "wu": 7.6, "ucH": 0.7, "upperCols": "yes", "upperPed": "yes", "pedH": 1.5,
                                               "capR": 3.9, "capH": 10.0},
                              [[r3((TJ[0] + TJ[1]) / 2), PT, r3((TJ[2] + TJ[3]) / 2), 0]],
                              _about="the Tower of Justice (OSM 8.8 x 8.4 m), the palace's tallest, 44 m: the stone shaft, Mahmud II's marble stage (1825: a tall arched "
                                     "window between paired columns in every face, segmental pediments) and the slender lead cone"))
TR = R_['treasury']
TB, TP = 8.1, 0.6
tre = {"n": 4, "B": TB, "p": TP, "SP": 6.0, "cn": 12, "wSill": 2.4, "wSpr": 4.4}
add("treasury", comp("domed-arcade", {**tre, "front": "door", "dOff": 4.0, "back": 1, "backWin": "arches"}, [[r3((TR[0] + TR[1]) / 2), PT, r3(TR[3] - TP), 0]],
                     _about="the Outer Treasury's court-side row of four domes, stone and brick (OSM 32.3 x 17.7 m)"))
add("treasury rear", comp("domed-arcade", {**tre, "front": "wall", "back": 0, "backWin": "arches"}, [[r3((TR[0] + TR[1]) / 2), PT, r3(TR[3] - TP - 2 * TB - TP), PI]],
                          _about="its back row, opening into the first through the spine's arches: eight domes in all"))
HAL = OSM['halberdiers']
solid("halberdiers", HAL, PT, 9.0, about="the dormitory of the halberdiers with tresses and the range along the palace's north-west wall over the stables (OSM way 32396154)")
add("carriage gate", {"type": "box", "width": 3.2, "length": 0.1, "height": 4.0, "at": [[111.3, PT, -44.0, 0]], "_about": "the Carriage Gate into the Harem, by the Tower of Justice"})

# =====================================================================================================================
# THE HAREM: OSM's outline and its three courts (relation 4743322; OSM leaves the courts unnamed -- named here from the
# published plans: the Black Eunuchs' court by the Carriage Gate, the Concubines' court over the Golden Horn, the Valide
# Sultan's in the middle). Seven ranges of different heights (8.5 to 15 m), split where the plans' blocks meet, each court
# a well in its range; the Golden Road (Altın Yol) a lane between the Harem's body and its range along the Third Court;
# the roofscape: the great domes of its halls, sixty small domes of rooms and baths, forty chimneys, raised rooms,
# a tower -- walled up as massing, not walked (the courts and the lane paved, seen from above)
# =====================================================================================================================
HA = OSM['harem']
def court_well(c):
    xs, zs = [p[0] for p in c], [p[1] for p in c]
    return [r3(max(xs) - min(xs) - 1.0), r3(max(zs) - min(zs) - 1.0)], [r3(sum(xs) / 4), r3(sum(zs) / 4)]
GR = (-44.5, -41.5)                                         # the Golden Road's sides (z), from x 160 to 234
HAREM = [  # name, plan, height, court, what
    ("harem eunuchs", clips(HA, (1, 0, 160.0), (0, -1, 105.0)), 11.0, 'harem court b', "the Black Eunuchs' quarters round their court, by the Carriage Gate"),
    ("harem concubines", clips(HA, (1, 0, 160.0), (0, 1, -105.0)), 9.5, 'harem court c', "the Concubines' court and their dormitory and baths over the Golden Horn"),
    ("harem mosque range", clips(HA, (-1, 0, -160.0), (1, 0, 175.0), (0, 1, GR[0])), 13.5, None, "the range between, the eunuchs' mosque"),
    ("harem valide", clips(HA, (-1, 0, -175.0), (1, 0, 212.0), (0, 1, GR[0])), 12.0, 'harem court a', "the Valide Sultan's apartments round her court"),
    ("harem imperial hall", clips(HA, (-1, 0, -212.0), (1, 0, 234.0), (0, 1, GR[0])), 15.0, None, "the Imperial Hall (Hünkâr Sofası), the Sultan's baths"),
    ("harem privy", clip(HA, -1, 0, -234.0), 10.5, None, "Murad III's Privy Chamber, the Twin Kiosk, the Favourites' court"),
    ("harem road range", clips(HA, (-1, 0, -160.0), (1, 0, 234.0), (0, -1, -GR[1])), 8.5, None, "the range along the Golden Road's south side, against the Third Court"),
]
HRANGES = []
for nm, pts, H, court, what in HAREM:
    if court:
        (cw, cl), (cx_, cz_) = court_well(OSM[court])
        plan = {"points": [[r3(x - cx_), r3(z - cz_)] for x, z in pts], "well": {"rect": [cw, cl], "at": [0, 0]}}; at = [cx_, PT, cz_, 0]
    else: plan = {"points": pts}; at = [0, PT, 0, 0]
    add(nm, {"type": "prism", "plan": plan, "height": H, "at": [at], "flatRoof": True, "railing": False,
             "courses": [{"y": r3(H - 0.6), "h": 0.6, "out": 0.35, "profile": "cornice"}], "_about": ("THE HAREM: " if nm == "harem eunuchs" else "") + what})
    HRANGES.append((nm, pts, H, court))
for court, about in (('harem court a', "the Valide Sultan's court"), ('harem court b', "the Black Eunuchs' court"), ('harem court c', "the Concubines' court")):
    (cw, cl), (cx_, cz_) = court_well(OSM[court])
    add(court, {"type": "prism", "plan": {"rect": [cw, cl]}, "height": 0.1, "flatRoof": True, "at": [[cx_, PT, cz_, 0]], "standsOn": ["plateau"],
                "_about": about + ", paved (the Harem is built as its massing: its courts are seen, not walked into)"})
add("harem garden court", {"type": "prism", "plan": {"points": [[166.8, -124.4], [162.7, -94.6], [171.3, -93.7], [172.2, -99.8], [188.3, -98.3], [189.7, -108.8], [198.1, -108.0],
                                                             [199.5, -120.6], [209.2, -119.5]]}, "height": 0.1, "flatRoof": True, "at": [[0, PT, 0, 0]], "standsOn": ["plateau"],
                          "_about": "the court the Harem's ranges close against the outer wall (outside OSM's Harem, inside the palace's), paved"})
add("golden road", {"type": "prism", "plan": {"points": clips(HA, (-1, 0, -160.0), (1, 0, 234.0), (0, 1, GR[1]), (0, -1, -GR[0]))}, "height": 0.1, "flatRoof": True,
                    "at": [[0, PT, 0, 0]], "standsOn": ["plateau"], "_about": "the Golden Road (Altın Yol), the Harem's lane from its gate to the Third Court, paved"})
add("harem windows", {"type": "box", "width": 1.0, "length": 0.08, "height": 1.6, "at": marks(HA, 3.6, PT + 2.0, 1.0, 1.6) + marks(HA, 3.6, PT + 6.0, 1.0, 1.6),
                      "_about": "the Harem's windows, two storeys, on its outer faces"})
def seg_d(p, a, b):
    dx, dz = b[0] - a[0], b[1] - a[1]; t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dz) / (dx * dx + dz * dz or 1)))
    return math.hypot(p[0] - a[0] - dx * t, p[1] - a[1] - dz * t)
def roof_at(x, z, clear):
    """the Harem's roof height at (x, z) if a dome or chimney `clear` m across fits there (away from courts, the lane, the ranges' edges)"""
    for nm, pts, H, court in HRANGES:
        if not pip((x, z), pts) or min(seg_d((x, z), pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))) < clear: continue
        for c in ('harem court a', 'harem court b', 'harem court c'):
            (cw, cl), (cx_, cz_) = court_well(OSM[c])
            if abs(x - cx_) < cw / 2 + clear and abs(z - cz_) < cl / 2 + clear: return None
        return PT + H
    return None
import random
rng = random.Random(1459)
BIG = [(212.0, -66.0, 5.2), (224.0, -96.0, 4.6), (204.0, -84.0, 4.2), (246.0, -52.0, 4.0), (166.0, -80.0, 3.8), (250.0, -80.0, 3.6), (140.0, -78.0, 3.4)]
big = [(x, z, roof_at(x, z, r + 0.5)) for x, z, r in BIG]
for k, (x, z, r) in enumerate(BIG):
    if big[k][2] is not None: domes(f"harem dome {k + 1}", [big[k]], None, r, drum=1.4, cn=16,
                                    about="the great domes of the Harem's halls: the Imperial Hall, Murad III's Privy Chamber, the Valide Sultan's hall, the Twin Kiosk, the mosque, the baths" if k == 0 else "")
taken = [(x, z, r) for x, z, r in BIG]
SMALL = {1.6: [], 2.2: [], 2.9: []}
CHIM = []
for gx in range(112, 272, 5):
    for gz in range(-132, -34, 5):
        x, z = gx + rng.uniform(-1.6, 1.6), gz + rng.uniform(-1.6, 1.6); u = rng.random()
        if u < 0.42:
            r = rng.choice(list(SMALL)); y = roof_at(x, z, r + 0.6)
            if y is not None and all(math.hypot(x - a, z - b) > r + c + 0.8 for a, b, c in taken) and sum(len(v) for v in SMALL.values()) < 64:
                SMALL[r].append((x, z, y)); taken.append((x, z, r))
        elif u < 0.62:
            y = roof_at(x, z, 1.0)
            if y is not None and all(math.hypot(x - a, z - b) > c + 1.4 for a, b, c in taken) and len(CHIM) < 42:
                CHIM.append((x, z, y)); taken.append((x, z, 0.6))
for r, pts in SMALL.items():
    domes(f"harem domes {r}", pts, None, r, drum=0.4 if r < 2 else 0.6, cn=12, about="the small domes over the Harem's rooms and baths")
chimneys("harem chimneys", CHIM, None, 2.6, 0.42)
for k, (x, z, w, l, h) in enumerate([(150.0, -62.0, 9.0, 7.0, 3.0), (196.0, -100.0, 8.0, 10.0, 3.5), (238.0, -92.0, 10.0, 8.0, 3.0), (256.0, -66.0, 7.0, 7.0, 2.5)]):
    y = roof_at(x, z, max(w, l) / 2 + 0.3)
    if y is None: continue
    add(f"harem upper room {k + 1}", {"type": "prism", "plan": {"rect": [w, l]}, "height": h, "at": [[x, r3(y), z, 0]], "_about": "a raised room over the roofs" if k == 0 else ""})
    add(f"harem upper room {k + 1} roof", {"type": "roof", "form": "hip", "width": w + 1.2, "length": l + 1.2, "pitch": 18, "overhang": 0.3, "at": [[x, r3(y + h), z, 0]],
                                          "standsOn": [f"harem upper room {k + 1}"]})
ty = roof_at(262.0, -50.0, 3.2)
add("harem tower", {"type": "prism", "plan": {"rect": [6.0, 6.0]}, "height": 6.0, "at": [[262.0, r3(ty), -50.0, 0]], "_about": "the Harem's tower (the Tower of the Favourites)"})
add("harem tower roof", {"type": "roof", "form": "pyramid", "width": 7.4, "length": 7.4, "pitch": 30, "overhang": 0.4, "at": [[262.0, r3(ty + 6.0), -50.0, 0]],
                         "standsOn": ["harem tower"]})
print("harem:", sum(len(v) for v in SMALL.values()), "small domes,", len(CHIM), "chimneys, tower at", ty)

# =====================================================================================================================
# THE GATE OF FELICITY (Bâbüssaâde) and THE THIRD COURT (Enderûn)
# =====================================================================================================================
FR = R_['felicity range']
FZ = 30.5                                                   # the passage (the canopy's middle)
block("felicity range", FR, PT, 11.0, faces={3: [DOOR(at_on(3, FR, FZ), 3.8, 4.4)], 1: [DOOR(at_on(1, FR, FZ), 3.8, 4.4)]}, every=4.4, interior=True,
      about="the range closing the Second Court, the Gate of Felicity through it")
block("felicity north", R_['felicity north'], PT, 11.0, every=4.4, about="its end behind the Outer Treasury")
block("felicity south", R_['felicity south'], PT, 11.0, every=4.4, about="its end by the kitchens")
add("felicity gate", comp("ottoman-portico", {"n": 3, "B": 5.4, "colH": 8.0, "colR": 0.32, "D": 6.7, "eave": 3.0, "back": 0, "dome": "yes",
                                              "domeR": 3.2, "arches": "no", "archH": 0.8, "pitch": 10, "roofForm": "hip"},
                          [[R_['felicity canopy'][0] + 6.7 - 0.01, PT, FZ, -Q]], _about="the Gate of Felicity's canopy (OSM 16.4 x 6.7 m): marble columns, the deep eave, the dome over the passage"))
AR = R_['arz']
add("audience chamber", comp("ottoman-kiosk", {"W": 19.5, "L": 17.4, "H": 6.0, "G": 3.5, "nf": 7, "ns": 6, "eave": 2.4},
                             [[r3((AR[0] + AR[1]) / 2), PT, r3((AR[2] + AR[3]) / 2), -Q]],
                             _about="the Arz Odası: the throne room in its colonnade of 22 columns under the deep roof (OSM's outline its eaves: 29.2 x 31.3 m), facing the gate"))
# the Library of Ahmed III (1719): a Greek cross, the dome over its middle, on a basement; the porch its fourth arm, stairs both sides
LB = 1.6
add("library basement", {"type": "prism", "plan": {"points": OSM['library']}, "height": LB, "at": [[0, PT, 0, 0]], "walked": True,
                         "courses": [{"y": r3(LB - 0.25), "h": 0.25, "out": 0.12, "profile": "cornice"}], "_about": "the LIBRARY OF AHMED III (1719) on its low basement (OSM way 32396231)"})
add("library", {"type": "enclosure", "plan": {"rect": [10.0, 9.0]}, "thickness": 1.0, "height": 8.0, "glass": True, "interior": True,
                "openings": [{"at": 0, "width": 2.0, "sill": 0, "springing": 3.0, "head": POINTED, "glass": False}], "at": [[223.0, PT + LB, 20.0, 0]],
                "_about": "the domed reading hall at the cross's middle, an arch into every arm"})
for nm, (x0, x1, z0, z1) in {"library arm north": (218.1, 228.2, 10.2, 15.5), "library arm south": (217.7, 227.8, 24.5, 29.3), "library arm east": (228.0, 231.0, 15.9, 24.9)}.items():
    block(nm, (x0, x1, z0, z1), PT + LB, 6.0, every=2.6, sill=1.0, spr=3.6, roof="flat", eave=0.4, interior=False,
          faces={{"library arm north": 0, "library arm south": 2, "library arm east": 3}[nm]: [{"at": 0, "width": 2.0, "sill": 0, "springing": 3.0, "head": POINTED, "glass": False}]})
add("library porch", comp("ottoman-portico", {"n": 2, "B": 2.8, "colH": 3.8, "colR": 0.2, "archH": 2.6, "D": 2.8, "eave": 1.2, "back": 0},
                          [[218.0, PT + LB, 20.0, -Q]], _about="the porch, the cross's fourth arm, toward the Audience Chamber"))
for e in (-1, 1):
    flight(f"library stair {'north' if e < 0 else 'south'}", (214.2, 20.0 + e * 2.0 + e * round(LB / 0.17) * 0.32), (0, -e), 1.4, PT, PT + LB,
           "a flight up to the porch from either side")
domes("library dome", [(223.0, 20.0)], PT + LB + 8.0, 4.6, drum=1.4, about="the library's dome")
# the Mosque of the Agas (turned to Mecca) with its minaret, the dormitories round the court with their porticoes
AG = OSM['agas mosque']
agc = (sum(p[0] for p in AG) / 4, sum(p[1] for p in AG) / 4); agL = math.dist(AG[1], AG[2]); agW = math.dist(AG[0], AG[1])
agy = math.atan2(AG[2][1] - AG[1][1], AG[2][0] - AG[1][0])
add("agas mosque", {"type": "enclosure", "plan": {"rect": [r3(agL), r3(agW)]}, "thickness": 1.1, "height": 9.0, "glass": True, "interior": False,
                    "openings": WIN(3.6, 1.4, 3.6), "at": [[r3(agc[0]), PT, r3(agc[1]), r3(-agy)]],
                    "_about": "the Mosque of the Agas (OSM way 32396236), turned to Mecca across the court's lines"})
add("agas mosque roof", {"type": "roof", "form": "hip", "width": r3(agL + 1.6), "length": r3(agW + 1.6), "pitch": 18, "overhang": 0.3,
                         "at": [[r3(agc[0]), PT + 9.0, r3(agc[1]), r3(-agy)]], "standsOn": ["agas mosque"]})
add("agas minaret", comp("ottoman-minaret", {"foot": 5.0, "h": 21.0, "r": 1.1, "balconies": 1, "tier": 15.0, "bw": 0.7},
                         [[r3(AG[0][0] + 1.0), PT, r3(AG[0][1] - 1.0), 0]], _about="its minaret"))
for nm, face, about in (("has oda dorm", 0, "the dormitory of the Privy Chamber's pages along the court's north-west side"),
                        ("dorm ne1", 3, "a dormitory on the Third Court's north-east side"), ("dorm ne2", 3, "the next"),
                        ("seferli", 2, "the Dormitory of the Expeditionary Force (1635)"), ("dorm se", 2, "the dormitory beside it")):
    r = R_[nm]
    block(nm, r, PT, 9.0, every=3.8, faces={face: [DOOR(0, 2.0, 2.8)]}, interior=False, about=about)
for nm, a, b, line, yaw, n in (("has oda portico", 227.4, 261.9, -8.0, 0, 9), ("seferli portico", 196.1, 229.3, 74.1, PI, 8), ("dorm ne portico", 9.5, 42.3, 268.5, -Q, 8)):
    if yaw == -Q: add(nm, place(row(a, b, n, "the portico before it", D=4.4, back=0), line, (a + b) / 2, yaw))
    else: add(nm, place(row(a, b, n, "the portico before it", D=4.4, back=0), (a + b) / 2, line, yaw))
# the Conqueror's Pavilion (the Treasury), two floors on its terrace over the Marmara, the loggia of double arches
TPV = R_['treasury pavilion']
TPR = (TPV[0], TPV[1], TPV[2], 95.5)
block("treasury pavilion", TPR, PT, 11.0, interior=False, every=4.0, faces={0: [DOOR(at_on(0, TPR, x), 2.4, 3.4) for x in (243.0, 271.0)], 2: [DOOR(at_on(2, TPR, 257.0), 2.6, 3.6)]},
      tiers=[{"h": 5.5, "openings": WIN(4.0, 1.4, 3.6)}, {"openings": WIN(4.0, 1.2, 3.4)}], roof="flat", eave=0.5,
      about="the CONQUEROR'S PAVILION (c. 1460), the Imperial Treasury: two floors, four domed rooms")
add("treasury loggia", comp("ottoman-portico", {"n": 14, "B": r3((TPV[1] - TPV[0]) / 14), "colH": 5.0, "colR": 0.3, "archH": 4.2, "D": 4.6, "eave": 0.6, "back": 0, "pitch": 6},
                            [[r3((TPV[0] + TPV[1]) / 2), PT, 100.1, 0]], _about="its loggia of arches over the Marmara, the terrace before the treasury's rooms"))
domes("treasury pavilion domes", [(x, 83.4) for x in (237.0, 251.0, 265.0, 278.0)], PT + 11.45, 4.8, drum=1.0, about="the treasury's four domes")
# the Pavilion of the Holy Mantle (the Privy Room, Has Oda): its four domed chambers, the porch on the court
HM = R_['holy mantle']
block("holy mantle", HM, PT, 10.0, every=4.0, faces={0: [DOOR(at_on(0, HM, 278.5), 2.4, 3.2)]}, interior=False, roof="flat", eave=0.5,
      about="the PAVILION OF THE HOLY MANTLE (Has Oda, Mehmed II's privy chambers, the relics' rooms)")
domes("holy mantle domes", [(271.0, -33.0), (284.0, -33.0), (271.0, -17.0), (284.0, -17.0)], PT + 10.45, 5.6, drum=1.0, about="its four domed chambers")
HP = R_['holy mantle porch']
add("holy mantle porch", comp("ottoman-portico", {"n": 5, "B": r3((HP[1] - HP[0]) / 5), "colH": 4.8, "colR": 0.3, "archH": 3.4, "D": r3(HP[3] - HP[2]), "eave": 1.8, "back": 0},
                              [[r3((HP[0] + HP[1]) / 2), PT, HP[3], 0]], _about="the domed porch with its fountain before the chambers"))

# =====================================================================================================================
# THE FOURTH COURT: the marble terrace with its pool, the Baghdad and Revan kiosks, the Circumcision Room, the Iftariye;
# the lower garden with the Sofa Kiosk, the Mecidiye, the Sofa Mosque
# =====================================================================================================================
BG = OSM['baghdad']
bgc = (sum(p[0] for p in BG) / len(BG), sum(p[1] for p in BG) / len(BG))
bgt = math.atan2(BG[2][1] - BG[1][1], BG[2][0] - BG[1][0])      # the kiosk's turn off the frame (its SE face, 10 deg)
add("baghdad kiosk", comp("ottoman-kiosk", {"W": 14.6, "L": 13.6, "H": 5.4, "G": 3.2, "nf": 6, "ns": 6, "eave": 2.4, "plat": 0.6, "dome": "yes", "domeR": 4.4, "pitch": 14},
                          [[r3(bgc[0]), PT, r3(bgc[1]), r3(-bgt - Q)]],
                          _about="the BAGHDAD KIOSK (1638-39): the domed octagon widened by four iwans, in its colonnade of marble columns under the deep eaves (OSM 26 x 25 m, its eaves)"))
RV = R_['revan']
add("revan kiosk", comp("ottoman-kiosk", {"W": 14.8, "L": 7.8, "H": 5.0, "G": 1.6, "nf": 7, "ns": 4, "eave": 0.6, "plat": 0.5, "dome": "yes", "domeR": 3.4, "pitch": 14},
                        [[r3((RV[0] + RV[1]) / 2), PT, r3((RV[2] + RV[3]) / 2), Q]], _about="the REVAN KIOSK (1635): the domed room in its portico on the terrace (OSM 12.3 x 20.2 m)"))
CR = R_['circumcision']
add("circumcision room", comp("ottoman-kiosk", {"W": 11.4, "L": 7.6, "H": 5.6, "G": 1.6, "nf": 5, "ns": 3, "eave": 0.6, "plat": 0.4, "pitch": 14},
                              [[r3((CR[0] + CR[1]) / 2), PT, r3((CR[2] + CR[3]) / 2), 0]], _about="the CIRCUMCISION ROOM (1641): the tiled room under its eaved roof (OSM 16 x 13.3 m)"))
IF = OSM['iftariye']
ifc = (sum(p[0] for p in IF) / 4, sum(p[1] for p in IF) / 4)
add("iftariye columns", {"type": "column", "radius": 0.09, "height": 2.6, "sides": 8,
                         "at": [[r3(ifc[0] + a), PT, r3(ifc[1] + b), 0] for a in (-1.7, 1.7) for b in (-0.55, 0.55)], "_about": "the IFTARIYE's four bronze posts on the terrace's edge"})
add("iftariye canopy", {"type": "roof", "form": "hip", "width": 4.6, "length": 2.2, "pitch": 38, "overhang": 0.2, "at": [[r3(ifc[0]), PT + 2.6, r3(ifc[1]), 0]],
                        "standsOn": ["iftariye columns"], "_about": "its gilt bronze canopy (OSM way 1272157518)"})
PO = R_['pool']
add("pool rim", {"type": "prism", "plan": {"rect": [r3(PO[1] - PO[0]), r3(PO[3] - PO[2])], "well": {"rect": [r3(PO[1] - PO[0] - 1.0), r3(PO[3] - PO[2] - 1.0)], "at": [0, 0]}},
                 "height": 0.5, "railing": False, "at": [[r3((PO[0] + PO[1]) / 2), PT, r3((PO[2] + PO[3]) / 2), 0]], "_about": "the marble pool before the Revan Kiosk, its rim"})
add("pool water", {"type": "box", "width": r3(PO[1] - PO[0] - 1.0), "length": r3(PO[3] - PO[2] - 1.0), "height": 0.3, "at": [[r3((PO[0] + PO[1]) / 2), PT, r3((PO[2] + PO[3]) / 2), 0]]})
add("pool fountain", {"type": "column", "radius": 0.35, "height": 1.0, "sides": 10, "taper": 0.6, "at": [[r3((PO[0] + PO[1]) / 2), PT + 0.3, r3((PO[2] + PO[3]) / 2), 0]]})
add("pool ripple", {"type": "marker", "role": "flow", "at": [[r3((PO[0] + PO[1]) / 2), PT + 0.31, r3((PO[2] + PO[3]) / 2), 0]], "data": {"kind": "pool", "r": 4.0, "seg": 24}})
for i, (x, z, w, l) in enumerate(POOLS):
    y = level(x, z)
    add(f"garden pool {i + 1}", {"type": "box", "width": w, "length": l, "height": 0.35, "at": [[x, y, z, 0]], "_about": "a garden pool (OSM)"})
SK = R_['sofa kiosk']
block("sofa kiosk", SK, PL, 9.0, interior=False, faces={0: [DOOR(0, 1.8, 2.6)]}, every=2.4, eave=2.0, pitch=15,
      tiers=[{"h": 5.0, "openings": WIN(2.6, 1.0, 3.4, w=1.2)}, {"openings": {"every": 2.0, "width": 1.4, "end": 1.0, "sill": 0.6, "springing": 2.8, "head": {"profile": "flat"}}}],
      about="the SOFA KIOSK (Mustafa Paşa, rebuilt 1752): two timber storeys in the tulip garden, the upper one level with the marble terrace, under a broad eave")
MC = R_['mecidiye']
block("mecidiye kiosk", MC, PL, 11.0, interior=False, faces={2: [DOOR(0, 2.2, 3.6)]}, every=3.2, pitch=12, eave=0.8,
      tiers=[{"h": 5.6, "openings": {"every": 3.2, "width": 1.5, "end": 2.0, "sill": 0.9, "springing": 3.8, "head": {"profile": "semicircular"}}},
             {"openings": {"every": 3.2, "width": 1.4, "end": 2.0, "sill": 0.8, "springing": 3.6, "head": {"profile": "semicircular"}}}],
      courses=[{"y": 5.4, "h": 0.4, "out": 0.15, "profile": "band"}, {"y": 10.4, "h": 0.6, "out": 0.3, "profile": "cornice"}],
      about="the MECIDIYE KIOSK (1840, Abdülmecid): the last pavilion, European in its two storeys of round-headed windows, over the Marmara")
block("sofa mosque", R_['sofa mosque'], PL, 7.5, every=2.6, interior=False, faces={0: [DOOR(0, 1.8, 2.8)]}, about="the Sofa Mosque (1858)")
add("sofa minaret", comp("ottoman-minaret", {"foot": 3.0, "h": 16.0, "r": 0.9, "balconies": 1, "tier": 12.0, "bw": 0.6}, [[300.6, PL, 87.6, 0]], _about="its minaret"))
block("wardrobe", R_['wardrobe'], PL, 5.5, every=2.4, interior=False, faces={3: [DOOR(0, 1.6, 2.6)]}, about="the wardrobe room")
wall_line("fourth court wall", OSM['fourth wall'], lambda x: PL, 11.0, t=1.2, crenel=False, about="the wall between the Harem and the Fourth Court (OSM way 335415774)")

# =====================================================================================================================
# THE TREES: the First Court's planes along the road and in its lawns, the Second Court's planes and cypresses, the
# Third Court's, the Fourth Court's gardens
# =====================================================================================================================
TREES = []
def mint_z(x):
    W_ = OSM['mint wall']
    return [za + (zb - za) * (x - xa) / (xb - xa) for (xa, za), (xb, zb) in zip(W_, W_[1:]) if min(xa, xb) <= x <= max(xa, xb) and xa != xb]
for x in range(-300, -20, 14):
    for side in (-1, 1):
        z = road_z(x) + side * 9.5 + (3.0 if side > 0 else -3.0) * ((x // 14) % 2)
        if all(abs(z - wz) > 3.5 for wz in mint_z(x)): TREES.append((x, z, yR(x)))
for x, z in [(-280, -20), (-250, -12), (-200, -40), (-170, -50), (-140, -55), (-110, -45), (-80, -50), (-50, -45), (-20, -40), (-150, -20), (-100, -25), (-60, -22),
             (-230, 25), (-200, 22), (-160, 10), (-110, 14), (-70, 28), (-40, 38), (-90, 40), (-20, 50),
             (-300, -60), (-290, -95), (-280, -112), (-270, -75), (-285, -40), (-120, -90), (-95, -85), (-70, -80), (-40, -85), (-15, -80), (-195, -55)]:
    if any(pip((x, z), P_) for P_ in (RAMP, MINT)): TREES.append((x, z, yR(x)))
CYPRESS = []
for x, z in [(45, -30), (52, -18), (60, -36), (75, -26), (90, -36), (100, -10), (40, 20), (48, 40), (62, 50), (78, 44), (95, 52), (110, 40), (125, 50), (140, 44), (150, 20), (140, 0)]:
    CYPRESS.append((x, z, PT))
for x, z in [(58, 0), (82, 20), (110, 0), (130, 24), (120, -6), (66, 30)]:
    TREES.append((x, z, PT))
for x, z in [(240, 15), (245, 45), (205, 60), (255, 60), (235, -0.5)]:
    TREES.append((x, z, PT))
for x, z in [(305, 20), (310, 35), (340, 25), (350, 45), (300, 60), (330, 50), (355, 0), (362, 20), (345, -60), (360, -70), (330, -75), (305, -80), (290, -90), (320, -95)]:
    if not pip((x, z), TER): TREES.append((x, z, level(x, z)))
TREES += HILL_TREES
add("tree trunks", {"type": "column", "radius": 0.35, "height": 4.0, "sides": 8, "taper": 0.75, "at": [[r3(x), r3(y), r3(z), 0] for x, z, y in TREES],
                    "_about": "the plane trees' trunks"})
add("tree crowns", {"type": "dome", "sides": 12, "radius": 4.2, "thickness": 0, "head": {"profile": "bell", "waist": 0.98, "lift": 0.6},
                    "at": [[r3(x), r3(y + 3.4), r3(z), 0] for x, z, y in TREES], "_about": "their crowns"})
add("cypress trunks", {"type": "column", "radius": 0.2, "height": 1.5, "sides": 6, "at": [[r3(x), r3(y), r3(z), 0] for x, z, y in CYPRESS]})
add("cypresses", {"type": "dome", "sides": 10, "radius": 1.3, "thickness": 0, "head": {"profile": "trigonal", "rise": 11.0},
                  "at": [[r3(x), r3(y + 1.4), r3(z), 0] for x, z, y in CYPRESS], "_about": "the Second Court's cypresses"})

doc = {"name": "Topkapı Palace",
       "_about": "TOPKAPI PALACE, Istanbul (15th-19th c.), along its promontory from OpenStreetMap's plan (tools/archgen/topkapi.py): the Imperial Gate in the "
                 "Sur-ı Sultani and the First Court rising to the Gate of Salutation between its two capped towers; the Second Court with its porticoes, "
                 "the Imperial Council's three domes under the Tower of Justice, the Outer Treasury, Sinan's kitchens with twenty chimneys, the Harem "
                 "to the north-west; the Gate of Felicity's canopy, the Third Court with the Audience Chamber in its colonnade, the Library of Ahmed III, "
                 "the Mosque of the Agas, the dormitories, the Conqueror's Pavilion and the Pavilion of the Holy Mantle; the Fourth Court's marble "
                 "terrace with its pool, the Baghdad and Revan kiosks, the Circumcision Room and the Iftariye, the lower garden with the Sofa Kiosk and "
                 "the Mecidiye; Hagia Irene in the First Court. +x along the axis (NNE), +z the Marmara side.",
       "params": {"detail": 4}, "build": build, "parts": parts}

# ---- THE FINISH ----------------------------------------------------------------------------------------------------
PORTICOES = [n for n in parts if "portico" in n or n in ("gate porch", "felicity gate", "treasury loggia", "holy mantle porch", "library porch")]
KITCH = ["kitchens", "kitchens rear", "confectionery", "treasury", "treasury rear", "kitchen range", "larders"]
fin = {"name": "Topkapı Palace", "building": "architecture/topkapi",
       "_about": "Topkapı: pale limestone for the gates, towers, walls and the ranges; white marble for the porticoes' columns and arcades, the Tower of Justice's "
                 "lantern, the Baghdad and Revan kiosks and the terrace; Ottoman stone-and-brick (almaşık) on the kitchens and the treasury; lead on every dome, "
                 "cap and roof, the alems gilt, the Iftariye's canopy gilt; the painted soffits (saçak) under the porticoes and the kiosks' eaves; Iznik tiles "
                 "inside the Divan and the Audience Chamber; the Sofa Kiosk's timber; the Mecidiye's white plaster; Hagia Irene's brick; the courts' lawns, "
                 "paths and plane trees and cypresses.",
       "stone": {"color": "#c4b89c", "accent": "#aea286", "pat": "ashlar"},
       "rules": [
           {"parts": ["alem", "dome alem"] + [n for n in parts if n.endswith(" alems")] + ["iftariye canopy",
                      "iftariye columns"], "pattern": "roofs/gold leaf", "palette": "gold", "_about": "the alems and the Iftariye gilt"},
           {"parts": ["tree trunks", "cypress trunks"], "pattern": "timber/bark", "palette": "oak"},
           {"parts": ["tree crowns"], "color": "#5a7a3a", "accent": "#45622c", "_about": "the plane trees"},
           {"parts": ["cypresses"], "color": "#2f4a2c", "accent": "#233a21", "_about": "the cypresses, dark"},
           {"parts": ["pool water"] + [f"garden pool {i + 1}" for i in range(len(POOLS))], "color": "#4f7f8c", "accent": "#3f6c78", "_about": "the pools' water"},
           {"parts": "kind:dome", "surface": "roof", "pattern": "roofs/sheet metal", "palette": "lead"},
           {"parts": ["divan/pendentives deck", "treasury/pendentives deck", "treasury rear/pendentives deck", "kitchens/pendentives deck", "kitchens rear/pendentives deck",
                      "confectionery/pendentives deck"], "pattern": "roofs/sheet metal", "palette": "lead", "_about": "the flat leads between the domes"},
           {"parts": [n for n in parts if parts[n]["type"] == "roof"], "surface": "roof", "pattern": "roofs/sheet metal", "palette": "lead", "_about": "the lead roofs"},
           {"parts": [n for n in parts if parts[n]["type"] == "prism" and n.endswith("roof") or n == "irene atrium roofs"], "pattern": "roofs/sheet metal", "palette": "lead",
            "_about": "the flat leads over the ranges, their eaves' edges"},
           {"parts": [nm for nm, *_ in HAREM] + [n for n in parts if n.startswith("harem upper room") and not n.endswith("roof")] + ["harem tower", "halberdiers", "kimyahane", "firincilar"], "surface": "floor", "pattern": "roofs/sheet metal", "palette": "lead"},
           {"parts": ["roof", "roof hipped"], "surface": "ceiling", "pattern": "painted/sachak", "palette": "divan-green", "_about": "the painted soffits of the porticoes' and kiosks' eaves"},
           {"parts": "kind:roof", "surface": "ceiling", "pattern": "stone/plaster", "palette": "plaster-white"},
           {"parts": "kind:roof", "pattern": "roofs/sheet metal", "palette": "lead"},
           {"parts": "fascia", "pattern": "painted/sachak", "palette": "divan-green", "scale": 0.4},
           {"parts": "ceiling", "surface": "ceiling", "pattern": "painted/caisson", "palette": "divan-green"},
           {"parts": "tower of justice", "above": PT + 25.0, "pattern": "stone/marble", "palette": "carrara", "_about": "the lantern stage: white marble over the limestone shaft"},
           {"parts": ["columns shafts", "columns bases", "columns capitals", "colonnade shafts", "colonnade bases", "colonnade capitals", "colonnade entablature"], "pattern": "stone/marble", "palette": "marble-grey"},
           {"parts": ["arcade", "beam"], "pattern": "stone/marble", "palette": "carrara", "_about": "the porticoes' arches, white against the walls behind"},
           {"parts": ["divan", "audience chamber", "baghdad kiosk", "revan kiosk", "circumcision room"], "surface": "wall", "side": "in", "below": PT + 3.2, "pattern": "tiles/iznik carnation", "palette": "iznik"},
           {"parts": ["divan", "audience chamber", "baghdad kiosk", "revan kiosk", "circumcision room"], "side": "in", "pattern": "painted/kalemisi", "palette": "iznik"},
           {"parts": ["audience chamber/room", "baghdad kiosk/room", "revan kiosk/room", "circumcision room/room", "library", "library arm north", "library arm south", "library arm east"],
            "surface": "wall", "side": "out", "pattern": "stone/revetment", "palette": "carrara", "_about": "the kiosks' and the library's marble-faced walls"},
           {"parts": KITCH, "surface": "wall", "side": "out", "pattern": "stone/almasik", "palette": "almasik", "_about": "stone and brick on the kitchens and the treasury"},
           {"parts": ["chimneys", "harem chimneys"], "pattern": "stone/almasik", "palette": "almasik"},
           {"parts": ["sofa kiosk"], "surface": "wall", "side": "out", "pattern": "timber/boards", "palette": "walnut", "_about": "the Sofa Kiosk's timber"},
           {"parts": ["mecidiye kiosk"], "surface": "wall", "side": "out", "pattern": "stone/plaster", "palette": "plaster-white", "_about": "the Mecidiye's white plaster"},
           {"parts": [n for n in parts if n.startswith("irene")], "surface": "wall", "pattern": "stone/brick", "palette": "roman-brick", "_about": "Hagia Irene's brick"},
           {"parts": [n for n in parts if n.endswith("windows")] + ["carriage gate"], "color": "#2c2f31", "accent": "#1f2224", "_about": "the windows' dark panes"},
           {"parts": ["first court", "hillside"] + [f"lower garden {i + 1}" for i in range(len(LOW))], "surface": "floor", "pattern": "materials/grass", "palette": "lawn",
            "_about": "the First Court's and the gardens' lawns"},
           {"parts": ["plateau"], "surface": "floor", "within": [27.0, -46.0, 158.0, 57.0], "pattern": "materials/grass", "palette": "lawn", "_about": "the Second Court's lawn"},
           {"parts": ["plateau"], "surface": "floor", "within": [214.0, -4.0, 262.0, 68.0], "pattern": "materials/grass", "palette": "lawn", "_about": "the Third Court's"},
           {"parts": ["first court road", "court path felicity", "court path divan", "court path kitchens"], "pattern": "floors/flagstones", "palette": "marble-grey", "_about": "the paved ways"},
           {"parts": ["marble terrace", "irene yard", "pool rim", "pool fountain", "library basement"] + [n for n in parts if n.startswith("terrace parapet")],
            "pattern": "stone/marble", "palette": "carrara", "_about": "the marble terrace, the pool, the library's basement"},
           {"parts": ["plateau", "plateau east", "plateau north", "first court", "mint yard"] + [f"lower garden {i + 1}" for i in range(len(LOW))], "surface": "wall", "pattern": "stone/ashlar", "palette": "limestone",
            "_about": "the terrace walls over the slopes"},
           {"parts": "platform", "pattern": "floors/flagstones", "palette": "marble-grey"},
           {"surface": "floor", "pattern": "floors/flagstones", "palette": "marble-grey"},
           {"surface": "wall", "side": "in", "pattern": "stone/plaster", "palette": "plaster-white"},
           {"parts": ["gate towers", "tower of justice", "gate wall", "gate crenellation", "imperial gate", "imperial gate niche"] + [n for n in parts if n.startswith("sur-i sultani")],
            "surface": "wall", "pattern": "stone/ashlar", "palette": "limestone"},
           {"surface": "wall", "pattern": "stone/ashlar fine", "palette": "sandstone-grey", "_about": "the ranges' walls: a darker stone than the marble arcades before them"}]}

DOORS = {"name": "Topkapı Palace: doors", "building": "topkapi",
         "_about": "Topkapı: the Gate of Salutation's iron-clad leaves (1524) and its hall's, the Imperial Gate's, the Divan's and the treasury's doors, the kitchens' "
                   "gates and doors, the Gate of Felicity, the Audience Chamber's and the kiosks' doors, the porticoes' -- walnut and iron, Ottoman panelled.",
         "doors": [
             {"_about": "the Middle Gate's outer leaves", "part": "gate wall", "style": "ottoman", "fill": "#d6d0c2"},
             {"_about": "its hall's inner pair, into the court", "part": "gate hall", "style": "ottoman"},
             {"_about": "the Imperial Gate", "part": "imperial gate", "style": "ottoman", "fill": "#d6d0c2"},
             {"_about": "the gate in the north-west portico's back wall", "part": "nw portico/back wall door", "style": "ottoman"},
             {"_about": "into the Divan", "part": "divan/front wall door", "style": "ottoman"},
             {"_about": "into the Outer Treasury", "part": "treasury/front wall door", "style": "ottoman"},
             {"_about": "the kitchens' three gates, from the portico and to the street", "part": "kitchen range", "style": "ottoman"},
             {"_about": "a door into every kitchen from the street", "part": "kitchens/front wall doors", "style": "ottoman"},
             {"_about": "into the confectionery", "part": "confectionery/front wall door", "style": "ottoman"},
             {"_about": "the Gate of Felicity, both faces of the range", "part": "felicity range", "style": "ottoman"},
             {"_about": "the Audience Chamber's two doors", "part": "audience chamber/room", "style": "ottoman"},
             {"_about": "the Baghdad Kiosk's", "part": "baghdad kiosk/room", "style": "ottoman"},
             {"_about": "the Revan Kiosk's", "part": "revan kiosk/room", "style": "ottoman"},
             {"_about": "the Circumcision Room's", "part": "circumcision room/room", "style": "ottoman"}]}

if __name__ == "__main__":
    write_components()
    open(os.path.join(ROOT, "assets/architecture/topkapi.json"), "w").write(json.dumps(doc, indent=1) + "\n")
    open(os.path.join(ROOT, "assets/finishes/topkapi.json"), "w").write(json.dumps(fin, indent=1) + "\n")
    open(os.path.join(ROOT, "assets/doors/topkapi.json"), "w").write(json.dumps(DOORS, indent=1) + "\n")
    xs = [p[0] for p in PAL + RAMP]; zs = [p[1] for p in PAL + RAMP]
    print("topkapi:", len(parts), "parts,", len(TREES) + len(CYPRESS), "trees; plan x %.0f..%.0f z %.0f..%.0f" % (min(xs), max(xs), min(zs), max(zs)))
