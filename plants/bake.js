// THE PLANTS' TEXTURES (2026-11-18), painted once at load -- no image files:
//
//   BARK   a tileable square per species: a HEIGHT field (the bark's relief: plates, ridges, fissures, rings,
//          lenticels -- `bark` in species.js picks the recipe) turned into an ALBEDO (the fissures dark, the plates'
//          faces in the species' bark colour, mottled; lichen on the old ones) and a NORMAL map (the relief's slope),
//          sampled round and along every branch (mesh.js: an integer number of tiles round, so no seam).
//   SPRAYS an atlas per species (and per bush fruit): five columns of 256 x 512 --
//            0, 1   two twig sprays in leaf: a twig with its leaves, painted from its base (the bottom edge, v = 0)
//                   toward its tip (v = 1) as a botanist would draw it -- the species' leaf shape and arrangement,
//                   each leaf shaded across its midrib, a few turned to show their paler undersides, the near ones
//                   over the far ones with a soft shadow
//            2      the same spray in flower (blossom, the ceiba's pink flowers, a horse chestnut's candles)
//            3      the same spray in fruit (apples, cherries, berries, acorns, cones) -- a leafy one where the species
//                   has no flowers or no fruit
//            4      column 0's spray FILLED: laid over copies of itself shifted round a small ring, a little in
//                   shade, so the gaps between its leaves close with its own leaves -- the far levels' cards
//                   (mesh.js leafMesh lod 1, 2: fewer, bigger, the same places), nearly solid, so a far crown needs
//                   few layers of them
//          The colours are the species' own (species.js colors); the shaders only vary them per tree and turn them
//          in autumn. The cut edges: the alpha is the leaves' coverage, and the colour is bled out past it so
//          filtering and mip-mapping never pull black into the edges.
// Everything is drawn with a seeded stream, so the bakes are the same on every load.
import * as THREE from "three";
import { rng } from "../rng.js";
import { BODY_BANDS, FAN_W } from "./mesh.js";

const TAU = Math.PI * 2;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
const rgbOf = (hex) => [(hex >> 16) & 255, (hex >> 8) & 255, hex & 255];
const mix3 = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
const css = (c, a = 1) => `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a})`;
const shade = (c, k) => c.map((v) => clamp(v * k, 0, 255));

// ---- periodic noise: value noise on a lattice that wraps every `per` cells, so the tile repeats seamlessly
function hash2(x, y, s) { let h = (x * 374761393 + y * 668265263 + s * 2147483647) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; }
function pnoise(x, y, px, py, s) {
  const xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi;
  const u = fx * fx * (3 - 2 * fx), v = fy * fy * (3 - 2 * fy);
  const w = (i, j) => hash2(((xi + i) % px + px) % px, ((yi + j) % py + py) % py, s);
  return (w(0, 0) * (1 - u) + w(1, 0) * u) * (1 - v) + (w(0, 1) * (1 - u) + w(1, 1) * u) * v;
}
// fractal sum over the unit tile: (x, y) in 0..1, base cells (px, py)
function fbm(x, y, px, py, oct, s) {
  let a = 0, amp = .5, n = 0;
  for (let o = 0; o < oct; o++) { a += amp * pnoise(x * px, y * py, px, py, s + o * 17); n += amp; amp *= .5; px *= 2; py *= 2; }
  return a / n;
}
// cellular (Worley) over the unit tile with gx x gy cells: the distances to the nearest and second-nearest seed,
// in the cells' own units (sx stretches across: an elongated plate)
function worley(x, y, gx, gy, s) {
  const X = x * gx, Y = y * gy, xi = Math.floor(X), yi = Math.floor(Y);
  let f1 = 9, f2 = 9, id = 0;
  for (let j = -1; j <= 1; j++) for (let i = -1; i <= 1; i++) {
    const cx = xi + i, cy = yi + j, wx = ((cx % gx) + gx) % gx, wy = ((cy % gy) + gy) % gy;
    const px = cx + hash2(wx, wy, s), py = cy + hash2(wx, wy, s + 9);
    const d = Math.hypot(X - px, Y - py);
    if (d < f1) { f2 = f1; f1 = d; id = hash2(wx, wy, s + 5); } else if (d < f2) f2 = d;
  }
  return [f1, f2, id];
}

// ---- BARK: a height field and colour per texel, by recipe. Each returns { h: 0..1 relief, c: 0..1 colour mix
// toward the dark, t: an extra tone (-1..1: the recipe's own patches), rel: how strong its relief reads }
const BARK = {
  // deep furrows between long blocky ridges, cracked across now and then (oak)
  furrowed: (x, y, s) => {
    // (the cells are worked out in a space squeezed up and down: each ridge 4-5 times as long as it is wide)
    const wx = x + .06 * fbm(x, y, 3, 2, 3, s + 1);
    const [f1, f2] = worley(wx, y, 9, 2, s);
    const e = f2 - f1, ridge = smooth(.02, .3, e), grain = fbm(x, y, 40, 4, 3, s + 2);
    const h = ridge * (.55 + .45 * grain) * (.85 + .15 * fbm(x, y, 6, 3, 2, s + 4));
    return { h, c: 1 - smooth(0, .5, h), t: fbm(x, y, 3, 3, 3, s + 3) * 2 - 1 };
  },
  // a maple's: shallower, finer, the ridges narrower and more broken
  fissured: (x, y, s) => {
    const wx = x + .04 * fbm(x, y, 4, 2, 3, s + 1);
    const [f1, f2] = worley(wx, y, 12, 3, s);
    const h = smooth(0, .22, f2 - f1) * (.7 + .3 * fbm(x, y, 40, 6, 3, s + 2));
    return { h, c: .8 - .8 * h, t: fbm(x, y, 4, 4, 2, s + 3) * 2 - 1 };
  },
  // a willow's: long interlacing ridges, a net of shallow diamonds
  ridged: (x, y, s) => {
    const a = Math.abs(Math.sin((x * 9 + .9 * fbm(x, y, 3, 2, 3, s)) * Math.PI + y * 2 * Math.PI));
    const b = Math.abs(Math.sin((x * 9 - .9 * fbm(x, y, 3, 2, 3, s + 4)) * Math.PI - y * 2 * Math.PI));
    const h = Math.pow(Math.max(a, b), 1.6) * (.7 + .3 * fbm(x, y, 20, 10, 3, s + 2));
    return { h, c: 1 - h, t: fbm(x, y, 3, 3, 2, s + 3) * 2 - 1 };
  },
  // a pine's: big flat plates, red-brown on their faces, grey-black in the cracks between
  pine: (x, y, s) => {
    const wx = x + .03 * fbm(x, y, 5, 3, 2, s + 1);
    const [f1, f2, id] = worley(wx, y, 5, 3, s);
    const e = f2 - f1, h = smooth(0, .12, e) * (.75 + .25 * fbm(x, y, 18, 10, 3, s + 2)) * (.85 + .15 * id);
    const flake = smooth(.5, .7, fbm(x, y, 12, 8, 3, s + 6)) * .25;   // flakes lifting off the plates' faces
    return { h: h - flake * h, c: 1 - smooth(0, .08, e), t: (id * 2 - 1) * .6 + flake * 2 };
  },
  // a spruce's: small round scales
  scaly: (x, y, s) => {
    const [f1, f2, id] = worley(x, y, 14, 9, s);
    const h = smooth(0, .3, f2 - f1) * (1 - .4 * f1);
    return { h, c: 1 - smooth(0, .2, f2 - f1), t: id * 2 - 1 };
  },
  // a cypress's: fine fibres running up, shredding in strips
  stringy: (x, y, s) => {
    const wx = x + .02 * fbm(x, y, 4, 1, 3, s);
    const f = fbm(wx, y, 40, 2, 4, s + 1), strip = Math.abs(Math.sin((wx * 14 + fbm(x, y, 3, 1, 2, s + 2)) * Math.PI));
    const h = clamp(.55 * f + .45 * Math.pow(strip, .5), 0, 1);
    return { h, c: 1 - h, t: fbm(x, y, 6, 2, 2, s + 3) * 2 - 1 };
  },
  // an apple's: grey-brown, flaking off in scales that show the paler bark under them
  flaky: (x, y, s) => {
    const [f1, f2, id] = worley(x, y, 6, 5, s);
    const e = f2 - f1, h = smooth(0, .18, e) * (.7 + .3 * fbm(x, y, 20, 14, 3, s + 2));
    return { h, c: 1 - smooth(0, .1, e) * .9, t: id > .62 ? 1 : (fbm(x, y, 4, 4, 2, s + 3) * 2 - 1) * .5 };
  },
  // a birch's: white, papery, scored across by dark lenticels, black diamonds where a branch was
  birch: (x, y, s) => {
    let len = 0;
    const row = Math.floor(y * 30), ry = y * 30 - row, off = hash2(row, 0, s);
    const seg = (x + off) * 4 % 1, on = hash2(row, Math.floor((x + off) * 4), s + 3), w = .2 + .5 * hash2(row, Math.floor((x + off) * 4), s + 8);
    if (on > .5) len = smooth(.2, .08, Math.abs(ry - .5)) * smooth(0, .04, seg) * smooth(w, w * .8, seg);
    const blot = smooth(.7, .8, fbm(x, y, 4, 7, 4, s + 7)) * smooth(.45, .6, fbm(x, y, 2, 3, 2, s + 11));
    const peel = fbm(x, y, 6, 30, 3, s + 9);
    return { h: 1 - len * .8 - blot * .5 - (peel > .66 ? .2 : 0), c: Math.max(len, blot), t: (peel - .5) * 2 };
  },
  // a cherry's: smooth, shiny red-brown, banded across with long lenticels, peeling in rings
  banded: (x, y, s) => {
    const row = Math.floor(y * 22), ry = y * 22 - row, seg = (x + hash2(row, 1, s)) * 3 % 1;
    const len = hash2(row, Math.floor((x + hash2(row, 1, s)) * 3), s + 1) > .35 ? smooth(.45, .15, Math.abs(ry - .5)) * smooth(0, .15, seg) * smooth(1, .85, seg) : 0;
    const ring = smooth(.6, .8, fbm(x, y, 2, 10, 3, s + 4));
    return { h: .75 - len * .6 + ring * .15 + .1 * fbm(x, y, 20, 20, 2, s + 2), c: len * .9, t: ring * 2 - 1 };
  },
  // a palm's: rings of old leaf scars up the stem, fibrous between
  palm: (x, y, s) => {
    const ry = y * 4 + .15 * fbm(x, y, 3, 1, 2, s), k = ry - Math.floor(ry);
    const scar = smooth(.0, .1, k) * smooth(.4, .12, k);
    const fib = fbm(x, y, 30, 6, 3, s + 1);
    return { h: clamp(.85 - scar * .55 + (fib - .5) * .3, 0, 1), c: scar * .8 + (1 - fib) * .2, t: fbm(x, y, 3, 2, 2, s + 2) * 2 - 1 };
  },
  // a coconut's (a fan palm's below its skirt): smooth and grey, ringed close by the scars of fallen fronds, cracked
  // finely up and down between them
  ringed: (x, y, s) => {
    const ry = y * 9 + .2 * fbm(x, y, 2, 1, 2, s), k = ry - Math.floor(ry);
    const scar = smooth(.0, .06, k) * smooth(.22, .08, k) * (.4 + .6 * fbm(x, y, 6, 2, 2, s + 3));
    const crack = smooth(.1, .02, Math.abs(fbm(x, y, 26, 3, 3, s + 1) - .5));
    const n = fbm(x, y, 10, 8, 3, s + 2);
    return { h: clamp(.8 - scar * .25 - crack * .25 + (n - .5) * .25, 0, 1), c: scar * .3 + crack * .35 + (1 - n) * .15, t: (n - .5) * 2 };
  },
  // a ceiba's: smooth, green-grey (it photosynthesises), streaked up and down, scarred round the prickles
  ceiba: (x, y, s) => {
    const streak = fbm(x, y, 18, 2, 3, s);
    const [f1] = worley(x, y, 5, 5, s + 3);
    const scar = smooth(.14, .05, f1);
    return { h: .7 + (streak - .5) * .35 - scar * .25, c: scar * .5 + (1 - streak) * .25, t: (fbm(x, y, 3, 3, 3, s + 4) - .5) * 2 };
  },
  // a yew's: thin red-brown bark shedding in long strips and flakes, purplish where fresh -- over a fluted bole
  yew: (x, y, s) => {
    const wx = x + .05 * fbm(x, y, 3, 1, 3, s);
    const [f1, f2, id] = worley(wx, y, 10, 2, s + 1);
    const e = f2 - f1, strip = smooth(0, .16, e);
    return { h: strip * (.7 + .3 * fbm(x, y, 30, 6, 3, s + 2)), c: 1 - strip * .85, t: id > .55 ? 1 : (id - .55) * 2 };
  },
  // a plane's: smooth, peeling in jigsaw patches -- olive, cream and grey, the camouflage of a London street
  plane: (x, y, s) => {
    const [f1, f2, id] = worley(x + .04 * fbm(x, y, 4, 4, 2, s), y, 5, 4, s);
    const edge = smooth(.02, .07, f2 - f1);
    return { h: .65 + .25 * edge * (id > .5 ? 1 : .7) + .08 * fbm(x, y, 20, 20, 2, s + 1), c: id < .33 ? .55 : id < .66 ? .15 : .35, t: id > .66 ? 1 : id < .33 ? -.8 : .2 };
  },
  // an old olive's: grey, ploughed by deep twisting fissures into a net of rough, knotted ridges
  olive: (x, y, s) => {
    const tw = x + .35 * y + .1 * fbm(x, y, 3, 2, 3, s);   // (twisting round the trunk as it rises)
    const [f1, f2] = worley(tw, y, 16, 3, s + 1);   // (cells far taller than wide: long ridges between the fissures)
    const ridge = smooth(.02, .22, f2 - f1), knot = smooth(.75, .9, fbm(x, y, 5, 5, 3, s + 4));
    return { h: ridge * (.65 + .35 * fbm(x, y, 30, 12, 3, s + 2)) + knot * .2, c: 1 - ridge * .9, t: fbm(x, y, 3, 3, 2, s + 3) * 2 - 1 };
  },
  // a baobab's: smooth, grey-pink and soft, folded in shallow wrinkles round the bole, marked with old scars
  baobab: (x, y, s) => {
    const fold = Math.sin((y * 9 + .5 * fbm(x, y, 3, 2, 3, s)) * TAU) * .5 + .5, n = fbm(x, y, 8, 8, 3, s + 1);
    const [f1] = worley(x, y, 4, 4, s + 2);
    return { h: .6 + .25 * fold * (.6 + .4 * n) - smooth(.1, .03, f1) * .3, c: (1 - fold) * .35 + smooth(.1, .03, f1) * .4, t: (n - .5) * 2 };
  },
  // a Joshua tree's: a thatch of dead leaves hanging down the arms, grey-brown, over a corky core where they fell
  shaggy: (x, y, s) => {
    const col = Math.floor(x * 40), off = hash2(col, 0, s), ry = (y * 10 + off) % 1;
    const blade = smooth(.25, 0, Math.abs((x * 40 % 1) - .5) - .1 + ry * .25) * (1 - ry * .6);
    const n = fbm(x, y, 6, 6, 2, s + 2);
    return { h: clamp(blade * .9 + .1 * n, 0, 1), c: 1 - blade * .8, t: n > .6 ? -.6 : (n - .5) };
  },
  // a banana's soft stem: the rolled sheaths of old leaves, streaked along it, green under brown dry blotches
  banana: (x, y, s) => {
    const sheath = Math.abs(Math.sin((x * 5 + .3 * fbm(x, y, 2, 1, 2, s)) * Math.PI)), n = fbm(x, y, 6, 3, 3, s + 1), streak = fbm(x, y, 40, 2, 2, s + 2);
    const dry = smooth(.55, .7, fbm(x, y, 4, 3, 3, s + 3));
    return { h: .55 + .3 * Math.pow(sheath, .3) + .1 * streak, c: dry * .8 + (1 - sheath) * .25, t: dry > .3 ? dry : (streak - .5) * .4 };
  },
  // a bamboo cane: smooth green between NODES (a raised ring at the tile's foot, a band of white bloom under it), finely streaked
  bamboo: (x, y, s) => {
    const node = smooth(.045, .015, Math.abs(y - .03)), bloom = smooth(.0, .02, y - .05) * smooth(.16, .07, y), streak = fbm(x, y, 30, 2, 2, s);
    return { h: .6 + .35 * node - .1 * smooth(.1, .06, Math.abs(y - .07)) + .05 * streak, c: node * .5 + (1 - streak) * .15, t: bloom * .9 - node * .3 };
  },
  // a saguaro's skin, one RIB a tile across (mesh.js: its crest at the tile's edge, the groove in its middle): waxy
  // grey-green, paler on the crests, a row of felted areoles down each crest with their spines raying out
  cactus: (x, y, s) => {
    const dx = Math.min(x, 1 - x), groove = smooth(.12, .5, dx), n = fbm(x, y, 4, 8, 3, s);
    const ay = (y * 4) % 1, k = Math.floor(y * 4), ox = (hash2(k, 0, s) - .5) * .03;
    const ex = dx - Math.abs(ox), ey = (ay - .5) * .25, d = Math.hypot(ex, ey);   // (from the areole: tiles are square in metres)
    const areole = smooth(.035, .022, d);
    let spine = 0;
    if (d > .02 && d < .16) {
      const a = Math.atan2(ey, ex), m = 9, f = ((a / TAU * m + hash2(k, 1, s) * m) % 1 + 1) % 1;
      const len = .07 + .09 * hash2(k, Math.floor(a / TAU * m + 9), s);
      spine = smooth(.012 / d * 1.2, 0, Math.abs(f - .5) / m * TAU) * smooth(len, len * .7, d);
    }
    return { h: clamp((1 - groove) * .75 + .08 * n + areole * .25 + spine * .1, 0, 1), c: groove * .55 + (1 - n) * .2 + areole * .5,
             t: Math.max(spine, (1 - groove) * .25, (n - .5) * .3) };
  },
  // a shrub's stems: smooth with fine lenticels
  smooth: (x, y, s) => {
    const n = fbm(x, y, 12, 6, 3, s);
    const [f1] = worley(x, y, 16, 10, s + 2);
    return { h: .7 + (n - .5) * .3 - smooth(.12, .04, f1) * .3, c: (1 - n) * .3 + smooth(.12, .04, f1) * .4, t: (n - .5) * 2 };
  },
};
// how strongly each recipe's relief tilts the normal, and the colour its third tone pulls toward
const BARK_LOOK = {
  furrowed: { rel: 5, tone: [104, 112, 82], toneK: .25 },   // (grey-green lichen on the ridges)
  fissured: { rel: 3.5, tone: [92, 96, 80], toneK: .2 },
  ridged: { rel: 3.5, tone: [96, 98, 84], toneK: .2 },
  pine: { rel: 4, tone: [176, 104, 62], toneK: .45 },        // (the plates' orange faces)
  scaly: { rel: 3, tone: [140, 92, 70], toneK: .3 },
  stringy: { rel: 3, tone: [150, 112, 88], toneK: .3 },
  flaky: { rel: 2.5, tone: [150, 140, 112], toneK: .4 },     // (the paler under-bark)
  birch: { rel: 1.5, tone: [236, 232, 222], toneK: .15 },
  banded: { rel: 1.5, tone: [150, 92, 76], toneK: .25 },
  palm: { rel: 3, tone: [120, 104, 84], toneK: .2 },
  ringed: { rel: 2, tone: [150, 146, 130], toneK: .3 },      // (the pale grey between the rings)
  ceiba: { rel: 1.5, tone: [120, 148, 98], toneK: .35 },     // (greener patches)
  smooth: { rel: 1.5, tone: [110, 96, 80], toneK: .2 },
  yew: { rel: 2.5, tone: [150, 70, 60], toneK: .45 },       // (the fresh purple-red under the strips)
  plane: { rel: 1.2, tone: [214, 206, 168], toneK: .7 },     // (the cream patches)
  olive: { rel: 5, tone: [128, 128, 112], toneK: .3 },
  baobab: { rel: 2, tone: [176, 150, 140], toneK: .3 },      // (pinkish)
  shaggy: { rel: 4, tone: [80, 70, 60], toneK: .3 },
  cactus: { rel: 3, tone: [196, 190, 168], toneK: .8 },
  banana: { rel: 1.5, tone: [128, 96, 62], toneK: .7 },        // (the dry brown sheaths)
  bamboo: { rel: 2, tone: [206, 212, 186], toneK: .55 },      // (the white bloom under a node)       // (the pale spines and crests)
};

