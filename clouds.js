// CLOUDS (2026-11-18): the sky's clouds by TYPE -- cumulus, towering cumulus, cumulonimbus, stratocumulus, scud,
// stratus, nimbostratus, altostratus, cirrostratus, altocumulus, cirrocumulus, cirrus -- each a definition in
// assets/sky/clouds/*.json, drawn as one of four FAMILIES, each a layer of its own at its own height (docs/clouds.md).
// Three are drawn in the sky dome's own shader (compose); the heaps in a small pass of their own first (heapPass):
//
//   heap    clouds with a body (cumulus and its kin): a VOLUME from `base` up `thickness` metres, marched through
//           (STEPS samples a pixel, at a quarter of the screen's size) -- a billow field `cover`ing it, each heap as tall
//           as it is thick there (`taper`: domed over a flat base), a 3D noise wearing its edges (`detail`), an `anvil`
//           spreading near the top; lit toward the sun (Beer's law, the silver lining) and by the sky (the base `dark`)
//   sheet   a layer with no body (stratus, nimbostratus, altostratus, cirrostratus): a broad field at `height`, `cover`
//           of the sky, `dark` grey; the sun showing through a thin one (`veil`), a 22-degree `halo` round it in an
//           icy one, `waves` (undulatus), and curtains of `rain` hanging from it toward the horizon
//   cells   the patterned layers (altocumulus, cirrocumulus): cells `size` metres across in patches, stretched and in
//           `rows`, `shading` their sunward side
//   streak  cirrus: fine streaks `stretch` times as long as wide, `hook`ed at their ends
//
// The sky shows one type a family at a time, so a SKY is up to four of them: `skies.json` names the usual ones (fair:
// cumulus under cirrus; mackerel: altocumulus; storm: cumulonimbus over nimbostratus ...) and which each weather draws
// from. A change of sky eases over `ease` seconds: a family that stays MORPHS (cumulus growing into congestus), one that
// goes thins away where it is, one that comes thickens in place.
//
//   const clouds = createClouds()                 (sky.js makes one: sky.clouds)
//   clouds.set([{ type: "cumulus" }, { type: "cirrus", amount: .5 }], { now })   // or { def } (a definition as edited)
//   clouds.sky("fair") / clouds.weather("rain", 2, seed) -> the sky's list; clouds.update(dt)
//   clouds.dim()     how much the sky's sheets and heaps take from the sun, 0..1 (sky.js greys the sky by it)
//   clouds.shadow()  { cover, amount } for the land's cloud shadows (cloudshadow.js CLOUD)
//   compose(ctx)     the node: the sky's colour with the clouds over it (sky.js)
//   heapPass(ctx)    the heaps' own pass: { texture, texel, render(renderer, camera) } -- render it before the frame
import * as THREE from "three";
import { Fn, uniform, vec2, vec3, float, smoothstep, mix, pow, max, clamp, dot, normalize, texture, Loop, If, Break, sin, cos, acos, atan, log2, fract, min, exp, vec4, screenUV, screenCoordinate, texture3D, interleavedGradientNoise, positionWorld, cameraPosition } from "three/tsl";
import cumulus from "./assets/sky/clouds/cumulus.json" with { type: "json" };
import congestus from "./assets/sky/clouds/congestus.json" with { type: "json" };
import cumulonimbus from "./assets/sky/clouds/cumulonimbus.json" with { type: "json" };
import stratocumulus from "./assets/sky/clouds/stratocumulus.json" with { type: "json" };
import fractus from "./assets/sky/clouds/fractus.json" with { type: "json" };
import stratus from "./assets/sky/clouds/stratus.json" with { type: "json" };
import nimbostratus from "./assets/sky/clouds/nimbostratus.json" with { type: "json" };
import altostratus from "./assets/sky/clouds/altostratus.json" with { type: "json" };
import cirrostratus from "./assets/sky/clouds/cirrostratus.json" with { type: "json" };
import altocumulus from "./assets/sky/clouds/altocumulus.json" with { type: "json" };
import cirrocumulus from "./assets/sky/clouds/cirrocumulus.json" with { type: "json" };
import cirrus from "./assets/sky/clouds/cirrus.json" with { type: "json" };
import SKIES from "./assets/sky/skies.json" with { type: "json" };

