// batmem_gen.mjs IN.json OUT.json -- the bat's wing skin as ONE membrane a wing (bodyspec.js "membrane": a sheet whose
// every vertex rides its own bone), in place of the 80 loose triangle parts a wing it was (each drawn as its own plate,
// so the skin came apart into 160 one-triangle pieces off the body). Same points, same faces, same colour and thickness;
// a vertex on the arm's panels rides the arm, one on the hand's the hand, one on the seam between them both, half each.
import { readFileSync, writeFileSync } from "fs";
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature } = await import(R + "creatures.js");
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const [inp, out] = process.argv.slice(2);
const d = JSON.parse(readFileSync(inp));
const def = buildCreature(JSON.parse(JSON.stringify(d)), new Map()); const s = def.sculpted ? def : sculptOf(markSculpt(def));
const parent = new Map(d.parts.map((p) => [p.id, p.parent]));
const isMem = (p) => p.shape === "tri" && /^wMem/.test(p.id);
const tris = s.sculpted.details.filter((q) => q.type === "tri" && /^wMem/.test(q.bone));
const side = (S) => {
  const T = tris.filter((q) => q.bone.endsWith(S));
  const pts = [], key = new Map(), bonesAt = [], faces = [];
  const vid = (p) => { const k = p.map((v) => Math.round(v * 1e5)).join(","); if (!key.has(k)) { key.set(k, pts.length); pts.push(p.map((v) => +v.toFixed(5))); bonesAt.push(new Set()); } return key.get(k); };
  for (const q of T) { const f = [vid(q.a), vid(q.b), vid(q.c)]; if (new Set(f).size < 3) continue; faces.push(f); for (const v of f) bonesAt[v].add(parent.get(q.bone)); }
  // (the faces wound alike: across each shared edge the neighbour runs it the other way -- the normals then agree)
  const edges = new Map(); faces.forEach((f, i) => { for (let e = 0; e < 3; e++) { const a = f[e], b = f[(e + 1) % 3], k = Math.min(a, b) + "," + Math.max(a, b); (edges.get(k) ?? edges.set(k, []).get(k)).push(i); } });
  const done = new Array(faces.length).fill(false); let flips = 0, comps = 0;
  for (let s0 = 0; s0 < faces.length; s0++) {
    if (done[s0]) continue; comps++; done[s0] = true; const Q = [s0];
    while (Q.length) { const i = Q.pop(), f = faces[i];
      for (let e = 0; e < 3; e++) { const a = f[e], b = f[(e + 1) % 3];
        for (const j of edges.get(Math.min(a, b) + "," + Math.max(a, b))) { if (done[j]) continue; const g = faces[j];
          const same = [0, 1, 2].some((m) => g[m] === a && g[(m + 1) % 3] === b);   // (runs a->b too: wound the other way)
          if (same) { faces[j] = [g[0], g[2], g[1]]; flips++; }
          done[j] = true; Q.push(j); } } }
  }
  // (and the whole sheet's normal up: its top the side seen from above)
  let ny = 0; for (const [a, b, c] of faces) { const u = pts[b].map((v, k) => v - pts[a][k]), w = pts[c].map((v, k) => v - pts[a][k]); ny += u[2] * w[0] - u[0] * w[2]; }
  if (ny < 0) for (const f of faces) [f[1], f[2]] = [f[2], f[1]];
  const bones = [...new Set(bonesAt.flatMap((b) => [...b]))].sort();
  const skin = bonesAt.map((b) => { const L = [...b].map((x) => bones.indexOf(x)).sort(); return L.length === 1 ? L[0] : [L[0], L[1], 0.5]; });
  console.error(S, "pts", pts.length, "faces", faces.length, "flipped", flips, "pieces", comps, "bones", bones.join(","), "shared", skin.filter(Array.isArray).length);
  return { pts, tris: faces.flat(), bones, skin };
};
const L = side("L"), Rr = side("R");
// (is the right wing the left's exact mirror? -- not quite, so each is written out)
const mir = new Set(Rr.pts.map((p) => [p[0], p[1], -p[2]].map((v) => Math.round(v * 1e4)).join(",")));
const miss = L.pts.filter((p) => !mir.has(p.map((v) => Math.round(v * 1e4)).join(","))).length;
console.error("left points without an exactly mirrored right twin:", miss, "(each wing written as it is, not mirrored)");
const t0 = d.parts.find(isMem);
const mems = [["wingSkinL", L], ["wingSkinR", Rr]].map(([id, W]) => ({ id, type: "membrane", pts: W.pts, tris: W.tris, bones: W.bones, skin: W.skin, r: t0.size.r, color: "@mem" }));
d.parts = d.parts.filter((p) => !isMem(p));
d.sculpt.shape = [...d.sculpt.shape.filter((q) => !/^wingSkin/.test(q.id)), ...mems];
writeFileSync(out, JSON.stringify(d, null, 1));
