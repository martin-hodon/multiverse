import sys, json, copy, os
sys.path.insert(0, "/home/martin/store/apps/multiverse/tools/creaturegen/sc/carn/gen")
from lib import dumps, MAM, rnd
from rigs import RIGS
from sk import Frames, r4

def rig_only(name):
    d = {"name": name, "_about": "(rig)", **copy.deepcopy(RIGS[name]), "c": {"body": "#806040"}}
    open(MAM + name + ".json", "w").write(dumps(d))

def build(name, about, cols, shapes, eyes=None, mesh=None, shade=None, coat=None, keep=None, extra=None):
    rig_only(name)                      # (the frames are the rig's: written first)
    F = Frames(name)
    ids = [s["id"] for s in shapes]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup: raise SystemExit("duplicate ids " + str(dup))
    sc = {"keep": keep or [], "mesh": mesh or {"tris": [7000, 2300]}, "shape": [r4(F.to_rest(s)) for s in shapes]}
    if eyes: sc["eyes"] = r4(eyes)
    if shade: sc["shade"] = shade
    if coat: sc["coat"] = coat
    d = {"name": name, "_about": about, **copy.deepcopy(RIGS[name]), **(extra or {}), "c": cols, "sculpt": sc}
    open(MAM + name + ".json", "w").write(dumps(d))
    return F
