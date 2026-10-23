# Butterflies

Butterflies as assets (2026-10-05): `assets/butterflies/*.json` (the shapes, and one file per species), built by
`butterflies.js` -- painted into a texture per species, drawn in the game as instanced flat wings that flap, shown in
the asset viewer as a specimen plate (upperside and underside).

## Analysis: what a butterfly wing is

**The wing is a plane.** Membrane stretched over veins, covered in scales; at the size it is seen in a world it is a
flat polygon -- the forewing and the hindwing each one plane per side, hinged at the thorax, the left the right's
mirror. Its two faces carry two different paintings: the UPPERSIDE (display: colour, iridescence, warning eyes) and
the UNDERSIDE (seen at rest with the wings closed over the back -- mostly cryptic: dead-leaf browns, marbling, small
eyes on the hindwing margin).

**Its outline**, named as entomologists name it: the forewing's COSTA (leading edge) from the base to the APEX, the
TERMEN (outer margin) from the apex to the TORNUS, the INNER MARGIN back to the base; the hindwing's costa under the
forewing, its outer margin -- smooth, scalloped (nymphalids), or drawn out into a TAIL at a vein (swallowtails at M3,
hairstreaks at CuA2) -- to the ANAL ANGLE and the inner margin along the abdomen. Seen from the base the outline is
star-shaped, so here it is a POLAR profile: the wing's radius R at each angle from the costa to the inner margin, a
few control points through a smooth curve, a scallop (amplitude, how many), and a tail (where, how long, how wide).
Families differ in the profile -- the nymphalid's broad triangle and rounded hindwing, the papilionid's long
forewing and tailed hindwing, the pierid's round apex, the lycaenid's small rounded pair, the morpho's huge broad
wings, the brimstone's hooked apex and pointed hindwing.

**Its veins** radiate from the base (through the discal cell) to the margin: R1-R5, M1-M3, CuA1-2, A -- about nine
reach a nymphalid forewing's margin, eight the hindwing's. The spaces between them are the CELLS, and patterns are
organised by them: a spot sits in a cell, a band is a row of cell-shaped pieces.

**The pattern's own plan** -- the NYMPHALID GROUND PLAN (Schwanwitsch 1924, Süffert 1927; Nijhout 1991): every
pattern is made of the same few elements, arranged in parallel SYMMETRY SYSTEMS that run across the wing from the
costa to the inner margin, at fixed distances from the base:

| element | where (fraction of the way from the base to the margin) |
|---|---|
| basal suffusion, the basal symmetry system | 0 - .25 |
| the DISCAL spot (the discal cell's end) | ~ .4 |
| the CENTRAL symmetry system (the median band) | .35 - .6 |
| the BORDER symmetry system: the EYESPOTS (border ocelli), one per cell | .65 - .8 |
| the submarginal band (lunules, chevrons, spots) | .8 - .9 |
| the marginal band (the dark border) | .9 - 1 |
| the FRINGE (cilia), often chequered at the veins | the edge |

So a band is defined in WING COORDINATES -- `t`, the distance from the base as a fraction of the way to the margin
along the same ray, and `a`, the angle from the costa (0) to the inner margin (1) -- and the same band definition fits
every shape: the margin's own curve (scallops, a tail) is followed by the bands near it. A tail lies beyond the
untailed margin (t > 1) and takes the tail's colour (`tail`: the border's, unless said).

## The definitions

    shape (assets/butterflies/shapes): fore / hind each { from, to (degrees from the body's forward, the costa's and
            the inner margin's), R: [[degrees, radius], ...] (x the forewing's length), veins (how many reach the
            margin), scallop: { amp, n }, tail: { at (degrees), length, width (degrees) } }, base (the hindwing's
            root behind the forewing's)
    a species: { kind: "butterfly", name, latin, shape (a shape's name) and overrides (fore / hind / tail ...),
            span (metres, the real wingspan), body (its colour), upper: { fore, hind }, under: { fore, hind } --
            each a SIDE: { ground (colour), layers: [...] } }

The layers, painted in order over the ground (`t` and `a` ranges; `soft` the edge, in t):

| layer | what |
|---|---|
| `band` | a region `t: [t0, t1]` over `a: [a0, a1]`, `slope` (t shifting with a: an oblique band), `wave` { amp, n } |
| `gradient` | from `color` at t0 to `to` at t1: a basal suffusion, an iridescent sheen |
| `veins` | the veins drawn, `width`, over `t` |
| `spots` | one spot per cell over `cells` (or `n` over `a`), at `t`, radius `r` (x the forewing's length), `shape` round / lunule / chevron / bar |
| `eye` | an ocellus at `cell` (or `a`) and `t`: `r`, `rings` outer to inner, `pupil`, a `glint` |
| `dust` | a mottle of `colors` (`scale`, `amount`): the underside's bark and dead-leaf crypsis |
| `fringe` | the edge's cilia, `color`, chequered `alt` at the veins |

## In the game

`butterflies.js createButterflies(scene)`: per species one texture (fore and hind, upperside and underside, the body)
and one instanced geometry -- each wing a fan from its root, its two faces the two sides (the upper face takes the
upperside's painting, the lower the underside's), the right the left's mirror; the flap is done in the vertex shader
(a per-instance angle, hinged at the body), the light per pixel from the plane's own normal (light.js). One draw call
a species. `config.json crowds.butterflies` how many; `butterflyScale` how much larger than life they fly (they are
small and fast: life-size they vanish).
