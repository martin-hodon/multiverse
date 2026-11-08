// the zebra's rest mesh round the tail: what is skinned to the tail bone, and how far from the tail's axis
import { readFileSync } from "fs";
await import("../../canvas_shim.mjs");
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature } = await import(R + "creatures.js");
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const { buildBody } = await import(R + "bodymesh.js");
const index = JSON.parse(readFileSync(R + "assets/index.json"));
const bank = new Map();
for (const c of index.categories) for (const p of c.paths) { try { bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json"))); } catch (e) {} }
const file = process.argv[2];
const d = JSON.parse(readFileSync(file));
const def = buildCreature(d, bank), s = def.sculpted ? def : sculptOf(markSculpt(def));
const B = buildBody(s.sculpted), L = B.lods[0];
const bones = s.sculpted.bones.map((b) => typeof b === "string" ? b : b.id ?? b.name);
console.log("keys", Object.keys(L).join(","), "bones", bones.join(","));
const ti = bones.findIndex((b) => /^tail/.test(b));
const P = L.pos, n = P.length / 3, SI = L.skinIndex ?? L.bone ?? L.si, SW = L.skinWeight ?? L.weight ?? L.sw;
if (!SI) { console.log("no skin arrays"); process.exit(); }
const tw = new Float32Array(n);
for (let v = 0; v < n; v++) for (let k = 0; k < 4; k++) if (bones[SI[4*v+k]]?.startsWith("tail")) tw[v] += SW[4*v+k];
// vertices partly on a tail bone: their spread
let rows = [];
for (let v = 0; v < n; v++) if (tw[v] > .05 && tw[v] < .95) rows.push([P[3*v], P[3*v+1], P[3*v+2], tw[v]]);
rows.sort((a, b) => a[1] - b[1]);
console.log("mixed tail-weight verts", rows.length);
const bins = {};
for (const r of rows) { const k = (Math.round(r[1] * 20) / 20).toFixed(2); (bins[k] ??= []).push(r); }
for (const [k, rs] of Object.entries(bins)) console.log("y", k, "n", rs.length, "x", Math.min(...rs.map((r) => r[0])).toFixed(3), Math.max(...rs.map((r) => r[0])).toFixed(3), "|z|max", Math.max(...rs.map((r) => Math.abs(r[2]))).toFixed(3), "w", (rs.reduce((a, r) => a + r[3], 0) / rs.length).toFixed(2));
