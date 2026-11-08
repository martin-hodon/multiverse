// t_view.mjs NAME OUT [variant|coat:k] -- a quick software render of a creature's sculpted mesh in its bind pose (no
// browser, no render lock): side, q (front-left 3/4 from above), front, back-q, and head close-ups; vertex colours,
// lambert shading, feather bars. For iterating shapes; the browser render remains the check of record.
import { readFileSync, writeFileSync } from "fs";
import { deflateSync } from "zlib";
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature, dressed } = await import(R + "creatures.js").then((m) => ({ ...m, dressed: m.dressed }));
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const { buildBody } = await import(R + "bodymesh.js");
const index = JSON.parse(readFileSync(R + "assets/index.json"));
const bank = new Map();
for (const c of index.categories) for (const p of c.paths) { try { bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json"))); } catch (e) {} }
const [name, out, opt] = process.argv.slice(2);
let d = [...bank.values()].find((q) => q?.name === name);
if (!d) { console.log("no", name); process.exit(1); }
d = JSON.parse(JSON.stringify(d));
if (process.env.DROP) { const re = new RegExp(process.env.DROP); d.sculpt.shape = d.sculpt.shape.filter((q) => !re.test(q.id)); }
if (opt) {
  if (opt.startsWith("coat:")) { const c = d.coats[+opt.slice(5)]; const { name: _n, scale, params, ...cols } = c; d.colors = { ...d.colors, ...cols }; d.params = { ...(d.params ?? {}), ...(params ?? {}) }; }
  else { const v = d.variants[opt]; d.colors = { ...d.colors, ...(v.colors ?? {}) }; d.params = { ...(d.params ?? {}), ...(v.params ?? {}) }; }
  delete d.coats; delete d.variants;
}
const def = buildCreature(d, bank);
const s = def.sculpted ? def : sculptOf(markSculpt(def));
const B = buildBody(s.sculpted);
const L = B.lods[0];
const nv = L.pos.length / 3, P = L.pos, C = L.col, N = L.nor, I = L.index;
const pid = L.patId, pp = L.patP, pq = L.patQ;
// bounds
let mn = [1e9, 1e9, 1e9], mx = [-1e9, -1e9, -1e9];
for (let i = 0; i < nv; i++) for (let k = 0; k < 3; k++) { mn[k] = Math.min(mn[k], P[3 * i + k]); mx[k] = Math.max(mx[k], P[3 * i + k]); }
const ctr = mn.map((v, k) => (v + mx[k]) / 2), ext = Math.max(mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2]);
// the head: the eyes' centre
const eyes = s.sculpted.eyes ?? [];
const hc = eyes.length ? [0, 1, 2].map((k) => eyes.reduce((a, e) => a + (e.at?.[k] ?? 0), 0) / eyes.length) : [mx[0] - .1 * ext, mx[1] - .1 * ext, 0];
hc[2] = 0;
const W = 560, H = 560;
function render(file, yaw, pitch, center, span) {
  const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
  // camera: rotate world by yaw about y, then pitch about x; view along -z
  const tr = (x, y, z) => { x -= center[0]; y -= center[1]; z -= center[2]; const x1 = x * cy - z * sy, z1 = x * sy + z * cy; const y2 = y * cp - z1 * sp, z2 = y * sp + z1 * cp; return [x1, y2, z2]; };
  const sc = W / span;
  const zb = new Float32Array(W * H).fill(-1e9), img = new Uint8Array(W * H * 3);
  for (let i = 0; i < W * H; i++) { img[3 * i] = 40; img[3 * i + 1] = 44; img[3 * i + 2] = 52; }
  const V = new Float32Array(nv * 3), Nn = new Float32Array(nv * 3);
  for (let i = 0; i < nv; i++) {
    const q = tr(P[3 * i], P[3 * i + 1], P[3 * i + 2]); V[3 * i] = W / 2 + q[0] * sc; V[3 * i + 1] = H / 2 - q[1] * sc; V[3 * i + 2] = q[2];
    const n = [N[3 * i], N[3 * i + 1], N[3 * i + 2]]; const x1 = n[0] * cy - n[2] * sy, z1 = n[0] * sy + n[2] * cy; Nn[3 * i] = x1; Nn[3 * i + 1] = n[1] * cp - z1 * sp; Nn[3 * i + 2] = n[1] * sp + z1 * cp;
  }
  const lt = [-.35, .6, .72]; const ll = Math.hypot(...lt); lt[0] /= ll; lt[1] /= ll; lt[2] /= ll;
  for (let t = 0; t < I.length; t += 3) {
    const a = I[t], b = I[t + 1], c = I[t + 2];
    const ax = V[3 * a], ay = V[3 * a + 1], bx = V[3 * b], by = V[3 * b + 1], cx = V[3 * c], cy_ = V[3 * c + 1];
    const area = (bx - ax) * (cy_ - ay) - (by - ay) * (cx - ax);
    if (Math.abs(area) < 1e-9) continue;
    const x0 = Math.max(0, Math.floor(Math.min(ax, bx, cx))), x1 = Math.min(W - 1, Math.ceil(Math.max(ax, bx, cx)));
    const y0 = Math.max(0, Math.floor(Math.min(ay, by, cy_))), y1 = Math.min(H - 1, Math.ceil(Math.max(ay, by, cy_)));
    for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) {
      const px = x + .5, py = y + .5;
      const w0 = ((bx - px) * (cy_ - py) - (by - py) * (cx - px)) / area, w1 = ((cx - px) * (ay - py) - (cy_ - py) * (ax - px)) / area, w2 = 1 - w0 - w1;
      if (w0 < 0 || w1 < 0 || w2 < 0) continue;
      const z = w0 * V[3 * a + 2] + w1 * V[3 * b + 2] + w2 * V[3 * c + 2];
      const o = y * W + x; if (z <= zb[o]) continue; zb[o] = z;
      let nx = w0 * Nn[3 * a] + w1 * Nn[3 * b] + w2 * Nn[3 * c], ny = w0 * Nn[3 * a + 1] + w1 * Nn[3 * b + 1] + w2 * Nn[3 * c + 1], nz = w0 * Nn[3 * a + 2] + w1 * Nn[3 * b + 2] + w2 * Nn[3 * c + 2];
      const nl = Math.hypot(nx, ny, nz) || 1; nx /= nl; ny /= nl; nz /= nl;
      if (nz < 0) { nx = -nx; ny = -ny; nz = -nz; }
      const sh = .38 + .62 * Math.max(0, nx * lt[0] + ny * lt[1] + nz * lt[2]);
      let col = [0, 1, 2].map((k) => w0 * C[3 * a + k] + w1 * C[3 * b + k] + w2 * C[3 * c + k]);
      const pS = pid ? pid.length / nv : 1; if (pid && pid[pS * a] > 22.5 && pid[pS * a] < 23.5 && pq) {   // feather bars
        const pl = [0, 1, 2, 3].map((k) => w0 * pp[4 * a + k] + w1 * pp[4 * b + k] + w2 * pp[4 * c + k]);
        const n = pq[4 * a], dk = pq[4 * a + 1];
        if (n > .5) { const tt = pl[0] / Math.max(pl[2], 1e-4); const bb = ((tt * n + .3 + .05 * Math.sin(pl[1] / Math.max(pl[3], 1e-4) * 3)) % 1 + 1) % 1; if (bb > .42 && bb < .72 && tt > .1) col = col.map((v) => v * dk); }
      }
      for (let k = 0; k < 3; k++) img[3 * o + k] = Math.max(0, Math.min(255, Math.round(255 * Math.pow(Math.max(0, col[k] * sh), 1 / 2.2))));
    }
  }
  // png
  const raw = Buffer.alloc((W * 3 + 1) * H);
  for (let y = 0; y < H; y++) { raw[y * (W * 3 + 1)] = 0; Buffer.from(img.buffer, y * W * 3, W * 3).copy(raw, y * (W * 3 + 1) + 1); }
  const crc = (buf) => { let c, crcT = []; for (let n = 0; n < 256; n++) { c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; crcT[n] = c >>> 0; } let x = 0xffffffff; for (const b of buf) x = crcT[(x ^ b) & 255] ^ (x >>> 8); return (x ^ 0xffffffff) >>> 0; };
  const chunk = (t, data) => { const len = Buffer.alloc(4); len.writeUInt32BE(data.length); const td = Buffer.concat([Buffer.from(t), data]); const cr = Buffer.alloc(4); cr.writeUInt32BE(crc(td)); return Buffer.concat([len, td, cr]); };
  const ih = Buffer.alloc(13); ih.writeUInt32BE(W, 0); ih.writeUInt32BE(H, 4); ih[8] = 8; ih[9] = 2; ih[10] = 0; ih[11] = 0; ih[12] = 0;
  writeFileSync(file, Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk("IHDR", ih), chunk("IDAT", deflateSync(raw)), chunk("IEND", Buffer.alloc(0))]));
}
const D = Math.PI / 180;
const views = (process.env.VIEWS ?? "side,q,hq,hside").split(",");
const hs = Math.max(ext * .32, .12);
for (const v of views) {
  if (v === "side") render(`${out}_side.png`, 0, 0, ctr, ext * 1.15);
  if (v === "q") render(`${out}_q.png`, 50 * D, 22 * D, ctr, ext * 1.15);
  if (v === "front") render(`${out}_front.png`, 90 * D, 8 * D, ctr, ext * 1.15);
  if (v === "back") render(`${out}_back.png`, -140 * D, 25 * D, ctr, ext * 1.15);
  if (v === "top") render(`${out}_top.png`, 0, 89 * D, ctr, ext * 1.15);
  if (v === "hq") render(`${out}_hq.png`, 45 * D, 15 * D, hc, hs);
  if (v === "hside") render(`${out}_hside.png`, 0, 0, hc, hs);
  if (v === "zside") render(`${out}_zside.png`, 0, 0, [ctr[0] + +(process.env.ZX ?? 0), ctr[1] + +(process.env.ZY ?? 0), ctr[2]], ext * .45);
  if (v === "zq") render(`${out}_zq.png`, 50 * D, 22 * D, [ctr[0] + +(process.env.ZX ?? 0), ctr[1] + +(process.env.ZY ?? 0), ctr[2]], ext * .45);
  if (v === "hfront") render(`${out}_hfront.png`, 90 * D, 5 * D, hc, hs);
}
console.log(name, "tris", B.stats.tris.join("/"), "ext", ext.toFixed(2), "views", views.join(","));
