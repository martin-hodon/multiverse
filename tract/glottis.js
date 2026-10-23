// THE VOICE SOURCE, as a larynx rather than as a waveform. Two folds stand some distance apart (ABDUCTION: pressed
// together, just touching, a little apart, wide open) and the air the lungs push between them sets them swinging about
// that rest position. The synthesiser is given only the AREA between them, sample by sample; the flow through it --
// the glottal pulse, its skew, the way it rides on the tract's resonances -- is worked out by the tube (acoustics.js)
// from that area and the lung pressure.
//
//   area(t) = soft-clip at zero of [ rest + swing * wave(phase) ]  +  chink
//
// One number, `rest`, is the whole continuum of voice quality: below zero the folds are pressed and shut for most of
// the cycle (a tight, bright voice); at zero they just meet (modal: open half the time); a little above, they never
// quite close and air leaks through all cycle long (breathy: a strong fundamental and noise, made by the tube where
// the jet is); far above, they are too far apart to swing at all and what is left is breath: /h/, and the voiceless
// consonants. So devoicing is a GESTURE -- the folds drawn apart and back -- not a switch.
//   `chink` is the other way of letting air through: a gap at the BACK, between the cartilages, while the membranous folds in
// front of it go on meeting each other. It does not swing with them, so the flow never stops -- which is what a voiced fricative
// needs: a z whose glottis shuts every cycle has a jet only half the time, its hiss is 13 dB under an s's, and what is heard is
// a buzz with an s let go after it (the frication only arrives when the folds part at the end of the word).
//   The swing needs pressure ACROSS the folds to keep going (threshold ~3 cm H2O). Behind a closed mouth that
// pressure dies as the mouth fills, and with it the voice: a voiced stop's voice bar fades by itself.
// No imports, no DOM.
export const CM_H2O = 980.665;                 // dyn/cm2

export const GLOTTIS = {
  swing: 0.105,          // cm2: how far the folds open at full pressure, for the reference (male) folds
  swingPressure: 8,      // cm H2O at which `swing` is reached; the swing goes with the square root of the pressure
  threshold: 2.6,        // cm H2O across the folds below which they stop swinging
  stopsAt: 0.17,         // cm2 of rest opening at which the folds no longer swing at all
  skew: 0.18,            // the closing half of the swing is this much quicker than the opening half (mucosal wave)
  soft: 0.0035,          // cm2: how gently the area meets zero (the folds close like a zip, not like a door)
  chinkMax: 0.09,        // cm2: as wide a gap as the cartilages hold open; more than this is not a chink but an open glottis
  pitchPerPressure: 0.012, // F0 rises by this share per cm H2O over swingPressure (louder is higher; a closing mouth lowers it)
  jitter: 0.006, shimmer: 0.03, slowShare: 0.75, memory: 0.9,   // cycle-to-cycle irregularity; most of it slow (each cycle resembles the last)
  flutter: 0.004,        // slow wander of the pitch (three incommensurate sines, Klatt's flutter), as a share of F0
  // CREAK (vocal fry), by how much of it is asked for (0..1): the folds pressed together and slack -- the pitch drops by `pitch`, the cycles
  // come in long-short pairs (`alternate`, and `alternateSize` in their strength), irregular (x `jitter`), the folds stay shut for most of
  // each cycle (`press` cm2 off the rest opening, a sharper closure) and keep going on little breath (`threshold`: x less pressure needed)
  creak: { pitch: .45, alternate: .16, alternateSize: .22, jitter: 5, press: .03, threshold: .5 },
};

export class Glottis {
  constructor(fs, cfg = GLOTTIS, seed = 7) { this.fs = fs; this.wobble = { flutter: 1, jitter: 1 }; this.person = { closure: 1, swing: 1 }; this.alt = 1;   /* person: x how sharply this speaker's folds close (brightness; pressed .. flow) and how far they swing */   /* x, one person's (set by whoever owns the voice) */ this.cfg = cfg; this.phase = 0; this.seed = seed >>> 0 || 1; this.slowJ = 0; this.slowS = 0; this.cycJ = 0; this.cycS = 0; this.t = 0; this.area = 0; this.f0Now = 0; }
  gauss() { let s = 0; for (let i = 0; i < 4; i++) { let x = this.seed; x ^= x << 13; x ^= x >>> 17; x ^= x << 5; this.seed = x >>> 0; s += this.seed / 4294967296; } return (s - 2) * 1.73; }
  // f0: Hz asked for.  rest: cm2 (see above).  across: pressure across the folds now, dyn/cm2.  size: fold size x reference (a woman ~ .62)
  // (the folds' REST opening goes with the square root of their size: drawing them apart is the cartilages' doing, and a small larynx
  // opens nearly as wide as a large one -- scaled with the folds, a woman's open glottis was narrower than her /s/, the pressure fell
  // at the folds instead of at the tongue and the /s/ had no hiss)
  step(f0, rest, across, size = 1, creak = 0, chink = 0) {
    const c = this.cfg, dP = Math.max(0, across) / CM_H2O, K = c.creak, cr = Math.max(0, Math.min(1, creak)), who = this.person;
    const flutter = 1 + c.flutter * this.wobble.flutter * (Math.sin(2 * Math.PI * 12.7 * this.t) + Math.sin(2 * Math.PI * 7.1 * this.t) + Math.sin(2 * Math.PI * 4.7 * this.t)) / 3;
    const f = f0 * flutter * (1 + c.pitchPerPressure * (dP - c.swingPressure)) * (1 + this.cycJ) * (1 - K.pitch * cr) * (1 + this.alt * K.alternate * cr);
    this.f0Now = f; this.t += 1 / this.fs; this.phase += f / this.fs;
    if (this.phase >= 1) {                                       // a new cycle: its own small departure from the last
      this.phase -= 1; this.alt = -this.alt; const g1 = this.gauss(), g2 = this.gauss(), k = Math.sqrt(1 - c.memory * c.memory);
      this.slowJ = c.memory * this.slowJ + k * g1; this.slowS = c.memory * this.slowS + k * g2;
      this.cycJ = c.jitter * this.wobble.jitter * (1 + K.jitter * cr) * (Math.sqrt(c.slowShare) * this.slowJ + Math.sqrt(1 - c.slowShare) * g1);
      this.cycS = c.shimmer * this.wobble.jitter * (Math.sqrt(c.slowShare) * this.slowS + Math.sqrt(1 - c.slowShare) * g2);
    }
    // do they swing? -- enough pressure across them, and not too far apart
    const drive = Math.max(0, Math.min(1, (dP - c.threshold * (1 - K.threshold * cr)) / 1.5)) * Math.max(0, Math.min(1, 1 - rest / (c.stopsAt * Math.sqrt(size))));
    const swing = c.swing * who.swing * (1 + this.alt * K.alternateSize * cr) * size * Math.sqrt(Math.max(dP, 0) / c.swingPressure) * drive * (1 + this.cycS);
    // the wave: a sine whose falling half is quicker than its rising half
    const p = this.phase, up = .5 + Math.min(.7, c.skew * who.closure * (1 + cr)) / 2, w = p < up ? -Math.cos(Math.PI * p / up) : Math.cos(Math.PI * (p - up) / (1 - up));
    const x = (rest - K.press * cr) * Math.sqrt(size) + swing * w, s = c.soft * size / (who.closure * (1 + cr));
    this.area = (x > 12 * s ? x : s * Math.log1p(Math.exp(x / s)))       // soft-clipped at zero
      + Math.max(0, Math.min(c.chinkMax, chink)) * Math.sqrt(size);       // ...plus the gap at the back, which never closes
    return this.area;
  }
}
