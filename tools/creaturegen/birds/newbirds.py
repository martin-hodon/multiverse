# newbirds.py [names...] -- the standing birds that came over from items/birds, from nb.py's body plan (units: the bird's
#   length, bill tip to tail tip)
import sys, math
from nb import bird as _bird, pal
# CLOSE-RANGE fixes (2026-11-05 review of the head close-ups): eyes set INTO the head (no marbles: smaller, sunk past
# half their radius, the socket in the head's own colour), the face meshed finer (no facets, the paint's edges not
# torn by long triangles), by name over what each bird says
CLOSE = {
    # (C final 2026-11-07: the small songbirds' eyes set INTO the head, no marbles; the pad wing; the body meshed finer --
    #  the faceted slabs gone)
    "swallow": dict(eye=.016, sink=.7, socket=1.08, mesh=[5200, 1000], focus={"head": 3}),
    "robin": dict(eye=.017, sink=.7, socket=1.08, mesh=[5200, 1000], focus={"head": 3}),
    "sparrow": dict(eye=.016, sink=.7, socket=1.08, mesh=[5200, 1000], focus={"head": 3}),
    "blackbird": dict(eye=.016, sink=.7, socket=1.08, mesh=[5200, 1000], focus={"head": 3}),
    "magpie": dict(cell=.0025, eye=.019, sink=.7, mesh=[4600, 1100]), "crow": dict(cell=.0028, eye=.018, sink=.7, mesh=[4000, 1100]), "raven": dict(cell=.0039, eye=.018, sink=.7, mesh=[3500, 1000]),   # (C 2026-11-07: the 11k floor)
    "pigeon": dict(mesh=[3900, 1000], focus={"head": 3}),   # (C final: finer -- the faceted slabs gone)
    "stork": dict(mesh=[5000, 1200], focus={"head": 3}), "crane": dict(mesh=[5000, 1200], focus={"head": 3}),   # (C final: finer -- no faceted slabs)
    "goose": dict(mesh=[3000, 1000]), "pheasant": dict(mesh=[4400, 1100]),   # (C 2026-11-07: the 11k floor, after the pad wing)
    "dove": dict(cell=.0017, eye=.016, sink=.7, socket=1.08, mesh=[4000, 1100]), "kingfisher": dict(cell=.001, eye=.015, sink=.7, socket=1.08, mesh=[5000, 1100]),   # (C final: the eyes set in -- no marbles)
    "vulture": dict(cell=.0065, mesh=[7000, 1400], focus={"head": 3}),
    "hoopoe": dict(eye=.015, sink=.7, socket=1.08, mesh=[4800, 1100], focus={"head": 3}),   # (C final: finer, eyes set in)
    "woodpecker": dict(eye=.014, sink=.75, socket=1.08, mesh=[6000, 1300], focus={"head": 3}),   # (C final: finer, the bar blades gone)
    "cockatoo": dict(eye=.018, sink=.7, socket=1.08, mesh=[4000, 1100], focus={"head": 3}),   # (C final: the eyes set in)
    "cockatiel": dict(eye=.015, sink=.7, socket=1.08, mesh=[3600, 1000], focus={"head": 3}),   # (C final: the eyes set in)
    "penguin": dict(cell=.0045, sink=.55, mesh=[9600, 1800], focus={"head": 3}),
    "ostrich": dict(cell=.011, eye=.045, sink=.55, socket=1.1, mesh=[3100, 1100], focus={"head": 3}),
    "toucan": dict(eye=.022, sink=.85, socket=1.06, focus={"head": 3}),   # (C final: the eyes set in -- no marbles)
    "ibis": dict(eye=.017, sink=.7, socket=1.08, mesh=[4400, 1100], focus={"head": 3}),   # (C final: eyes set in; finer after the pad wing)
    "pelican": dict(cell=.0065, sink=.5, mesh=[6000, 1400], focus={"head": 3}),
    "gull": dict(mesh=[3600, 1100], focus={"head": 2}),   # (C final: the pad-only fold left it coarse -- back over 11k)
}
# (2026-11-07, B) the named coats of the birds whose bodies stay as they are: the HEN where the sexes differ only in colour
#  (the sparrow's, the blackbird's), a sister species of one build (the black stork, the sacred ibis), the cage morphs
#  (the cockatiel's lutino and whiteface) and the domestic white dove -- by name, over the palette's own keys
_W = lambda c, *ks: {k: c for k in ks}
COATS = {
    "sparrow": [{"name": "house sparrow"},
                {"name": "house sparrow hen", "back": "#8a6a48", "rump": "#8a7a64", "neck": "#8a7458", "head": "#8a7c6a", "crown": "#8a7c6a", "nape": "#9a8a72",
                 "cheek": "#b8ae9c", "throat": "#b4ac9e", "bib": "#b4ac9e", "under": "#b4ac9e", "vent": "#bab2a4", "thigh": "#b4ac9e",
                 "cov": "#8a6a48", "covTip": "#7a5c3c", "gcov": "#7a5e40", "gcovTip": "#d8ccb4", "wpad": "#7e6040", "streak": "#3a2c20"}],
    "blackbird": [{"name": "blackbird"},
                  {"name": "blackbird hen", "back": "#4a3a2c", "rump": "#4a3a2c", "neck": "#4a3a2c", "head": "#4a3a2c", "crown": "#463628", "cheek": "#544232",
                   "throat": "#7a6450", "under": "#5e4a38", "vent": "#5a4636", "thigh": "#5a4636", "tail": "#3a2c22", "tailTip": "#3a2c22",
                   **_W("#46362a", "cov", "gcov", "sec", "tert", "wpad"), **_W("#3e3024", "covTip", "gcovTip", "secTip", "tertTip"),
                   "prim": "#3a2c22", "primTip": "#30241c", "bill": "#6a5638", "billLo": "#6a5638", "ring": "#5a4a3a"}],
    "stork": [{"name": "white stork"},
              {"name": "black stork", "scale": .9, **_W("#1c1e1c", "back", "rump", "neck", "head", "crown", "cheek", "throat", "tail", "tailTip", "cov", "gcov", "wpad"),
               "covTip": "#16201c", "gcovTip": "#1e2a24", "under": "#f2f2ee", "vent": "#f2f2ee", "thigh": "#f2f2ee", "bill": "#c8302a", "billLo": "#c8302a", "leg": "#c8302a"}],
    "ibis": [{"name": "scarlet ibis"},
             {"name": "sacred ibis", "scale": 1.15, **_W("#f0eeea", "back", "rump", "under", "vent", "thigh", "tail", "tailTip", "cov", "covTip", "gcov", "gcovTip", "prim", "wpad"),
              **_W("#1a1a1c", "neck", "head", "crown", "cheek", "throat", "bill", "billLo", "leg", "primTip"), "sec": "#e8e6e2", "secTip": "#2a2a2c",
              "tert": "#2a2a2e", "tertTip": "#1e1e22", "eye": "#3a2a20"}],
    "cockatiel": [{"name": "grey cockatiel"},
                  {"name": "lutino cockatiel", **_W("#f6f0d6", "back", "rump", "under", "vent", "neck", "thigh", "sec", "tert", "prim", "tail", "wpad"),
                   **_W("#f0e8c4", "secTip", "tertTip", "primTip", "tailTip", "crestTip"), "head": "#f4dc56", "crown": "#f0d850", "throat": "#f2dc60",
                   "eye": "#a8282a", "bill": "#d8c8b0", "billLo": "#ccbca4", "leg": "#d8b8a8"},
                  {"name": "whiteface cockatiel", "head": "#f2f0ea", "crown": "#ecebe6", "cheek": "#f2f0ea", "throat": "#e8e6e0", "crest": "#e2e0da", "orange": "#ecebe6"}],
    "dove": [{"name": "turtle dove"},
             {"name": "white dove", **_W("#f4f2ee", "back", "rump", "under", "vent", "neck", "head", "crown", "cheek", "throat", "thigh", "tail", "tailTip",
                                         "cov", "covTip", "gcov", "gcovTip", "sec", "secTip", "tert", "tertTip", "prim", "primTip", "wpad", "blk", "wht"),
              "bill": "#d8a8a8", "billLo": "#d8a8a8", "ring": "#e0b0b0", "eye": "#2a1a14"}],
}
def bird(name, about, L, colors, **kw):
    if name in COATS: kw.setdefault("coats", COATS[name])
    for k, v in CLOSE.get(name, {}).items(): kw.setdefault(k, v) if k not in ("mesh", "focus", "eye", "sink", "socket", "cell") else kw.__setitem__(k, v)
    return _bird(name, about, L, colors, **kw)
from bg import fea, row, add, nrm

SP = {}
# (C r7 2026-11-07: the folded wing as ONE smooth pad on the flank -- its colour regions, bars and spots painted on it --
#  instead of the rows of loose covert/secondary vanes that read as discs and blades at full size)
NOTRACT = {"cov": 0, "pcov": 0, "gcov": 0, "sec": 0, "tert": 0, "prim": 0}
def PAD(**kw): return dict(**{"out": .034, "th": .032, "rim": 0, "len": .6, "h": .6, "k": .03, "kc": .008, **kw})
def sp(f): SP[f.__name__] = f; return f
SMALL = dict(fold=dict(n=(2, 2, 3, 2)), mesh=[1000, 520])
MED = dict(fold=dict(n=(2, 3, 3, 2)), mesh=[1500, 700])
BIG = dict(fold=dict(n=(3, 3, 4, 3)), mesh=[2000, 900])
def M_(a, b):
    out = json_copy(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict): out[k].update(v)
        else: out[k] = v
    return out
import json
def json_copy(x): return json.loads(json.dumps(x))

@sp
def sparrow():
    c = pal("#8a5f3a", "#a29c92", head="#7f7c78", wing="#8a5f3a", tail="#5a4430", bill="#2e2a26", leg="#b08a74",
            cheek="#cfcac0", throat="#9a948a", bib="#1e1a16", neck="#8a4e2a", rump="#8a7a64",
            cov="#9a5a2e", covTip="#9a5a2e", gcov="#7a4e2e", gcovTip="#ece4d4", sec="#6a4a30", secTip="#b89a70", prim="#4e3a28", primTip="#3a2c20",
            streak="#2e2118", nape="#8a4a26")
    bird("sparrow", "a house sparrow cock on the ground: a compact streaked bird -- warm brown back streaked black, grey crown, chestnut from the eye round the nape, pale grey cheeks, the black bib, a white wing bar; grey breast; the stubby conical seed-eater's bill; short pink-brown legs",
         .15, c, **M_(SMALL, dict(tilt=22, spread=dict(span=1.5, armF=.36, asp=2.0, tipC=.55, hsweep=.15),
         bill=dict(len=.075, r=.034, droop=8, depth=1.3),
         tail=dict(len=.37, w=.075, n=5, ang=-12, spread=.32),
         fold=dict(pad=PAD(col="@cov", tipCol="@prim", patches=[dict(x=.44, y=.5, rx=.06, ry=.5, col="@gcovTip", rot=12, paint=True), dict(x=.74, y=.55, rx=.28, ry=.42, col="@sec", rot=-4)])),
         wing=dict(n=NOTRACT),
         marks=[("h", "napeBand", [-.035, .02, .045], [.07, .03, .025], "@nape", {"k": .01, "mirror": True}),
                ("p", "bib", [.0, -.085, 0], [.09, .048, .018], "@bib", {"dir": [1, -.45, 0]}), ("p", "bib2", [-.02, -.12, 0], [.07, .055, .018], "@bib", {"dir": [1, -.15, 0]}),   # (C final: below the bill, not round it)
                ("b", "streak1", [-.02, .12, .05], [.07, .008, .01], "@streak", {"k": .006, "mirror": True}),
                ("b", "streak2", [-.08, .11, .035], [.06, .007, .01], "@streak", {"k": .006, "mirror": True})])))

@sp
def robin():
    c = pal("#7b6a4a", "#d8652a", vent="#ece6da", thigh="#e0d8ca", belly="#ece6da", wing="#76643f", tail="#6a5a3e", bill="#2a2420", leg="#7a5e48", red="#d8652a", grey="#9aa29e",
            cheek="#d8652a", throat="#d8652a", gcovTip="#a08a5e", secTip="#5e5034", prim="#4e4430", primTip="#3e3626", eye="#120c08")
    bird("robin", "a European robin on the ground, upright and round: olive-brown above, the orange-red face and breast edged with blue-grey, a white belly; big dark eye, the thin insect-eater's bill, long slim legs",
         .14, c, **M_(SMALL, dict(tilt=32, spread=dict(span=1.55, armF=.36, asp=2.0, tipC=.55, hsweep=.15), trunk=[.2, .13, .115], breast=[.13, .12, .11], head=[.2, .15], hr=[.078, .072, .068],
         bill=dict(len=.07, r=.02, droop=6),
         tail=dict(len=.34, w=.075, n=5, ang=-20, spread=.3),
         tars=.17, legr=.009,
         fold=dict(pad=PAD(col="@wpad", tipCol="@primTip")), wing=dict(n=NOTRACT),
         marks=[("b", "belly", [-.05, -.075, 0], [.15, .075, .11], "@belly", {"k": .025}),
                ("h", "face", [.045, -.025, 0], [.07, .06, .08], "@red", {"k": .012}),
                ("b", "greyEdge", [.07, .085, 0], [.08, .025, .13], "@grey", {"k": .012})])))

