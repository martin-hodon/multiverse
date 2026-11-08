// THE WORLD'S BURROWS, ANTHILLS AND NESTS (2026-11-08): where each goes and who lives there. The things themselves are
// burrows.js (a hole in the ground, a tunnel, the spoil), ants.js (a wood ants' mound and its ants), nests.js (sticks in
// a tree's crown, reeds by the water); what each kind is -- its size, its colours, which species dig or build it -- is
// its asset (assets/nature/*). This puts them in the world once the ground has arrived (index.html, after terrainReady):
//   BURROWS: for each kind, for the species of the world's cast that dig it (the asset's `species`), one burrow in that
//     animal's range near where it is, on ground that suits it (a bank, a slope; `where: bank` by the water), clear of the
//     buildings, the roads, the trees and the water; a sett's several mouths shared out among its animals. Each animal
//     that walks gets a DEN (burrows.js makeDen): it goes home now and then, stands at the mouth, goes in and comes out.
//   ANTHILLS: at the forest's edge (in the sun, near a tree), else by a tree in the meadow -- their trails kept to dry,
//     open ground.
//   NESTS: in the crowns of trees near their birds (the heronry near the water), the eyrie in the tallest tree, the
//     ducks', geese's and swans' on dry ground at the water's edge; some with the bird stood on or by it (a figure of
//     the herd that stays put: a heron on its platform, the eagle sat on its eyrie, a swan by its mound).
// One terrain sampling for all of them (burrows.js terrainSampler: the DRAWN ground, which is what they must meet).
//
//   const N = placeNature(W)    // W: the world's helpers (below) -> { burrows, dens, anthills, ants, nests, birds, update }
import * as THREE from "three";
import { rng } from "./flora.js";
import { terrainSampler, burrowMesh, burrowGeometry, findBurrowSite, makeDen } from "./burrows.js";
import { createAnts } from "./ants.js";
import { nestBlocks, nestMesh, crownFork } from "./nests.js";
import { blockMesh } from "./blocks.js";
import { float, positionWorld, vertexColor } from "three/tsl";
import { setPits, markGroundProp, groundHole, GROUND_HOLES, soilGrain, groundEarth, earthOver } from "./grass.js";
import { litMaterial } from "./light.js";
import { snowyLit } from "./windowframes.js";
// EARTH: lit, its colour broken by the soil's grain per pixel (grass.js soilGrain) -- the tunnels' walls, the heaps
const soily = (m) => { m.colorNode = m.colorNode.mul(soilGrain({ wp: positionWorld })); return m; };

