await import("../canvas_shim.mjs");
const R = "/home/martin/store/apps/multiverse/";
import { readFileSync } from "fs"; globalThis.fetch = async (u) => ({ ok: true, json: async () => JSON.parse(readFileSync(new URL(u))) });
const { makePerson } = await import(R + "people.js");
const m = makePerson({"seed":52,"kind":"man","height":2.0,"skin":0x8e2a1e,"outfit":{"named":"demon","hair":"shaved"},"physique":"heroic"});
for (const p of m.parts.slice(0,8)) console.log(p.id, JSON.stringify(p.pivot ?? null), p.geomRot ?? "", p.parent, p.shape, JSON.stringify(p.size), JSON.stringify(p.pos), JSON.stringify(p.rot ?? null), p.color?.toString(16), p.k ?? "", p.flat ?? "", p.pat ?? "");
