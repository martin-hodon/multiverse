// ACOUSTIC-TO-ARTICULATORY: given the formants a sound should have, find the posture that makes them.
//
// Many postures make the same three formants (that is the old trouble with inversion), so the answer is not "a"
// posture but the most RELAXED one: the cost is the distance from the target formants (in octaves -- the ear's
// measure) plus a small price on every articulator's distance from rest, plus a price on a vowel that nearly shuts
// the airway. The search is plain coordinate descent with a shrinking step from several starts; each trial costs one
// knock on the tube (measure.js), a few milliseconds, and the formants it is judged by are the ones you will hear.
import { ARTICULATORS, neutral, clampArt, areaFunction, toSections } from "./anatomy.js";
import { formants } from "./measure.js";

export const INVERSION = { weights: [1, 1, .45], relax: .012, openArea: .12, openPrice: 3, free: ["jaw", "bodyX", "bodyY", "tipX", "tipY", "lipH", "lipP"], rounds: 26,
  price: { tipX: 6, tipY: 6 },      // x relax: a vowel is made with the body, the jaw and the lips; the tip goes along unless it must not
  starts: [{}, { bodyX: .7, bodyY: .5 }, { jaw: 15, bodyX: -.4, bodyY: -.7 },
           { bodyX: -.6, bodyY: .5, lipH: .45, lipP: .9 }, { bodyX: -1.0, bodyY: .8, lipH: .25, lipP: 1.3, jaw: 4 }, { bodyX: -.9, bodyY: -.2, lipH: .35, lipP: 1.2, jaw: 8 },
           { bodyX: .6, bodyY: .6, lipH: .3, lipP: 1.2, jaw: 3 }] };   // (the last: front AND rounded -- y, ø)

export function costOf(art, target, tube, anat, inv = INVERSION) {
  const af = areaFunction(art, anat), s = toSections(af, tube); tube.shape(s.areas, 0, s.lipExtra, s.gloExtra);
  const f = formants(tube, { max: 4 });
  let cost = 0;
  for (let k = 0; k < target.length; k++) { if (!target[k]) continue; const got = f[k]?.hz; cost += inv.weights[k] * (got ? Math.log2(got / target[k]) ** 2 : 4); }
  for (const k of inv.free) { const [lo, hi, n] = ARTICULATORS[k]; cost += inv.relax * (inv.price?.[k] ?? 1) * ((art[k] - n) / (hi - lo)) ** 2; }
  let minA = Infinity; for (let i = 2; i < af.As.length - 2; i++) minA = Math.min(minA, af.As[i]);   // (the lips may be as small as they like: that is rounding)
  if (minA < inv.openArea) cost += inv.openPrice * (inv.openArea - minA) / inv.openArea;
  return { cost, formants: f.map((x) => x.hz), minArea: minA };
}
export function invert(target, tube, anat, { inv = INVERSION, fixed = {}, from = null } = {}) {
  let best = null;
  for (const start of from ? [from] : inv.starts) {
    const art = clampArt({ ...neutral(), ...start, ...fixed }); let cur = costOf(art, target, tube, anat, inv);
    const step = Object.fromEntries(inv.free.map((k) => [k, (ARTICULATORS[k][1] - ARTICULATORS[k][0]) * .18]));
    for (let r = 0; r < inv.rounds; r++) {
      let moved = false;
      for (const k of inv.free) {
        if (k in fixed) continue;
        for (const dir of [1, -1]) {
          const was = art[k]; art[k] = Math.min(ARTICULATORS[k][1], Math.max(ARTICULATORS[k][0], was + dir * step[k])); if (art[k] === was) continue;
          const c = costOf(art, target, tube, anat, inv);
          if (c.cost < cur.cost - 1e-7) { cur = c; moved = true; break; } else art[k] = was;
        }
      }
      if (!moved) for (const k of inv.free) step[k] *= .55;
    }
    if (!best || cur.cost < best.cost) best = { ...cur, art: { ...art } };
  }
  return best;
}
