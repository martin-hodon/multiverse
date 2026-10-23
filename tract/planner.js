// FROM SOUNDS TO MOVEMENT. A sentence is a string of phones; a mouth is a handful of heavy things that cannot jump.
// The plan is made in two layers, the way speech is (Ohman 1966):
//   the VOWELS are one slow gesture of the whole tract from posture to posture, running on underneath everything;
//   each CONSONANT is a quick gesture of ONE organ laid over that, taking only what it needs (its organ, and perhaps
//   the jaw, the lips' rounding, the velum) for as long as it needs it, solved against whatever posture the vowels
//   have the mouth in at that moment -- so a /k/ is made further forward before /i/ than before /u/, by itself.
// The folds have their own layer: together for voice, drawn apart and back for a voiceless sound, and WHEN they come
// back relative to a stop's release is aspiration. Lung pressure and pitch are the last two tracks.
//   Every track is then passed through a critically damped second-order lag with that organ's own time constant:
// the tip is quick, the body and the jaw are slow. A short vowel between two consonants therefore never reaches its
// posture -- undershoot, without a rule for it.
// No DOM. Output: tracks at TIMING.control Hz.
import { ARTICULATORS, ANATOMY, areaFunction, neutral, clampArt, solveTip, solveBody, solveLips, adaptPosture, setJaw } from "./anatomy.js";
import { CONSONANTS, LANGUAGES, tokenize } from "./phonemes.js";

export const TIMING = {
  control: 400,                                  // Hz
  // (a language may have its own: phonemes.js LANGUAGES.<lang>.vowel overrides any of these, and `lax`)
  // beforeVoiceless: x a vowel right before a voiceless consonant in its word ("not", "cat", "leaf" are clipped; "nod", "cab", "leave" are not)
  vowel: { ms: 110, laxMs: 82, long: 1.45, stressed: 1.2, final: 1.3, diphthong: 1.45, unstressed: .85, beforeVoiceless: .9, glideAt: .45 },   // (glideAt: the share of a diphthong spent on its first posture before it sets off for the second)
  lax: "ɪʊəɐɛʌœʏɔ",
  lastConsonant: 1.3,                            // x: the final consonant of an utterance is held longer
  cluster: .82,                                  // x: a consonant next to another consonant
  leadMs: 110, tailMs: 230, pauseMs: 230, restAfterMs: 130,   // (restAfterMs: how long after the last sound the mouth starts back to rest; the tail must outlast that)
  // (carry: a helping movement -- rounding, the body lending the tip a hand -- lets go this much quicker than it came: the next
  // vowel is already pulling the other way)
  // A GESTURE IS A DRIVEN, DAMPED MOVEMENT, not a fade: it is switched on a little before its sound and off at its end, and
  // the organ answers like a critically damped spring with its own time constant (ms) -- a fast start, a slow arrival, and
  // a target just BEYOND the contact, so that a closure is made at full speed and held with pressure. `ahead` x tau is how
  // early it is switched on (so that it arrives on time): a slow organ therefore starts during the sound before, which is
  // anticipation, and clears during the sound after, which is carry-over -- each organ by its own clock, so the mouth's path
  // from sound to sound is a curve, not a straight line.
  // The VOWEL layer has the same thing as `vowelAhead` (x the tongue body's own time constant: how far ahead the slow whole-tract
  // gesture is read, so that it, lagged, still arrives on time). HOW FAR IN ADVANCE THE MOUTH MOVES ALTOGETHER is one number of the
  // speaker's: `anticipation` (PERSON) x both of these, and with it where in the consonants between two vowels the vowel gesture turns
  // to the next (`vowelSwitch` to that power). 0: nothing moves before its own sound -- gestures then arrive late, and what the mouth
  // cannot do in the time it is given is taken up by LIMITS below, which lengthens those sounds rather than letting them be slurred.
  gesture: { ahead: 3.0, vowelAhead: 1.6, carry: .55, tau: { lips: 13, tip: 11, body: 17, jaw: 27, round: 26, velum: 26, lateral: 10, help: 22, tap: 5 }, vowelShare: .3, velumShutTau: 11, velumLeadMs: 20, stopRelease: 21, bodyStopRelease: 24, lipStopRelease: 11,   // (lips have a centimetre to go, not three: slow, they never open for the schwa of "cup of" and it comes out as "u")   // (a release is the organ LEAVING at 20-50 cm/s, not vanishing: at 9ms the tip left a /t/ at 120 cm/s and the mouth opened 1cm2 in 5ms -- a gust, heard as a thump)
             lateralLeadMs: 25, lateralLagMs: 35, lateralShut: .45,   // (the tongue's sides are down BEFORE an l's tip closes and until after it has gone -- or the l is a stop for a moment, and clicks)
             // (...but when a CLOSURE follows, the sides come up with it and quickly: x this on the way out. Left to fade at their own
             //  rate they held the mouth open through 70ms of the /d/ of "old dog" -- the tip was on the ridge and the air still went
             //  round it, hissing, and the closure was finally made by the leak dying rather than by the tongue. Then it burst.)
             finalHoldMs: 140, finalFricativeHoldMs: 110, finalStopHoldMs: 10, finalStopPressure: .85 },   // a final voiceless stop is NOT held into the silence (its burst would then come alone, long after the word, as a pop): it lets go on time, on a breath that is already falling   // the last sound before silence is HELD until the voice has gone: released into a running voice it grows a vowel ("man-uh")
  // a trill by the AIR (acoustics.flap): the tip is held at this opening (cm2, what it has when the air is not moving it) and the
  // tube beats it. physical: false is the old kinematic trill (the planner opens and shuts the tip `trill` times a second)
  trill: { physical: true, area: .2 },
  // A NASAL TAKES THE PLACE OF WHAT FOLLOWS IT: n (and m) before f or v is the labiodental nasal, n before p b m is m, n before k g is ng.
  // Each happens when the speaker's effort is BELOW the number (the first nearly always, the others in ordinary to lazy speech);
  // across a word boundary `acrossWords` is added to the number (it takes a lazier speaker). 0 switches one off.
  assimilate: { beforeLabiodental: 1.45, beforeLabial: 1.0, beforeVelar: .9, acrossWords: -.15 },
  offglide: 1.1,                                  // x: the length of a glide a consonant is let go into (phonemes.js OFFGLIDES: the j of ñ)
  byMovement: { gain: 1.2, least: .8, most: 1.5, leadMs: 25 },   // gain: ms given per ms of movement (at the organs' full speed) above the average; least / most: x a sound's time may become; leadMs: a sound's movement starts this long before it
  twin: 1.5,                                      // x: the same consonant twice in a row (man now) is ONE gesture, this much longer
  // the vowel gesture's own lag per organ (ms): the jaw is the slowest thing in the mouth, the tip the quickest
  tauMs: { jaw: 34, bodyX: 30, bodyY: 25, tipX: 15, tipY: 15, lipH: 18, lipP: 30, velum: 22, larynx: 60, lateral: 14, rest: 9, pressure: 30, f0: 22 },
  vowelSwitch: .35,                              // where in the consonants between two vowels the vowel gesture turns to the next (0 = at once, 1 = at the end)
  // THE ROOM A VOWEL NEEDS. Between two constrictions a vowel is only a vowel if the one before it has let go of the organ and the one
  // after it has not yet taken hold: `ahead` time constants of the first's release, plus the lead of the second (see gesture.ahead).
  // x: how much of that a vowel is guaranteed (0 switches it off); tight: the opening (cm2) below which a consonant shuts a vowel in.
  vowelRoom: { x: 1, tight: .3 },
};
export const PROSODY = {
  pressure: 8, stressPressure: 1.2,                        // cm H2O; added on a stressed vowel
  // THE BREATH IS LET GO IN ADVANCE: from the middle of the last vowel on it falls, to x finalPressure by the end of the last sound, and
  // is gone finalPressureMs after it. (Held at full to the very end, the voice outlasted the last sound by 120ms and the mouth had to
  // stand still that long; nobody speaks like that.)
  finalPressure: .5, finalPressureMs: 60, finalBurstMs: 95,   // (finalBurstMs: after a final voiceless stop the breath lasts this much longer -- until it has burst)
  declination: -2.4, accent: 2.8, accentLeadMs: 30, finalFall: -2.6, floor: -4.5, questionRise: 6.5, exclaim: 1.5, finalMs: 260,   // semitones
  // the folds' rest opening (cm2): voiced, a voiced fricative, a voiceless fricative, a voiceless stop, breathing
  // voicedChink: the gap at the BACK of the glottis during a voiced fricative (glottis.js: it does not swing with the folds, so the
  // air never stops and the hiss is there all through the sound, not only in the devoiced tail at the end of the word)
  rest: { voicedFricative: .05, fricative: .18, stop: .13, breathing: .32, voicedChink: .04 },   // (stop: wider and the release is a gust of air -- a thump louder than the vowel)
  breathAfterStopMs: 22,                          // an h's folds start to part this long after a VOICED stop before it has ended (parting during
                                                  // one, they make its release a gust through an open glottis: "and his" had a tick for a d).
                                                  // After a voiceless stop there is nothing to protect -- the folds are already apart for it --
                                                  // and waiting only left the h no time to open: its glottis reached .06 cm2 where it wanted .2,
                                                  // and what came out was not breath but a squeezed hiss ("ist heute").
  finalDevoice: .45,                              // x rest.fricative: how far the folds part through a voiced fricative that ends the utterance (0: it keeps its voice).
                                                  // (At .75 the folds ended as far apart as for an s: the flow ROSE as they opened, and the loudest hiss of the whole
                                                  //  word came after the voice had gone -- a separate s let go at the end of "is". The voice still goes; the breath goes with it.)
  stopOpenBy: .55,                                // a voiceless stop's folds are fully apart by this share of their opening time, then wait for the release: parting
                                                  // all the way up to it they let the voice run 50ms into the closure ("and pig" was "and big")
  // *word*: a bigger accent, more breath, a longer vowel -- and what follows it in the phrase is said with less (post-focus)
  emphasis: { accent: 2.1, pressure: 2.2, vowel: 1.3, consonant: 1.12, after: .45 },
  // EFFORT (the voice's, x a (clear: ...) or (lazy: ...) in the text, x `emphasis` on an emphasised word), per unit away from 1:
  // vowel / unstressedVowel: how much of the way from rest to its posture a vowel goes; settle: how much slower the mouth settles;
  // open: how much wider a fricative or approximant is left; jaw: how much of a consonant's jaw raising is skipped;
  // unstressedMs: unstressed vowels' length; accent, pressure: the accents' size and the breath
  effort: { vowel: .35, unstressedVowel: .6, settle: .3, open: .5, jaw: .5, unstressedMs: .3, accent: .4, pressure: .12, emphasis: 1.2 },
  // what `variability` 1 does (each a share either way, drawn per accent / vowel / phrase): accent size, the chance an accent is nearly
  // skipped and what is left of it, accent timing (ms), vowel length, a phrase's pace, a phrase's pitch level (semitones), the final fall's depth
  vary: { accent: .7, skip: .3, skipTo: .35, accentMs: 30, vowel: .2, pace: .12, level: 1.5, finalFall: .35 },
  // a PHRASE is what stands between two pauses. reset: how much of the declination starts again with each phrase;
  // continuationRise (semitones over continuationMs): "there is more to come", at the end of every phrase but the last;
  // finalVowel / finalConsonant: x the last syllable of such a phrase; downstep: each accent in a phrase x this, phraseStep: each
  // phrase's accents x this; rhythm: each further unstressed syllable in a row shortens them all by this share;
  // tempoArc: a phrase starts and ends this much slower than its middle
  phrase: { reset: .6, continuationRise: 2.2, continuationMs: 200, finalVowel: 1.18, finalConsonant: 1.15, downstep: .86, phraseStep: .94, rhythm: .07, tempoArc: .05 },
  // (name: ...) in the text. tempo x, pitch in semitones, pressure x, range x, rest: added to the folds' opening (breathier)
  styles: { slow: { tempo: .78 }, fast: { tempo: 1.25 }, high: { pitch: 3 }, low: { pitch: -3 }, loud: { pressure: 1.3, range: 1.25 }, soft: { pressure: .72, range: .8, rest: .02 }, clear: { effort: 1.3, tempo: .92 }, lazy: { effort: .65, tempo: 1.08 }, smile: { smile: .8 }, creaky: { creak: .8 },
            aside: { pitch: -2, tempo: 1.12, pressure: .88, range: .7 } },
  smile: { lipSpread: .7, larynx: .35, pitch: 1 },   // what a full smile adds: lip spread, cm of larynx, semitones
  fry: { ms: 320 },                                 // fry sets in over the last `ms` of a falling sentence
  nasalityPort: .3,                                 // the velum's opening (0..1) at nasality 1
  staccatoGapMs: 70,                              // the silence between words at legato 0 (none from .5 up)
  aspirationMs: 58,                               // how long after a release the folds of an aspirated stop take to come back
  aspirateUnstressed: .35,                        // x the aspiration of a stop let go into an UNSTRESSED vowel: English aspirates what begins a stressed
                                                  // syllable ("to" in "today"), not what runs into a weak one -- fully aspirated, the t of "what" held the
                                                  // folds apart through the whole "it" of "what it is" and the vowel was whispered away
  tones: { 1: [5, 5, 5], 2: [3, 3.3, 5], 3: [2, 1, 2.2], 4: [5, 3.6, 1], 5: [3, 2.6, 2.2] }, toneSpan: 9,   // Chao levels; semitones across 1..5
};

