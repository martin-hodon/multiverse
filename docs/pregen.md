# Pregenerated data

Most of a world's startup went into three pure functions of data that rarely changes. Measured on this machine
(headless Chromium, CPU profile to `window.__ready`, seed 1: Florence, Sacré-Cœur, Schwerin):

| what | before | with pregen/ |
|---|---|---|
| building finishes: the pattern TILES (a marble's veins, a plaster's clouds: noise per texel, in JS) | 10.0 s | fetched: 16 PNGs |
| building finishes: every surface cut and told inside from outside by rays (`finishPieces`) | 8.8 s | fetched: 3 geometries |
| the walk's WALL FIELDS (`archWallField`) | 1.7 s | fetched: 3 fields |
| the people's FABRIC layers (fabric.js) | 0.7 s | fetched: 22 PNGs |
| time to ready | 34.6 s | 21.3 s (main-thread JS ~26 s -> ~5 s; the rest is waiting on shader compiles, the terrain worker and the CDN) |

People themselves are not worth storing: the tailor dresses one in well under a millisecond once its fabrics exist.

THE TOWN (town.js) is laid out by the world's seed, so its buildings' geometry and wall fields are made at startup
(about 2-3 s for ~75 sites; they are not reported as misses: `pregenMiss` skips the "town" finishes and the
`village/*` definitions). Its TILES are cached: the generator bakes every tile each style can draw with, over all of
the style's stones, roofs, woods, plasters and timbers (`town.js styleFinishes`), under `town/<style>`, and the game
fetches its own style's with the landmarks'.

## Faces, butterflies' wings, loose items (2026-10-06)

Measured again (scratchpad boot profiler: CPU profile + wall-clock marks `window.__boot`), three more things were
being made at every start, and none was in the cache:

| what | cost (headless, this PC) | now |
|---|---|---|
| the people's mesh HEADS -- face, hair, headwear, earrings (heads.js: ~100 ms each, a world's ~60 on its first frame) | 6.3 s, the first frame | fetched when a head first needs it |
| the butterflies' painted WINGS (butterflies.js speciesAtlas) | 2.2 s | fetched: one PNG a species |
| the LOOSE ITEMS' tiles -- tools in hands, carts, the boat, the mills' sails (itemMaterial: noise per texel) | ~4.7 s | fetched with the landmarks', under "items" |

