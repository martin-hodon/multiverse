// THE FLOWERS (2026-11-18): the meadow's and the cottage beds' flowers, grown here rather than read as items (they were
// tools/flowergen.py's polygon plants: flat-coloured petals cut to their outline in triangles, every petal of a whorl
// the same, the stem a straight rod). Now each plant is GROWN from its kind's recipe below with a seeded random, so no
// two petals, leaves or stems are alike, and its look is PAINTED: every petal, leaf, centre and stem is a few textured
// quads whose outline, veins, throat, spots and seeds are a cell of one baked ATLAS (cut out by alpha-to-coverage).
//
//   flowerGeometry(kind, variant)   a plant standing on y = 0: position, normal, uv (into the atlas), indexed;
//                                   userData.top the height of its highest bloom (where a butterfly sits)
//   flowerMaterial()                the one material every flower is drawn with (lit by the world's sun: light.js)
//   FLOWER_KINDS                    the kinds, by name ("daisy", "poppy", ...)
//
// A variant is a colouring and a growth: variant 0 and 1 of a kind differ in colour where the kind comes in several
// (a tulip red or yellow), and every variant is grown with its own random. A plant is about 150-450 triangles.
//
// THE PARTS (each a little mesh into the plant, in its own frame):
//   blade   a petal or a leaf: a grid `rows` along and `cols` across, bent up by `cup` (degrees over the horizontal)
//           and over its length by `curl` (+ up and in, - back), its sides lifted by `cupped`, twisted by `twist`;
//           its shape is the texture's (the cell is painted with the outline: widthAt, petals.js)
//   whorl   n blades round an axis, each a little different (length, angle, curl): the petals of a bloom
//   tube    a stem along a curve, 4 sides
//   dome    a bloom's centre: a low lathe with the centre's cell laid over it from above
//   spike   two crossed quads painted with a spike of florets (lavender): a whorl of florets each would be thousands
//
// THE ATLAS: CELL px square cells, painted on a canvas once (the first call): for every kind and variant its petal
// (and a second where the kind has two: an iris's standards, a rose's sepals, a cornflower's heart) and its centre;
// for every kind its leaf; one stem. Clear texels take the colour of their painted neighbours (bake.js bleed) so the
// mipmaps keep no dark fringe.
import * as THREE from "three";
import { wgslFn, texture, uv, normalWorld, faceDirection, attribute, positionLocal, uniform, renderGroup } from "three/tsl";
import { FOLIAGE_T } from "../foliage.js";
import { WIND, WIND_DIR } from "../grass.js";
import { lightWGSL } from "../light.js";
import { rng } from "../rng.js";
import { widthAt } from "../petals.js";
import { bleed } from "./bake.js";
import daisy from "../assets/plants/flowers/daisy.json" with { type: "json" };
import poppy from "../assets/plants/flowers/poppy.json" with { type: "json" };
import sunflower from "../assets/plants/flowers/sunflower.json" with { type: "json" };
import tulip from "../assets/plants/flowers/tulip.json" with { type: "json" };
import rose from "../assets/plants/flowers/rose.json" with { type: "json" };
import cornflower from "../assets/plants/flowers/cornflower.json" with { type: "json" };
import buttercup from "../assets/plants/flowers/buttercup.json" with { type: "json" };
import bluebell from "../assets/plants/flowers/bluebell.json" with { type: "json" };
import foxglove from "../assets/plants/flowers/foxglove.json" with { type: "json" };
import lavender from "../assets/plants/flowers/lavender.json" with { type: "json" };
import iris from "../assets/plants/flowers/iris.json" with { type: "json" };
import lily from "../assets/plants/flowers/lily.json" with { type: "json" };
import peony from "../assets/plants/flowers/peony.json" with { type: "json" };
import marigold from "../assets/plants/flowers/marigold.json" with { type: "json" };
import nettle from "../assets/plants/flowers/nettle.json" with { type: "json" };
import erica from "../assets/plants/flowers/erica.json" with { type: "json" };
import aloe from "../assets/plants/flowers/aloe.json" with { type: "json" };
import agave from "../assets/plants/flowers/agave.json" with { type: "json" };
import waterlily from "../assets/plants/flowers/waterlily.json" with { type: "json" };
import lotus from "../assets/plants/flowers/lotus.json" with { type: "json" };
import petunia from "../assets/plants/flowers/petunia.json" with { type: "json" };
import acanthus from "../assets/plants/flowers/acanthus.json" with { type: "json" };

const DEG = Math.PI / 180, TAU = Math.PI * 2;
const BLOOM = 1.6;   // (the blooms are drawn larger than life -- at true size they vanish at a few metres; tools/flowergen.py BLOOM_SCALE)

