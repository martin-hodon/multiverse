"""THE MODERN ARMS (2026-11-20; docs/modern.md): the firearms after the flintlock -- a revolver, a self-loading pistol,
a bolt-action rifle (a scope if asked), a pump shotgun, an assault rifle, a submachine gun, a light machine gun on its
bipod. Each is at its real size, in THE GUN'S FRAME: the bore along +x (the muzzle forward), y up (the sights on top),
z across (+z the right side, where the cases are thrown out), x = 0 at the trigger and y = 0 on the bore's line.

How they are drawn (the period musket and pistol, assets/items/weapons/, are a plate for the stock and a rod for the
barrel; these go further the same way):
  - what is seen from the side -- a frame, a receiver's lower half, a stock, a pistol grip, a magazine -- is a PLATE:
    its outline drawn in x, y and extruded across z at its real width (`side`);
  - what is round -- a barrel, a cylinder, a scope, a cocking tube, a flash hider -- is a LATHE laid along +x (`tube`,
    its profile [r, dx] from its back end);
  - the small things -- sights, levers, the bolt's handle, the guard's bow -- are boxes, rods and sweeps.

HOLDING THEM (docs/items.md "Holding it"): a HANDGUN is held as the flintlock pistol is -- the grip's centre, `axis`
up the grip's rake, `face` the muzzle; a LONG GUN as the musket is -- `axis` the muzzle, `face` the top, `grip2` the
other hand on the fore-end, carried upright at the shoulder and ordered on its butt (`rest: ground`)."""
import math
from kit import item, box, rod, lathe, sphere, ring, sweep, plate, write, tube

DARK = "#131416"     # (a bore, a port, a slot: what is a hole is drawn as a near-black inset)
ERA_MOD = "1950-2030"


# ---- THE GUNSMITH'S HELPERS ------------------------------------------------------------------------------------------
def side(id_, mat, pts, thick, z=0, **k):
    """a part seen from the side: its outline in (x, y), `thick` across z, centred on z"""
    return plate(id_, mat, pts, thick, [0, 0, z], **k)


def bore(id_, x, r, y=0, z=0):
    """the muzzle's hole: a black disc just proud of the face at x"""
    a, b = (f"{x} - 0.002", f"{x} + 0.0008") if isinstance(x, str) else (x - 0.002, x + 0.0008)
    return rod(id_, "dark", r, [a, y, z], [b, y, z], 10)


def guard(id_, mat, pts, w=0.006, t=0.0035):
    """a trigger guard's bow: a flat strap along the points in the xy plane, `w` across z, `t` thick"""
    return sweep(id_, mat, [[x, y, 0] for x, y in pts], None, section=[t, w], up=[0, 0, 1], seg=4)


def rail(id_, x0, x1, y, w=0.021, mat="metal"):
    """a Picatinny rail on top at height y: the base and its cross-slots' teeth every 10 mm"""
    n = max(2, int(round((x1 - x0) / 0.01)))
    return [box(id_, mat, [x1 - x0, 0.004, w * 0.75], [(x0 + x1) / 2, y + 0.002, 0]),
            box(id_ + "T", mat, [0.0052, 0.0036, w], [0, y + 0.0058, 0], along={"n": n, "from": [x0 + 0.004, 0, 0], "to": [x1 - 0.004, 0, 0]})]


def ring_x(id_, mat, r, t, x, y=0, z=0, **k):
    """a ring round the +x axis (a scope's mount, a barrel band)"""
    return ring(id_, mat, r, t, [x, y, z, 0, 0, 90], **k)


def curved(front, back, n=6):
    """a curved magazine's outline: the front edge's and the back edge's points top-down, joined across the bottom"""
    return front + list(reversed(back))


def arc_pts(x0, y0, x1, y1, bulge, n=6):
    """points from (x0, y0) to (x1, y1) bowed `bulge` to the right of the way (a magazine's curve, a stock's belly)"""
    out = []
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = dy / L, -dx / L
    for i in range(n + 1):
        t = i / n
        b = 4 * bulge * t * (1 - t)
        out.append([x0 + dx * t + nx * b, y0 + dy * t + ny * b])
    return out


def handgun_hold(grip, axis):
    return {"grip": grip, "axis": axis, "face": [1, 0, 0], "carry": {"axis": [0, -1, 0.3], "face": [1, 0, 0]}}


def longgun_hold(grip, grip2):
    return {"grip": grip, "axis": [1, 0, 0], "face": [0, 1, 0], "grip2": grip2,
            "carry": {"axis": [0.05, 1, 0], "face": [1, 0, 0]}, "follow": 0, "rest": "ground"}


def trigger(id_, mat, x, y, drop=0.022, t=0.0055):
    """a curved trigger blade hanging from (x, y), its face forward"""
    return side(id_, mat, [[x + 0.002, y], [x + 0.003, y - drop * 0.5], [x - 0.001, y - drop * 0.9], [x - 0.006, y - drop],
                           [x - 0.003, y - drop * 0.75], [x - 0.003, y - drop * 0.35], [x - 0.004, y]], t)


