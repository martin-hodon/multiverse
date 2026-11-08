// dragons.js dragonBatWing (not exported) run as it stands today: node dwing.mjs '<json opts>' '[at]' -> {L: {parts, geo}, R: {...}}
import { readFileSync } from "fs";
const s = readFileSync("/home/martin/store/apps/multiverse/dragons.js", "utf8");
const h = s.slice(s.indexOf("const add = "), s.indexOf("\n", s.indexOf("const lerp = ")));
const a = s.indexOf("const D2R = Math.PI / 180;"), b = s.indexOf("return { parts, geo };", a);
const src = h.split("\n").filter((l) => /^const (add|sub|mul|lerp)\b|^const add/.test(l)).join("\n") + "\n" + s.slice(a, b) + "return { parts, geo };\n}\nreturn dragonBatWing;";
const dragonBatWing = new Function(src)();
const o = JSON.parse(process.argv[2]), at = JSON.parse(process.argv[3]);
const out = {};
for (const sd of [1, -1]) out[sd > 0 ? "L" : "R"] = dragonBatWing(sd, [at[0], at[1], sd * at[2]], o);
console.log(JSON.stringify(out));
