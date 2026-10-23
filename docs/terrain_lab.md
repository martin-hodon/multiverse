# Terrain lab

`terrain_lab.html` grows land the way land grows: plates push rock up and pull it apart, volcanoes pour out new basalt,
rain wears the surface down, rivers carry the waste away and lay it down in valleys, lakes and the sea, and buried
sediment turns back into rock. Everything runs on the GPU (WebGPU compute, WGSL), on a grid of rock COLUMNS, in
geological time. What comes out is a height field and what it is made of -- plains, mountain belts, valleys, mesas,
canyons, rivers and lakes are not drawn, they are what the processes leave.

    terrain_lab.html        the page: the view, the controls, the tools
    terrain_lab.js          the engine: the state on the GPU, one step of geological time, the view's upscaling
    terrain_lab_wgsl.js     the shaders

## Scale and time

One run is a REGION: 256 x 256 cells of 100 m -- 25.6 km on a side (128 and 512 cells too). A step is `dt` years
(100 by default); rates are the real ones -- uplift in mm/yr, weathering in mm/kyr, rivers cutting a few mm/yr -- so a
mountain belt takes about a million years (ten thousand steps, a minute of running) and a canyon a few hundred thousand.
Relief is metres. The view adds the detail a 100 m cell cannot hold (below).

## What a cell is

A COLUMN: an infinite GRANITE BASEMENT whose top is at `base`, and on it a STACK of up to 8 layers, bottom to top, each
a material and a thickness. The ground is `base + sum of the stack`. Deposition lays a layer on the top (onto the top
layer if it is the same material); erosion takes from the top down, a layer at a time; in a full stack the thinnest
pair of neighbouring beds (under the top one) becomes one bed, of the thicker one's rock. A cross-section is therefore real bedding: flat-lying strata, a basalt cap,
a lake's sediments, cut through where a river went down.

Besides the rock, per cell: the WATER SURFACE `W` (lakes and sea: the ground filled to its spill level, below), the
DRAINAGE (the discharge `Q` through it and the sediment flux `Qs`), LAVA still flowing, and the UPLIFT RATE the tectonics
gives it.

## Materials

Few, and far apart in how they behave:

| material | made by | erodibility | weathers | stands at | colour |
|---|---|---|---|---|---|
| granite (basement) | plates: the crust itself, raised in collisions | 0.25 | slowly | 42 deg | pink grey |
| basalt | volcanoes, rifts: lava cooling | 0.35 | slowly | 48 deg (columnar cliffs) | near black |
| sandstone | buried sediment (lithified) | 1.0 | fast | 34 deg | red tan |
| limestone | shallow clear water (carbonate) | 0.6 | dissolves in rain | 40 deg | pale grey |
| sediment | erosion and weathering: loose sand, gravel, soil | 4.0 | -- | 27 deg | ochre |

Erodibility multiplies the river's cutting and the waves'; the angle is the steepest slope a 100 m cell of it holds
before it slides (a whole hillside's, gentler than a single cliff's). A hard cap over a soft rock is what makes a mesa:
the basalt holds a cliff while the sandstone under it is carried away.

No rock is the same everywhere: its erodibility varies by `rockVar` (+-30 %) over a smooth field a kilometre or two
across (joints, cement, grain). Rivers find the weak lines, and wander along them.

**Neighbours, and the grid.** Every process looks at all 8 neighbours, the diagonals at their true distance
(`sqrt 2 dx`). But a square grid still has directions of its own, and land grown on it takes them up wherever something
is decided cell by cell. So: water and sliding rock go down the TRUE steepest way, at any angle (D-infinity, below);
a river's cutting is spread over a few cells (a gully head one cell wide grows along the grid's axes, whose neighbours
are nearer than the diagonal ones); and every noise the land starts from is gradient noise on a lattice turned off the
grid. The headless check measures it: of the steep slopes, a third face within 7.5 degrees of one of the grid's 8
directions if nothing prefers them; the presets come out at 34-37 %.

## The edge

