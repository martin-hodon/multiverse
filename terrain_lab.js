// THE TERRAIN LAB'S ENGINE (docs/terrain_lab.md): the region's columns on the GPU, one step of geological time as a
// sequence of compute passes, and the view's upscaled mesh. The page (terrain_lab.html) drives it.
import { SIM, UP, DRAW, PARAM_INDEX, SCALARS, MATS, MAX_PLATES, MAX_HOT, MAX_OUT, MAX_IN, VIEW_FLOATS } from "./terrain_lab_wgsl.js";

export { MATS };
export const LAYERS = 8;

// ---- the presets: how each kind of land starts, and what drives it -------------------------------------------------
// relief(x, y) in [0, 1]^2 -> metres over `base`; strata bottom -> top [material, metres]; plates [x, y, vx, vy] in
// fractions of the domain and mm/yr; hotspots [x, y, rate m3/yr, radius m]; outlets [x, y, half-width m] on the edge (the
// only base level; none: all the edge is); inlets [x, y, Q m3/yr, Qs m3/yr] on the edge (a river from beyond: it needs
// outlets, else it leaves by the nearest edge); params: overrides of DEFAULTS
export const DEFAULTS = {
  dx: 100, dt: 500, rain: 1.0, sea: 0, K: 2e-5, V: 1.0, kappa: 3, weather: 1e-4, eps: 2e-3, slide: 0.5, lith: 50,
  carb: 3e-4, carbMud: 2000, upliftBg: 0, plateK: 0.12, plateW: 4000, riftBasalt: 0.02, lavaYield: 0.05, lavaCool: 0.3,
  rockVar: 0.3, lakeMin: 0.5, soilH: 0.5, seed: 1, Qc: 5e5, upNoise: 0.4, orog: 0.5, drift: 0,
  waves: 0.02, waveBase: 15, shelfSlope: 0.01, fallS: 0.2, plunge: 1.0,
};
const MM = 1e-3;   // mm/yr -> m/yr
export const PRESETS = {
  plains: { name: "Plains", base: 60, relief: (x, y, n) => 25 * n(x * 3, y * 3) + 15 * n(x * 9, y * 9) - 20 * y,
            strata: [[2, 120], [3, 80], [4, 15]], params: { rain: 1.1, upliftBg: -0.05 * MM } },
  mountains: { name: "Mountain belt", base: 150, relief: (x, y, n) => 40 * n(x * 4, y * 4) + 25 * n(x * 11, y * 11),
               strata: [[2, 350], [3, 220], [2, 120]], plates: [[0.5, 0.2, 0, 12], [0.5, 0.8, 0, -12]], params: { rain: 1.3 } },
  // (the rift's floor falls along its axis to one end, where it drains out: an open rift, lakes where it sinks fastest)
  rift: { name: "Rift valley", base: 700, relief: (x, y, n) => 40 * n(x * 4, y * 4) + 260 * y,
          strata: [[2, 250], [3, 100]], plates: [[0.18, 0.5, -8, 0], [0.82, 0.5, 8, 0]], params: { rain: 0.9, riftBasalt: 0.012 } },
  // a layer cake under lava flows that filled the old valleys (a patchy basalt cap), tilted gently, raised slowly: the rivers
  // cut down through it from the edges, and where the basalt is, it holds the ground up
  // (its rivers are older than the uplift: shallow winding valleys along the zero lines of a noise, which the rivers
  //  keep and cut down as the plateau rises -- antecedent drainage, the Colorado's; and it drains out by two rivers on its
  //  low sides, not over all its edge -- the canyons grow back from them, branching)
  mesas: { name: "Mesas and canyons", base: 520, relief: (x, y, n) => 14 * n(x * 5, y * 5) + 130 * (0.8 * x + 0.6 * y) - 45 * Math.pow(Math.max(0, 1 - 4 * Math.abs(n(x * 2.3 + 11, y * 2.3 + 3))), 2),
           strata: (x, y, n) => [[2, 260], [3, 110], [2, 170], [3, 60], ...(n(x * 4.3 + 5, y * 4.3) > 0.12 ? [[1, 45]] : [[2, 45]])],
           outlets: [[0, 0.22, 250], [0.58, 0, 250]], params: { rain: 0.9, upliftBg: 0.8 * MM, K: 1e-4, Qc: 3e5 } },
  island: { name: "Volcanic island", base: -260, relief: (x, y, n) => 40 * n(x * 3, y * 3),
            strata: [[3, 60], [4, 20]], hot: [[0.5, 0.5, 2e5, 1800]], params: { rain: 1.6, sea: 0, lavaYield: 0.06 } },
  valleys: { name: "River valleys", base: 250, relief: (x, y, n) => 180 * n(x * 2.2, y * 2.2) + 70 * n(x * 6, y * 6) + 60 * (1 - Math.abs(2 * x - 1)),
             strata: [[2, 220], [3, 120], [4, 2]], params: { rain: 1.6 } },
  // A PIECE OF A LARGER LAND at 20 m cells (2.6 km): a big river (10 m3/s, a few hundred km2 upstream) comes in from the
  // west and leaves east along a winding valley between hills, cutting down as the land rises; a basalt sill 30 m down
  // (a hard band over soft sandstone) is where its falls and rapids are, and side streams hang over its valley. The
  // game's maps are cut from this (mapgen.js).
  river: { name: "River country", base: 150,
           relief: (x, y, n) => 40 * n(x * 3, y * 3) + 14 * n(x * 8, y * 8) + 25 * (1 - x)
                               - 30 * Math.exp(-(((y - 0.5 - 0.14 * n(x * 2.2 + 7, 3.1) * Math.sin(Math.PI * x)) / 0.09) ** 2)),
           strata: (x, y, n) => [[2, 150], [1, n(x * 5 + 3, y * 5) > -0.3 ? 10 : 4], [2, 30], [4, 3]],
           outlets: [[1, 0.5, 300]], inlets: [[0, 0.5, 3e8, 0]],
           params: { dx: 20, dt: 100, rain: 0.9, upliftBg: 0.4 * MM, Qc: 2e5, kappa: 1, lakeMin: 0.3 } },
};