// BARK of a species: { map, normalMap } (DataTextures, repeating); N the tile's side in texels
export function bakeBark(S, seed = 1, N = 256) {
  const recipe = BARK[S.bark] ?? BARK.smooth, look = BARK_LOOK[S.bark] ?? BARK_LOOK.smooth;
  const light = rgbOf(S.colors.bark), dark = rgbOf(S.colors.barkDark);
  const H = new Float32Array(N * N), col = new Uint8Array(N * N * 4), nrm = new Uint8Array(N * N * 4);
  const s = (seed * 131 + S.bark.length * 7) | 0;
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const q = recipe((i + .5) / N, (j + .5) / N, s), k = j * N + i;
    H[k] = q.h;
    let c = mix3(light, dark, clamp(q.c, 0, 1));
    if (q.t > 0) c = mix3(c, look.tone, q.t * look.toneK);
    else c = shade(c, 1 + q.t * .12);
    c = shade(c, .78 + .32 * clamp(q.h, 0, 1));   // (the hollows in their own shade)
    col[k * 4] = c[0]; col[k * 4 + 1] = c[1]; col[k * 4 + 2] = c[2]; col[k * 4 + 3] = 255;
  }
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const h = (a, b) => H[((b + N) % N) * N + ((a + N) % N)];
    const dx = (h(i + 1, j) - h(i - 1, j)) * look.rel, dy = (h(i, j + 1) - h(i, j - 1)) * look.rel;
    const l = Math.hypot(dx, dy, 1), k = (j * N + i) * 4;
    nrm[k] = (-dx / l * .5 + .5) * 255; nrm[k + 1] = (-dy / l * .5 + .5) * 255; nrm[k + 2] = (1 / l * .5 + .5) * 255; nrm[k + 3] = 255;
  }
  return { map: dataTex(col, N, N, true), normalMap: dataTex(nrm, N, N, false) };
}

function dataTex(data, w, h, srgb) {
  const t = new THREE.DataTexture(data, w, h, THREE.RGBAFormat);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.magFilter = THREE.LinearFilter;
  t.minFilter = THREE.LinearMipmapLinearFilter;
  t.generateMipmaps = true;
  t.anisotropy = 8;
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.needsUpdate = true;
  return t;
}

// ---- SPRAYS ---------------------------------------------------------------------------------------------------
const CW = 256, CH = 512;   // a cell
function canvas(w, h) {
  if (typeof OffscreenCanvas !== "undefined") return new OffscreenCanvas(w, h);
  const c = document.createElement("canvas"); c.width = w; c.height = h; return c;
}

// a leaf's outline as a path, from its base (0, 0) along +y to its tip (0, len); w its half-width
function leafPath(g, kind, len, w, r) {
  g.beginPath();
  if (kind === "oak") {   // lobed: 4-5 rounded lobes a side, deepest at the middle
    const lobes = 4 + (r() < .5 ? 1 : 0);
    g.moveTo(0, 0);
    for (const side of [1, -1]) {
      if (side < 0) g.moveTo(0, len);
      for (let i = 0; i <= lobes; i++) {
        const t = side > 0 ? i / lobes : 1 - i / lobes;
        const env = Math.sin(Math.PI * clamp(.08 + t * .92, 0, 1)) * (t < .2 ? .7 : 1);
        const y = t * len, ww = w * env;
        if (i === 0) continue;
        const tp = side > 0 ? (i - .5) / lobes : 1 - (i - .5) / lobes, yp = tp * len;
        g.quadraticCurveTo(side * w * 1.25 * Math.sin(Math.PI * clamp(.08 + tp * .92, 0, 1)), yp, side * ww * .55, y);
      }
      g.lineTo(0, side > 0 ? len : 0);
    }
  } else if (kind === "maple" || kind === "palmate") {   // five pointed lobes from the petiole's end
    const n = 5, pts = [];
    for (let i = 0; i < n; i++) {
      const a = (i - (n - 1) / 2) / ((n - 1) / 2) * 1.35, L = len * (i === 2 ? 1 : i === 1 || i === 3 ? .88 : .6);
      pts.push([Math.sin(a) * L, Math.cos(a) * L, a]);
    }
    g.moveTo(0, -len * .05);
    for (let i = 0; i < n; i++) {
      const [x, y, a] = pts[i], sn = len * .32;
      g.lineTo(Math.sin(a - .28) * sn * 1.4, Math.cos(a - .28) * sn * 1.4);
      g.lineTo(x * .62 + Math.cos(a) * w * .25, y * .62 - Math.sin(a) * w * .25);
      g.lineTo(x, y);
      g.lineTo(x * .62 - Math.cos(a) * w * .25, y * .62 + Math.sin(a) * w * .25);
      g.lineTo(Math.sin(a + .28) * sn * 1.4, Math.cos(a + .28) * sn * 1.4);
    }
    g.closePath();
  } else if (kind === "triangle") {   // a birch's: a pointed triangle, toothed
    const teeth = 7;
    g.moveTo(0, 0);
    for (let i = 0; i <= teeth; i++) { const t = i / teeth; g.lineTo(w * (1 - t) * (i % 2 ? 1.06 : .96) * (t < .1 ? t / .1 * .9 + .1 : 1), len * (.12 + .88 * t)); }
    for (let i = teeth; i >= 0; i--) { const t = i / teeth; g.lineTo(-w * (1 - t) * (i % 2 ? 1.06 : .96) * (t < .1 ? t / .1 * .9 + .1 : 1), len * (.12 + .88 * t)); }
    g.closePath();
  } else if (kind === "obovate") {   // widest beyond the middle, a short point: a horse chestnut's leaflet, a magnolia's
    g.moveTo(0, 0);
    g.bezierCurveTo(w * .5, len * .15, w * 1.25, len * .55, w * .7, len * .9);
    g.quadraticCurveTo(w * .25, len * 1.02, 0, len);
    g.quadraticCurveTo(-w * .25, len * 1.02, -w * .7, len * .9);
    g.bezierCurveTo(-w * 1.25, len * .55, -w * .5, len * .15, 0, 0);
  } else if (kind === "heart" || kind === "vine" || kind === "tulip") {
    // round a middle a share up the leaf: R(th) from the tip (th 0) round to the stalk (pi), a notch at the stalk
    //   heart  a linden's, a hazel's: heart-shaped, pointed, finely toothed, a little lopsided
    //   vine   a grapevine's: rounded, three to five shallow lobes, coarsely toothed
    //   tulip  a tulip tree's: four lobes, the tip cut square across
    const mid = kind === "vine" ? .45 : .42, notch = kind === "tulip" ? .35 : .45;
    const R = (th) => {
      const a = Math.abs(th);
      if (kind === "heart") return .42 * (1 + .4 * Math.pow(Math.max(0, Math.cos(th)), 4)) * (1 + .025 * Math.sin(th * 38)) * (th < 0 ? 1.07 : 1);
      if (kind === "vine") return .47 * (1 - .22 * Math.pow(Math.abs(Math.sin(th * 2.5)), .7)) * (1 + .04 * Math.sin(th * 34));
      const r0 = .5 * (1 - .32 * Math.exp(-(((a - 1.2) / .2) ** 2)));
      return a < Math.PI / 2 ? Math.min(r0, (.36 + .05 * a) / Math.max(.05, Math.cos(th))) : r0;
    };
    const n = 90, aspect = w / (len * .42);
    g.moveTo(0, len * .12);
    for (let i = 0; i <= n; i++) {
      const th = -Math.PI + notch + (TAU - 2 * notch) * i / n;
      g.lineTo(Math.sin(th) * R(th) * len * aspect, len * mid + Math.cos(th) * R(th) * len);
    }
    g.closePath();
  } else if (kind === "toothed") {   // a broad oval, its edge sawn into small forward teeth (a hydrangea's)
    const n = 14, side = (sd) => { for (let i = 1; i <= n; i++) { const t = i / n, e = Math.pow(Math.sin(Math.PI * Math.min(1, t * .95 + .03)), .8);
      g.lineTo(sd * w * e * 1.06, len * (t - .5 / n)); g.lineTo(sd * w * e * .93, len * t); } };
    g.moveTo(0, 0); side(1); g.lineTo(0, len); g.moveTo(0, 0); side(-1); g.lineTo(0, len); g.closePath();
  } else if (kind === "fan") {       // a ginkgo's: a fan on a long stalk, its rim wavy and notched in the middle
    const p0 = len * .4, R = len * .6, A = 1.08, ax = w / (R * Math.sin(A)), n = 40;
    g.moveTo(-len * .012, 0); g.lineTo(-len * .012, p0);
    for (let i = 0; i <= n; i++) {
      const th = -A + 2 * A * i / n, rr = R * (1 - .22 * Math.exp(-((th / .1) ** 2))) * (1 + .03 * Math.sin(th * 23));
      g.lineTo(Math.sin(th) * rr * ax, p0 + Math.cos(th) * rr);
    }
    g.lineTo(len * .012, p0); g.lineTo(len * .012, 0); g.closePath();
  } else if (kind === "sword") {     // a long stiff blade, parallel-sided, to a sharp point: a dracaena's, a yucca's
    g.moveTo(-w * .7, 0); g.lineTo(-w, len * .15); g.lineTo(-w * .8, len * .8); g.lineTo(0, len); g.lineTo(w * .8, len * .8); g.lineTo(w, len * .15); g.lineTo(w * .7, 0);
    g.closePath();
  } else {   // oval / lance: a smooth pointed ellipse, widest a little below the middle
    const wide = kind === "lance" ? .4 : .42;
    g.moveTo(0, 0);
    g.bezierCurveTo(w * 1.1, len * wide * .5, w * 1.05, len * (wide + .3), 0, len);
    g.bezierCurveTo(-w * 1.05, len * (wide + .3), -w * 1.1, len * wide * .5, 0, 0);
  }
}

// one leaf on the canvas at (x, y), pointing at angle a (0: up the cell), shaded across its midrib
function leaf(g, r, x, y, a, len, w, kind, base, opt = {}) {
  g.save();
  g.translate(x, y); g.rotate(Math.PI - a);   // (canvas y runs down: a leaf drawn along +y, turned to point up)
  const under = r() < (opt.under ?? .18);       // turned over: its paler, greyer underside
  let c = shade(base, .82 + .36 * r());
  if (under) c = mix3(c, opt.underC ?? [190, 205, 170], opt.underK ?? .35);   // (an olive's silver, a magnolia's rust)
  if (opt.dry && r() < opt.dry) c = mix3(c, [150, 130, 70], .5);
  g.shadowColor = "rgba(10,20,5,0.45)"; g.shadowBlur = opt.blur ?? 5; g.shadowOffsetY = -2;
  leafPath(g, kind, len, w, r);
  const grad = g.createLinearGradient(-w, 0, w, 0), side = r() < .5 ? 1 : -1;
  grad.addColorStop(0, css(shade(c, side > 0 ? 1.12 : .8)));
  grad.addColorStop(.5, css(c));
  grad.addColorStop(1, css(shade(c, side > 0 ? .8 : 1.12)));
  g.fillStyle = grad; g.fill();
  g.shadowColor = "transparent";
  if (opt.gloss && !under) {   // a leathery leaf's shine: a soft highlight along one half
    const hl = g.createLinearGradient(-w, 0, w, 0);
    hl.addColorStop(0, "rgba(255,255,240,0)"); hl.addColorStop(side > 0 ? .3 : .7, `rgba(255,255,240,${opt.gloss})`); hl.addColorStop(1, "rgba(255,255,240,0)");
    leafPath(g, kind, len, w, r); g.fillStyle = hl; g.fill();
  }
  if (kind === "fan") {   // (a fan's veins: forking out from its foot, no midrib)
    g.strokeStyle = css(mix3(c, [225, 235, 190], .25), .45); g.lineWidth = .6;
    for (let i = 0; i <= 14; i++) { const th = -1 + 2 * i / 14; g.beginPath(); g.moveTo(0, len * .4); g.lineTo(Math.sin(th) * w * .95, len * .4 + Math.cos(th) * len * .55); g.stroke(); }
    g.restore(); return;
  }
  // the midrib and, on a big leaf, its veins
  g.strokeStyle = css(mix3(c, [225, 235, 190], .35), .8); g.lineWidth = Math.max(.6, len * .025);
  g.beginPath(); g.moveTo(0, 0); g.lineTo(0, len * .92); g.stroke();
  if (len > 30 && kind !== "maple" && kind !== "sword") {
    g.lineWidth = .6; g.strokeStyle = css(mix3(c, [225, 235, 190], .2), .5);
    for (let i = 1; i < 6; i++) { const t = i / 6; for (const sd of [1, -1]) { g.beginPath(); g.moveTo(0, t * len * .85); g.lineTo(sd * w * .7, t * len * .85 + len * .12); g.stroke(); } }
  }
  if (kind === "maple") {
    g.lineWidth = .7; g.strokeStyle = css(mix3(c, [225, 235, 190], .25), .6);
    for (const aa of [-1.35, -.67, .67, 1.35]) { g.beginPath(); g.moveTo(0, 0); g.lineTo(Math.sin(aa) * len * .8, Math.cos(aa) * len * .8); g.stroke(); }
  }
  g.restore();
}

