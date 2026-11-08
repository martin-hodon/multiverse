# bg.py -- helpers for authoring the birds' sculpt overlays (written into the species JSON; the JSON is the source of truth)
import json, math, os
R = "/home/martin/store/apps/multiverse/assets/creatures/birds/"

def rnd(v, d=4):
    if isinstance(v, float): return round(v, d)
    if isinstance(v, list): return [rnd(x, d) for x in v]
    if isinstance(v, dict): return {k: rnd(x, d) for k, x in v.items()}
    return v

def S(t, id, color, bone="body", **kw):
    d = {"id": id, "type": t}
    if bone != "body": d["bone"] = bone
    d.update(kw); d["color"] = color
    return d

def ell(id, c, r, color, k=.02, bone="body", rot=None, mirror=False, **kw):
    d = S("ell", id, color, bone, c=c, r=r, **({"rot": rot} if rot else {}), k=k, **kw)
    if mirror: d["mirror"] = True
    return d

def sph(id, c, r, color, k=.01, bone="body", mirror=False, **kw):
    d = S("sphere", id, color, bone, c=c, r=r, k=k, **kw)
    if mirror: d["mirror"] = True
    return d

def tube(id, pts, color, k=.01, bone="body", mirror=False, **kw):
    d = S("tube", id, color, bone, pts=pts, k=k, **kw)
    if mirror: d["mirror"] = True
    return d

def cone(id, a, b, ra, rb, color, k=.005, bone="body", mirror=False, **kw):
    d = S("cone", id, color, bone, a=a, b=b, ra=ra, rb=rb, k=k, **kw)
    if mirror: d["mirror"] = True
    return d

def row(at, to, w, bone=None, up=None):
    r = {"at": at, "to": to, "w": w}
    if bone: r["bone"] = bone
    if up: r["up"] = up
    return r

def fea(id, rows, n, color, tip, outline="round", bone="body", mirror=False, **kw):
    d = {"id": id, "type": "feathers"}
    if bone != "body": d["bone"] = bone
    d.update({"rows": rows, "n": n, "outline": outline}); d.update(kw)
    d["color"] = color; d["tip"] = tip
    if mirror: d["mirror"] = True
    return d

def add(a, b, t=1): return [x + y * t for x, y in zip(a, b)]
def sub(a, b): return [x - y for x, y in zip(a, b)]
def lerp(a, b, t): return [x + (y - x) * t for x, y in zip(a, b)]
def nrm(v): l = math.sqrt(sum(x * x for x in v)) or 1; return [x / l for x in v]
def rotz(v, deg): a = math.radians(deg); c, s = math.cos(a), math.sin(a); return [v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2]]

def fan(root, dirs, lens, w, side_off=None):
    """rows from one root (or a list of roots) out along dirs (unit-ish), each its own length"""
    out = []
    for i, (d, L) in enumerate(zip(dirs, lens)):
        at = root[i] if isinstance(root[0], list) else root
        out.append(row(at, add(at, nrm(d), L), w[i] if isinstance(w, list) else w))
    return out

# ---- writing: the JSON laid out like tiger.json (a shape per line) -------------------------------------------------
def one(v): return json.dumps(rnd(v), separators=(", ", ": "))
def fmt(v, ind=0, key=None):
    p = "  " * ind
    if isinstance(v, dict):
        if not v: return "{}"
        if key in ("shape",) or "type" in v and "id" in v or ("id" in v and "shape" in v and "parent" in v) or key in ("size", "anim", "eyes", "mesh", "flags", "fly", "swim", "dot", "rows"):
            return one(v)
        return "{\n" + ",\n".join(f'{p}  {json.dumps(k)}: {fmt(x, ind + 1, k)}' for k, x in v.items()) + "\n" + p + "}"
    if isinstance(v, list):
        if all(not isinstance(x, (dict, list)) for x in v) or all(isinstance(x, list) and all(not isinstance(y, (dict, list)) for y in x) for x in v):
            return one(v)
        return "[\n" + ",\n".join(f"{p}  {fmt(x, ind + 1)}" for x in v) + "\n" + p + "]"
    return one(v)