// W: { scene, ground (the terrain's group), groundH, waterSD, ok(x, z, m) (dry, open, m clear of everything),
//      clear(x, z, m) (clear of buildings, roads, trees -- may be by the water), trees (treeCols), herd, defOf(name),
//      PERCHERS, ASSETS, seed, forest: { x, z, R } | null, you() (the eye: a Vector3), night() }
export function placeNature(W) {
  const t0 = performance.now(), r = rng(W.seed * 113 + 29), A = W.ASSETS;
  const kinds = (dir) => [...A.keys()].filter((p) => p.startsWith(`nature/${dir}/`)).map((p) => ({ path: p, spec: A.get(p) }));
  const animals = (nm) => (W.herd?.animals ?? []).filter((a) => a.name === nm && a.w && !a.nest);
  const avoid = [], skipped = [];   // (skipped: [species, why] -- none of its kind placed)   // (what is placed: the next keeps clear)
  const free = (x, z, m) => !avoid.some((q) => Math.hypot(q.x - x, q.z - z) < q.r + m);
  const slope = (x, z) => Math.hypot(W.groundH(x + .5, z) - W.groundH(x - .5, z), W.groundH(x, z + .5) - W.groundH(x, z - .5));
  // a point drawn round (x, z) within d metres, inside the range f if given
  const around = (x, z, d, f) => () => {
    for (let k = 0; k < 30; k++) {
      const a = r() * Math.PI * 2, s = Math.sqrt(r()) * d, px = x + Math.cos(a) * s, pz = z + Math.sin(a) * s;
      if (!f || (px > f.x0 && px < f.x1 && pz > f.z0 && pz < f.z1 && (!f.inside || f.inside(px, pz)))) return [px, pz];
    }
    return [x + (r() - .5) * 4, z + (r() - .5) * 4];
  };
  // (a point moved onto the line `d` metres from the water's edge: a few steps down the signed distance's slope)
  const toShore = (x, z, d) => {
    for (let k = 0; k < 4; k++) {
      const sd = W.waterSD(x, z), gx = (W.waterSD(x + .5, z) - W.waterSD(x - .5, z)), gz = (W.waterSD(x, z + .5) - W.waterSD(x, z - .5)), g2 = gx * gx + gz * gz;
      if (!(g2 > 1e-6) || !(Math.abs(sd) < 400)) break;
      x -= gx * (sd - d) / g2; z -= gz * (sd - d) / g2;
    }
    return [x, z];
  };
  const bankOk = (x, z, m) => { const sd = W.waterSD(x, z); return sd > .5 && sd < 3.5 && W.clear(x, z, m * .5) && free(x, z, m * .5); };

  // ---- BURROWS: where (groundH is enough to choose) ----
  const plans = [];
  for (const { path, spec } of kinds("burrows")) for (const nm of spec.species ?? []) {
    const who = animals(nm);
    if (!who.length) { if (W.defOf(nm)) skipped.push([nm, "no walker"]); continue; }
    const sp = { ...spec, r: (spec.r ?? .15) * (spec.sizes?.[nm] ?? 1) };
    const p = who[0].position, bank = spec.where === "bank";
    const ok = bank ? bankOk : (x, z, m) => W.ok(x, z, m) && free(x, z, m);
    // (near it first, then farther: a forest-dweller's range is thick with trees, a rat's is the town)
    let site = null;
    for (const d of bank ? [60, 200, 400] : [30, 80, 160]) {
      site = findBurrowSite(sp, { spawn: around(p.x, p.z, d, bank || d > 30 ? null : who[0].w.f), near: [p.x, p.z], groundH: W.groundH, ok, r, avoid: [] });
      if (site) break;
    }
    if (!site) { skipped.push([nm, "no ground"]); continue; }
    const reach = (sp.len ?? 1.2) * 2.4 + sp.r * ((sp.heap?.len ?? 6) + 6) + 1.5;
    for (const m of site.mouths) avoid.push({ x: m.x, z: m.z, r: reach });
    plans.push({ path, nm, spec: sp, site, who, reach });
  }
  // ---- ANTHILLS: at the forest's edge, by a tree, in the open ----
  const ah = A.get("nature/anthill"), hills = [];
  if (ah) {
    const nearTree = (x, z) => W.trees.reduce((b, t) => Math.min(b, Math.hypot(t.x - x, t.z - z) - t.r), 1e9);
    const F = W.forest;
    for (let k = 0; k < 400 && hills.length < (ah.n ?? 2); k++) {
      let x, z;
      if (F) { const a = r() * Math.PI * 2, d = F.R * (.75 + .4 * r()); x = F.x + Math.cos(a) * d; z = F.z + Math.sin(a) * d; }
      else if (W.trees.length) { const t = W.trees[Math.floor(r() * W.trees.length)], a = r() * Math.PI * 2; x = t.x + Math.cos(a) * (2.5 + r() * 3); z = t.z + Math.sin(a) * (2.5 + r() * 3); }
      else break;
      const nt = nearTree(x, z);
      if (nt < 1.8 || nt > 6 || slope(x, z) > .25 || !W.ok(x, z, 2) || !free(x, z, 3) || hills.some((h) => Math.hypot(h.x - x, h.z - z) < 30)) continue;
      hills.push({ x, z });
      avoid.push({ x, z, r: 3 });
    }
  }
  const ants = hills.length ? createAnts(W.scene, hills, { seed: W.seed, spec: { ...ah, ants: ah.ants }, trailOk: (x, z) => W.ok(x, z, .3) }) : null;
  // ---- NESTS: in the trees, by the water ----
  const used = new Set(), treeNests = [], groundNests = [], birds = [];
  const tall = W.trees.filter((t) => t.h > 5 && t.boughs?.length);
  for (const { path, spec } of kinds("nests")) for (const nm of spec.species ?? []) {
    const def = W.defOf(nm);   // (the bird at the nest: only if its kind is drawn in this world -- the nest is there anyway)
    const who = animals(nm), p = who[0]?.position ?? { x: 0, z: 0 };
    if (spec.where === "crown" || spec.where === "tall") {
      let pool = tall.filter((t) => !used.has(t) && (spec.near !== "water" || (W.waterSD(t.x, t.z) > 2 && W.waterSD(t.x, t.z) < 45)));
      if (!pool.length) { skipped.push([nm, "no tree"]); continue; }
      // (the tallest, or the nearest its birds -- the first of them with a fork to build in)
      const score = spec.where === "tall" ? (t) => -t.h * (t.evergreen ? 1.1 : 1) : (t) => Math.hypot(t.x - p.x, t.z - p.z) - t.h;
      pool = pool.map((t) => [score(t), t]).sort((a, b) => a[0] - b[0]).map((q) => q[1]);
      const first = pool.slice(0, 40).find((t) => crownFork(t, spec.where === "tall" ? .92 : .82, W.groundH(t.x, t.z)));
      if (!first) { skipped.push([nm, "no fork"]); continue; }
      const group = [first, ...pool.filter((t) => t !== first && Math.hypot(t.x - first.x, t.z - first.z) < 18).sort((a, b) => Math.hypot(a.x - first.x, a.z - first.z) - Math.hypot(b.x - first.x, b.z - first.z)).slice(0, (spec.colony ?? 1) - 1)];
      group.forEach((t, i) => {
        const at = crownFork(t, spec.where === "tall" ? .92 : .82, W.groundH(t.x, t.z));
        if (!at) return;
        used.add(t);
        const n = { spec: { ...spec, eggs: spec.eggsBy?.[nm] ?? spec.eggs }, at, yaw: r() * 6.28, seed: W.seed * 7 + treeNests.length + 1, nm, tree: t };
        treeNests.push(n);
        if (i === 0 && def && r() < (spec.bird ?? 0)) birds.push({ def, n });
      });
    } else if (spec.where === "water") {
      const sz = spec.sizes?.[nm] ?? 1, sp = { ...spec, r: (spec.r ?? .2) * sz, stick: (spec.stick ?? .02) * Math.sqrt(sz), length: (spec.length ?? [.2, .3]).map((v) => v * sz), eggs: spec.eggsBy?.[nm] ?? spec.eggs };
      let best = null, bs = 1e9;
      for (let k = 0; k < 480; k++) {
        const spawn = around(p.x, p.z, k < 160 ? 70 : k < 320 ? 160 : 320, null);
        const [x, z] = toShore(...spawn(), 1.2 + r() * 1.2), sd = W.waterSD(x, z);
        if (!(sd > .7 && sd < 2.6) || !W.clear(x, z, sp.r + .5) || !free(x, z, sp.r + 1) || slope(x, z) > .35) continue;
        const s = Math.hypot(x - p.x, z - p.z) * .02 + slope(x, z) * 2 + Math.abs(sd - 1.4) * .3 + r() * .1;
        if (s < bs) { bs = s; best = [x, z]; }
      }
      if (!best) { skipped.push([nm, "no shore"]); continue; }
      avoid.push({ x: best[0], z: best[1], r: sp.r + 1.5 });
      const n = { spec: sp, x: best[0], z: best[1], yaw: r() * 6.28, seed: W.seed * 11 + groundNests.length + 1, nm };
      groundNests.push(n);
      if (def && r() < (spec.bird ?? 0)) birds.push({ def, n, by: true });
    }
  }
  // ---- the drawn ground, once, round every one of them ----
  const spots = [...plans.flatMap((q) => q.site.mouths.map((m) => ({ x: m.x, z: m.z, r: q.reach }))),
                 ...(ants?.hills ?? []).map((h) => ({ x: h.x, z: h.z, r: h.half + 1 })),
                 ...groundNests.map((n) => ({ x: n.x, z: n.z, r: n.spec.r * 1.5 + 1 }))];
  const S = terrainSampler(W.ground, spots, W.groundH);
  const tSample = performance.now();
  // ---- burrows: the tunnels (one mesh), the heaps (one a burrow), the holes, the dens ----
  const tun = { P: [], C: [], I: [] }, heapMat = soily(snowyLit()), pits = [], burrows = [], dens = [];
  for (const q of plans) {
    const B = burrowMesh(q.spec, q.site, S.at, { seed: W.seed * 17 + burrows.length });
    const o = tun.P.length / 3;
    tun.P.push(...B.tunnel.P); tun.C.push(...B.tunnel.C); tun.I.push(...B.tunnel.I.map((i) => i + o));
    pits.push(...B.pits);
    const m0 = q.site.mouths[0], y0 = S.at(m0.x, m0.z);
    const hp = { P: B.heap.P.map((v, k) => v - (k % 3 === 0 ? m0.x : k % 3 === 1 ? y0 : m0.z)), C: B.heap.C, I: B.heap.I };
    const heap = new THREE.Mesh(burrowGeometry(hp), heapMat);
    heap.position.set(m0.x, y0, m0.z); heap.updateMatrix(); heap.matrixAutoUpdate = false; heap.updateMatrixWorld(true);
    heap.name = "spoil heap"; heap.userData.noMerge = true;
    W.scene.add(heap); markGroundProp(heap);
    burrows.push({ kind: q.path.split("/").pop(), species: q.nm, x: m0.x, z: m0.z, mouths: B.mouths, top: B.top, heap });
    // its animals: the walkers each to a mouth of its own (a sett's badgers), going home now and then
    q.who.forEach((a, i) => {
      const w = a.w;
      if (w.alt > 0 || w.percher || w.skysteed || w.surface !== undefined) return;
      const m = B.mouths[i % B.mouths.length];
      const out = () => w.active === "night" ? W.night() : w.active === "day" ? !W.night() : true;
      w.den = makeDen(w, a, m, { groundH: W.groundH, top: B.top, out, near: () => { const y = W.you(); return Math.hypot(y.x - m.x, y.z - m.z); },
                                 shy: w.shy ? Math.max(w.shy, 6) : 0, visit: q.spec.visit });
      dens.push({ a, w, m, den: w.den });
    });
  }
  let tunnels = null;
  if (tun.P.length) {
    tunnels = new THREE.Mesh(burrowGeometry(tun), soily(litMaterial()));
    tunnels.material.side = THREE.DoubleSide;
    tunnels.name = "burrows"; tunnels.userData.noMerge = true;
    W.scene.add(tunnels);
  }
  setPits(pits);
  // ---- anthills: the mounds and the ants' ground ----
  const mounds = ants ? ants.ground(S.at) : [];
  for (const m of mounds) markGroundProp(m);
  // ---- nests: all in the trees one mesh; each on the ground its own (its foot at the ground, the grass kept out) ----
  const nestMat = snowyLit(); nestMat.side = THREE.DoubleSide;
  let treeMesh = null;
  if (treeNests.length) { treeMesh = nestMesh(treeNests, nestMat); treeMesh.name = "nests"; treeMesh.userData.noMerge = true; W.scene.add(treeMesh); }
  for (const n of groundNests) {
    // (its foot: the lowest of the drawn ground under its rim, a little in -- never a gap under it on a slope)
    let y = S.at(n.x, n.z);
    for (let k = 0; k < 8; k++) { const a = k / 8 * Math.PI * 2; y = Math.min(y, S.at(n.x + Math.cos(a) * n.spec.r * .8, n.z + Math.sin(a) * n.spec.r * .8)); }
    n.at = [n.x, y - .01, n.z];
    const m = nestMesh([n], nestMat, n.at);
    m.position.set(...n.at); m.updateMatrix(); m.matrixAutoUpdate = false; m.updateMatrixWorld(true);
    m.name = "nest"; m.userData.noMerge = true;
    W.scene.add(m); markGroundProp(m); n.mesh = m;
  }
  // ---- the birds at their nests: figures of the herd that stay put ----
  for (const b of W.herd ? birds : []) {
    const a = W.herd.add(b.def), n = b.n, { cup } = nestBlocks(n.spec, n.seed);
    a.name = b.def.name; a.nest = true; a.ampT = 0;
    const yaw = r() * Math.PI * 2;
    if (b.by) {   // stood beside it, turned to it
      const s = n.spec.r + .25, x = n.at[0] + Math.cos(yaw) * s, z = n.at[2] + Math.sin(yaw) * s;
      a.position.set(x, W.groundH(x, z), z); a.rotY = Math.atan2(-(n.at[2] - z), n.at[0] - x);
    } else if (W.PERCHERS[b.def.name]) seat(a, b.def, W.PERCHERS[b.def.name], n.at[0], n.at[1] + cup + .03, n.at[2], yaw);   // (a percher: sat in it, as on a bough -- perchers.js)
    else { a.position.set(n.at[0] + Math.cos(yaw) * n.spec.r * .2, n.at[1] + cup + .01, n.at[2] + Math.sin(yaw) * n.spec.r * .2); a.rotY = yaw; }
    b.a = a;
  }
  const ms = performance.now() - t0;
  console.info(`nature: ${burrows.length} burrows (${pits.length} mouths, ${dens.length} dens), ${mounds.length} anthills (${ants?.count ?? 0} ants), ` +
              `${treeNests.length + groundNests.length} nests (${birds.length} birds)${skipped.length ? `, none for ${skipped.map((q) => q.join(": ")).join(", ")}` : ""} -- ${S.tris} ground triangles sampled, ${ms.toFixed(0)}ms (${(tSample - t0).toFixed(0)} choosing and sampling)`);
  return { skipped, burrows, dens, tunnels, anthills: mounds, ants, nests: [...treeNests, ...groundNests], birds, pits,
           update(t, { out = 1 } = {}) { ants?.update(t, { out }); } };
}

