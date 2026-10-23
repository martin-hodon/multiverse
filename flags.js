// FLAGS on the towers: a pole on the spire of each wall tower, gatehouse and the church's tower, and a pennant or a
// banner on it snapping in the wind -- the town's two colours, split along or across -- waves running out along it
// from the pole, more the farther from it, gusting with the grass's wind (grass.js grassWind), streaming the way the
// wind blows. One mesh for the poles, one for the cloth (a grid of 8 x 3 cells each, placed on the GPU).
//
//   const flags = createFlags(scene, peaks, { seed, colours: ["#hex", "#hex"] })   // peaks: [{ x, y, z }]
//   flags.update(t)
import * as THREE from "three";
import { boundTo } from "./bounds.js";
import { attribute, uniform, vec3, vec4, float, uv, sin, step, mix, smoothstep, abs, positionGeometry, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { windAt, WIND_DIR as WIND } from "./grass.js";   // (WIND: the gusts' way)
import { rng } from "./flora.js";

export const FLAGS = { pole: 2.4, cloth: [1.6, .9], cols: 8, rows: 3 };

export function createFlags(scene, peaks, { seed = 1, colours = ["#b3262c", "#f0e6c8"] } = {}) {
  if (!peaks.length) return { count: 0, update() {} };
  const r = rng(seed * 61 + 7);
  const pole = [], poleI = [], pos = [], uvs = [], info = [], idx = [];
  const C = FLAGS.cols, R = FLAGS.rows;
  for (const pk of peaks) {
    // the pole: a thin square post up from the spire, a knob on top
    const o = pole.length / 3, h = FLAGS.pole, w = .035, y0 = pk.y - .2;
    for (const [dx, dz] of [[-w, -w], [w, -w], [w, w], [-w, w]]) pole.push(pk.x + dx, y0, pk.z + dz, pk.x + dx, y0 + h, pk.z + dz);
    for (let k = 0; k < 4; k++) { const a = o + k * 2, b = o + ((k + 1) % 4) * 2; poleI.push(a, b, b + 1, a, b + 1, a + 1); }
    // the cloth: a grid from the pole out (u along it, v down from the top), the shape and its colours chosen per flag
    const kind = r() < .5 ? 1 : 0;                          // 1 a pennant tapering to a point, 0 a banner (split across)
    const L = FLAGS.cloth[0] * (kind ? 1.25 : 1), H = FLAGS.cloth[1], top = y0 + h - .05, base = pos.length / 3, ph = r() * 50;
    for (let j = 0; j <= R; j++) for (let i = 0; i <= C; i++) {
      const u = i / C, v = j / R;
      pos.push(pk.x, top - v * H, pk.z);                   // (all at the pole: the shader lays it out down the wind)
      uvs.push(u, v); info.push(L, H, kind, ph);
    }
    for (let j = 0; j < R; j++) for (let i = 0; i < C; i++) { const q = base + j * (C + 1) + i; idx.push(q, q + 1, q + C + 2, q, q + C + 2, q + C + 1); }
  }
  const pg = new THREE.BufferGeometry();
  pg.setAttribute("position", new THREE.Float32BufferAttribute(pole, 3)); pg.setIndex(poleI);
  const poles = new THREE.Mesh(pg, new THREE.MeshBasicMaterial({ color: 0x3a2e24, side: THREE.DoubleSide }));
  poles.name = "flag poles"; poles.userData.noMerge = true;
  scene.add(poles);
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  g.setAttribute("flagInfo", new THREE.Float32BufferAttribute(info, 4));
  g.setIndex(idx);
  const U = { t: uniform(0), c0: uniform(new THREE.Color(colours[0])), c1: uniform(new THREE.Color(colours[1])) };
  const I = attribute("flagInfo", "vec4"), P = positionGeometry, u = uv().x, v = uv().y;
  const gust = windAt({ p: P.xz, t: U.t }).mul(.25).add(.85).max(.15);   // (never backwards: a gale only snaps it harder)
  // out along the wind, rippling: a wave running from the pole to the tip, bigger toward the tip; the cloth droops a
  // little as it slackens between gusts
  const wave = sin(u.mul(7).sub(U.t.mul(9).mul(gust)).add(I.w)).mul(u.mul(.28)).add(sin(u.mul(13).sub(U.t.mul(13)).add(v.mul(2))).mul(u.mul(.06)));
  const out = u.mul(I.x).mul(gust.mul(.15).add(.85));
  const sag = u.mul(u).mul(float(1.15).sub(gust)).mul(.45);
  const wp = P.add(vec3(out.mul(WIND.x).add(wave.mul(-WIND.y)), sag.negate(), out.mul(WIND.y).add(wave.mul(WIND.x))));
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(wp, 1)));
  // a pennant: cut to a point (and split along); a banner: two fields across, a swallowtail notch at the fly
  const pennant = step(abs(v.sub(.5)), u.oneMinus().mul(.5).add(.02));
  const notch = float(1).sub(step(.82, u).mul(step(abs(v.sub(.5)), u.sub(.82).mul(1.6))));
  const keep = mix(notch, pennant, I.z);
  const field = mix(step(.5, u), step(.5, v), I.z);       // (a banner split at the middle across; a pennant along)
  const shade = wave.mul(1.4).add(1).clamp(.75, 1.15);    // (the folds catching the light)
  mat.colorNode = mix(U.c0, U.c1, field).mul(shade);
  mat.opacityNode = keep;
  mat.alphaTest = .5;
  const cloth = new THREE.Mesh(g, mat);
  boundTo(cloth, null, FLAGS.cloth[0] * 1.3 + .5); cloth.name = "flags";   // (its vertices are at the poles: the cloth streams out from them) cloth.userData.noMerge = true; cloth.userData.cut = true;
  scene.add(cloth);
  return { count: peaks.length, update(t) { U.t.value = t; } };
}
