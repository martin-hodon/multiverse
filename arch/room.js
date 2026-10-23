// ROOM FOR THE FURNITURE (2026-10-23; docs/arch.md "Furniture with room round it"). A building's furniture -- its solid
// `item` parts: beds, tables and their benches, chests, casks, pews -- stands where its definition's numbers put it,
// and the same numbers in a smaller house, or with a trade's workshop in the front room, put a bed through the
// chimney, a bench into the forge, a table into the wall or across a doorway. So once a building is assembled
// (assemble.js, the whole building: not each component on its own) every SET of furniture -- the pieces placed
// together: a table and its benches, a row of casks, a bed -- is tested where it stands:
//   standing   every point of its footprint, a little over its foot, is on a floor (an up-facing surface at its foot,
//              or the building's own ground), in no other part's solid -- a wall, a chimney, a column, a stair, a
//              railing, another set -- and out of the ways: ROOM.door deep either side of a door, across its width
//              and ROOM.side more, and the approach before a stair's foot
//   moved      if not, to the nearest place within ROOM.reach where it stands so -- the set as one, turned as it was --
//              its markers (the seats on its benches, the bed's sleepers, the places at a table) going with it
//   left out   when there is none (a small house with a trade in its front room has no room for the dining table)
import { index, cellOf, heightOver, upFacing } from "./solid.js";

export const ROOM = { door: 1.0, side: .1, reach: 2.4, step: .15, near: 1.2, foot: .15, over: .3, storey: 1.5 };

// a part's own box (an item's: its geometry is the box -- assemble.js `item`)
function boxOf(P) {
  const lo = [1e9, 1e9, 1e9], hi = [-1e9, -1e9, -1e9];
  for (let j = 0; j < P.length; j += 3) for (let q = 0; q < 3; q++) { lo[q] = Math.min(lo[q], P[j + q]); hi[q] = Math.max(hi[q], P[j + q]); }
  return { lo, hi };
}
// an oriented rectangle on the ground: a frame (yaw at X, Z) and its extent in it, at height Y
const frame = (yaw, X, Y, Z, x0, x1, z0, z1, by) => ({ c: Math.cos(yaw), s: Math.sin(yaw), X, Y, Z, x0, x1, z0, z1, by });
const within = (r, x, z, e = 0) => {
  const dx = x - r.X, dz = z - r.Z, lx = dx * r.c - dz * r.s, lz = dx * r.s + dz * r.c;
  return lx > r.x0 - e && lx < r.x1 + e && lz > r.z0 - e && lz < r.z1 + e;
};

// the furniture's pieces (a solid item part's every copy) and the ways kept clear (doorways, stair approaches)
function survey(parts) {
  const pieces = [], ways = [];
  for (const p of parts) {
    if (p.kind === "marker" && p.role === "door")
      for (const [yaw, X, Y, Z] of p.instances) { const w = (p.data?.w ?? 1) / 2 + ROOM.side; ways.push(frame(yaw, X, Y, Z, -w, w, -ROOM.door, ROOM.door, p.name)); }
    if (p.approach) { const A = p.approach; for (const [yaw, X, Y, Z] of p.instances) ways.push(frame(yaw, X, Y + A.y, Z, A.x0, A.x1, A.z0, A.z1, p.name + " (its foot)")); }
    if (p.kind !== "item" || !p.geometry.position.length) continue;
    const { lo, hi } = boxOf(p.geometry.position);
    p.instances.forEach(([yaw, X, Y, Z], inst) => {
      const r = frame(yaw, X, Y + lo[1], Z, lo[0], hi[0], lo[2], hi[2], p.name);
      const pts = [];
      for (let i = 0; i <= 4; i++) for (let k = 0; k <= 4; k++) {
        const lx = lo[0] + .04 + (hi[0] - lo[0] - .08) * i / 4, lz = lo[2] + .04 + (hi[2] - lo[2] - .08) * k / 4;
        pts.push([lx * r.c + lz * r.s + X, -lx * r.s + lz * r.c + Z]);
      }
      const cx = (lo[0] + hi[0]) / 2, cz = (lo[2] + hi[2]) / 2;
      pieces.push({ part: p, inst, r, pts, foot: Y + lo[1], y: Y + lo[1] + Math.min(ROOM.over, (hi[1] - lo[1]) / 2), top: Y + hi[1],
                    at: [cx * r.c + cz * r.s + X, -cx * r.s + cz * r.c + Z], dx: 0, dz: 0,
                    group: p.name.includes("/") ? p.name.slice(0, p.name.lastIndexOf("/")) : p.name });
    });
  }
  return { pieces, ways };
}

