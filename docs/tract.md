# The tract lab: speech from a mouth, not from formants

`tract_lab.html` is a second speech synthesiser, independent of `speech.js`. Where that one draws formant curves
(Klatt), this one moves a jaw, a tongue, lips, a velum and two vocal folds, and lets a pipe of that shape make the
sound. Nothing in it is a formant, a burst or an aspiration: those are what the physics does. The only thing the two
engines share is `lexicon.js` (written text → IPA from the dictionary in `lang/`).

Why bother: every number here is something you could point at in a head — centimetres, square centimetres of
opening, centimetres of water of lung pressure, milliseconds of how fast a tongue tip is — so tuning is a matter of
"the tip is too slow" or "her throat is too long", not of juggling bandwidths.

## The chain

| file | what it is |
| --- | --- |
| `tract/anatomy.js` | the head in mid-sagittal section: fixed palate and throat wall; jaw, tongue body (a circle), tongue tip, lips, velum, larynx. Widths across the airway along fixed measuring lines → areas (`α·d^β` per region) → the area function. Also the reverse for consonants: "bring this organ to this place with this opening". |
| `tract/acoustics.js` | the tube: a Kelly–Lochbaum waveguide with the things speech needs — flow-separation loss at every widening joint, slit friction at near-closures, yielding walls, a nasal branch, lip radiation, turbulence, and a fractional delay at each end so the length changes smoothly. |
| `tract/glottis.js` | the folds: an area that swings about a rest opening when there is pressure across it. One number, `rest`, runs pressed → modal → breathy → voiceless. |
| `tract/measure.js` | knocks on the tube and reads its resonances — the formants shown and fitted are the ones the synthesiser really has. |
| `tract/inversion.js` | acoustic-to-articulatory: formant targets → the most relaxed posture that makes them. |
| `tract/vowels.js`, `tract/postures.json` | each vowel's formant targets, and the postures the inversion found for them (what is actually used; yours to edit). |
| `tract/phonemes.js` | consonants as constrictions (organ, place, area, voicing, timing), and the IPA reader. |
| `tract/planner.js` | sounds → movement: vowels as one slow gesture of the whole tract, consonants as quick gestures of one organ laid over it, the folds' gestures, lung pressure, pitch; every track lagged by its organ's time constant. |
| `tract/synth.js` | movement → sound, and the voices (a head's scale, a larynx's size). |
| `tract/config.js` | every number of all of the above as one JSON document (`bannerfield-tract/1`). |
| `tract_worklet.js` | the same tube running live in an AudioWorklet for the lab's "Hold sound". |

## What comes out of the physics by itself

Checked headless (`scratchpad/ref/tract*.html`), not asserted:

- **A uniform 17.5 cm pipe resonates at 523 / 1454 / 2417 Hz**, the same at 44.1 and 48 kHz; pushing the lips out
  1 cm lowers every formant. Without the yielding walls an /i/-shaped tube has F1 = 161 Hz; with them 231 Hz — which
  is why no real vowel goes lower.
- **A voiced stop's voice bar fades on its own.** During the closure of /b/ the glottal flow falls 308 → 48 cm³/s as
  the mouth fills and the pressure across the folds drops below what keeps them swinging; at the release it is back.
  Nothing in the planner says so.
- **A voiceless stop is silent, then bursts, then is breathy**: the closure holds the lung pressure (flow ≈ 0), the
  release discharges it past the teeth, and the folds — still apart, because the language is English — leak turbulent
  air until they come back together. Aspiration is `languages.en.aspirate`, a timing of the folds, not a noise burst.
- **s and ʃ differ because the cavity in front of the jet differs**; f and θ and x are quiet because their jet does
  not strike the teeth (`acoustics.noise.wall`).
- **Coarticulation**: a /k/ is made where the vowel has the tongue body (front before /i/, back before /u/); lips
  round through the consonants before a rounded vowel; a short vowel between consonants never reaches its posture.

## The four paranasal pairs, and a voice drawn again (2026-09-24)

The nose had two side rooms on it: the maxillary pair as one, and the frontal and ethmoid lumped together.
There are **four** pairs and they are four different rooms, so they are four now -- sphenoid, maxillary,
ethmoid, frontal -- each a Helmholtz resonator (a room of air breathing through its ostium down its neck)
hanging off the nose *where it really drains into it*, from the sphenoethmoidal recess at the back to the
frontonasal duct at the front. Each puts a zero in the nasal transfer function at its own frequency:

| pair | volume | ostium | neck | its zero |
|---|---|---|---|---|
| sphenoid | 7.5 ml | .04 cm² | .45 cm | ~606 Hz |
| maxillary | 15 ml | .05 cm² | .5 cm | ~455 Hz |
| ethmoid (the cells as one) | 5.5 ml | .055 cm² | .3 cm | ~1017 Hz |
| frontal | 7 ml | .066 cm² | .6 cm | ~698 Hz |

It is the SPREAD of those zeros between 400 and 1100 Hz that makes a nasal sound like a head rather than a
pipe, which is why lumping two of them together was worth undoing. They all scale with the voice's head.

**Randomize** (the button, or `?random=1` -- `?random=<word>` to seed it) draws a different person from the
same parts: every general setting moves -- the head's shape, the larynx, the habits of the way this voice
speaks. What a sound IS never moves: the phonemes, the vowel targets, the postures, the languages and the
timing tables are untouched, so the new voice says exactly the same words in exactly the same language and
sounds like somebody else saying them. (Its `postures` are dropped, though: a voice re-fitted to the head it
had has no business keeping them for a head it no longer has.)

Two things decide whether the result is a person rather than a caricature, and the first version of this got
both wrong:

- **A bell, not a flat draw.** Each setting comes from a normal distribution about the voice's own value --
  sigma a sixth of its slider's range, clipped at two and a half of them -- and the ratios (f0, the head's
  oral and pharyngeal scale, pressure, gain) from a log-normal, so half again and two thirds are equally far
  away. Drawn flat over a slider's whole range, "a mouth that hardly opens" is exactly as likely as an
  ordinary jaw, and thirty of those at once is nobody.
- **Every draw measures from the same place.** The first draw for a voice remembers where that voice stood,
  and every draw after it starts from there. Multiplying the CURRENT value instead is a random walk: press
  the button ten times and the head has wandered off, each press compounding the last -- which is exactly
  what it did, and what it sounded like. Checked with 24 draws in a row: f0 mean 110 Hz against a base of
  112, sd 14; the oral scale 0.997 against 1.000, sd 0.05; the last six draws no further out than the first
  six.

## The inversion

`Fit from here / from scratch` in the lab, and `Re-fit all vowels…` after any change to the anatomy (postures
fitted to one head do not fit another — a tip resting near the ridge became a closure once the tip's own gap was
measured, and every vowel had to be re-fitted). The cost is formant distance in octaves, plus a small price on every
articulator's distance from rest (many postures make the same formants: take the lazy one; the tip costs six times
as much, because vowels are made with body, jaw and lips), plus a price on a vowel that nearly shuts the airway.
All 21 vowels fit to within 1–2 % on F1 and F2. The rhotic vowel /ɜ/ does not reach its F3 of 1700 Hz: this tongue
has no way to bunch or curl.

## Four bugs worth remembering

