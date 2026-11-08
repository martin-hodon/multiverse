# ear_shapes.py (2026-11-08): each species' EAR as ears2.py draws it -- which old shapes it replaces (`ids`; `main` the
# one it is measured from), its outline (ears2.prof: base / tc / m / pe, `round` for a round end), how it is turned
# (`face`: the side the hollow looks to; `turn` about its own length, `tilt` [axis, degrees] of the whole ear, `L` / `W`
# outright), sized (`long`, `wide`: shares of the old ear's reach and half-width; `hw`, `reach` outright), cupped
# (`cup`), bent (`bend` degrees from `bendAt` of its length: a drop ear) and coloured (`color` the back, `inner` the
# hollow, `innerRim` a share of the half-width in `color` round it, `rim` a share of the half-width of `rimColor` round
# the edge on both faces, `tip` / `tipAt`); `fair` (a share of the half-width) the fillet into the head; `thick`
# metres; `tuft` a thin horn out of the tip (a lynx's).
F = [1, 0, 0.35]   # (forward and a little out: most hollows)
FO = [1, 0, 0.75]  # (forward and out: a cat's hollow, turned so)

# outlines
TRI = {"base": 1.0, "tc": 0.0, "m": 1.4, "pe": 0.85}             # a tall triangle: a fox's, a wolf's, a lynx's
CAT = {"base": 1.0, "tc": 0.0, "m": 1.35, "pe": 0.7, "round": 1}   # an upright triangle, the sides a little full, the tip round
ROUND = {"base": 0.8, "tc": 0.3, "m": 2.0, "pe": 0.55, "round": 1}  # a big cat's, a bear's
DROP = {"base": 0.75, "tc": 0.4, "m": 1.6, "pe": 0.6, "round": 1}  # a drop ear: a rounded flap
BROAD = {"base": 0.5, "tc": 0.45, "m": 2.0, "pe": 0.75}  # a cow's, a sheep's: a broad leaf
OVAL = {"base": 0.65, "tc": 0.4, "m": 2.0, "pe": 0.6, "round": 1}  # a reindeer's, an oryx's: short, round-ended
FENNEC = {"base": 0.85, "tc": 0.3, "m": 1.8, "pe": 0.65, "round": 1}   # a fennec's: huge, broad, the sides full, the tip round
LEAF = {"base": 0.55, "tc": 0.38, "m": 1.8, "pe": 0.85}            # a horse's, a deer's: narrow at the root, a point

HARE = {"base": 0.6, "tc": 0.4, "m": 2.2, "pe": 0.6, "round": 1}   # a hare's: very long, the tip round
PIG = {"base": 0.85, "tc": 0.25, "m": 1.3, "pe": 0.9}               # a pig's: a broad pointed flap
BAT = {"base": 0.85, "tc": 0.25, "m": 1.6, "pe": 0.7, "round": 1}  # a bat's: tall, broad below, the tip round
SHELL = {"base": 0.9, "tc": 0.35, "m": 2.0, "pe": 0.55, "round": 1}  # a primate's: a D-shaped shell

