# MILAN CATHEDRAL (Duomo di Milano, 1386-1965; the fabric and its forest of spires): five aisles stepping down --
# the nave over two aisles each side, every bay rib-vaulted -- two tiers of flying buttresses and pinnacles down both
# flanks, the five-portal facade, the transept as high as the nave, the polygonal apse, the tiburio and its spire with the
# Madonnina; spiral turrets up to the aisles' flat roofs, which are walked on (a flight between the two terraces).
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = {}; build = []
def add(n, d): parts[n] = d; build.append(n)
P = {"detail": 4, "bays": 10, "bayLen": 9.5, "naveW": 16.4, "aisleW": 9.6, "pierT": 2.8, "aisleT": 2.0,
     "naveL": "bays * bayLen", "spring": 13.0, "arcadeH": 27.0, "clearH": 32.0, "aisleRise": 3.5,
     "crown": "spring + (bayLen - pierT) / 2 * 1.7321", "aisleTop": "crown + aisleRise + 0.6", "naveTop": "clearH + naveW / 2 * 1.7321 + 1.2",
     "innerX": "naveW / 2 + pierT + aisleW", "outerX": "innerX + aisleT + aisleW", "wallX": "outerX + aisleT",
     "outerSpring": 11.0, "outerTop": "outerSpring + aisleW / 2 * 1.7321 + 0.8", "outerWallH": "outerTop + 1.2",
     "innerWallH": "aisleTop + 1.8", "crossZ": "0 - naveL / 2 + 2 * bayLen", "facadeH": 50.0, "facadeEave": 30.0, "facadePitch": "facadeH - facadeEave",
     "_innerX": "the inner aisles' outer edge: the arcade between the two aisles on each side stands there",
     "_crossZ": "the crossing, two bays from the east end of the nave"}
# THE NAVE, ITS AISLES AND THE TRANSEPT ACROSS THEM (2026-10-27: were the `basilica` component's arcade, clerestory and
# vaults, with a low transept arm off each outer aisle -- the crossing vaulted like any other bay and the tiburio shut
# off over it. Now the transept crosses the whole body at the nave's height in the two bays either side of crossZ, the
# aisles passing through its walls, and the crossing opens up into the tiburio's dome.)
BAYS, BAY = P["bays"], P["bayLen"]; NAVE_L = BAYS * BAY
CROSS_BAYS = (1, 2)                           # (the bays either side of crossZ, counted from the east end: the transept's)
NAVE_BAYS = [i for i in range(BAYS) if i not in CROSS_BAYS]
zc = lambda i: -NAVE_L / 2 + (i + .5) * BAY   # (bay i's middle)
HALF_B = P["naveW"] / 2 + P["pierT"]          # the nave walls' outer faces
INNER_X = HALF_B + P["aisleW"]
WALL_X = INNER_X + 2 * P["aisleT"] + P["aisleW"]
CROSS_Z = -NAVE_L / 2 + 2 * BAY
TZ0, TZ1 = CROSS_Z - BAY - 1, CROSS_Z + BAY + 1   # the transept walls' outer faces: 2m walls on the bay lines either side of it
TR_IN = TZ1 - TZ0 - 4                             # (17m between them)
ARM_X = WALL_X + 14                               # an arm's end wall, its outer face
POINTED = {"profile": "pointed", "spread": 1}
FLANK_WINDOW = {"width": 3.4, "sill": 4.0, "springing": 13.0, "head": {"profile": "pointed", "spread": 1.2}, "tracery": True}
def flank(name, x, z0, z1, tiers, y=0, **wall):
    # a stretch z0..z1 of a wall down both flanks on the line x: turned a quarter, as a flank's walls are (so it reaches
    # inward from its line), its openings given by their z -- `at` is from the wall's middle, along -z on the right
    # and +z on the left
    m = (z0 + z1) / 2
    for sx, nm in ((1, "right"), (-1, "left")):
        tt = [{**t, "openings": [{**{k: v for k, v in o.items() if k != "z"}, "at": round(-sx * (o["z"] - m), 4)} for o in t["openings"]]} for t in tiers]
        add(f"{name} {nm}", {"type": "wall", "width": round(z1 - z0, 4), **wall, "tiers": tt, "at": [[f"{sx} * ({x})", y, round(m, 4), f"{sx} * 1.5707963"]]})
# the nave's walls: the arcade into the inner aisles, broken off at the crossing (the transept opens there to the
# floor), and the clerestory over it, its window in every bay, and over the crossing the arch into the transept arm
ARCH = {"width": "bayLen - pierT", "sill": 0, "springing": "spring", "head": POINTED}
flank("nave arcade east", "naveW / 2 + pierT", -NAVE_L / 2, TZ0 + 2, [{"openings": [{"z": zc(0), **ARCH}]}], height="arcadeH", thickness="pierT")
flank("nave arcade west", "naveW / 2 + pierT", TZ1 - 2, NAVE_L / 2, [{"openings": [{"z": zc(i), **ARCH} for i in NAVE_BAYS if i > 2]}],
      height="arcadeH", thickness="pierT")
