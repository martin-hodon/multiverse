#!/usr/bin/env python3
"""BUTTERFLIES (2026-10-05, docs/butterflies.md): the wing shapes and the species as definitions -- assets/butterflies/
shapes.json and one file per species -- and the catalogue's "Butterflies" category. Each species: its shape, its real
wingspan, its body's colour, and two paintings (upper, under), each wing's a ground and a list of layers in WING
COORDINATES (t from the base to the margin, a from the costa to the inner margin; the nymphalid ground plan's bands).
Edit the numbers here or in the asset viewer; run again to rewrite the files.

    python3 tools/butterflygen.py
"""
import json, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "assets", "butterflies")

# ---- THE SHAPES: polar profiles (degrees from the body's forward, radius x the forewing's length)
SHAPES = {
 "nymphalid": {"_about": "the brush-foots' broad triangular forewing and rounded hindwing (admirals, monarchs, painted ladies)",
   "fore": {"from": 70, "to": 124, "veins": 9, "R": [[70, .96], [78, 1.0], [88, .95], [100, .86], [112, .78], [119, .72], [124, .62]]},
   "hind": {"from": 96, "to": 190, "veins": 8, "R": [[96, .5], [110, .66], [130, .76], [150, .76], [168, .68], [182, .53], [190, .42]]}, "hindRoot": [-.05, 0]},
 "nymphalid-scalloped": {"_about": "a nymphalid with the margins scalloped between the veins (peacock, tortoiseshell)",
   "fore": {"from": 70, "to": 124, "veins": 9, "scallop": {"amp": .04, "n": 9}, "R": [[70, .96], [78, 1.0], [86, .95], [96, .9], [106, .84], [116, .76], [124, .62]]},
   "hind": {"from": 96, "to": 190, "veins": 8, "scallop": {"amp": .06, "n": 8}, "R": [[96, .5], [110, .66], [130, .77], [150, .77], [168, .68], [182, .53], [190, .42]]}, "hindRoot": [-.05, 0]},
 "papilio": {"_about": "the swallowtails: a long forewing, the hindwing scalloped and drawn into a TAIL at vein M3",
   "fore": {"from": 68, "to": 122, "veins": 9, "R": [[68, 1.0], [76, 1.05], [88, .95], [102, .84], [114, .74], [122, .62]]},
   "hind": {"from": 96, "to": 192, "veins": 8, "scallop": {"amp": .07, "n": 7}, "tail": {"at": 150, "length": .3, "width": 5, "round": 4},
            "R": [[96, .48], [112, .62], [132, .7], [150, .7], [170, .62], [184, .5], [192, .38]]}, "hindRoot": [-.04, 0]},
 "pierid": {"_about": "the whites and yellows: a rounded apex, a round hindwing",
   "fore": {"from": 70, "to": 124, "veins": 9, "R": [[70, .92], [80, .98], [92, .95], [104, .88], [116, .78], [124, .64]]},
   "hind": {"from": 96, "to": 190, "veins": 8, "R": [[96, .5], [112, .65], [132, .72], [152, .7], [170, .62], [184, .5], [190, .4]]}, "hindRoot": [-.04, 0]},
 "gonepteryx": {"_about": "the brimstone: the forewing's apex hooked, the hindwing pointed at a vein",
   "fore": {"from": 70, "to": 124, "veins": 9, "R": [[70, .95], [78, 1.04], [84, .98], [96, .86], [110, .78], [124, .64]]},
   "hind": {"from": 96, "to": 190, "veins": 8, "tail": {"at": 148, "length": .06, "width": 9, "round": 1.5},
            "R": [[96, .52], [114, .68], [134, .77], [148, .78], [164, .7], [180, .57], [190, .42]]}, "hindRoot": [-.04, 0]},
 "lycaenid": {"_about": "the blues, coppers and hairstreaks: a small, rounded pair",
   "fore": {"from": 72, "to": 126, "veins": 8, "R": [[72, .92], [82, .97], [96, .92], [110, .84], [126, .66]]},
   "hind": {"from": 96, "to": 190, "veins": 7, "R": [[96, .5], [112, .64], [132, .7], [152, .68], [170, .6], [184, .48], [190, .38]]}, "hindRoot": [-.04, 0]},
 "morpho": {"_about": "the morphos and owls: very large, broad wings",
   "fore": {"from": 68, "to": 126, "veins": 9, "R": [[68, .95], [78, 1.0], [92, .96], [106, .9], [118, .82], [126, .7]]},
   "hind": {"from": 94, "to": 192, "veins": 8, "scallop": {"amp": .03, "n": 8}, "R": [[94, .58], [110, .76], [130, .84], [150, .84], [170, .76], [184, .6], [192, .45]]}, "hindRoot": [-.05, 0]},
 "heliconius": {"_about": "the longwings: a long narrow forewing, a small hindwing",
   "fore": {"from": 68, "to": 118, "veins": 9, "R": [[68, 1.0], [76, 1.03], [88, .9], [102, .74], [112, .62], [118, .5]]},
   "hind": {"from": 96, "to": 186, "veins": 8, "R": [[96, .46], [112, .58], [132, .62], [152, .58], [172, .5], [186, .38]]}, "hindRoot": [-.04, 0]},
}

