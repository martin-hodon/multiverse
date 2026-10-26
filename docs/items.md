# Items: what a hand holds and what a room is furnished with

A sword, a shield, a scythe, a lute, a chair, a four-poster are all **definitions** (`assets/items/**.json`), built
into triangles by one module, `items.js`, wherever they are drawn: the asset viewer, the tools and arms in people's
hands (`tools.js`), and the furniture in a building (`arch/assemble.js` `item` parts, drawn by `architecture.js`).
Nothing in `items.js` touches three. Out come plain arrays, one set per **material**, and the materials are named
(oak, walnut, iron, leather, rush, damask...) and textured from the pattern library (docs/patterns.md).

Everything is up to about 1800: no upholstered sofas, no revolvers. The catalogue has 56 weapons, 12 shields,
28 tools, 48 pieces of furniture, 30 ships, 43 components, one kit and 63 materials, and every one is seen in `assets.html`.

| folder | what |
|---|---|
| `weapons/` | swords (arming sword, gladius, xiphos, spatha, viking, longsword, claymore, zweihander, falchion, sabre, rapier, smallsword, shamshir, katana, jian, dao), daggers (rondel, seax, dirk, pugio, tanto, stiletto), axes (bearded, dane, francisca, battle), polearms (spear, winged spear, dory, pike, sarissa, halberd, glaive, bill, partisan, poleaxe, guandao, naginata, pilum, javelin), blunt (mace, flanged mace, morning star, war hammer, club, quarterstaff, flail), bows, a crossbow, a musket, a pistol |
| `shields/` | heater, round, kite, scutum, aspis, buckler, targe, pavise, oval, rattan, dhal -- their faces heraldic |
| `tools/` | the village's tools (scythe, spade, hoe, hammer, saw, cleaver, fishing rod, lute...) and things carried (lantern, torch, book, bucket, basket, pitcher, candlestick) |
| `furniture/` | seats (stools, benches, settle, chairs from the klismos and curule to the Windsor and the fauteuil, thrones), tables, beds (pallet, bedstead, box bed, four-poster, Chinese bed, Roman couch, cradle), storage (chests, cassone, cask, cupboard, armoire, dresser, bureau, bookcase), and the rest (lectern, harpsichord, spinning wheel, longcase clock, screen, mirror) |
| `components/` | the reusable pieces: grip, pommel, crossguard, boss, axe head, spearhead, polearm head, blunt head, turned / square / cabriole leg, bun and bracket feet, finial, knob, ring pull, drawer, panel door, spindle, cushion, strap, rocker |
| `ships/` | 30 vessels up to 1800 (`tools/shipgen.py` writes them): dugout, reed boat, Egyptian river boat, trireme, Roman merchantman, longship, knarr, cog, carrack, caravel, galleon, galley, dhow, junk, sampan, outrigger canoe, voyaging canoe, gondola, birchbark canoe, kayak, umiak, coracle, fishing boat, skiff, fluyt, xebec, felucca, ship of the line, frigate, East Indiaman |
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
  `along` (n copies from..to), `around` (a ring: `plane` "xz" for legs and flanges turned to face out, "xy" for
  studs round a shield), `mirror: "x"`, `stretch` (drawn out along the parent's axes, after turning), `scale`, and
  gated by `when` (a param, a list, or `{ param: word | [words] }`). `double: true` draws a thin shell from both sides.

| type | what |
|---|---|
| `lathe` | a profile `[[r, y], ...]` turned about y (`sides`, `caps`, `faceted` for a square leg) |
| `rod` | from..to, radius `r` (or `r0`..`r1`) |
| `sphere`, `box` | `r`; `size` [x, y, z] with `round` |
| `sweep` | a tube along a path (`r` or a list of radii, or a rectangular `section` with its `up`); `closed` |
| `ring` | a torus: `r`, `tube` |
| `blade` | `length`, `width` stations, `thick` [base, tip], one or two `edges`, `flat`, `curve` |
| `plate` | an outline extruded `thick` (or tapered) |
| `hull` | a ship's hull lofted along +x from its lines (see Ships) |
| `sail` | a cloth between four `corners`, bellied, with `battens` |
| `face` | a low-poly head on the anatomy (see Faces) |
| `hair` | strands grown from that head's scalp (see Hair) |
| `feathers` | a fan of feathers, each its own vane, seen from both sides (see Birds) |
| `petals` | a whorl of curved blades round the part's y axis, seen from both sides -- a flower's petals and sepals, a leaf or two (see Flowers): `n`, `layers`, `length`, `width`, `cup`, `curl`, `cupped`, `shape`, `throat` / `band` |
| `shield` | a shaped board (`shape`: round, oval, kite, heater, rect), bent and dished, a rim band, a back, a face whose heraldry is fitted to it |
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
  detail (scaled by `detail`).
- **`sail`** is a cloth between four `corners` in its plane (three make a lateen or a crab claw), `belly` out along
  +z, seen from both sides, with `battens` across it for a junk. A square sail is turned across the ship by its
  parent (yaw 90); a lateen, a junk sail and a spanker hang fore and aft.

The rigging and fittings are components (`components/`): `mast` (`top`: topmast or crow's nest), `yard`,
`square-sail` (`set` full or furled), `lateen-sail` (`tilt`), `junk-sail`, `crab-claw-sail`, `oar` and a bank of
`oars` (both sides), `steering-oar`, `rudder` (stern-hung, with its tiller), `figurehead` (dragon, swan, scroll,
lion), `castle` (a fore- or aftcastle on posts, crenellated or not), `cabin` (a deckhouse with windows), `awning`,
`outrigger`, `anchor`, `cannon`, `gun-row` (a broadside of ports and muzzles), `ram`, `shield-row` (round shields
along the gunwales), `bowsprit`. A stay is a thin `rod`. The materials added: `planks`, `planks-pine`,
`planks-grey`, `planks-tarred`, `deck`, `sail-striped`, `sail-tan`, `matting`, `reed`, `bamboo`, `cedar`, `hide`.

Every vessel has a range of sizes (`L`), its era and region, and a `set` drawn by its seed (most sails full, some
furled). They were checked as flat paintings from the side, above and the quarter, all thirty at once, every
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
  (a tonsure). Strand groups with `edge: true` hang from that edge (one a column, `extra` between) instead of
  growing all over the scalp -- a bob, long hair, the curls -- so the sides and back read as a rounded head of hair,
  not a sheet of ribbons.

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

Birds (`birds/*.json`, `tools/birdgen.py`, "Items: birds": 27 from the sparrow to the swan, the peacock, the
eagle) with FEATHERED WINGS AND TAILS: the part type `feathers` (`feathers.js`) lays a fan of feathers in the part's
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
flapping, barring and eye spots as patterns rather than paint.

## Props (2026-10-02)

What the world carries and moves, out of the code that built it (`tools/propgen.py`): `tools/sack`, `furniture/cask`
for the freight's and the carts' barrels, `components/water-wheel` (turned about z by the current), `components/
windmill-sails` (four `windmill-arm`s, turned by the wind), `ships/barge` (its ten cargo places `hold` markers, the
gangplank's foot a `plank` marker; `deckY`, `halfL`, `halfW` its params) and `components/gangplank`, `components/
cart-wheel` (r, n spokes) and the three cart bodies `components/cart-small|medium|large` (their `load` 0..4: casks
lying in chocked pyramids, standing casks, kegs, sacks in two courses; 5 the harvest's sheaves heaped, `tools/sheaf`,
never drawn on the road -- index.html CHORES; their bed, floor and axles in their params,
which carts.js reads its sizes from), `weapons/arrow`, and `food/fish` for the fisherman's catch -- and for the
season's chores (2026-10-23) `furniture/woodpile` (a chopping block with a round on it, the split billets stacked beside
at +x) and `components/ice-hole` (dark water in a round cut, slush and broken ice about it). Not generated:
`furniture/stall-season`, the market's greengrocer's and fruiterer's wares by `wares` and `season` (index.html builds
each season's once and shows the world's). The game builds
them through `architecture.js itemGroup` (one group) and `itemInstanced` (copies: the same root / set / commit API
as the parts-list helpers), and the arrow as one painted geometry (`tools.js paintedGeometry`, which the faces use
too). Each counter placement is a little heap of three and each basket holds one more (2026-10-24: two or three pods on a
2.4 m counter read as bare; 49 -> 133 pieces).

**Alternatives** (the same day, later): the pieces the code still drew its own way are items too, BESIDE the
catalogue's finer ones rather than instead of them -- `ships/fisher-boat` (the fisherman's rowing boat; `ships/skiff`
stays), `components/fisher-oar` (`side`), `tools/fishing-pole` (beside `tools/fishing-rod`), `components/fishing-line`
(1.8 m from the rod's tip; the game stretches it to the water), `furniture/barrel` (`h`, `belly`, `head`: a big barrel
or a keg; beside `furniture/cask`) and `barrel-on-side`, `tools/sack-standing`, `components/meal-chute`,
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
| `rest` | `"ground"`: at rest it stands on its butt on the ground, and the hand slides along it (a spear, a halberd, an ordered musket); `"body"`: it rests against the body where the hand holds it on the whole, the hand playing over it (a lute: tools.js BODY_REST) |

`holdMatrix(hold)` turns that into the one matrix that puts the item into any hand. `tools.js` moves each kind of item
into the hand's frame once, at build, as one InstancedMesh per material. Each frame, every copy is one matrix at a
person's hand, read from the posed skeleton. A person's `tool` is the old name (`"scythe"`, `"sword"`: `TOOL_ITEMS`),
an item's path, or either with `#seed` for one of its kind (`"items/shields/heater#3"`).

**Kits** (`kits/guard.json`) are loadouts by weight, each with a `main` (the weapon hand) and an `off` (the other: a
shield), each an item or a pick. `items.js pickKit(kit, seed)` draws one for a person, and one of `variants` of each
item, so a watch of a dozen carries a dozen weapons from only a few distinct meshes. The town's guards are armed this
way (index.html).

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

