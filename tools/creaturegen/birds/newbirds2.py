# newbirds2.py [names...] -- six new birds (2026-11-07) from nb.py's body plan (units: the bird's length, bill tip to
#   tail tip): the Atlantic puffin, the grey crowned crane, the Eurasian spoonbill (and the roseate as its coat), the
#   southern cassowary and the turkey (the bronze tom, the white domestic, the hen; the tom's display). The great hornbill
#   is hornbill.py (a flier and a percher, from the macaw's plan).
import sys, math as _m, json
from newbirds import bird, pal, M_, MED, BIG, SMALL, crest, both
from bg import fea, row, add, nrm, ell, tube, cone, sph

SP = {}
def sp(f): SP[f.__name__] = f; return f


@sp
def puffin():
    c = pal("#141416", "#f4f4f2", head="#141416", wing="#141416", tail="#141416", bill="#e8502a", leg="#f07a28",
            crown="#141416", neck="#141416", throat="#141416", cheek="#e2e3e0", billLo="#e8502a", billG="#8e9aa8", billY="#f0c43a",
            ring="#d8382a", rosette="#f2c84a", blk="#141416", eye="#1a120c")
    bird("puffin", "an Atlantic puffin standing upright on the cliff top: stocky, black above and white below, the pale grey-white face under the black crown and the black collar; the big triangular bill, flat-sided and deep, banded blue-grey at its base, a yellow line, then red-orange to the tip, the yellow rosette at the gape and the red ring round the eye; bright orange legs and webbed feet set far back",
         .28, c, eye=.013, sink=.7, socket=1.1, lid="@ring", **M_(SMALL, dict(mesh=[8200, 1900], focus={"head": 2}, tilt=42, trunk=[.2, .125, .118], breast=[.14, .122, .115], bc=[.08, -.01],
         neck=[[.1, .1, .09], [.13, .15, .084]], head=[.152, .222], hr=[.094, .088, .082],
         bill=dict(len=.125, r=.066, droop=6, curve=14, depth=1.25, comp=.3, blade=True, taper=.9, tipK=.95, lowK=.8, baseX=.84, baseY=.2, zones=[[0, .3, "@billG"], [.3, .37, "@billY"]]),
         tail=dict(len=.09, w=.04, n=5, ang=-10, spread=.3),
         # (the folded wing one smooth black shape on the flank, its point over the tail: no loose tracts)
         fold=dict(S=[.1, .06, .1], T=[-.22, -.02, .07], H=.1, w=.05, pad=dict(out=.03, th=.032, col="@blk", tipCol="@blk", rim=0, k=.02, kc=.012)),
         tars=.055, legr=.016, toes=.07, legx=-.04, legz=.055, web="#f07a28", gap=.006, rumpR=[.08, .07, .08],
         spread=dict(span=2.0, armF=.38, asp=2.8, tipC=.55, hsweep=.1), wing=dict(armK=.9, th=(20, 70), pointed=True, n={"cov": 0, "pcov": 0, "gcov": 0, "sec": 0, "tert": 0, "prim": 0}),
         walk=dict(deg=18, speed=1.4, flex=14),
         flight=dict(speed=2.2, beat=60),
         flags={"print": "bird", "shy": 5, "peck": .5, "shore": True},
         marks=[("h", "face", [.022, -.014, .038], [.074, .058, .05], "@cheek", {"k": .006, "kc": .006, "mirror": True}),
                ("m", "collar", [.17, .14, 0], [.06, .042, .108], "@blk", {"k": .008, "kc": .009, "bone": "neck", "rot": -30}),
                # (the black of the crown runs down the hind neck onto the back: the breast's white is round and would wrap it)
                ("m", "nape", [.05, .155, 0], [.11, .075, .118], "@blk", {"k": .012, "kc": .01, "rot": 42}),
                ("m", "nape2", [.11, .19, 0], [.06, .06, .09], "@blk", {"k": .01, "kc": .01, "bone": "neck", "rot": 30}),
                ("h", "chin", [.03, -.07, 0], [.045, .03, .05], "@blk", {"k": .006, "kc": .008}),
                ("b", "mantle", [-.02, .075, 0], [.21, .095, .128], "@back", {"k": .02, "kc": .012}),
                ("h", "rosette", [.082, -.02, .04], [.011, .009, .008], "@rosette", {"k": .002, "mirror": True})])))