export const CLOUD_TYPES = { cumulus, congestus, cumulonimbus, stratocumulus, fractus, stratus, nimbostratus, altostratus, cirrostratus, altocumulus, cirrocumulus, cirrus };
export { SKIES };
// each family's fields, four to a uniform (its vec4s), and which of them is its AMOUNT (0: the layer is not there)
export const FAMILIES = {
  heap:   { fields: ["base", "thickness", "cover", "scale", "taper", "anvil", "dark", "soft", "amount", "drift", "detail", "patchy"] },
  sheet:  { fields: ["height", "cover", "scale", "soft", "amount", "dark", "waves", "veil", "rain", "halo", "drift", "texture"] },
  cells:  { fields: ["height", "cover", "size", "stretch", "amount", "soft", "patchy", "drift", "rows", "angle", "shading", "_"] },
  streak: { fields: ["height", "amount", "stretch", "width", "hook", "density", "drift", "angle"] },
};
const STEPS = 48, SPAN = 32000, FAR = 160000, EARTH = 6.371e6;   // (the heap's march: samples a pixel over at most SPAN m of the line of sight, none starting past FAR)

// THE CLOUDS' NOISE, baked once into one tile that repeats, so the shader only reads it: r heaped billows (inverted
// Worley, three octaves, with some smooth noise so they aren't all round), g finer billows (edges; the cells), b broad
// drifts (where the sky is clearer or fuller; a sheet's body), a smooth wisps (cirrus, read stretched). Each 0..1.
export function bakeCloudNoise(N = 512) {
  const hash = (x, y, s) => { let h = Math.imul(x * 374761393 + y * 668265263 + s * 2147483647 | 0, 1274126177); h ^= h >>> 13; h = Math.imul(h, 1103515245); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };
  const worley = (u, v, f, s) => {                     // (distance to the nearest of a jittered grid, f cells a tile: 0 at a point, about 1 between them)
    const X = u * f, Y = v * f, ix = Math.floor(X), iy = Math.floor(Y);
    let best = 9;
    for (let b = -1; b <= 1; b++) for (let a = -1; a <= 1; a++) {
      const cx = ((ix + a) % f + f) % f, cy = ((iy + b) % f + f) % f, dx = ix + a + hash(cx, cy, s) - X, dy = iy + b + hash(cx, cy, s + 1) - Y, d = dx * dx + dy * dy;
      if (d < best) best = d;
    }
    return Math.min(1, Math.sqrt(best));
  };
  const smooth = (u, v, f, s) => {                     // (value noise, f cells a tile)
    const X = u * f, Y = v * f, ix = Math.floor(X), iy = Math.floor(Y), fx = X - ix, fy = Y - iy, a = fx * fx * (3 - 2 * fx), c = fy * fy * (3 - 2 * fy);
    const at = (i, j) => hash(((i % f) + f) % f, ((j % f) + f) % f, s);
    return (at(ix, iy) * (1 - a) + at(ix + 1, iy) * a) * (1 - c) + (at(ix, iy + 1) * (1 - a) + at(ix + 1, iy + 1) * a) * c;
  };
  const chans = [new Float32Array(N * N), new Float32Array(N * N), new Float32Array(N * N), new Float32Array(N * N)];
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    const u = x / N, v = y / N, i = y * N + x;
    const warp = smooth(u, v, 5, 41) * .05;            // (a little sideways: no billow is a perfect round)
    chans[0][i] = .55 * (1 - worley(u + warp, v, 7, 1)) + .3 * (1 - worley(u, v + warp, 15, 3)) + .15 * (1 - worley(u, v, 31, 5)) + .42 * (smooth(u, v, 4, 7) - .5);
    chans[1][i] = .5 * (1 - worley(u, v, 19, 9)) + .3 * (1 - worley(u, v, 37, 11)) + .2 * smooth(u, v, 64, 13);
    chans[2][i] = .6 * smooth(u, v, 3, 15) + .3 * smooth(u, v, 6, 17) + .1 * smooth(u, v, 12, 19);
    chans[3][i] = .5 * smooth(u, v, 8, 21) + .28 * smooth(u, v, 16, 23) + .15 * smooth(u, v, 32, 25) + .07 * smooth(u, v, 64, 27);
  }
  const data = new Uint8Array(N * N * 4);
  chans.forEach((c, k) => {
    let lo = Infinity, hi = -Infinity;
    for (const q of c) { if (q < lo) lo = q; if (q > hi) hi = q; }
    for (let i = 0; i < c.length; i++) data[i * 4 + k] = Math.round((c[i] - lo) / (hi - lo) * 255);
  });
  const tex = new THREE.DataTexture(data, N, N, THREE.RGBAFormat);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping; tex.magFilter = THREE.LinearFilter; tex.minFilter = THREE.LinearMipmapLinearFilter;
  tex.generateMipmaps = true; tex.anisotropy = 4; tex.needsUpdate = true;
  return tex;
}