def load(name): return json.load(open(R + name + ".json"))
def save(name, d, root=True):
    open(R + name + ".json", "w").write(fmt(d) + "\n")
    if root: root_feathers(name, d)

# ---- THE ROOTS: every feather blade's root sunk into the body (the post-pass of every generator's save) ---------------
# rootfix.mjs builds the bird as the game does, lays each blade as bodymesh.js does, and measures its root against the
# body's field; each authored row whose blades stand off it has its `at` moved in along the field's normal to `pen` inside
# (its `to` kept, so the tip stays put and only the root tilts in). Repeated until no blade stands off (or `tries` runs out).
RF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rootfix.mjs")
def root_feathers(name, d=None, tries=30, pen=.0025, quiet=False):
    import subprocess, tempfile
    d = d if d is not None else load(name)
    nm = d.get("name", name); fn = name.split("/")[-1]; moved = 0
    for q in d.get("sculpt", {}).get("shape", []):   # (a LAYER group: a row per blade, each blade's own, laid exactly where
        if False and q.get("type") == "feathers" and q.get("layer") and len(q["rows"]) != q["n"] and len(q["rows"]) > 1 and not any("bone" in r or "up" in r for r in q["rows"]):
            rs, n = q["rows"], q["n"]; out = []   #  bodymesh.js lays it between two rows -- so its root moves alone)
            for j in range(n):
                x = j / (n - 1) * (len(rs) - 1); i0 = min(len(rs) - 2, int(x)); t = x - i0; A, B_ = rs[i0], rs[i0 + 1]
                dA, dB = sub(A["to"], A["at"]), sub(B_["to"], B_["at"]); lA, lB = math.sqrt(sum(v * v for v in dA)), math.sqrt(sum(v * v for v in dB))
                at = lerp(A["at"], B_["at"], t); dv = nrm(lerp(nrm(dA), nrm(dB), t)); L = lA + (lB - lA) * t
                out.append({"at": [round(v, 4) for v in at], "to": [round(v, 4) for v in add(at, dv, L)], "w": round(A["w"] + (B_["w"] - A["w"]) * t, 4)})
            q["rows"] = out; open(R + name + ".json", "w").write(fmt(d) + "\n")
    for it in range(tries):
        tf = tempfile.NamedTemporaryFile(suffix=".json", delete=False).name
        out = subprocess.run(["node", RF, nm, "--patch=" + tf, "--pen=%g" % pen], capture_output=True, text=True).stdout
        P = json.load(open(tf)).get(fn, {}); os.unlink(tf)
        if not P: break
        sh = d["sculpt"]["shape"]
        for j, rows in P.items():
            fid, occ = j.rsplit("@", 1)
            S_ = [q for q in sh if q.get("type") == "feathers" and q.get("id") == fid]
            if len(S_) <= int(occ): print("  roots: %s -- feathers %r not in the JSON, left alone" % (nm, j)); continue
            for ri, mv in rows.items():
                r = S_[int(occ)]["rows"][int(ri)]
                r["at"] = [round(a + m, 4) for a, m in zip(r["at"], mv)] + r["at"][3:]; moved += 1
        open(R + name + ".json", "w").write(fmt(d) + "\n")
    if not quiet: print("  roots: %s -- %d row moves; %s" % (nm, moved, " ".join(out.split()[1:]) if out else "?"))
    return d

def shift(shapes, dv, scale=1.0, about=None):
    """move (and scale about `about`) authored shapes: points, radii"""
    about = about or [0, 0, 0]
    P = lambda p: [about[k] + (p[k] - about[k]) * scale + dv[k] for k in range(3)] + list(p[3:4] and [p[3] * scale] or [])
    out = []
    for s in shapes:
        s = json.loads(json.dumps(s))
        for k in ("c", "a", "b"):
            if k in s: s[k] = P(s[k])
        if "pts" in s: s["pts"] = [P(p) for p in s["pts"]]
        if "rows" in s:
            for r in s["rows"]:
                r["at"] = P(r["at"]); r["to"] = P(r["to"]); r["w"] *= scale
        for k in ("r", "ra", "rb", "k", "kc", "lift", "stagger"):
            if k in s: s[k] = [x * scale for x in s[k]] if isinstance(s[k], list) else s[k] * scale
        out.append(s)
    return out

