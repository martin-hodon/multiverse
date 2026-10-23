// THE SOUNDS, as things done with a mouth.
//   A VOWEL is a posture of the whole tract (postures.json: found by inversion from vowels.js, then yours to adjust).
//   A CONSONANT is a CONSTRICTION: one organ (lips, tongue tip, tongue body) brought to a place with a given opening
//   -- shut for a stop or a nasal, a slit for a fricative, a gap for an approximant -- while the folds are drawn apart
//   or not, the velum lowered or not. Everything the consonant does NOT mention is left to the vowels around it, which
//   is coarticulation: the lips of "stew" are rounded through its s and t because nothing told them otherwise.
// No imports, no DOM.

// organ: lips | tip | body.  area: cm2 at the constriction (0 = shut).  voiced: folds together (false: drawn apart).
// ms: how long it is held.  Then, as needed: velum (0..1), lateral, round (lip protrusion cm), lipArea, jawMax (deg),
// also: a second constriction { organ, place, area }, tap / trill, burst: a stop (has a release).
export const CONSONANTS = {
  p: { organ: "lips", area: 0, voiced: false, ms: 70, stop: true }, b: { organ: "lips", area: 0, voiced: true, ms: 60, stop: true }, m: { organ: "lips", area: 0, voiced: true, ms: 70, velum: .7 },
  f: { organ: "lips", area: .13, voiced: false, ms: 95, jawMax: 5 }, v: { organ: "lips", area: .2, voiced: true, ms: 65, jawMax: 5 }, "β": { organ: "lips", area: .35, voiced: true, ms: 55 },
  t: { organ: "tip", place: "alveolar", area: 0, voiced: false, ms: 65, stop: true, jawMax: 6 }, d: { organ: "tip", place: "alveolar", area: 0, voiced: true, ms: 55, stop: true, jawMax: 6 },
  n: { organ: "tip", place: "alveolar", area: 0, voiced: true, ms: 65, velum: .7, jawMax: 7 },
  // the nasal of "comfort", "invite", "fünf": made where the f or v after it is made (here, as they are, at the lips; the jaw as high as theirs).
  // Nobody writes it -- the planner puts it in (TIMING.assimilate) where an m or n stands before f or v
  "ɱ": { organ: "lips", area: 0, voiced: true, ms: 60, velum: .7, jawMax: 5 },
  s: { organ: "tip", place: "alveolar", area: .13, voiced: false, ms: 100, jawMax: 3 }, z: { organ: "tip", place: "alveolar", area: .15, voiced: true, ms: 75, jawMax: 3 },
  "θ": { organ: "tip", place: "dental", area: .2, voiced: false, ms: 90, jawMax: 5 }, "ð": { organ: "tip", place: "dental", area: .3, voiced: true, ms: 55, jawMax: 6 },
  "ʃ": { organ: "tip", place: "postalveolar", area: .2, voiced: false, ms: 100, round: .8, jawMax: 3, raise: .3 }, "ʒ": { organ: "tip", place: "postalveolar", area: .22, voiced: true, ms: 75, round: .8, jawMax: 3, raise: .3 },
  "ʂ": { organ: "tip", place: "postalveolar", area: .15, voiced: false, ms: 100, jawMax: 4 }, "ʐ": { organ: "tip", place: "postalveolar", area: .18, voiced: true, ms: 75, jawMax: 4 },
  "ɕ": { organ: "body", place: "prepalatal", area: .14, voiced: false, ms: 100, jawMax: 3 }, "ʑ": { organ: "body", place: "prepalatal", area: .16, voiced: true, ms: 75, jawMax: 3 },
  // (the palatals are made with the FRONT of the tongue under the front of the palate, the tip tucked down behind the lower teeth -- that is
  // what gives them their i-like transitions, F2 at 2200-2500: made at the top of the dome with the tip riding along they were a fronted ng / n)
  "ç": { organ: "body", place: "palatal", area: .16, voiced: false, ms: 90, jawMax: 5 }, "ʝ": { organ: "body", place: "prepalatal", tuck: [-.9, -1], area: .25, voiced: true, ms: 60, jawMax: 5 },
  j: { organ: "body", place: "prepalatal", tuck: [-.9, -1], area: .55, voiced: true, ms: 55, jawMax: 6 }, "ɥ": { organ: "body", place: "prepalatal", tuck: [-.9, -1], area: .55, voiced: true, ms: 55, round: 1.0, lipArea: .5 },
  k: { organ: "body", place: "velar", area: 0, voiced: false, ms: 65, stop: true, slides: true }, g: { organ: "body", place: "velar", area: 0, voiced: true, ms: 55, stop: true, slides: true },
  "ŋ": { organ: "body", place: "velar", area: 0, voiced: true, ms: 70, velum: .7, slides: true }, 
  // ɲ (Spanish ñ, Czech ň, Italian gn) is made with the BLADE against the ridge behind the teeth and the body of the tongue up under the
  // palate as for an i -- an n with the tongue in the shape of a j -- and it is let go INTO a j (OFFGLIDES): "nj". Made with the tongue's
  // body alone (a closure at the top of the palate) it was heard as a cut-off n: no ear takes a closure that far back for an n-sound's
  // place, and its glide was lost in the nose.
  "ɲ": { organ: "tip", place: "postalveolar", area: 0, voiced: true, ms: 80, velum: .6, velumLead: 25, jawMax: 5, raise: 1.0 },
  x: { organ: "body", place: "velar", area: .16, voiced: false, ms: 90, slides: true }, "ɣ": { organ: "body", place: "velar", area: .35, voiced: true, ms: 55, slides: true },
  "χ": { organ: "body", place: "uvular", area: .18, voiced: false, ms: 85 }, "ʁ": { organ: "body", place: "uvular", area: .32, voiced: true, ms: 60 },
  l: { organ: "tip", place: "alveolar", area: 0, voiced: true, ms: 60, lateral: 1 }, "ɫ": { organ: "tip", place: "alveolar", area: 0, voiced: true, ms: 65, lateral: 1, back: .5 },
  "ʎ": { organ: "body", place: "prepalatal", tuck: [-.9, -1], area: 0, voiced: true, ms: 70, lateral: 1 },
  // an English r is not a place, it is a SHAPE: what makes it an r is a third formant down near 1700Hz, and in this mouth that
  // takes the whole tract -- the tongue drawn back and down into the throat, its tip tucked away, the lips rounded (found by the
  // inversion for 420 / 1300 / 1600Hz; it reaches 417 / 1264 / 1739). As a raised tip with a gap it was an l: same place, same
  // opening, F3 up at 2600.
  // AN ENGLISH R IS A SHAPE OF THE WHOLE MOUTH, and no two people's are alike -- so it is given as THREE shapes and two numbers of
  // the speaker's (`shapeBy`). The first shape is where a weak r stops; the ones after it are the full realisations, and the first
  // knob (`rShape`) says which of them this mouth makes, the second (`rStrength`) how far from the weak one it goes.
  //   bunched: the tongue ROOT back into the pharynx (0.60 cm2 there), the blade flat, the lips out -- F3 1708 Hz.
  //   retroflex: the TIP curled right up (found by the inversion, once the room under the tongue was built) -- the constriction is
  //     at the tip at 12.9 cm and the room under it lengthens the front cavity: F3 1555, and F4/F5 pulled down to 3216/3779, which
  //     is what really tells the two apart. Without anatomy.sublingual a curled tip RAISES F3 (1708 -> 2048) and is not an r at all.
  //   weak: hardly rhotic -- the root only a little back, the lips nearly unrounded: F3 2268.
  "ɹ": { organ: "posture", shapeBy: ["rShape", "rStrength"],
         shapes: { weak: { jaw: 9, bodyX: -.25, bodyY: -1, tipX: -2, tipY: -.6, lipH: 1.1, lipP: .35 },
                   bunched: { jaw: 10.3, bodyX: -.31, bodyY: -1.6, tipX: -2.4, tipY: -1, lipH: .86, lipP: .86 },
                   retroflex: { jaw: .7, bodyX: .09, bodyY: -.95, tipX: -.5, tipY: 3, lipH: 1.05, lipP: 1.29 } }, area: 1, voiced: true, ms: 65 },
  "ɾ": { organ: "tip", place: "alveolar", area: 0, voiced: true, ms: 24, tap: true }, r: { organ: "tip", place: "alveolar", area: 0, voiced: true, ms: 85, trill: 27 },
  w: { organ: "body", place: "velar", area: .8, voiced: true, ms: 55, round: 1.1, lipArea: .35 },
  h: { organ: null, voiced: false, ms: 65, breath: .2 }, "ɦ": { organ: null, voiced: true, ms: 55, breath: .06 },
};
// written as two: a stop released into a fricative made at (nearly) the same place
export const AFFRICATES = { "tʃ": ["t", "ʃ"], "dʒ": ["d", "ʒ"], ts: ["t", "s"], dz: ["d", "z"], "tɕ": ["t", "ɕ"], "dʑ": ["d", "ʑ"], "tʂ": ["t", "ʂ"], "dʐ": ["d", "ʐ"], pf: ["p", "f"] };
// a diphthong is a MOVEMENT, and is named after where it starts and where it heads, not after what it reaches: English "ei"
// written [e]->[ɪ] is 400/2100 -> 400/1900, no movement at all and heard as a long i; spoken it opens at 500-550 and closes
// towards i. The second posture is the one AIMED AT -- the glide undershoots it (see the planner).
// a consonant that is let go into a glide when a vowel follows (the glide is a sound of its own in the plan, short)
export const OFFGLIDES = { "ɲ": "j" };
export const DIPHTHONGS = { "aɪ": ["a", "ɪ"], "aʊ": ["a", "ʊ"], "eɪ": ["ɛ", "i"], "oʊ": ["ɔ", "u"], "ɔɪ": ["ɔ", "ɪ"], "ɔʏ": ["ɔ", "ʏ"] };
// other spellings of the same sounds
export const ALIASES = { "ɡ": "g", "ɒ": "ɔ", "ɯ": "ɨ", "ʀ": "ʁ", "ɻ": "ɹ", "ʋ": "v", "ɸ": "f", "c": "k", "ɟ": "g", "ʔ": "" };
export const NASAL_VOWEL_MARK = "̃";
// how each language uses the folds with its voiceless stops: aspirated (the folds still apart at the release) or not
// vowel: this language's own vowel LENGTHS, over timing.vowel (ms: a plain vowel; laxMs + lax: which vowels are the short lax ones and how
// long they are; long: x for a vowel written with the length mark; stressed / unstressed / final: x). Length means different things:
// in English it is mostly the vowel's quality and stress does the lengthening; in Czech, Slovak, Hungarian, Finnish a long vowel is
// TWICE a short one whatever the stress, and stress lengthens nothing; German is in between; Spanish has no length, Italian lengthens
// the stressed vowel, Russian shrinks the unstressed ones.
// flap: American English says a /t/ or /d/ BETWEEN VOWELS, where the vowel after is unstressed, as a single tap of the tongue
// ("water", "a lot of", "what it is"): the number is the effort below which it happens (as timing.assimilate). Without it the two
// t's of "what it is" are two full closures with a 47 ms vowel between them, and the mouth never opens: heard as one long t.
// British English does not have it (it glottalises instead), so `en-GB` leaves it out.
// stress: where a word is stressed when the IPA does not say (no \u02c8 in it) -- the syllable counted from the END (1 = the last), or from
// the START when negative (-1 = the first). Only for the languages whose stress is FIXED and which have no dictionary here to mark it: typed
// as IPA, a Slovak sentence would otherwise be one long row of unstressed syllables, and a row of those is compressed (prosody.phrase.rhythm)
// until every vowel is a third short. A language whose dictionary marks stress (English, German, Spanish ...) must NOT have this: its
// unstressed words are unstressed on purpose.
export const LANGUAGES = {
  // (English: ː is length as everywhere -- beat / bit; the American "not" and "dog" are written with a plain ɑ, only "father" and "calm" with ɑː.
  // And every English vowel is clipped before a voiceless consonant: not / nod, beat / bead. `notLong` is there for a dictionary whose length
  // mark means something else for some vowel.)
  en: { aspirate: .8, flap: 1.1, vowel: { long: 1.4, beforeVoiceless: .78 } }, "en-GB": { aspirate: .8, vowel: { long: 1.5, beforeVoiceless: .75 } }, de: { aspirate: .7, vowel: { long: 1.7, stressed: 1.1, beforeVoiceless: .85 } }, zh: { aspirate: 1, tonal: true },
  fr: { aspirate: 0, vowel: { lax: "ə", stressed: 1.05, final: 1.45 } }, es: { aspirate: 0, vowel: { lax: "", stressed: 1.12, unstressed: .92 } },
  it: { aspirate: 0, vowel: { lax: "", stressed: 1.35, long: 1.5 } }, ru: { aspirate: 0, vowel: { lax: "əɐɪ", stressed: 1.35, unstressed: .7 } },
  pl: { aspirate: 0, vowel: { lax: "", stressed: 1.1 } },
  cs: { aspirate: 0, stress: -1, vowel: { lax: "", long: 1.9, stressed: 1, unstressed: 1, final: 1.15 } }, sk: { aspirate: 0, stress: -1, vowel: { lax: "", long: 1.9, stressed: 1, unstressed: 1, final: 1.15 } },
  hu: { aspirate: 0, stress: -1, vowel: { lax: "", long: 1.9, stressed: 1, unstressed: 1, final: 1.15 } }, fi: { aspirate: 0, stress: -1, vowel: { lax: "", long: 2.1, stressed: 1, unstressed: 1, final: 1.15 } },
};