@sp
def crowned_crane():
    c = pal("#767c84", "#7a8088", head="#18181a", wing="#f2f0ea", tail="#3a3c42", bill="#2a2a2c", leg="#1e1e20",
            neck="#a8acb0", throat="#18181a", cheek="#f4f2ee", crown="#141416", cov="#f2f0ea", covTip="#e8dcc0", gcov="#e0c890", gcovTip="#c8a050",
            sec="#7a3a1e", secTip="#5e2a16", tert="#8a7a5a", tertTip="#c8a860", prim="#1c1c1e", primTip="#141416", wpad="#efece4",
            wht="#f4f2ee", red="#c8242a", gold="#e2bc5a", velvet="#101012", eye="#c8d4e0", lance="#8c929a", tertP="#c8a050", tertP2="#b0843e", wingG="#80868e")
    def crown(B, M, R, u):   # (the golden crown: a ball of stiff straw bristles behind the black velvet forehead -- the coat's quills)
        hc, hr = [.272, .405], [.045, .038, .034]
        out = [ell("crownB", M([hc[0] - hr[0] * .15, hc[1] + hr[1] * .95, 0]), R([.026, .02, .024]), "@gold", k=.01 * u, kc=.004 * u, bone="head", coat=True)]
        # (C r7: the long grey lanceolate feathers of the lower foreneck, hanging over the breast -- fine tubes, as drawn)
        for j_, (z, x0, y0, ln, a0) in enumerate([(0, .226, .13, .13, -80), (.012, .222, .125, .12, -84), (-.012, .222, .125, .12, -84), (.021, .214, .115, .105, -88),
                                                  (-.021, .214, .115, .105, -88), (.006, .229, .14, .14, -76), (-.006, .229, .14, .14, -76)]):
            pts = []
            for f in (0, .35, .7, 1):
                a_ = _m.radians(a0 - 10 * f); pts.append(M([x0 + _m.cos(a_) * ln * f + .03 * f, y0 + _m.sin(a_) * ln * f, z * (1 + .6 * f), .0047 * (1 - .7 * f) + .0007]))
            out.append(tube("lance%d" % j_, pts, "@lance", k=.004 * u, kc=.0015 * u, bone="neck"))
        # (the drooping tertials: a soft grey-brown cloak off the lower back, arching over the tail and hanging past it --
        #  layered flat ellipsoids blended into the back, a few fine plume ends trailing from it)
        # (C r9: the golden-straw tertial plumes -- long smooth blades laid one over the next along the back, each
        #  drooping a little more than the one before, over the tail and past it)
        for j_, (x, y, rx, ry, rz, rot, zz) in enumerate([(-.13, .08, .12, .015, .036, -10, .04), (-.21, .058, .12, .014, .034, -20, .043), (-.28, .028, .1, .013, .03, -32, .04)]):
            out.append(ell("tertM%d" % j_, M([x, y, zz]), R([rx, ry, rz]), "@tertP" if j_ != 1 else "@tertP2", k=.03 * u, kc=.008 * u, rot=[0, 0, rot], mirror=True))
        for j_, (z, x0, ln) in enumerate([(.03, -.3, .1), (-.03, -.3, .1), (.055, -.29, .09), (-.055, -.29, .09)]):
            pts = [M([x0 - ln * f * .7, .02 - ln * f * .75, z, .0044 * (1 - .6 * f) + .0006]) for f in (-.3, 0, .5, 1)]   # (C 2026-11-07: rooted inside the cloak -- they floated 0.6 cm off it)
            out.append(tube("tert%d" % j_, pts, "@tertP2", k=.004 * u, kc=.0015 * u))
        return out
    bird("crowned crane", "a grey crowned crane: slender and pale grey, the long pale-grey neck; the black velvet forehead and over it the crown of stiff golden bristles; the bare white cheek patch topped red, the red wattle under the chin; the wing's great white panel, the golden-straw plumes over it and the chestnut secondaries, black primaries; long black legs",
         1.0, c, **M_(BIG, dict(mesh=[7800, 2400], cell=.0055, focus={"head": 6}, tilt=-2, trunk=[.25, .084, .08], breast=[.1, .084, .078], bc=[.13, .005],
         neck=[[.15, .045, .042], [.218, .125, .027], [.205, .21, .02], [.19, .285, .017], [.212, .355, .016], [.25, .39, .016]], head=[.272, .405], hr=[.045, .038, .034],   # (C r9: a gentle S)
         bill=dict(len=.072, r=.016, droop=10),
         tail=dict(len=.11, w=.05, n=5, ang=4, spread=.22, roof=20),
         # (the folded wing one smooth shape on the flank: the great white panel of the coverts, the golden-straw plumes
         #  along its upper rear, the chestnut secondaries at its lower rear and the black primaries' point over the tail)
         fold=dict(S=[.12, .04, .082], T=[-.3, -.005, .055], H=.088, w=.045,
                   pad=dict(out=.02, th=.03, col="@wingG", tipCol="@prim", rim=0, len=.56, h=.6, k=.03, kc=.008,   # (C r9: a grey wing, the white covert PANEL lying on it)
                            patches=[dict(x=.3, y=.45, rx=.46, ry=.5, col="@wht", rot=-6), dict(x=.6, y=.28, rx=.3, ry=.24, col="@gold", rot=-4), dict(x=.62, y=.68, rx=.2, ry=.24, col="@sec", rot=-6)])),
         tars=.24, tib=.2, legr=.0095, toes=.085, tibia="@leg", tuck="trail",
         spread=dict(span=2.0, armF=.5, asp=2.8, tipC=.62, hsweep=.08, fingered=True, kink=.08), wing=dict(armK=1.5, th=(15, 80), hand=.42, rounded=True, tert=.55, n={"cov": 0, "pcov": 0, "gcov": 0, "sec": 0, "tert": 0, "prim": 0}),
         walk=dict(deg=20, speed=.55, flex=26),
         flags={"print": "bird", "shy": 8, "peck": .45, "shore": True},
         flight=dict(speed=.6, flyTurn={"neck": -70, "head": 70}),
         coat={"gap": .0042, "len": .055, "r": .0011, "sides": 3, "lean": .25, "vary": .35, "skirt": -1, "drop": 0, "face": .9, "rise": 0,
               "tip": "#f0d070", "base": "#b08a3a", "dark": .2, "darkTip": "#c89a40", "hold": .5},
         marks=[("h", "velvet", [.03, .022, 0], [.03, .02, .028], "@velvet", {"k": .004}),
                ("h", "cheekW", [-.002, -.007, .026], [.034, .028, .014], "@wht", {"k": .004, "mirror": True}),
                ("h", "cheekR", [.002, .019, .028], [.024, .009, .01], "@red", {"k": .002, "mirror": True}),
                ("h", "wattle", [.02, -.045, 0], [.014, .022, .01], "@red", {"k": .003})],
         extra=crown)))


