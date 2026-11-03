// THE HARBOUR (2026-11-03): the game's side of a world with open water (sea.js) -- the port that port.js lays out on the
// stretch of shore sea.js chooses, built and joined to the roads; the culture's ships (assets/world/ships.json) moored at
// its berths and under way on the lanes, now and then one coming in to a free berth and leaving again; and the FREIGHT
// (freight.js addDock: the same goods, states and dock hands as the river's barge) carried from a moored ship's hold up
// its gangplank and across the quay to the port's warehouses. Nothing here runs on a river-only world (SEA null).
//
//   planHarbour(o)            BEFORE the roads and the ground: the site, the layout, its pads as flat zones, its street
//                             (-> { site, port, route: a road for planRoads' `extra`, inside(x, z, m), ... } or null)
//   buildHarbour(H, o)        with the town's buildings: each piece built, its walls and floors walkable
//   createHarbourLife(H, o)   after the freight: the ships, their berths and lanes, the dock hands
// docs/world.md "The harbour in the game".
import * as THREE from "three";
import { layoutPort, portCulture } from "./port.js";
import { archBuilding, buildBuilding, itemGroup, itemGeometry, itemMaterial } from "./architecture.js";
import { ASSETS } from "./catalogue.js";
import { laneFrom } from "./paths.js";
import { createWakes } from "./wakes.js";
import { setDryHulls } from "./seawater.js";

// moored / under way: how many at the start; speed m/s; stay: s a ship lies at its berth at least; away: s a ship is
// gone over the horizon before it comes back; every: s between ships coming in; hands: the dock hands; road: the street's
// width; fade: m the levelled pads ease back into the land over (ground.js indexes zones 20 m round: keep under it);
// green: m round the pads the beach's bare sand eases off into grass
export const PORT_LIFE = { moored: [2, 4], under: [1, 3], speed: { sail: 2.4, oar: 1.7 }, stay: [60, 120], away: [25, 60], every: [45, 100],
                           hands: 3, road: 3, fade: 14, green: 10, slots: 8, apron: { sink: .07, edge: 2 },
                           berth: { depth: 2.4, reach: 9, fade: 6 } };   // (the bed dredged before a quay: m under the water, m out, m back up)

