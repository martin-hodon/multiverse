# The speech engine as data

Everything `speech.js` knows is a plain object the code reads live, so any of it can be changed at run time,
saved as JSON, and loaded again. `voice_lab.html` is an editor over exactly that; nothing in it is special-cased.

## API

    import { getConfig, setConfig, resetConfig, applyProfile, voiceProfile, CONFIG,
             VOICE_SCHEMA, SWITCH_DOC, MODEL_DOC, PROFILE_FORMAT } from "./speech.js";

    getConfig()                      a deep copy of every section, JSON-safe
    setConfig(patch)                 lay a partial config over the live one
    setConfig(full, {replace:true})  make each given table EXACTLY what was passed (left-out entries are removed)
    resetConfig()                    back to what the file shipped with
    applyProfile(json)  -> key       setConfig + register json.voice as a preset; createSpeaker(ctx, {voice: key})
    voiceProfile("woman")            one preset spelt out in full, as a profile

Bad input is refused with the path that is wrong (`model.pace.measuredRate should be a number, not a string`).
The model's own structure cannot be deleted by a profile; tables keyed by you (phonemes, pairs, words...) can.

## Sections

| section | what it is |
|---|---|
| `voice` (profiles only) | one speaker: the parameters in `VOICE_SCHEMA`. `oq`, `ra`, `rk`, `bwHi`, `airLevel` are derived unless given |
| `switches` | each piece of the model on/off (`SWITCH_DOC`) |
| `model` | ~150 named constants that used to be literals: segment recipes, duration rules, reduction, both intonation models, the tract, the glottal source, the phonation track, consonant levels, the inhale |
| `model.pairs` | **diphone overrides** -- see below |
| `phonemes` | every sound: vowels F1-F3 + ms; consonants place, voicing, closure/VOT, `fric` noise bands `[Hz, bw, gain]` (up to three); nasals `anti` (the antiformant, Hz). Any sonorant may carry `f4`, `f5` (factors on the voice's F4/F5: .92 for a rounded u, .86 for ɹ, 1.06 for i), `bw` (`[B1,B2,B3]` factors on the bandwidth rule) and `zero` (`[Hz, bw]`: a lateral's antiformant; on a fricative, the zero below its hiss) |
| `places` | the locus equations: F2 at a consonant-vowel boundary = `k * F2(vowel) + c`, F3 offset, burst band |
| `languageOverrides` | per language, per symbol: any phoneme field |
| `ipa`, `ipaByLanguage` | IPA -> engine symbols (longest match first) |
| `languages` | per language: prosody and the lexicon (word -> IPA) |
| `moods`, `tones` | per-line multipliers (pitch, range, rate, stress, vol, precision, breath, jitter as factors; tilt and fundamental in dB added; creak as a floor) -- `furious joyful afraid bored sad` are measured on the labelled corpus in `voices/spr08` (see `voice_corpus.js`); Mandarin tone contours |
| `voiceDefaults`, `voices` | the reference voice and the presets laid over it |

## Diphones

This is a rule-based formant synthesiser, not a concatenative one, so it has no recorded diphones. What a
diphone table *does* -- say how one sound moves into the next -- is done here by `places` (a locus equation per
place of articulation) and the segment transition times in `model.segments`. `model.pairs` is the escape hatch
for a single pair where the rule is not good enough:

    "model": { "pairs": { "k>i": { "F2": 2550, "F3": 3000, "transMs": 60 },  "a>n": { "transMs": 70 } } }

`"a>b"` is sound a followed by sound b, in the engine's symbols (see `phonemes`). `F2`/`F3` replace the locus
the vowel is pulled to at that boundary; `transMs` replaces how long the vowel takes over it.

## Profiles

`voices/example.voice.json` is a small one. A profile may carry any subset of the sections; **Export changes** in
the lab writes the voice plus only what differs from the shipped engine, which is the form worth keeping in
version control. `?open=p-model,p-phonemes` opens panels from a link.

Not exposed yet: the scripted vocalisations (laugh, cry, cough, sneeze), which are sequences rather than
parameters, and the two grid constants the renderer is built on (5ms frames, 32kHz).