# ---- layer helpers
def band(t, color, a=None, **k): d = {"type": "band", "t": t, "color": color};  d.update({"a": a} if a else {}); d.update(k); return d
def grad(t, color, to, **k): d = {"type": "gradient", "t": t, "color": color, "to": to}; d.update(k); return d
def veins(color, width=.014, **k): d = {"type": "veins", "color": color, "width": width}; d.update(k); return d
def spots(t, r, color, **k): d = {"type": "spots", "t": t, "r": r, "color": color}; d.update(k); return d
def eye(t, r, rings, pupil=None, glint=None, **k):
    d = {"type": "eye", "t": t, "r": r, "rings": rings}
    if pupil: d["pupil"] = pupil
    if glint: d["glint"] = glint
    d.update(k); return d
def dust(colors, **k): d = {"type": "dust", "colors": colors}; d.update(k); return d
def fringe(color, alt=None, **k): d = {"type": "fringe", "color": color}; d.update({"alt": alt} if alt else {}); d.update(k); return d
def side(ground, *layers, tail=None): d = {"ground": ground, "layers": list(layers)}; d.update({"tail": tail} if tail else {}); return d

SP = {}
def species(key, name, latin, shape, span, body, upper, under, about, **k):
    SP[key] = {"kind": "butterfly", "name": name, "latin": latin, "shape": shape, "span": span, "body": body, "_about": about, **k, "upper": upper, "under": under}

BLACK, WHITE = "#1c1816", "#f4f1e8"
species("monarch", "Monarch", "Danaus plexippus", "nymphalid", .095, "#1e1814",
  {"fore": side("#e8801e", grad([0, .4], "#c45e12", "#e8801e"), veins(BLACK, .022), band([.6, 1.3], BLACK, a=[0, .32]), band([.88, 1.3], BLACK),
                spots(.78, .022, "#f4c36a", cells=[1, 2, 3]), spots(.71, .016, WHITE, cells=[0, 1]), spots(.93, .011, WHITE), spots(.975, .008, WHITE)),
   "hind": side("#e07a1a", grad([0, .4], "#c45e12", "#e07a1a"), veins(BLACK, .02), band([.86, 1.3], BLACK), spots(.91, .011, WHITE), spots(.965, .009, WHITE))},
  {"fore": side("#e48a2a", band([.55, .9], "#d9a650", a=[0, .4]), veins(BLACK, .022), band([.88, 1.3], BLACK), spots(.78, .022, "#f4dca0", cells=[1, 2, 3]), spots(.93, .011, WHITE), spots(.975, .008, WHITE)),
   "hind": side("#e2b05a", veins(BLACK, .026), band([.86, 1.3], BLACK), spots(.91, .012, WHITE), spots(.965, .009, WHITE))},
  "the migrant: tawny orange cut by black veins, the black margin with two rows of white spots; paler, buff beneath")
