"""THE MODERN COMPONENTS (2026-11-20; docs/modern.md): the pieces the modern things share, written once as items under
assets/items/modern/components/ and placed by `use` -- a road wheel (car, bus, lorry, tractor: its tyre, rim, hub),
a spoked wheel (a bicycle's, a wheelchair's), a seat (a car's, a bus's, a train's, an aircraft's), a lamp (head, tail,
signal), a bogie (a railway vehicle's two-axle truck), a rotor and a propeller, a screen (a monitor's, a television's,
a phone's). Each is in its own frame and says which way it faces. (The other modules write their own: vehicles.py the
door leaf and the car's pieces, machines.py the track, the lug wheel and the cab, furniture.py the slab door...)"""
from kit import item, box, rod, lathe, loft, sphere, ring, use, write, across, sweep


def wheel():
    # A ROAD WHEEL: its axle along z, centred at the origin, its outside face at +z (mirror a part for the left side);
    # `r` the tyre's outer radius, `w` its width, `rim` the rim's share of r, `spokes` the alloy's spokes (0: a steel
    # disc with holes painted, a lorry's)
    return item("Road wheel", "components", "a pneumatic-tyred wheel: the tyre's rounded tread and walls, the rim's dish, the hub and its nuts, the alloy's spokes -- the axle along z, the outside face at +z",
        {"tyre": "rubber", "rim": "aluminium", "hub": "chrome"}, [
            lathe("tyre", "tyre", [["r * rim * 1.02", "-w / 2"], ["r - w * 0.18", "-w / 2"], ["r - w * 0.04", "-w * 0.42"], ["r", "-w * 0.3"], ["r", "w * 0.3"], ["r - w * 0.04", "w * 0.42"], ["r - w * 0.18", "w / 2"], ["r * rim * 1.02", "w / 2"]], [0, 0, 0, 0, 90, 0], caps=False, sides=28),
            lathe("dish", "rim", [[0, "w * 0.08"], ["r * rim * 0.3", "w * 0.14"], ["r * rim", "w * 0.3"], ["r * rim * 1.03", "w * 0.36"], ["r * rim * 1.03", "-w * 0.4"], [0, "-w * 0.4"]], [0, 0, 0, 0, 90, 0], sides=24),
            box("spoke", "rim", ["r * rim * 0.62", "r * 0.07", "w * 0.08"], [0, 0, "w * 0.26", 0, 0, 0], around={"n": "spokes", "r": "r * rim * 0.5", "plane": "xy"}, when="spokes"),
            lathe("hub", "hub", [[0, "w * 0.3"], ["r * 0.12", "w * 0.3"], ["r * 0.1", "w * 0.36"], [0, "w * 0.37"]], [0, 0, 0, 0, 90, 0], sides=12),
            # (`seal` 1: the tyre's inside closed, a band under the bead from wall to wall -- the tyre is an open lathe, and
            #  past the rim's lip, between it and the tyre's wall, the eye ran on through the tyre's culled inside to
            #  whatever stood behind the wheel: a forklift's orange frame)
            lathe("bead", "tyre", [["r * rim * 1.02", "w / 2"], ["r * rim * 1.02", "-w / 2"]], [0, 0, 0, 0, 90, 0], caps=False, double=True, sides=28, when="seal"),
            sphere("nut", "hub", "r * 0.022", [0, 0, "w * 0.3"], around={"n": 5, "r": "r * 0.17", "plane": "xy"}, sides=6),
        ], params={"r": 0.32, "w": 0.2, "rim": 0.62, "spokes": 5, "seal": 0})


def spoked_wheel():
    # A BICYCLE'S WHEEL (a motorcycle's with fewer, thicker spokes): a thin tyre on a narrow rim, wire spokes from the
    # hub's two flanges, the axle along z
    return item("Spoked wheel", "components", "a wire-spoked wheel: a thin tyre, a narrow rim, the spokes laced from the hub's two flanges to the rim -- the axle along z",
        {"tyre": "rubber", "rim": "aluminium", "spoke": "steel", "hub": "chrome"}, [
            ring("tyre", "tyre", "r - t", "t", [0, 0, 0, 0, 90, 0], sides=8),
            ring("rim", "rim", "r - t * 2.1", "t * 0.45", [0, 0, 0, 0, 90, 0], sides=6),
            rod("spokeR", "spoke", "sr", [0, 0, "hubW"], ["r - t * 2.3", 0, 0], 4, around={"n": "n / 2", "r": 0, "plane": "xy"}),
            rod("spokeL", "spoke", "sr", [0, 0, "-hubW"], ["r - t * 2.3", 0, 0], 4, around={"n": "n / 2", "r": 0, "plane": "xy", "start": "180 / n * 2"}),
            rod("hub", "hub", "hubR", [0, 0, "-hubW * 1.3"], [0, 0, "hubW * 1.3"], 10),
        ], params={"r": 0.35, "t": 0.018, "n": 32, "sr": 0.0018, "hubW": 0.035, "hubR": 0.022})