# ---- the field, roughly (smooth union of the solid shapes): to lay feathers ON the surface, not inside it ----------
def _R(rot):
    ax, ay, az = [math.radians(a) for a in rot]
    a, b, c, dd, e, f = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    # three.js Euler XYZ: rows of the matrix
    return [[c * e, -c * f, dd], [a * f + b * e * dd, a * e - b * f * dd, -b * c], [b * f - a * e * dd, b * e + a * f * dd, a * c]]

def _seg(p, a, b, ra, rb):
    ab = sub(b, a); L2 = sum(x * x for x in ab) or 1e-12
    t = max(0, min(1, sum((p[k] - a[k]) * ab[k] for k in range(3)) / L2))
    q = [a[k] + ab[k] * t for k in range(3)]
    return math.dist(p, q) - (ra + (rb - ra) * t)

def sdf1(s, p):
    t = s["type"]
    if t == "sphere": return math.dist(p, s["c"]) - s["r"]
    if t == "ell":
        R = _R(s.get("rot", [0, 0, 0])); v = sub(p, s["c"])
        l = [sum(R[i][j] * v[i] for i in range(3)) for j in range(3)]   # R^T v
        r = s["r"]; q = math.sqrt(sum((l[k] / r[k]) ** 2 for k in range(3)))
        return (q - 1) * min(r)
    if t == "cone": return _seg(p, s["a"], s["b"], s["ra"], s["rb"])
    if t == "tube":
        P = s["pts"]; return min(_seg(p, P[i][:3], P[i + 1][:3], P[i][3], P[i + 1][3]) for i in range(len(P) - 1))
    return 1e9

def field(shapes, p, bones=None):
    dd = 1e9
    for s in shapes:
        if s["type"] == "feathers" or s.get("op") == "sub" or (bones and s.get("bone", "body") not in bones): continue
        x = sdf1(s, p); k = max(s.get("k", 0), 1e-6)
        h = max(k - abs(dd - x), 0) / k
        dd = min(dd, x) - h * h * k * .25
    return dd

def settle(shapes, fe, dirn, margin, bones=None):
    """each row's root and tip pushed along dirn until they stand `margin` off the surface"""
    dirn = nrm(dirn)
    def out(p):
        p = list(p)
        for _ in range(400):
            if field(shapes, p, bones) >= margin: return p
            p = add(p, dirn, .001)
        return p
    for r in fe["rows"]:
        r["at"] = out(r["at"]); r["to"] = out(r["to"])
    return fe

def place(sh, ids, dirn, margin, mir=True):
    """settle the named feather groups of `sh` (in place)"""
    for s in sh:
        if s.get("type") == "feathers" and s["id"] in ids:
            settle(sh, s, dirn, margin)

# ---- a FOLDED wing laid along the flank (the left; mirrored): from its bend S back to the primaries' tips over the tail
#      base T; H its depth at the front. Four tracts from the bend back -- coverts (lesser and median), greater coverts,
#      secondaries (and tertials), primaries -- each overlapping the next like tiles, the primaries lowest, their tips
#      crossing over the tail; the feathers' ends darker (tip) so the wing's edges read against the flank ----
def grad(shapes, p, e=.002):
    g = [field(shapes, add(p, [e if k == i else 0 for k in range(3)], 1), None) - field(shapes, add(p, [-e if k == i else 0 for k in range(3)], 1), None) for i in range(3)]
    return nrm(g)

def conform(shapes, fe, margin):
    """each row's root and tip pushed out along the surface's own normal there to `margin` off it, and the row's up that
       normal (the blade lies along the surface, not as a plate standing off a curved flank)"""
    def out(p):
        p = list(p)
        for _ in range(400):
            f = field(shapes, p)
            if f >= margin: return p
            p = add(p, grad(shapes, p), max(.0005, min(.002, margin - f)))
        return p
    for r in fe["rows"]:
        r["at"] = out(r["at"]); r["to"] = out(r["to"])
        g = nrm(add(grad(shapes, r["at"]), grad(shapes, r["to"]), 1))
        r["up"] = [round(v, 4) for v in g]
    return fe