# ---- A REVOLVER ------------------------------------------------------------------------------------------------------
def revolver():
    # A DOUBLE-ACTION REVOLVER (the medium frame of the police and the target shooter, .38 / .357, 1899 on): a blued
    # frame with its cylinder window, six chambers in a fluted cylinder swung out on its crane, a barrel with a full
    # under-lug round the ejector rod and a rib on top, a spurred hammer, wooden grips. 4" barrel: 240 mm long, 145 high.
    yc, R = -0.0125, 0.0185   # (the cylinder's axis under the bore: the top chamber is the one fired)
    B = "barrel"
    fx = 0.054                # (the frame's front, where the barrel screws in)
    parts = [
        # (the frame: one outline notched by the cylinder's window; the top strap closes the window above)
        side("frame", "metal", [[fx, 0.0155], [0.042, 0.0155], [0.042, -0.031], [0.0, -0.031], [-0.002, 0.0155], [-0.012, 0.0165],
                                [-0.027, 0.011], [-0.035, -0.003], [-0.041, -0.022], [-0.057, -0.062], [-0.067, -0.099], [-0.065, -0.11],
                                [-0.041, -0.112], [-0.031, -0.08], [-0.023, -0.052], [-0.015, -0.039], [0.041, -0.039], [fx, -0.031]], 0.025),
        box("topstrap", "metal", [0.048, 0.009, 0.02], [0.02, 0.0115, 0], round=0.002),
        box("rearSight", "metal", [0.008, 0.004, 0.012], [-0.002, 0.0175, 0]),
        box("rearNotch", "dark", [0.0085, 0.0042, 0.0025], [-0.002, 0.0178, 0]),
        # (the grips: walnut panels a little wider than the frame, their edge rounded by a second, narrower plate)
        side("grips", "grip", [[-0.0405, -0.026], [-0.056, -0.062], [-0.068, -0.1], [-0.066, -0.109], [-0.042, -0.111],
                               [-0.032, -0.08], [-0.025, -0.054], [-0.021, -0.034]], 0.031),
        side("gripsEdge", "grip", [[-0.0415, -0.03], [-0.055, -0.064], [-0.065, -0.098], [-0.064, -0.105], [-0.044, -0.107],
                                   [-0.035, -0.08], [-0.028, -0.055], [-0.025, -0.036]], 0.036),
        sphere("screw", "metal", 0.0028, [-0.045, -0.07, 0.018], stretch=[1, 1, 0.4], mirror="z"),
        # (the cylinder: six chambers, fluted between them, turning on the crane under the barrel)
        tube("cylinder", "metal", [[0.004, 0], [0.0172, 0], [R, 0.0025], [R, 0.0345], [0.0168, 0.0395], [0.005, 0.0395]], 0.0015, yc, sides=18),
        # (2026-11-22: the six flutes one part, the six chambers one -- were twelve; the cylinder 18 sides round, was 24)
        box("flutes", "flute", [0.02, 0.0024, 0.005], [[0.0195, yc + 0.0177 * math.cos(math.radians(30 + 60 * k)), 0.0177 * math.sin(math.radians(30 + 60 * k)), 0, 30 + 60 * k, 0] for k in range(6)]),
        rod("chambers", "dark", 0.0046, [0.039, 0, 0], [0.0415, 0, 0], 8, at=[[0, yc + 0.0122 * math.cos(math.radians(60 * k)), 0.0122 * math.sin(math.radians(60 * k))] for k in range(6)]),
        rod("pin", "metal", 0.003, [0.041, yc, 0], [0.06, yc, 0], 8),
        # (the barrel: its full under-lug shrouding the ejector rod, the rib on top, the ramp of the front sight)
        tube("barrel", "metal", [[0.0, 0], [0.0088, 0], [0.0088, B], [0.0068, B + "+ 0.001"], [0.0, B + "+ 0.001"]], fx - 0.004, 0, sides=16),
        side("lug", "metal", [[fx - 0.004, -0.004], [B + " + " + str(fx - 0.004), -0.004], [B + " + " + str(fx - 0.004), -0.014],
                              [B + " + " + str(fx - 0.006), -0.0165], [fx + 0.004, -0.0165], [fx - 0.004, -0.024]], 0.0115),
        box("rib", "metal", [B, 0.005, 0.008], [B + " / 2 + " + str(fx - 0.004), 0.008, 0]),
        side("frontSight", "metal", [[B + " + " + str(fx - 0.03), 0.0105], [B + " + " + str(fx - 0.008), 0.0105], [B + " + " + str(fx - 0.007), 0.021],
                                     [B + " + " + str(fx - 0.011), 0.021]], 0.003),
        bore("muzzle", B + " + " + str(fx - 0.003), 0.0046),
        # (the hammer cocked down, its spur back over the grip; the trigger in its guard)
        side("hammer", "metal", [[-0.01, 0.006], [-0.016, 0.022], [-0.027, 0.03], [-0.039, 0.03], [-0.04, 0.026], [-0.03, 0.023], [-0.024, 0.016], [-0.022, 0.004]], 0.007),
        trigger("trigger", "metal", 0.012, -0.038, 0.026),
        guard("guard", "metal", [[0.03, -0.038], [0.032, -0.056], [0.02, -0.071], [0.002, -0.073], [-0.011, -0.063], [-0.015, -0.045]]),
        box("latch", "metal", [0.012, 0.007, 0.004], [-0.009, 0.0, -0.0135], round=0.002),
    ]
    return item("Revolver", "weapon/firearm",
        "a double-action revolver of the police and the target range (a .38 or .357 medium frame, 1899 on): a blued steel frame round its cylinder's window, six chambers in a fluted cylinder, a barrel with a full under-lug and a rib, the front sight's ramp, a spurred hammer, a trigger in its guard, walnut grips. 240 mm long and 145 mm high with the 4-inch barrel (`barrel` 2.5, 4 or 6 inches); about 1 kg.",
        {"metal": "gunmetal", "grip": {"pick": ["walnut", "walnut", "rubber"]}, "flute": "#232528", "dark": DARK}, parts,
        params={"barrel": {"pick": [0.064, 0.102, 0.102, 0.152]}}, hold=handgun_hold([-0.047, -0.07, 0], [0.28, 1, 0]), era="1899-2030")


