# shp.py FILE ID KEY=JSON ... : set keys of the one-line sculpt shape {"id": ID ...} in FILE (re-read now; line layout kept)
#   KEY=null deletes the key.  --add-after=ID2 'JSON' inserts a new shape line after shape ID2 (ID is then the new shape's id).
#   --del removes the shape line.  Prints the old and the new line.
import sys, json, re
f, sid = sys.argv[1], sys.argv[2]
L = open(f).read().split("\n")
def find(i_d):
    hits = [i for i, l in enumerate(L) if re.search(r'^\s*\{"id": "%s"' % re.escape(i_d), l)]
    if len(hits) != 1: sys.exit(f"{f}: shape {i_d!r} found {len(hits)}x")
    return hits[0]
args = sys.argv[3:]
if args and args[0].startswith("--add-after="):
    i = find(args[0].split("=", 1)[1]); new = json.loads(args[1]); assert new["id"] == sid
    ind = re.match(r"\s*", L[i]).group(0)
    if not L[i].rstrip().endswith(","): L[i] = L[i].rstrip() + ","
    L.insert(i + 1, ind + json.dumps(new) + ",")
    # keep the list's last line without a trailing comma
    j = i + 1
    if j + 1 < len(L) and L[j + 1].strip().startswith("]"): L[j] = L[j].rstrip(",")
    print("ADD", L[j]); open(f, "w").write("\n".join(L)); json.load(open(f)); sys.exit()
i = find(sid)
if args and args[0] == "--del":
    print("DEL", L[i]); last = not L[i].rstrip().endswith(",")
    del L[i]
    if last: L[i - 1] = L[i - 1].rstrip().rstrip(",")
    open(f, "w").write("\n".join(L)); json.load(open(f)); sys.exit()
line = L[i]; ind = re.match(r"\s*", line).group(0); comma = line.rstrip().endswith(",")
o = json.loads(line.strip().rstrip(","))
for a in args:
    k, v = a.split("=", 1); v = json.loads(v)
    if v is None: o.pop(k, None)
    else: o[k] = v
L[i] = ind + json.dumps(o) + ("," if comma else "")
print("OLD", line.strip()[:400]); print("NEW", L[i].strip()[:400])
open(f, "w").write("\n".join(L)); json.load(open(f))