flank("clerestory", "naveW / 2 + pierT", -NAVE_L / 2, NAVE_L / 2,
      [{"openings": [{"z": zc(i), "width": 3.0, "sill": 0.5, "springing": 8.0, "head": POINTED, "tracery": 2} for i in NAVE_BAYS] +
                    [{"z": CROSS_Z, "width": TR_IN, "sill": 0, "springing": "clearH - arcadeH", "head": POINTED, "glass": False}]}],
      y="arcadeH", height="naveTop - arcadeH", thickness="pierT")
add("nave vaults", {"type": "groin", "width": "naveW", "length": "bayLen", "springing": "clearH", "top": "naveTop", "clears": "crown",
                    "across": POINTED, "along": {"profile": "pointed", "spread": "((naveW / bayLen) * (naveW / bayLen) * 3 - 1) / 2"},
                    "at": [[0, 0, round(zc(i), 4), 0] for i in NAVE_BAYS],
                    "_about": "the nave's vault, bay by bay, but for the crossing's two"})
add("nave ribs", {"type": "ribs", "on": "nave vaults", "width": 0.45, "depth": 0.3, "wall": {"width": 0.6, "depth": 0.35}})
add("inner vaults", {"type": "groin", "width": "aisleW", "length": "bayLen", "springing": "crown", "top": "aisleTop", "clears": "crown",
                     "across": {"profile": "segmental", "rise": "aisleRise"}, "along": {"profile": "segmental", "rise": "aisleRise"},
                     "at": [[f"{sx} * (naveW / 2 + pierT + aisleW / 2)", 0, round(zc(i), 4), 0] for sx in (1, -1) for i in NAVE_BAYS]})
add("inner ribs", {"type": "ribs", "on": "inner vaults", "width": 0.35, "depth": 0.25, "wall": {"width": 0.45, "depth": 0.3}})
# the arcade between the inner and outer aisles and the outer walls, each in two stretches either side of the transept
# (the stretches' end bays' arches drawn in a little, to leave a pier against the transept's walls)
AISLE_ARCH = {"sill": 0, "springing": "outerSpring - 1", "head": POINTED}
flank("aisle arcade east", "innerX + aisleT", -NAVE_L / 2, TZ0, [{"openings": [{"z": zc(0) - 0.5, "width": 6.5, **AISLE_ARCH}]}],
      height="innerWallH", thickness="aisleT")
flank("aisle arcade west", "innerX + aisleT", TZ1, NAVE_L / 2,
      [{"openings": [{"z": zc(i) + (0.5 if i == 3 else 0), "width": 6.5 if i == 3 else "bayLen - aisleT", **AISLE_ARCH} for i in range(3, BAYS)]}],
      height="innerWallH", thickness="aisleT")
flank("outer wall east", "wallX", -NAVE_L / 2, TZ0, [{"openings": [{"z": zc(0), **FLANK_WINDOW}]}], height="outerWallH", thickness="aisleT")
# (the westernmost bay's window narrower and west of the stair turret, between it and the facade)
flank("outer wall west", "wallX", TZ1, NAVE_L / 2, [{"openings": [{"z": zc(i), **FLANK_WINDOW} for i in range(3, BAYS - 1)]
                                                    + [{"z": NAVE_L / 2 - 2.4, **FLANK_WINDOW, "width": 2.3}]}], height="outerWallH", thickness="aisleT")
add("outer vaults", {"type": "groin", "width": "aisleW", "length": "bayLen", "springing": "outerSpring", "top": "outerTop",
                     "across": POINTED, "along": {"profile": "pointed", "spread": "((aisleW / bayLen) * (aisleW / bayLen) * 3 - 1) / 2"},
                     "at": [[f"{sx} * (innerX + aisleT + aisleW / 2)", 0, round(zc(i), 4), 0] for sx in (1, -1) for i in NAVE_BAYS if i < BAYS - 1],
                     "_about": "the outer aisles' vaults, all but the transept's bays and the westernmost: that one is the stair turret's, under a flat terrace"})
add("outer ribs", {"type": "ribs", "on": "outer vaults", "width": 0.35, "depth": 0.25, "wall": {"width": 0.45, "depth": 0.3}})
# THE ROOFS ARE WALKED: the nave's a gable (broken off round the tiburio), but the aisles' two flat marble TERRACES
# stepping down either side -- the outer one at the outer wall's head (the turret comes up onto it, its west bay the
# turret's own terrace), the inner one at the inner arcade's, a short flight up between them; a parapet along every
# edge that drops. (East of the transept, over the first bay, they are roofs only: the transept stands between.)
add("nave roof", {"type": "roof", "form": "gable", "width": "naveW + 2 * pierT + 0.4", "length": round(NAVE_L / 2 - TZ1, 4), "pitch": 22,
                  "at": [[0, "naveTop", round((TZ1 + NAVE_L / 2) / 2, 4), 0]]})
add("nave roof east", {"type": "roof", "form": "gable", "width": "naveW + 2 * pierT + 0.4", "length": round(TZ0 + NAVE_L / 2, 4), "pitch": 22,
                       "at": [[0, "naveTop", round((TZ0 - NAVE_L / 2) / 2, 4), 0]]})
