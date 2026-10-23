// A BONFIRE ON THE GREEN: lit at nightfall in a ring of stones, its logs crossed, flames licking up from them -- tongues
// that sway and flicker, white-gold at the root, orange, red at the tips -- embers rising and winking out above it, a
// pool of firelight on the grass round it that breathes with the flames (its crackle: environment.js's fire, which
// index.html feeds the distance to it while it burns). By day the ring stands cold. The light is in the night's glow scene (index.html: drawn after the darkening, so it shines), one
// mesh for the pool, the flames and the embers -- placed and shaded on the GPU from the time -- and one for the stones
// and the logs. Logs to sit on round it: `seats` (index.html seats villagers on them at night).
//
//   const fire = createBonfire(scene, glowScene, { at: [x, y, z], seed, groundH })
//   fire.update(t, { lit })   // lit 0 out .. 1 burning
//   fire.seats                // [{ x, y, z, face }] a seat's top and the way one sitting there faces (the fire)
//   fire.floor                // [x, z]: the open ground in the seats' gap, by the fire (where people dance)
import * as THREE from "three";
import { boundTo } from "./bounds.js";
import { attribute, uniform, vec3, vec4, float, uv, sin, fract, smoothstep, mix, abs, pow, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { rng } from "./flora.js";
import { blockMesh } from "./blocks.js";

export const BONFIRE = { flames: 7, embers: 40, pool: 13, ring: .95, seats: 5, seatR: 2.6, ear: 35 };   // ear: how far its crackle carries

export function createBonfire(scene, glowScene, { at, seed = 1, groundH = () => at[1] }) {
  const r = rng(seed * 59 + 3), [X, Y, Z] = at;
  // ---- the cold parts: a ring of stones, the crossed logs, the log seats round it ----------------------------------
  const blocks = [];
  const box = (cx, cy, cz, sx, sy, sz, yaw, colour, shape) => blocks.push({ at: [cx, cy, cz], size: [sx, sy, sz], yaw, colour, shape });
  for (let k = 0; k < 11; k++) {   // the stones
    const a = k / 11 * Math.PI * 2 + r() * .2, s = .22 + r() * .12, g = .42 + r() * .15;
    box(X + Math.cos(a) * BONFIRE.ring, Y + s * .3, Z + Math.sin(a) * BONFIRE.ring, s, s * .7, s * .8, a, [g, g * .98, g * .93]);
  }
  for (let k = 0; k < 4; k++) {    // the logs, crossed over the fire, charred at the middle
    const a = k / 4 * Math.PI + r() * .3;
    box(X, Y + .1 + k * .06, Z, 1.25, .13, .13, a, k % 2 ? [.24, .15, .09] : [.13, .09, .07], "log");
  }
  const seats = [];
  for (let k = 0; k < BONFIRE.seats; k++) {   // log seats round it, a gap toward the town
    const a = (k + .5) / (BONFIRE.seats + 1) * Math.PI * 2 + r() * .15, sx = X + Math.cos(a) * BONFIRE.seatR, sz = Z + Math.sin(a) * BONFIRE.seatR, gy = groundH(sx, sz);
    box(sx, gy + .19, sz, 1.3, .38, .38, -a - Math.PI / 2, [.36, .25, .15], "log");   // (along the ring)
    seats.push({ x: sx, y: gy + .37, z: sz, face: Math.atan2(-(Z - sz), X - sx) });   // (face: toward the fire, the lanes' convention -- cos, -sin)
  }
  scene.add(blockMesh(blocks, "bonfire stones"));
  // ---- the fire: kind 0 the pool of light, 1 a flame, 2 an ember -----------------------------------------------------
  const kinds = [0, ...Array(BONFIRE.flames).fill(1), ...Array(BONFIRE.embers).fill(2)], N = kinds.length;
  const cr = new Float32Array(N * 8), kd = new Float32Array(N * 4), sd = new Float32Array(N * 8), id2 = new Uint32Array(N * 6);
  kinds.forEach((k, i) => {
    const s = [r(), r()];
    for (let v = 0; v < 4; v++) { cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2); kd[i * 4 + v] = k; sd.set(s, (i * 4 + v) * 2); }
    id2.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 12).map((_, j) => [X, Y, Z][j % 3]), 3));
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));
  g.setAttribute("fireKind", new THREE.BufferAttribute(kd, 1));
  g.setAttribute("seedA", new THREE.BufferAttribute(sd, 2));
  g.setIndex(new THREE.BufferAttribute(id2, 1));
  const U = { t: uniform(0), lit: uniform(0) };
  const C = attribute("corner", "vec2"), K = attribute("fireKind", "float"), S = attribute("seedA", "vec2"), O = vec3(X, Y, Z);
  const flick = sin(U.t.mul(11.3)).mul(sin(U.t.mul(7.1).add(1.3))).mul(.1).add(sin(U.t.mul(3.3)).mul(.06)).add(.92);   // (the whole fire's breath)
  // where each corner goes: the pool flat on the grass; a flame standing on the logs, facing the eye, its foot fixed;
  // an ember rising on its own wobbling path, round and round
  const pool = cameraViewMatrix.mul(vec4(O.add(vec3(C.x.mul(BONFIRE.pool), .06, C.y.mul(BONFIRE.pool))), 1));
  const fa = S.x.mul(6.283), fw = S.y.mul(.35).add(.55), fh = S.y.mul(.6).add(1.05).mul(flick);
  const fview = cameraViewMatrix.mul(vec4(O.add(vec3(sin(fa).mul(.22), .12, sin(fa.add(1.57)).mul(.22))), 1));
  const flame = fview.add(vec4(C.x.mul(fw), C.y.add(.5).mul(fh), 0, 0));
  const life = fract(U.t.div(S.y.mul(1.2).add(1.8)).add(S.x));
  const ember = cameraViewMatrix.mul(vec4(O.add(vec3(sin(S.x.mul(40).add(U.t.mul(1.3))).mul(life).mul(.55), life.mul(life.mul(-1.2).add(5.2)).add(.4), sin(S.y.mul(31).add(U.t.mul(1.1))).mul(life).mul(.55))), 1)).add(vec4(C.mul(.07), 0, 0));
  const isPool = K.lessThan(.5), isFlame = K.lessThan(1.5);
  const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false, side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(isPool.select(pool, isFlame.select(flame, ember)));
  // and how each shines
  const q = uv(), d = q.sub(.5).mul(2).length();
  const poolC = vec3(1, .5, .2).mul(pow(smoothstep(1, 0, d), 1.7).mul(.42).mul(flick));
  const y = q.y, x = q.x.sub(.5).mul(2), sway = sin(y.mul(8).sub(U.t.mul(7)).add(S.x.mul(20))).mul(.16).add(sin(y.mul(15).sub(U.t.mul(11)).add(S.y.mul(13))).mul(.07)).mul(y);
  const w = pow(float(1).sub(y), .7).mul(.85).mul(sin(U.t.mul(13).add(S.x.mul(9))).mul(.12).add(.88));
  const body = smoothstep(w, w.mul(.35), abs(x.add(sway)));
  const core = smoothstep(w.mul(.55), 0, abs(x.add(sway))).mul(smoothstep(.75, .05, y));
  const flameC = mix(vec3(1, .78, .3), vec3(.9, .22, .04), smoothstep(.1, .85, y)).mul(body).add(vec3(1, .9, .65).mul(core).mul(.8)).mul(smoothstep(1, .55, y)).mul(.85);
  const emberC = vec3(1, .55, .15).mul(smoothstep(1, 0, d)).mul(smoothstep(1, .55, life)).mul(smoothstep(0, .08, life)).mul(2.2);
  mat.colorNode = isPool.select(poolC, isFlame.select(flameC, emberC)).mul(U.lit);
  mat.opacityNode = float(1);
  const hot = new THREE.Mesh(g, mat);
  boundTo(hot, [[X, Y, Z]], BONFIRE.pool + 6); hot.name = "bonfire"; hot.visible = false; hot.renderOrder = 5;
  glowScene.add(hot);
  // where the seats leave a gap (toward the town): room to dance
  const ga = (BONFIRE.seats + .5) / (BONFIRE.seats + 1) * Math.PI * 2, floor = [X + Math.cos(ga) * (BONFIRE.seatR - .2), Z + Math.sin(ga) * (BONFIRE.seatR - .2)];
  return {
    seats, at, floor,
    update(t, { lit = 0 } = {}) {
      U.t.value = t; U.lit.value = lit;
      hot.visible = lit > .01;
    },
  };
}