// a sky's entry as a full definition: its type's (or the `def` given) with the entry's own fields over it
const resolve = (e) => { const base = e.def ?? CLOUD_TYPES[e.type]; if (!base) throw new Error(`clouds: no type "${e.type}"`); return { ...base, ...e, def: undefined }; };

export function createClouds({ ease = 40 } = {}) {
  const fams = Object.keys(FAMILIES);
  const n = (f) => FAMILIES[f].fields.length, amountAt = (f) => FAMILIES[f].fields.indexOf("amount");
  const U = Object.fromEntries(fams.map((f) => [f, Array.from({ length: n(f) / 4 }, () => uniform(new THREE.Vector4()))]));
  // (the values shown, and those they ease to; a family not in the sky keeps its last look at amount 0)
  const cur = Object.fromEntries(fams.map((f) => [f, new Float32Array(n(f))])), tgt = Object.fromEntries(fams.map((f) => [f, new Float32Array(n(f))]));
  const put = () => { for (const f of fams) U[f].forEach((u, i) => u.value.set(...cur[f].slice(i * 4, i * 4 + 4))); };
  let list = [];
  const api = {
    U, ease,
    get list() { return list; },
    set(entries, { now = false } = {}) {
      list = entries.map(resolve);
      for (const f of fams) {
        const d = list.find((e) => e.family === f), a = amountAt(f);
        if (d) {
          FAMILIES[f].fields.forEach((k, i) => { tgt[f][i] = d[k] ?? (k === "amount" ? 1 : 0); });
          if (cur[f][a] < .001) { const keep = cur[f][a]; cur[f].set(tgt[f]); cur[f][a] = keep; }   // (it comes: thickening where it will be)
        } else tgt[f][a] = 0;                                                                        // (it goes: thinning where it is)
        if (now) cur[f].set(tgt[f]);
      }
      put();
      return api;
    },
    sky(name) { const s = SKIES.skies[name]; if (!s) throw new Error(`clouds: no sky "${name}"`); return s; },
    // the skies a weather (clear / rain / snow) at an intensity (0..2) draws from, and the `k`th of them (a seed, a count of changes)
    weather(kind, intensity, k = 0) { const opts = SKIES.weather[kind]?.[intensity] ?? ["blue"]; return opts[((k % opts.length) + opts.length) % opts.length]; },
    update(dt) {
      const k = Math.min(1, dt / Math.max(1e-3, api.ease));
      for (const f of fams) for (let i = 0; i < cur[f].length; i++) cur[f][i] += (tgt[f][i] - cur[f][i]) * k;
      put();
    },
    // how much of the sun's light the sky's clouds take, 0..1: a full sheet by its darkness, less the thinner it is to
    // the sun (a veil); a heap layer only once it closes over
    dim() {
      const [, sc, , , sa, sd, , sv] = cur.sheet, h = cur.heap;
      const sheet = sa * smoothstep01(.5, 1, sc) * (1 - sv * .8) * (.35 + .65 * sd);
      const heap = h[8] * smoothstep01(.55, .95, h[2]) * (.3 + .5 * h[6]);
      return Math.min(1, Math.max(sheet, heap));
    },
    // the land's cloud shadows: the heaps' and cells' cover, none under a closed grey sheet (the light is all diffuse)
    shadow() {
      const h = cur.heap, c = cur.cells, s = cur.sheet;
      const amount = Math.min(1, h[8] + c[4] * .35) * (1 - s[4] * smoothstep01(.6, .95, s[1]));
      return { cover: Math.min(.95, (h[8] * h[2] + c[4] * c[1] * .5) / Math.max(.05, h[8] + c[4] * .5)), amount };
    },
  };
  return api;
}
const smoothstep01 = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