// the SETS: a group's pieces (one component's: "table/table" and "table/benches") near one another -- a component
// placed twice (a tavern's two tables) is two sets
function setsOf(pieces) {
  const byGroup = new Map();
  for (const pc of pieces) { let l = byGroup.get(pc.group); if (!l) byGroup.set(pc.group, l = []); l.push(pc); }
  const sets = [];
  for (const [group, l] of byGroup) {
    const root = l.map((_, i) => i), find = (i) => (root[i] === i ? i : (root[i] = find(root[i])));
    for (let i = 0; i < l.length; i++) for (let j = i + 1; j < l.length; j++)
      if (Math.hypot(l[i].at[0] - l[j].at[0], l[i].at[1] - l[j].at[1]) < ROOM.near && Math.abs(l[i].foot - l[j].foot) < ROOM.storey) root[find(i)] = find(j);
    const m = new Map();
    l.forEach((pc, i) => { const k = find(i); if (!m.has(k)) m.set(k, []); m.get(k).push(pc); });
    for (const s of m.values()) sets.push({ group, pieces: s });
  }
  return sets;
}

// what is in a solid at (x, y, z): a part (not the furniture -- that is tested box by box) its surface crosses an odd
// number of times both above the point and below it (one only above -- a roof open underneath -- is not round it)
function solidAt(cells, x, y, z) {
  const up = new Map(), down = new Map(), rx = x + 1.37e-4, rz = z + 2.71e-4;
  for (const t of cells.get(cellOf(x, z)) ?? []) {
    if (t.part.shell || t.part.item) continue;
    const h = heightOver(t, rx, rz);
    if (h === null) continue;
    const m = h > y ? up : down;
    m.set(t.part.name, (m.get(t.part.name) ?? 0) + 1);
  }
  for (const [k, n] of up) if (n % 2 && (down.get(k) ?? 0) % 2) return k;
  return null;
}
const floorAt = (cells, x, z, foot) => {
  if (Math.abs(foot) < .05) return true;   // (the building's own ground)
  for (const t of cells.get(cellOf(x, z)) ?? []) {
    if (!upFacing(t) || t.part.item) continue;
    const h = heightOver(t, x, z);
    if (h !== null && Math.abs(h - foot) < ROOM.foot) return true;
  }
  return false;
};

// why a set cannot stand moved by (dx, dz): { kind, at, by }, or null where it can
function blocked(set, dx, dz, cells, ways, pieces) {
  for (const pc of set.pieces) for (const [x0, z0] of pc.pts) {
    const x = x0 + dx, z = z0 + dz, at = [x, pc.y, z];
    if (!floorAt(cells, x, z, pc.foot)) return { kind: "floor", at, by: "(no floor under it)" };
    const by = solidAt(cells, x, pc.y, z);
    if (by) return { kind: "inside", at, by };
    for (const o of pieces) {   // (another set's piece, where it stands now)
      if (o.set === set || o.gone || pc.y < o.r.Y || pc.y > o.top) continue;
      if (within(o.r, x - o.dx, z - o.dz)) return { kind: "inside", at, by: o.part.name };
    }
    for (const w of ways) if (Math.abs(w.Y - pc.foot) < ROOM.storey && within(w, x, z)) return { kind: "way", at, by: w.by };
  }
  return null;
}