def rig_fold(d, S, speed=.9, beat=44, hind=None, neck=None, yaw=90, roll=90, dih=8, trail=0, H=None, reach=0, sweep=25, flyTurn=None, px=0, ext=0, lift=None, fwd=0, iturn=0):
    """FLIGHT for a bird that walks or swims: its folded wing (fold_wing(..., bone="wrollL")) swung out aloft. wingL at the
       wing's bend S beats (a flutter too small to see on the ground, `beat` times deeper aloft); on it wfoldL turns the
       wing's tip out from the tail to square across (flyRot about y) and wrollL lays it flat (about the wing's own length),
       its top edge -- the coverts' -- leading. Only the asset viewer's fly (and a mount) takes it up: aloft the species'
       `flight` holds the arm where it is (arm 0) and the legs trail (hind)"""
    body = next(p for p in d["parts"] if p["id"] == "body")
    bp = body["pos"]
    out = []
    for p in d["parts"]:
        if p["id"].startswith(("wfold", "wroll", "wtip", "wext", "wlift", "wfwd", "witurn")): continue
        out.append(p)
        if p["id"] in ("wingL", "wingR"):
            s = p["id"][-1]; sg = 1 if s == "L" else -1
            p["pos"] = [round(S[0] - bp[0], 4), round(S[1] - bp[1], 4), round(S[2] * sg, 4)]
            p.pop("pivot", None); p.pop("rot", None)
            p["anim"] = {"axis": "x", "deg": .5 * sg, "speed": speed, "phase": 0, "wing": True}
            p["fold"] = [0, 0, 0]
            out.append({"id": "wfold" + s, "parent": p["id"], "shape": "sphere", "size": {"r": .005}, "color": p.get("color", "#808080"), "pos": [0, 0, 0],
                        "flyRot": [0, yaw * sg, 0], "fold": [0, 0, 0]})
            out.append({"id": "wroll" + s, "parent": "wfold" + s, "shape": "sphere", "size": {"r": .005}, "color": p.get("color", "#808080"), "pos": [0, 0, 0],
                        "flyRot": [roll * sg, 0, 0], "fold": [0, 0, 0]})
            par, off = "wroll" + s, [0, 0]
            if ext:   # (the whole folded wing slid `ext` m further out aloft -- a pure translation: +90 about z at one point, -90
                      #  about z at a child half-way out -- the gap behind it filled by fold_wing's hidden inner arm feathers)
                out.append({"id": "wextA" + s, "parent": "wroll" + s, "shape": "sphere", "size": {"r": .005}, "color": p.get("color", "#808080"),
                            "pos": [0, 0, 0], "flyRot": [0, 0, 90], "fold": [0, 0, 0]})
                out.append({"id": "wextB" + s, "parent": "wextA" + s, "shape": "sphere", "size": {"r": .005}, "color": p.get("color", "#808080"),
                            "pos": [round(ext / 2, 4), round(ext / 2, 4), 0], "flyRot": [0, 0, -90], "fold": [0, 0, 0]})
                par, off = "wextB" + s, [ext / 2, ext / 2]
            if lift:   # (lift = (s, up): the hidden inner feathers raised s along the fold's up aloft, level with the slid wing --
                       #  again a pure translation, +-90 about x)
                ls_, u = lift[0], nrm(list(lift[1])); vy, vz = ls_ * (u[2] - u[1]) / 2, -ls_ * (u[1] + u[2]) / 2
                out.append({"id": "wliftA" + s, "parent": "wroll" + s, "shape": "sphere", "size": {"r": .005}, "color": p.get("color", "#808080"),
                            "pos": [0, 0, 0], "flyRot": [90 * sg, 0, 0], "fold": [0, 0, 0]})
                out.append({"id": "wliftB" + s, "parent": "wliftA" + s, "shape": "sphere", "size": {"r": .005}, "color": p.get("color", "#808080"),
                            "pos": [0, round(vy, 4), round(vz * sg, 4)], "flyRot": [-90 * sg, 0, 0], "fold": [0, 0, 0]})
                if fwd:   # (and slid back `fwd` aloft: they lie that much further forward at rest, where the body is deep enough to hide them)
                    out.append({"id": "wfwdA" + s, "parent": "wliftB" + s, "shape": "sphere", "size": {"r": .005}, "color": p.get("color", "#808080"),
                                "pos": [0, 0, 0], "flyRot": [0, 0, 90], "fold": [0, 0, 0]})
                    out.append({"id": "wfwdB" + s, "parent": "wfwdA" + s, "shape": "sphere", "size": {"r": .005}, "color": p.get("color", "#808080"),
                                "pos": [round(fwd / 2, 4), round(fwd / 2, 4), 0], "flyRot": [0, 0, -90], "fold": [0, 0, 0]})
                if iturn:   # (aloft, the inner feathers turned `iturn` deg about the shoulder in the wing's plane: at rest they follow
                            #  the fold's slope to stay hidden, aloft they point straight out like the slid wing, not swept back)
                    out.append({"id": "witurn" + s, "parent": "wliftB" + s, "shape": "sphere", "size": {"r": .005}, "color": p.get("color", "#808080"),
                                "pos": [0, round(-vy, 4), round(-vz * sg, 4)], "flyRot": [0, 0, iturn], "fold": [0, 0, 0]})
            if reach:   # (the primaries, on wtipL: swung about a point `reach` m behind the spread wing, so aloft they
                        #  slide out past the folded wing's end -- the span longer by about reach * sin(sweep) -- and sweep back)
                out.append({"id": "wtip" + s, "parent": par, "shape": "sphere", "size": {"r": .005}, "color": p.get("color", "#808080"),
                            "pos": [round(px - off[0], 4), round(-(H + reach) - off[1], 4), 0], "flyRot": [0, 0, sweep], "fold": [0, 0, 0]})
    d["parts"] = out
    for p in out:   # (a wader's legs -- swinging parts, not IK -- trail straight back aloft)
        if p["id"] in ("legL", "legR"):
            if trail: p["flyRot"] = [0, 0, -trail]
            else: p.pop("flyRot", None)
    for p in out:   # (and any part's own turn aloft: a neck reaching straight forward, the head levelled on it)
        if flyTurn and p["id"] in flyTurn: p["flyRot"] = [0, 0, flyTurn[p["id"]]]
    fl = {"arm": 0, "hand": 0, "beat": beat, "bob": .03}
    if hind: fl["hind"] = hind
    if neck is not None: fl["neck"] = neck
    d.pop("flight", None)
    d.setdefault("flags", {})["flight"] = fl   # (a "parts" creature keeps only its flags beside the parts: creatures.js)

