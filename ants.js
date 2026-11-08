// ANTHILLS AND THEIR ANTS (2026-11-08): a wood ants' mound -- a dome of pine needles and twigs heaped knee-high at a
// forest's edge or in a sunny clearing -- and the ants round it: hundreds milling over its surface, and files of them
// along the TRAILS that run out from it into the grass, out and back, to the trees they milk. Out in warm daylight; at
// night, in the rain, on a frosty morning and while snow lies they are in (the mound stays). As the bees (bees.js), each
// ant is placed by the GPU from the time and its own seeds -- one mesh, one draw for every ant in the world.
//
// AN ANT reads as an ant close up: a card lying ON the ground (not facing the eye: an ant is flat to what it walks on),
// turned along the way it goes, its every corner set on the ground's own height -- so it lies on the slope of the mound
// or the bank it is crossing -- with an ant drawn on it per pixel: the black gaster, the waist, the red-brown thorax and
// head, six legs stepping in the alternating tripods ants walk on, the elbowed antennae. 1.6 cm a card, ~1.1 cm an ant.
//   Where the ground is: the DRAWN ground (burrows.js terrainSampler -- the terrain's tiles stray from groundH by up to
// 15 cm, more than an ant's height many times over), sampled once onto a small height patch round each mound (a float
// texture, a row of patches) that the vertex stage reads bilinearly; the mound's dome is the same formula here and in the
// mound's mesh. Farther than a metre they are drawn a little larger than life, at most ANTS.grow times (a few cm);
// further than ANTS.far from the eye they are not drawn (a speck that would only shimmer).
//
// What a mound is (its size, its colours, how many ants, how far its trails go) is its asset: assets/nature/anthill.json.
//
//   const ants = createAnts(scene, hills, { seed, spec, trailOk })   // hills: [{ x, z }] -- the mounds' middles; trailOk(x, z)
//   ants.ground(hAt)                                        // the drawn ground arrived: the mounds and the patches built
//   ants.update(t, { out, camera })                         // out 0 all in .. 1 all out
import * as THREE from "three";
import { attribute, uniform, varying, texture, wgslFn, uv, positionWorld, cameraPosition, vec3, vec4, float } from "three/tsl";
import { rng } from "./flora.js";
import { boundTo } from "./bounds.js";
import { snowyLit } from "./windowframes.js";

const TRAIL_WIND = [.12, .04];   // (radians: how a trail winds -- the shader's antTrailAng and the worn path's)
export const ANTS = { legible: 1.0, grow: 2.5, mound: 150, trail: 900, trails: [4, 7], reach: [5, 11], size: .016, speed: [.025, .05], far: 16, patch: 64, lift: .007,
                      R: [.75, 1.1], H: [.45, .75], needle: "#7a5634", dark: "#4a3220", litter: "#6d5a3c" };

// the mound's dome over the ground at plan distance rho from its middle -- the SAME in the mesh and in the ants' shader
export const domeAt = (rho, R, H) => H * Math.pow(Math.max(0, 1 - (rho / R) ** 2), .7);

