# rehead.py FILE FIRST_ID LAST_ID NEW.py : replace the contiguous shape lines FIRST..LAST with the list SHAPES built by NEW.py
#   (NEW.py sees FR = {"pat": "scales", "frame": ...} copied from FIRST's line). Re-reads FILE now; validates the JSON.
import sys, json, re
f, a, b, src = sys.argv[1:5]
L = open(f).read().split("\n")
def find(i_d):
    hits = [i for i, l in enumerate(L) if re.search(r'^\s*\{"id": "%s"' % re.escape(i_d), l)]
    if len(hits) != 1: sys.exit(f"{f}: shape {i_d!r} found {len(hits)}x")
    return hits[0]
i, j = find(a), find(b); assert i <= j
first = json.loads(L[i].strip().rstrip(",")); ind = re.match(r"\s*", L[i]).group(0); comma = L[j].rstrip().endswith(",")
FR = {k: first[k] for k in ("pat", "frame") if k in first}
g = {"FR": FR}; exec(open(src).read(), g); S = g["SHAPES"]
new = [ind + json.dumps(s) + "," for s in S]
if not comma: new[-1] = new[-1].rstrip(",")
L[i:j + 1] = new
open(f, "w").write("\n".join(L)); json.load(open(f)); print(f"replaced {j - i + 1} lines with {len(new)}")