def fold_wing(sh, S, T, H, w, cols, n=(7, 7, 8, 7), up=(0, .25, 1), base=.003, step=.0025, bars=None, prim_out=None, flush=False, bone=None, pbone=None, proot=.38, ebone=None, inner=None):
    up = nrm(list(up)); L = S[0] - T[0]
    def line(x, y0, y1, k, slant=.14):   # (each tract's root line leaning back as it goes down the wing)
        return [[x - slant * L * i / (k - 1), y0 + (y1 - y0) * i / (k - 1), S[2]] for i in range(k)]
    out = []
    def tract(id, roots, tos, ww, nn, col, tip, outline="round", **kw):
        rows = [row(a, b, ww) for a, b in zip(roots, tos)]
        bn = (pbone or ebone or bone) if id == "prim" else (ebone or bone)
        out.append(fea(id, rows, nn, col, tip, outline=outline, up=list(up), camber=.14, curve=-.02, stagger=.0012, mirror=True, **({"bone": bn} if bn else {}), **kw))
    # primaries: from the wing's lower middle, all toward the tip (a little spread), stacked
    pr = line(S[0] - proot * L, S[1] - .45 * H, S[1] - .72 * H, 3)   # (proot: how far up under the coverts they start -- their overlap, so a reach aloft stays attached)
    tip = [T[0], T[1], T[2]]
    tract("prim", pr, [add(tip, [.015 * i, .012 * (1 - i), -.006 * i]) for i in range(3)], w * .9, n[3], cols["prim"], cols.get("primTip", cols["prim"]),
          outline="flight", seed=31, **({"bars": bars} if bars else {}))
    # secondaries: the rear half, from high to the lower edge, back and a little up
    sr = line(S[0] - .3 * L, S[1] - .08 * H, S[1] - .86 * H, 3)
    tract("sec", sr, [add(r, nrm([-1, .12 + .1 * i, -.08]), .42 * L) for i, r in enumerate(sr)], w, n[2], cols["sec"], cols.get("secTip", cols["sec"]), seed=32,
          **({"bars": bars} if bars else {}))
    # greater coverts: a band across the middle
    gr = line(S[0] - .14 * L, S[1] - .02 * H, S[1] - .7 * H, 3)
    tract("gcov", gr, [add(r, nrm([-1, .05, -.05]), .3 * L) for r in gr], w * .95, n[1], cols["gcov"], cols.get("gcovTip", cols["gcov"]), seed=33)
    # lesser and median coverts: the front, small, from the bend
    cr = line(S[0], S[1], S[1] - .62 * H, 3)
    tract("cov", cr, [add(r, nrm([-1, -.05, -.05]), .24 * L) for r in cr], w * .85, n[0], cols["cov"], cols.get("covTip", cols["cov"]), seed=34)
    if inner:   # (the arm's own coverts and secondaries, for the wider span aloft: laid along the fold's first `len` m but sunk
                #  `inset` inside the body, so at rest they are hidden under the folded wing; aloft (on `bone`, not slid out) they fill
                #  the arm between the body and the slid-out folded wing)
        Li, ins, sl = inner["len"], inner["inset"], (T[1] - S[1]) / L
        fw, un = inner.get("fwd", 0), nrm(list(up))
        def at(dx, h): return add([S[0] - dx + fw, S[1] + sl * dx - h * H, S[2] + (T[2] - S[2]) * dx / L], un, 0)
        ins_tr = []
        hS = inner.get("h", (.15, .95))
        ic = inner.get("cols", {})
        for id, h0, h1, ln, nn, ww, col in (("inSec", hS[0], hS[1], Li, inner["n"][1], inner["w"], ic.get("sec", cols["sec"])),
                                              ("inCov", 0, .55, .6 * Li, inner["n"][0], inner["w"] * .9, ic.get("cov", cols["cov"]))):
            hs = [h0 + (h1 - h0) * i / 2 for i in range(3)]
            rows = [row(at(.02 * L, h), at(.02 * L + ln, h + .06), ww) for h in hs]
            ins_tr.append(fea(id, rows, nn, col, ic.get("tip", col), outline="round", up=list(up), camber=.1, curve=-.01, stagger=.0012, mirror=True,
                              bone=inner.get("bone", bone or "body"), seed=41 + len(ins_tr), **inner.get("kw", {})))
        def deep(q):   # (the deepest point on the line in along -up: from there settled out to -inset)
            return min((add(q, un, -.002 * i) for i in range(100)), key=lambda p: field(sh, p))
        for s_ in ins_tr:
            for r in s_["rows"]: r["at"], r["to"] = deep(r["at"]), deep(r["to"])
            settle(sh, s_, up, -ins)
            for r in s_["rows"]:
                for q in (r["at"], r["to"]):
                    if ins > 0 and field(sh, q) > -ins * .6: print("  WARN inner row out of the body", s_["id"], [round(v, 3) for v in q], round(field(sh, q), 4))
        sh += ins_tr
    sh += out
    # (laid on the surface in order: each tract over the one before it)
    for j, s in enumerate(out):
        if flush: conform(sh, s, base + step * j)
        else: settle(sh, s, up, base + step * j)
    return out