// ---- THE KINDS: colours, and how each is grown (grow(P, r, v): P the plant's parts, r its random, v its variant).
// petal / petal2: the painted petal -- shape, colours (base to tip; a list: one picked a variant), throat (its share
// from the base, and colour), veins ("fan" from the base, "mid" a midrib and its branches), and touches: spots
// (foxglove), crumple (poppy), sheen (a buttercup's gloss); leaf: the leaf's shape and colour; centre: its painting
const pick = (list, v) => Array.isArray(list) ? list[v % list.length] : list;
const GROW = {
  daisy(P, r) {
    const top = P.stem(.45, .04, .0018);
    for (let i = 0; i < 4; i++) P.leaf([0, .01, 0], i * 95 + r() * 40, 30, -40, .085, .02);
    P.leaf(top.at(.4), r() * 360, 35, -30, .045, .012); P.leaf(top.at(.6), r() * 360, 40, -30, .035, .01);
    P.bloom(top, 25, (B) => {
      B.whorl({ n: 11, r0: .006, L: .022, W: .0055, cup: 4, curl: -10, cupped: .15, cell: "petal" });
      B.whorl({ n: 10, r0: .006, L: .02, W: .0055, cup: 10, curl: -8, cupped: .15, cell: "petal", phase: 16 });
      B.dome(.0078, .0045);
    });
  },
  poppy(P, r) {
    const top = P.stem(.55, .08, .0018, .6);
    P.leaf([0, .02, 0], r() * 360, 25, -45, .11, .035); P.leaf([0, .03, 0], 180 + r() * 60, 30, -45, .1, .03);
    P.leaf(top.at(.3), r() * 360, 35, -35, .06, .02);
    P.bloom(top, 15, (B) => {
      B.whorl({ n: 2, r0: .003, L: .036, W: .046, cup: 30, curl: 16, cupped: .45, cell: "petal", rows: 3, cols: 2 });
      B.whorl({ n: 2, r0: .003, L: .033, W: .044, cup: 38, curl: 18, cupped: .45, cell: "petal", rows: 3, cols: 2, phase: 90 });
      B.dome(.0085, .011);
    });
  },
  sunflower(P, r) {
    const top = P.stem(1.6, .1, .011);
    for (let i = 0; i < 6; i++) P.leaf(top.at(.12 + i * .13), i * 137 + r() * 30, 25, -45, .16 - i * .015, .12 - i * .012, { stalk: .05, cols: 2 });
    P.bloom(top, 55, (B) => {
      B.whorl({ n: 17, r0: .055, L: .075, W: .024, cup: 2, curl: -12, cupped: .2, cell: "petal" });
      B.whorl({ n: 15, r0: .05, L: .065, W: .022, cup: 10, curl: -6, cupped: .2, cell: "petal", phase: 11 });
      B.dome(.064, .013);
    });
  },
  tulip(P, r) {
    const top = P.stem(.4, .02, .003);
    P.leaf([0, .02, 0], r() * 360, 72, -26, .2, .042, { cols: 2 }); P.leaf([0, .03, 0], 170 + r() * 30, 66, -34, .18, .038, { cols: 2 });
    P.bloom(top, 3, (B) => {
      B.whorl({ n: 3, r0: .004, L: .058, W: .044, cup: 74, curl: 12, cupped: .6, cell: "petal", rows: 3, cols: 2 });
      B.whorl({ n: 3, r0: .003, L: .055, W: .042, cup: 80, curl: 10, cupped: .6, cell: "petal", rows: 3, cols: 2, phase: 60 });
    });
  },
  rose(P, r) {
    const top = P.stem(.6, .06, .003);
    for (let i = 0; i < 3; i++) {
      const at = top.at(.25 + i * .2), yaw = 60 + i * 140 + r() * 30;
      for (let k = -1; k <= 1; k++) P.leaf(at, yaw + k * 35, 25 + Math.abs(k) * 5, -25, .045, .03);   // (a pinnate leaf: three leaflets)
    }
    P.bloom(top, 20, (B) => {
      B.whorl({ n: 5, r0: .002, L: .016, W: .007, cup: -35, curl: -10, cupped: .1, cell: "petal2", rows: 2, cols: 1, phase: 36 });
      B.whorl({ n: 5, r0: .003, L: .032, W: .034, cup: 24, curl: 26, cupped: .5, cell: "petal", rows: 2, cols: 2 });
      B.whorl({ n: 5, r0: .002, L: .026, W: .028, cup: 48, curl: 28, cupped: .5, cell: "petal", rows: 2, cols: 2, phase: 36 });
      B.whorl({ n: 4, r0: .001, L: .019, W: .02, cup: 72, curl: 30, cupped: .5, cell: "petal", rows: 2, cols: 1, phase: 10 });
    });
  },
  cornflower(P, r) {
    const top = P.stem(.5, .03, .0016);
    const side = P.branch(top, .55, [.08, .45, .02].map((x, i) => i === 1 ? x : x * (r() < .5 ? -1 : 1)), .0013);
    P.leaf(top.at(.15), r() * 360, 40, -40, .08, .008); P.leaf(top.at(.35), r() * 360, 45, -40, .07, .007);
    const head = (B) => {
      B.whorl({ n: 9, r0: .004, L: .015, W: .01, cup: 22, curl: -6, cupped: .3, cell: "petal" });
      B.whorl({ n: 6, r0: .001, L: .006, W: .003, cup: 60, curl: 0, cell: "petal2", rows: 1, cols: 1 });
    };
    P.bloom(top, 20, head); P.bloom(side, 30, head, .85);
  },
  buttercup(P, r) {
    const top = P.stem(.35, .03, .0014);
    const a = P.branch(top, .55, [-.06, .3, .03], .0012), b = P.branch(top, .7, [.05, .32, -.04], .0012);
    P.leaf([0, .015, 0], r() * 360, 12, -20, .05, .045); P.leaf([0, .02, 0], 150 + r() * 60, 15, -20, .05, .045);
    const cup = (B) => { B.whorl({ n: 5, r0: .0015, L: .012, W: .012, cup: 40, curl: 10, cupped: .45, cell: "petal", rows: 2, cols: 2 }); B.dome(.0032, .0026); };
    P.bloom(top, 10, cup); P.bloom(a, 20, cup, .9); P.bloom(b, 25, cup, .85);
  },
  bluebell(P, r) {
    const top = P.stem(.36, .07, .0018, .9);   // (arching over at the top)
    for (let i = 0; i < 4; i++) P.leaf([0, .01, 0], i * 95 + r() * 40, 72, -55, .23, .014);
    for (let i = 0; i < 5; i++) {   // (the bells hang along one side of the arch)
      const at = top.at(.72 + i * .06);
      P.hang(at, [.012 + r() * .01, -.012, .006 * (r() - .5)], 160 + r() * 15, (B) =>
        B.whorl({ n: 6, r0: .0015, L: .016, W: .008, cup: 82, curl: -80, cupped: .6, cell: "petal", rows: 3, cols: 1 }), 1 - i * .05);
    }
  },
  foxglove(P, r) {
    const top = P.stem(1.2, .03, .005);
    for (let i = 0; i < 5; i++) P.leaf([0, .02, 0], i * 72 + r() * 30, 15, -25, .26, .09, { cols: 2 });
    for (let i = 0; i < 3; i++) P.leaf(top.at(.12 + i * .1), r() * 360, 35, -25, .12 - i * .02, .045);
    for (let i = 0; i < 15; i++) {   // (the bells crowd round one side, smaller toward the tip, the topmost still buds)
      const at = top.at(.48 + i * .034), yaw = r() * 110 - 55, k = 1 - i * .045;
      P.hang(at, [.01 * Math.cos(yaw * DEG), -.004, .01 * Math.sin(yaw * DEG)], 105 + r() * 15, (B) =>
        B.whorl({ n: 5, r0: .004, L: .03, W: .02, cup: i > 12 ? 88 : 82, curl: i > 12 ? 10 : -30, cupped: .55, cell: "petal", rows: 2, cols: 1 }), k * .85);
    }
  },
  lavender(P, r) {   // (a low woody clump of grey needles, a dozen spikes standing out of it)
    for (let i = 0; i < 24; i++) {
      const a = i * 137.5, d = .02 + r() * .06;
      P.leaf([Math.cos(a * DEG) * d, .02 + r() * .12, Math.sin(a * DEG) * d], a, 45 + r() * 35, -25, .08, .013);
    }
    for (let i = 0; i < 12; i++) {
      const a = i * 30 + r() * 25, d = .06 + r() * .08;
      const top = P.stem(.34 + r() * .12, d, .0012, .15, a);
      P.spike(top, .08, .026);
    }
  },
  iris(P, r) {
    const top = P.stem(.7, .015, .004);
    for (let i = 0; i < 5; i++) P.leaf([0, .01, 0], (i - 2) * 14 + 90 + r() * 8, 84 - Math.abs(i - 2) * 5, -6 - r() * 10, .4 + r() * .12, .03, { flat: true });
    P.bloom(top, 2, (B) => {
      B.whorl({ n: 3, r0: .004, L: .052, W: .034, cup: 14, curl: -70, cupped: .35, cell: "petal", rows: 4, cols: 2 });
      B.whorl({ n: 3, r0: .003, L: .044, W: .026, cup: 78, curl: 22, cupped: .5, cell: "petal2", rows: 3, cols: 1, phase: 60 });
    });
  },
  lily(P, r) {
    const top = P.stem(.9, .03, .004);
    for (let i = 0; i < 7; i++) P.leaf(top.at(.12 + i * .1), i * 75 + r() * 30, 35, -35, .1, .016);
    const trumpet = (B) => {
      B.whorl({ n: 6, r0: .004, L: .07, W: .026, cup: 42, curl: -75, cupped: .3, cell: "petal", rows: 4, cols: 1 });
      B.stamens(6, .05, .018);
    };
    P.bloom(top, 55, trumpet); P.hang(top.at(.93), [-.02, .0, .01], 70, trumpet, .9);
  },
  peony(P, r) {   // (a leafy clump of three stems, each with a heavy double bloom: whorls of crumpled petals, the outer
    // open and broad, cupping tighter and smaller to a ball of a heart)
    for (let i = 0; i < 5; i++) P.leaf([0, .04, 0], i * 72 + r() * 30, 20, -35, .13, .06, { cols: 2 });
    for (let s = 0; s < 3; s++) {
      const top = P.stem(.6 + r() * .2, .05 + r() * .05, .0035, .1, s * 120 + r() * 40);
      for (let i = 0; i < 4; i++) P.leaf(top.at(.18 + i * .16), i * 110 + r() * 40, 28, -30, .12, .055, { cols: 2 });
      P.bloom(top, 14, (B) => {
        B.whorl({ n: 6, r0: .004, L: .05, W: .048, cup: 34, curl: 24, cupped: .55, cell: "petal", rows: 3, cols: 2 });
        B.whorl({ n: 7, r0: .003, L: .044, W: .042, cup: 52, curl: 28, cupped: .6, cell: "petal", rows: 3, cols: 2, phase: 25 });
        B.whorl({ n: 8, r0: .002, L: .037, W: .034, cup: 66, curl: 32, cupped: .6, cell: "petal2", rows: 2, cols: 2, phase: 12 });
        B.whorl({ n: 7, r0: .002, L: .03, W: .028, cup: 76, curl: 36, cupped: .6, cell: "petal2", rows: 2, cols: 2, phase: 40 });
        B.whorl({ n: 6, r0: .001, L: .022, W: .02, cup: 84, curl: 40, cupped: .55, cell: "petal2", rows: 2, cols: 1, phase: 5 });
        B.whorl({ n: 5, r0: .001, L: .014, W: .014, cup: 88, curl: 30, cupped: .5, cell: "petal2", rows: 2, cols: 1, phase: 30 });
      }, .95 + .15 * r());
    }
  },
  marigold(P, r) {   // (a bushy clump of finely cut leaves, a few stems each topped by a ruffled pompom, orange or gold)
    for (let i = 0; i < 8; i++) P.leaf([0, .03 + r() * .08, 0], i * 45 + r() * 30, 25 + r() * 25, -30, .07, .028);
    for (let s = 0; s < 5; s++) {
      const top = P.stem(.24 + r() * .12, .04 + r() * .05, .002, .05, s * 72 + r() * 40);
      for (let i = 0; i < 2; i++) P.leaf(top.at(.35 + i * .25), r() * 360, 30, -30, .055, .024);
      P.bloom(top, 12, (B) => {
        B.whorl({ n: 10, r0: .004, L: .017, W: .014, cup: 8, curl: 18, cupped: .4, cell: "petal", rows: 2, cols: 1 });
        B.whorl({ n: 9, r0: .003, L: .015, W: .013, cup: 32, curl: 22, cupped: .45, cell: "petal", rows: 2, cols: 1, phase: 18 });
        B.whorl({ n: 8, r0: .002, L: .012, W: .011, cup: 55, curl: 25, cupped: .45, cell: "petal2", rows: 2, cols: 1, phase: 9 });
        B.whorl({ n: 6, r0: .001, L: .008, W: .008, cup: 75, curl: 20, cupped: .4, cell: "petal2", rows: 1, cols: 1, phase: 30 });
      }, .9 + .2 * r());
    }
  },
  nettle(P, r) {   // (a stand of stiff square stems, toothed leaves in opposite pairs, green tassels of tiny flowers hanging at the nodes)
    for (let s = 0; s < 4; s++) {
      const top = P.stem(.7 + r() * .35, .03 + r() * .04, .003, .04, s * 90 + r() * 50);
      for (let i = 0; i < 6; i++) {
        const t = .14 + i * .14, at = top.at(t), yaw = s * 47 + i * 90, k = 1 - .45 * t;
        for (const sd of [0, 180]) {
          P.leaf(at, yaw + sd, 25, -45, .075 * k + .02, .04 * k + .01, { cols: 2 });
          if (i >= 2 && i < 5) {   // (the tassels: a strand of florets drooping from the leaf's foot)
            const a = (yaw + sd + 40) * DEG;
            P.spike({ tip: [at[0] + Math.cos(a) * .01, at[1], at[2] + Math.sin(a) * .01], dir: [Math.cos(a) * .7, -.7, Math.sin(a) * .7] }, .06, .014);
          }
        }
      }
      P.leaf(top.tip, r() * 360, 70, -20, .03, .014);
    }
  },
  erica(P, r) {   // (heather: a low mound of wiry stems, every one clad in tiny needles and topped by a spike of pink bells)
    for (let i = 0; i < 26; i++) {
      const a = i * 137.5, d = .02 + r() * .12;
      P.leaf([Math.cos(a * DEG) * d, .02 + r() * .1, Math.sin(a * DEG) * d], a, 40 + r() * 40, -10, .05, .01);
    }
    for (let i = 0; i < 20; i++) {
      const a = i * 137.5 + r() * 20, d = .04 + r() * .12;
      const top = P.stem(.16 + r() * .14, d, .0012, .3, a);
      P.spike(top, .065 + r() * .03, .028);
    }
  },
  aloe(P, r, v) {   // (a stemless rosette of thick, channelled, toothed leaves, grey-green flecked pale; a spike of tubular flowers)
    const n = 16;
    for (let i = 0; i < n; i++) {
      const u = i / n, a = i * 137.5;   // (the outer, older leaves first: longer, spread wider)
      P.leaf([0, .02 + u * .05, 0], a, 22 + u * 50, -18 + u * 10, .34 - u * .14, .045 - u * .01, { cupped: .55, cols: 2 });
    }
    if (v % 2 === 0) {
      const top = P.stem(.75 + r() * .2, .05, .006);
      P.spike(top, .2, .07);
    }
  },
  agave(P, r, v) {   // (a great rosette of broad, stiff, grey-blue leaves, each tapering to a black spine, the outer ones
    // arching over; once in its life a tall mast of yellow flowers in tiers -- the second variant in flower)
    const n = 26;
    for (let i = 0; i < n; i++) {
      const u = i / n, a = i * 137.5;
      P.leaf([0, .03 + u * .12, 0], a, 18 + u * 62, (u < .45 ? -32 : -6) * (1 - u), .62 - u * .28, .1 - u * .03, { cupped: .45, cols: 2, rows: 5 });
    }
    if (v % 2 === 1) {
      const top = P.stem(4.2 + r(), .15, .05);
      for (let i = 0; i < 9; i++) {
        const t = .55 + i * .05, at = top.at(t), a = (i * 137.5) * DEG, out = .5 * (1 - i / 11);
        const b = P.branch(top, t, [Math.cos(a) * out, at[1] + .25, Math.sin(a) * out], .01);
        P.spike(b, .14, .14);
      }
    }
  },
  waterlily(P, r) {   // (round notched pads flat on the water, a waxy many-petalled cup or two floating among them)
    for (let i = 0; i < 7; i++) {
      const a = i * 51 * DEG + r(), d = .12 + r() * .35;
      P.pad([Math.cos(a) * d, .01 + i * .0015, Math.sin(a) * d], .1 + r() * .07);
    }
    for (let k = 0; k < 1 + Math.floor(r() * 2); k++) {
      const a = r() * TAU, d = .05 + r() * .2;
      P.bloom({ tip: [Math.cos(a) * d, .02, Math.sin(a) * d], dir: [0, 1, 0] }, 6, (B) => {
        B.whorl({ n: 8, r0: .004, L: .042, W: .015, cup: 14, curl: 10, cupped: .35, cell: "petal", rows: 3, cols: 1 });
        B.whorl({ n: 8, r0: .004, L: .038, W: .014, cup: 36, curl: 10, cupped: .4, cell: "petal", rows: 3, cols: 1, phase: 22 });
        B.whorl({ n: 8, r0: .003, L: .031, W: .012, cup: 58, curl: 8, cupped: .4, cell: "petal", rows: 2, cols: 1, phase: 11 });
        B.whorl({ n: 7, r0: .002, L: .022, W: .009, cup: 76, curl: 5, cupped: .4, cell: "petal", rows: 2, cols: 1, phase: 33 });
        B.dome(.011, .006);
      }, .9 + .2 * r());
    }
  },
  lotus(P, r) {   // (great round pads, a few floating, most held up out of the water on stalks, cupped; the flowers higher still, big
    // cupped blooms round a flat-topped seed head)
    for (let i = 0; i < 3; i++) { const a = i * 2.1 + r(), d = .2 + r() * .3; P.pad([Math.cos(a) * d, .012 + i * .002, Math.sin(a) * d], .15 + r() * .06); }
    for (let i = 0; i < 4; i++) {
      const top = P.stem(.35 + r() * .5, .1 + r() * .2, .005, .1, i * 90 + r() * 40);
      P.pad(top.tip, .18 + r() * .08, { cup: .05, tilt: 10 + r() * 20 });
    }
    for (let k = 0; k < 2; k++) {
      const top = P.stem(.8 + r() * .35, .05 + r() * .12, .005, .05, k * 180 + r() * 60);
      P.bloom(top, 8, (B) => {
        B.whorl({ n: 5, r0: .006, L: .062, W: .044, cup: 30, curl: 26, cupped: .55, cell: "petal", rows: 3, cols: 2 });
        B.whorl({ n: 5, r0: .005, L: .058, W: .042, cup: 50, curl: 24, cupped: .55, cell: "petal", rows: 3, cols: 2, phase: 36 });
        B.whorl({ n: 5, r0: .004, L: .05, W: .036, cup: 68, curl: 18, cupped: .55, cell: "petal", rows: 3, cols: 2, phase: 18 });
        B.dome(.016, .012);
      }, .95 + .15 * r());
    }
  },
  petunia(P, r) {   // (a low sprawling mound of soft oval leaves, its stems trailing out and turning up, each with a wide
    // trumpet or two: five lobes round, flaring out of a narrow throat)
    for (let i = 0; i < 12; i++) P.leaf([0, .02 + r() * .05, 0], i * 30 + r() * 25, 12 + r() * 25, -25, .045, .03, { stalk: .01 });
    const trumpet = (B) => B.whorl({ n: 5, r0: .0015, L: .024, W: .03, cup: 66, curl: -62, cupped: .2, cell: "petal", rows: 3, cols: 2 });
    for (let s = 0; s < 7; s++) {
      const yaw = s * 51 + r() * 30, top = P.stem(.14 + r() * .1, .12 + r() * .1, .0016, .1, yaw);
      for (let i = 0; i < 3; i++) P.leaf(top.at(.3 + i * .22), yaw + 90 * (i % 2 ? 1 : -1) + r() * 30, 25, -25, .035, .022);
      P.bloom(top, 30 + r() * 25, trumpet, .95 + .15 * r());
      if (r() < .5) P.bloom(P.branch(top, .6, [Math.cos((yaw + 40) * DEG) * .06, top.tip[1] - .02, Math.sin((yaw + 40) * DEG) * .06], .0013), 45, trumpet, .85);
    }
  },
  acanthus(P, r, v) {   // (a clump of great glossy deeply cut leaves arching from the ground; one or two stiff spikes of hooded
    // flowers standing a metre and more above them)
    for (let i = 0; i < 11; i++) {
      const u = i / 11;
      P.leaf([0, .02 + u * .03, 0], i * 137.5, 28 + u * 30, -38 + u * 10, .5 - u * .16, .18 - u * .04, { cols: 2, rows: 5, cupped: .15 });
    }
    for (let k = 0; k < 1 + (v % 2); k++) {
      const top = P.stem(.55 + r() * .2, .03 + r() * .04, .006, 0, k * 150 + r() * 60);
      for (let i = 0; i < 3; i++) P.leaf(top.at(.25 + i * .2), r() * 360, 50, -20, .03, .012);
      P.spike(top, .42 + r() * .08, .14);
    }
  },
};
// a kind as drawn: its LOOK (the asset, assets/plants/flowers/<kind>.json: edited in the asset manager) and its recipe
const KINDS = Object.fromEntries(Object.entries({ daisy, poppy, sunflower, tulip, rose, cornflower, buttercup, bluebell, foxglove, lavender, iris, lily, peony,
  marigold, nettle, erica, aloe, agave, waterlily, lotus, petunia, acanthus }).map(([k, d]) => [k, { ...d, grow: GROW[k] }]));
