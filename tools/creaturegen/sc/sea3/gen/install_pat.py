# installs a generated pattern block into coatpat.js (before coatAt; replacing its earlier version), its dispatch
# lines in coatAt, its function in coatAt's dependencies, and its names in bodyspec.js PATS -- re-reading both files
# usage: install_pat.py BLOCK.js "START" "END" '{"dispatch": [...], "deps": [...], "pats": "seal: 60, greyseal: 61", "patcomment": "..."}'
import sys, json
P = "/home/martin/store/apps/multiverse/coatpat.js"
B = "/home/martin/store/apps/multiverse/bodyspec.js"
blk, start, end = open(sys.argv[1]).read().rstrip("\n") + "\n", sys.argv[2], sys.argv[3]
o = json.loads(sys.argv[4])
s = open(P).read()
if start in s:
    a = s.index(start); b = s.index(end, a) + len(end)
    s = s[:a] + blk.rstrip("\n") + s[b:]
else:
    m = "export const coatAt = wgslFn(`"
    assert s.count(m) == 1
    s = s.replace(m, blk + m)
for line in o["dispatch"]:
    if line.strip() not in s:
        m = "    if (id > 2.5 && id < 4.5) {"
        assert s.count(m) == 1
        s = s.replace(m, line + "\n" + m)
tail = ", patternAt]);"
assert s.count(tail) == 1
for dep in o["deps"]:
    i = s.index("export const coatAt"); j = s.index(tail, i)
    if (", " + dep + ",") not in s[i:j + len(tail)] and (", " + dep + tail) not in s[i:]:
        s = s[:j] + ", " + dep + s[j:]
open(P, "w").write(s)
print("installed", sys.argv[1])
