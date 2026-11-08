# The assets: what things ARE, as definitions

Everything in the world that has a shape is written down as JSON, under `assets/`, and built by the same code
the game runs. Nothing in `assets/` draws; nothing that draws holds numbers.

    assets/index.json                 the catalogue: every asset, by category
    assets/creatures/frames/*.json    BODY PLANS -- the horse, the big cat, the sheep, the deer
    assets/creatures/mammals/*.json   a species: the frame it stands on, its size, its colours, what it carries
                                      The primates (2026-11-05): gorilla (a silverback, knuckle-walking), orangutan (a
                                      flanged male on fists), baboon (olive, palms, a broken tail), lemur (ring-tailed) --
                                      and the kangaroo (biped, `hop.sync`): sculpted in their standing pose (engines.md)
                                      Also (2026-11-05): spotted hyena, impala (lyre horns, coatpat.js 34 `ridges`), giant
                                      anteater (its band: 38 `anteater`), pangolin (35 `pangolin` scales), striped skunk (39 `skunk`, in coarse fur), capybara (40 `coarse` hair)
                                      And (2026-11-06, generators scratchpad sc/must/badger.py, weasel.py): European badger (44 `badger`:
                                      the striped face, grizzled grey, black legs and belly; long pale fore claws), least weasel (45
                                      `weasel`: chestnut over white, a wavy crisp line; whiskers; `hop`, `flex`, `upright`)
                                      And (2026-11-06; generators scratchpad sc/m5/lynx.py, giantpanda.py, sc/new6/chamois.py,
                                      redpanda.py, porcupine.py): Eurasian lynx (the cat frame; 63 `lynx` spots, small to medium),
                                      chamois (the deer frame, lowered on shorter legs; hooked horns; `coarse` hair), giant panda
                                      (the bear's rig, scaled; 64 `panda` / 65 `qinling`: the eye patches and shoulder band per
                                      pixel), red panda (its own rig; a ringed tail of coloured tube segments; the face's white
                                      and tears as paints), crested porcupine (its own rig; banded quills: the coat's `bands`,
                                      `fan`, `sparse`; a crest of bristles)
                                      And (2026-11-08) three PREHISTORIC MAMMALS, sculpted on rigs of their own in the
                                      rhinoceros' plan (generator tools/creaturegen/prehistoric/gen.py): UINTATHERIUM (3.9 m,
                                      1.6 m at the shoulder; three pairs of blunt skull knobs, the bull's sabre canines past
                                      the jaw's bony flange, five-toed pads), BRONTOTHERIUM / Megacerops (5 m, 2.5 m at the
                                      withers hump; a saddle-shaped skull with the forked blunt nasal horn pair) and
                                      ELASMOTHERIUM (4.5 m, 2 m; a huge shoulder hump, long legs, a forehead dome with one
                                      1.1 m horn, a shaggy brown coat: `shag`, `coarse`). Each: three colour-only `coats`,
                                      a `cow` variant (smaller horns or tusks: shapes gated `when` bull / cow) and `young`.
                                      They live in the monster pen with the dinosaurs (docs/world.md)
                                      WHISKERS (2026-11-08, tools/creaturegen/sharp/whiskers.py; engines.md "Whiskers"):
                                      one `whiskers` shape per group, made into thin pointed strands on the head. The
                                      felids (cat, lion, tiger, leopard, lynx, smilodon, and the manticore's lion head)
                                      have four pale rows on the pad and a brow tuft. The dog, wolf, fox and hyena have
                                      sparse dark ones. The rodents and the hare (rat, squirrel, beaver, hare, capybara,
                                      porcupine) have long ones. So do the weasel, badger, red panda and hedgehog. The
                                      seal has a pale fan and brow whiskers. The walrus keeps its moustache of cones
    assets/creatures/birds/*.json     ...and the animals that share no plan with anything: their parts
    assets/creatures/dinosaurs|monsters|dragons|others/*.json
                                      The PTERANODON (2026-11-06, dinosaurs/pteranodon.json, SCULPTED; its generator
                                      scratchpad sc/ptero/gen.py): a 6 m male, a turkey's trunk in pale pycnofibre fuzz
                                      (agouti), a short stout neck in a gentle S, the head one flattened wedge (the beak run
                                      back into the skull, a mouth line, the rust crest a blade swept back in line with it,
                                      as long again). Its rest pose stands on all fours on the folded wings, the body tilted
                                      up at the front: the long round metacarpal the front leg (knuckles at the wrist and at
                                      the finger's root, three small clawed fingers ahead), the forearm sloping back down
                                      to the elbow at the flank, a short stout humerus muscled into the shoulder; the wing
                                      finger folded back along the arm, its tip up and back at about 38 degrees, its skin
                                      a thin dark strip behind the bones; its flight pose (flyRot) spreads long narrow wings, the
                                      skin out to the ankles, the hand flexing back on the upstroke (flyUp). The wings' skin
                                      is one MEMBRANE a side (bodyspec/bodymesh `membrane`, engines.md): furled beside the
                                      bones at rest, exact aloft, lighter from below (`under`). It soars over
                                      the water, pterosaurs.js (docs/world.md "Pteranodons over the water")
    assets/creatures/sea/*.json       SEA LIFE (the swimmers): the fish, the dolphin, the shark -- parts and a sculpt
                                      overlay each; the fish (and others/dragonfly) in seeded `coats` and sizes (`k`).
                                      (2026-11-07: the fish's overlay a roach's -- row scales, rayed fins, a forked
                                      tail; the dragonfly sculpted too, for the asset manager, the game drawing its parts;
                                      the shark and the dolphin rebuilt, gen/shark.py, dolphin.py; coatpat.js 66 koi, 67 rainbow)
                                      Also (2026-11-05): trout, carp, pike (fresh water), swordfish, clownfish, lionfish,
                                      a stingray (`ray`: three wing bones a side that flap in a wave out to the tips), an
                                      eel (nine spine bones), an octopus (eight arms of five bones each), and an edible crab
                                      (eight walking legs and two chelae; built facing +z, so it walks sideways). Their coats:
                                      coatpat.js 26-33 (zebratone, palespots, trout, mottle, suckers, clown,
                                      rowscales -- a carp's overlapping rows -- and finrays: rounded fins' faint rays)
                                      And (2026-11-06) the open water's giants, SCULPTED (one skinned surface each, the
                                      generators scratchpad sc/sea3/gen): a bull ORCA (7 m), a HUMPBACK (14 m, robust --
                                      3.5 m deep with its sagging pleated throat; the massive bowed lower jaw, golf-ball
                                      tubercles and the chin's lump; 4.5 m knobbed white flippers; serrated flukes) and a
                                      PLESIOSAURUS (3.3 m, a marine reptile, not a dinosaur, so filed here: a deep barrel
                                      of a trunk, the neck curving gently up, a small distinct head with interlocking
                                      needle teeth, four wing-like flippers). Their tails pitch (flukes beat up and down); their coats are
                                      SOLID patterns, coatpat.js 41-43 (orca, humpback, plesio). They swim in a sea or a
                                      big lake, sealife.js (docs/world.md "The open water's giants")
                                      And on the shore (2026-11-06, sculpted too, gen/seal.py, walrus.py): a HARBOUR
                                      SEAL (1.7 m: a plump spindle, a round dog-like head with V nostrils and no ear
                                      flaps, short clawed fore flippers, hind flippers that point back) in `coats`
                                      (harbour greys and browns; grey-seal bull and cows, larger, by `params`
                                      { greyseal }), coatpat.js 60/61; and a WALRUS bull (3 m: an elongated spindle,
                                      deepest at the shoulders and tapering to a narrow pelvis, a small head on a thick
                                      folded neck, 0.6 m tusks, a broad whiskered muzzle with the nostrils on top,
                                      paddle fore flippers propped forward and out, the hind flippers fanned flat
                                      behind), coatpat.js 62. They haul out, haulout.js
                                      (docs/world.md "Seals and walruses on the shore")
    assets/people/body.json           THE HUMAN CANON: every measure as a fraction of the stature
    assets/people/joints.json         THE JOINTS: how far each part turns, the body's rules, how a reach is chosen
    assets/people/positions|movements|exercises.json   the body in motion (docs/motion.md)
    assets/architecture/elements/*.json   ONE COMPONENT EACH: arch heads, a wall, a barrel, a groin, domes,
                                          roofs, a ring of bays, stairs and staircases, a column, colonnades
                                          -- what buildings are made of -- and small compositions of them
                                          (a stoa, a rotunda, towers with their stairs, coffers)
    assets/architecture/components/*.json   COMPONENTS a building `use`s: a chhatri, a minaret, a domed tower,
                                          a pavilion, a flying buttress... (docs/arch.md, "Components")
    assets/architecture/*.json        the buildings themselves (the component engine, docs/arch.md)

`assets.html` is the viewer and editor: pick an asset, see it built, edit its JSON, and watch it change as you
type. **+** and **-** change how many triangles it is made of -- for a building the arch engine's `detail`
(points per 90 degrees of arc, in powers of two), for a figure the sweep's own grid, rings up the chain and
points round a cut (shell.js `setDetail`). **T** shows the triangles it is actually made of -- for a figure that is the engine's own geometry view
(the shell builds its triangles in the vertex shader, so nothing on the CPU can draw them), for a building an
ordinary wireframe. **F** frames it again; nothing turns on its own. `python3 tools/serve.py` serves the
project and takes the **save**; with any other static server the page offers **download** instead (the same
JSON).

**The list** (2026-11-04) shows each building once. A building's DOORS (`assets/doors/<name>`) and its FINISH
(`assets/finishes/<name>`) are drawn on the building whenever it is shown -- in its finish when the box is ticked,
its doors always -- so listing them as well gave three entries, all showing the same thing, for every one of
eighty buildings. They stay in the catalogue (the game reads them). They are reached from the building itself, by
the **building · finish · doors** links beside its name in the bar (the open one in bold: a click opens that file
in the editor, still shown on its building), and through the search (a fold of their own appears while something is
typed). The door STYLES (`doors/styles`), a page of their own, stay listed under Buildings. A creature that flies
(a dragon, the manticore) has a **fly** box: aloft, in its flight pose (docs/motion.md "In flight"), wings beating;
`?fly=1` opens it so.

**The view** (2026-11-03, `cursornav.js`): the atlas's navigation (/home/martin/store/apps/atlas js/camera.js),
ported to three.js and y up, in place of OrbitControls. **Drag** turns the view about the point of the asset UNDER
THE POINTER -- that point keeps its place in the eye's frame, so it stays where it is on the page and the asset turns
round it (off the asset: about the middle of the view, the target). The **wheel** zooms about the point under the
pointer: the whole view is scaled about it, so it -- and everything on the line of sight through it -- stays under the
pointer, and the eye closes in on it by the same fraction each notch and never passes through it (off the asset: the
ground under the pointer if it lies nearer than the target -- ground beyond would carry the eye out past the asset --
else the line of sight's point at the target's depth, which is the atlas's `zoomAt`); turns
of the wheel at one spot keep the one point. **Right / middle drag** or **Shift+drag** pans, the grabbed point
following the pointer; **two fingers** pinch about the point between them and pan. **F** (and the **frame** button)
FLIES back to the framing, eased as the atlas's camera flies; a new asset is framed at once, and `"_view": "front"`
(the door styles, the arch heads) still frames it square on. Near and far follow the distance, so a coin can be looked
at from a centimetre. The point is picked by `standOn` in assets.html: a Raycaster against the building's / item's /
doors' own triangles, and a figure's parts as capsules (their triangles are made in the vertex shader, so no CPU ray
hits them). The state is the atlas's -- `target`, `yaw`, `pitch`, `r` -- and the page exposes it as
`__assets.nav` (`controls` is the same object, kept for old drivers: `.target`, `.update()`). Another lab page can
adopt it with `createNav(camera, canvas, { pick: meshPick(() => [root]) })` and `nav.update(dt)` per frame
(`nav.lookAt(eye, target)` to frame, `nav.fly(nav.poseOf(eye, target))` to fly). The other lab pages have it too
(2026-11-03) through `navControls`, an OrbitControls stand-in (`controls.target.set()` after placing the camera, then
`controls.update()` each frame; its "start" event): statuary.html and wardrobe.html pick a column round each figure
(`columnPick`: the figures are drawn in a shader) and statuary its pedestals; landscape_lab.html the land's meshes (not
the trees' instanced sets), its own near and far kept for the fog; menagerie.html and grove.html the ground.

**Cuts, parts and layers** (2026-11-03, `archview.js`, as the atlas has them): the panel at the view's top right.
**cuts** -- three axis-aligned section planes through whatever 3D asset is shown, each with a box to switch it on, a
slider across the asset's box (its place in metres beside it), **⇄** to keep the other side (by default the low side is
kept: below a level cut, -x, -z) and **face** to fly the eye square onto the cut (switching one on does too). The **y**
cut is the floor plan. Everything shown stands in a `THREE.ClippingGroup` (`stand` in assets.html); the three planes are
always there, an unused one far off, so switching one compiles nothing. **caps** fills the section: every opaque mesh's
back faces are drawn again after it in one flat red-brown, so a wall cut open reads as solid (no stencil: a closed solid's
inside back faces are exactly where the section is; an open sheet -- a lawn, a single-sided roof -- shows the colour
on its underside while a cut is on). **parts** (a building) -- with the tab open a CLICK (not a drag) picks the part
under the pointer, lit in the editor's amber: a part of the definition's `build` list (a component's pieces are its
part's: "church/high roof" is "church"), or with *pieces* the assembly's own part. **frame** flies to it, **isolate**
shows it alone (and flies; again: the rest back), **hide** hides it, **show all** brings back everything, **JSON** selects
its definition in the editor; Esc lets go. The list below shows every part with its triangles, a box to hide it and its
name to pick it (a filter over it). **layers** (a building) -- roofs, outer walls, inner walls, floors, ceilings & vaults,
stairs, windows & glass, doors, ornament, furniture, each with an opacity: 0 hides it, under 1 it is see-through (no
depth written); *no roofs* (roofs and ceilings off) and *x-ray walls* are presets. A face's layer is read from its part's
kind (roof, dome, vault, glass, tracery, a stair's, a moulding's...), which way it faces, and which side of it is IN --
arch/finish.js's interiors, told as `finishPieces` tells it (a roof's upper face is outside, a dome's face toward its own
axis inside, the rest by the air 30 cm before it). Picking, hiding and the layers need to know which part each drawn
triangle came from, and the game's meshes do not say (one mesh per finish rule, every part merged): the first time
parts or layers are asked for, the building is "exploded" -- each triangle looked up among the assembly's own (a
finish's piece is cut out of exactly one of them, in its plane), the meshes split by (part, layer), each in a copy of its
material whose opacity the layer's slider drives (Drachenburg: ~1100 meshes, ~0.6 s). Nothing in the game's code
changes for it. A rebuild while the definition is typed keeps the cuts, and what was hidden, picked and isolated (by
name). The page drives it as `__assets.view` (`cut(axis, on, at01, flip)`, `faceCut(axis)`, `setLayer(i, v)`,
`select(name, "part"|"piece")`, `isolate()`, `hide()`, `showAll()`, `state`).

**Finding an asset** (2026-10-03): the list is the catalogue in GROUPS by what the assets are -- Recent (the last
twelve opened), Creatures, Buildings, People & clothes, Items, Surfaces -- each group and category folding (what is
open is remembered), a big category split by its sub-folders. **/** jumps to the search: words in any order, all of
them in the path; the folds holding a match open, the rest hide; Enter opens the first, Esc clears it.

