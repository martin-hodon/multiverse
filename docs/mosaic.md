# Mosaic

Tesserae as a technique over any drawing: a pattern layer `{ kind: "mosaic", layers: [what's drawn], ... }`. The layers are any layers
of the pattern language: shapes, an ornament's knot, a Greek painting. No data but the layer. The family is
`assets/patterns/mosaic.json`, written by `tools/mosaicgen.py` (edit the generator, not the JSON); finishes place it like any
other pattern (`"pattern": "mosaic/bw meander"`).

| file | what it does |
|---|---|
| `mosaic.js` | registers the layer kind; `renderMosaic` keeps the last 8 layings; `measures(L)` the last numbers for a layer |
| `medieval.js` | the layer `{ kind: "figure", h, figure, at, seed }`: a medieval figure (`medieval/figure.js`) in flat colours, its faint strokes left out, for a drawing laid over; and `{ kind: "story", scene or person, seed, frame, dye, ground, ink, line, stone, wear, within, float }`: a scene of the canon the same way, an ink line round each piece |
| `mosaic/floor.js` | what a seed makes of a `plan`: Roman floors, Byzantine walls, geometric fields, border strips; the layer `{ kind: "polys", items, within }` they draw with |
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
- A big tile (over half a million texels) draws them at 1.5 times, not twice: that's what holds it to a second. A mortar texel then weighs .75 of what it does at twice, in the paint and so in `grout`; the lab reduces the drawing to the tile's texels before it compares.
- Gates in the lab, read off `__metrics`: `seam` under 1.3, `moire` under 1.5, `drift` under 8 (up to 12 where `mix` or `gleam` means it,
  gold), `pitchPx` at least 3 (its smallest, `fine` counted), `grout` under .3. Drawn twice it must give the same `hash`, and the worker's tile is the same code.
- A tile costs 200 ms to 1 s (the whole laying is a few passes over the map, each kept to a flat loop) (24 kinds of mosaic at most in a world, and `build/pregen.py` keeps them). Don't add a
  big region's worth of `flow` lightly: that's what costs the most.
- Domus has its `paving`, a part of its own, because a `court` has no floor to carry a rule. Its generator entry matches, but
  don't re-run `tools/archgen/dwellings.py` to apply it: that overwrites hand-edited finishes.

## A floor from its seed

A layer's `plan` becomes its drawing before any stone is laid (`planned` in `mosaic/floor.js`). Who's in the picture comes from the canon shared with glass (`docs/story.md`). The stones know nothing of it.

| plan | subject | what the seed decides |
|---|---|---|
| `{ kind: "floor", subject, layout, bw }` | `hunt`, `arena`, `gladiators`, `neptune`, `dionysus`, `triumph`, `orpheus`, `sea`, `xenia`, `any` | colours, one to three framing strips, the layout (`emblem`, `panels`, `open`, `registers`, `seasons`, `grid`, `octagons`, `lozenge`, `field`, `wheel`, `quad`) and what fills it. `bw` is Ostia's: black silhouettes, their lines in white |
| `{ kind: "wall", subject, ground, bands, piers, h, foot, sill }` | `bust`, `virgin`, `deesis`, `court`, `empress`, `apostles`, `fathers`, `shepherd`, `lambs`, `cross`, `roundels`, `arcade`, `nativity`, `any` | gold or starry lapis, head and foot bands, a meadow, who stands there. Bishops go bareheaded, as in the East |
| `{ kind: "field", field, fields, schemes, n, v, stone }` | one of `hexagons scales chequer octagons stars blocks peltae basket chevrons petals lozenges triangles rosettes`, or a list | which, in which colours, how many cells, what's inside each |
| `{ kind: "strip", strip, strips, schemes, bar, stone }` | one of `guilloche meander tkey wave dentil saw chequer lozenges beads ivy plait`, or a list | which, in which colours |

A floor's hunts, fights and triumphs are bodies in action on Greek's rig, its still subjects frontal figures (`docs/story.md`). A court stands before a palace: an entablature, columns at its ends, curtains looped back. `fathers` may be another company of the church's walls (prophets, apostles, deacons, virgins, warriors), bare on the gold or each in a niche.

`set` on a plan goes onto the layer as it's drawn (`wander`, `thin`), and `sets` is a field's own override of the plan.

Fields and strips hold whole, even numbers of cells, so what alternates comes round again and they tile. Their cell edges are kept off the tile's own edge. A line thinner than a stone is widened to what the stones will lay, or dropped if it only edges a fill.

`plan.keep`: at that seed the pattern stays the drawing it has always had, which is what the finishes use (`bw meander`, `bw hexagons`, `gold braid`, `gold fathers`, `gold virgin`...). Any other seed is a new one of the same kind. `follow` on an emblem makes the nested Greek painting follow the layer's seed.

The catalogue: `floor any|wide|hunt|arena|neptune|dionysus|orpheus|seasons|sea|xenia|ostia`, `wall any|pantocrator|virgin|deesis|emperor|empress|apostles|fathers|shepherd|lambs|cross|roundels|arcade`, `field bw|colour`, `strip any`. Long walls are `across: 2`: a 2.6 by 1.3 m tile on two layers.

`mosaic_lab.html` takes `&seeds=1,2,3` or a count, and `&plain=1` for pictures only.

## What the gates caught

Each of these failed a gate at some seed. The thresholds stayed where they were and the drawing or the plan changed.

- **A true chequer reads as moire.** Its rows and columns balance, so the drawing's own beat is about .0005 and lands on the floor of .004, and the ordinary straight courses (about .008) count as a pattern the laying added. The default drawing passes because it isn't balanced. `wander: .35` breaks the courses up (moire .87 at the seeds tried).
- **Sharp tips of a diagonal field read as thin lines** and get laid over their neighbours (drift 13 to 16). `thin: .3` gives 2.7 to 7.7. It raises a chequer's drift, so the chequer has its own `sets` entry.
- **Figure lines thinner than a stone** lay darker than they were drawn, which is contrast the drawing doesn't have (`gold fathers`, moire 1.5 at three seeds). Story lines are now 1.12 stones wide (`INK`).
- **Wall bands too fine:** a band's motif goes to its dark (drawn .288, laid .17, moire 1.69). A band is at least 10.5 stones deep, its rules at least 1.15, and no chequer among them.
- **Wide floors:** `thin: .45` on Roman floors takes drift from 8.3 to about 2.

## Figures on gold

`gold fathers` and `gold virgin` lay frontal figures on the gold ground. In Hagia Sophia the fathers stand on the tympana's piers: a tile is three of the wall's window bays, so each falls between two windows. The Virgin is on the east half dome, not in the apse, because the exedra's middle pier hides the apse from the nave. Her rule uses `map: "meridian"`, true metres up the dome: plain `revolve` counts both shells of a thick dome, which the existing finishes' scales rely on. Her tile is a third of the way round, so her neighbours fall off the half dome's sides, and runs over two layers of the tile array. Stones meet the 3-texel gate at the array's 512: about 12 cm on the half dome, 7 cm on the tympana, 6.5 cm on the other walls, the gold around each as coarse, so no tile shows an edge.

In the game `seedFinishes` (architecture.js) gives a building's planned patterns a seed of the world's. `gold fathers` has `pinned`: its figures have to fall between the windows, so it keeps its own seed. A plan's `reach` is how far up the tile a wall's picture may go: `gold virgin` has .74, because her rule cuts the tile's top at the half dome's crown and the seeded figures lost their heads there.