def spoon_bill(hc, hr, L, droop, col, tip):
    """a spoonbill's bill: long, flat (wider than deep) and straight, narrowing to the middle and spreading into the round
       spatula at the tip, its end yellow -- a chain of flattened ellipsoids"""
    def ex(B, M, R, u):
        b0 = [hc[0] + hr[0] * .85, hc[1] - hr[1] * .08]; a = _m.radians(-droop); n = 34; out = []   # (C r9: finer links, a smooth outline)
        for i in range(n):
            f = i / (n - 1); p = [b0[0] + _m.cos(a) * L * f, b0[1] + _m.sin(a) * L * f]
            # (narrowing to the middle, widening into the spatula, and its end ROUNDED -- the last links shrinking on a circle)
            w = (.013 * (1 - .4 * f / .5) if f < .5 else .0078 + .0262 * _m.sin((f - .5) / .33 * _m.pi / 2) ** .8 if f < .83
                 else .034 * _m.sqrt(max(.12, 1 - ((f - .83) / .18) ** 2)))
            # (C r7: the spatula as thick as the grid holds -- at .004 it fell under the cell and went to a stick)
            t = max(.011 * (1 - .5 * f), .0072) * (1 if f < .55 else .92)
            if f >= .55: p[1] += .002 * _m.sin((f - .55) / .45 * _m.pi)   # (the spoon a little dished, its middle raised)
            out.append(ell("bill%d" % i, M([p[0], p[1], 0]), R([L / (n - 1) * 1.6, t, w]), col, k=.007 * u, kc=.001 * u, bone="head", rot=[0, 0, -droop]))
        # (the yellow only on the spoon's end: painted on, a soft edge across it -- not a card of its own)
        pT = [b0[0] + _m.cos(a) * L * 1.0, b0[1] + _m.sin(a) * L * 1.0]
        out.append(ell("billTipP", M(pT + [0]), R([L * .14, .02, .05]), tip, k=.004 * u, kc=.006 * u, bone="head", rot=[0, 0, -droop], op="paint"))
        # (the shaft's ridges: two fine dark grooves either side of the culmen, back from the spoon)
        for zs in (1, -1):
            pts = []
            for f in (.04, .3, .52):
                p = [b0[0] + _m.cos(a) * L * f, b0[1] + _m.sin(a) * L * f]
                pts.append(M([p[0], p[1] + .0085 * (1 - .5 * f), zs * .006 * (1 - .4 * f), .0016]))
            out.append(tube("billRidge" + ("L" if zs > 0 else "R"), pts, "@ridge", k=.002 * u, kc=.0008 * u, bone="head"))
        return out
    return ex