// noise for the presets' starting relief and beds (CPU; once): gradient noise in about [-1, 1] on a lattice turned off
// the grid's axes, as the shaders' gnoise (value noise's contours ran along the grid: straight cap edges and valleys)
export function noise2(seed) {
  const h = (i, j) => { let n = (i * 374761393 + j * 668265263 + seed * 2147483647) | 0; n = (n ^ (n >>> 13)) * 1274126177 | 0; return ((n ^ (n >>> 16)) >>> 0) / 4294967295; };
  const g = (i, j, x, y) => { const a = 2 * Math.PI * h(i, j); return Math.cos(a) * x + Math.sin(a) * y; };
  const s = (t) => t * t * t * (t * (t * 6 - 15) + 10);
  return (x0, y0) => {
    const x = 0.8 * x0 - 0.6 * y0, y = 0.6 * x0 + 0.8 * y0;
    const i = Math.floor(x), j = Math.floor(y), fx = x - i, fy = y - j, u = s(fx), v = s(fy);
    const a = g(i, j, fx, fy), b = g(i + 1, j, fx - 1, fy), c = g(i, j + 1, fx, fy - 1), d = g(i + 1, j + 1, fx - 1, fy - 1);
    return Math.max(-1, Math.min(1, 2 * ((a + (b - a) * u) * (1 - v) + (c + (d - c) * u) * v)));
  };
}

// ---- small matrix helpers for the camera --------------------------------------------------------------------------
export function perspective(fovy, aspect, near, far) {
  const f = 1 / Math.tan(fovy / 2), nf = 1 / (near - far);
  return [f / aspect, 0, 0, 0, 0, f, 0, 0, 0, 0, far * nf, -1, 0, 0, far * near * nf, 0];   // (WebGPU: z 0..1)
}
export function lookAt(e, t, u = [0, 1, 0]) {
  const z = norm(sub(e, t)), x = norm(cross(u, z)), y = cross(z, x);
  return [x[0], y[0], z[0], 0, x[1], y[1], z[1], 0, x[2], y[2], z[2], 0, -dot(x, e), -dot(y, e), -dot(z, e), 1];
}
export function mul(a, b) {
  const o = new Array(16).fill(0);
  for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) for (let k = 0; k < 4; k++) o[j * 4 + i] += a[k * 4 + i] * b[j * 4 + k];
  return o;
}
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a) => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };

// ---- the lab ------------------------------------------------------------------------------------------------------
// canvas: where the view draws (null: no view -- the game grows its maps with it, mapgen.js); device: a GPU device to
// share (the game's renderer's), else the lab asks for its own
export async function createLab(canvas, { N = 256, device: shared = null } = {}) {
  let device = shared;
  if (!device) {
    const adapter = await navigator.gpu?.requestAdapter();
    if (!adapter) throw new Error("no WebGPU adapter");
    device = await adapter.requestDevice();
  }
  const format = navigator.gpu.getPreferredCanvasFormat(), ctx = canvas?.getContext("webgpu");
  ctx?.configure({ device, format, alphaMode: "opaque" });
  const lab = { device, N, M: 2 * N, params: { ...DEFAULTS }, plates: [], hot: [], outlets: [], inlets: [], steps: 0, years: 0, cur: 0, acur: 0,
                view: { mode: 0, exag: 2, detail: 1, riverQ: 7.3, section: 0.5, contour: 0, rel: true, hLo: 0, hHi: 1000 } };

  // ---- the state
  const S = (bytes) => device.createBuffer({ size: bytes, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST | GPUBufferUsage.COPY_SRC });
  let col, lay, flow, aux, wb, acc, out8, disp, simBG, upBG, drawBG, index, nIndex = 0;
  const pbuf = device.createBuffer({ size: PARAM_INDEX.__size * 4, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
  const pdata = new ArrayBuffer(PARAM_INDEX.__size * 4), pf = new Float32Array(pdata), pu = new Uint32Array(pdata);
  // the iteration state (which ping-pong half is current, whether the fill starts over): 8 entries, a dynamic offset each
  const IT = 256, itbuf = device.createBuffer({ size: IT * 8, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
  { const d = new Uint32Array(IT / 4 * 8); for (let e = 0; e < 8; e++) d.set([e & 1, (e >> 2) & 1, (e >> 1) & 1, 0], e * IT / 4); device.queue.writeBuffer(itbuf, 0, d); }
  const itOff = (cur, a, reset = 0) => ((reset << 2) | (a << 1) | cur) * IT;
  const vbuf = device.createBuffer({ size: VIEW_FLOATS * 4, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });

  // ---- the pipelines
  const simLayout = device.createBindGroupLayout({ entries: [
    { binding: 0, visibility: GPUShaderStage.COMPUTE, buffer: { type: "uniform" } },
    ...[1, 2, 3, 4, 5, 6, 7].map((b) => ({ binding: b, visibility: GPUShaderStage.COMPUTE, buffer: { type: "storage" } })),
    { binding: 8, visibility: GPUShaderStage.COMPUTE, buffer: { type: "uniform", hasDynamicOffset: true, minBindingSize: 16 } }] });
  const simModule = device.createShaderModule({ code: SIM });
  const K = {};
  for (const e of ["tect", "lavaA", "lavaB", "lavaCool", "slideA", "coastA", "moves", "weather", "fillInit", "fillIter", "route", "accum", "cutA", "erode", "dry", "walls", "paint"])
    K[e] = device.createComputePipeline({ layout: device.createPipelineLayout({ bindGroupLayouts: [simLayout] }), compute: { module: simModule, entryPoint: e } });
  const upLayout = device.createBindGroupLayout({ entries: [
    { binding: 0, visibility: GPUShaderStage.COMPUTE, buffer: { type: "uniform" } },
    ...[1, 2, 3, 4].map((b) => ({ binding: b, visibility: GPUShaderStage.COMPUTE, buffer: { type: "read-only-storage" } })),
    { binding: 5, visibility: GPUShaderStage.COMPUTE, buffer: { type: "storage" } },
    { binding: 6, visibility: GPUShaderStage.COMPUTE, buffer: { type: "uniform" } }] });
  const upPipe = device.createComputePipeline({ layout: device.createPipelineLayout({ bindGroupLayouts: [upLayout] }),
                                                compute: { module: device.createShaderModule({ code: UP }), entryPoint: "up" } });
  const drawLayout = device.createBindGroupLayout({ entries: [
    { binding: 0, visibility: GPUShaderStage.VERTEX | GPUShaderStage.FRAGMENT, buffer: { type: "uniform" } },
    { binding: 1, visibility: GPUShaderStage.VERTEX, buffer: { type: "read-only-storage" } }] });
  const drawModule = device.createShaderModule({ code: DRAW });
  const drawPipe = device.createRenderPipeline({
    layout: device.createPipelineLayout({ bindGroupLayouts: [drawLayout] }),
    vertex: { module: drawModule, entryPoint: "vs" },
    fragment: { module: drawModule, entryPoint: "fs", targets: [{ format }] },
    primitive: { topology: "triangle-list", cullMode: "none" },
    depthStencil: { format: "depth24plus", depthWriteEnabled: true, depthCompare: "less" } });
  let depthTex = null;

  // ---- (re)making the grid: the buffers and what binds them
  function alloc(n) {
    for (const b of [col, lay, flow, aux, wb, acc, out8]) b?.destroy();
    lab.N = N = n; lab.M = Math.min(1024, 2 * n);
    const C = N * N;
    col = S(C * 16); lay = S(C * LAYERS * 8); flow = S(C * 16); aux = S(C * 16); wb = S(C * 8); acc = S(C * 16); out8 = S(C * 32);
    simBG = device.createBindGroup({ layout: simLayout, entries: [pbuf, col, lay, flow, aux, wb, acc, out8].map((buffer, binding) => ({ binding, resource: { buffer } }))
      .concat([{ binding: 8, resource: { buffer: itbuf, size: 16 } }]) });
    mesh(lab.M);
  }
  // the view's mesh: M x M vertices (the grid upscaled), its buffer and its triangles
  function mesh(M) {
    disp?.destroy(); index?.destroy();
    lab.M = M;
    disp = S(M * M * 16);
    upBG = device.createBindGroup({ layout: upLayout, entries: [pbuf, col, lay, wb, acc, disp, vbuf].map((buffer, binding) => ({ binding, resource: { buffer } })) });
    drawBG = device.createBindGroup({ layout: drawLayout, entries: [vbuf, disp].map((buffer, binding) => ({ binding, resource: { buffer } })) });
    const idx = new Uint32Array((M - 1) * (M - 1) * 6);
    let o = 0;
    for (let j = 0; j < M - 1; j++) for (let i = 0; i < M - 1; i++) {
      const a = j * M + i, b = a + 1, c = a + M, d = c + 1;
      idx[o++] = a; idx[o++] = c; idx[o++] = b; idx[o++] = b; idx[o++] = c; idx[o++] = d;
    }
    index = device.createBuffer({ size: idx.byteLength, usage: GPUBufferUsage.INDEX | GPUBufferUsage.COPY_DST });
    device.queue.writeBuffer(index, 0, idx); nIndex = idx.length;
  }

  // ---- the parameters into the uniform (from the one field list)
  function upload() {
    const P = lab.params;
    for (const [name, t] of SCALARS) {
      const v = name === "N" ? N : name === "L" ? LAYERS : name === "nPlates" ? Math.min(lab.plates.length, MAX_PLATES)
              : name === "nHot" ? Math.min(lab.hot.length, MAX_HOT) : name === "nOut" ? Math.min(lab.outlets.length, MAX_OUT)
              : name === "nIn" ? Math.min(lab.inlets.length, MAX_IN)
              : name === "time" ? lab.years : P[name] ?? 0;
      if (t === "u") pu[PARAM_INDEX[name]] = v; else pf[PARAM_INDEX[name]] = v;
    }
    pf.set(lab.brush ?? [0, 0, 1, 0], PARAM_INDEX.brush);
    MATS.forEach((m, i) => pf.set([m.erod, m.weather, Math.tan(m.angle * Math.PI / 180), m.dissolve], PARAM_INDEX.mat + 4 * i));
    lab.plates.slice(0, MAX_PLATES).forEach((q, i) => pf.set(q, PARAM_INDEX.plates + 4 * i));
    lab.hot.slice(0, MAX_HOT).forEach((q, i) => pf.set(q, PARAM_INDEX.hot + 4 * i));
    lab.outlets.slice(0, MAX_OUT).forEach((q, i) => pf.set(q, PARAM_INDEX.outl + 4 * i));
    lab.inlets.slice(0, MAX_IN).forEach((q, i) => pf.set(q, PARAM_INDEX.inl + 4 * i));
    device.queue.writeBuffer(pbuf, 0, pdata);
  }

  // ---- a preset: the columns built on the CPU, once
  lab.reset = (key, { n = N, seed = lab.params.seed } = {}) => {
    const pr = PRESETS[key] ?? PRESETS.plains;
    if (n !== N || !col) alloc(n);
    lab.preset = key;
    lab.params = { ...DEFAULTS, ...pr.params, seed };
    const L = N * lab.params.dx;
    lab.plates = (pr.plates ?? []).map(([x, y, vx, vy]) => [x * L, y * L, vx * MM, vy * MM]);
    lab.hot = (pr.hot ?? []).map(([x, y, r, rad]) => [x * L, y * L, r, rad]);
    lab.outlets = (pr.outlets ?? []).map(([x, y, w]) => [x * (N - 1) * lab.params.dx, y * (N - 1) * lab.params.dx, w, 0]);
    lab.inlets = (pr.inlets ?? []).map(([x, y, q, qs]) => [x * (N - 1) * lab.params.dx, y * (N - 1) * lab.params.dx, q, qs ?? 0]);
    lab.steps = 0; lab.years = 0; lab.cur = 0; lab.acur = 0;
    lab.view.riverQ = Math.log10(Math.max(lab.params.rain * L * L * 0.015, 3e6));   // (a river: a fiftieth of the region's water or more, and 0.1 m3/s)
    const nz = noise2(seed * 7919 + 13), C = N * N;
    const colD = new Float32Array(C * 4), layD = new Float32Array(C * LAYERS * 2);
    // FLAT-LYING STRATA on a flat basement, cut by the starting relief: a hill shows the higher beds, a hollow the lower;
    // the uppermost ROCK bed reaches up to the surface wherever the surface stands above the pile. A loose bed on top
    // (sediment) is not a bed but a COVER: it drapes the surface at its own thickness, hills and all
    const strataAt = typeof pr.strata === "function" ? pr.strata : () => pr.strata;   // (the beds may vary over the region)
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      const c = j * N + i, x = i / (N - 1), y = j / (N - 1);
      const top = pr.base + pr.relief(x, y, nz), all = strataAt(x, y, nz);
      const cover = all.length > 1 && all[all.length - 1][0] === 4 ? all[all.length - 1][1] : 0;
      const beds = cover ? all.slice(0, -1) : all;
      const rockTop = top - cover, datum = pr.base - cover - beds.reduce((q, [, t]) => q + t, 0);
      let z = datum, k = 0;
      colD[c * 4] = Math.min(datum, rockTop);
      beds.forEach(([m, t], b) => {
        const th = Math.max(0, Math.min(b === beds.length - 1 ? Infinity : t, rockTop - z));
        if (th > 0 && k < LAYERS) { layD[(c * LAYERS + k) * 2] = th; layD[(c * LAYERS + k) * 2 + 1] = m; k++; }
        z += t;
      });
      if (cover > 0 && k < LAYERS) { layD[(c * LAYERS + k) * 2] = cover; layD[(c * LAYERS + k) * 2 + 1] = 4; k++; }
      colD[c * 4 + 1] = k; colD[c * 4 + 2] = top; colD[c * 4 + 3] = 0;
    }
    device.queue.writeBuffer(col, 0, colD); device.queue.writeBuffer(lay, 0, layD);
    for (const b of [flow, aux, acc, out8]) device.queue.writeBuffer(b, 0, new Float32Array(b.size / 4));
    device.queue.writeBuffer(wb, 0, new Float32Array(C * 2));
    upload();
    const enc = device.createCommandEncoder(), pass = enc.beginComputePass();
    if (lab.outlets.length) run(pass, "walls");
    refill(pass, true);
    pass.end(); device.queue.submit([enc.finish()]);
  };

  const WG = () => Math.ceil(N / 8);
  const run = (pass, k, off = itOff(lab.cur, lab.acur)) => { pass.setPipeline(K[k]); pass.setBindGroup(0, simBG, [off]); pass.dispatchWorkgroups(WG(), WG()); };
  // the water surface: a full fill from above (reset), or warm from the last one; `iters` Jacobi sweeps
  function refill(pass, reset, iters = reset ? (lab.outlets.length ? 4 : 2) * N + 16 : 12) {
    run(pass, "fillInit", itOff(lab.cur, lab.acur, reset ? 1 : 0));
    for (let k = 0; k < iters; k++) { run(pass, "fillIter"); lab.cur ^= 1; }
  }
  // ONE STEP of dt years
  const dry = (pass) => { run(pass, "dry"); lab.cur ^= 1; };   // (dry land follows its ground: read one half, write the other)
  const STAGES = [
    ["tect", (pass) => run(pass, "tect")],
    // (lava only comes from hotspots and plates pulling apart: without either -- and after what was flowing has set, 200
    //  steps on -- its 25 passes a step are skipped)
    ["lava", (pass) => {
      if (lab.hot.length || lab.plates.length) lab.lavaUntil = lab.steps + 200;
      if (!(lab.steps < (lab.lavaUntil ?? 0))) return;
      for (let k = 0; k < 12; k++) { run(pass, "lavaA"); run(pass, "lavaB"); } run(pass, "lavaCool");
    }],
    ["slides", (pass) => { run(pass, "slideA"); run(pass, "moves"); dry(pass); }],
    ["coast", (pass) => { run(pass, "coastA"); run(pass, "moves"); dry(pass); }],
    ["weather", (pass) => run(pass, "weather")],
    // (a full fill from above now and then: new hollows -- a valley the uplift dams, a sinking basin -- fill)
    ["fill", (pass) => { refill(pass, lab.steps % 16 === 15 || lab.fullFill); lab.fullFill = false; }],
    ["route", (pass) => run(pass, "route")],
    ["accum", (pass) => { for (let k = 0; k < 10; k++) { run(pass, "accum"); lab.acur ^= 1; } }],
    ["erode", (pass) => { run(pass, "cutA"); run(pass, "erode"); dry(pass); }],
    ["walls", (pass) => { if (lab.outlets.length) run(pass, "walls"); }],
  ];
  function step(pass) {
    for (const [name, stage] of STAGES) { stage(pass); if (lab.stopAfter === name) return; }   // (stopAfter: a debugging cut)
    lab.steps++; lab.years += lab.params.dt;
  }
  // (debugging: keep the whole state and go back to it)
  lab.saveState = () => {
    const enc = device.createCommandEncoder();
    lab.saved = [col, lay, flow, aux, wb, acc, out8].map((b) => { const c = device.createBuffer({ size: b.size, usage: GPUBufferUsage.COPY_SRC | GPUBufferUsage.COPY_DST }); enc.copyBufferToBuffer(b, 0, c, 0, b.size); return c; });
    lab.savedScalars = { cur: lab.cur, acur: lab.acur, steps: lab.steps, years: lab.years };
    device.queue.submit([enc.finish()]);
  };
  lab.restoreState = () => {
    const enc = device.createCommandEncoder();
    [col, lay, flow, aux, wb, acc, out8].forEach((b, k) => enc.copyBufferToBuffer(lab.saved[k], 0, b, 0, b.size));
    device.queue.submit([enc.finish()]); Object.assign(lab, lab.savedScalars);
  };
  lab.step = (count = 1) => {
    // the plates drift with themselves (their seeds move a share of their speed: the belts wander, slowly)
    const drift = lab.params.drift ?? 0;
    if (drift) for (const q of lab.plates) { q[0] += q[2] * drift * lab.params.dt * count; q[1] += q[3] * drift * lab.params.dt * count; }
    upload();
    const enc = device.createCommandEncoder(), pass = enc.beginComputePass();
    for (let s = 0; s < count; s++) step(pass);
    pass.end(); device.queue.submit([enc.finish()]);
  };
  // an outlet at the edge nearest world (x, y) metres, or none there any more if one was near: the base level changes,
  // so the water fills afresh
  lab.toggleOutlet = (x, y) => {
    const span = (N - 1) * lab.params.dx, near = lab.outlets.findIndex(([ox, oy]) => Math.hypot(ox - x, oy - y) < 1500);
    if (near >= 0) lab.outlets.splice(near, 1);
    else if (lab.outlets.length < MAX_OUT) {
      const d = [x, span - x, y, span - y], k = d.indexOf(Math.min(...d));
      lab.outlets.push([k === 0 ? 0 : k === 1 ? span : x, k === 2 ? 0 : k === 3 ? span : y, 250, 0]);
    }
    lab.fullFill = true; upload();
  };
  // is the edge cell (i, j) base level (the page's markers, the headless fill check); as the shaders' isOutlet
  lab.isOutlet = (i, j) => (i === 0 || j === 0 || i === N - 1 || j === N - 1)
    && (!lab.outlets.length || lab.outlets.some(([x, y, w]) => Math.hypot(i * lab.params.dx - x, j * lab.params.dx - y) <= w));
  // the tools: paint uplift (m/yr) at world (x, z) metres; clear it
  lab.paint = (x, y, radius, rate) => {
    lab.brush = [x, y, radius, rate]; upload();
    const enc = device.createCommandEncoder(), pass = enc.beginComputePass();
    run(pass, "paint"); pass.end(); device.queue.submit([enc.finish()]);
    lab.brush = null;
  };
  lab.clearPaint = () => lab.paint(0, 0, -1, 0);
  // done with it: its buffers back to the device (the game keeps the map it read, not the lab)
  lab.destroy = () => { for (const b of [col, lay, flow, aux, wb, acc, out8, disp, index, pbuf, itbuf, vbuf, ...(lab.saved ?? [])]) b?.destroy(); depthTex?.destroy(); };
  lab.setMesh = (M) => mesh(Math.max(2, Math.min(2048, M | 0)));

  // ---- the view
  // (lab.offscreen: draw into a texture of the canvas's size and never present -- a headless browser, ?probe, drops its
  //  GPU instance the moment a WebGPU canvas presents; the game does the same)
  let offTex = null;
  const offscreen = () => {
    if (!lab.offscreen) return null;
    if (!offTex || offTex.width !== canvas.width || offTex.height !== canvas.height) {
      offTex?.destroy();
      offTex = device.createTexture({ size: [canvas.width, canvas.height], format, usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC });
    }
    return offTex;
  };
  const vdata = new Float32Array(VIEW_FLOATS), vu = new Uint32Array(vdata.buffer);
  lab.render = (cam) => {
    const V = lab.view, size = N * lab.params.dx;
    if (!depthTex || depthTex.width !== canvas.width || depthTex.height !== canvas.height) {
      depthTex?.destroy();
      depthTex = device.createTexture({ size: [canvas.width, canvas.height], format: "depth24plus", usage: GPUTextureUsage.RENDER_ATTACHMENT });
    }
    const vp = mul(perspective(cam.fov ?? 0.8, canvas.width / canvas.height, size * 0.005, size * 8), lookAt(cam.eye, cam.target));
    vdata.set(vp, 0); vdata.set([...cam.eye, 1], 16); vdata.set([0.45, 0.8, 0.35, 0], 20);
    vu[24] = lab.M; vu[25] = V.mode; vu[26] = lab.cur; vu[27] = lab.acur;
    const outs = lab.outlets.slice(0, MAX_OUT), span = (N - 1) * lab.params.dx;
    vdata.set([V.exag, size, V.detail, V.riverQ, V.section, V.contour, lab.params.sea, V.rel ? 1 : 0, V.hLo ?? 0, V.hHi ?? 1000, outs.length, 0], 28);
    MATS.forEach((m, i) => { vdata[40 + i] = m.rough * lab.params.dx / 100; vdata.set([...m.color, 1], 48 + 4 * i); });   // (the detail a cell cannot hold: less on a finer grid)
    outs.forEach(([x, y, w], i) => vdata.set([x / span, y / span, Math.max(w * 1.2, 3 * lab.params.dx) / span, 0], 80 + 4 * i));
    device.queue.writeBuffer(vbuf, 0, vdata);
    const enc = device.createCommandEncoder();
    const cp = enc.beginComputePass();
    cp.setPipeline(upPipe); cp.setBindGroup(0, upBG); cp.dispatchWorkgroups(Math.ceil(lab.M / 8), Math.ceil(lab.M / 8));
    cp.end();
    const rp = enc.beginRenderPass({
      colorAttachments: [{ view: (cam.target_tex ?? offscreen() ?? ctx.getCurrentTexture()).createView(), clearValue: { r: 0.62, g: 0.7, b: 0.78, a: 1 }, loadOp: "clear", storeOp: "store" }],
      depthStencilAttachment: { view: depthTex.createView(), depthClearValue: 1, depthLoadOp: "clear", depthStoreOp: "store" } });
    rp.setPipeline(drawPipe); rp.setBindGroup(0, drawBG); rp.setIndexBuffer(index, "uint32"); rp.drawIndexed(nIndex);
    rp.end();
    device.queue.submit([enc.finish()]);
  };

  // a picture of the view, read back (the headless checks; the canvas itself need not be readable)
  lab.snapshot = async (cam, w = canvas.width, h = canvas.height) => {
    const tex = device.createTexture({ size: [w, h], format, usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC });
    const [cw, ch] = [canvas.width, canvas.height]; canvas.width = w; canvas.height = h;
    lab.render({ ...cam, target_tex: tex });
    canvas.width = cw; canvas.height = ch;
    const bpr = Math.ceil(w * 4 / 256) * 256, buf = device.createBuffer({ size: bpr * h, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ });
    const enc = device.createCommandEncoder(); enc.copyTextureToBuffer({ texture: tex }, { buffer: buf, bytesPerRow: bpr }, [w, h]); device.queue.submit([enc.finish()]);
    await buf.mapAsync(GPUMapMode.READ);
    const src = new Uint8Array(buf.getMappedRange()), px = new Uint8ClampedArray(w * h * 4), bgra = format.startsWith("bgra");
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const s = y * bpr + x * 4, d = (y * w + x) * 4;
      px[d] = src[s + (bgra ? 2 : 0)]; px[d + 1] = src[s + 1]; px[d + 2] = src[s + (bgra ? 0 : 2)]; px[d + 3] = 255;
    }
    buf.unmap(); buf.destroy(); tex.destroy();
    return new ImageData(px, w, h);
  };

  // ---- reading it back: every column (for the numbers, the picking, the tools), one row's layers (the cross-section)
  async function readBuffer(src, offset, size) {
    const st = device.createBuffer({ size, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ });
    const enc = device.createCommandEncoder(); enc.copyBufferToBuffer(src, offset, st, 0, size); device.queue.submit([enc.finish()]);
    await st.mapAsync(GPUMapMode.READ);
    const out = new Float32Array(st.getMappedRange().slice(0)); st.unmap(); st.destroy();
    return out;
  }
  lab.readColumns = async () => {
    const C = N * N, [c, w, a, f] = await Promise.all([readBuffer(col, 0, C * 16), readBuffer(wb, 0, C * 8), readBuffer(acc, 0, C * 16), readBuffer(flow, 0, C * 16)]);
    const H = new Float32Array(C), W = new Float32Array(C), Q = new Float32Array(C), Qs = new Float32Array(C), S = new Float32Array(C), F = new Float32Array(C);
    for (let i = 0; i < C; i++) { H[i] = c[i * 4 + 2]; W[i] = w[i * 2 + lab.cur] > 1e6 ? H[i] : w[i * 2 + lab.cur]; Q[i] = a[i * 4 + 2 * lab.acur]; Qs[i] = a[i * 4 + 2 * lab.acur + 1]; S[i] = f[i * 4 + 3]; F[i] = f[i * 4 + 2]; }
    lab.last = { H, W, Q, Qs, S, F, col: c };   // (F: where the water goes -- the facet and the side's share, -1: nowhere)
    return lab.last;
  };
  lab.readRow = async (j) => {
    const [c, l, w] = await Promise.all([readBuffer(col, j * N * 16, N * 16), readBuffer(lay, j * N * LAYERS * 8, N * LAYERS * 8), readBuffer(wb, j * N * 8, N * 8)]);
    return Array.from({ length: N }, (_, i) => ({ base: c[i * 4], H: c[i * 4 + 2], W: w[i * 2 + lab.cur],
      layers: Array.from({ length: c[i * 4 + 1] }, (_, k) => [l[(i * LAYERS + k) * 2 + 1], l[(i * LAYERS + k) * 2]]) }));
  };
  // the land in numbers: relief, water, rivers, what shows at the surface, the rock and sediment in it
  lab.stats = async () => {
    const { H, W, Q, col: c } = await lab.readColumns();
    const layD = await readBuffer(lay, 0, N * N * LAYERS * 8);
    const C = N * N, expo = new Array(MATS.length).fill(0);
    let lo = 1e9, hi = -1e9, sum = 0, lake = 0, sea = 0, river = 0, vol = 0, sed = 0;
    for (let i = 0; i < C; i++) {
      lo = Math.min(lo, H[i]); hi = Math.max(hi, H[i]); sum += H[i];
      const d = W[i] - H[i];
      if (d > lab.params.lakeMin) { if (W[i] <= lab.params.sea + 0.5) sea++; else lake++; }
      else if (Math.log10(Math.max(Q[i], 1)) > lab.view.riverQ) river++;
      const n = c[i * 4 + 1], tm = n ? layD[(i * LAYERS + n - 1) * 2 + 1] : 0, thin = tm === 4 && layD[(i * LAYERS + n - 1) * 2] < 1;
      expo[thin ? (n >= 2 ? layD[(i * LAYERS + n - 2) * 2 + 1] : 0) : tm]++;   // (soil under a metre shows the rock)
      vol += H[i];
      for (let k = 0; k < n; k++) if (layD[(i * LAYERS + k) * 2 + 1] === 4) sed += layD[(i * LAYERS + k) * 2];
    }
    lab.view.hLo = Math.max(lo, lab.params.sea); lab.view.hHi = Math.max(hi, lab.view.hLo + 50);   // (the relative colours' range)
    return { years: lab.years, steps: lab.steps, lo, hi, mean: sum / C, lakeShare: lake / C, seaShare: sea / C, riverShare: river / C,
             surface: Object.fromEntries(MATS.map((m, i) => [m.name, expo[i] / C])), meanSediment: sed / C, falls: lab.waterfalls() };
  };
  // THE WATERFALLS: channels (over Qc) steeper than fallS, each run of such cells one fall; its height from the top of its
  // lip to the pool under it; highest first
  lab.waterfalls = () => {
    const { H, W, Q, S } = lab.last, P = lab.params, C = N * N, seen = new Uint8Array(C), out = [];
    const isFall = (c) => Q[c] > P.Qc && S[c] > P.fallS && W[c] - H[c] <= P.lakeMin;
    for (let c0 = 0; c0 < C; c0++) {
      if (seen[c0] || !isFall(c0)) continue;
      const stack = [c0]; seen[c0] = 1; let top = -1e9, foot = 1e9, q = 0, at = c0;
      while (stack.length) {
        const c = stack.pop(), i = c % N, j = (c / N) | 0;
        if (W[c] > top) { top = W[c]; at = c; } foot = Math.min(foot, W[c] - S[c] * P.dx); q = Math.max(q, Q[c]);
        for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) {
          const ii = i + di, jj = j + dj, k = jj * N + ii;
          if (ii >= 0 && jj >= 0 && ii < N && jj < N && !seen[k] && isFall(k)) { seen[k] = 1; stack.push(k); }
        }
      }
      out.push({ i: at % N, j: (at / N) | 0, height: top - foot, Q: q });
    }
    return out.sort((a, b) => b.height - a.height);
  };

  // ---- export: the upscaled GROUND (the sea and lake beds too) as a 16-bit greyscale PNG and its range in metres, the
  // surface's rock as colours
  lab.exportHeight = async () => {
    const M = lab.M;
    lab.render(lab.lastCam ?? { eye: [0, 1, 1], target: [0, 0, 0] });
    const d = await readBuffer(disp, 0, M * M * 16);
    let lo = 1e9, hi = -1e9;
    for (let i = 0; i < M * M; i++) { const h = d[i * 4]; lo = Math.min(lo, h); hi = Math.max(hi, h); }   // (the ground, under the water too)
    const raw = new Uint8Array(M * (1 + M * 2));
    for (let j = 0; j < M; j++) {
      raw[j * (1 + 2 * M)] = 0;
      for (let i = 0; i < M; i++) {
        const k = j * M + i, v = Math.round((d[k * 4] - lo) / Math.max(hi - lo, 1e-6) * 65535);
        raw[j * (1 + 2 * M) + 1 + 2 * i] = v >> 8; raw[j * (1 + 2 * M) + 2 + 2 * i] = v & 255;
      }
    }
    return { png: await pngEncode(M, M, raw, 16, 0), lo, hi, size: N * lab.params.dx };
  };
  lab.exportMaterials = async () => {
    const M = lab.M, d = await readBuffer(disp, 0, M * M * 16), raw = new Uint8Array(M * (1 + M * 3));
    for (let j = 0; j < M; j++) for (let i = 0; i < M; i++) {
      const k = j * M + i, c = MATS[Math.round(d[k * 4 + 2])]?.color ?? [0, 0, 0], o = j * (1 + 3 * M) + 1 + 3 * i;
      raw[o] = c[0] * 255; raw[o + 1] = c[1] * 255; raw[o + 2] = c[2] * 255;
    }
    return pngEncode(M, M, raw, 8, 2);
  };

  alloc(N);
  return lab;
}

// a PNG from filtered scanlines (each row starts with its filter byte, 0): IHDR, IDAT (deflated), IEND
async function pngEncode(w, h, raw, depth, colorType) {
  const crcT = new Uint32Array(256).map((_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c; });
  const crc = (b) => { let c = 0xffffffff; for (const x of b) c = crcT[(c ^ x) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
  const chunk = (type, data) => {
    const out = new Uint8Array(12 + data.length), dv = new DataView(out.buffer);
    dv.setUint32(0, data.length); out.set([...type].map((ch) => ch.charCodeAt(0)), 4); out.set(data, 8);
    dv.setUint32(8 + data.length, crc(out.subarray(4, 8 + data.length)));
    return out;
  };
  const ihdr = new Uint8Array(13), dv = new DataView(ihdr.buffer);
  dv.setUint32(0, w); dv.setUint32(4, h); ihdr.set([depth, colorType, 0, 0, 0], 8);
  const z = new Uint8Array(await new Response(new Blob([raw]).stream().pipeThrough(new CompressionStream("deflate"))).arrayBuffer());
  const parts = [new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10]), chunk("IHDR", ihdr), chunk("IDAT", z), chunk("IEND", new Uint8Array(0))];
  return new Blob(parts, { type: "image/png" });
}
