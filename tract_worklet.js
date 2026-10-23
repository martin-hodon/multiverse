// the tube, live: one posture held, the folds running, shaped from the page by messages.
//   { type: "config", config }        the engine's numbers (same sections as tract/config.js)
//   { type: "voice", voice }          who speaks (rebuilds the tube: a different head is a different pipe)
//   { type: "art", art }              where the articulators are
//   { type: "source", f0, rest, pressure, on }   the folds and the lungs
import { Tube, ACOUSTICS } from "./tract/acoustics.js";
import { Glottis, GLOTTIS, CM_H2O } from "./tract/glottis.js";
import { ANATOMY, ARTICULATORS, areaFunction, toSections, neutral, clampArt } from "./tract/anatomy.js";
import { anatomyFor, tubeFor, OUTPUT } from "./tract/synth.js";

const merge = (dst, src) => { for (const [k, v] of Object.entries(src)) { if (v && typeof v === "object" && !Array.isArray(v) && dst[k] && typeof dst[k] === "object") merge(dst[k], v); else dst[k] = v; } };
class TractProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.voice = { oral: 1, pharynx: 1, folds: 1, gain: 1, pressure: 1 }; this.art = neutral(); this.src = { f0: 110, rest: .003, pressure: 0, on: false };
    this.p0 = 0; this.pNow = 0; this.f0Now = 110; this.restNow = .3; this.chinkNow = 0; this.build(); this.dirty = true;
    this.port.onmessage = (e) => { const m = e.data;
      if (m.type === "config") { merge(ACOUSTICS, m.config.acoustics ?? {}); merge(GLOTTIS, m.config.glottis ?? {}); merge(ANATOMY, m.config.anatomy ?? {}); merge(OUTPUT, m.config.output ?? {}); this.build(); }
      if (m.type === "voice") { this.voice = m.voice; this.build(); }
      if (m.type === "wobble") { Object.assign(this.voice, m.voice); this.folds.wobble = { flutter: this.voice.flutter ?? 1, jitter: this.voice.jitter ?? 1 }; this.folds.person = { closure: this.voice.closure ?? 1, swing: this.voice.swing ?? 1 }; this.tube.breathNoise = this.voice.breathNoise ?? 1; if (m.voice.rest !== undefined) this.src.rest = m.voice.rest; }   // (what of a voice belongs to the folds alone: no new tube)
      if (m.type === "art") { this.art = clampArt({ ...this.art, ...m.art }); this.dirty = true; }
      if (m.type === "source") Object.assign(this.src, m); };
  }
  build() { this.anat = anatomyFor(this.voice, ANATOMY); this.tube = tubeFor(sampleRate, this.anat, ACOUSTICS, 3); this.tube.breathNoise = this.voice.breathNoise ?? 1; this.folds = new Glottis(sampleRate, GLOTTIS, 9); this.folds.wobble = { flutter: this.voice.flutter ?? 1, jitter: this.voice.jitter ?? 1 }; this.folds.person = { closure: this.voice.closure ?? 1, swing: this.voice.swing ?? 1 }; this.dirty = true; }
  process(inputs, outputs) {
    const out = outputs[0][0]; if (!out) return true;
    if (this.dirty) { const s = toSections(areaFunction(this.art, this.anat), this.tube); this.tube.shape(s.areas, s.velum, s.lipExtra, s.gloExtra); this.dirty = false; }
    const g = { Ps: 0, Ag: 0 }, s = this.src, want = s.on ? s.pressure * (this.voice.pressure ?? 1) : 0;
    for (let i = 0; i < out.length; i++) {
      this.pNow += (want - this.pNow) * .0012; this.f0Now += (s.f0 - this.f0Now) * .002; this.restNow += ((s.on ? s.rest : .3) - this.restNow) * .003; this.chinkNow += ((s.on ? (s.chink ?? 0) : 0) - this.chinkNow) * .003;
      g.Ps = this.pNow * CM_H2O; this.p0 += (this.tube.R[0] + this.tube.L[0] - this.p0) * .02;
      g.Ag = this.folds.step(this.f0Now, this.restNow, g.Ps - this.p0, this.voice.folds ?? 1, this.voice.creakiness ?? 0, this.chinkNow);
      out[i] = this.tube.step(g) * OUTPUT.gain * (this.voice.gain ?? 1);
    }
    for (let c = 1; c < outputs[0].length; c++) outputs[0][c].set(out);
    return true;
  }
}
registerProcessor("tract", TractProcessor);
