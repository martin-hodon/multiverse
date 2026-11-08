# whiskers.py (2026-11-08): every species with PROMINENT whiskers given them as one `whiskers` shape a group (bodyspec.js
# whiskerStrands -> sharp.js strandMesh: thin tapered 3-sided strands with an exact tip, mirrored, on the head bone,
# near mesh only) -- the mystacial fan on the whisker pad, and on cats and seals the brow (superciliary) tufts.
# Each group's `at` is found on the body: a ray from a seed point inside the head (a shape's centre, or a point, plus
# `off`) along the fan's own `dir` to where it leaves the skin, then `inset` back in; the strands' roots spread round
# it on the pad, each buried `bury` back along its line. The hand-placed whiskers they replace (thin cones and tubes:
# the rat's, the weasel's, the seal's, the porcupine's) are dropped (`drop`: a regular expression of ids),
# kept in whiskers_orig.json (made on a species' first run) so --undo puts them back.
#   python3 whiskers.py SPECIES... | all      (species as in SPEC: "mammals/cat")
#   python3 whiskers.py --check SPECIES...   (each strand's buried root and skin point against the body's field)
#   python3 whiskers.py --undo SPECIES...
# The species written over head params (the lion's, the tiger's: `expr`) get `at` as the seed shape's own expressions
# plus the offset found, and their lengths times `hs` -- so the lioness's bigger head carries them too.
# WHAT HAS WHISKERS (the audit, 2026-11-08): felids (cat, lion, tiger, leopard, lynx, smilodon: pale, long, 4-5 rows,
# brow tufts), canids and the hyena (sparse, dark, short), rodents and the hare (long; rat, squirrel, beaver, hare,
# capybara, porcupine), mustelids and kin (weasel, badger, red panda), the hedgehog, the pinnipeds (seal: beaded, pale,
# brow tufts; walrus: a moustache of short thick bristles -- its own hand-placed cones, kept). Not: ungulates, primates, elephants, bears, the bat, the
# anteater and pangolin, the skunk (short and hidden in its fur), birds, reptiles, fish, dinosaurs, monsters; the
# dragons' barbels are their own.
import json, math, os, sys, re, subprocess
from shp import load, save, block, sub, add, mul, dot, crs, nrm, ln, note, r5, SH, path_of
HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
BK = HERE + "whiskers_orig.json"

def probe(sp, req):
    r = subprocess.run(["node", "--import", "../reg.mjs", "wprobe.mjs", "creatures/" + sp], input=json.dumps(req), capture_output=True, text=True, cwd=SH)
    if r.returncode: raise RuntimeError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().split("\n")[-1])

WHITE, IVORY, GREY, DARK, BLACK = "#f4f2ea", "#e8e2d2", "#b8b2a8", "#3a322c", "#1a1614"

# a group: id, on (a shape id: its centre, the left one -- or a point), off (added to the seed), dir, inset (metres
# back from the skin), and the `whiskers` shape's own parameters (bodyspec.js whiskerStrands)
def fan(id="whiskers", **k): return {"id": id, **k}

def felid(k, pad="pad", brow="@eye", brow_off=None, rows=4, per=3, color=WHITE, tip=IVORY, dir=(-.15, -.05, 1), long=1.0, **o):
    """a cat's whiskers at k times the house cat's size (lengths and spacing; the radius by k^.8, a big cat's a little
    finer for its size; `long` their length beyond that -- a big cat's muzzle is longer, its whiskers with it): four rows fanned out of the pad, the back ones longest, curving forward a little; a brow tuft"""
    m = {**dict(inset=.0018 * k, rows=rows, per=per, gap=[.0042 * k * 3 / max(3, per), .0032 * k * 4 / rows], fan=[18, -14], sweep=[-12, 28],
         len=[.040 * k * long, .060 * k * long], rowLen=[1, .72], droop=.08, curl=.10, r=round(.00055 * k ** .8 * long ** .5, 6), color=color, tip=tip, seed=3), **o}
    return [fan(on=pad, dir=list(dir), **m),
            fan(id="brows", on=brow, off=brow_off or [.002 * k, .006 * k, 0], dir=[-.4, .6, .7], along=[1, .5, -.8], inset=.001 * k, rows=1, per=3,
                gap=[.003 * k, 0], fan=[0, 0], bury=.006 * k, sweep=[-10, 18], len=[.019 * k, .026 * k], droop=.18, curl=-.05,
                r=round(.0004 * k ** .8, 6), color=color, tip=tip, seed=5)]

