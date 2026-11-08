// Animal calls, synthesized -- the world's other voices.
//
// Standalone like speech.js: give it an AudioContext and a species name.
// Three engines (from the creatures lab), each rendering a call offline into
// samples (dsp.js) that play as an AudioBuffer:
//   mammal -- a rough glottal source (pulse per cycle; jitter, shimmer,
//             chaos, a subharmonic, a second voice) through a four-formant
//             mouth that opens and closes, plus pulsed turbulence (roar),
//             nasality and amplitude modulation. Also frogs, crocodiles and
//             quacks: anything that is a throat and a mouth. `voice: 0`
//             leaves only the breath through the mouth (a hiss, a snort).
//   bird   -- the syrinx: FM sines with a couple of harmonics, a second
//             independent voice, trills, and noise syllables for caws.
//   insect -- click trains into a body resonance: chirps, buzzes, drums.
// Every call is a recipe of contours over normalised time; every render is
// a little different (pitch, length, timing, the random source itself), and
// a few renders per species are kept and reused.
//
//   animalCall(ctx, "cow", { dest: gainNode, pitch })  -> ends at (AC seconds)
//   CALLS[species] -> the recipe ({ loud, engine, p }), undefined = silent
//   WILD[name]     -> unseen wildlife (songbirds, crickets...) for the ambience
//   renderCall(name, over) -> Float32Array at SR (one fresh variant)

import { SR, clamp, lerp, rnd, gauss, contour, resonator, bandpass, concat, loudnorm, toBuffer, play } from "./dsp.js";

// ============================================================================
// ENGINE A: mammal. Contours over normalised time: f0 [t, Hz], amp [t, 0-1],
// mouth [t, 0 closed .. 1 open], am [t, depth]. Fc/Fo/Bw: the tract's own
// closed/open formants and bandwidths (default human-like), scaled by
// formantScale (tract size: < 1 bigger than a human, > 1 smaller).
// ============================================================================
const F_CLOSED = [280, 1000, 2400, 3300], F_OPEN = [800, 1350, 2600, 3400], BW = [80, 110, 170, 220];
const pulseAt = (ph) => ph < .4 ? .5 * (1 - Math.cos(Math.PI * ph / .4)) : ph < .6 ? Math.cos(Math.PI * (ph - .4) / .4) : 0;   // Rosenberg glottal pulse
function mammalOne(P) {
  // every repeat its own: a little shorter or longer, a shade higher or lower
  const N = Math.round(P.dur * (.93 + rnd() * .14) * SR), out = new Float32Array(N), pk = .96 + rnd() * .08;
  const casc = [0, 1, 2, 3].map(resonator), nasalPole = resonator(), roarBp = bandpass(50);
  const Fc = P.Fc || F_CLOSED, Fo = P.Fo || F_OPEN, Bw = P.Bw || BW, fs = P.formantScale, voiceG = P.voice ?? 1;
  nasalPole.set(250 * fs, 90); roarBp.set((P.roarFreq || 700) * fs, P.roarBw || 900);
  let phase = 1, period = SR / 200, cycAmp = 1, alt = 0, lastV = 0, phase2 = 0, lastV2 = 0, lp1 = 0, lp2 = 0, lpA = .5, mouth = 0, f0 = 200, gain = 0;
  for (let i = 0; i < N; i++) {
    if ((i & 7) === 0) {   // control rate 4 kHz: pitch, level, mouth and the harmonic lowpass (inaudible steps, 8x fewer contour reads)
      const t = i / N, ts = i / SR;
      f0 = Math.max(10, contour(P.f0, t) * pk);
      if (P.vibDepth > 0) f0 *= Math.pow(2, P.vibDepth / 24 * Math.sin(2 * Math.PI * P.vibRate * ts));
      gain = contour(P.amp, t) * (P.amRate > 0 ? 1 - contour(P.am, t) * (.5 + .5 * Math.cos(2 * Math.PI * P.amRate * ts)) : 1);
      mouth = contour(P.mouth, t);
      for (let f = 0; f < 4; f++) casc[f].set(lerp(Fc[f], Fo[f], mouth) * fs, Bw[f] * (1 + P.chaos * .5));
      // harmonic richness: two-pole lowpass at f0 * harmonics -- the number of strong harmonics (a howl ~3, a roar ~25)
      lpA = Math.exp(-2 * Math.PI * clamp(f0 * P.harmonics, 60, SR * .45) / SR);
    }
    // source: one pulse per cycle; the period is redrawn every cycle (jitter, chaos), the amplitude too
    // (shimmer), and every other cycle is weaker (the subharmonic: period doubling)
    phase += 1 / period;
    if (phase >= 1) {
      phase -= 1; alt ^= 1;
      period = Math.max(2, SR / f0 * (1 + P.jitter / 100 * gauss() + P.chaos * .12 * gauss()));
      cycAmp = (1 + P.shimmer / 100 * gauss()) * (alt ? 1 : 1 - P.subharm * .7) * (1 - P.chaos * .3 * rnd());
    }
    const pulse = pulseAt(phase);
    let voice = (pulse - lastV) * 40 * cycAmp; lastV = pulse;
    if (P.biphon > 0) {   // a second, independent voice (biphonation: the horse's whinny, a hydra's heads)
      phase2 += f0 * P.biphonRatio / SR; if (phase2 >= 1) phase2 -= 1;
      const p2 = pulseAt(phase2); voice += (p2 - lastV2) * 40 * P.biphon; lastV2 = p2;
    }
    lp1 = lpA * lp1 + (1 - lpA) * voice; lp2 = lpA * lp2 + (1 - lpA) * lp1; voice = lp2 * (1 + .5 / Math.max(.05, 1 - lpA));
    const noise = rnd() * 2 - 1;
    let x = voice * voiceG + noise * P.breath * .15;
    if (P.roar > 0) x += roarBp.run(noise) * P.roar * 1.4 * (.3 + .7 * pulse);   // roar: turbulence pulsed by the glottis
    for (let f = 0; f < 4; f++) x = casc[f].run(x);   // the mouth: a cascade of four formants
    if (P.nasal > 0) x = lerp(x, nasalPole.run(x) * 1.2, P.nasal * (1 - mouth * .6));
    out[i] = x * gain;
  }
  return out;
}
function renderMammal(P) {   // repeats: bark-bark, grunt-grunt-grunt, with uneven gaps
  const parts = [];
  for (let r = 0; r < P.repeat; r++) {
    parts.push(mammalOne(P));
    if (r < P.repeat - 1) parts.push(new Float32Array(Math.round(P.gap * (.85 + rnd() * .3) * SR)));
  }
  return concat(parts);
}

// ============================================================================
// ENGINE B: bird (FM sines from a syrinx). A song is a list of syllables,
// repeated `motifs` times. syllable: { type sweep|trill|noise, dur (s), f0
// [t, Hz], trillRate, trillDepth (octaves), h2, h3, level, gap (s), and for
// noise: bw, amRate }.
// ============================================================================
function renderBird(P) {
  const parts = [], ps = Math.pow(2, P.pitch / 12);
  for (let m = 0; m < P.motifs; m++) for (const s of P.syllables) {
    const dur = s.dur / P.speed, N = Math.round(dur * SR), out = new Float32Array(N), bp = bandpass(50);
    const h2 = s.h2 ?? P.h2, h3 = s.h3 ?? P.h3, tr = (s.trillRate || 20) * P.speed, td = s.trillDepth || .15;
    // pitch and envelope at 4 kHz control rate, ramped linearly within each 8-sample block (a stepped FM would buzz)
    const ctl = (i) => {
      const t = Math.min(1, i / N), ts = i / SR, tw = Math.sin(2 * Math.PI * tr * ts);
      let f = contour(s.f0, t) * ps;
      if (s.type === "trill") f *= Math.pow(2, td * tw);
      if (P.vib > 0) f *= Math.pow(2, P.vib / 24 * Math.sin(2 * Math.PI * P.vibRate * ts));
      let e = Math.max(0, Math.min(1, t / .08, (1 - t) / .15)) * (s.type === "trill" ? .6 + .4 * Math.max(0, tw) : 1);
      if (s.type === "noise") e *= .5 + .5 * Math.sin(2 * Math.PI * (s.amRate || 40) * ts);
      return [f, e];
    };
    let ph = 0, ph2 = 0, [fB, eB] = ctl(0), fA = fB, eA = eB;
    for (let i = 0; i < N; i++) {
      if ((i & 7) === 0) { fA = fB; eA = eB; [fB, eB] = ctl(i + 8); }
      const u = (i & 7) / 8, f = fA + (fB - fA) * u, env = eA + (eB - eA) * u;
      let y;
      if (s.type === "noise") {
        if ((i & 7) === 0) bp.set(f, s.bw || 800);
        y = bp.run(rnd() * 2 - 1);
      } else {
        ph += f / SR; if (ph > 1) ph -= 1; const w = 2 * Math.PI * ph;
        y = Math.sin(w) + h2 * Math.sin(2 * w) + h3 * Math.sin(3 * w);
        if (P.voice2 > 0) { ph2 += f * P.voice2Ratio / SR; if (ph2 > 1) ph2 -= 1; y += Math.sin(2 * Math.PI * ph2) * P.voice2; }
        y += (rnd() * 2 - 1) * P.noise * .3;
      }
      out[i] = y * env * (s.level ?? 1);
    }
    parts.push(out, new Float32Array(Math.round((s.gap || .05) / P.speed * (.9 + rnd() * .2) * SR)));
  }
  return concat(parts);
}

// ============================================================================
// ENGINE C: insect (click trains into a body resonance): chirps are pulse
// trains gated at chirpRate, a buzz is a continuous train (wingbeats), a
// chorus is several individuals with spread rates; flyby = approach, pass,
// recede (level and Doppler), wander = the wingbeat drifting.
// ============================================================================
function renderInsect(P) {
  const N = Math.round(P.dur * SR), out = new Float32Array(N);
  for (let c = 0; c < P.chorus; c++) {
    const rate = P.clickRate * (1 + (c ? (P.chorusSpread / 100) * gauss() * .5 : 0)), res = resonator(), bp = bandpass(50);
    res.set(P.resFreq * (1 + (c ? .03 * gauss() : 0)), P.resBw); bp.set(P.resFreq, P.resBw * 3);
    let nextClick = rnd() * SR / rate;
    const lvl = .6 + .4 * rnd(), offset = rnd() * SR, w1 = rnd() * 6.28, w2 = rnd() * 6.28, wr = P.wanderRate || 1, wander = (P.wander || 0) / 100;
    const flyby = P.flyby || 0, passAt = .35 + .3 * rnd();   // where in the clip the insect is nearest
    const chirpPeriod = SR / P.chirpRate, pulseLen = P.pulseLen / 1000 * SR, pulseGap = P.pulseGap / 1000 * SR;
    const trainLen = P.pulsesPerChirp * (pulseLen + pulseGap), continuous = trainLen >= chirpPeriod;   // a train that fills the period = continuous sound
    let rateK = 1, g = 0;
    for (let i = 0; i < N; i++) {
      if ((i & 15) === 0) {   // control rate 2 kHz: the wingbeat wanders (flight manoeuvres) and shifts with a fly-by's Doppler; loudness follows distance
        const tt = i / N, ts = i / SR;
        const drift = 1 + wander * (.6 * Math.sin(2 * Math.PI * wr * ts + w1) + .4 * Math.sin(2 * Math.PI * wr * 2.3 * ts + w2));
        const doppler = 1 + flyby * .04 * Math.tanh((passAt - tt) * 8), near = flyby > 0 ? lerp(1, Math.exp(-Math.pow((tt - passAt) / .22, 2)) + .08, flyby) : 1;
        const am = P.amRate > 0 ? 1 - P.amDepth * (.5 + .5 * Math.cos(2 * Math.PI * P.amRate * ts + c)) : 1;
        rateK = drift * doppler; g = am * near * lvl / Math.sqrt(P.chorus);
      }
      const tc = (i + offset) % chirpPeriod, inTrain = continuous || (tc < trainLen && ((tc % (pulseLen + pulseGap)) < pulseLen));
      let x = 0;
      if (inTrain && i >= nextClick) { x = 1; nextClick = i + SR / (rate * rateK) * (1 + P.clickJitter / 100 * gauss()); }
      out[i] += (res.run(x) * 14 + bp.run(inTrain ? (rnd() * 2 - 1) * P.noise * .4 : 0)) * g;
    }
  }
  return out;
}
const ENGINES = { mammal: renderMammal, bird: renderBird, insect: renderInsect };