// the parts' cells, the furniture left out of them (it is tested box by box, as it moves)
function cellsOf(parts) {
  const { cells, parts: own } = index({ parts });
  parts.forEach((p, i) => { if (p.kind === "item") own[i].item = true; });
  return cells;
}

// WHAT STANDS WRONG, as it stands (check.js `furnishing`): { part, inst, kind, at, by }
export function furnitureFindings(asm) {
  const cells = cellsOf(asm.parts), { pieces, ways } = survey(asm.parts), out = [];
  for (const set of setsOf(pieces)) {
    set.pieces.forEach((pc) => { pc.set = set; });
    const b = blocked(set, 0, 0, cells, ways, pieces);
    if (b) out.push({ part: set.pieces[0].part.name, inst: set.pieces[0].inst, kind: b.kind, at: b.at.map((v) => +v.toFixed(2)), by: b.by });
  }
  return out;
}

// THE FIT: every set that does not stand moved to the nearest place it does, or left out -- the parts changed in
// place; returns what was done: [{ set, moved: [dx, dz] } | { set, left: why }]
export function fitFurniture(parts) {
  const { pieces, ways } = survey(parts);
  if (!pieces.length) return [];
  const cells = cellsOf(parts), sets = setsOf(pieces), done = [];
  for (const set of sets) set.pieces.forEach((pc) => { pc.set = set; });
  const tries = [];
  for (let i = -Math.round(ROOM.reach / ROOM.step); i <= Math.round(ROOM.reach / ROOM.step); i++)
    for (let k = -Math.round(ROOM.reach / ROOM.step); k <= Math.round(ROOM.reach / ROOM.step); k++) {
      const dx = i * ROOM.step, dz = k * ROOM.step, d = Math.hypot(dx, dz);
      if (d > 0 && d <= ROOM.reach) tries.push([d, dx, dz]);
    }
  tries.sort((a, b) => a[0] - b[0]);
  const markers = parts.filter((p) => p.kind === "marker");
  const gone = new Map();   // part -> the copies left out
  for (const set of sets) {
    const why = blocked(set, 0, 0, cells, ways, pieces);
    if (!why) continue;
    const to = tries.find(([, dx, dz]) => !blocked(set, dx, dz, cells, ways, pieces));
    // its markers: the group's, standing on one of its pieces
    const mine = [];
    for (const m of markers) {
      if (!m.name.startsWith(set.group + "/")) continue;
      m.instances.forEach(([, X, Y, Z], i) => { if (set.pieces.some((pc) => Math.abs(pc.foot - Y) < ROOM.storey && within(pc.r, X, Z, .3))) mine.push([m, i]); });
    }
    if (to) {
      const [, dx, dz] = to;
      for (const pc of set.pieces) { pc.dx = dx; pc.dz = dz; const q = pc.part.instances[pc.inst]; pc.part.instances[pc.inst] = [q[0], q[1] + dx, q[2], q[3] + dz]; }
      for (const [m, i] of mine) { const q = m.instances[i]; m.instances[i] = [q[0], q[1] + dx, q[2], q[3] + dz]; }
      done.push({ set: set.group, moved: [+dx.toFixed(2), +dz.toFixed(2)], was: why });
    } else {
      for (const pc of set.pieces) { pc.gone = true; if (!gone.has(pc.part)) gone.set(pc.part, new Set()); gone.get(pc.part).add(pc.inst); }
      for (const [m, i] of mine) { if (!gone.has(m)) gone.set(m, new Set()); gone.get(m).add(i); }
      done.push({ set: set.group, left: why });
    }
  }
  for (const [p, s] of gone) p.instances = p.instances.filter((_, i) => !s.has(i));
  return done;
}
