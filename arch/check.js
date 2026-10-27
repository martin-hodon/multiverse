import { cellOf, index, heightOver, upFacing, pointTri, rayIndex, rayHits, rayDist, insideOf } from "./solid.js";
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
      // ARRIVAL: a stair leads somewhere. Past the end of its walk -- its last tread, or the landing it ends on -- the walker
      // steps off onto a floor (another part's up-facing surface within 15cm of the top, or the ground), straight on or to
      // either side; a stair whose top is in the air, or whose landing is a ledge with nothing round it, is found. (A copy
      // that another copy of the same stair carries on from -- a stair wound tread by tread, a flight repeated storey over
      // storey -- arrives on that one.)
      if (pts.length >= 2) {
        const e = pts[pts.length - 1], b = pts[pts.length - 2];
        let ux = e.p[0] - b.p[0], uz = e.p[2] - b.p[2]; const ul = Math.hypot(ux, uz) || 1; ux /= ul; uz /= ul;
        const yTop = e.p[1], reach = (e.landing ? (e.len ?? .9) / 2 : .25) + .35, half = e.w / 2 + .35;
        const goesOn = s.instances.some(([, X2, Y2, Z2], j) => j !== inst && s.foot && Math.abs(Y2 + s.foot[1] - yTop) < .3 && Math.hypot(X2 - X, Z2 - Z) < 1.5 + e.w);
        const floorAt = (x, z, yTop = e.p[1]) => {
          if (Math.abs(yTop) < .05) return true;
          for (const t of near(x, z)) {
            if (mine(t) || !upFacing(t)) continue;
            const h = heightOver(t, x, z);
            if (h !== null && Math.abs(h - yTop) < .15) return true;
          }
          return false;
        };
        const offs = [[ux * reach, uz * reach], [-uz * half, ux * half], [uz * half, -ux * half]];
        // (a staircase's top LANDING is stepped off across any of its free edges -- the floor may begin at its far side,
        //  a landing's width from the middle: probed 35cm past each free edge at the top, along its length)
        const yMax = Math.max(...pts.map((q) => q.p[1]));
        const across = (s.edges ?? []).filter((g) => Math.abs(g.a[1] + Y - yMax) < .05).some((g) => {
          const A = W(g.a), B = W(g.b), nl = Math.hypot(g.n[0], g.n[1]) || 1, nx = g.n[0] / nl, nz = g.n[1] / nl;
          const wx = nx * c + nz * sn, wz = -nx * sn + nz * c;
          return [.1, .3, .5, .7, .9].some((f) => floorAt(A[0] + (B[0] - A[0]) * f + wx * .35, A[2] + (B[2] - A[2]) * f + wz * .35, yMax));
        });
        if (!goesOn && !across && !offs.some(([dx, dz]) => floorAt(e.p[0] + dx, e.p[2] + dz))) report("arrival", e.p, "(nothing to step off onto at the top)");
      }
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
// another part is (null: none at all) -- and "isolated", "open", "on roof" (below).
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
      nodes.push({ key: p.name + "#" + inst, part: p.name, inst, kind: p.kind, ground: lo <= tol, lo, span: hi - lo, every,
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
  const kindOf = new Map(asm.parts.map((p) => [p.name, p.kind])), roofy = (k) => kindOf.get(k.slice(0, k.lastIndexOf("#"))) === "roof";
  for (const n of nodes) {
    n.by = new Set(); n.soft = 0; n.hard = 0;
    if (n.ground) continue;
    for (const [x, y, z] of n.bottom) {
      const hs = [...holders(x, y, z, n.key, n.span), ...holders(x, y - tol / 2, z, n.key)];
      for (const k of hs) n.by.add(k);
      // (what this point of its foot bears on: masonry, or only a roof -- unless masonry stands right under the roof
      //  there, a flat roof's slab laid on its walls, which carries the parapet over them down onto them)
      if (hs.length) {
        const through = hs.every(roofy) && near(x, z).some((t) => {
          if (t.part.kind === "roof" || t.part.name + "#" + t.inst === n.key) return false;
          const h = heightOver(t, x, z); return h !== null && h < y - tol && h > y - 1.5;
        });
        if (hs.every(roofy) && !through) n.soft++; else n.hard++;
      }
    }
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
  // BUILT FROM THE GROUND UP: the parts are raised in their build order, and each must be carried by what stands
  // already -- the ground, or a part built before it -- as a mason cannot set a lantern before the dome it stands on.
  // A part carried in the end, but only by one built after it, is reported "before support", with the part it
  // waits for; then it counts as built, so what stands on it is not reported again. Parts named alike but for a number
  // ("upper floor 3", "upper floor 7": one floor cut in pieces round its stairwells) are one element: a piece may lean
  // on another piece of it, wherever that one is listed.
  const famOf = (name) => name.replace(/ \d+$/, ""), partOf = (k) => k.slice(0, k.lastIndexOf("#"));
  const rank = new Map(asm.parts.map((p, i) => [p.name, i]));
  const up = new Set(), upAny = new Set(), turns = new Map();
  for (const n of nodes) { if (!turns.has(n.part)) turns.set(n.part, []); turns.get(n.part).push(n); }
  for (const group of turns.values()) {
    const raise = (n) => { up.add(n.key); upAny.add(n.part + "#*"); };
    const kin = (n, k) => famOf(partOf(k)) === famOf(n.part) && (carried.has(k) || any.has(k));
    for (let changed = true; changed;) {
      changed = false;
      for (const n of group) if (!up.has(n.key) && (n.ground || [...n.by].some((k) => up.has(k) || upAny.has(k) || kin(n, k)))) { raise(n); changed = true; }
    }
    const late = group.find((n) => !up.has(n.key) && carried.has(n.key));
    if (late) {
      const after = [...late.by].map(partOf).filter((k) => (rank.get(k) ?? -1) > rank.get(late.part)
        && nodes.some((m) => m.part === k && carried.has(m.key)));
      out.push({ part: late.part, inst: late.inst, kind: "before support", at: late.bottom[0].map((v) => +v.toFixed(2)), gap: null, by: [...new Set(after)].join(", ") });
    }
    for (const n of group) if (carried.has(n.key)) raise(n);
  }
  // A WALL STANDING ALONE: a wall or a ring of walls that touches nothing of the building but the platform under it
  // (it stands, but apart -- a front a metre and a half off the walls it should close)
  for (const n of nodes) {
    if (!["wall", "enclosure"].includes(n.kind)) continue;
    let joined = false;
    // (its corners, and points along its foot: a band round a tower has its corners where two walls of one part
    //  overlap -- inside both copies, an even count, "outside" -- and lies in one wall all along between)
    const foot = n.bottom.length <= 200 ? n.bottom : Array.from({ length: 200 }, (_, i) => n.bottom[Math.floor(i * n.bottom.length / 200)]);
    for (const v of [...n.every, ...foot]) {
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
  // MASONRY ON A ROOF: a wall, a ring of walls, a drum, a dome is carried down to the ground through walls and piers -- a
  // roof is a covering, spanning the space under it on its rafters, and bears nothing heavier than a dormer's cheek. A
  // masonry part standing (most of its foot) on roofs alone stands on air with a roof drawn over it: the drum of a dome
  // set on the attic roof with no piers under it inside. (Not a band of marble fixed to a wall's face, its foot on the
  // roof against it: it is fixed to the wall.)
  for (const n of nodes) {
    if (!["wall", "enclosure", "ring", "dome"].includes(n.kind) || n.soft < 3 || n.soft <= n.hard) continue;
    // (fixed to masonry up its side -- on its surface or set into it, halfway between its foot and its top, where
    //  what it carries stands: cladding, a band on a wall)
    const ym = n.lo + n.span / 2;
    const clad = n.every.some(([x, , z]) =>
      near(x, z).some((t) => t.part.kind !== "roof" && t.part.name + "#" + t.inst !== n.key && pointTri([x, ym, z], t) <= tol) ||
      [...holders(x, ym, z, n.key)].some((k) => !roofy(k)));
    if (clad) continue;
    out.push({ part: n.part, inst: n.inst, kind: "on roof", at: n.bottom[0].map((v) => +v.toFixed(2)), gap: null });
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

// A VAULT IS ABUTTED: an arch pushes out at its feet as well as down, and what it springs from must take that push --
// the mason's rule, from Vitruvius' counterforts to Blondel's construction, that the wall or pier behind a vault's
// springing be some share of its span deep (a quarter for a round barrel on a plain wall; less where the push is
// gathered to piers and buttresses, as a groin vault's is). So from every springing -- a barrel's along both its sides,
// a groin vault's at its four corners, out along each of its two spans, a ring vault's at its bay's middle, out and in
// -- the push is followed out: level, a little above the springing, and from the springing joint falling as the weight
// above turns it down, at two slopes. What lies along it is counted: masonry (inside some part's solid), or air under cover (the next bay,
// whose vault pushes back, or an aisle under its roof), until it reaches the open sky. The deepest of the three is the
// abutment, and it must be a tenth of the span at least (`ratio`): a nave's vault on a 1.4m wall over 9m takes 0.16;
// a vault left leaning on a wall's skin, or springing at a wall's end with nothing past it, takes nothing.
// (Not a Gothic system's vaults -- its flyers are set out from their thrust (gothic.js) -- nor a part built `light`, of
// poles and bark, that pushes nothing.)
// Findings: { part, inst, kind: "thrust", at, gap: the abutment found, need }.
export function abutment(asm, { ratio = .1 } = {}) {
  const idx = rayIndex(asm), out = [];
  for (const p of asm.parts) {
    if (!(p.kind === "groin" || p.kind === "barrel" || (p.kind === "vault" && p.count && p.face)) || p.light || p.abutted) continue;
    const P = p.geometry.position;
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity, z0 = Infinity, z1 = -Infinity;
    for (let j = 0; j < P.length; j += 3) {
      x0 = Math.min(x0, P[j]); x1 = Math.max(x1, P[j]); y0 = Math.min(y0, P[j + 1]); y1 = Math.max(y1, P[j + 1]);
      z0 = Math.min(z0, P[j + 2]); z1 = Math.max(z1, P[j + 2]);
    }
    const cx = (x0 + x1) / 2, cz = (z0 + z1) / 2;
    // the springings, in the part's frame: [x, z, push x, push z, span, side shifts] -- a corner's push followed a hand
    // to either side of it, into the pier it stands on (along a wall's face, or past a wall's end, it would run in no
    // stone at all), the better of the two its abutment
    const at = [];
    if (p.kind === "groin") {
      for (const x of [x0, x1]) for (const z of [z0, z1]) {
        const sx = Math.sign(x - cx), sz = Math.sign(z - cz);
        at.push([x, z, sx, 0, x1 - x0, [[0, .1 * sz], [0, -.1 * sz]]], [x, z, 0, sz, z1 - z0, [[.1 * sx, 0], [-.1 * sx, 0]]]);
      }
    } else if (p.kind === "barrel") {
      for (const z of [z0 + .2, cz, z1 - .2]) for (const x of [x0, x1]) at.push([x, z, Math.sign(x - cx), 0, x1 - x0, [[0, 0]]]);
    } else {
      let rI = Infinity, rO = 0, ax = 0, az = 0;
      for (let j = 0; j < P.length; j += 3) {
        ax += P[j]; az += P[j + 2];
        if (P[j + 1] < y0 + .01) { const r = Math.hypot(P[j], P[j + 2]); rI = Math.min(rI, r); rO = Math.max(rO, r); }
      }
      const a = Math.atan2(az, ax), ux = Math.cos(a), uz = Math.sin(a);
      at.push([ux * rO, uz * rO, ux, uz, rO - rI, [[0, 0]]]);
      if (rI > .5) at.push([ux * rI, uz * rI, -ux, -uz, rO - rI, [[0, 0]]]);   // (and in, onto the ring of piers it springs from inside)
    }
    const rise = Math.min(y1 - y0, p.crown ? p.crown - y0 : Infinity);
    p.instances.forEach(([yaw, X, Y, Z], inst) => {
      const c = Math.cos(yaw), s = Math.sin(yaw);
      for (const [lx, lz, dx, dz, span, shifts] of at) {
        const wx = lx * c + lz * s + X, wz = -lx * s + lz * c + Z, d = [dx * c + dz * s, -dx * s + dz * c];
        let best = 0;
        for (const [ox, oz] of shifts) for (const fall of [0, .6, 1.2]) {
          if (best >= span * ratio) break;
          const sx = lx + ox, sz = lz + oz, px = sx * c + sz * s + X, pz = -sx * s + sz * c + Z;
          const o = [px - d[0] * .08, y0 + Y + (fall ? -.05 : Math.min(Math.max(.15, span / 8), rise * .3)), pz - d[1] * .08];
          const T = Math.max(3, Math.min(12, span)), st = .05;
          let depth = 0, free = false;
          for (let t = st; t <= T; t += st) {
            const q = [o[0] + d[0] * t, o[1] - t * fall, o[2] + d[1] * t];
            if (q[1] <= .05) break;                                                   // (down to the ground: carried)
            if (insideOf(idx.cells, q[0], q[1], q[2]).length) { depth += st; continue; }
            // (out under the sky -- the ray nudged off the point as insideOf's is: straight up a bay's middle it can run
            //  exactly along the edges the meshes are split on, and slip between the triangles either side)
            if (rayDist(idx, [q[0] + 1.37e-4, q[1], q[2] + 2.71e-4], [0, 1, 0], 300) === Infinity) { free = true; break; }
          }
          best = Math.max(best, free ? depth : Infinity);
        }
        if (best < span * ratio) {
          out.push({ part: p.name, inst, kind: "thrust", at: [wx, y0 + Y, wz].map((v) => +v.toFixed(2)), gap: +best.toFixed(2), need: +(span * ratio).toFixed(2) });
          return;
        }
      }
    });
  }
  return out;
}

// FURNITURE WITH ROOM ROUND IT: every set of furniture on a floor, in nothing solid and out of the doorways and a stair's
// approach -- the test the assembly fits the furniture by (room.js), asked of what stands now. Findings: { part, inst,
// kind ("floor", "inside", "way"), at, by }; an assembled building has none (what could not stand was moved or left out).
export { furnitureFindings as furnishing } from "./room.js";

// A LINTEL HAS A LENGTH: a flat head is one beam -- a stone, a timber -- laid across its opening, and no quarry or
// forest gives one past a few metres; the Parthenon's architraves span 4.3m from column to column, and wider than
// that a builder turns an arch, or sets pillars in the opening, or corbels brackets out to shorten it. So what counts
// is the FREE span: the longest stretch of the beam's underside with nothing under it -- along the opening, a hand
// under the springing, through the wall's thickness and as much again either side (a pillar standing in the opening,
// a column of a portico before it, a bracket out of a jamb). Over `max` (4.5m) is found: `gap` the free span --
// unless its part is built `light` (poles and laths: no stone), or says what its builders could set (`beam`: the
// Egyptians quarried sandstone architraves of six metres and more for a processional way).
export function lintels(asm, { max = 4.5 } = {}) {
  const out = [];
  let cells = null;
  for (const p of asm.parts) {
    if (!p.lintels?.length || p.light) continue;
    p.instances.forEach(([yaw, X, Y, Z], inst) => {
      const c = Math.cos(yaw), s = Math.sin(yaw), W = ([x, z]) => [x * c + z * s, -x * s + z * c];
      const lim = p.beam ?? max;
      for (const { at: [x, y, z], span, e, t } of p.lintels) {
        if (span <= lim + 1e-6) continue;
        cells ??= index(asm).cells;
        const [cx, cz] = W([x, z]), [ex, ez] = W(e), yU = y + Y - .1;
        // (along it every 10cm, jamb to jamb, at five depths from a wall's thickness outside the face to two inside)
        const n = Math.ceil(span / .1), held = [];
        for (let k = 0; k <= n; k++) {
          const u = -span / 2 + span * k / n;
          held.push([-1, -.5, 0, .5, 1, 1.5, 2].some((d) => {
            const px = cx + X + ex * u + ez * d * t, pz = cz + Z + ez * u - ex * d * t;
            return insideOf(cells, px, yU, pz, p.name).length > 0;
          }));
        }
        // (the jambs hold its ends; the free span is the widest stretch between held points)
        let free = 0, last = 0;
        held[0] = held[n] = true;
        for (let k = 1; k <= n; k++) if (held[k]) { free = Math.max(free, (k - last - 1) * span / n); last = k; }
        if (free > lim + 1e-6) out.push({ part: p.name, inst, kind: "lintel", at: [cx + X, y + Y, cz + Z].map((v) => +v.toFixed(2)), gap: +free.toFixed(2), need: lim });
      }
    });
  }
  return out;
}

// THE VAULT IS ROOFED: a groin vault's cells open on each side in an arch -- its lunette -- and a wall must stand in
// that arch, or an arcade under it, up to where the roof takes over. A wall stopped at the vault's springing, under a
// roof set on the vault's crown, leaves every lunette open to the sky the length of the nave. So from the middle of
// every bay, level rays are cast out through its four mouths at two fifths of its rise and four fifths: one that leaves the building
// is a hole IF something stands just under its path where it passes the mouth -- the top of a wall stopped short. (A
// loggia's arch under a vault is open as it should be: under it the air runs down to the floor.)
// Findings: { part, inst, kind: "open vault", at } -- `at` where the ray leaves the vault.
export function vaultsRoofed(asm) {
  const idx = rayIndex(asm), out = [];
  for (const p of asm.parts) {
    if (p.kind !== "groin") continue;
    const P = p.geometry.position;
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity, z0 = Infinity, z1 = -Infinity;
    for (let j = 0; j < P.length; j += 3) {
      x0 = Math.min(x0, P[j]); x1 = Math.max(x1, P[j]); y0 = Math.min(y0, P[j + 1]); y1 = Math.max(y1, P[j + 1]);
      z0 = Math.min(z0, P[j + 2]); z1 = Math.max(z1, P[j + 2]);
    }
    const crown = p.crown ?? y1, cx = (x0 + x1) / 2, cz = (z0 + z1) / 2;
    p.instances.forEach(([yaw, X, Y, Z], inst) => {
      const c = Math.cos(yaw), s = Math.sin(yaw), W = (x, z) => [x * c + z * s + X, -x * s + z * c + Z];
      const [ox, oz] = W(cx, cz);
      // (the four mouths: the ray's way out, and how far from the middle the mouth is; low in the lunette and high)
      for (const f of [.4, .8]) for (const [lx, lz, reach] of [[1, 0, x1 - cx], [-1, 0, cx - x0], [0, 1, z1 - cz], [0, -1, cz - z0]]) {
        const ym = y0 + f * (crown - y0), o = [ox, ym + Y, oz];
        const d = [lx * c + lz * s, 0, -lx * s + lz * c];
        if (rayHits(idx, o, d, 400)) continue;
        // (what stands under the path just past the mouth: a wall's top within the lunette's own height)
        const under = [.1, .3, .6, 1, 1.5].some((k) => {
          const q = [o[0] + d[0] * (reach + k), o[1], o[2] + d[2] * (reach + k)];
          return rayDist(idx, q, [0, -1, 0], ym - y0 + .3) < Infinity;
        });
        if (under) { out.push({ part: p.name, inst, kind: "open vault", at: [o[0] + d[0] * reach, o[1], o[2] + d[2] * reach].map((v) => +v.toFixed(2)) }); return; }
      }
    });
  }
  return out;
}