SPEC = {
    # ---------------------------------------------------------------- FELIDS
    "mammals/cat": dict(ids=["ear0", "earIn0", "ear1", "earIn1"], main="ear0", tris=["ear0", "ear1"], outline=CAT, faceTo=FO,
                        cup=0.55, color="@ear", inner="@earIn", innerRim=0.28, fair=0.3,
                        about="The EARS (ears2.py): one cupped sheet each (sharp.js `fin`), an upright triangle with full sides and a round tip, the hollow pink inside a band of fur, the root faired into the head."),
    "mammals/lynx": dict(ids=["ear0", "earIn0", "ear1", "earIn1", "earBack", "earTuft", "earTuft2"], main="ear0", tris=["ear0", "ear1"], noreach=["earTuft", "earTuft2"],
                         outline=TRI, faceTo=FO, cup=0.55, color="@ear", inner="@earIn", innerRim=0.18, rim=0.38, rimColor="@black", fair=0.3,
                         tuft={"len": 0.55, "r": 0.035},
                         about="The EARS (ears2.py): tall pointed cupped sheets (sharp.js `fin`), the edge black on both faces (a pale patch in the black back), the hollow pale; the long black tuft the outline run on past the tip as a narrow spike (black by the edge band); the roots faired."),
    "mammals/leopard": dict(ids=["ear", "earIn", "earBack", "earSpot"], outline=ROUND, faceTo=FO, cup=0.6, color="@white", inner="@pale", innerRim=0.12,
                            rim=0.6, rimColor="@ear", fair=0.3,
                            about="The EARS (ears2.py): round cupped sheets (sharp.js `fin`), black behind round a white spot (the back's edge band `rim`), pale in the hollow; the roots faired."),
    "mammals/lion": dict(ids=["L3ear", "L4earTuft", "L3earIn", "L3earBase"], main="L3ear", expr=True, outline=ROUND, faceTo=FO, cup=0.6, skip=r"mane.*|lock\d+|tuft.*",
                         color="@ear", inner="@earIn", innerRim=0.15, rim=0.3, rimColor="@earBack", fair=0.3,
                         about="The EARS (ears2.py): round cupped sheets (sharp.js `fin`) written over the head's params (the lioness's bigger), dark edged, pale-furred in the hollow; the roots faired."),
    "mammals/tiger": dict(ids=["L3ear", "L4earTuft", "L3earIn", "L3earBase", "earBack", "earSpot"], main="L3ear", expr=True, outline=ROUND, faceTo=FO, cup=0.6,
                          color="@white", inner="@white", innerRim=0.1, rim=0.65, rimColor="@black", fair=0.3,
                          about="The EARS (ears2.py): round cupped sheets (sharp.js `fin`), black behind round the white spot (the edge band `rim`), white-furred in the hollow; the roots faired."),
    "mammals/smilodon": dict(ids=["ear", "earIn"], outline=ROUND, faceTo=FO, cup=0.55, color="@ear", inner="@cream", innerRim=0.15, fair=0.3,
                             about="The EARS (ears2.py): small round cupped sheets (sharp.js `fin`), cream in the hollow; the roots faired."),
    "monsters/manticore": dict(ids=["ear", "earIn", "earBack"], skip=r"mane.*|lock\d+", long=1.2, outline=ROUND, faceTo=FO, cup=0.6, color="@ear", inner="@cream", innerRim=0.15,
                               rim=0.3, rimColor="@black", fair=0.3,
                               about="The EARS (ears2.py): round cupped sheets (sharp.js `fin`), dark edged, cream in the hollow; the roots faired."),
    # ---------------------------------------------------------------- CANIDS, BEARS, SMALL CARNIVORES
    # (the farm dog's DROP ears: from the top of the skull, hanging down the side of the head, the hollow toward it)
    "mammals/dog": dict(ids=["ear", "earLow", "earRoot"], flat=True, rootAt="earRoot", Lhint=[0, -1, 0], Lplus=[0, 0, 0.18], face=[0, 0, -1],
                        outline=DROP, cup=0.3, lift=0.3, liftDir=[0, 0.2, 1], color="@ear", inner="@earIn", innerRim=0.15, fair=0.3,
                        about="The DROP EARS (ears2.py): one sheet each (sharp.js `fin`) out of the top of the skull, hanging down the side of the head, the hollow toward it, the root faired."),
    # (the FENNEC, a fox VARIANT: the fox's own old ear measured again, its numbers over the fox's -- 2.5 times as long
    #  against the head, broad from a wide root, splayed out; written into variants.fennec.sculpt (ears2.py run_variant)
    #  with the rest of the variant (`look`): its size, its colours, the dark streak under the eye)
    "mammals/fox#fennec": dict(of="mammals/fox", variant="fennec", long=3.3, wide=1.85, faceTo=[1, 0, 0.6], tilt=[[[1, 0, 0], 18]], shift=[0, -0.004, 0.02],
                               outline=FENNEC, keepPat=False, thick=0.005, cup=1.0, curl=0.12, curlAt=0.65, color="@ear", inner="@earIn", innerRim=0.0,
                               rim=0.22, rimColor="@earRim", rimBack=0.3,
                               look={"scale": 0.58, "colors": {
                                   "body": "#e0c08e", "saddle": "#cf9f66", "head": "#e4c89c", "mask": "#efdcbc", "muzzleC": "#ead6b6",
                                   "muzzle": "#f1e4cc", "lip": "#f7f1e6", "belly": "#f8f3ea", "chestc": "#f6efe2", "throat": "#f8f3ea",
                                   "ear": "#d4ae78", "earIn": "#ecd0bc", "earRim": "#f8f2e8", "leg": "#dfbf90", "foot": "#e8d2ae",
                                   "tail": "#d2a873", "tip": "#1e1612", "gland": "#3a2618", "eye": "#3a2412", "streak": "#7a4a26"},
                                     "shape": [{"id": "streak", "type": "cone", "bone": "head", "a": [0.4135, 0.4545, 0.0255], "b": [0.4385, 0.4375, 0.0215],
                                                "ra": 0.0042, "rb": 0.003, "k": 0.0008, "kc": 0.0012, "op": "paint", "color": "@streak", "mirror": True},
                                               {"id": "tailBlack", "type": "ell", "bone": "tail", "c": [-0.665, 0.2, 0], "r": [0.095, 0.11, 0.11],
                                                "k": 0.004, "kc": 0.006, "op": "paint", "color": "@tip"},
                                               {"id": "gland", "type": "ell", "bone": "tail", "c": [-0.31, 0.318, 0], "r": [0.034, 0.034, 0.022],
                                                "k": 0.002, "kc": 0.004, "op": "paint", "color": "@gland"}]},
                               about="The FENNEC (variant, ears2.py): the fox at .58, its ears about 2.3 times as long against the head and .6 as broad as long -- round-tipped, set wide and turned forward and out, deeply cupped with the edges rolled in, buff behind paling to a cream rim, pinkish cream in the hollow inside a band of white hair -- a pale face with a dark streak below each eye, a reddish-buff back, white below, pale legs, the brush's last seventh black and a dark spot (the gland) on its upper base. Only its ears (fins) and paints (streak, tail tip, gland) are its own: the fox's shape build is shared, scaled."),
    "mammals/wolf": dict(ids=["earF", "earB", "earSi", "earSo", "earRim"], main="earF", tris=["earF"], basePts=[[0.634, 0.89, 0.043], [0.626, 0.866, 0.09]],
                         outline=TRI, faceTo=[1, 0, 0.45], cup=0.55, color="@ear", inner="@earIn", innerRim=0.2, rim=0.1, rimColor="@tip", rimAt=0.45, fair=0.3,
                         about="The EARS (ears2.py): tall pointed cupped sheets (sharp.js `fin`), pale in the hollow, the upper edges dark; the roots faired."),
    "mammals/fox": dict(ids=["ear0", "earBack0", "earIn0", "ear1", "earBack1", "earIn1", "ear2", "earBack2", "earIn2", "earTip0", "earTip1"], main="ear0",
                        tris=["ear0", "ear1", "ear2"], basePts=[[0.372, 0.4914, 0.0136], [0.3461, 0.477, 0.0628]],
                        outline=TRI, faceTo=[1, 0, 0.45], cup=0.55, color="@ear", inner="@earIn", innerRim=0.12, fair=0.3,
                        about="The EARS (ears2.py): tall pointed cupped sheets (sharp.js `fin`), black behind, white fur in the hollow; the roots faired."),
    "mammals/hyena": dict(ids=["earBase", "ear", "earIn"], noreach=["earBase"], outline=ROUND, faceTo=[1, 0, 0.5], cup=0.6, color="@ear", inner="@earIn", innerRim=0.15,
                          rim=0.18, rimColor="@earRim", fair=0.3,
                          about="The EARS (ears2.py): broad ROUNDED cupped sheets (sharp.js `fin`), dark edged; the ball at the root gone, the roots faired."),
    "mammals/redpanda": dict(ids=["earIn", "earIn1", "earIn2", "earIn3", "earIn4", "ear", "ear1", "ear2", "ear3", "ear4", "earMid", "earMid1", "earMid2", "earMid3", "earMid4"],
                             main="ear", tris=["ear", "ear1", "ear2", "ear3", "ear4"], apexPt=[0.1857, 0.3161, 0.0812], basePts=[[0.195, 0.322, 0.031], [0.196, 0.281, 0.033]],
                             outline=CAT, faceTo=[1, 0.2, 0.3], cup=0.5, color="@ear", inner="@white", innerRim=0.1, rim=0.3, rimColor="@white", fair=0.3, keepPat=False,
                             about="The EARS (ears2.py): big rounded-triangular cupped sheets (sharp.js `fin`), white-furred in the hollow and round the edge, dark behind; the roots faired."),
    "mammals/badger": dict(ids=["ear"], outline=ROUND, faceTo=[1, 0, 0.6], cup=0.5, color="@body", inner="@ear", rim=0.35, rimColor="@white", fair=0.3, keepPat=False,
                           about="The EARS (ears2.py): small round cupped sheets (sharp.js `fin`), white edged; the roots faired."),
    "mammals/skunk": dict(ids=["ear"], outline=ROUND, faceTo=[1, 0, 0.6], cup=0.5, color="@body", inner="@ear", fair=0.3, keepPat=False,
                          about="The EARS (ears2.py): small round cupped sheets (sharp.js `fin`); the roots faired."),
    "mammals/weasel": dict(ids=["ear"], outline=ROUND, faceTo=[1, 0, 0.6], cup=0.45, color="@ear", fair=0.3, keepPat=False,
                           about="The EARS (ears2.py): small round cupped sheets (sharp.js `fin`); the roots faired."),
    "mammals/giantpanda": dict(ids=["ear"], outline=ROUND, faceTo=[1, 0, 0.6], cup=0.5, color="@black", fair=0.3, keepPat=False,
                               about="The EARS (ears2.py): round black cupped sheets (sharp.js `fin`); the roots faired."),
    "mammals/bear": dict(ids=["ear", "earIn"], outline=ROUND, faceTo=[1, 0, 0.6], cup=0.5, color="@ear", inner="@earIn", innerRim=0.2, fair=0.3,
                         about="The EARS (ears2.py): small round cupped sheets (sharp.js `fin`), darker in the hollow; the roots faired."),
    # ---------------------------------------------------------------- EQUIDS
    "mammals/horse": dict(ids=["ear", "earIn"], Lhint=[0, 1, 0], rootNear=1.0, skip=r"lk.*|fl\d+|mane.*|forelock.*", outline=LEAF, faceTo=[1, 0, 0.3], cup=0.6, color="@ear", inner="@earIn", innerRim=0.22, rim=0.12, rimColor="@mane", rimAt=0.5, fair=0.3,
                          about="The EARS (ears2.py): long LEAVES (sharp.js `fin`), narrow at the root and pointed, cupped forward, dark in the hollow and along the upper edges; the roots faired."),
    "monsters/pegasus": dict(ids=["ear", "earIn"], Lhint=[0, 1, 0], rootNear=1.0, skip=r"lk.*|fl\d+|mane.*|forelock.*", outline=LEAF, faceTo=[1, 0, 0.3], cup=0.6, color="@ear", inner="@earIn", innerRim=0.22, fair=0.3,
                             about="The EARS (ears2.py): long LEAVES (sharp.js `fin`), narrow at the root and pointed, cupped forward; the roots faired."),
    "monsters/unicorn": dict(ids=["ear", "earIn"], Lhint=[0, 1, 0], rootNear=1.3, skip=r"lk.*|fl\d+|mane.*|forelock.*", outline=LEAF, faceTo=[1, 0, 0.3], cup=0.6, color="@ear", inner="@earIn", innerRim=0.22, fair=0.3,
                             about="The EARS (ears2.py): long LEAVES (sharp.js `fin`), narrow at the root and pointed, cupped forward; the roots faired."),
    # ---------------------------------------------------------------- BOVIDS, CERVIDS, CAMELIDS
    "mammals/cow": dict(ids=["ear", "earIn"], outline=BROAD, faceTo=[1, -0.5, 0.1], cup=0.55, color="@ear", inner="@earIn", innerRim=0.18, fair=0.3,
                        about="The EARS (ears2.py): broad LEAVES held out sideways (sharp.js `fin`), the hollow forward and down; the roots faired."),
    "mammals/ox": dict(ids=["ear", "earIn"], outline=BROAD, faceTo=[1, -0.5, 0.1], cup=0.55, color="@ear", inner="@earIn", innerRim=0.18, fair=0.3,
                       about="The EARS (ears2.py): broad LEAVES held out sideways (sharp.js `fin`), the hollow forward and down; the roots faired."),
    "mammals/deer": dict(ids=["ear", "earTip", "earIn"], outline=LEAF, faceTo=[1, 0, 0.6], cup=0.6, color="@ear", inner="@earIn", innerRim=0.15, rim=0.1, rimColor="@head", fair=0.3,
                         patFace="back", about="The EARS (ears2.py): big LEAVES held up and out (sharp.js `fin`), cupped forward and out, pale in the hollow; the roots faired."),
    "mammals/reindeer": dict(ids=["ear", "earTip", "earIn"], outline=OVAL, faceTo=[1, 0, 0.6], cup=0.55, color="@ear", inner="@earIn", innerRim=0.15, fair=0.3,
                             about="The EARS (ears2.py): short oval cupped sheets (sharp.js `fin`); the roots faired."),
    "mammals/impala": dict(ids=["ear", "earTip", "earIn"], outline=LEAF, faceTo=[1, 0, 0.6], cup=0.6, color="@ear", inner="@earIn", innerRim=0.12, tip="@earTip", tipAt=0.82, fair=0.3,
                           about="The EARS (ears2.py): long pointed LEAVES (sharp.js `fin`), white in the hollow, the tips black; the roots faired."),
    "mammals/oryx": dict(ids=["ear", "earTip", "earIn"], outline=OVAL, faceTo=[1, 0, 0.6], cup=0.55, color="@ear", inner="@earIn", innerRim=0.15, fair=0.3,
                         about="The EARS (ears2.py): broad round-tipped cupped sheets (sharp.js `fin`), pale in the hollow; the roots faired."),
    "mammals/chamois": dict(ids=["ear", "earTip", "earIn"], outline=LEAF, faceTo=[1, 0, 0.6], cup=0.6, color="@ear", inner="@earIn", innerRim=0.12, tip="@earTip", tipAt=0.8, fair=0.3,
                            about="The EARS (ears2.py): pointed upright LEAVES (sharp.js `fin`), pale in the hollow, the tips dark; the roots faired."),
    "mammals/cervicapra": dict(ids=["ear", "earTip", "earIn"], outline=LEAF, faceTo=[1, 0, 0.6], cup=0.6, color="@ear", inner="@earIn", innerRim=0.12, fair=0.3,
                               about="The EARS (ears2.py): pointed LEAVES (sharp.js `fin`), paler in the hollow; the roots faired."),
    "mammals/ram": dict(ids=["earStalk", "ear", "earTip", "earIn"], outline=BROAD, faceTo=[1, -0.6, 0.2], cup=0.5, color="@ear", inner="@earIn", innerRim=0.18, fair=0.3,
                        about="The EARS (ears2.py): sideways LEAVES (sharp.js `fin`), drooping a little, the hollow forward and down; the stalk ball gone, the roots faired."),
    "mammals/sheep": dict(ids=["earStalk", "ear", "earTip", "earIn"], outline=BROAD, faceTo=[1, -0.6, 0.2], cup=0.5, color="@ear", inner="@earIn", innerRim=0.18, fair=0.3,
                          about="The EARS (ears2.py): sideways LEAVES (sharp.js `fin`), drooping a little, the hollow forward and down; the stalk ball gone, the roots faired."),
    "mammals/camel": dict(ids=["ear"], outline=ROUND, faceTo=[1, 0, 0.6], cup=0.5, color="@ear", fair=0.3,
                          about="The EARS (ears2.py): small round cupped sheets (sharp.js `fin`); the roots faired."),
    "mammals/bactrian": dict(ids=["ear"], outline=ROUND, faceTo=[1, 0, 0.6], cup=0.5, color="@ear", fair=0.3,
                             about="The EARS (ears2.py): small round cupped sheets (sharp.js `fin`); the roots faired."),
    # ---------------------------------------------------------------- PIG, HIPPO, RHINO, ELEPHANT
    "mammals/pig": dict(ids=["ear"], L=[0.45, 0.75, 0.5], rootNear=0.3, reach=0.12, wide=0.75, outline=PIG, faceTo=[1, -0.2, 0.3], cup=0.4, bend=-35, bendAt=0.4,
                        color="@body", inner="@ear", innerRim=0.12, fair=0.3,
                        about="The EARS (ears2.py): broad pointed flaps (sharp.js `fin`) out of the top of the head, leaning forward, the tips tipped further over, the hollow forward; the roots faired."),
    "mammals/hippo": dict(ids=["ear", "earIn"], outline=ROUND, faceTo=[1, 0, 0.6], cup=0.6, color="@skin", inner="@pink", innerRim=0.15, fair=0.3,
                          about="The EARS (ears2.py): small round cupped sheets (sharp.js `fin`) high on the head, pink in the hollow; the roots faired."),
    "mammals/rhinoceros": dict(ids=["ear", "earTip", "earIn"], outline=OVAL, faceTo=[1, 0, 0.5], cup=0.9, color="@ear", inner="@earIn", innerRim=0.12, fair=0.3,
                               about="The EARS (ears2.py): tall tubular cupped sheets (sharp.js `fin`), the edges rolled in, round-tipped; the roots faired."),
    "mammals/elephant": dict(ids=["ear", "earRim0_0", "earLobe", "earRim1_0", "earRoot"], main="ear", face=[-0.5, 0, -0.87],
                             plane2d={"origin": "earRoot", "outDir": [0.5, 0, 0.866], "out": 0.16, "outRamp": 0.35, "rootDepth": 0.09,
                                      "outline": [[0.0, -0.4], [-0.05, -0.7], [-0.08, -0.92], [0.0, -1.12], [0.12, -1.26], [0.3, -1.34], [0.55, -1.3], [0.75, -1.1],
                                                  [0.95, -0.92], [1.14, -0.73], [1.25, -0.5], [1.3, -0.25], [1.31, 0.0], [1.26, 0.2], [1.15, 0.38], [1.0, 0.52],
                                                  [0.8, 0.63], [0.58, 0.68], [0.36, 0.66], [0.16, 0.58], [0.02, 0.46]]},
                             # (2026-11-08: it read as a flat, plain cardboard disc -- now the skin's colour and its creased
                             #  `bark` (laid across the ear, as on the legs -- REMOVED the same day: it read as stripes, the trunk's
                             #  rings on the ear; plain skin as the body's), cupped deeper with its outer edge turned back
                             #  (curl < 0: away from the hollow), the rim blunt (edgeB) so it shows a thickness; held 16 cm off the shoulder
                             #  (was 6) and the fillet 4 cm (was 6): nearer, the fair's march found the upper arm across the
                             #  ear's lower middle and painted an oval of the arm's creases, in the arm's frame, on it)
                             thick=0.035, cup=0.3, curl=-0.12, curlAt=0.72, edgeB=4, color="@skin", inner="@earIn", innerRim=0.05, fairM=0.04,
                             about="The EARS (ears2.py): one huge fan each (sharp.js `fin`), the outline in metres in the old ear's plane -- the long lobe below, the rounded back edge -- its front edge rooted down the side of the head and faired, held just clear of the neck and shoulder; cupped, its outer edge turned back, the rim blunt; the skin's colour, plain as the body's (no `bark` creases: they read as stripes), the hollow (toward the body) pinker."),
    # ---------------------------------------------------------------- RODENTS, HARES, SMALL INSECTIVORES
    "mammals/hare": dict(ids=["ear", "earTip", "earIn"], outline=HARE, faceTo=[1, 0, 0.8], cup=0.6, color="@ear", inner="@earIn", innerRim=0.15,
                         tip="@earTip", tipAt=0.86, fair=0.3,
                         about="The EARS (ears2.py): very long round-tipped cupped sheets (sharp.js `fin`), pale in the hollow, the tips black; the roots faired."),
    "mammals/rat": dict(ids=["ear", "earBase", "earIn", "earCup"], noreach=["earBase"], outline=ROUND, faceTo=[1, 0, 0.6], cup=0.6, color="@ear", inner="@earIn",
                        innerRim=0.1, fair=0.3,
                        about="The EARS (ears2.py): round thin cupped sheets (sharp.js `fin`), near-naked and pink in the hollow; the roots faired."),
    "mammals/squirrel": dict(ids=["ear", "earTuft", "earIn"], noreach=["earTuft"], outline=CAT, faceTo=FO, cup=0.55, color="@ear", inner="@earIn", innerRim=0.18, fair=0.3,
                             # (2026-11-08 evening: the tuft a TASSEL of strands on the ear's upper rim -- it was one `tuftHorn` hair behind the ear)
                             tassel={"from": 0.6, "per": 8, "tipN": 12, "len": [0.25, 0.48], "fan": 32, "across": 18, "r": 0.00065, "color": "@ear", "tip": "@tuftE", "tipAt": 0.3, "coreLen": 0.3, "coreR": 0.35, "coreAspect": 0.55, "when": "tufts", "seed": 7},
                             about="The EARS (ears2.py): upright cupped sheets with round tips (sharp.js `fin`), pale in the hollow; the roots faired. The red squirrel's TUFTS (`tufts`; 2026-11-08 evening -- before, one thin horn standing up behind each ear): a BUSHY BRUSH of 31 hair strands an ear (horn `strand`s, the whiskers' kind) rooted ON the ear -- along both edges of its upper rim, over the tip, and densely on both faces round the tip -- fanning out ~30 degrees either way in the ear's plane and ~18 across it, of varied lengths, rising ~0.45 of the ear's length over the tip; a short fat `horn` core at the tip (the far mesh's dark tip); the ear's back colour darkening (`tuftE`) toward the ends. The grey squirrel has none."),
    "mammals/beaver": dict(ids=["ear"], outline=ROUND, faceTo=[1, 0, 0.6], cup=0.5, color="@ear", fair=0.3,
                           about="The EARS (ears2.py): small round cupped sheets (sharp.js `fin`) close to the head; the roots faired."),
    "mammals/capybara": dict(ids=["ear", "earIn"], outline=ROUND, faceTo=[1, 0, 0.6], cup=0.55, color="@ear", inner="@earIn", innerRim=0.15, fair=0.3,
                             about="The EARS (ears2.py): small round cupped sheets (sharp.js `fin`), darker in the hollow; the roots faired."),
    "mammals/porcupine": dict(ids=["ear"], outline=ROUND, faceTo=[1, 0, 0.6], cup=0.5, color="@ear", fair=0.3,
                              about="The EARS (ears2.py): small round cupped sheets (sharp.js `fin`) close to the head; the roots faired."),
    "mammals/pangolin": dict(ids=["ear"], outline=ROUND, faceTo=[1, 0, 0.6], cup=0.5, color="@face", fair=0.3,
                             about="The EARS (ears2.py): tiny round cupped sheets (sharp.js `fin`); the roots faired."),
    "mammals/anteater": dict(ids=["ear"], outline=ROUND, faceTo=[1, 0, 0.6], cup=0.5, color="@head", fair=0.3,
                             about="The EARS (ears2.py): small round cupped sheets (sharp.js `fin`); the roots faired."),
    # ---------------------------------------------------------------- PRIMATES (a shell close to the head, the hollow out and forward)
    "mammals/gorilla": dict(ids=["ear"], flat=True, rootK=0.75, L=[-1, 0, 0.45], W=[0, 1, 0], face=[0.3, 0, 1], outline=SHELL, cup=0.45,
                            color="@face", inner="@skin", innerRim=0.3, fair=0.3,
                            about="The EARS (ears2.py): small flat shells close to the head (sharp.js `fin`), rooted along their front edge, the hollow out and forward, its fold (the helix) a band of the outer colour; the roots faired."),
    "mammals/orangutan": dict(ids=["ear"], flat=True, rootK=0.75, L=[-1, 0, 0.45], W=[0, 1, 0], face=[0.3, 0, 1], outline=SHELL, cup=0.45,
                              color="@face", inner="@skin", innerRim=0.3, fair=0.3,
                              about="The EARS (ears2.py): small flat shells close to the head (sharp.js `fin`), rooted along their front edge, the hollow out and forward, its fold (the helix) a band of the outer colour; the roots faired."),
    "mammals/baboon": dict(ids=["ear"], flat=True, rootK=0.75, L=[-1, 0, 0.45], W=[0, 1, 0], face=[0.3, 0, 1], outline=CAT, cup=0.45,
                           color="@face", inner="@skin", innerRim=0.3, fair=0.3,
                           about="The EARS (ears2.py): small flat shells with a point at the top (sharp.js `fin`), close to the head, the hollow out and forward; the roots faired."),
    "mammals/lemur": dict(ids=["ear", "earIn", "earB"], noreach=["earB"], outline=CAT, faceTo=FO, cup=0.5, color="@ear", inner="@earIn", innerRim=0.2, fair=0.3,
                          about="The EARS (ears2.py): furry upright cupped sheets (sharp.js `fin`), round-pointed, paler in the hollow; the roots faired."),
    # ---------------------------------------------------------------- BAT
    "mammals/bat": dict(ids=["ear", "earIn"], outline=BAT, faceTo=[1, 0, 0.5], cup=0.6, color="@ear", inner="@earIn", innerRim=0.1, fair=0.3,
                        pat="ridges", patFace="face", ribs=0.09,
                        about="The EARS (ears2.py): big tall cupped sheets (sharp.js `fin`), broad below, round-tipped, the hollow ribbed across (the `ridges` pattern laid in the ear's own frame); the roots faired."),
}

