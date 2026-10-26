// THE SUN'S SHADOWS (2026-10-24): the world's sun is static (light.js), so what the buildings shade never changes --
// it is drawn ONCE, after they are built: the buildings seen from the sun (an orthographic camera along LIGHT.dir)
// into depth maps, and every surface that lies on the land (cloudshadow.js landShade: the ground, the roads, the
// buildings' walls and roofs) and the figures (shell.js) look themselves up in them. In the shadow of a house, a wall,
// a stall's awning, the direct share of the sun is taken away -- what Lambert gave it beyond the ambient -- so a face
// turned from the sun (already in its own shade) is unchanged and a street under a gable falls into shade. By night and
// under a grey sky it fades (SUN.k: index.html, with the clouds' shadow).
// TWO MAPS: a FINE one over the town's core (the buildings within SUN_SHADOW.reach of the middle of them all: ~11 cm a
// texel, four filtered taps), and a COARSE one over every building there is (the mill, the farms, the windmill out in
// the fields: ~40 cm a texel, one filtered tap) for whatever the fine one does not cover.
//
//   bakeSunShadow(renderer, scene, groups)   // groups: the buildings as placed (what casts)
//   sunShade(pw?, nw?)                        // a node: the colour's factor where the fragment is (1: in the sun)
import * as THREE from "three";
import { uniform, texture, positionWorld, normalWorld, vec2, vec4, float, max, dot, vec3, depth } from "three/tsl";
import { LIGHT } from "./light.js";

// fine/coarse: each map's texels a side, its bias (depth, of the light's range, a surface stands in front of what it is
// compared with) and normal offset (metres pushed out along its normal first: no acne on the slopes); margin: metres
// round the buildings; reach: how far from their middle a building casts into the fine map; soft: the fine taps' spread
// in texels; depth: how much darker a shadow is than Lambert's direct share alone would make it (the world's ambient is
// high -- .62 -- for the look; a shadow at only that read as a smudge), at most .55 off
export const SUN_SHADOW = { fine: { res: 3072, bias: .0006, normal: .08 }, coarse: { res: 2048, bias: .0012, normal: .3 },
                            margin: 20, reach: 200, soft: 1.0, depth: 1.5, layer: 7 };
const mapOf = (res) => {
  const rt = new THREE.RenderTarget(res, res, { depthBuffer: true });
  rt.depthTexture = new THREE.DepthTexture(res, res);
  rt.depthTexture.type = THREE.FloatType;
  rt.depthTexture.compareFunction = THREE.LessEqualCompare;
  rt.depthTexture.minFilter = rt.depthTexture.magFilter = THREE.LinearFilter;   // (a comparison sampler that filters: each tap is itself a 2x2 PCF)
  return { rt, res, matrix: uniform(new THREE.Matrix4()) };
};
const FINE = mapOf(SUN_SHADOW.fine.res), COARSE = mapOf(SUN_SHADOW.coarse.res);
export const SUN = { k: uniform(0), baked: false };

// where a map sees the point: its uv, its depth, whether it is inside
function inMap(M, S, pw, nw) {
  const lp = M.matrix.mul(vec4(pw.add(nw.mul(S.normal)), 1));
  const uv = vec2(lp.x.mul(.5).add(.5), lp.y.mul(-.5).add(.5));
  const inside = uv.x.greaterThan(0).and(uv.x.lessThan(1)).and(uv.y.greaterThan(0)).and(uv.y.lessThan(1)).and(lp.z.lessThan(1));
  return { uv, z: lp.z.sub(S.bias), inside };
}
// the share of the sun's light that reaches here, 0..1 (1 where neither map reaches)
function sunLit(pw, nw) {
  const f = inMap(FINE, SUN_SHADOW.fine, pw, nw), c = inMap(COARSE, SUN_SHADOW.coarse, pw, nw), t = SUN_SHADOW.soft / FINE.res;
  const tap = (dx, dy) => texture(FINE.rt.depthTexture, f.uv.add(vec2(dx * t, dy * t))).compare(f.z);
  const fine = tap(-.5, -.5).add(tap(.5, -.5)).add(tap(-.5, .5)).add(tap(.5, .5)).mul(.25);
  const coarse = texture(COARSE.rt.depthTexture, c.uv).compare(c.z);
  return f.inside.select(fine, c.inside.select(coarse, float(1)));
}
// the colour's factor: in shade, what the sun gave beyond the ambient taken off -- Lambert's direct share of the light
// (pw, nw: the world position and unit normal -- the fragment's own by default; the figures' shells hand theirs)
export const SUN_OFF = typeof location !== "undefined" && new URLSearchParams(location.search).get("sunshadow") === "0";   // (?sunshadow=0: not in the shaders at all)
export function sunShade(pw = positionWorld, nw = normalWorld) {
  if (SUN_OFF) return float(1);
  const [x, y, z] = LIGHT.dir, a = LIGHT.ambient;
  const nl = max(dot(nw, vec3(x, y, z)), 0);
  const direct = nl.mul(1 - a).div(nl.mul(1 - a).add(a));
  return float(1).sub(float(1).sub(sunLit(pw, nw)).mul(direct.mul(SUN_SHADOW.depth).min(.55)).mul(SUN.k));
}

