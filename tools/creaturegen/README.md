# creaturegen: the scripts that wrote the creature JSON (2026-11-05 to 11-07)

These scripts wrote, or patched, the species files in `assets/creatures/` during the animal pass of 2026-11-05 to
11-07. They were written in a session scratchpad and copied here afterwards, as they were: working scripts, not a tidy
library. Each file's header comment says what it does, and most species carry an `_about` in their JSON naming the
script that made them.

**The JSON is the source of truth.** Several species were made by a chain: a generator, then one or more patchers
(manes, tails, sabres, coats, wing fixes), sometimes with hand edits after. So re-running one script can undo a later
fix. Before regenerating a species, run its script on a copy, diff the result against the committed JSON, and keep
what the diff says you should keep. The table at the end says which scripts reproduce today's files exactly.

**Level of detail is not authored here.** A species sets only `mesh.far` (where its far mesh takes over, default 4 m).
The third, very far mesh is made in the game from the dressed far mesh (bodyfar.js, 2026-11-22) and drawn by size on
screen (bodies.js `BODY_LOD`); docs/engines.md "A herd at a distance". Nothing in the JSON or pregen/shapes/ changes for
it, and a re-bake is not needed.

## Running

From the repo root. Python 3 and Node 22. The scripts write straight into `assets/creatures/` (absolute paths under
`/home/martin/store/apps/multiverse`, the way the rest of `tools/` does). Some call node to sample the sculpted surface;
those run node with `--import ./reg.mjs` (in this folder), which points `three` at `build/vendor/`.

    python3 tools/creaturegen/birds/newbirds.py stork pigeon     # names, or none for all of its birds
    python3 tools/creaturegen/sc/ung/camelid.py camel            # camel | bactrian
    python3 tools/creaturegen/sc/carn/gen/sabres.py IN OUT       # a patcher: IN.json -> OUT.json

Files starting `_` (`_q.json`, `_s.json`, ...) are scratch outputs the scripts rewrite on each run. `orig/` folders
(giants, sc/others) hold the species as they were before the rework: the giants' generators build on them.

## Where things are