// the individual's variant: every render a shade higher or lower, faster or slower
const scaleF0 = (pts, k) => pts.map(([t, v]) => [t, v * k]);
const VARY = {
  mammal: (P) => ({ ...P, f0: scaleF0(P.f0, .95 + rnd() * .1) }),
  bird: (P) => ({ ...P, pitch: P.pitch + (rnd() - .5) * 1.2, speed: P.speed * (.94 + rnd() * .12) }),
  insect: (P) => ({ ...P, clickRate: P.clickRate * (.96 + rnd() * .08), resFreq: P.resFreq * (.97 + rnd() * .06), chirpRate: P.chirpRate * (.9 + rnd() * .2) }),
};

// ============================================================================
// RECIPES. Defaults per engine; a recipe lists what differs. `loud` says how
// far a call carries (index.html scales its reach by it), `p` is the preset
// (or a list of presets picked at random per render: a pig mostly oinks and
// sometimes squeals). Loudness at the source is normalised per render.
// ============================================================================
const MAM = { dur: .5, formantScale: 1, harmonics: 10, breath: .15, jitter: 2, shimmer: 5, subharm: 0, chaos: .1, biphon: 0, biphonRatio: 1.5,
  vibRate: 0, vibDepth: 0, amRate: 0, nasal: 0, roar: 0, roarFreq: 700, roarBw: 900, repeat: 1, gap: .3, voice: 1,
  f0: [[0, 200], [1, 200]], amp: [[0, 0], [.1, 1], [.8, .8], [1, 0]], mouth: [[0, .5], [1, .5]], am: [[0, 0], [1, 0]] };
const BIRD = { motifs: 1, speed: 1, pitch: 0, h2: .2, h3: .05, vib: 0, vibRate: 10, noise: .05, voice2: 0, voice2Ratio: 1.5 };
const BUG = { dur: 4, clickRate: 200, clickJitter: 0, resFreq: 4000, resBw: 500, pulseLen: 200, pulsesPerChirp: 12, pulseGap: 10, chirpRate: .4,
  amRate: 0, amDepth: 0, chorus: 1, chorusSpread: 0, noise: .1, wander: 0, wanderRate: 1, flyby: 0 };
const recipe = (engine, D) => (loud, p, extra) => ({ loud, engine, p: Array.isArray(p) ? p.map((q) => ({ ...D, ...q })) : { ...D, ...p }, ...extra });
const mammal = recipe("mammal", MAM), bird = recipe("bird", BIRD), insect = recipe("insect", BUG);

// ---- the lab's measured presets, shared by several species ----
// meow: pitch rises then falls while the mouth opens and closes (the ee-a-ow is the F1 track)
const MEOW = { dur: .75, formantScale: 1.9, harmonics: 9, Fc: [300, 1100, 2500, 3400], Fo: [750, 1500, 2700, 3500], breath: .15, jitter: 1.5, shimmer: 5, subharm: .1, chaos: .05, nasal: .35,
  f0: [[0, 430], [.3, 760], [.6, 700], [1, 400]], amp: [[0, 0], [.12, 1], [.75, .85], [1, 0]], mouth: [[0, .1], [.35, .95], [.75, .6], [1, .05]] };
// moo: low pitch rising slowly; a hummy, nasal, mouth-closed start, subharmonic roughness in the open middle
const MOO = { dur: 2.2, formantScale: .6, harmonics: 5, Fc: [220, 650, 1500, 2500], Fo: [480, 950, 1800, 2600], Bw: [70, 120, 200, 260], roarFreq: 500, roarBw: 600, breath: .1, jitter: 2, shimmer: 6,
  subharm: .5, chaos: .1, nasal: .75, roar: .15, f0: [[0, 80], [.35, 135], [.7, 125], [1, 85]], amp: [[0, 0], [.15, .8], [.45, 1], [.85, .7], [1, 0]], mouth: [[0, .05], [.4, .85], [.85, .5], [1, .05]] };
// bleat: the stutter is fast amplitude modulation (~28 Hz), not vibrato
const BLEAT = { dur: 1, formantScale: 1.05, harmonics: 13, Fc: [420, 1150, 2200, 3200], Fo: [700, 1600, 2500, 3300], breath: .15, jitter: 2, shimmer: 5, subharm: .2, chaos: .1, amRate: 28, nasal: .7,
  f0: [[0, 210], [.4, 300], [1, 190]], amp: [[0, 0], [.1, 1], [.8, .9], [1, 0]], mouth: [[0, .3], [.3, .7], [1, .4]], am: [[0, .75], [1, .75]] };
// whinny: very high for a big animal, fast wide vibrato, a second voice and chaos, ending in a pulsed nicker
const WHINNY = { dur: 1.7, formantScale: .55, harmonics: 10, Fc: [350, 1000, 2100, 3000], Fo: [700, 1300, 2300, 3100], breath: .2, jitter: 1.5, shimmer: 6, subharm: .3, chaos: .25, biphon: .35, biphonRatio: 1.37,
  vibRate: 14, vibDepth: 5, amRate: 9, nasal: .3, roar: .1, f0: [[0, 650], [.15, 1500], [.5, 1250], [.75, 500], [1, 280]], amp: [[0, 0], [.1, 1], [.7, .8], [1, 0]],
  mouth: [[0, .5], [.4, .8], [1, .3]], am: [[0, 0], [.68, 0], [.74, .7], [1, .85]] };
// bark: short, explosive, hoarse -- fast attack, pitch peaking early, chaos and subharmonic
const BARK = { dur: .22, formantScale: 1.1, harmonics: 18, Fc: [350, 1000, 2300, 3300], Fo: [800, 1400, 2500, 3400], roarFreq: 1200, roarBw: 1500, breath: .25, jitter: 2, shimmer: 8, subharm: .35, chaos: .4,
  nasal: .1, roar: .25, repeat: 3, gap: .28, f0: [[0, 300], [.2, 620], [.5, 520], [1, 280]], amp: [[0, 0], [.06, 1], [.5, .7], [1, 0]], mouth: [[0, .3], [.2, 1], [1, .4]] };
// howl: long, smooth, harmonic -- little jitter, slow gentle vibrato, rising to a plateau and sliding down
const HOWL = { dur: 3.6, formantScale: .85, harmonics: 3, Fc: [380, 900, 2200, 3200], Fo: [600, 1100, 2400, 3300], Bw: [60, 90, 150, 200], breath: .2, jitter: .4, shimmer: 1.5, chaos: .01,
  vibRate: 4.5, vibDepth: .7, nasal: .15, f0: [[0, 240], [.18, 540], [.65, 500], [1, 290]], amp: [[0, 0], [.15, .9], [.5, 1], [.9, .6], [1, 0]], mouth: [[0, .3], [.2, .55], [.7, .35], [1, .15]] };
// roar: huge tract, low pitch, chaos, subharmonic and pulsed noise; the 12 Hz AM is the roar's staccato
const LION_TRACT = { Fc: [220, 550, 1300, 2200], Fo: [520, 950, 1600, 2400], Bw: [90, 140, 220, 280] };
const ROAR = { dur: 1.9, formantScale: .5, harmonics: 28, ...LION_TRACT, roarFreq: 800, roarBw: 1400, breath: .2, jitter: 5, shimmer: 15, subharm: .7, chaos: .7, biphon: .2, biphonRatio: 1.42, amRate: 12,
  nasal: .05, roar: .9, f0: [[0, 80], [.3, 140], [.6, 120], [1, 55]], amp: [[0, 0], [.1, 1], [.7, .9], [1, 0]], mouth: [[0, .4], [.3, 1], [.8, .7], [1, .3]], am: [[0, .2], [.4, .35], [1, .3]] };
// squeak: a tiny tract and a very high thin pitch (3-6 kHz, the audible part of a rat)
const SQUEAK = { dur: .14, formantScale: 3.2, harmonics: 4, Fc: [400, 1200, 2600, 3500], Fo: [700, 1500, 2800, 3600], breath: .1, jitter: 1, shimmer: 4, chaos: .05, repeat: 3, gap: .12,
  f0: [[0, 3400], [.4, 5600], [1, 3000]], amp: [[0, 0], [.15, 1], [.7, .8], [1, 0]] };
// roe deer alarm bark: like a dog's from a slightly smaller tract, repeated at long intervals
const ROE = { dur: .18, formantScale: .9, harmonics: 16, breath: .25, jitter: 2, shimmer: 8, subharm: .3, chaos: .4, nasal: .1, roar: .3, roarFreq: 1200, roarBw: 1500, repeat: 3, gap: .65,
  Fc: [350, 1000, 2300, 3300], Fo: [800, 1400, 2500, 3400], f0: [[0, 400], [.15, 700], [.5, 600], [1, 350]], amp: [[0, 0], [.06, 1], [.5, .7], [1, 0]], mouth: [[0, .3], [.2, 1], [1, .4]] };
// wild boar: a run of short, very rough, nasal grunts; the mouth barely opens
const GRUNTS = { dur: .28, formantScale: .75, harmonics: 18, breath: .2, jitter: 4, shimmer: 12, subharm: .5, chaos: .45, nasal: .6, roar: .4, roarFreq: 600, roarBw: 900, repeat: 4, gap: .22,
  Fc: [250, 800, 1800, 2700], Fo: [500, 1100, 2000, 2800], f0: [[0, 110], [.3, 150], [1, 95]], amp: [[0, 0], [.1, 1], [.6, .8], [1, 0]], mouth: [[0, .1], [.3, .5], [1, .1]] };
// the domestic pig: the grunt rises into a nasal "oink"; the squeal is piercing and unstable
const OINK = { dur: .35, formantScale: .85, harmonics: 14, breath: .15, jitter: 3, shimmer: 8, subharm: .3, chaos: .3, nasal: .7, roar: .25, roarBw: 1000, repeat: 2, gap: .4,
  Fc: [280, 850, 1900, 2800], Fo: [550, 1150, 2100, 2900], f0: [[0, 120], [.5, 200], [1, 140]], amp: [[0, 0], [.1, .9], [.5, 1], [1, 0]], mouth: [[0, .1], [.4, .7], [1, .2]] };
