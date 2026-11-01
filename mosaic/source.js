// MOSAIC, what the stones are laid over (docs/mosaic.md): any drawing, its layers drawn as a pattern at twice the tile's texels,
// then read as a map of the stone colours. Each region of one colour is a segment, and `dist` is how far a texel is from
// the segment's edge: the rows of stones are the isolines of that. A mean or an edge detector would see antialiasing;
// here a mixed texel simply takes the stone of what it's next to.
import { renderPattern } from "../patterns.js";

const toLab = (r, g, b) => {   // (OKLab: a nearest stone by eye, not by sRGB's numbers)
  const f = (v) => { v /= 255; return v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }, R = f(r), G = f(g), B = f(b);
  const l = Math.cbrt(.4122 * R + .5363 * G + .0514 * B), m = Math.cbrt(.2119 * R + .6807 * G + .1074 * B), s = Math.cbrt(.0883 * R + .2817 * G + .6300 * B);
  return [.2105 * l + .7936 * m - .0041 * s, 1.978 * l - 2.4286 * m + .4506 * s, .0259 * l + .7828 * m - .8087 * s];
};

// the drawing: { W, H, rgba }
export function sourceOf(L, { tile, px, pal, repeat, scale = 2 }) {
  const def = { size: tile, repeat, palette: pal, ground: L.ground ?? 0, layers: L.layers ?? [] };
  const t = renderPattern(def, { res: Math.max(px[0], px[1]) * scale });
  const [W, H] = t.px;
  return { W, H, rgba: t.canvas.getContext("2d", { willReadFrequently: true }).getImageData(0, 0, W, H).data };
}

// texels to stone slots: { idx, seed } -- a texel near a stone's colour, or one amid its like, is sure of itself
function indexed({ W, H, rgba }, pal, wrap) {
  const labs = pal.map((c) => toLab(c[0], c[1], c[2])), lut = new Int16Array(32768).fill(-1), err = new Float32Array(32768);
  const near = (r, g, b) => {
    const k = (r >> 3) << 10 | (g >> 3) << 5 | b >> 3;
    if (lut[k] < 0) {
      const q = toLab(r | 4, g | 4, b | 4); let best = 0, bd = 1e9;
      labs.forEach((c, i) => { const d = (c[0] - q[0]) ** 2 + (c[1] - q[1]) ** 2 + (c[2] - q[2]) ** 2; if (d < bd) { bd = d; best = i; } });
      lut[k] = best; err[k] = bd;
    }
    return k;
  };
  const n = W * H, idx = new Uint8Array(n), sure = new Uint8Array(n);
  for (let i = 0; i < n; i++) { const k = near(rgba[i * 4], rgba[i * 4 + 1], rgba[i * 4 + 2]); idx[i] = lut[k]; sure[i] = err[k] < .0012 ? 1 : 0; }
  // (a fringe's blend can land on another stone's colour: it isn't sure unless some of its neighbours agree)
  const fringe = [];
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const i = y * W + x; if (!sure[i]) continue;
    let same = 0;
    for (let v = -1; v <= 1; v++) for (let u = -1; u <= 1; u++) { const Y = y + v, X = x + u; if ((u || v) && (wrap || (X >= 0 && Y >= 0 && X < W && Y < H)) && idx[((Y + H) % H) * W + (X + W) % W] === idx[i]) same++; }
    if (same < 3) fringe.push(i);
  }
  for (const i of fringe) sure[i] = 0;
  return { idx, sure };
}

// every unsure texel takes the commonest sure neighbour, ring on ring
function settle(idx, sure, W, H, wrap) {
  let todo = []; for (let i = 0; i < W * H; i++) if (!sure[i]) todo.push(i);
  const count = new Uint16Array(256);
  for (let pass = 0; pass < 8 && todo.length; pass++) {
    const next = [], sets = [];
    for (const i of todo) {
      const x = i % W, y = (i - x) / W; let best = -1, bc = 0;
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        let X = x + dx, Y = y + dy;
        if (wrap) { X = (X + W) % W; Y = (Y + H) % H; } else if (X < 0 || Y < 0 || X >= W || Y >= H) continue;
        const j = Y * W + X;
        if (sure[j] && ++count[idx[j]] > bc) { bc = count[idx[j]]; best = idx[j]; }
      }
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) { const X = wrap ? (x + dx + W) % W : x + dx, Y = wrap ? (y + dy + H) % H : y + dy; if (X >= 0 && Y >= 0 && X < W && Y < H) count[idx[Y * W + X]] = 0; }
      if (best >= 0) sets.push(i, best); else next.push(i);
    }
    for (let k = 0; k < sets.length; k += 2) { idx[sets[k]] = sets[k + 1]; sure[sets[k]] = 1; }
    todo = next;
  }
}