// a PERCHER sat on a nest's rim as it sits on a bough (perchers.js: the same foot and pitch -- its vent on the perch)
function seat(a, def, spec, x, y, z, h) {
  const legs = !!a.parts?.flight, byId = new Map((def?.parts ?? []).map((p) => [p.id, p])), fb = byId.get("footL");
  const fp = Array.isArray(def?.sculpt?.shape) ? def.sculpt.shape.find((q) => q.id === "foot" && q.type === "ell" && q.c && q.r) : null;
  let stand = null;
  if (fb && fb.perchPitch !== undefined) { stand = [0, 0]; for (let q = fb; q; q = q.parent ? byId.get(q.parent) : null) { stand[0] += q.pos?.[0] ?? 0; stand[1] += q.pos?.[1] ?? 0; } }
  const foot = legs ? [0, 0] : stand ?? (fp ? [fp.c[0], fp.c[1] - fp.r[1]] : spec.foot), th = legs ? 0 : (stand ? fb.perchPitch : spec.pitch) * Math.PI / 180;
  const cx = foot[0] * Math.cos(th) - foot[1] * Math.sin(th), cy = foot[0] * Math.sin(th) + foot[1] * Math.cos(th);
  a.position.set(x - cx * Math.cos(h), y - cy, z + cx * Math.sin(h));
  if (spec.fold) a.perchFold = { fold: spec.fold, squeeze: spec.squeeze };
  a.perch = 1; a.legs = 1; a.pitch = th; a.flyT = 0; a.look = 0; a.perchR = .04; a.rotY = h;
}