species("swallowtail", "Swallowtail", "Papilio machaon", "papilio", .08, "#1c1816",
  {"fore": side("#f0d448", band([0, .3], "#2a2420"), dust(["#2a2420", "#f0d448"], t=[0, .3], amount=.35, scale=60), band([.33, .4], BLACK, a=[0, .42]), band([.5, .56], BLACK, a=[0, .2]),
                veins(BLACK, .016), band([.68, 1.3], BLACK), spots(.84, .03, "#f0d448"), fringe("#f0d448", alt=BLACK)),
   "hind": side("#f0d448", band([0, .22], "#2a2420"), veins(BLACK, .016), band([.62, 1.3], BLACK), spots(.72, .03, "#4f78c4", shape="lunule", cells=[1, 2, 3, 4, 5, 6]),
                spots(.9, .032, "#f0d448", shape="lunule"), eye(.76, .05, ["#d8382a"], pupil="#2a4fa0", cell=7), fringe("#f0d448"), tail=BLACK)},
  {"fore": side("#eedc80", band([0, .2], "#6a5a3a"), band([.33, .4], "#3a3028", a=[0, .42]), veins("#3a3028", .016), band([.72, .95], "#4a3f30"), spots(.84, .03, "#eedc80"), fringe("#eedc80", alt="#3a3028")),
   "hind": side("#eedc80", veins("#3a3028", .016), band([.62, .95], "#4a3f30"), spots(.72, .03, "#6f8fc8", shape="lunule", cells=[1, 2, 3, 4, 5, 6]), spots(.73, .022, "#e89a3a", cells=[2, 3, 4]),
                eye(.76, .05, ["#d8382a"], pupil="#2a4fa0", cell=7), tail="#3a3028")},
  "yellow with black veins and bands, a row of blue lunules on the hindwing, a red eye at its anal angle, the tail black")
species("scarce-swallowtail", "Scarce swallowtail", "Iphiclides podalirius", "papilio", .08, "#2a2420",
  {"fore": side("#f1ead0", band([.1, .17], BLACK, slope=.04), band([.26, .34], BLACK), band([.44, .5], BLACK, a=[0, .8]), band([.58, .64], BLACK, a=[0, .5]), band([.75, .82], BLACK, a=[0, .35]),
                band([.86, .93], "#3a3430"), veins("#2a2420", .01), fringe("#f1ead0")),
   "hind": side("#f1ead0", band([.1, .3], BLACK, a=[.55, 1]), band([.4, .48], BLACK, a=[.5, 1]), band([.7, .78], "#3a3430"), spots(.86, .03, "#5a7fc0", shape="lunule", cells=[2, 3, 4, 5, 6]),
                eye(.84, .05, ["#e88a2a", "#e88a2a"], pupil="#3a64b0", cell=7), veins("#2a2420", .01), tail=BLACK)},
  {"fore": side("#ece4c4", band([.1, .17], "#4a3e30"), band([.26, .34], "#4a3e30"), band([.44, .5], "#4a3e30", a=[0, .8]), band([.58, .64], "#4a3e30", a=[0, .5]), veins("#5a4e40", .01)),
   "hind": side("#ece4c4", band([.4, .48], "#4a3e30", a=[.5, 1]), band([.5, .56], "#e8a050", a=[.2, .9]), band([.7, .78], "#5a4e40"), spots(.86, .03, "#7a9ad0", shape="lunule", cells=[2, 3, 4, 5, 6]), tail="#4a3e30")},
  "pale cream barred black like a tiger, the bars running on across both wings, blue lunules, an orange eye, very long tails")
species("peacock", "Peacock", "Aglais io", "nymphalid-scalloped", .06, "#241a18",
  {"fore": side("#a12a22", grad([0, .45], "#4a2a22", "#a12a22"), band([.3, .38], BLACK, a=[0, .12]), band([.46, .56], "#e8d08a", a=[0, .12]), band([.94, 1.3], "#4a332a"),
                eye(.72, .15, ["#e8d29a", "#3a2a50", "#7f52a6", "#e4d4b0"], pupil="#1c1424", at=.2, aspect=1.15)),
   "hind": side("#8b2420", grad([0, .5], "#3a2420", "#8b2420"), band([.93, 1.3], "#4a332a"), eye(.62, .21, ["#1d1a1e", "#5a6e9c", "#9ab0d6"], pupil="#121016", glint="#eef2ff", cell=3))},
  {"fore": side("#2a221e", dust(["#151110", "#3a2f28", "#221a16"], scale=40, amount=.8), band([.42, .46], "#100c0a", wave={"amp": .03, "n": 7})),
   "hind": side("#2a221e", dust(["#151110", "#3a2f28", "#221a16"], scale=40, amount=.8), band([.4, .44], "#100c0a", wave={"amp": .04, "n": 6}))},
  "maroon-red with a great peacock's eye on each wing (lilac and yellow on the forewing, blue on the hind); beneath almost black, like charred bark")