// THE CLOUDS' VOLUME: a tile of 3D noise (N^3) that repeats, baked once, for a heap's body to be worn into: r billows
// (inverted Worley, three octaves), g finer ones (its edges' detail)
export function bakeCloudVolume(N = 64) {
  const hash = (x, y, z, s) => { let h = Math.imul(x * 374761393 + y * 668265263 + z * 1440662683 + s * 2147483647 | 0, 1274126177); h ^= h >>> 13; h = Math.imul(h, 1103515245); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };
  const worley = (u, v, w, f, s) => {
    const X = u * f, Y = v * f, Z = w * f, ix = Math.floor(X), iy = Math.floor(Y), iz = Math.floor(Z);
    let best = 9;
    for (let c = -1; c <= 1; c++) for (let b = -1; b <= 1; b++) for (let a = -1; a <= 1; a++) {
      const cx = ((ix + a) % f + f) % f, cy = ((iy + b) % f + f) % f, cz = ((iz + c) % f + f) % f;
      const dx = ix + a + hash(cx, cy, cz, s) - X, dy = iy + b + hash(cx, cy, cz, s + 1) - Y, dz = iz + c + hash(cx, cy, cz, s + 2) - Z, d = dx * dx + dy * dy + dz * dz;
      if (d < best) best = d;
    }
    return Math.min(1, Math.sqrt(best));
  };
  const r = new Float32Array(N ** 3), g = new Float32Array(N ** 3);
  for (let z = 0, i = 0; z < N; z++) for (let y = 0; y < N; y++) for (let x = 0; x < N; x++, i++) {
    const u = x / N, v = y / N, w = z / N;
    r[i] = .6 * (1 - worley(u, v, w, 4, 1)) + .28 * (1 - worley(u, v, w, 8, 4)) + .12 * (1 - worley(u, v, w, 16, 7));
    g[i] = .6 * (1 - worley(u, v, w, 12, 10)) + .4 * (1 - worley(u, v, w, 24, 13));
  }
  const data = new Uint8Array(N ** 3 * 4);
  [r, g].forEach((c, k) => {
    let lo = Infinity, hi = -Infinity;
    for (const q of c) { if (q < lo) lo = q; if (q > hi) hi = q; }
    for (let i = 0; i < c.length; i++) data[i * 4 + k] = Math.round((c[i] - lo) / (hi - lo) * 255);
  });
  const tex = new THREE.Data3DTexture(data, N, N, N);
  tex.format = THREE.RGBAFormat; tex.type = THREE.UnsignedByteType;
  tex.wrapS = tex.wrapT = tex.wrapR = THREE.RepeatWrapping; tex.magFilter = tex.minFilter = THREE.LinearFilter;
  tex.needsUpdate = true;
  return tex;
}

