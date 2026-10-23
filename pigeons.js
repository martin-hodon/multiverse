// PIGEONS on the roofs: small flocks sitting along the ridges -- blue-grey rock doves and a few white ones -- each
// bobbing its head now and then; every so often one takes off, wheels round over the lane on beating wings and comes
// back to its place. Each bird is one card facing the eye: sitting, a pigeon's side view (body, head, tail); flying,
// the shape from below (spread wings, flapping). When it flies and where, from the time and its own seeds alone, on
// the GPU. One mesh, one draw.
// STARTLED: a fright -- the bell striking the hour, a clap of thunder, fireworks, a stone landing near -- puts every
// pigeon in its reach up at once, the nearest first (a ripple out from the fright), round a wider, higher loop, home
// again ten seconds on; the clatter of their wings if you are near.
//
//   const pigeons = createPigeons(scene, ridges, { seed, audio, camera, share })   // ridges: [{ a: [x, z], b: [x, z], y, share? }] (architecture.js lifeOf)
//   (lines on the ground do as well: the market square's flock pecks about the paving, crows the autumn stubble -- index.html)
//   pigeons.update(t, { dark })                               // (at night they sleep: no flights of their own)
//   pigeons.scare({ x, z, r, delay })                         // a fright r metres round x, z (r 0: the whole town), delay seconds from now
import * as THREE from "three";
import { boundTo } from "./bounds.js";
import { attribute, uniform, vec2, vec3, vec4, float, uv, sin, cos, fract, floor, smoothstep, mix, step, abs, max, min, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { rng } from "./flora.js";
import { SR, toBuffer, play } from "./dsp.js";

export const PIGEONS = { roofs: .45, per: [3, 8], every: [35, 90], flight: 7, white: .15, startled: 10, ripple: 25 };   // (ripple: m a second the fright spreads)

const _p = new THREE.Vector3();

export function createPigeons(scene, ridges, { seed = 1, audio = () => null, camera = null, share = PIGEONS.roofs, colour = [.42, .45, .52], white = PIGEONS.white, name = "pigeons" } = {}) {   // share: of the ridges, how many have birds; colour, white: theirs (crows: black, none white)
  const r = rng(seed * 89 + 5);
  const birds = [];
  for (const rd of ridges) {
    if (r() > (rd.share ?? share)) continue;   // (a ridge may say its own: a wall's merlons, a few of them)
    const dx = rd.b[0] - rd.a[0], dz = rd.b[1] - rd.a[1], len = Math.hypot(dx, dz);
    const n = Math.min(Math.floor(len / .4), PIGEONS.per[0] + Math.floor(r() * (PIGEONS.per[1] - PIGEONS.per[0])));
    let s = .1 + r() * .3;
    for (let k = 0; k < n && s < .95; k++) {
      birds.push([rd.a[0] + dx * s, rd.y, rd.a[1] + dz * s, r(), r(), r() < white ? 1 : 0, dx / len, dz / len]);
      s += (.3 + r() * .6) / len;
    }
  }
  if (!birds.length) return { count: 0, update() {}, scare() { return 0; } };
  const N = birds.length, at = new Float32Array(N * 16), sd = new Float32Array(N * 16), cr = new Float32Array(N * 8), idx = new Uint32Array(N * 6);
  birds.forEach(([x, y, z, s1, s2, white, ax, az], i) => {
    for (let v = 0; v < 4; v++) {
      at.set([x, y, z, white], (i * 4 + v) * 4); sd.set([s1, s2, ax, az], (i * 4 + v) * 4);
      cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2);
    }
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 12), 3));
  g.setAttribute("perch", new THREE.BufferAttribute(at, 4));
  g.setAttribute("seedA", new THREE.BufferAttribute(sd, 4));
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  const U = { t: uniform(0), awake: uniform(1), fright: uniform(new THREE.Vector4(0, 0, 0, -1e4)) };   // (x, z, reach, when)
  const A = attribute("perch", "vec4"), S = attribute("seedA", "vec4"), C = attribute("corner", "vec2");
  // its flights: one every `every` seconds (its own), lasting `flight`; f 0..1 through one, 0 when sitting
  const period = S.x.mul(PIGEONS.every[1] - PIGEONS.every[0]).add(PIGEONS.every[0]);
  const into = fract(U.t.div(period).add(S.y)).mul(period);
  const own = step(into, PIGEONS.flight).mul(U.awake);
  // ...or startled: up as the fright reaches it (a little late or early, as each bird is), for a longer flight
  const Fr = U.fright, away = vec2(A.x.sub(Fr.x), A.z.sub(Fr.y)).length();
  const since = U.t.sub(Fr.w).sub(away.div(PIGEONS.ripple)).sub(S.y.mul(.6));
  const scared = step(away, Fr.z).mul(step(0, since)).mul(step(since, PIGEONS.startled));
  const flying = max(own, scared), f = mix(min(into.div(PIGEONS.flight), 1), since.div(PIGEONS.startled).clamp(0, 1), scared);
  // the flight: off the ridge, round a loop out over one side and back (up and down again), landing where it was
  const side = S.y.lessThan(.5).select(float(1), float(-1)), ang = f.mul(6.283);
  const nx = S.w.negate(), nz = S.z;                                   // (the ridge's normal on the ground)
  const R = S.x.mul(5).add(5).mul(scared.mul(.8).add(1));
  const loop = vec3(nx.mul(sin(ang.mul(.5)).mul(R).mul(side)).add(S.z.mul(sin(ang).mul(R.mul(.5)))),
                    sin(f.mul(3.1416)).mul(S.y.mul(4).add(3)).mul(scared.mul(.7).add(1)),
                    nz.mul(sin(ang.mul(.5)).mul(R).mul(side)).add(S.w.mul(sin(ang).mul(R.mul(.5)))));
  const P = A.xyz.add(vec3(0, .12, 0)).add(loop.mul(flying));
  // sitting: the head bobs now and then (a peck at nothing); the card faces the eye, its size a pigeon's
  const size = mix(float(.34), float(.62), flying);
  const view = cameraViewMatrix.mul(vec4(P, 1));
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(view.add(vec4(C.mul(size), 0, 0)));
  const vFly = flying, q = uv().sub(.5).mul(2);
  // the sitting bird (side view): a plump body, a small head up front (bobbing), a tail behind
  const bob = smoothstep(.85, 1, sin(U.t.mul(S.x.mul(2).add(1.5)).add(S.y.mul(40)))).mul(.12);
  const facing = S.x.lessThan(.5).select(float(1), float(-1));        // (which way along the ridge it looks)
  const qx = q.x.mul(facing);
  const body = smoothstep(1, .9, vec2(qx.add(.05).div(.55), q.y.add(.25).div(.36)).length());
  const head = smoothstep(1, .85, vec2(qx.sub(.42).div(.2), q.y.sub(.12).add(bob).div(.2)).length());
  const tail = step(qx, -.4).mul(step(-.9, qx)).mul(step(abs(q.y.add(.32)), qx.add(.9).mul(.25)));
  const sit = max(max(body, head), tail);
  // the flying bird (from below): a body and two wings, beating -- their tips up and down
  const beat = sin(U.t.mul(14).add(S.x.mul(30)));
  const wingY = abs(q.x).mul(beat.mul(.55));
  const wing = step(abs(q.y.sub(wingY)), smoothstep(1, .1, abs(q.x)).mul(.22)).mul(step(abs(q.x), .95));
  const fbody = smoothstep(1, .8, vec2(q.x.div(.16), q.y.div(.45)).length());
  const fly = max(wing, fbody);
  const shape = mix(sit, fly, vFly);
  const grey = mix(vec3(...colour), vec3(.9, .9, .88), A.w);
  // (a sitting pigeon's iridescent neck, its darker wing bars; a flier dark against the sky)
  mat.colorNode = mix(mix(grey, grey.mul(vec3(.75, .9, .8)), head.mul(.6)).mul(smoothstep(-.6, .2, q.y).mul(.25).add(.75)), grey.mul(.7), vFly);
  mat.opacityNode = shape;
  mat.alphaTest = .5;
  const mesh = new THREE.Mesh(g, mat);
  boundTo(mesh, birds, 22); mesh.name = name;   // (their loops: up to ~18 m out, ~12 up) mesh.userData.noMerge = true; mesh.userData.cut = true;
  scene.add(mesh);
  // the wings' clatter: a burst of claps, fast at the take-off and thinning out, as loud as the nearest startled bird is near
  let clatter = null;
  const flapSound = (d, delay) => {
    const ctx = audio();
    if (!ctx || d > 45) return;
    clatter ??= toBuffer(Float32Array.from({ length: Math.round(1.6 * SR) }, (_, i) => { const t = i / SR, k = Math.exp(-t * 1.8);
      return k * (Math.random() * 2 - 1) * Math.pow(Math.max(0, Math.sin(2 * Math.PI * (11 - 4 * t) * t + Math.sin(t * 37))), 6); }));
    const g = ctx.createGain(); g.gain.value = Math.min(.6, 6 / Math.max(d, 3)) * .5; g.connect(ctx.destination);
    play(ctx, clatter, { dest: g, at: ctx.currentTime + delay, rate: .9 + Math.random() * .2 });
  };
  return {
    count: N, birds, mesh,
    update(t, { dark = 0 } = {}) { U.t.value = t; U.awake.value = dark < .5 ? 1 : 0; },
    // a fright: every bird within r of x, z (r 0: all of them) startled `delay` seconds from now; how many it put up
    scare({ x = 0, z = 0, r = 0, delay = 0 } = {}) {
      const reach = r || 1e6, F = U.fright.value;
      if (U.t.value - F.w < PIGEONS.startled) return 0;   // (still up from the last fright)
      let n = 0, dmin = 1e9;
      for (const b of birds) if (Math.hypot(b[0] - x, b[2] - z) < reach) {
        n++;
        if (camera) dmin = Math.min(dmin, camera.position.distanceTo(_p.set(b[0], b[1], b[2])));
      }
      if (!n) return 0;
      F.set(x, z, reach, U.t.value + delay);
      flapSound(dmin, delay + (r ? 0 : .3));
      return n;
    },
  };
}
