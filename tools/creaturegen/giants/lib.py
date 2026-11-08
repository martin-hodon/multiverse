# helpers to author a species' sculpt block from python
import json, os, math, copy
R = "/home/martin/store/apps/multiverse/assets/creatures/"
ORIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orig")
os.makedirs(ORIG, exist_ok=True)

def rnd(v):
    if isinstance(v, float): return round(v, 4)
    if isinstance(v, list): return [rnd(x) for x in v]
    if isinstance(v, dict): return {k: rnd(x) for k, x in v.items()}
    return v

def load(path):
    """the species JSON as it was before this rework (kept once in orig/)"""
    o = os.path.join(ORIG, path.replace("/", "_") + ".json")
    if not os.path.exists(o):
        open(o, "w").write(open(R + path + ".json").read())
    return json.load(open(o))

def save(path, d):
    d = rnd(d)
    shapes = d.get("sculpt", {}).get("shape")
    if shapes is not None:
        d["sculpt"]["shape"] = [f"@@{i}@@" for i in range(len(shapes))]
    s = json.dumps(d, indent=2, ensure_ascii=False)
    if shapes is not None:
        for i, p in enumerate(shapes):
            s = s.replace(f'"@@{i}@@"', json.dumps(p, ensure_ascii=False))
    # (short numeric arrays on one line)
    import re
    s = re.sub(r"\[\s+([-0-9.e\",*a-z\s]+?)\s+\]", lambda m: "[" + ", ".join(x.strip() for x in m.group(1).split(",")) + "]", s)
    open(R + path + ".json", "w").write(s + "\n")

class Shapes(list):
    def add(self, id, type, color, bone="body", k=0.0, **kw):
        p = {"id": id, "type": type}
        if bone != "body": p["bone"] = bone
        p.update(kw)
        p["k"] = k
        p["color"] = color if color.startswith("@") else color
        # order keys a little: id type bone geometry k kc color pat frame mirror
        self.append(p); return p
    def ell(self, id, c, r, color, bone="body", k=0.0, rot=None, **kw):
        g = {"c": c, "r": r}
        if rot: g["rot"] = rot
        return self.add(id, "ell", color, bone, k, **g, **kw)
    def sph(self, id, c, r, color, bone="body", k=0.0, **kw):
        return self.add(id, "sphere", color, bone, k, c=c, r=r, **kw)
    def cone(self, id, a, b, ra, rb, color, bone="body", k=0.0, **kw):
        return self.add(id, "cone", color, bone, k, a=a, b=b, ra=ra, rb=rb, **kw)
    def tube(self, id, pts, color, bone="body", k=0.0, **kw):
        return self.add(id, "tube", color, bone, k, pts=pts, **kw)
    def box(self, id, c, r, color, bone="body", k=0.0, round=0.05, rot=None, **kw):
        g = {"c": c, "r": r, "round": round}
        if rot: g["rot"] = rot
        return self.add(id, "box", color, bone, k, **g, **kw)
    def tri(self, id, a, b, c, r, color, bone="body", k=0.0, **kw):
        return self.add(id, "tri", color, bone, k, a=a, b=b, c=c, r=r, **kw)

def fix_order(p):
    order = ["id", "type", "bone", "c", "a", "b", "pts", "r", "ra", "rb", "rot", "k", "kc", "color", "wet", "pat", "frame", "mirror", "seat"]
    return {k: p[k] for k in order if k in p} | {k: v for k, v in p.items() if k not in order}

def arc_pts(c, R, a0, a1, n):
    return [[c[0] + R * math.cos(a0 + (a1 - a0) * i / n), c[1] + R * math.sin(a0 + (a1 - a0) * i / n)] for i in range(n + 1)]

def floorR(S, ids, m):   # (no horn thinner than about half a grid cell: below it the mesher drops pieces -- gaps, islands)
    for p in S:
        if not any(p["id"].startswith(i) for i in ids): continue
        if p["type"] == "cone": p["ra"] = max(p["ra"], m); p["rb"] = max(p["rb"], m)
        if p["type"] == "tube":
            for q in p["pts"]: q[3] = max(q[3], m)
