# Jewelry: what is worn on top

Necklaces, collars, torcs, pendants, diadems, wreaths and earrings (2026-10-06): items of the items language
(`assets/items/jewelry/`, written by `tools/jewelgen.py`), laid on GUIDES taken from the layers under them -- the body,
the clothes over it, the skull, the hair's cap -- so one necklace fits a child, a broad man, a woman in a kirtle and one
in a cloak. `jewelry.js` (the fits and the part types), `jewels.js` (the necklaces on the people, every frame),
`clothes.js outerSurface`, `face.js earFrame`, `hair.js capShape`.

## Analysis

**What is seen.** At the game's distances jewelry reads by its MASS and its COLOUR: the broad collar of Egypt (the
wesekh: rows of cylinder beads in lapis, carnelian, turquoise and gold between gold bands, a fringe of teardrops), a
pectoral plaque, a torc's heavy twisted bar, a livery collar's gold links over the shoulders, a festoon of glass beads, a
diadem's band and its front ornament (the uraeus), a wreath's leaves, a coronet's fleurons. Fine chains and small rings
are kept, as cords or ropes, but they are not what the eye finds. Every piece is a few hundred to ~3,000 triangles.

**What it must follow.** A necklace lies on the outermost surface round the neck and over the shoulders and the chest:
the torso (an oval, flattened front to back, with a squared cap up to the collar), the neck and the fillet between them,
each WORN layer of cloth over it (a chemise, a kirtle: millimetres each) -- except inside a neckline, where the skin is
-- and any STANDING shell hung round the torso (a cape, a hood's cape, a cloak). A headpiece lies on the skull or, where
the hairstyle covers it, on the hair's cap. An earring hangs at the lobe. None of these is placed by numbers: each is a
point on a FIT built from those layers, its frame (round the body, up the surface, out of it) the surface's own.

**Periods and colours.** A mix: Egypt (wesekh, pectoral, uraeus diadem, seshed circlet, disc ear studs), the Bronze and
Iron Ages (lunula, torc), Greece and Rome (gold chain with medallion, Hellenistic fringe necklace, pearls, the bulla,
the laurel wreath, crescent earrings), the Norse (oval brooches and bead festoons), China (jade bi on a red cord,
hairpins), the medieval and Renaissance West (cross on a cord, livery collar, pearl choker, circlet, coronet, flower
chaplet). Each in COLOURWAYS -- sets of materials that belong together (the wesekh's royal gold-lapis-carnelian, its
faience blues and greens, its festival colours; the torc in gold, bronze or silver).

## The fits (jewelry.js)

`at(th, v)` -> `{ p, n, t, u }`: a point on the surface, its outward normal, the way round (toward +th) and the way down;
th in degrees from the front (0 ahead, +90 the figure's +z side).

| fit | built from | v | frame |
|---|---|---|---|
| `neck` | people.js: the FORM and the tailor's work -> `clothes.js outerSurface(form, worn)` -> `neckFit` | the DROP: metres down the surface from the neck's base (negative: up the neck, a choker) | the chest's: origin on the torso's axis at the shoulders' rim, y up the chest, x the figure's forward |
| `head` | the face item's own head params -> `headGrid` (the skull, this face's forehead) + `hairCap` (`hair.js capShape`: its edge and thickness) | a HEIGHT on the head, canonical (the brows ~.02, the hairline ~.065, the crown .10), scaled with the head | the face's |
| `ear` | `face.js earFrame` (the ear's plate) | -- (th +90 / -90: the side) | the face's |

The neck's surface is sampled on 48 meridians every 2 mm, its BASE where it first stands clear of the neck, with a
clearance for the figure engine's ring corners (2.5% and 4.5 mm). Its KEY is the surface to 2 mm: people of one build
in one dress share their necklaces' meshes. People with no necklace never build it (`fitNeck` is made when first asked).
`setCanonNeck`: a bare woman's, for an item seen without a body.

## The parts (items.js part types)

- `strand` -- beads (`round`, `tube`, `disc`, `drop`, `cube`: the roles of `materials` in turn) or one tube (`rod`,
  `twist`: a square section turned along it -- a torc, a rope chain; `cord`) along a level round the fit: `level` (or
  `[front, back]`), `vee` deeper toward the front, `th` [from, to], `size`, `length`, `gap`, `swell` (thicker at its ends).
- `collar` -- a plate from `from` to `to` in `rows` inner to outer: `band`, `beads` (`n` cells round, the row's roles in
  turn, on a `ground`), `drops` (teardrops hanging from the edge); `thick`; open when `th` is less than all round.
- `band` -- a ribbon round the fit at `level`, `width` in the fit's own units, `thick`, `crest` (wider toward the front).
- `on: { fit, th | ring: { n, from, to }, level, lift, vee }` -- any part or component SET ON the fit (x round, y up the
  surface, z out): a pendant, a torc's terminals, a gem, a fleuron, wreath leaves (plates, turned in their plane by the
  `at`'s roll), a bloom of `items/flowers/blooms`, an earring.
- `colourways` on an item: `{ name: { role: material } }`, picked by the seed or named by the `colourway` param, over
  the roles' own and under the caller's.

## In the world

- `assets/items/jewelry/wear.json` (people.js `drawJewelry`): by style of dress (`village`, `gothic`, `greek`, `roman`,
  `chinese`, `egyptian`) and kind (`woman`, `man`, `child10f`...), looks with weights, each a pick of a necklace, a
  headpiece and earrings; `hidesNeck` (a hood) wears no necklace. Drawn from the person's own seeded stream, after
  everything else (an outfit never shifts for it). `makePerson({ outfit: { jewelry: { neck: [...], head, ears } } })`
  overrides it. The wardrobe gained an `egyptian` style (linen kilts and sheaths) and Giza's people wear it.
- Necklaces: `jewels.js` -- one InstancedMesh a piece-colouring-and-fit, painted and lit, set every frame in the chest's
  frame (index.html, wardrobe.html, assets.html, after the heads).
- Headpieces and earrings: components of the face (`facegen.py`: `headwear`, `earrings`, the head's params by name and
  `hairCap`), in heads.js's key; none under a hat or a hood.
- (`tools.js paintedGeometry` now reads a palette given by NAME -- "gold", "silver" -- every painted item's metals were a
  tan before.)

## Benches

- `wardrobe.html`: row 7 every necklace on a woman in a chemise and a kirtle (`?jewel=a,b`), row 8 every style of dress
  on a woman and a man with what their seed draws (`?seed=N`), row 9 every headpiece and pair of earrings.
- The asset viewer: a necklace shown WORN (the "head" switch off: alone on the canon neck), a headpiece or earrings on a
  head; the face bar's `headwear` and `earrings`.
- Scratchpad harnesses (session): `jewel/jewelsheet.py` (each item alone, with triangles and colourway),
  `jewel/wardsheet.py` (one close shot a person of a wardrobe row; `BARE=1` adds one with the body hidden).

## Pitfalls met

- The torso's cap is FLAT-TOPPED: a plate lying on it from the neck out (a lunula) is seen edge-on from the front --
  carry it down onto the chest.
- A head's level is a height (up), a neck's a drop (down): the frame's "down" takes the level's own sign.
- A component's param holding an OBJECT (a fit, a cap) is handed on by its name (`items.js val`).
