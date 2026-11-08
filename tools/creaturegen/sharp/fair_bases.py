# fair_bases.py (2026-11-08): the tusks' and horns' ROOTS faired into the head (sharp.js horn `fair`: a fillet grown out
# of the skin, the smooth union of the horn and the body, its paint and skin the body's) -- a boss where a horn leaves
# the skull, a gum where a tusk leaves the lip, instead of a crease. fair = F x the horn's radius at its root.
# Run from tools/creaturegen/sharp: python3 fair_bases.py   (idempotent: it sets the value again)
from shp import load, save
F = 0.75
TODO = {
    "mammals/boar": ["tusk"], "sea/walrus": ["tusk"], "mammals/elephant": ["tusk"],
    "mammals/ox": ["horn"], "mammals/cow": ["hornd"], "mammals/oryx": ["horn"], "mammals/impala": ["horn0"],
    "mammals/chamois": ["hornd"], "mammals/rhinoceros": ["horn", "horn2"], "dinosaurs/carnotaurus": ["horn"],
}
FACTOR = {"mammals/rhinoceros": 0.5, "sea/walrus": 0.6, "mammals/ox": 0.4, "mammals/cow": 0.5, "mammals/oryx": 0.5, "mammals/impala": 0.5,
          "mammals/chamois": 0.5, "dinosaurs/carnotaurus": 0.5}   # (a horn leaving the skull: a small boss, the bone close under the skin)
# the BOAR's lower tusk (a wild boar's: out of the mouth under the upper lip's flange, a third of the way back from the
# disc, flaring OUT from the cheek and curving up and a little back): its root deep in the jaw (it poked out before, a
# white stub under the lip), standing clear of the snout (it lay along the skin)
BOAR_TUSK = [[1.08, 0.44, 0.015, 0.0135], [1.1, 0.438, 0.05, 0.0135], [1.112, 0.452, 0.072, 0.013], [1.122, 0.48, 0.09, 0.0122],
             [1.122, 0.51, 0.102, 0.0105], [1.11, 0.536, 0.108, 0.0065], [1.095, 0.552, 0.108, 0.0]]
for sp, ids in TODO.items():
    txt, d = load(sp); sh = d["sculpt"]["shape"]; n = 0
    for p in sh:
        if p.get("type") == "horn" and p.get("id") in ids:
            if sp == "mammals/boar": p["pts"] = BOAR_TUSK
            r0 = max(q[3] for q in p["pts"][:2])
            p["fair"] = round(FACTOR.get(sp, F) * r0, 4); n += 1
    save(sp, sh, txt); print(sp, n, [p.get("fair") for p in sh if p.get("id") in ids])
from shp import note
for sp in TODO:
    note(sp, "(2026-11-08, fair_bases.py)", ("The TUSKS' roots are FAIRED into the head (sharp.js horn `fair`): the smooth union of tusk and skin, a gum "
         "the body's colour, no crease." if sp in ("mammals/boar", "sea/walrus", "mammals/elephant") else
         "The HORNS' roots are FAIRED into the skull (sharp.js horn `fair`): a small boss, the smooth union of horn and skin, no crease.")
         + (" The boar's lower tusk comes out from under the upper lip a third of the way back from the disc, flaring out from the cheek and curving up." if sp == "mammals/boar" else ""))
