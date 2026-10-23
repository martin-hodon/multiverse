// FLOWER BOXES under the windows of the town's houses: a plank box on the sill, outside, and a bank of leaves and
// blooms in it -- geraniums, pinks, daisies, violets, marigolds, a box all one colour -- stirring a little in the wind.
// A house has them under most of its windows or none at all. Two meshes for the town: the boxes (one painted box
// geometry, merged) and the flowers (two crossed cards a box, leaves and blooms cut in the shader).
//
//   createWindowBoxes(scene, windows, { seed })   // windows: [{ x, y, z, w, h, base, cx, cz, glazed, outer }] (the glow's list;
//                                                 // outer: how far out the wall's face is, metres)
//   -> { count, update(t) }
import * as THREE from "three";
import { boundTo } from "./bounds.js";
import { attribute, uniform, vec3, vec4, float, uv, sin, fract, floor, smoothstep, mix, positionGeometry, cameraViewMatrix, cameraProjectionMatrix } from "three/tsl";
import { windAt } from "./grass.js";
import { rng } from "./flora.js";

export const WINDOWBOX = { house: .7, window: .8, out: .33, depth: .24, height: .17, bloom: .42 };
const BLOOMS = ["#c8283a", "#e0607e", "#f2efe6", "#7a4fa8", "#e8a42c", "#d84a2a"];   // geranium, pink, daisy, violet, marigold, nasturtium