export const FLOWER_KINDS = Object.keys(KINDS);
// where a kind grows (its asset's `habitat`): "meadow" (every world's meadow), "dry" (a warm world's dry ground --
// the aloe, the agave -- where periods.json names it), "water" (still shallow water -- the water lily, the lotus --
// likewise), "garden" (a kind of some worlds only -- the petunia, the acanthus -- in clumps among the meadow's, where
// periods.json names it): FLOWERS_OF(habitat)
export const flowerHabitat = (kind) => KINDS[kind]?.habitat ?? "meadow";
export const FLOWERS_OF = (habitat) => FLOWER_KINDS.filter((k) => flowerHabitat(k) === habitat);
// a kind's look replaced (the asset manager: the definition being edited) -- the atlas painted again, the plants regrown
export function setFlowerLook(kind, doc) {
  KINDS[kind] = { ...doc, grow: GROW[kind] };
  ATLAS?.tex.dispose(); ATLAS = null; geos.clear();
  if (TEX) TEX.value = atlas().tex;
}

// ---- THE GEOMETRY ---------------------------------------------------------------------------------------------------
// a mesh being built: points, normals, uvs, triangles -- in a frame (M: a Matrix4, the part's place in the plant)
class Mesh {
  constructor() { this.p = []; this.n = []; this.uv = []; this.ix = []; this.top = 0; }
  vert(p, n, uv, M, NM) {
    const v = _v.set(p[0], p[1], p[2]).applyMatrix4(M), w = _w.set(n[0], n[1], n[2]).applyMatrix3(NM).normalize();
    this.p.push(v.x, v.y, v.z); this.n.push(w.x, w.y, w.z); this.uv.push(uv[0], uv[1]);
    return this.p.length / 3 - 1;
  }
  geometry() {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(this.p, 3));
    g.setAttribute("normal", new THREE.Float32BufferAttribute(this.n, 3));
    g.setAttribute("uv", new THREE.Float32BufferAttribute(this.uv, 2));
    g.setAttribute("aSway", new THREE.Float32BufferAttribute(this.p.filter((_, i) => i % 3 === 1), 1));   // (its height on the plant: how far it sways)
    g.setIndex(this.ix);
    g.userData.top = this.top;
    return g;
  }
}
const _v = new THREE.Vector3(), _w = new THREE.Vector3();

