# The assets: what things ARE, as definitions

Everything in the world that has a shape is written down as JSON, under `assets/`, and built by the same code
the game runs. Nothing in `assets/` draws; nothing that draws holds numbers.

    assets/index.json                 the catalogue: every asset, by category
    assets/creatures/frames/*.json    BODY PLANS -- the horse, the big cat, the sheep, the deer
    assets/creatures/mammals/*.json   a species: the frame it stands on, its size, its colours, what it carries
    assets/creatures/birds/*.json     ...and the animals that share no plan with anything: their parts
    assets/creatures/dinosaurs|monsters|others/*.json
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
  absent when either is not -- one frame for the horse that has a mane and the one that is only a body.
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
| `parts` | `creatures.js` | the part list itself, for the animals that share no plan (the birds, the fish) |
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