@sp
def spoonbill():
    c = pal("#f4f4f0", "#f6f6f2", head="#f4f4f0", wing="#f2f2ee", tail="#f2f2ee", bill="#1a1a1a", leg="#1a1a1a",
            billTip="#e8c84a", ridge="#3a3a36", buff="#e8cf8e", crestC="#f6f4ea", crestTip="#efe0b0", throat="#f4f0e2", wpad="#eeeee8", eye="#c83a2a")
    hc, hr = [.26, .33], [.044, .037, .034]
    def gated(B, M, R, u):   # (the breeding bird's nuchal crest: a shaggy tuft of fine plumes hanging back off the nape -- the coat's quills)
        # (C r7: the nuchal crest a drooping shaggy mane -- long soft plumes hanging back and down off the nape, curving
        #  as they fall, the middle ones longest; fine tubes, drawn as they are)
        out = []
        for j, (zz, yy, ln, dr, rr) in enumerate([(0, .3, .15, 26, .0068), (.007, .26, .145, 32, .0064), (-.007, .26, .145, 32, .0064), (.012, .18, .13, 40, .006),
                                                  (-.012, .18, .13, 40, .006), (.004, .4, .12, 18, .006), (-.004, .4, .12, 18, .006), (.015, .08, .11, 50, .0052), (-.015, .08, .11, 50, .0052),
                                                  (.002, .34, .16, 24, .0056), (-.009, .22, .14, 36, .0056)] + [(zz_ + .005, yy_ - .03, ln_ * .82, dr_ + 7, .006) for zz_, yy_, ln_, dr_ in
                                                  ((0, .3, .15, 26), (.012, .2, .13, 38), (-.012, .2, .13, 38), (.006, .38, .12, 18), (-.006, .36, .13, 22), (.015, .1, .11, 48), (-.015, .1, .11, 48))]):   # (C r9: thinner and more of them -- a mane, not fingers)
            r0 = [hc[0] - hr[0] * .55, hc[1] + hr[1] * (yy * 1.4 - .05), zz * 1.6]; pts = []
            for f in (0, .35, .7, 1):
                a_ = _m.radians(180 + dr * .7 + 16 * f * f)
                pts.append(M([r0[0] + _m.cos(a_) * ln * f, r0[1] + _m.sin(a_) * ln * f, r0[2] + zz * 1.6 * f, rr * .32 * (1 - .6 * f) + .0004]))
            out.append({"when": "crest", **tube("crestP%d" % j, pts, "@crestC" if j % 2 else "@crestTip", k=.006 * u, kc=.002 * u, bone="head")})
        return out + spoon_bill(hc, hr, .26, 6, "@bill", "@billTip")(B, M, R, u)
    coats = [{"name": "Eurasian spoonbill"},
             {"name": "roseate spoonbill", "params": {"crest": False}, "back": "#f2a6be", "under": "#f4aec4", "rump": "#e88aaa", "vent": "#f4aec4",
              "cov": "#d23a6e", "covTip": "#d23a6e", "gcov": "#e47ea2", "gcovTip": "#e890b0", "sec": "#ee9cb6", "secTip": "#e890b0", "prim": "#f0a8be", "primTip": "#e890b0",
              "wpad": "#dc5a86", "tail": "#e8904a", "tailTip": "#e0843e", "head": "#b4c09a", "crown": "#a8b48e", "cheek": "#b4c09a", "neck": "#f4e4ea", "throat": "#f4e4ea",
              "bill": "#a8ac94", "billTip": "#a8ac94", "leg": "#c84a68", "thigh": "#f2a6be", "buff": "#f4aec4", "eye": "#c8302a"}]
    bird("spoonbill", "a Eurasian spoonbill wading: all white, the long flat black bill spreading at its end into the round spatula, tipped yellow; the shaggy nuchal crest of the breeding bird and the buff wash on the breast; long black legs. Coat: the roseate spoonbill -- pink, the carmine shoulder, the orange tail, the bare greenish head, no crest",
         .85, c, eye=.016, sink=.6, socket=1.1, **M_(BIG, dict(mesh=[6500, 1500], focus={"head": 3}, tilt=4, trunk=[.19, .1, .095], breast=[.11, .1, .09], bc=[.09, 0],
         neck=[[.14, .05, .05], [.2, .13, .036], [.222, .22, .03], [.238, .29, .028]], head=hc, hr=hr,
         bill=dict(len=.26, r=.012, custom=True),
         tail=dict(len=.12, w=.055, n=6, ang=6, spread=.25, roof=18),
         cell=.003,
         # (the folded wing one smooth white shape on the flank: no loose tracts; the roseate's a deep carmine-pink)
         fold=dict(S=[.1, .04, .09], T=[-.25, -.01, .055], H=.1, w=.045,
                   pad=dict(out=.022, th=.03, col="@wpad", tip=False, rim=0, len=.64, h=.6, k=.03, kc=.008)),
         tars=.2, tib=.16, legr=.0095, toes=.085, tibia="@leg", tuck="trail",
         spread=dict(span=1.6, armF=.48, asp=2.8, tipC=.6, hsweep=.08, fingered=True, kink=.06), wing=dict(armK=1.3, th=(15, 75), hand=.4, rounded=True, n={"cov": 0, "pcov": 0, "gcov": 0, "sec": 0, "tert": 0, "prim": 0}),
         walk=dict(deg=20, speed=.6, flex=24),
         flags={"print": "bird", "shy": 7, "peck": 0, "shore": True},
         # (feeding: standing in the shallows the head goes down, bill in the water (`graze`), and swings side to side on
         #  the head's own yaw -- with the bill pointing down that is the spoonbill's sweep, the spatula scything through
         #  the water; walking or aloft the same swing is only its looking about)
         graze=.95, headAnim={"axis": "y", "deg": 30, "speed": .75, "phase": 0},
         flight=dict(speed=.8, flyTurn={"neck": -62, "head": 60}),
         coats=coats, params={"crest": True},
         # (the neck's base feathered out over the breast -- a fuller, looser ruff -- and the buff band across it)
         marks=[("b", "breastBuff", [.17, .025, 0], [.05, .045, .085], "@buff", {"k": .02, "kc": .012}),
                ("m", "neckRuff", [.165, .075, 0], [.05, .05, .055], "@under", {"k": .022, "kc": .01, "bone": "neck", "rot": -40}),
                ("m", "neckBand", [.172, .08, 0], [.03, .03, .058], "@buff", {"k": .012, "kc": .01, "bone": "neck", "rot": -40})],
         extra=gated)))


