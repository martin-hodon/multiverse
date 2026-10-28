# The architecture engine

(The buildings are one of the kinds of asset in `assets/`; the definition language they share with
the creatures -- `use`, params, expressions, merging -- is described in docs/assets.md.)

A separate engine from the game's `architecture.js`: buildings described in JSON, assembled from named parts
down to arch profiles, and turned into triangles that meet **exactly**. `arch_lab.html` is its viewer.

    arch/profiles.js   the curve an opening's head follows, as mathematics
    arch/build.js      wall faces and extrusion -- where "exactly" is enforced
    arch/assemble.js   the JSON layer: params, expressions, patterns, parts
    assets/architecture/*.json   the buildings
    arch_lab.html      the viewer and the geometry's self-check

## What "exactly" means, and how it is got

Three properties, each one a thing that goes wrong in procedural architecture:

- **closed** -- every edge belongs to exactly two triangles. One means a hole; three means two pieces overlap.
- **no T-junctions** -- no vertex sits in the middle of another triangle's edge. A T-junction is not a hole in
  the mesh but it *is* a hairline crack on screen, because the two sides of it round differently.
- **the ring closes** -- turning a bay by one step lands its side face exactly on its neighbour's.

They are got by three habits. A **weld table** (a micrometre grid), so a vertex asked for twice is one vertex.
A **common cut grid**: before a wall face is triangulated, every strip is subdivided at the same set of
heights, so a pier's edge and the arch band beside it break at the same points. And a **derived boundary**:
the loops that the extrusion's sides are built from are chained out of the edges that belong to one triangle,
never declared by hand -- which is also why an opening reaching the floor needs no special case, being simply
a notch in the outer loop.

`arch_lab.html?probe=1` checks all three headless and prints where any failure is. The arena currently reads:
`244 triangles, 124 vertices, 40 instances, open edges 0, edges shared by 3+ 0, T-junctions 0`.

## The definition language

```json
{
  "params": { "bays": 40, "rOuter": 48, "wallT": 2.4, "storeyH": 10.5, "openW": 4.4, "springing": 5.6 },
  "parts": {
    "arcade": {
      "type": "ring", "count": "bays", "rOuter": "rOuter", "rInner": "rOuter - wallT",
      "height": "storeyH",
      "opening": { "width": "openW", "springing": "springing",
                   "head": { "profile": "semicircular", "seg": 24 } }
    }
  },
  "build": [{ "part": "arcade" }]
}
```

Any number may be an **expression** over the params (`"rOuter - wallT"`, `"storeyH * 0.62"`) -- parsed, not
`eval`ed: names, numbers, `+ - * /` and brackets.

**An opening is three heights**: the `sill` it starts at, the `springing` where its head begins (the top of the
straight jambs), and the crown the head reaches. An arcade is mostly jamb; a head sitting straight on the sill
is not an arch but a hole shaped like one.

**Arch profiles** (`head.profile`), all the same construction with the centres moved:

| profile | parameters | what it is |
|---|---|---|
| `semicircular` | — | one centre on the springing line: the Roman arch |
| `segmental` | `rise` | the centre below the line: a shallow arc through the same springing points |
| `horseshoe` | `over` | the centre above the line: the curve turns back in under itself |
| `pointed` | `spread` | two centres, `spread` half-widths apart: equilateral at 1, lancet above, drop below |
| `trigonal` | `rise` | two straight chamfers to a point |
| `flat` | — | a square head, so a window needs no special case |

`seg` is how many segments the curve is drawn with, and it belongs to the *definition*: two pieces meeting
along an arch must be told the same number or they cannot share its points.

**Part types**

| type | what it is |
|---|---|
| `wall` | straight, with openings given one by one or as a **pattern**: `"pattern": "2-3-2"` is three blocks of two, three and two openings, `gap` apart within a block and `pier` apart between them, and the wall's length follows from the rhythm |
| `ring` | a round storey: one bay built in its own wedge and turned, so the copies meet exactly |
| `vault` | a ring of barrel vaults over the corridor between two walls. Its cross-section *is* a wall face whose single opening spans the full width, swept between the bay's radial planes rather than extruded straight; `clears` is the height it must spring above (the crown of the arches below), and the engine refuses rather than quietly roofing across them; `place` sets it round a centre of its own, as a ring's does (Milan's ambulatories, round the apse) |
| `steps` | seating or stairs -- the same part at two scales. A stepped cross-section swept through a bay's wedge, standing on `base` and rising `out` or `in`. `every`/`offset` say which bays get it: leave every fifth bay out and those gaps are the **vomitoria**, with a narrower, finer-stepped flight (`span`, `only: "every"`) climbing in them |
| `tunnel` | the void a passage runs in, as its surfaces: `floor` and `ceiling` are each `[height at rInner, height at rOuter]`, so a stair's tunnel has its ceiling straight on the flight's slope a head's height over it, and a landing's or a level passage's is flat. `faces`: `top` the ceiling, `sides` the two walls between floor line and ceiling line, `base`, `end-in`/`end-out`. Laid out like a parallel passage (`width`), same bay selection as `steps` |
| `column` | a drum of `sides` faces (from the detail level and its radius unless named: `detailFor`) |

Steps are triangulated from their OUTLINE, not filled as a grid of cells: both are exact, but the grid spends
a triangle on every cell under the steps -- a 33-step flight costs 1,100 of them, all masonry nobody sees --
where the outline spends two per step. The arena's seating and stairs went from 68,352 triangles to 21,504
that way, with the same geometry.

## The viewer

`arch_lab.html` — W/A/S/D + Q/E to fly, pointer to look, **T** triangle edges in red, **F** flat fill, **O**
orbit, **R** reload the definition. The readout gives fps, ms/frame, the split into cpu / gpu / rest, the
triangle and vertex counts, how many instances and how many draw calls. `?def=name` picks a definition,
`?probe=1` runs the geometry check headless (`&shot=`, `&eye=x,y,z`, `&edges=1` for the picture it takes).

## Straight buildings: placement, and the barrel vault (2026-09-24)

A ring needs no placement -- being a ring IS its placement -- but a straight building is nothing without one,
so `wall` (and the new `barrel`) take **`at`: [[x, y, z, yaw], ...]**, one entry per copy, exactly as `column`
already did. A wall is measured from its MIDDLE unless it says `"center": false`, which is how a symmetrical
building is written without arithmetic on every line.

**`barrel`** is the straight vault: the same cross-section the radial `vault` carries round a ring -- an arch's
head with the masonry above it, flat on top where the floor or roof above sits -- extruded along a line.
`width`, `springing`, `top`, `length`, and `clears` (the height its springing must not fall below, so a vault
that would cut across the arches it roofs is refused rather than built).

Three smaller things the cathedrals needed:

- **A parameter may be a WORD.** `"arch": "pointed"` in the params, `"head": { "profile": "arch" }` in every
  opening, and one line turns a Roman basilica into a Gothic one. A parameter may point at another
  (`"naveArch": "arch"`), so a part follows the building's own choice unless given one of its own.
- **A pattern's block counts are expressions**: `"pattern": "bays"` rather than `"pattern": "8"`.
- **`build` may be overridden by the caller**: the village builds a cathedral's walls, roofs and towers itself
  and asks this engine only for the arcades and the vaults.
- And a failing part now says **which part** it is: a bare complaint about a wall is no help in a building of
  fifty.

**A pointed head's rise is its `spread`**, and that is what makes a vault fit a height rather than a profile
being chosen by eye: the two centres stand `spread` half-widths apart and the crown then sits
`(w/2) * sqrt(1 + 2 * spread)` over the springing -- .87 of the span at spread 1 (the equilateral arch), half
of it at spread 0 (the semicircle). So the cathedral generator solves for the spread that fits the room it
has, and only where even a semicircle is too tall does the vault become a shallow `segmental` one.

## Vaults, domes and stairs (2026-09-24)

Three part types the cathedrals and Florence needed, and one way of placing copies:

- **`groin`** -- one bay of a groin vault, which is what a Gothic bay is roofed with: two barrels crossing.
  It needs no intersection to be computed. Over the bay's plan the soffit is simply the HIGHER of the two
  barrels, `y(u, v) = max(across(u), along(v))`: at a wall one of the two is at the springing, so the other
  draws that wall's arch; on the diagonal the two are equal, and that is the groin. (The LOWER of the two is
  the cloister vault -- the dome's shape -- which is why the two look like each other's negative.) `across`
  and `along` are separate heads, because a bay is rarely square and **a groin vault's crown is set by its
  longer arch**: Florence's aisle bays are 20.3m long against a 9.5m aisle, so their longitudinal arch is a
  shallow segmental one and only the transverse arch is pointed.
- **`dome`** -- a cloister vault over a regular polygon: Brunelleschi's eight webs on eight groins. Its
  meridian is an arch profile over its own span (the *quinto acuto*, the arc struck at four fifths of the
  span, is the pointed head at spread 0.6 -- which is how it was set out), and the horizontal section at any
  height is the same polygon shrunk to that meridian's radius, so the webs are the strips between successive
  polygons and the groins are where their corners line up. Two shells, inner and outer, with `oculus` left
  open at the crown for the lantern to stand on.
- **`flight`** -- a straight run of stairs, checked like the ring's: 12-22cm rise on a tread of 25cm or more.
- **`repeat`** on any placed part -- `{ count, step: [dx, dy, dz, dyaw] }` -- so a row of vault bays, a
  colonnade or the storeys of a tower is described rather than written out. (`place` is the placement list;
  on a ring `at` already means which BAYS are the part's own, so placement there is `place` alone.)

**A stair climbs a circle, so `spiral` places it**: `{ count, radius, x, z, y, dy, dr }` puts `count` flights
round a centre, each turned to follow the tangent and raised by `dy`. Given `curve` -- the same profile the
dome's meridian is struck with -- it reads that curve's radius at each step's own height and draws in by it,
less `inset`: the climb between a dome's two shells then stays in the gap. Set out any other way (a fixed
radius, or a centre left at the origin) the flights climb straight out through the vault and end in mid-air,
which is exactly what Florence's did until it was written down.

**A dome's RIBS are a part of their own**: eight box sections carried up the groins, set out on the same rows
as the webs, and emitted as a second part so they can be another stone -- white marble against the tile.

Florence's campanile is the case that shows why stairs turn: 84.7m of stair will not go up a 14.45m room in
straight runs, so it climbs in four flights a storey, turning at every wall -- twenty flights, 414 steps.

## In the village

Two buildings are built by this engine now, through `architecture.js`:

- **The Colosseum** (`colosseum.json`, tools/archgen/colosseum.py) is the whole building: `BUILDINGS.colosseum`, on
  its four-centred oval at its real size (`arena.json`, the earlier circular amphitheatre, is kept as an example).
- **Santa Maria del Fiore** (`florence.json`) is the whole church: `BUILDINGS.florence`. Real dimensions --
  four 20.3m nave bays, an octagon 45.5m across the flats, the dome springing at 54.8m to a crown at 91m --
  with the three tribunes, the campanile and its stairs. What the engine has no part for is a timber roof, so
  the nave's gable, the aisles' lean-tos, the tower's cornice and the lantern's cone are prisms of the
  village's own kind. **The climb is continuous and it is walked on the stone itself**: eight flights round
  the crossing to the gallery at 40m, eight more round the drum to the dome's springing at 54.8m, fourteen
  between the shells to the lantern at 90m -- and twenty in the campanile, four to a storey, from a door at
  the foot to the belfry at 84.7m. A building's parts may each have their own stone (`arch.colors`, by part
  name), which is how the dome is tile between marble ribs and the tower is banded.
- **The cathedrals** take their INTERIORS from it (`basilica.json`: arcades, clerestory, nave and aisle
  vaults) while `gothicCathedral` keeps the massing -- walls, roofs, towers, spires, buttresses, the apse.
  What the arcades replaced were square piers carrying nothing under a flat slab.

`buildBuilding` bakes the parts and their instances into ONE flat-shaded mesh in the village's own stone (the
village draws a static building as a single mesh and merges it with its neighbours), and two things the
village needs come from the definition's own numbers rather than being written twice:

- **The floor is read from the stone.** `archFloorField` indexes every up-facing triangle by its place on the
  ground and answers, at a point, with every surface height there -- the sand, a step of the cavea, the vault
  over a tunnel, the deck above. Where the building has a hole (a vomitorium), it answers with nothing. A
  guessed height field is how a walker climbs a slope the building does not have.
- **The colliders are the piers alone**, at the HALF angle between two bays: a bay is centred on its own
  angle, so a collider on the bay's angle stands in the archway you can see through.

## Not there yet

A floor with a stairwell as a part of its own (the towers' top floors are written as boxes and ring bays
round their hatches), the cross-gable and other roofs that intersect each other, balustrades, and the
room/floor layers above `part`.

## What a bay is, and which bays a part stands in

A ring of sixty is not sixty of the same thing. Every part now names its bays the same way:

    "every": 5, "offset": 0          every fifth bay is LEFT OUT (the plain cavea)
    "every": 5, "only": "every"      every fifth bay is TAKEN (the vomitorium's own pieces)
    "skip": [0, 30]                  ...except these, whatever the rule said
    "at": [0, 30]                    only these

The arena reads as 48 plain bays, 10 vomitoria and 2 main entrances on the axis, and the entrances exist
because the podium substructure -- a `solid` ring, an arcade with no opening -- is absent from those bays.
An absence is a doorway; nothing has to be cut.

## Steps that start where their neighbours have got to

`steps` takes a `first`: the height of the FIRST tread above the base, where `rise` governs every one after it.
It is what lets a mass standing on a tunnel head carry seating that continues the rows outside it. Without it
a stepped mass divides its own height by its own column count and comes out half a row off its neighbours --
which is exactly what the flanking seating did before, 27 rows of 67cm beside bays of 40 rows of 45cm.

The arena's numbers are chained so nothing is approximate: the row lattice is 70.5cm because the stair's 47
steps of 30cm then measure exactly 20 rows in plan, and the rows are 45cm on a 4m podium because the stair's
47 risers of exactly 20cm then arrive at row 12. Every radius in the definition is `rArena + row * rowRun` and
every height `podium + row * rowRise`, so seating that crosses a tunnel meets the seating either side of it
at the same rows, to the micrometre the welder works at.

A key beginning with `_` in `params` is a note, not a parameter -- the reason for a number can sit next to it.

## Surfaces, not solids

Most of a building is never seen from inside its own masonry. A part now says which of its surfaces to emit:

    "faces": ["top"]                  the treads and risers of a stepped mass
    "faces": ["top", "base"]          ...and the flat underside, which is a tunnel's soffit
    "faces": ["top", "sides"]         ...and the two ends of the sweep -- a passage's side walls
    "faces": ["end-in"]               the vertical at the near end (the two ends are named separately,
                                      because two pieces meeting end to end must not both draw the face
                                      between them: that is how you get z-fighting out of exact geometry)

A part built this way is a SHELL. It has boundary edges by design, and the self-check reports them as boundary
rather than as holes -- but everything else still holds: no T-junction, no edge used by three triangles, the
ring still closing exactly under rotation. The arena's whole cavea is four triangles per row per bay.

## How a cross-section is carried round: `plan`

    wedge (default)   swept between the bay's two radial planes -- seating, arcades, vaults
    parallel          run out along ONE ray at a fixed width -- a passage, which must not fan out to half
                      again its width at the facade; its width is the arch it comes through
    flank             the seating beside such a passage: bay plane on one side, passage wall on the other
    along             climbing ALONG the ring instead of across it

`along` carries a landing round the ring. The stair between storeys is a SWITCHBACK, and it lies entirely
PAST the arcade: level out of the ambulatory through one arch, then 28 risers of 20cm climbing inward inside
the cavea's own mass to a landing halfway up, then 27 back outward in the next bay, arriving at the floor above
exactly at the face of the cavea. So the ambulatory keeps its vault and its arches unbroken all the way round.

Two things that only arithmetic gets right. The return flight has one riser fewer than the first -- 28 + 27 of
20cm is the 11m storey -- so its treads are 31cm rather than 30, which is what makes both halves span the same
8.4m and land the top ON the floor instead of a step short of it. And a landing belongs to no single bay: it
straddles the two its flights climb in, so a part may be `turn`ed by half a bay, and its arc must be a bay PLUS
a flight's width -- a landing one bay wide reaches only the flights' centre lines and leaves half of each of
them hanging in the air.

A stepped cross-section's own sides stop at the treads, so they are not the walls of the stairwell: the wall
above a stair is a separate piece, floor to soffit. The landing's back and ends are walls too, but its front is
where the flights arrive, which is why a part can emit one side of its sweep (`side-in`, `side-out`) and not
both -- only the strip between the two flights is walled.

## An oval of four centres: `oval`

A Roman amphitheatre is not a circle and not an ellipse: it is set out from FOUR CENTRES, two end arcs about
(±c, 0) and two flatter side arcs about (0, ±d), meeting where the radii through the centres cross -- so every ring
of the building is an offset of the same four arcs, and a radial plane is straight through each. A `ring`, `vault`,
`steps` or `tunnel` part takes `oval: { c, d, ends, sides }` (bays in an end arc, in a side arc; odd, so a bay sits
on each axis) and its radii as the END arcs' (a side arc's are K = hypot(c, d) more). The part is built twice, as a
ring of the end arcs' bay angle and one of the side arcs', each copy turned and moved onto its arc's centre; the
side arcs' parts are named `"<name> 2"` (a finish rule for the name matches both). Bays are numbered as in a ring:
bay 0 on the +x axis, then on toward -z, `every`/`only`/`skip`/`at` choosing among all of them (assemble.js
ovalOf). The Colosseum's 15 + 25 bays a quarter are solved for equal bays on the facade (6.75m), which puts the
arena's end arcs at 15m radius -- an oval, not a lemon.

## Seating that ends on a walkway, a mass with a sloping underside, a stair cut as steps

`steps` takes `landing`: the last tread carried on that far past `rOuter` -- the walkway (praecinctio) behind a
maenianum's top row, and the mass under it, in one piece with the rows. `soffit: [yIn, yOut]` gives it a sloping
underside instead of a flat `base` (heights absolute, as `base` is): the seating over a stair that climbs under
it, the stair's headroom kept under the whole of it. And `use: "stair"` -- besides holding the rise and the tread
to what feet can climb -- gives the part a walking line, every tread's middle and width and the foot it is
stepped onto, as a `flight` has: the walk ramps it (its risers are not walls: three of them within a stride are
a wall's height, and the climb stopped there), the stair check asks its headroom and arrival, and its open sides
are railed.

## Two lessons from the arena's mouths and floors

**A wedge and a passage do not end on the same line.** A wedge's outer edge is the chord between its bay's two
radial planes -- at 40m that chord lies 5cm inside the radius it is named for -- while a parallel passage and
the seating flanking it start at the radius itself, square to the passage. Put a wedge of seating below a
vomitorium's mouth and a sliver of daylight opens between its last row and the top of the stair. So a bay with a
passage in it is built from `flank` pieces and a `parallel` piece all the way down to the arena, never from a
wedge: their edges are the same lines by construction.

**The top edge of a wall is a floor.** `wallFace` used to give every segment of an arch's curve its own piece of
masonry running up to the top of the wall, which cut the top edge once per segment -- and the top edge, extruded,
is the flat extrados of a vault or the top of an arcade. Arch `detail` therefore multiplied every flat floor in
the building. The masonry over a head is now two fans from ONE point on the top edge, over the crown (any convex
head is in plain sight from there), so the top edge is cut once per opening whatever the detail.


## Florence: which way a tribune faces, and where the church stands (2026-09-25)

Three lessons from finishing Santa Maria del Fiore, all of the same kind -- a number written twice.

**A ring's bays face where the place's yaw puts them.** A tribune is five bays of a ten-bay ring
(`skip: [0,1,2,8,9]`), and the five that are built are the ones centred on bay 5, a half turn from the place's
own yaw. The two side tribunes carried the yaws the wrong way round, so their arcades swept INTO the crossing
and their open side faced the fields -- which no picture of the east end shows and no measurement had been
asked for. `ref/trib.html` asks it now: for every bay, does it face away from the crossing?

**The marble and the roofs follow the tribune, not a copy of it.** The courses round a tribune were drawn as
full rings, so half of each hung in the air beside the church; the terrace and the cone over it are half rounds
too. They all come off one list in `architecture.js` (`TRIB`, the three seats with the yaw that points away
from the crossing) and are drawn as ARCS: `cyl` takes `a0` and `span` now, as CylinderGeometry always could.
A sector's edges are radial, so exactly half a round is a roof whose open side is the tribune's own diameter --
which is where the octagon's wall stands. Swept any further it pushes through the drum.

**A building stands in the middle of its site.** The world flattens the ground and keeps trees off a box
centred on the site, and Florence is set out from the middle of its NAVE -- with 43 m of church in front of
that point and 113 m behind. Trees grew through the apse. `zc` slides the whole church forward by half the
difference (it was already there for the nave; the crossing, the tower and the west front use it now too), and
the footprint is the true span about that middle.

**A door in the wall is not a door in the collider.** The tower's walls were four boxes, so Giotto's campanile
had 414 steps and no way in, and the facade's collider had one hole where the drawn facade has three portals.
The doors are named params in `florence.json` (`campDoorW`, `wingDoorW`, ...) and the colliders cut the same
holes from the same numbers. `ref/doors.html` walks each doorway and each blind wall between them, through the
game's own `collides()`.


## The masonry over a head, and what "in plain sight" cost (2026-09-25)

The face of a wall is triangulated by hand, and the piece over an opening -- between the head's curve and the
top edge -- was two FANS from one point on the top edge. The reason was sound: the top edge, extruded, is a
FLOOR (a vault's extrados, the top of an arcade wall), and giving every curve segment its own quad cuts that
edge once per segment, so every floor in the building multiplies with the arches' detail.

But a fan is only valid when every corner of the piece is in plain sight from its apex, and for a ROUND head
it is not: the chord from a point above the crown to a springing point passes INSIDE the curve. So the fan's
own rays cut across the arch, the shoulders came out as missing triangles, and a semicircular opening was
drawn as a coarse polygon with the arc floating inside it -- while the soffit behind it, swept from the same
curve, was smooth. That is what "the face does not follow the arch" was.

The piece is ONE polygon now -- along the curve, up the far side (broken at the cuts, because that vertical
stands against a pier whose edge is broken there too), across the top, down the near side -- and it is
EAR-CLIPPED, which is valid for any simple polygon and adds no vertex at all. The top edge is still cut once
per opening.

**A head may also overhang its jambs.** A horseshoe comes back in under itself, so the opening is wider above
the springing than the straight sides are, and the polygon touched its own edge at the bulge -- a pinch point,
where ear clipping has nothing to bite. The jambs stay put, the opening's SPAN grows to whatever the curve
reaches (plus a millimetre, so the shoulder beside it is a sliver and not a pinch), and the shoulder below the
springing is filled solid: which is what a horseshoe arch is built as.

Checked with the lab's own probe (`arch_lab.html?probe=1`) on the arena, the basilica and Florence: 0 open
edges, 0 T-junctions, 0 edges shared by three triangles -- the engine's three promises, unchanged.


## Triangles that were never needed (2026-09-25)

Two of them, both the same mistake: spending detail where there is no shape.

**A cut belongs to its opening, not to the wall.** A vertical is broken at a height for ONE reason: the edge
it stands against is broken there, and if it is not the two meet as one long edge against several short ones
-- a T-junction. That was implemented as a grid over the whole face: every solid strip cut at every opening's
sill, springing and crown, wherever they were. A pier between two openings carries their cuts on the sides
that touch them and nothing in between now, and a stretch of wall with no opening in it is ONE polygon
whatever its height. (Ear-clipped, so the sides keep the vertices they must have and the inside is the fewest
triangles that polygon can be.)

**A groin's grid follows its curves.** The soffit was sampled on a square grid, so a bay that is round across
and nearly flat along spent as many rows on the flat direction as on the round one. Each direction takes the
stations its own profile has -- which the profile library already gives by ARC, so a shallow segmental head
gets fewer points than a semicircle.

Measured, with the lab's probe still reporting 0 open edges, 0 T-junctions and 0 edges shared by three
triangles: the arena 56,580 -> 52,740 triangles, Florence 18,252 -> 16,844, and the cathedral interiors (whose
vaults are groins) Cologne 11,748 -> 8,364, Notre-Dame 10,918 -> 5,326, Milan 15,068 -> 10,812.

**...and a groin springs from the same arch both ways.** One `head` serves both directions unless they are
given separately: two different profiles no longer meet at one crown, and the vault reads as two mismatched
halves. Over an OBLONG bay the flatter span keeps the crown by taking a segmental head with its rise written
out, which is what the cathedrals' definitions do.


## Webs, profiles, domes of every kind, roofs, stairs that fly, coffers and the orders (2026-09-26)

**The groin vault is four webs.** Split the bay by its diagonals and each triangle is ONE web: the barrel that
springs from that wall, its edge on the wall being that wall's arch point for point, running in straight lines
to the groins. Where the two arches rise alike the webs are level; where one crown is lower its web ramps up
to the groin, which is set by the HIGHER of the two (a builder stilts the lower arch). The groins are where two
webs meet, so their points are made once -- from both arches' stations together, snapped to one list (two
stations a tenth of a millimetre apart are one point), always including the middle of the bay -- and both webs
use them. The crease is an edge of the mesh now, not something a grid cell folds across. Checked closed, no
T-junction, at detail 2 to 16, on Florence, the basilica and an oblong bay with unequal crowns.

**Arch profiles with more than one centre turned against each other:** `ogee` (an S of two radii: convex, then
concave to a point), `onion` (the same S swelling out past its springing first -- `bulge` is the first radius,
`neck` the second, in half-widths, and those two numbers fix the height), `trefoil` (three `lobe`s meeting in
cusps) and `inflexed` (two arcs bowing inward to a point, `rise` and `bow`).

**A dome is an arch turned about its axis**, so every profile is a dome: hemisphere, lowered (`segmental`),
pointed, horseshoe, onion, bell (`ogee`), cone (`trigonal`), flared spire (`inflexed`). `sides` a number is a
cloister vault of that many webs (Florence's 8); left out, the dome is ROUND and its facets follow the detail
level. `thickness` 0 is a SKIN -- the way a roof is built, closed by a disc underneath. `sweep` .5 is a
SEMIDOME, the conch over an apse, closed along its cut (a skin by the flat of its profile: a half-cone roof
against a wall). Two faults fixed on the way: the meridian used to stop at the last sample outside the oculus
and run in FLAT, laying the inner and outer shells over each other at the crown; and a dome closed at its
crown had an inner shell 2cm wide at the tip's own height, poking through it (it is now the outer one scaled
in by the thickness both ways).

**Ribs are laid ON a dome, not built into it:** a `ribs` part names the dome it stands `on` and takes that
dome's meridian, sides and placement, so the two cannot disagree. A plain dome has none; Florence adds its
eight (`florence.json` "dome ribs"), standing on the GROINS now -- they used to stand on the middle of each web.

**Roofs are stacks of rectangles** (`roof`, `form`): eave, any break line, ridge, joined side to side; a side
that comes in between two levels is a slope and one that does not is a gable. flat, shed, gable, hip,
pyramid, mansard, gambrel, jerkinhead, gablet, saltbox -- one function, and each form is only its levels.
`overhang` carries the eave out and down its own slope (every sloped side as far as makes one level eave) and
the verge out over a gable. Tower roofs are dome skins: `assets/architecture/elements/roofs.json` has both.

**Stairs that fly.** `flightFace` is a flight's side profile with a sloped SOFFIT parallel to its pitch, cut
into one pentagon per step so a helical map can bend it. `spiral-stair` winds it round a newel (tread measured
on the walking line, `hand` left or right -- the mirror is undone by swapping the two sides -- headroom
checked, `post` optional). `staircase` is a WALK: a flight, the landing it arrives on, and the flights leaving
that landing `ahead`, `left`, `right` or `back` beside the one that came, each with its own landing and flights;
`times` repeats a flight-and-landing, which is how a square tower's stair goes round its well storey after
storey. Where a flight meets a landing the two are one piece of stone: the landing's outline is broken at the
flight's corners and neither draws the face between them.

**Coffers are cut into a surface** (build.js `cofferedSurface`): over any S(u, v), a frame left at the surface
and a pocket sunk behind it in `steps` (one by default). The cell edges carry every station on them, so the
plain surface round the field meets it exactly. A dome takes `coffers` on its soffit (`count`, `rows`, `from`,
`to` along the inner meridian); `coffered-ceiling` is the flat case. `toward` sinks the pockets along the line
of sight from a point on the axis -- the Pantheon's are aimed at a standing eye in the middle of its floor, so
from there no coffer shows its sides.

**The orders:** `colonnade` is columns (base, tapered shaft, capital and abacus) and their entablature, STRAIGHT
at a spacing or ROUND on a radius (a whole ring, or an `arc` with a column at each end); `box` is the block
podiums, courses and entablatures are made of; `column` takes a `taper`, and one `drum` builds every round shaft.

**New assets:** elements `dome` (a gallery of every profile), `dome-ribbed`, `semidome`, `roofs`, `staircases`,
`towers` (a square tower with its stair round the well, a round one with a spiral), `colonnades`, `stoa`,
`rotunda` (a tempietto), `coffers`; and `pantheon.json`, the whole building at its real size -- a 43.3m rotunda
with eight niches, the drum and its step rings, the coffered hemisphere with its 9m oculus, the intermediate
block and the portico of sixteen columns under its pediment.

**Two old faults found by the new checks.** `extrude` turned every opening's REVEAL to face into the stone (a
face's border edges run with the masonry on the same side whether they bound the outside or a hole, and holes
were flipped a second time); and `column` was wound inside out. Neither showed, because the materials are
double-sided; both are right now. The floor field reads `|ny|`, so neither change moved a floor.

The headless check used for all this builds each definition and counts open edges, edges shared by three
triangles, T-junctions and the signed volume (positive = wound outward); every part of every new asset reads
closed, 0, 0, positive -- except the spiral stair with a post, whose inner ends are left open inside the newel
by design.

**The towers are fitted to their stairs** (`elements/towers.json`, generated arithmetic written out as data).
A stair ends ON something: the square tower's last landing is flush with a top floor that is cut away only
where the last flight and a half need headroom (2m under the slab), and the round tower's floor is a ring of
one bay per step of the spiral with the thirteen over its last steps left out -- the hatch it comes up
through. And a window belongs where the stair STOPS: the square tower's walls are built in pieces that begin
at the landings, so each landing has a slit window beside it and none falls halfway up a flight; the round
tower's windows are staggered up the helix, each in the bay the stair is passing, a metre over the tread.


## Temples, the orders, pendentives, rib vaults and the pieces before 1800 (2026-09-26, later)

**The orders are data** (`assemble.js ORDERS`): each is proportions of the shaft's radius -- base, capital,
abacus, the flare of the echinus or the bell, the taper -- and `volutes` for the Ionic. `colonnade` takes
`order`, and anything given outright wins over it; `shaft: "square"` makes pilasters and piers. A colonnade can
now be a PERISTYLE (`front` by `side` columns round a rectangle, the corners counted in both, the side columns
turned to face out), and its entablature is architrave and frieze (`h`), a CORNICE standing `out` proud of
them, and Doric TRIGLYPHS over every column and every gap -- one box drawn as many times as there are (the
Parthenon's ninety-six). Round a peristyle the entablature is a FRAME (build.js `frame`), a ring beam.
**`crepidoma`** is the stepped platform, one solid (the roof's stack of rectangles, `roofMesh`).

**The temples are assets now**, built from those components at their real sizes: `hephaestus.json` and
`parthenon.json` -- crepidoma, Doric peristyle with its triglyph frieze and cornice, the cella with its door,
porches of columns before and behind it, a coffered ceiling inside the entablature, one gable whose ends are
the pediments, acroteria. (The village still draws its temples with `architecture.js greekTemple`; they can be
moved onto these definitions the way the arena and Florence were.)

**The Pantheon got what it was missing**: the interior order (six exedrae each screened by two Corinthian
columns, the entablature they carry round the room, broken over the entrance and the apse), eight aediculae
between them (podium, two columns, a pediment -- placed by `spiral`), the attic zone with a blind window in
every bay (an inner ring cut through, a solid one behind it), the podium steps and the raised floor, Corinthian
columns and a cornice on the portico, and the cornices banding the drum. A wall STANDS ON a floor rather than
beside it: a floor's edge against a wall's face is two faces in one place, and they fight.

**Pendentives** (build.js `pendentives`): four arches over a square, and between them the spherical triangles of
the ONE sphere through the square's corners, cut level at the circle inscribed in the square -- the dome's
springing. Their stations are a dome's with its corners on the axes, so a dome `turn`ed by -0.5 (new: `turn`
on a dome) and a ring of windows turned by half a bay meet them point for point. Left whole, the same sphere is
the **sail vault** (`sail: true`). **Rib vaults**: `ribs` laid `on` a groin vault follow its groins (and with
`wall` its arches), set out from `groinGeometry` -- the numbers the vault itself is built from. Every rib in
the engine is now one function, `ribAlong` (a box section along a path of framed points).

**`elements/byzantine.json`** is what Hagia Sophia is made of, at a third of its size: piers, great arches,
pendentives, a ring of forty windows, a shallow dome of forty ribs, a semidome on its half ring of windows, an
exedra; and the vaults of a square bay side by side -- sail, cloister, rib. **`elements/details.json`**:
battlements on a wall and round a tower, a balustrade, an obelisk with its pyramidion, stepped buttresses with
weatherings, an Ottoman minaret, a window aedicula, a Romanesque portal in recessed orders.
**`elements/towers.json`** has a third tower: the viewing tower, whose stair arrives in a top room with a door
onto a GALLERY round the outside, on corbels, behind a parapet. **`elements/orders.json`**: the four orders side
by side, and pilasters.

Checked: all twenty-six architecture assets, 415 parts, closed or declared shells, no T-junction, no edge
shared by three triangles, none wound inward, at detail 4 and 8.


## Components, walls round plans, and five famous buildings (2026-09-26, evening)

**A building may use another building.** A `component` part names a definition (`use`, a path under
`assets/architecture`), gives it params as expressions over the caller's own, may pick some of its parts
(`build`), and places everything it makes at each of its own placements (`at`, `repeat`, `spiral`). The
definitions live in a library: `registerDocs` fills it (the game imports the JSON -- Florence's `iwan`), and
`loadUses` fetches what a definition asks for, all the way down (assets.html, arch_lab.html). Components nest: a
minaret carries a chhatri. `assets/architecture/components/` holds them, each written once:

    chhatri          the domed kiosk: platform, columns, eave, drum, onion, finial
    minaret          plinth, shaft, `balconies` balconies spaced up it, and a chhatri (or a pencil cap) on top
    iwan             the back of a deep arched recess: half cylinder, pointed semidome whose section is the arch's
    domed-tower      polygon tower, kokoshniki, drum and a cap of ANY profile (`cap`: onion / bell / trigonal),
                     optional ribs on the cap -- St Basil's chapels and tent, the Frauenkirche's towers, a flèche
    gallery          a one-storey wing of arched windows with a terrace roof and balustrades
    curved-gallery   the same round an arc (`range` of a ring's bays)
    pavilion         two storeys -- an arcade below, tall windows above -- under a mansard
    pinnacle         shaft, four-sided spire, finial
    flying-buttress  pier, pinnacle, and the flyer to the clerestory

**Walls round any plan** (`enclosure`): a rectangle, a chamfered rectangle or a regular polygon (build.js
`planPoints`), each edge a wall face with its own openings, the faces meeting on their mitres. Every edge has a
LABEL ("main", "chamfer", "side") and a plan may SPLIT the edges of a label into segments ("main:0", "main:1"...),
so a facade is flank, centre bay and flank; `faces` addresses faces by number, label or family. The inner face
of a thick wall runs PARALLEL through the middle of each face and takes up the mitre only at its ends, so a
reveal goes straight through: the Taj Mahal's iwans are the reveals of a 5m wall. `prism` is the solid on the
same plans.

**A face in tiers.** `wallFace` cuts a face into vertical strips, so it cannot stand a window over a door. A
face may now be `tiers` -- bands stacked from the ground, each with its own openings -- and where two bands meet
the joint is not drawn and is ONE edge on both sides: `wallFace` takes `topCuts`/`bottomCuts` (points its top and
bottom edges must carry) and `endCuts` (heights its end verticals must carry, so a tiered face meets an untiered
neighbour round a corner). Both `wall` and `enclosure` take tiers.

**An opening may have a FOOT**: a second profile below its sill, drawn downward -- a round window is a
semicircular head over a semicircular foot (Florence's drum oculi, Notre-Dame's roses); a trefoil foot cusps a
window's bottom. Every part that makes openings goes through one `openingOf`, so every one takes a foot.

**The `bell` profile**: concave below its WAIST, convex above it, vertical where it turns -- `waist` (how far out)
and `lift` (how high) say the whole shape. The Frauenkirche's stone bell. **`flyer`**: a strut on a rampant
quarter-arch from a pier to a wall.

**The buildings**, all at their real sizes, and each made mostly of components:

- `st-basil.json` -- nine `domed-tower`s at five sizes (the central tent with a small tower on its tip, four
  great ribbed onions on the axes, four smaller on the diagonals) and the belfry, on a platform with a gallery
  whose main faces are SPLIT for a door in each.
- `taj-mahal.json` -- the tomb's 5m walls round a chamfered, split plan, every iwan an opening closed by the
  `iwan` component, two tiers of them on the flanks and chamfers; parapet, pishtaq crowns, drum, onion, finial;
  four `chhatri`s on the roof, four `minaret`s on the plinth.
- `frauenkirche.json` -- a chamfered square in two tiers of arched windows with a portal in each side, the choir
  apse, a mansard, the windowed drum, the stone bell, its lantern and four corner towers (`domed-tower`s with bells).
- `zwinger.json` -- `gallery` wings, two `curved-gallery` ends, six `pavilion`s, and the Kronentor under an onion
  on a SQUARE plan (a dome of four sides) with its lantern.
- `notre-dame.json` -- its nave IS `basilica.json` used as a component (pointed arcades, clerestory, aisle walls,
  rib vaults -- the arch along a bay a lancet that meets the crown of the wide one); `flying-buttress`es down both
  flanks and radiating round the chevet; the west front in three tiers under two towers; the transept's roses;
  the apse, its half vault and roofs; the flèche.

**Florence is whole in its definition now.** The roofs the game used to draw as prisms (nave, aisles, the half
cones over the tribunes, the lantern's cone and ball) are `roof` and `dome` parts in florence.json, and the game
no longer draws them; the drum has its eight round oculi; the four tribune morte stand against the octagon's
diagonal faces (the `iwan` component with a round hood); the lantern has its eight radiating buttresses
(`flyer`s); the campanile its cornice. The game still draws the pavement, the marble courses and the colliders.
**The Gothic interiors** (`basilica.json`, used by the game for Cologne, Notre-Dame and Milan) have RIB VAULTS:
ribs along the groins and on the arches of every bay, nave and aisles.

Checked: forty-one architecture assets and components, 661 parts, closed or declared shells, no T-junction, no
edge shared by three triangles, none wound inward, at detail 4 and 8; the game's catalogue builds (Florence
17,714 triangles). The generators are `tools/archgen/*.py`.


## Walkable, and in the game (2026-09-26, night)

**The game builds from the definitions.** `architecture.js archBuilding(doc)` turns any definition into a site: its
mesh (coloured by part name, a component's part by its own name, or by KIND -- `kind:dome`, `kind:roof`,
`kind:ribs`...), its FLOORS read from its own geometry (`archFloorField`: every up-facing triangle -- the base,
stairs, landings, terraces, roofs), and its WALLS read the same way (`archWallField`): every near-vertical triangle
is sampled onto a 0.4m grid and each cell keeps the heights its stone spans, so a walker is blocked where there is
stone between knee and head, and a doorway, an arch or a window leaves its own gap with nothing written by hand
(index.html `collides` samples the walker's circle against it). It is centred on its site by the rectangle round
what it built. The Pantheon, the Taj Mahal, St Basil's, the Frauenkirche, the Zwinger, Notre-Dame, Cologne and Milan
are such sites, and the temples of Hephaestus and the Parthenon are their definitions now rather than code.

**Three buildings a world.** The catalogue is FACTORIES (`BUILDINGS` builds an entry the first time it is read), and
index.html picks three of `LANDMARKS` at random -- `?seed=` (written into the address if absent, so a shared link
opens the same world), or `?building=a,b` outright -- and lays them out in a row, facades on one line, each on its
own flattened rectangle with 40m of open ground to the next.

**A base under every building.** A definition's `base: { height, steps, stepOut, margin, plan }` is a platform built
first and everything lifted onto it; without a `plan` it is the rectangle round what the building built, `margin`
out, stepped (one solid, `stackMesh`). The Zwinger, the Frauenkirche, Notre-Dame, Cologne, Milan and Florence have
one (the game asks Florence without it -- `base: false` -- since it lays its own pavement).

**`atop`**: a part stands on another part's top -- a dome's crown (its placement plus its meridian's rise) or
anything with a height. The finials of `domed-tower` and `chhatri` are set this way; St Basil's lanterns on the
tents' tips are set where the tent has narrowed to their width (tools/archgen/shapes.py: the profiles' arithmetic).

**What is walked, building by building:**
- Zwinger: each `pavilion` has a dog-leg stair to its upper floor, level with the gallery terraces, and doors
  onto them; the terraces are floors behind their balustrades.
- Taj Mahal: a flight up the plinth; the great iwans' backs have doors into the tomb (the `iwan` back is cut so a
  bay is centred on its axis: `back door`).
- St Basil's: the platform's flight and gallery doors; every `domed-tower` has a door at its foot (a lower tier).
- Frauenkirche: the galleries (Emporen) round the inside -- the `enclosure` again, deep and thin -- and a flight
  up to them.
- Notre-Dame and Cologne (one generator, `tools/archgen/notre_dame.py gothic`): a spiral turret in each tower from
  the aisle to the tower's terrace, which is a floor round the turret's hatch; Cologne's spires stand on it.
- Milan: spiral turrets inside the facade to the outer aisles' flat terraces, a flight on up to the inner ones -- its aisle roofs are walked, under the flyers.
- Karlskirche: a flight up the back wall of each side hall to its gate pavilion's belfry floor, a door through both
  walls at its head.
- The temples: a flight up the east front (the Parthenon's steps are half a metre, the climb limit).

**Fixes on the way.** Florence's tribunes stood 1.85m short of the octagon and the sky showed past their ends: a
tribune now stands on the octagon's face (`tribD`, one param the game reads too) and a spandrel fills the wedge
beside each end. The clerestory now rises to the vault's top, closing the lunettes (the Gothic interiors had sky
behind every wall arch). A wall rib hangs on its own bay's side of the arch -- it poked out through the vault's side
wall, and two bays' transverse ribs lay on top of each other. An ambulatory's lean-to is a half cone cut off at
the apse's wall (`oculus`, `cap: false`), not one reaching across the apse. A masonry part-dome is a VAULT (stone),
not a dome (a roof's colour). Ribs stop short of a dome's tip, where they all met.

Checked: forty-three architecture assets and components, 804 parts, clean at detail 4 and 8; the game with seeds
1-4 and with named buildings (floors, wall-field probes: doorways open, walls blocking, terraces walkable).

## Stairs checked, glass, and five more buildings (2026-09-26, late)

**Every stair is checked** (`arch/check.js stairClearance`): each stair part carries its walking PATH (every tread's
middle and every landing's, with its width) and its FOOT; against every other part -- and every other COPY of
itself, so a stair repeated storey over storey stands on the one below -- it must have 2m clear over every tread,
no tread inside another part's solid (an odd count of crossings up from it), and a floor under its foot. A flight
arrives on a landing unless it says `landing: 0` (it arrives on a floor of its own); `walk: false` is stepped stone
that is not a way up (a balustrade). All fifty definitions pass.
A straight flight with a `soffit` has ONE underside quad (build.js flightFace `whole`: its section fanned from the
soffit's high corner), not one a step; a spiral keeps a station a step (its soffit bends). The headroom is asked at
the tread's very edges too (a walker's shoulder reaches them), there only of what hangs over (undersides).
A straight flight also has its APPROACH (2026-10-03): before its first riser, a strip as deep as the flight is wide
(2m at most for a broad one) must be floor and as clear -- room to stand and begin the climb, not a wall, a barrel, a
bin (item parts count as solids in the check). A copy that begins on another copy's top (a tread of a stair wound
round a wall) is mid-climb: neither its foot nor its approach is asked. Accepted findings: Chichen Itza's stairs (the
approach steps 30cm off its base platform), the landing's stair down into the water, and the older pit-house,
pueblo and Florence findings.

**A stair is walked as a slope** (`architecture.js stairRamps`): in the floor field its treads are replaced by a ramp
through their middles, half a tread past each end, so running and landing from a jump find one surface. And a jump
lands on a floor up to a step above where the fall started (index.html), so a stair rising under the feet catches
them.

**Glass is declared, not guessed.** An opening's `glass: true|false` is said once for a kind of opening: on an
openings spec (a pattern or a list entry), on a TIER, or on the PART -- the most particular wins; said nowhere, an
opening with a sill over 30cm is a window. The flag may be an expression (`domed-tower`'s `glazed` param: 0 for an
open belfry). Open belfries, galleries, loggias, iwans, the Pantheon's niches say `glass: false`.

**The engine, a little more general:**
- expressions know `min`, `max`, `floor`, `ceil`, `round` (expr.js) -- a count that follows the detail level but
  stays within what the shape allows (the iwan's back and hood are ONE polygon of `sides`, at most as many bays as
  leave the door room);
- a `repeat` count may be 0 (a one-storey wing has no storeys above); a `spiral` placement may go round `turns`
  times (a band wound up a column);
- a `crepidoma` may lean its steps in (`batter`: a Maya pyramid's talud); a flight may be `steep` (30cm on 22cm);
- a roof's `form`, like a profile, may name a param (`"form": "roofForm"`);
- a prism's caps are ear-clipped, so its plan may be concave (a floor round a half ring);
- a door in an upper tier stands on the tier below, whose top is drawn there as its threshold;
- colours: a part's own name, its name less a trailing number ("aisle roof 3"), its name inside a component, the
  component's name, its kind.

**`palace-wing`** (components/): the block every palace, abbey and castle is made of -- `n` storeys of `H` on
`L` x `D`, a window every `axis` metres, the ground storey's +z face doors or windows, floors, a dog-leg stair to
every storey (`stairAt` sets it in from the end, clear of a neighbouring wing), a roof of any form. Walked through.

**New buildings:** Hagia Sophia (the Byzantine kit at full size: dome on pendentives and forty windows, semidomes
over two-storey half-ring arcades, tympana, galleries over the aisles reached by stairs along the outer walls,
narthex, apse, buttresses, minarets); Stift Melk (four wings round the Prälatenhof, the church with its twin towers
and the dome on pendentives over the crossing, the terrace between two wings closed by the curved Altane); Schloss
Schwerin (wings round a pentagonal court, a tower over every corner, the gate tower with its gilded dome, the lake
as a moat and the bridge); the Karlskirche (round church, drum and tall dome, the portico, two giant columns with
their wound bands, gate pavilions); Chichen Itza (nine battered terraces, four steep stairs of 91 steps, the
temple). Generators in tools/archgen (hagia_sophia, melk, schwerin, karlskirche, chichen_itza).

**Fixes:** Cologne's octagon stages and spires are nearly the towers' width (the stair turrets moved to the towers'
outer flanks, out of the octagon's way) with a pinnacle on every corner; Milan's front is one gable (its buttresses
and pinnacles climb with the slope) and the flank rows stop a bay short of it (they doubled its pinnacles).

## Nothing on air, courts, and three more buildings (2026-09-26, later still)

**Everything is carried to the ground** (`arch/check.js floating`). Every copy of every part must stand on the
ground or be held -- resting on another part (a point of its underside, sampled every 40cm, lies on that part's
surface or inside its solid), hanging from one (the same for its top), or fixed to one at the side (a corner of it
touches its surface: a flyer against its pier) -- by something that is itself carried, all the way down. Two parts
holding each other up in the air (a drum and the cap on it, the neck they should stand on left out) are found. A
shell (a dome's skin) holds what passes through it; "inside" is counted over all copies of a part (a ring's bays
are open slices). The check page prints it beside the stairs: `SUPPORT <def>: n floating`.

**A part says what it stands on**: `standsOn: ["neck"]` -- asking for it builds that too. The `domed-tower`'s parts
are chained so (tower <- head <- neck <- drum <- cornice <- cap <- finial): a caller that picks the cap cannot leave
its supports out. The tower's head is now a floor closing the hollow tower (the neck used to hang over the hollow),
and a cornice round the drum's top carries a cap wider than its drum.

**`atopR`**: a part set `atop` a dome stands where the dome has narrowed to that radius -- a lantern on a pointed or
onion dome sits on its surface, not on its tip (the Python generators no longer work this out themselves).

**Statues** (2026-10-04, `statues.js`, `tools/archgen/statuary.py`): a `statue` marker -- { kind, pose (stand | guard |
sit), style (greek | roman | gothic | chinese) or outfit, hold { R, L } (items, carved too), stone (marble | bronze | gold
| limestone), scale (x a person), seed, face } -- is a carved FIGURE: the people engine's own, every part, its cloth, its
mesh head and what it holds marked stone (skeleton.js `stone`, composite flags 2048 x the material; shell.js `stoneAt`
paints it in a world-space grain under the world's Lambert, the metals with the sun's highlight; `stoneMaterial` for
the head and the items, tools.js `@stone<m>`, held items scaled with the figure). Carved cloth is FULL: every
garment cut closed (its clip `solid`: the hem, a sleeve's mouth) and a standing piece filled where no layer lies -- real
cloth is a shell open at its edges. A pediment's figures FIT ITS TRIANGLE (temples.py pediment_figures): each sized by
the clear height at its outer edge, standing in the middle third facing out, seated further out turned toward the middle
and the front, reclining along the floor in the corners. Pedestals are the definition's own
boxes (`statuary.pedestal`); at most 50 a building (`statuary.capped`: the first listed are the most prominent). The
game stands them in one herd (index.html statueHerd, `?statues=0` none); the asset viewer shows them with the building
(lifeOf, as the game reads them). Placed: the Parthenon (Athena Parthenos in gold, 23 with the two pediments, the
gables set back 1 m for the ledge), the Hephaestus temple (its bronze pair), Didyma (Apollo), the Pantheon (the gods in
the exedrae, the apse and the aediculae), Notre-Dame (the Gallery of Kings, 28), Karlskirche (pediment and the two
angels before the steps), St Paul's (the apostles on the pediment, the Evangelists at the towers), Versailles (the
roofline's balustrade), the Zwinger (Hercules on the Wallpavillon, the Langgalerie's terrace).

**Below the ground** (2026-10-03, the mine): `site.dig: [[x0, z0, x1, z1], ...]` are rectangles where the ground is OPEN
over a building (a shaft's mouth: no floor near the surface to open it as a cellar's stair does); the game opens it
over floors within `DIG` (4 m) of the surface and over these, and leaves it whole -- walked on -- over anything deeper.
`archBuilding` returns the building's `extent` (half sizes from its middle, past a footprint of its own) for the
walls the walker meets, and its `dig`. Marker data `crew` keeps a spot for the building's own people (a mine's
miners), not the villagers'.

**`court`**: a ring of rooms round a courtyard as ONE part -- outer and courtyard walls on any plan (rect, sides,
points), windows every `axis` metres, doors from the court into the rooms, floors continuous on every storey, a
dog-leg stair up every storey (the floors cut round it), a `gate` through both walls, a roof on every side. It is
written as the engine's own parts (enclosures, prisms, a staircase, roofs) and built as any other. Melk's
Prälatenhof and Schwerin's pentagon are each one court now: walked all the way round, entered by the gate (at
Schwerin through the gate tower). `joins: [{face, at, width, door}]`: where another building stands against an outer
face, that stretch has no windows and, with `door`, a doorway on the ground storey (Melk's crossing against the west
wing: the church and the abbey one plan, 2026-10-03). A pattern's `middle` is another opening in the middle of an odd row (the gate among
the windows).

**`tower-stair`** (components/): a round turret in a square tower's corner, a spiral to the top floor, and that floor
round the turret's head -- the Stephansdom's two towers are climbed by it (next: Notre-Dame's and Cologne's, whose
generator writes the same thing out by hand).

**Fixes:** the Zwinger's curved galleries have their balustrade along the inner edge too; the Karlskirche's sides
are halls from the church (a door through its diagonal faces) to the gate pavilions (an arch into each), not screen
walls standing apart; the lanterns of Melk, the Karlskirche and Sacre-Coeur stand on their domes.

**New buildings:** Sacre-Coeur (a Greek cross round a crossing with pendentives, the colonnaded drum and pointed dome,
small domed towers in the angles, a stair turret up to the flat roofs walked round the drum, porch, campanile,
terrace); the Stephansdom (a groin-vaulted hall church under the great tiled roof, choir and apse, the south tower in
stages to its 136m spire and the north tower under its cap, both climbed, the Heathen Towers either side of the
Giant's Door).

## Repeatable pieces, and two more buildings (2026-09-26, last)

**What was written out by hand in several buildings is a component now:**
- `drum-dome`: a drum of `n` bays (a window every `every`th), a dome of any profile, the lantern standing on it where
  it has narrowed to the lantern's width, and -- by name -- ribs and a PERISTYLE of columns round the drum. The
  Karlskirche, Melk, Sacre-Coeur, Hagia Sophia (drum = the ring of forty windows, ribs on), St Paul's (peristyle)
  and the Parliament (ribs) all use it.
- `portico`: a temple front against a wall -- steps, a row of columns of an order with their entablature, the
  pediment roofing back to the wall; side columns by name. St Paul's west front is two of them, one over the other.
- `tower-stair` places its turret anywhere in the tower (`tx`, `tz`; the corner by default), its door toward the
  tower's middle, its top floor in up to four pieces round the turret's head. Notre-Dame and Cologne use it now
  (their generator wrote the same thing out); their turret doors, which faced the flank wall, face into the tower.
- `pendentives` `deck: { thickness, out }`: the roof over the crossing's corners round the drum's circle -- Melk's
  and Sacre-Coeur's generators each had their own copy of it (`corner_fill`).
- `gallery` takes `sill` and `arch`: with `sill` 0 it is an open arcade, a loggia (the Parliament's river front).
- expressions know `abs` and `atan2`; the colonnade's `order` may name a param.

**New buildings:** St Paul's (a Latin cross round the crossing and its pendentives, a round base over the roofs, the
`drum-dome` with its peristyle of 32 columns, attic, dome and lantern; the two-storey west portico; the west towers,
climbed, under their belfries; the semicircular transept porticoes; balustrades round every roof) and the Hungarian
Parliament (two `court`s gated toward the domed central hall, the tall ribbed dome and its spire, turrets, the
river loggias, pinnacles, the entrance porch).

Not yet: St Paul's stair to its galleries round the dome; the Parliament's two chambers and its many smaller towers.

**Two more checks** (`arch/check.js floating`, printed on the check page): a WALL STANDING ALONE -- a wall or an
enclosure touching nothing of the building but its platform (`ALONE`; element and component sheets are exempt, they
show pieces alone) -- found Hagia Sophia's narthex front 1.5m off its walls: a `wall`'s thickness lies on the -z side
of its placement (-x turned a quarter), and three generators had assumed +z (Hagia Sophia's narthex and tympana,
Sacre-Coeur's porch). And a HALF DOME OPEN TO THE SKY (`OPEN`): a semidome's cut face must look into the building (a
roof over it) or be closed by another part -- St Paul's and Sacre-Coeur's apses rose above their choirs' end walls;
they spring lower now. A wall given a `width` keeps it and centres its pattern of openings (it used to take the
pattern's length). New: St Isaac's (the body under a flat roof walked on, piers, arches, pendentives, a stylobate and
the `drum-dome` with its peristyle of 24 -- the colonnade walked round the drum, reached by a `tower-stair` and a
flight -- four octastyle `portico`s, four small gilded domes).

## Floors, railings, and every floor reached (2026-09-26, night)

**Floors are floors** (architecture.js `archMesh` `floor`): every flat, up-facing triangle of the stone -- floors,
landings, treads, terraces, the platform -- is baked apart in the building's floor pattern and colours
(`archBuilding(..., { floor: { pat, color, accent } })`: checkered marble by default, black-and-white at St Paul's,
terracotta tiles at Melk, flagstones at Chichen Itza...). Roofs, domes and vaults keep their own.

**Railings where a stair could be fallen off** (assemble.js `railingsFor`, after the whole building is assembled):
along each side of every flight and staircase, just past the tread's edge, the building is asked whether stone stands
there (a wall the stair hugs) and whether the floor beside is more than half a metre below the tread; where it is open
and there is a drop, the side gets a railing -- `railing: { type, height }` on the definition: "balusters" (the
default), "iron" (dark in the game), "stone" (a sloping parapet) -- on the tread's very edge. A component's railings
are recomputed by the building that uses it. Spiral stairs, walled in their turrets, get none.
(2026-10-06) The open side of a flight is closed by a STRINGER, part of the railing: a board 6 cm thick from 1 cm inside
the flight's side to 5 cm outside it, its top 3 cm over the nosings, its foot under the soffit, swept along the treads
and half a step on to the floor it starts from; the balusters (or the iron posts) stand on it and the handrail is
centred over them. A side with stone beside EVERY tread needs none -- the wall is the stringer -- and the flight's own
flat side, which lay in the wall's face and drew over it wherever the wall showed beside a tread, is pushed a
centimetre into the wall. (The town's houses finish their railings in the flights' wood: `kind:railing`.)

**Every floor reached** (architecture.js `archAccess`, the check page `access.html`): the building is walked as the
game walks it -- the same floor field and wall field, the same step (the next floor at most .5m up, else the fall),
the walker's 0.25m circle -- from the open ground round it, over a 0.25m grid in eight directions. Then every flat
floor with a room's headroom (2m of it under a ceiling, no more than 20m up) or open to the sky and marked walked, is
looked at, and the ones never reached are reported in regions per level. Not floors: the tops of walls, enclosures
and rings (sills, a wall's head) unless `walked`; a slab marked `flatRoof`; an attic under a pitched roof; anything
inside a solid. What it found and what was fixed:
- the wall field held every stair's risers, and the step after next read as a wall: stairs are left out of it now
  (their open sides have railings, which are walls) -- the game's walk up a stair is no longer stopped short;
- the wall field's cells are 0.2m (they were 0.4: a doorway had to be 1.3m to pass the walker): turret doors are
  1.3m, in turrets of 8 or 10 bays;
- a turret's octagon sits inside the circle its floor was cut to -- a crack round the stair's head: the floor reaches
  the octagon's faces (`tR cos(pi/n)`);
- a spiral starts at its door (it used to start anywhere and the door opened on its middle), and a pair of towers'
  spirals wind one each way (`hand`) to arrive on the same side;
- courts and palace wings, Melk's terrace (the Altane an open arcade now: `curved-gallery` `sill`), Schwerin's gate
  (a square gate storey with the gateway through it), the Pantheon's door (it was glazed), the Zwinger's galleries
  (a door at each end), Milan's turrets. A domed tower's door is on its first face, 180/sides degrees round from +z.

**Walking a spiral stair** (index.html): the game knows every spiral's axis (`archBuilding` `spirals`); walking on
one, the view turns by the angle the walk goes round the axis, so going up or down faces along the treads.

**More pieces:** `apse` (a half ring of windows under a half dome or a half cone: Hagia Sophia, St Paul's, Sacre-Coeur,
the Stephansdom); `tower-stair` takes `tx`/`tz`/`n`/`doorBay`/`hand` (Milan's turrets are it now); `gallery` has a
door at each end; `chhatri` `floor`; parts may say `walked` and `flatRoof` as expressions (`terrace`); expressions
know `sin`, `cos`, `sqrt`. New buildings: the Berliner Dom and Moritzburg (and the Fisherman's Bastion, Mainz
Cathedral).

## Detail by size, and four more buildings (2026-09-26, last of the night)

**A round thing's detail follows its size** (`detailFor(params, radius)` in assemble.js). A great dome 30m across
needs far more points on its meridian than a lantern 2m across to look as smooth, so domes and columns no longer
take the building's `detail` flat: at about 4m radius they get it, twice it at 8m, four times at 16m (to the nearest
power of two, so from about 11m), capped at `maxDetail` (a param, 16 unless the building says), and half of it
under 2m (lanterns, finials, column shafts). St Paul's, the Pantheon, Hagia Sophia, Florence and the Berliner Dom get
16 per quarter on their main dome; columns got cheaper. Every building together grew by about 1%.
  Everything set out from a dome's meridian reads the same curve (`domeCurve`): the dome, the ribs laid on it, a
spiral whose flights follow it (`spiral.curve`), a stair wound under it (`follow`), and `atop`/`atopR`. A height
worked out by hand from the curve does not survive a change of detail: Florence's lantern stood at `drumTop +
domeRise`, sunk 3.5m into the shell at detail 4 and floating at 16. It stands `atop` the dome at its oculus now, its
roof `atop` the lantern and its ball `atop` the roof -- `topOf` follows an `atop` chain -- and the eight buttresses
stand on the dome at their own radius (`atopR: "lanternR + 4.2"`).
  The support check samples a part's corners strewn by the golden ratio, not at an even stride, which fell in step
with meshes built of repeated sections and missed every corner that touches.

**The drum-dome's peristyle carries a deck** (`peristyle deck`, a ring from the drum to the colonnade's outer edge
at the columns' head) instead of a wide entablature disc: the Berliner Dom's dome looked like it sat on a platform.
The Berliner Dom was redone round it (corner towers from the ground, a bigger dome on a taller drum, the front's
great arch); St Paul's and St Isaac's use the same deck.

**New buildings**, each by its own generator, with its pieces as components: **El Pilar** (Zaragoza: a hall church
under a central dome and coloured cupolas, four `baroque-tower`s, one climbed); the **Sultan Qaboos Grand Mosque**
(`arcade-walk` riwaqs with `crenellation` round the court, `portal`s -- a deep frame closed by an `iwan` --, the
prayer hall under a `drum-dome`, `omani-minaret`s: square, then octagonal between balconies); **Ulm Minster**
(the five-aisled `basilica`, and the west tower stacked from `gothic-tower-stage`s, a `gothic-octagon-stage` and a
hollow `gothic-spire`, climbed by a `round-stair-tower` to the gallery at 143m); the **Blue Mosque** (the Ottoman
`dome-cascade`: central dome, four semidomes with their exedrae, corner domes, turrets; a `riwaq` of four
`domed-arcade` rows round the forecourt; six `ottoman-minaret`s, `minaret` on a tall pedestal under a pencil cap).
All four pass the stair, support and access checks (the only unreached floors are pockets under 20m²: minaret
balconies with no stair, a cornice ledge).

## Chinese roofs, brackets and halls; the Temple of Heaven (2026-09-26, later)

**A Chinese roof's section is its own profile, `jujia`** (profiles.js): the "raising" of the purlins -- the half-span
cut into steps from the eave in, each steeper than the one outside it, from `lo` (the slope at the eave) to `hi` (at
the crown), the Qing rule's 0.5, 0.65, 0.75, 0.9 in proportion. The purlins lie on the parabola y = lo d + (hi - lo) d^2
/ 2a whatever their number, so the detail level changes the steps and not the roof. Turned about its axis it is a round
hall's or a pavilion's roof -- a `dome` whose head is `jujia` -- and with an `oculus` the ring of roof round the drum of
the tier above, which stands on it where it has narrowed to its radius (`atop`, `atopR`).

**Any rectangular roof bends into it** (build.js `curvedRoof`): given `lo`/`hi` or `upturn`/`flare`, a `roof` of any
form (hip: wudian; gablet: xieshan; gable; pyramid) has its stack cut finer and every level raised along the concave
curve (a straight roof's height share t becomes (lo t + (hi - lo) t^2/2) / ((lo + hi)/2)), and its sides cut into
pieces so the EAVE can rise toward its corners (`upturn` metres, over `reach`, dying away up the roof) and sweep out
there (`flare`): the hips curve up at their feet. Every level has the same number of points, so it closes exactly.

**`repeat` may be a list** (a grid): each repeats everything the one before made -- a hall's columns, row by row.

**Components:** `dougong` (one bracket set: cap block, arms, tongues, blocks, the beams the rafters rest on -- placed
round a ring by `spiral` or along a row by `repeat`), `chinese-hall` (platform and steps, a grid of columns, lattice
doors and windows front and back, the ends blind, architrave, dougong rows, a curved roof of any form with its ridge
and ridge beasts; `backSill` 0 makes it a gate hall walked through), `palace-wall` (a red wall under a tiled coping).
`elements/chinese.json` shows the roofs side by side and a row of brackets.

**The Temple of Heaven** (`temple-of-heaven.json`, tools/archgen/temple_of_heaven.py): the Hall of Prayer for Good
Harvests on the Altar of Prayer -- three round marble tiers as the building's `base` (91, 80 and 68m across), a
balustrade of posts and panels round every tier, stairs on four sides (to the south and north two flights either side
of the carved imperial way, a `shed` roof as its wedge) -- the hall in three tiers (twelve bays of lattice between the
eave columns, a drum of windows on the gold columns, a smaller drum on the four dragon-well columns, three jujia roofs
on rings of dougong, the gilt finial, the coffered caisson inside), in its court with the Qinian Gate and the annex
halls. Walked: every floor reached (archAccess), stairs and support clean.

**Two things the support check could not see** (check.js `floating`): a beam resting on one small block at its middle
(the underside is now sampled on an even grid, so every edge's middle is a sample), and a roof resting on its bracket
sets -- the roof's own lowest band is its eave, out in the air; now a part also rests on whatever reaches up to it from
below (another part's top lying on its surface or set into its solid).

## Surfaces: patterns and finishes (2026-09-26, later still)

Every building has a FINISH now -- its floors, walls inside and out, ceilings, vaults and roofs as rules over its parts
(assets/finishes/, arch/finish.js), patterned from a library of patterns written as mathematics (assets/patterns/,
patterns.js). docs/patterns.md has the language, the rules, how inside and outside are told, and the mapping. The
buildings' colours, which were code in architecture.js, are in their finishes.

## Railings round landings (2026-09-27)

A stair's railing used to stop where its flight did: the flat between the two flights of a dog-leg, the platform a
flight arrives on, stood open over the drop. A staircase now reports its landings' FREE EDGES (build.js `staircase`:
every stretch of a landing's outline no flight arrives at or leaves from, in the order and direction the outline runs,
each with the way out across it), and a flight its own landing's three; `railingsFor` walks them round the landing as
one railing -- one post and a mitred rail at each corner, back to where it began -- asking at every point the same
question the flights ask (`openBeside`: no stone just past the edge at knee and chest height, and a drop of more than
half a metre), and puts posts and a level rail on the open stretches. They are a part of their own ("<stair> landing
railing"), so they meet the flights' railings end to end rather than welding into them.

## The village: town houses, longhouses, the wall and the church (2026-09-27)

`tools/archgen/village.py` writes the village's definitions (`assets/architecture/village`, `.../furniture`), and
`town.js` builds a whole town of them (docs/world.md "The town"). What they added to the engine and its conventions:

- **Four kinds of town house** from one generator: the GABLE house (narrow and deep, its gable to the street), the
  EAVES house (broad, its ridge along the street -- the roof turned), the JETTIED house (upper storeys out over the
  street and the yard by `j`), the STONE house (thick walls, round heads, a hipped roof). Params: `W` frontage, `D`
  depth, `n` storeys (2 or 3; the roof sits on the n-th), `H` a storey, `pitch`, `t`, `j`. The street front is +z. A
  dog-leg stair climbs the -x side wall in two columns (1.15m wide: a flight's railing, as the walker's wall field
  sees it, takes 0.4m of its open side, and a narrower one left a lane no walker fits), one flight a storey, each floor cut only over the flight
  that comes up through it (the ground floor over the cellar's, open from its first step's top: 2m over every
  tread); the door on the +x side of the front; the beds upstairs against the back wall; a CELLAR dug under the
  whole house with its own flight; a SHOP front replacing door and window with one wide arch and a trade's
  furniture in the front room. What a house has is its BUILD LIST (`walls 0` or `walls 0 shop`, `walls 1..n-1`,
  `floor 0` or the cellar set, `floor k` + `flight k-1` + `way k` per upper storey, beds, the door, a trade):
  the definition holds every part any house may need, the plan builds the ones this house has.
- **The longhouse**: one long low jerkinhead roof over people at one end round an open hearth and beasts at the
  other beyond a partition; doors in the middle of both long sides.
- **The wall**: a stretch whose top is the walk, a crenellated parapet on the field side (+z), a low one on the
  town side; each parapet's two ends stop where the town plan says (`pa`/`pb`, `ia`/`ib`: short of a tower
  astride the wall, into a corner tower, flush with a gatehouse's face); with `stair` a flight climbs the town
  face to a landing of its own beside the walk, and the low parapet opens there (stepped off the flight's side,
  its railing -- rising where the wall's top falls below knee height -- was in the way). **The round tower** stands astride the wall's outer face (`zt`):
  solid to the walk, then a stage entered from the walk that passes behind it, a spiral to a platform (its
  hatch the bays over the spiral's last 2.3m), and a top: merlons, or a room under a cone, an ogee bell or a
  tent roof. **The gatehouse**: the gate passage through its field and town faces, the walk through its upper
  storey by doors in its side faces, a hipped roof or battlements, `guard` places outside.
- **The church**: nave, lower chancel through a round chancel arch, a square west tower (its door the church's)
  with the spiral turret up to the belfry floor (a turret of 1.8m radius in six bays: at 1.3m no walker fits
  between the newel and the turret wall, so the tower is 7.2m to hold it, the way through its foot clear of it); its top one of spire (and cross), pyramid (and cross),
  saddleback, onion (on a drum), battlements; pews in two ranks, the altar.
- **Furniture** as components (`furniture/*`): bed, table (its seats and sitting places), hearth (its fire),
  chest, barrels, the tavern room, pew, altar, and a trade's workplace each (smithy, bakery, pottery, weaver,
  tailor, carpenter, cooper, butcher) with its worker's place and a customer's. The movables in them are ITEMS
  (a part of `type: "item"`: a bedstead, a trestle table and benches, casks, a settle for a pew -- docs/items.md):
  the building keeps the item's box and takes its markers, `architecture.js` draws the item in its own materials.
- **Dwellings** (`assets/architecture/dwellings/*`, `tools/archgen/dwellings.py`, the "Dwellings" category, each with
  its finish in `assets/finishes/<name>.json`): 31 tents and houses beyond the medieval town -- pavilion, bell tent,
  marquee, wedge tent, Roman papilio, ger, tipi, Bedouin black tent, wigwam; igloo, Iron Age roundhouse, crannog,
  rondavel, beehive hut, hogan; pit house, Norse and Iroquois longhouses, stilt house, minka; domus, Greek house,
  Arab courtyard house, siheyuan (the `court` part); Egyptian house, pueblo, blackhouse; the Russian izba (round
  logs, carved window frames, the stove's chimney), the Maya house, the Indian village hut and the haveli. Round ones have their door at
  +x (ring bay 0), straight ones on face 0 (+z; on a CHAMFERED rect face 2 is +z). Every one can be entered, and its
  inside follows its outside: domes and cones have no cap (`cap: false`), a cone or a dome down to the ground gets its
  doorway as a band cut off at the door's head (`oculus`) with a gap round it (`sweep`) and the rest above it (a
  sphere's top is a segmental dome), ridge tents and the pit house leave their front gable open (roof `open`). Their
  windows are unglazed (`glass: false`, which `court` now passes to its walls). Curved meridians carry `seg`, so a
  small dome stays a dome at a low detail.
  The nine the period towns are built of (domus, Greek house, courtyard house, siheyuan, haveli, Egyptian house,
  izba, Maya house, Indian hut) are FURNISHED (2026-10-27): a `door` marker in the doorway (its panel, and the way
  the villagers go in and out: village-life.js), beds of the time and place (lectus, kline, pallet, Ming canopy bed,
  charpai, Egyptian bed, hammock -- a bed marker `one: 1` sleeps one), a table or a tray with seats and a sitting
  `spot` at each (the town's inn is one of these houses: its guests eat there), and for the look the rest (the
  triclinium, the main hall's altar table and cabinets, the upper rooms). What the villagers use stands in the room
  the door opens into, in a straight line from a step inside it -- a court house's front wing, beside the gate.
- **Period furniture in the village's houses** (`assets/architecture/furnishing.json` `swaps`): a town of a period
  built of the village's houses gives them a `furnish` word (periods.json `town.furnish`: ottoman, industrial),
  which a `component` passes on like `detail`; under it an `item` part is the one the swap names -- its own
  `params` over the placement's, its own `markers`, turned `turn` about its foot. The Ottoman house sleeps on a
  mattress and eats from a brass tray between divans; the Victorian sits on settles at a deal table.
- **Roof `open`**: "front" (+z), "back" (-z) or "ends" -- the gable ends left out (a shell roof's inner face too).
- (Two engine fixes found on the way: a face's TIERS are known by `openings` as well as `h` -- a one-storey court's
  single tier was read as a list of openings; and a finish rule naming a component paints its walls, not its window
  panes -- a pane is finished only by a rule naming its own part or `kind:glass`.)
- **`when`** on any part: drawn only while a WORD parameter has the value (or one of the values) it names
  (`"when": {"style": ["rails", "picket"]}`) -- one fence definition holds its five styles. A word param is
  passed to a component by name (`"params": {"style": "fence"}`: the yard's `fence` word reaches the component).
  `p0`/`p1` 0 leave out the post at the start/the end of a run: where two runs meet at a corner ONE post stands
  (the town wall's town-side balustrades both run to the corner, `ia`/`ib` = T/2 - .15; the wall a side begins
  leaves its end post out, `ka`/`kb`).
- **The market and the beekeeper's garden** (`village/market`, `village/apiary`, 2026-10-02; were village.js code): the
  paving and the market cross as parts, eight `items/furniture/market-stall` items (counter, posts as tall as the awning
  over them, a tilted striped awning, wares by `wares`, the vendor's spot), shoppers' spots; the apiary's picket fence,
  `items/tools/skep` hives, bench, the beekeeper's spot. town.js finishes them (`marketFinish`, the yards' wood).
- **Farmyards as assets** (`village/pig-yard`, `hen-yard`, `stable-yard`; `tools/archgen/village.py`): a `fence`
  component a side (styles rails, picket, wattle, zigzag, stone; `L`, `bay`, `h`), a `gate` leaf swung open
  toward the street, a `pigsty` / `hen-house` / `stable` component, and the markers the game's stock live by:
  `pen` (the range, `w` by `d`, of a `kind`), `block` rects they keep out of (a value a placement), `trough`
  (a water vessel). town.js builds them in the town's style (`yardFinish`, a fence style per town style) and
  `lifeOf` hands `pen`, `blocks` and `vessels` on as the old village.js farmyard did.
- **Zones** (a part of `type: "zone"`): a floor area marked by WHAT BELONGS THERE, not by the furniture itself --
  `zone` names a rule of `assets/architecture/furnishing.json` (`seating`, `altar`, `organ`, `lectern`, `choir`),
  `w` across (the zone's z), `d` deep (its x), `h` the headroom, `at` its centre and turn with its +x the way the
  furniture faces (toward the altar). The rule fills it: `one` component or item at the centre (the altar, the
  organ -- `yaw` turned, `params` as expressions over w, d, h) or `rows` of a component from the back (`pitch`
  apart, `margin` free at the sides, an `aisle` down the middle when wider than `aisleOver`; `L` a row's length).
  A church says where its seats, altar and organ are; what stands there is the rule's -- the village church
  (seating, altar) and the cathedrals (Cologne, Notre-Dame, Milan: + organ) are furnished this way, their items and markers (seats, the priest's
  and the organist's spots) coming out as from any `item` or `component` part.
- **Markers** (a part of `type: "marker"`, no geometry, placed like any part): `bed`, `door` (`panel: 0` a doorway
  without a door), `window`, `spot` (a person's place: `face`, `pose`, `work`, `gesture`, `tool`), `seat`/`lie`,
  `fire`, `guard`, `way` (the route up the stairs, by `order` and `storey`). `architecture.js lifeOf` reads them into
  the shapes the game's hand-built houses always exported (beds, doors, windows, folkSpots, seats, fires, guards,
  ways), so the villagers' day, the door panels, the seats and the guards take a definition as they took those.
- **Turned buildings**: `yaw` (degrees) among a building's params turns the whole assembly about its origin
  (`archAssembly` -> `turnAssembly`: every instance of every part) -- a house facing its street -- so its mesh,
  floors, walls, finish and markers all come out turned alike.
- **A gable is a wall** (arch/finish.js): a roof's vertical triangles take the finish of the walls under them, not
  the roof covering, and are mapped in the wall's own coordinates -- a timber-framed gable over framed storeys,
  a pediment in the temple's marble.
- **The timber family** (`assets/patterns/timber.json`): `frame` (a storey of framing: sill, plate, a rail at the
  window-sill line, a post every 1.3m, braces; plastered infill) and `close studding`, both a storey tall and laid
  with `align: "part"` on the storey's foot; `boards`; plain `wood`. And `roofs/thatch`; palettes for timbers,
  woods, thatch, earth and a brown tile.

Checked (the scratchpad harness): every house variant (three storeys, cellar, shop), the inn, the church with each
top, the wall with its stair and corner ends, the tower and the gatehouse -- 0 bad parts, 0 stair and 0 support
findings; `archAccess` reaches the cellar, every storey under a ceiling and the belfry, and a walk along the flights
reaches the top storeys and steps off the wall stair's landing onto the walk. (`archAccess` now stands on the
highest floor at or below the walker, as the game does -- it used to put the ground at 0 under everything, and a
cellar could never be reached.)

## Shell roofs, lofts and doors that fit (2026-09-27, later)

- **A roof is solid down to its eaves** -- a stack of levels closed by a flat soffit at the overhang's eave line -- which
  under a longhouse's low eaves was a ceiling 1.7m over the floor. `shell` (metres) makes it a COVERING over an open roof
  space instead (build.js `roofMesh` with an inner stack): its underside follows the slopes that far below them, its
  gables stand in the wall plane (`overhang(..., false)`: the verge is the covering's alone), and a band round the eave
  closes the skin. The longhouse's roof is a shell: its walls are 3m, a boarded LOFT spans the house at the eaves (open
  over the hearth for the smoke and over its stair), and the stair runs down the middle under the ridge -- a stair along a
  wall climbs into the low slope.
- **Door panels are shaped to their doorways**: a door marker carries its opening's `spring` and `head` (the same numbers
  as the opening's), and architecture.js `doorPanel` builds the panel from `archCurve` -- flat, segmental, round, pointed
  -- 3cm clear of the jambs and 2cm under the head, with iron strap hinges and a knob on both faces. The game draws every
  door of one shape in one instanced draw.

## The last code-built buildings, and the site's own life (2026-10-02)

Every building the game stands up is a definition now. What was left as code -- the fisherman's hut, the fountain, the
fields, the currant rows and the orchard (village.js), the water mill and the landing, Caerphilly and Versailles
(architecture.js englishCastle, baroquePalace) -- is `assets/architecture/village/*`, `caerphilly.json` and
`versailles.json`, written by `tools/archgen/village.py`, `riverside.py`, `caerphilly.py` and `versailles.py`, each with
its finish. village.js keeps only MAX_PIER_DEPTH; the old box stairs (stairSteps, wellRail, stairY) went with them.

- **`site`** on a definition: `origin: true` keeps the definition's own origin as the site's (the mill and the hut are set
  against the bank by their yard, not by the middle of a jetty or a wheel out over the water), its footprint the params
  `footW` x `footD`; `moat: { hw, hd, w, depth }` is the island's water the game carves (Caerphilly); `glazed: true` makes
  its windows' panes glass instead of shutters (Versailles).
- **More of a site's life as markers** (architecture.js lifeOf): `vessel` (a mug, a jug, a bucket, a trough to drink
  from: tableware.js), `dish` (food on a plate), `flow` (a falling jet or a rippling pool: the fountain), `cobweb`,
  `plant` (a fruit tree or a bush the flora grows), `crop` (a field's painted rows: cropPanels), `slot` (the quay's
  goods), `path` (the dock hands' way, by `i`), `dock` (the boat's), `rotor` (the mill wheel's axle and numbers),
  `drop` (the sacks'), `berth` (the barge's), `lift` (a stair's shortcut: from the marker to its top `dx`, `dy`, `dz`),
  `painting` and `mirror` (`w` x `h`, facing the marker's +z; a mirror reflects only within its `room`).
- **Marker data per placement**: a list in a marker's `data` is one value per placement when it has several (a door
  part's widths, the cobwebs' corners) -- so a value that is itself a list (a mirror's `room`) is given once per
  placement too.
- **The catalogue registers itself**: every `architecture/*` definition assets/index.json lists is in the library, and
  every finish in it serves the building it names -- a new definition needs no import in architecture.js.
- **The land is cached**: architecture.js `LAND` lists the village's and the riverside's sites; pregen.html bakes them
  with the landmarks and index.html asks for them.

Versailles is the plan the code laid, by its rules: a wall per face in three storey TIERS (a window over a door), the
end walls between the long ones (no face in another's plane), the party walls between touching blocks with one
doorway through them (the corps' end doors moved 7.5 m toward the court, clear of the stairs), real flights through
railed stairwells, the Hall of Mirrors' mirrors and the canvases behind them as markers, its furniture items. The
ground floor runs under the walls, so a doorway has its floor.

## Open stairs, notches, shutters (2026-10-02, later)

- **`soffit` on a `flight`**: an OPEN stair -- its underside a sloping soffit that far under the nosings (build.js
  `flightFace`, as a spiral's), room beneath it. Without it a flight is solid to its base.
- **An opening open to the top** (flat head, springing at the wall's height) is a NOTCH: nothing is built over it
  (build.js `wallFace`). The village church's nave has one in its west wall as wide as the tower: the tower's east
  wall is the only wall there (two walls in one place flickered), and the nave roof's west gable stands in the
  middle of that wall; the floors of the nave, the tower and the chancel meet end to end (no two floors in a
  doorway), the chancel's side walls stop at its east wall.
- **Town houses**: the window openings are holes (`glass: false`); every window has a `window` marker, so the game
  hangs wooden SHUTTERS there (open by day) -- or glass panes where the house's `glazed` param is 1 (the stone
  merchant's house); archBuilding takes `glazed` from the params as from `site`. The longhouse's windows are shuttered
  too, the gatehouse's unglazed. A house with a cellar builds `flight 0 open` (the first flight on a soffit), and the
  cellar's flight runs UNDER it in the same column against the side wall, entered from behind the stair, with a rail
  beside its well on the ground floor.
- **Temples**: the Greek temples' added "front steps" flight is gone -- they are climbed by the crepidoma's own steps
  (the Parthenon's 0.5 m ones are just within the walk's step); only Didyma keeps its genuine east stairway
  (temples.py `front_stair`).


## Workshops and trade signs (2026-10-02, last)

- **The trades' furniture** (village.py `furniture()`: smithy, bakery, pottery, weaver, tailor, carpenter, cooper,
  butcher, tavern-room) has its real pieces -- a brick forge with hood, chimney and bellows, an anvil with its horn,
  the quench tub and tool rack; the oven with its mouth, woodpile, peel, loaves and flour; the kick wheel, a brick kiln,
  shelves of pots, jars and bowls; a floor loom with warp, heddles and treadles; bolts of dyed cloth and a dress form;
  the joiner's bench with its vice, sawhorse and stacked planks; a cask being raised; the meat rail with hams and
  sausages. Its parts are NAMED BY THEIR MATERIAL (last word: brick, iron, clay, leather, cloth, wool, meat, linen,
  madder, woad, weld, russet) and town.js `TRADE_MATERIAL` finishes them by that word; the rest is the town's wood.
- **Trade signs**: items/components/trade-sign (propgen.py) -- a wrought bracket and the emblem on chains, `kind` a
  word: anvil, pretzel, jug, shuttle, shears, saw, cask, ham, ale-bush and tankard. Each house's `sign <trade>` part
  hangs it by the +x corner under the first floor; town.js builds it with the trade, and a shop front drops the
  front-window shutters (they had stood inside the arch).

## One face where two parts meet in a plane (2026-10-02, last)

Two parts whose faces lie in one plane, facing the same way, and overlap -- a floor's edge in a wall's face, a cornice
in its drum's, two roofs over a corner, two fences' posts at a corner, a pavement over a pavement -- drew the same place
twice, and the depth buffer flipped between them. A scan of every definition (scratchpad harness ships.html
`?coplanar=1&arch=...`) found them in most buildings, landmarks included. arch/finish.js `coverIndex` now settles it
for every finished building: of each such pair of triangles the LARGER keeps the place (the wall's face, not the
floor's 5 cm edge; on a tie the part that comes first) and the other has it cut out (`minusCover`: convex pieces of it
outside the cover). Undersides are left alone in the scan (two bottoms on the ground are never seen). Hidden by it,
not removed from the definitions: the overlapping solids still stand (the walk's floors and walls are unchanged).
Also fixed at the source: the centaur's kind (species.js `tauric`) lost its man's mesh head -- makePerson's upper body
returned before the face was made.
And (2026-10-24) it no longer carries the animal's `mane`: mammals.js reports a mane by its neck's and head's part
INDICES, and with the neck and head dropped those indices fell on a leg, which wore the horse's mane of thorns.

## Mills that grind, and an open longhouse (2026-10-03)

- **`spin` markers** (architecture.js lifeOf -> a building's `spins`): a piece of millwork -- an item: a gear, a shaft,
  a runner stone -- that the game turns about its own `axis` (x, y, z of the marker's frame) `ratio` times as fast as
  the building's drive: its water wheel (the current) or its sails (the wind). Millwork items (tools/propgen.py):
  components/face-gear (pit wheel, brake wheel), lantern-pinion (wallower), millstone, tun, hopper-horse, mill-shaft.
- **The water mill** (riverside.py) in two storeys: the pit wheel on the wheel's axle drives the wallower, its upright
  shaft goes up through the stone floor to the runner (underdrift); upstairs the bedstone and runner in the tun under the
  hopper on its horse, the grain sacks, reached by a stair up the north wall; below the meal chute into the meal bin.
- **The windmill** (windmill.py), walkable: three storeys of round tower (each narrower), steps wound up the wall
  (spiral placement, one tread a copy) through a hatch in each floor; the meal floor (meal chute, bin, flour sacks),
  the stone floor (bedstone, runner, tun, hopper fed from the grain bin above by a chute), the bin floor under the cap,
  where the windshaft from the sails carries the brake wheel that drives the wallower on the main shaft. Every world
  has one among the first farm's fields (town.js FARMS) as it has its water mill by the river; architecture.js LAND
  caches it.
- **The longhouse** has no loft: the roof open to its frame -- two rows of aisle posts with purlins, tie beams and
  king posts, wall plates -- and the open hearth in the middle of the living end (a kerb of stones round the ash, no
  chimney or hood: the smoke goes out under the thatch); the byre partition stops at the tie beams.

## Furniture with room round it (2026-10-23)

A building's furniture stands where its definition's numbers put it, and the same numbers in a smaller house, or with a
trade's workshop in the front room, put things where they cannot be: every town house's upstairs beds stood in the
chimney, the eating table's bench in a small house's forge or oven, the tavern's tables in the shop's side wall and a
bench in its doorway, Florence's pews in the nave arcade's piers, a cask in the watermill's meal bin. Now
(`arch/room.js`), once a building is assembled -- the whole of it, not each component on its own -- every SET of
furniture (a solid `item` part's copies near one another in one group: a table and its benches, a row of casks, a bed)
is tested where it stands: every point of its footprint on a floor, in no other part's solid (a point is in a part's
solid when that part's surface crosses an odd number of times both above it and below it -- a roof open underneath is
not round what stands far under it), in no other set, and out of the ways (1 m either side of a door, across its width
and 10 cm; a stair's approach). A set that fails is moved, as one and turned as it was, to the nearest place within
2.4 m where it stands so, its markers (seats, sleepers, places at a table) with it, or left out where there is none.
`assemble()` returns what it did as `fitted`; `check.js furnishing` asks the same test of what stands (none, once
assembled). The beds now stand beside the chimney, the tables and benches clear of the forge, the oven, the bar and
the doorway; Florence's seating zone was narrowed to clear the piers itself, so its pews need no moving.

## Joists under the floors (2026-10-24)

The town houses (tools/archgen/village.py) carry `joists 1` / `joists 2`: a 14 x 16 cm beam across the house every
0.75 m under the upper floors' slabs, the ceiling's timbers seen from the room below -- only beside the stair's two
columns (the flights' headroom, tuned to the walker, is untouched); they span the house's width within its walls (a
jetty's joist ends, out through the front, are not drawn). town.js `houseSpec` builds them with their floor; they take the house's woodwork (`WOODWORK`).

## String courses (2026-10-24)

The town houses but the jettied one carry `course 1` / `course 2`: an enclosure band 16 cm high standing 6 cm proud of
the walls at each upper floor's line, in the town's fine stone (town.js houseFinish: `S.fine`) -- the storeys read on
a plastered front as on a stone one. The jettied house has its jetty for that.
**Quoins** (`quoins`, `quoins b`): dressed stones up each corner of a town house, long and short in turn, 2 cm proud of
both faces, in the fine stone -- town.js builds them only on a plastered or stone house (no timber frame on the ground
or upper storeys: drawn after the house's look) and not on the jettied one.
**Plinth** (`plinth`, `plinth shop`): a low wall of the town's rough stone round the foot of every town house but the
stone one, 55 cm high and 4 cm proud, cut for the door (or the shop's arch) -- what a framed or plastered house stands
on. (An enclosure's opening may not rise above the wall: the cut is the plinth's own height.)

## A fireplace, not a box (2026-10-24)

`furniture/hearth` (village.py): the raised hearth now has two jambs up to its hood, the hood a flue on up to the
ceiling (it had hung in the air), and a sooted brick fireback against the wall behind the fire (town.js: the rule
`hearth/fireback`, iron-black brick, before the hearth's own stone). The furniture check: no change in any house.
**Jetty joist ends** (`jetty 1`, `jetty 2`): under a jettied house's overhang, front and back, its floor's joists show as
a row of beam ends every half metre (woodwork) -- the jettied house's mark where the others have string courses.
**The church tower's courses** (`tower courses`): two bands 12 cm proud round the tower at its stages -- over the door's
storey and under the belfry. **Arched doorways** get a keystone at the crown (windowframes.js: frameDoors' `arched`;
the church's, the stone houses'), and their doorstep like any door; woodpiles stand only by plain doors.
**Planed wood indoors** (town.js houseFinish, churchFinish: `WOODWORK` -- furniture, stairs, joists, pews -- in
`timber/wood`, the pattern meant for them): the coarse `timber/bark` read as zebra stripes on a bar counter. Bark stays
on the yards' posts, the longhouse's rustic woodwork and its frame, and the wall-walk's rails. The ITEMS' woods too
(assets/items/materials.json `oak`, `pine`, `oak-grey`: furniture, stalls, carts, ships, tool handles) are planed wood
now -- the market's counters were striped bark.
**Windmill sails with their lattice** (tools/propgen.py `components/windmill-arm`): the cloth now has its bars across
every ~45 cm and the hemlath along its outer edge in front of it -- it was a plain board. (Regenerating propgen rewrote
all 44 props; only the arm's content changed.)
**The fisherman's hut** (tools/archgen/riverside.py finish): its reed roof's gable ends -- vertical faces, a wall to
`surface` -- took the catch-all floorboards, a big plank triangle under the thatch. The roof is now thatch by its part
alone (its underside boards), and the walls weatherboard (floorboards stood in for them). (The watermill's gable ends
are stone, as its walls: right for a stone mill.)

## Structure first: double aisles, wells, and stairs that arrive (2026-10-27)

**Double aisles** (gothic.js `basilica`, `aisles: 2`): two rings of aisle round the nave and the apse, a row of
free-standing piers on the line between them (placed wherever a bay beside them has its aisle), each ring its own rib
vaults (the cells on the mid line share their side, and a transverse rib is hung there once). The transept carries the
same rings across it, its side walls one lower arch and one upper window per ring. Over two aisles the flyers are
`flyerStages`: **2** (Cologne) -- an intermediate pier rises from the mid-line pier through the inner aisle's lean-to,
with its own pinnacle, one flight from the clerestory to it and one on down to the outer buttress; **1** (Notre-Dame's
single leap) -- one flight over both. `roofAt(x)` gives the lean-to's height wherever a flight or a pier meets it.
Notre-Dame's aisles are now its real double ones, and Cologne's too (53k and 68k triangles).

**A well through a prism** (`plan.well`: `radius`/`sides` or `rect`, `at`; build.js `wellPoints`, `prismMesh`): the hole
a stair comes up through. The outline takes a corner where the cut line x = cx crosses it, the well's sides face into
it, and each cap is the plan halved on that line with the well's half ring carried round -- ear-clipped, closed (the
mesh check finds no open edge). Florence's two shaft floors over the octagon became one slab with the dome stair's
well; the dome stair arrives on a 6.4 m landing, and the gallery between the shells is a ring of eight floor slabs.

**Finishes by what a surface is, not where it happens to be**: a wall's top, sill or set-back is masonry unless walked
(the ledge rule takes `kind: "wall"`); a floor is indoors when a ray straight up meets a ceiling and, from a point
under it, every one of 16 rays round meets stone -- a platform outside a door, under the sky beyond its edge, is
paving; probes more than a metre apart no longer share a cached answer; and a floor piece that is part in, part out is
halved along its longer side (down to 60 cm) until each piece's probes agree -- no checker mixed into paving.

**The arrival check across an edge** (check.js): a staircase's top landing is stepped off across any free edge -- the
floor may begin past its far side, a landing's width from its middle -- so 35 cm past each free edge at the top is
probed along its length; a spiral's landing reaches as far as its own length (`len`).

**`arrive`: the floor a stair arrives on** (assemble.js `arrivalFloor`; on a `staircase`, a `flight`, a `spiral-stair`):
a stair leads somewhere, and one standing alone is given the floor it would reach in a house -- built from the ground
up: square posts (`post`, 35 cm) at its corners and every `span` (3.5 m) along its sides, standing where the stair
stands, and on them a slab `thick` deep (the stair's soffit). A straight stair's floor begins at the far edge of each
top landing (build.js `staircase` hands back `tops`; landings ending on one line share one floor: the imperial stair's
two arrive on one gallery), `depth` deep (2.5 m) and `width` wide (their span and a metre either side). A spiral's is a
square `depth` past its treads every way, with a polygonal well whose sides stand 5 cm clear of the treads' outer edge.
The floor's outline and the well's are its `edges`, so railingsFor rails them as a landing's -- wherever the drop is:
round the well but over the treads just below the arrival, along the outer sides but where the landing meets them.
All the staircase specimens and the plain flight arrive now (elements/staircases, elements/stairs: no finding).

**Two railing faults**: a rail's two end caps were wound against its sides (every rail failed the mesh check: an edge
walked twice); and the railing round a staircase's landings, turned to begin at a closed point, joined the list's end
to its start even where the landings' edges did not close -- a rail flew from one landing's corner to another's. It
is turned without a break only round a closed loop now.

## Things bear on what is under them: seated roofs, cut doorways, flat octagons (2026-10-27)

**The wall's front face** is the line a wall stands on: `straightAt` runs its thickness BACK from z 0 to -t, and only
along x is it centred. A veneer -- a band of coloured marble on a facade, a course round a tower -- stands on the
wall's outer face line, a few centimetres into it, not on a centre line it does not have (Florence's bands floated
half a wall off the stone).

**Polygonal rings** (`ring.polygon`; build.js `chordal`): a bay laid flat on the chord between its two corners at the
ring's corner radii, as wide as the chord -- an octagon's faces flat, as its dome's webs are. A round ring's bay is
an arc (`radial`). Florence's octagon, drum, piers, tribunes and their cornices are polygonal now; the drum no longer
bulges past the dome's corners and the face walls, and its marble courses are eight-sided rings 4 cm into the faces.
(A ring's radii are corner radii: a face set d out is d / cos(pi / n) out at the corner.)

**A sloped prism** (`prism.slope` [sx, sz]): its top a plane, `height` at the plan's origin and rising sx a metre along
x. The wedge beside a tribune, between its end and the octagon's diagonal face, is built up to the tribune roof's line
along the cut, so the half pyramid's cut -- wider than the octagon's face -- rests against masonry all along, not sky.
The tribune roofs are half pyramids on the tribunes' five faces (`sides` 10, corner for corner with the polygonal ring).

**A seated roof** (`dome.seat`: the name of a ring or of an enclosure on a `sides` plan; assemble.js `seatLift`): the dome
is lifted until its soffit meets the wall's outer edge 2 cm under the wall head, where the soffit is lowest over it
(mid-face). A cone guessed at a height stood a hand's breadth over its wall (the rondavel), or with its foot ring out
past the wall in the air (the crannog). The roundhouse, crannog, rondavel and hogan roofs are seated now; the hogan's
roof was widened until its soffit reaches out over the walls (`seat` refuses one that does not).

**A doorway cut in a dome** (`dome.door` { width, height, at }; build.js `domeShell`): whole faces of its polygon (the
count nearest `width` at the springing), centred on `at` (+x), up to `height` -- a row spliced into the web and the
soffit there, the web and soffit left out below it, the jambs closed by the section through the shell, a lintel facing
down, no springing ring across the threshold. The igloo and the tipi were a band with a gap under a separate cap,
whose meridians never met: the band's cut was taken on its sampled meridian (0.58 m up), the cap's on the true sphere
(0.75 m) -- a ledge round the house with sky in it. The igloo's tunnel now runs from 3.2 m out back into the dome's
wall, its side walls under the barrel along the same stretch.

**A semidome's cut** (the `open` support finding) is asked only of a dome of sweep 0.5 or less -- whose open side is one
plane. A doorway's jambs are not a cut.

**Shell roofs open at a gable** (build.js `roofMesh`, `open` with an `inner` stack): the covering's thickness shows at the
doorway -- a strip up each verge from the outer slope to the inner, the eave band left off that side -- so the sheet is
closed (the tents' and the pit house's roofs had six open edges).

**Railings**: an open stretch of ONE tread gets none (a lone post beside the top tread of a short flight, holding no rail,
on 5 cm of tread). **Pyramids** are shells by design -- each band one mass's faces cut where the stone changes, the
rooms its hollows -- and say so (`shell`), so the mesh check takes their edges for what they are.

**Fixes found by the check, made in the definitions**: the Zwinger's and Schwerin's bridge steps climbed 60 cm past the
deck (`top` is the deck's 0 now, four steps from the shore); Didyma's front stair stopped on the crepidoma's lowest
step -- it climbs over the steps to the stylobate's edge; the windmill's cap overhung the tower on nothing -- it turns
on a timber CURB laid on the wall head and reaching out under its eaves; the hen house's perch ends 1 cm into its end
boards (it stopped 6 cm short of both); the stable's hay is a heap on each stall's floor showing over the half-door (a
cap of it hung at the door's height); the fountain's finial is closed underneath and sits on its stem; the landing's
stair comes down onto the stage, through a break in the deck's rail (it came down past the stage's end); the mine's
windlass has an axle through its posts, the crank arms on its ends and the grips on the arms, and its walking shaft's
landings are as deep as a flight is wide (room to stand at the next flight's foot); the marquee's roof is planned on
its walls' outline and takes their heads into its sheet, its poles under the ridge's ends; the longhouse's ends are
walls with doors (they were 12 cm enclosures, inside out); the pueblo's second ladder climbs level 1's west face from
the terrace (it climbed inside the rooms); the pit house's steps come up from its floor through a gap in the lining,
beside the ridge post.

## The hall church, and tracery drawn with compasses (2026-10-27)

**A HALL (`basilica` with `hall: true`, gothic.js `hallLevels`).** Stephansdom was assembled from old parts: an
enclosure, a row of columns, groin vaults, a flat ceiling box and a roof, its long walls flat, with nothing to take
the vaults' thrust. A Gothic hall church is a structural type of its own: nave and aisles vaulted from the SAME
capitals (the aisles' keystones as high as the nave's, or `aisleDrop` under them: Vienna's stepped hall), so there
is no clerestory, no triforium and no aisle roof, and nothing for a flyer to stand on. The light comes in through
the outer walls, which stand to the vaults' extrados with tall windows under the aisle vaults. One roof covers all
three vessels, its eave on the outer wall (the high roof's eave line is the outer line, hipped over the apse). The
thrust is taken in the wall's own plane by deep stepped buttresses at every node, round the apse's polygon as down
the flanks. Each buttress's head stops under the eave and its pinnacle stands out past the overhang, in front of
the roof. The arcade wall is only the strip from the arch up to the vaults, and the arch rises as high as the lower
of the two wall arches over it allows. The vaulting shafts are gone, since the vaults spring from the piers'
capitals. `skipButtress: [[from, to]]` leaves a node bare where a tower stands against the wall. A hall has no
transept here (it says so). Stephansdom is now one `basilica` hall: ten bays, a five-sided apse with its
ambulatory, the two towers against the wall on the sixth node, the west front across the open west end, and a
west gable cut to the roof's pitch: two prisms whose `slope` falls with the roof.

**TRACERY (tracery.js), an opening's `tracery`.** `true` takes as many lights as the span allows; a number gives
the lights; `{ lights, foils, bar, depth }` sets each. The tracery is drawn from the window's own arch by the rules
masons used:
- mullions split the span into equal lights;
- the lights are gathered under sub-arches of the window's own profile at their smaller span: in pairs when even
  (a 4-light window is two 2-light windows under one arch, so the rule recurses), one each when odd;
- in the head, the largest circle that fits on the axis between the sub-arches and the arch over them. In an
  equilateral 2-light window that is the classical quarter-span oculus √5/4 of the span up; it is found, not
  placed, so it holds for any profile;
- foils are cusped inside the window's top circle: four over a pair, three over an odd row, each touching its
  neighbours and the ring.

A ROUND window (a head and a foot) is a ROSE: a hub, an even number of spokes, a pointed arch over each light, and
between each two arches and the rim the largest circle on the spoke's line. Every line is a bar of one width and
depth, centred on it, in the middle of the wall round the glass. `glassPanes` builds the bars into `g.tracery`;
the part with the glass gets a `<name> tracery` part (kind `tracery`, stone, a shell). `basilica` tracers all its
windows and roses unless `tracery: false`. Cost: the sub-arches use a step coarser segmentation than the head, the
circles 8 to 12 sides, the foils 6 to 8, and the small circles over the sub-arches are left plain. Notre-Dame,
Cologne and Stephansdom together went from 89k to 124k vertices.

**Other tracery styles.** `style: "perpendicular"` fills the head with panels: mullions run up into the arch,
transoms cut the tall lights about every 1.6 widths, and a small pointed head stands under each transom
(Parliament's tall windows). `style: "bars"` draws a sash: 50 cm panes in 5 cm bars, rows 1.35 panes tall, and a
fanlight with radial bars where the head rises past 0.6 of the half span (Moritzburg). Moritzburg finishes its bars
white, like its dormers (`"parts": "kind:tracery"`). Milan, Ulm (stages and octagon included, by a `lights` param)
and the basilica's clerestory (`clearLights`) use the geometric rule.

## Envelopes that close, and one place one finish (2026-10-27)

**A VAULT IS ROOFED (check.js `vaultsRoofed`, in archcheck's support column).** A groin vault's cells open on
every side in their wall arches, the lunettes. A wall must stand in each lunette, or an arcade under it, up to
the wall plate the roof sits on. Two buildings had walls stopped at the vault's springing under a roof set at
its crown, leaving the lunettes open to the sky: Florence along the whole nave, and the basilica example at both
end walls. The check casts level rays from the middle of every bay out through its four mouths, at 0.4 and 0.8
of its rise. A ray that escapes the building is a hole if something stands just under its path past the mouth:
the top of a wall stopped short. Under a loggia's open arch the air runs down to the floor, so it is not flagged.

**Florence, set right.** Florence's arcade and flank walls had been set on centre lines, but a wall stands on its
line with its thickness behind it. So the arcade ran 1.5 m into the nave vault and left a slot from the floor to
the roof beside the aisle vaults, and the flanks stood 90 cm inside the facade's ends. `halfB` and `halfA` are
now outer faces. The clerestory rises to `naveTop`. The tribunes were rings of 6 m arches open from the
pavement, with the green course crossing each one in mid air. They are now chapels lit by a traceried lancet in
each face. The basilica example is roofed too: a gable roof over the nave and lean-tos over the aisles. Its end
walls step in at the aisles' wall plate (`eaveA`) and rise to the nave's (`east gable wall`; `west rose` with
`west aisle ends` beside it).

**ONE PLACE, ONE FINISH (finish.js).**
- A face's bands are asked at five points spread evenly along the line the band's level cuts through the face,
  each counting alike. Before, a band was asked at its largest triangles, weighted by area. Moritzburg's
  courtyard facades went white (inside) because their largest triangles were their two ends, buried in the
  hollow corner towers.
- A FLOOR under cover is inside if rays close all round at two of its three heights (a room or a nave, broken
  only by doors low down), or if under a tenth of all 48 level rays escape. Each height is turned a third of a
  step from the last, so a point lined up behind an arcade's pier doesn't find its rows blocked by the same
  piers. Before, one closed height was enough, and a loggia, closed only in the spandrel band under its deck,
  came out as a room.
- A WALL OR SOFFIT FOUND CLOSED IN GOES AS THE FLOOR UNDER IT. A loggia's back wall and ceiling face a cover and
  little sky, but the loggia's floor is open sideways, so it is outside. Parliament's river loggias now read as
  one outdoor space: limestone wall, ceiling and pavement, where the walls and ceiling had been painted faux marble.
  The same rule moves portico back walls, and the Frauenkirche's corner towers above the cornice, to their outside
  finishes.
- Stephansdom's west gable prisms had their `at` in the wrong order. A part's `at` is `[x, y, z, yaw]`, so the
  two halves had been standing in the nave. They now close the roof's west end.

## The wimperg: a gable drawn from the arch under it (2026-10-27)

`arch/wimperg.js`. Any opening may say `wimperg: true` (or `{ pitch, coping, depth, crockets, finial, field, shafts,
side, top }`); a `basilica` says `wimpergs: true` for its aisle windows and transept portals, and the `gothic`
generator's `portalGables` puts one over each west portal (Cologne: yes; Notre-Dame, whose portals stand under the
gallery of kings: no). Nothing in it is placed by eye -- every line follows from the opening laid out by `wallFace`:

- the ARCHIVOLT: a band a coping wide round the arch's extrados (the curve offset along its own outward normals), run
  on down both jambs to the sill, so it frames the opening from the ground (or sill) up -- it stands where the opening
  stands;
- the ARMS at the pitch asked (62 degrees), spread as wide as they must be for their inner edges to clear the archivolt
  by a quarter coping everywhere. (Steepening the pitch cannot do it: at a pointed arch's foot the archivolt rises
  straight, so the arms' feet must stand out past it -- as the masons set them);
- the SHAFTS the arms' feet stand on, from the sill to the springing: the gable is carried, not stuck on the wall;
- the WALL'S TOP bounds it: `glassPanes` is told how high the wall it is part of rises (a tiered wall: all its tiers),
  and a gable whose apex would stand over it is tried flatter, down to 40 degrees, and left off if none fits -- it never
  pierces the roof over the eave. The finial takes what room is left, or is left off;
- CROCKETS every three copings up the outer edges, a FINIAL on the apex, and in the FIELD the largest circle on the
  axis touching both arms and clear of the archivolt's crown, a trefoil cusped in it when there is room -- blind
  tracery drawn with tracery.js's `barsMesh`, a bar's depth proud of the wall.

`side: true` sets it on the face's back, for a wall whose outside is `map`'s far side (a basilica's aisle wall).
All of Stephansdom's aisle windows cost 2,775 vertices.

## Courses: plinth, string course, cornice as the wall's own (2026-10-27)

`arch/courses.js`. A `wall` or an `enclosure` may say `courses: true` (or `{ plinth, strings, cornice, skip }`): the
mouldings run along its outer face, each a PROFILE (`PROFILES`: plinth -- a water table; string -- a band with a drip
and a weathered top; cornice -- corbelled out to a corona with a cyma; band) carried along the face's line at a height
the wall gives:

- the PLINTH at its foot, the CORNICE crowning its top, a STRING COURSE at every TIER JOINT -- the floor line where one
  storey of the facade stands on the next (or `strings: [heights]`). Sizes follow the wall's height, the projection each
  moulding's own height; any may be `{ h, out, profile }` or `false`;
- round a corner of an enclosure every line of the profile runs on to where it meets the neighbouring face's offset
  line -- a true MITRE, out on a convex corner, in on a concave one -- so a cornice turns a tower's corner as one moulding;
- an opening whose height it crosses STOPS it at the jambs, its end closed with the profile (a door breaks the plinth, a
  window the string course it would cut); so does a wall's free end;
- `skip`: faces (number, label or family) it does not run along -- one against a neighbouring block, or inside one; a
  moulding coming to that corner ends flush there, so the neighbour's own course takes up from it.

They are a part of their own, "<name> courses", kind `moulding` (open at the back: a shell). St Paul's arms and west
towers carry them: the plinth, the floor line at 15m and the cornice under the balustrade run round the whole
cross and its towers, and turn every corner.

A RING bay (a rotunda's drum, the Pantheon's 24-gon) is built once and turned round the ring, so its courses could
not see their neighbours: the bay's line is laid with the neighbouring bays' first and last segments as GHOSTS --
mitred into, not drawn -- so each bay's cornice ends on the very plane its neighbour's starts on, and the turned copies
meet in true mitres. `clear`: spans of a face (keyed by number, label or family, `[[x0, x1], ...]` along it) the
courses leave free over their whole height -- the Berliner Dom's body runs its mouldings only between the corner
towers, which carry their own. `strings: { at: [heights], h, out, profile }` gives a string course its own heights and
section: the Pantheon's drum is banded by a cornice-profile course at 12.4m between plinthless brick and its crowning
cornice (all marble, kind `moulding` in its finish).

`courses.inner` runs them along an enclosure's INSIDE face (its inner outline walked backwards, so the inside is on
the left; an opening at x on the outer face comes through at the face's own square-reveal mapping, `innerAlong` in
build.js). A `court` with `courses` gives them to both its rings of wall: the outer walls on their outside -- stopped
where a joined building stands against a face -- and the courtyard walls on the face the court sees; its eaves reach
past the crowning cornice. The `palace-wing` component carries them too: a plinth and a band under each floor, and a
top storey of its own whose cornice is sized by the whole front, not by the storey.

TRIM in the finishes (finish.js): a part of kind `moulding` or `wimperg` is one material over all its faces -- every
face of it a wall, outside -- so a cornice's top does not take the terrace's flagstones and its underside the
ceiling's plaster, nor a court's string course the rooms' faux marble. What no rule names takes the facade's own
finish (relief, not colour); `{"parts": "kind:moulding", ...}` gives the trim its own -- Melk's and Moritzburg's white
on the render, Schwerin's dressed sandstone.

## The applied order: pilasters and entablature from the storey's height (2026-10-27)

`arch/order.js`. A `wall` or an `enclosure` may say `orders: [{ tier, kind, span, ends, proj }]`: an order of
pilasters standing in storey `tier` (and rising through `span` of them: a giant order), set out the way Vignola set
out every order -- from the height it has to fill:

- the height from the pilasters' foot (the top of whatever course runs under it: the plinth, a string course) to the
  storey's top is divided into MODULES (the column's radius): the column takes 14 (tuscan), 16 (doric), 18 (ionic) or
  20 (corinthian), the entablature a quarter of that (`VIGNOLA`); so the storey gives the module and the module gives
  everything else -- the pilaster two modules wide and half a module proud (`proj`), its base and capital by
  `ORDERS` (the same table the free-standing columns use), architrave, frieze and cornice by Vignola's shares, the
  cornice reaching out as far as it is tall;
- the PILASTERS stand on the piers between the storey's openings, in the middle of every pier wide enough for a
  capital clear of both windows, and at each face's ends (`ends: false` leaves those off): in from the corner by their
  own half and by what the next face's pilaster reaches out, so a convex corner has one on each face side by side and
  a concave one keeps them clear of each other;
- the ENTABLATURE is a course with its own section (`pts`, in metres) -- run round the whole building by courses.js,
  mitred at every corner, stopped where something cuts through it -- its architrave flush with the pilasters' faces,
  so they carry it. It takes the place of the string course at the order's top and of the cornice when the order
  crowns the wall; a giant order has no string course across it.

Pilasters and entablature are drawn into the wall's "<name> courses" part (kind `moulding`: one trim material).
St Paul's arms carry two storeys of Corinthian pilasters; Versailles was rebuilt on it: each block of the plan ONE
enclosure (its courses mitred round its corners, `clear` where another block stands against a face), Ionic pilasters
through the piano nobile and a Tuscan attic order over them on the stone blocks, the brick court wings only their
courses, the ground storey rusticated (a finish band), a pierced balustrade on the wall heads round the roof slab --
where the old port had cornice boxes overlapping each other at every corner and pilasters as loose boxes.

## The window surround: architrave, sill, cornice, pediment from the opening (2026-10-27)

`arch/surround.js`, the classical counterpart of the wimperg. An opening (in a pattern or a list) may say
`surround: true | { band, depth, sill, keystone, head, pediment, pitch, side }`, and every size comes from the
opening's own width:

- the ARCHITRAVE is a band a seventh of the opening wide (`band`, held between 12 and 40 cm), half that proud. It
  frames the jambs from the sill up (from the ground for a door) and then the head: a lintel over a flat head, or a
  band carried along an arched head with a KEYSTONE at its crown (`keystone: false` leaves it off);
- a window's SILL is a slab reaching past the architrave and standing out twice as far, so it sheds the rain
  (`sill: false` leaves it off);
- the HEAD over the architrave is a frieze and a cornice (`head: "cornice"`), and on the cornice a PEDIMENT
  (`head: "pediment"`, the default). It can be triangular at the classical 22.5° (`pitch`), segmental (an arc rising a
  quarter of its half-width), or `alternate`, the two taking turns along the row with the middle one triangular, as
  on Roman palace fronts (the row numbers each surround by how far it stands from the middle). `head: false` gives
  the architrave alone. A head that would rise past the wall's top falls back to its cornice, or to the architrave;
- `side: 1` sets it on the face's back, as with a wimperg: the court type uses this on its courtyard walls, whose
  face towards the court is their back.

It is drawn into the wall's "<name> surrounds" part, kind `moulding`, so it takes the trim material. Its slabs leave
off their backs, which lie flush on the wall. The court type takes `surround` as one spec for every storey or as a
list storey by storey. It puts the ground storey's on the outer windows, the gate and the court doors, and the upper
storeys' on both rings of windows. Melk is plain on the ground floor, has cornice heads on the two main floors and is
plain under the main cornice. Schwerin has alternating pediments on its piano nobile. Versailles has architraves and
keystones round the arched windows and cornice heads on the brick wings. Melk's palace wing has its own surrounds,
storey by storey.

## Folded pilasters, plinths that break forward, and two buildings dressed (2026-10-27)

- A shallow OUTER CORNER (a polygon's, turning less than about 46°: an octagon's, a rotunda's sixteen faces) no
  longer gets two pilasters side by side, one in from each face. It gets ONE pilaster FOLDED over the arris: each
  face draws its half, its end mitred by the tangent of half the corner's turn, so the two halves meet in one block
  (`pilasterSpots` returns `folds` beside `spots`; `pilasterMesh(..., fold, k)`). A square corner still has one
  pilaster on each face.
- A pilaster's base reaches out further than the plinth or string course it stands on, so it stood on air. The
  course now BREAKS FORWARD under every pilaster: a block from the course's foot to the pilaster's foot, as wide and
  as deep as the base (`yb`, the foot of the course under the order).
- Finishes:
  - A point inside a tall solid (the foot of a 30 m column) counts as buried all the way up, not only within 8 m.
  - A floor piece that a wall's foot crosses (some sample points under stone, some open) is halved down to 0.6 m
    even when its open points agree.
  - The pavement at a wall's foot, under a cornice reaching out over it, counts as outside when three of eight ways
    round at 46° see the sky. Before, the ground between pilasters there took the inside floor's checker.
- St Isaac's has a giant Corinthian order through its two storeys of windows. Its entablature sits at the porticoes'
  height and runs round the building, with an attic over it. The lower windows have triangular pediments, the upper
  ones cornices, and the plinth is red granite like the porticoes' columns.
- Karlskirche:
  - The church's door was on face 0, which on a sixteen-sided plan sits 22.5° off the axis, with a window on the
    axis behind the portico. It is now on the axis (face 15).
  - The side halls' doors were on faces 2 and 14, one on each side of the portico, so neither led into a hall. Their
    rectangular plans never met the church's wall either. Each hall is now a pentagon whose inner end lies on the
    church's diagonal face (faces 1 and 13, the two wall faces in one plane), with a door through both walls.
  - The church has a giant Corinthian order folded round its sixteen corners. The halls are as tall as the
    portico's entablature and continue its order out to the pavilions. Each pavilion has a Doric order round its
    arches and an Ionic one above.

## The Frauenkirche carried down to the ground (2026-10-27)

- The drum and the stone bell stood on the attic roof, a solid filling the whole square from the cornice to the
  ridge, with nothing under it inside. The drum now stands on a RING OF PIERS (`dome piers`): the drum's own sixteen
  faces carried down to the floor, with the same corners (`turn` 0 sets a pier under each corner of the drum) and
  the same thickness, arched between, up to the drum's foot.
- The attic roof is a `shell` over an open attic. Between the walls and the piers, a slab over the galleries
  (`vaults`, a `prism` on the church's inner plan) forms the attic floor. Its `well` is the piers' inner polygon,
  so from the floor the church looks up past the arches into the drum and the bell.
  - Wells take `turn` (build.js `wellPoints`), so a well can follow a polygon plan.
  - A prism passes `railing: false` through to its well's edges, so an attic floor nobody walks gets no rail round its hole.
- ROOFS ON CHAMFERED PLANS: a roof takes `chamfer`, the corners cut that far along each side in the wall plane.
  Every level of the roof becomes an octagon whose corner face comes in as far as the slopes beside it
  (build.js `chamferLevels`, with `roofMesh` drawing eight-sided rings and fans). The Frauenkirche's mansard is now
  hipped down onto its chamfers between the stair towers, where it used to overhang them as a square.
- The east front, where the choir stands against it: the middle bay is the CHOIR ARCH, the church's full-height
  opening into the apse. The flanks' windows have moved out past the apse wall, which used to cut through them.
- Finish: the piers and vaults are plain plaster, the structure, and the painted panels stay on the walls between them.

## Masonry does not stand on roofs; orders round rings; the Zwinger dressed (2026-10-27)

- A NEW CHECK, "on roof" (check.js `floating`). A wall, a ring of walls, a drum or a dome is carried down to the ground
  through walls and piers; a roof is a covering on rafters. A masonry part with most of its foot on roofs alone is
  reported. Two cases are excused:
  - a point where masonry stands within 1.5 m under the roof surface, as with a flat roof slab laid on walls,
    carrying the parapet above them;
  - a part fixed to masonry halfway up its side, as cladding is (a marble band on an octagon's wall, its foot on
    the roof against it).
  It finds the old Frauenkirche's drum. On the full set it found:
  - Milan's tiburio, standing on the nave roof. Milan now has a crossing that carries it: a DIAPHRAGM wall at each
    end of the two crossing bays, over the transverse arch and pierced by it, from the vault's springing to the
    roof's foot. The tiburio's octagon is widened so that its sides stand on the clerestory walls and its ends on
    the diaphragms, its foot at the clerestory's top (inside the roof, as a crossing tower rises through it).
- ORDERS ON RINGS (assemble.js, ring): `orders: [{ kind }]` over the ring's height. A pilaster on every pier is folded
  over the corner between two bays: each bay draws a half at either end of its face, and the neighbouring bay, the
  same bay turned, draws the other half. The entablature runs round as a course mitred into the next bays.
  `dress: "in"` puts the ring's courses and order on its INNER face, walked backwards so that what it faces is on
  its left, with the corners turning in: the court side of a curved gallery's inner wall.
- OPENINGS KNOW THE ORDER OVER THEM. The courses and orders of a wall are planned before its openings are drawn
  (`orderPlan`). Every tier an order spans gets a `top` at the entablature's foot (`withOrderTops`), and a window's
  surround or wimperg stays under it: a pediment that would rise into the architrave is left at its architrave.
- COMPONENTS DRESSED ON REQUEST:
  - An order of kind "none" is none, so a component can name its orders by parameter (`"kind": "order1"`) and stay
    plain by default.
  - `courses` and `surround` may be flags over the parameters (`"courses": "dressed"`).
  - The pavilion, gallery and curved-gallery components take `order` / `order1`, `order2` and `dressed`. The
    galleries take `head`, the wall left over their arches (1.2 by default, room for an entablature when ordered).
  - The pavilion's arches crown a fifth of each storey below its top.
- THE ZWINGER, one decision for the whole court: the galleries' arches between Doric pilasters, with an entablature
  under the terrace balustrade, the curved galleries dressed on both faces. The pavilions have Doric pilasters round
  their arcades, Corinthian above, and framed windows. This cost about 50k triangles (balusters remain the largest item).
- THE ARENA's two outer arcades take a Tuscan order (`orders: [{ kind: "tuscan" }]` on the rings), as the Colosseum's
  lowest storey does: a pilaster folded over every pier between two arches, the entablature running round over them,
  and the plinth breaking forward under each pilaster's base. 0 findings, 57.6k vertices.

## Built in order; the pedestal (2026-10-27)

- BUILT FROM THE GROUND UP (check.js `floating`, finding "before support"): the parts are raised in their build order,
  as a mason raises them, and each must be carried by what stands already, the ground or a part built before it. A
  part carried in the end, but only by a part built after it, is reported along with the part it waits for. It then
  counts as built, so nothing standing on it is reported again. On the first five buildings it found one: Florence's
  gallery between the shells, which was built before the inner dome it rests on. archcheck prints "waits for <part>".
- A NAME STANDS FOR A WORD as it does for a number (expr.js `evalValue`): a component's `"stone": "stone"` takes the
  word the building gave it ("bronze"). A marker's data is read over the parameters inside its tables too (a
  statue's `hold: { R, L }`).
- THE PEDESTAL (components/pedestal), proportioned as the classical writers have it: the BASE (a plinth and a
  moulding over it, a quarter of the height), the DIE (three fifths) and the CORNICE (a bed moulding and the slab,
  the rest). The base and the cornice stand out round the die, the cornice further. On it stands a `statue` marker:
  the carved figure (statues.js), given its kind, style, stone, scale and what it holds by parameter. Sacre-Coeur's
  saints over the porch (bronze, gothic) and the Berliner Dom's six figures (limestone) were green and grey blocks
  and columns; they stand on pedestals now.
- The full set with the new rule: 13 buildings had parts listed before what carries them. All are reordered at their
  source:
  - piles before the crannog's platform and the jetty;
  - legs before tables and benches, posts before the hitching rail;
  - floor rings before the windmill's floor discs;
  - Sultan Qaboos's platform laid first (it was added last);
  - the Pantheon's floor before its niches;
  - Versailles' stairs after the floors they start on;
  - the arena's landing walls before the landing;
  - the tents' poles before their roofs and the pavilion's valance after its roof;
  - the longhouse's walls before its vault.
- Parts named alike but for a trailing number ("upper floor 3" and "upper floor 7": one floor cut into pieces round
  its stairwells) are one element. A piece may lean on another piece of the same element wherever that piece is
  listed.

## The fortified ward: Caerphilly from the rules of defence (2026-10-27)

A `ward` part (arch/castle.js `wardDefs`; assemble.js builds what it writes, as for `court`) is a curtain round a
convex `plan`, its outer face line, `height` to the wall walk and `thickness` thick. Everything else follows from the
rules a thirteenth-century mason worked by:
- FLANKING: a tower on every corner, centred on the corner of the outer face, projects its whole radius past both
  curtains it joins, so its loops see the foot of each. A face longer than `towers.flank` (40 m, bowshot between two
  towers) gets towers between, evenly spaced.
- GATES (`gate` or `gates`: face, width, height, radius, at): a passage through the curtain between two towers that
  stand clear of it on either side. The curtain and the walk carry on over it.
- THE WALL WALK is the curtain's head behind a CRENELLATED PARAPET on its outer edge. The parapet is one wall with
  crenels cut down from its top as notches, `step` apart and `crenel` wide, the merlons wider than the crenels.
- THE TOWERS rise `over` above the walk, with a floor at the walk and every `storeyH` below it, and a deck with its own
  crenellated parapet on top. Every level is a whole number of treads (the rise is worked from the walk's height),
  so ONE NEWEL STAIR climbs from the ward to the deck past every floor, through a well in each. It stands against the
  wall a quarter turn from the door and arrives on the deck through a railed well.
- THE WALK RUNS THROUGH THE TOWERS: a doorway at its level on the face where each curtain's walk line meets the tower.
  The faces a curtain (or, above the walk, its parapet) stands against are blind.
- LOOPS look onto the field, staggered storey by storey so that no vertical line of the wall is cut all the way up.
  Every storey also has a loop on the first face clear of each curtain, the one that rakes its foot. The face onto the
  ward has the door below and windows above. A storey too low for a loop gets none.
- Curtains and parapets end inside the tower walls, square, clear of the room.
- THE TALUS: the foot of the curtain and the towers spreads in a batter (the courses' new `batter` profile, a plinth
  of one slope), at one level all round. It is a quarter of the walk's height, sloping one in three and a half. It
  throws stones dropped from the parapet out at attackers and thickens the wall where it would be mined.
- MACHICOLATIONS over every gate: the parapet over the gate is carried forward on corbels a metre apart, with holes
  between them over the passage's mouth. The build-order check caught the first draft, which built the parapet before
  its corbels.

CAERPHILLY is two wards now, CONCENTRIC: the inner ward is higher (9 m to the walk), so both lines can shoot over the
outer one at once. The inner ward has four drum towers and the twin-towered gatehouse to the front; the outer ward
(5.5 m) has a turret on every corner and gates front and back between pairs. It replaces solid columns, boxes for
parapets, and lifts onto the tower decks. 0 findings (the stairs walked foot to arrival), 24.1k vertices.

## The Egyptian temple: Dendera from the rules of the axis (2026-10-27)

Dendera was fourteen parts, thirteen of them boxes: a temple modelled as blocks with nothing to say why any block was
where it was. It is now set out by the rules the Egyptian temple is built by (tools/archgen/dendera.py), and the
engine has learnt the pieces those rules need:
- TWO NEW PROFILES (courses.js): the `torus`, a half round, and the `gorge`, the cavetto cornice, a hollow rising out of
  the face and sweeping forward under a fillet.
- COURSES AS A LIST: `courses: [{ y, h, out, profile }, ...]` (or `{ list, skip, clear }`) when a wall's mouldings are not
  plinth, string courses and cornice. The Egyptian wall is `crown(H)`: a BATTER from the ground leaning back 1 in 12, the
  torus over it, the gorge (a ninth of the height) on top, all sized from the wall's height. A `clear` stretch may now
  give `[x0, x1, y0, y1]` and stop only the courses in that height band. The pronaos's back face keeps its torus and gorge
  above the lower temple it stands against and loses only the batter there.
- EGYPTIAN ORDERS (assemble.js ORDERS): `hathoric` (a flat disc base, a barely tapering shaft, the goddess's four-faced
  block, the sistrum's shrine with its lip, and an abacus narrower than the shaft) and `campaniform` (a bell turned as one
  `lathe` surface, swelling slowly and then fast, with a small abacus on its broad top).
- THE HYPOSTYLE (`colonnade` with `plan: "grid"`): `count` files at `spacing`, the middle intercolumniation `nave`, `rows` at
  `rowSpacing`. Its entablature is ARCHITRAVES over the files, front to back, with `reach` [a, b] how far each runs past
  the first and last rows (to the facade's and the back wall's faces), so the roof slabs span across from beam to beam.
The temple itself:
- ONE AXIS: the pronaos (6 × 4 Hathor columns, the middle aisle 1.3 times the rest; the front row standing in the open
  facade and joined by half-height screen walls with their own gorges, the middle bay a door with a broken lintel), the
  Hall of Appearances (six campaniform columns, three store rooms either side behind partitions, each with a door), the
  Hall of Offerings, the Hall of the Ennead, and the sanctuary standing free in its corridor with the naos in it.
- FLOORS RISE AND ROOFS FALL: each hall is a list entry {depth, floor, soffit, wall}. At every door the floor steps up (a
  short flight on the lower side, a threshold through the wall at the higher level), and each roof is lower than the one
  before. Each cross wall is built up to the soffit of the hall in front of it, so that hall's slabs bear on it and the
  lower roof behind abuts it: the roof falls in steps exactly where the walls are.
- THE ROOF IS USED: a newel stair in its own walled room off the Hall of Offerings climbs through a well in that hall's
  roof and arrives on the slab. Short flights on the axis join each terrace to the next one up, and the twelve-column
  kiosk with its screens stands on the lowest terrace's south-west corner. LION SPOUTS drain every terrace through the
  side walls, at its own surface under the torus, one either side for each 12 m of its length.
0 findings, 61 parts, 6.8k vertices (it was 14 parts of boxes).

## El Castillo counted by the calendar; the corbel vault (2026-10-27)

Chichen Itza's pyramid was right in outline, but its serpent heads and roof crest were boxes and its temple was a hollow
cube. Now (tools/archgen/chichen_itza.py):
- THE CALENDAR decides the details. 91 steps × 4 + 1 = 365. The nine terraces, cut by the stairs, give the 18 Haab months
  on each face. Each face carries 52 recessed PANELS (the Calendar Round): 26 on each side of the stair, shared among the
  terraces in proportion to their length by largest remainder (5, 4, 4, 3, 3, 2, 2, 2, 1 from the foot), the same on
  both sides, so every face is symmetrical.
- TALUD AND TABLERO: the crepidoma's new `tablero` share makes each step a leaning talud with a vertical band over it.
  The panels are a skin laid on that band with the panels cut through it, so the core shows behind them. Each terrace
  has one skin that runs on to the corner and one that stops at it; turned round the pyramid, the four faces close the
  corners without overlapping. The skins are dressed stone and the taluds rubble, so the recesses read.
- THE FEATHERED SERPENT as two components: `serpent-head` (the skull with its plume collar, wedge-shaped jaws gaping
  over the tongue, fangs, brow plates and nose curl, all from its width) and `serpent-column` (the head on the floor,
  the body rising out of its skull as the shaft, the tail bent forward as the capital under the lintel). Only the north
  stair has heads, as at the real one, and the check moved them clear of the treads' approach. Two serpent columns
  divide the temple's north door into three.
- THE CORBEL VAULT (profiles.js `corbel`: straight soffits leaning in at `slope`, closed by a capstone `cap`, optionally
  with `steps` showing) limits a Maya room's width, so the temple is narrow rooms: a gallery round three sides with a
  door in each, the portico, and the sanctuary, whose two pillars (the middle piers of walls along the axis, the
  lintels over them) cut its vault in three. The temple's HEIGHT is worked out, not given: the springing, the widest
  span's corbel rise, the capstone. The medial moulding runs at the springing, the cornice at the roof, and the
  crest of stepped merlons along the roof's edge.
0 findings, 9.8k vertices.

## Finishes checked for patches; the Romanesque opening (2026-10-27)

**A face in one finish per cell.** `finishPieces` now reports, for every wall face (not domes or vaults, whose
inside and outside are one skin), the area each finish takes in each CELL of it: the cells are cut by the rules'
own band and region lines (`below`, `above`, `within`) and by the face's level cuts between inside and outside.
A face may change finish at those lines -- the Iznik tiles stop at 12 m and kalemisi paint goes on above -- but two
finishes in one cell are a patch. `archcheck.py finish=1 minor=0.01` lists faces whose patched share is over
`minor`. All 93 buildings pass.

**The Romanesque opening** (`surround: { style: "romanesque", orders, band, depth, shafts }`, surround.js). The
opening is not framed but recessed in ORDERS, the outer ones standing furthest out. Each order has:
- a strip of jamb;
- a NOOK SHAFT in the angle of its step: a half-round on a base, under a cushion capital;
- a band of archivolt round the head, with the shaft carried on round it as a roll.

An IMPOST runs across every order under the springing. Measures come from the opening: the step is about a ninth
of the span. The step is limited by `o.room`, the free wall each side of the opening, which `glassPanes` now
works out from the face (half the pier when a neighbour shares it). So an arcade of dressed arches shares its
piers without overlaps. Orders are dropped until the archivolt fits under the wall's top.

Used on Fisherman's Bastion (the arcades in one order, the end doors in three) and Mainz Cathedral (its
transept portals in three orders, the tower openings in one).

**Covered faces on a diagonal.** Where two parts' faces lie in one plane, `coverIndex` drops the smaller one's
share. It compares them in 2D, projected along the plane's main axis. A face at 45° is as much x as z, and
rounding sent its triangles to different axes, so St Basil's chapels, whose diagonal faces share planes
across the gaps, had triangles compared in mismatched coordinates. The wrong pieces were dropped, and holes
showed the painted inside through the brick. Each plane cluster now uses one axis.

**The Lombard band** (lombard.js), the articulation of a Romanesque wall:
- LESENES, flat pilaster strips at the face's ends and every `bay`;
- under the top, an ARCHED CORBEL TABLE: a band with small round arches hanging from it, field by field between
  the lesenes, a whole number about `arch` wide in each, every foot on a corbel.

A lesene that would cross an opening is left out, and so is an arch over an opening's head. `lombard` goes on a
tier (`{ h, openings, lombard }`: one band per storey, as Romanesque fronts have it), or on a wall or an
enclosure, where it applies to the top tier of every face. It is drawn into the openings' dressing mesh, so a
finish rule for `kind:moulding` can set it off. Mainz's articulation is now in lighter dressed sandstone.

**The rising frieze** (`frieze` on a gable roof, `gableFriezeMesh`). The same corbel table runs up both rakes
of the gable under a band that follows the slope. Each arch's crown sits under the band and its springing at
the lower of its two feet, so the row climbs in steps. It starts where the first arch clears the gable's foot
(the wall's own band lies below it), and the two rows meet at the apex. Used on Mainz's transept fronts and
towers.

`lombard` may also be a flag, or carry `on` (a flag over the params). The `basilica` component uses this: its
clerestory and aisle walls take the band when `lombard: 1`, with lesenes a bay apart, and Mainz's nave sets
it. The vaulted basilica (gothic.js) takes `lombard`/`aisleLombard` and a `surround` for its windows the same
way.

## Maria Laach: the helm, the dwarf gallery, and finishes by face (2026-10-27)

**The Rhenish helm** (`type: "helm"`, helm.js). This is the Romanesque tower roof of the Rhineland: a GABLE over
every side of the tower, and between the gables the roof's faces, each a RHOMBUS from a corner up past the two
neighbouring apexes to the point. Only the gables' `pitch` is chosen. A rhombus is flat only if the point
stands where the lines from the corners through the apexes meet, which is `g / sin²(π/n)` over the eaves for
gables `g` high on an `n`-sided tower: twice the gable on a square tower, about seven times on an octagon. The
helm takes `sides` (4), `radius` or a square's `width`, `pitch` (60) and `turn`. `frieze` adds a rising arched
frieze up every gable, as a moulding part of its own.

**Maria Laach Abbey** (tools/archgen/maria_laach.py) is the building that tries all of this: six towers, every
one with a helm. Its parts:
- the nave is the `basilica` component under groin vaults over oblong bays, with the Lombard band on its walls;
- the transept fronts carry rising friezes, and the arms have apsidioles;
- the westwork is a square tower over the west bay;
- two ROUND STAIR TOWERS (`round-stair-tower`, which now takes `doorW`/`archW` for narrow bays) climb from the
  aisles to the tower's floor. The number of steps is chosen so each landing faces the door into the tower;
- the PARADISE is an atrium of arcades in Romanesque orders, with lean-to roofs and a gabled west portal.

**The gallery apse** (`components/gallery-apse`) is the Rhenish apse with its DWARF GALLERY. It has:
- the half-ring wall with its windows;
- the conch, springing from the wall's inner face;
- under the eaves, a PASSAGE inside the wall's thickness, with an open arcade on the outer face and a solid
  wall behind;
- a half cone over all.

The passage's floor is not chosen. The conch's back rises inward from the springing, and the floor goes where
that back has dropped below the passage's inner edge (`spring + sqrt(cr² − rp²)`), so the walk never cuts into
the vault. The old Mainz apses opened the gallery straight through the wall into the void over the conch;
Mainz's four apses now use the component.

**`outside: true`** on a part says its faces belong to the open air, whatever the finishes' rays make of them.
The dwarf gallery's passage is open through its arcade but too narrow to see out of, and the rays called it
a room.

**Finishes by face, not by plane.** facesOf now joins flat pieces of one face that share no edge, as long as
they lie in one plane and touch. Examples are a wall's courses on either side of an opening, a tier's seam,
and the bars of a tracery. Such a face is asked once and is inside or out as a whole. The patch check (`mixed`)
is keyed by that face, and reports where each finish was first met (`at`). The plane-keyed check flagged 12
buildings, all of them coplanar faces far apart: the two ends of a vault, a stair's risers a flight apart.
With the face key, 0 are flagged.

**Bands cut where the cover is.** Where two of a face's 3m bands disagree (a wall inside under a roof and
outside above it), the face is asked again between them, halving the gap down to 20cm. The finish changes
where the roof meets the wall, not on the 3m grid. A covered FLOOR is asked at shares of its whole height up
to its cover (0.3, 0.55, 0.8 from the floor), not from 1.2m up, so a low gallery is asked through its arches.

**Hidden sides.** proudOf's `slab` takes `hide`, a list of side edges that stand against something just as
proud. The Lombard band's spandrels skip their tops (under the band) and their uprights (against the next arch
or a lesene); the lesenes skip their heads and feet; the corbels skip their tops. This cuts about 45% of a
frieze's triangles. A Romanesque head's curve is also thinned to about 12cm a segment.

**The Lombard band stops at what stands against the wall.** `lombard.clear` lists stretches of a face, each
`[from, to]` in face metres, where something stands against it, such as a stair tower or a buttress. The band
and its lesenes stop at either side, and each remaining stretch is laid out as a face of its own, with whole
fields and whole arches. Maria Laach's west bay uses this where its round stair towers meet it, so the corbel
table does not run through a stair's headroom.

**Lombard bands on rings.** A ring passes its `lombard` to each bay's face, so an apse or a round tower gets
lesenes and an arched corbel table bay by bay, as at Maria Laach's west apse.

**A crossing stage roof.** At Maria Laach the square crossing stage carries a low pyramid (pitch 30) from its
eaves to the foot of the octagonal tower. The stage's top is not left as a flat terrace that rain would stand on.

## Abutment: every vault's push is taken (2026-10-27)

An arch pushes out at its feet as well as down, so a vault needs masonry behind its springing. The new check
`abutment` (check.js, run by archcheck with the support findings) follows that push from every springing:
- a barrel's along both sides;
- a groin vault's from its four corners, out along each of its two spans, a hand to either side of the corner
  (into whatever pier is there);
- a ring vault's at the middle of its bay, out and in.

It walks the push level, a little above the springing, and also down from the springing joint at two slopes, as
the weight above turns it. Masonry (inside some part's solid) counts. Covered air is passed through: the next bay
pushes back, or it is an aisle under its roof. The walk stops at open sky. The best of the three walks must be at
least a tenth of the span. A finding is `thrust`, with the abutment found (`gap`) and what was needed (`need`).

Measured across the buildings, Romanesque and Gothic nave vaults have 0.13–0.17 of their span. The vaults a Gothic
system lays out are skipped, because gothic.js sets their flyers out from the thrust. A part built `light: true`
(poles, laths and bark: the longhouse's barrel) is skipped too, since it pushes nothing.

The check and the support check found faults in the element demos (assets/architecture/elements), which archcheck
does not cover:
- The barrel vault's walls stood off to one side and along the wrong half of its length, so one side sprang from
  air.
- The groin and rib vaults had their corners on slender columns, or on nothing. They now stand on square piers
  under their corners, each reaching past its corner.
- The cloister vault stood on the ground. It now covers a square room.
- The Byzantine exedra stood on nothing, its mouth open to the sky, so it was removed.
- The semidomes stood alone. They now open from an end wall over their arch.
- The rotunda's lantern hovered over its dome, and the minaret's upper shaft hovered over the balcony. The
  minaret's cap now sits on a cornice.

Also, a stair's arrival floor now lists its posts before its slab, the order they are raised in.

## Shikhara and samvarana: a tower made of copies of itself (2026-10-27)

A Nagara temple tower can't be modelled well from its outline. Its form comes from rules, and shikhara.js builds
it from those rules.

**The ratha plan** (`rathaPlan`): a square divided along each side into offsets.
- `rathas` 5 makes it pancharatha: karna, pratiratha, bhadra, pratiratha, karna.
- The bhadra is `bhadra` of the side wide.
- Each offset stands `step` further out toward the middle.

Every ring of the tower and of the hall roofs is this plan, scaled.

**The shikhara** (type `shikhara`: width, height, rathas, step, bhadra, top, bend, bhumis, nest, tiers, corners):
- **The body** is a stack of bhumis (storeys). Each is closed by a projecting band.
- **The rekha:** the sides bend in along a curve, 1 − (1 − top)(y/H)^bend.
- **The crown** sits on the shoulder: neck, ribbed amalaka, chandrika, amalasaraka and kalasha (crownMesh). A small
  crown is simplified.
- **The urushringas** are COPIES of the tower: smaller, with fewer rathas, set into the middle of each face, tier
  by tier. Each tier gives `{ scale, lift, out }`, where `out` is how far the copy stands out of the face (0.45
  shows a little under half of it). Copies of copies follow, as deep as `nest` allows.
- **Karna shringas** (`corners`) stand on the karnas at the heights given.

The copies are parts by tier, "shringas 1", "shringas 2" and so on, because insideOf counts crossings part by part
and would be fooled by overlapping solids inside one part.

**The samvarana** (type `samvarana`: width, length, rise, tiers, top, bells, rathas): a hall roof.
- It is a stepped pyramid of slab courses on the ratha plan, each course set back from the one below.
- A bell stands on every course, at the corners and over the bhadras (`bells: false` makes the plain phamsana of
  a porch).
- A bell-crowned finial sits on top. `length` stretches the plan for an oblong hall.

**Kandariya Mahadeva** (kandariya.py) builds its parts in the order they are raised:
- the terrace and its stairs;
- each unit's moulded plinth;
- the sanctum: a square core on the karna line, with the pratirathas and the back bhadra set against it (a wall
  0.3 m deep can't be 1.2 m thick: the inset outline would cross itself), and the cell inside;
- the balconies on the bhadras;
- the halls' parapets, pillars and beams, and the roofs on the beams;
- the tower on the sanctum's cornice.

That comes to 40k triangles, with no findings.

**Fix:** rathaPlan used to return the outline wound with the outside on the right, so every shikhara and
samvarana came out inside-out (negative volume in archcheck's mesh check). It now returns it in planPoints'
winding.

**Courses on solids.** A `box` or a `prism` now takes `courses`, as a wall or an enclosure does:
- the mouldings run round its own outline, closed and mitred at every corner, in and out;
- `clear` stops them where something stands against a face, such as a stair;
- the faces are numbered as an enclosure's are.

The Nagara plinth's mouldings are profiles in courses.js, beside the Egyptian torus and gorge:
- **khura**, the hoof: its top sloping steeply back;
- **kumbha**, the pot: a fillet, a swelling belly, a neck;
- **kalasha**, a smaller roll;
- **kapota**, the dovecote eave: its underside curling out to a drooping beak.

Kandariya's adhishthana is now ONE prism on the union of the units' outlines. Its half-width is a function of z,
because every unit is centred on the axis. The five mouldings run round all of its projections and stop at the
stair. The terrace's foot and eave are courses too. This replaced stacked boxes, whose tops counted as one big
floor (most of it buried) and so painted a strip of flagstones along each visible ledge.

**Rect face numbering.** planPoints reverses `rect` into its winding, so rect face 0 is the +z side, 1 is +x, 2 is
−z and 3 is −x.

**Roof slope mapping (finish.js).** v up a roof is the height divided by the mean sine of the roof's pitch. That
mean now covers only the faces mapped up the slope. Before, it also counted flat tops, which are mapped on the
plan. A stepped roof's course tops dragged it to its floor of 0.2, and the sloped faces' stone courses came out
squeezed by up to 3.5×.

## Lintels: a beam has a length (2026-10-27)

A flat head is one beam laid across its opening, of stone or timber, and no quarry or forest gives one longer than
a few metres. The Parthenon's architraves span 4.3 m from column to column. Wider than that, a builder turns an
arch, sets pillars in the opening, or corbels brackets out to shorten it.

**Walls and enclosures record their lintels.** Every wall and enclosure records the lintel of each flat-headed
opening as `lintels: [{ at, span, e, t }]`, in the part's frame (assemble.js lintelsOf).

**The check** (`lintels` in check.js, run by archcheck with the support findings) measures the FREE span: the
widest stretch of the beam's underside, jamb to jamb, with nothing standing under it. The underside is probed
every 10 cm, a hand under the springing, at depths from a wall's thickness outside the face to two inside. That
finds a pillar standing in the opening, a portico's column before it, or a bracket out of a jamb.

**The limit:**
- A free span over 4.5 m is a finding: `lintel`, with `gap` the free span.
- A part may say what its builders could set with `beam` (metres). Dendera's pronaos says 6.5, for the sandstone
  architraves over its processional way.
- A part built `light` (poles and laths) is skipped.

**What it found:**
- Kandariya's great hall had bare openings of 6 m and 5.6 m. Each now has two pillars standing under its lintel.
- Dendera's middle intercolumniation has 5.8 m free.
- The Greek temples' great doors are single marble lintels: the Parthenon's spans 4.8 m and Didyma's 5.5 m (on
  site 5.6 m, about seventy tonnes). temples.py gives the cella front `beam: 6`.

Over all 95 buildings, the full archcheck with the lintel check now reports 0 findings.

## Ranges along a line, tiered towers, and the first Japanese castle (2026-10-27)

Two new composite parts. Like `ward`, each writes the engine's own parts and builds them under its name
(`<part>/<sub>`), placed together.

**The range** (`range`, arch/range.js) is a building one bay deep carried along a folding line. Examples are a
covered walk on a city wall, the arcaded corridors of a bastion, a palace's long gallery, and the watari-yagura
of a Japanese castle.
- `path` is its middle line. `width` is one number, or one per segment. `height` is the height of the walk, and
  `side` says which side looks out.
- `bandPoints` mitres the band at every fold and refuses a path that folds back on itself.
- `faces` give the openings of the `out`, `in` and `end` faces, or of one face: `"out:2"`, `"end:1"`.
- `walk` lays a slab on top, just over the faces. `parapet` crenellates its edge from the corners in, with `gaps`
  where a stair or a tower arrives. A gap is given from its path segment's middle and carried across onto the
  parapet's face.
- `solid: true` builds one mass on the band instead of walls round a hollow: a breastwork or a dyke.

**A row that fits its face.** An openings spec with `every` holds as many openings as the face has room for, at
that pitch, centred, with the outermost `end` clear of the corners. One spec then serves faces of every length:
a range's folds, an irregular plan, a tower's storeys. `with` adds other openings (a door in the row) and `clear`
keeps stretches blind. A fitted opening that overlaps either is left out.

**Batter.** A prism's `batter` { out, power, steps } carries its plan out toward the foot by `out` × (depth/H)^power.
Power 1 is a straight talus. Power 2 is the Japanese fan slope (ōgi-kōbai): upright at the top, flaring at the
ground.

**Flights carried to the ground.** A flight's `ground` builds its masonry down to that height, not as a solid only
one riser deep. It is for an outside stair standing off a sloping wall.

**Lintels open to the sky.** An opening that runs to the top of a wall's topmost tier has no beam over it (a gap
in a parapet), so lintelsOf no longer records one.

**Roofs.** There are two new forms and a ring:
- `pent` is a skirt from its eave up to the wall of a smaller storey standing on it (`top: [w, l]`).
- `kara` is the cusped kara-hafu: a bell section that breaks the eave.
- curvedRoof's `ring` closes a pent round its hole, with a soffit and an inner face against the wall above.
- A pent is always curved (lo = hi = 1 by default), so `upturn` and `flare` lift its corners.

**The tiered tower** (`tiered`, arch/tiered.js) stacks storeys `{ w, l, h }`, each set in from the one below. It
is a Japanese keep, a yagura, a pagoda.
- Each storey gets plastered walls with its windows, laid out by `every` and kept above the skirt below.
- A pent skirt runs round the foot of every storey but the first. `roof: false` hides a storey's floor behind the
  roof below, as the great keep's fourth floor is hidden.
- The crowning roof is a hip-and-gable (irimoya) with its ridge along the longer side.
- Gables sit on the slopes (`gables: [{ side, kind, width, at }]`): `chidori` (a small triangular gable on the
  slope), `irimoya` (a larger one, lower down) and `kara`.
- Doors are given by side, with `at` a plain x or z. A list makes a passage through.
- Inside there is a floor on every storey. A steep flight runs up the longer side to each floor, against
  alternate walls, with the floor above open over its whole run.

**The Fisherman's Bastion** (fishermans_bastion.py) is rebuilt on its OpenStreetMap plan:
- the folded corridors as `range`s: arcaded toward the Danube, open toward the square, walked on top behind
  battlements;
- the middle parapet as `solid` ranges;
- the three-stage Schulek stair on the hill's battered wall;
- the seven towers, each on its foot;
- St Stephen's court.

**Himeji Castle** (himeji.py, himeji.json) is the great keep and the East, Inui and West small keeps. Two-storey
watari-yagura join them round their court, and all of it stands on one fan-sloped stone base 14.85 m high. The
great keep follows the Japanese Wikipedia's floors in ken, with its gables placed storey by storey: kara on the
first roof's east, kara south and great irimoya gables east and west on the second, twin gables on the third,
chidori and kara on the fourth, and kara under the crowning roof. A stone stair climbs the west face to the gate
through the western watari. Its finish (finishes/himeji.json) has white plaster, grey hongawara tiles (a new
`kawara` palette) and rough granite.

**arch_lab** takes `&finish=1` to draw a definition in its finish (finishes/<def>.json), as the game does.

**A roof along a line** (build.js bandRoofMesh; a roof part given a `path` instead of a length) puts two slopes
either side of a ridge that follows the path.
- They are mitred at every fold: a hip outside the bend, a valley inside.
- Each end is a gable or a hip (`ends`), and the eaves overhang at the sides and the ends.
- It is solid down to a flat underside. With `shell` it is a covering that thick, with its underside following
  the slopes and open gables: a corridor's roof with its rafters showing.
- A `range` takes it as `roof` { pitch, overhang, ends, shell } in place of the walk. It is one width all along.

**The finial.** A `tiered` tower's `finial` { height, radius, rings, base } sets a pagoda's sōrin on the apex of
its pyramid: a square base, the mast, the nine rings and the jewel.

**Bracket sets.** A `tiered` tower's `brackets` { use, s, every } sets a row of bracket sets under every eave,
along each side from corner to corner. The default is components/dougong, now shared with the Temple of Heaven.
They hang twice the straight slope's drop below the wall top, because a curved slope sags under its pitch line
toward the eave. usesOf now also loads the components a tiered part uses.

**The Japanese wall.** A new `timber/shinkabe` pattern draws posts standing proud of white plaster, one to a
bay, with the low nuki, the head nageshi and the plate across them. With the new `ni-red` palette the timber is a
temple's faded red ochre.

**Hōryū-ji** (horyuji.py, horyuji.json), the Western Precinct:
- the five-storeyed pagoda, `tiered`: square storeys, the fifth half the first, every eave deep, not climbed;
- the Golden Hall, two `tiered` storeys under a hip-and-gable roof;
- the Middle Gate, its passage through the two middle bays;
- each on its stone platform with a stair;
- the kairō, a roofed `range` round the court from the gate back to the gate: lattice windows outward, open to the
  court between its posts.

**Kinkaku-ji** (kinkakuji.py, kinkakuji.json), the Golden Pavilion on its island in the Mirror Pond:
- one `tiered` part of three storeys in three manners. The first (the palace manner, dark timber and white plaster)
  has no roof of its own. The second has the same plan, with the skirt roof round it. The third is the small square
  Zen hall with bell-headed windows (katōmado), under the pyramid. The phoenix is a short `finial` with no rings.
- The upper two storeys are gilt by the finish (gold leaf on their outer walls), and so are the bracket sets.
- The pond is the site's `moat`, which the game carves round the island. Its footprint (`footW` x `footD`) takes in
  the water, as Caerphilly's does. A stone bridge of five arches crosses it behind.
- A tiered storey must be tall enough for what the skirt below covers. The skirt rises up the wall above it by the
  set-in times the slope, here (13.6 - 6.5)/2 x tan 24° = 1.6 m, and tiered lifts the windows' sills over it. So the
  third storey is 4.5 m, not the 3 m of the room inside.
- The bridge component's arches are semicircles over their span. Their crown must stay under the body's `depth`,
  so a long, shallow bridge needs more arches (`n`), not fewer.

**Curved roofs rest on their walls.** A curved (jujia) slope sags below the straight line from eave to ridge. A roof
placed by that line passed over the wall line lower than the wall top, so the wall's top edge came up through it.
This was 0.38 m on a one-storey hall and 0.13 m under Himeji's skirts. Archcheck found it only on a one-storey hall,
whose walls then touched nothing ("support isolated"); on towers the skirts and floors hid it.
- A roof part now takes `rest: true`. build.js `restLift` measures the curve's sag where it crosses the wall top, and
  the roof is lifted by that much.
- `tiered` sets it on every skirt and on its top, and its windows' sills clear the lifted skirt.
- It is the curved roof's counterpart of a dome's `seat`. A straight roof needs neither: its slope is the line.

**Bracket sets and openings.** Lowered under the sag, a tiered storey's bracket sets could hang in front of its
windows. Kinkaku-ji's second storey had one bracket hanging in front of a window head. Hōryū-ji's Kondō doors were
3.6 m, under bracket seats at 3.2 m. Now:
- the windows' heads are kept under the seat (a head that is not flat, by its width more);
- a storey with no room for windows between the skirt below and the brackets is an error;
- so is a door that runs into the brackets.
Hōryū-ji's Kondō and pagoda doors and the Chūmon's were lowered to fit. Kinkaku-ji's second roof is flatter (21°, as
the real one), with smaller bracket sets.

**The beam.** A new part, `beam`, is a member swept up at its ends (build.js beamMesh):
- `length` along x, `height` deep, `depth` across;
- its soffit rises by `sori` at `reach` from the middle, as the `power` of the distance (2 by default);
- `taper` cuts the tips back underneath.
It is drawn as an elevation and carried across its depth, as the flyer is. Two beams of one `sori` and `reach` lie
exactly one on the other, whatever their lengths: a torii's shimaki and the longer kasagi on it.

**The torii** (components/torii) is a myōjin torii:
- two round pillars on stone footings, running up into the shimaki where its soffit rises over them;
- the nuki through them;
- the plaque (gaku) on its strut, which `plaque: "no"` leaves out (a part's `when`);
- the shimaki and the kasagi, `beam`s on one curve.
Its params are `span`, `height`, `r`, `over` and `sori`.

**Fushimi Inari Taisha** (fushimi_inari.py, fushimi-inari.json):
- the great torii on the approach;
- the tower gate (rōmon), two `tiered` storeys under one roof with the passage through;
- the worship hall and the main hall, one `tiered` storey each, the main hall under a long gable;
- the senbon torii, two tunnels side by side. Each is one torii part placed a gate every 0.62 m along a path that
  climbs in flights between level stretches, on every other tread on the flights: a few hundred gates in two parts.
  They are 3 m tall, so that their nuki clear a climber's head on the steps.
Its finish uses a new `shu-vermilion` palette: the torii and the halls' timber in shu, the kasagi capped in black.

**The site lint and moats.** worldlint's check of a building's own ground (index.html lintPlaces) skips the ring of
the site's own moat, which is water by design. Before this, Kinkaku-ji reported "ground fallen away" over 44% of
its ground: the pond inside its footprint. The check now covers only the island and the ground beyond the water.

**In the game** a new period, "Edo Japan" (assets/world/periods.json `japanese`), has Himeji, Hōryū-ji,
Kinkaku-ji and Fushimi Inari as its landmarks and minka for its town. Its people wear a new `japanese` dress style (wardrobe.json):
- men: a samurai's kosode with hakama and obi, or a commoner's short kosode and kasa;
- women: a kosode to the floor with a broad obi.

Over all 104 buildings the full archcheck reports 0 findings. The arena's upper vomitoria had a finding from
before this work: their stair feet stood on nothing, because the level passage had a ceiling and no floor. The
passage now has its own floor.

## The Matthias Church at the bastion, the Kremlin at St Basil's (2026-10-28)

Two landmarks stood alone where the real ones stand in an ensemble. The Fisherman's Bastion is a lookout in front of
the Matthias Church; St Basil's is one end of Red Square, with the Kremlin wall along its west side. Each now has its
neighbours, on the real plan (OpenStreetMap).

**The Matthias Church** (fishermans_bastion.py) stands on the hill behind the bastion, along its own axis (21.3°
north of east):
- a Gothic hall church (`basilica` with `hall`) of seven bays, its five-sided apse toward the bastion;
- side chapels between the buttresses, under lean-to roofs;
- the west front with its portal and traceried window, its gable;
- the Matthias tower at the south-west: two `gothic-tower-stage`s, a `gothic-octagon-stage` and a ribbed
  `gothic-spire`, 80 m over the square;
- the lower Béla tower at the north-west.
The roofs are in Zsolnay's glazed diamonds (`roofs/glazed diamonds`, palette `zsolnay`) and the windows in stained
glass. The **Holy Trinity Column** stands in the square west of the church: its steps, pedestal, shaft and clouds,
the gilt Trinity on top and three saints round the pedestal (statue markers). The hill's outline was carried west
to hold both.

**Long triangles in the solid index (solid.js).** The index skips a triangle that covers more than 4000 cells,
because filing it in every cell is too slow. Those vast triangles were then left out of every cell lookup, so a
height query over the hill's broad top found nothing: the Trinity Column "floated" and a stair had "no floor". The
index now keeps each vast triangle with its cell box, and a lookup adds those whose box holds the cell.

**Forked merlons** (components/crenellation). `merlon` names the merlons' heads:
- "stepped" (the default: the Omani and Persian kind);
- "square";
- "forked": the swallowtail. A V `fork` deep is cut into each head, and the two horns are half-width prisms whose
  tops slope (a prism's `slope`) from the V's bottom up to the merlon's full height. This is the Ghibelline merlon
  of Verona and Milan, and the Kremlin's.
The body of a forked merlon is its own part, so that each kind is chosen by `when`. Every existing caller keeps its
merlons.

**Two new components** for a fortress:
- **curtain-wall**: a stretch of wall `L` long, `T` thick and `H` high to its walk. The battlements (any
  `crenellation`) run along its outer edge (+z) and a low parapet along its inner edge. One is set between each pair
  of towers, from the face of one to the face of the next.
- **kremlin-tower**: a tower of the Moscow Kremlin. It has a square body with a loop high in each face (`gate`
  "yes": an arched passage through faces 0 and 2 instead), the corbel band, the forked battlements round a deck, the
  square tier (chetverik) with an arched window in each face, the open octagon (vosmerik) and the tent. Leave out
  the tier or the octagon for a lower tower, with `ch` or `oH` set to 0 so that what is above comes down.

**Red Square** (st_basil.py), on its OSM plan in metres from the cathedral's middle:
- The Kremlin wall runs from the Konstantino-Eleninskaya tower, past the Nabatnaya, to the Spasskaya and on
  north-west to the Senate tower. It is 11 m to the walk and 4.5 m thick, behind forked merlons.
- The Tsarskaya is the `kremlin-tower`'s tier and tent alone: a pavilion of four arches on the wall's walk.
- The Spasskaya is two gate bodies, the tower and its barbican, the passage straight through both. On the tower
  stand Galloway's tiers of 1625 (two `gothic-tower-stage`s with white-stone corner pinnacles), the open octagon and
  the tent, its ruby star at 71 m.
- Lenin's mausoleum is red granite in steps up to a colonnade, with tribunes either side, square to the wall before
  the Senate tower.
- The Lobnoye Mesto is the round stone tribune before the cathedral, with its stair.
The cathedral itself was turned to its real orientation: its stair up from the square on the north, its belfry
against the gallery on the east (it was on the south-west).

**Rules name a tail of a nested part** (finish.js partNames). A part inside a component inside a component is called
"nabatnaya tower/tent/spire". A rule could name only all of that, its last name ("spire") or its first ("nabatnaya
tower"). Now every tail is a name too, longest first: "tent/spire" is the spire of every Kremlin tower's tent. The
check that keeps a component's name from painting its windows now compares that name instead of a list position.

Over all 104 buildings the full archcheck (meshes and finishes) reports 0 findings. worldlint finds nothing on the
bastion's or St Basil's own ground; the few problems on some seeds are village buildings by the river, and the old
St Basil's had them too.

## Polygonal tiered towers, the Summer Palace and the Sheikh Zayed Grand Mosque (2026-10-28)

**A tiered tower on an n-gon** (tiered.js `sides`). With `sides` n, a storey is `{ r, h }`: a regular n-gon `r` to
its outer corners, with a face on each axis's side (planPoints' `sides` plan). A tower is built as before (storeys
set in one above another, bracket sets, floors with steep stairs inside, a finial), but its roofs are different:
- every skirt and the top is a `dome` of n faces on the jujia section. `roof` { lo, hi, overhang, t } gives the
  slopes at the eave and at the crown, the eave's reach square to the faces and the thickness; `top` overrides any
  of them;
- each roof is `seat`ed on the wall it covers, with its soffit on the wall head (assemble.js seatLift). A skirt is
  cut by an `oculus` where the storey above rises through it;
- the windows' sills clear the skirt below. The bracket sets run along every face, set low enough that their outer
  tips stay under the slope;
- a door's `side` is the face toward it, found from the plan's own edges;
- there are no gables.

A seated dome is placed at 0. seatLift measures the wall's head from the wall's own placement and lifts the dome
from its own, so a dome placed at the wall's foot would be lifted by the wall's height twice. The first skirt, on
a wall standing at 0, looked right; the second floated 7.5 m in the air.

**The Summer Palace** (summer_palace.py) is the axis of Longevity Hill. The plan is OpenStreetMap's, its axis (four
degrees off north) turned to north, with the Foxiang Ge at the origin:
- On the lakeshore: the Yunhui Yuyu pailou (four columns, the beams, three roofs, the middle one raised), a stretch
  of the Long Corridor (a roofed `range`, open between its posts on both sides), the embankment and the lake.
- Up the hill: the Paiyun Gate and the Second Gate, then the Paiyun Dian between its ear halls and side halls, then
  the Dehui Hall. All are `chinese-hall`s.
- The hill is its terraces, at 3, 7, 12, 31 and 50 m, with flights between them: on the axis, either side past the
  Paiyun Dian, and up the sides of the tower's terrace and on along the summit's.
- The Foxiang Ge stands on its octagonal plinth: four storeys, three skirts and the top (the real tower's four
  eaves), bracket sets on every face, floors and stairs inside, the gilt jewel 36 m over its terrace.
- On the summit: the Sea of Wisdom behind its glazed pailou.

**The Sheikh Zayed Grand Mosque** (sheikh_zayed.py) is on its OSM plan too, the axis (twelve degrees off west)
turned to east-west, with the prayer hall toward the qibla in the west:
- The sahn is 110 × 150 m between the riwaq's piers. A `riwaq` of small domes closes it on three sides. Its rows'
  bay counts are odd, since `domed-arcade` puts its gate in the middle bay.
- The prayer hall stands behind a portico (an `arcade-walk`). It has walls, flat roofs on a grid of columns, and
  three crossings cut through the roofs: piers, round arches, pendentives, and tympana closing the arches over the
  roofs. Each crossing carries a `drum-dome` on the onion section with bulge 1.08, the slight swell of the real
  domes: the main dome, 32.8 m across and 85 m to its finial, and the two 65 m domes.
- Small onion domes stand over the hall's entrance and in rows on its roofs. Counted with the riwaq's, the main
  entrance's and the great three, there are 79, close to the real 82.
- On the east: the entrance hall, its dome, and a `portal` deep enough for its iwan.
- Four `omani-minaret`s, 107 m, stand on the court's corners. Reflecting pools run outside the riwaq. A platform
  carries it all, with flights on three sides.
- The finish is white marble, a floral inlay in the sahn and at the walls' feet, gold leaf on every finial, and the
  hall's carpet in three pieces (one under each great dome). The lab's headless render draws carpets black, the
  Sultan Qaboos's included.

Over all 106 buildings the full archcheck (meshes and finishes) reports 0 findings: the square tiered towers
(Himeji, Horyu-ji, Kinkaku-ji, Fushimi Inari) are unchanged by the polygonal mode. worldlint finds nothing on either
new landmark's ground. The only problems it reports are village buildings by the river, the same as on other seeds.

## Borobudur and Angkor Wat (2026-10-28)

Both are new buildings made only from existing parts. Both are on their OSM plans, made symmetric, and both join
the Medieval India period's landmarks, the Indianized temples of Java and Cambodia beside Kandariya Mahadeva.

**Borobudur** (borobudur.py) is the foot, five square terraces, three round ones and the great stupa:
- Each square terrace is a `prism` from the ground up, its outline written as a profile from the axis to the corner:
  the stair projection, the redents, the corner. The survey's outlines give the steps. The overlaps are one stone.
- The stairs climb straight up the four axes, each flight cut into the terrace it climbs: a notch in that
  terrace's outline as deep as the flight is long, the flight standing in it. They are `steep` (28 cm on 22 cm), as
  on site. archcheck's approach rule wants a strip as deep as the flight is wide before each flight's foot. Between
  one flight's head and the next one's foot there must be a gallery's width, so the stair projections stand a
  metre or two further out than the survey's.
- The four galleries are walled in by balustrades: `enclosure`s on the terrace's own edge (their walls inward from
  it), the outline without its notch, broken over the stair. Each has a niche every 2.6 m, its openings written per
  face from the outline's own edges. A small stupa (cushion, bell, spire) stands over every niche, 392 in all. A
  seated Buddha (a `statue`, limestone) sits in each of the first balustrade's 32 niches on the stair projections.
- On the round terraces stand 72 perforated stupas in rings of 32, 24 and 16, set so that the stairs come up between
  two. Each is a lotus cushion, a `dome` on the bell section (the skirt flaring to the cushion, a level crown) with
  the jali lattice on it, the harmika (square on the first two rings, octagonal on the last) and the spire, each one
  `atop` the last. The great stupa is the same on its own cushion, 8.4 m in radius, the spire's tip 41 m up.
- The finish is grey andesite (the trachyte palette) throughout.

**Angkor Wat** (angkor_wat.py) faces west, the central tower at the origin:
- Before it: a stretch of the causeway with its naga balustrades, the stairs down to the two reflecting ponds, and
  the cruciform Terrace of Honour with the naga on its edges (an `enclosure` on the cross's outline, broken where the
  causeway and the stairs come in).
- The three enclosures stand at 3, 9.5 and 22.5 m: the outer terrace, the second platform and the bakan, the
  last two with battered sides.
- The galleries are roofed `range`s, each an open path from its west gopura round to it again. Their faces open as
  each side does: a colonnade out and windows in on the outer gallery, windows both sides on the second, balustered
  windows on the bakan's. Each has a door wherever another gallery meets or crosses it, an `every` row `with` the
  door.
- The pavilions are `enclosure`s with their doors where a gallery passes through: the gopuras on every axis and the
  pavilions on every corner. Those under a tower carry a flat slab or a cornice, the rest a hip roof.
- The cruciform cloister is three galleries along the axis and one across, pillared on both sides. The kerbs of
  basins stand in its four courts. Its two libraries, and the two in the second court, are each a plinth with a
  stair at each end, a hall and a steep gable.
- The stairs: ordinary flights up to the outer terrace, `steep` ones up to the second platform, and on the bakan,
  44 risers on four axes. The bakan's square gallery and the cross of galleries meet under the sanctuary.
- The five towers are `shikhara`s without the Nagara crown: five rathas, five banded storeys, bending in on the
  rekha to a fifth of their width. Small spires on the corners at four heights stand for the antefixes. Each tower
  has an onion `dome` `atop` it as the lotus bud. The central tower is 15 m across and its bud's tip 65 m up; the
  corner towers reach about 52 m, the second gallery's 28 m. The west gopura's three towers are truncated, with no bud.
- The finish is grey sandstone, the roofs cut as tiles, the platforms' sides and the paving in a darker stone, and
  the ponds' water.
- Checked: archcheck finds nothing on either; over all 108 buildings the full archcheck (meshes and finishes)
  reports 0 findings, and worldlint none on either landmark's ground.

**The Imam Mosque** (imam_mosque.py), Isfahan, on its OSM plan with the qibla axis turned to run west, the dome's
axis at the origin:
- The court (56 x 75m, its pool in the middle) is closed by four `range`s, 8m deep and 13m high, their court faces
  two tiers of pointed niches (fitted rows). Each range is an L round a corner, broken where an iwan stands: the
  iwans are `portal`s set flush with the court's face, their depth the range's, so the court is one plane of niches
  and pishtaqs. `side_away` picks each range's `side` so that `in` is the court's face whichever way its path runs.
- The qibla iwan's pishtaq (30m) stands before the sanctuary, a hall 38 x 91m under flat roofs. The dome chamber in
  it is a crossing as Sheikh Zayed's are -- four piers, semicircular arches (a pointed one would rise past the
  pendentives' top), pendentives, tympana closing the arches over the roofs -- under a `drum-dome` on the onion section
  (bulge 1.06, neck .32): 52m to its crown. The two qibla minarets (`minaret`, one balcony and its kiosk) stand on
  the sanctuary's roof beside the pishtaq.
- Behind the side iwans the winter halls, under low pointed domes of bare brick; either side of the sanctuary a
  madrasa, a `range` round its court with a gap on the east, through to the winter hall's door.
- The entrance is turned to the square (the portal faces north in the world, 33 degrees off the court's axis): the
  portal, the square vestibule behind it and its dome, all at that yaw, the vestibule's back door looking at the
  east iwan's across a few metres of open ground; the two entrance minarets behind the portal's corners.
- Everything stands on a platform one riser high (15cm): the main block in tiles, and a quad under the entrance
  band, cut to meet it at x 91, so the two never overlap.
- The finish: the rumi arabesque in cream and turquoise on cobalt (palette `isfahan`) on every face of the court,
  the iwans' half domes and the entrance portal (one `within` box over the court and the iwans' depth); the onions
  turquoise with yellow arabesques (`isfahan-dome`); girih on cobalt (`isfahan-girih`) on the drums, the minarets and
  in the domes; prayer carpets in the sanctuary and winter halls, the court flagged, the roofs and every outer wall in
  buff brick.
- Checked: archcheck (meshes and finishes) finds nothing.

## Interiors: inside and out without rays (2026-10-28)

The finish used to MEASURE each face's side: rays to the sky and into the air before it, bands of 3m, a 2m
grid on the floors. That took most of the finishing time and failed wherever a ray slipped through a crack or a
column hid a wall. Now the building SAYS where its inside is. docs/patterns.md has the rules; in short:

- An INTERIOR is a volume of air on the plan, a polygon with holes from `y0` to `y1`. It is a marker part
  (`role: "interior"`), so a component that has one has it in every copy, and nothing is stored per face.
- Interiors come from three places:
  - the `interior` flag on plan parts (`true`, or a height), on by default for `range` and `tiered` storeys;
  - the `interior` part type (`plan` or `radius`/`sides`, `arc`, `hole`, `of`);
  - the engines: `basilica` and `gothic` give their aisles, nave and transept, `court` the ring of wings round
    the court.
- `inside` / `outside` on a part still overrides; buttresses, flyers and pinnacles are always outside.
- A face is in when the point 30cm before it lies in an interior. A dome's skin turned toward its axis is
  inside, a vault's down-turned face too, a roof's upper slopes outside. Pieces are cut first on the
  interiors' planes, so a tower's face changes along a level line at the church roof.
- An interior runs on the walls' MIDDLE line, so a window's reveal is split at mid-wall: outer half the facade's,
  inner half the room's. It stops at the vault's springing or under the roof. Where a tower rises beside a sloped
  roof, it stops at the eave.
- Open porticoes, loggias and colonnades get none:
  - Horyuji's kairo and the Long Corridor (`interior: false`);
  - an `arcade-walk` without its own back wall;
  - a `gallery` or `curved-gallery` with sill 0 (the `hall` param);
  - the Tsarskaya (`tierIn` 0).

Every landmark and the village buildings were given their interiors. Compared with the rays, 8.2% of the surface area
across the 92 finished buildings now takes another rule. The largest changes, read cell by cell, are mostly the
rays' mistakes put right:
- Cologne's tower halls and crossing vault are in;
- the Hagia Sophia's ground storey is revetment;
- the Blue Mosque's crossing piers are tiled;
- a pier's or an opening's two halves no longer differ by chance.

The rest is hidden: roof undersides, vault backs, a platform's underside. Finishing all 92 buildings took
154s and now takes 27.5s. Rays survive only in check.js, for stairs and support (solid.js `rayIndex`). The full
archcheck (meshes and finishes) reports 0 findings over 108 buildings.

Left open:
- Himeji: a skirt roof runs on inside the storey above (tiered.js).
- The Frauenkirche: the mansard roof crosses the drum, because roofs have no `well`.
- El Pilar: the finish rule `portal` does not reach the names `portal 1/...`.
- The Temple of Heaven and St Paul's: their compass panels at `at: [0, 0]` cover nothing.