// a stem from p0 to p1, bending through a control point; width w0 to w1
function stem(g, p0, c, p1, w0, w1, col) {
  const n = 8;
  g.strokeStyle = css(col); g.lineCap = "round";
  for (let i = 0; i < n; i++) {
    const q = (t) => [(1 - t) * (1 - t) * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0], (1 - t) * (1 - t) * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]];
    const a = q(i / n), b = q((i + 1) / n);
    g.lineWidth = w0 + (w1 - w0) * (i + .5) / n;
    g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke();
  }
}
const qpt = (p0, c, p1, t) => [(1 - t) * (1 - t) * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0], (1 - t) * (1 - t) * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]];
const qdir = (p0, c, p1, t) => { const dx = 2 * (1 - t) * (c[0] - p0[0]) + 2 * t * (p1[0] - c[0]), dy = 2 * (1 - t) * (c[1] - p0[1]) + 2 * t * (p1[1] - c[1]); return Math.atan2(dx, -dy); };

// a five-petalled flower (blossom, the ceiba's) at (x, y), radius R, facing the viewer at a slant
function flower(g, r, x, y, R, col, eye, opt = {}) {
  g.save(); g.translate(x, y); g.rotate(r() * TAU);
  const sq = .55 + .45 * r();   // (foreshortened: seen at a slant)
  g.scale(1, sq);
  g.shadowColor = "rgba(30,20,20,0.35)"; g.shadowBlur = 3;
  const n = opt.petals ?? 5;
  for (let i = 0; i < n; i++) {
    g.save(); g.rotate(i / n * TAU + .2 * (r() - .5));
    g.beginPath();
    const L = R * (opt.long ?? 1), Wd = R * (opt.wide ?? .55);
    g.moveTo(0, 0); g.bezierCurveTo(Wd, L * .3, Wd * .9, L, 0, L); g.bezierCurveTo(-Wd * .9, L, -Wd, L * .3, 0, 0);
    const gr = g.createLinearGradient(0, 0, 0, L);
    gr.addColorStop(0, css(opt.heart ?? shade(col, .9))); gr.addColorStop(.45, css(col)); gr.addColorStop(1, css(shade(col, 1.05)));
    g.fillStyle = gr; g.fill();
    g.restore();
  }
  g.shadowColor = "transparent";
  g.fillStyle = css(eye); g.beginPath(); g.arc(0, 0, R * .22, 0, TAU); g.fill();
  g.fillStyle = css([230, 200, 90]);
  for (let i = 0; i < 6; i++) { const a = r() * TAU; g.beginPath(); g.arc(Math.cos(a) * R * .2, Math.sin(a) * R * .2, R * .07, 0, TAU); g.fill(); }
  g.restore();
}
// a FRUIT, R its half-width: a ball lit from the upper left, its shadow side a DEEPER TONE OF ITS OWN COLOUR (a rim
// shaded toward black reads as brown on an orange). o, its look (FRUIT_LOOK, by the spray style):
//   long   its height to its width (an olive 1.3, a date 1.5)        tilt   turned by (radians)
//   gloss  0..1, a sharp sheen (a cherry's)                           bloom  0..1, a plum's or a grape's dusty haze
//   peel   a citrus's pitted rind                                     speck  an apple's pale lenticels
//   blush  a second colour streaked over its sunny side (an apple's red on its green), blushK how much of it
//   stalk  its stalk's length (R's), dimple: sunk in a hollow          calyx  a green star where the stalk sits
function fruit(g, x, y, R, col, o = {}) {
  const deep = [col[0] * .72, col[1] * .58, col[2] * .6], lit = mix3(col, [255, 250, 235], .4), H = R * (o.long ?? 1);
  g.save(); g.translate(x, y); g.rotate(o.tilt ?? 0);
  g.save(); g.scale(1, o.long ?? 1);
  g.shadowColor = "rgba(20,10,10,0.35)"; g.shadowBlur = 4;
  const gr = g.createRadialGradient(-R * .35, -R * .4, R * .08, 0, 0, R);
  gr.addColorStop(0, css(lit)); gr.addColorStop(.4, css(col)); gr.addColorStop(1, css(deep));
  g.fillStyle = gr; g.beginPath(); g.arc(0, 0, R, 0, TAU); g.fill();
  g.shadowColor = "transparent"; g.clip();
  // (the details' scatter: a hash of where the fruit is, so a fruit is the same at every bake without a stream threaded in)
  let h = (Math.floor(x * 7.3) * 73856093 ^ Math.floor(y * 5.1) * 19349663) >>> 0;
  const rnd = () => ((h = (h * 1664525 + 1013904223) >>> 0) / 4294967296);
  const dots = (n, rad, c, alpha) => { g.fillStyle = css(c, alpha); for (let i = 0; i < n; i++) { const a = rnd() * TAU, d = Math.sqrt(rnd()) * R; g.beginPath(); g.arc(Math.cos(a) * d, Math.sin(a) * d, rad, 0, TAU); g.fill(); } };
  if (o.blush) {
    const k = o.blushK ?? .8, bg = g.createRadialGradient(R * .3, -R * .2, 0, R * .3, -R * .2, R * 1.3);
    bg.addColorStop(0, css(o.blush, k)); bg.addColorStop(.7, css(o.blush, k * .6)); bg.addColorStop(1, css(o.blush, 0));
    g.fillStyle = bg; g.fillRect(-R, -R, 2 * R, 2 * R);
    g.strokeStyle = css(shade(o.blush, .85), k * .28); g.lineWidth = Math.max(.7, R * .05);
    for (let i = 0; i < 12; i++) { const u = (rnd() - .3) * 1.6 * R; g.beginPath(); g.moveTo(u * .3, -R); g.quadraticCurveTo(u * 1.1, 0, u * .5, R); g.stroke(); }
    const rim = g.createRadialGradient(0, 0, R * .55, 0, 0, R);   // (its shading again, over the blush)
    rim.addColorStop(0, "rgba(40,10,0,0)"); rim.addColorStop(1, "rgba(40,10,0,0.35)");
    g.fillStyle = rim; g.fillRect(-R, -R, 2 * R, 2 * R);
  }
  if (o.peel) { const d = Math.max(.6, R * .06); dots(Math.round(R * 6), d, lit, .35); dots(Math.round(R * 5), d, deep, .3); }
  if (o.speck) dots(Math.round(R * .8), Math.max(.5, R * .035), [236, 226, 170], .4);
  if (o.bloom) { g.fillStyle = css([206, 210, 228], o.bloom * .55); g.fillRect(-R, -R, 2 * R, 2 * R); }
  if (o.gloss) {
    const sg = g.createRadialGradient(-R * .38, -R * .45, 0, -R * .38, -R * .45, R * .32);
    sg.addColorStop(0, css([255, 255, 255], o.gloss * .9)); sg.addColorStop(.5, css([255, 255, 255], o.gloss * .35)); sg.addColorStop(1, css([255, 255, 255], 0));
    g.fillStyle = sg; g.beginPath(); g.ellipse(-R * .38, -R * .45, R * .32, R * .2, -.6, 0, TAU); g.fill();
  }
  g.restore();
  if (o.dimple) { g.fillStyle = css(shade(o.blush ?? col, .55), .55); g.beginPath(); g.ellipse(0, -H * .84, R * .24, R * .08, 0, 0, TAU); g.fill(); }
  if (o.stalk) {
    g.strokeStyle = css([96, 78, 44]); g.lineWidth = Math.max(1, R * .09); g.lineCap = "round";
    g.beginPath(); g.moveTo(0, -H * .82); g.quadraticCurveTo(R * .05, -H - o.stalk * R * .5, R * .18, -H - o.stalk * R); g.stroke();
  }
  if (o.calyx) {
    g.fillStyle = css([112, 128, 52]); g.beginPath();
    for (let i = 0; i <= 10; i++) { const a = i / 10 * TAU, rr = (i % 2 ? .08 : .2) * R; g.lineTo(Math.cos(a) * rr, -H * .82 + Math.sin(a) * rr * .45); }
    g.fill();
  }
  g.restore();
}
// how each spray style's fruit looks (fruit()'s o) -- where the species has nothing of its own, a berry's sheen
const FRUIT_LOOK = {
  citrus: { peel: 1, calyx: 1, stalk: .22, gloss: .22 },
  apple: { blush: 1, speck: 1, stalk: .55, dimple: 1, gloss: .18, long: .92 },   // (blush: its colors.fruit, over a green)
  cherry: { gloss: .75, dimple: 1, long: .95 },
  olive: { gloss: .45, long: 1.3, stalk: .15 },
  grape: { bloom: .4, gloss: .12, long: 1.08 },
  frond: { gloss: .4, long: 1.45 },
  shrub: { gloss: .55 },
};
const APPLE_GREEN = [206, 198, 88];   // (an apple's ground, yellow-green; its red the blush, most of it)

// THE SPRAY RECIPES: each paints one twig into a cell (0, 0)-(CW, CH), its base at the bottom middle.
// k: 0/1 the variant, mode: "leaf" | "flower" | "fruit"
const L = (S) => S.colors.leaf.map(rgbOf);
const WOODC = (S) => mix3(rgbOf(S.colors.bark), [70, 60, 45], .4);
function broadSpray(g, r, S, mode, P) {
  const [l0, l1] = L(S), wood = WOODC(S);
  const base = [CW / 2 + (r() - .5) * 20, CH], tip = [CW / 2 + (r() - .5) * 60, CH * (.08 + .06 * r())], ctl = [CW / 2 + (r() - .5) * 90, CH * .5];
  const items = [];   // (painted back to front: the leaves and the side shoots in one list by depth)
  // the side shoots along the main stem, alternating (or opposite), each with leaves at its nodes
  const nodes = P.nodes;
  for (let i = 0; i < nodes; i++) {
    const t = P.from + (1 - P.from) * (i + .5 + .3 * (r() - .5)) / nodes;
    const p = qpt(base, ctl, tip, t), d = qdir(base, ctl, tip, t);
    const sides = P.opposite ? [1, -1] : [i % 2 ? 1 : -1];
    for (const sd of sides) {
      const a = d + sd * (P.angle + 15 * (r() - .5)) * Math.PI / 180;
      const len = P.shoot * (1 - .55 * t) * (.75 + .5 * r());
      const end = [p[0] + Math.sin(a) * len, p[1] - Math.cos(a) * len];
      items.push({ z: r(), draw: () => {
        if (len > 8) stem(g, p, [(p[0] + end[0]) / 2 + sd * 6, (p[1] + end[1]) / 2 - 4], end, P.w * .55, P.w * .35, wood);
        P.leafAt(g, r, end, a, mode, l0, l1, t);
        if (P.leavesAlong) for (let j = 1; j <= P.leavesAlong; j++) { const u = j / (P.leavesAlong + 1); P.leafAt(g, r, [p[0] + (end[0] - p[0]) * u, p[1] + (end[1] - p[1]) * u], a + (j % 2 ? 1 : -1) * .9, mode, l0, l1, t * .8, .7); }
      } });
    }
  }
  stem(g, base, ctl, tip, P.w, P.w * .45, wood);
  items.sort((a, b) => a.z - b.z).forEach((it) => it.draw());
  P.leafAt(g, r, tip, qdir(base, ctl, tip, 1), mode, l0, l1, 1, 1.1);   // the leading bud's leaves
}
const leafCluster = (kind, n, len, w, spread, extra = {}) => (g, r, p, a, mode, l0, l1, t, k = 1) => {
  for (let i = 0; i < n; i++) {
    const aa = a + (i - (n - 1) / 2) / Math.max(1, n - 1) * spread + .25 * (r() - .5);
    const L = len * k * (.75 + .4 * r());
    leaf(g, r, p[0], p[1], aa, L, w * k * (.85 + .3 * r()), kind, mix3(l0, l1, r()), extra);
  }
};
// blossom clusters and fruit, laid over a painted spray
function bloomOver(g, r, S, mode, n, R) {
  const bl = rgbOf(S.colors.blossom ?? 0xffc0d8), fr = rgbOf(S.colors.fruit ?? 0xc03030);
  for (let i = 0; i < n; i++) {
    const x = CW * (.18 + .64 * r()), y = CH * (.08 + .7 * r());
    if (mode === "flower") {
      const m = 2 + Math.floor(r() * 4);
      for (let j = 0; j < m; j++) flower(g, r, x + (r() - .5) * R * 2.4, y + (r() - .5) * R * 2.4, R * (.8 + .4 * r()), shade(bl, .92 + .1 * r()), [210, 190, 120], S.flowerOpt);
    } else {
      const m = S.twig.style === "cherry" ? 2 : 1 + Math.floor(r() * 2);
      for (let j = 0; j < m; j++) {
        const fx = x + (j - (m - 1) / 2) * R * 1.6, fy = y + R * 2.2;
        if (S.twig.style !== "apple") { g.strokeStyle = css([90, 80, 40]); g.lineWidth = 1.2; g.beginPath(); g.moveTo(x, y); g.lineTo(fx, fy - R); g.stroke(); }
        const look = FRUIT_LOOK[S.twig.style] ?? FRUIT_LOOK.shrub;
        if (look.blush) fruit(g, fx, fy, R * (.9 + .2 * r()), shade(APPLE_GREEN, .95 + .1 * r()), { ...look, blush: shade(fr, .9 + .2 * r()), blushK: .7 + .3 * r() });
        else fruit(g, fx, fy, R * (.9 + .2 * r()), shade(fr, .9 + .2 * r()), look);
      }
    }
  }
}

