# The world

## Cultural periods (2026-10-09)

A world is set in one PERIOD, decided at startup (`?period=NAME`, else drawn from the seed by weight):
greek, roman, egyptian, chinese, medieval, byzantine, ottoman, islamic, industrial. Everything with a time and
place follows it, all declared in `assets/world/periods.json`: the monuments (`landmarks`, from architecture.js
LANDMARKS), what people wear (`dress`: wardrobe styles by weight, `""` the village's own -- each style brings its
hair and jewelry), the town (`town.styles`: a medieval town style; or `town.houses`: the period's dwellings in the
street rows, at the inn and on the farms; `church`, `walls` [pattern, palette], `without` farm plots such as the
windmill), the fisherman's boat, the trees (flora.js species; the palm is a warm one, never in the wild mix) and the
`ground` -- `grounds` gives its colours into grass.js GRADE, whether blades grow on it (sand: none, no fringe) and how
many flowers it keeps. `?townstyle=` still forces a town style.

## The grown map (2026-09-28)

By default the land is GROWN at load (`mapgen.js`): the terrain lab (`terrain_lab.js`, docs/terrain_lab.md) runs its
"river country" preset -- 2.6 km at 20 m cells, a big river (10 m³/s) coming in from beyond the region and cutting
down through a layer cake with a basalt sill in it as the land rises, its side streams, its falls -- for 150,000
years on the renderer's own GPU device, and the world is a window cut out of it. `?map=0` keeps the old world below
(the sines, the lake, three landmarks); `?trees=0` scenes have no room for a map and keep it too; `?mapyears=`
grows a shorter history (the headless checks: a software GPU takes minutes).

- **The window**: the world's size (2 x groundR and a margin), along the big river where its banks, the herd's
  meadow and the facade line are gentlest, turned so the river runs east (+x) about `extent + 120` south of the
  middle -- where the old river ran -- so the town, the landing, the mill and the barge still find a river running
  east along `z = riverZ(x)`. The big river (and each side stream) is found as water finds its way: from where it
  comes in, on each time to the lowest cell beside those reached -- filling a hollow until it spills -- to the
  preset's outlet (a stream: to one already drawn, or the edge). (2026-10-23: it followed the lab's discharge
  before, and three of the four cached lands lost their river in a hollow the lab's last fill had left in its bed --
  the lab's water stops there too -- so their worlds fell back to the old ground.)
- **The ground**: the lab's, bicubic onto a 2 m grid with a little detail, then SETTLED -- the land shifted so the
  river stands at the old -2.2 m at the bridge, and eased (a smooth warp ~110 m wide) so the town, its farms, the
  meadow and the monument's stretch stand at 0. Everything built is laid out on 0 and stays there; the land round it
  rises and falls. Plots are levelled toward 0 as before, but never under water (`wet`).
- **The water has no one level any more.** Every channel -- the big river and each side stream with water enough
  (a brook, 0.016 m³/s) -- is carved at ITS OWN level, falling downstream, never rising: the bed under it, a low bank
  raised above it where the land is lower. The lakes the lab held keep their levels, the moats the old one. The
  water is one mesh over the wet samples of the grid, each vertex at its water's height (and a ring round it, sunk
  under the banks, so the shore is where the land rises through it); `river` on it says how much flows (the waves
  slide downstream there), `fall` how steep it is (white water down a fall). The grass's mask reads the same
  surface as a texture (grass.js `WATER_LEVEL`). `waterY(x, z)` (ground.js) is the surface anywhere (-Infinity:
  dry) and `riverLevel(x)` the river's: swimmers, fish, birds, the barge, the rowing boat, arrows, a struck
  animal, the swimming player and the underwater view all ask them. The reflection's plane follows the river's
  level under the camera.
- **The town** goes where both banks are flattest and the river quiet (falling 2.5 m at most past it, the banks
  about 2.2 m over the water: a terrace over a gorge would be cut down to it): the bridge there, the town south of
  it, the farms and the mill north and 95 m down. And the river runs PAST it (2026-10-23): along the town and the farms
  it bends no more than `SWING` (6 m) north or south of where it passes the bridge -- the town is laid out as though it
  ran straight on, and a grown river's bend into it stood a gatehouse or a house over the channel, its plot unlevelled.
- **ONE landmark, the monument**, on the facade line where it is flattest; the highway along it reaches the
  meadow's path at x = 0 wherever it stands.

The lab is deterministic on one machine (every pass reads one state and writes another), so a seed grows the same
land every time there. Different GPUs may round differently, so peers of one session on different hardware can
grow different maps -- a shared session would have to send the host's.

## Terrain and layout (the old world, `?map=0`)

Ground height is an analytic function: three layered sines, blended flat
(smoothstep over 20m) under every building footprint, the herd meadow, and
the lake's surroundings. **There is one water level for the whole world**
(-2.2m): the plain is held softly above it (a smooth floor at -1.4m), and
only what is deliberately carved fills with water -- the lake (a bowl
5.5m deep), the river (a 16m groove 4.4m deep), the castle moat. One
translucent water sheet at that level covers the whole ground; it shows
wherever terrain dips below it and hides under the plain elsewhere. The
rendered ground is a 400x400 plane displaced by the same function (cells
~4m in the full town, so the river groove survives sampling),
vertex-colored by elevation (lush valleys → dry crests) with faint contour
bands, plus a per-pixel grass overlay (blade flecks + tone patches)
injected into the toon material. Because mesh interpolation can sit a hair
above the analytic surface, walkers stand 4cm proud and paths float 12cm.

The **river** meanders in from the west edge (a sine of 12m amplitude) and
flows east into the lake's west arm, fading into the lake bowl over its
last 25m. Flow is in the water shader: inside the river band the whole
wave pattern slides downstream at 1.6 m/s and fine streaks stretch along
the current; the lake stays still.

Zones: buildings line up along a north road; the fenced nature range holds
animals and people; a smaller fenced pen to the east holds the monsters;
the lake lies south, the river runs into it from the west, and the water
mill stands on the river's north bank (the one building off the facade
row: sites carry an optional `z`). Packed-earth paths (one merged mesh with wheel
ruts, stone specks and a worn grassy verge) connect the road, every building
door, the meadow and the lake.

**Roads cut into the terrain (2026-10-06).** The roads are planned BEFORE the
ground is built (paths.js `planRoads`): each route laid out and kept dry,
sampled every ~1.5 m, its centreline's height following the natural ground
along it (smoothed over ~6 m), pinned where it runs onto a wider road already
laid (a spur meets the street at its height), and LEVEL ACROSS -- both edges
at the centre's height. The ground then adjusts to the road, not the road to
the ground: inside a road `groundH` is the road's surface, and over a 3 m
shoulder beyond its edge it eases back to the land (ground.js `roads`,
`naturalH` the land without them). The terrain is CUT along the roads' edges
(terrain_data.js `roadTileData`): a tile a road or its shoulder touches is
built at its finest level, and each cell a road touches is the cell less the
road -- the square cut by every road piece over it, convex pieces fanned into
triangles; the road's edges are split where they cross the lattice's lines, so
the cut's points ARE the road's points, shared by the road mesh
(buildPathNetwork) and the terrain, at the same heights. No terrain lies under
a road; the skirts skip the stretches of a tile's border a road crosses.
`?roadcut=0` lays the roads over the uncut ground as before (the comparison).
Where a road runs over one laid before it (a door's spur on the street it leaves) its surface sinks up to 3 cm under
that road's, in the mesh only: at one height the two drew over each other, the spur's verge flickering on the street.

The road itself is a 6m **highway** in the Roman manner: two lanes 3.5m
apart, right-hand traffic, running the whole facade line and ending in a
9m-radius turning loop past the last building at each end (the ground
plane is widened to hold them). The closed lane loop is the carts' route,
sampled by arc length so teams bend around the loops.

## Walkability

The FPS controller is a 0.25m circle at eye height 1.5m: wall collision
with sliding, climb ≤ 0.5m (stairs are real 0.25m steps with a 1m landing),
gravity with anti-tunneling landing checks, Space jump (~0.9m of rise, 2026-10-03: was 1.2, so
with the step-up a 1.4m sill is reachable), Shift+Space 10m dash. Every
wall opening is real: doors from the floor, windows between sill and
lintel -- open a window, jump, and you are through it: in the air the body
tucks (collides `duck`: 60cm of gap instead of 1.2m), lands on the sill,
and where only a ducked body fits (`wedged`: on a sill under its lintel) it
ducks on through and down; a closed pane blocks at its own height. Steps
are judged with the feet where they will stand: going down a stair the
headroom is from the lower tread (and a ring sample that meets stone is
asked again from the floor under it). A straight flight's sides and
underside are in the wall field: it is walked up, not through. Support is footprint-aware (five probes) so hairline seams can't
swallow you. Colliders derive automatically from building data — boxes and
closed cylinders over 1.2m tall, `hwall` segments with passable door holes —
plus closed doors and tree trunks. `floorY` fields make every storey,
staircase, bowl and gallery walkable, with headroom cutouts sized for a 2m
walker. The big animals are bodies too: every mount (and anything with a
trunk over .35m) carries one collision circle round its trunk -- cheaper
and steadier than testing every part -- that you cannot walk into, though
you can always walk out of one that has stepped onto you.

## Life

- **Species** (`species.js`): 42 animals with real sizes, mirrored
  symmetry, surface-snapped eyes with real colors, gaits whose cadence
  follows actual travel speed. The 22 mid-to-large mammals (cat, fox, dog,
  wolf, sheep, pig, boar, deer, tiger, lion, cow, ox, zebra, horse, camel,
  bear, hippo, giraffe, elephant, unicorn, centaur, manticore) use the
  mammal rig (`mammals.js`, see architecture.md): two-lobe metaball
  bodies, head and muzzle, two-bone legs with knees and hocks from IK,
  hooves or paws, curved tails (a cat's curl, a pig's corkscrew), and walk
  and run gaits -- walk or run by one Froude rule (`runs()`: every
  wanderer, and a ridden mount at 2.5x its speed, 7x with Shift), head and
  tail on the same stretched gait clock as the legs, a standing
  animal fades its stride out onto straight legs. The small and odd ones
  keep their classic capsule parts (still a trot of diagonal leg pairs);
  monsters (hydra, dragon, manticore, unicorn, beast-men, tauric beasts) with
  jointed bat wings -- all on the rig: the dragon (a long raised neck,
  horns and frill, spines, a sweeping tail with a spade), the hydra (three
  slender necks splaying apart, each an arc chain with its head), the
  beast-men (species.js `beastman`: the human rig with an animal's own
  rig head -- its head sphere and everything hung on it, muzzle, ears,
  eye marks, horns, tusks, fangs -- scaled to a human-sized head, in the
  animal's hide with its tail, hooves for the hoofed, dressed by `outfit`
  -- kilts, tunics, breeches, never headwear; they call as the animal): the minotaur (ox, red-eyed), wolfman, boarman, catman,
  foxman, bearman, ramman, smilodonman; tauric beasts (species.js
  `tauric`: an animal's trunk, legs and tail without its head, neck and
  mane, optionally scaled, with a person's upper body -- makePerson's
  `upper` -- standing on its chest): the centaur (horse), the drider (the
  spider at 25x) and the sphinx (lion); winged people (winged.js, kind
  "winged" in assets/creatures/monsters: makePerson's whole figure with a
  pair of wings from the back of the chest, on a root bone turned up the
  back so the wings spread behind it, chord hanging down, flapping about
  the spine): the angel (mammals.js `birdWing`: primaries rooted ON the
  hand's axis, secondaries along the forearm, coverts over their roots)
  and the demon (`batWing`: the arm to the wrist, three fingers fanned
  from it in the hand's frame, the skin between them scalloped and from
  the last finger back to the flank -- the dragon and the manticore have
  the same wing -- red skin, two horns); two camels, the dromedary and the
  two-humped bactrian; dinosaurs (`dinosaur: true`, in the monster pen)
  on the rig's `biped` option -- the tyrannosaur at real size (12.7m,
  hips at 3.3m, knees folding forward, tiny arms, the tail held out as a
  counterweight) and the triceratops (9.1m: brow and nose horns, a parrot
  beak, the frill as three flat triangles fanned into a shield) -- one
  `ceratopsian()` family: the styracosaurus is its frame at .6 (5.5m) with a
  long nose horn and a crown of frill spikes; the stegosaurus (9.1m: two
  rows of plates, the tail's riding its links, the four-spiked
  thagomizer) and the ankylosaurus (8.2m, twin side lobes for its width,
  scutes, flank spikes, a tail club); all but the stegosaurus
  mountable; riders sit at one shared `saddle(def)` point, a third
  of the way from rump to chest; generative
  butterflies, pond fish, a shark and a dolphin. The small and odd ones:
  a snake whose chained segments carry a travelling wave, rat, wild boar
  with bristle mane and tusks, hedgehog under a coat of spine cones,
  scorpion with pincers and a tail curled over its back, a tarantula-sized
  spider stepping its eight legs in two alternating sets, a peacock whose
  seven-plume train is eyespotted in the shader; on the lake three swans
  and three mallards (`swim`: they ride the shared water level
  half-submerged) and on
  the lagoon's grassy heart a crocodile, a frog, a turtle and a beaver
  with its paddle tail (`shore`).
- **Ranges**: a wanderer's range is a rectangle, or a shape: the lake range
  tests the carved bottom for water and steers home toward the arc, so
  fish, swans and ducks spread over the whole C instead of one belly.
- **Wanderers**: every creature alternates walking and standing at random
  intervals; hoppers (the frog) travel in bursts, airborne on a little
  parabola for each hop and still between. All are
  steered back inside their fence; standers settle legs perfectly
  straight. Fliers cruise at per-individual altitudes and glide instead of
  standing: twenty parrots, fifty owls, twenty eagles, a hundred bats and 140 butterflies
  (`?butterflies=N`) range over the whole sky, spawned across the ground
  (butterflies PERCH, 2026-10-09: at the end of a flight one may make
  for the nearest free flower head within 18m, land on its bloom, fan its
  wings there 4-14s and fly on -- one butterfly a flower; picking the
  flower sends it off; `perchStep`, the flowers' `perches`)
  disc like the people, parrots up to 60m, owls 45m, eagles up to 155m
  -- the cathedral spires (bats swarm low around the buildings they roost
  in, town row and riverside); parrots and eagles fly by day, owls and bats
  only at night (N), roosting out of sight otherwise; swimmers do the same between lake floor and surface. Terrain is
  sampled under nose, center and tail so long bodies never bury a nose.
- **People** (`people.js`, see architecture.md): seeded kind -- man, woman, ten-year-old,
  five-year-old (children with bigger heads and shorter legs; working people are adults) -- height,
  build, skin, face (nose, ears), hair style and a medieval wardrobe: shirts, tunics, dresses,
  kirtle + surcoat, hose, trousers, skirts, hoods, caps, brimmed, pointed and straw hats,
  belts, boots or shoes, aprons, in patterned cloth with trims, pleats and seams. They walk on
  IK knees with counter-swinging arms and settle when they stop; poses —
  standing, sitting (cathedral pews, cart boxes), riding, carrying (a load in both arms), lying. 66 wanderers by default (`?people=N`), spread uniformly over
  the whole open country -- every patch of grass on the ground that is not
  water, moat or a building -- and kept out of those as they roam.
  Cathedrals export `folkSpots` and get a static congregation.
- **Dragonflies** (`makeDragonfly` in `species.js`): 70 generative
  darters, 7-8cm with a 10cm span in four colorings, beating four glassy
  wings fast and low (0.3-2.2m) over water only -- their range is the 5m
  band along the lake's shores and the river; every flier now rides above
  the water surface rather than the carved bed beneath it. A world with a river but no lake has 30 of them along the
  river's banks (index.html DFLY_RIVER; before 2026-10-23 none at all).
- **Animal calls** (`calls.js`, standalone): 35 species have a
  synthesized call -- moo, bleat, grunt, bark, meow, howl, neigh, bray,
  roar, trumpet, cluck, quack, hoot, screech, squawk, croak, hiss, squeak,
  the peacock's scream, the dragon's roar -- each a recipe of notes (a
  buzzing, pulsing, pure or noisy source through a resonance standing in
  for the mouth, with pitch glide, envelope, vibrato, tremolo or
  roughness). What keeps them from sounding like game bleeps is chaos:
  every voiced note carries random pitch jitter and loudness flicker,
  growls pulse at a subharmonic, mouths can glide between two shapes
  (a "mee-ow"), and all calls sound in a light outdoor reverb. No two
  repeats are the same bark: each is a shade higher or lower, shorter or
  longer, its gap uneven; the slow pitch wander and the growl/bleat
  wobble rates drift too. Every recipe carries a measured `level` (make-up
  gain) so all species sound about equally loud at the source (a sheep's
  narrow mouth swallowed 12 dB, a horse's broad one gave 7 back). Every such creature calls now and then within earshot (up
  to ~55m, louder species carry further but are not louder up close --
  a mount is right under the ear -- and all animals sit ~8 dB under the
  people), from where it stands, pitched to its own size. The Colosseum's lions and tigers roar. Mounting an
  animal rouses it; creatures with a voice that cannot be ridden offer
  "click to rouse" when you stand close and look at them.
- **Cobwebs**: some ceiling corners (houses, tavern, mill, castle hall,
  palace wings) carry a web: an inclined triangle with a vertex a little
  way along each of the three edges meeting in the corner, so it really
  spans the corner; one mesh for all of them, spokes and rings from the
  shader, translucent.
- **Speech** (`speech.js`, see architecture.md): every person -- walkers,
  the tavern's company, riders in the saddle, cart drivers on the box, the
  Colosseum's gladiators, the dock hands and the boatman -- has a
  language (English, German, French, Spanish, Russian) drawn from their
  seed and a voice that follows their body -- man, woman, ten-year-old or
  five-year-old, with a seeded pitch jitter -- and a mood per utterance
  (normal, excited, angry: key, pace, how hard the stresses land, how the
  line falls, loudness), and says
  a word -- sometimes a two-word phrase, sometimes a question -- from the
  shared 18-word lexicon every ~30s while you are within
  ~40m -- full within 3m, then about 4 dB per doubling of distance, and
  panned to where they stand. Standing
  within reach of someone and looking at them offers "click to greet
  them": they answer "hello, <word>!" at once, turn to you, and a walker stands still
  for half a minute before wandering on. **L** cycles a
  language override for everyone, **K** a voice override (kid, woman,
  man), **J** pins the word everyone says (random, then each of the 18 in
  turn -- for testing pronunciation), **H** pins a mood; "random" gives
  each their own. The label shows all four.
- **The mine** (2026-10-03; `tools/archgen/mine.py` -> assets/architecture/village/mine.json, finishes mine-silver,
  mine-copper, mine-salt; `?mine=silver|copper|salt` picks, `?mine=0` none): one a world, its ore by the town's seed,
  placed after the town on open land away from every site and the water (its galleries too), where the ground over
  the galleries never dips below -6.5 (they lie 10 m down), the higher the better. The surface: the shaft house over the
  hauling shaft with its windlass (two men at the cranks) and kibbles, the walking shaft with steep flights (25 cm on
  25 cm) under a roof, the spoil heap, the dressing bench, pit timber. Ten metres down: the shaft bottom, two galleries
  with door sets every 1.5 m (none in the salt) and a plank track, carts, stopes with the vein and hewers, oil lamps.
  Its CREW (the spots with `crew: "miner"`) is its own: men in the wardrobe's `miner` outfit (linen smock and hood,
  leather apron), at work day and night with the spot's gesture and tool (index.html crewHerd); village-life leaves those
  spots alone. The ground over the deep galleries stays a floor (`DIG`: only a floor within 4 m of the surface opens
  the ground, and a building's `dig` rectangles -- the shafts' mouths); colliders reach the whole `extent`.
- **The forest** (config.json `forest`, `?forest=N`): one dense wood -- `trees` trees `spacing` (6.6 m, 2026-10-03: was 4.4) apart, thinning
  to an irregular edge `radius` (46 m) across, spruce, pine, oak, birch and maple with an undergrowth of bushes and
  mushrooms -- on the clearest patch of open land nearest the world's middle (away from the sites with a margin for
  their streets, the water and the meadow). Same herd and foliage mesh as the woods: no extra draw calls (+~140k
  triangles in view at 130 trees; 60 now).