// THE HEAPS' PASS: a dome of its own round the eye, drawn into a picture a quarter of the screen's size each way at
// the frame's start (render), which the sky's shader then reads by the pixel (compose's heapTex) -- the heaps are
// marched through as a volume, too dear at full size and too soft to need it. ctx: as compose's (no base/heapTex).
//
// Along the line of sight -- over the curve of the earth, so the layer runs down to the horizon -- from where it
// enters the layer's base to where it leaves its top (at most SPAN m of it), STEPS samples, each start jittered
// per pixel. A heap's body: a COVER from the billow field (`cover`, gathered by the broad drifts by `patchy`), its top
// as high in the layer as it is thick there (`taper`: 0 a flat slab), so each heap is domed over its middle with a
// flat base; near the top an ANVIL spreading over the towers' neighbourhood (the field blurred); the 3D noise wearing
// its edges into billows (`detail`), more toward the top. Light: three steps toward the sun (Beer's law, the edges'
// powder), forward scattering toward the sun (the silver lining), the sky's light from above (the tops brighter, the
// base `dark`); the far ones into the haze.
export function heapPass(ctx, { radius = 1000, scale = 1 / 4 } = {}) {
  const { U, noise, vol, cam, dir, t, lit, shade, hor, sun, sunUp, solid } = ctx;
  const [hA, hB, hC] = U.heap;
  const node = Fn(() => {
    const v = normalize(positionWorld.sub(cameraPosition)), up = v.y;
    const out = vec4(0).toVar();
    If(hC.x.greaterThan(.001).and(up.greaterThan(-.03)), () => {
      // where the line of sight reaches height h over a round earth (stable for any `up`)
      const reach = (h) => { const a = max(h.sub(cam.y), 1); return a.mul(2).div(up.add(up.mul(up).add(a.mul(2 / EARTH)).sqrt())); };
      const dA = reach(hA.x), dB = min(reach(hA.x.add(hA.y)), dA.add(min(hA.y.mul(7), SPAN)));   // (no further than the slab is thick, sevenfold: fine steps near the horizon)
      If(dA.lessThan(FAR), () => {
        const H = hA.w, drift = vec2(t.mul(hC.y).negate(), 0), dt = dB.sub(dA).div(STEPS);
        const lodAt = (d) => clamp(log2(d.mul(.0016).div(max(up.add(.075), .04)).mul(512).div(H)), 0, 8);
        // the body's density at p (its height share hs), 0..1
        const density = (p, hs, lod, erode) => {
          const xz = p.xz.add(drift);
          const f = texture(noise, xz.div(H)).level(lod.add(1.5)).r, mask = texture(noise, xz.div(H.mul(4.5))).level(lod.sub(2.2).max(0)).b;
          const L0 = mix(float(.74), float(.3), hA.z).add(float(.5).sub(mask).mul(hC.w).mul(.7));
          const lumps = texture3D(vol, vec3(xz.x, p.y.mul(1.6), xz.y).div(H.mul(.3))).r;   // (the cover changing as it rises: sides that bulge, not curtains)
          const c = smoothstep(L0, L0.add(.28), f.add(lumps.sub(.5).mul(.3).mul(hC.z)));
          const top = mix(float(1), c.sqrt(), hB.x);                               // (the heap's height here: by its cover, steep-sided, round-topped)
          const body = c.mul(smoothstep(0, .05, hs)).mul(clamp(top.sub(hs).mul(7), 0, 1)).toVar();
          If(hB.y.greaterThan(.01), () => {                                         // (an anvil over the towers' neighbourhood)
            const around = smoothstep(L0.add(.1), L0.add(.26), texture(noise, xz.div(H)).level(lod.add(2.6)).r);
            body.assign(max(body, around.mul(hB.y).mul(smoothstep(.74, .84, hs)).mul(smoothstep(1, .93, hs))));
          });
          const dens = body.toVar();
          if (erode !== false) If(body.greaterThan(.001).and(erode), () => {
            const q = vec3(xz.x, p.y, xz.y);
            const n = texture3D(vol, q.div(H.mul(.12))).r.mul(.65).add(texture3D(vol, q.div(H.mul(.045))).g.mul(.35));
            dens.assign(clamp(body.sub(float(1).sub(n).mul(mix(float(.18), float(.5), hs)).mul(hC.z.mul(1.6))), 0, 1));
          });
          return dens;
        };
        const K = 1 / 90;   // (extinction a metre at full density)
        const T = float(1).toVar(), col = vec3(0).toVar();
        const jit = interleavedGradientNoise(screenCoordinate.xy), toSun = max(dot(v, dir), 0);
        const phase = float(.55).add(pow(toSun, 6).mul(.9)).add(pow(toSun, 40).mul(1.6));
        const Ls = hA.y.mul(.08).max(80);   // (the light's steps toward the sun)
        Loop(STEPS, ({ i }) => {
          const d = dA.add(float(i).add(jit).mul(dt));
          const p = cam.add(v.mul(d)), alt = cam.y.add(d.mul(up)).add(d.mul(d).div(2 * EARTH));
          const hs = alt.sub(hA.x).div(hA.y), lod = lodAt(d);
          const P = vec3(p.x, alt, p.z);
          const dens = density(P, hs, lod, d.lessThan(70000));
          If(dens.greaterThan(.004), () => {
            let sumL = float(0);
            for (const k of [1.5, 5]) {
              const q = P.add(dir.mul(Ls.mul(k)));
              sumL = sumL.add(density(q, q.y.sub(hA.x).div(hA.y), lod.add(.5), false).mul(Ls.mul(k === 1.5 ? 1.8 : 3.5)));
            }
            const toLight = exp(sumL.mul(K * -.5)), powder = float(1).sub(exp(dens.mul(-6)));
            const sky = mix(shade.mul(float(1).sub(hB.z.mul(.5))), lit.mul(.82), clamp(hs, 0, 1));
            const S = lit.mul(toLight).mul(powder.mul(.5).add(.5)).mul(phase).mul(sunUp.mul(.85).add(.15)).mul(float(1).sub(hB.z.sub(.4).max(0).mul(1.3))).add(sky.mul(.62));   // (a rain cloud's `dark`: the sun's light too)
            const step = exp(dens.mul(dt).mul(-K));
            col.addAssign(S.mul(T).mul(float(1).sub(step)));
            T.mulAssign(step);
            If(T.lessThan(.02), () => { Break(); });
          });
        });
        const haze = float(1).sub(exp(dA.div(-52000))).mul(smoothstep(.35, 0, up).mul(.6).add(.4));
        const a = float(1).sub(T).mul(hC.x).mul(solid);
        out.assign(vec4(mix(col.div(max(float(1).sub(T), 1e-3)), hor, haze).mul(a), a));
      });
    });
    return out;
  })();
  const scene = new THREE.Scene();
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.BackSide, depthWrite: false, depthTest: false });
  mat.fragmentNode = node;
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(radius, 32, 16), mat);
  mesh.frustumCulled = false; scene.add(mesh);
  const rt = new THREE.RenderTarget(16, 16, { type: THREE.HalfFloatType, depthBuffer: false });
  const size = new THREE.Vector2(), clear = new THREE.Color(), texel = uniform(new THREE.Vector2(1 / 16, 1 / 16));
  let drawn = false;
  return {
    texture: rt.texture, texel,
    // at the frame's start: the heaps as the camera sees them (skipped, once cleared, while there are none)
    render(renderer, camera) {
      const on = hC.value.x > .001;
      if (!on && !drawn) return;
      renderer.getDrawingBufferSize(size);
      const w = Math.max(16, Math.round(size.x * scale)), h = Math.max(16, Math.round(size.y * scale));
      if (rt.width !== w || rt.height !== h) { rt.setSize(w, h); texel.value.set(1 / w, 1 / h); }
      mesh.position.copy(camera.position); mesh.visible = on;
      const prev = renderer.getRenderTarget(), ca = renderer.getClearAlpha(); renderer.getClearColor(clear);
      renderer.setRenderTarget(rt); renderer.setClearColor(0x000000, 0); renderer.clear();
      if (on) renderer.render(scene, camera);
      renderer.setRenderTarget(prev); renderer.setClearColor(clear, ca);
      drawn = on;
    },
  };
}