// a BIPINNATE leaf (a jacaranda's, an acacia's): a stalk with pinnae off both sides, each a row of tiny leaflets -- a
// fern's lace; `thorns`: a pair of white spines where it leaves the shoot
function pinnate(g, r, p, a, len, pinnae, leaflet, col, opt = {}) {
  const tip = [p[0] + Math.sin(a) * len, p[1] - Math.cos(a) * len];
  g.strokeStyle = css(shade(col, .7)); g.lineWidth = 1.2;
  g.beginPath(); g.moveTo(p[0], p[1]); g.lineTo(tip[0], tip[1]); g.stroke();
  if (opt.thorns) {
    g.strokeStyle = css([232, 228, 214]); g.lineWidth = 1.6;
    for (const sd of [1, -1]) { const ta = a + sd * 1.1, tl = opt.thorns * (.8 + .4 * r()); g.beginPath(); g.moveTo(p[0], p[1]); g.lineTo(p[0] + Math.sin(ta) * tl, p[1] - Math.cos(ta) * tl); g.stroke(); }
  }
  for (let i = 0; i < pinnae; i++) {
    const t = .12 + .85 * i / pinnae, q = [p[0] + (tip[0] - p[0]) * t, p[1] + (tip[1] - p[1]) * t];
    for (const sd of [1, -1]) {
      const pa = a + sd * (1.0 - .3 * t), pl = len * .32 * (1 - .5 * t) * (.85 + .3 * r()), n = Math.max(3, Math.round(pl / (leaflet * .6)));
      const e = [q[0] + Math.sin(pa) * pl, q[1] - Math.cos(pa) * pl];
      g.strokeStyle = css(shade(col, .75)); g.lineWidth = .7; g.beginPath(); g.moveTo(q[0], q[1]); g.lineTo(e[0], e[1]); g.stroke();
      const c = shade(col, .85 + .3 * r());
      g.fillStyle = css(c);
      for (let j = 0; j < n; j++) {
        const u = (j + .7) / n, x = q[0] + (e[0] - q[0]) * u, y = q[1] + (e[1] - q[1]) * u;
        for (const s2 of [1, -1]) {
          const la = pa + s2 * 1.2;
          g.beginPath(); g.ellipse(x + Math.sin(la) * leaflet * .5, y - Math.cos(la) * leaflet * .5, leaflet * .5, leaflet * .2, la + Math.PI / 2, 0, TAU); g.fill();
        }
      }
    }
  }
}
// a ROPE (an araucaria's shoot) from p0 to p1 through c, w across: stiff triangular leaves overlapping all round it,
// pointing toward its tip, darker toward its sides (it is round)
function rope(g, r, p0, c, p1, w, l0, l1) {
  const n = 70;
  for (let i = 0; i <= n; i++) {
    const t = i / n, p = qpt(p0, c, p1, t), d = qdir(p0, c, p1, t), ww = w * (1 - .45 * t);
    for (let k = 0; k < 5; k++) {
      const off = (k / 4 - .5 + (i % 2) * .1) * ww * .9, side = Math.abs(off) / (ww * .5);
      const x = p[0] + Math.cos(d) * off, y = p[1] + Math.sin(d) * off, L2 = 13 * (1 - .3 * t);
      g.fillStyle = css(shade(mix3(l0, l1, r()), 1.15 - .5 * side * side + .1 * r()));
      g.beginPath(); g.moveTo(x - Math.cos(d) * 5, y - Math.sin(d) * 5); g.lineTo(x + Math.sin(d) * L2 + Math.cos(d) * off * .15, y - Math.cos(d) * L2); g.lineTo(x + Math.cos(d) * 5, y + Math.sin(d) * 5); g.fill();
    }
  }
}
// a CYME (a linden's): a long pale bract, and hanging from its middle a few small flowers (or round nutlets)
function cyme(g, r, x, y, col, flowers) {
  const a = (r() - .5) * 1.2;
  g.save(); g.translate(x, y); g.rotate(a);
  g.fillStyle = css([196, 210, 150]); g.beginPath(); g.ellipse(0, -24, 7, 28, 0, 0, TAU); g.fill();
  g.strokeStyle = css([150, 150, 90]); g.lineWidth = 1; g.beginPath(); g.moveTo(0, -10); g.lineTo(-a * 20, 26); g.stroke();
  for (let i = 0; i < (flowers ? 7 : 4); i++) {
    const fx = -a * 20 + (r() - .5) * 26, fy = 26 + r() * 18;
    if (flowers) { g.fillStyle = css(shade(col, .9 + .2 * r())); for (let k = 0; k < 5; k++) { const b = k / 5 * TAU; g.beginPath(); g.ellipse(fx + Math.cos(b) * 3, fy + Math.sin(b) * 3, 3, 2, b, 0, TAU); g.fill(); } }
    else fruit(g, fx, fy, 5, col, { bloom: .5 });
  }
  g.restore();
}
// a TULIP CUP (a tulip tree's flower, a prickly pear's): six upright petals, R high, an orange band low in it
function tulipCup(g, r, x, y, R, col) {
  g.save(); g.shadowColor = "rgba(30,30,10,0.35)"; g.shadowBlur = 3;
  for (const [dx, k, w] of [[-.35, .85, .4], [.35, .85, .4], [0, .9, .45], [-.2, 1, .42], [.2, 1, .42]]) {
    g.fillStyle = css(shade(col, k)); g.beginPath(); g.ellipse(x + dx * R, y - R * .5, R * w, R * .6, dx * .6, 0, TAU); g.fill();
  }
  g.shadowColor = "transparent";
  g.fillStyle = css([230, 130, 40], .7); g.beginPath(); g.ellipse(x, y - R * .15, R * .55, R * .18, 0, 0, TAU); g.fill();
  g.restore();
}
// a BUNCH of grapes hanging from (x, y): a shoulder, then rows narrowing (unevenly) to its tip, berries missing here
// and there; the ones behind first and darker
function bunch(g, r, x, y, col) {
  hung(g, x, y - 16, 16);
  const rows = 10 + Math.floor(r() * 4), lean = (r() - .5) * 8, shoulder = r() < .5 ? -1 : 1;
  const berries = [];
  for (let row = 0; row < rows; row++) {
    const t = row / rows, w = 36 * Math.pow(1 - t, .8) * (.85 + .3 * r()) + 6, n = Math.max(1, Math.round(w / 9.5)), yy = y + row * 9.5;
    for (let i = 0; i < n; i++) if (r() > .12 || row === 0)
      berries.push({ x: x + lean * t + (i - (n - 1) / 2) * 10 + (r() - .5) * 3.5, y: yy + (r() - .5) * 3, z: r() });
    if (row === 1) for (let i = 0; i < 3; i++) berries.push({ x: x + shoulder * (24 + i * 9), y: yy - 2 + i * 7, z: r() });   // (its shoulder)
  }
  berries.sort((a, b) => a.z - b.z).forEach((b) => fruit(g, b.x, b.y, 6.4, shade(col, .7 + .45 * b.z), FRUIT_LOOK.grape));
}
// a hazelNUT in its ragged husk
function nut(g, r, x, y, col) {
  fruit(g, x, y + 4, 9, col, { gloss: .35, long: 1.1 });
  g.fillStyle = css([120, 150, 70]); g.beginPath();
  for (let i = 0; i <= 14; i++) { const a = Math.PI * (.05 + .9 * i / 14), R = i % 2 ? 9 : 14; g.lineTo(x + Math.cos(a) * R * 1.1, y + 6 + Math.sin(a) * R * 1.2); }
  g.closePath(); g.fill();
}
// a MOPHEAD (a hydrangea's): a ball of small four-petalled florets, R across, lit from above left, its tint
// wandering a little toward pink on some heads
function mophead(g, r, x, y, R, col) {
  const c0 = mix3(col, [214, 140, 190], r() * .45);
  g.save(); g.shadowColor = "rgba(20,20,40,0.35)"; g.shadowBlur = 4;
  g.fillStyle = css(shade(c0, .6)); g.beginPath(); g.arc(x, y, R * .92, 0, TAU); g.fill();
  g.shadowColor = "transparent";
  const fl = Array.from({ length: 90 }, () => { const a = r() * TAU, d = Math.sqrt(r()) * R * .9; return [x + Math.cos(a) * d, y + Math.sin(a) * d * .92]; })
    .sort((p, q) => p[1] - q[1]);
  for (const [fx, fy] of fl) {
    const lit = clamp(1.12 - ((fx - x) + (fy - y)) / R * .3 - Math.hypot(fx - x, fy - y) / R * .25, .6, 1.25), c = shade(c0, lit * (.9 + .15 * r())), s = 4.5 + 2.5 * r(), rot = r() * TAU;
    g.fillStyle = css(c);
    for (let k = 0; k < 4; k++) { const a = rot + k / 4 * TAU; g.beginPath(); g.ellipse(fx + Math.cos(a) * s * .6, fy + Math.sin(a) * s * .6, s * .62, s * .42, a, 0, TAU); g.fill(); }
    g.fillStyle = css(mix3(c, [250, 250, 240], .4)); g.beginPath(); g.arc(fx, fy, s * .18, 0, TAU); g.fill();
  }
  g.restore();
}
// a TRUSS (a rhododendron's): a dome of a dozen and more funnel flowers, R across, freckled in their throats
function truss(g, r, x, y, R, col) {
  const fl = Array.from({ length: 15 }, () => { const a = r() * TAU, d = Math.sqrt(r()) * R; return [x + Math.cos(a) * d, y + Math.sin(a) * d * .7]; })
    .sort((p, q) => p[1] - q[1]);
  for (const [fx, fy] of fl) flower(g, r, fx, fy, R * .36 * (.85 + .3 * r()), shade(col, .88 + .2 * r()), shade(col, .55), { wide: .85, heart: shade(mix3(col, [240, 230, 200], .4), 1) });
  g.fillStyle = css([110, 40, 60], .7);
  for (const [fx, fy] of fl) for (let k = 0; k < 3; k++) { g.beginPath(); g.arc(fx + (r() - .5) * 6, fy - 3 - r() * 4, 1.1, 0, TAU); g.fill(); }
}
// a CANDLE: an upright cone of small flowers (a horse chestnut's panicle), its foot at (x, y), h tall
function candle(g, r, x, y, h, w, col, spot) {
  g.save(); g.shadowColor = "rgba(30,25,20,0.35)"; g.shadowBlur = 3;
  for (let i = 0; i < 70; i++) {
    const t = Math.pow(r(), .8), ww = w * (1 - t) * (.6 + .4 * Math.sqrt(1 - t)), fx = x + (r() - .5) * 2 * ww, fy = y - t * h;
    const R = 3.2 + 2.2 * r();
    g.fillStyle = css(shade(col, .86 + .2 * r()));
    for (let k = 0; k < 4; k++) { const a = k / 4 * TAU + r(); g.beginPath(); g.ellipse(fx + Math.cos(a) * R * .55, fy + Math.sin(a) * R * .55, R * .6, R * .38, a, 0, TAU); g.fill(); }
    if (r() < .5) { g.fillStyle = css(spot); g.beginPath(); g.arc(fx, fy, R * .28, 0, TAU); g.fill(); }
  }
  g.restore();
}
// a ROSETTE of sword leaves radiating from a point a share `mid` up the cell (grow.js rosette sits it on a shoot's tip):
// the young ones standing up, the old ones out and down, the dead ones (`dead`: share) hanging, dry, under them
function rosettePaint(g, r, S, mode) {
  const [l0, l1] = L(S), W = S.twig, cx = CW / 2, cy = CH * (1 - (W.mid ?? .38)), n = W.blades ?? 60;
  const blades = [];
  for (let i = 0; i < n; i++) {
    const dead = r() < (W.dead ?? 0);
    const a = dead ? (Math.PI * (.62 + .3 * r())) * (r() < .5 ? 1 : -1) : (r() - .5) * 2 * Math.PI * (W.reach ?? .55) * Math.sqrt(r() * .6 + .4);
    blades.push({ a, dead, z: dead ? -1 : Math.cos(a) + .3 * r() });
  }
  const len = W.blade ?? [150, 220], wd = W.width ?? 7;
  g.save(); g.lineJoin = "round";
  for (const b of blades.sort((p, q) => p.z - q.z)) {
    const L2 = (b.dead ? .6 : 1) * lerp(len[0], len[1], r()) * (1 - .25 * Math.abs(Math.sin(b.a)) * (b.dead ? 0 : 1));
    const c = b.dead ? mix3([140, 120, 90], [95, 85, 70], r()) : mix3(l0, l1, r());
    leaf(g, r, cx, cy, b.a, L2, wd * (.8 + .4 * r()), "sword", c, { under: 0, blur: 3, gloss: W.gloss });
  }
  if (mode === "flower" && W.bloom) {   // (a Joshua tree's: a cluster of cream bells on the rosette's top)
    for (let i = 0; i < 26; i++) fruit(g, cx + (r() - .5) * 46, cy - 40 - r() * 60, 7 + 3 * r(), shade(rgbOf(S.colors.blossom ?? 0xeae6c8), .9 + .15 * r()));
  }
  g.restore();
}
const lerp = (a, b, t) => a + (b - a) * t;
// a spray's flowers or fruit laid over it: `n` clusters, flowers of radius R (petals, opt as flower()) or fruit
function clusters(g, r, n, area, draw) {
  for (let i = 0; i < n; i++) draw(CW * (area[0] + (area[1] - area[0]) * r()), CH * (area[2] + (area[3] - area[2]) * r()));
}

// a HIBISCUS flower, face on at a slant: five broad petals overlapping, veined from the deep-red eye, the column of
// stamens standing out with its pollen and its five red stigma knobs
function hibiscusFlower(g, r, x, y, R, col) {
  g.save(); g.translate(x, y); g.rotate(r() * TAU); const sq = .7 + .3 * r(); g.scale(1, sq);
  g.shadowColor = "rgba(40,10,10,0.35)"; g.shadowBlur = 4;
  for (let i = 0; i < 5; i++) {
    g.save(); g.rotate(i / 5 * TAU + .15 * (r() - .5));
    g.beginPath(); g.moveTo(0, 0); g.bezierCurveTo(R * .75, R * .2, R * .95, R * .95, R * .2, R * 1.02); g.quadraticCurveTo(0, R * .9, -R * .25, R); g.bezierCurveTo(-R * .9, R * .9, -R * .6, R * .2, 0, 0);
    const gr = g.createRadialGradient(0, 0, 0, 0, 0, R);
    gr.addColorStop(0, css(shade(col, .38))); gr.addColorStop(.28, css(shade(col, .7))); gr.addColorStop(.45, css(col)); gr.addColorStop(1, css(shade(col, 1.08)));
    g.fillStyle = gr; g.fill();
    g.strokeStyle = css(shade(col, .65), .35); g.lineWidth = .7;
    for (let k = 0; k < 6; k++) { const a = (k / 5 - .5) * .9; g.beginPath(); g.moveTo(0, R * .1); g.quadraticCurveTo(Math.sin(a) * R * .4, R * .5, Math.sin(a) * R * .75, R * .9); g.stroke(); }
    g.restore();
  }
  g.shadowColor = "transparent"; g.restore();
  // (the column: out of the eye, upward on the card, its tip a fork of red knobs)
  const a = -Math.PI / 2 + (r() - .5) * 1.2, L = R * 1.25, tx = x + Math.cos(a) * L, ty = y + Math.sin(a) * L * .8;
  g.strokeStyle = css(shade(col, .9)); g.lineWidth = 2.6; g.lineCap = "round"; g.beginPath(); g.moveTo(x, y); g.lineTo(tx, ty); g.stroke();
  g.fillStyle = css([240, 200, 70]); for (let k = 0; k < 14; k++) { const u = .45 + .45 * r(); g.beginPath(); g.arc(x + (tx - x) * u + (r() - .5) * 6, y + (ty - y) * u + (r() - .5) * 6, 1.4, 0, TAU); g.fill(); }
  g.fillStyle = css([190, 20, 40]); for (let k = 0; k < 5; k++) { const b = a + (k - 2) * .45; g.beginPath(); g.arc(tx + Math.cos(b) * 4, ty + Math.sin(b) * 4, 2, 0, TAU); g.fill(); }
}
// a FAN PALM's leaf in its cell: (u, t) on the frond's ribbon (mesh.js frondMeshes: the stalk to t = fan, then the
// blade, FAN_W(s) its half-width s along it) -- a point of the blade in its own measure (along: s, across: x of the
// widest half-width) drawn where the ribbon puts it, so the segments radiate on the tree as they do here
function fanLeaf(g, r, S, dead) {
  const [l0, l1] = L(S), fan = S.crown?.fan ?? .45, X = (s, x) => CW / 2 + CW * .5 * x / FAN_W(s), Y = (s) => CH * (1 - (fan + .03 + (1 - fan - .03) * s));
  const green = (k) => dead ? shade(mix3([168, 140, 92], [130, 104, 66], r()), k) : shade(mix3(l0, l1, r()), k);
  // the stalk: its own colour, hooked teeth along its edges (orange on a live leaf)
  const sc = dead ? [120, 96, 64] : mix3(l0, [200, 180, 110], .35);
  g.fillStyle = css(sc); g.fillRect(CW * .3, Y(0) - 4, CW * .4, CH - Y(0) + 4);
  g.fillStyle = css(shade(sc, 1.2), .6); g.fillRect(CW * .45, Y(0), CW * .1, CH - Y(0));
  g.fillStyle = css(dead ? [90, 70, 46] : [196, 130, 50]);
  for (let y = CH - 6; y > Y(0) + 6; y -= 11) for (const sd of [-1, 1]) { const x = CW / 2 + sd * CW * .2; g.beginPath(); g.moveTo(x, y); g.lineTo(x + sd * 9, y - 6); g.lineTo(x, y - 5); g.fill(); }
  // the blade: segments from the hastula (s 0, x 0), out to the rim; each a pleat lit on one face, dark on the other
  const nSeg = 34, H = (1 - fan) * 1;   // (its length in the frond's units: the angle's measure; the widest half-width is about H * .55)
  const rim = (th) => { const c = Math.cos(th), sn = Math.sin(th); let best = 0;   // (how far a ray at th runs before it leaves the outline)
    for (let q = 1; q <= 60; q++) { const d = q / 60 * 1.1, s = d * c, x = d * sn / .55; if (s < 0 || s > 1 || Math.abs(x) > FAN_W(s)) break; best = d; } return best; };
  for (let i = 0; i < nSeg; i++) {
    const th0 = -1.45 + 2.9 * i / nSeg, th1 = -1.45 + 2.9 * (i + 1) / nSeg, tm = (th0 + th1) / 2, R = rim(tm), split = dead ? .9 : .62 + .1 * r();
    const P = (th, d) => [X(Math.max(0, d * Math.cos(th)), d * Math.sin(th) / .55), Y(Math.max(0, d * Math.cos(th)))];
    const face = (a0, a1, k) => { g.fillStyle = css(green(k)); g.beginPath(); g.moveTo(...P(tm, 0));
      for (let q = 1; q <= 10; q++) g.lineTo(...P(a0, R * split * q / 10));
      const tip = P(tm + (r() - .5) * .04, R * (dead ? .96 : 1.02));   // (past the split, one strip narrowing to its tip)
      g.lineTo(...tip);
      for (let q = 10; q >= 1; q--) g.lineTo(...P(a1, R * split * q / 10));
      g.closePath(); g.fill(); };
    face(th0 + .005, tm, dead ? .85 + .2 * r() : 1.12);   // (the lit face of the pleat)
    face(tm, th1 - .005, dead ? .7 + .2 * r() : .78);      // (its shaded face)
    if (!dead && r() < .75) {   // (a thread or two hanging from the split: a Washingtonia's)
      g.strokeStyle = css([226, 220, 196], .8); g.lineWidth = 1; const t0 = P(tm, R * .9);
      g.beginPath(); g.moveTo(...t0); g.quadraticCurveTo(t0[0] + (r() - .5) * 16, t0[1] + 4, t0[0] + (r() - .5) * 24, t0[1] - 10 - 12 * r()); g.stroke();
    }
  }
  g.fillStyle = css(dead ? [110, 86, 56] : shade(l0, .8)); g.beginPath(); g.ellipse(CW / 2, Y(0), CW * .1, 6, 0, 0, TAU); g.fill();   // (the hastula)
}