The region's edge is its BASE LEVEL: where the water leaves and what the rivers cut down to. By default the whole edge
is, fixed where it started (the uplift fades out towards it along a wavy line). A preset can instead give OUTLETS
(points on the edge, a few hundred metres wide; the tool sets them too): then only they are base level, and elsewhere
the edge is a WALL -- each edge cell a copy of the one inside it, the land going on flat across it, nothing running out
over it -- and it is no one's neighbour: water, talus, lava and the fill all go round it. A plateau drains by a river or
two, and its canyons grow back from them, branching; with base level all round, the plateau wore back from all four
sides into a square of scarps.

INLETS (a preset's, [x, y, Q, Qs]) bring a river from beyond: a region is a piece of a larger land, and its big river
drains far more than the region does. Its water and sediment join the first cell inside the edge (they need outlets,
or the river leaves again by the nearest edge).

## The processes, in one step

1. **Tectonics.** PLATES are the Voronoi regions of a few seeds, each moving at its own velocity (mm/yr). Where two
   meet, their relative motion across the boundary decides: CONVERGING, the crust thickens and rises -- uplift
   `U = k_c * convergence * g(d)` over a belt a few km wide (`g` a Gaussian of the distance to the boundary); DIVERGING, it
   thins and sinks into a rift, and basalt wells up along the axis; SLIDING past, nothing. Uplift moves the whole column:
   `base += U dt`. The seeds drift with their plates, so the belts wander. On top of the plates: a regional uplift (a
   plateau being raised -- canyons need it) and the tools' painted uplift and subsidence.
2. **Volcanism.** Hotspots (placed, or a preset's) and rift axes put out lava at a rate (m^3/yr). Lava FLOWS: down the
   surface in a few sub-iterations, stopping where the slope is below its yield (a couple of degrees); what has stopped
   cools into a basalt layer. Slow, it builds a shield; fast, it floods the lowlands into a basalt plateau.
3. **Water.** Rain `R` (m/yr) falls everywhere. The WATER SURFACE is the ground with every depression filled to the
   level where it spills (Planchon-Darboux: `W = max(H, min(W, min_neighbours W + eps))`, from above, with the base level
   and the sea as outlets): where `W > H` there is a lake, or the sea below sea level -- whose surface is sea level
   exactly, flat. Water follows `W` down its steepest direction, at ANY angle (D-infinity, Tarboton): of the 8
   triangular facets round a cell, the one the surface falls fastest across gives the direction, and the water is
   split between the facet's two neighbours (a cardinal and a diagonal) by how close the direction lies to each. So a
   river running 20 degrees off the grid runs 20 degrees off the grid, not in steps along it. A CHANNEL (discharge over
   `Qc`) is one thread: its water goes all to the side or all to the corner, which by a fixed draw per cell weighted by
   the share (Rho8) -- the same course on average, but not smeared a little wider every cell. The DISCHARGE is the rain
   gathered from everything upstream, `Q_i = R dx^2 + sum of the shares flowing in`.
   Both are relaxed a few iterations per step from the last step's, so they follow the land as it changes.
4. **Rivers: erosion and deposition** (the stream power law with sediment: SPACE / Davy-Lague). A river cuts
   `E = K * erodibility * (Q^0.5 - Qc^0.5) * S` (m/yr; `S` the slope), from the top layer down, spread over the cell and
   its neighbours (a Gaussian, 4:2:1), and never more in a step than half the drop to the next cell (in metres, whatever
   the rock); what it cuts joins its sediment flux `Qs`, which travels on down the drainage.
   WATERFALLS: a channel steeper than `fallS` (0.2) leaves its bed at the lip -- the lip wears only as a reach at
   `fallS` would, and the rest of the fall's power (times `plunge`) scours a POOL at its foot, down to half the fall's
   height, kept clear of sediment. Where the lip is hard and what lies under it soft (a basalt sill or limestone on
   sandstone) the pool undercuts it, the lip breaks off when it stands higher than its rock holds, and the fall steps
   back upstream, still a fall. Side streams hang over a valley their trunk cut faster. The stats list the falls
   (runs of such cells, highest first) and the view marks them white. Sediment settles `D = V * Qs / Q` (m/yr) -- little in a torrent, all of
   it in a lake or the sea, where the flow stops: deltas, lake beds, floodplains, the sea filling up. What settles is a
   sediment layer.
5. **Hillslopes.** Weathering turns rock at the surface into sediment, fastest where it is bare
   (`P = P0 * weathering * exp(-soil / 0.5m)`), and rain dissolves limestone. Loose sediment creeps downhill
   (diffusion). Anything steeper than its material stands (by the true slope, as the water's) slides down the steepest
   way as sediment (talus) -- cliffs hold at their rock's angle, and retreat as the rock under them goes.
6. **The coast.** WAVES attack land that faces the sea: a coastal cell is cut down at `waves * erodibility` (m/yr,
   more the more open sea round it), as far as a metre under sea level -- the cliff retreats and leaves a WAVE-CUT
   PLATFORM; what falls goes into the sea as sediment. Under water, down to WAVE BASE (15 m), the waves stir the bottom
   (less the deeper): loose sediment and a little worn rock move on to deeper water until the shelf slopes no more than
   `shelfSlope` -- a planed shelf, and the sand off it on the slope below. Soft rock retreats fast, basalt holds headlands.
7. **Sea and lakes.** Clear shallow water (under 60 m, away from rivers' mud) grows limestone (reefs, platforms).
8. **Burial.** Sediment under more than 50 m of rock and sediment becomes sandstone.

Mass is kept: what a river takes is what it lays down or carries out at the base level; the lab counts both.

## Events and presets

The SANDBOX: play, pause and speed; rain, sea level, rates; plates (how many, how fast, re-drawn, drifting); tools that
paint uplift or subsidence into the land or set down a volcano where you click. The PRESETS set the stack, the relief
and the events for a kind of land:

- **Plains** -- flat-lying sandstone and limestone, low relief, slow subsidence, rain: wide rivers, floodplains, lakes.
- **Mountain belt** -- two plates colliding across the middle: a range rises, rivers cut it into ridges and valleys,
  its waste fills the forelands.
- **Rift valley** -- plates pulling apart: a trough with lakes, basalt welling up along it, shoulders eroding.
- **Mesas and canyons** -- a layer cake of sandstone and limestone under a patchy basalt flood, raised slowly as a
  plateau that drains by two outlets: canyons grow back from them through the layers, branching, with banded walls and
  rounded heads, and leave mesas and buttes between them.
- **Volcanic island** -- a hotspot in the sea: a shield rises out of the water, rain carves its flanks, reefs of
  limestone grow round its shore.
- **River valleys** -- rolling hills, a humid climate: valleys, a river network, lakes in the hollows.
- **River country** -- 20 m cells, 2.6 km: a big river (3e8 m³/yr, 10 m³/s) from an inlet in the west to an outlet
  in the east along a winding valley between hills, a basalt sill 30 m down, the land rising 0.4 mm/yr. The game's
  maps are cut from it (mapgen.js, docs/world.md). In 150 kyr: a valley with falls where the trunk crosses the sill
  (5 m) and side streams dropping 20-90 m into it.

## The view

The terrain is drawn from the grid, coloured by height (sea blue to lowland green, upland ochre, rock grey, snow), with
the water on it (lakes and the sea at their surface, rivers where the discharge is large). The water surface comes only
from the cells that hold water, so a shore is where the ground rises through the flat surface -- it follows the land,
not the grid. Rivers are drawn from the discharge smoothed (a cubic B-spline of its log): a ribbon along the river's
course, not the staircase of cells it runs through. Or coloured by the rock: the bed the drawn surface cuts at its own
height, so the bands on a canyon wall run along it; or by discharge. Outlets show as rings. A CROSS-SECTION under it shows the columns along a line: the strata, the basement, the water.

DETAIL: the display mesh is finer than the grid (up to 8x): the grid is interpolated (bicubic) and smaller waves are
added -- fractal noise whose amplitude follows the rock and the slope (rough on steep granite and basalt, smooth on
sediment and under water). The model stays small; the picture gets dense. The upscaled height map (16-bit PNG) and the
surface material map can be saved.

## GPU

Every process is a pass over the cells (a thread a cell): nothing reads what another thread writes in the same pass,
and whatever moves between cells (water shares, sediment, lava, sliding rock) is written as outflows in one pass and
gathered as inflows in the next. The stack operations are a cell's own. About forty dispatches a step; at 256 x 256 a
step takes a millisecond or two on an integrated GPU, so the lab runs tens of steps a frame.

## Using it

Pick a PRESET (and the grid: 128, 256 or 512 cells; a seed), press play (space). Drag to orbit, right-drag always orbits,
shift-drag pans, the wheel zooms. The TOOLS act on the land under the pointer: **raise** / **lower** paint uplift or
subsidence into it (a rate, kept until cleared -- the land keeps moving there), **volcano** sets down a vent, **outlet**
sets an outlet at the edge nearest the click (or takes one away; "no outlets" makes the whole edge base level again),
**probe** puts the cross-section through the point and lists the beds there. The VIEW colours by height (relative: the land's own
range, spread over as much of the scale as its relief deserves; or absolute), by the rock at the surface, or by discharge;
vertical exaggeration, the detail waves, the mesh's resolution (1-4x the grid), contour lines. SAVE writes the upscaled
ground as a 16-bit PNG (its name carries the range in metres) and the rock at the surface as colours.

`?N=`, `?preset=`, `?seed=`; `?probe` draws offscreen and never presents (a headless browser drops its GPU instance when a
WebGPU canvas presents -- the game has the same switch).

## What building it taught (2026-09-27)

- **Channels need a head.** With every cell a river the land cut into parallel grooves a cell apart. A channel only
  where the discharge passes `Qc` (half a square kilometre of land draining through, by default) leaves hillslopes
  between the valleys, and the valleys space themselves a kilometre or two apart.
- **Symmetry breaks drainage.** A uniform uplift on a smooth plain drains in parallel lines. The crust is uneven
  (`upNoise`: the plates' uplift varies by a smooth field a few km across) and it rains more on high ground (`orog`); both
  are real, and both give branching networks.
- **Angles at the grid's scale.** A 100 m cell's slope is a hillside's, not a cliff's: the angles a material stands at
  are 27-48 degrees, not the 60-70 of a single rock face -- else nothing slides, and summits rise as rounded plateaus.
- **The rim is base level.** The domain's edge is fixed; uplift fades out over the last twelfth of the region (along a
  wavy line), so it rises as a dome with its rivers cutting in from the rim, not as a box with 500 m walls.
- **The grid shows through, five ways** (2026-09-28; the measure: the share of steep slopes facing a grid direction,
  33 % if none is preferred -- 44 % at worst on the way).
  (1) A flow rule: water sent to the lower neighbours weighted by drop^4 goes almost all to the steepest of 8
  directions, and canyons ran dead straight along the axes and diagonals -- D-infinity routing.
  (2) Slides judged along the 8 directions: a slope facing between two stood 8 % steeper than one facing along one --
  failure by the D-infinity slope, talus down that way.
  (3) Value noise: its contours run along its lattice, and the lattice ran along the grid -- basalt patches, antecedent
  valleys and soft rock came out with straight edges; gradient noise on a turned lattice.
  (4) One-cell features: a gully head a cell wide is a pit whose side neighbours (100 m) fall to it 41 % steeper than
  its diagonal ones (141 m), so heads grew along the axes and side canyons ran straight along them -- no routing rule
  cures that; spreading the cut over a Gaussian footprint of 3 x 3 cells did (the heads became rounded amphitheatres).
  (5) The edge: base level all round a square makes a square of scarps with gullies straight in from them -- outlets.
- **The water is only as good as its fill** (2026-09-28, the inlet river of river country, lost again and again):
  (1) a wall copied its inner neighbour's discharge and surface, so the steepest way down led into it and nothing came
  out -- a wall is now no one's neighbour; (2) uplift raised the ground under a lake and not its surface, and the fill
  between full refills only lowers -- lakes sank under their rising spills; the water now rises with the land;
  (3) a cell whose ground rose after the fill saw it (talus in a lake) had its surface under its ground, and its
  neighbours drained through it a sweep at a time -- surfaces are read never below their ground; (4) a delta laid up
  to a lake's surface, cut the next step, took its new ground as its surface -- a hole the lake drained through,
  metres a step -- dry land now follows its ground but never below the lowest surface round it; (5) a pit the fill has
  not reached is raised to its lowest neighbour and a step (refilling it from above instead cascaded up whole lakes,
  each cell losing its one lower neighbour to the refill, and drained them); (6) two cells at exactly one level (the
  dry rule makes such ties) pass their water to the one with the lower index, never back. The headless check: the GPU's
  lakes against an exact priority flood, 8 steps after a full refill -- 0.4 % against 0.4 %, where it had been 0.3 %
  against 5.5 %.
- **Two runs, two lands.** The dry rule, done inside the passes that change the ground, read neighbours as they were
  being written; now the passes mark the cells and a pass of its own reads one ping-pong half and writes the other.
  One seed grows the same land every time on one machine (other GPUs may round differently).
- **Throttled by a veneer.** The cap on a step's cutting (half the drop to the next cell) was reckoned in the top bed's
  terms: a few dm of loose sand (erodibility 4) on a knickpoint held the basalt under it to a tenth of its cutting, and
  the canyons stalled a kilometre or two from their outlets for 800 kyr. Reckoned in metres, they cross the plateau.
- **A river is one thread.** Split between two neighbours at every cell, a big river's water spread over the valley floor
  (its discharge jumped by 3x from cell to cell along it) and cut a shallow band; in channels it now goes one way, drawn
  per cell by the D-infinity share -- right on average, still one thread.
- **The view has a grid too.** The rock colour taken from the nearest cell's top bed drew canyon-wall bands as saw teeth,
  rivers drawn from interpolated discharge as staircases: the bed at the drawn height, and a smoothed discharge.
- **Rivers older than the land.** A plateau raised flat drains in sheets and barely cuts; the mesa preset starts with a
  few shallow winding valleys (antecedent drainage), which the rivers keep and cut into canyons.
- **Lakes, three ways wrong first.** The water surface is relaxed from the last step's, and only lowered from above, so:
  (1) a channel the river had just cut kept its old surface as a "lake" -- a cell whose surface IS its ground (exactly:
  the fill copies it) now takes the new ground; (2) the same rule applied to a shallow shore drained the whole lake a few
  cm a step through it -- hence "exactly", not "nearly"; (3) a lake took all the sediment of a step at its inlet, a mound
  tens of metres high that dammed a new hollow behind it -- a lake now fills at most up to its surface, the rest goes on
  across it (a delta grows out). New hollows the relaxation cannot raise (a sinking basin, a valley the uplift dams) are
  caught by a full fill from above every 16 steps. The headless check compares the GPU's surface with an exact priority
  flood: within 0.1 m (a step's lag).
- **Stacks keep their rock.** A full stack of 8 used to sink its lowest bed into the granite -- 220 m of sandstone turned
  basement. Then its thinnest bed merged into the one under it, of the thicker one's rock -- and a 20 m talus bed took in
  lava flow after lava flow until a ring of the volcano's core was sediment. Now the thinnest PAIR of neighbouring beds
  merges (thin beds join each other, a thick bed keeps its rock), and beds of a few cm join the one above.
- **Shores are not thresholds.** Water drawn where the cells' interpolated depth passed half a metre turned a wave-cut
  platform a metre under the sea into a chequer of cell squares; the flat surface of the wet cells, with the ground
  rising through it, draws the shore.
- **Covers are not beds.** A preset's loose top layer (soil, alluvium) drapes the surface at its own thickness; the rock
  bed under it fills the relief (else the hills were made of 300 m of loose sediment).
- **Lava is instant.** At 500-year steps lava that cooled by elapsed time never flowed; a share of what still stands
  sets each step, after a dozen flow iterations.

Lava's 25 passes a step are skipped without hotspots or plates (and 200 steps after the last). Measured headless
(SwiftShader, the CPU pretending to be a GPU): about 90-150 ms a step at 128 x 128. A real GPU is two orders
of magnitude faster; the page runs `steps a frame` of them.