for nm, (z0, z1), walked in (("", (TZ1, NAVE_L / 2), True), (" east", (-NAVE_L / 2, TZ0), False)):
    add(f"inner aisle terraces{nm}", {**({"walked": True} if walked else {}), "type": "box", "width": "aisleW", "length": round(z1 - z0, 4), "height": 0.4,
        "at": [[f"{sx} * (naveW / 2 + pierT + aisleW / 2)", "innerWallH - 0.4", round((z0 + z1) / 2, 4), 0] for sx in (-1, 1)],
        **({"_about": "the inner aisles' roofs: flat, level with the inner arcade's head, against the clerestory"} if walked else {})})
for nm, (z0, z1), walked in (("", (TZ1, NAVE_L / 2 - BAY), True), (" east", (-NAVE_L / 2, TZ0), False)):
    add(f"outer aisle terraces{nm}", {**({"walked": True} if walked else {}), "type": "box", "width": "aisleW", "length": round(z1 - z0, 4), "height": 0.4,
        "at": [[f"{sx} * (innerX + aisleT + aisleW / 2)", "outerWallH - 0.4", round((z0 + z1) / 2, 4), 0] for sx in (-1, 1)],
        **({"_about": "the outer aisles' roofs, level with the outer wall's head (the west bay is the turret's terrace)"} if walked else {})})
for nm, (z0, z1) in (("", (TZ1, NAVE_L / 2)), (" east", (-NAVE_L / 2, TZ0))):
    add(f"outer parapets{nm}", {"type": "box", "width": 0.5, "length": round(z1 - z0, 4), "height": 1.1,
        "at": [[f"{sx} * (wallX - aisleT + 0.25)", "outerWallH", round((z0 + z1) / 2, 4), 0] for sx in (-1, 1)],
        **({"_about": "along the outer wall's head, the terrace's edge over the street"} if not nm else {})})
# the flight from the outer terrace up to the inner one, against the inner arcade in the bay east of the turret's,
# rising east; its landing level with the arcade's head, which is the way across onto the inner terrace (the parapet
# along that head left open there)
FL_N, FL_RUN, FL_W, FL_Z = 19, 0.28, 1.4, NAVE_L / 2 - BAY - 0.5
FL_END = FL_Z - FL_N * FL_RUN - FL_W                     # (the landing's east edge: the flight's run and its landing, as wide as it)
add("terrace flight", {"type": "flight", "width": FL_W, "run": FL_RUN, "base": "outerWallH", "top": "innerWallH", "steps": FL_N, "landing": FL_W,
                       "at": [[f"{sx} * (innerX + aisleT) + {FL_W if sx > 0 else 0}", 0, FL_Z, 1.5707963] for sx in (-1, 1)],
                       "_about": "up from the outer terrace to the inner, along the inner arcade's outer face"})
for k, (z0, z1) in enumerate(((-NAVE_L / 2, TZ0), (TZ1, FL_END), (FL_END + FL_W, NAVE_L / 2))):
    add(f"arcade parapets {k + 1}", {"type": "box", "width": 0.5, "length": round(z1 - z0, 4), "height": 1.1,
        "at": [[f"{sx} * (innerX + aisleT - 0.25)", "innerWallH", round((z0 + z1) / 2, 4), 0] for sx in (-1, 1)],
        **({"_about": "along the inner arcade's head, over the drop to the outer terrace: open where the flight arrives"} if k == 0 else {})})
# BUTTRESSES AND PINNACLES down both flanks, on every bay line but the transept's (its walls are its buttresses): a
# flying buttress from a pier outside the outer wall over the outer terrace to the inner arcade -- springing high
# enough off its pier to be walked under along the terrace, as Milan's are -- and a second tier from a pier on the
# inner arcade over the inner terrace to the clerestory, where the nave vault pushes out; each pier with its pinnacle
FLANK_LINES = [k for k in range(BAYS) if k not in (1, 2, 3)]
fb = {"pierH": "outerWallH + 3.8", "pierD": 2.4, "span": "wallX + 1.2 - innerX - aisleT", "low": "outerWallH + 1.6", "high": "innerWallH - 0.3",
      "top0": "outerWallH + 3.2", "top1": "innerWallH + 1.4", "pin": 1.5, "pinH": 5.0, "pinS": 7.0}
add("flank buttresses", {"type": "component", "use": "components/flying-buttress", "params": fb,
                         "at": [[f"{sx} * (wallX + 1.2)", 0, round(-NAVE_L / 2 + k * BAY, 4), 3.14159265 if sx > 0 else 0]
                                for sx in (1, -1) for k in FLANK_LINES]})
up = {"pierH": 8.0, "pierD": "aisleT", "pierW": 1.6, "span": "innerX - naveW / 2 - pierT", "low": 6.3, "high": 10.3, "top0": 7.4, "top1": 12.5,
      "pin": 1.2, "pinH": 4.0, "pinS": 6.0}
