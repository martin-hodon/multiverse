#!/usr/bin/env python3
"""MODERN CLOTHES (2026-11-20; docs/clothes.md): the garments of the twentieth and twenty-first centuries, written in the
tailor's own language -- flat pieces laid round the body (clothes.js) -- not as items. Run: python3 tools/modern/clothesgen.py

It writes
  assets/clothes/<garment>.json            jeans, the t-shirt, the hoodie, the suit (jacket, trousers, shirt, tie), a
                                           day dress, a skirt, the puffer, the trench coat, sneakers, the baseball cap,
                                           the beanie, the polo, shorts, the sweater, the hi-vis vest, the hard hat,
                                           work boots
  assets/clothes/components/<name>.json    two new components: `collar` (a stand or turned-down collar round the neck,
                                           a hang from just above the collar point) and `peak` (a cap's bill or a helmet's
                                           rim: a brim disc set forward and tilted)
  assets/patterns/palettes.json            the modern dyes (denim, khaki, navy, hi-vis yellow...: added, never removed)
  assets/clothes/wardrobe.json             the garments registered (`garments`, which is what the tailor loads), the
                                           `modern` style (by kind, outfits by weight, its hair) and three named
                                           outfits: office-worker, casual, construction-worker
  assets/index.json                        the garments under "Clothes", the components under "Garment components"
                                           (under the fcntl lock on assets/index.json.lock: other generators write it too)

THE LAYERS the modern dress is worn in (outermost wins where two cover a point, clothes.js tailor): a dress shirt or a
blouse is TUCKED (0) under the trousers and the skirt (1-2); a t-shirt, a polo is worn OUT over the jeans (2); a sweater,
a hoodie, the suit jacket over those (3); the puffer (4); the trench coat and the hi-vis vest outside everything (5). Shoes
are 0, so the trousers' hem lies over the shaft of a boot.
"""
import fcntl, json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
CLOTHES = os.path.join(ROOT, "assets", "clothes")

# ---- the dyes (assets/patterns/palettes.json: four slots -- the dye, a second thread, an accent, a dark) -------------
PALETTES = {
    "denim":          ["#3a5680", "#263d61", "#7f97b8", "#16233a"],   # (indigo warp, the twill's dark rib)
    "denim-light":    ["#6f8db3", "#56739a", "#a9bdd6", "#2f4563"],   # (stone-washed)
    "denim-black":    ["#3a3c42", "#2a2c31", "#5a5d64", "#131417"],
    "khaki":          ["#b9a57c", "#a08c63", "#d3c39f", "#5f5236"],   # (chinos, cargo shorts)
    "navy":           ["#1f2a44", "#172036", "#3a4a6e", "#0b101c"],
    "charcoal":       ["#3b3e44", "#2d3035", "#6c7078", "#16181b"],
    "suit-grey":      ["#6c7078", "#565a61", "#9da2aa", "#2e3135"],
    "cotton-white":   ["#eceef0", "#dadee3", "#ffffff", "#a4abb3"],
    "shirt-blue":     ["#b7cde4", "#a0b9d6", "#dce8f4", "#6c839f"],
    "heather-grey":   ["#9a9ca0", "#86888c", "#b8babd", "#4e5054"],
    "tee-red":        ["#b3262e", "#981d24", "#d4565c", "#4e0b0f"],
    "tee-green":      ["#3f6b46", "#335a3a", "#6a9470", "#18301c"],
    "mustard":        ["#c9a227", "#ad8a1c", "#e2c45e", "#5e4a0a"],
    "teal":           ["#2f7f86", "#246970", "#5fa8ae", "#0f3639"],
    "burgundy":       ["#6e1f2f", "#5a1826", "#913a4c", "#2c0a11"],
    "olive":          ["#5a6338", "#4a522d", "#7d8756", "#262a16"],
    "rose":           ["#d98ca0", "#c5768b", "#efb6c4", "#7a3a4a"],
    "hivis-yellow":   ["#d4ee12", "#bcd40c", "#eef87a", "#6b7a06"],
    "hivis-orange":   ["#ff6a12", "#e55a08", "#ffa060", "#7a2e04"],
    "reflective":     ["#c9cdd3", "#b0b5bc", "#eef0f3", "#70757c"],
    "hardhat-yellow": ["#f2c418", "#d9ab0c", "#ffe070", "#7a5c04"],
    "hardhat-white":  ["#eeece6", "#d8d6d0", "#ffffff", "#8e8c86"],
    "trench":         ["#b39a6b", "#9c845a", "#cbb68a", "#5e4e32"],
    "camel":          ["#a87d4f", "#906a42", "#c49c6e", "#5a3f22"],
    "sneaker-white":  ["#f0f0ec", "#dcdcd6", "#ffffff", "#9a9a94"],
    "leather-tan":    ["#8a5a2b", "#734a22", "#b07a44", "#3e2610"],
    "rubber":         ["#2b2b2b", "#202020", "#444444", "#0c0c0c"],
}


