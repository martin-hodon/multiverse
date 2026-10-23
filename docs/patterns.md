# Patterns and finishes

What a building's surfaces are made of -- a marble floor, a carpet, a wall of glazed tiles, a painted beam, a roof of
glazed tube tiles -- is written as MATHEMATICS and drawn into a texture when it is needed. Nothing is a picture.

    patterns.js                 the pattern language: shapes, grids, symmetries, fields, drawn into a tile
    assets/patterns/*.json      the library: palettes, and families of patterns
    arch/finish.js              which surface of a building is what: rules, inside and out, texture coordinates
    assets/finishes/*.json      one building's finish: its rules
    architecture.js             the finish material (the tile, lit and snowed on like every building material)
    assets.html                 a family shown as a sheet of swatches in its palettes; a building in its finish

## Why this way

A surface pattern has to be crisp near, calm far, cheap to draw and easy to vary. So a pattern is a DEFINITION (shapes
set out on a tile a given number of metres across) and the game BAKES it: at load the tile is drawn with Canvas2D
paths -- exact, anti-aliased, at any resolution -- into a texture with mipmaps and anisotropy, so a chequered floor seen
at a grazing angle stays a chequer instead of a moire, and a tile costs one texture read a pixel. The definition is
the source; the texture is its picture, made when needed. (The older tiles of textures.js -- ashlar, brick, marble,
checker, the crops -- are evaluated in WGSL and carry parallax relief; a finish may still use them as `pat`.)

Colour is by SLOT: a pattern says "slot 1", a PALETTE says what slot 1 is, so every pattern is as many colourings as
there are palettes -- the same Iznik tile in cobalt, in turquoise, in Kashan brown. And a pattern may USE another inside
any of its shapes, with its slots remapped -- a carpet is its border vine round its herati field round a star medallion.

## The language

    { "size": [w, h],            metres: one tile (one period)
      "repeat": false,           a PANEL: drawn once (a carpet, a compass rose), placed by the finish
      "params": { "W": 8 },      numbers the layers may use -- every number may be an expression (expr.js), and W, H
                                 are the tile's size
      "palette": "iznik",        its colours unless the finish says (palettes.json), and "palettes": [...] the ones
                                 the viewer shows it in besides
      "ground": 0,               the slot under everything
      "res": 1024,               texels across its longer side (512 unless it says)
      "layers": [ ... ] }        drawn in order

A LAYER is one shape (or a group, a field, another pattern) and how many times it is drawn:

| key | what |
|---|---|
| `shape` | `rect` (w, h, r corners), `frame` (w, h, t: a rectangle with a rectangle out of it), `circle` (r), `ellipse` (rx, ry), `ring` (r, w), `poly` (n, r), `star` (n, r, inner), `lens` (r, w: a vesica), `petals` (n, r, inner, w), `cross` (w, h, t), `points` (a polygon), `spline` (a smooth outline through `points`, Catmull-Rom by `tension`; a point `[x, y, 1]` a corner; `closed: false` an open curve, stroked), `path` (SVG path syntax, metres, y up), `line` (from, to), `arc` (r, a0, a1), `band` / `vband` (a stripe across the whole tile), `wave` / `zigzag` (a band swinging `amp`, `n` times across) |
| `fill`, `stroke`, `line` | a slot or "#rrggbb"; the stroke's width in metres |
| `at` | where it stands (a point or a list), from the tile's middle |
| `grid` | `[nx, ny]` or `{ n, offset, span }`: copies over the tile, every other row set off by `offset` (a brick bond, fish scales -- rows are drawn top down, each overlapping the one above) |
| `sym`, `mirror` | copies turned round the centre (`sym` 4: a quatrefoil from one circle set out from the middle), reflected ("x", "y", "xy") |
| `rot`, `scale` | turn and size the shape in its place |
| `vary`, `seed` | each copy its own tone (every stone of a wall, every tessera) |
| `alpha`, `shade` | see-through; lighter or darker than its slot |
| `clip` | a shape (with its own `at`, `rot`) the layer is drawn only inside |
| `layers` | a group: its children in this layer's frame (clip them together) |
| `use`, `useScale`, `colors`, `palette`, `params` | another pattern, tiled inside this layer's shape, its slots mapped to this one's |
| `kind` | a layer another module draws (`LAYER_KINDS`): `hieroglyphs` (glyphs.js: a wall of text, docs/glyphs.md) |
| `field` | a function of the point, per texel: `veins` (marble: `freq`, `turns`, `sharp`), `speckle` (granite: `grain`), `cloud` (plaster), `grain` (wood) -- periodic with the tile, so it repeats without a seam |

The tile is drawn with every layer at the tile and its eight neighbours, so whatever crosses an edge carries on into
the next tile; a field is periodic noise on a lattice that wraps with the tile. `patterns.js drawSheet` draws a family
as a sheet; `tileSampler` reads a tile at (u, v) metres (the headless checks render with it). `drawShapes(g, layers, ...)` draws layers into any frame outside a tile -- how glyphs.js draws a sign.

## The library

| family | patterns |
|---|---|
| shapes | the alphabet: one pattern for each shape and each way of multiplying one |
| stone | ashlar, fine ashlar, rusticated, brick (running and Flemish bond), rubble, marble, book-matched revetment, travertine, granite, plaster, scored stucco, sand, a column's flute |
| floors | chequer (square and diagonal), the Pantheon's opus sectile, octagon and dot, star and cross, basketweave, flagstones, terracotta, a Cosmatesque roundel, a compass rose (panel) |
| carpets | the herati field, a border vine, prayer rows, kilim, and the medallion carpet (a panel of any size: W, H) |
| tiles | Iznik carnation, rumi and frieze; zellige star; girih; azulejo |
| painted | gold mosaic, starry vault, stained glass, the Chinese painted beam (caihua), cloud scroll, window lattice, coffered ceiling, Russian floral, Ottoman stencil, faux marble |
| roofs | Chinese tube tiles, coppi, slate, fish scale, sheet metal (lead, copper), gold leaf, glazed chevrons (the Stephansdom), onion stripes, spiral and diamonds, glazed diamonds |
| panels | Florentine polychrome, pietra dura, jali, a Chinese balustrade's panel, wainscot |
| timber | (bark is the rough wood's texture -- town woodwork, yards, mills, poles, item materials oak/oak-grey/pine/birch/ash/cedar; plain `wood` grain stays on the fine woods: walnut, mahogany, cherry, ebony, bamboo) a storey of framing, close studding, boards, plain wood (grain); rough planks (`turn: 90` for vertical cladding), weatherboard, knotty softwood, herringbone and basket-weave parquet, wainscot panelling, a log's end grain, bark. Wood palettes: oak, oak-grey, pine, walnut, mahogany, cherry, birch, ash, chestnut, larch, tarred |
| fabrics | the tailor's cloth (clothes.js): plain, linen, twill, herringbone, stripes, checks, tartan, damask, brocade, quilted, mail, leather, fur, straw, braid... |
| materials | what items are made of when it is not wood, stone or cloth: paint, metal (brushed), hammered, lacquer, horn |
| hieroglyphs | walls of writing (glyphs.js, docs/glyphs.md): sunk relief, painted columns, tomb wall, blue tomb, temple frieze |
| heraldry | a shield's face (panels, `W` x `H`: fitted to the shield): plain; per pale, per fess, quarterly, per bend, gyronny; cross, saltire, chevron, bend, pale, fess, chief, bordure, roundel; paly, barry, chequy; wings, sun, lion |

## Finishes

A building's finish is a list of RULES; the first that matches a piece of surface gives it its look.

    { "building": "architecture/temple-of-heaven",
      "stone": { "color": "#ece9e1", "accent": "#d6d2c8", "pat": "marble" },     what no rule takes
      "rules": [
        { "parts": "kind:glass", "pattern": "painted/lattice", "palette": "chinese-red" },
        { "parts": "kind:dome", "surface": "roof", "pattern": "roofs/tube tiles", "palette": "glazed-blue" },
        { "parts": "architrave", "pattern": "painted/caihua", "align": "part" },
        { "surface": "floor", "at": [0, 0], "pattern": "floors/compass", "scale": 0.4 },
        { "surface": "floor", "side": "in", "pattern": "floors/terracotta", "palette": "slate" },
        { "surface": "wall", "side": "in", "below": 2.5, "pattern": "tiles/iznik carnation" }, ... ] }

MATCH: `parts` (a part's name, its name less a trailing number, its own name inside a component, the component's name,
or `kind:<kind>` -- the same list the building's colours were read by; a rule without `parts` never takes a window's
GLASS: a pane is finished only by a rule that names it, its part or `kind:glass`, else it is the building's glass), `surface` (floor, wall, ceiling, roof), `side`
(in, out), `below` / `above` (a height), `within` ([x0, z0, x1, z1] on the plan). GIVE: `pattern`, `palette`,
`scale`, `turn`, `map`, `align` ("part": the tile's foot on the part's foot -- a painted beam, a band), `offset`,
`count` (tiles round a round thing: one balustrade panel to a bay), `params`, `res`; a PANEL at a point (`at`) or made
to a rectangle (`fit`: its W and H); or a plain stone (`color`, `accent`, `pat`).

**Surface** is read from the triangle -- up-facing a floor, down-facing a ceiling, else a wall; a roof's or a dome's
outside its roof. A ceiling no rule takes (a soffit under an arch, a window's head) is tried again as its wall.

**Side is decided by the FACE, not the triangle** (2026-09-27, after triangles of one wall came out in two finishes).
A part's triangles are joined into faces across every edge where the surface bends by less than 25 degrees
(`facesOf`: a wall's face with its holes, a dome's skin, a column's shaft, a roof's slope), and each face -- in each copy
of the part -- is decided in level BANDS about 3m tall (`bandsOf`), at points at the band's mid-height on its largest
triangles and on those turned most unlike them (round a column, not two facets side by side). A face is cut only where
two bands disagree -- a tower's face toward the church it stands against, inside below the church's roof and outside
above it -- so a finish changes on a level line across an element, never along a triangle's edge. A point that is
HIDDEN is not asked (`tell.hidden`): stone standing before it within 60cm (a column or a pier against a wall), or the
point buried in another part's solid (a portal's corner shaft standing half into its face -- solid.js `insideOf`, an
odd count of crossings over it, asked only when stone lies ahead of it within 8m). Asked there, the air would be
the inside of the column, and a facade would come out inside.
  At each point: **sky straight over the air before it** (a wall asked from 40cm off, clear of its mouldings; a floor from
where one standing on it would see, 1.2m up, over a parapet) is outside at once -- a floor must also see it steeply to
the side (not only through an oculus), a roof any steep way. Otherwise the **openness** of the air it faces: sixteen
directions spread evenly over the half of space in front (level and rising for a wall, level all round for a soffit,
asked 1.5m under it), outside if a sixth or more escape the building. A room or a nave is closed but for its doors (the
Hall of Prayer's four: a tenth, from its middle); a portico's back wall, an arch's soffit, a drum behind its peristyle
are covered but open sideways. A flat face goes the way most of its area goes; a face that wraps round (a column) is
outside if a quarter of it looks out. **A reveal is its wall's**: the jamb or soffit of an opening measures as closed
in, so a face found inside takes the side of a larger face it meets along a crease, at its own height, if that one is
outside -- an outside window's reveals follow the facade, an opening between two rooms stays inside.
  The rays walk 2m cubes (solid.js `rayIndex`); points are cached every 3m (by facing too) and an answer is reused only where the two probes see each other -- the same air (2026-10-03: a windmill bay outside took the answer of the grain bin inside, 2m off, facing alike); a face is asked only when a rule needs its
side (a finish whose inside and outside walls look alike never asks).

A FLOOR is asked at up to eight points spread over its face, those with open air over them (not hidden under a wall,
a column's foot, or the deck an abacus carries); a face with none is out of sight, and outside. Points that agree
decide it; a floor that runs from a room out onto a terrace (a building's platform, or a floor too large to be one
room) is asked piece by piece. A small up-facing face that is not a stair's (under 2 square metres, or a column's) is a
LEDGE, finished as its wall.

Large floors are cut on a 2m grid first -- a platform under a church and before its door is one plane, inside and out
-- and bands and regions cut what crosses their lines; a cut is made from the edge's own ends in one order, so the
triangle on the other side of the edge is cut at the same point.

**Mapping**, in metres: `plan` (floors and ceilings: u east, v north), `face` (walls: along, up), `revolve` (domes,
vaults, drums, columns: round the part's own axis, a whole number of tiles round so the rows meet, and up a dome's
meridian by its length -- the rows of a round roof converge toward its crown as the real ones do), `slope` (roofs: along
the eave, up the slope).

## In the game

`architecture.js` imports the library and every finish (`FINISHES`, by building); `archBuilding` finds its own,
Florence and the arena ask for theirs. `archMesh(name, { finish })` builds one mesh per rule: a pattern's in the FINISH
MATERIAL (the tile read at the vertex's `aUV`, lit and snowed on by the same WGSL as every building material --
`SHADE_K`, `SNOW_ON`), a plain stone's in the building material with its colour in the vertices, the glass no rule took
in the glass. Tiles are shared across rules and buildings (keyed by pattern, palette and params).

Cost, measured on this machine (the headless check): 0.1 s (a Greek temple) to 2-4 s (the Zwinger, 220k triangles,
and the Berliner Dom); about 32 s for all thirty-one buildings (it varies by a third from run to run). A world builds
three.

## The viewer

`assets.html`: **Patterns** -- a family is a sheet, each pattern two tiles across with its other colourings under it,
edited live (the palettes are a sheet of their own); **Finishes** -- a finish on its building; a building in its finish
when it has one (the **finish** box), or in plain stone.