def sparse(on, k, color=DARK, off=(0, 0, 0), rows=3, per=3, dir=(-.2, -.05, 1), **o):
    """a dog's, a fox's, a rodent's: fewer, stiffer, dark (k: the house cat's size again, for the lengths)"""
    m = {**dict(inset=.0015 * k, rows=rows, per=per, gap=[.0045 * k, .0035 * k], fan=[14, -16], sweep=[-8, 30], len=[.034 * k, .05 * k],
         rowLen=[1, .75], droop=.10, curl=.04, r=round(.00045 * k ** .8, 6), color=color, seed=7), **o}
    return [fan(on=on, off=list(off), dir=list(dir), **m)]

SPEC = {
  # ---- felids: four rows of long pale whiskers fanned out of the pad, the back ones the longest; brow tufts
  "mammals/cat": felid(1),
  "mammals/lion": felid(2.4, pad="L3pad", brow="L4browR", brow_off=[0, 0, 0], per=4, long=1.3),
  "mammals/tiger": felid(2.6, pad="L3pad", brow="L4browR", brow_off=[0, 0, 0], per=4, long=1.3),
  "mammals/leopard": felid(1.9, brow="browR", brow_off=[0, 0, 0], per=4, long=1.3),
  "mammals/lynx": felid(1.4, brow="browR", brow_off=[0, 0, 0], color=IVORY, tip=GREY),
  "mammals/smilodon": felid(2.4, brow="browR", brow_off=[0, 0, 0], per=4, long=1.3),
  "monsters/manticore": felid(2.3, per=4, color=IVORY, long=1.3),
  # ---- canids and the hyena: sparse, dark, short
  "mammals/dog": sparse([.585, .598, 0], 1.0, rows=3, per=3, gap=[.008, .006], len=[.03, .045]),
  "mammals/wolf": sparse([.80, .795, 0], 1.0, rows=3, per=4, gap=[.009, .006], len=[.04, .065]),
  "mammals/fox": sparse([.445, .427, 0], 1.0, color=BLACK, rows=3, per=4, gap=[.0055, .0042], len=[.042, .068]),
  "mammals/hyena": sparse([.90, .765, 0], 1.0, color=BLACK, rows=3, per=3, gap=[.012, .009], len=[.035, .055], r=.0007),
  # ---- rodents and the hare: long, many
  "mammals/rat": sparse("whiskerPad", 1.0, color="@whisker", rows=4, per=4, gap=[.0028, .0022], len=[.028, .048], fan=[16, -18], r=.0004, drop=r"whisker\d+"),
  "mammals/squirrel": sparse("pad", 1.0, color=BLACK, rows=4, per=3, gap=[.0035, .003], len=[.032, .05], fan=[18, -16], r=.0004),
  "mammals/beaver": sparse("pad", 2.0, color=DARK, rows=4, per=4, gap=[.0075, .006], len=[.06, .09], r=.0008),
  "mammals/hare": sparse("pad", 1.4, color="#ece8e0", tip=GREY, rows=4, per=3, gap=[.004, .0035], len=[.05, .075], fan=[20, -16], r=.00045),
  "mammals/capybara": sparse([.82, .47, 0], 2.0, rows=3, per=3, gap=[.014, .012], len=[.04, .06], r=.0008),
  "mammals/porcupine": sparse("muzzle", 2.0, color="@whisker", off=(.017, 0, 0), rows=3, per=3, gap=[.009, .008], len=[.08, .12], r=.0009, drop=r"whisker\d+"),
  # ---- mustelids and kin, the hedgehog
  "mammals/weasel": sparse([.0985, .0455, 0], .6, color="@whisker", rows=3, per=3, gap=[.0022, .0018], len=[.018, .028], r=.0003, drop=r"whisker\d+"),
  "mammals/hedgehog": sparse([.14, .041, 0], .8, rows=3, per=3, gap=[.003, .0026], len=[.022, .032], r=.0003),
  "mammals/badger": sparse([.385, .142, 0], 1.0, rows=3, per=3, gap=[.006, .005], len=[.03, .045], r=.0005),
  "mammals/redpanda": sparse([.28, .228, 0], 1.0, color=WHITE, rows=3, per=3, gap=[.005, .004], len=[.04, .055], r=.0005),
  # ---- pinnipeds: the seal's fan and brows; the walrus's moustache of thick bristles, forward and down
  "sea/seal": [fan(on="pad", dir=[.1, -.05, 1], inset=.003, rows=4, per=[3, 4, 4, 3], gap=[.014, .013], fan=[10, -18], sweep=[-20, 25],
                   len=[.07, .10], rowLen=[1, .85], droop=.06, curl=.12, r=.0016, sides=4, color="@whisker", seed=11, drop=r"wh\d+|brow\d+"),
               fan(id="brows", on="@eye", off=[0, .025, -.035], dir=[-.3, .7, .6], along=[1, .3, -.5], inset=.002, rows=1, per=2, gap=[.014, 0], fan=[0, 0],
                   bury=.012, sweep=[-5, 15], len=[.045, .055], droop=.12, r=.0013, sides=4, color="@whisker", seed=13)],
  # (the walrus keeps its hand-placed grid of thick cones: 29 a side over the whole front of the muzzle, a surface too
  #  curved for one root plane -- the strands' roots stood 35 mm off it)
}

