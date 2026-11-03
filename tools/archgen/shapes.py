# The profiles' own arithmetic (arch/profiles.js), for placing things ON them: how tall a dome of a given profile
# stands, and at what height it has narrowed to a given radius -- where a lantern of that radius can sit on it.
import math

def onion_height(a, bulge=1.25, neck=1.0):
    R1, R2 = a * max(1, bulge), a * max(.05, neck)
    yc = math.sqrt(max(0, R1 * R1 - a * a))
    return yc + math.sqrt(R1 * R1 + 2 * R1 * R2)

def onion_y_at(a, r, bulge=1.25, neck=1.0):
    """the height near the tip where an onion is r across its radius (on its concave neck)"""
    R2, H = a * max(.05, neck), onion_height(a, bulge, neck)
    return H - math.sqrt(max(0, R2 * R2 - (R2 - r) ** 2))

def bell_height(a, waist=.78, lift=1.0):
    return a * (lift + waist)

def tent_y_at(a, rise, r):
    """a cone (trigonal) `rise` tall over radius a: the height at which it is r across"""
    return rise * (1 - r / a)

def bell_y_at(a, r, waist=.78, lift=1.0):
    """the height at which a bell's round crown is r across (r <= its waist)"""
    R2, cy = a * waist, a * lift
    return cy + math.sqrt(max(0, R2 * R2 - r * r))


# PLANS (build.js planPoints' winding: x0*z1 - x1*z0 summing negative, the outside on each edge's left), for setting
# things out round an outline as the engine does: insetPoints' mitred offset, and each edge's frame
def inset_points(pts, d):
    """the outline `pts` moved in by `d` (out if negative), each corner mitred"""
    n = len(pts); lines = []
    for i in range(n):
        (x0, z0), (x1, z1) = pts[i], pts[(i + 1) % n]
        L = math.hypot(x1 - x0, z1 - z0); ex, ez = (x1 - x0) / L, (z1 - z0) / L
        lines.append((x0 + ez * d, z0 - ex * d, ex, ez))
    out = []
    for i in range(n):
        xa, za, ea, fa = lines[i - 1]; xb, zb, eb, fb = lines[i]
        u = ((xb - xa) * fb - (zb - za) * eb) / (ea * fb - fa * eb)
        out.append([round(xa + ea * u, 4), round(za + fa * u, 4)])
    return out


def plan_edges(pts):
    """each edge of an outline: its middle, direction `e`, inward normal `n_in`, length, and the yaw laying a part's x along it"""
    out = []
    for i in range(len(pts)):
        (x0, z0), (x1, z1) = pts[i], pts[(i + 1) % len(pts)]
        L = math.hypot(x1 - x0, z1 - z0); ex, ez = (x1 - x0) / L, (z1 - z0) / L
        out.append({"mid": ((x0 + x1) / 2, (z0 + z1) / 2), "e": (ex, ez), "n_in": (ez, -ex), "L": L, "yaw": math.atan2(-ez, ex)})
    return out
