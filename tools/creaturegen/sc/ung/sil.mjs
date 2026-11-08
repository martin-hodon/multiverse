// sil.mjs out.png name... -> side silhouettes (rest frame, sculpt field) of the rear half, with hind leg bones in red; several species in a row
import { field } from "/home/martin/store/apps/multiverse/sculpt.js";
import { readFileSync, writeFileSync } from "fs";
import { execFileSync } from "child_process";
import zlib from "zlib";
const R = "/home/martin/store/apps/multiverse/assets/creatures/";
const z = (v) => [v[0], v[1], -(v[2] ?? 0), ...v.slice(3)];
const out = process.argv[2], names = process.argv.slice(3);
const PX = 200, W = PX * names.length, H = 200;
const img = Buffer.alloc(W * H * 3, 255);
const put = (x, y, c) => { if (x < 0 || y < 0 || x >= W || y >= H) return; const i = (y * W + x) * 3; img[i] = c[0]; img[i + 1] = c[1]; img[i + 2] = c[2]; };
names.forEach((nm, ni) => {
  const [name, dir] = nm.includes("/") ? nm.split("/").reverse() : [nm, "mammals"];
  const d = JSON.parse(readFileSync(R + dir + "/" + name + ".json")), shapes = d.sculpt.shape;
  const J = JSON.parse(execFileSync("node", ["jj.mjs", name]).toString());
  const all = shapes.filter((p) => p.op !== "sub").flatMap((p) => p.mirror ? [p, { ...p, c: p.c && z(p.c), a: p.a && z(p.a), b: p.b && z(p.b), pts: p.pts && p.pts.map(z), rot: p.rot && [-p.rot[0], -p.rot[1], p.rot[2]] }] : [p]);
  const F = field(all.map((p) => ({ ...p, attr: [1] })), 1, {});
  const hip = J.legHLu.o, foot = J.legHLl.b;
  const S = hip[1] * (+process.env.SW || 2.0);                 // (the window: 1.6 hip heights square, the hip at 60% across)
  const x0 = hip[0] - S * 0.4, y0 = 0;
  const zs = []; for (let q = -0.5; q <= 0.5; q += 0.025) zs.push(q * hip[1]);
  for (let py = 0; py < H; py++) for (let px = 0; px < PX; px++) {
    const x = x0 + (px / PX) * S, y = y0 + ((H - 1 - py) / H) * S;
    let inside = false; for (const zz of zs) if (F.dist(x, y, zz) < 0) { inside = true; break; }
    if (inside) put(ni * PX + px, py, [90, 90, 100]);
  }
  const P = (v) => [ni * PX + Math.round((v[0] - x0) / S * PX), H - 1 - Math.round((v[1] - y0) / S * H)];
  for (const b of ["legHLu", "legHLl"]) { const a = J[b].a, e = J[b].b; for (let t = 0; t <= 1; t += 0.01) { const [u, v] = P([a[0] + (e[0] - a[0]) * t, a[1] + (e[1] - a[1]) * t]); put(u, v, [220, 30, 30]); } }
  for (let py = 0; py < H; py++) put(ni * PX, py, [0, 0, 0]);
  // a ruler: 5 cm ticks behind the hip, at the hip height
  for (let k = 1; k <= 8; k++) { const [u, v] = P([hip[0] - 0.05 * k, hip[1]]); put(u, v - 1, [0, 120, 0]); put(u, v + 1, [0, 120, 0]); }
});
const raw = Buffer.alloc((W * 3 + 1) * H);
for (let y = 0; y < H; y++) { raw[y * (W * 3 + 1)] = 0; img.copy(raw, y * (W * 3 + 1) + 1, y * W * 3, (y + 1) * W * 3); }
const crc = (b) => { let c, t = []; for (let n = 0; n < 256; n++) { c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } c = 0xffffffff; for (const x of b) c = t[(c ^ x) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
const chunk = (ty, data) => { const l = Buffer.alloc(4); l.writeUInt32BE(data.length); const td = Buffer.concat([Buffer.from(ty), data]); const c = Buffer.alloc(4); c.writeUInt32BE(crc(td)); return Buffer.concat([l, td, c]); };
const ih = Buffer.alloc(13); ih.writeUInt32BE(W, 0); ih.writeUInt32BE(H, 4); ih[8] = 8; ih[9] = 2;
writeFileSync(out, Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk("IHDR", ih), chunk("IDAT", zlib.deflateSync(raw)), chunk("IEND", Buffer.alloc(0))]));
