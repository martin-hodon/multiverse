# Hieroglyphs

Egyptian writing as assets (2026-10-05): the signs of Gardiner's list built up from elementary shapes, drawn in 2D
in the painters' colours, and laid out as walls of text -- in the asset viewer (Hieroglyphs), on a bench of its own
(`glyphs.html`), and on the game's buildings (a pattern layer: Dendera's walls and columns).

## Higher stands on lower

    a shape     the pattern language's (patterns.js): rect, circle, ellipse, ring, lens, star, points, spline, path,
                line, arc ... with fill, stroke, at, rot, scale, clip -- one 2D engine for surfaces and signs alike.
                glyphs.js adds `limb`: a thick stroke along points with its outline (an arm, a leg, a stem, a rope)
    a part      assets/glyphs/parts.json -- an eye, a face, a short wig, the tripartite wig, a god's beard, the torso,
                the kilt, the seated legs, a hand; a bird's body, folded wing, legs, and the heads of falcon, vulture,
                owl, duck, small bird, ibis, cormorant; a feather -- shapes in the part's own frame
    a sign      assets/glyphs/<category>.json, one file per Gardiner category (A man ... Aa unclassified): parts and
                shapes in the QUADRAT -- 100 units square, x right, y up, the baseline at 0 -- facing LEFT, as
                Gardiner and Unicode have them
    a text      assets/glyphs/textures.json: an X x Y grid of quadrats, filled by seed (renderTexture)

A layer that is a part or another sign: `{ "part": "eye" | "sign": "A1", "at", "rot", "scale", "flip", "colors" }`.

## Colours

`assets/glyphs/colors.json`: the six pigments (red and yellow ochre, Egyptian blue, green, carbon black, gypsum
white) and their shades, by name, then the ROLES (`skin` red, `skin-woman` yellow, `wig` black, `cloth` white,
`water` blue, `plant` green, `bread` yellow, `line` black, `ground` limestone...). A colour in a layer is a role, a
palette name or `#rrggbb`. The roles a sign sets flow down into every part it uses (B1's `skin: skin-woman` reaches
her torso); a part's own `colors` are its defaults, used where nobody set the role. Each sign gives its traditional
colouring: the vulture yellow with a green wing, the falcon blue, the owl yellow-brown, the water blue, the reed and
the baskets green, the sun, the mouth, the house and the folded cloth red, the loaf yellow, the ankh blue.

Every filled shape is outlined in `line` at one width however deep it is scaled (`outline: false` not; a sign's
`outline` its width, 1.1 units). A stroke alone is a DETAIL (an eye's line, a mat's weave) -- or, thicker than 2.5,
the sign's body (the water's zigzag, the house plan's walls).

`modes` paint a whole sign or text in one way: `blue`, `green`, `black`, `gold` (one colour for every sign, as tomb
walls and shrines have them), `red draft` (outlines only), `carved` (sunk relief in the stone). Each is
`{ fill, line, detail }`, null for not drawn.

## A sign

    "G17": { "name": "owl", "u": "13153", "reading": "m", "freq": 8,
             "colors": { "plumage": "yellow", "wing": "yellow-dark", ... },
             "layers": [ { "part": "bird-legs" }, { "part": "bird-body" }, { "part": "bird-wing" },
                         { "part": "head-owl", "at": [30, 64] } ] }

`u` is the Unicode code point, `reading` the sound value (or the sense of a determinative), `freq` how often texts
use it -- a text draws by it, the alphabet's signs most. 106 signs in all 26 categories: the whole uniliteral
alphabet (G1 A, M17 i, D36 a, G43 w, D58 b, Q3 p, I9 f, G17 m, N35 n, D21 r, O4 h, V28 H, Aa1 x, F32 X, O34 z, S29 s,
N37 S, N29 q, V31 k, W11 g, X1 t, V13 T, D46 d, I10 D, Z4 y, Z7 w) and common bi- and triliterals and determinatives.

A mirror is a flip: `drawGlyph(g, code, { flip: true })` -- a line read the other way turns all its signs.

## A text

    "tomb wall": { "cols": 10, "rows": 6, "cell": 64, "lines": "columns", "face": "left", "pool": { "*": 1 },
                   "ground": "limestone", "divider": { "color": "blue", "width": 0.04 }, "cartouche": 0.03, "seed": 1 }

`pool`: categories or codes with weights (times each sign's `freq`); `lines` columns or rows; `face` left, right,
alternate (lines facing each other, a doorway's jambs) or random; `mode`; `ground`, `divider`, `border`;
`cartouche`: the chance a line's next two or three quadrats are a name in its ring (one a line at most).

The QUADRAT is packed as scribes pack it, by each sign's class from its drawn bounds (`classOf`): a tall sign alone
(two narrow ones side by side), flat signs stacked two or three, small ones in pairs or under a flat one -- each at
its own size in the quadrat, never blown up, the group shrunk to fit. Presets: tomb wall, blue tomb, temple frieze,
sunk relief, papyrus, gold shrine.

## On a building

A pattern layer `{ "kind": "hieroglyphs", "texture": <name or a text>, "seed", "size" }` (patterns.js
`LAYER_KINDS`, which glyphs.js registers) lays a text over the tile. `assets/patterns/hieroglyphs.json`: sunk
relief, painted columns, tomb wall, blue tomb, temple frieze -- a quadrat about 30 cm; Dendera's finish carves the
hall's and the inner rooms' walls and paints the columns. A divider at the tile's edge (half each side) lets a wall of
text repeat without a seam. The pregen cache keys a tile on the glyph library too (`deps`).

## The viewer and the bench

assets.html, Hieroglyphs: a category is a sheet of its signs, each with its mirror small beside its name and its
reading; the parts and the palette likewise; the texts whole. `M` cycles the modes, `S` draws another text. The form
suggests parts, signs and colours. `glyphs.html` is a bench without WebGPU: `?doc=glyphs/G`, `?doc=all` (every sign),
`?sign=G17&px=400&flip=1`, `?doc=glyphs/textures&seed=3`, `&mode=blue`, `&bare=1` (no header, for shots).

Pitfall: the 2D contexts are software (`willReadFrequently`) -- Chromium puts a larger canvas on the GPU, and that
can come back blank while WebGPU starts (a text over 70 px a quadrat came out empty on the walls).