// a curve from a to c through b's pull (quadratic): its point and its direction at t
const bez = (a, b, c, t) => a.map((_, i) => (1 - t) ** 2 * a[i] + 2 * (1 - t) * t * b[i] + t * t * c[i]);
const bezD = (a, b, c, t) => { const d = a.map((_, i) => 2 * (1 - t) * (b[i] - a[i]) + 2 * t * (c[i] - b[i])), l = Math.hypot(...d) || 1; return d.map((x) => x / l); };
// a frame at p whose +y is the direction d, turned about it by roll (radians)
function frameAt(p, d, roll = 0, scale = 1) {
  const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), new THREE.Vector3(...d).normalize());
  q.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), roll));
  return new THREE.Matrix4().compose(new THREE.Vector3(...p), q, new THREE.Vector3(scale, scale, scale));
}

// the parts of one plant, into mesh G; cells: the atlas's uv rectangles by name ("petal", "leaf", ...)
function plantParts(G, r, cells) {
  const put = (M, fn) => { const NM = new THREE.Matrix3().getNormalMatrix(M); fn((p, n, uv) => G.vert(p, n, uv, M, NM)); };
  const uvIn = (cell, u, t) => [cell[0] + u * cell[2], cell[1] + t * cell[3]];   // (u across, t from the cell's foot to its top)
  // a blade in frame M: from the origin out along +x, `cup` up from the horizontal, `curl` more over its length; z across
  function blade(M, { L, W, cup, curl = 0, cupped = 0, twist = 0, rows = 2, cols = 1, cell, flat = false }) {
    const C = cells[cell], steps = 12, pts = [[0, 0]], th = (s) => (cup + curl * s) * DEG;
    for (let q = 1; q <= steps; q++) { const a = th((q - .5) / steps); pts.push([pts[q - 1][0] + L / steps * Math.cos(a), pts[q - 1][1] + L / steps * Math.sin(a)]); }
    const mid = (s) => { const f = s * steps, q = Math.min(steps - 1, Math.floor(f)), t = f - q; return [pts[q][0] + (pts[q + 1][0] - pts[q][0]) * t, pts[q][1] + (pts[q + 1][1] - pts[q][1]) * t]; };
    put(M, (vert) => {
      const base = G.p.length / 3, cl = flat ? 1 : Math.max(1, cols);
      for (let i = 0; i <= rows; i++) {
        const s = i / rows, [x, y] = mid(s), a = th(s), tw = twist * DEG * s;
        const up = [-Math.sin(a), Math.cos(a), 0];   // (the blade's face, before its twist)
        for (let j = 0; j <= cl; j++) {
          const t = -1 + 2 * j / cl, w = W / 2 * t, lift = cupped * W / 2 * t * t;
          const ax = [Math.sin(tw) * up[0], Math.sin(tw) * up[1], Math.cos(tw)];   // (across: z, twisted toward the face)
          const nu = [Math.cos(tw) * up[0], Math.cos(tw) * up[1], -Math.sin(tw)];
          const n = [nu[0] - ax[0] * cupped * t * 1.5, nu[1] - ax[1] * cupped * t * 1.5, nu[2] - ax[2] * cupped * t * 1.5];
          vert([x + ax[0] * w + nu[0] * lift, y + ax[1] * w + nu[1] * lift, ax[2] * w + nu[2] * lift], n, uvIn(C, .5 + t * .5, s));
        }
      }
      for (let i = 0; i < rows; i++) for (let j = 0; j < cl; j++) {
        const a = base + i * (cl + 1) + j, b = a + 1, c = a + cl + 1, d = c + 1;
        G.ix.push(a, b, d, a, d, c);
      }
    });
  }
  // a tube along a curve (a stem), `sides` round, radius rr tapering to rr * .7
  function tube(a, b, c, rr, segs = 4, sides = 4) {
    const C = cells.stem;
    put(new THREE.Matrix4(), (vert) => {
      const base = G.p.length / 3;
      for (let i = 0; i <= segs; i++) {
        const t = i / segs, p = bez(a, b, c, t), d = bezD(a, b, c, t);
        const side = Math.abs(d[1]) < .9 ? [0, 1, 0] : [1, 0, 0];
        const u = new THREE.Vector3(...side).cross(new THREE.Vector3(...d)).normalize(), w = new THREE.Vector3(...d).cross(u);
        const R = rr * (1 - .3 * t);
        for (let k = 0; k <= sides; k++) {
          const ang = k / sides * TAU, n = [u.x * Math.cos(ang) + w.x * Math.sin(ang), u.y * Math.cos(ang) + w.y * Math.sin(ang), u.z * Math.cos(ang) + w.z * Math.sin(ang)];
          vert([p[0] + n[0] * R, p[1] + n[1] * R, p[2] + n[2] * R], n, uvIn(C, k / sides, t));
        }
      }
      for (let i = 0; i < segs; i++) for (let k = 0; k < sides; k++) {
        const q = base + i * (sides + 1) + k, s = q + sides + 1;
        G.ix.push(q, s, q + 1, q + 1, s, s + 1);
      }
    });
  }
  // the bloom's parts, in its frame M (its face up +y)
  const bloomParts = (M) => ({
    whorl({ n, r0, L, W, cup, curl = 0, cupped = 0, twist = 0, rows = 2, cols = 1, cell, phase = 0 }) {
      const ph = phase + r() * 360 / n;
      for (let i = 0; i < n; i++) {
        const yaw = (ph + i * 360 / n + (r() - .5) * 360 / n * .35) * DEG, k = 1 + (r() - .5) * .22;
        const Mi = M.clone().multiply(new THREE.Matrix4().makeRotationY(-yaw)).multiply(new THREE.Matrix4().makeTranslation(r0, 0, 0));
        blade(Mi, { L: L * k, W: W * (1 + (r() - .5) * .16), cup: cup + (r() - .5) * 10, curl: curl + (r() - .5) * 14, cupped, twist: twist + (r() - .5) * 12, rows, cols, cell });
      }
    },
    // a centre: a low dome, the centre's cell laid over it from above
    dome(R, h, sides = 8) {
      const C = cells.centre, prof = [[0, h], [R * .55, h * .85], [R, h * .3], [R * .96, 0]];
      put(M, (vert) => {
        const base = G.p.length / 3;
        vert([0, h, 0], [0, 1, 0], uvIn(C, .5, .5));
        for (let i = 1; i < prof.length; i++) for (let k = 0; k < sides; k++) {
          const a = k / sides * TAU, [rr, y] = prof[i], x = Math.cos(a) * rr, z = Math.sin(a) * rr;
          const ny = i === prof.length - 1 ? .2 : 1 - i * .25;
          vert([x, y, z], [Math.cos(a) * (1 - ny), ny, Math.sin(a) * (1 - ny)], uvIn(C, .5 + x / R * .48, .5 + z / R * .48));
        }
        for (let k = 0; k < sides; k++) G.ix.push(base, base + 1 + (k + 1) % sides, base + 1 + k);
        for (let i = 1; i < prof.length - 1; i++) for (let k = 0; k < sides; k++) {
          const a = base + 1 + (i - 1) * sides, b = a + sides, k1 = (k + 1) % sides;
          G.ix.push(a + k, a + k1, b + k1, a + k, b + k1, b + k);
        }
      });
    },
    // stamens standing out of a trumpet: thin blades of the centre's cell
    stamens(n, L, spread) {
      for (let i = 0; i < n; i++) {
        const a = (i / n * 360 + r() * 30) * DEG;
        blade(M.clone().multiply(new THREE.Matrix4().makeRotationY(-a)), { L, W: .004, cup: 90 - Math.atan2(spread, L) / DEG + (r() - .5) * 8, curl: -15, rows: 1, cols: 1, cell: "centre", flat: true });
      }
    },
  });
  return {
    // the main stem, from the foot: height h, its top bent off by `bend` (in a random direction, or the given yaw),
    // `nod` its top's droop (0 straight, 1 over to the side); returns the stem: .at(t) a point on it, .tip, .dir
    stem(h, bend, rr, nod = 0, yaw = r() * 360) {
      const a = yaw * DEG, dx = Math.cos(a), dz = Math.sin(a);
      const A = [0, 0, 0], B = [dx * bend * .3, h * .6, dz * bend * .3], C = [dx * (bend + nod * h * .25), h * (1 - nod * .2), dz * (bend + nod * h * .25)];
      tube(A, B, C, rr, h > .8 ? 6 : 4, h > .8 ? 5 : 4);
      return { at: (t) => bez(A, B, C, t), tip: C, dir: bezD(A, B, C, 1), h };
    },
    // a side stem from the main one's point at t, to `to` (relative to the foot)
    branch(stem, t, to, rr) {
      const A = stem.at(t), C = [A[0] + to[0], to[1], A[2] + to[2]], B = [A[0] + to[0] * .3, (A[1] + C[1]) / 2 + .03, A[2] + to[2] * .3];
      tube(A, B, C, rr, 3, 4);
      return { at: (s) => bez(A, B, C, s), tip: C, dir: bezD(A, B, C, 1) };
    },
    // a leaf from point p, turned to yaw (degrees), rising at cup and bending by curl, L long and W wide
    // (cupped: how far its sides rise -- a succulent's channelled leaf; rows: along it, more for a long arching one)
    leaf(p, yaw, cup, curl, L, W, { cols = 1, flat = false, stalk = 0, cupped = flat ? .05 : .25, rows = L > .15 ? 4 : 3 } = {}) {
      const k = 1 + (r() - .5) * .2;
      const M = new THREE.Matrix4().makeTranslation(...p).multiply(new THREE.Matrix4().makeRotationY(-(yaw + (r() - .5) * 20) * DEG));
      if (stalk) M.multiply(new THREE.Matrix4().makeTranslation(stalk, -stalk * .2, 0));
      blade(M, { L: L * 1.4 * k, W: W * 1.5 * k, cup: cup + (r() - .5) * 12, curl: curl + (r() - .5) * 20, cupped, twist: (r() - .5) * 30, rows, cols, cell: "leaf", flat });
    },
    // a round PAD (a water lily's, a lotus's) centred on p, R across its middle, face up -- tipped by `tilt` degrees,
    // its rim raised by `cup` metres (a lotus's bowl) -- a grid of the leaf's cell, painted a disc (paintPad)
    pad(p, R, { cup = 0, tilt = 0 } = {}) {
      const n = 4, M = frameAt(p, [Math.sin(tilt * DEG) * Math.cos(r() * TAU), Math.cos(tilt * DEG), Math.sin(tilt * DEG) * .3], r() * TAU), C = cells.leaf;
      put(M, (vert) => {
        const base = G.p.length / 3;
        for (let i = 0; i <= n; i++) for (let j = 0; j <= n; j++) {
          const x = (i / n * 2 - 1) * R, z = (j / n * 2 - 1) * R, q = (x * x + z * z) / (R * R);
          vert([x, cup * q, z], [-2 * cup * x / (R * R), 1, -2 * cup * z / (R * R)], uvIn(C, i / n, j / n));
        }
        for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { const a = base + i * (n + 1) + j, b = a + n + 1; G.ix.push(a, a + 1, b + 1, a, b + 1, b); }
      });
      G.top = Math.max(G.top, p[1]);
    },
    // a bloom on a stem's tip, tilted off its stem by `tilt` degrees (a random way), built by fn(B) in its own frame
    bloom(stem, tilt, fn, scale = 1) {
      const d = new THREE.Vector3(...stem.dir), a = r() * TAU;
      const off = new THREE.Vector3(Math.cos(a), 0, Math.sin(a)).cross(d).normalize();
      d.applyAxisAngle(off.lengthSq() > 1e-6 ? off : new THREE.Vector3(1, 0, 0), tilt * DEG);
      fn(bloomParts(frameAt(stem.tip, d.toArray(), r() * TAU, BLOOM * scale)));
      G.top = Math.max(G.top, stem.tip[1]);
    },
    // a bloom hanging off point p on a short stalk `off`, its face turned `angle` degrees from up (180: straight down)
    hang(p, off, angle, fn, scale = 1) {
      const q = [p[0] + off[0], p[1] + off[1], p[2] + off[2]], o = new THREE.Vector3(off[0], 0, off[2]).normalize();
      const d = new THREE.Vector3(0, 1, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0).cross(o).normalize(), angle * DEG);
      tube(p, [(p[0] + q[0]) / 2, Math.max(p[1], q[1]) + .004, (p[2] + q[2]) / 2], q, .0007, 1, 3);
      fn(bloomParts(frameAt(q, d.toArray(), r() * TAU, BLOOM * scale)));
      G.top = Math.max(G.top, q[1]);
    },
    // a spike of florets on a stem's tip: two crossed quads of the spike's cell, len long and w wide
    spike(stem, len, w) {
      const M = frameAt(stem.tip, stem.dir, r() * TAU, BLOOM * .8);
      for (const a of [0, 90]) put(M.clone().multiply(new THREE.Matrix4().makeRotationY(a * DEG)), (vert) => {
        const base = G.p.length / 3, C = cells.spike;
        for (const [x, y, u, t] of [[-w / 2, -len * .1, 0, 0], [w / 2, -len * .1, 1, 0], [w / 2, len, 1, 1], [-w / 2, len, 0, 1]]) vert([x, y, 0], [0, 0, 1], uvIn(C, u, t));
        G.ix.push(base, base + 1, base + 2, base, base + 2, base + 3);
      });
      G.top = Math.max(G.top, stem.tip[1] + len * BLOOM * .8);
    },
  };
}