**The form** (`assetform.js`): beside the JSON, the definition as a FORM read from its own values -- numbers (drag
a label sideways to scrub, Shift finer), colours (`#hex`: a picker), checkboxes, short number lists in a row,
objects and lists as sections that open (made only when opened), `_about` and the other `_` notes as help text,
and strings that name something offered from their library as you type (a material, a pattern, a palette, an
asset's path). Each change writes the JSON (two-space) and rebuilds; the JSON stays the truth, edited either way.

A **hairstyle** is shown on a head (items/faces/woman wearing it; `head` off: alone), and a face or a hairstyle
gets the hair's controls: its colour (`own` the definition's), and the sheen and fibres (heads.js HAIR_SHEEN:
fibre, fine, sheen, tint, tight, shift; **copy** puts config.json people.faceShade.hair on the clipboard).

## Higher stands on lower

The rule is the one the buildings have always had (docs/arch.md): **each level only names the one below it.**

    a primitive     capsule, ellipsoid, sphere, tube, membrane        (skeleton.js segmentFor)
    a component     a leg of two bones and a foot; a head cluster; a tail as an arc of links; a lobe
    a body plan     "frames/horse": those components, at one scale, as expressions over the frame's params
    a species       "creatures/mammals/zebra": that frame at .85, in these colours, with these extras
    a hybrid        a centaur: a horse's body and a person's torso (species.js, still built in code)
    a winged one    an angel: a person and a pair of wings (kind "winged": winged.js, registered in creatures.js KINDS)

    an opening's profile -> a wall face -> a bay -> a ring or a row -> a storey -> a building