// WHAT A MOUTH CAN DO. The last thing that happens to every track: no organ moves faster than `speed` or changes its speed quicker
// than `accel` (per second; cm, degrees for the jaw, 0..1 for velum and lateral, cm2 for the folds' opening, cm H2O for the lungs,
// semitones for the pitch -- which rises slower than it falls). The plan above should never ask for more: where it does, that is
// a bug in the plan, and the limiter both refuses it (a slurred sound instead of a click) and SAYS SO -- tracks.limited lists every
// place, the lab draws them red. The numbers sit at the edge of what people do (a tap, a stop's release), not at the typical.
export const LIMITS = {
  // TAKING THE TIME. How fast a gesture moves is its TIME CONSTANT's doing, not its sound's length: an organ asked to cross a long way in
  // a gesture's usual time is asked for too much speed. Where that happens the sentence is planned again (up to `passes` times) with the
  // gestures of the consonants there made SLOWER -- by the speed asked / the speed allowed, at most maxStretch; a slower gesture also
  // starts earlier, so it still arrives on time -- and the sounds around them given `slowDown` of that extra time (x the voice's effort: a
  // careful speaker takes the time, a lazy one slurs). What is still held back after that is slurred by the limiter, and reported.
  slowDown: .7, maxStretch: 1.6, passes: 2,
  on: true, tolerance: .06,     // tolerance: a track counts as held back where it is this share of its range away from what was asked
  jaw: { speed: 160, accel: 16000, range: 24 },                // (1 degree is ~1.6mm at the teeth: 25 cm/s)
  bodyX: { speed: 45, accel: 5000, range: 3 }, bodyY: { speed: 45, accel: 5000, range: 3.3 },
  tipX: { speed: 90, accel: 14000, range: 4 }, tipY: { speed: 130, accel: 20000, range: 4 },
  lipH: { speed: 80, accel: 12000, range: 2.2 }, lipP: { speed: 35, accel: 4000, range: 1.4 },
  velum: { speed: 25, accel: 3000, range: 1 }, larynx: { speed: 12, accel: 800, range: 2 }, lateral: { speed: 45, accel: 8000, range: 1 },
  rest: { speed: 7, accel: 1200, range: .3 }, pressure: { speed: 190, accel: 12000, range: 8 },
  f0: { speed: 110, speedUp: 85, accel: 6000, range: 12 },
};
// follow `x` as closely as speed and acceleration allow, braking in time (no overshoot); returns the most that was asked for
function follow(x, dt, lim, agility, log) {
  const n = x.length, h = dt / 1000, vDown = lim.speed * agility, vUp = (lim.speedUp ?? lim.speed) * agility, aMax = lim.accel * agility, val = (i) => log ? 12 * Math.log2(Math.max(1, x[i])) : x[i];
  const y = new Float32Array(n), wvs = new Float32Array(n); let asked = { speed: 0, accel: 0, at: 0 }, pos = val(0), v = 0, pv = 0; y[0] = x[0];
  for (let i = 1; i < n; i++) { const want = val(i), wv = (want - val(i - 1)) / h; wvs[i] = wv; if (Math.abs(wv) > asked.speed) { asked.speed = Math.abs(wv); asked.at = i * dt; } asked.accel = Math.max(asked.accel, Math.abs(wv - pv) / h); pv = wv;
    const e = want - pos; let nv = e / h;                                       // the speed that would get there this frame
    const brake = Math.sqrt(2 * aMax * Math.abs(e)) + Math.abs(wv);              // ...but never more than can still be stopped at the target (which may itself be moving)
    nv = Math.max(-Math.min(vDown, brake), Math.min(Math.min(vUp, brake), nv));
    nv = Math.max(v - aMax * h, Math.min(v + aMax * h, nv)); v = nv; pos += v * h; y[i] = log ? Math.pow(2, pos / 12) : pos; }
  return { y, asked, wvs, vMax: Math.min(vDown, vUp) };
}
export function limitTracks(tracks, limits = LIMITS, agility = 1) {
  const dt = 1000 / tracks.control, out = [], asked = {}, before = {};      // (before: each track as it was asked for)
  for (const [k, lim] of Object.entries(limits)) { if (!lim || typeof lim !== "object" || !tracks[k]) continue;
    // (the tip RIDES ON the body: what has a speed is where the tip is, not where it is relative to the body -- and when the body is
    // held back the tip makes up for it. Limited relative to a body that was itself limited, the tip of the s in "thanks" sat 3mm
    // too high while the body was still coming down from the k, and shut: "thankts")
    const carrier = k === "tipX" ? "bodyX" : k === "tipY" ? "bodyY" : null, askedCarrier = carrier && before[carrier];
    if (carrier) { const abs = new Float32Array(tracks.n); for (let i = 0; i < tracks.n; i++) abs[i] = tracks[k][i] + askedCarrier[i]; before[k] = tracks[k]; tracks[k] = abs; }
    const log = k === "f0", r = follow(tracks[k], dt, lim, agility, log); asked[k] = r.asked;
    if (!limits.on) { if (carrier) tracks[k] = before[k]; continue; }
    const tol = limits.tolerance * lim.range, diff = (i) => log ? Math.abs(12 * Math.log2(Math.max(1, tracks[k][i]) / Math.max(1, r.y[i]))) : Math.abs(tracks[k][i] - r.y[i]);
    for (let i = 0, from = -1, worst = 0; i <= tracks.n; i++) { const d = i < tracks.n ? diff(i) : 0; if (d > tol) { if (from < 0) from = i; worst = Math.max(worst, d); } else if (from >= 0) { let sp = 0; for (let j = Math.max(1, from - 12); j < i; j++) sp = Math.max(sp, Math.abs(r.wvs[j])); out.push({ track: k, t0: from * dt, t1: i * dt, by: worst, of: lim.range, over: sp / r.vMax }); from = -1; worst = 0; } }
    if (carrier) { const rel = before[k]; for (let i = 0; i < tracks.n; i++) rel[i] = r.y[i] - tracks[carrier][i]; tracks[k] = rel; } else { before[k] = Float32Array.from(tracks[k]); tracks[k].set(r.y); } }
  tracks.asked = asked; tracks.limited = out; return tracks;
}

// SOUNDS NOBODY MAKES. The limiter above says what a mouth can DO; this says what a mouth would never be caught doing. A plan can
// put the tract in a shape that is perfectly possible and never used -- a vowel with the tongue so near the palate that the air
// whistles and hisses through it instead of ringing ("bad radio"), a voice going on with no breath left behind it (a creak nobody
// asked for), the nose opening while the mouth is holding pressure (a gurgle, air let out of the wrong door). Each rule here is one
// such thing, checked frame by frame on the tract the plan really produced, mended with the SMALLEST movement that will do, and
// written down (tracks.odd, red in the lab): a rule that has to fire often is a bug somewhere earlier, not a fix.
//   The mending is smoothed before it is applied and the whole plan goes through the limiter again, so nothing is mended into a jump.
export const SANITY = {
  on: true,
  open: .22,          // cm2: the narrowest the mouth may be while a vowel or an approximant is sounding. Below this the air is a jet:
                      // the sound is a buzz with a hiss on it and no vowel in it. (A real /i/ is about .25 at its tightest.)
  openBy: 1.1,        // cm (degrees for the jaw): as far as an organ may be moved out of the way to make that room, and no further
  voicePressure: 3.2, // cm H2O: under this the folds swing badly and the voice creaks. A vowel in the middle of a sentence is given
                      // at least this much breath; the last one is not -- a sentence is meant to run out of air.
  nasalPressure: 2.2, // cm H2O: the velum may not stand open while the mouth is shut and holding more than this
  nasalPort: .12,     // ...and this is as far as it may stand open there
  holdMs: 25,         // nothing under this is mended: a breath still coming in at the first sound, a velum on its way down out of a
                      // nasal -- these are moments of a mouth working, not sounds. Only what LASTS is a sound nobody makes.
};