const geos = new Map();
// a plant of `kind` (FLOWER_KINDS), its `variant` (0, 1, ...: its colouring and growth) -- made once, then shared
export function flowerGeometry(kind, variant = 0) {
  const key = kind + "|" + variant;
  if (!geos.has(key)) {
    const K = KINDS[kind], { cells } = atlas(), G = new Mesh();
    const own = (name) => cells.get(kind + "|" + (variant % VARIANTS) + "|" + name) ?? cells.get(kind + "|" + name);
    const named = new Proxy({}, { get: (_, name) => name === "stem" ? cells.get("stem") : own(name) });
    K.grow(plantParts(G, rng(KIND_SEED(kind) + variant * 7919), named), rng(KIND_SEED(kind) * 3 + variant * 31), variant);
    geos.set(key, G.geometry());
  }
  return geos.get(key);
}
const KIND_SEED = (kind) => [...kind].reduce((a, c) => (a * 31 + c.charCodeAt(0)) | 0, 7);
const VARIANTS = 2;   // (colourings painted a kind: a variant beyond takes these in turn, grown anew)

// ---- THE ATLAS ------------------------------------------------------------------------------------------------------
const CELL = 128, COLS = 16;
let ATLAS = null;
function atlas() {
  if (ATLAS) return ATLAS;
  const jobs = [["stem", (g, r) => paintStem(g, r)]];
  for (const [kind, K] of Object.entries(KINDS)) {
    if (K.leaf) jobs.push([kind + "|leaf", (g, r) => paintLeaf(g, r, K.leaf)]);
    for (let v = 0; v < VARIANTS; v++) {
      const p = (name) => kind + "|" + v + "|" + name;
      if (K.petal) jobs.push([p("petal"), (g, r) => paintPetal(g, r, K.petal, v)]);
      if (K.petal2) jobs.push([p("petal2"), (g, r) => paintPetal(g, r, K.petal2, v)]);
      if (K.centre) jobs.push([p("centre"), (g, r) => paintCentre(g, r, K.centre, v)]);
      if (K.spike) jobs.push([p("spike"), (g, r) => paintSpike(g, r, K.spike, v)]);
    }
  }
  const rows = Math.ceil(jobs.length / COLS), W = COLS * CELL, H = 2 ** Math.ceil(Math.log2(rows * CELL));
  const cv = document.createElement("canvas"); cv.width = W; cv.height = H;
  const g = cv.getContext("2d"), cells = new Map(), m = 3 / CELL;
  jobs.forEach(([name, paint], i) => {
    const cx = (i % COLS) * CELL, cy = Math.floor(i / COLS) * CELL;
    g.save(); g.translate(cx, cy); g.beginPath(); g.rect(0, 0, CELL, CELL); g.clip();
    paint(g, rng(KIND_SEED(name)));
    g.restore();
    // (uv: u across the cell, v from its foot -- the canvas's lower edge -- to its top; the image goes up unflipped,
    //  row 0 at v = 0, so a cell's foot is its larger canvas y)
    cells.set(name, [cx / W + m * CELL / W, (cy + CELL) / H - m * CELL / H, (CELL / W) * (1 - 2 * m), -(CELL / H) * (1 - 2 * m)]);
  });
  const img = g.getImageData(0, 0, W, H), data = bleed(img.data, W, H, 6);
  const tex = new THREE.DataTexture(new Uint8Array(data.buffer), W, H, THREE.RGBAFormat);
  tex.colorSpace = THREE.SRGBColorSpace; tex.generateMipmaps = true;
  tex.minFilter = THREE.LinearMipmapLinearFilter; tex.magFilter = THREE.LinearFilter; tex.anisotropy = 4;
  tex.needsUpdate = true;
  return ATLAS = { tex, cells, canvas: cv };
}