## The language

A definition is a JSON object. Four things make it a definition rather than a dump of numbers:

- **`use`** names the definition it stands on, by path: `"use": "creatures/frames/horse"`. The two are merged
  (the frame first), and the chain may be any depth.
- **`params`** are its own names, and **any number may be an expression over them** -- `"0.55*s"`,
  `"0.15*s*bulk"`. One parser for the whole project (`expr.js`): names, numbers, `+ - * /`, brackets, nothing
  else. A frame written this way is a frame: the zebra IS the horse at .85.
- **`when`** gates a piece on a param: `{ "when": ["mane", "head"], ... }` is drawn when both are true and
  absent when either is not -- one frame for the horse that has a mane and the one that is only a body. A WORD may
  be gated the same way (2026-11-06): `"pat": { "when": "tabby", "v": "tabby" }` is the tabby's stripes while the
  param holds and no pattern when it does not, and a list of them is the first that holds --
  `"pat": [{ "when": "pinto", "v": "piebald" }, { "when": "spotted", "v": "dots" }]` (creatures.js `gatedWord`).
- **a `component`** is a piece asked for by NAME rather than written out: `{ "component": "curlHorn",
  "s": 1.1 }` among a ram's extras is the rule that draws a curled horn (four tube links about a centre behind
  the ear), not the four tubes it comes to. The definition keeps the question; `mammals.js` COMPONENTS knows
  the answer. Change `links` or `sweep` and the horn changes.