add("clerestory flyers", {"type": "component", "use": "components/flying-buttress", "params": up,
                          "at": [[f"{sx} * innerX", "innerWallH", round(-NAVE_L / 2 + k * BAY, 4), 3.14159265 if sx > 0 else 0]
                                 for sx in (1, -1) for k in FLANK_LINES],
                          "_about": "the upper flyers: their piers on the inner arcade, over the inner terrace to the clerestory"})
add("clerestory pinnacles", {"type": "component", "use": "components/pinnacle", "params": {"w": 1.0, "h": 3.0, "s": 5.0},
                             "at": [[f"{sx} * (naveW / 2 + pierT)", "naveTop", round(-NAVE_L / 2 + k * BAY, 4), 0] for sx in (1, -1) for k in FLANK_LINES]})
# the facade: five portals, five great windows, a gable zone; six buttresses with their pinnacles
bx = ["0 - wallX + 1", "0 - innerX - aisleT / 2", "0 - naveW / 2 - pierT / 2", "naveW / 2 + pierT / 2", "innerX + aisleT / 2", "wallX - 1"]
mid = ["0 - (innerX + aisleT + aisleW / 2)", "0 - (naveW / 2 + pierT + aisleW / 2)", "0", "naveW / 2 + pierT + aisleW / 2", "innerX + aisleT + aisleW / 2"]
# (the upper windows each as high as its bay inside allows: the nave's tall; an inner aisle's under its vault's crown
#  and the inner terrace over it; an outer aisle's under its vault -- or, in the turret's bay, under the terrace)
UPPER = [{"width": 2.4, "sill": 0.5, "springing": 2.0}, {"width": 3.0, "sill": 0.5, "springing": 3.5}, {"width": 4.0, "sill": 1.5, "springing": 9.0},
         {"width": 3.0, "sill": 0.5, "springing": 3.5}, {"width": 2.4, "sill": 0.5, "springing": 2.0}]
# THE FACADE IS ONE GABLE: a wall to `facadeEave` across the whole width, and on it a single triangle of stone up
# to `facadeH` at the middle -- no square shoulders. The buttresses climb with its slope, the outer ones lowest,
# each carrying its pinnacle at the gable's edge.
add("facade", {"type": "wall", "width": "2 * wallX", "height": "facadeEave", "thickness": 2.4, "at": [[0, 0, "naveL / 2 + 2.4", 0]],
               "tiers": [{"h": 15, "openings": [{"at": m, "width": 6.0 if m == "0" else 4.2, "sill": 0, "springing": 9.0 if m == "0" else 7.5,
                                                "head": {"profile": "pointed", "spread": 1}} for m in mid]},
                         {"openings": [{"at": m, **UPPER[k], "head": {"profile": "pointed", "spread": 1.4}, "tracery": True} for k, m in enumerate(mid)]}],
               "_about": "the facade below the gable, in two tiers: five portals, and five great pointed windows over them"})
add("facade gable", {"type": "roof", "form": "gable", "width": "2 * wallX", "length": 2.4, "pitch": 30.32, "at": [[0, "facadeEave", "naveL / 2 + 1.2", 0]],
                     "_about": "the gable: one triangle across the whole front, its apex over the nave (pitch: facadeH - facadeEave over wallX)"})
slope = "(facadePitch) / wallX"
heights = {x: f"facadeEave + (wallX - {ax}) * {slope} + 2" for x, ax in zip(bx, ["(wallX - 1)", "(innerX + aisleT / 2)", "(naveW / 2 + pierT / 2)",
                                                                                  "(naveW / 2 + pierT / 2)", "(innerX + aisleT / 2)", "(wallX - 1)"])}
add("facade buttresses", {"type": "box", "width": 2.2, "length": 3.2, "height": "facadeEave", "at": [[x, 0, "naveL / 2 + 3.6", 0] for x in bx]})
for k, x in enumerate(bx):
    add(f"facade buttress {k + 1}", {"type": "box", "width": 2.2, "length": 3.2, "height": f"{heights[x]} - facadeEave",
                                      "at": [[x, "facadeEave", "naveL / 2 + 3.6", 0]],
                                      **({"_about": "each buttress on up with the gable's slope: the outer ones lowest, the two by the nave highest"} if k == 0 else {})})
add("facade pinnacles", {"type": "component", "use": "components/pinnacle", "params": {"w": 2.0, "h": 6.0, "s": 10.0},
                         "at": [[x, heights[x], "naveL / 2 + 3.6", 0] for x in bx]})
# THE TRANSEPT: an arm each side as high as the nave, from the clerestory out past the outer wall -- its walls on the
# bay lines either side of the crossing's two bays, the aisles running on through them by an arch each, its windows
# over the aisles' roofs; a portal and a great window in each end; four rib vaults down each arm, as high as the nave's
TR_BAY = (ARM_X - 2 - HALF_B) / 4
TR_BAYS = [HALF_B + (j + .5) * TR_BAY for j in range(4)]
tc = (HALF_B + ARM_X) / 2
SIDE = [{"h": 24.0, "openings": [{"x": INNER_X - P["aisleW"] / 2, "width": 7.0, "sill": 0, "springing": 13.0, "head": POINTED, "glass": False},
                                 {"x": INNER_X + P["aisleT"] + P["aisleW"] / 2, "width": 7.0, "sill": 0, "springing": 10.0, "head": POINTED, "glass": False},
                                 {"x": ARM_X - 7, **FLANK_WINDOW}]},
        {"openings": [{"x": x, "width": 2.6, "sill": 3.0, "springing": 14.0, "head": POINTED, "tracery": True} for x in TR_BAYS]}]