# ---- A SELF-LOADING PISTOL -------------------------------------------------------------------------------------------
def pistol():
    # A SELF-LOADING PISTOL (the polymer-framed service pistol of the 1980s on, 9 mm): a squared steel slide over a
    # polymer frame, its grip raked 22 degrees round a 17-round magazine, a squared trigger guard, a rail under the
    # dust cover. 186 mm long, 138 mm high, 30 mm wide.
    parts = [
        box("slide", "metal", [0.186, 0.03, 0.0255], [0.072, 0.007, 0], round=0.003),
        box("slideTop", "metal", [0.186, 0.004, 0.019], [0.072, 0.0225, 0], round=0.0015),
        box("serr", "dark", [0.0016, 0.022, 0.0262], [0, 0.007, 0], along={"n": 7, "from": [-0.015, 0, 0], "to": [0.0, 0, 0]}),
        box("port", "dark", [0.03, 0.008, 0.002], [0.04, 0.0185, 0.0125]),
        box("hood", "barrel", [0.026, 0.006, 0.004], [0.04, 0.019, 0.0115]),
        bore("muzzle", 0.1652, 0.0048, 0.004),
        box("frontSight", "metal", [0.004, 0.0055, 0.0035], [0.155, 0.026, 0]),
        box("rearSight", "metal", [0.008, 0.0055, 0.009], [-0.009, 0.026, 0.0062], mirror="z"),
        # (the frame: the dust cover with its rail, the grip raked back, the beavertail)
        side("frame", "frame", [[0.151, -0.008], [0.153, -0.024], [0.052, -0.024], [0.004, -0.024], [-0.004, -0.034], [-0.022, -0.075],
                                [-0.037, -0.114], [-0.038, -0.123], [-0.071, -0.121], [-0.069, -0.106], [-0.052, -0.05], [-0.044, -0.024],
                                [-0.037, -0.012], [-0.03, -0.008]], 0.028),
        side("gripPanel", "texture", [[-0.007, -0.038], [-0.034, -0.11], [-0.066, -0.108], [-0.05, -0.05], [-0.042, -0.03]], 0.0305),
        box("railSlot", "dark", [0.003, 0.003, 0.0285], [0, -0.0235, 0], along={"n": 3, "from": [0.09, 0, 0], "to": [0.13, 0, 0]}),
        guard("guard", "frame", [[0.052, -0.023], [0.053, -0.047], [0.045, -0.056], [0.008, -0.056], [-0.004, -0.044], [-0.008, -0.033]], 0.012, 0.004),
        trigger("trigger", "frame", 0.02, -0.024, 0.022, 0.006),
        side("baseplate", "frame", [[-0.035, -0.121], [-0.037, -0.13], [-0.073, -0.128], [-0.072, -0.12]], 0.026),
        box("slideStop", "metal", [0.016, 0.003, 0.003], [0.03, -0.009, -0.0145]),
        box("takedown", "metal", [0.006, 0.006, 0.0305], [0.06, -0.013, 0]),
    ]
    return item("Self-loading pistol", "weapon/firearm",
        "a polymer-framed self-loading service pistol (9 mm, the 1980s on): a squared steel slide with its rear serrations, ejection port and sights, a polymer frame with a rail under the dust cover, a grip raked 22 degrees round its 17-round magazine, a squared trigger guard. 186 mm long, 138 mm high, 30 mm wide; 0.7 kg loaded.",
        {"metal": "gunmetal", "barrel": "steel", "frame": {"pick": ["polymer", "polymer", "olive-drab", "#8a7a5a"]}, "texture": "polymer", "dark": DARK}, parts,
        hold=handgun_hold([-0.04, -0.07, 0], [0.41, 1, 0]), era="1982-2030")