@sp
def swallow():
    c = pal("#1c2846", "#efe0c8", wing="#1a1f32", tail="#1a2036", bill="#141414", leg="#2a2420", red="#a8362a",
            throat="#a8362a", cheek="#1c2846", gcovTip="#1a1f32", prim="#14171f", primTip="#101218", eye="#100c08")
    bird("swallow", "a barn swallow perched: slim, glossy blue-black above, the brick-red throat and forehead under a dark breast band, cream below; the long pointed wings crossing to the deep fork of the tail with its long outer streamers; a tiny bill on a wide gape, short legs",
         .18, c, **M_(SMALL, dict(tilt=10, trunk=[.16, .085, .085], breast=[.1, .08, .08], bc=[.07, -.01],
         neck=[[.1, .04, .065], [.145, .07, .055]], head=[.165, .085], hr=[.065, .058, .056],
         bill=dict(len=.03, r=.022, droop=4),
         tail=dict(len=.22, w=.05, n=5, ang=4, spread=.22, lens=[2.1, 1.05, .85, 1.05, 2.1], outline="flight"),
         fold=dict(S=[.07, .045, .08], T=[-.42, -.02, .035], H=.085, w=.04, pad=PAD(col="@wpad", tipCol="@primTip")),
         tars=.05, legr=.006, toes=.06, eye=.02, flight=dict(speed=2.2), spread=dict(span=1.65, armF=.3, asp=3.4, tipC=.12, hsweep=.8, kink=.2, pinch=.8), wing=dict(armK=.6, th=(40, 84), pointed=True, tert=.36, prim=.045, hand=.3, n=NOTRACT),
         marks=[("h", "forehead", [.05, .025, 0], [.03, .02, .04], "@red", {"k": .006}),
                ("b", "band", [.1, -.0, 0], [.055, .075, .082], "@back", {"k": .01})])))

@sp
def blackbird():
    c = pal("#161616", "#1c1c1c", wing="#151515", tail="#121212", bill="#e8a320", leg="#3a2e26", ring="#e0b030",
            prim="#101010", primTip="#0c0c0c", eye="#0e0a08")
    bird("blackbird", "a blackbird cock on the lawn: all black, a little glossy, the orange-yellow bill and the yellow ring round the eye; a long tail, often cocked; slim dark legs",
         .25, c, lid="@ring", **M_(SMALL, dict(tilt=22, spread=dict(span=1.5, armF=.38, asp=2.1, tipC=.55, hsweep=.18), bill=dict(len=.085, r=.025, droop=6),
         tail=dict(len=.42, w=.07, n=5, ang=-14, spread=.25), tars=.14, legr=.009,
         fold=dict(pad=PAD(col="@wpad", tipCol="@primTip")), wing=dict(n=NOTRACT))))

@sp
def magpie():
    c = pal("#131416", "#131416", wing="#1a2240", tail="#24363a", wht="#f0f0ec", bill="#141414", leg="#161616",
            cov="#1a2240", covTip="#1c2648", wpad="#161a2c", gcov="#1c2648", gcovTip="#24305a", sec="#22305c", secTip="#1a2246", prim="#161a28", primTip="#101218",
            tailTip="#3a5a48", eye="#100c08")
    bird("magpie", "a magpie strutting: pied -- the black head, breast and back, white belly and the white scapulars along the folded wing, the wings glossed blue, the long graduated tail glossed green; a stout black bill, black legs",
         .45, c, **M_(MED, dict(tilt=14, trunk=[.17, .098, .088], breast=[.1, .09, .085], bc=[.08, -.01],
         neck=[[.1, .06, .062], [.145, .09, .052]], head=[.17, .115], hr=[.06, .054, .05],
         bill=dict(len=.07, r=.025, droop=8, depth=1.1),
         tail=dict(len=.56, w=.06, n=6, ang=-8, spread=.08, lens=[.62, .85, 1.0, .85, .62]),
         fold=dict(S=[.07, .055, .09], T=[-.24, .01, .045], H=.1, w=.045,
                   pad=PAD(col="@cov", tipCol="@primTip", patches=[dict(x=.3, y=.24, rx=.5, ry=.3, col="@wht", rot=-4), dict(x=.62, y=.6, rx=.16, ry=.26, col="@sec", rot=-6)])),
         tars=.11, legr=.009, toes=.08, spread=dict(span=1.25, armF=.42, asp=1.9, tipC=.6, hsweep=.1, fingered=True), wing=dict(armK=1.0, th=(18, 70), rounded=True, n=NOTRACT),
         marks=[("b", "belly", [-.03, -.06, 0], [.15, .085, .1], "@wht", {"k": .02})])))

def corvid(name, L, about, bill, tail, extra_marks=(), **kw):
    c = pal("#18181b", "#1c1c20", wing="#17181e", tail="#16171b", bill="#121212", leg="#141414",
            gcov="#1a1d28", gcovTip="#1e2232", sec="#1c2030", secTip="#181a24", prim="#121318", primTip="#0e0f12", eye="#0e0a08")
    # (C r7: sleek -- a longer, slimmer trunk carried level, the crown flat (the head long and low), the heavy bill
    #  running straight on from the forehead; the folded wing one glossy pad, its primaries' point reaching the tail)
    bird(name, about, L, c, **M_(BIG if L > .6 else MED, dict(tilt=10, trunk=[.22, .11, .1], breast=[.13, .1, .095], bc=[.1, -.01], head=[.215, .125], hr=[.082, .058, .06],
         neck=[[.13, .06, .075], [.18, .095, .064]], bill=bill, tail=tail, tars=.13, legr=.012, toes=.1,
         fold=dict(S=[.09, .05, .1], T=[-.3, .0, .055], H=.1, w=.045, pad=PAD(tipCol="@primTip", patches=[dict(x=.62, y=.6, rx=.16, ry=.26, col="@sec", rot=-6)])),
         spread=dict(span=2.0, armF=.44, asp=2.4, tipC=.62, hsweep=.08, fingered=True), wing=dict(armK=1.4, th=(18, 82), hand=.4, n=NOTRACT),
         marks=list(extra_marks), **kw)))

@sp
def crow():
    corvid("crow", .48, "a carrion crow walking: all black with a faint blue-green gloss, the heavy black bill, the tail square-ended and the folded wingtips reaching it; black legs, a sturdy walk",
           dict(len=.12, r=.021, droop=5, curve=8, depth=1.1, baseY=.0, comp=.5, blade=True, taper=1.3, tipK=.95, lowK=.78, minR=.0008, wTip=.85), dict(len=.36, w=.07, n=6, ang=6, spread=.2),
           coats=[{"name": "carrion crow"},   # (B 2026-11-07: the hooded crow -- the grey body, the black head, bib, wings and tail)
                  {"name": "hooded crow", "back": "#8e8e92", "under": "#9a9a9e", "rump": "#8e8e92", "vent": "#9a9a9e", "thigh": "#8a8a8e", "throat": "#18181b", "wpad": "#14151b"}])

@sp
def raven():
    corvid("raven", .64, "a raven: the great black crow -- the massive arched bill, the shaggy throat hackles, the long wedge-shaped tail; glossy black all over",
           dict(len=.145, r=.025, droop=4, curve=10, depth=1.15, baseY=.0, comp=.48, blade=True, taper=1.3, tipK=.95, lowK=.78, minR=.0009, wTip=.85), dict(len=.4, w=.07, n=6, ang=6, spread=.18, lens=[.75, .9, 1.05, .9, .75]),
           extra_marks=[("h", "hackles", [.02, -.1, 0], [.07, .06, .062], "@throat", {"k": .035, "lumps": {"amp": .004, "size": .016}}),   # (C 2026-11-07: shaggy, merged -- no ball under the chin)
                        ("h", "shag", [-.01, -.13, 0], [.05, .04, .055], "@throat", {"k": .03})])

@sp
def pigeon():
    c = pal("#8f98a6", "#8a93a2", head="#727a88", wing="#98a0ac", tail="#8e97a4", bill="#3a3436", leg="#c4505a",
            neck="#5f8a72", rump="#b4bcc6", gcovTip="#1e1e22", secTip="#222226", prim="#4e5460", primTip="#2e3036", tailTip="#26262a",
            cere="#f0eeea", purple="#7a5a88", eye="#e07a20")
    coats = [{"name": "blue bar"},   # (B 2026-11-07: the feral pigeon's morphs)
             {"name": "blue checker", "cov": "#6a7280", "covTip": "#2a2c34", "gcov": "#6a7280", "gcovTip": "#1e1e22", "wpad": "#5e6672", "back": "#7e8796"},
             {"name": "ash-red", "back": "#c8b8b0", "under": "#c0aaa2", "head": "#b49890", "crown": "#b49890", "cheek": "#b49890", "rump": "#d8ccc6", "wing": "#ccbcb4",
              "cov": "#ccbcb4", "covTip": "#cab8b0", "gcov": "#ccbcb4", "gcovTip": "#8a3a26", "secTip": "#8a3a26", "sec": "#c4b2aa", "prim": "#b8a49a", "primTip": "#9a8278",
              "tail": "#c8b8b0", "tailTip": "#a07060", "neck": "#a8786a", "purple": "#9a6a6a", "wpad": "#bcaca4", "thigh": "#c0aaa2"},
             {"name": "white", "back": "#f0eeea", "under": "#f2f0ec", "head": "#f0eeea", "crown": "#f0eeea", "cheek": "#f0eeea", "throat": "#f2f0ec", "rump": "#f0eeea", "vent": "#f2f0ec",
              "cov": "#eeece8", "covTip": "#eeece8", "gcov": "#eeece8", "gcovTip": "#eeece8", "sec": "#eeece8", "secTip": "#eeece8", "prim": "#eae8e4", "primTip": "#e6e4e0",
              "tail": "#eeece8", "tailTip": "#eeece8", "neck": "#f0eeea", "purple": "#f0eeea", "wpad": "#e4e2de", "thigh": "#f2f0ec", "eye": "#3a2010"},
             {"name": "pied", "head": "#f0eeea", "crown": "#f0eeea", "cheek": "#f0eeea", "throat": "#eeecea", "prim": "#f0eeea", "primTip": "#e8e6e2", "under": "#d8dadf",
              "vent": "#eeece8", "tail": "#6e7684", "tailTip": "#3a3e46"},
             {"name": "spread black", "back": "#2a2c32", "under": "#2e3036", "head": "#26282e", "crown": "#26282e", "cheek": "#26282e", "throat": "#2e3036", "rump": "#2a2c32", "vent": "#2e3036",
              "cov": "#2c2e34", "covTip": "#2c2e34", "gcov": "#2c2e34", "gcovTip": "#222428", "sec": "#2a2c32", "secTip": "#222428", "prim": "#24262a", "primTip": "#1e2024",
              "tail": "#2a2c32", "tailTip": "#1e2024", "neck": "#2e4a40", "purple": "#3e3048", "wpad": "#26282c", "thigh": "#2e3036"}]
    bird("pigeon", "a feral rock pigeon: plump and blue-grey, the head darker, the neck glossed green and purple, two black bars across the folded wing, a dark band at the tail's end, the white cere over the short bill, red legs, an orange eye",
         .32, c, **M_(MED, dict(tilt=8, trunk=[.23, .15, .14], breast=[.15, .14, .13], bc=[.12, 0],
         neck=[[.15, .08, .1], [.22, .135, .075]], head=[.25, .165], hr=[.068, .062, .056],
         bill=dict(len=.06, r=.018, droop=12),
         tail=dict(len=.33, w=.08, n=6, ang=4, spread=.25), tars=.1, legr=.012, toes=.1, tuck="back",
         fold=dict(pad=PAD(col="@cov", tipCol="@primTip",   # (C final: the two bars PAINTED across the pad -- the blade rows read as dashes)
                           patches=[dict(x=.4, y=.36, rx=.042, ry=.62, col="@gcovTip", rot=-16, paint=True), dict(x=.55, y=.38, rx=.042, ry=.62, col="@gcovTip", rot=-16, paint=True)])),
         spread=dict(span=2.0, armF=.38, asp=2.8, tipC=.28, hsweep=.5, pinch=.7), wing=dict(armK=1.3, th=(25, 76), rounded=True, n=NOTRACT),
         coats=coats,
         marks=[("h", "cere", [.075, .008, 0], [.02, .013, .02], "@cere", {"k": .004}),
                ("m", "neckSheen", [.19, .1, 0], [.06, .05, .085], "@purple", {"k": .015, "bone": "neck"})])))