species("red-admiral", "Red admiral", "Vanessa atalanta", "nymphalid", .06, "#1c1816",
  {"fore": side("#1d1a1c", band([.4, .58], "#d84a24", slope=.22, a=[0, .85]), spots(.76, .03, WHITE, cells=[0, 1, 2]), spots(.6, .035, WHITE, cells=[0], aspect=1.6), spots(.9, .012, "#5a7ac0", cells=[7, 8]), fringe(WHITE, alt=BLACK)),
   "hind": side("#1d1a1c", band([.78, .95], "#d84a24", a=[.12, 1]), spots(.865, .018, BLACK, cells=[1, 2, 3, 4, 5]), spots(.9, .03, "#3a6ab8", cells=[7]), fringe(WHITE, alt=BLACK))},
  {"fore": side("#2a2428", band([.4, .58], "#d8604a", slope=.22, a=[0, .85]), band([.1, .3], "#4a5a8a", a=[.1, .5]), spots(.76, .03, WHITE, cells=[0, 1, 2]), dust(["#2a2428", "#5a4a40"], t=[.62, 1], a=[0, .4], amount=.5)),
   "hind": side("#6a5040", dust(["#3a2c24", "#8a6a50", "#c0a080", "#4a3a30"], scale=26, amount=.9), band([.4, .46], "#c8b090", wave={"amp": .03, "n": 5}))},
  "velvet black with an oblique red band across the forewing and a red border on the hindwing, white spots at the apex; the hindwing beneath a marbled bark")
species("painted-lady", "Painted lady", "Vanessa cardui", "nymphalid", .055, "#3a2a20",
  {"fore": side("#e8944c", grad([0, .35], "#9a6a48", "#e8944c"), band([.56, 1.3], BLACK, a=[0, .45]), band([.36, .48], BLACK, a=[.32, .82]), spots(.72, .028, WHITE, cells=[0, 1, 2]), spots(.88, .02, WHITE, cells=[0, 1, 2, 3])),
   "hind": side("#e8944c", grad([0, .4], "#9a6a48", "#e8944c"), spots(.78, .03, BLACK, cells=[1, 2, 3, 4, 5, 6]), spots(.9, .02, "#2a2420", shape="lunule"), band([.97, 1.3], BLACK))},
  {"fore": side("#e8a888", band([.56, 1.3], "#5a4030", a=[0, .45]), spots(.72, .028, WHITE, cells=[0, 1, 2]), spots(.4, .04, BLACK, cells=[4, 5])),
   "hind": side("#c8b090", dust(["#a08868", "#e8dcc0", "#6a5a48"], scale=30, amount=.7), *[eye(.78, .035, ["#d8c8a8", "#5a6a8a"], pupil="#2a2a3a", cell=c) for c in [2, 3, 4, 5, 6]])},
  "salmon orange, the forewing's tip black with white spots, rows of black spots on the hindwing; beneath marbled, with five small eyes")
species("cabbage-white", "Large white", "Pieris brassicae", "pierid", .06, "#2a2a2a",
  {"fore": side("#f3f1e6", grad([0, .18], "#9a9a9a", "#f3f1e6"), band([.72, 1.3], "#262626", a=[0, .55], slope=-.15), spots(.62, .045, "#262626", cells=[3, 5])),
   "hind": side("#f3f1e6", grad([0, .2], "#9a9a9a", "#f3f1e6"), spots(.7, .04, "#262626", cells=[0]))},
  {"fore": side("#f2eedc", band([.72, 1.3], "#e8e0a0", a=[0, .55]), spots(.62, .045, "#3a3a3a", cells=[3, 5])),
   "hind": side("#e9e2b0", dust(["#d8d0a0", "#b8b498"], scale=50, amount=.4))},
  "white, the forewing's tip black and (in the female) two black spots; beneath the hindwing pale yellow, dusted grey")
species("brimstone", "Brimstone", "Gonepteryx rhamni", "gonepteryx", .06, "#8a8a50",
  {"fore": side("#f2e24a", spots(.45, .028, "#e67a1c", at=.42), spots(.995, .008, "#8a4a2a")),
   "hind": side("#f0de48", spots(.45, .032, "#e67a1c", at=.4), spots(.99, .008, "#8a4a2a"))},
  {"fore": side("#e2e4a0", veins("#c8c88a", .012), spots(.45, .022, "#9a6a3a", at=.42)),
   "hind": side("#dfe0a0", veins("#c4c486", .014), spots(.45, .026, "#9a6a3a", at=.4))},
  "sulphur yellow with an orange spot on each wing, the forewing's tip hooked like a leaf's; beneath leaf-green, veined like a leaf")