const SQUEAL = { dur: 1.2, formantScale: .85, harmonics: 12, breath: .15, jitter: 3, shimmer: 10, subharm: .35, chaos: .5, biphon: .3, biphonRatio: 1.3, nasal: .2, roar: .3, roarFreq: 2500, roarBw: 1500,
  Fc: [400, 1100, 2300, 3200], Fo: [800, 1500, 2600, 3400], f0: [[0, 900], [.2, 2200], [.6, 2000], [1, 1200]], amp: [[0, 0], [.08, 1], [.8, .9], [1, 0]], mouth: [[0, .5], [.3, .9], [1, .4]] };

// a quack: a buzzy, very nasal voice through a small bright mouth that snaps open and shut (the duck; the goose's honk from it)
const QUACK = { dur: .18, formantScale: 1.5, harmonics: 30, Fc: [500, 1400, 2500, 3400], Fo: [800, 1700, 2700, 3500], breath: .2, jitter: 3, shimmer: 8, subharm: .2, chaos: .25, nasal: .85, roar: .2, roarFreq: 1500,
  repeat: 4, gap: .12, f0: [[0, 240], [.3, 300], [1, 220]], amp: [[0, 0], [.06, 1], [.6, .8], [1, 0]], mouth: [[0, .3], [.25, .9], [1, .3]] };