@sp
def dove():
    c = pal("#8a7462", "#e4d6d2", head="#a8a6b4", wing="#2e2420", tail="#4a4448", bill="#2e2a2a", leg="#c06070",
            neck="#c49aa0", throat="#c49aa0", rump="#7a6a60", cov="#2e2420", covTip="#c27c40", gcov="#2e2420", gcovTip="#c27c40",
            sec="#5a5050", secTip="#6a5e5a", prim="#3e383a", primTip="#2e2a2c", tailTip="#9a9496", blk="#1a1a1a", wht="#f2f0ee", ring="#c04848", eye="#e08a30")
    bird("dove", "a turtle dove: slim and small, the head blue-grey, neck and breast pinkish, the wings scaled black and chestnut, the black-and-white striped patch on the side of the neck, the dark tail edged white; a slender dark bill, red eye-ring, pinkish legs",
         .27, c, lid="@ring", **M_(MED, dict(tilt=8, trunk=[.21, .13, .125], breast=[.13, .12, .115], bc=[.11, 0],
         neck=[[.15, .075, .085], [.21, .12, .07]], head=[.24, .15], hr=[.066, .06, .055],
         bill=dict(len=.06, r=.016, droop=10), tail=dict(len=.4, w=.065, n=6, ang=4, spread=.25), tuck="back",
         fold=dict(pad=PAD(col="@covTip", tipCol="@primTip", patches=[dict(x=x_, y=y_, rx=.1, ry=.12, col="@cov", rot=-10) for x_, y_ in ((.18, .32), (.3, .26), (.42, .3), (.24, .52), (.36, .48), (.48, .5), (.3, .7), (.42, .68))])),
         spread=dict(span=1.7, armF=.38, asp=2.7, tipC=.28, hsweep=.5, pinch=.7), wing=dict(armK=1.05, th=(25, 76), rounded=True, n=NOTRACT),
         tars=.09, legr=.01, toes=.09,
         # (C final: the neck patch PAINTED on -- as lumps it stood off the neck as a chip)
         marks=[("m", "neckPatch", [.2, .105, .062], [.034, .03, .03], "@blk", {"k": .005, "kc": .003, "mirror": True, "bone": "neck", "op": "paint"}),   # (C final: one black patch, two broad white bars)
                ("m", "neckStripe", [.2, .114, .068], [.031, .006, .03], "@wht", {"k": .003, "kc": .002, "mirror": True, "bone": "neck", "op": "paint"}),
                ("m", "neckStripe2", [.2, .096, .068], [.031, .006, .03], "@wht", {"k": .003, "kc": .002, "mirror": True, "bone": "neck", "op": "paint"})])))

@sp
def kingfisher():
    c = pal("#1f88c6", "#e0782e", head="#1a6c9c", wing="#1b6a8c", tail="#1a5a8a", bill="#1a1818", leg="#e0603a",
            cheek="#e0782e", throat="#f4efe6", gcovTip="#3aa8d8", covTip="#2a90c0", sec="#1a5a7a", prim="#1a4a6a", primTip="#163e58",
            cyan="#4ccaf2", wht="#f4efe6", eye="#0e0a08")
    bird("kingfisher", "a common kingfisher on its perch: a big head and the long black dagger of a bill, electric blue back with the brilliant cyan stripe down to the rump, blue-green wings spotted paler, orange cheeks and underparts, white throat and neck patch, the stump of a tail, tiny red feet",
         .17, c, **M_(SMALL, dict(tilt=25, trunk=[.16, .11, .105], breast=[.11, .105, .1], bc=[.075, -.01],
         neck=[[.11, .07, .09], [.165, .1, .085]], head=[.19, .13], hr=[.1, .088, .084],
         bill=dict(len=.21, r=.032, droop=3, depth=1.15, comp=.46, blade=True, taper=1.0, tipK=.97, lowK=.85, minR=.0007, wTip=.9),   # (C 2026-11-07: a dagger, not a slab)
         tail=dict(len=.16, w=.06, n=5, ang=-6, spread=.2),
         fold=dict(S=[.08, .06, .1], T=[-.19, .01, .058], H=.1, w=.045, pad=PAD(out=.026, th=.028, col="@cov", tipCol="@primTip",
                   patches=[dict(x=x_, y=y_, rx=.05, ry=.06, col="@gcovTip") for x_, y_ in ((.14, .22), (.26, .2), (.2, .38), (.34, .36), (.12, .52), (.28, .52))])),
         tars=.05, legr=.011, toes=.07, eye=.018, gap=.006,   # (mesh in CLOSE) (C 2026-11-07: legr .007 left the stubby tarsus too thin for the grid at 1000 tris -- the feet floated)
         spread=dict(span=1.6, armF=.36, asp=2.2, tipC=.5, hsweep=.2), wing=dict(armK=1.25, th=(25, 70), rounded=True, n=NOTRACT),
         marks=[("b", "backP", [-.01, .065, 0], [.22, .075, .13], "@back", {"k": .006, "kc": .004, "op": "paint"}),   # (C 2026-11-07: a crisp blue back, no pink blend band)
                ("b", "rumpStripe", [-.05, .112, 0], [.17, .025, .022], "@cyan", {"k": .006, "kc": .003, "op": "paint"}),
                ("h", "neckW", [-.05, -.045, .07], [.03, .035, .02], "@wht", {"k": .006, "mirror": True}),
                ("h", "moustache", [.02, -.05, .06], [.05, .015, .02], "@back", {"k": .005, "mirror": True})])))

@sp
def gull():
    c = pal("#a9b2bb", "#f4f4f2", head="#f4f4f2", wing="#a9b2bb", tail="#f2f2f0", bill="#f0c830", leg="#e0a8a0",
            rump="#f2f2f0", neck="#f4f4f2", secTip="#f4f4f2", prim="#1a1a1a", primTip="#2a2a2a", red="#d8302a", ring="#e0a020", eye="#e8e0a0")
    coats = [{"name": "herring gull"},   # (B 2026-11-07: the gulls of the shore, each at its own size)
             {"name": "black-headed gull", "scale": .64, "head": "#3e2c24", "crown": "#3a2a22", "cheek": "#3e2c24", "throat": "#44322a", "neck": "#f4f4f2", "bill": "#a8242a", "billLo": "#a8242a",
              "red": "#a8242a", "leg": "#b02a30", "web": "#b02a30", "back": "#b8c0c8", "wing": "#b8c0c8", "cov": "#b8c0c8", "covTip": "#b8c0c8", "gcov": "#b8c0c8", "gcovTip": "#c0c8d0",
              "sec": "#b8c0c8", "wpad": "#a8b0b8", "ring": "#8a2a2a", "eye": "#1a120c"},
             {"name": "lesser black-backed gull", "scale": .92, "back": "#4e545c", "wing": "#4e545c", "cov": "#4e545c", "covTip": "#4e545c", "gcov": "#4e545c", "gcovTip": "#585e66",
              "sec": "#4e545c", "wpad": "#464c54", "leg": "#e8c84a", "web": "#e0c040", "ring": "#d8402a"},
             {"name": "great black-backed gull", "scale": 1.2, "back": "#24282e", "wing": "#24282e", "cov": "#24282e", "covTip": "#24282e", "gcov": "#24282e", "gcovTip": "#2c3036",
              "sec": "#24282e", "wpad": "#202428", "ring": "#d8402a"}]
    c["web"] = "#d89890"
    bird("gull", "a herring gull standing on the shore: white, the pale grey mantle and wings, the black wingtips crossing over the white tail, the stout yellow bill hooked at the tip with its red spot, pale eye in an orange ring, pink legs and webbed feet",
         .6, c, lid="@ring", **M_(BIG, dict(tilt=0, trunk=[.22, .12, .12], breast=[.13, .115, .11], bc=[.12, -.02],
         neck=[[.16, .06, .08], [.23, .125, .065]], head=[.27, .16], hr=[.075, .064, .06],
         bill=dict(len=.11, r=.025, droop=4, hook=.012, depth=1.15),
         tail=dict(len=.13, w=.075, n=6, ang=-2, spread=.24),   # (C final: under the wingtips, which reach past it)
         # (C final: one smooth grey pad, the black wingtip and its white spot painted on its rear -- the tracts stood up as black
         #  fins over the back and splayed out sideways, seen from behind)
         fold=dict(S=[.1, .05, .115], T=[-.42, .035, .05], H=.11, w=.055,
                   pad=PAD(col="@wpad", tipCol="@prim", tip=False, len=.64, patches=[dict(x=.86, y=.48, rx=.2, ry=.62, col="@prim", rot=-4, paint=True),
                                                                                      dict(x=.93, y=.46, rx=.035, ry=.16, col="@secTip", rot=-4, paint=True)])),
         tars=.12, legr=.012, toes=.12, web="@web", tibia="@leg", tib=.03, tuck="back",
         spread=dict(span=2.3, armF=.46, asp=3.8, tipC=.18, hsweep=.55, pinch=.8), wing=dict(armK=1.15, th=(30, 82), pointed=True, tert=.36, prim=.05, n=NOTRACT),
         flags={"print": "bird", "shy": 6, "peck": .6, "shore": True}, coats=coats,
         marks=[("h", "gonys", [.145, -.035, 0], [.012, .01, .013], "@red", {"k": .003})])))

@sp
def goose():
    c = pal("#7f7666", "#a8a090", head="#8a8274", wing="#7a7262", tail="#6e685e", bill="#e88a3a", leg="#e0a0a0",
            vent="#f0ece4", rump="#c8c4ba", covTip="#c8c0b0", gcovTip="#cfc7b6", sec="#4e4a46", secTip="#8a8276", prim="#5a5a5e", primTip="#3e3e42",
            tailTip="#e8e4dc", belly="#c4bcb0", eye="#1a120c", chin="#8a8274", web="#d89090")
    coats = [{"name": "greylag goose"},   # (B 2026-11-07: the farmyard's white goose and the Canada goose -- the black neck, the white chinstrap)
             {"name": "domestic white goose", "scale": 1.08, "back": "#f2f0ea", "under": "#f4f2ec", "head": "#f2f0ea", "crown": "#f2f0ea", "cheek": "#f2f0ea", "throat": "#f4f2ec", "neck": "#f2f0ea",
              "chin": "#f2f0ea", "rump": "#f2f0ea", "vent": "#f6f4ee", "thigh": "#f4f2ec", "belly": "#f4f2ec", "cov": "#efede6", "covTip": "#f2f0ea", "gcov": "#efede6", "gcovTip": "#f2f0ea",
              "sec": "#ecebe4", "secTip": "#f2f0ea", "prim": "#e8e6e0", "primTip": "#e2e0da", "tail": "#f2f0ea", "tailTip": "#f6f4ee", "wing": "#efede6", "wpad": "#e6e4dc",
              "bill": "#f08a2a", "billLo": "#f08a2a", "leg": "#f0902a", "web": "#e88428", "eye": "#2a5a8a"},
             {"name": "Canada goose", "scale": 1.1, "back": "#6e5e4c", "under": "#cfc6b8", "head": "#141414", "crown": "#141414", "cheek": "#141414", "throat": "#141414", "neck": "#161616",
              "chin": "#f2f0ea", "rump": "#5e5040", "vent": "#f4f2ec", "thigh": "#b8ac9c", "belly": "#d8d0c4", "cov": "#6e5e4c", "covTip": "#a89a86", "gcov": "#6a5a48", "gcovTip": "#a49480",
              "sec": "#3e342a", "secTip": "#5a4e40", "prim": "#2e2a26", "primTip": "#22201e", "tail": "#1c1a18", "tailTip": "#1c1a18", "wing": "#6a5a48", "wpad": "#62543f",
              "bill": "#1a1a1a", "billLo": "#1a1a1a", "leg": "#1e1e1e", "web": "#1e1e1e"}]
    bird("goose", "a greylag goose grazing upright: heavy grey-brown body barred pale by its feather edges, the long thick neck held high, the big orange bill, white under the tail, pink legs and webbed feet",
         .82, c, **M_(BIG, dict(tilt=2, trunk=[.24, .13, .125], breast=[.14, .12, .115], bc=[.12, -.02],
         neck=[[.16, .06, .075], [.215, .14, .055], [.235, .25, .046], [.25, .34, .043]], head=[.29, .375], hr=[.062, .046, .042],
         bill=dict(len=.09, r=.03, droop=10),
         tail=dict(len=.14, w=.07, n=6, ang=8, spread=.3),
         fold=dict(S=[.11, .05, .12], T=[-.27, .03, .07], H=.12, w=.055,
                   pad=PAD(col="@cov", tipCol="@primTip", patches=[dict(x=.62, y=.6, rx=.16, ry=.26, col="@sec", rot=-6)]
                           )),   # (C 2026-11-07: no bars -- they meshed as broken pale dashes)
         tars=.1, legr=.014, toes=.11, web="@web", tibia="@leg", tib=.02, tuck="back",
         spread=dict(span=2.0, armF=.45, asp=3.2, tipC=.3, hsweep=.4, pinch=.7), wing=dict(armK=1.25, th=(22, 78), n=NOTRACT),
         flags={"print": "bird", "shy": 5, "peck": .9, "beg": 6}, coats=coats,
         flight=dict(speed=1.0, flyTurn={"neck": -70, "head": 70}),
         marks=[("b", "bellyP", [-.03, -.07, 0], [.15, .05, .09], "@belly", {"k": .02}),
                ("h", "chinstrap", [-.004, -.024, .022], [.03, .026, .022], "@chin", {"k": .004, "kc": .002, "mirror": True, "rot": 20})])))