- **The lips were not in the tube.** The sections covered the first 15 cm and the rest was "extra length", so every
  lip setting gave the same formants. The array is now anchored at the lips, and the two ends that really are
  uniform tubes — the lip tube and the tube over the folds — are the variable-length delays.
- **A shut mouth could not hold pressure.** A loss factor on the waves drains a steady pressure too, and walls with
  mass and friction but no spring give way for ever. Losses now act on the flow only (R−L), and the walls have
  stiffness.
- **A closure one point wide vanished** when the area function was averaged onto sections; a section now takes the
  exact minimum over its span when something narrow lies in it, eased into the mean so that nothing clicks.

- **The nose made energy from nothing.** The three-way joint at the velum admitted what a port of the velum's area
  admits, but the wave then travelled on in a nose whose first section had its full area: a nearly shut port passed
  the mouth's whole closure pressure into a wide pipe, the nose rang at several times lung pressure, and the output
  clipped on a single sample. The port now IS the nose's first section.

## "It sounds like random letters" — and what that turned out to be

The first version produced a human-sounding voice saying the wrong sounds. Two measurements found why, and both
are now standing checks (`scratchpad/ref/tract9.html`, `tract11.html`):

- **What the mouth actually does in a word.** For each vowel's midpoint, the formants of the posture the planner
  really produced, against the vowel's target; for each consonant, the narrowest opening it really reached. It
  showed /t/ in "water" never closing (1.0 cm²), /ŋ k/ in "thanks" never closing, /ʃ/ in "fish" and /s/ in "thanks"
  jammed shut, and the /i/ of "very" with F2 at 1256 Hz instead of 2250 because /ɹ/'s gesture was still on it. The
  cause was one design decision: every gesture went through a slow second-order lag, and a consonant was solved
  once, against a posture the mouth had left by the time the gesture arrived. Now only the slow vowel gesture is
  lagged; a consonant's constriction is solved FRAME BY FRAME against the posture the mouth really has, comes in and
  goes out by a smooth weight, and is exact while it holds. Body consonants are placed before tip and lip ones (a tip
  that asks the body for help must not pull a /k/ open), and the tip is tucked down for a body consonant (or it rides
  up with the body and becomes the narrow place itself). Mean vowel error went from 0.34 to 0.13 octaves and every
  constriction reaches its area.
- **What a fricative's noise really is**, measured over the fricative alone (band spectrum and level against the
  vowel). /s/ was 42 dB under the vowel and every voiceless fricative had the same spectrum — the glottis's
  aspiration: there was no frication. An earlier level check had included the voiced transitions, and on that
  reading the turbulence had been turned down twice. The jet is now found as the narrowest section (the lips
  included, a long palatal constriction included), its flow read from its own waves, its noise band-limited and
  injected where the jet ends. /s/ −10 dB with its energy at 2.5–8 kHz, /ʃ/ −11 dB peaking at 2–2.5 kHz, /f/ −30,
  /θ/ −23.

## Gestures are driven movements, not fades

The second round of listening: "every movement is strictly exact, ignoring what comes before and after; it moves
in straight lines; two n's in a row and the beginnings and ends of words are wrong (man now)". All three were true.

- **A gesture is a switch answered by a critically damped spring**, not a weight faded in over a fixed 38 ms. It is
  switched on `gesture.ahead` time constants before its sound, so that it ARRIVES on time — which means a slow organ
  (the jaw, 27 ms; rounding, 26; the velum, 26) starts during the sound before, and a quick one (the tip, 11) does
  not: anticipation and carry-over fall out of each organ's own clock, and because the clocks differ the mouth's path
  from sound to sound is a curve. The target of a closure lies a little beyond the contact, so the closure is made at
  speed and held with pressure. Helping movements let go quicker than they came (`gesture.carry`).
- **The same consonant twice is one gesture** (`timing.twin`, x1.5): "man now" has one long n, not two.
- **The first and last sounds of an utterance.** A consonant that starts an utterance is already formed when the
  breath comes (or the voice starts through a half-made /m/: "uh-man"); one that ends it is HELD until the voice has
  gone (released into a running voice it grows a vowel: "man-uh"); a final voiceless stop is held longer still, so its
  burst comes on falling pressure. A pause drops the pressure and parts the folds.
- Turbulence builds up over a few milliseconds (`acoustics.noise.buildUp`): a release is not noise in its first
  instant, which was making every /t/ a small explosion.

## Clicks: four causes, one family

"The c of computer is super-clicky; wolf alone is passable but in wolf is the l clicks". A click is a discontinuity,
and each of these was a place where something changed in a step while air was flowing (`ref/tract6.html?spike=1`
reports the loudest sample of an utterance and its neighbours: after these fixes it is always the crest of a vowel).

- **A section that changes size must keep its pressure and its flow, not its two waves.** In a narrow place with air
  streaming through it the two waves are huge and nearly cancel (+36000 and −34000 for a pressure of 2000), so changing
  the area under them invents flow. R−L is now rescaled by old area / new area whenever an area moves — in the mouth
  and in the velar port.
- **Joints must not hop.** The velum's three-way joint was re-placed every frame from the posture, and moved a section
  whenever the mouth's path length changed: every /ŋ/ clicked. It is placed once per tube. The yielding-wall branches
  used to switch off below an area threshold, taking their flow with them; they fade. A /k/'s place used to jump from
  "velar" to "palatal" as the vowel's tongue position crossed a threshold — a centimetre in one frame; it slides.
- **The velum stays shut through an obstruent.** Opening early for the /m/ of "computer" it vented the /k/'s closure
  pressure through the nose; still open from the /ŋ/ of "thanks" it did the same at the /k/'s release. Anticipatory
  nasalisation now waits for the last obstruent to end, and a nasal before an obstruent shuts its port early and fast.
- **An /l/ is never a stop.** The tongue's sides are down before the tip closes and until after it has gone
  (`gesture.lateralLeadMs / lateralLagMs`); before, the tip arrived first and the /l/ began with a closure and a burst.
- The output is the mean of two successive samples: a wave caught between two neighbouring joints goes round once per
  sample, which is the model's grain at the very top of the band, not a sound.

## Fourth round: t/d clicks, voice bars, creak, "cup of", r

- **Where a cut lies along the tract is read off the fixed wall**, not off the tongue. Positions used to be measured along
  the line through the cuts' midpoints; every movement of the tongue tip re-routed that line, the tract's length jumped
  by a centimetre between two frames (16.8 → 15.9 → 17.3 cm) and a closure hopped three sections of the tube -- which
  opened a section holding the lungs' pressure. That was the click on every t and d. (`anatomy.midline`; postures re-fitted.)
- **A section's area is the harmonic mean over its span** (what a stretch of pipe does to the flow goes with length /
  area), so a constriction shorter than a section is still one.
- **A release is the organ LEAVING at 20–50 cm/s** (`gesture.stopRelease` 21 ms for the tip, 24 for the body, 11 for the
  lips, which have a centimetre to go and must open for the schwa of "cup of"); the tip peels off the ridge
  (`anatomy.tipPeel`); turbulence past `noise.knee` grows with the flow, not its square. A final voiceless stop lets go on
  time, on a falling breath, instead of alone in the silence after the word.
