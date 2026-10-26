// THE NIGHT'S OWN LIGHTS: what still shines after the night pass has darkened the frame (index.html multiplies the
// whole picture down) -- lamplight in the windows and fireflies over the meadows and the water. They live in their
// own scene, drawn AFTER the darkening with the world's depth still in the buffer, so a wall or a tree in front of a
// window or a firefly hides it, and they keep their full brightness. Two meshes, two draws, only at night.
//
// WINDOWS: a lit house has most of its windows lit. A shuttered window shows the lamplight only where it leaks --
// round the shutter's edges, down the crack where its two leaves meet and through the little heart cut in it; a
// window opened by the player, or one with glass, shows the room's warm glow with its glazing bars. Each light
// breathes a little, as a hearth or a candle does.
// FIREFLIES: points of cold yellow-green light drifting a metre or so over the grass, each blinking in its own
// rhythm; more of them near water.
//
//   const glow = createNightGlow({ windows, fireflyAt, seed, fog })
//     windows: [{ x, y, z, w, h, base, glazed, cx, cz, rec }]  (the pane's middle, its axis yaw, its building's middle,
//               rec: the shutter's record -- its `open` is read every frame)
//     fireflyAt(r): a place for a firefly ({x, y, z} or null), r a random function
//   glow.update(t, { night, level, fireflies })   level: the hour's darkness 0..1 (the lamps come on as it deepens)   then, at night, renderer.render(glow.scene, camera)
import * as THREE from "three";
import { blockMesh } from "./blocks.js";
import { attribute, uniform, vec2, vec3, vec4, float, varying, uv, fract, sin, cos, smoothstep, mix, clamp, abs, max, min, step,
         cameraViewMatrix, cameraProjectionMatrix, positionGeometry } from "three/tsl";
import { rng } from "./flora.js";
import { LEAD } from "./archmat.js";   // (the leaded glass by day: its quarries at night too)

const SPILL = .55, PULL = .4;   // metres: the light thrown round a window; how far toward the eye it is drawn (the wall's depth)
export const NIGHTGLOW = {
  litHouse: .78,       // the share of buildings with a lamp burning
  litWindow: .72,      // ...and of a lit building's windows
  lamp: [1.0, .66, .30],
  fireflies: 320,
  firefly: [.78, 1.0, .38],
};

