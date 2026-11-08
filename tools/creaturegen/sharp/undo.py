# undo.py SPECIES REGEX : the horns whose ids match put back as the backup's field shapes of those ids ($SHARP2_BACKUP:
# the copy taken before the first conversion), and any backup shape of a matching id that is now missing put back after
# the first; nothing else in the file touched
import sys, re, json, os
from sharp2 import *
sp, rx = sys.argv[1], sys.argv[2]
bk = json.load(open(os.path.join(BK, sp.replace("/", "__") + ".json")))["sculpt"]["shape"]
old = [s for s in bk if re.fullmatch(rx, s.get("id", ""))]
txt, d = load(sp); S = d["sculpt"]["shape"]
idx = [i for i, s in enumerate(S) if re.fullmatch(rx, s.get("id", ""))]
at = idx[0] if idx else len(S)
out = S[:at] + old + [s for i, s in enumerate(S) if i >= at and i not in idx]
save(sp, out, txt); print(sp, "restored", len(old), "(replacing", len(idx), ")")