| folder | what |
|---|---|
| `birds/` | the birds. `nb.py` the standing body plan, `nbwing.py` its folded wing and flight rig, `flier.py` the spread-winged fliers; `newbirds.py` / `newbirds2.py` most species by name (newbirds2: puffin, crowned crane, spoonbill, cassowary, turkey); own files for chicken, duck, eagle, flamingo, heron, hornbill, owl, parrot, peacock, raptor (buzzard, falcon), rooster, swan; `varB.py` named coats; `fchk.py`, `flyck.py`, `rootfix.mjs` feather checks |
| `giants/` | elephant, hippo, rhino and the dinosaurs (`gen_*.py`, on `lib.py` and `orig/`); `eletail.py` the elephant's sculpted tail; `tailfix.py`, `beartail.py` the same fix for rhino, cow, ox, giraffe and bear (applied 2026-11-08 by merging only the tail's keys and shapes into each file's own text: `lib.save` reformats the whole file, and the species JSON has changed since -- do not re-run them on today's files) |
| `sc/ung/` | the ungulate frames: `bovine.py`, `camelid.py` (camel, bactrian), `cervid.py` (deer, reindeer, cervicapra, oryx), `equid.py`, `giraffe.py`, `ovine.py`, `suid.py`; `lib.py` the overlay helpers |
| `sc/carn/gen/` | carnivores: `canid(s).py`, `felid.py`, `cat.py`, `leopard.py`, `lion.py`, `tiger.py`, `smilodon.py`, `bear.py`, `bat.py`, `small.py`; `sabres.py` the smilodon's mesh sabres |
| `sc/m5/` | giant panda, lynx (`felid.py` moves the tiger's sculpt onto other cats) |
| `sc/new6/`, `sc/must/` | anteater, capybara, chamois, impala, hyena, pangolin, porcupine, red panda, skunk; badger, weasel (`rigs.py`, `rigs5.py` their rigs) |
| `sc/prim/gen/` | primates and the kangaroo: baboon, gorilla, lemur, orangutan, kangaroo |
| `sc/others/gen/` | crocodile, frog, hydra, manticore, scorpion, snake, spider, turtle, unicorn |
| `sc/sea2/gen/` | fish, carp, trout, pike, swordfish, lionfish, clownfish, eel, ray (and manta), crab, octopus, dragonfly; `sealib.py`, `finsheet.py` (a fin as one membrane); `sealib.sheet` (2026-11-21: a fan of faces as one `sheet` -- the manta's wings) |
| `sc/sea3/gen/`, `sea/` | `cetlib.py`; shark (hammerhead, whale shark), dolphin, orca, humpback, seal, walrus, plesiosaur; `wgsl_*.py` their coat shaders; `plesio_flippers.py` (2026-11-21: only the flippers, as `sheet`s, put into today's plesiosaurus.json) |
| `sc/ptero/` | the pteranodon |
| `sharp/` | (2026-11-22: `tri2sheet.py`, a JSON's runs of `tri` faces as `sheet`s; `runs2brush.py`, its runs of like tubes, horns or fins as `brush` bundles -- README "Fins as sheets, manes as brushes") (2026-11-08) converting field parts to the engine's SHARP types (sharp.js `horn`, `fin`): `shp.py` edits a species' shape list line by line and holds the geometry, `conv.py` `ear_fin` (an ear ellipsoid made a cupped sheet, its root buried in the head by probing the field with `fd.mjs`) and `horn_of`, `horns.py` the HORN family (ox, oryx, rhinoceros, carnotaurus, impala, chamois, cow; each horn's field part and detail tip merged into one centreline), `named.py` the exemplars (boar, walrus, elephant, crane, crowned crane, zebra, kangaroo, giraffe: run once each, it stops when the shapes are gone; `stork` re-runnable: the white stork's lower mandible re-pointed to just behind the upper's tip, 2026-11-08 evening), `t_sharp.mjs` a unit check of the meshes. SECOND PASS (2026-11-08, `sharp2.py` the helpers -- replace in place re-reading the file, roots sunk on the field with `sink_many`, a backup per species in `$SHARP2_BACKUP` -- and `undo.py SPECIES REGEX` to put the field shapes back from it): `claws.py` (claws, talons, the anteater's and pangolin's nails, theropod hands split into a field finger and a hooked claw, the hoof-nails of camels, hippo, rhino, capybara, ankylosaurus, stegosaurus), `teeth.py` (theropods, crocodile, plesiosaur, hydra, the spider's fang), `spikes.py` (ceratopsian horns and frill spikes, the armoured dinosaurs' spikes, the hydra's horns, the unicorn's and blackbuck's spiral horns, the ram's coil), `antlers.py` (deer, reindeer: beam and tines each a horn, tines rooted in the beam, the reindeer's palms flat horns), `bills.py` (every bird's bill as two mandibles meeting on the commissure, the crane's way; the duck's and swan's flat with a rounded end and a nail, the spoonbill's spoon, the hornbill's casque, the swordfish's sword, the turtle's hook and two dinosaur beaks). The cetaceans' fins are in `sc/sea3/gen/cetlib.py` (`dorsal_sheet`, `flipper_sheet`, `fluke_sheet2`, `fluke_sheet_blade`; their joins `fair`, the field fillets gone). THIRD PASS (2026-11-08): `fair_bases.py` (the tusks' and the horn family's roots faired: horn `fair`; the boar's tusk re-placed), `ears.py` (the zebra's, giraffe's and kangaroo's ears: knobs gone, faired, `rim`/`rimAt`/`patFace` colour, the giraffe's turned and drooped, the kangaroo's tip rounded; it works from `ears_orig.json`, its backup of named.py's ears); `ears2.py` with its table `ear_shapes.py` (EVERY other mammal's and monster's ears, 2026-11-08: each one cupped `fin` sheet measured from the old ear shapes -- its reach, half-width, root where its axis leaves the head (or, `flat`, a drop ear's or a primate's root on the skull), the base corners brought onto the skin, outline by family (TRI, CAT, ROUND, LEAF, BROAD, HARE, PIG, BAT, SHELL...), `faceTo` the hollow's look, `inner`/`innerRim`/`rim`/`tip` colours, `fair` root; extras: `tuft` (a lynx's, in the outline), `tassel` (a red squirrel's tuft, 2026-11-08 evening: a pointed `fin` core rooted along the back of the ear's upper rim and a brush of hair `strand`s rooted on the rim and back face near the tip, drawn in to a point above it -- it was `tuftHorn`, one horn behind the ear), `ribs` (a bat's, the `ridges` pattern in the ear's frame), `plane2d` (the elephant's fan, its outline in metres in the old ear's plane), `expr` (the lion's and tiger's written over the head params); it works from `ears2_orig.json`, `python3 ears2.py FAMILY|SPECIES|all`, `--undo SPECIES`); `review.py` (fixes after the review of the second pass: bills curled into a "C", the crocodile's teeth on the jaw margin interlocking, claw roots faired, reindeer palms as `fin`s, theropod fingers as smooth horns, the pachycephalosaur's knobs); `dropear.py SPECIES` (a DROP ear stood off the skin: each outline point moved along the field normal to 4 mm clear at the root, 14 mm at the tip -- the dog, whose ears2.py flaps lay inside the head); `caribou.py` (the reindeer's antlers rebuilt as a caribou bull's: beam flattened through a `fin` crown, bez and shovel palm sheets -- the shovels a mirrored pair since 2026-11-08 evening, the antlers wholly symmetric, every tine a `horn` rooted on a palm's rim or the beam, tapered to a point); `plates.py` (the stegosaurus's plates and the dilophosaurus's crests as faired `fin` sheets); `whiskers.py SPECIES|all` (2026-11-08, `--check`, `--undo`): every species with prominent whiskers given `whiskers` shapes (bodyspec.js `whiskerStrands`, sharp.js `strandMesh`) from its table `SPEC` (the audit in its header: felids white with brow tufts, canids and hyena sparse and dark, rodents, hare, mustelids, red panda, hedgehog, seal) -- `at` found by a ray from a seed inside the head to the skin and `normal` from the field (`wprobe.mjs`), the lion's and tiger's written over their head params; the rat's, weasel's, seal's and porcupine's hand-placed whiskers replaced (kept in `whiskers_orig.json`), the walrus's left |
| `prehistoric/` | (2026-11-08) the prehistoric mammals written from scratch: `gen.py [uintatherium brontotherium elasmotherium]` (each a rig of its own in the rhinoceros' plan, its whole sculpt -- trunk, legs on the rig's joints, head, a hanging tail rooted on the rump by a ray -- and its SHARP parts: knobs, horns, tusks and hoof-nails as `horn`s (blunt hemispherical ends, roots sunk in the field and `fair`), the ears the rhinoceros' `fin` moved and scaled; the bull's and the cow's horns and tusks both written, gated `when`), `plib.py` its helpers, `probe.mjs FILE.json` (joints, field distances and ray hits of a species given as a file, catalogued or not). It writes the JSON whole and nothing patches it after: re-running reproduces today's files |
| `prehistoric/` (reptiles) | (2026-11-08) `dimetrodon.py`, `desmatosuchus.py` (assets/creatures/dinosaurs; run from anywhere, `python3 prehistoric/dimetrodon.py`): "parts" rigs in the wall lizard's / crocodile's plan (sprawling legs swinging on the gait clock, tail links `caud1..4`), the whole sculpt written one shape a line, then the SHARP parts placed on the body field probed through `sharp/fd.mjs` and roots sunk with `sharp2.sink_many`: the dimetrodon's sail (21 spine `horn`s + one scalloped `fin` between them, `fair`), its teeth (fangs, incisors, cheek teeth) and claws; the desmatosuchus's scutes (one `fin` plate per row and side, paramedian and lateral merged -- `MERGE`, rims lifted so each overlaps the next), its neck/flank/tail spikes and the curved shoulder spikes (`horn`s, faired), leaf teeth and claws. `rept.py` the shared helpers (limb bones, `bent` claws, `index_add` lists a path in assets/index.json -- the species must be listed before `fd` can probe it). They write the JSON whole: re-running reproduces today's files |
| `herps/` | (2026-11-08) the small herps written from scratch (assets/creatures/others; `python3 herps/agama.py`, `salamander.py`, `gila.py`, `iguana.py`): the AGAMA (Agama agama, 28 cm), the FIRE SALAMANDER (20 cm), the GILA MONSTER (50 cm) and the GREEN IGUANA (1.5 m: its spined crest serrated `fin`s one per bone, the dewlap a `fin` sheet, the cheek's subtympanic shield a raised pale disc, neck tubercles). `hlib.py` the shared plan -- the wall lizard's "parts" rig (body -> chest -> nape -> head, the tail's links `caud1..4` swinging on the gait clock, sprawled legs from `prehistoric/rept.py` limb_parts), each tail ONE `sweep` along caud1..4 (`sweep_tail`; the agama's colour rings as its `bands`), limbs and digits, claws as `horn`s rooted with `sharp2.sink_many`, and `Painter`: markings as paints (colour only) laid on the skin found by rays through `sharp/fd.mjs` -- or, given the body's `axis`, written as `dabs` the engine lays (the salamander's and the gila's: "Coat marks as dabs" below) (the agama female's spots and flank patches, the salamander's yellow blotches and stripes, the gila's bands and reticulation, each gated `when` by its coat's params). The jaw lines are one `sub` tube through skin hits, the salamander's costal grooves and the gila's ear slits small `sub` ellipsoids in the skin's tangent plane; the agama's nuchal crest a serrated `fin`. Two passes each (the body written bare and probed, then the rest); they write the JSON whole: re-running reproduces today's files |
| `ungulates/` | (2026-11-08) the big northern ungulates written from scratch: `gen.py [moose bison ibex]` (assets/creatures/mammals; run from its folder, `PREHIST_TMP` a scratch folder for probe.mjs's files): the MOOSE (the deer frame, its own rig numbers: trunk, hump, neck and the long overhanging head by hand; the bull's palmate antlers -- a flattened `horn` beam and two dished `fin` palms on it a side, every tine a `horn` on a palm's rim, mirrored; the bell a `fin`), the BISON (a cattle rig in the ox's plan, the ox's legs thickened; one mass from the low head through the hump to small hindquarters; the matte cape's shaggy outline all field LUMPS placed on the skin by rays -- hump wool, the skirt under throat, chest and elbows, the forearm chaps, a thick beard, a curly forelock mat -- its colour fading over ~20 cm with paint patches past an irregular edge; short black `horn`s), the IBEX (the chamois' whole sculpt and rig scaled, the trunk thickened, the head larger; the knobbed scimitar `horn`s -- `knob_horn`, a ridge every 5 cm -- and a `fin` beard); variants gated `when` (bull/cow/calf, billy/nanny/kid; the bison cow's and calf's lower hump a variant `sculpt`). `ulib.py` the helpers on `prehistoric/plib.py`: `legs_from` (the chamois' legs moved onto a rig's hips), `ear_onto` (another species' `fin` ear moved by its own frame), `palm_fin`/`tine_pts` (sharp/caribou.py's), `index_add`. It writes the JSON whole and nothing patches it after: re-running reproduces today's files |
| `kin/` | (2026-11-21) KIN species: a near species' asset taken whole (`use`) and re-coloured, resized and trimmed -- `kinlist.py` the table (128: cheetah, puma, jackal ... the songbirds, waders, vultures, the fish from barracuda to zander, the snakes, lizards and the tree frog; the platypus a beaver with a duck's bill), `python3 kin/kin.py [names]` writes assets/creatures/<dir>/<name>.json and the index (`--keys BASE` lists a base's colours). Its options: `tone` (hue/sat/light, or `to` a body colour the whole table is moved toward, eyes, nose, teeth and the like kept), `colors`, `plain` (patterns off), `recol` and `drop` (shapes -- and parts -- by id regex: creatures.js filters `{id, drop: true}`, a dropped part taking its children), `short` (a tail sweep cut), `shape` (sculpt overrides), the top-level `size` (creatures.js scales the built creature: `dressed()` overwrites `scaleBy`) |
| `rework/` | (2026-11-21) every KIN species REBUILT as its own model (the user: "jerboa is nothing like kangaroo ... take the effort with each"), one script a species or a family, each writing its asset whole (no `use`), with `_about`, coats and life sizes; each group has its helpers, a node build check (`node --import ../../reg.mjs check.mjs NAMES`) and its render loop (`dozen/cshot.py`). `small/` (jerboa, hamster, vole, shrew ... 14, `slib.py`), `carn/` (cheetah, puma, jackal, coyote, wolverine ... 11, `clib.py`), `bigmam/` (armadillo, aardvark, sloth, chimpanzee, gibbon, macaque, wildebeest, muskox, pronghorn, manatee, beluga, sperm whale ... 16), `herps/` (the snakes on `snakelib.py` -- the cobra's hood two `fin` sheets with `horn`-disc spectacles -- skink, gecko, monitor, chameleon, tree frog, slowworm), `fish/` (22 on `flib.py`: perch, zander, cod, piranha, flounder, monkfish, cuttlefish...; fins `membrane`s, the mouth a `horn` line laid on the skin by `surf_z`), `passerines/` (25 songbirds on birds/nb.py: `cone_bill`, `cocked`, `spots`), `bigbirds/` (27: waders, grouse, vultures, owls, the harrier and osprey on the eagle's plan; `bblib.py`). INSECTS in 3-D (new, Others): `insects/` (35 crawlers on `insectlib.py` -- `Bug`, `elytra`, `hull`, `segments`, `antenna` kinds, tripod `legs`; beetles, bugs, ants, termites, flea, louse, mite, tick, caterpillar, grub...) and `winged/` (28 on `wlib.py`: bees, wasps, flies, gnat, mosquito, butterflies with painted wing patterns, moths, mayfly, cicada, lacewing, damselfly; `clear_wing` veined grey membranes folded in a V) |
| `slim/` | (2026-11-21) fewer shapes, the same animal: `python3 slim/slim.py [--write] [names] [--only fins|tufts|chains]` -- a flat fin authored as a fan of `tri`s retraced to its outline, simplified (Douglas-Peucker, 2 % of its size) and ear-clipped again (a carp's dorsal 42 -> 9), a tuft of `horn` strands thinned to ~8 a little thicker (the squirrel's ear tassels 31 -> 8), a `brush`/`plume` chain of ellipsoids every other one kept, longer (the squirrel's tail 16 -> 9); kept pieces keep their ids. Run 2026-11-21 on squirrel, dragonfly, carp, fish, lionfish, pike, swordfish, trout: 959 -> 605 shapes |
| `monsters/` | (2026-11-08) `cerberus.py` (assets/creatures/monsters; `PREHIST_TMP` a scratch folder for probe.mjs's files, `python3 tools/creaturegen/monsters/cerberus.py`): the three-headed hound written from the WOLF (`wolf_base.json`, its snapshot, so later wolf edits do not move it) scaled 1.5x, the trunk and legs bulked to a mastiff's, the wolf's head given an opened jaw on its own bone `headJaw` (the jaw's shapes turned about the hinge; mouth, tongue, snarl ridges; teeth `horn`s rooted by rays on `prehistoric/plib.py` probes), scaled 1.18x and raised 14 deg; the SIDE heads that head moved by one rigid motion (turned 32 deg out and 10 deg up about the neck's root, set out 26 cm) onto bones `neckL`/`headL`/`headJawL`, mirrored (`mesh.symmetric`); shoulder masses, quill `coat` mane on the necks and withers; the SERPENT tail one `sweep` on `tail..tail5` ending in a snake's head (fangs and forked tongue `horn`s, slit amber eyes); claws `horn`s; each head's and jaw's idle anims on its own phase. It writes the JSON whole: re-running reproduces today's file |
| `sweep/` | (2026-11-08) long necks and thin tails as ONE `sweep` shape each (sculpt.js `prepareSweep`, sharp.js `sweepMesh`; docs/engines.md "Sweeps"): `necks.py SPECIES... [--dry]` (assets/creatures/birds) merges a bird's neckA/neckB/neckC tubes into one sweep on the bones `neck`, `neck2` (`neck3`), its points the tubes' with shared ends merged, `aspect` 1.1 and the radii / sqrt(1.1); `tails.py CAT/SPECIES... [--chain a,b] [--end point] [--thin cells] [--dry]` joins a mammal's tail cones (or one tube) on the `tail*` bones into one sweep: the commonest colour its `color`, the others `bands` (shares of its length), a `tailTip` sphere absorbed as the last band; k, kc, hair, coat, pat, frame from the first segment. Both edit the species line by line (`sharp/shp.py`) and append a note to `_about`. Run so far: necks -- swan, flamingo, heron, crane, goose, ibis, ostrich, pelican, spoonbill, cassowary, turkey, vulture, crowned crane, stork (its neck only, after the bill fix); tails -- cat (`thin` 3.2 by hand), rat (`--end point`), lemur, kangaroo, baboon (`thin` 3 by hand), tiger, lynx, dog (its root moved into the rump, k .028), wolf, cow, ox (2026-11-08: hyena, fox, lion, leopard, giraffe, zebra, horse, camel, elephant, rhinoceros and hippo were looked at and left: no better as a sweep, or a rig `keep` tail already smooth; the pig's rig curl given `links: true, n: 12`). `flynecks.py [SPECIES...]` sets the flight neck of the swan, goose, crane, stork, flamingo (inserting its third neck bone `neck3`), ibis and spoonbill: the neck sweep's `bones` from `body`, `knotsAt`, `spread` and the parts' `flyRot`, so the neck is held nearly straight aloft (not the heron's: it flies with its neck folded). A generator re-run for one of these writes the tubes and cones back: run the script again after it |
| `var/` | variants and patchers: `mane/mane.py` lock and brush manes (horse, pegasus, unicorn, zebra; `zeb/` samples the zebra's stripes), `gri.py` / `peg.py` + `wlib/skywing.py` the griffin's and pegasus's wings, `tgr.py` tiger and lion coats, `isl/mantwing.py` (+ `isl/mantwing_probe.mjs`) the manticore's wings as ONE `membrane` a side, shared vertices, from the old plates' outline (run once on `isl/manticore_plates.json`, the plated JSON: `python3 var/isl/mantwing.py var/isl/manticore_plates.json OUT`), `catjson.py`, `horsejson.py`, `lionjson.py`, `frogjson.py`, `snakejson.py`, `snakemarks.mjs` |
| `aud/`, `sc/au/`, `sc/aud2/` | audit fixes: dinosaur coats (`dcoats.py`), coat patterns (`coats.py`), boar stripes, deer spots |
| top level | `reg.mjs` + `hooks.mjs` the node loader; `r3.py`, `views.py`, `sheet.py`, `t_view.mjs` the render and view helpers some scripts call |

## Coat marks as dabs (2026-11-21)

A coat's hand-placed marks -- a snake's saddles and blotches, a lizard's bands and flecks, a salamander's spots -- were
each an `op: "paint"` shape of their own, probed onto the skin by the script (hundreds an asset: the grass snake's coats
766). They are now `dabs` shapes (bodyspec.js header, `sculpt.js` layDabs): ONE shape a run of marks gated by the same
`when`, each mark a row `[s, phi, la, lr, rot, colour, {...}]` measured on an axis (`along: [1, 0, 0]` and a polyline
over x for a lizard, a spline through the centreline for a snake), or `{ o, d, ... }` with a ray of its own (the head's).
The ENGINE lays them when the body is meshed (`bodymesh.js` ready: the same ray-to-the-skin a script did, so they ride
any girth or young), and the field keeps the set as one primitive with a grid over its marks (a vertex asks only the
few near it: the paints' share of the mesh time down ~3x); the pictures' baker (deutsch `tools/syncbeasts.mjs`) expands
them back to paints with `dabsLaid`.

`herps/dabs.py` writes them: `Dabs(axis=[[x, y, z, R], ...] | axis_fn=axis)` then `.spot(s, phi, ...)`, `.ray(o, d, ...)`
(a ray from the straight axis square to x becomes a row by itself), `.ring`, `.stroke`, `.rays`, and `.shapes()` -- a new
set wherever `when` (or `mirror`) changes, each in its commonest colour. The painters use it: `snakelib.Snake` (always),
`lizlib.Marks(SP, SH, axis=axis)` and `hlib.Painter(SP, SH, axis=axis)` (with an axis; without one they probe and write
paints as before -- agama, iguana, skink, chameleon, tree frog still do), each keeping its own depth and softness rules
(`depth: [f, m, g]`, `soft`), so the marks land where the probed ones did. The old grass snake's are `var/snakemarks.mjs`'s
(`node --import ./reg.mjs var/snakemarks.mjs MARKS.json && python3 var/snakejson.py --marks MARKS.json
../../assets/creatures/others/snake.json`: its axis the trunk tubes' own points, girth expressions and all).

## Fins as sheets, manes as brushes (2026-11-21)

Two more runs of repeated shapes made ONE shape each, the way `dabs` did for coat marks:

- `sheet` (sculpt.js prepareSheet, bodyspec.js header): a flat part -- the manta's wings (`mwing0..2`), the plesiosaur's
  flippers (`fore0..2`, `hind0..2`) -- was a fan of `tri` faces each smooth-unioned into the body (177 on the manta, 192 on
  the plesiosaur). It is now `{ type: "sheet", pts: [[x, y, z, r], ...], tris: [i, j, k, ...], bones, skin }`: the
  UNION of its faces (the nearest face's distance, r eased across it), one primitive blended into the body by its `k`,
  its faces grouped six to a bound so a point asks only the near ones. Its skin weights ease per point across the
  nearest face (`skin[i]` the index into `bones` of point i). The old per-face union swelled up to k/4 along every inner
  edge and piled at the fan's vertices (the "ribbed belly"); the sheet has none of that, so it lies a little inside the
  old surface (median ~1 mm, at most ~7 mm on the edges). Written by `sealib.sheet(pts, r, color, bone=...)` (fin()'s
  ear-clipped faces; a callable `bone` gives `bones`/`skin`): `sc/sea2/gen/ray.py` and `sc/sea3/gen/plesio.py`. The
  plesiosaur's file is no longer plesio.py's whole (teeth.py since), so `sc/sea3/gen/plesio_flippers.py` puts only the
  flipper lines in. A thin sheet becomes `tri` details; deutsch `tools/syncbeasts.mjs` expands sheets to their `tri`s
  with `sheetsLaid`.
- `brush` (bodyspec.js brushTufts): the zebra's stiff mane was 198 `tube`s (66 tufts x 3 rows). It is one shape: a
  `roots` and a `tips` polyline (n tufts along them), `rows` [[shift, dz, len]], `r` per tube point, `spread`, `bury`,
  `vary`/`seed` (the tip jitter, the whisker rng), `palette` + `pick` (the stripe colour per tuft). It is made into the
  same tubes (same ids `brushNa/b/c`, colours, roots, radii) when the body is converted, so nothing downstream sees it;
  the tips differ from the old by at most 5 mm (the engine's jitter, not Python's). `var/mane/mane.py` writes it. The
  donkey's (`dozen/donkey.py`, 90 tubes) and the wildebeest's (`rework/bigmam/wildebeest.py`, 68) brush manes could take
  it next; the horse, pony, unicorn and pegasus manes are LOCKS (`lkA`/`lkB`), not brushes.

SECOND ROUND (2026-11-22). The brush took `each` (a tuft at every root point: tufts measured one by one), `first` and
`tuft` (one run of tube ids over two brushes on two bones) and `lift` (each point's bow up, metres): the donkey's mane
(`dozen/donkey.py`, 90 tubes -> one brush) and the wildebeest's (`rework/bigmam/wildebeest.py`, 68 tubes -> two, the
neck's and the body's), both re-run and laid back to the same tubes (to 0.1 mm). `dozen/dlib.py` scale_shape, move and
stretch now know a brush's `roots`/`tips` (and a sheet's pts). The sheet took `ids` ([prefix, first]: its faces' ids
when they were written prefix0, prefix1 ...). `sharp/tri2sheet.py FILE.json ...` makes the runs of `tri` faces in a JSON
as it stands into sheets -- a run one fin's faces next to each other alike in every other key (bone, r, k, colour, pat,
frame, mirror), so each sheet lays back to exactly the faces it was (`--min`, default 6 faces; `--dry`): seal and walrus
(the hind flippers' two plates each -- field parts, so their ribs are gone as on the plesiosaur), eel (fin7), lionfish
(web, soft, anal, caudal, the pectoral rays and web), pike and swordfish (dorsal, anal, caudal). The fishes' fins are too
thin for the grid -- tri details either way -- so their meshes are the same to the triangle. Left as faces: the
clownfish (30 faces, the runs short), the eel's dorsal and anal (two to four faces a bone), a fin's last few faces on
another bone (pike, swordfish). `sc/sea3/gen/cetlib.py` plates() writes sheets now (seal.py and walrus.py no longer
reproduce their files whole; their flippers come out as tri2sheet made them).

Shapes: zebra 304 -> 107, ray 236 -> 63, plesiosaurus 236 -> 50; donkey 145 -> 56, wildebeest 138 -> 72, seal 96 -> 46,
walrus 134 -> 94, eel 104 -> 93, lionfish 177 -> 52, pike 104 -> 49, swordfish 70 -> 34. Mesh time (node, bodycache off): the manta 3.6 s ->
2.8 s, the plesiosaur 3.8 s -> 2.1 s, the zebra unchanged; triangle budgets unchanged (within 2).

THIRD ROUND (2026-11-22): BUNDLES. A run of shapes no rule makes -- a horse's locks draped over the probed neck, a
bumblebee's pile, a mosquito's antenna whorls, a butterfly's wing-pattern panels -- is one `brush` holding each one's own
keys (bodyspec.js brushStrands): `strands: [pts, ...]` (tubes, or horns with `kind: "horn"`) or `items: [{...}, ...]`
(any kind: the butterflies' `kind: "fin"`, each item its root and edge); the shared keys (bone, k, sides, mirror, when,
thick, slope ...) once; colours one `color` or `palette` + `pick`; ids tuft/id + (first + i x step) (the pony's near-side
lkL32, lkL30 ... lkL0: `step: -2`), or with `per` + `groups` id + group + "_" + j (antMHair1_0 ... antMHair12_5). It is
made back into exactly the shapes it was, in order, before anything sees them: the meshes are the same (checked by a hash
of every LOD's arrays, the mosquito's male variant too). `sharp/runs2brush.py [--min N] [--only REGEX] [--dry] FILE.json`
makes a JSON's runs of like tubes, horns or fins into bundles (a run: next to each other, alike in every key but the id,
colour and own points, the ids one numbering; default 10 or more). Written by their scripts: `var/mane/mane.py` (horse,
unicorn, pegasus: lkA, lkB), `rework/bigmam/pony.py` (`dlib.bundle`; `dlib.load` makes a file's bundles back into tubes
for the scripts that rework them, as donkey.py's lock drop), `rework/insects/insectlib.py` dump (`BUNDLE`: the mosquito's
and bumblebee's hairs, the butterflies' foreP/hindP panels). The horse, unicorn, pegasus, fritillary and butterfly files
are no longer their scripts' whole (later passes), so they were converted with runs2brush.py as they stand.
Left: the centipede's femurS/tibiaS spines (15 each, but one or two a leg between the leg's other parts and bones: no
run), the unicorn's 10 tail tubes and lkC (6-9), the tortoiseshell's hindP (8).

The zebra's brush (TODO: "reads a little too regular, like a comb") took `lean: [along, across]` (each tuft tipped its
own seeded way, shares of its length) and `jog` (each tuft's place along the crest +- that share of the spacing), drawn
only when set (the donkey's and wildebeest's come out as before): mane.py writes vary .12, lean [.18, .1], jog .25.

Shapes: horse 127 -> 67, pony 144 -> 68, unicorn 145 -> 85, pegasus 153 -> 93, mosquito 131 -> 37, bumblebee 134 -> 48,
fritillary 92 -> 24, swallowtail 76 -> 24, purple emperor 64 -> 24, tortoiseshell 47 -> 31, butterfly 53 -> 24.

## Reproducibility (checked 2026-11-07)

Each script run (with its species names where it takes them) and its output compared with the JSON as it stood that
day, then the JSON restored.

**Reproduce today's files exactly:**
- birds: `newbirds.py`, `newbirds2.py`, `raptor.py`, `hornbill.py`, `duck.py`, `eagle.py`, `heron.py`, `owl.py`, `parrot.py`, `peacock.py`, `wader.py`, `varB.py`, `swan.py` (2026-11-08: the duck, the swan, the flamingo and the heron fly on `nbwing.aloft`'s spread wing, the goose's; their old rig, `bg.rig_fold` -- the folded wing swung out -- read as loose blades. Nothing uses rig_fold now; the chicken and the peacock have no flight at all. flamingo.py and heron.py are run into a scratch copy and only their wing parts merged into the JSON, whose bills the review pass had re-made).
- sea: every script in `sc/sea2/gen/` and `sc/sea3/gen/` (fish family, crab, octopus, ray, eel, dragonfly, shark, dolphin, orca, humpback, seal, walrus, plesiosaur). (2026-11-21: plesio.py no longer -- teeth.py finished it; ray.py still does, its wings sheets now)
- primates and the kangaroo: all of `sc/prim/gen/`.
- `sc/new6/` (all but the impala), `sc/m5/`, `sc/ptero/gen.py`.
- carnivores: `bear.py`, `leopard.py`.
- ungulates: `camelid.py camel|bactrian`, `cervid.py deer|cervicapra`, `suid.py boar`, `giraffe.py`.

**Run, but a later step finished the species**, so their output is the earlier state:

| script | finished afterwards by |
|---|---|
| `giants/gen_*.py` (dinosaurs, elephant, hippo, rhino) | dinosaur coats `aud/dcoats.py`; the elephant's tail `giants/eletail.py`; audit edits |
| `equid.py horse|zebra` | `var/mane/mane.py` (lock mane; the zebra's brush mane -- one `brush` shape since 2026-11-21), coats |
| `cervid.py reindeer` | `var/rnd.py` (the bull's antlers; input `var/reindeer_r1.json`) |
| `cervid.py oryx`, `bovine.py cow|ox`, `ovine.py sheep|ram`, `suid.py pig` | audit edits (coats, horn tips) |
| `smilodon.py` | `sc/carn/gen/sabres.py` (the mesh sabres) |
| `tiger.py`, `lion.py` | `var/tgr.py` (ruff, coat, agouti ticking) |
| `bat.py`, `canids.py` (wolf), `cat.py`, `small.py` (rat, squirrel) | later edits (the bat's wing membranes; coats) |
| `impala_base.py` | `sc/new6/chamois.py` builds on it |
| `sc/others/gen/` croc, frog, hydra, scorpion, snake, spider, turtle | coats `sc/aud2/coats.py`; `var/snakemarks.mjs`, `var/frogjson.py` |
| `birds/chicken.py`, `flamingo.py`, `rooster.py` | later edits to the JSON |
| `sea/gen.mjs` | superseded by `sc/sea2` and `sc/sea3` (it writes older shark, dolphin, fish, dragonfly) |

**The sharp pass (2026-11-08) comes after every generator:** `sharp/claws.py`, `teeth.py`, `spikes.py`,
`antlers.py`, `bills.py` (and `horns.py`, `named.py`) rewrote the pointed parts of the species they list (their `SPEC`
tables) as `horn`s. A generator above re-run for one of those species writes the old field shapes back: run the
matching sharp script for it afterwards (`python3 sharp/bills.py chicken`, `... claws.py all` -- each converts only what
is still a field shape, so it is safe to run on a converted file). Then `sharp/review.py` (the review's fixes: gull,
duck, crocodile teeth, reindeer palms, cockatoo, cockatiel, pelican, the theropods' hands, pachycephalosaurus knobs,
flamingo, and `claws` -- every claws.py claw's root faired into its toe) for the species concerned: `python3 review.py
claws:bear`, `python3 review.py gull` (run from `sharp/`; `claws` before `dilophosaurus` / `allosaurus` / `tyrannosaur`). The EARS: `python3 sharp/ears.py` (zebra, giraffe, kangaroo) and `python3 sharp/ears2.py SPECIES` (the rest) after a generator rewrites a head. The REINDEER's antlers: `python3 sharp/caribou.py` (run from `sharp/`, after `antlers.py`; `review.py reindeer` now runs it: a caribou bull's beam, crown, bez and shovel palms as `fin` sheets with `horn` tines rooted on their rims, the cow's tips re-tapered). PLATES and CRESTS: `python3 sharp/plates.py stegosaurus dilophosaurus` (the stegosaurus's 19 dorsal plates and the dilophosaurus's twin crests as faired `fin` sheets, rooted on the back / skull measured with `fd.mjs`).

**Superseded, no longer run:** `sc/others/gen/manticore.py` and `unicorn.py` expect fields the JSON no longer has
(the manticore's and unicorn's later rework; the manticore's wing skin is `var/isl/mantwing.py`'s since 2026-11-08 -- its
wedge plates, covers and their bones are gone).

**Patchers** take files as arguments (`IN OUT`, or a name): `sabres.py`, `var/*.py` (`mane/mane.py IN OUT MODE`,
`gri.py`, `peg.py`, `tgr.py`, `rnd.py`, ...), `giants/tailfix.py`, `sc/sea3/gen/install_pat.py`. Read the header
comment for the arguments.

Comments in the scripts still say "scratchpad X": that is `tools/creaturegen/X` now.