const SPRAYS = {
  oak: (g, r, S, mode) => broadSpray(g, r, S, mode, { nodes: 8, from: .08, angle: 48, shoot: 105, w: 4.5, leavesAlong: 1,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("oak", 5, 42, 13, 2.4)(g2, r2, p, a, m, l0, l1, t, k) }),
  maple: (g, r, S, mode) => broadSpray(g, r, S, mode, { nodes: 5, from: .1, angle: 52, shoot: 95, w: 4, opposite: true, leavesAlong: 1,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("maple", 3, 48, 13, 1.9, { under: .12 })(g2, r2, p, a, m, l0, l1, t, k) }),
  birch: (g, r, S, mode) => broadSpray(g, r, S, mode, { nodes: 10, from: .06, angle: 38, shoot: 85, w: 2.5, leavesAlong: 3,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("triangle", 3, 26, 10, 1.4)(g2, r2, p, a, m, l0, l1, t, k) }),
  apple: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 8, from: .08, angle: 48, shoot: 85, w: 4, leavesAlong: 1,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("oval", 5, 38, 12, 2.2, { under: .3 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode !== "leaf") bloomOver(g, r, S, mode, mode === "flower" ? 9 : 6, mode === "flower" ? 12 : 13); },
  cherry: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 8, from: .08, angle: 44, shoot: 85, w: 4, leavesAlong: 1,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("lance", 5, 42, 11, 2.0, { under: .2 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode !== "leaf") bloomOver(g, r, S, mode, mode === "flower" ? 10 : 7, mode === "flower" ? 11 : 8); },
  shrub: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 10, from: .05, angle: 52, shoot: 80, w: 3, leavesAlong: 2,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("oval", 4, 28, 10, 2.0, { under: .25 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode !== "leaf") bloomOver(g, r, S, mode, 11, 8); },
  // the ceiba: hand-shaped compound leaves, 5-7 leaflets fanned from a long stalk; in flower, big pink flowers
  ceiba: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 7, from: .08, angle: 48, shoot: 95, w: 4,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => {
      const n = 5 + Math.floor(r2() * 3), c = mix3(l0, l1, r2());
      for (let i = 0; i < n; i++) leaf(g2, r2, p[0], p[1], a + (i - (n - 1) / 2) * .42, 40 * k * (1 - Math.abs(i - (n - 1) / 2) * .12), 9 * k, "lance", c);
    } });
    if (mode === "flower") bloomOver(g, r, { ...S, colors: { ...S.colors, blossom: 0xe86aa6 }, flowerOpt: { long: 1.3, wide: .5, heart: [250, 240, 215] } }, "flower", 5, 20); },
  // YEW: flat sprays of short dark needles in two ranks along every shoot; in fruit, red cups (arils), each round a seed
  yew: (g, r, S, mode) => {
    const [l0, l1] = L(S), wood = WOODC(S);
    const needles = (p0, c, p1, n, len) => {
      for (let i = 0; i < n; i++) {
        const t = .04 + .94 * i / n, p = qpt(p0, c, p1, t), d = qdir(p0, c, p1, t);
        for (const sd of [1, -1]) leaf(g, r, p[0], p[1], d + sd * (1.3 + .25 * r()), len * (.8 + .35 * r()) * (1 - .3 * t), 4.6, "lance", mix3(l0, l1, r()), { under: .15, underC: [150, 170, 110], blur: 2 });
      }
    };
    const base = [CW / 2, CH], tip = [CW / 2 + (r() - .5) * 40, CH * .05], ctl = [CW / 2 + (r() - .5) * 50, CH * .5];
    stem(g, base, ctl, tip, 3.5, 2, wood);
    for (let i = 0; i < 13; i++) {
      const t = .08 + .86 * i / 13, p = qpt(base, ctl, tip, t), d = qdir(base, ctl, tip, t), sd = i % 2 ? 1 : -1;
      const a = d + sd * (.6 + .25 * r()), len = CW * .44 * (1 - .5 * t) * (.8 + .3 * r());
      const e = [p[0] + Math.sin(a) * len, p[1] - Math.cos(a) * len], c = [(p[0] + e[0]) / 2, (p[1] + e[1]) / 2 - 6];
      stem(g, p, c, e, 1.8, 1, wood);
      needles(p, c, e, Math.round(len / 4.5), 30);
    }
    needles(base, ctl, tip, 80, 32);
    if (mode === "fruit") clusters(g, r, 9, [.2, .8, .15, .8], (x, y) => { fruit(g, x, y, 7 + 2 * r(), shade(rgbOf(S.colors.fruit), .9 + .2 * r()), { gloss: .7 }); g.fillStyle = css([40, 50, 30]); g.beginPath(); g.arc(x, y - 3, 2.6, 0, TAU); g.fill(); });
  },
  // OLIVE: slender willowy leaves in pairs, dark grey-green above and silver beneath, many turned to show it; in fruit
  // small green-to-black olives
  olive: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 10, from: .05, angle: 62, shoot: 80, w: 3, opposite: true, leavesAlong: 2,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("lance", 5, 46, 6.5, 2.4, { under: .45, underC: [196, 204, 190], underK: .7, blur: 3 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode === "fruit") clusters(g, r, 10, [.18, .82, .12, .8], (x, y) => fruit(g, x, y, 5 + 1.5 * r(), r() < .5 ? [70, 50, 70] : [120, 130, 60], { ...FRUIT_LOOK.olive, tilt: (r() - .5) * 1.4 })); },
  // PLANE: big maple-like leaves, three to five lobed, on long stalks; in fruit the seed balls on long hanging threads
  plane: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 9, from: .06, angle: 50, shoot: 95, w: 4.2, leavesAlong: 2,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("maple", 4, 60, 16, 2.0, { under: .15 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode === "fruit") clusters(g, r, 4, [.25, .75, .3, .6], (x, y) => {
      const m = 1 + Math.floor(r() * 3);
      for (let j = 0; j < m; j++) { const fy = y + 30 + j * 26; g.strokeStyle = css([90, 80, 50]); g.lineWidth = 1; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 2, fy); g.stroke(); fruit(g, x + 2, fy, 10, shade(rgbOf(S.colors.fruit), .9 + .2 * r()), { peel: 1 }); }
    }); },
  // MAGNOLIA (grandiflora): big leathery glossy leaves, rust beneath, crowded at the shoot's end; in flower big white
  // cups of nine petals round a cone
  magnolia: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 4, from: .3, angle: 45, shoot: 40, w: 4.5,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("oval", 3, 84, 24, 2.2, { under: .25, underC: [150, 100, 60], underK: .7, gloss: .35 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode === "flower") clusters(g, r, 2, [.3, .7, .12, .45], (x, y) => flower(g, r, x, y, 40, rgbOf(S.colors.blossom), [205, 190, 140], { petals: 9, long: 1, wide: .62, heart: [236, 230, 210] })); },
  // OLEANDER: long narrow leathery leaves in threes up the shoot; in flower, clusters of pink five-petalled flowers
  oleander: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 5, from: .15, angle: 40, shoot: 30, w: 3.5,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("lance", 3, 76, 8, 2.2, { under: .2, gloss: .2 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode === "flower") clusters(g, r, 4, [.25, .75, .06, .35], (x, y) => { for (let j = 0; j < 6; j++) flower(g, r, x + (r() - .5) * 46, y + (r() - .5) * 40, 13 + 3 * r(), shade(rgbOf(S.colors.blossom), .9 + .15 * r()), shade(rgbOf(S.colors.blossom), .7), { wide: .7 }); }); },
  // HORSE CHESTNUT: hand-shaped leaves of seven big leaflets, widest toward their tips, on long stalks; in spring the
  // upright white candles, spotted yellow and pink
  chestnut: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 5, from: .08, angle: 48, shoot: 70, w: 4.5, opposite: true,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => {
      const n = 7, c = mix3(l0, l1, r2());
      for (let i = 0; i < n; i++) leaf(g2, r2, p[0], p[1], a + (i - 3) * .48, 56 * k * (1 - Math.abs(i - 3) * .13), 16 * k, "obovate", c, { under: .1 });
    } });
    if (mode === "flower") clusters(g, r, 2, [.3, .7, .3, .4], (x, y) => candle(g, r, x, y, 120, 30, rgbOf(S.colors.blossom), [230, 180, 60])); },
  // BAOBAB: sparse hand-shaped leaves of five leaflets; in fruit the velvety grey-green pods on long stalks
  baobab: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 5, from: .15, angle: 50, shoot: 80, w: 4,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => {
      const n = 5, c = mix3(l0, l1, r2());
      for (let i = 0; i < n; i++) leaf(g2, r2, p[0], p[1], a + (i - 2) * .5, 46 * k * (1 - Math.abs(i - 2) * .12), 12 * k, "obovate", c, { under: .15 });
    } });
    if (mode === "fruit") clusters(g, r, 3, [.25, .75, .3, .6], (x, y) => { g.strokeStyle = css([80, 70, 50]); g.lineWidth = 1.5; g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + 50); g.stroke(); g.save(); g.translate(x, y + 76); g.scale(.55, 1); fruit(g, 0, 0, 26, rgbOf(S.colors.fruit), { bloom: .45 }); g.restore(); }); },
  // JACARANDA: feathery fern-like leaves (twice divided into tiny leaflets); in flower, loose clusters of violet trumpets
  jacaranda: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 6, from: .1, angle: 50, shoot: 30, w: 3,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => pinnate(g2, r2, p, a, 120 * k, 9, 6, mix3(l0, l1, r2())) });
    if (mode === "flower") clusters(g, r, 7, [.18, .82, .05, .6], (x, y) => { for (let j = 0; j < 9; j++) flower(g, r, x + (r() - .5) * 40, y + (r() - .5) * 36, 9 + 2 * r(), shade(rgbOf(S.colors.blossom), .88 + .2 * r()), [240, 236, 245], { long: 1.1, wide: .75 }); }); },
  // ACACIA (the umbrella thorn): tiny twice-divided leaves, grey-green and see-through, long white thorns in pairs
  acacia: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 12, from: .04, angle: 55, shoot: 24, w: 2.5,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => pinnate(g2, r2, p, a, 84 * k, 8, 5, mix3(l0, l1, r2()), { thorns: 22 }) });
    if (mode === "flower") clusters(g, r, 12, [.15, .85, .1, .8], (x, y) => fruit(g, x, y, 6 + 2 * r(), rgbOf(S.colors.blossom))); },
  // CITRUS: glossy dark oval leaves, dense; in fruit oranges, a few white flowers among them (it fruits and flowers at once)
  citrus: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 8, from: .08, angle: 46, shoot: 70, w: 3.5, leavesAlong: 1,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("oval", 4, 46, 15, 2.0, { under: .15, gloss: .3 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode === "fruit") {
      const ripe = rgbOf(S.colors.fruit);
      clusters(g, r, 5, [.2, .8, .2, .75], (x, y) => fruit(g, x, y, 15 + 3 * r(), shade(mix3(ripe, [150, 160, 50], r() < .15 ? .55 : .08 * r()), .95 + .1 * r()), { ...FRUIT_LOOK.citrus, tilt: (r() - .5) * .8 }));
      clusters(g, r, 3, [.2, .8, .1, .7], (x, y) => flower(g, r, x, y, 9, [250, 248, 238], [235, 220, 120], { wide: .5 }));
    } },
  // HYDRANGEA: big broad toothed leaves in pairs; in flower the round mopheads of four-petalled florets
  hydrangea: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 4, from: .12, angle: 50, shoot: 34, w: 4.5, opposite: true,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("toothed", 2, 70, 27, 1.1, { under: .15 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode === "flower") clusters(g, r, 2, [.3, .7, .08, .32], (x, y) => mophead(g, r, x, y, 50 + 10 * r(), rgbOf(S.colors.blossom))); },
  // RHODODENDRON: long leathery glossy leaves in whorls at the shoots' ends; in flower a domed truss of funnels
  rhododendron: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 3, from: .3, angle: 42, shoot: 70, w: 4,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("lance", 7, 78, 15, 4.2, { under: .2, underC: [150, 130, 90], underK: .5, gloss: .35 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode === "flower") clusters(g, r, 2, [.3, .7, .06, .3], (x, y) => truss(g, r, x, y, 46, rgbOf(S.colors.blossom))); },
  // SAGUARO: not a spray -- what crowns each top of the column (grow.js columnCactus: the card's middle `mid` up it on
  // the top): the felted, spiny crown; in flower a ring of waxy white flowers on it, in fruit red fruit, some split
  saguaro: (g, r, S, mode) => {
    // (at(a): round the dome's shoulder, a radians from its top -- the top the card's middle, where grow.js pins it to
    //  the column's tip, and R about the column's girth there)
    const cx = CW / 2, R = CW * .44, cy = CH * (1 - (S.twig.mid ?? .24)), at = (a) => [cx + Math.sin(a) * R * .95, cy + (1 - Math.cos(a)) * R * 1.05];
    g.save(); g.lineCap = "round";
    for (let i = 0; i < 60; i++) {   // (the top's spines, pale, raying from the felt)
      const a = (r() - .5) * 2.4, [x, y] = at(a * .8), l = 10 + 12 * r();
      g.strokeStyle = css(mix3([200, 190, 160], [120, 100, 80], r()), .9); g.lineWidth = 1.2;
      g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.sin(a) * l, y - Math.cos(a) * l); g.stroke();
    }
    g.fillStyle = css([150, 130, 100], .8); g.beginPath(); g.ellipse(cx, cy + 3, R * .32, 7, 0, 0, TAU); g.fill();   // (the felt)
    if (mode === "flower") for (let i = 0; i < 9; i++) {
      const a = (i / 8 - .5) * 2.1 + .1 * (r() - .5), [x, y] = at(a), ux = Math.sin(a), uy = -Math.cos(a), l = 16 + 8 * r();
      g.strokeStyle = css([110, 130, 80]); g.lineWidth = 9; g.beginPath(); g.moveTo(x, y); g.lineTo(x + ux * l, y + uy * l); g.stroke();
      flower(g, r, x + ux * (l + 8), y + uy * (l + 8), 21 + 5 * r(), shade(rgbOf(S.colors.blossom), .92 + .1 * r()), [236, 206, 90], { petals: 12, wide: .45, long: 1.05, heart: [230, 226, 200] });
    }
    if (mode === "fruit") for (let i = 0; i < 8; i++) {
      const a = (i / 7 - .5) * 2 + .15 * (r() - .5), [x, y] = at(a), fx = x + Math.sin(a) * 14, fy = y - Math.cos(a) * 14;
      g.save(); g.translate(fx, fy); g.rotate(a); g.scale(.75, 1); fruit(g, 0, 0, 15, shade(rgbOf(S.colors.fruit), .85 + .25 * r())); g.restore();
      if (r() < .45) { g.fillStyle = css([150, 20, 40]); g.beginPath(); g.ellipse(fx, fy - 9, 9, 5, a, 0, TAU); g.fill(); }   // (split: the flesh)
    }
    g.restore();
  },
  // LINDEN: heart-shaped toothed leaves, lopsided; in flower hanging cymes of pale yellow flowers under their long
  // pale bracts, in fruit the same bracts with round nutlets
  linden: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 7, from: .08, angle: 50, shoot: 62, w: 3.5, leavesAlong: 1,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("heart", 2, 50, 24, 1.3, { under: .2 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode !== "leaf") clusters(g, r, 7, [.15, .85, .15, .8], (x, y) => cyme(g, r, x, y, mode === "flower" ? rgbOf(S.colors.blossom) : rgbOf(S.colors.fruit), mode === "flower")); },
  // TULIP TREE: four-lobed leaves cut square at the tip; in flower upright green-and-orange cups, in fruit upright cones
  tuliptree: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 6, from: .1, angle: 50, shoot: 70, w: 4,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("tulip", 2, 60, 30, 1.2, { under: .15 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode === "flower") clusters(g, r, 3, [.25, .75, .1, .5], (x, y) => tulipCup(g, r, x, y, 24, rgbOf(S.colors.blossom)));
    if (mode === "fruit") clusters(g, r, 3, [.25, .75, .1, .5], (x, y) => cone(g, r, x, y, 54, 18, rgbOf(S.colors.fruit), (r() - .5) * .4)); },
  // ARAUCARIA: rope-like shoots clad all round in stiff overlapping triangular leaves; in fruit a great round cone
  araucaria: (g, r, S, mode) => {
    const [l0, l1] = L(S), base = [CW / 2, CH], tip = [CW / 2 + (r() - .5) * 40, CH * .06], ctl = [CW / 2 + (r() - .5) * 50, CH * .5];
    for (let i = 0; i < 2; i++) {   // (a side rope or two, behind)
      const t = .35 + .3 * r(), p = qpt(base, ctl, tip, t), sd = i ? 1 : -1, e = [p[0] + sd * (60 + 30 * r()), p[1] - 110 - 60 * r()];
      rope(g, r, p, [(p[0] + e[0]) / 2, (p[1] + e[1]) / 2 + 20], e, 26, l0, l1);
    }
    rope(g, r, base, ctl, tip, 36, l0, l1);
    if (mode === "fruit") { const R = 34; fruit(g, tip[0], tip[1] + R + 10, R, rgbOf(S.colors.fruit));
      g.strokeStyle = css([60, 60, 30], .5); g.lineWidth = 1; for (let i = 0; i < 40; i++) { const a = r() * TAU, d = r() * R * .8; g.beginPath(); g.arc(tip[0] + Math.cos(a) * d, tip[1] + R + 10 + Math.sin(a) * d, 3, 0, TAU); g.stroke(); } }
  },
  // BANANA: a paddle leaf (the frond's cell: its midrib up the middle) -- broad, its blade torn along its veins (its
  // bunch is no painting but bodies of its own: grow.js bunch, paintBodies)
  banana: (g, r, S, mode) => {
    const [l0, l1] = L(S), cx = CW / 2;
    for (const sd of [1, -1]) {
      let y = CH * .97;
      while (y > CH * .03) {
        const h = 8 + r() * 48, y1 = Math.max(CH * .02, y - h), hw = (yy) => CW * .48 * Math.pow(Math.sin(Math.PI * clamp(1 - yy / CH, 0, 1)), .45);
        const slope = 22, c = shade(mix3(l0, l1, r()), .92 + .16 * r());
        const gr = g.createLinearGradient(cx, 0, cx + sd * CW * .5, 0);
        gr.addColorStop(0, css(shade(c, 1.1))); gr.addColorStop(.85, css(c)); gr.addColorStop(1, css(shade(mix3(c, [150, 130, 70], r() < .3 ? .5 : 0), .85)));
        g.fillStyle = gr; g.beginPath(); g.moveTo(cx, y); g.lineTo(cx + sd * hw(y - slope), y - slope); g.lineTo(cx + sd * hw(y1 - slope), y1 - slope); g.lineTo(cx, y1); g.fill();
        g.strokeStyle = css(shade(c, .85), .5); g.lineWidth = .7;
        for (let v = y - 4; v > y1; v -= 5) { g.beginPath(); g.moveTo(cx, v); g.lineTo(cx + sd * hw(v - slope), v - slope); g.stroke(); }
        y = y1 - (r() < .6 ? 1.5 : 0);   // (a tear)
      }
    }
    g.strokeStyle = css([196, 206, 150]); g.lineWidth = 6; g.beginPath(); g.moveTo(cx, CH); g.lineTo(cx, CH * .03); g.stroke();
  },
  // BAMBOO: fans of long narrow pointed leaves on thin twigs
  bamboo: (g, r, S, mode) => broadSpray(g, r, S, mode, { nodes: 7, from: .08, angle: 44, shoot: 56, w: 1.6, leavesAlong: 1,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("lance", 5, 96, 12, 1.5, { under: .25, blur: 2 })(g2, r2, p, a, m, l0, l1, t, k) }),
  // GRAPEVINE: big rounded lobed leaves on a cane, curling tendrils; in fruit hanging bunches of grapes
  grape: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 4, from: .12, angle: 55, shoot: 40, w: 3,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("vine", 1, 70, 32, 0, { under: .2 })(g2, r2, p, a, m, l0, l1, t, k) });
    g.strokeStyle = css([130, 140, 70]); g.lineWidth = 1.3;
    for (let i = 0; i < 4; i++) { let x = CW * (.2 + .6 * r()), y = CH * (.15 + .6 * r()), a = r() * TAU; g.beginPath(); g.moveTo(x, y);
      for (let k = 0; k < 24; k++) { a += .35; x += Math.cos(a) * (5 - k * .15); y += Math.sin(a) * (5 - k * .15); g.lineTo(x, y); } g.stroke(); }
    if (mode === "fruit") clusters(g, r, 2, [.3, .7, .3, .55], (x, y) => bunch(g, r, x, y, rgbOf(S.colors.fruit))); },
  // HAZEL: soft rounded toothed leaves; in flower (late winter) hanging yellow catkins, in fruit nuts in ragged husks
  hazel: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 7, from: .08, angle: 48, shoot: 60, w: 3, leavesAlong: 1,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("heart", 2, 50, 26, 1.3, { under: .2 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode === "flower") clusters(g, r, 9, [.15, .85, .1, .8], (x, y) => catkin(g, r, x, y, 60 + 20 * r(), 10, rgbOf(S.colors.blossom), Math.PI + (r() - .5) * .5));
    if (mode === "fruit") clusters(g, r, 5, [.2, .8, .15, .75], (x, y) => { const n = 2 + Math.floor(r() * 2); for (let j = 0; j < n; j++) nut(g, r, x + (j - (n - 1) / 2) * 20, y + (j % 2) * 6, rgbOf(S.colors.fruit)); }); },
  // PERSIMMON (kaki): broad glossy oval leaves, alternate; in fruit (late autumn, often on bare wood) orange globes,
  // flattened, each sat in its big four-lobed calyx
  persimmon: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 7, from: .08, angle: 48, shoot: 70, w: 4, leavesAlong: 1,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("oval", 3, 60, 25, 1.8, { under: .2, gloss: .3 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode === "fruit") clusters(g, r, 7, [.2, .8, .15, .75], (x, y) => {
      const R = 19 + 4 * r(), c = shade(rgbOf(S.colors.fruit), .92 + .14 * r());
      fruit(g, x, y, R, c, { gloss: .4, long: .82, tilt: (r() - .5) * .4 });
      g.fillStyle = css([96, 104, 52]);   // (the calyx: four broad sepals on its top)
      for (let i = 0; i < 4; i++) { const a = i / 4 * TAU + .4; g.beginPath(); g.ellipse(x + Math.cos(a) * R * .3, y - R * .74 + Math.sin(a) * R * .1, R * .34, R * .12, a, 0, TAU); g.fill(); }
    }); },
  // PAULOWNIA (the foxglove tree): huge soft heart-shaped leaves, few to a shoot; in spring, before them, upright
  // panicles of violet foxglove bells; in fruit clusters of pointed brown capsules
  paulownia: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 4, from: .12, angle: 52, shoot: 50, w: 5, opposite: true,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("heart", 1, 100, 70, 0, { under: .2 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode === "flower") clusters(g, r, 4, [.2, .8, .38, .62], (x, y) => candle(g, r, x, y, 160, 52, rgbOf(S.colors.blossom), [236, 214, 120]));
    if (mode === "fruit") clusters(g, r, 4, [.2, .8, .15, .6], (x, y) => { for (let j = 0; j < 5; j++) fruit(g, x + (r() - .5) * 34, y + (r() - .5) * 30, 7 + 2 * r(), shade(rgbOf(S.colors.fruit), .9 + .2 * r()), { long: 1.45, gloss: .2, calyx: 1, tilt: (r() - .5) * .8 }); }); },
  // AVOCADO: long leathery elliptic leaves, dark and glossy, paler beneath; in fruit the pears on long stalks -- a
  // narrow neck over a round body, green-black and pebbled
  avocado: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 7, from: .08, angle: 46, shoot: 70, w: 3.8, leavesAlong: 1,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("oval", 4, 70, 22, 2.1, { under: .3, underC: [150, 162, 130], underK: .6, gloss: .3 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode === "fruit") clusters(g, r, 4, [.2, .8, .2, .6], (x, y) => {
      const R = 16 + 3 * r(), c = shade(rgbOf(S.colors.fruit), .85 + .25 * r()), tl = (r() - .5) * .3;
      hung(g, x, y, 26);
      fruit(g, x, y + 26 + R * .55, R * .55, c, { long: 1.2, tilt: tl });   // (the neck)
      fruit(g, x + Math.sin(tl) * R, y + 26 + R * 1.6, R, c, { long: 1.12, speck: 1, gloss: .2, tilt: tl });
    }); },
  // CACAO: big drooping oblong leaves, red-bronze when young; its pods are no painting but bodies on the trunk and the
  // big limbs (grow.js pods, paintBodies)
  cacao: (g, r, S, mode) => broadSpray(g, r, S, mode, { nodes: 5, from: .12, angle: 58, shoot: 50, w: 3.5,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("lance", 3, 100, 26, 1.4, { under: .2, gloss: .2 })(g2, r2, p, a + (a > 0 ? .5 : -.5), m, t > .92 ? [150, 80, 50] : l0, t > .92 ? [170, 100, 60] : l1, t, k) }),
  // DELONIX (the flame tree): feathery twice-divided leaves; in flower clusters of scarlet flowers, one petal of each
  // streaked white and yellow; in fruit long dark flat pods hanging
  delonix: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 6, from: .1, angle: 52, shoot: 30, w: 3,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => pinnate(g2, r2, p, a, 120 * k, 10, 6, mix3(l0, l1, r2())) });
    if (mode === "flower") clusters(g, r, 7, [.15, .85, .05, .6], (x, y) => { for (let j = 0; j < 6; j++) {
      const fx = x + (r() - .5) * 46, fy = y + (r() - .5) * 40, R = 12 + 3 * r();
      flower(g, r, fx, fy, R, shade(rgbOf(S.colors.blossom), .9 + .15 * r()), [200, 40, 20], { wide: .85, long: 1.05 });
      g.fillStyle = css([250, 236, 200], .9); g.beginPath(); g.ellipse(fx, fy - R * .55, R * .22, R * .4, (r() - .5) * .6, 0, TAU); g.fill();   // (the standard: white, flecked)
      g.fillStyle = css([220, 60, 30]); for (let q = 0; q < 4; q++) { g.beginPath(); g.arc(fx + (r() - .5) * R * .3, fy - R * (.4 + .3 * r()), 1.2, 0, TAU); g.fill(); }
    } });
    if (mode === "fruit") clusters(g, r, 4, [.2, .8, .1, .4], (x, y) => pod(g, x, y, 150 + 40 * r(), 12, rgbOf(S.colors.fruit), (r() - .5) * .5)); },
  // ALBIZIA (the silk tree): feathery leaves, finer still; in flower the powder-puffs, silky threads white at their
  // base and pink at their tips; in fruit pale flat papery pods
  albizia: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 7, from: .08, angle: 54, shoot: 28, w: 2.6,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => pinnate(g2, r2, p, a, 100 * k, 9, 5, mix3(l0, l1, r2())) });
    if (mode === "flower") clusters(g, r, 11, [.15, .85, .05, .6], (x, y) => puff(g, r, x, y, 30 + 8 * r(), rgbOf(S.colors.blossom)));
    if (mode === "fruit") clusters(g, r, 5, [.2, .8, .1, .5], (x, y) => pod(g, x, y, 90 + 30 * r(), 16, rgbOf(S.colors.fruit), (r() - .5) * .9, { flat: 1 })); },
  // KIWI (Actinidia): a twining vine's big round heart leaves, felted pale beneath, on bristly red-brown canes; in
  // flower cream cups round a golden boss; in fruit the brown fuzzy ovals hanging in twos and threes
  kiwi: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 4, from: .12, angle: 55, shoot: 44, w: 3.4,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("heart", 1, 76, 66, 0, { under: .3, underC: [196, 196, 160], underK: .6 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode === "flower") clusters(g, r, 5, [.2, .8, .15, .7], (x, y) => flower(g, r, x, y, 15 + 3 * r(), rgbOf(S.colors.blossom), [226, 176, 40], { petals: 6, wide: .75, long: .95 }));
    if (mode === "fruit") clusters(g, r, 3, [.25, .75, .2, .55], (x, y) => { const n = 2 + Math.floor(r() * 2);
      for (let j = 0; j < n; j++) { const fx = x + (j - (n - 1) / 2) * 26; hung(g, x, y, 14 + j * 6); fruit(g, fx, y + 34 + (j % 2) * 8, 13, shade(rgbOf(S.colors.fruit), .9 + .2 * r()), { long: 1.25, peel: 1, tilt: (r() - .5) * .3 }); } }); },
  // GINKGO: long shoots set with knobbly spurs, each spur a tuft of three to five fans on long stalks; in fruit the
  // round yellow seeds hanging in twos on long stalks, dusted with bloom
  ginkgo: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 11, from: .06, angle: 62, shoot: 12, w: 3.6,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => {
      g2.fillStyle = css(WOODC(S)); g2.beginPath(); g2.arc(p[0], p[1], 3.2, 0, TAU); g2.fill();   // (the spur)
      leafCluster("fan", 3 + Math.floor(r2() * 3), 62, 30, 2.6, { under: .1, blur: 3 })(g2, r2, p, a, m, l0, l1, t, k);
    } });
    if (mode === "fruit") clusters(g, r, 5, [.2, .8, .2, .75], (x, y) => { for (const sd of [-1, 1]) { const fx = x + sd * 9, fy = y + 34 + 6 * r(); hung(g, x, y, fy - y - 9);
      fruit(g, fx, fy, 9.5, shade(rgbOf(S.colors.fruit), .9 + .2 * r()), { bloom: .35, long: 1.06 }); } }); },
  // HIBISCUS (Chinese hibiscus, rosa-sinensis): glossy toothed ovals; in flower great open trumpets, five broad
  // overlapping petals round a dark eye, the column of stamens standing far out of it, tipped with red stigmas
  hibiscus: (g, r, S, mode) => { broadSpray(g, r, S, mode, { nodes: 6, from: .1, angle: 48, shoot: 26, w: 3.2, leavesAlong: 1,
    leafAt: (g2, r2, p, a, m, l0, l1, t, k = 1) => leafCluster("toothed", 2, 52, 18, 1.3, { under: .12, gloss: .35 })(g2, r2, p, a, m, l0, l1, t, k) });
    if (mode === "flower") clusters(g, r, 4, [.22, .78, .08, .6], (x, y) => hibiscusFlower(g, r, x, y, 26 + 5 * r(), rgbOf(S.colors.blossom))); },
  // a FAN PALM's leaf (`fan`: the share of it that is stalk -- mesh.js FAN_W, the blade's outline): the stalk, edged
  // with hooked teeth; the blade pleated, its segments radiating from the hastula and split apart toward the rim,
  // their tips drooping, white threads hanging from them. `dead` (the skirt's): straw-brown, the segments folded shut
  fan: (g, r, S, mode) => fanLeaf(g, r, S, mode === "dead"),
  // OPUNTIA: one PAD (grow.js padPlant sets its pads on this oval: its middle .38 up the card, .36 long and .23 wide a
  // side of it, as shares of the card's length): green, dotted with areoles in a lattice; in flower yellow cups on its
  // upper rim, in fruit red-purple barrels
  opuntia: (g, r, S, mode) => {
    const [l0, l1] = L(S), cx = CW / 2, cy = CH * .62, ry = CH * .36, rx = CW * .43;
    const ex = (t) => rx * (.82 + .18 * t);   // (wider toward its top: t 0 the foot .. 1 the top)
    const c = mix3(l0, l1, r());
    g.save(); g.beginPath();
    for (let i = 0; i <= 64; i++) { const a = i / 64 * TAU, t = .5 - .5 * Math.cos(a); g.lineTo(cx + Math.sin(a) * ex(t), cy + Math.cos(a) * ry); }
    const gr = g.createRadialGradient(cx - rx * .3, cy - ry * .3, 10, cx, cy, ry);
    gr.addColorStop(0, css(shade(c, 1.15))); gr.addColorStop(.75, css(c)); gr.addColorStop(1, css(shade(c, .7)));
    g.fillStyle = gr; g.fill(); g.clip();
    for (let j = 0; j < 12; j++) for (let i = 0; i < 7; i++) {   // (the areoles: felt dots, yellow bristles, a spine or two)
      const x = cx + (i - 3 + (j % 2) * .5) * 34 + (r() - .5) * 4, y = cy - ry + 18 + j * 34 + (r() - .5) * 4;
      g.fillStyle = css([150, 130, 70]); g.beginPath(); g.arc(x, y, 3.2, 0, TAU); g.fill();
      g.strokeStyle = css([220, 200, 120], .8); g.lineWidth = 1;
      if (r() < .4) { const a = -Math.PI / 2 + (r() - .5); g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * 16, y + Math.sin(a) * 16); g.stroke(); }
    }
    g.restore();
    const rim = (n, draw) => { for (let i = 0; i < n; i++) { const a = Math.PI + (i / Math.max(1, n - 1) - .5) * 1.5 + (r() - .5) * .2; draw(cx + Math.sin(a) * ex(1) * .9, cy + Math.cos(a) * ry * .97, a); } };
    if (mode === "flower") rim(3, (x, y) => tulipCup(g, r, x, y - 4, 22, rgbOf(S.colors.blossom)));
    if (mode === "fruit") rim(4, (x, y, a) => { g.save(); g.translate(x, y); g.rotate(Math.PI - a); fruit(g, 0, -16, 11, shade(rgbOf(S.colors.fruit), .85 + .25 * r()), { long: 1.4 });
      g.fillStyle = css([90, 30, 50]); g.beginPath(); g.ellipse(0, -31, 6, 2.2, 0, 0, TAU); g.fill();
      g.fillStyle = css([230, 210, 130], .9); for (let i = 0; i < 9; i++) { g.beginPath(); g.arc((i % 3 - 1) * 6 + (i / 3 | 0) % 2 * 3 - 1.5, -26 + (i / 3 | 0) * 9, 1.2, 0, TAU); g.fill(); }
      g.restore(); });
  },
  // a ROSETTE of sword leaves (the dragon blood tree's, the Joshua tree's): rosettePaint
  rosette: rosettePaint,
  // willow: a long hanging strand of narrow leaves
  willow: (g, r, S) => {
    const [l0, l1] = L(S), wood = WOODC(S);
    for (let s = 0; s < 3; s++) {
      const x0 = CW / 2 + (s - 1) * 40 + (r() - .5) * 20, base = [x0, CH], tip = [x0 + (r() - .5) * 60, CH * .03], ctl = [x0 + (r() - .5) * 50, CH * .5];
      stem(g, base, ctl, tip, 2.5, 1.2, wood);
      for (let i = 0; i < 26; i++) {
        const t = .04 + .95 * i / 26, p = qpt(base, ctl, tip, t), d = qdir(base, ctl, tip, t);
        leaf(g, r, p[0], p[1], d + (i % 2 ? 1 : -1) * (.35 + .25 * r()), 44 + 18 * r(), 6 + 2 * r(), "lance", mix3(l0, l1, r()), { under: .35, blur: 3 });
      }
    }
  },
  // pine: a twig dense with long needles in pairs, brushing forward, a bud at its tip
  pine: (g, r, S) => {
    const [l0, l1] = L(S), wood = WOODC(S);
    for (let s = 0; s < 5; s++) {
      const x0 = CW / 2 + (s - 2) * 42, base = [CW / 2, CH], tip = [x0 + (r() - .5) * 30, CH * (.08 + .3 * r())], ctl = [(CW / 2 + x0) / 2, CH * .6];
      stem(g, base, ctl, tip, 5, 3, wood);
      g.shadowColor = "rgba(5,15,5,0.4)"; g.shadowBlur = 3;
      for (let i = 0; i < 130; i++) {
        const t = .3 + .7 * Math.pow(r(), .7), p = qpt(base, ctl, tip, t), d = qdir(base, ctl, tip, t);
        const a = d + (r() - .5) * 2.2 * (1.1 - t * .4), len = 55 + 30 * r();
        const c = shade(mix3(l0, l1, r()), .8 + .45 * r());
        g.strokeStyle = css(c); g.lineWidth = 2;
        g.beginPath(); g.moveTo(p[0], p[1]); g.quadraticCurveTo(p[0] + Math.sin(a) * len * .5, p[1] - Math.cos(a) * len * .5 - 4, p[0] + Math.sin(a) * len, p[1] - Math.cos(a) * len); g.stroke();
      }
      g.shadowColor = "transparent";
    }
  },
  // spruce: a flat fishbone spray, side shoots off both sides, every shoot bristling with short needles
  spruce: (g, r, S) => {
    const [l0, l1] = L(S), wood = WOODC(S);
    const needles = (p0, c, p1, len, n) => {
      for (let i = 0; i < n; i++) {
        const t = i / n, p = qpt(p0, c, p1, t), d = qdir(p0, c, p1, t);
        for (const sd of [1, -1]) {
          const a = d + sd * (.9 + .4 * r()), L2 = len * (.7 + .5 * r()) * (1 - .3 * t);
          g.strokeStyle = css(shade(mix3(l0, l1, r()), .75 + .5 * r())); g.lineWidth = 2.2;
          g.beginPath(); g.moveTo(p[0], p[1]); g.lineTo(p[0] + Math.sin(a) * L2, p[1] - Math.cos(a) * L2); g.stroke();
        }
      }
    };
    const base = [CW / 2, CH], tip = [CW / 2 + (r() - .5) * 30, CH * .04], ctl = [CW / 2 + (r() - .5) * 40, CH * .5];
    g.shadowColor = "rgba(5,15,5,0.35)"; g.shadowBlur = 3;
    for (let i = 0; i < 9; i++) {
      const t = .1 + .85 * i / 9, p = qpt(base, ctl, tip, t), d = qdir(base, ctl, tip, t);
      for (const sd of [1, -1]) {
        const a = d + sd * (.85 + .2 * r()), len = (CW * .48) * (1 - .6 * t) * (.8 + .3 * r());
        const e = [p[0] + Math.sin(a) * len, p[1] - Math.cos(a) * len], c = [(p[0] + e[0]) / 2, (p[1] + e[1]) / 2 - 10];
        stem(g, p, c, e, 2.2, 1.2, wood);
        needles(p, c, e, 16, Math.round(len / 3.5));
      }
    }
    stem(g, base, ctl, tip, 4, 2, wood);
    needles(base, ctl, tip, 18, 90);
    g.shadowColor = "transparent";
  },
  // cypress: scale-leaved sprays forking again and again into a feathery fan
  cypress: (g, r, S) => {
    const [l0, l1] = L(S);
    g.lineCap = "round";
    g.shadowColor = "rgba(5,15,5,0.4)"; g.shadowBlur = 3;
    const fork = (p, a, len, w, depth) => {
      const e = [p[0] + Math.sin(a) * len, p[1] - Math.cos(a) * len];
      g.strokeStyle = css(shade(mix3(l0, l1, r()), .8 + .4 * r())); g.lineWidth = w;
      g.beginPath(); g.moveTo(p[0], p[1]); g.lineTo(e[0], e[1]); g.stroke();
      if (depth === 0) return;
      const n = 3 + Math.floor(r() * 2);
      for (let i = 1; i <= n; i++) {
        const q = [p[0] + (e[0] - p[0]) * i / (n + .5), p[1] + (e[1] - p[1]) * i / (n + .5)];
        fork(q, a + (i % 2 ? 1 : -1) * (.55 + .2 * r()), len * (.45 + .1 * r()), w * .72, depth - 1);
      }
      fork(e, a + (r() - .5) * .3, len * .5, w * .75, depth - 1);
    };
    fork([CW / 2, CH], (r() - .5) * .2, CH * .5, 8, 3);
    g.shadowColor = "transparent";
  },
  // a palm frond: the midrib down the middle of the cell, the leaflets off both sides, reaching forward (twig
  // `leaflets` a side, their `reach` -- how far forward they point, radians from straight out -- and `width`: a
  // coconut's many, long and narrow; a date palm's stiffer)
  frond: (g, r, S) => {
    const [l0, l1] = L(S), n = S.twig.leaflets ?? 46, reach = S.twig.reach ?? .35, lw = S.twig.width ?? 4.5;
    g.shadowColor = "rgba(5,15,5,0.35)"; g.shadowBlur = 3;
    for (let i = 0; i < n; i++) {
      const t = .05 + .93 * i / n, y = CH * (1 - t);
      for (const sd of [1, -1]) {
        const len = CW * .5 * Math.sin(Math.PI * clamp(.1 + t * .9, 0, 1)) * (.85 + .2 * r()), a = sd * (1.4 - reach - .35 * t);
        leaf(g, r, CW / 2, y, a, len, lw + 2 * (1 - t), "lance", mix3(l0, l1, r()), { under: .1, blur: 2, dry: S.twig.dry });
      }
    }
    g.shadowColor = "transparent";
    g.strokeStyle = css([150, 140, 80]); g.lineWidth = 4;
    g.beginPath(); g.moveTo(CW / 2, CH); g.lineTo(CW / 2, 6); g.stroke();
  },
};