A face's cached SHAPE is everything but its size and its skin's and hair's colours: it is built at the canon's size
(the copy's matrix scales it to the person's head) in placeholder colours (`paintedGeometry`'s `recolor` paints the
person's on as it is drawn), keyed by kind, seed (of 16 since 2026-11-03; it was 5), the face's fullness (`full`: the body's fat, heads.js), hairstyle, fringe, stone, headwear and earrings -- and by the
definitions it is made of (faces, hair, jewelry, the blooms, the materials). The generator draws people AT RANDOM, as
the world draws them -- every style of dress, every kind, `?faces=N` seeds of each (18) -- and keeps the heads they
would wear. A person whose exact head is not there gets another of its FAMILY (same kind, hair and what is worn: a
different seed's face); a family not there at all is built at startup as before. Each run keeps another random lot.
Each recorded face also records its FAR shape (2026-11-22: heads.js `FAR`, the same head at `detail` .7 for those more
than 10 m away; its family ends `|far@0.7`). The game takes those like the near ones; one not in the cache is built
in a worker (faceworker.js), never at startup or on the main thread.

THE WORLDS. After that first pass `pregen.py` opens the game itself (`--worlds N`), as
`index.html?pregenrecord=1`: a world built as always, with `pregen.js` recording (RECORD_WORLD) whatever it
had to make that the cache has not got -- its seeded furniture's and tools' tiles, the faces of families the random
people missed -- written out after sixty frames as a fragment, and merged into the manifest: the new files, and under
the entry "world" every tile a world used (the game asks for it with "items" and its landmarks'). Each run keeps
another random lot.

LANDS AND TOWNS. The grown map (mapgen.js `growMap`: the terrain lab's 150,000 years on the GPU, most of a start's
waiting -- ~8 s) is kept by its seed (section `maps`: the lab's fields H, W, Q and its stats; the cut, the river and
the roads are worked out from them as before). A recorded world also keeps its TOWN: its houses' finished geometry
and wall fields, under "world/<seed>". And with no `?seed=` the game picks its world AMONG THE CACHED SEEDS
(pregen.js `cachedSeeds`): its land, its town and its tiles all fetched. `?seed=N` opens any other world, grown and
built at startup. The cache keeps `--worlds N` of them (default 4; each needs ~2 GB while it runs): a run first
records again the lands it kept whose towns it has lost -- the same worlds, built by today's code (the lands
themselves are carried over while the code that grows them is the same) -- then new seeds until it has N.

EARLY. `pregen.js` fetches the manifest, every fabric, the wings and the list of faces AS IT IS IMPORTED (a top-level
await): species.js builds its winged people and centaurs while the modules load, and their cloth was drawn from scratch
before `loadPregen` came. `loadPregen(buildings)` then fetches only the buildings' geometry, wall fields and tiles.

Measured (headless, this PC, a cold start to ready + the terrain + 60 frames): 82 s with the cache stale, 33 s with
the old cache, 20 s with all of this -- what is left is the WebGPU device and the shaders' first compiles, the 1,130
asset files, and the town's own houses (laid out by the world's seed, made at every start by design).

## Sections

The manifest checks each SECTION against the code that makes it (`pregen.js SECTIONS`): `tiles` (tiles and fabrics:
pregen.js, patterns.js, expr.js, fabric.js, glyphs.js, murals.js), `maps` (the grown lands: terrain_lab.js), `buildings` (finished geometry and wall fields:
architecture.js, arch/finish.js, arch/solid.js and the patterns), `faces` (heads.js, items.js, face.js, hair.js, thorns.js,
jewelry.js, petals.js, defs.js, expr.js), `wings` (butterflies.js). An edit retires its own section only -- before, one
code hash covered everything, and a line changed in architecture.js sent every start back to drawing every tile.
The buildings' SHADERS live apart, in archmat.js (glass, the pattern materials, the finish tiles' material, moss and
snow): they change how a surface looks, never its triangles, so they are in no section -- before 2026-10-23 they sat
in architecture.js, and every tweak to a look (the roofs' moss, the grain's gusts) retired the whole buildings cache.

## How

    python3 build/pregen.py                          # every landmark, every fabric, the loose items, the wings, a random lot of faces, the worlds -> pregen/
    python3 build/pregen.py --resume                 # carry on a run that stopped, from the parts it had finished
    python3 build/pregen.py --worlds-only --worlds 4 # only record worlds, into the cache as it is
    python3 build/pregen.py --bodies                 # only bake the creatures' shapes -> pregen/shapes/ (docs/engines.md "Faster shapes, baked shapes")
    # (2026-11-22: the very far body mesh, bodyfar.js, is made from the dressed far mesh at run time -- it is not baked, and the shapes' hash does not cover it)

It opens `pregen.html` headless (build/headless.py, shared with build/textures.py) ONE PART AT A TIME -- six
landmarks, the towns' tiles, the items, the wings, the faces, the fabrics (`pregen.html?part=list` names them) --
each in a browser of its own, which builds them through the game's own code with `pregen.js` RECORDING what was made,
and writes it at once: tiles and fabric layers as PNG, finished geometry (`arch/finish.js` groups) and wall fields as
gzipped binaries, and its part of the manifest (`parts/<part>.json`), merged into `manifest.json` (which files each
landmark needs) when all are done. It writes beside the old folder (`pregen.new/`) and swaps it in, so a failed run
leaves the old cache alone. (Until 2026-10-23 one browser built the whole cache and held all of it until the end: on
this PC, with the rest of the desktop open, it was killed for want of memory.)

MEMORY. Before each browser it checks the memory free (/proc/meminfo MemAvailable) against what such a browser needs
(`NEED`: the peaks measured, with a margin), and if there is not enough it stops, saying so -- the parts finished
are kept, and `--resume` carries on from them (`--worlds-only` for the worlds). Each part's line ends with the most
its browser held (`browser peak`, sampled each second: build/headless.py `stats`).

The game (`index.html`) chooses its town, then `await loadPregen(townKeys)` fetches those landmarks' files and every
fabric (a few hundred milliseconds) before anything is built; the builders look there first
(`archmat.js finishTile`, `architecture.js finishMeshes / archWallField`, `fabric.js fabricIndex`).

## Never stale

Every entry is filed under a HASH of what made it: a tile under its pattern and every pattern it uses, its palette,
params and resolution; a building's geometry under its assembly's actual triangles and instances (whatever
definitions and components produced them), its finish and the sizes of the finish's patterns; a wall field under the
assembly and the cell; a fabric under its pattern. And the manifest records a hash of the code that makes them
(`PREGEN_SOURCES`: pregen.js, architecture.js, arch/finish.js, arch/solid.js, patterns.js, expr.js, fabric.js) --
when the game can read those sources (the dev setup) it checks them, and if they changed it ignores the cache.

So after editing a building, a finish, a pattern or that code, run `build/pregen.py` again. Until then the game builds
what changed from scratch, exactly as it did before pregen/ existed, and says so in the console
(`pregen/: made from scratch after all -- ...`). Without a pregen/ folder nothing changes at all.

The folder is generated, not source (`.gitignore`). A distribution build (dist/bannerfield.html, one file) looks for
`pregen/` beside itself when served over HTTP.

## The statues' smoothing (2026-11-03)

Measured again (seed 353465086, Greek, CDP CPU profile to `window.__ready`): ready at 117 s, 90 of them in the FIRST
FRAME, and 73 s of those in heads.js `smoothNormals` -- the carved heads' normals (`CARVED_SMOOTH`, docs/arch.md) were
averaged over every COPY of every vertex (the geometry repeats a vertex in each triangle it is in: some six times as
many points, some thirty-six times the pairs), and `stoneFaceGeometry` did it again for every statue of a shape. Now it
works over the surface's own points once each (same position, normal and kind), each weighted by how many copies it
stands for -- the same sums, to 1e-16 -- and a carved shape's smoothed normals are kept like a living face's. Ready
at 36 s. Most of what is left is the cache being stale (pattern tiles 8 s, wall fields 5 s, faces 4 s: the sources
it hashes changed since the last `build/pregen.py`).

## Re-run, 2026-11-22

Before: the manifest of 2026-11-02, tiles, buildings, faces and wings stale (the game ignored them: "made by other
code"), pregen/shapes/ baked by other mesher code -- only the two worlds' maps were taken. `python3 build/pregen.py`
(full: the parts, the bodies, four worlds) ran in 734 s for the parts plus about 4 x 70 s for the worlds, browser peak
3.7 GB (a world), 0 errors.

| | 2026-11-02 | 2026-11-22 | why |
|---|---|---|---|
| total | 215 MB | 412 MB | |
| buildings + fields | 71.5 + 12.3 MB, 80 buildings | 142 + 29 MB, 105 | 22 landmarks added since (Grand Palace 7.9 MB, Alhambra 7.8, Park Guell 6.3, Cordoba 5.7, Hohenzollern 5.6 ...); 4 world towns for 2 |
| tiles | 69.5 MB, 523 | 87 MB, 1016 | the landmarks' and the worlds' tiles (the items' are 523 alone) |
| faces | 29.8 MB, 412 | 91 MB, 1710 | the far shapes (855, 33 MB -- none before: they did not exist on 2026-11-02) and their near twins (855, 58 MB); 370 families |
| shapes | 28.8 MB, 217 | 64 MB, 446 | the species rework and the insects (166 bodies a medieval town draws) |
| maps | 2 | 4 | worlds 1181487403, 547745597, 1340756457, 584735322 (the two old ones gone with their towns) |

Each face entry now says its `seed` (pregen.html, the world fragments): heads.js takes the same seed for a stand-in
face's near and far forms (docs/face.md, Far heads).

Loads (headless real GPU, scratch harness: 9 s from `ready`, a 16 s walk through the biggest crowd, an 8 s spin):

| | ready | near heads built | far built in the worker | made from scratch |
|---|---|---|---|---|
| medieval seed 7, stale cache | 42.6 s | 171 (4.1 s) | 170 (5.0 s) | everything |
| medieval seed 7, fresh cache | 31.0 s | 27 (0.9 s) | 27 (1.3 s) | 58 entries: the map, the mine, 4 face families near and far (not a recorded world) |
| a recorded world (no ?seed) | 15.3 s | 0 | 0 | nothing |

Frame times, seed 7: load mean 45 → 65 ms, walk mean 37 → 54 ms (p50 33 → 50), spin 25 → 32 ms. Not the cache's
cost: with the shapes baked every creature is there from the start -- 166 bodies against 43 the stale run had built
by its end, 169 skinned meshes and 750k triangles drawn against 60 and 303k (the scene 3.31M → 3.96M at the walk's
start). Near the crowd the frames are the same or better (34 → 31 ms at 20 m, 28 → 27 at the crowd). In a recorded
world: load mean 36 ms, walk 49, spin 27, nothing built.