def seat():
    # A SEAT: its front at +x, its cushion's top at `h`, `w` wide -- a car's (headrest), a bus's (a grab handle),
    # a train's, an aircraft's (`arms`)
    return item("Seat", "components", "an upholstered seat on a frame: the cushion, the back raked back, a headrest, armrests if asked -- its front at +x, the cushion's top at h",
        {"cover": "upholstery", "frame": "plastic-black"}, [
            box("cushion", "cover", ["d", 0.12, "w"], [0, "h - 0.06", 0], round=0.04),
            box("back", "cover", [0.12, "back", "w"], ["-d / 2 + 0.02", "h + back / 2 - 0.04", 0, 0, 0, 12], round=0.04),
            box("headrest", "cover", [0.1, 0.2, "w * 0.55"], ["-d / 2 - 0.06", "h + back + 0.08", 0, 0, 0, 12], round=0.04, when="headrest"),
            box("arm", "frame", ["d * 0.8", 0.05, 0.05], [0, "h + 0.14", "w / 2 + 0.02"], mirror="z", when="arms"),
            box("pedestal", "frame", ["d * 0.6", "h - 0.12", "w * 0.6"], [0, "(h - 0.12) / 2", 0], when="pedestal"),
            rod("grab", "frame", 0.012, ["-d / 2 - 0.02", "h + back - 0.02", "-w * 0.35"], ["-d / 2 - 0.02", "h + back - 0.02", "w * 0.35"], 6, when="grab"),
        ], params={"w": 0.5, "d": 0.5, "h": 0.45, "back": 0.6, "headrest": 1, "arms": 0, "pedestal": 1, "grab": 0})


def lamp():
    # A LAMP set in a body: a short lens facing +x in its bezel -- a head lamp, a tail lamp (red), a signal (amber)
    return item("Lamp", "components", "a lamp: a round or square lens in its chrome bezel, facing +x",
        {"lens": "lamp", "bezel": "chrome"}, [
            lathe("lens", "lens", [[0, 0.012], ["r * 0.8", 0.01], ["r * 0.95", 0], ["r * 0.95", -0.02]], [0, 0, 0, 0, 0, -90], sides=16, when={"shape": "round"}),
            ring("bezel", "bezel", "r * 0.95", "r * 0.08", [0, 0, 0, 0, 0, 90], when={"shape": "round"}),
            box("lensSq", "lens", [0.03, "h", "r * 2"], [0, 0, 0], when={"shape": "square"}),
            box("rimSq", "bezel", [0.024, "h + 0.02", "r * 2 + 0.02"], [-0.006, 0, 0], when={"shape": "square"}),
        ], params={"r": 0.08, "h": 0.07, "shape": "round"})


def bogie():
    # A RAILWAY BOGIE: two wheelsets in a frame, under a car's end -- the track's gauge `g` (1.435 standard)
    return item("Bogie", "components", "a two-axle railway bogie: four flanged wheels on two axles, the side frames with their springs -- for the standard gauge",
        {"wheel": "steel", "frame": "paint-black", "spring": "steel-blue"}, [
            lathe("wheels", "wheel", [["0", "-0.07"], ["r + 0.025", "-0.07"], ["r + 0.025", "-0.05"], ["r", "-0.04"], ["r * 0.97", "0.07"], [0, "0.07"]], [["-base / 2", "r", "g / 2", 0, -90, 0], ["base / 2", "r", "g / 2", 0, -90, 0], ["-base / 2", "r", "-g / 2", 0, 90, 0], ["base / 2", "r", "-g / 2", 0, 90, 0]], sides=20),
            rod("axle", "frame", 0.06, ["0", "r", "-g / 2"], ["0", "r", "g / 2"], 8, at=[["-base / 2", 0, 0], ["base / 2", 0, 0]]),
            box("side", "frame", ["base + 0.6", 0.22, 0.12], [0, "r + 0.05", "g / 2 + 0.13"], mirror="z"),
            box("bolster", "frame", [0.4, 0.2, "g + 0.3"], [0, "r + 0.2", 0]),
            rod("coil", "spring", 0.09, [0, "r + 0.12", "g / 2 + 0.13"], [0, "r + 0.34", "g / 2 + 0.13"], 10, at=[["-0.25", 0, 0], ["0.25", 0, 0]], mirror="z"),
        ], params={"r": 0.46, "g": 1.435, "base": 2.5})


def screen():
    # A SCREEN: a flat panel facing +x -- a monitor's, a television's, a phone's, a dashboard's; `w` x `h`, a bezel
    return item("Screen", "components", "a flat screen facing +x: the dark glass in a thin bezel, the back a little thicker",
        {"glass": "screen", "case": "plastic-black"}, [
            box("case", "case", ["t", "h + b * 2", "w + b * 2"], ["-t / 2", 0, 0]),
            box("glass", "glass", [0.004, "h", "w"], [0.001, 0, 0]),
        ], params={"w": 0.6, "h": 0.34, "b": 0.012, "t": 0.03})


def rotor():
    # A ROTOR (a helicopter's) or a PROPELLER (an aircraft's, a boat's): `n` blades round the y axis from a hub
    return item("Rotor", "components", "blades round a hub, turning about y: a helicopter's rotor (long, thin), a propeller (short, twisted) turned by its parent",
        {"blade": "paint-black", "hub": "steel"}, [
            box("blade", "blade", ["R", "t", "c"], [0, 0, 0, 0, "pitch", 0], around={"n": "n", "r": "R / 2 + hubR * 0.8", "plane": "xz"}),
            lathe("hub", "hub", [[0, "-hubH / 2"], ["hubR", "-hubH / 2"], ["hubR", "hubH / 2"], ["hubR * 0.5", "hubH * 0.8"], [0, "hubH * 0.9"]], [0, 0, 0], sides=12),
        ], params={"n": 4, "R": 5.0, "c": 0.3, "t": 0.04, "pitch": 6, "hubR": 0.18, "hubH": 0.3})


def write_all():
    for name, f in [("wheel", wheel), ("spoked-wheel", spoked_wheel), ("seat", seat), ("lamp", lamp), ("bogie", bogie), ("screen", screen), ("rotor", rotor)]:
        write("modern/components/" + name, f(), "components")

GROUPS = {"components": "components"}