# ---- A BOLT-ACTION RIFLE ---------------------------------------------------------------------------------------------
def bolt_rifle():
    # A BOLT-ACTION RIFLE (the hunter's and the sniper's, the Mauser's descendants): a round receiver, the bolt's handle
    # turned down on the right, a 610 mm (24") tapered barrel, a walnut stock with a pistol grip and a Monte Carlo
    # comb, a rubber pad, sling swivels; a telescopic sight in rings (`scope` 1) or open sights (0). 1.13 m long, 3.6 kg.
    xb, BL = 0.16, 0.61   # (the barrel's breech and length)
    stock = [[0.505, -0.008], [0.16, -0.007], [-0.07, -0.009], [-0.1, -0.021], [-0.135, -0.009], [-0.175, 0.008], [-0.3, 0.012],
             [-0.36, 0.007], [-0.364, -0.128], [-0.2, -0.092], [-0.115, -0.08], [-0.098, -0.1], [-0.068, -0.101], [-0.046, -0.072],
             [-0.032, -0.052], [0.13, -0.049], [0.45, -0.037], [0.497, -0.031], [0.508, -0.02]]
    sc = 0.047   # (the scope's axis over the bore)
    parts = [
        side("stock", "wood", stock, 0.042),
        side("comb", "wood", [[-0.14, 0.0], [-0.175, 0.008], [-0.3, 0.012], [-0.355, 0.006], [-0.355, -0.04], [-0.14, -0.04]], 0.047),
        side("pad", "pad", [[-0.36, 0.008], [-0.384, 0.009], [-0.388, -0.131], [-0.364, -0.129]], 0.044),
        side("cap", "cap", [[-0.098, -0.1], [-0.068, -0.101], [-0.066, -0.098], [-0.097, -0.097]], 0.03),
        # (the action: the receiver, the bolt's shroud behind it, the handle down on the right, the port, the floorplate)
        tube("receiver", "metal", [[0, 0], [0.0165, 0.004], [0.0172, 0.01], [0.0172, 0.225], [0.0, 0.225]], -0.065, 0, sides=16),
        tube("shroud", "metal", [[0, 0], [0.008, 0.002], [0.0128, 0.012], [0.0135, 0.045], [0, 0.045]], -0.11, 0.001, sides=12),
        rod("bolt", "bolt", 0.0035, [-0.05, 0.004, 0.016], [-0.055, -0.024, 0.06], 8),
        sphere("knob", "bolt", 0.0095, [-0.056, -0.027, 0.064], sides=12),
        box("port", "dark", [0.07, 0.016, 0.006], [0.03, 0.007, 0.014, 0, -25, 0]),
        box("floor", "metal", [0.13, 0.005, 0.03], [0.07, -0.05, 0]),
        guard("guard", "metal", [[0.036, -0.05], [0.038, -0.064], [0.025, -0.077], [0.0, -0.078], [-0.022, -0.07], [-0.032, -0.052]], 0.01),
        trigger("trigger", "metal", 0.004, -0.05, 0.022),
        # (the barrel, tapering from the breech's 26 mm to the muzzle's 17)
        tube("barrel", "metal", [[0, 0], [0.0135, 0], [0.013, 0.08], [0.0088, BL], [0, BL]], xb, 0, sides=14),
        bore("muzzle", xb + BL, 0.0035),
        ring("swivelF", "metal", 0.007, 0.0015, [0.41, -0.05, 0, 0, 90, 0]), ring("swivelB", "metal", 0.007, 0.0015, [-0.27, -0.116, 0, 0, 90, 0]),
        # (a telescope: the 1-inch tube, the objective's bell forward, the eyepiece behind, the turrets, two rings on bases)
        tube("scope", "scope", [[0.019, 0], [0.019, 0.05], [0.0127, 0.075], [0.0127, 0.235], [0.024, 0.285], [0.025, 0.33]], -0.135, sc, sides=20, when="scope"),
        rod("lensF", "lens", 0.022, [0.194, sc, 0], [0.196, sc, 0], 20, when="scope"),
        rod("lensB", "lens", 0.016, [-0.137, sc, 0], [-0.135, sc, 0], 16, when="scope"),
        rod("turret", "scope", 0.0105, [0.03, sc, 0], [0.03, sc + 0.026, 0], 14, when="scope"),
        rod("turretS", "scope", 0.0105, [0.03, sc, 0], [0.03, sc, 0.026], 14, when="scope"),
        rod("power", "scope", 0.0165, [-0.07, sc, 0], [-0.045, sc, 0], 16, when="scope"),
        ring("ring", "metal", 0.0135, 0.0035, [[-0.02, sc, 0, 0, 0, 90], [0.12, sc, 0, 0, 0, 90]], when="scope"),
        box("base", "metal", [0.016, sc - 0.03, 0.014], [[-0.02, 0.016 + (sc - 0.03) / 2, 0], [0.12, 0.016 + (sc - 0.03) / 2, 0]], when="scope"),
        # (or open sights: a ramp and bead at the muzzle, a leaf over the barrel)
        side("ramp", "metal", [[xb + BL - 0.04, 0.007], [xb + BL - 0.008, 0.007], [xb + BL - 0.008, 0.016], [xb + BL - 0.015, 0.016]], 0.004, when={"scope": 0}),
        side("leaf", "metal", [[0.33, 0.009], [0.345, 0.009], [0.343, 0.019], [0.332, 0.019]], 0.012, when={"scope": 0}),
    ]
    return item("Bolt-action rifle", "weapon/firearm",
        "a bolt-action hunting rifle, the Mauser's descendant (the 20th century on): a round steel receiver, the bolt's handle turned down on the right, a tapered 610 mm barrel, a walnut stock with a pistol grip, a Monte Carlo comb and a rubber pad, sling swivels; a 3-9x40 telescope in rings (`scope` 1) or a ramp and leaf (0). 1.13 m long; 3.6 kg, 4.2 with the scope.",
        {"metal": "gunmetal", "bolt": "steel", "wood": {"pick": ["walnut", "walnut", "#3b3d33"]}, "pad": "rubber", "cap": "ebony", "scope": "gunmetal",
         "lens": "glass", "dark": DARK}, parts, params={"scope": {"pick": [1, 1, 0]}}, hold=longgun_hold([-0.074, -0.06, 0], [0.3, -0.03, 0]), era="1898-2030")


