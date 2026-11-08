import { markSculpt } from "/home/martin/store/apps/multiverse/bodyspec.js";
// Generative pond fish, ~0.25-0.45m. Swimmers ride the flier plumbing: constant motion, `alt` = height above the lake
// floor. SCULPTED (2026-11-05, the sculpt overlay, docs/engines.md): a roach's fusiform body, deepest a third of the way
// back (its depth 28% of its length), a blunt head with the gill cover's line and a big eye, a slim caudal peduncle and a
// forked tail on the tail's bone (it beats), dorsal, pectoral, pelvic and anal fins as thin plates; countershaded --
// the back the colour's dark, the flanks its own over scales, a pale silver belly, the lateral line
const FISHC = [
  { b: 0x8a9aa6, t: 0x4d5d6a, f: 0x9a7a6a },     // silver (roach: its fins reddish)
  { b: 0x7a7a4e, t: 0x49583e, f: 0x6a6a44 },     // olive carp
  { b: 0xd0782e, t: 0xa85a20, f: 0xd8904a },     // koi orange
  { b: 0x6a7a92, t: 0x3c4a63, f: 0x5a6a80 },     // blue-grey
];
export function makeFish({ seed = 1 } = {}) {
  let s = (seed * 2246822519) >>> 0 || 1;
  const r = () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296;
  const vi = Math.floor(r() * FISHC.length), v = FISHC[vi];
  // (three sizes, not any: each fish a sculpted body, built once for its colour and its size)
  const ks = Math.min(2, Math.floor(r() * 3)), k = .8 + ks * .35, key = vi * 3 + ks;
  if (!FISH.has(key)) FISH.set(key, markSculpt(fishDef(v, k)));
  return FISH.get(key);
}
const FISH = new Map();
function fishDef(v, k) {
  const pale = 0xd6dad4, dark = 0x141618;
  const mixC = (a, b, t) => [16, 8, 0].reduce((o, sh) => o | Math.round(((a >> sh) & 255) * (1 - t) + ((b >> sh) & 255) * t) << sh, 0);
  const gillC = mixC(v.t, dark, .45), lineC = mixC(v.t, dark, .3), finC = mixC(v.f, 0xb04a30, .18), tailC = mixC(v.f, dark, .3);
  const FR = { u: [1, 0, 0], v: [0, 1, 0], r: .075 };   // (one frame for the trunk's scales: r sets their size, ~5 mm -- a roach's)
  const shape = [
    { id: "trunk", type: "ell", c: [.012, 0, 0], r: [.092, .029, .0145], k: .006, color: v.b, pat: "scales", frame: FR },
    { id: "back", type: "ell", c: [.005, .017, 0], r: [.075, .016, .0105], k: .006, kc: .008, color: v.t, pat: "scales", frame: FR },
    { id: "belly", type: "ell", c: [.015, -.014, 0], r: [.075, .015, .0115], k: .006, kc: .008, color: pale },
    { id: "rear", type: "ell", c: [-.05, .001, 0], r: [.045, .017, .0085], k: .008, color: v.b, pat: "scales", frame: FR },
    { id: "peduncle", type: "tube", pts: [[-.06, .001, 0, .009], [-.085, .001, 0, .0055]], k: .006, color: v.t },
    { id: "head", type: "ell", c: [.07, -.001, 0], r: [.038, .024, .0135], k: .008, color: v.b },
    { id: "snout", type: "ell", c: [.1, -.003, 0], r: [.014, .009, .0078], k: .005, color: v.t },
    { id: "chin", type: "ell", c: [.085, -.013, 0], r: [.022, .007, .009], k: .005, color: pale },
    // (the operculum's rear edge a raised dark rim, the mouth's line, the lateral line painted on: each a couple of the
    // mesh's cells across so it holds together rather than breaking into beads)
    { id: "gill", type: "tube", pts: [[.058, .016, .011, .0022], [.0505, .004, .0134, .0022], [.0535, -.01, .0131, .0022], [.062, -.019, .0104, .0018]], k: .0012, kc: .0006, color: gillC, mirror: true },
    { id: "mouth", type: "tube", pts: [[.108, -.004, .0062, .0018], [.1005, -.0072, .0082, .0018]], k: .0008, kc: .0005, color: dark, mirror: true },
    { id: "line", type: "tube", pts: [[.045, .006, .0123, .0019], [0, .004, .0127, .0019], [-.04, .002, .0111, .0017], [-.07, .001, .0089, .0015]], k: .0007, kc: .0003, color: lineC, mirror: true },
    // fins: thin plates (details), the caudal forked on the tail's bone
    { id: "dorsal", type: "tri", a: [-.02, .026, 0], b: [.03, .026, 0], c: [-.012, .056, 0], r: .0015, color: finC },
    { id: "dorsal2", type: "tri", a: [-.02, .026, 0], b: [-.012, .056, 0], c: [-.03, .03, 0], r: .0015, color: finC },
    { id: "anal", type: "tri", a: [-.04, -.017, 0], b: [-.065, -.012, 0], c: [-.06, -.032, 0], r: .0013, color: finC },
    { id: "pelvic", type: "tri", a: [.005, -.026, .006], b: [-.022, -.026, .008], c: [-.02, -.04, .014], r: .0012, color: finC, mirror: true },
    { id: "pectoral", type: "tri", bone: "body", a: [.055, -.012, .012], b: [.03, -.02, .026], c: [.035, -.026, .018], r: .0012, color: finC, mirror: true },
    { id: "caudalU", type: "tri", bone: "tail", a: [-.084, .003, 0], b: [-.142, .042, 0], c: [-.118, .002, 0], r: .0014, color: tailC },
    { id: "caudalD", type: "tri", bone: "tail", a: [-.084, -.002, 0], b: [-.14, -.038, 0], c: [-.118, -.001, 0], r: .0014, color: tailC },
    { id: "caudalM", type: "tri", bone: "tail", a: [-.082, .006, 0], b: [-.082, -.006, 0], c: [-.112, 0, 0], r: .0016, color: tailC },
  ];
  return { name: "fish", fly: { alt: [.3, 1.1], speed: [.4, 1.2], hz: 3 }, parts: [
    // the rig: the body (a spindle, forward along a -> b) and the tail that beats
    { id: "body", parent: null, shape: "tube", size: { a: [-.1 * k, 0, 0], c: [0, .004 * k, 0], b: [.1 * k, 0, 0], r1: .014 * k, r2: .012 * k, bulge: .04 * k }, pos: [0, 0, 0], color: v.b },
    { id: "tail", parent: "body", shape: "tri", pos: [-.075 * k, 0, 0],
      size: { a: [0, 0, 0], b: [-.065 * k, .04 * k, 0], c: [-.065 * k, -.035 * k, 0], r: .012 * k }, color: v.t,
      anim: { axis: "y", deg: 24, speed: 3, phase: 0 } },
  ], sculptScale: k,   // (the overlay written at k = 1, scaled by the engine: bodyspec.js scaleOverlay)
           sculpt: { keep: [], patScale: .032, mesh: { tris: [2200, 700] }, shape,
               eyes: { at: [.082, .007, .012], from: [.075, .006, 0], r: .0054, color: 0x101010, iris: 0xb89a70, pupil: "round", lid: v.b, sink: .35, bone: "body" } } };
}

