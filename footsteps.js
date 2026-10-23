// YOUR FOOTSTEPS: a step every stride you actually walk -- by the ground under your feet: the soft brush of grass, the
// grit of a road, the sharp tap of stone flags, the hollow knock of boards (a floor, the bridge), the squeaky crunch of
// snow, a squelch in mud, a splash wading -- and, riding, the mount's hooves at its own pace. Synthesized here, a few
// takes of each so no two steps sound alike, left and right feet a little apart; quiet, as your own steps are -- under the
// world round you, not over it.
//
//   const steps = createFootsteps({ audio })
//   steps.update(dt, { speed, surface, riding, airborne })   // every frame: speed m/s over the ground; surface one of
//                                                            //   SURFACES (or null: no sound -- swimming)
import { SR, toBuffer, play } from "./dsp.js";

export const SURFACES = ["grass", "gravel", "stone", "wood", "snow", "mud", "water"];
// gain: the whole (times `volume`, config.json `footsteps` / ?steps=); rms: each take's loudness, the average not the
// peak -- a sharp tap and a soft brush come out alike, and each surface's `vol` then sets it (2026-10-23: they were each
// scaled to full peak, .22 of it, into the speakers -- loud and harsh over everything else)
export const FOOTSTEPS = { stride: .72, run: 1.05, hoof: 1.25, takes: 4, gain: .14, rms: .16 };

// one take of a surface's step: noise and a little resonance, enveloped (a one-pole filter or two, nothing more)
export function take(surface, seed) {   // (exported for checks)
  let s = seed * 9301 + 49297;
  const rnd = () => ((s = (s * 9301 + 49297) % 233280) / 233280) * 2 - 1;
  const len = Math.round(SR * (surface === "water" ? .32 : surface === "snow" || surface === "mud" ? .22 : .16)), out = new Float32Array(len);
  let lp = 0, lp2 = 0, y1 = 0, y2 = 0;
  // lo: the noise's low-pass (0..1, brighter up); thump: the heel; grains: grit; ring: a body's resonance (Hz, how fast it
  // dies); att: the onset, never under 4 ms (a click); vol: the surface's loudness, grass the softest
  const P = {
    grass:  { lo: .18, thump: .35, grains: 0, ring: [0, 0], att: .014, dec: 18, vol: .55 },
    gravel: { lo: .32, thump: .45, grains: .18, ring: [0, 0], att: .006, dec: 24, vol: .8 },
    stone:  { lo: .4, thump: .5, grains: 0, ring: [640, 80], att: .004, dec: 40, vol: .7 },
    wood:   { lo: .25, thump: .8, grains: 0, ring: [190, 40], att: .004, dec: 26, vol: .8 },
    snow:   { lo: .3, thump: .25, grains: .35, ring: [0, 0], att: .02, dec: 12, vol: .65 },
    mud:    { lo: .1, thump: .5, grains: 0, ring: [0, 0], att: .015, dec: 14, vol: .65 },
    water:  { lo: .16, thump: .2, grains: .1, ring: [0, 0], att: .03, dec: 9, vol: 1 },
    hoof:   { lo: .45, thump: .8, grains: 0, ring: [430, 60], att: .004, dec: 36, vol: .8 },
  }[surface];
  // the ring: a two-pole resonator the step's noise strikes (a board, a flag, a hoof's horn)
  const rf = P.ring[0] * (1 + rnd() * .08), r = Math.exp(-P.ring[1] / SR), c1 = 2 * r * Math.cos(2 * Math.PI * rf / SR), c2 = -r * r;
  for (let i = 0; i < len; i++) {
    const t = i / SR, env = Math.min(1, t / P.att) * Math.exp(-Math.max(0, t - P.att) * P.dec);
    let n = rnd();
    if (P.grains && Math.random() < P.grains * .25) n *= 3;                     // (grit, crystals: sharp grains in it)
    lp += (n - lp) * P.lo; lp2 += (lp - lp2) * P.lo;                           // (two poles down)
    let v = lp2 * env;
    if (rf) { const y = c1 * y1 + c2 * y2 + v * .08; y2 = y1; y1 = y; v += y; }
    v += Math.sin(2 * Math.PI * 55 * t) * Math.exp(-t * 40) * P.thump * .5;    // (the heel's thump)
    if (surface === "mud") v *= .7 + .3 * Math.sin(2 * Math.PI * (300 - 600 * t) * t);   // (a sucking squelch)
    out[i] = v;
  }
  // (to its loudness: the average over the step's body, the first 60 ms, not its peak -- and never past full scale)
  let e = 0, m = 1e-6; const body = Math.min(len, Math.round(SR * .06));
  for (let i = 0; i < body; i++) e += out[i] * out[i];
  for (const v of out) m = Math.max(m, Math.abs(v));
  const k = Math.min(FOOTSTEPS.rms / Math.sqrt(e / body + 1e-12), .95 / m) * P.vol;
  for (let i = 0; i < len; i++) out[i] *= k;
  return out;
}

export function createFootsteps({ audio = () => null, volume = 1 } = {}) {
  const bank = new Map();   // surface -> its takes (made the first time it is walked on)
  let walked = 0, foot = 1;
  const sound = (ctx, surface, loud) => {
    if (!bank.has(surface)) bank.set(surface, Array.from({ length: FOOTSTEPS.takes }, (_, k) => toBuffer(take(surface, k + 1))));
    const takes = bank.get(surface), g = ctx.createGain(), pan = ctx.createStereoPanner();
    g.gain.value = FOOTSTEPS.gain * volume * loud; pan.pan.value = foot * .12; foot = -foot;
    g.connect(pan); pan.connect(ctx.destination);
    play(ctx, takes[Math.floor(Math.random() * takes.length)], { dest: g, rate: .92 + Math.random() * .16 });
    setTimeout(() => { g.disconnect(); pan.disconnect(); }, 600);
  };
  return {
    update(dt, { speed = 0, surface = "grass", riding = false, airborne = false } = {}) {
      const ctx = audio();
      if (!ctx || !surface || airborne || speed < .3 || !volume) { walked = 0; return; }
      walked += speed * dt;
      const stride = riding ? FOOTSTEPS.hoof : speed > 3 ? FOOTSTEPS.run : FOOTSTEPS.stride;
      if (walked < stride) return;
      walked -= stride;
      if (riding) {   // two hooves to a stride, a little apart (a walk's four-beat, roughly)
        sound(ctx, surface === "grass" || surface === "snow" || surface === "mud" ? surface : "hoof", 1);
        setTimeout(() => ctx && sound(ctx, surface === "grass" || surface === "snow" || surface === "mud" ? surface : "hoof", .8), stride / Math.max(speed, .5) * 500);
      } else sound(ctx, surface, Math.min(1, .75 + speed * .06));   // (a run a little louder than a walk)
    },
  };
}
