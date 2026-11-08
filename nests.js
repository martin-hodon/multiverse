// NESTS (2026-11-08): the nests of the birds that build them, out of sticks, reeds and grass, where those birds live --
//   a STICK NEST in a tree's crown, in the fork where a bough leaves the trunk: the crows', the ravens', the buzzard's,
//     and the HERONRY, a few big ones in the tall trees near the water;
//   the MAGPIE's: a stick nest roofed over with a dome of thorny sticks, a way in at the side;
//   the EAGLE's EYRIE: a wide flat platform of thick sticks, built on year after year, a lining of green sprigs, in
//     the tallest tree (the cliffs' ledges are bare stone in this world's terrain: a big tree, then);
//   on the ground by the water: the DUCK's and the GOOSE's, a ring of dry grass and stems lined with grey down, and the
//     SWAN's, a mound of reeds a metre across with a cup in its top;
//   some with EGGS in them (each kind's own size and colour), and here and there the bird itself on the nest or by it.
// The storks' nests are on the town's chimneys (index.html storkNests), the swallows' under the eaves (icicles.js).
//
// A nest is made of sticks: each stick a `log` of blocks.js (an eight-sided round, its ends cut), laid in COURSES round
// the rim (each course turned half a stick from the last, so they cross as woven), a floor of short sticks across the
// bowl, a lining; a mound or a dome adds its own. One mesh for all the nests up in the trees, one a nest on the ground
// (in its own frame, its base at the ground: the grass mask's occluder keeps the grass out of it); lit, snowed on
// (windowframes.js snowyLit). What each kind is lives in its asset: assets/nature/nests/*.json -- its size, its sticks,
// its eggs, which species build it (`species`) and where (`where`: crown, tall, water).
//
//   const B = nestBlocks(spec, seed)        // one nest in its own frame (y 0 its foot) -> { blocks, top, cup }
//   const m = nestMesh(list, material)      // [{ spec, at: [x, y, z], yaw, seed }] -> one mesh (world)
import * as THREE from "three";
import { rng } from "./flora.js";
import { blockMesh } from "./blocks.js";

const TWIG = [[.42, .35, .26], [.36, .3, .22], [.48, .41, .31], [.3, .25, .19]];
const pickC = (r, cs) => cs[Math.floor(r() * cs.length)];

