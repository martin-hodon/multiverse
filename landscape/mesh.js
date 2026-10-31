// THE LANDSCAPE ENGINE's mesher (docs/landscape.md): a cave's volume to triangles

// SURFACE NETS: the surface where a sampled field crosses 0 (solid where > 0), as a mesh -- a vertex in every cell the
// surface passes through (at the mean of its edges' crossings), a quad across every grid edge it crosses. `f` is
// nx*ny*nz samples, x fastest; the vertices are in grid units. (Smoother than marching cubes for the same grid, and
// needs no tables.) The quads face out of the solid, counter-clockwise seen from outside in a right-handed x, y, z.
export function surfaceNets(f, nx, ny, nz) {
  const cx = nx - 1, cy = ny - 1, cz = nz - 1, vid = new Int32Array(cx * cy * cz).fill(-1), pos = [], idx = [];
  const E = [[0, 0, 0, 1, 0, 0], [0, 1, 0, 1, 1, 0], [0, 0, 1, 1, 0, 1], [0, 1, 1, 1, 1, 1], [0, 0, 0, 0, 1, 0], [1, 0, 0, 1, 1, 0],
             [0, 0, 1, 0, 1, 1], [1, 0, 1, 1, 1, 1], [0, 0, 0, 0, 0, 1], [1, 0, 0, 1, 0, 1], [0, 1, 0, 0, 1, 1], [1, 1, 0, 1, 1, 1]];
  const at = (x, y, z) => f[x + nx * (y + ny * z)];
  for (let z = 0; z < cz; z++) for (let y = 0; y < cy; y++) for (let x = 0; x < cx; x++) {
    let sx = 0, sy = 0, sz = 0, c = 0;
    for (const [a, b, d, e, g, h] of E) {
      const va = at(x + a, y + b, z + d), vb = at(x + e, y + g, z + h);
      if ((va > 0) === (vb > 0)) continue;
      const t = va / (va - vb); sx += a + (e - a) * t; sy += b + (g - b) * t; sz += d + (h - d) * t; c++;
    }
    if (!c) continue;
    vid[x + cx * (y + cy * z)] = pos.length / 3; pos.push(x + sx / c, y + sy / c, z + sz / c);
  }
  const cell = (x, y, z) => vid[x + cx * (y + cy * z)], st = [1, nx, nx * ny], dims = [nx, ny, nz];
  for (let d = 0; d < 3; d++) {
    const u = (d + 1) % 3, v = (d + 2) % 3;
    for (let z = 0; z < nz; z++) for (let y = 0; y < ny; y++) for (let x = 0; x < nx; x++) {
      const p = [x, y, z];
      if (p[d] >= dims[d] - 1 || p[u] < 1 || p[v] < 1 || p[u] >= dims[u] - 1 || p[v] >= dims[v] - 1) continue;
      const k = x + nx * (y + ny * z), a = f[k] > 0, b = f[k + st[d]] > 0;
      if (a === b) continue;
      const q = (du, dv) => { const r = [x, y, z]; r[u] -= du; r[v] -= dv; return cell(r[0], r[1], r[2]); };
      const c0 = q(1, 1), c1 = q(0, 1), c2 = q(0, 0), c3 = q(1, 0);
      if (c0 < 0 || c1 < 0 || c2 < 0 || c3 < 0) continue;
      if (a) idx.push(c0, c1, c2, c0, c2, c3); else idx.push(c0, c2, c1, c0, c3, c2);
    }
  }
  return { pos, idx };
}