// THE FRUIT AND FLOWERS laid over a spray whose recipe has none of its own (bake.js bakeSprays: its fruit column, its
// flower column) -- every species bears something: acorns, cones, catkins, keys, dates, pods. Each by the spray style;
// colours the species' colors.fruit / colors.blossom
const acorn = (g, r, x, y, R, col) => {
  g.save(); g.translate(x, y); g.rotate((r() - .5) * .8);
  fruit(g, 0, R * .3, R, col, { gloss: .3, long: 1.15 });
  g.fillStyle = css([110, 92, 60]); g.beginPath(); g.ellipse(0, -R * .3, R * 1.02, R * .55, 0, Math.PI, TAU); g.fill();   // (its cup)
  g.fillStyle = css([80, 66, 44]);
  for (let i = 0; i < 9; i++) { g.beginPath(); g.arc(-R * .8 + i * R * .2, -R * .45 + Math.sin(i) * R * .08, R * .1, 0, TAU); g.fill(); }
  g.restore();
};
// a cone: scales in rows round an ellipse, hanging (a spruce's) or held (a pine's), len along `a` (0: up)
const cone = (g, r, x, y, len, w, col, a) => {
  g.save(); g.translate(x, y); g.rotate(a); g.shadowColor = "rgba(20,10,5,0.4)"; g.shadowBlur = 3;
  g.fillStyle = css(shade(col, .6)); g.beginPath(); g.ellipse(0, -len / 2, w / 2, len / 2, 0, 0, TAU); g.fill();
  g.shadowColor = "transparent";
  const rows = Math.max(3, Math.round(len / (w * .32)));
  for (let i = 0; i < rows; i++) for (let j = -1; j <= 1; j++) {
    const t = (i + .5) / rows, ww = w * .5 * Math.sin(Math.PI * clamp(.08 + t * .9, 0, 1));
    g.fillStyle = css(shade(col, .8 + .35 * r()));
    g.beginPath(); g.ellipse(j * ww * .55 + (i % 2) * ww * .25, -len * t, ww * .42, len / rows * .65, 0, 0, TAU); g.fill();
  }
  g.restore();
};
// a catkin: a soft hanging (or standing) tassel of tiny flowers
const catkin = (g, r, x, y, len, w, col, a) => {
  g.save(); g.translate(x, y); g.rotate(a);
  for (let i = 0; i < len / 2; i++) {
    const t = i / (len / 2), cx = Math.sin(t * 2.2) * w * .4;
    g.fillStyle = css(shade(col, .75 + .45 * r())); g.beginPath(); g.arc(cx + (r() - .5) * w * .6, -t * len, w * .32 * (1 - .4 * t), 0, TAU); g.fill();
  }
  g.restore();
};
// a pair of maple keys: two winged seeds joined at their nuts
const keys = (g, r, x, y, L, col) => {
  g.save(); g.translate(x, y); g.rotate((r() - .5) * .6);
  g.strokeStyle = css([90, 80, 40]); g.lineWidth = 1; g.beginPath(); g.moveTo(0, -L * .4); g.lineTo(0, 0); g.stroke();
  for (const sd of [1, -1]) {
    g.save(); g.rotate(sd * (.9 + .2 * r()));
    g.fillStyle = css(shade(col, .9 + .2 * r())); g.beginPath(); g.moveTo(0, 0);
    g.bezierCurveTo(L * .32, L * .15, L * .3, L * .9, 0, L); g.bezierCurveTo(-L * .05, L * .6, -L * .12, L * .2, 0, 0); g.fill();
    fruit(g, 0, L * .1, L * .12, shade(col, .7));
    g.restore();
  }
  g.restore();
};
// a hanging POD from (x, y): a long flat bean, `w` wide, curving by `bend` (radians) along its length -- its edge darker,
// the seeds' bumps along it (flat: papery, the seeds showing through as paler lumps)
const pod = (g, x, y, len, w, col, bend, o = {}) => {
  g.save(); g.translate(x, y); g.rotate(bend * .3);
  g.shadowColor = "rgba(20,15,10,0.35)"; g.shadowBlur = 3;
  const c = [w * .2 + bend * len * .5, len * .5], e = [bend * len * .7, len];
  g.strokeStyle = css(shade(col, .75)); g.lineCap = "round"; g.lineWidth = w;
  g.beginPath(); g.moveTo(0, 0); g.quadraticCurveTo(c[0], c[1], e[0], e[1]); g.stroke();
  g.shadowColor = "transparent"; g.strokeStyle = css(col); g.lineWidth = w * .7;
  g.beginPath(); g.moveTo(0, 0); g.quadraticCurveTo(c[0], c[1], e[0], e[1]); g.stroke();
  g.fillStyle = css(o.flat ? shade(col, 1.12) : shade(col, .82), .7);
  for (let t = .12; t < .95; t += .1) { const q = qpt([0, 0], c, e, t); g.beginPath(); g.ellipse(q[0], q[1], w * .26, w * .36, 0, 0, TAU); g.fill(); }
  g.restore();
};
// a POWDER-PUFF (albizia, mimosa): silky threads radiating from a point into a half ball, white at their base and
// `col` at their tips
const puff = (g, r, x, y, R, col) => {
  g.save(); g.lineCap = "round";
  for (let i = 0; i < 90; i++) {
    const a = -Math.PI * (.05 + .9 * r()) + (r() - .5) * .4, L = R * (.65 + .35 * r()), ex = x + Math.cos(a) * L, ey = y + Math.sin(a) * L * .9;
    const gr = g.createLinearGradient(x, y, ex, ey); gr.addColorStop(0, css([250, 246, 240], .9)); gr.addColorStop(.5, css(mix3([250, 246, 240], col, .5), .9)); gr.addColorStop(1, css(shade(col, .95 + .1 * r())));
    g.strokeStyle = gr; g.lineWidth = 1.1; g.beginPath(); g.moveTo(x, y); g.lineTo(ex, ey); g.stroke();
    g.fillStyle = css(shade(col, 1.05)); g.beginPath(); g.arc(ex, ey, 1.3, 0, TAU); g.fill();
  }
  g.restore();
};
const hung = (g, x, y, dy) => { g.strokeStyle = css([90, 80, 50]); g.lineWidth = 1.2; g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + dy); g.stroke(); };
const FC = (S, k, dflt) => rgbOf(S.colors[k] ?? dflt);
const OVERLAY = {
  oak: { fruit: (g, r, S) => clusters(g, r, 9, [.2, .8, .15, .8], (x, y) => { const n = 2 + Math.floor(r() * 2); for (let j = 0; j < n; j++) acorn(g, r, x + j * 20, y + 8 * j, 11 + 2 * r(), FC(S, "fruit", 0x8a8a34)); }) },
  birch: { fruit: (g, r, S) => clusters(g, r, 6, [.2, .8, .15, .7], (x, y) => catkin(g, r, x, y, 60 + 20 * r(), 9, FC(S, "fruit", 0x7a5a34), Math.PI + (r() - .5) * .6)) },
  willow: { flower: (g, r, S) => clusters(g, r, 12, [.25, .75, .05, .9], (x, y) => catkin(g, r, x, y, 30 + 10 * r(), 10, FC(S, "blossom", 0xd8d060), (r() - .5) * 1.2)) },
  pine: { fruit: (g, r, S) => clusters(g, r, 4, [.3, .7, .2, .55], (x, y) => cone(g, r, x, y, 58 + 12 * r(), 34, FC(S, "fruit", 0x8a6a44), (r() - .5) * 1.4)) },
  spruce: { fruit: (g, r, S) => clusters(g, r, 4, [.25, .75, .05, .45], (x, y) => cone(g, r, x, y, 70 + 16 * r(), 24, FC(S, "fruit", 0x7a5032), Math.PI + (r() - .5) * .3)) },
  cypress: { fruit: (g, r, S) => clusters(g, r, 8, [.25, .75, .15, .75], (x, y) => cone(g, r, x, y, 18, 18, FC(S, "fruit", 0x7a7458), r() * TAU)) },
  maple: { fruit: (g, r, S) => clusters(g, r, 6, [.2, .8, .15, .75], (x, y) => keys(g, r, x, y, 34 + 6 * r(), FC(S, "fruit", 0xb0a050))) },
  frond: { fruit: (g, r, S) => { for (let i = 0; i < 3; i++) { const x = CW / 2 + (i - 1) * 34, y = CH * .82; hung(g, x, y - 30, 30); for (let j = 0; j < 30; j++) fruit(g, x + (r() - .5) * 44, y + r() * 64, 6.5, shade(FC(S, "fruit", 0xc0702a), .8 + .3 * r()), FRUIT_LOOK.frond); } } },
  ceiba: { fruit: (g, r, S) => clusters(g, r, 3, [.25, .75, .2, .6], (x, y) => { hung(g, x, y, 20); g.save(); g.translate(x, y + 50); g.scale(.6, 1); fruit(g, 0, 0, 30, FC(S, "fruit", 0x5a7a3a)); g.restore(); }) },
  chestnut: { fruit: (g, r, S) => clusters(g, r, 5, [.25, .75, .2, .7], (x, y) => {
    const R = 13 + 3 * r(), c = FC(S, "fruit", 0x7a9a3a);
    g.strokeStyle = css(shade(c, .8)); g.lineWidth = 1.4;
    for (let k = 0; k < 16; k++) { const a = k / 16 * TAU; g.beginPath(); g.moveTo(x + Math.cos(a) * R * .8, y + Math.sin(a) * R * .8); g.lineTo(x + Math.cos(a) * R * 1.35, y + Math.sin(a) * R * 1.35); g.stroke(); }
    fruit(g, x, y, R, c);
  }) },
  rosette: { fruit: (g, r, S) => {   // (a dragon blood tree's: berry bunches hanging on stalks below the leaves' fan)
    const cy = CH * (1 - (S.twig.mid ?? .38));
    for (let k = 0; k < 4; k++) { const bx = CW / 2 + (k - 1.5) * 34, by = cy + 30 + r() * 20; hung(g, bx, cy, by - cy);
      for (let i = 0; i < 16; i++) fruit(g, bx + (r() - .5) * 30, by + r() * 34, 6.5, shade(FC(S, "fruit", 0xd0502a), .8 + .3 * r()), { gloss: .5 }); } } },
};