for sx, nm in ((1, "right"), (-1, "left")):
    add(f"transept walls {nm}", {"type": "wall", "width": round(ARM_X - HALF_B, 4), "height": "naveTop", "thickness": 2.0,
        "tiers": [{**t, "openings": [{**{k: v for k, v in o.items() if k != "x"}, "at": round(sx * (o["x"] - tc), 4)} for o in t["openings"]]} for t in SIDE],
        "at": [[round(sx * tc, 4), 0, TZ0 + 2, 0], [round(sx * tc, 4), 0, TZ1, 0]],
        **({"_about": "the arm's two side walls (on the bay lines: a wall's thickness is behind its line), an arch through each for each aisle"} if sx > 0 else {})})
    add(f"transept end {nm}", {"type": "wall", "width": TZ1 - TZ0, "height": "naveTop", "thickness": 2.0,
        "tiers": [{"h": 12.0, "openings": [{"at": 0, "width": 5.0, "sill": 0, "springing": 7.0, "head": POINTED}]},
                  {"openings": [{"at": 0, "width": 5.0, "sill": 3.0, "springing": 22.0, "head": {"profile": "pointed", "spread": 1.2}, "tracery": True}]}],
        "at": [[round(sx * ARM_X, 4), 0, CROSS_Z, round(sx * 1.5707963, 7)]]})
add("transept vaults", {"type": "groin", "width": round(TR_BAY, 4), "length": TR_IN, "springing": "clearH", "top": "naveTop",
                        "across": {"profile": "pointed", "spread": round(((TR_IN / TR_BAY) ** 2 * 3 - 1) / 2, 4)}, "along": POINTED,
                        "at": [[round(sx * x, 4), 0, CROSS_Z, 0] for sx in (1, -1) for x in TR_BAYS],
                        "_about": "four bays down each arm, their crowns the nave's"})
add("transept ribs", {"type": "ribs", "on": "transept vaults", "width": 0.45, "depth": 0.3, "wall": {"width": 0.6, "depth": 0.35}})
# THE ARMS BUTTRESSED: they stand 14m out past the outer aisles, the nave's height, carrying its vaults -- a buttress
# on each side wall at the bay line between the last two windows and at the end, and two on each end wall either side
# of the portal, each one carrying a pinnacle clear of the eaves: the forest of spires carried round the arms
TB_H = "naveTop - 1"
tb_side = [[round(sx * x, 4), 0, z, 0] for sx in (1, -1) for x in (TR_BAYS[2] + TR_BAY / 2, ARM_X - 1.2) for z in (TZ0 - 1.0, TZ1 + 1.0)]
tb_end = [[round(sx * (ARM_X + 1.5), 4), 0, round(CROSS_Z + dz, 4), 0] for sx in (1, -1) for dz in (-6.0, 6.0)]
add("transept buttresses", {"type": "box", "width": 2.4, "length": 3.0, "height": TB_H, "at": tb_side,
                            "_about": "the arms' side-wall buttresses, half a metre into the wall"})
add("transept end buttresses", {"type": "box", "width": 4.0, "length": 2.4, "height": TB_H, "at": tb_end})
add("transept pinnacles", {"type": "component", "use": "components/pinnacle", "params": {"w": 1.5, "h": 5.0, "s": 7.0},
                           "at": [[x, TB_H, round(z + (-0.3 if z < CROSS_Z else 0.3), 4), 0] for x, _, z, _ in tb_side]
                               + [[round(x + (0.4 if x > 0 else -0.4), 4), TB_H, z, 0] for x, _, z, _ in tb_end]})
TR_ROOF = ARM_X + 0.2 - HALF_B
add("transept roofs", {"type": "roof", "form": "gable", "width": TZ1 - TZ0 + 0.4, "length": round(TR_ROOF, 4), "pitch": 22,
                       "at": [[round(sx * (HALF_B + TR_ROOF / 2), 4), "naveTop", CROSS_Z, 1.5707963] for sx in (1, -1)]})
# the apse: a polygonal chevet (half an octagon) round the ambulatory, the choir's inner half ring, its vault and roofs
apse = [[0, 0, "0 - naveL / 2", 0]]
add("chevet", {"type": "ring", "count": 8, "turn": 0.5, "at": [2, 3, 4, 5], "rOuter": "wallX", "rInner": "wallX - aisleT", "height": "outerWallH",
               "opening": {"width": 4.0, "sill": 4.0, "springing": 12.0, "head": {"profile": "pointed", "spread": 1.2}, "tracery": True}, "place": apse,
               "_about": "(its windows' crowns under the outer ambulatory's vault, which springs at 16m)"})