# ---- A PUMP SHOTGUN --------------------------------------------------------------------------------------------------
def shotgun():
    # A PUMP-ACTION SHOTGUN (12 bore, the 1950s pattern): a machined receiver, a 711 mm (28") barrel with a ventilated
    # rib and a bead, the tube magazine under it, the grooved fore-end that slides on its action bars, a walnut stock
    # with a semi-pistol grip and a pad. 1.24 m long, 3.6 kg.
    xb, BL, ym = 0.15, 0.66, -0.0255
    parts = [
        box("receiver", "metal", [0.215, 0.058, 0.033], [0.0425, -0.006, 0], round=0.006),
        box("port", "dark", [0.072, 0.02, 0.004], [0.07, 0.004, 0.015]),
        box("bolt", "bolt", [0.06, 0.012, 0.004], [0.07, 0.004, 0.0158]),
        box("release", "metal", [0.009, 0.006, 0.004], [-0.0, -0.02, -0.0168]),
        # (the barrel with its vent rib on posts and the brass bead; the magazine tube beneath and its cap)
        tube("barrel", "metal", [[0, 0], [0.0128, 0], [0.0125, 0.06], [0.0112, 0.12], [0.0112, BL], [0, BL]], xb, 0, sides=16),
        box("rib", "metal", [BL - 0.03, 0.0025, 0.008], [xb + BL / 2, 0.0175, 0]),
        box("ribPost", "metal", [0.004, 0.005, 0.005], [0, 0.014, 0], along={"n": 16, "from": [xb + 0.03, 0, 0], "to": [xb + BL - 0.03, 0, 0]}),
        sphere("bead", "bead", 0.0022, [xb + BL - 0.012, 0.0205, 0], sides=8),
        bore("muzzle", xb + BL, 0.0092),
        tube("magazine", "metal", [[0, 0], [0.0115, 0], [0.0115, 0.44], [0, 0.44]], xb - 0.01, ym, sides=14),
        tube("magCap", "metal", [[0, 0], [0.013, 0], [0.013, 0.026], [0.009, 0.034], [0, 0.036]], xb + 0.43, ym, sides=14),
        box("barrelRing", "metal", [0.018, 0.04, 0.02], [xb + 0.42, -0.012, 0], round=0.006),
        # (the fore-end on the magazine: grooved round, the action bars back to the receiver)
        tube("foreend", "fore", [[0, 0], [0.019, 0.0], [0.023, 0.012]] + [[0.023 if i % 2 == 0 else 0.0205, 0.025 + 0.013 * i] for i in range(13)] + [[0.022, 0.2], [0.019, 0.21], [0, 0.21]], xb + 0.03, ym - 0.002, sides=18),
        rod("bars", "metal", 0.0022, [xb - 0.005, ym + 0.006, 0.0105], [xb + 0.04, ym + 0.006, 0.0105], 6, mirror="z"),
        # (the guard, the trigger, the safety)
        side("guardBody", "metal", [[0.06, -0.035], [0.062, -0.042], [-0.03, -0.042], [-0.05, -0.035]], 0.02),
        guard("guard", "metal", [[0.04, -0.042], [0.04, -0.06], [0.026, -0.072], [0.0, -0.073], [-0.022, -0.064], [-0.035, -0.042]], 0.011),
        trigger("trigger", "metal", 0.008, -0.042, 0.022),
        rod("safety", "metal", 0.003, [-0.028, -0.036, -0.019], [-0.028, -0.036, 0.019], 8),
        # (the stock: the semi-pistol grip and the drop to the heel, the pad)
        side("stock", "wood", [[-0.062, 0.018], [-0.09, 0.0], [-0.14, -0.011], [-0.2, -0.016], [-0.43, -0.038], [-0.432, -0.18],
                               [-0.27, -0.135], [-0.17, -0.112], [-0.13, -0.106], [-0.105, -0.11], [-0.085, -0.104], [-0.065, -0.07],
                               [-0.055, -0.036], [-0.06, -0.01]], 0.041),
        side("pad", "pad", [[-0.43, -0.038], [-0.452, -0.038], [-0.455, -0.181], [-0.432, -0.18]], 0.043),
    ]
    return item("Pump shotgun", "weapon/firearm",
        "a pump-action 12-bore shotgun (the 1950s pattern, still made): a machined steel receiver with its ejection port, a 711 mm barrel under a ventilated rib with a brass bead, the tube magazine beneath it, the grooved fore-end that slides back on its action bars, a walnut stock with a semi-pistol grip and a rubber pad. 1.24 m long; 3.6 kg.",
        {"metal": "gunmetal", "bolt": "steel", "wood": {"pick": ["walnut", "walnut", "polymer"]}, "fore": "wood", "pad": "rubber", "bead": "brass", "dark": DARK}, parts,
        hold=longgun_hold([-0.08, -0.06, 0], [0.26, -0.03, 0]), era="1950-2030")