// connected regions of one colour, across the tile's edge when it repeats
function regions(idx, W, H, wrap) {
  const n = W * H, up = new Int32Array(n);
  for (let i = 0; i < n; i++) up[i] = i;
  const find = (a) => { while (up[a] !== a) a = up[a] = up[up[a]]; return a; };
  const join = (a, b) => { a = find(a); b = find(b); if (a !== b) up[b] = a; };
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const i = y * W + x;
    if (x + 1 < W ? idx[i + 1] === idx[i] : wrap && idx[y * W] === idx[i]) join(i, x + 1 < W ? i + 1 : y * W);
    if (y + 1 < H ? idx[i + W] === idx[i] : wrap && idx[x] === idx[i]) join(i, y + 1 < H ? i + W : x);
  }
  const id = new Int32Array(n), names = new Map();
  for (let i = 0; i < n; i++) { const r = find(i); let v = names.get(r); if (v === undefined) names.set(r, v = names.size); id[i] = v; }
  return { id, count: names.size };
}

// a region too small for a stone is the drawing's dust: it goes to what most of it touches
function dedust(idx, id, count, W, H, wrap, least) {
  const size = new Int32Array(count), n = W * H;
  for (let i = 0; i < n; i++) size[id[i]]++;
  const small = []; for (let i = 0; i < n; i++) if (size[id[i]] < least) small.push(i);
  if (!small.length) return false;
  const touch = new Map();
  for (const i of small) {
    const x = i % W, y = (i - x) / W, c = id[i];
    for (const [ax, ay] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      let X = x + ax, Y = y + ay;
      if (wrap) { X = (X + W) % W; Y = (Y + H) % H; } else if (X < 0 || Y < 0 || X >= W || Y >= H) continue;
      const j = Y * W + X, d = id[j];
      if (d === c || size[d] < least) continue;
      const t = touch.get(c) ?? new Map(); touch.set(c, t); t.set(idx[j], (t.get(idx[j]) ?? 0) + 1);
    }
  }
  for (const i of small) { const t = touch.get(id[i]); if (t) { let best = idx[i], bc = 0; for (const [s, k] of t) if (k > bc) { bc = k; best = s; } idx[i] = best; } }
  return true;
}

// how far each texel is from its region's edge (8SSEDT; wrapped, its sweeps go twice round). A panel's own edge is an edge.
function distances(id, W, H, wrap) {
  const n = W * H, FAR = 16000, dx = new Int16Array(n).fill(FAR), dy = new Int16Array(n).fill(FAR);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const i = y * W + x, c = id[i];
    const L = x > 0 ? id[i - 1] : wrap ? id[y * W + W - 1] : -1, R = x < W - 1 ? id[i + 1] : wrap ? id[y * W] : -1;
    const U = y > 0 ? id[i - W] : wrap ? id[(H - 1) * W + x] : -1, D = y < H - 1 ? id[i + W] : wrap ? id[x] : -1;
    if (L !== c || R !== c || U !== c || D !== c) { dx[i] = 0; dy[i] = 0; }
  }
  const look = (i, X, Y, ox, oy) => {
    if (X < 0 || Y < 0 || X >= W || Y >= H) { if (!wrap) return; X = (X + W) % W; Y = (Y + H) % H; }
    const j = Y * W + X, a = dx[j] + ox, b = dy[j] + oy, p = dx[i], q = dy[i];
    if (a * a + b * b < p * p + q * q) { dx[i] = a; dy[i] = b; }
  };
  for (let round = 0; round < (wrap ? 2 : 1); round++) {
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) { const i = y * W + x; look(i, x - 1, y, 1, 0); look(i, x, y - 1, 0, 1); look(i, x - 1, y - 1, 1, 1); look(i, x + 1, y - 1, -1, 1); }
      for (let x = W - 1; x >= 0; x--) look(y * W + x, x + 1, y, -1, 0);
    }
    for (let y = H - 1; y >= 0; y--) {
      for (let x = W - 1; x >= 0; x--) { const i = y * W + x; look(i, x + 1, y, -1, 0); look(i, x, y + 1, 0, -1); look(i, x + 1, y + 1, -1, -1); look(i, x - 1, y + 1, 1, -1); }
      for (let x = 0; x < W; x++) look(y * W + x, x - 1, y, 1, 0);
    }
  }
  const dist = new Float32Array(n);
  for (let i = 0; i < n; i++) { const a = dx[i], b = dy[i]; dist[i] = a === FAR ? 1e6 : Math.hypot(a, b) + .5; }
  return dist;
}

// the map stones are laid on: { W, H, wrap, idx, id, count, dist }
export function segment(src, pal, wrap, least = 0) {
  const { W, H } = src, { idx, sure } = indexed(src, pal, wrap);
  settle(idx, sure, W, H, wrap);
  let { id, count } = regions(idx, W, H, wrap);
  for (let k = 0; k < 3 && dedust(idx, id, count, W, H, wrap, least); k++) ({ id, count } = regions(idx, W, H, wrap));
  return { W, H, wrap, idx, id, count, dist: count === 1 && wrap ? new Float32Array(W * H).fill(1e6) : distances(id, W, H, wrap) };
}