# the chevet's BUTTRESSES, one on each corner between its bays -- as down the flanks, each carrying a pinnacle (the
# corners at the flanks' ends are the flank's own last buttresses')
CHEVET_R = P["naveW"] / 2 + P["pierT"] + 2 * P["aisleW"] + 2 * P["aisleT"] + 1.3
chev = [[round(CHEVET_R * math.sin(t), 4), 0, round(-NAVE_L / 2 + CHEVET_R * math.cos(t), 4), round(t, 6)] for t in (3 * math.pi / 4, math.pi, 5 * math.pi / 4)]
add("chevet buttresses", {"type": "box", "width": 2.4, "length": 3.0, "height": "outerWallH + 3.8", "at": chev,
                          "_about": "a buttress on each of the chevet's corners, 1.5m into its wall and 1.5m out"})
add("chevet pinnacles", {"type": "component", "use": "components/pinnacle", "params": {"w": 1.5, "h": 5.0, "s": 7.0},
                         "at": [[x, "outerWallH + 3.8", z, t] for x, _, z, t in chev]})
# THE CHOIR opens to the ambulatory as the nave does to its aisles: an ARCADE round the half ring below the arcade's
# height, the clerestory over it; and the aisles go on round it -- the arcade between them turns with them, and both
# ambulatories are vaulted round the apse's centre, each at its own aisle's height, so the aisles' vaults run on
add("choir arcade", {"type": "ring", "count": 8, "turn": 0.5, "at": [2, 3, 4, 5], "rOuter": "naveW / 2 + pierT", "rInner": "naveW / 2", "height": "arcadeH",
                     "opening": {"width": 6.0, "sill": 0, "springing": "spring", "head": {"profile": "pointed", "spread": 1}}, "place": apse,
                     "_about": "the choir's piers and their arches into the inner ambulatory: the nave arcade's springing and pointed head"})
add("choir", {"type": "ring", "count": 8, "turn": 0.5, "at": [2, 3, 4, 5], "rOuter": "naveW / 2 + pierT", "rInner": "naveW / 2", "y": "arcadeH", "height": "naveTop - arcadeH",
              "opening": {"width": 3.2, "sill": 1, "springing": "clearH + 5 - arcadeH", "head": {"profile": "pointed", "spread": 1}, "tracery": True}, "place": apse,
              "_about": "the choir's clerestory, over its arcade"})
add("ambulatory arcade", {"type": "ring", "count": 16, "turn": 0.5, "at": list(range(4, 12)), "rOuter": "innerX + aisleT", "rInner": "innerX", "height": "aisleTop",
                          "opening": {"width": 6.6, "sill": 0, "springing": "outerSpring - 1", "head": {"profile": "pointed", "spread": 1}}, "place": apse,
                          "_about": "the arcade between the inner and outer aisles, turned round the apse: half a ring of sixteen"})
add("inner ambulatory vault", {"type": "vault", "count": 16, "turn": 0.5, "at": list(range(4, 12)), "rInner": "naveW / 2 + pierT", "rOuter": "innerX",
                               "springing": "crown", "top": "aisleTop", "clears": "spring + 3 * 1.7321", "head": {"profile": "segmental", "rise": "aisleRise"}, "place": apse,
                               "_about": "the inner aisles' vault carried round: their springing, rise and top"})
add("outer ambulatory vault", {"type": "vault", "count": 16, "turn": 0.5, "at": list(range(4, 12)), "rInner": "innerX + aisleT", "rOuter": "wallX - aisleT",
                               "springing": 16.0, "top": "outerTop", "clears": "outerSpring - 1 + 3.3 * 1.7321", "head": {"profile": "segmental", "rise": 3.0}, "place": apse,
                               "_about": "the outer ambulatory's: springing over the arcade's crowns, to the outer aisles' top"})
# (the CHOIR VAULT springs over its windows' heads, at 40.5m -- sprung at the nave's springing it buried them, the
#  half dome's shell standing across their upper lights -- and rises a shallow segment, under the choir's roof; over
#  the arch between it and the nave a DIAPHRAGM closes the nave's attic off from the choir)
CHOIR_SPRING = 40.5
add("choir vault", {"type": "dome", "sweep": 0.5, "sides": 8, "radius": "naveW / 2 + pierT", "thickness": "pierT", "head": {"profile": "segmental", "rise": 5.5},
                    "at": [[0, CHOIR_SPRING, "0 - naveL / 2", 3.14159265]]})
add("choir diaphragm", {"type": "wall", "width": "naveW + 2 * pierT", "height": f"naveTop - clearH", "thickness": 2.0, "glass": False,
                        "openings": [{"at": "naveW / 2 + pierT", "width": "naveW", "sill": 0, "springing": 0, "head": POINTED}],
                        "at": [[0, "clearH", "0 - naveL / 2", 0]],
                        "_about": "the wall over the choir's arch, from the nave vault's springing to the roof: the nave's last cell ends against it"})