FAMILY = {
    "canids": ["mammals/dog", "mammals/wolf", "mammals/fox", "mammals/hyena", "mammals/redpanda", "mammals/badger", "mammals/skunk", "mammals/weasel",
               "mammals/giantpanda", "mammals/bear"],
    "equids": ["mammals/horse", "monsters/pegasus", "monsters/unicorn"],
    "ungulates": ["mammals/cow", "mammals/ox", "mammals/deer", "mammals/reindeer", "mammals/impala", "mammals/oryx", "mammals/chamois", "mammals/cervicapra",
                  "mammals/ram", "mammals/sheep", "mammals/camel", "mammals/bactrian"],
    "bigheads": ["mammals/pig", "mammals/hippo", "mammals/rhinoceros", "mammals/elephant"],
    "rodents": ["mammals/hare", "mammals/rat", "mammals/squirrel", "mammals/beaver", "mammals/capybara", "mammals/porcupine", "mammals/anteater"],   # (the pangolin's ear is a slit with a rim of skin, sunk in the head: left a field bump)
    "primates": ["mammals/gorilla", "mammals/orangutan", "mammals/baboon", "mammals/lemur"],
    "bats": ["mammals/bat"],
    "felids": ["mammals/cat", "mammals/lynx", "mammals/leopard", "mammals/lion", "mammals/tiger", "mammals/smilodon", "monsters/manticore"],
}
