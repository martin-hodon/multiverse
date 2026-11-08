await import("../canvas_shim.mjs");
import { readFileSync } from "fs"; globalThis.fetch = async (u) => ({ ok: true, json: async () => JSON.parse(readFileSync(new URL(u))) });
const R = "/home/martin/store/apps/multiverse/";
const { KINDS } = await import(R + "creatures.js"); await import(R + "winged.js");
for (const n of ["demon", "angel"]) { const d = JSON.parse(readFileSync(R + `assets/creatures/monsters/${n}.json`)); const m = KINDS.winged(d);
  console.log(n, m.parts.length, m.parts.filter(p=>/^(pec|abs|wHum)/.test(p.id)).map(p=>p.id+JSON.stringify(p.pos?.map(v=>+v.toFixed(3)))).join(" ")); }