// THE SAME SHADE ON THE CPU (shadows.js: whether a figure stands in the sun, so it casts a shadow of its own): the fine
// map's view drawn once more, small, its depth as colour, and read back -- sunAt(x, y, z) 1 in the sun, 0 in a
// building's shadow (1 where the map does not reach, or until it has been read)
export const SUN_CPU = { res: 1024, data: null, matrix: new THREE.Matrix4() };   // (exported for the checks)
const CPU = SUN_CPU, _v = new THREE.Vector3();
export function sunAt(x, y, z) {
  if (!CPU.data) return 1;
  _v.set(x, y, z).applyMatrix4(CPU.matrix);
  const u = _v.x * .5 + .5, w = .5 - _v.y * .5;   // (rows as the shader samples them: v down)
  if (u <= 0 || u >= 1 || w <= 0 || w >= 1 || _v.z >= 1) return 1;
  const R = CPU.res, d = CPU.data[(Math.floor(w * R) * R + Math.floor(u * R))];
  return _v.z - SUN_SHADOW.coarse.bias <= d ? 1 : 0;
}
async function readCPU(renderer, scene, cam, groups) {
  const rt = new THREE.RenderTarget(CPU.res, CPU.res, { type: THREE.FloatType, depthBuffer: true });   // (RGBA: a one-channel target drew nothing here)
  const L7 = SUN_SHADOW.layer, mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  mat.colorNode = vec3(depth);
  for (const g of groups) g.traverse((o) => o.layers.enable(L7));
  const over = scene.overrideMaterial, was = renderer.getRenderTarget(), cc = renderer.getClearColor(new THREE.Color()), ca = renderer.getClearAlpha();
  // (the scene's own sky would be drawn as its clear: no background for this, the far plane's 1 where nothing is)
  const bg = scene.background, env = scene.backgroundNode;
  scene.overrideMaterial = mat; scene.background = null; scene.backgroundNode = null; renderer.setClearColor(0xffffff, 1);
  renderer.setRenderTarget(rt); renderer.clear(); renderer.render(scene, cam);
  renderer.setRenderTarget(was); renderer.setClearColor(cc, ca);
  scene.overrideMaterial = over; scene.background = bg; scene.backgroundNode = env;
  for (const g of groups) g.traverse((o) => o.layers.disable(L7));
  const px = await renderer.readRenderTargetPixelsAsync(rt, 0, 0, CPU.res, CPU.res);
  // (one value a texel whatever the format the backend hands back: RED, or RGBA with red first)
  const step = px.length / (CPU.res * CPU.res);
  CPU.data = step === 1 ? px : Float32Array.from({ length: CPU.res * CPU.res }, (_, i) => px[i * step]);
  CPU.matrix.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse);
  rt.dispose(); mat.dispose();
}
// draw these groups (their boxes) from the sun into a map
function bakeMap(renderer, scene, M, groups, boxes) {
  const box = new THREE.Box3();
  for (const b of boxes) box.union(b);
  if (box.isEmpty()) return null;
  const c = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3());
  const R = Math.hypot(size.x, size.z) / 2 + SUN_SHADOW.margin, D = R + size.y + 50;
  const cam = new THREE.OrthographicCamera(-R, R, R, -R, 1, 2 * D + size.y);
  const L = new THREE.Vector3(...LIGHT.dir);
  cam.position.copy(c).addScaledVector(L, D); cam.up.set(0, 1, 0); cam.lookAt(c); cam.updateMatrixWorld(true);
  const L7 = SUN_SHADOW.layer;
  cam.layers.set(L7);
  for (const g of groups) g.traverse((o) => o.layers.enable(L7));
  const over = scene.overrideMaterial, mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  const was = renderer.getRenderTarget();
  scene.overrideMaterial = mat;
  renderer.setRenderTarget(M.rt); renderer.clear(); renderer.render(scene, cam);
  renderer.setRenderTarget(was);
  scene.overrideMaterial = over;
  for (const g of groups) g.traverse((o) => o.layers.disable(L7));
  mat.dispose();
  cam.updateProjectionMatrix();   // (the renderer set its coordinate system: the projection is the one it drew with)
  M.matrix.value.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse);
  return { R, texel: 2 * R / M.res, cam };
}
// draw the casters from the sun, once: the core into the fine map, all of them into the coarse one
export function bakeSunShadow(renderer, scene, groups0) {
  const all = groups0.map((g) => { g.updateMatrixWorld(true); return { g, b: new THREE.Box3().setFromObject(g) }; }).filter((q) => !q.b.isEmpty());
  if (!all.length) return;
  const mid = (k) => all.map((q) => (q.b.min[k] + q.b.max[k]) / 2).sort((a, b) => a - b)[all.length >> 1];
  const mx = mid("x"), mz = mid("z");
  const core = all.filter((q) => Math.hypot((q.b.min.x + q.b.max.x) / 2 - mx, (q.b.min.z + q.b.max.z) / 2 - mz) <= SUN_SHADOW.reach);
  // (the fine map is SIZED by the core but DRAWS every building: its square reaches past the core's circle, and a mill
  //  standing inside it undrawn cast nothing there -- the fine map wins wherever it reaches)
  const fine = bakeMap(renderer, scene, FINE, all.map((q) => q.g), core.map((q) => q.b));
  const coarse = bakeMap(renderer, scene, COARSE, all.map((q) => q.g), all.map((q) => q.b));
  SUN.baked = true; SUN.k.value = 1;   // (on from the start: the frame's tick eases it by the hour and the weather)
  if (fine) readCPU(renderer, scene, fine.cam, all.map((q) => q.g)).catch((e) => console.warn("sun shadows: no CPU copy --", e.message));
  return { R: fine?.R ?? 0, texel: fine?.texel ?? 0, coarseR: coarse?.R ?? 0, coarseTexel: coarse?.texel ?? 0 };
}