export function createNightGlow({ windows, fireflyAt, seed = 11, fog = null }) {
  const scene = new THREE.Scene();
  scene.fog = fog;
  const r = rng(seed * 17 + 3);
  const U = { t: uniform(0), level: uniform(1), lamp: uniform(new THREE.Color(...NIGHTGLOW.lamp)), fly: uniform(new THREE.Color(...NIGHTGLOW.firefly)) };

  // ---- the windows -------------------------------------------------------------------------------------------------
  const byHouse = new Map();
  const lit = windows.filter((w) => {
    const k = `${w.cx.toFixed(1)},${w.cz.toFixed(1)}`;
    if (!byHouse.has(k)) byHouse.set(k, r() < NIGHTGLOW.litHouse);
    return byHouse.get(k) && r() < NIGHTGLOW.litWindow;
  });
  let winMesh = null, openAttr = null;
  if (lit.length) {
    const n = lit.length, pos = new Float32Array(n * 12), uvA = new Float32Array(n * 8), sizeA = new Float32Array(n * 8), info = new Float32Array(n * 12), open = new Float32Array(n * 4), idx = new Uint32Array(n * 6);
    lit.forEach((w, i) => {
      const ax = Math.cos(w.base), az = -Math.sin(w.base);
      let nx = az, nz = -ax;                                               // the pane's normal, turned out of the building
      if (nx * (w.x - w.cx) + nz * (w.z - w.cz) < 0) { nx = -nx; nz = -nz; }
      // (the card reaches SPILL metres past the opening on every side: the lamplight thrown on the wall round it)
      // (on the wall's outer face, measured -- index.html wallOuter -- in front of a shutter closed over it; else a little
      //  out from the opening's middle)
      const out = !w.glazed && w.outer !== undefined ? w.outer + .08 : .045;
      const ox = w.x + nx * out, oz = w.z + nz * out, hw = w.w / 2 + SPILL, hh = w.h / 2 + SPILL, ph = r();   // (one phase a window: drawn per corner, it ran across the pane)
      [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([sx, sy], v) => {
        pos.set([ox + ax * hw * sx, w.y + hh * sy, oz + az * hw * sx], (i * 4 + v) * 3);
        uvA.set([.5 + sx * hw / w.w, .5 + sy * hh / w.h], (i * 4 + v) * 2);   // (0..1 over the opening itself)
        sizeA.set([w.w, w.h], (i * 4 + v) * 2);
        info.set([ph, w.glazed ? 1 + (w.arched ? 1 : 0) : 0, w.h / Math.max(.2, w.w)], (i * 4 + v) * 3);   // its phase, glass (2: under a round head) or shutters, its tallness
      });
      idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
    });
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    g.setAttribute("wuv", new THREE.BufferAttribute(uvA, 2));
    g.setAttribute("info", new THREE.BufferAttribute(info, 3));
    g.setAttribute("wsize", new THREE.BufferAttribute(sizeA, 2));
    openAttr = new THREE.BufferAttribute(open, 1); openAttr.setUsage(THREE.DynamicDrawUsage);
    g.setAttribute("open", openAttr);
    g.setIndex(new THREE.BufferAttribute(idx, 1));
    const W = attribute("wuv", "vec2"), I = attribute("info", "vec3"), O = attribute("open", "float"), Z = attribute("wsize", "vec2");
    const ph = I.x.mul(37.0);
    const breathe = sin(U.t.mul(2.1).add(ph)).mul(sin(U.t.mul(5.3).add(ph.mul(1.7)))).mul(.12).add(.92);
    // a shutter: two leaves of boards -- light along the outer edges, the meeting crack, the board seams faintly,
    // and a heart cut high in each leaf
    const ex = min(W.x, W.x.oneMinus()), ey = min(W.y, W.y.oneMinus());   // (how near an edge, across and up)
    const rim = smoothstep(.07, .0, min(ex, ey.mul(I.z)));   // (the same width of gap on every side: up is scaled by its tallness)
    const crack = smoothstep(.022, .004, abs(W.x.sub(.5)));
    const lx = fract(W.x.mul(2)).sub(.5), hy = W.y.sub(.76).mul(I.z).mul(2.6);               // each leaf's own across, the heart's height
    const hp = vec2(abs(lx).mul(1.25), hy.mul(1.1).sub(abs(lx).mul(.9)));
    const heart = smoothstep(.15, .11, hp.length());
    const seams = smoothstep(.012, .0, abs(fract(W.x.mul(6)).sub(.5)).sub(.48).abs()).mul(.25);
    const leak = max(max(rim, crack), max(heart, seams));
    // an open window or glass: the room's light, warmer low down, the glazing bars across it (glass only)
    // (glass is LEADED: diamond quarries as by day -- archmat.js LEAD -- the lead dark against the room's light)
    const qd = W.mul(Z).div(LEAD.size), qa = abs(fract(qd.x.add(qd.y)).sub(.5)), qb = abs(fract(qd.x.sub(qd.y)).sub(.5));
    const bars = step(.5, I.y).mul(smoothstep(.5 - LEAD.width - .03, .5 - LEAD.width, max(qa, qb)));
    // (a round-headed window, I.y 2: its light cut to the arch -- a half-disc over its top width)
    const archR = Z.x.div(2), archY = W.y.mul(Z.y).sub(Z.y.sub(archR)), archOut = vec2(W.x.sub(.5).mul(Z.x), archY.max(0)).length().sub(archR);
    const arched = step(1.5, I.y).mul(smoothstep(-.01, .01, archOut));
    const room = smoothstep(0, .12, min(ex, ey)).mul(mix(float(1), float(.75), W.y)).mul(bars.oneMinus().mul(.9).add(.1)).mul(arched.oneMinus());
    // SOMEONE INSIDE: every 25-55 s (each window its own) a figure crosses the room in front of the lamp -- a head and
    // shoulders, a dark shape gliding past the glass (or across the light between the shutters), bobbing as it walks
    const every = I.x.mul(30).add(25), pass = fract(U.t.div(every).add(I.x.mul(7))).mul(every).div(3.2);
    const way = I.x.greaterThan(.5).select(pass, pass.oneMinus()), sx = mix(float(-.3), float(1.3), way);
    const dxm = W.x.sub(sx).mul(Z.x), bobm = sin(U.t.mul(8)).mul(.012);
    const headS = smoothstep(.12, .09, vec2(dxm, W.y.sub(.62).mul(Z.y).sub(bobm)).length());
    const bodyS = smoothstep(1.03, .97, vec2(dxm.div(.25), W.y.sub(.2).mul(Z.y).sub(bobm).div(.44)).length());
    const sil = max(headS, bodyS).mul(step(pass, 1));
    const shut = I.y.oneMinus().mul(O.oneMinus());                                          // shuttered and closed
    const on = smoothstep(I.x.mul(.35).add(.3), I.x.mul(.35).add(.36), U.level);   // (the lamps come on one by one as the dusk deepens)
    // outside the opening: the SPILL on the wall, fading over SPILL metres (more of it round an opened window)
    const out = vec2(max(W.x.negate(), W.x.sub(1)).max(0).mul(Z.x), max(W.y.negate(), W.y.sub(1)).max(0).mul(Z.y)).length();
    const inside = step(out, 0.0001);
    const spill = smoothstep(SPILL, 0, out).pow(2.2).mul(mix(float(.32), float(.5), shut.oneMinus()));
    const a = mix(spill, mix(room.mul(.95).mul(sil.mul(-.85).add(1)), leak.mul(sil.mul(-.7).add(1)), shut), inside).mul(breathe).mul(on);   // (per pixel: the shape lives in wuv -- at the corners it is all edge)
    const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide });
    // drawn a little toward the eye: the opening sits in the wall's middle, the spill must lie on its outer face
    mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(positionGeometry, 1)).add(vec4(0, 0, PULL, 0)));
    mat.colorNode = U.lamp.mul(a.mul(.25).add(.85));
    mat.opacityNode = clamp(a, 0, 1);
    mat.alphaTest = .02;
    winMesh = new THREE.Mesh(g, mat);
    winMesh.frustumCulled = false;
    winMesh.name = "lit windows";
    scene.add(winMesh);
  }

  // ---- the fireflies -----------------------------------------------------------------------------------------------
  let flyMesh = null;
  // ...in SWARMS: a few dozen places (most of them by the water), a dozen or so fireflies drifting round each
  const spots = [];
  for (let tries = 0; spots.length < NIGHTGLOW.fireflies && tries < NIGHTGLOW.fireflies; tries++) {
    const c = fireflyAt(r);
    if (!c) continue;
    for (let k = 0, n = 8 + Math.floor(r() * 10); k < n && spots.length < NIGHTGLOW.fireflies; k++) {
      const a = r() * Math.PI * 2, d = Math.sqrt(r()) * 7;
      spots.push({ x: c.x + Math.cos(a) * d, y: c.y + (r() - .5) * .8, z: c.z + Math.sin(a) * d });
    }
  }
  if (spots.length) {
    const n = spots.length, base = new Float32Array(n * 12), cr = new Float32Array(n * 8), sd = new Float32Array(n * 12), idx = new Uint32Array(n * 6);
    spots.forEach((p, i) => {
      const s = [r(), r(), r()];
      for (let v = 0; v < 4; v++) {
        base.set([p.x, p.y, p.z], (i * 4 + v) * 3);
        cr.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], (i * 4 + v) * 2);
        sd.set(s, (i * 4 + v) * 3);
      }
      idx.set([i * 4, i * 4 + 1, i * 4 + 3, i * 4, i * 4 + 3, i * 4 + 2], i * 6);
    });
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(base.slice(), 3));
    g.setAttribute("base", new THREE.BufferAttribute(base, 3));
    g.setAttribute("corner", new THREE.BufferAttribute(cr, 2));
    g.setAttribute("uv", new THREE.BufferAttribute(cr.map((v) => v + .5), 2));   // (the quad's own 0..1, for the shape drawn on it)
    g.setAttribute("seedA", new THREE.BufferAttribute(sd, 3));
    g.setIndex(new THREE.BufferAttribute(idx, 1));
    const B = attribute("base", "vec3"), C = attribute("corner", "vec2"), S = attribute("seedA", "vec3");
    const f1 = S.x.mul(.25).add(.12), f2 = S.y.mul(.2).add(.09), ph = S.z.mul(40);
    // a lazy wander about its spot: two slow loops, a bob
    const off = vec3(sin(U.t.mul(f1).add(ph)).mul(1.4).add(sin(U.t.mul(f2.mul(2.3)).add(ph.mul(.7))).mul(.6)),
                     sin(U.t.mul(f2.mul(3.1)).add(ph.mul(1.3))).mul(.45),
                     cos(U.t.mul(f2).add(ph.mul(.5))).mul(1.4).add(cos(U.t.mul(f1.mul(1.9)).add(ph)).mul(.6)));
    // the blink: a soft flash of ~0.7 s every 2.5..5 s, each in its own beat
    const beat = fract(U.t.div(S.y.mul(2.5).add(2.5)).add(S.x));
    const flash = smoothstep(0, .05, beat).mul(smoothstep(.22, .08, beat)).add(.04).mul(smoothstep(S.z.mul(.2).add(.55), S.z.mul(.2).add(.65), U.level));   // (out once it is dark enough)
    const view = cameraViewMatrix.mul(vec4(B.add(off), 1));
    const sz = float(.42);
    const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false });
    mat.vertexNode = cameraProjectionMatrix.mul(vec4(view.xy.add(C.mul(sz)), view.z, view.w));
    const vF = varying(flash);
    const d = uv().sub(.5).mul(2).length();
    const core = smoothstep(.22, .0, d), halo = smoothstep(1, .0, d).pow(2.2).mul(.45);
    mat.colorNode = U.fly.mul(core.add(halo)).mul(vF).mul(1.4);
    mat.opacityNode = float(1);
    flyMesh = new THREE.Mesh(g, mat);
    flyMesh.frustumCulled = false;
    flyMesh.name = "fireflies";
    scene.add(flyMesh);
  }

  // ---- the lanterns people carry: a halo round each, and the pool of light it throws on the ground under it ----------
  // (placed every frame from where the hands are: setLamps; LAMPS at most)
  const LAMPS = 72;
  const lampAt = new Float32Array(LAMPS * 8 * 4), lc = new Float32Array(LAMPS * 8 * 2), lk = new Float32Array(LAMPS * 8), lidx = new Uint32Array(LAMPS * 12);
  for (let i = 0; i < LAMPS; i++) for (let q = 0; q < 2; q++) {
    for (let v = 0; v < 4; v++) { const j = i * 8 + q * 4 + v; lc.set([v & 1 ? .5 : -.5, v & 2 ? .5 : -.5], j * 2); lk[j] = q; }
    const o = i * 8 + q * 4; lidx.set([o, o + 1, o + 3, o, o + 3, o + 2], i * 12 + q * 6);
  }
  const lg = new THREE.BufferGeometry();
  const lampAttr = new THREE.BufferAttribute(lampAt, 4); lampAttr.setUsage(THREE.DynamicDrawUsage);
  lg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(LAMPS * 8 * 3), 3));
  lg.setAttribute("lampAt", lampAttr);
  lg.setAttribute("corner", new THREE.BufferAttribute(lc, 2));
  lg.setAttribute("uv", new THREE.BufferAttribute(lc.map((v) => v + .5), 2));
  lg.setAttribute("kind", new THREE.BufferAttribute(lk, 1));
  lg.setIndex(new THREE.BufferAttribute(lidx, 1));
  lg.setDrawRange(0, 0);
  {
    const L = attribute("lampAt", "vec4"), C = attribute("corner", "vec2"), K = attribute("kind", "float");
    // a halo: a card facing the eye; a pool: flat on the ground under the lamp, 5 m across
    const halo = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(L.xyz, 1)).add(vec4(C.mul(1.5), 0, 0)));
    const pool = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(L.x.add(C.x.mul(5)), L.w.add(.04), L.z.add(C.y.mul(5)), 1)));
    const mat = new THREE.MeshBasicNodeMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false, side: THREE.DoubleSide });
    mat.vertexNode = mix(halo, pool, K);
    const vK = varying(K), vF = varying(sin(U.t.mul(9.3).add(L.x.mul(3.1))).mul(sin(U.t.mul(4.1).add(L.z))).mul(.12).add(.9));
    const d = uv().sub(.5).mul(2).length();
    const h = smoothstep(.16, .0, d).mul(.9).add(smoothstep(1, .0, d).pow(2.5).mul(.55));
    const pl = smoothstep(1, .0, d).pow(1.8).mul(.32);
    mat.colorNode = U.lamp.mul(mix(h, pl, vK)).mul(vF).mul(U.level.sub(.3).mul(3).clamp(0, 1));
    mat.opacityNode = float(1);
    const lampMesh = new THREE.Mesh(lg, mat);
    lampMesh.frustumCulled = false;
    lampMesh.name = "lanterns";
    scene.add(lampMesh);
  }

  return {
    scene, windows: lit.length, fireflies: spots.length, spots, lit,
    // the lanterns now: [[x, y, z, groundY]...] (the lamp's middle; the ground under it)
    setLamps(list) {
      const n = Math.min(LAMPS, list.length);
      for (let i = 0; i < n; i++) for (let v = 0; v < 8; v++) lampAt.set(list[i], (i * 8 + v) * 4);
      lampAttr.needsUpdate = true;
      lg.setDrawRange(0, n * 12);
    },
    update(t, { night = false, level = 1, fireflies = true } = {}) {
      U.t.value = t; U.level.value = level;
      if (!night) return;
      if (flyMesh) flyMesh.visible = fireflies;
      if (openAttr) {   // a shutter the player opened shows the room behind it
        let dirty = false;
        for (let i = 0; i < lit.length; i++) {
          const o = lit[i].rec?.open || lit[i].rec?.ang > .2 ? 1 : 0;
          if (openAttr.array[i * 4] !== o) { openAttr.array.fill(o, i * 4, i * 4 + 4); dirty = true; }
        }
        if (dirty) openAttr.needsUpdate = true;
      }
    },
  };
}