@sp
def stork():
    c = pal("#f2f2ee", "#f4f4f0", wing="#f0f0ec", tail="#f2f2ee", bill="#d8402a", leg="#d8503a",
            sec="#151515", secTip="#101010", prim="#141414", primTip="#0e0e0e", pcov="#141414", pcovTip="#101010", gcovTip="#e8e8e4", blk="#1a1a1a", eye="#1a120c")
    bird("stork", "a white stork on the meadow: tall and white, the black flight feathers along the folded wing's rear half, the long straight red bill, long red legs, the neck carried straight and a little forward",
         1.0, c, lid="@blk", **M_(BIG, dict(tilt=0, trunk=[.2, .11, .1], breast=[.12, .105, .095], bc=[.1, 0],
         neck=[[.15, .05, .06], [.21, .14, .05], [.245, .25, .045], [.265, .33, .042]], head=[.3, .37], hr=[.05, .04, .038],
         bill=dict(len=.24, r=.026, droop=22, depth=1.1),
         tail=dict(len=.13, w=.06, n=6, ang=-4, spread=.3),
         fold=dict(S=[.1, .04, .1], T=[-.27, -.02, .06], H=.1, w=.045,   # (C final: one smooth pad, its rear half painted black -- no loose covert discs)
                   pad=PAD(col="@wpad", tipCol="@primTip", tip=False, dx=-.015, len=.56, patches=[dict(x=.7, y=.5, rx=.4, ry=.64, col="@sec", rot=-4, paint=True)])),   # (no separate tip lobe: it read as a loose disc)
         tars=.25, tib=.2, legr=.011, toes=.09, tibia="@leg", web="#c84a36", tuck="trail",
         spread=dict(span=2.5, armF=.5, asp=3.0, tipC=.62, hsweep=.08, fingered=True, kink=.08), wing=dict(armK=1.45, th=(15, 80), hand=.42, rounded=True, n=NOTRACT),
         walk=dict(deg=20, speed=.55, flex=26),
         flags={"print": "bird", "shy": 8, "peck": .45, "shore": True},
         flight=dict(speed=.6, flyTurn={"neck": -62, "head": 60}))))

@sp
def crane():
    c = pal("#8e9398", "#a0a4a8", head="#1e1e20", wing="#8a8f94", tail="#3a3a3e", bill="#9a9a7a", leg="#1a1a1a",
            neck="#1e1e20", throat="#1e1e20", cheek="#1e1e20", sec="#2a2a2e", secTip="#1e1e22", prim="#222226", primTip="#18181a",
            wht="#eeeeec", red="#c82a20", bustle="#3a3a3e", eye="#c8402a")
    def bustle(B, M, R, u):
        # (C final: over the pad now -- rooted on the back above it, the plumes drooping over the pad's rear and the tail)
        rows = [row(B([-.05, .112, z]), B([-.32, -.02, z * 1.9]), .07 * u) for z in (.075, 0, -.075)]
        return [fea("bustle", rows, 7, "@bustle", "#222224", outline="round", up=[0, 1, .0], camber=.14, curve=-.08, lift=.004 * u, stagger=.003 * u, seed=9, mirror=False)]
    bird("crane", "a common crane stalking: tall, ash-grey, the black neck and head with the white stripe from behind the eye down the neck, the red crown, a long dagger bill; the bustle of drooping dark tertials over the tail; long black legs",
         1.1, c, **M_(BIG, dict(tilt=0, trunk=[.19, .11, .1], breast=[.11, .1, .09], bc=[.1, 0],
         neck=[[.14, .05, .045], [.2, .16, .029], [.225, .28, .024], [.245, .38, .022]], neckK=[.04, .02], head=[.28, .41], hr=[.045, .037, .034],   # (2026-11-08: slender -- was .055/.042/.037/.035, k .04/.03)
         bill=dict(len=.17, r=.015, droop=14),
         tail=dict(len=.16, w=.06, n=5, ang=-6, spread=.3),
         fold=dict(S=[.09, .04, .095], T=[-.25, -.01, .055], H=.1, w=.045, pad=PAD(col="@wpad", tipCol="@primTip")),   # (C final: the pad -- no covert discs)
         tars=.25, tib=.22, legr=.01, toes=.09, tibia="@leg", tuck="trail",
         spread=dict(span=2.5, armF=.5, asp=3.0, tipC=.62, hsweep=.08, fingered=True, kink=.08), wing=dict(armK=1.65, th=(15, 80), hand=.42, rounded=True, n=NOTRACT),
         walk=dict(deg=20, speed=.5, flex=26),
         flags={"print": "bird", "shy": 9, "peck": .4, "shore": True},
         flight=dict(speed=.6, flyTurn={"neck": -70, "head": 70}),
         marks=[("h", "crownR", [-.005, .033, 0], [.022, .01, .02], "@red", {"k": .003}),
                ("h", "stripe", [-.035, -.008, .03], [.04, .012, .02], "@wht", {"k": .004, "kc": .004, "mirror": True, "op": "paint"}),   # (C 2026-11-07: paint, not slivers)
                ("m", "neckStripe", [.215, .27, .03], [.014, .075, .022], "@wht", {"k": .004, "kc": .008, "mirror": True, "bone": "neck2", "op": "paint"})],
         extra=bustle)))

def tail_alt(f, base, when):
    """post(): the tail gated `base`, and a second, `f` as long, gated `when` (a pheasant hen's short tail)"""
    def post(B, M, R, u, sh):
        import json as _j
        out = []
        for q in sh:
            if q.get("type") == "feathers" and q.get("id") == "tail":
                q["when"] = base; t = _j.loads(_j.dumps(q)); t["id"] = "tailH"; t["when"] = when
                for r_ in t["rows"]: r_["to"] = [round(a + (b - a) * f, 4) for a, b in zip(r_["at"], r_["to"])]; r_["w"] = round(r_["w"] * 1.25, 4)
                out.append(t)
        return out
    return post

@sp
def pheasant():
    c = pal("#b0602a", "#a8502a", head="#1c4a3a", wing="#9a6a3a", tail="#a88050", bill="#c8b48a", leg="#7a7470",
            neck="#2a3a5a", throat="#1c4a3a", cheek="#1c4a3a", crown="#2a5a3a", flank="#c8883a", covTip="#e0c090", gcov="#8a6a4a", gcovTip="#d8b888",
            sec="#6a5a40", secTip="#a08a60", prim="#5a4a36", primTip="#4a3c2c", tailTip="#8a6840", red="#c8241c", wht="#f0eee8", eye="#c8a030")
    bird("pheasant", "a cock pheasant: copper and gold, the bottle-green head with the red wattled face and the white collar, the long tapering barred tail; short horn-coloured bill, grey legs",
         .8, c, **M_(MED, dict(tilt=6, trunk=[.19, .085, .078], breast=[.105, .08, .074], bc=[.09, -.005],
         neck=[[.13, .07, .05], [.18, .14, .038]], head=[.205, .185], hr=[.046, .041, .038],
         bill=dict(len=.045, r=.02, droop=22),
         tail=dict(len=.6, w=.035, n=6, ang=10, spread=.05, lens=[.6, .85, 1.0, .85, .6], bars={"n": 14, "dark": .55}),
         fold=dict(S=[.08, .04, .085], T=[-.2, .0, .05], H=.08, w=.04,
                   pad=PAD(col="@gcov", tipCol="@primTip", patches=[dict(x=.3, y=.3, rx=.3, ry=.26, col="@wing", rot=-6), dict(x=.62, y=.6, rx=.16, ry=.26, col="@sec", rot=-6)])),   # (C 2026-11-07: no bars -- they meshed as pale dashes)
         tars=.12, legr=.009, toes=.07, tuck="back",
         spread=dict(span=1.0, armF=.38, asp=2.0, tipC=.6, hsweep=.12), wing=dict(armK=.8, th=(12, 58), rounded=True, tert=.5, hand=.3, n=NOTRACT),
         flags={"print": "bird", "shy": 7, "peck": 1.1},
         params={"cock": True, "hen": False}, post=tail_alt(.45, "cock", "hen"),
         variants={"hen": {"scale": .82, "params": {"cock": False, "hen": True},   # (B 2026-11-07: the hen -- mottled buff and brown all over, the short tail)
                           "colors": {"back": "#9a7a52", "under": "#b8986a", "rump": "#9a7a52", "vent": "#b8986a", "neck": "#a88a60", "head": "#a08258", "crown": "#7a5e3e",
                                      "cheek": "#b09468", "throat": "#c4a87a", "thigh": "#b8986a", "tail": "#8a6a44", "tailTip": "#6a5034", "cov": "#7e6040", "covTip": "#c8aa7a",
                                      "gcov": "#7a5c3e", "gcovTip": "#c0a070", "sec": "#6a5438", "secTip": "#a88c62", "prim": "#5e4a34", "primTip": "#4a3a2a", "wpad": "#74583a",
                                      "flank": "#a8885a", "red": "#a08258", "wht": "#a88a60", "tert": "#6a5438", "tertTip": "#a88c62"}}},
         marks=[("h", "wattle", [.025, -.005, .03], [.03, .03, .012], "@red", {"k": .004, "mirror": True}),
                ("m", "collar", [.16, .11, 0], [.02, .012, .05], "@wht", {"k": .004, "bone": "neck", "rot": -40}),
                ("b", "flankG", [-.02, -.04, .05], [.12, .06, .05], "@flank", {"k": .02, "mirror": True})])))

# ---- round 9: five new birds (the rooster is rooster.py, from the chicken) ----
@sp
def penguin():
    c = pal("#56606c", "#f6f4ee", head="#141416", wing="#2a3038", tail="#1e2228", bill="#18181a", leg="#2a2a2e",
            neck="#141416", throat="#141416", cheek="#141416", crown="#101012", rump="#3a424c", vent="#f2f0ea",
            billLo="#e8782a", orange="#f08a1e", gold="#f4b43a", cream="#f6e6b0", blk="#16181c", flipper="#262c36", flipperIn="#f2f0ea", eye="#2a1a10")
    bird("penguin", "a king penguin standing upright: the silver-grey back and the black head, the orange comma of each ear patch running down to the golden upper breast, the white belly; the long slender bill, black with the orange stripe along the lower mandible; stiff narrow flippers held out a little from the flanks, the short black feet; it waddles",
         1.0, c, lid="@blk", **M_(MED, dict(mesh=[3600, 1300], tilt=82, trunk=[.33, .16, .15], breast=[.24, .15, .14], bc=[.02, -.03],
         neck=[[.07, .24, .1], [.09, .33, .075]], head=[.1, .39], hr=[.07, .062, .058],
         bill=dict(len=.11, r=.016, droop=14, curve=12, depth=1.0),
         tail=dict(len=.07, w=.05, n=4, ang=-30, spread=.3),
         fold=dict(S=[.17, .03, .15], T=[-.1, .02, .14], H=.08, w=.04),
         tars=.02, legr=.02, toes=.06, legx=-.05, legz=.06, web="#2a2a2e", gap=.004, toeR=.9, eye=.03,
         flightless=True, flipper=dict(len=.32, w=.085, ang=76, out=6, flap=10), waddle=9, kc=.006,
         walk=dict(deg=14, speed=1.5, flex=10),
         flags={"print": "bird", "shy": 3, "peck": .25, "shore": True},
         coats=[{"name": "king penguin"},   # (B 2026-11-07: the emperor -- a third heavier, the ear patches pale yellow, the breast's gold fading to white)
                {"name": "emperor penguin", "scale": 1.15, "orange": "#f4cc52", "gold": "#f6e6a6", "cream": "#f8f2dc", "back": "#4a525e", "billLo": "#e8907a"}],
         marks=[("b", "paunch", [-.12, -.05, 0], [.19, .13, .14], "@under", {"k": .05}),
                ("h", "ear", [-.035, -.03, .045], [.035, .026, .018], "@orange", {"k": .005, "mirror": True, "rot": -30}),
                ("p", "earRun0", [-.02, -.075, 0], [.045, .022, .02], "@orange", {"k": .005, "kc": .012, "dir": [.15, 0, 1], "side": True, "spin": -62, "mirror": True, "bone": "neck"}),
                ("p", "earRun1", [.002, -.125, 0], [.045, .026, .02], "@orange", {"k": .005, "kc": .012, "dir": [.2, 0, 1], "side": True, "spin": -62, "mirror": True, "bone": "neck"}),
                ("p", "earRun2", [.025, -.175, 0], [.045, .03, .02], "@gold", {"k": .005, "kc": .012, "dir": [.3, 0, 1], "side": True, "spin": -60, "mirror": True}),
                ("b", "goldBib", [.2, -.12, 0], [.08, .05, .1], "@gold", {"k": .02, "kc": .03}),
                ("b", "creamBib", [.09, -.14, 0], [.07, .04, .1], "@cream", {"k": .02, "kc": .03})])))