// WHO IS SPEAKING, as a way of speaking: every voice (synth.js VOICES) carries these, and what a voice leaves out is taken
// from here. They scale what PROSODY and TIMING describe; they are what makes two people with the same head sound different.
export const PERSON = {
  range: 1,              // x every movement of the pitch: .5 a flat speaker, 1.5 a lively one
  register: 0,           // semitones: where in the voice the speech sits (above / below the voice's f0)
  liveliness: 1,         // x the accents alone (how much a stressed word is marked), leaving fall and declination as they are
  finalLengthening: 1,   // x how much the end of a phrase is drawn out (0: not at all)
  pauseScale: 1,         // x every pause
  legato: .5,            // 0 staccato: late, quick gestures and a gap between words ... 1: early, overlapping gestures, a gliding pitch
  anticipation: 1,       // x how far in advance the mouth moves for what is coming (timing.gesture.ahead and vowelAhead, and how early the
                         // vowel gesture turns to the next vowel): 0 nothing before its own sound, 1 as configured, 2 a mouth that runs ahead
                         // of itself. It does not touch the leads that keep a sound from breaking (an l's sides, a velum before an obstruent).
  vibratoHz: 5.5, vibratoDepth: 0, vibratoDelayMs: 220,   // semitones each way, setting in this long after a vowel has begun
  flutter: 1, jitter: 1, // x the folds' slow wander and their cycle-to-cycle irregularity (glottis)
  // THE HEAD'S OWN SHAPE (synth.js reshape; all x the reference head): see there
  palateHeight: 1, pharynxDepth: 1, lipWidth: 1, lipThickness: 1, tongueSize: 1, noseSize: 1,
  agility: 1,            // x every limit of LIMITS: how quick this mouth is
  // the FOLDS of this speaker (with `rest`, the opening they voice at: below 0 pressed, 0 modal, above breathy): closure -- how sharply they
  // shut: above 1 bright and pressed, below 1 warm and soft; swing -- how far they open: above 1 "flow" voice, loud on little effort
  closure: 1, swing: 1,
  breathNoise: 1,        // x the hiss of air through the folds (with `rest`, the voice's breathiness: rest lets the air through, this is how much it is heard)
  ring: 1,               // the tube over the folds this much NARROWER than the reference: the voice carries (energy gathers near 3 kHz)
  fry: 0,                // 0..1: how much the end of a falling sentence drops into creak
  creakiness: 0,         // 0..1: creak all the way through
  // HABITS OF THE MOUTH, laid over every sound: nasality (0..1, the velum never quite shut -- except under sounds that hold pressure),
  // lipSpread (-.5 drawn in .. 1 a broad smile's lips), larynxHeight (cm: up is brighter and younger, down darker and warmer),
  // jawSetting (degrees added to every vowel: below 0 clenched), smile (0..1: spread lips, a raised larynx, a little more pitch)
  nasality: 0, lipSpread: 0, larynxHeight: 0, jawSetting: 0, smile: 0,
  // HOW FREELY THE JAW MOVES (x how far every vowel takes it from this speaker's own jaw setting): 1 as the postures were fitted,
  // 0 a jaw that never leaves its rest -- someone speaking through nearly closed teeth. The TONGUE is put back where the sound needs
  // it (anatomy.setJaw: it rides the jaw, so a jaw held back would carry every vowel with it), which is what people really do; the
  // lips are not, because they are on the chin (anatomy.lips.jawShare), so a held jaw is also a smaller mouth. Above 1 the jaw works
  // harder than the fit asked for. Consonants look after themselves: their constrictions are solved against the posture of the moment.
  jawFreedom: 1,
  // WHOSE R (consonants.ɹ.shapes). rShape: 0 bunched -- the tongue root back in the pharynx, the blade flat (F3 1708 Hz); 1 retroflex
  // -- the tip curled right up, the room under it lengthening the front cavity (F3 1555, and F4/F5 down at 3216/3779, which is what
  // really tells them apart). The two sound alike in F1-F3 and differ above, as they do in people. rStrength: how far from a weak,
  // hardly rhotic r (0: F3 2270) this mouth goes (1: all the way). Any consonant with `shapes` + `shapeBy` works this way.
  rShape: 0, rStrength: 1,
  // VARIABILITY (0..1): nobody says two accents, two syllables or two phrases alike. With it, each accent has its own size (some are nearly
  // skipped) and timing, each vowel its own length, each phrase its own pace and pitch level, the final fall its own depth -- drawn from the
  // text itself, so the same sentence always comes out the same. What each amounts to at 1: prosody.vary. 0: every accent alike (monotonous).
  variability: 0,
  // TIME BY MOVEMENT (0..1): how long a sound gets goes with how much the mouth has to MOVE for it. The sentence is planned once, the way
  // each organ travels during every sound is measured against how fast that organ can go (limits) -- the share of the sound's time the
  // movement needs -- and the time is then dealt out again: sounds with long or many-organ movements get more, easy ones less, the
  // sentence as a whole keeps its length. 0: the table's durations as they are. (timing.byMovement: how far it may go)
  byMovement: 0,
  effort: 1,             // how far the speaker bothers to go: below 1 lazy (vowels stop short of their postures, constrictions are looser, the jaw
                         // moves less, the mouth settles slower, unstressed syllables shrink), above 1 careful. What each of these amounts to: prosody.effort
};

const smoothstep = (u) => { u = Math.max(0, Math.min(1, u)); return u * u * (3 - 2 * u); };

