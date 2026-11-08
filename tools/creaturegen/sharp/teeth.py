# teeth.py SPECIES... | all : TEETH and FANGS made the engine's `horn` (sharp.js), one per field cone, the same id, bone,
# colour, mirror: the root sunk into the jaw (found on the body's field), a theropod's blade recurved (its front edge
# convex, the tip turned back) and compressed side to side (`up` forward, aspect > 1), a crocodile's and plesiosaur's
# round and slightly curved, the points true. The rows were already set to interlock (upper and lower alternate).
# Not converted: the rodents' incisors (hare, rat, squirrel: a chisel edge, not a point, and a millimetre across).
# Run once per species. RE-RUN after the species' generator.
import sys
from claws import run

F = (1, 0, 0)
SPEC = {
    "dinosaurs/tyrannosaur": [(r"tooth\d", dict(bend=0.1, ext=1.0, aspect=1.5, ref=F, need=0.6, rk=1.0, pw=1.0))],
    "dinosaurs/allosaurus": [(r"tooth\d", dict(bend=0.1, ext=1.0, aspect=1.5, ref=F, need=0.6, rk=1.0, pw=1.0))],
    "dinosaurs/carnotaurus": [(r"tooth\d", dict(bend=0.1, ext=1.0, aspect=1.5, ref=F, need=0.6, rk=1.0, pw=1.0))],
    "others/crocodile": [(r"tooth[UL]\d", dict(bend=0.06, ext=1.0, aspect=1.0, ref=F, need=0.6, rk=1.0, pw=1.0))],
    "sea/plesiosaurus": [(r"tooth[UL]\d+", dict(bend=0.12, ext=1.0, aspect=1.0, ref=(0, 0, 1), need=0.6, rk=1.0, pw=1.0))],
    "monsters/hydra": [(r"neck[A-Z]Tooth[LR]\d", dict(bend=0.1, ext=1.0, aspect=1.3, ref=F, need=0.6, rk=1.0, pw=1.0))],
    "others/spider": [(r"fang", dict(bend=0.2, ext=1.0, aspect=1.0, ref=F, need=0.5, rk=1.0, pw=1.0))],
}

if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["all"]: args = list(SPEC)
    for a in args:
        sp = a if "/" in a else next(k for k in SPEC if k.endswith("/" + a))
        run(sp, [(rx, dict(kw)) for rx, kw in SPEC[sp]])
