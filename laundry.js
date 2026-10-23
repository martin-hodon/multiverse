// WASHING LINES across the lanes: a rope from an upstairs window to the one facing it in the house across the way,
// sagging between them, with the wash pegged along it -- sheets, shirts, breeches, stockings, in linen and in the
// colours of the town's dyes -- stirring in the wind (the grass's own gusts: grass.js grassWind). Found from the
// windows alone: pairs of upper-storey windows of different houses that face each other 4 to 10 m apart at about the
// same height. One mesh for all the wash (its shapes cut in the shader), one for the ropes.
//
//   const laundry = createLaundry(scene, windows, { seed })   // windows: [{ x, y, z, w, h, base, cx, cz }] (the glow's list)
//   laundry.update(t)
import * as THREE from "three";
import { boundTo } from "./bounds.js";
import { attribute, uniform, vec3, vec4, float, uv, sin, smoothstep, abs, mix, max, step, positionGeometry, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { windAt } from "./grass.js";
import { rng } from "./flora.js";

export const LAUNDRY = { lines: 16, near: 4, far: 10, minY: 3, sag: .38 };
// the wash: [kind, width, drop, colours]
const KINDS = [
  ["sheet", [1.0, 1.5], [.9, 1.3], ["#efeadf", "#e8e2d4", "#dfe6ea"]],
  ["shirt", [.55, .7], [.6, .75], ["#efeadf", "#c9d3dc", "#8fa7bf", "#b5654a", "#d7c48e"]],
  ["breeches", [.4, .5], [.6, .75], ["#6b5a45", "#4f5b66", "#7b6a52", "#3e4a3a"]],
  ["stocking", [.12, .16], [.4, .5], ["#efeadf", "#8b3a32", "#3d5a80", "#d9c9a8"]],
  ["cloth", [.45, .7], [.4, .6], ["#c94f3d", "#e0b04b", "#4f7aa8", "#7a9a5a", "#efeadf"]],
];
const KIND_ID = Object.fromEntries(KINDS.map(([k], i) => [k, i]));

export function createLaundry(scene, windows, { seed = 1 } = {}) {
  const r = rng(seed * 53 + 17);
  // the pairs: facing each other across a lane, upstairs, of two houses
  const up = windows.filter((w) => w.y >= LAUNDRY.minY);
  const norm = (w) => { const ax = Math.cos(w.base), az = -Math.sin(w.base); let nx = az, nz = -ax; if (nx * (w.x - w.cx) + nz * (w.z - w.cz) < 0) { nx = -nx; nz = -nz; } return [nx, nz]; };
  const cand = [];
  for (let i = 0; i < up.length; i++) for (let j = i + 1; j < up.length; j++) {
    const a = up[i], b = up[j];
    if (Math.abs(a.cx - b.cx) + Math.abs(a.cz - b.cz) < .5 || Math.abs(a.y - b.y) > 1) continue;
    const dx = b.x - a.x, dz = b.z - a.z, d = Math.hypot(dx, dz);
    if (d < LAUNDRY.near || d > LAUNDRY.far) continue;
    const [nax, naz] = norm(a), [nbx, nbz] = norm(b);
    if ((nax * dx + naz * dz) / d < .85 || -(nbx * dx + nbz * dz) / d < .85) continue;
    cand.push([d + r() * 2, a, b, nax, naz, nbx, nbz]);
  }
  cand.sort((p, q) => p[0] - q[0]);
  const used = new Set(), lines = [];
  for (const [, a, b, nax, naz, nbx, nbz] of cand) {
    if (used.has(a) || used.has(b) || lines.length >= LAUNDRY.lines) continue;
    used.add(a); used.add(b);
    // tied at the window's head, a hand's breadth out of the wall
    lines.push([[a.x + nax * .35, a.y + a.h / 2 - .08, a.z + naz * .35], [b.x + nbx * .35, b.y + b.h / 2 - .08, b.z + nbz * .35]]);
  }
  if (!lines.length) return { lines: 0, update() {} };

  // ---- the wash: a grid of 4 x 3 cells a piece (so it can bow), hung from the rope at its top edge
  const pos = [], rope = [], cell = [], info = [], col = [], idx = [];
  const ropeAt = (L, s) => { const [a, b] = L; return [a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s - LAUNDRY.sag * 4 * s * (1 - s), a[2] + (b[2] - a[2]) * s]; };
  const c = new THREE.Color();
  let pieces = 0;
  for (const L of lines) {
    const len = Math.hypot(L[1][0] - L[0][0], L[1][2] - L[0][2]), ax = (L[1][0] - L[0][0]) / len, az = (L[1][2] - L[0][2]) / len;
    for (let s = .6 + r() * .5; s < len - .6;) {
      const [kind, wr, dr, cols] = KINDS[Math.floor(r() * r() * KINDS.length * 1.3) % KINDS.length];
      const w = wr[0] + r() * (wr[1] - wr[0]), h = dr[0] + r() * (dr[1] - dr[0]);
      if (s + w > len - .4) break;
      c.set(cols[Math.floor(r() * cols.length)]);
      const ph = r() * 6.283, base = pos.length / 3;
      for (let j = 0; j <= 3; j++) for (let i = 0; i <= 4; i++) {
        const u = i / 4, v = j / 3, along = s + u * w, top = ropeAt(L, along / len);
        pos.push(top[0], top[1] - v * h, top[2]);           // (straight down from the rope; the shader blows it about)
        rope.push(ax, az, h);
        cell.push(u, v);
        info.push(KIND_ID[kind], ph, w);
        col.push(c.r, c.g, c.b);
      }
      for (let j = 0; j < 3; j++) for (let i = 0; i < 4; i++) { const q = base + j * 5 + i; idx.push(q, q + 1, q + 6, q, q + 6, q + 5); }
      pieces++;
      s += w + .12 + r() * .45;
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("ropeDir", new THREE.Float32BufferAttribute(rope, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(cell, 2));
  g.setAttribute("info", new THREE.Float32BufferAttribute(info, 3));
  g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  g.setIndex(idx);
  const U = { t: uniform(0) };
  const R = attribute("ropeDir", "vec3"), I = attribute("info", "vec3"), C = attribute("color", "vec3");
  const v = uv().y, P = positionGeometry;
  // the wind: out of the line's plane (its normal on the ground), more the lower the cloth hangs, in gusts
  const gust = windAt({ p: P.xz, t: U.t }).mul(.5).add(.75).max(.15);   // (never backwards: a gale only blows it harder)
  const blow = v.pow(1.3).mul(R.z).mul(.42).mul(gust).add(sin(U.t.mul(3.1).add(I.y).add(uv().x.mul(2.2))).mul(.05).mul(v));
  const lift = blow.mul(blow).mul(.35);                                              // (blown out, it rises)
  const wp = P.add(vec3(R.y.negate().mul(blow), lift, R.x.mul(blow)));
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(wp, 1)));
  // the shapes, cut from the piece's rectangle: a shirt's sleeves and body, breeches' two legs, a stocking's foot
  const x = uv().x, y = uv().y, k = I.x;
  const shirt = max(step(abs(x.sub(.5)), .27), step(y, .32)).mul(step(y, .98));        // body, and the sleeves across the top
  const breeches = max(step(y, .38), step(.12, abs(x.sub(.5)))).mul(step(abs(x.sub(.5)), .5));   // the seat, then two legs
  const stocking = max(step(y, .82), step(x, .9)).mul(1);                              // (a foot turned out at the bottom)
  const keep = mix(float(1), shirt, step(.5, k).mul(step(k, 1.5))).mul(mix(float(1), breeches, step(1.5, k).mul(step(k, 2.5)))).mul(mix(float(1), stocking, step(2.5, k).mul(step(k, 3.5))));
  // a fold's light: the cloth's own bow, and the sun on it
  const shade = sin(x.mul(3.14 * 2).add(U.t.mul(1.7)).add(I.y)).mul(.06).add(.94).mul(smoothstep(0, .15, y).mul(.12).add(.88));
  mat.colorNode = C.mul(shade);
  mat.opacityNode = keep;
  mat.alphaTest = .5;
  const wash = new THREE.Mesh(g, mat);
  boundTo(wash, null, 1); wash.name = "laundry"; wash.userData.noMerge = true; wash.userData.cut = true;
  scene.add(wash);

  // ---- the ropes: each a sagging line of 12 segments
  const rp = [];
  for (const L of lines) for (let i = 0; i < 12; i++) rp.push(...ropeAt(L, i / 12), ...ropeAt(L, (i + 1) / 12));
  const rg = new THREE.BufferGeometry();
  rg.setAttribute("position", new THREE.Float32BufferAttribute(rp, 3));
  const ropes = new THREE.LineSegments(rg, new THREE.LineBasicMaterial({ color: 0x5b5048 }));
  boundTo(ropes, null, .5); ropes.name = "washing lines"; ropes.userData.noMerge = true;
  scene.add(ropes);
  return { lines: lines.length, pieces, ends: lines, update(t) { U.t.value = t; } };
}
