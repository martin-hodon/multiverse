// BEES at the hives: round every skep a dozen of them -- zigzagging about its mouth, and every so often one off to the
// flowers a few metres out and back again, the way bees come and go. Each is a tiny card facing the eye (a striped
// amber body, a blur of wings), placed by the GPU from the time and its own seeds. Out by day in fair weather, in the
// skeps at night and in the rain (the hum is the environment's: environment.js, near the hives). One mesh, one draw.
//
//   const bees = createBees(scene, skeps, { seed })   // skeps: [{ x, y, z }] (a skep's mouth)
//   bees.update(t, { out })                            // out 0 all home .. 1 all flying
import * as THREE from "three";
import { boundTo } from "./bounds.js";
import { attribute, uniform, vec2, vec3, vec4, float, uv, sin, cos, fract, floor, smoothstep, mix, step, abs, max, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { rng } from "./flora.js";

export const BEES = { per: 12, size: .05, forage: [3, 9], trip: [7, 16] };   // forage: metres out a trip goes; trip: seconds it takes

export function createBees(scene, skeps, { seed = 1 } = {}) {
  const r = rng(seed * 29 + 31), bees = [];
  for (const k of skeps) for (let i = 0; i < BEES.per; i++) bees.push([k.x, k.y, k.z, i / BEES.per, r(), r(), r(), r()]);
  if (!bees.length) return { count: 0, update() {} };
  const N = bees.length, at = new Float32Array(N * 16), sd = new Float32Array(N * 16), cr = new Float32Array(N * 8), idx = new Uint32Array(N * 6);
  bees.forEach(([x, y, z, share, a, b, c, e], i) => {
    for (let v = 0; v < 4; v++) { at.set([x, y, z, share], (i * 4 + v) * 4); sd.set([a, b, c, e], (i * 4 + v) * 4); cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2); }
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 12), 3));
  g.setAttribute("skepAt", new THREE.BufferAttribute(at, 4));
  g.setAttribute("beeSeed", new THREE.BufferAttribute(sd, 4));
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  const U = { t: uniform(0), out: uniform(0) };
  const A = attribute("skepAt", "vec4"), S = attribute("beeSeed", "vec4"), C = attribute("corner", "vec2");
  // about the mouth: quick wandering loops half a metre round, jittering
  const t = U.t, ph = S.x.mul(50);
  const near = vec3(sin(t.mul(S.y.mul(2).add(2.2)).add(ph)).mul(.45).add(sin(t.mul(11).add(ph.mul(3))).mul(.06)),
                    sin(t.mul(S.z.mul(1.5).add(1.7)).add(ph.mul(2))).mul(.25).add(.3),
                    cos(t.mul(S.w.mul(2).add(1.9)).add(ph)).mul(.45).add(cos(t.mul(13).add(ph.mul(5))).mul(.06)));
  // ...and a trip: out to the flowers along its own bearing and back, once a period of its own
  const period = S.y.mul(BEES.trip[1] - BEES.trip[0]).add(BEES.trip[0]).mul(2.2);
  const k = fract(t.div(period).add(S.z)), trip = smoothstep(.0, .25, k).mul(smoothstep(.7, .45, k));   // (out, a while there, back)
  const reach = S.w.mul(BEES.forage[1] - BEES.forage[0]).add(BEES.forage[0]), bear = S.x.mul(6.283).add(floor(t.div(period).add(S.z)).mul(2.4));
  const away = vec3(cos(bear).mul(reach), sin(t.mul(3).add(ph)).mul(.3).add(.2), sin(bear).mul(reach)).mul(trip);
  const P = A.xyz.add(near.mul(trip.oneMinus().mul(.8).add(.2))).add(away);
  const on = step(A.w, U.out.mul(1.02));
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(P, 1)).add(vec4(C.mul(BEES.size).mul(on), 0, 0)));
  // the bee: a little striped body, a pale blur of wings above it
  const q = uv().sub(.5).mul(2);
  const body = smoothstep(1, .8, vec2(q.x.div(.62), q.y.add(.15).div(.38)).length());
  const wings = smoothstep(1, .7, vec2(abs(q.x).sub(.25).div(.42), q.y.sub(.35).div(.3)).length()).mul(.55);
  const stripes = step(.5, fract(q.x.mul(2.2).add(.2)));
  mat.colorNode = mix(mix(vec3(.85, .6, .12), vec3(.12, .09, .05), stripes.mul(.8)).mul(body), vec3(.9, .92, .95), wings.mul(body.oneMinus()));
  mat.opacityNode = max(body, wings).mul(on);
  mat.alphaTest = .4;
  const mesh = new THREE.Mesh(g, mat);
  boundTo(mesh, skeps, BEES.forage[1] + 1.5); mesh.name = "bees"; mesh.visible = false;
  mesh.userData.noMerge = true; mesh.userData.cut = true;
  scene.add(mesh);
  return {
    count: N, mesh,
    update(time, { out = 1 } = {}) { U.t.value = time; U.out.value = out; mesh.visible = out > .01; },
  };
}
