// SWALLOWS over the river: little flocks hawking for flies low over the water and the meadows by it -- fast, swooping
// figure-of-eight loops round their own patch, dipping to skim the surface and climbing again, wings flicking between
// glides. Most of them in the afternoon and toward evening (the flies are up), gone at nightfall (the bats' hour) and in
// rain. Each bird is one card facing the eye -- the swallow from below: swept-back pointed wings, a deeply forked tail,
// dark blue-black over a pale throat -- placed and flapped on the GPU from the time and its own seeds. One mesh, one
// draw; their twittering when you are near.
//
//   const swallows = createSwallows(scene, patches, { seed, audio, camera })   // patches: [{ x, y, z, r }] (y: the water's height)
//   swallows.update(t, { amount })   // amount 0 none .. 1 all of them out
import * as THREE from "three";
import { boundTo } from "./bounds.js";
import { attribute, uniform, vec2, vec3, vec4, float, uv, sin, cos, fract, smoothstep, mix, max, step, abs, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { rng } from "./flora.js";
import { SR, toBuffer, play } from "./dsp.js";

export const SWALLOWS = { per: 7, speed: 9, size: .48, ear: 30 };

export function createSwallows(scene, patches, { seed = 1, audio = () => null, camera = null } = {}) {
  const r = rng(seed * 43 + 19), birds = [];
  for (const P of patches) for (let k = 0; k < SWALLOWS.per; k++) birds.push([P.x, P.y, P.z, P.r, r(), r(), r(), k / SWALLOWS.per]);
  if (!birds.length) return { count: 0, update() {} };
  const N = birds.length, at = new Float32Array(N * 16), sd = new Float32Array(N * 16), cr = new Float32Array(N * 8), idx = new Uint32Array(N * 6);
  birds.forEach(([x, y, z, rr, a, b, c, share], i) => {
    for (let v = 0; v < 4; v++) { at.set([x, y, z, rr], (i * 4 + v) * 4); sd.set([a, b, c, share], (i * 4 + v) * 4); cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2); }
    idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 12), 3));
  g.setAttribute("flockAt", new THREE.BufferAttribute(at, 4));   // (not "patch": a reserved word in WGSL)
  g.setAttribute("seedA", new THREE.BufferAttribute(sd, 4));
  g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
  g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  const U = { t: uniform(0), amount: uniform(0) };
  const A = attribute("flockAt", "vec4"), S = attribute("seedA", "vec4"), C = attribute("corner", "vec2");
  // its loop: a figure of eight round the patch (two speeds on the two axes), turned and sized by its own seeds, at a
  // swallow's pace -- the loop's length over its speed is its period; low, with dips that skim the water
  const R = A.w.mul(S.x.mul(.5).add(.6));
  const w = float(SWALLOWS.speed).div(R.mul(2.4)), ph = U.t.mul(w).add(S.y.mul(40)), turn = S.z.mul(6.283);
  const lx = sin(ph).mul(R), lz = sin(ph.mul(2)).mul(R.mul(.45));
  const dip = smoothstep(.75, 1, sin(ph.mul(1.5).add(S.x.mul(9)))).mul(1.6);   // (now and then down to the water)
  const y = sin(ph.mul(.7).add(S.z.mul(5))).mul(1.4).add(2.6).sub(dip).max(.25);
  const P = A.xyz.add(vec3(lx.mul(cos(turn)).sub(lz.mul(sin(turn))), y, lx.mul(sin(turn)).add(lz.mul(cos(turn)))));
  // out only as many as `amount` asks (each bird its own share of the flock)
  const out = step(S.w, U.amount.mul(1.02));
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(P, 1)).add(vec4(C.mul(SWALLOWS.size).mul(out), 0, 0)));
  // the swallow from below: a slim body, long swept wings beating in quick flicks between glides, a forked tail
  const q = uv().sub(.5).mul(2);
  const flick = sin(U.t.mul(19).add(S.y.mul(30))).mul(smoothstep(-.2, .4, sin(U.t.mul(1.3).add(S.x.mul(11)))));   // (beats, then glides)
  const ax = abs(q.x), sweep = ax.mul(ax).mul(.55).sub(flick.mul(ax).mul(.3));          // the wing's line, swept back toward the tips
  const wing = step(abs(q.y.sub(sweep).add(.05)), smoothstep(1, .15, ax).mul(.13)).mul(step(ax, .98));
  const body = smoothstep(1, .85, vec2(q.x.div(.11), q.y.add(.05).div(.42)).length());
  const tailY = q.y.add(.38), fork = step(tailY.negate(), .5).mul(step(0, tailY.negate())).mul(step(abs(abs(q.x).sub(tailY.negate().mul(.28))), .035));
  const shape = max(max(wing, body), fork);
  const throat = smoothstep(.15, -.05, q.y.sub(.12)).mul(smoothstep(.12, .0, ax)).mul(body);
  mat.colorNode = mix(vec3(.08, .1, .2), vec3(.85, .8, .72), throat.mul(.8));
  mat.opacityNode = shape.mul(out);
  mat.alphaTest = .5;
  const mesh = new THREE.Mesh(g, mat);
  boundTo(mesh, patches, Math.max(...patches.map((p) => p.r)) * 1.2 + 6); mesh.name = "swallows"; mesh.visible = false;
  mesh.userData.noMerge = true; mesh.userData.cut = true;
  scene.add(mesh);
  // their twitter: a run of quick bright chirps, now and then, from the nearest flock out
  let buf = null, next = 0;
  const twitter = (t) => {
    const ctx = audio();
    if (!ctx || !camera || t < next) return;
    next = t + 3 + Math.random() * 6;
    let d = 1e9; for (const p of patches) d = Math.min(d, Math.hypot(p.x - camera.position.x, p.z - camera.position.z) - p.r * .5);
    if (d > SWALLOWS.ear) return;
    buf ??= toBuffer(Float32Array.from({ length: Math.round(.9 * SR) }, (_, i) => { const tt = i / SR, k = tt % .11, n = Math.floor(tt / .11);
      const f = 4200 + 900 * Math.sin(n * 2.3) + 2600 * k / .11;
      return (n % 3 === 2 ? 0 : 1) * .3 * Math.exp(-k * 45) * Math.sin(2 * Math.PI * f * k + 3 * Math.sin(2 * Math.PI * 60 * k)); }));
    const gn = ctx.createGain(); gn.gain.value = Math.min(.35, 4 / Math.max(d, 4)) * .4; gn.connect(ctx.destination);
    play(ctx, buf, { dest: gn, rate: .9 + Math.random() * .25 });
  };
  return {
    count: N, mesh,
    update(t, { amount = 0 } = {}) {
      U.t.value = t; U.amount.value = amount;
      mesh.visible = amount > .01;
      if (amount > .3) twitter(t);
    },
  };
}
