await import("../canvas_shim.mjs");
import { readFileSync } from "fs";
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature } = await import(R + "creatures.js");
const sp = await import(R + "species.js").catch((e) => ({ err: e.message }));
console.log(Object.keys(sp).filter((k) => /coat|variant/i.test(k)), sp.err ?? "");
