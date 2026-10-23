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
