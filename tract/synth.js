// movement -> sound: the plan's tracks drive the head (anatomy.js), the head shapes the tube (acoustics.js), the folds
// (glottis.js) open and close at its bottom. One loop, one sample at a time; the shape is renewed at the control rate.
import { Tube, ACOUSTICS } from "./acoustics.js";
import { Glottis, GLOTTIS, CM_H2O } from "./glottis.js";
import { ANATOMY, ARTICULATORS, areaFunction, toSections, neutral } from "./anatomy.js";
import { plan, TIMING, PROSODY, PERSON } from "./planner.js";

// who is speaking: a tract (as scales of the reference head), a larynx, a way of talking
// a head and a larynx (oral ... gain), and a WAY OF SPEAKING (planner.js PERSON: range ... jitter) -- spelled out in every voice so
// that each is a complete, editable row of the configuration
const person = (o) => ({ ...o, ...PERSON, ...Object.fromEntries(Object.entries(o).filter(([k]) => k in PERSON)) });
export const VOICES = {
  man:   person({ name: "Man", oral: 1, pharynx: 1, f0: 112, folds: 1, rest: .003, pressure: 1, rate: 1, gain: 1, variability: .35 }),
  woman: person({ name: "Woman", oral: .91, pharynx: .82, f0: 205, folds: .62, rest: .012, pressure: .95, rate: 1, gain: 1, range: 1.25, liveliness: 1.1, legato: .6, variability: .5 }),
  child: person({ name: "Child (~7)", oral: .78, pharynx: .66, f0: 300, folds: .45, rest: .012, pressure: 1, rate: .95, gain: 1, range: 1.4, liveliness: 1.2, legato: .4, jitter: 1.3, variability: .6 }),
  deep:  person({ name: "Deep man", oral: 1.05, pharynx: 1.1, f0: 92, folds: 1.12, rest: .0, pressure: 1.05, rate: .95, gain: 1, range: .8, register: -1, legato: .65, finalLengthening: 1.2, variability: .3 }),
  breathy: person({ name: "Breathy woman", oral: .91, pharynx: .82, f0: 195, folds: .62, rest: .035, pressure: .9, rate: .95, gain: 1, range: 1.1, legato: .75, pauseScale: 1.2, variability: .4 }),
};
export const OUTPUT = { gain: 5e-3, limit: .95 };

// ONE PERSON'S HEAD is the reference head scaled (oral, pharynx) and then RESHAPED -- all x the reference, 1 = as drawn:
//   palateHeight   the dome of the palate above the teeth (high and narrow .. low and flat)
//   pharynxDepth   how far behind the tongue the throat's back wall stands
//   lipWidth, lipThickness   the mouth's width; the length of the lip tube at rest
//   tongueSize     the tongue body's radius (a big tongue in a small mouth narrows everything: keep within a few %)
//   noseSize       the nasal passages' width
// The tongue's habits (the postures) were learned in the reference head: in a reshaped one the same movements give somewhat other
// vowels -- which is how heads differ -- unless the voice has postures of its own (voice.postures, fitted in the lab: "Re-fit for this voice").
export const HEAD_SHAPE = ["palateHeight", "pharynxDepth", "lipWidth", "lipThickness", "tongueSize", "noseSize"];
const smooth = (u) => { u = Math.max(0, Math.min(1, u)); return u * u * (3 - 2 * u); };
function reshape(anat, v) {
  const pal = v.palateHeight ?? 1, ph = v.pharynxDepth ?? 1, teethY = anat.wall[anat.wall.length - 1][1];
  if (pal === 1 && ph === 1 && (v.lipWidth ?? 1) === 1 && (v.lipThickness ?? 1) === 1 && (v.tongueSize ?? 1) === 1) return anat;
  // the dome rises about the teeth's level, from the velum forward; the throat's back wall moves back below the velum
  const move = ([x, y]) => [x - (ph - 1) * 1.1 * (1 - smooth((y - 4.3) / 2.2)) * (1 - smooth((x - .3) / 1)), y + (pal - 1) * Math.max(0, y - teethY) * smooth((x - .85) / 1.2)];
  // (shape: what adaptPosture needs -- how far the palate rose over the tongue's body, how far the throat's wall went back; cm, reference head)
  const top = Math.max(...anat.wall.map((p) => p[1]));
  return { ...anat, shape: { palateRise: (pal - 1) * (top - teethY), throatBack: (ph - 1) * 1.1 }, wall: anat.wall.map(move), velumAt: move(anat.velumAt), places: Object.fromEntries(Object.entries(anat.places).map(([k, p]) => [k, move(p)])),
    lips: { ...anat.lips, width: anat.lips.width * (v.lipWidth ?? 1), thickness: anat.lips.thickness * (v.lipThickness ?? 1) }, tongue: { ...anat.tongue, radius: anat.tongue.radius * (v.tongueSize ?? 1) } };
}
// (ring: the tube over the folds narrower than the reference -- the narrower, the more the voice carries around 3 kHz)
export const anatomyFor = (voice, anat = ANATOMY) => ({ ...reshape(anat, voice), scale: { oral: voice.oral ?? 1, pharynx: voice.pharynx ?? 1, nose: voice.noseSize ?? 1 }, larynxTube: { ...anat.larynxTube, area: anat.larynxTube.area / Math.max(.4, voice.ring ?? 1), length: anat.larynxTube.length * (1 + .3 * ((voice.ring ?? 1) - 1)) } });   // (and a little longer: a resonator of its own needs both)
// the array must be shorter than the shortest tract this head will make: the neutral length less what lips and larynx can take back
export function tubeFor(fs, anat, cfg = ACOUSTICS, seed = 1) { const af = areaFunction(neutral(), anat), tube = new Tube(fs, af.length - 2.6 * Math.min(anat.scale.oral, anat.scale.pharynx), cfg, seed, anat.scale); toSections(af, tube); return tube; }   // (the neutral posture places the velum's joint)

