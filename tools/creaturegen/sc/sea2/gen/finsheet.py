# (2026-11-07) A FIN AS ONE SHEET: the outline laid flat onto its own best plane, rounded and triangulated as sealib's
# fin() does, but written as ONE membrane -- its points shared by every face, one normal for them all -- instead of a
# plate a triangle. A fin's plates are each offset along their OWN normal (bodymesh.js detailMesh), so on a tilted fin
# (a pectoral, a pelvic) the JSON's rounding alone turned them a few degrees apart and they met nowhere: loose crumbs
# of one or two triangles in the mesh. The sheet is one connected piece, rooted on the body.
from sealib import S, fin as _fin, chaikin


def flat(pts):
    """an outline laid onto its own best plane (Newell's normal through its middle)"""
    n = len(pts); c = [sum(p[k] for p in pts) / n for k in range(3)]
    N = newell(pts)
    return [[p[k] - N[k] * sum((p[j] - c[j]) * N[j] for j in range(3)) for k in range(3)] for p in pts]


def newell(pts):
    N = [0.0, 0.0, 0.0]
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        N[0] += (a[1] - b[1]) * (a[2] + b[2]); N[1] += (a[2] - b[2]) * (a[0] + b[0]); N[2] += (a[0] - b[0]) * (a[1] + b[1])
    L = sum(x * x for x in N) ** 0.5 or 1.0
    return [x / L for x in N]


def mfin(pts, r, color, bone=None, id="fin", mirror=False, smooth=2, rays=True, pat=None, frame=None):
    """a fin as one membrane sheet (the arguments as sealib's fin(); `bone` a name or a function of x)"""
    pts = flat(pts)
    if smooth: pts = chaikin([list(p) for p in pts], smooth)
    N = newell(pts)
    tris = _fin(pts, r, color, bone=bone, id=id, rays=rays, pat=pat, frame=frame)   # (its triangulation and rays' frame)
    key = {tuple(p): i for i, p in enumerate(pts)}
    T = []
    for q in tris:
        f = [key[tuple(q["a"])], key[tuple(q["b"])], key[tuple(q["c"])]]
        A, B, C = (pts[v] for v in f)
        cr = [(B[1] - A[1]) * (C[2] - A[2]) - (B[2] - A[2]) * (C[1] - A[1]), (B[2] - A[2]) * (C[0] - A[0]) - (B[0] - A[0]) * (C[2] - A[2]),
              (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0])]
        if sum(cr[k] * N[k] for k in range(3)) < 0: f = [f[0], f[2], f[1]]   # (every face wound to the one normal)
        T += f
    bn = [(bone(p[0]) if callable(bone) else bone) or "body" for p in pts]
    bones = sorted(set(bn), key=bn.index)
    return [S("membrane", id=id, pts=[[round(x, 5) for x in p] for p in pts], tris=T, bones=bones, skin=[bones.index(b) for b in bn],
              nrm=[[round(x, 5) for x in N]] * len(pts), r=r, color=color, pat=tris[0].get("pat"), frame=tris[0].get("frame"),
              mirror=True if mirror else None)]