// ---- THE ASSET VIEWER'S SPECIMEN (assets.html, kind "nature"): one of each, as the world builds it, on a patch of its
// own ground -- a burrow in a bank (the patch cut by the same oval test the world's ground uses: grass.js PITS), an
// anthill with its ants about it, a nest (in a tree's kind on a fork of two boughs). -> { object, label, stats, tick(t) }
export function natureSpecimen(path, def, { seed = 1 } = {}) {
  const g = new THREE.Group(), leaf = path.split("/").pop();
  const lit = () => { const m = litMaterial(); m.side = THREE.DoubleSide; return m; };
  const patch = (hAt, W, cut) => {   // a square of ground W across, its height hAt, cut where the pits are
    const n = Math.ceil(W / .08), P = [], C = [], I = [], c = new THREE.Color("#5f7a3a"), c2 = new THREE.Color("#6d8442");
    for (let j = 0; j <= n; j++) for (let i = 0; i <= n; i++) {
      const x = -W / 2 + W * i / n, z = -W / 2 + W * j / n, k = .5 + .5 * Math.sin(x * 7.1) * Math.sin(z * 6.3), q = c.clone().lerp(c2, k);
      P.push(x, hAt(x, z), z); C.push(q.r, q.g, q.b);
    }
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { const a = j * (n + 1) + i, b = a + 1, d = a + n + 1, e = d + 1; I.push(a, d, b, b, d, e); }
    const geo = burrowGeometry({ P, C, I }), m = lit();
    if (cut) {
      m.alphaTest = .5; m.opacityNode = float(1).sub(groundHole({ wp: positionWorld, holes: GROUND_HOLES.tex, box: GROUND_HOLES.box, rects: GROUND_HOLES.rects }));
      const lit0 = m.colorNode.mul(vertexColor());   // (the bare earth round the mouths and under the heaps, as the world's ground lays it)
      m.vertexColors = false;
      m.colorNode = earthOver({ rgb: lit0, lit: lit0, vcol: vertexColor(), k: groundEarth({ wp: positionWorld, rects: GROUND_HOLES.rects }), snow: float(0), wp: positionWorld });
    }
    return new THREE.Mesh(geo, m);
  };
  if (path.includes("/burrows/")) {
    const hAt = (x, z) => .22 * x + .04 * Math.sin(z * .9) + .03 * Math.sin(x * 1.7 + z * .4);
    const r = rng(seed * 31 + 7), mouths = [{ x: 0, z: 0, yaw: 0, scale: 1 }];
    for (let i = 1; i < (def.mouths ?? 1); i++) { const a = Math.PI / 2 + (i - 1) * Math.PI + (r() - .5) * .6, d = (def.spread ?? 3) * (.6 + .3 * r()); mouths.push({ x: Math.cos(a) * d * .4, z: Math.sin(a) * d, yaw: (r() - .5) * .5, scale: .85 + .25 * r() }); }
    const B = burrowMesh(def, { x: 0, z: 0, yaw: 0, mouths }, hAt, { seed });
    setPits(B.pits);
    const W = Math.max(3, (def.r ?? .15) * ((def.heap?.len ?? 6) * 2 + 8) + (def.mouths > 1 ? (def.spread ?? 3) * 2 : 0));
    g.add(patch(hAt, W, true), new THREE.Mesh(burrowGeometry(B.tunnel), soily(lit())), new THREE.Mesh(burrowGeometry(B.heap), soily(lit())));
    return { object: g, label: `${leaf} · ${(def.species ?? []).join(", ")}`, stats: `${B.mouths.length} mouth${B.mouths.length > 1 ? "s" : ""} · ${((def.r ?? .15) * 200).toFixed(0)} cm across · ${(B.tunnel.I.length + B.heap.I.length) / 3} triangles` };
  }
  if (leaf === "anthill") {
    const hAt = (x, z) => .03 * Math.sin(x * .8) + .02 * Math.sin(z * 1.1);
    const ants = createAnts(g, [{ x: 0, z: 0, R: def.R?.[1] ?? 1, H: def.H?.[1] ?? .6 }], { seed, spec: def });
    ants.ground(hAt);   // (its needles as the world draws them: ants.js anthillMaterial)
    g.add(patch(hAt, Math.min(24, 2 * (ants.hills[0].half ?? 6)), false));
    ants.update(0, { out: 1 });
    const t0 = performance.now();
    ants.mesh.onBeforeRender = () => ants.update((performance.now() - t0) / 1000, { out: 1 });
    return { object: g, label: "anthill · wood ants", stats: `${ants.count} ants · ${ants.hills[0].trails.length} trails · ${(ants.hills[0].R * 2).toFixed(1)} m across` };
  }
  // a nest: as it sits -- on a fork of two boughs (a tree's), on the ground (by the water)
  const onTree = def.where === "crown" || def.where === "tall";
  const { cup, top } = nestBlocks(def, seed), y0 = onTree ? .9 : 0;
  const nest = nestMesh([{ spec: def, at: [0, y0, 0], seed }], lit());
  g.add(nest);
  if (onTree) g.add(blockBoughs(def.r ?? .3, y0, lit()));
  else g.add(patch(() => -.005, Math.max(2, (def.r ?? .2) * 5), false));
  return { object: g, label: `${leaf} nest · ${(def.species ?? []).join(", ")}`, stats: `${((def.r ?? .3) * 200).toFixed(0)} cm across · rim ${(top * 100).toFixed(0)} cm · cup ${(cup * 100).toFixed(0)} cm` };
}
// two boughs forking under a nest (the viewer's)
function blockBoughs(R, y0, material) {
  const col = [.33, .27, .2], B = [];
  B.push({ at: [0, y0 / 2, 0], size: [y0 + .1, .16, .16], tilt: Math.PI / 2, shape: "log", colour: col });
  for (const s of [-1, 1]) B.push({ at: [s * R * .7, y0 + .05, 0], size: [R * 2.4, .09, .09], yaw: 0, tilt: s * .7, shape: "log", colour: col });
  return blockMesh(B, "boughs", material);
}
