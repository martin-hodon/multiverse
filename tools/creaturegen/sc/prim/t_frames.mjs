// each bone's REST frame (bodyspec convert: as built) and its STANDING frame (skeleton.js writeAnimal, amp 0) as JSON
import { readFileSync } from "fs";
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const THREE = await import("three");
const { buildCreature } = await import(R + "creatures.js");
const { writeAnimal, compileDef, lastFrames } = await import(R + "skeleton.js");
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const index = JSON.parse(readFileSync(R + "assets/index.json"));
const bank = new Map();
for (const c of index.categories) for (const p of c.paths) { try { bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json"))); } catch {} }
const [name, TS = "0", ampS = "0"] = process.argv.slice(2);
const d = JSON.parse(JSON.stringify([...bank.values()].find((x) => x?.name === name)));
delete d.sculpt;
const def = buildCreature(d, bank), parts = compileDef(def), n = parts.length;
const A = new Float32Array(n * 3), B = new Float32Array(n * 3), C = new Float32Array(n * 3);
writeAnimal({ parts, position: new THREE.Vector3(), rotY: 0, base: 0, amp: +ampS, wingT: 0 }, +TS, A, B, C);
const out = {};
for (let i = 0; i < n; i++) { const p = def.parts[i]; out[p.id] = { posed: [...lastFrames()[i].elements], pos: p.pos, len: p.size?.len ?? null, parent: p.parent ?? null, level: !!p.level }; }
// rest: chain pos/rot as bodyspec convert does
const idx = new Map(def.parts.map((p, i) => [p.id, i])), W = [];
for (let i = 0; i < n; i++) {
  const p = def.parts[i], m = new THREE.Matrix4().compose(new THREE.Vector3(...(p.pos ?? [0, 0, 0])), new THREE.Quaternion().setFromEuler(new THREE.Euler(...(p.rot ?? [0, 0, 0]).map((x) => x * Math.PI / 180))), new THREE.Vector3(...(p.scale ?? [1, 1, 1])));
  let w = p.parent ? W[idx.get(p.parent)].clone().multiply(m) : m;
  if (p.level && p.parent) { const t = new THREE.Vector3().setFromMatrixPosition(w); w = m.clone(); w.setPosition(t); }
  W.push(w); out[p.id].rest = [...w.elements];
}
console.log(JSON.stringify(out));
