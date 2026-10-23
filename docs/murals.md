# Murals: Egyptian tomb paintings

Large wall paintings in the Egyptian manner (2026-10-05): figures of gods, kings and the dead, built from the canon of
proportions and a pose, dressed and crowned from reusable parts, set in registers with columns of hieroglyphs, an
offering table, a frieze above and a dado below -- `murals.js`, `assets/murals/*.json`; shown in the asset viewer;
painted on the walls of the pyramids' passages and burial chambers (pattern family `murals`).

## Analysis: how an Egyptian painter drew a figure

**The grid.** A standing figure was laid out on a squared grid: 18 squares from the soles to the HAIRLINE (the Old
and Middle Kingdom canon; the Late Period's 21 squares reach the upper eyelid, the same proportions on a finer
grid). Fixed heights, in squares: the knee at 6, the lower buttocks at 9, the small of the back / elbow at 11-12, the
armpit at 14-14.5, the junction of neck and shoulders at 16, the hairline at 18. The shoulders are 6 squares across
for a man (about 5 for a woman); a striding man's feet span about 5. A seated figure keeps the same grid above the
seat: the seat's top at 5-6, the hairline at 14. The grid is why every figure on a wall, at any size, has the same
body -- and why this engine builds a body from heights in squares, not from a drawing.

**The composite view (aspective).** Each part is shown from its most characteristic side and the parts are joined:
the HEAD in profile, the EYE and eyebrow seen from the front within it, the SHOULDERS frontal (full width, both
shown), the chest turned between (a single breast or nipple in profile on the leading side), the waist, hips, LEGS
and FEET in profile, both feet usually shown from the inside (the big toe on both). Hands are the ones that read
best for what they do. A figure faces the way it acts: toward the god, toward the offering table, toward the centre
of the wall; the engine draws every figure facing left and mirrors it to face right.

**Pose and gesture** are a small fixed vocabulary: STANDING with the feet together (women, gods at rest), STRIDING
with the far leg forward (men, kings, gods acting), SEATED on a block throne, KNEELING; arms HANGING, holding a STAFF
or a SCEPTRE forward, OFFERING (forearms forward, palms up, bearing a vessel or bread), ADORING (both hands raised,
palms out).

**Colour** was conventional, from the same six pigments as the hieroglyphs (red and yellow ochre, Egyptian blue,
green, black, white): men's skin red-brown, women's yellow ochre; Osiris green (rebirth) or black (the fertile
earth), Amun blue, Anubis's jackal head black, Ptah's skull-cap blue; hair black or blue (lapis, of the gods);
linen white, often shown transparent over the limbs; collars in bands of blue, green, red and gold.

**The iconography** that tells one figure from another:

| figure | head | headdress | holds | dress, skin |
|---|---|---|---|---|
| Ra(-Horakhty) | falcon | sun disc with uraeus | was sceptre, ankh | kilt; red |
| Horus | falcon | double crown | was, ankh | kilt |
| Anubis | jackal (black) | -- | was, ankh | kilt |
| Thoth | ibis | (lunar disc) | was, ankh | kilt |
| Khnum | ram | -- | was | kilt |
| Sekhmet | lioness | sun disc, uraeus | was (papyrus) | sheath dress |
| Osiris | human | atef (white crown, plumes) | crook and flail | mummiform; green, enthroned |
| Ptah | human | blue skull-cap | was-djed sceptre | mummiform |
| Amun | human | two tall plumes | was, ankh | kilt; blue |
| Isis | woman | throne sign | ankh, was (papyrus) | sheath dress; yellow |
| Hathor | woman | cow horns and sun disc | ankh | sheath dress |
| Maat | woman | ostrich feather | ankh | sheath dress |
| the king | human | nemes (or the blue khepresh, the white, red or double crown) with the uraeus; the false beard | crook and flail, an offering | royal kilt, collar, bull's tail |
| the queen | woman | vulture headdress, tall plumes | ankh, sistrum | sheath dress |
| the dead (a noble) | human | short or long wig | -- | kilt or robe, collar |

