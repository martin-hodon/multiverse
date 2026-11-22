# Items: what a hand holds and what a room is furnished with

A sword, a shield, a scythe, a lute, a chair, a four-poster are all **definitions** (`assets/items/**.json`), built
into triangles by one module, `items.js`, wherever they are drawn: the asset viewer, the tools and arms in people's
hands (`tools.js`), and the furniture in a building (`arch/assemble.js` `item` parts, drawn by `architecture.js`).
Nothing in `items.js` touches three. Out come plain arrays, one set per **material**, and the materials are named
(oak, walnut, iron, leather, rush, damask...) and textured from the pattern library (docs/patterns.md).

The period catalogue below runs up to about 1800; the modern age (vehicles, the street, machines, guns, furniture,
electronics, stations and the airport; 146 items in assets/items/modern/) is described in docs/modern.md. In the period part: no upholstered sofas, no revolvers. The catalogue has 56 weapons, 12 shields,
28 tools, 48 pieces of furniture, 40 ships, 46 components, one kit and 63 materials, and every one is seen in `assets.html`.

| folder | what |
|---|---|
| `weapons/` | swords (arming sword, gladius, xiphos, spatha, viking, longsword, claymore, zweihander, falchion, sabre, rapier, smallsword, shamshir, katana, jian, dao), daggers (rondel, seax, dirk, pugio, tanto, stiletto), axes (bearded, dane, francisca, battle), polearms (spear, winged spear, dory, pike, sarissa, halberd, glaive, bill, partisan, poleaxe, guandao, naginata, pilum, javelin), blunt (mace, flanged mace, morning star, war hammer, club, quarterstaff, flail), bows, a crossbow, a musket, a pistol |
| `shields/` | heater, round, kite, scutum, aspis, buckler, targe, pavise, oval, rattan, dhal -- their faces heraldic |
| `tools/` | the village's tools (scythe, spade, hoe, hammer, saw, cleaver, fishing rod, lute...) and things carried (lantern, torch, book, bucket, basket, pitcher, candlestick) |
| `mushrooms/` | the woods' mushrooms (`tools/mushroomgen.py`, 2026-11-08): fly agaric (amanita), cep (boletus), chanterelle -- lathes at real size (6-20 cm), `s` their size and the agaric's `spin` its warts' turn, drawn by the seed; the game grows them in the trees' shade in the flowers' pool (docs/world.md) |
| `furniture/` | seats (stools, benches, settle, divan, chairs from the klismos and curule to the Windsor and the fauteuil, thrones), tables (and the brass tray on its stand), beds (pallet, bedstead, box bed, four-poster, Chinese bed, Roman couch, Egyptian bed, charpai, hammock, cradle), storage (chests, cassone, cask, cupboard, armoire, dresser, bureau, bookcase), and the rest (lectern, harpsichord, spinning wheel, longcase clock, screen, mirror) |
| `components/` | the reusable pieces (68): the arms' grip, pommel, crossguard, boss, axe head, spearhead, polearm head, blunt head; the furniture's turned / square / cabriole leg, bun and bracket feet, finial, knob, ring pull, drawer (joinery or slab front, also the modern drawers'), panel door, spindle, cushion, strap, rocker; the ships' rigging and fittings (mast, yard, the sails, shrouds, bowsprit, rudder, steering oar, oar(s), hatch, bitts, cabin, castle, figurehead, anchor, cannon, gun and shield rows, awning, ram, outrigger, gangplank); the props the game places on their own (cart wheel and the three cart bodies, the water wheel, the windmill's sails and arm, the mill's gears, shaft, stones, hopper and tun, the fisherman's oar, line and hanging fish, the ice hole, the tipi's poles, the trade sign); the stork's wing. Those with no `use` in an item are the game's own (index.html, carts.js, harbour.js, architecture.js and the buildings' JSON place them) |
| `ships/` | 40 vessels up to 1800 (`tools/shipgen.py` writes them; docs/ships.md): punt ship, gaulos, dromon, kadirga, hulk, treasure ship, bezaisen, atakebune, Maya canoe, koch, dugout, reed boat, Egyptian river boat, trireme, Roman merchantman, longship, knarr, cog, carrack, caravel, galleon, galley, dhow, junk, sampan, outrigger canoe, voyaging canoe, gondola, birchbark canoe, kayak, umiak, coracle, fishing boat, skiff, fluyt, xebec, felucca, ship of the line, frigate, East Indiaman |
| `faces/` | the parametric head (`tools/facegen.py`): the canon `face`, and `man`, `woman`, `child`, `elder`, `beast-man` drawn from it |
| `hair/` | 25 hairstyles grown from the head's vertices (`tools/hairgen.py`): none, crop, short, flat (under a hat), bowl, bob, Egyptian bob, long, long wavy, curly, ponytail, bun, braid, plaits, two locks, viking side plaits, topknot, tonsure, shoulder length; and as zig-zag sheets: long, bob and short in drawn locks; in thorns: spiky back, up, wild |
| `jewelry/` | worn on top, on guides from the layers under it (`tools/jewelgen.py`, docs/jewelry.md): 13 necklaces (wesekh, pectoral, torc, gold chain with medallion, Hellenistic fringe, pearls, choker, livery collar, cross on a cord, Norse brooches and festoons, jade bi, bulla, lunula), 8 headpieces (uraeus diadem, seshed circlet, laurel wreath, circlet, coronet, flower chaplet, hairpins, woven headband), 4 earrings (hoops, pearl drops, disc studs, crescents), each in colourways; `wear.json` who wears what |
| `kits/` | what a kind of person carries: `guard` (the town's watch) |
| `materials.json` | the library: every material by name -- a pattern, its palette, its scale |

## The language

An item is `params`, `materials` (its **roles**), `parts`, and optionally `hold` and `markers`. It may stand on
another (`use`, merged as every definition is: defs.js). A dagger is a sword with other numbers, and a hatchet is an axe.

- **Params** are numbers, expressions over the params before them (`"gripL * 0.45"`), words (`"baluster"`),
  a **range** `[lo, hi]` (a value in it, drawn by the item's seed, so every sword of a kind is a little its
  own), or `{ "pick": [...] }` (one of a list: numbers, words, whole material specs).
- **Parts** are primitives or components, each placed by `at` (`[x, y, z, yaw, pitch, roll]`, degrees; one or a list),
  `along` (n copies from..to), `each` (n copies, each seeing its index `i` and share `i_t` in its own expressions --
  `{ n, as: "j" }` renames them; ids become `id#i`: a mast's shrouds fanning from one masthead along the rail, which
  `along` cannot, since it moves both ends; a copy's `when` may name its own param, `"w{i}"` -> `w0`, `w1`, ..: a
  footbridge's bays, each left open by its own; a hinge or slide repeated so is named by its copy, `id#i` (and
  `id#i~2` its mirror twin), and one inside a copied `use` is `id#i.<its id>`: a cart's crates, `load 10 crate#2.lid`; a fold leaves a part's id inside the run as it is, the tram's `leaf`.
  Nothing keys on a joint's name -- itemObject hangs each joint on a pivot named by it and `setOpen(t, prefix)` swings
  those whose name starts so, `"load 10 crate"` every crate's lid), `around` (a ring: `plane` "xz" for legs and flanges turned to face out, "xy" for
  studs round a shield), `mirror: "x"`, `stretch` (drawn out along the parent's axes, after turning), `scale`, and
  gated by `when` (a param, a list, or `{ param: word | [words] }`). `double: true` draws a thin shell from both sides.
- **`rnd(a, b, ...)`** in any expression (2026-11-22, expr.js) is a seeded draw: a number in [0, 1) hashed (an
  integer hash, the same on every run and machine) from the item's seed and its arguments. The same arguments give the
  same number anywhere in the build, so a run of copies draws by its index and a key -- `"0.02 + 0.025 * rnd(i, 1)"`,
  `"rnd(i, 2)"` for another quantity -- and two parts that must agree (a book's right edge, its neighbour's left)
  ask with the same arguments. A component draws with its own seed (`seed` + its part's `seed`); outside items (no
  seed) it draws with seed 0. A packed row of different widths, which a sum of the widths before each could not
  write, is written by its EDGES: edge j at `x0 + s * j + J * (rnd(k, j) - 0.5)`, the two ends held by a factor
  `min(j, 1)` / `min(n - j, 1)`, each copy from edge i to edge i + 1 (modern/furniture/bookshelf, J < s: no overlap).

| type | what |
|---|---|
| `lathe` | a profile `[[r, y], ...]` turned about y (`sides`, `caps` -- false, or `"top"` / `"bottom"` for only that one, `faceted` for a square leg, `smooth` to shade its bands as one round body, `arc` [a0, a1] degrees for only that span round: a beach ball's gore, no caps) |
| `rod` | from..to, radius `r` (or `r0`..`r1`) |
| `sphere`, `box` | `r`; `size` [x, y, z] with `round` |
| `sweep` | a tube along a path (`r` or a list of radii, or a rectangular `section` with its `up`); `closed` |
| `ring` | a torus: `r`, `tube` (`sides` round the tube; by default a closed sweep smoothed to twice its stations -- `smooth: false` keeps the stations as they are, `stations` sets how many: a cord or hoop of 6 sides by 10-24 stations is 120-290 triangles, not 300-1500; opt-in, the default build unchanged) |
| `blade` | `length`, `width` stations, `thick` [base, tip], one or two `edges`, `flat`, `curve` |
| `plate` | an outline extruded `thick` (or tapered) |
| `hull` | a ship's hull lofted along +x from its lines (see Ships) |
| `loft` | rounded-rectangle sections along +x (`stations [x, hw, y0, y1, tw?]`, `round`, `holes`, `arches`, `caps`): car bodies, buses, carriages, fuselages, cabinets (docs/modern.md) |
| `sail` | a cloth between four `corners`, bellied, with `battens` |
| `face` | a low-poly head on the anatomy (see Faces) |
| `hair` | strands grown from that head's scalp (see Hair) |
| `feathers` | a fan of feathers, each its own vane, seen from both sides (see Birds) |
| `petals` | a whorl of curved blades round the part's y axis, seen from both sides -- a flower's petals and sepals, a leaf or two (see Flowers): `n`, `layers`, `length`, `width`, `cup`, `curl`, `cupped`, `shape`, `throat` / `band` |
| `shield` | a shaped board (`shape`: round, oval, kite, heater, rect), bent and dished, a rim band, a back, a face whose heraldry is fitted to it; `rimFlat` (2026-10-30): the rim band a flat ring standing off the bowl, as an aspis's broad offset rim (it had read as a plain dish) |
| (a component) | `use`: another item by path, its own `params` (expressions over the parent's) and `materials` |

- `mirror` is in the part's own frame (the one its `at` is written in): `"x"` reflects across x = 0, `"z"` across
  z = 0 -- a ship's two sides (oars, shields, gun ports) from one side written out.

- **Materials**: a part names a ROLE (`wood`, `blade`, `face`). The item's `materials` say what each role is: a
  library name (`"walnut"`), a colour (`"#8e2f35"`, plain paint) or a spec written out
  (`{ "pattern": "heraldry/quarterly", "palette": [...] }`), any of them picked by the seed. A component takes its
  parent's roles for its own, so a crossguard is brass because the sword said so. The library
  (`materials.json`) draws on the pattern families `materials` (paint, metal, hammered, lacquer, horn), `timber`,
  `stone`, `fabrics` (the tailor's: linen, damask, brocade, velvet, fur, leather, straw) and `heraldry` (divisions and
  charges, fitted to a shield's face at its size).

## Ships

A vessel is an item like any other (`assets/items/ships/`, category `ship`), in the frame: the stern at x = 0, the
bow at +x, y up from the keel's lowest point, z across (starboard +z). Two primitives carry it:

- **`hull`** lofts the hull from its LINES, each a list of `[t, value]` over t = 0 (stern) .. 1 (bow): `sheer` (the
  gunwale's height), `keel` (the bottom's: a rocker, rising to the posts), `plan` (the half-breadth as a share of
  `beam` / 2; a share > 0 at an end is a transom, closed flat), `fullness` (the section: 0 a V, .3 a round bilge, 1 a
  flat-bottomed box) and `tumblehome` (the sides leaning in above the waterline). It also lays `deck`s where the
  hull is that high, a `rail` along both sheer lines, a `keelBeam` with its stem and sternpost, `thwarts` across
  an open boat and `ribs` inside it. `double` for an open boat seen from inside. `stations` and `sides` are its
  detail (scaled by `detail`). `lean` (2026-11-22, every shipgen hull): the rail, keel beam and ribs swept through
  the stations themselves (no spline between them), and `double` turning only the skin and its transoms -- the rail,
  keel, ribs and thwarts are closed solids and the decks two-sided already, so their turned copies lay inside them.
- **`sail`** is a cloth between four `corners` in its plane (three make a lateen or a crab claw), `belly` out along
  +z, seen from both sides, with `battens` across it for a junk. A square sail is turned across the ship by its
  parent (yaw 90); a lateen, a junk sail and a spanker hang fore and aft.

The rigging and fittings are components (`components/`): `mast` (`top`: topmast or crow's nest), `yard`,
`square-sail` (`set` full or furled), `lateen-sail` (`tilt`), `junk-sail`, `crab-claw-sail`, `oar` (2026-11-22:
`loomL`, `taper`, `sides`, `bladeT` and role `blade` -- the oar's wood unless named -- so the game's `fisher-oar` is
this oar turned onto z) and a bank of `oars` (both sides), `steering-oar` (2026-11-22: the `oar` hung blade down --
rolled -90 from its handle at l x .25, 1.1 l long, the loom .65 l, the blade the lower .6 l, `bladeT` its bladeW and 5 cm
across -- and its own tiller; its eight ships build the same but for the blade's texture running the other way and its
faces' diagonals, 2 parts where it had 3), `rudder` (stern-hung, with its tiller), `figurehead` (dragon, swan, scroll,
lion), `castle` (a fore- or aftcastle on posts, crenellated or not), `cabin` (a deckhouse with windows), `awning`,
`outrigger`, `anchor`, `cannon`, `shrouds` (a mast's lower shrouds, ratlines and topmast shrouds by `each`: one part a mast where the ships wrote every rope, 950 → 618 ship parts, the same geometry), `gun-row` (a broadside of ports, each with its lid hinged at the top and a gun behind it; its `open`, default 1, swings the lids up over the first half and runs the guns out over the second, by joint `range`s -- galleon, frigate, ship of the line, xebec, East Indiaman), `ram`, `shield-row` (round shields
along the gunwales), `bowsprit`. A stay is a thin `rod`. The materials added: `planks`, `planks-pine`,
`planks-grey`, `planks-tarred`, `deck`, `sail-striped`, `sail-tan`, `matting`, `reed`, `bamboo`, `cedar`, `hide`.

Every vessel has a range of sizes (`L`), its era and region, and a `set` drawn by its seed (most sails full, some
furled). 2026-11-03: docs/ships.md -- the states (`set`, `oars`), the anchors every ship carries (`waterline`,
`moor`, `gangplank`, `hold`, `helm`), the components `hatch`, `bitts`, `headsail`, the ten large period ships added,
the lateen and crab-claw sails turned the right way round, and `assets/world/ships.json` (which ships a culture sails). They were checked as flat paintings from the side, above and the quarter, all thirty at once, every
material found. Not there yet: rigging beyond a few stays, crews at the oars, a vessel placed on the water in the
game (a boat is an item -- `arch` can place one as it places furniture).

## Faces

Besides the composite's head (a capsule with an SDF nose and eyes, `people.js`) there is a DETAILED head built on the
anatomy: `face.js`, the part type `face`, the definitions in `faces/`. Its frame is the composite head's -- the origin
at the cranium's centre, +x where it looks, y up -- so it is placed on the head bone the way tools are on hands.

Rebuilt 2026-10-05 on GUIDE LINES -- the whole of it in **docs/face.md**: anatomical ATTRIBUTES (`FACE_ATTRS`:
Farkas's measurements -- face height, upper and lower width, the eyes' distance, width and height, the nose's height,
width and projection, the mouth's width, the lips' heights -- and the profile's angles: nasolabial, forehead, upper
lip, the jaw's) place the LANDMARKS, each from those it depends on (the eyebrow over the eye, the gonion from the
jaw's angle); the landmarks are the nodes of a LATTICE of guide rows (brow, lids, lip borders, jawline...) and
columns (midline, nose side, the inner line through endocanthion and mouth corner, the pupil line, the outer line,
the face's outline); the skin is the lattice SUBDIVIDED, interpolating (it keeps the guide lines), each region's
ROUNDNESS (`chubby` and `chubForehead`, `chubCheek`, ...) bowing the new points out. `detail`: below .75 the lattice
itself (~900 triangles), 1 once (~5,000), 1.5 twice. The back of the head is the cranium's loft (`headGrid`, which
the hair grows on). ACTIONS move the lines (FACS: `browInnerUp`, `browOuterUp`, `browDown`, `lidUp`, `blink`,
`cheekUp`, `smile`, `mouthDown`, `pucker`, `lipsPart`, `jawOpen` -- the jaw turning about the condyle), mixed by
`expression` (happy, sad, angry, surprised, afraid, disgusted, sleepy) and `viseme` (A, E, I, O, U, MBP, FV, L, S,
TH); the lattice's topology never changes, so these are morph targets in waiting. Roles: `skin`, `lip`, `mouth` (the
mouth's inside), `eye`, `iris`, `pupil`, `brow`, `hair`. The viewer draws the guide lines red over the skin (`guides`,
G). Every attribute is read from the definition's params by name (a part maps only the skull's: `faceW`,
`forehead`, `occiput`, `crown`, `earS`, `hairline`); `tools/facegen.py` writes the canon and the kinds (man, woman,
child, elder, beast-man) as ranges over them, then `tools/hairgen.py` gives them their hairstyles.

## Hair

A hairstyle (`hair.js`, `hair/*.json`, the part type `hair`) is GROWN FROM THE HEAD'S OWN VERTICES: the scalp is the
face loft's rows above the hairline (`face.js headGrid`, shared with the face), and from its points strands start --
each a ribbon of a few segments, seen from both sides, leaving the scalp along it (the comb's direction laid on the
surface, a little off the skin), bent down by gravity, pushed off the skull wherever it would pass inside, waved or
curled. Only the outside is seen, so a sheet of ribbons is enough: no volume inside. A style says:

- `strands` groups: a `region` of the scalp (`y` heights in the face's frame: the crown +.10, the hairline ~.06,
  the ears' top 0, the nape -.06; `th` angles round the head: 0 the forehead, 90 the ears, 180 the nape),
  `length` [front, back], `comb` (down, back, forward, out, up, or a vector, mirrored per side), `hang` (0 stands
  off .. 1 falls), `off` (how far off the skin it starts), `wave` {amp, per}, `curl` {r, per}, `width` [root, tip],
  `every` / `extra` (how many), `to` (gathered at a point; `toMirror` one a side), `when` / `unless` a param
  (a fringe, a middle parting without one);
- `locks`: single long strands from a place (`at` [angle, height]), `n` of them -- the two locks in front of the ears;
- `gather`: what holds it -- a `rope` (a ponytail) or a `plait` (three strands winding round its path) from a
  point in a direction, with a `tie`; a `bun` or a `knot` (a topknot); `mirror` for one a side.

- `cap`: THE HAIR'S BODY -- one rounded shell of triangles over the skull (the grid's own rows and rings pushed out
  by `thick`, more by `crown` at the top and back, thinning to nothing at its edge), whose EDGE runs lower than the
  skin's hairline as hair does: `front` (y at the forehead), `temple` (45 degrees round), `side` (over the ears),
  `nape` (the back), `fringe` the front's y when the face has one, `top` the y above which the skull is bare
  (a tonsure), `sweep` (2026-10-30) the degrees round the head its locks run back for every 10 cm they fall from
  the crown -- its u sheared by its height, so hair drawn back (a bun's, a braid's: hairgen.py `BACK` 80) is carved
  and painted from a parting at the front back over the temples to the nape, where it had radiated from the crown as a
  crop does (0, the default). Strand groups with `edge: true` hang from that edge (one a column, `extra` between) instead of
  growing all over the scalp -- a bob, long hair, the curls -- so the sides and back read as a rounded head of hair,
  not a sheet of ribbons.

- CARVED (2026-10-30, hair.js `CARVE`; the face's `carved`, set by heads.js for a statue's head and handed to its
  hairstyle): every strand is a solid LOCK (a crest standing `lock` of its width off the head, its sides falling to
  its edges), its curls `curl` as wide, `length` as long, and a lock in front of the face (within `open` degrees of
  the forehead) ends above the brows (`brow`). Flat ribbons in stone were chips lit from either side, and a fringe of
  curls hung over a statue's eyes as a scatter of shards.
  A style may say what a sculptor makes of it (2026-10-30, its part's `carved`: keys laid over the part when carved,
  hair.js hairGeometry; `carve` there too, heads.js): `curly` is carved as its cap in round CURLS, its strands left off
  -- the classical head of curls, a philosopher's, Zeus's -- and `short` as its cap alone, cut in locks combed from the
  crown -- a Roman portrait's; their hanging strands had been carved as a mop of stone noodles over the brow. The cap is
  the same either way: a wreath, a diadem is fitted to it.
  Its cap and sheets are cut in WAVY LOCKS in relief (shell.js `stoneCarve`, `STONE.locks` .. `lockRelief`): the
  hair's uv (u across it, v down it in metres -- a carved lock's own v too) makes each lock a rounded ridge whose slope
  tilts the normal (the surface gradient from the pixel's derivatives), waving down the head as an S every `lockLen`,
  each a little behind its neighbour. Straight grooves down the meridians had made every statue's hair a ribbed pot.
  CURLS (2026-10-30, shell.js `stoneCurls`, `CURLS`; heads.js the geometry's `curl`): a beard is carved in curls, and so
  is the hair of a hairstyle that says `"carve": "curls"` (`ushnisha`: a Buddha's -- a close cap and the crown's bump,
  snail curls over both): domes packed over the surface, a Voronoi of jittered points `size` apart in the world (statues
  stand still), each rising from the groove where it meets the next, a spiral cut round it `turns` times, the normal
  tilted out from its middle by `relief`, the grooves in shade -- fading where a curl is under a few pixels.

- `sheets` (2026-10-03): the hair as a CLOTH hung from the cap's edge -- its first ring IS the cap's edge, column for
  column; each further ring a horizontal cut (`drop` below the edge, `out` off the head, zig-zagged: points out by
  `zig` and in, the out ones down by `zy`, `phase` shifting the teeth half a step, `vary` jitter, `onHead` back on the
  skin). Cuts half a tooth apart fold the cloth into pyramid-shaped locks, the last cut's points their tips -- drawn
  ("manga") hair; rows are added every 3.5cm between the cuts so a long fall bends over the shoulders. `region.th`
  the columns it covers (60 or more leaves the face open; [0, 50] is a fringe of pointed bangs), `sub` points a column,
  `double` both faces. Styles `manga-long`, `manga-bob`, `manga-short`; on the people (people.js) a woman's long hair is
  straight, wavy or drawn by her seed, her bob drawn every other seed, a man's short hair drawn one in four, and an
  outfit's `hair` may name any hairstyle (wardrobe.html's hair row shows them all; `?hairs=a,b` picks some).
- `spikes` (2026-10-03): hair in THORNS -- a lattice of its own over the cap (`rows` from its edge toward the crown,
  `cols` per 180 degrees), every point on the cap but a sparse checkerboard (`every`-th column on every other row,
  the rows half a step apart) pushed far out: `length` [front, back] along the normal bent `blend` toward `comb`, `vary`
  jitter. Each far point's neighbours stay on the cap, so each is a sharp pyramid; the edge rows lie on the cap's edge,
  so the thorns rise from the hair and fall back to it; flat facets. Its rows are spaced evenly along the skull's curve
  (by the angle from the crown, not in height) up to a few degrees from the crown, and a full ring is closed there by
  one more thorn -- the top of the head is thorns too. The lattice itself is `thorns.js` (thornLattice), shared with the
  manes. Styles `spiky-back` (swept back and up all round, pointed bangs and side locks), `spiky-up`, `spiky-wild`.
- **Manes of thorns** (`manes.js`): a creature whose mane (an `extras` ellipsoid) has `thorns` -- the lion's, the
  manticore's -- gets the same lattice as a SLEEVE hugging its neck and the back of its head (rows `along` [from, to]
  neck lengths from the chest end, each at the creature's radius there, `inset` into the fur so the spikes grow out
  of it; spikes `length` x the mane's radius, swept by `comb`/`blend`); the soft ball is no longer drawn (its part
  stays, a point). One InstancedMesh per kind, placed every frame on the posed NECK (sized by its length now), shaded
  as hair with a softer sheen. mammals.js reports it as `def.mane`; composite.js keeps it on the animal; the game and
  the asset viewer place them. (The hair's sheen itself was halved: s1 .17, s2 .15 -- it read oily.) The sleeve sits a
  little OVER the fur (`inset` 1.15: the blended surface stands out past the parts' radii) so mane, not skin, shows
  between the thorns; round a ring whose columns are no multiple of `every` a spike gives way to its neighbour across
  the seam (it made one thorn with two points). A triangle part's plate in shell.js closes its rim ring ON its first
  corner (its last cut carried the third edge's offset, its first the first edge's: a sliver of nothing from the
  plate's centre to that corner -- the cracks across wing membranes, ears, fins); wing parts draw no border band
  (`edge: 0`).
- **Sculpted creatures** (`"kind": "sculpt"`, 2026-11-04: bodyspec.js, bodymesh.js, bodies.js; docs/engines.md
  "Sculpted bodies"): the hedgehog is no longer parts. Its definition is a `skeleton` (the root, the head's pivot and
  idle turn, four IK legs from hip points, an ankle height and radii), a `shape` list of blended primitives on those
  bones (ellipsoids, round cones, spheres, tubes, boxes; `k` the blend, `mirror`, `seat` -- an ear set ON the surface
  the others make), `eyes` (found on the head's surface, eyeballs in carved sockets, mirrored), a `coat` of quills
  (gap, len, r, lean, vary, skirt, drop, face, rise, tip, dark, darkTip, base, hold: sown where shapes with
  `coat: true` are) and a `mesh` budget (`cell`, `tris: [near, far]`, `far` metres). It is ONE skinned mesh: about
  5.4k triangles near (1.6k of body, 1077 quills of 3, two eyeballs) and 1.8k past 4 m (600 of body, 350 quills).
  Its first versions were 126 cone parts, then a rig mammal under a quill coat mesh -- seams, steps in the density,
  eyes floating off a head they were painted beside.
  Every other creature is now drawn the same way, converted from its parts when it joins a herd (bodyspec.js
  `sculptOf`): its parts become its bones and their shapes the field, and nothing in its definition changes.
  `"sculpt": false` keeps a definition as parts, and `?sculpt=0` shows the old drawing.
- Hair below the nape is pushed OFF THE BODY (an ellipse growing from the neck's to the shoulders' section): long
  hair falls over the back, not into the dress. Hanging hair starts 55-60 degrees round from the front, so it frames
  the face instead of covering its sides.

**The sheen** (`heads.js` HAIR_SHEEN, config.json people.faceShade.hair overrides): hair is shaded KAJIYA-KAY on top of
the faces' half-Lambert -- two highlights where the half vector is square to the hair's direction (one white and
tight shifted toward the tip, one broad in the hair's colour toward the root, both jittered strand by strand). The
direction is v's gradient on the surface, read from screen derivatives (v runs along the hair in every part: a
strand's length, the cap's and a sheet's height), so it needs no tangent attribute and holds under the instancing.
`paintedGeometry(built, { strands: ["hair"] })` keeps the hair's uv and a `hairMask`. THE FIBRES are the hair's
texture, drawn in the same shader: value-noise streaks across u (which runs across the hair) at `freq` and 2.7 times
that, wavering down it, `fibre` strong, fading where finer than a pixel. A hairstyle whose cap has a `top` (the
tonsure) gives the face `bare` (heads.js hairFaceParams): the face paints its scalp as skin above it, so the shaven
crown shows. (Found on the way: items.js
dropped the groups' `roles`, so the lips' flat shading had never applied either.) The asset viewer shows a hairstyle
ON A HEAD (items/faces/woman wearing it; `head` off shows it alone, `fringe` toggles the face's fringe), through the
same material.

A face definition names its `hairstyle` (a pick by kind: `facegen.py`) and passes the head's own parameters to it
by their own names (hairgen.py `PASS`; the hair part maps them onto its fields, `scale` as its `headScale` -- until
2026-10-06 the face passed `headScale` and the hair never read it: every hairstyle was the canon's size, 5-15% too big
on the people, whose heads are .85-.99 of it), with the forehead's attributes (`foreheadHeight`, `foreheadAngle`,
`browRidge`: face.js `foreheadOf` lifts the scalp to this face's forehead, as the face's own forehead rows are -- a
child's upright brow stood a centimetre through the fringe), so the strands sit on that skull; `fringe` draws or parts the front. Checked as a contact sheet of every style on
the canon face (front, side, quarter). 3-6k triangles a head with hair; the wide long styles use one strand a
scalp point, the short ones two.

**On the people** (`heads.js`, `PEOPLE.face`, on by default; `config.json` people.face turns it off): every person
gets a mesh head instead of the SDF marks and nose. `people.js` shrinks the head capsule to a pin (it stays the
parent of the hair and the hat, and the frame the mesh stands in) and keeps a pin of a nose as the GAZE; the def
carries `face` { kind, seed, skin, hair, hr, head, gaze }, the composite keeps it on the animal, and `heads.place(herds)`
sets one instance matrix per person each frame from `herd.ends` -- the head's axis from the capsule, where it looks
from the gaze -- as `tools.place` does for hands. A kind is (kind of face, seed % 5, skin, hair, cranium radius to 5
mm): one InstancedMesh each, its colours baked into the vertices and shaded by facing (every face material is paint):
what looks forward (+x, where the face looks) is lit full and the shade falls off gradually round to the back --
`config.json` people.faceShade: `dark` (how dark the back gets), `gamma` (the gradient's shape), `up` (a little light
from above), `skin` (one base skin colour for all, or null for each person's own).
The mesh head wears its hair too (`face.style`, from the person's SDF style: short, bob, long / long wavy, ponytail,
bun, braid; `flat` under a hat; `none` shaved), so `people.js` draws no SDF hair for it; the hats stay SDF, over
the mesh skull, which wears the hair colour above a low hairline so nothing shows through them as skin. What is lost: the marks' expressions (faces.js:
blinks, smiles, talking mouths) -- a mesh head is still; `PEOPLE.face = false` brings them back. Not there yet:
expressions on the mesh (swap eye and mouth pieces), eyelids, teeth, beards.

## Organ

`furniture/organ`: a pipe organ by `W`, `H`, `D` -- a case on a plinth, the impost and cornice gilt, the facade of
pewter pipes (conical feet, cylindrical bodies) in a centre tower, two side towers and two flats under pipe shades,
the console (two manuals, pedals, a bench) built into the front; it faces -x into the nave and carries the organist's
`spot` marker (pose sit, gesture `play`). Churches place it through a floor `zone` (docs/arch.md): the cathedrals a 10 m one at
the west end; a village church has none (its west door needs the nave end free).

## Food

The produce of the orchard, the field and the market (`food/*.json`, generated by `tools/foodgen.py`; the
"Items: food" category): 30 fruits and vegetables built from the language's own primitives, nothing new in
`items.js` -- a fruit or a root is a `lathe` (apple, pear, plum, peach, orange, lemon, fig, pomegranate, melon,
pumpkin, marrow, carrot, parsnip, turnip, onion, garlic, beetroot, radish, tomato, potatoes, an ear of maize),
`faceted` where it is ribbed or lumpy (pumpkin, garlic, potatoes, maize); a pod or a cucumber a `sweep` with one
segment a station; grapes, cherries a cluster of 5-6-sided `sphere`s on rings; caps (strawberry, tomato, mushroom's
gills and cap) a capless `double` lathe. Each comes with its GREENS, as a market stall sells them (`foodgen.py`
LEAVES): a leaf or two on a fruit's stalk, the carrot's and parsnip's feathery tops, the rosettes of the turnip,
beetroot and radish, the strawberry's trefoils, the dry straps of onion and garlic -- fans of leaves are the
`feathers` primitive (one vane a leaf), the lobed leaves of vine, fig, pumpkin, melon, marrow and cucumber thin
plates. Each carries a
`hold` (the grip at its middle, the axis up its length), its size drawn a little its own by the seed (`s`), and
its colour from paint materials added to `materials.json` (apple-red / green / yellow, plum, grape-purple /
green, pumpkin, carrot, ...; a few are picks: an apple is red, green or yellow). 90-340 triangles each, the grape
bunch 740. The market's other wares are here too: loaf, round loaf, cheese wheel and wedge, ham, sausages, fish,
eggs -- on the stalls of `furniture/market-stall` (its `wares`: pottery, vegetables, fish, meat, eggs, bread, fruit,
cheese), which the market places (docs/arch.md). Not there yet: heaps of them in kitchens, cut halves.

## Birds

Birds (`birds/*.json`, `tools/birdgen.py`). Since 2026-11-05 only the stork is still an item (listed under "Items:
components"), for the chimney nest's folded and spread poses (index.html `storkSet`); the other 26 duplicated the
creatures in `assets/creatures/birds` and were removed (birdgen.py keeps their numbers in `BIRDS`, writing only `KEEP`).
The item birds were made with FEATHERED WINGS AND TAILS: the part type `feathers` (`feathers.js`) lays a fan of feathers in the part's
x-z plane -- `n` quills rooted along a `roots` line, their directions from `dir` [first, last] (degrees from +z out
along the span, 90 straight back), `length` and `width` [first, last], each vane a strip of 7 triangles (leading
vane narrow, trailing wide, `shape` pointed / rounded / square at the tip), `droop` bending the tips down, `lift`
stacking each next one a hair higher so they overlap without fighting, `tuck` running each quill on inward of
its root by that share of its length, under the coverts (a vane starts at nothing: rooted on the coverts' edge, a
notch of nothing opened between every two -- the wing component tucks .35), `band` the tip's share in a second `tips`
material (a magpie's white primaries with black ends, a pigeon's tail bar, the peacock's eyes). Doubled like a
sail. One wing component (`components/wing`) is the arm and the hand: the secondaries fanned off the forearm,
the primaries off the hand, one plate of coverts over their roots (the rest of the wing has no single feathers),
by `span`, `chord`, `pri` / `sec` counts, `sweep` and `spread` (1 flying, 0 folded along the flank with the hand
folded onto the arm); the bird's `pose` pick puts the spread or the folded pair on the shoulders (`when`). The legs follow the pose too (2026-10-24): standing legs with the folded wings, and with the spread ones `thigh/tarsus/toes flying`, trailing back under the tail. Before, every bird flew with its legs hanging as if it stood. The
body is a spindle `sweep` with a breast ellipsoid, the neck a curved sweep for the long-necked (goose, swan,
heron, stork, flamingo, crane), the head a sphere, the beak a cone rod (`flat` stretched for the ducks), a crest
or comb another feather fan, a train (peacock, pheasant, the rooster's sickles) a second longer fan in the tail.
~1100-1400 triangles a bird; the wing shapes: pointed (swallow, gull, falcon, pigeon), rounded (crow, hen,
buzzard), broad (eagle, stork, swan). Not there yet: on the game's flying birds (creatures/birds are SDF parts),
flapping, barring and eye spots as patterns rather than paint. The STORK (2026-11-03, birdgen.py `stork_poses`) has
the poses the nest's pair live by (index.html storkTick): `folded` (standing), `bow`, `clatter` / `clatter2` (head
thrown back on the shoulders, the bill shut / open), `preen` (bill in the breast), `sit` (in the bowl; `sitDrop` its
drop), and in flight `spread` (gliding), `flap-up` / `flap-down` (the beat's two ends) and `landing` (legs down,
wings braked forward).

## Props (2026-10-02)

What the world carries and moves, out of the code that built it (`tools/propgen.py`): `tools/sack`, `furniture/cask`
for the freight's and the carts' barrels, `components/water-wheel` (turned about z by the current), `components/
windmill-sails` (four `windmill-arm`s, turned by the wind), `ships/barge` (its ten cargo places `hold` markers, the
gangplank's foot a `plank` marker; `deckY`, `halfL`, `halfW` its params) and `components/gangplank`, `components/
cart-wheel` (r, n spokes) and the three cart bodies `components/cart-small|medium|large` (their `load` 0..4: casks
lying in chocked pyramids, standing casks, kegs, sacks in two courses; 5 the harvest's sheaves heaped, `tools/sheaf`,
never drawn on the road -- index.html CHORES; 6-12, 2026-11-03, `cultural`: amphorae lying in straw, amphorae and
sacks, jars and hampers in straw, bales, crates and sacks, tubs and bales, a pyramid of rice bales -- which a world
draws is assets/world/goods.json `loads`; their bed, floor and axles in their params,
which carts.js reads its sizes from), `weapons/arrow`, and `food/fish` for the fisherman's catch -- and for the
season's chores (2026-10-23) `furniture/woodpile` (a chopping block with a round on it, the split billets stacked beside
at +x) and `components/ice-hole` (dark water in a round cut, slush and broken ice about it). The CULTURES' VESSELS
(2026-11-03, the freight's goods by period: assets/world/goods.json, docs/world.md "Freight"): `tools/transport-amphora`
(0.74 m, pointed toe, two handles), `tools/pithos` (1.35 m storage jar, rope bands), `tools/storage-jar` (cloth-covered,
tied), `tools/hamper` (lidded basket), `tools/bale` (corded cloth bale), `tools/straw-bale` (Japanese tawara, lying along
x), `tools/crate`, `tools/tub` (with rope ears), and what porters carry with them: `tools/carrying-pole` (on the
shoulder, cords down to the load at `reach` ahead, the porter's own basket behind) and `tools/tumpline` (the strap
from the brow, `hy`, down to a load at `ly`/`lx` behind). Not generated:
`furniture/stall-season`, the market's greengrocer's and fruiterer's wares by `wares` and `season` (index.html builds
each season's once and shows the world's). The game builds
them through `architecture.js itemGroup` (one group) and `itemInstanced` (copies: the same root / set / commit API
as the parts-list helpers), and the arrow as one painted geometry (`tools.js paintedGeometry`, which the faces use
too). Each counter placement is a little heap of three and each basket holds one more (2026-10-24: two or three pods on a
2.4 m counter read as bare; 49 -> 133 pieces).

**Alternatives** (the same day, later): the pieces the code still drew its own way are items too, BESIDE the
catalogue's finer ones rather than instead of them -- `ships/fisher-boat` (the fisherman's rowing boat; `ships/skiff`
stays), `components/fisher-oar` (`side`; since 2026-11-22 a wrapper placing `components/oar` along z, its loom and blade
colours its own, the geometry unchanged), `tools/fishing-pole` (beside `tools/fishing-rod`), `components/fishing-line`
(1.8 m from the rod's tip; the game stretches it to the water), `furniture/barrel` (`h`, `belly`, `head`: a big barrel
or a keg; beside `furniture/cask`) and `barrel-on-side`, `tools/sack-standing`, `components/meal-chute` (retired 2026-11-22: the mills' meal chute is the building's own upright duct),
`components/fish-hanging` (from a drying rack), the tableware `mug`, `jug`, `bucket` (a vessel's walls are one lathe,
id `walls`: tableware.js reads the drink's level from its profile and the `floor` param) and `trough` (w, h, d, t,
floor), the plates' food `food/plain-loaf`, `cheese-slice`, `sausage`, a field's `food/cabbage-head`, and the plain
furniture the castle and the palace are furnished with -- `furniture/plain-table`, `plain-chair` (a `seat`),
`plain-bed` (a `lie`), `plain-wardrobe`, `sofa` (a `seat`), `chandelier` (hung from its origin). index.html rows the
boat, ships its oars and fishes with the pole and line from them; tableware.js makes every vessel and dish from them.

## Holding it

Every item a hand can hold says where the hand closes on it. **`hold`**:

| key | what |
|---|---|
| `grip` | where the fist closes, in the item's own frame |
| `axis` | the handle's line through the fist, pointing out of it on the thumb's side (toward a sword's point, a spade's blade) |
| `face` | square to it: which way the edge or the front looks (a sword's edge, a shield's face) |
| `grip2` | the other hand's place, for a two-handed hold (a halberd, a longsword, a bow's string) |
| `carry` | `{ axis, face }` in the HAND's frame (+x forward, +y up, +z to the right): how it is carried -- upright by default |
| `follow` | how much of the forearm's turn the HAND takes holding it -- the wrist: 1 rigid with the forearm, 0 upright in the figure's frame (0.7 by default: a hoe swings; a sword 0.35; polearms, shields, bows and the lute 0; a holder may give a negative one, tipping it forward: an axe on the block). The skeleton turns the hand so and the item lies rigidly in it, its grip in the fist (2026-10-24: it used to be placed in a frame of its own built from the forearm's heading, which flipped as the forearm passed upright, the hand going on without it) |
| `upright` | an ATTRIBUTE, shown held up whatever the hand does (2026-10-30): a statue's hand takes the `upright` grip for it, whatever its pose's grip (statues.js) -- a horn of plenty stands on an offering palm, it does not lie along the fingers into the body |
| `rest` | `"ground"` (or a holder's `ground`, 2026-10-30: a statue's shield resting by its side): at rest it stands on its butt on the ground (the floor its figure stands on: a rig's `sole` under its origin, joints.js ground -- a kneeling spearman's spear had stood half a metre into the floor, at his lowered origin), and the hand slides along it (a spear, a halberd, an ordered musket); `"body"`: it rests against the body where the hand holds it on the whole, the hand playing over it (a lute: tools.js BODY_REST) |

`holdMatrix(hold)` turns that into the one matrix that puts the item into any hand. `tools.js` moves each kind of item
into the hand's frame once, at build, as one InstancedMesh per material. Each frame, every copy is one matrix at a
person's hand, read from the posed skeleton. A person's `tool` is the old name (`"scythe"`, `"sword"`: `TOOL_ITEMS`),
an item's path, or either with `#seed` for one of its kind (`"items/shields/heater#3"`).

**Kits** (`kits/guard.json`) are loadouts by weight, each with a `main` (the weapon hand) and an `off` (the other: a
shield), each an item or a pick. `items.js pickKit(kit, seed)` draws one for a person, and one of `variants` of each
item, so a watch of a dozen carries a dozen weapons from only a few distinct meshes. The town's guards are armed this
way (index.html).

**Attributes** (2026-10-30, `tools/attributegen.py`): what a figure of myth or allegory carries, as items of
`items/tools/`: the PALM FROND (a rachis, two `feathers` fans of leaflets swept toward its tip, long at the foot), the
CORNUCOPIA (a `sweep` of growing radii curling to its point below the hand, a rim at the mouth, the food catalogue's
grapes, apple, pear and pomegranate heaped in it by `use`), the SCROLL (a turned roll on its rod, knobs at either end)
and the VICTOR'S WREATH (a ring of laurel, one sprig placed round it by an `at` list, held by its rim facing forward); and of the gods (2026-10-30): the PATERA (the libation dish, a turned bowl round its raised boss, tongues round it by
`around`, level on the fingers), the LYRE (a turned dome laid on its back for the tortoise-shell box, `stretch`ed oval, two
horns mirrored up out of it, a yoke, seven strings by `along` from a bridge; stood on the fist by its foot), the TRIDENT
(a shaft, a socket, three barbed prongs, the outer two `mirror`ed; it `rest`s on the ground as a spear does) and the
CADUCEUS (a short staff, two snakes one helix mirrored across it so they cross before and behind, their heads meeting
under a pair of `feathers` wings turned upright).
Each is `upright`; a statue's marker hands them out (`hold: { R: "items/tools/victor-wreath" }`).

## In a building

An arch part of `type: "item"` (arch/assemble.js) places an item: `item` (its path), `params` (expressions over the
building's, as a component's are), `seed`, `materials`, and the usual `at` / `repeat`.

- The building keeps only the item's **box**, so the walk and the wall field go round it as they went round the
  blocks rooms were furnished with before. `solid: false` gives no box (a candlestick on the altar).
- `architecture.js` draws the item itself: every copy of every item in the building merged into one mesh per
  material (`itemMeshes`), the finish leaving the part alone.
- Its **markers** (a seat, a bed, the places at a table) become the building's, at every placement. `markers` keeps
  them all (true), none (false) or those of the listed roles: a table's benches give their seats, and the table
  gives the places. `data` is added to each (a bed upstairs: its `storey`).

A marker's `at` may carry a yaw (degrees) like any placement. Every bed lies along x with its head at -x, and its
marker is turned 90 degrees, so its local +z is the foot, which is where `lifeOf` looks for it. A place's `face` is a
heading relative to the marker (0 faces +x, pi/2 faces -z).

The village's furniture (`tools/archgen/village.py` -> `assets/architecture/furniture/`) is built this way. The bed is
a bedstead with the pallet lying in it, and the table is a trestle table with two benches. There are a plank chest,
casks, a settle with a pew's low back, candlesticks on the altar, and the trades' tables, stools, benches, spinning
wheel and quench cask. Hearths, forges, ovens, counters and shelves stay masonry and joinery of the house's own. A
house passes `look` (a seed from its own size) so no two houses have quite the same furniture.

The game registers every item in the catalogue with the assembler (`catalogue.js`, loaded once). A page that
fetches what a definition asks for (`loadUses`) fetches the items too, and what they stand on.

## The viewer

`assets.html`: an item is shown built from the editor's text. Its grip is a red dot with the handle's line out of it,
`grip2` an orange dot, its markers green dots. `S` draws another of its kind, and `+`/`-` changes its detail. A kit
is shown on a row of eight people, each armed out of it by `tools.js` exactly as the game arms them. The materials are
shown on spheres.

## How it was checked

Contact sheets of every item at two seeds (`ref/items.html`): all build, no missing materials. Rows of guards and
of villagers at work, armed through `tools.js` (`ref/kitshot.html`): grips in the hands, shields on the off arm facing
out, pole butts on the ground (lowest point 0.00-0.07 m). The game, headless: the guards at the gate. The village's
furniture assembled (`ref/furncheck.html`): item parts, their meshes and triangles, the markers with their headings
drawn (a table's places face it, a pew's face the altar), every house's bed on its storey.

## Ornaments (2026-10-30)

Category `ornament` (`assets/items/ornaments/`): architectural ornaments that a building places as an item part
(`type: item`). The first is the **acroterion**: a Greek temple's floral apex ornament. Two volutes rise in an S from a
calyx of acanthus on its plinth, and a palmette fans out over them, its leaves alternately green and blue round a red
heart, the volutes gilt. Its face is the x-y plane, seen from either side, and `h` is its height. The temples put one
on each apex of a pediment (temples.py, acropolis.py `acroteria`).

## Crafts and trades (2026-11-21)

Nineteen items for the musicians, the tables, the workshops and the mine, made by `tools/craftgen.py` (in the manner
of `tools/propgen.py` and `tools/modern/kit.py`: a params block, materials as roles, most of them a seeded pick). Run
it with `python3 tools/craftgen.py`: it writes the files and registers them in assets/index.json under its lock.

- Instruments, held as the lute is: **`tools/fiddle`** (style `violin` or `vielle`, its bow across the strings),
  **`tools/recorder`** (length `L`, optional ivory rings), **`tools/flute`** (a six-holed transverse flute, optional
  ferrules), and **`tools/harp`** (a soundbox, a curved neck and a pillar, sixteen strings, the pins). A musician holds
  the instrument of the song being played. The fire's and the wedding's musicians get it from index.html `bardTick`, and
  the fountain bard gets it from village-life.js `holders()`, which now gives `bard`. tools.js `TOOL_ITEMS` names these four and
  the lyre.
- **`tableware/plate`**: `style` trencher, pewter (a cast bead round the rim) or ceramic (a painted band), and `well`,
  the height of the food above the foot. In tableware.js every dish stands on a plate, a trencher unless the dish says
  `plate`. When the food is eaten, the plate stays.
- **`tableware/cauldron`**: a pot-bellied iron pot with a bail and ears. `mount` is `legs`, `chain` (links from `top`
  down to the bail) or `tripod`, and `lift` is the height of the pot's foot. A house hearth (architecture/furniture/hearth)
  hangs one on its chain over the fire.
- Workshops (tools/archgen/village.py, in place of their box clusters):
  - **`furniture/anvil`** on its banded stump, its horn at +x (smithy);
  - **`furniture/bellows`**, its nozzle at +x, its top board on a hinge (`open`, the `blow` hinge) and `pipe` bending the
    pipe toward -z (smithy, piped into the forge);
  - **`furniture/floor-loom`**, the weaver at +z (weaver);
  - **`furniture/workbench`** with a leg vice and a drawer, its front at +z, and **`furniture/sawhorse`** (carpenter);
  - **`furniture/kick-wheel`**, the potter at -x and a pot on its head (pottery);
  - **`furniture/chopping-block`** (butcher);
  - **`furniture/dress-form`** with a garment on it, and **`tools/shears`** lying open (tailor);
  - **`tools/oven-peel`**, which leans `lean` degrees toward -x (bakery).
- The mine (mine.js, then `node tools/archgen/mine.mjs`):
  - **`tools/frog-lamp`**, a miner's open lamp. Its origin is the flame, which is also its `fire` marker, so it gives
    the light that the bare markers gave. Its spike points to -x and is driven into the rock.
  - **`furniture/windlass`**: its axle runs along z at 1.06, with posts at z ±1.25, a roped drum of radius 0.15, and two
    cranks half a turn apart.
  - **`tools/kibble`**: a banded hauling tub on a bail. With `full` it holds ore.

Hoops and small rings are open lathes, built by craftgen's `band()` and `ring()`, rather than items.js `ring` sweeps,
which cost two to three times the triangles.

## Everyday things (2026-11-21)

Twenty-nine household, yard, farm, bath, school and music items, made by `tools/craftgen2.py`. It is a sibling of
craftgen.py: it imports craftgen's helpers (`item`, `beam`, `band`, `ring`, `smooth`, `write`) and kit.py's parts, and
it registers its items in assets/index.json under the same lock. Run it with `python3 tools/craftgen2.py`. Where one
item covers an old and a modern form, `style` picks it (the seed draws one when it isn't given).

- Kitchen and table (catalogued under "Items: tools", as craftgen's tableware is):
  - **`tableware/cooking-pot`**: `style` earthen, copper or saucepan (handle along +x); `lid`; `fill` shows the stew;
  - **`tableware/frying-pan`**: `style` iron (a skillet with a hanging hole) or steel (a non-stick floor, a long grip),
    the handle along +x; `egg` fries two eggs in it;
  - **`tableware/kettle`**: `style` copper (a hob kettle with a gooseneck spout at +x) or electric (a jug on its base,
    its flip lid on the `flip` hinge);
  - **`tableware/bowl`**: `style` wood or ceramic; with `fill` it holds food, as the mug shows its ale;
  - **`tableware/goblet`**: `style` pewter, silver or glass (`window-glass`, so you see the wine); `fill` is the wine;
  - **`tableware/bottle`**: `style` wine (corked, `label`) or stoneware (a Bartmann bottle with its handle and mask);
  - **`tools/ladle`** (`style` iron or wood), **`tools/wooden-spoon`** and **`tools/kitchen-knife`** (`style` chef or
    old). All three hang with the handle up +y, the ladle's and spoon's bowls opening toward +z.
- Yard:
  - **`tools/wheelbarrow`**: `style` wood (on `components/cart-wheel`) or steel (a lofted tray, open at the top, on a
    tubular frame with a tyre); the wheel is at +x;
  - **`tools/ladder`**: `n` rungs 0.28 m apart, `L` derived from them; `style` wood or aluminium; `lean` tips it back
    toward -z about its feet;
  - **`tools/watering-can`**, its spout and rose toward +x;
  - **`tools/flowerpot`**: a terracotta pot on a saucer. `plant` names an item in assets/items/flowers, which is placed
    in the pot and drawn at `ph` (its `h`); `""` leaves the pot empty. Each plant is its own literal `use` part,
    gated by `when`, because loaders fetch an item's uses by their written paths. The eight whole plants it can hold
    (tulip, daisy, rose, lavender, poppy, cornflower, iris, sunflower) are now registered under "Items: flowers",
    since the viewer builds only from the catalogue;
  - **`tools/suitcase`**: it lies on its back with the handle at +z; `style` leather or hard. The upper half is the
    `lid` hinge along the back edge;
  - **`tools/rope-coil`**: flat turns as one open lathe of bumps, a second layer, a loose turn and a trailing end;
  - **`tools/chain`**: `n` links of length `link`, hanging from a ring, with a hook at the bottom.
- Farm: **`tools/plough`** (`style` ard or mouldboard, the team at +x; the mouldboard turns the sod to +z),
  **`tools/butter-churn`** (a plunge churn, its height `h`) and **`tools/quern`** (a rotary hand quern on its board).
- Bath and medicine:
  - **`furniture/washstand`**, on turned legs, with its basin, ewer and towel; `water` fills the basin;
  - **`furniture/bathtub`**, along x: `style` clawfoot (a lathe drawn out 2.12 times along x, painted outside and
    enamelled inside, on claw-and-ball feet) or built-in (a lofted basin in its apron); `water` fills it;
  - **`modern/furniture/toilet`**, its back at -z, the `lid` hinge at the back; a `seat` marker;
  - **`modern/furniture/wheelchair`**, its front at +z, with a `seat` marker;
  - **`tools/crutch`**: `style` underarm or forearm.
- School: **`tools/globe`**, its axis tilted 23.5 degrees. The continents are spherical caps in three colour roles
  (craftgen2 `cap`).
- Music and play:
  - **`tools/drum`**: `style` tabor (V-laced, with a snare and a strap) or snare (lugs, rods and sticks);
  - **`tools/ball`**: `style` leather, football (twelve 5-sided caps where an icosahedron's corners are) or beach
    (twelve sweeps of a flat section, as gores, over a core);
  - **`tools/guitar`**: `style` classical or steel; held as the lute is;
  - **`tools/trumpet`**: `style` valved or natural, its bell toward +x.

New helpers in craftgen2:
- `shell(outer, t, floor)` turns a vessel's outside profile into a closed turned wall;
- `surface()` puts a level disc (stew, water, soil) at the wall's inside radius;
- `orient(pos, ("x", a), ("z", b))` applies turns in the order given (a side board leaned out, then the tray tipped);
- `toward(pos, d)` points a part's +y along d;
- `cap()` makes a spherical cap;
- `ringx()` is a ring whose radius and tube may be expressions;
- its `sweep` defaults to 3 samples a span, not items.js's 6.

Two materials were added: `stoneware`, a salt-glazed brown, for the Bartmann bottle and as a pick for pots and bowls;
and `copper-bright`, polished kitchen copper (the library's `copper` is roof verdigris), for the copper pot, kettle,
watering can, ladle and a clawfoot tub's outside.

## Not there yet

- `grip2` is data only: nobody's other hand is moved to it yet.
- Held items don't lie flat, hang at a belt or ride on a back. A carry is always in a hand.
- Items in rooms are drawn at full detail however far away the house is.
- Only the town's watch has a kit. The farmers' tools are still one per trade.

## Flowers

`flowers/` (tools/flowergen.py, "Items: flowers"): BLOOMS (`flowers/blooms/<kind>`: the flower alone, its face up +y,
at true size -- daisy, poppy, sunflower, tulip, rose, cornflower, buttercup, bluebell, foxglove bell, lavender spike,
iris, lily, hibiscus, frangipani) and PLANTS (`flowers/<kind>`: stem, leaves and blooms on y = 0 -- the blooms drawn
1.6 x life, the leaves fuller, or at a few metres they vanish). The petals, sepals and leaves are the `petals`
primitive (petals.js): a whorl of `n` curved blades (in `layers`), each leaving the axis at `r0`, rising at `cup`
degrees and bending by `curl` more over its length, cupped across by `cupped`, twisted by `twist` (a pinwheel), its
outline the `shape`'s (round, oval, pointed, strap, heart, fringed, spoon, lance), `rows` x `cols` quads, `throat`
and `band` shares in their own materials (a poppy's black blotch, a lily's gold heart); `spread` less than 360 makes
a fan (an iris's leaves). 84-510 triangles a bloom, 220-700 a plant (both sides counted).

In the game (index.html buildFlora) the plants grow in clumps over the land (not on the roads), each kind in two
colourings, each colouring a shape with its colours painted into the vertices (tools.js `paintedItemGeometry`, lit by the sun), all of
them in one batched pool (batchpool.js): one object, each flower culled on its own. A picked flower is its copy hidden. The old SDF flowers (flora.js
makeFlower) are gone.

IN THE HAIR: a face's `flower` (1: worn) and `hairFlower` (a bloom's path) put the bloom over the left ear on the hair,
its face turned out (`flowerScale`, .75); a woman wears one a quarter of the time (rose, daisy, hibiscus, frangipani,
poppy, cornflower, lily). The asset viewer's face bar has a `flower` dropdown.


### Dense small items slimmed (2026-11-22)

Small things held in a hand or set on a table that carried far more triangles than their size needs (shut, static
triangles; renders before/after compared at full size, bounds kept within ~1 mm):

| item | tris | parts | what changed |
|---|---|---|---|
| tableware/lekythos | 2944 → 1324 | 11 → 4 | body 24 sides (was 40), profile thinned (Douglas-Peucker 0.8 mm on the rounded curve, propgen `_thin`); inside only to the neck, closed there; foot 16 sides; handle one 6-sided sweep instead of 8 rods |
| tableware/kylix | 3232 → 1624 | 35 → 5 | body and tondo 32 sides; handles one sweep each (were 16 rods each) |
| tableware/hydria | 4160 → 2228 | 31 → 6 | body 28 sides, thinned; inside to the neck; three handles a sweep each |
| tableware/krater | 3456 → 2088 | 27 → 5 | body 32 sides, thinned; handles a sweep each |
| tableware/amphora | 4320 → 2168 | 27 → 5 | body 28 sides, thinned; inside to the neck; handles a sweep each |
| modern/electronics/desk-phone | 2498 → 1472 | 8 | coiled cord 14 turns of 4 points, 4 sides (was 16 x 6, 5 sides; the sweep's seg 1 was clamped to 2 anyway) |
| modern/arms/revolver | 1260 → 1188 | 30 → 20 | flutes one part, chambers one part (`at` lists), cylinder 18 sides |
| tools/caduceus | 4296 → 1608 | 4 | the snakes' sweep `seg` 2 (its path already has 10 points a turn) |
| jewelry/head/laurel-wreath | 2304 → 1448 | 5 | band `step` 10° (was 5); leaves 8 outline points (10), 22 a wreath (26) |
| jewelry/head/flower-chaplet | 2236 → 2020 | 2 | cord `step` 10 only: the blooms are the shared flower assets, already lean |
| jewelry/head/coronet | 1904 → 1240 | 4 | band `step` 10; gems `small` (6 sides, two-step dome) |
| jewelry/head/circlet | 1584 → 864 | 7 | band `step` 10; gems `small` |

Generators: tools/propgen.py (`_greek`, `_thin`, `_well`, `_handle`), tools/attributegen.py, tools/modern/electronics.py,
tools/modern/arms.py, tools/jewelgen.py (`gem(..., small=True)`, the band's `step`).

### In-game budget (2026-11-22)

Ranked by what the GAME draws, not by the file: triangles of an item's static shut build times the copies a world
places. Measured in five game loads (`?menu=0&period=` medieval, roman, industrial, japanese, maya) by walking the
scene after load: `architecture.js itemBudget(scene, camera?)` sums every drawn mesh's triangles by the item they
came from. The hook: items.js gives each built group a non-enumerable `src` (its path: no copy or comparison of the
arrays sees it); `itemGeometry`, the merged furniture of a building (`itemMeshes`), tools.js `paintedGeometry` and
merge.js's joins carry `geometry.userData.items` { path: triangles }, a batched pool its shapes (`userData.geos`).
From the console: `(await import("./architecture.js")).itemBudget(__dbg.scene, __dbg.camera)`.

Top of the ranking before (mean scene triangles over the five loads; copies = scene / one build):

| # | item | scene tris | one build | copies |
|---|---|---|---|---|
| 1 | mushrooms/amanita | 184 722 | 991 | ~186 |
| 2 | faces/man | 137 645 | (game face) | ~30 |
| 3 | faces/woman | 126 015 | (game face) | ~15 |
| 4 | mushrooms/chanterelle | 67 896 | 360 | ~189 |
| 5 | mushrooms/boletus | 62 986 | 339 | ~186 |
| 6 | tableware/cauldron (hearth chain) | 47 552 | 3774 | ~13 a world, 30 in a medieval town |
| 7 | food/cabbage-head | 30 822 | 172 | ~179 |
| 8 | faces/child | 19 360 | (game face) | ~3 |
| 9 | furniture/cask | 16 845 | 448 | ~38 |
| 10 | furniture/roman-table | 16 184 | 2348 | ~7 (34 in a Roman town) |
| 11 | tools/straw-bale | 13 997 | 2592 | ~5 (27 in a Japanese one) |
| 12 | furniture/roman-couch | 13 464 | 792 | ~17 |
| 13 | tools/frog-lamp | 13 170 | 878 | ~15 (the mine) |
| 14 | furniture/settle | 11 713 | 484 | ~24 |
| 15 | furniture/chest-of-drawers | 11 704 | 3080 | ~4 |
| 16 | stall wares (the market's, index.html) | 10 964 | | 1 |
| 17 | tools/sack | 10 398 | 776 | ~13 |
| 18 | furniture/bedstead | 9 623 | 460 | ~21 |
| 19 | furniture/market-stall | 8 312 | 756 | ~11 |
| 20 | tools/sack-standing | 6 674 | 776 | ~9 |

What changed (one build's triangles; everything else builds identically, fold4/geo4):

| item | tris | what changed |
|---|---|---|
| mushrooms/amanita | 991 → 599 | warts five-sided low domes (a lathe, 20 tris) for squashed spheres (36, half under the cap); cap and gills one-sided (the cap closes over the gills) |
| mushrooms/boletus | 339 → 219 | cap and pores one-sided |
| mushrooms/chanterelle | 360 → 252 | the stem one-sided, only the cap a two-sided shell; the foot's disc and the dip's last ring gone |
| tableware/cauldron | 3774 → 2606 (on the hearth's chain; 1194 → 1146 on legs) | chain links a diamond section round 8 sides (64 tris, were 120); ears 8 sides (craftgen `ring(..., sec=4)`) |
| tools/straw-bale | 2592 → 864 | the three ropes hexagonal-section lathes, 16 round (the `ring` primitive made 768 each) |
| tools/hamper | 2086 → 886 | lashings lathes on the body's own 14 corners; cord ends and the lid's cross cord `seg` 1 and 2 |
| tools/sack (and sack-standing) | 776 → 384 | the neck cord a 10-sided hexagonal lathe (was a 512-tri `ring`) |
| components/ring-pull | 352 → 160 | the ring a hexagonal lathe of 10 sides: chest of drawers 3080 → 1544, bureau 3104 → 1568, armoire 2516 → 2132 |
| furniture/roman-table | 2348 → 1884 | the stretcher ring a hexagonal lathe of 20 sides |
| furniture/plank-chest | 1436 → 536 | the folded linen `inside` (seen only open) |
| tools/frog-lamp | 878 → 608 | bowl and lid 10 sides, hanger sweep `seg` 3, swivel 8 sides |
| components/cart-* | their loads 6..12 follow the hamper, bales and sacks |

Savings: the changed items drew 460k triangles a world on average (five loads), 291k after (-37 %); in view at a
town's market, church, houses and landing 158k → 101k. Medieval: 494k → 327k scene, 183k → 129k in view; Japanese
458k → 261k and 168k → 79k. Whole-scene totals swing by far more from load to load (how many people are about, which
landmarks the world drew), so the item sums are the comparison. Generators: tools/mushroomgen.py (`wart`),
tools/craftgen.py (`ring` `sec`), tools/propgen.py (`cord_ring`); ring-pull, roman-table and plank-chest by hand.

### Far heads, cheaper rings, three field items (2026-11-22)

- **Far heads** (heads.js `FAR`, docs/face.md "Far heads"): past 10 m (near again inside 8) a head is drawn from its
  `detail` .7 shape, about half (a man 4014 → 1776, a woman 4250 → 2012), built in a worker (faceworker.js) or taken
  from pregen/, into indexed pools of their own. Near faces are byte-identical (geo4).
- **`ring`** gained `smooth: false` (its stations as given, not a sweep smoothed to twice as many) and `stations`;
  without them nothing changes. Converted, the ring parts' triangles: sampan hoop 3072 → 1152, reed-boat lashing
  4608 → 1152, flail links 2808 → 576, pithos bands and lugs 2496 → 672, storage-jar 1304 → 408, outrigger lashing
  1088 → 288, bucket 960 → 384, spinning-wheel rim 768 → 288, strongbox handles 672 → 240, anchor 672 → 144, wreath
  456 → 192, patera 432 → 288, cornucopia 384 → 192, crossbow stirrup 360 → 120, lantern 336 → 100, threshing-flail
  312 → 80 (and the carts, the Maya canoe and the ships that `use` the jar or the anchor with them). Generators edited
  to match (shipgen, propgen, attributegen), not re-run.
- **`lathe` `caps`** takes `"top"` / `"bottom"` for one cap only. **cask** 448 → 336 (one-sided staves, a chime band
  inside the top, the head capped on top only); **settle** 484 → 268 (its panel-doors without knobs, `knob: 0`);
  **cabbage-head** 172 → 138 (the head a three-band dome, not a ball half sunk in the cup; the cup's bottom band
  one-sided).
- Budget (seed 7, items in the whole scene; then the mean in view over four headings at each spot):

  | period | scene total | items | faces | in view (market / church or house / landing) |
  |---|---|---|---|---|
  | medieval | 2.957M → 2.658M | 1.098M → 0.833M | 537k → 300k | 1.505M → 1.424M, 1.473M → 1.408M, 1.433M → 1.334M |
  | roman | 2.828M → 2.520M | 1.177M → 0.877M | 669k → 378k | 1.424M → 1.335M, 1.462M → 1.371M, 1.534M → 1.431M |
  | japanese | 1.691M → 1.652M | 426k → 388k | 75k → 48k | 769k → 756k, 774k → 762k, 904k → 873k |

  Frame times (medieval, headless, ~30 fps): the walk unchanged within the runs' spread; the first ~5 s after the
  world is ready a little rougher while the worker builds the 170 far shapes (it shares four cores with the game).
  Re-running build/pregen.py records them (and the near faces, whose section is stale: 171 builds, ~4 s of main
  thread at every load).

Next: re-run build/pregen.py (done 2026-11-22, docs/pregen.md); the jewellery and hair at distance (they ride the face's detail already); the cart and
ship hulls (done 2026-11-22, below); `ring` defaults could follow the opt-in once every user is seen.

### Hulls, the amphora, flat shields (2026-11-22)

Ranked over three game loads by the budget hook (seed 7, `&water=sea` so each has a harbour: medieval, roman,
japanese), the ships and carts drew: medieval knarr 21.9k, cog 5.5k, carts 4.4k; roman transport amphorae 59.7k (82 on
the quay and in holds), gaulos 49.4k, freight wagon 17.0k, roman merchantman 15.6k, trireme 8.3k, the other carts
12.4k; japanese freight wagon 15.8k (rice bales), bezaisen 14.7k, sampan 3.7k. No boat is boarded or sailed by the
player (harbour.js moves the ships, index.html rows the fisherman's boat), so nothing is held at close-up quality
beyond what the quay shows. What a hull's triangles went to (knarr): the skin 784 doubled, the two rails 1368 (a
6-sided round sweep along a spline through 28 stations, at two steps a station), ten ribs 2320, the keel beam 488 --
and `double` turned ALL of it, rails, ribs and keel included. So:

- **`hull` `lean`** (items.js; shipgen.py puts it on every hull it writes): the rail, keel beam and ribs go through
  the stations themselves, and a `double` hull's back is its skin's alone. (The keel beam starting straight down its
  sternpost then had an `up` along its first tangent: items.js `sweep` takes another axis where `up` has no part
  across the tangent -- before, the section fell flat; nothing built before changes, geo4.)
- **Flat shields** (items.js `shield`: no `bend`, no `dish`) are one fan in from the rim instead of eight rings -- the
  uv is the plane's, the painting the same: a round shield 1172 → 500, a longship's or a dromon's `shield-row` 23440 →
  10000.
- **transport-amphora** (propgen.py): 12 sides for 14, the handles 3 steps a span round 6 -- 1456 → 974.

One build (seed 1): knarr 10928 → 4672, gaulos 24760 → 17100, longship 45960 → 20364, dromon 29676 → 15324, fishing-boat
7448 → 3044, skiff 4756 → 1808, umiak 7048 → 2548, birchbark canoe 8216 → 2748, coracle 5224 → 1964, gondola 4918 →
2626, sampan 3668 → 2416, decked hulls ~900 less each (cog 5752 → 4840, roman merchantman 5444 → 4532, bezaisen 5048 →
4376); freight wagon with amphorae (load 6) 24972 → 16778, load 7 17004 → 11702. geo4: those 46 items, nothing else.

In the scene (same loads): medieval ships and carts 32.0k → 18.6k (knarr 21.9k → 9.4k); roman 165.5k → 117.6k
(amphorae 59.7k → 39.9k, gaulos 49.4k → 34.1k, wagon 17.0k → 11.7k), scene 2.746M → 2.699M, in view 20-28k less at
each spot; japanese 45.7k → 42.4k (bezaisen 14.7k → 12.7k, sampan 3.7k → 2.4k; the rice-bale wagon unchanged).
Renders: assets viewer close and at ~2.4 x the item's size, and in game at a harbour (the Phoenician merchantman,
the knarr) at 16 and 40 m -- no difference seen.

The generators re-run (shipgen.py, propgen.py, attributegen.py) wrote the same content as the JSON but for key
order -- the hull's `smooth`, `stations`, `sides` came before `at` where the files have them last -- and
attributegen.py dropping index.json's final newline; both fixed in the generators, and before the trims all three
gave the files back byte for byte (`diff -r`). After them only ships/*.json (40) and tools/transport-amphora.json
differ, as above.

Next: the rice-bale load (18 tawara at 864, 15.8k in a Japanese town: their rope lathes 6 sided, 576 of each);
cart-wheel (328 each, 12-24 drawn in a town); the harbour builds each ship twice (moored and going) and hides one -- only the
drawn one counts here, but both are uploaded.

### Cheap items reworked (2026-11-21)

- **Beach ball** (2026-11-22): six smooth `arc` lathe gores, one per colour, instead of twelve flat strips over a core sphere (1824 → 1008 tris). **Toilet**: the lid's outline fitted to the seat ring (it was mirrored 9 cm aft) and it stops at 88°, against the cistern. **Trumpet**: each valve one lathe (bottom, casing, cap) instead of three rods (2194 → 2080).
- **furniture/sofa** is now the Louis XV canapé. It stands on the fauteuil by `use` and only says what differs: the
  params (w 2.0, d .72, the back's height) and the `legs` part, with two more legs under the middle (parts merge by
  id, see defs.js). It replaces the four bare boxes it was.
- **furniture/fauteuil**'s seat rail is a closed spline through ten points round a serpentine rounded rectangle. The
  five it had looped out at the corners once the chair was drawn wide.
- **furniture/divan** gained a round bolster at each end, and the cushion's cloth hanging over the platform's front
  with its fringe.

- **crate** (tools/propgen.py): three side and end boards a face with gaps onto a dark inside box, three lid
  boards, corner battens and end cleats instead of one box with bands; 288 tris; outer size kept (0.8 x 0.5 x 0.55).
- **sack** (propgen): one turned profile (belly, gathered waist, tied-off ear) laid along +x and `stretch`ed flat
  under its weight, a cord ring round the neck, instead of two stretched spheres; same footprint, hold and
  `sack-standing` contract.
- **book** (hand JSON): two boards, a round spine with three raised bands, the page block, the clasps -- spine at
  -x where the hold grips it.
- **drawers everywhere**: `components/drawer` is now a `slide` carrying its tray (`depth`, the tray `inside`), so
  the chest of drawers, bureau, dresser, armoire, workbench and kitchen table open with `open` (docs/modern.md,
  "Joints in components"); the game's static shut build leaves the trays out.
  (2026-11-22) It is the ONE drawer: `front` "joinery" (its own front, knobs or ring pulls -- the default) or "slab"
  (modern/components/slab-door, `t` thick from `back`), the tray's `floor`, `lift`, `wall`, `rise` (of h), `gap`,
  `travel` (of the depth), role `tray` (the wood unless the use names it), `stock` (two packs, roles goods, goods2).
  The modern kitchen's and desk's drawers, the fridge-freezer's freezer drawers and (2026-11-22, `stock` "sheet": a
  baking sheet, role goods) the cooker's storage drawer place it; and (2026-11-22, `stock` "powder": two dividers,
  role tray, and the powder, role goods) the washing machine's detergent drawer; and (2026-11-22, `stock` "veg":
  three heads of veg, role goods, two tomatoes, role goods2) the fridge's crisper. A slab front's `stand`, `r`,
  `sides`, `pr`, `psides` and `inset` go on to its bar handle (the cooker's: 25 mm, 7 mm, 10; posts r 5.6 mm, 8
  sides, 15 mm in -- the oven door's kind), `gh` and `gd` size its moulded grip (20 mm high, 7 mm proud; the washing
  machine's 12, 2.5), and `frame` makes it a shaker front (docs/modern.md, "Shaker fronts").
- **plank-chest, gothic-chest**: hollow (floor and walls between the ends / inside the posts and panels), folded
  linen inside, the lid -- with the plank chest's straps and hasp -- a hinge at the back edge (`open`).
- **armoire, cupboard**: `components/panel-door` takes `swing` 1 -- the same parts in a hinge at the edge away
  from its knob (`side`), `max` -105 x side -- so a pair is ONE door part mirrored in x. Both cases are hollow: the
  armoire has linen shelves on the left, coats on a rail on the right and a centre muntin over the doors' meeting
  gap; the cupboard has bowls on one shelf and pewter plates (pitched 75, stood against the back) and a jug on the
  other. The other eight panel-door users keep `swing` 0, fixed. (2026-11-22) `anchor`: 1 (the default) its face at
  z 0, 0 its back at z 0 -- the way modern/components/slab-door stands, which takes the same param (default 0);
  docs/modern.md, "Which way a door stands". `knob` 0 leaves its knob off -- slab-door's shaker front (`frame`)
  places panel-door so, with its own pull. (2026-11-22) The panel is role `panel`, `"panel": "wood"` in its own
  materials, so it is the frame's wood unless the user names it: a shaker front's panel a shade darker (the modern
  kitchen's colourways). A user's own role called `panel` reaches it too (roles go down by name).
- **folding-screen**: was six boxes posed at fixed places (its `n` ignored); now a chain of nested hinges, each
  leaf on the one before, their `open` bound to the `fold` param (a hinge's `open` may name a param): the first
  leaf turned fold x 80, each after it back and forth by twice that, so `n` (to 8) leaves zigzag about a line --
  0.25 as it stands, 0 flat, 1 packed up.
- **Openings, 2026-11-22.** These all open with `open`, and their contents are `inside`, so the static shut build
  barely grows.
  - **crate** (propgen): the inside box is now a floor and liners. The lid is hinged at the back edge (105°) over
    straw, nine bottles and two stoneware jugs.
  - **hamper** (propgen): the lid and its cross cord are hinged at the back over grain, apples and a cloth. The
    lashing rings and cord ends stay on the body.
  - **cooking-pot** (craftgen2): each style's lid is hinged about z at the rim, away from the handle (75°). The
    stew under a lid is `inside`.
  - **chinese-cabinet:** the faceted case is an open arc behind the doors, with an inner lining, a front frame
    and a central stile. The doors are one `panel-door` hinge mirrored in x, each with its half of the face plate.
    Inside: a shelf with bound books, cloth wrappers, scrolls and a porcelain jar.
  - **longcase-clock:** the trunk is boards round the door, which is a `panel-door` with `swing` 1. Inside: the
    pendulum rod and bob, and two weights on cords with pulleys.
  - **cassone:** the body lathe is open with a rimmed lining lathe. Both steps of the lid are hinged at the back
    (105°) over linen, a bolt of brocade and a gilt casket.
  - **sarcophagus:** the set-on lid (`lid` 1) is a slide over [0, .15] that lifts it 5 cm. A nested slide over
    [.15, 1] pushes it .8 m along and .45 m across. Inside is a gilded mummy-case with its face and a blue band:
    `inside` under lid 1, and plain when the lid lies aside (`lid` 2). The old gold `rim`, a solid slab across the
    mouth, is now a band of four strips round the outside.
  - **harpsichord:** the case is a keyhole `plate` (the outline, then the inner outline reversed), with a bottom,
    the soundboard and the wrestplank. The lid is hinged along the straight spine (55°, over [0, .7]). Its stick
    rises on its own hinge over [.7, 1]. Inside: fourteen strings stopping at the bentside, the bridge and a gilt
    rose. The plates turn +90 now, so the spine is at -z where the legs were set out for it; the middle bentside
    leg moved in to z 0.
  - **gate-leg-table:** the top is a fixed centre strip and two leaves, each hinged at the strip's edge (z ±.21).
    Each gate is a leg, two rails and a stile, pivoting on the stile at z ±.15. `open` (default 1, spread)
    raises the leaves over [0, .5], then swings the gates out under them over [.5, 1]. The leaf goes first
    because, while it hangs, it stands in the gate's path. At 0 the leaves hang and the gates lie folded along
    the frame.