# ---- AN ASSAULT RIFLE ------------------------------------------------------------------------------------------------
def assault_rifle():
    # AN ASSAULT RIFLE (the 5.56 mm carbine of the 1990s on, the M4 pattern): an aluminium upper with a rail on its flat
    # top, a lower with the magazine well and the pistol grip, the 30-round curved magazine, a 368 mm barrel in round
    # ribbed handguards, the triangular front sight, a birdcage flash hider, a flip-up rear sight, a collapsible stock
    # on its buffer tube. 840 mm long (the stock out), 255 mm high with the magazine; 3.4 kg loaded.
    xb, BL = 0.135, 0.368
    mfront = arc_pts(0.108, -0.045, 0.14, -0.215, 0.01, 6)
    mback = arc_pts(0.048, -0.045, 0.08, -0.222, 0.01, 6)
    parts = [
        # (the upper: the receiver, the rail, the charging handle, the forward assist and the port on the right)
        box("upper", "metal", [0.215, 0.034, 0.027], [0.025, 0.008, 0], round=0.003),
        *rail("rail", -0.08, 0.135, 0.025),
        box("charging", "metal", [0.016, 0.008, 0.042], [-0.088, 0.019, 0], round=0.002),
        tube("assist", "metal", [[0, 0], [0.0065, 0], [0.0065, 0.035], [0, 0.035]], -0.055, 0.014, 0.017, sides=10),
        box("port", "dark", [0.055, 0.013, 0.003], [0.035, 0.006, 0.0133]),
        side("deflector", "metal", [[-0.012, 0.005], [-0.0, 0.016], [0.004, 0.016], [0.004, 0.0]], 0.006, 0.014),
        # (the lower: the magazine well flared at its mouth, over the guard; the buffer housing behind)
        side("lower", "metal", [[0.112, -0.009], [0.113, -0.05], [0.106, -0.058], [0.046, -0.058], [0.044, -0.03], [0.0, -0.03], [-0.03, -0.03],
                                [-0.06, -0.024], [-0.095, -0.02], [-0.098, -0.009]], 0.026),
        guard("guard", "metal", [[0.044, -0.03], [0.04, -0.054], [0.0, -0.057], [-0.024, -0.046], [-0.03, -0.03]], 0.012, 0.004),
        trigger("trigger", "metal", 0.012, -0.03, 0.019),
        rod("selector", "metal", 0.0045, [-0.04, -0.017, -0.016], [-0.04, -0.017, -0.012], 10),
        box("magRelease", "metal", [0.008, 0.008, 0.004], [0.058, -0.035, 0.0145], round=0.002),
        side("grip", "plastic", [[-0.03, -0.028], [-0.022, -0.04], [-0.045, -0.115], [-0.05, -0.122], [-0.078, -0.12], [-0.074, -0.1],
                                 [-0.064, -0.06], [-0.058, -0.028]], 0.024),
        # (the curved magazine and its base)
        side("magazine", "mag", curved(mfront, mback), 0.022),
        side("magBase", "mag", [[0.139, -0.212], [0.141, -0.222], [0.078, -0.229], [0.076, -0.218]], 0.026),
        # (the buffer tube and the collapsible stock on it)
        tube("buffer", "metal", [[0, 0], [0.0145, 0], [0.0145, 0.26], [0, 0.26]], -0.355, 0.0, sides=14),
        side("stock", "plastic", [[-0.22, 0.02], [-0.27, 0.024], [-0.37, 0.027], [-0.373, -0.095], [-0.345, -0.096], [-0.3, -0.06],
                                  [-0.245, -0.03], [-0.22, -0.017]], 0.038),
        side("buttpad", "pad", [[-0.37, 0.027], [-0.382, 0.027], [-0.384, -0.096], [-0.373, -0.095]], 0.04),
        # (the barrel and its handguards: a delta ring at the receiver, the round ribbed guards, the cap)
        tube("barrel", "metal", [[0, 0], [0.0095, 0], [0.0095, BL], [0, BL]], xb, 0, sides=12),
        tube("delta", "metal", [[0, 0], [0.028, 0], [0.028, 0.012], [0.02, 0.016], [0, 0.016]], xb, -0.002, sides=18),
        tube("handguard", "plastic", [[0, 0], [0.025, 0]] + [[0.025 if i % 2 == 0 else 0.0225, 0.008 + 0.012 * i] for i in range(14)] + [[0.022, 0.175], [0, 0.175]], xb + 0.016, -0.002, sides=18),
        tube("cap", "metal", [[0, 0], [0.019, 0], [0.019, 0.008], [0, 0.008]], xb + 0.19, -0.002, sides=14),
        # (the front sight base: an A-frame up from the gas block to its post between two ears)
        side("fsb", "metal", [[xb + 0.2, -0.012], [xb + 0.226, -0.012], [xb + 0.221, 0.012], [xb + 0.219, 0.052], [xb + 0.209, 0.052], [xb + 0.205, 0.012]], 0.012),
        box("ears", "metal", [0.008, 0.016, 0.003], [xb + 0.214, 0.06, 0.0045], mirror="z"),
        box("post", "metal", [0.003, 0.012, 0.0025], [xb + 0.214, 0.058, 0]),
        box("lugB", "metal", [0.012, 0.012, 0.009], [xb + 0.225, -0.016, 0]),
        # (the birdcage: a hider with its slots)
        tube("hider", "metal", [[0, 0], [0.0105, 0.003], [0.0105, 0.044], [0, 0.044]], xb + BL, 0, sides=12),
        box("slot", "dark", [0.026, 0.0025, 0.0222], [[xb + BL + 0.027, 0, 0, 0, 90, 0], [xb + BL + 0.027, 0, 0, 0, 30, 0], [xb + BL + 0.027, 0, 0, 0, -30, 0]]),
        bore("muzzle", xb + BL + 0.044, 0.0035),
        # (the flip-up rear sight on the rail: its body and the aperture)
        side("rearSight", "metal", [[-0.075, 0.033], [-0.045, 0.033], [-0.05, 0.045], [-0.06, 0.054], [-0.066, 0.054]], 0.02),
        ring("aperture", "metal", 0.0045, 0.0018, [-0.063, 0.057, 0, 0, 0, 90]),
        ring("sling", "metal", 0.008, 0.0016, [-0.36, -0.08, 0, 0, 90, 0]),
    ]
    return item("Assault rifle", "weapon/firearm",
        "a 5.56 mm assault carbine of the M4 pattern (the 1990s on): an aluminium upper receiver with a Picatinny rail on its flat top, the charging handle, the forward assist and the brass deflector, a lower with the flared magazine well and the pistol grip, a curved 30-round magazine, a 368 mm barrel in round ribbed handguards, the A-frame front sight, a birdcage flash hider, a flip-up rear sight and a collapsible stock on its buffer tube. 840 mm long with the stock out; 3.4 kg loaded.",
        {"metal": "gunmetal", "plastic": "polymer", "mag": {"pick": ["gunmetal", "polymer", "#8a7a5a"]}, "pad": "rubber", "dark": DARK}, parts,
        hold=longgun_hold([-0.05, -0.065, 0], [0.24, -0.015, 0]), era="1994-2030")