- **`@colour`** reaches into the species' own table: `"color": ["@mane", "@tail"]` is "its mane's colour, or
  else its tail's", which is how a frame speaks about colours it does not know the names of. Colours are
  written as `"#8a5a33"` everywhere.

Merging is by these rules: objects merge key by key; `null` removes what the frame had; plain arrays
**replace** (a species that gives its own legs means those); and a list of NAMED things -- every entry an
object with an `id` -- **merges by that name**, so a species adds its horn to the frame's mane instead of
replacing it, and can reach in and change the mane by naming it. That is the same distinction the definitions
draw themselves: what a thing IS, against what it carries.

## The kinds

| `kind` | built by | what it is |
|---|---|---|
| `mammal` | `creatures.js` -> `mammals.js` `mammal()` | a body of two lobes, a neck, a head cluster, legs, a tail |
| `parts` | `creatures.js` | the part list itself, for the animals that share no plan (the birds, the fish, the dragonfly) |
| `body` | `people.js` `makePerson()` | the human canon: proportions, not parts |
| `garment` | `clothes.js` `tailor()` | a garment (assets/clothes/*.json) or a garment component (assets/clothes/components): sheets of cloth on the body, in fabrics (docs/clothes.md) |
| `wardrobe` | `clothes.js` `drawOutfit()` | who wears what: outfits by kind of person, the kits by name, the dyes each garment is drawn from |
| (a document) | `arch/assemble.js` | a building |
| (a family) | `patterns.js` | patterns: shapes on a tile, drawn into a texture (docs/patterns.md) -- and the palettes they are coloured from |
| (a finish) | `arch/finish.js` | a building's surfaces: rules naming patterns for its floors, walls, ceilings and roofs, inside and out |
| `item` | `items.js` `buildItem()` | a thing: a weapon, a shield, a tool, a piece of furniture, or a component of one -- parts in named materials, a `hold` (where the hand goes), `markers` (docs/items.md) |
| `item-kit` | `items.js` `pickKit()` | what a kind of person carries: loadouts by weight, an item in each hand |
| `item-materials` | `items.js` `materialOf()` | the materials items name (oak, iron, damask...): a pattern, its palette, its scale |
| `glyphs` | `glyphs.js` | hieroglyphs: the palette and modes, the parts, a Gardiner category's signs -- drawn as a sheet (docs/glyphs.md) |
| `glyph-texture` | `glyphs.js` `renderTexture()` | walls of hieroglyphic text: grids of quadrats filled by seed |

### One of a family

Patterns, Greek paintings and mural paintings are families whose members can take a second each, so the viewer lists them
and generates only the one picked (`assetpick.js`). Below the list is what can be asked of that one: `seed`, `palette`,
`texels` and the pattern's `params`; `width px`, `style` and `period` on a Greek painting. An empty field means the item's own value,
shown greyed. **Regenerate** draws it with what's asked, **New seed** with a random seed; the line under the view says how long
it took. Nothing asked here is written to the definition: to keep it, put it in the form or the JSON. Picking another item
clears what was asked.

## Coats and variants

(2026-11-06.) One definition, several looks. Two lists say what else a creature may be dressed in, and
`creatures.js dressed(def, { coat | variant })` dresses it -- the game (species.js) and the viewer alike, so what the
viewer shows for a coat is what the world builds:

- **`coats`**: a LIST the world picks from BY SEED -- a herd of horses bay, chestnut and grey, a black sheep in the
  flock, a town's cats. Each is a colour table laid over the definition's own; it may also give its **`name`**
  ("dapple grey": a label, never a colour) and the **`params`** it changes, so a coat is more than colours where the
  definition gates something on a param (the black cat's `{ "tabby": false }`: no stripes; the piebald horse's
  `{ "pinto": true }`: its patches). A coat that changes nothing is the definition itself, and a coat written twice is
  picked twice as often (the sheep: six white to one black and one cream). Picked by `species.js coatDef(species, k)`
  (the paddocks' animals, the riders' and the loose horses), `makeCat({ seed })` (the house cats), and the fish and
  the dragonflies (`makeFish`, `makeDragonfly`, at a size of their own too), and the seals (`makeSeal({ seed | coat })`:
  four harbour coats, then a grey seal's dark bull at `scale` 1.25 and pale cows at 1.1, whose `params`
  `{ harbour: false, greyseal: true }` swap the muzzle and the pattern).
- **`variants`**: NAMED looks the world asks for BY NAME -- `{ "rooster": { "params": {...}, "colors": {...} } }`, the
  hen yard's cock; the peacock's `display`; the lion's `lioness`. Built by `species.js variantDef(species, name)`;
  renaming one the game asks for loses it there.
- **`scale`** (either may say it): the whole creature at that share of the definition's size -- built as it is, then
  scaled as a whole (`geom.js scaleDef`, as a species' young), since what an asset writes in metres stays as written. The
  lioness is `.8` of the lion.
- **`sculpt`** (a variant, 2026-11-08): shapes of its own over the base's sculpt (`creatures.js sculptOver`) -- one
  with the `id` of a base shape is laid over it (its fields over the base's; a field written `null` taken out; `"drop":
  true` takes the shape out), one of a new id is added at the end; any other sculpt field (`eyes`, `mesh`) over the
  base's. The fox's `fennec` replaces the `ear` fin and adds a `streak` paint.

**One shape for all the looks (2026-11-08).** Coats and variants cost little: a definition's looks share ONE shape build
(docs/engines.md "Shapes shared by a definition's looks") and each is only DRESSED on it -- its colours, patterns,
details. A coat (colours, and params the field does not read) shares it; so does a `scale` (the shape is built once and
laid out at that size) and a variant `sculpt` that changes only fins, horns, feathers or paints. One whose params or
sculpt change the field's shapes (the rooster's comb, a calf's big head) builds its own -- write the difference as
details or paint where it can be. In the viewer (`?bodycache=0`), picking all fourteen of the horse's coats one after another
went from 25.4 s to 11.9 s, the dog's eight from 8.9 s to 4.7 s, the cat's eight from 9.4 s to 3.7 s (a coat about 0.4-0.8 s
instead of 1.0-2.0); the first look shown costs more (horse 2.2 -> 4.9 s, dog 1.4 -> 3.8, cat 1.5 -> 2.9): its shape holds
every look's colour boundaries, and the looks are made to be read.

The FENNEC (2026-11-08) is the fox's `fennec` variant: `scale` .58, its own colours (a pale face and a dark `streak`
under each eye -- a paint shape -- a reddish-buff back, white below, pale legs) and its own `ear`: a fin about 2.3 times
the fox's length against the head and .6 as broad as long, round-tipped (`outline` FENNEC), set wide and turned forward
and out, deeply cupped (`cup` 1) with the far part rolled in (`curl`), buff behind (`@ear`) paling a little toward the
rim, pinkish cream in the hollow inside a band of white hair (`rim` / `rimColor` "@earRim", `rimBack` .3: the band
full in front, faint behind), written by tools/creaturegen/sharp/ears2.py (`fox#fennec` in
ear_shapes.py: the fox's own old ear measured again with `long`, `wide`, `tilt`, its outline). It is drawn on the fox's
shape, scaled; only the ears and its paints are its own: the streak, the brush's black last eighth (`tailBlack`, an
`ell` of "@tip") and the dark scent-gland spot on top of the tail near its root (`gland`). In the world (index.html): a
pair in an arid world
(`MAP.climate`), elsewhere a stray one in a fifth of the worlds.

(2026-11-07, the mammals' audit.) **Coats** (picked by seed; index.html puts each cast bear, fox, dog, leopard, cow,
baboon, kangaroo, camel and bactrian in one): the bear's brown, grizzly and dark brown; the fox's red, cross and
silver; the dog's eight, now named; the leopard's spotted ones and a black panther; the cow's Holstein (twice), red
Holstein, Jersey (`.86`), polled Angus (`{ horns: false }`) and Hereford; the baboon's olive, yellow (`.92`), chacma
(`1.08`) and hamadryas; the kangaroo's red (twice), blue flier (`.85`) and eastern grey (`.95`); the dromedary's sand
(twice), cream and brown; the bactrian's brown (twice), sandy and dark. **Variants** (by name): the boar's `piglet`
(`.32`, striped -- its stripes `"when": "piglet"`, the tusks and crest `"when": "adult"`); the red deer's `hind` (`.86`),
`fallow doe` (`.74`, white spots `"when": "fallow"`) and `roe doe` (`.58`), all without the antlers (`"when":
"antlers"`); the blackbuck's `doe` (fawn, the horns `"when": "horns"`); the bear's `black` (`.72`) and `polar` (`1.1`);
the fox's `arctic` (`.82`); the leopard's `snow` (`.85`); the hare's `mountain` (white, `.9`) and `mountain summer`; the
gorilla's `female` (`.8`, no silver saddle); the hippo's `calf` (`.32`); the impala's `ewe` (`.9`, hornless -- the horns
`"when": "horns"`). With the boar come three piglets, with the stag two hinds and a fallow or a roe doe (by the town's
seed), two blackbuck does, a female gorilla, a hippo calf and two impala ewes.

A variant is more than a recolour where the definition writes the difference as PARAMS. The lion (2026-11-06) gates
its mane -- the crown, ruff, beard and neck shapes, the locks, the cape over the withers, the ragged rim of tufts -- on `"when": "mane"` and his cheek pods and jowls on `jowls`, and writes what makes him heavy over factors
that are 1 for him: `girth` (the trunk's depth and width), `neckG` (the neck's: hers clearly narrower than her head),
`fore` / `wrist` (the foreleg above and at the wrist), `pawS` (the paws), `hind` / `hock` (the hind leg above and below
the hock), `faceX` (metres his muzzle sits further forward than hers, and broader), and the face's own factors: `hs`
(every head and ear shape and the eyes scaled about the head joint: hers 1.15, a big head on a narrow neck), `earS` /
`earX` / `earY` / `earZ` (the ears' size and place), `mw` (the muzzle's width), `nS` (the nose leather), `eyeS` (the
eye). His `lioness` turns the mane and the jowls off, the trunk and neck down, the head, ears, muzzle and nose up and
the eye down, a smaller tuft, sandy-buff colours paler beneath, at `scale` .8. Both share one cat's
face (2026-11-06, round 3: the long sloping head read as a rodent's): a rounded crown and a broad forehead dropping
steeply to a short bridge, broad cheeks, a boxy muzzle with puffy whisker pads, a white upper lip and chin, a broad
nose leather with a dark rim, and the lip line, philtrum, tear lines and the white under the eyes painted (`op:
"paint"`); the eyes forward and frontal (`eyeX` / `eyeY` / `eyeZ` / `eyeF` on `sculpt.eyes`); round ears set to the
side, black-backed and pale inside (round 4: the ears about twice the size, clear of the head's outline, a pale tuft
inside; the whisker pads part of a wide, flat-fronted muzzle and their cream a soft paint grading into the cheek; a
white lower lip; a heavier brow over a smaller eye). His mane has a ragged rim of tufts round the face and down the
chest (`tuft*`, `tuftC*`), darker toward the chest; no quill coat (its flat cards read as shards at full size). Their feet: large but compact paws with
four toe lobes, about 1.4x the leg above (no longer discs; her legs as heavy as his for her size), a carpal bump and a bent pastern at the wrist, a clear hock with the heel behind it, thighs tapering to the
knee. The face and toes need a finer grid: `sculpt.mesh` cell 1.4 cm and 12000 triangles near. In the world she is his pride: three lionesses with
the meadow's lion, sharing one range about 28 m across around where he spawned, so they keep together, and three of
the Colosseum's four lions (index.html).

Both are taken off before the definition is built (creatures.js resolveDef), so neither leaks into what the engines see.

Which assets have them: the horse (14 coats: bay, chestnut, black, grey, dun, chestnut with a blaze and white
stockings, bay with white socks, dark bay, dapple grey, palomino, buckskin, flaxen chestnut, piebald, appaloosa -- its
`_coats` note says which keys and params each uses), the cat (8: ginger, black, white, grey, tuxedo, cream, brown,
calico; until 2026-11-06 mammals.js CAT_COATS), the dog, the pig, the sheep, the chicken, the duck, the fish and the
dragonfly, the frog (4) and the snake (4), the lynx (plain, `grey`, `red`), the chamois (summer, `winter`), the giant panda
(black-and-white, the brown `qinling` -- its `params.qinling` picks pattern 65 over 64), the red panda (plain, `pale`, `dark`); variants: the chicken (`rooster`), the peacock (`display`, `peahen`), the lion (`lioness`), the frog (4)
and the snake (4), the lynx (`spotted`: its spots smaller and denser -- `params.ps` .8 against 1, read by `sculpt.patScale: "ps"`), the chamois
(`winter`, `kid` at `scale` .6), the giant panda (`cub`, .45), the red panda (`cub`, .6). The birds whose species differ in colour (the
parrots, the toucans) take coats the same way -- but a coat is only SEEN where something in the world picks one (above):
a bird spawned with its plain definition shows the base however many coats it has. The toucan has 4 (keel-billed, toco,
channel-billed, chestnut-mandibled), the parrot 4 (scarlet, blue-and-yellow, green-winged, hyacinth macaw), the duck 2
(mallard drake, mallard hen: its `params` turn the drake's ring and curl off and the hen's mottling, eye stripe and bill
saddle on); the peahen variant's params take the train off and give her a short brown tail. In town (index.html) each
parrot, toucan and duck takes a seeded `coatDef`, every other duck a hen (the ducklings follow a hen), and two peahens
walk with the peacocks.

The mammals' coats (2026-11-07). The WOLF: grey (its own, twice), `arctic`, `black`, `red` (Canis rufus, at `.82`); its
coat has the agouti pattern's ticked fur. The TIGER: `Bengal` (its own), `Siberian` (`1.1`, paler and yellower), `white`
(blue-eyed; the stripes stay dark: the shader's). The ZEBRA: `plains` (its own), `Grevy's` (`1.12`, the stripes narrow and close:
`params.zs` .6 against 1, read by `sculpt.patScale: "zs"`, a white belly, a brown muzzle). The RAT: `brown`, `black` (the ship
rat). The SQUIRREL: `red`, `grey` (`1.2`, no ear tufts: the `earTuft` shape says `"when": "tufts"`), `dark red`; a town in
three has the greys (index.html createSquirrels). The OX: `brown`, `red`, `grey` (the steppe ox), `black`. The RAM: `white`,
`Soay`, `black`. The LION: tawny, `white` (the Timbavati's; a town in six). The REINDEER: `wild`, `white`; its variant `cow`
(`.85`, slender antlers: the bull's -- a long C-shaped beam with a back tine, a small crown of three tines, a bez tine and the
brow shovel -- are `"when": "bull"`, hers `"when": "cow"`). The PIG adds a mahogany `Duroc`, and its `young`
(two piglets at a sow's side in spring: index.html YOUNG). In town each of these takes `coatDef(name, townSeed)`, and a
reindeer cow walks with the bull.

The SKY STEEDS (2026-11-07: monsters/pegasus.json, monsters/griffin.json; skysteeds.js). The PEGASUS is the horse (its frame,
shapes and coats: white, `dapple grey`, `black`, `palomino`, each with `wing`, `wingTip`, `covert`, `wingIn`) with a pair of
great wings rooted at the withers: the birds' own wing builder (flier.wing, as the eagle's -- covert-shingled arm, secondaries,
fingered primaries; a copy at scratchpad var/wlib/skywing.py, the wing 2.9 m a side, broad at the arm, its eight primaries lengthening to the tip, the outer ones parted into fingers, the tip about 3.2 m out, raised 33 degrees, a span of about 6.4 m; var/peg.py).
The GRIFFIN (`1.15`) is the lion's rig and hindquarters with the eagle's head (brow shelf, ear tufts, a hackle ruff into the
breast), the same wing (2.6 m a side, raised 29 degrees, barred; var/gri.py) and eagle forelegs -- yellow scaled shanks, four
toes, black talons -- scaled feathers (`rowscales`) blending into agouti fur at the waist (`golden`, `white-headed`, `dark`).
Both wings are authored SPREAD; on the ground skeleton.js PERCH folds them along the flanks, the primaries crossing over the rump
(`an.perch`, `an.perchFold` from `SKYSTEEDS[name].fold / squeeze`). In the world (index.html) each is a wanderer that now and
then gallops, climbs on hard beats, glides round in circles with bursts of beats, then comes down on open level ground in its
range and canters to a walk: the pegasus in the monsters' range (a second, coloured one in half the worlds), the griffin on the
crags (cragRange). Aloft the legs are held (`an.pose`, `SKYSTEEDS[name].tuck`): forelegs folded forward and up, hind legs
trailing, blended in on the climb and out at touchdown.

The frog and the snake (2026-11-06). The FROG's coats are the European frogs the meadow picks from: common frog (olive, the
base; and brown), pool frog (`.9`, bright green, a pale `midline` down the spine, no mask) and European tree frog (`.45`, leaf
green, smooth: no `spots`, `ridges` or `mask`, the dark side `stripe` edged pale). Its variants are the exotic ones: bullfrog
(`1.7`, no ridges, `tympS` 1.7: the big eardrum), blue poison dart frog (`.45`, blue with black spots, round black eyes),
yellow-banded dart frog (`.38`, black with yellow `bands`, the legs yellow spotted black) and red-eyed tree frog (`.6`, green over
blue flanks with pale `flankBars`, orange toes, red eyes with a vertical pupil: `pupilSlit`). New colour keys `limb`, `leg` and
`toe` fall back to the old ones (`side`, `back`), so the base is unchanged. The mouth is a soft painted line (a ridged tube's
hard vertex colours read as a toothy grin). The SNAKE's coats: grass snake (the base: its flank
`bars` and yellow `collar`), adder male (grey) and female (brown) (`.42`/`.45`, `girth` 1.3: stout; the dark `zig`-zag, flank
spots, the X on the crown, the stripe behind the eye, a `slit` pupil, a dark belly) and smooth snake (`.42`, the paired `dots`,
dark crown and eye stripe). Variants: corn snake (`.85`, red `saddles` edged black on orange), coral snake (`.5`, `girth` .8,
`rings` red-yellow-black, black snout, yellow band over the head), green tree snake (`.8`, `girth` .62, plain green over
yellow) and python (`2.5`, `girth` 1.55: about 4 m and 17 cm thick, brown `blotch`es edged black on tan, the spearhead on the
crown). `girth` thickens the trunk (the neck less, the belly kept on the ground). The markings on both are PAINTS --
`op: "paint"` shapes (docs/engines.md), colour without shape -- the snake's laid along its rest pose's curve by a script and
written with `girth` in them, so they stay on the skin as it thickens. In the meadow (index.html) three frogs and two snakes take
a seeded `coatDef`; the exotic ones are variants and stay in the asset manager.

The water's and the shore's (2026-11-07). The SHARK (rebuilt, sculpted: a great white, 3.2 m) has coats great white (the
base, twice) and blue shark (`.9`, indigo over white) and variants `hammerhead` (`1.1`: `params` { pointed: false, hm: 1 }, the
cephalofoil with the eyes at its ends) and `whale shark` (`3.5`, ~11 m: `spots`, coatpat.js 27 `palespots`). The DOLPHIN
(rebuilt: a bottlenose, 2.6 m): bottlenose (twice) and common dolphin (`.78`: `params.common` paints the hourglass -- buff
thoracic patch, pale grey rear, dark eye ring and flipper stripe). The CARP: common carp (twice) and a dark river carp;
variants `koi (kohaku)` (white with red patches over the back and the upper flank, the row scales over all: coatpat.js 66 `koi`) and
`koi (yamabuki ogon)` (gold) -- `params` { wild, koi, ogon } pick the trunk's pattern (a gated word list) and gate the
`shade`. The TROUT: brown (twice) and rainbow trout (`params.rainbow`: coatpat.js 67 `rainbow`, small black spots and a
pink band). The CRAB: edible crab and green and red-orange shore crabs (`.3`); the CLOWNFISH: ocellaris, the black
(Darwin) form, a deeper orange; the OCTOPUS: common (and flushed red, pale) and variant `giant Pacific octopus` (`3`); the
RAY: common stingray (and dark, sandy). The CROCODILE: Nile (twice), saltwater (`1.25`, paler) and variant `American
alligator (colour)` (near black; the snout is still the crocodile's). The TURTLE: red-eared slider (twice),
yellow-bellied slider, European pond turtle (`.72`, dark with yellow flecks, no red ear). The SPIDER (a wolf spider):
brown (twice), grey and variants `tarantula (Mexican red-knee)` (`3`, the leg joints orange) and `garden cross spider`
(`.65`, tan, its abdomen's chevrons white). The SCORPION: brown (twice), deathstalker (yellow) and variant `emperor
scorpion` (`1.8`, black). The DRAGONFLY gains a banded demoiselle (metallic blue, tinted wings). In the world
(index.html): the lake's shark and dolphin, the fresh-water carp and trout, the crocodile, the turtle, the spider and
the scorpion each take a seeded `coatDef`; KOI (the carp's two koi variants) swim in every pool moat -- Kinkaku-ji's
pond, the Phoenix Hall's, Kunming Lake.

**The variant editor** (`assetvariants.js`): a creature in the viewer gets a **variant** list in the bar -- *base*,
then every coat (by number and name) and every variant -- and the stand shows the one picked (**V** the next one,
**Shift+V** the one before; `?coat=3` or `?variant=rooster` opens one; the page drives it as `__assets.pickDress({ coat:
3 })`). The FORM opens with it: its name (a variant's key, renamed in place), its **size ×** (`scale`; empty: the base's), the colours it changes -- each a picker,
beside a swatch of the base's colour under it, **×** to take it out (back to the base's), and a field to **add** any key
(the base's, any other coat's -- a horse's `pastern`, `blaze` -- or a new one) -- and the params it changes, the same
way (a checkbox, a number, a text; offered: the base's params and its frame's). **duplicate** copies it (after it),
**delete** (click twice) takes it out, **↑ ↓** move a coat in the list (the seeds' picks follow the order), **+ coat** and
**+ variant** start a new one. Every change rebuilds at once, as typing does, and is written into the JSON; **save**
saves it. At the base, the panel says how many there are and offers the two **+**.

## How the move was checked

The definitions were written out of the code that used to hold them (`ref/gen.html`, `mammals.js` CAPTURE),
and then every species was built BOTH ways and compared part by part, field by field -- position, radius,
colour, blend, animation, the lot (`ref/same.html`). **68 species, 0 differ.** Only then did `species.js`
start reading the files. `mammals.js` went from 885 lines to 324 and `species.js` from 731 to 470; the numbers
did not move, they changed address.

## Not there yet

- Some parts still carry an anisotropic `scale` from the SDF, which drew ellipsoids and the polygon sweep
  cannot: they come out as fat pills. The flattened ones that matter are membranes now (a beaver's tail, a
  hare's ears, the folded and outstretched wings), but a comb, a wattle, an owl's face disc and a turtle's
  plastron are still scaled spheres.
- The **wardrobe** -- what each garment is shaped like -- is still in `people.js`, and belongs in a set of
  definitions of its own: the body's canon is about the body, and the viewer shows it on a bare figure for
  that reason.
- The **winged people** (angel, demon) are definitions already: kind `winged` (`person`: makePerson's options,
  `wing`: bird or bat and its numbers, `horns`, `hair`), built by winged.js, which registers the kind with
  creatures.js `KINDS` (a module building a kind from other engines imports creatures.js, never the reverse).
- The **hybrids** (the centaur, the beast-men) are still composed in `species.js`: they are a person and an
  animal put together, and want a `kind` of their own that names both.