- **Contact shadows** (shadows.js, index.html `floorUnder`): a soft dark ellipse on the ground under every figure within
  60 m (the 160 nearest) -- people, animals, riders, the carts' teams, and the carts' beds by their own footprint
  (`bodies`: halfL, halfW, yaw) -- along its heading, as wide as its bones spread plus a body's
  flesh and the shade past its feet (composite.js now keeps each drawn figure's lowest point and spread: an._y0, _fx,
  _fz). On the floor or the ground under it (supportAt, but never a cellar's floor deep under the ground; looked up
  again only when the figure has moved 15 cm), lifted 10 cm and pulled nearer in depth than the roads' paving; none
  for what is off the floor (a bird in the air, a swimmer) -- fainter the higher a figure is off it (the child on the swing,
  a leap: gone at .6 m). One mesh, one draw, placed on the CPU. PITFALLS found on
  the way: a per-frame geometry draw range was not honoured here (unused quads are folded out of sight instead); a
  figure's `_out` is the LAST render pass's culling (a reflection's), not the main view's; and darkening blends in
  linear light, so a shadow needs ~.6 to read at all on screen.
  The trees cast the same soft shade, round, under each crown (shadows.js `createShadeBlobs`, built with the flora in
  buildFlora: as wide as the crown reaches -- flora.js makeTree `crown`, where nine leaves in ten lie -- at half the
  strength, the light coming through the leaves; ~130 of them, one static mesh, one draw).
  In autumn the same mesh carries LEAF LITTER under every broadleaf crown (index.html LITTER, flora.js makeTree
  `evergreen`/`autumnC`): a patch .85 of the crown's reach in the tree's own autumn colour browned a third toward russet,
  as strong as the autumn is far on, drawn as scattered leaves (shadows.js `blobT`: in two offset world grids a leaf a
  cell, its centre jittered, turned its own way, twice as long as wide, each its own shade). index.html `treeCol` is
  now the one place a tree is recorded in treeCols.
  And the buildings: a soft band 1.5 m wide round the foot of every building's walls, darkest at the wall
  (shadows.js `createWallShade`, from the sites' footprints -- not the fields, yards, market paving, fountain, landing
  or bridge -- in pieces of 4 m following the ground; ~900 quads, one static mesh, one draw). `?shadows=0`: none of it. Not round a ROUND building (the windmill, the wall's towers): its footprint's square showed as a dark square round it (2026-10-24).
- **Haycocks** (index.html HAY, `?hay=0`): in summer the meadows round the farm fields are mown and the hay stands in
  nine cocks to dry -- a rounded cone each (three balls stacked round a pole, blocks.js, in the straw's shades), 10-34 m
  from a field on open level ground, clear of the lanes, the sites, the hedges, the river and the children's green.
  One mesh, shown in summer only (I).
- **Coming and going out of sight** (index.html `outToPlay`, `unseen`): the figures who go home at dusk or in the wet
  (kite flyers, the bubble child, the swing's, the leapfrog pair, bathers, skaters, the washerwoman, the stone-skimmer)
  appear and leave only where you cannot see them -- 40 m off, or out of view -- judged where they stand (or, hidden,
  where they will appear). Before, only distance counted: they popped away in front of you in the rain, or a skater
  kept skating on thawed ice while you stood by watching. The washerwoman and the skimmer used to blink out at once.
  The night watchman does the same (judged at his height on the wall walk). Groups go together with `party` /
  `partyToPlay`, all out or all home while no part of them (a sphere r metres round their middle) is in view: the
  juggler and his crowd, the fire's sitters and its dancing couple, the shepherd with the flock and the dog; the
  wedding starts and ends by the same `unseen` test. On the world's first frame everyone just takes their place (and
  the bonfire starts burning or cold), so you do not arrive to an empty show. Fixed with it: a figure never hidden
  before has `an.hidden` undefined, which the old `hidden === out` test never matched -- kite flyers never went home.
- **Home at dusk, and in the rain** (tag.js `send`, index.html `tagPlanTick`, TAG_HOME; village-life.js `homeWay`): the
  children at tag no longer vanish in view at nightfall. Once the dark passes TAG_HOME (.3), or it rains, the game ends
  and each runs home along the streets (the router's way to a house door, `TAG.way` 2.3 m/s) and goes in there; in the
  morning, or when it clears, they come out of those doors and the game takes up. On the world's tick, from the
  world's clock: the same in a shared world. On a dance day they walk to the maypole (mode "held") and the dance
  starts when all are there, on its own clock; after it the game takes up from where they stand -- they used to jump
  from the ring to the green when it started to rain.
- **Rain sends people in** (village-life.js RAIN, the world's `isWet` and `roofed`): when it starts to rain, the
  villagers working or idling under the open sky -- the fields, the market, the green -- take their next decision within
  a few seconds of each other (`stagger`), hurry (`hurry` 1.35) to a free place to eat or home, and
  stay while it rains; walking in it by day with nothing in their hands, they hold both hands over their heads (the
  `cover` gesture). When it clears they go back to their day.
- **Life on the wall** (index.html SENTRY, WATCH, `wallStep`; pigeons.js on `perch` parts): by day a SENTRY in the
  guard's kit walks the wall walk, stopping every `every` metres (34: the towers' spacing) to look out over the field
  for 5-11 s, a hand shading his eyes, facing away from the town; at night the watchman walks it with his lantern as
  before. Pigeons settle on the battlements: the crenellation's merlons are `perch` parts (their share of birds .06),
  their tops ridge lines the pigeons land on (architecture.js), as on the roofs. Both walk the walk's MIDDLE, town.js
  `frame.walkIn` in from the wall's line -- between the field parapet's inner face and the town-side rail, from the wall's
  own `fp` and `ri` (they walked a metre in: on the rail).
- **Up the towers** (index.html SPIRAL_STEER): every wall tower can be climbed from its walk door up the spiral stair to
  the platform. On the stair the view is steered round with the treads within `from` (.9 m) of the axis, at most
  `most` (.2 rad) a frame, and kept on the stair's walking line (`keep` a frame per metre off it): near the newel the
  view used to spin, and a walker drifted out to the wall and stuck at a window's shutter.
- **Hide and seek** (hideseek.js HIDE; index.html `hideSpots`, `seenFrom`): by day in the dry, come up to the two
  children at leapfrog and click: you count twenty seconds while each runs off along the paths to a place you cannot
  see from where you stand (round a house's corner, behind a haycock: a crouched child there hidden from your eyes by a
  wall or a prop) and crouches. Then go and find them -- a child is found within 1.8 m, or when you look at it within
  7 m with nothing between; it laughs and runs back to where you counted. All found, or three minutes gone (they come
  out by themselves), they go back to leapfrog. On the frame's clock: the game is yours alone.
- **The market by the season, and its crier** (items/furniture/stall-season; index.html stallSeasons, CRY): the
  greengrocer's and the fruiterer's counters show the season's produce -- radishes, leeks and spring onions in spring;
  peas, beans, cucumbers, strawberries and cherries in summer; cabbages, carrots, beetroot, plums, apples, pears and
  grapes in autumn; what keeps (leeks, onions, parsnips, cabbages, apples, pears) late in the year -- Old World produce
  only, as the market stands in every period. Each season's wares for both stalls are one item, built once; the
  season's is shown. Now and then (every 10-26 s) by day in the dry, when you are within 38 m, a vendor at their stall
  calls out their wares in the people's language ("Frisches Gemüse, frisch vom Feld!").
- **Chores of the seasons** (index.html CHORES, `choreTick`, `choreMiss`): someone at the season's work with its things
  about them, by day, not in the rain, out and home out of your sight. While the river is frozen hard, a man FISHES
  THROUGH THE ICE beyond the skaters, sitting on a stool by a hole cut in it (items/components/ice-hole), jigging his
  rod over it (the `jig` gesture). In autumn a man SPLITS LOGS at a farmhouse's chopping block (items/furniture/
  woodpile: the stump, a round on it, the billets stacked beside; there all year), the axe in both hands up over his
  head and down (`split`). Once the corn is cut, a HARVEST WAGON stands in a grain field heaped with sheaves (the cart
  bodies' load 5, items/tools/sheaf -- never on the road; it stands there overnight) and a man pitches more up onto it
  with a fork (`pitch`). A chore's place is the first of its candidates whose points are all open ground and claimed by
  nothing else; `__dbg.choreWhy(name)` says why each candidate would not do. A tool's tilt can be the holder's own
  (tools.js holders' `follow`): an item worked by what reaches up out of the hand -- the rod over the hole, the axe
  coming down on the block, the fork -- tips forward as the forearm lifts, where a spade's blade swings forward.
- **Ground claimed** (index.html `claim`, `claimedAt`, `lintPlaces`; build/worldlint.py): every activity laid out on
  open ground claims it -- the green, the kites, the bubbles, the spots by the river (the washerwoman's, the skimmer's,
  the bathers': `wet`), the pasture, the fire, the snowman, the swing, the leapfrog line, the sled run, the chores --
  and nothing later is laid out over a claim (`clearOfStands`). `python3 build/worldlint.py [SEED ...]` loads worlds one
  at a time (the cached seeds by default) and checks every claim's ground, a metre apart along it and round it at its
  breadth, for walls and yards, water, the land's edge, tree trunks, props not its own, and other claims.
  A chore placed on a site's own ground by design (`own`: the harvest's cart in its grain field) claims `own`, and the
  check counts only walls and posts there, not the site itself -- in autumn it was flagged as all in a building or yard (2026-10-24).
- **Snow on the roads** (paths.js trackFrag `snow`, grass.js GROUND_SNOW): the roads used to stay bare brown in snow
  with a bright green verge along both edges. Now the verge whitens with the meadow, and the track is trodden snow --
  patchy, the wheel ruts left brown; frost rimes the verges too.
  And the open-air sites -- the market, the farmyards, the bridge -- declare it (their finish's `open: true`): their
  surfaces and the items on them (the stalls' awnings and counters) take snow at any height, where a building's
  take it only well above the ground (its floors are indoors).
- **Placed by rule, checked against the buildings** (index.html `hitsBuildings` -- the buildings' part of `collides`,
  usable from the start -- and `openStand`: no building part there and nothing lower than 3 m overhead): the juggler's
  spectators take the nearest open spot on their ring (one used to stand inside a market stall, behind its counter; one
  with nowhere open is left out), and trees, bushes and hedges are never planted in a wall or a fence. Checked over
  three worlds: every placed figure and prop clear (harness game/placed.js).
- **Props you bump into** (index.html `propCols`, checked in `collides` beside the tree trunks): circles placed with
  the props that stand in the open -- each haycock (summer only), the snowman (while it stands), the swing's four legs;
  you used to walk straight through them.
- **Windows on the wall's face** (index.html `wallOuter`, SHUTTER): the window markers stand in the wall's middle and
  say nothing of its thickness, so each window's outer face is measured once at load (a ray from outside just under the
  sill). Its flower box sits just outside it (0.15-0.33 m out, by wall), not a fixed 0.33 m (a box on a thick wall sat
  inside the window's reveal); its SHUTTER hangs on that face -- closed over the opening from outside, and open it
  swings right back flat against the wall (SHUTTER.open, 173 degrees; it used to stick out of the reveal at 109) --
  and its night glow is drawn in front of the closed shutter (nightglow.js: the leaks round it and its cut heart).
  Glass casements stay in the wall, opening as before.
- **Terrain seams closed** (terrain_data.js roadTileData `nb`, 2026-10-23): the tiles a road touches are built at the
  finest level and cut along the roads, but they did not know their neighbours' levels -- beside a coarser tile on a
  slope their border followed the ground while the neighbour's edge was a straight chord, and slivers showed along the
  join (measured: 34 points along the borders disagreeing by 5-13 cm). Their border vertices now take the coarser
  neighbour's chord, as ordinary tiles' always did; the same measurement finds none.
- **No trees in the streets** (index.html `offRoad`, 2026-10-23): the woods' trees keep 2 m off every road and the
  scattered bushes 1.2 m (they used to check the sites and the water only -- a bush could stand in a town street); the
  hedges use the same check.
- **Hedgerows** (index.html buildFlora HEDGE, `hedgeSpots`): the country lanes (routes 1.4 m wide or more, not the
  carts' turning loops) are hedged on both sides outside the town's walls -- a bush of 1.5-2.1 m every 2.1 m, 1.6 m
  off the lane's edge, in runs with gaps (a fifth left open, each gap 2-6 bushes long); never on another road, in water
  or on a site. Seeded by the town (their own stream: the woods' and meadows' draws unchanged), rebuilt with the
  season like every bush; same herd and leaf cards (no draw of their own; ~220 bushes). The children's green is found
  clear of them (its search rejects a spot with a hedge within its radius + 3 m).
- **Riders**: a person in riding pose fused onto a horse skeleton, patrolling
  one grand tour of the whole path network; loose horses roam free and can
  be mounted. Where a rider sits is ONE placement (index.html `riderOrigin` /
  `riderEye`, from the saddle `fuseRider` hangs the fused riders at): your
  eyes when you ride anything -- a horse or a diplodocus -- your own body on
  the saddle, a peer's rider and a clone all sit there. Your own body is
  placed right after the move, before its head and the bow read it.
- **Water mill** (`assets/architecture/village/watermill`, tools/archgen/riverside.py): a 9 x 6.5m stone
  mill house with a 6.1m undershot wheel standing off the river wall on a
  piled frame, its axle only .5m above the floor so the paddles reach the
  stream 2.35m below (the wheel turns at flow speed over radius, bottom
  running with the current). Inside, walkable: the axle's pit wheel turns
  in a fenced pit cut through the floor and drives the wallower on the
  upright shaft; the runner stone turns over the bedstone on the hurst
  frame under a hopper, meal runs down a chute; wheat waits in sacks by
  the door, flour leaves in barrels along the wall. The door opens east
  onto the riverside street.
- **Fire**: a hearth's fire is live -- a handful of cones that sway, stretch and flicker in a vertex shader on
  the render clock (far faster than the water), yellow core to orange tips; any building may export `fires`
  (a definition's `fire` markers) and get one.
- **Riverside street**: a 1.5m track along the north bank 4m up from the water, from the lake path to the
  mill's door, then on round the landing yard to the bridge's north ramp.
- **Stone bridge** (`assets/architecture/village/bridge`, tools/archgen/village.py): 35m west of the basin
  a three-arch bridge crosses the river, built to the river's width where
  it stands. The middle arch (4.3m radius) springs .3m over the water, so
  its crown clears the barge and its boatman by more than a metre; the side
  arches reach the abutments on the bank lines; two piers with cutwaters
  stand on footings below the bed. The 4.4m deck sits 2.9m over the banks
  behind .95m parapets, reached by 14m stone-faced ramps (11.7 degrees) at
  either end, all walkable through its `floorY`. The barge passes under it
  coming and going. Roads: from the mill west along the quay, round the
  landing yard, up the north ramp; down the south ramp into the town's bridge street.
- **The town** (`town.js`, 2026-09-27): a walled market town on the south bank at the bridge's head, and its
  farms over the river -- laid out and styled by the world's seed, built of the village definitions alone
  (`assets/architecture/village`, docs/arch.md "The village"). The seed draws a STYLE first -- timbered (framed
  upper storeys over plastered or stone ground storeys), stone (grey ashlar or rubble under slate), brick, or
  plastered -- and every building shares it: one stone for the walls, the church, cellars and flagstones, ONE
  roof covering for the town (its church, towers and most houses; since 2026-10-23 about a third of the houses --
  town.js `roofAt`, by a hash of where they stand -- wear another of the style's roofs, a town re-roofed over the
  years: red tiles among the slates), one wood, two or three plasters and one or two timber colours the houses
  choose among, the house kinds the town favours, and the tops of its church tower (spire, pyramid, saddleback,
  onion, battlements), its wall towers (open behind merlons, or a room under a cone, an ogee bell or a tent
  roof) and its gatehouses (hipped roof or battlements). `?townstyle=timbered|stone|brick|plastered` forces one.
  THE PLAN: the main street runs east-west 30m south of the bridge's foot from the west gate to the east gate;
  the bridge street runs from the south ramp's foot past the square to the south gate; the south street 36m
  beyond the main street, two lanes between them. Every house faces its street, set 1.2m back from its edge,
  eaves-drip alleys between them and now and then a passage to the yards; each is its own definition --
  frontage, depth, two or three storeys, pitch, jetty, a cellar or not, turned to its street (`yaw`) -- and its
  own look within the style. Eight of them on the main and bridge streets are SHOPS (the ground storey an open
  arch, a trade's furniture in the front room and its worker at it: smithy, bakery, pottery, weaver, tailor,
  carpenter, cooper, butcher). The SQUARE at the bridge's head holds the market (stalls, market cross, vendors)
  and the fountain; the INN (`tavern`: the eaves house at its largest, a cellar, the tavern room with the keeper
  at the bar and two tables of guests) faces it from the east, the CHURCH (`church`: nave, chancel, west tower
  with a spiral turret to the belfry, pews, the altar and the priest) from across the main street, its door in
  the tower toward the bridge street. The fisherman's hut stands on the bank east of the square (its jetty, and
  the fisherman's boat: rowed out, fished from, rowed back on the sim tick like the barge).
  THE WALL: west, south and east, open to the river; a gatehouse where each street leaves (the west and east
  gates watched: two soldiers in mail and steel caps outside each, armed out of the watch's kit -- a spear or a
  sword and a shield, a halberd, a bill, an axe, a crossbow, a musket (assets/items/kits/guard, docs/items.md) -- the
  gatehouse's `guard` markers), a round tower at each corner, at each river end and between, every stretch at
  most 34m. The walk runs along the top all the way round -- behind the towers (their doors face it), through
  the gatehouses' upper storeys -- behind a crenellated parapet on the field side and a low one on the town
  side, which run into the corner towers and meet the gatehouses' faces; a flight climbs to it beside each gate.
  The towers between FLANK the wall, as they were built (town.js FLANK, from the assets' R and T): out from its field
  face, their backs where the field parapet's inside runs, so the walk passes each full width with the tower's door
  on it, the crenellated parapet runs into the tower (flankStop) and the town-side balustrade runs on behind it,
  one post where two walls' meet. They used to stand astride the wall's outer face, taking half the walk, with
  both parapets stopped 2.8 m short of them -- no balustrade there at all. The corner and river-end towers stay
  astride: they close the wall's turn and its end.
  THE LONGHOUSE: 3m walls under a thatched shell roof, a boarded loft over the whole house at the eaves (a stair up the
  middle under the ridge, a smoke hole over the hearth), arched doors in both long sides.
  THE FARMS: over the river, two longhouse farmsteads west of the bridge road (a farm track from the north
  ramp's foot along their doors) and one east of the landing on the quay road, each with its plots in rows
  behind it: rye and barley (14 x 12m), cabbage, beans on poles and garlic (12 x 10 / 10 x 8m), the plowed
  field, three rows of currant bushes, the orchard (apples and cherries on a 5m grid), the pig yard (a
  pigsty with lean-to roof, trough and a wallow of trodden mud in overlapping rounds with a wet, darker middle, the rest of the yard rooted bare -- `scratched`, as the hen yard's), the hen yard (a hen house on legs, the ground scratched bare -- `scratched`, dry earth in overlapping rounds over most of the pen, palette `dust`), the stable yard (the ground trodden bare before the stalls and from the gate -- `scratched`; a stable
  block with four stalls, a trough, a hitching rail, hay) and the beekeeper's garden -- five pigs, eight hens
  and four horses in their yards, penned by their own ranges. The hen yard has a rooster too (the chicken's `rooster` variant; the dawn crow -- ROOSTER -- now comes from him,
  wherever he is in the yard, and he crows now and then through the day too, every three to seven minutes), and the hens and
  the cock go in at dusk and come out in the morning (index.html roostTick, `hidden` while out of sight). By day a woman
  feeds them (CHORES `feed`: the basket on her arm, the `scatter` gesture -- people.js -- casting the grain: GRAIN, a few dozen specks arcing from her hand
  to the ground in time with the swing, one small instanced mesh placed each frame -- only during a bout: inBout,
  the one clock the lure reads too), and the hens gather round her feet; in the pig yard a farmhand tips out a bucket of slop
  (CHORES `slop`, the `pour` gesture) and the pigs crowd to it; in the stable yard a stable-hand forks hay (CHORES
  `hay`, `pitch`, `lureR` 2.6: the horses keep a wider ring). A chore's `lure` names a yard (its fence's `yard`):
  choreLureTick lures that yard's animals that `beg` to places of their own round the worker (begStep's lure, as the
  ducks to a splash) -- in bouts (`FEED.bout` seconds in every `FEED.cycle`, each chore its own moment; the worker's
  swing, `an.work`, eased in for a bout and out after it); between them they wander (the pigs: 5.3 m round the farmhand, 1.8 m in a bout, 7.6 m after it). Chores may name a working kit (`outfit`: wardrobe.json `farmhand` -- the slop, the woodchopping,
  the harvest -- and `farmwife`, the hens' feeding) -- medieval kits, so only in a period that dresses in the default
  style (periods.json `dress` with ""): an Egyptian or a Roman farmhand keeps his period's own dress. The chicken now `beg`s too: it comes to its fence when you stand still near. Each farm's side track runs past its plots' real east edge (2026-10-24: a pair of plots
  reaches 1.5 m plus its own width each way; half their summed widths put the track inside the hen yard's fence), and
  the second western farm moves west if its track and plots would run into the first's. The currant bushes and the orchard trees are
  PLANTS, not building parts (`plants`: the flora builder grows them with the woods' `makeBush` / `makeTree`);
  fields are tilled slabs whose crops are shader cut-outs, so a field costs a few dozen boxes. Nothing in a
  field obstructs walking.
  THE GROUND UNDER THE BUILDINGS is cut away (grass.js `GROUND_HOLES`): wherever a town building has a floor of its own
  at or below its ground floor -- its rooms, a cellar, the stair down -- read from its own floors on a 20cm grid, the
  ground's material, the grass mask and the water plane all leave it out, so a stairwell opens onto the cellar and not
  onto the lawn, nothing grows indoors, and a cellar dug below the water level stays dry.
  The town's ground is level from the river to past the south wall; every building levels its own plot too
  (`flatZones` with `level`, which also suppresses the river-bank carve under it) except what reaches over the
  water -- landing, mill, fisherman's jetty, bridge -- and the wall, whose ends stand by the river. The
  streets are paths.js tracks (`TOWN.routes`: gate to gate, the bridge to the south gate, the lanes, a spur to
  every door, the farm tracks) and the villagers walk them. The town's buildings are drawn in the finish
  material and merged across buildings (merge.js `mergeAcross`, taking the meshes from under each building's
  translated groups): some 45 meshes for the whole town, about 2-3s of building at startup (pregen/ holds
  every style's tiles, `town/<style>`; the houses' geometry is made per seed).
- **Goods** (`architecture.js`): barrels at two real sizes (the ~225 l
  barrique and the ~40 l keg) and full grain sacks (~1m long, ~.5m
  across, standing or lying) -- shared by the mill and the cart loads.
- **Carts** (`carts.js`): three real-dimension vehicles -- a two-wheeled
  cart on 1.5m wheels behind a single animal in shafts, a 2.8m farm wagon
  (one pair, or a single), and a 4.2m freight wagon behind two or three
  pairs -- drawn by oxen (a new draft species) or horses under a yoke, ox
  pairs with their neck bows, the first pair on the pole, further pairs on
  trace chains. Loads come in five variants per size: barrels in lying
  rows chocked into pyramids, standing casks, kegs in the gaps, grain
  sacks laid across the bed in two courses, and mixed sack-and-cask
  loads. A driver sits on the front board. Bodies are merged
  polygon groups (architecture materials), wheels are shared instanced
  meshes rolled by distance / radius (three sizes for the whole fleet),
  teams and drivers are banner skeletons in one herd, so a dozen carts
  cost a few dozen draw calls. Carts circle the highway on the sim tick,
  spaced evenly, oxen at .85 m/s and horses at 1.25 m/s, slowing behind a
  slower cart instead of driving through it. Bodies pitch over the terrain
  between their axle probes. `?carts=N` sets the fleet (default one per
  ~200m of lane, 2-12). Carts are placed every frame at their fractional
  position between sim ticks, so they glide; a bed is a floor -- jump on
  and it carries you, turning with it, at its own pace -- and the body is
  solid: below the bed you are blocked, the side boards are stepped over
  when low and jumped when high (the freight wagon keeps you in). The
  barge's hull and gunwales work the same way. The walker's
  physics itself sub-steps at 50Hz whatever the frame rate. ONE FRAME
  OF REFERENCE (2026-10-09): `frameBody` advances the simulation and
  places every mover (carts, barge, boat) and every rider first, then
  moves the walker and the camera, so the cart, its driver, its load and
  you on its bed all stand in the same frame; the bed's height is taken
  on its tilted floor (`bedY`), the eye sits fixed on it (no easing while
  carried), and figures on a mover (`moving`) are posed every frame
  whatever their distance.
- **Freight** (the transport chain): 60m west of the mill the river
  widens into a ~36m basin with a **landing** -- a gravel yard on the
  quay top, a plank deck on piles out over the bank, stairs down to a
  floating stage at barge-deck height, bollards -- joined to the highway
  by a 4m freight road. A **barge** (11m, raked ends, cabin, tiller,
  gangplank) sails in from downriver, moors at the stage, is unloaded,
  sails out, waits out of sight, refills and returns. Two **dock hands**
  carry each barrel or sack from the hold, over the plank, up the stairs
  to the yard's storage rows, one at a time, and wait when the barge is
  away. Five **freight carts** run their own loop -- yard, freight road,
  the highway east, into the palace yard and the castle yard, round the
  east loop, back west -- halting at the quay to load (a piece every 3s,
  2-5 per cart by size) and at the yards to unload; delivered goods are
  consumed after 90s and return to the pool for the barge's next trip.
  Goods are one pool of 14 barrels and 14 sacks, two instanced meshes,
  each piece always somewhere: hold, hands, quay, bed, yard, ground or
  your arms. Cart beds and the barge deck are moving floors. The whole
  chain runs on the deterministic tick.
- **Flora** (`flora.js`): trees GROWN from a seed by recursive branching
  (after the trees lab): six species -- oak (random forks), birch
  (alternate, drooping twigs), Scots pine (whorled crown on a long bole),
  spruce (a leader with whorls of near-level branches, conical), willow
  (weeping), maple (dichotomous) -- each a mode plus depth, fork count and
  angle, jitter, length/radius ratios, curvature, wobble and lean, grown in
  trunk units and scaled to its real height. The wood is capsule banners
  in the trunk's bark out to the thinnest twig; the outer
  levels carry leaf cards painted from the leaf atlas (oval, ovate, lobed,
  needles, willow; textures.js -- ovate, the birch's and some bushes', was "round", discs, until 2026-10-24: now
  pointed at the tip, broad at the base, on a stalk; flora.js takes the cells' ids from LEAF_STYLES, no copy), cut out by alpha with alpha-to-coverage
  edges, shaded by facing and depth in the crown, swaying in the wind, all
  cards of the forest in one draw (`foliage.js`). By default every card is
  a banner turned to the camera (each by its own angle in the screen
  plane; its grown orientation still shades it) -- `?billboard=0` stands
  them fixed in space. Autumn turns each card on its own, so a crown turns
  mottled. Bushes (1.6-3.2m) are a few bark stems fanning out of the ground
  with a rounded clump of the same leaf cards; about a third bear fruit --
  berry-cluster cards in currant, blueberry, blackberry, gooseberry or rose
  hip colour on the clump's surface alongside the leaves. Five flower kinds at
  generous real sizes, mushrooms; drifting multi-tone clouds. The wood and
  undergrowth share one instanced draw; everything rebuilds
  deterministically when the season changes. `grove.html` shows every
  species (A: autumn, R: re-roll).

## Village life

`village-life.js` gives the town and its farms their people (`?villagers=32`):
every villager has a home -- a house and a place in one of its double beds
(each house exports `beds` and, when the beds are upstairs, `ways.up` -- the
walk up the stairs) -- and a job: a work spot a building exports (folkSpots
with `role: "work"`: miller, inn keeper, market vendors, baker, potter, smith,
weaver, spinner, tailor, priest, a fisher on the jetty), two sack carriers
(home to the mill's `drop` with wheat, or back with flour), and farming for
everyone else (places spread over the fields, the orchard, the currants).

- Night (N): home to bed; the keeper stays at the inn, a quarter first go
  to the inn to eat if a seat is free.
- The bell (the real clock's hours): half of those awake -- a different half
  each hour, never the sleepers -- sit ten minutes in church (the rest stand
  at the back), then go on.
- Work: arms busy by trade -- `GESTURES` in `people.js` (dig, hoe, mow,
  hammer, knead, sell, fish, strum, bless, eat, pick, weave, sew, lift), named by
  the spot, swung by `skeleton.js` on the world clock (`an.gesture`, `an.work`);
  a worker whose spot names a `tool` holds it in the right hand -- a low-poly
  mesh (`tools.js`, one instanced draw per kind, placed each frame from the
  posed hand and forearm; SDF shafts smeared the one-quad engine): the
  scythe in the rye and barley, the spade on the plowed field, the hoe among
  the vegetables, the smith's hammer, the fisher's rod, the bard's lute. Seated
  hands work too (potter, weaver, spinner; guests eat). Between spells a small
  chance to go and eat (a seat free) or to buy at the market or a shop.
- The trades work in their shops on the main and bridge streets (town.js); the
  beekeeper tends straw skeps in the garden behind a farmstead over the river.
- What a site IS comes from the town plan, never from its key: `home`, `role`
  ("inn": its keeper and its guests' seats; "church": the pews and the back),
  `farm` (land the farmers work; the tool by the field's `crop`).
- Homes: every site the town plan marks `home` (the houses, the inn, the
  longhouses) with beds; two sleepers to a bed, laid along the bed however it is
  turned; an upstairs bed's way up is the house's `way` markers only as far as
  its own storey. A house's own table is its household's: only a place where
  someone works (a shop, the market) takes customers.
- The inn is never empty: at least three guests, day and night -- one whose
  meal is over waits until someone new has come in and sat down.
- Shutters stand open by day and close at night; glass (palace, church) stays.
- The bard at the fountain plays a random song on a random instrument of the
  day (lute, lyre, harp, flute, recorder, fiddle), then another -- heard from
  where they stand (`instruments.js`).
- Walking: out of the door (down the stairs first), the shortest way over the
  path network (`routeGraph` in `paths.js`; the bridge deck is its one link
  over the water), in at the door; doors open as they pass.
- Each villager is four composite entries (walking, seated, lying, carrying a
  sack), one shown; it moves on the fixed tick by its own seeded stream and is
  drawn between ticks by the shared tracks. `__dbg.life.census()` lists where
  everyone is; `__dbg.life.bell(h)` rings the bell for them.

Sound: `environment.js` is fed the world's state each frame (weather,
intensity, wind, night, indoors, distance to lake, river and hearth); `calls.js`
gives every creature its own call; `speech.js` gives every person a seeded
voice preset of their kind (`voiceFor`: men, women, children, and some old
voices) and they say one to three random words when you are near.

Wandering animals follow ROUTES planned once (`wanderLoop` in paths.js): a loop of waypoints inside
their range, every leg checked when planned; per tick they only advance along it (walking and
standing, hops, gliding and swimming as before), their heights sampled along the route the first time
they pass and read back ever after -- no range tests or terrain probes per step (about 4.5 ms -> 1 ms a
tick for ~520 of them). One moved by something else (a ridden horse let go) plans a new loop from there.

Squirrels (`squirrels.js`, `?squirrels=14`) live in the groves -- trunks with a neighbour within a
dash: across the ground to the next tree, up the trunk head first along its real bole (makeTree exports the trunk's centreline;
the skeleton's root takes a pitch, `an.pitch`, matched to the trunk's slant, the feet on the bark), a pause up there, down head first, a watch at the foot.

Behind the mirrors, on the salon side of the partition, hang gilt-framed paintings whose canvases are
views of the world itself: on the third frame `paintings.js` draws the scene once from ten lookouts
(on the town wall's walk, the middle of each stretch, spread round the town, each looking at its heart) into 640 x 480 pictures, which the frames take in turn.

The lake is 6.6 m deep at its deepest (the bowl carved 8.8 m below the plain), with 30 fish. In water
deeper than you stand you swim: afloat with the head just above the surface, E rises, Q dives to the
bottom (Shift faster), a little slower than walking; a mount swims the same way, and a winged one
lands on the water going down onto it and takes off from its surface. Bees hum round the beekeeper's
hives by day in dry weather (the environment's `hives` distance).

The palace's gallery is a Hall of Mirrors: sixteen tall gilt-framed mirrors on the partition opposite
the windows (`mirror` markers in versailles.json, each with the gallery it reflects in: tools/archgen/versailles.py). `mirrors.js` makes them reflect with three's
Reflector -- the scene drawn again from the mirrored camera. The reflection through a plane is the same
for every mirror on it, so all the mirrors of one wall are ONE Reflector over their merged panes: one
extra draw of the scene lights all sixteen. Up to two planes reflect (the largest on screen, in view,
within 60 m), at half resolution, dulled like old glass, one bounce only; a plane off the budget shows
still glass of the same tone. During a reflection the composite figures are drawn in full.

Grain sways in the wind: the rye and barley cut-outs bend as rows on the
leaves' wind clock (`FOLIAGE_T`), gusts running over the field -- broad bands
travelling down the wind (the grass's way) in world space, so they run on from
one field to the next, bending the stalks further and turning the ears a third
paler as they bow: the silver waves over ripe grain (architecture.js archFrag).
In LATE AUTUMN the grain is in (foliage.js HARVEST, set by index.html from the season): the rye and barley stand
cut to stubble a hand high, and the sheaves are stood up in stooks every 3 m across the field -- a cone each, drawn
in the same cut-out shader where the crossing rows meet, so two silhouettes cross in it and it reads round.

Culling the GPU-placed effects: smoke, washing, window flowers, pigeons, flags, swallows, starlings, bees, reeds, the
juggler's balls, the bonfire's light and the river mist are drawn where their shaders put them, so their vertices
say nothing of where they are; bounds.js `boundTo` gives each the sphere round its anchors (padded by how far the
shader takes it) and three skips it while that is out of view. The bees, the balls and the ducklings are also not
drawn past 100, 120 and 160 m (index.html farOff). Together: about half a millisecond of a frame for all of the
loop's additions (12.4 against 11.9 ms measured headless with them switched off).

## Environment switches

- The church bell strikes the hours by the real clock: on the hour, as
  many strikes as the hour shows, the same moment on every peer's wall
  clock -- and the roofs' pigeons go up at the first strike (checked every frame, sound or no sound).
- **P** rain → snow → clear; **O** intensity -- which on a clear day also
  sets the cloud cover: few, half or all of the 28 clouds (flora.js `makeCloud`, since 2026-10-23 cumulus: a flat grey
  base of two or three thin slabs and a heap of seven to ten round puffs on it, tallest in the middle, brighter the
  higher; CLOUD_PARTS 13 a cloud); rain and snow always bring them all. Precipitation is three
  depth-tested billboard curtains 4/10/22m ahead of the camera, so walls
  occlude it and interiors stay dry (each curtain also hides itself when its
  anchor point is under a roof). Snow raises a shared uniform (foliage.js SNOW) that whitens
  roofs, spires, grass and the trees' crowns (the leaves facing up, the outside of the crown most) while keeping relief shading
  -- settling over a minute and a half of snowfall (on buildings in an uneven dusting first: archmat.js SNOW_ON's noise)
  and melting over five minutes once it stops, everything wet while it melts (index.html SNOW_EASE); light rain, and the
  minute and a half after any rain stops, shows a rainbow -- in the sky dome's shader (sky.js), 42 degrees round
  the point opposite the sun, so low at noon and a tall arch toward evening, with the faint reversed second bow,
  the brighter sky inside and Alexander's dark band; by day only, since it needs rain AND sun (`?bow=1`).
- **Music from the inn** at night: its guests' fiddle and lute, muffled by the walls (a 900 Hz low-pass), heard in the
  street outside -- the musicians' player (playAt, `muffle`), from the inn's door.
- **A tour flight** (index.html startTour, Y): the camera glides along a smooth curve (centripetal Catmull-Rom, 12 s a
  leg) through the world's sights -- the town from above, the market and its juggler, the children's green, the bridge
  and the river, the mill, the fields over the river, a herd in the meadow -- looking at each as it passes, at least 4 m
  over the ground between them, and back to where you stood; any key or click ends it there.
  The first time the world is opened in a browser, a welcome hint says so (Y for the tour, Tab for the controls).
- **Ring the bell yourself** (index.html ringBell): at the church's door, facing it, "click to ring the bell" -- three
  strikes of the bell, the roofs' and the square's pigeons up, and half of the villagers about walk to church as at
  the hour (village-life.js bell); not again for half a minute.
- **A wedding** (index.html WEDDING/weddingTick, `?wedding=0`): every 4-7 minutes by day in fair weather the bells
  peal (8 strikes; the pigeons go up) and a couple just married stands at the church door, 2.2 m out (town.js
  `doorNormal`: the way out of a door) -- the bride in white (wardrobe.json `bride`: white wool houppelande trimmed with
  white fur, a linen coif), the groom in his best (`groom`: woad tunic with gold braid, black hose and felt hat), who
  waves now and then -- with seven guests in an arc 4.2 m round them clapping in bursts and laughing, one more at its
  end playing a lute (heard: playAt "wedding"), and handfuls of pink petals thrown over the couple for the first 25 s
  (createPuffs, falling). It lasts 75 s; never begun or ended while you are within 25 m (no one appears or vanishes
  in front of you).
- **The rooster** (calls.js `rooster`): as the night turns to morning (dark falls past .45) the cock in the hen yard
  crows -- "cock-a-doodle-DOO", two clipped notes, a rising run and the long wavering last one -- three times over
  the next minute, heard as far as a cow's moo.
- **Sunbeams** (sky.js `sunRays`, U.rays): round sunset (dark .24-.52) in a clear sky, the sun's wide glow breaks into
  bands of light and cloud-shadow fanning out of it -- crepuscular rays, by the angle round the sun, drifting slowly.
  In the dome's shader.
- **The northern lights** (sky.js `aurora`/`curtain`, index.html AURORA): at each nightfall a 3-in-10 chance
  (`?aurora=1`: every night) that once it is dark (dark > .6, dry) the aurora eases in over half a minute -- two curtains
  low over the northern sky (-z), their feet folding and drifting, a bright lower rim, fine rays flickering along them,
  bright stretches and gaps, green at the foot going violet up their height, a faint red haze above. In the dome's
  shader (no extra draw), behind the far ridges; a toast when it comes. `__dbg.setAurora(k, t)`.
- **Morning mist** (index.html `fogFrom`): at the same turn to morning, seven dawns in ten (not in rain) a mist lies
  on the land -- the scene fog pulled in to 8..110 m, so the far trees and hills are pale shapes in the dawn's colour
  -- and after a minute it lifts over two more, back to the day's fog. `__dbg.setFog(t)` starts one.
- **N** night, and **U** the hours: one value, `dark` (0 day .. 1 night), eased over ~7 s by N or run round a
  whole day every 4 minutes by U (`?day=minutes`, `?dark=` presets the hour; .4 is sunset). It drives the SKY
  (sky.js: a dome from zenith to horizon, the sun high and pale by day, setting a little south of west with the sky
  round it on fire, gone at night; the fog takes the horizon's colour so the land melts into it), the frame's TINT
  (the one multiply pass: through warm evening light to deep blue), the four brightness classes of stars and the
  crescent moon (fading in past the middle of the dusk), the MILKY WAY (sky.js `milky`: a band along a great circle,
  mottled by value-noise fbm and split by a dark rift, brightest toward its core, with a dust of faint stars; never
  under cloud), occasional shooting stars, and DISTANT MOUNTAINS round the edge of the world (sky.js `ridges`: two
  ridges 2-6 degrees over the horizon, a height by bearing from whole-numbered waves; the far one paler, silhouettes
  against the sunset; below the horizon -- past the land's edge, seen from high up -- the haze of the fog's colour). `night` -- the villagers' bed
  time, the owls, the shutters -- turns at the middle of the dusk.
- **Lightning** (lightning.js): in mid and heavy rain a strike every half minute or so (twice as often in heavy): a
  bolt 0.6-5.6 km off -- a jagged channel from the cloud base, a branch or two forking off it, a ribbon facing the eye
  -- flickering in two or three return strokes over half a second, and the whole sky lit with it (an additive flash in
  the glow scene, closer strikes brighter). Its THUNDER comes km / 0.343 s later: the environment renders a clap ahead
  and the game calls it (`createEnvironment({ selfThunder: false })`), so every clap follows its own flash.
- **Breath on a cold day** (breath.js): in snow (or a deep-autumn evening) the people within 16 m breathe out a puff
  of steam every 2.6-4.2 s -- from the mouth (by their height: man, woman, child), out a hand's breadth the way they
  face and up, swelling and gone in 1.5 s -- and so do you, just below your eyes. A pool of 64 puffs on the GPU.
- **Footprints in the snow -- and the mud** (footprints.js): while snow lies (SNOW over .5: on after the snowfall
  stops, until it half melts), walking outdoors on the ground itself (not mounted, swimming, resting, under a roof, nor
  up on a bridge's deck or the wall's walk -- the print went on the ground under you) leaves a print every
  0.72 m, left and right by turns 13 cm off your line, pointing the way you went -- a boot sole (heel, waist, ball)
  pressed blue-grey into the white, filling in over 2.5 minutes; 320 kept (the oldest reused). On a road soaked by the
  rain (ROAD_WET over .45, no snow) the same prints in the mud, dark wet earth (per print: `printKind`).
  And everyone else's: while snow lies, every figure walking within 35 m of you -- villagers, walkers, children, the
  animals -- leaves its own trail, a print a pace of its legs (`parts.legLen` x .8), left and right by turns, sized by
  its legs, not under a roof nor off the ground (every third frame; a pool of 900). A person's is a boot; an ANIMAL'S
  is its kind's (2026-10-24 -- every animal had left the same boot print, a hen's as big as a man's): a species
  declares `print` (assets/creatures; composite.js carries it onto the animal; tauric beasts keep their base's -- the
  centaur's hooves) -- `hoof` (a horse's rounded U), `cloven` (cattle, deer, sheep, pigs), `paw` (a pad and four toes:
  dogs, cats, bears, small beasts; also the default), `bird` (three toes and a spur: the birds, the two-legged
  dinosaurs), `pad` (round, its nails in front: elephants, hippos, camels, the great dinosaurs) or `none` (a snake, a
  spider). footprints.js PRINTS sizes each from the legs (printOf: k x leg length, within min..max metres; a gauge
  from the legs too) and draws its shape in the shader (`printShape`).
- **Rain and snow under a grey sky**: the weather sets the sky's `overcast` (.3/.6/.9 by intensity): the blue and the
  sunset's colours give way to grey, the sun goes behind the cloud (its disc and glitter), the light dims by up to a
  third (the tint pass runs by day then too), the clouds turn grey. In rain every stretch of water is pocked with
  drops: a ring spreading in each cell of two offset 0.6 m grids, each drop at its own moment, more of them the harder
  it rains (waterShade `rain`).
- **The water and the clouds keep the hour**: away from the mirror (the water reflector works near the water only) the
  surface takes a share of the horizon's colour at grazing angles -- gold at sunset, deep blue at night -- and the
  sun's path, and at night the moon's, glitter on it: only the crests' facets that catch the light, more of them the
  lower it lies (waterShade's sky/sunDir/sunCol/moonDir/moonCol, set by applyHour). The clouds (and the chimney smoke)
  are multiplied by the hour's `cloud` colour: rose-gold under the low sun, slate at night (createHerd `tint`).
- **What the small life costs**: `?ambient=0` hides the smoke, the starlings, the wash, the flower boxes, the reeds, the
  falling leaves and the wall lamps. Measured headless on this PC's GPU (the medieval town, 120 frames, two runs
  each): 232 draws against 224, 10.3 against 10.5 ms a frame, GPU 4.1-4.6 ms both -- inside the noise.
- **Flags** (flags.js): a pole on the spire of every wall tower, gatehouse and the church's tower (architecture.js
  lifeOf exports a roof whose top is a point as `peaks`), with a pennant (tapering, split along) or a swallowtailed
  banner (split across) in the town's two colours (one heralds' pair by the town's seed) -- streaming down the wind,
  waves running out from the pole, gusting and slackening with the grass's wind. Two meshes.
- **Bees** (bees.js): round each of the beekeeper's eight skeps a dozen bees zigzag about its mouth, and every 15-35 s
  each flies out 3-9 m on its own bearing (a new one each trip), stays a while at the flowers and comes back. Tiny
  cards facing the eye (a striped amber body under a blur of wings), placed on the GPU from the time and their seeds;
  out by day in fair weather, home at dusk and in the rain (the hum: environment.js near the hives). One draw.
- **Rooks going home** (geese.js ROOKS, index.html `rookWay`): at dusk (dark .28-.52, dry) loose streams of 28 rooks
  every 25-60 s cross toward the woods (the middle of the trees), 22-45 m up, quick wingbeats, cawing as they pass
  (calls.js WILD `crow`: playCall now reads the WILD calls too). The same flyover as the geese (createFlyover, one kind
  of flock declared as data: a V or a loose stream).
- **Wild geese** (geese.js, index.html `geeseWay`): in autumn (both stages) a skein of 21 crosses the sky going south
  every 70-170 s, in spring coming back north; by day, in fair weather. A ragged V (the left arm longer), 60-100 m up,
  15 m/s, passing over you or up to 130 m off to the side: out of the haze 700 m off and into it on the far side. Each
  goose is a chevron (murmuration.js `chevronBirds`/`chevron`, now shared with the starlings) placed on the GPU from the
  leader and its rank and side, bobbing in its place, the slow wingbeat running down the line. Honks (calls.js `goose`,
  the duck's QUACK voice longer and higher) from along the skein while it is near. `__dbg.geese.fly(t, camera, [dx, dz])`.
- **Herons** (assets/creatures/birds/heron.json, from the flamingo's parts: grey back and wings, white neck and head,
  a black crest, a yellow dagger bill; flags shore, shy 9, peck .45 about the neck's root): three along a river, two at
  a lake, standing at the water's edge or wading the shallows, now and then striking down at a fish (the hens' `peck`).
  With no lake the shore birds -- herons and flamingos -- keep to the river's BANKS (index.html: a band from .6 m in
  from the water's edge to 2 m up the bank), not the herd's meadow.
- **Wakes** (wakes.js): a duck or a swan under way draws a V of ripples behind it on the water -- two arms at the
  Kelvin angle (19.5 degrees each side, as every boat's and duck's wake), short crests slanting off them, fading behind;
  longer and brighter with its speed (full at .45 m/s), gone when it rests or is 90 m off. One card a swimmer, one draw.
- **Swallows** (swallows.js): three flocks of seven hawk for flies over the river round the bridge -- fast figure-of-
  eight loops round their patch at 9 m/s, dipping now and then to skim the water and climbing again, wings flicking
  in quick beats between glides; each a card from below (swept pointed wings, forked tail, dark blue-black over a
  pale throat), all from the time and their seeds on the GPU. Half of them out by day, all of them toward evening,
  gone at nightfall (the bats' hour) and in rain; a run of bright chirps now and then within 30 m. One draw.
- **River mist** (mist.js): from dusk (dark .3) to full night the river grows banks of mist -- 114 soft, wide
  quads facing the eye, 9-16 m long and a man's height deep, three to every 9 m of river within 200 m of the bridge
  where it is half a metre deep -- each sliding 22 m downstream at .35 m/s and fading in and out at the ends of its
  run so the drift never jumps, the top edge rolling in slow lobes, thinning to nothing within 4 m of the eye. Lit by
  the hour's cloud colour (rose at sunset, slate at night), thin in rain, thicker in autumn; eased over 6 s, hidden
  by day. One draw.
- **Fishing** (fishing.js, R): on the bank, facing the water, R casts -- the float lands in the first water half a metre
  deep 4-9 m ahead (a ring from it, a plop), bobs on the ripples, nibbles for a moment after 4-14 s and then goes
  under: R within 1.3 s strikes and lands a fish (a roach, a perch, a trout, a carp or a pike, its weight, how many
  today; a splash); too slow and it is gone with the bait. R while it floats reels in.
- **Your footsteps** (footsteps.js): a step every stride you actually walk (.72 m; 1.05 running) by what is under your
  feet -- grass (a soft brush), a road (grit; a squelch once it is soaked), stone a hand above the ground (flags,
  paving: a sharp tap), boards raised off it (floors, the bridge: a hollow knock), snow (a squeaky crunch), water when
  wading (a splash) -- and riding, two hoof-falls a stride (clops on hard ground). Synthesized once a surface, four
  takes each (noise through a couple of poles, a heel thump, grit, a struck resonance for boards, flags and horn),
  left and right a little apart. 2026-10-23 (too loud and harsh, by ear): each take scaled to its loudness (the RMS of
  its first 60 ms), not its peak, times the surface's `vol` (grass softest, water loudest), darker (lower low-passes, less
  grit, stone's ring 640 Hz not 1100, a 4 ms onset at least) and 12-14 dB under what it was; config.json `footsteps`
  (?steps=) scales it, 0 for none.
- **A dog at your heel** (companion.js, X): a whistle (two notes, the second sliding up) brings the nearest dog
  within 150 m running; it barks, and keeps at your left heel (1.3 m behind, .7 m aside) -- trotting when you walk,
  running when you run or ride (up to 7 m/s), standing turned to you when you stop, never stepping into the water.
  Throw a stone (G) and it races to where the stone came down (stones.js `land`), noses about for it a second, brings
  it to your feet and barks. X again sends it off (its wanderer replans from where it stands). While it is yours its
  wanderer is frozen and companion.js moves it every frame (local to you, like riding). Something shy within 10 m of it
  (a hare, a cat, a hen, a fox...) and it is off after it, barking, at a romp (4.5 m/s) -- the prey runs from the dog
  as from you (shyStep: both are threats) -- until it comes within a metre (a bark: let it go), loses it past 25 m or
  has run 5 s; then back to your heel, and no other chase for 20 s. It swims after a duck.
- **The river freezes** (index.html ICE, waterShade `ice`, `?ice=1` frozen from the start): under deep snow (SNOW over
  .8) the water freezes over three minutes, and thaws over two and a half once the snow has gone (under .3) --
  waterfalls never. The ice: dark glassy blue-grey with snow blown over it in pale drifts, long cracks through the clear
  stretches, the low sun glinting on it; opaque once frozen. Frozen hard (over .9) it BEARS YOU: supportAt counts its
  surface as a floor (`iceFirm`), so you walk out on it dry-footed; the ducks and swans stand on it (`floatY`); the
  contact shadows lie on it. SKATERS (SKATE/skateTick): three townsfolk skate near the bridge -- each a long
  figure-of-eight over the ice, arms out to the sides swinging with the strokes (`skate`), leaning onto each skate in
  turn and into the turns (an.roll); by day, not in the rain.
- **Sledding** (sled.js, index.html SLEDS/sledTick, `?sled=0`): while snow lies (SNOW over .5), by day, two children
  sled down the steadiest slope near the green (searched at load: an 18 m run dropping all the way, at least 2.2 m in
  all, on open ground -- no water, sites, hedges, tree trunks or props (index.html `clearOfStands`) across both
  children's lanes, every 1.5 m; the cheap height profile first, the lanes only for a run that would win -- ~20 ms).
  The steepest such run is taken if it drops at least `SLEDS.drop` (1 m): in gentle country (seed 7) a run of a metre
  or two does, the sleds going slower -- a 2.2 m floor used to leave such a seed without sledding. (Seed 7's run used
  to go through a tree.) Each child is two figures, sitting on
  the sled and walking, shown in turn: sitting at its back, tipped with the hill (an.pitch), pushing off and gathering
  speed by the slope against the snow's drag (to 6.5 m/s), snow kicked up behind when fast; at the bottom off and
  trudging back up pulling the sled on its rope (a line from the hand to the sled's curled front); a wait at the top,
  and again, the two 3.5 s apart. Sleds are blocks.js meshes (runners curled up in front, posts, five slats).
- **A snowball fight** (index.html SNOWBALL): in snow the children at tag lob snowballs at each other now and then
  (each every 1.4-3.4 s, at the nearest within 2.5-9 m, aimed where they are running to): an arc 1.3 m high over 0.8 s,
  a burst of snow where it lands (createPuffs) and, three times in ten, a laugh from the one it hit.
- **A snowman** (index.html, blocks.js `ball` shapes): on the far side of the children's green from the bonfire,
  looking into its middle -- three balls of snow, coal eyes and three coal buttons, a carrot nose, stick arms raised a
  little and an old black hat; there while the snow lies (SNOW over .35: built as it settles, gone as it melts).
- **The maypole** (maypole.js, index.html MAYDANCE): in spring a 6.5 m pole stands in the middle of the children's
  green -- a wreath of greenery and flowers at its top, a gilded knob -- and on a fair day the children dance round it
  instead of playing tag: each holding a ribbon in a raised right hand (`ribbon`), half going one way round and half
  the other, weaving in and out past each other; the ribbons (a strip each, sagging and fluttering, in fair colours)
  re-laid every frame from under the wreath to the hand that holds it. At night and in the rain the pole stands with
  its ribbons hanging; when the dance ends the game of tag takes up from where the children are.
- **Kites** (kites.js, index.html KITE/kiteTick, `?kites=0`): on a dry day, two children stand on the upwind side of
  the green (WIND_DIR: the way the grass's gusts travel) and fly kites out over it -- a two-coloured diamond on a sagging
  string, its tail of bows snaking out downwind. The line pays out as the wind takes it; the kite climbs, sways across
  the wind, banks into its swings, lifts in a gust (grass.js `gustAt`: the grass's own gusts on the CPU) and now and
  then turns a loop. A fine day's breeze now comes and goes over minutes (index.html `breeze`: .45..1.25, the grass,
  smoke and windmill with it): below KITE.wind the kites sink and are reeled in and lie in the grass by their flyers
  until it freshens. The flyers hold the string up (`kite` gesture) while there is a kite on it; they go home at dusk and
  in the wet (out of your sight: outToPlay). Their spots keep off sites and tree trunks (`clearOfStands`); the
  leapfrog line too. Two draws (the kites and tails; the strings as lines), CPU-placed.
- **The swing** (swing.js, index.html swingTick, `?swing=0`): on the green's edge (5 m out, clear of the bonfire,
  the snowman and the kite flyers, on level ground) an A-frame of rough poles with a crossbeam, two ropes and a board
  seat. By day in fair weather a child swings on it -- seated (`pose: "sit"`), hands up on the ropes, leaning back on
  each forward swing (`swing` gesture), the body tipped with the ropes (an.pitch) -- and another stands behind and
  pushes each time the seat comes back (`push`: on the world clock, in step with the seat). The seat rides a
  pendulum of .36 swings a second, what 2 m ropes swing at; without the children it eases to rest.
  YOU CAN RIDE IT: by its seat, "click to sit on the swing" -- the child on it hops off and sits on the grass by the
  frame watching, the other goes on pushing, and you swing (index.html `swingSeat`: resting `swing`, the camera on the
  seat each frame); click to stand up.
- **Working down low** (people.js gestures' `crouch` -> CROUCH, carried on the compiled parts with the legs' length,
  skeleton.js adds `crouch x work x legLen` to an.rest): a gesture done low bends the knees -- the washerwoman crouched
  at the water's edge scrubbing (.42 of the legs), the berry pickers (.12), the beekeeper (.15), a child out of breath
  with its hands on its knees (.1) -- easing in and out with the gesture's strength. Declared on the gesture: any figure
  doing it crouches.
- **Leapfrog** (leapfrog.js, index.html leapTick, `?leapfrog=0`): two children at the green's edge (clear of the swing,
  the fire, the kites and the hedges) take turns: one crouched as the frog (skeleton.js `an.rest` -- the same lowering
  that lays the cattle down folds a child's knees -- and the hands-on-knees `puff`), the other running up from wherever
  it stands (round the frog, at the line's turn), vaulting over its back (`leap`: the hands forward and down; the body
  pitched forward through the arc, .75 m high) and landing crouched 1.5 m on, the frog springing up to go next. A
  cycle of 2.2 s; they work their way 10 m along the edge and back. By day in fair weather (outToPlay).
- **Soap bubbles** (bubbles.js, index.html kiteTick `bubbleKid`): between the kite flyers a little one blows bubbles
  from a wand (`blow` gesture: the wand before the mouth for a breath of ~1.6 s, a stream of a bubble every ~.1 s, then
  down to the pot for 2 s). The breeze takes them over the green -- downwind with the grass's gusts (`gustAt`),
  wobbling, rising and sinking a little -- each a card drawn as a sphere: clear in the middle, the thin film's swirling
  bands of colour (sky.js `spectrum`, the rainbow's hues) toward its rim, a bright window of sky on its shoulder; they
  pop (swell a little and are gone) after 3.5-9 s or on touching the grass (each its own ground height). A pool of 48,
  one draw. **Z** (held): you blow them too, off ahead of you (`blowYours`).
- **The shepherd's flock** (pasture.js, `?flock=0` none): on a level round of open country 90-180 m from the town, a
  shepherd walks his loop with his crook (.55 m/s), standing a while every 20-40 s to let them graze; seven sheep follow
  in a loose bunch behind him -- each to its own place in the flock, turned with him, kept apart -- heads down to the
  grass whenever they stand (their `graze`); his dog runs wide circles round them, one way and then the other. By day;
  in extrasHerd; the shepherd a talker.
- **Children bathing** (index.html BATHE/batheTick): in summer, on warm fair days, three children wade knee-deep off the
  town's bank downstream of the stone-skimmer (`bankAt`, then out toward the river's middle until the water is .3 m
  deep) -- ambling about their patch of shallows (only where it stays knee-deep), and now and then turning to the
  nearest and splashing at them (`splash`: bent forward, both arms sweeping the water up, in turn) -- spray thrown their
  way and rings on the water (stones.js `spray`, now exported, and `ring`), a laugh now and then.
- **A child skimming stones** (index.html SKIM/skimTick): further along the town's bank (`bankAt`, the washerwoman's
  bank search, now shared) a child throws a stone every 4-9 s, a sidearm throw (`skim` gesture) let go at the swing's
  forward peak -- stones.js `throw({ p, dir })`, the same stones as yours (G): skipping, ringing and spraying, but quiet
  (no count shown, the dog does not fetch them). By day, in fair weather.
- **The washerwoman** (index.html washer): on the town's bank a little below (or above) the bridge, where the bank is
  clear, a woman bends over the water scrubbing linen (`scrub`: bent forward, both arms down in it, working in turn),
  rings spreading from her hands every second or two, her basket of washing beside her (blocks.js). By day, not in the
  rain. In extrasHerd; a talker.
- **The night watchman** (index.html WATCH): after dark a man walks the town wall's walk, from the river end of the
  west wall round the south to the east wall's and back, a lantern in his left hand (its light on the walk: the
  lanterns' glow) and a spear in his right; every minute or two he calls the old verse -- "Hört, ihr Leut, und lasst
  euch sagen: bewahrt das Feuer und das Licht!" -- in the people's language (WATCH_CALL: de en fr es it ru cs). He
  keeps to the floor 6 m up (over a gate passage, at the walk's height). In extrasHerd; a talker.
- **The juggler** (juggler.js, index.html SHOW, `?juggler=0` none): on the open south side of the market square a fool
  in motley (the wardrobe's `jester`: red-striped tunic, saffron hood, green hose) keeps three balls going -- the
  `juggle` gesture (forearms out, the hands bobbing in turn at 1.5 Hz) and a real cascade: three throws a second,
  each ball two beats in the air from one hand to the other in a 55 cm arc and one beat carried, the hands' places
  read from the posed figure every frame (the composite's ends). Five people stand round watching and every 9 s
  applaud for a moment (`clap`, each a little late or early; a patter of synthesized claps within 30 m). By day, not
  in the rain. In extrasHerd; talkers.
- **The bonfire** (bonfire.js, `?bonfire=0` none): beside the children's green (the first level round of ground just
  past its edge) a ring of eleven stones with four logs crossed in it and five log seats round it. As night falls
  (dark .45, not in rain; eased over 5 s) it is lit -- seven flame tongues standing on the logs, facing the eye,
  swaying and flickering (white-gold at the root, orange, red at the tips), forty embers rising on wobbling paths and
  winking out, a 13 m pool of firelight on the grass breathing with the flames -- all one additive mesh in the
  night's glow scene, shaded from the time on the GPU; its crackle is the environment's fire (environment.js, fed the
  distance to it scaled so it carries 35 m). Five villagers sit on the logs, facing the fire, while it burns -- the
  first of them PLAYING, a lute in hand and strumming, songs on a lute, fiddle or recorder (index.html MUSICIANS: the
  same player as the bard at the fountain, one graph a musician) -- and a couple DANCES to it in the seats' gap (the
  fire's `floor`), circling each other face to face, stepping, arms up and swaying (`dance`); there is room for you at
  the end of every log, beside the one sitting there (click to sit) (in extrasHerd; talkers, so they
  chat). By day the ring stands cold, the seats empty. The stones and logs: blocks.js (shared with the wall lamps).
- **Children playing tag** (tag.js, `?kids=6`, 0 none): on the flattest open round of ground nearest the town's
  middle (a 9 m green the country's wanderers could stand on, level within a metre) six children of the period play
  tag by day. "It" counts 1.8 s facing the middle, then chases the nearest it may catch (no tagging straight back for
  4 s), aiming a little ahead and bursting over the last two metres; the rest flee when it comes within 6.5 m --
  curving round along the green's edge rather than out of it -- and jog about or stand catching their breath when it
  is far. Long sprints tire a runner (6 s to spent, then 40% slower), so catches come every few seconds. Real run
  gait (people.js `run`, by species.js `runs`), the catcher laughs (speech.js vocal). Pure logic on the fixed sim
  tick from the children's state and a seeded stream, so deterministic; in the townsfolk-at-play herd (index.html extrasHerd: one draw shared with the juggler's and the bonfire's people),
  talkers (they chatter, can be greeted), home at night. YOU CAN PLAY: walk onto the green on foot and you are one of
  them -- it may chase you, and a touch makes you it ("You're it! Catch one of them"); reach one (85 cm) and they
  are it ("Got one! Now run"); walk off while you are it and the nearest child takes over. (Your part is local: a
  guest's children would go their own way from there.)
- **Pigeons** (pigeons.js): on nearly half the roofs a few rock doves (and the odd white one) sit along the ridge
  (architecture.js lifeOf exports each roof part's `ridges`: its top line end to end), bobbing their heads; every 35-90 s
  one takes off, wheels round over the lane on beating wings and lands back in its place; at night they sleep. One
  card a bird facing the eye (sitting: side view; flying: the shape from below), all from time and seeds on the GPU.
  STARTLED (`pigeons.scare({ x, z, r, delay })`): the bell's first strike, a near clap of thunder (under 3 km), the
  fireworks' first bangs (F), a thrown stone coming down within 14 m -- every pigeon in reach goes up at once, the
  ones nearest the fright first (it spreads at 25 m/s), round a wider, higher loop and home 10 s later, with the
  clatter of wings if you are within 45 m. One fright at a time (a uniform: where, how far, when).
  A second flock pecks about the MARKET SQUARE's paving round the cross (the same module on four short lines on the
  ground, `share: 1`): walk in among them (within 4.5 m, on foot) and up they all go, back ten seconds later.
  And in late autumn CROWS pick over the stubble of the grain fields (the same module, black, none white, three lines
  across each field): come within 9 m and up they go.
- **The smith's sparks** (sparks.js): while the smithy's smith is at the anvil (village-life holders carry their
  workshop's `trade`; a cooper's hammer throws none), every blow throws a spray of sparks -- out low and fast, arcing
  down, gone in half a second, brighter by night -- and rings the anvil (a struck-steel ting within 35 m). The blows
  keep the `hammer` gesture's own time: once a second on the world clock, landing three quarters into it; where they
  land is the smith's hand at that moment (index.html `anvils`).
- **Reeds** (reeds.js): 900 clumps where the banks of the river (and the lake) run into the water -- found by walking
  out from the water's middle to where the ground comes up out of it, then standing the clump in the last 1.2 m of
  shallows or 0.4 m up the bank. Three crossed cards a clump, five blades a card cut in the shader (tapering leaves; one
  in four a cattail: a stalk with its dark brown head), swaying with the grass's wind, straw-gold in autumn. One mesh.
- **Fish in the river, and leaps**: a world without a lake (a grown map) stocks its river instead -- 24 fish in its
  deep water (RIVERF = riverRange(.7): 70 cm or more, home the river's line) -- and its swans and ducks float on it
  (RIVER_FLOAT = riverRange(.3); before, with no lake they took the whole land for their range and waddled on the
  grass), a pair of swans and a flotilla of ducks. Now and then a fish -- or the lake's dolphin -- leaps
  clear in an arc, nose up and down (`an.pitch`), with rings where it leaves the water and where it falls back;
  when, from its place in the herd and the shared sim clock (LEAP), so every peer sees the same leaps.
- **Greetings**: walk up to someone -- within 4.5 m, facing them -- and they wave (the `wave` gesture, people.js,
  laid over whatever they were doing for 2.6 s) and say "hello!" in their own language and voice; walk off past 9 m
  and they wave you goodbye. Each greets you at most once a minute (index.html GREET, greetTick). While greeting (and
  while you stay close) the head turns to you as far as a neck goes (+-70 degrees, eased): `an.look`, the skeleton's
  head turn about the vertical, two fifths of it in the neck and the rest in the head (skeleton.js compiled `look`). The chatter and the
  greetings speak through one `utter(talker, figure, {text | vocal, mood})`: language, voice, distance law, pan, face.
- **The meadows' drifts** (cloudshadow.js `meadowPatches`, on the ground): the lawn is never one green -- broad drifts
  a little drier and yellower, others lusher and deeper, at two scales (~60 m and ~20 m), from the same smooth noise.
- **The wind by the weather** (grass.js WIND, `windAt()`): one strength for everything the wind moves -- the grass and
  its lawn texture, the grain, the leaves, the flags, the washing, the reeds, the chimney smoke -- a breeze on a fine
  day (.85), more in snow (1.3), rising with the rain (1.2, 1.6, 2.2: a gale in a storm), eased over a few seconds;
  the flags and the washing never blow backwards, a gale only snaps them harder.
  The rain slants with it (weather.js: steeper in a gale) and the snow is blown sideways once it rises past a breeze. Falling leaves and
  chimney smoke are carried further downwind the harder it blows. The windmill's sails turn with it too, lazily on a still day,
  racing in a gale (and the millwork inside with them).
- **Moss on the roofs** (architecture.js finishShade): weathered patches of dull green on every patterned face that
  slopes and looks up (a roof; never a ceiling, never a floor), more on the north side where the sun is short -- two
  octaves of the shared smooth noise, the moss keeping a third of the roof's own colour.
- **Cloud shadows** (cloudshadow.js): on a clear day soft shade patches slide over the land at the clouds' drift
  (1.5 m/s along +x) -- two octaves of smooth noise over the world's x/z, about a sixth of the land under a few
  clouds, a third under half, nearly half under many (O on a clear day), each 36% darker at its heart. One function
  (`landShade()`) on everything that lies on the land, so it darkens together: the ground, the roads, every building
  material (pattern, finish, plain stone) and the trees' leaves; none in rain or snow (the sky is grey all over) or
  after sunset. (The people and animals keep their light: small, and quick to walk out of it.)
- **Spray at the water wheel**: where its paddles strike the river a fine white mist puffs up and drifts downstream,
  all the time it turns (a puff every .12 s within 80 m of you; createPuffs again).
- **Dust behind the carts**: on a dry day (no rain, the roads dry) a rolling cart within 70 m of you kicks up dust
  behind each back wheel, a puff every .2 s drifting back and up and spreading (breath.js `createPuffs`, the same
  pool as breath on a cold day: brown, bigger, slower). One draw.
- **Raindrops splashing** (rainsplash.js): in rain, on the open dry ground within 10 m of you (not in a building's
  footprint, not on water), little crowns of spray pop up and are gone in a quarter of a second -- a ring of droplets
  thrown out and up and falling back, the drop's own jet, a ripple at the foot; a pool of 220 dealt round you again as
  each ends, as many in use as the rain is heavy. One draw.
- **Wet roads and puddles** (paths.js ROAD_WET, in the road's own shader -- no extra draw): rain soaks the roads over
  about a minute (faster the harder it falls), and they dry over four after it stops. Soaked, the packed earth darkens
  by a third and puddles spread in its hollows -- a smooth lumpiness over the ground, deepest along the wheel ruts,
  the water standing higher in it the wetter it is -- showing the sky's colour (the horizon's, by the hour), more of it
  the flatter you look across them (a puddle at your feet shows the mud), a darker rim of wet earth round each, and the
  drops' rings on them while it still rains (as many as on the river).
  The market square's paving takes them too (2026-10-23): one shader function for both (cloudshadow.js `puddleShade`,
  PUDDLE: the sky, clock and rain the roads' ROAD_WET shares), on the level faces of a finish rule that says
  `puddles` (town.js marketFinish: the paving) -- so the square's puddles fill and dry with the roads'.
  The same wetness (cloudshadow.js `WET`, which ROAD_WET.wet is) darkens the buildings: their roofs by up to 30%, walls
  by 10% -- outside faces only (archmat.js finishMaterial: not a room's inside, a ceiling or a floor).
- **Ducklings** (ducklings.js): behind every duck three to five ducklings swim in a line, each where its mother was
  a moment before -- her wake kept as a trail of points every 6 cm she swims (160 of them), the ducklings 38 cm apart
  along it, so they follow her curves and bunch up when she stops; bobbing on the ripples, at the water's height.
  Each is one card facing the eye, drawn in the shader side on and turned to the way it swims: a fluffy round body
  sitting low, a big head, a dusky back over a yellow face and breast, an eye stripe, a little bill. One draw for all.
- **Frost** (index.html FROST, late autumn): through the night the grass rimes white (the ground's snow input at .58,
  grass.js GROUND_SNOW -- the fringe's stalks whiten with it), forming over 2.5 minutes of dark and melting by morning.
- **Lying down to rest** (skeleton.js `an.rest`/`restT`, a species' `rest` in its asset -- cow, ox, sheep, ram .75; deer,
  reindeer, dog .7; camel, bactrian, pig .8: how far down it lies, a share of its legs' hip-to-foot length, skeleton.js
  `legLength`): the body is lowered so many metres and each leg's IK aims its foot as much higher, so the legs fold
  under it by themselves -- no new pose data. A herd animal of such a species lies down for some of its stops (REST:
  three in ten by day, most at night), head up instead of grazing, lowering itself slowly (.35 m/s) and getting up
  quicker (1.1 m/s) when it walks on; the shepherd's sheep lie down through his stops, four in ten (pasture.js `lie`).
- **Grazing**: a grazer standing between walks lowers its head to the grass -- its species' `graze` (radians, in its
  asset: horse and zebra 1.25, deer and reindeer 1.1, oryx and blackbuck 1.05, cattle and sheep 1, camels .7, pigs and
  boar .5, rhino .45; and nosing the ground: bear .6, dog .55, fox and wolf .45), eased down over a second or so and up again when it walks on (or you mount it). skeleton.js
  `an.nod` turns the neck about its root and swings the head -- hung beside it on the body -- about that same root, in
  the body's frame; an extra marked `"nod": true` (the manes along a horse's, a reindeer's, a giraffe's neck) rides
  down with them.
  The HENS in their yard peck: a bird with `peck` (radians) standing about dips every second or so on its own beat --
  the body tipping forward over its feet and the head down with it (skeleton.js: half the dip each; a neckless head
  turns about its definition's `nodPivot`).
- **An eagle hunting** (index.html HUNT, huntTick): every minute or so by day, one of the eagles within 140 m of you
  with a hare, a rat or a hen within 70 m below it stoops: a 2.6 s dive, faster and faster, onto where the prey is
  now (nose down: an.pitch), and a 4 s climb back to its height on the way it was going, then it soars on. The prey
  bolts as it comes down (shyStep: a hunting eagle is a threat once it is low). Its wanderer is frozen while it hunts.
- **Come for bread -- or just to look** (index.html begStep; a species' `beg`, metres, in its asset -- duck 16, swan 14,
  horse 12, cow and goat (ram) 10, pig 9, ox and sheep 8): stand still on foot for 2.5 s and the animals of those
  kinds within their range come over, turned to you -- the ducks and swans paddling to the bank, the livestock to
  their fence (their range: as near as it lets them) -- the nose 2.2 m from you (BEG.stop plus its half-length), and
  wait there, a call when they arrive and now and then after (BEG.call: a duck oftener than a horse); a lying cow
  gets up to come (and does not lie down at your feet). Take a step and they go about their business (or are shy
  again: shyStep). `youStill` is the frame's (frameBody: the camera unmoved 5 cm, not riding, swimming or resting);
  `__dbg.setStill`. And a splash brings the water birds too: where a skipped stone sinks (stones.js `land`), the ducks
  and swans within 22 m rush to the spot (index.html `lureBirds`: at 1.6 times their paddling pace, for up to 9 s) --
  it might be bread -- and, finding nothing, go about their business.
- **Shy animals** (index.html shyStep; a species' `shy`, metres, in its asset -- deer 14, oryx and blackbuck 14, wolf 13,
  reindeer and zebra 12, fox 11, boar 10, hare 9, beaver 7, duck and peacock 6, cat 5, rat 4, the hens in their yard
  and the frogs 3, the turtles 2.5):
  come nearer than that, on foot or riding (not flying over), and it bolts straight away from you at a gallop by its
  legs' length (v^2 = 25 x its gait base: a deer ~4.5 m/s, a hen ~2), swinging back toward the middle of its range
  where running on would take it out, and keeps running 3.5 s after you were last too near -- then walks on from
  there, its route replanned. Ducks flee across the water, staying on it. (Your camera, read in the sim's tick: local.)
- **The old** (index.html OLD, people.js makePerson `old`): one country walker in seven (not a child) is old --
  grey to white hair (OLD_HAIR; the seed's draws unchanged; and a child is never grey: GREY_HAIR), stooped a little from the hips (the chest held tipped
  forward 0.2 rad: skeleton.js an.pose), walking at .62 the pace, a walking staff in the right hand (tools.js, the
  `staff` gesture holding the hand forward so it stands clear of a gown); idle, they only look about, and in the rain
  they keep the staff down rather than their hands over their heads.
- **Carrying things** (index.html CARRY): one country walker in five (not the old) is on its way somewhere with
  something in hand -- a basket or a bucket hanging from it, a sack, a rake or a pitchfork upright (tools.js, the
  folk's holders; a child: a basket). With something in hand (`laden`: these and the old) a walker only looks about
  when idle, keeps it down in the rain, and greets you with a word but no wave.
- **Standing about** (index.html IDLE, idleTick): a wanderer stopped between walks, every 5-14 s, looks about (its
  head turned one way, then the other -- `t.idleLook`, which greetTick eases the head to) or for 2-4 s stretches,
  scratches its head or shades its eyes to look far off (people.js idle gestures `stretch`, `scratch`, `shade`, their
  strength `work` eased in and out over a third of a second); a child at tag who has stopped running out of breath
  puts their hands on their knees (`puff`). A greeting takes over at once. Display only, on the frame's clock.
  IN THE RAIN the people out walking hurry -- half as fast again (RAIN_HURRY, their gait clock with them, so the feet
  stay planted) -- with both hands held over their heads (`cover`, eased in and out), until it stops.
- **Washing lines** (laundry.js): ropes strung from an upstairs window to the one facing it across the lane (pairs of
  upper-storey windows of two houses, 4-10 m apart, facing each other, at about the same height; 16 at most), sagging,
  with the wash pegged along them -- sheets, shirts, breeches, stockings, cloths, in linen and the town's dyes -- each
  piece a 4x3 grid blown out of the line's plane by the grass's own gusts, more the lower it hangs; the shapes cut in
  the shader. One mesh for the wash, one for the ropes. The wash is taken in when it rains or snows and for the
  night (`update(t, out)`, 2026-10-24); the lines stay up.
- **Flower boxes** (windowbox.js): seven houses in ten keep a box under most of their windows (shutters, not glass;
  not a shop's wide opening): a plank box on the sill's outside (0.33 m out from the window's middle -- the walls are
  0.35-0.65 m thick) and two crossed cards of leaves and round blooms cut in the shader, all one colour a house
  (geranium, pink, daisy, violet, marigold, nasturtium), swaying a little in the grass's wind. Two meshes.
  In winter (foliage.js `SNOW`, 2026-10-24) the blooms go, the plants are cut back by a third and withered, and snow
  caps them; they had flowered red through the snow.
- **Window and door frames** (windowframes.js, 2026-10-24): every window on the glow's list gets jambs and a lintel
  standing a little proud of the wall's outer face and a sill reaching further out (the flower boxes sit on it), a
  flat-headed doorway its jambs and lintel -- in one colour a house (oak, weathered, or painted green, blue-grey,
  oxblood, white), pale stone round glass; an arched window its sill and a keystone at its crown (`FRAME.key`). One lit mesh for the town (`?frames=0` off).
  The boxes are wound by the wall's side (a left- or right-handed along-up-out frame): culled the wrong way round they
  hid inside the wall. A house's ROOF EDGES get boards too (`boards`, FRAME.board: 20 cm deep, upright): the outline of
  the roof's upper sheet but the ridge (architecture.js lifeOf `roofEdges` -- a shell roof is a closed slab, so its
  open edges are none; the up-facing triangles' outline is the eaves and the verges) -- a bargeboard up each gable, a
  fascia along the eaves, in the house's paint. The frames, boards, ridge tiles and chimney caps take the snow on their
  faces looking up (windowframes.js `snowyLit`, foliage.js SNOW): a bare terracotta ridge on a white roof read as a stripe.
  After rain they darken wet with the walls and roofs (cloudshadow.js WET).
- **Doorsteps and woodpiles** (2026-10-24): a door whose sill stands 5-50 cm over the street gets a stone step out in
  front (windowframes.js, `FRAME.step`, given `groundH`); and nearly half the houses keep a woodpile against the wall
  beside the door (index.html `WOODPILE`: split logs in courses, ends out, blocks.js logs, one lit mesh that takes the snow -- blockMesh may be given a material; propCols keeps you
  out of it). windowframes.js `wallFrame` -- an opening's along/out frame and a point off its wall -- serves both.
- **Cottage beds** (index.html buildFlora `BEDS`, 2026-10-24): under three in ten of the houses' ground-floor shuttered
  windows, two staggered rows of one tall garden flower along the wall -- foxgloves, irises, roses or lilies (the
  flower items) -- in the flowers' one batched pool, rebuilt with them by the season. The meadow's flowers keep off the
  sites, so there were none by a house. Never in a road, a wall or a prop; `?beds=0`.
  ALL the flowers (the meadow's too) and the woods' mushrooms are hidden while the snow lies (`SNOW` > .5, the tick;
  the mushrooms flipped only as the snow comes or goes) and cannot be picked then -- they had grown through it.
  The BUTTERFLIES fly only by day, in fair weather and with no snow lying (the gate in index.html, not butterflies.js,
  which keys the startup cache's wings: they
  had fluttered at night, in the rain and over the snow), and the bees stay in while snow lies; the swallows are gone
  south in late autumn and while snow lies, and no moths come to the lamps in the snow.
  The DUCKLINGS swim behind their mothers in spring and summer only, with no snow lying -- folded into their own
  near-you cull at the end of the frame (it set `visible` last, so a separate season check before it did nothing).
  No FALLING LEAVES drift down while snow lies (the crowns are bare): hidden after leaves.update, which shows them by
  distance.
  The WASHERWOMAN stays home while snow lies, as in the rain (she knelt at the icy river while the town's wash was in).
  On a river frozen hard (`iceFirm`: the skaters' ice) the WATER MILL'S WHEEL stands, its millwork with it, and no
  spray rises off it; the windmill's sails turn on. The fisherman's SKIFF stays at its mooring (one out when the ice
  firms turns for home -- boatStep); the ducks and swans already stand on the ice (floatY). (The harness pins the animation clock: checked by the ice state the
  gate reads -- `?ice=1` firm, open water not -- not by watching the wheel.)
- **Farm wood** (town.js, 2026-10-24): the yards' sheds (the hen house, the pigsty, the stable) are boards
  (`timber/boards`), their posts, fences and gates planed wood (`timber/wood`), and the longhouse's woodwork and the
  railings planed wood too -- all were `timber/bark`, which read as zebra stripes (the town houses' woodwork had
  moved off it earlier the same night). The shed rule sits after the hay, floor and ground rules: the first rule that
  matches a surface wins, and those are the sheds' own parts too.
- **Roof boards only in styled towns** (2026-10-24): the painted bargeboards and fascias (windowframes.js `boards`) are
  given only where the town is built in the styles (a period without its own `houses`, periods.json) -- on a Greek
  courtyard house's roof they crossed its corners as two broad white bands.
- **Bank places clear of trees** (index.html bankAt, 2026-10-24): the riverbank spots for the washerwoman and the
  stone-skipper are checked against the trees too (treeCols, which buildFlora has filled by then), with more places
  to try for the skimmer -- the placement check had found the skimmer under a tree in two worlds of three.
- **The drip line** (index.html `DRIP`, 2026-10-24): round every house's foot a .55 m strip of trodden earth where
  the eaves drip and feet go (the lawn had run right up to the stone). The wall's face is found per side by stepping in
  from the footprint (which reaches past the wall: eaves, a margin) with hitsBuildings at three places, the middle
  answer kept (a doorway's hole, a frame proud of the wall), plus CR (hitsBuildings asks round a body's width). In
  1 m pieces, each left out on a road, in another site or in the water; snowyLit under landShade.
- **The fields' edges** (index.html `SKIRT`, 2026-10-24): a tilled field's soil slab (village/field-* `soil`, 12 cm
  proud) had straight sides -- a hard box edge. A skirt of earth now slopes from its top edge out to the grass
  (`SKIRT.out` .45 m), corners mitred, snowyLit under landShade; laid at runtime, the cached fields untouched.
- **The landing's gravel** (index.html, 2026-10-24): the river landing's apron (village/landing `apron`) has no finish
  and showed one flat grey. A thin gravel sheet is laid on it at runtime -- 60 x 36 cells, its tone mottled per vertex
  (linear colours: the sRGB tone raised to 2.2), snowyLit and under landShade -- at the floor supportAt measures, so
  the cached building stays as it is (no pregen rerun).
- **Barrels by the shops** (index.html `SHOP_BARRELS`, 2026-10-24): seven shops in ten stand a barrel or two
  (items/furniture/barrel) against the wall beside their door, on the side away from the lamp; never in the
  carriageway; propCols (`by: "barrel"`).
- **Cats on the sills** (index.html `SILL_CATS`, 2026-10-24): a cat or two asleep on a ground-floor window's sill --
  shutters, no flower box (windowbox.js now returns its `windows`), lying along it (`an.rest`, in the extras herd),
  its coat by the seed; `?cats=0`. They go in out of the rain and the snow (roostTick, while out of sight).
  And one lies on the market's paving by the corner of the fish stall, waiting for scraps (a small propCol: the
  shoppers step round it).
- **Wayside shrines** (index.html `SHRINES`, 2026-10-24): two or three a world along the country roads and tracks
  (`from` 75 m out of the market, `apart` 70 m from each other), `side` metres off the road's edge and turned to it --
  by turns a stone pillar (a step, the shaft, a niche with its dark hollow to the road, a small roof, an iron cross)
  and a wooden wayside cross with a pale figure under a little roof -- a few flowers at the foot. Clear of the road,
  buildings and water; propCols (`by: "shrine"`); `?shrines=0`. A stone pillar's niche holds a candle that glows at night
  (`LITTLE_LIGHTS`, with the grave lights: after every other lamp; the light a little in front of the niche -- inside
  the stone the glow's shape cut through it). Only in a period whose town has a church
  (periods.json `church`): none in a Greek, Roman, Egyptian, Chinese, Ottoman or Islamic town.
- **Icicles** (icicles.js, 2026-10-24): while the snow lies (`SNOW` > .5) icicles hang along the houses' eaves -- the
  level roof edges (lifeOf roofEdges, the fascia boards' lines; not the gables' verges), a board's depth down, every
  ~20 cm with gaps, 7-55 cm long and thicker the longer they are, a little off plumb. One lit mesh (~2500 in a town),
  hidden the rest of the year.
  The same module puts SWALLOWS' NESTS under some eaves all year (`ICICLES.nest`: one eave in three, one to three mud
  cups -- half bowls against the wall's top under the board -- in a mesh of their own).
- **The churchyard** (index.html `CHURCHYARD`, 2026-10-24): up to 46 graves round the church on the ground it has free,
  in rows square to it between `near` and `far` metres out of its walls: headstones with rounded tops (a blocks.js
  log across the slab, its round faces stone), some leaning (`tilt`), crosses of stone or weathered wood, now and then
  a flat ledger, and a low grassed mound before each, flowers on some. Never on a road (offRoad), in a building (inSites), by the water,
  under anything (openStand) or in the forecourt at the church door (`door`: the wedding gathers there). One snowyLit
  mesh; propCols so walkers go round (`by: "grave"`); `?graves=0` leaves it out.
  About one grave in four has a GRAVE LIGHT (red glass under a cap) that the night glow lights after dark --
  `LITTLE_LIGHTS`, appended after every other lamp (the glow takes `LAMPS` at most: they never crowd out a carried
  lantern).
- **Stork nests** (index.html `STORK`, 2026-10-24): two house chimneys a town (chimneyTops carry `home`), picked by
  its seed, carry a stork's nest: sticks in four courses round the capstone (`RIDGE.cap`) and a darker bowl, made of
  blocks.js logs in one snowyLit mesh, with a pair of storks (items/birds/stork, `pose: folded`) standing in it -- the
  mate turned well away from the other, and keeping the nest while it flies. A nested
  chimney gets `nest`, and smoke.js passes it over (a cold chimney). The nests are not in the sun-shadow bake.
  Every `STORK.cycle` seconds (offset per nest) the stork flies for `STORK.flight` s (storkTick): up off the nest
  along a curve to a circle of `STORK.ring` (radius, height) that passes over the nest, `laps` times round, then
  down again (by day and dry only: at night and in the rain both keep the nest); in late autumn and in winter (`SNOW`) the nest is empty -- they are away south. The standing item is hidden and a second item in `pose: spread` flies, yawed along its path, pitched
  with the climb and banked into the turn (eased).
- **Ivy** (ivy.js, 2026-10-24): nearly half the houses' plain doors (`IVY.share` .45) have ivy planted on the side
  away from the woodpile (`d.pile`). From the root its stems wander up the wall and branch to the sides (`IVY.branch`).
  They go round the door and the house's windows on that wall, which are boxes with a margin, and stop where the wall's
  face ends. That edge is found by probing: frameDoors carry `probe(x, y, z)`, the same wallOuter ray, so a corner, a
  jetty's overhang or the eaves ends them. The leaves are three-lobed polygons, the older ones bigger and the young
  ones at the stems' ends a fresher green, tilted off the wall on their stalks. Their tips stir in the wind (a
  positionNode, `flex`). Leaves and stems are one snowyLit mesh each; ?ivy=0 leaves them out.
  Arched doors get it more often (`IVY.arched`: the church's, a merchant's), with a taller margin over the arch. A
  door's wall lamp (frameDoors `lamp`, from index.html `hasLamp` -- the same rule createWallLamps uses) is kept
  clear, and a stem that reaches the top ends there, under a top that is ragged along the wall.
- **Board shutters** (index.html `shutterGeometry`, 2026-10-24): the unit box each shutter is stretched from carries two
  ledges across and a Z-brace between them, a shade darker, proud on both faces (a shutter opens back against the wall:
  either face is seen) -- it was a plain slab.
- **Grime at the wall's foot** (archmat.js `GRIME`, 2026-10-24): an outside wall darker and a little green to knee
  height, its top line ragged -- by the pattern's v, which is the height over the building's ground for a pattern laid
  from the ground (not for one laid from each part's foot, `align: part`: no grime there). Faint RAIN STREAKS run down
  those walls too (`GRIME.streak`: a noise narrow across the wall, long down it, stronger low). (And the roofs' moss
  now mixes into what is already there -- it mixed from the bare colour and would have wiped anything before it.)
- **The sun's shadows** (sunshadow.js, 2026-10-24): the sun is static, so the buildings are drawn ONCE from it, after
  they are built, into two depth maps (an orthographic camera along LIGHT.dir, every caster on layer 7 with one plain
  override material): a FINE one sized by the town's core (the sites within `SUN_SHADOW.reach` 200 m of their middle:
  3072 texels, ~11 cm) and a COARSE one over every building (2048, ~40 cm: the mill, the farms, the windmill). The fine
  map draws every building too -- its square reaches past the core's circle, and a mill standing in it undrawn cast
  nothing (the fine map wins wherever it reaches); the coarse one is read, one filtered tap, only outside it.
  `landShade()` (cloudshadow.js) multiplies `sunShade()` in -- the ground, the roads, the walls, roofs and paving -- and
  the figures' shells too (shell.js, with their own world position and normal): four filtered comparison taps (fine), and in
  shade Lambert's direct share of the light taken off (times `depth` 1.5, at most .55 -- the world's high ambient left
  a shadow at Lambert's alone a smudge). Faint under a grey sky, none by night (`SUN.k`, set with the clouds'
  shadow). `?sunshadow=0` off. Trees do not cast (their shade blobs do that). The WATER takes them too, softer (.7 of
  the land's: what it mirrors is not shaded) -- the bridge's shadow lies across the river under its arches.
  **Figures cast too** (shadows.js, `SHADOWS.cast`): each figure within 40 m standing in the sun gets, besides the
  shade under it, its own sun shadow -- an ellipse from its feet away from the sun, as long as its height (composite.js
  `an._y1`) over the sun's slope, as wide as it is across that way, as strong as `SUN.k`. "In the sun" is read on the
  CPU (sunshadow.js `sunAt`): the fine map's view drawn once more at 1024 texels with its depth as colour (an RGBA
  float target -- a one-channel one drew nothing; no scene background for it, or the sky was its clear) and read back,
  rows as the shader samples them (v down) -- so nobody casts a sun shadow indoors or in a house's shade. Its edge is
  crisper than the shade under a body (`blobH` 1: the fall-off from .82 of the ellipse out, not from half). The carts
  cast one too (a body's `high`, 1.6 m by default).
  **Trees cast too** (index.html buildFlora, shadows.js `createShadeBlobs` `sun` blobs): besides a lighter shade right
  under the crown, the crown's own shadow -- an ellipse cast away from the sun as far as the crown stands high (`AWAY`,
  `SLOPE`), firm-edged, fading with the sun on the GPU (`blobSun` times SUN.k: none by night, faint under grey skies).
- **Ridge tiles** (ridgecaps.js): a row of half-round tiles along each roof ridge in the roof's palette's second
  colour (lifeOf records the ridge's `part`; index.html roofRuleOf finds the finish rule over it), each tile's lapped
  end darker; a thatch gets a thick roll. A HIPPED roof's hips are tiled too (lifeOf `roofHips`: an edge two up-facing
  slopes share at a crease that climbs -- the stone houses', the gatehouses' pyramids, the longhouses' hipped ends;
  ridgecaps.js follows a line from `ya` to `yb`; the pigeons perch on the level ridges only). Every chimney's top a capstone a little wider than the stack over a darker
  brick course (`RIDGE.cap`).
- **Leaded glass** (archmat.js `leadedGlass`, `LEAD`): glazed panes in diamond quarries, the lead opaque and dark, the
  glass faintly blue; an arched pane by its geometry in metres, a box pane by its uv. At night a lit glazed window shows
  the same diamond leading against the room's light (nightglow.js reads archmat.js `LEAD`; it drew a plain cross of
  bars), its light cut to a round head where the window has one (glowWins `arched`). The glass catches the sky by
  Fresnel (little square on, much at a glance) and each quarry a little askew, so the sky in it varies pane to pane.
- **A murmuration** (murmuration.js): 800 starlings over the farms' fields, ~34 m up, flying as one cloud that folds,
  stretches and ripples while it wanders over the land -- by day and at dusk (gone to roost once it is dark). Each
  bird is a chevron of two flapping wings turned along its own flight; where it is comes from the time and its three
  seeds alone (flockPos, WGSL), its heading from where it will be 0.12 s later. One draw.
- **Lamps and fireflies** (nightglow.js): a scene of its own drawn AFTER the tint, with the world's depth, so it
  keeps its brightness and walls still hide it. Most houses have a lamp burning: the light leaks round a closed
  shutter's edges, down the crack between its leaves and through the heart cut in each; an opened shutter or glass
  shows the room's warm glow and its glazing bars; each lamp breathes, and they come on one by one as the dusk
  deepens. Now and then SOMEONE INSIDE crosses the room in front of the lamp -- every 25-55 s a window, each on its
  own clock (its one phase: drawn once a window, not per corner, or it ran across the pane) -- a head and shoulders
  gliding past the glass in 3.2 s, bobbing as they walk, a dark shape across the light between the shutters too.
  Fireflies blink over the grass, more along the water (not in rain, snow or deep autumn).
- **Lanterns**: villagers out after dark (walking home, to the inn) carry a lantern in the left hand -- two in three
  of them (village-life `holders`, the lantern item in tools.js) -- and nightglow.js draws a halo round each and a
  pool of warm light on the ground under it (`setLamps`, 48 at most, placed every frame from the hands) -- and the fisherman's skiff carries one at its stern, its light on the water.
- **Splashes**: your feet going into water -- striding in from the bank, or jumping off the bridge -- make a splash
  as big as you came in hard (stones.splash: a ring, spray, a plunge); wading or swimming, a ring spreads from you
  every half second while you move.
- **Fireworks** (F, fireworks.js): a show of 12-18 rockets over the town in about half a minute, the last few close
  together: each climbs from the ground slowing to its top, then bursts into a PEONY (a sphere of stars), a RING
  (tilted, upright-ish) or a gold WILLOW that hangs and droops; stars white-hot, then their colour, crackling out.
  All on the GPU (a pool of 18 bursts x 150 stars: drag and gravity in closed form; the CPU writes a burst's numbers
  at launch), in the night-glow scene -- drawn whenever a show is on, day or night. Sound where you stand: the
  whistle, the BANG late by distance / 343 m/s, the crackle after.
- **Lanterns under the market's awnings** (nightglow.js `createHangingLamps`, index.html): a lantern on a short chain at
  the front of each of the market's eight stalls (from the market asset's own `stall` parts: where each stands and
  which way it faces the square; 1.75 m up under the valance), one block mesh, its lights joining the wall lamps' list
  (wallLamps) -- the night's glow lights them, a pool on the paving, and moths come. The lantern itself is one helper
  (`lantern`) shared with the wall lamps.
- **Moths** (moths.js): round each of the ten lanterns nearest you (within 40 m: the wall lamps, the lanterns carried,
  the watchman's, the skiff's -- the frame's own lamp list) four pale moths flutter in erratic loops, in close to the
  light and out, beating; tiny bright cards in the glow scene. Not in the rain.
- **Wall lamps** (nightglow.js createWallLamps): an iron lantern on a bracket beside the door of the inn, the church
  and every shop (town.js sites carry their `trade`), horn panes pale by day; at night they join the carried lanterns
  in the glow's lamps (setLamps, 72 at most): a halo and a pool of light on the step.
- **Skipping stones** (G, stones.js): a flat pebble thrown low over the lake or the river skims while it comes in
  shallow and fast enough, each touch costing a fifth of its speed and kicking up spray and rings; too steep or too
  slow and it sinks with a plunk. The skips are counted (and your best for the visit). The rings are a public
  `stones.ring(x, y, z, strength)` for anything else that touches the water.
- **Chimney smoke** (smoke.js): the chimneys of the lit hearths (a building's `chimney` part: its top, lifeOf
  `chimneys`) smoke all day -- soft puffs placed by the GPU from the time alone, leaning with the grass's wind,
  growing and thinning as they climb; more on a cold day (snow, autumn). One draw for the town. Seven chimneys in ten
  smoke all year (`SMOKE.lit`, each chimney's `warm`); the rest light up only while the snow lies (2026-10-24: every
  hearth burning in winter), their puffs shrunk to nothing the rest of the year so they cost no overdraw.
  The farm LONGHOUSES have no chimney: their hearth smoke rises through the thatch at the middle of the ridge
  (`smokeHoles`, handed to createSmoke beside the chimneys but not chimneys -- no capstone, no stork's nest).
- **I** season: summer → half → full autumn → SPRING (flora rebuilds in place; `?season=spring`). In spring the
  deciduous leaves are the first pale yellow-green (flora.js SPRING_GREEN, by each card's own tint) and the orchard
  trees are in blossom -- apple pink-white, cherry white (a species' `blossom`): the fruit's places flower and half
  of each crown with them, drawn as clusters of dots, and their PETALS drift down round you (leaves.js, 240 at a time, from the trees in flower only: a tree's `bloom`); a fruit bush's berries are white flowers. No fireflies in late
  autumn; the mist thicker and the smoke more in autumn, not in spring. Leaves FALL from the trees within 45 m of
  you (leaves.js): 60 at a time in summer, up to 720 in full autumn, in the season's colours -- each from one tree's
  crown, swinging like a pendulum, spinning, drifting with the grass's wind, then lying flat five seconds and fading;
  dealt again to a tree near you when it has gone (the CPU writes four vertices; the fall is the GPU's, from time). In spring the YOUNG are out (index.html
  YOUNG; a species' `young` in its asset: { s, n, side, hop, name }; species.js makeYoung, scaled whole by geom.js
  `scaleDef`): the shepherd's first two ewes (else the meadow's) have TWIN LAMBS at their sides, two mares a FOAL each,
  a cow a CALF -- trotting with her, now and then gambolling a quick circle round her at a run, springing up off all
  four feet every few seconds (a lamb high, a calf hardly), and lying down by her side when she lies down.
- Underwater (below the water level over carved ground: lake, river or
  moat), the whole view washes blue-green with drifting light bands.

## Interactions

At most one action is available at a time, shown bottom-center:

- **mount / dismount** — click a loose horse within ~1m while looking at
  it. The camera sits at the rider's head (2.35m), movement drives the horse
  at double speed, its legs trot in step; click again to dismount.
- **lie down** — on a bed you lie flat: peers and your Shift+N copies show
  the lying figure (pose "lie" in `people.js`), not a seated one.
- **fly** — the dragon, the manticore and the hydra are mountable too
  (visit the monster pen). On a winged mount **E** climbs and **Q**
  descends (running, Shift on/off: faster); in the air gravity is off, the mount never
  sinks below the ground it crosses, walls still block, and it moves 1.5x
  faster. In flight the wings beat on their own clock and the legs hang
  still, while head and tail keep the pace of movement (faster with
  Shift, as on the ground); on the ground the legs trot and the wings
  rest folded. Landing
  is holding Q down onto support; dismounting needs solid ground. Peers
  see a flying mount beat its wings from the pose altitude alone.
- **pick up / put down** — a barrel or sack lying on the quay, in a yard,
  on the ground, on a cart bed or on the barge's deck offers "click to pick up"
  (not one a dock hand is already heading for); you carry it in front of you
  (it rides carts and the barge with you) and "click to put down" sets it
  on whatever is in front of you. A piece in your arms is out of the
  chain until you drop it; drop it on the quay rows and the carts take it.
- **open / close** — every building exports its doorways and its windows
  (all storeys, palace included); a hinged panel swings ~110° on click.
  Closed doors are genuine walls. Glass was a luxury: only buildings
  flagged `glazed` (the palace, the church) have glass panes, every other
  window is a wooden shutter. All panes share two InstancedMeshes (glass,
  shutters): each hinge is a bare transform whose matrix feeds its
  instance when it swings, so hundreds of openable windows cost two draws.
- Stairs whose one side is open carry a balustrade along the flight (a
  baluster per step, close enough to stop the walker, plus the handrail);
  the top landing stays open so you can step off, and stairs against a
  wall need none. Stairwell openings in upper floors are railed the same
  way (`wellRail`): the drop edges get posts and a rail, the landing's
  stretch stays free.

## The bow (archery.js)

B takes the bow out or puts it away (a counter shows the quiver, 24 to
start). With it out the mouse is the bow: hold to draw (~0.8 s to full
draw, the view closing in a little, the player's own body in the draw
pose with the bow in its left hand), release to loose, right button to
lower it; clicking a stuck or fallen arrow close by takes it back. An
arrow leaves at 14-50 m/s by the draw (the square root of it: a half draw
already carries it past 100m, a full one about 240m at 45 degrees, as a
real war bow), falls under gravity with a little
drag and is traced every frame in steps of at most a metre against the
ground, the water, the buildings' colliders (only the sites its path
crosses), tree trunks, moving decks and every composite figure (a
bounding sphere, then each part as a capsule). It sticks where it hits,
a little way in: still targets keep it in the world; a cart, the barge
or a figure keep it in their own frame -- a figure's in the very part it
struck -- so it goes along. In water it floats a while and is gone.
People and animals are struck alike, no reactions yet. All arrows are
one InstancedMesh; the twang and the impacts (wood, body, earth, splash)
are synthesised once. A shot is sent to peers (op `arrow`), who fly it
too.

## Tableware (tableware.js)

The inn's mugs and jugs and the food on its plates are not building parts
but data the building exports (`vessels`, `dishes`), built as separate
objects because they change: each vessel an open stoneware shell (seen
into) with a floor and the drink inside as a disc at its level -- 90%, 60%
or 30% of the way up, or none when empty (dealt out in turn; ale in mugs,
ale or wine in the jugs), the disc as wide as the inside at that height.
Within reach and looked at -- standing, or seated at the table (the drink
comes before "stand up": look away to rise) -- a click drinks one level
down, or eats the bread, cheese or sausage off its plate. Both go to peers
(ops `drink`, `eat`). Water vessels are the same thing: the fountain's two
buckets on its rim and the stable yard's stone trough (a box vessel, an
unseen solid box keeping you out of it) show their water at the same
empty / 30% / 60% / 90% levels and can be drunk from.



## A rider is parted once (2026-09-25)

A rider on the tour is ONE figure -- the horse's parts and the man's, fused in a single def -- so a blow has to
part it: the struck one falls and the other goes on (the horse riderless, the man on foot). `onStrike` decides
whether the figure it was handed is still that fused one, and the test used to be a count of parts: more parts
than a horse has, so it must be horse-and-man. It is not. A man in a hat with a braid has thirty parts and a
horse twenty-five -- so felling the horse and then shooting the man who walked on parted him a second time,
and a fresh horse appeared out of nowhere under him.

The rider now remembers the figure it was MADE as (`fused`), and only that one can be parted; parting clears
it. `ref/rider.html` shoots both orders and counts the figures in the world: the first blow adds two (the horse
and the man, the fused one hidden), the second adds none.