# ---- A SUBMACHINE GUN ------------------------------------------------------------------------------------------------
def smg():
    # A SUBMACHINE GUN (9 mm, the roller-delayed pattern of the police, 1966 on): a pressed-steel receiver, the cocking
    # tube over the barrel and its lever at the left front, a slim fore-end, the hooded front sight and the drum of
    # apertures at the rear, a curved 30-round magazine, a polymer trigger group with its grip, a fixed stock.
    # 680 mm long, 225 mm barrel, 2.9 kg loaded.
    ct = 0.021   # (the cocking tube's axis)
    mfront = arc_pts(0.112, -0.03, 0.16, -0.2, 0.016, 6)
    mback = arc_pts(0.082, -0.03, 0.125, -0.207, 0.016, 6)
    parts = [
        box("receiver", "metal", [0.27, 0.052, 0.033], [0.012, 0.003, 0], round=0.009),
        box("ribs", "metal", [0.27, 0.006, 0.035], [0.012, -0.012, 0]),
        box("port", "dark", [0.045, 0.012, 0.003], [0.06, 0.01, 0.016]),
        box("mount", "metal", [0.012, 0.007, 0.022], [[-0.05, 0.03, 0], [0.09, 0.03, 0]]),
        tube("cocking", "metal", [[0, 0], [0.0115, 0], [0.0115, 0.13], [0.009, 0.135], [0, 0.135]], 0.147, ct, sides=14),
        rod("lever", "metal", 0.003, [0.2, ct, -0.01], [0.212, ct + 0.012, -0.032], 6),
        sphere("leverKnob", "plastic", 0.006, [0.213, ct + 0.013, -0.034], sides=8),
        # (the fore-end round the barrel: slim, grooved)
        box("foreend", "plastic", [0.135, 0.046, 0.044], [0.215, -0.012, 0], round=0.016),
        box("groove", "dark", [0.1, 0.003, 0.0445], [[0.215, -0.006, 0], [0.215, -0.018, 0]]),
        # (the barrel and its three-lug muzzle)
        tube("barrel", "metal", [[0, 0], [0.0085, 0], [0.0085, 0.08], [0.011, 0.082], [0.011, 0.094], [0, 0.094]], 0.283, 0, sides=12),
        bore("muzzle", 0.377, 0.0045),
        # (the front sight: a hooded post over the cocking tube; the rear drum)
        side("fsPost", "metal", [[0.262, ct + 0.006], [0.284, ct + 0.006], [0.279, 0.05], [0.267, 0.05]], 0.012),
        ring("hood", "metal", 0.0115, 0.0024, [0.273, 0.058, 0, 0, 0, 90]),
        box("fsBlade", "metal", [0.003, 0.009, 0.002], [0.273, 0.052, 0]),
        side("rsBase", "metal", [[-0.125, 0.028], [-0.095, 0.028], [-0.1, 0.045], [-0.12, 0.045]], 0.02),
        rod("drum", "metal", 0.0115, [-0.11, 0.054, -0.012], [-0.11, 0.054, 0.012], 12),
        rod("aperture", "dark", 0.0025, [-0.12, 0.054, 0], [-0.0995, 0.054, 0], 8),
        # (the magazine, curved forward)
        side("magazine", "mag", curved(mfront, mback), 0.02),
        side("magWell", "metal", [[0.116, -0.022], [0.116, -0.04], [0.08, -0.04], [0.08, -0.022]], 0.026),
        # (the trigger group: its housing, a big guard and the grip)
        side("trigGroup", "plastic", [[0.05, -0.022], [0.05, -0.034], [0.0, -0.036], [-0.02, -0.036], [-0.025, -0.045], [-0.045, -0.11],
                                      [-0.047, -0.118], [-0.075, -0.116], [-0.074, -0.1], [-0.07, -0.05], [-0.09, -0.032], [-0.1, -0.022]], 0.03),
        guard("guard", "plastic", [[0.045, -0.035], [0.048, -0.058], [0.035, -0.07], [0.0, -0.068], [-0.018, -0.058], [-0.026, -0.045]], 0.014, 0.0045),
        trigger("trigger", "metal", 0.012, -0.035, 0.019),
        box("selector", "metal", [0.012, 0.004, 0.003], [-0.06, -0.03, -0.0158, 0, 0, 30]),
        rod("pins", "metal", 0.0025, [0, -0.028, -0.0165], [0, -0.028, 0.0165], 6, at=[[0.03, 0, 0], [-0.095, 0, 0]]),
        # (the fixed stock)
        side("stock", "plastic", [[-0.12, 0.024], [-0.2, 0.021], [-0.3, 0.018], [-0.304, -0.09], [-0.285, -0.092], [-0.24, -0.06], [-0.2, -0.04],
                                  [-0.15, -0.024], [-0.12, -0.02]], 0.036),
        side("buttpad", "pad", [[-0.3, 0.018], [-0.312, 0.018], [-0.314, -0.099], [-0.304, -0.098]], 0.038),
    ]
    return item("Submachine gun", "weapon/firearm",
        "a 9 mm submachine gun of the roller-delayed police pattern (1966 on): a pressed-steel receiver with the cocking tube over the barrel and its lever at the left front, a slim grooved fore-end, a three-lug muzzle, the hooded front post and the rear drum of apertures, a curved 30-round steel magazine, a polymer trigger group with its large guard and grip, a fixed stock. 680 mm long with a 225 mm barrel; 2.9 kg loaded.",
        {"metal": "gunmetal", "plastic": "polymer", "mag": "gunmetal", "pad": "rubber", "dark": DARK}, parts,
        hold=longgun_hold([-0.055, -0.07, 0], [0.21, -0.03, 0]), era="1966-2030")


