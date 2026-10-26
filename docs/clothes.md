# Clothes

What people wear is written the way a tailor cuts it: as flat PIECES of cloth -- a 2D sheet with its edges, its
openings and its hems -- laid round the body. A piece is mathematics (where it starts and ends on the body, how far
round it goes, what is cut out of it); a garment is pieces; an outfit is garments in layers; and the cloth itself is a
pattern of the same language the buildings' finishes use (docs/patterns.md), in the garment's own colours.

    assets/people/body.json        the body the clothes are cut for (the unisex canon)
    assets/clothes/components/*    reusable pieces with parameters: a bodice, a sleeve, a skirt, a hood...
    assets/clothes/*.json          garments: components, their parameters, the fabrics they are cut from
    assets/clothes/wardrobe.json   who wears what: the garments and dyes a villager is dressed from
    assets/patterns/fabrics.json   the cloths: weaves, stripes, checks, twill, mail, leather... (four colour slots)
    clothes.js                     the tailor: an outfit and a body -> the parts the figure engine draws
    people.js                      the body; asks clothes.js to dress it

## The body it is cut for

The canon (assets/people/body.json) is UNISEX: the means of men's and women's proportions, each against their own
stature (segment lengths after Drillis & Contini; breadths, depths and girths after the ANSUR II survey), with a few
widths moved by sex (`build.sex`: shoulders, waist, hips, thighs, bust) and a child's head, hips and legs by age.

The TORSO is one shape: three cuts swept as a single flattened lathe through four rings -- the shoulders' rim, the chest
under the armpits, the natural waist, the hips -- closed at the top by a low, squared cap that is the shoulders and at the
bottom by a rounder one down to the crotch (the engine's flat `spine` chain and `caps`). The ARMS hang beside it: the
shoulder joint just outside the chest, under the shoulders' flare (which covers the joint as a deltoid does), the arm a
couple of degrees out from the vertical -- so no arm passes through the chest or the hips, and a bodice and a sleeve are
two sheets that meet at the shoulder, not one passing through the other. That makes the shoulders about 6% wider than
the real mean (bideltoid .30 of the stature against .28).

## The sheet

A PIECE is a sheet laid round a HOST -- a region of the body -- between two LANDMARKS:

| host | its landmarks, top down |
|---|---|
| `torso` | `collar` (where the neck leaves the shoulders), `armtop` (the top of the arms beside it), `shoulder` (the rim), `armpit`, `chest`, `waist`, `hip`, `crotch` -- and below it, for what hangs from it, `thigh`, `knee`, `calf`, `ankle`, `floor` |
| `arm` | `shoulder`, `biceps`, `elbow`, `forearm`, `wrist`, `knuckles` |
| `leg` | `hip`, `thigh`, `knee`, `calf`, `ankle` |
| `neck`, `head` | `jaw`, `ear`, `brow`, `crown` |

A landmark may be moved by metres (`"waist + 0.05"`) or the piece may stop at a fraction between two (`"0.6 knee"`).
Round the host it is CLOSED (it goes all the way round: a sleeve, a skirt) or OPEN (`wrap`: an arc about the figure's
front, in degrees -- a cloak open at the front is `{ "centre": 180, "span": 320 }`, an apron `{ "centre": 0, "span": 110 }`).
Along it, it may FOLLOW the body (`ease` 0: a bodice, hose, a fitted sleeve) or stand off it: `ease` metres, and
`flare` -- how much wider it gets per metre down (a skirt's A-line, a bell sleeve's mouth) -- and how it clears what is under it (`fit`: "flare", its ring stays and its flare grows, a kirtle hugging the waist over the hips; "ring", its drape stays and its ring grows, a cloak over the arms). A piece that hangs -- a skirt
from the waist, a cloak from the shoulders -- is a `hang`: its own cone from a ring round the body, swinging behind the
stride, not following the legs.

OPENINGS are cut out of the sheet, in its own coordinates: a NECKLINE at its top edge (`round`, `scoop`, `v`, `square`,
`boat`, with a width and a depth at the front and the back), a WINDOW anywhere (an ellipse or a rounded slot at an
angle round the host and a height on it: a sideless surcoat's great armholes, a keyhole, a tunic's side vents). Its
EDGES are straight, or DAGGED (scalloped, the late medieval fashion), and any edge may carry a BAND of another fabric --
a hem's embroidered border, a neckline's trim.

## How the figure engine draws a sheet

Two ways, chosen from the piece's own geometry, never by hand:

* A piece that FOLLOWS the body is drawn ON it: the body part's surface wears it. Each body part carries a short stack of
  LAYERS (outermost first) -- the region of the sheet that lies on that part (from/to along it, its arc round it, its
  openings), its fabric and colours, its thickness -- and the engine (shell.js) lifts the surface by the thickness of what
  covers each point and, per pixel, shows the outermost layer that covers it: a V-neck shows the shirt under the tunic, the
  tunic's hem shows the hose under it, and where nothing covers the body it is skin. A sleeve to the elbow and a bare
  forearm are one arm.
* A piece that stands OFF the body (a skirt, a cloak, a hood, a bell sleeve, a short sleeve's mouth) is a SHELL of its
  own: a lathe between two cuts round its host's axis, open where its `wrap` says, with its own layers -- and where no
  layer covers a point of it, there is no cloth: the openings are HOLES (the surcoat's armholes, a dagged hem's scallops).

The sheet's coordinates ARE the fabric's: `u` round the host (a whole number of repeats round a closed piece, so the
pattern meets itself at the back seam), `v` down it from the garment's own top edge -- stripes run on from the chest to
the hips, a check is square on the sleeve as on the skirt.

THE CLOTH'S FRAME (2026-10-05). The fabric's coordinates are the part's length (`s`, from its A end) and the angle
round it (`th`). The angle used to be counted from the FIGURE's forward, which does not move with an arm -- so a
working arm's sleeve slid its weave round itself as it swung. Now each dressed part keeps its REST AXIS (its axis
when first posed, in the figure's frame: composite.js `restAxes`, in the second colour's texel, marked -1 in the
strands' slot), and the shader carries the figure's forward and left from that axis to the part's axis now by the
least rotation before measuring the angle: the weave stays on the cloth whatever the arm does (a twist about the arm's
own axis is not followed -- the rig's limbs do not twist).

## Fabrics

A FABRIC is a pattern (patterns.js) of at most four colour SLOTS, in `assets/patterns/fabrics.json`. The engine does not
keep a picture of each colouring: it bakes each fabric once into a layer of a texture ARRAY as the WEIGHTS of its slots
(red, green and blue are slots 1-3, slot 0 what is left), and the colours come from the garment -- so every fabric is
every dye, a whole village is dressed from one small array, and a pattern is exact where it is sharp and mipmapped where
it is far. The dyes are palettes (`assets/patterns/palettes.json`): madder, woad, weld, walnut, undyed linen and wool...

## Components and garments

A COMPONENT is a parameterized piece (or a few): `components/bodice` (from the collar to the waist or the hip, its
neckline, its lacing), `components/sleeve` (to the elbow or the wrist, fitted or belled or hanging), `components/skirt`
(from the waist or the hip, its length, its fullness), `components/hood` (the cowl, its face opening, a liripipe, a
capelet), `components/hose`, `components/cloak`, `components/apron`, `components/belt`...

A GARMENT uses components with its own numbers, names its FABRIC SLOTS (`main`, `lining`, `trim`...) and its LAYER (the
chemise is next to the skin, the kirtle over it, the surcoat over that, the cloak outside everything):

    { "name": "Kirtle", "layer": 2,
      "fabrics": { "main": { "pattern": "fabrics/plain", "palette": "madder" }, "trim": { "pattern": "fabrics/braid" } },
      "use": [ { "use": "components/bodice", "params": { "to": "hip", "neckline": "scoop", "lacing": true } },
               { "use": "components/sleeve", "params": { "to": "wrist" } },
               { "use": "components/skirt", "params": { "from": "hip", "to": "ankle", "flare": 0.35 } } ] }

An OUTFIT is a list of garments, each with its fabrics (dyed as the wardrobe draws them), worn in layer order.
A garment says what it is for the rest of the world: `head` (a hood, a cap, a hat: the hair lies flat under it, and
`hat: "none"` takes it off), `feet` (shoes, boots: never on a beast's hooves), `skirted` (ridden in as a tunic of the
same cloth).

## Other times and places (2026-09-27)

The wardrobe's `styles` hold the same lists as its `people` -- by kind, outfits by weight -- for the dress of other ages,
and `makePerson({ style })` draws from them:

| style | garments |
|---|---|
| `greek` | the Ionic `chiton` (pinned loose sleeves, fine pleats, a key border), the Doric `peplos` (sleeveless, its `overfold` hanging to below the waist), the `himation` and the short `chlamys` (both `mantle`s), `sandals`, the `petasos` |
| `roman` | the `tunica` (short sleeves, to the knee; a matron's to the feet), `clavi` (the purple stripes: a garment of four `strip`s over it, running on over its skirt), the `toga` (a `mantle` to the ankles, open at the right front, the praetexta's purple hem), the `stola` (girded under the breast), the `palla` |
| `chinese` | the `shenyi` (one deep robe, its crossed collar edged in black -- a `strip` -- great hanging sleeves), the `ruqun` (a short jacket with the `qun`, its skirt, tied high at the breast), the `sash`, the `guan` (a tall black cap: `tall-hat`), cloth shoes |
| `gothic` | the `doublet` (padded, a short pleated skirt) with parti-coloured hose, the `hennin` (a steeple headdress), with the cote-hardie, the houppelande, the sideless surcoat and the hood with its liripipe |

New components: `mantle` (a great cloth wrapped round the body over the arms, open where its `wrap` is not: `centre` the
middle of the cloth round the body, `span` how far round), `overfold`, `strip`, `qun`, `hennin`, `tall-hat`. New fabrics:
`meander` (the Greek key -- the Chinese hui fret too), `clouds` (xiangyun silk), `straps` (a sandal's thongs); dyes
`tyrian`, `wool-white`, the `silk-*` colours, `meander-red`/`-black`, `sandal`.

In the world a landmark's people wear its dress (architecture.js `DRESS`: the Greek temples Greek, the arena and the
Pantheon Roman, the Temple of Heaven Chinese, the Gothic cathedrals and the castle Gothic), and two in five wanderers
dress as the people of a landmark standing in that world (or of any style when none has one). The village keeps its own.

## The tailor

`clothes.js tailor(form, outfit, { add, bone })`: people.js builds the body and hands it a FORM -- each host's parts
(the torso's three cuts, each arm's upper arm, forearm and hand, each leg's thigh and shin, the feet, the neck, the
head), its landmarks in metres down it, its girth and, for the torso, its half-width at any height with and without the
arms beside it. The tailor:

* evaluates every piece of every garment (a component's params over the garment's, expressions over params and
  landmarks);
* lays a WORN piece on each part it reaches, in that part's own coordinates, its fabric's repeat carried across the
  joints (and a hem band as a layer of its own over the piece's last centimetres);
* builds the STANDING pieces from the skin out, each clearing the torso (flattened: `squash`, its depth against its
  width), the arms if it says (`arms`: a cloak, a cape) and whatever already hangs there -- a mail skirt over a
  gambeson's, a tabard's over both. `fit` says how: "flare" keeps its ring and widens its flare (a kirtle hugging the
  waist over the hips), "ring" keeps its drape and widens its ring (a hood's fall over the arms). Pieces hung end to
  end (a cape and its fall) meet in one ring;
* lays whatever is worn OVER a standing piece on the torso onto it too, where it reaches (a belt round a skirt's
  top, an apron on it);
* drops what cannot be seen: a layer an outer one covers everywhere on a part (the chemise under a kirtle's bodice);
  the engine reads six at most.

It returns the parts' layers, the standing parts (already added), the skirts and the height of the lowest hem --
the legs a skirt covers are not drawn, and a skirted walk takes shorter strides. Seated, a short skirt becomes a lap
ending in a rounded knee, a long one tilts forward over the knees (people.js).

**What is worn on top** (2026-10-06, docs/jewelry.md): `outerSurface(form, worn)` hands the tailor's own data to the
jewelry -- the torso's oval and the neck joined by the fillet, every worn layer's thickness over a point except inside
its neckline (the shader's ball), the standing torso shells round it -- as one function of height and angle; a
necklace lies on it. The wardrobe's `egyptian` style (linen kilts, chitons cut as sheaths) dresses Giza's people.

## In the game and the viewer

`makePerson({ outfit })`: `wear` (the garments), `named` (a kit of the wardrobe's: the town guard is `soldier`, the
beast-men theirs), `bare` (nothing: the canon), `hat: "none"`, and the looks (`hair`, `fringe`). Without them a person
is dressed from the wardrobe by kind (man, woman, boy, girl) from their own seeded stream.

`assets.html`: **Clothes** -- a garment on the canon's body (a skirted one on a woman), edited live; **Garment
components** -- a component worn alone; **Wardrobe** -- ten villagers dressed from it; **Patterns / fabrics** -- the
cloths as a sheet, each in its dyes. `wardrobe.html` is the bench: every garment over a shirt and hose, the kits,
every hat, hairstyles, poses, trades and faces.

Cost, measured on this machine (headless): dressing a person takes about 4.7 ms (the bare body 0.9) -- about a
second for the ~240 people of a world. The shell material now DISCARDS (a standing piece's openings), which costs
the figures early depth rejection; if that shows on the iGPU, standing pieces can move to a material of their own.

## Limbs and static cloth (2026-10-23)

The cloth does not move with the body, so two cases let a limb come out through it, both now handled by rules, not
per-garment fixes:

- **A thigh under a skirt is a BONE** (people.js: posed, never drawn) -- only under a skirt reaching past the knee
  (2026-10-24: from 80% of the thigh down, a guard's tabard left the thighs' last hand's breadth missing above the boots). It used to be "hidden" by an empty cut
  (`clip: { lo: 1e3, hi: 1e3 }`), which the shell engine drew whole after all; a standing thigh only looked hidden
  because it lay inside the skirt's cone, and a crouch (skeleton.js `an.rest`, the gestures' `crouch`) brought the
  knee out through the front of the gown.
- **Under a cloak the upper arm stays down.** The tailor reports `armsUnder`: the lowest edge of what is hung over the
  arms (a cloak, a mantle, a hood's fall; clothes.js `arms` pieces). When it reaches below mid upper arm, the figure's
  gestures are built low (people.js LOW_ARM: the upper arm never lifted out to the side, at most 32 degrees forward;
  a forearm swung sideways -- a clap -- swings up in front instead), so the forearm and hand do the gesture and come
  out from under the cloak's front: a cloaked wave is a wave from the elbow.
- **A stride no wider than the hem.** Where a skirt hides the thighs, both the walk's and the run's stride are capped
  by its hem (people.js `cap`: the lowest skirt's bottom radius, front to back, less half a foot), and the run's knee
  lift halved: a child running at tag in a gown had a foot swinging out behind the hem with nothing above it. A tunic
  above the knee leaves the stride alone.
- **A bell sleeve sags.** Its mouth piece (clothes.js `hang` on the arm) carries `sag` (skeleton.js): each pose its
  axis is tipped toward the plumb line by up to the cone's own half-angle less a margin (`atan(flare) - .08`), so the
  sleeve's top rests along the arm and the cloth hangs below it -- arms out or raised no longer hold the bells up like
  trumpets, and the arm inside never comes through the side. The bell is one piece past the elbow (the hand's length
  added to the forearm's: loose cloth does not bend at the wrist); it used to be cut at the wrist, and a sleeve running
  past the knuckles never counted its last piece as the mouth.
  Only the mouth piece has the garment's edge (clothes.js `dress(len, mouth)`): its hem band and dags. A sleeve
  from the shoulder (the dalmatica's) is two pieces, and both had a hem band -- a second gold ring at the elbow.
- **Seated, the shins show whole.** A long skirt hides all but the last few centimetres of shin standing; seated it
  tips forward off the knees, so the clip is skipped for `pose: "sit"` -- the shoes used to stand below the hem with
  nothing above them.
- **A skirt over rising thighs drapes forward with them** (skeleton.js `DRAPE`, shared with joints.js `setAngles`):
  a skirt part (the person's `motion.skirts`) is turned forward by .55 of the thighs' MEAN swing, up to 70 degrees --
  a crouch or a stoop (a gesture's `crouch`: tending, scrubbing) lifts both thighs and the skirt goes with them; a
  stride's thighs swing both ways and leave it hanging. The robes of the Islamic and Ottoman styles had both knees
  out through the front while tending a fire (found by the check below).
- **Cloth that trails** (skeleton.js `TRAIL`, a piece's `trail` in degrees: the cloak's body 14, the mantle's 8): a
  cloak's hem is swept back as its wearer goes, `walk` (.35) of its `trail` at a walk and all of it at a run, on a
  damped spring (`w` 6 rad/s, `zeta` .45) so it swings on past when they stop; and as the body turns, the cloth's
  heading lags behind it (`turn` 4 /s), the hem twisted by that lag (`twist` .6, at most `maxTwist` .5 rad). Per
  figure, on the frame's clock (display only); a part that trails is never cached as still.
- **A cloak's front lifts with the arm** (skeleton.js `LIFT`, a torso piece's `follow`): the cloak is three pieces --
  the back and a panel either side of the opening (components/cloak: `body`, `front a`, `front b`, their `wrap`s
  meeting) -- and each panel swings forward with the arm on its side (the wrap's middle tells which: +z is the rig's
  "L"), `follow` (.5) of that arm's swing forward in the chest past `from` (8 degrees: a hanging arm, a walk's swing
  leave it), at most `max` (45). A raised hand lifts the cloth's edge instead of coming through it, and a carried load
  opens the cloak over both forearms. Measured with the check below (n=2): the cloak's clips 2010 -> 1535, their mean
  depth 4.6 -> 4.0 cm (a rigid panel cannot fold round a forearm bent up to the brow: those remain).

## Checking for clipping (2026-10-23)

`python3 build/clipcheck.py [QUERY]` (clipcheck.html, clipcheck.js; no GPU, a couple of seconds) dresses people of
every style and kind, `n=` seeds each (4), standing, sitting, carrying, on guard and drawing a bow, and poses each
through `CLIP_STATES` -- a walk's and a run's stride at eight points, every gesture at eight moments -- with the
skeleton's own `writeAnimal`. Every HANGING piece (skirts, cloaks, capes, hoods' falls, bell sleeves: the cut cones of
clothes.js `standPiece`, oval by their `squash`, open where their `wrap` leaves them open) is tested against every
limb that is drawn, as the engines draw both: the limb a round cone thickened by the cloth worn on it, the piece its
cone, its angle counted from the figure's forward as shell.js counts it. A limb's surface past the cloth by more than
`tol=` (1 cm) -- out through it from inside, or into it from outside -- is a clip, unless another hanging piece covers
that point (a thigh in the skirt a sleeve hangs against) or it lies at the joint the piece starts from (a forearm's
sleeve always meets the upper arm at the elbow). It prints the worst of each garment piece, limb and motion, with a
person to see it on: `wardrobe.html?specs=[that person]&crowd=0` (`&gesture=` in the spec, `&t=` to freeze), and
`clipcheck.html?specs=[...]` lists that person's every clip by the parts' own ids.

Known and left (2026-10-23): with the forearm raised, a bell sleeve tips toward the plumb line and onto the upper
arm (shenyi, ruqun, houppelande: ~6 cm) -- a real sleeve slides down the arm and folds, which a rigid cone cannot;
and a hood's fall that a raised arm goes through (the bow-drawing arm). The cloak now lifts with the arm (above).

THE HAIR UNDER A HAT (clipcheck.js `hairClips`, in the same run): the mesh hair of everyone wearing something on the
head (heads.js places it as the game does) against each head piece -- a crown (a cone, its top closed), a cowl (a
ball, open at the face) -- printing how far the worst hair point comes through and what share of the hair does. A
point inside ANOTHER standing piece is hidden by it (an official's tall kavuk stands out of his turban; a hood's fall
covers the nape); a brim (a slab a few centimetres thick) covers nothing. The check used to skip every piece whose
cut lies behind its centre -- meant for the brims, it skipped all the hoods, caps, headscarves and turbans, so these
were never checked and never counted as cover. Found then: under a headscarf or a maphorion the flat hair's ends
showed at the nape below it; a garment that covers the hair whole now says so (`"hair": "none"`: headscarf,
maphorion) and people.js draws none under it. Left: a poke bonnet shows the hair at the nape (as it does), a hood's
ball by the check's reckoning (its fall hides it: seen from behind).

## A sleeve bends as one sheet (2026-10-24)

A worn piece was always one sheet on one swept arm (its layers run across the elbow), but the arm itself bent like two
tubes: the ring at the elbow was a circle turned halfway, which pinched a bent elbow to cos(half the bend) of its girth,
and past a few metres no ring fell on the elbow at all. Now a joint between two long parts is a SEAM shared by both
(shell.js "THE JOINT IS A SEAM", docs/engines.md): the mitre of the two cones, one ring of points that moves with both,
always a ring at every detail -- the sleeve, the hose at the knee, the bare arm alike. And a limb's top belongs to the
body: an arm's and a leg's ROOT (people.js `ROOT`, 1.6 of its top radius) keeps its rest as the limb moves and the limb
bends out of it, so a sleeve's top stays sewn in at the shoulder instead of its round end swinging out behind it.
Left: the hand and the foot are shells of their own (a flat hand, a shoe), and the bodice and the sleeve still meet
where the arm's shell meets the torso's, as before.

## Folds, hems that wave, skirts that sway (2026-10-24)

- **Folds** (`shell.js` `foldPhase`, the `pleats` of a piece): not even pleats (a ribbed cone) but `pleats` folds
  round it whose phase is warped by a few slow waves -- more so lower down, where folds fan out -- shallow gathers at
  the top of the piece deepening to the hem; a broad lit ridge and a narrow dark valley, the same profile tilting the
  normal. The skirt component folds softly by default (`pleats` 9); stiff ones say 0 (the gambeson, mail, the tabard);
  the kilt 26. The cloak, mantle, overfold, bell sleeve and the hood's cape and fall fold too (the hood's fall flares
  .4 now: straight, it read as a lampshade).
- **The hem waves** with them (`HEM_WAVE`: a valley lifts it by that share of a fold's width): `layerIn` lifts the
  hem, and a standing piece is cut where no layer is, so its silhouette waves; a hem band keeps its piece's pleats and
  follows.
- **Sway**: a standing piece's `anim.sway` (3 degrees) swings it side to side once a stride with the legs
  (`skeleton.js`), as the hips carry it from foot to foot.
- **Trims drawn person by person** (wardrobe.json, `clothes.js drawOutfit`): a param given as a LIST is drawn from it
  -- the folk's tunics and kirtles carry `hem: [0, 0, .03, .04]` and a `trim` fabric list (undyed, black, madder, woad,
  braids, a check), so some wear a contrasting band at the hem and most none; only listed params draw from the seed.
- **No fringe under a hat** (people.js face `fringe`): the flat hair a hat leaves kept its forelock, which came through
  a coif, a bonnet, a hood's cowl, a fez (clipcheck: up to 58 mm) -- under any hat the face goes without it. The coif
  and the bonnet cover the hair (`hair: "none"`, as the headscarf): the flat hair still came 5 cm through them. Left
  (clipcheck n=4): 4 kinds over 5 mm, the worst a child's hair 20 mm through a fez -- it was 9 kinds, 58 mm.
- **A cowl drawn out behind** (clothes.js `cowl`: `length` head radii, `taper`): the hood's cowl runs back along its axis
  and narrows a little (.5, .86) -- a hood, not a ball round the head; other cowls keep the ball (length 0).
- **A pouch at the belt** (components/belt `pouch`, the belt garment's default 1): a leather purse hanging at the left
  hip -- a thick worn patch (16 mm proud) under the belt, standing out over a tunic or the top of a skirt.
- **Standing pieces end at their hem** (clothes.js `standPiece` dress, `LAYER_TOP`; fixed later the same night): a
  standing piece's layers ran from -1e3 to 1e3, so on a skirt, a cloak or a bell sleeve the fold depth was one value
  all down it, the hem wave and the soiling sat at 1e3 m (never seen), and dags never cut -- the claims above held only
  for worn pieces. Now a piece ending at the garment's edge has its layers end at its own length (`len`) and begin
  LAYER_TOP (.25 m) above it; seated, the layers that ended at the hem move with it (people.js -- an apron keeps its own
  end). HEM_WAVE .12 (at .22, once real, it read as dags). Clipcheck unchanged.
- **Brims with a thickness** (components/brimmed-hat `brimT` .1 head radii, ~9 mm): at .05 a straw hat's or a felt
  hat's brim read as a hairline from the side.
- **Patches** (shell.js `PATCH`): about three worn pieces in ten (by their layer's slot: it stays where it is) carry a
  darned square of near-matching cloth -- a shade off its own, a touch of its second colour -- edged with a dashed
  stitch, at a place round it and down it drawn from the same hash; not on bands or thin pieces, gone where finer than
  a few pixels.
- **A seam is no hem** (clothes.js tailor: `seam` on a standing piece the next one of its garment hangs on from -- a
  hood's cape above its fall, a mantle's cape above its body): no wave, dags or border there -- once the hems waved for
  real, they cut slivers of holes along those seams. The hood's fall flares .25 in 9 broad folds (at .4 and 14, with
  the wave, it read as a frill).
- **Sleeves fall off a raised arm** (skeleton.js `SLIDE.fall`, clothes.js `fall` on every hanging piece of a sleeve):
  once the arm rises past level, the sag's limit (keep the arm inside the cone) gives way over the first .35 of the
  rise, and the piece hangs plumb from its top ring, the arm going up out of it -- a dalmatica's upper sleeve from the
  shoulder, a bell from the elbow. (First it was shortened instead, to .35 of itself with its mouth drawn in -- still a
  funnel round the raised hand; that is gone.)