@sp
def cassowary():
    c = pal("#121212", "#151515", head="#2d62c0", wing="#121212", tail="#121212", bill="#1c1c1c", leg="#68705e",
            neck="#3a7ccc", throat="#3a7ccc", cheek="#2d62c0", crown="#2d62c0", thigh="#141414", talon="#2a2826",
            casque="#6e4e32", casqueHi="#8a6a46", red="#cc1f28", purple="#7a2a6a", eye="#7a4a1a")
    def head_bits(B, M, R, u):
        hc, hr = [.263, .49], [.045, .04, .035]
        # (the CASQUE: a tall blade of horn on the crown, flat side to side, higher than the head is deep -- broad at its
        #  foot over the forehead, leaning back as it rises, its top a rounded ridge; built of three stacked flats)
        cq = [ell("casque%d" % i, M([hc[0] + .012 - .012 * i, hc[1] + hr[1] * .85 + .016 + .04 * i, 0]), R([.056 - .009 * i, .03 + .004 * i - .008 * (i == 2), .0135 - .0022 * i]),
                  "@casque" if i < 2 else "@casqueHi", k=.03 * u, kc=.012 * u, bone="head", rot=[0, 0, -20]) for i in range(3)]
        # (the WATTLES: two fleshy red lobes hanging side by side from the front of the neck, swelling to their rounded ends)
        wt = [tube("wattle", [M([.26, .335, .014, .005]), M([.269, .305, .018, .01]), M([.276, .274, .022, .0145]), M([.278, .25, .023, .0135]), M([.276, .234, .022, .006])],
                   "@red", k=.004 * u, kc=.0015 * u, bone="neck2", mirror=True)]
        return cq + wt
    def nohwing(B, M, R, u, sh):   # (no wing to speak of: the tracts gone, the quills of the wing's stubs hidden in the coat)
        sh[:] = [q for q in sh if not (q.get("type") == "feathers" and q.get("id") in ("prim", "sec", "tert", "cov", "gcov", "pcov"))]
        return []
    hairy = {"coat": True}
    bird("cassowary", "a southern cassowary in the rainforest: the great black body under coarse, hair-like glossy plumage hanging loose; the bare blue head and neck, purple-red at the nape, the two red wattles hanging from the front of the neck; the tall brown casque on the crown; thick grey legs, three toes, the inner one armed with its long dagger of a claw; it cannot fly",
         1.5, c, eye=.04, sink=.55, socket=1.1, lid="#1e3a7a", **M_(BIG, dict(mesh=[8000, 2600], focus={"head": 6, "tarsL": 4, "tarsR": 4}, tilt=12, trunk=[.34, .165, .15], breast=[.15, .15, .13], bc=[.13, -.03],   # (C r9: level and long -- deeper at the shoulders than the rump)
         neck=[[.15, .1, .062], [.2, .21, .045], [.236, .35, .033], [.256, .462, .028]], head=[.263, .49], hr=[.045, .04, .035],
         bill=dict(len=.088, r=.022, droop=12, depth=.95),
         tail=dict(len=.06, w=.03, n=3, ang=-30, spread=.3),
         fold=dict(S=[.12, .07, .13], T=[-.15, -.02, .1], H=.12, w=.06, pad=None, lay=False),
         tars=.22, tib=.13, legr=.046, legz=.1, tibK=1.3, ankK=1.18, heel=.055, footFwd=.02, tibBare=.45, toes=.19, toeR=.52, toeDz=(.68, -.4), toeIK=.72, toePads=True, noHallux=True, thighR=[.13, .15, .1], tibia="@thigh", talons=.065, clawK=.55, dagger=.085, daggerK=.9, daggerUp=-.03,   # (C final 2: the drumstick bare below the hair, the heel jutting back, the tarsus slanting forward; three spread padded toes, sharp claws, the inner one's dagger)
         rumpR=[.11, .095, .115], ventR=[.08, .08, .09],
         flightless=True, wing=dict(armK=.6, th=(20, 70), rounded=True, hand=.3),
         walk=dict(deg=24, speed=.75, flex=24),
         flags={"print": "bird", "shy": 3, "peck": .4},
         coat={"gap": .028, "len": .15, "r": .0045, "sides": 3, "lean": .96, "vary": .3, "skirt": -.75, "drop": .55, "face": .6, "rise": .3,
               "tip": "#1e1e22", "base": "#0e0e0e", "dark": .5, "darkTip": "#2a2c34", "hold": .5},
         pats={k_: hairy for k_ in ("trunk", "back", "rump", "breast", "ruff", "thigh", "tibia")},
         marks=[("m", "nape", [.21, .38, 0], [.024, .06, .03], "@purple", {"k": .01, "bone": "neck2", "rot": -18}),
                ("m", "napeR", [.19, .29, 0], [.03, .055, .038], "@red", {"k": .01, "bone": "neck2", "rot": -22}),
                ("m", "ruff", [.17, .17, 0], [.075, .085, .09], "@back", {"k": .03, "kc": .008, "bone": "neck"}),
                # (C r7: the hump at the shoulders -- the body's highest point, the back sloping away to the drooping rump)
                ("b", "hump", [.08, .08, 0], [.18, .09, .135], "@back", {"k": .05}),
                ("b", "rumpD", [-.22, -.07, 0], [.15, .12, .125], "@back", {"k": .05})],   # (C r9: the rump drooping low behind)
         extra=head_bits, post=nohwing)))