# ---- the OSTRICH's plumage (2026-11-05): no tiled wing -- loose PLUMES. The white wing plumes long, narrow and soft,
#      drooping over the flank and fanned back over the hips (two layers, the upper lifted over the lower); a HEM of soft
#      black plumes hanging below the belly line, the thighs' tops lost in it; the tail a drooping white tuft. Every root a
#      hair inside the body (along the way in to the trunk's axis), every tip pushed off it: they drape, none sinks ----
def ostrich_plumes(B, M, R, u, sh):
    from bg import field
    body = [q for q in sh if q.get("type") != "feathers" and q.get("bone", "body") == "body"]
    def inb(p, c=(0, 1.2, 0), d=.006):   # (along the way in to the trunk's axis until d inside)
        p = list(p); v = nrm([c[0] * 0 + p[0] * 0, c[1] - p[1], c[2] - p[2]])
        for _ in range(400):
            if field(body, p) <= -d: break
            p = add(p, v, .002)
        return [round(x, 4) for x in p]
    def off(p, m):   # (out along the field's slope until m off the body)
        p = list(p)
        for _ in range(300):
            f = field(body, p)
            if f >= m: break
            g = [field(body, add(p, [.003 if k == i else 0 for k in range(3)])) - f for i in range(3)]; p = add(p, nrm(g), .003)
        return [round(x, 4) for x in p]
    def grp(id, spec, n, col, tip, m, **kw):
        rows = []
        for at, dv, L, w in spec:
            a = inb(at); rows.append(row(a, off(add(a, nrm(dv), L), m), w))
        return fea(id, rows, n, col, tip, outline="round", mirror=kw.pop("mirror", True), **kw)
    sh[:] = [q for q in sh if q.get("id") not in ("prim", "sec", "tert")]
    soft = dict(camber=.04, jitter=.2, vary=.2)
    out = [
        # (the wing plumes: the lower layer longer and further down over the hip, the upper over it)
        grp("plumeB", [([.18, 1.14, .27], [-.05, -1, .14], .4, 0.0529), ([.06, 1.16, .29], [-.15, -1, .12], .44, 0.0529), ([-.06, 1.18, .29], [-.35, -.94, .1], .5, 0.0529),
                       ([-.18, 1.21, .27], [-.6, -.8, .08], .52, 0.0517), ([-.3, 1.25, .23], [-.85, -.53, .05], .48, 0.0506)],
            11, "@sec", "@secTip", .02, up=[0, .8, .6], curve=-.22, stagger=.005, seed=71, **soft),
        grp("plumeA", [([.22, 1.2, .28], [-.02, -1, .16], .32, 0.0552), ([.1, 1.22, .3], [-.1, -1, .14], .36, 0.0552), ([-.02, 1.25, .3], [-.3, -.95, .12], .42, 0.0552),
                       ([-.14, 1.28, .29], [-.55, -.83, .09], .44, 0.054), ([-.27, 1.31, .25], [-.8, -.6, .05], .42, 0.0529)],
            11, "@prim", "@primTip", .03, up=[0, .8, .6], curve=-.2, stagger=.005, lift=.008, seed=72, **soft),
        # (the hem: soft black plumes hanging from the lower flank, flaring a little at their ends)
        grp("hemA", [([.32, 1.06, .17], [.1, -1, .25], .2, 0.084), ([.15, 1.03, .21], [0, -1, .32], .24, 0.0864), ([-.05, 1.02, .22], [-.08, -1, .32], .26, 0.0864),
                     ([-.25, 1.04, .2], [-.2, -1, .28], .24, 0.084), ([-.4, 1.08, .14], [-.35, -1, .2], .2, 0.0792)],
            9, "@back", "@covTip", .012, up=[0, 0, 1], curve=.06, stagger=.004, lift=.004, seed=73, **soft),
        grp("hemB", [([.26, 1.0, .1], [.05, -1, .12], .17, 0.0825), ([.06, .97, .14], [0, -1, .16], .2, 0.085),
                     ([-.15, .97, .14], [-.1, -1, .16], .21, 0.085), ([-.32, 1.0, .1], [-.25, -1, .12], .18, 0.08)],
            6, "@vent", "@covTip", .01, up=[0, 0, 1], curve=.05, stagger=.004, seed=74, **soft),
        # (the tail's tuft: white plumes from the rump drooping over the tail's fan)
        grp("tuft", [([-.42, 1.36, .12], [-.55, -.83, .25], .36, 0.0506), ([-.46, 1.4, 0], [-.6, -.8, 0], .4, 0.0528), ([-.42, 1.36, -.12], [-.55, -.83, -.25], .36, 0.0506)],
            8, "@tail", "@tailTip", .03, up=[-.6, .8, 0], curve=-.12, stagger=.004, lift=.006, seed=75, mirror=False, **soft),
    ]
    return out

@sp
def ostrich():
    c = pal("#2a2525", "#2c2727", head="#c49a92", wing="#262222", tail="#f2efe8", bill="#d8b4a0", leg="#d8a898",
            neck="#c49a92", throat="#c49a92", cheek="#c49a92", crown="#8a7870", thigh="#d0a090", vent="#1e1c1c",
            cov="#1a1818", covTip="#262222", gcov="#1c1a1a", gcovTip="#2e2a2a", sec="#f2efe8", secTip="#ffffff", prim="#f4f1ea", primTip="#ffffff",
            tailTip="#ffffff", collar="#f2efe8", eye="#2a1a10", lash="#2a2020")
    bird("ostrich", "a male ostrich: the great black body of loose plumes, the white plumes of the wings and the tail, the long bare pinkish neck with the ruff of white at its base, the small flat head with the huge eye and the broad flat bill; the bare pink thighs and the thick legs, two toes to each foot, the big one clawed; it cannot fly",
         2.0, c, lid="@lash", **M_(BIG, dict(tilt=8, trunk=[.24, .15, .14], breast=[.14, .13, .12], bc=[.1, -.02],
         neck=[[.17, .08, .06], [.23, .25, .04], [.255, .42, .03], [.27, .58, .027]], head=[.295, .645], hr=[.045, .036, .035],
         bill=dict(len=.06, r=.02, droop=6, depth=.7),
         tail=dict(len=.16, w=.03, n=9, ang=50, spread=.55, camber=.05),
         fold=dict(S=[.12, .07, .135], T=[-.22, -.02, .1], H=.15, w=.07, pad=None, lay=False),
         tars=.25, tib=.2, legr=.022, toes=.11, toeR=.95, toes2=True, thighR=[.075, .11, .06], tibia="@thigh", eye=.06,
         flightless=True, wing=dict(armK=.8, th=(20, 70), rounded=True, tert=.5, hand=.35),
         walk=dict(deg=26, speed=.7, flex=24),
         flags={"print": "bird", "shy": 5, "peck": .5},
         marks=[("m", "ruff", [.17, .11, 0], [.05, .045, .065], "@collar", {"k": .015, "bone": "neck"})],
         pats={k_: {"pat": "shag", "fleece": {"amp": .009, "size": .05}} for k_ in ("trunk", "breast", "belly", "back", "rump", "vent", "wing")},
         variants={"hen": {"scale": .9, "colors": {   # (B 2026-11-07: the hen -- grey-brown all over, the plumes of the wings and the tail a paler dun)
             "back": "#6e6254", "under": "#74685a", "rump": "#6e6254", "vent": "#665a4c", "cov": "#64584a", "covTip": "#74685a", "gcov": "#64584a", "gcovTip": "#7a6e60",
             "sec": "#a89c8a", "secTip": "#b4a896", "prim": "#aca08e", "primTip": "#b8ac9a", "tert": "#a89c8a", "tertTip": "#b4a896", "tail": "#a49886", "tailTip": "#b0a492",
             "collar": "#8a7e6e", "wpad": "#5e5244", "neck": "#a8968a", "head": "#a8968a", "cheek": "#a8968a", "throat": "#a8968a", "thigh": "#b0a094", "leg": "#b8a8a0"}}},
         post=ostrich_plumes)))

@sp
def toucan():
    c = pal("#141214", "#161416", head="#141214", wing="#141214", tail="#121012", bill="#8ac83a", leg="#5a7aa8",
            throat="#f4d82a", cheek="#f4d82a", vent="#161416", billLo="#5a9ad8", band="#f08a1a", tipR="#c8241c", red="#d02a20",
            orbit="#a8d83a", rump="#1a1818", eye="#1a120c", redE="#d02a20")
    # (COATS, picked by seed in game: keel-billed (the asset's own), toco, channel-billed, chestnut-mandibled -- the bill's
    #  zones (upper, lower, the band, the tip), the face and bib, the bib's red edge and the eye's skin each a colour)
    coats = [{"name": "keel-billed toucan"},
             {"name": "toco toucan", "params": {"toco": True, "billS": False}, "bill": "#f08a1a", "billLo": "#ec7c14", "band": "#f6a02a", "tipR": "#141212", "throat": "#f6f4ee", "cheek": "#f6f4ee",
              "redE": "#f6f4ee", "orbit": "#3a74d8"},
             {"name": "channel-billed toucan", "bill": "#161416", "billLo": "#161416", "band": "#e8c43a", "tipR": "#161416", "throat": "#f2a02a", "cheek": "#f4b83a",
              "orbit": "#4a7ae0"},
             {"name": "chestnut-mandibled toucan", "bill": "#f0cc2a", "billLo": "#5a2418", "band": "#f0cc2a", "tipR": "#e8c020", "throat": "#f4d82a", "cheek": "#f4d82a",
              "orbit": "#b8d84a"}]
    bird("toucan", "a keel-billed toucan: the huge keeled bill, lime green with the orange band down its side, the tip red, the lower mandible blue; black all over but for the lemon-yellow face, throat and bib edged red below, the red under the tail and the yellow-green skin round the eye; blue feet",
         .5, c, **M_(MED, dict(mesh=[2600, 1000], tilt=40, trunk=[.175, .105, .1], breast=[.11, .095, .09], bc=[.075, -.015],
         neck=[[.08, .1, .075], [.11, .155, .066]], head=[.13, .195], hr=[.072, .067, .062],
         bill=dict(len=.33, r=.055, droop=8, curve=12, depth=1.5, comp=.5, blade=True, zones=[[.5, .78, "@band"], [.86, 1.01, "@tipR"]], alt={"s": 1.17, "when": "toco", "base": "billS"}),   # (as long as the body; the toco's a sixth longer again)
         tail=dict(len=.31, w=.085, n=11, ang=-24, spread=.04, camber=.3),
         fold=dict(S=[.07, .06, .1], T=[-.17, .02, .065], H=.1, w=.05),
         tars=.085, legr=.01, toes=.065, eye=.035, gap=.035, legx=.03,
         spread=dict(span=1.15, armF=.38, asp=2.0, tipC=.6, hsweep=.12), wing=dict(armK=.9, th=(20, 65), rounded=True, hand=.35, prim=0),
         flags={"print": "bird", "shy": 5, "peck": .7}, coats=coats, params={"toco": False, "billS": True},
         flight=dict(speed=1.2),
         marks=[("h", "bib", [.03, -.075, 0], [.065, .055, .062], "@throat", {"k": .008}),
                ("m", "bibN", [.13, .12, 0], [.06, .07, .07], "@throat", {"k": .01, "bone": "neck"}),
                ("p", "redEdge", [.04, -.15, 0], [.014, .05, .006], "@redE", {"decal": True, "dir": [.7, -1, 0]}),
                ("b", "undertail", [-.165, -.045, 0], [.045, .035, .05], "@red", {"k": .008}),
                ("h", "orbit", [.025, .012, .05], [.026, .022, .016], "@orbit", {"k": .004, "mirror": True})])))

