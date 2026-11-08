// builds species.js's sea creatures outside the browser (the section between the fish and THE DEFINITIONS)
import { readFileSync, writeFileSync } from "fs";
const R = "/home/martin/store/apps/multiverse/";
const D = "/home/martin/store/apps/multiverse/tools/creaturegen/sc/others/";
const s = readFileSync(R + "species.js", "utf8");
const a = s.indexOf("// Generative pond fish"), b = s.indexOf("// ---- THE DEFINITIONS");
writeFileSync(D + "sea_t.mjs", `import { markSculpt } from "${R}bodyspec.js";\n` + s.slice(a, b));
const { sculptOf } = await import(R + "bodyspec.js");
const { buildBody } = await import(R + "bodymesh.js");
const m = await import(D + "sea_t.mjs");
const defs = [["dolphin", m.makeDolphin()], ["shark", m.makeShark()]];
for (let i = 1; i < 40; i++) { const f = m.makeFish({ seed: i + 5 }); if (!defs.some(([, d]) => d === f)) defs.push([`fish${defs.length - 1}`, f]); }
const dump = process.argv[2];
for (const [n, d] of defs) {
  try {
    const sd = sculptOf(d); const sc = sd.sculpted; const B = buildBody(sc);
    console.log(n.padEnd(9), "prims", sc.prims.length, "det", sc.details.length, "eyes", sc.eyes.length, "cell", sc.mesh.cell.toFixed(4), "tris", B.stats.tris.join("/"), "ms", B.stats.ms.all);
    if (dump && n === dump) writeFileSync(D + "def_" + n + ".json", JSON.stringify(d));
  } catch (e) { console.log("ERR", n, e.stack.split("\n").slice(0, 3).join(" | ")); }
}
// export for viewing in assets.html (temporary: assets/creatures/others/zz_*.json, deleted after)
if (process.argv[3] === "export") for (const [n, d] of [["dolphin", m.makeDolphin()], ["shark", m.makeShark()], ["fish", m.makeFish({ seed: 9 })]]) {
  const flags = d.sculptScale ? { sculptScale: d.sculptScale } : {};
  writeFileSync(D + `zz_${n}.json`, JSON.stringify({ name: "zz_" + n, kind: "parts", facet: false, flags, parts: d.parts, sculpt: d.sculpt }));
}