# ---- A LIGHT MACHINE GUN ---------------------------------------------------------------------------------------------
def lmg():
    # A LIGHT MACHINE GUN (the belt-fed 5.56 mm squad gun, the 1980s on): a riveted box receiver, the feed cover on top
    # with its rear sight, a 465 mm barrel with its carrying handle, the gas tube under it and the bipod at the gas
    # block (`bipod` "out": its legs spread to the ground, "folded": along the barrel), a plastic box of 200 rounds
    # under the left side and the belt into the feed tray, the pistol grip, a solid stock. 1.04 m long, 7.5 kg loaded.
    xb, BL, xg = 0.19, 0.42, 0.52
    parts = [
        box("receiver", "metal", [0.32, 0.07, 0.056], [0.03, -0.004, 0], round=0.004),
        box("rivet", "metal", [0.004, 0.004, 0.058], [0, -0.03, 0], along={"n": 6, "from": [-0.1, 0, 0], "to": [0.15, 0, 0]}),
        box("cover", "metal", [0.19, 0.022, 0.05], [0.04, 0.041, 0], round=0.004),
        *rail("rail", -0.04, 0.12, 0.052, 0.021),
        side("rearSight", "metal", [[-0.075, 0.03], [-0.045, 0.03], [-0.05, 0.05], [-0.07, 0.05]], 0.022),
        box("tray", "metal", [0.07, 0.016, 0.02], [0.115, 0.022, -0.035]),
        box("port", "dark", [0.07, 0.012, 0.003], [0.04, -0.03, 0.0285]),
        box("charging", "metal", [0.012, 0.012, 0.03], [0.1, 0.0, 0.04], round=0.003),
        # (the barrel, its carrying handle, the gas tube beneath, the handguard)
        tube("barrel", "metal", [[0, 0], [0.014, 0], [0.014, 0.06], [0.011, 0.07], [0.011, BL], [0, BL]], xb, 0.012, sides=14),
        sweep("handle", "metal", [[xb + 0.05, 0.026, 0], [xb + 0.07, 0.07, 0.02], [xb + 0.15, 0.075, 0.02], [xb + 0.17, 0.026, 0]], 0.006, seg=5),
        tube("gas", "metal", [[0, 0], [0.011, 0], [0.011, xg - xb], [0, xg - xb]], xb, -0.022, sides=12),
        box("handguard", "plastic", [0.17, 0.045, 0.058], [xb + 0.085, -0.03, 0], round=0.01),
        box("gasBlock", "metal", [0.03, 0.05, 0.03], [xg, -0.006, 0], round=0.004),
        side("fsBase", "metal", [[xb + BL - 0.035, 0.012], [xb + BL - 0.01, 0.012], [xb + BL - 0.014, 0.05], [xb + BL - 0.026, 0.05]], 0.012),
        box("fsPost", "metal", [0.004, 0.012, 0.003], [xb + BL - 0.02, 0.056, 0]),
        tube("hider", "metal", [[0, 0], [0.012, 0.004], [0.012, 0.045], [0, 0.045]], xb + BL, 0.012, sides=12),
        bore("muzzle", xb + BL + 0.045, 0.0035, 0.012),
        # (the bipod: its yoke under the gas block, two telescoping legs and their feet; out or folded)
        box("yoke", "metal", [0.02, 0.014, 0.04], [xg, -0.036, 0]),
        rod("legU", "metal", 0.0065, [xg, -0.04, 0.012], [xg + 0.07, -0.2, 0.09], 8, mirror="z", when={"bipod": "out"}),
        rod("legL", "metal", 0.0045, [xg + 0.07, -0.2, 0.09], [xg + 0.11, -0.3, 0.125], 8, mirror="z", when={"bipod": "out"}),
        box("foot", "metal", [0.03, 0.006, 0.015], [xg + 0.112, -0.303, 0.127], mirror="z", when={"bipod": "out"}),
        rod("legUf", "metal", 0.0065, [xg, -0.04, 0.014], [xg + 0.18, -0.04, 0.014], 8, mirror="z", when={"bipod": "folded"}),
        rod("legLf", "metal", 0.0045, [xg + 0.18, -0.04, 0.014], [xg + 0.27, -0.04, 0.014], 8, mirror="z", when={"bipod": "folded"}),
        # (the ammunition box under the left side, the belt rising into the tray)
        box("ammo", "box", [0.13, 0.11, 0.075], [0.115, -0.1, -0.045], round=0.008),
        box("ammoLid", "box", [0.135, 0.012, 0.08], [0.115, -0.041, -0.045], round=0.004),
        rod("belt", "brass", 0.0048, [-0.028, 0, 0], [0.028, 0, 0], 6, at=[[0.115, -0.03 + 0.0105 * i, -0.04 + 0.001 * i] for i in range(6)]),
        # (the guard, the trigger, the grip, the stock)
        guard("guard", "metal", [[0.04, -0.039], [0.042, -0.06], [0.03, -0.072], [0.0, -0.07], [-0.02, -0.058], [-0.026, -0.039]], 0.014, 0.0045),
        trigger("trigger", "metal", 0.012, -0.039, 0.019),
        side("grip", "plastic", [[-0.02, -0.036], [-0.026, -0.05], [-0.045, -0.115], [-0.05, -0.122], [-0.078, -0.12], [-0.074, -0.1],
                                 [-0.064, -0.06], [-0.06, -0.036]], 0.028),
        side("stock", "plastic", [[-0.12, 0.024], [-0.2, 0.024], [-0.35, 0.026], [-0.355, -0.115], [-0.33, -0.115], [-0.26, -0.085],
                                  [-0.19, -0.05], [-0.12, -0.04]], 0.044),
        side("stockHole", "dark", [[-0.17, 0.006], [-0.29, 0.008], [-0.29, -0.05], [-0.25, -0.045], [-0.2, -0.025], [-0.17, -0.016]], 0.0445),
        side("buttpad", "pad", [[-0.35, 0.026], [-0.362, 0.026], [-0.365, -0.116], [-0.355, -0.115]], 0.046),
    ]
    return item("Light machine gun", "weapon/firearm",
        "a belt-fed 5.56 mm light machine gun, the squad's (the 1980s on): a riveted steel box receiver, the feed cover with its rail and rear sight, the feed tray on the left, a 465 mm barrel with its carrying handle and flash hider, the gas tube and the bipod at the gas block (`bipod` out: its legs spread on the ground, or folded along the barrel), a plastic box of 200 rounds under the left side, a pistol grip and a solid stock. 1.04 m long; 7.5 kg loaded.",
        {"metal": "gunmetal", "plastic": "polymer", "box": "olive-drab", "brass": "brass", "pad": "rubber", "dark": DARK}, parts,
        params={"bipod": {"pick": ["out", "out", "folded"]}}, hold=longgun_hold([-0.05, -0.07, 0], [0.25, -0.04, 0]), era="1984-2030")


ITEMS = [("revolver", revolver), ("pistol", pistol), ("bolt-rifle", bolt_rifle), ("shotgun", shotgun),
         ("assault-rifle", assault_rifle), ("smg", smg), ("lmg", lmg)]


def write_all():
    for name, f in ITEMS:
        write("modern/arms/" + name, f(), "arms")

GROUPS = {"arms": "arms"}