// THE MOUND: a dome of needles (the shape: domeAt) with a few lumps, its foot ringed by a thin skirt of litter running out
// and under the ground -- on the drawn ground hAt. -> { P, C, I } (world)
export function anthillMesh(h, hAt, spec = {}, seed = 1) {
  const r = rng(seed * 59 + 3), P = [], C = [], I = [];
  const nd = new THREE.Color(spec.needle ?? ANTS.needle), dk = new THREE.Color(spec.dark ?? ANTS.dark), lt = new THREE.Color(spec.litter ?? ANTS.litter), c = new THREE.Color();
  const NR = 18, NA = 44, ph = [r() * 6.28, r() * 6.28];
  const rings = [];
  for (let i = 0; i <= NR; i++) rings.push((i / NR) ** 1.15 * h.R);
  rings.push(h.R * 1.18, h.R * 1.4, h.R * 1.48);   // the litter skirt, its edge under the ground
  rings.forEach((rho0, i) => {
    for (let k = 0; k < NA; k++) {
      // (the litter's edge ragged: it runs out farther here, less there, into the grass)
      const a = k / NA * Math.PI * 2, rho = i > NR ? h.R + (rho0 - h.R) * (1 + .45 * Math.sin(a * 3 + ph[0]) + .3 * Math.sin(a * 7 + ph[1])) : rho0;
      const x = h.x + Math.cos(a) * rho, z = h.z + Math.sin(a) * rho;
      const lump = rho < h.R ? .006 * Math.sin(a * 5 + ph[0] + rho * 9) * Math.sin(rho * 13 + ph[1]) : 0;
      const skirt = i > NR ? [.016, .004, -.03][i - NR - 1] : .01 * Math.min(1, (rho / h.R) ** 4);   // (kept clear of the drawn ground's facets)
      const y = hAt(x, z) + domeAt(rho, h.R, h.H) + lump + skirt;
      const u = rho / h.R;
      if (i > NR) c.copy(lt); else c.copy(nd).lerp(dk, .35 * (1 - u) * (.5 + .5 * Math.sin(a * 3 + ph[1])) + .15 * r());
      P.push(x, y, z); C.push(c.r, c.g, c.b);
    }
  });
  for (let i = 0; i < rings.length - 1; i++) for (let k = 0; k < NA; k++) {
    const k1 = (k + 1) % NA, a = i * NA + k, b = i * NA + k1, d = (i + 1) * NA + k, e = (i + 1) * NA + k1;
    I.push(a, b, d, b, e, d);
  }
  return { P, C, I };
}

// the needles' look per pixel: short streaks in every direction, lighter and darker (a few cells deep)
const needles = wgslFn(`
  fn antNeedles(p: vec3<f32>) -> f32 {
    var v = 0.0;
    for (var o: i32 = 0; o < 3; o = o + 1) {
      let q = p.xz * 42.0 + vec2<f32>(p.y * 31.0, -p.y * 27.0) + vec2<f32>(f32(o) * 17.31, f32(o) * 5.17);
      let cl = floor(q);
      let f = fract(q) - 0.5;
      let h = fract(sin(dot(cl, vec2<f32>(127.1, 311.7))) * 43758.5453);
      let a = h * 6.2832;
      let d = vec2<f32>(cos(a), sin(a));
      let s = smoothstep(0.1, 0.0, abs(dot(f, vec2<f32>(-d.y, d.x)))) * smoothstep(0.5, 0.3, abs(dot(f, d)));
      v = v + s * (fract(h * 13.7) - 0.45);
    }
    return 0.9 + 0.75 * v;
  }
`);
export function anthillMaterial() {
  const m = snowyLit();
  m.colorNode = m.colorNode.mul(needles({ p: positionWorld }));
  return m;
}