def cloth(pattern, palette):
    return {"pattern": "fabrics/" + pattern, "palette": palette}


def use(component, **params):
    return {"use": "clothes/components/" + component, "params": params} if params else {"use": "clothes/components/" + component}


def garment(name, title, layer, about, fabrics, uses=(), pieces=(), params=None, **flags):
    d = {"name": title, "kind": "garment", "layer": layer, "_about": about}
    d.update(flags)   # (head, feet, skirted, thick, hair)
    d["fabrics"] = fabrics
    if params: d["params"] = params
    if uses: d["use"] = list(uses)
    if pieces: d["pieces"] = list(pieces)   # (a garment's own pieces, beside its components': clothes.js piecesOf walks both)
    return name, d


# ---- the new components -----------------------------------------------------------------------------------------
COMPONENTS = {
    "collar": {
        "name": "Collar", "kind": "component",
        "_about": "A COLLAR round the neck: a short cone HUNG from `height` metres above the collar point down to just "
                  "under it, its ring the neck's own (`fromRadius` 0: the tailor takes the neck's radius and its ease), "
                  "flaring out by `flare` a metre -- a shirt's turned-down collar, a polo's, a coat's stand collar zipped "
                  "up (flare low), a trench coat's turned out (flare high). Open at the front over `gap` degrees. Stiff: "
                  "no folds, no sway.",
        "params": {"height": 0.04, "drop": 0.012, "flare": 0.8, "gap": 30, "fabric": "main"},
        "pieces": [{"name": "collar", "kind": "hang", "on": "torso", "from": "collar - height", "to": "collar + drop",
                    "fromRadius": 0, "flare": "flare", "wrap": [180, "360 - gap"], "fabric": "main",
                    "pleats": 0, "swing": False, "lid": False, "open": True}],
    },
    "peak": {
        "name": "Peak", "kind": "component",
        "_about": "A PEAK: a stiff bill or rim -- a disc (clothes.js `brim`) of `radius` cranium radii centred `forward` "
                  "of the head's middle at `at` high, tilted down at the front (its axis [-.18, -1, 0]: clothes.js takes a brim's axis as"
                  " written, not as an expression -- a level rim is a piece of its own); its "
                  "back half lies inside the crown it is sewn to, so only the bill shows: a baseball cap's, a hard "
                  "hat's rim.",
        "params": {"forward": 0.85, "at": 0.42, "radius": 0.95, "thick": 0.06},
        "pieces": [{"name": "peak", "kind": "brim", "centre": ["forward", "at"], "axis": [-0.18, -1, 0],
                    "radius": "radius", "thickness": "thick", "fabric": "peak"}],
    },
}

# (patch and band: one worn sheet on the torso, closed or open over an arc, a neckline cut from it if it says -- in the
#  garment's main cloth or its trim; what a garment sews ON, used after the body it lies on)
for _name, _slot, _what in (("patch", "main", "in the garment's own cloth: a pocket, a waistband, a welt, a rib, a lapel"),
                            ("band", "trim", "in its TRIM cloth: reflective tape, a drawcord, a pocket square, a zip")):
    COMPONENTS[_name] = {
        "name": _name.capitalize(), "kind": "component",
        "_about": f"A {_name.upper()} sewn on the torso {_what} -- from `from` to `to`, closed round it or (`open`) over "
                  "`span` degrees about `centre` (0 the front, 90 the left), `thick` standing proud; a `neckline` cut "
                  "from it when it says (a rib round the collar). Used AFTER the body it lies on: a garment's own pieces "
                  "lie under its components' (clothes.js piecesOf lists them first).",
        "params": {"from": "waist", "to": "hip", "open": False, "centre": 0, "span": 360, "thick": 0.004,
                   "neckline": "none", "neckFront": 0, "neckBack": 0, "neckWidth": 60, "pleats": 0},
        "pieces": [{"name": _name, "unless": "open", "on": "torso", "from": "from", "to": "to", "fabric": _slot, "thick": "thick", "pleats": "pleats",
                    "opening": {"neckline": "neckline", "front": "neckFront", "back": "neckBack", "width": "neckWidth"}},
                   {"name": _name, "if": "open", "on": "torso", "from": "from", "to": "to", "wrap": ["centre", "span"], "fabric": _slot,
                    "thick": "thick", "pleats": "pleats", "opening": {"neckline": "neckline", "front": "neckFront", "back": "neckBack", "width": "neckWidth"}}]}

