"""STATUARY (2026-10-04): the `statue` markers and their pedestals, shared by every building generator that has statues
(statues.js draws them: a carved figure -- pose, dress or another time's style, what it holds, its stone, its size).
A figure's turn (`face`) is its rotY: +x is its forward, so FACE_PZ looks along +z, FACE_NZ along -z, FACE_PX along +x."""
FACE_PZ, FACE_NZ, FACE_PX, FACE_NX = -1.5707963, 1.5707963, 0.0, 3.1415927
FACE_E, FACE_W = FACE_PZ, FACE_NZ          # (a temple's front is +z: its east)
LIMIT = 50                                 # a building's statues at most: the most prominent ones


def statue(at, **d):
    """a `statue` marker at `at` (its feet -- or a seated figure's seat top), the figure's numbers in `d`:
    kind (man | woman), pose (stand | guard | sit | lie), style (greek | roman | gothic | chinese) or outfit,
    hold { R, L } (items: its right hand, its left), grip { R, L } (how that hand holds it, over its pose's: statuary.json
    `grips` -- "shield rest"), wings (raised | spread | folded: an angel's, a Victory's --
    assets/people/statuary.json `wings`), stone (marble | bronze | gold | limestone | painted | chryselephantine | sandstone:
    shell.js STONES), scale, seed, face"""
    return {"type": "marker", "role": "statue", "at": [[round(at[0], 3), round(at[1], 3), round(at[2], 3), 0]], "data": d}


def pedestal(at, w, d, h, about="a statue's pedestal"):
    """a plain pedestal box (its top at at[1] + h): the figure stands at its top"""
    return {"type": "box", "width": round(w, 3), "length": round(d, 3), "height": round(h, 3), "at": [[round(at[0], 3), round(at[1], 3), round(at[2], 3), 0]], "_about": about}


def row(prefix, pts, **d):
    """statues at several points (a balustrade's, a gallery's), each its own seed; `d` as statue's -- a list value is
    taken in turn (kinds, holds)"""
    out = {}
    for i, p in enumerate(pts):
        di = {k: (v[i % len(v)] if isinstance(v, list) and k != "hold" else v) for k, v in d.items()}
        if isinstance(d.get("hold"), list): di["hold"] = d["hold"][i % len(d["hold"])]
        di.setdefault("seed", i + 1)
        out[f"{prefix} {i}"] = statue(p, **{**di, "seed": di["seed"] * 7 + i})
    return out


def madonna(at, scale=1.0, face=FACE_PZ, stone="gold", seed=1, style="roman", child=None, prefix="virgin"):
    """(2026-11-04) a VIRGIN AND CHILD: two `statue` markers -- the Mother standing ("offering left": her left forearm
    held out), the Child seated on that forearm, a third of her size. `at` her feet, `face` her turn (FACE_PZ: looking
    along +z); `child` [up, forward, left] overrides where the Child sits, in her heights (1.0 = her full height) -- the
    Garde's gilt colossus, a crypt's painted Virgin with her bouquet, a silver one on an altar"""
    import math
    H = 1.78 * scale
    up, fwd, left = child or (0.64, 0.21, 0.12)
    # (a figure's +x is its forward and -z its left; turned by `face` as statues.js turns it: x' = x cos + z sin, z' = -x sin + z cos)
    c, s = math.cos(face), math.sin(face)
    fx, fz = fwd * H, -left * H
    p = (at[0] + fx * c + fz * s, at[1] + up * H, at[2] - fx * s + fz * c)
    return {prefix: statue(at, kind="woman", pose="offering left", style=style, stone=stone, scale=scale, seed=seed, face=face),
            f"{prefix} child": statue(p, kind="man", pose="seated", style=style, stone=stone, scale=round(scale * 0.32, 3), seed=seed + 1, face=face)}


def capped(statues):
    """no more than LIMIT: the ones listed first are the more prominent"""
    keep, n = {}, 0
    for k, v in statues.items():
        if v.get("role") == "statue":
            if n >= LIMIT: continue
            n += 1
        keep[k] = v
    return keep