species("blue-morpho", "Blue morpho", "Morpho menelaus", "morpho", .14, "#2a2018",
  {"fore": side("#2a8adb", grad([0, 1], "#5ac0ff", "#1a58b0"), band([.84, 1.3], "#121418", a=[0, .62]), band([.0, .12], "#121418", a=[0, .08]), spots(.9, .02, WHITE, cells=[0, 1, 2])),
   "hind": side("#2a8adb", grad([0, 1], "#5ac0ff", "#1a58b0"), band([.9, 1.3], "#121418"), spots(.95, .012, "#8ac0f0"))},
  {"fore": side("#6a4a2e", dust(["#4a3020", "#8a6a48", "#6a4a2e"], scale=22, amount=.6), *[eye(.62, .07, ["#d8b860", "#2a1a10"], pupil="#f0e8d0", pupilR=.25, cell=c) for c in [2, 4, 6]]),
   "hind": side("#6a4a2e", dust(["#4a3020", "#8a6a48", "#6a4a2e"], scale=22, amount=.6), *[eye(.62, .08, ["#d8b860", "#2a1a10"], pupil="#f0e8d0", pupilR=.25, cell=c) for c in [1, 3, 5]])},
  "iridescent sky blue edged black (the colour is the scales' structure: it shifts from bright to deep across the wing); beneath brown with a row of ochre-ringed eyes")
species("common-blue", "Common blue", "Polyommatus icarus", "lycaenid", .033, "#3a3a4a",
  {"fore": side("#7a8fe0", grad([0, 1], "#8a7ae8", "#6a8ae0"), band([.96, 1.3], "#2a2a3a"), fringe(WHITE, width=.05)),
   "hind": side("#7a8fe0", grad([0, 1], "#8a7ae8", "#6a8ae0"), band([.95, 1.3], "#2a2a3a"), spots(.92, .012, "#2a2a3a", cells=[1, 2, 3, 4, 5]), fringe(WHITE, width=.05))},
  {"fore": side("#c8bcaa", grad([0, .25], "#8a9ab0", "#c8bcaa"), eye(.62, .032, [WHITE], pupil=BLACK, pupilR=.6, cells=[2, 3, 4, 5, 6]), eye(.42, .03, [WHITE], pupil=BLACK, pupilR=.6, at=.45, aspect=1.4),
                spots(.86, .02, "#a89888", shape="lunule"), fringe(WHITE, width=.05)),
   "hind": side("#c8bcaa", grad([0, .25], "#8a9ab0", "#c8bcaa"), eye(.55, .03, [WHITE], pupil=BLACK, pupilR=.6, cells=[1, 2, 3, 4, 5]), eye(.3, .028, [WHITE], pupil=BLACK, pupilR=.6, cells=[2, 4]),
                spots(.84, .03, "#e8822a", shape="lunule", cells=[1, 2, 3, 4, 5, 6]), spots(.93, .012, BLACK, cells=[1, 2, 3, 4, 5, 6]), fringe(WHITE, width=.05))},
  "small, violet-blue above with a white fringe; beneath grey-brown, sprinkled with white-ringed black spots and a row of orange lunules")
species("small-tortoiseshell", "Small tortoiseshell", "Aglais urticae", "nymphalid-scalloped", .05, "#2a201a",
  {"fore": side("#e0592a", band([.28, .38], BLACK, a=[0, .26]), band([.48, .6], BLACK, a=[0, .3]), band([.68, .8], BLACK, a=[0, .3]), band([.38, .48], "#f0c040", a=[0, .2]), band([.6, .68], "#f0c040", a=[0, .2]),
                spots(.86, .025, WHITE, cells=[0]), spots(.5, .035, BLACK, cells=[4, 5]), spots(.4, .04, BLACK, cells=[7]), band([.9, 1.3], "#2b2420"), spots(.935, .018, "#4a7ad0", shape="lunule")),
   "hind": side("#e0592a", band([0, .55], "#2a221e"), band([.9, 1.3], "#2b2420"), spots(.935, .02, "#4a7ad0", shape="lunule"))},
  {"fore": side("#c8a878", band([0, .5], "#3a2c22"), band([.28, .38], "#2a201a", a=[0, .26]), band([.48, .6], "#2a201a", a=[0, .3]), dust(["#a88858", "#d8c098"], t=[.5, 1], amount=.5)),
   "hind": side("#4a3a2c", band([0, .55], "#2a201a"), dust(["#3a2c22", "#6a5644", "#8a7458"], scale=34, amount=.7), band([.88, .94], "#6a5a8a"))},
  "orange-red, the costa barred black and yellow, the hindwing's base dark, a row of blue lunules in the dark border; beneath two-toned bark")
