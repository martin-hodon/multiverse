# Scenes shared by the 2D engines

Stained glass and mosaic tell the same stories; what differs is what happens to a drawing afterwards. Glass cuts pieces to panes and leads; a mosaic lays stones. So who is in a picture, in what clothes and doing what, is data in one canon, and each engine has only its styling. A seed gives a different picture: which scene, who plays it, how it's arranged, in what frame and colours. The same seed always gives the same picture.

| file | what it holds |
|---|---|
| `story/seed.js` | the seed's grammar, shared with Greek: `stream` (one per label), `pick`, `resolve` (`{ of }`, `{ p, v }` in data), `one`, `shuffled`, `scramble` |
| `story/roles.js` | also shared with Greek: `rolesOf` (a scene's roles, `variants`, `beats`, `chain`), `planDeck`, `shuffledDeck` |
| `story/compose.js` | `composeScene`, `personPieces`: a name and a seed to stacked polygons in a frame, colours in the caller's slots. No glass or stone in it |
| `medieval/figure.js` | `buildFigure`: the frontal body; poses and attributes come from the canon |
| `tools/storygen.py` | writes `assets/story/canon.json`: `poses`, `attrs`, `things`, `cast`, `standing`, `scenes`, `beats`, `cycles`, `tints` |
| `story_lab.html` | the scenes flat, before any styling: `?name=` or `?cycle=` or `?people=all`, `&seeds=1,2`, `&cell=`, `&w=` |

Edit the generator, not the JSON.

## What is shared, and what isn't

There is one seed grammar and one way to deal roles, in `story/`, and Greek, glass and mosaic all use it. Scenes in the canon have the same shape as Greek's (`roles`, `variants`, `beats`, `slots`, `chain`).

There are two kinds of body, on purpose:

- **Greek's rig** (profile, solved by IK, bodies aiming at each other and checked for faults) draws bodies in action. Greek's paintings and the `emblem` mosaics use it, and so now do Roman floors' hunts, fights and triumphs (below).
- **The medieval frontal figure** is what glass and Byzantine walls are made of, and Roman floors' still subjects (Orpheus, the seasons, Neptune among his creatures). Late antique and Byzantine art is frontal and hieratic too, so one figure serves Chartres and Ravenna. Its beasts are drawings in the canon, so these don't depend on Greek's data.

### What stays frontal on a Roman floor

Only what real pavements set frontally: Orpheus in the medallion at a wheel's hub (`orpheus-hub`: Palermo, Paphos) and the seasons' heads in the corners (Cirencester, Bignor: `bust: "head"`, cut at the shoulders, the attribute over the shoulder). Everywhere else Orpheus sits side on and the beasts come in to listen (`rom-orpheus`), and Neptune among his creatures rides a sea horse with dolphins alongside (`rom-neptune-sea`), side on as at Ostia.

### The Roman rig

The canon's `rig` section (`tools/storygen.py`) holds what's Roman in Greek's format, and `mosaic/floor.js` merges it over Greek's data at use, so Greek's canon and its hashes don't change:

- `beasts`: `boar`, `stag`, `hound`, `panther`, `hare`, `hippocamp`, `dolphin`. A beast with no `hind` is what ends in a fish's tail (`greek/beast.js`), and one with no `gaits` is a drawing.
- `cast`: `venator`, `venator-rider`, `murmillo`, `retiarius`, `auriga`, `fallen-murmillo`.
- `scenes`: `rom-*`, as Greek's scenes.
- `of`: the story scene each one stands for (`hunt-boar` to `rom-boar`). `near`: the same for square or round frames, only those the story can't do without, so they're drawn large rather than crowded. `emblems`: an emblem's other seeds, the same subject told differently, its own seed keeping the painting it has always had.

The layer is `{ kind: "rig", scene, seed, frame, within, tech, mono, earth, water, foam, tree, paper, stone }`. It isn't `sparse`: pressed into a square frame, a hunt's bodies stand in each other. It looks at where the picture came out, then lifts it off the floor of a tall frame, runs earth under its feet (or the sea, for a scene with `water`), and puts a tree in the room left at its side. `mono` is Ostia's: black-figure with no added red. Without Greek's data registered, a floor falls back on the frontal scene of the same name.

`scramble` exists because close seeds give close first draws from a `stream`. Greek's pictures are fixed by those draws, so `stream` stays as it is, and new code scrambles its seed first.

## The canon

- A **person** in `cast` is what tells them apart: dress (`robe`, `mantle`, `cut`, `veil`, `mitre`, `crown`...), `holdL`, `holdR` and `underfoot`, `beside`, a `pose`. Any value may be a choice. `standing` lists who can stand alone in a window.
- A **thing** is a drawing with colours by name, optionally anchors (`seat`, `mouth`). A piece with `span` runs out to the frame (ground, water); `stars` lie in fractions of it.
- A **scene** places roles: `R(cast, pose, at, face)`, `T(thing, at, y, size)`, `B(beast, at, face, gait=)`. `on` rides or sits on another role; `reach` puts a hand on someone; `p` is a chance of being there.
- A **cycle** is a list of scenes: `infancy`, `passion`, `genesis`, `lives`, `months`, `guilds`, `byzantine`, `seasons`, `sea`, `xenia`, `hunt`, `arena`, `triumph`, `animals`.

Colours are the 14 names in `tints`. An engine passes `dye`, its own map from name to palette slot, and `ground`, the name of what's behind: nothing stands in the colour it stands on. `float` (a mosaic's) sits a picture up off its frame's foot on a thin ground, where a window's stands on the sill; water runs down to the foot.

## Adding

A new scene or saint needs only `tools/storygen.py`; both engines have it at once. Check it flat in `story_lab.html`, then in each engine.
