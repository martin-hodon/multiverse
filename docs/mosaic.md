# Mosaic

Tesserae as a technique over any drawing: a pattern layer `{ kind: "mosaic", layers: [what's drawn], ... }`. The layers are any layers
of the pattern language: shapes, an ornament's knot, a Greek painting. No data but the layer. The family is
`assets/patterns/mosaic.json`, written by `tools/mosaicgen.py` (edit the generator, not the JSON); finishes place it like any
other pattern (`"pattern": "mosaic/bw meander"`).

| file | what it does |
|---|---|
| `mosaic.js` | registers the layer kind; `renderMosaic` keeps the last 8 layings; `measures(L)` the last numbers for a layer |
| `medieval.js` | the layer `{ kind: "figure", h, figure, at, seed }`: a medieval figure (`medieval/figure.js`) in flat colours, its faint strokes left out, for a drawing laid over |
| `mosaic/source.js` | the drawing at twice the tile's texels, read as a map: each texel's stone, regions of one stone, how far from a region's edge |
| `mosaic/lay.js` | every texel to one stone, in the order a mosaicist sets them; then the joints |
| `mosaic/paint.js` | each stone's colour, lifted for what the joints take away; the texels boxed down to the tile |
| `mosaic_lab.html` | a sheet: `?name=a,b&cell=&crop=&cx=&cy=&res=&palette=`; `window.__metrics` holds the numbers below |

## The laying

**Stones partition the map.** There are no rectangles with gaps between them: every texel goes to a stone, and grout is what's
left where two stones meet. Stones laid side by side with jitter leave holes, and small stones to fill those turn a plain floor to salt.

1. **Lines.** A texel is thin if no disc about a stone across fits round it inside its region. Thin texels are walked along
   their ridge, one stone wide however thin the drawing's line was. A line's stones may lie over their neighbours.
2. **Andamento.** `halo` rows hug each region's edge: each stone runs along its isoline of `dist` from where the last stopped.
   A slot in `flow` (or `fill: "flow"`) carries on inwards, as flesh does.
3. **The field.** What's left: rows and columns as a map of the point, wandering together (sines of whole turns, so it wraps).
4. **Scraps.** A stone under `scrap` of a whole one goes to its neighbours in the region.
5. **Joints.** `joint` of a stone wide, half mortar and half the stones' own colour, so joints on black aren't pale.

Its colour is never a mean of what's under it, which would turn lines to mud: a stone is its region's slot.

## The layer

| key | meaning |
|---|---|
| `layers`, `ground` | the drawing, and its ground slot. It sees the tile as usual, once |
| `stone`, `aspect` | row spacing in metres (rounded to whole rows up a repeating tile); length to width |
| `joint`, `groutColor` | a joint's width as a share of a stone; the mortar |
| `halo`, `flow`, `fill` | rows along each region's edge; slots whose rows carry on inwards; `"flow"` for all |
| `lay`, `wander`, `jitter`, `wobble` | the field's rows: `x` or `y`; in stones; `[length]` share; a row stone's turn in degrees (rows only: the field has no angle to turn) |
| `fine` | `{ slot: k }`: stones in that slot `k` the size (flesh) |
| `tone`, `gleam`, `mix`, `model` | each stone's lightness, plus or minus; glass tilted, a few stones catching the light; `{ slot: [slots] }` stones drawn from others; `{ slot: [by row] }` modelling |
| `dust`, `thin`, `thread`, `scrap` | a region smaller than (this × a stone) squared goes to its neighbour; a line is thinner than this many stones' radius (runs under two stones' area aren't lines); a line stone's half width; see above |
| `seed` | the draw |

The drawing's colours must be the palette's: a painting comes in through the Greek technique `mosaic` (`greek/paint.js`), whose
flat colours are `opus-stone`'s and whose lines are a stone wide. It takes a `box` in metres, and stands where the layer says.

## Rules for anyone adding to it

- `stone` sets the tile's real resolution. Below about 3 texels a stone at the game's 512, joints eat the picture
  (`grout` over .3) and faces go: use a coarser stone or a bigger `size`, not a higher `res`.
- It replaces the whole tile, so it goes at the pattern's top level, once. To frame or inset, put it in `layers`.
- It's the source's texels that count: `layers` are drawn at twice `res`, so a `use` inside gets four times the work.
- Gates in the lab, read off `__metrics`: `seam` under 1.3, `moire` under 1.5, `drift` under 8 (up to 12 where `mix` or `gleam` means it,
  gold), `pitchPx` at least 3 (its smallest, `fine` counted), `grout` under .3. Drawn twice it must give the same `hash`, and the worker's tile is the same code.
- A tile costs 200 ms to 1.2 s (the whole laying is a few passes over the map, each kept to a flat loop) (24 kinds of mosaic at most in a world, and `build/pregen.py` keeps them). Don't add a
  big region's worth of `flow` lightly: that's what costs the most.
- Domus has its `paving`, a part of its own, because a `court` has no floor to carry a rule. Its generator entry matches, but
  don't re-run `tools/archgen/dwellings.py` to apply it: that overwrites hand-edited finishes.

## Figures on gold

`gold fathers` and `gold virgin` lay frontal figures on the gold ground. In Hagia Sophia the fathers stand on the tympana's piers: a tile is three of the wall's window bays, so each falls between two windows. The Virgin is on the east half dome, not in the apse, because the exedra's middle pier hides the apse from the nave. Her rule uses `map: "meridian"`, true metres up the dome: plain `revolve` counts both shells of a thick dome, which the existing finishes' scales rely on. Her tile is a third of the way round, so her neighbours fall off the half dome's sides, and runs over two layers of the tile array. Stones meet the 3-texel gate at the array's 512: about 12 cm on the half dome, 7 cm on the tympana, 6.5 cm on the other walls, the gold around each as coarse, so no tile shows an edge.