species("owl", "Owl butterfly", "Caligo eurilochus", "morpho", .13, "#3a2c20",
  {"fore": side("#6a6a78", grad([0, .7], "#4a5a8a", "#8a7a68"), band([.5, .6], "#d8c8a0", a=[.1, .7], slope=.1)),
   "hind": side("#4a4258", grad([0, .7], "#3a4a7a", "#5a4a40"), band([.88, 1.3], "#2a2420"))},
  {"fore": side("#a89478", dust(["#6a5a48", "#c8b898", "#4a3e32"], scale=28, amount=.75), eye(.72, .06, ["#e0d0a0", "#1a1410"], pupil="#f0e8d0", pupilR=.3, cell=6)),
   "hind": side("#9a8670", dust(["#5a4a3a", "#c0ae90", "#3a3028"], scale=24, amount=.8), eye(.55, .22, ["#e9d9a0", "#1a1410", "#d8c890"], pupil="#0e0c0a", glint="#ffffff", cell=4))},
  "dull blue and brown above; beneath marbled grey-brown with a great owl's eye on each hindwing, shown when it rests")
species("zebra-longwing", "Zebra longwing", "Heliconius charithonia", "heliconius", .08, "#1c1816",
  {"fore": side("#1a1818", band([.18, .3], "#f2e070", a=[0, 1]), band([.46, .56], "#f2e070", a=[0, .72], slope=.05), band([.7, .78], "#f2e070", a=[0, .42]), spots(.88, .012, "#f2e070", cells=[0, 1, 2, 3, 4])),
   "hind": side("#1a1818", band([.32, .5], "#f2e070", a=[0, .9]), spots(.82, .014, "#f2e070", cells=[1, 2, 3, 4, 5, 6]), spots(.9, .012, "#f2e070", cells=[1, 2, 3, 4, 5, 6]))},
  {"fore": side("#2a2422", band([.18, .3], "#f0e8b0"), band([.46, .56], "#f0e8b0", a=[0, .72]), band([.7, .78], "#f0e8b0", a=[0, .42]), spots(.1, .02, "#d84a3a", cells=[0, 1])),
   "hind": side("#2a2422", band([.32, .5], "#f0e8b0", a=[0, .9]), spots(.82, .014, "#f0e8b0", cells=[1, 2, 3, 4, 5, 6]), spots(.12, .02, "#d84a3a", cells=[0, 1, 2]))},
  "long narrow black wings striped lemon yellow (it flies slowly, being poisonous); beneath the same, paler, with red spots at the base")

def main():
    os.makedirs(OUT, exist_ok=True)
    json.dump({"kind": "butterfly-shapes", "name": "Butterfly wing shapes", "_about": "the wing outlines as POLAR profiles from the wing's root (butterflies.js wingProfile): for the forewing and the hindwing, `from` / `to` the costa's and the inner margin's direction (degrees from the body's forward), `R` [[degrees, radius x the forewing's length], ...] through a smooth curve, `veins` how many reach the margin (the cells between them), `scallop` { amp, n }, `tail` { at (degrees), length, width (degrees), round }; `hindRoot` the hindwing's root behind the forewing's. A species names one and may override any number of it.", "shapes": SHAPES},
              open(os.path.join(OUT, "shapes.json"), "w"), indent=1, ensure_ascii=False)
    for k, v in SP.items(): json.dump(v, open(os.path.join(OUT, k + ".json"), "w"), indent=1, ensure_ascii=False)
    ip = os.path.join(ROOT, "assets", "index.json"); idx = json.load(open(ip))
    cats = [c for c in idx["categories"] if c["kind"] != "butterfly"]
    cats.append({"name": "Butterflies", "kind": "butterfly", "paths": ["butterflies/shapes"] + ["butterflies/" + k for k in SP]})
    idx["categories"] = cats; json.dump(idx, open(ip, "w"), indent=2, ensure_ascii=False); open(ip, "a").write("\n")
    print(len(SHAPES), "shapes,", len(SP), "species")

if __name__ == "__main__": main()
