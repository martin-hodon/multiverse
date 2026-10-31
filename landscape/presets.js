// THE LANDSCAPE ENGINE's presets (docs/landscape.md): the rocks, the geologies' stacks of beds, the climates, the
// features a scene has unless the spec says otherwise
import { clamp, noise, fbm, rng } from "./core.js";

// ---- GEOLOGY ----------------------------------------------------------------------------------------------------------
// ROCKS: how steep a metre-scale wall of it stands (deg), how hard it is (the stream's cutting, how far a fall's lip
// holds), its colour; `joint`: how far apart the cracks through it are (m) -- a wall fails along them, leaving notches and
// the buttresses between; `karst`: rain dissolves it (sinkholes, springs, caves); `columns`: it cracks in columns (three
// sets of joints at 60 deg, close)
export const ROCKS = {
  sandstone: { angle: 78, hard: .6, joint: 9, color: [.78, .55, .37], name: "sandstone" },
  shale:     { angle: 33, hard: .15, color: [.50, .45, .43], name: "shale" },
  limestone: { angle: 84, hard: .7, joint: 7, karst: true, color: [.80, .78, .71], name: "limestone" },
  marl:      { angle: 36, hard: .25, color: [.66, .62, .52], name: "marl" },
  basalt:    { angle: 86, hard: .9, joint: 2.6, columns: true, color: [.25, .24, .24], name: "basalt" },
  tuff:      { angle: 45, hard: .3, color: [.62, .52, .44], name: "tuff" },
  granite:   { angle: 75, hard: 1, joint: 15, color: [.66, .61, .58], name: "granite" },
  till:      { angle: 38, hard: .1, color: [.55, .50, .42], name: "till" },
};
export const SCREE_ANGLE = 34;   // loose rock: what falls lies at this
// GEOLOGY presets: the beds from the top of the stack down (thickness in metres; the last goes on down), how the stack
// dips (deg, toward `dipDir`) and how its bed boundaries wander (m); `lake`: what makes a hollow on the upland for water
export const GEOLOGY = {
  canyon:   { name: "sandstone canyon country", beds: [["sandstone", 7], ["shale", 9], ["sandstone", 5], ["shale", 7], ["sandstone"]], dip: .6, warp: .8 },
  karst:    { name: "limestone karst", beds: [["limestone", 12], ["marl", 4], ["limestone", 9], ["marl", 6], ["limestone"]], dip: .4, warp: .6 },
  volcanic: { name: "basalt flows", beds: [["basalt", 6], ["tuff", 6], ["basalt", 8], ["tuff", 5], ["basalt"]], dip: .3, warp: 1.2 },
  granite:  { name: "granite upland", beds: [["till", 1.5], ["granite"]], dip: 0, warp: .4 },
};
// CLIMATE presets: rain (mm/yr), mean temperature (C). What follows from them is worked out (climateOf)
export const CLIMATES = {
  temperate: { name: "temperate, wet", rain: 1100, temp: 10 },
  arid:      { name: "arid", rain: 160, temp: 21 },
  alpine:    { name: "alpine", rain: 1500, temp: 1 },
  tropical:  { name: "tropical", rain: 2600, temp: 25 },
  mediterranean: { name: "mediterranean", rain: 560, temp: 16 },
};
export function climateOf(c) {
  const { rain, temp } = c, evap = clamp(300 + 45 * temp, 150, 1500);   // (what the warmth takes back, mm/yr)
  const wet = clamp((rain - evap * .55) / 900, 0, 1);                    // 0 dry .. 1 wet: runoff, soil, plants
  return { ...c, evap, wet,
    flows: rain > 420,                                         // a stream that runs all year (else only after storms)
    lakes: rain > evap * .7,                                   // a lake that stays (else a pan, a pool)
    frost: clamp((8 - Math.abs(temp - 0)) / 8, 0, 1) * clamp(rain / 600, 0, 1) + (temp < 3 ? .3 : 0),   // freeze and thaw: scree
    soil: clamp(wet * 1.4 + (temp > 18 ? .3 : 0) * wet, 0, 1.5),   // how deep the soil gets on gentle ground (m)
    plants: temp < -2 ? "none" : temp < 3 ? "tundra" : rain < 250 ? "desert" : rain < 600 ? "scrub" : temp > 20 && rain > 1800 ? "jungle" : "forest" };
}
// the bed at a point: depth below the stack's top (its datum, dipping and warped) -> the bed it falls in
export function makeStrata(geo, top, seed) {
  // (each place's beds their own thickness: the preset's, give or take `vary` -- 0.3 unless said)
  const vr = rng(seed * 7919 + 13), vary = geo.vary ?? .3;
  const beds = geo.beds.map(([rock, t]) => ({ rock, t: t == null ? Infinity : t * (1 + vary * (vr() * 2 - 1)), ...ROCKS[rock] }));
  const dip = Math.tan((geo.dip ?? 0) * Math.PI / 180), dd = (geo.dipDir ?? 30) * Math.PI / 180, dx = Math.cos(dd) * dip, dy = Math.sin(dd) * dip;
  const base = [];   // depth of each bed's top
  let d = 0; for (const b of beds) { base.push(d); d += b.t; }
  const datum = (x, y) => top - dx * x - dy * y + (geo.warp ?? 0) * fbm(x / 70, y / 70, seed + 5, 2);
  const bedAt = (x, y, z) => {
    const depth = datum(x, y) - z;
    if (depth < 0) return 0;
    for (let k = beds.length - 1; k > 0; k--) if (depth >= base[k]) return k;
    return 0;
  };
  // the depth of the next bed boundary below a point (how much of this bed is left under it)
  const topOf = (x, y, k) => datum(x, y) - base[k];   // the elevation of bed k's top here
  return { beds, base, datum, bedAt, topOf };
}

// ---- THE SCENE --------------------------------------------------------------------------------------------------------
// spec: { seed, size (m), dx (m a cell), geology (a GEOLOGY name or one), climate (a CLIMATES name or one), relief
// (a scale on the beds' thicknesses), features: { lake: { r, islands }, waterfall, ravine: { length }, cliff, cave } }
export const DEFAULT_FEATURES = { cliff: true, waterfall: true, ravine: { length: .28 }, lake: { r: .13, islands: 1 }, cave: true, outliers: { count: 3 }, bridge: { chance: .6 }, meanders: { amp: 1 }, steps: true, tributary: true, fans: true, badlands: true, tufa: true, moraine: true, coast: { chance: .45 }, dunes: true, cone: { chance: .7 }, dolines: true, tors: true, hoodoos: true };
