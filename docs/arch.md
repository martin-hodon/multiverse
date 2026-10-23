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
| `vault` | a ring of barrel vaults over the corridor between two walls. Its cross-section *is* a wall face whose single opening spans the full width, swept between the bay's radial planes rather than extruded straight; `clears` is the height it must spring above (the crown of the arches below), and the engine refuses rather than quietly roofing across them |
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

- **The amphitheatre** (`arena.json`) is the whole building: `BUILDINGS.colosseum`.
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
- Milan: spiral turrets inside the facade to the aisle roofs, flights on to the nave roof -- its roofs are walked.
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
  its finish in `assets/finishes/<name>.json`): 27 tents and houses beyond the medieval town -- pavilion, bell tent,
  marquee, wedge tent, Roman papilio, ger, tipi, Bedouin black tent, wigwam; igloo, Iron Age roundhouse, crannog,
  rondavel, beehive hut, hogan; pit house, Norse and Iroquois longhouses, stilt house, minka; domus, Greek house,
  Arab courtyard house, siheyuan (the `court` part); Egyptian house, pueblo, blackhouse. Round ones have their door at
  +x (ring bay 0), straight ones on face 0 (+z; on a CHAMFERED rect face 2 is +z). Every one can be entered, and its
  inside follows its outside: domes and cones have no cap (`cap: false`), a cone or a dome down to the ground gets its
  doorway as a band cut off at the door's head (`oculus`) with a gap round it (`sweep`) and the rest above it (a
  sphere's top is a segmental dome), ridge tents and the pit house leave their front gable open (roof `open`). Their
  windows are unglazed (`glass: false`, which `court` now passes to its walls). Curved meridians carry `seg`, so a
  small dome stays a dome at a low detail.
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
