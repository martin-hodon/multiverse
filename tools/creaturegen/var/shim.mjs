import { readFileSync } from "fs";
import { existsSync } from "fs";
globalThis.fetch = async (u) => ({ ok: true, json: async () => { const f = new URL(u); if (existsSync(f)) return JSON.parse(readFileSync(f)); const d = JSON.parse(readFileSync(new URL("../mammals/deer.json", f))); d.name = String(f).split("/").pop().replace(".json", ""); return d; } });
const anyp = () => new Proxy(function () {}, { get: (t, k) => k === Symbol.toPrimitive ? () => 0 : k === "data" ? new Uint8ClampedArray(4 * 4096 * 4096 > 0 ? 64 : 0) : anyp(), apply: () => anyp(), set: () => true });
globalThis.OffscreenCanvas = class { constructor(w, h) { this.width = w; this.height = h; } getContext() { return new Proxy({}, { get: (t, k) => k === "getImageData" || k === "createImageData" ? (x, y, w, h) => ({ data: new Uint8ClampedArray((w || 1) * (h || 1) * 4), width: w, height: h }) : typeof k === "string" && /^(fill|stroke|set|draw|put|begin|close|move|line|arc|rect|save|restore|translate|rotate|scale|clip|quad|bezier|ellipse|clear|transform|reset)/.test(k) ? () => {} : k === "createLinearGradient" || k === "createRadialGradient" || k === "createPattern" ? () => ({ addColorStop() {} }) : k === "measureText" ? () => ({ width: 1 }) : undefined, set: () => true }); } };
globalThis.Path2D = class { constructor() { return new Proxy({}, { get: () => () => {} }); } };
globalThis.ImageData = class { constructor(w, h) { this.width = w; this.height = h; this.data = new Uint8ClampedArray(w * h * 4); } };

