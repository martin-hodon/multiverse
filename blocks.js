// BLOCKS: small props made of coloured boxes -- a wall lantern and its bracket, a fire's ring of stones and its logs --
// in one mesh of vertex colours (no texture, no light: the world's flat look), each box's top a shade lighter than its
// foot. Colours are given as they should look (sRGB) and stored linear, as vertex colours are read.
//
//   const mesh = blockMesh([{ at: [x, y, z], size: [sx, sy, sz], yaw, tilt, colour: [r, g, b], shape }...], name)
//   (yaw turns a box's x the lanes' way: toward (cos yaw, -sin yaw); tilt then raises that x end, radians); shape "log":
//   a round of wood along x instead -- eight-sided, sy across, its sawn ends pale (`ends`: their colour); "ball": a ball
//   of diameter sx, lighter on top
import * as THREE from "three";

const CORNERS = [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]];
const FACES = [[0, 1, 2, 3], [5, 4, 7, 6], [4, 0, 3, 7], [1, 5, 6, 2], [3, 2, 6, 7], [4, 5, 1, 0]];

export function blockMesh(blocks, name) {
  const pos = [], col = [], idx = [];
  for (const { at: [cx, cy, cz], size: [sx, sy, sz], yaw = 0, tilt = 0, colour, shape, ends = [.72, .6, .42] } of blocks) {
    const o = pos.length / 3, cs = Math.cos(yaw), sn = Math.sin(yaw), ct = Math.cos(tilt), st = Math.sin(tilt);
    // a local point: tilted about its own z (x end up), then turned about y, then moved
    const place = (lx, ly, lz) => { const x = lx * ct - ly * st, y = lx * st + ly * ct; return [cx + x * cs + lz * sn, cy + y, cz - x * sn + lz * cs]; };
    const put = (lx, ly, lz, c, k = 1) => { pos.push(...place(lx, ly, lz)); col.push(...c.map((v) => (v * k) ** 2.2)); };
    if (shape === "ball") {   // eight round, six up
      const R = sx / 2;
      for (let j = 0; j <= 6; j++) for (let k = 0; k < 8; k++) {
        const v = j / 6 * Math.PI, a = k / 8 * Math.PI * 2, y = -Math.cos(v);
        put(Math.sin(v) * Math.cos(a) * R, y * R, Math.sin(v) * Math.sin(a) * R, colour, .8 + .2 * (y + 1) / 2);
      }
      for (let j = 0; j < 6; j++) for (let k = 0; k < 8; k++) { const a = o + j * 8 + k, b = o + j * 8 + (k + 1) % 8; idx.push(a, b, b + 8, a, b + 8, a + 8); }
      continue;
    }
    if (shape === "log") {   // a ring of eight round the axis at each end, and a middle point on each end
      const R = sy / 2;
      for (const e of [-1, 1]) for (let k = 0; k < 8; k++) { const a = k / 8 * Math.PI * 2; put(e * sx / 2, Math.sin(a) * R, Math.cos(a) * R, colour, .82 + .18 * (Math.sin(a) + 1) / 2); }
      for (const e of [-1, 1]) for (let k = 0; k < 8; k++) { const a = k / 8 * Math.PI * 2; put(e * sx / 2, Math.sin(a) * R, Math.cos(a) * R, ends); }
      put(-sx / 2, 0, 0, ends, .9); put(sx / 2, 0, 0, ends, .9);
      for (let k = 0; k < 8; k++) { const a = o + k, b = o + (k + 1) % 8; idx.push(a, b, b + 8, a, b + 8, a + 8); }   // the bark
      for (let k = 0; k < 8; k++) { idx.push(o + 32, o + 16 + (k + 1) % 8, o + 16 + k); idx.push(o + 33, o + 24 + k, o + 24 + (k + 1) % 8); }   // the sawn ends
      continue;
    }
    for (const [x, y, z] of CORNERS) put(x * sx / 2, y * sy / 2, z * sz / 2, colour, .85 + .15 * (y + 1) / 2);
    for (const f of FACES) idx.push(o + f[0], o + f[1], o + f[2], o + f[0], o + f[2], o + f[3]);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  g.setIndex(idx);
  const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide }));   // (the faces' winding is not checked)
  m.name = name; m.userData.noMerge = true;
  return m;
}