@sp
def ibis():
    c = pal("#e0382a", "#e8452e", head="#e0382a", wing="#dc3628", tail="#d83226", bill="#b84a3a", leg="#e04030",
            neck="#e44030", cheek="#e85040", sec="#d43024", secTip="#c82a20", prim="#d83226", primTip="#141010",
            gcovTip="#e85040", eye="#2a1a10")
    bird("ibis", "a scarlet ibis wading: brilliant scarlet all over, the wingtips black; the long down-curved bill, reddish and darker toward the tip; long scarlet legs; it flies with the neck stretched out and the legs trailing",
         .6, c, **M_(MED, dict(tilt=4, trunk=[.18, .1, .095], breast=[.11, .095, .09], bc=[.09, 0],
         neck=[[.13, .05, .055], [.19, .12, .045], [.215, .2, .04]], head=[.24, .24], hr=[.045, .038, .035],
         bill=dict(len=.26, r=.02, droop=16, curve=26, depth=1.0),
         tail=dict(len=.1, w=.05, n=5, ang=-4, spread=.3),
         fold=dict(S=[.09, .04, .095], T=[-.24, -.01, .055], H=.09, w=.045, pad=PAD(col="@wpad", tipCol="@primTip")),   # (C final: a pad -- no covert discs)
         tars=.17, tib=.12, legr=.009, toes=.09, tibia="@leg", tuck="trail",
         spread=dict(span=1.6, armF=.45, asp=2.7, tipC=.55, hsweep=.18, fingered=True), wing=dict(armK=1.3, th=(15, 80), hand=.4, rounded=True, n=NOTRACT),
         walk=dict(deg=20, speed=.7, flex=24),
         flags={"print": "bird", "shy": 7, "peck": .9, "shore": True},
         flight=dict(speed=1.0, flyTurn={"neck": -55, "head": 50}))))

@sp
def pelican():
    c = pal("#f4eeea", "#f6ece8", head="#f6f2ee", wing="#f2ece8", tail="#f2ece8", bill="#e8b4a0", leg="#f0a080",
            neck="#f6f0ec", gcovTip="#f6f2ee", sec="#1c1c1e", secTip="#202022", prim="#161618", primTip="#101012", pcov="#161618", pcovTip="#101012",
            billLo="#f0c850", pouch="#f2c43a", face="#f0c890", crest="#f8f4f0", breastY="#f4e4b8", eye="#8a2a1a")
    bird("pelican", "a great white pelican: big and white with a blush of pink, a pale yellow patch on the breast; the long bill hooked at the tip and the yellow pouch slung under it, the bare yellowish face; the black flight feathers showing along the folded wing and the whole black trailing half of the wing aloft, nearly three metres across; short orange-pink legs and webbed feet",
         1.6, c, lid="@face", **M_(BIG, dict(tilt=5, trunk=[.22, .12, .12], breast=[.13, .11, .11], bc=[.1, -.02],
         neck=[[.16, .06, .07], [.21, .14, .05], [.205, .23, .045], [.225, .29, .042]], head=[.255, .32], hr=[.05, .042, .04],
         bill=dict(len=.28, r=.022, droop=8, hook=.012, hookR=.26, tipR=.26, depth=.8),
         tail=dict(len=.1, w=.07, n=6, ang=2, spread=.3),
         fold=dict(S=[.11, .05, .12], T=[-.3, .02, .06], H=.12, w=.055,   # (C final: one smooth white pad, the black flight feathers painted along its rear and lower edge -- the tracts splayed out sideways, seen from in front and behind)
                   pad=PAD(col="@wpad", tipCol="@primTip", tip=False, dx=-.015, len=.56, patches=[dict(x=.76, y=.56, rx=.42, ry=.64, col="@prim", rot=-6, paint=True)])),
         tars=.07, tib=.05, legr=.012, toes=.1, web="#e89878", tibia="@leg", tuck="back",
         spread=dict(span=1.8, armF=.55, asp=3.4, tipC=.5, hsweep=.1, fingered=True, kink=.08), wing=dict(armK=1.4, th=(15, 80), hand=.4, rounded=True, n=NOTRACT),
         walk=dict(deg=22, speed=.7, flex=20),
         flags={"print": "bird", "shy": 6, "peck": .3, "shore": True},
         flight=dict(speed=.55, flyTurn={"neck": -40, "head": 35}),
         marks=[("h", "pouch", [.165, -.05, 0], [.12, .026, .022], "@pouch", {"k": .005, "rot": -8}),
                ("h", "faceP", [.03, .0, .03], [.03, .02, .012], "@face", {"k": .004, "mirror": True}),
                ("h", "crest", [-.05, .02, 0], [.03, .02, .02], "@crest", {"k": .006}),
                ("b", "breastY", [.13, -.03, 0], [.06, .06, .08], "@breastY", {"k": .015})])))

# ---- round 10 ----
import math as _m
from bg import ell
def crest(hc, hr, roots, angs, lens, w, col, tip, curve=0., outline="round", seed=31, id="crest", roll=0, bands=()):
    """a crest of single feathers in the midline, from `roots` (each a fraction along the crown, 0 its front, 1 its back)
       at `angs` (deg back from straight up) and `lens` (units): returns extra(B, M, R, u) for bird().
       roll: each blade turned this far (deg) from flat-on-the-side toward facing forward, the crest doubled (mirrored, a
       hair apart) -- so its `curve` bends the tips FORWARD (and a little apart, as a raised crest splays), not sideways.
       bands: (f0, f1, colour, tip colour, width) -- a piece laid over each feather from f0 to f1 of its length: a hoopoe's
       white band under the black tips"""
    def ex(B, M, R, u):
        rows, over = [], [[] for _ in bands]
        ph = _m.radians(roll); zo = w * .35 if roll else 0
        for f, a, Ln in zip(roots, angs, lens):
            r0 = [hc[0] + hr[0] * (.35 - .85 * f), hc[1] + hr[1] * (.75 - .2 * f * f)]
            d = [-_m.sin(_m.radians(a)), _m.cos(_m.radians(a))]
            upv = [round(_m.sin(ph) * d[1], 4), round(-_m.sin(ph) * d[0], 4), round(_m.cos(ph), 4)] if roll else None
            rows.append(row(M([r0[0], r0[1], zo]), M([r0[0] + d[0] * Ln, r0[1] + d[1] * Ln, zo]), round(w * u, 4), up=upv))
            for i, (f0, f1, c_, t_, wf) in enumerate(bands):
                over[i].append(row(M([r0[0] + d[0] * Ln * f0, r0[1] + d[1] * Ln * f0, zo]), M([r0[0] + d[0] * Ln * f1, r0[1] + d[1] * Ln * f1, zo]), round(w * wf * u, 4), up=upv))
        mir = {"mirror": True} if roll else {}
        out = [fea(id, rows, len(rows), col, tip, outline=outline, bone="head", up=[0, 0, 1], camber=0, curve=curve, seed=seed, **mir)]
        for i, (f0, f1, c_, t_, wf) in enumerate(bands):
            out.append(fea("%sB%d" % (id, i), over[i], len(rows), c_, t_, outline="round", bone="head", up=[0, 0, 1], camber=0, curve=curve,
                           lift=round(.0007 * u, 5), seed=seed, mirror=True, layer=True))   # (layer: it rests on its feather -- the root pass leaves it there)
        return out
    return ex

def both(*fs):
    """several extra(B, M, R, u) as one"""
    def ex(B, M, R, u):
        out = []
        for f in fs: out += f(B, M, R, u)
        return out
    return ex

def parrot_bill(hc, hr, Rc, col, colLo, wz=.8):
    """a parrot's bill: the upper mandible a deep arc from the top of the face, over and DOWN to the hooked tip that points
       back under it (a chain of ellipsoids along the culmen's circle, Rc its radius, deep at the base and laterally
       flattened), the broad scooped lower mandible tucked inside the hook"""
    def ex(B, M, R, u):
        b0 = [hc[0] + hr[0] * .82, hc[1] + hr[1] * .1]
        t0, t1 = 98., -62.; C = [b0[0] - Rc * _m.cos(_m.radians(t0)), b0[1] - Rc * _m.sin(_m.radians(t0))]
        n = 10; seg = Rc * _m.radians(t0 - t1) / (n - 1); out = []
        for i in range(n):
            f = i / (n - 1); th = t0 + (t1 - t0) * f; rr = Rc * (.44 * (1 - f) ** 1.15 + .05)
            p = [C[0] + (Rc - rr) * _m.cos(_m.radians(th)), C[1] + (Rc - rr) * _m.sin(_m.radians(th)), 0]
            out.append(ell("upperBill%d" % i, M(p), R([seg * .95, rr, rr * wz * (1 - .35 * f)]), col, k=.006 * u, kc=.0015 * u, bone="head", rot=[0, 0, round(th - 90, 1)]))
        out += [ell("lowerBill", M([C[0] + Rc * .05, C[1] - Rc * .22, 0]), R([Rc * .52, Rc * .36, Rc * .5]), colLo, k=.005 * u, kc=.0015 * u, bone="head", rot=[0, 0, 18]),
                ell("lowerLip", M([C[0] + Rc * .4, C[1] - Rc * .08, 0]), R([Rc * .2, Rc * .2, Rc * .38]), colLo, k=.004 * u, kc=.0015 * u, bone="head", rot=[0, 0, 30])]
        return out
    return ex

def vulture_bill(hc, hr, b, col):
    """the dark horn tip of the vulture's heavy hooked bill (where nb.py's bill tube ends in its hook)"""
    def ex(B, M, R, u):
        base = [hc[0] + hr[0] * .9, hc[1] - hr[1] * .12]
        def bp(f, dr):
            a = _m.radians(-(b["droop"] + b["curve"] * f * f)); return [base[0] + _m.cos(a) * b["len"] * f, base[1] + _m.sin(a) * b["len"] * f + dr]
        q1 = bp(.95, b["r"] * .1 * b["depth"] - b["hook"] * .6)
        return [ell("billTip", M([q1[0], q1[1], 0]), R([b["len"] * .42, b["r"] * 1.6, b["r"] * .9]), col, k=.007 * u, kc=.004 * u, bone="head",
                    rot=[0, 0, -(b["droop"] + b["curve"] * .8 + 40)], op="paint")]   # (C 2026-11-07: paint on the hook, no added lump)
    return ex

@sp
def vulture():
    c = pal("#b08a5e", "#a88458", head="#e2d8cc", wing="#7c5e3e", tail="#2e241c", bill="#b0a48c", leg="#8a8884",
            neck="#c4b0a4", throat="#cdbcb0", cheek="#d8ccc0", crown="#ece6dc", cov="#6a4e34", covTip="#5e442c", gcov="#4a3826", gcovTip="#3e2e20", mantle="#62482f",
            sec="#30261e", secTip="#221a14", tert="#3a2e22", tertTip="#2a2018", prim="#2a2018", primTip="#1a1410", tailTip="#221a14", ruff="#ece2cc", tip="#2a2622",
            eye="#5a3a1a", lid="#4a4040")
    hc, hr = [.335, .13], [.04, .033, .031]   # (C r9: smaller still, on a longer thinner neck)   # (C 2026-11-07: a small bare head on a thin neck, a raptor's hooked bill)
    bl = dict(len=.066, r=.024, droop=6, curve=30, hook=.02, depth=1.4, tipR=.3, hookR=.3)
    bird("vulture", "a griffon vulture standing hunched: the big body tilted up at the shoulders, the long folded wings draped down its sides and back, their dark flight feathers reaching the tail -- a broad dark back; the neck in an S, sunk into the thick, shaggy cream ruff, the small bald head held low and forward in short white down; the deep heavy hooked bill, horn with a dark tip; strong grey legs; aloft the huge broad wings, fingered at the tips, some 2.6 m across",
         1.25, c, lid="@lid", **M_(BIG, dict(tilt=32, trunk=[.25, .13, .13], breast=[.13, .12, .118], bc=[.11, -.015],
         neck=[[.14, .1, .062], [.2, .175, .03], [.26, .19, .021], [.305, .155, .019]], head=hc, hr=hr,
         bill=bl,
         tail=dict(len=.15, w=.08, n=6, ang=-10, spread=.3),
         fold=dict(S=[.13, .09, .15], T=[-.36, .0, .065], H=.18, w=.075),
         tars=.115, legr=.02, toes=.09, legz=.065, tuck="back", thighR=[.085, .1, .06],
         spread=dict(span=2.09, armF=.5, asp=2.3, tipC=.72, hsweep=.04, fingered=True, kink=.06), wing=dict(armK=1.3, th=(15, 80), hand=.42, rounded=True),
         walk=dict(deg=20, speed=.5, flex=20),
         flags={"print": "bird", "shy": 9, "peck": .6},
         flight=dict(speed=.45),
         marks=[("b", "mantle", [-.03, .085, 0], [.24, .07, .135], "@mantle", {"k": .03}),
                ("m", "ruff", [.16, .135, 0], [.07, .06, .118], "@ruff", {"k": .014, "kc": .006, "bone": "neck", "lumps": {"amp": .011, "size": .02}}),
                ("m", "ruffB", [.13, .11, 0], [.06, .05, .105], "@ruff", {"k": .012, "kc": .006, "lumps": {"amp": .007, "size": .022}})],
         extra=vulture_bill(hc, hr, bl, "@tip"))))