// ONE NEST in its own frame, its foot at y 0, its middle at x = z = 0. -> { blocks, top (the rim's height), cup (the
// bowl's floor: where eggs lie and a bird sits) }
export function nestBlocks(spec, seed = 1) {
  const r = rng(seed * 97 + 13), R = spec.r ?? .3, t = spec.stick ?? .03, L = spec.length ?? [R * 1.2, R * 1.8];
  const twig = spec.twig ?? TWIG, B = [];
  const log = (at, len, th, yaw, tilt, colour) => B.push({ at, size: [len, th, th], yaw, tilt, shape: "log", colour, ends: colour.map((v) => Math.min(1, v * 1.35)) });
  const kind = spec.kind ?? "platform";
  let base = 0;
  // a MOUND under it (the swan's): reeds in layers, each ring smaller, a stepped core of flat reed under them so
  // nothing shows through
  if (kind === "mound") {
    const Hm = spec.h ?? .3, NL = 6;
    for (let l = 0; l < NL; l++) {
      const u = l / NL, rho = R * (1 - .55 * u ** 1.5), y = u * Hm + t / 2;
      B.push({ at: [0, y, 0], size: [rho * 1.5, Hm / NL * 1.1, rho * 1.5], yaw: r() * 3, colour: [.36, .32, .21] });
      const n = Math.round(2 * Math.PI * rho / (t * 2.1));
      for (let i = 0; i < n; i++) {
        const a = (i + r() * .6 + l * .5) / n * Math.PI * 2, rr = rho * (.86 + .14 * r());
        log([Math.cos(a) * rr, y + t * .3, Math.sin(a) * rr], (L[0] + r() * (L[1] - L[0])) * (1 - .3 * u), t, -a + Math.PI / 2 + (r() - .5) * 1.1, (r() - .5) * .5, pickC(r, twig));
      }
    }
    base = Hm;
  }
  // THE RIM: courses of sticks round it, each crossing the last
  const courses = spec.courses ?? 3, sticks = spec.sticks ?? 14, rim = kind === "mound" ? R * .45 : R, rise = spec.rise ?? 1.2;
  for (let q = 0; q < courses; q++) for (let i = 0; i < sticks; i++) {
    const a = (i + q * .5) / sticks * Math.PI * 2 + (r() - .5) * .25, rr = rim * (.78 + .18 * r() + q * .04);
    log([Math.cos(a) * rr, base + t * (.5 + q * rise), Math.sin(a) * rr], (L[0] + r() * (L[1] - L[0])) * (kind === "mound" ? .7 : 1), t * (.8 + .4 * r()),
        -a + Math.PI / 2 + (r() - .5) * .6, (r() - .5) * .35, pickC(r, twig));
  }
  const top = base + t * (1 + (courses - 1) * rise);
  // THE FLOOR: short sticks across the bowl, darker; a CUP a little down in it
  const cup = base + t * .9;
  const nf = spec.floor ?? 12;
  for (let i = 0; i < nf; i++) {
    const a = r() * Math.PI, d = (r() - .5) * rim * .9;
    log([Math.cos(a + 1.57) * d, base + t * .5, Math.sin(a + 1.57) * d], rim * (1.3 + .4 * r()), t * .9, -a, (r() - .5) * .1, spec.floorColour ?? [.27, .22, .17]);
  }
  // THE LINING: the eyrie's green sprigs, a crow's wool and moss, the ducks' and geese's DOWN (soft balls round the cup)
  const lin = spec.lining;
  if (lin) {
    const n = lin.n ?? 12;
    for (let i = 0; i < n; i++) {
      const a = i / n * Math.PI * 2 + r() * .4, rr = rim * (lin.at ?? .6) * (.8 + .3 * r());
      if (lin.down) B.push({ at: [Math.cos(a) * rr, cup + lin.size * .35, Math.sin(a) * rr], size: [lin.size * (.8 + .4 * r()), 0, 0], shape: "ball", colour: lin.colour });
      else B.push({ at: [Math.cos(a) * rr, cup + t * .3, Math.sin(a) * rr], size: [lin.size * (.7 + .6 * r()), t * .5, lin.size * .45], yaw: r() * 6.28, colour: lin.colour });
    }
  }
  // THE DOME (the magpie's): sticks laid over a half-sphere above the bowl, a gap to one side -- the way in
  if (kind === "dome") {
    const n = spec.dome ?? 26, gap = .9;
    for (let i = 0; i < n; i++) {
      const ph = gap / 2 + (i + r() * .7) / n * (Math.PI * 2 - gap), e = .25 + 1.2 * ((i * .618) % 1), DR = rim * 1.02;
      log([Math.cos(ph) * Math.cos(e) * DR, top + Math.sin(e) * DR * .9, Math.sin(ph) * Math.cos(e) * DR], (L[0] + r() * (L[1] - L[0])) * .9, t * .8,
          -ph + Math.PI / 2 + (r() - .5) * .9, (r() - .5) * 1.1, pickC(r, twig));
    }
  }
  // THE EGGS: in the bowl, together
  const eg = spec.eggs;
  if (eg && (eg.n?.[1] ?? 0) > 0) {
    const n = eg.n[0] + Math.floor(r() * (eg.n[1] - eg.n[0] + 1)), d = eg.d ?? .05;
    for (let i = 0; i < n; i++) {
      const a = i / n * Math.PI * 2 + r() * .3, rr = n > 1 ? d * .62 * (n > 4 && i % 2 ? 1.6 : 1) : 0;
      B.push({ at: [Math.cos(a) * rr, cup + d * .42, Math.sin(a) * rr], size: [d, 0, 0], shape: "ball", colour: eg.colour ?? [.9, .88, .8] });
    }
  }
  return { blocks: B, top, cup };
}

// several nests, each placed, turned and in its own colours -> one mesh, world coordinates (in the frame given: `at`
// subtracted by `origin` if any, for a ground nest's own frame)
export function nestMesh(list, material, origin = [0, 0, 0]) {
  const all = [];
  for (const { spec, at, yaw = 0, seed = 1 } of list) {
    const { blocks } = nestBlocks(spec, seed), c = Math.cos(yaw), s = Math.sin(yaw);
    for (const b of blocks) {
      const [x, y, z] = b.at;
      all.push({ ...b, at: [at[0] - origin[0] + x * c + z * s, at[1] - origin[1] + y, at[2] - origin[2] - x * s + z * c], yaw: (b.yaw ?? 0) + yaw });
    }
  }
  return blockMesh(all, "nests", material);
}

// WHERE IN A TREE: the fork where its highest bough under `frac` of its height leaves the trunk (the nest a little out
// along the bough, sat on it) -> [x, y, z] or null. (`trunk`, `boughs`: index.html treeCol's, world)
export function crownFork(tree, frac = .8, ground = 0) {
  const top = ground + tree.h * frac, bs = (tree.boughs ?? []).filter((b) => b.a && b.a[1] < top && b.a[1] > ground + tree.h * .35);
  if (!bs.length) return null;
  const b = bs.reduce((p, q) => (q.a[1] > p.a[1] ? q : p));
  const k = .12;
  return [b.a[0] + (b.b[0] - b.a[0]) * k, b.a[1] + (b.b[1] - b.a[1]) * k + (b.r0 ?? .05) * .6, b.a[2] + (b.b[2] - b.a[2]) * k];
}