add("choir roof", {"type": "dome", "sweep": 0.5, "sides": 8, "radius": "naveW / 2 + pierT + 0.3", "thickness": 0, "head": {"profile": "trigonal", "rise": 4.5},
                   "at": [[0, "naveTop", "0 - naveL / 2", 3.14159265]]})
add("ambulatory roof", {"type": "dome", "sweep": 0.5, "sides": 8, "radius": "wallX + 0.3", "thickness": 0, "head": {"profile": "trigonal", "rise": 6},
                        "oculus": "naveW / 2 + pierT", "cap": False,
                        "at": [[0, "outerWallH", "0 - naveL / 2", 3.14159265]],
                        "_about": "the lean-to round the choir: a half cone cut off at the choir's wall (`oculus`) and left open there"})
# THE CROSSING carries the tiburio: its octagon stands on the clerestory walls either side, and across the nave on a
# DIAPHRAGM at each end of the crossing -- a wall over the transverse arch, pierced by the arch itself, from the vault's
# springing up to the roof's foot, as the four great arches of a crossing are -- and over the four corners between them
# on SQUINCHES, a triangle of masonry across each corner under the octagon's diagonal face. Inside, the crossing is open
# up into the tiburio: its octagonal DOME springs from the octagon's foot.
TIB = 10.25                                   # (its octagon's outer faces: over the clerestory walls, and over the diaphragms)
add("crossing diaphragms", {"type": "wall", "width": "naveW + 2 * pierT", "height": "naveTop - clearH", "thickness": 2.0, "glass": False,
                            "openings": [{"at": "naveW / 2 + pierT", "width": "naveW", "sill": 0, "springing": 0, "head": POINTED}],
                            "at": [[0, "clearH", TZ0 + 2, 0], [0, "clearH", TZ1, 0]],
                            "_about": "the walls over the crossing's two end arches, on which the tiburio's end faces stand"})
ap = (TIB - 1.0) * math.sqrt(2)               # (the octagon's inner diagonal faces: x + z = ap from the crossing's middle)
hx, hz = P["naveW"] / 2, TR_IN / 2
for n, (sx, sz) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
    tri = [[round(sx * x, 4), round(CROSS_Z + sz * z, 4)] for x, z in ((hx, hz), (hx, ap - hx), (ap - hz, hz))]
    add(f"crossing squinch {n + 1}", {"type": "prism", "plan": {"points": tri if sx * sz > 0 else tri[::-1]}, "height": "naveTop - 42", "at": [[0, 42.0, 0, 0]],
        **({"_about": "the squinches: a triangle across each of the crossing's corners, carrying the tiburio's diagonal faces"} if n == 0 else {})})
add("crossing dome", {"type": "dome", "sides": 8, "radius": round(TIB / math.cos(math.pi / 8) - 0.5, 3), "thickness": 0.6,
                      "head": {"profile": "pointed", "spread": 0.6}, "at": [[0, "naveTop", CROSS_Z, 0]],
                      "_about": "the crossing's own dome inside the tiburio, struck from the octagon's foot"})
# the tiburio over the crossing, its spire, the Madonnina
add("tiburio", {"type": "component", "use": "components/domed-tower",
                "params": {"sides": 8, "R": round(TIB / math.cos(math.pi / 8), 3), "H": 16, "t": 1.0, "cap": "trigonal", "capRise": 28, "capR": 4.2, "drumR": 3.6, "drumH": 6,
                           "kok": 1.5, "finial": 4.2, "winW": 1.8},
                "build": ["tower", "kokoshniki", "neck", "drum", "cap", "finial"], "at": [[0, "naveTop", "crossZ", 0]],
                "_about": "the tiburio: the octagonal lantern over the crossing, its spire and the Madonnina at the top -- the domed-tower component, gabled, with a tall tent"})
