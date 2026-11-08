# tailframe.py SPECIES [ROOT_ID] (2026-11-08): a striped tail's pattern frames made CONTINUOUS. Each tail segment
# (tailSeg*, tail1Seg*, ...) had a frame of its own (`frame: {o: its start, u: its direction}`), so the stripes started
# afresh in every segment, and at the root up to five frames (the body's, the root cone's, the first segments')
# overlapped: the stripes broke into chevrons and terraces there. Now:
#   - the ROOT cone (ROOT_ID, default tailRoot) and the segments inside its reach share ONE frame (frames written alike
#     are one frame: bodymesh.js crossfades only between different ones);
#   - the rest are grouped, a few consecutive segments a frame (u: the group's chord), each frame's origin set back along
#     its u by the ARC LENGTH run so far, so the along-coordinate (what the stripes run across) is continuous from frame
#     to frame -- a crossfade between two neighbours paints the same stripe at their seam;
#   - v (where round the tail the stripes are measured from) up for all, so they all start from the top.
# Only the `frame` keys of the patterned tail shapes change (re-read right before writing; one shape a line kept).
import sys, re, math, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sharp"))
from shp import load, save, note, sub, add, mul, dot, nrm, ln, r5

sp = sys.argv[1]; root_id = sys.argv[2] if len(sys.argv) > 2 else "tailRoot"
GROUP_DEG = 12.0   # (a new frame once the direction has turned this far from the group's first segment)
txt, d = load(sp)
sh = [dict(s) for s in d["sculpt"]["shape"]]
by = {s.get("id"): s for s in sh}
segs = [s for s in sh if re.fullmatch(r"tail\d*Seg\d+", s.get("id", "")) and s.get("type") == "cone"]
key = lambda s: (int(re.match(r"tail(\d*)Seg", s["id"]).group(1) or 0), int(re.search(r"Seg(\d+)", s["id"]).group(1)))
segs.sort(key=key)
R = by.get(root_id)
r0 = (R or segs[0]).get("frame", {}).get("r", 0.05) if isinstance((R or segs[0]).get("frame"), dict) else 0.05
V = [0, 1, 0]
frames = {}
if R:
    uR = nrm(sub(R["b"], R["a"])); oR = list(R["a"]); LR = ln(sub(R["b"], R["a"]))
    FR = {"o": r5(oR), "u": r5(uR), "v": V, "r": r0}
    frames[root_id] = FR
    # (the segments that start inside the root cone's reach take its frame)
    rest = []
    for s in segs:
        if dot(sub(s["a"], oR), uR) < LR * 0.98: frames[s["id"]] = FR
        else: rest.append(s)
    s_run = dot(sub(rest[0]["a"], oR), uR) if rest else 0.0
else:
    rest = segs; s_run = 0.0
# (the rest: groups of consecutive segments, the arc length carried on)
i = 0
while i < len(rest):
    j = i; d0 = nrm(sub(rest[i]["b"], rest[i]["a"]))
    while j + 1 < len(rest) and math.degrees(math.acos(max(-1, min(1, dot(d0, nrm(sub(rest[j + 1]["b"], rest[j + 1]["a"]))))))) < GROUP_DEG: j += 1
    a, b = rest[i]["a"], rest[j]["b"]; u = nrm(sub(b, a))
    o = add(a, u, -s_run)   # (the along-coordinate at the group's start = the arc length so far)
    F = {"o": r5(o), "u": r5(u), "v": V, "r": r0}
    for k in range(i, j + 1):
        frames[rest[k]["id"]] = F
    # (the arc length: the segments' own lengths -- black rings without a pattern included)
    s_run += sum(ln(sub(rest[k]["b"], rest[k]["a"])) for k in range(i, j + 1))
    i = j + 1
n = 0
for s in sh:
    if s.get("id") in frames and s.get("pat"):
        s["frame"] = frames[s["id"]]; n += 1
txt2, d2 = load(sp)
if [x.get("id") for x in d2["sculpt"]["shape"]] != [x.get("id") for x in sh]: sys.exit("the shape list changed meanwhile: re-run")
cur = {x["id"]: x for x in d2["sculpt"]["shape"] if x.get("id")}
out = [dict(cur[s["id"]], frame=s["frame"]) if s.get("id") in frames and s.get("pat") else cur.get(s.get("id"), s) for s in sh]
save(sp, out, txt2)
note(sp, "(2026-11-08, tailframe.py)", "The tail's stripe frames CONTINUOUS (tools/creaturegen/var/tailframe.py): the root cone and the "
     "segments inside it one frame, the rest a frame per few segments, each frame's origin set back by the arc length so "
     "the stripes run on across every seam, all measured from the top -- they broke into chevrons at the tail's root, "
     "each segment's stripes started afresh.")
print(sp, "frames set on", n, "shapes,", len({id(f) for f in frames.values()}), "frames")