- **The tip's constriction has a length** (`anatomy.tipLength`, 0.8 cm of blade against the ridge). As a single point of
  the area function it slid, while the tongue drew back, from one section of the tube into the next -- and the section
  it left went from 0.14 to 0.68 cm² in half a millisecond: the click that was left on /t/. With a length, neighbouring
  sections share the constriction and hand it over gradually. (Changes the vowels' tubes too: postures re-fitted.)
- **Voice bars are heard through the skin**: the yielding walls' own movement is radiated (`walls.radiate`, high-passed at
  `radiateAboveHz`). Without it a /d/ was a gap: "did" had no d's.
- **The tune has a floor** (`prosody.floor`): fall + declination + a short word took 112 Hz to 70 Hz inside one syllable, and
  a voice that low on a failing breath creaks (the "nd / nt" creak).
- **An English r is a shape, not a place** (`organ: "posture"`): F3 1740–1860 against an l's 2750. As a raised tip with a gap
  it was an l. Closures and fricatives made after it take their organ back.
- Voiced fricatives get more breath (`prosody.rest.voicedFricative`) and a jet at the lips radiates (`noise.lipGain`): f −28 dB.

## Fifth round: "and pig", "ei"

- **A voiceless stop's folds are apart EARLY in the closure** (`prosody.stopOpenBy`: fully open by 55% of the way, then they
  wait for the release). Parting evenly right up to the release, they let the voice run 50 ms into a closure that followed
  a voiced one -- the yielding walls keep the flow going -- and "and pig" was "and big". Now the voice is gone in 20 ms.
- **A diphthong is named after where it starts and where it HEADS** (`DIPHTHONGS` in phonemes.js): "eɪ" as [e]→[ɪ] is
  400/2100 → 400/1900 Hz, no movement, heard as a long i. It is ɛ → i (547/1700 → 324/2200 in "make"), "oʊ" is ɔ → u; the
  glide sets off at `timing.vowel.glideAt` (.45) of the vowel, and a diphthong is never lax-short.

## Sixth round: a vowel shut in between two closures ("what it is")

