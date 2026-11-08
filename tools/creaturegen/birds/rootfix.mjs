// rootfix.mjs -- every feather blade's ROOT measured against the body's own field (the one bodymesh meshes) and, with
// --patch=<file>, the corrections written out: for each authored feather group whose blades stand off the surface, each
// row's `at` moved in to the surface along the field's normal and on `pen` into it (its `to` kept: the tip stays where
// it was, the blade's root tilts in). Usage: node rootfix.mjs [name,name|all] [--patch=out.json] [--tol=.003] [--pen=.0025]
import { readFileSync, writeFileSync } from "fs";
const R = "/home/martin/store/apps/multiverse/";
globalThis.fetch = async (u) => ({ json: async () => JSON.parse(readFileSync(new URL(u))) });
const { buildCreature } = await import(R + "creatures.js");
const { markSculpt, sculptOf } = await import(R + "bodyspec.js");
const { field, gradient } = await import(R + "sculpt.js");
const index = JSON.parse(readFileSync(R + "assets/index.json"));
const arg = (k, d) => { const a = process.argv.find((x) => x.startsWith(`--${k}=`)); return a ? a.split("=")[1] : d; };
const SMAX = +arg("smax", 1.5), TOL = +arg("tol", .003), FIXAT = +arg("fixat", .0012), PEN = +arg("pen", .0025), SINK = +arg("sink", .06), patchFile = arg("patch", null), verbose = process.argv.includes("-v");
const names = process.argv[2] && !process.argv[2].startsWith("--") && process.argv[2] !== "all" ? process.argv[2].split(",") : null;
const bank = new Map();
for (const c of index.categories) for (const p of c.paths) { try { bank.set(p, JSON.parse(readFileSync(R + "assets/" + p + ".json"))); } catch (e) {} }
const nrm = (v) => { const l = Math.hypot(...v) || 1; return v.map((x) => x / l); };
const crs = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
function rng(seed) {
  let a = (seed >>> 0) || 1;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
const OUT = {
  flight: (t) => { const b = Math.min(1, t / .14) ** .6 * Math.max(0, 1 - t ** 3.2) ** .55; return [b * .42, b]; },
  round: (t) => { const b = Math.sin(Math.PI * Math.min(1, t) ** .8) ** .55 * Math.min(1, t / .1) ** .5; return [b * .9, b]; },
  train: (t) => { const e = 1 / (1 + Math.exp(-(t - .82) / .03)), tipR = t > .93 ? Math.sqrt(Math.max(0, 1 - ((t - .93) / .07) ** 2)) : 1;
                  const b = (.36 + .64 * e) * tipR * Math.min(1, t / .04); return [b, b]; },
};
// (bodymesh.js featherMesh's blades, LOD0, exactly: per blade its root, its row pair and weight, and its two faces' vertices)
function blades(q) {
  const rows = q.rows, Rn = rows.length, n = Math.max(1, q.n ?? 8), r = rng(q.seed ?? 7), out = OUT[q.outline] ?? OUT.round;
  const nt = 10, cs = [-1, -.5, 0, .5, 1], res = [];
  for (let j = 0; j < n; j++) {
    const u = n === 1 ? 0 : j / (n - 1), x = u * (Rn - 1), i0 = Math.min(Rn - 2, Math.floor(x)), t = Rn === 1 ? 0 : x - Math.max(0, i0);
    const ia = Math.max(0, i0), ib = Math.min(Rn - 1, ia + 1), A = rows[ia], B = rows[ib];
    const L = (k) => (A[k] + (B[k] - A[k]) * t);
    const root = [0, 1, 2].map((k) => A.at[k] + (B.at[k] - A.at[k]) * t), jit = (q.jitter ?? 0) * (r() - .5);
    let d = nrm([0, 1, 2].map((k) => A.dir[k] + (B.dir[k] - A.dir[k]) * t));
    const len = L("len") * (1 - (q.vary ?? 0) * r()), w = L("w") * (1 + (r() - .5) * .12);
    const upR = A.up && B.up ? [0, 1, 2].map((k) => A.up[k] + (B.up[k] - A.up[k]) * t) : q.up ?? (() => { const tg = Rn > 1 ? B.at.map((v, k) => v - A.at[k]) : [0, 0, 1], c = crs(tg, d); return c[1] < 0 ? c.map((v) => -v) : c; })();
    let up = nrm(upR.map((v, k) => v - d[k] * dot(upR, d)));
    let side = nrm(crs(d, up));
    if (jit) { const ca = Math.cos(jit), sa = Math.sin(jit); d = nrm(d.map((v, k) => v * ca + side[k] * sa)); side = nrm(crs(d, up)); }
    const lift = (q.lift ?? 0) + (j % 2 ? q.stagger ?? 0 : 0) + j * (q.stack ?? 0);
    r();   // (the tone)
    const camber = (q.camber ?? .1) * w, curve = (q.curve ?? 0) * len, th = Math.max(4e-4, w * .03);
    const sOf = (a) => 1 - (1 - a / nt) ** 1.8, F = [];
    for (let a = 0; a <= nt; a++) { const s = sOf(a), wd = out(s);
      for (const c of cs) { const half = c < 0 ? wd[0] : wd[1], off = w * half * c, bow = camber * Math.max(wd[0], wd[1]) * (1 - c * c);
        F.push([0, 1, 2].map((k) => root[k] + d[k] * len * s + side[k] * off + up[k] * (lift + bow + curve * s * s))); } }
    res.push({ j, ia, ib, t, root: root.map((v, k) => v + up[k] * lift), up, lift, d, len, curve, at0: root, front: F, back: F.map((p) => p.map((v, k) => v - up[k] * th)) });
  }
  return res;
}
// (a point's distance to a triangle: Ericson's closest point)
function triD(p, a, b, c) { return Math.hypot(...triP(p, a, b, c).map((v, k) => v - p[k])); }
function triP(p, a, b, c) {
  const sub = (u, v) => [u[0] - v[0], u[1] - v[1], u[2] - v[2]];
  const ab = sub(b, a), ac = sub(c, a), ap = sub(p, a), d1 = dot(ab, ap), d2 = dot(ac, ap);
  const at = (q) => q;
  if (d1 <= 0 && d2 <= 0) return at(a);
  const bp = sub(p, b), d3 = dot(ab, bp), d4 = dot(ac, bp); if (d3 >= 0 && d4 <= d3) return at(b);
  const vc = d1 * d4 - d3 * d2; if (vc <= 0 && d1 >= 0 && d3 <= 0) { const v = d1 / (d1 - d3); return at(a.map((x, k) => x + ab[k] * v)); }
  const cp = sub(p, c), d5 = dot(ab, cp), d6 = dot(ac, cp); if (d6 >= 0 && d5 <= d6) return at(c);
  const vb = d5 * d2 - d1 * d6; if (vb <= 0 && d2 >= 0 && d6 <= 0) { const w = d2 / (d2 - d6); return at(a.map((x, k) => x + ac[k] * w)); }
  const va = d3 * d6 - d5 * d4; if (va <= 0 && d4 - d3 >= 0 && d5 - d6 >= 0) { const w = (d4 - d3) / ((d4 - d3) + (d5 - d6)); return at(b.map((x, k) => x + (c[k] - x) * w)); }
  const den = 1 / (va + vb + vc), v = vb * den, w = vc * den; return at(a.map((x, k) => x + ab[k] * v + ac[k] * w));
}
const patch = {}, report = [];
for (const [path, d] of bank) {
  if (!path.startsWith("creatures/birds/") || !d?.name) continue;
  if (names && !names.includes(d.name)) continue;
  let B;
  try { const def = buildCreature(d, bank); const s = def.sculpted ? def : sculptOf(markSculpt(def)); B = s.sculpted; } catch (e) { console.log(d.name, "ERR", e.message.slice(0, 90)); continue; }
  const F = field(B.prims, 0), dist = (p) => F.dist(p[0], p[1], p[2]);
  const minD = (P) => P.reduce((m, p) => Math.min(m, dist(p)), 1e9);
  const seen = new Map(), occ = new Map(), fix = {};
  let bad = 0, badParts = 0, worst = 0, layN = 0, layBad = 0; const where = [];
  // (every blade first: a LAYER group's -- `layer: true`, a peacock's train tiers lying on the ground -- may rest on the
  //  blades beneath it instead of the body: it counts as held when its root is within TOL of the body or of a held blade)
  const all = [];
  for (const q of B.details) {
    if (q.type !== "feathers") continue;
    const tw = q.own != null && seen.has(q.own); if (q.own != null && !tw) { seen.set(q.own, occ.get(q.id) ?? 0); occ.set(q.id, (occ.get(q.id) ?? 0) + 1); }
    q._occ = seen.get(q.own);
    for (const b of blades(q)) all.push({ q, tw, b, g: Math.max(minD(b.front), minD(b.back)), gf: [minD(b.front), minD(b.back)].filter((x) => x > TOL).length, rd: dist(b.root) });
  }
  if (process.env.DUMP) for (const e of all) if (process.env.DUMP.split(",").includes(e.q.id) && !e.tw) console.log(e.q.id, e.b.j, "root", e.b.root.map((v) => v.toFixed(3)).join(","), "mid", [0, 15, 30, 40, 45, 50].map((i) => e.b.front[i + 2].map((v) => v.toFixed(3)).join(",")).join(" | "));
  const held = new Set(all.filter((e) => !e.q.layer).map((e, i) => e));
  const lay = all.filter((e) => e.q.layer); layN = lay.length;
  const bladeP = (p, e) => { let m = 1e9, best = null; for (const P of [e.b.front, e.b.back]) for (let a = 0; a < 10; a++) for (let c = 0; c < 4; c++) {
      const v0 = P[a * 5 + c], v1 = P[a * 5 + c + 1], v2 = P[a * 5 + c + 5], v3 = P[a * 5 + c + 6];
      for (const t of [[v0, v2, v1], [v1, v2, v3]]) { const q = triP(p, ...t), dd = Math.hypot(...q.map((v, k) => v - p[k])); if (dd < m) { m = dd; best = q; } } } return [m, best]; };
  const bladeD = (p, e) => bladeP(p, e)[0];
  let grew = true;
  for (const e of lay) if (e.rd <= TOL) { held.add(e); }
  while (grew) { grew = false;
    for (const e of lay) { if (held.has(e)) continue;
      for (const h of held) { if (h === e || h.q === e.q && h.tw === e.tw) continue; if (bladeD(e.b.root, h) <= TOL) { held.add(e); grew = true; e.on = h.q.id + "#" + h.b.j; break; } } } }
  // (an unheld layer blade: its root SNAPPED onto the nearest held blade, a hair into it -- or into the body, if that is
  if (process.env.ON) console.log(lay.map((e) => e.q.id + "#" + e.b.j + (e.rd <= TOL ? ":body" : ":" + e.on)).join(" "));
  // (a train blade is SUPPORTED when its root is within TOL of the body, or of a supported blade of another group -- the
  //  train blade under it; the first layer's roots are in the body, the later layers rest on the layers below)
  if (process.env.PROBE) for (const e of lay) { if (held.has(e) || e.rd < .1) continue; const b = e.b;
    const others = all.filter((h) => h.q !== e.q && h.q.layer);
    const at = (sv) => b.at0.map((v, k) => v + b.d[k] * b.len * sv + b.up[k] * (b.lift + b.curve * sv * sv));
    let up = null; for (let dy = 0; dy < .15; dy += .002) { const P = [b.root[0], b.root[1] + dy, b.root[2]]; const h = others.find((h) => bladeD(P, h) <= TOL); if (h) { up = [dy, h.q.id + "#" + h.b.j]; break; } }
    let ax = null; for (let sv = 0; sv < .6; sv += .005) { const P = at(sv); const h = others.find((h) => bladeD(P, h) <= TOL); if (h) { ax = [sv, h.q.id + "#" + h.b.j]; break; } }
    console.log("PROBE", e.q.id + "#" + b.j, "z", b.root[2].toFixed(2), "len", b.len.toFixed(2), "up", up ? up[0].toFixed(3) + " " + up[1] : "-", "axis", ax ? ax[0].toFixed(3) + " (" + (ax[0] * b.len * 100).toFixed(0) + "cm) " + ax[1] : "-"); }
  const unheld = lay.filter((e) => !held.has(e)).map((e) => { let m = 1e9, pt = null; for (const h of held) { if (h === e || h.q === e.q && h.tw === e.tw) continue; const [dd, q_] = bladeP(e.b.root, h); if (dd < m) { m = dd; pt = q_; } } return Object.assign(e, { dH: m, pH: pt }); });
  const dMin = Math.min(1e9, ...unheld.map((e) => e.dH));
  // (the layers wait until every blade rooted in the body is in: what they rest on must not move under them)
  const bodyFirst = all.some((e) => !e.q.layer && e.q.own != null && e.g > FIXAT);
  for (const e of all) {
    const { q, tw, b, g, gf } = e;
    if (q.layer) {
      if (held.has(e)) continue;
      layBad++; where.push(`${q.id}${tw ? "'" : ""}#${b.j} unsupported (body ${(e.rd * 100).toFixed(1)}cm, nearest supporting blade ${(e.dH * 100).toFixed(1)}cm)`);
      if (e.rd > SINK && !q.reach) continue;   // (a TRAIN blade is not moved: it rests on the body or on the train blade under it, or is reported)
      if (q.reach) {
        // (a REACHING blade -- the ramp under the slope's end: its root carried back along its own axis until it meets a
        //  supported blade, the blade lengthened from the root, its line and front end where they were)
        const near = [...held].filter((h) => h !== e && h.q !== e.q);
        const at = (sv) => b.at0.map((v, k) => v + b.d[k] * b.len * sv + b.up[k] * b.lift);
        let sHit = null;
        for (let sv = 0; sv >= -SMAX && near.length; sv -= .004) { const P = at(sv); if (near.some((h) => bladeD(P, h) <= TOL * .8)) { sHit = sv; break; } }
        if (sHit == null) continue;
        let mv = b.d.map((v) => v * b.len * sHit); if (tw) mv[2] = -mv[2];
        const G = (fix[q.id + "@" + q._occ] ??= {});
        for (const [ri, wt] of [[b.ia, 1 - b.t], [b.ib, b.t]]) { if (wt < 1e-3 && b.ia !== b.ib) continue;
          const old = G[ri]; if (!old || Math.hypot(...mv) > Math.hypot(...old)) G[ri] = mv.map((v) => +v.toFixed(5)); }
        continue;
      }
      // (else the FIRST layer, its root near the rump: sunk into the body like any other blade, below)
    } else if (gf) { bad += gf; worst = Math.max(worst, g); if (q.own == null) badParts += gf; where.push(`${q.id}${tw ? "'" : ""}#${b.j} ${(g * 100).toFixed(1)}cm`); }
    if (q.own == null) continue;
    // (the root's depth wanted: PEN inside; the move it needs, along the field's normal at the surface below it)
    if (g <= FIXAT && !q.layer) continue;   // (in, or touching: left as it is)
    let p = b.root.slice();
    for (let it = 0; it < 60; it++) { const f = dist(p); if (Math.abs(f + PEN) < 2e-4) break; const gN = gradient(F.dist, p[0], p[1], p[2]); p = p.map((v, k) => v - gN[k] * (f + PEN)); }
    let mv = p.map((v, k) => v - b.root[k]);
    if (tw) mv[2] = -mv[2];   // (the twin's move, mirrored back onto the authored side)
    const G = (fix[q.id + "@" + q._occ] ??= {});
    for (const [ri, wt] of [[b.ia, 1 - b.t], [b.ib, b.t]]) {
      if (wt < 1e-3 && b.ia !== b.ib) continue;
      // (each row moved by the deepest any of its blades asks, so a blade between two rows is in at both ends)
      const old = G[ri]; const m2 = (v) => Math.hypot(...v);
      if (!old || m2(mv) > m2(old)) G[ri] = mv.map((v) => +v.toFixed(5));
    }
  }
  bad += layBad;
  report.push([d.name, bad, badParts, worst]);
  console.log(d.name.padEnd(16), "blade faces off >", (TOL * 100).toFixed(1) + "cm:", String(bad).padStart(3), layN ? `(layered ${layN}, unheld ${layBad})` : "", badParts ? `(from parts ${badParts})` : "", bad ? `worst ${(worst * 100).toFixed(1)}cm` : "", verbose ? where.slice(0, +(process.env.NW ?? 12)).join("  ") : "");
  if (Object.keys(fix).length) patch[path.split("/").pop()] = fix;
}
if (patchFile) writeFileSync(patchFile, JSON.stringify(patch));
