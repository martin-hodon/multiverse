#!/usr/bin/env python3
"""FLIGHT NECKS (2026-11-08): a long-necked bird flies with its neck held nearly STRAIGHT out ahead, sagging a little --
the swan, the goose, the cranes, the storks, the flamingo, the ibis, the spoonbill (not the heron: it flies with its neck
folded back). Their necks are S-shaped at rest, and a bone turned rigidly keeps the S of the stretch it carries, so
turning the neck bones aloft (`flyRot`) alone drew a wave with a kink behind the head.

Each neck `sweep` (necks.py) is skinned here so its turn is shared out ALONG it (bodyspec.js sweepSkin):
  bones   ["body", "neck", ...]: its root handed from the body to the neck, not torn off it (the lumpy join)
  knotsAt where along it (shares of its length) each bone takes over: on the rest curve's own bends, not at the joints
          (a stretch rides its bone rigidly wherever the joint is; at rest nothing moves)
  spread  each hand-off widened to that share of the stretch to its neighbour: the turn grows along the neck
and the parts' `flyRot` [0, 0, z] (the neck bones' and the head's turn aloft, about z) set with them. The numbers were
searched together (scratchpad sweep/fly/opt2.mjs: the flight centreline skinned through skeleton.js's flight pose, its
stretches from -6 degrees at the root to +2 at the head -- a slight sag -- with as little turn between them as can be,
the bill 12 degrees below level).

The FLAMINGO's two neck bones could not undo its long double curve: a `neck3` part is inserted halfway between neck2 and
the head (the head re-parented on it, its offset halved), so its neck has three like the swan's.

  python3 flynecks.py [SPECIES ...]     (default: all of them; idempotent; RE-RUN after necks.py or a generator)"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from necks import about, ROOT

FLY = {
    "swan":      dict(bones=["body", "neck", "neck2", "neck3"], knotsAt=[0.045, 0.272, 0.758], spread=1.2,
                      flyRot={"neck": -72.5, "neck2": -24, "neck3": 45.5, "head": 55.5}),
    "goose":     dict(bones=["body", "neck", "neck2"], knotsAt=[0.025, 0.21], spread=1.05,
                      flyRot={"neck": -69, "neck2": -12.5, "head": 63}),
    "crane":     dict(bones=["body", "neck", "neck2"], knotsAt=[0.025, 0.205], spread=1.2,
                      flyRot={"neck": -71.5, "neck2": -7.5, "head": 68.5}),
    "stork":     dict(bones=["body", "neck", "neck2"], knotsAt=[0.025, 0.24], spread=1.2,
                      flyRot={"neck": -66.5, "neck2": -9, "head": 72.5}),
    "flamingo":  dict(bones=["body", "neck", "neck2", "neck3"], knotsAt=[0.115, 0.21, 0.82], spread=1.2,
                      flyRot={"neck": -84.5, "neck2": -17, "neck3": 45, "head": 72.5}),
    "ibis":      dict(bones=["body", "neck", "neck2"], knotsAt=[0.025, 0.505], spread=0.84,
                      flyRot={"neck": -51.5, "neck2": -20.5, "head": 87.5}),
    "spoonbill": dict(bones=["body", "neck", "neck2"], knotsAt=[0.035, 0.235], spread=1.2,
                      flyRot={"neck": -65.5, "neck2": -12, "head": 64}),
}
NOTE = (" (2026-11-08, tools/creaturegen/sweep/flynecks.py) ALOFT the neck is held nearly straight ahead with a slight"
        " sag: the neck sweep is skinned from the body along its bones with its hand-offs on the rest curve's bends"
        " (`knotsAt`, `spread`), and the neck bones' and head's `flyRot` set with them.")

def fmt(x): return json.dumps(x)

def run(sp):
    F = FLY[sp]
    path = os.path.join(ROOT, "assets/creatures/birds", sp + ".json")
    L = open(path).read().split("\n")
    ids = {}
    for i, l in enumerate(L):
        m = re.match(r'\s*\{"id": "([a-z0-9]+)", "parent"', l)
        if m: ids[m.group(1)] = i
    # (the flamingo's third neck bone, halfway from neck2 to the head)
    if "neck3" in F["bones"] and "neck3" not in ids:
        i = ids["head"]; h = json.loads(L[i].rstrip().rstrip(","))
        assert h["parent"] == "neck2" and "rot" not in h, sp + ": head not on neck2 as expected"
        half = [round(v / 2, 4) for v in h["pos"]]
        L[i] = L[i].replace('"parent": "neck2"', '"parent": "neck3"').replace('"pos": ' + fmt(h["pos"]), '"pos": ' + fmt(half))
        L.insert(i, '    {"id": "neck3", "parent": "neck2", "shape": "sphere", "size": {"r": 0.022}, "pos": ' + fmt(half) +
                 ', "color": "#f4b0b6", "anim": {"axis": "z", "deg": 5, "speed": 0.3, "phase": 1.5}},')
        return run_lines(sp, path, L)
    return run_lines(sp, path, L)

def run_lines(sp, path, L):
    F = FLY[sp]
    for part, z in F["flyRot"].items():
        i = next(k for k, l in enumerate(L) if re.match(r'\s*\{"id": "%s", "parent"' % part, l))
        new = '"flyRot": ' + fmt([0, 0, z])
        if '"flyRot": [' in L[i]: L[i] = re.sub(r'"flyRot": \[[^\]]*\]', new, L[i])
        else: L[i] = re.sub(r'\}(,?)\s*$', ', ' + new + r'}\1', L[i])
    i = next(k for k, l in enumerate(L) if '"id": "neck", "type": "sweep"' in l)
    l = re.sub(r'"bones": \[[^\]]*\]', '"bones": ' + fmt(F["bones"]), L[i])
    l = re.sub(r', "knotsAt": \[[^\]]*\]', '', l); l = re.sub(r', "spread": [0-9.]+', '', l)
    l = l.replace('"pts": ', '"knotsAt": %s, "spread": %s, "pts": ' % (fmt(F["knotsAt"]), F["spread"]), 1)
    L[i] = l
    txt = "\n".join(L); json.loads(txt); open(path, "w").write(txt)
    about("birds/" + sp, NOTE)
    print(sp, "done")

if __name__ == "__main__":
    for sp in [a for a in sys.argv[1:] if not a.startswith("--")] or list(FLY): run(sp)