// THE CLOUDS OVER THE SKY: the node sky.js makes its colour with. ctx: { U (createClouds's), noise, v (the view's
// direction), up (its y), cam (the eye), dir (the sun's), t (seconds: the drift), base (the sky's colour), lit, shade,
// hor, sun (colours: the clouds' sunlit side, their shade, the horizon's haze, the sun's), disc (the sun's disc 0..1, 0
// behind a grey sky), sunUp (the sun above the horizon 0..1), solid (the clouds' night thinning) }
export const compose = (ctx) => Fn(() => {
  const { U, noise, heapTex, heapTexel, v, up, cam, dir, t, base, lit, shade, hor, sun, disc, sunUp, solid } = ctx;
  const [hA] = U.heap, [sA, sB, sC] = U.sheet, [cA, cB, cC] = U.cells, [wA, wB] = U.streak;
  // where the line of sight meets a height h: bent a little so a layer never runs out at the horizon
  const bend = max(up.add(.075), .012);
  const dist = (h) => max(h.sub(cam.y), 60).div(bend);
  // the noise's level of detail for a feature `scale` metres a tile at distance d: a pixel's footprint over a texel
  const lodAt = (d, scale) => clamp(log2(d.mul(.0016).div(max(bend, .04)).mul(512).div(scale)), 0, 8);
  const tex = (uv, lod) => texture(noise, uv).level(lod);
  const toSun = max(dot(v, dir), 0), sunXZ = normalize(dir.xz.add(vec2(.001, 0)));
  const hazed = smoothstep(.28, .02, up).mul(.62);                     // (far off they go into the haze)
  const seen = smoothstep(.0, .07, up);                                // (only above the land)
  const rim = pow(toSun, 9).mul(.75).add(pow(toSun, 90).mul(1.1)).mul(disc);   // (the silver lining)

  // -- STREAK: cirrus, combed out along `angle`, hooked
  const dw = dist(wA.x), pw0 = cam.xz.add(v.xz.mul(dw)).add(vec2(t.mul(wB.z).negate(), 0));
  const ca = cos(wB.w), sa = sin(wB.w), pw = vec2(pw0.x.mul(ca).sub(pw0.y.mul(sa)), pw0.x.mul(sa).add(pw0.y.mul(ca)));
  const W = wA.w, wy = pw.y.add(sin(pw.x.div(W.mul(1.3))).mul(W.mul(.35)).mul(wB.x)), lw = lodAt(dw, W);
  const streaks = tex(vec2(pw.x.div(W.mul(wA.z)).add(wy.div(W.mul(17))), wy.div(W)), lw).a.mul(.7)
    .add(tex(vec2(pw.x.div(W.mul(1.55)), wy.div(W.mul(.38))), lw.add(1.4)).a.mul(.3));
  const aW = smoothstep(.5, .78, streaks).mul(wA.y).mul(wB.y).mul(.7).mul(smoothstep(.03, .2, up)).mul(solid);
  const colW = mix(lit, hor, hazed.mul(.5)).add(sun.mul(rim).mul(.5));

  // -- CELLS: altocumulus, cirrocumulus -- cells in rows and patches
  const dc = dist(cA.x), pc0 = cam.xz.add(v.xz.mul(dc)).add(vec2(t.mul(cB.w).negate(), 0));
  const cc = cos(cC.y), sc = sin(cC.y), pc = vec2(pc0.x.mul(cc).sub(pc0.y.mul(sc)), pc0.x.mul(sc).add(pc0.y.mul(cc)));
  const tile = cA.z.mul(19), uvc = vec2(pc.x.div(cA.w), pc.y).div(tile), lc = lodAt(dc, tile);
  const cellAt = (uv) => tex(uv, lc).g.mul(mix(float(1), sin(uv.y.mul(tile).div(cA.z).mul(2.1)).mul(.3).add(.7), cC.x));
  const cf = cellAt(uvc), cfSun = cellAt(uvc.add(vec2(sunXZ.x.mul(cc).sub(sunXZ.y.mul(sc)), sunXZ.x.mul(sc).add(sunXZ.y.mul(cc))).mul(.004)));
  const patch = mix(float(1), smoothstep(.38, .62, tex(pc0.div(cA.z.mul(60)), lodAt(dc, cA.z.mul(60))).b), cB.z);
  const lineC = mix(float(.9), float(.35), cA.y);
  const aC = smoothstep(lineC, lineC.add(cB.y), cf).mul(patch).mul(cB.x).mul(seen).mul(solid);
  const reliefC = clamp(cf.sub(cfSun).mul(9).add(.5), 0, 1);
  const colC = mix(mix(lit, shade.mul(1.15), cC.z.mul(.6)), lit, reliefC.mul(cC.z)).add(sun.mul(rim).mul(float(1).sub(smoothstep(lineC, lineC.add(.25), cf)))).toVar();
  colC.assign(mix(colC, hor, hazed));

  // -- SHEET: stratus, nimbostratus, altostratus, cirrostratus
  const ds = dist(sA.x), ps = cam.xz.add(v.xz.mul(ds)).add(vec2(t.mul(sC.z).negate(), 0)), S = sA.z, ls = lodAt(ds, S);
  const fs = tex(ps.div(S), ls).b.mul(.62).add(tex(ps.div(S.mul(.21)), ls.add(2.25)).a.sub(.5).mul(.5).mul(sC.w))
    .add(tex(ps.div(S.mul(.06)), ls.add(4)).g.sub(.5).mul(.25).mul(sC.w)).add(.19)
    .add(sin(dot(ps, vec2(.8, .6)).div(S.mul(.012))).mul(.08).mul(sB.z));   // (undulatus: long waves across it)
  const lineS = mix(float(.95), float(-.15), sA.y);
  const aS0 = smoothstep(lineS.sub(sA.w), lineS.add(sA.w), fs).mul(sB.x);
  const thickS = smoothstep(lineS, lineS.add(.35), fs);
  const colS = mix(lit, shade.mul(mix(float(1), float(.55), sB.y)), sB.y.mul(thickS.mul(.35).add(.65))).toVar();
  // the sun through a thin one (ground glass), the halo round it in an icy one
  const ang = acos(clamp(dot(v, dir), -1, 1)).mul(57.2958);
  const halo = smoothstep(21.2, 22, ang).mul(smoothstep(23.6, 22.3, ang)).mul(sC.y).mul(sunUp);
  colS.addAssign(sun.mul(pow(toSun, 25).mul(.45).add(pow(toSun, 900).mul(1.6))).mul(sB.w).mul(sunUp).mul(float(1).sub(sB.y)));
  colS.addAssign(vec3(1, .92, .82).mul(halo).mul(.3));
  colS.assign(mix(colS, hor, hazed.mul(.8)));
  // its rain: grey curtains hanging toward the horizon, streaked
  const az = atan(v.z, v.x).div(6.2832);
  const curtain = smoothstep(.35, .72, tex(vec2(az.mul(14), up.mul(.9)), 0).a).mul(smoothstep(.16, .01, up)).mul(smoothstep(-.02, .015, up)).mul(sC.x).mul(sB.x);
  const aS = max(aS0.mul(smoothstep(-.01, .05, up)), curtain.mul(.8)).mul(solid);
  colS.assign(mix(colS, mix(shade, hor, .4), curtain.mul(float(1).sub(aS0.mul(.5)))));

  // -- HEAP: the volumetric pass's picture (heapPass, drawn at the frame's start at a quarter of the size): premultiplied
  const o = heapTexel.mul(.85), hp = texture(heapTex, screenUV.add(vec2(o.x, o.y))).add(texture(heapTex, screenUV.add(vec2(o.x.negate(), o.y))))
    .add(texture(heapTex, screenUV.add(vec2(o.x, o.y.negate())))).add(texture(heapTex, screenUV.sub(o))).mul(.25), aH = hp.a;   // (four taps: the march's jitter smoothed away)

  // -- over the sky, the highest first; the sheet and the heaps by which is the lower (in front)
  const c2 = mix(mix(base, colW, aW), colC, aC);
  const sheetLow = sA.x.lessThan(hA.x), overH = (c) => c.mul(float(1).sub(aH)).add(hp.rgb);
  const heapThenSheet = mix(overH(c2), colS, aS), sheetThenHeap = overH(mix(c2, colS, aS));
  return mix(sheetThenHeap, heapThenSheet, sheetLow.select(float(1), float(0)));
})();
