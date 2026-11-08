// dump every coat/variant the game builds, as JSON hashes -- to compare before/after the variants rework
import { readFileSync, writeFileSync } from "fs";
import { createHash } from "crypto";
globalThis.fetch = async (u) => ({ ok: true, json: async () => JSON.parse(readFileSync(new URL(u))) });
const anyp = () => new Proxy(function () {}, { get: (t, k) => k === Symbol.toPrimitive ? () => 0 : k === "data" ? new Uint8ClampedArray(4 * 4096 * 4096 > 0 ? 64 : 0) : anyp(), apply: () => anyp(), set: () => true });
globalThis.OffscreenCanvas = class { constructor(w, h) { this.width = w; this.height = h; } getContext() { return new Proxy({}, { get: (t, k) => k === "getImageData" || k === "createImageData" ? (x, y, w, h) => ({ data: new Uint8ClampedArray((w || 1) * (h || 1) * 4), width: w, height: h }) : typeof k === "string" && /^(fill|stroke|set|draw|put|begin|close|move|line|arc|rect|save|restore|translate|rotate|scale|clip|quad|bezier|ellipse|clear|transform|reset)/.test(k) ? () => {} : k === "createLinearGradient" || k === "createRadialGradient" || k === "createPattern" ? () => ({ addColorStop() {} }) : k === "measureText" ? () => ({ width: 1 }) : undefined, set: () => true }); } };
globalThis.Path2D = class { constructor() { return new Proxy({}, { get: () => () => {} }); } };
globalThis.ImageData = class { constructor(w, h) { this.width = w; this.height = h; this.data = new Uint8ClampedArray(w * h * 4); } };
const R = "/home/martin/store/apps/multiverse/";
const S = await import(R + "species.js");
const h = (o) => createHash("md5").update(JSON.stringify(o, (k, v) => typeof v === "number" ? +v.toFixed(6) : v)).digest("hex").slice(0, 10);
const out = {};
await (S.loadSpecies?.() ?? S.ready ?? Promise.resolve());
const col = (d) => { const p = (d.parts ?? []).find((q) => /body|torso|trunk/.test(q.id ?? "")) ?? d.parts?.[0]; return (p?.color ?? d.c?.body ?? 0).toString(16); };
const sc = (d) => JSON.stringify(d.sculpt?.shape?.find((q) => q.id === "barrel" || q.color !== undefined)?.color ?? null);
const names = JSON.parse(readFileSync(R + "assets/creatures/mammals/horse.json")).coats.map((c) => c.name);
const n = names.length;
console.log("riders (coatDef horse i*5):", [0, 1, 2, 3, 4, 5].map((i) => names[(i * 5) % n]).join(" | "));
console.log("loose (coatDef horse 9+i):", [0, 1, 2, 3].map((i) => names[(9 + i) % n]).join(" | "));
for (const s of [0, 1]) console.log(`paddock townSeed%2=${s}:`, [0, 1, 2, 3].map((k) => names[(k * 2 + 1 + s) % n]).join(" | "));
const seen = new Set(); for (let i = 0; i < n; i++) { const d = S.coatDef("horse", i); seen.add(JSON.stringify(d.sculpt?.shape?.map((q) => q.color)) + JSON.stringify(d.parts?.map((q) => q.color))); }
console.log("distinct horse coat builds:", seen.size, "of", n);
const cs = new Set(); for (let s = 1; s < 60; s++) cs.add(S.makeCat({ seed: s }));
console.log("distinct cats over 59 seeds:", cs.size);
