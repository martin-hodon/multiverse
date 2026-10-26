# The face: attributes, landmarks, guide lines, a smooth skin

The head (face.js, the item part type `face`, assets/items/faces) rebuilt 2026-10-05 on GUIDE LINES. The old face was
a loft of rings with features pushed in and out (brow ridge, sockets, cheeks as bumps; the front cut into sheets
between angle tables) -- and its defects came from that: the eyebrows stood at a fixed distance from the midline
whatever the eyes did (nothing tied them to the eye), and the jaw was not a line at all but a clamp of everything below
a height onto the neck's circle, which stepped where the clamp began. Now everything is DERIVED: a set of anatomical
attributes places the landmarks, each from the ones it depends on (the brow from the eye under it, the gonion from the
jaw's angle and the chin), the landmarks are the nodes of a lattice of guide lines, and the skin is a smooth surface
through the lines.

## Research: what varies, and how much

Soft-tissue anthropometry (L. G. Farkas, *Anthropometry of the Head and Face*, 1994; adult means, North American
whites, male / female, mm) -- the attributes are these measurements, so a definition says "a narrow jaw" in the units
an anatomist would:

| attribute | landmarks | male | female | in face.js |
|---|---|---|---|---|
| face height | nasion - gnathion (n-gn) | 121 | 112 | `faceHeight` .123 m |
| forehead height | trichion - nasion (tr-n) | 62 | 59 | `foreheadHeight` |
| upper width | zygion - zygion (zy-zy) | 137 | 130 | `upperWidth` |
| forehead width | frontotemporale (ft-ft) | 112 | 108 | `foreheadWidth` |
| lower width | gonion - gonion (go-go) | 97 | 91 | `lowerWidth` |
| eye distance | endocanthion - endocanthion (en-en) | 33 | 32 | `eyeDistance` |
| eye width | palpebral fissure (en-ex) | 31 | 30 | `eyeWidth` |
| eye height | palpebral fissure height (ps-pi) | 10 | 10 | `eyeHeight` |
| nose height | nasion - subnasale (n-sn) | 54 | 50 | `noseHeight` |
| nose width | alare - alare (al-al) | 35 | 31 | `noseWidth` |
| nose projection | subnasale - pronasale (sn-prn) | 20 | 19 | `noseProjection` |
| mouth width | cheilion - cheilion (ch-ch) | 53 | 50 | `mouthWidth` |
| upper lip height | subnasale - stomion (sn-sto) | 22 | 20 | `upperLipHeight` |
| upper vermilion | labrale superius - stomion (ls-sto) | 9 | 8 | `upperVermilion` |
| lower vermilion | stomion - labrale inferius (sto-li) | 10 | 9 | `lowerVermilion` |
| lower lip height | stomion - sublabiale (sto-sl) | 19 | 18 | `lowerLipHeight` |
| chin width | the chin's breadth | ~45 | ~40 | `chinWidth` |

Angles (soft tissue, profile):

| attribute | what | range | in face.js |
|---|---|---|---|
| nasolabial angle | columella against the upper lip | 90-110 deg (men nearer 90, women 100-110) | `nasolabialAngle` 102 |
| forehead angle | glabella - trichion against the vertical | 5-20 deg (men more sloping) | `foreheadAngle` 12 |
| upper lip angle | sn - ls against the vertical | 0-15 deg forward | `upperLipAngle` 8 |
| mandibular angle | ramus against the mandible's body | 115-135 deg (men lower, squarer) | `jawAngle` 122 |
| canthal tilt | ex above en | 0-8 deg (positive: lifted outer corner) | `eyeTilt` 4 |

Proportion canons that fall OUT of these rather than being imposed: the thirds (trichion - glabella - subnasale -
menton about equal), the fifths (the face about five eye widths across at the eyes: en-en ~ en-ex), the mouth's
corners on the medial limbus, the lower lip's third of the lower face.

Placement rules (aesthetic surgery's, which are measurements of the average face): the eyebrow's HEAD lies above the
endocanthion (on the line up from the ala), its APEX above the lateral limbus (two thirds of the way from en to ex),
its TAIL on the line from the ala through the exocanthion, a little beyond ex; the brow sits on the orbital rim in
men and arches above it in women. The nasolabial fold runs from the ala past the mouth's corner, a centimetre outside
it; the jawline runs unbroken from the menton round the chin and along the mandible's body to the gonion, below the
ear, where the ramus rises to the condyle in front of the tragus.

Movement (for expressions and speech): the Facial Action Coding System (Ekman & Friesen) names the muscles' actions --
AU1 inner brow raiser, AU2 outer brow raiser, AU4 brow lowerer, AU5 upper lid raiser, AU6 cheek raiser, AU12 lip
corner puller (the smile), AU15 lip corner depressor, AU18 lip pucker, AU25 lips part, AU26 jaw drop, AU43 eyes
closed. Speech is a sequence of VISEMES (the mouth shapes of phonemes: open A, spread E/I, rounded O/U, closed
M/B/P, lip-to-teeth F/V...), each a mix of jaw drop, lip parting, rounding and spreading. Every one of these moves
LINES -- the brow line, the lid lines, the lip lines, the jaw -- which is what the guide-line frame is built to allow.

## The frame

    attributes     faceHeight, upperWidth, lowerWidth, nasolabialAngle, eyeDistance, ... (FACE_ATTRS)
       |           the expressions' weights too (browInnerUp, smile, jawOpen, blink, ...)
    landmarks      n g tr sn prn ls sto li sl pg me (the profile), en ex ps pi (the eye), brow head / apex / tail,
       |           al ac (the ala), ch (the mouth's corner), zy ft go co (the face's outline and the jaw)
    the lattice    ROWS (top to bottom) and COLUMNS (from the midline out), each a GUIDE LINE through landmarks:
       |             rows: crown, trichion, mid-forehead, BROW, orbital sulcus, UPPER LID, LOWER LID, infraorbital,
       |                   pronasale, subnasale, UPPER LIP MIDDLE, UPPER LIP BORDER, upper lip inside, lower lip inside,
       |                   LOWER LIP BORDER, mentolabial sulcus, pogonion, JAWLINE, neck
       |             columns: midline, paramedian (dorsum's flat, philtral column), nose side (ala), inner line
       |                   (endocanthion - ala groove - cheilion), pupil line (brow apex - lid - cheek - fold), outer
       |                   line (brow tail - exocanthion - malar - jaw), malar line, the face's OUTLINE (temple - zygion
       |                   - gonion); behind it the skull's rings to the nape
       |           a node is where a row crosses a column: a landmark, or a point derived from them
       |           (the forehead's profile -- glabella, mid forehead, trichion -- is `foreheadOf`, shared with headGrid:
       |            the scalp behind it, where the hair grows, is lifted by the same push, eased off to the crown)
    the mesh       the FRAME: only the guide lines' nodes (and the skull's frame behind the face) are vertices at the
                   lowest detail -- the regions the guide lines bound (a flood fill of the lattice's cells that crosses
                   no wall, a wall being an edge between two of those nodes) are each ear-clipped into triangles in the
                   lattice's domain, so no triangle has all its vertices off the frame. Each detail level splits every
                   triangle in four in the domain; every vertex at any level is a point of the SURFACE: a smooth
                   field over the lattice (the cubic through each line's nodes with chord-length tangents, along the
                   rows then down the columns; the free nodes filled by a membrane through the real ones), its normal
                   the field's own -- so detail adds points, never shape, and the shading is smooth whatever the
                   triangles' shapes
    soft tissue    `chubby` and the regions' multipliers (`chubCheek`, `chubJaw`, `chubLips`, `chubChin`, `chubForehead`,
                   `chubTemple`, `chubNose`, `chubEye`) scale FAT PADS (face.js PADS: the buccal and malar pads, the
                   jowls, under the chin, the lips, the forehead...) pushed out along the normal: 0 bony, 1 the canon,
                   2 a full face, below 0 hollow. (The first version made roundness the subdivision's tension, which
                   bowed whole spans out: a chubby face went grotesque.)