# spiral turrets up to the roofs, in the westernmost bay of each outer aisle: the stair climbs from the aisle floor to
# a flat terrace over that bay, round the turret, and out through a door in the turret's head onto it; from there the aisle roofs are walked.
# The turret stands at the bay's EAST end against the outer wall, clear of the side portal and its window, the bay
# behind the portal a vestibule
tR = 2.4
a, h8 = round(tR * 0.92388, 4), round(tR * 0.38268, 4)            # the octagon's apothem, and half a face
off = round(a + 0.8, 4)                                          # (clear of the bay line's wall rib, and its flyer over the head)
tz = f"naveL / 2 - bayLen + {off}"
for sx, nm in ((1, "right"), (-1, "left")):
    tx = f"{sx} * (wallX - aisleT - {a})"                            # (its outer face against the outer wall)
    # the turret, its door (bay 4 of 8: -z, into the aisle -- the turret stands at the component's middle, so say it) and the
    # spiral from the door up through its open head onto the terrace -- `tower-stair`, less the floor it would lay
    add(f"stair {nm}", {"type": "component", "use": "components/tower-stair", "params": {"W": 6.0, "H": "outerWallH", "tR": tR, "tx": 0, "tz": 0, "doorBay": 4, "hand": "right" if sx > 0 else "left"},
                        "build": ["turret", "turret door", "stair"], "at": [[tx, 0, tz, 0]]})
    # the terrace over the turret's bay: the bay less the turret's octagon (faces a = tR cos 22.5 from its middle), so
    # there is no crack round the stair's head -- slabs in the turret's own frame (u out toward the outer wall, v west):
    # inside it, west of it, the strips east of it and outside it, and the four corners of its square the octagon
    # leaves open
    u0, u1 = f"innerX + aisleT - (wallX - aisleT - {a})", a      # (the arcade, the outer wall)
    v0, v1 = -off, f"bayLen - {off}"                  # (the bay's east and west ends)
    def slab(u, v):   # a rectangle u x v, mirrored to the turret's side
        return [[f"{sx} * ({x})", z] for x, z in ((u[0], v[0]), (u[1], v[0]), (u[1], v[1]), (u[0], v[1]))]
    pieces = [slab((u0, -a), (v0, v1)), slab((-a, u1), (a, v1)), slab((-a, u1), (v0, -a))]
    pieces += [[[sx * su * a, sv * a], [sx * su * h8, sv * a], [sx * su * a, sv * h8]] for su in (1, -1) for sv in (1, -1)]
    for k, pts in enumerate(pieces):
        add(f"stair terrace {nm} {k + 1}", {"walked": True, "type": "prism", "plan": {"points": pts}, "height": 0.4,
            "at": [[tx, "outerWallH - 0.4", tz, 0]], **({"_about": "the flat roof over the turret's bay, round the turret's head"} if k == 0 else {})})
    # the turret's HEAD over the terrace: its octagon on up, a door in the bay the spiral arrives in (bay 0: west, onto
    # the terrace beside it -- the last tread ends some 20 degrees round from there, either hand), a stone lid and a
    # pinnacle on it
    head = {"type": "ring", "count": 8, "rOuter": tR, "rInner": tR - 0.4, "height": 3.0, "y": "outerWallH", "place": [[tx, 0, tz, 0]]}
    add(f"turret head {nm}", {**head, "skip": [0], "solid": True, **({"_about": "the stair turret's head over the terrace, the spiral arriving inside it"} if sx > 0 else {})})
    add(f"turret head door {nm}", {**head, "at": [0], "opening": {"width": 1.2, "sill": 0, "springing": 1.8, "head": {"profile": "pointed", "spread": 1}}})
    add(f"turret lid {nm}", {"type": "prism", "plan": {"sides": 8, "radius": tR + 0.05}, "height": 0.35, "at": [[tx, "outerWallH + 3.0", tz, 0]]})
    add(f"turret pinnacle {nm}", {"type": "component", "use": "components/pinnacle", "params": {"w": 1.5, "h": 4.0, "s": 6.0},
                                  "at": [[tx, "outerWallH + 3.35", tz, 0]]})
# ---- INSIDE (as notre_dame.py gothic): seating up to the crossing (crossZ), the altar east of it, the organ in the north transept
add("seating", {"type": "zone", "zone": "seating", "w": "naveW - 1.6", "d": "(naveL / 2 - bayLen - 1.5) - (crossZ + bayLen + 1.5)", "h": "arcadeH",
                "at": [[0, 0, "((crossZ + bayLen + 1.5) + (naveL / 2 - bayLen - 1.5)) / 2", 1.5707963]]})
add("altar", {"type": "zone", "zone": "altar", "w": "naveW - 2", "d": 3.2, "h": "arcadeH", "at": [[0, 0, "crossZ - bayLen - 2.5", 1.5707963]]})
add("organ", {"type": "zone", "zone": "organ", "w": 5, "d": 4.0, "h": 12, "at": [[round(-(ARM_X - 4.1), 3), 0, f"crossZ + {dz}", 0] for dz in (-5.5, 5.5)],
              "_about": "the organ in two cases, against the north transept arm's end wall either side of its portal (Milan has no west gallery: its organs face each other across the choir)"})
doc = {"name": "Milan Cathedral",
  "_about": "THE DUOMO OF MILAN, from components: the nave, and two aisles either side stepping down beside it, every bay rib-vaulted; down both flanks two tiers of `flying-buttress` at every bay, each pier with its pinnacle, and a `pinnacle` on the clerestory -- the forest of spires; the facade, a portal and a window over it in each of its five bays, under one gable, between six buttresses with their pinnacles; the transept, as high as the nave, crossing the whole body (the aisles run through its walls); the polygonal chevet round the choir with its half vault; the tiburio over the crossing with its spire and the Madonnina (the `domed-tower`), the crossing open up into its dome on four squinches. Spiral turrets in the westernmost bays climb to the outer aisles' flat terraces, a flight from there to the inner ones: the aisle roofs are walked on, under the flyers.",
  "params": P, "base": {"height": 1.2, "steps": 4, "stepOut": 0.8, "margin": 3}, "railing": {"type": "stone"}, "build": build, "parts": parts}
open(os.path.join(ROOT, "assets/architecture/milan.json"), "w").write(json.dumps(doc, indent=2) + "\n")