// ---- THE PAINTING (each into a CELL square, its foot at the bottom: y = CELL the base of a petal or leaf) -----------
const hex = (c) => { const n = parseInt(c.slice(1), 16); return [n >> 16, (n >> 8) & 255, n & 255]; };
const css = ([r, g, b], a = 1) => `rgba(${r | 0},${g | 0},${b | 0},${a})`;
const shade = (c, k) => c.map((x) => Math.max(0, Math.min(255, k > 1 ? x + (255 - x) * (k - 1) : x * k)));
const M = 3;   // (the margin kept clear round a cell's painting: the uv rectangle's inset)
// the outline of a blade of `shape`, its base at the cell's foot and its tip at the top; ragged: an edge's wobble
function outline(g, shape, r, { ragged = 0 } = {}) {
  const S = CELL - 2 * M, half = S / 2, cx = CELL / 2, N = 48, left = [], right = [];
  const wob = Array.from({ length: N + 1 }, () => 1 + (r() - .5) * ragged);
  const base = shape === "needle" || shape === "sword" || shape === "strap" ? "strap" : shape === "toothed" || shape === "cut" ? "lance" : shape === "lobed" ? "pointed" : shape;
  for (let i = 0; i <= N; i++) {
    const s = i / N;
    let w = widthAt(base, s);
    if (shape === "needle") w = .5 * (1 - s * .7);
    if (shape === "sword") w = s < .85 ? .9 : .9 * Math.sqrt(Math.max(0, 1 - (s - .85) / .15));
    if (shape === "heart" && s < .2) w = Math.max(w, .55 + s * 2);   // (a heart-shaped leaf's lobes at its base)
    if (shape === "toothed") w *= 1 - .12 * Math.max(0, Math.sin(s * Math.PI * 14));
    if (shape === "cut") w *= .45 + .55 * Math.abs(Math.sin(s * Math.PI * 3.5 + .3));
    if (shape === "lobed") w *= (.32 + .68 * Math.pow(Math.abs(Math.sin(s * Math.PI * 5.5 + .2)), .6)) * (1 - .1 * Math.max(0, Math.sin(s * Math.PI * 30)));   // (an acanthus's: deep lobes, each toothed)
    w = Math.max(0, w) * half * wob[i];
    const y = CELL - M - s * S;
    left.push([cx - w, y]); right.push([cx + w, y]);
  }
  g.beginPath();
  left.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y));
  if (shape === "fringed") {   // (a cornflower floret's tip: teeth)
    const [lx, ly] = left[N], [rx] = right[N];
    for (let k = 0; k <= 6; k++) g.lineTo(lx + (rx - lx) * k / 6, ly + (k % 2 ? 14 : 0));
  }
  if (shape === "heart") g.lineTo(cx, M + S * .08);   // (a notch)
  for (let i = N; i >= 0; i--) g.lineTo(...right[i]);
  g.closePath();
}
function paintPetal(g, r, P, v) {
  const base = hex(pick(P.colour, v)), tip = P.tip ? hex(pick(P.tip, v)) : shade(base, 1.12);
  const edge = (r() * 1e9) | 0, ragged = P.crumple ? .08 : .03;   // (the outline's wobble: the same for its fill and its rim)
  outline(g, P.shape, rng(edge), { ragged });
  g.save(); g.clip();
  const grd = g.createLinearGradient(0, CELL, 0, 0);
  grd.addColorStop(0, css(shade(base, .82))); grd.addColorStop(.5, css(base)); grd.addColorStop(1, css(tip));
  g.fillStyle = grd; g.fillRect(0, 0, CELL, CELL);
  if (P.throat) {   // (the throat: its own colour from the base, fading out; or the base colour paled (null))
    const [share, col] = P.throat, c = col ? hex(col) : shade(base, 1.35), t = g.createLinearGradient(0, CELL, 0, CELL - CELL * share * 1.4);
    t.addColorStop(0, css(c)); t.addColorStop(.65, css(c, .9)); t.addColorStop(1, css(c, 0));
    g.fillStyle = t; g.fillRect(0, 0, CELL, CELL);
  }
  if (P.throatPale) {   // (a foxglove's lip: pale inside its mouth, where the spots are)
    const t = g.createLinearGradient(0, CELL * .25, 0, CELL * .75);
    t.addColorStop(0, css(shade(base, 1.6), 0)); t.addColorStop(.5, css(shade(base, 1.6), .85)); t.addColorStop(1, css(shade(base, 1.6), 0));
    g.fillStyle = t; g.fillRect(0, 0, CELL, CELL);
  }
  // veins: fanning from the base, or a midrib with its branches
  g.strokeStyle = P.veinC ?? "rgba(0,0,0,.12)"; g.lineWidth = 1;
  if (P.veins === "fan") for (let i = 0; i < 13; i++) {
    const a = (i / 12 - .5) * 1.5;
    g.beginPath(); g.moveTo(CELL / 2, CELL - M);
    g.quadraticCurveTo(CELL / 2 + Math.sin(a) * CELL * .25, CELL * .55, CELL / 2 + Math.sin(a) * CELL * .55 + (r() - .5) * 6, M + r() * 10); g.stroke();
  } else if (P.veins === "mid") {
    g.lineWidth = 1.6; g.beginPath(); g.moveTo(CELL / 2, CELL - M); g.lineTo(CELL / 2, M + 6); g.stroke(); g.lineWidth = .8;
    for (let i = 1; i < 7; i++) { const y = CELL - M - i * CELL / 8; for (const s of [-1, 1]) { g.beginPath(); g.moveTo(CELL / 2, y); g.quadraticCurveTo(CELL / 2 + s * 14, y - 10, CELL / 2 + s * 40, y - 26); g.stroke(); } }
  }
  if (P.crumple) for (let i = 0; i < 16; i++) {   // (a poppy's crumpled silk: light and dark creases)
    g.strokeStyle = r() < .5 ? "rgba(255,200,180,.16)" : "rgba(60,0,0,.16)"; g.lineWidth = 1 + r() * 2;
    const x = r() * CELL; g.beginPath(); g.moveTo(x, CELL); g.bezierCurveTo(x + (r() - .5) * 40, CELL * .6, x + (r() - .5) * 40, CELL * .3, x + (r() - .5) * 30, 0); g.stroke();
  }
  if (P.spots) {   // (spots inside the throat: a foxglove's ringed in white, a lily's plain)
    const c = hex(P.spots);
    for (let i = 0; i < 22; i++) {
      const s = .2 + r() * .45, y = CELL - M - s * (CELL - 2 * M), x = CELL / 2 + (r() - .5) * CELL * .55 * widthAt(P.shape, s), rad = 1.5 + r() * 2.2;
      if (P.throatPale) { g.fillStyle = "rgba(255,250,255,.85)"; g.beginPath(); g.arc(x, y, rad + 1.3, 0, TAU); g.fill(); }
      g.fillStyle = css(c, .9); g.beginPath(); g.arc(x, y, rad, 0, TAU); g.fill();
    }
  }
  if (P.beard) {   // (an iris's fall: a yellow beard of hairs down its middle)
    for (let i = 0; i < 60; i++) { const y = CELL - M - r() * CELL * .45; g.fillStyle = r() < .5 ? "rgba(255,210,60,.9)" : "rgba(255,240,150,.8)"; g.fillRect(CELL / 2 + (r() - .5) * 10, y, 2, 3); }
  }
  if (P.sheen) {   // (a glossy petal: a soft highlight up its middle)
    const s = g.createRadialGradient(CELL / 2, CELL * .45, 2, CELL / 2, CELL * .45, CELL * .4);
    s.addColorStop(0, "rgba(255,255,255,.22)"); s.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = s; g.fillRect(0, 0, CELL, CELL);
  }
  for (let i = 0; i < 40; i++) {   // (mottling: no petal flat)
    g.fillStyle = r() < .5 ? "rgba(255,255,255,.05)" : "rgba(0,0,0,.05)";
    g.beginPath(); g.arc(r() * CELL, r() * CELL, 2 + r() * 6, 0, TAU); g.fill();
  }
  g.restore();
  // the edge: a little darker (or paler, `edge`), as a petal's rim catches the light
  outline(g, P.shape, rng(edge), { ragged }); g.save(); g.clip();
  g.strokeStyle = P.edge ? css(shade(base, 1 + P.edge), .6) : css(shade(base, .7), .5); g.lineWidth = 3; g.stroke();
  g.restore();
}
function paintLeaf(g, r, P) {
  if (P.shape === "pad") return paintPad(g, r, P);
  const c = hex(P.colour), edge = (r() * 1e9) | 0;
  outline(g, P.shape, rng(edge), { ragged: .02 });
  g.save(); g.clip();
  const grd = g.createLinearGradient(0, CELL, 0, 0);
  grd.addColorStop(0, css(shade(c, .72))); grd.addColorStop(.6, css(c)); grd.addColorStop(1, css(shade(c, 1.1)));
  g.fillStyle = grd; g.fillRect(0, 0, CELL, CELL);
  if (P.shape !== "needle" && P.shape !== "sword" && P.shape !== "strap") {   // (side veins, paired up the midrib)
    g.strokeStyle = css(shade(c, 1.25), .45); g.lineWidth = 1;
    for (let i = 1; i < 9; i++) { const y = CELL - M - i * CELL / 10; for (const s of [-1, 1]) { g.beginPath(); g.moveTo(CELL / 2, y); g.quadraticCurveTo(CELL / 2 + s * 16, y - 8, CELL / 2 + s * 50, y - 22); g.stroke(); } }
  } else {   // (a strap's or a sword's veins: parallel, along it)
    g.strokeStyle = css(shade(c, .8), .35); g.lineWidth = 1;
    for (let i = -3; i <= 3; i++) { g.beginPath(); g.moveTo(CELL / 2 + i * 7, CELL); g.lineTo(CELL / 2 + i * 6, 0); g.stroke(); }
  }
  g.strokeStyle = css(shade(c, 1.4), .7); g.lineWidth = P.shape === "needle" ? 1 : 2.2;   // (the midrib)
  g.beginPath(); g.moveTo(CELL / 2, CELL); g.lineTo(CELL / 2, M + 4); g.stroke();
  if (P.glossy) { const s = g.createLinearGradient(CELL * .3, 0, CELL * .6, 0); s.addColorStop(0, "rgba(255,255,255,0)"); s.addColorStop(.5, "rgba(255,255,255,.14)"); s.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = s; g.fillRect(0, 0, CELL, CELL); }
  for (let i = 0; i < 50; i++) { g.fillStyle = r() < .5 ? "rgba(255,255,230,.05)" : "rgba(0,20,0,.07)"; g.beginPath(); g.arc(r() * CELL, r() * CELL, 2 + r() * 5, 0, TAU); g.fill(); }
  if (P.spots) {   // (an aloe's pale flecks, in bands across it)
    g.fillStyle = P.spots;
    for (let i = 0; i < 60; i++) { const y = M + r() * (CELL - 2 * M), x = CELL / 2 + (r() - .5) * 40; g.beginPath(); g.ellipse(x, y, 3 + r() * 2, 1.4, 0, 0, TAU); g.fill(); }
  }
  g.restore();
  // (its rim: darker -- or its own colour, an agave's horny margin and teeth)
  outline(g, P.shape, rng(edge), { ragged: .02 }); g.save(); g.clip(); g.strokeStyle = P.edge ?? css(shade(c, .6), .5); g.lineWidth = P.edge ? 4 : 2.5; g.stroke(); g.restore();
  if (P.spine) { g.fillStyle = P.spine; g.beginPath(); g.moveTo(CELL / 2 - 3, M + 14); g.lineTo(CELL / 2, 0); g.lineTo(CELL / 2 + 3, M + 14); g.fill(); }   // (its tip a spine)
}
// a round PAD (shape "pad"): a disc filling the cell, veins raying from its middle, a slit to it (`notch`, a water
// lily's) or none (a lotus's, its middle a pale navel), waxy (`sheen`)
function paintPad(g, r, P) {
  const c = hex(P.colour), mid = CELL / 2, R = CELL / 2 - M;
  g.save(); g.beginPath();
  if (P.notch) { g.moveTo(mid, mid); g.arc(mid, mid, R, Math.PI / 2 + .12, Math.PI / 2 - .12 + TAU); g.closePath(); } else g.arc(mid, mid, R, 0, TAU);
  const grd = g.createRadialGradient(mid, mid, 4, mid, mid, R);
  grd.addColorStop(0, css(shade(c, 1.15))); grd.addColorStop(.8, css(c)); grd.addColorStop(1, css(shade(c, .7)));
  g.fillStyle = grd; g.fill(); g.clip();
  g.strokeStyle = css(shade(c, 1.3), .4); g.lineWidth = 1.2;
  for (let i = 0; i < 22; i++) { const a = i / 22 * TAU + r() * .1; g.beginPath(); g.moveTo(mid, mid); g.quadraticCurveTo(mid + Math.cos(a + .1) * R * .5, mid + Math.sin(a + .1) * R * .5, mid + Math.cos(a) * R, mid + Math.sin(a) * R); g.stroke(); }
  for (let i = 0; i < 40; i++) { g.fillStyle = r() < .5 ? "rgba(255,255,230,.06)" : "rgba(40,20,0,.08)"; g.beginPath(); g.arc(r() * CELL, r() * CELL, 3 + r() * 6, 0, TAU); g.fill(); }
  if (P.rim) { g.strokeStyle = P.rim; g.lineWidth = 4; g.beginPath(); g.arc(mid, mid, R - 1, 0, TAU); g.stroke(); }   // (a lily pad's red rim)
  if (!P.notch) { g.fillStyle = css(shade(c, 1.45), .8); g.beginPath(); g.arc(mid, mid, 6, 0, TAU); g.fill(); }
  if (P.sheen) { const s = g.createRadialGradient(mid - R * .3, mid - R * .3, 0, mid - R * .3, mid - R * .3, R * .8); s.addColorStop(0, "rgba(220,235,240,.3)"); s.addColorStop(1, "rgba(220,235,240,0)"); g.fillStyle = s; g.fillRect(0, 0, CELL, CELL); }
  g.restore();
}
function paintCentre(g, r, P) {
  const c = hex(P.colour), d = hex(P.dark), mid = CELL / 2, R = CELL / 2 - M;
  if (P.paint === "stamens") {   // (a lily's stamen: a pale filament, the anther a dark rust bar at its tip)
    g.fillStyle = "rgba(220,230,180,1)"; g.fillRect(mid - 6, M + 14, 12, CELL - 2 * M - 14);
    g.fillStyle = css(c); g.beginPath(); g.ellipse(mid, M + 14, 18, 14, 0, 0, TAU); g.fill();
    g.fillStyle = css(d, .6); g.beginPath(); g.ellipse(mid + 4, M + 16, 10, 8, 0, 0, TAU); g.fill();
    return;
  }
  const disc = g.createRadialGradient(mid, mid, 2, mid, mid, R);
  disc.addColorStop(0, css(P.paint === "seeds" ? d : shade(c, 1.1))); disc.addColorStop(.8, css(c)); disc.addColorStop(1, css(shade(c, .75)));
  g.fillStyle = disc; g.beginPath(); g.arc(mid, mid, R, 0, TAU); g.fill();
  if (P.paint === "seeds") {   // (a sunflower's seeds: two spirals of them, the golden angle)
    for (let i = 0; i < 520; i++) {
      const a = i * 2.39996, rr = Math.sqrt(i / 520) * R * .97, x = mid + Math.cos(a) * rr, y = mid + Math.sin(a) * rr;
      g.fillStyle = css(shade(i % 3 ? d : c, .8 + r() * .5)); g.beginPath(); g.ellipse(x, y, 1.9, 1.3, a, 0, TAU); g.fill();
    }
  } else if (P.paint === "florets") {   // (a daisy's disc: tiny florets, the outer ones open)
    for (let i = 0; i < 300; i++) {
      const a = i * 2.39996, rr = Math.sqrt(i / 300) * R * .95, x = mid + Math.cos(a) * rr, y = mid + Math.sin(a) * rr;
      g.fillStyle = css(shade(rr > R * .6 ? c : d, .85 + r() * .4)); g.beginPath(); g.arc(x, y, 1.6 + rr / R, 0, TAU); g.fill();
    }
  } else if (P.paint === "pod") {   // (a lotus's seed head from above: a flat green-gold top pitted with seed holes, a fringe of stamens)
    g.fillStyle = css(d); for (let i = 0; i < 200; i++) { const a = r() * TAU, rr = R * (.7 + r() * .3); g.fillRect(mid + Math.cos(a) * rr - 1, mid + Math.sin(a) * rr - 1.5, 2, 3); }
    g.fillStyle = css(c); g.beginPath(); g.arc(mid, mid, R * .68, 0, TAU); g.fill();
    for (let i = 0; i < 18; i++) { const a = i * 2.39996, rr = Math.sqrt((i + .5) / 18) * R * .58; g.fillStyle = css(shade(c, .55)); g.beginPath(); g.arc(mid + Math.cos(a) * rr, mid + Math.sin(a) * rr, 3.4, 0, TAU); g.fill(); }
  } else if (P.paint === "poppy") {   // (a poppy's seed head from above: the stigma's dark rays, black stamens round it)
    g.fillStyle = css(d); for (let i = 0; i < 160; i++) { const a = r() * TAU, rr = R * (.62 + r() * .36); g.fillRect(mid + Math.cos(a) * rr - 1.5, mid + Math.sin(a) * rr - 1.5, 3, 3); }
    g.fillStyle = css(c); g.beginPath(); g.arc(mid, mid, R * .55, 0, TAU); g.fill();
    g.strokeStyle = css(shade(d, 1.5), .9); g.lineWidth = 2;
    for (let i = 0; i < 9; i++) { const a = i / 9 * TAU; g.beginPath(); g.moveTo(mid, mid); g.lineTo(mid + Math.cos(a) * R * .5, mid + Math.sin(a) * R * .5); g.stroke(); }
  }
}
function paintStem(g, r) {
  const grd = g.createLinearGradient(0, 0, CELL, 0);
  grd.addColorStop(0, "#3c6a2a"); grd.addColorStop(.5, "#5a8a40"); grd.addColorStop(1, "#3c6a2a");
  g.fillStyle = grd; g.fillRect(0, 0, CELL, CELL);
  for (let i = 0; i < 12; i++) { g.fillStyle = r() < .5 ? "rgba(255,255,200,.08)" : "rgba(0,30,0,.1)"; g.fillRect(r() * CELL, 0, 2, CELL); }
}
function paintSpike(g, r, P, v) {   // (lavender: whorls of tiny florets up a stalk, the tip's still in bud)
  const c = hex(pick(P.colour, v)), d = hex(P.dark), mid = CELL / 2;
  g.strokeStyle = "rgba(100,130,90,1)"; g.lineWidth = 3; g.beginPath(); g.moveTo(mid, CELL); g.lineTo(mid, M); g.stroke();
  if (P.style === "hooded") {   // (an acanthus's: rows of flowers up the spike, each a white lip jutting out and down under a
    // purple hooded bract with spiny edges; smaller, closer and all bract toward the tip)
    for (let i = 0; i < 11; i++) {
      const y = CELL - M - 8 - i * 10.5, k = 1 - i * .05;
      for (const sd of [-1, 1, 0]) {
        const x = mid + sd * 13 * k + (r() - .5) * 3;
        if (i < 9) { g.fillStyle = css(shade(c, .9 + .15 * r())); g.beginPath(); g.ellipse(x + sd * 3, y + 4, 6 * k, 4 * k, sd * .5, 0, TAU); g.fill(); }
        g.fillStyle = css(shade(d, .85 + .3 * r())); g.beginPath(); g.moveTo(x - 7 * k, y + 2); g.quadraticCurveTo(x, y - 12 * k, x + 7 * k, y + 2);
        for (let q = 0; q < 4; q++) g.lineTo(x + 7 * k - q * 3.5 * k, y + (q % 2 ? -1 : 2));
        g.fill();
      }
    }
    return;
  }
  for (let i = 0; i < 9; i++) {
    const y = CELL - M - 10 - i * 12.5, w = 14 - i * .8;
    for (let k = 0; k < 9; k++) {
      const x = mid + (r() - .5) * w * 2, yy = y + (r() - .5) * 8;
      g.fillStyle = css(shade(r() < .3 ? d : c, .8 + r() * .5)); g.beginPath(); g.ellipse(x, yy, 3 + r() * 2, 2.5 + r() * 1.5, r() * 3, 0, TAU); g.fill();
    }
  }
}

