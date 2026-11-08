import json, math
R = "/home/martin/store/apps/multiverse/assets/creatures/"
def rnd(v):
    if isinstance(v, float): return round(v, 4)
    if isinstance(v, list): return [rnd(x) for x in v]
    if isinstance(v, dict): return {k: rnd(x) for k, x in v.items()}
    return v
def dump(path, d):
    # one shape / part per line, like tiger.json
    def line(x): return json.dumps(rnd(x), separators=(", ", ": "))
    out = ["{"]
    keys = list(d.keys())
    for i, k in enumerate(keys):
        v = d[k]; comma = "," if i < len(keys) - 1 else ""
        if k == "parts":
            out.append(f'  "parts": [\n' + ",\n".join("    " + line(p) for p in v) + f"\n  ]{comma}")
        elif k == "sculpt":
            sk = list(v.keys()); inner = []
            for j, kk in enumerate(sk):
                vv = v[kk]; c2 = "," if j < len(sk) - 1 else ""
                if kk == "shape":
                    inner.append('    "shape": [\n' + ",\n".join("      " + line(p) for p in vv) + f"\n    ]{c2}")
                else:
                    inner.append(f'    "{kk}": {line(vv)}{c2}')
            out.append('  "sculpt": {\n' + "\n".join(inner) + f"\n  }}{comma}")
        else:
            out.append(f'  "{k}": {line(v)}{comma}')
    out.append("}")
    open(R + path, "w").write("\n".join(out) + "\n")
def add(a, b, t=1): return [a[i] + b[i] * t for i in range(3)]
def lerp(a, b, t): return [a[i] + (b[i] - a[i]) * t for i in range(3)]
def mz(v): return [v[0], v[1], -v[2]] + list(v[3:])