def unit(v): return nrm(v)

def shapes_of(d): return d["sculpt"]["shape"] if "sculpt" in d else d["shape"]   # (an overlay's, or a natively sculpted body's: the hedgehog's)

def save2(sp, shapes, txt):
    """shp.save for either kind (the shape list one a line, the rest of the file untouched)"""
    d = json.loads(txt)
    if "sculpt" in d: return save(sp, shapes, txt)
    L, a, b = block(txt, len(d["shape"]))
    ind = re.match(r'^(\s*)', L[a]).group(1)
    out = "\n".join(L[:a] + [ind + json.dumps(x) + ("," if k < len(shapes) - 1 else "") for k, x in enumerate(shapes)] + L[b:])
    json.loads(out); open(path_of(sp), "w").write(out)

def rr(v):
    """numbers kept to a tenth of a millimetre's hundredth (a whisker's radius is a few tenths of a millimetre)"""
    if isinstance(v, float): return float(f"{v:.6g}") if abs(v) < .01 else round(v, 5)
    if isinstance(v, list): return [rr(x) for x in v]
    return v

def apply(sp):
    groups = SPEC[sp]
    txt, d = load(sp)
    sh = shapes_of(d)
    P = dict(d.get("params") or {})
    expr = any(isinstance(v, str) and "hs" in v for s in sh for v in (s.get("c") or []))
    # (the old hand-placed whiskers, kept once)
    drop = [g["drop"] for g in groups if g.get("drop")]
    if drop:
        ORIG = json.load(open(BK)) if os.path.exists(BK) else {}
        if sp not in ORIG:
            ORIG[sp] = [s for s in sh if any(re.fullmatch(x, str(s.get("id", ""))) for x in drop)]
            json.dump(ORIG, open(BK, "w"), indent=0)
    seeds = [g["on"] for g in groups if isinstance(g["on"], str) and g["on"][0] != "@"]
    info = probe(sp, {"ids": seeds})
    rays, at0 = [], []
    for g in groups:
        s = g["on"]
        c = info["eyes"][0] if s == "@eye" else info["shapes"][s]["c"] if isinstance(s, str) else s
        c = add(c, g.get("off", [0, 0, 0]))
        u = unit(g["dir"])
        at0.append((c, u)); rays.append([c, add(c, u, .5)])
    hits = probe(sp, {"rays": rays})["hits"]
    if None in hits: raise RuntimeError(f"{sp} {groups[hits.index(None)]['id']}: the ray never leaves the body")
    grads = probe(sp, {"grads": hits})["grads"]   # (the skin's normal where the fan's line leaves it: the roots' plane)
    new = []
    for g, (c, u), h, nn in zip(groups, at0, hits, grads):
        at = add(h, u, -g.get("inset", .001))
        if g.get("plane", True): g = {**g, "normal": [round(x, 3) for x in nn]}
        w = {"id": g["id"], "type": "whiskers", "bone": g.get("bone", "head")}
        par = {k: v for k, v in g.items() if k not in ("id", "on", "off", "inset", "drop", "bone", "plane")}
        if expr:
            hs = float(P.get("hs", 1))
            s = g["on"]
            src = next(x for x in sh if x.get("id") == s) if isinstance(s, str) and s[0] != "@" else None
            cres = info["shapes"][s]["c"] if src else None
            if src is None: raise RuntimeError(f"{sp}: an expression species needs a shape seed")
            # (the left one: the shape's own expressions; its resolved centre was the left twin)
            w["at"] = [f"({e})+({(at[k] - cres[k]) / hs:.5f})*hs" for k, e in enumerate(src["c"])]
            for k in ("gap", "len", "r", "bury"):
                if k in par: par[k] = [f"({x / hs:.5f})*hs" for x in par[k]] if isinstance(par[k], list) else f"({par[k] / hs:.6f})*hs"
        else:
            w["at"] = rr(at)
        w.update({k: (rr(v) if not expr or k not in ("gap", "len", "r", "bury") else v) for k, v in par.items()})
        new.append(w)
    # write: the old ones gone, each group in place of its namesake (or after its seed shape)
    txt, d = load(sp)
    sh = [s for s in shapes_of(d) if not any(re.fullmatch(x, str(s.get("id", ""))) for x in drop)]
    for w in new:
        i = next((k for k, s in enumerate(sh) if s.get("id") == w["id"]), None)
        if i is not None: sh[i] = w; continue
        g = next(g for g in groups if g["id"] == w["id"])
        key = g.get("after", g["on"] if isinstance(g["on"], str) and g["on"][0] != "@" else None)
        j = next((k for k, s in enumerate(sh) if key is not None and s.get("id") == key), None)
        if j is None:
            hj = [k for k, s in enumerate(sh) if s.get("bone") == "head"]
            j = hj[-1] if hj else len(sh) - 1
        sh.insert(j + 1, w)
    save2(sp, sh, txt)
    note(sp, "WHISKERS (2026-11-08, tools/creaturegen/sharp/whiskers.py):", about(sp, groups, P, bool(drop)))
    print(sp, "whiskers:", [w["id"] for w in new])