// IPA -> phones.  ˈ stresses the next vowel, ː lengthens, ʲ palatalises, ʰ aspirates, a tilde nasalises, a digit 1-5 is
// a tone on the syllable just written, a space is a word gap, a comma a pause; *...* is emphasis, (name: ...) a way of
// speaking from PROSODY.styles and plain (...) an aside.
const ASIDE_PAUSE_MS = 130;      // an aside is set off from the sentence around it, as if by commas
export function tokenize(ipa, vowels, lang = "en") {
  const out = []; let stress = false, emph = false, word = 0; const c = [...ipa.normalize("NFC")], styles = [];
  // every phone knows its word, whether it is emphasised (*...*) and which named ways of speaking it stands in ((slow: ...), (...))
  const add = (...ps) => { for (const p of ps) { p.word = word; if (emph) p.emph = true; if (styles.length) p.styles = [...styles]; if (p.kind === "gap" || p.kind === "pause") word++; out.push(p); } };
  const isV = (s) => s in vowels;
  for (let i = 0; i < c.length;) {
    let ch = c[i], two = ch + (c[i + 1] ?? ""), three = two + (c[i + 2] ?? "");
    if (ch === "*") { emph = !emph; i++; continue; }
    if (ch === "(") { const m = c.slice(i, i + 24).join("").match(/^\(([\p{L}]+):/u); const breath = () => { if (out.length && out[out.length - 1].kind !== "pause") add({ kind: "pause", ms: ASIDE_PAUSE_MS }); };
      if (!m) breath(); styles.push(m ? m[1].toLowerCase() : "aside"); i += m ? [...m[0]].length : 1; continue; }
    if (ch === ")") { if (styles.pop() === "aside" && c.slice(i + 1).some((x) => x !== ")" && x !== "*" && x !== " ")) add({ kind: "pause", ms: ASIDE_PAUSE_MS }); i++; continue; }
    if (ch === "ˈ") { stress = true; i++; continue; }
    if (ch === "ˌ" || ch === "." || ch === "‿" || ch === "͡") { i++; continue; }
    if (ch === " ") { add({ kind: "gap" }); i++; continue; }
    if (ch === ",") { add({ kind: "pause", ms: 220 }); i++; continue; }
    if (/[1-5]/.test(ch)) { for (let k = out.length - 1; k >= 0 && out[k].kind !== "gap" && out[k].kind !== "pause" && !out[k].tone; k--) out[k].tone = +ch; i++; continue; }
    if (ch === "ː") { if (out.length) out[out.length - 1].long = true; i++; continue; }
    if (ch === "ʲ") { if (out.length) out[out.length - 1].palatal = true; i++; continue; }
    if (ch === "ʰ") { if (out.length) out[out.length - 1].aspirated = true; i++; continue; }
    if (ch === NASAL_VOWEL_MARK) { if (out.length) out[out.length - 1].nasal = true; i++; continue; }
    const tie = (s) => s.replace("͡", "");
    if (AFFRICATES[tie(three)] && c[i + 1] === "͡") { for (const s of AFFRICATES[tie(three)]) add({ kind: "consonant", sym: s, affricate: true }); i += 3; continue; }
    if (AFFRICATES[two]) { const [a, b] = AFFRICATES[two]; add({ kind: "consonant", sym: a, affricate: 1 }, { kind: "consonant", sym: b, affricate: 2 }); i += 2; continue; }
    if (DIPHTHONGS[two]) { const [a, b] = DIPHTHONGS[two]; add({ kind: "vowel", sym: a, stress, glideTo: b }); stress = false; i += 2; continue; }
    ch = ALIASES[ch] ?? ch; if (ch === "") { i++; continue; }
    if (isV(ch)) { add({ kind: "vowel", sym: ch, stress }); stress = false; }
    else if (CONSONANTS[ch]) { add({ kind: "consonant", sym: ch }); const nx = ALIASES[c[i + 1]] ?? c[i + 1]; if (OFFGLIDES[ch] && (isV(nx) || nx === "ˈ")) add({ kind: "consonant", sym: OFFGLIDES[ch], offglide: true }); }
    i++;
  }
  return out;
}