"I can never be sure what it is" was cut off around "what". Measured per phone (level against the loudest vowel, the narrowest
place in the tract, the folds' opening): the ɪ of "it" was **−67 dB with the tract shut from 0.00 to 0.00 cm² and the folds
0.116 cm² apart** — the t of "what", the ɪ and the t of "it" were one 176 ms closure with silence inside it. Two causes, both
now rules:

- **A vowel between two constrictions is given the time to be one** (`timing.vowelRoom` = `{ x: 1, tight: .3 }`). The consonant
  before it needs `gesture.ahead` × its release time constant to let go of the organ (a tip stop: 3 × 21 ms) and the one after
  it takes hold `ahead` × its own beforehand (3 × 11 ms): 96 ms in all, and the vowel was 47. Both gestures pull the same
  organ shut, so a vowel shorter than the two together is never reached at all — the weighted blend of "closed" and "closed"
  is closed. The vowel is now floored at that length, which is the same answer the limiter gives a movement that is too far
  for its gesture: take the time. `x: 0` switches it off; `tight` is the opening below which a consonant counts as shutting
  the vowel in (between two open sounds the mouth is never shut in). The ɪ of "it": 47 → 96 ms, shut → **0.96 cm²**, −67 →
  **−10 dB**. Aside from that sentence: "computer" 0.198 → 0.061 octaves of vowel error, "cup of" 0.095 → 0.039, "Der Hund
  ist schlecht" 0.237 → 0.090 (its ɪ was the worst vowel in the set at 0.92), the eight together 0.174 → 0.123. Sentences
  grow about 3–4 %.
- **Aspiration goes with the stress of the vowel that follows** (`prosody.aspirateUnstressed` .35). English aspirates what
  begins a stressed syllable, not what runs into a weak one; aspirated in full, the t of "what" held the folds 0.116 cm²
  apart through the whole of "it" and the vowel was whispered away even when the tract did open. The fold gesture is also
  shorter for it (`asp` scales both the peak and how long the folds stay apart).

The two time constants of a consonant's gesture (how fast its organ takes hold, how fast it lets go) are now worked out in one
place, `gestureTau()`, because the durations need them as well as the gestures.

## Seventh round: "it is" as bad radio — the flap

With the vowel between the two t's of "what it is" given its time (above), it was audible but ugly: "bad radio". Traced through
the tube 10 ms at a time, the 96 ms vowel was open for **30 of them and only to 0.67 cm²** — the rest of it was the tip still
leaving one closure or already making the next, and what came out was turbulence through a nearly shut mouth: its loudest band
was 0–400 Hz, there was no F2 at all, and 4–8 kHz sat only 20 dB down (a vowel sits 32–43 dB down there).

The cause is not the timing but the phonology: **American English does not say a full /t/ there.** `languages.en.flap` (1.1, the
effort below which it happens, as `timing.assimilate`) turns a t or d between two vowels, the second unstressed, into the tap `ɾ`
— the consonant that already existed for Spanish. It fires exactly where a speaker's does: water → wɔˈɾəɹ, city → sɪˈɾi, little →
lɪˈɾəl, writer → ɹaˈɾəɹ, "a lot of it" → əlɔˈɾəv ɪt (the last t, before silence, stays a t); and not in today, attack (a stressed
vowel follows) or "after tea". `en-GB` has no `flap` — British glottalises instead — and `flap: 0` switches it off.

A tap is one quick flick (`gesture.tau.tap` 5 ms) rather than a closure held and released, so the vowels around it keep their own
time and open properly. The same stretch of sound: the ɪ of "it" now runs 60 ms and opens to **1.61 cm²** with the narrowest place
back in the palate where the vowel makes it, no turbulence at all, and an F2 in the spectrum; the two vowels are −6 and −7 dB
under the loudest vowel of the sentence instead of −11 and −12; the sentence is 1980 ms instead of 2061. The eight utterances:
0.126 → 0.118 octaves, and "computer" (which an American flaps too) 0.061 → 0.021.

One consequence to know about: the tip has a long way to go for the flap of "computer" after /uː/, and the limiter says so
(tipY 22 % over) — so that word is now planned again with its vowels lengthened, 1071 → 1192 ms. That is the engine's usual
answer to a movement that is too far for its gesture; if it is too much, `gesture.tau.tap` may be raised (8 ms puts it back to
1108 ms) at the cost of a less flick-like tap in Spanish.

## Eighth round: the z, and the gap at the back of the glottis

"There is some problem with z as well — a human releases some component of that sound at a different time." Measured band by
band through "this is", against the /s/ of "this" in the same utterance:

| | flow at the constriction | hiss (3–8 kHz) |
| --- | --- | --- |
| /s/ | 250 cm³/s, steady (min 247, max 250) | −7 … −11 dB |
| /z/ (was) | max 226, **min 0** | −20 … −24 dB |

The /z/'s glottis shut completely on every cycle, so there was a jet only half the time and its hiss was 13 dB under the /s/'s.
Worse, the loudest hiss of the word came 60 ms AFTER the voice had gone, when the folds parted for the final devoicing and the
flow rose: the sibilance detached from the voiced part and was heard as a separate s let go at the end. That is the component
arriving at the wrong time.

Two things were missing, both now in:

- **The chink at the back** (`glottis.chink`, driven by `prosody.rest.voicedChink` = .04 cm², capped at `glottis.chinkMax`).
  Real folds let air through a gap between the cartilages while the membranous folds in front of it go on meeting: the voice is
  there AND the air never stops. In the model it is a term added after the soft clip at zero, so it does not swing with them:
  `area = softclip(rest + swing·wave) + chink`. The planner raises it over a voiced fricative on the same bell as the folds'
  rest opening (`bellOn`, which the rest opening now shares). The flow through the /z/ no longer falls below ~70 cm³/s and its
  hiss rises to −15 … −19 dB.
- **The final devoicing is gentler** (`prosody.finalDevoice` .75 → .45). At .75 the folds ended a final voiced fricative as far
  apart as for an /s/, and because opening them lets MORE air through, the hiss grew while the voice died. At .45 the voice
  still goes (it is down 40 dB within 20 ms of the end) but the breath goes with it, so the hiss fades from −15 to −54 dB over
  the last 70 ms instead of swelling.

In the sentence that prompted it the final z now holds a steady hiss at −25 dB through the voiced part and fades away with the
voice; a medial z ("his eyes") keeps its voice at full strength at any chink between .03 and .05, so the change costs nothing
in the middle of a word. The eight utterances are unmoved at 0.118 octaves — the chink touches only voiced fricatives.

The lab's live "Hold sound" has a chink slider next to "folds apart", and the worklet takes it, so the two ways of letting air
through the glottis can be heard against each other.

## Whose r

No two English speakers' /r/ are alike, so the r is not one posture but three, and two numbers of the speaker's between them
(`consonants.ɹ.shapes`, `shapeBy: ["rShape", "rStrength"]`; the sliders "r: bunched … retroflex" and "r: weak … full"):

| | how it is made | F3 of the posture | F4 / F5 |
| --- | --- | --- | --- |
| `bunched` (rShape 0, the default) | the tongue ROOT back into the pharynx, 0.60 cm² there; the blade flat | 1708 Hz | 3917 / 5353 |
| `retroflex` (rShape 1) | the TIP curled right up, the constriction at 12.9 cm, the room under the tongue behind it | 1555 Hz | 3216 / 3779 |
| `weak` (rStrength 0) | the root only a little back, the lips nearly unrounded | 2268 Hz | — |

That is the real difference between the two: alike in F1–F3, apart above, exactly as they are in people. In running speech the
retroflex reaches further (F3 1359 Hz in "red" against the bunched r's 2063) because the tip is the quickest thing in the mouth
and the root the slowest — a difference between speakers that falls out of the anatomy rather than being written down.

The retroflex shape was not written by hand: once the room under the tongue existed (`anatomy.sublingual`), the inversion was
asked for r formants from a curled-tip start and found it. Before that room was built, curling the tip RAISED F3 (1708 → 2048)
and no retroflex r was possible — measured over a sweep, what lowers F3 in this mouth is the constriction in the pharynx
(bodyY −0.4 → −1.6 takes F3 2491 → 1708) and rounding takes another 40 Hz. Drawing the root further back than the bunched
shape shuts the pharynx altogether, so that end is at the geometry's limit.

The rhotic VOWEL (ɜ, ɚ) is a posture of its own in `postures.json` and is not touched by these knobs; its F3 of 1700 Hz is
still out of reach, because a vowel is fitted with the tip near its rest and so has no room under the tongue.

## The d of "dog": the sides have to come up

"The old dog is very bad" — the /d/ made a click. Traced 4 ms at a time, the /d/ was not a stop at all: from the /l/ of "old"
onward the mouth narrowed from 0.34 cm² to 0.01 over **84 ms**, hissing the whole way (turbulence 26–48 all through it), reached
a closure for about 16 ms, and then flew open from 0.02 to 1.09 cm² in 12 ms with 8 cm H₂O behind it — a gust, which is what was
heard.

The cause was the lateral. The tongue's sides are down for an /l/ and the front of the mouth is held open by
`anatomy.lateralLeak` while they are; the gesture ends early when a closure follows (`-12` ms), but its tail decays at the
sides' own time constant and was still leaking 70–90 ms later. So the tip was on the ridge from the start and the air went
round it: the closure was finally made by the LEAK dying rather than by the tongue, and the release had no organ behind it.

`gesture.lateralShut` (.45): when what follows is a closure, the sides come up × that much quicker. Now the /d/ is silent
within 30 ms, holds a real closure with a voice bar for 40 ms, and bursts on the release as a /d/ should. The value is set by
what the tongue can do rather than by taste — at .28 the limiter says the sides are 23–32 % over their speed and stretches the
sentence by 4 %; at .45 it is quiet, and at 1 (the old behaviour) the closure is never reached at all (0.01 cm²).

## The /h/ of "heute": folds that were never given time to open

German "ist heute", and only in some contexts. The /h/ wants its glottis at 0.2 cm² (`consonants.h.breath`); it was reaching
**0.06**, and what came out was not breath but a squeezed hiss — loud with it, −11 dB under the vowel where an /h/ belongs
around −20.

The cause was a rule meant for something else. An /h/ after a stop starts to part its folds only
`prosody.breathAfterStopMs` before the stop ends, because parting them during a stop makes its release a gust ("and his" had a
tick for its /d/). But that rule was applied after EVERY stop — and after a voiceless one there is nothing to protect, since
the folds are already apart for the stop itself. With the wait, the /h/ had 12 ms to open a glottis whose own speed limit
(`limits.rest.speed`, 7 cm²/s) needs 29, so the limiter held it back and the /h/ was made through a nearly shut glottis.

Now the wait applies only after a VOICED stop, and no breath gesture is ever asked to open faster than the folds can move
(`c.breath / limits.rest.speed`). "ist heute": the glottis reaches 0.159 and the /h/ falls to −23 dB (woman) and −16 (man).
"and his" still keeps its /d/ voiced through the closure (folds at 0.003) and its /h/ still opens.

## The click that was only some voices: a room hanging off a closure

The /d/ of "dog" still clicked for the woman after the lateral fix, and not for the man. Measured across the voices, the
loudest sample step as a share of the loudest vowel: man 17 %, child 20 %, woman 54 %, breathy 61 %, deep 68 % — not a
question of head size (the child has the smallest head of all), which meant alignment, not scale.

Sample by sample through the release, the areas were gliding smoothly and there was no numerical jump: what came out was a
genuine transient, half a cycle at about 6–7 kHz, the front cavity ringing as the closure let go. The cause was found by
taking the new parts away one at a time: with `anatomy.sublingual.area: 0` the woman's step fell from 70 % to 17 %.

**The room under the tongue was open during the closure.** The tip is raised for a /d/, which is all the old test asked, so a
1.1 cm² room hung off the joint behind a closure holding the lungs' pressure — and emptied into the mouth when it opened.
Physically it should not be there at all: the same contact that makes the /d/ seals the room off from the tract.

Two things now gate it, and it took both:

- **`sublingual.opensAt` ([.06, .22] cm², × this head's own size)**: the room opens only while the air can get past the tip AND
  the mouth is not shut somewhere else. Unscaled, a big head's closure counted as open and the bang came back — which is why
  `deep` was the worst of the five.
- **`acoustics.sublingual.openMs` (30 ms)**: it is sealed AT ONCE by a closure, as flesh is, and opens again only as slowly as
  the tongue changes shape. Opening at the tube's own 5 ms it ramped in while the burst was still ringing; opening AND shutting
  slowly was worse still (it stayed open from the /l/ right through the closure).

All five voices are now between 14.7 % and 20 % — the ordinary crest of a vowel — and the retroflex r still has its room:
F3 1359 Hz, unchanged.

The two guards added while hunting this (`acoustics.areaRate`, a cm²/ms cap on how fast a section may change, and
`areaDoubleMs`, a cap on how fast it may grow in proportion) did NOT fix it and never fire in ordinary speech. They are kept as
what they are: a floor under any future frame of nonsense, at two flops a section.

## Sounds nobody makes

The limiter says what a mouth CAN do. This says what a mouth would never be caught doing — a last pass over the plan
(`planner.js SANITY`, config section `sanity`, `on: false` to see what it was mending), after the limiter, on the tract the
plan really produced:

| the rule | what it catches | how it mends |
| --- | --- | --- |
| **a vowel is an open mouth** (`open` .22 cm²) | the "bad radio" sound: a vowel whose mouth never opens, so the voice comes out as a buzz with a jet hissing through it | moves whatever is nearest the wall out of the way (`openBy` 1.1 cm at most), all of it at the vowel's widest moment, eased over the vowel |
| **a voice needs breath** (`voicePressure` 3.2 cm H₂O) | a creak nobody asked for: voicing going on with too little pressure across the folds to swing properly | lifts the breath to that floor. The LAST vowel of a sentence is exempt — a sentence is meant to run out of air — and a breath still rising at the first sound is not sagging |
| **the nose is not a relief valve** (`nasalPressure` 2.2, `nasalPort` .12) | gurgling: the velum standing open while the mouth is shut and holding pressure, letting the closure out of the wrong door | shuts the port to `nasalPort` |

Three things make it a safety net rather than a patch. It is measured on the **tract the plan produced**, not on what the plan
meant. It mends with the **smallest movement that will do**, smoothed and put through the limiter again, so nothing is mended
into a jump. And every firing is **written down** — `tracks.odd`, shown under the timeline in the lab, with what the narrowest
place was before and what it came to after: a rule that fires often is a bug earlier in the plan, not a fix.

It also refuses to lie: the "came to" is measured on the tracks as they finally stand, not on the trial that proposed the
mending, and where the answer is still a shut mouth the report says "and none to be had" — which means the fault is earlier
(too little time for the vowel), where `timing.vowelRoom` lives.

Nothing under `holdMs` (25 ms) is mended at all: a breath still on its way in at the first sound, a velum still coming down out
of a nasal, are a mouth working, not sounds.

On the engine as it ships the rules are almost silent — over the eight standing utterances exactly one fires (the /j/ of
"computer", squeezed by the /p/ before it, mended from a shut mouth to 0.24 cm²). Turned loose on the old broken plan that
started all this ("what it is" with `vowelRoom` off and no flapping), rule one finds the ɪ of "it" and opens it from 0.00 to
0.34 cm². That is the shape a safety net should have.

**What it costs**: the pass computes the area function once per control frame (every 5 ms for the vowel scan), which is about
8 % of a render — the only thing in this engine so far whose cost is worth stating. `sanity.on: false` takes it away.

## A person's way of speaking, and marks in the text

**Per voice** (`voices`, and the sliders "How this voice speaks"; defaults in `planner.js PERSON`): `range` scales every
movement of the pitch, `register` moves where the speech sits, `liveliness` scales the accents alone, `rate` is tempo,
`finalLengthening`, `pauseScale`, `legato`, `anticipation`, `jawFreedom`, `vibratoHz / vibratoDepth / vibratoDelayMs`, `flutter` and
`jitter` (x the glottis's). Head + larynx + these is one person.

**In the sentence** (written text or IPA — `lexicon.js` passes them through with `{ marks: true }`, and drops them for
`speech.js`):

| written | does | configured in |
| --- | --- | --- |
| `*word*`, `*two words*` | emphasis: a bigger accent without downstep, more breath, a longer vowel; the accents after it in the phrase shrink (post-focus). An unstressed word (`*the*`) becomes stressed. | `prosody.emphasis` |
| `(slow: …)` `(fast: …)` `(high: …)` `(low: …)` `(loud: …)` `(soft: …)` | that way of speaking while the brackets last; they nest and may run over several sentences | `prosody.styles` (add your own: tempo, pitch, pressure, range, rest) |
| `(…)` | an aside: lower, quicker, flatter, set off by short pauses | `prosody.styles.aside` |
| `,` `;` `:` `…` | a pause, and a new PHRASE | `voices.*.pauseScale` |
| `.` `?` `!` | fall / rise / more force | `prosody.finalFall, questionRise, exclaim` |

**Phrases** (`prosody.phrase`): what stands between two pauses has its own share of the declination (`reset`), ends
with a continuation rise if more follows, draws out its last syllable, downsteps its accents, and runs a little
faster in its middle (`tempoArc`); a row of unstressed syllables is compressed (`rhythm`).

**Anticipation** is how far in advance the mouth moves for what is coming — one number (`voices.*.anticipation`, the slider
"anticipation") over the three places the engine moves early: `timing.gesture.ahead` x an organ's own time constant (a consonant's
gesture, so that it ARRIVES on time), `timing.gesture.vowelAhead` x the tongue body's (the slow vowel layer, read that far ahead of
itself), and `timing.vowelSwitch` raised to that power (where in the consonants between two vowels the tract turns to the next).
1 is the engine as tuned; 0 is a mouth that starts every movement at its own sound and therefore arrives late everywhere (the
sounds undershoot, but nothing is asked to move faster — a spring's speed is its time constant's, not its deadline's); 2 runs ahead
of itself and swallows short vowels. Where moving that early DOES ask an organ for more speed than it has, nothing is forced: the
limiter reports it and the sentence is planned again with those sounds LENGTHENED (`limits.slowDown / maxStretch / passes`) — the
same machinery that takes the time for a movement too far for its gesture. Measured over eight utterances (mean distance of each
vowel's midpoint formants from its target, and how the lengthening answers):

| anticipation | vowel error | sounds lengthened | still held back | the eight together |
| --- | --- | --- | --- | --- |
| 0 | 0.223 oct | 6 | 1 | 9.77 s |
| 0.5 | 0.175 | 7 | 1 | — |
| 1 | 0.174 | 10 | 1 | 9.89 s |
| 1.5 | 0.227 | 10 | 1 | — |
| 2 | 0.330 | 12 | 4 | 10.01 s |
The leads that keep a sound from breaking are NOT scaled by it: an l's sides (`lateralLeadMs`), the velum before an obstruent
(`velumLeadMs`), the guard that keeps a vowel open for `gesture.vowelShare` of itself.

**Legato** is one number over what already connects speech: at 0 gestures start late and settle fast, consonants are
longer, the breath lets up between words (`prosody.staccatoGapMs`); at 1 gestures start early, helpers let go slowly,
vowels undershoot more and the pitch glides. .5 is the timing as configured.

**The trill is beaten by the air** (`acoustics.flap`, `timing.trill`). The planner only holds the tip near the ridge
(`trill.area`); in the tube the tip is a sprung mass, preloaded shut, pushed open by the pressure behind the closure and
pulled back when the air streaming through the gap lowers the pressure in it. Measured: "perro" 4–5 beats at ~27 Hz
with 10–15 dB of modulation, "rosa" 2 beats once the breath is there, "tres" a single beat — none of that is written
anywhere. `trill.physical: false` brings back the timed open-and-shut.

## "and his"

- **An h after a stop waits for the stop** (`prosody.breathAfterStopMs`): its folds were parting during the /d/'s closure, so
  the /d/ was released through an open glottis -- a gust, heard as a tick.
- **A voiced fricative that ends the utterance loses its voice** (`prosody.finalDevoice`): the folds part from its middle on and
  stay apart. Before, "his" ended in a buzz with no hiss and then, let go with the voice still running, a little vowel.
- Frication re-balanced after the tip got a length (three narrow sections creep more than one): `noise.gain` 4.5e-6, s .13 / z .15
  cm2, and the teeth's effect falls off with the jet's distance (`noise.teethFull`) -- s -12.6, sh -8.3, f -13 dB re the vowel.

- **The velum is on its way up before a nasal ends** when something oral follows (`gesture.velumLeadMs`), quicker when an
  obstruent is two sounds away: closing only after the m, it was open through the vowel of "doom is" and into the z -- and a z
  with the nose open is an n ("doom in"). Velum at the z's start: .23 before, .03 now.

- **Another head is the reference head, stretched** -- tongue and all. The tongue body used to be a circle of the MEAN scale inside
  a vault scaled by the smaller one, so in a child's head (and a little in a woman's) it stood nearer the palate: the /ɪ/ of "doom is"
  had a palatal channel of .16 cm2 and was heard as a nasal, though the velum was shut. Geometry is now worked out in the reference
  head and stretched (the body is an ellipse); an area is the reference area x the stretch along the gap x the stretch across. The
  man's numbers are unchanged; a child's areas are ~.5 of his, its formants ~1.3x.

## Effort: lazy to careful

One number per voice (`voices.*.effort`, slider "effort"; in the text `(lazy: …)` / `(clear: …)`; an emphasised word gets x1.2).
Below 1 the speaker does not bother to go all the way: vowels are AIMED short of their postures (unstressed ones more), the mouth
settles slower, fricatives and approximants are left wider, the jaw is raised less for consonants, unstressed vowels shrink, accents
and breath get smaller. Above 1 the opposite (vowels are never aimed BEYOND their postures: that shuts the lips of an u). 1 is the configuration as written; what each part amounts
to is `prosody.effort`. Closures stay closures at any effort.

## The head scales everything (nose, walls, sinuses)

`Tube(fs, length, cfg, seed, head)`: the nose is as long as the mouth's scale says and as wide as the head's cross-section; the
walls' surface goes with the cross-section and their mass, friction and spring with their thickness; the piriform sinuses
(`acoustics.piriform`: a closed side branch at the top of the larynx tube, a delay there and back) go with the throat. The sinuses
add the 4-5 kHz dip of every real voice (higher in a shorter throat) and lower F1/F2 by 5-13 %, so the postures were re-fitted.

Two things learned on the way. (1) Re-fitting the postures FROM SCRATCH after a small change to the tube can land on an unnatural
twin (an /u/ with the jaw 20 degrees open and the lips all but shut -- right formants, and the lips then shut over every sound next
to it): re-fit from the postures that were (`ref/tract5.html?from=1`). (2) A stop let go into a narrow sound of the same organ ("and
soup", "it's", "cats") releases as quickly as it closed, like an affricate; let go slowly its closure lay over the s for 60 ms.
For small heads: consonant openings go with the head's length scale, the slit's friction with the mouth's width, and the folds' rest
opening with the square root of their size.

## Voice quality, per person

All in `voices.*` (sliders under "How this voice speaks"), all 1 or 0 by default, each a physical cause rather than a filter.
Measured on one sentence (`scratchpad/ref/tract22.html`; tilt = 2-5 kHz re 0-1 kHz, ring = 2.5-3.5 kHz re 0-1 kHz):

| setting | what it is | measured |
| --- | --- | --- |
| `rest` | the opening the folds voice at: below 0 pressed, 0 modal, above breathy | .03: tilt -1.6 dB, breath noise |
| `closure` | how sharply the folds shut (`glottis.soft` /, `skew` x): brightness, pressed..warm | 2: tilt +1.9 dB, louder; .5: -2.5 dB |
| `swing` | how far the folds open: above 1 "flow" voice | 1.4: +2.8 dB level, tilt +2.9 dB |
| `ring` | the tube over the folds narrower and a little longer -- a resonator of its own near 3 kHz | 1.6: ring +6 dB; 2.2: +11.5 dB |
| `fry` | creak over the last `prosody.fry.ms` of a falling sentence | f0 falls to 44 Hz at the end |
| `creakiness` | creak throughout | .7: f0 55-95 Hz, -3.7 dB |
| `nasality` | the velum never quite shut -- except under and around sounds that hold pressure (`prosody.nasalityPort`) | velum in vowels .15 -> .27 |
| `lipSpread`, `smile` | lips' corners drawn back: a wider, shorter lip opening; a smile adds a raised larynx and a semitone (`prosody.smile`) | smile 1: f0 +4 %, F2/F3 up |
| `larynxHeight` | cm: up bright/young, down dark/warm (also lengthens the tube over the folds) | -1: ring +4.9 dB, formants lower |
| `jawSetting` | degrees added to every vowel | |

Creak (`glottis.creak`) is the folds pressed and slack: pitch down by 45 %, cycles in long-short pairs, irregular, shut for most
of each cycle, still swinging on little breath. In the text: `(creaky: …)`, `(smile: …)`.
The stretch of tract below the section array (a delay line) now has the larynx tube's own area and a joint where it meets the array;
before, it was taken to be as wide as the first section.

## The jaw, and the lips that ride on it

Two couplings, one of the head and one of the speaker.

**The lower lip is on the chin** (`anatomy.lips.jawShare`, 0.7). The lip opening is now the jaw's own opening at the teeth, times
that share, plus what the lips do themselves — so `lipH` means the opening the LIPS make ON TOP of the jaw's, and its range starts
at −1.6 cm: below zero the lips are closing over an open jaw (which is what /u/ and /b/ ask for after an open vowel). Drop the jaw
and the mouth opens with it; clamp the jaw for an /s/ (`jawMax` 3°) and the lips close with it by 0.25 cm of height, about
0.9 cm² of opening. Both the drawing and `solveLips` go through one function, `lipRide()`, so a consonant that asks for a lip
area still gets it exactly — the solver takes the jaw's share off first. A closure is asked for 0.25 cm BEYOND contact in the
lips' own coordinate, not at −0.25 flat, or a /b/ after an open jaw would not have closed.

`tract/postures.json` was compensated in the same move (every vowel's `lipH` less `jawShare` × its own jaw's ride), so the vowels
are **exactly** what they were: through the tube as it stands now, all 21 are within 0.004 octaves of the formants the fit
recorded. No re-fit was needed.

**How freely a person's jaw moves** (`voices.*.jawFreedom`, the slider "jaw freedom"): × how far every vowel takes the jaw from
that speaker's own `jawSetting`. 1 is the postures as fitted; 0 is someone speaking through nearly closed teeth; above 1 the jaw
works harder than the fit asked. The **tongue is put back** where the sound needs it (`anatomy.setJaw`: the body rides
`tongue.jawShare` = 0.45 of the jaw's turn, so a jaw held back would otherwise carry every vowel up with it) — this is what people
do with a bite block between their teeth, and it is why a clenched speaker is still understood. The **lips are not** put back,
because they are on the chin: a held jaw really is a smaller mouth. Consonants need no help at all — their constrictions are
solved frame by frame against the posture of the moment, so the tongue simply reaches further.

Measured over the eight utterances (mean vowel-midpoint formant error): jawFreedom 0 → 0.171 octaves, 0.4 → 0.155, 1 → 0.126,
1.4 → 0.121. A fixed jaw costs about 0.045 octaves of vowel distinctness — muffled, not destroyed, which is the point.

What is still NOT modelled at the lips: their orientation. There is a length, a width and a height, and the tube runs straight
along the axis; nothing represents lips turned up or down, rolled in or everted, and nothing aims the airstream. The jet's noise
knows only HOW FAR the constriction is from the teeth (`acoustics.noise.teethReach / teethFull / wall`) and whether the jet is the
lips themselves, in which case it radiates straight out (`noise.lipGain`). /f/ is a small lip opening with the jaw brought up, not
a lower lip against the upper incisors. Changing that means changing the front of the area function, and that does mean a re-fit.

## Losses that grow with frequency

`acoustics.wallLossHigh` / `wallLossCornerHz`: on top of the flat friction, each section loses more of its flow wave the faster it
changes (the wave less its own low-pass), so the loss is positive at every frequency and nothing at DC -- closures hold pressure as
before. Bandwidths of the man's /ə/ before -> after: F1 82 -> 82, F2 70 -> 82, F3 70 -> 117, F4 59 -> 117, F5 152 -> 211 Hz
(a mouth's: ~60, 90, 120, 170, 250). Formants move down 1-2 %, so the postures were re-fitted from where they were.
The space under the tongue tip was looked at and NOT added as a branch: the cuts in front of the tip already reach down to the floor
of the mouth, so that space is part of the front cavity (which is why sh peaks at 2-2.5 kHz and s at 4-5 kHz), and this tongue
has no undercut for a blind pocket to sit in -- one would have to be invented (.5-1 cm: a zero above 8 kHz).

## The end of a sentence

**The breath is let go in advance** (`prosody.finalPressure` .5, from the middle of the last vowel to the end of the last sound;
gone `finalPressureMs` 60 after it), as people do -- so the voice is fading when the last sound ends, not 120 ms later. Whatever the
mouth does while the voice still sounds is heard, so it waits for it, briefly: it starts back to rest `timing.restAfterMs` (130)
after the last sound, a final closure is held `gesture.finalHoldMs` (140) and a final fricative `finalFricativeHoldMs` (110).
After a final VOICELESS STOP everything waits `prosody.finalBurstMs` (95) longer -- the breath, the return to rest, the folds opening
to breathe: the stop is let go after its time is up and needs breath to burst ("meet" had no t), and a mouth opening on the rest of
that breath was a second puff.
History: the mouth used to set off for rest 12 ms after the last sound at full breath -- a final vowel became a diphthong ("see-uh",
+3 dB as the mouth opened), a final d or n was let go on the last of the breath, a final z opened while still hissing. Every ending
now decays monotonically (`ref/tract6.html?env=1`).

## Against monotony

`voices.*.variability` (0..1; amounts in `prosody.vary`): every accent gets its own size -- on the whole bigger, some nearly skipped --
and its own timing, every vowel its own length, every phrase its own pace and pitch level, the final fall its own depth. The draws are
seeded by the sentence's text, so a sentence always comes out the same way. With `range` (x every pitch movement), `liveliness` (x the
accents), `*emphasis*` and commas (each phrase resets the pitch and ends on a rise) that is what makes a delivery lively; `legato` is NOT
one of them -- it is how connected the sounds are, and it changes pace only slightly (consonants 10 % longer at 0, shorter at 1).
Two things found under legato: a vowel now keeps the first `gesture.vowelShare` (30 %) of itself free of the next consonant's closing
gesture, and a gesture slowed by the limiter is slowed on the side that was too fast only (coming or going) -- a g that had to come
slowly used to leave slowly too, and lay over the short vowel after it ("dog is" had no i, at ANY legato).

## Time by movement (an option)

`voices.*.byMovement` (0..1, slider "time by movement"; bounds in `timing.byMovement`). A sound's time is what the language gives it
PLUS what its movement takes. The sentence is planned once; for every sound the way each organ travels (from `leadMs` before it) is
measured against how fast that organ can go (`limits`) -- the time the movement would take at full speed; each sound then gets `gain` x
(its own - the average) ms more or less, within `least`..`most` of what it had, the sentence keeps its length, and it is planned again
(then the limiter's passes as usual). At 1, on "The old dog is very bad": diphthong and open stressed vowels grow (ou 196 -> 261,
a: 238 -> 308), r and the i after it grow (92 -> 111, 134 -> 200), schwas and stops with nowhere to go shrink (72 -> 47, 68 -> 44 at the
old bounds). A first version dealt time by the SHARE of a sound's time its movement needs: long vowels, which move little per ms, shrank --
the opposite of what length and stress are for.

## Vowel length

`timing.vowel`: `ms` (a plain vowel, 110), `laxMs` + `timing.lax` (the short lax vowels, 82), `long` (x for a vowel written with ː),
`stressed`, `unstressed`, `final`, `diphthong`. A language may override any of them: `languages.<lang>.vowel`. English keeps the
defaults (length is mostly quality; stress lengthens). Czech, Slovak, Hungarian: `long` 1.9, no lax set, stress lengthens nothing;
Finnish 2.1; German 1.7; Italian lengthens the stressed vowel (1.35); Russian shrinks the unstressed (.7); Spanish has no length.
Measured in "maːma" vs "mama": long/short 1.8 in cs.
**English**: ː is length as everywhere (`long` 1.4: beat 146 ms / bit 101, bead 187 / bid 129). The American dictionary used to write
its one open back vowel ɑː throughout ("not" [nɑːt], "dog" [dɑːɡ]) and both came out drawn out; the LOT words are now written with a
plain ɑ (313 entries; ɑː stays in father, calm, pasta). `beforeVoiceless` (x.78) clips any vowel right before a voiceless consonant:
not 74 ms / nod 182. **British English** is the language `en-GB` (derived word list, `lang_british.js`; ɒ is said as a short ɔ here,
linking r comes from the lexicon: "far away" [fɑːɹ əˈweɪ]). The lab's language list now also offers the languages that have no
dictionary (IPA only). Phrase rhythm (`prosody.phrase.rhythm`, `tempoArc`), effort and the voice's `rate` come on top.

**Fixed stress** (`languages.<lang>.stress`): the syllable a word is stressed on when its IPA carries no ˈ — counted from the end
(1 = the last) or, negative, from the start (-1 = the first). Slovak, Czech, Hungarian and Finnish are `-1`; a language whose
dictionary marks stress must not have it, or its unstressed words would be stressed. Why it matters: with nothing stressed, a whole
sentence is one row of unstressed syllables, and such a row is compressed (`phrase.rhythm`) — Slovak "to je tak ako keby" typed as
IPA had every vowel about a quarter short, and the a and o of "ako" were squeezed between the two velar closures until the mouth
never opened (F1 355 Hz where /a/ wants 750, the narrowest place never past 0.5 cm²: "ako" was heard as "k"). With the stress where
Slovak puts it the vowels are 96–134 ms, the a of "ako" reaches F1 608 and 1.3 cm², and the whole sentence's mean vowel error falls
from 0.249 to 0.102 octaves. (The a of "tak" is now lengthened x1.5 by the limiter, which reports bodyY 25 % over its speed there —
the tongue really does have a long way to go from /a/ to the velar closure.)

## The palatals (ɲ ʎ j ʝ ɥ)

j ʝ ɥ ʎ are made with the FRONT of the tongue under the front of the palate (`place: "prepalatal"`), the tip tucked down behind the
lower teeth (`tuck: [x, y]`: the most the tip may be forward / up while the body makes the sound). At the top of the dome with the tip
riding along, j's F2 reached 1815; now 2160.

**ɲ** (ñ, ň, gn) took three tries, and the user's ear each time. (1) A body closure at the top of the palate: a fronted ŋ. (2) The same
further forward, with a slow release and the velum shut early so that the glide out is oral -- right on paper (F2 2500 -> 1430 over
100 ms in the rendered sound), heard as "a cut-off n, no nj": a closure made with the tongue's body is not taken for an n-sound's place,
and the early velum cut the murmur short. (3) What it is in the mouth of a Spanish or Czech speaker: an **n made with the blade**
(`organ: "tip"`, postalveolar) **with the body up as for an i** (`raise`), **let go into a j** -- `OFFGLIDES` in phonemes.js puts a short
j after it whenever a vowel follows (`timing.offglide` x its length). In the sound: a rising, nasal on-glide, the murmur of an n,
then 2250 -> 1990 -> 1710 -> 1570 -> 1430 Hz through a shut nose. Typing `anja` gives nearly the same, which is the point.
Tools: `ref/tract25.html` (the mouth: formants and narrowest place through a word), `ref/tract26.html` (the SOUND: strongest peak in
900-3400 Hz every 15 ms) -- judge from the second.

## Nasals take the place of what follows

`timing.assimilate`: m or n before f / v becomes the labiodental nasal `ɱ` ("comfort", "invite", "fünf"; a consonant of its own in
`consonants`, made where this mouth makes f and v), n before p b m becomes m ("ten pigs"), n before k g becomes ŋ ("in car"). Each
happens when the speaker's effort is below its number -- the first nearly always, the others in ordinary-to-lazy speech, and across
a word boundary only for a somewhat lazier speaker (`acrossWords`). Nobody writes ɱ: the dictionary keeps m and n.
A closure let go into a narrow sound of the same organ (now also a nasal's: m-f) releases with a tap's speed, or it lies over the
fricative (the f of "comfort" was shut at its middle).

## One person's head

Besides its size (`oral`, `pharynx`) a voice's head has a SHAPE, all x the reference head (`synth.js reshape`, sliders in the lab):
`palateHeight` (the dome above the teeth's level), `pharynxDepth` (how far back the throat's wall stands), `lipWidth`,
`lipThickness` (the lip tube at rest), `tongueSize` (keep within a few %), `noseSize`; with `ring` and `larynxHeight` that is the
anatomy a person brings. Walls, the velum's place and the consonants' places move together.

The postures were learned in the reference head. Taken as they are into another shape they break (a palate 15 % lower shut every
/i/, a throat 20 % narrower every /u/), so they are CARRIED OVER (`anatomy.js adaptPosture`): a tongue aims at a gap, not at a place --
a high vowel's body follows the palate (all the way down, 65 % of the way up: a raised palate rises less toward the teeth), a back
vowel's body follows the throat wall. What is left is that head's colour, e.g. palate x1.2: /i/ 301/1902/2901 instead of 280/2246/2716.
For an exact match there is **Re-fit for this voice** in the lab: each vowel's target is what this head's SIZE alone gives with the
reference posture, the inversion starts from the carried-over posture, and the result is stored as `voices.<name>.postures` (used
instead of the shared ones; in the config under Raw JSON). Measured on palate 1.2 + throat 1.3: /i/ 374/1702 -> 283/2288 (target
280/2246), /u/ 289/1043 -> 312/870; F3 stays the head's own. Under a higher palate the tongue body may go as much higher.
Check: `scratchpad/ref/tract24.html`.

## What a mouth can do (`limits`)

The last thing that happens to every track: no organ moves faster than its `speed` or changes speed quicker than its `accel`
(`planner.js LIMITS`, x the voice's `agility`), following what was asked as closely as that allows and braking in time, so it never
overshoots. The numbers sit at the edge of what people do (body 45 cm/s, tip 90/130, jaw 160 deg/s = 25 cm/s at the teeth, lips
80, pitch 85 semitones/s up and 110 down), not at the typical: a tap and a stop's release pass untouched. The plan should never
ask for more -- where it does, that is a bug in the plan, and the limiter both refuses it (a slur, not a click) and REPORTS it:
`tracks.limited` (track, time, how far behind), `tracks.asked` (the most that was asked of each organ), red bands and a line of
text in the lab. The tip is limited in ABSOLUTE position (it rides on the body and makes up for a body that is held back; limited
relative to it, the s of "thanks" shut: "thankts").

**Taking the time** (`limits.slowDown`, `maxStretch`, `passes`). Where an organ is asked for more speed than it has, the sentence is
planned again with the consonant gestures there made slower by (speed asked / speed allowed) -- a gesture's speed is its time
constant's doing, not its sound's length, and a slower gesture starts earlier, so it still arrives on time -- and the sounds around
them, vowels included, are given `slowDown` of that extra time x the voice's effort. (Lengthening the sounds alone changed nothing:
measured.) On the test sentences 17 gestures are slowed 1.2-1.6x and nothing is left for the limiter to hold back; the lab lists what
was slowed. `slowDown: 0` and `passes: 0` give back the plain limiter (slur, don't slow).

Switching it on found three discontinuities at once, all now fixed at the source: a consonant demand that was already met dropped
out of the weighted sum (two consonants with different jaw heights: the jaw jumped a degree in a frame, 500 deg/s); the body "lent
the tip a hand" in steps of 1.8 mm (140 cm/s) and through a gate at 5%; an r's posture let go with a 9 ms time constant. What is
still reported is real: the body is asked for up to 70 cm/s into and out of velars and after r (`gesture.tau.body`, `ahead`).
Check: `scratchpad/ref/tract20.html`.

## Not there yet

Sibilant grooves and the sublingual cavity (ʃ vs ʂ), a tongue that can bunch (ɹ, ɜ), piriform sinuses and the
subglottal system, real trills (this one is kinematic), durations and intonation beyond the basics — the planner's
prosody is deliberately simple and entirely in `timing` / `prosody`.