# ---- the garments -------------------------------------------------------------------------------------------------
# (a garment's OWN `pieces` lie UNDER its components' -- clothes.js piecesOf lists them first, and a later piece lies over
#  an earlier one -- so whatever is sewn ON a garment, a pocket, a waistband, reflective tape, is a `patch` or a `band`
#  used after the body it lies on; the lapels go before the jacket's body, so its V shows them)
def patch(frm, to, centre=None, span=None, thick=0.004, neck=None, trim=False, pleats=0):
    """a worn sheet sewn on the torso (components/patch, in the garment's main cloth; components/band, in its trim):
    closed round it, or over `span` degrees about `centre` (0 the front, 90 the left); `neck`: a neckline cut from it."""
    p = {"from": frm, "to": to, "thick": thick, **({"pleats": pleats} if pleats else {})}
    if span is not None: p.update(open=True, centre=centre or 0, span=span)
    if neck: p.update(neckline=neck[0], neckFront=neck[1], neckBack=neck[2], **({"neckWidth": neck[3]} if len(neck) > 3 else {}))
    return use("band" if trim else "patch", **p)


WAIST = lambda thick: patch("waist - 0.005", "waist + 0.035", thick=thick)   # (a trouser's waistband)
# (a short sleeve's MOUTH: a plain cone standing a little off the upper arm -- the bell-sleeve component folds nine
#  times round and read as a ruffle; a t-shirt's is unpleated jersey)
MOUTH = lambda to: {"name": "mouth", "kind": "hang", "on": "arm", "from": "biceps - 0.075", "to": to, "flare": 0.08, "fabric": "main", "pleats": 0}
G = dict([
    garment("jeans", "Jeans", 1,
            "blue jeans (Levi Strauss & Jacob Davis, 1873; everyone's trousers from the 1950s): heavy cotton denim, a "
            "3/1 twill of indigo warp over white weft, five pockets, from the waist to the instep, a little loose, "
            "its waistband standing proud (the seat's patch pockets are left out: the figure engine reads six layers a "
            "part, and a hi-vis vest over a t-shirt over the jeans' seat spends them all)",
            {"main": cloth("twill", "denim")},
            uses=[use("hose", **{"from": "waist", "to": "ankle + 0.015", "feet": False}), WAIST(0.008)],
            thick=0.005, wear=0),
    garment("shorts", "Shorts", 1,
            "shorts: cotton chino or cargo shorts from the waist to above the knee (a hand above it) -- summer's and "
            "the child's",
            {"main": cloth("twill", "khaki")},
            uses=[use("hose", **{"from": "waist", "to": "knee - 0.07", "feet": False}), WAIST(0.007)],
            thick=0.005, wear=0),
    garment("suit-trousers", "Suit trousers", 1,
            "the lounge suit's trousers (worsted wool, 1900s on): from the natural waist straight to the instep, a "
            "crease down the front and a break over the shoe; chinos in khaki cotton cut the same",
            {"main": cloth("plain", "charcoal")},
            uses=[use("hose", **{"from": "waist", "to": "ankle + 0.025", "feet": False}), WAIST(0.006)],
            thick=0.004, wear=0),
    garment("t-shirt", "T-shirt", 2,
            "the t-shirt (the US Navy's undershirt of 1913, outerwear from the 1950s): cotton jersey, a ribbed crew "
            "neck, short sleeves to mid upper arm standing a little off it, to the hips and worn out over the trousers "
            "(on its own: a sweater or a hoodie is worn instead of it, its sleeves' mouths would stand out through theirs)",
            {"main": cloth("plain", "cotton-white")},
            uses=[use("bodice", **{"to": "hip + 0.035", "neckline": "round", "neckFront": 0.018, "neckBack": 0.004}),
                  use("sleeve", to="biceps - 0.05"),
                  patch("collar - 0.01", "collar + 0.012", thick=0.005, neck=("round", 0.012, 0.0))],
            pieces=[MOUTH("biceps + 0.03")],
            thick=0.003, wear=0),
    garment("polo-shirt", "Polo shirt", 2,
            "the polo shirt (René Lacoste's tennis shirt, 1926): cotton piqué, a soft turned-down collar over a "
            "buttoned placket of two or three buttons, short sleeves with ribbed bands, worn out over the trousers",
            {"main": cloth("plain", "navy")},
            uses=[use("bodice", **{"to": "hip + 0.03", "neckline": "v", "neckFront": 0.075, "neckBack": 0.004, "neckWidth": 9}),
                  use("sleeve", to="biceps - 0.05"),
                  use("collar", height=0.028, drop=0.015, flare=0.6, gap=22)],
            pieces=[MOUTH("biceps + 0.02")],
            thick=0.0035, wear=0),
    garment("dress-shirt", "Dress shirt", 0,
            "the dress shirt (the collar sewn on from the 1920s): white or pale blue cotton poplin, a turned-down collar "
            "on a stand, buttoned all down the front, long sleeves with buttoned cuffs, TUCKED into the trousers or the "
            "skirt (layer 0) -- worn open at the throat, or closed under a tie; a woman's blouse is cut the same",
            {"main": cloth("plain", "cotton-white")},
            uses=[use("bodice", **{"to": "hip + 0.06", "neckline": "v", "neckFront": 0.035, "neckBack": 0.002, "neckWidth": 14}),
                  use("sleeve", to="wrist + 0.012"),
                  use("collar", height=0.032, drop=0.02, flare=1.0, gap=26)],
            thick=0.0025, wear=0),
    garment("tie", "Necktie", 1,
            "the necktie (the four-in-hand, from the 1880s): a silk blade knotted under the shirt's collar, about 8 cm "
            "wide at its tip, to the belt -- over the shirt, under the jacket, its knot the narrow top",
            {"main": cloth("plain", "silk-red")},
            pieces=[{"name": "knot", "on": "torso", "from": "collar - 0.01", "to": "collar + 0.03", "wrap": [0, 15], "fabric": "main", "thick": 0.009},
                    {"name": "blade", "on": "torso", "from": "collar + 0.03", "to": "waist - 0.02", "wrap": [0, 21], "fabric": "main", "thick": 0.004}],
            wear=0),
    garment("sweater", "Sweater", 3,
            "a knitted sweater (the jumper, the pullover): wool or cotton jersey, a crew neck, long sleeves, to the hips, "
            "its welt and cuffs ribbed tight",
            {"main": cloth("plain", "heather-grey")},
            uses=[use("bodice", **{"to": "hip + 0.04", "neckline": "round", "neckFront": 0.012, "neckBack": 0.004}),
                  use("sleeve", to="wrist + 0.01"),
                  patch("hip - 0.01", "hip + 0.04", thick=0.009),
                  patch("collar - 0.012", "collar + 0.014", thick=0.009, neck=("round", 0.0, 0.0))],
            thick=0.006, wear=0),
    garment("hoodie", "Hoodie", 3,
            "the hooded sweatshirt (Champion, 1930s; everyone's from the 1980s): cotton fleece, the hood down on the "
            "back in a thick double fold, its drawcords at the throat, a kangaroo pocket across the belly, ribbed welt",
            {"main": cloth("plain", "heather-grey"), "trim": cloth("plain", "cotton-white")},
            uses=[use("bodice", **{"to": "hip + 0.05", "neckline": "v", "neckFront": 0.05, "neckBack": 0.01, "neckWidth": 20}),
                  use("sleeve", to="wrist + 0.01"),
                  patch("hip", "hip + 0.05", thick=0.011),
                  patch("waist - 0.03", "hip - 0.005", 0, 96, 0.011),
                  patch("collar - 0.015", "armpit - 0.05", 180, 176, 0.032, pleats=9),
                  patch("armpit - 0.05", "armpit + 0.03", 180, 92, 0.032, pleats=5),
                  patch("collar - 0.015", "collar + 0.02", thick=0.016, neck=("v", 0.05, 0.01)),
                  patch("collar + 0.0", "armpit - 0.02", 10, 3, 0.012, trim=True),
                  patch("collar + 0.0", "armpit - 0.04", -10, 3, 0.012, trim=True)],
            thick=0.007, wear=0),
    garment("suit-jacket", "Suit jacket", 3,
            "the lounge-suit jacket (the sack coat of the 1860s, the office's from the 1920s): worsted wool, single "
            "breasted, buttoned at the waist, its lapels rolled back in a deep V over the shirt and tie, sleeves to the "
            "wrist bone (the shirt's cuff showing), to the top of the seat (a worn sheet: hung below the hips it "
            "had to clear the thighs and stood out a box), a white pocket square at the breast",
            {"main": cloth("plain", "charcoal"), "trim": cloth("plain", "cotton-white")},
            params={"length": "hip + 0.035"},
            uses=[patch("collar - 0.01", "waist", 0, 120, 0.009, neck=("v", 0.23, 0.0, 15)),
                  use("bodice", **{"to": "length", "neckline": "v", "neckFront": 0.24, "neckBack": 0.004, "neckWidth": 30}),
                  use("sleeve", to="wrist - 0.015"),
                  patch("armpit - 0.02", "armpit + 0.004", 32, 11, 0.012, trim=True)],
            thick=0.005, wear=0),
    garment("puffer-jacket", "Puffer jacket", 4,
            "the puffer (down) jacket (Eddie Bauer, 1936; a city coat from the 1980s): nylon shell quilted in horizontal "
            "baffles filled with down, a zip up the front to a stand collar, to the hips, its sleeves puffed to the wrist",
            {"main": cloth("hoops", "navy"), "trim": cloth("plain", "rubber")},
            uses=[use("bodice", **{"to": "hip + 0.05", "neckline": "round", "neckFront": 0.004, "neckBack": 0.0}),
                  use("sleeve", to="wrist + 0.005"),
                  use("collar", height=0.06, drop=0.01, flare=0.35, gap=0),
                  patch("collar", "hip + 0.05", 0, 2.5, 0.024, trim=True)],
            thick=0.02, wear=0),
    garment("trench-coat", "Trench coat", 5,
            "the trench coat (Burberry's and Aquascutum's for the officers of 1914-18; a city coat since): khaki cotton "
            "gabardine, double-breasted to the waist, a wide collar turned out, a belt of its own cloth, and skirts to "
            "below the knee open at the front -- the overcoat, in charcoal or camel wool, is cut the same",
            {"main": cloth("twill", "trench"), "buckle": cloth("buckle", "brass")},
            params={"length": "knee + 0.08"},
            uses=[use("bodice", **{"to": "waist + 0.03", "neckline": "v", "neckFront": 0.16, "neckBack": 0.004, "neckWidth": 30}),
                  use("sleeve", to="wrist + 0.01"),
                  use("collar", height=0.05, drop=0.035, flare=1.4, gap=70),
                  use("belt", at="waist + 0.01", width=0.045)],
            pieces=[{"name": "skirts", "kind": "hang", "on": "torso", "from": "waist + 0.02", "to": "length", "flare": 0.16, "fit": "flare",
                     "wrap": [180, 338], "fabric": "main", "pleats": 6, "cling": 0.35, "trail": 8, "lid": False}],
            thick=0.006, wear=0),
    garment("hi-vis-vest", "Hi-vis vest", 5,
            "the high-visibility vest (EN ISO 20471): fluorescent yellow or orange polyester mesh, sleeveless, open "
            "in a V, two bands of retro-reflective tape round the body and two braces of it up the front (the back's braces are "
            "left out: six layers a part, and the vest is worn over a shirt over the jeans)",
            {"main": cloth("plain", "hivis-yellow"), "trim": cloth("plain", "reflective")},
            uses=[use("bodice", **{"to": "hip + 0.02", "neckline": "v", "neckFront": 0.15, "neckBack": 0.01, "neckWidth": 34}),
                  patch("armpit + 0.10", "armpit + 0.15", thick=0.006, trim=True),
                  patch("waist + 0.06", "waist + 0.11", thick=0.006, trim=True),
                  patch("collar + 0.03", "armpit + 0.10", 46, 13, 0.006, trim=True),
                  patch("collar + 0.03", "armpit + 0.10", -46, 13, 0.006, trim=True)],
            thick=0.004, wear=0),
    garment("day-dress", "Day dress", 2,
            "a modern day dress (the shirtwaist and the sheath of the 1950s on): a fitted bodice, a V neck, short "
            "sleeves, and a skirt from the natural waist to the knee, a little flared and falling onto the legs",
            {"main": cloth("plain", "teal"), "trim": cloth("plain", "teal")},
            params={"length": "knee + 0.03", "sleeves": "biceps - 0.03"},
            uses=[use("bodice", **{"to": "waist + 0.01", "neckline": "v", "neckFront": 0.1, "neckBack": 0.01, "neckWidth": 34}),
                  use("sleeve", to="sleeves"),
                  use("skirt", **{"from": "waist", "to": "length", "flare": 0.28, "pleats": 7, "cling": 0.5})],
            skirted=True, thick=0.003, wear=0),
    garment("a-line-skirt", "A-line skirt", 2,
            "an A-line skirt (Dior's line of 1955, everyone's since the 1960s): from the natural waist to the knee, "
            "flaring evenly, a narrow waistband -- worn with a blouse tucked in",
            {"main": cloth("plain", "navy")},
            params={"length": "knee + 0.02"},
            uses=[use("skirt", **{"from": "waist", "to": "length", "flare": 0.2, "pleats": 6, "cling": 0.5}),
                  patch("waist - 0.03", "waist + 0.005", thick=0.006)],
            skirted=True, thick=0.004, wear=0),
    garment("sneakers", "Sneakers", 0,
            "sneakers (trainers; Converse 1917, the running shoe from the 1970s): a canvas or leather upper on a thick "
            "rubber sole, laced, a padded collar round the ankle",
            {"main": cloth("leather", "sneaker-white"), "trim": cloth("plain", "sneaker-white")},
            uses=[use("shoes", boot=True, to="ankle - 0.025")],
            feet=True, thick=0.011, wear=0),
    garment("work-boots", "Work boots", 0,
            "work boots: laced leather boots to a hand above the ankle, a steel toecap under a thick lugged sole -- "
            "worn under the trousers' hem",
            {"main": cloth("leather", "leather-tan"), "trim": cloth("leather", "leather-dark")},
            uses=[use("shoes", boot=True, to="ankle - 0.12")],
            feet=True, thick=0.009),
    garment("baseball-cap", "Baseball cap", 6,
            "the baseball cap (the Brooklyn style of 1860, everyone's from the 1980s): a crown of six cotton panels "
            "close over the skull and a stiff curved bill over the eyes",
            {"main": cloth("plain", "navy"), "peak": cloth("plain", "navy")},
            uses=[use("cap", radius=1.16, brow=0.36),
                  use("peak", forward=0.95, at=0.38, radius=0.95, thick=0.05)],
            head=True, wear=0),
    garment("beanie", "Beanie", 6,
            "the knitted beanie (the watch cap): rib-knit wool pulled down over the skull to the top of the ears",
            {"main": cloth("plain", "burgundy")},
            uses=[use("cap", radius=1.2, brow=0.26)],
            head=True, thick=0.006, wear=0),
    garment("hard-hat", "Hard hat", 7,
            "the safety helmet (the hard hat: E. W. Bullard, 1919; HDPE since the 1950s): a domed shell raised off the "
            "head on its harness, a ridge fore and aft, a short peak over the brow and a narrow rim round it",
            {"main": cloth("plain", "hardhat-yellow"), "peak": cloth("plain", "hardhat-yellow"), "plume": cloth("plain", "hardhat-yellow")},
            uses=[use("cap", radius=1.3, brow=0.55),
                  use("crest", rise=0.55, back=-0.18, radius=0.98, thick=0.09)],
            pieces=[{"name": "rim", "kind": "brim", "centre": [0.18, 0.5], "axis": [-0.06, -1, 0], "radius": 1.42, "thickness": 0.07, "fabric": "peak"}],
            head=True, wear=0),
])