def turkey_parts(B, M, R, u, sh):
    """the tom's own: the SNOOD hanging over the bill, the BEARD of black bristles from the breast, the caruncles of the
       neck; the tail gated `rest`, and in DISPLAY (variants.display) the fan raised upright behind him"""
    hc, hr = [.24, .315], [.034, .03, .027]
    for q in sh:
        if q.get("id") == "tail": q["when"] = "rest"
    # (the snood: a slim fleshy finger from the forehead at the bill's base, over the base and down beside the bill)
    out = [{"when": "tom", **tube("snood", [M([hc[0] + hr[0] * .72, hc[1] + hr[1] * .45, 0, .0052]), M([hc[0] + hr[0] * 1.02, hc[1] + hr[1] * .42, .002, .005]),
                                             M([hc[0] + hr[0] * 1.3, hc[1] + hr[1] * .05, .007, .0047]), M([hc[0] + hr[0] * 1.38, hc[1] - hr[1] * .7, .009, .0042]),
                                             M([hc[0] + hr[0] * 1.32, hc[1] - hr[1] * 1.5, .009, .0036])], "@red", k=.003 * u, kc=.001 * u, bone="head")}]
    out += [{"when": "tom", **ell("car%d%d" % (i, j), M([.2 + .012 * i - .01 * j, .245 - .03 * i + .02 * j, .022 - .002 * i]), R([.008, .008, .008]), "@red", k=.003 * u, kc=.001 * u, bone="neck2", mirror=True)}
            for i in range(3) for j in range(2)]
    # (the tom's spur: a short blunt horn at the back of each shank, a third of the way up)
    ts_ = next(q for q in sh if q.get("id") == "tarsus"); sp0 = [ts_["b"][k] + (ts_["a"][k] - ts_["b"][k]) * .33 for k in range(3)]
    sp0 = [round(sp0[0] - ts_["ra"] * .7, 4), round(sp0[1], 4), sp0[2]]
    out += [{"when": "tom", **cone("spur", sp0, [round(sp0[0] - .022 * u, 4), round(sp0[1] - .004 * u, 4), sp0[2]], .0055 * u, .0016 * u, "@spur", k=.002 * u, kc=.0008 * u, bone="tarsL", mirror=True)}]
    from bg import field
    body = [q for q in sh if q.get("type") != "feathers"]
    b0 = B([.13, .1, 0]); fw = nrm([1, -.1, 0])   # (the beard's root: on the breast's surface, marched out from inside)
    while field(body, b0) < -.004 * u: b0 = add(b0, fw, .002 * u)
    b0 = [round(v, 4) for v in b0]
    # (C r7: the beard a slim hanging TASSEL of hair-like bristles -- a tight bundle from one root on the upper breast,
    #  each bristle a fine tube hanging nearly straight down, splaying a little toward its ends; each point walked forward
    #  just clear of the breast's feathers so it hangs against them, not into them)
    for j_, (dz, dx, ln) in enumerate([(0, 0, .17), (.004, .003, .16), (-.004, .003, .16), (.007, -.002, .15), (-.007, -.002, .15), (.002, .006, .155), (-.002, .006, .155), (0, -.004, .145)]):
        dv = nrm([.18 + dx * 6, -1, dz * 4]); bp_ = []
        for f in (0, .35, .7, 1):
            r_ = (.0032 - .0018 * f) * u
            q_ = [b0[0] + (dv[0] * f * ln + dx * .3) * u, b0[1] + dv[1] * f * ln * u, (dz * .5 + dv[2] * f * ln) * u]
            while f > 0 and field(body, q_) < r_ * .2: q_[0] += .0015 * u
            bp_.append([round(q_[0] - (.009 - .022 * f * f) * u, 4),   # (C r9: the root set into the breast, the lower tassel hanging free of it)
                         round(q_[1], 4), round(q_[2], 4), round(r_, 4)])   # (set back onto the meshed surface, which sits inside the raw field)
        out.append({"when": "tom", **tube("beard%d" % j_, bp_, "@beard", k=.0015 * u, kc=.0006 * u)})
    # (the display fan: ~16 feathers radiating in the plane square to the body from the rump, upright; each with its band and tip)
    rr = B([-.24, .06, 0]); fan = []
    for i in range(7):
        a = _m.radians(-82 + 164 * i / 6); dvf = [-.18, _m.cos(a), _m.sin(a)]; dvf = nrm(dvf); Lf = .42 * (1 - .12 * abs(i - 3) / 3)
        fan.append(row([rr[0], rr[1], round(_m.sin(a) * .02 * u, 4)], [round(rr[0] + dvf[0] * Lf * u, 4), round(rr[1] + dvf[1] * Lf * u, 4), round(dvf[2] * Lf * u, 4)], round(.06 * u, 4),
                       up=[1, 0, 0]))
    out.append({"when": "display", **fea("fan", fan, 17, "@tail", "@tailTip", outline="round", camber=.08, curve=-.03, seed=63, bars={"n": 9, "dark": .55}, bone="tail")})
    out.append({"when": "display", **fea("fanCov", [dict(r_, to=[round(r_["at"][k] + (r_["to"][k] - r_["at"][k]) * .55, 4) for k in range(3)], w=round(.05 * u, 4)) for r_ in fan], 15,
                                         "@cov", "@covTip", outline="round", camber=.08, curve=-.02, lift=round(.012 * u, 4), seed=64, bone="tail", layer=True)})
    return out


