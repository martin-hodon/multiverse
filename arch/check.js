import { cellOf, index, heightOver, upFacing, pointTri } from "./solid.js";
// STAIRS THAT MAKE SENSE: a check over an assembled building (assemble.js) that every stair can be walked.
//
// A stair part carries its WALKING PATH -- every tread's middle and every landing's, with the stair's width -- and
// its FOOT, half a metre before its first riser. Against every OTHER part of the building:
//   headroom   2m clear above every tread, on the walking line and at both edges: nothing between 0.1 and 2.0m
//              over it (a ceiling it climbs into, a floor it passes under, a column it stands against) -- at the
//              edges (a walker's shoulder reaches them) only what hangs over: undersides, not railings or walls
//   inside     the tread is not inside another part's solid (a stair running through a wall: an upward ray from
//              it crosses that part's surface an odd number of times)
//   foot       it starts on a floor -- the ground (the building's own 0) or an up-facing surface within 15cm --
//              with the same 2m clear above
//   approach   before a straight flight's first riser, a strip as deep as the flight is wide (2m at most) is that floor and as
//              clear (room to stand and begin the climb: not a wall, a barrel, a bin) -- neither asked of a copy that
//              begins on another copy of itself (a tread of a stair wound round a wall: it is mid-climb)
// Findings are data: { stair, kind, at: [x, y, z], by }. The check page prints them; a building is right when
// there are none.

export function stairClearance(asm, { head = 2.0 } = {}) {
  const { cells } = index(asm);
  const out = [];
  const near = (x, z) => cells.get(cellOf(x, z)) ?? [];
  for (const s of asm.parts) {
    if (!s.path) continue;
    // (its OWN stone is this copy's -- a stair repeated storey over storey stands on, and passes under, its other copies)
    s.instances.forEach(([yaw, X, Y, Z], inst) => {
      const mine = (t) => t.inst === inst && (t.part.name === s.name || t.part.name === s.name + " newel");
      const c = Math.cos(yaw), sn = Math.sin(yaw);
      const W = ([x, y, z]) => [x * c + z * sn + X, y + Y, -x * sn + z * c + Z];
      const pts = s.path.map((q) => ({ ...q, p: W(q.p) }));
      const report = (kind, at, by) => { if (out.filter((o) => o.stair === s.name).length < 6) out.push({ stair: s.name, kind, at: at.map((v) => +v.toFixed(2)), by }); };
      pts.forEach((q, i) => {
        const o = pts[Math.min(i + 1, pts.length - 1)], pr = pts[Math.max(i - 1, 0)];
        let dx = o.p[0] - pr.p[0], dz = o.p[2] - pr.p[2]; const l = Math.hypot(dx, dz) || 1; dx /= l; dz /= l;
        const half = Math.max(0, q.w / 2 - .03);   // (at its edges: a walker's shoulder reaches them -- 20cm in, a beam over the edge of a stair's hole went unseen)
        for (const f of [0, -1, 1]) {
          const x = q.p[0] - dz * half * f, z = q.p[2] + dx * half * f, y = q.p[1];
          // headroom: anything over the tread within `head` -- at the EDGES only what hangs over it (an underside: a
          // beam, a slab's edge, a vault), not the stair's own railing or the wall it runs along, standing on the edge
          const rail = (t) => t.part.name.startsWith(s.name + " ") && t.part.name.endsWith("railing");
          for (const t of near(x, z)) {
            if (mine(t) || (f && (upFacing(t) || rail(t)))) continue;
            const h = heightOver(t, x, z);
            if (h !== null && h > y + .1 && h < y + head) { report("headroom", [x, y, z], t.part.name); break; }
          }
          if (f) continue;
          // inside another part's solid: an upward ray crosses its surface an odd number of times
          // (only the triangles over this point can cross the ray: the cell's own list, counted part by part)
          // (the ray is moved a hair off the point: one passing exactly through an edge two triangles share -- a ridge,
          //  a hip -- would count it twice and call the point inside)
          const count = new Map(), rx = x + 1.37e-4, rz = z + 2.71e-4;
          for (const t of near(x, z)) {
            if (t.part.shell || mine(t)) continue;
            const h = heightOver(t, rx, rz);
            if (h !== null && h > y + .1) count.set(t.part, (count.get(t.part) ?? 0) + 1);
          }
          for (const [part, n] of count) if (n % 2) { report("inside", [x, y, z], part.name); break; }
        }
      });
      // (a copy that begins where another copy of the same stair ends -- one tread of a stair wound round a wall, a
      //  flight repeated end to end -- is mid-climb: its foot is that copy's top)
      const midClimb = s.topOf !== undefined && s.instances.some(([, X2, Y2, Z2], j) => j !== inst && Math.abs(Y2 + s.topOf - (Y + s.foot[1])) < .05 && Math.hypot(X2 - X, Z2 - Z) < 1.5);
      if (s.foot && !midClimb) {
        const [x, y, z] = W(s.foot);
        let floor = Math.abs(y) < .05;
        for (const t of near(x, z)) {
          if (mine(t) || !upFacing(t)) continue;
          const h = heightOver(t, x, z);
          if (h !== null && Math.abs(h - y) < .15) { floor = true; break; }
        }
        if (!floor) report("foot", [x, y, z], "(no floor under the foot)");
        for (const t of near(x, z)) {
          if (mine(t)) continue;
          const h = heightOver(t, x, z);
          if (h !== null && h > y + .1 && h < y + head) { report("foot headroom", [x, y, z], t.part.name); break; }
        }
        if (s.approach) {
          const A = s.approach, n = 4;
          let bad = null;
          for (let i = 0; i <= n && !bad; i++) for (let j = 0; j <= n && !bad; j++) {
            const lx = A.x0 + (A.x1 - A.x0) * (.05 + .9 * i / n), lz = A.z0 + (A.z1 - A.z0) * (.05 + .9 * j / n);
            const [px, py, pz] = W([lx, A.y, lz]);
            let fl = Math.abs(py) < .05;
            for (const t of near(px, pz)) {
              if (mine(t)) continue;
              const h = heightOver(t, px, pz);
              if (h === null) continue;
              if (upFacing(t) && Math.abs(h - py) < .15) fl = true;
              else if (h > py + .1 && h < py + head) { bad = [[px, py, pz], t.part.name]; break; }
            }
            if (!bad && !fl) bad = [[px, py, pz], "(no floor before the stair)"];
          }
          if (bad) report("approach", ...bad);
        }
      }
    });
  }
  return out;
}