# ---- the wardrobe: the modern style (a top is ONE of the t-shirt, the polo, the sweater, the hoodie: a short sleeve's
# standing mouth would come out through a knit's sleeve over it) -------------------------------------------------------------------------------
TOPS_TEE = ["plain:cotton-white", "plain:black", "plain:heather-grey", "plain:navy", "plain:tee-red", "plain:tee-green", "plain:mustard", "plain:teal", "hoops:navy"]
KNIT = ["plain:heather-grey", "plain:navy", "plain:burgundy", "plain:olive", "plain:camel", "plain:charcoal", "lozenge:wool-white", "plain:mustard"]
JEANS = ["twill:denim", "twill:denim", "twill:denim-light", "twill:denim-black"]
CHINOS = ["twill:khaki", "twill:olive", "twill:navy", "plain:charcoal"]
SUIT = ["plain:charcoal", "plain:navy", "plain:suit-grey", "pinstripe:navy", "pinstripe:charcoal", "twill:suit-grey", "plain:black"]
SHIRT = ["plain:cotton-white", "plain:cotton-white", "plain:shirt-blue", "pinstripe:shirt-blue", "checks:shirt-blue"]
TIES = ["plain:silk-red", "plain:navy", "plain:burgundy", "stripes:stripe-madder", "dots:navy", "plain:silk-black", "damask:damask-blue"]
PUFFER = ["hoops:navy", "hoops:black", "hoops:tee-red", "hoops:olive", "hoops:mustard"]
COATS = ["twill:trench", "twill:trench", "plain:camel", "plain:charcoal", "plain:navy"]
CAPS = ["plain:navy", "plain:black", "plain:tee-red", "plain:cotton-white", "plain:khaki", "plain:tee-green"]
BEANIES = ["plain:burgundy", "plain:charcoal", "plain:navy", "plain:mustard", "plain:olive"]
DRESSES = ["plain:teal", "plain:navy", "plain:burgundy", "dots:navy", "plain:rose", "checks:tee-red", "plain:black", "plain:mustard"]
SKIRTS = ["plain:navy", "plain:charcoal", "plain:black", "plain:camel", "checks:check-russet", "plain:burgundy", "twill:denim"]
SNEAKERS = ["leather:sneaker-white", "leather:sneaker-white", "plain:black", "plain:navy", "plain:tee-red"]
OFFICE_SHOES = ["leather:leather-dark", "plain:black", "leather:black"]


