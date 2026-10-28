# Patterns and finishes

What a building's surfaces are made of -- a marble floor, a carpet, a wall of glazed tiles, a painted beam, a roof of
glazed tube tiles -- is written as MATHEMATICS and drawn into a texture when it is needed. Nothing is a picture.

    patterns.js                 the pattern language: shapes, grids, symmetries, fields, drawn into a tile
    assets/patterns/*.json      the library: palettes, and families of patterns
    arch/finish.js              which surface of a building is what: rules, inside and out, texture coordinates
    assets/finishes/*.json      one building's finish: its rules
    architecture.js             the finish material (the tile, lit and snowed on like every building material)
    tile_worker.js              tiles drawn in workers while the map grows (archmat.js drawTilesAhead)
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
| timber | (bark is the rough wood's texture -- town woodwork, yards, mills, poles, item materials oak/oak-grey/pine/birch/ash/cedar; plain `wood` grain stays on the fine woods: walnut, mahogany, cherry, ebony, bamboo) a storey of framing, close studding, boards, plain wood (grain); rough planks (`turn: 90` for vertical cladding), weatherboard, round logs (a log house's wall: an izba's, a cabin's), knotty softwood, herringbone and basket-weave parquet, wainscot panelling, a log's end grain, bark. Wood palettes: oak, oak-grey, pine, walnut, mahogany, cherry, birch, ash, chestnut, larch, tarred |
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

**Side is what the building SAYS** (2026-10-28; before, it was measured by rays -- sky over a face, the openness of the
air before it -- slow, and wrong wherever a ray slipped through a crack or a column hid a wall). A building says where
its INSIDE is: its INTERIORS, volumes of air on the plan -- a polygon (with holes) standing from `y0` to `y1` -- carried
as markers (`kind: "marker"`, `role: "interior"`) through every placement, so a component that has one has it in every
copy. A face is in when the air just before it (30cm off along its normal) is in an interior; nothing is stored per face.
  WHERE INTERIORS COME FROM:
- the `interior` flag on a plan part (`walls`, a tower's storeys, an `enclosure`): `true` is the part's own plan and
  height, a number or expression a height of its own (to the vault's springing, into the roof). Given a `thickness`,
  the plan is inset by half of it -- the interior runs on the walls' MIDDLE line, so an opening's reveal is split at
  mid-wall, the outer half the facade's and the inner the room's. `range` and `tiered` storeys have it by default.
- the `interior` part type: `plan` (or `radius` + `sides`, `arc` [from, to] for a sector -- an apse's half disc, its
  centre included), `hole` (a court in the middle), `height`, `at`, and `of`: the parts it belongs to (built only
  with one of them, when a single part is asked for).
- the engines: `basilica` and `gothic` say their aisles' and nave's air (the nave up to its ridge, the aisles to their
  eaves), `court` its ring of wings round the court.
- the flags `inside` / `outside` on any part (or an element within a component): every face of it is that side, the
  innermost flag winning -- buttresses, flyers and pinnacles are outside whatever air they stand in.
  HOW A FACE IS TOLD, in order: a building with no interiors (or a pane of glass) is all out; a part's own `side`;
trim (mouldings, cornices) out; a dome's or a vault's skin in where it faces down or toward its axis, out where it faces
up and away; a roof's upward slopes out; else the probe. Pieces that would cross an interior's boundary are cut first
on its planes -- its floor and top, and the upright plane of every edge of its plan and holes -- so a tower's face is
in below the church roof and out above it, along a level line, never along a triangle's edge. A face is asked only when
a rule needs its side (a finish whose inside and outside walls look alike never asks).
  AUTHORING: the plan on the walls' middle line; the height to the vault's or the roof's springing (or into an
enclosed roof space); where something stands beside a sloped roof (a tower over an aisle), cap the interior at the
eave, so the tower's face above it is out. A portico, an open hall or a loggia under its roof is IN if it has an
interior -- give it one when its plaster and plank floors are meant, leave it out when it is street.
  Rays survive only in the checks (check.js: is a stair walkable, is something held) through solid.js `rayIndex`.

A small up-facing face that is not a stair's (under 2 square metres, or a column's) is a LEDGE, finished as its wall.

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

Tiles are drawn while the map grows. The map is grown on the GPU before any building is built, and the page only waits
on it then. So `archmat.js drawTilesAhead` gives the tiles of every finish the world will ask for to workers
(`tile_worker.js`), one per core. That covers the landmark's finish and its furniture's materials, every `village/`
finish and the windmill's (`architecture.js finishesAhead`), and every finish the town's style may use (`town.js
townFinishes`, the style as its period changes it). The workers register the same library: families, glyphs and murals
(`architecture.js PATTERN_LIBRARY`). Each posts back the tile's layer of the tile array, stretched and flipped as
`tileLayer` makes it, byte for byte the same. The first finish that asks takes it like a cached tile; one not back yet
is drawn on the page as before. At "buildings done" the ones not asked for are let go. On this machine (4 cores, Vulkan,
2026-10-28) the workers drew 41-55 tiles in 4.5-6 s while the map grew for 6.5 s, which did not slow it. The buildings
phase fell from 4.6 s to 2.0-2.9 s. Compare with `?tilesahead=0`. Pregen's tiles are not drawn again, and nothing is
drawn ahead while the generator records or with `?tilearray=0`.

A field's values (`cloud`, `grain`, `veins`, `speckle`) are the same in any colours. So `fieldImage` keeps the last eight,
and the next tile with the same field in other colours only colours them. The items' paints are one brushing in some
sixty colours. They were 4.8 s of a world's 6.6 s of item tiles; with the cache they take 0.4 s, and the pixels are
identical.

Cost, measured on this machine (the headless check): 0.1 s (a Greek temple) to 2-4 s (the Zwinger, 220k triangles,
and the Berliner Dom); about 32 s for all thirty-one buildings (it varies by a third from run to run). A world builds
three.

## The viewer

`assets.html`: **Patterns** -- a family is a sheet, each pattern two tiles across with its other colourings under it,
edited live (the palettes are a sheet of their own); **Finishes** -- a finish on its building; a building in its finish
when it has one (the **finish** box), or in plain stone.