OWLF = dict(lobe=[.04, .003, .023], h=.006, ry=.034, rz=.022, out=.001, kd=.0018, rimOff=.0015, rimR=.0028, rimDent=.0003, rimA=(10, 225),
            brow=[[.047, .002, .002, .0026], [.043, .021, .01, .002], [.036, .031, .021, .0012]], browSink=.8,
            billAt=[.047, -.004, 0], bill=[[-.003, .0, .0056], [.004, -.004, .0046], [.0065, -.0095, .003], [.0048, -.0145, .0012]],
            billLo=[[-.002, -.005, .003], [.0025, -.0105, .0016]], brist=[-.001, .001, .0045, .004, .006, .0035])
def owl_face(hc, F=OWLF):
    """the tawny owl's face carved into its round head: two shallow dishes (one round each eye, @disc) meeting over the
       bill, a thin dark rim line flush with the feathers round their outer edge, the pale V of the brows on the ridge
       between them, and the small pale hooked bill set into that ridge, its base hidden in bristles"""
    import bg
    def ex(B, M, R, u, sh):
        K = M([hc[0], hc[1], 0]); f = lambda p: bg.field(sh, p)
        def surf(rel):
            d = bg.nrm(rel); p = bg.add(K, d, .15)
            while f(p) > 0: p = bg.add(p, d, -.0004)
            lo, hi = p, bg.add(p, d, .0004)
            for _ in range(20):
                m = bg.lerp(lo, hi, .5)
                if f(m) > 0: hi = m
                else: lo = m
            return hi, bg.grad(sh, hi, .001)
        def onS(p, n, sink):   # p brought onto the surface along n, then `sink` below it
            q = bg.add(p, n, .02)
            while f(q) > 0: q = bg.add(q, n, -.0002)
            return bg.add(q, n, -sink)
        out = []
        for sd in (1, -1):
            S0, n = surf([F["lobe"][0], F["lobe"][1], F["lobe"][2] * sd])
            dc = bg.add(S0, n, F["out"])
            up = bg.nrm(bg.sub([0, 1, 0], [n[1] * x for x in n])); ot = bg.nrm([n[1] * up[2] - n[2] * up[1], n[2] * up[0] - n[0] * up[2], n[0] * up[1] - n[1] * up[0]])
            if ot[2] * sd < 0: ot = [-x for x in ot]
            out.append({"id": "dish" + "LR"[sd < 0], "type": "ell", "c": bg.rnd(dc), "r": [F["h"], F["ry"], F["rz"]], "axes": [bg.rnd(n), bg.rnd(up), bg.rnd(ot)],
                        "k": F["kd"], "op": "sub", "color": "@disc", "bone": "head"})
            def inside(q):
                v = bg.sub(q, dc); return sum((sum(a * b for a, b in zip(v, ax)) / r) ** 2 for ax, r in ((n, F["h"]), (up, F["ry"]), (ot, F["rz"]))) < 1
            pts = []
            for a in range(F["rimA"][0], F["rimA"][1] + 1, 15):
                t = bg.add([math.cos(math.radians(a)) * x for x in up], ot, math.sin(math.radians(a)))
                rho = .004
                while rho < .06:
                    q = onS(bg.add(S0, t, rho), n, 0)
                    if not inside(q): break
                    rho += .0005
                q = onS(bg.add(S0, t, rho + F["rimOff"]), n, -(F["rimR"] - F["rimDent"]))
                pts.append(bg.rnd(q) + [F["rimR"]])
            out.append({"id": "rim" + "LR"[sd < 0], "type": "tube", "pts": pts, "k": .0003, "op": "sub", "color": "@rim", "bone": "head"})
            bp = [onS(bg.add(K, bg.nrm([b[0], b[1], b[2] * sd]), .06), bg.nrm([b[0], b[1], b[2] * sd]), b[3] * F["browSink"]) + [b[3]] for b in F["brow"]]
            out.append({"id": "brow" + "LR"[sd < 0], "type": "tube", "pts": [bg.rnd(p) for p in bp], "k": .0008, "kc": .0012, "color": "@brow", "bone": "head"})
        Sb, nb_ = surf(F["billAt"])
        for s_ in sh:
            if s_.get("id") == "upperBill": s_["pts"] = [bg.rnd(bg.add(Sb, [b[0], b[1], 0])) + [b[2]] for b in F["bill"]]; s_["k"] = .0015; s_["kc"] = .0006
            if s_.get("id") == "lowerBill": s_["pts"] = [bg.rnd(bg.add(Sb, [b[0], b[1], 0])) + [b[2]] for b in F["billLo"]]; s_["k"] = .0012; s_["kc"] = .0006
        br = F["brist"]
        out.append(ell("brist", bg.add(Sb, [br[0], br[1], br[2]]), br[3:], "@disc", k=.002, kc=.001, bone="head", mirror=True))
        return out
    return ex

def owl_coverts(A, B_, wid=.064, t=.02, proud=.003, spots=5, col="@cov", spot="@spot", k=.012):
    """the folded wing's coverts as one smooth shield on each flank (root space A -> B_ in x, y), over the roots of the
       barred flight feathers that come out from under its lower edge; a row of small pale scapular spots flush along
       its upper edge"""
    import bg
    def ex(B, M, R, u, sh):
        body = [q for q in sh if q.get("type") != "feathers" and q.get("bone", "body") not in ("head",)]
        f = lambda p: bg.field(body, p)
        def flank(x, y, z0=.2):
            p = [x, y, z0]
            while f(p) > 0 and p[2] > 0: p[2] -= .0004
            return p, bg.grad(body, p, .001)
        ax = bg.nrm([B_[0] - A[0], B_[1] - A[1], 0]); L2 = math.hypot(B_[0] - A[0], B_[1] - A[1]) / 2
        mid = [(A[0] + B_[0]) / 2, (A[1] + B_[1]) / 2]
        S0, n = flank(*mid)
        pr = bg.nrm([n[1] * ax[2] - n[2] * ax[1], n[2] * ax[0] - n[0] * ax[2], n[0] * ax[1] - n[1] * ax[0]])
        ax2 = bg.nrm([pr[1] * n[2] - pr[2] * n[1], pr[2] * n[0] - pr[0] * n[2], pr[0] * n[1] - pr[1] * n[0]])
        c = bg.add(S0, n, proud - t)
        out = [{"id": "covShield", "type": "ell", "c": bg.rnd(c), "r": [L2, wid / 2, t], "axes": [bg.rnd(ax2), bg.rnd(pr), bg.rnd(n)], "k": k, "kc": .003,
                "color": col, "pat": "palespots", "frame": {"o": "$body", "u": [0, 1, 0], "r": .026}, "mirror": True}]
        # (the spots: on the shield's upper edge -- the side of `pr` that points up)
        sg = 1 if pr[1] * .3 - pr[0] > 0 else -1
        allf = lambda p: bg.field(body + out[:1], p)
        for i in range(spots):
            a = -.75 + 1.5 * i / max(1, spots - 1)
            q = bg.add(bg.add(c, ax2, a * L2 * .95), pr, sg * wid * .2 * (1 - .25 * a * a))
            q = bg.add(q, n, .03)
            while allf(q) > 0: q = bg.add(q, n, -.0002)
            nq = bg.grad(body + out[:1], q, .001)
            out.append(flat("scap%d" % i, q, nq, ax2, [.0012, .0075, .005], spot, dent=.0004))
        return out
    return ex

def flat(id, q, n, along, r, col, dent=.0003, mirror=True, k=.0004):
    """a mark FLUSH with the surface at q (normal n): a CARVING a hair deep that paints what it opens (sculpt.js: a
       carving with a colour of its own) -- paint, not a plate; r: its half-thickness (along n), length, width"""
    import bg
    a = bg.nrm(bg.sub(along, [sum(x * y for x, y in zip(along, n)) * x for x in n])); w = bg.nrm([n[1] * a[2] - n[2] * a[1], n[2] * a[0] - n[0] * a[2], n[0] * a[1] - n[1] * a[0]])
    return {"id": id, "type": "ell", "c": bg.rnd(bg.add(q, n, r[0] - dent)), "r": r, "axes": [bg.rnd(n), bg.rnd(a), bg.rnd(w)], "k": k, "op": "sub",
            "color": col, **({"mirror": True} if mirror else {})}

def owl_streaks(ys=(.06, .155), n_=18, col="@strk", seed=3):
    """the dark shaft streaks down an owl's breast: flush marks, each along the body's vertical"""
    import bg, random
    def ex(B, M, R, u, sh):
        body = [q for q in sh if q.get("type") != "feathers" and q.get("bone", "body") not in ("head",) and not q.get("id", "").startswith(("scap", "covS"))]
        f = lambda p: bg.field(body, p); rg = random.Random(seed); out = []
        for i in range(n_):
            y = ys[0] + (ys[1] - ys[0]) * (i + rg.random() * .6) / n_; a = math.radians(rg.uniform(-55, 55))
            d = [math.cos(a), 0, math.sin(a)]; p = bg.add([.0, y, 0], d, .2)
            while f(p) > 0 and p[0] > -.2: p = bg.add(p, d, -.0004)
            n = bg.grad(body, p, .001)
            if n[1] < -.6: continue
            out.append(flat("strk%d" % i, p, n, [0, 1, 0], [.0012, .012 * rg.uniform(.7, 1.2), .0028], col, dent=.0004, mirror=False))
        return out
    return ex

def chain(*fs):
    def ex(B, M, R, u, sh):
        out = []
        for f_ in fs: out += f_(B, M, R, u, sh + out)
        return out
    return ex

@sp
def tawny_owl():
    c = pal("#8a5a34", "#c49a66", head="#8a5a34", wing="#7e5232", tail="#7a5030", bill="#dccf9c", leg="#d8bf94", thigh="#ccaa7a",
            crown="#7e5230", cheek="#8a5a34", throat="#b88c5a", cov="#7a5030", covTip="#e8d0a2", gcov="#7a5030", gcovTip="#6a4628", sec="#6e4a2c", secTip="#5e3e24",
            prim="#74502e", primTip="#5a3c22", tailTip="#5e3e24", disc="#b89068", rim="#2a1608", spot="#fff2d8", brow="#f4e6c6", strk="#4a2c16", talon="#3a3634",
            eye="#160c06", lid="#6e7888")
    hc, hr = [.09, .29], [.125, .12, .125]
    bird("tawny owl", "a tawny owl: plump, the big round head over an egg-shaped body, NO ear tufts; warm brown above mottled darker with a row of pale scapular spots, buff below with dark shaft streaks and fine bars; the facial disc of two lobes, one round each eye, meeting over the bill, rimmed by a thin dark line, the pale brows rising in a V from the bill; big dark eyes set into the disc in blue-grey lids; the small pale hooked bill half buried; the legs and toes feathered buff, dark talons",
         .38, c, lid="@lid", sink=.8, socket=1.12, **M_(MED, dict(tilt=60, trunk=[.19, .165, .185], breast=[.165, .165, .175], bc=[.04, -.02],
         neck=[[.06, .16, .11], [.072, .205, .1]], head=hc, hr=hr,
         bill=dict(len=.06, r=.014, droop=50, curve=40, hook=.01, depth=1.6),
         tail=dict(len=.11, w=.07, n=6, ang=-8, spread=.25, bars={"n": 4, "dark": .55}),
         fold=dict(S=[.1, .065, .17], T=[-.21, .03, .13], H=.13, w=.065, upright=True, tight=True, fw=1.7), mesh=[6000, 1200], cell=.0024, patScale=.15,
         tars=.045, legr=.026, toes=.055, zygo=True, tibia="@thigh", talons=.022, eye=.032, eyeAt=[.1, .022, .045], eyeFrom=[.0, .022, .045], focus={"head": 4},
         spread=dict(span=2.5, armF=.45, asp=2.0, tipC=.55, hsweep=.08), wing=dict(armK=1.1, th=(18, 72), rounded=True, pbars={"n": 5, "dark": .6}, sbars={"n": 4, "dark": .7},
                                                                                   n={"prim": 5, "sec": 4, "tert": 0, "gcov": 0, "pcov": 0, "cov": 0}),
         flags={"print": "bird", "shy": 6, "peck": .3},
         flight=dict(speed=.8),
         pats={**{k_: {"pat": "stripes", "frame": {"o": "$body", "u": [0, 0, 1], "v": [0, -1, 0], "r": .02}} for k_ in ("trunk", "back", "rump", "breast", "belly", "vent")},
               "wing": {"pat": "palespots", "frame": {"o": "$body", "u": [0, 1, 0], "r": .026}},
               **{k_: {"pat": "agouti"} for k_ in ("skull", "crown", "cheek", "neckA")},
               "throat": {"r": [.022, .016, .024], "k": .014, "c": [.0437, .176, 0], "pat": "agouti"}, "tarsus": {"pat": None, "frame": None, "k": .006, "lumps": {"amp": .0015, "size": .005}}},
         extra=owl_face(hc), post=owl_coverts([.03, .15], [-.05, .05], spots=0))))

