# Plants: trees, bushes and flowers

The world's trees, bushes and flowers are GROWN at load from species data, MESHED at a few levels of detail, and
PAINTED into textures on a canvas. There are no model or image files. The engine replaced the old `makeTree` and
leaf cards of flora.js and foliage.js, and the flowergen items, on 2026-11-18. The aims: a realistic forest of about
a thousand trees at about 5,000 triangles a tree nearest, see-through leaves only up close, and leaves baked into
textures everywhere else.

    assets/plants/      the species DATA: trees/*.json, bush.json (with its fruits), flowers/*.json -- shown and
                        edited live in the asset manager (assets.html, "Plants")
    plants/species.js   the species' parameters documented, and the JSON turned into the engine's form (speciesDef)
    plants/grow.js      a skeleton from a species and a seed: branches (polylines with radii), twig sprays, prickles
    plants/mesh.js      a skeleton into triangles: wood tubes, spray cards; per level of detail
    plants/bake.js      the textures: bark (albedo + normal), each species' spray atlas (sprays, flower, fruit, filled)
    plants/render.js    the PLANT FIELD: kinds, variants, instancing, culling, LOD cross-fade, the WGSL shaders
    plants/flowers.js   the flowers: thirteen kinds grown and painted, one atlas, one material
    grove.html          the lab: every species twice, the bushes, the flowers in a row and a meadow; ?forest=1000,
                        ?kinds=olive,yew (only those species), ?lod=0/1/2 (one level forced)
    tools/pshot.py      headless screenshots, timings and a JS profile (see its docstring)

## The trees

`species.js` documents every parameter in its header. There are 38 species:

| habit | what it is | species |
|---|---|---|
| broad | a trunk forking into leaders | oak, maple, apple, cherry, yew, olive, plane, horse chestnut (`chestnut`), jacaranda, acacia, citrus, linden, persimmon, paulownia, avocado, cacao, flame tree (`delonix`), silk tree (`albizia`) |
| excurrent | one leader to the top | birch, pine, spruce, cypress, magnolia, tulip tree (`tuliptree`), monkey puzzle (`araucaria`), ginkgo |
| weeping | broad, the outer levels hanging | willow |
| palm | a bare bole and fronds | date palm (`palm`), coconut palm (`coconut`), fan palm (`fanpalm`), banana (its paddle leaves are fronds, torn along their veins) |
| bottle | broad on a swollen bole | ceiba (*Ceiba speciosa*), baobab |
| forking | forks of forks, sword-leaf rosettes at the ends | dragon blood tree (`dragon`), Joshua tree (`joshua`) |
| shrub | stems from the ground | oleander, hibiscus, hydrangea, rhododendron, hazel, grapevine (`grape`), kiwi vine (`kiwi`), bamboo (canes), the bush |
| column | a ribbed cactus column and its arms | saguaro |
| pads | flat pads grown from each other's rims | prickly pear (`opuntia`) |

A tree also has a trunk (radius, taper, root flare, buttresses, lean, S-sway, fork, bulge, prickles, `gnarl` for a
contorted olive or yew), a crown envelope and asymmetry, and up to three LEVELS of branching (count, spacing, angles, spiral or whorls, length, radius, gravity, phototropism,
wiggle, sympodial kinks). Its TWIG is the spray painted at the ends.

`grow.js` walks the trunk, then each level's children along their parent within the crown envelope. Each branch bends
under gravity, turns up toward the light, wanders, and sometimes kinks. The deepest level is not wood but twig sprays:
each card is one painted twig with its leaves, placed and turned where that twig would grow. The leaves therefore
follow the branch structure, clumped at the shoots' ends, rather than being scattered over a sphere. Nothing is
symmetric: the crown leans to its light side (`asym`), has gaps and dead snags, and every variant is a different seed.

A FORKING tree (`fork` instead of levels) runs its trunk to `trunk.split.at`, then forks in two (sometimes three) for
`fork.depth` rounds, each shorter (`ratio`); a Joshua tree's arms stop early at random (`stop`). Every last shoot ends
in a ROSETTE: `twig.cards` crossed cards turned round its tip, each painted with a fan of sword leaves radiating from a
point `twig.mid` up the card (bake.js `rosettePaint`; dead ones hanging, `dead`). All the forks are level 1 wood, so
the far levels, which drop level 2, keep the arms the rosettes sit on.

A COLUMN (the saguaro: `grow.js columnCactus`) is one column, rounded at the top in a few closing rings, with `arms`
that leave it level (pinched where they join), turn up through an elbow and rise beside it, never above its top. Its
wood is meshed with RIBS (`trunk.ribs`, standing out `ribA`): a crest and a groove a rib near, the crests alone
further; the bark tile is one rib across (bake.js `cactus`: areoles and spines down the crest), and its rings are at
its own points, dense round an elbow, so a 16-ribbed saguaro stays within ~4k triangles. `trunk.stiff` takes most of
the wind out of it. A rosette card crowns each top: its felt and spines, flowers in May, red fruit after.

A PAD cactus (the prickly pear: `grow.js padPlant`) is a short woody stem with pads on it, each pad growing more from
its upper rim at its own angle, a few deep. A pad is a card (bake.js `opuntia` paints the oval it is grown on) but
FLAT: its corners are meshed where they are and never turned to the eye or fluttered, and the far levels keep every
pad -- they are its body, not its leaves.

A BANANA's bunch (`crown.bunch`) is not painted on a card -- too big and solid for one -- but BODIES: grow.js `bunch`
grows tubes (`sk.bodies`: the stalk bowing out of the crown and hanging, hands of fingers spiralling up it and curving
to the light, the bare rachis, the purple bud), mesh.js `bodyMeshes` meshes them with the fronds at every level
(fewer sides and rings further off, widened to keep their outline; ~1-1.5k triangles of a banana's 3-4k), in
swatches bake.js `paintBodies` paints into the atlas's last column (a palm has no far cards). Their uv is the
atlas's own (`aTone.w` -1: render.js `cardUv` takes it as it is). A bunch is there all year.
A PALM's crown takes its shape from a few numbers (species.js): `rise` (the fronds' angles, oldest to youngest),
`droop`, `fold` (the leaflets' V: below 0 they hang, as a coconut's do) and `fan` (a fan leaf: a bare stalk for that
share of its length, then a round pleated blade, its width mesh.js `FAN_W`, which bake.js `fanLeaf` paints to the same
outline). The fronds spring from round the trunk's rim, whose tip is blunt. A fan palm's `skirt` hangs the dead
leaves flat down the trunk under the crown (painted dry in the atlas's second column), and a coconut's `nuts` are
bodies like the banana's bunch: green-to-orange ovoids in bunches under the fronds, there all year.
A CACAO's pods (`pods`) are bodies too: grow.js `pods` hangs ridged pointed pods on short stalks from the trunk and the
big limbs (not the twigs: cauliflory), yellow, maroon and green; a tree with bodies and far cards has a sixth atlas
column for their swatches. They too are there all year.

Where they grow: `assets/world/periods.json` names each world's trees (olive, oleander and grapevine in Greece; plane,
grapevine and hazel in Rome; acacia in Egypt; citrus, grapevine and banana in the Islamic world; banana and bamboo in
India; jacaranda and prickly pear with the Maya; bamboo and rhododendron in China, with hydrangea in Japan; yew,
linden and hazel in medieval Europe and Russia; horse chestnut, plane, magnolia, linden, tulip tree, monkey puzzle and
rhododendron in industrial Europe; persimmon and paulownia in China and Japan, with silk tree and kiwi in China; cacao
and avocado with the Maya; the flame tree in India; the silk tree in the Ottoman and Islamic worlds; coconut and hibiscus in India, ginkgo in China and Japan, hibiscus in China, the fan palm in the Islamic world and industrial Europe, with ginkgo). Baobab, dragon blood, Joshua tree and saguaro are in no world yet: the grove and
the asset manager show them.

## The levels of detail and the draws

| level | distance (scaled by the tree's height) | wood | leaves |
|---|---|---|---|
| 0 | under `PLANT_LOD.near` (34 m for a 15 m tree) | everything, fitted into the budget | every spray as an alpha-to-coverage card |
| 1 | under `PLANT_LOD.mid` (120 m) | trunk and limbs | 30% of the same cards, 1.15× bigger, filled spray |
| 2 | beyond | trunk and big limbs on few sides | 16% of the same cards, 1.3× bigger, filled spray |

A FAR LEVEL IS THE SAME TREE with details left out (mesh.js `FAR_CARDS`): its cards are a share of the near level's
very cards (the same thinning: `levels` passes the near level's `maxCards`), the outer ones first, each in its own
place and slant, grown about its middle so the crown keeps its outline, and painted with the FILLED spray (atlas
column 4: the spray laid over shifted copies of itself, so it is nearly solid and a far crown needs few layers). The
wood drops the twigs, then the thin branches. Until 2026-11-18 the far crowns were camera-facing clumps painted from
the skeleton: cheaper in pixels, but a different tree at every switch.

Levels cross-fade over a dithered band (`fade`), so they never pop. LEVEL 0 IS BUDGETED at `TRI_BUDGET` (5,000)
a tree: the leaves are meshed first, and `woodMesh` gets whatever is left (at least 1,200), coarsening its rings and
then dropping the thinnest twigs until it fits; if wood and leaves still overrun, the leaves are meshed again with
fewer cards (`levels`), never fewer than `MIN_CARDS` (15% of the budget: a bamboo's hundreds of side shoots once
left its leaves nothing). Every variant of every species is within 5,000 (the largest: maple 4,949, oak 4,996).
The cards of DROPPED TWIGS are moved (mesh.js `rootCards`): each is based where its twig left the nearest branch still
drawn and reaches toward where its tip was (grown up to 1.5x), swaying with that branch -- before, they hung in the
air where the twig had been (a yew drops nearly all of its; oak, plane, linden, chestnut many).

A KIND (a species, or a bush) grows `PLANT_LOD.variants` (3) skeletons. An instance is a variant placed with its
own yaw, scale, tint and wind phase. The DRAWS:

- wood and leaves are drawn apart, with two shaders. One merged shader halved the draws but cost the GPU half again:
  every pixel sampled both textures, and the leaves' discard cost the wood its early depth test.
- level 0: one draw per variant (they are heavy).
- levels 1 and 2: one draw per kind for all its variants, each instance carrying its variant in its phase
  (`PHASE_SPAN`). The WOOD's meshes are joined end to end, each vertex tagged with its variant (`aWind.z`), and the
  vertex shader sends the other variants' points out of view. The far CARDS are PULLED (render.js `pullBuffer`):
  every variant's vertices in a storage buffer, padded to the longest, and the draw runs only that many, each vertex
  reading its own instance's variant -- joined, every instance ran all three variants' cards, about 2 ms of a dense
  wood's GPU time, nearly all of it on vertices sent out of view. All far cards are quads, so one index serves all.

WebGPU allows 8 vertex buffers. The meshes use 6 and the instances 2, so anything new has to be packed into an
existing attribute.

CULLING is by 48 m cells (a sphere each, frustum-tested), then by instance. Only level 0 draws into the grass mask
(`NOGRASS_LAYER`), because the grass fringe is gone before level 1.

CARDS ARE TRIMMED to their paintings (bake.js `trims`): a spray card's quad is cut to the rectangle round the
sprays' paintings. The atlas is therefore baked BEFORE meshing (`grow`: skeletons, then `K.atlas`, then the meshes).

Measured (headless Chromium, this machine's integrated Radeon Vega (Renoir), 1280×800; `index.html?seed=353465086&
period=medieval&trees=1000`, standing inside the densest wood (74 trees within 40 m), three views; 25 s for the world
to finish streaming, then the plants' group shown and hidden in turn four times, medians -- single readings drift by
several ms while terrain tiles still load):

| view | GPU hidden → shown | CPU hidden → shown | draws |
|---|---|---|---|
| 0 | 19.0 → 28.4 ms | 21.6 → 30.1 ms | 839 → 910 |
| 1 | 15.8 → 21.8 ms | 15.1 → 20.3 ms | 554 → 616 |
| 2 | 12.3 → 16.2 ms | 12.9 → 16.0 ms | 425 → 489 |

(With the far clumps and the near cards fixed in space the GPU's share was 7.8 / 5.1 / 3.8 ms: the near cards
turned to the eye cost ~2 ms at view 0 -- a card seen edge-on covers no pixels, one turned does.) So the plants add
4 to 9 ms GPU and 3 to 9 ms CPU at the worst spot, on a world that already takes 13 to 21 ms
without them on this machine. The CPU part is three's per-draw cost: about 0.1 ms per plant draw (near meshes and far
meshes alone cost about the same; the grass-mask pass little), so the lever there is FEWER DRAWS -- each kind in view
adds up to 2 far draws and 2 near draws a variant. The grove with 1,030 trees (`?forest=1000`) runs at 60 fps (vsync),
~0.37 M plant triangles.

The plants are FILL-bound, not shader-bound: a cheaper leaf fragment changed nothing, and the near distance
(26 vs 34 m) changed nothing measurable. What costs is pixels covered by cards (when it was measured: L0 sprays
about 55%, the old clumps 25%, wood 15%) -- and, for the far levels, their vertices (above). A depth prepass was
judged useless for that reason.

## The textures

- BARK: a tileable height field per species (plates, ridges, fissures, rings, lenticels), turned into an albedo
  and a normal map and sampled in each branch's own frame. Recipes (bake.js `BARK`): furrowed, fissured, ridged,
  pine, scaly, stringy, flaky, birch, banded, palm, ceiba, smooth, yew (shedding strips), plane (camouflage patches),
  olive (twisting fissures), baobab (smooth folds), shaggy (a Joshua tree's dead-leaf thatch), cactus (a saguaro's
  rib, a tile across), banana (rolled sheaths, dry blotches), bamboo (a node ring and its white bloom a tile), ringed (a palm's frond-scar rings, fine vertical cracks).
  Leaf outlines (bake.js `leafPath`) include `toothed` (hydrangea), `fan` (ginkgo: a notched wedge), `heart` (linden, hazel), `vine` (grapevine) and
  `tulip` (the tulip tree's, cut square at the tip).
- SPRAYS: an atlas per species, 5 columns of 256×512. Columns 0 and 1 are two sprays in leaf, column 2 the spray
  in flower, column 3 in fruit (a leafy one where the species has none), column 4 column 0's spray FILLED (the far
  levels' cards: drawn over copies of itself shifted round a 7 px ring, a little darker, so its gaps close with its
  own leaves). The far cards show the flower and fruit cells as the near ones do. An apple both blossoms and bears, so the two need cells of their
  own: with one shared cell the blossom took it and the apples never showed. Every species bears something: where
  its spray recipe paints no fruit or flowers of its own, bake.js `OVERLAY` lays them on (acorns, cones, catkins,
  maple keys, dates, the ceiba's pods, the horse chestnut's conkers, the dragon blood tree's berries). Clear texels are bled with
  their neighbours' colour (`bleed`), so mipmaps pull in no dark edge.
- FRUIT (bake.js `fruit`): a ball whose shadow side is a deeper tone of its own colour, never toward black (an orange
  shaded to black read as brown), with its look by spray style (`FRUIT_LOOK`): an orange's pitted peel and green calyx,
  an apple's red blush streaked over a yellow-green ground with pale specks and a stalk in its dimple, a cherry's
  gloss, an olive's or a date's length, a grape's (and a baobab pod's, a linden nutlet's) dusty bloom. Sized to life
  at the card's scale (~2.5 mm a texel on a 1.3 m spray: an orange R 16). A grape `bunch` has a shoulder, uneven rows
  and gaps; a prickly pear's fruit is a barrel with a sunk top and glochid tufts.
- BUSH FRUIT: all bushes are one kind. Berries are painted in `FRUIT_MARKER` magenta and recoloured in the shader
  from an 8×1 palette by the instance's fruit slot, which is packed into its tint.

## The shaders

The world's one sun (light.js `lightWGSL`), cloud shadows, and snow on what faces up apply throughout.

- LEAVES are lit by the CROWN's normal (out from its middle), bent toward the card's own, so the crown reads as one
  mass. The sun shows through when it is behind a leaf.
- AUTUMN turns a share of the cards (each by its own random) to the species' autumn colour, keeping the painted
  light and dark.
- BARE and snowy seasons drop the deciduous cards.
- BLOOM (or a species' `flowers` in their season) shows the flower cells on a share of the sprays,
  FRUIT the fruit cells on another (each card by its own random, flowers winning): a tree can be in both.
- NEAR CARDS (render.js `cardCorner`): a card's corners sit on its midline (mesh.js leafMesh) and the shader spreads
  them to its side, turned round its own axis toward the eye, by at most `CARD_TURN` (~35°) from its grown facing
  (packed with its width into `aTone.w`). So a spray is never seen edge-on, as the old leaf banners never were, and
  close by nothing visibly swings round. Its tip flutters on its own phase, more in a gust; its base stays put.
- Leaf materials are OPAQUE with alpha-to-coverage, sharpened to a one-pixel edge and lifted with the mip so a far
  crown keeps its leaves. Blending them showed whatever had been drawn first: white fringes.
- WIND: every vertex sways by its bend weight (none at the foot) on its limb's phase (mesh.js `swayer`). A limb is
  the trunk's child a branch grew from, so a forking tree's forks of forks sway as one arm. A branch's foot takes its
  parent's weight and phase, blending to its own a few girths on, so no joint opens in the wind; a leaf card takes
  its branch's at its base (grow.js stores the branch on the card: `on`, `s`), so it stays on its twig. Eased on
  2026-11-18 (render.js `plantPoint`: `0.16 + 0.38 * gust`, was `0.25 + 0.6`; the cards' flutter by a third) -- the
  branches swung too wildly.
- FLOWERS sway too (flowers.js `flowerSway`): downwind by the square of their height on the plant, on the grass's
  gusts plus a flutter of their own.

`SEASON` (render.js) holds `autumn`, `bare`, `bloom`, `fruit` and `flowers`. The game sets them in `plantSeason`
(index.html).

## The flowers

`plants/flowers.js` grows twenty-two kinds: daisy, poppy, sunflower, tulip, rose, cornflower, buttercup, bluebell,
foxglove, lavender, iris, lily, peony, marigold, nettle, heather (`erica`), aloe, agave, water lily (`waterlily`),
lotus, petunia and acanthus. Each kind has a HABITAT (its JSON's `habitat`, `meadow` by default; `FLOWERS_OF(habitat)`): the meadow's kinds
are scattered everywhere; the `dry` ones (aloe, agave) the `water` ones (water lily, lotus) and the `garden` ones (petunia, acanthus) only where a world's
periods.json `flowers` names them -- a dry kind on a quarter of the meadow's spots, one plant a spot, a garden kind's on 30% of them (acanthus in Greece,
Rome and Byzantium, petunia in industrial Europe), and a water kind
in clumps on the lake's and the river's still margins, 0.25 to 1.2 m deep, at the water's surface. Each kind is a
recipe of PARTS:

| part | what it is |
|---|---|
| stem | a curved tube |
| blade | a petal or leaf: a bent quad grid with cup, curl, cupping and twist, its outline in the texture |
| whorl | n blades, each jittered in length, angle and curl, so no two petals match |
| dome | a centre lathe |
| hang | a bell on a stalk |
| spike | two crossed quads: lavender |

Shapes, veins, throats, crumple, spots, beards and seed spirals are all painted into one atlas (128 px cells; two
colourings a kind). A plant is 140 to 550 triangles. The material is opaque, alpha-to-coverage and double-sided.
In the game the flowers have their own batched pool (one draw), and the mushrooms a second (`litMaterial`, vertex
colours). tools/flowergen.py still writes the bloom items worn in the hair; the plant items it writes are no longer
used by the game.

## In the game (index.html)

- `plants = createPlantField(scene)`; `plants.add(kind, x, y, z, { yaw, scale, seed, height })` returns
  `{ kind, variant, info, position, rotY }`.
- `info` is the tree as the game knows it: trunk segments, boughs (perches), crown radius, height, evergreen and
  autumn colour. `treeCol` builds the colliders, squirrel runs, perches, shade and litter from it.
- `buildFlora` calls `plants.clear()`, adds the trees, bushes, hedges and site plants, then calls `plants.build()`.
  The frame loop calls `plants.update(camera)`.
- Debug hooks: `__dbg.plants` (stats, kinds, `first(kind)`) and `__dbg.treeCols`.

## The asset manager

assets.html lists `assets/plants` under "Plants" (kind `plant`): a tree shows three variants side by side, the bush
bare and with its fruits, a flower four plants; the stats line gives each variant's triangles per level. Editing the
JSON regrows it live (`createPlantField(scene, { species })` for trees, `setFlowerLook` for flowers). The "shown"
switch by walk/fly sets a tree or the bush in flowers + fruit, in flower, in fruit or in leaf only (live: the
season uniforms; `?season=` in the URL).

## Notes for later

- Draws: the far levels could share one draw across kinds (their atlases in a texture array, the bark tiles in
  another), which would cut the plants' CPU cost in a varied wood -- each new species in a world costs draws.
- The yew's sprays read a little as separate fishbones up close.
- The far levels' crowns are a little sparser than the near one where the card share is low (level 2): raising
  `FAR_CARDS` fills them at a cost in pixels and vertices.
- Light fringes show at the edges of some conifer spray cards in the game; not yet looked into.
- examples/webgpu_herd.html and webgl_herd_ref.html take the old capsule `makeTree` from the harness's frozen
  `/ref/flora.js` copy (docs/webgpu.md), not from the app.
