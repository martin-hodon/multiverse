// narwhal_stock.mjs: samples the narwhal's sculpted tail stock (the gridded shapes only, from the asset narwhal.py
// last wrote) -- its top and bottom at each x and z -- into narwhal_stock.json, so narwhal.py can lay the flukes' root
// over it (the wedge that spreads out of the stock's sides follows its surface). Run: node narwhal_stock.mjs
import { field } from "../../../../../sculpt.js";
import fs from "fs";
const HERE = new URL(".", import.meta.url).pathname;
const d = JSON.parse(fs.readFileSync(HERE + "../../../../../assets/creatures/sea/narwhal.json"));
const shapes = d.sculpt.shape.filter((p) => p.op !== "paint" && p.op !== "sub" && !["feathers", "membrane"].includes(p.type) && (!p.when || (d.params ?? {})[p.when] !== false));
const F = field(shapes.map((p) => ({ ...p, attr: [1] })), 1, {});
const { x0, x1, dx, zs } = JSON.parse(fs.readFileSync(HERE + "narwhal_stock_req.json"));
const edge = (x, z, up) => {   // (the surface's height at (x, z) from above or below; null where it is not there)
  let y = up ? 0.4 : -0.4, s = up ? -0.004 : 0.004;
  for (let i = 0; i < 200; i++, y += s) if (F.dist(x, y, z) < 0) {
    let a = y - s, b = y;
    for (let k = 0; k < 30; k++) { const m = (a + b) / 2; (F.dist(x, m, z) < 0 ? (b = m) : (a = m)); }
    return +((a + b) / 2).toFixed(5);
  }
  return null;
};
const rows = [];
for (let x = x0; x >= x1 - 1e-9; x -= dx) rows.push({ x: +x.toFixed(5), top: zs.map((z) => edge(x, z, true)), bot: zs.map((z) => edge(x, z, false)) });
fs.writeFileSync(HERE + "narwhal_stock.json", JSON.stringify({ zs, rows }));
console.log(rows.map((r) => `${r.x.toFixed(3)} ${r.top.map((v) => v ?? "-").join(" ")} | ${r.bot.map((v) => v ?? "-").join(" ")}`).join("\n"));