// THE BODIES' SWATCHES (mesh.js BODY_BANDS): the last column (col) in bands, each a tube's skin unrolled -- across,
// round it; down the cell, along it from its foot (the cell's bottom, v 0) to its tip. Opaque: a far bunch keeps its colour
function paintBodies(g, S, r, col) {
  const x0 = col * CW, band = (k) => [x0 + BODY_BANDS[k][0] * CW - 6, x0 + BODY_BANDS[k][1] * CW + 6], Y = (v) => CH * (1 - v);
  g.save(); g.beginPath(); g.rect(x0, 0, CW, CH); g.clip();
  g.fillStyle = css([110, 120, 60]); g.fillRect(x0, 0, CW, CH);
  // a NUT (a coconut's): three faint ridges along it, glossy green ripening yellow-orange (by the plant: its own
  // shade), its cap of brown sepals at its foot and a dark point at its tip
  if (S.crown?.nuts) { const [a, b] = band("nut"), f = rgbOf(S.colors.fruit), w = b - a;
    const gr = g.createLinearGradient(0, Y(0), 0, Y(1));
    gr.addColorStop(0, css([110, 84, 50])); gr.addColorStop(.1, css([120, 96, 56])); gr.addColorStop(.16, css(shade(f, .85))); gr.addColorStop(.5, css(f));
    gr.addColorStop(.92, css(shade(f, .9))); gr.addColorStop(1, css([70, 60, 36]));
    g.fillStyle = gr; g.fillRect(a, 0, w, CH);
    for (let i = 0; i < 3; i++) { const fx = a + 6 + (i + .5) / 3 * (w - 12);
      g.fillStyle = css([255, 255, 220], .14); g.fillRect(fx - w / 16, 0, w / 8, CH); g.fillStyle = css([40, 50, 10], .2); g.fillRect(fx + w / 6, 0, 3, CH); }
    for (let i = 0; i < 70; i++) { g.fillStyle = css(r() < .5 ? [255, 250, 200] : [70, 60, 20], .1); g.beginPath(); g.arc(a + r() * w, Y(.15 + .8 * r()), 1 + r() * 3, 0, TAU); g.fill(); }
  } else
  // a POD (a cacao's): ten deep furrows down it, warty between them; green at its foot ripening to its colour, its
  // tip darker
  if (S.pods) { const [a, b] = band("pod"), f = rgbOf(S.colors.fruit), w = b - a;
    const gr = g.createLinearGradient(0, Y(0), 0, Y(1));
    gr.addColorStop(0, css([96, 104, 50])); gr.addColorStop(.12, css(mix3(f, [120, 130, 50], .4))); gr.addColorStop(.3, css(f));
    gr.addColorStop(.85, css(shade(f, .92))); gr.addColorStop(1, css(shade(f, .55)));
    g.fillStyle = gr; g.fillRect(a, 0, w, CH);
    for (let i = 0; i < 10; i++) {   // (the ridges: a lit crest, a dark furrow)
      const fx = a + 6 + (i + .5) / 10 * (w - 12);   // (round the band itself, inside its margins)
      g.fillStyle = css([255, 250, 200], .16); g.fillRect(fx - w / 40, 0, w / 20, CH);
      g.fillStyle = css([60, 30, 10], .35); g.fillRect(fx + w / 20 - 1.5, 0, 3, CH);
    }
    for (let i = 0; i < 160; i++) { g.fillStyle = css(r() < .5 ? [255, 240, 190] : [70, 40, 20], .18); g.beginPath(); g.arc(a + r() * w, Y(.1 + .85 * r()), 1 + r() * 2, 0, TAU); g.fill(); }
  } else
  // a FINGER: five-angled (lighter and darker facets round it), a dark neck at its foot, a black-brown tip
  { const [a, b] = band("finger"), f = rgbOf(S.colors.fruit), w = b - a;
    const gr = g.createLinearGradient(0, Y(0), 0, Y(1));
    gr.addColorStop(0, css([92, 96, 52])); gr.addColorStop(.1, css(shade(f, .8))); gr.addColorStop(.25, css(f)); gr.addColorStop(.85, css(shade(f, 1.05)));
    gr.addColorStop(.93, css(mix3(f, [70, 60, 30], .5))); gr.addColorStop(.97, css([46, 38, 26])); gr.addColorStop(1, css([30, 26, 20]));
    g.fillStyle = gr; g.fillRect(a, 0, w, CH);
    for (let i = 0; i < 5; i++) {   // (the facets: a lighter face, a darker ridge)
      const fx = a + 6 + (i + .5) / 5 * (w - 12);
      g.fillStyle = css([255, 255, 220], .1); g.fillRect(fx - w / 14, 0, w / 9, CH);
      g.fillStyle = css([40, 50, 20], .22); g.fillRect(fx + w / 10 - 1.5, 0, 3, CH);
    }
    g.fillStyle = css([90, 70, 40], .35);
    for (let i = 0; i < 40; i++) { g.beginPath(); g.arc(a + r() * w, Y(.2 + .7 * r()), .8 + r() * 1.5, 0, TAU); g.fill(); } }
  // the BUD: maroon-purple bracts, overlapping, their edges paler; a waxy bloom over it
  { const [a, b] = band("bud"), w = b - a;
    const gr = g.createLinearGradient(0, Y(0), 0, Y(1));
    gr.addColorStop(0, css([96, 40, 52])); gr.addColorStop(.5, css([118, 42, 74])); gr.addColorStop(1, css([84, 30, 56]));
    g.fillStyle = gr; g.fillRect(a, 0, w, CH);
    for (let v = .04; v < 1; v += .07 + .03 * r()) {   // (the bracts' lower edges: arcs round it)
      g.strokeStyle = css([170, 90, 120], .55); g.lineWidth = 2.5;
      g.beginPath(); for (let x = a; x <= b; x += 4) g.lineTo(x, Y(v) - 10 * Math.sin((x - a) / w * Math.PI * 2 + v * 9)); g.stroke();
      g.strokeStyle = css([50, 16, 30], .4); g.lineWidth = 2;
      g.beginPath(); for (let x = a; x <= b; x += 4) g.lineTo(x, Y(v) - 10 * Math.sin((x - a) / w * Math.PI * 2 + v * 9) + 3); g.stroke();
    }
    g.fillStyle = css([200, 190, 220], .12); g.fillRect(a, 0, w, CH); }
  // the STALK: green, finely lined along it, a scar here and there where a bract fell
  { const [a, b] = band("stalk"), w = b - a;
    g.fillStyle = css([118, 132, 64]); g.fillRect(a, 0, w, CH);
    for (let i = 0; i < 14; i++) { g.fillStyle = css(r() < .5 ? [96, 110, 50] : [140, 150, 84], .5); g.fillRect(a + r() * w, 0, 1.2, CH); }
    for (let i = 0; i < 9; i++) { g.fillStyle = css([90, 76, 50], .6); g.fillRect(a, Y(r()), w, 2.5); } }
  g.restore();
}

