import fs from "fs"; import path from "path";
import { buildItem } from "/home/martin/store/apps/multiverse/items.js";
const A = "/home/martin/store/apps/multiverse/assets/";
const bank = new Map();
const walk = (d) => { for (const f of fs.readdirSync(d)) { const p = path.join(d, f); if (fs.statSync(p).isDirectory()) walk(p); else if (f.endsWith(".json")) bank.set(p.slice(A.length, -5), JSON.parse(fs.readFileSync(p))); } };
walk(A + "items");
const lib = bank.get("items/materials").materials;
const which = process.argv.slice(2);
for (const k of [...bank.keys()].filter((k) => k.startsWith("items/modern/") && (!which.length || which.some((w) => k.includes(w))))) {
  try { const b = buildItem(k, bank, lib, { seed: 3 }); const miss = [...new Set(b.groups.filter((g) => g.material.missing).map((g) => g.material.missing))];
    const nan = b.groups.some((g) => g.pos.some((v) => !isFinite(v)));
    console.log(k.padEnd(44), String(b.tris).padStart(6), "tris", b.bounds.lo.map((v) => v.toFixed(2)).join(","), "..", b.bounds.hi.map((v) => v.toFixed(2)).join(","), miss.length ? "MISSING " + miss : "", nan ? "NaN!" : "");
  } catch (e) { console.log(k, "ERROR", e.message.slice(0, 200)); }
}