**The wall.** A painting is in REGISTERS -- horizontal bands each standing on its own ground line; the most important
figure is the largest (hierarchic scale), the god usually enthroned and facing the deceased; between them an
OFFERING TABLE heaped with loaves, vegetables, a duck, a lotus; above each figure COLUMNS OF HIEROGLYPHS naming them
and their words, between ruled lines. Above everything a KHEKER FRIEZE (bundled reeds) or a SKY band with stars; at
the bottom a DADO of coloured bands; round it a border of coloured rectangles.

**Where they were.** Painted tombs belong to the New Kingdom's Valley of the Kings and the nobles' tombs at Thebes; the
Old Kingdom's pyramids were unpainted inside, and from Unas on (5th dynasty) their chambers were carved with the
Pyramid Texts -- columns of hieroglyphs, often filled with blue or green. The game's pyramids take both: the texts
in the passage, painted scenes in the chamber.

## The engine

    the canon        murals.js CANON: heights in squares (sole 0 .. hairline 18), widths, a woman's and a man's
    a body           murals.js body(): the torso, the limbs as tapering outlines between joints, the feet, the hands
                     -- from the canon and a POSE (stand, stride, sit, kneel, mummy) and ARMS (hang, staff, sceptre,
                     offer, adore, crook-flail); the joints are in figure units (a square is 10 units)
    the parts        assets/murals/parts.json (in the hieroglyphs' language: shapes, roles, colours): the profile
                     head with its frontal eye, the animal heads (falcon, jackal, ibis, ram, lioness), wigs, crowns
                     (nemes, white, red, double, atef, khepresh, plumes, sun disc, horns-and-disc, throne sign,
                     feather), beards, the collar, held things (was, ankh, crook, flail, staff, lotus, sistrum, jar,
                     loaves), the throne, the offering table, the frieze's kheker
    a figure         assets/murals/figures.json: a named figure -- kind, pose, arms, head, headdress, beard,
                     garment, collar, holds, skin -- Ra, Horus, Anubis, Thoth, Osiris, Isis, Hathor, Maat, Amun,
                     Ptah, Khnum, Sekhmet, the king, the queen, a noble, his wife, an offering bearer
    a painting       assets/murals/paintings.json: its size, its border, frieze and dado, its registers -- each a
                     height and its items: figures (a named one, or one written out; `face` left / right, `scale`),
                     the offering table, text columns (glyphs.js, by seed), a sky band

## The pyramids (landmark `giza`)

`tools/pyramidgen.py` writes `assets/architecture/giza.json`, its finish and the `murals` pattern family. Khufu's,
Khafre's and Menkaure's pyramids at a quarter of their size, in their line across the plateau, each an arch-engine
part of type `pyramid` (arch/assemble.js):

- `base`, `height`; the faces in bands -- `core` (plain limestone), `casing` from `casing` metres up (the white Tura
  limestone near the top; Khafre's keeps the most), `cap` the last `cap` metres (the gilded pyramidion);
- `entrance` { width, height }: a door at the foot of the north face (+z), its height where the passage's sloping
  ceiling meets the face; the DESCENDING PASSAGE going down at `slope` (26.5 degrees, as Khufu's and Khafre's) to
  `depth` under the ground (limited so a level stretch is left), then LEVEL to the burial CHAMBER (`chamber` { width,
  length, height }) cut in the rock under the pyramid's middle -- each wall its own part (north with the passage's
  door, south, east, west), the ceiling, the floor;
- the SARCOPHAGUS (`items/furniture/sarcophagus`: a red granite basin, its lid on, aside or gone) at the chamber's
  west end, as Khufu's stands;
- `site.dig`: the ground open where the passage goes down through it (the walk reads it in floorsAt; the ground's
  shaders through grass.js `GROUND_HOLES.rects`, up to 16 open rectangles in the world).

The finish paints the chambers: a scene on each wall (patterns `murals/<painting>`, sized to the wall by the rule's
W and H, centred by an `offset` of the wall's middle -- finish.js's face u runs along the wall in the building's
frame), the passages with the Pyramid Texts (blue, repeating), the ceilings starred. The player walks in from the
door, down the slope, to the chamber.
