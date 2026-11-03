# Ships

The vessels are items (`assets/items/ships/`, the item language in docs/items.md), written by `tools/shipgen.py`
with their components (`assets/items/components/`), and the world's choice of them is data:
`assets/world/ships.json`, written by the same script. `python3 tools/shipgen.py` rewrites the ships, the components
and ships.json; it never rewrites `assets/index.json` (it prints what the catalogue lacks; `--index` only appends)
and adds a material to `assets/items/materials.json` only when the library has none of that name.

## The frame

The stern at x = 0, the bow at +x (the hull's length `L`), y up from the keel's lowest point, z across (starboard
+z). The two propgen boats (`barge`, `fisher-boat`, tools/propgen.py) are the exception: their origin is the
waterline amidships (ships.json says `frame: "centre"`).

## The catalogue (40 + 2)

dugout, reed boat, Egyptian river boat, trireme, Roman merchantman, longship, knarr, cog, carrack, caravel, galleon,
galley, dhow, junk, sampan, outrigger canoe, voyaging canoe, gondola, birchbark canoe, kayak, umiak, coracle,
fishing boat, skiff, fluyt, xebec, felucca, ship of the line, frigate, East Indiaman -- and, 2026-11-03, the large
ships the periods lacked:

| ship | period | L (m) | what |
|---|---|---|---|
| `punt-ship` | Egypt, -2500..-1000 | 21-25 | Hatshepsut's Punt ship: hogging truss over crutches, beam ends, papyrus-umbel stern, wide sail between yard and boom, 15 oars a side, two quarter steering oars, end platforms |
| `gaulos` | Phoenicia, Greece, -1100..-300 | 18-24 | the round merchantman: equal posts, horse-head stem, wicker fence, crow's nest, amphorae in the open hold |
| `dromon` | Byzantium, 500..1200 | 30-34 | bireme of 2 x 25 oars, two lateens, spur, Greek-fire siphon under a forecastle, xylokastron, stern tent, shields |
| `kadirga` | Ottoman, 1450..1800 | 40-46 | galley: three bow guns, red-canopied köşk with three lanterns, gilt band |
| `hulk` | Hansa, 1300..1550 | 28-34 | banana hull, aftcastle and forecastle, main + topsail, fore, lateen mizzen |
| `treasure-ship` | Ming, 1400..1500 | 55-64 | baochuan: six junk masts (two off the centre line, the fore raked), red sails, two storeys of stern cabins, deep rudder, bow eyes |
| `bezaisen` | Edo Japan, 1650..1870 | 24-30 | sengoku-bune: raked stem, open transom with a huge rudder, kakoi side boards, one great cotton-strip sail |
| `atakebune` | Sengoku Japan, 1550..1640 | 30-42 | a fortress on a flat hull: the full-length shield box (tatebita) with black posts, sill and cap, a row of loopholes and 26 oar ports a side, a gate amidships each side; a fighting deck on its roof behind a loopholed parapet; a three-storey white yagura over black boards under tiled eaves, gilt finials; one matting square sail; banners |
| `maya-canoe` | Maya, -500..1550 | 14-18 | the great trading dugout: raised flat ends, thatched shelter, jars, paddles |
| `koch` | the Russian north, 1400..1800 | 18-24 | Pomor koch: round ice hull with an ice belt, deckhouse, main and fore square sails |

New materials: `sail-cotton` (the strips of a Japanese sail), `sail-red` (the junks' tanned sails), `thatch`.

## States (params)

Every ship takes them as params (buildItem `params`), else its seed picks:

- `set`: `full` | `furled` -- every sail on board: square (rolled on the yard), lateen (rolled along its yard), junk
  (lowered, the battens stacked on the boom), crab claw (the spars brought together), the headsails (stowed along
  their stays), a spanker or jib drawn straight into the ship.
- `oars`: `out` (thrust out and dipping, rowing) | `shipped` (a third of them laid fore and aft inside the
  gunwale) -- only a ship that has a bank of oars (or paddles).

ships.json `states` names the poses: `moored` {set furled, oars shipped}, `sailing` {full, shipped}, `rowing`
{furled, out}, `under way` {full, out}. A ship's `params` in ships.json lists which of the two it takes.

## Anchors (markers)

`fit_out()` in shipgen gives every shipgen ship, from its hull lines (so they sit on the hull it draws):

| role | where | data |
|---|---|---|
| `waterline` | amidships on the centre line at the load waterline (`D * wl`; `params.wl` the share) | `{draught}` |
| `moor` x 2 | on the bitts it draws (a decked ship with a hatch), else on the stem- and sternpost heads | `{end: bow \| stern}` |
| `gangplank` x 2 | on the rail at its `plank` share of L, both sides, yawed outboard (-90 starboard, 90 port); a twin hull's on its outer sides | `{side, deck}` |
| `hold` x n | over each hatch it draws (decked ships), else on the open boat's floor | `{i, w, l, floor}` / `{i, floor}` |
| `helm` | where the steersman stands | -- |

It also draws the hatches (`components/hatch`: coaming and grating), the bitts (`components/bitts`) and the lower
shrouds of every upright mast (n a side from the masthead to the rail, and three to each topmast's top), with a
hint of ratlines where there are three shrouds or more (five rungs a side, about 120 triangles a mast).
A FIT entry may put the gangplanks elsewhere than the rail (`plankY`, `plankZ`, `plankDeck`): the atakebune's are at
the gates in its shield box, on the hull's deck inside.
The propgen boats (tools/propgen.py) carry the same roles in their centred frame: the `barge` `hold` x 10, `plank`
(the gangplank's foot on the quay), `waterline`, `moor` x 2 (its bollards), `gangplank` x 2, `helm`; the
`fisher-boat` `waterline`, `moor` x 2, `gangplank` x 2, `hold`, `helm`.

## assets/world/ships.json

```
{ name, kind: "ships", _about,
  states:  { moored | sailing | rowing | under way: { set, oars } },
  anchors: { role: what it is },
  ships:   { id: { item, name, type: merchant|war|small, drive: sail|oar|paddle|pole|sail+oar|sail+paddle,
                   crew: [min, max], length: [min, max] (hull m), beam (m), draught (m, keel to waterline, at the
                   middle size; null for the propgen boats), cargo: { tons, holds }, era, region,
                   frame: stern|centre, params: ["set", "oars"] } },
  cultures: { period: { merchant: [[id, weight]...], war: [...], small: [...] } } }
```

`cultures` is keyed like `assets/world/goods.json` (freight.js `goodsCulture`): the world's period, else its
dress's first style that has an entry, else `default` -- greek, roman, egyptian, chinese, japanese, indian, maya,
medieval, byzantine, ottoman, islamic, russian, industrial, default. The crews and burdens are estimates (said so in
each ship's `_about`, with the sources of the sizes).

## Fixed 2026-11-03 (the audit at true scale, next to a 1.75 m figure)

- Every lateen flew backwards (the peak forward, the tack high in the air): its tack is now forward and low, made
  fast near the stem or the deck (`lateen_rig`: the yard's slant follows from the tack's height), its mast ending
  at the yard's sling; its third corner no longer doubles the first (a degenerate fan drawn black).
- The crab claws rose forward, away from their masts: they rise aft and rest on the mast (`crab`).
- The 18th-century ships' giant black-backed jib is a jib and a fore staysail (`headsail`), their masts shorter
  (0.57-0.58 L).
- The steering oars hung straight down under the keel: they trail aft.
- The trireme's sail was always furled: it follows `set`.
- No rigging but a few stays: the shrouds above.
- Second pass: the atakebune rebuilt as a fortress (it read as a boxy barge); the xebec's stern a platform on its
  counter with knees and a rail (it was a board floating behind the transom); the galleon's beakhead pointed forward
  (it stood across the bow) and its spritsail slung under the bowsprit and sheeted to the beakhead (it hung off it
  like a flag); the barge and the fisher's boat given the anchors.

## Not there yet

Running rigging and braces (ratlines only hinted); crews at the oars; the hull planking texture is coarse at close
range.