NAMES = {WHITE: "white", IVORY: "ivory", GREY: "grey", DARK: "dark brown", BLACK: "black", "#ece8e0": "pale"}

def about(sp, groups, P, converted):
    """the sentence for the species' _about"""
    out = []
    for g in groups:
        per = g.get("per", 4); rows = g.get("rows", 4)
        n = sum(per) if isinstance(per, list) else rows * per
        L = g.get("len", .05); L = L if isinstance(L, list) else [L, L]
        col = NAMES.get(g.get("color"), "@whisker-coloured" if g.get("color") == "@whisker" else str(g.get("color")))
        where = "a brow tuft" if g["id"] == "brows" else f"{rows} rows on the whisker pad"
        out.append(f"{n} {col} whiskers a side, {where} ({L[0] * 1000:.0f}-{L[1] * 1000:.0f} mm)")
    return ("; ".join(out) + " -- `whiskers` shapes (bodyspec.js whiskerStrands: thin pointed strands, mirrored, on the head, "
            "near mesh only; details, so every coat and variant still shares one mesh)" + (", replacing the hand-placed cones" if converted else "") + ".")

def check(sp):
    out = probe(sp, {"strands": True})["strands"]
    left = [s for s in out if s["z"] > 0]
    bad = [s for s in left if s["d1"] > s["r"] * 1.5]
    deep = [s for s in left if s["d1"] < -.004]
    print(f"{sp}: {len(left)} strands a side; root outside {len([s for s in left if s['d0'] >= 0])}, skin point clear of the skin {len(bad)}, deeper than 4 mm {len(deep)}",
          " ".join(f"{s['id']}:{s['d1']*1000:.1f}" for s in left))

def undo(sp):
    ORIG = json.load(open(BK)) if os.path.exists(BK) else {}
    txt, d = load(sp)
    ids = {g["id"] for g in SPEC.get(sp, [])}
    sh = [s for s in shapes_of(d) if not (s.get("type") == "whiskers" and s.get("id") in ids)]
    if sp in ORIG:
        hj = max(k for k, s in enumerate(sh) if s.get("bone") == "head")
        sh = sh[:hj + 1] + ORIG[sp] + sh[hj + 1:]
    save2(sp, sh, txt)
    print(sp, "undone")

if __name__ == "__main__":
    a = sys.argv[1:]
    mode = "apply"
    if a and a[0] in ("--check", "--undo"): mode = a.pop(0)[2:]
    sps = list(SPEC) if a == ["all"] else a
    for sp in sps:
        {"apply": apply, "check": check, "undo": undo}[mode](sp)
