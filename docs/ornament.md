# Ornament

Geometric ornament as layers of the pattern language (docs/patterns.md): Islamic star patterns and girih, Celtic and
Viking knots, Roman guilloche, Byzantine braids, and the arabesque vine. No figures and no data: a layer's numbers say
everything. The family is `assets/patterns/ornament.json`, written by `tools/ornamentgen.py` (edit the generator, not the
JSON); finishes place it like any other pattern (`"pattern": "ornament/rosette 10"`).

| file | what it does |
|---|---|
| `ornament.js` | registers the layer kinds `stars`, `knot`, `scroll`; paints them; `measures(L, tile)` for the checks |
| `ornament/net.js` | a net on the torus: cuts segments, joins nodes, finds faces and strands |
| `ornament/stars.js` | polygons in contact (Hankin, Kaplan) |
| `ornament/knot.js` | a grid of crossings with walls (Bain) |
| `ornament/weave.js` | over and under as a two-colouring, band drawing, curves |
| `ornament/scroll.js` | the vine: curls in packed circles, leaves, palmettes, flowers |
| `ornament_lab.html` | a sheet: `?name=a,b&cell=&res=&small=&w=&palette=`; `window.__metrics` holds the seam ratio and the net's measures |

## Stars: `kind: "stars"`

Polygons are laid edge to edge, and each edge's middle sends two rays into each polygon at a contact angle. Where a ray
meets its partner it stops. The gaps between polygons aren't described anywhere: they are the faces of the net and get
rays like any other face.

| key | meaning |
|---|---|
| `n`, `k`, `gap` | the lattice: `n`-sided polygons sharing edges along two normals `k` apart, or `gap` apart with a rectangle between. 8,2 octagons and squares; 12,2 dodecagons and triangles; 12,3 dodecagons on a square; 10,2 ten-point stars; 12,2,gap 1 is 4.6.12 |
| `angle`, `gapAngle` | the contact angle in the polygons, and in what's between them |
| `delta` | two-point patterns: rays start this share of an edge off its middle |
| `depth` | a regular polygon's rays go on past their first partner: above 1 gives a rosette |
| `cells` | how many cells across the tile |
| `fills` | slots by face rank (largest pieces first); a slot may be a list, chosen by which polygon a piece is in; `null` leaves it empty |
| `vary`, `seed` | each piece its own tone, hashed from its centroid so every tile copy agrees |
| `band`, `edge`, `strap`, `strapEdge`, `core`, `coreWidth` | the strapwork, in edges of the polygon |
| `weave` | `false`: flat lines, the grout of zellige |
| `inlay` | `{ ranks, size, stem, flower, heart }`: the vine inside those pieces |

A lattice has one proper aspect, so the generator works out each tile's width from `U`, its height in metres.

## Knots: `kind: "knot"`

Grid points with an odd coordinate sum are nodes. At a crossing a strand goes straight through; at a wall it bounces.

| key | meaning |
|---|---|
| `cols`, `rows`, `wrap` | cells (two grid steps each); `wrap` "x", "y", "xy" or "" for a closed panel. One row with no walls is a guilloche, two a braid |
| `breaks`, `run`, `seed`, `tries` | share of nodes that start a wall, how far a wall runs, the draw; of `tries` draws the one with the fewest strands is kept |
| `symmetry`, `walls` | `x`, `y`, `xy`, `r2`, `r4` repeat the walls (use a square grid for `r4`); `walls` lists any by hand as `[i, j, "h"\|"v"]` |
| `band`, `edge`, `strap`, `strapEdge`, `core`, `coreWidth`, `margin`, `bounce`, `samples`, `curve` | the band, in grid steps |
| `eye`, `eyeSize` | a dot in each loop of a guilloche |

## Vines: `kind: "scroll"`

`cols` and `rows` circles, both even for the rows to meet. A stem runs over one circle and under the next, a curl winds
into each, and palmettes fill the hollows. `width`, `leaf`, `turns`, `leaves`, `end`, `flowers`, `stem`, `leafColor`,
`flower`, `heart`; `under` (a slot) and `underThin` add a second thinner vine half a circle off.

## Rules for anyone adding to it

- A kind draws its own copies once, when `ctx.copy` is `[0, 0]`. Drawn nine times by the tile's loop, a neighbour's whole
  strand would land on this tile's crossings.
- The weave is a two-colouring, and a repeating cell may not have one. `conflicts` in `measures` must be 0; if it isn't,
  the tile has to be two cells.
- `ends`, `loose` and `crowded` must also be 0. A star that needs them not to be is usually a concave gap: `n` 9 was dropped
  for that.
- Don't reuse the language's generic keys for other meanings: `sym`, `at`, `grid`, `rot`, `scale`, `vary`, `seed`, `alpha`,
  `shade`, `clip`.
- The game's tile array is 512 square, so a higher `res` is wasted there.
- A tile's canvas is software-backed (`willReadFrequently`): a GPU canvas drawn while WebGPU starts comes back empty, and
  the tile renders black.
- On a dome use `map: "conformal"`, and for the crown a rule with `above`, `map: "plan"` and `offset`. Not a panel (`at`, `fit`): its
  rectangle cuts the dome, and a conformal mapping tears along a cut. On a pendentive use `map: "revolve"`.
- Pattern scale is chosen in the finish (`scale`), and it decides whether a wall is calm at a distance: domes need about 4
  and large walls about 2. At 1 a star is under a metre across and turns into a mesh.