NOT EVERY NODE IS A GUIDE. Each row says where its nodes are REAL (`REAL` in face.js): the lips' rows only from the
midline to the mouth's corner, the lids only between the canthi, the subnasale row only under the nose; the midline
(the profile) and the outline real all the way down. The rest are FREE -- a membrane fill through the real ones,
adding no shape: the cheek from the mouth's corner to the face's outline is ONE surface (a node there on every lip
row, at the nasolabial fold, put a bump in the cheek for each), the fold being no line of the frame. `SHAPE` nodes
(the skull's forehead) are real but no guide is drawn through them.

THE MOUTH (2026-10-05): the four lip rows share ONE corner node, which goes a third of the way with the jaw's drop --
the lips stay joined at their corners in every shape (O, a smile, a laugh). Between the parted lips the opening is
left open (its lattice triangles are not drawn): behind it stand the TEETH -- an upper and a lower arch (`teeth`,
`teethWidth`, `teethDepth` how far the arch curves back, `teethSet` how far behind the stomion, `teethHeight`), the
upper incisors' edges a little below the lips' line, the lower arch behind them turning with the jaw; closed lips
hide both -- and behind them the mouth's BACK WALL (a dark squarish disc curving back into the cheeks), the INSIDE
of the lips and cheeks (the skin round the mouth turned inward, 2.5 mm within, in the mouth's dark) and a strip
closing the lips' rim between the two. Roles `teeth` (teeth-ivory) and `mouth` (mouth-dark).

THE EYE (2026-10-05), to look alive and wet: the iris (`irisR`) on a dark LIMBAL ring, the pupil, a CATCHLIGHT (a
small white disc up and toward the outer corner: the sky in the cornea), all cut by the lids; a LASH LINE along the
upper lid (`lashThickness`, role `lash`) that falls with it; and a WET SHINE in the face material (heads.js
`wetShine`: a very sharp Blinn-Phong highlight under the sun and a faint rim, weighted by the vertex's `wetMask` --
heads.js `WET`: the eye 1, the lips .3). Roles `limbus` (iris-limbus), `glint` (eye-glint), `lash` (lash-dark).

Where rows meet -- the canthi, the mouth's corners -- the lattice's lines meet in one point, so the eye's opening and
the mouth's are quads that close to their corners; the eye's white is the opening's surface, set back; the iris is
clipped by the lid lines (a lid that falls covers it); the mouth's inside is the quads between the two inner lip rows
(nothing while the lips are closed, the dark of the mouth when they part). The eyebrow is a strip along the BROW row
from its head to its tail -- so it is wherever the eye under it puts it.

## Movement, and what comes next

Expressions move landmarks before the lattice is made (face.js `ACTIONS`): `browInnerUp`, `browOuterUp`, `browDown`,
`lidUp`, `blink`, `cheekUp`, `smile`, `mouthDown`, `pucker`, `lipsPart`, `jawOpen` (the lower rows turn about the
jaw's hinge at the condyle), each 0..1; `expression` names a preset mix (`EXPRESSIONS`: happy, sad, angry,
surprised...) and `viseme` a mouth shape of speech (`VISEMES`). Because the lattice's TOPOLOGY never changes -- the
same rows and columns whatever the attributes and the actions -- two builds of one head differ only in where their
vertices are. That is the next step for the game: build a head once neutral and once per action, keep the
differences as MORPH TARGETS (heads.js's instanced head meshes then blend them per instance: a speaking villager's
visemes, a smile when greeted), with no new geometry per frame.

## In the viewer

assets.html, Items: faces -- the head drawn as the game draws it, its GUIDE LINES over it in red (`guides`, G):
the guide spans followed along the smooth surface, so the lines that shape the face stand out from the triangles
between them -- shown WITH the triangles, on the same switch (edges, T). The face's own bar: MOOD (an expression), MOUTH (a viseme), HAIRCUT (any of
items/hair on this face), LIPS (a colour; the kinds pick theirs from lip-rose, -pink, -brown, -pale, -dark, and the
lips take the light as the skin does). The params are the attributes; the form edits them.

## State (2026-10-05) and what is next

- `detail` (the item's; the game's heads `config.json people.faceDetail`, 1): below .75 the frame itself (~620
  triangles), 1 one split (~2,500 with the eyes, brows, ears, neck: ~3,600), 1.5 two, 1.9 three. 19 rows x 22 columns round the head.
- The kinds (`tools/facegen.py`, then `tools/hairgen.py` for their hair) are ranges over the attributes: the man's
  lower jaw angle and brow, the woman's arched brows and obtuse nasolabial angle, the child's small face in a large
  cranium, the elder's hollow cheeks (`chubCheek` below 0) and deep eyes, the beast-man's massive jaw.
- Seen to work: the brows follow `eyeDistance` (they are placed from the eye); the jawline is one unbroken line from
  the menton to the gonion; every expression and viseme; blink hides the iris under the lid.
- Rough still: the mouth's corners fold a little sharply into the cheek; the nose's underside is plain (no nostrils
  cut); the eye's white is the lattice's opening, not an eyeball (the gaze does not turn).
- Next: MORPH TARGETS for the game (a neutral build and one per action, the same vertices moved: heads.js blends them
  per instance -- visemes timed by speech.js, expressions by mood); an eyeball whose iris turns for the gaze; teeth and
  a tongue behind the lips for the open visemes; wrinkles as creases on the lattice's lines (the forehead's rows under
  `browInnerUp`, the crow's feet beside `ex` under `cheekUp`).

## Form in the paint, and brows that read (2026-10-24)

- **Hollows** (`heads.js` `cavityOf` / `cavityShade`, `CAVITY`): the sun's half-Lambert gives a head its round, not its
  form. Each vertex is darkened by how concave the surface is round it -- the mean of the points within two radii
  (`r`: .7 cm for creases, 1.8 cm for sockets) lies in front of a hollow -- and warmer in the skin (`warm`). Sockets,
  the creases beside the nose and under the lip, the mouth's corners and the ear's bowl take it; the hair does not
  (its strands are dense and costly to measure, and its sheen shades them). It is the shape's alone, so it is worked
  out once per built face (a WeakMap) and shared by every colouring of it: ~4 ms a shape once warm.
- **Brows a shade darker than the hair** (`BROW_TONE` .55): the face is built with its own brow placeholder colour
  (`BROW0`), recoloured to the hair's times the tone -- fair brows on dark skin all but vanished. `lashThickness` 1.5 mm.
- **Hair in the wind** (`heads.js HAIR_SWAY`, the face material's positionNode): what hangs below the head's middle (the
  geometry's own y) is blown the wind's way (grass.js `WIND_DIR`, `WIND.strength`, the grass's gusts) and flutters back,
  the flutter running down the hair -- the tips most, the crown not at all; each head on its own phase by where the
  batch placed it (positionLocal is already the world's in a positionNode after batching). ~4 cm at the tips of
  long hair in a full wind.
- **Beards** (`face.js BEARDS`, the `beard` attribute; tools/facegen.py picks by kind -- men 5 in 8, elders 4 in 5,
  beast-men always): soft regions on the lattice's domain (the moustache, the chin, the cheeks and jaw with sideburns,
  under the jaw), `beardWeight(B, u, v)`; a triangle more than half in is the `beard` role (the brows' colour), and
  every point stands out by `thick` times its weight -- skin and beard welded, no step; a full beard falls below the
  chin (`point`). Styles: moustache, goatee, short, full (stubble exists, its own colour -- heads.js STUBBLE -- but its
  triangle edges were patchy: not picked). Brows and beards darken TOWARD a warm dark brown (heads.js BROW_DARK): by a
  plain factor a blond's went olive.
- **Old men wear the elder's face** (people.js `faceOf`: `old` and not a woman or a child -> kind `elder`): hollow
  cheeks under the cheekbones, deep-set eyes, jowls, and mostly a beard (grey with the hair) -- they had a young man's
  face under grey hair.
- **Old women** (tools/facegen.py `old-woman`): a woman's face aged -- the cheek pads gone, deeper eyes under heavier
  lids, thinner lips, the nose and ears grown, softer jaw -- grey or white hair; people.js gives it to every old woman
  (a girl keeps the woman's face, as before).
- **A girl wears the child's face** (people.js `faceOf`): `female` is set for girls too, and she was given the grown
  woman's face (the kind was tested before the child).
- **Fuller tails** (tools/hairgen.py, hair.js rope): the ponytail 7.5 cm (was 5), fuller below the tie than at it; the
  braid 6.8 cm, the two plaits 5.8 cm (were 5 and 4.5) -- they read as strings from behind.
- (heads.js `browOf` reads the hair's grey in sRGB, as the eye does: in linear light a mid grey's lightness is .32, so
  grey hair failed the "light grey" test and its beard went dark.) Freckles were tried and dropped: the face's vertices
  are too far apart for a speck -- they blurred into faint blotches.
- **Lips in the skin's own tone** (heads.js `lipOf`, `LIPS`; the face's lip built in its own placeholder colour LIP0):
  the skin's colour drawn toward a red-brown (more on pale skin, less on dark) and darkened -- worked in sRGB, as the
  colours are written (three's Color mixes in linear light and washed them out). A pink picked at random sat on dark
  skin like paint.