export const CALLS = {
  // ---- farm ----
  cow:      mammal(1.4, MOO),
  ox:       mammal(1.5, { ...MOO, dur: 2.5, formantScale: .52, subharm: .6, roar: .25, f0: [[0, 62], [.35, 108], [.7, 98], [1, 66]] }),   // bigger, lower, rougher
  sheep:    mammal(1, BLEAT),
  pig:      mammal(.9, [OINK, OINK, OINK, SQUEAL]),
  horse:    mammal(1.3, WHINNY),
  dog:      mammal(1.2, BARK),
  cat:      mammal(.6, MEOW),
  // a cluck series, then "ba-GAWK": clucks are short buzzy notes with strong harmonics
  chicken:  bird(.7, { h2: .8, h3: .6, noise: .35, voice2: .25, voice2Ratio: 1.41, vib: .4, vibRate: 30,
    syllables: [{ type: "sweep", dur: .07, f0: [[0, 520], [1, 420]], gap: .16 }, { type: "sweep", dur: .06, f0: [[0, 500], [1, 410]], gap: .22 }, { type: "sweep", dur: .07, f0: [[0, 540], [1, 430]], gap: .14 },
      { type: "sweep", dur: .1, f0: [[0, 600], [1, 650]], gap: .03 }, { type: "sweep", dur: .38, f0: [[0, 700], [.25, 1150], [1, 800]], h2: .7, gap: .3 }] }),
  // the rooster at dawn: "cock-a-doodle-DOO" -- two clipped notes, a rising run, and the long held last one, wavering
  rooster:  bird(1.6, { h2: .9, h3: .7, noise: .3, voice2: .3, voice2Ratio: 1.41, vib: .6, vibRate: 7,
    syllables: [{ type: "sweep", dur: .1, f0: [[0, 620], [1, 560]], gap: .06 }, { type: "sweep", dur: .08, f0: [[0, 560], [1, 700]], gap: .04 },
      { type: "sweep", dur: .16, f0: [[0, 760], [1, 980]], gap: .05 }, { type: "sweep", dur: .75, f0: [[0, 1000], [.15, 1120], [.8, 1040], [1, 760]], h2: .8, gap: .4 }] }),
  duck:     mammal(.9, QUACK),
  // a goose's honk overhead (geese.js): the quack's nasal voice, longer, higher and rising -- "aahng, aahng"
  goose:    mammal(2, { ...QUACK, dur: .26, formantScale: 1.3, nasal: .9, repeat: 2, gap: .22, f0: [[0, 330], [.3, 430], [1, 340]], mouth: [[0, .3], [.2, 1], [.8, .8], [1, .3]] }),
  // ---- wild mammals ----
  wolf:     mammal(1.6, HOWL),
  // a fox: a hoarse, high "wow-wow-wow" that cracks upward
  fox:      mammal(1.1, { dur: .22, formantScale: 1.5, harmonics: 16, breath: .3, jitter: 3, shimmer: 10, subharm: .3, chaos: .45, roar: .3, roarFreq: 1800, roarBw: 1500, repeat: 3, gap: .35,
    f0: [[0, 500], [.25, 1100], [1, 650]], amp: [[0, 0], [.08, 1], [.6, .7], [1, 0]], mouth: [[0, .3], [.3, 1], [1, .3]] }),
  deer:     mammal(1.1, ROE),
  boar:     mammal(1.1, GRUNTS),
  // a bear: a throaty growl-roar, low, chesty, very rough and nasal, no staccato
  bear:     mammal(1.7, { dur: 1.6, formantScale: .6, harmonics: 24, Fc: [260, 700, 1600, 2500], Fo: [560, 1050, 1800, 2600], breath: .25, jitter: 5, shimmer: 14, subharm: .7, chaos: .65, roar: .6, roarFreq: 600, roarBw: 900,
    nasal: .15, f0: [[0, 60], [.3, 100], [.7, 85], [1, 55]], amp: [[0, 0], [.12, 1], [.8, .9], [1, 0]], mouth: [[0, .2], [.35, .8], [.8, .5], [1, .15]] }),
  // a beaver kit's nasal whine (the adults mostly slap their tails)
  beaver:   mammal(.4, { dur: .45, formantScale: 1.8, harmonics: 8, nasal: .7, breath: .25, jitter: 1.5, repeat: 2, gap: .35, f0: [[0, 650], [.4, 900], [1, 600]], mouth: [[0, .2], [.4, .6], [1, .2]] }),
  // a hedgehog snuffles: breath only, short puffs through a tiny nose, pulsed turbulence
  hedgehog: mammal(.3, { voice: 0, breath: 1, formantScale: 2.4, roar: .7, roarFreq: 2500, roarBw: 2000, dur: .09, repeat: 6, gap: .07, f0: [[0, 25], [1, 25]], amp: [[0, 0], [.2, 1], [1, 0]], mouth: [[0, .3], [1, .3]] }),
  rat:      mammal(.4, SQUEAK),
  // a bat's audible social squeaks: higher and faster than the rat's, a thin tiny tract
  bat:      mammal(.3, { dur: .035, formantScale: 3.5, harmonics: 3, breath: .05, jitter: 1, chaos: .05, repeat: 5, gap: .06, f0: [[0, 8000], [.3, 10500], [1, 7000]], amp: [[0, 0], [.2, 1], [1, 0]] }),
  // a spotted hyena (2026-11-05): mostly the WHOOP -- a smooth, hollow "whoo-OOP" sliding up an octave and more, carried far
  // -- and now and then the GIGGLE, a fast run of harsh high "hee-hee-hee" yelps
  hyena:    mammal(1.9, [
    { dur: 1.5, formantScale: .8, harmonics: 4, Fc: [330, 800, 2200, 3200], Fo: [520, 1000, 2400, 3300], Bw: [60, 90, 150, 200], breath: .15, jitter: .6, shimmer: 2, chaos: .02,
      f0: [[0, 170], [.45, 300], [.8, 560], [1, 380]], amp: [[0, 0], [.2, .55], [.78, 1], [1, 0]], mouth: [[0, .15], [.6, .55], [.85, .9], [1, .3]] },
    { dur: 1.3, formantScale: .78, harmonics: 4, Fc: [330, 800, 2200, 3200], Fo: [520, 1000, 2400, 3300], Bw: [60, 90, 150, 200], breath: .15, jitter: .6, shimmer: 2, chaos: .02,
      f0: [[0, 190], [.5, 340], [.85, 620], [1, 420]], amp: [[0, 0], [.2, .6], [.8, 1], [1, 0]], mouth: [[0, .15], [.6, .6], [.85, .9], [1, .3]] },
    { dur: .1, formantScale: 1.25, harmonics: 12, breath: .3, jitter: 3, shimmer: 10, subharm: .25, chaos: .35, roar: .2, roarFreq: 1500, repeat: 9, gap: .045,
      f0: [[0, 720], [.4, 980], [1, 640]], amp: [[0, 0], [.15, 1], [.7, .6], [1, 0]], mouth: [[0, .4], [.35, 1], [1, .35]] }]),
  // an impala's alarm SNORT -- breath only, a sharp burst through the nose -- and the ram's rutting bark, a rough grunting cough
  impala:   mammal(1.3, [
    { voice: 0, breath: 1, formantScale: .9, roar: .7, roarFreq: 1400, roarBw: 1800, dur: .16, repeat: 1, f0: [[0, 40], [1, 30]], amp: [[0, 0], [.04, 1], [.4, .55], [1, 0]], mouth: [[0, .9], [1, .4]] },
    { voice: 0, breath: 1, formantScale: .9, roar: .7, roarFreq: 1300, roarBw: 1800, dur: .13, repeat: 2, gap: .22, f0: [[0, 40], [1, 30]], amp: [[0, 0], [.04, 1], [.4, .5], [1, 0]], mouth: [[0, .9], [1, .4]] },
    { ...ROE, dur: .2, formantScale: .85, roar: .45, repeat: 4, gap: .3, f0: [[0, 170], [.3, 230], [1, 120]] }]),
  // a capybara: chattering CLICKS of the teeth (short dry bursts), a high thin WHISTLE, a low purring grunt
  capybara: mammal(1, [
    { voice: 0, breath: 1, formantScale: 2.2, roar: .8, roarFreq: 3200, roarBw: 2500, dur: .018, repeat: 9, gap: .075, f0: [[0, 30], [1, 30]], amp: [[0, 0], [.1, 1], [1, 0]], mouth: [[0, .5], [1, .5]] },
    { dur: .55, formantScale: 2.6, harmonics: 2, breath: .08, jitter: .5, shimmer: 1, chaos: .01, f0: [[0, 1500], [.4, 2100], [1, 1650]], amp: [[0, 0], [.15, 1], [.8, .8], [1, 0]], mouth: [[0, .6], [1, .6]] },
    { ...GRUNTS, formantScale: .9, nasal: .7, roar: .2, dur: .16, repeat: 6, gap: .09, f0: [[0, 110], [.5, 140], [1, 100]] }]),
  // a skunk: hisses and huffs, the forefeet stamping -- breath only; a pangolin hisses and snuffles; a giant anteater
  // keeps quiet but for a snorting huff (and a bellow when cornered)
  skunk:    mammal(.4, { voice: 0, breath: 1, formantScale: 2.4, roar: .7, roarFreq: 3500, roarBw: 3000, dur: .35, repeat: 2, gap: .25, f0: [[0, 30], [1, 30]], amp: [[0, 0], [.1, 1], [.7, .6], [1, 0]], mouth: [[0, .6], [1, .4]] }),
  pangolin: mammal(.4, { voice: 0, breath: 1, formantScale: 2.2, roar: .7, roarFreq: 2800, roarBw: 2500, dur: .5, repeat: 1, f0: [[0, 25], [1, 25]], amp: [[0, 0], [.2, 1], [.8, .7], [1, 0]], mouth: [[0, .3], [1, .3]] }),
  // a badger (2026-11-06): quiet mostly -- low rough GRUNTS as it snuffles about, and the soft rapid PURR (a throaty
  // trill, pulsed some 24 times a second); a least weasel: a short high TRILL, a quick run of chirps, or a harsh CHITTER
  badger:   mammal(.8, [
    { ...GRUNTS, formantScale: 1, nasal: .5, roar: .35, dur: .14, repeat: 5, gap: .12, f0: [[0, 140], [.4, 170], [1, 120]] },
    { dur: .9, formantScale: 1.1, harmonics: 10, breath: .3, jitter: 3, shimmer: 8, subharm: .3, chaos: .3, nasal: .4, amRate: 24, am: [[0, .6], [1, .6]],
      f0: [[0, 110], [.5, 130], [1, 100]], amp: [[0, 0], [.1, .8], [.8, .7], [1, 0]], mouth: [[0, .2], [1, .2]] }]),
  weasel:   mammal(.3, [
    { ...SQUEAK, dur: .04, formantScale: 3.6, repeat: 7, gap: .03, f0: [[0, 4200], [.5, 5000], [1, 3900]] },
    { ...SQUEAK, dur: .07, formantScale: 3.4, chaos: .3, breath: .3, repeat: 4, gap: .05, f0: [[0, 3000], [.4, 3800], [1, 2600]] }]),
  // (2026-11-06) a lynx: mostly silent -- a spitting HISS when cornered, and in the rut a long low moaning YOWL, far
  // deeper and rougher than a house cat's; a chamois: the alarm WHISTLE, a sharp hissing whistle through the nose;
  // a red panda: high SQUEAKS and a soft twittering "huff-quack" run; a giant panda: a goat-like BLEAT, and a low honk;
  // a porcupine: grunts, and the dry RATTLE of its quills shaken in warning (breath only)
  lynx:     mammal(1, [
    { voice: 0, breath: 1, formantScale: 1.6, roar: .7, roarFreq: 3000, roarBw: 3500, dur: .6, repeat: 1, f0: [[0, 30], [1, 30]], amp: [[0, 0], [.05, 1], [.7, .7], [1, 0]], mouth: [[0, .7], [1, .5]] },
    { ...MEOW, dur: 1.8, formantScale: 1.15, harmonics: 14, breath: .3, jitter: 3, shimmer: 9, subharm: .35, chaos: .3, nasal: .25, vibRate: 5, vibDepth: 1.2,
      f0: [[0, 240], [.25, 380], [.6, 330], [1, 200]], amp: [[0, 0], [.15, .9], [.8, 1], [1, 0]], mouth: [[0, .1], [.3, .9], [.8, .7], [1, .1]] }]),
  chamois:  mammal(1, [
    { voice: 0, breath: 1, formantScale: 1.8, roar: .8, roarFreq: 3200, roarBw: 900, dur: .55, repeat: 1, f0: [[0, 40], [1, 30]], amp: [[0, 0], [.05, 1], [.6, .6], [1, 0]], mouth: [[0, .2], [1, .2]] },
    { dur: .5, formantScale: 2.4, harmonics: 2, breath: .5, jitter: .5, shimmer: 2, chaos: .02, repeat: 2, gap: .5, f0: [[0, 2600], [.3, 2900], [1, 2300]], amp: [[0, 0], [.05, 1], [.7, .6], [1, 0]], mouth: [[0, .3], [1, .3]] }]),
  redpanda: mammal(.4, [
    { ...SQUEAK, dur: .09, formantScale: 3, repeat: 5, gap: .07, f0: [[0, 2600], [.4, 3400], [1, 2400]] },
    { ...SQUEAK, dur: .05, formantScale: 2.8, chaos: .2, breath: .35, repeat: 8, gap: .04, f0: [[0, 1900], [.5, 2400], [1, 1800]] }]),
  giantpanda: mammal(1.4, [
    { ...BLEAT, dur: .8, formantScale: .9, f0: [[0, 260], [.4, 340], [1, 220]] },
    { ...BLEAT, dur: .4, formantScale: .8, amRate: 0, nasal: .8, repeat: 2, gap: .3, f0: [[0, 180], [.5, 210], [1, 160]] }]),
  porcupine: mammal(.6, [
    { ...GRUNTS, formantScale: 1.4, nasal: .5, dur: .1, repeat: 4, gap: .14, f0: [[0, 220], [.5, 260], [1, 200]] },
    { voice: 0, breath: 1, formantScale: 2, roar: .9, roarFreq: 4500, roarBw: 4000, amRate: 30, am: [[0, .9], [1, .9]], dur: .9, repeat: 1, f0: [[0, 30], [1, 30]], amp: [[0, 0], [.1, 1], [.8, .8], [1, 0]], mouth: [[0, .5], [1, .5]] }]),
  anteater: mammal(.7, [
    { voice: 0, breath: 1, formantScale: 1, roar: .7, roarFreq: 1100, roarBw: 1500, dur: .25, repeat: 2, gap: .3, f0: [[0, 30], [1, 30]], amp: [[0, 0], [.08, 1], [.5, .6], [1, 0]], mouth: [[0, .6], [1, .3]] },
    { dur: .9, formantScale: .75, harmonics: 18, breath: .4, jitter: 4, shimmer: 12, subharm: .5, chaos: .5, roar: .45, roarFreq: 700, nasal: .4, f0: [[0, 120], [.3, 170], [1, 90]], mouth: [[0, .2], [.4, .7], [1, .2]] }]),
  // ---- savanna ----
  lion:     mammal(2.2, ROAR),
  // a tiger: one continuous rough "aaunngh" -- the lion's tract, a touch smaller, no staccato pulsing
  tiger:    mammal(2, { ...ROAR, dur: 1.5, formantScale: .55, harmonics: 22, Fc: [240, 600, 1350, 2250], Fo: [560, 1000, 1650, 2450], roarFreq: 700, roarBw: 1100, breath: .25, jitter: 4, shimmer: 12, subharm: .6,
    chaos: .55, biphon: .1, amRate: 0, roar: .7, f0: [[0, 95], [.25, 150], [.6, 130], [1, 70]], amp: [[0, 0], [.08, 1], [.75, .85], [1, 0]], mouth: [[0, .5], [.25, 1], [.8, .6], [1, .2]] }),
  // a trumpet: a blaring, rattling blast -- a trunk's high bright resonances, a second voice, a ~38 Hz rattle
  elephant: mammal(2.4, { dur: 1.4, formantScale: 1, Fc: [500, 1300, 2600, 3600], Fo: [900, 1800, 3000, 4000], harmonics: 30, breath: .3, jitter: 3, shimmer: 8, subharm: .2, chaos: .35, biphon: .35,
    roar: .5, roarFreq: 2500, roarBw: 2000, amRate: 38, am: [[0, .2], [1, .3]], vibRate: 6, vibDepth: .8, f0: [[0, 420], [.2, 780], [.6, 720], [1, 480]], amp: [[0, 0], [.06, 1], [.8, .9], [1, 0]],
    mouth: [[0, .6], [.3, 1], [1, .7]] }),
  // a hippo: a run of wheezing honks from a huge chest, nasal and rough
  hippo:    mammal(1.8, { dur: .32, formantScale: .45, harmonics: 18, breath: .35, jitter: 4, shimmer: 12, subharm: .6, chaos: .55, roar: .5, roarFreq: 600, nasal: .5, repeat: 5, gap: .18,
    f0: [[0, 80], [.3, 140], [1, 70]], amp: [[0, 0], [.1, 1], [.7, .8], [1, 0]], mouth: [[0, .3], [.3, .9], [1, .3]] }),
  // a zebra brays in rough breathy "kwa-ha" pairs, a barking donkey
  zebra:    mammal(1.3, { dur: .2, formantScale: .9, harmonics: 20, breath: .5, jitter: 3, shimmer: 10, subharm: .4, chaos: .5, biphon: .25, biphonRatio: 1.6, roar: .4, roarFreq: 1500, roarBw: 1500, repeat: 5, gap: .14,
    f0: [[0, 420], [.3, 640], [1, 360]], amp: [[0, 0], [.05, 1], [.6, .7], [1, 0]], mouth: [[0, .3], [.25, 1], [1, .4]] }),
  // a giraffe mostly keeps quiet; it snorts: breath only, through a long throat, pulsed
  giraffe:  mammal(.5, { voice: 0, breath: 1, formantScale: .5, roar: .6, roarFreq: 900, roarBw: 1500, dur: .45, repeat: 2, gap: .25, f0: [[0, 40], [1, 30]], amp: [[0, 0], [.05, 1], [.4, .6], [1, 0]], mouth: [[0, .8], [1, .3]] }),
  // a camel: a gurgling, bellowing groan (the gurgle is a slow ~9 Hz AM)
  camel:    mammal(1.4, { dur: 1.6, formantScale: .6, harmonics: 16, breath: .3, jitter: 4, shimmer: 12, subharm: .5, chaos: .45, roar: .35, roarFreq: 500, roarBw: 700, nasal: .45, amRate: 9,
    f0: [[0, 110], [.3, 165], [.7, 140], [1, 90]], mouth: [[0, .2], [.4, .9], [1, .3]], am: [[0, .1], [.3, .45], [1, .3]] }),
  bactrian: mammal(1.4, { dur: 2, formantScale: .55, harmonics: 16, breath: .3, jitter: 4, shimmer: 12, subharm: .55, chaos: .5, roar: .35, roarFreq: 450, roarBw: 700, nasal: .5, amRate: 7,
    f0: [[0, 95], [.3, 140], [.7, 120], [1, 75]], mouth: [[0, .2], [.4, .9], [1, .3]], am: [[0, .15], [.3, .5], [1, .35]] }),
  // ---- water ----
  // a crocodile bellows: a very low, near-infrasonic rumble, pulsed, with a huge subharmonic
  crocodile:mammal(1.6, { dur: 1.8, formantScale: .4, harmonics: 12, Fc: [200, 550, 1300, 2200], Fo: [420, 850, 1500, 2400], breath: .2, jitter: 5, shimmer: 14, subharm: .85, chaos: .6, roar: .45, roarFreq: 400, roarBw: 600,
    amRate: 11, am: [[0, .4], [1, .5]], nasal: .3, f0: [[0, 38], [.3, 52], [1, 34]], amp: [[0, 0], [.15, 1], [.8, .9], [1, 0]], mouth: [[0, .2], [.4, .6], [1, .2]] }),
  // a tyrannosaur: no roar (archosaurs boom with the mouth shut, like a crocodile or an ostrich) -- a huge
  // closed-mouth rumble, very low and rough, swelling and dying away
  tyrannosaur: mammal(2.4, { dur: 2.6, formantScale: .3, harmonics: 30, ...LION_TRACT, Bw: [110, 170, 260, 320], breath: .3, jitter: 6, shimmer: 16, subharm: .9, chaos: .7,
    roar: .55, roarFreq: 350, roarBw: 700, nasal: .35, amRate: 8, am: [[0, .3], [1, .5]], f0: [[0, 34], [.3, 58], [.7, 50], [1, 28]],
    amp: [[0, 0], [.12, 1], [.8, .9], [1, 0]], mouth: [[0, .15], [.4, .5], [1, .1]] }),
  // a carnotaurus: the tyrannosaur's closed-mouth boom, smaller and rougher -- a shorter, deeper-pulsed growl from a
  // short deep head
  carnotaurus: mammal(2.1, { dur: 1.9, formantScale: .38, harmonics: 26, ...LION_TRACT, Bw: [110, 170, 260, 320], breath: .32, jitter: 7, shimmer: 18, subharm: .8, chaos: .75,
    roar: .5, roarFreq: 420, roarBw: 750, nasal: .3, amRate: 13, am: [[0, .35], [1, .55]], f0: [[0, 44], [.3, 74], [.7, 62], [1, 36]],
    amp: [[0, 0], [.1, 1], [.75, .85], [1, 0]], mouth: [[0, .15], [.4, .55], [1, .1]] }),
  // an allosaurus: a boom between the two, longer and smoother than the carnotaur's
  allosaurus: mammal(2.2, { dur: 2.2, formantScale: .35, harmonics: 28, ...LION_TRACT, Bw: [110, 170, 260, 320], breath: .3, jitter: 5, shimmer: 14, subharm: .75, chaos: .6,
    roar: .5, roarFreq: 380, roarBw: 700, nasal: .35, amRate: 9, am: [[0, .3], [1, .45]], f0: [[0, 40], [.3, 68], [.7, 58], [1, 32]],
    amp: [[0, 0], [.12, 1], [.8, .9], [1, 0]], mouth: [[0, .15], [.4, .5], [1, .1]] }),
  // a dilophosaurus: higher and lighter -- a hollow, gular hoot rising and breaking, from a slim throat (crested heads
  // likely resonated; kept closed-mouthed like its kin)
  dilophosaurus: mammal(1.7, { dur: 1.3, formantScale: .55, harmonics: 22, ...LION_TRACT, Bw: [100, 150, 230, 300], breath: .3, jitter: 5, shimmer: 12, subharm: .5, chaos: .45,
    roar: .35, roarFreq: 700, roarBw: 900, nasal: .45, amRate: 7, am: [[0, .2], [1, .4]], f0: [[0, 80], [.25, 150], [.6, 170], [1, 90]],
    amp: [[0, 0], [.1, 1], [.7, .85], [1, 0]], mouth: [[0, .2], [.4, .6], [1, .15]] }),
  // a pachycephalosaurus: a honk-grunt -- a short nasal honk (the ceratopsians' moo tract, smaller) ending in a
  // rough grunt, two or three in a run
  pachycephalosaurus: mammal(1.6, { ...MOO, dur: .55, repeat: 3, gap: .22, formantScale: .62, harmonics: 16, subharm: .5, chaos: .5, roar: .38, roarFreq: 560, nasal: .6,
    f0: [[0, 95], [.25, 150], [.6, 120], [1, 70]], amp: [[0, 0], [.08, 1], [.55, .9], [.75, .6], [1, 0]], mouth: [[0, .3], [.3, .9], [1, .3]] }),
  // a triceratops: a deep nasal honking bellow (the moo's tract, far bigger), closed-mouthed like its kin
  triceratops: mammal(2.2, { ...MOO, dur: 2.2, formantScale: .4, harmonics: 18, subharm: .55, chaos: .35, roar: .25, roarFreq: 420, nasal: .55,
    f0: [[0, 48], [.35, 82], [.7, 76], [1, 44]] }),
  // a styracosaurus: the ceratopsian honk, smaller and higher
  styracosaurus: mammal(1.8, { ...MOO, dur: 1.6, formantScale: .55, harmonics: 16, subharm: .45, chaos: .3, roar: .2, roarFreq: 520, nasal: .6,
    f0: [[0, 70], [.35, 120], [.7, 110], [1, 64]] }),
  // a diabloceratops: the styracosaurus' honk, a shade lower and rougher (a deeper, shorter face)
  diabloceratops: mammal(1.9, { ...MOO, dur: 1.7, formantScale: .5, harmonics: 16, subharm: .5, chaos: .38, roar: .24, roarFreq: 480, nasal: .55,
    f0: [[0, 62], [.35, 108], [.7, 98], [1, 56]] }),
  // a stegosaurus: a low, breathy moan
  stegosaurus: mammal(2.2, { ...MOO, dur: 2.4, formantScale: .38, harmonics: 14, breath: .35, subharm: .6, chaos: .4, roar: .3, roarFreq: 380, nasal: .4,
    f0: [[0, 40], [.4, 62], [.8, 55], [1, 36]] }),
  // an ankylosaurus: a run of deep nasal grunts
  ankylosaurus: mammal(2, { ...MOO, dur: .5, repeat: 4, gap: .25, formantScale: .42, harmonics: 14, subharm: .7, chaos: .55, roar: .45, roarFreq: 450, nasal: .5,
    f0: [[0, 55], [.3, 75], [1, 48]], amp: [[0, 0], [.15, 1], [.7, .8], [1, 0]] }),
  // the new beasts: a smilodon's roar (the tiger's tract, lower), a leopard's rasping 'sawing' (short hoarse grunts in a
  // run), a ram's deeper bleat, the antelopes' snorts and grunts, a reindeer's grunting series, a rhino's snort-bellow
  smilodon: mammal(2, { ...ROAR, dur: 1.4, formantScale: .5, f0: [[0, 70], [.3, 120], [.7, 100], [1, 60]] }),
  leopard:  mammal(1.6, { ...ROAR, dur: .35, repeat: 6, gap: .18, formantScale: .7, roar: .5, f0: [[0, 90], [.3, 130], [1, 80]], amp: [[0, 0], [.1, 1], [.8, .6], [1, 0]] }),
  ram:      mammal(1.1, { ...BLEAT, formantScale: .8, f0: [[0, 170], [.4, 240], [1, 160]] }),
  cervicapra: mammal(1, { ...ROE, formantScale: 1.2 }),
  oryx:     mammal(1.4, { ...MOO, dur: .6, repeat: 2, gap: .3, formantScale: .7, f0: [[0, 90], [.4, 110], [1, 80]] }),
  reindeer: mammal(1.3, { ...MOO, dur: .3, repeat: 4, gap: .2, formantScale: .75, roar: .4, f0: [[0, 70], [.5, 85], [1, 60]] }),
  rhinoceros: mammal(2, { ...MOO, dur: 1.2, formantScale: .45, roar: .45, subharm: .6, f0: [[0, 50], [.3, 75], [1, 45]] }),
  // ---- the primates and the kangaroo (2026-11-05) ----
  // a silverback: a run of soft rising hoots -- or the CHEST-BEAT, a fast patter of hollow pops off cupped hands (no voice)
  gorilla:  mammal(2, [{ dur: .2, formantScale: .5, harmonics: 6, Bw: [70, 110, 170, 220], breath: .15, jitter: 1, shimmer: 4, chaos: .05, nasal: .35, repeat: 6, gap: .12,
                         f0: [[0, 170], [.5, 215], [1, 185]], amp: [[0, 0], [.2, 1], [1, 0]], mouth: [[0, .15], [.5, .35], [1, .15]] },
                       { voice: 0, breath: 1, formantScale: .35, roar: .85, roarFreq: 240, roarBw: 320, dur: .055, repeat: 11, gap: .05,
                         f0: [[0, 30], [1, 30]], amp: [[0, 0], [.08, 1], [1, 0]], mouth: [[0, .9], [1, .5]] }]),
  // an olive baboon: the male's two-syllable bark, "wa-HOO"
  baboon:   mammal(1.6, { dur: .38, formantScale: .8, harmonics: 16, breath: .3, jitter: 3, shimmer: 10, subharm: .3, chaos: .35, roar: .3, roarFreq: 900, roarBw: 1200, repeat: 2, gap: .55,
                          f0: [[0, 240], [.3, 400], [.55, 290], [.7, 330], [1, 190]], amp: [[0, 0], [.08, 1], [.45, .45], [.6, .9], [1, 0]], mouth: [[0, .3], [.3, 1], [.55, .35], [1, .7]] }),
  // a ring-tailed lemur: the plaintive, cat-like wail
  lemur:    mammal(.8, { dur: .85, formantScale: 1.5, harmonics: 10, breath: .2, jitter: 1.5, shimmer: 5, chaos: .1, nasal: .5, vibRate: 6, vibDepth: .4,
                         f0: [[0, 480], [.3, 780], [.8, 690], [1, 430]], amp: [[0, 0], [.15, 1], [.8, .7], [1, 0]], mouth: [[0, .3], [.3, .8], [1, .3]] }),
  // an orangutan's LONG CALL (the throat sac's): deep bellowing pulses that rise, then grumble away
  orangutan: mammal(1.6, { dur: .5, formantScale: .45, harmonics: 20, breath: .3, jitter: 4, shimmer: 10, subharm: .6, chaos: .4, roar: .35, roarFreq: 450, roarBw: 700, nasal: .4, repeat: 5, gap: .32,
                           f0: [[0, 90], [.4, 140], [1, 85]], amp: [[0, 0], [.15, 1], [.7, .8], [1, 0]], mouth: [[0, .3], [.4, .8], [1, .3]] }),
  // a red kangaroo: soft guttural clucks and grunts
  kangaroo: mammal(.9, { dur: .1, formantScale: .9, harmonics: 10, breath: .4, jitter: 3, shimmer: 10, subharm: .3, chaos: .4, roar: .3, roarFreq: 700, roarBw: 900, nasal: .4, repeat: 4, gap: .26,
                         f0: [[0, 125], [1, 100]], amp: [[0, 0], [.1, 1], [1, 0]], mouth: [[0, .2], [.3, .5], [1, .15]] }),
  // a flamingo: a honking, goose-like gabble
  flamingo: bird(1.1, { h2: .8, h3: .5, noise: .25, voice2: .3, voice2Ratio: 1.4, vib: .3, vibRate: 25,
    syllables: [{ type: "sweep", dur: .12, f0: [[0, 700], [1, 600]], gap: .08 }, { type: "sweep", dur: .14, f0: [[0, 760], [1, 640]], gap: .09 }, { type: "sweep", dur: .12, f0: [[0, 720], [1, 620]], gap: .4 }] }),
  // a frog: a run of pulsed croaks, a throat sac's low nasal resonance
  frog:     mammal(.7, { dur: .3, formantScale: 1.2, harmonics: 14, breath: .1, jitter: 2, shimmer: 6, subharm: .3, chaos: .2, nasal: .7, amRate: 45, am: [[0, .8], [1, .8]], repeat: 3, gap: .35,
    f0: [[0, 130], [.4, 145], [1, 115]], amp: [[0, 0], [.1, 1], [.8, .9], [1, 0]], mouth: [[0, .15], [1, .25]] }),
  // a dolphin surfacing: a signature whistle (a wide, wavering FM sweep) and a click train
  dolphin:  bird(.9, { h2: .1, h3: 0, vib: 1.5, vibRate: 8, noise: .03,
    syllables: [{ type: "sweep", dur: .6, f0: [[0, 6000], [.4, 11000], [1, 8000]], gap: .1 }, { type: "noise", dur: .4, f0: [[0, 4000], [1, 4000]], bw: 5000, amRate: 150, level: .6, gap: .3 }] }),
  // a humpback's song, a phrase of it: long low moans sliding up and down (slow FM, a hollow second voice), a groan, a
  // rising whoop
  humpback: bird(1.6, { h2: .45, h3: .2, vib: .5, vibRate: 2.5, noise: .05, voice2: .25, voice2Ratio: 1.5,
    syllables: [{ type: "sweep", dur: 1.9, f0: [[0, 150], [.45, 235], [1, 125]], gap: .45 }, { type: "sweep", dur: 1.3, f0: [[0, 95], [.6, 80], [1, 70]], gap: .5 },
                { type: "sweep", dur: 1.1, f0: [[0, 260], [.8, 520], [1, 480]], gap: .9 }] }),
  // an orca: a PULSED CALL (a buzzing two-tone squeal: narrow-band noise pulsed 260 times a second, gliding up and
  // down) and a high whistle
  orca:     bird(1.1, { h2: .4, h3: .15, vib: .3, vibRate: 6, noise: .04,
    syllables: [{ type: "noise", dur: .55, f0: [[0, 1300], [.35, 2400], [1, 1700]], bw: 350, amRate: 260, gap: .12 }, { type: "noise", dur: .3, f0: [[0, 1900], [1, 1500]], bw: 300, amRate: 300, level: .8, gap: .35 },
                { type: "sweep", dur: .8, f0: [[0, 5500], [.5, 8500], [1, 6500]], level: .6, gap: .5 }] }),
  // a seal on the shore (haulout.js): mostly a long wavering MOAN through the nose (a grey seal's "singing", a harbour
  // seal's growling moan), sometimes a hoarse double BARK, or a short throaty growl
  seal:     mammal(1.1, [
    { dur: 1.9, formantScale: .8, harmonics: 9, Fc: [300, 900, 2100, 3000], Fo: [520, 1150, 2300, 3200], breath: .2, jitter: 1.5, shimmer: 5, subharm: .25, chaos: .12,
      nasal: .55, vibRate: 5, vibDepth: 1.4, f0: [[0, 170], [.25, 290], [.6, 270], [1, 150]], amp: [[0, 0], [.15, .9], [.6, 1], [1, 0]], mouth: [[0, .15], [.3, .6], [.8, .4], [1, .1]] },
    { dur: 1.4, formantScale: .8, harmonics: 9, Fc: [300, 900, 2100, 3000], Fo: [520, 1150, 2300, 3200], breath: .25, jitter: 2, shimmer: 6, subharm: .35, chaos: .15,
      nasal: .6, vibRate: 4, vibDepth: 1, f0: [[0, 240], [.4, 210], [1, 130]], amp: [[0, 0], [.1, 1], [.7, .8], [1, 0]], mouth: [[0, .3], [.4, .5], [1, .1]] },
    { dur: .26, formantScale: .9, harmonics: 18, Fc: [320, 950, 2200, 3200], Fo: [700, 1300, 2400, 3300], roarFreq: 900, roarBw: 1200, breath: .3, jitter: 3, shimmer: 10, subharm: .45, chaos: .5,
      nasal: .2, roar: .35, repeat: 2, gap: .32, f0: [[0, 220], [.2, 380], [.5, 330], [1, 190]], amp: [[0, 0], [.06, 1], [.5, .7], [1, 0]], mouth: [[0, .3], [.2, 1], [1, .4]] },
    { dur: .7, formantScale: .75, harmonics: 20, breath: .3, jitter: 4, shimmer: 12, subharm: .5, chaos: .5, nasal: .4, roar: .45, roarFreq: 600, roarBw: 900, amRate: 18,
      f0: [[0, 110], [.4, 140], [1, 95]], amp: [[0, 0], [.1, 1], [.7, .8], [1, 0]], mouth: [[0, .1], [.4, .4], [1, .1]], am: [[0, .3], [1, .4]] }]),
  // a walrus bull: a deep rough BELLOW out of the huge chest, or a run of short GRUNTS
  walrus:   mammal(1.6, [
    { dur: 1.7, formantScale: .45, harmonics: 26, Fc: [200, 520, 1250, 2100], Fo: [480, 900, 1550, 2300], Bw: [90, 140, 220, 280], roarFreq: 500, roarBw: 900, breath: .25, jitter: 5, shimmer: 14,
      subharm: .65, chaos: .55, nasal: .3, roar: .7, amRate: 9, f0: [[0, 70], [.3, 118], [.75, 100], [1, 58]], amp: [[0, 0], [.12, 1], [.75, .85], [1, 0]], mouth: [[0, .2], [.3, .9], [.85, .6], [1, .2]],
      am: [[0, .15], [.5, .3], [1, .25]] },
    { dur: .3, formantScale: .55, harmonics: 20, breath: .2, jitter: 4, shimmer: 12, subharm: .55, chaos: .45, nasal: .5, roar: .5, roarFreq: 500, roarBw: 800, repeat: 4, gap: .3,
      Fc: [220, 650, 1500, 2400], Fo: [450, 950, 1700, 2500], f0: [[0, 85], [.3, 115], [1, 80]], amp: [[0, 0], [.1, 1], [.6, .8], [1, 0]], mouth: [[0, .1], [.3, .5], [1, .1]] }]),
  // and its BELL: a walrus bull's ringing knocks -- a run of pure tones struck and dying away, an inharmonic partial over
  // each (a bell's, 2.76 times up), the run slowing, then a softer pair
  walrusBell: bird(1.2, { h2: .12, h3: .05, vib: 0, noise: .01, voice2: .35, voice2Ratio: 2.76,
    syllables: [{ type: "sweep", dur: .32, f0: [[0, 455], [1, 440]], gap: .22 }, { type: "sweep", dur: .32, f0: [[0, 455], [1, 438]], gap: .26 },
                { type: "sweep", dur: .34, f0: [[0, 450], [1, 436]], gap: .32 }, { type: "sweep", dur: .36, f0: [[0, 448], [1, 432]], level: .8, gap: .42 },
                { type: "sweep", dur: .5, f0: [[0, 452], [1, 430]], level: .55, gap: .8 }, { type: "sweep", dur: .5, f0: [[0, 452], [1, 430]], level: .4, gap: .5 }] }),
  // ---- birds ----
  // a whooper swan: trumpeting "whoop-whoop", strongly harmonic with a second voice
  swan:     bird(.9, { motifs: 2, h2: .8, h3: .6, noise: .25, voice2: .3, vib: .3, vibRate: 20,
    syllables: [{ type: "sweep", dur: .28, f0: [[0, 560], [.3, 720], [1, 640]], gap: .12 }, { type: "sweep", dur: .35, f0: [[0, 700], [.4, 760], [1, 560]], gap: .5 }] }),
  // a peacock: the loud "may-AWE" scream, twice
  peacock:  bird(1.5, { motifs: 2, h2: .6, h3: .4, noise: .2, voice2: .3, voice2Ratio: 1.33, vib: .5, vibRate: 18,
    syllables: [{ type: "sweep", dur: .18, f0: [[0, 650], [1, 900]], gap: .02 }, { type: "sweep", dur: .55, f0: [[0, 1200], [.2, 1350], [1, 950]], gap: .5 }] }),
  // the tawny owl: "hoo ... hu, hu-hu-hoooo", soft low tones, a long pause, a quavering last note
  owl:      bird(.9, { h2: .3, h3: .08, vibRate: 7, noise: .08,
    syllables: [{ type: "sweep", dur: .55, f0: [[0, 420], [.2, 470], [1, 400]], gap: 1 }, { type: "sweep", dur: .16, f0: [[0, 430], [1, 400]], gap: .25 },
      { type: "trill", dur: 1.1, f0: [[0, 480], [.3, 460], [1, 400]], trillRate: 7, trillDepth: .1, gap: 1 }] }),
  // an eagle: a shrill wavering scream, then a string of falling chips
  eagle:    bird(1.3, { h2: .25, h3: .05, noise: .2, vib: .6, vibRate: 28,
    syllables: [{ type: "sweep", dur: .4, f0: [[0, 2400], [.2, 3000], [1, 2100]], gap: .08 },
      ...Array.from({ length: 5 }, (_, k) => ({ type: "sweep", dur: .07, f0: [[0, 2800 - k * 120], [1, 2300 - k * 100]], gap: .06 }))] }),
  // a parrot: a harsh squawk -- noise and a biphonic voice fighting each other
  parrot:   bird(1.1, { motifs: 2, h2: .7, h3: .5, noise: .6, voice2: .5, voice2Ratio: 1.41, vib: .8, vibRate: 45,
    syllables: [{ type: "noise", dur: .18, f0: [[0, 1800], [.5, 2400], [1, 1600]], bw: 1400, amRate: 110, gap: .04 }, { type: "sweep", dur: .22, f0: [[0, 1400], [.4, 2300], [1, 1200]], gap: .3 }] }),
  // a king penguin's trumpet: a short pick-up note, then the long brassy call -- two voices a hair apart, beating
  penguin:  bird(1.3, { h2: .85, h3: .6, noise: .2, voice2: .5, voice2Ratio: 1.06, vib: .6, vibRate: 22,
    syllables: [{ type: "sweep", dur: .12, f0: [[0, 520], [1, 640]], gap: .05 }, { type: "sweep", dur: .9, f0: [[0, 700], [.2, 820], [.8, 760], [1, 560]], gap: .6 }] }),
  // an ostrich booms with its bill shut, like a crocodile: a low, hollow "boo-boo-boooom", the neck puffed out
  ostrich:  mammal(1.6, { dur: .7, formantScale: .5, harmonics: 8, breath: .2, jitter: 3, shimmer: 8, subharm: .6, chaos: .3, nasal: .5, repeat: 3, gap: .35,
    f0: [[0, 70], [.3, 92], [1, 58]], amp: [[0, 0], [.15, 1], [.8, .8], [1, 0]], mouth: [[0, .1], [.5, .25], [1, .1]] }),
  // a keel-billed toucan: a dry croaking "krrrek, krrrek", frog-like, over and over
  toucan:   bird(1, { motifs: 3, h2: .5, h3: .3, noise: .7, syllables: [{ type: "noise", dur: .16, f0: [[0, 900], [1, 780]], bw: 600, amRate: 60, gap: .25 }] }),
  // an ibis: mostly quiet -- a few low nasal honks, "hunk-hunk-hunk"
  ibis:     bird(.8, { h2: .7, h3: .5, noise: .4, voice2: .2, voice2Ratio: 1.3,
    syllables: [{ type: "sweep", dur: .09, f0: [[0, 460], [1, 380]], gap: .1 }, { type: "sweep", dur: .09, f0: [[0, 450], [1, 370]], gap: .1 }, { type: "sweep", dur: .1, f0: [[0, 440], [1, 360]], gap: .5 }] }),
  // a pelican: nearly silent away from the colony -- a low hoarse grunt or two
  pelican:  mammal(.8, { dur: .25, formantScale: .7, harmonics: 12, breath: .5, jitter: 3, shimmer: 10, subharm: .4, chaos: .4, roar: .3, roarFreq: 600, nasal: .3, repeat: 2, gap: .3,
    f0: [[0, 110], [.4, 140], [1, 95]], amp: [[0, 0], [.1, 1], [.7, .7], [1, 0]], mouth: [[0, .2], [.4, .6], [1, .2]] }),
  // a griffon vulture: no song at all -- a breathy hiss and a guttural grunt over a carcass
  vulture:  mammal(.9, { dur: .45, formantScale: .6, harmonics: 10, breath: .8, jitter: 4, shimmer: 12, subharm: .5, chaos: .6, roar: .2, roarFreq: 500, nasal: .2, repeat: 2, gap: .4,
    f0: [[0, 120], [.3, 150], [1, 90]], amp: [[0, 0], [.1, 1], [.7, .6], [1, 0]], mouth: [[0, .3], [.4, .7], [1, .2]] }),
  // a tawny owl's other call: the female's sharp "ke-WICK", then the male's hoot
  "tawny owl": bird(1, { h2: .3, h3: .1, noise: .15, vib: .4, vibRate: 20,
    syllables: [{ type: "sweep", dur: .12, f0: [[0, 1200], [1, 1800]], gap: .1 }, { type: "sweep", dur: .2, f0: [[0, 1600], [.3, 1700], [1, 1100]], gap: 1.2 },
      { type: "sweep", dur: .5, f0: [[0, 420], [.2, 470], [1, 400]], gap: .8 }, { type: "trill", dur: .9, f0: [[0, 480], [.3, 460], [1, 400]], trillRate: 7, trillDepth: .1, gap: 1 }] }),
  // a hoopoe: its name -- a soft, low, hollow "oop-oop-oop"
  hoopoe:   bird(.7, { h2: .15, h3: .03, noise: .05,
    syllables: [0, 1, 2].map((k) => ({ type: "sweep", dur: .1, f0: [[0, 520], [.3, 540], [1, 480]], gap: k < 2 ? .13 : .9 })) }),
  // a great spotted woodpecker: a sharp "kik!" (its drumming is the bill on wood, not a call)
  woodpecker: bird(1, { h2: .4, h3: .2, noise: .3, syllables: [{ type: "sweep", dur: .04, f0: [[0, 3000], [1, 2500]], gap: .7 }] }),
  // a sulphur-crested cockatoo: an ear-splitting raucous screech
  cockatoo: bird(1.6, { h2: .8, h3: .6, noise: .8, voice2: .6, voice2Ratio: 1.37, vib: 1, vibRate: 50,
    syllables: [{ type: "noise", dur: .5, f0: [[0, 1600], [.2, 2300], [1, 1500]], bw: 2200, amRate: 90, gap: .6 }] }),
  // a cockatiel: a rising whistled "queel", again and again
  cockatiel: bird(.9, { motifs: 2, h2: .2, h3: .05, noise: .05, vib: .3, vibRate: 25,
    syllables: [{ type: "sweep", dur: .3, f0: [[0, 2200], [.6, 3000], [1, 3200]], gap: .45 }] }),
  // (2026-11-07) an Atlantic puffin: nearly silent but at the burrow -- a low, droning groan, "arr-arr-arrr"
  puffin:   mammal(.5, { dur: .5, formantScale: .9, harmonics: 10, breath: .4, jitter: 3, shimmer: 8, subharm: .3, chaos: .2, nasal: .4, repeat: 3, gap: .15,
    f0: [[0, 180], [.5, 200], [1, 150]], amp: [[0, 0], [.15, 1], [.8, .8], [1, 0]], mouth: [[0, .2], [.5, .5], [1, .2]] }),
  // a grey crowned crane: a honking two-note "ka-wonk", and a deep booming in display
  "crowned crane": bird(1.1, { h2: .7, h3: .45, noise: .3, voice2: .3, voice2Ratio: 1.26,
    syllables: [{ type: "sweep", dur: .12, f0: [[0, 520], [1, 600]], gap: .06 }, { type: "sweep", dur: .3, f0: [[0, 700], [.3, 760], [1, 520]], gap: 1.4 }] }),
  // a spoonbill: all but silent -- a soft grunting
  spoonbill: mammal(.5, { dur: .2, formantScale: .8, harmonics: 8, breath: .5, jitter: 3, shimmer: 8, subharm: .3, chaos: .2, nasal: .3, repeat: 2, gap: .25,
    f0: [[0, 160], [1, 130]], amp: [[0, 0], [.2, 1], [1, 0]], mouth: [[0, .2], [.5, .4], [1, .2]] }),
  // a southern cassowary: a booming rumble, felt more than heard
  cassowary: mammal(1.4, { dur: 1.1, formantScale: .55, harmonics: 14, breath: .3, jitter: 2, shimmer: 6, subharm: .6, chaos: .2, roar: .2, roarFreq: 300, nasal: .1,
    f0: [[0, 48], [.3, 56], [1, 40]], amp: [[0, 0], [.2, 1], [.8, .8], [1, 0]], mouth: [[0, .1], [.4, .3], [1, .1]] }),
  // a turkey tom: the gobble -- a fast throaty rattle falling away
  turkey:   bird(1.2, { h2: .8, h3: .6, noise: .4, voice2: .3, voice2Ratio: 1.33,
    syllables: [{ type: "trill", dur: .7, f0: [[0, 900], [.3, 1000], [1, 620]], trillRate: 22, trillDepth: .35, gap: 1.5 }] }),
  // a great hornbill: a loud, barking "kok" -- in pairs and bursts, from the canopy
  hornbill: bird(1.4, { motifs: 2, h2: .7, h3: .5, noise: .5, voice2: .3, voice2Ratio: 1.41,
    syllables: [{ type: "noise", dur: .14, f0: [[0, 700], [1, 560]], bw: 700, amRate: 50, gap: .12 }, { type: "noise", dur: .16, f0: [[0, 680], [1, 520]], bw: 700, amRate: 50, gap: .9 }] }),
  // ---- insects ----
  // a dragonfly's wings: a soft clattering rustle (~35 beats a second), passing by
  dragonfly:insect(.25, { dur: 2.5, clickRate: 35, clickJitter: 5, resFreq: 900, resBw: 1500, noise: .6, wander: 10, wanderRate: 1.5, flyby: .8 }),
  // ---- beasts ----
  // a minotaur: a bull's bellow that tears into a roar
  minotaur: mammal(2, { dur: 1.9, formantScale: .5, Fc: [220, 650, 1500, 2500], Fo: [480, 950, 1800, 2600], Bw: [70, 120, 200, 260], harmonics: 14, breath: .2, jitter: 4, shimmer: 10, subharm: .6, chaos: .5,
    roar: .5, roarFreq: 600, roarBw: 800, nasal: .4, f0: [[0, 70], [.3, 135], [.7, 120], [1, 60]], amp: [[0, 0], [.12, .9], [.5, 1], [.85, .7], [1, 0]], mouth: [[0, .1], [.35, .95], [.85, .5], [1, .1]] }),
  // a manticore: the lion's roar with a second, inharmonic voice and a hissing edge, faster pulsing
  manticore:mammal(2, { ...ROAR, dur: 2, formantScale: .45, biphon: .45, biphonRatio: 1.26, amRate: 16, roarFreq: 1400, f0: [[0, 70], [.3, 125], [.6, 110], [1, 50]] }),
  unicorn:  mammal(1.3, { ...WHINNY, formantScale: .7, harmonics: 7, jitter: .8, shimmer: 3, chaos: .06, subharm: .1, biphon: .5, biphonRatio: 1.5, roar: 0, breath: .12, vibRate: 11, vibDepth: 3.5,
    f0: [[0, 850], [.15, 1900], [.5, 1650], [.75, 700], [1, 420]], am: [[0, 0], [.7, 0], [.76, .5], [1, .6]] }),   // a cleaner, glassier whinny
  centaur:  mammal(1.4, { ...WHINNY, dur: 1.6, formantScale: .8, harmonics: 14, chaos: .3, biphon: .15, biphonRatio: 1.26, vibRate: 10, vibDepth: 3, nasal: .1, amRate: 7,
    f0: [[0, 300], [.15, 720], [.5, 600], [.75, 260], [1, 160]], am: [[0, 0], [.7, 0], [.76, .6], [1, .7]] }),   // half a man's throat: a lower, shouted whinny
  // a dragon: an enormous tract, near-infrasonic pitch, all chaos and turbulence, slow pulsing
  dragon:   mammal(3, { dur: 2.8, formantScale: .32, harmonics: 30, ...LION_TRACT, Bw: [110, 170, 260, 320], roarFreq: 600, roarBw: 1600, breath: .4, jitter: 6, shimmer: 18, subharm: .8, chaos: .8,
    biphon: .3, biphonRatio: 1.33, amRate: 7, am: [[0, .1], [.4, .3], [1, .2]], roar: 1, f0: [[0, 45], [.25, 95], [.6, 80], [1, 38]], amp: [[0, 0], [.1, 1], [.75, .9], [1, 0]], mouth: [[0, .3], [.25, 1], [.8, .8], [1, .2]] }),
  // a hydra: many heads at once (a strong second voice), hissing turbulence, fast pulsing, twice
  hydra:    mammal(2.2, { dur: 1.6, formantScale: .6, harmonics: 20, roarFreq: 3200, roarBw: 2500, roar: .9, breath: .5, jitter: 5, shimmer: 14, subharm: .4, chaos: .6, biphon: .7, biphonRatio: 1.26, amRate: 22,
    am: [[0, .3], [1, .4]], repeat: 2, gap: .2, f0: [[0, 120], [.3, 190], [.7, 160], [1, 90]], mouth: [[0, .4], [.3, 1], [1, .4]] }),
  // a snake's hiss: breath only, through a small open mouth
  snake:    mammal(.5, { voice: 0, breath: 1, formantScale: 2.6, Fc: [400, 1200, 2600, 3500], Fo: [700, 1500, 2800, 3600], dur: 1.3, f0: [[0, 100], [1, 100]], amp: [[0, 0], [.15, 1], [.75, .9], [1, 0]], mouth: [[0, .5], [1, .8]] }),
};
// silent (absent from the table on purpose): hare, butterfly, fish, shark, turtle, scorpion, spider, drider, and the
// sea's and the rivers' others (trout, carp, pike, swordfish, clownfish, lionfish, ray, eel, octopus, crab, plesiosaurus
// -- whatever a plesiosaur sounded like, nobody knows), and the pteranodon (soaring far overhead; a pterosaur's voice is
// as unknown, and it has no syrinx to borrow a bird's from)