// THE ANTS' PLACE: the drawn ground from the mound's patch (bilinear), the dome over it; where an ant is on its trail
// or on the mound at time t; the card's corner laid on that ground along its way
const PATCH = ANTS.patch;
const antWGSL = wgslFn(`
  fn antCorner(t: f32, a0: vec4<f32>, a1: vec4<f32>, a2: vec4<f32>, a3: vec4<f32>, c: vec2<f32>, out: f32, cam: vec3<f32>, far: f32, hm: texture_2d<f32>) -> vec3<f32> {
    let p = antXZ(t, a0, a1, a2);
    let q = antXZ(t + 0.3, a0, a1, a2);
    var dir = q - p;
    if (dot(dir, dir) < 1e-10) { dir = vec2<f32>(cos(a0.w), sin(a0.w)); }
    dir = normalize(dir);
    let side = vec2<f32>(-dir.y, dir.x);
    let near = step(distance(cam.xz, p), far);
    // (true size within ANTS.legible metres of the eye; past it drawn larger with the distance -- a 1 cm ant is a speck
    //  at eye height, and a trail of specks does not read -- but at most ANTS.grow times (2.5: a 2.8 cm ant): grown
    //  without a cap, the trails' ants 8 m off were 10 cm, mice in a file; past ~7 m they shrink to specks, and are not
    //  drawn beyond ANTS.far)
    let y0 = antY(p, a0, a2, a3, hm);
    let grow = clamp(distance(cam, vec3<f32>(p.x, y0, p.y)) / ${ANTS.legible.toFixed(2)}, 1.0, ${ANTS.grow.toFixed(2)});
    let s = a3.y * grow * step(a2.x, out) * near;
    let xz = p + dir * c.x * s + side * c.y * s * 0.85;
    return vec3<f32>(xz.x, antY(xz, a0, a2, a3, hm) + ${ANTS.lift} * grow, xz.y);
  }
  fn antXZ(t: f32, a0: vec4<f32>, a1: vec4<f32>, a2: vec4<f32>) -> vec2<f32> {
    let R = a2.z;
    if (a2.y > 0.5) {
      // a trail ant: out to the trail's end and back, the trail winding; out on one side of it, home on the other
      let L = a1.x;
      let k = fract(t * a1.z / (2.0 * L) + a1.w);
      let l = R * 0.35 + (L - R * 0.35) * (1.0 - abs(1.0 - 2.0 * k));
      let ang = antTrailAng(a0.w, l);   // (the trail's own winding: every ant on it keeps to it, its worn path drawn under them)
      let d = vec2<f32>(cos(ang), sin(ang));
      let lane = a1.y * select(1.0, -1.0, k > 0.5) + 0.012 * sin(t * 1.7 + a1.w * 40.0);
      return a0.xy + d * l + vec2<f32>(-d.y, d.x) * lane;
    }
    // a mound ant: wandering over the dome, round and in and out
    let w = t * a1.z / R;
    let rho = R * (0.1 + 0.82 * (0.5 + 0.5 * sin(w * 0.41 + a1.w * 6.283)));
    let psi = a0.w + w * select(-1.0, 1.0, a1.y > 0.0) + 0.7 * sin(w * 0.53 + a1.w * 12.0);
    return a0.xy + vec2<f32>(cos(psi), sin(psi)) * rho;
  }
  fn antTrailAng(th: f32, l: f32) -> f32 { return th + ${TRAIL_WIND[0]} * sin(l * 0.55 + th * 7.0) + ${TRAIL_WIND[1]} * sin(l * 2.3 + th * 13.0); }
  fn antY(xz: vec2<f32>, a0: vec4<f32>, a2: vec4<f32>, a3: vec4<f32>, hm: texture_2d<f32>) -> f32 {
    let half = a3.z;
    let n = ${PATCH}.0;
    let fu = clamp((xz.x - a0.x + half) / (2.0 * half) * (n - 1.0), 0.0, n - 1.001);
    let fv = clamp((xz.y - a0.y + half) / (2.0 * half) * (n - 1.0), 0.0, n - 1.001);
    let i = i32(floor(fu));
    let j = i32(floor(fv)) + i32(a0.z + 0.5) * ${PATCH};
    let a = fu - floor(fu);
    let b = fv - floor(fv);
    let h00 = textureLoad(hm, vec2<i32>(i, j), 0).r;
    let h10 = textureLoad(hm, vec2<i32>(i + 1, j), 0).r;
    let h01 = textureLoad(hm, vec2<i32>(i, j + 1), 0).r;
    let h11 = textureLoad(hm, vec2<i32>(i + 1, j + 1), 0).r;
    let g = mix(mix(h00, h10, a), mix(h01, h11, a), b);
    let rho = distance(xz, a0.xy) / a2.z;
    return g + a3.w * pow(max(0.0, 1.0 - rho * rho), 0.7);
  }
`);
// THE ANT drawn on its card: q the card's uv (x along: the tail at 0, the head at 1), gait its legs' phase
const antShade = wgslFn(`
  fn antShade(q0: vec2<f32>, gait: f32) -> vec4<f32> {
    let p = (q0 - vec2<f32>(0.5)) * 2.0;
    let gas = length((p - vec2<f32>(-0.44, 0.0)) / vec2<f32>(0.33, 0.24));
    let pet = length((p - vec2<f32>(-0.09, 0.0)) / vec2<f32>(0.07, 0.065));
    let tho = length((p - vec2<f32>(0.11, 0.0)) / vec2<f32>(0.2, 0.1));
    let hea = length((p - vec2<f32>(0.44, 0.0)) / vec2<f32>(0.15, 0.14));
    var leg = 1.0e3;
    for (var i: i32 = 0; i < 3; i = i + 1) {
      let fi = f32(i);
      let root = vec2<f32>(0.18 - fi * 0.08, 0.0);
      for (var s: i32 = 0; s < 2; s = s + 1) {
        let sg = select(-1.0, 1.0, s == 1);
        let swing = 0.32 * sin(gait + 3.14159 * f32((i + s) % 2));
        let a = 0.85 + fi * 0.8 + swing;
        let knee = root + vec2<f32>(cos(a - 0.35), sg * sin(a - 0.35)) * 0.24;
        let tip = knee + vec2<f32>(cos(a + 0.25), sg * sin(a + 0.25)) * 0.3;
        leg = min(leg, min(antSeg(p, root, knee), antSeg(p, knee, tip)));
      }
    }
    var ant = 1.0e3;
    for (var s: i32 = 0; s < 2; s = s + 1) {
      let sg = select(-1.0, 1.0, s == 1);
      let b0 = vec2<f32>(0.53, sg * 0.05);
      let e = vec2<f32>(0.66, sg * 0.15);
      let tip = vec2<f32>(0.86, sg * 0.21 + 0.02 * sin(gait * 0.5 + sg));
      ant = min(ant, min(antSeg(p, b0, e), antSeg(p, e, tip)));
    }
    let body = min(min(gas, pet), min(tho, hea));
    let onBody = step(body, 1.0);
    let onLeg = step(leg, 0.055) + step(ant, 0.04);
    let a = min(1.0, onBody + onLeg);
    let red = vec3<f32>(0.4, 0.15, 0.06);
    let black = vec3<f32>(0.06, 0.045, 0.035);
    var col = select(red, black, gas < 1.0 || (hea < 0.6 && p.x > 0.5));
    col = select(col, vec3<f32>(0.12, 0.07, 0.045), onBody < 0.5);
    let sheen = smoothstep(0.7, 0.0, length((p - vec2<f32>(-0.48, 0.05)) / vec2<f32>(0.2, 0.1))) * 0.25;
    return vec4<f32>(col + vec3<f32>(sheen), a);
  }
  fn antSeg(p: vec2<f32>, a: vec2<f32>, b: vec2<f32>) -> f32 {
    let pa = p - a;
    let ba = b - a;
    let h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h);
  }
`);