// where the sprung tip is: the narrowest section of the front half of the mouth
const narrowestFront = (areas) => { let k = areas.length - 2; for (let i = Math.floor(areas.length * .55); i < areas.length - 1; i++) if (areas[i] < areas[k]) k = i; return k; };
export function renderTracks(tracks, voice, { fs = 48000, anatomy = ANATOMY, acoustics = ACOUSTICS, glottis = GLOTTIS, seed = 1, trace = null, onSample = null } = {}) {
  const anat = anatomyFor(voice, anatomy), tube = tubeFor(fs, anat, acoustics, seed), folds = new Glottis(fs, glottis, seed + 6); tube.breathNoise = voice.breathNoise ?? 1; folds.wobble = { flutter: voice.flutter ?? 1, jitter: voice.jitter ?? 1 }; folds.person = { closure: voice.closure ?? 1, swing: voice.swing ?? 1 };
  const N = Math.ceil(tracks.total / 1000 * fs), out = new Float32Array(N), per = fs / tracks.control, keys = Object.keys(ARTICULATORS), art = neutral();
  const reach = Math.max(0, anat.shape?.palateRise ?? 0);      // (under a higher palate the tongue's body may go as much higher: or no k would shut)
  let p0 = 0; const g = { Ps: 0, Ag: 0 };
  for (let i = 0, frame = -1; i < N; i++) {
    const f = Math.min(tracks.n - 1, Math.floor(i / per));
    if (f !== frame) { frame = f; for (const k of keys) art[k] = Math.min(ARTICULATORS[k][1] + (k === "bodyY" ? reach : 0), Math.max(ARTICULATORS[k][0], tracks[k][f])); const s = toSections(areaFunction(art, anat), tube); tube.shape(s.areas, s.velum, s.lipExtra, s.gloExtra); tube.flapOn = tracks.flap?.[f] ?? 0; if (tube.flapOn > .01) tube.flapAt = narrowestFront(s.areas); if (i === 0) tube.snap(); }
    const u = i / per - f, f2 = Math.min(tracks.n - 1, f + 1), mix = (tr) => tr[f] + (tr[f2] - tr[f]) * u;
    g.Ps = mix(tracks.pressure) * (voice.pressure ?? 1) * CM_H2O;
    p0 += (tube.R[0] + tube.L[0] - p0) * .02;                                  // the pressure just above the folds, its ripple smoothed off
    g.Ag = folds.step(mix(tracks.f0), mix(tracks.rest), g.Ps - p0, voice.folds ?? 1, tracks.creak ? mix(tracks.creak) : 0, tracks.chink ? mix(tracks.chink) : 0);
    const y = tube.step(g) * OUTPUT.gain * (voice.gain ?? 1);
    if (onSample) onSample(i, tube, y, g);
    if (trace) { const k = Math.floor(i / fs * 100); const r = trace[k] ?? (trace[k] = { Ag: 0, U: 0, across: 0, f0: 0 }); r.Ag = Math.max(r.Ag, g.Ag); r.U = Math.max(r.U, tube.U0); r.across = (g.Ps - p0) / CM_H2O; r.f0 = folds.f0Now; }
    out[i] = Math.abs(y) < OUTPUT.limit ? y : Math.sign(y) * (OUTPUT.limit + (1 - OUTPUT.limit) * Math.tanh((Math.abs(y) - OUTPUT.limit) / (1 - OUTPUT.limit)));
  }
  tracks.blewUp = tube.meter.blewUp ?? 0;
  return out;
}
export function renderIPA(ipa, { lang = "en", voice = VOICES.man, postures, mark = ".", fs = 48000, anatomy = ANATOMY, acoustics, glottis, timing = TIMING, prosody = PROSODY, seed = 1, trace = null, onSample = null } = {}) {
  const tracks = plan(ipa, { lang, postures, voice, mark, timing, prosody, anatomy: anatomyFor(voice, anatomy) });
  return { samples: renderTracks(tracks, voice, { fs, anatomy, acoustics, glottis, seed, trace, onSample }), tracks };
}