// Unseen wildlife for the ambience (environment.js): `when` it sings (day,
// night, dusk) and `kind`. Same recipes, same engine, never a game species.
const wild = (when, kind, r) => ({ ...r, when, kind });
export const WILD = {
  // fluty, low for a songbird, slow melodic sweeps and a scratchy high flourish
  blackbird:   wild("day", "bird", bird(1, { h2: .25, h3: .05, vib: .3, vibRate: 12,
    syllables: [{ type: "sweep", dur: .22, f0: [[0, 1800], [1, 2400]], gap: .08 }, { type: "sweep", dur: .18, f0: [[0, 2600], [.5, 2100], [1, 2300]], gap: .06 }, { type: "sweep", dur: .3, f0: [[0, 1600], [.4, 2900], [1, 2200]], gap: .1 },
      { type: "sweep", dur: .16, f0: [[0, 2000], [1, 1700]], gap: .05 }, { type: "trill", dur: .25, f0: [[0, 4500], [1, 5200]], trillRate: 35, trillDepth: .2, level: .5, gap: .6 }] })),
  // "tee-cher, tee-cher": a high note and a lower one
  greattit:    wild("day", "bird", bird(.8, { motifs: 4, h2: .1, h3: 0, noise: .03,
    syllables: [{ type: "sweep", dur: .12, f0: [[0, 4200], [1, 4000]], gap: .05 }, { type: "sweep", dur: .14, f0: [[0, 3200], [1, 2900]], gap: .22 }] })),
  cuckoo:      wild("day", "bird", bird(1.2, { motifs: 3, h2: .08, h3: 0, noise: .02,
    syllables: [{ type: "sweep", dur: .25, f0: [[0, 690], [1, 660]], gap: .12 }, { type: "sweep", dur: .3, f0: [[0, 560], [1, 540]], gap: .8 }] })),
  // a descending series that speeds up, then a flourish sweeping up
  chaffinch:   wild("day", "bird", bird(.9, { syllables: [...Array.from({ length: 9 }, (_, k) => ({ type: "sweep", dur: .09 - k * .004, f0: [[0, 5000 - k * 220], [1, 4300 - k * 200]], gap: .075 - k * .006 })),
    { type: "sweep", dur: .18, f0: [[0, 2600], [.5, 4200], [1, 3800]], gap: .6 }] })),
  robin:       wild("day", "bird", bird(.8, { motifs: 2, h2: .08, h3: 0, vib: .45, vibRate: 22,
    syllables: [{ type: "sweep", dur: .12, f0: [[0, 6600], [1, 4600]], gap: .05 }, { type: "sweep", dur: .09, f0: [[0, 3900], [1, 5300]], gap: .04 }, { type: "trill", dur: .22, f0: [[0, 4600], [1, 4400]], trillRate: 26, trillDepth: .2, gap: .06 },
      { type: "sweep", dur: .16, f0: [[0, 7000], [.5, 5400], [1, 6400]], gap: .05 }, { type: "sweep", dur: .2, f0: [[0, 5000], [1, 4200]], level: .7, gap: .5 }] })),
  // no tone at all: pulsed broadband noise with a rough 40 Hz modulation
  crow:        wild("day", "bird", bird(1.3, { motifs: 3, h2: 0, h3: 0, noise: 0, syllables: [{ type: "noise", dur: .35, f0: [[0, 1400], [.3, 1700], [1, 1200]], bw: 900, amRate: 42, gap: .35 }] })),
  // lower and more tonal than a crow: a harsh "kraa" with heavy harmonics and noise riding on it
  raven:       wild("day", "bird", bird(1.4, { motifs: 3, h2: .9, h3: .7, vib: .15, vibRate: 30, noise: 1, voice2: .25, syllables: [{ type: "sweep", dur: .5, f0: [[0, 300], [.25, 380], [1, 290]], gap: .6 }] })),
  // a mimic's jumble: whistle, rattle, clicks, warble, chuckle, a burst of noise
  starling:    wild("day", "bird", bird(.8, { h2: .3, h3: .1, vib: .2, vibRate: 14, noise: .08, voice2: .15,
    syllables: [{ type: "sweep", dur: .3, f0: [[0, 1900], [1, 3600]], gap: .06 }, { type: "trill", dur: .35, f0: [[0, 6200], [1, 5800]], trillRate: 45, trillDepth: .15, level: .6, gap: .08 },
      { type: "noise", dur: .04, f0: [[0, 3000], [1, 3000]], bw: 3000, amRate: 200, gap: .05 }, { type: "noise", dur: .04, f0: [[0, 3200], [1, 3200]], bw: 3000, amRate: 200, gap: .05 },
      { type: "noise", dur: .04, f0: [[0, 2800], [1, 2800]], bw: 3000, amRate: 200, gap: .12 }, { type: "sweep", dur: .32, f0: [[0, 3100], [.5, 2200], [1, 3300]], gap: .06 },
      { type: "trill", dur: .3, f0: [[0, 1500], [1, 1300]], trillRate: 14, trillDepth: .4, gap: .08 }, { type: "noise", dur: .25, f0: [[0, 5000], [1, 4000]], bw: 4000, amRate: 60, level: .7, gap: .6 }] })),
  // "coo-COO-coo, coo-coo": soft breathy low notes with a strong second harmonic
  woodpigeon:  wild("day", "bird", bird(.9, { motifs: 2, h2: .55, h3: .15, noise: .15,
    syllables: [{ type: "sweep", dur: .3, f0: [[0, 420], [1, 440]], level: .7, gap: .08 }, { type: "sweep", dur: .42, f0: [[0, 470], [1, 440]], gap: .1 }, { type: "sweep", dur: .3, f0: [[0, 420], [1, 400]], level: .8, gap: .16 },
      { type: "sweep", dur: .28, f0: [[0, 430], [1, 420]], level: .75, gap: .08 }, { type: "sweep", dur: .14, f0: [[0, 420], [1, 380]], level: .5, gap: .9 }] })),
  // the green woodpecker's "laugh": a dozen ringing notes that drop and quicken
  yaffle:      wild("day", "bird", bird(1.2, { h2: .4, h3: .15, noise: .1,
    syllables: Array.from({ length: 12 }, (_, k) => ({ type: "sweep", dur: .11 - k * .003, f0: [[0, 1650 - k * 25], [1, 1250 - k * 20]], gap: .09 - k * .004 })) })),
  // the great spotted woodpecker drumming: a bill striking wood ~16 times a second, rolls every couple of seconds
  drumming:    wild("day", "bird", insect(1.2, { dur: 4.5, clickRate: 16, clickJitter: 4, resFreq: 800, resBw: 600, pulseLen: 200, pulsesPerChirp: 4, pulseGap: 0, chirpRate: .55, noise: .35 })),
  // rich whistles with an inharmonic second syrinx voice, then a fast pulsed run -- sings at night
  nightingale: wild("night", "bird", bird(1, { h2: .3, h3: .1, vib: .2, vibRate: 15, noise: .05, voice2: .35, voice2Ratio: 1.33,
    syllables: [{ type: "sweep", dur: .35, f0: [[0, 2200], [1, 2400]], gap: .05 }, { type: "sweep", dur: .3, f0: [[0, 2400], [1, 2450]], gap: .05 }, { type: "sweep", dur: .4, f0: [[0, 2500], [1, 2600]], gap: .15 },
      { type: "trill", dur: .6, f0: [[0, 3200], [1, 3000]], trillRate: 18, trillDepth: .3, gap: .7 }] })),
  // no tone: a drawn-out hiss-scream sweeping around 3 kHz
  barnowl:     wild("night", "bird", bird(1, { h2: 0, h3: 0, noise: 0, syllables: [{ type: "noise", dur: 1.2, f0: [[0, 2200], [.4, 3600], [1, 2400]], bw: 2200, amRate: 65, gap: .8 }] })),
  tawnyowl:    wild("night", "bird", CALLS.owl),
  // a near-pure 4.5 kHz wing resonance gated into chirps of four pulses, two or three a second
  cricket:     wild("night", "insect", insect(.5, { clickRate: 4500, resFreq: 4500, resBw: 60, pulseLen: 22, pulsesPerChirp: 4, pulseGap: 35, chirpRate: 2.2, noise: .05 })),
  // tymbal clicks exciting a 5-6 kHz abdomen, several individuals beating, slow swelling
  cicada:      wild("day", "insect", insect(.8, { dur: 5, clickRate: 220, clickJitter: 6, resFreq: 5400, resBw: 700, pulsesPerChirp: 12, amRate: 1.3, amDepth: .5, chorus: 6, chorusSpread: 12, noise: .3 })),
  // wingbeats ~230/s are the pitch; the pitch wanders and the level passes by
  honeybee:    wild("day", "insect", insect(.3, { clickRate: 230, clickJitter: 2, resFreq: 900, resBw: 1300, noise: .05, wander: 6, wanderRate: 1.5, flyby: .7 })),
  bumblebee:   wild("day", "insect", insect(.35, { clickRate: 160, clickJitter: 3, resFreq: 600, resBw: 1000, noise: .1, wander: 8, wanderRate: 1.2, flyby: .6 })),
  mosquito:    wild("dusk", "insect", insect(.2, { dur: 5, clickRate: 580, clickJitter: .8, resFreq: 1900, resBw: 1600, noise: .04, wander: 12, wanderRate: 2.4, flyby: .9 })),
  // broadband scraping in short fast bursts, a dozen a second
  grasshopper: wild("day", "insect", insect(.3, { dur: 3, clickRate: 90, clickJitter: 25, resFreq: 7000, resBw: 2500, pulseLen: 25, pulsesPerChirp: 8, pulseGap: 45, chirpRate: 1.4, noise: .9 })),
};

