import sys, re
p = "/home/martin/store/apps/multiverse/assets/index.json"
s = open(p).read()
for n in sys.argv[1:]:
    path = f'"creatures/sea/{n}"'
    if path in s: continue
    old = '"creatures/sea/shark"'
    # (append after the last sea entry in the "Sea life" list)
    m = re.search(r'("name": "Sea life".*?"paths": \[)(.*?)(\n\s*\])', s, re.S)
    body = m.group(2)
    ind = re.search(r'\n(\s*)"', body).group(1)
    s = s[:m.end(2)] + f',\n{ind}{path}' + s[m.end(2):]
open(p, "w").write(s)