def w(garment_, p=1, **fabrics):
    e = {"garment": garment_, "p": p}
    params = fabrics.pop("params", None)
    layer = fabrics.pop("layer", None)
    if fabrics: e["fabrics"] = fabrics
    if params: e["params"] = params
    if layer is not None: e["layer"] = layer
    return e


MODERN = {
    "_about": "the twentieth and twenty-first centuries (tools/modern/clothesgen.py): the office's suit, shirt and tie, "
              "jeans and a t-shirt, the hoodie, the puffer and the trench coat, the day dress and the skirt, sneakers, "
              "the baseball cap and the beanie; the worker's hi-vis vest and hard hat",
    "man": [
        {"name": "office", "weight": 2, "wear": [
            w("dress-shirt", main=SHIRT), w("suit-trousers", main=SUIT), w("tie", .6, main=TIES),
            w("suit-jacket", .75, main=SUIT), w("shoes", main=OFFICE_SHOES),
            w("trench-coat", .15, main=COATS)]},
        {"name": "casual", "weight": 4, "wear": [
            w(["t-shirt", "t-shirt", "t-shirt", "polo-shirt", "sweater", "hoodie"], main=TOPS_TEE + KNIT), w(["jeans", "jeans", "suit-trousers", "shorts"], main=JEANS + CHINOS[:2]),
            w("puffer-jacket", .12, main=PUFFER),
            w("sneakers", main=SNEAKERS), w(["baseball-cap", "baseball-cap", "beanie"], .25, main=CAPS)]},
        {"name": "worker", "weight": 2, "work": True, "wear": [
            w(["t-shirt", "t-shirt", "sweater"], main=["plain:heather-grey", "plain:navy", "plain:black", "plain:olive", "plain:cotton-white"]),
            w(["jeans", "suit-trousers"], main=["twill:denim", "twill:khaki", "twill:navy", "twill:olive", "plain:charcoal"]),
            w("hi-vis-vest", .8, main=["plain:hivis-yellow", "plain:hivis-yellow", "plain:hivis-orange"]),
            w("work-boots"), w("hard-hat", .7, main=["plain:hardhat-yellow", "plain:hardhat-white", "plain:hivis-orange"])]},
    ],
    "woman": [
        {"name": "office", "weight": 2, "wear": [
            w("dress-shirt", main=SHIRT + ["plain:rose"]), w(["a-line-skirt", "suit-trousers"], main=SUIT + ["plain:camel"]),
            w("suit-jacket", .6, main=SUIT), w("shoes", main=OFFICE_SHOES), w("trench-coat", .2, main=COATS)]},
        {"name": "dress", "weight": 2, "wear": [
            w("day-dress", main=DRESSES), w(["shoes", "sneakers"], main=OFFICE_SHOES), w("trench-coat", .15, main=COATS)]},
        {"name": "casual", "weight": 4, "wear": [
            w(["t-shirt", "t-shirt", "t-shirt", "polo-shirt", "sweater", "hoodie"], main=TOPS_TEE + KNIT + ["plain:rose"]), w(["jeans", "jeans", "a-line-skirt", "shorts"], main=JEANS),
            w("puffer-jacket", .12, main=PUFFER),
            w("sneakers", main=SNEAKERS), w("beanie", .1, main=BEANIES)]},
    ],
    "boy": [{"name": "child", "weight": 1, "wear": [
        w(["t-shirt", "t-shirt", "polo-shirt", "hoodie"], main=TOPS_TEE + ["plain:tee-red"]), w(["jeans", "shorts", "shorts"], main=JEANS + ["twill:khaki", "twill:navy"]),
        w("sneakers", main=SNEAKERS), w("baseball-cap", .3, main=CAPS)]}],
    "girl": [
        {"name": "child", "weight": 2, "wear": [
            w(["t-shirt", "t-shirt", "sweater", "hoodie"], main=TOPS_TEE + ["plain:rose"]), w(["jeans", "a-line-skirt", "shorts"], main=JEANS + ["plain:rose", "checks:tee-red"]),
            w("sneakers", main=SNEAKERS)]},
        {"name": "dress", "weight": 1, "wear": [w("day-dress", main=DRESSES), w("sneakers", main=SNEAKERS)]}],
    "hair": {"man": ["short", "short", "crop", "curly", "spiky-up", "crop"], "woman": ["ponytail", "bob", "long", "shoulder", "bun", "long-wavy"]},
}
NAMED = {
    "office-worker": {"_about": "an office worker of today: a white shirt and a tie, the suit's trousers and jacket in charcoal, black shoes",
                      "wear": [w("dress-shirt", main=["plain:cotton-white"]), w("suit-trousers", main=["plain:charcoal"]), w("tie", main=["plain:silk-red"]),
                               w("suit-jacket", main=["plain:charcoal"]), w("shoes", main=["leather:black"])]},
    "casual": {"_about": "casual dress of today: a grey hoodie over blue jeans, white sneakers, a baseball cap",
               "wear": [w("jeans", main=["twill:denim"]), w("hoodie", main=["plain:heather-grey"]),
                        w("sneakers", main=["leather:sneaker-white"]), w("baseball-cap", main=["plain:navy"])]},
    "construction-worker": {"_about": "a construction worker: a t-shirt, jeans, the hi-vis vest, laced work boots and a yellow hard hat",
                            "wear": [w("t-shirt", main=["plain:heather-grey"]), w("jeans", main=["twill:denim"]), w("hi-vis-vest", main=["plain:hivis-yellow"]),
                                     w("work-boots"), w("hard-hat", main=["plain:hardhat-yellow"])]},
}
for o in NAMED.values():
    for e in o["wear"]: e.pop("p", None)