// render one fresh variant of a call (loudness-normalised); `over` overrides
// preset fields (environment.js asks for 8 s of crickets to loop)
export function renderCall(name, over) {
  const rec = CALLS[name] ?? WILD[name];
  if (!rec) return null;
  const P = Array.isArray(rec.p) ? rec.p[Math.floor(rnd() * rec.p.length)] : rec.p;
  return loudnorm(ENGINES[rec.engine](VARY[rec.engine]({ ...P, ...over })), .2);
}

// An outdoor space: a light, dark-tailed reverb (a generated impulse) with
// a dry path. Feed calls into `input`; it goes to `dest` (default speakers).
export function makeSpace(ctx, { wet = .3, size = 1.3, dest } = {}) {
  const n = Math.ceil(ctx.sampleRate * size), ir = ctx.createBuffer(2, n, ctx.sampleRate);
  for (let c = 0; c < 2; c++) {
    const d = ir.getChannelData(c); let lp = 0;
    for (let i = 0; i < n; i++) { lp += (Math.random() * 2 - 1 - lp) * .25; d[i] = lp * Math.pow(1 - i / n, 2.2) * (i < 40 ? i / 40 : 1); }
  }
  const input = ctx.createGain(), conv = ctx.createConvolver(), wg = ctx.createGain(), dg = ctx.createGain();
  conv.buffer = ir; wg.gain.value = wet; dg.gain.value = 1;
  input.connect(dg); dg.connect(dest ?? ctx.destination);
  input.connect(conv); conv.connect(wg); wg.connect(dest ?? ctx.destination);
  return { input };
}

