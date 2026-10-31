// THE LANDSCAPE ENGINE's stages (docs/landscape.md) -- the frame: the spec read, the scene's axes, the stack of beds.
// Each stage takes the scene so far, `c`, and adds what it makes to it; landscape.js runs them in order.
import { rng } from "./core.js";
import { GEOLOGY, CLIMATES, climateOf, makeStrata, DEFAULT_FEATURES } from "./presets.js";

export function frame(c) {
  const { spec } = c;
  // (the stages' loops are each wrapped in a function of their own, `(() => { ... })()`: this function is too big for
  // the JIT to optimise as a whole, and a loop run in it unoptimised is several times slower)
  const T = { t0: performance.now(), stages: [] };
  const mark = (name) => { const t = performance.now(); T.stages.push([name, Math.round(t - (T.last ?? T.t0))]); T.last = t; };
  const seed = spec.seed ?? 1, size = spec.size ?? 320, dx = spec.dx ?? 1, N = Math.round(size / dx) + 1;
  const geo0 = typeof spec.geology === "object" ? spec.geology : GEOLOGY[spec.geology ?? "canyon"];
  const relief = spec.relief ?? 1;
  const geo = { ...geo0, beds: geo0.beds.map(([r, t]) => [r, t === undefined ? undefined : t * relief]) };
  const clim = climateOf(typeof spec.climate === "object" ? spec.climate : CLIMATES[spec.climate ?? "temperate"]);
  const F = { ...DEFAULT_FEATURES, ...(spec.features ?? {}) };
  const R = rng(seed * 9301 + 49297);
  const notes = [];   // what was made and why (the lab lists them)

  // the frame: the land falls along u (the flow), v across it; the scene's middle at the origin
  const theta = (spec.flow ?? R() * 360) * Math.PI / 180, cu = Math.cos(theta), su = Math.sin(theta);
  const half = size / 2;
  const toUV = (x, y) => [(x - half) * cu + (y - half) * su, -(x - half) * su + (y - half) * cu];
  const toXY = (u, v) => [half + u * cu - v * su, half + u * su + v * cu];
  Object.assign(c, { T, mark, seed, size, dx, N, geo0, relief, geo, clim, F, R, notes, theta, cu, su, half, toUV, toXY });
}

export function strata(c) {
  const { clim, dx, geo, N, notes, seed, toUV } = c;
  // GEOLOGY: the stack's top is the upland's surface
  const TOP = 40;
  const S = makeStrata(geo, TOP, seed);
  const capK = S.beds.findIndex((b) => b.hard >= .5);                     // the first hard bed: the cap
  const softK = S.beds.findIndex((b, k) => k > capK && b.hard < .5);      // the soft bed under it
  const benchK = S.beds.findIndex((b, k) => k > softK && b.hard >= .5);   // the next hard bed: the bench
  const soft2K = benchK >= 0 ? S.beds.findIndex((b, k) => k > benchK && b.hard < .5) : -1;   // and under it a soft one,
  const bench2K = soft2K >= 0 ? S.beds.findIndex((b, k) => k > soft2K && b.hard >= .5) : -1;   // and a hard one: a second step
  const capT = S.beds[capK].t, depthTo = (k) => S.base[k] ?? 0;
  notes.push(`geology: ${geo.name}; climate: ${clim.name} (rain ${clim.rain} mm, ${clim.temp} C: ${clim.flows ? "streams run all year" : "streams run after storms"}, ${clim.plants})`);

  const n = N * N, H = new Float32Array(n), soil = new Float32Array(n), carved = new Uint8Array(n), bar = new Uint8Array(n);   // (bar: a point bar's sand)   // carved: the stream's bed (what lands in it is carried away)
  const U = new Float32Array(n), V = new Float32Array(n);
  (() => {
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) { const [u, v] = toUV(i * dx, j * dx); U[j * N + i] = u; V[j * N + i] = v; }
  })();
  Object.assign(c, { TOP, S, capK, softK, benchK, soft2K, bench2K, capT, depthTo, n, H, soil, carved, bar, U, V });
}