const rnd = (seed) => { let a = (seed >>> 0) || 1; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
const norm = ([x, z]) => { const l = Math.hypot(x, z) || 1; return [x / l, z / l]; };
// a piece's local (x, z) in the world, turned by the engine's yaw (rotation.y: local +x -> (cos, -sin), +z -> (sin, cos))
const toWorld = (o, yaw, x, z) => [o[0] + x * Math.cos(yaw) + z * Math.sin(yaw), o[1] - x * Math.sin(yaw) + z * Math.cos(yaw)];
const angDiff = (a, b) => ((b - a + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
const smooth = (t) => { t = Math.min(1, Math.max(0, t)); return t * t * (3 - 2 * t); };

// ---- PLAN: before the roads (the street is one) and the ground (the pads are flat zones) -----------------------------
// o: { SEA, areas (MAP.areas: [0] the town), period, dress, seed, flatZones (ground.js, by reference), naturalH,
//      routes (the town's planned streets [{ pts }]: harbourSite keeps near them, the street ends on one), blocked(x, z),
//      surface (MAP.surface: its `bare` eased off over the port -- a lawn behind the quay, not the beach's sand) }
export function planHarbour({ SEA, areas = [], period, dress, seed = 1, flatZones, naturalH = null, routes = [], blocked = () => false, surface = null }) {
  if (!SEA) return null;
  const table = ASSETS.get("world/ports");
  if (!table) return null;
  const C = portCulture(table, period, dress);
  const a = areas[0], town = a ? [(a.x0 + a.x1) / 2, (a.z0 + a.z1) / 2] : [0, 0];
  const roads = routes.map((r) => ({ pts: r.pts }));
  // (the culture's own length of shore if there is one, else sea.js's 100 m)
  const site = SEA.harbourSite(town, { length: C.length ?? 140, roads }) ?? SEA.harbourSite(town, { roads });
  if (!site) { console.warn("harbour: no site for a port", SEA.why); return null; }
  // THE STREET'S END: the nearest point of the town's streets that a straight way reaches from `from` clear of buildings
  // and water (routeGraph ties a route's end to the line it lies on: the port joins the network there)
  const cands = [];
  for (const r of routes) for (let i = 0; i + 1 < r.pts.length; i++) {
    const [ax, az] = r.pts[i], [bx, bz] = r.pts[i + 1], n = Math.max(1, Math.ceil(Math.hypot(bx - ax, bz - az) / 3));
    for (let k = 0; k <= n; k++) cands.push([ax + (bx - ax) * k / n, az + (bz - az) * k / n]);
  }
  const clear = (p, q) => { const n = Math.max(1, Math.ceil(Math.hypot(q[0] - p[0], q[1] - p[1]) / 2));
    for (let k = 1; k < n; k++) { const x = p[0] + (q[0] - p[0]) * k / n, z = p[1] + (q[1] - p[1]) * k / n; if (blocked(x, z) || SEA.isOpenWater(x, z)) return false; } return true; };
  const junction = (from) => {
    const byD = cands.map((c) => [Math.hypot(c[0] - from[0], c[1] - from[1]), c]).sort((p, q) => p[0] - q[0]);
    for (let k = 0; k < Math.min(byD.length, 300); k++) if (byD[k][0] < 260 && clear(from, byD[k][1])) return byD[k][1];
    return null;
  };
  const inland = [site.mid[0] - site.normal[0] * 40, site.mid[1] - site.normal[1] * 40];
  const gate0 = junction(inland);
  const port = layoutPort({ points: site.points, normals: site.normals, level: site.level, period, dress, seed, table, gate: gate0, groundY: naturalH });
  // the street: from just behind the quay (the quay's own paving carries it to the face) up through the row to the junction
  const [p0, p1] = port.path, dir = norm([p1[0] - p0[0], p1[1] - p0[1]]), B = C.quay?.B ?? 10;
  const start = [p0[0] + dir[0] * (B / 2 + .6), p0[1] + dir[1] * (B / 2 + .6)];
  const gate = junction(p1) ?? port.path[2];
  const route = { w: PORT_LIFE.road, pts: [start, p1, gate] };
  // THE TERRACE: the row behind the apron stands at the quay's own height, one level with it -- ground.js settles a
  // point to its NEAREST zone's y, so plots at the land's height beside a quay pad 6 m lower met in a sheer bank. The
  // land higher behind comes down to it over `fade` (port.js's pads ask max(quayTop, ground): taken down here)
  const qt = port.quayTop;
  for (const pd of port.pads) if (pd.y > qt + .01) {
    for (const p of port.placements) if (Math.abs(p.x - pd.x) < .01 && Math.abs(p.z - pd.z) < .01 && Math.abs(p.y - pd.y) < .01) p.y = qt;
    pd.y = qt;
  }
  // THE CRANES off the carry line: port.js stands each at its berth's middle, just where a moored hull's plank comes
  // down (amidships) -- moved along the quay by half its width and 3 m, to the side with more quay (a jib crane's jib
  // turned to keep over the same hold point)
  const R0 = rnd(seed * 7 + 3);
  for (const p of port.placements.filter((q) => q.role === "crane")) {
    const ux = Math.cos(p.yaw), uz = -Math.sin(p.yaw), s0 = p.w / 2 + 3;
    const room = (s) => port.placements.filter((q) => q !== p && ["quay"].includes(q.role)).some((q) => {   // (still on a quay run there)
      const dx = p.x + ux * s - q.x, dz = p.z + uz * s - q.z, lx = dx * Math.cos(q.yaw) - dz * Math.sin(q.yaw);
      return Math.abs(lx) < q.w / 2 - 2 && Math.abs(dx * Math.sin(q.yaw) + dz * Math.cos(q.yaw)) < q.d + 4; });
    const clear = (s) => !port.placements.some((q) => q !== p && ["pier", "crane", "sheds", "slip", "light"].includes(q.role) && Math.hypot(p.x + ux * s - q.x, p.z + uz * s - q.z) < (q.w + p.w) / 2 + 1);
    const s = [R0() < .5 ? s0 : -s0, R0() < .5 ? -s0 : s0].find((v) => room(v) && clear(v));
    if (s === undefined) continue;
    p.x += ux * s; p.z += uz * s;
    if (p.params?.jib !== undefined) { const r = p.params.reach ?? 6, a = p.params.jib * Math.PI / 180, lx = r * Math.sin(a) - s, lz = r * Math.cos(a);
      p.params = { ...p.params, jib: Math.round(Math.max(-70, Math.min(70, Math.atan2(lx, lz) * 180 / Math.PI))) }; }
  }
  // THE PADS as flat zones (ground.js: axis-aligned, with their own `y`): squares along each turned rectangle's long axis
  // THE APRON (pass 3): a quay's pad is its paving (a 12 cm slab, its top at quayTop), and the ground was settled to that
  // same height -- coplanar, it z-fought through the flags in patches, the lawn and its stalks with it; and the zones'
  // squares, axis-aligned, left a turned quay's corners to the 14 m ease, the land rising through the paving there. Now
  // the ground under a quay's pad lies `sink` under the paving's top (inside the slab, so its back edge is a kerb, no
  // gap under it), each square grown to cover its turned stretch and `edge` m round it (no slope met inside the paving),
  // and the quay's squares first (ground.js takes the first nearest zone: where a plot's pad overlaps, the quay wins)
  const zones = [], qc = port.placements.filter((p) => p.role === "quay").map((p) => toWorld([p.x, p.z], p.yaw, 0, -p.d / 2));
  const isQuay = (p) => qc.some((c) => Math.abs(c[0] - p.x) < .05 && Math.abs(c[1] - p.z) < .05);
  for (const p of port.pads) {
    if (!(p.w > 0 && p.d > 0)) continue;
    const quay = isQuay(p), s = Math.max(2, Math.min(p.w, p.d)), L = Math.max(s, p.w, p.d), ax = p.w >= p.d ? [Math.cos(p.yaw), -Math.sin(p.yaw)] : [Math.sin(p.yaw), Math.cos(p.yaw)];
    const n = Math.max(1, Math.ceil((L - s) / (s * .4))) + 1, h = quay ? s * .5 * (Math.abs(ax[0]) + Math.abs(ax[1])) : s * .5;
    // (a quay's square grown `edge` m landward only -- its centre moved inland half that, its halves grown by as much: the
    //  seaward side stays where it was, the berth's bed is not lifted)
    const E = PORT_LIFE.apron.edge, land = quay ? [-Math.sin(p.yaw), -Math.cos(p.yaw)] : [0, 0];   // (the quay's local -z: inland, toWorld)
    for (let k = 0; k < n; k++) {
      const t = n > 1 ? -(L - s) / 2 + (L - s) * k / (n - 1) : 0;
      zones.push({ x: p.x + ax[0] * t + land[0] * E / 2, z: p.z + ax[1] * t + land[1] * E / 2, hx: h + Math.abs(land[0]) * E / 2, hz: h + Math.abs(land[1]) * E / 2,
                   y: quay ? p.y - PORT_LIFE.apron.sink : p.y, fade: PORT_LIFE.fade, harbour: true, quay,
                   // (the quay's own pad, turned: ground.js levels the ground under it even where the wet mask bleeds in)
                   ...(quay ? { pad: { x: p.x, z: p.z, c: Math.cos(p.yaw), s: Math.sin(p.yaw), hw: p.w / 2, hd: p.d / 2 } } : {}) });
    }
  }
  zones.sort((p, q) => q.quay - p.quay);
  // THE BERTHS DREDGED: before each quay the bed is taken down to `berth.depth` under the water, `reach` m out (ground.js
  // `dig`) -- a rocky shore's bed rose at the face, a strip of beach stood out of the water under the wall, and the
  // ships moored up to 3 m off it (gapFor: with the bed dredged, at the wall)
  const BR = PORT_LIFE.berth;
  for (const p of port.placements.filter((q) => q.role === "quay")) {
    const [cx, cz] = toWorld([p.x, p.z], p.yaw, 0, BR.reach / 2), r = Math.hypot(p.w / 2, BR.reach / 2);
    zones.push({ x: cx, z: cz, hx: r, hz: r, y: site.level - BR.depth, fade: BR.fade, harbour: true,
                 dig: { x: p.x, z: p.z, c: Math.cos(p.yaw), s: Math.sin(p.yaw), hw: p.w / 2, D: BR.reach } });
  }
  flatZones?.push(...zones);
  // the ground's colour over the port: grass and its lawn behind the quay and round the row, the beach's sand eased off
  // (sea.js paints 26 m back from the water bare sand)
  if (surface?.bare) {
    const { n, res, x0, z0, bare } = surface, F = PORT_LIFE.green;
    const padD = (x, z) => { let m = Infinity; for (const p of port.pads) {
      const dx = x - p.x, dz = z - p.z, lx = dx * Math.cos(p.yaw) - dz * Math.sin(p.yaw), lz = dx * Math.sin(p.yaw) + dz * Math.cos(p.yaw);
      m = Math.min(m, Math.hypot(Math.max(0, Math.abs(lx) - p.w / 2), Math.max(0, Math.abs(lz) - p.d / 2))); } return m; };
    const xs = port.pads.flatMap((p) => [p.x - p.w - p.d, p.x + p.w + p.d]), zs = port.pads.flatMap((p) => [p.z - p.w - p.d, p.z + p.w + p.d]);
    const i0 = Math.max(0, Math.floor((Math.min(...xs) - F - x0) / res)), i1 = Math.min(n - 1, Math.ceil((Math.max(...xs) + F - x0) / res));
    const j0 = Math.max(0, Math.floor((Math.min(...zs) - F - z0) / res)), j1 = Math.min(n - 1, Math.ceil((Math.max(...zs) + F - z0) / res));
    for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) {
      const x = x0 + i * res, z = z0 + j * res;
      if (SEA.isOpenWater(x, z)) continue;
      const k = j * n + i; bare[k] *= smooth(padD(x, z) / F);
    }
  }
  // what keeps the trees, bushes and the wild out: the pads, and every piece's own box (the piers and the mole too)
  const boxes = [...port.pads.map((p) => ({ x: p.x, z: p.z, yaw: p.yaw, w: p.w, d: p.d })),
                 ...port.placements.map((p) => { const c = p.role === "quay" ? toWorld([p.x, p.z], p.yaw, 0, -p.d / 2) : p.role === "pier" || p.role === "mole" ? toWorld([p.x, p.z], p.yaw, 0, p.d / 2) : [p.x, p.z];
                   return { x: c[0], z: c[1], yaw: p.yaw, w: p.w, d: p.d }; })];
  const inside = (x, z, m = 0) => boxes.some((b) => {
    const dx = x - b.x, dz = z - b.z, lx = dx * Math.cos(b.yaw) - dz * Math.sin(b.yaw), lz = dx * Math.sin(b.yaw) + dz * Math.cos(b.yaw);
    return Math.abs(lx) < b.w / 2 + m && Math.abs(lz) < b.d / 2 + m;
  });
  console.log(`harbour: a ${port.culture} port on ${site.length.toFixed(0)} m of ${site.type} shore, ${site.dist.toFixed(0)} m from the town -- ` +
              `${port.placements.length} pieces, ${port.berths.length} berths${port.dropped.length ? `, no room for ${port.dropped.join(", ")}` : ""}`);
  return { site, port, culture: C, town, route, zones, inside, pieces: [] };
}

// ---- BUILD: each piece as a building of the archgen system (its params turned by the placement's yaw: the mesh, its
// floors and walls come out turned, so it stands by translation alone -- siteGroups, the sun's shadows, the merge)
// o: { scene, markGroundProp, siteGroups, colliderSites, heightFields } (index.html's lists, by reference)
export function buildHarbour(H, { scene, markGroundProp = null, siteGroups = null, colliderSites = null, heightFields = null }) {
  const t0 = performance.now();
  for (const p of H.port.placements) {
    let def;
    try { def = archBuilding(p.def, { name: p.role, params: { ...p.params, yaw: +(p.yaw * 180 / Math.PI).toFixed(3) }, finish: ASSETS.get(p.finish) ?? null, origin: true }); }
    catch (e) { console.warn(`harbour: ${p.def} would not build: ${e.message}`); continue; }
    const b = buildBuilding(def);
    b.position.set(p.x, p.y, p.z);
    markGroundProp?.(b); siteGroups?.push(b);
    scene.add(b);
    const r = Math.max(...(def.footprint ?? [p.w, p.d])) / 2 + 2, y = p.y;
    // (its walls and floors in its own frame, read at the walker's height less the piece's: they were built at y 0)
    // (a piece keeps its OWN origin -- a quay's front edge, a crane's foot -- not its footprint's middle, so the box the
    //  walker is tested in is how far it reaches from that origin each way, `extent`: half its footprint round the
    //  origin left a quay's back half, a warehouse's far rooms and the light's tower out of it, walked through)
    const ex = def.extent ?? [r - 2, r - 2];
    if (def.wallField) colliderSites?.push({ x: p.x, z: p.z, rx: ex[0] + 2, rz: ex[1] + 2, cols: [], solids: [], field: (lx, lz, lo, hi) => def.wallField(lx, lz, lo - y, hi - y) });
    if (def.floorY) heightFields?.push({ f: (lx, lz) => { const v = def.floorY(lx, lz); return Array.isArray(v) ? v.map((h) => h + y) : v; }, x: p.x, z: p.z, dig: null, deep: 0 });
    H.pieces.push({ ...p, def, group: b });
  }
  console.log(`harbour: ${H.pieces.length} pieces built in ${(performance.now() - t0).toFixed(0)} ms`);
  return H;
}

// ---- LIFE: the ships and the dock -----------------------------------------------------------------------------------
// o: { scene, SEA, freight ({ addDock, loadShip, placeItem }: freight.js), period, dress, seed, standY(x, z) (the floor a
//      figure stands on there), surfaceAt(x, z), camera, movers (index.html's moving floors, by reference: a ship afloat and
//      its plank down are walked into and stood on as a cart's bed is) }
export function createHarbourLife(H, { scene, SEA, freight, period, dress, seed = 1, standY, surfaceAt, camera, movers = null }) {
  const T = ASSETS.get("world/ships");
  if (!T?.ships) return null;
  const R = rnd(seed * 131 + 7), between = ([a, b]) => a + R() * (b - a), betweenN = ([a, b]) => a + Math.floor(R() * (b - a + 1));
  const styles = typeof dress === "string" ? [dress] : Object.keys(dress ?? {});
  const CK = T.cultures?.[period] ? period : styles.find((k) => k && T.cultures?.[k]) ?? "default", C = T.cultures?.[CK] ?? {};
  const pickW = (list) => { const tot = list.reduce((s, [, w]) => s + w, 0); let x = R() * tot; for (const [id, w] of list) if ((x -= w) < 0) return id; return list[0]?.[0]; };
  const P = H.port, level = P.waterY, quayTop = P.quayTop, Q = { style: "stone", ...(H.culture.quay ?? {}) };
  const reach = Q.reach ?? (Q.style === "steps" ? 4.6 : .3);
  const lane = SEA.lanes?.[0] ?? null, lanePts = lane?.pts ?? [];

  // THE BERTHS: the hull's line a..b (the side against the quay), `out` the side it lies on; a pier's ships lie bow to the land
  const berths = P.berths.map((b, i) => {
    const u = norm([b.b[0] - b.a[0], b.b[1] - b.a[1]]), mid = [(b.a[0] + b.b[0]) / 2, (b.a[1] + b.b[1]) / 2];
    const dir = b.kind === "pier" ? [-u[0], -u[1]] : (R() < .5 ? u : [-u[0], -u[1]]);
    // the apron's way to its plank, from the land: behind a quay berth on the apron; a pier's root, then along the pier
    const back = (d) => [mid[0] - b.out[0] * d, mid[1] - b.out[1] * d];
    let way;
    if (b.kind === "pier") { const PW = H.culture.piers?.W ?? 3.4, axis = back(PW / 2 + .3), root = [b.a[0] - u[0] * 4 - b.out[0] * (PW / 2 + .3), b.a[1] - u[1] * 4 - b.out[1] * (PW / 2 + .3)];
      way = [[root[0] - u[0] * 4, root[1] - u[1] * 4], root, axis]; }
    else way = [back(reach + (Q.T ?? 1.6) + 4.5)];
    return { ...b, i, u, mid, dir, way, ship: null };
  });
  const yawOfDir = (d) => Math.atan2(-d[1], d[0]);

  // THE SHIPS: each built twice from its item (assets/items/ships), as it lies moored (sails furled, oars shipped) and as it
  // goes (sailing, rowing or both: its drive), under one root at the waterline amidships that the pose turns and rocks
  const ships = [];
  const fits = (id, b) => { const S = T.ships[id]; return S && (S.length?.[0] ?? 8) <= b.length + .5 && (S.draught ?? 1) <= (b.depth ?? 3) + .3; };
  function makeShip(id, L, k) {
    const S = T.ships[id], takes = new Set(S.params ?? []);
    const stateP = (st) => { const s = T.states?.[st] ?? {}, o = { L }; if (takes.has("set")) o.set = s.set; if (takes.has("oars")) o.oars = s.oars; return o; };
    const go = /oar|paddle|pole/.test(S.drive) ? (S.drive.startsWith("sail") ? "under way" : "rowing") : "sailing";
    const root = new THREE.Object3D(); root.rotation.order = "YXZ"; root.name = S.name; scene.add(root);
    const sd = 11 + k * 17, variants = {};
    for (const st of ["moored", go]) { const g = itemGroup(S.item, { seed: sd, params: stateP(st) }); g.userData.moves = true; root.add(g); variants[st] = g; }
    const built = variants.moored.userData.built, mk = (role) => built.markers.filter((m) => m.role === role);
    const lo = built.bounds.lo, hi = built.bounds.hi, centre = S.frame === "centre";
    const wlM = mk("waterline")[0], xMid = centre ? 0 : wlM?.at[0] ?? (lo[0] + hi[0]) / 2, wl = centre ? 0 : wlM?.at[1] ?? (hi[1] - lo[1]) * .3;
    for (const g of Object.values(variants)) g.position.set(-xMid, -wl, 0);
    const planks = mk("gangplank").map((m) => ({ side: m.data.side, at: [m.at[0] - xMid, m.at[1] - wl, m.at[2]], deck: (m.data.deck ?? m.at[1]) - wl }));
    // (the hull's length and beam: the bounds' length; the beam from the planks' rail, the bounds take the oars and the yards)
    const Lh = hi[0] - lo[0], Bh = planks.length ? 2 * Math.max(...planks.map((q) => Math.abs(q.at[2]))) : hi[2] - lo[2] || S.beam || 3;
    // (the floor the hands walk and the cargo stands on: the deck, or an open hull's bottom boards -- under the waterline
    //  too: the water is cut out inside the hull (`dry`, an ellipse inside its waterline plan: seawater.js setDryHulls))
    // AN OPEN HULL (its bottom boards under the waterline: a gaulos's): the sea bed lies higher than the boards at many a
    // berth (the hull's keel is in it), so the hold gets a floor of its own just OVER the waterline (OPEN_FLOOR: above
    // the moored bob and pitch at its ends; under it, .1 m down, the water outside the `dry` ellipse lay a band of bilge
    // over the floor's rim all round) planked in the deck's own material -- and its planking is drawn from both sides
    // (single-sided, the far side's inside showed the sea beyond it)
    const OPEN_FLOOR = .08;
    const dry = [Math.min(L ?? Lh, Lh) * .42, Bh * .36], deck0 = planks[0]?.deck ?? (hi[1] - wl) * .6, open = deck0 < -.1;
    const deck = open ? OPEN_FLOOR : deck0;
    if (open) {
      // (its outline: the planking's own section at the floor's height -- each hull triangle crossing it, the widest
      //  |z| in 0.5 m bins along the length -- so nothing of the bed or the water shows between the floor and the hull)
      const gs = built.groups, gd = gs.find((g) => g.roles.has("deck")) ?? gs[0], gp = gs.find((g) => g.roles.has("planks")), yy = deck + wl, bw = .5, bins = new Map();
      if (gp) for (let t = 0; t < gp.idx.length; t += 3) {
        const v = [0, 1, 2].map((k) => gp.idx[t + k] * 3).map((o) => [gp.pos[o], gp.pos[o + 1], gp.pos[o + 2]]);
        for (let e = 0; e < 3; e++) { const a = v[e], b = v[(e + 1) % 3]; if ((a[1] - yy) * (b[1] - yy) > 0 || a[1] === b[1]) continue;
          const f = (yy - a[1]) / (b[1] - a[1]), x = a[0] + (b[0] - a[0]) * f, z = Math.abs(a[2] + (b[2] - a[2]) * f), k = Math.round(x / bw);
          if (z <= Bh / 2 + .1) bins.set(k, Math.max(bins.get(k) ?? 0, z)); }
      }
      const ks = [...bins.keys()].sort((p, q) => p - q), pos = [], nor = [], uv = [], idx = [];
      for (const k of ks) { const x = k * bw - xMid, w = Math.max(0, bins.get(k) - .03);
        for (const z of [-w, w]) { pos.push(x, deck, z); nor.push(0, 1, 0); uv.push(x, z); } }
      for (let i = 0; i + 1 < ks.length; i++) { const a = i * 2, b = a + 2; idx.push(a, a + 1, b + 1, a, b + 1, b); }
      const geo = itemGeometry({ pos: new Float32Array(pos), nor: new Float32Array(nor), uv: new Float32Array(uv), idx: Uint16Array.from(idx) });
      const floor = new THREE.Mesh(geo, itemMaterial(gd.material, false, geo)); floor.name = `${S.name} hold floor`; floor.userData.moves = true; root.add(floor);
      for (const v of Object.values(variants)) v.children.forEach((m, i) => { const g = gs[i];
        if (m.isMesh && g && g.material.side !== "double" && [...g.roles].some((r) => r === "planks" || r === "hull")) m.material = itemMaterial({ ...g.material, side: "double" }, false, m.geometry); });
    }
    const slots = [];
    for (const h of mk("hold")) {
      const hl = h.data.l ?? 1.0, hw = Math.min((h.data.w ?? Bh * .3) * .35, Bh * .25);
      for (const [sx, sz] of [[-1, -1], [-1, 1], [1, -1], [1, 1]]) slots.push([h.at[0] - xMid + sx * (hl / 2 + .45), deck + .02, h.at[2] + sz * hw]);   // (on deck beside the hatch: the hold's floor is under it)
    }
    if (!slots.length) for (const sx of [-1, 1]) for (const sz of [-1, 1]) slots.push([sx * Lh * .12, deck + .02, sz * Bh * .15]);
    slots.length = Math.min(slots.length, PORT_LIFE.slots);
    const plank = itemGroup("items/components/gangplank"); plank.rotation.order = "YXZ"; plank.visible = false; plank.userData.moves = true; scene.add(plank);
    const sw = { position: new THREE.Vector3(0, -100, 0), rotY: 0, hidden: true, size: Math.max(1, Lh * .32) };
    const ship = { id, name: S.name, spec: S, L: Lh, B: Bh, wl, root, variants, go, sail: /sail/.test(S.drive) && go !== "rowing", speed: (/sail/.test(S.drive) ? PORT_LIFE.speed.sail : PORT_LIFE.speed.oar) * (.9 + R() * .25),
                   planks, slots, plank, swimmer: sw, hold: [], state: "gone", berth: null, path: null, s: 0, x: 0, z: 0, yaw: 0, ph: R() * 6.28, t: 0, heel: R() < .5 ? 1 : -1,
                   moored: false, plankSide: null, deck, dry };
    // AS A MOVER (index.html collides, cartFloorsAt): a box round the hull -- its deck (an open hull's floor) to stand on,
    // what is under the deck solid, the gunwale its rim (`side`, from the deck up to the rail) -- carried along when it
    // moves (`carry`, pose); its plank down, a ramp from the rail to the quay (`ramp`: its bed read where you stand on it)
    const rail = Math.max(0, ...planks.map((q) => q.at[1]));
    Object.assign(ship, { body: root, carry: { dx: 0, dz: 0, dyaw: 0 }, halfL: Lh * .46, halfW: Bh / 2, top: deck, side: Math.max(.3, rail - deck),
                          plankMover: { body: new THREE.Object3D(), yaw: 0, carry: { dx: 0, dz: 0, dyaw: 0 }, halfL: 1, halfW: .35, top: 0, side: 0, ramp: true, active: false } });
    ship.plankMover.body.rotation.order = "YZX";
    // the dock's questions (freight.js): where the hold's pieces lie, its plank's ends, the apron's way to them
    const _v = new THREE.Vector3();
    ship.holdWorld = (it) => { const s = slots[it.slot % slots.length]; ship.root.updateMatrixWorld(); _v.set(...s).applyMatrix4(ship.root.matrixWorld); return [_v.x, _v.y, _v.z]; };
    ship.plankTop = () => { const pl = ship.plankSide; ship.root.updateMatrixWorld(); _v.set(...pl.at).applyMatrix4(ship.root.matrixWorld); return [_v.x, _v.y + .03, _v.z]; };
    ship.plankFoot = () => { const b = ship.berth, top = ship.plankTop(), d = .3 + reach + 1.1 + (ship.gap ?? 0), x = top[0] - b.out[0] * d, z = top[2] - b.out[1] * d; return [x, standY(x, z), z]; };
    // (a quay berth's: straight in from the apron behind the plank's foot; a pier's: its root, then along it)
    ship.way = () => { const b = ship.berth;
      if (b.kind !== "pier") { const f = ship.plankFoot(), d = (Q.T ?? 1.6) + 3.4, x = f[0] - b.out[0] * d, z = f[2] - b.out[1] * d; return [[x, standY(x, z), z]]; }
      return b.way.map(([x, z]) => [x, standY(x, z), z]); };
    ships.push(ship);
    return ship;
  }
  const show = (S, st) => { for (const [k, g] of Object.entries(S.variants)) g.visible = st === k; S.root.visible = !!st;
    // (afloat it is a floor and a wall; its plank only while moored)
    if (!movers) return;
    const on = (k, want) => { const i = movers.indexOf(k); if (want && i < 0) movers.push(k); else if (!want && i >= 0) movers.splice(i, 1); };
    on(S, !!st); on(S.plankMover, st === "moored"); };

  // MOORED: at the berth's middle, its side a hand off the quay, rocking a little; the plank down from the rail on the
  // quay's side; the hold filled from the pool (freight.js loadShip)
  // (the plank on the quay's side: starboard is the hull's +z, (sin yaw, cos yaw) in the world)
  const plankFor = (S, yaw, b) => { const sb = Math.sin(yaw) * b.out[0] + Math.cos(yaw) * b.out[1] < 0;
    return S.planks.find((q) => (q.side === "starboard") === sb) ?? S.planks[0] ?? { at: [0, S.deck, S.B * (sb ? .5 : -.5)] }; };
  // (along the berth, as far as it has room: the plank's foot kept clear of a crane standing on the quay behind it --
  //  the hands' way up it goes straight in from the apron)
  const cranes = H.pieces.filter((p) => p.role === "crane");
  const shiftFor = (S, b, ax) => {
    const room = Math.max(0, (b.length - S.L) / 2), near = cranes.map((c) => ({ c, along: (c.x - b.mid[0]) * b.dir[0] + (c.z - b.mid[1]) * b.dir[1], half: c.w / 2 + 1.2 }))
      .filter(({ c }) => Math.abs((c.x - b.mid[0]) * b.out[0] + (c.z - b.mid[1]) * b.out[1]) < 12);
    const ok = (s) => Math.abs(s) <= room + 1e-6 && near.every(({ along, half }) => Math.abs(s + ax - along) >= half);
    return [0, ...near.flatMap(({ along, half }) => [along - ax - half, along - ax + half])].filter(ok).sort((p, q) => Math.abs(p) - Math.abs(q))[0] ?? 0;
  };
  // (and off the berth line by `gap` as far as it takes -- up to 3 m -- for the bed along the hull's quay side to lie
  //  under its floor: port.js takes a berth's depth on trust, and a rocky shore's bed often rises at the face, up into
  //  an open hull)
  const gaps = new Map();
  const gapFor = (S, b, sh) => {
    const k = `${S.id}|${b.id}`; if (gaps.has(k)) return gaps.get(k);
    let g = 3;
    for (let e = 0; e <= 3; e += .5) {
      const c = .3 + e + S.B * .05, ok = [-.36, -.27, -.18, -.09, 0, .09, .18, .27, .36].every((u) => { const x = b.mid[0] + b.out[0] * c + b.dir[0] * (sh + u * S.L), z = b.mid[1] + b.out[1] * c + b.dir[1] * (sh + u * S.L); return standY(x, z) < level + S.deck - .15; });
      if (ok) { g = e; break; }
    }
    gaps.set(k, g); return g;
  };
  const mooredPose = (S, b) => {
    const yaw = yawOfDir(b.dir), sh = shiftFor(S, b, plankFor(S, yaw, b).at[0]), o = S.B / 2 + .3 + gapFor(S, b, sh);
    return { x: b.mid[0] + b.out[0] * o + b.dir[0] * sh, z: b.mid[1] + b.out[1] * o + b.dir[1] * sh, yaw };
  };
  function moor(S, b) {
    S.berth = b; b.ship = S; b.coming = null;
    const p = mooredPose(S, b); S.x = p.x; S.z = p.z; S.yaw = p.yaw; S.gap = gapFor(S, b, shiftFor(S, b, plankFor(S, p.yaw, b).at[0]));
    S.state = "moored"; S.moored = true; S.t = 0; S.stay = between(PORT_LIFE.stay); show(S, "moored");
    S.plankSide = plankFor(S, S.yaw, b);
    S.plank.visible = true;
    S.swimmer.hidden = true;
    pose(S, 0);
    if (stores.length) freight?.loadShip?.(S, S.slots.length);
  }
  // UNDER WAY: along a path (laneFrom, open): its heading eased in, slower near a berth, heeling under sail, pitching
  function sail(S, pts, end, o = {}) {
    S.path = laneFrom(pts, true); S.s = 0; S.end = end; S.astern = o.astern ?? 0; S.dock = o.dock ?? null;
    S.state = "going"; S.moored = false; show(S, S.go); S.plank.visible = false; S.swimmer.hidden = false;
    if (o.yaw === undefined) S.yaw = S.path.heading(Math.min(1, S.path.total)); else S.yaw = o.yaw;
    const [x, z] = S.path.at(0); S.x = x; S.z = z;
  }
  function pose(S, t) {
    const going = S.state === "going", r = S.root;
    const bob = going ? .07 * Math.sin(t * 1.1 + S.ph) : .035 * Math.sin(t * .8 + S.ph);
    // (what one standing on it follows: its move since it was last posed -- not the jump from over the horizon)
    const ddx = S.x - r.position.x, ddz = S.z - r.position.z;
    if (r.visible && Math.abs(ddx) + Math.abs(ddz) < 5) { S.carry.dx += ddx; S.carry.dz += ddz; S.carry.dyaw += angDiff(r.rotation.y, S.yaw); }
    r.position.set(S.x, level + bob, S.z);
    r.rotation.y = S.yaw;
    // (heel: leeward under sail, a few degrees; the roll and the pitch of the swell)
    r.rotation.x = (going && S.sail ? .055 * S.heel : 0) + (going ? .022 : .007) * Math.sin(t * .9 + S.ph * 1.7);
    r.rotation.z = (going ? .012 : .003) * Math.sin(t * .67 + S.ph * 2.3);
    if (going) {   // (the wake: from the stern)
      const fx = Math.cos(S.yaw), fz = -Math.sin(S.yaw), k = S.swimmer.size * .45 - S.L / 2;
      S.swimmer.position.set(S.x + fx * k, level, S.z + fz * k); S.swimmer.rotY = S.yaw;
    }
    if (S.moored) {   // the plank: from the rail down (or up) to the quay, a hand inland of its face
      const a = S.plankTop(), f = S.plankFoot(), dx = f[0] - a[0], dz = f[2] - a[2], h = Math.hypot(dx, dz), dy = f[1] - a[1];
      S.plank.position.set(a[0], a[1] - .03, a[2]); S.plank.rotation.set(Math.atan2(dy, h), Math.atan2(-dx, -dz), 0);
      S.plank.scale.set(1, 1, Math.hypot(h, dy) / 2.6);
      // (the plank as a floor: its middle, +x down it to the quay, tilted by its fall over its run)
      const pm = S.plankMover, b = pm.body, mx = (a[0] + f[0]) / 2, mz = (a[2] + f[2]) / 2, yw = Math.atan2(-dz, dx);
      pm.carry.dx += mx - b.position.x; pm.carry.dz += mz - b.position.z;
      b.position.set(mx, (a[1] + f[1]) / 2 - .03, mz); b.rotation.set(0, yw, Math.atan2(dy, h)); b.updateMatrixWorld();
      pm.yaw = yw; pm.halfL = h / 2 + .1;
      for (const it of S.hold) { const w = S.holdWorld(it); freight?.placeItem?.(it, w[0], w[1], w[2], S.yaw + (it.slot % 2) * 1.2); }
    }
  }

  // ---- the ways in and out: the lane (sea.js) to the harbour's point on it, then a route over deep water (sea.js route)
  const near = (p) => { let k = 0, d = Infinity; lanePts.forEach((q, i) => { const e = Math.hypot(q[0] - p[0], q[1] - p[1]); if (e < d) { d = e; k = i; } }); return k; };
  const kH = lanePts.length ? near(H.site.lane?.at ?? H.site.mid) : 0;
  const approach = (S, b) => b.kind === "pier" ? [b.mid[0] - b.dir[0] * (S.L + 20) + b.out[0] * 5, b.mid[1] - b.dir[1] * (S.L + 20) + b.out[1] * 5]
    : [b.mid[0] + b.out[0] * 26 - b.dir[0] * (S.L * .6 + 10), b.mid[1] + b.out[1] * 26 - b.dir[1] * (S.L * .6 + 10)];
  const leave = (S, b) => b.kind === "pier" ? approach(S, b) : [b.mid[0] + b.out[0] * 26 + b.dir[0] * (S.L * .6 + 10), b.mid[1] + b.out[1] * 26 + b.dir[1] * (S.L * .6 + 10)];
  const deep = (a, b, S) => SEA.route(a, b, { minDepth: Math.max(2, (S.spec.draught ?? 1.5) + .5), clear: 10 }) ?? [a, b];
  const join = (...parts) => { const out = []; for (const p of parts) for (const q of p) { const l = out[out.length - 1]; if (!l || Math.hypot(l[0] - q[0], l[1] - q[1]) > .5) out.push(q); } return out; };
  const nL = lanePts.length;
  const laneTo = (from, to) => { const out = []; if (lane.closed) { for (let i = from; ; i = (i + 1) % nL) { out.push(lanePts[i]); if (i === to) break; } } else for (let i = from; ; i += Math.sign(to - from) || 1) { out.push(lanePts[i]); if (i === to) break; } return out; };
  const berthEnd = (S, b) => mooredPose(S, b);
  function comeIn(S, b, fromK) {   // from lane point fromK along the lane to the harbour's, then in to the berth
    b.coming = S; S.berth = b;
    const ap = approach(S, b), c = berthEnd(S, b);
    sail(S, join(laneTo(fromK, kH), deep(lanePts[kH], ap, S), [ap, [c.x, c.z]]), "moor", { dock: b });
  }
  function goOut(S) {   // from the berth out (a pier's astern), over deep water to the lane, then away along it
    const b = S.berth, lv = leave(S, b);
    b.ship = null; S.berth = null;
    for (const it of S.hold.slice()) S.hold.splice(S.hold.indexOf(it), 1);   // (nothing is left aboard: the dock asked first)
    const toK = lane.closed ? (kH + Math.floor(nL / 2)) % nL : (R() < .5 ? 0 : nL - 1);
    const pts = join([[S.x, S.z]], [lv], deep(lv, lanePts[kH], S), laneTo(kH, toK));
    sail(S, pts, lane.closed ? "lap" : "gone", { yaw: S.yaw, astern: b.kind === "pier" ? Math.hypot(lv[0] - S.x, lv[1] - S.z) : 0 });
  }
  function passBy(S, k0) {   // a sea's: along the lane from one end to the other (k0: a start part way along); a lake's: once round
    if (!lane) return;
    if (lane.closed) { const k = k0 ?? 0, pts = laneTo(k, (k + nL - 1) % nL); pts.push(lanePts[k]); sail(S, pts, "lap"); return; }
    const fwd = R() < .5, from = k0 ?? (fwd ? 0 : nL - 1);
    sail(S, laneTo(from, fwd ? nL - 1 : 0), "gone");
  }

  // THE STORES: the warehouses (else a store, a market or the office), each a stack of 12 in front of its door. A port
  // with none has no dock: its ships come and go unladen
  const storesOf = P.placements.filter((p) => p.role === "warehouse");
  const fallback = storesOf.length ? storesOf : P.placements.filter((p) => ["store", "market", "office"].includes(p.role)).slice(0, 1);
  const stores = freight?.addDock ? fallback.map((p) => {
    const o = [p.x, p.z], at = (x, z) => { const [wx, wz] = toWorld(o, p.yaw, x, z); return [wx, standY(wx, wz), wz]; };
    const slots = [];
    for (const zz of [1.1, 2.1]) for (const side of [-1, 1]) for (let k = 0; k < 3; k++) slots.push(at(side * (2.1 + k * .95), p.d / 2 + zz));
    return { id: p.id, def: p.def, door: at(0, p.d / 2 + 3.2), slots, yaw: p.yaw };
  }) : [];

  // ---- the fleet: moored ones at the berths that fit them (one kept free where there are two or more), and some under way
  const freeBerths = () => berths.filter((b) => !b.ship && !b.coming);
  const chooseFor = (b) => {
    for (const kind of ["merchant", "merchant", "war", "small"]) {
      const list = (C[kind] ?? []).filter(([id]) => fits(id, b));
      if (list.length) { const id = pickW(list), Ls = T.ships[id].length ?? [8, 12]; return [id, Math.max(Ls[0], Math.min(Ls[1], b.length - 1, between(Ls)))]; }
    }
    return null;
  };
  const nMoor = Math.min(betweenN(PORT_LIFE.moored), Math.max(0, berths.length - (berths.length > 1 ? 1 : 0)));
  const order = berths.slice().sort((p, q) => q.length - p.length);
  for (const b of order.slice(0, nMoor)) { const c = chooseFor(b); if (!c) continue; const S = makeShip(c[0], c[1], ships.length); moor(S, b); }
  if (lane && lanePts.length >= 2) {
    const nGo = betweenN(PORT_LIFE.under), big = berths.length ? Math.max(...berths.map((b) => b.length)) : 30;
    for (let k = 0; k < nGo; k++) {
      const kind = R() < .7 ? "merchant" : "war", list = (C[kind] ?? C.merchant ?? []).filter(([id]) => T.ships[id]);
      if (!list.length) continue;
      const id = pickW(list), Ls = T.ships[id].length ?? [8, 12], S = makeShip(id, Math.min(Ls[1], Math.max(Ls[0], Math.min(big - 1, between(Ls)))), ships.length);
      passBy(S, Math.floor(((k + .2 + R() * .6) / nGo) * (lanePts.length - 1)));   // (spread along the lane)
      S.s = 0;
    }
  }
  for (const S of ships) if (S.state === "gone") show(S, null);
  let nextIn = between(PORT_LIFE.every) * .5;

  // THE DOCK (freight.js addDock): the warehouses' stacks out in front of their doors (above), the hands' posts on the apron
  // THE HANDS' WAY over the apron round what stands on it -- a crane's frame, a shed, a warehouse's corner (each piece's
  // own walls, archgen's wallField, at a walker's height): a straight stretch that meets one goes round by a point
  // beside it, or two
  const solids = H.pieces.filter((p) => p.def?.wallField && !["quay", "pier", "mole"].includes(p.role)).map((p) => ({ p, r: Math.hypot(p.w, p.d) / 2 + 1 }));
  const hit = (x, y, z) => solids.some(({ p, r }) => Math.abs(x - p.x) < r && Math.abs(z - p.z) < r && p.def.wallField(x - p.x, z - p.z, y - p.y + .3, y - p.y + 1.6));
  const clearLine = (a, b) => { const n = Math.max(1, Math.ceil(Math.hypot(b[0] - a[0], b[2] - a[2]) / .3));
    for (let k = 1; k < n; k++) { const t = k / n; if (hit(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)) return false; } return true; };
  const at3 = (x, z) => [x, standY(x, z), z];
  const around = (a, b) => {
    const dx = b[0] - a[0], dz = b[2] - a[2], l = Math.hypot(dx, dz) || 1, nx = -dz / l, nz = dx / l, mx = (a[0] + b[0]) / 2, mz = (a[2] + b[2]) / 2;
    for (const d of [1.5, 2.5, 3.5, 5, 7, 9]) for (const s of [1, -1]) {
      const c = at3(mx + nx * d * s, mz + nz * d * s);
      if (!hit(...c) && clearLine(a, c) && clearLine(c, b)) return [c];
      const c1 = at3(a[0] + nx * d * s, a[2] + nz * d * s), c2 = at3(b[0] + nx * d * s, b[2] + nz * d * s);
      if (clearLine(a, c1) && clearLine(c1, c2) && clearLine(c2, b)) return [c1, c2];
    }
    return [];
  };
  const pathOf = (pts) => { const out = [pts[0]]; for (let i = 1; i < pts.length; i++) { const a = out[out.length - 1], b = pts[i]; if (!clearLine(a, b)) out.push(...around(a, b)); out.push(b); } return out; };
  let dock = null;
  if (stores.length && freight?.addDock) {
    const s0 = stores[0], [fx, , fz] = s0.door, n = norm([s0.door[0] - s0.slots[0][0], s0.door[2] - s0.slots[0][2]]);
    const posts = Array.from({ length: PORT_LIFE.hands }, (_, i) => { const x = fx + n[0] * 1.5 + Math.cos(s0.yaw) * (i - 1) * 1.6, z = fz + n[1] * 1.5 - Math.sin(s0.yaw) * (i - 1) * 1.6; return [x, standY(x, z), z]; });
    dock = freight.addDock({ ships, stores, posts, path: pathOf });
  }

  // THE WAKES (wakes.js): one for each ship under way
  const wakes = createWakes(scene, ships.map((S) => S.swimmer));
  function update(t, dt) {
    if (!(dt > 0)) dt = 0;
    for (const S of ships) {
      S.t += dt;
      if (S.state === "moored") {
        if (S.t > S.stay && !S.hold.length && !(dock?.busy(S)) && lane && lanePts.length >= 2) goOut(S);
      } else if (S.state === "going") {
        const left = S.path.total - S.s, slow = S.end === "moor" ? Math.min(1, .2 + left / 45) : 1, start = Math.min(1, .3 + S.s / 30);
        // (another ship under way close ahead, going the same way: it slows, down to a stop, and keeps its distance)
        let keep = 1;
        const fx = Math.cos(S.yaw), fz = -Math.sin(S.yaw);
        for (const O of ships) {
          if (O === S || O.state !== "going" || Math.cos(O.yaw - S.yaw) < .3) continue;
          const dx = O.x - S.x, dz = O.z - S.z, ahead = dx * fx + dz * fz, gap = (S.L + O.L) / 2 + 8;
          if (ahead > 0 && Math.abs(dx * fz - dz * fx) < (S.B + O.B) / 2 + 6 && ahead < gap * 2) keep = Math.min(keep, Math.max(0, (ahead - gap) / gap));
        }
        S.s = Math.min(S.path.total, S.s + S.speed * slow * start * keep * dt);
        const [x, z] = S.path.at(S.s); S.x = x; S.z = z;
        let want = S.path.heading(S.s);
        if (S.s < S.astern) want += Math.PI;                                                       // (backing off a pier: astern)
        if (S.end === "moor" && left < 35) want += angDiff(want, mooredPose(S, S.dock).yaw) * smooth(1 - left / 35);   // (turning onto the berth's line)
        S.yaw += Math.max(-.3 * dt, Math.min(.3 * dt, angDiff(S.yaw, want)));
        if (S.s >= S.path.total - .05) {
          if (S.end === "moor") moor(S, S.dock);
          else if (S.end === "lap") passBy(S, near([S.x, S.z]));
          else { S.state = "gone"; S.t = 0; S.away = between(PORT_LIFE.away); show(S, null); S.swimmer.hidden = true; S.plank.visible = false; }
        }
      } else if (S.state === "gone" && S.t > S.away) { if (!(nextIn <= 0 && tryIn(S))) passBy(S); }   // (back over the horizon: in to the port, or by)
    }
    // NOW AND THEN ONE COMES IN to a free berth that takes it: a sea's ship as it comes back over the horizon (above), a
    // lake's from its round
    nextIn -= dt;
    if (nextIn <= 0 && lane?.closed) for (const S of ships) if (S.state === "going" && S.end === "lap" && S.s > 10 && tryIn(S)) break;
    for (const S of ships) if (S.state !== "gone") pose(S, t);
    // (the water cut out inside each hull afloat: seawater.js setDryHulls)
    setDryHulls(ships.filter((S) => S.state !== "gone").map((S) => ({ x: S.x, z: S.z, yaw: S.yaw, a: S.dry[0], b: S.dry[1] })));
    wakes.update(t, dt, { surface: surfaceAt, camera });
  }
  function tryIn(S) {
    const b = freeBerths().filter((b) => b.length + 1 >= S.L && (S.spec.draught ?? 1) <= (b.depth ?? 3) + .3).sort((p, q) => p.length - q.length)[0];
    if (!b) return false;
    nextIn = between(PORT_LIFE.every);
    if (S.state === "gone") { show(S, S.go); comeIn(S, b, R() < .5 ? 0 : lanePts.length - 1); }
    else comeIn(S, b, near([S.x, S.z]));
    return true;
  }
  update(0, 0);
  console.log(`harbour: ${ships.length} ships of the ${CK} fleet -- ${ships.filter((S) => S.moored).map((S) => `${S.name} ${S.L.toFixed(0)} m`).join(", ") || "none"} moored, ` +
              `${ships.filter((S) => S.state === "going").length} under way; ${stores.length} warehouse${stores.length === 1 ? "" : "s"}, ${dock ? PORT_LIFE.hands : 0} dock hands`);
  return { ships, berths, stores, dock, update, culture: CK, H };
}
