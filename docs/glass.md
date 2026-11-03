# Stained glass

A window as a pattern layer `{ kind: "glass", form, ... }`, drawn once over the whole tile: pieces are cut into panes, the panes
coloured and painted, and the leads drawn where the panes meet. The family is generated: edit `tools/glassgen.py`, not
`assets/patterns/glass.json`. The bench is `glass_lab.html`.

| file | what it holds |
|---|---|
| `glass.js` | the layer, its cache, `measures(L)` |
| `glass/forms.js` | outlines: `circle`, `foil`, `lancet` (a canopy's arch), the rings of a rose, the stone rose read from `arch/tracery.js` |
| `glass/layout.js` | what's in a window: border, medallion, saint, grisaille, props, `stonePanels` |
| `glass/panes.js` | `partition`: pieces to an arrangement to panes; slivers merged, dead ends pruned, islands bridged |
| `glass/cuts.js` | `cutPane`: the chords a glazier needs through a pane too big or too concave |
| `glass/stain.js` | the painting: colour per pane, sheet mottle, paint hidden by what's in front, corrosion, leads, bars, rim |
| `glass/window.js` | what a seed makes of a `plan`: layouts, borders, grounds, diapers, medallion shapes; a rose's theme and rings |
| `medieval/figure.js`, `story/compose.js` | robed figures and whole scenes as pieces, from the canon shared with mosaic (`docs/story.md`) |

## Layer keys

`form`: `rose` (`rings`), `stone` (`lights`, must equal what `arch/tracery.js` chose for that wall, so the bars sit on the leads) or `light` (`opening`, `border`, `panels`: `medallion`, `saint`, `grisaille`).
`lead`, `minPane`, `maxPane`, `maxAspect`, `depth`: the leading. `ironBars: false` drops the armature. `lie: true`: see below.

## In a building

A finish names a picture for each CELL of a pane with `map: "opening"` (`arch/finish.js`). The rules are written by `tools/glassgen.py` from its `WINDOWS` table, one line each; the rest of a finish is left alone.

    {"parts": "kind:glass", "opening": "round", "map": "opening", "pattern": "glass/rose stone 16", "palette": "paris"}
    {"parts": "kind:glass", "opening": "head", "map": "opening", "pattern": "glass/tracery diaper", "palette": "chartres"}
    {"parts": "kind:glass", "opening": "tall", "nth": [8, 0], "map": "opening", "turn": 90, "pattern": "glass/saint peter", "palette": "chartres"}

- **Cells.** The stone divides a pane, so the pane is cut where it does: a rose is one cell; a traceried window is one cell for each row of each light between its mullions, and one for all the tracery above. A light stops where its little arch closes (`.87` of its width above the springing), so the arch crops the top of the picture, as stone does. The mullions are read from the tracery part beside the glass. A window with no mullions goes up in rows, head and all.
- **Folds.** A robe, mantle or wing over `maxPane` comes apart along its own painted folds (`foldLeads`, `glass/cuts.js`), each run on straight to the pane's edge; only then do chords cut what remains.
- **Frames.** `border.sides` keeps a frame to a light's two sides, so white glass (grisaille, quarries) runs on from one stacked panel to the next with no rail across it: a tile's ends cut the same quarry and the same border block, when `d` divides the tile.
- **Cast light.** `castLight` (`arch/finish.js`) carries the sun-facing panes down the sun's rays to the level face they first meet, as a `cast` group with the glass's own uvs; `castLightMaterial` (`archmat.js`) adds it to the floor, as strong as there's sun (`GLASS_SUN`). What the building shades casts nothing. The sun is fixed (`light.js`), so this is geometry, baked with the building, its key holding the sun.
- **`opening`** is the cell's shape: `round`, `head` (tracery), `tall` (a light at least 2.2 times as high as wide) or `short`. **`nth: [n, k]`** counts cells, so the lights of one window differ.
- **Rows, then pictures.** The stone decides the rows (`rowsOf` in `arch/finish.js`): with `r = ceil(aspect / 3.75)`, a long light goes up in `r` tall rows if each stays at 2.2 or over, and otherwise in rows near square. A row is `tall` or `short`, and rules choose by that. A picture fills its row exactly, repeating if it is much shorter (grisaille), so a figure may be up to a quarter off its drawn build. Only a row far wider than a picture crops it, about the middle. `h` in `light()` is the aspect it's nearest.
- **Which way is out.** An interior says if one is near; otherwise the side from which more of a fan of five rays reaches open sky (an aisle, or a tower looking over the nave's roof).
- The tile array holds 512 squares and runs a long tile only sideways (`across`), so tall lights are `lie: true`: drawn upright, kept with up to the left, and turned back by the rule's `turn: 90`.
- A rule with `map: "opening"` draws in `glassFinishMaterial` (`archmat.js`): the pane's normal looks out, so the material knows the two sides. From inside by day it's the sky through the glass, a little more with the sun on it; from outside it's dark with the sky glancing off. At night every window glows from outside as if lamps stood within, whether or not any do, and goes nearly black from inside.
- A rose with `tracery` takes `rose stone N`, where N is the lights its wall gets: `clamp(2*round(pi*R/1.4), 8, 16)`. The transept roses, R 4.7 and 5.6, take 16.

## A window from its seed

A layer with a `plan` says its subject and leaves the rest to `seed`; `glass/window.js` turns it into plain panels before anything is cut. The seed also retunes the palette a little.

| plan | subject | what the seed decides |
|---|---|---|
| `{ kind: "story", cycles, scene, layout }` | a run of a cycle, or one scene | the scenes, then `stack` (medallions), `cluster` (one, with four busts round it), `registers` (under arches) or `band` (between grisaille); border, ground, diaper, medallion shape |
| `{ kind: "saint", who }` | a saint, or anyone in `standing` | who, a donor, a scene or second saint above in a tall light |
| `{ kind: "tree" }` | the Tree of Jesse | its kings and colours |
| `{ kind: "rose" }` on `form: "stone"` | a stone rose | a theme: who's in the lights, what's at the hub, the colours |
| `{ kind: "rings", like }` on `form: "rose"` | a free rose | how many shapes and which, the colours, busts in one ring |

`saint peter` and the rest name their subject. `saint any`, `panel any`, `medallion story`, `window infancy|passion|genesis|lives|jesse|guilds` and `panel months|guild` leave more to the seed. The palette has 14 slots, in the order of the canon's `tints`.

`glass_lab.html` takes `&seeds=1,2,3` or a count, and `&cw=` for the column width, to show a sheet of seeds. In the game `seedFinishes` (architecture.js) gives each planned pattern a seed from the world and the building, one per pattern per building, so rules sharing a pattern share a tile; a named subject stays itself. An override of `seed` in the asset manager reaches the layer, so New seed is a new window.

## Gates

`glass_lab.html` prints `window.__metrics`: `open` 0 (a lead that ends in glass), `gap` under .004 (share of the opening with no pane), `tiny` 0 (a pane under half of `minPane`, unless it has no other pane to join and is over a quarter of it: a corner the stone leaves). `?twice=1` draws each again past the cache and fails if the pixels differ; a window with no numbers throws rather than passing on nothing. `lab.keep` keeps the panes for the bench's second picture; the game doesn't hold them.

All of them pass on the patterns the finishes hold, on stone and free roses at three seeds each, and on the sweep of 100 seeded tiles (seeds 1 to 10 and 21 to 30 of five plans). A sliver with nothing beside it but something kept `whole` goes into that, a hair more of a face, and a face under a square millimetre is no pane. Those tiles take about 0.2 s on average and up to about 1 s (a narrative window, in the asset manager about 1.2 s).

## Not here

Cast light is judged a patch at a time, about two metres of window, by one ray: a pier takes a whole patch or none of it. A garment's folds take the first leads, but what they leave too big or too long still gets a straight chord. Figures are the medieval canon's, one rig-less build: mitten hands, one face type.