// the berries' colour in a bush's atlas: a magenta no leaf has, which render.js leafFrag recolours to each bush's own fruit
export const FRUIT_MARKER = 0xff00ff;
// THE SPRAY ATLAS of a species (fruitHex: a bush's berries, FRUIT_MARKER): a DataTexture 1280 (1536) x 512, columns as above
const DENSE = 7;   // (px: how far column 4's copies are shifted -- about half a small leaf)
export function bakeSprays(S, seed = 1, fruitHex = null) {
  // (columns: five -- and a sixth for the bodies of a plant with far cards; a palm's go in its fifth, it has no far cards)
  const bodies = !!(S.crown?.bunch || S.crown?.nuts || S.pods), cells = bodies && S.habit !== "palm" ? 6 : 5;
  const W = CW * cells, H = CH, cv = canvas(W, H), g = cv.getContext("2d", { willReadFrequently: true });
  const r = rng(seed * 977 + S.twig.style.length * 31);
  const paint = SPRAYS[S.twig.style] ?? SPRAYS.shrub;
  const Sx = fruitHex != null ? { ...S, colors: { ...S.colors, fruit: fruitHex } } : S;
  // the species' flowers (a spring blossom, or flowers in their season) and its fruit, each a column of its own -- an
  // apple both blossoms and bears; what it has not, a leafy spray stands in for
  const flower = !!(S.season?.blossom || S.season?.flowers), fruit = !!(S.season?.fruit || fruitHex != null);
  for (const [col, mode] of [[0, "leaf"], [1, S.crown?.skirt ? "dead" : "leaf"], [2, flower ? "flower" : "leaf"], [3, fruit ? "fruit" : "leaf"]]) {
    g.save(); g.beginPath(); g.rect(col * CW, 0, CW, CH); g.clip(); g.translate(col * CW, 0);
    paint(g, r, Sx, mode);
    OVERLAY[S.twig.style]?.[mode]?.(g, r, Sx);   // (fruit or flowers for a recipe that paints none of its own)
    g.restore();
  }
  // the far spray: column 0's, filled (a palm has no far cards: its bodies' swatches there)
  if (bodies) paintBodies(g, Sx, r, cells - 1);
  if (cells === 6 || !bodies) {
  const src = canvas(CW, CH);
  src.getContext("2d").drawImage(cv, 0, 0, CW, CH, 0, 0, CW, CH);
  g.save(); g.beginPath(); g.rect(4 * CW, 0, CW, CH); g.clip();
  g.filter = "brightness(0.9)";
  for (let k = 0; k < 8; k++) g.drawImage(src, 4 * CW + Math.cos(k / 8 * TAU) * DENSE, Math.sin(k / 8 * TAU) * DENSE);
  g.filter = "none";
  g.drawImage(src, 4 * CW, 0);
  g.restore();
  }
  const img = g.getImageData(0, 0, W, H);
  const data = bleed(img.data, W, H);
  // (rows flipped: the cell's bottom edge -- the spray's base -- is v = 0)
  const out = new Uint8Array(W * H * 4);
  for (let y = 0; y < H; y++) out.set(data.subarray((H - 1 - y) * W * 4, (H - y) * W * 4), y * W * 4);
  const t = new THREE.DataTexture(out, W, H, THREE.RGBAFormat);
  t.colorSpace = THREE.SRGBColorSpace;
  t.magFilter = THREE.LinearFilter; t.minFilter = THREE.LinearMipmapLinearFilter; t.generateMipmaps = true;
  t.anisotropy = 4; t.needsUpdate = true;
  t.userData = { cells, flower, fruit, sprayBox: trims(img.data, W) };
  return t;
}

// THE CARDS' TRIM: where the paintings are, so the cards are cut to them (mesh.js) -- a card's clear texels are pixels
// rasterized, sampled and thrown away, and that, not the shading, is what a forest's leaves cost (2026-11-18: the
// sprays fill 25-60% of their cells). [u0, u1, v0, v1]: the rectangle round all five columns' paintings (v from the
// base, the cell's lower edge), a card's quad cut to it at no cost in triangles
function trims(px, W) {
  const on = (x, y) => px[(y * W + x) * 4 + 3] > 8, m = 2;
  let x0 = CW, x1 = -1, y0 = CH, y1 = -1;
  for (let col = 0; col < 5; col++)
    for (let y = 0; y < CH; y++) for (let x = 0; x < CW; x++) if (on(col * CW + x, y)) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
  return x1 < 0 ? [0, 1, 0, 1]
    : [Math.max(0, x0 - m) / CW, Math.min(CW, x1 + 1 + m) / CW, 1 - Math.min(CH, y1 + 1 + m) / CH, 1 - Math.max(0, y0 - m) / CH];
}

// the colour carried out past the leaves' edges into the clear texels (their alpha stays 0), ring by ring, so
// a filtered or mip-mapped edge blends toward the leaf's own colour instead of toward black
export function bleed(src, W, H, rings = 8) {
  const d = new Uint8ClampedArray(src), A = new Uint8Array(W * H);
  for (let i = 0; i < W * H; i++) A[i] = d[i * 4 + 3] > 120 ? 1 : 0;   // (a shadow's faint dark fringe is not a leaf: it takes the leaves' colour too)
  // the first front: the clear texels touching a leaf; each ring takes the mean of its leafy neighbours, then the
  // clear texels touching it are the next front
  let front = [];
  const N4 = [1, -1, W, -W];
  const touches = (i) => { const x = i % W; for (const o of N4) { const j = i + o; if (j < 0 || j >= W * H || (o === 1 && x === W - 1) || (o === -1 && x === 0)) continue; if (A[j]) return true; } return false; };
  for (let i = 0; i < W * H; i++) if (!A[i] && touches(i)) front.push(i);
  for (let ring = 0; ring < rings && front.length; ring++) {
    const vals = new Float32Array(front.length * 3);
    front.forEach((i, k) => {
      const x = i % W; let r = 0, g = 0, b = 0, n = 0;
      for (const o of N4) { const j = i + o; if (j < 0 || j >= W * H || (o === 1 && x === W - 1) || (o === -1 && x === 0) || !A[j]) continue; r += d[j * 4]; g += d[j * 4 + 1]; b += d[j * 4 + 2]; n++; }
      vals[k * 3] = r / n; vals[k * 3 + 1] = g / n; vals[k * 3 + 2] = b / n;
    });
    front.forEach((i, k) => { d[i * 4] = vals[k * 3]; d[i * 4 + 1] = vals[k * 3 + 1]; d[i * 4 + 2] = vals[k * 3 + 2]; A[i] = 2; });
    const next = new Set();
    for (const i of front) { const x = i % W; for (const o of N4) { const j = i + o; if (j < 0 || j >= W * H || (o === 1 && x === W - 1) || (o === -1 && x === 0) || A[j]) continue; next.add(j); } }
    for (const i of front) A[i] = 1;
    front = [...next];
  }
  // beyond the rings: the image's mean leaf colour
  let mr = 0, mg = 0, mb = 0, mn = 0;
  for (let i = 0; i < W * H; i++) if (src[i * 4 + 3] > 128) { mr += src[i * 4]; mg += src[i * 4 + 1]; mb += src[i * 4 + 2]; mn++; }
  if (mn) for (let i = 0; i < W * H; i++) if (!A[i]) { d[i * 4] = mr / mn; d[i * 4 + 1] = mg / mn; d[i * 4 + 2] = mb / mn; }
  return d;
}

// the aspect (width / length) of a spray cell, which the leaf cards are cut to
export const SPRAY_ASPECT = CW / CH;