export function createWindowBoxes(scene, windows, { seed = 1 } = {}) {
  const r = rng(seed * 71 + 29);
  const house = new Map();
  const picked = windows.filter((w) => {
    if (w.glazed || w.w > 1.6) return false;   // (glass is a palace's or a church's; a wide opening is a shop's)
    const k = `${w.cx.toFixed(1)},${w.cz.toFixed(1)}`;
    if (!house.has(k)) house.set(k, r() < WINDOWBOX.house ? BLOOMS[Math.floor(r() * BLOOMS.length)] : null);
    return house.get(k) && r() < WINDOWBOX.window;
  });
  if (!picked.length) return { count: 0, update() {} };
  const boxP = [], boxC = [], boxI = [], flP = [], flUV = [], flC = [], flS = [], flI = [];
  const wood = new THREE.Color("#6e4a2c"), wood2 = new THREE.Color("#5a3b22"), c = new THREE.Color();
  for (const w of picked) {
    const ax = Math.cos(w.base), az = -Math.sin(w.base);
    let nx = az, nz = -ax; if (nx * (w.x - w.cx) + nz * (w.z - w.cz) < 0) { nx = -nx; nz = -nz; }
    const out = w.outer !== undefined ? w.outer + WINDOWBOX.depth / 2 + .02 : WINDOWBOX.out;   // (just outside the wall's face, where it was measured: index.html wallOuter)
    const hw = w.w / 2 + .05, sill = w.y - w.h / 2, cx = w.x + nx * out, cz = w.z + nz * out;
    const y0 = sill - WINDOWBOX.height + .03, y1 = sill + .03, hd = WINDOWBOX.depth / 2;
    // the box: 8 corners, 5 faces (no top: the earth is under the flowers), the front a shade darker
    const P = (s, t, y) => [cx + ax * hw * s + nx * hd * t, y, cz + az * hw * s + nz * hd * t];
    const faces = [[[-1, 1, y0], [1, 1, y0], [1, 1, y1], [-1, 1, y1], wood2], [[1, -1, y0], [-1, -1, y0], [-1, -1, y1], [1, -1, y1], wood],
                   [[-1, -1, y0], [-1, 1, y0], [-1, 1, y1], [-1, -1, y1], wood], [[1, 1, y0], [1, -1, y0], [1, -1, y1], [1, 1, y1], wood],
                   [[-1, -1, y0], [1, -1, y0], [1, 1, y0], [-1, 1, y0], wood2]];
    for (const [a, b, cc, d, col] of faces) {
      const o = boxP.length / 3;
      for (const q of [a, b, cc, d]) { boxP.push(...P(...q)); boxC.push(col.r, col.g, col.b); }
      boxI.push(o, o + 1, o + 2, o, o + 2, o + 3);
    }
    // the flowers: two cards crossing along the box, a little leaning out
    c.set(house.get(`${w.cx.toFixed(1)},${w.cz.toFixed(1)}`));
    const fh = WINDOWBOX.bloom, ph = r() * 50;
    for (const lean of [-.35, .35]) {
      const o = flP.length / 3;
      const lx = nx * fh * lean, lz = nz * fh * lean;
      for (const [s, v] of [[-1, 0], [1, 0], [1, 1], [-1, 1]]) {
        flP.push(cx + ax * (hw - .02) * s + lx * v, y1 - .04 + fh * v, cz + az * (hw - .02) * s + lz * v);
        flUV.push((s + 1) / 2 * w.w * 3, v);   // (u in ~third-metres along: the blooms keep their size whatever the box's width)
        flC.push(c.r, c.g, c.b); flS.push(ph + lean);
      }
      flI.push(o, o + 1, o + 2, o, o + 2, o + 3);
    }
  }
  const bg = new THREE.BufferGeometry();
  bg.setAttribute("position", new THREE.Float32BufferAttribute(boxP, 3));
  bg.setAttribute("color", new THREE.Float32BufferAttribute(boxC, 3));
  bg.setIndex(boxI);
  const boxes = new THREE.Mesh(bg, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide }));
  boxes.name = "flower boxes"; boxes.userData.noMerge = true;
  scene.add(boxes);

  const fg = new THREE.BufferGeometry();
  fg.setAttribute("position", new THREE.Float32BufferAttribute(flP, 3));
  fg.setAttribute("uv", new THREE.Float32BufferAttribute(flUV, 2));
  fg.setAttribute("bloom", new THREE.Float32BufferAttribute(flC, 3));
  fg.setAttribute("seedA", new THREE.Float32BufferAttribute(flS, 1));
  fg.setIndex(flI);
  const U = { t: uniform(0) };
  const S = attribute("seedA", "float"), B = attribute("bloom", "vec3"), P = positionGeometry;
  const v = uv().y, u = uv().x;
  const sway = windAt({ p: P.xz, t: U.t }).mul(.025).mul(v);
  const mat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  mat.vertexNode = cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(P.add(vec3(sway, 0, sway.mul(.6))), 1)));
  // leaves: a scalloped mound, higher in clumps; blooms: round heads in the upper part, in a jittered grid
  const cell = floor(u.mul(1.6)), cu = fract(u.mul(1.6)), h1 = fract(sin(cell.mul(12.9898).add(S)).mul(43758.5));
  const mound = sin(u.mul(7).add(S)).mul(.1).add(sin(u.mul(19).add(S.mul(2))).mul(.05)).add(.55).add(h1.mul(.1));
  const leaf = smoothstep(mound.add(.02), mound.sub(.02), v);
  const bx = cu.sub(.5).sub(h1.sub(.5).mul(.4)), by = v.sub(mound.sub(.06).add(h1.mul(.1)));
  const head = smoothstep(.3, .2, vec3(bx, by.mul(1.9), 0).length());
  const head2 = smoothstep(.24, .15, vec3(cu.sub(.12).sub(h1.mul(.1)), v.sub(mound.mul(.85)).mul(2.1), 0).length());
  const head3 = smoothstep(.22, .14, vec3(cu.sub(.85).add(h1.mul(.1)), v.sub(mound.mul(.9).add(.05)).mul(2.1), 0).length());
  const bloom = head.add(head2).add(head3).min(1);
  const green = mix(vec3(.18, .36, .14), vec3(.3, .5, .2), fract(u.mul(7.3).add(v.mul(3.1))).mul(.5).add(v.mul(.4)));
  mat.colorNode = mix(green, B.mul(bloom.mul(.15).add(.88)), bloom);
  mat.opacityNode = leaf.max(bloom);
  mat.alphaTest = .5;
  const flowers = new THREE.Mesh(fg, mat);
  boundTo(flowers, null, .5); flowers.name = "window flowers"; flowers.userData.noMerge = true; flowers.userData.cut = true;
  scene.add(flowers);
  return { count: picked.length, update(t) { U.t.value = t; } };
}