// ---- THE MATERIAL ---------------------------------------------------------------------------------------------------
// the atlas's colour lit by the sun (the side seen: thin petals and leaves are drawn from both sides), its alpha
// sharpened to a pixel's edge for alpha-to-coverage (and lifted with the mip, so a far flower keeps its petals)
const flowerFrag = wgslFn(`
  fn flowerFrag(tex: vec4<f32>, n: vec3<f32>) -> vec4<f32> {
    let m = normalize(n);
    let k = ${lightWGSL("m")};
    var a = tex.a;
    a = (a - 0.5) / max(fwidth(a), 1e-4) + 0.5;
    if (a <= 0.0) { discard; }
    return vec4<f32>(tex.rgb * k, clamp(a, 0.0, 1.0));
  }
`);
let MATERIAL = null;
// THE SWAY: every point bent downwind by the square of its height on its plant (the foot still, the bloom most), on the
// grass's gusts (grass.js gustAt: the same waves roll over the meadow and the lawn) and a quick flutter of its own. The
// pool's transform is applied before this (a BatchedMesh's: three's batch node), so p is where the plant stands --
// neighbours sway nearly together, as in a field -- and the height is the geometry's own (aSway)
const flowerSway = wgslFn(`
  fn flowerSway(p: vec3<f32>, h: f32, t: f32, s: f32, dir: vec2<f32>) -> vec3<f32> {
    let g = sin((p.x * 0.31 + p.z * 0.95) * 0.35 - t * 1.35) + 0.5 * sin((p.x * -0.8 + p.z * 0.6) * 0.17 - t * 0.85)
          + 0.35 * sin((p.x * 0.62 - p.z * 0.78) * 0.9 - t * 2.4);
    let flutter = 0.22 * sin(t * 4.3 + p.x * 3.1 + p.z * 2.3);
    let k = h * h * s * 0.1 * (0.55 + 0.35 * g + flutter);
    return p + vec3<f32>(dir.x * k, -0.4 * k * k / max(h, 0.05), dir.y * k);
  }
`);
let TEX = null;   // (the material's atlas node: a new atlas is swapped into it)
export function flowerMaterial() {
  if (MATERIAL) return MATERIAL;
  const m = new THREE.MeshBasicNodeMaterial({ alphaToCoverage: true, side: THREE.DoubleSide });
  TEX = texture(atlas().tex, uv());
  const t = uniform(0).setGroup(renderGroup).onRenderUpdate(() => FOLIAGE_T.value);
  m.positionNode = flowerSway({ p: positionLocal, h: attribute("aSway", "float"), t, s: WIND.strength, dir: uniform(WIND_DIR.clone()) });
  const out = flowerFrag({ tex: TEX, n: normalWorld.mul(faceDirection) });
  m.colorNode = out.xyz; m.opacityNode = out.w;
  return MATERIAL = m;
}
// the atlas's canvas (the lab shows it)
export const flowerAtlas = () => atlas();