// THE TRAILS' WORN PATHS: a strip of trodden litter along each trail, the way the shader's ants walk it (antTrailAng),
// from the mound's foot to the trail's end, narrowing out and its ends sunk into the ground -- added to the mound's mesh
function trailPaths(G, h, hAt, spec) {
  const c = new THREE.Color(spec.litter ?? ANTS.litter).multiplyScalar(.75), c2 = new THREE.Color();
  for (const tr of h.trails) {
    const l0 = h.R * .9, n = Math.max(4, Math.ceil((tr.L - l0) / .12)), b0 = G.P.length / 3;
    for (let j = 0; j <= n; j++) {
      const l = l0 + (tr.L + .2 - l0) * j / n, ang = tr.th + TRAIL_WIND[0] * Math.sin(l * .55 + tr.th * 7) + TRAIL_WIND[1] * Math.sin(l * 2.3 + tr.th * 13);
      const dx = Math.cos(ang), dz = Math.sin(ang), w = .045 * (1 - .45 * j / n) * (1 + .25 * Math.sin(l * 9 + tr.th * 5));
      const end = j === 0 || j === n ? -.02 : .0025;
      for (const sd of [-1, 1]) {
        const x = h.x + dx * l - dz * w * sd, z = h.z + dz * l + dx * w * sd;
        G.P.push(x, hAt(x, z) + end, z); c2.copy(c).multiplyScalar(.85 + .3 * Math.abs(Math.sin(l * 17 + sd))); G.C.push(c2.r, c2.g, c2.b);
      }
    }
    for (let j = 0; j < n; j++) { const a = b0 + j * 2; G.I.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
  }
}

export function createAnts(scene, hills, { seed = 1, spec = {}, trailOk = null } = {}) {
  const A = { ...ANTS, ...(spec.ants ?? {}) }, r = rng(seed * 37 + 5);
  // (the asset's R and H: [least, most] -- or one number)
  const span = (v, d) => { const q = v ?? d; return Array.isArray(q) ? q[0] + r() * (q[1] - q[0]) : q; };
  const H = hills.map((h, i) => ({ ...h, i, R: h.R ?? span(spec.R, A.R), H: h.H ?? span(spec.H, A.H) }));
  const ants = [];
  for (const h of H) {
    const nT = A.trails[0] + Math.floor(r() * (A.trails[1] - A.trails[0] + 1)), trails = [];
    for (let k = 0; k < nT; k++) {   // (a trail ends where the ground stops being fit for it: water, a wall, a road -- trailOk)
      const th = (k + r() * .7) / nT * Math.PI * 2;
      let L = A.reach[0] + r() * (A.reach[1] - A.reach[0]);
      if (trailOk) for (let s = h.R; s < L; s += .4) if (!trailOk(h.x + Math.cos(th) * s, h.z + Math.sin(th) * s)) { L = s - .4; break; }
      if (L > h.R + 1.5) trails.push({ th, L });
    }
    if (!trails.length) trails.push({ th: r() * 6.28, L: h.R + 1.5 });
    h.trails = trails; h.half = Math.max(...trails.map((q) => q.L)) + 1;
    for (let i = 0; i < A.mound; i++) ants.push({ h, kind: 0, th: r() * 6.283, L: 0, lane: r() < .5 ? -1 : 1, sp: A.speed[0] + r() * (A.speed[1] - A.speed[0]), ph: r(), share: r() * .35, s2: r() });
    for (let i = 0; i < A.trail; i++) {
      const tr = trails[i % trails.length];
      ants.push({ h, kind: 1, th: tr.th, L: tr.L, lane: .018 + r() * .014, sp: A.speed[0] + r() * (A.speed[1] - A.speed[0]), ph: r(), share: .3 + r() * .7, s2: r() });
    }
  }
  if (!ants.length) return { count: 0, hills: H, ground() {}, update() {}, mounds: null };
  const N = ants.length, a0 = new Float32Array(N * 16), a1 = new Float32Array(N * 16), a2 = new Float32Array(N * 16), a3 = new Float32Array(N * 16), cr = new Float32Array(N * 8), idx = new Uint32Array(N * 6);
  ants.forEach((q, i) => {
    for (let v = 0; v < 4; v++) {
      const o = (i * 4 + v) * 4;
      a0.set([q.h.x, q.h.z, q.h.i, q.th], o); a1.set([q.L, q.lane, q.sp, q.ph], o);
      a2.set([q.share, q.kind, q.h.R, q.s2], o); a3.set([0, A.size, q.h.half, q.h.H], o);
      cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2);
    }
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 12), 3));
  for (const [nm, arr] of [["antA", a0], ["antB", a1], ["antC", a2], ["antD", a3]]) g.setAttribute(nm, new THREE.BufferAttribute(arr, 4));
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  // the height patches: one PATCH x PATCH square a mound, stacked -- filled when the drawn ground has come (ground())
  const hdata = new Float32Array(PATCH * PATCH * H.length);
  const htex = new THREE.DataTexture(hdata, PATCH, PATCH * H.length, THREE.RedFormat, THREE.FloatType);
  htex.needsUpdate = true;
  const U = { t: uniform(0), out: uniform(0) };
  const B = attribute("antB", "vec4");
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  mat.positionNode = antWGSL({ t: U.t, a0: attribute("antA", "vec4"), a1: B, a2: attribute("antC", "vec4"), a3: attribute("antD", "vec4"),
                               c: attribute("corner", "vec2"), out: U.out, cam: cameraPosition, far: float(A.far), hm: texture(htex) });
  const gait = varying(U.t.mul(B.z).mul(2 * Math.PI / .011).add(B.w.mul(40)));   // (a stride about a body's length)
  const look = antShade({ q0: uv(), gait });
  mat.colorNode = look.xyz;
  mat.opacityNode = look.w;
  mat.alphaTest = .5;
  const mesh = new THREE.Mesh(g, mat);
  boundTo(mesh, H.map((h) => ({ x: h.x, y: 0, z: h.z })), Math.max(...H.map((h) => h.half)) + 2);
  mesh.name = "ants"; mesh.visible = false;
  mesh.userData.noMerge = true; mesh.userData.cut = true;
  scene.add(mesh);
  let ready = false, mounds = null;
  return {
    count: N, mesh, hills: H, get mounds() { return mounds; },
    // the drawn ground is here (hAt: burrows.js terrainSampler's at): the mounds' meshes and the ants' height patches
    ground(hAt, material = anthillMaterial()) {
      H.forEach((h) => {
        for (let j = 0; j < PATCH; j++) for (let i = 0; i < PATCH; i++)
          hdata[(h.i * PATCH + j) * PATCH + i] = hAt(h.x - h.half + 2 * h.half * i / (PATCH - 1), h.z - h.half + 2 * h.half * j / (PATCH - 1));
      });
      htex.needsUpdate = true;
      // (the bound's middle at the ground's height: it was put at y 0)
      const ys = H.map((h) => hAt(h.x, h.z)), my = ys.reduce((a, b) => a + b, 0) / ys.length;
      g.boundingSphere.center.y = my; g.boundingSphere.radius += Math.max(...ys.map((y) => Math.abs(y - my)));
      mounds = H.map((h) => {
        const G = anthillMesh(h, hAt, spec, seed + h.i), geo = new THREE.BufferGeometry(), y0 = hAt(h.x, h.z);
        trailPaths(G, h, hAt, spec);   // (the trails worn into the grass: no stalks over them, the ants on them)
        // (in its own frame, its base at its middle's ground: the grass mask reads a prop's height over its base)
        const P = G.P.map((v, k) => k % 3 === 0 ? v - h.x : k % 3 === 1 ? v - y0 : v - h.z);
        geo.setAttribute("position", new THREE.Float32BufferAttribute(P, 3));
        geo.setAttribute("color", new THREE.Float32BufferAttribute(G.C, 3));
        geo.setIndex(G.I); geo.computeVertexNormals();
        for (let k = 0; k < 44; k++) geo.attributes.normal.setXYZ(k, 0, 1, 0);   // (the top: one point, its normal straight up -- not a star)
        const m = new THREE.Mesh(geo, material);
        m.position.set(h.x, y0, h.z); m.updateMatrix(); m.matrixAutoUpdate = false; m.updateMatrixWorld(true);
        m.name = "anthill"; m.userData.noMerge = true;
        scene.add(m);
        return m;
      });
      ready = true;
      return mounds;
    },
    update(time, { out = 1 } = {}) { U.t.value = time; U.out.value = out; mesh.visible = ready && out > .01; },
  };
}
