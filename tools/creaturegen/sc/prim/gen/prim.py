import sys, json, copy, math
sys.path.insert(0, "/home/martin/store/apps/multiverse/tools/creaturegen/sc/carn/gen")
from lib import dumps, joints, MAM, rnd
from rigs import RIGS
def save_rig(name, cols, about="(rig)"):
    d = {"name": name, "_about": about, **copy.deepcopy(RIGS[name]), "c": cols}
    open(MAM + name + ".json", "w").write(dumps(d))
    return d
if __name__ == "__main__":
    for n in sys.argv[1:]:
        save_rig(n, {"body": "#806040"})
        J = joints(n)
        for k, v in J.items(): print(n, k, v)