// NOTHING STANDS ON AIR: every copy of every part is carried, down a chain of parts, to the ground. A part rests on
// another where some point of its underside lies ON that part's surface or INSIDE its solid, hangs from one where
// some point of its top does, and is fixed to one where any corner of it touches its surface; it is carried if it stands on the ground (the building's own 0, or below it: a
// bridge's piers in the water) or rests on, or hangs from, a part that is carried. So a drum set on a neck that was
// left out, with its cap sitting on it, is found -- the two hold each other up, and nothing holds them.
// Findings: { part, inst, kind: "floating", at, gap } -- `gap` how far below its underside the nearest surface of
// another part is (null: none at all).
export function floating(asm, { tol = .03 } = {}) {
  const { cells } = index(asm);
  const near = (x, z) => cells.get(cellOf(x, z)) ?? [];
  const nodes = [];                                          // one per copy of a part
  for (const p of asm.parts) {
    if (p.kind === "glass") continue;                        // (glass sits in its opening's reveal)
    const P = p.geometry.position, I = p.geometry.index, nv = P.length / 3;
    if (!nv) continue;
    p.instances.forEach(([yaw, X, Y, Z], inst) => {
      const c = Math.cos(yaw), s = Math.sin(yaw);
      const V = [];
      for (let j = 0; j < nv; j++) V.push([P[j * 3] * c + P[j * 3 + 2] * s + X, P[j * 3 + 1] + Y, -P[j * 3] * s + P[j * 3 + 2] * c + Z]);
      let lo = Infinity, hi = -Infinity;
      for (const v of V) { if (v[1] < lo) lo = v[1]; if (v[1] > hi) hi = v[1]; }
      // the points it could stand on (or hang by): across its whole underside -- every triangle lying in its lowest
      // 5cm, sampled every 40cm (a wall under a roof is a narrow line), not only its corners (an abacus overhangs its capital, an eave its wall) --
      // and the same across its top
      const face = (inBand) => {
        const pts = [];
        for (let k = 0; k < I.length; k += 3) {
          const a = V[I[k]], b = V[I[k + 1]], d = V[I[k + 2]];
          if (!inBand(a[1]) || !inBand(b[1]) || !inBand(d[1])) continue;
          const L = Math.max(Math.hypot(a[0] - b[0], a[2] - b[2]), Math.hypot(b[0] - d[0], b[2] - d[2]), Math.hypot(d[0] - a[0], d[2] - a[2]));
          // (an even count, so the middle of every edge is sampled: a beam resting on one small block at its middle)
          const n = Math.min(60, 2 * Math.max(1, Math.ceil(L / .8)));
          for (let i = 0; i <= n; i++) for (let j = 0; j <= n - i; j++) {
            const u = i / n, v = j / n, w = 1 - u - v;
            pts.push([a[0] * w + b[0] * u + d[0] * v, a[1] * w + b[1] * u + d[1] * v, a[2] * w + b[2] * u + d[2] * v]);
          }
        }
        if (!pts.length) for (const v of V) if (inBand(v[1])) pts.push(v);     // (a rim, not a face: its points)
        return pts.length <= 4000 ? pts : Array.from({ length: 4000 }, (_, i) => pts[Math.floor(i * pts.length / 4000)]);
      };
      // (a sample of its corners, strewn by the golden ratio: an even stride falls in step with a mesh built of
      //  repeated sections -- every eighth corner of a rib is on its outer face -- and misses all that touch)
      const every = V.length <= 600 ? V : Array.from({ length: 600 }, (_, i) => V[Math.floor(((i * .6180339887) % 1) * V.length)]);
      nodes.push({ key: p.name + "#" + inst, part: p.name, inst, kind: p.kind, ground: lo <= tol, span: hi - lo, every,
                   bottom: face((y) => y < lo + .05), top: face((y) => y > hi - .05) });
    });
  }
  // the copies of parts holding a point: their surface passes through it, or it is inside their solid
  // (a SHELL -- a skin of a dome, a roof's sheet -- has no inside: it holds what passes through it, a point whose part
  //  reaches from below its surface to above it -- a lantern set down into a dome's skin)
  const holders = (x, y, z, self, span = 0) => {
    const out = new Set(), count = new Map();
    for (const t of near(x, z)) {
      const k = t.part.name + "#" + t.inst;
      if (k === self) continue;
      const h = heightOver(t, x, z);
      if (h !== null && (Math.abs(h - y) <= tol || (t.part.shell && h > y && h < y + span))) out.add(k);
      const hr = heightOver(t, x + 1.37e-4, z + 2.71e-4);
      if (hr !== null && hr > y && !t.part.shell && t.part.name !== self.split("#")[0]) count.set(t.part.name, (count.get(t.part.name) ?? 0) + 1);
    }
    // (inside a part is counted over ALL its copies: a ring's bays are open slices, closed only together -- so the
    //  holder is the part, any copy of it: "name#*")
    for (const [k, n] of count) if (n % 2) out.add(k + "#*");
    return out;
  };
  for (const n of nodes) {
    n.by = new Set();
    if (n.ground) continue;
    for (const [x, y, z] of n.bottom) for (const k of [...holders(x, y, z, n.key, n.span), ...holders(x, y - tol / 2, z, n.key)]) n.by.add(k);
    for (const [x, y, z] of n.top) for (const k of [...holders(x, y, z, n.key), ...holders(x, y + tol / 2, z, n.key)]) n.by.add(k);
    // ...or it is fixed to one at the side: a flyer against its pier and its wall, a landing against the walls round
    // it, a rib on its vault -- some corner of it lies on another part's surface
    for (const v of n.every) for (const t of near(v[0], v[2])) {
      const k = t.part.name + "#" + t.inst;
      if (k !== n.key && !n.by.has(k) && pointTri(v, t) <= tol) n.by.add(k);
    }
  }
  // ...and a part RESTS ON whatever reaches up to it from below: another's top lying on its surface or set into its
  // solid. A roof's own lowest band is its eave, out in the air; what carries it are the beams of its bracket sets,
  // whose tops meet its soffit somewhere up the slope. (Contact is contact: seen from the beam, the roof hangs from it.)
  const byKey = new Map(nodes.map((n) => [n.key, n]));
  for (const b of nodes) for (const [x, y, z] of b.top) for (const k of holders(x, y, z, b.key)) {
    if (k.endsWith("#*")) { for (const n of nodes) if (n.part + "#*" === k && n.key !== b.key) n.by.add(b.key); }
    else byKey.get(k)?.by.add(b.key);
  }
  // carried: on the ground, or held by something carried -- to a fixed point
  const carried = new Set(nodes.filter((n) => n.ground).map((n) => n.key));
  const any = new Set(nodes.filter((n) => n.ground).map((n) => n.part + "#*"));   // (parts with some copy carried)
  for (let changed = true; changed;) {
    changed = false;
    for (const n of nodes) if (!carried.has(n.key) && [...n.by].some((k) => carried.has(k) || any.has(k))) {
      carried.add(n.key); any.add(n.part + "#*"); changed = true;
    }
  }
  const out = [];
  // A WALL STANDING ALONE: a wall or a ring of walls that touches nothing of the building but the platform under it
  // (it stands, but apart -- a front a metre and a half off the walls it should close)
  for (const n of nodes) {
    if (!["wall", "enclosure"].includes(n.kind)) continue;
    let joined = false;
    for (const v of n.every) {
      for (const t of near(v[0], v[2])) {
        const k = t.part.name + "#" + t.inst;
        if (k === n.key || t.part.name === "base") continue;
        if (pointTri(v, t) <= tol) { joined = true; break; }
      }
      if (!joined) joined = [...holders(v[0], v[1], v[2], n.key)].some((k) => !k.startsWith("base#"));   // (or set into one)
      if (joined) break;
    }
    if (!joined) out.push({ part: n.part, inst: n.inst, kind: "isolated", at: n.every[0].map((v) => +v.toFixed(2)), gap: null });
  }
  // A HALF DOME OPEN TO THE SKY: a semidome's cut face must look into the building (something over it: the roof of
  // the choir it opens into) or be closed by another part (the choir's end wall) -- not stand open above the roofs
  for (const p of asm.parts) {
    if (!p.cut) continue;
    const top = (x) => { for (let i = 0; i + 1 < p.cut.length; i++) { const [x0, y0] = p.cut[i], [x1, y1] = p.cut[i + 1];
      if ((x0 - x) * (x1 - x) <= 0 && x0 !== x1) return y0 + (y1 - y0) * (x - x0) / (x1 - x0); } return 0; };
    const r = Math.max(...p.cut.map(([x]) => x));
    p.instances.forEach(([yaw, X, Y, Z], inst) => {
      const c = Math.cos(yaw), sn = Math.sin(yaw), self = p.name + "#" + inst;
      for (let x = -r * .9; x <= r * .9 + 1e-9; x += Math.max(.5, r / 12)) for (let y = .3; y < top(Math.abs(x)) * .95; y += .5) {
        const lx = x, lz = -.05, w = [lx * c + lz * sn + X, y + Y, -lx * sn + lz * c + Z];
        let covered = holders(w[0], w[1], w[2], self).size > 0;
        if (!covered) for (const t of near(w[0], w[2])) {
          if (t.part.name === p.name) continue;
          const h = heightOver(t, w[0], w[2]);
          if (h !== null && h > w[1]) { covered = true; break; }
        }
        if (!covered) { out.push({ part: p.name, inst, kind: "open", at: w.map((v) => +v.toFixed(2)), gap: null }); return; }
      }
    });
  }
  for (const n of nodes) {
    if (carried.has(n.key)) continue;
    let gap = null;
    for (const [x, y, z] of n.bottom) for (const t of near(x, z)) {
      if (t.part.name + "#" + t.inst === n.key) continue;
      const h = heightOver(t, x, z);
      if (h !== null && h < y - tol && (gap === null || y - h < gap)) gap = y - h;
    }
    out.push({ part: n.part, inst: n.inst, kind: "floating", at: n.bottom[0].map((v) => +v.toFixed(2)), gap: gap === null ? null : +gap.toFixed(2) });
  }
  return out;
}

// FURNITURE WITH ROOM ROUND IT: every set of furniture on a floor, in nothing solid and out of the doorways and a stair's
// approach -- the test the assembly fits the furniture by (room.js), asked of what stands now. Findings: { part, inst,
// kind ("floor", "inside", "way"), at, by }; an assembled building has none (what could not stand was moved or left out).
export { furnitureFindings as furnishing } from "./room.js";