@sp
def turkey():
    c = pal("#5a4024", "#3e2e1e", head="#9cb8de", wing="#4e3c2a", tail="#4a3624", bill="#d8ccb4", leg="#a8908a",
            neck="#c8403a", throat="#c8403a", cheek="#9cb8de", crown="#b8cce8", cov="#5a4630", covTip="#2e2418", gcov="#5a4630", gcovTip="#2a2016",
            sec="#e2dccc", secTip="#5a4a38", prim="#e2dccc", primTip="#3a3026", tert="#5a4630", tertTip="#2e2418", tailTip="#8a5a36",
            red="#cc2a26", beard="#16120e", eye="#3a2414", spur="#7a6a62", wat="#d8484a", primD="#3a2c20", secBar="#3e3024")
    c.update(head="#6e90cc", crown="#8aa8d8", cheek="#6e90cc")
    coats = [{"name": "bronze turkey"},
             {"name": "white turkey", "back": "#eeebe4", "under": "#f2efe8", "rump": "#eeebe4", "vent": "#f2efe8", "cov": "#f0ede6", "covTip": "#e2ddd2", "gcov": "#f0ede6", "gcovTip": "#e2ddd2",
              "sec": "#f2efe8", "secTip": "#e6e1d6", "prim": "#f2efe8", "primTip": "#e6e1d6", "tert": "#f0ede6", "tertTip": "#e2ddd2", "tail": "#f2efe8", "tailTip": "#e8e3d8",
              "wing": "#f0ede6", "wpad": "#e6e2d8", "thigh": "#f2efe8", "leg": "#d8a8a0"}]
    variants = {"display": {"params": {"display": True, "rest": False}},
                "hen": {"scale": .78, "params": {"tom": False},
                        "colors": {"back": "#5a4836", "under": "#5e4c38", "rump": "#5a4836", "vent": "#5e4c38", "cov": "#6a563e", "covTip": "#3a2e22", "gcov": "#6a563e", "gcovTip": "#3a2e22",
                                   "tert": "#6a563e", "tertTip": "#3a2e22", "tail": "#5a4632", "tailTip": "#a07a52", "head": "#8a9ab0", "crown": "#6a6a66", "cheek": "#8a9ab0",
                                   "neck": "#9a6a62", "throat": "#a05a52", "wpad": "#5e4c38"}}}
    bird("turkey", "a wild turkey tom: the big body in dark bronze plumage, every feather edged black and glossed copper and green; the bare head blue and red, the red snood hanging over the bill and the red wattle under the chin, the caruncles down the neck; the beard of black bristles from the breast; the barred white-and-dark flight feathers, the rounded tail tipped chestnut; long pinkish legs. Variants: display (the tail raised upright in its fan), hen (smaller, duller, no snood or beard); coat: the white domestic",
         1.1, c, eye=.022, sink=.55, socket=1.1, **M_(BIG, dict(mesh=[3000, 1050], focus={"head": 3}, tilt=18, trunk=[.27, .14, .13], breast=[.155, .16, .125], bc=[.13, -.04],
         neck=[[.15, .1, .05], [.2, .19, .032], [.215, .265, .026]], head=[.24, .315], hr=[.034, .03, .027],
         bill=dict(len=.048, r=.013, droop=18),
         tail=dict(len=.27, w=.07, n=9, ang=2, spread=.13, roof=30, bars={"n": 8, "dark": .6}),
         # (the folded wing as one smooth shape on the flank -- the bronze coverts, the white secondaries along its lower
         #  edge crossed by dark bars -- and the barred primaries laid back from it over the tail: no loose tracts)
         fold=dict(S=[.1, .05, .135], T=[-.22, -.0, .1], H=.12, w=.055, pad=dict(out=.026, th=.034, col="@cov", tip=False, rim=0, len=.6,
                   patches=[dict(x=.62, y=.55, rx=.36, ry=.42, col="@sec", rot=-8)],
                   bars=dict(n=7, x0=-.1, x1=-.88, w=.0075, h=1.0, tilt=18, seg=4, col="@secBar"))),
         tars=.17, tib=.04, legr=.03, toes=.1, toeR=.62, thighR=[.08, .09, .06], rumpR=[.1, .085, .1],
         spread=dict(span=1.35, armF=.38, asp=2.0, tipC=.6, hsweep=.12), wing=dict(armK=.85, th=(12, 58), rounded=True, tert=.5, hand=.3, pbars={"n": 6, "dark": .2}, sbars={"n": 5, "dark": .25},
                   n={"cov": 0, "pcov": 0, "gcov": 0, "sec": 0, "tert": 0, "prim": 0}),
         walk=dict(deg=22, speed=.8, flex=22),
         flags={"print": "bird", "shy": 4, "peck": 1.0},
         coats=coats, variants=variants, params={"tom": True, "display": False, "rest": True},
         # (the bronze plumage in rows of big rounded feathers, each one's end rimmed dark: coatpat.js rowscales, its rows
         #  along the body from the tail to the breast, some 3 cm apart)
         pats={k_: {"pat": "rowscales", "frame": {"o": [0, .45, 0], "u": [.96, .28, 0], "v": [-.28, .96, 0], "r": .6}} for k_ in ("trunk", "back", "breast", "rump", "belly")},
         marks=[("h", "wattle", [.016, -.042, 0], [.014, .03, .015], "@wat", {"k": .007, "kc": .003}),
                ("h", "throatR", [.004, -.022, 0], [.028, .018, .022], "@red", {"k": .005, "kc": .003}),
                ("m", "ruffN", [.165, .13, 0], [.06, .055, .07], "@back", {"k": .02, "kc": .006, "bone": "neck"})],
         post=turkey_parts)))


if __name__ == "__main__":
    for n in (sys.argv[1:] or SP): SP[n]()
