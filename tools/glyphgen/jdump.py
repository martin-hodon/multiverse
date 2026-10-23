# compact JSON: indent 1, but a list of numbers (or of short number lists) on one line -- point lists stay readable
import json
def _inline(v):
    if isinstance(v, list) and all(isinstance(x, (int, float)) for x in v): return True
    if isinstance(v, list) and all(isinstance(x, list) and all(isinstance(y, (int, float)) for y in x) for x in v) and len(v) <= 40: return True
    return False
def num(x):
    if isinstance(x, float):
        r = round(x, 2)
        return str(int(r)) if r == int(r) else repr(r)
    return json.dumps(x)
def dumps(v, ind=0):
    pad = " " * (ind + 1)
    if isinstance(v, dict):
        if not v: return "{}"
        if all(not isinstance(x, (dict, list)) for x in v.values()) and len(json.dumps(v)) < 110:
            return "{ " + ", ".join(f"{json.dumps(k)}: {num(x) if isinstance(x,(int,float)) and not isinstance(x,bool) else json.dumps(x, ensure_ascii=False)}" for k, x in v.items()) + " }"
        return "{\n" + ",\n".join(f"{pad}{json.dumps(k)}: {dumps(x, ind + 1)}" for k, x in v.items()) + "\n" + " " * ind + "}"
    if isinstance(v, list):
        if _inline(v):
            return "[" + ", ".join(("[" + ", ".join(num(y) for y in x) + "]") if isinstance(x, list) else num(x) for x in v) + "]"
        return "[\n" + ",\n".join(pad + dumps(x, ind + 1) for x in v) + "\n" + " " * ind + "]"
    if isinstance(v, bool) or v is None: return json.dumps(v)
    if isinstance(v, (int, float)): return num(v)
    return json.dumps(v, ensure_ascii=False)
def write(path, v):
    open(path, "w").write(dumps(v) + "\n")