// WALL LAMPS: an iron lantern on a bracket beside a door -- the inn's, the church's, a shop's -- its horn panes pale by
// day; at night the glow's lamps (setLamps) light it, a halo and a pool on the step. One mesh for all of them.
//   createWallLamps(scene, doors) -> [[x, y, z, groundY], ...] (where each lamp's light is)   (and createHangingLamps, below)
//   doors: [{ x, z, y, w, base, cx, cz, ground }] (the doorway's middle and floor, its width, its axis, its building's middle)
export function createWallLamps(scene, doors) {
  const blocks = [], out = [];
  const iron = [.2, .19, .18], pane = [.86, .74, .5];
  const box = (cx, cy, cz, sx, sy, sz, colour) => blocks.push({ at: [cx, cy, cz], size: [sx, sy, sz], colour });
  for (const d of doors) {
    const ax = Math.cos(d.base), az = -Math.sin(d.base);
    let nx = az, nz = -ax; if (nx * (d.x - d.cx) + nz * (d.z - d.cz) < 0) { nx = -nx; nz = -nz; }
    const along = d.w / 2 + .38, x = d.x + ax * along + nx * .42, z = d.z + az * along + nz * .42, y = d.y + 2.3;
    // the bracket from the wall, the lantern hanging from it: a roof, the panes, a base
    box(d.x + ax * along + nx * .2, y + .2, d.z + az * along + nz * .2, Math.abs(ax) * .04 + Math.abs(nx) * .5, .04, Math.abs(az) * .04 + Math.abs(nz) * .5, iron);
    lantern(box, x, y, z, iron, pane);
    out.push([x, y, z, d.ground]);
  }
  if (!out.length) return out;
  scene.add(blockMesh(blocks, "wall lamps"));
  return out;
}
// a lantern's blocks, its light at x, y, z: a roof, the horn panes, a base (the wall lamps', the stalls')
function lantern(box, x, y, z, iron, pane) {
  box(x, y + .16, z, .2, .05, .2, iron);
  box(x, y, z, .15, .24, .15, pane);
  box(x, y - .14, z, .17, .04, .17, iron);
}
// HANGING LAMPS: the same lantern on a short chain from what is over it -- under the market stalls' awnings (index.html)
//   createHangingLamps(scene, points) -> [[x, y, z, groundY], ...]   // points: [{ x, y, z, ground }] (where each light is)
export function createHangingLamps(scene, points) {
  const blocks = [], out = [], iron = [.2, .19, .18], pane = [.86, .74, .5];
  const box = (cx, cy, cz, sx, sy, sz, colour) => blocks.push({ at: [cx, cy, cz], size: [sx, sy, sz], colour });
  for (const q of points) {
    box(q.x, q.y + .31, q.z, .02, .26, .02, iron);   // (the chain)
    lantern(box, q.x, q.y, q.z, iron, pane);
    out.push([q.x, q.y, q.z, q.ground]);
  }
  if (out.length) scene.add(blockMesh(blocks, "hanging lamps"));
  return out;
}