// The lake's big swimmers. Same swimmer plumbing as the fish; real sizes (dolphin ~2.6m, shark ~3.2m). The dolphin's
// tail pitches (axis z), the shark's sweeps sideways (axis y) -- true to how each actually swims -- each tail on two
// bones (stock and fin, a beat apart). SCULPTED (2026-11-05, the sculpt overlay): see each below.
// A bottlenose: the beak short under a rounded melon, the girth greatest 40% back, a falcate dorsal fin mid-back, the
// pectoral flippers swept back, a laterally flattened tail stock to broad notched flukes; countershaded -- a dark cape
// over grey flanks and a pale belly; the mouth's upturned line, the blowhole on top
export function makeDolphin() {
  const cape = 0x4e5a66, c = 0x7c8a96, pale = 0xdcdcd8, dark = 0x3e4852;
  const shape = [
    { id: "trunk", type: "tube", pts: [[.96, .0, 0, .11], [.75, .03, 0, .19], [.42, .03, 0, .23], [.05, .02, 0, .2], [-.3, .02, 0, .14], [-.55, .02, 0, .1], [-.75, .02, 0, .07]], k: .04, color: cape },
    { id: "flank", type: "ell", c: [.3, -.01, 0], r: [.78, .14, .238], k: .04, kc: .07, color: c },
    { id: "melon", type: "ell", c: [.9, .075, 0], r: [.15, .13, .125], k: .03, color: cape },
    { id: "beak", type: "tube", pts: [[.97, -.035, 0, .065], [1.08, -.038, 0, .046], [1.17, -.036, 0, .03]], k: .02, color: c },
    { id: "belly", type: "ell", c: [.38, -.09, 0], r: [.7, .14, .17], k: .05, kc: .1, color: pale },
    { id: "chin", type: "ell", c: [1.02, -.06, 0], r: [.16, .04, .06], k: .02, kc: .03, color: pale },
    { id: "mouth", type: "tube", pts: [[1.17, -.045, .012, .008], [1.08, -.05, .04, .008], [.98, -.04, .078, .008], [.92, -.022, .1, .007]], k: .004, kc: .005, color: dark, mirror: true },
    { id: "blowhole", type: "ell", c: [.7, .225, 0], r: [.012, .01, .03], op: "sub", k: .01, color: dark },
    { id: "dorsal", type: "tri", a: [-.12, .2, 0], b: [.24, .21, 0], c: [.02, .36, 0], r: .03, k: .04, color: cape },
    { id: "dorsalTip", type: "tri", a: [-.12, .2, 0], b: [.02, .35, 0], c: [-.22, .47, 0], r: .022, k: .03, color: cape },
    { id: "stock", bone: "tailStock", type: "tube", pts: [[-.6, .02, 0, .085], [-.8, .02, 0, .062], [-1.0, .02, 0, .04]], k: .04, color: cape },
    { id: "keel", bone: "tailStock", type: "ell", c: [-.76, .02, 0], r: [.3, .11, .045], k: .05, color: cape },
    { id: "fluke", bone: "fluke", type: "tri", a: [-.98, .02, .03], b: [-1.24, .03, .34], c: [-1.2, .025, .06], r: .024, k: .03, color: cape, mirror: true },
    { id: "flukeTE", bone: "fluke", type: "tri", a: [-1.2, .025, .06], b: [-1.24, .03, .34], c: [-1.27, .025, .04], r: .02, k: .03, color: cape, mirror: true },
    { id: "pect", bone: "pectL", type: "tri", a: [.64, -.09, .15], b: [.3, -.26, .38], c: [.44, -.17, .17], r: .026, k: .04, color: dark, mirror: true },
  ];
  return markSculpt({ name: "dolphin", fly: { alt: [.6, 1.8], speed: [1.5, 3.2], hz: 1.1 }, parts: [
    { id: "body", parent: null, shape: "tube", size: { a: [-.55, .02, 0], c: [.2, .03, 0], b: [.95, 0, 0], r1: .12, r2: .14, bulge: .1 }, pos: [0, 0, 0], color: c },
    { id: "pectL", parent: "body", shape: "tri", size: { a: [0, 0, 0], b: [-.3, -.15, .22], c: [-.13, -.1, .03], r: .02 }, pos: [.6, -.09, .14], color: dark,
      anim: { axis: "x", deg: 6, speed: .55, phase: 0 } },
    { id: "pectR", parent: "body", shape: "tri", size: { a: [0, 0, 0], b: [-.3, -.15, -.22], c: [-.13, -.1, -.03], r: .02 }, pos: [.6, -.09, -.14], color: dark,
      anim: { axis: "x", deg: -6, speed: .55, phase: 0 } },
    { id: "tailStock", parent: "body", shape: "tube", size: { a: [0, 0, 0], c: [-.22, 0, 0], b: [-.45, 0, 0], r1: .1, r2: .05 }, pos: [-.55, .02, 0], color: c,
      anim: { axis: "z", deg: 12, speed: 1.1, phase: 0 } },   // pitches: the flukes beat up and down
    { id: "fluke", parent: "tailStock", shape: "tri", size: { a: [0, 0, 0], b: [-.27, .01, .3], c: [-.27, .01, -.3], r: .02 }, pos: [-.45, 0, 0], color: cape,
      anim: { axis: "z", deg: 14, speed: 1.1, phase: -.9 } },
  ], sculpt: { keep: [], mesh: { tris: [4200, 1300] }, shape,
               eyes: { at: [.83, .01, .15], from: [.83, .01, 0], r: .018, color: 0x121416, iris: 0x2a2018, pupil: "round", lid: dark, sink: .4, bone: "body" } } });
}
// A grey shark (a great white's build): the conical snout over an underslung mouth, the girth greatest a third back,
// five gill slits, a tall triangular first dorsal, the small second dorsal and anal fins, long falcate pectorals,
// pelvic fins, the caudal keel and a near-lunate tail (its upper lobe the longer) on the tail's own bone; sharply
// countershaded -- slate above, white below
export function makeShark() {
  const c = 0x6a7882, pale = 0xe4e4e0, dark = 0x2a3036, fin = 0x5e6c76;
  const gills = [0, 1, 2, 3, 4].map((i) => ({ id: `gill${i}`, type: "ell", c: [.76 - i * .055, -.01, .24 - i * .002], r: [.008, .085 - i * .004, .035], rot: [0, 0, -8], op: "sub", k: .008, color: dark, mirror: true }));
  const shape = [
    { id: "trunk", type: "tube", pts: [[1.28, -.02, 0, .03], [1.18, .0, 0, .09], [.95, .02, 0, .2], [.6, .04, 0, .26], [.25, .04, 0, .27], [-.15, .03, 0, .22], [-.5, .02, 0, .15], [-.8, .02, 0, .085], [-1.0, .02, 0, .065]], k: .05, color: c },
    { id: "snoutF", type: "ell", c: [1.1, .01, 0], r: [.2, .1, .13], k: .05, color: c },
    { id: "belly", type: "ell", c: [.25, -.13, 0], r: [.95, .16, .22], k: .05, kc: .05, color: pale },
    { id: "jaw", type: "ell", c: [.98, -.1, 0], r: [.25, .08, .15], k: .05, kc: .05, color: pale },
    { id: "mouth", type: "tube", pts: [[1.12, -.105, 0, .012], [1.05, -.12, .07, .012], [.92, -.115, .13, .011], [.84, -.09, .16, .009]], k: .008, kc: .006, color: dark, mirror: true },
    { id: "nostril", type: "ell", c: [1.2, -.03, .055], r: [.025, .008, .012], op: "sub", k: .005, color: dark, mirror: true },
    ...gills,
    { id: "dorsal", type: "tri", a: [-.08, .25, 0], b: [.36, .25, 0], c: [-.06, .76, 0], r: .03, k: .05, color: fin },
    { id: "dorsalTE", type: "tri", a: [-.08, .25, 0], b: [-.06, .76, 0], c: [-.18, .28, 0], r: .022, k: .03, color: fin },
    { id: "dorsal2", type: "tri", a: [-.72, .09, 0], b: [-.6, .09, 0], c: [-.75, .18, 0], r: .012, k: .02, color: fin },
    { id: "anal", type: "tri", a: [-.76, -.05, 0], b: [-.64, -.06, 0], c: [-.78, -.14, 0], r: .012, k: .02, color: fin },
    { id: "pelvic", type: "tri", a: [-.32, -.17, .06], b: [-.48, -.15, .06], c: [-.52, -.24, .14], r: .016, k: .02, color: fin, mirror: true },
    { id: "keel", bone: "tailStock", type: "ell", c: [-1.02, .02, 0], r: [.14, .045, .085], k: .03, color: c },
    { id: "lobeU", bone: "tail", type: "tri", a: [-1.08, .05, 0], b: [-1.55, .62, 0], c: [-1.22, .06, 0], r: .022, k: .03, color: fin },
    { id: "lobeU2", bone: "tail", type: "tri", a: [-1.22, .06, 0], b: [-1.55, .62, 0], c: [-1.32, .22, 0], r: .018, k: .02, color: fin },
    { id: "lobeD", bone: "tail", type: "tri", a: [-1.08, -.01, 0], b: [-1.45, -.4, 0], c: [-1.22, .02, 0], r: .02, k: .03, color: fin },
    { id: "pect", bone: "pectL", type: "tri", a: [.6, -.14, .17], b: [.12, -.44, .62], c: [.38, -.2, .2], r: .028, k: .05, color: fin, mirror: true },
    { id: "pectU", bone: "pectL", type: "tri", a: [.38, -.2, .2], b: [.12, -.44, .62], c: [.1, -.34, .42], r: .018, k: .02, color: fin, mirror: true },
  ];
  return markSculpt({ name: "shark", fly: { alt: [.4, 1.4], speed: [1.2, 2.4], hz: .7 }, parts: [
    { id: "body", parent: null, shape: "tube", size: { a: [-.75, .02, 0], c: [.2, .05, 0], b: [1.1, 0, 0], r1: .14, r2: .2, bulge: .12 }, pos: [0, 0, 0], color: c },
    { id: "pectL", parent: "body", shape: "tri", size: { a: [0, 0, 0], b: [-.48, -.3, .45], c: [-.22, -.06, .03], r: .02 }, pos: [.6, -.14, .17], color: fin },
    { id: "pectR", parent: "body", shape: "tri", size: { a: [0, 0, 0], b: [-.48, -.3, -.45], c: [-.22, -.06, -.03], r: .02 }, pos: [.6, -.14, -.17], color: fin },
    { id: "tailStock", parent: "body", shape: "tube", size: { a: [0, 0, 0], c: [-.15, 0, 0], b: [-.3, 0, 0], r1: .12, r2: .065 }, pos: [-.78, .02, 0], color: c,
      anim: { axis: "y", deg: 12, speed: .7, phase: 0 } },   // sweeps: the tail beats side to side
    { id: "tail", parent: "tailStock", shape: "tri", size: { a: [0, 0, 0], b: [-.45, .6, 0], c: [-.4, -.42, 0], r: .02 }, pos: [-.3, 0, 0], color: fin,
      anim: { axis: "y", deg: 16, speed: .7, phase: -.9 } },
  ], sculpt: { keep: [], mesh: { tris: [4200, 1400] }, shape,
               eyes: { at: [1.02, .07, .14], from: [1.0, .06, 0], r: .022, color: 0x08090a, iris: 0x14161a, pupil: "round", lid: dark, sink: .4, bone: "body" } } });
}