// play one species' call (or a WILD voice); `pitch` scales the playback rate
// (an individual's size: pitch and tempo together), `dest` is where it goes
// (default the speakers). A few renders per name are kept and reused, with a
// fresh one now and then, so no two calls in a row are quite the same and a
// herd costs a handful of renders. Returns the end time (AC seconds).
const pool = new Map(), VARIANTS = 4;
// the mammals' loudness on top of the renders' common calibration: they were
// all as soft as a songbird. Two to three times louder, by how loud the real
// animal is (a lion's roar or a cow's moo carries; a cat or a rat stays small)
const LOUDER = { smilodon: 3, rhinoceros: 3, leopard: 2.5, oryx: 2.5, reindeer: 2.5, ram: 2, cervicapra: 2, tyrannosaur: 3, carnotaurus: 3, allosaurus: 3, dilophosaurus: 2.5, pachycephalosaurus: 2.5, triceratops: 3, styracosaurus: 3, diabloceratops: 3, stegosaurus: 3, ankylosaurus: 3, cow: 3, ox: 3, lion: 3, tiger: 3, elephant: 3, hippo: 3, minotaur: 3, manticore: 3,
  bear: 2.5, horse: 2.5, wolf: 2.5, pig: 2.5, camel: 2.5, bactrian: 2.5, unicorn: 2.5, centaur: 2.5,
  rooster: 2.5, dog: 2, sheep: 2, deer: 2, boar: 2, zebra: 2, giraffe: 2, fox: 2, cat: 2, rat: 2, beaver: 2, hedgehog: 2, bat: 2,
  gorilla: 3, orangutan: 2.5, baboon: 2.5, lemur: 2, kangaroo: 2,
  hyena: 2.5, impala: 2, capybara: 2, anteater: 2, skunk: 2, pangolin: 2, badger: 2, weasel: 2,
  lynx: 2.5, chamois: 2.5, redpanda: 2, giantpanda: 2.5, porcupine: 2 };
for (const [n, l] of Object.entries(LOUDER)) CALLS[n].level = l;

export function animalCall(ctx, name, { dest, at, pitch = 1, volume = .5 } = {}) {
  const rec = CALLS[name] ?? WILD[name];
  if (!rec) return ctx.currentTime;
  let vs = pool.get(name); if (!vs) pool.set(name, vs = []);
  let buf;
  if (vs.length < VARIANTS || rnd() < .1) {
    buf = toBuffer(renderCall(name));
    if (vs.length < VARIANTS) vs.push(buf); else vs[Math.floor(rnd() * VARIANTS)] = buf;
  } else buf = vs[Math.floor(rnd() * vs.length)];
  // (renders sit at -14 dB RMS; volume .5 puts a call at about -18 dB RMS, the old calibration)
  return play(ctx, buf, { dest, at, rate: pitch * (.97 + rnd() * .06), gain: volume * 1.25 * (rec.level ?? 1) }).end;
}