export function plan(ipa, { lang = "en", postures, voice, mark = ".", timing = TIMING, prosody = PROSODY, limits = LIMITS, sanity = SANITY, anatomy, stretch = null, pass = 0, pace = null } = {}) {
  const postures0 = postures;
  // (the shared postures are taken into this head's shape; a voice that has learned its vowels in its own head has them as they are)
  if (anatomy?.shape) postures = Object.fromEntries(Object.entries(postures).map(([k, a]) => [k, adaptPosture(a, anatomy)]));
  if (voice?.postures) postures = { ...postures, ...voice.postures };
  const phones = tokenize(ipa, postures, lang).filter((p, i, a) => !(p.kind === "gap" && (i === 0 || a[i - 1].kind === "gap")));
  const L = LANGUAGES[lang] ?? LANGUAGES.en, T = timing, V = { ...T.vowel, lax: T.lax, ...(L.vowel ?? {}) }, who = { ...PERSON, ...voice }, lg = Math.max(0, Math.min(1, who.legato)), ant = Math.max(0, who.anticipation ?? 1), Ph = prosody.phrase, E = prosody.emphasis;
  const styleOf = (p, key, combine, start) => (p.styles ?? []).reduce((a, name) => { const v = prosody.styles[name]?.[key]; return v === undefined ? a : combine(a, v); }, start);
  // (a consonant's opening is given for the reference head: a smaller head makes it smaller, as its folds' opening is -- left at the
  // adult's size, a child's /s/ was wider than its glottis, the pressure fell at the folds and there was no hiss: -30 dB)
  const headArea = anatomy?.scale ? Math.sqrt(anatomy.scale.oral * anatomy.scale.pharynx) : 1;      // (with the head's LENGTH scale: a channel as small as the cross-section says lets no air through -- friction goes with 1/area3)
  // (the draws come from the text: the same sentence is always said the same way)
  let seed = 2166136261; for (const ch of ipa) seed = Math.imul(seed ^ ch.codePointAt(0), 16777619) >>> 0; seed ||= 1;
  const rnd = () => { seed ^= seed << 13; seed >>>= 0; seed ^= seed >>> 17; seed ^= seed << 5; seed >>>= 0; return seed / 4294967296 * 2 - 1; };   // -1..1
  const vy = Math.max(0, Math.min(1, who.variability ?? 0)), Vr = prosody.vary;
  const Ef = prosody.effort, effortOf = (p) => Math.max(.4, Math.min(1.6, (who.effort ?? 1) * styleOf(p, "effort", (a, v) => a * v, 1) * (p.emph ? Ef.emphasis : 1)));
  const vowelsOf = new Map(); for (const p of phones) if (p.kind === "vowel") { const w = vowelsOf.get(p.word) ?? []; w.push(p); vowelsOf.set(p.word, w); }
  // an emphasised word is stressed, whatever the dictionary says of it ("*the* dog")
  for (const w of vowelsOf.values()) if (w.some((v) => v.emph) && !w.some((v) => v.stress)) w.find((v) => v.emph).stress = true;
  // FIXED STRESS: a language that always stresses the same syllable (LANGUAGES.<lang>.stress) needs no mark in the IPA -- a word typed
  // without one is stressed where the language puts it. Without this a Slovak sentence is one unbroken row of unstressed syllables, and
  // such a row is compressed (phrase.rhythm): "to je tak ako keby" lost a quarter of every vowel and the a and o of "ako" all but vanished.
  if (L.stress) for (const w of vowelsOf.values()) if (w.length && !w.some((v) => v.stress)) w[L.stress < 0 ? Math.min(w.length - 1, -L.stress - 1) : Math.max(0, w.length - L.stress)].stress = true;
  // AMERICAN FLAPPING (LANGUAGES.<lang>.flap): a t or d between two vowels, the second unstressed, is one tap of the tip -- "water",
  // "what it is". Said as two full stops, the tip has to close, let go and close again over a 47 ms vowel and never gets out of the
  // way: the vowel is a buzz through a shut mouth. A tap is a single quick movement (gesture.tau.tap), and the vowels keep their own time.
  if (L.flap) phones.forEach((p, i) => { if (p.kind !== "consonant" || (p.sym !== "t" && p.sym !== "d") || p.long || p.affricate) return;
    const near = (k, d) => { while (phones[k]?.kind === "gap") k += d; return phones[k]; };
    const before = near(i - 1, -1), after = near(i + 1, 1);
    if (before?.kind !== "vowel" && before?.sym !== "ɹ") return;
    if (after?.kind !== "vowel" || after.stress) return;
    if (effortOf(p) < L.flap) { p.was = p.sym; p.sym = "ɾ"; } });
  // place assimilation of nasals (TIMING.assimilate)
  { const As = T.assimilate; if (As) phones.forEach((p, i) => { if (p.kind !== "consonant" || (p.sym !== "n" && p.sym !== "m") || p.long) return;
      let k = i + 1, across = false; while (phones[k]?.kind === "gap") { across = true; k++; } const q = phones[k]; if (q?.kind !== "consonant") return;
      const to = "fv".includes(q.sym) ? ["ɱ", As.beforeLabiodental] : p.sym === "n" && "pbm".includes(q.sym) ? ["m", As.beforeLabial] : p.sym === "n" && "kg".includes(q.sym) ? ["ŋ", As.beforeVelar] : null;
      if (to && to[1] > 0 && effortOf(p) < to[1] + (across ? As.acrossWords : 0)) { p.was = p.sym; p.sym = to[0]; } }); }
  // phrases: what stands between two pauses
  const phrases = [[]]; for (const p of phones) { if (p.kind === "pause") phrases.push([]); else if (p.kind !== "gap") phrases[phrases.length - 1].push(p); }
  for (let k = phrases.length - 1; k >= 0; k--) if (!phrases[k].length) phrases.splice(k, 1);
  phrases.forEach((ph, k) => { const lastV = [...ph].reverse().find((p) => p.kind === "vowel"), iv = ph.indexOf(lastV); let run = [];
    ph.forEach((p, i) => { p.phrase = k; p.at = ph.length > 1 ? i / (ph.length - 1) : .5; if (k < phrases.length - 1 && lastV) { if (p === lastV) p.phraseFinal = Ph.finalVowel; else if (i > iv && p.kind === "consonant") p.phraseFinal = Ph.finalConsonant; }
      if (p.kind === "vowel") { if (p.stress) { for (const q of run) q.crowd = run.length; run = []; } else run.push(p); } });
    for (const q of run) q.crowd = run.length; });
  const fin = (x) => 1 + (x - 1) * who.finalLengthening, paceOf = [], levelOf = [];
  for (let i = 0; i < phones.length; i++) { if (phones[i].kind !== "consonant") continue; let j = i + 1; while (phones[j]?.kind === "gap") j++;
    if (phones[j]?.kind === "consonant" && phones[j].sym === phones[i].sym && !phones[i].affricate && !phones[j].affricate) { phones[i].twin = true; phones.splice(j, 1); } }
  const G = { ...T.gesture, ahead: T.gesture.ahead * (.7 + .6 * lg) * ant, carry: Math.min(1, T.gesture.carry * (.8 + .4 * lg)) };
  // a closure (a stop's, a nasal's: "comfort") let go INTO a narrow sound of the same organ ("and soup", "it's") opens no further than that sound: its release is that sound's
  // beginning, as in an affricate. Let go slowly, as into a vowel, its closure lay over the s for 60ms and the s never opened (.01 cm2)
  const intoNarrow = (p) => { let k = phones.indexOf(p) + 1; while (phones[k]?.kind === "gap") k++; const q = phones[k]; return q?.kind === "consonant" && q.c.organ === p.c.organ && q.c.area > 0 && q.c.area < .4; };
  // A CONSONANT'S OWN TWO TIME CONSTANTS: how quickly its organ takes hold of it, and how quickly it lets go again (a stop lets go faster
  // than it closed; an r is a whole posture; a tap is quick both ways). The DURATIONS need them as much as the gestures do -- a vowel is
  // only a vowel if there is time for the one before it to let go and the one after it to take hold -- so they are worked out here, once.
  const gestureTau = (p) => { const c = p.c, on = c.tap || c.trill ? G.tau.tap : G.tau[c.organ] ?? G.tau.body;
    const off = c.area <= 0 && !c.tap && !c.trill && intoNarrow(p) ? G.tau.tap * 1.6 : c.stop && p.affricate !== 1 ? (c.organ === "body" ? G.bodyStopRelease : c.organ === "lips" ? G.lipStopRelease : G.stopRelease) : c.release ? c.release : c.organ === "posture" ? on * Math.sqrt(G.carry) : on;     // (a posture -- an r -- at x carry had 9ms to cross a centimetre)
    return c.trill && T.trill.physical ? { on: G.tau.tip, off: G.tau.tip } : { on, off }; };      // (a trill the air beats: the tip only goes near the ridge and back)
  // ---- how long each phone is
  const real = phones.filter((p) => p.kind === "vowel" || p.kind === "consonant"), lastReal = real[real.length - 1], lastVowel = [...real].reverse().find((p) => p.kind === "vowel");
  phones.forEach((p, i) => {
    const prev = phones[i - 1], next = phones[i + 1];
    if (p.kind === "vowel") p.ms = (V.lax.includes(p.sym) && !p.long && !p.glideTo ? V.laxMs : V.ms) * (p.long && !(V.notLong ?? "").includes(p.sym) ? V.long : 1) * (p.glideTo ? V.diphthong : 1) * (p.stress ? V.stressed : V.unstressed) * (next?.kind === "consonant" && CONSONANTS[next.sym] && !CONSONANTS[next.sym].voiced ? V.beforeVoiceless : 1) * (p === lastVowel ? fin(V.final) : 1) * (p.emph && p.stress ? E.vowel : 1) * (p.stress ? 1 : Math.max(.5, 1 + Ef.unstressedMs * (effortOf(p) - 1))) / (1 + Ph.rhythm * Math.max(0, (p.crowd ?? 1) - 1));
    else if (p.kind === "consonant") { const c = CONSONANTS[p.sym]; p.c = c; p.ms = c.ms * (p.long ? 1.7 : 1) * (p.twin ? T.twin : 1) * ((prev?.kind === "consonant" || next?.kind === "consonant") ? T.cluster : 1) * (p === lastReal ? fin(T.lastConsonant) : 1) * (p.emph ? E.consonant : 1) * (1.1 - .2 * lg) * (p.offglide ? T.offglide : 1) * (p.affricate === 2 ? .8 : 1) * (p.affricate === 1 ? .8 : 1); }
    else if (p.kind === "pause") p.ms = (p.ms ?? T.pauseMs) * who.pauseScale;
    else p.ms = prev && next && prev.kind !== "pause" && next.kind !== "pause" ? Math.max(0, .5 - lg) * 2 * prosody.staccatoGapMs : 0;
    if (p.phraseFinal) p.ms *= fin(p.phraseFinal);
    if (p.at !== undefined) p.ms *= 1 + Ph.tempoArc * (Math.abs(p.at - .5) * 4 - 1);
    if (vy > 0 && p.phrase !== undefined) p.ms *= (paceOf[p.phrase] ??= 1 + vy * Vr.pace * rnd()) * (p.kind === "vowel" ? 1 + vy * Vr.vowel * rnd() : 1);
    p.ms /= styleOf(p, "tempo", (a, v) => a * v, 1);
  });
  if (pace) phones.forEach((p, i) => { p.ms *= pace[i] ?? 1; });      // (time dealt out by movement: see PERSON.byMovement)
  if (stretch) phones.forEach((p, i) => { p.ms *= 1 + limits.slowDown * Math.max(.3, who.effort ?? 1) * ((stretch.ms[i] ?? 1) - 1); });      // (the time taken where the mouth could not keep up: see LIMITS)
  // A VOWEL SHUT IN BETWEEN TWO CONSTRICTIONS IS GIVEN THE TIME TO BE ONE (TIMING.vowelRoom). Both gestures pull the same tract shut, one
  // letting go while the other takes hold, and a vowel shorter than the two together is never reached: "what it is" came out as a single
  // 176 ms closure with silence inside it -- "wha ... iz" -- because the t of "what" was still on the tip 14 ms later, when the t of "it"
  // began to close again over a 47 ms vowel. It is the same answer as the limiter's for a movement that is too far: take the time.
  { const V = T.vowelRoom; if (V?.x > 0) phones.forEach((p, i) => { if (p.kind !== "vowel") return;
      const at = (k, d) => { while (phones[k]?.kind === "gap") k += d; const q = phones[k]; return q?.kind === "consonant" && q.c?.organ && q.c.area < V.tight ? q : null; };
      const before = at(i - 1, -1), after = at(i + 1, 1);
      p.ms = Math.max(p.ms, V.x * ((before ? T.gesture.ahead * gestureTau(before).off : 0) + (after ? G.ahead * gestureTau(after).on : 0))); }); }
  const rate = voice?.rate ?? 1; let t = T.leadMs; for (const p of phones) { p.t0 = t; t += p.ms / rate; p.t1 = t; }
  const burstExtra = lastReal?.c?.stop && !lastReal.c.voiced ? prosody.finalBurstMs : 0;      // (after a final voiceless stop everything that ends the utterance waits for its burst)
  const total = t + T.tailMs + burstExtra, n = Math.ceil(total / 1000 * T.control), dt = 1000 / T.control;
  const tracks = { n, control: T.control, total }; const keys = Object.keys(ARTICULATORS);
  for (const k of [...keys, "rest", "pressure", "f0", "flap", "creak", "chink"]) tracks[k] = new Float32Array(n);
  // LEGATO is one number over what already makes speech connected: how slowly the vowel gesture settles, how early a consonant's
  // gesture starts and how slowly its helpers let go, how much the pitch glides (.5 is the configuration as written)
  const tauMs = Object.fromEntries(Object.entries(T.tauMs).map(([k, v]) => [k, k === "f0" ? v * (.6 + .8 * lg) : k === "rest" || k === "pressure" ? v : v * (.75 + .5 * lg) * Math.max(.6, 1 + Ef.settle * (1 - (who.effort ?? 1)))]));
  // ---- the vowel layer: posture to posture
  const vowels = phones.filter((p) => p.kind === "vowel"), rest0 = neutral();
  // (where in the consonants between two vowels the tract turns to the next one, x the speaker's anticipation: to that power, so that
  // 0 turns only at the vowel itself and 2 turns twice as early into the consonants, and any anticipation leaves it somewhere inside them)
  const vSwitch = Math.pow(Math.max(1e-3, T.vowelSwitch), ant);
  const marks = [];                                  // [time, posture]: from this time on, head for this posture
  // (how far towards its posture a vowel is AIMED goes with the effort: a lazy vowel stops short, nearer the mouth's rest; a careful one goes all the way -- never beyond: a posture pushed past itself shuts the lips of an u or the palate of an i)
  const jawHome = rest0.jaw + (who.jawSetting ?? 0), jawFree = Math.max(0, who.jawFreedom ?? 1);
  const asFreeAsTheJawIs = (a) => jawFree === 1 ? a : setJaw(a, jawHome + (a.jaw - jawHome) * jawFree, anatomy);
  const aim = (v, sym) => { const full = { ...rest0, ...postures[sym] }; full.jaw += who.jawSetting ?? 0; const g = Math.max(.45, Math.min(1, 1 + (v.stress ? Ef.vowel : Ef.unstressedVowel) * (effortOf(v) - 1))); if (g === 1) return asFreeAsTheJawIs(full);
    return asFreeAsTheJawIs(Object.fromEntries(Object.entries(full).map(([k, x]) => [k, k === "velum" || k === "lateral" ? x : rest0[k] + (x - rest0[k]) * g]))); };
  vowels.forEach((v, i) => {
    const prevV = vowels[i - 1], from = prevV ? prevV.t1 + (v.t0 - prevV.t1) * vSwitch : 0;
    marks.push([from, aim(v, v.sym)]);
    if (v.glideTo) marks.push([v.t0 + (v.t1 - v.t0) * T.vowel.glideAt, aim(v, v.glideTo)]);
  });
  if (!marks.length) marks.push([0, rest0]);
  const lastSound = lastReal ? lastReal.t1 : T.leadMs; marks.push([lastSound + burstExtra + T.restAfterMs, rest0]);      // and back to rest when it is over -- when the VOICE is over: the breath takes ~120ms to go, and a mouth that
  // sets off for rest while the folds still sound turns its last vowel into a diphthong ("see-uh") -- every sentence ended with something added
  const carrierAt = (ms) => { let m = marks[0][1]; for (const [at, p] of marks) if (at <= ms) m = p; return m; };
  for (let i = 0; i < n; i++) { const m = carrierAt(i * dt + tauMs.bodyX * T.gesture.vowelAhead * ant); for (const k of keys) tracks[k][i] = m[k] ?? rest0[k]; }
  // the vowel gesture is the SLOW one: it alone is lagged by the organs' time constants (so a short vowel undershoots)
  const lag = (tr, tauMs) => { const w = 1000 / tauMs, h = dt / 1000; let y = tr[0], v = 0; for (let i = 0; i < n; i++) { const a = w * w * (tr[i] - y) - 2 * w * v; v += a * h; y += v * h; tr[i] = y; } };
  for (const k of keys) lag(tracks[k], tauMs[k] ?? 30);
  // ---- the consonants, laid over it.
  // A consonant's gesture is QUICK and EXACT: while it holds, its organ is where the constriction needs it, whatever
  // the vowels are doing underneath -- so the constriction is SOLVED FRAME BY FRAME against the posture the mouth really
  // has at that frame (a tip that was placed once, against a posture the mouth has since left, leaks or jams: measured,
  // "water" had no closure for its t and "fish" a shut sh). What is smooth is the WEIGHT the gesture comes in and goes
  // out with; two gestures of one organ that overlap share it by weight.
  // a gesture's ACTIVATION over time: a switch (on `ahead` time constants early, off at the end -- or later, if it is held),
  // answered by a critically damped second-order system; tauOff may differ (a stop lets go quicker than it closes)
  const edgeStart = (p) => p === real[0], heldAfter = (p) => { const k = phones.indexOf(p); let q = k + 1; while (phones[q]?.kind === "gap") q++; return !phones[q] || phones[q].kind === "pause"; };
  const activation = (a, b, tauOn, tauOff = tauOn, { fromStart = false, hold = 0, notBefore = -1e9, offEarly = 0 } = {}) => {
    const on = fromStart ? -1e9 : Math.max(notBefore, a - G.ahead * tauOn), off = b + hold - offEarly, i0 = fromStart ? 0 : Math.max(0, Math.floor(on / dt)), i1 = Math.min(n, Math.ceil((off + 7 * tauOff) / dt)), w = new Float32Array(Math.max(0, i1 - i0));
    let y = fromStart ? 1 : 0, v = 0; const h = dt / 1000;
    for (let i = i0; i < i1; i++) { const ms = i * dt, u = ms >= on && ms < off ? 1 : 0, om = 1000 / (u ? tauOn : tauOff); v += (om * om * (u - y) - 2 * om * v) * h; y += v * h; w[i - i0] = Math.max(0, Math.min(1, y)); }
    return { i0, i1, w };
  };
  // (x this consonant's time constants, coming and going apart: a g that had to come slowly need not leave slowly -- leaving slowly it lay
  // over the short vowel after it, and "dog is" had no i)
  const slower = (p, side) => stretch?.[side][phones.indexOf(p)] ?? 1;
  // A VOWEL KEEPS ITS OPENING: the constriction after a vowel does not start to close before `gesture.vowelShare` of that vowel has gone by,
  // however early its gesture would like to start (at high legato, with slowed gestures, the z of "dog is" began in the g and the i between
  // them was never open: "dog'z").
  const afterVowel = (p) => { let k = phones.indexOf(p) - 1; while (phones[k]?.kind === "gap") k--; const v = phones[k]; return v?.kind === "vowel" ? v.t0 + (v.t1 - v.t0) * G.vowelShare : -1e9; };
  const actFor = (p, tauOn0, tauOff0 = tauOn0, guard = false) => { const tauOn = tauOn0 * slower(p, "on"), tauOff = tauOff0 * slower(p, "off"); return activation(p.t0, p.t1, tauOn, tauOff, { notBefore: guard ? afterVowel(p) : -1e9, fromStart: edgeStart(p), hold: heldAfter(p) ? (p.c.stop && !p.c.voiced ? G.finalStopHoldMs : p.c.area > 0 && p.c.area < .3 ? G.finalFricativeHoldMs : G.finalHoldMs) : 0 }); };
  const acc = () => ({ w: new Float32Array(n), v: new Float32Array(n) });
  const blend = (key, o) => { const tr = tracks[key]; for (let i = 0; i < n; i++) if (o.w[i] > 1e-4) { const w = Math.min(1, o.w[i]); tr[i] = tr[i] * (1 - w) + (o.v[i] / o.w[i]) * w; } };
  const cons = phones.filter((p) => p.kind === "consonant" && p.c.organ), bodyHeld = new Float32Array(n);
  // A CONSONANT THAT IS A WHOLE SHAPE (an r) is given SHAPES and the names of the speaker's knobs that choose between them -- people's
  // r's differ far more than their t's do. With one knob: from the first shape to the second. With two (`shapeBy: [which, how far]`):
  // the shapes AFTER the first are the full ways of making the sound and the first knob picks among them; the first shape is where a
  // weak one stops, and the second knob says how far from it this mouth goes. One shape and no knob: `posture`, as it was.
  const mix = (a, b, u) => Object.fromEntries(Object.keys({ ...a, ...b }).map((k) => [k, (a[k] ?? rest0[k]) * (1 - u) + (b[k] ?? rest0[k]) * u]));
  const knob = (name, dflt) => Math.max(0, Math.min(1, who[name] ?? dflt));
  const postureOf = (c) => { if (!c.shapes) return c.posture; const sh = Object.values(c.shapes);
    if (!Array.isArray(c.shapeBy)) return mix(sh[0], sh[1] ?? sh[0], knob(c.shapeBy, 1));
    const full = sh.length > 2 ? mix(sh[1], sh[2], knob(c.shapeBy[0], 0)) : sh[1];
    return mix(sh[0], full, knob(c.shapeBy[1], 1)); };
  // (1) what a consonant asks of the REST of the mouth: a raised jaw, rounded lips, the body lending a hand, the velum, the tongue's sides
  { const sec = Object.fromEntries(["jaw", "lipP", "bodyX", "bodyY", "velum", "lateral"].map((k) => [k, acc()]));
    const put = (key, act, value, { relative = false, floor = false, ceil = false } = {}) => { const o = sec[key]; for (let i = act.i0; i < act.i1; i++) { const cur = tracks[key][i], w = act.w[i - act.i0], idle = (floor && cur >= value) || (ceil && cur <= value);
      // (a demand that is already met still takes its SHARE, asking for what is there: dropped from the sum, two consonants with different
      // jaw heights made the jaw jump a degree in one frame as the vowel's jaw crossed one of them -- 500 degrees a second)
      o.v[i] += w * (idle ? cur : relative ? cur + value : value); o.w[i] += w; } };
    for (const p of cons) { const c = p.c;
      if (c.jawMax !== undefined) put("jaw", actFor(p, G.tau.jaw), c.jawMax + Math.max(0, Ef.jaw * (1 - effortOf(p))) * Math.max(0, rest0.jaw - c.jawMax), { ceil: true });
      if (c.round !== undefined) put("lipP", actFor(p, G.tau.round, G.tau.round * G.carry), c.round);
      // back / palatal: the body shifted by so much; raise: the body AT LEAST this high and this far forward (one that is
      // already up under the palate for an /i/ must not be pushed into it)
      const dx = -(c.back ?? 0) + (p.palatal ? .45 : 0), dy = p.palatal ? .55 : 0;
      if (dx || dy) { const a = actFor(p, G.tau.help, G.tau.help * G.carry); put("bodyX", a, dx, { relative: true }); put("bodyY", a, dy, { relative: true }); }
      if (c.raise) { const a = actFor(p, G.tau.help, G.tau.help * G.carry); put("bodyY", a, c.raise, { floor: true }); put("bodyX", a, .2, { floor: true }); }
      if (c.velum) {   // THE VELUM STAYS SHUT THROUGH AN OBSTRUENT. It opens early for a nasal while a vowel is going (that is why the vowel
        // of "man" is nasal), but not while the mouth is holding pressure: opened under a /k/'s closure it lets the pressure out
        // through the nose with a pop ("computer"), and left open into one it does the same at the release ("thanks").
        const k = phones.indexOf(p), obstruent = (q) => q?.kind === "consonant" && !q.c.velum && q.c.organ && q.c.area < .3;
        let a0 = k - 1; while (phones[a0]?.kind === "gap") a0--; let b0 = k + 1; while (phones[b0]?.kind === "gap") b0++;
        const before = [...phones.slice(0, k)].reverse().find((q) => q.kind !== "gap" && q.kind !== "vowel" ? true : false), lastObs = [...phones.slice(0, k)].reverse().find(obstruent);
        const tight = obstruent(phones[b0]);
        // and it is on its way up BEFORE the nasal ends when something oral follows -- quicker if an obstruent is two sounds away: left
        // to close after the m, it was open through the whole vowel of "doom is" and into the z, and a z with the nose open is an n ("doom in")
        let c0 = b0 + 1; while (phones[c0]?.kind === "gap") c0++;
        const oralNext = phones[b0] && phones[b0].kind !== "pause" && !phones[b0].c?.velum && !phones[b0].nasal, soon = oralNext && obstruent(phones[c0]);
        put("velum", activation(p.t0, p.t1, G.tau.velum, tight || c.velumLead ? G.velumShutTau : soon ? G.velumShutTau * 1.4 : G.tau.velum, { fromStart: edgeStart(p), hold: heldAfter(p) ? G.finalHoldMs : 0, notBefore: lastObs ? lastObs.t1 + 8 : -1e9, offEarly: tight ? 2.2 * G.velumShutTau : oralNext ? (c.velumLead ?? G.velumLeadMs) : 0 }), c.velum); }
      // (the sides stay down a little past an l -- unless a closure of the tip follows: "old dog" had a d that leaked past the tongue's sides)
      const shutNext = (() => { let k = phones.indexOf(p) + 1; while (phones[k]?.kind === "gap") k++; const q = phones[k]; return q?.kind === "consonant" && CONSONANTS[q.sym]?.organ === "tip" && CONSONANTS[q.sym].area <= 0 && !CONSONANTS[q.sym].lateral; })();
      if (c.lateral) put("lateral", activation(p.t0 - G.lateralLeadMs, p.t1 + (shutNext ? -12 : G.lateralLagMs), G.tau.lateral, shutNext ? G.tau.lateral * G.lateralShut : G.tau.lateral, { fromStart: edgeStart(p), hold: heldAfter(p) ? G.finalHoldMs + 60 : 0 }), 1); }
    for (const v of vowels) if (v.nasal) { const k = phones.indexOf(v), lastObs = [...phones.slice(0, k)].reverse().find((q) => q.kind === "consonant" && !q.c.velum && q.c.organ && q.c.area < .3); put("velum", activation(v.t0, v.t1, G.tau.velum, G.tau.velum, { notBefore: lastObs ? lastObs.t1 + 8 : -1e9 }), .55); }
    for (const k of Object.keys(sec)) blend(k, sec[k]); }
  // (the tongue's BODY first, then tip and lips: a tip that cannot reach asks the body to come part of the way, but only
  // where no consonant of the body's own holds it -- in "thanks" the s must not pull the k's closure open)
  // (...and before either, a consonant that is a SHAPE of the whole mouth (r): whatever closes or narrows after it takes its organ back)
  for (const pass of ["posture", "body", "rest"]) { const crit = Object.fromEntries(["jaw", "lipH", "lipP", "tipX", "tipY", "bodyX", "bodyY"].map((k) => [k, acc()])), art = {}, held = pass === "rest" ? bodyHeld : null;
    for (const p of cons) { if ((p.c.organ === "posture" ? "posture" : p.c.organ === "body" ? "body" : "rest") !== pass) continue; const c = p.c, { on: tauOn, off: tauOff } = gestureTau(p);
      const sprung = !!c.trill && T.trill.physical, ef = effortOf(p), area = (sprung ? T.trill.area : c.area > 0 ? c.area * Math.max(.6, 1 + Ef.open * (1 - ef)) : c.area) * headArea;
      const beats = c.trill && !sprung ? Math.max(2, Math.round((p.t1 - p.t0) / 1000 * c.trill)) : 1;      // a trill: the tip beats against the ridge, shut for half of each beat
      const gates = c.trill && !sprung ? Array.from({ length: beats }, (_, j) => [p.t0 + (p.t1 - p.t0) * j / beats, p.t0 + (p.t1 - p.t0) * (j + .5) / beats]) : [[p.t0, p.t1]];
      for (const [a, b] of gates) { const act = gates.length > 1 ? activation(a, b, tauOn, tauOff) : actFor(p, tauOn, tauOff, true);
        for (let i = act.i0; i < act.i1; i++) { const w = act.w[i - act.i0]; if (w <= .002) continue;
          for (const k of keys) art[k] = tracks[k][i]; clampArt(art); if (sprung) tracks.flap[i] = Math.max(tracks.flap[i], w);
          let place = c.place; if (c.slides) { const u = Math.max(-1, Math.min(1, art.bodyX / 1.1)), e = u * u * (3 - 2 * Math.abs(u)); place = u >= 0 ? ["velar", "palatal", e * .8] : ["velar", "uvular", e * .8]; }   // a body consonant is made where the vowel has the body -- sliding, never jumping
          const set = (k, v, share = 1) => { crit[k].v[i] += w * share * v; crit[k].w[i] += w * share; };
          if (pass === "body") bodyHeld[i] = Math.max(bodyHeld[i], w);
          if (c.organ === "posture") { for (const [k, v] of Object.entries(postureOf(c))) if (crit[k]) set(k, v); }   // a shape of the whole mouth (r)
          else if (c.organ === "lips") { solveLips(art, area, anatomy); set("lipH", area <= 0 ? art.lipH - .25 : art.lipH); if (c.round === undefined && c.area > 0) set("lipP", Math.min(art.lipP, .15)); }
          else if (c.organ === "tip") { const bx = art.bodyX, by = art.bodyY; solveTip(art, place, area, anatomy); set("tipX", art.tipX); set("tipY", art.tipY + (area <= 0 ? .1 : 0)); if (art.bodyX !== bx || art.bodyY !== by) { set("bodyX", art.bodyX, 1 - held[i]); set("bodyY", art.bodyY, 1 - held[i]); } }   // (by as much as no body consonant holds it: a gate at 5% was a jump)
          else { const tuck = c.tuck ?? [0, -.5]; art.tipY = Math.min(art.tipY, tuck[1]); art.tipX = Math.min(art.tipX, tuck[0]); set("tipY", art.tipY); set("tipX", art.tipX);      // (the tip rides up with a raised body: for a sound made with the body it is tucked down behind the lower teeth, or IT becomes the narrow place)
            solveBody(art, place, area, anatomy); set("bodyX", art.bodyX); set("bodyY", art.bodyY); }
          if (c.lipArea !== undefined) { solveLips(art, c.lipArea * headArea, anatomy); set("lipH", art.lipH); } } } }
    for (const k of Object.keys(crit)) blend(k, crit[k]); }
  // ---- the folds
  const R = prosody.rest, voicedRest = voice?.rest ?? .004, restT = tracks.rest.fill(voicedRest);
  // the folds drawn apart and brought back: widest at `centre`, opening over `before` ms and closing over `after`
  const bellOn = (tr, base, centre, before, peak, after = before, openBy = 1) => { for (let i = Math.max(0, Math.floor((centre - before) / dt)); i < Math.min(n, Math.ceil((centre + after) / dt)); i++) { const ms = i * dt, u = ms < centre ? Math.min(1, (1 - (centre - ms) / before) / openBy) : 1 - (ms - centre) / after; tr[i] = Math.max(tr[i], base + (peak - base) * smoothstep(u)); } };
  const bell = (centre, before, peak, after = before, openBy = 1) => bellOn(restT, voicedRest, centre, before, peak, after, openBy);
  const firstSound = real[0]?.t0 ?? T.leadMs;
  // before and after speaking the folds stand open for breathing -- but they are TOGETHER before the pressure comes,
  // and the pressure is gone before they part again: a breath is not part of the word
  for (let i = 0; i < n; i++) { const ms = i * dt; if (ms < firstSound - 45) restT[i] = Math.max(voicedRest, R.breathing * (1 - smoothstep((ms - (firstSound - 105)) / 60))); if (ms > lastSound + burstExtra + 70) restT[i] = Math.max(restT[i], R.breathing * smoothstep((ms - lastSound - burstExtra - 70) / 110)); }
  phones.forEach((p, i) => {
    if (p.kind !== "consonant") return; const c = p.c, next = phones.slice(i + 1).find((q) => q.kind !== "gap");
    const before = phones.slice(0, i).reverse().find((q) => q.kind !== "gap");
    // (an h after a stop: the folds wait for the stop to let go. Parting during a /d/'s closure they made its release a gust through
    // an open glottis -- "and his" had a tick for a d)
    if (c.breath !== undefined) { const mid = (p.t0 + p.t1) / 2, own = (p.t1 - p.t0) / 2 + 28;
      // (...and never quicker than the folds themselves can open: asked for it in 12 ms, they are held back by the limiter and the h is a hiss)
      const need = c.breath / Math.max(.1, limits.rest?.speed ?? 7) * 1000;
      const lead = before?.c?.stop && before.c.voiced ? Math.max(need, mid - (p.t0 + prosody.breathAfterStopMs)) : own;
      bell(mid, Math.max(need, lead), c.breath, own); return; }
    if (c.voiced) { if (c.area > 0 && c.area < .3 && c.organ) { bell((p.t0 + p.t1) / 2, (p.t1 - p.t0) / 2 + 20, R.voicedFricative);
        // THE GAP AT THE BACK OF THE GLOTTIS (glottis.js `chink`): the folds go on meeting in front of it, so the voice is there, but the
        // air never stops -- and a voiced fricative HISSES all the way through instead of only where the folds happen to be apart.
        bellOn(tracks.chink, 0, (p.t0 + p.t1) / 2, (p.t1 - p.t0) / 2 + 25, R.voicedChink, (p.t1 - p.t0) / 2 + 25);
        // a voiced fricative before silence LOSES ITS VOICE on the way (English "his" ends nearly in an s): the folds part from its middle on and
        // stay apart -- let go with the voice still running, it grew a vowel ("hiz-uh")
        if (heldAfter(p)) bell(p.t1 + 20, (p.t1 - p.t0) * .6 + 20, R.fricative * prosody.finalDevoice, 140); }
      return; }
    if (c.stop && p.affricate !== 1) {
      const asp = (p.aspirated ? 1 : L.aspirate) * (next?.kind === "vowel" ? (next.stress ? 1 : prosody.aspirateUnstressed) : .4) * (phones[i - 1]?.sym === "s" ? .15 : 1);
      // the folds part during the closure; with aspiration their widest is AT the release and they are back `aspirationMs` later
      const centre = p.t1 - (1 - asp) * (p.t1 - p.t0) * .6;
      bell(centre, (p.t1 - p.t0) * .9 + 10, R.stop * (.7 + .5 * asp), asp * prosody.aspirationMs + 22, prosody.stopOpenBy);
    } else bell((p.t0 + p.t1) / 2, (p.t1 - p.t0) / 2 + 30, R.fricative);
  });
  // ---- breath and tune
  const P = tracks.pressure, F = tracks.f0, f0 = voice?.f0 ?? 118, spoken = Math.max(1, lastSound - firstSound);
  // (a final voiceless stop is let go AFTER its time is up: the breath has to last until it has burst -- "meet" had no t)
  const breathEnd = lastSound + burstExtra;
  const fallFrom = lastVowel ? Math.min(lastSound - 120, (lastVowel.t0 + lastVowel.t1) / 2) : lastSound - 300;
  for (let i = 0; i < n; i++) { const ms = i * dt; P[i] = prosody.pressure * smoothstep((ms - (firstSound - 55)) / 50) * (ms > breathEnd ? 1 - smoothstep((ms - breathEnd) / prosody.finalPressureMs) : 1) * (1 - (1 - prosody.finalPressure) * smoothstep((ms - fallFrom) / Math.max(60, lastSound - fallFrom))); }
  // a PAUSE is a breath of silence, not a held note: the pressure goes, the folds part, and both come back for what follows
  for (const q of phones) if (q.kind === "pause" && q.t1 - q.t0 > 60) { const a0 = q.t0 + 10, b0 = q.t1 - 45;
    for (let i = Math.floor(a0 / dt); i < Math.min(n, q.t1 / dt); i++) { const ms = i * dt; P[i] *= 1 - smoothstep((ms - a0) / 70) * (1 - smoothstep((ms - b0) / 45)); }
    if (q.t1 - q.t0 > 150) bell((q.t0 + q.t1) / 2, (q.t1 - q.t0) / 2 - 10, R.breathing * .7); }
  for (const q of cons) if (q.c.stop && !q.c.voiced && heldAfter(q)) for (let i = Math.floor(q.t0 / dt); i < Math.min(n, (q.t1 + 200) / dt); i++) { const ms = i * dt, u = smoothstep((ms - q.t0) / Math.max(20, q.t1 - q.t0)) * (1 - smoothstep((ms - q.t1 - 80) / 120)); P[i] *= 1 - (1 - G.finalStopPressure) * u; }   // (and back up after it: what follows a pause has its own breath)
  // ---- the tune. Everything that MOVES the pitch is gathered in `st` (semitones about the voice's own pitch), so that one
  // person's range can scale it; where the speech sits (register, a (high: ...)) is added after.
  // staccato: the breath lets up between the words
  for (const q of phones) if (q.kind === "gap" && q.t1 - q.t0 > 15) for (let i = Math.floor((q.t0 - 25) / dt); i < Math.min(n, (q.t1 + 25) / dt); i++) { if (i < 0) continue; const ms = i * dt; P[i] *= 1 - .65 * smoothstep((ms - (q.t0 - 25)) / 30) * (1 - smoothstep((ms - (q.t1 - 5)) / 30)); }
  const st = new Float32Array(n), span = (p) => [Math.max(0, Math.floor(p.t0 / dt)), Math.min(n, Math.ceil(p.t1 / dt))];
  // what the named ways of speaking ask for, frame by frame, eased so that a bracket is not a step
  const sty = { pitch: new Float32Array(n), range: new Float32Array(n).fill(1), pressure: new Float32Array(n).fill(1), rest: new Float32Array(n), smile: new Float32Array(n), creak: new Float32Array(n) };
  { let last = null; for (const p of phones) { if (p.kind !== "gap") last = p; const [a, b] = span(p); if (!p.styles) continue;
      const v = { pitch: styleOf(p, "pitch", (x, y) => x + y, 0), range: styleOf(p, "range", (x, y) => x * y, 1), pressure: styleOf(p, "pressure", (x, y) => x * y, 1), rest: styleOf(p, "rest", (x, y) => x + y, 0), smile: styleOf(p, "smile", (x, y) => Math.max(x, y), 0), creak: styleOf(p, "creak", (x, y) => Math.max(x, y), 0) };
      for (let i = a; i < b; i++) for (const k in sty) sty[k][i] = v[k]; }
    if (last?.styles) { const [, b] = span(last); for (let i = b; i < n; i++) for (const k in sty) sty[k][i] = sty[k][b - 1]; }
    for (const k in sty) lag(sty[k], 45); }
  // declination: part of it runs over the whole utterance, the rest starts again with every phrase
  const bounds = phrases.map((ph) => [ph[0].t0, ph[ph.length - 1].t1]); if (!bounds.length) bounds.push([firstSound, lastSound]);
  for (let i = 0; i < n; i++) { const ms = i * dt, u = Math.max(0, Math.min(1, (ms - firstSound) / spoken)); let k = 0; while (k < bounds.length - 1 && ms >= bounds[k + 1][0] - 60) k++;
    const v = Math.max(0, Math.min(1, (ms - bounds[k][0]) / Math.max(1, bounds[k][1] - bounds[k][0])));
    st[i] = prosody.declination * (bounds.length > 1 ? (1 - Ph.reset) * (u - .35) + Ph.reset * (v - .35) : u - .35) + (vy > 0 ? (levelOf[k] ??= vy * Vr.level * (rnd() + .3)) : 0); }
  // accents: each stressed vowel a bump, smaller down the phrase; an emphasised word's is bigger and takes the rest of its phrase down
  const stressed = vowels.filter((v) => v.stress), seen = new Map();
  stressed.forEach((v) => { const k = v.phrase ?? 0, j = seen.get(k) ?? { n: 0, after: false }; seen.set(k, j);
    const c = (v.t0 + v.t1) / 2 - prosody.accentLeadMs + (vy > 0 ? vy * Vr.accentMs * rnd() : 0), w = (v.t1 - v.t0) * .9 + 60;
    const own = vy > 0 && !v.emph ? (Math.abs(rnd()) < vy * Vr.skip ? Vr.skipTo : 1 + vy * Vr.accent * (rnd() * .85 + .4)) : 1;      // (uneven, and on the whole BIGGER: evening accents out is what monotony is)
    const h = own * prosody.accent * who.liveliness * Math.max(.3, 1 + Ef.accent * (effortOf(v) - 1)) * (mark === "!" ? prosody.exclaim : 1) * (v.emph ? E.accent : Math.pow(Ph.downstep, j.n) * Math.pow(Ph.phraseStep, k) * (j.after ? E.after : 1));
    j.n++; if (v.emph) j.after = true;
    for (let i = 0; i < n; i++) { const d = (i * dt - c) / w; if (Math.abs(d) < 1) st[i] += h * (.5 + .5 * Math.cos(Math.PI * d)); }
    for (let i = Math.floor(v.t0 / dt); i < Math.min(n, v.t1 / dt); i++) P[i] += prosody.stressPressure * (v.emph ? E.pressure : 1) * (.5 - .5 * Math.cos(2 * Math.PI * (i * dt - v.t0) / (v.t1 - v.t0))); });
  // the end of a phrase that is not the last says "there is more": up, and let go in the pause
  bounds.slice(0, -1).forEach(([, end]) => { for (let i = 0; i < n; i++) { const ms = i * dt; st[i] += Ph.continuationRise * smoothstep((ms - (end - Ph.continuationMs)) / Ph.continuationMs) * (1 - smoothstep((ms - end - 40) / 160)); } });
  const endMove = (mark === "?" ? prosody.questionRise : prosody.finalFall) * (vy > 0 ? 1 + vy * Vr.finalFall * rnd() : 1);
  for (let i = 0; i < n; i++) st[i] += endMove * smoothstep((i * dt - (lastSound - prosody.finalMs)) / prosody.finalMs);
  for (let i = 0; i < n; i++) st[i] *= who.range * sty.range[i];
  if (L.tonal) { st.fill(0); const syl = []; let cur = null; for (const p of real) { if (!cur || (p.kind === "consonant" && cur.hasV)) { cur = { t0: p.t0, t1: p.t1, tone: p.tone, hasV: false }; syl.push(cur); } cur.t1 = p.t1; cur.tone = cur.tone ?? p.tone; if (p.kind === "vowel") cur.hasV = true; }
    for (const s of syl) { const c = prosody.tones[s.tone ?? 5]; for (let i = Math.floor(s.t0 / dt); i < Math.min(n, s.t1 / dt); i++) { const u = (i * dt - s.t0) / Math.max(1, s.t1 - s.t0), lv = u < .5 ? c[0] + (c[1] - c[0]) * u * 2 : c[1] + (c[2] - c[1]) * (u - .5) * 2; st[i] = (lv - 3) / 4 * prosody.toneSpan - 1.5 * (i * dt - firstSound) / spoken; } } }
  // (the tune has a FLOOR, approached softly: fall, declination and a short word together took a 112Hz voice to 70Hz inside
  // one syllable, and a voice that low on a failing breath is a creak)
  // ---- the habits of this mouth, over everything: a smile, the lips' and the larynx's setting, a nose never quite shut, and creak
  { const Sm = prosody.smile, hold = new Float32Array(n);                // hold: where the mouth is holding pressure (and a little around it) the nose stays shut
    for (const q of cons) if (!q.c.velum && (q.c.stop || (q.c.area > 0 && q.c.area < .3))) for (let i = Math.max(0, Math.floor((q.t0 - 60) / dt)); i < Math.min(n, (q.t1 + 40) / dt); i++) hold[i] = 1;
    lag(hold, 10);
    const fryFrom = lastSound - prosody.fry.ms, falls = mark !== "?" && !L.tonal;
    for (let i = 0; i < n; i++) { const ms = i * dt, smile = Math.min(1, (who.smile ?? 0) + sty.smile[i]);
      tracks.lipSpread[i] += (who.lipSpread ?? 0) + Sm.lipSpread * smile; tracks.larynx[i] += (who.larynxHeight ?? 0) + Sm.larynx * smile;
      sty.pitch[i] += Sm.pitch * smile;
      tracks.velum[i] = Math.max(tracks.velum[i], (who.nasality ?? 0) * prosody.nasalityPort * Math.max(0, 1 - 1.4 * hold[i]));
      tracks.creak[i] = ms > lastSound + 80 ? 0 : Math.min(1, (who.creakiness ?? 0) + sty.creak[i] + (falls ? (who.fry ?? 0) * smoothstep((ms - fryFrom) / prosody.fry.ms) : 0)); } }
  for (let i = 0; i < n; i++) st[i] += who.register + sty.pitch[i];
  if (!L.tonal) for (let i = 0; i < n; i++) if (st[i] < 0) { const fl = -prosody.floor; st[i] = -fl * Math.tanh(-st[i] / fl); }
  for (let i = 0; i < n; i++) { F[i] = f0 * Math.pow(2, st[i] / 12); P[i] *= sty.pressure[i] * (1 + Ef.pressure * ((who.effort ?? 1) - 1)); restT[i] += sty.rest[i]; }
  // ---- nothing in a mouth jumps: a critically damped lag per track
  for (const k of ["rest", "pressure", "f0"]) lag(tracks[k], tauMs[k]);      // (the folds, the lungs, the pitch; the articulators were done above)
  lag(tracks.chink, tauMs.rest);
  for (const k of ["velum", "lateral"]) lag(tracks[k], 6);
  // VIBRATO sets in on a vowel that lasts: the pitch swings, and the breath a little with it (a quarter cycle ahead)
  if (who.vibratoDepth > 0) for (const v of vowels) { if (v.t1 - v.t0 < who.vibratoDelayMs + 60) continue; const [a, b] = span(v);
    for (let i = a; i < b; i++) { const ms = i * dt - v.t0, env = smoothstep((ms - who.vibratoDelayMs) / 150) * (1 - smoothstep((i * dt - (v.t1 - 50)) / 50)), ph = 2 * Math.PI * who.vibratoHz * ms / 1000;
      F[i] *= Math.pow(2, who.vibratoDepth * env * Math.sin(ph) / 12); P[i] *= 1 + .04 * who.vibratoDepth * env * Math.cos(ph); } }
  // ---- time by movement: measure what this plan asks of the organs, sound by sound, and plan again with the time dealt out accordingly.
  // A sound's time is what the language gives it PLUS what its movement takes: the time each sound's movement would take at the organs'
  // full speed is measured, and a sound gets `gain` x (its own - the average) more or less -- so a long vowel stays long, and it is the short
  // sounds with far to go that gain most.
  if ((who.byMovement ?? 0) > 0 && !pace) { const B = T.byMovement, organs = ["jaw", "bodyX", "bodyY", "tipX", "tipY", "lipH", "lipP"], move = phones.map(() => -1); let sum = 0, cnt = 0;
    phones.forEach((p, i) => { if (p.kind !== "vowel" && p.kind !== "consonant") return; const a = Math.max(1, Math.floor((p.t0 - B.leadMs) / dt)), b = Math.min(n, Math.ceil((p.t1 - B.leadMs) / dt)); let sec = 0;
      for (const k of organs) { let path = 0; for (let j = a; j < b; j++) path += Math.abs(tracks[k][j] - tracks[k][j - 1]); sec += path / (limits[k]?.speed ?? 50); }
      move[i] = sec * 1000; sum += move[i]; cnt++; });
    const mean = sum / Math.max(1, cnt), s = Math.min(1, who.byMovement);
    const dealt = phones.map((p, i) => move[i] < 0 ? 1 : Math.max(B.least, Math.min(B.most, 1 + s * B.gain * (move[i] - mean) / Math.max(20, p.t1 - p.t0))));
    let was = 0, now = 0; phones.forEach((p, i) => { if (move[i] >= 0) { was += p.t1 - p.t0; now += (p.t1 - p.t0) * dealt[i]; } }); const keep = was / Math.max(1, now);   // (the sentence keeps its length)
    return plan(ipa, { lang, postures: postures0, voice, mark, timing, prosody, limits, anatomy, pace: dealt.map((f, i) => move[i] >= 0 ? f * keep : 1) }); }
  limitTracks(tracks, limits, who.agility);
  for (const l of tracks.limited) { const p = real.find((q) => q.t1 > l.t0) ?? lastReal; l.near = p?.sym; }
  if (limits.on && limits.slowDown > 0 && pass < limits.passes && tracks.limited.length) {
    const next = { ms: phones.map((p, i) => stretch?.ms[i] ?? 1), on: phones.map((p, i) => stretch?.on[i] ?? 1), off: phones.map((p, i) => stretch?.off[i] ?? 1) }; let any = false;
    const raise = (arr, i, f) => { const was = arr[i]; arr[i] = Math.min(limits.maxStretch, Math.max(arr[i], was * f)); if (arr[i] > was + .01) any = true; };
    // (the vowels there get the time too: a slower gesture takes it out of them; only consonants have gestures to slow)
    for (const l of tracks.limited) { if (!(l.over > 1.02)) continue; const f = Math.min(limits.maxStretch, l.over);
      phones.forEach((p, i) => { if (p.kind !== "consonant" && p.kind !== "vowel") return; if (p.t1 < l.t0 - 40 || p.t0 > l.t1 + 15) return; raise(next.ms, i, f);
        if (p.kind === "consonant") { const mid = (p.t0 + p.t1) / 2; if (l.t0 < mid) raise(next.on, i, f); if (l.t1 > mid + 10) raise(next.off, i, f); } }); }
    if (any) return plan(ipa, { lang, postures: postures0, voice, mark, timing, prosody, limits, anatomy, stretch: next, pass: pass + 1, pace });
  }
  // ---- the last word: the things a mouth would never be caught doing (SANITY)
  tracks.odd = [];
  if (sanity?.on) {
    const An = anatomy ?? ANATOMY, art = {}, S = sanity;
    const fix = Object.fromEntries(["jaw", "bodyY", "tipY", "lipH", "pressure", "velum"].map((k) => [k, new Float32Array(n)]));
    const note = [];
    const narrowest = (a) => { const af = areaFunction(a, An); let m = 1e9, at = 0; for (let j = 2; j < af.As.length; j++) if (af.As[j] < m) { m = af.As[j]; at = j; } return { m, at, af }; };
    const whenAt = (ms) => { for (const p of real) if (p.t0 <= ms && p.t1 > ms) return p; return null; };
    const lastV = lastVowel;
    // (1) A VOWEL IS AN OPEN MOUTH -- at some moment in it, not at every one: its edges belong to the consonants beside it. So the
    // test is the WIDEST the mouth ever gets while the vowel sounds; if even that is a jet, the vowel never happened, and whatever
    // is nearest the wall is moved out of the way at the vowel's best moment -- a little at a time, no further than `openBy`, and
    // eased over the whole vowel so that nothing else is disturbed.
    for (const p of real) {
      const sonorant = p.kind === "vowel" || (p.kind === "consonant" && p.c.organ && p.c.area >= .3 && !p.c.velum && !p.c.stop);
      if (!sonorant) continue;
      const i0 = Math.max(0, Math.round(p.t0 / dt)), i1 = Math.min(n, Math.round(p.t1 / dt)); if (i1 <= i0) continue;
      let best = -1, bestM = -1;
      const every = Math.max(1, Math.round(5 / dt));      // (every 5 ms: the widest moment of a vowel is not a needle, and the area function is the dear part of this)
      for (let i = i0; i < i1; i += every) { for (const k of keys) art[k] = tracks[k][i]; const { m } = narrowest(art); if (m > bestM) { bestM = m; best = i; } }
      if (bestM >= S.open || best < 0) continue;
      for (const k of keys) art[k] = tracks[k][best];
      let { m, af } = narrowest(art), moved = 0, organ = null;
      // (whichever organ is making the narrow place, then the body, then the jaw -- and an organ already at its limit is passed over,
      //  or the rule would spend its whole allowance pushing on something that cannot move)
      while (m < S.open && moved < S.openBy) {
        const at = af.xs[narrowest(art).at], lips = at >= af.lipStart - .2, tip = !lips && af.sagittal.cuts.some((c) => c.tipCut && c.A <= m + .02), step = .12;
        const can = { lipH: art.lipH < ARTICULATORS.lipH[1] - .01, tipY: art.tipY > ARTICULATORS.tipY[0] + .01, bodyY: art.bodyY > ARTICULATORS.bodyY[0] + .01, jaw: art.jaw < ARTICULATORS.jaw[1] - .01 };
        const pick = (lips && can.lipH) ? "lipH" : (tip && can.tipY) ? "tipY" : can.bodyY ? "bodyY" : can.jaw ? "jaw" : can.tipY ? "tipY" : can.lipH ? "lipH" : null;
        if (!pick) break;
        if (pick === "lipH") art.lipH += step; else if (pick === "tipY") art.tipY -= step; else if (pick === "bodyY") art.bodyY -= step; else art.jaw += 1.4;
        organ = pick; moved += step; ({ m, af } = narrowest(art));
      }
      if (moved <= 0) continue;
      // eased in and out over the vowel, and ALL of it where the mouth was at its widest -- that is the moment the vowel is heard at
      const half = Math.max(1, best - i0, i1 - best);
      for (let i = i0; i < i1; i++) { const u = .5 + .5 * Math.cos(Math.PI * Math.min(1, Math.abs(i - best) / half));
        for (const k of ["jaw", "bodyY", "tipY", "lipH"]) fix[k][i] += (art[k] - tracks[k][best]) * u; }
      note.push([best, "a vowel with no room in it", organ, moved, bestM, 0, i0, i1]);      // (what it came to is measured after the mending, below)
    }
    // (2) A VOICE NEEDS BREATH, and (3) THE NOSE IS NOT A RELIEF VALVE. Both are gathered first and mended only where they LAST
    // (`holdMs`): a breath still on its way in at the first sound of all, or a velum still coming down out of a nasal, is a mouth
    // working, not a sound nobody makes.
    { const want = [{ rule: "a voice on no breath", track: "pressure", flag: new Uint8Array(n), to: 0 },
                    { rule: "the nose open on a shut mouth", track: "velum", flag: new Uint8Array(n), to: 0 }];
      for (let i = 0; i < n; i++) {
        const p = whenAt(i * dt); if (!p) continue;
        // the last vowel of all is allowed to run out of air -- that is how sentences end -- and a breath still rising is not sagging
        if (p.kind === "vowel" && p !== lastV && tracks.rest[i] < .03 && tracks.pressure[i] < S.voicePressure && (i === 0 || tracks.pressure[i] <= tracks.pressure[i - 1])) want[0].flag[i] = 1;
        if (!p.c?.velum && tracks.velum[i] > S.nasalPort && tracks.pressure[i] > S.nasalPressure) { for (const k of keys) art[k] = tracks[k][i]; if (narrowest(art).m < .02) want[1].flag[i] = 1; }
      }
      const least = Math.max(1, Math.round(S.holdMs / dt));
      for (const w of want) for (let i = 0; i < n;) { if (!w.flag[i]) { i++; continue; } let j = i; while (j < n && w.flag[j]) j++;
        if (j - i >= least) { let by = 0;
          for (let k = i; k < j; k++) { const d = w.track === "pressure" ? S.voicePressure - tracks.pressure[k] : S.nasalPort - tracks.velum[k]; fix[w.track][k] = d; by = Math.max(by, Math.abs(d)); }
          note.push([i, w.rule, w.track, by]); }
        i = j; } }
    note.sort((a, b) => a[0] - b[0]);
    // mended smoothly, and through the limiter once more: nothing is mended into a jump
    if (note.length) { for (const k of Object.keys(fix)) { lag(fix[k], 7); for (let i = 0; i < n; i++) tracks[k][i] += fix[k][i]; }
      limitTracks(tracks, limits, who.agility);
      // what the mending CAME TO, measured on the tracks as they now stand -- not on the trial that proposed it. Where the answer is
      // still a shut mouth, the rule says so: there was no room to be had, and the fault is earlier (too little time for the vowel).
      for (const r of note) { if (r.length < 7) continue; let mx = 0;
        for (let i = r[6]; i < r[7]; i++) { for (const k of keys) art[k] = tracks[k][i]; mx = Math.max(mx, narrowest(art).m); }
        r[5] = mx; r[1] = mx >= S.open ? "a vowel with no room in it" : "a vowel with no room in it, and none to be had"; }
      // (one line per run of frames with the same complaint)
      let run = null;
      const shut = () => { if (run) tracks.odd.push({ rule: run.rule, organ: run.organ, by: +run.by.toFixed(2), t0: +(run.i0 * dt).toFixed(0), t1: +((run.i1 + 1) * dt).toFixed(0), near: whenAt(run.i0 * dt)?.sym ?? "", ...(run.was === undefined ? {} : { was: +run.was.toFixed(2), now: +run.now.toFixed(2) }) }); run = null; };
      for (const [i, rule, organ, by, was, now] of note) {
        if (run && rule === run.rule && organ === run.organ && i <= run.i1 + 3) { run.i1 = i; run.by = Math.max(run.by, by); }
        else { shut(); run = { rule, organ, by, i0: i, i1: i, was, now }; } }
      shut(); }
  }
  tracks.slowed = stretch ? phones.map((p, i) => ({ sym: p.sym, by: stretch.ms[i] ?? 1 })).filter((x) => x.sym && x.by > 1.01) : [];
  tracks.phones = phones.filter((p) => p.kind !== "gap").map((p) => ({ sym: p.sym ?? "_", t0: p.t0, t1: p.t1, stress: !!p.stress, ...(p.glideTo ? { glideTo: p.glideTo } : {}) }));
  return tracks;
}