@sp
def hoopoe():
    c = pal("#d8946a", "#dea07a", head="#da9a70", wing="#161412", tail="#161412", bill="#1e1a18", leg="#6a6260",
            crest="#d8905e", crestTip="#141210", cov="#161412", covTip="#121010", gcov="#161412", gcovTip="#121010", sec="#161412", secTip="#121010",
            tert="#161412", tertTip="#121010", prim="#161412", primTip="#121010", tailTip="#121010", rump="#f2eee6", wbar="#f4f0e8", eye="#1a120c")
    hc, hr = [.19, .12], [.052, .048, .044]
    bird("hoopoe", "a hoopoe: the cinnamon-pink head and body, the long fan of a crest tipped black and white, the long thin down-curved black bill; broad rounded wings and the tail barred boldly black and white, a white rump; short grey legs",
         .28, c, **M_(MED, dict(tilt=12, trunk=[.19, .09, .085], breast=[.1, .085, .08], bc=[.09, -.01],
         neck=[[.12, .05, .05], [.16, .085, .042]], head=hc, hr=hr,
         bill=dict(len=.2, r=.011, droop=18, curve=26),
         tail=dict(len=.3, w=.08, n=7, ang=-6, spread=.16, roof=16, band={"f0": .56, "f1": .74, "col": "@wbar", "top": True}),
         fold=dict(S=[.1, .045, .08], T=[-.3, .01, .05], H=.1, w=.055, pad=dict(out=.024, th=.03, col="@cov", tipCol="@prim", rim=0,
                   bars=dict(n=4, x0=.62, x1=-.24, w=.0068, h=.8, tilt=22, seg=4, col="@wbar", paint=True))),   # (C final: painted bars -- their blades went to a finer body)   # (four white bars across the black wing)
         tars=.08, tib=.03, legr=.0075, toes=.075, thighR=[.055, .06, .04],
         spread=dict(span=1.6, armF=.4, asp=1.8, tipC=.62, hsweep=.08,
                    strips=[{"x": .56, "w": .075, "col": "@wbar"}, {"x": .82, "w": .07, "col": "@wbar"}, {"x": .62, "w": .07, "col": "@wbar", "hand": True, "to": .75}]),
         wing=dict(armK=1.0, th=(20, 70), rounded=True, n=NOTRACT),   # (the fold: the barred pad alone -- its primaries splayed out sideways from the front and behind)
         flags={"print": "bird", "shy": 6, "peck": 1.1},
         flight=dict(speed=1.1),
         extra=crest(hc, hr, [0, .2, .4, .6, .8, 1.0], [62, 69, 76, 84, 91, 98], [.12, .155, .178, .175, .155, .12], .017, "@crest", "@crest", curve=0,
                     bands=((.6, 1.0, "@wbar", "@crestTip", .78),)))))

@sp
def woodpecker():
    c = pal("#141414", "#141414", head="#141414", wing="#141414", tail="#141414", bill="#3a3a3e", leg="#5a5a62",
            crown="#141414", cheek="#f2efea", throat="#f2efea", vent="#d0242a", cov="#f2efea", covTip="#ece8e2", gcov="#f0ece6", gcovTip="#e8e4de",
            sec="#d8d4cc", secTip="#161616", prim="#d0ccc4", primTip="#141414", tert="#161616", tertTip="#141414", wht="#f0ece6", tailTip="#1e1e1e", red="#d0242a", blk="#141414", eye="#1a0c0a",
            patch="#f0ece6", mous="#141414", ventC="#d0242a", padC="#141414", wbar="#f0ece6")
    coats = [{"name": "great spotted woodpecker"},   # (B 2026-11-07: the green woodpecker -- green above, the yellow rump, the red crown and nape, the black mask, pale below)
             {"name": "green woodpecker", "scale": 1.35, "back": "#5e7a2e", "under": "#c8cca0", "rump": "#c8c03a", "vent": "#c4c89c", "neck": "#6a8434", "head": "#5e7a2e", "crown": "#c8242a",
              "cheek": "#1a1a1a", "throat": "#d0d4ac", "thigh": "#b8bc90", "tail": "#4a5a28", "tailTip": "#2e3418", "cov": "#5e7a2e", "covTip": "#5a7430", "gcov": "#5a7430", "gcovTip": "#56702c",
              "sec": "#56682a", "secTip": "#3a4420", "prim": "#4a4a2e", "primTip": "#2e2e20", "tert": "#56702c", "tertTip": "#4a6026", "wpad": "#5a7430", "wht": "#c8cca0",
              "patch": "#5e7a2e", "mous": "#141414", "ventC": "#c4c89c", "padC": "#5a7430", "wbar": "#a8ac78", "red": "#c8242a", "eye": "#e8e4d8", "bill": "#4a4a50", "billLo": "#7a7a70"}]
    bird("woodpecker", "a great spotted woodpecker upright against a trunk: black above with the big white shoulder patches, the wings barred white, white beneath with the crimson vent; the black crown and the red nape (a male), white cheeks inside a black moustache; the straight chisel bill; the stiff pointed black tail propped beneath it; two toes forward, two back",
         .23, c, **M_(SMALL, dict(tilt=58, trunk=[.21, .095, .09], breast=[.12, .09, .085], bc=[.07, -.02],
         neck=[[.09, .13, .06], [.12, .18, .052]], head=[.14, .23], hr=[.062, .056, .052],
         bill=dict(len=.145, r=.019, droop=2, depth=1.0, comp=.6, blade=True, taper=1.0, tipK=.97, lowK=.8, minR=.0006, wTip=.9),   # (C final: a tapered chisel, not a blunt stick)
         tail=dict(len=.36, w=.06, n=7, ang=16, spread=.16, outline="flight"),
         fold=dict(S=[.11, .05, .08], T=[-.27, .015, .05], H=.1, w=.055, pad=PAD(out=.026, th=.028, col="@padC", tipCol="@padC",
                   patches=[dict(x=.24, y=.34, rx=.24, ry=.36, col="@patch", rot=-8)],
                   bars=dict(n=5, x0=-.12, x1=-.62, w=.0055, h=.9, tilt=8, seg=6, col="@wbar", gap=.003, paint=True))),   # (C final: painted -- crisp, not beaded)   # (C 2026-11-07: the white wing spots as rows on the pad)
         tars=.1, tib=.02, legr=.0085, toes=.075, zygo=True, thighR=[.05, .055, .04],
         spread=dict(span=1.75, armF=.38, asp=2.2, tipC=.55, hsweep=.12), wing=dict(armK=1.0, th=(20, 70), rounded=True, n=NOTRACT),
         flags={"print": "bird", "shy": 6, "peck": 1.3}, coats=coats,
         flight=dict(speed=1.3),
         marks=[("b", "belly", [.03, -.085, 0], [.15, .05, .06], "@wht", {"k": .03, "kc": .01}),
                ("h", "nape", [-.055, .015, 0], [.03, .032, .05], "@red", {"k": .005, "kc": .004, "op": "paint"}),   # (C 2026-11-07: paint, not a ball)
                ("h", "moustache", [.005, -.03, .05], [.06, .012, .04], "@mous", {"k": .004, "kc": .003, "mirror": True, "rot": -25, "op": "paint"}),
                ("b", "ventR", [-.15, -.07, 0], [.06, .045, .06], "@ventC", {"k": .01})])))

@sp
def cockatoo():
    c = pal("#f6f5f0", "#f4f3ee", head="#f8f7f2", wing="#f4f3ee", tail="#f2f0e8", bill="#3a3a40", billLo="#2c2c32", leg="#4a4a50", wpad="#eceae4",
            crest="#f2d23a", crestTip="#f4dc50", crestBase="#f6f2de", sec="#f2f0e0", secTip="#f4f2e6", prim="#f0eed8", primTip="#f2f0e2", cheekY="#f4ecb8", ring="#e6eef4", eye="#141010")
    hc, hr = [.2, .135], [.064, .058, .054]
    bird("cockatoo", "a sulphur-crested cockatoo: stocky and white all over, the long sulphur-yellow crest raised and curving forward, a faint yellow wash on the cheeks and under the wings and tail; the heavy black hooked bill, a pale bare ring round the dark eye; grey zygodactyl feet",
         .48, c, lid="@ring", **M_(MED, dict(tilt=40, trunk=[.2, .09, .082], breast=[.13, .115, .1], bc=[.07, -.005], rumpR=[.05, .045, .05], ventR=[.045, .04, .045],
         neck=[[.11, .065, .062], [.16, .095, .05]], head=hc, hr=hr,
         bill=dict(len=.075, r=.036, custom=True),
         tail=dict(len=.34, w=.06, n=7, ang=-2, spread=.16, lens=[.88, .96, 1.0, .96, .88]),
         fold=dict(S=[.11, .06, .085], T=[-.33, .0, .05], H=.12, w=.06, pad=dict(out=.025, th=.032)),
         tars=.042, tib=0, gap=.008, legr=.012, toes=.07, zygo=True, thighR=[.05, .05, .042], tibia="@leg",
         spread=dict(span=2.0, armF=.42, asp=2.4, tipC=.5, hsweep=.15), wing=dict(armK=1.1, th=(20, 72), rounded=True, n=NOTRACT),   # (C final: the pad alone -- no loose secondary discs)
         flags={"print": "bird", "shy": 5, "peck": .8},
         flight=dict(speed=1.0),
         marks=[("h", "cheekY", [.025, -.028, .042], [.03, .026, .016], "@cheekY", {"k": .006, "mirror": True}),
                ("h", "ringE", [.03, .009, .046], [.017, .016, .008], "@ring", {"k": .003, "kc": .001, "mirror": True})],
         extra=both(crest(hc, hr, [0, .15, .3, .45, .6, .75], [40, 50, 59, 67, 75, 83], [.085, .12, .15, .17, .17, .15], .011, "@crestBase", "@crest", curve=.42, outline="flight", roll=65),
                    parrot_bill(hc, hr, .056, "@bill", "@billLo")))))

@sp
def cockatiel():
    c = pal("#8c8c90", "#9a9a9e", head="#f0d23a", wing="#86868a", tail="#6e6e72", bill="#7e7a7c", billLo="#6e6a6c", leg="#8a8486",
            crown="#e8cc40", throat="#e8d050", neck="#9a9a9e", crest="#d8c860", crestTip="#8c8c90", cov="#f2f0ea", covTip="#e8e6e0", gcov="#f2f0ea", gcovTip="#dcdad4",
            sec="#7e7e82", secTip="#6e6e72", prim="#6a6a6e", primTip="#5a5a5e", tailTip="#5e5e62", orange="#e8742a", eye="#141010")
    hc, hr = [.17, .12], [.05, .046, .043]
    bird("cockatiel", "a cockatiel: slim and grey with the broad white patch on each wing, the yellow face and the long upright crest, a round orange patch on each cheek; the small grey hooked bill, the long pointed grey tail -- half its length",
         .32, c, **M_(SMALL, dict(tilt=34, trunk=[.16, .072, .066], breast=[.09, .07, .064], bc=[.06, -.01],
         neck=[[.09, .05, .045], [.13, .08, .038]], head=hc, hr=hr,
         bill=dict(len=.035, r=.017, custom=True),
         tail=dict(len=.5, w=.03, n=7, ang=-2, spread=.05, outline="flight", lens=[.55, .78, 1.0, .78, .55]),
         fold=dict(S=[.08, .04, .065], T=[-.26, .0, .042], H=.085, w=.045, pad=dict(out=.022, th=.028, col="@sec",
                   patches=[dict(x=.24, y=.4, rx=.24, ry=.36, col="@cov", rot=-6, paint=True)])),   # (C final: the white patch painted on the pad)
         tars=.05, tib=.025, legr=.008, toes=.06, zygo=True, thighR=[.045, .05, .035],
         spread=dict(span=1.3, armF=.36, asp=2.8, tipC=.2, hsweep=.5, pinch=.7), wing=dict(armK=1.0, th=(22, 74), pointed=True, n=NOTRACT),   # (C final: no loose white covert discs)
         flags={"print": "bird", "shy": 4, "peck": .9},
         flight=dict(speed=1.4),
         marks=[("h", "cheekO", [.02, -.02, .042], [.022, .02, .012], "@orange", {"k": .004, "mirror": True})],
         extra=both(crest(hc, hr, [0, .12, .24, .36], [10, 20, 30, 40], [.16, .18, .17, .14], .012, "@crest", "@crestTip", curve=.3, outline="flight", roll=58),
                    parrot_bill(hc, hr, .027, "@bill", "@billLo", wz=.85)))))

if __name__ == "__main__":
    for n in (sys.argv[1:] or SP): SP[n]()