def dump(path, doc, indent=2):
    with open(path, "w") as f:
        json.dump(doc, f, indent=indent, ensure_ascii=False)
        f.write("\n")


def main():
    for name, d in COMPONENTS.items(): dump(os.path.join(CLOTHES, "components", name + ".json"), d)
    for name, d in G.items(): dump(os.path.join(CLOTHES, name + ".json"), d)
    # (the dyes: added or updated, never removed)
    pp = os.path.join(ROOT, "assets", "patterns", "palettes.json")
    # (the file is hand-formatted -- a dye a line -- so the new ones are put in as text before its closing braces, a line
    #  each, and one already there is written over in place: re-dumping it whole would reformat every dye in it)
    text, have = open(pp).read(), json.load(open(pp))["palettes"]
    for k, v in PALETTES.items():
        line = f'  "{k}": {json.dumps(v)}'
        if k in have:
            start = text.index(f'\n  "{k}": ') + 1
            end = text.index("]", start) + 1
            text = text[:start] + line + text[end:]
        else:
            cut = text.rstrip().rindex("}", 0, len(text.rstrip()) - 1)   # (the palettes' own closing brace)
            body = text[:cut].rstrip()
            text = body + ",\n" + line + "\n " + text[cut:]
    json.loads(text)   # (still json)
    open(pp, "w").write(text)
    # (the wardrobe: the garments it loads, the style, the named outfits)
    wp = os.path.join(CLOTHES, "wardrobe.json")
    wd = json.load(open(wp))
    for name in G: wd["garments"][name] = True
    wd["styles"]["modern"] = MODERN
    wd["outfits"].update(NAMED)
    dump(wp, wd, indent=1 if open(wp).read(40).count("\n  ") == 0 else 2)
    # (the catalogue, under the lock every generator takes)
    p = os.path.join(ROOT, "assets", "index.json")
    lock = open(p + ".lock", "w"); fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        idx = json.load(open(p))
        cats = {c["name"]: c for c in idx["categories"]}
        for cat, paths in (("Clothes", ["clothes/" + n for n in G]), ("Garment components", ["clothes/components/" + n for n in COMPONENTS])):
            have = cats[cat]["paths"]
            have += [q for q in paths if q not in have]
        dump(p, idx)
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
    print(f"{len(G)} garments, {len(COMPONENTS)} components, {len(PALETTES)} dyes, style modern, outfits {', '.join(NAMED)}")


if __name__ == "__main__":
    main()
