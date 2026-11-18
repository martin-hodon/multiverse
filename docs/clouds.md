# The clouds

The sky's clouds are **types** of the four families real clouds come in, drawn together in the sky dome
(`sky.js`) by one engine, `clouds.js`. A **sky** is a list of types, for example cumulus under cirrus. The world picks
one for its weather and changes it every few minutes.

| file | what |
|---|---|
| `clouds.js` | the engine: the types and skies, the easing between skies, the shader nodes (`compose`, `heapPass`), the baked noises |
| `assets/sky/clouds/*.json` | the 12 types, each a set of its family's numbers (asset manager: **Sky › Cloud types**) |
| `assets/sky/skies.json` | the named skies, which skies each weather and intensity draws from, `change` (seconds between skies) (asset manager: **Sky › Skies**) |
| `clouds.html` | the lab: one sky or `?types=a,b` over a meadow; `?hour=`, `?look=yaw,pitch`, `?t=`; K next sky, H the hour |

## The families

At most one type of each family is shown at a time. A sky with two of one family keeps the first.

| family | types | how it is drawn |
|---|---|---|
| **heap** | cumulus, congestus (towering), cumulonimbus, stratocumulus, fractus (scud) | a **volume**, marched (below) |
| **sheet** | stratus, nimbostratus, altostratus, cirrostratus | a layer at `height`: its cover from broad noise, `veil` (the sun shows through as through ground glass), `halo` (the 22° ring), `rain` (grey curtains toward the horizon), `waves` (undulatus) |
| **cells** | altocumulus, cirrocumulus | a layer of Worley cells, stretched (`stretch`), in rows (`rows`, `angle`), gathered in patches (`patchy`), shaded on the side away from the sun (`shading`) |
| **streak** | cirrus | the drifted wisps: long, thin, `hook`ed (uncinus) |

The numbers each family reads are listed in the header of `clouds.js`, where the uniforms are packed. Every JSON
type has `_about` notes saying what each number does.

## The heaps: a volume

`heapPass` draws its own dome round the eye into a picture a quarter of the screen's size, **before** the frame is
drawn (`sky.render(renderer, camera)`, called by each page). The sky's shader reads that picture through four
taps, which smooth away the march's jitter.

- **The march:** along the line of sight, over a round earth (so the layer runs down to the horizon), from the
  layer's base to its top. It takes 48 jittered samples, over no more than 7 times the layer's thickness.
- **The body:** a cover from the baked billow field (`cover`, gathered by `patchy`).
  - Its top is as high as the cloud is thick there (`taper`), so each heap is domed over a flat base.
  - A 3D lump field changes the cover as the cloud rises, so the sides bulge instead of hanging like curtains.
  - A 64³ Worley volume (`bakeCloudVolume`) wears the edges into billows (`detail`), more toward the top.
  - The anvil (`anvil`) spreads at 75–93% of the height over a tower's neighbourhood: the field blurred.
- **The light:**
  - two samples toward the sun (Beer's law, with "powder" at the edges);
  - forward scattering toward the sun (the silver lining);
  - the sky's light from above, darker at the base by `dark`, with a rain cloud's `dark` cutting the sunlight too;
  - far heaps fade into the horizon's haze.

The pass is skipped once its picture has cleared while there are no heaps.

## The easing and the world

`sky.clouds.set(list)` eases every number toward the new sky over `ease` (40 s):

- a family that is leaving fades out where it is;
- a family that is arriving starts at its own numbers with amount 0 and fades in.

`set(list, {now: true})` jumps straight to the new sky. `sky.update` steps the easing in real time.

In the game (index.html, `applyClouds`):

- The sky comes from `SKIES.weather[clear|rain|snow][intensity]`. P and O change the weather and the intensity,
  and a peer's weather does too.
- The world's seed picks which sky of that list, so peers in one world see the same sky.
- Every `SKIES.change` seconds the next one eases in. `?sky=NAME` holds one sky.
- `clouds.dim()` greys the sky and hides the sun's disc under a closed sheet.
- `clouds.shadow()` sets the land's cloud shadows (`cloudshadow.js` `CLOUD.cover`, `CLOUD.amount`): the heaps' and
  cells' cover, and none under a grey sheet (its light is all diffuse).

## Adding a type

1. Write `assets/sky/clouds/NAME.json` with `name`, `latin`, `family` and that family's numbers. Copy a type of the
   same family.
2. Add it to the imports and `CLOUD_TYPES` in `clouds.js`, and to the "Sky: cloud types" category in
   `assets/index.json`.
3. Use it in a sky in `skies.json`.

Look at it in `clouds.html?types=NAME`, at noon and at `hour=.4`, low (`look=70,6`) and high (`look=70,38`).

## Cost

In the medieval test world (1280×800), the heap pass costs about 4 ms of GPU under a fair sky and about 3 ms under a storm.
The skies with no heaps cost nothing extra. The levers, should it need to be cheaper:

- the picture's size (`heapPass` `scale`, ¼ now);
- `STEPS`;
- the two light samples;
- drawing the pass only above the horizon.
